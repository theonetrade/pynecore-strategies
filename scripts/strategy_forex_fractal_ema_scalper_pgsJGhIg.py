"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import high, hl2, input, low, script, strategy, ta
from pynecore.types import Series


@script.strategy('Forex Fractal EMA Scalper', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    n=input.int(title='Period Fractals', defval=2, minval=2, group='Optimization Parameters'),
    src: Series[float] = input(hl2, title='Source for EMA\'s', group='Optimization Parameters'),
    len1=input.int(10, minval=1, title='Length EMA 1', group='Optimization Parameters'),
    len2=input.int(20, minval=1, title='Length EMA 2', group='Optimization Parameters'),
    len3=input.int(100, minval=1, title='Length EMA 3', group='Optimization Parameters'),
    __input_5__=input(25, title='TP in PIPS', group='Risk Management'),
    __input_6__=input(25, title='SL in PIPS', group='Risk Management')
):
    out1 = ta.ema(src, len1)
    out2 = ta.ema(src, len2)
    out3 = ta.ema(src, len3)
    upflagDownFrontier: bool = True
    upflagUpFrontier0: bool = True
    upflagUpFrontier1: bool = True
    upflagUpFrontier2: bool = True
    upflagUpFrontier3: bool = True
    upflagUpFrontier4: bool = True
    for i in pine_range(1, n, 1):
        upflagDownFrontier = upflagDownFrontier and high[n - i] < high[n]
        upflagUpFrontier0 = upflagUpFrontier0 and high[n + i] < high[n]
        upflagUpFrontier1 = upflagUpFrontier1 and high[n + 1] <= high[n] and (high[n + i + 1] < high[n])
        upflagUpFrontier2 = upflagUpFrontier2 and high[n + 1] <= high[n] and (high[n + 2] <= high[n]) and (high[n + i + 2] < high[n])
        upflagUpFrontier3 = upflagUpFrontier3 and high[n + 1] <= high[n] and (high[n + 2] <= high[n]) and (high[n + 3] <= high[n]) and (high[n + i + 3] < high[n])
        upflagUpFrontier4 = upflagUpFrontier4 and high[n + 1] <= high[n] and (high[n + 2] <= high[n]) and (high[n + 3] <= high[n]) and (high[n + 4] <= high[n]) and (high[n + i + 4] < high[n])
    flagUpFrontier = upflagUpFrontier0 or upflagUpFrontier1 or upflagUpFrontier2 or upflagUpFrontier3 or upflagUpFrontier4
    upFractal = upflagDownFrontier and flagUpFrontier
    downflagDownFrontier: bool = True
    downflagUpFrontier0: bool = True
    downflagUpFrontier1: bool = True
    downflagUpFrontier2: bool = True
    downflagUpFrontier3: bool = True
    downflagUpFrontier4: bool = True
    for i in pine_range(1, n, 1):
        downflagDownFrontier = downflagDownFrontier and low[n - i] > low[n]
        downflagUpFrontier0 = downflagUpFrontier0 and low[n + i] > low[n]
        downflagUpFrontier1 = downflagUpFrontier1 and low[n + 1] >= low[n] and (low[n + i + 1] > low[n])
        downflagUpFrontier2 = downflagUpFrontier2 and low[n + 1] >= low[n] and (low[n + 2] >= low[n]) and (low[n + i + 2] > low[n])
        downflagUpFrontier3 = downflagUpFrontier3 and low[n + 1] >= low[n] and (low[n + 2] >= low[n]) and (low[n + 3] >= low[n]) and (low[n + i + 3] > low[n])
        downflagUpFrontier4 = downflagUpFrontier4 and low[n + 1] >= low[n] and (low[n + 2] >= low[n]) and (low[n + 3] >= low[n]) and (low[n + 4] >= low[n]) and (low[n + i + 4] > low[n])
    flagDownFrontier = downflagUpFrontier0 or downflagUpFrontier1 or downflagUpFrontier2 or downflagUpFrontier3 or downflagUpFrontier4
    downFractal = downflagDownFrontier and flagDownFrontier
    long = out1 > out2 and out2 > out3 and upFractal
    short = out1 < out2 and out2 < out3 and downFractal
    if short:
        strategy.entry('long', strategy.long)
    if long:
        strategy.entry('short', strategy.short)
    tp = __input_5__ * 10
    sl = __input_6__ * 10
    strategy.exit('X_long', 'long', profit=tp, loss=sl)
    strategy.exit('x_short', 'short', profit=tp, loss=sl)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
