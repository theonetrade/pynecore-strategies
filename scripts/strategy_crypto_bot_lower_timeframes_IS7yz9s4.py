"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, high, input, low, script, strategy, syminfo, ta
from pynecore.types import Color, Series


@script.strategy(title='Price EMA with stock', shorttitle='EMA STOCH', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    src: Series[float] = input(title='Source', defval=close),
    len50=input.int(50, minval=1, title='Length'),
    src50: Series[float] = input(close, title='Source'),
    len100=input(100),
    src100: Series[float] = input(close, title='Source'),
    len1=input.int(1, minval=1, title='Length'),
    src1: Series[float] = input(close, title='Source'),
    length=input.int(5, minval=1),
    OverBought=input(80),
    OverSold=input(20),
    fast_length=input(title='Fast Length', defval=12),
    slow_length=input(title='Slow Length', defval=26),
    src_macd: Series[float] = input(title='Source', defval=close),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9),
    sma_source=input(title='Simple MA(Oscillator)', defval=False),
    sma_signal=input(title='Simple MA(Signal Line)', defval=False),
    tp=input(0.1),
    sl=input(0.1)
):
    src_0 = src
    src_1 = src[1]
    src_2 = src[2]
    src_3 = src[3]
    src_4 = src[4]
    out50 = ta.ema(src50, len50)
    out100 = ta.ema(src100, len100)
    out1 = ta.sma(src1, len1)
    smoothK: int = 3
    smoothD: int = 3
    k = ta.sma(ta.stoch(close, high, low, length), smoothK)
    d = ta.sma(k, smoothD)
    cu = ta.crossover(k, OverSold)
    co = ta.crossunder(k, OverBought)
    sma_down = ta.crossunder(out1, out50)
    sma_up = ta.crossover(out1, out50)
    crossCandle_4 = ta.crossover(src[4], out50)
    crossCandleUnder_4 = ta.cross(src[4], out50)
    crossCandle_3 = ta.crossover(src[3], out50)
    crossCandleUnder_3 = ta.crossunder(src[3], out50)
    crossCandle_2 = ta.crossover(src[2], out50)
    crossCandleUnder_2 = ta.crossunder(src[2], out50)
    crossCandle_1 = ta.crossover(src[1], out50)
    crossCandleUnder_1 = ta.crossunder(src[1], out50)
    crossCandle_0 = ta.crossover(src, out50)
    crossCandleUnder_0 = ta.crossunder(src, out50)
    conditionOver = crossCandle_4 or crossCandle_3 or crossCandle_2 or crossCandle_1 or crossCandle_0
    conditionUnder = crossCandleUnder_4 or crossCandleUnder_3 or crossCandleUnder_2 or crossCandleUnder_1 or crossCandleUnder_0
    cross_1 = ta.cross(high[4], out50)
    touch4 = ta.cross(low[4], out50) or cross_1
    cross_2 = ta.cross(high[3], out50)
    touch3 = ta.cross(low[3], out50) or cross_2
    cross_3 = ta.cross(high[2], out50)
    touch2 = ta.cross(low[2], out50) or cross_3
    cross_4 = ta.cross(high[1], out50)
    touch1 = ta.cross(low[1], out50) or cross_4
    touch = touch1 or touch2 or touch3 or touch4
    col_grow_above: Color = color.new('#26A69A')
    col_grow_below: Color = color.new('#FFCDD2')
    col_fall_above: Color = color.new('#B2DFDB')
    col_fall_below: Color = color.new('#EF5350')
    col_macd: Color = color.new('#0094FF')
    col_signal: Color = color.new('#FF6A00')
    fast_ma = ta.sma(src_macd, fast_length) if sma_source else ta.ema(src_macd, fast_length)
    slow_ma = ta.sma(src_macd, slow_length) if sma_source else ta.ema(src_macd, slow_length)
    macd = fast_ma - slow_ma
    signal = ta.sma(macd, signal_length) if sma_signal else ta.ema(macd, signal_length)
    hist = macd - signal
    long_cond = (conditionOver or conditionUnder or touch) and src >= out50 and (close > out50) and cu and (out50 > out100) and (hist >= 0)
    short_cond = (conditionOver or conditionUnder or touch) and src <= out50 and (close < out50) and co and (out50 < out100) and (hist <= 0)
    if long_cond:
        strategy.entry('long', strategy.long)
    if short_cond:
        strategy.entry('short', strategy.short)
    if touch:
        strategy.exit('X_long', 'long', profit=close * tp / syminfo.mintick, loss=close * sl / syminfo.mintick)
    if touch:
        strategy.exit('x_short', 'short', profit=close * tp / syminfo.mintick, loss=close * sl / syminfo.mintick)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
