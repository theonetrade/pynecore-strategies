"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    barcolor, close, color, currency, hl2, input, location, math, na, nz,
    plot, plotshape, script, shape, size, strategy, ta, time, timestamp
)
from pynecore.types import Persistent, Series


@script.strategy('PPS', overlay=True, initial_capital=500000, currency=currency.USD, default_qty_type=strategy.cash, default_qty_value=50000, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    prd=input.int(defval=2, title='Pivot Point Period', minval=1, maxval=50),
    Factor=input.float(defval=3, title='ATR Factor', minval=1, step=0.1),
    Pd=input.int(defval=10, title='ATR Period', minval=1),
    showpivot=input(defval=False, title='Show Pivot Points'),
    showlabel=input(defval=True, title='Show Buy/Sell Labels'),
    showcl=input(defval=False, title='Show PP Center Line'),
    showsr=input(defval=False, title='Show Support/Resistance'),
    Periods=input(title='ATR Period', defval=10),
    src: Series[float] = input(hl2, title='Source'),
    Multiplier=input.float(title='ATR Multiplier', step=0.1, defval=3.0),
    changeATR=input(title='Change ATR Calculation Method ?', defval=True),
    periodes_ma=input(title='Moving Average Period', defval=20),
    src_ma: Series[float] = input(title='Moving Average Source', defval=close),
    FromMonth=input.int(defval=9, title='From Month', minval=1, maxval=12),
    FromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    FromYear=input.int(defval=2018, title='From Year', minval=999),
    ToMonth=input.int(defval=1, title='To Month', minval=1, maxval=12),
    ToDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    ToYear=input.int(defval=9999, title='To Year', minval=999)
):
    ph: float = ta.pivothigh(prd, prd)
    pl: float = ta.pivotlow(prd, prd)
    plotshape(cast_bool(ph) and showpivot, text='H', style=shape.labeldown, color=na, textcolor=color.new(color.red, 0), location=location.abovebar, offset=-prd)
    plotshape(cast_bool(pl) and showpivot, text='L', style=shape.labeldown, color=na, textcolor=color.new(color.lime, 0), location=location.belowbar, offset=-prd)
    center: Persistent[float] = na(float)
    lastpp: float = ph if cast_bool(ph) else pl if cast_bool(pl) else na
    if cast_bool(lastpp):
        if na(center):
            center = lastpp
        else:
            center = (center * 2 + lastpp) / 3
    Up = center - Factor * ta.atr(Pd)
    Dn = center + Factor * ta.atr(Pd)
    TUp: Series[float] = na(float)
    TDown: Series[float] = na(float)
    Trend: Series[int] = 0
    TUp = math.max(Up, TUp[1]) if close[1] > TUp[1] else Up
    TDown = math.min(Dn, TDown[1]) if close[1] < TDown[1] else Dn
    Trend = 1 if close > TDown[1] else -1 if close < TUp[1] else nz(Trend[1], 1)
    Trailingsl = TUp if Trend == 1 else TDown
    linecolor = color.lime if Trend == 1 and nz(Trend[1]) == 1 else color.red if Trend == -1 and nz(Trend[1]) == -1 else na
    plot(Trailingsl, color=linecolor, linewidth=2, title='PP SuperTrend')
    plot(center if showcl else na, color=(color.blue if center < hl2 else color.red) if showcl else na)
    bsignal = Trend == 1 and Trend[1] == -1
    ssignal = Trend == -1 and Trend[1] == 1
    plotshape(Trailingsl if bsignal and showlabel else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.lime, 0), textcolor=color.new(color.black, 0))
    plotshape(Trailingsl if ssignal and showlabel else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    resistance: Series[float] = na(float)
    support: Series[float] = na(float)
    support = pl if cast_bool(pl) else support[1]
    resistance = ph if cast_bool(ph) else resistance[1]
    plot(support if showsr and cast_bool(support) else na, color=color.lime if showsr and support else na, style=plot.style_circles, offset=-prd)
    plot(resistance if showsr and cast_bool(resistance) else na, color=color.red if showsr and resistance else na, style=plot.style_circles, offset=-prd)
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
    ma = ta.sma(src_ma, periodes_ma)
    start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    window_1 = window()
    longCondition = trend == 1 and trend[1] == -1 and (close > ma) or (bsignal and window_1)
    window_2 = window()
    shortCondition = trend == -1 and trend[1] == 1 and (close < ma) or (ssignal and window_2)
    if longCondition:
        strategy.entry('BUY', strategy.long)
    if shortCondition:
        strategy.close('BUY')
        strategy.entry('SELL', strategy.short)
    window_3 = window()
    buy1: Series = ta.barssince(trend == 1 and trend[1] == -1 and (close > ma) or (bsignal and window_3))
    window_4 = window()
    sell1: Series = ta.barssince(trend == -1 and trend[1] == 1 and (close < ma) or (ssignal and window_4))
    color1 = color.green if buy1[1] < sell1[1] else color.red if buy1[1] > sell1[1] else na
    barcolor(color1)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
