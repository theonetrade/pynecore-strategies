"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, bgcolor, close, color, high, input, low, na, plot, script,
    strategy, ta
)


@script.strategy('Support Resistance Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    LB=input(10, title='length'),
    Barcolor=input(True, title='Barcolor'),
    Bgcolor=input(True, title='Bgcolor')
):
    R = ta.valuewhen(ta.cross(ta.sma(close, LB), close), ta.highest(high, LB), 1)
    S = ta.valuewhen(ta.cross(close, ta.sma(close, LB)), ta.lowest(low, LB), 1)
    plot(R, title='Resistance', color=color.new(color.new('#008000'), 0))
    plot(S, title='Support', color=color.new(color.new('#FF0000'), 0))
    iff_1 = color.new('#FFFF00') if S < close else color.new('#FF0000')
    colors = color.new('#008000') if close > R else iff_1
    barcolor(colors if Barcolor else na)
    bgcolor(colors if Bgcolor else na)
    if ta.crossover(close, R):
        strategy.entry('Long', strategy.long, comment='Long')
    if ta.crossunder(close, S):
        strategy.entry('Short', strategy.short, comment='Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
