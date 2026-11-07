"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, fill, input, math, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy("Peri Bollinger Mean Reversion V2", overlay=True)
def main(
    source: Series[float] = input.source(close, "Source"),
    length=input.int(20, "BB Length", minval=1),
    mult=input.float(2.0, "BB Multiplier", minval=0.001, maxval=50.0),
    rsiOversold=input.int(30, "RSI Oversold Level", minval=1, maxval=50),
    rsiOverbought=input.int(70, "RSI Overbought Level", minval=50, maxval=99)
):
    basis = ta.sma(source, length)
    dev = mult * ta.stdev(source, length)
    upper = basis + dev
    lower = basis - dev

    strength = ta.rsi(close, 14)

    pbasis = plot(basis, 'Middle BB')
    p1 = plot(upper, 'Upper BB')
    p2 = plot(lower, 'Lower BB')
    fill(p1, p2)

    amount = 0.1 * (strategy.initial_capital + strategy.netprofit)
    units = math.floor(amount / close)

    if close < lower and strength < rsiOversold and (strategy.position_size < units * 5):
        strategy.order('Long', strategy.long, units)

    if close > upper and strength > 50 and (strategy.position_size > 0):
        strategy.close('Long', comment='Close Long')

    if close > upper and strength > rsiOverbought and (strategy.position_size > -units * 5):
        strategy.order('Short', strategy.short, units)

    if strategy.position_size < 0 and close <= basis:
        strategy.close('Short', comment='Close Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)