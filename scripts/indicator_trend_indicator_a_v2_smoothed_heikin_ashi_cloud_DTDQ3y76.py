"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fill, high, input, low, math, na, open, plot, request,
    script, syminfo, ta, ticker, timeframe
)
from pynecore.types import Series


@script.indicator('Trend Indicator A (v2.3)', 'Trend Indicator A (v2.3)', True)
def main(
    ma_type=input.string('EMA', 'MA Type', options=('ALMA', 'HMA', 'SMA', 'SWMA', 'VWMA', 'WMA', 'ZLEMA', 'EMA'), group='Setup'),
    ma_period=input.int(9, 'MA Period (Length)', minval=1, group='Setup'),
    alma_offset=input.float(0.85, 'ALMA Shift', minval=0, maxval=1, step=0.05, group='Setup (ALMA)'),
    alma_sigma=input.int(6, 'ALMA Deviation', minval=1, step=1, group='Setup (ALMA)'),
    __input_4__=input.bool(True, 'Show Close line', group='On/Off'),
    __input_5__=input.bool(False, 'Show High/Low lines', group='On/Off'),
    __input_6__=input.bool(True, 'Show fill', group='On/Off'),
    color_positive=input.color(color.new(color.new('#26A69A'), 0), 'Positive color (Bullish)', group='Colors'),
    color_negative=input.color(color.new(color.new('#EF5350'), 0), 'Negative color (Bearish)', group='Colors'),
    color_neutral=input.color(color.new(color.new('#808080'), 0), 'Neutral color', group='Colors')
):
    def show_line_1(x):
        return x if __input_4__ else na

    def show_line_2(x):
        return x if __input_5__ else na

    def show_fill(x):
        return x if __input_6__ else na

    def f(x: Series):
        __block_result__ = na
        __switch__ = ma_type
        if __switch__ == 'ALMA':
            __block_result__ = ta.alma(x, ma_period, alma_offset, alma_sigma)
        elif __switch__ == 'HMA':
            __block_result__ = ta.hma(x, ma_period)
        elif __switch__ == 'SMA':
            __block_result__ = ta.sma(x, ma_period)
        elif __switch__ == 'SWMA':
            __block_result__ = ta.swma(x)
        elif __switch__ == 'VWMA':
            __block_result__ = ta.vwma(x, ma_period)
        elif __switch__ == 'WMA':
            __block_result__ = ta.vwma(x, ma_period)
        elif __switch__ == 'ZLEMA':
            __block_result__ = ta.ema(x + x - x[math.floor((ma_period - 1) / 2)], ma_period)
        else:
            __block_result__ = ta.ema(x, ma_period)
        return __block_result__

    ma_heikinashi_open = f(request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, open))
    ma_heikinashi_close = f(request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, close))
    ma_heikinashi_high = f(request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, high))
    ma_heikinashi_low = f(request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, low))
    trend = 100 * (ma_heikinashi_close - ma_heikinashi_open) / (ma_heikinashi_high - ma_heikinashi_low)
    color_trend = color_positive if trend > 0 else color_negative
    plot_open = plot(ma_heikinashi_open, 'Open line', na)
    plot_close = plot(ma_heikinashi_close, 'Close line', show_line_1(color_trend), 2)
    plot_high = plot(ma_heikinashi_high, 'High line', show_line_2(color_neutral))
    plot_low = plot(ma_heikinashi_low, 'Low line', show_line_2(color_neutral))
    plot_highest = plot(math.max(ma_heikinashi_open, ma_heikinashi_close), 'Highest Body line', na)
    plot_lowest = plot(math.min(ma_heikinashi_open, ma_heikinashi_close), 'Lowest Body line', na)
    fill(plot_open, plot_close, color.new(color_trend, 50), 'Open/Close Cloud')
    fill(plot_high, plot_highest, show_fill(color.new(color_neutral, 87.5)), title='High Cloud')
    fill(plot_lowest, plot_low, show_fill(color.new(color_neutral, 87.5)), title='Low Cloud')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
