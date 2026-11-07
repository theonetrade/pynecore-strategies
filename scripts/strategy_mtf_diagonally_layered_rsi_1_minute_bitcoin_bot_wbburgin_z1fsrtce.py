"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.core.series import inline_series
from pynecore.lib import (
    barstate, close, color, fill, hline, input, location, math, na, plot,
    plotshape, request, script, shape, size, strategy, syminfo, ta, timeframe
)
from pynecore.types import Series


@script.strategy('MTF Layered RSI - Bitcoin Bot [wbburgin]', overlay=False, initial_capital=10000, pyramiding=2, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    length=input.int(7, 'RSI Length', group='Config'),
    tf2=input.timeframe('3', title='HT 1', group='Config'),
    tf3=input.timeframe('5', title='HT 2', group='Config'),
    ob=input.int(80, 'Overbought Level', group='Config'),
    os=input.int(20, 'Oversold Level', group='Config'),
    calcType=input.string('Manual Calculation', options=('Security Function', 'Manual Calculation'), title='Calc Type', tooltip='Manual calculation is a way to stop repaint without using request.security().'),
    use200ma=input.bool(False, 'Use EMA Filter', group='Risk Management'),
    emaLen=input.int(200, 'EMA Length', group='Risk Management'),
    stoploss=input.bool(False, 'Use % Stop Loss', group='Risk Management'),
    stoplosspercent=input.float(0.5, title='Stop Loss (%)', group='Risk Management'),
    tradeType=input.string('Long-only', options=('Long-only', 'Long and Short'), title='Allow Shorts?')
):
    rsi: Series = ta.rsi(close, length)
    indexHighTF = 1 if barstate.isrealtime else 0
    indexCurrTF = 0 if barstate.isrealtime else 1
    rsi2_sec = inline_series(request.security(syminfo.tickerid, tf2, rsi[indexHighTF]), indexCurrTF)
    rsi3_sec = inline_series(request.security(syminfo.tickerid, tf3, rsi[indexHighTF]), indexCurrTF)
    currentTF = timeframe.period
    def tf_to_int(timeframe__ren__):
        __block_result__ = na
        if timeframe__ren__ == '1S':
            __block_result__ = 1
        elif timeframe__ren__ == '5S':
            __block_result__ = 5
        elif timeframe__ren__ == '10S':
            __block_result__ = 10
        elif timeframe__ren__ == '15S':
            __block_result__ = 15
        elif timeframe__ren__ == '30S':
            __block_result__ = 30
        elif timeframe__ren__ == '1':
            __block_result__ = 60
        elif timeframe__ren__ == '3':
            __block_result__ = 180
        elif timeframe__ren__ == '5':
            __block_result__ = 300
        elif timeframe__ren__ == '15':
            __block_result__ = 900
        elif timeframe__ren__ == '30':
            __block_result__ = 1800
        elif timeframe__ren__ == '45':
            __block_result__ = 2700
        elif timeframe__ren__ == '60':
            __block_result__ = 3600
        elif timeframe__ren__ == '120':
            __block_result__ = 7200
        elif timeframe__ren__ == '180':
            __block_result__ = 10800
        elif timeframe__ren__ == '240':
            __block_result__ = 14400
        elif timeframe__ren__ == '480':
            __block_result__ = 28800
        elif timeframe__ren__ == '720':
            __block_result__ = 43200
        elif timeframe__ren__ == 'D':
            __block_result__ = 86400
        elif timeframe__ren__ == 'W':
            __block_result__ = 604800
        elif timeframe__ren__ == 'M':
            __block_result__ = 2595000
        return __block_result__

    ct_int = tf_to_int(currentTF)
    ht1_int = tf_to_int(tf2)
    ht2_int = tf_to_int(tf3)
    ht1_mult = cast_int(ht1_int / ct_int)
    ht2_mult = cast_int(ht2_int / ct_int)
    def manualRSI(time_mult, len):
        htclose: Series = close
        u = math.max(htclose - htclose[time_mult], 0)
        d = math.max(htclose[time_mult] - htclose, 0)
        rs = ta.rma(u, len * time_mult) / ta.rma(d, len * time_mult)
        res = 100 - 100 / (1 + rs)
        return res

    rsi2_man = manualRSI(ht1_mult, length)
    rsi3_man = manualRSI(ht2_mult, length)
    rsi2 = rsi2_sec if calcType == 'Security Function' else rsi2_man
    rsi3 = rsi3_sec if calcType == 'Security Function' else rsi3_man
    plot(rsi, color=color.yellow, title='RSI Current TF')
    plot(rsi2, color=color.new(color.yellow, 50), title='RSI HT1')
    plot(rsi3, color=color.new(color.yellow, 75), title='RSI HT2')
    lm = hline(os, title='Oversold')
    hm = hline(ob, title='Overbought')
    fill(hm, lm, color=color.new(color.blue, 95))
    crossover_1 = ta.crossover(rsi3, os)
    htCross = ta.crossover(rsi2, os) and rsi3 > os and (rsi > os) or (crossover_1 and rsi2 > os and (rsi > os))
    buySig = ta.crossover(rsi, os) and rsi2 < os and (rsi3 < os) or htCross
    sellSig = ta.crossunder(rsi, ob)
    crossunder_1 = ta.crossunder(rsi3, ob)
    htCross_short = ta.crossunder(rsi2, ob) and rsi3 < ob and (rsi < ob) or (crossunder_1 and rsi2 < ob and (rsi < ob))
    shortEntry = ta.crossunder(rsi, ob) and rsi2 > ob and (rsi3 > ob) or htCross_short
    shortExit = ta.crossover(rsi, os)
    ema200 = ta.ema(close, emaLen)
    filter = (True if close > ema200 else False) if use200ma else True
    shortfilter = (True if close < ema200 else False) if use200ma else True
    stoplosslevel_long = (1 - stoplosspercent / 100) * ta.valuewhen(buySig and filter, close, 0)
    stoplosslevel_short = (1 + stoplosspercent / 100) * ta.valuewhen(shortEntry and shortfilter, close, 0)
    initiate_stoploss_long = ta.crossunder(close, stoplosslevel_long) if stoploss else na
    initiate_stoploss_short = ta.crossover(close, stoplosslevel_short) if stoploss else na
    if buySig and filter:
        strategy.entry('Long', strategy.long)
    if sellSig or initiate_stoploss_long:
        strategy.close('Long')
    if shortEntry and shortfilter and (tradeType == 'Long and Short'):
        strategy.entry('Short', strategy.short)
    if shortExit or initiate_stoploss_short:
        strategy.close('Short')
    plotshape(buySig and filter, title='Buysig', style=shape.triangleup, location=location.bottom, color=color.green, size=size.tiny)
    plotshape(sellSig or initiate_stoploss_long, title='Sellsig', style=shape.triangledown, location=location.top, color=color.red, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
