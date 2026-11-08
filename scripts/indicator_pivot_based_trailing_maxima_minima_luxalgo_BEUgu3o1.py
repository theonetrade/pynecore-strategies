"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    bar_index, barstate, color, fill, fixnan, high, input, line, linefill,
    location, low, math, na, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Persistent


@script.indicator('Pivot Based Trailing Maxima & Minima [LuxAlgo]', 'LuxAlgo - Pivot Based Trailing Maxima & Minima', overlay=True, max_bars_back=500, max_lines_count=500)
def main(
    length=input.int(24, minval=2, maxval=500),
    backpaint=input(False, tooltip='Backpainting offset displayed elements in the past. Disable backpainting to see real time information returned by the indicator.'),
    maxCss=input.color(color.teal, 'Trailing Maximum Color', group='Style'),
    minCss=input.color(color.red, 'Trailing Minimum Color', group='Style'),
    avgCss=input.color(color.new('#FF5D00'), 'Trailing Maximum Color', group='Style'),
    bullFill=input.color(color.new(color.teal, 80), 'Uptrend Area', group='Style'),
    bearFill=input.color(color.new(color.red, 80), 'Downtrend Area', group='Style')
):
    max: Persistent[float] = na(float)
    min: Persistent[float] = na(float)
    offset: Persistent = length if backpaint else 0
    ph = ta.pivothigh(length, length)
    pl = ta.pivotlow(length, length)
    if cast_bool(ph) or cast_bool(pl):
        max = high[length]
        min = low[length]
    max = math.max(high[offset], max)
    min = math.min(low[offset], min)
    avg = math.avg(max, min)
    n = bar_index
    max_prev = max
    min_prev = min
    avg_prev = avg
    max2 = max
    min2 = min
    fill_css = fixnan(bearFill if cast_bool(ph) else bullFill if cast_bool(pl) else na)
    if barstate.islast and backpaint:
        for line_object in line.all:
            line.delete(line_object)
        for i in pine_range(0, length - 1, 1):
            max2 = math.max(high[length - 1 - i], max_prev)
            min2 = math.min(low[length - 1 - i], min_prev)
            avg2 = math.avg(max2, min2)
            line1 = line.new(n - (length - i), max_prev, n - (length - 1 - i), max2, color=maxCss)
            line2 = line.new(n - (length - i), min_prev, n - (length - 1 - i), min2, color=minCss)
            linefill.new(line1, line2, color.new(fill_css, 80))
            line.new(n - (length - i), avg_prev, n - (length - 1 - i), avg2, color=avgCss)
            max_prev = max2
            min_prev = min2
            avg_prev = avg2
    plot1 = plot(max, 'Trailing Maximum', na if cast_bool(ph) or cast_bool(pl) else maxCss, 1, plot.style_linebr, offset=-offset)
    plot2 = plot(min, 'Trailing Minimum', na if cast_bool(ph) or cast_bool(pl) else minCss, 1, plot.style_linebr, offset=-offset)
    plot(avg, 'Average', na if cast_bool(ph) or cast_bool(pl) else avgCss, 1, plot.style_linebr, offset=-offset)
    fill(plot1, plot2, na if cast_bool(ph) or cast_bool(pl) else fill_css)
    plotshape(pl if cast_bool(pl) else na, 'Pivot High', shape.labelup, location.absolute, maxCss, -offset, text='▲', textcolor=color.white, size=size.tiny)
    plotshape(ph if cast_bool(ph) else na, 'Pivot Low', shape.labeldown, location.absolute, minCss, -offset, text='▼', textcolor=color.white, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
