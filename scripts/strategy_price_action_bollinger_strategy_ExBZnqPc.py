"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, math, open, script, strategy, ta
from pynecore.types import Series


@script.strategy(title='Price Action + Bollinger Strategy ', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    b_sma=input.int(21, minval=1, title=' SMA candle')
):
    bar: Series = 1 if close > open else -1 if close < open else 0
    body: Series = math.abs(close - open)
    avgbody = ta.sma(body, 100)
    b_sma_no_of_deviations: float = 2.1
    b_sma_signal = ta.sma(close, b_sma)
    b_sma_deviation = b_sma_no_of_deviations * ta.stdev(close, b_sma)
    b_sma_upper = b_sma_signal + b_sma_deviation
    b_sma_lower = b_sma_signal - b_sma_deviation
    up1: Series = body < body[1] / 2 and body[1] > avgbody * 2 and (bar[1] == 1) and (bar == -1) and (close[1] > b_sma_upper)
    dn1: Series = body < body[1] / 2 and body[1] > avgbody * 2 and (bar[1] == -1) and (bar == 1) and (close[1] < b_sma_lower)
    up2: Series[bool] = False
    dn2: Series[bool] = False
    up2 = (up1[1] or up2[1]) and close < close[1]
    dn2 = (dn1[1] or dn2[1]) and close > close[1]
    longCondition = dn1
    if longCondition:
        strategy.entry('Long Entry', strategy.long)
    shortCondition = up1
    if shortCondition:
        strategy.entry('Short Entry', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
