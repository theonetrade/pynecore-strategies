"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    bar_index, bgcolor, close, color, fill, high, input, low, na, plot,
    script, strategy, ta, timestamp
)
from pynecore.types import Persistent, PersistentSeries, Series

group_ema: str = 'EMA'
group_stoch: str = 'Stochastic RSI'
group_atr: str = 'ATR Stoploss Finder'


@script.strategy('2 EMA + Stoch RSI + ATR [Pt]', shorttitle='2EMA+Stoch+ATR', overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, calc_on_order_fills=False, max_bars_back=500, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    startY=input(title='Start Year', defval=2011, group='Backtesting window'),
    startM=input.int(title='Start Month', defval=1, minval=1, maxval=12, group='Backtesting window'),
    startD=input.int(title='Start Day', defval=1, minval=1, maxval=31, group='Backtesting window'),
    finishY=input(title='Finish Year', defval=2050, group='Backtesting window'),
    finishM=input.int(title='Finish Month', defval=12, minval=1, maxval=12, group='Backtesting window'),
    finishD=input.int(title='Finish Day', defval=31, minval=1, maxval=31, group='Backtesting window'),
    ema1_len=input.int(50, 'EMA Length 1', group=group_ema),
    ema2_len=input.int(200, 'EMA Length 2', group=group_ema),
    smoothK=input.int(3, 'K', minval=1, group=group_stoch),
    smoothD=input.int(3, 'D', minval=1, group=group_stoch),
    lengthRSI=input.int(14, 'RSI Length', minval=1, group=group_stoch),
    lengthStoch=input.int(14, 'Stochastic Length', minval=1, group=group_stoch),
    length=input.int(title='Length', defval=14, minval=1, group=group_atr),
    smoothing=input.string(title='Smoothing', defval='EMA', options=('RMA', 'SMA', 'EMA', 'WMA'), group=group_atr),
    m=input.float(0.7, 'Multiplier', step=0.1, group=group_atr),
    src1: Series[float] = input(high, 'Source for upper band', group=group_atr),
    src2: Series[float] = input(low, 'Source for lower band', group=group_atr),
    showatr=input.bool(True, 'Show ATR Bands', group=group_atr),
    collong=input.color(color.purple, 'Long ATR SL', inline='1', group=group_atr),
    colshort=input.color(color.purple, 'Short ATR SL', inline='2', group=group_atr),
    RR=input.float(2.0, 'Reward to Risk ratio (X times SL)', step=0.1, group='Profit Target'),
    breakeven=input.bool(True, 'Move SL to breakeven when RR hit', group='Profit Target', inline='breakenven'),
    be_RR=input.float(1.0, '', inline='breakeven', group='Profit Target')
):
    timestart = timestamp(startY, startM, startD, 0, 0)
    timefinish = timestamp(finishY, finishM, finishD, 23, 59)
    ema1 = ta.ema(close, ema1_len)
    ema2 = ta.ema(close, ema2_len)
    plot(ema1, 'ema1', color.white, linewidth=2)
    plot(ema2, 'ema2', color.orange, linewidth=2)
    ema_bull = ema1 > ema2
    ema_bear = ema1 < ema2
    src = close
    rsi1 = ta.rsi(src, lengthRSI)
    k = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
    d = ta.sma(k, smoothD)
    trigger_stoch_OB: Persistent = k > 80
    trigger_stoch_OS: Persistent = k < 20
    stoch_crossdown = ta.crossunder(k, d)
    stoch_crossup = ta.crossover(k, d)
    P_hi = ta.pivothigh(k, 1, 1)
    P_lo = ta.pivotlow(k, 1, 1)
    previous_high = ta.valuewhen(cast_bool(P_hi), k, 1)
    previous_low = ta.valuewhen(cast_bool(P_lo), k, 1)
    recent_high = ta.valuewhen(cast_bool(P_hi), k, 0)
    recent_low = ta.valuewhen(cast_bool(P_lo), k, 0)
    def ma_function(source, length):
        __block_result__ = na
        if smoothing == 'RMA':
            __block_result__ = ta.rma(source, length)
        else:
            __block_result_1__ = na
            if smoothing == 'SMA':
                __block_result_1__ = ta.sma(source, length)
            else:
                __block_result_2__ = na
                if smoothing == 'EMA':
                    __block_result_2__ = ta.ema(source, length)
                else:
                    __block_result_2__ = ta.wma(source, length)
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    a = ma_function(ta.tr(True), length) * m
    up = ma_function(ta.tr(True), length) * m + src1
    down = src2 - ma_function(ta.tr(True), length) * m
    p1 = plot(up if showatr else na, title='ATR Short Stop Loss', color=colshort)
    p2 = plot(down if showatr else na, title='ATR Long Stop Loss', color=collong)
    L_PT: PersistentSeries[float] = 0.0
    S_PT: PersistentSeries[float] = 0.0
    L_SL: PersistentSeries[float] = 0.0
    S_SL: PersistentSeries[float] = 0.0
    L_be_PT: PersistentSeries[float] = 0.0
    S_be_PT: PersistentSeries[float] = 0.0
    BSLE = ta.barssince(strategy.opentrades.entry_bar_index(0) == bar_index)
    entry_price = strategy.opentrades.entry_price(0) if strategy.position_size != 0 else na
    if strategy.position_size > 0:
        L_PT = L_PT[1]
        L_SL = entry_price if breakeven and high >= L_be_PT else L_SL[1]
        S_PT = close - (up - close) * RR
        S_SL = up
        L_be_PT = L_be_PT[1]
        S_be_PT = close - (up - close) * be_RR
    elif strategy.position_size < 0:
        S_PT = S_PT[1]
        S_SL = entry_price if breakeven and low <= S_be_PT else S_SL[1]
        L_PT = close + (close - down) * RR
        L_SL = down
        S_be_PT = S_be_PT[1]
        L_be_PT = close + (close - down) * be_RR
    elif strategy.position_size != 0:
        L_PT = L_PT[1]
        S_PT = S_PT[1]
    else:
        L_PT = close + (close - down) * RR
        L_SL = down
        S_PT = close - (up - close) * RR
        S_SL = up
        L_be_PT = close + (close - down) * be_RR
        S_be_PT = close - (up - close) * be_RR
    entry_line = plot(entry_price, 'Entry Price', color.white, linewidth=1, style=plot.style_linebr)
    L_PT_line = plot(L_PT if strategy.position_size > 0 and BSLE > 0 else na, 'L PT', color.green, linewidth=2, style=plot.style_linebr)
    S_PT_line = plot(S_PT if strategy.position_size < 0 and BSLE > 0 else na, 'S PT', color.green, linewidth=2, style=plot.style_linebr)
    L_SL_line = plot(L_SL if strategy.position_size > 0 and BSLE > 0 else na, 'L SL', color.red, linewidth=2, style=plot.style_linebr)
    S_SL_line = plot(S_SL if strategy.position_size < 0 and BSLE > 0 else na, 'S SL', color.red, linewidth=2, style=plot.style_linebr)
    L_be_PT_line = plot(L_be_PT if strategy.position_size > 0 and BSLE > 0 else na, 'L BE PT', color.blue, linewidth=2, style=plot.style_linebr)
    S_be_PT_line = plot(S_be_PT if strategy.position_size < 0 and BSLE > 0 else na, 'S BE PT', color.blue, linewidth=2, style=plot.style_linebr)
    fill(L_PT_line, entry_line, color=color.new(color.green, 90))
    fill(S_PT_line, entry_line, color=color.new(color.green, 90))
    fill(L_SL_line, entry_line, color=color.new(color.red, 90))
    fill(S_SL_line, entry_line, color=color.new(color.red, 90))
    L_entry_trigger1: PersistentSeries[bool] = False
    S_entry_trigger1: PersistentSeries[bool] = False
    L_entry_trigger1 = ema_bull and close < ema1 and (k < 20) and (strategy.position_size == 0)
    S_entry_trigger1 = ema_bear and close > ema1 and (k > 80) and (strategy.position_size == 0)
    L_entry1 = L_entry_trigger1[1] and stoch_crossup and (recent_low > previous_low)
    S_entry1 = S_entry_trigger1[1] and stoch_crossdown and (recent_high < previous_high)
    plot(1 if L_entry_trigger1[1] else 0, 'L Entry Trigger')
    plot(1 if stoch_crossup else 0, 'Stoch Cross Up')
    plot(1 if recent_low > previous_low else 0, 'Higher low')
    plot(1 if S_entry_trigger1[1] else 0, 'S Entry Trigger')
    plot(1 if stoch_crossdown else 0, 'Stoch Cross down')
    plot(1 if recent_high < previous_high else 0, 'Lower high')
    if L_entry1:
        strategy.entry('Long', strategy.long)
    if S_entry1:
        strategy.entry('Short', strategy.short)
    strategy.exit('Exit Long', 'Long', limit=L_PT, stop=L_SL, comment_profit='Exit Long, PT hit', comment_loss='Exit Long, SL hit')
    strategy.exit('Exit Short', 'Short', limit=S_PT, stop=S_SL, comment_profit='Exit Short, PT hit', comment_loss='Exit Short, SL hit')
    L_entry_trigger1 = (False if L_entry1 or ema_bear or S_entry1 else True) if L_entry_trigger1[1] else L_entry_trigger1
    S_entry_trigger1 = (False if S_entry1 or ema_bull or L_entry1 else True) if S_entry_trigger1[1] else S_entry_trigger1
    bgcolor(color.new(color.green, 90) if L_entry_trigger1 else na)
    bgcolor(color.new(color.red, 90) if S_entry_trigger1 else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)