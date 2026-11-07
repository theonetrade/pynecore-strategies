"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, fill, input, math, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy('Donchain BO', shorttitle='DBO', default_qty_type=strategy.percent_of_equity, default_qty_value=100, overlay=True, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    length=input.int(20, minval=1),
    exit=input.int(1, minval=1, maxval=2, title='Exit Option')
):
    lower: Series = ta.lowest(length)
    upper: Series = ta.highest(length)
    basis: Series = math.avg(upper, lower)
    l = plot(lower, color=color.new(color.blue, 0))
    u = plot(upper, color=color.new(color.blue, 0))
    plot(basis, color=color.new(color.orange, 0))
    fill(u, l, color=color.new(color.blue, 90))
    longCondition = ta.crossover(close, upper[1])
    if longCondition:
        strategy.entry('Long', strategy.long)
    if exit == 1:
        if ta.crossunder(close, lower[1]):
            strategy.close('Long')
    if exit == 2:
        if ta.crossunder(close, basis[1]):
            strategy.close('Long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
