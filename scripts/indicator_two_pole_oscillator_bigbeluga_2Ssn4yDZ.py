"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    bar_index, barstate, chart, close, color, display, fill, high, input,
    label, line, location, low, na, plot, plotshape, script, shape, size, string, ta
)
from pynecore.types import Color, Line, NA, Persistent, Series


@script.indicator("Two-Pole Oscillator [BigBeluga]", max_labels_count=500, max_lines_count=500)
def main(
    length=input.int(15, minval=1, title="Filter Length"),
    disp_lvl=input.bool(True, "Levels"),
    up_color=input.color(color.new('#55FFDA'), "", inline="color"),
    dn_color=input.color(color.new('#8C5BFF'), "", inline="color")
):
    buy_line: Persistent = NA(Line)
    sell_line: Persistent = NA(Line)

    sma1: float = ta.sma(close, 25)
    sma_n1: float = (close - sma1 - ta.sma(close - sma1, 25)) / ta.stdev(close - sma1, 25)
    area: float = ta.sma(high - low, 100)

    def f_two_pole_filter(source, length):
        smooth1: Persistent[float] = na(float)
        smooth2: Persistent[float] = na(float)
        alpha = 2.0 / (length + 1)

        if na(smooth1):
            smooth1 = source
        else:
            smooth1 = (1 - alpha) * smooth1 + alpha * source

        __block_result__ = na
        if na(smooth2):
            smooth2 = smooth1
            __block_result__ = smooth2
        else:
            smooth2 = (1 - alpha) * smooth2 + alpha * smooth1
            __block_result__ = smooth2
        return __block_result__

    two_p: Series = f_two_pole_filter(sma_n1, length)
    two_pp = two_p[4]

    buy_col1: Color = color.from_gradient(two_p, -1, 0.5, up_color, na)
    buy_col2: Color = color.from_gradient(two_p, -1, 0.5, color.new(up_color, 50), na)
    sell_col1: Color = color.from_gradient(two_p, -0.5, 1, na, dn_color)
    sell_col2: Color = color.from_gradient(two_p, -0.5, 1, na, color.new(dn_color, 50))
    color__ren__: Color = color.from_gradient(two_p, -1, 1, up_color, color.new(up_color, 0)) if two_p > two_pp else color.from_gradient(two_p, -1, 1, color.new(dn_color, 0), dn_color)

    buy: bool = ta.crossover(two_p, two_pp) and two_p < 0 and barstate.isconfirmed
    sell: bool = ta.crossunder(two_p, two_pp) and two_p > 0 and barstate.isconfirmed

    if buy:
        sell_line = NA(Line)

        if disp_lvl:
            buy_line = line.new(bar_index, low - area, bar_index, low - area, force_overlay=True, color=buy_col1, style=line.style_dashed)

        label.new(bar_index, low - area, color=buy_col1, style=label.style_label_up, force_overlay=True, size=size.tiny)

        label.new(bar_index, low - area * 1.5, color=color.new(color.black, 100), text=string.tostring(low - area), style=label.style_label_up, force_overlay=True, size=size.small, textcolor=color.new(chart.fg_color, 30))

    if ta.crossunder(low, method_call('get_y1', buy_line)) and barstate.isconfirmed:
        label.new(bar_index, method_call('get_y1', buy_line), color=color.new(up_color, 100), style=label.style_label_center, force_overlay=True, size=size.large, text='✖', textcolor=up_color)

        buy_line = NA(Line)

    if sell:
        buy_line = NA(Line)
        if disp_lvl:
            sell_line = line.new(bar_index, high + area, bar_index, high + area, force_overlay=True, color=sell_col1, style=line.style_dashed)

        label.new(bar_index, high + area, color=sell_col1, style=label.style_label_down, force_overlay=True, size=size.tiny)

        label.new(bar_index, high + area * 1.5, color=color.new(color.black, 100), text=string.tostring(high + area), style=label.style_label_down, force_overlay=True, size=size.small, textcolor=color.new(chart.fg_color, 30))

    if ta.crossover(high, method_call('get_y1', sell_line)) and barstate.isconfirmed:
        label.new(bar_index, method_call('get_y1', sell_line), color=color.new(dn_color, 100), style=label.style_label_center, force_overlay=True, size=size.large, text='✖', textcolor=dn_color)

        sell_line = NA(Line)

    if not na(buy_line):
        method_call('set_x2', buy_line, bar_index)
    elif not na(sell_line):
        method_call('set_x2', sell_line, bar_index)

    plotshape(two_p if buy else na, 'Buy', shape.circle, location.absolute, buy_col2, 0, size=size.small)
    plotshape(two_p if buy else na, 'Buy', shape.circle, location.absolute, buy_col1, 0, size=size.tiny)

    plotshape(two_p if sell else na, 'Sell', shape.circle, location.absolute, sell_col2, 0, size=size.small)
    plotshape(two_p if sell else na, 'Sell', shape.circle, location.absolute, sell_col1, 0, size=size.tiny)

    p11 = plot(1, color=color.new(chart.fg_color, 80))
    plot(0.5, color=color.new(chart.fg_color, 50))
    p00 = plot(0, color=color.new(chart.fg_color if bar_index % 2 == 0 else na, 0))
    plot(-0.5, color=color.new(chart.fg_color, 50))
    p_1 = plot(-1, color=color.new(chart.fg_color, 80))

    fill(p11, p00, 2, -1, color.new(chart.fg_color, 80), na)
    fill(p_1, p00, 1, -2, na, color.new(chart.fg_color, 80))

    p1 = plot(two_p, color=color__ren__, linewidth=1)
    p2 = plot(two_pp, display=display.none)

    fill(p1, p2, two_p, two_pp, color__ren__, na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
