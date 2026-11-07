"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, close, color, high, input, low, nz, open, plot, script, strategy,
    string, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy(title='Renko Strategy V2', shorttitle='Renko Strategy V2', overlay=True, precision=3, commission_value=0.025, default_qty_type=strategy.cash, default_qty_value=10000, initial_capital=10000, margin_long=0, margin_short=0, close_by_id=True)
def main(
    i_startTime=input.time(defval=timestamp('01 Jan 2020 00:00 +0000'), title='Start Time', group='Date Range'),
    i_endTime=input.time(defval=timestamp('31 Dec 2023 23:59 +0000'), title='End Time', group='Date Range'),
    allow_short=input.bool(False, title='Allow Short', group='Settings'),
    atr_len=input.int(10, 'ATR Length', group='Settings')
):
    time_cond = time >= i_startTime and time <= i_endTime
    atr = ta.atr(atr_len)
    def Renko1():
        p1: Series[float] = 0.0
        p1 = nz(p1[1]) + atr if close > nz(p1[1]) + atr else nz(p1[1]) - atr if close < nz(p1[1]) - atr else nz(p1[1])
        return p1

    def Renko2():
        p2: Series[float] = 0.0
        Br_1: Series = Renko1()
        p2 = Br_1[1] if Renko1() != inline_series(Renko1(), 1) else nz(p2[1])
        return p2

    def Renko3():
        p3: Series[float] = 0.0
        p3 = nz(p3[1]) + atr if open > nz(p3[1]) + atr else nz(p3[1]) - atr if open < nz(p3[1]) - atr else nz(p3[1])
        return p3

    def Renko4():
        open_v: Series[float] = 0.0
        Br_2: Series = Renko3()
        open_v = Br_2[1] if Renko3() != inline_series(Renko3(), 1) else nz(open_v[1])
        return open_v

    o2 = Renko4()
    c2 = Renko1()
    l2 = low
    h2 = high
    crossPlot: float = 0.0
    if o2 < c2:
        crossPlot = o2
    else:
        crossPlot = o2
    bars_since_up = ta.barssince(o2 < c2)
    bars_since_down = ta.barssince(o2 > c2)
    go_long = bars_since_up < bars_since_down and o2 < c2
    go_short = bars_since_up > bars_since_down and o2 > c2
    plotColor: Series = color.green if go_long else color.red if go_short else color.white
    plot(crossPlot, color=plotColor, style=plot.style_circles, linewidth=2, join=True)
    changeCond = plotColor != plotColor[1]
    closeStatus = 'win' if strategy.openprofit > 0 else 'lose'
    long_entry = plotColor == color.green and time_cond and changeCond
    long_exit_entry = plotColor == color.red
    short_entry = plotColor == color.red and time_cond and changeCond
    short_exit_entry = plotColor == color.green
    if long_entry:
        strategy.entry('long', strategy.long)
    if long_exit_entry:
        strategy.close('long', comment=closeStatus)
    if allow_short:
        if short_entry:
            strategy.entry('short', strategy.short)
    if short_exit_entry:
        strategy.close('short', comment=closeStatus)
    if long_entry:
        alert('Long Entry at price (' + string.tostring(close) + ')', alert.freq_once_per_bar)
    if allow_short and short_entry:
        alert('Short Entry at price (' + string.tostring(close) + ')', alert.freq_once_per_bar)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
