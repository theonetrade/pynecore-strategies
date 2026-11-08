"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barstate, chart, close, color, display, fill, high,
    hl2, input, label, line, linefill, location, low, math, na, open, plot, plotcandle, plotshape,
    script, shape, size, string, ta
)
from pynecore.types import Color, Label, Line, Persistent, PersistentSeries


@udt
class TrendTargets:
    lines: list[Line] = na(list)
    labels: list[Label] = na(list)


@script.indicator('Target Trend [BigBeluga]', overlay=True, max_lines_count=40, na_bool=True)
def main(
    length=input.int(10, 'Trend Length'),
    target=input.int(0, 'Set Targets')
):
    trend: PersistentSeries[bool] = na(bool)
    trend_value: float = na(float)
    up_color: Color = color.new('#06B690')
    dn_color: Color = color.rgb(182, 112, 6)
    atr_value: float = ta.sma(ta.atr(200), 200) * 0.8
    sma_high: float = ta.sma(high, length) + atr_value
    sma_low: float = ta.sma(low, length) - atr_value
    plot_color: Color = color.new(chart.fg_color, 80)
    targets_up: Persistent[TrendTargets] = TrendTargets(array.new_line(), array.new_label())
    targets_down: Persistent[TrendTargets] = TrendTargets(array.new_line(), array.new_label())
    if ta.crossover(close, sma_high) and barstate.isconfirmed:
        trend = True
    if ta.crossunder(close, sma_low) and barstate.isconfirmed:
        trend = False
    __block_result__ = na
    if trend:
        __block_result__ = sma_low
    elif not trend:
        __block_result__ = sma_high
    trend_value = __block_result__
    trend_color = up_color if trend else dn_color if not trend else na
    signal_up: bool = ta.change(trend) and (not trend[1])
    signal_down: bool = ta.change(trend) and trend[1]
    @method
    def draw_targets(targets: TrendTargets, signal1: bool, signal2: bool, direction: bool):
        base: float = sma_low if direction else sma_high
        atr_multiplier: float = atr_value * (1 if direction else -1)
        count_up: Persistent[int] = 0
        count_down: Persistent[int] = 0
        if trend:
            count_down = 0
            count_up = count_up + 1
        if not trend:
            count_down = count_down + 1
            count_up = 0
        count: int = count_up if direction else count_down
        if signal1:
            target_len1: float = atr_multiplier * (5 + target)
            target_len2: float = atr_multiplier * (10 + target * 2)
            target_len3: float = atr_multiplier * (15 + target * 3)
            for line_i in targets.lines:
                i: int = array.indexof(targets.lines, line_i)
                label.delete(array.get(targets.labels, i))
                line.delete(line_i)
            array.clear(targets.lines)
            array.clear(targets.labels)
            stop_loss_line: Line = line.new(bar_index, base, bar_index + 20, base)
            entry_line: Line = line.new(bar_index, close, bar_index + 20, close)
            target1_line: Line = line.new(bar_index, close + target_len1, bar_index + 20, close + target_len1)
            target2_line: Line = line.new(bar_index, close + target_len2, bar_index + 20, close + target_len2)
            target3_line: Line = line.new(bar_index, close + target_len3, bar_index + 20, close + target_len3)
            linefill.new(stop_loss_line, entry_line, color.new(dn_color, 95))
            linefill.new(entry_line, target3_line, color.new(up_color, 95))
            stop_loss_label: Label = label.new(bar_index + 20, base, string.tostring(math.round(base, 2)))
            entry_label: Label = label.new(bar_index + 20, close, string.tostring(math.round(close, 2)))
            target1_label: Label = label.new(bar_index + 20, close + target_len1, '１ - ' + string.tostring(math.round(close + target_len1, 2)))
            target2_label: Label = label.new(bar_index + 20, close + target_len2, '２ - ' + string.tostring(math.round(close + target_len2, 2)))
            target3_label: Label = label.new(bar_index + 20, close + target_len3, '３ - ' + string.tostring(math.round(close + target_len3, 2)))
            array.push(targets.lines, stop_loss_line)
            array.push(targets.lines, entry_line)
            array.push(targets.lines, target1_line)
            array.push(targets.lines, target2_line)
            array.push(targets.lines, target3_line)
            array.push(targets.labels, stop_loss_label)
            array.push(targets.labels, entry_label)
            array.push(targets.labels, target1_label)
            array.push(targets.labels, target2_label)
            array.push(targets.labels, target3_label)
            for lbl in targets.labels:
                idx: int = array.indexof(targets.labels, lbl)
                line_ref: Line = array.get(targets.lines, idx)
                label.set_style(lbl, label.style_label_left)
                label.set_color(lbl, chart.fg_color)
                label.set_textcolor(lbl, chart.bg_color)
                line.set_color(line_ref, chart.fg_color)
        if signal2:
            for line_i in targets.lines:
                i: int = array.indexof(targets.lines, line_i)
                label.delete(array.get(targets.labels, i))
                line.delete(line_i)
            array.clear(targets.lines)
            array.clear(targets.labels)
        __block_result_1__ = na
        for line_i in targets.lines:
            idx: int = array.indexof(targets.lines, line_i)
            lbl_ref: Label = array.get(targets.labels, idx)
            first_label: Label = array.first(targets.labels)
            entry_line: Line = array.get(targets.lines, 1)
            entry_label: Label = array.get(targets.labels, 1)
            if high >= line.get_y2(line_i) and low <= line.get_y2(line_i) and (count > 1):
                label.set_style(lbl_ref, label.style_label_left)
                label.set_color(lbl_ref, chart.fg_color)
                label.set_text(lbl_ref, '   ✔   ')
                label.set_textcolor(lbl_ref, color.new('#16AC09'))
                line.set_style(line_i, line.style_dashed)
                line.set_color(line_i, plot_color)
            if high >= line.get_y2(array.first(targets.lines)) and low <= line.get_y2(array.first(targets.lines)) and (count > 1):
                label.set_text(first_label, '  ✖  ')
            __block_result_2__ = na
            if trend if direction else not trend:
                label.set_textcolor(first_label, color.new('#DB1E1E'))
                line.set_x2(line_i, bar_index + 20)
                method_call('set_color', array.first(targets.lines), color.new('#DB1E1E'))
                label.set_x(array.get(targets.labels, idx), bar_index + 20)
                line.set_style(entry_line, line.style_solid)
                line.set_color(entry_line, up_color)
                label.set_text(entry_label, '◉ ' + string.tostring(math.round(line.get_y2(entry_line), 2)))
                __block_result_2__ = label.set_textcolor(entry_label, color.new('#1D80DD'))
            __block_result_1__ = __block_result_2__
        return __block_result_1__

    draw_targets(targets_down, signal_down, signal_up, False)
    draw_targets(targets_up, signal_up, signal_down, True)
    plotcandle(open, high, low, close, title='Title', color=trend_color, wickcolor=trend_color, bordercolor=trend_color)
    p1 = plot(trend_value if trend else na, style=plot.style_linebr, color=plot_color)
    p2 = plot(trend_value if not trend else na, style=plot.style_linebr, color=plot_color)
    p0 = plot(hl2, display=display.none, editable=False)
    fill(p1, p0, trend_value, hl2, color.new(chart.fg_color, 90), na)
    fill(p2, p0, trend_value, hl2, color.new(chart.fg_color, 90), na)
    sigUp: float = low - atr_value * 2 if signal_up else na
    sigDn: float = high + atr_value * 2 if signal_down else na
    plotshape(sigUp, '', shape.triangleup, location.absolute, up_color, size=size.tiny)
    plotshape(sigUp, '', shape.triangleup, location.absolute, color.new(up_color, 80), size=size.small)
    plotshape(sigDn, '', shape.triangledown, location.absolute, dn_color, size=size.tiny)
    plotshape(sigDn, '', shape.triangledown, location.absolute, color.new(dn_color, 80), size=size.small)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
