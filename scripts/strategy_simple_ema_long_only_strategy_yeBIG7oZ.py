"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, fill, input, plot, script, strategy, ta


@script.strategy('EMA Long Only Strategy', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    len=input.int(21, minval=1, title='Length'),
    mul=input.float(1, minval=0, title='Length')
):
    price = ta.sma(close, 2)
    average = ta.ema(close, len)
    diff = ta.atr(len) * mul
    bull_level = average + diff
    bear_level = average - diff
    bull_cross = ta.crossover(price, bull_level)
    bear_cross = ta.crossover(bear_level, price)
    if bull_cross:
        strategy.entry('Buy', strategy.long)
    if bear_cross:
        strategy.close('Buy')
    plot(price, title='price', color=color.new(color.black, 50), linewidth=2)
    a0 = plot(average, title='average', color=color.new(color.red, 50), linewidth=1)
    a1 = plot(bull_level, title='bull', color=color.new(color.green, 50), linewidth=1)
    a2 = plot(bear_level, title='bear', color=color.new(color.red, 50), linewidth=1)
    fill(a0, a1, color=color.new(color.green, 97))
    fill(a0, a2, color=color.new(color.red, 97))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
