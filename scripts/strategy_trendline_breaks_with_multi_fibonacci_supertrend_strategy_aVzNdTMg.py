"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    bar_index, barstate, close, color, extend, fill, high, input, line,
    location, low, math, na, nz, plot, plotshape, script, shape, size, strategy, syminfo, ta
)
from pynecore.types import Line, Persistent, PersistentSeries, Series


@script.strategy('Trendline Breaks with Multi Fibonacci Supertrend Strategy', shorttitle="TMFS Strategy", overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=4, commission_type=strategy.commission.percent, commission_value=0.03, pyramiding=2)
def main(
    atrPeriod=input.int(13, 'ATR Length', minval=1, tooltip="ATR period used for volatility calculation"),
    factor1=input.float(0.618, 'Factor 1 (Weak/Fibonacci)', minval=0.01, step=0.01, tooltip="First Fibonacci factor (0.618)"),
    factor2=input.float(1.618, 'Factor 2 (Medium/Golden Ratio)', minval=0.01, step=0.01, tooltip="Second Fibonacci factor (1.618)"),
    factor3=input.float(2.618, 'Factor 3 (Strong/Extended Fib)', minval=0.01, step=0.01, tooltip="Third Fibonacci factor (2.618)"),
    superlength=input.int(21, "Smoothing Length", tooltip="EMA length for smoothing the average supertrend"),
    swing_length=input.int(8, 'Swing Lookback Period', tooltip="Number of bars to look back for pivot points"),
    atr_multiplier=input.float(1.0, 'ATR Slope Multiplier', minval=0.0, step=0.1, tooltip="Multiplier for ATR to control trendline slope"),
    show_extended_lines=input.bool(True, 'Show Extended Lines', tooltip="Display dashed extensions for trendlines"),
    enable_backpainting=input.bool(True, 'Use Backpainting', tooltip="Enable backpainting to move indicators to pivot point"),
    dmi_length=input.int(13, "DMI Length", tooltip="Length for DMI calculation"),
    enable_long_positions=input.bool(defval=True, title='Enable Long Positions', group='Strategy Settings'),
    enable_short_positions=input.bool(defval=True, title='Enable Short Positions', group='Strategy Settings'),
    fast_sma_length=input.int(defval=2, title='Fast SMA Length', minval=1, group='Strategy Settings'),
    slow_sma_length=input.int(defval=3, title='Slow SMA Length', minval=1, group='Strategy Settings'),
    atr_length=input.int(13, 'ATR Length for SL/TP', minval=1, group='Risk Management'),
    stop_loss_method=input.string(defval='ATR', title='Stop Loss Method', options=('PERC', 'ATR'), group='Stop Loss'),
    __input_16__=input.float(defval=0.75, title='Long Position Stop Loss %', minval=0.05, maxval=100, step=0.05, group='Stop Loss'),
    __input_17__=input.float(defval=0.75, title='Short Position Stop Loss %', minval=0.05, maxval=100, step=0.05, group='Stop Loss'),
    long_stop_loss_atr_multiplier=input.float(defval=8.0, title='Long Position ATR Multiplier', minval=0.1, step=0.1, group='Stop Loss'),
    short_stop_loss_atr_multiplier=input.float(defval=8.0, title='Short Position ATR Multiplier', minval=0.1, step=0.1, group='Stop Loss'),
    stop_loss_trailing_mode=input.string(defval='ON', title='Trailing Stop Loss Mode', options=('TP', 'ON', 'OFF'), tooltip='ON: Always trail, TP: Trail after Take Profit hit, OFF: Fixed stop', group='Stop Loss'),
    break_even_enabled=input.bool(defval=True, title='Move to Break Even After TP', group='Stop Loss'),
    take_profit_quantity_percent=input.float(defval=100, title='Take Profit Quantity %', minval=0.0, maxval=100, step=1.0, group='Take Profit'),
    take_profit_method=input.string(defval='PERC', title='Take Profit Method', options=('PERC', 'ATR', 'RR'), group='Take Profit'),
    __input_24__=input.float(defval=1, title='Long Position Take Profit %', minval=0.05, step=0.05, group='Take Profit'),
    __input_25__=input.float(defval=1, title='Short Position Take Profit %', minval=0.05, step=0.05, group='Take Profit'),
    long_take_profit_atr_multiplier=input.float(defval=1.5, title='Long Position TP ATR Multiplier', minval=0.1, step=0.1, group='Take Profit'),
    short_take_profit_atr_multiplier=input.float(defval=2, title='Short Position TP ATR Multiplier', minval=0.1, step=0.1, group='Take Profit'),
    long_risk_reward_ratio=input.float(defval=0.6, title='Long Position Risk/Reward Ratio', minval=0.1, step=0.1, group='Take Profit'),
    short_risk_reward_ratio=input.float(defval=1, title='Short Position Risk/Reward Ratio', minval=0.1, step=0.1, group='Take Profit'),
    trailing_take_profit_enabled=input.bool(defval=True, title='Enable Trailing Take Profit', group='Take Profit'),
    deviation_method=input.string(defval='PERC', title='Trailing Deviation Method', options=('PERC', 'ATR'), group='Take Profit'),
    __input_32__=input.float(defval=0.01, title='Trailing Deviation %', minval=0.01, maxval=100, step=0.05, group='Take Profit'),
    deviation_atr_multiplier=input.float(defval=1.0, title='Trailing Deviation ATR Multiplier', minval=0.01, step=0.05, group='Take Profit')
):
    supertrend1, direction1 = ta.supertrend(factor1, atrPeriod)
    supertrend2, direction2 = ta.supertrend(factor2, atrPeriod)
    supertrend3, direction3 = ta.supertrend(factor3, atrPeriod)

    supertrend1 = na if barstate.isfirst else supertrend1
    supertrend2 = na if barstate.isfirst else supertrend2
    supertrend3 = na if barstate.isfirst else supertrend3
    average_trend: Series = (supertrend1 + supertrend2 + supertrend3) / 3
    smoothed_trend: Series = ta.ema(average_trend, superlength)

    trend_plot = plot(average_trend, color=color.green if average_trend > average_trend[1] else color.red, title='Average Supertrend')
    smoothed_plot = plot(smoothed_trend, linewidth=2, color=color.green if smoothed_trend > smoothed_trend[1] else color.red, title='Smoothed Supertrend')
    fill(trend_plot, smoothed_plot, color=color.new(color.green, 50) if average_trend > smoothed_trend else color.new(color.red, 50), title='Trend Direction Fill')

    uptrend_color = color.new(color.teal, 0)
    downtrend_color = color.new(color.red, 0)

    upper_trendline: Persistent[float] = na(float)
    lower_trendline: Persistent[float] = na(float)
    upper_slope: Persistent[float] = na(float)
    lower_slope: Persistent[float] = na(float)
    upline_extension: Persistent[Line] = na(Line)
    downline_extension: Persistent[Line] = na(Line)

    offset = swing_length if enable_backpainting else 0
    bar_idx = bar_index

    pivot_high = ta.pivothigh(swing_length, swing_length)
    pivot_low = ta.pivotlow(swing_length, swing_length)

    atr_value = ta.atr(swing_length)
    slope = atr_value / swing_length * atr_multiplier

    if cast_bool(pivot_high):
        upper_slope = slope
        upper_trendline = pivot_high
    else:
        upper_trendline = nz(upper_trendline) - nz(upper_slope)

    if cast_bool(pivot_low):
        lower_slope = slope
        lower_trendline = pivot_low
    else:
        lower_trendline = nz(lower_trendline) + nz(lower_slope)

    if show_extended_lines:
        if na(upline_extension):
            upline_extension = line.new(na, na, na, na, extend=extend.right, style=line.style_dashed, color=uptrend_color)

        if na(downline_extension):
            downline_extension = line.new(na, na, na, na, extend=extend.right, style=line.style_dashed, color=downtrend_color)

        if cast_bool(pivot_high):
            line.set_xy1(upline_extension, bar_idx - offset, pivot_high if enable_backpainting else upper_trendline)
            line.set_xy2(upline_extension, bar_idx - offset + 1, pivot_high - slope if enable_backpainting else upper_trendline - slope)

        if cast_bool(pivot_low):
            line.set_xy1(downline_extension, bar_idx - offset, pivot_low if enable_backpainting else lower_trendline)
            line.set_xy2(downline_extension, bar_idx - offset + 1, pivot_low + slope if enable_backpainting else lower_trendline + slope)

    upper_breakout_state: PersistentSeries[int] = 0
    lower_breakout_state: PersistentSeries[int] = 0

    upper_breakout: bool = close > upper_trendline
    lower_breakout: bool = close < lower_trendline

    upper_breakout_state = 0 if cast_bool(pivot_high) else 1 if upper_breakout else upper_breakout_state
    lower_breakout_state = 0 if cast_bool(pivot_low) else 1 if lower_breakout else lower_breakout_state

    plot(upper_trendline if enable_backpainting else upper_trendline, color=na if cast_bool(pivot_high) else uptrend_color, linewidth=2, offset=-offset, title='Upper Trendline')
    plot(lower_trendline if enable_backpainting else lower_trendline, color=na if cast_bool(pivot_low) else downtrend_color, linewidth=2, offset=-offset, title='Lower Trendline')

    true_range = math.max(math.max(high - low, math.abs(high - nz(close[1]))), math.abs(low - nz(close[1])))

    directional_movement_plus = math.max(high - nz(high[1]), 0) if high - nz(high[1]) > nz(low[1]) - low else 0
    directional_movement_minus = math.max(nz(low[1]) - low, 0) if nz(low[1]) - low > high - nz(high[1]) else 0

    smoothed_true_range: PersistentSeries[float] = 0.0
    smoothed_true_range = nz(smoothed_true_range[1]) - nz(smoothed_true_range[1]) / dmi_length + true_range

    smoothed_directional_plus: PersistentSeries[float] = 0.0
    smoothed_directional_plus = nz(smoothed_directional_plus[1]) - nz(smoothed_directional_plus[1]) / dmi_length + directional_movement_plus

    smoothed_directional_minus: PersistentSeries[float] = 0.0
    smoothed_directional_minus = nz(smoothed_directional_minus[1]) - nz(smoothed_directional_minus[1]) / dmi_length + directional_movement_minus

    di_plus = smoothed_directional_plus / smoothed_true_range * 100
    di_minus = smoothed_directional_minus / smoothed_true_range * 100

    fast_sma = ta.sma(close, fast_sma_length)
    slow_sma = ta.sma(close, slow_sma_length)

    sma_cross_up = ta.crossover(fast_sma, slow_sma)
    sma_cross_down = ta.crossunder(fast_sma, slow_sma)

    long_entry_condition = enable_long_positions and upper_breakout_state > upper_breakout_state[1] and (di_plus > di_minus) and (close > smoothed_trend)
    short_entry_condition = enable_short_positions and lower_breakout_state > lower_breakout_state[1] and (di_minus > di_plus) and (close < smoothed_trend)

    long_exit_condition = ta.crossunder(close[1], smoothed_trend)
    short_exit_condition = ta.crossover(close[1], smoothed_trend)

    plotshape(long_entry_condition, title='BUY', text='BUY', location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    plotshape(short_entry_condition, title='SELL', text='SELL', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))

    long_trailing_tp_executed: PersistentSeries[bool] = False
    short_trailing_tp_executed: PersistentSeries[bool] = False

    entry_atr: float = ta.valuewhen(long_entry_condition or short_entry_condition, ta.atr(atr_length), 0)
    long_stop_loss_percent = __input_16__ / 100
    short_stop_loss_percent = __input_17__ / 100
    long_take_profit_percent = __input_24__ / 100
    short_take_profit_percent = __input_25__ / 100
    deviation_percent = __input_32__ / 100

    def get_long_stop_loss_price(base_price):
        __block_result__ = na
        __switch__ = stop_loss_method
        if __switch__ == 'PERC':
            __block_result__ = base_price * (1 - long_stop_loss_percent)
        elif __switch__ == 'ATR':
            __block_result__ = base_price - long_stop_loss_atr_multiplier * entry_atr
        else:
            __block_result__ = na
        return __block_result__

    long_tp_trailing_enabled = stop_loss_trailing_mode == 'ON' or (stop_loss_trailing_mode == 'TP' and long_trailing_tp_executed)

    long_stop_loss_price: PersistentSeries[float] = na(float)
    __block_result_1__ = na
    if strategy.position_size > 0:
        __block_result_2__ = na
        if long_entry_condition:
            __block_result_2__ = get_long_stop_loss_price(close)
        else:
            stop_price = get_long_stop_loss_price(high if long_tp_trailing_enabled else strategy.position_avg_price)
            stop_price = math.max(stop_price, strategy.position_avg_price) if break_even_enabled and long_trailing_tp_executed else stop_price
            __block_result_2__ = math.max(stop_price, nz(long_stop_loss_price[1]))
        __block_result_1__ = __block_result_2__
    else:
        __block_result_1__ = na
    long_stop_loss_price = __block_result_1__

    def get_short_stop_loss_price(base_price):
        __block_result_3__ = na
        __switch__ = stop_loss_method
        if __switch__ == 'PERC':
            __block_result_3__ = base_price * (1 + short_stop_loss_percent)
        elif __switch__ == 'ATR':
            __block_result_3__ = base_price + short_stop_loss_atr_multiplier * entry_atr
        else:
            __block_result_3__ = na
        return __block_result_3__

    short_tp_trailing_enabled = stop_loss_trailing_mode == 'ON' or (stop_loss_trailing_mode == 'TP' and short_trailing_tp_executed)

    short_stop_loss_price: PersistentSeries[float] = na(float)
    __block_result_4__ = na
    if strategy.position_size < 0:
        __block_result_5__ = na
        if short_entry_condition:
            __block_result_5__ = get_short_stop_loss_price(close)
        else:
            stop_price: Persistent[float] = get_short_stop_loss_price(low if short_tp_trailing_enabled else strategy.position_avg_price)
            if break_even_enabled and short_trailing_tp_executed:
                stop_price = math.min(stop_price, strategy.position_avg_price)
            short_stop_loss_price = math.min(stop_price, nz(short_stop_loss_price[1], 999999.9))
            __block_result_5__ = short_stop_loss_price
        __block_result_4__ = __block_result_5__
    else:
        __block_result_4__ = na
    short_stop_loss_price = __block_result_4__

    def get_long_take_profit_price():
        __block_result_6__ = na
        __switch__ = take_profit_method
        if __switch__ == 'PERC':
            __block_result_6__ = close * (1 + long_take_profit_percent)
        elif __switch__ == 'ATR':
            __block_result_6__ = close + long_take_profit_atr_multiplier * entry_atr
        elif __switch__ == 'RR':
            __block_result_6__ = close + long_risk_reward_ratio * (close - get_long_stop_loss_price(close))
        else:
            __block_result_6__ = na
        return __block_result_6__

    long_take_profit_price: PersistentSeries[float] = na(float)
    __block_result_7__ = na
    if strategy.position_size > 0 and (not long_trailing_tp_executed):
        __block_result_8__ = na
        if long_entry_condition:
            __block_result_8__ = get_long_take_profit_price()
        else:
            __block_result_8__ = nz(long_take_profit_price[1], get_long_take_profit_price())
        __block_result_7__ = __block_result_8__
    else:
        __block_result_7__ = na
    long_take_profit_price = __block_result_7__

    long_trailing_tp_executed = strategy.position_size > 0 and (long_trailing_tp_executed[1] or strategy.position_size < strategy.position_size[1] or (strategy.position_size[1] == 0 and high >= long_take_profit_price))

    __block_result_9__ = na
    __switch__ = deviation_method
    if __switch__ == 'PERC':
        __block_result_9__ = long_take_profit_price * deviation_percent / syminfo.mintick
    elif __switch__ == 'ATR':
        __block_result_9__ = deviation_atr_multiplier * entry_atr / syminfo.mintick
    else:
        __block_result_9__ = na
    long_trailing_tp_step_ticks = __block_result_9__

    def get_short_take_profit_price():
        __block_result_10__ = na
        __switch__ = take_profit_method
        if __switch__ == 'PERC':
            __block_result_10__ = close * (1 - short_take_profit_percent)
        elif __switch__ == 'ATR':
            __block_result_10__ = close - short_take_profit_atr_multiplier * entry_atr
        elif __switch__ == 'RR':
            __block_result_10__ = close - short_risk_reward_ratio * (get_short_stop_loss_price(close) - close)
        else:
            __block_result_10__ = na
        return __block_result_10__

    short_take_profit_price: PersistentSeries[float] = na(float)
    __block_result_11__ = na
    if strategy.position_size < 0 and (not short_trailing_tp_executed):
        __block_result_12__ = na
        if short_entry_condition:
            __block_result_12__ = get_short_take_profit_price()
        else:
            __block_result_12__ = nz(short_take_profit_price[1], get_short_take_profit_price())
        __block_result_11__ = __block_result_12__
    else:
        __block_result_11__ = na
    short_take_profit_price = __block_result_11__

    short_trailing_tp_executed = strategy.position_size < 0 and (short_trailing_tp_executed[1] or strategy.position_size > strategy.position_size[1] or (strategy.position_size[1] == 0 and low <= short_take_profit_price))

    __block_result_13__ = na
    __switch__ = deviation_method
    if __switch__ == 'PERC':
        __block_result_13__ = short_take_profit_price * deviation_percent / syminfo.mintick
    elif __switch__ == 'ATR':
        __block_result_13__ = deviation_atr_multiplier * entry_atr / syminfo.mintick
    else:
        __block_result_13__ = na
    short_trailing_tp_step_ticks = __block_result_13__

    if long_entry_condition:
        strategy.entry('L', strategy.long, comment='LONG')

    if short_entry_condition:
        strategy.entry('S', strategy.short, comment='SHORT')

    if long_exit_condition:
        strategy.close('L', comment='SL Triggered')

    if short_exit_condition:
        strategy.close('S', comment='SL Triggered')

    strategy.exit(id='Long Take Profit / Stop Loss', from_entry='L', qty_percent=take_profit_quantity_percent, limit=na if trailing_take_profit_enabled else long_take_profit_price, stop=long_stop_loss_price, trail_price=long_take_profit_price if trailing_take_profit_enabled else na, trail_offset=long_trailing_tp_step_ticks if trailing_take_profit_enabled else na, comment='TP/SL Triggered')
    strategy.exit(id='Long Stop Loss', from_entry='L', stop=long_stop_loss_price, comment='SL Triggered')

    strategy.exit(id='Short Take Profit / Stop Loss', from_entry='S', qty_percent=take_profit_quantity_percent, limit=na if trailing_take_profit_enabled else short_take_profit_price, stop=short_stop_loss_price, trail_price=short_take_profit_price if trailing_take_profit_enabled else na, trail_offset=short_trailing_tp_step_ticks if trailing_take_profit_enabled else na, comment='TP/SL Triggered')
    strategy.exit(id='Short Stop Loss', from_entry='S', stop=short_stop_loss_price, comment='SL Triggered')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
