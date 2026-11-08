"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, extend, high, input, label, line, low, na, plot,
    script, size, ta
)
from pynecore.types import Label, Line, Series


@script.indicator('Extrapolated Pivot Connector', overlay=True, max_bars_back=5000, na_bool=True)
def main(
    length=input(100),
    astart=input(1, 'A-High Position'),
    aend=input(0, 'B-High Position'),
    bstart=input(1, 'A-Low Position'),
    bend=input(0, 'B-Low Position'),
    csrc=input(False, 'Use Custom Source ?'),
    src: Series[float] = input(close, 'Custom Source')
):
    up: Series = ta.pivothigh(src if csrc else high, length, length)
    dn: Series = ta.pivotlow(src if csrc else low, length, length)
    n: Series = bar_index
    a1 = ta.valuewhen(not na(up), n, astart)
    b1 = ta.valuewhen(not na(dn), n, bstart)
    a2 = ta.valuewhen(not na(up), n, aend)
    b2 = ta.valuewhen(not na(dn), n, bend)
    upper: Series[Line] = line.new(n[n - a1 + length], up[n - a1], n[n - a2 + length], up[n - a2], extend=extend.right, color=color.blue, width=2)
    lower: Series[Line] = line.new(n[n - b1 + length], dn[n - b1], n[n - b2 + length], dn[n - b2], extend=extend.right, color=color.orange, width=2)
    line.delete(upper[1])
    line.delete(lower[1])
    ahigh: Series[Label] = label.new(n[n - a1 + length], up[n - a1], 'A-High', color=color.blue, style=label.style_label_down, textcolor=color.white, size=size.small)
    bhigh: Series[Label] = label.new(n[n - a2 + length], up[n - a2], 'B-High', color=color.blue, style=label.style_label_down, textcolor=color.white, size=size.small)
    alow: Series[Label] = label.new(n[n - b1 + length], dn[n - b1], 'A-Low', color=color.orange, style=label.style_label_up, textcolor=color.white, size=size.small)
    blow: Series[Label] = label.new(n[n - b2 + length], dn[n - b2], 'B-Low', color=color.orange, style=label.style_label_up, textcolor=color.white, size=size.small)
    label.delete(ahigh[1])
    label.delete(bhigh[1])
    label.delete(alow[1])
    label.delete(blow[1])
    plot(up, "Pivot High's", color.new(color.blue, 0), 4, style=plot.style_circles, offset=-length, join=True)
    plot(dn, "Pivot Low's", color.new(color.orange, 0), 4, style=plot.style_circles, offset=-length, join=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)