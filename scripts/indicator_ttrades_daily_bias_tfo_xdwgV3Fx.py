"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barstate, chart, close, color,
    display, extend, high, input, label, line, location, low, math, na, open, plot, plotshape,
    position, script, shape, size, string, table, time, timeframe, xloc, yloc
)
from pynecore.types import Color, Line, Persistent


@udt
class lines:
    ph_line: Line = na(Line)
    pl_line: Line = na(Line)
    hit_ph_line: bool = False
    hit_pl_line: bool = False


@udt
class info:
    ph: float = na(float)
    pl: float = na(float)
    ch: float = na(float)
    cl: float = na(float)
    co: float = na(float)
    p_up: bool = na(bool)
    bias: int = 0
    bias_ph: int = 0
    bias_pl: int = 0
    hit_ph: int = 0
    hit_pl: int = 0
    close_ph: int = 0
    close_pl: int = 0


g_VIS: str = 'Bias'
g_PLT: str = 'Plotting'
g_STY: str = 'Style'
g_TBL: str = 'Table'


@script.indicator('TTrades Daily Bias [TFO]', 'TTrades Daily Bias [TFO]', True, max_lines_count=500, max_labels_count=500)
def main(
    d_stats=input.bool(True, 'Daily Bias', tooltip='Apply TTrades bias concepts to the 1 Day timeframe', group=g_VIS),
    w_stats=input.bool(False, 'Weekly Bias', tooltip='Apply TTrades bias concepts to the 1 Week timeframe', group=g_VIS),
    bias_reason=input.bool(True, 'Show Bias Reasoning', tooltip='Show the reason why a given bias is being established', group=g_VIS),
    bull_color=input.color(color.teal, 'Bull / Bear Bias Colors', inline='COLOR', group=g_PLT),
    bear_color=input.color(color.red, '', inline='COLOR', group=g_PLT),
    d_bias_plot=input.bool(True, 'Plot Daily Bias', inline='DBIAS', group=g_PLT),
    w_bias_plot=input.bool(True, 'Plot Weekly Bias', inline='WBIAS', group=g_PLT),
    d_bias_loc=input.string('Top', '', inline='DBIAS', options=('Top', 'Bottom'), group=g_PLT),
    w_bias_loc=input.string('Bottom', '', inline='WBIAS', options=('Top', 'Bottom'), group=g_PLT),
    before_raid_color=input.color(color.blue, 'Before / After Hit Colors', inline='HIT', tooltip='All previous high and low lines will start out as this color', group=g_STY),
    after_raid_color=input.color(color.red, '', inline='HIT', tooltip='Once a previous high or low line is reached, it will become this color', group=g_STY),
    stop_ext=input.bool(False, 'Stop Extending Lines After Hit', tooltip='Once a previous high or low line is reached, its line will stop extending', group=g_STY),
    use_d_sep=input.bool(True, 'Day Separator', inline='DSEP', group=g_STY),
    use_w_sep=input.bool(True, 'Week Separator', inline='WSEP', group=g_STY),
    d_sep=input.color(color.new(color.black, 80), '', inline='DSEP', group=g_STY),
    w_sep=input.color(color.new(color.black, 30), '', inline='WSEP', group=g_STY),
    line_width=input.int(1, 'Line Width', group=g_STY),
    tbl_show_stats=input.bool(True, 'Show Statistics', tooltip='Show statistics on bias accuracy\n\nSuccess Rate: how often has price successfully reached the assigned draw on liquidity?\n\nClose Thru Rate: from the number of times that price reached the assigned draw on liquidity, how often did it close through that level?\n\nSample Size: the total number of times that a given bias was assigned', group=g_TBL),
    tbl_loc=input.string('Top Right', 'Position', options=('Bottom Center', 'Bottom Left', 'Bottom Right', 'Middle Center', 'Middle Left', 'Middle Right', 'Top Center', 'Top Left', 'Top Right'), group=g_TBL),
    tbl_size=input.string('Normal', 'Size', options=('Auto', 'Tiny', 'Small', 'Normal', 'Large', 'Huge'), group=g_TBL)
):
    new_day = timeframe.change('D')
    new_week = timeframe.change('W')
    can_plot_d = timeframe.in_seconds() < timeframe.in_seconds('D')
    can_plot_w = timeframe.in_seconds() < timeframe.in_seconds('W')
    if use_d_sep and new_day and can_plot_d:
        line.new(bar_index, high * 1.000001, bar_index, low, color=d_sep, extend=extend.both, width=line_width)
    if use_w_sep and new_week and can_plot_w:
        line.new(bar_index, high * 1.000001, bar_index, low, color=w_sep, extend=extend.both, width=line_width)
    def get_table_pos(pos):
        __block_result__ = na
        __switch__ = pos
        if __switch__ == 'Bottom Center':
            __block_result__ = position.bottom_center
        elif __switch__ == 'Bottom Left':
            __block_result__ = position.bottom_left
        elif __switch__ == 'Bottom Right':
            __block_result__ = position.bottom_right
        elif __switch__ == 'Middle Center':
            __block_result__ = position.middle_center
        elif __switch__ == 'Middle Left':
            __block_result__ = position.middle_left
        elif __switch__ == 'Middle Right':
            __block_result__ = position.middle_right
        elif __switch__ == 'Top Center':
            __block_result__ = position.top_center
        elif __switch__ == 'Top Left':
            __block_result__ = position.top_left
        elif __switch__ == 'Top Right':
            __block_result__ = position.top_right
        return __block_result__

    def get_table_size(size__ren__):
        __block_result_1__ = na
        __switch__ = size__ren__
        if __switch__ == 'Tiny':
            __block_result_1__ = size.tiny
        elif __switch__ == 'Small':
            __block_result_1__ = size.small
        elif __switch__ == 'Normal':
            __block_result_1__ = size.normal
        elif __switch__ == 'Large':
            __block_result_1__ = size.large
        elif __switch__ == 'Huge':
            __block_result_1__ = size.huge
        elif __switch__ == 'Auto':
            __block_result_1__ = size.auto
        return __block_result_1__

    def handle_bias(n: info, tf: str):
        _yloc = yloc.price
        _style = label.style_label_up if tf == 'D' else label.style_label_down
        _y = n.cl if tf == 'D' else n.ch
        can_plot = can_plot_d if tf == 'D' else can_plot_w
        if close[1] > n.ph:
            if n.bias == 1:
                n.close_ph = n.close_ph + 1
            n.bias = 1
            if bias_reason and can_plot:
                txt = 'Close Above P' + tf + 'H\nBias P' + tf + 'H'
                label.new(bar_index, _y, txt, textcolor=chart.fg_color, color=chart.bg_color, yloc=_yloc, style=_style)
        elif close[1] < n.pl:
            if n.bias == -1:
                n.close_pl = n.close_pl + 1
            n.bias = -1
            if bias_reason and can_plot:
                txt = 'Close Below P' + tf + 'L\nBias P' + tf + 'L'
                label.new(bar_index, _y, txt, textcolor=chart.fg_color, color=chart.bg_color, yloc=_yloc, style=_style)
        elif close[1] < n.ph and close[1] > n.pl and (n.ch > n.ph) and (n.cl > n.pl):
            n.bias = -1
            if bias_reason and can_plot:
                txt = 'Failed to Close Above P' + tf + 'H\nBias P' + tf + 'L'
                label.new(bar_index, _y, txt, textcolor=chart.fg_color, color=chart.bg_color, yloc=_yloc, style=_style)
        elif close[1] > n.pl and close[1] < n.ph and (n.ch < n.ph) and (n.cl < n.pl):
            n.bias = 1
            if bias_reason and can_plot:
                txt = 'Failed to Close Below P' + tf + 'L\nBias P' + tf + 'H'
                label.new(bar_index, _y, txt, textcolor=chart.fg_color, color=chart.bg_color, yloc=_yloc, style=_style)
        elif n.ch <= n.ph and n.cl >= n.pl:
            if n.p_up:
                n.bias = 1
            else:
                n.bias = -1
            if bias_reason and can_plot:
                txt = 'Close Inside\nBias P' + tf + ('H' if n.p_up else 'L')
                label.new(bar_index, _y, txt, textcolor=chart.fg_color, color=chart.bg_color, yloc=_yloc, style=_style)
        else:
            n.bias = 0
            if bias_reason and can_plot:
                txt: str = 'Outside Bar but Closed Inside\nNo Bias'
                label.new(bar_index, _y, txt, textcolor=chart.fg_color, color=chart.bg_color, yloc=_yloc, style=_style)
        __block_result_2__ = na
        if n.bias == 1:
            n.bias_ph = n.bias_ph + 1
            __block_result_2__ = alert('Bias P' + tf + 'H', alert.freq_once_per_bar)
        elif n.bias == -1:
            n.bias_pl = n.bias_pl + 1
            __block_result_2__ = alert('Bias P' + tf + 'L', alert.freq_once_per_bar)
        return __block_result_2__

    @method
    def update_info(n: info, tf: str):
        if new_day if tf == 'D' else new_week:
            if not na(n.ch):
                handle_bias(n, tf)
                if close[1] >= n.co:
                    n.p_up = True
                else:
                    n.p_up = False
                n.ph = n.ch
                n.pl = n.cl
                n.ch = high
                n.cl = low
                n.co = open
        __block_result_3__ = na
        if na(n.ch):
            n.ch = high
            n.ch = low
            __block_result_3__ = n.ch
        else:
            n.ch = math.max(high, n.ch)
            n.cl = math.min(low, n.cl)
            __block_result_3__ = n.cl
        return __block_result_3__

    @method
    def update_lines(L: list[lines], n: info, tf: str):
        hit_high: bool = False
        hit_low: bool = False
        can_plot = can_plot_d if tf == 'D' else can_plot_w
        if new_day if tf == 'D' else new_week:
            array.pop(L)
            _right = time + timeframe.in_seconds(tf) * 1000
            _style = line.style_solid if tf == 'D' else line.style_dashed
            array.unshift(L, lines(line.new(time, n.ph, _right, n.ph, xloc=xloc.bar_time, color=before_raid_color if can_plot else na, style=_style, width=line_width), line.new(time, n.pl, _right, n.pl, xloc=xloc.bar_time, color=before_raid_color if can_plot else na, style=_style, width=line_width), False, False))
        for i in pine_range(0, array.size(L) - 1, 1):
            x = array.get(L, i)
            if not na(x.ph_line):
                if high >= method_call('get_y1', x.ph_line) and (not x.hit_ph_line):
                    if stop_ext:
                        method_call('set_x2', x.ph_line, time)
                    if n.bias == 1:
                        n.hit_ph = n.hit_ph + 1
                    x.hit_ph_line = True
                    if can_plot:
                        method_call('set_color', x.ph_line, after_raid_color)
                    hit_high = True
                    alert('Hit P' + tf + 'H', alert.freq_once_per_bar)
                if low <= method_call('get_y1', x.pl_line) and (not x.hit_pl_line):
                    if stop_ext:
                        method_call('set_x2', x.pl_line, time)
                    if n.bias == -1:
                        n.hit_pl = n.hit_pl + 1
                    x.hit_pl_line = True
                    if can_plot:
                        method_call('set_color', x.pl_line, after_raid_color)
                    hit_low = True
                    alert('Hit P' + tf + 'L', alert.freq_once_per_bar)
        return (hit_high, hit_low)

    d_info: Persistent[info] = info()
    w_info: Persistent[info] = info()
    d_lines: Persistent[list[lines]] = array.new(1, lines())
    w_lines: Persistent[list[lines]] = array.new(1, lines())
    d_hit_high: bool = False
    d_hit_low: bool = False
    w_hit_high: bool = False
    w_hit_low: bool = False
    if d_stats and timeframe.in_seconds() <= timeframe.in_seconds('D'):
        update_info(d_info, 'D')
        hr, lr = update_lines(d_lines, d_info, 'D')
        d_hit_high = hr
        d_hit_low = lr
    if w_stats and timeframe.in_seconds() <= timeframe.in_seconds('W'):
        update_info(w_info, 'W')
        hr, lr = update_lines(w_lines, w_info, 'W')
        w_hit_high = hr
        w_hit_low = lr
    plotshape(can_plot_d and d_hit_high, 'PDH Raid', style=shape.triangleup, location=location.abovebar, color=after_raid_color, size=size.tiny)
    plotshape(can_plot_d and d_hit_low, 'PDL Raid', style=shape.triangledown, location=location.belowbar, color=after_raid_color, size=size.tiny)
    plotshape(can_plot_w and w_hit_high, 'PWH Raid', style=shape.triangleup, location=location.abovebar, color=after_raid_color, size=size.tiny)
    plotshape(can_plot_w and w_hit_low, 'PWL Raid', style=shape.triangledown, location=location.belowbar, color=after_raid_color, size=size.tiny)
    plotshape(d_bias_plot, 'Daily Bias', style=shape.square, size=size.tiny, location=location.top if d_bias_loc == 'Top' else location.bottom, color=bull_color if d_info.bias == 1 else bear_color if d_info.bias == -1 else na)
    plotshape(w_bias_plot, 'Weekly Bias', style=shape.square, size=size.tiny, location=location.top if w_bias_loc == 'Top' else location.bottom, color=bull_color if w_info.bias == 1 else bear_color if w_info.bias == -1 else na)
    alertcondition(new_day and d_info.bias == 1, 'Bias PDH', 'Bias PDH')
    alertcondition(new_day and d_info.bias == -1, 'Bias PDL', 'Bias PDL')
    alertcondition(new_day and d_info.bias == 0, 'No Daily Bias', 'No Daily Bias')
    alertcondition(new_week and w_info.bias == 1, 'Bias PWH', 'Bias PWH')
    alertcondition(new_week and w_info.bias == -1, 'Bias PWL', 'Bias PWL')
    alertcondition(new_week and w_info.bias == 0, 'No Weekly Bias', 'No Weekly Bias')
    alertcondition(d_hit_high, 'Hit PDH', 'Hit PDH')
    alertcondition(d_hit_low, 'Hit PDL', 'Hit PDL')
    alertcondition(w_hit_high, 'Hit PWH', 'Hit PWH')
    alertcondition(w_hit_low, 'Hit PWL', 'Hit PWL')
    def format_result(hit: int, bias: int):
        result: str = ''
        if bias > 0:
            result = string.tostring(math.floor(hit / bias * 1000) / 10)
        else:
            result = '0'
        result = result + '%'
        return result

    def format_color(bull: bool, n: info, L: list[lines]):
        result: Color = na(Color)
        __block_result_4__ = na
        if n.bias == 1 if bull else n.bias == -1:
            __block_result_5__ = na
            if array.get(L, 0).hit_ph_line if bull else array.get(L, 0).hit_pl_line:
                result = color.new(after_raid_color, 50)
                __block_result_5__ = result
            else:
                result = color.new(before_raid_color, 50)
                __block_result_5__ = result
            __block_result_4__ = __block_result_5__
        return __block_result_4__

    stats: Persistent = table.new(get_table_pos(tbl_loc), 20, 20, chart.bg_color, chart.fg_color, 2, chart.fg_color, 1)
    text_size: Persistent = get_table_size(tbl_size)
    if barstate.islast:
        table.cell(stats, 0, 0, 'Bias', text_color=chart.fg_color, text_size=text_size)
        if tbl_show_stats:
            table.cell(stats, 1, 0, 'Success\nRate', text_color=chart.fg_color, text_size=text_size)
            table.cell(stats, 2, 0, 'Close Thru\nRate', text_color=chart.fg_color, text_size=text_size)
            table.cell(stats, 3, 0, 'Sample\nSize', text_color=chart.fg_color, text_size=text_size)
        if d_stats:
            table.cell(stats, 0, 1, 'PDH', text_color=chart.fg_color, bgcolor=format_color(True, d_info, d_lines), text_size=text_size)
            table.cell(stats, 0, 2, 'PDL', text_color=chart.fg_color, bgcolor=format_color(False, d_info, d_lines), text_size=text_size)
            if tbl_show_stats:
                table.cell(stats, 1, 1, format_result(d_info.hit_ph, d_info.bias_ph), text_color=chart.fg_color, text_size=text_size)
                table.cell(stats, 1, 2, format_result(d_info.hit_pl, d_info.bias_pl), text_color=chart.fg_color, text_size=text_size)
                table.cell(stats, 2, 1, format_result(d_info.close_ph, d_info.hit_ph), text_color=chart.fg_color, text_size=text_size)
                table.cell(stats, 2, 2, format_result(d_info.close_pl, d_info.hit_pl), text_color=chart.fg_color, text_size=text_size)
                table.cell(stats, 3, 1, string.tostring(d_info.bias_ph), text_color=chart.fg_color, text_size=text_size)
                table.cell(stats, 3, 2, string.tostring(d_info.bias_pl), text_color=chart.fg_color, text_size=text_size)
        if w_stats:
            table.cell(stats, 0, 3, 'PWH', text_color=chart.fg_color, bgcolor=format_color(True, w_info, w_lines), text_size=text_size)
            table.cell(stats, 0, 4, 'PWL', text_color=chart.fg_color, bgcolor=format_color(False, w_info, w_lines), text_size=text_size)
            if tbl_show_stats:
                table.cell(stats, 1, 3, format_result(w_info.hit_ph, w_info.bias_ph), text_color=chart.fg_color, text_size=text_size)
                table.cell(stats, 1, 4, format_result(w_info.hit_pl, w_info.bias_pl), text_color=chart.fg_color, text_size=text_size)
                table.cell(stats, 2, 3, format_result(w_info.close_ph, w_info.hit_ph), text_color=chart.fg_color, text_size=text_size)
                table.cell(stats, 2, 4, format_result(w_info.close_pl, w_info.hit_pl), text_color=chart.fg_color, text_size=text_size)
                table.cell(stats, 3, 3, string.tostring(w_info.bias_ph), text_color=chart.fg_color, text_size=text_size)
                table.cell(stats, 3, 4, string.tostring(w_info.bias_pl), text_color=chart.fg_color, text_size=text_size)
    plot(d_info.bias, 'Daily Bias', color=na, display=display.none)
    plot(w_info.bias, 'Weekly Bias', color=na, display=display.none)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)