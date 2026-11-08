"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, array, barcolor, close, color, extend, high, input, line,
    location, low, math, na, open, plot, plotshape, script, shape, size, string, ta, time, xloc
)
from pynecore.types import Color, Line, Persistent, PersistentSeries, Series


@script.indicator(title='Trendlines - JD', shorttitle='Trendlines', overlay=True, na_bool=True)
def main(
    len=input(30, title='loockback length pivots'),
    wicks=input(True, title='Draw lines from wicks (checked) or real bodies (unchecked)?'),
    disp_select=input(True, title='Display only falling \'high\' and rising \'low\' trendlines?'),
    do_mono=input(False, title='checked = monochrome lines, unchecked = direction colored lines?'),
    limit_extension=input.int(2, title='Limit extensions of the lines? 0 = infinite, other values x 50 bars', minval=0),
    do_alerts=input(True, title='show trendline breaks'),
    limit_trendline_nr=input(False, title='limit number of trendlines shown (value in next setting calculates the lookback period)'),
    trendline_nr=input.int(5, title='number of trendlines to show (select true above to limit)', minval=1, maxval=50),
    trendline_check_nr=input.int(1, title='number of past trendlines to check for breaks', minval=1, maxval=50),
    select_breaks=input(True, title='only display \'long\' breaks on trendlines connecting \'highs\' and \'short\' for \'lows\''),
    log_chart=input(False, title='USING A LOG CHART? MAKE SURE TO CHECK THIS BOX!!')
):
    bar_time = time - time[1]
    color_rising: Persistent[Color] = color.teal if do_mono else color.lime
    color_falling: Persistent[Color] = color.teal if do_mono else color.fuchsia
    def f_get_slope(_x1, _y1, _x2, _y2):
        _slope = (math.log(_y2) - math.log(_y1)) / (_x2 - _x1) if log_chart else (_y2 - _y1) / (_x2 - _x1)
        return _slope

    def line_get_price(_start_time, _start_price, _slope, _lookback_period, _log_chart):
        current_price: Persistent[float] = 0.0
        elapsed_time = time - _start_time
        current_price = _start_price * math.exp((elapsed_time - _lookback_period * bar_time) * _slope) if _log_chart else _start_price + (elapsed_time - _lookback_period * bar_time) * _slope
        return current_price

    def line_cross(_check_value: Series, _start_time, _start_price, _slope, _log_chart):
        current_value: Persistent[float] = 0.0
        previous_value: Persistent[float] = 0.0
        current_value = line_get_price(_start_time, _start_price, _slope, 0, _log_chart)
        previous_value = line_get_price(_start_time, _start_price, _slope, 1, _log_chart)
        cross = 1 if _check_value[1] < previous_value and _check_value > current_value else -1 if _check_value[1] > previous_value and _check_value < current_value else 0
        return cross

    def f_df_array_new(_nr_of_sheets, _nr_of_rows, _nr_of_columns, _fill):
        _array_size = 3 + _nr_of_sheets * _nr_of_rows * _nr_of_columns
        _m: list[float] = array.new_float(_array_size, _fill)
        array.set(_m, 0, _nr_of_sheets)
        array.set(_m, 1, _nr_of_rows)
        array.set(_m, 2, _nr_of_columns)
        return _m

    def f_df_array_get_size(_m):
        _nr_of_sheets = cast_int(array.get(_m, 0))
        _nr_of_rows = cast_int(array.get(_m, 1))
        _nr_of_columns = cast_int(array.get(_m, 2))
        return (_nr_of_sheets, _nr_of_rows, _nr_of_columns)

    def f_df_array_get_sheet_index_range(_m, _sheet_index):
        _nr_of_sheets, _nr_of_rows, _nr_of_columns = f_df_array_get_size(_m)
        _start_index = 3 + math.min(_sheet_index, _nr_of_sheets - 1) * _nr_of_rows * _nr_of_columns
        _end_index = _start_index + _nr_of_rows * _nr_of_columns - 1
        return (_start_index, _end_index)

    def f_df_array_add_new_record(_m, _sheet_index, _record):
        _nr_of_sheets, _nr_of_rows, _nr_of_columns = f_df_array_get_size(_m)
        __block_result__ = na
        if array.size(_record) == 3:
            _sheet_start_index, _sheet_end_index = f_df_array_get_sheet_index_range(_m, _sheet_index)
            _sheet = array.slice(_m, _sheet_start_index, _sheet_end_index + 1)
            __block_result_1__ = na
            for i in pine_range(3 - 1, 0, 1):
                array.unshift(_sheet, array.get(_record, i))
                __block_result_1__ = array.pop(_sheet)
            __block_result__ = __block_result_1__
        return __block_result__

    def f_df_array_get_record(_m, _sheet_index, _row_index):
        _nr_of_sheets, _nr_of_rows, _nr_of_columns = f_df_array_get_size(_m)
        _sheet_start_index, _sheet_end_index = f_df_array_get_sheet_index_range(_m, math.min(_nr_of_sheets - 1, _sheet_index))
        _start_index = _sheet_start_index + math.min(_nr_of_rows - 1, _row_index) * _nr_of_columns
        _record_slice = array.slice(_m, _start_index, _start_index + math.min(_sheet_end_index + 1, _nr_of_columns))
        _record = array.copy(_record_slice)
        return _record

    def f_df_array_get(_m, _sheet_index, _row_index, _column_index):
        _record = f_df_array_get_record(_m, _sheet_index, _row_index)
        _value = array.get(_record, _column_index)
        return _value

    def f_df_array_set(_m, _sheet_index, _row_index, _column_index, _value):
        _nr_of_sheets, _nr_of_rows, _nr_of_columns = f_df_array_get_size(_m)
        _sheet_start_index, _sheet_end_index = f_df_array_get_sheet_index_range(_m, _sheet_index)
        _start_index = _sheet_start_index + math.min(_nr_of_rows - 1, _row_index) * _nr_of_columns
        _record_slice = array.slice(_m, _start_index, _start_index + _nr_of_columns)
        return array.set(_record_slice, math.min(_nr_of_columns - 1, _column_index), _value)

    def f_array_print(_m, _nr_of_dimensions, _header):
        _text = '' if _nr_of_dimensions <= 1 or not _header else '(' + string.tostring(array.get(_m, 0)) + 'x' + string.tostring(array.get(_m, 1)) + ('' if _nr_of_dimensions <= 2 else 'x' + string.tostring(array.get(_m, 2))) + ')' + '\n' + '\n'
        _text = _text + '[' + (string.tostring(array.get(_m, 0)) + ' ' if _nr_of_dimensions == 1 or not _header else '')
        for i in pine_range(_nr_of_dimensions, array.size(_m) - 1, 1):
            _text = _text + ('' if i == _nr_of_dimensions else ']' + '\n' + ('            ' if i >= array.get(_m, 1) * array.get(_m, 2) + 2 else '') + '[' if (i - _nr_of_dimensions) % array.get(_m, 2) == 0 else ' ') + string.tostring(array.get(_m, i), '#')
        _text = _text + ']'
        return _text

    nr_of_sheets: int = 2
    nr_of_rows: int = 42
    nr_of_columns: int = 3
    high_pivot_data: int = 0
    low_pivot_data: int = 1
    pivot_bar_nr: int = 0
    pivot_value: int = 1
    slope_to_previous: int = 2
    trendlines: Persistent[list[float]] = f_df_array_new(nr_of_sheets, nr_of_rows, nr_of_columns, 0)
    high_pivot = ta.pivothigh(high if wicks else math.max(open, close), len, len / 2)
    low_pivot = ta.pivotlow(low if wicks else math.min(open, close), len, len / 2)
    high_line: list[float] = array.new_float(3, 0)
    if not na(high_pivot):
        array.set(high_line, 0, time[len / 2])
        array.set(high_line, 1, high_pivot)
        f_df_array_add_new_record(trendlines, high_pivot_data, high_line)
    phx1 = cast_int(f_df_array_get(trendlines, high_pivot_data, 1, pivot_bar_nr))
    phy1 = f_df_array_get(trendlines, high_pivot_data, 1, pivot_value)
    phx2 = cast_int(f_df_array_get(trendlines, high_pivot_data, 0, pivot_bar_nr))
    phy2 = f_df_array_get(trendlines, high_pivot_data, 0, pivot_value)
    slope_high = f_get_slope(phx1, phy1, phx2, phy2)
    f_df_array_set(trendlines, high_pivot_data, 0, slope_to_previous, slope_high)
    low_line: list[float] = array.new_float(3, 0)
    if not na(low_pivot):
        array.set(low_line, 0, time[len / 2])
        array.set(low_line, 1, low_pivot)
        f_df_array_add_new_record(trendlines, low_pivot_data, low_line)
    plx1 = cast_int(f_df_array_get(trendlines, low_pivot_data, 1, pivot_bar_nr))
    ply1 = f_df_array_get(trendlines, low_pivot_data, 1, pivot_value)
    plx2 = cast_int(f_df_array_get(trendlines, low_pivot_data, 0, pivot_bar_nr))
    ply2 = f_df_array_get(trendlines, low_pivot_data, 0, pivot_value)
    slope_low = f_get_slope(plx1, ply1, plx2, ply2)
    f_df_array_set(trendlines, low_pivot_data, 0, slope_to_previous, slope_low)
    lookback_time = bar_time * (len / 2)
    phx2_lb = phx2 + lookback_time
    phy2_lb = phy2 * math.exp(lookback_time * slope_high) if log_chart else phy2 + lookback_time * slope_high
    plx2_lb = plx2 + lookback_time
    ply2_lb = ply2 * math.exp(lookback_time * slope_low) if log_chart else ply2 + lookback_time * slope_low
    extension_time = limit_extension * bar_time * 100
    phx2_adj = phx2 if limit_extension == 0 else phx2 + extension_time
    phy2_adj = phy2 if limit_extension == 0 else phy2 * math.exp(extension_time * slope_high) if log_chart else phy2 + extension_time * slope_high
    plx2_adj = plx2 if limit_extension == 0 else plx2 + extension_time
    ply2_adj = ply2 if limit_extension == 0 else ply2 * math.exp(extension_time * slope_low) if log_chart else ply2 + extension_time * slope_low
    looback_line_high: Persistent[Line] = na(Line)
    trendline_high: Persistent[Line] = na(Line)
    looback_line_low: Persistent[Line] = na(Line)
    trendline_low: PersistentSeries[Line] = na(Line)
    xtend: Persistent[bool] = True if limit_extension == 0 else False
    if not na(high_pivot):
        line_color_high = color_rising if slope_high * time < 0 else na if disp_select else color_falling
        if not na(line_color_high):
            looback_line_high = line.new(phx1, phy1, phx2_lb, phy2_lb, xloc.bar_time, extend=extend.none, color=line_color_high, style=line.style_solid, width=1)
    if not na(high_pivot):
        line_color_high = color_rising if slope_high * time < 0 else na if disp_select else color_falling
        if not na(line_color_high):
            trendline_high = line.new(phx1, phy1, phx2_adj, phy2_adj, xloc.bar_time, extend=extend.right if xtend else extend.none, color=line_color_high, style=line.style_dotted, width=1)
    lookback_period_to_delete_tl_high = (time - f_df_array_get(trendlines, high_pivot_data, trendline_nr, pivot_bar_nr)) / bar_time
    if limit_trendline_nr:
        line.delete(trendline_low[lookback_period_to_delete_tl_high])
    if not na(low_pivot):
        line_color_low = (na if disp_select else color_rising) if slope_high * time < 0 else color_falling
        if not na(line_color_low):
            looback_line_low = line.new(plx1, ply1, plx2_lb, ply2_lb, xloc.bar_time, extend=extend.none, color=line_color_low, style=line.style_solid, width=1)
    if not na(low_pivot):
        line_color_low = (na if disp_select else color_rising) if slope_high * time < 0 else color_falling
        if not na(line_color_low):
            trendline_low = line.new(plx1, ply1, plx2_adj, ply2_adj, xloc.bar_time, extend=extend.right if xtend else extend.none, color=line_color_low, style=line.style_dotted, width=1)
    lookback_period_to_delete_tl_low = (time - f_df_array_get(trendlines, low_pivot_data, trendline_nr, pivot_bar_nr)) / bar_time
    if limit_trendline_nr:
        line.delete(trendline_low[lookback_period_to_delete_tl_low])
    high_line_values = f_df_array_get_record(trendlines, 0, 0)
    cross_high: int = 0
    high_x: float = 0.0
    high_y: float = 0.0
    high_sl: float = 0.0
    low_line_values = f_df_array_get_record(trendlines, 1, 0)
    cross_low: int = 0
    low_x: float = 0.0
    low_y: float = 0.0
    low_sl: float = 0.0
    cross_high_values: list[int] = array.new_int()
    cross_low_values: list[int] = array.new_int()
    for i in pine_range(0, trendline_check_nr, 1):
        high_x = cast_int(f_df_array_get(trendlines, high_pivot_data, i, pivot_bar_nr))
        high_y = f_df_array_get(trendlines, high_pivot_data, i, pivot_value)
        high_sl = f_df_array_get(trendlines, high_pivot_data, i, slope_to_previous)
        array.push(cross_high_values, 0 if disp_select and high_sl * time > 0 else line_cross(close, high_x, high_y, high_sl, log_chart))
        low_x = cast_int(f_df_array_get(trendlines, low_pivot_data, i, pivot_bar_nr))
        low_y = f_df_array_get(trendlines, low_pivot_data, i, pivot_value)
        low_sl = f_df_array_get(trendlines, low_pivot_data, i, slope_to_previous)
        array.push(cross_low_values, 0 if disp_select and low_sl * time > 0 else line_cross(close, low_x, low_y, low_sl, log_chart))
    long_break = array.includes(cross_high_values, 1)
    short_break = array.includes(cross_low_values, 1)
    color_high = color_rising if slope_high * time < 0 else na if disp_select else color_falling
    color_low = color_falling if slope_low * time > 0 else na if disp_select else color_rising
    plot(high_pivot, color=color_high, offset=-len / 2)
    plot(low_pivot, color=color_low, offset=-len / 2)
    plotshape((close if long_break else na) if do_alerts else na, title='cross_high', style=shape.triangleup, size=size.small, location=location.belowbar, color=color.new(color.lime, 0))
    plotshape((close if short_break else na) if do_alerts else na, title='cross_low', style=shape.triangledown, size=size.small, location=location.abovebar, color=color.new(color.fuchsia, 0))
    barcolor((color.lime if long_break else color.fuchsia if short_break else na) if do_alerts else na)
    alertcondition(long_break or short_break, title='trendline break', message='trendline break: {{close}}')
    alertcondition(long_break, title='trendline break up', message='trendline break up: {{close}}')
    alertcondition(short_break, title='trendline break down', message='trendline break down: {{close}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
