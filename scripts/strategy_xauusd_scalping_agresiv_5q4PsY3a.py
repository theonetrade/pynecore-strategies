"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, input, location, plot, plotshape, script, shape, strategy,
    syminfo, ta
)


@script.strategy('XAUUSD Scalping V2 AGRESIV', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=10, margin_long=0, margin_short=0, initial_capital=1000000, close_by_id=True)
def main(
    emaFastLen=input.int(5, 'EMA Rapid'),
    emaSlowLen=input.int(13, 'EMA Lent'),
    rsiLen=input.int(7, 'RSI Rapid'),
    atrLen=input.int(14, 'ATR Length'),
    tpATR=input.float(1.2, 'Take Profit (ATR multiplu)'),
    slATR=input.float(0.8, 'Stop Loss (ATR multiplu)'),
    trailATR=input.float(0.5, 'Trailing Stop (ATR multiplu)'),
    minVolatility=input.float(0.5, 'Filtru volatilitate (ATR minim)')
):
    emaFast = ta.ema(close, emaFastLen)
    emaSlow = ta.ema(close, emaSlowLen)
    rsi = ta.rsi(close, rsiLen)
    atr = ta.atr(atrLen)
    volatilityOK = atr > minVolatility
    longCondition = ta.crossover(emaFast, emaSlow) and rsi > 55 and volatilityOK
    shortCondition = ta.crossunder(emaFast, emaSlow) and rsi < 45 and volatilityOK
    if longCondition:
        entryPrice = close
        takeProfit = entryPrice + atr * tpATR
        stopLoss = entryPrice - atr * slATR
        strategy.entry('BUY', strategy.long)
        strategy.exit('TP/SL BUY', from_entry='BUY', limit=takeProfit, stop=stopLoss, trail_points=atr * trailATR / syminfo.mintick)
    if shortCondition:
        entryPrice = close
        takeProfit = entryPrice - atr * tpATR
        stopLoss = entryPrice + atr * slATR
        strategy.entry('SELL', strategy.short)
        strategy.exit('TP/SL SELL', from_entry='SELL', limit=takeProfit, stop=stopLoss, trail_points=atr * trailATR / syminfo.mintick)
    plot(emaFast, color=color.green)
    plot(emaSlow, color=color.red)
    plotshape(longCondition, location=location.belowbar, color=color.lime, style=shape.labelup, text='BUY')
    plotshape(shortCondition, location=location.abovebar, color=color.red, style=shape.labeldown, text='SELL')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
