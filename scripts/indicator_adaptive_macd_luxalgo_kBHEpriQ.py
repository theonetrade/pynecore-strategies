"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, chart, close, color, input, math, nz, plot, script, ta
from pynecore.types import Persistent, PersistentSeries, Series


@script.indicator('Adaptive MACD [LuxAlgo]', 'LuxAlgo - Adaptive MACD')
def main(
    length=input.int(20, 'R2 Period', minval=2),
    fast=input.int(10, minval=2),
    slow=input.int(20, minval=2),
    signal=input.int(9, minval=2)
):
    macd: PersistentSeries[float] = 0.0
    lag: Persistent = (signal - 1) / 2
    a1: Persistent = 2 / (fast + 1)
    a2: Persistent = 2 / (slow + 1)
    r2 = 0.5 * math.pow(ta.correlation(close, bar_index, length), 2) + 0.5
    K = r2 * (1 - a1) * (1 - a2) + (1 - r2) * ((1 - a1) / (1 - a2))
    macd = (close - close[1]) * (a1 - a2) + (-a2 - a1 + 2) * nz(macd[1]) - K * nz(macd[2])
    ema = ta.ema(macd, signal)
    hist: Series = macd - ema
    hist_css = color.new('#5B9CF6') if hist > 0 and hist > hist[1] else color.new(color.new('#5B9CF6'), 50) if hist > 0 and hist < hist[1] else color.new('#F77C80') if hist < 0 and hist < hist[1] else color.new(color.new('#F77C80'), 50)
    plot(hist, 'Histogram', hist_css, 1, plot.style_columns)
    plot(macd, 'MACD', chart.fg_color)
    plot(ema, 'Signal', color.new('#FF5D00'))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
