"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, close, color, display, fill, high, input, location, low, na,
    ohlc4, open, plot, plotshape, script, shape, size, strategy, ta, time, timestamp
)
from pynecore.types import Persistent, Series


@script.strategy('Double Supertrend', overlay=True, currency='USD', default_qty_value=1, process_orders_on_close=True, pyramiding=10, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, close_by_id=True, na_bool=True)
def main(
    showIndicators=input.bool(True, 'Show Indicators', group='Technical Analysis'),
    atrPeriod=input(14, 'Length', group='Technical Analysis', inline='ATR'),
    factor1=input.float(1.0, 'Dev Fast', step=0.01, group='Technical Analysis', inline='ATR'),
    factor2=input.float(4.0, 'Dev Slow', step=0.01, group='Technical Analysis', inline='ATR'),
    exitType=input.string('ATR', 'Exit Type', options=('Reversals', 'ATR', 'Fast Supertrend', 'Slow Supertrend'), group='Technical Analysis', inline='Exit Type'),
    exitLength=input.int(60, 'Period', group='Technical Analysis', inline='Exit Type'),
    exitMultiplier=input.int(2, 'Multiplier', group='Technical Analysis', inline='Exit Type'),
    useStrategy=input.bool(True, 'Use The Strategy', group='Strategy'),
    showLongs=input.bool(True, 'Show/Use Long Entries', group='Strategy', inline='Entries'),
    showShorts=input.bool(True, 'Show/Use Short Entries', group='Strategy', inline='Entries'),
    entryAlerts=input.bool(True, 'Enable Entry Alerts', group='Strategy', inline='Entries'),
    showExitLongs=input.bool(True, 'Show/Use Exit Longs', group='Strategy', inline='Exits'),
    showExitShorts=input.bool(True, 'Show/Use Exit Shorts', group='Strategy', inline='Exits'),
    exitAlerts=input.bool(True, 'Enable Exit Alerts', group='Strategy', inline='Exits'),
    showAddLongs=input.bool(True, 'Show/Use Add Longs', group='Strategy', inline='Adds'),
    showAddShorts=input.bool(True, 'Show/Use Add Shorts', group='Strategy', inline='Adds'),
    addAlerts=input.bool(True, 'Enable Add Alerts', group='Strategy', inline='Adds'),
    dateStart=input.time(timestamp('2021-12-01T10:00:00-03:00'), 'Trades Date Start', group='Strategy'),
    dateEnd=input.time(timestamp('2022-02-01T10:00:00-03:00'), 'Trades Date End', group='Strategy')
):
    buy: Persistent[bool] = True
    sell: Persistent[bool] = True
    isInsideDateRange = time > dateStart and time < dateEnd
    bodyMiddleValue = (open + close) / 2
    rangeMiddleValue = (high + low) / 2
    direction1: Series
    supertrend1, direction1 = ta.supertrend(factor1, atrPeriod)
    direction2: Series
    supertrend2, direction2 = ta.supertrend(factor2, atrPeriod)
    diffFromTop: Series = ta.highest(exitLength) - (ta.highest(exitLength) - ta.lowest(exitLength / 4)) / 2
    diffFromBottom: Series = ta.lowest(exitLength) + (ta.highest(exitLength / 4) - ta.lowest(exitLength)) / 2
    condLong: Series = direction1 < 0 and direction2 < 0 and (direction1[1] > 0 or direction2[1] > 0)
    condShort: Series = direction1 > 0 and direction2 > 0 and (direction1[1] < 0 or direction2[1] < 0)
    atr = ta.atr(atrPeriod)
    def getATRPrice(type):
        return close + atr * exitMultiplier * (1 if type == 'long' else -1)

    longTakeProfit: Persistent = getATRPrice('long')
    shortTakeProfit: Persistent = getATRPrice('Short')
    if condLong and buy:
        longTakeProfit = getATRPrice('long')
    if condShort and sell:
        shortTakeProfit = getATRPrice('Short')
    colorSignal1 = color.from_gradient(ohlc4, ta.lowest(exitLength / 4), ta.highest(exitLength), color.green, color.aqua)
    colorSignal2 = color.from_gradient(ohlc4, ta.lowest(exitLength), ta.highest(exitLength / 4), color.red, color.orange)
    plotshape(condLong and buy, 'Trend Up', shape.triangleup, location.belowbar, color.lime, 0, 'Long', color.lime, False, size.small)
    plotshape(condShort and sell, 'Trend Down', shape.triangledown, location.abovebar, color.red, 0, 'Short', color.red, False, size.small)
    if useStrategy and isInsideDateRange:
        if condLong and buy and showLongs:
            strategy.entry('Long', strategy.long)
            if entryAlerts:
                alert('Entry Long', alert.freq_once_per_bar)
        if condShort and sell and showShorts:
            strategy.entry('Short', strategy.short)
            if entryAlerts:
                alert('Entry Short', alert.freq_once_per_bar)
    plotshape(ohlc4 <= diffFromTop and ohlc4[1] > diffFromTop[1] and sell and (not condShort) and showExitLongs, 'Exit Trend Up', shape.xcross, location.abovebar, color.aqua, 0, 'Exit', color.aqua, False, size.tiny)
    plotshape(ohlc4 >= diffFromBottom and ohlc4[1] < diffFromBottom[1] and buy and (not condLong) and showExitShorts, 'Exit Trend Down', shape.xcross, location.belowbar, color.orange, 0, 'Exit', color.orange, False, size.tiny)
    if sell and (not condShort) and showExitLongs and isInsideDateRange:
        if ohlc4 <= diffFromTop and ohlc4[1] > diffFromTop[1] and (exitType == 'Reversals'):
            strategy.exit('Exit Long', 'Long', stop=low, qty_percent=100)
            strategy.exit('Exit Add Long', 'Add Long', stop=low, qty_percent=100)
            if exitAlerts:
                alert('Exit Long', alert.freq_once_per_bar)
        if condLong[1] and exitType == 'ATR':
            strategy.exit('Exit Long', 'Long', limit=longTakeProfit, qty_percent=100)
            strategy.exit('Exit Add Long', 'Add Long', limit=longTakeProfit, qty_percent=100)
            if exitAlerts:
                alert('Exit Long', alert.freq_once_per_bar)
        if condLong[1] and (exitType == 'Fast Supertrend' or exitType == 'Slow Supertrend'):
            strategy.exit('Exit Long', 'Long', limit=rangeMiddleValue + rangeMiddleValue - (supertrend1 if exitType == 'Fast Supertrend' else supertrend2), qty_percent=100)
            strategy.exit('Exit Add Long', 'Add Long', limit=rangeMiddleValue + rangeMiddleValue - (supertrend1 if exitType == 'Fast Supertrend' else supertrend2), qty_percent=100)
            if exitAlerts:
                alert('Exit Long', alert.freq_once_per_bar)
    if buy and (not condLong) and showExitShorts and isInsideDateRange:
        if ohlc4 >= diffFromBottom and ohlc4[1] < diffFromBottom[1] and (exitType == 'Reversals'):
            strategy.exit('Exit Short', 'Short', stop=high, qty_percent=100)
            strategy.exit('Exit Add Short', 'Add Short', stop=high, qty_percent=100)
            if exitAlerts:
                alert('Exit Short', alert.freq_once_per_bar)
        if condShort[1] and exitType == 'ATR':
            strategy.exit('Exit Short', 'Short', limit=shortTakeProfit, qty_percent=100)
            strategy.exit('Exit Add Short', 'Add Short', limit=shortTakeProfit, qty_percent=100)
            if exitAlerts:
                alert('Exit Short', alert.freq_once_per_bar)
        if condShort[1] and (exitType == 'Fast Supertrend' or exitType == 'Slow Supertrend'):
            strategy.exit('Exit Short', 'Short', limit=rangeMiddleValue - ((supertrend1 if exitType == 'Fast Supertrend' else supertrend2) - rangeMiddleValue), qty_percent=100)
            strategy.exit('Exit Add Short', 'Add Short', limit=rangeMiddleValue - ((supertrend1 if exitType == 'Fast Supertrend' else supertrend2) - rangeMiddleValue), qty_percent=100)
            if exitAlerts:
                alert('Exit Short', alert.freq_once_per_bar)
    bodyMiddle = plot(bodyMiddleValue, display=display.none)
    upTrend1 = plot(supertrend1 if direction1 < 0 else na, 'Up Trend', color=colorSignal1 if showIndicators else na, style=plot.style_linebr)
    plot(longTakeProfit if direction1 < 0 and direction2 < 0 and (longTakeProfit > high) else na, 'Take Profit Up Trend', color=color.olive if showIndicators else na, style=plot.style_linebr, linewidth=3)
    plot(rangeMiddleValue + rangeMiddleValue - (supertrend1 if exitType == 'Fast Supertrend' else supertrend2), 'Supertrend Long Take Profit', color.new(color.olive, 30) if (exitType == 'Fast Supertrend' or exitType == 'Slow Supertrend') and direction1 < 0 and (direction2 < 0) else na, style=plot.style_linebr)
    downTrend1 = plot(na if direction1 < 0 else supertrend1, 'Down Trend', color=colorSignal2 if showIndicators else na, style=plot.style_linebr)
    upTrend2 = plot(supertrend2 if direction2 < 0 else na, 'Up Trend', color=colorSignal1 if showIndicators else na, style=plot.style_linebr)
    plot(shortTakeProfit if direction1 >= 0 and direction2 >= 0 and (shortTakeProfit < low) else na, 'Take Profit Down Trend', color=color.maroon if showIndicators else na, style=plot.style_linebr, linewidth=3)
    plot(rangeMiddleValue - ((supertrend1 if exitType == 'Fast Supertrend' else supertrend2) - rangeMiddleValue), 'Supertrend Short Take Profit', color.new(color.maroon, 30) if (exitType == 'Fast Supertrend' or exitType == 'Slow Supertrend') and direction1 >= 0 and (direction2 >= 0) else na, style=plot.style_linebr)
    downTrend2 = plot(na if direction2 < 0 else supertrend2, 'Down Trend', color=colorSignal2 if showIndicators else na, style=plot.style_linebr)
    fill(bodyMiddle, upTrend1, color.new(colorSignal1, 95) if showIndicators else na, fillgaps=False)
    fill(bodyMiddle, downTrend1, color.new(colorSignal2, 90) if showIndicators else na, fillgaps=False)
    fill(bodyMiddle, upTrend2, color.new(colorSignal1, 95) if showIndicators else na, fillgaps=False)
    fill(bodyMiddle, downTrend2, color.new(colorSignal2, 90) if showIndicators else na, fillgaps=False)
    plotshape(low < supertrend1 and close > supertrend1 and sell and (not (ohlc4 <= diffFromTop and ohlc4[1] > diffFromTop[1])) and showAddLongs, 'Add Long', shape.cross, location.belowbar, color.new(color.green, 20), 0, 'L', color.new(color.green, 20), False, size.tiny)
    plotshape(high > supertrend1 and close < supertrend1 and buy and (not (ohlc4 >= diffFromBottom and ohlc4[1] < diffFromBottom[1])) and showAddShorts, 'Add Short', shape.cross, location.abovebar, color.new(color.red, 20), 0, 'S', color.new(color.red, 20), False, size.tiny)
    if useStrategy and isInsideDateRange:
        if low < supertrend1 and close > supertrend1 and sell and (not (ohlc4 <= diffFromTop and ohlc4[1] > diffFromTop[1])) and showAddLongs:
            strategy.entry('Add Long', strategy.long)
            if addAlerts:
                alert('Add Long', alert.freq_once_per_bar)
        if high > supertrend1 and close < supertrend1 and buy and (not (ohlc4 >= diffFromBottom and ohlc4[1] < diffFromBottom[1])) and showAddShorts:
            strategy.entry('Add Short', strategy.short)
            if addAlerts:
                alert('Add Short', alert.freq_once_per_bar)
    if condLong and buy:
        buy = False
        sell = True
        strategy.cancel('Exit Short')
        strategy.cancel('Exit Add Short')
    if condShort and sell:
        sell = False
        buy = True
        strategy.cancel('Exit Long')
        strategy.cancel('Exit Add Long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
