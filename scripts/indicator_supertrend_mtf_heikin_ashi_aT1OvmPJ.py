"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, barmerge, close, color, high, input, low, math, na, nz,
    plot, request, script, syminfo, ta, ticker, timeframe
)
from pynecore.types import Series


@script.indicator('Supertrend MTF Heikin Ashi', overlay=True, na_bool=True)
def main(
    mode=input.string(title='HTF Method', defval='Auto', options=('Auto', 'User Defined')),
    HTFm=input.timeframe('5', title='Time Frame (if HTF Method=User Defined)'),
    Mult=input.float(defval=2.0, title='ATR Factor', minval=0.5, maxval=100, step=0.1),
    Period=input.int(defval=7, title='ATR Period', minval=1, maxval=100)
):
    HTFo = '5' if timeframe.period == '1' else '15' if timeframe.period == '3' else '15' if timeframe.period == '5' else '60' if timeframe.period == '15' else '120' if timeframe.period == '30' else '120' if timeframe.period == '45' else '240' if timeframe.period == '60' else '240' if timeframe.period == '120' else '240' if timeframe.period == '180' else 'D' if timeframe.period == '240' else 'W' if timeframe.period == 'D' else '5W' if timeframe.period == 'W' else 'D'
    HTF = HTFo if mode == 'Auto' else HTFm
    h = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, high)
    l = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, low)
    c: Series = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, close)
    Atr = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, ta.atr(Period))
    Up = (h + l) / 2 - Mult * Atr
    Dn = (h + l) / 2 + Mult * Atr
    TUp: Series[float] = na(float)
    TDown: Series[float] = na(float)
    Trend: Series[int] = 0
    TUp = math.max(Up, TUp[1]) if c[1] > TUp[1] else Up
    TDown = math.min(Dn, TDown[1]) if c[1] < TDown[1] else Dn
    Trend = 1 if c > TDown[1] else -1 if c < TUp[1] else nz(Trend[1], 1)
    Trailingsl = TUp if Trend == 1 else TDown
    linecolor = color.lime if Trend == 1 and nz(Trend[1]) == 1 else color.red if Trend == -1 and nz(Trend[1]) == -1 else na
    plot(Trailingsl, color=linecolor, linewidth=2, title='SuperTrend')
    highhtf = request.security(ticker.heikinashi(syminfo.tickerid), HTF, high[1], lookahead=barmerge.lookahead_on)
    lowhtf = request.security(ticker.heikinashi(syminfo.tickerid), HTF, low[1], lookahead=barmerge.lookahead_on)
    closehtf: Series = request.security(ticker.heikinashi(syminfo.tickerid), HTF, close[1], lookahead=barmerge.lookahead_on)
    HTfatr = request.security(ticker.heikinashi(syminfo.tickerid), HTF, inline_series(ta.atr(Period), 1), lookahead=barmerge.lookahead_on)
    Uphtf = math.abs(highhtf + lowhtf) / 2 - Mult * HTfatr
    Dnhtf = math.abs(highhtf + lowhtf) / 2 + Mult * HTfatr
    TUphtf: Series[float] = na(float)
    TDownhtf: Series[float] = na(float)
    TrendHtf: Series[int] = 0
    TUphtf = math.max(Uphtf, TUphtf[1]) if closehtf[1] > TUphtf[1] else Uphtf
    TDownhtf = math.min(Dnhtf, TDownhtf[1]) if closehtf[1] < TDownhtf[1] else Dnhtf
    TrendHtf = 1 if closehtf > TDownhtf[1] else -1 if closehtf < TUphtf[1] else nz(TrendHtf[1], 1)
    TrailingslHtf = TUphtf if TrendHtf == 1 else TDownhtf
    linecolorHtf = color.blue if TrendHtf == 1 and nz(TrendHtf[1]) == 1 else color.red if TrendHtf == -1 and nz(TrendHtf[1]) == -1 else na
    st = plot(TrailingslHtf, color=linecolorHtf, linewidth=3, title='Supertrend HTF')
    plot(TrailingslHtf if TrendHtf == 1 and TrendHtf[1] == -1 else na, title='Supertrend HTF Trend Up', linewidth=4, color=color.new(color.blue, 0), style=plot.style_circles)
    plot(TrailingslHtf if TrendHtf == -1 and TrendHtf[1] == 1 else na, title='Supertrend HTF Trend Down', linewidth=4, color=color.new(color.red, 0), style=plot.style_circles)
    alertcondition(Trend == 1 and Trend[1] == -1, title='Supertrend Trend Up', message='Supertrend Trend Up')
    alertcondition(Trend == -1 and Trend[1] == 1, title='Supertrend  Trend Down', message='Supertrend Trend Down')
    alertcondition(TrendHtf == 1 and TrendHtf[1] == -1, title='Supertrend HTF Trend Up', message='Supertrend HTF Trend Upl')
    alertcondition(TrendHtf == -1 and TrendHtf[1] == 1, title='Supertrend HTF Trend Down', message='Supertrend HTF Trend Down')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
