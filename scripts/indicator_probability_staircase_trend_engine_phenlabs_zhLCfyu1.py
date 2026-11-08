"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from enum import StrEnum as Enum
from pynecore import pine_range
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, box, close, color, display,
    fill, high, hl2, input, label, line, location, low, math, na, plot, plotshape, position,
    script, shape, size, string, ta, table, text, xloc, yloc
)
from pynecore.types import Box, Color, Label, Line, NA, Persistent, PersistentSeries, Table


class Sensitivity(Enum):
    fast = 'Fast'
    balanced = 'Balanced'
    slow = 'Slow'


class Ladder(Enum):
    conservative = 'Conservative (70 / 50 / 30%)'
    balanced = 'Balanced (60 / 40 / 20%)'
    aggressive = 'Aggressive (50 / 30 / 15%)'


class TableSize(Enum):
    tiny = 'Tiny'
    small = 'Small'
    normal = 'Normal'


@udt
class Outcome:
    bucket: int = na(int)
    dir: int = na(int)
    mfeR: float = na(float)
    exitR: float = na(float)
    r0: int = -1
    r1: int = -1
    r2: int = -1
    r3: int = -1
    r4: int = -1
    r5: int = -1
    r6: int = -1
    r7: int = -1


@udt
class Plan:
    zStop: Box = na(Box)
    z1: Box = na(Box)
    z2: Box = na(Box)
    z3: Box = na(Box)
    l1: Label = na(Label)
    l2: Label = na(Label)
    l3: Label = na(Label)
    lS: Label = na(Label)
    ent: Line = na(Line)
    g1: int = -1
    g2: int = -1
    g3: int = -1
    col: Color = na(Color)
    live: bool = True


G1: str = "Trend Engine"
G2: str = "Calibration"
G3: str = "Visuals"
MAX_STORE: int = 300
NEUTRAL: Color = color.new('#8A93A6')
CLEAR: Color = color.new('#00000000')
DASH_BG: Color = color.new('#0F131C')
DASH_TXT: Color = color.new('#D6DAE3')


@script.indicator("Probability Staircase Trend Engine [PhenLabs]", shorttitle="PSTE [PhenLabs]", overlay=True, max_boxes_count=40, max_labels_count=40, max_lines_count=20)
def main(
    sensIn=input.enum(Sensitivity.balanced, "Trend Sensitivity", group=G1, tooltip="Preset for the efficiency-adaptive baseline and its ATR trailing band. Fast = more flips, Slow = fewer, longer trends."),
    stopLen=input.int(10, "Stop Swing Lookback", minval=3, maxval=50, group=G1, tooltip="Bars used to find the structural swing extreme for the stop. Risk (1R) is clamped between 0.5 and 3 ATR."),
    horizon=input.int(60, "Plan Horizon (bars)", minval=10, maxval=300, group=G1, tooltip="A shadow trade that has not been stopped or reversed after this many bars is closed and recorded."),
    minN=input.int(20, "Minimum Sample", minval=8, maxval=150, group=G2, tooltip="Resolved flips required before a pool is trusted. Pools fall back: same direction + context, then same direction, then all flips."),
    ladderIn=input.enum(Ladder.balanced, "Target Ladder", group=G2, tooltip="Reach probabilities used to place T1 / T2 / T3 on the survival curve."),
    useCtx=input.bool(True, "Split by Trend Efficiency", group=G2, tooltip="Separate evidence for flips that happen in clean (efficient) vs choppy conditions."),
    showPlan=input.bool(True, "Show Probability Staircase", group=G3),
    keepPlans=input.int(2, "Past Plans Kept", minval=0, maxval=5, group=G3, tooltip="Resolved plans stay on the chart, frozen at their exit bar, with a check mark on every target that was reached."),
    showSkip=input.bool(True, "Show SKIP Flips", group=G3, tooltip="Grey markers for flips whose evidence says the T1 plan had negative expectancy."),
    bullCol=input.color(color.new('#00A8C6'), "Bull", inline="col", group=G3),
    bearCol=input.color(color.new('#F0457A'), "Bear", inline="col", group=G3),
    showDash=input.bool(True, "Show Dashboard", group=G3),
    tblIn=input.enum(TableSize.small, "Table Size", group=G3)
):
    erLen: int = 8 if sensIn == Sensitivity.fast else 14 if sensIn == Sensitivity.slow else 10
    slowLen: int = 20 if sensIn == Sensitivity.fast else 40 if sensIn == Sensitivity.slow else 30
    bandK: float = 1.0 if sensIn == Sensitivity.fast else 2.0 if sensIn == Sensitivity.slow else 1.5

    p1: float = 0.7 if ladderIn == Ladder.conservative else 0.5 if ladderIn == Ladder.aggressive else 0.6
    p2: float = 0.5 if ladderIn == Ladder.conservative else 0.3 if ladderIn == Ladder.aggressive else 0.4
    p3: float = 0.3 if ladderIn == Ladder.conservative else 0.15 if ladderIn == Ladder.aggressive else 0.2

    tSz: str = size.tiny if tblIn == TableSize.tiny else size.normal if tblIn == TableSize.normal else size.small


    @method
    def reachAt(this: Outcome, g: int):
        __block_result__ = na
        __switch__ = g
        if __switch__ == 0:
            __block_result__ = this.r0
        elif __switch__ == 1:
            __block_result__ = this.r1
        elif __switch__ == 2:
            __block_result__ = this.r2
        elif __switch__ == 3:
            __block_result__ = this.r3
        elif __switch__ == 4:
            __block_result__ = this.r4
        elif __switch__ == 5:
            __block_result__ = this.r5
        elif __switch__ == 6:
            __block_result__ = this.r6
        else:
            __block_result__ = this.r7
        v: int = __block_result__
        return v

    def f_inPool(o: Outcome, lvl: int, bucket: int, dirIdx: int):
        return o.bucket == bucket if lvl == 0 else o.dir == dirIdx if lvl == 1 else True

    def f_stats(store: list[Outcome], grid: list[float], bucket: int, dirIdx: int, minCount: int, q1: float, q2: float, q3: float):
        nB: int = 0
        nD: int = 0
        nA: int = array.size(store)
        for o in store:
            if o.bucket == bucket:
                nB += 1
            if o.dir == dirIdx:
                nD += 1
        lvl: int = 0 if nB >= minCount else 1 if nD >= minCount else 2 if nA >= minCount else 3
        n: int = nB if lvl == 0 else nD if lvl == 1 else nA
        g1: int = -1
        g2: int = -1
        g3: int = -1
        s1: float = na(float)
        s2: float = na(float)
        s3: float = na(float)
        edge: float = na(float)
        if lvl < 3 and n > 0:
            surv: list[float] = array.new_float(8, 0.0)
            for o in store:
                if f_inPool(o, lvl, bucket, dirIdx):
                    for g in pine_range(0, 7):
                        if o.mfeR >= array.get(grid, g):
                            array.set(surv, g, array.get(surv, g) + 1.0)
            for g in pine_range(0, 7):
                array.set(surv, g, array.get(surv, g) / n)
            for g in pine_range(0, 7):
                sv: float = array.get(surv, g)
                if sv >= q1:
                    g1 = g
                if sv >= q2:
                    g2 = g
                if sv >= q3:
                    g3 = g
            if g2 == g1:
                g2 = -1
            prevG: int = g2 if g2 >= 0 else g1
            if g3 == prevG:
                g3 = -1
            s1 = array.get(surv, math.max(g1, 0)) if g1 >= 0 else na
            s2 = array.get(surv, math.max(g2, 0)) if g2 >= 0 else na
            s3 = array.get(surv, math.max(g3, 0)) if g3 >= 0 else na

            tgt: float = array.get(grid, math.max(g1, 0))
            acc: float = 0.0
            for o in store:
                if f_inPool(o, lvl, bucket, dirIdx):
                    acc += tgt if o.mfeR >= tgt else o.exitR
            edge = acc / n
        return (lvl, n, g1, g2, g3, s1, s2, s3, edge)

    def f_medBars(store: list[Outcome], lvl: int, bucket: int, dirIdx: int, g: int):
        med: float = na(float)
        if g >= 0 and lvl < 3:
            tmp: list[int] = array.new_int()
            for o in store:
                rb: int = reachAt(o, g)
                if f_inPool(o, lvl, bucket, dirIdx) and rb >= 0:
                    array.push(tmp, rb)
            if array.size(tmp) > 0:
                med = array.median(tmp)
        return med

    def f_rTxt(r: float):
        return string.tostring(r, '#.#') + 'R'

    def f_pctTxt(s: float):
        return 'n/a' if na(s) else string.tostring(math.round(s * 100)) + '%'

    def f_freezeBox(b: Box, atBar: int):
        __block_result_1__ = na
        if not na(b):
            __block_result_1__ = box.set_right(b, math.min(box.get_right(b), atBar))
        return __block_result_1__

    def f_freezeLabel(l: Label, atBar: int, mark: bool, suffix: str):
        __block_result_2__ = na
        if not na(l):
            label.set_x(l, math.min(label.get_x(l), atBar))
            __block_result_3__ = na
            if mark:
                __block_result_3__ = label.set_text(l, label.get_text(l) + suffix)
            __block_result_2__ = __block_result_3__
        return __block_result_2__

    def f_fadeBox(b: Box, c: Color, bgT: int, bdT: int):
        __block_result_4__ = na
        if not na(b):
            box.set_bgcolor(b, color.new(c, bgT))
            __block_result_4__ = box.set_border_color(b, color.new(c, bdT))
        return __block_result_4__

    def f_fadeLabel(l: Label, c: Color):
        __block_result_5__ = na
        if not na(l):
            __block_result_5__ = label.set_textcolor(l, color.new(c, 45))
        return __block_result_5__

    def f_eraseBox(b: Box):
        __block_result_6__ = na
        if not na(b):
            __block_result_6__ = box.delete(b)
        return __block_result_6__

    def f_eraseLabel(l: Label):
        __block_result_7__ = na
        if not na(l):
            __block_result_7__ = label.delete(l)
        return __block_result_7__

    def f_drawTarget(x0: int, x1: int, yFrom: float, yTo: float, c: Color, prob: float, txt: str, tip: str):
        bgT: int = 88 if na(prob) else math.round(88 - prob * 20)
        b: Box = box.new(x0, math.max(yFrom, yTo), x1, math.min(yFrom, yTo), border_color=color.new(c, 55), border_width=1, bgcolor=color.new(c, bgT), xloc=xloc.bar_index)
        l: Label = label.new(x1, yTo, txt, xloc=xloc.bar_index, yloc=yloc.price, color=CLEAR, style=label.style_label_left, textcolor=c, size=size.small, tooltip=tip)
        return (b, l)

    atr: float = ta.atr(14)
    netMove: float = math.abs(close - close[erLen])
    pathLen: float = math.sum(math.abs(ta.change(close)), erLen)
    er: float = 0.0 if na(netMove) or na(pathLen) or pathLen <= 0 else netMove / pathLen
    erMed: float = ta.percentile_linear_interpolation(er, 200, 50)
    cleanCtx: bool = er >= 0.3 if na(erMed) else er >= erMed

    fastSC: float = 2.0 / 3.0
    slowSC: float = 2.0 / (slowLen + 1)
    sc: float = math.pow(er * (fastSC - slowSC) + slowSC, 2)
    kama: Persistent[float] = na(float)
    kama = close if na(kama) else kama + sc * (close - kama)

    swingLo: float = ta.lowest(low, stopLen)
    swingHi: float = ta.highest(high, stopLen)

    trail: Persistent[float] = na(float)
    trend: PersistentSeries[int] = 0
    flipUp: bool = False
    flipDn: bool = False
    if not na(atr):
        upTrail: float = kama - bandK * atr
        dnTrail: float = kama + bandK * atr
        if trend == 0:
            trend = 1 if close >= kama else -1
            trail = upTrail if trend == 1 else dnTrail
        elif trend == 1:
            trail = math.max(trail, upTrail)
            if close < trail:
                trend = -1
                trail = dnTrail
                flipDn = True
        else:
            trail = math.min(trail, dnTrail)
            if close > trail:
                trend = 1
                trail = upTrail
                flipUp = True

    sigUp: bool = flipUp and barstate.isconfirmed
    sigDn: bool = flipDn and barstate.isconfirmed

    grid: Persistent[list[float]] = array.from_items(0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0)
    store: Persistent[list[Outcome]] = array.new(0, NA(Outcome))
    plans: Persistent[list[Plan]] = array.new(0, NA(Plan))
    tReach: Persistent[list[int]] = array.new_int(8, -1)

    tOpen: Persistent[bool] = False
    tDir: Persistent[int] = 0
    tBucket: Persistent[int] = 0
    tStartBar: Persistent[int] = na(int)
    tEntry: Persistent[float] = na(float)
    tRisk: Persistent[float] = na(float)
    tStop: Persistent[float] = na(float)
    tMfe: Persistent[float] = 0.0
    ties: Persistent[int] = 0
    resolved: Persistent[int] = 0
    lastExit: Persistent[str] = "—"

    lastDir: Persistent[int] = 0
    lastVerdict: Persistent[int] = -1
    lastSigBar: Persistent[int] = na(int)
    pLvl: Persistent[int] = 3
    pN: Persistent[int] = 0
    pG1: Persistent[int] = -1
    pG2: Persistent[int] = -1
    pG3: Persistent[int] = -1
    pS1: Persistent[float] = na(float)
    pS2: Persistent[float] = na(float)
    pS3: Persistent[float] = na(float)
    pM1: Persistent[float] = na(float)
    pM2: Persistent[float] = na(float)
    pM3: Persistent[float] = na(float)
    pEdge: Persistent[float] = na(float)
    pCtxClean: Persistent[bool] = True

    resolveNow: bool = False
    stopped: bool = False
    if barstate.isconfirmed and tOpen and (bar_index > tStartBar) and (tRisk > 0):
        stopHit: bool = low <= tStop if tDir == 1 else high >= tStop
        barMfe: float = (high - tEntry) / tRisk if tDir == 1 else (tEntry - low) / tRisk
        if stopHit:
            wouldReach: bool = False
            for g in pine_range(0, 7):
                if array.get(tReach, g) < 0 and barMfe >= array.get(grid, g):
                    wouldReach = True
            if wouldReach:
                ties += 1
            resolveNow = True
            stopped = True
        else:
            if barMfe > tMfe:
                tMfe = barMfe
                for g in pine_range(0, 7):
                    if array.get(tReach, g) < 0 and tMfe >= array.get(grid, g):
                        array.set(tReach, g, bar_index - tStartBar)
            if bar_index - tStartBar >= horizon:
                resolveNow = True
        if sigUp or sigDn:
            resolveNow = True

    if resolveNow:
        exitR: float = -1.0 if stopped else tDir * (close - tEntry) / tRisk
        o: Outcome = Outcome(bucket=tBucket, dir=0 if tDir == 1 else 1, mfeR=math.max(tMfe, 0.0), exitR=exitR, r0=array.get(tReach, 0), r1=array.get(tReach, 1), r2=array.get(tReach, 2), r3=array.get(tReach, 3), r4=array.get(tReach, 4), r5=array.get(tReach, 5), r6=array.get(tReach, 6), r7=array.get(tReach, 7))
        array.push(store, o)
        if array.size(store) > MAX_STORE:
            array.shift(store)
        resolved += 1
        lastExit = 'stopped' if stopped else 'reversed' if sigUp or sigDn else 'horizon'
        tOpen = False
        if array.size(plans) > 0:
            lp: Plan = array.last(plans)
            if lp.live:
                f_freezeBox(lp.zStop, bar_index)
                f_freezeBox(lp.z1, bar_index)
                f_freezeBox(lp.z2, bar_index)
                f_freezeBox(lp.z3, bar_index)
                f_freezeLabel(lp.l1, bar_index, lp.g1 >= 0 and array.get(tReach, math.max(lp.g1, 0)) >= 0, ' ✓')
                f_freezeLabel(lp.l2, bar_index, lp.g2 >= 0 and array.get(tReach, math.max(lp.g2, 0)) >= 0, ' ✓')
                f_freezeLabel(lp.l3, bar_index, lp.g3 >= 0 and array.get(tReach, math.max(lp.g3, 0)) >= 0, ' ✓')
                f_freezeLabel(lp.lS, bar_index, stopped, ' ✕')
                if not na(lp.ent):
                    line.set_x2(lp.ent, math.min(line.get_x2(lp.ent), bar_index))
                lp.live = False

    if (sigUp or sigDn) and (not na(atr)) and (atr > 0):
        dirSign: int = 1 if sigUp else -1
        dirIdx: int = 0 if sigUp else 1
        entry: float = close
        swing: float = swingLo if sigUp else swingHi
        riskRaw: float = atr if na(swing) else entry - swing if dirSign == 1 else swing - entry
        risk: float = math.max(0.5 * atr, math.min(3.0 * atr, riskRaw))
        ctxIdx: int = (0 if cleanCtx else 1) if useCtx else 0
        bucket: int = dirIdx * 2 + ctxIdx

        sLvl, sN, sG1, sG2, sG3, sS1, sS2, sS3, sEdge = f_stats(store, grid, bucket, dirIdx, minN, p1, p2, p3)
        m1: float = f_medBars(store, sLvl, bucket, dirIdx, sG1)
        m2: float = f_medBars(store, sLvl, bucket, dirIdx, sG2)
        m3: float = f_medBars(store, sLvl, bucket, dirIdx, sG3)
        verdict: int = 2 if sLvl == 3 else 1 if sG1 >= 0 and sEdge > 0 else 0

        tOpen = True
        tDir = dirSign
        tBucket = bucket
        tStartBar = bar_index
        tEntry = entry
        tRisk = risk
        tStop = entry - dirSign * risk
        tMfe = 0.0
        array.fill(tReach, -1)

        lastDir = dirSign
        lastVerdict = verdict
        lastSigBar = bar_index
        pLvl = sLvl
        pN = sN
        pG1 = sG1
        pG2 = sG2
        pG3 = sG3
        pS1 = sS1
        pS2 = sS2
        pS3 = sS3
        pM1 = m1
        pM2 = m2
        pM3 = m3
        pEdge = sEdge
        pCtxClean = cleanCtx

        if showPlan:
            if array.size(plans) > 0:
                prev: Plan = array.last(plans)
                f_fadeBox(prev.z1, prev.col, 93, 82)
                f_fadeBox(prev.z2, prev.col, 94, 84)
                f_fadeBox(prev.z3, prev.col, 95, 86)
                f_fadeBox(prev.zStop, NEUTRAL, 94, 86)
                f_fadeLabel(prev.l1, prev.col)
                f_fadeLabel(prev.l2, prev.col)
                f_fadeLabel(prev.l3, prev.col)
                f_fadeLabel(prev.lS, NEUTRAL)
            calib: bool = verdict == 2
            c: Color = NEUTRAL if verdict == 0 else bullCol if dirSign == 1 else bearCol
            opp: Color = bearCol if dirSign == 1 else bullCol

            dg1: int = 1 if calib else sG1
            dg2: int = 3 if calib else sG2
            dg3: int = 5 if calib else sG3
            w1: int = math.round(horizon * 0.25) if calib else math.round(horizon * 0.5) if na(m1) else math.round(m1)
            w2: int = math.round(horizon * 0.5) if calib else math.round(horizon * 0.5) if na(m2) else math.round(m2)
            w3: int = math.round(horizon * 0.75) if calib else math.round(horizon * 0.5) if na(m3) else math.round(m3)
            w1 = math.max(2, math.min(w1, 480))
            w2 = math.max(2, math.min(w2, 480))
            w3 = math.max(2, math.min(w3, 480))
            poolTxt: str = 'same direction + context' if sLvl == 0 else 'same direction' if sLvl == 1 else 'all flips' if sLvl == 2 else 'calibrating'
            tipBase: str = 'Evidence: ' + poolTxt + ' (n=' + string.tostring(sN) + ')'
            pl: Plan = Plan(col=c, g1=dg1, g2=dg2, g3=dg3)
            lastLvl: float = entry
            xMax: int = bar_index + 2
            if dg1 >= 0:
                y1: float = entry + dirSign * array.get(grid, dg1) * risk
                t1: str = 'T1 +' + f_rTxt(array.get(grid, dg1)) + ('' if calib else '  ' + f_pctTxt(sS1) + '  ~' + string.tostring(w1) + ' bars')
                b1, lb1 = f_drawTarget(bar_index, bar_index + w1, lastLvl, y1, c, na if calib else sS1, t1, tipBase)
                pl.z1 = b1
                pl.l1 = lb1
                lastLvl = y1
                xMax = math.max(xMax, bar_index + w1)
            if dg2 >= 0:
                y2: float = entry + dirSign * array.get(grid, dg2) * risk
                t2: str = 'T2 +' + f_rTxt(array.get(grid, dg2)) + ('' if calib else '  ' + f_pctTxt(sS2) + '  ~' + string.tostring(w2) + ' bars')
                b2, lb2 = f_drawTarget(bar_index, bar_index + w2, lastLvl, y2, c, na if calib else sS2, t2, tipBase)
                pl.z2 = b2
                pl.l2 = lb2
                lastLvl = y2
                xMax = math.max(xMax, bar_index + w2)
            if dg3 >= 0:
                y3: float = entry + dirSign * array.get(grid, dg3) * risk
                t3: str = 'T3 +' + f_rTxt(array.get(grid, dg3)) + ('' if calib else '  ' + f_pctTxt(sS3) + '  ~' + string.tostring(w3) + ' bars')
                b3, lb3 = f_drawTarget(bar_index, bar_index + w3, lastLvl, y3, c, na if calib else sS3, t3, tipBase)
                pl.z3 = b3
                pl.l3 = lb3
                xMax = math.max(xMax, bar_index + w3)
            yS: float = tStop
            pl.zStop = box.new(bar_index, math.max(entry, yS), xMax, math.min(entry, yS), border_color=color.new(opp, 60), border_width=1, border_style=line.style_dashed, bgcolor=color.new(NEUTRAL, 88), xloc=xloc.bar_index)
            stopTxt: str = 'Stop −1R · ' + ('SKIP' if verdict == 0 else 'calibrating' if verdict == 2 else 'TAKE')
            pl.lS = label.new(xMax, yS, stopTxt, xloc=xloc.bar_index, yloc=yloc.price, color=CLEAR, style=label.style_label_left, textcolor=NEUTRAL, size=size.small, tooltip=tipBase)
            pl.ent = line.new(bar_index, entry, xMax, entry, xloc=xloc.bar_index, color=color.new(NEUTRAL, 35), style=line.style_dotted, width=1)
            array.push(plans, pl)
            while array.size(plans) > keepPlans + 1:
                old: Plan = array.shift(plans)
                f_eraseBox(old.z1)
                f_eraseBox(old.z2)
                f_eraseBox(old.z3)
                f_eraseBox(old.zStop)
                f_eraseLabel(old.l1)
                f_eraseLabel(old.l2)
                f_eraseLabel(old.l3)
                f_eraseLabel(old.lS)
                if not na(old.ent):
                    line.delete(old.ent)

    trendCol: Color = bullCol if trend == 1 else bearCol if trend == -1 else NEUTRAL
    pTrail = plot(na if trend != trend[1] else trail, 'Trend Trail', trendCol, 2, plot.style_linebr)
    pMid = plot(hl2, 'Mid', display=display.none, editable=False)
    fill(pTrail, pMid, color.new(trendCol, 90), 'Trend Fill')

    takeUp: bool = sigUp and lastVerdict == 1
    takeDn: bool = sigDn and lastVerdict == 1
    skipUp: bool = sigUp and lastVerdict == 0
    skipDn: bool = sigDn and lastVerdict == 0
    calUp: bool = sigUp and lastVerdict == 2
    calDn: bool = sigDn and lastVerdict == 2

    offs: float = 0.0 if na(atr) else 0.35 * atr
    yTakeUp: float = low - offs if takeUp else na
    yTakeDn: float = high + offs if takeDn else na
    ySkipUp: float = low - offs if skipUp and showSkip else na
    ySkipDn: float = high + offs if skipDn and showSkip else na
    yCalUp: float = low - offs if calUp else na
    yCalDn: float = high + offs if calDn else na
    plotshape(yTakeUp, 'Long TAKE', shape.triangleup, location.absolute, bullCol, size=size.small)
    plotshape(yTakeDn, 'Short TAKE', shape.triangledown, location.absolute, bearCol, size=size.small)
    plotshape(ySkipUp, 'Long SKIP', shape.xcross, location.absolute, color.new(NEUTRAL, 20), size=size.tiny)
    plotshape(ySkipDn, 'Short SKIP', shape.xcross, location.absolute, color.new(NEUTRAL, 20), size=size.tiny)
    plotshape(yCalUp, 'Long flip (calibrating)', shape.triangleup, location.absolute, color.new(bullCol, 55), size=size.tiny)
    plotshape(yCalDn, 'Short flip (calibrating)', shape.triangledown, location.absolute, color.new(bearCol, 55), size=size.tiny)

    plot(high, 'Scale Anchor High', CLEAR, display=display.pane, editable=False)
    plot(low, 'Scale Anchor Low', CLEAR, display=display.pane, editable=False)

    sigCode: float = (1.0 if lastVerdict == 1 else 0.5) if sigUp else (-1.0 if lastVerdict == 1 else -0.5) if sigDn else 0.0
    plot(sigCode, 'Signal (+1 long TAKE, -1 short TAKE, ±0.5 other flip)', display=display.data_window)
    plot(trend, 'Trend State (+1 / -1)', display=display.data_window)
    plot(pEdge, 'Edge at T1 (R per trade)', display=display.data_window)
    plot(na if na(pS1) else pS1 * 100, 'T1 Reach Probability (%)', display=display.data_window)
    plot(na if na(lastSigBar) else bar_index - lastSigBar, 'Bars Since Flip', display=display.data_window)

    alertcondition(takeUp, 'PSTE Long TAKE', 'PSTE: long flip with positive T1 evidence on {{ticker}} ({{interval}}) at {{close}}')
    alertcondition(takeDn, 'PSTE Short TAKE', 'PSTE: short flip with positive T1 evidence on {{ticker}} ({{interval}}) at {{close}}')
    alertcondition(sigUp, 'PSTE Long Flip (any verdict)', 'PSTE: bullish trend flip on {{ticker}} ({{interval}}) at {{close}}')
    alertcondition(sigDn, 'PSTE Short Flip (any verdict)', 'PSTE: bearish trend flip on {{ticker}} ({{interval}}) at {{close}}')

    dash: Persistent[Table] = table.new(position.top_right, 2, 10, bgcolor=color.new(DASH_BG, 8), frame_color=color.new(NEUTRAL, 60), frame_width=1, border_color=color.new(NEUTRAL, 85), border_width=1)

    def f_row(t: Table, r: int, k: str, v: str, vc: Color, sz: str):
        table.cell(t, 0, r, k, text_color=color.new(DASH_TXT, 30), text_halign=text.align_left, text_size=sz)
        return table.cell(t, 1, r, v, text_color=vc, text_halign=text.align_right, text_size=sz)

    if barstate.islast and showDash:
        dirC: Color = bullCol if lastDir == 1 else bearCol if lastDir == -1 else NEUTRAL
        trendTxt: str = ('▲ BULL' if trend == 1 else '▼ BEAR' if trend == -1 else '—') + (' · clean' if cleanCtx else ' · choppy')
        verdTxt: str = 'TAKE' if lastVerdict == 1 else 'SKIP' if lastVerdict == 0 else 'CALIBRATING' if lastVerdict == 2 else '—'
        verdC: Color = dirC if lastVerdict == 1 else NEUTRAL
        flipTxt: str = '—' if na(lastSigBar) else ('LONG · ' if lastDir == 1 else 'SHORT · ') + verdTxt + ' · ' + string.tostring(bar_index - lastSigBar) + ' bars ago'
        poolTxt: str = 'Direction + context' if pLvl == 0 else 'Direction pool' if pLvl == 1 else 'All flips' if pLvl == 2 else 'Calibrating'
        evTxt: str = poolTxt + ' ' + string.tostring(array.size(store)) + '/' + string.tostring(minN) if pLvl == 3 else poolTxt + ' · n=' + string.tostring(pN)
        t1Txt: str = 'none ≥ ' + string.tostring(math.round(p1 * 100)) + '%' if pLvl == 3 or pG1 < 0 else '+' + f_rTxt(array.get(grid, pG1)) + ' · ' + f_pctTxt(pS1) + ' · ~' + string.tostring(pM1, '#') + ' bars'
        t2Txt: str = '—' if pLvl == 3 or pG2 < 0 else '+' + f_rTxt(array.get(grid, pG2)) + ' · ' + f_pctTxt(pS2) + ' · ~' + string.tostring(pM2, '#') + ' bars'
        t3Txt: str = '—' if pLvl == 3 or pG3 < 0 else '+' + f_rTxt(array.get(grid, pG3)) + ' · ' + f_pctTxt(pS3) + ' · ~' + string.tostring(pM3, '#') + ' bars'
        edgeTxt: str = '—' if na(pEdge) else ('+' if pEdge >= 0 else '') + string.tostring(pEdge, '#.00') + 'R / trade'
        edgeC: Color = NEUTRAL if na(pEdge) else bullCol if pEdge > 0 else bearCol
        liveTxt: str = 'Open · MFE +' + string.tostring(tMfe, '#.0') + 'R · ' + string.tostring(bar_index - tStartBar) + '/' + string.tostring(horizon) if tOpen else '—' if na(lastSigBar) else 'Closed · ' + lastExit
        table.cell(dash, 0, 0, 'PSTE', text_color=DASH_TXT, text_halign=text.align_left, text_size=tSz, text_formatting=text.format_bold)
        table.cell(dash, 1, 0, trendTxt, text_color=trendCol, text_halign=text.align_right, text_size=tSz, text_formatting=text.format_bold)
        f_row(dash, 1, 'Last flip', flipTxt, verdC, tSz)
        f_row(dash, 2, 'Evidence', evTxt, DASH_TXT, tSz)
        f_row(dash, 3, 'T1', t1Txt, dirC, tSz)
        f_row(dash, 4, 'T2', t2Txt, dirC, tSz)
        f_row(dash, 5, 'T3', t3Txt, dirC, tSz)
        f_row(dash, 6, 'Edge at T1', edgeTxt, edgeC, tSz)
        f_row(dash, 7, 'Live plan', liveTxt, DASH_TXT, tSz)
        f_row(dash, 8, 'Record', string.tostring(resolved) + ' resolved · ' + string.tostring(ties) + ' stop-first ties', color.new(DASH_TXT, 25), tSz)
        f_row(dash, 9, 'Data mode', 'ALL PLANS · closed-bar OHLC', color.new(DASH_TXT, 25), tSz)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)