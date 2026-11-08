"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, fill, input, location, math, na, nz, ohlc4,
    plot, plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator(title='Twin Range Filter', overlay=True, timeframe='')
def main(
    source: Series[float] = input(defval=close, title='Source'),
    showsignals=input(title='Show Buy/Sell Signals ?', defval=True),
    per1=input.int(defval=27, minval=1, title='Fast period'),
    mult1=input.float(defval=1.6, minval=0.1, title='Fast range'),
    per2=input.int(defval=55, minval=1, title='Slow period'),
    mult2=input.float(defval=2, minval=0.1, title='Slow range')
):
    def smoothrng(x: Series, t, m):
        wper = t * 2 - 1
        avrng = ta.ema(math.abs(x - x[1]), t)
        smoothrng__0000000c__ = ta.ema(avrng, wper) * m
        return smoothrng__0000000c__

    smrng1 = smoothrng(source, per1, mult1)
    smrng2 = smoothrng(source, per2, mult2)
    smrng = (smrng1 + smrng2) / 2
    def rngfilt(x, r):
        rngfilt__00000019__: Series = x
        rngfilt__00000019__ = (nz(rngfilt__00000019__[1]) if x - r < nz(rngfilt__00000019__[1]) else x - r) if x > nz(rngfilt__00000019__[1]) else nz(rngfilt__00000019__[1]) if x + r > nz(rngfilt__00000019__[1]) else x + r
        return rngfilt__00000019__

    filt: Series = rngfilt(source, smrng)
    upward: Series[float] = 0.0
    upward = nz(upward[1]) + 1 if filt > filt[1] else 0 if filt < filt[1] else nz(upward[1])
    downward: Series[float] = 0.0
    downward = nz(downward[1]) + 1 if filt < filt[1] else 0 if filt > filt[1] else nz(downward[1])
    STR = filt + smrng
    STS = filt - smrng
    FUB: Series[float] = 0.0
    FUB = STR if STR < nz(FUB[1]) or close[1] > nz(FUB[1]) else nz(FUB[1])
    FLB: Series[float] = 0.0
    FLB = STS if STS > nz(FLB[1]) or close[1] < nz(FLB[1]) else nz(FLB[1])
    TRF: Series[float] = 0.0
    TRF = FUB if nz(TRF[1]) == FUB[1] and close <= FUB else FLB if nz(TRF[1]) == FUB[1] and close >= FUB else FLB if nz(TRF[1]) == FLB[1] and close >= FLB else FUB if nz(TRF[1]) == FLB[1] and close <= FLB else FUB
    long = ta.crossover(close, TRF)
    short = ta.crossunder(close, TRF)
    plotshape(showsignals and long, title='Long', text='BUY', style=shape.labelup, textcolor=color.white, size=size.tiny, location=location.belowbar, color=color.rgb(0, 19, 230))
    plotshape(showsignals and short, title='Short', text='SELL', style=shape.labeldown, textcolor=color.white, size=size.tiny, location=location.abovebar, color=color.rgb(0, 19, 230))
    alertcondition(long, title='Long', message='Long')
    alertcondition(short, title='Short', message='Short')
    Trfff = plot(TRF)
    mPlot = plot(ohlc4, title='', style=plot.style_circles, linewidth=math.max(1, 0))
    longFillColor = color.green if close > TRF else na
    shortFillColor = color.red if close < TRF else na
    fill(mPlot, Trfff, title='UpTrend Highligter', color=longFillColor)
    fill(mPlot, Trfff, title='DownTrend Highligter', color=shortFillColor)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
