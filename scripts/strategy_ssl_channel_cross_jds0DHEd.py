"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, high, input, low, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy('SSL Channel Cross', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    period=input(title='Period', defval=10),
    len=input(title='Period', defval=10)
):
    smaHigh = ta.sma(high, len)
    smaLow = ta.sma(low, len)
    Hlv: Series[int] = 0
    Hlv = 1 if close > smaHigh else -1 if close < smaLow else Hlv[1]
    sslDown = smaHigh if Hlv < 0 else smaLow
    sslUp = smaLow if Hlv < 0 else smaHigh
    plot(sslDown, linewidth=2, color=color.new(color.red, 0))
    plot(sslUp, linewidth=2, color=color.new(color.lime, 0))
    longCondition = ta.crossover(sslUp, sslDown)
    shortCondition = ta.crossunder(sslUp, sslDown)
    if longCondition:
        if strategy.long:
            strategy.close('Short')
        strategy.entry('Long', strategy.long)
    if shortCondition:
        if strategy.long:
            strategy.close('Long')
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
