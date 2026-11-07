"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fill, high, input, low, math, na, nz, plot, script,
    strategy, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy('Automated Bitcoin (BTC) Investment Strategy', overlay=True, initial_capital=5000, pyramiding=0, currency='USD', default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.1, margin_long=0, margin_short=0, close_by_id=True)
def main(
    tradeType=input.string('LONG', title='What trades should be taken : ', options=('LONG', 'SHORT', 'BOTH', 'NONE')),
    trend_type1=input.string('TEMA', title='First Trend Line : ', options=('LSMA', 'TEMA', 'EMA', 'SMA')),
    trend_type2=input.string('LSMA', title='First Trend Line : ', options=('LSMA', 'TEMA', 'EMA', 'SMA')),
    trend_type1_length=input(25, 'Length of the First Trend Line'),
    trend_type2_length=input(100, 'Length of the Second Trend Line'),
    __input_5__=input.float(15, title='Long Take Profit 1 %', step=0.1),
    long_tp1_qty=input.int(20, title='Long Take Profit 1 Qty', step=1),
    __input_7__=input.float(30, title='Long Take Profit 2%', step=0.1),
    long_tp2_qty=input.int(20, title='Long Take Profit 2 Qty', step=1),
    __input_9__=input.float(5, title='stop loss in %', step=0.1),
    multiplier=input.float(3.5, 'SL Mutiplier', minval=1, step=0.1),
    ATR_period=input.int(8, 'ATR period', minval=1, step=1),
    SC: Series[float] = input(close, 'Source'),
    testStartYear=input(2016, 'Backtest Start Year'),
    testStartMonth=input(1, 'Backtest Start Month'),
    testStartDay=input(1, 'Backtest Start Day'),
    testStopYear=input(9999, 'Backtest Stop Year'),
    testStopMonth=input(12, 'Backtest Stop Month'),
    testStopDay=input(31, 'Backtest Stop Day')
):
    def Atr(p):
        atr: Series[float] = 0.0
        Tr = math.max(high - low, math.max(math.abs(high - close[1]), math.abs(low - close[1])))
        atr = nz(atr[1] + (Tr - atr[1]) / p, Tr)
        return atr

    def TEMA(series, length):
        __block_result__ = na
        if length > 0:
            ema1 = ta.ema(series, length)
            ema2 = ta.ema(ema1, length)
            ema3 = ta.ema(ema2, length)
            __block_result__ = 3 * ema1 - 3 * ema2 + ema3
        else:
            __block_result__ = na
        return __block_result__

    source = close
    __block_result_1__ = na
    if trend_type1 == 'LSMA':
        __block_result_1__ = ta.linreg(close, trend_type1_length, 0)
    elif trend_type1 == 'TEMA':
        __block_result_1__ = TEMA(close, trend_type1_length)
    elif trend_type1 == 'EMA':
        __block_result_1__ = ta.ema(close, trend_type1_length)
    else:
        __block_result_1__ = ta.sma(close, trend_type1_length)
    leadLine1 = __block_result_1__
    __block_result_2__ = na
    if trend_type2 == 'LSMA':
        __block_result_2__ = ta.linreg(close, trend_type2_length, 0)
    elif trend_type2 == 'TEMA':
        __block_result_2__ = TEMA(close, trend_type2_length)
    elif trend_type2 == 'EMA':
        __block_result_2__ = ta.ema(close, trend_type2_length)
    else:
        __block_result_2__ = ta.sma(close, trend_type2_length)
    leadLine2 = __block_result_2__
    p3 = plot(leadLine1, color=color.new(color.new('#53B987'), 50), title='EMA', linewidth=1)
    p4 = plot(leadLine2, color=color.new(color.new('#EB4D5C'), 50), title='SMA', linewidth=1)
    fill(p3, p4, color=color.new('#53B987') if leadLine1 > leadLine2 else color.new('#EB4D5C'))
    UT = ta.crossover(leadLine1, leadLine2)
    DT = ta.crossunder(leadLine1, leadLine2)
    long_tp1_inp = __input_5__ / 100
    long_tp2_inp = __input_7__ / 100
    long_take_level_1 = strategy.position_avg_price * (1 + long_tp1_inp)
    long_take_level_2 = strategy.position_avg_price * (1 + long_tp2_inp)
    long_sl_input = __input_9__ / 100
    long_sl_input_level = strategy.position_avg_price * (1 - long_sl_input)
    SL1 = multiplier * Atr(ATR_period)
    Trail1: Series[float] = 0.0
    iff_1 = SC - SL1 if SC > nz(Trail1[1], 0) else SC + SL1
    Trail1 = math.min(nz(Trail1[1], 0), SC + SL1) if SC < nz(Trail1[1], 0) and SC[1] < nz(Trail1[1], 0) else iff_1
    Trail1_high = ta.highest(Trail1, 50)
    entry_long = ta.crossover(leadLine1, leadLine2) and Trail1_high < close
    crossover_1 = ta.crossover(leadLine2, leadLine1)
    exit_long = close < Trail1_high or crossover_1 or close < long_sl_input_level
    testPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, 0, 0)
    testPeriodStop = timestamp(testStopYear, testStopMonth, testStopDay, 0, 0)
    def testPeriod():
        return True if time >= testPeriodStart and time <= testPeriodStop else False

    if testPeriod():
        if tradeType == 'LONG' or tradeType == 'BOTH':
            if strategy.position_size == 0 or strategy.position_size > 0:
                if entry_long:
                    strategy.entry('long', strategy.long, comment='b8f60da7_ENTER-LONG_BINANCE_BTC/USDT_b8f60da7-BTC-Investment_4H')
                strategy.exit('TP1', 'long', qty_percent=long_tp1_qty, limit=long_take_level_1)
                strategy.exit('TP2', 'long', qty_percent=long_tp2_qty, limit=long_take_level_2)
                if exit_long:
                    strategy.close('long', comment='b8f60da7_EXIT-LONG_BINANCE_BTC/USDT_b8f60da7-BTC-Investment_4H')
    plot(long_take_level_1 if strategy.position_size > 0 else na, style=plot.style_linebr, color=color.new(color.green, 0), linewidth=1, title='1st Long Take Profit')
    plot(long_take_level_2 if strategy.position_size > 0 else na, style=plot.style_linebr, color=color.new(color.green, 0), linewidth=1, title='2nd Long Take Profit')
    plot(Trail1_high if strategy.position_size > 0 else na, style=plot.style_linebr, color=color.new(color.red, 0), linewidth=1, title='Long Stop Loss')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
