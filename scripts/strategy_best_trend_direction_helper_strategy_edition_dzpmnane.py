"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    bar_index, close, color, currency, extend, high, input, label, line,
    location, low, math, na, nz, open, plot, plotshape, script, shape, size, strategy, ta, time,
    xloc, yloc
)
from pynecore.types import Color, Label, Line, NA, Persistent, PersistentSeries, Series

percent_description: str = 'Percent of last pivot price for zigzag reversal:'


@script.strategy(title='Trend Direction Helper', shorttitle='Trend Direction Helper', overlay=True, pyramiding=0, default_qty_value=10, precision=7, currency=currency.USD, commission_value=0.2, commission_type=strategy.commission.percent, initial_capital=100000, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, close_by_id=True, na_bool=True)
def main(
    orderType=input.string('Longs+Shorts', title='What type of Orders', options=('Longs+Shorts', 'LongsOnly', 'ShortsOnly')),
    fastLength=input(7, title='Fast Length SMA'),
    slowLength=input(20, title='Slow Length SMA'),
    TD=input(title='== TREND DIRECTION ==', defval=True),
    RISK=input(title='Risk', defval=10),
    SIZE=input.string(title='Size', defval=size.large, options=(size.tiny, size.normal, size.large, size.huge)),
    text_up=input(title='TEXT Buy', defval='B'),
    text_dn=input(title='TEXT Sell', defval='S'),
    showSR=input(title='Show Supports & Resistances', defval=True),
    left=input(50, title='Left Pivot'),
    right=input(25, title='Right Pivot'),
    quick_right=input(5, title='Quick Right Pivot'),
    showHHLL=input(title='Show Higher/Highs and Lower Lows labels', defval=False),
    showZZ=input(title='Show ZIG ZAG Lines', defval=True),
    __input_14__=input.float(defval=0.75, title=percent_description, minval=0.0, maxval=99.0, step=0.25)
):
    isLong = orderType != 'ShortsOnly'
    isShort = orderType != 'LongsOnly'
    def range_1(length):
        sum: float = 0.0
        for i in pine_range(1, length - 5, 1):
            sum = sum + math.abs(close[i] - open[i])
        return sum / length

    def MRO1(length, range_2):
        true_count: int = 0
        counter: int = 0
        for i in pine_range(1, length - 5, 1):
            if math.abs(open[i] - close[i + 1]) >= range_2 * 2.0:
                true_count = true_count + 1
                i
        __block_result__ = na
        if true_count >= 1:
            __block_result__ = counter
        else:
            __block_result__ = -1
        mro = __block_result__
        return mro

    def MRO2(length, range_3):
        true_count: float = 0.0
        counter: int = 0
        for i in pine_range(1, length - 1, 1):
            if math.abs(close[i + 3] - close[i]) >= range_3 * 8.2:
                true_count = true_count + 1
                i
        __block_result_1__ = na
        if true_count >= 1:
            __block_result_1__ = counter
        else:
            __block_result_1__ = -1
        mro = __block_result_1__
        return mro

    def wpr(length):
        upper = ta.highest(length)
        lower = ta.lowest(length)
        out = 100 * (close - upper) / (upper - lower)
        return out

    def TS(RISK):
        value10 = math.abs(RISK / 180) + 1
        value11 = value10
        x1 = 60 + RISK
        x2 = 20 - RISK
        rng = range_1(2)
        mro1 = MRO1(1, rng)
        mro2 = MRO2(1, rng)
        __block_result_2__ = na
        if mro1 > -1:
            __block_result_2__ = 2
        else:
            __block_result_2__ = value10
        rez = __block_result_2__
        value11 = rez
        __block_result_3__ = na
        if mro2 > -1:
            __block_result_3__ = 2
        else:
            __block_result_3__ = value10
        rez1 = __block_result_3__
        value11 = rez1
        value2 = 100 - math.abs(wpr(value10))
        Table_value2: Series = value2
        notset: bool = False
        ii1: int = 1
        for i1 in pine_range(1, 50, 1):
            if (Table_value2[i1] < x2 or Table_value2[i1] > x1) and notset == False:
                notset = True
                ii1 = i1
        z = Table_value2[ii1]
        __block_result_4__ = na
        if value2 < x2:
            __block_result_5__ = na
            if Table_value2[ii1] > x1:
                __block_result_5__ = ii1
            else:
                __block_result_5__ = 0
            __block_result_4__ = __block_result_5__
        else:
            __block_result_4__ = 0
        dn = __block_result_4__
        __block_result_6__ = na
        if value2 > x1:
            __block_result_7__ = na
            if Table_value2[ii1] < x2:
                __block_result_7__ = ii1
            else:
                __block_result_7__ = 0
            __block_result_6__ = __block_result_7__
        else:
            __block_result_6__ = 0
        up = __block_result_6__
        return (up, dn)

    up: Series
    dn: Series
    up, dn = TS(RISK)
    text_label = text_up if up else text_dn
    color_label = color.new(color.green, 20) if up else color.new(color.red, 20)
    textcolor_label = color.new(color.maroon, 20) if up else color.new(color.black, 20)
    style_label = label.style_label_up if up else label.style_label_down
    y_label = yloc.belowbar if up else yloc.abovebar
    x_pos = up if up else dn
    _up: int = 0
    _dn: int = 0
    _up = ta.barssince(up)
    _dn = ta.barssince(dn)
    curr = 0 - ta.barssince(cast_bool(_dn)) + ta.barssince(cast_bool(_up))
    TD_Buy = 1 if curr < 0 else 0
    TD_Sell = 1 if curr > 0 else 0
    TS_UP_Label: Persistent[Label] = na(Label)
    TS_DN_Label: Persistent[Label] = na(Label)
    AVG_RANGE: Persistent = range_1(RISK)
    pos_y_up: Persistent = low - AVG_RANGE * low
    pos_y_dn: Persistent = high + AVG_RANGE * high
    oblique_up: Persistent = NA(Line)
    oblique_dn: Persistent = NA(Line)
    if up:
        TS_UP_Label = label.new(x=bar_index - _up, y=pos_y_up, text=text_label, color=color_label, textcolor=textcolor_label, style=style_label, xloc=xloc.bar_index, yloc=yloc.belowbar, size=SIZE)
    if dn:
        TS_DN_Label = label.new(x=bar_index - _dn, y=pos_y_dn, text=text_label, color=color_label, textcolor=textcolor_label, style=style_label, xloc=xloc.bar_index, yloc=yloc.abovebar, size=SIZE)
    pivot_high = ta.pivothigh(high, left, right)
    pivot_lows = ta.pivotlow(low, left, right)
    quick_pivot_high = ta.pivothigh(high, left, quick_right)
    quick_pivot_lows = ta.pivotlow(low, left, quick_right)
    level1 = ta.valuewhen(cast_bool(quick_pivot_high), high[quick_right], 0)
    level2 = ta.valuewhen(cast_bool(quick_pivot_lows), low[quick_right], 0)
    level3 = ta.valuewhen(cast_bool(pivot_high), high[right], 0)
    level4 = ta.valuewhen(cast_bool(pivot_lows), low[right], 0)
    level5 = ta.valuewhen(cast_bool(pivot_high), high[right], 1)
    level6 = ta.valuewhen(cast_bool(pivot_lows), low[right], 1)
    level7 = ta.valuewhen(cast_bool(pivot_high), high[right], 2)
    level8 = ta.valuewhen(cast_bool(pivot_lows), low[right], 2)
    level1_col = color.green if close >= level1 else color.red
    level2_col = color.green if close >= level2 else color.red
    level3_col = color.green if close >= level3 else color.red
    level4_col = color.green if close >= level4 else color.red
    level5_col = color.green if close >= level5 else color.red
    level6_col = color.green if close >= level6 else color.red
    level7_col = color.green if close >= level7 else color.red
    level8_col = color.green if close >= level8 else color.red
    event = close >= level6
    since_event = ta.barssince(event)
    first_event = since_event == 1
    second_event = close < level6
    since_second_event = ta.barssince(second_event)
    sec_event = since_second_event == 1
    plot(level1 if showSR else na, style=plot.style_circles, color=level1_col, show_last=1, linewidth=2, trackprice=True)
    plot(level2 if showSR else na, style=plot.style_circles, color=level2_col, show_last=1, linewidth=2, trackprice=True)
    plot(level3 if showSR else na, style=plot.style_circles, color=level3_col, show_last=1, linewidth=2, trackprice=True)
    plot(level4 if showSR else na, style=plot.style_circles, color=level4_col, show_last=1, linewidth=2, trackprice=True)
    plot(level5 if showSR else na, style=plot.style_circles, color=level5_col, show_last=1, linewidth=2, trackprice=True)
    plot(level6 if showSR else na, style=plot.style_circles, color=level6_col, show_last=1, linewidth=2, trackprice=True)
    plot(level7 if showSR else na, style=plot.style_circles, color=level7_col, show_last=1, linewidth=2, trackprice=True)
    plot(level8 if showSR else na, style=plot.style_circles, color=level8_col, show_last=1, linewidth=2, trackprice=True)
    def isBWFractal(mode):
        ret = high[4] < high[2] and high[3] <= high[2] and (high[2] >= high[1]) and (high[2] > high) if mode == 1 else low[4] > low[2] and low[3] >= low[2] and (low[2] <= low[1]) and (low[2] < low) if mode == 2 else False
        return ret

    filteredtopf = isBWFractal(1)
    filteredbotf = isBWFractal(2)
    higherhigh = False if filteredtopf == False else ta.valuewhen(filteredtopf == True, high[2], 1) < ta.valuewhen(filteredtopf == True, high[2], 0) and ta.valuewhen(filteredtopf == True, high[2], 2) < ta.valuewhen(filteredtopf == True, high[2], 0)
    lowerhigh = False if filteredtopf == False else ta.valuewhen(filteredtopf == True, high[2], 1) > ta.valuewhen(filteredtopf == True, high[2], 0) and ta.valuewhen(filteredtopf == True, high[2], 2) > ta.valuewhen(filteredtopf == True, high[2], 0)
    higherlow = False if filteredbotf == False else ta.valuewhen(filteredbotf == True, low[2], 1) < ta.valuewhen(filteredbotf == True, low[2], 0) and ta.valuewhen(filteredbotf == True, low[2], 2) < ta.valuewhen(filteredbotf == True, low[2], 0)
    lowerlow = False if filteredbotf == False else ta.valuewhen(filteredbotf == True, low[2], 1) > ta.valuewhen(filteredbotf == True, low[2], 0) and ta.valuewhen(filteredbotf == True, low[2], 2) > ta.valuewhen(filteredbotf == True, low[2], 0)
    plotshape((na if na(higherhigh) else 1 if higherhigh else 0) if showHHLL else na, title='Higher High', style=shape.square, location=location.abovebar, color=color.new(color.maroon, 0), text='[HH]', offset=-2)
    plotshape((na if na(lowerhigh) else 1 if lowerhigh else 0) if showHHLL else na, title='Lower High', style=shape.square, location=location.abovebar, color=color.new(color.maroon, 0), text='[LH]', offset=-2)
    plotshape((na if na(higherlow) else 1 if higherlow else 0) if showHHLL else na, title='High Low', style=shape.square, location=location.belowbar, color=color.new(color.green, 0), text='[HL]', offset=-2)
    plotshape((na if na(lowerlow) else 1 if lowerlow else 0) if showHHLL else na, title='Lower Low', style=shape.square, location=location.belowbar, color=color.new(color.green, 0), text='[LL]', offset=-2)
    zzrealpivot_description: str = 'Show real zigzag pivots:'
    percent = __input_14__ / 100
    show_real_pivots_zz: bool = False
    def f_zz(_percent):
        _is_direction_up: PersistentSeries[bool] = na(bool)
        _htrack: PersistentSeries[float] = na(float)
        _ltrack: PersistentSeries[float] = na(float)
        _pivot: PersistentSeries[float] = na(float)
        _reverse_range: Persistent[float] = 0.0
        _real_pivot_time: Persistent[int] = na(int)
        _reverse_line: Persistent[float] = 0.0
        if bar_index >= 1:
            _reverse_range = nz(_pivot[1]) * _percent
            _is_direction_up = nz(_is_direction_up[1], True)
            if _is_direction_up:
                _htrack = math.max(math.max(high, high[1]), nz(_htrack[1], high))
                if ta.change(_htrack) > 0:
                    _real_pivot_time = time
                _ltrack = na
                _reverse_line = _htrack[1] - _reverse_range
                if close < _reverse_line:
                    _pivot = _htrack
                    _is_direction_up = False
            if not _is_direction_up:
                _ltrack = math.min(math.min(low, low[1]), nz(_ltrack[1], low))
                if ta.change(_ltrack) < 0:
                    _real_pivot_time = time
                _htrack = na
                _reverse_line = _ltrack[1] + _reverse_range
                if close > _reverse_line:
                    _pivot = _ltrack
                    _is_direction_up = True
        return (_pivot, _is_direction_up, _reverse_line, _real_pivot_time)

    pivot, is_up, reverse, _rl_time = f_zz(percent)
    zz_color = color.orange if is_up else color.teal
    zz = pivot if ta.change(pivot) != 0 else na
    tt = _rl_time if show_real_pivots_zz else time
    __x_A00: Persistent[int] = na(int)
    __x_A01: Persistent[int] = na(int)
    __x_A02: Persistent[int] = na(int)
    __x_A03: Persistent[int] = na(int)
    __x_A04: Persistent[int] = na(int)
    __x_A05: Persistent[int] = na(int)
    __x_A06: Persistent[int] = na(int)
    __x_A07: Persistent[int] = na(int)
    __x_A08: Persistent[int] = na(int)
    __x_A09: Persistent[int] = na(int)
    __x_A10: Persistent[int] = na(int)
    __x_ALEN: Persistent[int] = 10
    __x_AMODE: str = na(str)
    __x_ASET: int = na(int)
    def f__x_AGET(_i):
        return __x_A00 if _i == 0 else __x_A01 if _i == 1 else __x_A02 if _i == 2 else __x_A03 if _i == 3 else __x_A04 if _i == 4 else __x_A05 if _i == 5 else __x_A06 if _i == 6 else __x_A07 if _i == 7 else __x_A08 if _i == 8 else __x_A09 if _i == 9 else __x_A10 if _i == 10 else na

    def f__x_ASET(_value, _index, _length, _mode):
        _return: int = na(int)
        if _index > _length:
            _return = na
        else:
            if _index == 0:
                _return = _value
            else:
                if _mode == 'push' or _mode == 'PUSH' or _mode == 'p' or (_mode == 'P'):
                    _return = f__x_AGET(_index - 1)
                if _mode == 'replace' or _mode == 'REPLACE' or _mode == 'r' or (_mode == 'R'):
                    _return = f__x_AGET(_index)
        return _return

    __y_A00: Persistent[float] = na(float)
    __y_A01: Persistent[float] = na(float)
    __y_A02: Persistent[float] = na(float)
    __y_A03: Persistent[float] = na(float)
    __y_A04: Persistent[float] = na(float)
    __y_A05: Persistent[float] = na(float)
    __y_A06: Persistent[float] = na(float)
    __y_A07: Persistent[float] = na(float)
    __y_A08: Persistent[float] = na(float)
    __y_A09: Persistent[float] = na(float)
    __y_A10: Persistent[float] = na(float)
    __y_ALEN: Persistent[int] = 10
    __y_AMODE: str = na(str)
    __y_ASET: float = na(float)
    def f__y_AGET(_i):
        return __y_A00 if _i == 0 else __y_A01 if _i == 1 else __y_A02 if _i == 2 else __y_A03 if _i == 3 else __y_A04 if _i == 4 else __y_A05 if _i == 5 else __y_A06 if _i == 6 else __y_A07 if _i == 7 else __y_A08 if _i == 8 else __y_A09 if _i == 9 else __y_A10 if _i == 10 else na

    def f__y_ASET(_value, _index, _length, _mode):
        _return: float = na(float)
        if _index > _length:
            _return = na
        else:
            if _index == 0:
                _return = _value
            else:
                if _mode == 'push' or _mode == 'PUSH' or _mode == 'p' or (_mode == 'P'):
                    _return = f__y_AGET(_index - 1)
                if _mode == 'replace' or _mode == 'REPLACE' or _mode == 'r' or (_mode == 'R'):
                    _return = f__y_AGET(_index)
        return _return

    def f_y(_i):
        return ta.valuewhen(zz, zz, _i)

    def f_x(_i):
        return ta.valuewhen(zz, tt, _i)

    if zz:
        if na(f__y_AGET(1)):
            __x_AMODE = 'push'
            __y_AMODE = 'push'
            __x_ASET = tt
            __y_ASET = zz
        else:
            f_y_1 = f_y(0)
            f_y_2 = f_y(2)
            if f_y(0) > f_y(1) and f_y_1 > f_y_2:
                if f__y_AGET(0) < f__y_AGET(1):
                    __x_AMODE = 'push'
                    __y_AMODE = 'push'
                    __x_ASET = tt
                    __y_ASET = zz
                else:
                    __x_AMODE = 'replace'
                    __y_AMODE = 'replace'
                    __x_ASET = tt
                    __y_ASET = zz
            f_y_3 = f_y(0)
            f_y_4 = f_y(2)
            if f_y(0) < f_y(1) and f_y_3 < f_y_4:
                if f__y_AGET(0) > f__y_AGET(1):
                    __x_AMODE = 'push'
                    __y_AMODE = 'push'
                    __x_ASET = tt
                    __y_ASET = zz
                else:
                    __x_AMODE = 'replace'
                    __y_AMODE = 'replace'
                    __x_ASET = tt
                    __y_ASET = zz
    if not na(__x_ASET):
        __x_A10 = f__x_ASET(__x_ASET, 10, __x_ALEN, __x_AMODE)
        __x_A09 = f__x_ASET(__x_ASET, 9, __x_ALEN, __x_AMODE)
        __x_A08 = f__x_ASET(__x_ASET, 8, __x_ALEN, __x_AMODE)
        __x_A07 = f__x_ASET(__x_ASET, 7, __x_ALEN, __x_AMODE)
        __x_A06 = f__x_ASET(__x_ASET, 6, __x_ALEN, __x_AMODE)
        __x_A05 = f__x_ASET(__x_ASET, 5, __x_ALEN, __x_AMODE)
        __x_A04 = f__x_ASET(__x_ASET, 4, __x_ALEN, __x_AMODE)
        __x_A03 = f__x_ASET(__x_ASET, 3, __x_ALEN, __x_AMODE)
        __x_A02 = f__x_ASET(__x_ASET, 2, __x_ALEN, __x_AMODE)
        __x_A01 = f__x_ASET(__x_ASET, 1, __x_ALEN, __x_AMODE)
        __x_A00 = f__x_ASET(__x_ASET, 0, __x_ALEN, __x_AMODE)
    if not na(__y_ASET):
        __y_A10 = f__y_ASET(__y_ASET, 10, __y_ALEN, __y_AMODE)
        __y_A09 = f__y_ASET(__y_ASET, 9, __y_ALEN, __y_AMODE)
        __y_A08 = f__y_ASET(__y_ASET, 8, __y_ALEN, __y_AMODE)
        __y_A07 = f__y_ASET(__y_ASET, 7, __y_ALEN, __y_AMODE)
        __y_A06 = f__y_ASET(__y_ASET, 6, __y_ALEN, __y_AMODE)
        __y_A05 = f__y_ASET(__y_ASET, 5, __y_ALEN, __y_AMODE)
        __y_A04 = f__y_ASET(__y_ASET, 4, __y_ALEN, __y_AMODE)
        __y_A03 = f__y_ASET(__y_ASET, 3, __y_ALEN, __y_AMODE)
        __y_A02 = f__y_ASET(__y_ASET, 2, __y_ALEN, __y_AMODE)
        __y_A01 = f__y_ASET(__y_ASET, 1, __y_ALEN, __y_AMODE)
        __y_A00 = f__y_ASET(__y_ASET, 0, __y_ALEN, __y_AMODE)
    col1: Color = color.new('#6D8B0D90')
    col2: Color = color.new('#BB704590')
    line_width: int = 5
    _li: Persistent[Line] = na(Line)
    _li_color = col1 if f__y_AGET(0) > f__y_AGET(1) else col2
    if showZZ:
        line.delete(_li)
        _li = line.new(x1=f__x_AGET(0), y1=f__y_AGET(0), x2=f__x_AGET(1), y2=f__y_AGET(1), xloc=xloc.bar_time, extend=extend.none, color=_li_color, style=line.style_solid, width=line_width)
        _li1: Persistent[Line] = na(Line)
        _li_color1 = col1 if f__y_AGET(1) > f__y_AGET(2) else col2
        line.delete(_li1)
        _li1 = line.new(x1=f__x_AGET(1), y1=f__y_AGET(1), x2=f__x_AGET(2), y2=f__y_AGET(2), xloc=xloc.bar_time, extend=extend.none, color=_li_color1, style=line.style_solid, width=line_width)
        _li2: Persistent[Line] = na(Line)
        _li_color2 = col1 if f__y_AGET(2) > f__y_AGET(3) else col2
        line.delete(_li2)
        _li2 = line.new(x1=f__x_AGET(2), y1=f__y_AGET(2), x2=f__x_AGET(3), y2=f__y_AGET(3), xloc=xloc.bar_time, extend=extend.none, color=_li_color2, style=line.style_solid, width=line_width)
        _li3: Persistent[Line] = na(Line)
        _li_color3 = col1 if f__y_AGET(3) > f__y_AGET(4) else col2
        line.delete(_li3)
        _li3 = line.new(x1=f__x_AGET(3), y1=f__y_AGET(3), x2=f__x_AGET(4), y2=f__y_AGET(4), xloc=xloc.bar_time, extend=extend.none, color=_li_color3, style=line.style_solid, width=line_width)
        _li4: Persistent[Line] = na(Line)
        _li_color4 = col1 if f__y_AGET(4) > f__y_AGET(5) else col2
        line.delete(_li4)
        _li4 = line.new(x1=f__x_AGET(4), y1=f__y_AGET(4), x2=f__x_AGET(5), y2=f__y_AGET(5), xloc=xloc.bar_time, extend=extend.none, color=_li_color4, style=line.style_solid, width=line_width)
        _li5: Persistent[Line] = na(Line)
        _li_color5 = col1 if f__y_AGET(5) > f__y_AGET(6) else col2
        line.delete(_li5)
        _li5 = line.new(x1=f__x_AGET(5), y1=f__y_AGET(5), x2=f__x_AGET(6), y2=f__y_AGET(6), xloc=xloc.bar_time, extend=extend.none, color=_li_color5, style=line.style_solid, width=line_width)
        _li6: Persistent[Line] = na(Line)
        _li_color6 = col1 if f__y_AGET(6) > f__y_AGET(7) else col2
        line.delete(_li6)
        _li6 = line.new(x1=f__x_AGET(6), y1=f__y_AGET(6), x2=f__x_AGET(7), y2=f__y_AGET(7), xloc=xloc.bar_time, extend=extend.none, color=_li_color6, style=line.style_solid, width=line_width)
        _li7: Persistent[Line] = na(Line)
        _li_color7 = col1 if f__y_AGET(7) > f__y_AGET(8) else col2
        line.delete(_li7)
        _li7 = line.new(x1=f__x_AGET(7), y1=f__y_AGET(7), x2=f__x_AGET(8), y2=f__y_AGET(8), xloc=xloc.bar_time, extend=extend.none, color=_li_color7, style=line.style_solid, width=line_width)
    entry_price = ta.valuewhen(up or dn, close, 0)
    sma_fast = ta.sma(close, fastLength)
    sma_slow = ta.sma(close, slowLength)
    long_exit = ta.crossunder(sma_fast, sma_slow)
    short_exit = ta.crossover(sma_fast, sma_slow)
    plot(sma_fast, 'SMA fastLength', color=color.new(color.orange, 0), linewidth=2)
    plot(sma_slow, 'SMA slowLength', color=color.new(color.blue, 0), linewidth=2)
    plotshape(ta.crossover(sma_fast, sma_slow), color=color.new(color.green, 0), style=shape.circle, size=size.small)
    plotshape(ta.crossunder(sma_fast, sma_slow), color=color.new(color.red, 0), style=shape.circle, size=size.small)
    if isLong:
        if up[1]:
            strategy.entry('Long', strategy.long)
        if long_exit:
            strategy.close('Long')
    if isShort:
        if dn[1]:
            strategy.entry('Short', strategy.short)
        if short_exit:
            strategy.close('Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
