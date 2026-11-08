"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alertcondition, array, bar_index, chart, close, color, fill, high, input,
    label, last_bar_index, line, linefill, location, low, math, na, plot, plotshape, script, shape,
    size, ta, yloc
)
from pynecore.types import Label, Line, LineFill, NA, Persistent, Series


@udt
class piv:
    b: int = na(int)
    p: float = na(float)
    d: int = na(int)


@udt
class fib:
    n0_382: Line = na(Line)
    _0_000: Line = na(Line)
    _0_236: Line = na(Line)
    _0_382: Line = na(Line)
    _0_500: Line = na(Line)
    _0_618: Line = na(Line)
    _0_764: Line = na(Line)
    _1_000: Line = na(Line)
    _1_382: Line = na(Line)
    diagon: Line = na(Line)
    lab1: Label = na(Label)
    lab2: Label = na(Label)
    active: bool = na(bool)
    count: int = na(int)


@udt
class fibLast:
    lf_0: LineFill = na(LineFill)
    lfM0: LineFill = na(LineFill)
    lfM1: LineFill = na(LineFill)
    lf_1: LineFill = na(LineFill)
    ln_0_5: Line = na(Line)
    diagon: Line = na(Line)
    lab: Label = na(Label)


z: str = '       '
y: str = '          '
x: str = '             '


@script.indicator('Fibonacci Ranges (Real-Time) [LuxAlgo]', shorttitle='LuxAlgo - Fibonacci Ranges (Real-Time)', max_lines_count=500, max_labels_count=500, overlay=True, na_bool=True)
def main(
    L=input.int(5, 'L', minval=1, group='Swing Settings'),
    R=input.int(1, 'R', minval=1, group='Swing Settings'),
    c_=input.string('Channel + Shadows', 'Channel', options=('Channel', 'Channel + Shadows', 'None'), group='Fibonacci Channel'),
    opt=input.string('0.000 - 1.000', 'Break level', group='Fibonacci Channel', options=('-0.382 - 1.382', '0.000 - 1.000', '0.236 - 0.764', '0.382 - 0.618')),
    c=input.int(2, 'Break count', minval=0, group='Fibonacci Channel'),
    sb=input.bool(True, z + x + 'Show breaks', group='Fibonacci Channel'),
    sF=input.bool(False, z + y + 'Latest Fibonacci', group='Fibonacci'),
    F0=input.color(color.new('#08998164'), '      ', inline='f', group='Fibonacci'),
    F_=input.color(color.new('#08998180'), '', inline='f', group='Fibonacci'),
    Fm=input.color(color.new('#1E42B070'), '', inline='f', group='Fibonacci'),
    Fp=input.color(color.new('#F2364580'), '', inline='f', group='Fibonacci'),
    F1=input.color(color.new('#F2364564'), '', inline='f', group='Fibonacci')
):
    Fc = True if c_ != 'None' else False
    fl = True if c_ == 'Channel + Shadows' else False
    n = bar_index
    pivs: Persistent[list[piv]] = array.new(0, NA(piv))
    f: Persistent[fib] = fib(n0_382=line.new(na, na, na, na, color=F0), _0_000=line.new(na, na, na, na, color=F0), _0_236=line.new(na, na, na, na, color=F_), _0_382=line.new(na, na, na, na, color=F_), _0_500=line.new(na, na, na, na, color=Fm), _0_618=line.new(na, na, na, na, color=Fp), _0_764=line.new(na, na, na, na, color=Fp), _1_000=line.new(na, na, na, na, color=F1), _1_382=line.new(na, na, na, na, color=F1), lab1=label.new(na, na, color=color.gray, style=label.style_label_center, yloc=yloc.price, size=size.tiny), lab2=label.new(na, na, color=color.gray, style=label.style_label_center, yloc=yloc.price, size=size.tiny), diagon=line.new(na, na, na, na, color=color.silver, style=line.style_dashed), active=False, count=0)
    fLast: Persistent[fibLast] = fibLast(lf_0=linefill.new(line.new(na, na, na, na, color=F0), line.new(na, na, na, na, color=F0), color.new(F0, 75)), lfM0=linefill.new(line.new(na, na, na, na, color=F_), line.new(na, na, na, na, color=F_), color.new(F_, 75)), lfM1=linefill.new(line.new(na, na, na, na, color=Fp), line.new(na, na, na, na, color=Fp), color.new(Fp, 75)), lf_1=linefill.new(line.new(na, na, na, na, color=F1), line.new(na, na, na, na, color=F1), color.new(F1, 75)), ln_0_5=line.new(na, na, na, na, color=color.blue), diagon=line.new(na, na, na, na, color=color.silver, style=line.style_dashed), lab=label.new(na, na, color=color.gray))
    ln: Persistent[Line] = line.new(na, na, na, na)
    brokeU: bool = False
    brokeD: bool = False
    ph = ta.pivothigh(L, R)
    pl = ta.pivotlow(L, R)
    __block_result__ = na
    __switch__ = opt
    if __switch__ == '-0.382 - 1.382':
        __block_result__ = -0.382
    elif __switch__ == '0.000 - 1.000':
        __block_result__ = 0
    elif __switch__ == '0.236 - 0.764':
        __block_result__ = 0.236
    elif __switch__ == '0.382 - 0.618':
        __block_result__ = 0.382
    a1 = __block_result__
    __block_result_1__ = na
    __switch__ = opt
    if __switch__ == '-0.382 - 1.382':
        __block_result_1__ = 1.382
    elif __switch__ == '0.000 - 1.000':
        __block_result_1__ = 1
    elif __switch__ == '0.236 - 0.764':
        __block_result_1__ = 0.764
    elif __switch__ == '0.382 - 0.618':
        __block_result_1__ = 0.618
    a2 = __block_result_1__
    if cast_bool(ph):
        if array.size(pivs) > 0:
            get = array.first(pivs)
            if get.d > 0 and ph > get.p:
                get.b = n - R
                get.p = high[R]
            if get.d < 0 and ph > get.p:
                array.unshift(pivs, piv(n - R, high[R], 1))
        else:
            array.unshift(pivs, piv(n - R, high[R], 1))
        if array.size(pivs) > 1 and (not f.active) and Fc:
            get1 = array.get(pivs, 1)
            idx1 = get1.b
            diff = high[R] - get1.p
            line.set_xy1(f.n0_382, n - R, high[R] + diff * 0.382)
            line.set_xy2(f.n0_382, n + 8, high[R] + diff * 0.382)
            line.set_xy1(f._0_000, n - R, high[R])
            line.set_xy2(f._0_000, n + 8, high[R])
            line.set_xy1(f._0_236, n - R, high[R] - diff * 0.236)
            line.set_xy2(f._0_236, n + 8, high[R] - diff * 0.236)
            line.set_xy1(f._0_382, n - R, high[R] - diff * 0.382)
            line.set_xy2(f._0_382, n + 8, high[R] - diff * 0.382)
            line.set_xy1(f._0_500, n - R, high[R] - diff * 0.5)
            line.set_xy2(f._0_500, n + 8, high[R] - diff * 0.5)
            line.set_xy1(f._0_618, n - R, high[R] - diff * 0.618)
            line.set_xy2(f._0_618, n + 8, high[R] - diff * 0.618)
            line.set_xy1(f._0_764, n - R, high[R] - diff * 0.764)
            line.set_xy2(f._0_764, n + 8, high[R] - diff * 0.764)
            line.set_xy1(f._1_000, n - R, get1.p)
            line.set_xy2(f._1_000, n + 8, get1.p)
            line.set_xy1(f._1_382, n - R, get1.p - diff * 0.382)
            line.set_xy2(f._1_382, n + 8, get1.p - diff * 0.382)
            label.set_xy(f.lab1, n + 8, high[R] - diff * a1)
            label.set_xy(f.lab2, n + 8, high[R] - diff * a2)
            line.set_xy1(f.diagon, idx1, get1.p)
            line.set_xy2(f.diagon, n - R, high[R])
            f.active = True
    if cast_bool(pl):
        if array.size(pivs) > 0:
            get = array.first(pivs)
            if get.d < 0 and pl < get.p:
                get.b = n - R
                get.p = low[R]
            if get.d > 0 and pl < get.p:
                array.unshift(pivs, piv(n - R, low[R], -1))
        else:
            array.unshift(pivs, piv(n - R, low[R], -1))
        if array.size(pivs) > 1 and (not f.active) and Fc:
            get1 = array.get(pivs, 1)
            idx1 = get1.b
            diff = get1.p - low[R]
            line.set_xy1(f.n0_382, n - R, low[R] - diff * 0.382)
            line.set_xy2(f.n0_382, n + 8, low[R] - diff * 0.382)
            line.set_xy1(f._0_000, n - R, low[R])
            line.set_xy2(f._0_000, n + 8, low[R])
            line.set_xy1(f._0_236, n - R, low[R] + diff * 0.236)
            line.set_xy2(f._0_236, n + 8, low[R] + diff * 0.236)
            line.set_xy1(f._0_382, n - R, low[R] + diff * 0.382)
            line.set_xy2(f._0_382, n + 8, low[R] + diff * 0.382)
            line.set_xy1(f._0_500, n - R, low[R] + diff * 0.5)
            line.set_xy2(f._0_500, n + 8, low[R] + diff * 0.5)
            line.set_xy1(f._0_618, n - R, low[R] + diff * 0.618)
            line.set_xy2(f._0_618, n + 8, low[R] + diff * 0.618)
            line.set_xy1(f._0_764, n - R, low[R] + diff * 0.764)
            line.set_xy2(f._0_764, n + 8, low[R] + diff * 0.764)
            line.set_xy1(f._1_000, n - R, get1.p)
            line.set_xy2(f._1_000, n + 8, get1.p)
            line.set_xy1(f._1_382, n - R, get1.p + diff * 0.382)
            line.set_xy2(f._1_382, n + 8, get1.p + diff * 0.382)
            label.set_xy(f.lab1, n + 8, low[R] + diff * a1)
            label.set_xy(f.lab2, n + 8, low[R] + diff * a2)
            line.set_xy1(f.diagon, idx1, get1.p)
            line.set_xy2(f.diagon, n - R, low[R])
            f.active = True
    if array.size(pivs) >= 2:
        max = math.max(array.first(pivs).p, array.get(pivs, 1).p)
        min = math.min(array.first(pivs).p, array.get(pivs, 1).p)
        dif = max - min
        _0i = array.first(pivs).b
        _0p = array.first(pivs).p
        _1i = array.get(pivs, 1).b
        _1p = array.get(pivs, 1).p
        d = -dif if _0p < _1p else dif
        x2 = math.max(last_bar_index, _0i) + 8
        l0_1 = linefill.get_line1(fLast.lf_0)
        l0_2 = linefill.get_line2(fLast.lf_0)
        lM01 = linefill.get_line1(fLast.lfM0)
        lM02 = linefill.get_line2(fLast.lfM0)
        lM11 = linefill.get_line1(fLast.lfM1)
        lM12 = linefill.get_line2(fLast.lfM1)
        l1_1 = linefill.get_line1(fLast.lf_1)
        l1_2 = linefill.get_line2(fLast.lf_1)
        if (cast_bool(ph) or cast_bool(pl)) and sF:
            method_call('set_xy1', l0_1, _0i, _0p + d * 0.382)
            method_call('set_xy2', l0_1, x2, _0p + d * 0.382)
            method_call('set_xy1', l0_2, _0i, _0p)
            method_call('set_xy2', l0_2, x2, _0p)
            method_call('set_xy1', lM01, _0i, _0p - d * 0.236)
            method_call('set_xy2', lM01, x2, _0p - d * 0.236)
            method_call('set_xy1', lM02, _0i, _0p - d * 0.382)
            method_call('set_xy2', lM02, x2, _0p - d * 0.382)
            method_call('set_xy1', lM11, _0i, _0p - d * 0.618)
            method_call('set_xy2', lM11, x2, _0p - d * 0.618)
            method_call('set_xy1', lM12, _0i, _0p - d * 0.764)
            method_call('set_xy2', lM12, x2, _0p - d * 0.764)
            method_call('set_xy1', l1_1, _0i, _0p - d)
            method_call('set_xy2', l1_1, x2, _0p - d)
            method_call('set_xy1', l1_2, _0i, _1p - d * 0.382)
            method_call('set_xy2', l1_2, x2, _1p - d * 0.382)
            line.set_xy1(fLast.ln_0_5, _0i, _0p - d * 0.5)
            line.set_xy2(fLast.ln_0_5, x2, _0p - d * 0.5)
            line.set_xy1(fLast.diagon, _0i, _0p)
            line.set_xy2(fLast.diagon, _1i, _1p)
            label.set_xy(fLast.lab, _0i, _0p)
            label.set_style(fLast.lab, label.style_label_up if _1p > _0p else label.style_label_down)
        else:
            method_call('set_x2', l0_1, n + 8)
            method_call('set_x2', l0_2, n + 8)
            method_call('set_x2', lM01, n + 8)
            method_call('set_x2', lM02, n + 8)
            method_call('set_x2', lM11, n + 8)
            method_call('set_x2', lM12, n + 8)
            method_call('set_x2', l1_1, n + 8)
            method_call('set_x2', l1_2, n + 8)
            line.set_x2(fLast.ln_0_5, n + 8)
    if f.active:
        lv1 = f._0_000 if opt == '0.000 - 1.000' else f._0_236 if opt == '0.236 - 0.764' else f._0_382 if opt == '0.382 - 0.618' else f.n0_382
        lv2 = f._1_000 if opt == '0.000 - 1.000' else f._0_764 if opt == '0.236 - 0.764' else f._0_618 if opt == '0.382 - 0.618' else f._1_382
        max = math.max(method_call('get_y2', lv1), method_call('get_y2', lv2))
        min = math.min(method_call('get_y2', lv1), method_call('get_y2', lv2))
        if close < max and close > min:
            f.count = 0
        else:
            if close > max or close < min:
                f.count = f.count + 1
        if f.count > c:
            line.set_xy1(f.n0_382, na, na)
            line.set_xy2(f.n0_382, na, na)
            line.set_xy1(f._0_000, na, na)
            line.set_xy2(f._0_000, na, na)
            line.set_xy1(f._0_236, na, na)
            line.set_xy2(f._0_236, na, na)
            line.set_xy1(f._0_382, na, na)
            line.set_xy2(f._0_382, na, na)
            line.set_xy1(f._0_500, na, na)
            line.set_xy2(f._0_500, na, na)
            line.set_xy1(f._0_618, na, na)
            line.set_xy2(f._0_618, na, na)
            line.set_xy1(f._0_764, na, na)
            line.set_xy2(f._0_764, na, na)
            line.set_xy1(f._1_000, na, na)
            line.set_xy2(f._1_000, na, na)
            line.set_xy1(f._1_382, na, na)
            line.set_xy2(f._1_382, na, na)
            line.set_xy1(f.diagon, na, na)
            line.set_xy2(f.diagon, na, na)
            label.set_xy(f.lab1, na, na)
            label.set_xy(f.lab2, na, na)
            f.active = False
            if close > max:
                brokeU = True
            else:
                brokeD = True
        else:
            line.set_x2(f.n0_382, n + 8)
            line.set_x2(f._0_000, n + 8)
            line.set_x2(f._0_236, n + 8)
            line.set_x2(f._0_382, n + 8)
            line.set_x2(f._0_500, n + 8)
            line.set_x2(f._0_618, n + 8)
            line.set_x2(f._0_764, n + 8)
            line.set_x2(f._1_000, n + 8)
            line.set_x2(f._1_382, n + 8)
            label.set_x(f.lab1, n + 8)
            label.set_x(f.lab2, n + 8)
    plotn0_382 = line.get_y2(f.n0_382)
    plot_0_000 = line.get_y2(f._0_000)
    plot_0_236 = line.get_y2(f._0_236)
    plot_0_382 = line.get_y2(f._0_382)
    plot_0_500 = line.get_y2(f._0_500)
    plot_0_618 = line.get_y2(f._0_618)
    plot_0_764 = line.get_y2(f._0_764)
    plot_1_000 = line.get_y2(f._1_000)
    plot_1_382 = line.get_y2(f._1_382)
    ch = ta.change(plot_0_000)
    p1 = plot(na if cast_bool(ch) else plotn0_382, color=color.new(color.blue, 100), style=plot.style_steplinebr)
    p2 = plot(na if cast_bool(ch) else plot_0_000, color=color.new(color.blue, 100), style=plot.style_steplinebr)
    p3 = plot(na if cast_bool(ch) else plot_0_236, color=color.new(color.blue, 100), style=plot.style_steplinebr)
    p4 = plot(na if cast_bool(ch) else plot_0_382, color=color.new(color.blue, 100), style=plot.style_steplinebr)
    p5 = plot(na if cast_bool(ch) else plot_0_500, color=color.new(color.blue, 100), style=plot.style_steplinebr)
    p6 = plot(na if cast_bool(ch) else plot_0_618, color=color.new(color.blue, 100), style=plot.style_steplinebr)
    p7 = plot(na if cast_bool(ch) else plot_0_764, color=color.new(color.blue, 100), style=plot.style_steplinebr)
    p8 = plot(na if cast_bool(ch) else plot_1_000, color=color.new(color.blue, 100), style=plot.style_steplinebr)
    p9 = plot(na if cast_bool(ch) else plot_1_382, color=color.new(color.blue, 100), style=plot.style_steplinebr)
    fill(p1, p2, na if cast_bool(ch) or not fl else plot_0_000, math.avg(plotn0_382, plot_0_000), F0, color.new(chart.bg_color, 100))
    fill(p1, p2, na if cast_bool(ch) or not fl else plotn0_382, math.avg(plotn0_382, plot_0_000), F0, color.new(chart.bg_color, 100))
    fill(p3, p4, na if cast_bool(ch) or not fl else plot_0_236, math.avg(plot_0_382, math.avg(plot_0_382, plot_0_236)), F_, color.new(chart.bg_color, 100))
    fill(p3, p4, na if cast_bool(ch) or not fl else math.avg(plot_0_236, math.avg(plot_0_382, plot_0_236)), plot_0_382, color.new(chart.bg_color, 100), F_)
    fill(p4, p5, na if cast_bool(ch) or not fl else plot_0_382, plot_0_500, color.new(chart.bg_color, 100), Fm)
    fill(p5, p6, na if cast_bool(ch) or not fl else plot_0_500, plot_0_618, Fm, color.new(chart.bg_color, 100))
    fill(p6, p7, na if cast_bool(ch) or not fl else plot_0_764, math.avg(plot_0_618, math.avg(plot_0_618, plot_0_764)), Fp, color.new(chart.bg_color, 100))
    fill(p6, p7, na if cast_bool(ch) or not fl else math.avg(plot_0_764, math.avg(plot_0_618, plot_0_764)), plot_0_618, color.new(chart.bg_color, 100), Fp)
    fill(p8, p9, na if cast_bool(ch) or not fl else plot_1_000, math.avg(plot_1_382, plot_1_000), F1, color.new(chart.bg_color, 100))
    fill(p8, p9, na if cast_bool(ch) or not fl else plot_1_382, math.avg(plot_1_382, plot_1_000), F1, color.new(chart.bg_color, 100))
    field_0: Series[bool] = f.active
    plotshape(high if sb and brokeU and field_0[1] else na, location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.new('#089981'))
    field_1: Series[bool] = f.active
    plotshape(low if sb and brokeD and field_1[1] else na, location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.new('#F23645'))
    field_2: Series[bool] = f.active
    alertcondition(brokeU and field_2[1], 'break Up', 'break Up')
    field_3: Series[bool] = f.active
    alertcondition(brokeD and field_3[1], 'break Down', 'break Donw')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
