"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, close, color, fill, hl2, input, location, math, na, nz, ohlc4,
    plot, plotshape, script, shape, size, strategy, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy('SuperTrend STRATEGY', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    Periods=input(title='ATR Period', defval=10),
    src: Series[float] = input(hl2, title='Source'),
    Multiplier=input.float(title='ATR Multiplier', step=0.1, defval=3.0),
    changeATR=input(title='Change ATR Calculation Method ?', defval=True),
    showsignals=input(title='Show Buy/Sell Signals ?', defval=False),
    highlighting=input(title='Highlighter On/Off ?', defval=True),
    barcoloring=input(title='Bar Coloring On/Off ?', defval=True),
    FromMonth=input.int(defval=9, title='From Month', minval=1, maxval=12),
    FromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    FromYear=input.int(defval=2018, title='From Year', minval=999),
    ToMonth=input.int(defval=1, title='To Month', minval=1, maxval=12),
    ToDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    ToYear=input.int(defval=9999, title='To Year', minval=999)
):
    atr2 = ta.sma(ta.tr, Periods)
    atr = ta.atr(Periods) if changeATR else atr2
    up: Series = src - Multiplier * atr
    up1 = nz(up[1], up)
    up = math.max(up, up1) if close[1] > up1 else up
    dn: Series = src + Multiplier * atr
    dn1 = nz(dn[1], dn)
    dn = math.min(dn, dn1) if close[1] < dn1 else dn
    trend: Series[int] = 1
    trend = nz(trend[1], trend)
    trend = 1 if trend == -1 and close > dn1 else -1 if trend == 1 and close < up1 else trend
    upPlot = plot(up if trend == 1 else na, title='Up Trend', style=plot.style_linebr, linewidth=2, color=color.new(color.green, 0))
    buySignal = trend == 1 and trend[1] == -1
    plotshape(up if buySignal else na, title='UpTrend Begins', location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(color.green, 0))
    plotshape(up if buySignal and showsignals else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    dnPlot = plot(na if trend == 1 else dn, title='Down Trend', style=plot.style_linebr, linewidth=2, color=color.new(color.red, 0))
    sellSignal = trend == -1 and trend[1] == 1
    plotshape(dn if sellSignal else na, title='DownTrend Begins', location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(color.red, 0))
    plotshape(dn if sellSignal and showsignals else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    mPlot = plot(ohlc4, title='', style=plot.style_circles, linewidth=math.max(1, 0))
    longFillColor = (color.green if trend == 1 else color.white) if highlighting else color.white
    shortFillColor = (color.red if trend == -1 else color.white) if highlighting else color.white
    fill(mPlot, upPlot, title='UpTrend Highligter', color=longFillColor)
    fill(mPlot, dnPlot, title='DownTrend Highligter', color=shortFillColor)
    start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    longCondition = buySignal
    if longCondition:
        if window():
            strategy.entry('BUY', strategy.long)
    shortCondition = sellSignal
    if shortCondition:
        if window():
            strategy.entry('SELL', strategy.short)
    buy1: Series = ta.barssince(buySignal)
    sell1: Series = ta.barssince(sellSignal)
    color1 = color.green if buy1[1] < sell1[1] else color.red if buy1[1] > sell1[1] else na
    barcolor(color1 if barcoloring else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
