"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, bgcolor, box, close, color, high, input,
    label, location, low, math, na, plotshape, position, script, shape, size, strategy, string,
    syminfo, ta, table, text, time, timestamp
)
from pynecore.types import Box, Label, Persistent, Series, Table

emaGroup: str = "EMA Settings"
tradeGroup: str = "Trade Direction"
trendGroup: str = "Trend Filter (ADX)"
tpslGroup: str = "Take Profit / Stop Loss"
tpslGroup_points: str = "Point Based TP/SL"
tpslGroup_per: str = "Percentage Based TP/SL"
tpslGroup_atr: str = "ATR Based Tp/SL"
tpslGroup_piv: str = "Pivot Based Tp/SL"
trailGroup: str = "Trailing Stop Loss"
beGroup: str = "Break-Even Stop"
timeExitGroup: str = "Time-Based Exit"
dateGroup: str = "Backtest Date Range"
visualGroup: str = "Visuals"
tableGroup: str = "Status Table"


@script.strategy(title="TP/SL Toolkit [AxeAlgo]", overlay=True, initial_capital=10000, process_orders_on_close=True, commission_type=strategy.commission.percent, commission_value=0.05, slippage=2, margin_long=100, margin_short=100)
def main(
    fastLength=input.int(9, "Fast EMA Length", minval=1, group=emaGroup, tooltip="Number of bars the fast (quick-reacting) EMA looks back over. Smaller = more sensitive."),
    slowLength=input.int(21, "Slow EMA Length", minval=1, group=emaGroup, tooltip="Number of bars the slow (smooth) EMA looks back over. Larger = smoother, less sensitive."),
    emaSource: Series[float] = input.source(close, "Source", group=emaGroup, tooltip="The price value the EMAs are calculated from (e.g. close, open, hl2...)."),
    allowLong=input.bool(True, "Allow Long Trades", group=tradeGroup),
    allowShort=input.bool(True, "Allow Short Trades", group=tradeGroup),
    useTrendFilter=input.bool(False, "Enable Trend Filter", group=trendGroup, tooltip="When enabled, ignores new crossover entries while ADX is below the threshold below (i.e. while the market isn't trending strongly enough)."),
    adxLength=input.int(14, "ADX/DI Length", minval=1, group=trendGroup, tooltip="Lookback length for the Directional Movement calculation that ADX is built from."),
    adxSmoothing=input.int(14, "ADX Smoothing", minval=1, group=trendGroup, tooltip="Smoothing length applied to ADX itself. Higher = smoother/slower trend-strength reading."),
    adxThreshold=input.float(20.0, "Minimum ADX To Trade", minval=0.0, step=1.0, group=trendGroup, tooltip="New entries are skipped while ADX is below this level. 20-25 is the commonly used 'trending vs. choppy' cutoff."),
    useTpSl=input.bool(True, "Enable Take Profit / Stop Loss", group=tpslGroup),
    tpslMode=input.string("ATR", "TP/SL Mode", options=("Points", "Percentage", "ATR", "Pivot"), group=tpslGroup, tooltip="Points = fixed price distance. Percentage = scales with entry price. ATR = scales with volatility. Pivot = stop at last swing high/low, target = Risk:Reward multiple of it."),
    tpPoints=input.float(100.0, "Take Profit (points)", minval=0.0, step=10.0, group=tpslGroup_points, tooltip="Used when TP/SL Mode = Points. Distance from entry to the take-profit target, in points (1 point = 1 minimum tick). 0 = disabled."),
    slPoints=input.float(50.0, "Stop Loss (points)", minval=0.0, step=10.0, group=tpslGroup_points, tooltip="Used when TP/SL Mode = Points (and Trailing/Break-Even Stop are off). Distance from entry to the stop-loss, in points. 0 = disabled."),
    tpPercent=input.float(1.0, "Take Profit (%)", minval=0.0, step=0.1, group=tpslGroup_per, tooltip="Used when TP/SL Mode = Percentage. Take-profit distance as a % of the entry price. 0 = disabled."),
    slPercent=input.float(0.5, "Stop Loss (%)", minval=0.0, step=0.1, group=tpslGroup_per, tooltip="Used when TP/SL Mode = Percentage (and Trailing/Break-Even Stop are off). Stop-loss distance as a % of entry price. 0 = disabled."),
    atrLength=input.int(14, "ATR Length", minval=1, group=tpslGroup_atr, tooltip="Used when TP/SL Mode = ATR, and/or when Trailing/Break-Even Stop Mode = ATR. Lookback length for the Average True Range."),
    tpAtrMult=input.float(2.0, "Take Profit (ATR multiple)", minval=0.0, step=0.1, group=tpslGroup_atr, tooltip="Used when TP/SL Mode = ATR. Take-profit distance = ATR × this multiple. 0 = disabled."),
    slAtrMult=input.float(2.0, "Stop Loss (ATR multiple)", minval=0.0, step=0.1, group=tpslGroup_atr, tooltip="Used when TP/SL Mode = ATR (and Trailing/Break-Even Stop are off). Stop-loss distance = ATR × this multiple. 0 = disabled."),
    pivotLeftBars=input.int(5, "Pivot Left Bars", minval=1, group=tpslGroup_piv, tooltip="Used when TP/SL Mode = Pivot. Bars required on the left of a swing point for it to qualify as a pivot."),
    pivotRightBars=input.int(5, "Pivot Right Bars", minval=1, group=tpslGroup_piv, tooltip="Used when TP/SL Mode = Pivot. Bars required on the right of a swing point to confirm it — this is also the detection delay."),
    pivotSlBufferPoints=input.float(0.0, "Stop Loss Buffer (points beyond pivot)", minval=0.0, step=5.0, group=tpslGroup_piv, tooltip="Used when TP/SL Mode = Pivot. Extra points placed beyond the pivot so the stop isn't sitting exactly on the swing point. 0 = no buffer."),
    pivotRiskReward=input.float(2.0, "Take Profit (Risk:Reward multiple)", minval=0.0, step=0.1, group=tpslGroup_piv, tooltip="Used when TP/SL Mode = Pivot. Take-profit distance = pivot stop distance × this multiple. 0 = stop-loss only, no take-profit."),
    useTrailingStop=input.bool(False, "Enable Trailing Stop Loss", group=trailGroup, tooltip="When enabled, contributes a stop that continuously follows price and only ever tightens in your favor. Take Profit above is unaffected."),
    trailingMode=input.string("Points", "Trailing Stop Mode", options=("Points", "Percentage", "ATR"), group=trailGroup, tooltip="Same three distance types as Take Profit / Stop Loss above, but applied continuously as the trade runs instead of once at entry."),
    trailPoints=input.float(50.0, "Trailing Distance (points)", minval=0.0, step=10.0, group=trailGroup, tooltip="Used when Trailing Stop Mode = Points. Distance kept between the stop and the best price reached, in points."),
    trailPercent=input.float(0.5, "Trailing Distance (%)", minval=0.0, step=0.1, group=trailGroup, tooltip="Used when Trailing Stop Mode = Percentage. Distance kept, as a % of the current close price."),
    trailAtrMult=input.float(1.5, "Trailing Distance (ATR multiple)", minval=0.0, step=0.1, group=trailGroup, tooltip="Used when Trailing Stop Mode = ATR. Distance kept = current ATR × this multiple."),
    useBreakEven=input.bool(True, "Enable Break-Even Stop", group=beGroup, tooltip="When enabled, moves the stop to entry (+ offset) once price has moved this far in the trade's favor, so the trade can no longer turn into a loss."),
    beMode=input.string("ATR", "Break-Even Trigger Mode", options=("Points", "Percentage", "ATR"), group=beGroup, tooltip="Same three distance types as elsewhere. Determines how far in profit the trade must be before the stop jumps to break-even."),
    beTriggerPoints=input.float(50.0, "Break-Even Trigger (points)", minval=0.0, step=10.0, group=beGroup, tooltip="Used when Break-Even Trigger Mode = Points."),
    beTriggerPercent=input.float(0.5, "Break-Even Trigger (%)", minval=0.0, step=0.1, group=beGroup, tooltip="Used when Break-Even Trigger Mode = Percentage."),
    beTriggerAtrMult=input.float(1.0, "Break-Even Trigger (ATR multiple)", minval=0.0, step=0.1, group=beGroup, tooltip="Used when Break-Even Trigger Mode = ATR."),
    beOffsetPoints=input.float(0.0, "Break-Even Offset (points beyond entry)", minval=0.0, step=5.0, group=beGroup, tooltip="Extra points added beyond entry, in the trade's favor, so the locked-in stop is a hair better than exactly flat (helps cover commission/slippage). 0 = stop exactly at entry."),
    useTimeExit=input.bool(False, "Enable Time-Based Exit", group=timeExitGroup, tooltip="Force-closes a trade that's still open after the given number of bars, instead of waiting indefinitely for Take Profit / Stop Loss."),
    maxBarsInTrade=input.int(50, "Max Bars In Trade", minval=1, group=timeExitGroup, tooltip="Number of bars after entry at which a still-open trade is force-closed at market."),
    useDateFilter=input.bool(False, "Limit Backtest To Date Range", group=dateGroup, tooltip="If enabled, only trades taken between the Start/End dates below are simulated."),
    startDate=input.time(timestamp('2020-01-01T00:00:00'), "Start Date", group=dateGroup),
    endDate=input.time(timestamp('2099-01-01T00:00:00'), "End Date", group=dateGroup),
    showSignalLabels=input.bool(True, "Show Buy/Sell Labels on Chart", group=visualGroup),
    showTpSlLines=input.bool(True, "Show Take Profit / Stop Loss Zones", group=visualGroup),
    showChopBackground=input.bool(True, "Highlight Choppy Market Background", group=visualGroup, tooltip="Shades the chart background while the Trend Filter is blocking new entries. Has no effect if the Trend Filter above is disabled."),
    fastEmaColor=input.color(color.new(color.new('#D4AF37'), 0), "Fast EMA Color", group=visualGroup),
    slowEmaColor=input.color(color.new(color.new('#5B8DEF'), 0), "Slow EMA Color", group=visualGroup),
    tpLineColor=input.color(color.new(color.new('#10B981'), 0), "Take Profit Line Color", group=visualGroup),
    slLineColor=input.color(color.new(color.new('#DC2626'), 0), "Stop Loss Line Color", group=visualGroup),
    beLineColor=input.color(color.new(color.new('#FBBF24'), 0), "Break-Even Stop Color", group=visualGroup, tooltip="Used for the Stop Loss zone once the Break-Even Stop has actually triggered on a trade, so a risk-free trade reads differently from one still risking real loss."),
    buySignalColor=input.color(color.new(color.new('#10B981'), 0), "Buy Signal Color", group=visualGroup),
    sellSignalColor=input.color(color.new(color.new('#DC2626'), 0), "Sell Signal Color", group=visualGroup),
    chopBgColor=input.color(color.new(color.new('#787B86'), 90), "Choppy Market Background Color", group=visualGroup),
    showStatusTable=input.bool(True, "Show Status Table", group=tableGroup),
    tablePositionMode=input.string("Top Right", "Position", options=("Top Right", "Top Left", "Bottom Right", "Bottom Left"), group=tableGroup),
    wm_theme=input.string('Dark', 'Watermark Theme', group=' A X E A L G O ', options=('Dark', 'Light'))
):
    fastEMA = ta.ema(emaSource, fastLength)
    slowEMA = ta.ema(emaSource, slowLength)

    atrValue = ta.atr(atrLength)

    rawPivotHigh = ta.pivothigh(pivotLeftBars, pivotRightBars)
    rawPivotLow = ta.pivotlow(pivotLeftBars, pivotRightBars)

    lastPivotHigh: Persistent[float] = na(float)
    lastPivotLow: Persistent[float] = na(float)
    if not na(rawPivotHigh):
        lastPivotHigh = rawPivotHigh
    if not na(rawPivotLow):
        lastPivotLow = rawPivotLow

    diPlusUnused, diMinusUnused, adxValue = ta.dmi(adxLength, adxSmoothing)

    def f_pointsToPrice(points: float):
        return points * syminfo.mintick

    def f_calcTpSlPoints(entryPrice: float, isLong: bool, tpPoints: float, slPoints: float):
        tpDistance = f_pointsToPrice(tpPoints)
        slDistance = f_pointsToPrice(slPoints)
        takeProfitPrice = (entryPrice + tpDistance if isLong else entryPrice - tpDistance) if tpPoints > 0 else na
        stopLossPrice = (entryPrice - slDistance if isLong else entryPrice + slDistance) if slPoints > 0 else na
        return (takeProfitPrice, stopLossPrice)

    def f_percentToPrice(referencePrice: float, percent: float):
        return referencePrice * (percent / 100)

    def f_calcTpSlPercent(entryPrice: float, isLong: bool, tpPercent: float, slPercent: float):
        tpDistance = f_percentToPrice(entryPrice, tpPercent)
        slDistance = f_percentToPrice(entryPrice, slPercent)
        takeProfitPrice = (entryPrice + tpDistance if isLong else entryPrice - tpDistance) if tpPercent > 0 else na
        stopLossPrice = (entryPrice - slDistance if isLong else entryPrice + slDistance) if slPercent > 0 else na
        return (takeProfitPrice, stopLossPrice)

    def f_atrToPrice(atrValue: float, atrMultiple: float):
        return atrValue * atrMultiple

    def f_calcTpSlAtr(entryPrice: float, isLong: bool, atrValue: float, tpAtrMult: float, slAtrMult: float):
        tpDistance = f_atrToPrice(atrValue, tpAtrMult)
        slDistance = f_atrToPrice(atrValue, slAtrMult)
        takeProfitPrice = (entryPrice + tpDistance if isLong else entryPrice - tpDistance) if tpAtrMult > 0 else na
        stopLossPrice = (entryPrice - slDistance if isLong else entryPrice + slDistance) if slAtrMult > 0 else na
        return (takeProfitPrice, stopLossPrice)

    def f_pivotToDistance(entryPrice: float, pivotLevel: float):
        return math.abs(entryPrice - pivotLevel)

    def f_calcTpSlPivot(entryPrice: float, isLong: bool, pivotHigh: float, pivotLow: float, slBufferPts: float, riskReward: float):
        structureLevel = pivotLow if isLong else pivotHigh
        hasStructure = not na(structureLevel)
        bufferDistance = f_pointsToPrice(slBufferPts)
        stopLossPrice = (structureLevel - bufferDistance if isLong else structureLevel + bufferDistance) if hasStructure else na
        slDistance = f_pivotToDistance(entryPrice, stopLossPrice) if hasStructure else na
        takeProfitPrice = (entryPrice + slDistance * riskReward if isLong else entryPrice - slDistance * riskReward) if hasStructure and riskReward > 0 else na
        return (takeProfitPrice, stopLossPrice)

    def f_resolveTrailDistance(mode: str, points: float, percent: float, atrMultiple: float, referencePrice: float, atrValue: float):
        __block_result__ = na
        if mode == 'Points':
            __block_result__ = f_pointsToPrice(points)
        elif mode == 'Percentage':
            __block_result__ = f_percentToPrice(referencePrice, percent)
        else:
            __block_result__ = f_atrToPrice(atrValue, atrMultiple)
        return __block_result__

    def f_updateTrailingStop(isLong: bool, extremePrice: float, trailDistance: float, prevStop: float):
        candidateStop = extremePrice - trailDistance if isLong else extremePrice + trailDistance
        newStop = candidateStop if na(prevStop) else math.max(prevStop, candidateStop) if isLong else math.min(prevStop, candidateStop)
        return newStop

    def f_calcBreakEvenStop(isLong: bool, entryPrice: float, currentPrice: float, triggerDistance: float, offsetDistance: float, prevStop: float):
        profit = currentPrice - entryPrice if isLong else entryPrice - currentPrice
        triggered = profit >= triggerDistance
        breakEvenLevel = entryPrice + offsetDistance if isLong else entryPrice - offsetDistance
        newStop = (breakEvenLevel if na(prevStop) else math.max(prevStop, breakEvenLevel) if isLong else math.min(prevStop, breakEvenLevel)) if triggered else prevStop
        return (newStop, triggered)

    def f_combineStops(isLong: bool, stopA: float, stopB: float):
        hasA = not na(stopA)
        hasB = not na(stopB)
        combined = (math.max(stopA, stopB) if isLong else math.min(stopA, stopB)) if hasA and hasB else stopA if hasA else stopB if hasB else na
        return combined

    def f_isTradeExpired(barsSinceEntry: int, maxBars: int):
        return barsSinceEntry >= maxBars

    def f_passesTrendFilter(filterEnabled: bool, adxValue: float, adxThreshold: float):
        return not filterEnabled or adxValue >= adxThreshold

    bullishCross = ta.crossover(fastEMA, slowEMA)
    bearishCross = ta.crossunder(fastEMA, slowEMA)

    inDateRange = not useDateFilter or (time >= startDate and time <= endDate)

    trendFilterOk = f_passesTrendFilter(useTrendFilter, adxValue, adxThreshold)

    chopZone = useTrendFilter and (not trendFilterOk)

    bgcolor(chopBgColor if showChopBackground and chopZone else na, title='Choppy Market (Trend Filter Active)')

    plotshape(showSignalLabels and bullishCross and trendFilterOk, title='Buy Signal', style=shape.triangleup, location=location.belowbar, color=buySignalColor, size=size.tiny, text='LONG', textcolor=buySignalColor)

    plotshape(showSignalLabels and bearishCross and trendFilterOk, title='Sell Signal', style=shape.triangledown, location=location.abovebar, color=sellSignalColor, size=size.tiny, text='SHORT', textcolor=sellSignalColor)

    def f_resolveTpSl(entryPrice: float, isLong: bool, mode: str, tpPts: float, slPts: float, tpPct: float, slPct: float, atrVal: float, tpAtrMult: float, slAtrMult: float, pivotHigh: float, pivotLow: float, pivotSlBuffer: float, pivotRR: float):
        __block_result_1__ = (na, na)
        if mode == 'Points':
            __block_result_1__ = f_calcTpSlPoints(entryPrice, isLong, tpPts, slPts)
        elif mode == 'Percentage':
            __block_result_1__ = f_calcTpSlPercent(entryPrice, isLong, tpPct, slPct)
        elif mode == 'ATR':
            __block_result_1__ = f_calcTpSlAtr(entryPrice, isLong, atrVal, tpAtrMult, slAtrMult)
        else:
            __block_result_1__ = f_calcTpSlPivot(entryPrice, isLong, pivotHigh, pivotLow, pivotSlBuffer, pivotRR)
        return __block_result_1__

    activeTpPrice: Persistent[float] = na(float)
    activeSlPrice: Persistent[float] = na(float)
    activeSide: Persistent[str] = na(str)
    tradeExtreme: Persistent[float] = na(float)
    trailStopPrice: Persistent[float] = na(float)
    breakEvenStopPrice: Persistent[float] = na(float)
    breakEvenActive: Persistent[bool] = False
    entryBarIndex: Persistent[int] = na(int)

    if strategy.position_size == 0:
        activeTpPrice = na
        activeSlPrice = na
        activeSide = na
        tradeExtreme = na
        trailStopPrice = na
        breakEvenStopPrice = na
        breakEvenActive = False
        entryBarIndex = na

    usingDynamicStop = useTrailingStop or useBreakEven

    if bullishCross and inDateRange:
        if allowShort:
            strategy.close('Short', comment='Close Short (Bull Cross)')
        if allowLong and trendFilterOk:
            strategy.entry('Long', strategy.long, comment='Buy')
            activeSide = "Long"
            tradeExtreme = high
            entryBarIndex = bar_index
            if useTpSl:
                tpPrice, slPrice = f_resolveTpSl(close, True, tpslMode, tpPoints, slPoints, tpPercent, slPercent, atrValue, tpAtrMult, slAtrMult, lastPivotHigh, lastPivotLow, pivotSlBufferPoints, pivotRiskReward)
                activeTpPrice = tpPrice
                activeSlPrice = na if usingDynamicStop else slPrice
                if useBreakEven:
                    breakEvenStopPrice = slPrice
                if not usingDynamicStop:
                    strategy.exit('Long Exit', from_entry='Long', limit=tpPrice, stop=slPrice, comment_profit='TP Hit', comment_loss='SL Hit')

    if bearishCross and inDateRange:
        if allowLong:
            strategy.close('Long', comment='Close Long (Bear Cross)')
        if allowShort and trendFilterOk:
            strategy.entry('Short', strategy.short, comment='Sell')
            activeSide = "Short"
            tradeExtreme = low
            entryBarIndex = bar_index
            if useTpSl:
                tpPrice, slPrice = f_resolveTpSl(close, False, tpslMode, tpPoints, slPoints, tpPercent, slPercent, atrValue, tpAtrMult, slAtrMult, lastPivotHigh, lastPivotLow, pivotSlBufferPoints, pivotRiskReward)
                activeTpPrice = tpPrice
                activeSlPrice = na if usingDynamicStop else slPrice
                if useBreakEven:
                    breakEvenStopPrice = slPrice
                if not usingDynamicStop:
                    strategy.exit('Short Exit', from_entry='Short', limit=tpPrice, stop=slPrice, comment_profit='TP Hit', comment_loss='SL Hit')

    if usingDynamicStop and strategy.position_size != 0 and (not na(activeSide)):
        isLong = activeSide == 'Long'
        tradeExtreme = math.max(tradeExtreme, high) if isLong else math.min(tradeExtreme, low)

        trailDistance = f_resolveTrailDistance(trailingMode, trailPoints, trailPercent, trailAtrMult, close, atrValue)
        trailCandidate = f_updateTrailingStop(isLong, tradeExtreme, trailDistance, trailStopPrice) if useTrailingStop else trailStopPrice

        beTriggerDistance = f_resolveTrailDistance(beMode, beTriggerPoints, beTriggerPercent, beTriggerAtrMult, strategy.position_avg_price, atrValue)
        beOffsetDistance = f_pointsToPrice(beOffsetPoints)
        beCandidate = breakEvenStopPrice
        beTriggeredNow: bool = False
        if useBreakEven:
            beCandidate1, beTriggeredNow1 = f_calcBreakEvenStop(isLong, strategy.position_avg_price, close, beTriggerDistance, beOffsetDistance, breakEvenStopPrice)
            beCandidate = beCandidate1
            beTriggeredNow = beTriggeredNow1

        trailStopPrice = trailCandidate
        breakEvenStopPrice = beCandidate
        breakEvenActive = breakEvenActive or beTriggeredNow
        activeSlPrice = f_combineStops(isLong, trailCandidate, beCandidate)

        strategy.exit('Long Exit' if isLong else 'Short Exit', from_entry='Long' if isLong else 'Short', limit=activeTpPrice, stop=activeSlPrice, comment_profit='TP Hit', comment_loss='SL Hit')

    if useTimeExit and strategy.position_size != 0 and (not na(entryBarIndex)) and f_isTradeExpired(bar_index - entryBarIndex, maxBarsInTrade):
        strategy.close('Long' if activeSide == 'Long' else 'Short', comment='Time Exit')

    def f_priceFormat():
        tick = syminfo.mintick
        __block_result_2__ = na
        if tick <= 1e-05:
            __block_result_2__ = "0.00000"
        elif tick <= 0.0001:
            __block_result_2__ = "0.0000"
        elif tick <= 0.001:
            __block_result_2__ = "0.000"
        elif tick <= 0.01:
            __block_result_2__ = "0.00"
        elif tick <= 0.1:
            __block_result_2__ = "0.0"
        else:
            __block_result_2__ = "0"
        return __block_result_2__

    priceFmt = f_priceFormat()

    tpZoneFillColor = color.new(tpLineColor, 88)
    tpZoneBorderColor = color.new(tpLineColor, 45)
    slZoneFillColor = color.new(slLineColor, 88)
    slZoneBorderColor = color.new(slLineColor, 45)
    beZoneFillColor = color.new(beLineColor, 88)
    beZoneBorderColor = color.new(beLineColor, 45)

    slZoneIsBreakEven = useBreakEven and breakEvenActive
    slZoneFill = beZoneFillColor if slZoneIsBreakEven else slZoneFillColor
    slZoneBorder = beZoneBorderColor if slZoneIsBreakEven else slZoneBorderColor
    slZoneTextColor = beLineColor if slZoneIsBreakEven else slLineColor
    slZonePrefix = 'BE  ' if slZoneIsBreakEven else 'SL  '

    tpZone: Persistent[Box] = na(Box)
    slZone: Persistent[Box] = na(Box)
    tpZoneLabel: Persistent[Label] = na(Label)
    slZoneLabel: Persistent[Label] = na(Label)

    if showTpSlLines and strategy.position_size != 0 and (not na(entryBarIndex)):
        entryPrice = strategy.position_avg_price

        if not na(activeTpPrice):
            tpTop = math.max(entryPrice, activeTpPrice)
            tpBottom = math.min(entryPrice, activeTpPrice)
            if na(tpZone):
                tpZone = box.new(entryBarIndex, tpTop, bar_index, tpBottom, border_color=tpZoneBorderColor, border_width=1, bgcolor=tpZoneFillColor)
                tpZoneLabel = label.new(bar_index, activeTpPrice, 'TP  ' + string.tostring(activeTpPrice, priceFmt), style=label.style_label_left, color=color.new(color.white, 100), textcolor=tpLineColor, size=size.small)
            else:
                box.set_left(tpZone, entryBarIndex)
                box.set_top(tpZone, tpTop)
                box.set_bottom(tpZone, tpBottom)
                box.set_right(tpZone, bar_index)
                label.set_xy(tpZoneLabel, bar_index, activeTpPrice)
                label.set_text(tpZoneLabel, 'TP  ' + string.tostring(activeTpPrice, priceFmt))
        elif not na(tpZone):
            box.delete(tpZone)
            label.delete(tpZoneLabel)
            tpZone = na
            tpZoneLabel = na

        if not na(activeSlPrice):
            slTop = math.max(entryPrice, activeSlPrice)
            slBottom = math.min(entryPrice, activeSlPrice)
            if na(slZone):
                slZone = box.new(entryBarIndex, slTop, bar_index, slBottom, border_color=slZoneBorder, border_width=1, bgcolor=slZoneFill)
                slZoneLabel = label.new(bar_index, activeSlPrice, slZonePrefix + string.tostring(activeSlPrice, priceFmt), style=label.style_label_left, color=color.new(color.white, 100), textcolor=slZoneTextColor, size=size.small)
            else:
                box.set_left(slZone, entryBarIndex)
                box.set_top(slZone, slTop)
                box.set_bottom(slZone, slBottom)
                box.set_right(slZone, bar_index)
                box.set_border_color(slZone, slZoneBorder)
                box.set_bgcolor(slZone, slZoneFill)
                label.set_xy(slZoneLabel, bar_index, activeSlPrice)
                label.set_text(slZoneLabel, slZonePrefix + string.tostring(activeSlPrice, priceFmt))
                label.set_textcolor(slZoneLabel, slZoneTextColor)
        elif not na(slZone):
            box.delete(slZone)
            label.delete(slZoneLabel)
            slZone = na
            slZoneLabel = na
    else:
        if not na(tpZone):
            box.delete(tpZone)
            label.delete(tpZoneLabel)
            tpZone = na
            tpZoneLabel = na
        if not na(slZone):
            box.delete(slZone)
            label.delete(slZoneLabel)
            slZone = na
            slZoneLabel = na

    alertcondition(bullishCross and trendFilterOk, title='Bullish EMA Cross (Buy)', message='TP/SL Toolkit [AxeAlgo]: Fast EMA crossed ABOVE Slow EMA on {{ticker}} ({{interval}}) - BUY signal.')

    alertcondition(bearishCross and trendFilterOk, title='Bearish EMA Cross (Sell)', message='TP/SL Toolkit [AxeAlgo]: Fast EMA crossed BELOW Slow EMA on {{ticker}} ({{interval}}) - SELL signal.')

    def f_toTablePosition(posText: str):
        __block_result_3__ = na
        __switch__ = posText
        if __switch__ == "Top Right":
            __block_result_3__ = position.top_right
        elif __switch__ == "Top Left":
            __block_result_3__ = position.top_left
        elif __switch__ == "Bottom Right":
            __block_result_3__ = position.bottom_right
        elif __switch__ == "Bottom Left":
            __block_result_3__ = position.bottom_left
        else:
            __block_result_3__ = position.top_right
        return __block_result_3__

    trendIsBullish = fastEMA > slowEMA
    inPosition = strategy.position_size != 0

    rewardDistance = math.abs(activeTpPrice - strategy.position_avg_price) if inPosition and (not na(activeTpPrice)) else na
    riskDistance = math.abs(strategy.position_avg_price - activeSlPrice) if inPosition and (not na(activeSlPrice)) else na
    riskRewardText = '1 : ' + string.tostring(rewardDistance / riskDistance, '0.00') if not na(rewardDistance) and (not na(riskDistance)) and (riskDistance > 0) else '—'

    statusTable: Persistent[Table] = na(Table)
    if showStatusTable:
        statusTable = table.new(f_toTablePosition(tablePositionMode), 2, 8, bgcolor=color.new(color.new('#131722'), 15), border_color=color.new(color.gray, 50), border_width=1)
        table.merge_cells(statusTable, 0, 0, 1, 0)

        table.cell(statusTable, 0, 0, 'TP/SL TOOLKIT [AXEALGO]', text_color=color.new(color.new('#D4AF37'), 0), text_size=size.small, text_halign=text.align_center)

        table.cell(statusTable, 0, 1, 'Trend', text_color=color.gray, text_size=size.small, text_halign=text.align_left)
        table.cell(statusTable, 1, 1, 'Bullish ▲' if trendIsBullish else 'Bearish ▼', text_color=buySignalColor if trendIsBullish else sellSignalColor, text_size=size.small, text_halign=text.align_right)

        table.cell(statusTable, 0, 2, 'Position', text_color=color.gray, text_size=size.small, text_halign=text.align_left)
        table.cell(statusTable, 1, 2, 'Flat' if na(activeSide) else activeSide, text_color=color.silver if na(activeSide) else buySignalColor if activeSide == 'Long' else sellSignalColor, text_size=size.small, text_halign=text.align_right)

        table.cell(statusTable, 0, 3, 'Entry', text_color=color.gray, text_size=size.small, text_halign=text.align_left)
        table.cell(statusTable, 1, 3, string.tostring(strategy.position_avg_price, priceFmt) if inPosition else '—', text_color=color.silver, text_size=size.small, text_halign=text.align_right)

        table.cell(statusTable, 0, 4, 'Take Profit', text_color=color.gray, text_size=size.small, text_halign=text.align_left)
        table.cell(statusTable, 1, 4, '—' if na(activeTpPrice) else string.tostring(activeTpPrice, priceFmt), text_color=tpLineColor, text_size=size.small, text_halign=text.align_right)

        table.cell(statusTable, 0, 5, 'Stop Loss', text_color=color.gray, text_size=size.small, text_halign=text.align_left)
        table.cell(statusTable, 1, 5, '—' if na(activeSlPrice) else string.tostring(activeSlPrice, priceFmt), text_color=slLineColor, text_size=size.small, text_halign=text.align_right)

        table.cell(statusTable, 0, 6, 'Risk : Reward', text_color=color.gray, text_size=size.small, text_halign=text.align_left)
        table.cell(statusTable, 1, 6, riskRewardText, text_color=color.silver, text_size=size.small, text_halign=text.align_right)

        table.cell(statusTable, 0, 7, 'ADX', text_color=color.gray, text_size=size.small, text_halign=text.align_left)
        table.cell(statusTable, 1, 7, string.tostring(adxValue, '0.0') + (' (Choppy)' if chopZone else ' (Trending)') if useTrendFilter else 'Filter Off', text_color=(sellSignalColor if chopZone else buySignalColor) if useTrendFilter else color.silver, text_size=size.small, text_halign=text.align_right)

    if True:
        dark = wm_theme == 'Dark'
        wm_bg = color.new(color.new('#0D1117'), 0) if dark else color.new(color.new('#F0F2F5'), 0)
        wm_dot_col = color.new(color.new('#26A69A'), 25) if dark else color.new(color.new('#26A69A'), 10)
        wm_txt_col = color.new(color.new('#4D5566'), 0) if dark else color.new(color.new('#6B7280'), 0)
        wm_frm_col = color.new(color.new('#2A2E39'), 0) if dark else color.new(color.new('#C8CDD6'), 0)

        wm = table.new(position.bottom_center, 2, 1, frame_color=wm_frm_col, frame_width=1, border_width=0)
        table.cell(wm, 0, 0, ' ◆ ', bgcolor=wm_bg, text_color=wm_dot_col, text_size=size.tiny, text_halign=text.align_center, text_valign=text.align_center)
        table.cell(wm, 1, 0, ' A X E A L G O ', bgcolor=wm_bg, text_color=wm_txt_col, text_size=size.small, text_halign=text.align_left, text_valign=text.align_center)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
