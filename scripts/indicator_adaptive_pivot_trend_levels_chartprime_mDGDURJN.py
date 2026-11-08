"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barstate, chart, close, color, display, fill, high,
    input, label, line, low, na, plot, position, script, string, ta, table, text
)
from pynecore.types import Color, Label, Line, NA, Persistent, Series


@udt
class level:
    l: Line = na(Line)
    isBelow: bool = na(bool)
    count: Label = na(Label)


@script.indicator("Adaptive Pivot Trend Levels [ChartPrime]", overlay=True, max_lines_count=500)
def main(
    Length=input.int(5),
    actvLevels=input.bool(True, "Active", inline="c"),
    crossLevels=input.bool(True, "Crossed", inline="c"),
    colorUP=input.color(color.rgb(36, 224, 133), "", inline="color"),
    colorDN=input.color(color.rgb(230, 36, 165), "", inline="color")
):
    pivots: Persistent[list[float]] = array.new_float()
    levels: Persistent[list[level]] = array.new(0, NA(level))

    active: int = 0
    crossed: Persistent[int] = 0
    start: Persistent[int] = 0

    ph = ta.pivothigh(Length, Length)
    pl = ta.pivotlow(Length, Length)

    if not na(ph):
        l__00000014__ = line.new(bar_index - Length, ph, bar_index, ph)
        count__00000014__ = label.new(bar_index, ph, '', color=NA(Color), style=label.style_label_left)

        array.push(pivots, ph)
        array.push(levels, level(l__00000014__, False, count__00000014__))

    if not na(pl):
        l__0000001b__ = line.new(bar_index - Length, pl, bar_index, pl)
        count__0000001b__ = label.new(bar_index, ph, '', color=NA(Color), style=label.style_label_left)

        array.push(pivots, pl)
        array.push(levels, level(l__0000001b__, True, count__0000001b__))

    if array.size(pivots) > 10:
        array.shift(pivots)

    trendLine = array.avg(pivots)

    Uptrend = low >= trendLine
    Dntrend = high <= trendLine
    TColor: Series = colorUP if Uptrend else colorDN if Dntrend else color.gray

    upTrend = TColor == colorUP or (TColor == color.gray and TColor[1] == colorUP and (TColor[2] == colorUP))
    dnTrend = TColor == colorDN or (TColor == color.gray and TColor[1] == colorDN and (TColor[2] == colorDN))

    upChange = ta.change(upTrend)
    dnChange = ta.change(dnTrend)

    TrendChange = upChange or dnChange

    if TrendChange:
        crossed = 0
        start = bar_index

    if not TrendChange:
        for i in levels:
            if start > line.get_x2(i.l):
                line.delete(i.l)
                label.delete(i.count)

                array.remove(levels, array.indexof(levels, i))
            else:
                active += 1

                line.set_x2(i.l, bar_index)
                line.set_color(i.l, color.new(TColor, 100))

                if actvLevels:
                    label.set_xy(i.count, bar_index, line.get_y1(i.l))

                    line.set_color(i.l, TColor)
                    line.set_style(i.l, line.style_dashed)

                    label.set_text(i.count, string.tostring(active))
                    label.set_textcolor(i.count, color.new(chart.fg_color, 60))

                if i.isBelow:
                    if low < line.get_y1(i.l):
                        crossed += 1
                        label.delete(i.count)

                        line.set_color(i.l, color.new(TColor, 50 if crossLevels else 100))
                        line.set_style(i.l, line.style_dotted)
                        array.remove(levels, array.indexof(levels, i))
                else:
                    if high > line.get_y1(i.l):
                        crossed += 1
                        label.delete(i.count)
                        line.set_color(i.l, color.new(TColor, 50 if crossLevels else 100))
                        line.set_style(i.l, line.style_dotted)
                        array.remove(levels, array.indexof(levels, i))

    tbl: Persistent = table.new(position.top_right, 100, 100, chart.bg_color)

    if barstate.islast:
        method_call('cell', tbl, 0, 0, 'Trend', text_halign=text.align_left, text_color=chart.fg_color)
        method_call('cell', tbl, 1, 0, '↑' if upTrend else '↓' if Dntrend else '-', text_color=TColor)

        method_call('cell', tbl, 0, 1, 'Active Levels', text_halign=text.align_left, text_color=chart.fg_color)
        method_call('cell', tbl, 1, 1, string.tostring(active), text_color=TColor)

        method_call('cell', tbl, 0, 2, 'Crossed Levels', text_halign=text.align_left, text_color=chart.fg_color)
        method_call('cell', tbl, 1, 2, string.tostring(crossed), text_color=TColor)

    pt = plot(trendLine, 'Trend Line', style=plot.style_stepline, color=TColor)
    plot(trendLine, 'Trend Line Shadow', style=plot.style_stepline, color=color.new(TColor, 70), linewidth=5)
    pc = plot(close, display=display.none, editable=False)

    fill(pc, pt, trendLine, close, NA(Color), color.new(TColor, 70))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)