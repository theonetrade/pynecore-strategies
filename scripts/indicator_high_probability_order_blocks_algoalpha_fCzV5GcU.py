"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_float, cast_int
from pynecore.core.pine_method import method_call
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, box, chart, close, color,
    high, input, label, line, location, low, math, na, nz, open, plotchar, polyline, script, size,
    string, ta, text
)
from pynecore.types import Box, Label, Line, NA, Persistent, PersistentSeries, Polyline, Series
from pynecore.types.chart import ChartPoint


@script.indicator("High Probability Order Blocks [AlgoAlpha]", shorttitle="AlgoAlpha - High Probability OB", overlay=True, max_boxes_count=500, max_lines_count=500, max_polylines_count=100)
def main(
    preventOverlap=input.bool(True, title="Prevent Overlap", group="Calculation", tooltip="Avoid creating blocks that overlap existing ones."),
    zLen=input.int(50, title="Z-Score Window (bars)", minval=1, group="Calculation", tooltip="Bars used to normalize distance into z-scores. Bigger = smoother; smaller = faster."),
    maxAge=input.int(2000, title="Max Box Age (bars)", minval=1, group="Calculation", tooltip="Expire blocks after this many bars if not mitigated."),
    kmLookback=input.int(70, title="KM Training Window (zones)", minval=1, group="Reliability Calculation", tooltip="Recent mitigated blocks kept per side (bullish/bearish) for KM. Higher = smoother, lower = more reactive."),
    kmMinSamples=input.int(5, title="Minimum Sample Size", minval=5, group="Reliability Calculation", tooltip="Minimum mitigated blocks needed to compute KM. Otherwise shows not enough data (N.E.D.)"),
    showKmPanel=input.bool(True, title="Show KM Panel", group="Appearance", tooltip="Toggle KM axes/grid and curves."),
    kmAxisCol=input.color(color.new(color.white, 0), title="KM Axis Color", group="Appearance", tooltip="Axis line color."),
    kmGridCol=input.color(color.new(color.silver, 60), title="KM Grid Color", group="Appearance", tooltip="Grid line color."),
    bullCol=input.color(color.new('#00FFBB'), title="Bullish Colour", group="Appearance", tooltip="Color for bullish blocks and curve."),
    bearCol=input.color(color.new('#FF1100'), title="Bearish Colour", group="Appearance", tooltip="Color for bearish blocks and curve."),
    probTxtSizeOpt=input.string("Tiny", title="Probability Text Size", options=("Tiny", "Small", "Medium", "Large"), group="Appearance", tooltip="Text size inside each orderblock label.")
):
    probTxtSizeConst = size.tiny if probTxtSizeOpt == 'Tiny' else size.small if probTxtSizeOpt == 'Small' else size.normal if probTxtSizeOpt == 'Medium' else size.large

    kmGridYDivs: int = 4
    kmGridXStep: int = 50
    showKmLabels: bool = True
    kmXAxisTitle: str = "Orderblock Age (Bars)"
    kmYAxisTitle: str = "Probability of Zone Survival %"

    updist: PersistentSeries[float] = 0.0
    downdist: PersistentSeries[float] = 0.0

    updist = nz(updist[1]) + (close - open) if close > open else 0.0
    downdist = nz(downdist[1]) + (open - close) if close < open else 0.0

    upMean = ta.sma(updist, zLen)
    upStdev = ta.stdev(updist, zLen)
    dnMean = ta.sma(downdist, zLen)
    dnStdev = ta.stdev(downdist, zLen)

    zUp: Series = (updist - upMean) / (na if upStdev == 0.0 else upStdev)
    zDn = (downdist - dnMean) / (na if dnStdev == 0.0 else dnStdev)

    bullish = ta.crossover(zUp, 4) and nz(zUp[1]) != 0
    bearish = ta.crossunder(-zDn, -4) and nz(inline_series(-zDn, 1)) != 0

    bullBoxes: Persistent[list[Box]] = array.new_box()
    bearBoxes: Persistent[list[Box]] = array.new_box()
    bullStarts: Persistent[list[int]] = array.new_int()
    bearStarts: Persistent[list[int]] = array.new_int()
    bullMidlines: Persistent[list[Line]] = array.new_line()
    bearMidlines: Persistent[list[Line]] = array.new_line()
    bullKmCurve: Persistent[Polyline] = na(Polyline)
    bearKmCurve: Persistent[Polyline] = na(Polyline)

    kmStartBars: Persistent[list[int]] = array.new_int()
    kmStartSides: Persistent[list[int]] = array.new_int()
    kmEventStartBars: Persistent[list[int]] = array.new_int()
    kmEventSides: Persistent[list[int]] = array.new_int()
    kmEventAges: Persistent[list[float]] = array.new_float()
    kmCensorStartBars: Persistent[list[int]] = array.new_int()
    kmCensorSides: Persistent[list[int]] = array.new_int()
    kmCensorAges: Persistent[list[float]] = array.new_float()
    kmOpenCensorStartBars: Persistent[list[int]] = array.new_int()
    kmOpenCensorSides: Persistent[list[int]] = array.new_int()
    kmOpenCensorAges: Persistent[list[float]] = array.new_float()

    def f_remove_samples_for_start(side: int, startBar: int):
        nEvRm: int = array.size(kmEventStartBars)
        if nEvRm > 0:
            for k in pine_range(nEvRm - 1, 0):
                if k >= 0 and array.size(kmEventSides) > k and (array.size(kmEventStartBars) > k) and (array.size(kmEventAges) > k):
                    if array.get(kmEventSides, k) == side and array.get(kmEventStartBars, k) == startBar:
                        array.remove(kmEventStartBars, k)
                        array.remove(kmEventSides, k)
                        array.remove(kmEventAges, k)
        nCeRm: int = array.size(kmCensorStartBars)
        __block_result__ = na
        if nCeRm > 0:
            __block_result_1__ = na
            for k in pine_range(nCeRm - 1, 0):
                __block_result_2__ = na
                if k >= 0 and array.size(kmCensorSides) > k and (array.size(kmCensorStartBars) > k) and (array.size(kmCensorAges) > k):
                    __block_result_3__ = na
                    if array.get(kmCensorSides, k) == side and array.get(kmCensorStartBars, k) == startBar:
                        array.remove(kmCensorStartBars, k)
                        array.remove(kmCensorSides, k)
                        __block_result_3__ = array.remove(kmCensorAges, k)
                    __block_result_2__ = __block_result_3__
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    def f_trim_km_starts_and_samples(side: int, lookback: int):
        idxs: list[int] = array.new_int()
        for i in pine_range(0, array.size(kmStartBars) - 1):
            if array.size(kmStartSides) > i:
                if array.get(kmStartSides, i) == side:
                    array.push(idxs, i)
        n: int = array.size(idxs)
        __block_result_4__ = na
        if n > lookback:
            __block_result_5__ = na
            for j in pine_range(n - 1, lookback):
                idx: int = array.get(idxs, j)
                __block_result_6__ = na
                if array.size(kmStartBars) > idx and array.size(kmStartSides) > idx:
                    sb: int = array.get(kmStartBars, idx)
                    f_remove_samples_for_start(side, sb)
                    array.remove(kmStartBars, idx)
                    __block_result_6__ = array.remove(kmStartSides, idx)
                __block_result_5__ = __block_result_6__
            __block_result_4__ = __block_result_5__
        return __block_result_4__

    kmAxisX: Persistent[Polyline] = na(Polyline)
    kmAxisY: Persistent[Polyline] = na(Polyline)
    kmGridLines: Persistent[list[Polyline]] = array.new(0, NA(Polyline))
    kmYTickLabels: Persistent[list[Label]] = array.new_label()
    kmXTickLabels: Persistent[list[Label]] = array.new_label()
    kmXAxisTitleLabel: Persistent[Label] = na(Label)
    kmYAxisTitleLabel: Persistent[Label] = na(Label)
    kmPlotTitleLabel: Persistent[Label] = na(Label)

    bullrej: bool = False
    bearrej: bool = False
    bullCreate: bool = False
    bearCreate: bool = False

    def f_km_survival(side: int, lookbackZones: int, minSamples: int, ageBars: int):
        includeStarts: list[int] = array.new_int()
        totalStarts: int = array.size(kmStartBars)
        taken: int = 0
        if totalStarts > 0:
            for i in pine_range(0, totalStarts - 1):
                if taken >= lookbackZones:
                    break
                if i >= 0 and array.size(kmStartSides) > i and (array.size(kmStartBars) > i):
                    if array.get(kmStartSides, i) == side:
                        array.push(includeStarts, array.get(kmStartBars, i))
                        taken += 1
        E: list[float] = array.new_float()
        C: list[float] = array.new_float()
        nEvt: int = array.size(kmEventStartBars)
        if nEvt > 0:
            for i in pine_range(0, nEvt - 1):
                if i >= 0 and array.size(kmEventSides) > i and (array.size(kmEventStartBars) > i) and (array.size(kmEventAges) > i):
                    if array.get(kmEventSides, i) == side:
                        sb: int = array.get(kmEventStartBars, i)
                        if array.indexof(includeStarts, sb) != -1:
                            array.push(E, array.get(kmEventAges, i))
        nCen: int = array.size(kmCensorStartBars)
        if nCen > 0:
            for i in pine_range(0, nCen - 1):
                if i >= 0 and array.size(kmCensorSides) > i and (array.size(kmCensorStartBars) > i) and (array.size(kmCensorAges) > i):
                    if array.get(kmCensorSides, i) == side:
                        sb: int = array.get(kmCensorStartBars, i)
                        if array.indexof(includeStarts, sb) != -1:
                            array.push(C, array.get(kmCensorAges, i))
        nOpen: int = array.size(kmOpenCensorStartBars)
        if nOpen > 0:
            for i in pine_range(0, nOpen - 1):
                if i >= 0 and array.size(kmOpenCensorSides) > i and (array.size(kmOpenCensorStartBars) > i) and (array.size(kmOpenCensorAges) > i):
                    if array.get(kmOpenCensorSides, i) == side:
                        sb: int = array.get(kmOpenCensorStartBars, i)
                        if array.indexof(includeStarts, sb) != -1:
                            array.push(C, array.get(kmOpenCensorAges, i))
        N0: int = array.size(includeStarts)
        total: int = array.size(E) + array.size(C) + 0
        __block_result_7__ = na
        if N0 < minSamples or array.size(E) == 0:
            __block_result_7__ = na
        else:
            array.sort(E)
            array.sort(C)
            S: float = 1.0
            nRisk: int = N0
            ei: int = 0
            ci: int = 0
            nE: int = array.size(E)
            nC: int = array.size(C)
            while ei < nE:
                ti: float = array.get(E, ei)
                if ti > ageBars:
                    break
                while ci < nC and ci >= 0 and (array.size(C) > ci) and (array.get(C, ci) < ti):
                    nRisk -= 1
                    ci += 1
                d: int = 0
                while ei < nE and ei >= 0 and (array.size(E) > ei) and (array.get(E, ei) == ti):
                    d += 1
                    ei += 1
                if nRisk > 0:
                    S = S * (1.0 - cast_float(d) / cast_float(nRisk))
                nRisk -= d
                cEq: int = 0
                while ci < nC and ci >= 0 and (array.size(C) > ci) and (array.get(C, ci) == ti):
                    cEq += 1
                    ci += 1
                nRisk -= cEq
            __block_result_7__ = S
        return __block_result_7__

    def f_km_points(side: int, lookbackZones: int, minSamples: int, topY: float, botY: float, xStart: int, maxBars: int):
        pts: list[ChartPoint] = array.new(0, NA(ChartPoint))
        __block_result_8__ = na
        if maxBars <= 0:
            __block_result_8__ = pts
        else:
            includeStarts: list[int] = array.new_int()
            totalStarts: int = array.size(kmStartBars)
            taken: int = 0
            if totalStarts > 0:
                for i in pine_range(0, totalStarts - 1):
                    if taken >= lookbackZones:
                        break
                    if i >= 0 and array.size(kmStartSides) > i and (array.size(kmStartBars) > i):
                        if array.get(kmStartSides, i) == side:
                            array.push(includeStarts, array.get(kmStartBars, i))
                            taken += 1
            E: list[float] = array.new_float()
            C: list[float] = array.new_float()
            nEvt: int = array.size(kmEventStartBars)
            if nEvt > 0:
                for i in pine_range(0, nEvt - 1):
                    if i >= 0 and array.size(kmEventSides) > i and (array.size(kmEventStartBars) > i) and (array.size(kmEventAges) > i):
                        if array.get(kmEventSides, i) == side:
                            sb: int = array.get(kmEventStartBars, i)
                            if array.indexof(includeStarts, sb) != -1:
                                array.push(E, array.get(kmEventAges, i))
            nCen: int = array.size(kmCensorStartBars)
            if nCen > 0:
                for i in pine_range(0, nCen - 1):
                    if i >= 0 and array.size(kmCensorSides) > i and (array.size(kmCensorStartBars) > i) and (array.size(kmCensorAges) > i):
                        if array.get(kmCensorSides, i) == side:
                            sb: int = array.get(kmCensorStartBars, i)
                            if array.indexof(includeStarts, sb) != -1:
                                array.push(C, array.get(kmCensorAges, i))
            nOpen: int = array.size(kmOpenCensorStartBars)
            for i in pine_range(0, nOpen - 1):
                if i >= 0 and array.size(kmOpenCensorSides) > i and (array.size(kmOpenCensorStartBars) > i) and (array.size(kmOpenCensorAges) > i):
                    if array.get(kmOpenCensorSides, i) == side:
                        sb: int = array.get(kmOpenCensorStartBars, i)
                        if array.indexof(includeStarts, sb) != -1:
                            array.push(C, array.get(kmOpenCensorAges, i))
            total: int = array.size(E) + array.size(C)
            __block_result_9__ = na
            if total < minSamples or array.size(E) == 0:
                __block_result_9__ = pts
            else:
                array.sort(E)
                array.sort(C)
                S: float = 1.0
                nRisk: int = total
                ei: int = 0
                ci: int = 0
                nE: int = array.size(E)
                nC: int = array.size(C)
                y0: float = botY + S * (topY - botY)
                array.push(pts, chart.point.from_index(xStart, y0))
                while ei < nE:
                    ti: int = cast_int(array.get(E, ei))
                    if ti > maxBars:
                        break
                    while ci < nC and ci >= 0 and (array.size(C) > ci) and (cast_int(array.get(C, ci)) < ti):
                        nRisk -= 1
                        ci += 1
                    yS: float = botY + S * (topY - botY)
                    array.push(pts, chart.point.from_index(xStart + ti, yS))
                    d: int = 0
                    while ei < nE and ei >= 0 and (array.size(E) > ei) and (cast_int(array.get(E, ei)) == ti):
                        d += 1
                        ei += 1
                    if nRisk > 0:
                        S = S * (1.0 - cast_float(d) / cast_float(nRisk))
                    nRisk -= d
                    cEq: int = 0
                    while ci < nC and ci >= 0 and (array.size(C) > ci) and (cast_int(array.get(C, ci)) == ti):
                        cEq += 1
                        ci += 1
                    nRisk -= cEq
                    yNew: float = botY + S * (topY - botY)
                    array.push(pts, chart.point.from_index(xStart + ti, yNew))
                yEnd: float = botY + S * (topY - botY)
                array.push(pts, chart.point.from_index(xStart + maxBars, yEnd))
                __block_result_9__ = pts
            __block_result_8__ = __block_result_9__
        return __block_result_8__

    def f_can_create(tNew: float, bNew: float):
        ok: bool = True
        if array.size(bullBoxes) > 0:
            for j in pine_range(0, array.size(bullBoxes) - 1):
                exB = array.get(bullBoxes, j)
                exTop: float = box.get_top(exB)
                exBot: float = box.get_bottom(exB)
                if tNew > exBot and bNew < exTop:
                    ok = False
                    break
        if ok and array.size(bearBoxes) > 0:
            for j in pine_range(0, array.size(bearBoxes) - 1):
                exS = array.get(bearBoxes, j)
                exTop2: float = box.get_top(exS)
                exBot2: float = box.get_bottom(exS)
                if tNew > exBot2 and bNew < exTop2:
                    ok = False
                    break
        return ok

    lastDownIdx = ta.valuewhen(close < open, bar_index, 0)
    lastDownHigh = ta.valuewhen(close < open, high, 0)
    lastDownLow = ta.valuewhen(close < open, low, 0)
    if bullish and (not na(lastDownIdx)) and (not na(lastDownHigh)) and (not na(lastDownLow)):
        if not preventOverlap or f_can_create(lastDownHigh, lastDownLow):
            bgTransB: int = 85
            brdTransB: int = math.min(100, bgTransB + 10)
            bx = box.new(lastDownIdx, lastDownHigh, lastDownIdx + 1, lastDownLow, border_color=color.new(bullCol, brdTransB), bgcolor=color.new(bullCol, bgTransB))
            array.unshift(bullBoxes, bx)
            array.unshift(bullStarts, lastDownIdx)
            array.unshift(kmStartBars, lastDownIdx)
            array.unshift(kmStartSides, 1)
            f_trim_km_starts_and_samples(1, kmLookback)
            midYB: float = (lastDownHigh + lastDownLow) / 2.0
            midB: Line = line.new(lastDownIdx, midYB, lastDownIdx + 1, midYB, color=color.new(bullCol, 60), width=1, style=line.style_dashed)
            array.unshift(bullMidlines, midB)
            bullCreate = True

    lastUpIdx = ta.valuewhen(close > open, bar_index, 0)
    lastUpHigh = ta.valuewhen(close > open, high, 0)
    lastUpLow = ta.valuewhen(close > open, low, 0)
    if bearish and (not na(lastUpIdx)) and (not na(lastUpHigh)) and (not na(lastUpLow)):
        if not preventOverlap or f_can_create(lastUpHigh, lastUpLow):
            bgTransS: int = 85
            brdTransS: int = math.min(100, bgTransS + 10)
            bx2 = box.new(lastUpIdx, lastUpHigh, lastUpIdx + 1, lastUpLow, border_color=color.new(bearCol, brdTransS), bgcolor=color.new(bearCol, bgTransS))
            array.unshift(bearBoxes, bx2)
            array.unshift(bearStarts, lastUpIdx)
            array.unshift(kmStartBars, lastUpIdx)
            array.unshift(kmStartSides, -1)
            f_trim_km_starts_and_samples(-1, kmLookback)
            midYS: float = (lastUpHigh + lastUpLow) / 2.0
            midS: Line = line.new(lastUpIdx, midYS, lastUpIdx + 1, midYS, color=color.new(bearCol, 60), width=1, style=line.style_dashed)
            array.unshift(bearMidlines, midS)
            bearCreate = True

    if array.size(bullBoxes) > 0:
        for i in pine_range(array.size(bullBoxes) - 1, 0):
            if array.size(bullBoxes) <= i or array.size(bullStarts) <= i:
                continue
            b = array.get(bullBoxes, i)
            box.set_right(b, bar_index)
            if array.size(bullMidlines) > i:
                mB: Line = array.get(bullMidlines, i)
                line.set_x2(mB, bar_index)
            topB: float = box.get_top(b)
            botB: float = box.get_bottom(b)
            mitigatedB: bool = close < botB and close[1] < botB
            startB: int = array.get(bullStarts, i)
            expiredB: bool = bar_index - startB >= maxAge
            if mitigatedB or expiredB:
                if mitigatedB:
                    durB: int = bar_index - startB
                    array.unshift(kmEventStartBars, startB)
                    array.unshift(kmEventSides, 1)
                    array.unshift(kmEventAges, durB)
                elif expiredB:
                    durBX: int = bar_index - startB
                    array.unshift(kmCensorStartBars, startB)
                    array.unshift(kmCensorSides, 1)
                    array.unshift(kmCensorAges, durBX)
                array.remove(bullBoxes, i)
                array.remove(bullStarts, i)
                if array.size(bullMidlines) > i:
                    array.remove(bullMidlines, i)
            else:
                ageB: int = bar_index - startB
                if close > topB and close[1] < topB:
                    bullrej = True

    if array.size(bearBoxes) > 0:
        for i in pine_range(array.size(bearBoxes) - 1, 0):
            if array.size(bearBoxes) <= i or array.size(bearStarts) <= i:
                continue
            b = array.get(bearBoxes, i)
            box.set_right(b, bar_index)
            if array.size(bearMidlines) > i:
                mS: Line = array.get(bearMidlines, i)
                line.set_x2(mS, bar_index)
            topS: float = box.get_top(b)
            botS: float = box.get_bottom(b)
            mitigatedS: bool = close > topS and close[1] > topS
            startS: int = array.get(bearStarts, i)
            expiredS: bool = bar_index - startS >= maxAge
            if mitigatedS or expiredS:
                if mitigatedS:
                    durS: int = bar_index - startS
                    array.unshift(kmEventStartBars, startS)
                    array.unshift(kmEventSides, -1)
                    array.unshift(kmEventAges, durS)
                elif expiredS:
                    durSX: int = bar_index - startS
                    array.unshift(kmCensorStartBars, startS)
                    array.unshift(kmCensorSides, -1)
                    array.unshift(kmCensorAges, durSX)
                array.remove(bearBoxes, i)
                array.remove(bearStarts, i)
                if array.size(bearMidlines) > i:
                    array.remove(bearMidlines, i)
            else:
                ageS: int = bar_index - startS
                if close < botS and close[1] > botS:
                    bearrej = True

    if barstate.islast:
        if array.size(kmOpenCensorStartBars) > 0:
            for i in pine_range(array.size(kmOpenCensorStartBars) - 1, 0):
                array.remove(kmOpenCensorStartBars, i)
                array.remove(kmOpenCensorSides, i)
                array.remove(kmOpenCensorAges, i)
        if array.size(bullBoxes) > 0 and array.size(bullStarts) > 0:
            for i in pine_range(0, array.size(bullBoxes) - 1):
                if array.size(bullStarts) > i:
                    startB2: int = array.get(bullStarts, i)
                    ageB2: int = bar_index - startB2
                    array.unshift(kmOpenCensorStartBars, startB2)
                    array.unshift(kmOpenCensorSides, 1)
                    array.unshift(kmOpenCensorAges, cast_float(ageB2))
        if array.size(bearBoxes) > 0 and array.size(bearStarts) > 0:
            for i in pine_range(0, array.size(bearBoxes) - 1):
                if array.size(bearStarts) > i:
                    startS2: int = array.get(bearStarts, i)
                    ageS2: int = bar_index - startS2
                    array.unshift(kmOpenCensorStartBars, startS2)
                    array.unshift(kmOpenCensorSides, -1)
                    array.unshift(kmOpenCensorAges, cast_float(ageS2))
        rightStart: int = bar_index + 50
        maxBarsRight: int = 450
        rightEnd: int = math.min(rightStart + maxBarsRight, bar_index + 500)
        maxBarsDraw: int = rightEnd - rightStart
        frameTop: float = na(float)
        frameBottom: float = na(float)
        if array.size(bullBoxes) > 0:
            for i in pine_range(0, array.size(bullBoxes) - 1):
                if array.size(bullBoxes) > i:
                    bx_ = array.get(bullBoxes, i)
                    t: float = box.get_top(bx_)
                    btm: float = box.get_bottom(bx_)
                    frameTop = t if na(frameTop) else math.max(frameTop, t)
                    frameBottom = btm if na(frameBottom) else math.min(frameBottom, btm)
        if array.size(bearBoxes) > 0:
            for i in pine_range(0, array.size(bearBoxes) - 1):
                if array.size(bearBoxes) > i:
                    bx2_ = array.get(bearBoxes, i)
                    t2: float = box.get_top(bx2_)
                    btm2: float = box.get_bottom(bx2_)
                    frameTop = t2 if na(frameTop) else math.max(frameTop, t2)
                    frameBottom = btm2 if na(frameBottom) else math.min(frameBottom, btm2)
        yTop: float = high if na(frameTop) else frameTop
        yBottom: float = low if na(frameBottom) else frameBottom
        if yTop <= yBottom:
            yTop += 1
            yBottom -= 1
        if showKmPanel:
            if not na(kmAxisX):
                polyline.delete(kmAxisX)
            if not na(kmAxisY):
                polyline.delete(kmAxisY)
            if array.size(kmGridLines) > 0:
                for gi in pine_range(array.size(kmGridLines) - 1, 0):
                    if array.size(kmGridLines) > gi:
                        gl: Polyline = array.get(kmGridLines, gi)
                        if not na(gl):
                            polyline.delete(gl)
                        array.remove(kmGridLines, gi)
            if array.size(kmYTickLabels) > 0:
                for li in pine_range(array.size(kmYTickLabels) - 1, 0):
                    if array.size(kmYTickLabels) > li:
                        lb: Label = array.get(kmYTickLabels, li)
                        if not na(lb):
                            label.delete(lb)
                        array.remove(kmYTickLabels, li)
            if array.size(kmXTickLabels) > 0:
                for li in pine_range(array.size(kmXTickLabels) - 1, 0):
                    if array.size(kmXTickLabels) > li:
                        lb: Label = array.get(kmXTickLabels, li)
                        if not na(lb):
                            label.delete(lb)
                        array.remove(kmXTickLabels, li)

            xAxisPts: list[ChartPoint] = array.new(0, NA(ChartPoint))
            array.push(xAxisPts, chart.point.from_index(rightStart, yBottom))
            array.push(xAxisPts, chart.point.from_index(rightEnd, yBottom))
            kmAxisX = polyline.new(xAxisPts, line_color=kmAxisCol, line_style=line.style_solid)

            yAxisPts: list[ChartPoint] = array.new(0, NA(ChartPoint))
            array.push(yAxisPts, chart.point.from_index(rightStart, yBottom))
            array.push(yAxisPts, chart.point.from_index(rightStart, yTop))
            kmAxisY = polyline.new(yAxisPts, line_color=kmAxisCol, line_style=line.style_solid)

            for d in pine_range(0, kmGridYDivs):
                frac: float = cast_float(d) / cast_float(kmGridYDivs)
                yLvl: float = yBottom + frac * (yTop - yBottom)
                hPts: list[ChartPoint] = array.new(0, NA(ChartPoint))
                array.push(hPts, chart.point.from_index(rightStart, yLvl))
                array.push(hPts, chart.point.from_index(rightEnd, yLvl))
                hLine: Polyline = polyline.new(hPts, line_color=kmGridCol, line_style=line.style_dotted)
                array.push(kmGridLines, hLine)
                if showKmLabels:
                    lbl: str = string.tostring(math.round(frac * 100)) + '%'
                    ly: Label = label.new(rightEnd, yLvl, lbl, textcolor=chart.fg_color, color=color.new(color.black, 100), textalign=text.align_left, style=label.style_label_left, size=size.tiny)
                    array.push(kmYTickLabels, ly)

            vCount: int = cast_int(math.floor(maxBarsDraw / kmGridXStep))
            if vCount > 0:
                for i in pine_range(1, vCount):
                    xoff: int = i * kmGridXStep
                    vPts: list[ChartPoint] = array.new(0, NA(ChartPoint))
                    array.push(vPts, chart.point.from_index(rightStart + xoff, yBottom))
                    array.push(vPts, chart.point.from_index(rightStart + xoff, yTop))
                    vLine: Polyline = polyline.new(vPts, line_color=kmGridCol, line_style=line.style_dotted)
                    array.push(kmGridLines, vLine)
                    if showKmLabels:
                        tl: str = string.tostring(xoff)
                        lx: Label = label.new(rightStart + xoff, yBottom, tl, textcolor=chart.fg_color, color=color.new(color.black, 100), textalign=text.align_center, style=label.style_label_down, size=size.tiny)
                        array.push(kmXTickLabels, lx)

            if not na(kmXAxisTitleLabel):
                label.delete(kmXAxisTitleLabel)
            if not na(kmYAxisTitleLabel):
                label.delete(kmYAxisTitleLabel)
            if not na(kmPlotTitleLabel):
                label.delete(kmPlotTitleLabel)
            kmXAxisTitleLabel = label.new(cast_int((rightStart + rightEnd) / 2), yBottom, kmXAxisTitle, textcolor=chart.fg_color, color=color.new(color.black, 100), textalign=text.align_center, style=label.style_label_up, size=size.small)
            yMid: float = yBottom + 0.5 * (yTop - yBottom)
            yTitle: float = yMid - 0.04 * (yTop - yBottom)
            titlePadBars: int = math.max(6, cast_int(math.round(maxBarsDraw * 0.02)))
            titleX: int = math.min(bar_index + 500 - 1, rightEnd + titlePadBars)
            kmPlotTitleLabel = label.new(titleX, yTitle, kmYAxisTitle, textcolor=chart.fg_color, color=color.new(color.black, 100), textalign=text.align_left, style=label.style_label_left, size=size.small)
        bullTop: float = na(float)
        bullBot: float = na(float)
        bearTop: float = na(float)
        bearBot: float = na(float)
        if array.size(bullBoxes) > 0:
            bullTop = box.get_top(array.get(bullBoxes, 0))
            bullBot = box.get_bottom(array.get(bullBoxes, 0))
        if array.size(bearBoxes) > 0:
            bearTop = box.get_top(array.get(bearBoxes, 0))
            bearBot = box.get_bottom(array.get(bearBoxes, 0))
        if showKmPanel:
            if not na(bullTop) and (not na(bullBot)) and (bullTop != bullBot):
                ptsB: list[ChartPoint] = f_km_points(1, kmLookback, kmMinSamples, yTop, yBottom, rightStart, maxBarsDraw)
                if array.size(ptsB) > 1:
                    if not na(bullKmCurve):
                        polyline.delete(bullKmCurve)
                    bullKmCurve = polyline.new(ptsB, line_color=bullCol, line_style=line.style_solid)
            if not na(bearTop) and (not na(bearBot)) and (bearTop != bearBot):
                ptsS: list[ChartPoint] = f_km_points(-1, kmLookback, kmMinSamples, yTop, yBottom, rightStart, maxBarsDraw)
                if array.size(ptsS) > 1:
                    if not na(bearKmCurve):
                        polyline.delete(bearKmCurve)
                    bearKmCurve = polyline.new(ptsS, line_color=bearCol, line_style=line.style_solid)
        else:
            if not na(bullKmCurve):
                polyline.delete(bullKmCurve)
                bullKmCurve = na
            if not na(bearKmCurve):
                polyline.delete(bearKmCurve)
                bearKmCurve = na

        if array.size(bullBoxes) > 0 and array.size(bullStarts) > 0:
            for i in pine_range(0, array.size(bullBoxes) - 1):
                if array.size(bullBoxes) > i and array.size(bullStarts) > i:
                    b = array.get(bullBoxes, i)
                    startB3: int = array.get(bullStarts, i)
                    ageB3: int = bar_index - startB3
                    sB2: float = f_km_survival(1, kmLookback, kmMinSamples, ageB3)
                    txtB2: str = 'Age ' + string.tostring(ageB3) + ' | N.E.D' if na(sB2) else 'Age ' + string.tostring(ageB3) + ' | ' + string.tostring(math.round(sB2 * 100)) + '%'
                    method_call('set_text', b, txtB2)
                    method_call('set_text_halign', b, text.align_right)
                    method_call('set_text_valign', b, text.align_bottom)
                    method_call('set_text_color', b, chart.fg_color)
                    method_call('set_text_size', b, probTxtSizeConst)
        if array.size(bearBoxes) > 0 and array.size(bearStarts) > 0:
            for i in pine_range(0, array.size(bearBoxes) - 1):
                if array.size(bearBoxes) > i and array.size(bearStarts) > i:
                    b = array.get(bearBoxes, i)
                    startS3: int = array.get(bearStarts, i)
                    ageS3: int = bar_index - startS3
                    sS2: float = f_km_survival(-1, kmLookback, kmMinSamples, ageS3)
                    txtS2: str = 'Age ' + string.tostring(ageS3) + ' | N.E.D' if na(sS2) else 'Age ' + string.tostring(ageS3) + ' | ' + string.tostring(math.round(sS2 * 100)) + '%'
                    method_call('set_text', b, txtS2)
                    method_call('set_text_halign', b, text.align_right)
                    method_call('set_text_valign', b, text.align_top)
                    method_call('set_text_color', b, chart.fg_color)
                    method_call('set_text_size', b, probTxtSizeConst)

    volatility = ta.atr(14)
    plotchar(low - volatility * 2 if bullrej else na, 'Bullish Rejection', '▲', location.absolute, bullCol, size=size.tiny)
    plotchar(high + volatility * 2 if bearrej else na, 'Bearish Rejection', '▼', location.absolute, bearCol, size=size.tiny)

    alertcondition(bullCreate, 'Bullish Zone Created', 'Bullish OrderBlock Created')
    alertcondition(bearCreate, 'Bearish Zone Created', 'Bearish OrderBlock Created')
    alertcondition(bullrej, 'Bullish Rejection', 'Bullish Rejection Signal')
    alertcondition(bearrej, 'Bearish Rejection', 'Bearish Rejection Signal')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
