"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    bar_index, barstate, chart, close, color, fill, format, high, input,
    label, line, low, math, na, open, plot, plotcandle, position, script, string, syminfo, ta,
    table
)
from pynecore.types import Label, Line, NA, Persistent, PersistentSeries


@script.indicator('Trend Levels [ChartPrime]', overlay=True, max_labels_count=500, na_bool=True)
def main(
    length=input.int(30),
    up_col=input.color(color.lime, 'Up Color'),
    dn_col=input.color(color.fuchsia, 'Down Color')
):
    bars: Persistent[int] = 0
    trend: PersistentSeries[bool] = na(bool)
    count_up: Persistent[int] = NA(int)
    count_dn: Persistent[int] = NA(int)
    l1: Persistent[float] = NA(float)
    h1: Persistent[float] = NA(float)
    m1: Persistent[float] = NA(float)
    label_upper: PersistentSeries[Label] = NA(Label)
    label_lower: PersistentSeries[Label] = NA(Label)
    label_mid: PersistentSeries[Label] = NA(Label)
    line_upper: PersistentSeries[Line] = NA(Line)
    line_lower: PersistentSeries[Line] = NA(Line)
    line_mid: PersistentSeries[Line] = NA(Line)
    h = ta.highest(length)
    l = ta.lowest(length)
    if h == high:
        trend = True
    if l == low:
        trend = False
    if trend:
        bars = bars + 1
        label_lower = label.new(bar_index + 10, l1, string.tostring(l1, '#.#'), color=dn_col, style=label.style_label_left)
        label_upper = label.new(bar_index + 10, h1, string.tostring(h1, '#.#'), color=up_col, style=label.style_label_left)
        label_mid = label.new(bar_index + 10, m1, string.tostring(m1, '#.#'), color=color.gray, style=label.style_label_left)
        label.delete(label_mid[1])
        label.delete(label_upper[1])
        label.delete(label_lower[1])
        line_upper = line.new(bar_index, h1, bar_index + 10, h1, color=up_col)
        line_mid = line.new(bar_index, m1, bar_index + 10, m1, color=color.gray, style=line.style_dashed)
        line_lower = line.new(bar_index, l1, bar_index + 10, l1, color=dn_col)
        line.delete(line_upper[1])
        line.delete(line_lower[1])
        line.delete(line_mid[1])
    if not trend:
        bars = bars + 1
        label_lower = label.new(bar_index + 10, l1, string.tostring(l1, '#.#'), color=dn_col, style=label.style_label_left)
        label_upper = label.new(bar_index + 10, h1, string.tostring(h1, '#.#'), color=up_col, style=label.style_label_left)
        label_mid = label.new(bar_index + 10, m1, string.tostring(m1, '#.#'), color=color.gray, style=label.style_label_left)
        label.delete(label_mid[1])
        label.delete(label_upper[1])
        label.delete(label_lower[1])
        line_upper = line.new(bar_index, h1, bar_index + 10, h1, color=up_col)
        line_mid = line.new(bar_index, m1, bar_index + 10, m1, color=color.gray, style=line.style_dashed)
        line_lower = line.new(bar_index, l1, bar_index + 10, l1, color=dn_col)
        line.delete(line_upper[1])
        line.delete(line_lower[1])
        line.delete(line_mid[1])
    if ta.change(trend):
        label.delete(label_lower)
        label.delete(label_mid)
        label.delete(label_upper)
        line.delete(line_upper)
        line.delete(line_lower)
        line.delete(line_mid)
        bars = 1
        count_up = 0
        count_dn = 0
    h1 = ta.highest(bars)
    l1 = ta.lowest(bars)
    m1 = math.avg(h1, l1)
    if bars == 1:
        h1 = na
        l1 = na
        m1 = na
    if close > m1:
        count_up = count_up + 1
    if close < m1:
        count_dn = count_dn + 1
    total = count_up + count_dn
    delta_percent = (count_up - count_dn) / total * 100
    if trend and (not trend[1]):
        label.new(bar_index, low, '⇗', color=up_col, style=label.style_label_upper_right)
    if trend[1] and (not trend):
        label.new(bar_index, high, '⇘', color=dn_col, style=label.style_label_lower_right)
    color__ren__ = color.from_gradient(delta_percent, -50, 50, dn_col, up_col)
    plotcandle(open, high, low, close, title='Candles', color=color__ren__, wickcolor=color__ren__, bordercolor=color__ren__)
    pl = plot(l1, color=dn_col, style=plot.style_linebr)
    ph = plot(h1, color=up_col, style=plot.style_linebr)
    pm = plot(m1, color=color.gray if bar_index % 3 == 0 else na, style=plot.style_linebr)
    fill(pm, ph, h1, m1, color.new(up_col, 90), na)
    fill(pm, pl, m1, l1, na, color.new(dn_col, 90))
    if barstate.islast:
        tbl: Persistent = table.new(position.top_right, 10, 10)
        method_call('cell', tbl, 0, 0, 'Symbol: ', text_color=chart.fg_color)
        method_call('cell', tbl, 1, 0, syminfo.basecurrency, text_color=color__ren__)
        method_call('cell', tbl, 0, 1, 'Trend: ', text_color=chart.fg_color)
        method_call('cell', tbl, 1, 1, string.tostring(delta_percent, format.percent), text_color=color__ren__)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
