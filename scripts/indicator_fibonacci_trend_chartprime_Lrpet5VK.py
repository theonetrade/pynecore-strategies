"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    bar_index, chart, color, display, fill, high, hl2, input, label, line,
    linefill, low, na, plot, script, string, ta
)
from pynecore.types import Label, Line, NA, Persistent, PersistentSeries, Series


@udt
class data:
    fib05: Line = na(Line)
    fib0: Line = na(Line)
    fib236: Line = na(Line)
    fib382: Line = na(Line)
    fib618: Line = na(Line)
    fib786: Line = na(Line)
    fib_: Line = na(Line)
    fib_di: Line = na(Line)

    H: Label = na(Label)
    L: Label = na(Label)

    L0: Label = na(Label)
    L236: Label = na(Label)
    L382: Label = na(Label)
    L618: Label = na(Label)
    L786: Label = na(Label)
    L_: Label = na(Label)


@script.indicator("Fibonacci Trend [ChartPrime]", overlay=True, max_lines_count=500)
def main(
    trend_on=input.bool(True, "", inline="trend", group="Trend"),
    trend_=input.float(4, "Trend", step=0.01, inline="trend", group="Trend"),
    col1=input.color(color.new('#26905D'), "", inline="trend", group="Trend"),
    col2=input.color(color.new('#74286D'), "", inline="trend", group="Trend"),
    extend__ren__=input.int(15, "Extend", group="Fibonacci", inline="1"),
    fill_col=input.color(color.new('#2689901C'), "", group="Fibonacci", inline="1"),
    __input_6__=input.float(0.236, "1"),
    __input_7__=input.float(0.382, "2"),
    __input_8__=input.float(0.618, "3"),
    __input_9__=input.float(0.786, "4")
):
    v_236: float = __input_6__ * 100
    v_382: float = __input_7__ * 100
    v_618: float = __input_8__ * 100
    v_786: float = __input_9__ * 100

    fib_d: PersistentSeries[data] = data()

    direction: Series
    supertrend, direction = ta.supertrend(trend_, 25)

    def draw_fibb(trend: Series):
        __hist_fib_d__: Series[data] = fib_d[0]
        h: Persistent = NA(float)
        l: Persistent = NA(float)
        hi: Persistent = NA(int)
        li: Persistent = NA(int)

        val_0: Persistent = NA(float)
        val_: Persistent = NA(float)

        atr = ta.atr(200)

        if trend != trend[1]:
            line.delete(fib_d.fib_)
            line.delete(fib_d.fib0)
            line.delete(fib_d.fib05)
            line.delete(fib_d.fib_di)
            line.delete(fib_d.fib236)
            line.delete(fib_d.fib382)
            line.delete(fib_d.fib618)
            line.delete(fib_d.fib786)
            label.delete(fib_d.H)
            label.delete(fib_d.L)
            label.delete(fib_d.L0)
            label.delete(fib_d.L_)
            label.delete(fib_d.L236)
            label.delete(fib_d.L382)
            label.delete(fib_d.L618)
            label.delete(fib_d.L786)

        if trend != trend[1] and trend == -1:
            fib_d.fib_ = line.new(bar_index, low, bar_index, low, color=chart.fg_color, width=2)
            fib_d.fib0 = line.new(bar_index, high + atr * 3, bar_index, high + atr * 3, color=chart.fg_color, width=2)

        if trend != trend[1] and trend == 1:
            fib_d.fib_ = line.new(bar_index, high, bar_index, high, color=chart.fg_color, width=2)
            fib_d.fib0 = line.new(bar_index, low - atr * 3, bar_index, low - atr * 3, color=chart.fg_color, width=2)

            fib_d.fib_di = line.new(li, l, hi, h, style=line.style_dashed, color=chart.fg_color)

        __block_result__ = na
        if trend == trend[1]:
            if low < line.get_y1(fib_d.fib_):
                line.set_y1(fib_d.fib_, low)
                line.set_y2(fib_d.fib_, low)

            if high > line.get_y1(fib_d.fib0):
                line.set_y1(fib_d.fib0, high)
                line.set_y2(fib_d.fib0, high)

            if high == line.get_y1(fib_d.fib0):
                h = high
                hi = bar_index
                label.delete(__hist_fib_d__[1].H)
                fib_d.H = label.new(hi, h, string.tostring(h, '#,###.####'), color=color.new('#15373B'))

            if low == line.get_y1(fib_d.fib_):
                l = low
                li = bar_index
                label.delete(__hist_fib_d__[1].L)
                fib_d.L = label.new(li, l, string.tostring(l, '#,###.####'), style=label.style_label_up, color=color.new('#15373B'))

            line.set_x2(fib_d.fib_, bar_index + extend__ren__)
            line.set_x2(fib_d.fib0, bar_index + extend__ren__)

            line.delete(__hist_fib_d__[1].fib_di)
            fib_d.fib_di = line.new(li, l, hi, h, style=line.style_dashed, color=chart.fg_color)

            if line.get_x1(fib_d.fib_di) < line.get_x1(fib_d.fib0) or line.get_x2(fib_d.fib_di) < line.get_x1(fib_d.fib0):
                line.delete(fib_d.fib_di)

            size_step = (line.get_y1(fib_d.fib0) - line.get_y1(fib_d.fib_)) / 100

            line.delete(__hist_fib_d__[1].fib05)
            line.delete(__hist_fib_d__[1].fib382)
            line.delete(__hist_fib_d__[1].fib236)
            line.delete(__hist_fib_d__[1].fib618)
            line.delete(__hist_fib_d__[1].fib786)

            if trend == -1:
                val_0 = line.get_y1(fib_d.fib0)
                val_ = line.get_y1(fib_d.fib_)

            if trend == 1:
                val_0 = line.get_y1(fib_d.fib_)
                val_ = line.get_y1(fib_d.fib0)

            fib_d.fib236 = line.new(line.get_x1(fib_d.fib0), val_0 - size_step * v_236 * trend * -1, line.get_x2(fib_d.fib0), val_0 - size_step * v_236 * trend * -1, color=chart.fg_color)
            fib_d.fib382 = line.new(line.get_x1(fib_d.fib0), val_0 - size_step * v_382 * trend * -1, line.get_x2(fib_d.fib0), val_0 - size_step * v_382 * trend * -1, color=chart.fg_color)

            fib_d.fib05 = line.new(line.get_x1(fib_d.fib0), val_0 - size_step * 50 * trend * -1, line.get_x2(fib_d.fib0), val_0 - size_step * 50 * trend * -1, color=color.new(chart.fg_color, 50), style=line.style_dotted)

            fib_d.fib618 = line.new(line.get_x1(fib_d.fib0), val_0 - size_step * v_618 * trend * -1, line.get_x2(fib_d.fib0), val_0 - size_step * v_618 * trend * -1, color=chart.fg_color)
            fib_d.fib786 = line.new(line.get_x1(fib_d.fib0), val_0 - size_step * v_786 * trend * -1, line.get_x2(fib_d.fib0), val_0 - size_step * v_786 * trend * -1, color=chart.fg_color)

            label.delete(__hist_fib_d__[1].L0)
            label.delete(__hist_fib_d__[1].L_)
            label.delete(__hist_fib_d__[1].L236)
            label.delete(__hist_fib_d__[1].L382)
            label.delete(__hist_fib_d__[1].L618)
            label.delete(__hist_fib_d__[1].L786)

            fib_d.L0 = label.new(bar_index + extend__ren__, val_0, text='0 ' + string.tostring(val_0, '(#,###.####)'), textcolor=chart.fg_color, color=chart.bg_color, style=label.style_label_left)
            fib_d.L_ = label.new(bar_index + extend__ren__, val_, text='1 ' + string.tostring(val_, '(#,###.####)'), textcolor=chart.fg_color, color=chart.bg_color, style=label.style_label_left)

            fib_d.L236 = label.new(bar_index + extend__ren__, line.get_y1(fib_d.fib236), text=string.tostring(v_236 / 100) + string.tostring(line.get_y1(fib_d.fib236), ' (#,###.####)'), textcolor=chart.fg_color, color=chart.bg_color, style=label.style_label_left)
            fib_d.L382 = label.new(bar_index + extend__ren__, line.get_y1(fib_d.fib382), text=string.tostring(v_382 / 100) + string.tostring(line.get_y1(fib_d.fib382), ' (#,###.####)'), textcolor=chart.fg_color, color=chart.bg_color, style=label.style_label_left)
            fib_d.L618 = label.new(bar_index + extend__ren__, line.get_y1(fib_d.fib618), text=string.tostring(v_618 / 100) + string.tostring(line.get_y1(fib_d.fib618), ' (#,###.####)'), textcolor=chart.fg_color, color=chart.bg_color, style=label.style_label_left)
            fib_d.L786 = label.new(bar_index + extend__ren__, line.get_y1(fib_d.fib786), text=string.tostring(v_786 / 100) + string.tostring(line.get_y1(fib_d.fib786), ' (#,###.####)'), textcolor=chart.fg_color, color=chart.bg_color, style=label.style_label_left)

            linefill.new(fib_d.fib618, fib_d.fib786, fill_col)
            __block_result__ = linefill.new(fib_d.fib05, fib_d.fib786, fill_col)
        return __block_result__

    draw_fibb(direction)

    color__ren__ = (col2 if direction == 1 else col1) if trend_on else na
    p1 = plot(supertrend, 'Trend', color=na if direction != direction[1] else color__ren__, style=plot.style_linebr)
    p2 = plot(hl2, display=display.none)

    fill(p1, p2, hl2, supertrend, na, na if direction != direction[1] else color.new(color__ren__, 90))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
