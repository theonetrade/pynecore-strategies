"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    bar_index, chart, close, color, display, fill, format, high, hl2, input,
    label, line, low, math, na, open, plot, plotcandle, script, size, string, ta
)
from pynecore.types import Color, Line, NA, Persistent, PersistentSeries


@script.indicator('Market Structure Trend Targets [ChartPrime]', 'Market Structure TT [ChartPrime]', overlay=True, max_lines_count=500, max_labels_count=500, na_bool=True)
def main(
    length=input.int(10, 'Length', maxval=30, minval=2),
    display_per=input.bool(False, 'Display %'),
    display_stop=input.bool(True, 'Display Trailing Stop'),
    col_up=input.color(color.new('#54B6D4'), '+', inline='col'),
    col_dn=input.color(color.new('#CF3737'), '-', inline='col')
):
    ph: float = ta.pivothigh(length, length)
    pl: float = ta.pivotlow(length, length)
    def market_structure():
        upper: Persistent = NA(float)
        lower: Persistent = NA(float)
        upper_count: Persistent[int] = 0
        lower_count: Persistent[int] = 0
        upper_index: Persistent[int] = 0
        lower_index: Persistent[int] = 0
        trend: PersistentSeries = NA(bool)
        source: float = ta.sma(high - low, 50) * 2
        source1: float = ta.sma(ta.median(close, 40), 10)
        volatility: float = math.avg(ta.highest(source, 200), ta.lowest(source, 200))
        trend_line: float = NA(float)
        line_h: Persistent = NA(Line)
        line_l: Persistent = NA(Line)
        if not na(ph):
            upper_index = bar_index[length]
            upper = high[length]
            line_h = line.new(upper_index, upper, upper_index, upper, color=col_up)
        if not na(pl):
            lower_index = bar_index[length]
            lower = low[length]
            line_l = line.new(lower_index, lower, lower_index, lower, color=col_dn)
        if ta.crossover(high, upper):
            upper_count = upper_count + 1
            price_enter: Persistent[float] = 0.0
            index: int = bar_index - (bar_index - upper_index) / 2
            if upper_count == 1:
                price_enter = method_call('get_y1', line_h)
            percent: float = (method_call('get_y1', line_h) - price_enter) / price_enter * 100
            txt: str = string.tostring(price_enter, '#.# △') if upper_count == 1 else string.tostring(percent, format.percent) if display_per else string.tostring(upper_count - 1)
            label.new(index, method_call('get_y1', line_h), txt, textcolor=chart.fg_color, color=NA(Color))
            method_call('set_x2', line_h, bar_index)
            line_h = na
            upper = na
            lower_count = 0
            trend = True
        if ta.crossunder(low, lower):
            lower_count = lower_count + 1
            price_enter: Persistent[float] = 0.0
            index: int = bar_index - (bar_index - lower_index) / 2
            if lower_count == 1:
                price_enter = method_call('get_y1', line_l)
            percent: float = (method_call('get_y1', line_l) - price_enter) / price_enter * 100
            txt: str = string.tostring(price_enter, '#.# ▽') if lower_count == 1 else string.tostring(percent, format.percent) if display_per else string.tostring(lower_count - 1)
            label.new(index, method_call('get_y1', line_l), txt, textcolor=chart.fg_color, color=NA(Color), style=label.style_label_up)
            method_call('set_x2', line_l, bar_index)
            line_l = na
            lower = na
            upper_count = 0
            trend = False
        if trend:
            trend_line = source1 - volatility
        else:
            trend_line = source1 + volatility
        color__ren__: Color = col_up if trend else col_dn
        crossover_1 = ta.crossover(low, trend_line)
        if trend and crossover_1 and display_stop and (not (trend and (not trend[1]))):
            label.new(bar_index[1], low[1], text='◈', style=label.style_label_up, textcolor=color__ren__, color=NA(Color))
        crossunder_1 = ta.crossunder(high, trend_line)
        if not trend and crossunder_1 and display_stop and (not (trend[1] and (not trend))):
            label.new(bar_index[1], high[1], text='◈', style=label.style_label_down, textcolor=color__ren__, color=NA(Color))
        if trend and (not trend[1]):
            label.new(bar_index, trend_line, text='△', textcolor=color__ren__, style=label.style_label_center, color=NA(Color), size=size.large)
        if not trend and trend[1]:
            label.new(bar_index, trend_line, text='▽', textcolor=color__ren__, style=label.style_label_center, color=NA(Color), size=size.large)
        return (color__ren__, trend_line, trend)

    color__ren__, trend_line, trend = market_structure()
    stop_loss: float = trend_line
    stop_loss = na if ta.change(trend) else na if high > stop_loss and (not trend) else na if low < stop_loss and trend else stop_loss
    display__ren__ = display.all if display_stop else display.none
    color1 = 90 if display_stop else 100
    sl = plot(stop_loss, style=plot.style_linebr, color=color__ren__, display=display__ren__)
    plot(stop_loss, style=plot.style_linebr, color=color.new(color__ren__, 80), linewidth=5, display=display__ren__)
    pp = plot(hl2, color=NA(Color))
    fill(sl, pp, stop_loss, hl2, color.new(color__ren__, color1), na)
    candle_col = color.new(color__ren__, 50)
    plotcandle(open, high, low, close, title='Candles Trend', color=candle_col, wickcolor=candle_col, bordercolor=candle_col)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
