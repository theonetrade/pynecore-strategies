"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, display, fill, high, input, location, low, math,
    na, nz, ohlc4, plot, plotshape, script, shape, size, strategy, ta, time, timestamp
)
from pynecore.types import Color, Persistent, PersistentSeries, Series


@script.strategy('Chandelier Exit - Strategy', shorttitle='CE-STG', overlay=True, default_qty_type=strategy.cash, default_qty_value=10000, initial_capital=10000, currency=currency.USD, commission_value=0.03, commission_type=strategy.commission.percent, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    length=input(title='ATR Period', defval=22),
    mult=input.float(title='ATR Multiplier', step=0.1, defval=3.0),
    showLabels=input(title='Show Buy/Sell Labels ?', defval=False),
    useClose=input(title='Use Close Price for Extremums ?', defval=True),
    highlightState=input(title='Highlight State ?', defval=True),
    long_short=input.bool(True, 'Long-Short', group='Strategy Settings'),
    start=input.time(timestamp('2019-01-01'), 'Date', group='Strategy Settings'),
    finish=input.time(timestamp('2025-01-01'), 'Date', group='Strategy Settings'),
    slRatio=input.float(5, 'Manuel Stop Loss Ratio', minval=0, group='Strategy Settings'),
    tpRatio=input.float(20, 'Take Profit Ratio', minval=0, group='Strategy Settings'),
    tsStartRatio=input.float(10, 'Trailing Stop Start Ratio', minval=0, group='Strategy Settings'),
    tsRatio=input.float(5, 'Trailing Stop Ratio', minval=1, group='Strategy Settings')
):
    atr = mult * ta.atr(length)
    longStop: Series = (ta.highest(close, length) if useClose else ta.highest(length)) - atr
    longStopPrev = nz(longStop[1], longStop)
    longStop = math.max(longStop, longStopPrev) if close[1] > longStopPrev else longStop
    shortStop: Series = (ta.lowest(close, length) if useClose else ta.lowest(length)) + atr
    shortStopPrev = nz(shortStop[1], shortStop)
    shortStop = math.min(shortStop, shortStopPrev) if close[1] < shortStopPrev else shortStop
    dir: PersistentSeries[int] = 1
    dir = 1 if close > shortStopPrev else -1 if close < longStopPrev else dir
    longColor: Persistent[Color] = color.green
    shortColor: Persistent[Color] = color.red
    longStopPlot = plot(longStop if dir == 1 else na, title='Long Stop', style=plot.style_linebr, linewidth=2, color=longColor)
    buySignal = dir == 1 and dir[1] == -1
    plotshape(longStop if buySignal else na, title='Long Stop Start', location=location.absolute, style=shape.circle, size=size.tiny, color=longColor)
    plotshape(longStop if buySignal and showLabels else na, title='Buy Label', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=longColor, textcolor=color.new(color.white, 0))
    shortStopPlot = plot(na if dir == 1 else shortStop, title='Short Stop', style=plot.style_linebr, linewidth=2, color=shortColor)
    sellSignal = dir == -1 and dir[1] == 1
    plotshape(shortStop if sellSignal else na, title='Short Stop Start', location=location.absolute, style=shape.circle, size=size.tiny, color=shortColor)
    plotshape(shortStop if sellSignal and showLabels else na, title='Sell Label', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=shortColor, textcolor=color.new(color.white, 0))
    midPricePlot = plot(ohlc4, title='', style=plot.style_circles, linewidth=math.max(1, 0), display=display.none, editable=False)
    longFillColor = (longColor if dir == 1 else na) if highlightState else na
    shortFillColor = (shortColor if dir == -1 else na) if highlightState else na
    fill(midPricePlot, longStopPlot, title='Long State Filling', color=longFillColor)
    fill(midPricePlot, shortStopPlot, title='Short State Filling', color=shortFillColor)
    def window():
        return True if time >= start and time <= finish else False

    lastBuyPrice = strategy.position_avg_price
    diffHiPriceRatio = (high - lastBuyPrice) / lastBuyPrice * 100
    diffLoPriceRatio = (close - lastBuyPrice) / lastBuyPrice * 100
    posHiRatio: Series[float] = 0.0
    posHiRatio = (diffHiPriceRatio if diffHiPriceRatio > posHiRatio[1] else posHiRatio[1]) if strategy.position_size > 0 else 0
    s_diffHiPriceRatio = (low - lastBuyPrice) / lastBuyPrice * 100
    s_diffLoPriceRatio = (close - lastBuyPrice) / lastBuyPrice * 100
    s_posHiRatio: Series[float] = 0.0
    s_posHiRatio = (s_diffLoPriceRatio if s_diffLoPriceRatio < s_posHiRatio[1] else s_posHiRatio[1]) if strategy.position_size < 0 else 0
    if window() and buySignal:
        strategy.entry('LONG', strategy.long)
    if window() and sellSignal:
        strategy.close('LONG')
    if diffLoPriceRatio < slRatio * -1:
        strategy.close('LONG', comment='STOP-LONG')
    if diffHiPriceRatio > tpRatio:
        strategy.close('LONG', comment='TAKE-PROFIT-LONG')
    if posHiRatio[1] > tsStartRatio and posHiRatio[1] - diffHiPriceRatio > tsRatio:
        strategy.close('LONG', comment='TRAILING-STOP-LONG')
    if long_short:
        if window() and sellSignal:
            strategy.entry('SHORT', strategy.short)
        if window() and buySignal:
            strategy.close('SHORT')
        if s_diffLoPriceRatio > slRatio:
            strategy.close('SHORT', comment='STOP-SHORT')
        if s_diffHiPriceRatio < tpRatio * -1:
            strategy.close('SHORT', comment='TAKE-PROFIT-SHORT')
        if s_posHiRatio[1] * -1 > tsStartRatio and (s_posHiRatio[1] - s_diffLoPriceRatio) * -1 > tsRatio:
            strategy.close('SHORT', comment='TRAILING-STOP-SHORT')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
