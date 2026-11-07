"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import close, input, script, strategy, ta
from pynecore.types import Series


@script.strategy(title='HIGHER HIGH LOWER LOW STRATEGY', shorttitle='HH LL STRATEGY', overlay=True, calc_on_order_fills=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, currency='USD', default_qty_value=100, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    price: Series[float] = input(close),
    LookBack=input(41),
    length=input(10),
    length2=input(1)
):
    Highest: Series = ta.highest(LookBack)
    Lowest: Series = ta.lowest(LookBack)
    long = price > Highest[1]
    short = price < Lowest[1]
    High_Guard: Series = ta.highest(length)
    Low_Guard: Series = ta.lowest(length)
    long1 = long == cast_bool(1) and Highest[1] > High_Guard[length2]
    short1 = short == cast_bool(1) and Lowest[1] < Low_Guard[length2]
    if long1:
        strategy.entry('Long', strategy.long)
    if short1:
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
