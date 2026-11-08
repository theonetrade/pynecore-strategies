"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    barmerge, barstate, close, color, high, input, low, math, na, plot,
    position, request, script, session, string, syminfo, ta, table, ticker
)
from pynecore.types import Persistent

day_trading: str = 'Day'
multiday_trading: str = 'Multiday'
swing_trading: str = 'Swing'
position_trading: str = 'Position'
longterm_trading: str = 'Long-term'


@script.indicator('Saty ATR Levels', shorttitle='Saty ATR Levels', overlay=True)
def main(
    trading_type=input.string(day_trading, 'Trading Type', options=(day_trading, multiday_trading, swing_trading, position_trading, longterm_trading)),
    use_options_labels=input(True, 'Use Options Labels'),
    atr_length=input(14, 'ATR Length'),
    trigger_percentage=input(0.236, 'Trigger Percentage'),
    previous_close_level_color=input(color.white, 'Previous Close Level Color'),
    lower_trigger_level_color=input(color.yellow, 'Lower Trigger Level Color'),
    upper_trigger_level_color=input(color.aqua, 'Upper Trigger Level Color'),
    key_target_level_color=input(color.silver, 'Key Target Level Color'),
    atr_target_level_color=input(color.white, 'ATR Target Level Color'),
    intermediate_target_level_color=input(color.gray, 'Intermediate Target Level Color'),
    show_all_fibonacci_levels=input(True, 'Show All Fibonacci Levels'),
    show_extensions=input(False, 'Show Extensions'),
    level_size=input(2, 'Level Size'),
    show_info=input(True, 'Show Info Label'),
    use_current_close=input(False, 'Use Current Close'),
    fast_ema=input(8, 'Fast EMA'),
    pivot_ema=input(21, 'Pivot EMA'),
    slow_ema=input(34, 'Slow EMA')
):
    def timeframe_func():
        timeframe__ren__: str = 'D'
        __block_result__ = na
        if trading_type == day_trading:
            timeframe__ren__ = 'D'
            __block_result__ = timeframe__ren__
        elif trading_type == multiday_trading:
            timeframe__ren__ = 'W'
            __block_result__ = timeframe__ren__
        elif trading_type == swing_trading:
            timeframe__ren__ = 'M'
            __block_result__ = timeframe__ren__
        elif trading_type == position_trading:
            timeframe__ren__ = '3M'
            __block_result__ = timeframe__ren__
        elif trading_type == longterm_trading:
            timeframe__ren__ = '12M'
            __block_result__ = timeframe__ren__
        else:
            timeframe__ren__ = 'D'
            __block_result__ = timeframe__ren__
        return __block_result__

    price = close
    fast_ema_value = ta.ema(price, fast_ema)
    pivot_ema_value = ta.ema(price, pivot_ema)
    slow_ema_value = ta.ema(price, slow_ema)
    bullish = price >= fast_ema_value and fast_ema_value >= pivot_ema_value and (pivot_ema_value >= slow_ema_value)
    bearish = price <= fast_ema_value and fast_ema_value <= pivot_ema_value and (pivot_ema_value <= slow_ema_value)
    period_index = 0 if use_current_close else 1
    ticker__ren__ = ticker.new(syminfo.prefix, syminfo.ticker, session=session.extended)
    previous_close = request.security(ticker__ren__, timeframe_func(), close[period_index], gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    atr = request.security(ticker__ren__, timeframe_func(), inline_series(ta.atr(atr_length), period_index), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    period_high = request.security(ticker__ren__, timeframe_func(), high, gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    period_low = request.security(ticker__ren__, timeframe_func(), low, gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    range_1 = period_high - period_low
    tr_percent_of_atr = range_1 / atr * 100
    lower_trigger = previous_close - trigger_percentage * atr
    upper_trigger = previous_close + trigger_percentage * atr
    lower_0382 = previous_close - atr * 0.382
    upper_0382 = previous_close + atr * 0.382
    lower_0500 = previous_close - atr * 0.5
    upper_0500 = previous_close + atr * 0.5
    lower_0618 = previous_close - atr * 0.618
    upper_0618 = previous_close + atr * 0.618
    lower_0786 = previous_close - atr * 0.786
    upper_0786 = previous_close + atr * 0.786
    lower_1000 = previous_close - atr
    upper_1000 = previous_close + atr
    lower_1236 = lower_1000 - atr * 0.236
    upper_1236 = upper_1000 + atr * 0.236
    lower_1382 = lower_1000 - atr * 0.382
    upper_1382 = upper_1000 + atr * 0.382
    lower_1500 = lower_1000 - atr * 0.5
    upper_1500 = upper_1000 + atr * 0.5
    lower_1618 = lower_1000 - atr * 0.618
    upper_1618 = upper_1000 + atr * 0.618
    lower_1786 = lower_1000 - atr * 0.786
    upper_1786 = upper_1000 + atr * 0.786
    lower_2000 = lower_1000 - atr
    upper_2000 = upper_1000 + atr
    lower_2236 = lower_2000 - atr * 0.236
    upper_2236 = upper_2000 + atr * 0.236
    lower_2382 = lower_2000 - atr * 0.382
    upper_2382 = upper_2000 + atr * 0.382
    lower_2500 = lower_2000 - atr * 0.5
    upper_2500 = upper_2000 + atr * 0.5
    lower_2618 = lower_2000 - atr * 0.618
    upper_2618 = upper_2000 + atr * 0.618
    lower_2786 = lower_2000 - atr * 0.786
    upper_2786 = upper_2000 + atr * 0.786
    lower_3000 = lower_2000 - atr
    upper_3000 = upper_2000 + atr
    tr_vs_atr_color = color.green
    if tr_percent_of_atr <= 70:
        tr_vs_atr_color = color.green
    elif tr_percent_of_atr >= 90:
        tr_vs_atr_color = color.red
    else:
        tr_vs_atr_color = color.orange
    trading_mode: str = 'Day'
    if trading_type == day_trading:
        trading_mode = 'Day'
    elif trading_type == multiday_trading:
        trading_mode = 'Multiday'
    elif trading_type == swing_trading:
        trading_mode = 'Swing'
    elif trading_type == position_trading:
        trading_mode = 'Position'
    elif trading_type == longterm_trading:
        trading_mode = 'Long-term'
    else:
        trading_mode = ''
    long_label: str = ''
    short_label: str = ''
    if use_options_labels:
        long_label = 'Calls'
        short_label = 'Puts'
    else:
        long_label = 'Long'
        short_label = 'Short'
    trend_color = color.orange
    if bullish:
        trend_color = color.green
    elif bearish:
        trend_color = color.red
    else:
        trend_color = color.orange
    tbl: Persistent = table.new(position.top_right, 1, 4)
    if barstate.islast and show_info:
        table.cell(tbl, 0, 0, 'Saty ATR Levels', bgcolor=trend_color)
        table.cell(tbl, 0, 1, trading_mode + ' Range ($' + string.tostring(range_1, '#.##') + ') is ' + string.tostring(tr_percent_of_atr, '#.#') + '% of ATR ($' + string.tostring(atr, '#.##') + ')', bgcolor=tr_vs_atr_color)
        table.cell(tbl, 0, 2, long_label + ' > $' + string.tostring(upper_trigger, '#.##') + ' | +1 ATR $' + string.tostring(upper_1000, '#.##'), bgcolor=upper_trigger_level_color)
        table.cell(tbl, 0, 3, short_label + ' < $' + string.tostring(lower_trigger, '#.##') + ' | -1 ATR: $' + string.tostring(lower_1000, '#.##'), bgcolor=lower_trigger_level_color)
    plot(lower_3000 if show_extensions else na, color=color.new(atr_target_level_color, 40), linewidth=math.max(1, level_size), title='-300.0%', style=plot.style_stepline)
    plot(lower_2618 if show_extensions else na, color=color.new(key_target_level_color, 40), linewidth=math.max(1, level_size), title='-261.8%', style=plot.style_stepline)
    plot(lower_2236 if show_extensions else na, color=color.new(key_target_level_color, 40), linewidth=math.max(1, level_size), title='-223.6%', style=plot.style_stepline)
    plot(lower_2000 if show_extensions else na, color=color.new(atr_target_level_color, 40), linewidth=math.max(1, level_size), title='-200.0%', style=plot.style_stepline)
    plot(lower_1786 if show_all_fibonacci_levels and show_extensions else na, color=color.new(intermediate_target_level_color, 40), linewidth=math.max(1, level_size), title='-178.6%', style=plot.style_stepline)
    plot(lower_1618 if show_extensions else na, color=color.new(key_target_level_color, 40), linewidth=math.max(1, level_size), title='-161.8%', style=plot.style_stepline)
    plot(lower_1500 if show_all_fibonacci_levels and show_extensions else na, color=color.new(intermediate_target_level_color, 40), linewidth=math.max(1, level_size), title='-150.0%', style=plot.style_stepline)
    plot(lower_1382 if show_all_fibonacci_levels and show_extensions else na, color=color.new(intermediate_target_level_color, 40), linewidth=math.max(1, level_size), title='-138.2%', style=plot.style_stepline)
    plot(lower_1236 if show_extensions else na, color=color.new(key_target_level_color, 40), linewidth=math.max(1, level_size), title='-123.6%', style=plot.style_stepline)
    plot(lower_1000, color=color.new(atr_target_level_color, 40), linewidth=math.max(1, level_size), title='-100%', style=plot.style_stepline)
    plot(lower_0786 if show_all_fibonacci_levels else na, color=color.new(intermediate_target_level_color, 40), linewidth=math.max(1, level_size), title='-78.6%', style=plot.style_stepline)
    plot(lower_0618, color=color.new(key_target_level_color, 40), linewidth=math.max(1, level_size), title='-61.8%', style=plot.style_stepline)
    plot(lower_0500 if show_all_fibonacci_levels else na, color=color.new(intermediate_target_level_color, 40), linewidth=math.max(1, level_size), title='-50.0%', style=plot.style_stepline)
    plot(lower_0382 if show_all_fibonacci_levels else na, color=color.new(intermediate_target_level_color, 40), linewidth=math.max(1, level_size), title='-38.2%', style=plot.style_stepline)
    plot(lower_trigger, color=color.new(lower_trigger_level_color, 40), linewidth=math.max(1, level_size), title='Lower Trigger', style=plot.style_stepline)
    plot(previous_close, color=color.new(previous_close_level_color, 40), linewidth=math.max(1, level_size), title='Previous Close', style=plot.style_stepline)
    plot(upper_trigger, color=color.new(upper_trigger_level_color, 40), linewidth=math.max(1, level_size), title='Upper Trigger', style=plot.style_stepline)
    plot(upper_0382 if show_all_fibonacci_levels else na, color=color.new(intermediate_target_level_color, 40), linewidth=math.max(1, level_size), title='38.2%', style=plot.style_stepline)
    plot(upper_0500 if show_all_fibonacci_levels else na, color=color.new(intermediate_target_level_color, 40), linewidth=math.max(1, level_size), title='50.0%', style=plot.style_stepline)
    plot(upper_0618, color=color.new(key_target_level_color, 40), linewidth=math.max(1, level_size), title='61.8%', style=plot.style_stepline)
    plot(upper_0786 if show_all_fibonacci_levels else na, color=color.new(intermediate_target_level_color, 40), linewidth=math.max(1, level_size), title='78.6%', style=plot.style_stepline)
    plot(upper_1000, color=color.new(atr_target_level_color, 40), linewidth=math.max(1, level_size), title='100%', style=plot.style_stepline)
    plot(upper_1236 if show_extensions else na, color=color.new(key_target_level_color, 40), linewidth=math.max(1, level_size), title='123.6%', style=plot.style_stepline)
    plot(upper_1382 if show_all_fibonacci_levels and show_extensions else na, color=color.new(intermediate_target_level_color, 40), linewidth=math.max(1, level_size), title='138.2%', style=plot.style_stepline)
    plot(upper_1500 if show_all_fibonacci_levels and show_extensions else na, color=color.new(intermediate_target_level_color, 40), linewidth=math.max(1, level_size), title='150.0%', style=plot.style_stepline)
    plot(upper_1618 if show_extensions else na, color=color.new(key_target_level_color, 40), linewidth=math.max(1, level_size), title='161.8%', style=plot.style_stepline)
    plot(upper_1786 if show_all_fibonacci_levels and show_extensions else na, color=color.new(intermediate_target_level_color, 40), linewidth=math.max(1, level_size), title='178.6%', style=plot.style_stepline)
    plot(upper_2000 if show_extensions else na, color=color.new(atr_target_level_color, 40), linewidth=math.max(1, level_size), title='200.0%', style=plot.style_stepline)
    plot(upper_2236 if show_extensions else na, color=color.new(key_target_level_color, 40), linewidth=math.max(1, level_size), title='223.6%', style=plot.style_stepline)
    plot(upper_2618 if show_extensions else na, color=color.new(key_target_level_color, 40), linewidth=math.max(1, level_size), title='261.8%', style=plot.style_stepline)
    plot(upper_3000 if show_extensions else na, color=color.new(atr_target_level_color, 40), linewidth=math.max(1, level_size), title='300%', style=plot.style_stepline)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
