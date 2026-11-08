"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, barcolor, close, color, fill, input, location, math, nz,
    plot, plotshape, script, shape, size, ta
)
from pynecore.types import Color, NA, Series


@script.indicator(title='Range Filter Buy and Sell 5min', shorttitle='Range Filter', overlay=True)
def main(
    src: Series[float] = input(defval=close, title='Source'),
    per=input.int(defval=100, minval=1, title='Sampling Period'),
    mult=input.float(defval=3.0, minval=0.1, title='Range Multiplier')
):
    upColor = color.white
    midColor: Color = color.new('#90BFF9')
    downColor = color.blue
    def smoothrng(x: Series, t, m):
        wper = t * 2 - 1
        avrng = ta.ema(math.abs(x - x[1]), t)
        smoothrng__00000009__ = ta.ema(avrng, wper) * m
        return smoothrng__00000009__

    smrng = smoothrng(src, per, mult)
    def rngfilt(x, r):
        rngfilt__00000015__: Series = x
        rngfilt__00000015__ = (nz(rngfilt__00000015__[1]) if x - r < nz(rngfilt__00000015__[1]) else x - r) if x > nz(rngfilt__00000015__[1]) else nz(rngfilt__00000015__[1]) if x + r > nz(rngfilt__00000015__[1]) else x + r
        return rngfilt__00000015__

    filt: Series = rngfilt(src, smrng)
    upward: Series[float] = 0.0
    upward = nz(upward[1]) + 1 if filt > filt[1] else 0 if filt < filt[1] else nz(upward[1])
    downward: Series[float] = 0.0
    downward = nz(downward[1]) + 1 if filt < filt[1] else 0 if filt > filt[1] else nz(downward[1])
    hband = filt + smrng
    lband = filt - smrng
    filtcolor = upColor if upward > 0 else downColor if downward > 0 else midColor
    barcolor__ren__ = upColor if src > filt and src > src[1] and (upward > 0) else upColor if src > filt and src < src[1] and (upward > 0) else downColor if src < filt and src < src[1] and (downward > 0) else downColor if src < filt and src > src[1] and (downward > 0) else midColor
    filtplot = plot(filt, color=filtcolor, linewidth=2, title='Range Filter')
    hbandplot = plot(hband, color=color.new(upColor, 70), title='High Target')
    lbandplot = plot(lband, color=color.new(downColor, 70), title='Low Target')
    fill(hbandplot, filtplot, color=color.new(upColor, 90), title='High Target Range')
    fill(lbandplot, filtplot, color=color.new(downColor, 90), title='Low Target Range')
    barcolor(barcolor__ren__)
    longCond = NA(bool)
    shortCond = NA(bool)
    longCond = src > filt and src > src[1] and (upward > 0) or (src > filt and src < src[1] and (upward > 0))
    shortCond = src < filt and src < src[1] and (downward > 0) or (src < filt and src > src[1] and (downward > 0))
    CondIni: Series[int] = 0
    CondIni = 1 if longCond else -1 if shortCond else CondIni[1]
    longCondition = longCond and CondIni[1] == -1
    shortCondition = shortCond and CondIni[1] == 1
    plotshape(longCondition, title='Buy Signal', text='Buy', textcolor=color.white, style=shape.labelup, size=size.small, location=location.belowbar, color=color.new(color.new('#AAAAAA'), 20))
    plotshape(shortCondition, title='Sell Signal', text='Sell', textcolor=color.white, style=shape.labeldown, size=size.small, location=location.abovebar, color=color.new(downColor, 20))
    alertcondition(longCondition, title='Buy alert on Range Filter', message='Buy alert on Range Filter')
    alertcondition(shortCondition, title='Sell alert on Range Filter', message='Sell alert on Range Filter')
    alertcondition(longCondition or shortCondition, title='Buy and Sell alert on Range Filter', message='Buy and Sell alert on Range Filter')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
