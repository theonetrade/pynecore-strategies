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
from pynecore.types import Series


@script.strategy('KPL Swing Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    no=input(20, title='Length'),
    Barcolor=input(True, title='Barcolor'),
    Bgcolor=input(True, title='Bgcolor')
):
    res: Series = ta.highest(high, no)
    sup: Series = ta.lowest(low, no)
    iff_1 = -1 if close < sup[1] else 0
    avd = 1 if close > res[1] else iff_1
    avn = ta.valuewhen(avd != 0, avd, 0)
    tsl = sup if avn == 1 else res
    lowest_1 = ta.lowest(low, no / 2)
    highest_1 = ta.highest(lowest_1, no / 2)
    highest_2 = ta.highest(high, no / 2)
    lowest_2 = ta.lowest(highest_2, no / 2)
    sl = highest_1 if close > tsl else lowest_2
    Buy = ta.crossover(close, tsl)
    Sell = ta.crossover(tsl, close)
    iff_2 = color.yellow if tsl < close else color.red
    colors = color.green if close > tsl else iff_2
    barcolor(colors if Barcolor else na)
    bgcolor(colors if Bgcolor else na)
    plot(tsl, color=colors)
    plot(sl, color=color.new(color.white, 0), title='Stoploss')
    if ta.crossover(close, tsl):
        strategy.entry('Long', strategy.long, comment='Long')
    if ta.crossunder(close, tsl):
        strategy.entry('Short', strategy.short, comment='Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)