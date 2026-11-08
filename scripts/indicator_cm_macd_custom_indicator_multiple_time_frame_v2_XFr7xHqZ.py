"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, barcolor, bgcolor, close, color, hline, input, math, na, plot,
    request, script, string, syminfo, ta, timeframe
)
from pynecore.types import PersistentSeries, Series


@script.indicator(title='_CM_MacD_Ult_MTF_V2.1', shorttitle='_CM_Ult_MacD_MTF_V2.1', na_bool=True)
def main(
    res=input.timeframe('', 'Indicator TimeFrame'),
    fast_length=input.int(title='Fast Length', defval=12),
    slow_length=input.int(title='Slow Length', defval=26),
    src: Series[float] = input.source(title='Source', defval=close),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=999, defval=9),
    sma_source=input.string(title='Oscillator MA Type', defval='EMA', options=('SMA', 'EMA')),
    sma_signal=input.string(title='Signal Line MA Type', defval='EMA', options=('SMA', 'EMA')),
    show_macd=input.bool(True, title='Show MACD Lines', group='Show Plots?', inline='SP10'),
    show_macd_LW=input.int(3, minval=0, maxval=5, title='MACD Width', group='Show Plots?', inline='SP11'),
    show_signal_LW=input.int(2, minval=0, maxval=5, title='Signal Width', group='Show Plots?', inline='SP11'),
    show_Hist=input.bool(True, title='Show Histogram', group='Show Plots?', inline='SP20'),
    show_hist_LW=input.int(5, minval=0, maxval=5, title='-- Width', group='Show Plots?', inline='SP20'),
    show_trend=input.bool(True, title='Show MACD Lines w/ Trend Color', group='Show Plots?', inline='SP30'),
    show_HB=input.bool(False, title='Show Highlight Price Bars', group='Show Plots?', inline='SP40'),
    show_cross=input.bool(False, title='Show BackGround on Cross', group='Show Plots?', inline='SP50'),
    show_dots=input.bool(True, title='Show Circle on Cross', group='Show Plots?', inline='SP60'),
    show_dots_LW=input.int(5, minval=0, maxval=5, title='-- Width', group='Show Plots?', inline='SP60'),
    col_macd=input.color(color.new('#FF6D00'), 'MACD Line  ', group='Color Settings', inline='CS1'),
    col_signal=input.color(color.new('#2962FF'), 'Signal Line  ', group='Color Settings', inline='CS1'),
    col_trnd_Up=input.color(color.new('#4BAF4F'), 'Trend Up      ', group='Color Settings', inline='CS2'),
    col_trnd_Dn=input.color(color.new('#B71D1C'), 'Trend Down    ', group='Color Settings', inline='CS2'),
    col_grow_above=input.color(color.new('#26A69A'), 'Above   Grow', group='Histogram Colors', inline='Hist10'),
    col_fall_above=input.color(color.new('#B2DFDB'), 'Fall', group='Histogram Colors', inline='Hist10'),
    col_grow_below=input.color(color.new('#FF5252'), 'Below Grow', group='Histogram Colors', inline='Hist20'),
    col_fall_below=input.color(color.new('#FFCDD2'), 'Fall', group='Histogram Colors', inline='Hist20'),
    alert_Long=input.bool(True, title='MACD Cross Up', group='Alerts', inline='Alert10'),
    alert_Short=input.bool(True, title='MACD Cross Dn', group='Alerts', inline='Alert10'),
    alert_Long_A=input.bool(False, title='MACD Cross Up & > 0', group='Alerts', inline='Alert20'),
    alert_Short_B=input.bool(False, title='MACD Cross Dn & < 0', group='Alerts', inline='Alert20')
):
    fast_ma = request.security(syminfo.tickerid, res, ta.sma(src, fast_length) if sma_source == 'SMA' else ta.ema(src, fast_length))
    slow_ma = request.security(syminfo.tickerid, res, ta.sma(src, slow_length) if sma_source == 'SMA' else ta.ema(src, slow_length))
    macd: Series = fast_ma - slow_ma
    signal: Series = request.security(syminfo.tickerid, res, ta.sma(macd, signal_length) if sma_signal == 'SMA' else ta.ema(macd, signal_length))
    hist: Series = macd - signal
    trend_up = macd > signal
    trend_dn = macd < signal
    cross_UP = signal[1] >= macd[1] and signal < macd
    cross_DN = signal[1] <= macd[1] and signal > macd
    cross_UP_A = signal[1] >= macd[1] and signal < macd and (macd > 0)
    cross_DN_B = signal[1] <= macd[1] and signal > macd and (macd < 0)
    trend_col = col_trnd_Up if show_trend and trend_up else col_macd if trend_up else col_trnd_Dn if show_trend and trend_dn else col_macd if trend_dn else na
    histA_IsUp: PersistentSeries[bool] = False
    histA_IsDown: PersistentSeries[bool] = False
    histB_IsDown: PersistentSeries[bool] = False
    histB_IsUp: PersistentSeries[bool] = False
    histA_IsUp = histA_IsUp[1] if hist == hist[1] else hist > hist[1] and hist > 0
    histA_IsDown = histA_IsDown[1] if hist == hist[1] else hist < hist[1] and hist > 0
    histB_IsDown = histB_IsDown[1] if hist == hist[1] else hist < hist[1] and hist <= 0
    histB_IsUp = histB_IsUp[1] if hist == hist[1] else hist > hist[1] and hist <= 0
    hist_col = col_grow_above if histA_IsUp else col_fall_above if histA_IsDown else col_grow_below if histB_IsDown else col_fall_below if histB_IsUp else color.silver
    bgcolor(col_trnd_Up if show_cross and cross_UP else na, editable=False)
    bgcolor(col_trnd_Dn if show_cross and cross_DN else na, editable=False)
    barcolor(col_trnd_Up if show_HB and trend_up else na, title='Trend Up', offset=0, editable=False)
    barcolor(col_trnd_Dn if show_HB and trend_dn else na, title='Trend Dn', offset=0, editable=False)
    plot(hist if show_Hist and cast_bool(hist) else na, title='Histogram', style=plot.style_columns, color=color.new(hist_col, 0), linewidth=math.max(1, show_hist_LW))
    plot(signal if show_macd and cast_bool(signal) else na, title='Signal', color=color.new(col_signal, 0), style=plot.style_line, linewidth=math.max(1, show_signal_LW))
    plot(macd if show_macd and cast_bool(macd) else na, title='MACD', color=color.new(trend_col, 0), style=plot.style_line, linewidth=math.max(1, show_macd_LW))
    hline(0, title='0 Line', color=color.new(color.gray, 0), linestyle=hline.style_dashed, linewidth=1, editable=False)
    plot(macd if show_dots and cross_UP else na, title='Dots', color=color.new(trend_col, 0), style=plot.style_circles, linewidth=math.max(1, show_dots_LW), editable=False)
    plot(macd if show_dots and cross_DN else na, title='Dots', color=color.new(trend_col, 0), style=plot.style_circles, linewidth=math.max(1, show_dots_LW), editable=False)
    if alert_Long and cross_UP:
        alert('Symbol = (' + syminfo.tickerid + ') TimeFrame = (' + timeframe.period + ') Current Price (' + string.tostring(close) + ') MACD Crosses Up.', alert.freq_once_per_bar_close)
    if alert_Short and cross_DN:
        alert('Symbol = (' + syminfo.tickerid + ') TimeFrame = (' + timeframe.period + ') Current Price (' + string.tostring(close) + ') MACD Crosses Down.', alert.freq_once_per_bar_close)
    if alert_Long_A and cross_UP_A:
        alert('Symbol = (' + syminfo.tickerid + ') TimeFrame = (' + timeframe.period + ') Current Price (' + string.tostring(close) + ') MACD > 0 And Crosses Up.', alert.freq_once_per_bar_close)
    if alert_Short_B and cross_DN_B:
        alert('Symbol = (' + syminfo.tickerid + ') TimeFrame = (' + timeframe.period + ') Current Price (' + string.tostring(close) + ') MACD < 0 And Crosses Down.', alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)