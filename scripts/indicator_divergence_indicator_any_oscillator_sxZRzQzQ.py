"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barstate, color, format, high, input, location, low, na, ohlc4, plot,
    plotshape, script, shape, ta
)
from pynecore.types import Series


@script.indicator(title='Divergence Indicator (any oscillator)', format=format.price, overlay=True, timeframe='', na_bool=True)
def main(
    overlay_main=input(False, title='Plot on price (rather than on indicator)'),
    osc: Series[float] = input(ohlc4, title='Indicator'),
    lbR=input(title='Pivot Lookback Right', defval=5),
    lbL=input(title='Pivot Lookback Left', defval=5),
    rangeUpper=input(title='Max of Lookback Range', defval=60),
    rangeLower=input(title='Min of Lookback Range', defval=5),
    plotBull=input(title='Plot Bullish', defval=True),
    plotHiddenBull=input(title='Plot Hidden Bullish', defval=False),
    plotBear=input(title='Plot Bearish', defval=True),
    plotHiddenBear=input(title='Plot Hidden Bearish', defval=False),
    delay_plot_til_closed=input(title='Delay plot until candle is closed (don\'t repaint)', defval=False)
):
    bearColor = color.red
    bullColor = color.green
    hiddenBullColor = color.new(color.green, 80)
    hiddenBearColor = color.new(color.red, 80)
    textColor = color.white
    noneColor = color.new(color.white, 100)
    repaint = not delay_plot_til_closed or barstate.ishistory or barstate.isconfirmed
    plFound: Series = False if na(ta.pivotlow(osc, lbL, lbR)) else True
    phFound: Series = False if na(ta.pivothigh(osc, lbL, lbR)) else True
    def _inRange(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange_1 = _inRange(plFound[1])
    oscHL = osc[lbR] > ta.valuewhen(plFound, osc[lbR], 1) and _inRange_1
    priceLL = low[lbR] < ta.valuewhen(plFound, low[lbR], 1)
    bullCond = plotBull and priceLL and oscHL and plFound and repaint
    plot((low[lbR] if overlay_main else osc[lbR]) if plFound else na, offset=-lbR, title='Regular Bullish', linewidth=2, color=bullColor if bullCond else noneColor)
    plotshape((low[lbR] if overlay_main else osc[lbR]) if bullCond else na, offset=-lbR, title='Regular Bullish Label', text=' Bull ', style=shape.labelup, location=location.absolute, color=color.new(bullColor, 0), textcolor=color.new(textColor, 0))
    _inRange_2 = _inRange(plFound[1])
    oscLL = osc[lbR] < ta.valuewhen(plFound, osc[lbR], 1) and _inRange_2
    priceHL = low[lbR] > ta.valuewhen(plFound, low[lbR], 1)
    hiddenBullCond = plotHiddenBull and priceHL and oscLL and plFound and repaint
    plot((low[lbR] if overlay_main else osc[lbR]) if plFound else na, offset=-lbR, title='Hidden Bullish', linewidth=2, color=hiddenBullColor if hiddenBullCond else noneColor)
    plotshape((low[lbR] if overlay_main else osc[lbR]) if hiddenBullCond else na, offset=-lbR, title='Hidden Bullish Label', text=' H Bull ', style=shape.labelup, location=location.absolute, color=color.new(bullColor, 0), textcolor=color.new(textColor, 0))
    _inRange_3 = _inRange(phFound[1])
    oscLH = osc[lbR] < ta.valuewhen(phFound, osc[lbR], 1) and _inRange_3
    priceHH = high[lbR] > ta.valuewhen(phFound, high[lbR], 1)
    bearCond = plotBear and priceHH and oscLH and phFound and repaint
    plot((high[lbR] if overlay_main else osc[lbR]) if phFound else na, offset=-lbR, title='Regular Bearish', linewidth=2, color=bearColor if bearCond else noneColor)
    plotshape((high[lbR] if overlay_main else osc[lbR]) if bearCond else na, offset=-lbR, title='Regular Bearish Label', text=' Bear ', style=shape.labeldown, location=location.absolute, color=color.new(bearColor, 0), textcolor=color.new(textColor, 0))
    _inRange_4 = _inRange(phFound[1])
    oscHH = osc[lbR] > ta.valuewhen(phFound, osc[lbR], 1) and _inRange_4
    priceLH = high[lbR] < ta.valuewhen(phFound, high[lbR], 1)
    hiddenBearCond = plotHiddenBear and priceLH and oscHH and phFound and repaint
    plot((high[lbR] if overlay_main else osc[lbR]) if phFound else na, offset=-lbR, title='Hidden Bearish', linewidth=2, color=hiddenBearColor if hiddenBearCond else noneColor)
    plotshape((high[lbR] if overlay_main else osc[lbR]) if hiddenBearCond else na, offset=-lbR, title='Hidden Bearish Label', text=' H Bear ', style=shape.labeldown, location=location.absolute, color=color.new(bearColor, 0), textcolor=color.new(textColor, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)