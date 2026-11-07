"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, hl2, input, location, math, na, nz, plot,
    plotshape, script, shape, size, strategy, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy("SuperTrend STRATEGY", overlay=True, initial_capital=10000000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.015, currency=currency.NONE, process_orders_on_close=True)
def main(
    Periods=input.int(10, title="ATR Period"),
    src: Series[float] = input(hl2, title="Source"),
    Multiplier=input.float(8.5, title="ATR Multiplier", step=0.1),
    FromMonth=input.int(1, title="From Month", minval=1, maxval=12),
    FromDay=input.int(1, title="From Day", minval=1, maxval=31),
    FromYear=input.int(2020, title="From Year", minval=999),
    ToMonth=input.int(1, title="To Month", minval=1, maxval=12),
    ToDay=input.int(1, title="To Day", minval=1, maxval=31),
    ToYear=input.int(9999, title="To Year", minval=999)
):
    atrVal = ta.sma(ta.tr, Periods)
    up: Series = src - Multiplier * atrVal
    up1 = nz(up[1], up)
    up = math.max(up, up1) if close[1] > up1 else up
    dn: Series = src + Multiplier * atrVal
    dn1 = nz(dn[1], dn)
    dn = math.min(dn, dn1) if close[1] < dn1 else dn

    trend: Series[int] = 1
    trend = nz(trend[1], trend)
    trend = 1 if trend == -1 and close > dn1 else -1 if trend == 1 and close < up1 else trend

    plot(up if trend == 1 else na, title='Up Trend', style=plot.style_linebr, linewidth=2, color=color.green)
    plot(na if trend == 1 else dn, title='Down Trend', style=plot.style_linebr, linewidth=2, color=color.red)

    buySignal = trend == 1 and trend[1] == -1
    sellSignal = trend == -1 and trend[1] == 1

    plotshape(up if buySignal else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.green, textcolor=color.white)
    plotshape(dn if sellSignal else na, title='Close', text='Close', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.black, textcolor=color.white)

    start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def window():
        return time >= start and time <= finish

    if buySignal and window():
        strategy.entry('BUY', strategy.long)

    if sellSignal and window():
        strategy.close('BUY')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
