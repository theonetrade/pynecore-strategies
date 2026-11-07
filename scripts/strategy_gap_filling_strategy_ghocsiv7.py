"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    close, color, high, input, low, math, open, plot, script, strategy, ta,
    time
)
from pynecore.types import Series


@script.strategy('Gap Filling Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    invert=input(False),
    clw=input.string('New Session', 'Close When:', options=('New Session', 'New Gap', 'Reverse Position'))
):
    ses = ta.change(time('D'))
    o: Series = open
    c: Series = close
    upgap = o > high[1] and math.min(c, o) > math.max(c[1], o[1])
    dngap = o < low[1] and math.min(c[1], o[1]) > math.max(c, o)
    val = math.max(c[1], o[1]) if upgap else math.min(c[1], o[1])
    lim = ta.valuewhen(cast_bool(ses) and (upgap or dngap), val, 0)
    if ses if clw == 'New Session' else ses and (upgap or dngap) if clw == 'New Gap' else False:
        strategy.close_all()
    if invert:
        if cast_bool(ses) and upgap:
            strategy.entry('Buy', strategy.long)
        if cast_bool(ses) and dngap:
            strategy.entry('Sell', strategy.short)
    else:
        if cast_bool(ses) and dngap:
            strategy.entry('Buy', strategy.long)
        if cast_bool(ses) and upgap:
            strategy.entry('Sell', strategy.short)
    if invert:
        strategy.exit('ExitBuy', 'Buy', stop=lim)
        strategy.exit('ExitSell', 'Sell', stop=lim)
    else:
        strategy.exit('ExitBuy', 'Buy', limit=lim)
        strategy.exit('ExitSell', 'Sell', limit=lim)
    plot(lim, 'Limit/Stop', color.new(color.new('#FF1100'), 0), 2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
