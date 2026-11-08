"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, low, open, plotcandle, request, script,
    syminfo, ticker, timeframe
)


@script.indicator('Heiken Ashi Candles', 'Heiken Ashi', overlay=True)
def main(
    isHA=input(True, 'HA Candles')
):
    heikenashi_1 = ticker.heikinashi(syminfo.tickerid)
    data = heikenashi_1 if isHA else syminfo.tickerid

    o = request.security(data, timeframe.period, open)
    h = request.security(data, timeframe.period, high)
    l = request.security(data, timeframe.period, low)
    c = request.security(data, timeframe.period, close)
    col = color.green if c > o else color.red

    plotcandle(o, h, l, c, 'Heiken Ashi', col, color.black)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
