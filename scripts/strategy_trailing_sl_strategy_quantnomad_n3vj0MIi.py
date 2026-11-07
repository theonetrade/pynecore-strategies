"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, low, math, nz, plot, script, strategy, ta,
    time, timestamp
)
from pynecore.types import Series


@script.strategy(title='Trailing SL Strategy [QuantNomad]', shorttitle='TrailingSL [QN]', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=50, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    sl_type=input.string('%', options=('%', 'ATR', 'Absolute')),
    sl_perc=input.float(4, title='% SL'),
    atr_length=input(10, title='ATR Length'),
    atr_mult=input.float(2, title='ATR Mult'),
    sl_absol=input.float(10, title='Absolute SL'),
    fromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    fromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    fromYear=input.int(defval=2016, title='From Year', minval=1970),
    toDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    toMonth=input.int(defval=1, title='To Month', minval=1, maxval=12),
    toYear=input.int(defval=2100, title='To Year', minval=1970)
):
    startDate = timestamp(fromYear, fromMonth, fromDay, 0, 0)
    finishDate = timestamp(toYear, toMonth, toDay, 0, 0)
    time_cond = time >= startDate and time <= finishDate
    sl_val = atr_mult * ta.atr(atr_length) if sl_type == 'ATR' else sl_absol if sl_type == 'Absolute' else close * sl_perc / 100
    pos: Series[int] = 0
    trailing_sl: Series[float] = 0.0
    long_signal = nz(pos[1]) != 1 and high > nz(trailing_sl[1])
    short_signal = nz(pos[1]) != -1 and low < nz(trailing_sl[1])
    trailing_sl = high + sl_val if short_signal else low - sl_val if long_signal else math.max(low - sl_val, nz(trailing_sl[1])) if nz(pos[1]) == 1 else math.min(high + sl_val, nz(trailing_sl[1])) if nz(pos[1]) == -1 else nz(trailing_sl[1])
    pos = 1 if long_signal else -1 if short_signal else nz(pos[1])
    plot(trailing_sl, linewidth=2, color=color.green if pos == 1 else color.red)
    if time_cond and pos != 1:
        strategy.entry('long', strategy.long, stop=trailing_sl)
    if time_cond and pos != -1:
        strategy.entry('short', strategy.short, stop=trailing_sl)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
