"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, fill, high, hl2, input, location, low,
    math, na, ohlc4, open, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator(title='ENVELOPE - RSI - Buy Sell Signals', shorttitle='ENVELOPE - RSI', overlay=True, na_bool=True)
def main(
    len=input.int(8, title='Envelope Length', minval=1, group='Envelope Settings'),
    percent=input(0.22, title='Envelope Percent', group='Envelope Settings'),
    src: Series[float] = input(hl2, title='Envelope Source', group='Envelope Settings'),
    exponential=input(False),
    rsiLengthInput=input.int(8, minval=1, title='RSI Length', group='RSI Settings'),
    rsiSourceInput: Series[float] = input.source(hl2, 'RSI Source', group='RSI Settings'),
    Overbought_RSI=input.price(title='RSI OverBought Limit(Recommended: 70-85)', defval=80, group='RSI Settings'),
    Oversold_RSI=input.price(title='RSI OverSold Limit(Recommended: 20-30)', defval=25, group='RSI Settings'),
    TP_Percent=input.float(0.15, 'TP %'),
    SL_Percent=input.float(0.15, 'SL %')
):
    basis = ta.ema(src, len) if exponential else ta.sma(src, len)
    k = percent / 100.0
    upper = basis * (1 + k)
    lower = basis * (1 - k)
    plot(basis, 'Basis', color=color.new('#ED7300'))
    u = plot(upper, 'Upper', color=color.new('#FF2424'))
    l = plot(lower, 'Lower', color=color.new('#24FF24'))
    fill(u, l, color=color.rgb(33, 150, 243, 95), title='Background')
    cross_buy: Series = ta.crossover(close, lower)
    cross_sell: Series = ta.crossunder(close, upper)
    up = ta.rma(math.max(ta.change(rsiSourceInput), 0), rsiLengthInput)
    down = ta.rma(-math.min(ta.change(rsiSourceInput), 0), rsiLengthInput)
    rsi = 100 if down == 0 else 0 if up == 0 else 100 - 100 / (1 + up / down)
    cross_1 = ta.cross(low, lower)
    cross_2 = ta.cross(close, lower)
    cross_3 = ta.cross(high, lower)
    cross_4 = ta.cross(open, lower)
    condition_buy = rsi < Oversold_RSI and (cross_1 or cross_2 or cross_3 or cross_4)
    cross_5 = ta.cross(low, upper)
    cross_6 = ta.cross(close, upper)
    cross_7 = ta.cross(high, upper)
    cross_8 = ta.cross(open, upper)
    condition_sell = rsi > Overbought_RSI and (cross_5 or cross_6 or cross_7 or cross_8)
    plotshape((na if na(condition_sell) else 1 if condition_sell else 0) if cross_sell else na, title='Sell Label', text='Sell', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.red, textcolor=color.white)
    sell_sig = plot(high if cross_sell else na, color=color.new(color.new('#000000'), 100))
    plotshape((na if na(condition_buy) else 1 if condition_buy else 0) if cross_buy else na, title='Buy Label', text='Buy', location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.green, textcolor=color.white)
    buy_sig = plot(ohlc4 if cross_buy else na, color=color.new(color.new('#000000'), 100))
    __block_result__ = na
    if cross_sell[1] or cross_sell[2] or cross_buy[1] or cross_buy[2]:
        __block_result__ = color.new(color.new('#1DBC60'), 30)
    else:
        __block_result__ = color.new(color.new('#000000'), 100)
    tpColor = __block_result__
    __block_result_1__ = na
    if cross_sell[1] or cross_sell[2] or cross_buy[1] or cross_buy[2]:
        __block_result_1__ = color.new(color.new('#F74A58'), 30)
    else:
        __block_result_1__ = color.new(color.new('#000000'), 100)
    slColor = __block_result_1__
    __block_result_2__ = na
    if condition_sell:
        __block_result_2__ = ohlc4 - ohlc4 * (TP_Percent / 100)
    elif condition_buy:
        __block_result_2__ = ohlc4 + ohlc4 * (TP_Percent / 100)
    tp = __block_result_2__
    __block_result_3__ = na
    if condition_sell:
        __block_result_3__ = ohlc4 + ohlc4 * (SL_Percent / 100)
    elif condition_buy:
        __block_result_3__ = ohlc4 - ohlc4 * (SL_Percent / 100)
    sl = __block_result_3__
    tp_sig = plot(tp, color=color.new(color.new('#000000'), 100), title='tp')
    sl_sig = plot(sl, color=color.new(color.new('#000000'), 100), title='tp')
    lower_plot = plot(lower, color=color.new(color.new('#000000'), 100))
    fill(sell_sig, tp_sig, color=tpColor)
    fill(buy_sig, tp_sig, color=tpColor)
    fill(buy_sig, sl_sig, color=slColor)
    fill(sell_sig, sl_sig, color=slColor)
    alertConditionBuy = cross_buy and condition_buy
    alertConditionSell = cross_sell and condition_sell
    alertcondition(alertConditionBuy, title='Envelope RSI Buy signal!', message='Buy signal')
    alertcondition(alertConditionSell, title='Envelope RSI Sell signal!', message='Sell signal')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
