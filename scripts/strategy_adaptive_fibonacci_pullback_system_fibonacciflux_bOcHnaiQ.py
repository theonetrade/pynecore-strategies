"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barstate, close, color, fill, high, input, location, low, math, na, nz,
    plot, plotshape, request, script, shape, size, strategy, syminfo, ta, volume
)
from pynecore.types import Persistent, PersistentSeries, Series

filter_group: str = 'MTF Filters'
risk_group: str = 'Risk Management'
sl_group: str = 'Stop Loss Settings'
tp_group: str = 'Take Profit Settings'


@script.strategy('Adaptive Fibonacci Pullback System -FibonacciFlux', shorttitle='AFPS', overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=7.5, commission_type=strategy.commission.percent, commission_value=0.03, pyramiding=1, slippage=2)
def main(
    st_atr_period=input.int(8, 'Supertrend ATR Length', minval=1, group='Supertrend Settings', tooltip='ATR period for Supertrend calculations'),
    st_factor1=input.float(0.618, 'Factor 1 (0.618)', minval=0.01, step=0.01, group='Supertrend Settings', tooltip='Weak Fibonacci factor'),
    st_factor2=input.float(1.618, 'Factor 2 (1.618)', minval=0.01, step=0.01, group='Supertrend Settings', tooltip='Medium/Golden Ratio factor'),
    st_factor3=input.float(2.618, 'Factor 3 (2.618)', minval=0.01, step=0.01, group='Supertrend Settings', tooltip='Strong/Extended Fibonacci factor'),
    st_smooth_length=input.int(21, 'Supertrend Smoothing Length', group='Supertrend Settings', tooltip='EMA length for smoothing the average Supertrend'),
    ama_length=input.int(55, 'AMA Channel Length', group='AMA Channel Settings'),
    use_mtf_filters=input.bool(True, title='--- Use MTF Filters? ---', group=filter_group, tooltip='Enable/Disable all MTF Filters globally.'),
    rsi_filter_enable=input.bool(True, title='Enable RSI Filter', group=filter_group, tooltip='Filter signals based on RSI from a lower timeframe.'),
    rsi_timeframe=input.timeframe('60', title='RSI Timeframe', group=filter_group),
    rsi_length=input.int(7, title='RSI Length', minval=1, group=filter_group),
    rsi_buy_threshold=input.int(70, title='RSI Buy Threshold (>)', minval=0, maxval=100, group=filter_group, tooltip='RSI must be above this value for a Long signal.'),
    rsi_sell_threshold=input.int(30, title='RSI Sell Threshold (<)', minval=0, maxval=100, group=filter_group, tooltip='RSI must be below this value for a Short signal.'),
    macd_filter_enable=input.bool(False, title='Enable MACD Filter', group=filter_group, tooltip='Filter signals based on MACD crossover from a lower timeframe.'),
    macd_timeframe=input.timeframe('1', title='MACD Timeframe', group=filter_group),
    macd_fast_length=input.int(12, title='MACD Fast Length', minval=1, group=filter_group),
    macd_slow_length=input.int(26, title='MACD Slow Length', minval=1, group=filter_group),
    macd_signal_length=input.int(9, title='MACD Signal Length', minval=1, group=filter_group),
    volume_filter_enable=input.bool(False, title='Enable Volume Filter', group=filter_group, tooltip='Filter signals based on Volume increase from a lower timeframe.'),
    volume_timeframe=input.timeframe('1', title='Volume Timeframe', group=filter_group),
    volume_lookback=input.int(20, title='Volume MA Lookback', minval=1, group=filter_group, tooltip='Lookback period for the Volume Moving Average.'),
    volume_multiplier=input.float(1.3, title='Volume Multiplier (> Avg)', minval=0.1, step=0.1, group=filter_group, tooltip='Current volume must be > (Volume MA * Multiplier) for signal.'),
    enable_long_positions=input.bool(True, title='Enable Long Positions', group='Strategy Settings'),
    enable_short_positions=input.bool(True, title='Enable Short Positions', group='Strategy Settings'),
    atr_length_sl_tp=input.int(13, 'ATR Length for SL/TP', minval=1, group=risk_group),
    stop_loss_method=input.string('ATR', 'Stop Loss Method', options=('PERC', 'ATR'), group=sl_group),
    __input_25__=input.float(0.75, 'Long SL %', minval=0.05, maxval=100, step=0.05, group=sl_group),
    __input_26__=input.float(0.75, 'Short SL %', minval=0.05, maxval=100, step=0.05, group=sl_group),
    long_stop_loss_atr_multiplier=input.float(8.0, 'Long SL ATR Multiplier', minval=0.1, step=0.1, group=sl_group),
    short_stop_loss_atr_multiplier=input.float(8.0, 'Short SL ATR Multiplier', minval=0.1, step=0.1, group=sl_group),
    stop_loss_trailing_mode=input.string('ON', 'Trailing Stop Loss Mode', options=('TP', 'ON', 'OFF'), tooltip='ON: Always trail, TP: Trail after Take Profit hit, OFF: Fixed stop', group=sl_group),
    break_even_enabled=input.bool(True, 'Move SL to Break Even After TP', group=sl_group),
    take_profit_quantity_percent=input.float(100, 'Take Profit Quantity %', minval=0.0, maxval=100, step=1.0, group=tp_group),
    take_profit_method=input.string('PERC', 'Take Profit Method', options=('PERC', 'ATR', 'RR'), group=tp_group),
    __input_33__=input.float(5.0, 'Long TP %', minval=0.05, step=0.05, group=tp_group),
    __input_34__=input.float(5.0, 'Short TP %', minval=0.05, step=0.05, group=tp_group),
    long_take_profit_atr_multiplier=input.float(1.5, 'Long TP ATR Multiplier', minval=0.1, step=0.1, group=tp_group),
    short_take_profit_atr_multiplier=input.float(2.0, 'Short TP ATR Multiplier', minval=0.1, step=0.1, group=tp_group),
    long_risk_reward_ratio=input.float(0.6, 'Long Risk/Reward Ratio', minval=0.1, step=0.1, group=tp_group),
    short_risk_reward_ratio=input.float(1.0, 'Short Risk/Reward Ratio', minval=0.1, step=0.1, group=tp_group),
    trailing_take_profit_enabled=input.bool(True, 'Enable Trailing Take Profit', group=tp_group),
    deviation_method=input.string('PERC', 'Trailing Deviation Method', options=('PERC', 'ATR'), group=tp_group),
    __input_41__=input.float(0.01, 'Trailing Deviation %', minval=0.01, maxval=100, step=0.05, group=tp_group),
    deviation_atr_multiplier=input.float(1.0, 'Trailing Deviation ATR Multiplier', minval=0.01, step=0.05, group=tp_group)
):
    fiboLine1: str = '██████╗  ██╗ ██████╗  ██████╗ ███╗  ██╗  █████╗   ██████╗  ██████╗   ██╗'
    fiboLine2: str = '██╔════╝ ██║ ██╔══██╗██╔══██╗████╗  ██║ ██╔══██╗ ██╔════╝ ██╔════╝   ██║'
    fiboLine3: str = '██████╗  ██║ ██████╔╝██║  ██║██╔██╗ ██║ ███████║ ██║      ██║        ██║'
    fiboLine4: str = '██╔════╝ ██║ ██╔══██╗██║  ██║██║╚██╗██║ ██╔══██║ ██║   █╗ ██║   █╗   ██║'
    fiboLine5: str = '██║      ██║ ██████╔╝██████╔╝██║ ╚████║ ██║  ██║ ███████║ ███████║   ██║'

    fluxLine1: str = '██████╗  ██║     ██╗   ██╗ ██╗  ██╗'
    fluxLine2: str = '██╔════╝ ██║     ██║   ██║ ╚██╗██╔╝'
    fluxLine3: str = '██████╗  ██║     ██║   ██║  ╚███╔╝ '
    fluxLine4: str = '██╔════╝ ██║     ██║   ██║  ██╔██╗ '
    fluxLine5: str = '██║      ███████╗╚██████╔╝ ██╔╝ ██╗'

    supertrend1, direction1 = ta.supertrend(st_factor1, st_atr_period)
    supertrend2, direction2 = ta.supertrend(st_factor2, st_atr_period)
    supertrend3, direction3 = ta.supertrend(st_factor3, st_atr_period)

    supertrend1 = na if barstate.isfirst else supertrend1
    supertrend2 = na if barstate.isfirst else supertrend2
    supertrend3 = na if barstate.isfirst else supertrend3
    average_supertrend: Series = (supertrend1 + supertrend2 + supertrend3) / 3
    smoothed_supertrend: Series = ta.ema(average_supertrend, st_smooth_length)

    ama1: Series[float] = 0.0
    ama2: Series[float] = 0.0
    hh = math.max(math.sign(ta.change(ta.highest(ama_length))), 0)
    ll = math.max(math.sign(ta.change(ta.lowest(ama_length)) * -1), 0)
    tc = math.pow(ta.sma(1.0 if hh > 0 or ll > 0 else 0.0, ama_length), 2)

    ama1 = nz(ama1[1] + tc * (high - ama1[1]), high)
    ama2 = nz(ama2[1] + tc * (low - ama2[1]), low)

    ama_high_band = ama1
    ama_low_band = ama2
    ama_midline: Series = (ama_high_band + ama_low_band) / 2

    ama_dist = (ama_high_band - ama_low_band) / 2
    ama_h6 = ama_midline + ama_dist * 13.618
    ama_h5 = ama_midline + ama_dist * 8.618
    ama_h4 = ama_midline + ama_dist * 5.618
    ama_h3 = ama_midline + ama_dist * 3.618
    ama_h2 = ama_midline + ama_dist * 2.618
    ama_h1 = ama_midline + ama_dist * 1.618
    ama_l1 = ama_midline - ama_dist * 1.618
    ama_l2 = ama_midline - ama_dist * 2.618
    ama_l3 = ama_midline - ama_dist * 3.618
    ama_l4 = ama_midline - ama_dist * 5.618
    ama_l5 = ama_midline - ama_dist * 8.618
    ama_l6 = ama_midline - ama_dist * 13.618

    ltf_rsi_value = request.security(syminfo.tickerid, rsi_timeframe, ta.rsi(close, rsi_length))
    rsi_filter_long_ok = not use_mtf_filters or not rsi_filter_enable or ltf_rsi_value > rsi_buy_threshold
    rsi_filter_short_ok = not use_mtf_filters or not rsi_filter_enable or ltf_rsi_value < rsi_sell_threshold

    ltf_macd_line, ltf_macd_signal, _ = request.security(syminfo.tickerid, macd_timeframe, ta.macd(close, macd_fast_length, macd_slow_length, macd_signal_length))
    macd_filter_long_ok = not use_mtf_filters or not macd_filter_enable or ltf_macd_line > ltf_macd_signal
    macd_filter_short_ok = not use_mtf_filters or not macd_filter_enable or ltf_macd_line < ltf_macd_signal

    ltf_volume = request.security(syminfo.tickerid, volume_timeframe, volume)
    ltf_volume_ma = request.security(syminfo.tickerid, volume_timeframe, ta.sma(volume, volume_lookback))
    volume_filter_ok = not use_mtf_filters or not volume_filter_enable or ltf_volume > ltf_volume_ma * volume_multiplier

    base_long_entry = low < average_supertrend and close > smoothed_supertrend and (close[1] > ama_midline)
    base_short_entry = high > average_supertrend and close < smoothed_supertrend and (close[1] < ama_midline)

    long_entry_condition = enable_long_positions and base_long_entry and rsi_filter_long_ok and macd_filter_long_ok and volume_filter_ok and (close > ama_midline)
    short_entry_condition = enable_short_positions and base_short_entry and rsi_filter_short_ok and macd_filter_short_ok and volume_filter_ok and (close < ama_midline)

    long_exit_condition = ta.crossunder(close[1], smoothed_supertrend)
    short_exit_condition = ta.crossover(close[1], smoothed_supertrend)

    long_stop_loss_percent = __input_25__ / 100
    short_stop_loss_percent = __input_26__ / 100
    long_take_profit_percent = __input_33__ / 100
    short_take_profit_percent = __input_34__ / 100
    deviation_percent = __input_41__ / 100

    entry_atr = ta.valuewhen(long_entry_condition or short_entry_condition, ta.atr(atr_length_sl_tp), 0)

    long_stop_loss_price: PersistentSeries[float] = na(float)
    long_trailing_tp_executed: PersistentSeries[bool] = False

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

    __block_result_1__ = na
    if strategy.position_size > 0:
        initial_sl: float = get_long_stop_loss_price(strategy.opentrades.entry_price(0))
        trail_sl: float = get_long_stop_loss_price(high) if long_tp_trailing_enabled else na
        current_sl: float = nz(long_stop_loss_price[1], initial_sl)

        new_sl = initial_sl
        if not na(trail_sl):
            new_sl = math.max(current_sl, trail_sl)
        if break_even_enabled and long_trailing_tp_executed:
            new_sl = math.max(new_sl, strategy.opentrades.entry_price(0))

        __block_result_1__ = math.max(initial_sl, new_sl)
    else:
        __block_result_1__ = na
    long_stop_loss_price = __block_result_1__

    short_stop_loss_price: PersistentSeries[float] = na(float)
    short_trailing_tp_executed: PersistentSeries[bool] = False

    def get_short_stop_loss_price(base_price):
        __block_result_2__ = na
        __switch__ = stop_loss_method
        if __switch__ == 'PERC':
            __block_result_2__ = base_price * (1 + short_stop_loss_percent)
        elif __switch__ == 'ATR':
            __block_result_2__ = base_price + short_stop_loss_atr_multiplier * entry_atr
        else:
            __block_result_2__ = na
        return __block_result_2__

    short_tp_trailing_enabled = stop_loss_trailing_mode == 'ON' or (stop_loss_trailing_mode == 'TP' and short_trailing_tp_executed)

    __block_result_3__ = na
    if strategy.position_size < 0:
        initial_sl: float = get_short_stop_loss_price(strategy.opentrades.entry_price(0))
        trail_sl: float = get_short_stop_loss_price(low) if short_tp_trailing_enabled else na
        current_sl: float = nz(short_stop_loss_price[1], initial_sl)

        new_sl = initial_sl
        if not na(trail_sl):
            new_sl = math.min(current_sl, trail_sl)
        if break_even_enabled and short_trailing_tp_executed:
            new_sl = math.min(new_sl, strategy.opentrades.entry_price(0))

        __block_result_3__ = math.min(initial_sl, new_sl)
    else:
        __block_result_3__ = na
    short_stop_loss_price = __block_result_3__

    long_take_profit_price: Persistent[float] = na(float)

    def get_long_take_profit_price(entryPrice):
        __block_result_4__ = na
        __switch__ = take_profit_method
        if __switch__ == 'PERC':
            __block_result_4__ = entryPrice * (1 + long_take_profit_percent)
        elif __switch__ == 'ATR':
            __block_result_4__ = entryPrice + long_take_profit_atr_multiplier * entry_atr
        elif __switch__ == 'RR':
            __block_result_4__ = entryPrice + long_risk_reward_ratio * math.abs(entryPrice - get_long_stop_loss_price(entryPrice))
        else:
            __block_result_4__ = na
        return __block_result_4__

    __block_result_5__ = na
    if strategy.position_size > 0 and (not long_trailing_tp_executed):
        __block_result_5__ = get_long_take_profit_price(strategy.opentrades.entry_price(0))
    else:
        __block_result_5__ = na
    long_take_profit_price = __block_result_5__

    __block_result_6__ = na
    if strategy.position_size > 0:
        __block_result_6__ = long_trailing_tp_executed[1] or (not na(long_take_profit_price) and high >= long_take_profit_price)
    else:
        __block_result_6__ = False
    long_trailing_tp_executed = __block_result_6__

    __block_result_7__ = na
    __switch__ = deviation_method
    if __switch__ == 'PERC':
        __block_result_7__ = na if na(long_take_profit_price) else long_take_profit_price * deviation_percent / syminfo.mintick
    elif __switch__ == 'ATR':
        __block_result_7__ = deviation_atr_multiplier * entry_atr / syminfo.mintick
    else:
        __block_result_7__ = na
    long_trailing_tp_step_ticks = __block_result_7__

    short_take_profit_price: Persistent[float] = na(float)

    def get_short_take_profit_price(entryPrice):
        __block_result_8__ = na
        __switch__ = take_profit_method
        if __switch__ == 'PERC':
            __block_result_8__ = entryPrice * (1 - short_take_profit_percent)
        elif __switch__ == 'ATR':
            __block_result_8__ = entryPrice - short_take_profit_atr_multiplier * entry_atr
        elif __switch__ == 'RR':
            __block_result_8__ = entryPrice - short_risk_reward_ratio * math.abs(get_short_stop_loss_price(entryPrice) - entryPrice)
        else:
            __block_result_8__ = na
        return __block_result_8__

    __block_result_9__ = na
    if strategy.position_size < 0 and (not short_trailing_tp_executed):
        __block_result_9__ = get_short_take_profit_price(strategy.opentrades.entry_price(0))
    else:
        __block_result_9__ = na
    short_take_profit_price = __block_result_9__

    __block_result_10__ = na
    if strategy.position_size < 0:
        __block_result_10__ = short_trailing_tp_executed[1] or (not na(short_take_profit_price) and low <= short_take_profit_price)
    else:
        __block_result_10__ = False
    short_trailing_tp_executed = __block_result_10__

    __block_result_11__ = na
    __switch__ = deviation_method
    if __switch__ == 'PERC':
        __block_result_11__ = na if na(short_take_profit_price) else short_take_profit_price * deviation_percent / syminfo.mintick
    elif __switch__ == 'ATR':
        __block_result_11__ = deviation_atr_multiplier * entry_atr / syminfo.mintick
    else:
        __block_result_11__ = na
    short_trailing_tp_step_ticks = __block_result_11__

    plot_average_supertrend = plot(average_supertrend, color=color.new(color.green, 25) if average_supertrend > average_supertrend[1] else color.new(color.red, 25), title='Average Supertrend', linewidth=1)
    plot_smoothed_supertrend = plot(smoothed_supertrend, linewidth=2, color=color.new(color.green, 0) if smoothed_supertrend > smoothed_supertrend[1] else color.new(color.red, 0), title='Smoothed Supertrend')
    fill(plot_average_supertrend, plot_smoothed_supertrend, color=color.new(color.green, 75) if average_supertrend > smoothed_supertrend else color.new(color.red, 75), title='Supertrend Fill')

    plot(ama_midline, title='AMA Midline', linewidth=3, color=color.new(color.lime, 25) if ama_midline > ama_midline[1] else color.new(color.red, 25))
    ph6 = plot(ama_h6, title='AMA H6', color=color.new(color.green, 75))
    ph5 = plot(ama_h5, title='AMA H5', color=color.new(color.green, 75))
    ph4 = plot(ama_h4, title='AMA H4', color=color.new(color.green, 75))
    ph3 = plot(ama_h3, title='AMA H3', color=color.new(color.green, 75))
    ph2 = plot(ama_h2, title='AMA H2', color=color.new(color.green, 75))
    ph1 = plot(ama_h1, title='AMA H1', color=color.new(color.green, 75))
    pl1 = plot(ama_l6, title='AMA L6', color=color.new(color.red, 75))
    pl2 = plot(ama_l5, title='AMA L5', color=color.new(color.red, 75))
    pl3 = plot(ama_l4, title='AMA L4', color=color.new(color.red, 75))
    pl4 = plot(ama_l3, title='AMA L3', color=color.new(color.red, 75))
    pl5 = plot(ama_l2, title='AMA L2', color=color.new(color.red, 75))
    pl6 = plot(ama_l1, title='AMA L1', color=color.new(color.red, 75))

    fill(ph6, ph5, color=color.new(color.lime, 80))
    fill(pl6, pl5, color=color.new(color.red, 80))
    fill(ph5, ph4, color=color.new(color.lime, 85))
    fill(pl5, pl4, color=color.new(color.red, 85))
    fill(ph4, ph3, color=color.new(color.lime, 90))
    fill(pl4, pl3, color=color.new(color.red, 90))
    fill(ph3, ph2, color=color.new(color.lime, 95))
    fill(pl3, pl2, color=color.new(color.red, 95))
    fill(ph2, ph1, color=color.new(color.lime, 98))
    fill(pl2, pl1, color=color.new(color.red, 98))

    plotshape(long_entry_condition, title='BUY Signal', location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), text='BUY', textcolor=color.new(color.white, 0))
    plotshape(short_entry_condition, title='SELL Signal', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), text='SELL', textcolor=color.new(color.white, 0))

    if long_entry_condition and strategy.opentrades == 0:
        strategy.entry('L', strategy.long, comment='Long Entry')

    if short_entry_condition and strategy.opentrades == 0:
        strategy.entry('S', strategy.short, comment='Short Entry')

    if long_exit_condition and strategy.position_size > 0:
        strategy.close('L', comment='Exit Long (Supertrend Cross)')

    if short_exit_condition and strategy.position_size < 0:
        strategy.close('S', comment='Exit Short (Supertrend Cross)')

    if strategy.position_size > 0:
        strategy.exit('L Exit', from_entry='L', stop=long_stop_loss_price, limit=long_take_profit_price, qty_percent=take_profit_quantity_percent, trail_price=long_take_profit_price if trailing_take_profit_enabled else na, trail_offset=long_trailing_tp_step_ticks if trailing_take_profit_enabled else na)

    if strategy.position_size < 0:
        strategy.exit('S Exit', from_entry='S', stop=short_stop_loss_price, limit=short_take_profit_price, qty_percent=take_profit_quantity_percent, trail_price=short_take_profit_price if trailing_take_profit_enabled else na, trail_offset=short_trailing_tp_step_ticks if trailing_take_profit_enabled else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
