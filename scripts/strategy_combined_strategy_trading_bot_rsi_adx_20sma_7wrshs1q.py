"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, fixnan, high, hl2, input, low, math, na, nz, script, strategy,
    syminfo, ta
)
from pynecore.types import Series


@script.strategy('Combined Strategy', overlay=True, default_qty_value=100, initial_capital=1000, margin_long=0.1, margin_short=0, default_qty_type=strategy.fixed, close_by_id=True)
def main(
    adxlen=input(7, title='ADX Smoothing'),
    dilen=input(7, title='DI Length'),
    OB=input(70),
    OS=input(30),
    length=input.int(title='Length', minval=1, maxval=1000, defval=5)
):
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
        adx__00000011__ = 100 * ta.rma(math.abs(plus - minus) / (1 if sum == 0 else sum), adxlen)
        return adx__00000011__

    sig = adx(dilen, adxlen)
    def pine_supertrend(factor, atrPeriod):
        src = hl2
        atr: Series = ta.atr(atrPeriod)
        upperBand: Series = src + factor * atr
        lowerBand: Series = src - factor * atr
        prevLowerBand = nz(lowerBand[1])
        prevUpperBand = nz(upperBand[1])
        lowerBand = lowerBand if lowerBand > prevLowerBand or close[1] < prevLowerBand else prevLowerBand
        upperBand = upperBand if upperBand < prevUpperBand or close[1] > prevUpperBand else prevUpperBand
        direction: int = na(int)
        superTrend: Series[float] = na(float)
        prevSuperTrend = superTrend[1]
        rsi_1 = ta.rsi(close, 21)
        rsi_2 = ta.rsi(close, 3)
        rsi_3 = ta.rsi(close, 28)
        if na(atr[1]) and rsi_1 < 66 and (rsi_2 > 80) and (rsi_3 > 49) and (sig > 20):
            direction = 1
        elif prevSuperTrend == prevUpperBand:
            direction = -1 if close > upperBand else 1
        else:
            direction = 1 if close < lowerBand else -1
        superTrend = lowerBand if direction == -1 else upperBand
        return (superTrend, direction)

    pineSupertrend, pineDirection = pine_supertrend(3, 10)
    upTrend = pineDirection < 0
    downTrend = pineDirection > 0
    sma20 = ta.sma(close, 20)
    a = ta.rsi(close, 14)
    os = a > OB
    ob = a < OS
    if upTrend and close > pineSupertrend and (close > sma20) and os:
        strategy.entry('Buy', strategy.long)
    if ta.crossunder(close, sma20) or ob:
        strategy.close_all()
    upBound = ta.highest(high, length)
    downBound = ta.lowest(low, length)
    if not na(close[length]):
        strategy.entry('ChBrkLE', strategy.long, stop=upBound + syminfo.mintick, comment='ChBrkLE')
    strategy.entry('ChBrkSE', strategy.short, stop=downBound - syminfo.mintick, comment='ChBrkSE')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)