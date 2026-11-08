"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, fill, input, math, nz, plot, script, ta
from pynecore.types import Persistent, PersistentSeries, Series


@script.indicator('Moving Average Converging [LuxAlgo]', overlay=True)
def main(
    length=input(100),
    incr=input(10, 'Increment'),
    fast=input(10),
    src: Series[float] = input(close)
):
    ma: PersistentSeries[float] = 0.0
    fma: PersistentSeries[float] = 0.0
    alpha: PersistentSeries[float] = 0.0
    k: Persistent = 1 / incr
    upper: Series = ta.highest(length)
    lower: Series = ta.lowest(length)
    init_ma = ta.sma(src, length)
    cross = ta.cross(src, ma)
    alpha = 2 / (length + 1) if cross else alpha + k if src > ma and upper > upper[1] else alpha + k if src < ma and lower < lower[1] else alpha
    ma = nz(ma[1] + alpha[1] * (src - ma[1]), init_ma)
    fma = nz(math.avg(src, fma[1]) if cross else math.max(src, fma[1]) + (src - fma[1]) / fast if src > ma else math.min(src, fma[1]) + (src - fma[1]) / fast, src)
    css = color.teal if fma > ma else color.red
    plot0 = plot(fma, 'Fast MA', color=color.new('#FF5D00'))
    plot1 = plot(ma, 'Converging MA', color=css)
    fill(plot0, plot1, css, 'Fill')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
