"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool, cast_int
from pynecore.lib import (
    array, bar_index, barstate, box, color, extend, input, label, line, math,
    na, nz, plot, script, size, string, ta, time, volume, xloc, yloc
)
from pynecore.types import Box, Color, Label, Line, NA, Persistent, PersistentSeries, Series
import lib.RicardoSantos.ColorExtension.v4 as colore
import lib.RicardoSantos.FunctionZigZagMultipleMethods.v1 as zigzag
import lib.RicardoSantos.HarmonicPattern.v3 as pattern

m_000: str = '(MANUAL) Percent price move over X * Y'
m_001: str = 'Percent price move over atr(X) * Y'
m_002: str = 'Percent price move over max(tr) * Y'
m_003: str = 'high or low pivot(X, Y)'
m_004: str = 'Price Action'


@script.indicator(title='[RS]ZigZag Multiple Methods - Forecast - patterns - labels', shorttitle='ZZ', overlay=True)
def main(
    show_real_pivots=input.bool(defval=True, title='Show real zigzag pivots:', group='ZigZag Options:'),
    show_zigzag_lines=input.bool(defval=True, title='Show zigzag lines:', group='ZigZag Options:'),
    zigzag_method=input.string(defval=m_000, title='Method to use for the zigzag:', options=(m_000, m_001, m_002, m_003, m_004), group='ZigZag Options:'),
    param_x=input.float(defval=1.0, title='parameter X', group='ZigZag Options:'),
    param_y=input.float(defval=1.0, title='parameter Y', group='ZigZag Options:'),
    show_pivot_price=input.bool(defval=True, title='Show price labels on zigzag:', group='Label Options:'),
    show_triangle_rates=input.bool(defval=True, title='Show rate labels on triangles:', group='Label Options:'),
    show_angles=input.bool(defval=False, title='Show Angle Degree information(EXPERIMENTAL):', group='Label Options:'),
    show_patterns=input.bool(defval=True, title='Show Patterns:', group='Pattern Options:'),
    err=input.float(defval=5.0, title='Pattern Error Margin:', group='Pattern Options:'),
    show_projections=input.bool(defval=True, title='Show projections forecast of zigzag:', group='Projection Options:'),
    show_projections_square=input.bool(defval=True, title='Show projections forecast Bounds:', group='Projection Options:'),
    show_projections_square_rates=input.bool(defval=False, title='Show projections target rates:', group='Projection Options:'),
    __input_13__=input.float(defval=10.0, title='Averaging Weight:', group='Projection Options:'),
    i_color_hue_zig=input.int(defval=175, minval=0, maxval=360, title='Zig Color Hue:', group='Color Profile'),
    i_color_hue_zag=input.int(defval=20, minval=0, maxval=360, title='Zag Color Hue:', group='Color Profile'),
    i_color_hue_rate=input.int(defval=200, minval=0, maxval=360, title='Rate Color Hue:', group='Color Profile'),
    i_color_hue_ptarget=input.int(defval=200, minval=0, maxval=360, title='Proj. target Color Hue:', group='Color Profile'),
    i_color_hue_zigbox=input.int(defval=175, minval=0, maxval=360, title='Zig Proj. box Color Hue:', group='Color Profile'),
    i_color_hue_zagbox=input.int(defval=20, minval=0, maxval=360, title='Zag Proj. box Color Hue:', group='Color Profile'),
    i_color_reverse=input.color(defval=color.gray, title='Reverse Line:', group='Color Profile'),
    i_color_saturation=input.int(defval=80, minval=0, maxval=100, title='Color Saturation:', group='Color Profile'),
    i_color_lightness=input.int(defval=70, minval=0, maxval=100, title='Color Lightness:', group='Color Profile'),
    i_label_text_size=input.string(defval=size.small, title='Text Size:', options=(size.tiny, size.small, size.normal, size.large, size.huge, size.auto), group='Color Profile')
):
    weight: float = 2 / (__input_13__ + 1)
    i_color_transparency: int = 0
    c_zig: Color = colore.hsl(i_color_hue_zig, i_color_saturation, i_color_lightness, i_color_transparency)
    c_zag: Color = colore.hsl(i_color_hue_zag, i_color_saturation, i_color_lightness, i_color_transparency)
    c_rate: Color = colore.hsl(i_color_hue_rate, 10, i_color_lightness, i_color_transparency)
    c_ptarget: Color = colore.hsl(i_color_hue_ptarget, i_color_saturation, i_color_lightness, i_color_transparency)
    c_zigbox: Color = colore.hsl(i_color_hue_zigbox, i_color_saturation, i_color_lightness, 75)
    c_zagbox: Color = colore.hsl(i_color_hue_zigbox, i_color_saturation, i_color_lightness, 75)
    c_text: Color = colore.hsl(200, 10, 100 - i_color_lightness, i_color_transparency)
    price_a: Series
    price_a, is_up, reverse, _rl_time = zigzag.function(zigzag_method, param_x, param_y)
    alt_time = _rl_time if show_real_pivots else time
    zz_color = c_zag if is_up else c_zig
    is_new_zig = price_a if ta.change(price_a) != 0 else na
    plot(reverse, title='R', color=i_color_reverse, style=plot.style_stepline, linewidth=1, offset=1)
    plot(reverse, title='R', color=i_color_reverse, style=plot.style_circles, linewidth=4, offset=1, show_last=1)
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
    cumvol: int = cast_int(ta.cum(volume))
    vol_a: PersistentSeries[int] = na(int)
    vol_b: Persistent[int] = na(int)
    if cast_bool(is_new_zig):
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
        vol_a = cumvol
        vol_b = vol_a[1]
    AB_price_difference: float = math.abs(price_a - price_b)
    AB_time_difference: int = time_a - time_b
    AB_volume: int = vol_a - vol_b
    max_zigzag_lines: int = 20
    zigzag_lines: Persistent[list[Line]] = array.new_line(max_zigzag_lines, NA(Line))
    def f_draw_zigzag_lines():
        _li: Persistent[Line] = na(Line)
        _li_color = c_zig if price_a > price_b else c_zag
        __block_result__ = na
        if cast_bool(is_new_zig):
            if array.size(zigzag_lines) >= max_zigzag_lines:
                line.delete(array.pop(zigzag_lines))
            _li = line.new(time_a, price_a, time_b, price_b, xloc.bar_time, extend=extend.none, color=_li_color, width=2)
            __block_result__ = array.unshift(zigzag_lines, _li)
        return __block_result__

    if show_zigzag_lines:
        f_draw_zigzag_lines()
    max_zigzag_labels: int = 20
    zigzag_labels: Persistent[list[Label]] = array.new_label(max_zigzag_labels, NA(Label))
    def f_draw_zigzag_labels(_text):
        _la: Persistent[Label] = na(Label)
        _la_color: Color = c_zag if price_a > price_b else c_zig
        _la_style: str = label.style_label_down if price_a > price_b else label.style_label_up
        _la_text: str = na(str)
        if show_pivot_price:
            _la_text = string.tostring(price_a, '#.#####') + ', V: ' + string.tostring(AB_volume, '#') + _text if price_a > price_b else _text + string.tostring(price_a, '#.#####') + ', V: ' + string.tostring(AB_volume, '#')
        else:
            _la_text = _text
        __block_result_1__ = na
        if cast_bool(is_new_zig):
            if array.size(zigzag_labels) >= max_zigzag_labels:
                label.delete(array.pop(zigzag_labels))
            _la = label.new(x=time_a, y=price_a, text=_la_text, xloc=xloc.bar_time, yloc=yloc.price, style=_la_style, color=_la_color, textcolor=c_text, size=i_label_text_size)
            __block_result_1__ = array.unshift(zigzag_labels, _la)
        return __block_result_1__

    def f_mode_process_stats(_weight, _data: Series):
        _avg_range: Series[float] = _data
        _max_range: Series[float] = 0.0
        if bar_index < 1:
            _avg_range = _data
        else:
            if _data != _data[1]:
                _weight_data = _weight * _data
                _weight_previous = (1 - _weight) * nz(_avg_range[1], _data[1])
                _avg_range = _weight_data + _weight_previous
            else:
                _avg_range = _avg_range[1]
            _max_range = math.max(nz(_max_range[1], _data), _data)
        _pos_range: Series = math.max(0.0, _data - _avg_range)
        _neg_range: Series = math.min(0.0, _data - _avg_range)
        _pos_dev: PersistentSeries[float] = 0.0
        _neg_dev: PersistentSeries[float] = 0.0
        if bar_index >= 1:
            if _pos_range != _pos_range[1]:
                _pos_dev = _weight * _pos_range + (1 - _weight) * _pos_dev[1]
            else:
                _pos_dev = _pos_dev[1]
            if _neg_range != _neg_range[1]:
                _neg_dev = _weight * _neg_range + (1 - _weight) * _neg_dev[1]
            else:
                _neg_dev = _neg_dev[1]
        return (_avg_range, _max_range, _pos_dev, _neg_dev)

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
    max_forecast_boxs: int = 1
    forecast_boxs: Persistent[list[Box]] = array.new_box(max_forecast_boxs, NA(Box))
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
        line_midline = line.new(time_a, price_a, target_avg_time, target_avg_price, xloc.bar_time, extend=xtend, color=c_ptarget, style=st_dash, width=1)
        line_price_dev = line.new(target_avg_time, target_price_lower_dev, target_avg_time, target_price_upper_dev, xloc.bar_time, color=c_ptarget, style=st_arrow, width=1)
        line_time_dev = line.new(target_time_lower_dev, target_avg_price, target_time_upper_dev, target_avg_price, xloc.bar_time, color=c_ptarget, style=st_arrow, width=1)
        __block_result_2__ = na
        if show_projections_square:
            if array.size(forecast_boxs) >= max_forecast_boxs:
                box.delete(array.pop(forecast_boxs))
            _c = c_zigbox if is_up else c_zagbox
            _bo = box.new(left=target_time_0618_dev, top=target_price_0618_dev, right=target_time_1618_dev, bottom=target_price_1618_dev, border_color=color.gray, border_style=line.style_dashed, border_width=1, xloc=xloc.bar_time, extend=extend.none, bgcolor=_c)
            array.unshift(forecast_boxs, _bo)
            __block_result_3__ = na
            if show_projections_square_rates:
                _la0618 = label.new(x=target_time_1618_dev, y=target_price_1618_dev, text='Max. Target 1.618 @ ' + string.tostring(target_price_1618_dev, '#.#####'), xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_down if is_up else label.style_label_up, color=c_rate, textcolor=c_text, size=i_label_text_size, tooltip='Likelyhood taken from the zigzag swing distribution.')
                _la1618 = label.new(x=target_time_0618_dev, y=target_price_0618_dev, text='Min. Target 0.618 @ ' + string.tostring(target_price_0618_dev, '#.#####'), xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_up if is_up else label.style_label_down, color=c_rate, textcolor=c_text, size=i_label_text_size, tooltip='Likelyhood taken from the zigzag swing distribution.')
                __block_result_3__ = _la1618
            __block_result_2__ = __block_result_3__
        return __block_result_2__

    first_realtime_bar = barstate.islast and barstate.ishistory[1]
    if show_projections and (cast_bool(is_new_zig) or first_realtime_bar):
        f_cast_projections()
    def f_draw_rate_lines_and_label(_price_rate, _time_rate, _x1, _y1, _x2, _y2, _is_up):
        __block_result_4__ = na
        if show_triangle_rates:
            _text = 'Price: ' + string.tostring(_price_rate, '#.###') + ('' if not show_angles else ', (sin:' + string.tostring(nz(math.asin(_price_rate) * (180 / 3.1416), 0), '#') + 'º, cos:' + string.tostring(nz(math.acos(_price_rate) * (180 / 3.1416), 0), '#') + 'º' + ', tan:' + string.tostring(nz(math.atan(_price_rate) * (180 / 3.1416), 0), '#') + 'º)')
            _text = _text + '\nTime: ' + string.tostring(_time_rate, '#.###') + ('' if not show_angles else ', (sin:' + string.tostring(nz(math.asin(_time_rate) * (180 / 3.1416), 0), '#.###') + 'º, cos:' + string.tostring(nz(math.acos(_time_rate) * (180 / 3.1416), 0), '#.###') + 'º' + ', tan:' + string.tostring(nz(math.atan(_time_rate) * (180 / 3.1416), 0), '#.###') + 'º)')
            _li: Persistent[Line] = na(Line)
            _la: Persistent[Label] = na(Label)
            line.delete(_li)
            label.delete(_la)
            _li = line.new(x1=_x1, y1=_y1, x2=_x2, y2=_y2, xloc=xloc.bar_time, extend=extend.none, color=color.gray, style=line.style_dashed, width=1)
            _la = label.new(x=math.round((_x1 + _x2) / 2), y=(_y1 + _y2) / 2, text=_text, xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_up if _is_up else label.style_label_down, color=c_rate, textcolor=c_text, size=i_label_text_size)
            __block_result_4__ = _la
        return __block_result_4__

    def f_Detect_Patterns(_percent_of_error):
        _pattern_label_placeholder: str = ''
        _margin_of_error: float = _percent_of_error / 100
        if show_patterns:
            _format: str = '{0}\n' if is_up else '\n{0}'
            _pattern_list: list[str] = pattern.extract(price_g, price_f, price_e, price_d, price_c, price_b, price_a, _margin_of_error)
            f_draw_zigzag_labels(string.format(_format, array.join(_pattern_list, '\n')) if array.size(_pattern_list) > 0 else '')
        else:
            if show_pivot_price:
                f_draw_zigzag_labels('')
        __block_result_5__ = na
        if show_triangle_rates:
            _price_cba: float = pattern.line_price_rate(price_c, price_b, price_a)
            _price_edc: float = pattern.line_price_rate(price_e, price_d, price_c)
            _price_gfe: float = pattern.line_price_rate(price_g, price_f, price_e)
            _price_dcb: float = pattern.line_price_rate(price_d, price_c, price_b)
            if _price_cba < _price_edc and _price_edc < _price_gfe:
                f_draw_rate_lines_and_label(pattern.line_price_rate(price_g, price_f, price_a), pattern.line_time_rate(time_g, time_f, time_a), time_a, price_a, time_g, price_g, price_a < price_f)
                f_draw_rate_lines_and_label(pattern.line_price_rate(price_g, price_d, price_a), pattern.line_time_rate(time_g, time_d, time_a), time_a, price_a, time_g, price_g, price_a < price_d)
                f_draw_rate_lines_and_label(pattern.line_price_rate(price_g, price_b, price_a), pattern.line_time_rate(time_g, time_b, time_a), time_a, price_a, time_g, price_g, price_a < price_b)
            if _price_cba < _price_edc:
                f_draw_rate_lines_and_label(pattern.line_price_rate(price_e, price_d, price_a), pattern.line_time_rate(time_e, time_d, time_a), time_a, price_a, time_e, price_e, price_a < price_d)
                f_draw_rate_lines_and_label(pattern.line_price_rate(price_e, price_b, price_a), pattern.line_time_rate(time_e, time_b, time_a), time_a, price_a, time_e, price_e, price_a < price_b)
            f_draw_rate_lines_and_label(_price_cba, pattern.line_time_rate(time_c, time_b, time_a), time_a, price_a, time_c, price_c, price_a < price_b)
            f_draw_rate_lines_and_label(_price_dcb, pattern.line_time_rate(time_d, time_c, time_b), time_b, price_b, time_d, price_d, price_b < price_c)
            __block_result_6__ = na
            if _price_dcb < pattern.line_price_rate(price_f, price_e, price_d):
                __block_result_6__ = f_draw_rate_lines_and_label(pattern.line_price_rate(price_f, price_e, price_b), pattern.line_time_rate(time_f, time_e, time_b), time_b, price_b, time_f, price_f, price_b < price_e)
            __block_result_5__ = __block_result_6__
        return __block_result_5__

    if (show_pivot_price or show_patterns) and cast_bool(is_new_zig):
        f_Detect_Patterns(err)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)