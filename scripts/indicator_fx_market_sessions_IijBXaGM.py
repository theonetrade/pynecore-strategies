"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore import pine_loop, pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_cast import cast_bool
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barcolor, barstate, box, close,
    color, dayofweek, extend, font, format, high, input, label, line, linefill, location, low,
    math, na, open, plot, plotcandle, plotshape, position, script, session, shape, size, string,
    syminfo, ta, table, text, time, timeframe, yloc
)
from pynecore.types import Box, Color, Label, Line, LineFill, NA, Persistent, Series
import lib.boitoki.AwesomeColor.v9 as ac
import lib.boitoki.Utilities.v11 as util


@udt
class OHLC:
    open: float = na(float)
    high: float = na(float)
    low: float = na(float)
    close: float = na(float)
    hl: float = na(float)


@udt
class Dot:
    x: int = na(int)
    y: float = na(float)
    t: str = ''
    c: Color = na(Color)


@udt
class Candle:
    body: list[Box] = na(list)
    wick: list[Line] = na(list)


@udt
class State:
    extend_style: str = na(str)
    show_fibs: bool = na(bool)
    show_op: bool = na(bool)


@udt
class OpeningRange:
    top: float = na(float)
    btm: float = na(float)
    avg: float = na(float)
    R1: float = na(float)
    R2: float = na(float)
    S1: float = na(float)
    S2: float = na(float)
    total_count: int = 0
    reached_count: int = 0
    reached_R1_count: int = 0
    reached_R2_count: int = 0
    reached_S1_count: int = 0
    reached_S2_count: int = 0


@udt
class Session:
    sess: str = na(str)
    tz: str = na(str)
    name: str = na(str)
    colour: Color = na(Color)

    price_ranges: list[float] = na(list)
    price_range_avg: float = na(float)
    boxes: list[Box] = na(list)
    lines: list[Line] = na(list)
    labels: list[Label] = na(list)
    oclines: list[Line] = na(list)
    ocboxes: list[Box] = na(list)
    oc_labels: list[Label] = na(list)
    opr_boxes: list[Box] = na(list)
    opr_lines: list[Line] = na(list)
    opr_linefills: list[LineFill] = na(list)
    opr_labels: list[Label] = na(list)
    fib: list[Line] = na(list)
    session__ren__: int = na(int)
    is_extended: bool = na(bool)
    in_session: bool = na(bool)

    candle: 'Candle' = _dataclass_field(default_factory=lambda: na(Candle))
    ohlc: 'OHLC' = _dataclass_field(default_factory=lambda: na(OHLC))
    state: 'State' = _dataclass_field(default_factory=lambda: na(State))
    op: 'OpeningRange' = _dataclass_field(default_factory=lambda: na(OpeningRange))

    value: int = na(int)
    start_bar: int = 0


g0: str = '// GENERAL //'
g1_01: str = '// ♯1 SESSION //'
g1_02: str = '// ♯2 SESSION //'
g1_03: str = '// ♯3 SESSION //'
g1_04: str = '// ♯4 SESSION //'
g4: str = '// BOX //'
g6: str = '// LABELS //'
g5: str = '// OPENING RANGE //'
g7: str = '// FIBONACCI LEVELS //'
g11: str = '// CANDLE //'
g10: str = '// ALERTS VISUALISED //'
g12: str = '// INFORMATION //'
option_yes: str = 'Yes'
option_no: str = '× No'
option_border_style1: str = '────'
option_border_style2: str = '- - - - - -'
option_border_style3: str = '•••••••••'
option_chart_1: str = 'Bar color'
option_chart_2: str = 'Candles'
option_candle_color1: str = 'Session color'
option_candle_color2: str = 'Red • Green'
option_candle_body: str = 'OC'
option_candle_wick: str = 'OHLC'


@script.indicator('FX Market Sessions', 'Sessions', overlay=True, max_lines_count=200, max_boxes_count=200, max_labels_count=200, max_bars_back=1000, explicit_plot_zorder=True)
def main(
    i_tz=input.string('GMT+0', title='Timezone', options=('GMT-11', 'GMT-10', 'GMT-9', 'GMT-8', 'GMT-7', 'GMT-6', 'GMT-5', 'GMT-4', 'GMT-3', 'GMT-2', 'GMT-1', 'GMT+0', 'GMT+1', 'GMT+2', 'GMT+3', 'GMT+330', 'GMT+4', 'GMT+430', 'GMT+5', 'GMT+530', 'GMT+6', 'GMT+7', 'GMT+8', 'GMT+9', 'GMT+10', 'GMT+11', 'GMT+12'), group=g0),
    i_history_period=input.int(10, 'History', minval=1, group=g0),
    __input_2__=input.bool(True, 'Session 1 ', group=g1_01, inline='session1_1'),
    i_sess1_label=input.string('London', '', group=g1_01, inline='session1_1'),
    i_sess1_color=input.color(color.new('#66D9EF'), '', group=g1_01, inline='session1_1'),
    i_sess1_barcolor1=input.color(color.new('#66D9EF'), '•', group=g1_01, inline='session1_1'),
    i_sess1_barcolor2=input.color(color.new('#66D9EF'), '', group=g1_01, inline='session1_1'),
    i_sess1=input.session('0800-1700', 'Time', group=g1_01),
    i_sess1_extend=input.string(option_no, 'Extend', options=(option_yes, option_no), group=g1_01),
    __input_9__=input.string(option_no, 'Opening range', group=g1_01, options=(option_yes, option_no)),
    __input_10__=input.string(option_no, 'Fibonacci levels', group=g1_01, options=(option_yes, option_no)),
    i_sess1_chart=input.string(option_no, 'Bar', options=(option_chart_1, option_chart_2, option_no), group=g1_01),
    __input_12__=input.bool(True, 'Session 2 ', group=g1_02, inline='session2_1'),
    i_sess2_label=input.string('New York', '', group=g1_02, inline='session2_1'),
    i_sess2_color=input.color(color.new('#FD971F'), '', group=g1_02, inline='session2_1'),
    i_sess2_barcolor1=input.color(color.new('#FD971F'), '•', group=g1_02, inline='session2_1'),
    i_sess2_barcolor2=input.color(color.new('#FD971F'), '', group=g1_02, inline='session2_1'),
    i_sess2=input.session('1300-2200', 'Time', group=g1_02),
    i_sess2_extend=input.string(option_no, 'Extend', options=(option_yes, option_no), group=g1_02),
    __input_19__=input.string(option_no, 'Opening range', group=g1_02, options=(option_yes, option_no)),
    __input_20__=input.string(option_no, 'Fibonacci levels', group=g1_02, options=(option_yes, option_no)),
    i_sess2_chart=input.string(option_no, 'Bar', options=(option_chart_1, option_chart_2, option_no), group=g1_02),
    __input_22__=input.bool(True, 'Session 3 ', group=g1_03, inline='session3_1'),
    i_sess3_label=input.string('Tokyo', '', group=g1_03, inline='session3_1'),
    i_sess3_color=input.color(color.new('#AE81FF'), '', group=g1_03, inline='session3_1'),
    i_sess3_barcolor1=input.color(color.new('#AE81FF'), '•', group=g1_03, inline='session3_1'),
    i_sess3_barcolor2=input.color(color.new('#AE81FF'), '', group=g1_03, inline='session3_1'),
    i_sess3=input.session('0000-0900', 'Time', group=g1_03),
    i_sess3_extend=input.string(option_no, 'Extend', options=(option_yes, option_no), group=g1_03),
    __input_29__=input.string(option_no, 'Opening range', group=g1_03, options=(option_yes, option_no)),
    __input_30__=input.string(option_no, 'Fibonacci levels', group=g1_03, options=(option_yes, option_no)),
    i_sess3_chart=input.string(option_no, 'Bar', options=(option_chart_1, option_chart_2, option_no), group=g1_03),
    __input_32__=input.bool(False, 'Session 4 ', group=g1_04, inline='session4_1'),
    i_sess4_label=input.string('Sydney', '', group=g1_04, inline='session4_1'),
    i_sess4_color=input.color(color.new('#FB71A3'), '', group=g1_04, inline='session4_1'),
    i_sess4_barcolor1=input.color(color.new('#FB71A3'), '•', group=g1_04, inline='session4_1'),
    i_sess4_barcolor2=input.color(color.new('#FB71A3'), '', group=g1_04, inline='session4_1'),
    i_sess4=input.session('2000-0500', 'Time', group=g1_04),
    i_sess4_extend=input.string(option_no, 'Extend', options=(option_yes, option_no), group=g1_04),
    __input_39__=input.string(option_no, 'Opening range', group=g1_04, options=(option_yes, option_no)),
    __input_40__=input.string(option_no, 'Fibonacci levels', group=g1_04, options=(option_yes, option_no)),
    i_sess4_chart=input.string(option_no, 'Bar', options=(option_chart_1, option_chart_2, option_no), group=g1_04),
    i_sess_box_style=input.string('Box', '', options=('Box', 'Background', 'Hamburger', 'Sandwich'), group=g4, inline='box_style'),
    __input_43__=input.string(option_border_style2, '', options=(option_border_style1, option_border_style2, option_border_style3), group=g4, inline='box_style'),
    i_sess_border_width=input.int(1, '', minval=0, group=g4, inline='box_style'),
    i_sess_box_background=input.bool(True, 'BG color', group=g4, inline='box_style_options'),
    i_sess_box_dots=input.bool(True, 'Dots', group=g4, inline='box_style_options'),
    i_sess_end_offset=input.bool(True, 'Include the latest bar in the Session end', group=g4),
    __input_48__=input.bool(True, '', inline='label_show', group=g6),
    __input_49__=input.string('Small', '', options=('Auto', 'Tiny', 'Small', 'Normal', 'Large', 'Huge'), inline='label_show', group=g6),
    __input_50__=input.string('Top', '', options=('Top', 'Bottom'), inline='label_show', group=g6),
    __input_51__=input.string('Outside', '', options=('Inside', 'Outside'), inline='label_show', group=g6),
    i_label_format_name=input.bool(True, 'Name', inline='label_format', group=g6),
    i_label_format_day=input.bool(False, 'Day', inline='label_format', group=g6),
    i_label_format_price=input.bool(False, 'Price', inline='label_format', group=g6),
    i_label_format_pips=input.bool(False, 'Pips', inline='label_format', group=g6),
    i_o_minutes=input.int(15, title='Periods mins', minval=1, step=1, group=g5),
    i_o_size=input.string(size.small, 'Label size', options=(size.auto, size.tiny, size.small, size.normal, size.large, size.huge), group=g5),
    i_o_color=input.string(option_candle_color2, 'Label color   ', options=(option_candle_color1, option_candle_color2), group=g5, inline="op_label_color"),
    i_o_label_1=input.string('price', 'Label text    ', group=g5, inline='op_label', tooltip="Type \"price\" to display the price"),
    i_o_label_2=input.string('price', '', group=g5, inline='op_label'),
    i_o_label_color=input.string('white', '', options=('black', 'white'), group=g5, inline='op_label_color'),
    i_o_nowonly=input.bool(False, 'Current session only', group=g5, inline='op_options'),
    i_o_breakout_icon=input.bool(False, 'Breakout flag', group=g5, inline='op_options'),
    i_o_target=input.bool(False, 'Target lines', group=g5, inline='op_options'),
    i_o_target_boxes=input.bool(False, 'Target boxes', group=g5, inline='op_options'),
    i_show_op_table=input.bool(False, 'Data table', group=g5),
    i_show_candle=input.bool(False, '', group=g11, inline='candle_display'),
    i_candle=input.string(option_candle_wick, '', options=(option_candle_wick, option_candle_body), group=g11, inline='candle_display'),
    i_candle_border_width=input.int(1, '', minval=1, group=g11, inline='candle_display'),
    i_candle_color=input.string(option_candle_color1, '', options=(option_candle_color1, option_candle_color2), group=g11, inline='candle_display'),
    i_candle_color_g=input.color(color.new('#A6E22E'), '', group=g11, inline='candle_display'),
    i_candle_color_r=input.color(color.new('#F92672'), '', group=g11, inline='candle_display'),
    i_f_show=input.bool(True, '', group=g7, inline='fib_display'),
    __input_74__=input.string(option_border_style1, '', options=(option_border_style1, option_border_style2, option_border_style3), group=g7, inline='fib_display'),
    i_f_linewidth=input.int(1, '', minval=1, group=g7, inline='fib_display'),
    i_show_info=input.bool(True, '', group=g12, inline='info_display'),
    i_info_size=input.string(size.small, '', options=(size.auto, size.tiny, size.small, size.normal, size.large, size.huge), group=g12, inline='info_display'),
    i_info_value_type=input.string('Pips', '', options=('Price', 'Pips'), group=g12, inline='info_display'),
    i_info_period=input.int(50, '', group=g12, inline='info_display'),
    i_alert1_show=input.bool(False, 'Alerts - Sessions stard/end', group=g10),
    i_alert2_show=input.bool(False, 'Alerts - Opening range breakouts', group=g10),
    i_alert3_show=input.bool(False, 'Alerts - Price crossed session\'s High/Low after session closed', group=g10)
):
    g8: str = '// OPTIONS //'

    MAX_BARS: int = 500

    option_hide: str = '× Hide'
    option_opr_label1: str = 'High・Low'
    option_opr_label2: str = 'Buy・Sell'
    option_opr_label_none: str = 'None'

    fmt_price: str = '{0,number,#.#####}'
    fmt_pips: str = '{0,number,#.#}'

    icon_separator: str = ' • '

    color_text = color.new(color.white, 0)
    TRANSPARENT = color.new(color.black, 100)

    @overload
    @method
    def clear(id: list[str], _min: int = 0):
        __block_result__ = na
        if array.size(id) > _min:
            __block_result__ = array.pop(id)
        return __block_result__

    @overload
    @method
    def clear(id: list[float], _min: int = 0):
        __block_result_1__ = na
        if array.size(id) > _min:
            __block_result_1__ = array.pop(id)
        return __block_result_1__



    @overload
    @method
    def create(this: Dot):
        return label.new(this.x, this.y, this.t, style=label.style_label_center, color=TRANSPARENT, textcolor=this.c, size=size.small)


    @overload
    @method
    def create(this: Candle):
        this.body = array.new_box()
        this.wick = array.new_line()
        return this


    @method
    def is_extended(this: State):
        return this.extend_style != option_no



    @overload
    @method
    def create(this: Session, _extend: str, _show_fib: bool, _show_op: bool):
        this.boxes = array.new_box()
        this.lines = array.new_line()
        this.labels = array.new_label()
        this.oclines = array.new_line()
        this.ocboxes = array.new_box()
        this.oc_labels = array.new_label()
        this.opr_boxes = array.new_box()
        this.opr_lines = array.new_line()
        this.opr_linefills = array.new_linefill()
        this.opr_labels = array.new_label()
        this.fib = array.new_line()
        this.price_ranges = array.new_float()

        this.state = State(_extend, _show_fib, _show_op)
        this.candle = method_call(create, Candle())
        this.ohlc = OHLC()
        this.op = OpeningRange()

        this.is_extended = is_extended(this.state)

        return this

    @method
    def update(this: Session):
        t: Series = time(timeframe.period, this.sess, this.tz)
        this.value = t
        __block_result_2__ = na
        if not na(t) and na(t[1]):
            this.start_bar = bar_index
            __block_result_2__ = this.start_bar
        return __block_result_2__

    @method
    def get_bars_from_start(this: Session):
        return bar_index - this.start_bar + 1

    @method
    def session__global__(this: Session):
        return this.value

    @method
    def add(this: Session, range_price, length = 50):
        array.unshift(this.price_ranges, range_price)
        clear(this.price_ranges, length)
        this.price_range_avg = array.avg(this.price_ranges)
        return this.price_range_avg

    def f_get_time_by_bar(bar_count):
        return timeframe.multiplier * bar_count * 60 * 1000

    def f_border_style(_style):
        __block_result_3__ = na
        __switch__ = _style
        if __switch__ == option_border_style1:
            __block_result_3__ = line.style_solid
        elif __switch__ == option_border_style2:
            __block_result_3__ = line.style_dashed
        elif __switch__ == option_border_style3:
            __block_result_3__ = line.style_dotted
        else:
            __block_result_3__ = _style
        return __block_result_3__

    def f_get_label_position(_y, _side):
        __block_result_4__ = na
        __switch__ = _y
        if __switch__ == 'top':
            __block_result_4__ = label.style_label_lower_left if _side == 'outside' else label.style_label_upper_left
        elif __switch__ == 'bottom':
            __block_result_4__ = label.style_label_upper_left if _side == 'outside' else label.style_label_lower_left
        return __block_result_4__

    def f_get_started(_session: Series):
        return na(_session[1]) and cast_bool(_session)

    def f_get_ended(_session: Series):
        return na(_session) and cast_bool(_session[1])

    def f_message_limit_bars(_v):
        return "⚠️ This box's right position exceeds 500 bars(" + string.tostring(_v) + '). This box is not displayed correctly.'

    def f_set_line_x1(_line, _x):
        __block_result_5__ = na
        if line.get_x1(_line) != _x:
            __block_result_5__ = line.set_x1(_line, _x)
        return __block_result_5__

    def f_set_line_x2(_line, _x):
        __block_result_6__ = na
        if line.get_x2(_line) != _x:
            __block_result_6__ = line.set_x2(_line, _x)
        return __block_result_6__

    def f_set_box_right(_box, _x):
        __block_result_7__ = na
        if box.get_right(_box) != _x:
            __block_result_7__ = box.set_right(_box, _x)
        return __block_result_7__

    i_show = i_history_period > 0
    i_lookback = 12 * 60

    i_show_sess1 = __input_2__ and i_show
    i_sess1_op = __input_9__ != option_no and i_show
    i_sess1_fib = __input_10__ != option_no
    i_sess1_barcolor = i_sess1_chart == option_chart_1
    i_sess1_plotcandle = i_sess1_chart == option_chart_2

    i_show_sess2 = __input_12__ and i_show
    i_sess2_op = __input_19__ != option_no and i_show
    i_sess2_fib = __input_20__ != option_no
    i_sess2_barcolor = i_sess2_chart == option_chart_1
    i_sess2_plotcandle = i_sess2_chart == option_chart_2

    i_show_sess3 = __input_22__ and i_show
    i_sess3_op = __input_29__ != option_no and i_show
    i_sess3_fib = __input_30__ != option_no
    i_sess3_barcolor = i_sess3_chart == option_chart_1
    i_sess3_plotcandle = i_sess3_chart == option_chart_2

    i_show_sess4 = __input_32__ and i_show
    i_sess4_op = __input_39__ != option_no and i_show
    i_sess4_fib = __input_40__ != option_no
    i_sess4_barcolor = i_sess4_chart == option_chart_1
    i_sess4_plotcandle = i_sess4_chart == option_chart_2
    i_sess_border_style = f_border_style(__input_43__)
    i_sess_bgopacity = 94 if i_sess_box_background else 100
    i_sess_bgopacity2 = math.min(i_sess_bgopacity - 4, 100)
    i_sess_border_width = 0 if i_sess_box_style == 'Background' else i_sess_border_width
    session_end_offset = 0 if i_sess_end_offset else 1

    i_label_show = __input_48__ and i_show
    i_label_size = string.lower(__input_49__)
    i_label_position_y = string.lower(__input_50__)
    i_label_position_s = string.lower(__input_51__)
    i_label_position = f_get_label_position(i_label_position_y, i_label_position_s)
    i_o_minutes = math.max(i_o_minutes, timeframe.multiplier + 1)
    i_o_transp: int = 50

    i_candle = i_candle if i_show_candle else option_hide
    i_show_candle_wick = i_candle == option_candle_wick
    i_sess_bgopacity2 = 100 if i_show_candle else i_sess_bgopacity2
    i_f_linestyle = f_border_style(__input_74__)
    i_sess1_fib = i_sess1_fib if i_f_show else False
    i_sess2_fib = i_sess2_fib if i_f_show else False
    i_sess3_fib = i_sess3_fib if i_f_show else False
    i_sess4_fib = i_sess4_fib if i_f_show else False

    def f_render_label(_show, data: Session, _is_started, _color, _top, _bottom):
        my_label: Persistent[Label] = na(Label)
        start_time: Persistent[int] = na(int)
        session__ren__ = session__global__(data)

        v_position_y = _top if i_label_position_y == 'top' else _bottom
        v_label: list[str] = array.new_string()
        v_chg = _top - _bottom

        if _is_started:
            start_time = time

        if i_label_format_name and (not na(data.name)):
            array.push(v_label, data.name)

        if i_label_format_day:
            array.push(v_label, util.get_day(dayofweek(start_time, i_tz)))

        if i_label_format_price:
            array.push(v_label, string.format(fmt_price, v_chg))

        if i_label_format_pips:
            array.push(v_label, string.format(fmt_pips, util.toPips(v_chg)))

        if _show:
            if _is_started:
                util.clear_labels(data.labels, 0 if data.is_extended else i_history_period - 1)

                my_label = label.new(bar_index, v_position_y, array.join(v_label, icon_separator), textcolor=_color, color=TRANSPARENT, size=i_label_size, style=i_label_position, tooltip='Pips')

                array.push(data.labels, my_label)
            elif cast_bool(session__ren__):
                label.set_y(my_label, v_position_y)
                label.set_text(my_label, array.join(v_label, icon_separator))

        return data

    def f_render_fibonacci(_show, data, _is_started, _is_ended, _x1, _x2, _color, _top, _bottom, _level, _width, _style):
        my_line: Persistent[Line] = na(Line)
        session__ren__ = method_call(session__global__, data)

        if _show:
            y = (_top - _bottom) * _level + _bottom

            if _is_started:
                my_line = line.new(_x1, y, _x2, y, width=_width, color=color.new(_color, 30), style=_style)
                array.push(data.fib, my_line)

                if data.is_extended:
                    line.set_extend(my_line, extend.right)
            elif cast_bool(session__ren__):
                line.set_y1(my_line, y)
                line.set_y2(my_line, y)

                f_set_line_x2(my_line, _x2)
            elif _is_ended:
                f_set_line_x2(my_line, _x2 - session_end_offset)
        return data

    def f_render_oprange(_show, data: Session, _is_started, _is_ended, _x1, _x2, _color, _max):
        start_time: Persistent[int] = na(int)
        my_label1: Persistent[Label] = na(Label)
        my_label2: Persistent[Label] = na(Label)
        is_opened: Persistent[bool] = False
        R1: Persistent[float] = na(float)
        R2: Persistent[float] = na(float)
        S1: Persistent[float] = na(float)
        S2: Persistent[float] = na(float)

        is_reached_R1: Persistent[bool] = False
        is_reached_R2: Persistent[bool] = False
        is_reached_S1: Persistent[bool] = False
        is_reached_S2: Persistent[bool] = False
        color_gray: Persistent = ac.tradingview('gray')
        color_orange: Persistent = ac.tradingview('orange')
        target_line_width: Persistent[int] = 1

        session__ren__ = session__global__(data)

        top = ta.highest(high, _max)
        btm = ta.lowest(low, _max)

        saved_top: Persistent[float] = na(float)

        if _show:
            if _is_started:
                util.clear_boxes(data.opr_boxes, 0 if data.is_extended else math.max(0, (i_history_period - 1) * 2))
                util.clear_lines(data.opr_lines, 0 if data.is_extended else math.max(0, (i_history_period - 1) * 2))
                util.clear_labels(data.opr_labels, 0 if data.is_extended else math.max(0, (i_history_period - 1) * 2))

                start_time = time
                is_opened = True
            elif cast_bool(session__ren__):
                time_op = start_time + i_o_minutes * 60 * 1000
                time_op_delay = time_op - f_get_time_by_bar(1)

                if time <= time_op and time > time_op_delay:
                    top_color = ac.tradingview('blue') if i_o_color == option_candle_color2 else _color
                    btm_color = ac.tradingview('red') if i_o_color == option_candle_color2 else _color
                    top_text_color = color.from_gradient(85, 0, 100, top_color, ac.panda(i_o_label_color))
                    bot_text_color = color.from_gradient(85, 0, 100, btm_color, ac.panda(i_o_label_color))
                    extend__ren__ = extend.right if data.is_extended else extend.none

                    mdl = math.avg(top, btm)
                    avg1 = data.price_range_avg * 0.786 * 0.5
                    avg2 = data.price_range_avg * 1.272 * 0.5

                    saved_top = top

                    R1 = math.avg(btm, mdl) + avg1
                    R2 = math.avg(btm, mdl) + avg2
                    S1 = math.avg(top, mdl) - avg1
                    S2 = math.avg(top, mdl) - avg2

                    array.push(data.opr_boxes, box.new(_x1, top, bar_index, btm, border_width=0, bgcolor=color.new(ac.tradingview('yellow'), i_o_transp)))
                    array.push(data.opr_lines, line.new(_x1, top, _x2, top, style=line.style_dotted, color=top_color, extend=extend__ren__))
                    array.push(data.opr_lines, line.new(_x1, btm, _x2, btm, style=line.style_dotted, color=btm_color, extend=extend__ren__))

                    array.push(data.opr_lines, line.new(_x1, R2, _x2, R2, style=line.style_solid, color=color.new(top_color, 40) if i_o_target else TRANSPARENT, width=target_line_width, extend=extend__ren__))
                    array.push(data.opr_lines, line.new(_x1, S2, _x2, S2, style=line.style_solid, color=color.new(btm_color, 40) if i_o_target else TRANSPARENT, width=target_line_width, extend=extend__ren__))
                    array.push(data.opr_lines, line.new(_x1, R1, _x2, R1, style=line.style_solid, color=color.new(top_color, 40) if i_o_target else TRANSPARENT, width=target_line_width, extend=extend__ren__))
                    array.push(data.opr_lines, line.new(_x1, S1, _x2, S1, style=line.style_solid, color=color.new(btm_color, 40) if i_o_target else TRANSPARENT, width=target_line_width, extend=extend__ren__))
                    array.push(data.opr_boxes, box.new(_x1, R1, _x1 + 1, R2, border_width=0, bgcolor=color.new(top_color, i_o_transp) if i_o_target_boxes else TRANSPARENT))
                    array.push(data.opr_boxes, box.new(_x1, S1, _x1 + 1, S2, border_width=0, bgcolor=color.new(btm_color, i_o_transp) if i_o_target_boxes else TRANSPARENT))

                    if i_o_target:
                        array.unshift(data.opr_linefills, linefill.new(array.get(data.opr_lines, array.size(data.opr_lines) - 1), array.get(data.opr_lines, array.size(data.opr_lines) - 3), color.new(btm_color, 96)))
                        array.unshift(data.opr_linefills, linefill.new(array.get(data.opr_lines, array.size(data.opr_lines) - 2), array.get(data.opr_lines, array.size(data.opr_lines) - 4), color.new(top_color, 96)))

                    t1 = string.tostring(top, format.mintick) if i_o_label_1 == 'price' else i_o_label_1
                    t2 = string.tostring(btm, format.mintick) if i_o_label_2 == 'price' else i_o_label_2

                    my_label1 = label.new(_x1 - 1, top, t1, yloc=yloc.price, style=label.style_label_right, color=top_color, textcolor=top_text_color, size=i_o_size, tooltip=string.tostring(top, format.mintick))
                    my_label2 = label.new(_x1 - 1, btm, t2, yloc=yloc.price, style=label.style_label_right, color=btm_color, textcolor=bot_text_color, size=i_o_size, tooltip=string.tostring(btm, format.mintick))

                    array.push(data.opr_labels, my_label1)
                    array.push(data.opr_labels, my_label2)

                    alert('Opening range is fixed.', alert.freq_once_per_bar)
                elif is_opened:
                    if ta.crossover(high, R1) and (not is_reached_R1):
                        is_reached_R1 = True

                        if i_o_breakout_icon:
                            label.new(bar_index, high, '×', yloc=yloc.price, style=label.style_label_center, color=TRANSPARENT, textcolor=ac.tradingview('blue'), size=size.large)

                    if ta.crossover(high, R2) and (not is_reached_R2):
                        is_reached_R2 = True

                        if i_o_breakout_icon:
                            label.new(bar_index, high, '×', yloc=yloc.price, style=label.style_label_center, color=TRANSPARENT, textcolor=ac.tradingview('blue'), size=size.large)

                    if ta.crossunder(low, S1) and (not is_reached_S1):
                        is_reached_S1 = True

                        if i_o_breakout_icon:
                            label.new(bar_index, low, '×', yloc=yloc.price, style=label.style_label_center, color=TRANSPARENT, textcolor=ac.tradingview('red'), size=size.large)

                    if ta.crossunder(low, S2) and (not is_reached_S2):
                        is_reached_S2 = True

                        if i_o_breakout_icon:
                            label.new(bar_index, low, '×', yloc=yloc.price, style=label.style_label_center, color=TRANSPARENT, textcolor=ac.tradingview('red'), size=size.large)
            elif _is_ended:
                if i_o_nowonly:
                    util.clear_lines(data.opr_lines, -1)
                    util.clear_labels(data.opr_labels, -1)
                    util.clear_boxes(data.opr_boxes, -1)
                elif array.size(data.opr_lines) > 0:
                    for i in pine_range(0, 5):
                        the_line = array.get(data.opr_lines, array.size(data.opr_lines) - (i + 1))
                        line.set_x2(the_line, _x2 - session_end_offset)

                    for i in pine_range(0, 1):
                        the_label = array.get(data.opr_labels, array.size(data.opr_labels) - (i + 1))
                        label.set_text(the_label, '')
                        label.set_style(the_label, label.style_label_center)
                        label.set_textcolor(the_label, (ac.tradingview('blue') if label.get_y(the_label) >= saved_top else ac.tradingview('red')) if i_o_color == option_candle_color2 else _color)
                        label.set_color(the_label, TRANSPARENT)
                        label.set_size(the_label, size.tiny)
                        label.set_x(the_label, _x1)

                data.op.total_count = data.op.total_count + 1
                data.op.reached_count = data.op.reached_count + 1 if is_reached_R1 or is_reached_R2 or is_reached_S1 or is_reached_S2 else data.op.reached_count
                data.op.reached_R1_count = data.op.reached_R1_count + session_end_offset if is_reached_R1 else data.op.reached_R1_count
                data.op.reached_R2_count = data.op.reached_R2_count + session_end_offset if is_reached_R2 else data.op.reached_R2_count
                data.op.reached_S1_count = data.op.reached_S1_count + session_end_offset if is_reached_S1 else data.op.reached_S1_count
                data.op.reached_S2_count = data.op.reached_S2_count + session_end_offset if is_reached_S2 else data.op.reached_S2_count

                R1 = na
                R2 = na
                S1 = na
                S2 = na
                is_reached_R1 = False
                is_reached_R2 = False
                is_reached_S1 = False
                is_reached_S2 = False
                is_opened = False
                saved_top = na
        return data

    def f_render_candle(_show, data: Session, _is_started, _is_ended, _color, _top, _bottom, _open, _x1, _x2):
        body: Persistent[Box] = na(Box)
        wick1: Persistent[Line] = na(Line)
        wick2: Persistent[Line] = na(Line)
        session__ren__ = session__global__(data)

        border_width = i_candle_border_width
        cx = math.round(math.avg(_x2, _x1)) - math.round(border_width / 2)

        body_color = (i_candle_color_g if close > _open else i_candle_color_r) if i_candle_color == option_candle_color2 else _color
        body_color = color.new(body_color, 30)

        if _show:
            if _is_started:
                body = box.new(_x1, _top, _x2, _bottom, body_color, border_width, line.style_solid, bgcolor=color.new(color.black, 100))
                wick1 = line.new(cx, _top, cx, _top, color=body_color, width=border_width, style=line.style_solid) if i_show_candle_wick else na
                wick2 = line.new(cx, _bottom, cx, _bottom, color=body_color, width=border_width, style=line.style_solid) if i_show_candle_wick else na

                array.push(data.candle.body, body)
                array.push(data.candle.wick, wick1)
                array.push(data.candle.wick, wick2)

                util.clear_boxes(data.candle.body, i_history_period)
                util.clear_lines(data.candle.wick, i_history_period * 2)
            elif cast_bool(session__ren__):
                top = math.max(_open, close)
                bottom = math.min(_open, close)

                box.set_top(body, top)
                box.set_bottom(body, bottom)
                box.set_right(body, _x2)
                box.set_border_color(body, body_color)

                line.set_y1(wick1, _top)
                line.set_y2(wick1, top)
                f_set_line_x1(wick1, cx)
                f_set_line_x2(wick1, cx)
                line.set_color(wick1, body_color)

                line.set_y1(wick2, _bottom)
                line.set_y2(wick2, bottom)
                f_set_line_x1(wick2, cx)
                f_set_line_x2(wick2, cx)
                line.set_color(wick2, body_color)
            elif _is_ended:
                box.set_right(body, bar_index - session_end_offset)

        return data

    def f_render_limitmessage(_show, data: Session, _is_started, _is_ended, _x, _y, _rightbars):
        my_note: Persistent[Label] = na(Label)
        session__ren__ = session__global__(data)

        if _show:
            if _is_started:
                if _rightbars > MAX_BARS:
                    my_note = label.new(_x, _y, f_message_limit_bars(_rightbars), style=label.style_label_upper_left, color=color.yellow, textalign=text.align_left, yloc=yloc.price)
            elif cast_bool(session__ren__):
                if _rightbars > MAX_BARS:
                    label.set_y(my_note, _y)
                    label.set_text(my_note, f_message_limit_bars(_rightbars))
                else:
                    label.delete(my_note)
            elif _is_ended:
                label.delete(my_note)
        return data

    def f_render_sessionrange(_show, data: Session, _is_started, _is_ended, _color, _top: Series, _bottom: Series, _x1, _x2, _is_vertical = False):
        above_line: Persistent[Line] = na(Line)
        below_line: Persistent[Line] = na(Line)
        session__ren__ = session__global__(data)

        __block_result_8__ = na
        if _show:
            if _is_started:
                util.clear_lines(data.lines, 0 if data.is_extended else i_history_period * 2 - 2)

                if _is_vertical:
                    above_line = line.new(_x1, _top, _x1, _bottom, width=i_sess_border_width, style=i_sess_border_style, color=_color)
                    below_line = line.new(_x2, _top, _x2, _bottom, width=i_sess_border_width, style=i_sess_border_style, color=_color)
                else:
                    above_line = line.new(_x1, _top, _x2, _top, width=i_sess_border_width, style=i_sess_border_style, color=_color)
                    below_line = line.new(_x1, _bottom, _x2, _bottom, width=i_sess_border_width, style=i_sess_border_style, color=_color)

                linefill.new(above_line, below_line, color.new(_color, i_sess_bgopacity))

                array.push(data.lines, above_line)
                array.push(data.lines, below_line)

                if data.is_extended:
                    if _is_vertical:
                        line.set_extend(above_line, extend.both)
                        line.set_extend(below_line, extend.both)
                    else:
                        line.set_extend(above_line, extend.right)
                        line.set_extend(below_line, extend.right)
            elif cast_bool(session__ren__):
                if _is_vertical:
                    line.set_y1(above_line, _bottom)
                    line.set_y2(above_line, _top)
                    line.set_y1(below_line, _bottom)
                    line.set_y2(below_line, _top)
                else:
                    line.set_y1(above_line, _top)
                    line.set_y2(above_line, _top)
                    line.set_x2(above_line, _x2)

                    line.set_y1(below_line, _bottom)
                    line.set_y2(below_line, _bottom)
                    line.set_x2(below_line, _x2)
            elif _is_ended:
                if _is_vertical:
                    line.set_x1(below_line, _x2 - session_end_offset)
                    line.set_x2(below_line, _x2 - session_end_offset)
                else:
                    line.set_x2(above_line, _x2 - session_end_offset)
                    line.set_x2(below_line, _x2 - session_end_offset)

                add(data, _top[1] - _bottom[1], i_info_period)

            __block_result_8__ = data
        return __block_result_8__

    def f_render_session(_show, data: Session, _is_started, _is_ended, _color, _top: Series, _bottom: Series, _x1, _x2):
        my_box: Persistent[Box] = na(Box)
        session__ren__ = session__global__(data)

        if _show:
            if _is_started:
                util.clear_boxes(data.boxes, 0 if data.is_extended else i_history_period - 1)

                my_box = box.new(_x1, _top, _x2, _bottom, _color, i_sess_border_width, i_sess_border_style, bgcolor=color.new(_color, i_sess_bgopacity))
                array.push(data.boxes, my_box)

                if data.is_extended:
                    box.set_extend(my_box, extend.right)
            elif cast_bool(session__ren__):
                box.set_top(my_box, _top)
                box.set_bottom(my_box, _bottom)
                f_set_box_right(my_box, _x2)
            elif _is_ended:
                box.set_right(my_box, _x2 - session_end_offset)
                add(data, _top[1] - _bottom[1], i_info_period)

        return data

    def f_render_current_line(_show, data: Session, _is_started, _is_ended, _color, _top, _bottom, _x1, _x2):
        my_line: Persistent[Line] = na(Line)
        session__ren__ = session__global__(data)

        __block_result_9__ = na
        if _show:
            if _is_started:
                my_line = line.new(_x1, close, _x1 + 2, close, color=_color, width=3)
            elif cast_bool(session__ren__):
                line.set_y1(my_line, close)
                line.set_y2(my_line, close)
            elif _is_ended:
                line.delete(my_line)

            __block_result_9__ = True
        return __block_result_9__

    def f_render_dots(_show, data: Session, _is_started, _is_ended, _color, _top, _bottom, _x1, _x2):
        _open: Persistent[float] = na(float)
        oc_box: Persistent[Box] = na(Box)
        oc_line_u: Persistent[Line] = na(Line)
        oc_line_l: Persistent[Line] = na(Line)
        session__ren__ = session__global__(data)

        if _show and i_sess_box_dots:
            if _is_started:
                util.clear_lines(data.oclines, 0 if data.is_extended else i_history_period * 2 - 2)
                util.clear_labels(data.oc_labels, 0 if data.is_extended else math.max(0, i_history_period * 2 - 2))

                oc_line_u = line.new(_x1, open, _x2, open, color=color.new(_color, 70), style=line.style_dotted)
                oc_line_l = line.new(_x1, close, _x2, close, color=color.new(_color, 70), style=line.style_dotted)
                linefill.new(oc_line_u, oc_line_l, color.new(_color, i_sess_bgopacity2))

                array.push(data.oclines, oc_line_u)
                array.push(data.oclines, oc_line_l)

                _open = open
            elif cast_bool(session__ren__):
                line.set_x2(oc_line_u, _x2)
                line.set_x2(oc_line_l, _x2)
                line.set_y1(oc_line_l, close)
                line.set_y2(oc_line_l, close)
            elif _is_ended:
                array.push(data.oc_labels, method_call(create, Dot(_x1, _open, '●', _color)))
                array.push(data.oc_labels, method_call(create, Dot(_x2 - session_end_offset, close[1], '◉', _color)))

                line.set_x2(oc_line_u, _x2 - session_end_offset)
                line.set_x2(oc_line_l, _x2 - session_end_offset)
                line.set_y1(oc_line_l, close[1])
                line.set_y2(oc_line_l, close[1])

                _open = na
        return True

    def f_render_main(_show, data: Session, _is_started, _is_ended, _color, _top, _bottom):
        x1: Persistent[int] = 0
        x2: Persistent[int] = 0
        x2_offset: int = 1
        session__ren__: Series = session__global__(data)

        x0_1 = ta.valuewhen(na(session__ren__[1]) and cast_bool(session__ren__), bar_index, 1)
        x0_2 = ta.valuewhen(na(session__ren__) and cast_bool(session__ren__[1]), bar_index, 0)
        x0_d = math.min(math.abs(x0_2 - x0_1), MAX_BARS)
        rightbars = x0_d

        if _show:
            if _is_started:
                x1 = bar_index
                x2 = bar_index + x0_d

                data.ohlc.open = open
                data.ohlc.high = _top
                data.ohlc.low = _bottom
                data.ohlc.hl = _top - _bottom
                data.in_session = True
            elif cast_bool(session__ren__):
                true_x2 = x1 + x0_d
                rightbars = true_x2 - bar_index
                max_bars = bar_index + MAX_BARS
                x2 = math.min(true_x2, max_bars)

                data.ohlc.high = _top
                data.ohlc.low = _bottom
                data.ohlc.hl = _top - _bottom
            elif _is_ended:
                data.in_session = False
                data.ohlc.open = na

        return (x1, x2, data.ohlc, rightbars)

    def draw(_show, data: Session, _extend, _show_fib, _show_op):
        update(data)

        session__ren__ = session__global__(data)
        max = get_bars_from_start(data)

        top = ta.highest(high, max)
        bottom = ta.lowest(low, max)

        col: Color = data.colour

        is_started = f_get_started(session__ren__)
        is_ended = f_get_ended(session__ren__)

        x1, x2, ohlc__00000220__, _rightbars = f_render_main(_show, data, is_started, is_ended, col, top, bottom)

        if i_sess_box_style == 'Box' or i_sess_box_style == 'Background' or i_sess_box_style == 'Candle':
            f_render_session(_show, data, is_started, is_ended, col, top, bottom, x1, x2)
            f_render_dots(_show, data, is_started, is_ended, col, top, bottom, x1, x2)
        elif i_sess_box_style == 'Hamburger':
            f_render_sessionrange(_show, data, is_started, is_ended, col, top, bottom, x1, x2)
        elif i_sess_box_style == 'Sandwich':
            f_render_sessionrange(_show, data, is_started, is_ended, col, top, bottom, x1, x2, True)

        if i_show_candle:
            f_render_candle(_show, data, is_started, is_ended, col, top, bottom, ohlc__00000220__.open, x1, x2)

        if i_label_show:
            f_render_label(_show, data, is_started, col, top, bottom)

        if _show_op:
            f_render_oprange(_show, data, is_started, is_ended, x1, x2, col, max)
            f_render_current_line(_show, data, is_started, is_ended, col, top, bottom, x1, x2)

        if _show_fib:
            if is_started:
                util.clear_lines(data.fib, -1 if data.is_extended else i_history_period * 3 - 4)

            f_render_fibonacci(_show, data, is_started, is_ended, x1, x2, col, top, bottom, 0.5, 2, line.style_solid)
            f_render_fibonacci(_show, data, is_started, is_ended, x1, x2, col, top, bottom, 0.628, i_f_linewidth, i_f_linestyle)
            f_render_fibonacci(_show, data, is_started, is_ended, x1, x2, col, top, bottom, 0.382, i_f_linewidth, i_f_linestyle)

        f_render_limitmessage(_show, data, is_started, is_ended, x1, bottom, _rightbars)

        return (cast_bool(session__ren__), ohlc__00000220__)

    tz: str = na if i_tz == option_no or i_tz == '' else i_tz

    sess1_data: Persistent[Session] = method_call(create, Session(i_sess1, tz, i_sess1_label, i_sess1_color), i_sess1_extend, i_sess1_fib, i_sess1_op)
    sess2_data: Persistent[Session] = method_call(create, Session(i_sess2, tz, i_sess2_label, i_sess2_color), i_sess2_extend, i_sess2_fib, i_sess2_op)
    sess3_data: Persistent[Session] = method_call(create, Session(i_sess3, tz, i_sess3_label, i_sess3_color), i_sess3_extend, i_sess3_fib, i_sess3_op)
    sess4_data: Persistent[Session] = method_call(create, Session(i_sess4, tz, i_sess4_label, i_sess4_color), i_sess4_extend, i_sess4_fib, i_sess4_op)

    is_sess1: Series
    is_sess1, sess1_ohlc = draw(i_show_sess1, sess1_data, i_sess1_extend, i_sess1_fib, i_sess1_op)
    is_sess2: Series
    is_sess2, sess2_ohlc = draw(i_show_sess2, sess2_data, i_sess2_extend, i_sess2_fib, i_sess2_op)
    is_sess3: Series
    is_sess3, sess3_ohlc = draw(i_show_sess3, sess3_data, i_sess3_extend, i_sess3_fib, i_sess3_op)
    is_sess4: Series
    is_sess4, sess4_ohlc = draw(i_show_sess4, sess4_data, i_sess4_extend, i_sess4_fib, i_sess4_op)

    is_positive_bar = close > open

    c_barcolor: Color = na(Color)
    c_plotcandle: Color = na(Color)

    c_sess1_barcolor = (i_sess1_barcolor1 if is_positive_bar else i_sess1_barcolor2) if is_sess1 else na
    c_sess2_barcolor = (i_sess2_barcolor1 if is_positive_bar else i_sess2_barcolor2) if is_sess2 else na
    c_sess3_barcolor = (i_sess3_barcolor1 if is_positive_bar else i_sess3_barcolor2) if is_sess3 else na
    c_sess4_barcolor = (i_sess4_barcolor1 if is_positive_bar else i_sess4_barcolor2) if is_sess4 else na

    if i_sess1_chart != option_no and is_sess1:
        c_barcolor = c_sess1_barcolor if i_sess1_barcolor else na
        c_plotcandle = c_sess1_barcolor if i_sess1_plotcandle else na

    if i_sess2_chart != option_no and is_sess2:
        c_barcolor = c_sess2_barcolor if i_sess2_barcolor else na
        c_plotcandle = c_sess2_barcolor if i_sess2_plotcandle else na

    if i_sess3_chart != option_no and is_sess3:
        c_barcolor = c_sess3_barcolor if i_sess3_barcolor else na
        c_plotcandle = c_sess3_barcolor if i_sess3_plotcandle else na

    if i_sess4_chart != option_no and is_sess4:
        c_barcolor = c_sess4_barcolor if i_sess4_barcolor else na
        c_plotcandle = c_sess4_barcolor if i_sess4_plotcandle else na

    barcolor(c_barcolor)
    plotcandle(open, high, low, close, color=TRANSPARENT if is_positive_bar else c_plotcandle, bordercolor=c_plotcandle, wickcolor=c_plotcandle)

    sess1_started = is_sess1 and (not is_sess1[1])
    sess1_ended = not is_sess1 and is_sess1[1]
    sess2_started = is_sess2 and (not is_sess2[1])
    sess2_ended = not is_sess2 and is_sess2[1]
    sess3_started = is_sess3 and (not is_sess3[1])
    sess3_ended = not is_sess3 and is_sess3[1]
    sess4_started = is_sess4 and (not is_sess4[1])
    sess4_ended = not is_sess4 and is_sess4[1]

    alertcondition(sess1_started, 'Session #1 started')
    alertcondition(sess1_ended, 'Session #1 ended')
    alertcondition(sess2_started, 'Session #2 started')
    alertcondition(sess2_ended, 'Session #2 ended')
    alertcondition(sess3_started, 'Session #3 started')
    alertcondition(sess3_ended, 'Session #3 ended')
    alertcondition(sess4_started, 'Session #4 started')
    alertcondition(sess4_ended, 'Session #4 ended')

    alertcondition(not is_sess1 and ta.crossover(close, sess1_ohlc.high), 'Session #1 High crossed (after session closed)')
    alertcondition(not is_sess1 and ta.crossunder(close, sess1_ohlc.low), 'Session #1 Low crossed (after session closed)')
    alertcondition(not is_sess2 and ta.crossover(close, sess2_ohlc.high), 'Session #2 High crossed (after session closed)')
    alertcondition(not is_sess2 and ta.crossunder(close, sess2_ohlc.low), 'Session #2 Low crossed (after session closed)')
    alertcondition(not is_sess3 and ta.crossover(close, sess3_ohlc.high), 'Session #3 High crossed (after session closed)')
    alertcondition(not is_sess3 and ta.crossunder(close, sess3_ohlc.low), 'Session #3 Low crossed (after session closed)')
    alertcondition(not is_sess4 and ta.crossover(close, sess4_ohlc.high), 'Session #4 High crossed (after session closed)')
    alertcondition(not is_sess4 and ta.crossunder(close, sess4_ohlc.low), 'Session #4 Low crossed (after session closed)')

    if i_alert1_show:
        if i_show_sess1:
            if sess1_started:
                label.new(bar_index, close, 'Start', yloc=yloc.abovebar, color=i_sess1_color, textcolor=color_text, size=size.small, style=label.style_label_down)
            if sess1_ended:
                label.new(bar_index - session_end_offset, close, 'End', yloc=yloc.abovebar, color=i_sess1_color, textcolor=color_text, size=size.small, style=label.style_label_down)

        if i_show_sess2:
            if sess2_started:
                label.new(bar_index, close, 'Start', yloc=yloc.abovebar, color=i_sess2_color, textcolor=color_text, size=size.small, style=label.style_label_down)
            if sess2_ended:
                label.new(bar_index - session_end_offset, close, 'End', yloc=yloc.abovebar, color=i_sess2_color, textcolor=color_text, size=size.small, style=label.style_label_down)

        if i_show_sess3:
            if sess3_started:
                label.new(bar_index, close, 'Start', yloc=yloc.abovebar, color=i_sess3_color, textcolor=color_text, size=size.small, style=label.style_label_down)
            if sess3_ended:
                label.new(bar_index - session_end_offset, close, 'End', yloc=yloc.abovebar, color=i_sess3_color, textcolor=color_text, size=size.small, style=label.style_label_down)

        if i_show_sess4:
            if sess4_started:
                label.new(bar_index, close, 'Start', yloc=yloc.abovebar, color=i_sess4_color, textcolor=color_text, size=size.small, style=label.style_label_down)
            if sess4_ended:
                label.new(bar_index - session_end_offset, close, 'End', yloc=yloc.abovebar, color=i_sess4_color, textcolor=color_text, size=size.small, style=label.style_label_down)

    plot(sess1_ohlc.high if i_alert3_show else na, 'sess1_high', style=plot.style_linebr, color=i_sess1_color)
    plot(sess1_ohlc.low if i_alert3_show else na, 'sess1_low', style=plot.style_linebr, color=i_sess1_color, linewidth=2)
    plot(sess2_ohlc.high if i_alert3_show else na, 'sess2_high', style=plot.style_linebr, color=i_sess2_color)
    plot(sess2_ohlc.low if i_alert3_show else na, 'sess2_low', style=plot.style_linebr, color=i_sess2_color, linewidth=2)
    plot(sess3_ohlc.high if i_alert3_show else na, 'sess3_high', style=plot.style_linebr, color=i_sess3_color)
    plot(sess3_ohlc.low if i_alert3_show else na, 'sess3_low', style=plot.style_linebr, color=i_sess3_color, linewidth=2)
    plot(sess4_ohlc.high if i_alert3_show else na, 'sess4_high', style=plot.style_linebr, color=i_sess4_color)
    plot(sess4_ohlc.low if i_alert3_show else na, 'sess4_low', style=plot.style_linebr, color=i_sess4_color, linewidth=2)

    plotshape(sess1_ohlc.high if i_alert3_show and (not is_sess1) and ta.crossover(close, sess1_ohlc.high) else na, 'cross sess1_high', color=i_sess1_color, style=shape.triangleup, location=location.absolute, size=size.tiny)
    plotshape(sess1_ohlc.low if i_alert3_show and (not is_sess1) and ta.crossunder(close, sess1_ohlc.low) else na, 'cross sess1_low', color=i_sess1_color, style=shape.triangledown, location=location.absolute, size=size.tiny)
    plotshape(sess2_ohlc.high if i_alert3_show and (not is_sess2) and ta.crossover(close, sess2_ohlc.high) else na, 'cross sess2_high', color=i_sess2_color, style=shape.triangleup, location=location.absolute, size=size.tiny)
    plotshape(sess2_ohlc.low if i_alert3_show and (not is_sess2) and ta.crossunder(close, sess2_ohlc.low) else na, 'cross sess2_low', color=i_sess2_color, style=shape.triangledown, location=location.absolute, size=size.tiny)
    plotshape(sess3_ohlc.high if i_alert3_show and (not is_sess3) and ta.crossover(close, sess3_ohlc.high) else na, 'cross sess3_high', color=i_sess3_color, style=shape.triangleup, location=location.absolute, size=size.tiny)
    plotshape(sess3_ohlc.low if i_alert3_show and (not is_sess3) and ta.crossunder(close, sess3_ohlc.low) else na, 'cross sess3_low', color=i_sess3_color, style=shape.triangledown, location=location.absolute, size=size.tiny)
    plotshape(sess4_ohlc.high if i_alert3_show and (not is_sess4) and ta.crossover(close, sess4_ohlc.high) else na, 'cross sess4_high', color=i_sess4_color, style=shape.triangleup, location=location.absolute, size=size.tiny)
    plotshape(sess4_ohlc.low if i_alert3_show and (not is_sess4) and ta.crossunder(close, sess4_ohlc.low) else na, 'cross sess4_low', color=i_sess4_color, style=shape.triangledown, location=location.absolute, size=size.tiny)

    text_color: Persistent[Color] = color.new('#E1E2E4')
    bgcolor__ren__: Persistent[Color] = color.new('#1A1C20')
    color_green: Persistent = ac.monokai('green')
    color_orange: Persistent = ac.monokai('orange')
    color_red: Persistent = ac.monokai('red')
    color_ind_green: Persistent = ac.tradingview('green')
    color_ind_gray: Persistent = color.new(ac.tradingview('gray'), 30)
    color_white: Persistent[Color] = color.new('#E1E2E4')

    i_show_analysis2: bool = False

    if i_show_info and barstate.islast:
        data: list[Session] = array.new(0, NA(Session))

        if array.size(sess1_data.price_ranges) > 0:
            array.push(data, sess1_data)
        if array.size(sess2_data.price_ranges) > 0:
            array.push(data, sess2_data)
        if array.size(sess3_data.price_ranges) > 0:
            array.push(data, sess3_data)
        if array.size(sess4_data.price_ranges) > 0:
            array.push(data, sess4_data)

        tbl_avg: Persistent = table.new(position.top_right, 5, 5, frame_width=2, bgcolor=bgcolor__ren__, frame_color=color.new('#25272C'), border_width=1, border_color=color.new('#25272C'))

        table.cell(tbl_avg, 0, 0, 'Session', text_color=color.new(text_color, 60), text_size=i_info_size, text_halign=text.align_center)
        table.cell(tbl_avg, 1, 0, '', text_color=color.new(text_color, 60), text_size=i_info_size)
        table.cell(tbl_avg, 2, 0, 'Cur', text_color=color.new(text_color, 60), text_size=i_info_size)
        table.cell(tbl_avg, 3, 0, 'Avg(' + string.tostring(i_info_period) + ')', text_color=color.new(text_color, 60), text_size=i_info_size)
        table.cell(tbl_avg, 4, 0, '%', text_color=color.new(text_color, 60), text_size=i_info_size)
        table.merge_cells(tbl_avg, 0, 0, 1, 0)

        if array.size(data) > 0:
            for i in pine_range(0, array.size(data) - 1):
                my_data = array.get(data, i)
                in_session = my_data.in_session and session.ismarket
                p = my_data.ohlc.hl / my_data.price_range_avg
                col_cur = color_green if p < 0.75 else color_orange if p < 1.25 else color_red
                v1 = string.tostring(my_data.ohlc.hl, format.mintick) if i_info_value_type == 'Price' else string.tostring(util.toPips(my_data.ohlc.hl), '#.#')
                v2 = string.tostring(my_data.price_range_avg, format.mintick) if i_info_value_type == 'Price' else string.tostring(util.toPips(my_data.price_range_avg), '#.#')
                v3 = '◉' if in_session else '●'

                color_name = color_white if in_session else color.new(ac.monokai('gray'), 30)
                color_ind = color_ind_green if in_session else color_ind_gray
                color_cur = col_cur if in_session else color.new(col_cur, 60)

                table.cell(tbl_avg, 0, i + 1, my_data.name, text_color=color_name, text_size=i_info_size, text_halign=text.align_left)
                table.cell(tbl_avg, 1, i + 1, v3, text_color=color_ind, text_size=size.tiny, text_halign=text.align_center, text_valign=text.align_center)
                table.cell(tbl_avg, 2, i + 1, v1, text_color=color_cur, text_size=i_info_size, text_halign=text.align_right, text_font_family=font.family_monospace)
                table.cell(tbl_avg, 3, i + 1, v2, text_color=color_name, text_size=i_info_size, text_halign=text.align_right, text_font_family=font.family_monospace)
                table.cell(tbl_avg, 4, i + 1, string.format('{0,number,percent}', p), text_color=color_cur, text_size=i_info_size, text_halign=text.align_right, text_font_family=font.family_monospace)

    row_index: int = 2
    tbl_op: Persistent = table.new(position.bottom_right, 7, 5, frame_width=2, bgcolor=bgcolor__ren__, frame_color=color.new('#25272C'), border_width=1, border_color=color.new('#25272C'))

    if i_show_op_table and (barstate.islast or barstate.isconfirmed):
        data: list[Session] = array.new(0, NA(Session))

        if sess1_data.op.reached_count > 0:
            array.unshift(data, sess1_data)
        if sess2_data.op.reached_count > 0:
            array.unshift(data, sess2_data)
        if sess3_data.op.reached_count > 0:
            array.unshift(data, sess3_data)
        if sess4_data.op.reached_count > 0:
            array.unshift(data, sess4_data)

        table.cell(tbl_op, 0, 0, 'Opening range(' + syminfo.ticker + ')' + (' (No data)' if array.size(data) == 0 else ''), text_size=i_info_size)
        table.merge_cells(tbl_op, 0, 0, 6, 0)

        if array.size(data) > 0:
            table.cell(tbl_op, 0, 1, 'Session', text_size=i_info_size)
            table.cell(tbl_op, 1, 1, 'Sum', text_size=i_info_size)
            table.cell(tbl_op, 2, 1, 'R1', text_size=i_info_size)
            table.cell(tbl_op, 3, 1, 'S1', text_size=i_info_size)
            table.cell(tbl_op, 4, 1, 'R2', text_size=i_info_size)
            table.cell(tbl_op, 5, 1, 'S2', text_size=i_info_size)
            table.cell(tbl_op, 6, 1, 'Total', text_size=i_info_size)

            for i in pine_range(0, array.size(data) - 1):
                my_data = array.get(data, i)
                row_index = row_index + i
                table.cell(tbl_op, 0, row_index, my_data.name, text_size=i_info_size, text_color=color_white, text_halign=text.align_left)
                table.cell(tbl_op, 1, row_index, string.format('{0,number,percent}', my_data.op.reached_count / my_data.op.total_count), text_font_family=font.family_monospace, text_halign=text.align_right, text_color=color_white, text_size=i_info_size)
                table.cell(tbl_op, 2, row_index, string.format('{0,number,percent}', my_data.op.reached_R1_count / my_data.op.total_count), text_font_family=font.family_monospace, text_halign=text.align_right, text_color=color_white, text_size=i_info_size)
                table.cell(tbl_op, 3, row_index, string.format('{0,number,percent}', my_data.op.reached_S1_count / my_data.op.total_count), text_font_family=font.family_monospace, text_halign=text.align_right, text_color=color_white, text_size=i_info_size)
                table.cell(tbl_op, 4, row_index, string.format('{0,number,percent}', my_data.op.reached_R2_count / my_data.op.total_count), text_font_family=font.family_monospace, text_halign=text.align_right, text_color=color_white, text_size=i_info_size)
                table.cell(tbl_op, 5, row_index, string.format('{0,number,percent}', my_data.op.reached_S2_count / my_data.op.total_count), text_font_family=font.family_monospace, text_halign=text.align_right, text_color=color_white, text_size=i_info_size)
                table.cell(tbl_op, 6, row_index, string.tostring(my_data.op.total_count), text_font_family=font.family_monospace, text_halign=text.align_right, text_color=color_white, text_size=i_info_size)

    if i_show_analysis2 and barstate.islast:
        max: int = 100
        g_base = ta.lowest(max)
        s3_count: int = 0
        s2_count: int = 0

        if array.size(sess1_data.price_ranges) > 0 and array.size(sess3_data.price_ranges) > 0:
            __loop_2__ = pine_loop(0)
            while __loop_2__.step(array.size(sess1_data.price_ranges) - 1):
                i = __loop_2__.value
                s1 = array.get(sess1_data.price_ranges, i)
                s3 = array.get(sess3_data.price_ranges, i)

                if s3 / s1 > 1:
                    s3_count = s3_count + 1

            row_index = row_index + 1

            table.cell(tbl_op, 0, row_index, sess3_data.name + ' > ' + sess1_data.name, text_halign=text.align_left, text_color=color_white, text_size=i_info_size)
            table.cell(tbl_op, 4, row_index, string.tostring(s3_count) + ' / ' + string.tostring(array.size(sess1_data.price_ranges)), text_halign=text.align_right, text_font_family=font.family_monospace, text_color=color_white, text_size=i_info_size)
            table.cell(tbl_op, 6, row_index, string.format('{0,number,percent}', s3_count / array.size(sess1_data.price_ranges)), text_halign=text.align_right, text_font_family=font.family_monospace, text_color=color_white, text_size=i_info_size)

            table.merge_cells(tbl_op, 0, row_index, 3, row_index)
            table.merge_cells(tbl_op, 4, row_index, 5, row_index)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
