"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barcolor, close, color, high, input, low, nz, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy('Highest High and Lowest Low Channel Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    length=input(20),
    reverse=input(False, title='Trade reverse')
):
    hh: Series = ta.highest(high, length)
    ll: Series = ta.lowest(low, length)
    pos: Series[float] = 0.0
    iff_1 = -1 if close < ll[1] else nz(pos[1], 0)
    pos = 1 if close > hh[1] else iff_1
    iff_2 = 1 if reverse and pos == -1 else pos
    possig = -1 if reverse and pos == 1 else iff_2
    if possig == 1:
        strategy.entry('Long', strategy.long)
    if possig == -1:
        strategy.entry('Short', strategy.short)
    barcolor(color.red if possig == -1 else color.green if possig == 1 else color.blue)
    plot(hh[1], color=color.new(color.green, 0), title='HH', linewidth=2)
    plot(ll[1], color=color.new(color.red, 0), title='LL', linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
