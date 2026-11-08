"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    array, bar_index, chart, close, color, display, fill, high, hline, input,
    label, line, linefill, low, na, plot, script, string, ta
)
from pynecore.types import Color, Label, Line, NA, Persistent, PersistentSeries, Series


@script.indicator("Momentum Shift [Bigbeluga]", max_labels_count=500, max_lines_count=500)
def main(
    length=input.int(50, "Length", group="Momentum", inline="mom"),
    smooth=input.int(50, "Smooth", group="Momentum", inline="mom"),
    mult_dist=input.float(1, step=0.1, title="Shift Zone Size"),
    col_u=input.color(color.new('#3AD79B'), "", inline="ccc"),
    col_d=input.color(color.new('#FB6B2E'), "", inline="ccc")
):
    lines_up: Persistent[list[Line]] = array.new_line()
    lines_dn: Persistent[list[Line]] = array.new_line()
    labels: Persistent[list[Label]] = array.new_label()

    mom: Series = ta.hma(close - close[length], smooth)
    high_ = ta.highest(mom, 150)
    low_ = ta.lowest(mom, 150)

    colorM: Color = color.from_gradient(mom, low_, high_, col_d, col_u)

    rising: bool = ta.crossover(mom, mom[2])
    falling: bool = ta.crossunder(mom, mom[2])

    dist: float = ta.sma(high - low, 100) * mult_dist

    def draw_lbl(x, y, txt, col):
        lbl: PersistentSeries = NA(Label)

        lbl = label.new(x, y, txt, color=NA(Color), style=label.style_label_right, textcolor=col, force_overlay=True)

        label.delete(lbl[1])
        return array.push(labels, lbl)

    if rising:
        label.new(bar_index, low, '▲', color=NA(Color), textcolor=color.new(col_u, 50), style=label.style_label_up, force_overlay=True)

        if mom < 0:
            label.new(bar_index, mom, '▲', color=NA(Color), textcolor=col_u, style=label.style_label_up, force_overlay=False)
            label.new(bar_index, low, '△', color=NA(Color), textcolor=col_u, style=label.style_label_up, force_overlay=True)

        if array.size(lines_dn) > 0:
            for i in pine_range(0, array.size(lines_dn) - 1):
                line_id = array.get(lines_dn, i)

                line.delete(line_id)

        array.clear(lines_dn)

        for i in pine_range(0, 5):
            array.push(lines_up, line.new(bar_index + i * 3, high + dist * i, bar_index + 15 + i * 3, high + dist * i, force_overlay=True, color=color.new(col_u, 60 - 10 * i)))

            if i > 0:
                draw_lbl(bar_index + i * 3, high + dist * i, string.tostring(i), color.new(col_u, 60 - 10 * i))

    if falling:
        label.new(bar_index, high, '▼', color=NA(Color), textcolor=color.new(col_d, 50), style=label.style_label_down, force_overlay=True)

        if mom > 0:
            label.new(bar_index, mom, '▼', color=NA(Color), textcolor=col_d, style=label.style_label_down, force_overlay=False)
            label.new(bar_index, high, '▽', color=NA(Color), textcolor=col_d, style=label.style_label_down, force_overlay=True)

        if array.size(lines_up) > 0:
            for i in pine_range(0, array.size(lines_up) - 1):
                line_id = array.get(lines_up, i)

                line.delete(line_id)

        array.clear(lines_up)

        for i in pine_range(0, 5):
            array.push(lines_dn, line.new(bar_index + i * 3, low - dist * i, bar_index + 15 + i * 3, low - dist * i, force_overlay=True, color=color.new(col_d, 60 - 10 * i)))
            if i > 0:
                draw_lbl(bar_index + i * 3, low - dist * i, string.tostring(i), color.new(col_d, 60 - 10 * i))

    if array.size(lines_up) > 0:
        for i in pine_range(0, array.size(lines_up) - 1):
            line_id = array.get(lines_up, i)
            line_id1 = array.get(lines_up, i + 1 if i < array.size(lines_up) - 1 else i)

            line.set_x2(line_id, bar_index + 5 + i * 3)

            linefill.new(line_id, line_id1, color.new(col_u, 90 - i * 5))

            if high >= method_call('get_y2', line_id):
                line.set_x2(line_id, bar_index)
                array.set(lines_up, i, NA(Line))

    if array.size(lines_dn) > 0:
        for i in pine_range(0, array.size(lines_dn) - 1):
            line_id = array.get(lines_dn, i)
            line_id1 = array.get(lines_dn, i + 1 if i < array.size(lines_dn) - 1 else i)

            line.set_x2(line_id, bar_index + 5 + i * 3)

            linefill.new(line_id, line_id1, color.new(col_d, 90 - i * 5))

            if low <= method_call('get_y2', line_id):
                line.set_x2(line_id, bar_index)
                array.set(lines_dn, i, NA(Line))

    if array.size(labels) > 5:
        label.delete(array.shift(labels))

    hline(0)
    pm = plot(mom, color=chart.fg_color)
    p0 = plot(0, display=display.none)

    fill(pm, p0, high_, low_, colorM if mom > 0 else na, na)
    fill(pm, p0, high_, low_, na, colorM if mom < 0 else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
