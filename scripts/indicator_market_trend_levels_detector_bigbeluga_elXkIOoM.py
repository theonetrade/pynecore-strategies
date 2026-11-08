"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    array, bar_index, barstate, chart, close, color, display, fill, high,
    input, label, line, location, low, na, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Color, Line, NA, Persistent, Series


@script.indicator("Market Trend Levels Detector [BigBeluga]", overlay=True, max_lines_count=500)
def main(
    length1=input.int(12, "Fast", group="Trend"),
    length2=input.int(25, "Slow", group="Trend"),
    extend__ren__=input.bool(False, "Extend Lines", group="Levels"),
    qty=input.int(50, "Display Last", group="Levels"),
    col1=input.color(color.new('#26BA9F'), "", inline="col", group="Color"),
    col2=input.color(color.new('#6626BA'), "", inline="col", group="Color")
):
    lines_up: Persistent[list[Line]] = array.new_line()
    lines_dn: Persistent[list[Line]] = array.new_line()

    ema1: Series[float] = ta.ema(close, length1)
    ema2: float = ta.ema(close, length2)
    diff: float = ema1 - ema2
    cross_up: bool = ta.crossover(ema1, ema2) and barstate.isconfirmed
    cross_dn: bool = ta.crossunder(ema1, ema2) and barstate.isconfirmed
    lowest: float = ta.lowest(length2)
    highest: float = ta.highest(length2)

    if cross_up:
        for i in pine_range(0, length2):
            if low[i] == lowest:
                index = bar_index - i
                array.push(lines_dn, line.new(index, lowest, index + 25, lowest, color=col1))
                label.new(index, lowest, '●', color=col1, style=label.style_label_up, textcolor=color.white, size=size.tiny)

    if cross_dn:
        for i in pine_range(0, length2):
            if high[i] == highest:
                index = bar_index - i
                array.push(lines_up, line.new(index, highest, index + 25, highest, color=col2))
                label.new(index, highest, '●', color=col2, style=label.style_label_down, textcolor=color.white, size=size.tiny)

    if extend__ren__:
        if array.size(lines_up) > 0:
            for i in pine_range(array.size(lines_up) - 1, 0):
                line_id = array.get(lines_up, i)
                method_call('set_x2', line_id, bar_index)

                if high > method_call('get_y2', line_id):
                    method_call('set_style', line_id, line.style_dotted)
                    array.set(lines_up, i, NA(Line))

        if array.size(lines_dn) > 0:
            for i in pine_range(array.size(lines_dn) - 1, 0):
                line_id = array.get(lines_dn, i)
                method_call('set_x2', line_id, bar_index)

                if low < method_call('get_y2', line_id):
                    method_call('set_style', line_id, line.style_dotted)
                    array.set(lines_dn, i, NA(Line))

    a_allLines: list[Line] = line.all
    if array.size(a_allLines) > qty:
        line.delete(array.shift(a_allLines))

    p1 = plot(ema1, 'Fast EMA', display=display.none, color=col1)
    p2 = plot(ema2, 'Slow EMA', display=display.none, color=col2)

    color1: Color = color.from_gradient(diff, 0, ta.highest(diff, 100), color.new(col1, 70), col1)
    color2: Color = color.from_gradient(diff, ta.lowest(diff, 100), 0, col2, color.new(col2, 70))

    fill(p1, p2, color1 if ema1 > ema2 else color2)
    plotshape(ema1[1] if cross_up or cross_dn else na, 'Signal', shape.xcross, location.absolute, offset=-1, color=chart.fg_color)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
