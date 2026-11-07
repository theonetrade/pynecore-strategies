"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, bgcolor, close, color, high, input, location, low, na,
    plotshape, script, shape, size, strategy, ta, time, timestamp
)
from pynecore.types import Persistent, Series


@script.strategy('Moon Phases Strategy [LuxAlgo]', overlay=True, process_orders_on_close=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    new=input.time(title='New Moon Reference Date', defval=timestamp('2021-01-13:05:00')),
    buy=input.string('Full Moon', options=('New Moon', 'Full Moon', 'Higher Moon', 'Lower Moon'), inline='buy'),
    sell=input.string('New Moon', options=('New Moon', 'Full Moon', 'Higher Moon', 'Lower Moon'), inline='sell'),
    longcol=input.color(color.new(color.new('#2157F3'), 80), '', inline='buy'),
    shortcol=input.color(color.new(color.new('#FF1100'), 80), '', inline='sell')
):
    n = bar_index
    cycle: float = 2551442876.8992
    day: float = 86400000.0
    diff: Series = (new + time + day * 2) % cycle / cycle
    newmoon = ta.crossover(diff, 0.5)
    fullmoon = diff < diff[1]
    plotshape(low if newmoon else na, 'New Moon', shape.labelup, location.top, na, text='🌑', size=size.tiny)
    plotshape(high if fullmoon else na, 'Full Moon', shape.labeldown, location.bottom, na, text='🌕', size=size.tiny)
    src = close
    long: Persistent[bool] = na(bool)
    short: Persistent[bool] = na(bool)
    if buy == 'New Moon':
        long = newmoon
    elif buy == 'Full Moon':
        long = fullmoon
    elif buy == 'Higher Moon':
        long = ta.valuewhen(newmoon or fullmoon, src, 0) > ta.valuewhen(newmoon or fullmoon, src, 1)
    else:
        long = ta.valuewhen(newmoon or fullmoon, src, 0) < ta.valuewhen(newmoon or fullmoon, src, 1)
    if sell == 'New Moon':
        short = newmoon
    elif sell == 'Full Moon':
        short = fullmoon
    elif sell == 'Higher Moon':
        short = ta.valuewhen(newmoon or fullmoon, src, 0) > ta.valuewhen(newmoon or fullmoon, src, 1)
    else:
        short = ta.valuewhen(newmoon or fullmoon, src, 0) < ta.valuewhen(newmoon or fullmoon, src, 1)
    pos: Persistent[int] = 0
    if long:
        pos = 1
        strategy.close('Short')
        strategy.entry('Long', strategy.long)
    if short:
        pos = -1
        strategy.close('Long')
        strategy.entry('Short', strategy.short)
    bgcolor(longcol if pos == 1 else shortcol)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
