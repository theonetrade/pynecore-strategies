"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, hl2, input, math, nz, plot, script, strategy, ta, time,
    timestamp
)
from pynecore.types import Series


@script.strategy('SuperTrend Backtester', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    Factor=input.int(3, minval=1, maxval=100),
    Pd=input.int(7, minval=1, maxval=100),
    FromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    FromDay=input.int(defval=9, title='From Day', minval=1, maxval=31),
    FromYear=input.int(defval=2019, title='From Year', minval=2018),
    ToMonth=input.int(defval=1, title='To Month', minval=1, maxval=12),
    ToDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    ToYear=input.int(defval=9999, title='To Year', minval=2017),
    exitsEnabled=input(True),
    takeProfit=input(100),
    stopLoss=input(100)
):
    start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    Up = hl2 - Factor * ta.atr(Pd)
    Dn = hl2 + Factor * ta.atr(Pd)
    TrendUp: Series[float] = 0.0
    TrendUp = math.max(Up, TrendUp[1]) if close[1] > TrendUp[1] else Up
    TrendDown: Series[float] = 0.0
    TrendDown = math.min(Dn, TrendDown[1]) if close[1] < TrendDown[1] else Dn
    Trend: Series[int] = 0
    Trend = 1 if close > TrendDown[1] else -1 if close < TrendUp[1] else nz(Trend[1], 1)
    Tsl = TrendUp if Trend == 1 else TrendDown
    linecolor = color.green if Trend == 1 else color.red
    plot(Tsl, color=linecolor, style=plot.style_line, linewidth=2, title='SuperTrend')
    window_1 = window()
    if Trend != Trend[1] and window_1:
        if Trend == 1:
            strategy.entry('long', strategy.long)
            if exitsEnabled:
                strategy.exit('long', profit=takeProfit, loss=stopLoss)
        else:
            strategy.entry('short', strategy.short)
            if exitsEnabled:
                strategy.exit('short', profit=takeProfit, loss=stopLoss)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
