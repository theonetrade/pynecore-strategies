"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool, cast_int
from pynecore.lib import (
    bar_index, barstate, close, color, extend, high, input, label, line, low,
    math, na, nz, open, plot, script, size, string, ta, time, xloc, yloc
)
from pynecore.types import Color, Label, Line, Persistent, PersistentSeries, Series


@script.indicator(title='[RS]ZigZag Percent Reversal - Forecast - patterns - labels', shorttitle='ZZ', overlay=True, na_bool=True)
def main(
    percent_method=input.string(defval='MANUAL', title='Method to use for the zigzag reversal range:', options=('MANUAL', 'ATR005 * X', 'ATR010 * X', 'ATR020 * X', 'ATR050 * X', 'ATR100 * X', 'ATR250 * X')),
    __input_1__=input.float(defval=0.25, title='Percent of last pivot price for zigzag reversal:', minval=0.0, maxval=99.0),
    percent_multiplier=input(defval=1.0, title='Multiplier to apply to ATR if applicable:'),
    show_real_pivots=input(defval=True, title='Show real zigzag pivots:'),
    show_zigzag_lines=input(defval=True, title='Show zigzag lines:'),
    show_pivot_price=input(defval=True, title='Show price labels on zigzag:'),
    show_triangle_rates=input(defval=True, title='Show rate labels on triangles:'),
    show_angles=input(defval=False, title='Show Angle Degree information(EXPERIMENTAL):'),
    show_patterns=input(defval=True, title='Show Patterns:'),
    show_harmonic=input(defval=True, title='Show Harmonic Triangle Pattern:'),
    show_tap=input(defval=True, title='Show 2/3/4 Tap Patterns:'),
    show_abcd=input(defval=True, title='Show AB=CD Pattern:'),
    show_bat=input(defval=True, title='Show Bat Pattern:'),
    show_butterfly=input(defval=True, title='Show Butterfly Pattern:'),
    show_gartley=input(defval=True, title='Show Gartley Pattern:'),
    show_crab=input(defval=True, title='Show Crab Pattern:'),
    show_shark=input(defval=True, title='Show Shark Pattern:'),
    show_5o=input(defval=True, title='Show 5o Pattern:'),
    show_wolfe=input(defval=True, title='Show wolfe Pattern:'),
    show_contria=input(defval=True, title='Show Contracting Triangle Pattern:'),
    show_exptria=input(defval=True, title='Show Expanding Triangle Pattern:'),
    show_hns=input(defval=True, title='Show Head and Shoulders Pattern:'),
    show_projections=input(defval=True, title='Show projections forecast of zigzag:'),
    show_projections_square=input(defval=True, title='Show projections forecast Bounds:'),
    show_projections_square_rates=input(defval=False, title='Show projections target rates:'),
    __input_25__=input(10),
    err=input(5.0)
):
    percent: Persistent[float] = __input_1__ / 100
    if percent_method == 'ATR005 * X':
        percent = ta.atr(5) / open * percent_multiplier
    if percent_method == 'ATR010 * X':
        percent = ta.atr(10) / open * percent_multiplier
    if percent_method == 'ATR020 * X':
        percent = ta.atr(20) / open * percent_multiplier
    if percent_method == 'ATR050 * X':
        percent = ta.atr(50) / open * percent_multiplier
    if percent_method == 'ATR100 * X':
        percent = ta.atr(100) / open * percent_multiplier
    if percent_method == 'ATR250 * X':
        percent = ta.atr(250) / open * percent_multiplier
    def f_zz(_percent):
        _is_direction_up: Persistent[bool] = na(bool)
        _htrack: Persistent[float] = na(float)
        _ltrack: Persistent[float] = na(float)
        _pivot: PersistentSeries[float] = na(float)
        _reverse_range: float = 0.0
        _real_pivot_time: Persistent[int] = na(int)
        _htime: Persistent[int] = na(int)
        _ltime: Persistent[int] = na(int)
        _reverse_line: Persistent[float] = 0.0
        if bar_index >= 1:
            if na(_is_direction_up):
                _is_direction_up = True
            _reverse_range = nz(_pivot[1]) * _percent
            if _is_direction_up:
                _ltrack = na
                _ltime = time
                if na(_htrack):
                    if high > high[1]:
                        _htrack = high
                        _htime = time
                    else:
                        _htrack = high[1]
                        _htime = time[1]
                else:
                    if high > _htrack:
                        _htrack = high
                        _htime = time
                _reverse_line = _htrack - _reverse_range
                if close <= _reverse_line:
                    _pivot = _htrack
                    _real_pivot_time = _htime
                    _is_direction_up = False
            if not _is_direction_up:
                _htrack = na
                _htime = na
                if na(_ltrack):
                    if low < low[1]:
                        _ltrack = low
                        _ltime = time
                    else:
                        _ltrack = low[1]
                        _ltime = time[1]
                else:
                    if low < _ltrack:
                        _ltrack = low
                        _ltime = time
                _reverse_line = _ltrack + _reverse_range
                if close >= _reverse_line:
                    _pivot = _ltrack
                    _real_pivot_time = _ltime
                    _is_direction_up = True
        return (_pivot, _is_direction_up, _reverse_line, _real_pivot_time)

    price_a: Series
    price_a, is_up, reverse, _rl_time = f_zz(percent)
    alt_time = _rl_time if show_real_pivots else time
    zz_color = color.orange if is_up else color.teal
    is_new_zig = price_a if ta.change(price_a) != 0 else na
    plot(reverse, title='R', color=color.new(color.gray, 40), style=plot.style_stepline, linewidth=1, offset=1)
    plot(reverse, title='R', color=color.new(color.white, 40), style=plot.style_circles, linewidth=4, offset=1, show_last=1)
    time_a: PersistentSeries[int] = na(int)
    time_b: PersistentSeries[int] = na(int)
    price_b: PersistentSeries[float] = na(float)
    time_c: PersistentSeries[int] = na(int)
    price_c: PersistentSeries[float] = na(float)
    time_d: PersistentSeries[int] = na(int)
    price_d: PersistentSeries[float] = na(float)
    time_e: PersistentSeries[int] = na(int)
    price_e: PersistentSeries[float] = na(float)
    time_f: PersistentSeries[int] = na(int)
    price_f: PersistentSeries[float] = na(float)
    time_g: Persistent[int] = na(int)
    price_g: Persistent[float] = na(float)
    if is_new_zig:
        time_a = alt_time
        time_b = time_a[1]
        price_b = price_a[1]
        time_c = time_b[1]
        price_c = price_b[1]
        time_d = time_c[1]
        price_d = price_c[1]
        time_e = time_d[1]
        price_e = price_d[1]
        time_f = time_e[1]
        price_f = price_e[1]
        time_g = time_f[1]
        price_g = price_f[1]
    AB_price_difference: float = math.abs(price_a - price_b)
    AB_time_difference: int = time_a - time_b
    def f_draw_zigzag_lines():
        _li: Persistent[Line] = na(Line)
        _li_color = color.teal if price_a > price_b else color.orange
        __block_result__ = na
        if is_new_zig:
            _li = line.new(time_a, price_a, time_b, price_b, xloc.bar_time, extend=extend.none, color=_li_color, width=2)
            __block_result__ = _li
        return __block_result__

    if show_zigzag_lines:
        f_draw_zigzag_lines()
    def f_draw_zigzag_labels(_text):
        _la: Persistent[Label] = na(Label)
        _la_color: Color = color.orange if price_a > price_b else color.teal
        _la_style: str = label.style_label_down if price_a > price_b else label.style_label_up
        _la_text: str = na(str)
        if show_pivot_price:
            _la_text = string.tostring(price_a, '#.#####') + _text if price_a > price_b else _text + string.tostring(price_a, '#.#####')
        else:
            _la_text = _text
        __block_result_1__ = na
        if is_new_zig:
            _la = label.new(x=time_a, y=price_a, text=_la_text, xloc=xloc.bar_time, yloc=yloc.price, style=_la_style, color=_la_color, textcolor=color.black, size=size.small)
            __block_result_1__ = _la
        return __block_result_1__

    def f_mode_process_stats(_weight, _data: Series):
        _avg_range: Series[float] = _data
        _max_range: Series[float] = 0.0
        if bar_index < 1:
            _avg_range = _data
        else:
            if ta.change(_data) != 0:
                _weight_data = _weight * _data
                _weight_previous = (1 - _weight) * nz(_avg_range[1], _data[1])
                _avg_range = _weight_data + _weight_previous
            else:
                _avg_range = _avg_range[1]
            _max_range = math.max(nz(_max_range[1], _data), _data)
        _pos_range = math.max(0.0, _data - _avg_range)
        _neg_range = math.min(0.0, _data - _avg_range)
        _pos_dev: PersistentSeries[float] = 0.0
        _neg_dev: PersistentSeries[float] = 0.0
        if bar_index >= 1:
            if ta.change(_pos_range) != 0:
                _pos_dev = _weight * _pos_range + (1 - _weight) * _pos_dev[1]
            else:
                _pos_dev = _pos_dev[1]
            if ta.change(_neg_range) != 0:
                _neg_dev = _weight * _neg_range + (1 - _weight) * _neg_dev[1]
            else:
                _neg_dev = _neg_dev[1]
        return (_avg_range, _max_range, _pos_dev, _neg_dev)

    weight = 2 / (__input_25__ + 1)
    price_avg_range, price_max_range, price_pos_dev, price_neg_dev = f_mode_process_stats(weight, AB_price_difference)
    time_avg_range, time_max_range, time_pos_dev, time_neg_dev = f_mode_process_stats(weight, AB_time_difference)
    target_avg_price = price_a - price_avg_range if price_a > price_b else price_a + price_avg_range
    target_price_upper_dev = price_a - price_avg_range - price_neg_dev if price_a > price_b else price_a + price_avg_range + price_neg_dev
    target_price_lower_dev = price_a - price_avg_range - price_pos_dev if price_a > price_b else price_a + price_avg_range + price_pos_dev
    target_price_0618_dev = price_a - (price_avg_range + price_neg_dev) * 0.618 if price_a > price_b else price_a + (price_avg_range + price_neg_dev) * 0.618
    target_price_1618_dev = price_a - (price_avg_range + price_pos_dev) * 1.618 if price_a > price_b else price_a + (price_avg_range + price_pos_dev) * 1.618
    target_avg_time = cast_int(time_a + time_avg_range)
    target_time_upper_dev = cast_int(target_avg_time + time_pos_dev)
    target_time_lower_dev = cast_int(target_avg_time + time_neg_dev)
    target_time_0618_dev = cast_int(time_a + (time_avg_range + time_neg_dev) * 0.618)
    target_time_1618_dev = cast_int(time_a + (time_avg_range + time_pos_dev) * 1.618)
    def f_cast_projections():
        line_midline: Persistent[Line] = na(Line)
        line_price_dev: Persistent[Line] = na(Line)
        line_time_dev: Persistent[Line] = na(Line)
        _la0618: Persistent[Label] = na(Label)
        _la1618: Persistent[Label] = na(Label)
        xtend = extend.right
        st_dash = line.style_dashed
        st_arrow = line.style_arrow_both
        line.delete(line_midline)
        line.delete(line_price_dev)
        line.delete(line_time_dev)
        label.delete(_la0618)
        label.delete(_la1618)
        line_midline = line.new(time_a, price_a, target_avg_time, target_avg_price, xloc.bar_time, extend=xtend, color=color.orange, style=st_dash, width=1)
        line_price_dev = line.new(target_avg_time, target_price_lower_dev, target_avg_time, target_price_upper_dev, xloc.bar_time, color=color.new('#0066FF'), style=st_arrow, width=1)
        line_time_dev = line.new(target_time_lower_dev, target_avg_price, target_time_upper_dev, target_avg_price, xloc.bar_time, color=color.new('#0066FF'), style=st_arrow, width=1)
        __block_result_2__ = na
        if show_projections_square_rates:
            _la0618 = label.new(x=target_time_1618_dev, y=target_price_1618_dev, text='Target 1.618 @ ' + string.tostring(target_price_1618_dev, '#.#####'), xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_down if is_up else label.style_label_up, color=color.new(color.silver, 20), textcolor=color.black, size=size.small)
            _la1618 = label.new(x=target_time_0618_dev, y=target_price_0618_dev, text='Target 0.618 @ ' + string.tostring(target_price_0618_dev, '#.#####'), xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_up if is_up else label.style_label_down, color=color.new(color.silver, 20), textcolor=color.black, size=size.small)
            __block_result_2__ = _la1618
        return __block_result_2__

    first_realtime_bar = barstate.islast and barstate.ishistory[1]
    if show_projections and (is_new_zig or first_realtime_bar):
        f_cast_projections()
    def f_line_rectangle(_x1, _y1, _x2, _y2, _xloc, _extend, _color, _style, _width):
        _side1: Persistent[Line] = na(Line)
        _side2: Persistent[Line] = na(Line)
        _side3: Persistent[Line] = na(Line)
        _side4: Persistent[Line] = na(Line)
        line.delete(_side1)
        line.delete(_side2)
        line.delete(_side3)
        line.delete(_side4)
        _side1 = line.new(x1=_x1, y1=_y1, x2=_x1, y2=_y2, xloc=_xloc, extend=_extend, color=_color, style=_style, width=_width)
        _side2 = line.new(x1=_x1, y1=_y2, x2=_x2, y2=_y2, xloc=_xloc, extend=_extend, color=_color, style=_style, width=_width)
        _side3 = line.new(x1=_x2, y1=_y2, x2=_x2, y2=_y1, xloc=_xloc, extend=_extend, color=_color, style=_style, width=_width)
        _side4 = line.new(x1=_x2, y1=_y1, x2=_x1, y2=_y1, xloc=_xloc, extend=_extend, color=_color, style=_style, width=_width)
        return _side4

    if show_projections and show_projections_square and (is_new_zig or first_realtime_bar):
        f_line_rectangle(target_time_0618_dev, target_price_0618_dev, target_time_1618_dev, target_price_1618_dev, xloc.bar_time, extend.none, color.gray, line.style_dashed, 2)
    def f_rate(_c, _b, _a):
        return (_a - _b) / (_b - _c)

    def f_timerate(_c, _b, _a):
        return (0 - (_a - _b)) / (_b - _c)

    def f_is_inrange(_value, _min, _max):
        return _value <= _max and _value >= _min

    def f_draw_rate_lines_and_label(_price_rate, _time_rate, _x1, _y1, _x2, _y2, _is_up):
        __block_result_3__ = na
        if show_triangle_rates:
            _text = 'Price: ' + string.tostring(_price_rate, '#.###') + ('' if not show_angles else ', (sin:' + string.tostring(nz(math.asin(_price_rate) * (180 / 3.1416), 0), '#') + 'º, cos:' + string.tostring(nz(math.acos(_price_rate) * (180 / 3.1416), 0), '#') + 'º' + ', tan:' + string.tostring(nz(math.atan(_price_rate) * (180 / 3.1416), 0), '#') + 'º)')
            _text = _text + '\nTime: ' + string.tostring(_time_rate, '#.###') + ('' if not show_angles else ', (sin:' + string.tostring(nz(math.asin(_time_rate) * (180 / 3.1416), 0), '#.###') + 'º, cos:' + string.tostring(nz(math.acos(_time_rate) * (180 / 3.1416), 0), '#.###') + 'º' + ', tan:' + string.tostring(nz(math.atan(_time_rate) * (180 / 3.1416), 0), '#.###') + 'º)')
            _li: Persistent[Line] = na(Line)
            _la: Persistent[Label] = na(Label)
            line.delete(_li)
            label.delete(_la)
            _li = line.new(x1=_x1, y1=_y1, x2=_x2, y2=_y2, xloc=xloc.bar_time, extend=extend.none, color=color.gray, style=line.style_dashed, width=1)
            _la = label.new(x=math.round((_x1 + _x2) / 2), y=(_y1 + _y2) / 2, text=_text, xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_up if _is_up else label.style_label_down, color=color.new(color.silver, 0), textcolor=color.black, size=size.small)
            __block_result_3__ = _la
        return __block_result_3__

    def isHarmonicTriangle(_cba, _margin_of_error):
        _return: bool = False
        for _i in pine_range(1, 12, 1):
            if f_is_inrange(_cba, -math.pow(1.618, -5 + _i) - _margin_of_error, -math.pow(1.618, -5 + _i) + _margin_of_error):
                _return = True
        return _return

    def is2Tap(_cba, _margin_of_error):
        _is_cba = f_is_inrange(_cba, -1.0 - _margin_of_error, -1.0 + _margin_of_error)
        return _is_cba

    def is3Tap(_edc, _cba, _margin_of_error):
        _is_edc = f_is_inrange(_edc, -1.0 - _margin_of_error, -1.0 + _margin_of_error)
        _is_cba = f_is_inrange(_cba, -1.0 - _margin_of_error, -1.0 + _margin_of_error)
        return cast_bool(_is_edc) and cast_bool(_is_cba)

    def is4Tap(_gfe, _edc, _cba, _margin_of_error):
        _is_gfe = f_is_inrange(_gfe, -1.0 - _margin_of_error, -1.0 + _margin_of_error)
        _is_edc = f_is_inrange(_edc, -1.0 - _margin_of_error, -1.0 + _margin_of_error)
        _is_cba = f_is_inrange(_cba, -1.0 - _margin_of_error, -1.0 + _margin_of_error)
        return cast_bool(_is_gfe) and cast_bool(_is_edc) and cast_bool(_is_cba)

    def isABCD(_cba, _dcb, _margin_of_error):
        _is_cba = f_is_inrange(_cba, -1.618 - _margin_of_error, -1.27 + _margin_of_error)
        _is_dcb = f_is_inrange(_dcb, -0.786 - _margin_of_error, -0.618 + _margin_of_error)
        return cast_bool(_is_cba) and cast_bool(_is_dcb)

    def isBat(_edc, _dcb, _cba, _eda, _margin_of_error):
        _is_edc = f_is_inrange(_edc, -0.5 - _margin_of_error, -0.382 + _margin_of_error)
        _is_dcb = f_is_inrange(_dcb, -0.886 - _margin_of_error, -0.382 + _margin_of_error)
        _is_cba = f_is_inrange(_cba, -2.618 - _margin_of_error, -1.618 + _margin_of_error)
        _is_eda = f_is_inrange(_eda, -0.886 - _margin_of_error, -0.886 + _margin_of_error)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    def isButterfly(_edc, _dcb, _cba, _eda, _margin_of_error):
        _is_edc = f_is_inrange(_edc, -0.786 - _margin_of_error, -0.786 + _margin_of_error)
        _is_dcb = f_is_inrange(_dcb, -0.886 - _margin_of_error, -0.382 + _margin_of_error)
        _is_cba = f_is_inrange(_cba, -2.618 - _margin_of_error, -1.618 + _margin_of_error)
        _is_eda = f_is_inrange(_eda, -1.618 - _margin_of_error, -1.27 + _margin_of_error)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    def isGartley(_edc, _dcb, _cba, _eda, _margin_of_error):
        _is_edc = f_is_inrange(_edc, -0.618 - _margin_of_error, -0.618 + _margin_of_error)
        _is_dcb = f_is_inrange(_dcb, -0.886 - _margin_of_error, -0.382 + _margin_of_error)
        _is_cba = f_is_inrange(_cba, -2.618 - _margin_of_error, -1.13 + _margin_of_error)
        _is_eda = f_is_inrange(_eda, -0.786 - _margin_of_error, -0.786 + _margin_of_error)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    def isCrab(_edc, _dcb, _cba, _eda, _margin_of_error):
        _is_edc = f_is_inrange(_edc, -0.886 - _margin_of_error, -0.886 + _margin_of_error)
        _is_dcb = f_is_inrange(_dcb, -0.886 - _margin_of_error, -0.382 + _margin_of_error)
        _is_cba = f_is_inrange(_cba, -3.618 - _margin_of_error, -2.0 + _margin_of_error)
        _is_eda = f_is_inrange(_eda, -1.618 - _margin_of_error, -1.618 + _margin_of_error)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    def isShark(_edc, _dcb, _cba, _eda, _margin_of_error):
        _is_edc = f_is_inrange(_edc, -0.886 - _margin_of_error, -0.886 + _margin_of_error)
        _is_dcb = f_is_inrange(_dcb, -1.618 - _margin_of_error, -1.13 + _margin_of_error)
        _is_cba = f_is_inrange(_cba, -2.24 - _margin_of_error, -1.27 + _margin_of_error)
        _is_eda = f_is_inrange(_eda, -1.13 - _margin_of_error, -0.886 + _margin_of_error)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    def is5o(_edc, _dcb, _cba, _eda, _margin_of_error):
        _is_edc = f_is_inrange(_edc, -1.618 - _margin_of_error, -1.13 + _margin_of_error)
        _is_dcb = f_is_inrange(_dcb, -2.24 - _margin_of_error, -1.618 + _margin_of_error)
        _is_cba = f_is_inrange(_cba, -0.5 - _margin_of_error, -0.5 + _margin_of_error)
        _is_eda = f_is_inrange(_eda, -0.236 - _margin_of_error, 0.236 + _margin_of_error)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    def isWolfe(_edc, _dcb, _cba, _eda, _margin_of_error):
        _is_edc = f_is_inrange(_edc, -1.618 - _margin_of_error, -1.27 + _margin_of_error)
        _is_dcb = f_is_inrange(_dcb, -5.0 - _margin_of_error, -0.0 + _margin_of_error)
        _is_cba = f_is_inrange(_cba, -1.618 - _margin_of_error, -1.27 + _margin_of_error)
        _is_eda = f_is_inrange(_eda, -5.0 - _margin_of_error, -0.0 + _margin_of_error)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    def isConTria(_edc, _dcb, _cba, _eda, _margin_of_error):
        _is_edc = f_is_inrange(_edc, -0.886 - _margin_of_error, -0.236 + _margin_of_error)
        _is_dcb = f_is_inrange(_dcb, -0.886 - _margin_of_error, -0.236 + _margin_of_error)
        _is_cba = f_is_inrange(_cba, -0.886 - _margin_of_error, -0.236 + _margin_of_error)
        _is_eda = f_is_inrange(_eda, -0.886 - _margin_of_error, -0.236 + _margin_of_error)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    def isExpTria(_edc, _dcb, _cba, _eda, _margin_of_error):
        _is_edc = f_is_inrange(_edc, -2.618 - _margin_of_error, -1.125 + _margin_of_error)
        _is_dcb = f_is_inrange(_dcb, -2.618 - _margin_of_error, -1.125 + _margin_of_error)
        _is_cba = f_is_inrange(_cba, -2.618 - _margin_of_error, -1.125 + _margin_of_error)
        _is_eda = f_is_inrange(_eda, -2.618 - _margin_of_error, -1.125 + _margin_of_error)
        return cast_bool(_is_edc) and cast_bool(_is_dcb) and cast_bool(_is_cba) and cast_bool(_is_eda)

    def isHnS(_fed, _feb, _dcb, _edc, _eda, _cba, _margin_of_error):
        _is_fed = f_is_inrange(_fed, -0.618 - _margin_of_error, -0.09 + _margin_of_error)
        _is_feb = f_is_inrange(_feb, -0.886 - _margin_of_error, -0.09 + _margin_of_error)
        _is_edc = f_is_inrange(_edc, -9.999 - _margin_of_error, -1.0 + _margin_of_error)
        _is_eda = f_is_inrange(_eda, -1.618 - _margin_of_error, -0.09 + _margin_of_error)
        _is_dcb = f_is_inrange(_dcb, -1.25 - _margin_of_error, -0.75 + _margin_of_error)
        _is_cba = f_is_inrange(_cba, -0.886 - _margin_of_error, -0.09 + _margin_of_error)
        return cast_bool(_is_fed) and cast_bool(_is_feb) and cast_bool(_is_edc) and cast_bool(_is_eda) and cast_bool(_is_dcb) and cast_bool(_is_cba)

    def f_Detect_Patterns(_percent_of_error):
        _pattern_label_placeholder: str = ''
        _margin_of_error: float = _percent_of_error / 100
        price_gfe: Persistent[float] = na(float)
        time_gfe: Persistent[float] = na(float)
        price_gfc: Persistent[float] = na(float)
        time_gfc: Persistent[float] = na(float)
        price_gfa: Persistent[float] = na(float)
        time_gfa: Persistent[float] = na(float)
        price_gdc: Persistent[float] = na(float)
        time_gdc: Persistent[float] = na(float)
        price_gda: Persistent[float] = na(float)
        time_gda: Persistent[float] = na(float)
        price_gba: Persistent[float] = na(float)
        time_gba: Persistent[float] = na(float)
        price_fed: Persistent[float] = na(float)
        time_fed: Persistent[float] = na(float)
        price_feb: Persistent[float] = na(float)
        time_feb: Persistent[float] = na(float)
        price_fcb: Persistent[float] = na(float)
        time_fcb: Persistent[float] = na(float)
        price_edc: Persistent[float] = na(float)
        time_edc: Persistent[float] = na(float)
        price_eda: Persistent[float] = na(float)
        time_eda: Persistent[float] = na(float)
        price_eba: Persistent[float] = na(float)
        time_eba: Persistent[float] = na(float)
        price_dcb: Persistent[float] = na(float)
        time_dcb: Persistent[float] = na(float)
        price_cba: Persistent[float] = na(float)
        time_cba: Persistent[float] = na(float)
        price_gfc = f_rate(price_g, price_f, price_c)
        time_gfc = f_timerate(time_g, time_f, time_c)
        price_gfa = f_rate(price_g, price_f, price_a)
        time_gfa = f_timerate(time_g, time_f, time_a)
        price_gdc = f_rate(price_g, price_d, price_c)
        time_gdc = f_timerate(time_g, time_d, time_c)
        price_gda = f_rate(price_g, price_d, price_a)
        time_gda = f_timerate(time_g, time_d, time_a)
        price_gfe = f_rate(price_g, price_f, price_e)
        time_gfe = f_timerate(time_g, time_f, time_e)
        price_gba = f_rate(price_g, price_b, price_a)
        time_gba = f_timerate(time_g, time_b, time_a)
        price_fed = f_rate(price_f, price_e, price_d)
        time_fed = f_timerate(time_f, time_e, time_d)
        price_feb = f_rate(price_f, price_e, price_b)
        time_feb = f_timerate(time_f, time_e, time_b)
        price_fcb = f_rate(price_f, price_c, price_b)
        time_fcb = f_timerate(time_f, time_c, time_b)
        price_edc = f_rate(price_e, price_d, price_c)
        time_edc = f_timerate(time_e, time_d, time_c)
        price_eda = f_rate(price_e, price_d, price_a)
        time_eda = f_timerate(time_e, time_d, time_a)
        price_eba = f_rate(price_e, price_b, price_a)
        time_eba = f_timerate(time_e, time_b, time_a)
        price_dcb = f_rate(price_d, price_c, price_b)
        time_dcb = f_timerate(time_d, time_c, time_b)
        price_cba = f_rate(price_c, price_b, price_a)
        time_cba = f_timerate(time_c, time_b, time_a)
        if show_patterns:
            _isvalid_gfa: bool = price_fed >= -1 and price_feb >= -1 and (price_cba <= -1) and (price_eda <= -1)
            _isvalid_gda: bool = price_fed <= -1 and price_gfe >= -1 and (price_cba <= -1) and (price_dcb >= -1)
            _isvalid_gba: bool = price_feb <= -1 and price_gfe >= -1 and (price_cba <= -1) and (price_dcb <= -1)
            _isvalid_eba: bool = price_cba <= -1 and price_dcb <= -1
            _isvalid_eda: bool = price_cba <= -1 and price_dcb >= -1
            _isvalid_fcb: bool = price_fed >= -1 and price_edc <= -1
            _isvalid_feb: bool = price_edc >= -1 and price_dcb <= -1
            _pattern_list: str = '\n'
            if show_harmonic:
                if isHarmonicTriangle(price_gfa, _margin_of_error) and _isvalid_gfa:
                    _pattern_list = _pattern_list + '• Harmonic Triangle(GFA) •\n'
                if isHarmonicTriangle(price_gda, _margin_of_error) and _isvalid_gda:
                    _pattern_list = _pattern_list + '• Harmonic Triangle(GDA) •\n'
                if isHarmonicTriangle(price_gba, _margin_of_error) and _isvalid_gba:
                    _pattern_list = _pattern_list + '• Harmonic Triangle(GBA) •\n'
                if isHarmonicTriangle(price_eba, _margin_of_error) and _isvalid_eba:
                    _pattern_list = _pattern_list + '• Harmonic Triangle(EBA) •\n'
                if isHarmonicTriangle(price_eda, _margin_of_error) and _isvalid_eda:
                    _pattern_list = _pattern_list + '• Harmonic Triangle(EDA) •\n'
                if isHarmonicTriangle(price_cba, _margin_of_error):
                    _pattern_list = _pattern_list + '• Harmonic Triangle(CBA) •\n'
            if show_tap:
                if is2Tap(price_cba, _margin_of_error):
                    _pattern_list = _pattern_list + '• Double Tap(CBA) •\n'
                if is2Tap(price_eba, _margin_of_error) and _isvalid_eba:
                    _pattern_list = _pattern_list + '• Double Tap(EBA) •\n'
                if is2Tap(price_eda, _margin_of_error) and _isvalid_eda:
                    _pattern_list = _pattern_list + '• Double Tap(EDA) •\n'
            if show_tap:
                if is3Tap(price_edc, price_cba, _margin_of_error):
                    _pattern_list = _pattern_list + '• Triple Tap(EDC, CBA) •\n'
            if show_tap:
                if is4Tap(price_gfe, price_edc, price_cba, _margin_of_error):
                    _pattern_list = _pattern_list + '• Quadruple Tap(GFE, EDC, CBA) •\n'
            if show_abcd:
                if isABCD(price_cba, price_dcb, _margin_of_error):
                    _pattern_list = _pattern_list + '• AB=CD(CBA, DCB) •\n'
                if isABCD(price_cba, price_fcb, _margin_of_error) and _isvalid_fcb:
                    _pattern_list = _pattern_list + '• AB=CD(CBA, FCB) •\n'
                if isABCD(price_eba, price_feb, _margin_of_error) and _isvalid_feb:
                    _pattern_list = _pattern_list + '• AB=CD(EBA, FEB) •\n'
                if isABCD(price_eda, price_fed, _margin_of_error) and _isvalid_eda:
                    _pattern_list = _pattern_list + '• AB=CD(EDA, FED) •\n'
            if show_bat:
                if isBat(price_edc, price_dcb, price_cba, price_eda, _margin_of_error):
                    _pattern_list = _pattern_list + '• Bat(EDC, DCB, CBA, EDA) •\n'
                if isBat(price_gfe, price_feb, price_eba, price_gfa, _margin_of_error) and _isvalid_eba:
                    _pattern_list = _pattern_list + '• Bat(GFE, FEB, EBA, GFA) •\n'
                if isBat(price_gfe, price_fed, price_eda, price_gfa, _margin_of_error) and _isvalid_eda:
                    _pattern_list = _pattern_list + '• Bat(GFE, FED, EDA, GFA) •\n'
            if show_butterfly:
                if isButterfly(price_edc, price_dcb, price_cba, price_eda, _margin_of_error):
                    _pattern_list = _pattern_list + '• Butterfly(EDC, DCB, CBA, EDA) •\n'
                if isButterfly(price_gfe, price_feb, price_eba, price_gfa, _margin_of_error) and _isvalid_eba:
                    _pattern_list = _pattern_list + '• Butterfly(GFE, FEB, EBA, GFA) •\n'
                if isButterfly(price_gfe, price_fed, price_eda, price_gfa, _margin_of_error) and _isvalid_eda:
                    _pattern_list = _pattern_list + '• Butterfly(GFE, FED, EDA, GFA) •\n'
            if show_gartley:
                if isGartley(price_edc, price_dcb, price_cba, price_eda, _margin_of_error):
                    _pattern_list = _pattern_list + '• Gartley(EDC, DCB, CBA, EDA) •\n'
                if isGartley(price_gfe, price_feb, price_eba, price_gfa, _margin_of_error) and _isvalid_eba:
                    _pattern_list = _pattern_list + '• Gartley(GFE, FEB, EBA, GFA) •\n'
                if isGartley(price_gfe, price_fed, price_eda, price_gfa, _margin_of_error) and _isvalid_eda:
                    _pattern_list = _pattern_list + '• Gartley(GFE, FED, EDA, GFA) •\n'
            if show_crab:
                if isCrab(price_edc, price_dcb, price_cba, price_eda, _margin_of_error):
                    _pattern_list = _pattern_list + '• Crab(EDC, DCB, CBA, EDA) •\n'
                if isCrab(price_gfe, price_feb, price_eba, price_gfa, _margin_of_error) and _isvalid_eba:
                    _pattern_list = _pattern_list + '• Crab(GFE, FEB, EBA, GFA) •\n'
                if isCrab(price_gfe, price_fed, price_eda, price_gfa, _margin_of_error) and _isvalid_eda:
                    _pattern_list = _pattern_list + '• Crab(GFE, FED, EDA, GFA) •\n'
            if show_shark:
                if isShark(price_edc, price_dcb, price_cba, price_eda, _margin_of_error):
                    _pattern_list = _pattern_list + '• Shark(EDC, DCB, CBA, EDA) •\n'
                if isShark(price_gfe, price_feb, price_eba, price_gfa, _margin_of_error) and _isvalid_eba:
                    _pattern_list = _pattern_list + '• Shark(GFE, FEB, EBA, GFA) •\n'
                if isShark(price_gfe, price_fed, price_eda, price_gfa, _margin_of_error) and _isvalid_eda:
                    _pattern_list = _pattern_list + '• Shark(GFE, FED, EDA, GFA) •\n'
            if show_5o:
                if is5o(price_edc, price_dcb, price_cba, price_eda, _margin_of_error):
                    _pattern_list = _pattern_list + '• 5o(EDC, DCB, CBA, EDA) •\n'
                if is5o(price_gfe, price_feb, price_eba, price_gfa, _margin_of_error) and _isvalid_eba:
                    _pattern_list = _pattern_list + '• 5o(GFE, FEB, EBA, GFA) •\n'
                if is5o(price_gfe, price_fed, price_eda, price_gfa, _margin_of_error) and _isvalid_eda:
                    _pattern_list = _pattern_list + '• 5o(GFE, FED, EDA, GFA) •\n'
            if show_wolfe:
                if isWolfe(price_edc, price_dcb, price_cba, price_eda, _margin_of_error):
                    _pattern_list = _pattern_list + '• Wolf(EDC, DCB, CBA, EDA) •\n'
                if isWolfe(price_gfe, price_feb, price_eba, price_gfa, _margin_of_error) and _isvalid_eba:
                    _pattern_list = _pattern_list + '• Wolf(GFE, FEB, EBA, GFA) •\n'
                if isWolfe(price_gfe, price_fed, price_eda, price_gfa, _margin_of_error) and _isvalid_eda:
                    _pattern_list = _pattern_list + '• Wolf(GFE, FED, EDA, GFA) •\n'
            if show_contria:
                if isConTria(price_edc, price_dcb, price_cba, price_eda, _margin_of_error):
                    _pattern_list = _pattern_list + '• Contracting Triangle(EDC, DCB, CBA, EDA) •\n'
                if isConTria(price_gfe, price_feb, price_eba, price_gfa, _margin_of_error) and _isvalid_eba:
                    _pattern_list = _pattern_list + '• Contracting Triangle(GFE, FEB, EBA, GFA) •\n'
                if isConTria(price_gfe, price_fed, price_eda, price_gfa, _margin_of_error) and _isvalid_eda:
                    _pattern_list = _pattern_list + '• Contracting Triangle(GFE, FED, EDA, GFA) •\n'
            if show_exptria:
                if isExpTria(price_edc, price_dcb, price_cba, price_eda, _margin_of_error):
                    _pattern_list = _pattern_list + '• Expanding Triangle(EDC, DCB, CBA, EDA) •\n'
                if isExpTria(price_gfe, price_feb, price_eba, price_gfa, _margin_of_error) and _isvalid_eba:
                    _pattern_list = _pattern_list + '• Expanding Triangle(GFE, FEB, EBA, GFA) •\n'
                if isExpTria(price_gfe, price_fed, price_eda, price_gfa, _margin_of_error) and _isvalid_eda:
                    _pattern_list = _pattern_list + '• Expanding Triangle(GFE, FED, EDA, GFA) •\n'
            if show_hns:
                if isHnS(price_fed, price_feb, price_dcb, price_edc, price_eda, price_cba, _margin_of_error):
                    _pattern_list = _pattern_list + '• Head and Shoulders(FED, FEB, DCB, EDC, EDA, CBA) •\n'
            f_draw_zigzag_labels(_pattern_list)
        else:
            if show_pivot_price:
                f_draw_zigzag_labels('')
        __block_result_4__ = na
        if show_triangle_rates:
            if price_cba < price_edc and price_edc < price_gfe:
                f_draw_rate_lines_and_label(price_gfa, time_gfa, time_a, price_a, time_g, price_g, price_a < price_f)
                f_draw_rate_lines_and_label(price_gda, time_gda, time_a, price_a, time_g, price_g, price_a < price_d)
                f_draw_rate_lines_and_label(price_gba, time_gba, time_a, price_a, time_g, price_g, price_a < price_b)
            if price_cba < price_edc:
                f_draw_rate_lines_and_label(price_eda, time_eda, time_a, price_a, time_e, price_e, price_a < price_d)
                f_draw_rate_lines_and_label(price_eba, time_eba, time_a, price_a, time_e, price_e, price_a < price_b)
            f_draw_rate_lines_and_label(price_cba, time_cba, time_a, price_a, time_c, price_c, price_a < price_b)
            f_draw_rate_lines_and_label(price_dcb, time_dcb, time_b, price_b, time_d, price_d, price_b < price_c)
            __block_result_5__ = na
            if price_dcb < price_fed:
                __block_result_5__ = f_draw_rate_lines_and_label(price_feb, time_feb, time_b, price_b, time_f, price_f, price_b < price_e)
            __block_result_4__ = __block_result_5__
        return __block_result_4__

    if (show_pivot_price or show_patterns) and is_new_zig:
        f_Detect_Patterns(err)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
