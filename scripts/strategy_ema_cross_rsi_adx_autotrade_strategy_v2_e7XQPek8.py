"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, location, low, na, plot, plotarrow, plotshape,
    script, shape, size, strategy, ta
)
from pynecore.types import Persistent


@script.strategy("EMA Cross + RSI + ADX - Strategy V2", overlay=True, initial_capital=1000, default_qty_value=10, default_qty_type=strategy.fixed, commission_type=strategy.commission.percent, commission_value=0.075)
def main(
    ema_fast=input.int(9, "Fast EMA", minval=1),
    ema_slow=input.int(21, "Slow EMA", minval=1),
    rsi_length=input.int(14, "RSI Length", minval=1),
    rsi_long=input.int(55, "RSI Long Threshold", minval=1, maxval=100),
    rsi_short=input.int(40, "RSI Short Threshold", minval=1, maxval=100),
    sl_percent=input.float(2.0, "Stop Loss %", minval=0.1, maxval=10),
    use_adx=input.bool(True, "Use ADX Filter"),
    adx_length=input.int(14, "ADX Length", minval=1),
    adx_threshold=input.float(0, "ADX Threshold", minval=0, maxval=100)
):
    ema9 = ta.ema(close, ema_fast)
    ema21 = ta.ema(close, ema_slow)
    rsi = ta.rsi(close, rsi_length)

    diPlus, diMinus, adx = ta.dmi(adx_length, adx_length)

    bullCross = ta.crossover(ema9, ema21)
    bearCross = ta.crossunder(ema9, ema21)

    adx_ok = adx > adx_threshold if use_adx else True
    longCondition = bullCross and rsi > rsi_long and adx_ok
    shortCondition = bearCross and rsi < rsi_short and adx_ok

    longSL: Persistent[float] = na(float)
    shortSL: Persistent[float] = na(float)

    if longCondition:
        longSL = close * (1 - sl_percent / 100)

    if shortCondition:
        shortSL = close * (1 + sl_percent / 100)

    closeLongCondition = bearCross and strategy.position_size > 0
    closeShortCondition = bullCross and strategy.position_size < 0

    longSLHit = strategy.position_size > 0 and (not na(longSL)) and (low <= longSL)
    shortSLHit = strategy.position_size < 0 and (not na(shortSL)) and (high >= shortSL)

    if longCondition:
        strategy.entry('LONG', strategy.long, alert_message='Entry Buy')

    if shortCondition:
        strategy.entry('SHORT', strategy.short, alert_message='Entry Sell')

    if closeLongCondition:
        strategy.close('LONG', comment='Opposite Cross', alert_message='Close Long')
        longSL = na

    if closeShortCondition:
        strategy.close('SHORT', comment='Opposite Cross', alert_message='Close Short')
        shortSL = na

    if longSLHit:
        strategy.close('LONG', comment='SL Hit', alert_message='SL Hit Long')
        longSL = na

    if shortSLHit:
        strategy.close('SHORT', comment='SL Hit', alert_message='SL Hit Short')
        shortSL = na

    plot(ema9, 'EMA 9', color.blue, 2)
    plot(ema21, 'EMA 21', color.red, 2)
    plot(longSL if strategy.position_size > 0 else na, 'Long SL', color.orange, 2, plot.style_linebr)
    plot(shortSL if strategy.position_size < 0 else na, 'Short SL', color.orange, 2, plot.style_linebr)

    plotshape(longCondition, 'Long Entry', shape.triangleup, location.belowbar, color.new(color.green, 0), size=size.large)
    plotshape(shortCondition, 'Short Entry', shape.triangledown, location.abovebar, color.new(color.red, 0), size=size.large)

    plotarrow(-1 if closeLongCondition else na, 'Close Long', color.red, minheight=15, maxheight=15)
    plotarrow(1 if closeShortCondition else na, 'Close Short', color.green, minheight=15, maxheight=15)

    plotshape(longSLHit, 'Long SL Hit', shape.xcross, location.belowbar, color.new(color.orange, 0), size=size.normal)
    plotshape(shortSLHit, 'Short SL Hit', shape.xcross, location.abovebar, color.new(color.orange, 0), size=size.normal)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
