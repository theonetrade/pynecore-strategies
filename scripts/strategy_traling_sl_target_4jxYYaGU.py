"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    array, bar_index, close, color, dayofmonth, hour, input, label, minute,
    month, na, plot, position, script, second, size, strategy, string, ta, table, time, year, yloc
)
from pynecore.types import Label, NA, Persistent


@script.strategy('Traling.SL.Target', overlay=True, process_orders_on_close=True, max_labels_count=500, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    _1=input.bool(title='━━━━━━━ ↓ Pivot parameters for trade ↓ ━━━━━━━', defval=False),
    fast_len=input.int(title='Fast len', defval=20),
    slow_len=input.int(title='Slow len', defval=50),
    label_bg_color=input.color(title='BG color for ongoing trade SL/Target label', defval=color.white),
    sl_target_method=input.string(title='Method to be used for SL/Target trailing', defval='% Based Target and SL', options=('% Based Target and SL', 'Fix point Based Target and SL')),
    _2=input.bool(title='━━━━━━━ ↓ % Based Target and SL ↓ ━━━━━━━', defval=True),
    __input_6__=input.float(title='Inital profit %', defval=1),
    __input_7__=input.float(title='Inital SL %', defval=1),
    __input_8__=input.float(title='Initiate trailing %', defval=0.5, tooltip='Initiate trailing of target and SL after change in price in % after taking trade'),
    __input_9__=input.float(title='Trail profit by %', defval=0.3),
    __input_10__=input.float(title='Trail SL by %', defval=0.3),
    _3=input.bool(title='━━━━━━━ ↓ Fix point Based Target and SL ↓ ━━━━━━━', defval=False),
    initial_profit_points=input.float(title='Inital profit target points', defval=100),
    initial_sl_points=input.float(title='Inital SL points', defval=50),
    initiate_trailing_points=input.float(title='Initiate trailing points', defval=60, tooltip='Initiate trailing of target and SL after change in price in points after taking trade'),
    trail_profit_points=input.float(title='Trail profit by points', defval=25),
    trail_sl_points=input.float(title='Trail SL by %', defval=30)
):
    initial_profit_percent = __input_6__ / 100
    initial_sl_percent = __input_7__ / 100
    initiate_trailing_percent = __input_8__ / 100
    trail_profit_percent = __input_9__ / 100
    trail_sl_percent = __input_10__ / 100
    tab = table.new(position=position.bottom_right, columns=7, rows=200, frame_color=color.yellow, frame_width=1)
    def msg(row: int, col: int, msg_str: str, clr = color.blue):
        return table.cell(table_id=tab, column=col, row=row, text=msg_str, text_color=clr)

    def getVal(val):
        ret_val = 0 if na(val) else val
        return ret_val

    def t(val):
        return string.tostring(val, '0.00')

    def timeToString(_t: int):
        return string.tostring(dayofmonth(_t), '00') + '/' + string.tostring(month(_t), '00') + '/' + string.tostring(year(_t), '0000') + ' ' + string.tostring(hour(_t), '00') + ':' + string.tostring(minute(_t), '00') + ':' + string.tostring(second(_t), '00')

    percent_based = True if sl_target_method == '% Based Target and SL' else False
    initial_long_entry_price: Persistent = NA(float)
    initial_short_entry_price: Persistent = NA(float)
    long_target: Persistent = NA(float)
    long_sl: Persistent = NA(float)
    short_target: Persistent = NA(float)
    short_sl: Persistent = NA(float)
    long_entry_price: Persistent = NA(float)
    short_entry_price: Persistent = NA(float)
    initial_long_percent_target: Persistent = NA(float)
    initial_long_percent_sl: Persistent = NA(float)
    initial_long_point_target: Persistent = NA(float)
    initial_long_point_sl: Persistent = NA(float)
    initial_short_percent_target: Persistent = NA(float)
    initial_short_percent_sl: Persistent = NA(float)
    initial_short_point_target: Persistent = NA(float)
    initial_short_point_sl: Persistent = NA(float)
    is_long: Persistent = NA(bool)
    is_short: Persistent = NA(bool)
    trail_long_iteration: Persistent = NA(int)
    trail_short_iteration: Persistent = NA(int)
    fast_ema = ta.ema(close, fast_len)
    slow_ema = ta.ema(close, slow_len)
    plot(fast_ema, color=color.red)
    plot(slow_ema, color=color.green)
    go_long = ta.crossover(fast_ema, slow_ema) and strategy.position_size == 0
    go_short = ta.crossunder(fast_ema, slow_ema) and strategy.position_size == 0
    long_trailing_point = close >= long_entry_price + long_entry_price * initiate_trailing_percent if percent_based else close >= long_entry_price + initiate_trailing_points
    short_trailing_point = close <= short_entry_price - short_entry_price * initiate_trailing_percent if percent_based else close >= short_entry_price - initiate_trailing_points
    if is_long and long_trailing_point:
        trail_long_iteration = trail_long_iteration + 1
        long_target = long_target + long_target * trail_profit_percent if percent_based else long_target + trail_profit_points
        long_sl = long_sl + long_sl * trail_sl_percent if percent_based else long_sl + trail_sl_points
        long_entry_price = long_entry_price + long_entry_price * initiate_trailing_percent if percent_based else long_entry_price + initiate_trailing_points
    if is_short and short_trailing_point:
        trail_short_iteration = trail_short_iteration + 1
        short_target = short_target - short_target * trail_profit_percent if percent_based else short_target - trail_profit_points
        short_sl = short_sl - short_sl * trail_sl_percent if percent_based else short_sl - trail_sl_points
        short_entry_price = short_entry_price - short_entry_price * initiate_trailing_percent if percent_based else short_entry_price - initiate_trailing_points
    if go_long:
        is_long = True
        is_short = False
        trail_long_iteration = 0
        trail_short_iteration = 0
        initial_long_entry_price = close
        long_entry_price = close
        initial_long_percent_target = close + close * initial_profit_percent
        initial_long_percent_sl = close - close * initial_sl_percent
        initial_long_point_target = close + initial_profit_points
        initial_long_point_sl = close - initial_sl_points
        long_target = initial_long_percent_target if percent_based else initial_long_point_target
        long_sl = initial_long_percent_sl if percent_based else initial_long_point_sl
        strategy.entry(id='Long', direction=strategy.long)
    if go_short:
        is_long = False
        is_short = True
        trail_long_iteration = 0
        trail_short_iteration = 0
        initial_short_entry_price = close
        short_entry_price = close
        initial_short_percent_target = close - close * initial_profit_percent
        initial_short_percent_sl = close + close * initial_sl_percent
        initial_short_point_target = close - initial_profit_points
        initial_short_point_sl = close + initial_sl_points
        short_target = initial_short_percent_target if percent_based else initial_short_point_target
        short_sl = initial_short_percent_sl if percent_based else initial_short_point_sl
        strategy.entry(id='Short', direction=strategy.short)
    method__ren__ = '% Based' if percent_based else 'Fixed Points'
    long_tooltip = 'Long @ ' + timeToString(time) + '\n' + 'Method             : ' + method__ren__ + '\n' + 'Initial Trade Price: ' + t(initial_long_entry_price) + '\n' + 'Inital Target      : ' + t(long_target) + '\n' + 'Inital SL          : ' + t(long_sl)
    short_tooltip = 'Short @ ' + timeToString(time) + '\n' + 'Method             : ' + method__ren__ + '\n' + 'Initial Trade Price: ' + t(initial_short_entry_price) + '\n' + 'Inital Target      : ' + t(short_target) + '\n' + 'Inital SL          : ' + t(short_sl)
    label.new(bar_index if go_long else na, bar_index if go_long else na, style=label.style_diamond, yloc=yloc.belowbar, color=color.green, size=size.tiny, tooltip=long_tooltip)
    label.new(bar_index if go_short else na, bar_index if go_short else na, style=label.style_diamond, yloc=yloc.abovebar, color=color.red, size=size.tiny, tooltip=short_tooltip)
    trail_long_tooltip = 'Trail @ ' + timeToString(time) + '\n' + 'Iteration no : ' + t(trail_long_iteration) + '\n' + 'New Target   : ' + t(long_target) + '\n' + 'New SL       : ' + t(long_sl)
    trail_short_tooltip = 'Trail @ ' + timeToString(time) + '\n' + 'Iteration no : ' + t(trail_short_iteration) + '\n' + 'New Target   : ' + t(short_target) + '\n' + 'New SL       : ' + t(short_sl)
    label.new(bar_index if is_long and long_trailing_point and (strategy.position_size > 0) else na, bar_index if is_long and long_trailing_point and (strategy.position_size > 0) else na, text=string.tostring(trail_long_iteration), style=label.style_circle, textcolor=color.white, yloc=yloc.belowbar, color=color.green, size=size.tiny, tooltip=trail_long_tooltip)
    label.new(bar_index if is_short and short_trailing_point and (strategy.position_size < 0) else na, bar_index if is_short and short_trailing_point and (strategy.position_size < 0) else na, text=string.tostring(trail_short_iteration), style=label.style_circle, textcolor=color.white, yloc=yloc.abovebar, color=color.red, size=size.tiny, tooltip=trail_short_tooltip)
    if close <= long_sl:
        strategy.close(id='Long', comment='SL')
    if close >= short_sl:
        strategy.close(id='Short', comment='SL')
    if close >= long_target:
        strategy.close(id='Long', comment='Target')
    if close <= short_target:
        strategy.close(id='Short', comment='Target')
    no_of_labels: int = 1
    def label_q(_array, _val):
        array.push(_array, _val)
        _return = array.shift(_array)
        return _return

    target_label: Persistent = NA(float)
    sl_label: Persistent = NA(float)
    if strategy.position_size > 0:
        target_label = long_target
        sl_label = long_sl
    elif strategy.position_size < 0:
        target_label = short_target
        sl_label = short_sl
    else:
        target_label = NA(float)
        sl_label = NA(float)
    target_array: Persistent[list[Label]] = array.new_label(no_of_labels)
    label.delete(label_q(target_array, label.new(bar_index, target_label, 'Target:' + t(target_label), style=label.style_label_down, color=label_bg_color, size=size.small, textcolor=color.green)))
    sl_array: Persistent[list[Label]] = array.new_label(no_of_labels)
    label.delete(label_q(sl_array, label.new(bar_index, sl_label, 'SL:' + t(sl_label), style=label.style_label_up, color=label_bg_color, size=size.small, textcolor=color.red)))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
