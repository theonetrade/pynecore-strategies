"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, script, strategy, ta
from pynecore.types import Series


@script.strategy(title='Scalping Trading System Crypto and Stocks', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    src: Series[float] = input(low, title='Source'),
    len=input.int(25, minval=1, title='Length SMA', group='Moving Averages'),
    len2=input.int(200, minval=1, title='Length EMA', group='Moving Averages'),
    lengthk=input.int(10, minval=1, title='Length Keltner Channel', group='Keltner'),
    mult=input(2.0, 'Multiplier', group='Keltner'),
    BandsStyle=input.string('Average True Range', options=('Average True Range', 'True Range', 'Range'), title='Bands Style', group='Keltner'),
    atrlength=input(14, 'ATR Length', group='Keltner'),
    periodK=input.int(10, title='%K Length', minval=1, group='Stochastic'),
    smoothK=input.int(1, title='%K Smoothing', minval=1, group='Stochastic'),
    periodD=input.int(1, title='%D Smoothing', minval=1, group='Stochastic'),
    fast_length=input(title='Fast Length MACD', defval=4, group='MACD Fast'),
    slow_length=input(title='Slow Length MACD', defval=34, group='MACD Fast'),
    signal_length=input.int(title='Signal Smoothing MACD', minval=1, maxval=50, defval=5, group='MACD Fast'),
    sma_source=input.string(title='Oscillator MA Type MACD', defval='EMA', options=('SMA', 'EMA'), group='MACD Fast'),
    sma_signal=input.string(title='Signal Line MA Type MACD', defval='EMA', options=('SMA', 'EMA'), group='MACD Fast')
):
    out = ta.sma(src, len)
    out2 = ta.ema(src, len2)
    ma = ta.sma(src, lengthk)
    rangema = ta.tr(True) if BandsStyle == 'True Range' else ta.atr(atrlength) if BandsStyle == 'Average True Range' else ta.rma(high - low, lengthk)
    upper = ma + rangema * mult
    lower = ma - rangema * mult
    k = ta.sma(ta.stoch(close, high, low, periodK), smoothK)
    d = ta.sma(k, periodD)
    fast_ma = ta.sma(src, fast_length) if sma_source == 'SMA' else ta.ema(src, fast_length)
    slow_ma = ta.sma(src, slow_length) if sma_source == 'SMA' else ta.ema(src, slow_length)
    macd = fast_ma - slow_ma
    signal = ta.sma(macd, signal_length) if sma_signal == 'SMA' else ta.ema(macd, signal_length)
    hist = macd - signal
    long = close > out and close < upper and (close > lower) and (hist < 0) and (k < 50) and (close > out2)
    short = close < out and close < upper and (close > lower) and (hist > 0) and (k > 50) and (close < out2)
    if long:
        strategy.entry('long', strategy.long)
    if short:
        strategy.entry('short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
