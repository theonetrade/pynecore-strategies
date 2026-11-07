"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    array, bar_index, box, close, color, dayofmonth, dayofweek, extend, high,
    hour, input, line, low, minute, month, na, script, strategy, time, timeframe, timestamp, year
)
from pynecore.types import Box, Line, Persistent, Series


@script.strategy('BSL/SSL Sweep + FVG Strategy (Fixed Entry Logic)', overlay=True, margin_long=100, margin_short=100, default_qty_type=strategy.percent_of_equity, default_qty_value=10, initial_capital=1000000, close_by_id=True)
def main(
    show_levels=input.bool(True, 'Show BSL/SSL Levels', group='Display'),
    show_fvg=input.bool(True, 'Show FVG', group='Display'),
    fvg_lookback=input.int(10, 'FVG Detection Lookback', minval=3, maxval=50, group='FVG Settings'),
    min_fvg_size=input.float(0.001, 'Minimum FVG Size', minval=0.0001, group='FVG Settings'),
    session_7_929=input.session('0700-0929', 'BSL/SSL Session (7:00-9:29 EST)', group='Time Settings'),
    session_930_1030=input.session('0930-1030', 'Trading Window (9:30-10:30 EST)', group='Time Settings'),
    est_timezone=input.string('America/New_York', 'Timezone', group='Time Settings'),
    allow_wick_entries=input.bool(True, 'Allow Wick-Based Entries', group='Entry Settings', tooltip='Allow entries when wick breaks FVG, not just closes'),
    extend_trading_window=input.bool(True, 'Extend Trading Window', group='Entry Settings', tooltip='Allow entries until 11:30 AM instead of 10:30 AM')
):
    bsl: Persistent[float] = na(float)
    ssl: Persistent[float] = na(float)
    levels_set: Persistent[bool] = False
    bsl_swept: Persistent[bool] = False
    ssl_swept: Persistent[bool] = False
    bsl_line: Persistent[Line] = na(Line)
    ssl_line: Persistent[Line] = na(Line)
    fvg_boxes: Persistent[list[Box]] = array.new_box()
    fvg_tops: Persistent[list[float]] = array.new_float()
    fvg_bottoms: Persistent[list[float]] = array.new_float()
    fvg_is_bullish: Persistent[list[bool]] = array.new_bool()
    fvg_used_for_entry: Persistent[list[bool]] = array.new_bool()
    fvg_broken: Persistent[list[bool]] = array.new_bool()
    entry_price: Persistent[float] = na(float)
    stop_loss: Persistent[float] = na(float)
    in_trade: Persistent[bool] = False
    trade_direction: Persistent[str] = ''
    post_sweep_low: Persistent[float] = na(float)
    post_sweep_high: Persistent[float] = na(float)
    has_traded_today: Persistent[bool] = False
    trades_today: Persistent[int] = 0
    first_trade_was_loss: Persistent[bool] = False
    in_bsl_ssl_session: Series = time(timeframe.period, session_7_929, est_timezone)
    extended_session = '0930-1130' if extend_trading_window else '0930-1030'
    in_trading_window = time(timeframe.period, extended_session, est_timezone)
    current_hour_est = hour(time, est_timezone)
    current_minute_est = minute(time, est_timezone)
    is_11am_cutoff = current_hour_est == 11 and current_minute_est == 0
    new_day = dayofweek != dayofweek[1]
    start_time = timestamp(est_timezone, year, month, dayofmonth, 7, 0)
    end_time = timestamp(est_timezone, year, month, dayofmonth, 11, 30)
    in_fvg_window = time >= start_time and time <= end_time
    if new_day:
        bsl = na
        ssl = na
        levels_set = False
        bsl_swept = False
        ssl_swept = False
        post_sweep_low = na
        post_sweep_high = na
        in_trade = False
        has_traded_today = False
        trades_today = 0
        first_trade_was_loss = False
        trade_direction = ''
        if not na(bsl_line):
            line.delete(bsl_line)
            bsl_line = na
        if not na(ssl_line):
            line.delete(ssl_line)
            ssl_line = na
        array.clear(fvg_boxes)
        array.clear(fvg_tops)
        array.clear(fvg_bottoms)
        array.clear(fvg_is_bullish)
        array.clear(fvg_used_for_entry)
        array.clear(fvg_broken)
    if cast_bool(in_bsl_ssl_session):
        if na(bsl) or high > bsl:
            bsl = high
        if na(ssl) or low < ssl:
            ssl = low
    if not in_bsl_ssl_session and cast_bool(in_bsl_ssl_session[1]) and (not na(bsl)) and (not na(ssl)) and (not levels_set):
        levels_set = True
        if show_levels:
            bsl_line = line.new(bar_index, bsl, bar_index + 200, bsl, color=color.red, width=2, extend=extend.right)
            ssl_line = line.new(bar_index, ssl, bar_index + 200, ssl, color=color.blue, width=2, extend=extend.right)
    if not na(bsl_line) and show_levels:
        line.set_x2(bsl_line, bar_index + 50)
    if not na(ssl_line) and show_levels:
        line.set_x2(ssl_line, bar_index + 50)
    bullish_fvg = in_fvg_window and low[2] > high and (low[2] - high >= min_fvg_size)
    bearish_fvg = in_fvg_window and high[2] < low and (low - high[2] >= min_fvg_size)
    fvg_top = low[2] if bullish_fvg else low if bearish_fvg else na
    fvg_bot = high if bullish_fvg else high[2] if bearish_fvg else na
    if (bullish_fvg or bearish_fvg) and show_fvg:
        fvg_color = color.new(color.red, 85) if bullish_fvg else color.new(color.green, 85)
        new_box = box.new(bar_index - 2, fvg_top, bar_index + 50, fvg_bot, bgcolor=fvg_color, border_color=color.new(color.black, 90))
        array.push(fvg_boxes, new_box)
        array.push(fvg_tops, fvg_top)
        array.push(fvg_bottoms, fvg_bot)
        array.push(fvg_is_bullish, bullish_fvg)
        array.push(fvg_used_for_entry, False)
        array.push(fvg_broken, False)
    if array.size(fvg_boxes) > fvg_lookback:
        box.delete(array.shift(fvg_boxes))
        array.shift(fvg_tops)
        array.shift(fvg_bottoms)
        array.shift(fvg_is_bullish)
        array.shift(fvg_used_for_entry)
        array.shift(fvg_broken)
    if cast_bool(in_trading_window) and levels_set:
        if high >= bsl and (not bsl_swept):
            bsl_swept = True
            post_sweep_high = high
        if low <= ssl and (not ssl_swept):
            ssl_swept = True
            post_sweep_low = low
    if bsl_swept and high > post_sweep_high:
        post_sweep_high = high
    if ssl_swept and low < post_sweep_low:
        post_sweep_low = low
    if array.size(fvg_tops) > 0:
        for i in pine_range(0, array.size(fvg_tops) - 1, 1):
            current_broken = array.get(fvg_broken, i)
            if not current_broken:
                top = array.get(fvg_tops, i)
                bot = array.get(fvg_bottoms, i)
                is_bullish = array.get(fvg_is_bullish, i)
                if not is_bullish and close > top:
                    array.set(fvg_broken, i, True)
                if is_bullish and close < bot:
                    array.set(fvg_broken, i, True)
    can_enter_trade = trades_today == 0 or (first_trade_was_loss and trades_today < 2)
    if can_enter_trade and (not in_trade) and (array.size(fvg_tops) > 0) and levels_set:
        for i in pine_range(0, array.size(fvg_tops) - 1, 1):
            top = array.get(fvg_tops, i)
            bot = array.get(fvg_bottoms, i)
            is_bullish = array.get(fvg_is_bullish, i)
            already_used = array.get(fvg_used_for_entry, i)
            if not already_used:
                if not is_bullish and ssl_swept and (not na(post_sweep_low)):
                    entry_condition: bool = False
                    if allow_wick_entries:
                        entry_condition = high > top or close > top
                    else:
                        entry_condition = close > top
                    if entry_condition:
                        strategy.entry('Long', strategy.long)
                        stop_loss = post_sweep_low
                        in_trade = True
                        trade_direction = 'Long'
                        trades_today = trades_today + 1
                        has_traded_today = True
                        array.set(fvg_used_for_entry, i, True)
                        break
                if is_bullish and bsl_swept and (not na(post_sweep_high)):
                    entry_condition: bool = False
                    if allow_wick_entries:
                        entry_condition = low < bot or close < bot
                    else:
                        entry_condition = close < bot
                    if entry_condition:
                        strategy.entry('Short', strategy.short)
                        stop_loss = post_sweep_high
                        in_trade = True
                        trade_direction = 'Short'
                        trades_today = trades_today + 1
                        has_traded_today = True
                        array.set(fvg_used_for_entry, i, True)
                        break
    if in_trade and trades_today == 1:
        if trade_direction == 'Long' and low <= stop_loss:
            first_trade_was_loss = True
            in_trade = False
        if trade_direction == 'Short' and high >= stop_loss:
            first_trade_was_loss = True
            in_trade = False
    if in_trade and trades_today == 1:
        if trade_direction == 'Long' and high >= bsl:
            in_trade = False
        if trade_direction == 'Short' and low <= ssl:
            in_trade = False
    if in_trade and trades_today == 2:
        if trade_direction == 'Long' and (low <= stop_loss or high >= bsl):
            in_trade = False
        if trade_direction == 'Short' and (high >= stop_loss or low <= ssl):
            in_trade = False
    if in_trade:
        if trade_direction == 'Long':
            strategy.exit('Long Exit', from_entry='Long', stop=stop_loss, limit=bsl)
        if trade_direction == 'Short':
            strategy.exit('Short Exit', from_entry='Short', stop=stop_loss, limit=ssl)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
