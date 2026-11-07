"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, close, color, extend, high, input, line,
    location, low, math, na, open, plot, plotshape, script, shape, size, strategy, ta
)
from pynecore.types import Line, Persistent, Series

grpMain: str = 'Main Settings'
grpRisk: str = 'Risk Settings'
grpFilters: str = 'Optional Filters'
grpVisual: str = 'Visual / Debug Settings'


@script.strategy('20 / 200 SMA Bot Strategy - Clean Usable Version', overlay=True, pyramiding=0, max_labels_count=500, max_lines_count=500, initial_capital=50000, default_qty_type=strategy.fixed, default_qty_value=1, process_orders_on_close=True, margin_long=0, margin_short=0, close_by_id=True)
def main(
    tradeDirection=input.string('Both', 'Trade Direction', options=('Both', 'Buy Only', 'Sell Only'), group=grpMain),
    fastLength=input.int(20, 'Fast SMA Length', minval=1, group=grpMain),
    slowLength=input.int(200, 'Slow SMA Length', minval=1, group=grpMain),
    entryStrictness=input.string('Trend Pullback Entry', 'Entry Strictness', options=('Original Cross Entry', 'Trend Pullback Entry', 'Relaxed Testing Entry'), group=grpMain),
    entryWindowBars=input.int(100, 'Bars Allowed After SMA Cross', minval=1, maxval=1000, group=grpMain),
    takeProfitPoints=input.float(100.0, 'Take Profit Points', minval=0.25, step=0.25, group=grpRisk),
    stopLossMode=input.string('Last Opposing Candle Beyond 200 SMA', 'Stop Loss Method', options=('Last Opposing Candle Beyond 200 SMA', 'Fixed Points', 'Recent Swing'), group=grpRisk),
    fixedStopPoints=input.float(30.0, 'Fixed / Fallback Stop Points', minval=0.25, step=0.25, group=grpRisk),
    stopBufferPoints=input.float(1.0, 'Stop Buffer Points', minval=0.0, step=0.25, group=grpRisk),
    opposingLookback=input.int(300, 'Opposing Candle Lookback', minval=1, maxval=2000, group=grpRisk),
    swingLookback=input.int(10, 'Recent Swing Lookback', minval=1, maxval=500, group=grpRisk),
    useOpposingWick=input.bool(True, 'Opposing Candle Stop Uses Wick', group=grpRisk),
    use200SlopeFilter=input.bool(False, 'Use 200 SMA Slope Filter', group=grpFilters),
    slopeLookback=input.int(5, '200 SMA Slope Lookback', minval=1, maxval=100, group=grpFilters),
    useCandleColorFilter=input.bool(False, 'Use Candle Color Filter', group=grpFilters),
    useDistanceFilter=input.bool(False, 'Avoid Entries Too Far From 20 SMA', group=grpFilters),
    maxDistanceFrom20=input.float(50.0, 'Max Distance From 20 SMA', minval=0.25, step=0.25, group=grpFilters),
    showSMAs=input.bool(True, 'Show SMAs', group=grpVisual),
    showTradeLabels=input.bool(True, 'Show Trade Labels', group=grpVisual),
    showDebugSignals=input.bool(True, 'Show Debug Markers', group=grpVisual),
    showStopTargetLines=input.bool(True, 'Show Stop / Target Lines', group=grpVisual),
    fastSmaColor=input.color(color.orange, '20 SMA Color', group=grpVisual),
    slowSmaColor=input.color(color.blue, '200 SMA Color', group=grpVisual)
):
    allowLong = tradeDirection == 'Both' or tradeDirection == 'Buy Only'
    allowShort = tradeDirection == 'Both' or tradeDirection == 'Sell Only'
    fastSma = ta.sma(close, fastLength)
    slowSma: Series = ta.sma(close, slowLength)
    bullCross = ta.crossover(fastSma, slowSma)
    bearCross = ta.crossunder(fastSma, slowSma)
    fastAboveSlow = fastSma > slowSma
    fastBelowSlow = fastSma < slowSma
    closeAboveFast = close > fastSma
    closeBelowFast = close < fastSma
    bullCandle = close > open
    bearCandle = close < open
    slowSmaRising = slowSma > slowSma[slopeLookback]
    slowSmaFalling = slowSma < slowSma[slopeLookback]
    distanceFrom20 = math.abs(close - fastSma)
    longArmed: Persistent[bool] = False
    shortArmed: Persistent[bool] = False
    longCrossBar: Persistent[int] = na(int)
    shortCrossBar: Persistent[int] = na(int)
    if bullCross:
        longArmed = True
        shortArmed = False
        longCrossBar = bar_index
    if bearCross:
        shortArmed = True
        longArmed = False
        shortCrossBar = bar_index
    longWindowValid = longArmed and (not na(longCrossBar)) and (bar_index - longCrossBar <= entryWindowBars)
    shortWindowValid = shortArmed and (not na(shortCrossBar)) and (bar_index - shortCrossBar <= entryWindowBars)
    originalLong = longWindowValid and closeAboveFast
    originalShort = shortWindowValid and closeBelowFast
    crossover_1 = ta.crossover(close, fastSma)
    trendPullbackLong = fastAboveSlow and crossover_1
    crossunder_1 = ta.crossunder(close, fastSma)
    trendPullbackShort = fastBelowSlow and crossunder_1
    relaxedLong = fastAboveSlow and closeAboveFast
    relaxedShort = fastBelowSlow and closeBelowFast
    baseLongSignal = originalLong if entryStrictness == 'Original Cross Entry' else trendPullbackLong if entryStrictness == 'Trend Pullback Entry' else relaxedLong
    baseShortSignal = originalShort if entryStrictness == 'Original Cross Entry' else trendPullbackShort if entryStrictness == 'Trend Pullback Entry' else relaxedShort
    longSlopeOk = slowSmaRising if use200SlopeFilter else True
    shortSlopeOk = slowSmaFalling if use200SlopeFilter else True
    longCandleOk = bullCandle if useCandleColorFilter else True
    shortCandleOk = bearCandle if useCandleColorFilter else True
    distanceOk = distanceFrom20 <= maxDistanceFrom20 if useDistanceFilter else True
    longSignal = allowLong and baseLongSignal and longSlopeOk and longCandleOk and distanceOk and (strategy.position_size == 0)
    shortSignal = allowShort and baseShortSignal and shortSlopeOk and shortCandleOk and distanceOk and (strategy.position_size == 0)
    buyOpposingCondition = close < open and close < slowSma
    sellOpposingCondition = close > open and close > slowSma
    buyOppBarsAgo = ta.barssince(buyOpposingCondition)
    sellOppBarsAgo = ta.barssince(sellOpposingCondition)
    buyOppStopRaw = ta.valuewhen(buyOpposingCondition, low, 0) if useOpposingWick else ta.valuewhen(buyOpposingCondition, math.min(open, close), 0)
    sellOppStopRaw = ta.valuewhen(sellOpposingCondition, high, 0) if useOpposingWick else ta.valuewhen(sellOpposingCondition, math.max(open, close), 0)
    buyOppStop = buyOppStopRaw if buyOppBarsAgo <= opposingLookback else na
    sellOppStop = sellOppStopRaw if sellOppBarsAgo <= opposingLookback else na
    longStopByOpposing = buyOppStop - stopBufferPoints
    shortStopByOpposing = sellOppStop + stopBufferPoints
    longStopByFixed = close - fixedStopPoints
    shortStopByFixed = close + fixedStopPoints
    longStopBySwing = ta.lowest(low, swingLookback) - stopBufferPoints
    shortStopBySwing = ta.highest(high, swingLookback) + stopBufferPoints
    selectedLongStop = longStopByOpposing if stopLossMode == 'Last Opposing Candle Beyond 200 SMA' else longStopByFixed if stopLossMode == 'Fixed Points' else longStopBySwing
    selectedShortStop = shortStopByOpposing if stopLossMode == 'Last Opposing Candle Beyond 200 SMA' else shortStopByFixed if stopLossMode == 'Fixed Points' else shortStopBySwing
    finalLongStop = selectedLongStop if not na(selectedLongStop) and selectedLongStop < close else longStopByFixed
    finalShortStop = selectedShortStop if not na(selectedShortStop) and selectedShortStop > close else shortStopByFixed
    longTarget = close + takeProfitPoints
    shortTarget = close - takeProfitPoints
    if longSignal:
        strategy.entry('BUY', strategy.long)
        strategy.exit('BUY TP/SL', from_entry='BUY', stop=finalLongStop, limit=longTarget)
        longArmed = False
    if shortSignal:
        strategy.entry('SELL', strategy.short)
        strategy.exit('SELL TP/SL', from_entry='SELL', stop=finalShortStop, limit=shortTarget)
        shortArmed = False
    plot(fastSma if showSMAs else na, '20 SMA', color=fastSmaColor, linewidth=2)
    plot(slowSma if showSMAs else na, '200 SMA', color=slowSmaColor, linewidth=2)
    plotshape(showTradeLabels and longSignal, title='BUY', style=shape.labelup, text='BUY', color=color.lime, textcolor=color.black, location=location.belowbar, size=size.small)
    plotshape(showTradeLabels and shortSignal, title='SELL', style=shape.labeldown, text='SELL', color=color.red, textcolor=color.white, location=location.abovebar, size=size.small)
    plotshape(showDebugSignals and bullCross, title='Bullish SMA Cross', style=shape.triangleup, text='Cross Up', color=color.green, textcolor=color.white, location=location.belowbar, size=size.tiny)
    plotshape(showDebugSignals and bearCross, title='Bearish SMA Cross', style=shape.triangledown, text='Cross Down', color=color.red, textcolor=color.white, location=location.abovebar, size=size.tiny)
    plotshape(showDebugSignals and longArmed, title='Long Armed', style=shape.circle, color=color.green, location=location.bottom, size=size.tiny)
    plotshape(showDebugSignals and shortArmed, title='Short Armed', style=shape.circle, color=color.red, location=location.top, size=size.tiny)
    stopLine: Persistent[Line] = na(Line)
    targetLine: Persistent[Line] = na(Line)
    if showStopTargetLines and longSignal:
        if not na(stopLine):
            line.delete(stopLine)
        if not na(targetLine):
            line.delete(targetLine)
        stopLine = line.new(bar_index, finalLongStop, bar_index + 20, finalLongStop, extend=extend.right, color=color.red, width=2)
        targetLine = line.new(bar_index, longTarget, bar_index + 20, longTarget, extend=extend.right, color=color.green, width=2)
    if showStopTargetLines and shortSignal:
        if not na(stopLine):
            line.delete(stopLine)
        if not na(targetLine):
            line.delete(targetLine)
        stopLine = line.new(bar_index, finalShortStop, bar_index + 20, finalShortStop, extend=extend.right, color=color.red, width=2)
        targetLine = line.new(bar_index, shortTarget, bar_index + 20, shortTarget, extend=extend.right, color=color.green, width=2)
    alertcondition(longSignal, title='BUY Signal', message='BUY Signal triggered.')
    alertcondition(shortSignal, title='SELL Signal', message='SELL Signal triggered.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
