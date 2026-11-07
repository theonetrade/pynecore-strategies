"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barcolor, close, color, high, input, na, plot, script, strategy, ta


@script.strategy('ATR Trailing Stoploss Strategy ', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    Atr=input.int(defval=5, title='Atr Period', minval=1, maxval=500),
    Hhv=input.int(defval=10, title='HHV Period', minval=1, maxval=500),
    Mult=input.float(defval=2.5, title='Multiplier', minval=0.1),
    Barcolor=input(True, title='Barcolor')
):
    Prev = ta.highest(high - Mult * ta.atr(Atr), Hhv)
    ta.barssince(close > ta.highest(high - Mult * ta.atr(Atr), Hhv) and close > close[1])
    cum_1 = ta.cum(1)
    atr_1 = ta.atr(Atr)
    highest_1 = ta.highest(high - Mult * atr_1, Hhv)
    atr_2 = ta.atr(Atr)
    highest_2 = ta.highest(high - Mult * atr_2, Hhv)
    iff_1 = highest_2 if close > highest_1 and close > close[1] else Prev
    TS = close if cum_1 < 16 else iff_1
    iff_2 = color.red if close < TS else color.black
    Color__ren__ = color.green if close > TS else iff_2
    barcolor(Color__ren__ if Barcolor else na)
    plot(TS, color=Color__ren__, linewidth=3, title='ATR Trailing Stoploss')
    Buy = ta.crossover(close, TS)
    Sell = ta.crossunder(close, TS)
    if Buy:
        strategy.entry('Buy', strategy.long, comment='Buy')
    if Sell:
        strategy.entry('Sell', strategy.short, comment='Sell')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
