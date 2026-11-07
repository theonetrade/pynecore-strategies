"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, fill, fixnan, high, input, low, math, na,
    plot, script, strategy, ta
)


@script.strategy('DAX Shooter 5M Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    adxlen=input(14, title='ADX Smoothing'),
    dilen=input(14, title='DI Length'),
    th=input(title='threshold', defval=20),
    len=input.int(7, minval=1, title='Periodo RSI'),
    bandainf=input(30, title='Livello Ipervenduto'),
    bandasup=input(70, title='Livello Ipercomprato'),
    length=input.int(50, minval=1, title='Periodo BB'),
    mult=input.float(2.0, minval=0.001, maxval=50, title='Dev BB')
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
        adx__00000012__ = 100 * ta.rma(math.abs(plus - minus) / (1 if sum == 0 else sum), adxlen)
        return adx__00000012__

    plus, minus = dirmov(dilen)
    sig = adx(dilen, adxlen)
    src = close
    up = ta.rma(math.max(ta.change(src), 0), len)
    down = ta.rma(-math.min(ta.change(src), 0), len)
    rsi = 100 if down == 0 else 0 if up == 0 else 100 - 100 / (1 + up / down)
    source = close
    basis = ta.sma(source, length)
    dev = mult * ta.stdev(source, length)
    upper = basis + dev
    lower = basis - dev
    plot(basis, color=color.new(color.white, 0))
    p1 = plot(upper, color=color.new(color.aqua, 0))
    p2 = plot(lower, color=color.new(color.aqua, 0))
    fill(p1, p2)
    adx_1 = adx(dilen, adxlen)
    if ta.crossover(rsi, bandainf) and adx_1 > 32 and (low < lower):
        strategy.entry('COMPRA', strategy.long, limit=upper, oca_name='DaxShooter', oca_type=strategy.oca.cancel, comment='COMPRA')
    else:
        strategy.cancel(id='COMPRA')
    adx_2 = adx(dilen, adxlen)
    if ta.crossunder(rsi, bandasup) and adx_2 > 32 and (high > upper):
        strategy.entry('VENDI', strategy.short, limit=lower, oca_name='DaxShooter', oca_type=strategy.oca.cancel, comment='VENDI')
    else:
        strategy.cancel(id='VENDI')
    adx_3 = adx(dilen, adxlen)
    buy = ta.crossover(rsi, bandainf) and adx_3 > 32 and (low < lower)
    adx_4 = adx(dilen, adxlen)
    sell = ta.crossunder(rsi, bandasup) and adx_4 > 32 and (high > upper)
    alertcondition(buy, title='Segnale Acquisto', message='Compra DAX')
    alertcondition(sell, title='Segnale Vendita', message='Vendi DAX')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
