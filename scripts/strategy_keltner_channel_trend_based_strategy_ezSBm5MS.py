"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fill, fixnan, high, input, low, math, na, open, plot,
    script, strategy, ta, time, timestamp
)


@script.strategy('Keltner Channel ETH/USDT 1H', overlay=True, initial_capital=1000, pyramiding=0, currency='USD', default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.07, margin_long=0, margin_short=0, close_by_id=True)
def main(
    ribbon_period=input.int(46, 'Period', step=1),
    useTrueRange=input(True),
    length=input.int(81, step=1, minval=1),
    mult=input.float(2.5, step=0.1),
    dilen=input(19, title='DI Length'),
    benchmark=input.int(title='DMI Benchmark', defval=27, minval=1, step=1),
    testStartYear=input(2019, 'Backtest Start Year'),
    testStartMonth=input(1, 'Backtest Start Month'),
    testStartDay=input(1, 'Backtest Start Day'),
    testStopYear=input(9999, 'Backtest Stop Year'),
    testStopMonth=input(12, 'Backtest Stop Month'),
    testStopDay=input(31, 'Backtest Stop Day'),
    __input_12__=input.float(4.5, title='Long Take Profit 1 %', step=0.1),
    long_tp1_qty=input.int(15, title='Long Take Profit 1 Qty', step=1),
    __input_14__=input.float(20, title='Long Take Profit 2%', step=0.1),
    long_tp2_qty=input.int(100, title='Long Take Profit 2 Qty', step=1),
    __input_16__=input.float(4, title='Long Stop Loss %', step=0.1)
):
    leadLine1 = ta.ema(close, ribbon_period)
    leadLine2 = ta.sma(close, ribbon_period)
    UT = leadLine2 < leadLine1
    DT = leadLine2 > leadLine1
    source = close
    ma = ta.sma(source, length)
    range_1 = ta.tr if useTrueRange else high - low
    rangema = ta.sma(range_1, length)
    upper = ma + rangema * mult
    lower = ma - rangema * mult
    plot(ma, title='Middle', color=color.new(color.orange, 0))
    p1 = plot(upper, title='Upper', color=color.new(color.orange, 0))
    p2 = plot(lower, title='Lower', color=color.new(color.orange, 0))
    fill(p1, p2)
    adxlen: int = 10
    keyLevel: int = 23
    def dirmov(len):
        up = ta.change(high)
        down = -ta.change(low)
        truerange = ta.rma(ta.tr, len)
        plus = fixnan(100 * ta.rma(up if up > down and up > 0 else 0, len) / truerange)
        minus = fixnan(100 * ta.rma(down if down > up and down > 0 else 0, len) / truerange)
        return (plus, minus)

    def adx(dilen, adxlen):
        plus, minus = dirmov(dilen)
        sum = plus + minus
        adx__0000001d__ = 100 * ta.rma(math.abs(plus - minus) / (1 if sum == 0 else sum), adxlen)
        return (adx__0000001d__, plus, minus)

    sig, up, down = adx(dilen, adxlen)
    testPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, 0, 0)
    testPeriodStop = timestamp(testStopYear, testStopMonth, testStopDay, 0, 0)
    def testPeriod():
        return True if time >= testPeriodStart and time <= testPeriodStop else False

    long_tp1_inp = __input_12__ / 100
    long_tp2_inp = __input_14__ / 100
    long_take_level_1 = strategy.position_avg_price * (1 + long_tp1_inp)
    long_take_level_2 = strategy.position_avg_price * (1 + long_tp2_inp)
    long_sl_inp = __input_16__ / 100
    long_stop_level = strategy.position_avg_price * (1 - long_sl_inp)
    entry_long = open > lower and open < upper and (close > upper) and (up > down) and (up > benchmark)
    entry_price_long = ta.valuewhen(entry_long, close, 0)
    SL_long = entry_price_long * (1 - long_sl_inp)
    exit_long = close < lower or low < SL_long
    if testPeriod():
        if UT:
            if entry_long:
                strategy.entry(id='Long', direction=strategy.long, comment='INSERT ENTER LONG COMMAND')
        strategy.exit('TP1', 'Long', qty_percent=long_tp1_qty, limit=long_take_level_1)
        strategy.exit('TP2', 'Long', qty_percent=long_tp2_qty, limit=long_take_level_2)
        if exit_long:
            strategy.close(id='Long', comment='INSERT EXIT LONG COMMAND')
    plot(long_take_level_1 if strategy.position_size > 0 else na, style=plot.style_linebr, color=color.new(color.green, 0), linewidth=1, title='1st Long Take Profit')
    plot(long_take_level_2 if strategy.position_size > 0 else na, style=plot.style_linebr, color=color.new(color.green, 0), linewidth=1, title='2nd Long Take Profit')
    plot(long_stop_level if strategy.position_size > 0 else na, style=plot.style_linebr, color=color.new(color.red, 0), linewidth=1, title='Long Stop Loss')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
