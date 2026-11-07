"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, location, low, na, open, plot, plotshape,
    script, shape, size, strategy, ta
)


@script.strategy('Super Scalper - 5 Min 15 Min', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    atrlen=input.int(14, 'ATR Period'),
    mult=input.float(1, 'ATR Multi', step=0.1),
    smoothing=input.string(title='ATR Smoothing', defval='WMA', options=('RMA', 'SMA', 'EMA', 'WMA')),
    ShortEMAlen=input.int(21, 'Fast EMA'),
    LongEMAlen=input.int(65, 'Slow EMA'),
    RSILen1=input.int(25, 'Fast RSI Length'),
    RSILen2=input.int(100, 'Slow RSI Length')
):
    source = close
    def ma_function(source, atrlen):
        __block_result__ = na
        if smoothing == 'RMA':
            __block_result__ = ta.rma(source, atrlen)
        else:
            __block_result_1__ = na
            if smoothing == 'SMA':
                __block_result_1__ = ta.sma(source, atrlen)
            else:
                __block_result_2__ = na
                if smoothing == 'EMA':
                    __block_result_2__ = ta.ema(source, atrlen)
                else:
                    __block_result_2__ = ta.wma(source, atrlen)
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    atr_slen = ma_function(ta.tr(True), atrlen)
    upper_band = atr_slen * mult + close
    lower_band = close - atr_slen * mult
    shortSMA = ta.ema(close, ShortEMAlen)
    longSMA = ta.ema(close, LongEMAlen)
    rsi1 = ta.rsi(close, RSILen1)
    rsi2 = ta.rsi(close, RSILen2)
    atr = ta.atr(atrlen)
    RSILong = rsi1 > rsi2
    RSIShort = rsi1 < rsi2
    longCondition = open < lower_band
    shortCondition = open > upper_band
    GoldenLong = ta.crossover(shortSMA, longSMA)
    Goldenshort = ta.crossover(longSMA, shortSMA)
    plotshape(shortCondition, title='Sell Label', text='Sell', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.red, textcolor=color.white)
    plotshape(longCondition, title='Buy Label', text='Buy', location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.green, textcolor=color.white)
    plotshape(Goldenshort, title='Golden Sell Label', text='Golden Crossover Short', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.blue, textcolor=color.white)
    plotshape(GoldenLong, title='Golden Buy Label', text='Golden Crossover Long', location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.yellow, textcolor=color.white)
    if longCondition:
        stopLoss = low - atr * 2
        takeProfit = high + atr * 5
        if RSILong:
            strategy.entry('long', strategy.long)
    if shortCondition:
        stopLoss = high + atr * 2
        takeProfit = low - atr * 5
        if RSIShort:
            strategy.entry('short', strategy.short)
    plot(upper_band)
    plot(lower_band)
    plot(shortSMA, color=color.red)
    plot(longSMA, color=color.yellow)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
