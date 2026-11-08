"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, box, close, color, extend,
    format, high, input, label, line, location, low, math, na, plotshape, script, shape, size,
    string, ta, text, time, timeframe, xloc, yloc
)
from pynecore.types import Box, Color, Label, Line, NA, Persistent


@udt
class SwingPt:
    price: float = 0.0
    barIdx: int = 0
    isHigh: bool = False


@udt
class FibCluster:
    center: float = 0.0
    strength: int = 0


@udt
class Zone:
    center: float = 0.0
    top: float = 0.0
    bot: float = 0.0
    strength: int = 0
    kind: int = 0
    touched: bool = False
    bx: Box = na(Box)
    ln: Line = na(Line)
    lb: Label = na(Label)


@udt
class PerDraw:
    boxes: list[Box] = na(list)
    lines: list[Line] = na(list)
    labels: list[Label] = na(list)


grpA: str = "Anchor"
grpGP: str = "Golden Pocket & Equilibrium"
grpCl: str = "Clustering"
grpLC: str = "Lifecycle Engine"
grpVM: str = "Virgin Magnets"
grpSep: str = "Period Separators"
grpD: str = "Display"
grpC: str = "Colors"


@script.indicator("Strong Fibo Clusters", overlay=True, max_lines_count=500, max_boxes_count=500, max_labels_count=500)
def main(
    anchorTf=input.string("W", "Anchor Period", options=("W", "2W", "M"), group=grpA, tooltip="W = weekly (last week's data). 2W = bi-weekly. M = monthly. Clusters, extremes and separators all follow this anchor."),
    sourceLookback=input.int(1, "Source Swings Lookback (periods)", minval=1, maxval=8, group=grpA, tooltip="How many completed periods of swings feed the cluster search. 1 = last period only."),
    maxPer=input.int(4, "Periods to Keep Drawn", minval=1, maxval=12, group=grpA, tooltip="Most recent periods whose zones stay drawn. Older periods are removed — virgin magnets survive the cull."),
    swingLen=input.int(10, "Swing Length (bars)", minval=3, maxval=50, group="Swing Detection"),
    maxSwings=input.int(10, "Max Swings per Side", minval=4, maxval=15, group="Swing Detection"),
    useFib236=input.bool(True, "0.236", group="Retracement Levels", inline="r1"),
    useFib382=input.bool(True, "0.382", group="Retracement Levels", inline="r1"),
    useFib500=input.bool(True, "0.500", group="Retracement Levels", inline="r1"),
    useFib618=input.bool(True, "0.618", group="Retracement Levels", inline="r2"),
    useFib786=input.bool(True, "0.786", group="Retracement Levels", inline="r2"),
    useFib1000=input.bool(False, "1.000", group="Retracement Levels", inline="r2"),
    showExt113=input.bool(True, "1.130 (above high)", group="Extension Zones", inline="e1"),
    showExt127=input.bool(True, "1.270 (above high)", group="Extension Zones", inline="e1"),
    showExtN013=input.bool(True, "-0.130 (below low)", group="Extension Zones", inline="e2"),
    showExtN027=input.bool(True, "-0.270 (below low)", group="Extension Zones", inline="e2"),
    showGP=input.bool(True, "Show Golden Pocket", group=grpGP),
    gpFibLow=input.float(0.5, "Lower Fib", minval=0.0, maxval=1.0, step=0.001, group=grpGP),
    gpFibHigh=input.float(0.618, "Upper Fib", minval=0.0, maxval=1.0, step=0.001, group=grpGP),
    showEQ=input.bool(True, "Show Equilibrium (50%) Line", group=grpGP),
    atrMult=input.float(0.5, "Cluster Tolerance (x ATR)", minval=0.1, maxval=3.0, step=0.1, group=grpCl, tooltip="Two Fib levels from different swing pairs must be within this distance to be counted as confluent."),
    minRangeMult=input.float(2.0, "Min Pair Range (x ATR)", minval=0.1, maxval=10.0, step=0.1, group=grpCl, tooltip="A swing high/low pair must span at least this distance to contribute Fib levels."),
    minStr=input.int(2, "Min Cluster Strength", minval=2, maxval=20, group=grpCl, tooltip="Minimum number of distinct swing pairs that must agree on a zone."),
    maxClusters=input.int(5, "Max Clusters to Display", minval=1, maxval=10, group=grpCl),
    sepMult=input.float(1.5, "Min Separation (x ATR)", minval=0.5, maxval=5.0, step=0.1, group=grpCl, tooltip="Minimum center-to-center distance between displayed clusters."),
    showLiqLines=input.bool(True, "Show Prior High/Low Lines", group=grpLC, tooltip="Draws the prior period high and low as key liquidity levels, recolored as their state changes."),
    showState=input.bool(True, "Recolor Lines by State", group=grpLC, tooltip="INTACT -> SWEPT -> ACCEPTED -> FAILED BREAK."),
    showMarks=input.bool(True, "Plot Lifecycle Markers", group=grpLC),
    maxMark=input.int(40, "Max Event Markers Kept", minval=4, maxval=200, group=grpLC),
    mkSize=input.string("tiny", "Marker Size", options=("tiny", "small", "normal"), group=grpLC),
    sweepMult=input.float(0.08, "Sweep Threshold (x ATR)", minval=0.0, maxval=5.0, step=0.01, group=grpLC, tooltip="Wick beyond the extreme by this much, closing back inside, is a sweep."),
    breakMult=input.float(0.3, "Acceptance Threshold (x ATR)", minval=0.0, maxval=5.0, step=0.01, group=grpLC, tooltip="A close beyond the extreme by this much is acceptance."),
    useMagnet=input.bool(True, "Track Untouched Levels as Magnets", group=grpVM, tooltip="A cluster or prior extreme never traded into during its period is promoted to a persistent magnet that projects right until price tags it."),
    maxMagnet=input.int(8, "Max Active Magnets", minval=1, maxval=40, group=grpVM),
    magWidth=input.int(1, "Magnet Line Width", minval=1, maxval=4, group=grpVM),
    magStyle=input.string("dotted", "Magnet Line Style", options=("dotted", "dashed", "solid"), group=grpVM),
    magLabels=input.bool(True, "Label Magnets", group=grpVM),
    showSep=input.bool(True, "Show Period Separators", group=grpSep),
    sepCol=input.color(color.new('#5C6470'), "Separator Color", group=grpSep),
    sepWidth=input.int(1, "Separator Width", minval=1, maxval=4, group=grpSep),
    sepStyle=input.string("dashed", "Separator Style", options=("dashed", "dotted", "solid"), group=grpSep),
    zoneHalfMult=input.float(0.2, "Zone Half-Height (x ATR)", minval=0.1, maxval=2.0, step=0.1, group=grpD),
    showLabels=input.bool(True, "Show Zone Labels", group=grpD),
    extRight=input.int(30, "Extend Latest Period (bars)", minval=0, maxval=300, group=grpD),
    labelSz=input.string("small", "Label Size", options=("tiny", "small", "normal", "large"), group=grpD),
    showDots=input.bool(False, "Show Swing Dots", group=grpD),
    colElite=input.color(color.new('#21C997'), "Cluster Elite  (>=6)", group=grpC),
    colStrong=input.color(color.new('#26A69A'), "Cluster Strong (4-5)", group=grpC),
    colMedium=input.color(color.new('#00897B'), "Cluster Medium (2-3)", group=grpC),
    colExt1=input.color(color.new('#CC24E2'), "Ext 1.130 / -0.130", group=grpC),
    colExt2=input.color(color.new('#880E4F'), "Ext 1.270 / -0.270", group=grpC),
    gpColor=input.color(color.new('#787878'), "Golden Pocket Zone", group=grpC),
    eqCol=input.color(color.new('#8E8E8E'), "Equilibrium Line", group=grpC),
    domHiCol=input.color(color.new('#21C997'), "Prior High Line", group=grpC),
    domLoCol=input.color(color.new('#CC24E2'), "Prior Low Line", group=grpC),
    sweptCol=input.color(color.new('#CC24E2'), "State: Swept", group=grpC),
    accCol=input.color(color.new('#00897B'), "State: Accepted", group=grpC),
    failCol=input.color(color.new('#880E4F'), "State: Failed Break", group=grpC),
    magCol=input.color(color.new('#9AA5B1'), "Virgin Magnet", group=grpC),
    colLabel=input.color(color.white, "Label Text", group=grpC),
    boxTransp=input.int(78, "Box Transparency", minval=0, maxval=100, group=grpC),
    brdTransp=input.int(40, "Border Transparency", minval=0, maxval=100, group=grpC),
    gpTransp=input.int(80, "Golden Pocket Transparency", minval=40, maxval=99, group=grpC),
    showBorder=input.bool(False, "Show Zone Borders", group=grpC)
):
    clearC = color.new(color.gray, 100)

    magPx: Persistent[list[float]] = array.new_float()
    magLn: Persistent[list[Line]] = array.new_line()
    magLb: Persistent[list[Label]] = array.new_label()

    def f_lblSize():
        return size.tiny if labelSz == 'tiny' else size.small if labelSz == 'small' else size.large if labelSz == 'large' else size.normal

    def f_mkSizeF():
        return size.tiny if mkSize == 'tiny' else size.small if mkSize == 'small' else size.normal

    def f_magStyleF():
        return line.style_dashed if magStyle == 'dashed' else line.style_solid if magStyle == 'solid' else line.style_dotted

    def f_sepStyleF():
        return line.style_dotted if sepStyle == 'dotted' else line.style_solid if sepStyle == 'solid' else line.style_dashed

    def f_anchorName():
        return 'WEEK' if anchorTf == 'W' else '2-WEEK' if anchorTf == '2W' else 'MONTH'

    def f_tier(s: int):
        return 'ELITE' if s >= 6 else 'STRONG' if s >= 4 else 'MEDIUM'

    def f_clCol(s: int):
        return colElite if s >= 6 else colStrong if s >= 4 else colMedium

    def f_stateTag(st: int):
        return 'SWEPT' if st == 1 else 'ACCEPTED' if st == 2 else 'FAILED BREAK' if st == 3 else 'INTACT'

    def f_stateCol(st: int, baseC: Color):
        return sweptCol if st == 1 else accCol if st == 2 else failCol if st == 3 else baseC

    def f_delPer(d: PerDraw):
        if not na(d.boxes):
            for b in d.boxes:
                box.delete(b)
        if not na(d.lines):
            for l in d.lines:
                line.delete(l)
        __block_result__ = na
        if not na(d.labels):
            __block_result_1__ = na
            for x in d.labels:
                __block_result_1__ = label.delete(x)
            __block_result__ = __block_result_1__
        return __block_result__

    def f_spawnMag(price: float, tagTxt: str, leftB: int, rightBar: int):
        mLn = line.new(leftB, price, rightBar, price, xloc=xloc.bar_index, color=magCol, width=magWidth, style=f_magStyleF())
        mLb = label.new(rightBar, price, tagTxt, xloc=xloc.bar_index, color=color.new(color.gray, 100), textcolor=magCol, style=label.style_label_left, size=f_mkSizeF()) if magLabels else na
        array.push(magPx, price)
        array.push(magLn, mLn)
        return array.push(magLb, mLb)

    atr14: float = ta.atr(14)
    phVal: float = ta.pivothigh(high, swingLen, swingLen)
    plVal: float = ta.pivotlow(low, swingLen, swingLen)
    swingCap: int = math.min(maxSwings, 15)

    swings: Persistent[list[SwingPt]] = array.new(0, NA(SwingPt))
    boundaryBars: Persistent[list[int]] = array.new_int()
    drawPer: Persistent[list[PerDraw]] = array.new(0, NA(PerDraw))
    activeZones: Persistent[list[Zone]] = array.new(0, NA(Zone))
    mkArr: Persistent[list[Label]] = array.new_label()
    sepArr: Persistent[list[Line]] = array.new_line()

    pHigh: Persistent[float] = na(float)
    pLow: Persistent[float] = na(float)

    haveActive: Persistent[bool] = False
    abLeft: Persistent[int] = na(int)
    lvHigh: Persistent[float] = na(float)
    lvLow: Persistent[float] = na(float)
    lvSwU: Persistent[float] = na(float)
    lvBkU: Persistent[float] = na(float)
    lvSwL: Persistent[float] = na(float)
    lvBkL: Persistent[float] = na(float)
    stU: Persistent[int] = 0
    stL: Persistent[int] = 0
    tchU: Persistent[bool] = False
    tchL: Persistent[bool] = False
    lnHi: Persistent[Line] = na(Line)
    lnLo: Persistent[Line] = na(Line)
    lbHi: Persistent[Label] = na(Label)
    lbLo: Persistent[Label] = na(Label)

    if not na(phVal):
        array.unshift(swings, SwingPt(phVal, bar_index - swingLen, True))
    if not na(plVal):
        array.unshift(swings, SwingPt(plVal, bar_index - swingLen, False))
    while array.size(swings) > 300:
        array.pop(swings)

    plotshape(showDots and (not na(phVal)), title='SH', location=location.abovebar, style=shape.circle, color=color.new(colElite, 20), size=size.tiny)
    plotshape(showDots and (not na(plVal)), title='SL', location=location.belowbar, style=shape.circle, color=color.new(colExt1, 20), size=size.tiny)

    evSweepU: bool = False
    evSweepL: bool = False
    evAccU: bool = False
    evAccL: bool = False
    evFailU: bool = False
    evFailL: bool = False
    evMagTag: bool = False
    evTouch: bool = False

    newP: bool = ta.change(time(anchorTf)) != 0

    if newP:
        boundaryBar: int = bar_index

        if haveActive:
            if useMagnet and (not tchU) and (not na(lvHigh)):
                f_spawnMag(lvHigh, 'VIRGIN ' + f_anchorName() + ' HIGH', abLeft, boundaryBar)
            if useMagnet and (not tchL) and (not na(lvLow)):
                f_spawnMag(lvLow, 'VIRGIN ' + f_anchorName() + ' LOW', abLeft, boundaryBar)
            if array.size(activeZones) > 0:
                for z in activeZones:
                    if useMagnet and z.kind == 0 and (not z.touched):
                        f_spawnMag(z.center, 'VIRGIN CLUSTER', abLeft, boundaryBar)
            while array.size(magPx) > maxMagnet:
                array.shift(magPx)
                oldln = array.shift(magLn)
                oldlb = array.shift(magLb)
                if not na(oldln):
                    line.delete(oldln)
                if not na(oldlb):
                    label.delete(oldlb)

        if showSep:
            sepLn = line.new(boundaryBar, low, boundaryBar, high, xloc=xloc.bar_index, extend=extend.both, color=sepCol, width=sepWidth, style=f_sepStyleF())
            array.push(sepArr, sepLn)
            while array.size(sepArr) > maxPer + 1:
                osep = array.shift(sepArr)
                if not na(osep):
                    line.delete(osep)

        prevH: float = pHigh
        prevL: float = pLow

        szB: int = array.size(boundaryBars)
        idxB: int = sourceLookback - 1
        startBar: int = 0
        if szB > 0:
            startBar = array.get(boundaryBars, idxB) if idxB < szB else array.get(boundaryBars, szB - 1)

        haveActive = False
        array.clear(activeZones)
        stU = 0
        stL = 0
        tchU = False
        tchL = False

        valid: bool = not na(prevH) and (not na(prevL)) and (prevH > prevL) and (not na(atr14))

        if valid:
            rng: float = prevH - prevL
            clusterTol: float = atr14 * atrMult
            minRange: float = atr14 * minRangeMult
            zoneHalf: float = atr14 * zoneHalfMult

            srcHighs: list[SwingPt] = array.new(0, NA(SwingPt))
            srcLows: list[SwingPt] = array.new(0, NA(SwingPt))
            nAll: int = array.size(swings)
            if nAll > 0:
                for i in pine_range(0, nAll - 1):
                    sp = array.get(swings, i)
                    if sp.barIdx >= startBar and sp.barIdx < boundaryBar:
                        if sp.isHigh:
                            if array.size(srcHighs) < swingCap:
                                array.push(srcHighs, sp)
                        else:
                            if array.size(srcLows) < swingCap:
                                array.push(srcLows, sp)

            clusters: list[FibCluster] = array.new(0, NA(FibCluster))
            nH: int = array.size(srcHighs)
            nL: int = array.size(srcLows)
            if nH > 0 and nL > 0:
                for hi in pine_range(0, nH - 1):
                    sh = array.get(srcHighs, hi)
                    for li in pine_range(0, nL - 1):
                        sl = array.get(srcLows, li)
                        prng: float = sh.price - sl.price
                        if prng >= minRange:
                            pairLevels: list[float] = array.new_float()
                            if useFib236:
                                array.push(pairLevels, sh.price - prng * 0.236)
                            if useFib382:
                                array.push(pairLevels, sh.price - prng * 0.382)
                            if useFib500:
                                array.push(pairLevels, sh.price - prng * 0.5)
                            if useFib618:
                                array.push(pairLevels, sh.price - prng * 0.618)
                            if useFib786:
                                array.push(pairLevels, sh.price - prng * 0.786)
                            if useFib1000:
                                array.push(pairLevels, sh.price - prng * 1.0)
                            nLevels: int = array.size(pairLevels)
                            if nLevels > 0:
                                nCbefore: int = array.size(clusters)
                                pairContributed: list[bool] = array.new_bool()
                                if nCbefore > 0:
                                    for k in pine_range(0, nCbefore - 1):
                                        array.push(pairContributed, False)
                                for lv in pine_range(0, nLevels - 1):
                                    lp: float = array.get(pairLevels, lv)
                                    bestK: int = -1
                                    bestDist: float = clusterTol + 1.0
                                    nCurr: int = array.size(clusters)
                                    if nCurr > 0:
                                        for k in pine_range(0, nCurr - 1):
                                            ck0 = array.get(clusters, k)
                                            dist: float = math.abs(lp - ck0.center)
                                            if dist <= clusterTol and dist < bestDist:
                                                bestDist = dist
                                                bestK = k
                                    if bestK >= 0:
                                        ck = array.get(clusters, bestK)
                                        already: bool = array.get(pairContributed, bestK) if array.size(pairContributed) > bestK else False
                                        ck.center = (ck.center * ck.strength + lp) / (ck.strength + 1)
                                        if not already:
                                            ck.strength = ck.strength + 1
                                            if array.size(pairContributed) > bestK:
                                                array.set(pairContributed, bestK, True)
                                        array.set(clusters, bestK, ck)
                                    else:
                                        array.push(clusters, FibCluster(lp, 1))
                                        array.push(pairContributed, True)

            qualified: list[FibCluster] = array.new(0, NA(FibCluster))
            nRaw: int = array.size(clusters)
            if nRaw > 0:
                for k in pine_range(0, nRaw - 1):
                    ck = array.get(clusters, k)
                    if ck.strength >= minStr:
                        array.push(qualified, ck)

            nQ: int = array.size(qualified)
            if nQ > 1:
                for i in pine_range(0, nQ - 2):
                    for j in pine_range(0, nQ - 2 - i):
                        ca = array.get(qualified, j)
                        cb = array.get(qualified, j + 1)
                        if ca.strength < cb.strength:
                            array.set(qualified, j, cb)
                            array.set(qualified, j + 1, ca)

            selected: list[FibCluster] = array.new(0, NA(FibCluster))
            minSep: float = atr14 * sepMult
            if nQ > 0:
                for i in pine_range(0, nQ - 1):
                    if array.size(selected) >= maxClusters:
                        break
                    cand = array.get(qualified, i)
                    overlaps: bool = False
                    nSel0: int = array.size(selected)
                    if nSel0 > 0:
                        for j in pine_range(0, nSel0 - 1):
                            ex = array.get(selected, j)
                            if math.abs(cand.center - ex.center) < minSep:
                                overlaps = True
                                break
                    if not overlaps:
                        array.push(selected, cand)

            pd: PerDraw = PerDraw(array.new_box(), array.new_line(), array.new_label())

            nSel: int = array.size(selected)
            if nSel > 0:
                for i in pine_range(0, nSel - 1):
                    cl = array.get(selected, i)
                    rank: int = i + 1
                    s: int = cl.strength
                    zTop: float = cl.center + zoneHalf
                    zBot: float = cl.center - zoneHalf
                    baseCol: Color = f_clCol(s)
                    bordC: Color = color.new(baseCol, brdTransp) if showBorder else clearC
                    bordW: int = 1 if showBorder else 0
                    bx: Box = box.new(boundaryBar, zTop, boundaryBar, zBot, bgcolor=color.new(baseCol, boxTransp), border_color=bordC, border_width=bordW, extend=extend.none)
                    ln: Line = line.new(boundaryBar, cl.center, boundaryBar, cl.center, xloc=xloc.bar_index, color=color.new(baseCol, math.max(0, brdTransp - 10)), style=line.style_dashed, width=1)
                    lb: Label = na(Label)
                    if showLabels:
                        txt: str = '#' + string.tostring(rank) + '  ' + f_tier(s) + '  STR ' + string.tostring(s) + '  @ ' + string.tostring(cl.center, format.mintick)
                        lb = label.new(boundaryBar, cl.center, txt, xloc=xloc.bar_index, color=color.new(color.black, 100), textcolor=colLabel, size=f_lblSize(), style=label.style_label_left)
                    array.push(pd.boxes, bx)
                    array.push(pd.lines, ln)
                    if not na(lb):
                        array.push(pd.labels, lb)
                    array.push(activeZones, Zone(cl.center, zTop, zBot, s, 0, False, bx, ln, lb))

            if showGP:
                gpTop: float = prevL + rng * math.max(gpFibLow, gpFibHigh)
                gpBot: float = prevL + rng * math.min(gpFibLow, gpFibHigh)
                gpMid: float = (gpTop + gpBot) / 2.0
                bxGP: Box = box.new(boundaryBar, gpTop, boundaryBar, gpBot, bgcolor=color.new(gpColor, gpTransp), border_color=clearC, border_width=0, extend=extend.none)
                lbGP: Label = na(Label)
                if showLabels:
                    lbGP = label.new(boundaryBar, gpMid, 'GOLDEN POCKET  @ ' + string.tostring(gpMid, format.mintick), xloc=xloc.bar_index, color=color.new(color.black, 100), textcolor=colLabel, size=f_lblSize(), style=label.style_label_left)
                array.push(pd.boxes, bxGP)
                if not na(lbGP):
                    array.push(pd.labels, lbGP)
                array.push(activeZones, Zone(gpMid, gpTop, gpBot, 0, 3, False, bxGP, na, lbGP))

            if showEQ:
                eqMid: float = prevL + rng * 0.5
                lnEQ: Line = line.new(boundaryBar, eqMid, boundaryBar, eqMid, xloc=xloc.bar_index, color=eqCol, width=1, style=line.style_dotted)
                lbEQ: Label = na(Label)
                if showLabels:
                    lbEQ = label.new(boundaryBar, eqMid, 'EQUILIBRIUM 50%', xloc=xloc.bar_index, color=color.new(color.black, 100), textcolor=eqCol, size=f_lblSize(), style=label.style_label_left)
                array.push(pd.lines, lnEQ)
                if not na(lbEQ):
                    array.push(pd.labels, lbEQ)
                array.push(activeZones, Zone(eqMid, eqMid, eqMid, 0, 4, False, na, lnEQ, lbEQ))

            extPx: list[float] = array.new_float()
            extColA: list[Color] = array.new_color()
            extKindA: list[int] = array.new_int()
            extTagA: list[str] = array.new_string()
            if showExt113:
                array.push(extPx, prevH + rng * 0.13)
                array.push(extColA, colExt1)
                array.push(extKindA, 1)
                array.push(extTagA, 'EXT 1.13')
            if showExt127:
                array.push(extPx, prevH + rng * 0.27)
                array.push(extColA, colExt2)
                array.push(extKindA, 2)
                array.push(extTagA, 'EXT 1.27')
            if showExtN013:
                array.push(extPx, prevL - rng * 0.13)
                array.push(extColA, colExt1)
                array.push(extKindA, 1)
                array.push(extTagA, 'EXT -0.13')
            if showExtN027:
                array.push(extPx, prevL - rng * 0.27)
                array.push(extColA, colExt2)
                array.push(extKindA, 2)
                array.push(extTagA, 'EXT -0.27')
            nExt: int = array.size(extPx)
            if nExt > 0:
                for i in pine_range(0, nExt - 1):
                    ep: float = array.get(extPx, i)
                    ec: Color = array.get(extColA, i)
                    ek: int = array.get(extKindA, i)
                    et: str = array.get(extTagA, i)
                    bxE: Box = box.new(boundaryBar, ep + zoneHalf, boundaryBar, ep - zoneHalf, bgcolor=color.new(ec, boxTransp), border_color=clearC, border_width=0, extend=extend.none)
                    lnE: Line = line.new(boundaryBar, ep, boundaryBar, ep, xloc=xloc.bar_index, color=color.new(ec, math.max(0, brdTransp - 10)), style=line.style_dashed, width=1)
                    lbE: Label = na(Label)
                    if showLabels:
                        lbE = label.new(boundaryBar, ep, et + '  @ ' + string.tostring(ep, format.mintick), xloc=xloc.bar_index, color=color.new(color.black, 100), textcolor=colLabel, size=f_lblSize(), style=label.style_label_left)
                    array.push(pd.boxes, bxE)
                    array.push(pd.lines, lnE)
                    if not na(lbE):
                        array.push(pd.labels, lbE)
                    array.push(activeZones, Zone(ep, ep + zoneHalf, ep - zoneHalf, 0, ek, False, bxE, lnE, lbE))

            aName: str = f_anchorName()
            if showLiqLines:
                lnHi = line.new(boundaryBar, prevH, boundaryBar, prevH, xloc=xloc.bar_index, color=domHiCol, width=2, style=line.style_solid)
                lnLo = line.new(boundaryBar, prevL, boundaryBar, prevL, xloc=xloc.bar_index, color=domLoCol, width=2, style=line.style_solid)
                lbHi = label.new(boundaryBar, prevH, 'PREV ' + aName + ' HIGH  @ ' + string.tostring(prevH, format.mintick), xloc=xloc.bar_index, color=color.new(color.black, 100), textcolor=domHiCol, size=f_lblSize(), style=label.style_label_left) if showLabels else na
                lbLo = label.new(boundaryBar, prevL, 'PREV ' + aName + ' LOW  @ ' + string.tostring(prevL, format.mintick), xloc=xloc.bar_index, color=color.new(color.black, 100), textcolor=domLoCol, size=f_lblSize(), style=label.style_label_left) if showLabels else na
                array.push(pd.lines, lnHi)
                array.push(pd.lines, lnLo)
                if not na(lbHi):
                    array.push(pd.labels, lbHi)
                if not na(lbLo):
                    array.push(pd.labels, lbLo)
            else:
                lnHi = na
                lnLo = na
                lbHi = na
                lbLo = na

            haveActive = True
            abLeft = boundaryBar
            lvHigh = prevH
            lvLow = prevL
            lvSwU = prevH + atr14 * sweepMult
            lvBkU = prevH + atr14 * breakMult
            lvSwL = prevL - atr14 * sweepMult
            lvBkL = prevL - atr14 * breakMult

            array.push(drawPer, pd)
            while array.size(drawPer) > maxPer:
                f_delPer(array.shift(drawPer))
        else:
            lnHi = na
            lnLo = na
            lbHi = na
            lbLo = na

        array.unshift(boundaryBars, boundaryBar)
        capB: int = math.max(sourceLookback, maxPer) + 3
        while array.size(boundaryBars) > capB:
            array.pop(boundaryBars)

        pHigh = high
        pLow = low
    else:
        pHigh = high if na(pHigh) else math.max(pHigh, high)
        pLow = low if na(pLow) else math.min(pLow, low)

    rightB: int = bar_index + (extRight if barstate.islast else 0)

    if haveActive:
        if array.size(activeZones) > 0:
            for z in activeZones:
                if not na(z.bx):
                    box.set_right(z.bx, rightB)
                if not na(z.ln):
                    line.set_x2(z.ln, rightB)
                if not na(z.lb):
                    label.set_x(z.lb, rightB)
        if not na(lnHi):
            line.set_x2(lnHi, rightB)
        if not na(lbHi):
            label.set_x(lbHi, rightB)
        if not na(lnLo):
            line.set_x2(lnLo, rightB)
        if not na(lbLo):
            label.set_x(lbLo, rightB)

        if array.size(activeZones) > 0:
            for z in activeZones:
                if not z.touched:
                    if high >= z.bot and low <= z.top:
                        z.touched = True
                        evTouch = True

        if high >= lvHigh and low <= lvHigh:
            tchU = True
        if high >= lvLow and low <= lvLow:
            tchL = True

        sweepU: bool = high >= lvSwU and close < lvHigh
        sweepL: bool = low <= lvSwL and close > lvLow
        acceptU: bool = close > lvBkU
        acceptL: bool = close < lvBkL
        prevStU: int = stU
        prevStL: int = stL

        if acceptU:
            stU = 2
        elif stU == 2 and close < lvHigh:
            stU = 3
        elif stU == 0 and sweepU:
            stU = 1

        if acceptL:
            stL = 2
        elif stL == 2 and close > lvLow:
            stL = 3
        elif stL == 0 and sweepL:
            stL = 1

        evSweepU = stU == 1 and prevStU == 0
        evSweepL = stL == 1 and prevStL == 0
        evAccU = stU == 2 and prevStU != 2
        evAccL = stL == 2 and prevStL != 2
        evFailU = stU == 3 and prevStU == 2
        evFailL = stL == 3 and prevStL == 2

        if showState and stU != prevStU:
            if not na(lnHi):
                line.set_color(lnHi, f_stateCol(stU, domHiCol))
            if not na(lbHi):
                label.set_text(lbHi, 'PREV ' + f_anchorName() + ' HIGH  ·  ' + f_stateTag(stU))
                label.set_textcolor(lbHi, f_stateCol(stU, domHiCol))
        if showState and stL != prevStL:
            if not na(lnLo):
                line.set_color(lnLo, f_stateCol(stL, domLoCol))
            if not na(lbLo):
                label.set_text(lbLo, 'PREV ' + f_anchorName() + ' LOW  ·  ' + f_stateTag(stL))
                label.set_textcolor(lbLo, f_stateCol(stL, domLoCol))

        if showMarks:
            if evSweepU:
                array.push(mkArr, label.new(bar_index, high, 'SWEEP ▲', xloc=xloc.bar_index, yloc=yloc.price, color=color.new(sweptCol, 20), textcolor=color.new('#101010'), style=label.style_label_down, size=f_mkSizeF()))
            if evSweepL:
                array.push(mkArr, label.new(bar_index, low, 'SWEEP ▼', xloc=xloc.bar_index, yloc=yloc.price, color=color.new(sweptCol, 20), textcolor=color.new('#101010'), style=label.style_label_up, size=f_mkSizeF()))
            if evAccU:
                array.push(mkArr, label.new(bar_index, high, 'ACCEPT ▲', xloc=xloc.bar_index, yloc=yloc.price, color=color.new(accCol, 20), textcolor=color.new('#F2F2F2'), style=label.style_label_down, size=f_mkSizeF()))
            if evAccL:
                array.push(mkArr, label.new(bar_index, low, 'ACCEPT ▼', xloc=xloc.bar_index, yloc=yloc.price, color=color.new(accCol, 20), textcolor=color.new('#F2F2F2'), style=label.style_label_up, size=f_mkSizeF()))
            if evFailU:
                array.push(mkArr, label.new(bar_index, high, 'FAILED BREAK', xloc=xloc.bar_index, yloc=yloc.price, color=color.new(failCol, 15), textcolor=color.new('#F2F2F2'), style=label.style_label_down, size=f_mkSizeF()))
            if evFailL:
                array.push(mkArr, label.new(bar_index, low, 'FAILED BREAK', xloc=xloc.bar_index, yloc=yloc.price, color=color.new(failCol, 15), textcolor=color.new('#F2F2F2'), style=label.style_label_up, size=f_mkSizeF()))
            while array.size(mkArr) > maxMark:
                omk = array.shift(mkArr)
                if not na(omk):
                    label.delete(omk)

    if array.size(magPx) > 0:
        for i in pine_range(array.size(magPx) - 1, 0):
            px: float = array.get(magPx, i)
            ln: Line = array.get(magLn, i)
            lb: Label = array.get(magLb, i)
            tagged: bool = low <= px and high >= px
            if tagged:
                evMagTag = True
                if not na(ln):
                    line.set_x2(ln, bar_index)
                    line.set_color(ln, color.new(magCol, 55))
                if not na(lb):
                    label.delete(lb)
                array.remove(magPx, i)
                array.remove(magLn, i)
                array.remove(magLb, i)
            else:
                if not na(ln):
                    line.set_x2(ln, rightB)
                if not na(lb):
                    label.set_x(lb, rightB)

    tfTooBig: bool = timeframe.in_seconds() >= timeframe.in_seconds(anchorTf)
    warnLb: Persistent[Label] = na(Label)
    if barstate.islast:
        if not na(warnLb):
            label.delete(warnLb)
            warnLb = na
        if tfTooBig:
            warnLb = label.new(bar_index, high, 'Chart timeframe ≥ ' + anchorTf + ' anchor —\nswitch to an intra-' + f_anchorName() + ' timeframe so clusters can resolve.', xloc=xloc.bar_index, yloc=yloc.price, color=color.new(color.new('#7A2B2B'), 15), textcolor=color.new('#F0F0F0'), style=label.style_label_down, size=size.small, textalign=text.align_left)

    alertcondition(evTouch, 'Cluster / zone touched', 'Price touched a Strong Fibo Clusters zone')
    alertcondition(evSweepU, 'Sweep above prior high', 'Liquidity sweep above the prior-period high — closed back inside')
    alertcondition(evSweepL, 'Sweep below prior low', 'Liquidity sweep below the prior-period low — closed back inside')
    alertcondition(evAccU, 'Acceptance above prior high', 'Close accepted above the prior-period high')
    alertcondition(evAccL, 'Acceptance below prior low', 'Close accepted below the prior-period low')
    alertcondition(evFailU, 'Failed break above prior high', 'Accepted above the prior high then closed back inside')
    alertcondition(evFailL, 'Failed break below prior low', 'Accepted below the prior low then closed back inside')
    alertcondition(evMagTag, 'Virgin magnet tagged', 'Price tagged a previously untouched virgin level')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)