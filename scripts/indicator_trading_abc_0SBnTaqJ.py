"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, array, bar_index, close, color, extend, fill, high,
    input, label, line, location, low, math, na, open, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Label, Line, Persistent, Series


@script.indicator('Trading ABC', overlay=True, max_bars_back=500, max_lines_count=500, max_labels_count=500, na_bool=True)
def main(
    prd=input.int(defval=8, title='ZigZag Period', minval=2, maxval=50, group='Setup'),
    fiboup=input.float(defval=0.618, title='Fibonacci Max', group='Setup'),
    fibodn=input.float(defval=0.382, title='Fibonacci Min', group='Setup'),
    __input_3__=input.float(defval=5.0, title='Error Rate', minval=0, maxval=30, group='Setup'),
    showabc=input.bool(defval=True, title='Show ABC', group='Extras'),
    keepabc=input.bool(defval=True, title='Keep Old ABCs', group='Extras'),
    showcloud=input.bool(defval=True, title='Show Cloud', group='Extras', inline='cloud'),
    c_upcol=input.color(defval=color.new(color.lime, 75), title='', group='Extras', inline='cloud'),
    c_dncol=input.color(defval=color.new(color.red, 75), title='', group='Extras', inline='cloud'),
    showzigzag=input.bool(defval=True, title='Show Zig Zag & Fibo', group='Extras', inline='zigzag'),
    upcol=input.color(defval=color.lime, title='', group='Extras', inline='zigzag'),
    dncol=input.color(defval=color.red, title='', group='Extras', inline='zigzag'),
    srcma: Series[float] = input.source(defval=close, title='Source for Moving Averages', group='Trend Cloud'),
    malen1=input.int(defval=50, title='SMA 1 Length', minval=1, group='Trend Cloud'),
    malen2=input.int(defval=100, title='SMA 2 Length', minval=1, group='Trend Cloud'),
    malen3=input.int(defval=150, title='SMA 3 Length', minval=1, group='Trend Cloud'),
    malen4=input.int(defval=200, title='SMA 4 Length', minval=1, group='Trend Cloud'),
    malen5=input.int(defval=20, title='EMA 1 Length', minval=1, group='Trend Cloud'),
    malen6=input.int(defval=40, title='EMA 2 Length', minval=1, group='Trend Cloud')
):
    errorrate = __input_3__ / 100
    ma_array: list[float] = array.new_float(6)
    array.set(ma_array, 0, ta.sma(srcma, malen1))
    array.set(ma_array, 1, ta.sma(srcma, malen2))
    array.set(ma_array, 2, ta.sma(srcma, malen3))
    array.set(ma_array, 3, ta.sma(srcma, malen4))
    array.set(ma_array, 4, ta.ema(srcma, malen5))
    array.set(ma_array, 5, ta.ema(srcma, malen6))
    umax: float = na(float)
    umin: float = na(float)
    lmax: float = na(float)
    lmin: float = na(float)
    upper: Series[int] = 0
    lower: Series[int] = 0
    for x in pine_range(1, 6, 1):
        ma = array.get(ma_array, x - 1)
        if ma >= math.max(open, close):
            upper = upper + 1
            if na(umax):
                umax = ma
                umin = ma
            else:
                umax = math.max(umax, ma)
                umin = math.min(umin, ma)
        elif ma <= math.min(open, close):
            lower = lower + 1
            if na(lmax):
                lmax = ma
                lmin = ma
            else:
                lmax = math.max(lmax, ma)
                lmin = math.min(lmin, ma)
    trend: Persistent[int] = 0
    trend = 1 if lower > 0 and upper == 0 and (lower[1] > 0) and (upper[1] == 0) else -1 if lower == 0 and upper > 0 and (lower[1] == 0) and (upper[1] > 0) else trend
    tucolor = c_upcol if trend == 1 else na
    tdcolor = c_dncol if trend == -1 else na
    fill(plot(umax, color=na), plot(umin, color=na), color=tdcolor if showcloud else na)
    fill(plot(lmax, color=na), plot(lmin, color=na), color=tucolor if showcloud else na)
    def get_ph_pl_dir(len):
        ph: float = high if ta.highestbars(high, len) == 0 else na
        pl: float = low if ta.lowestbars(low, len) == 0 else na
        dir: Persistent[int] = 0
        iff_1 = -1 if pl and na(ph) else dir
        dir = 1 if ph and na(pl) else iff_1
        return (ph, pl, dir)

    ph, pl, dir = get_ph_pl_dir(prd)
    max_array_size: Persistent[int] = 10
    zigzag: Persistent[list[float]] = array.new_float(0)
    def add_to_zigzag(value, bindex):
        array.unshift(zigzag, bindex)
        array.unshift(zigzag, value)
        __block_result__ = na
        if array.size(zigzag) > max_array_size:
            array.pop(zigzag)
            __block_result__ = array.pop(zigzag)
        return __block_result__

    def update_zigzag(value, bindex):
        __block_result_1__ = na
        if array.size(zigzag) == 0:
            __block_result_1__ = add_to_zigzag(value, bindex)
        else:
            if dir == 1 and value > array.get(zigzag, 0) or (dir == -1 and value < array.get(zigzag, 0)):
                array.set(zigzag, 0, value)
                array.set(zigzag, 1, bindex)
            __block_result_1__ = 0.0
        return __block_result_1__

    dir_changed = ta.change(dir)
    if cast_bool(ph) or cast_bool(pl):
        if cast_bool(dir_changed):
            add_to_zigzag(ph if dir == 1 else pl, bar_index)
        else:
            update_zigzag(ph if dir == 1 else pl, bar_index)
    if showzigzag and array.size(zigzag) > 5:
        zzline1: Persistent[Line] = na(Line)
        zzline2: Persistent[Line] = na(Line)
        line.delete(zzline1)
        line.delete(zzline2)
        zzline1 = line.new(x1=math.round(array.get(zigzag, 1)), y1=array.get(zigzag, 0), x2=math.round(array.get(zigzag, 3)), y2=array.get(zigzag, 2), color=upcol if dir == 1 else dncol, width=2, style=line.style_dashed)
        zzline2 = line.new(x1=math.round(array.get(zigzag, 3)), y1=array.get(zigzag, 2), x2=math.round(array.get(zigzag, 5)), y2=array.get(zigzag, 4), color=upcol if dir == -1 else dncol, width=2, style=line.style_dashed)
        zzlen = math.abs(array.get(zigzag, 2) - array.get(zigzag, 4))
        fmin = array.get(zigzag, 2) + zzlen * (fibodn - errorrate) if dir == 1 else array.get(zigzag, 4) + zzlen * (1 - fibodn + errorrate)
        fmax = array.get(zigzag, 2) + zzlen * (fiboup + errorrate) if dir == 1 else array.get(zigzag, 4) + zzlen * (1 - fiboup - errorrate)
        fibo1: Persistent[Line] = na(Line)
        fibo2: Persistent[Line] = na(Line)
        line.delete(fibo1)
        line.delete(fibo2)
        fibo1 = line.new(x1=math.round(array.get(zigzag, 3)), y1=fmin, x2=math.round(array.get(zigzag, 3)) + 1, y2=fmin, color=color.blue, style=line.style_dashed, extend=extend.right)
        fibo2 = line.new(x1=math.round(array.get(zigzag, 3)), y1=fmax, x2=math.round(array.get(zigzag, 3)) + 1, y2=fmax, color=color.blue, style=line.style_dashed, extend=extend.right)
    zchange = array.get(zigzag, 0) if array.size(zigzag) > 0 else 0.0
    abc: list[float] = array.new_float(0)
    if cast_bool(ta.change(zchange)) and array.size(zigzag) > 5 and (cast_bool(pl) and trend == 1 and (dir == -1) and (low < array.max(ma_array)) or (cast_bool(ph) and trend == -1 and (dir == 1) and (high > array.min(ma_array)))):
        a = array.get(zigzag, 0)
        b = array.get(zigzag, 2)
        b_loc = array.get(zigzag, 3)
        c = array.get(zigzag, 4)
        c_loc = array.get(zigzag, 5)
        rate = (a - b) / (c - b)
        if rate >= fibodn - fibodn * errorrate and rate <= fiboup + fiboup * errorrate:
            array.push(abc, b)
            array.push(abc, b_loc)
            array.push(abc, c)
            array.push(abc, c_loc)
    def draw_line(dir, x1_, y1_, x2_, y2_, x3_, y3_):
        l1 = line.new(x1=x1_, y1=y1_, x2=x2_, y2=y2_, color=upcol if dir == 1 else dncol, width=2)
        l2 = line.new(x1=x2_, y1=y2_, x2=x3_, y2=y3_, color=dncol if dir == 1 else upcol, width=2)
        return (l1, l2)

    def draw_label(dir, x1_, y1_, x2_, y2_, x3_, y3_):
        alabel = label.new(x=x1_, y=y1_, text='C', style=label.style_label_down if dir == 1 else label.style_label_up, color=color.new(color.white, 100), textcolor=color.blue)
        blabel = label.new(x=x2_, y=y2_, text='B', style=label.style_label_down if dir == -1 else label.style_label_up, color=color.new(color.white, 100), textcolor=color.blue)
        clabel = label.new(x=x3_, y=y3_, text='A', style=label.style_label_down if dir == 1 else label.style_label_up, color=color.new(color.white, 100), textcolor=color.blue)
        return (alabel, blabel, clabel)

    abclines: Persistent[list[Line]] = array.new_line(2)
    abclabels: Persistent[list[Label]] = array.new_label(3)
    if showabc and array.size(abc) >= 4:
        if not keepabc:
            line.delete(array.pop(abclines))
            line.delete(array.pop(abclines))
            label.delete(array.pop(abclabels))
            label.delete(array.pop(abclabels))
            label.delete(array.pop(abclabels))
        l1_, l2_ = draw_line(dir, bar_index, array.get(zigzag, 0), math.round(array.get(abc, 1)), array.get(abc, 0), math.round(array.get(abc, 3)), array.get(abc, 2))
        array.unshift(abclines, l1_)
        array.unshift(abclines, l2_)
        la1_, la2_, la3_ = draw_label(dir, bar_index, array.get(zigzag, 0), math.round(array.get(abc, 1)), array.get(abc, 0), math.round(array.get(abc, 3)), array.get(abc, 2))
        array.unshift(abclabels, la1_)
        array.unshift(abclabels, la2_)
        array.unshift(abclabels, la3_)
    lbounced: bool = False
    sbounced: bool = False
    for i in pine_range(0, 5, 1):
        if math.min(low, low[1]) <= array.get(ma_array, i) and close > array.get(ma_array, i) and (close > open):
            lbounced = True
        if math.max(high, high[1]) >= array.get(ma_array, i) and close < array.get(ma_array, i) and (close < open):
            sbounced = True
    sto: Series = ta.sma(ta.stoch(close, high, low, 5), 3)
    sto_sig: Series = ta.sma(sto, 3)
    lstoch = sto[1] <= sto_sig[1] and sto > sto_sig and (sto[1] < 50)
    sstoch = sto[1] >= sto_sig[1] and sto < sto_sig and (sto[1] > 50)
    there_is_abc = array.size(abc) != 0
    last_zz_point: Persistent[float] = 0.0
    last_zz_point = array.get(zigzag, 0) if array.size(zigzag) > 2 and there_is_abc else last_zz_point
    abc_bar_count: Persistent[int] = 0
    abc_bar_count = 0 if there_is_abc else abc_bar_count + 1
    hhh_ = ta.highest(abc_bar_count + 1)
    lll_ = ta.lowest(abc_bar_count + 1)
    long = trend == 1 and abc_bar_count <= 6 and lbounced and (lll_ >= last_zz_point)
    short = trend == -1 and abc_bar_count <= 6 and sbounced and (hhh_ <= last_zz_point)
    plotshape(long, style=shape.triangleup, color=upcol, location=location.belowbar, size=size.small)
    plotshape(short, style=shape.triangledown, color=dncol, location=location.abovebar, size=size.small)
    alertcondition(long, title='ABC Long', message='ABC Long')
    alertcondition(short, title='ABC Short', message='ABC Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)