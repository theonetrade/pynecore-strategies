"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, fill, hl2, hlc3, input, location, math, na,
    nz, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator('IDEAL BB with MA (With Alerts) by Adarsh', overlay=True, na_bool=True)
def main(
    length1=input.int(title='1st Length', minval=1, defval=120),
    length2=input.int(title='2nd Length', minval=1, defval=12),
    maInput=input.string(title='MA Type', defval='EMA', options=('EMA', 'SMA', 'VWMA', 'WMA')),
    src: Series[float] = input(title='Source', defval=hl2),
    lenvwap=input.int(1, minval=1, title='VWAP Length'),
    src1a: Series[float] = input(close, title='VWAP Source'),
    offsetvwap=input.int(title='VWAP Offset', defval=0, minval=-500, maxval=500),
    srchull: Series[float] = input(hl2, 'Price Data'),
    lengthhull=input(24, 'Lookback'),
    showcross=input(True, 'Show cross over/under'),
    gain=input(10000, 'Gain'),
    k=input(True, 'Use Kahlman')
):
    def getMA(src, length):
        ma: float = 0.0
        if maInput == 'EMA':
            ma = ta.ema(src, length)
        if maInput == 'SMA':
            ma = ta.sma(src, length)
        if maInput == 'VWMA':
            ma = ta.vwma(src, length)
        if maInput == 'WMA':
            ma = ta.wma(src, length)
        return ma

    def getNMA(src, length1, length2):
        lambda__ren__ = length1 / length2
        alpha = lambda__ren__ * (length1 - 1) / (length1 - lambda__ren__)
        ma1 = getMA(src, length1)
        ma2 = getMA(ma1, length2)
        nma = (1 + alpha) * ma1 - alpha * ma2
        return nma

    nma = getNMA(src, length1, length2)
    plot(nma, title='NMA Black Line', linewidth=2, style=plot.style_stepline, color=color.new(color.black, 0))
    srcvwap = hlc3
    vvwap = ta.vwap(srcvwap)
    line1 = ta.sma(src1a, lenvwap)
    plot(vvwap, color=color.new(color.new('#E91E63'), 0), linewidth=2, style=plot.style_line, title='VWAP MIDDLE')
    emaSource = close
    emaPeriod: int = 20
    devMultiple: int = 2
    baseline = ta.sma(emaSource, emaPeriod)
    plot(baseline, title='BB Red Line', color=color.new(color.red, 0))
    stdDeviation = devMultiple * ta.stdev(emaSource, emaPeriod)
    upperBand = baseline + stdDeviation
    lowerBand = baseline - stdDeviation
    p1 = plot(upperBand, title='BB Top', color=color.new(color.blue, 0))
    p2 = plot(lowerBand, title='BB Bottom', color=color.new(color.new('#311B92'), 0))
    fill(p1, p2, color=color.new(color.blue, 90))
    def hma(_srchull, _lengthhull):
        return ta.wma(2 * ta.wma(_srchull, _lengthhull / 2) - ta.wma(_srchull, _lengthhull), math.round(math.sqrt(_lengthhull)))

    def hma3(_srchull, _lengthhull):
        p = lengthhull / 2
        return ta.wma(ta.wma(close, p / 3) * 3 - ta.wma(close, p / 2) - ta.wma(close, p), p)

    def kahlman(x, g):
        kf: Series[float] = 0.0
        dk = x - nz(kf[1], x)
        smooth = nz(kf[1], x) + dk * math.sqrt(g / 10000 * 2)
        velo: Series[float] = 0.0
        velo = nz(velo[1], 0) + g / 10000 * dk
        kf = smooth + velo
        return kf

    a: Series = kahlman(hma(srchull, lengthhull), gain) if k else hma(srchull, lengthhull)
    b: Series = kahlman(hma3(srchull, lengthhull), gain) if k else hma3(srchull, lengthhull)
    c = color.lime if b > a else color.red
    crossdn = a > b and a[1] < b[1]
    crossup = b > a and b[1] < a[1]
    p1hma = plot(a, color=c, linewidth=1, title='Long Plot')
    p2hma = plot(b, color=c, linewidth=1, title='Short Plot')
    fill(p1hma, p2hma, color=color.new(c, 55), title='Fill')
    plotshape(a if showcross and crossdn else na, location=location.abovebar, style=shape.labeldown, color=color.new(color.red, 0), size=size.tiny, text='Sell', textcolor=color.new(color.white, 0), offset=-1)
    plotshape(a if showcross and crossup else na, location=location.belowbar, style=shape.labelup, color=color.new(color.green, 0), size=size.tiny, text='Buy', textcolor=color.new(color.white, 0), offset=-1)
    alertcondition(crossup, title='Buy', message='Go Long')
    alertcondition(crossdn, title='Sell', message='Go Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
