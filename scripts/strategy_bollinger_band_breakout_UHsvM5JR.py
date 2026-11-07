"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, fill, input, plot, script, strategy, ta


@script.strategy(title='Bollinger Band Breakout', shorttitle='BB-BO', default_qty_type=strategy.percent_of_equity, default_qty_value=100, overlay=True, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    length=input.int(20, minval=1, title='Period'),
    mult=input.float(1.5, minval=0.001, maxval=50, title='Standard Deviation'),
    exit=input.int(1, minval=1, maxval=2, title='Exit Option')
):
    source = close
    basis = ta.sma(source, length)
    dev = mult * ta.stdev(source, length)
    upper = basis + dev
    lower = basis - dev
    if ta.crossover(source, upper):
        strategy.entry('Long', strategy.long)
    if exit == 1:
        if ta.crossunder(source, lower):
            strategy.close('Long')
    if exit == 2:
        if ta.crossunder(source, basis):
            strategy.close('Long')
    plot(basis, color=color.new(color.red, 0), title='SMA')
    p1 = plot(upper, color=color.new(color.blue, 0), title='UB')
    p2 = plot(lower, color=color.new(color.blue, 0), title='LB')
    fill(p1, p2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
