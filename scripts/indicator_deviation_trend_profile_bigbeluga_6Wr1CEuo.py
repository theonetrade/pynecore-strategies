"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.series import inline_series
from pynecore.lib import (
    array, bar_index, barstate, box, chart, close, color, input, label, line,
    location, na, plot, plotshape, script, shape, size, string, ta
)
from pynecore.types import Box, NA, Persistent, PersistentSeries, Series

grp: str = "Standart Deviation Levels"


@script.indicator("Deviation Trend Profile [BigBeluga]", overlay=True, max_boxes_count=500, max_bars_back=5000)
def main(
    length=input.int(50, "SMA Length", group="SMA"),
    mult1=input.int(1, "Standart Deviation 1", group=grp),
    mult2=input.int(2, "Standart Deviation 2", group=grp),
    mult3=input.int(3, "Standart Deviation 3", group=grp),
    show_tp=input.bool(True, "Show", group="Trend Distribution Profile"),
    bins=input.int(50, "Bins Amount", group="Trend Distribution Profile"),
    offset=input.int(30, "Offset", group="Trend Distribution Profile"),
    col_up=input.color(color.rgb(18, 209, 235), "", group="Theme", inline="c"),
    col_dn=input.color(color.rgb(250, 40, 86), "", group="Theme", inline="c")
):
    start_index: Persistent = NA(int)
    trend: PersistentSeries = NA(bool)

    avg: Series = ta.sma(close, length)
    atr = ta.atr(200)

    stdv1 = avg + atr * mult1
    stdv2 = avg + atr * mult2
    stdv3 = avg + atr * mult3

    stdv_1 = avg - atr * mult1
    stdv_2 = avg - atr * mult2
    stdv_3 = avg - atr * mult3

    max = stdv3
    min = stdv_3

    avg_diff = avg - avg[5]

    avg_col = avg_diff / ta.percentile_linear_interpolation(avg_diff, 500, 100)

    avg_color = color.from_gradient(avg_col, -0.3, 0.3, col_dn, col_up)

    if ta.crossover(avg_col, 0.1) and (not trend):
        trend = True
        start_index = bar_index

    if ta.crossunder(avg_col, -0.1) and trend:
        trend = False
        start_index = bar_index

    loockback = bar_index - start_index

    def profile(min: Series, max):
        __hist_avg__: Series = avg[0]
        boxes: Persistent[list[Box]] = array.new_box()
        bin: Persistent[list[int]] = array.new_int(bins)

        step: Series = (max - min) / bins

        start = bar_index + offset

        __block_result__ = na
        if barstate.islast:
            if array.size(boxes) >= 0:
                for b in boxes:
                    box.delete(b)

            for g in pine_range(0, bins - 1):
                array.set(bin, g, 0)

            for l in pine_range(0, loockback):
                c = close[l]
                a = __hist_avg__[l]

                mi = min[l]

                s = step[l]

                for i in pine_range(0, array.size(bin) - 1):
                    lower = mi + s * i
                    upper = lower + s

                    if c >= lower - s and c <= upper + s:
                        array.set(bin, i, array.get(bin, i) + 1)

            for j in pine_range(0, array.size(bin) - 1):
                val = array.get(bin, j)

                lower = min + step * j
                upper = lower + step

                col = color.from_gradient(val, 0, array.max(bin), color.new(chart.fg_color, 80), avg_color)

                array.push(boxes, box.new(start - val, upper, start, lower, bgcolor=col, border_color=chart.fg_color if val == 0 else chart.bg_color))

            __block_result__ = label.delete(inline_series(label.new(start, max, string.tostring(loockback), textcolor=chart.fg_color, color=color.new(avg_color, 80), tooltip=string.tostring(loockback) + ' bars back beginnig of the trend'), 1))
        return __block_result__

    def draw_stdv(src, mult, mid = False):
        __block_result_1__ = na
        if barstate.islast:
            if mid:
                line.delete(inline_series(line.new(bar_index, avg, bar_index + 5, avg, color=avg_color, width=2), 1))

            line.delete(inline_series(line.new(bar_index, src, bar_index + 5, src, color=chart.fg_color, width=2), 1))
            __block_result_1__ = label.delete(inline_series(label.new(bar_index + 5, src, color=color.new(chart.fg_color, 100), textcolor=chart.fg_color, text=mult, style=label.style_label_left), 1))
        return __block_result_1__

    draw_stdv(stdv1, '+1', True)
    draw_stdv(stdv2, '+2')
    draw_stdv(stdv3, '+3')

    draw_stdv(stdv_1, '-1')
    draw_stdv(stdv_2, '-2')
    draw_stdv(stdv_3, '-3')

    if show_tp:
        profile(min, max)

    plot(avg, color=avg_color, linewidth=3)

    plotshape(avg if trend != trend[1] and trend else na, 'Up', shape.circle, location.absolute, size=size.tiny, color=col_up)
    plotshape(avg if trend != trend[1] and trend else na, 'Up', shape.circle, location.absolute, size=size.small, color=color.new(col_up, 50))

    plotshape(avg if trend != trend[1] and (not trend) else na, 'Down', shape.circle, location.absolute, size=size.tiny, color=col_dn)
    plotshape(avg if trend != trend[1] and (not trend) else na, 'Down', shape.circle, location.absolute, size=size.small, color=color.new(col_dn, 50))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)