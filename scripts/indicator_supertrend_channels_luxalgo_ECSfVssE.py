"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, fill, hl2, input, math, na, nz, plot, script, ta
from pynecore.types import Persistent, Series


@script.indicator('Supertrend Channels [LuxAlgo]', overlay=True, max_lines_count=500)
def main(
    length=input(14),
    mult=input(2)
):
    upper: Series[float] = 0.0
    lower: Series[float] = 0.0
    os: Series[int] = 0
    max: Series[float] = 0.0
    min: Series[float] = 0.0
    src: Series = close
    atr = ta.atr(length) * mult
    up = hl2 + atr
    dn = hl2 - atr
    upper = math.min(up, upper[1]) if src[1] < upper[1] else up
    lower = math.max(dn, lower[1]) if src[1] > lower[1] else dn
    os = 1 if src > upper else 0 if src < lower else os[1]
    spt = lower if os == 1 else upper
    max = nz(math.max(max[1], src), src) if ta.cross(src, spt) else math.max(src, max[1]) if os == 1 else math.min(spt, max[1])
    min = nz(math.min(min[1], src), src) if ta.cross(src, spt) else math.min(src, min[1]) if os == 0 else math.max(spt, min[1])
    avg = math.avg(max, min)
    area_up_col: Persistent = color.new(color.new('#0CB51A'), 80)
    area_dn_col: Persistent = color.new(color.new('#FF1100'), 80)
    plot0 = plot(max, 'Upper Channel', na if max != max[1] and os == 1 else color.new('#0CB51A'))
    plot1 = plot(avg, 'Average', color.new('#FF5D00'))
    plot2 = plot(min, 'Lower Channel', na if min != min[1] and os == 0 else color.new('#FF1100'))
    fill(plot0, plot1, area_up_col, 'Upper Area')
    fill(plot1, plot2, area_dn_col, 'Lower Area')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
