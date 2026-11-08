"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    close, color, format, high, hline, input, location, low, na, open, plot,
    plotshape, script, shape, ta, volume
)
from pynecore.types import Series


@script.indicator(title='Volume Divergence by MM', shorttitle='Volume Divergence', format=format.volume, na_bool=True)
def main(
    vl1=input(defval=5, title='First Moving Average length'),
    vl2=input(defval=8, title='Second Moving Average length'),
    lbR=input(title='Pivot Lookback Right', defval=5),
    lbL=input(title='Pivot Lookback Left', defval=5),
    rangeUpper=input(title='Max of Lookback Range', defval=60),
    rangeLower=input(title='Min of Lookback Range', defval=5),
    plotBull=input(title='Plot Bullish', defval=True),
    plotHiddenBull=input(title='Plot Hidden Bullish', defval=False),
    plotBear=input(title='Plot Bearish', defval=True),
    plotHiddenBear=input(title='Plot Hidden Bearish', defval=False)
):
    def pine_wma(x: Series, y):
        norm: float = 0.0
        sum: float = 0.0
        for i in pine_range(0, y - 1, 1):
            weight = (y - i) * y
            norm = norm + weight
            factor = -1 if close[i] < open[i] else 1
            sum = sum + x[i] * weight * factor
        return sum / norm

    vl3 = vl1 + vl2
    vl4 = vl2 + vl3
    vl5 = vl3 + vl4
    v1 = pine_wma(volume, vl1)
    v2 = pine_wma(v1, vl2)
    v3 = pine_wma(v2, vl3)
    v4 = pine_wma(v3, vl4)
    vol: Series = pine_wma(v4, vl5)
    vol_color = color.green if vol > 0 else color.red
    hline(0, title='Baseline', color=color.silver, linewidth=1)
    plot(vol, color=vol_color, linewidth=2, title='Volume')
    bearColor = color.red
    bullColor = color.green
    hiddenBullColor = color.new(color.green, 25)
    hiddenBearColor = color.new(color.red, 25)
    textColor = color.white
    noneColor = color.new(color.white, 100)
    plFound: Series = False if na(ta.pivotlow(vol, lbL, lbR)) else True
    phFound: Series = False if na(ta.pivothigh(vol, lbL, lbR)) else True
    def _inRange(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange_1 = _inRange(plFound[1])
    volHL = vol[lbR] > ta.valuewhen(plFound, vol[lbR], 1) and _inRange_1
    priceLL = low[lbR] < ta.valuewhen(plFound, low[lbR], 1)
    bullCond = plotBull and priceLL and volHL and plFound
    plot(vol[lbR] if plFound else na, offset=-lbR, title='Regular Bullish', linewidth=2, color=bullColor if bullCond else noneColor)
    plotshape(vol[lbR] if bullCond else na, offset=-lbR, title='Regular Bullish Label', text=' Bull ', style=shape.labelup, location=location.absolute, color=color.new(bullColor, 0), textcolor=color.new(textColor, 0))
    _inRange_2 = _inRange(plFound[1])
    volLL = vol[lbR] < ta.valuewhen(plFound, vol[lbR], 1) and _inRange_2
    priceHL = low[lbR] > ta.valuewhen(plFound, low[lbR], 1)
    hiddenBullCond = plotHiddenBull and priceHL and volLL and plFound
    plot(vol[lbR] if plFound else na, offset=-lbR, title='Hidden Bullish', linewidth=2, color=hiddenBullColor if hiddenBullCond else noneColor)
    plotshape(vol[lbR] if hiddenBullCond else na, offset=-lbR, title='Hidden Bullish Label', text=' H Bull ', style=shape.labelup, location=location.absolute, color=color.new(bullColor, 0), textcolor=color.new(textColor, 0))
    _inRange_3 = _inRange(phFound[1])
    volLH = vol[lbR] < ta.valuewhen(phFound, vol[lbR], 1) and _inRange_3
    priceHH = high[lbR] > ta.valuewhen(phFound, high[lbR], 1)
    bearCond = plotBear and priceHH and volLH and phFound
    plot(vol[lbR] if phFound else na, offset=-lbR, title='Regular Bearish', linewidth=2, color=bearColor if bearCond else noneColor)
    plotshape(vol[lbR] if bearCond else na, offset=-lbR, title='Regular Bearish Label', text=' Bear ', style=shape.labeldown, location=location.absolute, color=color.new(bearColor, 0), textcolor=color.new(textColor, 0))
    _inRange_4 = _inRange(phFound[1])
    volHH = vol[lbR] > ta.valuewhen(phFound, vol[lbR], 1) and _inRange_4
    priceLH = high[lbR] < ta.valuewhen(phFound, high[lbR], 1)
    hiddenBearCond = plotHiddenBear and priceLH and volHH and phFound
    plot(vol[lbR] if phFound else na, offset=-lbR, title='Hidden Bearish', linewidth=2, color=hiddenBearColor if hiddenBearCond else noneColor)
    plotshape(vol[lbR] if hiddenBearCond else na, offset=-lbR, title='Hidden Bearish Label', text=' H Bear ', style=shape.labeldown, location=location.absolute, color=color.new(bearColor, 0), textcolor=color.new(textColor, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
