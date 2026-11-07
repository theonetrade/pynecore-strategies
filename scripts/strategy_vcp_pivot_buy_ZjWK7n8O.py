"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_float
from pynecore.lib import (
    bgcolor, close, color, high, input, low, na, plot, script, strategy, ta,
    volume
)
from pynecore.types import Series


@script.strategy('My Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    len50=input.int(50, minval=1, title='Length'),
    src: Series[float] = input(close, title='Source'),
    offset=input.int(title='Offset', defval=0, minval=-500, maxval=500),
    len200=input.int(200, minval=1, title='Length'),
    len150=input.int(150, minval=1, title='Length'),
    slow=input.int(50, minval=1, title='TREND'),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=500, defval=10),
    mat11=input.string(defval='ema', options=('ema', 'sma', 'rma', 'vwma', 'wma', 'tema'), title='Moving Average 1 Type'),
    len11=input.int(10, minval=1, title='Moving Average 1 Length'),
    src11: Series[float] = input(close, title='Moving Average 1 Source'),
    off11=input.int(0, minval=0, title='Moving Average 1 Offset'),
    mat22=input.string(defval='ema', options=('ema', 'sma', 'rma', 'vwma', 'wma', 'tema'), title='Moving Average 2 Type'),
    len22=input.int(20, minval=1, title='Moving Average 2 Length'),
    src22: Series[float] = input(close, title='Moving Average 2 Source'),
    off22=input.int(0, minval=0, title='Moving Average 2 Offset'),
    atr_length=input(defval=3, title='ATR Length'),
    lookback=input(defval=150, title='Look Back Period'),
    closerange=input(defval=4, title='Close range'),
    percentile1=input(defval=30, title='Smaller Percentile'),
    percentile2=input(defval=40, title='Largerer Percentile'),
    high_loopback=input(3, 'High Lookback Length'),
    __input_21__=input(10.0, title='Take Profit %'),
    __input_22__=input(10.0, title='Stoploss %')
):
    out50: Series = ta.sma(src, len50)
    plot(out50, color=color.new(color.blue, 0), title='MA', offset=offset)
    out200: Series = ta.sma(src, len200)
    plot(out200, color=color.new(color.red, 0), title='MA', offset=offset)
    out150 = ta.sma(src, len150)
    plot(out150, color=color.new(color.green, 0), title='MA', offset=offset)
    slowline = ta.sma(volume, slow)
    trend = ta.sma(slowline, signal_length)
    def tema(s, p):
        return 3 * ta.ema(s, p) - 3 * ta.ema(ta.ema(s, p), p) + ta.ema(ta.ema(ta.ema(s, p), p), p)

    def ma(t, s, p):
        ema_1 = ta.ema(s, p)
        rma_1 = ta.rma(s, p)
        vwma_1 = ta.vwma(s, p)
        wma_1 = ta.wma(s, p)
        tema_1 = tema(s, p)
        sma_1 = ta.sma(s, p)
        return ema_1 if t == 'ema' else rma_1 if t == 'rma' else vwma_1 if t == 'vwma' else wma_1 if t == 'wma' else tema_1 if t == 'tema' else sma_1

    def off(s: Series, o):
        offset_1 = s[1 if o == 0 else o]
        return offset_1 if o > 0 else s

    out11 = ma(mat11, off(src11, off11), len11)
    out22 = ma(mat22, off(src22, off22), len22)
    plot(out11, color=color.new(color.new('#1155CC'), 0), title='MA 1')
    plot(out22, color=color.new(color.new('#FF0000'), 50), linewidth=2, title='MA 2')
    bullishtrenddef = close > out50 and out50 > out150 and (out150 > out200) and (out200 > out200[1]) and (out200 > out200[20]) and (out50 >= out50[1])
    atr_value1: float = 0.0
    stan1: float = 0.0
    range1: float = 0.0
    l1: float = 0.0
    h1: float = 0.0
    for i in pine_range(1, atr_length, 1):
        h1 = ta.highest(high, atr_length)
        l1 = ta.lowest(low, atr_length)
        range1 = h1 - l1
    atrp1 = range1 / h1 * 100
    atr_value2: float = 0.0
    stan2: float = 0.0
    range2: float = 0.0
    l2: float = 0.0
    h2: float = 0.0
    for i in pine_range(1, atr_length, 1):
        h2 = ta.highest(close, atr_length)
        l2 = ta.lowest(close, atr_length)
        range2 = h2 - l2
    atrp2 = range2 / h2 * 100
    per1 = ta.percentrank(atrp1, lookback)
    per2 = ta.percentrank(atrp2, lookback)
    setting1 = per1 <= percentile2 and per1 > percentile1
    rangepivot = per1 <= percentile1 and atrp1 <= 10
    closepivot = atrp2 <= closerange
    pivot = rangepivot or closepivot
    sessioncolor2 = color.yellow if setting1 and bullishtrenddef else na
    sessioncolor3 = color.blue if rangepivot and bullishtrenddef else na
    sessioncolor4 = color.red if closepivot and bullishtrenddef else na
    bgcolor(sessioncolor2)
    bgcolor(sessioncolor3)
    bgcolor(sessioncolor4)
    h3: Series = cast_float(ta.highest(high, high_loopback))
    takePer = __input_21__ / 100
    shortPer = __input_22__ / 100
    stoploss = strategy.position_avg_price * (1 - shortPer)
    longTake1 = strategy.position_avg_price * (1 + takePer)
    longTake2 = strategy.position_avg_price * (1 + takePer * 2)
    longTake3 = strategy.position_avg_price * (1 + takePer * 3)
    long1 = bullishtrenddef and pivot
    if long1:
        strategy.entry('Long', strategy.long, stop=h3[1])
    if strategy.position_size > 0:
        strategy.exit(id='Close Long1', qty_percent=25, stop=stoploss, limit=longTake1)
    if strategy.position_size > 0:
        strategy.exit(id='Close Long2', qty_percent=50, stop=stoploss, limit=longTake2)
    if strategy.position_size > 0:
        strategy.exit(id='Close Long3', qty_percent=100, stop=stoploss, limit=longTake3)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
