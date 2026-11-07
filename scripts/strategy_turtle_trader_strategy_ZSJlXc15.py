"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, fill, high, input, label, location, low, na,
    plot, plotchar, script, size, strategy, syminfo, ta, time, timestamp
)
from pynecore.types import Persistent, Series

t1: str = 'Percentage of the account the trader is willing to lose. This percentage is used to define the position size based on previous gains or losses. Turtle traders default to 1%.'
t2: str = 'ATR Length'
t3: str = 'ATR Multiplier to fix the Stop Loss'
t4: str = 'Pyramiding : ATR Multiplier to set a profit target to increase position size'
t5: str = 'System 1 enter long if there is a new high after this selected period of time'
t6: str = 'System 2 enter long if there is a new high after this selected period of time'
t7: str = 'Exit Long from system 1 if there is a new low after this selected period of time'
t8: str = 'Exit Long from system 2 if there is a new low after this selected period of time'
t9: str = 'System 1 enter short if there is a new low after this selected period of time'
t10: str = 'System 2 enter short if there is a new low after this selected period of time'
t11: str = 'Exit short from system 1 if there is a new high after this selected period of time'
t12: str = 'Exit short from system 2 if there is a new high after this selected period of time'


@script.strategy('TURTLE STRATEGY', precision=2, overlay=True, initial_capital=1000, commission_type=strategy.commission.percent, commission_value=0.18, slippage=3, pyramiding=5, close_entries_rule='ANY', margin_long=100, margin_short=100, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    percentage_to_risk=input.float(1, 'Risk % of capital', maxval=100, minval=0, group='Turtle Parameters', tooltip=t1),
    atr_period=input.int(20, 'ATR period', minval=1, group='Turtle Parameters', tooltip=t2),
    stop_N_multiplier=input.float(1.5, 'Stop ATR', minval=0.1, group='Turtle Parameters', tooltip=t3),
    pyramid_profit=input.float(0.5, 'Pyramid Profit', minval=0.01, group='Turtle Parameters', tooltip=t4),
    S1_long=input.int(20, 'S1 Long', minval=1, group='Turtle Parameters', tooltip=t5),
    S2_long=input.int(55, 'S2 Long', minval=1, group='Turtle Parameters', tooltip=t6),
    S1_long_exit=input.int(10, 'S1 Long Exit', minval=1, group='Turtle Parameters', tooltip=t7),
    S2_long_exit=input.int(20, 'S2 Long Exit', minval=1, group='Turtle Parameters', tooltip=t8),
    S1_short=input.int(15, 'S1 Short', minval=1, group='Turtle Parameters', tooltip=t9),
    S2_short=input.int(55, 'S2 Short', minval=1, group='Turtle Parameters', tooltip=t10),
    S1_short_exit=input.int(7, 'S1 Short Exit', minval=1, group='Turtle Parameters', tooltip=t11),
    S2_short_exit=input.int(20, 'S2 Short Exit', minval=1, group='Turtle Parameters', tooltip=t12),
    startDate=input.time(title='Start Date', defval=timestamp('1 Jan 2020 00:00:00'), group='Backtesting Period'),
    endDate=input.time(title='End Date', defval=timestamp('1 July 2034 00:00:00'), group='Backtesting Period')
):
    def debugLabel(txt, color__ren__):
        return label.new(bar_index, high, text=txt, color=color__ren__, style=label.style_label_lower_right, textcolor=color.black, size=size.small)

    def inBacktestPeriod(start, end):
        return time >= start and time <= end

    atr = ta.atr(atr_period)
    buy_price_long: Persistent[float] = na(float)
    buy_price_short: Persistent[float] = na(float)
    stop_loss_long: Persistent[float] = na(float)
    stop_loss_short: Persistent[float] = na(float)
    account: float = na(float)
    day_high_syst1: Series = ta.highest(high, S1_long)
    day_low_syst1: Series = ta.lowest(low, S1_short)
    day_high_syst2: Series = ta.highest(high, S2_long)
    day_low_syst2: Series = ta.lowest(low, S2_short)
    skip: Persistent[bool] = False
    unskip_buffer_long: Persistent[bool] = False
    unskip_buffer_short: Persistent[bool] = False
    exit_long_syst1: Series = ta.lowest(low, S1_long_exit)
    exit_short_syst1: Series = ta.highest(high, S1_short_exit)
    exit_long_syst2: Series = ta.lowest(low, S2_long_exit)
    exit_short_syst2: Series = ta.highest(high, S2_short_exit)
    exit_signal: float = na(float)
    inRange: bool = na(bool)
    inRange = inBacktestPeriod(startDate, endDate)
    if strategy.equity - strategy.openprofit < strategy.initial_capital:
        account = (strategy.equity - strategy.openprofit) * (strategy.equity - strategy.openprofit) / strategy.initial_capital
    else:
        account = strategy.equity - strategy.openprofit
    if strategy.position_size != 0 and (not inRange):
        strategy.close_all()
        debugLabel('END OF BACKTESTING PERIOD : we close the trade', color__ren__=color.rgb(116, 116, 116))
    if skip and high > day_high_syst1[1] and (high < day_high_syst2[1]):
        unskip_buffer_long = True
    if skip and low < day_low_syst1[1] and (low > day_low_syst2[1]):
        unskip_buffer_short = True
    if unskip_buffer_long:
        if high < day_high_syst1[1]:
            skip = False
            unskip_buffer_long = False
    if unskip_buffer_short:
        if low > day_low_syst1[1]:
            skip = False
            unskip_buffer_short = False
    if strategy.position_size != 0 and skip:
        skip = False
        unskip_buffer_long = False
        unskip_buffer_short = False
    unit = percentage_to_risk / 100 * account / atr * syminfo.pointvalue
    if not skip and (not strategy.position_size > 0) and inRange and (unit > 0):
        strategy.cancel('Long Syst 2')
        if unit * day_high_syst1 > account:
            unit = account / day_high_syst1
        stop_loss_long = day_high_syst1 - stop_N_multiplier * atr
        if stop_loss_long < day_high_syst1 * 0.9:
            stop_loss_long = day_high_syst1 * 0.9
        strategy.order('Long Syst 1', strategy.long, unit, stop=day_high_syst1)
        buy_price_long = day_high_syst1
    if skip and (not strategy.position_size > 0) and inRange and (unit > 0):
        if unit * day_high_syst2 > account:
            unit = account / day_high_syst2
        stop_loss_long = day_high_syst2 - stop_N_multiplier * atr
        if stop_loss_long < day_high_syst2 * 0.9:
            stop_loss_long = day_high_syst2 * 0.9
        strategy.order('Long Syst 2', strategy.long, unit, stop=day_high_syst2)
        buy_price_long = day_high_syst2
    if not skip and (not strategy.position_size < 0) and inRange and (unit > 0):
        strategy.cancel('Short Syst 2')
        if unit * day_low_syst1 > account:
            unit = account / day_low_syst1
        stop_loss_short = day_low_syst1 + stop_N_multiplier * atr
        if stop_loss_short > day_low_syst1 * 1.1:
            stop_loss_short = day_low_syst1 * 1.1
        strategy.order('Short Syst 1', strategy.short, unit, stop=day_low_syst1)
        buy_price_short = day_low_syst1
    if skip and (not strategy.position_size < 0) and inRange and (unit > 0):
        if unit * day_low_syst2 > account:
            unit = account / day_low_syst2
        stop_loss_short = day_low_syst2 + stop_N_multiplier * atr
        if stop_loss_short > day_low_syst2 * 1.1:
            stop_loss_short = day_low_syst2 * 1.1
        strategy.order('Short Syst 2', strategy.short, unit, stop=day_low_syst2)
        buy_price_short = day_low_syst2
    if close > buy_price_long + pyramid_profit * atr and strategy.position_size > 0:
        remaining_capital = account - strategy.position_size * strategy.position_avg_price * (1 - 0.0018)
        units_to_add = percentage_to_risk / 100 * remaining_capital / atr * syminfo.pointvalue
        if remaining_capital > units_to_add and units_to_add > 0:
            stop_loss_long = stop_loss_long + pyramid_profit * atr
            strategy.entry('Pyramid Long', strategy.long, units_to_add)
            buy_price_long = close
    if close < buy_price_short - pyramid_profit * atr and strategy.position_size < 0:
        remaining_capital = account + strategy.position_size * strategy.position_avg_price * (1 - 0.0018)
        units_to_add = percentage_to_risk / 100 * remaining_capital / atr * syminfo.pointvalue
        if remaining_capital > units_to_add and units_to_add > 0:
            stop_loss_short = stop_loss_short - pyramid_profit * atr
            strategy.entry('Pyramid Short', strategy.short, units_to_add)
            buy_price_short = close
    if strategy.opentrades.entry_id(0) == 'Long Syst 1':
        if exit_long_syst1[1] > stop_loss_long:
            exit_signal = exit_long_syst1[1]
        else:
            exit_signal = stop_loss_long
    if strategy.opentrades.entry_id(0) == 'Long Syst 2':
        if exit_long_syst2[1] > stop_loss_long:
            exit_signal = exit_long_syst2[1]
        else:
            exit_signal = stop_loss_long
    if strategy.opentrades.entry_id(0) == 'Short Syst 1':
        if exit_short_syst1[1] < stop_loss_short:
            exit_signal = exit_short_syst1[1]
        else:
            exit_signal = stop_loss_short
    if strategy.opentrades.entry_id(0) == 'Short Syst 2':
        if exit_short_syst2[1] < stop_loss_short:
            exit_signal = exit_short_syst2[1]
        else:
            exit_signal = stop_loss_short
    if strategy.position_size * exit_signal > strategy.position_size * strategy.position_avg_price * (1 - 0.0018):
        strategy.cancel('Long Syst 1')
        strategy.cancel('Short Syst 1')
        skip = True
    if strategy.position_size * exit_signal <= strategy.position_size * strategy.position_avg_price * (1 - 0.0018):
        skip = False
    if strategy.position_size > 0:
        strategy.exit('Exit Long', stop=exit_signal)
    if strategy.position_size < 0:
        strategy.exit('Exit Short', stop=exit_signal)
    plotchar(atr, 'ATR', '', location.top, color.rgb(131, 5, 83))
    plot(day_high_syst1[1], '20 day high', color.rgb(118, 217, 159))
    plot(day_high_syst2[1], '55 day high', color.rgb(4, 92, 53))
    plot(day_low_syst1[1], '20 day low', color.rgb(234, 108, 108))
    plot(day_low_syst2[1], '55 day low', color.rgb(149, 17, 17))
    plot(exit_signal, 'Exit Signal', color.blue, style=plot.style_circles)
    exit_long_syst2_plot = plot(exit_long_syst2[1], color=na)
    day_high_syst2_plot = plot(day_high_syst2[1], color=na)
    exit_short_syst2_plot = plot(exit_short_syst2[1], color=na)
    day_low_syst2_plot = plot(day_low_syst2[1], color=na)
    fill(exit_long_syst2_plot, day_high_syst2_plot, color=color.new(color.lime, 90) if strategy.position_size > 0 else na)
    fill(exit_short_syst2_plot, day_low_syst2_plot, color=color.new(color.red, 90) if strategy.position_size < 0 else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
