"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, fill, input, location, plot, plotshape,
    script, shape, size, ta
)
from pynecore.types import Series


@script.indicator(shorttitle='BBSR Extreme', title='Bollinger Bands Stochastic RSI Extreme Signal', overlay=True, timeframe='', na_bool=True)
def main(
    src: Series[float] = input(close, title='Source'),
    offset=input.int(0, 'Offset', minval=-500, maxval=500),
    length=input.int(20, title='Bollinger Band Length', minval=1),
    mult=input.float(2.0, minval=0.001, maxval=50, title='StdDev'),
    smoothK=input.int(3, 'K', minval=1),
    smoothD=input.int(3, 'D', minval=1),
    lengthRSI=input.int(14, 'RSI Length', minval=1),
    lengthStoch=input.int(14, 'Stochastic Length', minval=1),
    upperlimit=input.float(90, 'Upper Limit', minval=0.01),
    lowerlimit=input.float(10, 'Upper Limit', minval=0.01)
):
    basis = ta.sma(src, length)
    dev = mult * ta.stdev(src, length)
    upper: Series = basis + dev
    lower: Series = basis - dev
    plot(basis, 'BB Basis', color=color.new(color.new('#872323'), 0), offset=offset)
    p1 = plot(upper, 'BB Upper', color=color.new(color.teal, 0), offset=offset)
    p2 = plot(lower, 'BB Lower', color=color.new(color.teal, 0), offset=offset)
    fill(p1, p2, title='BB Background', color=color.new(color.new('#198787'), 95))
    rsi1 = ta.rsi(src, lengthRSI)
    k: Series = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
    d: Series = ta.sma(k, smoothD)
    Bear = close[1] > upper[1] and close < upper and (k[1] > upperlimit) and (d[1] > upperlimit)
    Bull = close[1] < lower[1] and close > lower and (k[1] < lowerlimit) and (d[1] < lowerlimit)
    plotshape(Bear, style=shape.triangledown, location=location.abovebar, color=color.new(color.red, 0), size=size.tiny)
    plotshape(Bull, style=shape.triangleup, location=location.belowbar, color=color.new(color.green, 0), size=size.tiny)
    alertcondition(Bear or Bull, title='Any Signal', message='{{exchange}}:{{ticker}}' + ' {{interval}}' + ' BB Stochastic Extreme!')
    alertcondition(Bear, title='Bearish Signal', message='{{exchange}}:{{ticker}}' + ' {{interval}}' + ' Bearish BB Stochastic Extreme!')
    alertcondition(Bull, title='Bullish Signal', message='{{exchange}}:{{ticker}}' + ' {{interval}}' + ' Bullish BB Stochastic Extreme!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
