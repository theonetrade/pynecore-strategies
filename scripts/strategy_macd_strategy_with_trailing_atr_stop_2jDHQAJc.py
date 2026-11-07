"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, fill, high, input, low, math, na, nz, plot,
    script, strategy, ta, time, timestamp
)
from pynecore.types import Color, Series


@script.strategy('MACD Strategy', overlay=True, pyramiding=2, commission_type=strategy.commission.percent, commission_value=0.04, initial_capital=100, default_qty_type=strategy.cash, default_qty_value=100, currency=currency.USD, margin_long=0, margin_short=0, close_by_id=True)
def main(
    ribbon_period=input.int(34, 'Period', step=1),
    fast_length=input(title='Fast Length', defval=3),
    slow_length=input(title='Slow Length', defval=5),
    src: Series[float] = input(title='Source', defval=close),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=2),
    sma_source=input(title='Simple MA(Oscillator)', defval=False),
    sma_signal=input(title='Simple MA(Signal Line)', defval=True),
    __input_7__=input.float(1, title='Long Take Profit 1 %', step=0.1),
    long_tp1_qty=input.int(10, title='Long Take Profit 1 Qty', step=1),
    __input_9__=input.float(5, title='Long Take Profit 2%', step=0.1),
    long_tp2_qty=input.int(50, title='Long Take Profit 2 Qty', step=1),
    multiplier=input.float(2.2, 'SL Mutiplier', minval=1, step=0.1),
    ATR_period=input.int(17, 'ATR period', minval=1, step=1),
    testStartYear=input(2018, 'Backtest Start Year'),
    testStartMonth=input(1, 'Backtest Start Month'),
    testStartDay=input(1, 'Backtest Start Day'),
    testStopYear=input(9999, 'Backtest Stop Year'),
    testStopMonth=input(12, 'Backtest Stop Month'),
    testStopDay=input(31, 'Backtest Stop Day')
):
    def Ema(src, p):
        ema: Series[float] = 0.0
        sf = 2 / (p + 1)
        ema = nz(ema[1] + sf * (src - ema[1]), src)
        return ema

    def Sma(src, p):
        a: Series = ta.cum(src)
        return (a - a[math.max(p, 0)]) / math.max(p, 0)

    def Atr(p):
        atr: Series[float] = 0.0
        Tr = math.max(high - low, math.max(math.abs(high - close[1]), math.abs(low - close[1])))
        atr = nz(atr[1] + (Tr - atr[1]) / p, Tr)
        return atr

    leadLine1 = ta.ema(close, ribbon_period)
    leadLine2 = ta.sma(close, ribbon_period)
    p3 = plot(leadLine1, color=color.new(color.new('#53B987'), 50), title='EMA', linewidth=1)
    p4 = plot(leadLine2, color=color.new(color.new('#EB4D5C'), 50), title='SMA', linewidth=1)
    fill(p3, p4, color=color.new('#53B987') if leadLine1 > leadLine2 else color.new('#EB4D5C'))
    col_grow_above: Color = color.new('#26A69A')
    col_grow_below: Color = color.new('#FFCDD2')
    col_fall_above: Color = color.new('#B2DFDB')
    col_fall_below: Color = color.new('#EF5350')
    col_macd: Color = color.new('#0094FF')
    col_signal: Color = color.new('#FF6A00')
    fast_ma = Sma(src, fast_length) if sma_source else Ema(src, fast_length)
    slow_ma = Sma(src, slow_length) if sma_source else Ema(src, slow_length)
    macd = fast_ma - slow_ma
    signal = Sma(macd, signal_length) if sma_signal else Ema(macd, signal_length)
    hist = macd - signal
    long_tp1_inp = __input_7__ / 100
    long_tp2_inp = __input_9__ / 100
    long_take_level_1 = strategy.position_avg_price * (1 + long_tp1_inp)
    long_take_level_2 = strategy.position_avg_price * (1 + long_tp2_inp)
    entry_long = ta.crossover(macd, signal) and leadLine2 < leadLine1
    entry_price_long = ta.valuewhen(entry_long, close, 0)
    SL_floating_long = entry_price_long - multiplier * Atr(ATR_period)
    exit_long = close < SL_floating_long
    testPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, 0, 0)
    testPeriodStop = timestamp(testStopYear, testStopMonth, testStopDay, 0, 0)
    def testPeriod():
        return True if time >= testPeriodStart and time <= testPeriodStop else False

    if testPeriod():
        if entry_long:
            strategy.entry('long', strategy.long, comment='Long')
        strategy.exit('TP1', 'long', qty_percent=long_tp1_qty, limit=long_take_level_1)
        strategy.exit('TP2', qty_percent=long_tp2_qty, limit=long_take_level_2)
        if exit_long:
            strategy.close('long', comment='exit long')
    plot(long_take_level_1 if strategy.position_size > 0 else na, style=plot.style_linebr, color=color.new(color.green, 0), linewidth=1, title='1st Long Take Profit')
    plot(long_take_level_2 if strategy.position_size > 0 else na, style=plot.style_linebr, color=color.new(color.green, 0), linewidth=1, title='2nd Long Take Profit')
    plot(SL_floating_long if strategy.position_size > 0 else na, style=plot.style_linebr, color=color.new(color.red, 0), linewidth=1, title='Long Stop Loss')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
