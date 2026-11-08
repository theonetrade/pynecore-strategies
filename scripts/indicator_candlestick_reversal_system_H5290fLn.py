"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, close, color, high, input, location, low, math, na, open,
    plot, plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator('Candlestick Reversal System', overlay=True, na_bool=True)
def main(
    pivotlbar=input(defval=5, title='Length to Highest/Lowest'),
    showma=input.bool(defval=False, title='SMA', inline='ma'),
    malen=input.int(defval=10, title='', inline='ma'),
    macol=input.color(defval=color.blue, title='', inline='ma'),
    l01=input(True, title='Enable Wick Reversal System'),
    wick_multiplier=input.float(title='Wick Multiplier', defval=2.5, step=0.5, maxval=20),
    body_percentage=input.float(title='Body Percentage', defval=0.25, step=0.1, maxval=1),
    l02=input(True, title='Enable Exteme Reversal System'),
    bodysize=input.float(title='Body Size', defval=0.525, step=0.05, maxval=1),
    barsback=input.int(title='Bars Back', defval=50, maxval=50),
    bodymultiplier=input.float(title='Body Multiplier', defval=2, step=0.25, maxval=5),
    l03=input(True, title='Enable Outside Reversal System'),
    BarMultiplier=input.float(title='Body Multiplier', defval=1.25, step=0.05, maxval=3.5),
    BarsBack=input.int(title='Bars Back', defval=50, maxval=250),
    l04=input(True, title='Enable Doji Reversal System'),
    percentage=input.float(title='Body Percentage', defval=0.1, step=0.1, minval=0.1)
):
    highleftempty = ta.pivothigh(pivotlbar, 0)
    lowleftempty = ta.pivotlow(pivotlbar, 0)
    plot(ta.sma(close, malen) if showma else na, color=macol if showma else na, linewidth=2)
    O: Series = open
    C: Series = close
    H: Series = high
    L: Series = low
    sma_1 = ta.sma(H - L, 50)
    Wlongsignal = C > O and O - L >= (C - O) * wick_multiplier and (H - C <= (H - L) * body_percentage) or (C < O and C - L >= (O - C) * wick_multiplier and (H - C <= (H - L) * body_percentage)) or (C == O and C != H and (H - L >= (H - C) * wick_multiplier) and (H - C <= (H - L) * body_percentage)) or (O == H and C == H and (H - L >= sma_1))
    sma_2 = ta.sma(H - L, 50)
    Wshortsignal = C < O and H - O >= (O - C) * wick_multiplier and (C - L <= (H - L) * body_percentage) or (C > O and H - C >= (C - O) * wick_multiplier and (C - L <= (H - L) * body_percentage)) or (C == O and C != L and (H - L >= (C - L) * wick_multiplier) and (C - L <= (H - L) * body_percentage)) or (O == L and C == L and (H - L >= sma_2))
    mybodysize = math.abs(C - O)
    AverageBody = ta.sma(mybodysize, barsback)
    mycandlesize = H - L
    AverageCandle = ta.sma(mycandlesize, barsback)
    Elongsignal = O[1] - C[1] >= bodysize * (H[1] - L[1]) and H[1] - L[1] > AverageCandle * bodymultiplier and (O[1] - C[1] > AverageBody) and (C > O)
    Eshortsignal = C[1] - O[1] >= bodysize * (H[1] - L[1]) and H[1] - L[1] > AverageCandle * bodymultiplier and (C[1] - O[1] > AverageBody) and (O > C)
    AverageCandle1 = ta.sma(mycandlesize, BarsBack)
    Olongsignal = L < L[1] and C > H[1] and (H - L >= AverageCandle1 * BarMultiplier)
    Oshortsignal = H > H[1] and C < L[1] and (H - L >= AverageCandle1 * BarMultiplier)
    frangehl = H[1] - L[1]
    frangeco = math.abs(C[1] - O[1])
    sma10 = ta.sma(close, 10)
    Dshortsignal = frangeco <= frangehl * percentage and C < L[1] and (L[1] > sma10) and (C < O) or (C < L[2] and C[1] >= L[2] and (frangeco <= frangeco * percentage) and (C < O) and (L[2] > sma10))
    Dlongsignal = frangeco <= frangehl * percentage and C > H[1] and (H[1] < sma10) and (C > O) or (C > H[2] and C[1] <= H[2] and (frangeco <= frangeco * percentage) and (C > O) and (H[2] < sma10))
    longsignal = cast_bool(lowleftempty) and (l01 and Wlongsignal or (l02 and Elongsignal) or (l03 and Olongsignal) or (l04 and Dlongsignal))
    shortsignal = cast_bool(highleftempty) and (l01 and Wlongsignal or (l02 and Eshortsignal) or (l03 and Oshortsignal) or (l04 and Dshortsignal))
    plotshape(longsignal, color=color.new(color.blue, 0), location=location.belowbar, style=shape.triangleup, size=size.small)
    plotshape(shortsignal, color=color.new(color.red, 0), location=location.abovebar, style=shape.triangledown, size=size.small)
    alertcondition(longsignal, title='Long Signal', message='Long Signal')
    alertcondition(shortsignal, title='Short Signal', message='Short Signal')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
