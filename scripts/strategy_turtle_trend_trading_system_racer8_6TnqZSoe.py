"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, high, input, low, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy('Turtle System', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    n=input(55, 'Entry Length'),
    e=input(20, 'Exit Length')
):
    HI: Series = ta.highest(n)
    LO: Series = ta.lowest(n)
    hi: Series = ta.highest(e)
    lo: Series = ta.lowest(e)
    if close > HI[1]:
        strategy.entry('Buy', strategy.long)
    if close < LO[1]:
        strategy.entry('Sell', strategy.short)
    if low < lo[1]:
        strategy.close('Buy')
    if high > hi[1]:
        strategy.close('Sell')
    plot(HI, color=color.new(color.lime, 0))
    plot(LO, color=color.new(color.red, 0))
    plot(hi, color=color.new(color.blue, 0))
    plot(lo, color=color.new(color.maroon, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
