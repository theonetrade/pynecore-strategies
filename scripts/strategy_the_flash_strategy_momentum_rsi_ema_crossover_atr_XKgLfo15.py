"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, input, math, na, nz, plot, script, strategy, ta, time,
    timestamp
)
from pynecore.types import Series

group_mom_rsi: str = 'Rsi Of Momentum '
group_supertrend: str = 'SuperTrend indicator'
group_most: str = 'Ema indicator'
group_strategy: str = 'Settings of Strategy'
group_line: str = 'Line Settings'


@script.strategy('The Flash-Strategy (Momentum-RSI, EMA-crossover, ATR)', shorttitle='The Flash-Strategy (Momentum-RSI, EMA-crossover, ATR)', overlay=True, initial_capital=1000, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    len=input.int(10, minval=1, title='Length Mom-Rsi', group=group_mom_rsi, tooltip='This ind calculate Rsi value of Momentum we use this ind to determine power of trend'),
    mom_rsi_val=input.int(60, minval=1, title='Mom-Rsi Limit Val', group=group_mom_rsi, tooltip='When our Mom-Rsi value more then this we open LONG or Short, with help of this indicator we we determine the status of the trend'),
    atrPeriod=input(10, 'ATR Length SuperTrend', group=group_supertrend),
    factor=input.float(3.0, 'Factor SuperTrend', step=0.01, group=group_supertrend),
    src: Series[float] = input(close, 'Source Ema Ind', group=group_most),
    AP2=input.int(defval=12, title='Length Ema Ind', minval=1, group=group_most),
    __input_6__=input.float(defval=1, title='Percent Ema Ind', minval=0.1, group=group_most),
    Start_Time=input.time(defval=timestamp('01 January 2000 13:30 +0000'), title='Start Time of BackTest', group=group_strategy),
    End_Time=input.time(defval=timestamp('30 April 2030 19:30 +0000'), title='End Time of BackTest', group=group_strategy),
    dollar=input.float(title='Dollar Cost Per Position* ', defval=1000, group=group_strategy),
    trade_direction=input.string(title='Trade_direction', group=group_strategy, options=('LONG', 'SHORT', 'BOTH'), defval='BOTH'),
    v1=input(True, title='Version 1 - Uses SL/TP Dynamically ', group=group_strategy, tooltip='With this settings our stoploss price increase or decrease with price to get better PNL score'),
    v2=input(False, title='Version 2 -  Uses SL/TP Statically', group=group_strategy),
    __input_13__=input.float(5, title='Static Stop.Loss % Val', minval=0.01, group=group_strategy),
    __input_14__=input.float(10, title='Static Take.Prof % Val', minval=0.01, group=group_strategy),
    show_sl_tp=input.bool(title='  Show StopLoss - TakeProf Lines', inline='1', defval=True, group=group_line),
    show_trend_line=input.bool(title='  Show Trend Line', inline='3', defval=True, group=group_line),
    stoploss_colour=input.color(title='StopLoss Line Colour', inline='2', defval=color.rgb(255, 255, 0), group=group_line),
    up_trend_line_colour=input.color(title='Up Trend line Colour', inline='4', defval=color.rgb(0, 255, 0, 30), group=group_line),
    down_trend_line_colour=input.color(title='Down Trend line Colour', inline='4', defval=color.rgb(255, 0, 0, 30), group=group_line)
):
    src2: Series = close
    mom = src2 - src2[len]
    rsi_mom = ta.rsi(mom, len)
    supertrend, direction = ta.supertrend(factor, atrPeriod)
    Trail1: Series = ta.ema(src, AP2)
    AF2 = __input_6__ / 100
    SL2 = Trail1 * AF2
    Trail2: Series[float] = 0.0
    iff_1 = Trail1 - SL2 if Trail1 > nz(Trail2[1], 0) else Trail1 + SL2
    iff_2 = math.min(nz(Trail2[1], 0), Trail1 + SL2) if Trail1 < nz(Trail2[1], 0) and Trail1[1] < nz(Trail2[1], 0) else iff_1
    Trail2 = math.max(nz(Trail2[1], 0), Trail1 - SL2) if Trail1 > nz(Trail2[1], 0) and Trail1[1] > nz(Trail2[1], 0) else iff_2
    v2stoploss_input = __input_13__ / 100
    v2takeprofit_input = __input_14__ / 100
    v2stoploss_level_long = strategy.position_avg_price * (1 - v2stoploss_input)
    v2takeprofit_level_long = strategy.position_avg_price * (1 + v2takeprofit_input)
    v2stoploss_level_short = strategy.position_avg_price * (1 + v2stoploss_input)
    v2takeprofit_level_short = strategy.position_avg_price * (1 - v2takeprofit_input)
    plot(supertrend, color=stoploss_colour if show_sl_tp and v1 else na, style=plot.style_steplinebr, linewidth=2)
    plot(v2stoploss_level_long, color=stoploss_colour if strategy.position_size > 0 and show_sl_tp and v2 else na, style=plot.style_steplinebr, linewidth=2)
    plot(v2stoploss_level_short, color=stoploss_colour if strategy.position_size < 0 and show_sl_tp and v2 else na, style=plot.style_steplinebr, linewidth=2)
    plot(v2takeprofit_level_long, color=up_trend_line_colour if strategy.position_size > 0 and show_sl_tp and v2 else na, style=plot.style_steplinebr, linewidth=2)
    plot(v2takeprofit_level_short, color=up_trend_line_colour if strategy.position_size < 0 and show_sl_tp and v2 else na, style=plot.style_steplinebr, linewidth=2)
    TS2 = plot(Trail2, 'Ema Strategy', style=plot.style_line, color=down_trend_line_colour if show_trend_line and Trail1 < Trail2 else up_trend_line_colour if show_trend_line else na, linewidth=2)
    Time_interval = time > Start_Time and time < End_Time
    buy_signal = Trail1 > Trail2 and direction < 0 and (rsi_mom > mom_rsi_val) and Time_interval
    sell_signal = Trail1 < Trail2 and direction > 0 and (rsi_mom > mom_rsi_val) and Time_interval
    if strategy.opentrades == 0 and buy_signal and (trade_direction == 'LONG' or trade_direction == 'BOTH'):
        strategy.entry('Long_0', strategy.long, qty=dollar / close)
    if strategy.opentrades == 0 and sell_signal and (trade_direction == 'SHORT' or trade_direction == 'BOTH'):
        strategy.entry('Short_0', strategy.short, qty=dollar / close)
    if close < supertrend and v1:
        strategy.exit('Long_Close', from_entry='Long_0', stop=supertrend, qty_percent=100)
    if v2 and strategy.position_size > 0:
        strategy.exit('Long_Close', from_entry='Long_0', stop=v2stoploss_level_long, limit=v2takeprofit_level_long, qty_percent=100)
    if close > supertrend and v1:
        strategy.exit('Short_Close', from_entry='Short_0', stop=supertrend, qty_percent=100)
    if v2 and strategy.position_size < 0:
        strategy.exit('Short_Close', from_entry='Short_0', stop=v2stoploss_level_short, limit=v2takeprofit_level_short, qty_percent=100)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)