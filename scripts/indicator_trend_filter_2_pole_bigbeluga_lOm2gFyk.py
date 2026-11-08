"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method
from pynecore.lib import (
    barcolor, barstate, close, color, input, location, math, na, nz, plot,
    plotshape, script, shape, size, ta
)
from pynecore.types import Persistent, PersistentSeries, Series


@script.indicator("Trend Filter (2-pole) [BigBeluga]", overlay=True)
def main(
    length=input.int(20, "Length"),
    damping=input.float(0.9, "Damping", minval=0.1, maxval=1.0, step=0.01),
    ris_fal=input.int(5, "Rising and Falling"),
    bands=input.float(1.0, "Bands", step=0.1, minval=0.5),
    up_col=input.color(color.lime, "↑", inline="color"),
    dn_col=input.color(color.red, "↓", inline="color"),
    __col=input.color(color.yellow, "〜", inline="color"),
    bar_col=input.bool(False, "BarColor", inline="Features"),
    signals=input.bool(False, "Signals", inline="Features")
):
    atr = ta.atr(200) * bands

    @method
    def two_pole_filter(src: float, length: int, damping: float):
        omega: float = 2.0 * math.pi / length
        alpha: float = damping * omega
        beta: float = math.pow(omega, 2)

        f1: PersistentSeries[float] = na(float)
        f2: PersistentSeries[float] = na(float)

        f1 = nz(f1[1]) + alpha * (src - nz(f1[1]))
        f2 = nz(f2[1]) + beta * (f1 - nz(f2[1]))

        return f2

    tp_f: Series = two_pole_filter(close, length, damping)

    rising: Persistent[int] = 0
    falling: Persistent[int] = 0

    up = tp_f > tp_f[2]
    dn = tp_f < tp_f[2]

    if up:
        rising += 1
        falling = 0

    if dn:
        rising = 0
        falling += 1

    color__ren__ = color.from_gradient(rising, 0, 15, __col, up_col) if up else color.from_gradient(falling, 0, 15, __col, dn_col) if dn else __col

    plot(tp_f, 'Two-Pole Filter', color=color__ren__, linewidth=3)

    plotshape(tp_f + atr if falling >= ris_fal else na, 'Falling', shape.circle, location.absolute, color=color__ren__)
    plotshape(tp_f - atr if rising >= ris_fal else na, 'Rising', shape.circle, location.absolute, color=color__ren__)

    sig_up: bool = ta.crossover(rising, ris_fal) and barstate.isconfirmed and signals
    sig_dn: bool = ta.crossover(falling, ris_fal) and barstate.isconfirmed and signals

    plotshape(tp_f[1] + atr if sig_dn else na, 'Falling', shape.triangledown, location.absolute, color=color__ren__, size=size.tiny, offset=-1)
    plotshape(tp_f[1] - atr if sig_up else na, 'Rising', shape.triangleup, location.absolute, color=color__ren__, size=size.tiny, offset=-1)

    barcolor(color__ren__ if bar_col else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
