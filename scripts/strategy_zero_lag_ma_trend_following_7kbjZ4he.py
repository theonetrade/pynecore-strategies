"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barstate, box, close, color, high, input, location, low, na,
    plot, plotshape, script, shape, size, strategy, ta
)
from pynecore.types import Box, Persistent


@script.strategy('Zero-Lag MA Trend Following', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=10, margin_long=0, margin_short=0, initial_capital=1000000, close_by_id=True)
def main(
    length=input.int(34, title='Length'),
    rr_ratio=input.float(2.0, title='Risk-Reward Ratio', step=0.1),
    up=input.color(color.green, 'Up Label Color'),
    dn=input.color(color.red, 'Down Label Color')
):
    box1: Persistent[Box] = na(Box)
    atr = ta.atr(14)
    emaValue = ta.ema(close, length)
    correction = close + close - emaValue
    zlma = ta.ema(correction, length)
    signalUp = ta.crossover(zlma, emaValue)
    signalDn = ta.crossunder(zlma, emaValue)
    longConditionMet: Persistent[bool] = False
    shortConditionMet: Persistent[bool] = False
    if signalUp:
        box1 = box.new(bar_index, zlma, bar_index, zlma - atr, bgcolor=color.new(up, 90))
        longConditionMet = True
    if signalDn:
        box1 = box.new(bar_index, zlma + atr, bar_index, zlma, bgcolor=color.new(dn, 90))
        shortConditionMet = True
    if na(box1) == False:
        box.set_right(box1, bar_index + 4)
    crossover_1 = ta.crossover(low, box.get_top(box1))
    if longConditionMet and crossover_1 and barstate.isconfirmed:
        sl = box.get_bottom(box1)
        tp = close + (close - sl) * rr_ratio
        strategy.entry('Long', strategy.long)
        strategy.exit('TP/SL Long', from_entry='Long', limit=tp, stop=sl)
        longConditionMet = False
    crossunder_1 = ta.crossunder(high, box.get_bottom(box1))
    if shortConditionMet and crossunder_1 and barstate.isconfirmed:
        sl = box.get_top(box1)
        tp = close - (sl - close) * rr_ratio
        strategy.entry('Short', strategy.short)
        strategy.exit('TP/SL Short', from_entry='Short', limit=tp, stop=sl)
        shortConditionMet = False
    plot(zlma, color=color.new(color.blue, 0), linewidth=2)
    plot(emaValue, color=color.new(color.orange, 0), linewidth=2)
    plotshape(series=signalUp, style=shape.diamond, location=location.abovebar, color=color.new(color.green, 50), size=size.small, title='Bullish Signal')
    plotshape(series=signalDn, style=shape.diamond, location=location.belowbar, color=color.new(color.red, 50), size=size.small, title='Bearish Signal')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
