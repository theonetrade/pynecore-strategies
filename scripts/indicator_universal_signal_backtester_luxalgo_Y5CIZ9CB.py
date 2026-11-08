"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, bar_index, barcolor, barstate, close, color, dayofweek, high,
    hour, input, label, line, location, low, map, math, month, na, nz, open, order, plot,
    plotshape, position, script, shape, size, string, syminfo, ta, table, text, time, weekofyear,
    year
)
from pynecore.types import Color, Label, Line, Persistent, Series, Table


@script.indicator(title="Universal Signal Backtester [LuxAlgo]", shorttitle="LuxAlgo - Universal Signal Backtester", overlay=True, max_lines_count=500, max_labels_count=500)
def main(
    sourceMode=input.string("Predefined Crosses", "Source Mode", options=("Predefined Crosses", "External Sources (Crossovers)", "External Signals (Triggers)"), group="Source Settings"),
    predefCross=input.string("9/21 EMA Cross", "Predefined Cross", options=("9/21 EMA Cross", "12/26 EMA Cross", "Golden/Death Cross (50/200 SMA)"), tooltip="Used if Source Mode is Predefined Crosses.", group="Source Settings"),
    fastSource: Series[float] = input.source(close, "External Fast Source", tooltip="Only used if Source Mode is External Sources (Crossovers).", group="Source Settings"),
    slowSource: Series[float] = input.source(open, "External Slow Source", tooltip="Only used if Source Mode is External Sources (Crossovers).", group="Source Settings"),
    extLongSignal: Series[float] = input.source(close, "External Long Signal", tooltip="Only used if Source Mode is External Signals (Triggers).", group="Source Settings"),
    extShortSignal: Series[float] = input.source(close, "External Short Signal", tooltip="Only used if Source Mode is External Signals (Triggers).", group="Source Settings"),
    signalLogic=input.string("Not NA (Plotshape/Markers)", "External Signal Logic", options=("Not NA (Plotshape/Markers)", "Crosses Over 0", "Crosses Under 0", "Value Changes", "Greater Than 0", "Less Than 0"), tooltip="How should the script interpret the external signal?", group="Source Settings"),
    tradeDirection=input.string("Both", "Trade Direction", options=("Both", "Long Only", "Short Only")),
    useAtrFilter=input.bool(False, "Use ATR Choppiness Filter", group="Filters", tooltip="Ignores signals when volatility (ATR) is below its average, helping to avoid choppy clustering."),
    atrFilterLen=input.int(50, "ATR Smoothing Length", group="Filters"),
    distType=input.string("ATR", "Distance Type", options=("ATR", "Ticks", "Points/Fiat"), group="Target Settings"),
    atrLen=input.int(14, "ATR Length", tooltip="Only used if Distance Type is ATR", group="Target Settings"),
    useTp1=input.bool(True, "Take Profit 1", inline="tp1", group="Take Profit"),
    tp1Val=input.float(1.0, "", inline="tp1", group="Take Profit", step=0.5),
    useTp2=input.bool(True, "Take Profit 2", inline="tp2", group="Take Profit"),
    tp2Val=input.float(2.0, "", inline="tp2", group="Take Profit", step=0.5),
    useTp3=input.bool(True, "Take Profit 3", inline="tp3", group="Take Profit"),
    tp3Val=input.float(3.0, "", inline="tp3", group="Take Profit", step=0.5),
    useSl1=input.bool(True, "Stop Loss 1", inline="sl1", group="Stop Loss"),
    sl1Val=input.float(1.5, "", inline="sl1", group="Stop Loss", step=0.5),
    useSl2=input.bool(True, "Stop Loss 2", inline="sl2", group="Stop Loss"),
    sl2Val=input.float(2.5, "", inline="sl2", group="Stop Loss", step=0.5),
    useSl3=input.bool(True, "Stop Loss 3", inline="sl3", group="Stop Loss"),
    sl3Val=input.float(3.5, "", inline="sl3", group="Stop Loss", step=0.5),
    showDash=input.bool(True, "Show Dashboard", group="Dashboard"),
    dashPos=input.string("Top Right", "Dashboard Position", options=("Top Right", "Bottom Right", "Bottom Left"), group="Dashboard"),
    dashSize=input.string("Small", "Dashboard Size", options=("Tiny", "Small", "Normal", "Large"), group="Dashboard"),
    heatmapPeriod=input.string("Days of Week", "Heatmap Period", options=("Days of Week", "Months"), group="Dashboard"),
    suggestMetric=input.string("Hit Rate", "Suggested TP Metric", options=("Hit Rate", "Expected Profit", "Total Profit", "Risk/Reward"), group="Dashboard"),
    useCandleColor=input.bool(True, "Gradient Candle Coloring", group="Visuals"),
    useCosts=input.bool(False, "Simulate Spread & Commission", group="Costs"),
    costProfile=input.string("Manual", "Cost Profile", options=("Manual", "Forex (Avg)", "Crypto (Tier 1)", "Stocks (US)"), group="Costs"),
    manualSpread=input.float(1.0, "Manual Spread (Ticks)", group="Costs", tooltip="Spread applied per round trip in ticks"),
    manualComm=input.float(0.01, "Manual Commission (%)", group="Costs", tooltip="Commission applied per round trip as a % of position value")
):
    def get_block_char(val: float, max_val: float):
        __block_result__ = na
        if max_val == 0 or val == 0:
            __block_result__ = " "
        else:
            ratio: float = math.abs(val) / max_val
            res: str = " "
            if ratio < 0.125:
                res = " "
            elif ratio < 0.25:
                res = "▂"
            elif ratio < 0.375:
                res = "▃"
            elif ratio < 0.5:
                res = "▄"
            elif ratio < 0.625:
                res = "▅"
            elif ratio < 0.75:
                res = "▆"
            elif ratio < 0.875:
                res = "▇"
            else:
                res = "█"
            __block_result__ = res
        return __block_result__

    def get_heatmap_color(val: float, maxV: float, minV: float):
        c: Color = color.new('#161616')
        if val > 0 and maxV > 0:
            c = color.from_gradient(val, 0, maxV, color.new(color.new('#089981'), 80), color.new(color.new('#089981'), 10))
        elif val < 0 and minV < 0:
            c = color.from_gradient(val, minV, 0, color.new(color.new('#F23645'), 10), color.new(color.new('#F23645'), 80))
        return c

    def get_month_name(i: int):
        __block_result_1__ = na
        __switch__ = i
        if __switch__ == 0:
            __block_result_1__ = "Jan"
        elif __switch__ == 1:
            __block_result_1__ = "Feb"
        elif __switch__ == 2:
            __block_result_1__ = "Mar"
        elif __switch__ == 3:
            __block_result_1__ = "Apr"
        elif __switch__ == 4:
            __block_result_1__ = "May"
        elif __switch__ == 5:
            __block_result_1__ = "Jun"
        elif __switch__ == 6:
            __block_result_1__ = "Jul"
        elif __switch__ == 7:
            __block_result_1__ = "Aug"
        elif __switch__ == 8:
            __block_result_1__ = "Sep"
        elif __switch__ == 9:
            __block_result_1__ = "Oct"
        elif __switch__ == 10:
            __block_result_1__ = "Nov"
        elif __switch__ == 11:
            __block_result_1__ = "Dec"
        return __block_result_1__

    def get_day_name(i: int):
        __block_result_2__ = na
        __switch__ = i
        if __switch__ == 0:
            __block_result_2__ = "Sun"
        elif __switch__ == 1:
            __block_result_2__ = "Mon"
        elif __switch__ == 2:
            __block_result_2__ = "Tue"
        elif __switch__ == 3:
            __block_result_2__ = "Wed"
        elif __switch__ == 4:
            __block_result_2__ = "Thu"
        elif __switch__ == 5:
            __block_result_2__ = "Fri"
        elif __switch__ == 6:
            __block_result_2__ = "Sat"
        return __block_result_2__

    def format_time(ms: int):
        days: int = math.round(ms / 86400000.0)
        res: str = string.tostring(days) + 'd'
        return res

    fastLen: float = 9
    slowLen: float = 21
    isEma: bool = True

    if predefCross == '9/21 EMA Cross':
        fastLen = 9
        slowLen = 21
        isEma = True
    elif predefCross == '12/26 EMA Cross':
        fastLen = 12
        slowLen = 26
        isEma = True
    elif predefCross == 'Golden/Death Cross (50/200 SMA)':
        fastLen = 50
        slowLen = 200
        isEma = False

    def get_ribbon_ma(is_ema: bool, len: float):
        l: int = math.round(len)
        e: float = ta.ema(close, l)
        s: float = ta.sma(close, l)
        return e if is_ema else s

    builtInFast: float = get_ribbon_ma(isEma, fastLen)
    builtInSlow: float = get_ribbon_ma(isEma, slowLen)

    stepLen: float = (slowLen - fastLen) / 10
    r1: float = get_ribbon_ma(isEma, fastLen + stepLen * 1)
    r2: float = get_ribbon_ma(isEma, fastLen + stepLen * 2)
    r3: float = get_ribbon_ma(isEma, fastLen + stepLen * 3)
    r4: float = get_ribbon_ma(isEma, fastLen + stepLen * 4)
    r5: float = get_ribbon_ma(isEma, fastLen + stepLen * 5)
    r6: float = get_ribbon_ma(isEma, fastLen + stepLen * 6)
    r7: float = get_ribbon_ma(isEma, fastLen + stepLen * 7)
    r8: float = get_ribbon_ma(isEma, fastLen + stepLen * 8)
    r9: float = get_ribbon_ma(isEma, fastLen + stepLen * 9)

    isPredef: bool = sourceMode == 'Predefined Crosses'
    isExtCross: bool = sourceMode == 'External Sources (Crossovers)'
    isExtSig: bool = sourceMode == 'External Signals (Triggers)'

    activeFast: float = builtInFast if isPredef else fastSource
    activeSlow: float = builtInSlow if isPredef else slowSource

    atrFilterVal: float = nz(ta.atr(14))
    atrFilter: bool = atrFilterVal > ta.sma(atrFilterVal, atrFilterLen) if useAtrFilter else True

    baseLongCond: bool = False
    baseShortCond: bool = False

    if isPredef or isExtCross:
        baseLongCond = ta.crossover(activeFast, activeSlow)
        baseShortCond = ta.crossunder(activeFast, activeSlow)
    elif isExtSig:
        __switch_1__ = signalLogic
        if __switch_1__ == "Not NA (Plotshape/Markers)":
            baseLongCond = not na(extLongSignal) and na(extLongSignal[1])
            baseShortCond = not na(extShortSignal) and na(extShortSignal[1])
        elif __switch_1__ == "Crosses Over 0":
            baseLongCond = ta.crossover(extLongSignal, 0)
            baseShortCond = ta.crossover(extShortSignal, 0)
        elif __switch_1__ == "Crosses Under 0":
            baseLongCond = ta.crossunder(extLongSignal, 0)
            baseShortCond = ta.crossunder(extShortSignal, 0)
        elif __switch_1__ == "Value Changes":
            baseLongCond = ta.change(extLongSignal) != 0
            baseShortCond = ta.change(extShortSignal) != 0
        elif __switch_1__ == "Greater Than 0":
            baseLongCond = extLongSignal > 0
            baseShortCond = extShortSignal > 0
        elif __switch_1__ == "Less Than 0":
            baseLongCond = extLongSignal < 0
            baseShortCond = extShortSignal < 0

    longCond = baseLongCond and atrFilter
    shortCond = baseShortCond and atrFilter

    canLong = tradeDirection == 'Both' or tradeDirection == 'Long Only'
    canShort = tradeDirection == 'Both' or tradeDirection == 'Short Only'

    atrVal: float = nz(ta.atr(atrLen))
    multi: float = atrVal if distType == 'ATR' else syminfo.mintick if distType == 'Ticks' else 1.0

    d_tp1: float = tp1Val * multi
    d_tp2: float = tp2Val * multi
    d_tp3: float = tp3Val * multi
    d_sl1: float = sl1Val * multi
    d_sl2: float = sl2Val * multi
    d_sl3: float = sl3Val * multi

    spreadTicks: float = 0.0
    commPerc: float = 0.0

    if useCosts:
        __switch_1__ = costProfile
        if __switch_1__ == "Forex (Avg)":
            spreadTicks = 1.0
            commPerc = 0.005
        elif __switch_1__ == "Crypto (Tier 1)":
            spreadTicks = 1.0
            commPerc = 0.12
        elif __switch_1__ == "Stocks (US)":
            spreadTicks = 2.0
            commPerc = 0.0
        elif __switch_1__ == "Manual":
            spreadTicks = manualSpread
            commPerc = manualComm

    isActive: Persistent[bool] = False
    tradeDir: Persistent[int] = 0
    entryPx: Persistent[float] = 0.0
    entryTime: Persistent[int] = 0
    qtyLeft: Persistent[float] = 0.0
    tradePnl: Persistent[float] = 0.0

    active_tp1: Persistent[bool] = False
    px_tp1: Persistent[float] = 0.0
    hit_tp1: Persistent[bool] = False
    ln_tp1: Persistent[Line] = na(Line)
    lb_tp1: Persistent[Label] = na(Line)
    active_tp2: Persistent[bool] = False
    px_tp2: Persistent[float] = 0.0
    hit_tp2: Persistent[bool] = False
    ln_tp2: Persistent[Line] = na(Line)
    lb_tp2: Persistent[Label] = na(Line)
    active_tp3: Persistent[bool] = False
    px_tp3: Persistent[float] = 0.0
    hit_tp3: Persistent[bool] = False
    ln_tp3: Persistent[Line] = na(Line)
    lb_tp3: Persistent[Label] = na(Line)

    active_sl1: Persistent[bool] = False
    px_sl1: Persistent[float] = 0.0
    hit_sl1: Persistent[bool] = False
    ln_sl1: Persistent[Line] = na(Line)
    lb_sl1: Persistent[Label] = na(Line)
    active_sl2: Persistent[bool] = False
    px_sl2: Persistent[float] = 0.0
    hit_sl2: Persistent[bool] = False
    ln_sl2: Persistent[Line] = na(Line)
    lb_sl2: Persistent[Label] = na(Line)
    active_sl3: Persistent[bool] = False
    px_sl3: Persistent[float] = 0.0
    hit_sl3: Persistent[bool] = False
    ln_sl3: Persistent[Line] = na(Line)
    lb_sl3: Persistent[Label] = na(Line)

    hourlyPnL: Persistent[list[float]] = array.new_float(24, 0.0)
    activeYears: Persistent[list[int]] = array.new_int()
    activeWeeks: Persistent[list[int]] = array.new_int()
    monthlyMap: Persistent[dict[int, float]] = map.new()
    dailyMap: Persistent[dict[int, float]] = map.new()

    allTradePnL: Persistent[list[float]] = array.new_float()
    equityCurve: Persistent[list[float]] = array.new_float()

    totalTrades: Persistent[int] = 0
    wins: Persistent[int] = 0
    losses: Persistent[int] = 0
    grossWin: Persistent[float] = 0.0
    grossLoss: Persistent[float] = 0.0

    maxEq: Persistent[float] = 0.0
    currentEq: Persistent[float] = 0.0
    maxDd: Persistent[float] = 0.0
    lastHighTime: Persistent[int] = time
    maxStagMs: Persistent[int] = 0

    tp1HitsCount: Persistent[int] = 0
    tp2HitsCount: Persistent[int] = 0
    tp3HitsCount: Persistent[int] = 0

    isLongEntry: bool = False
    isShortEntry: bool = False
    isLongWin: bool = False
    isLongLoss: bool = False
    isShortWin: bool = False
    isShortLoss: bool = False

    if active_tp1 and (not hit_tp1):
        line.set_x2(ln_tp1, bar_index)
        label.set_x(lb_tp1, bar_index)
    if active_tp2 and (not hit_tp2):
        line.set_x2(ln_tp2, bar_index)
        label.set_x(lb_tp2, bar_index)
    if active_tp3 and (not hit_tp3):
        line.set_x2(ln_tp3, bar_index)
        label.set_x(lb_tp3, bar_index)

    if active_sl1 and (not hit_sl1):
        line.set_x2(ln_sl1, bar_index)
        label.set_x(lb_sl1, bar_index)
    if active_sl2 and (not hit_sl2):
        line.set_x2(ln_sl2, bar_index)
        label.set_x(lb_sl2, bar_index)
    if active_sl3 and (not hit_sl3):
        line.set_x2(ln_sl3, bar_index)
        label.set_x(lb_sl3, bar_index)

    if isActive:
        h: float = high
        l: float = low
        closedThisBar: bool = False

        if active_sl1 and (not hit_sl1) and (tradeDir == 1 and l <= px_sl1 or (tradeDir == -1 and h >= px_sl1)):
            hit_sl1 = True
            label.set_text(lb_sl1, 'SL 1 ✗')
        if active_sl2 and (not hit_sl2) and (tradeDir == 1 and l <= px_sl2 or (tradeDir == -1 and h >= px_sl2)):
            hit_sl2 = True
            label.set_text(lb_sl2, 'SL 2 ✗')
        if active_sl3 and (not hit_sl3) and (tradeDir == 1 and l <= px_sl3 or (tradeDir == -1 and h >= px_sl3)):
            hit_sl3 = True
            label.set_text(lb_sl3, 'SL 3 ✗')

        if hit_sl1 or hit_sl2 or hit_sl3:
            exitPx: float = px_sl1 if hit_sl1 else px_sl2 if hit_sl2 else px_sl3
            rawPnl: float = (exitPx - entryPx) * tradeDir / syminfo.mintick * qtyLeft
            costTicks: float = (spreadTicks + entryPx * (commPerc / 100) / syminfo.mintick) * qtyLeft
            tradePnl += rawPnl - costTicks
            qtyLeft = 0.0
            closedThisBar = True

        if not closedThisBar:
            tpQty: float = 1.0 / math.max(1, (1 if active_tp1 else 0) + (1 if active_tp2 else 0) + (1 if active_tp3 else 0))

            if active_tp1 and (not hit_tp1) and (tradeDir == 1 and h >= px_tp1 or (tradeDir == -1 and l <= px_tp1)):
                hit_tp1 = True
                tp1HitsCount += 1
                rawPnl: float = (px_tp1 - entryPx) * tradeDir / syminfo.mintick * tpQty
                costTicks: float = (spreadTicks + entryPx * (commPerc / 100) / syminfo.mintick) * tpQty
                tradePnl += rawPnl - costTicks
                qtyLeft -= tpQty
                label.set_text(lb_tp1, 'TP 1 ✓')

            if active_tp2 and (not hit_tp2) and (tradeDir == 1 and h >= px_tp2 or (tradeDir == -1 and l <= px_tp2)):
                hit_tp2 = True
                tp2HitsCount += 1
                rawPnl: float = (px_tp2 - entryPx) * tradeDir / syminfo.mintick * tpQty
                costTicks: float = (spreadTicks + entryPx * (commPerc / 100) / syminfo.mintick) * tpQty
                tradePnl += rawPnl - costTicks
                qtyLeft -= tpQty
                label.set_text(lb_tp2, 'TP 2 ✓')

            if active_tp3 and (not hit_tp3) and (tradeDir == 1 and h >= px_tp3 or (tradeDir == -1 and l <= px_tp3)):
                hit_tp3 = True
                tp3HitsCount += 1
                rawPnl: float = (px_tp3 - entryPx) * tradeDir / syminfo.mintick * tpQty
                costTicks: float = (spreadTicks + entryPx * (commPerc / 100) / syminfo.mintick) * tpQty
                tradePnl += rawPnl - costTicks
                qtyLeft -= tpQty
                label.set_text(lb_tp3, 'TP 3 ✓')

            if qtyLeft <= 0.001:
                closedThisBar = True

        if not closedThisBar:
            if tradeDir == 1 and shortCond or (tradeDir == -1 and longCond):
                rawPnl: float = (close - entryPx) * tradeDir / syminfo.mintick * qtyLeft
                costTicks: float = (spreadTicks + entryPx * (commPerc / 100) / syminfo.mintick) * qtyLeft
                tradePnl += rawPnl - costTicks
                qtyLeft = 0.0
                closedThisBar = True

        if closedThisBar:
            isActive = False
            totalTrades += 1

            array.push(allTradePnL, tradePnl)

            if tradePnl > 0:
                wins += 1
                grossWin += tradePnl
                if tradeDir == 1:
                    isLongWin = True
                else:
                    isShortWin = True
            elif tradePnl < 0:
                losses += 1
                grossLoss += math.abs(tradePnl)
                if tradeDir == 1:
                    isLongLoss = True
                else:
                    isShortLoss = True

            currentEq += tradePnl
            array.push(equityCurve, currentEq)

            if currentEq > maxEq:
                maxEq = currentEq
                lastHighTime = time

            stag: int = time - lastHighTime
            if stag > maxStagMs:
                maxStagMs = stag

            dd: float = maxEq - currentEq
            if dd > maxDd:
                maxDd = dd

            hr: int = hour(entryTime)
            array.set(hourlyPnL, hr, array.get(hourlyPnL, hr) + tradePnl)

            y: int = year(entryTime)
            m: int = month(entryTime) - 1
            y_m: int = y * 100 + m
            if array.indexof(activeYears, y) == -1:
                array.push(activeYears, y)
            map.put(monthlyMap, y_m, nz(map.get(monthlyMap, y_m)) + tradePnl)

            w: int = weekofyear(entryTime)
            d: int = dayofweek(entryTime) - 1
            y_w: int = y * 100 + w
            y_w_d: int = y_w * 100 + d
            if array.indexof(activeWeeks, y_w) == -1:
                array.push(activeWeeks, y_w)
            map.put(dailyMap, y_w_d, nz(map.get(dailyMap, y_w_d)) + tradePnl)

    if not isActive:
        h: float = high
        l: float = low
        if active_tp1 and (not hit_tp1) and (tradeDir == 1 and h >= px_tp1 or (tradeDir == -1 and l <= px_tp1)):
            hit_tp1 = True
            label.set_text(lb_tp1, 'TP 1 ✓')
        if active_tp2 and (not hit_tp2) and (tradeDir == 1 and h >= px_tp2 or (tradeDir == -1 and l <= px_tp2)):
            hit_tp2 = True
            label.set_text(lb_tp2, 'TP 2 ✓')
        if active_tp3 and (not hit_tp3) and (tradeDir == 1 and h >= px_tp3 or (tradeDir == -1 and l <= px_tp3)):
            hit_tp3 = True
            label.set_text(lb_tp3, 'TP 3 ✓')

        if active_sl1 and (not hit_sl1) and (tradeDir == 1 and l <= px_sl1 or (tradeDir == -1 and h >= px_sl1)):
            hit_sl1 = True
            label.set_text(lb_sl1, 'SL 1 ✗')
        if active_sl2 and (not hit_sl2) and (tradeDir == 1 and l <= px_sl2 or (tradeDir == -1 and h >= px_sl2)):
            hit_sl2 = True
            label.set_text(lb_sl2, 'SL 2 ✗')
        if active_sl3 and (not hit_sl3) and (tradeDir == 1 and l <= px_sl3 or (tradeDir == -1 and h >= px_sl3)):
            hit_sl3 = True
            label.set_text(lb_sl3, 'SL 3 ✗')

    currentStag: int = time - lastHighTime
    if currentStag > maxStagMs:
        maxStagMs = currentStag

    if not isActive:
        newDir: int = 0
        if longCond and canLong:
            newDir = 1
        elif shortCond and canShort:
            newDir = -1

        if newDir != 0:
            isActive = True
            tradeDir = newDir
            entryPx = close
            entryTime = time
            qtyLeft = 1.0
            tradePnl = 0.0

            if newDir == 1:
                isLongEntry = True
            else:
                isShortEntry = True

            tr: float = math.max(1, totalTrades)
            rate1: float = tp1HitsCount / tr
            rate2: float = tp2HitsCount / tr
            rate3: float = tp3HitsCount / tr

            slDist: float = math.max(syminfo.mintick, d_sl1)
            __block_result_3__ = na
            __switch_2__ = suggestMetric
            if __switch_2__ == "Expected Profit":
                __block_result_3__ = rate1 * d_tp1
            elif __switch_2__ == "Total Profit":
                __block_result_3__ = tp1HitsCount * d_tp1
            elif __switch_2__ == "Risk/Reward":
                __block_result_3__ = d_tp1 / slDist
            else:
                __block_result_3__ = rate1 * 100
            v1: float = __block_result_3__
            __block_result_4__ = na
            __switch_2__ = suggestMetric
            if __switch_2__ == "Expected Profit":
                __block_result_4__ = rate2 * d_tp2
            elif __switch_2__ == "Total Profit":
                __block_result_4__ = tp2HitsCount * d_tp2
            elif __switch_2__ == "Risk/Reward":
                __block_result_4__ = d_tp2 / slDist
            else:
                __block_result_4__ = rate2 * 100
            v2: float = __block_result_4__
            __block_result_5__ = na
            __switch_2__ = suggestMetric
            if __switch_2__ == "Expected Profit":
                __block_result_5__ = rate3 * d_tp3
            elif __switch_2__ == "Total Profit":
                __block_result_5__ = tp3HitsCount * d_tp3
            elif __switch_2__ == "Risk/Reward":
                __block_result_5__ = d_tp3 / slDist
            else:
                __block_result_5__ = rate3 * 100
            v3: float = __block_result_5__

            bestV: float = v1
            bestTp: int = 1
            bestRate: float = rate1 * 100

            if v2 > bestV and useTp2:
                bestV = v2
                bestTp = 2
                bestRate = rate2 * 100
            if v3 > bestV and useTp3:
                bestV = v3
                bestTp = 3
                bestRate = rate3 * 100

            lblText: str = 'TP' + string.tostring(bestTp) + ' ' + string.tostring(bestRate, '#.#') + '%'
            offset: float = atrVal if atrVal != 0 else high - low

            if newDir == 1:
                y1: float = low
                y2: float = low - offset * 1.5
                line.new(bar_index, y1, bar_index, y2, color=color.new('#089981'), style=line.style_dashed)
                label.new(bar_index, y2, '', color=color.new(color.new('#089981'), 80), style=label.style_circle, size=size.huge)
                label.new(bar_index, y2, lblText, color=color.new('#363A45'), textcolor=color.white, style=label.style_label_center, size=size.small)
            else:
                y1: float = high
                y2: float = high + offset * 1.5
                line.new(bar_index, y1, bar_index, y2, color=color.new('#F23645'), style=line.style_dashed)
                label.new(bar_index, y2, '', color=color.new(color.new('#F23645'), 80), style=label.style_circle, size=size.huge)
                label.new(bar_index, y2, lblText, color=color.new('#363A45'), textcolor=color.white, style=label.style_label_center, size=size.small)

            active_tp1 = useTp1
            px_tp1 = close + newDir * d_tp1
            hit_tp1 = False
            active_tp2 = useTp2
            px_tp2 = close + newDir * d_tp2
            hit_tp2 = False
            active_tp3 = useTp3
            px_tp3 = close + newDir * d_tp3
            hit_tp3 = False

            active_sl1 = useSl1
            px_sl1 = close - newDir * d_sl1
            hit_sl1 = False
            active_sl2 = useSl2
            px_sl2 = close - newDir * d_sl2
            hit_sl2 = False
            active_sl3 = useSl3
            px_sl3 = close - newDir * d_sl3
            hit_sl3 = False

            if active_tp1:
                ln_tp1 = line.new(bar_index, px_tp1, bar_index, px_tp1, color=color.new('#089981'), style=line.style_dashed)
                lb_tp1 = label.new(bar_index, px_tp1, 'TP 1', textcolor=color.new('#089981'), color=color.new('#00000000'), size=size.tiny, style=label.style_label_left)
            if active_tp2:
                ln_tp2 = line.new(bar_index, px_tp2, bar_index, px_tp2, color=color.new('#089981'), style=line.style_dashed)
                lb_tp2 = label.new(bar_index, px_tp2, 'TP 2', textcolor=color.new('#089981'), color=color.new('#00000000'), size=size.tiny, style=label.style_label_left)
            if active_tp3:
                ln_tp3 = line.new(bar_index, px_tp3, bar_index, px_tp3, color=color.new('#089981'), style=line.style_dashed)
                lb_tp3 = label.new(bar_index, px_tp3, 'TP 3', textcolor=color.new('#089981'), color=color.new('#00000000'), size=size.tiny, style=label.style_label_left)

            if active_sl1:
                ln_sl1 = line.new(bar_index, px_sl1, bar_index, px_sl1, color=color.new('#F23645'), style=line.style_dashed)
                lb_sl1 = label.new(bar_index, px_sl1, 'SL 1', textcolor=color.new('#F23645'), color=color.new('#00000000'), size=size.tiny, style=label.style_label_left)
            if active_sl2:
                ln_sl2 = line.new(bar_index, px_sl2, bar_index, px_sl2, color=color.new('#F23645'), style=line.style_dashed)
                lb_sl2 = label.new(bar_index, px_sl2, 'SL 2', textcolor=color.new('#F23645'), color=color.new('#00000000'), size=size.tiny, style=label.style_label_left)
            if active_sl3:
                ln_sl3 = line.new(bar_index, px_sl3, bar_index, px_sl3, color=color.new('#F23645'), style=line.style_dashed)
                lb_sl3 = label.new(bar_index, px_sl3, 'SL 3', textcolor=color.new('#F23645'), color=color.new('#00000000'), size=size.tiny, style=label.style_label_left)

    def rColor(idx: int):
        isBull: bool = activeFast > activeSlow
        baseC: Color = color.new('#089981') if isBull else color.new('#F23645')
        return color.new(baseC, idx * 8)

    cDist: float = activeFast - activeSlow
    maxDist: float = nz(ta.sma(math.abs(cDist), 100)) * 2
    candleColor: Color = color.from_gradient(cDist, -maxDist, maxDist, color.new('#F23645'), color.new('#089981'))
    barcolor(candleColor if useCandleColor else na, title='Gradient Candles')

    plot(builtInFast if isPredef else activeFast, 'Fast Source', color=rColor(0) if isPredef else color.new('#2962FF'))
    plot(r1 if isPredef else na, 'Ribbon 1', color=rColor(1))
    plot(r2 if isPredef else na, 'Ribbon 2', color=rColor(2))
    plot(r3 if isPredef else na, 'Ribbon 3', color=rColor(3))
    plot(r4 if isPredef else na, 'Ribbon 4', color=rColor(4))
    plot(r5 if isPredef else na, 'Ribbon 5', color=rColor(5))
    plot(r6 if isPredef else na, 'Ribbon 6', color=rColor(6))
    plot(r7 if isPredef else na, 'Ribbon 7', color=rColor(7))
    plot(r8 if isPredef else na, 'Ribbon 8', color=rColor(8))
    plot(r9 if isPredef else na, 'Ribbon 9', color=rColor(9))
    plot(builtInSlow if isPredef else activeSlow, 'Slow Source', color=rColor(10) if isPredef else color.new('#FF6D00'))

    plotshape(isLongWin, title='Long Win', style=shape.xcross, location=location.abovebar, color=color.new('#089981'), size=size.tiny)
    plotshape(isLongLoss, title='Long Loss', style=shape.xcross, location=location.abovebar, color=color.new('#F23645'), size=size.tiny)

    plotshape(isShortWin, title='Short Win', style=shape.xcross, location=location.belowbar, color=color.new('#089981'), size=size.tiny)
    plotshape(isShortLoss, title='Short Loss', style=shape.xcross, location=location.belowbar, color=color.new('#F23645'), size=size.tiny)

    DATA: Color = color.new('#DBDBDB')
    HEADERS: Color = color.new('#808080')
    BACKGROUND: Color = color.new('#161616')
    BORDERS: Color = color.new('#2E2E2E')

    __block_result_6__ = na
    __switch__ = dashPos
    if __switch__ == "Top Right":
        __block_result_6__ = position.top_right
    elif __switch__ == "Bottom Right":
        __block_result_6__ = position.bottom_right
    elif __switch__ == "Bottom Left":
        __block_result_6__ = position.bottom_left
    parsedDashPos: Persistent = __block_result_6__

    __block_result_7__ = na
    __switch__ = dashSize
    if __switch__ == "Tiny":
        __block_result_7__ = size.tiny
    elif __switch__ == "Small":
        __block_result_7__ = size.small
    elif __switch__ == "Normal":
        __block_result_7__ = size.normal
    elif __switch__ == "Large":
        __block_result_7__ = size.large
    parsedDashSize: Persistent = __block_result_7__

    dash: Persistent[Table] = table.new(parsedDashPos, 24, 30, bgcolor=BACKGROUND, border_width=1, border_color=BACKGROUND, frame_color=BORDERS, frame_width=1)

    if barstate.islast and showDash:
        array.sort(activeYears, order.ascending)
        array.sort(activeWeeks, order.ascending)

        winRate: float = wins / totalTrades * 100 if totalTrades > 0 else 0
        pf: float = grossWin / grossLoss if grossLoss > 0 else 99.9 if grossWin > 0 else 0
        avgWin: float = grossWin / wins if wins > 0 else 0
        avgLoss: float = grossLoss / losses if losses > 0 else 0
        netProfit: float = grossWin - grossLoss
        recoveryFactor: float = netProfit / maxDd if maxDd > 0 else 99.9 if netProfit > 0 else 0

        meanPnL: float = array.sum(allTradePnL) / array.size(allTradePnL) if array.size(allTradePnL) > 0 else 0
        devSum: float = 0.0
        if array.size(allTradePnL) > 0:
            for p in allTradePnL:
                devSum += math.pow(p - meanPnL, 2)
        stdDev: float = math.sqrt(devSum / array.size(allTradePnL)) if array.size(allTradePnL) > 0 else 0
        sharpe: float = meanPnL / stdDev if stdDev > 0 else 0

        eqStr: str = ""
        eqSize: int = array.size(equityCurve)
        if eqSize > 0:
            bins: int = 24
            step: float = eqSize / bins
            minE: float = array.min(equityCurve)
            maxE: float = array.max(equityCurve)
            rangeE: float = math.max(0.0001, maxE - minE)

            for i in pine_range(0, bins - 1):
                idx: int = math.floor(i * step)
                if idx >= eqSize:
                    idx = eqSize - 1
                val: float = array.get(equityCurve, idx) - minE
                r: float = val / rangeE
                char: str = ' ' if r < 0.125 else '▂' if r < 0.25 else '▃' if r < 0.375 else '▄' if r < 0.5 else '▅' if r < 0.625 else '▆' if r < 0.75 else '▇' if r < 0.875 else '█'
                eqStr += char

        tp1Perc: float = tp1HitsCount / totalTrades * 100 if totalTrades > 0 else 0
        tp2Perc: float = tp2HitsCount / totalTrades * 100 if totalTrades > 0 else 0
        tp3Perc: float = tp3HitsCount / totalTrades * 100 if totalTrades > 0 else 0

        tp1Str: str = string.tostring(tp1HitsCount) + ' (' + string.tostring(tp1Perc, '#.#') + '%)'
        tp2Str: str = string.tostring(tp2HitsCount) + ' (' + string.tostring(tp2Perc, '#.#') + '%)'
        tp3Str: str = string.tostring(tp3HitsCount) + ' (' + string.tostring(tp3Perc, '#.#') + '%)'

        table.merge_cells(dash, 0, 0, 23, 0)
        table.cell(dash, 0, 0, 'Advanced Backtest Analytics', text_color=DATA, text_size=parsedDashSize, text_halign=text.align_center, bgcolor=BORDERS)

        table.merge_cells(dash, 0, 1, 5, 1)
        table.cell(dash, 0, 1, 'Total Trades', text_color=HEADERS, text_size=parsedDashSize)
        table.merge_cells(dash, 6, 1, 11, 1)
        table.cell(dash, 6, 1, 'Win Rate', text_color=HEADERS, text_size=parsedDashSize)
        table.merge_cells(dash, 12, 1, 17, 1)
        table.cell(dash, 12, 1, 'Profit Factor', text_color=HEADERS, text_size=parsedDashSize)
        table.merge_cells(dash, 18, 1, 23, 1)
        table.cell(dash, 18, 1, 'Total PnL (Ticks)', text_color=HEADERS, text_size=parsedDashSize)

        table.merge_cells(dash, 0, 2, 5, 2)
        table.cell(dash, 0, 2, string.tostring(totalTrades), text_color=DATA, text_size=parsedDashSize)
        table.merge_cells(dash, 6, 2, 11, 2)
        table.cell(dash, 6, 2, string.tostring(winRate, '#.#') + '%', text_color=color.new('#089981') if winRate >= 50 else color.new('#F23645'), text_size=parsedDashSize)
        table.merge_cells(dash, 12, 2, 17, 2)
        table.cell(dash, 12, 2, string.tostring(pf, '#.##'), text_color=color.new('#089981') if pf >= 1 else color.new('#F23645'), text_size=parsedDashSize)
        table.merge_cells(dash, 18, 2, 23, 2)
        table.cell(dash, 18, 2, string.tostring(currentEq, '#.##'), text_color=color.new('#089981') if currentEq >= 0 else color.new('#F23645'), text_size=parsedDashSize)

        table.merge_cells(dash, 0, 3, 7, 3)
        table.cell(dash, 0, 3, 'Sharpe Ratio', text_color=HEADERS, text_size=parsedDashSize)
        table.merge_cells(dash, 8, 3, 15, 3)
        table.cell(dash, 8, 3, 'Recovery Factor', text_color=HEADERS, text_size=parsedDashSize)
        table.merge_cells(dash, 16, 3, 23, 3)
        table.cell(dash, 16, 3, 'Max Stagnation', text_color=HEADERS, text_size=parsedDashSize)

        table.merge_cells(dash, 0, 4, 7, 4)
        table.cell(dash, 0, 4, string.tostring(sharpe, '#.##'), text_color=DATA, text_size=parsedDashSize)
        table.merge_cells(dash, 8, 4, 15, 4)
        table.cell(dash, 8, 4, string.tostring(recoveryFactor, '#.##'), text_color=DATA, text_size=parsedDashSize)
        table.merge_cells(dash, 16, 4, 23, 4)
        table.cell(dash, 16, 4, format_time(maxStagMs), text_color=DATA, text_size=parsedDashSize)

        table.merge_cells(dash, 0, 5, 7, 5)
        table.cell(dash, 0, 5, 'TP 1 Hits', text_color=HEADERS, text_size=parsedDashSize)
        table.merge_cells(dash, 8, 5, 15, 5)
        table.cell(dash, 8, 5, 'TP 2 Hits', text_color=HEADERS, text_size=parsedDashSize)
        table.merge_cells(dash, 16, 5, 23, 5)
        table.cell(dash, 16, 5, 'TP 3 Hits', text_color=HEADERS, text_size=parsedDashSize)

        table.merge_cells(dash, 0, 6, 7, 6)
        table.cell(dash, 0, 6, tp1Str, text_color=DATA, text_size=parsedDashSize)
        table.merge_cells(dash, 8, 6, 15, 6)
        table.cell(dash, 8, 6, tp2Str, text_color=DATA, text_size=parsedDashSize)
        table.merge_cells(dash, 16, 6, 23, 6)
        table.cell(dash, 16, 6, tp3Str, text_color=DATA, text_size=parsedDashSize)

        table.merge_cells(dash, 0, 7, 23, 7)
        table.cell(dash, 0, 7, 'Equity Curve  ' + eqStr, text_color=color.new('#089981'), text_size=parsedDashSize, text_halign=text.align_left)

        table.merge_cells(dash, 0, 8, 23, 8)
        table.cell(dash, 0, 8, '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', text_color=BORDERS, text_size=parsedDashSize, height=0.5)

        table.merge_cells(dash, 0, 9, 23, 9)
        table.cell(dash, 0, 9, 'Performance by Hour of Day', text_color=HEADERS, text_size=parsedDashSize)

        maxH: float = array.max(hourlyPnL)
        minH: float = array.min(hourlyPnL)
        absMaxH: float = math.max(math.abs(maxH), math.abs(minH))

        for i in pine_range(0, 23):
            val: float = array.get(hourlyPnL, i)
            table.cell(dash, i, 10, get_block_char(val, absMaxH), text_color=color.new('#089981') if val >= 0 else color.new('#F23645'), text_size=parsedDashSize)
            table.cell(dash, i, 11, string.tostring(i), text_color=HEADERS, text_size=size.tiny)

        table.merge_cells(dash, 0, 12, 23, 12)
        table.cell(dash, 0, 12, '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', text_color=BORDERS, text_size=parsedDashSize, height=0.5)

        table.merge_cells(dash, 0, 13, 23, 13)
        table.cell(dash, 0, 13, 'Performance by ' + heatmapPeriod, text_color=HEADERS, text_size=parsedDashSize)

        startRow: int = 14

        if heatmapPeriod == 'Months':
            allMonths: list[float] = map.values(monthlyMap)
            maxM: float = array.max(allMonths) if array.size(allMonths) > 0 else 0.0
            minM: float = array.min(allMonths) if array.size(allMonths) > 0 else 0.0

            table.merge_cells(dash, 4, startRow, 5, startRow)
            table.cell(dash, 4, startRow, 'Year', text_color=HEADERS, text_size=size.tiny, text_halign=text.align_center)
            for i in pine_range(0, 11):
                table.cell(dash, 6 + i, startRow, get_month_name(i), text_color=HEADERS, text_size=size.tiny, text_halign=text.align_center)
            table.merge_cells(dash, 18, startRow, 19, startRow)
            table.cell(dash, 18, startRow, 'Total', text_color=HEADERS, text_size=size.tiny, text_halign=text.align_center)

            startRow += 1

            nYears: int = array.size(activeYears)
            drawYears: int = math.min(nYears, 10)

            if drawYears > 0:
                for i in pine_range(0, drawYears - 1):
                    rOffset: int = startRow + i
                    y: int = array.get(activeYears, nYears - drawYears + i)

                    table.merge_cells(dash, 4, rOffset, 5, rOffset)
                    table.cell(dash, 4, rOffset, string.tostring(y), text_color=DATA, text_size=size.tiny, text_halign=text.align_center)

                    rowTotal: float = 0.0
                    for m in pine_range(0, 11):
                        y_m: int = y * 100 + m
                        val: float = nz(map.get(monthlyMap, y_m))
                        rowTotal += val
                        c: Color = BACKGROUND if val == 0 else get_heatmap_color(val, maxM, minM)
                        table.cell(dash, 6 + m, rOffset, '-' if val == 0 else string.tostring(val, '#.#'), bgcolor=c, text_color=DATA, text_size=size.tiny, text_halign=text.align_center)

                    cTot: Color = BACKGROUND if rowTotal == 0 else get_heatmap_color(rowTotal, maxM * 3, minM * 3)
                    table.merge_cells(dash, 18, rOffset, 19, rOffset)
                    table.cell(dash, 18, rOffset, string.tostring(rowTotal, '#.#'), bgcolor=cTot, text_color=DATA, text_size=size.tiny, text_halign=text.align_center)
        else:
            allDays: list[float] = map.values(dailyMap)
            maxD: float = array.max(allDays) if array.size(allDays) > 0 else 0.0
            minD: float = array.min(allDays) if array.size(allDays) > 0 else 0.0

            table.merge_cells(dash, 3, startRow, 5, startRow)
            table.cell(dash, 3, startRow, 'Week', text_color=HEADERS, text_size=size.tiny, text_halign=text.align_center)
            for i in pine_range(0, 6):
                c: int = 6 + i * 2
                table.merge_cells(dash, c, startRow, c + 1, startRow)
                table.cell(dash, c, startRow, get_day_name(i), text_color=HEADERS, text_size=size.tiny, text_halign=text.align_center)
            table.merge_cells(dash, 20, startRow, 22, startRow)
            table.cell(dash, 20, startRow, 'Total', text_color=HEADERS, text_size=size.tiny, text_halign=text.align_center)

            startRow += 1

            nWeeks: int = array.size(activeWeeks)
            drawWeeks: int = math.min(nWeeks, 10)

            if drawWeeks > 0:
                for i in pine_range(0, drawWeeks - 1):
                    rOffset: int = startRow + i
                    y_w: int = array.get(activeWeeks, nWeeks - drawWeeks + i)
                    y: int = math.floor(y_w / 100)
                    w: int = y_w % 100

                    table.merge_cells(dash, 3, rOffset, 5, rOffset)
                    table.cell(dash, 3, rOffset, string.tostring(y) + '-W' + string.tostring(w), text_color=DATA, text_size=size.tiny, text_halign=text.align_center)

                    rowTotal: float = 0.0
                    for d in pine_range(0, 6):
                        y_w_d: int = y_w * 100 + d
                        val: float = nz(map.get(dailyMap, y_w_d))
                        rowTotal += val
                        c: Color = BACKGROUND if val == 0 else get_heatmap_color(val, maxD, minD)
                        col: int = 6 + d * 2
                        table.merge_cells(dash, col, rOffset, col + 1, rOffset)
                        table.cell(dash, col, rOffset, '-' if val == 0 else string.tostring(val, '#.#'), bgcolor=c, text_color=DATA, text_size=size.tiny, text_halign=text.align_center)

                    cTot: Color = BACKGROUND if rowTotal == 0 else get_heatmap_color(rowTotal, maxD * 3, minD * 3)
                    table.merge_cells(dash, 20, rOffset, 22, rOffset)
                    table.cell(dash, 20, rOffset, string.tostring(rowTotal, '#.#'), bgcolor=cTot, text_color=DATA, text_size=size.tiny, text_halign=text.align_center)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)