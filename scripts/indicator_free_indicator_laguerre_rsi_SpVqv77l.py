"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, high, input, low, nz, open, plot, script, ta
from pynecore.types import Series


@script.indicator('laguerre RSI v4 | LK', overlay=False, na_bool=True)
def main(
    g=input(0.75, title='Gamma'),
    ob=input(0.8, title='Over Bought'),
    os=input(0.2, title='Over Sold'),
    smooth=input.int(1, minval=1, title='Smoothing (1 = off)'),
    coloring=input(True, title='3 colors?')
):
    h = high
    l = low
    o = open
    c = close
    p = c
    L0: Series[float] = 0.0
    L1: Series[float] = 0.0
    L2: Series[float] = 0.0
    L3: Series[float] = 0.0
    L0 = (1 - g) * p + g * nz(L0[1])
    L1 = -g * L0 + nz(L0[1]) + g * nz(L1[1])
    L2 = -g * L1 + nz(L1[1]) + g * nz(L2[1])
    L3 = -g * L2 + nz(L2[1]) + g * nz(L3[1])
    cu = (L0 - L1 if L0 > L1 else 0) + (L1 - L2 if L1 > L2 else 0) + (L2 - L3 if L2 > L3 else 0)
    cd = (L1 - L0 if L0 < L1 else 0) + (L2 - L1 if L1 < L2 else 0) + (L3 - L2 if L2 < L3 else 0)
    lrsi: Series = ta.ema(0 if (-1 if cu + cd == 0 else cu + cd) == -1 else cu / (-1 if cu + cd == 0 else cu + cd), smooth)
    col1 = color.new('#00FF7B') if lrsi > lrsi[1] and lrsi > os else color.new('#FF3571') if lrsi < lrsi[1] and lrsi < ob else color.new('#ECA700') if lrsi == lrsi else color.new('#ECA700')
    col2 = color.new('#00FF7B') if lrsi > lrsi[1] and lrsi > os else color.new('#FF3571') if lrsi < lrsi[1] and lrsi < ob else color.new('#FF3571') if lrsi < os else color.new('#00FF7B') if lrsi > ob else color.new('#ECA700') if lrsi == lrsi else color.new('#ECA700')
    col = col1 if coloring else col2
    plot(lrsi, color=col, linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
