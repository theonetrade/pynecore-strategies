"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    array, bar_index, barcolor, barstate, chart, close, color, display, fill,
    high, input, label, location, low, na, open, plot, plotcandle, plotchar, script, size, string,
    ta
)
from pynecore.types import Color, NA, Persistent, PersistentSeries, Series


@script.indicator('Linear Regression Oscillator [ChartPrime]', overlay=False, max_labels_count=500)
def main(
    length=input.int(20, 'Length'),
    upper=input.float(1.5, 'Upper Threshold', step=0.1),
    lower=input.float(-1.5, 'Lower Threshold', step=0.1),
    candles=input.bool(False, 'Plot Bar Color')
):
    col_up: Color = color.new('#10CAB8')
    col_dn: Color = color.blue
    source: Series[float] = close[0 if barstate.isconfirmed else 1]
    lowest: Persistent[list[float]] = array.new_float(5)
    highest: Persistent[list[float]] = array.new_float(5)
    points: PersistentSeries[float] = na(float)
    def linear_regression_osc(length: int):
        __hist_source__: Series[float] = source[0]
        n = length
        sum_x: float = 0.0
        sum_y: float = 0.0
        sum_xy: float = 0.0
        sum_x_squared: float = 0.0
        __block_result__ = na
        for i in pine_range(0, n - 1, 1):
            sum_x = sum_x + i
            sum_y = sum_y + __hist_source__[i]
            sum_xy = sum_xy + i * __hist_source__[i]
            sum_x_squared = sum_x_squared + i * i
            m = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x * sum_x)
            c = (sum_y - m * sum_x) / n
            linear_regression__0000000b__ = (m * bar_index + c) * -1
            __block_result__ = linear_regression__0000000b__
        return __block_result__

    linear_regression: Series = linear_regression_osc(length)
    linear_regression = (linear_regression - ta.sma(linear_regression, 100)) / ta.stdev(linear_regression, 100)
    cond1 = ta.crossunder(linear_regression, 0)
    cond2 = ta.crossover(linear_regression, 0)
    cond_1 = linear_regression[1] if ta.crossunder(linear_regression, linear_regression[2]) and linear_regression > upper else na
    cond_2 = linear_regression[1] if ta.crossover(linear_regression, linear_regression[2]) and linear_regression < lower else na
    array.push(lowest, low)
    array.push(highest, high)
    if array.size(lowest) > 5:
        array.shift(lowest)
        array.shift(highest)
    if cond1:
        points = array.max(highest)
    elif cond2:
        points = array.min(lowest)
    color__ren__ = color.from_gradient(linear_regression, 0, 2, NA(Color), col_up) if linear_regression > 0 else color.from_gradient(linear_regression, -2, 0, col_dn, NA(Color))
    color1 = color.from_gradient(linear_regression, 0, 2, NA(Color), color.new(chart.fg_color, 50)) if linear_regression > 0 else color.from_gradient(linear_regression, -2, 0, color.new(chart.fg_color, 50), NA(Color))
    color2 = color.from_gradient(linear_regression, 0, 1, NA(Color), col_up) if linear_regression > 0 else color.from_gradient(linear_regression, -1, 0, col_dn, NA(Color))
    plot(linear_regression, color=color__ren__, style=plot.style_area)
    plot(0, color=color1, linewidth=2)
    p1 = plot(upper, display=display.none)
    p3 = plot(lower, display=display.none)
    p4 = plot(-4, display=display.none)
    p2 = plot(4, display=display.none)
    fill(p1, p2, 4, upper, na, color.new(col_up, 75))
    fill(p3, p4, lower, -4, color.new(col_dn, 75), na)
    if barstate.islast:
        l1: Series = label.new(bar_index, upper, string.tostring(upper), style=label.style_diamond, size=size.tiny, textcolor=chart.fg_color, color=col_up)
        label.delete(l1[1])
        l2: Series = label.new(bar_index, lower, string.tostring(lower), style=label.style_diamond, size=size.tiny, textcolor=chart.fg_color, color=col_dn)
        label.delete(l2[1])
    plotchar(cond_1, '', '◇', color=col_dn, location=location.absolute, size=size.small, offset=-1)
    plotchar(cond_2, '', '◇', color=col_up, location=location.absolute, size=size.small, offset=-1)
    plotchar(0 if cond1 else na, '', '◆', color=color.new(col_dn, 0), location=location.absolute, size=size.tiny, offset=-1)
    plotchar(0 if cond2 else na, '', '◆', color=color.new(col_up, 0), location=location.absolute, size=size.tiny, offset=-1)
    if cond2:
        label.new(chart.point.from_index(bar_index, low), '▲', style=label.style_label_up, textcolor=col_up, size=size.large, color=NA(Color), force_overlay=True)
    elif cond1:
        label.new(chart.point.from_index(bar_index, high), '▽', style=label.style_label_down, textcolor=col_dn, size=size.large, color=NA(Color), force_overlay=True)
    if cast_bool(cond_2):
        label.new(chart.point.from_index(bar_index, low), text='◆\nReversion', style=label.style_label_up, textcolor=col_up, size=size.normal, color=NA(Color), force_overlay=True)
    elif cast_bool(cond_1):
        label.new(chart.point.from_index(bar_index, high), text='Reversion\n◆', style=label.style_label_down, textcolor=col_dn, size=size.normal, color=NA(Color), force_overlay=True)
    plot(points if not ta.change(points) else na, color=color2, linewidth=2, style=plot.style_linebr, force_overlay=True)
    if cast_bool(ta.change(points)):
        label.new(chart.point.from_index(bar_index, points[1]), text='Invalidation\nLevel', style=label.style_label_left, textcolor=col_up if linear_regression < 0 else col_dn, size=size.small, color=NA(Color), force_overlay=True)
    candle_col = (col_dn if linear_regression < 0 else col_up) if candles else na
    plotcandle(open, high, low, close, title='Color Candles', color=candle_col, bordercolor=candle_col, wickcolor=candle_col, force_overlay=True)
    barcolor(candle_col)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)