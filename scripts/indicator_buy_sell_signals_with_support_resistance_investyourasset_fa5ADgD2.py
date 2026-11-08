"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, dayofmonth, high, hline, input, location, low, month, na,
    plot, plotshape, request, script, shape, size, ta, time, timestamp, year
)
from pynecore.types import Persistent


@script.indicator('buy/sell signals with Support/Resistance (InvestYourAsset)', overlay=True)
def main(
    ma1=input(12, title='Short MA Period'),
    ma2=input(26, title='Long MA Period'),
    symbol=input('NA', title='Ticker Symbol'),
    lookback=input(20, title='Lookback Period for S&R')
):
    data = request.security(symbol, 'D', close)
    filteredClose: Persistent[float] = na(float)
    if time >= timestamp(year, month, dayofmonth, 0, 0) and time <= timestamp(year, month, dayofmonth, 23, 59):
        filteredClose = close
    short_ma = ta.sma(filteredClose, ma1)
    long_ma = ta.sma(filteredClose, ma2)
    macd_line = short_ma - long_ma
    positions = ta.crossover(short_ma, long_ma)
    signals = 1 if positions else -1 if ta.crossunder(short_ma, long_ma) else 0
    swingHigh = ta.pivothigh(high, lookback, lookback)
    swingLow = ta.pivotlow(low, lookback, lookback)
    plot(data, color=color.blue, title='Close Price')
    plotshape(signals == 1, style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small, title='Long Signal')
    plotshape(signals == -1, style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small, title='Short Signal')
    hline(0, 'Zero Line', color=color.gray)
    plot(macd_line, color=color.red, title='MACD Oscillator', style=plot.style_histogram, linewidth=1)
    plot(short_ma, color=color.orange, title='Short MA')
    plot(long_ma, color=color.purple, title='Long MA')
    plot(swingHigh, color=color.red, style=plot.style_stepline_diamond, linewidth=2, title='Swing High')
    plot(swingLow, color=color.green, style=plot.style_stepline_diamond, linewidth=2, title='Swing Low')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
