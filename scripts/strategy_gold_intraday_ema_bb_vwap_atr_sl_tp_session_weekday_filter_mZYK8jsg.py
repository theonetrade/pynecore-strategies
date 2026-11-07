"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, dayofweek, hour, input, location, na, plot, plotshape,
    script, shape, size, strategy, ta, time
)


@script.strategy("Gold Intraday EMA/BB/VWAP + ATR SL/TP + Session/Weekday Filter", overlay=True, margin_long=100, margin_short=100, default_qty_type=strategy.percent_of_equity, default_qty_value=10)
def main(
    emaFastLen=input.int(9, "Fast EMA Length"),
    emaSlowLen=input.int(21, "Slow EMA Length"),
    bbLen=input.int(20, "BB Mid (SMA) Length"),
    atrLen=input.int(14, "ATR Length"),
    atrSLmult=input.float(1.5, "ATR Stop Multiplier", minval=0.5, step=0.1),
    atrTPmult=input.float(2.0, "ATR Take Profit Multiplier", minval=0.5, step=0.1),
    sessionAsia=input.bool(True, "Trade Asian Session (00:00–08:00 UTC)"),
    sessionLondon=input.bool(True, "Trade London Session (08:00–16:00 UTC)"),
    sessionNY=input.bool(False, "Trade New York Session (16:00–23:59 UTC)"),
    tradeMonday=input.bool(True, "Trade Monday"),
    tradeTuesday=input.bool(True, "Trade Tuesday"),
    tradeWednesday=input.bool(True, "Trade Wednesday"),
    tradeThursday=input.bool(True, "Trade Thursday"),
    tradeFriday=input.bool(False, "Trade Friday")
):
    emaFast = ta.ema(close, emaFastLen)
    emaSlow = ta.ema(close, emaSlowLen)
    bbMid = ta.sma(close, bbLen)
    vwapVal = ta.vwap(close)
    atrVal = ta.atr(atrLen)

    atrStopBuy = close - atrSLmult * atrVal
    atrStopSell = close + atrSLmult * atrVal
    atrTPBuy = close + atrTPmult * atrVal
    atrTPSell = close - atrTPmult * atrVal

    bullCross = ta.crossover(emaFast, bbMid)
    bearCross = ta.crossunder(emaFast, bbMid)

    buySignal = bullCross and close > emaSlow and (close > vwapVal)
    sellSignal = bearCross and close < emaSlow and (close < vwapVal)

    hourUTC = hour(time, 'UTC')
    inAsia = sessionAsia and hourUTC >= 0 and (hourUTC < 8)
    inLondon = sessionLondon and hourUTC >= 8 and (hourUTC < 16)
    inNY = sessionNY and hourUTC >= 16 and (hourUTC < 24)
    sessionAllowed = inAsia or inLondon or inNY

    dayOfWeek = dayofweek(time)
    weekdayAllowed = dayOfWeek == dayofweek.monday and tradeMonday or (dayOfWeek == dayofweek.tuesday and tradeTuesday) or (dayOfWeek == dayofweek.wednesday and tradeWednesday) or (dayOfWeek == dayofweek.thursday and tradeThursday) or (dayOfWeek == dayofweek.friday and tradeFriday)

    tradeAllowed = sessionAllowed and weekdayAllowed

    if buySignal and tradeAllowed:
        strategy.entry('BUY', strategy.long)
        strategy.exit('BUY Exit', 'BUY', stop=atrStopBuy, limit=atrTPBuy)

    if sellSignal and tradeAllowed:
        strategy.entry('SELL', strategy.short)
        strategy.exit('SELL Exit', 'SELL', stop=atrStopSell, limit=atrTPSell)

    plot(emaFast, 'EMA Fast', color=color.blue)
    plot(emaSlow, 'EMA Slow', color=color.purple)
    plot(bbMid, 'BB Mid', color=color.orange)
    plot(vwapVal, 'VWAP', color=color.aqua)

    plot(atrStopBuy if buySignal else na, 'ATR Stop Buy', color=color.red, style=plot.style_linebr)
    plot(atrTPBuy if buySignal else na, 'ATR TP Buy', color=color.green, style=plot.style_linebr)
    plot(atrStopSell if sellSignal else na, 'ATR Stop Sell', color=color.red, style=plot.style_linebr)
    plot(atrTPSell if sellSignal else na, 'ATR TP Sell', color=color.green, style=plot.style_linebr)

    plotshape(buySignal and tradeAllowed, title='Buy Signal', text='BUY', style=shape.labelup, location=location.belowbar, color=color.green, size=size.small)
    plotshape(sellSignal and tradeAllowed, title='Sell Signal', text='SELL', style=shape.labeldown, location=location.abovebar, color=color.red, size=size.small)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
