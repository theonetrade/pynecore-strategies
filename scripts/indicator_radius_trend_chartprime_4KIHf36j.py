"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, chart, close, color, display, fill, high, hl2, input, low,
    math, na, plot, script, ta
)
from pynecore.types import Persistent, Series


@script.indicator('Radius Trend [ChartPrime]', overlay=True, na_bool=True)
def main(
    step=input.float(0.15, 'Radius Step', step=0.001),
    multi=input.float(2, 'Start Points Distance', step=0.1)
):
    trend: Series[bool] = na(bool)
    multi1: Persistent[float] = 0.0
    multi2: Persistent[float] = 0.0
    n: int = 3
    band: Persistent[float] = 0.0
    distance: float = ta.sma(math.abs(high - low), 100) * multi
    distance1: float = ta.sma(math.abs(high - low), 100) * 0.2
    if bar_index == 101:
        trend = True
        band = low * 0.8
    if close < band:
        trend = False
    if close > band:
        trend = True
    change_1 = ta.change(trend)
    if trend[1] == False and change_1:
        band = low - distance
    change_2 = ta.change(trend)
    if trend[1] == True and change_2:
        band = high + distance
    if bar_index % n == 0 and trend:
        multi1 = 0
        multi2 = multi2 + step
        band = band + distance1 * multi2
    if bar_index % n == 0 and (not trend):
        multi1 = multi1 + step
        multi2 = 0
        band = band - distance1 * multi1
    Sband = ta.sma(band, n)
    color__ren__ = color.new('#54B6D4') if trend else color.new('#CF2B2B')
    band_upper = ta.sma(band + distance * 0.5, n)
    band_lower = ta.sma(band - distance * 0.5, n)
    band1 = band_upper if trend else band_lower
    plot(band1, color=color.new(chart.fg_color, 50) if bar_index % 2 == 0 else na)
    p1 = plot(na if ta.change(trend) else Sband, style=plot.style_linebr, color=color.gray)
    p2 = plot(ta.sma(hl2, 20), display=display.none)
    fill(p1, p2, band, ta.sma(hl2, 20), color.new(color__ren__, 60), na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
