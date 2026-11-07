"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, close, color, fill, high, input, low, math, na, nz, open, plot,
    script, strategy, syminfo, ta
)
from pynecore.types import IBPersistent, NA, Series


@script.strategy(title='Twin Range Filter Algo v.3', shorttitle='Twin Range Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    source: Series[float] = input(defval=close, title='Source'),
    per1=input.int(defval=27, minval=1, title='Fast period', group='Twin Range Filter @colinmck'),
    mult1=input.float(defval=1.6, minval=0.1, title='Fast range', group='Twin Range Filter @colinmck'),
    per2=input.int(defval=55, minval=1, title='Slow period', group='Twin Range Filter @colinmck'),
    mult2=input.float(defval=2, minval=0.1, title='Slow range', group='Twin Range Filter @colinmck'),
    Separator=input.bool(title='Following conditions and backtest algorithm are added by @greenmask9 🎯, original script is written by @colinmck 👍. Read both of their\'s release notes for more info on how this script works.', defval=False, group='Greenmask\'s testing resources & ATR condition'),
    disabler=input.bool(title='Disable @greenmask9\'s ATR conditions', defval=False, group='Greenmask\'s testing resources & ATR condition'),
    l2=input.int(title='ATR1', defval=32, minval=1, group='ATR condition', tooltip='C: Short-range volatility must be low than long-term volatility measurement for the entry.'),
    s2=input.string(title='Smoothing', defval='SMA', options=('RMA', 'SMA', 'EMA', 'WMA'), tooltip='C: Short-range volatility must be low than long-term volatility measurement for the entry.', group='ATR condition'),
    l3=input.int(title='ATR2', defval=64, minval=1, group='ATR condition', tooltip='C: Short-range volatility must be low than long-term volatility measurement for the entry.'),
    s3=input.string(title='Smoothing', defval='RMA', options=('RMA', 'SMA', 'EMA', 'WMA'), tooltip='C: Short-range volatility must be low than long-term volatility measurement for the entry.', group='ATR condition'),
    maxcandles_till_close=input.int(title='Time-based Close', defval=17, group='Alternative Exit'),
    i_time=input.bool(True, 'Enable Time Base Close', group='Alternative Exit'),
    i_sl_type=input.string('Low - (close - lowest low[len]) * %', options=('Low - (ATR[len] * %)', 'Low - (close - lowest low[len]) * %', 'Low - (close - average low[len]) * %', 'Close - (ATR[len] * %)', 'Low - TicksNumber'), title='Calculation (Long)', group='Stop-loss', tooltip='This is a stop-loss calculation for long positions. Reversed logic is used for short stop-loss. *Calculation Low - TicksNumber doesn\'t use Percentage-based multiplier. **Number of ticks is always substracted (added) after the initial calculation. '),
    i_sl_atr=input.int(10, 'Calculation Length', group='Stop-loss'),
    __input_15__=input.float(80, 'Percentage', group='Stop-loss'),
    __input_16__=input.int(defval=10, minval=1, title='Number of ticks', group='Stop-loss'),
    i_stoploss=input.bool(True, 'Enable Stop-loss', group='Stop-loss'),
    i_tr_type=input.string('Close + (ATR[len] * %)', options=('High + (ATR[len] * %)', 'Close + (ATR[len] * %)', 'Close + abs(close - highest high[len]) * %', 'Close + abs(close - average high[len]) * %', 'High + TicksNumber', 'Close + TicksNumber'), title='Calculation (Long)', group='Target', tooltip='Raw number of ticks is always added to the target.'),
    i_tr_atr=input.int(10, 'Calculation Length', group='Target'),
    __input_20__=input.float(500, 'Percentage', group='Target'),
    __input_21__=input.int(defval=10, minval=1, title='Number of ticks', group='Target'),
    i_target=input.bool(True, 'Enable Target', group='Target'),
    i_message_long=input.string('Long entry default message: x', 'Long Entry Alert Message', group='Alert'),
    i_long_alert=input.bool(True, 'Enable Long Alert', group='Alert'),
    i_message_short=input.string('Long entry default message: x', 'Short Entry Alert Message', group='Alert'),
    i_short_alert=input.bool(True, 'Enable Short Alert', group='Alert')
):
    def smoothrng(x: Series, t, m):
        wper = t * 2 - 1
        avrng = ta.ema(math.abs(x - x[1]), t)
        smoothrng__0000000b__ = ta.ema(avrng, wper) * m
        return smoothrng__0000000b__

    smrng1 = smoothrng(source, per1, mult1)
    smrng2 = smoothrng(source, per2, mult2)
    smrng = (smrng1 + smrng2) / 2
    def rngfilt(x, r):
        rngfilt__00000018__: Series = x
        rngfilt__00000018__ = (nz(rngfilt__00000018__[1]) if x - r < nz(rngfilt__00000018__[1]) else x - r) if x > nz(rngfilt__00000018__[1]) else nz(rngfilt__00000018__[1]) if x + r > nz(rngfilt__00000018__[1]) else x + r
        return rngfilt__00000018__

    filt: Series = rngfilt(source, smrng)
    upward: Series[float] = 0.0
    upward = nz(upward[1]) + 1 if filt > filt[1] else 0 if filt < filt[1] else nz(upward[1])
    downward: Series[float] = 0.0
    downward = nz(downward[1]) + 1 if filt < filt[1] else 0 if filt > filt[1] else nz(downward[1])
    hband = filt + smrng
    lband = filt - smrng
    longCond = NA(bool)
    shortCond = NA(bool)
    longCond = source > filt and source > source[1] and (upward > 0) or (source > filt and source < source[1] and (upward > 0))
    shortCond = source < filt and source < source[1] and (downward > 0) or (source < filt and source > source[1] and (downward > 0))
    CondIni: Series[int] = 0
    CondIni = 1 if longCond else -1 if shortCond else CondIni[1]
    long = longCond and CondIni[1] == -1
    short = shortCond and CondIni[1] == 1
    def atr2(source, l2):
        __block_result__ = na
        if s2 == 'SMA':
            __block_result__ = ta.sma(source, l2)
        else:
            __block_result_1__ = na
            if s2 == 'RMA':
                __block_result_1__ = ta.rma(source, l2)
            else:
                __block_result_2__ = na
                if s2 == 'EMA':
                    __block_result_2__ = ta.ema(source, l2)
                else:
                    __block_result_2__ = ta.wma(source, l2)
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    def atr3(source, l3):
        __block_result_3__ = na
        if s3 == 'RMA':
            __block_result_3__ = ta.rma(source, l3)
        else:
            __block_result_4__ = na
            if s3 == 'SMA':
                __block_result_4__ = ta.sma(source, l3)
            else:
                __block_result_5__ = na
                if s3 == 'EMA':
                    __block_result_5__ = ta.ema(source, l3)
                else:
                    __block_result_5__ = ta.wma(source, l3)
                __block_result_4__ = __block_result_5__
            __block_result_3__ = __block_result_4__
        return __block_result_3__

    atr20 = atr2(ta.tr(True), l2)
    atr30 = atr3(ta.tr(True), l3)
    ordersize = math.floor(strategy.initial_capital / close)
    stop_long: IBPersistent[float] = 0.0
    entry: IBPersistent[float] = 0.0
    stop_short: IBPersistent[float] = 0.0
    i_sl_perc = __input_15__ / 100
    i_sl_ticks = __input_16__ * syminfo.mintick
    def f_stop_long(calculation, length, mult, ticks):
        stop_0 = low - ta.atr(length) * mult - ticks if calculation == 'Low - (ATR[len] * %)' else low - (close - ta.lowest(low, length)) * mult - ticks if calculation == 'Low - (close - lowest low[len]) * %' else low - (close - ta.sma(low, length)) * mult - ticks if calculation == 'Low - (close - average low[len]) * %' else close - ta.atr(length) * mult - ticks if calculation == 'Close - (ATR[len] * %)' else low - ticks
        return stop_0

    def f_stop_short(calculation, length, mult, ticks):
        stop_0 = high + ta.atr(length) * mult + ticks if calculation == 'Low - (ATR[len] * %)' else high + math.abs(close - ta.lowest(high, length)) * mult + ticks if calculation == 'Low - (close - lowest low[len]) * %' else high + math.abs(close - ta.sma(high, length)) * mult + ticks if calculation == 'Low - (close - average low[len]) * %' else close + ta.atr(length) * mult + ticks if calculation == 'Close - (ATR[len] * %)' else high + ticks
        return stop_0

    target_long: IBPersistent[float] = 0.0
    target_short: IBPersistent[float] = 0.0
    i_tr_perc = __input_20__ / 100
    i_tr_ticks = __input_21__ * syminfo.mintick
    def f_target_long(calculation, length, mult, ticks):
        stop_0 = high + ta.atr(length) * mult + ticks if calculation == 'High + (ATR[len] * %)' else close + ta.atr(length) * mult + ticks if calculation == 'Close + (ATR[len] * %)' else close + math.abs(close - ta.highest(high, length)) * mult + ticks if calculation == 'Close + abs(close - highest high[len]) * %' else close + math.abs(close - ta.sma(high, length)) * mult + ticks if calculation == 'Close + abs(close - average high[len]) * %' else high + ticks if calculation == 'High + TicksNumber' else close + ticks
        return stop_0

    def f_target_short(calculation, length, mult, ticks):
        stop_0 = low - ta.atr(length) * mult - ticks if calculation == 'High + (ATR[len] * %)' else close - ta.atr(length) * mult - ticks if calculation == 'Close + (ATR[len] * %)' else close - math.abs(close - ta.lowest(low, length)) * mult - ticks if calculation == 'Close + abs(close - highest high[len]) * %' else close - math.abs(close - ta.sma(low, length)) * mult - ticks if calculation == 'Close + abs(close - average high[len]) * %' else low - ticks if calculation == 'High + TicksNumber' else close - ticks
        return stop_0

    if strategy.position_size >= 0 or strategy.position_size[1] != strategy.position_size:
        stop_short = f_stop_short(i_sl_type, i_sl_atr, i_sl_perc, i_sl_ticks) if i_stoploss else na
        target_short = f_target_short(i_tr_type, i_tr_atr, i_tr_perc, i_tr_ticks) if i_target else na
    if strategy.position_size <= 0 or strategy.position_size[1] != strategy.position_size:
        stop_long = f_stop_long(i_sl_type, i_sl_atr, i_sl_perc, i_sl_ticks) if i_stoploss else na
        target_long = f_target_long(i_tr_type, i_tr_atr, i_tr_perc, i_tr_ticks) if i_target else na
    if strategy.position_size == 0 or strategy.position_size[1] != strategy.position_size:
        entry = open
    bull = long and (atr20 < atr30 or disabler)
    bear = short and (atr20 < atr30 or disabler)
    bullclock = ta.barssince(bull)
    bearclock = ta.barssince(bear)
    if bull:
        strategy.entry('Twin Long', strategy.long, ordersize)
    strategy.exit('Exit', from_entry='Twin Long', limit=target_long, stop=stop_long)
    if bear:
        strategy.entry('Twin Short', strategy.short, ordersize)
    strategy.exit('Exit', from_entry='Twin Short', limit=target_short, stop=stop_short)
    if bull and strategy.position_size[1] == 0 and i_long_alert:
        alert(i_message_long, alert.freq_once_per_bar_close)
    if bear and strategy.position_size[1] == 0 and i_short_alert:
        alert(i_message_short, alert.freq_once_per_bar_close)
    if i_time:
        if bullclock == maxcandles_till_close:
            strategy.close('Twin Long', comment='Time')
        if bearclock == maxcandles_till_close:
            strategy.close('Twin Short', comment='Time')
    c_fill_stop = color.new(color.red, 90)
    c_fill_target = color.new(color.green, 90)
    p_longstop = plot(stop_long if strategy.position_size > 0 and i_stoploss else na, linewidth=2, color=color.new(color.red, 0), style=plot.style_linebr)
    p_shortstop = plot(stop_short if strategy.position_size < 0 and i_stoploss else na, linewidth=2, color=color.new(color.red, 0), style=plot.style_linebr)
    p_entry = plot(entry if strategy.position_size != 0 else na, linewidth=2, color=color.new(color.blue, 0), style=plot.style_linebr)
    p_longtarget = plot(target_long if strategy.position_size > 0 and i_target else na, linewidth=2, color=color.new(color.green, 0), style=plot.style_linebr)
    p_shorttarget = plot(target_short if strategy.position_size < 0 and i_target else na, linewidth=2, color=color.new(color.green, 0), style=plot.style_linebr)
    fill(p_entry, p_longstop, c_fill_stop)
    fill(p_entry, p_shortstop, c_fill_stop)
    fill(p_entry, p_longtarget, c_fill_target)
    fill(p_entry, p_shorttarget, c_fill_target)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
