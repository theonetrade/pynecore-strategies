"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import close, color, fill, hline, input, math, nz, plot, script, ta
from pynecore.types import Series


@script.indicator(title='RSI cyclic smoothed', shorttitle='cRSI', na_bool=True)
def main(
    domcycle=input.int(20, minval=10, title='Dominant Cycle Length')
):
    src = close
    crsi: Series[float] = 0.0
    cyclelen = domcycle / 2
    vibration: int = 10
    leveling: float = 10.0
    cyclicmemory = domcycle * 2
    h1 = hline(30, color=color.silver, linestyle=hline.style_dashed)
    h2 = hline(70, color=color.silver, linestyle=hline.style_dashed)
    torque = 2.0 / (vibration + 1)
    phasingLag = (vibration - 1) / 2.0
    up = ta.rma(math.max(ta.change(src), 0), cyclelen)
    down = ta.rma(-math.min(ta.change(src), 0), cyclelen)
    rsi: Series = 100 if down == 0 else 0 if up == 0 else 100 - 100 / (1 + up / down)
    crsi = torque * (2 * rsi - rsi[phasingLag]) + (1 - torque) * nz(crsi[1])
    lmax = -999999.0
    lmin: float = 999999.0
    for i in pine_range(0, cyclicmemory - 1, 1):
        if nz(crsi[i], -999999.0) > lmax:
            lmax = nz(crsi[i])
        else:
            if nz(crsi[i], 999999.0) < lmin:
                lmin = nz(crsi[i])
    mstep = (lmax - lmin) / 100
    aperc = leveling / 100
    db: float = 0.0
    for steps in pine_range(0, 100, 1):
        testvalue = lmin + mstep * steps
        above: int = 0
        below: int = 0
        for m in pine_range(0, cyclicmemory - 1, 1):
            below = below + (1 if crsi[m] < testvalue else 0)
        ratio = below / cyclicmemory
        if ratio >= aperc:
            db = testvalue
            break
        else:
            continue
    ub: float = 0.0
    for steps in pine_range(0, 100, 1):
        testvalue = lmax - mstep * steps
        above: int = 0
        for m in pine_range(0, cyclicmemory - 1, 1):
            above = above + (1 if crsi[m] >= testvalue else 0)
        ratio = above / cyclicmemory
        if ratio >= aperc:
            ub = testvalue
            break
        else:
            continue
    lowband = plot(db, 'LowBand', color.new(color.aqua, 0))
    highband = plot(ub, 'HighBand', color.new(color.aqua, 0))
    fill(h1, h2, color=color.new(color.silver, 90))
    fill(lowband, highband, color=color.new(color.gray, 90))
    plot(crsi, 'CRSI', color.new(color.fuchsia, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)