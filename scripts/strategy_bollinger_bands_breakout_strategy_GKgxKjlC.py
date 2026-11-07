"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    barcolor, close, color, currency, display, fill, input, na, plot, script,
    strategy, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy(shorttitle='BB Breakout Strategy', title='Bollinger Bands Filter', overlay=True, pyramiding=1, currency=currency.NONE, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    src: Series[float] = input(close, title='Source'),
    length=input.int(55, minval=1, title='SMA length'),
    mult=input.float(1.0, minval=0.236, maxval=2, title='Standard Deviation'),
    Show=input.string('Both', options=('Longs Only', 'Shorts Only', 'Both'), title='Trade Type'),
    CC=input(True, 'Color Bars'),
    Notestart1=input(True, '╔═══ Time Range to BackTest ═══╗'),
    FromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    FromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    FromYear=input.int(defval=2018, title='From Year', minval=2015),
    ToMonth=input.int(defval=1, title='To Month', minval=1, maxval=12),
    ToDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    ToYear=input.int(defval=9999, title='To Year', minval=2010)
):
    basis = ta.sma(src, length)
    dev = mult * ta.stdev(src, length)
    upper = basis + dev
    lower = basis - dev
    short = src < lower
    long = src > upper
    L1 = ta.barssince(long)
    S1 = ta.barssince(short)
    longSignal = L1 < S1 and (not inline_series(L1 < S1, 1))
    shortSignal = S1 < L1 and (not inline_series(S1 < L1, 1))
    p1 = plot(upper, color=color.new(color.new('#FF0000'), 75), display=display.all, title='Upper Band')
    p2 = plot(lower, color=color.new(color.new('#008000'), 75), display=display.all, title='Lower Band')
    p = plot(basis, color=color.new('#008000') if L1 < S1 else color.new('#FF0000') if S1 < L1 else na, linewidth=2, editable=False, title='Basis')
    fill(p, p1, color=color.new(color.teal, 85), title='Top Fill')
    fill(p, p2, color=color.new(color.orange, 85), title='Bottom Fill')
    bcol = color.new(color.new('#8CEB07'), 0) if src > upper else color.new(color.new('#FF0000'), 0) if src < lower else color.green if src > basis else color.red if src < basis else na
    barcolor(bcol if CC else na, editable=False, title='Color Bars')
    start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    if window() and (Show == 'Longs Only' or Show == 'Both'):
        if longSignal:
            strategy.entry('Long', direction=strategy.long)
        if shortSignal:
            strategy.close('Long', comment='Close Long')
    if window() and (Show == 'Shorts Only' or Show == 'Both'):
        if shortSignal:
            strategy.entry('Short', direction=strategy.short)
        if longSignal:
            strategy.close('Short', comment='Close Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
