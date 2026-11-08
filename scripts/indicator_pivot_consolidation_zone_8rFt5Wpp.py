"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, array, bar_index, box, close, color, display, extend,
    format, high, input, label, line, linefill, location, low, math, na, plot, plotshape, script,
    shape, size, string, ta, time, volume, xloc
)
from pynecore.types import Box, Color, Label, Line, LineFill, Persistent

PROFILE_BIN_GAP_PCT: float = 10.0


@script.indicator("Pivot Consolidation Zone", overlay=True, max_boxes_count=500, max_labels_count=500, max_lines_count=500, max_bars_back=600)
def main(
    length=input.int(10, "Pivot Length", minval=2, maxval=30, group="Zone Settings", tooltip="Number of bars required on both sides to confirm a local swing high/low (pivot)."),
    maxPairBars=input.int(100, "Max Pivot Pair Distance (bars)", minval=20, group="Zone Settings", tooltip="Maximum distance in bars between a pivot pair (high and low) that can form a zone. Setting this too high may combine price extremes that are far apart in time."),
    maxLeftBack=input.int(250, "Max Box Left Edge (bars back)", minval=20, group="Zone Settings", tooltip="How far back (in bars) the left edge of the zone box can extend from the pivot, as long as the closing price stays inside the zone."),
    useAtrCap=input.bool(True, "Cap Max Zone Height by ATR", group="Zone Settings", tooltip="Rejects pivot pairs whose price range exceeds a specified multiple of ATR, preventing very wide, low-value zones from being created."),
    atrLen=input.int(100, "ATR Length", minval=1, group="Zone Settings", tooltip="ATR period used to cap the zone height and for the minimum breakout filter below."),
    maxMultBox=input.float(5.0, "Max Zone Height (x ATR)", minval=0, group="Zone Settings", tooltip="Maximum allowed zone height as a multiple of ATR. Active only when 'Cap Max Zone Height by ATR' is enabled."),
    minBreakAtr=input.float(0.0, "Min Breakout Size (x ATR)", minval=0, step=0.1, group="Zone Settings", tooltip="0 disables this filter. Price must close beyond the pivot/zone by N x ATR to invalidate a level or end a zone, filtering out minor noise breakouts."),
    showProfile=input.bool(True, "Show Zone Volume Profile", group="Volume Profile", tooltip="Draws a horizontal buy/sell volume histogram along the right edge of the zone, split into price bins."),
    profileBins=input.int(30, "Number of Price Bins", minval=3, maxval=40, group="Volume Profile", tooltip="Number of horizontal price bins the zone height is divided into when computing the profile."),
    profileWidth=input.int(30, "Max Profile Width (bars)", minval=5, maxval=100, group="Volume Profile", tooltip="Width, in bars, of the strongest bin in the profile. All other bins are scaled proportionally to it."),
    includeOuterWicks=input.bool(False, "Include Wick Volume Outside the Zone", group="Volume Profile", tooltip="Disabled (default): only volume occurring at prices inside the zone is counted; the portion of a candle's wick extending outside the zone is ignored. Enabled: the candle's full volume is counted, with the excess from an outside wick assigned to the nearest edge bin. This setting also affects the buy/sell bars, the buy/sell label, and the breakout signals."),
    showBoxVolBars=input.bool(True, "Show Buy/Sell Bars Below Zone", group="Zone Volume Split", tooltip="Two horizontal bars below the zone showing the ratio of buy to sell volume across the entire zone."),
    showBoxVolLabel=input.bool(True, "Show Buy/Sell % Label", group="Zone Volume Split", tooltip="Percentage label below the bars showing the exact buy/sell volume split within the zone."),
    volLabelSizeInput=input.string("Small", "Buy/Sell % Label Size", options=("Tiny", "Small", "Normal"), group="Zone Volume Split", tooltip="Size of the buy/sell percentage label, independent of the pivot/test marker size."),
    showBreakoutSignals=input.bool(True, "Show Breakout Signals", group="Breakout Signals", tooltip="Plots a triangle on the chart when the zone breaks out to the upside or downside."),
    requireVolConfirmation=input.bool(False, "Require Dominant Volume Confirmation", group="Breakout Signals", tooltip="Enabled: a signal (and the zone recolor) fires only when the breakout direction agrees with the dominant volume side within the zone. Disabled: the signal is determined solely by breakout direction, regardless of volume."),
    recolorBoxOnBreakout=input.bool(True, "Recolor Zone on Breakout", group="Breakout Signals", tooltip="After a breakout, the zone box changes from neutral to bullish/bearish based on the breakout direction (and volume, if required above). If the signal is not confirmed, the box remains neutral."),
    signalSizeInput=input.string("Small", "Breakout Signal Size", options=("Tiny", "Small", "Normal"), group="Breakout Signals", tooltip="Size of the breakout signal triangles on the chart."),
    showPivotMarkers=input.bool(False, "Show Pivot Markers (▼/▲)", group="Pivot & Test Markers", tooltip="Labels marking the pivots that formed the upper (▼) and lower (▲) boundary of the zone."),
    showTestMarkers=input.bool(False, "Show Zone Boundary Test Markers", group="Pivot & Test Markers", tooltip="Numbered markers showing each successive test of the zone's upper and lower boundary by price."),
    markerSizeInput=input.string("Small", "Pivot & Test Marker Size", options=("Tiny", "Small", "Normal"), group="Pivot & Test Markers", tooltip="Applies to both pivot markers and zone boundary test markers."),
    colBull=input.color(color.rgb(6, 162, 47), "Bullish Color", group="Colors", tooltip="Used for: the lower zone boundary (support) and its tests, a confirmed upside breakout, and the buy side of the volume profile/bars."),
    colBear=input.color(color.rgb(207, 23, 23), "Bearish Color", group="Colors", tooltip="Used for: the upper zone boundary (resistance) and its tests, a confirmed downside breakout, and the sell side of the volume profile/bars."),
    colNeutral=input.color(color.gray, "Neutral Color", group="Colors", tooltip="Color of the zone box itself until a breakout occurs. After a breakout, the box switches to the bullish or bearish color (see 'Breakout Signals')."),
    zoneBgTransp=input.int(85, "Zone Background Transparency", minval=0, maxval=100, group="Colors", tooltip="Transparency of the zone box fill (0 = fully opaque, 100 = invisible). Applies to both the neutral color and the post-breakout color."),
    zoneBorderTransp=input.int(0, "Zone Border Transparency", minval=0, maxval=100, group="Colors", tooltip="Transparency of the zone box border (0 = fully opaque, 100 = invisible). Applies to both the neutral color and the post-breakout color."),
    profileTransp=input.int(60, "Volume Profile Transparency", minval=0, maxval=100, group="Colors", tooltip="Transparency of the volume profile bins (0 = fully opaque, 100 = invisible)."),
    showTargets=input.bool(True, "Show TP/SL Levels", group="TP/SL", tooltip="Plots Entry, Stop Loss, and Take Profit levels for every new breakout signal."),
    useAtrSL=input.bool(True, "SL = ATR", group="TP/SL", tooltip="Enabled: the Stop Loss distance from the entry price is calculated from ATR (ATR multiplier for SL).\nDisabled: a fixed percentage value is used (SL % from Entry)."),
    tpAtrPeriod=input.int(14, "ATR Period (TP/SL)", minval=1, group="TP/SL", tooltip="ATR period used to determine the Stop Loss distance and Take Profit levels. Independent from the ATR used for zone filtering above."),
    slAtrMult=input.float(1.5, "SL ATR Multiplier", step=0.1, group="TP/SL", tooltip="ATR multiplier that determines the Stop Loss distance from the entry price, active when 'SL = ATR' is enabled."),
    slPercent=input.float(1.0, "SL % from Entry", step=0.1, group="TP/SL", tooltip="Percentage distance of the Stop Loss from the entry price, used when 'SL = ATR' is disabled."),
    rrTP1=input.float(1.0, "TP1 Risk:Reward", step=0.1, group="TP/SL", tooltip="Risk:Reward ratio for Take Profit 1. A value of 1.0 means TP1 sits at a distance equal to the risk (SL) from the entry price."),
    rrTP2=input.float(2.0, "TP2 Risk:Reward", step=0.1, group="TP/SL", tooltip="Risk:Reward ratio for Take Profit 2."),
    rrTP3=input.float(3.0, "TP3 Risk:Reward", step=0.1, group="TP/SL", tooltip="Risk:Reward ratio for Take Profit 3."),
    showSlLevel=input.bool(True, "Show SL Level", group="TP/SL Display", tooltip="Draws the line and label for the Stop Loss of the active signal."),
    showTp1Level=input.bool(True, "Show TP1 Level", group="TP/SL Display", tooltip="Draws the line and label for Take Profit 1 of the active signal."),
    showTp2Level=input.bool(True, "Show TP2 Level", group="TP/SL Display", tooltip="Draws the line and label for Take Profit 2 of the active signal."),
    showTp3Level=input.bool(True, "Show TP3 Level", group="TP/SL Display", tooltip="Draws the line and label for Take Profit 3 of the active signal.")
):
    __block_result__ = na
    __switch__ = markerSizeInput
    if __switch__ == "Tiny":
        __block_result__ = size.tiny
    elif __switch__ == "Small":
        __block_result__ = size.small
    elif __switch__ == "Normal":
        __block_result__ = size.normal
    else:
        __block_result__ = size.small
    markerSize = __block_result__

    __block_result_1__ = na
    __switch__ = volLabelSizeInput
    if __switch__ == "Tiny":
        __block_result_1__ = size.tiny
    elif __switch__ == "Small":
        __block_result_1__ = size.small
    elif __switch__ == "Normal":
        __block_result_1__ = size.normal
    else:
        __block_result_1__ = size.small
    volLabelSize = __block_result_1__

    atrVal = ta.atr(atrLen)
    atrTP = ta.atr(tpAtrPeriod)
    brk = minBreakAtr * atrVal

    hP: Persistent[list[float]] = array.new_float()
    hL: Persistent[list[float]] = array.new_float()
    hI: Persistent[list[int]] = array.new_int()
    hTi: Persistent[list[int]] = array.new_int()
    hT: Persistent[list[int]] = array.new_int()
    hIn: Persistent[list[bool]] = array.new_bool()
    hTB: Persistent[list[str]] = array.new_string()

    lP: Persistent[list[float]] = array.new_float()
    lH: Persistent[list[float]] = array.new_float()
    lI: Persistent[list[int]] = array.new_int()
    lTi: Persistent[list[int]] = array.new_int()
    lT: Persistent[list[int]] = array.new_int()
    lIn: Persistent[list[bool]] = array.new_bool()
    lTB: Persistent[list[str]] = array.new_string()

    zoneActive: Persistent[bool] = False
    zoneTop: Persistent[float] = na(float)
    zoneBottom: Persistent[float] = na(float)
    zoneBox: Persistent[Box] = na(Box)
    zoneLeftIdx: Persistent[int] = na(int)

    profBullVol: Persistent[list[float]] = array.new_float(0)
    profBearVol: Persistent[list[float]] = array.new_float(0)
    profBullBox: Persistent[list[Box]] = array.new_box(0)
    profBearBox: Persistent[list[Box]] = array.new_box(0)

    bullVolBox: Persistent[Box] = na(Box)
    bearVolBox: Persistent[Box] = na(Box)
    volPctLabel: Persistent[Label] = na(Label)

    tpslDir: Persistent[int] = 0
    tpslSL: Persistent[float] = na(float)
    tpslExtreme: Persistent[float] = na(float)
    tpslEntryLn: Persistent[Line] = na(Line)
    tpslEntryLb: Persistent[Label] = na(Label)
    tpslSlLn: Persistent[Line] = na(Line)
    tpslSlLb: Persistent[Label] = na(Label)
    tpslTp1Ln: Persistent[Line] = na(Line)
    tpslTp1Lb: Persistent[Label] = na(Label)
    tpslTp2Ln: Persistent[Line] = na(Line)
    tpslTp2Lb: Persistent[Label] = na(Label)
    tpslTp3Ln: Persistent[Line] = na(Line)
    tpslTp3Lb: Persistent[Label] = na(Label)
    tpslExtLn: Persistent[Line] = na(Line)
    tpslRiskFill: Persistent[LineFill] = na(LineFill)
    tpslRewardFill: Persistent[LineFill] = na(LineFill)
    tpslEntryBar: Persistent[int] = na(int)

    ph = ta.pivothigh(length, length)
    pl = ta.pivotlow(length, length)

    def appendTest(s: str, idx: int):
        return string.tostring(idx) if s == '' else s + ',' + string.tostring(idx)

    def markTests(s: str, price: float, c: Color):
        __block_result_2__ = na
        if s != '':
            parts = string.split(s, ',')
            __block_result_3__ = na
            for k in pine_range(0, array.size(parts) - 1):
                idx = cast_int(string.tonumber(array.get(parts, k)))
                __block_result_3__ = label.new(idx, price, string.tostring(k + 1), style=label.style_circle, color=color.new(c, 40), textcolor=color.white, size=markerSize)
            __block_result_2__ = __block_result_3__
        return __block_result_2__

    def leftEdgeTime(top: float, bot: float, pivotOffset: int, breakSize: float, maxBack: int):
        leftOff = pivotOffset
        lim = math.min(maxBack, bar_index)
        if pivotOffset < lim:
            for k in pine_range(pivotOffset + 1, lim):
                c = close[k]
                if na(c):
                    break
                if c > top + breakSize or c < bot - breakSize:
                    break
                leftOff = k
        return (leftOff, time[leftOff])

    def f_addBarToProfile(bullBins: list[float], bearBins: list[float], nBins: int, top: float, bot: float, bH: float, bL: float, bC: float, bV: float, clip: bool):
        binH: float = (top - bot) / nBins
        __block_result_4__ = na
        if binH > 0 and bH > bL:
            fullRange: float = bH - bL
            coreHigh: float = math.min(bH, top)
            coreLow: float = math.max(bL, bot)
            if coreHigh > coreLow:
                for b in pine_range(0, nBins - 1):
                    binTop: float = top - b * binH
                    binBot: float = binTop - binH
                    ov_h: float = math.min(coreHigh, binTop)
                    ov_l: float = math.max(coreLow, binBot)
                    if ov_h > ov_l:
                        overlap: float = ov_h - ov_l
                        addedVol: float = bV * overlap / fullRange
                        bullPart: float = addedVol * (bC - bL) / fullRange
                        bearPart: float = addedVol * (bH - bC) / fullRange
                        array.set(bullBins, b, array.get(bullBins, b) + bullPart)
                        array.set(bearBins, b, array.get(bearBins, b) + bearPart)
            __block_result_5__ = na
            if not clip:
                if bH > top:
                    overlapAbove: float = bH - math.max(bL, top)
                    if overlapAbove > 0:
                        addedVol2: float = bV * overlapAbove / fullRange
                        bullPart2: float = addedVol2 * (bC - bL) / fullRange
                        bearPart2: float = addedVol2 * (bH - bC) / fullRange
                        array.set(bullBins, 0, array.get(bullBins, 0) + bullPart2)
                        array.set(bearBins, 0, array.get(bearBins, 0) + bearPart2)
                __block_result_6__ = na
                if bL < bot:
                    overlapBelow: float = math.min(bH, bot) - bL
                    __block_result_7__ = na
                    if overlapBelow > 0:
                        addedVol3: float = bV * overlapBelow / fullRange
                        bullPart3: float = addedVol3 * (bC - bL) / fullRange
                        bearPart3: float = addedVol3 * (bH - bC) / fullRange
                        array.set(bullBins, nBins - 1, array.get(bullBins, nBins - 1) + bullPart3)
                        __block_result_7__ = array.set(bearBins, nBins - 1, array.get(bearBins, nBins - 1) + bearPart3)
                    __block_result_6__ = __block_result_7__
                __block_result_5__ = __block_result_6__
            __block_result_4__ = __block_result_5__
        return __block_result_4__

    if not na(ph):
        array.push(hP, ph)
        array.push(hL, low[length])
        array.push(hI, bar_index - length)
        array.push(hTi, time[length])
        array.push(hT, 0)
        array.push(hIn, False)
        array.push(hTB, '')
        if array.size(hP) > 40:
            array.shift(hP)
            array.shift(hL)
            array.shift(hI)
            array.shift(hTi)
            array.shift(hT)
            array.shift(hIn)
            array.shift(hTB)

    if not na(pl):
        array.push(lP, pl)
        array.push(lH, high[length])
        array.push(lI, bar_index - length)
        array.push(lTi, time[length])
        array.push(lT, 0)
        array.push(lIn, False)
        array.push(lTB, '')
        if array.size(lP) > 40:
            array.shift(lP)
            array.shift(lH)
            array.shift(lI)
            array.shift(lTi)
            array.shift(lT)
            array.shift(lIn)
            array.shift(lTB)

    if array.size(hP) > 0:
        for i in pine_range(array.size(hP) - 1, 0):
            p = array.get(hP, i)
            plo = array.get(hL, i)
            if close > p + brk:
                array.remove(hP, i)
                array.remove(hL, i)
                array.remove(hI, i)
                array.remove(hTi, i)
                array.remove(hT, i)
                array.remove(hIn, i)
                array.remove(hTB, i)
            elif low <= p and high >= plo:
                if not array.get(hIn, i):
                    array.set(hT, i, array.get(hT, i) + 1)
                    array.set(hIn, i, True)
                    array.set(hTB, i, appendTest(array.get(hTB, i), bar_index))
            else:
                array.set(hIn, i, False)

    if array.size(lP) > 0:
        for i in pine_range(array.size(lP) - 1, 0):
            p = array.get(lP, i)
            phi = array.get(lH, i)
            if close < p - brk:
                array.remove(lP, i)
                array.remove(lH, i)
                array.remove(lI, i)
                array.remove(lTi, i)
                array.remove(lT, i)
                array.remove(lIn, i)
                array.remove(lTB, i)
            elif high >= p and low <= phi:
                if not array.get(lIn, i):
                    array.set(lT, i, array.get(lT, i) + 1)
                    array.set(lIn, i, True)
                    array.set(lTB, i, appendTest(array.get(lTB, i), bar_index))
            else:
                array.set(lIn, i, False)

    pairH: int = na(int)
    pairL: int = na(int)
    bestStart: int = na(int)

    if array.size(hP) > 0 and array.size(lP) > 0:
        for i in pine_range(0, array.size(hP) - 1):
            if array.get(hT, i) >= 1:
                hp = array.get(hP, i)
                hIx = array.get(hI, i)
                for j in pine_range(0, array.size(lP) - 1):
                    if array.get(lT, j) >= 1:
                        lp = array.get(lP, j)
                        lIx = array.get(lI, j)
                        if hp > lp:
                            startIdx = math.min(hIx, lIx)
                            barsBack = bar_index - startIdx
                            okRange = barsBack >= 0 and barsBack <= maxPairBars
                            if okRange:
                                contained: bool = True
                                for k in pine_range(1, barsBack):
                                    if close[k] > hp + brk or close[k] < lp - brk:
                                        contained = False
                                passesAtr = not useAtrCap or hp - lp <= maxMultBox * atrVal
                                if contained and passesAtr:
                                    if na(bestStart) or startIdx < bestStart:
                                        bestStart = startIdx
                                        pairH = i
                                        pairL = j

    if not zoneActive and (not na(pairH)) and (not na(pairL)):
        zoneActive = True
        zoneTop = array.get(hP, pairH)
        zoneBottom = array.get(lP, pairL)
        pivotOff = bar_index - math.min(array.get(hI, pairH), array.get(lI, pairL))
        leftOff, startTime = leftEdgeTime(zoneTop, zoneBottom, pivotOff, brk, maxLeftBack)
        zoneLeftIdx = bar_index - leftOff
        zoneBox = box.new(startTime, zoneTop, time, zoneBottom, border_color=color.new(colNeutral, zoneBorderTransp), bgcolor=color.new(colNeutral, zoneBgTransp), xloc=xloc.bar_time)
        if showPivotMarkers:
            label.new(array.get(hI, pairH), zoneTop, '▼', style=label.style_label_down, color=colBear, textcolor=color.white, size=markerSize)
            label.new(array.get(lI, pairL), zoneBottom, '▲', style=label.style_label_up, color=colBull, textcolor=color.white, size=markerSize)
        if showTestMarkers:
            markTests(array.get(hTB, pairH), zoneTop, colBear)
            markTests(array.get(lTB, pairL), zoneBottom, colBull)

        if array.size(profBullBox) > 0:
            for i in pine_range(0, array.size(profBullBox) - 1):
                bb = array.get(profBullBox, i)
                if not na(bb):
                    box.delete(bb)
                be = array.get(profBearBox, i)
                if not na(be):
                    box.delete(be)
        profBullVol = array.new_float(profileBins, 0.0)
        profBearVol = array.new_float(profileBins, 0.0)
        profBullBox = array.new_box(profileBins, na)
        profBearBox = array.new_box(profileBins, na)

        if leftOff > 0:
            for k in pine_range(1, leftOff):
                f_addBarToProfile(profBullVol, profBearVol, profileBins, zoneTop, zoneBottom, high[k], low[k], close[k], volume[k], not includeOuterWicks)

        if showBoxVolBars:
            bullVolBox = box.new(zoneLeftIdx, zoneBottom, zoneLeftIdx, zoneBottom, bgcolor=color.new(colBull, 15), border_color=color.new(colBull, 15), xloc=xloc.bar_index)
            bearVolBox = box.new(zoneLeftIdx, zoneBottom, zoneLeftIdx, zoneBottom, bgcolor=color.new(colBear, 15), border_color=color.new(colBear, 15), xloc=xloc.bar_index)
        if showBoxVolLabel:
            volPctLabel = label.new(zoneLeftIdx, zoneBottom, '', style=label.style_label_upper_left, color=colNeutral, textcolor=color.white, size=volLabelSize, xloc=xloc.bar_index)

    bullBreakoutSignal: bool = False
    bearBreakoutSignal: bool = False

    if zoneActive:
        box.set_right(zoneBox, time)

        breakoutUp: bool = close > zoneTop + brk
        breakoutDown: bool = close < zoneBottom - brk
        isBreakoutBar: bool = breakoutUp or breakoutDown

        if not isBreakoutBar:
            f_addBarToProfile(profBullVol, profBearVol, profileBins, zoneTop, zoneBottom, high, low, close, volume, not includeOuterWicks)

        if showProfile:
            maxBinTotal: float = 0.0
            for b in pine_range(0, profileBins - 1):
                tot = array.get(profBullVol, b) + array.get(profBearVol, b)
                if tot > maxBinTotal:
                    maxBinTotal = tot

            nominalBinH = (zoneTop - zoneBottom) / profileBins
            binGapAmt = nominalBinH * PROFILE_BIN_GAP_PCT / 100.0
            totalGapSpace = binGapAmt * (profileBins - 1)
            binH = (zoneTop - zoneBottom - totalGapSpace) / profileBins
            leftAnchor = bar_index + 1

            for b in pine_range(0, profileBins - 1):
                bullV = array.get(profBullVol, b)
                bearV = array.get(profBearVol, b)
                tot = bullV + bearV
                width = math.round(profileWidth * tot / maxBinTotal) if maxBinTotal > 0 else 0.0
                bullW = math.round(width * bullV / tot) if tot > 0 else 0.0
                bearW = width - bullW

                binTop = zoneTop - b * (binH + binGapAmt)
                binBot = binTop - binH

                bullLeft = leftAnchor
                bullRight = leftAnchor + cast_int(bullW)
                bearLeft = bullRight
                bearRight = bullRight + cast_int(bearW)

                existingBull = array.get(profBullBox, b)
                if na(existingBull):
                    newBull = box.new(bullLeft, binTop, bullRight, binBot, border_color=color.new(colBull, profileTransp), border_width=1, bgcolor=color.new(colBull, profileTransp), xloc=xloc.bar_index)
                    array.set(profBullBox, b, newBull)
                else:
                    box.set_left(existingBull, bullLeft)
                    box.set_right(existingBull, bullRight)
                    box.set_top(existingBull, binTop)
                    box.set_bottom(existingBull, binBot)

                existingBear = array.get(profBearBox, b)
                if na(existingBear):
                    newBear = box.new(bearLeft, binTop, bearRight, binBot, border_color=color.new(colBear, profileTransp), border_width=1, bgcolor=color.new(colBear, profileTransp), xloc=xloc.bar_index)
                    array.set(profBearBox, b, newBear)
                else:
                    box.set_left(existingBear, bearLeft)
                    box.set_right(existingBear, bearRight)
                    box.set_top(existingBear, binTop)
                    box.set_bottom(existingBear, binBot)

        totalBull = array.sum(profBullVol)
        totalBear = array.sum(profBearVol)

        if showBoxVolBars or showBoxVolLabel:
            barH2: float = atrVal * 0.18
            gapH2: float = atrVal * 0.08
            bullTop2: float = zoneBottom - gapH2
            bullBot2: float = bullTop2 - barH2
            bearTop2: float = bullBot2 - gapH2
            bearBot2: float = bearTop2 - barH2

            if showBoxVolBars:
                totalVolBars: float = totalBull + totalBear
                fullWidth2: int = math.max(bar_index + 1 - zoneLeftIdx, 1)
                bullRight2: int = zoneLeftIdx + math.round(fullWidth2 * (totalBull / totalVolBars)) if totalVolBars > 0 else zoneLeftIdx + math.round(fullWidth2 * 0.5)
                bearRight2: int = zoneLeftIdx + math.round(fullWidth2 * (totalBear / totalVolBars)) if totalVolBars > 0 else zoneLeftIdx + math.round(fullWidth2 * 0.5)

                box.set_lefttop(bullVolBox, zoneLeftIdx, bullTop2)
                box.set_rightbottom(bullVolBox, bullRight2, bullBot2)
                box.set_lefttop(bearVolBox, zoneLeftIdx, bearTop2)
                box.set_rightbottom(bearVolBox, bearRight2, bearBot2)

            if showBoxVolLabel:
                totalVolL: float = totalBull + totalBear
                bullPctL: float = math.round(totalBull / totalVolL * 100.0 * 10) / 10 if totalVolL > 0 else 50.0
                sellPctL: float = 100.0 - bullPctL
                bgColL: Color = colBull if bullPctL > 50.0 else colBear if bullPctL < 50.0 else colNeutral
                txtL: str = 'Buy ' + string.tostring(bullPctL, '#.#') + '%\nSell ' + string.tostring(sellPctL, '#.#') + '%'
                label.set_xy(volPctLabel, zoneLeftIdx, bearBot2 - gapH2 * 0.5)
                label.set_text(volPctLabel, txtL)
                label.set_color(volPctLabel, bgColL)

        if isBreakoutBar:
            bullDominant: bool = totalBull >= totalBear
            bearDominant: bool = totalBear > totalBull
            validUp: bool = breakoutUp and (not requireVolConfirmation or bullDominant)
            validDown: bool = breakoutDown and (not requireVolConfirmation or bearDominant)

            if showBreakoutSignals:
                bullBreakoutSignal = validUp
                bearBreakoutSignal = validDown

            if recolorBoxOnBreakout:
                if validUp:
                    box.set_bgcolor(zoneBox, color.new(colBull, zoneBgTransp))
                    box.set_border_color(zoneBox, color.new(colBull, zoneBorderTransp))
                elif validDown:
                    box.set_bgcolor(zoneBox, color.new(colBear, zoneBgTransp))
                    box.set_border_color(zoneBox, color.new(colBear, zoneBorderTransp))

            zoneActive = False

    if showTargets and (bullBreakoutSignal or bearBreakoutSignal):
        isBuyTrade: bool = bullBreakoutSignal

        line.delete(tpslEntryLn)
        label.delete(tpslEntryLb)
        line.delete(tpslSlLn)
        label.delete(tpslSlLb)
        line.delete(tpslTp1Ln)
        label.delete(tpslTp1Lb)
        line.delete(tpslTp2Ln)
        label.delete(tpslTp2Lb)
        line.delete(tpslTp3Ln)
        label.delete(tpslTp3Lb)
        line.delete(tpslExtLn)
        linefill.delete(tpslRiskFill)
        linefill.delete(tpslRewardFill)

        tpslDir = 1 if isBuyTrade else -1
        tpslEntryBar = bar_index

        entryP: float = close
        riskDist: float = atrTP * slAtrMult if useAtrSL else entryP * (slPercent / 100.0)

        entryCol: Color = color.new(colBull if isBuyTrade else colBear, 40)
        slCol: Color = color.new(colBear if isBuyTrade else colBull, 40)
        tpCol: Color = color.new(colBull if isBuyTrade else colBear, 40)
        riskFillC: Color = color.new(colBear if isBuyTrade else colBull, 80)
        rewardFillC: Color = color.new(colBull if isBuyTrade else colBear, 80)

        slP: float = entryP - riskDist if isBuyTrade else entryP + riskDist
        tp1P: float = entryP + riskDist * rrTP1 if isBuyTrade else entryP - riskDist * rrTP1
        tp2P: float = entryP + riskDist * rrTP2 if isBuyTrade else entryP - riskDist * rrTP2
        tp3P: float = entryP + riskDist * rrTP3 if isBuyTrade else entryP - riskDist * rrTP3

        tpslSL = slP
        tpslExtreme = tp3P if showTp3Level else tp2P if showTp2Level else tp1P if showTp1Level else na

        tpslEntryLn = line.new(bar_index, entryP, bar_index + 1, entryP, color=entryCol, width=2, extend=extend.none)
        tpslEntryLb = label.new(bar_index, entryP, ('BUY ' if isBuyTrade else 'SELL ') + string.tostring(entryP, format.mintick), style=label.style_label_left, color=entryCol, textcolor=color.white, size=size.small)

        if showSlLevel:
            tpslSlLn = line.new(bar_index, slP, bar_index + 1, slP, color=slCol, width=1, style=line.style_dashed, extend=extend.none)
            tpslSlLb = label.new(bar_index, slP, 'SL ' + string.tostring(slP, format.mintick), style=label.style_label_left, color=slCol, textcolor=color.white, size=size.small)

        if showTp1Level:
            tpslTp1Ln = line.new(bar_index, tp1P, bar_index + 1, tp1P, color=tpCol, width=1, extend=extend.none)
            tpslTp1Lb = label.new(bar_index, tp1P, 'TP1 ' + string.tostring(tp1P, format.mintick), style=label.style_label_left, color=tpCol, textcolor=color.white, size=size.small)

        if showTp2Level:
            tpslTp2Ln = line.new(bar_index, tp2P, bar_index + 1, tp2P, color=tpCol, width=1, extend=extend.none)
            tpslTp2Lb = label.new(bar_index, tp2P, 'TP2 ' + string.tostring(tp2P, format.mintick), style=label.style_label_left, color=tpCol, textcolor=color.white, size=size.small)

        if showTp3Level:
            tpslTp3Ln = line.new(bar_index, tp3P, bar_index + 1, tp3P, color=tpCol, width=1, style=line.style_dotted, extend=extend.none)
            tpslTp3Lb = label.new(bar_index, tp3P, 'TP3 ' + string.tostring(tp3P, format.mintick), style=label.style_label_left, color=tpCol, textcolor=color.white, size=size.small)

        if showSlLevel:
            tpslRiskFill = linefill.new(tpslEntryLn, tpslSlLn, riskFillC)

        fillExtreme: float = entryP
        if isBuyTrade:
            if showTp1Level:
                fillExtreme = math.max(fillExtreme, tp1P)
            if showTp2Level:
                fillExtreme = math.max(fillExtreme, tp2P)
            if showTp3Level:
                fillExtreme = math.max(fillExtreme, tp3P)
            if fillExtreme > entryP:
                tpslExtLn = line.new(bar_index, fillExtreme, bar_index + 1, fillExtreme, color=na, extend=extend.none)
                tpslRewardFill = linefill.new(tpslEntryLn, tpslExtLn, rewardFillC)
        else:
            if showTp1Level:
                fillExtreme = math.min(fillExtreme, tp1P)
            if showTp2Level:
                fillExtreme = math.min(fillExtreme, tp2P)
            if showTp3Level:
                fillExtreme = math.min(fillExtreme, tp3P)
            if fillExtreme < entryP:
                tpslExtLn = line.new(bar_index, fillExtreme, bar_index + 1, fillExtreme, color=na, extend=extend.none)
                tpslRewardFill = linefill.new(tpslEntryLn, tpslExtLn, rewardFillC)

    if tpslDir != 0:
        if not na(tpslEntryLb):
            label.set_x(tpslEntryLb, bar_index)
        if not na(tpslSlLb):
            label.set_x(tpslSlLb, bar_index)
        if not na(tpslTp1Lb):
            label.set_x(tpslTp1Lb, bar_index)
        if not na(tpslTp2Lb):
            label.set_x(tpslTp2Lb, bar_index)
        if not na(tpslTp3Lb):
            label.set_x(tpslTp3Lb, bar_index)

        if not na(tpslEntryLn):
            line.set_x2(tpslEntryLn, bar_index + 1)
        if not na(tpslSlLn):
            line.set_x2(tpslSlLn, bar_index + 1)
        if not na(tpslTp1Ln):
            line.set_x2(tpslTp1Ln, bar_index + 1)
        if not na(tpslTp2Ln):
            line.set_x2(tpslTp2Ln, bar_index + 1)
        if not na(tpslTp3Ln):
            line.set_x2(tpslTp3Ln, bar_index + 1)
        if not na(tpslExtLn):
            line.set_x2(tpslExtLn, bar_index + 1)

        slHit: bool = low <= tpslSL if tpslDir == 1 else high >= tpslSL
        tpHit: bool = not na(tpslExtreme) and (high >= tpslExtreme if tpslDir == 1 else low <= tpslExtreme)

        if bar_index > tpslEntryBar and (slHit or tpHit):
            if not na(tpslEntryLn):
                line.set_x2(tpslEntryLn, bar_index)
            if not na(tpslSlLn):
                line.set_x2(tpslSlLn, bar_index)
            if not na(tpslTp1Ln):
                line.set_x2(tpslTp1Ln, bar_index)
            if not na(tpslTp2Ln):
                line.set_x2(tpslTp2Ln, bar_index)
            if not na(tpslTp3Ln):
                line.set_x2(tpslTp3Ln, bar_index)
            if not na(tpslExtLn):
                line.set_x2(tpslExtLn, bar_index)
            tpslDir = 0

    plot(1 if bullBreakoutSignal else na, 'backtest_buy', display=display.none)
    plot(1 if bearBreakoutSignal else na, 'backtest_sell', display=display.none)

    plotshape(bullBreakoutSignal and signalSizeInput == 'Tiny', title='Breakout Up (Tiny)', style=shape.triangleup, location=location.belowbar, color=colBull, size=size.tiny)
    plotshape(bullBreakoutSignal and signalSizeInput == 'Small', title='Breakout Up (Small)', style=shape.triangleup, location=location.belowbar, color=colBull, size=size.small)
    plotshape(bullBreakoutSignal and signalSizeInput == 'Normal', title='Breakout Up (Normal)', style=shape.triangleup, location=location.belowbar, color=colBull, size=size.normal)

    plotshape(bearBreakoutSignal and signalSizeInput == 'Tiny', title='Breakout Down (Tiny)', style=shape.triangledown, location=location.abovebar, color=colBear, size=size.tiny)
    plotshape(bearBreakoutSignal and signalSizeInput == 'Small', title='Breakout Down (Small)', style=shape.triangledown, location=location.abovebar, color=colBear, size=size.small)
    plotshape(bearBreakoutSignal and signalSizeInput == 'Normal', title='Breakout Down (Normal)', style=shape.triangledown, location=location.abovebar, color=colBear, size=size.normal)

    alertcondition(bullBreakoutSignal, title='Zone Breakout Up', message='Consolidation zone breakout to the UPSIDE')
    alertcondition(bearBreakoutSignal, title='Zone Breakout Down', message='Consolidation zone breakout to the DOWNSIDE')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)