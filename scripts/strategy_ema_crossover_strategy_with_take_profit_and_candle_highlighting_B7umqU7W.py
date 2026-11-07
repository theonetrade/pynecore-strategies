"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bgcolor, close, color, high, input, location, low, na, plot, plotshape,
    script, shape, strategy, ta
)
from pynecore.types import Persistent


@script.strategy('EMA Crossover Strategy with Take Profit and Candle Highlighting', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    tp1_multiplier=input.float(0.5, title='TP1 Multiplier', minval=0.1, maxval=5.0, step=0.1),
    tp2_multiplier=input.float(1.0, title='TP2 Multiplier', minval=0.1, maxval=5.0, step=0.1),
    tp3_multiplier=input.float(1.5, title='TP3 Multiplier', minval=0.1, maxval=5.0, step=0.1),
    tp4_multiplier=input.float(2.0, title='TP4 Multiplier', minval=0.1, maxval=5.0, step=0.1)
):
    ema200 = ta.ema(close, 200)
    ema50 = ta.ema(close, 50)
    ema20 = ta.ema(close, 20)
    plot(ema200, color=color.new('#C204898E'), title='EMA 200', linewidth=2)
    plot(ema50, color=color.blue, title='EMA 50', linewidth=2)
    plot(ema20, color=color.orange, title='EMA 20', linewidth=2)
    buySignal = ta.crossover(ema20, ema50)
    sellSignal = ta.crossunder(ema20, ema50)
    takeProfit1: Persistent[float] = na(float)
    takeProfit2: Persistent[float] = na(float)
    takeProfit3: Persistent[float] = na(float)
    takeProfit4: Persistent[float] = na(float)
    if buySignal:
        takeProfit1 = high + (high - low) * tp1_multiplier
        takeProfit2 = high + (high - low) * tp2_multiplier
        takeProfit3 = high + (high - low) * tp3_multiplier
        takeProfit4 = high + (high - low) * tp4_multiplier
    if sellSignal:
        takeProfit1 = low - (high - low) * tp1_multiplier
        takeProfit2 = low - (high - low) * tp2_multiplier
        takeProfit3 = low - (high - low) * tp3_multiplier
        takeProfit4 = low - (high - low) * tp4_multiplier
    plot(takeProfit1, color=color.new('#B4B4B8'), style=plot.style_line, linewidth=1, title='Take Profit 1')
    plot(takeProfit2, color=color.new('#B4B4B8'), style=plot.style_line, linewidth=1, title='Take Profit 2')
    plot(takeProfit3, color=color.new('#B4B4B8'), style=plot.style_line, linewidth=1, title='Take Profit 3')
    plot(takeProfit4, color=color.new('#B4B4B8'), style=plot.style_line, linewidth=1, title='Take Profit 4')
    plotshape(series=buySignal, location=location.belowbar, color=color.green, style=shape.labelup, title='Buy Signal', text='BUY')
    plotshape(series=sellSignal, location=location.abovebar, color=color.red, style=shape.labeldown, title='Sell Signal', text='SELL')
    uptrend = ta.crossover(ema20, ema50)
    downtrend = ta.crossunder(ema20, ema50)
    bgcolor(color=color.new(color.green, 80) if ema20 > ema50 else color.new(color.red, 80) if ema20 < ema50 else na)
    if buySignal:
        strategy.entry('Buy', strategy.long)
    if sellSignal:
        strategy.entry('Sell', strategy.short)
    strategy.exit('Take Profit 1', 'Buy', limit=takeProfit1)
    strategy.exit('Take Profit 2', 'Buy', limit=takeProfit2)
    strategy.exit('Take Profit 3', 'Buy', limit=takeProfit3)
    strategy.exit('Take Profit 4', 'Buy', limit=takeProfit4)
    strategy.exit('Take Profit 1', 'Sell', limit=takeProfit1)
    strategy.exit('Take Profit 2', 'Sell', limit=takeProfit2)
    strategy.exit('Take Profit 3', 'Sell', limit=takeProfit3)
    strategy.exit('Take Profit 4', 'Sell', limit=takeProfit4)
    stopLoss: float = 0.03
    strategy.exit('Stop Loss', 'Buy', stop=close * (1 - stopLoss))
    strategy.exit('Stop Loss', 'Sell', stop=close * (1 + stopLoss))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
