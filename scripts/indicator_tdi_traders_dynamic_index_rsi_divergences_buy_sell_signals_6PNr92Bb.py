"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bgcolor, close, color, fill, high, hline, input,
    location, low, na, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator('TDI - Traders Dynamic Index + RSI Divergences + Buy/Sell Signals', shorttitle='TDI + RSI Div', na_bool=True)
def main(
    rsiPeriod=input.int(14, minval=1, title='RSI Period'),
    bandLength=input.int(34, minval=1, title='Band Length'),
    lengthrsipl=input.int(7, minval=0, title='Fast MA on RSI'),
    lengthtradesl=input.int(2, minval=1, title='Slow MA on RSI'),
    len=input.int(title='RSI Period', minval=1, defval=14),
    src: Series[float] = input(title='RSI Source', defval=close),
    lbR=input(title='Pivot Lookback Right', defval=5),
    lbL=input(title='Pivot Lookback Left', defval=5),
    rangeUpper=input(title='Max of Lookback Range', defval=60),
    rangeLower=input(title='Min of Lookback Range', defval=5),
    plotBull=input(title='Plot Bullish', defval=True),
    plotHiddenBull=input(title='Plot Hidden Bullish', defval=False),
    plotBear=input(title='Plot Bearish', defval=True),
    plotHiddenBear=input(title='Plot Hidden Bearish', defval=False)
):
    src1 = close
    r = ta.rsi(src1, rsiPeriod)
    ma = ta.sma(r, bandLength)
    offs = 1.6185 * ta.stdev(r, bandLength)
    up = ma + offs
    dn = ma - offs
    mid = (up + dn) / 2
    mbb = ta.sma(r, lengthrsipl)
    mab = ta.sma(r, lengthtradesl)
    hline(30, color=color.red, linewidth=1, linestyle=hline.style_dotted)
    hline(50, color=color.orange, linewidth=1, linestyle=hline.style_dotted)
    hline(70, color=color.green, linewidth=1, linestyle=hline.style_dotted)
    upl = plot(up, color=color.new(color.new('#12BCC9'), 60), title='VB Channel High', linewidth=2)
    dnl = plot(dn, color=color.new(color.new('#12BCC9'), 60), title='VB Channel Low', linewidth=2)
    midl = plot(mid, color=color.new(color.orange, 40), linewidth=2, title='MBL')
    mabl = plot(mab, color=color.new(color.lime, 30), linewidth=2, title='RSI PL')
    mbbl = plot(mbb, color=color.new(color.red, 60), linewidth=2, title='TSL Signal')
    fill(mabl, mbbl, color=color.new(color.green if mab > mbb else color.red, 80))
    long1 = ta.crossover(mab, mbb) and mbb > mid and (mbb > 50)
    short1 = ta.crossunder(mab, mbb) and mbb < mid and (mbb < 50)
    plotshape(long1, style=shape.labelup, location=location.bottom, color=color.new(color.lime, 0), size=size.tiny, editable=True)
    plotshape(short1, style=shape.labeldown, location=location.top, color=color.new(color.red, 0), size=size.tiny, editable=True)
    alertcondition(long1, title='Long', message='Crossover')
    alertcondition(short1, title='Short', message='Crossunder')
    best_setup = ta.crossover(mab, mid)
    alertcondition(best_setup, title='RSI Crosses Yellow', message='rsi crosses mid')
    scalp = mab > mid
    bgcolor(color.lime if scalp else na)
    bearColor = color.red
    bullColor = color.green
    hiddenBullColor = color.new(color.green, 80)
    hiddenBearColor = color.new(color.red, 80)
    textColor = color.white
    noneColor = color.new(color.white, 100)
    osc: Series = ta.rsi(src, len)
    plFound: Series = False if na(ta.pivotlow(osc, lbL, lbR)) else True
    phFound: Series = False if na(ta.pivothigh(osc, lbL, lbR)) else True
    def _inRange(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange_1 = _inRange(plFound[1])
    oscHL = osc[lbR] > ta.valuewhen(plFound, osc[lbR], 1) and _inRange_1
    priceLL = low[lbR] < ta.valuewhen(plFound, low[lbR], 1)
    bullCond = plotBull and priceLL and oscHL and plFound
    plot(osc[lbR] if plFound else na, offset=-lbR, title='Regular Bullish', linewidth=2, color=bullColor if bullCond else noneColor)
    plotshape(osc[lbR] if bullCond else na, offset=-lbR, title='Regular Bullish Label', text=' Bull ', style=shape.labelup, location=location.absolute, color=color.new(bullColor, 0), textcolor=color.new(textColor, 0))
    _inRange_2 = _inRange(plFound[1])
    oscLL = osc[lbR] < ta.valuewhen(plFound, osc[lbR], 1) and _inRange_2
    priceHL = low[lbR] > ta.valuewhen(plFound, low[lbR], 1)
    hiddenBullCond = plotHiddenBull and priceHL and oscLL and plFound
    plot(osc[lbR] if plFound else na, offset=-lbR, title='Hidden Bullish', linewidth=2, color=hiddenBullColor if hiddenBullCond else noneColor)
    plotshape(osc[lbR] if hiddenBullCond else na, offset=-lbR, title='Hidden Bullish Label', text=' H Bull ', style=shape.labelup, location=location.absolute, color=color.new(bullColor, 0), textcolor=color.new(textColor, 0))
    _inRange_3 = _inRange(phFound[1])
    oscLH = osc[lbR] < ta.valuewhen(phFound, osc[lbR], 1) and _inRange_3
    priceHH = high[lbR] > ta.valuewhen(phFound, high[lbR], 1)
    bearCond = plotBear and priceHH and oscLH and phFound
    plot(osc[lbR] if phFound else na, offset=-lbR, title='Regular Bearish', linewidth=2, color=bearColor if bearCond else noneColor)
    plotshape(osc[lbR] if bearCond else na, offset=-lbR, title='Regular Bearish Label', text=' Bear ', style=shape.labeldown, location=location.absolute, color=color.new(bearColor, 0), textcolor=color.new(textColor, 0))
    _inRange_4 = _inRange(phFound[1])
    oscHH = osc[lbR] > ta.valuewhen(phFound, osc[lbR], 1) and _inRange_4
    priceLH = high[lbR] < ta.valuewhen(phFound, high[lbR], 1)
    hiddenBearCond = plotHiddenBear and priceLH and oscHH and phFound
    plot(osc[lbR] if phFound else na, offset=-lbR, title='Hidden Bearish', linewidth=2, color=hiddenBearColor if hiddenBearCond else noneColor)
    plotshape(osc[lbR] if hiddenBearCond else na, offset=-lbR, title='Hidden Bearish Label', text=' H Bear ', style=shape.labeldown, location=location.absolute, color=color.new(bearColor, 0), textcolor=color.new(textColor, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
