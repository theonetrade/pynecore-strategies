"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, color, high, input, line, location, low, na, plotshape,
    script, shape, strategy, ta
)
from pynecore.types import Line, Persistent


@script.strategy('Double Bottom and Top Hunter', overlay=True, default_qty_type=strategy.fixed, default_qty_value=1000, margin_long=0, margin_short=0, initial_capital=1000000, close_by_id=True)
def main(
    length=input.int(100, title='Dönem Uzunluğu'),
    lookback=input.int(100, title='Geriye Dönük Kontrol Süresi')
):
    low1 = ta.lowest(low, length)
    high1 = ta.highest(high, length)
    low2 = ta.valuewhen(low == low1, low, 1)
    high2 = ta.valuewhen(high == high1, high, 1)
    lowest_1 = ta.lowest(low, lookback)
    doubleBottom = low == low1 and lowest_1 == low1 and (low == low2)
    highest_1 = ta.highest(high, lookback)
    doubleTop = high == high1 and highest_1 == high1 and (high == high2)
    longCondition = doubleBottom
    shortCondition = doubleTop
    closeLongCondition = ta.highest(high, length) > high1 and low < low1
    closeShortCondition = ta.lowest(low, length) < low1 and high > high1
    if longCondition:
        strategy.entry('Long', strategy.long, qty=100)
    if shortCondition:
        strategy.entry('Short', strategy.short, qty=100)
    if closeLongCondition:
        strategy.close('Long')
    if closeShortCondition:
        strategy.close('Short')
    plotshape(series=longCondition, title='İkili Dip Bulundu', location=location.belowbar, color=color.green, style=shape.labelup, text='LONG')
    plotshape(series=shortCondition, title='İkili Tepe Bulundu', location=location.abovebar, color=color.red, style=shape.labeldown, text='SHORT')
    zigzagLine: Persistent[Line] = na(Line)
    if doubleBottom or doubleTop:
        zigzagLine = line.new(x1=bar_index[1], y1=na, x2=bar_index, y2=low if doubleBottom else high, color=color.green if doubleBottom else color.red, width=2)
    line.set_xy1(zigzagLine, bar_index[1], na)
    line.set_xy2(zigzagLine, bar_index, low if doubleBottom else high)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
