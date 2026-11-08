"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    bar_index, box, close, color, fill, high, input, label, low, math, na,
    open, plot, plotcandle, script, size, string, ta
)
from pynecore.types import Box, Color, NA, Persistent, Series


@script.indicator('Kalman Trend Levels [BigBeluga]', overlay=True, max_labels_count=500, max_boxes_count=500, na_bool=True)
def main(
    short_len=input.int(50),
    long_len=input.int(150),
    retest_sig=input.bool(False, 'Retest Signals'),
    candle_color=input.bool(True, 'Candle Color'),
    upper_col=input.color(color.new('#13BD6E'), 'up', inline='colors'),
    lower_col=input.color(color.new('#AF0D4B'), 'dn', inline='colors')
):
    atr: float = ta.atr(200) * 0.5
    lower_box: Persistent = NA(Box)
    upper_box: Persistent = NA(Box)
    def kalman_filter(src: Series, length, R = 0.01, Q = 0.1):
        estimate: Persistent[float] = na(float)
        error_est: Persistent[float] = 1.0
        error_meas: Persistent[float] = R * length
        kalman_gain: Persistent[float] = 0.0
        prediction: Persistent[float] = na(float)
        if na(estimate):
            estimate = src[1]
        prediction = estimate
        kalman_gain = error_est / (error_est + error_meas)
        estimate = prediction + kalman_gain * (src - prediction)
        error_est = (1 - kalman_gain) * error_est + Q / length
        return estimate

    short_kalman: Series[float] = kalman_filter(close, short_len)
    long_kalman: float = kalman_filter(close, long_len)
    trend_up: Series[bool] = short_kalman > long_kalman
    trend_col: Color = upper_col if trend_up else lower_col
    trend_col1: Color = upper_col if short_kalman > short_kalman[2] else lower_col
    candle_col: Color = (upper_col if trend_up and short_kalman > short_kalman[2] else lower_col if not trend_up and short_kalman < short_kalman[2] else color.gray) if candle_color else na
    if trend_up and (not trend_up[1]):
        label.new(bar_index, short_kalman, '🡹\n' + string.tostring(math.round(close, 1)), color=NA(Color), textcolor=upper_col, style=label.style_label_up, size=size.normal)
        lower_box = box.new(bar_index, low + atr, bar_index, low, border_color=na, bgcolor=color.new(upper_col, 60))
    if not ta.change(trend_up):
        method_call('set_right', lower_box, bar_index)
    if trend_up[1] and (not trend_up):
        label.new(bar_index, short_kalman, string.tostring(math.round(close, 1)) + '\n🢃', color=NA(Color), textcolor=lower_col, style=label.style_label_down, size=size.normal)
        upper_box = box.new(bar_index, high, bar_index, high - atr, border_color=na, bgcolor=color.new(lower_col, 60))
    if not ta.change(trend_up):
        method_call('set_right', upper_box, bar_index)
    if retest_sig:
        if high < method_call('get_bottom', upper_box) and high[1] >= method_call('get_bottom', upper_box):
            label.new(bar_index - 1, high[1], 'x', color=NA(Color), textcolor=lower_col, style=label.style_label_down, size=size.normal)
        if low > method_call('get_top', lower_box) and low[1] <= method_call('get_top', lower_box):
            label.new(bar_index - 1, low[1], '+', color=NA(Color), textcolor=upper_col, style=label.style_label_up, size=size.normal)
    p1 = plot(short_kalman, 'Short Kalman', color=trend_col1)
    p2 = plot(long_kalman, 'Long Kalman', linewidth=2, color=trend_col)
    fill(p1, p2, short_kalman, long_kalman, na, color.new(trend_col, 80))
    plotcandle(open, high, low, close, title='Title', color=candle_col, wickcolor=candle_col, bordercolor=candle_col)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
