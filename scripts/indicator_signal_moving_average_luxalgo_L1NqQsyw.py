"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import bar_index, close, color, display, fill, input, math, nz, plot, script, ta
from pynecore.types import Persistent, PersistentSeries, Series


@script.indicator('Signal Moving Average [LuxAlgo]', overlay=True)
def main(
    length=input(50),
    src: Series[float] = input(close)
):
    ma: PersistentSeries[float] = 0.0
    os: Persistent[float] = 0.0
    target: Series = ta.sma(src, length)
    abs_diff = math.abs(target - target[1])
    r2 = math.pow(ta.correlation(close, bar_index, length), 2)
    os = math.sign(src[1] - target[1]) if r2 > 0.5 else os
    ma = r2 * target + (1 - r2) * nz(ma[1], target) if r2 > 0.5 else ma[1] - abs_diff * os
    plot0 = plot(src, display=display.none, editable=False)
    css = color.new('#0CB51A') if os == 1 else color.new('#FF1100')
    plot1 = plot(ma, 'Signal MA', css)
    fill_css = color.new(color.new('#0CB51A'), 80) if src > ma else color.new(color.new('#FF1100'), 80)
    fill(plot0, plot1, fill_css, 'Fill')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
