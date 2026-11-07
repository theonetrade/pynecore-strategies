"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, script, strategy, ta
from pynecore.types import Series


@script.strategy('Mov Avg Speed Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    src: Series[float] = input(close, title='Source'),
    avg_len=input.int(50, minval=1, title='Avg Length', group='MA Speed'),
    roc_len=input.int(1, minval=1, title='Rate of Change Length', group='MA Speed'),
    avg_roc_len=input.int(10, minval=1, title='Avg Rate of Change Length', group='MA Speed'),
    stoch_len=input.int(14, minval=1, title='Stochastic Length', group='Stochastic'),
    smooth_k=input.int(3, minval=1, title='Stochastic Smooth K', group='Stochastic'),
    overbought=input.float(80, title='Stochastic Overbought', group='Stochastic'),
    oversold=input.float(20, title='Stochastic Oversold', group='Stochastic'),
    fast_length=input(12, title='Fast Length', group='MACD'),
    slow_length=input(26, title='Slow Length', group='MACD'),
    macd_avg_length=input.int(9, title='MACD Avg Length', minval=1, group='MACD')
):
    avg = ta.sma(src, avg_len)
    roc = ta.roc(avg, roc_len)
    avg_roc = ta.sma(roc, avg_roc_len)
    avg_roc_signal = 1 if avg_roc > 0 else -1 if avg_roc < 0 else 0
    k = ta.sma(ta.stoch(close, high, low, stoch_len), smooth_k)
    stochastic_signal = 1 if k <= oversold else -1 if k >= overbought else 0
    fast_ma = ta.ema(src, fast_length)
    slow_ma = ta.ema(src, slow_length)
    macd = fast_ma - slow_ma
    macd_avg: Series = ta.ema(macd, macd_avg_length)
    macd_signal = 1 if macd_avg > macd_avg[1] else -1 if macd_avg < macd_avg[1] else 0
    long_count: int = 0
    short_count: int = 0
    if macd_signal == 1:
        long_count = long_count + 1
    elif macd_signal == -1:
        short_count = short_count + 1
    if stochastic_signal == 1:
        long_count = long_count + 1
    elif stochastic_signal == -1:
        short_count = short_count + 1
    if avg_roc_signal == 1:
        long_count = long_count + 1
    elif avg_roc_signal == -1:
        short_count = short_count + 1
    if long_count >= 2:
        strategy.entry('Long', strategy.long)
    if short_count >= 2:
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)