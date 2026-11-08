"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barcolor, barstate, chart, close, color, high, input, label,
    low, math, na, open, plot, plotcandle, script, ta
)
from pynecore.types import NA, Persistent, PersistentSeries, Series


@script.indicator("Zone Shift [ChartPrime]", max_lines_count=500, overlay=True, max_labels_count=500)
def main(
    length=input.int(100, "Length 60-200", minval=60, maxval=200),
    upColor=input.color(color.lime, "", inline="colors"),
    dnColor=input.color(color.blue, "", inline="colors")
):
    trend: Persistent[bool] = False
    trendStart: PersistentSeries = NA(float)
    lastRetest: Persistent = bar_index

    ema: float = ta.ema(close, length)
    hma: float = ta.hma(close, length - 40)
    dist: float = ta.sma(high - low, 200)
    mid: float = math.avg(ema, hma)
    top: Series[float] = mid + dist
    bot: Series[float] = mid - dist

    if barstate.isconfirmed:
        if low > top and low[1] < top[1] and (not trend):
            trend = True
            trendStart = low

        if high < bot and high[1] > bot[1] and trend:
            trend = False
            trendStart = high

    trend_col = upColor if trend else dnColor

    if barstate.isconfirmed:
        if (close > trendStart and close[1] < trendStart[1] or (low > trendStart and low[1] < trendStart[1])) and trend and (bar_index - lastRetest > 5):
            lastRetest = bar_index
            label.new(bar_index, low, '⯁', color=color.new(color.black, 100), style=label.style_label_up, textcolor=trend_col)

        if (close[1] > trendStart and close < trendStart[1] or (high[1] > trendStart and high < trendStart[1])) and (not trend) and (bar_index - lastRetest > 5):
            lastRetest = bar_index
            label.new(bar_index, high, '⯁', color=color.new(color.black, 100), style=label.style_label_down, textcolor=trend_col)

    plot(mid, 'Middle', color=chart.fg_color if bar_index % 2 == 0 else na)
    plot(top, 'Top', color=chart.fg_color)
    plot(bot, 'Bottom', color=chart.fg_color)

    barcolor(trend_col)
    plotcandle(open, high, low, close, title='CandleColor', color=trend_col, wickcolor=trend_col, bordercolor=trend_col, force_overlay=True)

    plot(na if trendStart != trendStart[1] else trendStart, 'Trend Initiation Level', style=plot.style_linebr, color=chart.fg_color if bar_index % 2 == 0 else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
