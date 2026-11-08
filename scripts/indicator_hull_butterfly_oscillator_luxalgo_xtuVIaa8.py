"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    array, bar_index, barstate, chart, close, color, input, math, na, plot,
    script, ta
)
from pynecore.types import Persistent, PersistentSeries, Series


@script.indicator('Hull Butterfly Oscillator [LuxAlgo]', 'Hull Butterfly Oscillator [LuxAlgo]')
def main(
    length=input(14),
    mult=input(2.0, 'Levels Multiplier'),
    src: Series[float] = input(close),
    bull_css_0=input.color(color.new(color.new('#0CB51A'), 50), 'Bullish Gradient', inline='inline0', group='Style'),
    bull_css_1=input.color(color.new('#0CB51A'), '', inline='inline0', group='Style'),
    bear_css_0=input.color(color.new(color.new('#FF1100'), 50), 'Bearish Gradient', inline='inline1', group='Style'),
    bear_css_1=input.color(color.new('#FF1100'), '', inline='inline1', group='Style')
):
    short_len: Persistent = cast_int(length / 2)
    hull_len: Persistent = cast_int(math.sqrt(length))
    den1: Persistent = short_len * (short_len + 1) / 2
    den2: Persistent = length * (length + 1) / 2
    den3: Persistent = hull_len * (hull_len + 1) / 2
    lcwa_coeffs: Persistent[list[float]] = array.new_float(hull_len, 0)
    hull_coeffs: Persistent[list[float]] = array.new_float(0)
    if barstate.isfirst:
        for i in pine_range(0, length - 1, 1):
            sum1 = math.max(short_len - i, 0)
            sum2 = length - i
            array.unshift(lcwa_coeffs, 2 * (sum1 / den1) - sum2 / den2)
        for i in pine_range(0, hull_len - 2, 1):
            array.unshift(lcwa_coeffs, 0)
        for i in pine_range(hull_len, array.size(lcwa_coeffs) - 1, 1):
            sum3: float = 0.0
            for j in pine_range(i - hull_len, i - 1, 1):
                sum3 = sum3 + array.get(lcwa_coeffs, j) * (i - j)
            array.unshift(hull_coeffs, sum3 / den3)
    os: PersistentSeries[int] = 0
    len: Persistent = array.size(hull_coeffs) - 1
    hma: float = 0.0
    inv_hma: float = 0.0
    for i in pine_range(0, len, 1):
        hma = hma + src[i] * array.get(hull_coeffs, i)
        inv_hma = inv_hma + src[len - i] * array.get(hull_coeffs, i)
    hso: Series = hma - inv_hma
    cmean = ta.cum(math.abs(hso)) / bar_index * mult
    cross_1 = ta.cross(hso, -cmean)
    os = 0 if ta.cross(hso, cmean) or cross_1 else -1 if hso < hso[1] and hso > cmean else 1 if hso > hso[1] and hso < -cmean else os
    css0 = color.from_gradient(hso, 0, cmean, bull_css_0, bull_css_1)
    css1 = color.from_gradient(hso, -cmean, 0, bear_css_1, bear_css_0)
    css = css0 if hso > 0 else css1
    plot(hso, 'Hull Butterfly', css, style=plot.style_histogram)
    plot(hso, 'Hull Butterfly', chart.fg_color)
    plot(hso if os > os[1] and os == 1 else na, 'Bullish Dot', bull_css_1, 2, plot.style_circles)
    plot(hso if os < os[1] and os == -1 else na, 'Bearish Dot', bear_css_1, 2, plot.style_circles)
    plot(cmean, color=color.gray, editable=False)
    plot(cmean / 2, color=color.gray, editable=False)
    plot(-cmean / 2, color=color.gray, editable=False)
    plot(-cmean, color=color.gray, editable=False)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
