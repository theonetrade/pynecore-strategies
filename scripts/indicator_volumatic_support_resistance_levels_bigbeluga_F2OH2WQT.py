"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, color, fill, high, input, location, low, na, plot, plotshape,
    script, shape, size, ta, volume
)
from pynecore.types import Color, NA, Persistent, PersistentSeries, Series


@script.indicator("Volumatic Support/Resistance Levels [BigBeluga]", overlay=True)
def main(
    length=input.int(25, "Length"),
    upper_threshold=input.int(80, "Resistance Max Volume %", maxval=100, minval=50, inline="sup"),
    sup_col=input.color(color.rgb(28, 194, 114), "", inline="sup"),
    lower_threshold=input.int(80, "Support Max Volume %", maxval=100, minval=50, inline="res"),
    res_col=input.color(color.rgb(206, 37, 37), "", inline="res"),
    bars_threshold=input.int(50, "Bars Max Volume %", maxval=100, minval=50, inline="bar"),
    bar_col=input.color(color.rgb(255, 145, 55), "", inline="bar")
):
    upper1: PersistentSeries = NA(float)
    upper2: Persistent = NA(float)
    lower1: PersistentSeries = NA(float)
    lower2: Persistent = NA(float)

    h: Series = ta.highest(length)
    l: Series = ta.lowest(length)

    n_vol = volume / ta.percentile_linear_interpolation(volume, 500, 100) * 100

    if h[1] == high[1] and high < h:
        upper1 = h
        upper2 = h

    if l[1] == low[1] and low > l:
        lower1 = l
        lower2 = l

    atr = ta.atr(200) / 100
    upper_col = NA(Color) if upper1 != upper1[1] else res_col
    lower_col = NA(Color) if lower1 != lower1[1] else sup_col

    plot(upper1, 'Resistance', color=upper_col)
    ph1 = plot(upper1 + atr * n_vol, color=na, editable=False)
    ph2 = plot(upper2 - atr * n_vol, color=na, editable=False)

    upper_fill = na if upper1 != upper1[1] else color.from_gradient(n_vol, 0, 100, color.new(res_col, 80), res_col)

    fill(ph1, ph2, upper_fill)

    plot(lower1, 'Support', color=lower_col)
    pl1 = plot(lower2 + atr * n_vol, color=na, editable=False)
    pl2 = plot(lower2 - atr * n_vol, color=na, editable=False)

    lower_fill = na if lower1 != lower1[1] else color.from_gradient(n_vol, 0, 100, color.new(sup_col, 80), sup_col)

    fill(pl1, pl2, lower_fill)

    plotshape(lower2 - atr * n_vol if n_vol > lower_threshold else NA(float), 'Max Volume Support', shape.circle, location.absolute, color=sup_col, size=size.tiny)
    plotshape(lower2 + atr * n_vol if n_vol > lower_threshold else NA(float), 'Max Volume Support', shape.circle, location.absolute, color=sup_col, size=size.tiny)

    plotshape(upper2 + atr * n_vol if n_vol > upper_threshold else NA(float), 'Max Volume Resistance', shape.circle, location.absolute, color=res_col, size=size.tiny)
    plotshape(upper2 - atr * n_vol if n_vol > upper_threshold else NA(float), 'Max Volume Resistance', shape.circle, location.absolute, color=res_col, size=size.tiny)

    barcolor(bar_col if n_vol > bars_threshold else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)