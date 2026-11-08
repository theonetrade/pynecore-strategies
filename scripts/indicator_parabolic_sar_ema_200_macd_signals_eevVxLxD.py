"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, high, input, location, low, na, ohlc4,
    plot, plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator(title='Parabolic SAR + EMA 200 + MACD Signals', shorttitle='SAR EMA MACD', overlay=True, timeframe='', timeframe_gaps=True)
def main(
    sar_start=input(0.02),
    sar_increment=input(0.02),
    sar_maximum=input(0.2, 'Max Value'),
    ema_len=input.int(200, minval=1, title='Length'),
    ema_src: Series[float] = input(close, title='Source'),
    ema_offset=input.int(title='Offset', defval=0, minval=-500, maxval=500),
    macd_fast_length=input(title='Fast Length', defval=12),
    macd_slow_length=input(title='Slow Length', defval=26),
    macd_src: Series[float] = input(title='Source', defval=close),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9),
    sma_source=input.string(title='Oscillator MA Type', defval='EMA', options=('SMA', 'EMA')),
    sma_signal=input.string(title='Signal Line MA Type', defval='EMA', options=('SMA', 'EMA')),
    col_macd=input(color.new('#2962FF'), 'MACD Line  ', group='Color Settings', inline='MACD'),
    col_signal=input(color.new('#FF6D00'), 'Signal Line  ', group='Color Settings', inline='Signal'),
    col_grow_above=input(color.new('#26A69A'), 'Above   Grow', group='Histogram', inline='Above'),
    col_fall_above=input(color.new('#B2DFDB'), 'Fall', group='Histogram', inline='Above'),
    col_grow_below=input(color.new('#FFCDD2'), 'Below Grow', group='Histogram', inline='Below'),
    col_fall_below=input(color.new('#FF5252'), 'Fall', group='Histogram', inline='Below')
):
    SAR = ta.sar(sar_start, sar_increment, sar_maximum)
    plot(SAR, 'ParabolicSAR', style=plot.style_circles, color=color.new('#2962FF'))
    EMA_200 = ta.ema(ema_src, ema_len)
    plot(EMA_200, title='EMA', color=color.blue, offset=ema_offset)
    fast_ma = ta.sma(macd_src, macd_fast_length) if sma_source == 'SMA' else ta.ema(macd_src, macd_fast_length)
    slow_ma = ta.sma(macd_src, macd_slow_length) if sma_source == 'SMA' else ta.ema(macd_src, macd_slow_length)
    macd = fast_ma - slow_ma
    signal = ta.sma(macd, signal_length) if sma_signal == 'SMA' else ta.ema(macd, signal_length)
    delta = macd - signal
    __block_result__ = na
    if ohlc4 < EMA_200:
        __block_result__ = 'Bearish'
    else:
        __block_result__ = 'Bullish'
    main_trend = __block_result__
    __block_result_1__ = na
    if SAR < low:
        __block_result_1__ = True
    else:
        __block_result_1__ = False
    sar_long = __block_result_1__
    __block_result_2__ = na
    if SAR > high:
        __block_result_2__ = True
    else:
        __block_result_2__ = False
    sar_short = __block_result_2__
    __block_result_3__ = na
    if ta.crossover(delta, 0):
        __block_result_3__ = True
    else:
        __block_result_3__ = False
    macd_long = __block_result_3__
    __block_result_4__ = na
    if ta.crossunder(delta, 0):
        __block_result_4__ = True
    else:
        __block_result_4__ = False
    macd_short = __block_result_4__
    buy_signal = sar_long and macd_long and (main_trend == 'Bullish')
    sell_signal = sar_short and macd_short and (main_trend == 'Bearish')
    plotshape(buy_signal, title='Buy Label', text='Buy', location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.green, textcolor=color.white)
    plotshape(sell_signal, title='Sell Label', text='Sell', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.red, textcolor=color.white)
    alertcondition(buy_signal, title='SAR EMA200 MACD Buy signal!', message='Buy signal')
    alertcondition(sell_signal, title='SAR EMA200 MACD Sell signal!', message='Sell signal')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
