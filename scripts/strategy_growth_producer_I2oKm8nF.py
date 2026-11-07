"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fill, high, hlc3, input, low, math, na, nz, plot, script,
    strategy, ta, time, timestamp, volume
)
from pynecore.types import Series


@script.strategy('Growth Producer', overlay=True, initial_capital=1000, currency='USD', pyramiding=2, commission_type=strategy.commission.percent, commission_value=0.07, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, close_by_id=True)
def main(
    ribbon_period=input.int(19, 'Period', step=1),
    length=input.int(120, 'RVI period', minval=1),
    benchmark=input.float(35, 'RVI benchmark', minval=10, maxval=100, step=0.1),
    mfi_length=input.int(19, 'MFI Length', minval=1),
    mfi_lower=input.int(15, 'MFI Lower level', minval=0, maxval=50),
    mfi_upper=input.int(90, 'MFI Higher level', minval=50, maxval=100),
    Act_RSI_VWAP_long=input(True, 'RSI VOLUME WEIGHTED AVERAGE PRICE LONG'),
    RSI_VWAP_length_long=input(16, 'RSI-VWAP LENGTH LONG'),
    RSI_VWAP_overSold_long=input.float(13, 'RSI-VWAP OVERSOLD LONG'),
    RSI_VWAP_overBought_long=input.float(68, 'RSI-VWAP OVERBOUGHT LONG'),
    Act_RSI_VWAP_short=input(True, 'RSI VOLUME WEIGHTED AVERAGE PRICE SHORT'),
    RSI_VWAP_length_short=input(14, 'RSI-VWAP LENGTH SHORT'),
    RSI_VWAP_overSold_short=input.float(7, 'RSI-VWAP OVERSOLD SHORT'),
    RSI_VWAP_overBought_short=input.float(68, 'RSI-VWAP OVERBOUGHT SHORT'),
    __input_14__=input.float(3.3, title='Long Take Profit 1 %', step=0.1),
    long_tp1_qty=input.int(15, title='Long Take Profit 1 Qty', step=1),
    __input_16__=input.float(12, title='Long Take Profit 2%', step=0.1),
    long_tp2_qty=input.int(100, title='Long Take Profit 2 Qty', step=1),
    __input_18__=input.float(3.3, title='Long Stop Loss %', step=0.1),
    __input_19__=input.float(3.2, title='Short Take Profit 1 %', step=0.1),
    short_tp1_qty=input.int(20, title='Short Take Profit 1 Qty', step=1),
    __input_21__=input.float(5.5, title='Short Take Profit 2%', step=0.1),
    short_tp2_qty=input.int(100, title='Short Take Profit 2 Qty', step=1),
    __input_23__=input.float(3.2, title='Short Stop Loss %', step=0.1),
    testStartYear=input(2019, 'Backtest Start Year'),
    testStartMonth=input(1, 'Backtest Start Month'),
    testStartDay=input(1, 'Backtest Start Day'),
    testStopYear=input(2099, 'Backtest Stop Year'),
    testStopMonth=input(12, 'Backtest Stop Month'),
    testStopDay=input(31, 'Backtest Stop Day')
):
    def Atr(p):
        atr: Series[float] = 0.0
        Tr = math.max(high - low, math.max(math.abs(high - close[1]), math.abs(low - close[1])))
        atr = nz(atr[1] + (Tr - atr[1]) / p, Tr)
        return atr

    leadLine1 = ta.ema(close, ribbon_period)
    leadLine2 = ta.sma(close, ribbon_period)
    p1 = plot(leadLine1, color=color.new(color.new('#53B987'), 50), title='EMA', linewidth=1)
    p2 = plot(leadLine2, color=color.new(color.new('#EB4D5C'), 50), title='SMA', linewidth=1)
    fill(p1, p2, color=color.new('#53B987') if leadLine1 > leadLine2 else color.new('#EB4D5C'))
    src = close
    len: int = 14
    stddev = ta.stdev(src, length)
    upper = ta.ema(0 if ta.change(src) <= 0 else stddev, len)
    lower = ta.ema(0 if ta.change(src) > 0 else stddev, len)
    rvi = upper / (upper + lower) * 100
    mfi_source = hlc3
    upper_s = math.sum(volume * (0 if ta.change(mfi_source) <= 0 else mfi_source), mfi_length)
    lower_s = math.sum(volume * (0 if ta.change(mfi_source) >= 0 else mfi_source), mfi_length)
    mf = 100.0 - 100.0 / (1.0 + upper_s / lower_s)
    RSI_VWAP_long = ta.rsi(ta.vwap(close), RSI_VWAP_length_long)
    RSI_VWAP_short = ta.rsi(ta.vwap(close), RSI_VWAP_length_short)
    long_tp1_inp = __input_14__ / 100
    long_tp2_inp = __input_16__ / 100
    long_sl_inp = __input_18__ / 100
    long_take_level_1 = strategy.position_avg_price * (1 + long_tp1_inp)
    long_take_level_2 = strategy.position_avg_price * (1 + long_tp2_inp)
    long_stop_level = strategy.position_avg_price * (1 - long_sl_inp)
    short_tp1_inp = __input_19__ / 100
    short_tp2_inp = __input_21__ / 100
    short_sl_inp = __input_23__ / 100
    short_take_level_1 = strategy.position_avg_price * (1 - short_tp1_inp)
    short_take_level_2 = strategy.position_avg_price * (1 - short_tp2_inp)
    short_stop_level = strategy.position_avg_price * (1 + short_sl_inp)
    crossunder_1 = ta.crossunder(mf, mfi_lower)
    entry_long = ta.crossover(RSI_VWAP_long, RSI_VWAP_overSold_long) and leadLine2 < leadLine1 or (crossunder_1 and leadLine2 < leadLine1)
    entry_price_long = ta.valuewhen(entry_long, close, 0)
    exit_long = ta.crossunder(RSI_VWAP_long, RSI_VWAP_overBought_long)
    crossover_1 = ta.crossover(mf, mfi_upper)
    entry_short = ta.crossunder(RSI_VWAP_short, RSI_VWAP_overBought_short) and leadLine2 > leadLine1 or (crossover_1 and leadLine2 > leadLine1)
    entry_price_short = ta.valuewhen(entry_short, close, 0)
    exit_short = ta.crossover(RSI_VWAP_short, RSI_VWAP_overSold_short)
    testPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, 0, 0)
    testPeriodStop = timestamp(testStopYear, testStopMonth, testStopDay, 0, 0)
    def testPeriod():
        return True if time >= testPeriodStart and time <= testPeriodStop else False

    if testPeriod():
        if strategy.position_size == 0 or (strategy.position_size > 0 and rvi > benchmark):
            if entry_long:
                strategy.entry('long', strategy.long, comment='Insert Enter Long Comment')
        strategy.exit('TP1', 'long', qty_percent=long_tp1_qty, limit=long_take_level_1, stop=long_stop_level)
        strategy.exit('TP2', 'long', qty_percent=long_tp2_qty, limit=long_take_level_2, stop=long_stop_level)
        if exit_long:
            strategy.close('long', comment='Insert Exit Long Comment')
        if strategy.position_size == 0 or (strategy.position_size < 0 and rvi > benchmark):
            if entry_short:
                strategy.entry('short', strategy.short, comment='Insert Enter Short Comment')
        strategy.exit('TP1', 'short', qty_percent=short_tp1_qty, limit=short_take_level_1, stop=short_stop_level)
        strategy.exit('TP2', 'short', qty_percent=short_tp2_qty, limit=short_take_level_2, stop=short_stop_level)
        if exit_short:
            strategy.close('short', comment='Insert Exit Short Comment')
    plot(long_take_level_1 if strategy.position_size > 0 else na, style=plot.style_linebr, color=color.new(color.green, 0), linewidth=1, title='1st Long Take Profit')
    plot(long_take_level_2 if strategy.position_size > 0 else na, style=plot.style_linebr, color=color.new(color.green, 0), linewidth=1, title='2nd Long Take Profit')
    plot(long_stop_level if strategy.position_size > 0 else na, style=plot.style_linebr, color=color.new(color.red, 0), linewidth=1, title='Long Stop Loss')
    plot(short_take_level_1 if strategy.position_size < 0 else na, style=plot.style_linebr, color=color.new(color.green, 0), linewidth=1, title='1st Short Take Profit')
    plot(short_take_level_2 if strategy.position_size < 0 else na, style=plot.style_linebr, color=color.new(color.green, 0), linewidth=1, title='2nd Short Take Profit')
    plot(short_stop_level if strategy.position_size < 0 else na, style=plot.style_linebr, color=color.new(color.red, 0), linewidth=1, title='Long Stop Loss')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
