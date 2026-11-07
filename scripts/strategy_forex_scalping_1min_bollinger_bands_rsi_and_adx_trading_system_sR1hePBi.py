"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fixnan, high, input, low, math, na, script, strategy,
    string, ta, time
)
from pynecore.types import Series


@script.strategy('Bollinger Bands, RSI and ADX Trading System', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    length=input(20),
    overSold=input(35),
    overBought=input(65),
    lengthB=input.int(60, minval=1),
    src: Series[float] = input(close, title='Source'),
    mult=input.float(2.0, minval=0.001, maxval=50, title='StdDev'),
    adxlen=input(14, title='ADX Smoothing'),
    dilen=input(14, title='DI Length'),
    tp=input.int(90, step=10),
    sl=input.int(90, step=10)
):
    def timeinrange(res, sess):
        return time(res, sess if sess == '' else sess + ('23456' if string.endswith(sess, ':') else '' if string.contains(sess, ':') else ':23456')) != 0

    timer = color.red
    price = close
    vrsi = ta.rsi(price, length)
    co = ta.crossover(vrsi, overSold)
    cu = ta.crossunder(vrsi, overBought)
    basis = ta.sma(src, lengthB)
    dev = mult * ta.stdev(src, lengthB)
    upper = basis + dev
    lower = basis - dev
    def dirmov(len):
        up = ta.change(high)
        down = -ta.change(low)
        plusDM = na if na(up) else up if up > down and up > 0 else 0
        minusDM = na if na(down) else down if down > up and down > 0 else 0
        truerange = ta.rma(ta.tr, len)
        plus = fixnan(100 * ta.rma(plusDM, len) / truerange)
        minus = fixnan(100 * ta.rma(minusDM, len) / truerange)
        return (plus, minus)

    def adx(dilen, adxlen):
        plus, minus = dirmov(dilen)
        sum = plus + minus
        adx__00000020__ = 100 * ta.rma(math.abs(plus - minus) / (1 if sum == 0 else sum), adxlen)
        return adx__00000020__

    sig = adx(dilen, adxlen)
    crossover_1 = ta.crossover(vrsi, overSold)
    longEntry = close < upper and crossover_1 and (sig < 32)
    crossunder_1 = ta.crossunder(vrsi, overBought)
    shortEntry = close > upper and crossunder_1 and (sig < 32)
    if longEntry:
        strategy.entry('long', strategy.long)
    strategy.exit('X_long', 'long', profit=tp, loss=sl)
    if ta.crossunder(close, basis):
        strategy.close('long')
    if shortEntry:
        strategy.entry('short', strategy.short)
    strategy.exit('x_short', 'short', profit=tp, loss=sl)
    if ta.crossover(close, basis):
        strategy.close('short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
