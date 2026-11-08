"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, high, input, location, low, na, plot,
    plotshape, script, shape, ta
)
from pynecore.types import Series


@script.indicator(title='MACD Divergences by @DaviddTech', timeframe='', na_bool=True)
def main(
    fast_length=input(title='Fast Length', defval=12),
    slow_length=input(title='Slow Length', defval=26),
    src: Series[float] = input(title='Source', defval=close),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9),
    sma_source=input.string(title='Oscillator MA Type', defval='EMA', options=('SMA', 'EMA')),
    sma_signal=input.string(title='Signal Line MA Type', defval='EMA', options=('SMA', 'EMA')),
    col_macd=input.color(color.new('#2962FF'), 'MACD Line  ', group='Color Settings', inline='MACD'),
    col_signal=input.color(color.new('#FF6D00'), 'Signal Line  ', group='Color Settings', inline='Signal'),
    col_grow_above=input.color(color.new('#26A69A'), 'Above   Grow', group='Histogram', inline='Above'),
    col_fall_above=input.color(color.new('#B2DFDB'), 'Fall', group='Histogram', inline='Above'),
    col_grow_below=input.color(color.new('#FFCDD2'), 'Below Grow', group='Histogram', inline='Below'),
    col_fall_below=input.color(color.new('#FF5252'), 'Fall', group='Histogram', inline='Below'),
    donttouchzero=input(title='Don\'t touch the zero line?', defval=True),
    lbR=input(title='Pivot Lookback Right', defval=5),
    lbL=input(title='Pivot Lookback Left', defval=5),
    rangeUpper=input(title='Max of Lookback Range', defval=60),
    rangeLower=input(title='Min of Lookback Range', defval=5),
    plotBull=input(title='Plot Bullish', defval=True),
    plotBear=input(title='Plot Bearish', defval=True)
):
    fast_ma = ta.sma(src, fast_length) if sma_source == 'SMA' else ta.ema(src, fast_length)
    slow_ma = ta.sma(src, slow_length) if sma_source == 'SMA' else ta.ema(src, slow_length)
    macd = fast_ma - slow_ma
    signal = ta.sma(macd, signal_length) if sma_signal == 'SMA' else ta.ema(macd, signal_length)
    hist: Series = macd - signal
    plot(hist, title='Histogram', style=plot.style_columns, color=(col_grow_above if hist[1] < hist else col_fall_above) if hist >= 0 else col_grow_below if hist[1] < hist else col_fall_below)
    plot(macd, title='MACD', color=col_macd)
    plot(signal, title='Signal', color=col_signal)
    plotHiddenBull: bool = False
    plotHiddenBear: bool = False
    bearColor = color.red
    bullColor = color.green
    hiddenBullColor = color.new(color.green, 80)
    hiddenBearColor = color.new(color.red, 80)
    textColor = color.white
    noneColor = color.new(color.white, 100)
    osc: Series = macd
    plFound: Series = False if na(ta.pivotlow(osc, lbL, lbR)) else True
    phFound: Series = False if na(ta.pivothigh(osc, lbL, lbR)) else True
    def _inRange(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    _inRange_1 = _inRange(plFound[1])
    oscHL = osc[lbR] > ta.valuewhen(plFound, osc[lbR], 1) and _inRange_1 and (osc[lbR] < 0)
    priceLL = low[lbR] < ta.valuewhen(plFound, low[lbR], 1)
    priceHHZero = ta.highest(osc, lbL + lbR + 5)
    blowzero = priceHHZero < 0 if donttouchzero else True
    bullCond = plotBull and priceLL and oscHL and plFound and blowzero
    plot(osc[lbR] if plFound else na, offset=-lbR, title='Regular Bullish', linewidth=2, color=bullColor if bullCond else noneColor)
    plotshape(osc[lbR] if bullCond else na, offset=-lbR, title='Regular Bullish Label', text=' Bull ', style=shape.labelup, location=location.absolute, color=color.new(bullColor, 0), textcolor=color.new(textColor, 0))
    _inRange_2 = _inRange(plFound[1])
    oscLL = osc[lbR] < ta.valuewhen(plFound, osc[lbR], 1) and _inRange_2
    priceHL = low[lbR] > ta.valuewhen(plFound, low[lbR], 1)
    hiddenBullCond = plotHiddenBull and priceHL and oscLL and plFound
    plot(osc[lbR] if plFound else na, offset=-lbR, title='Hidden Bullish', linewidth=2, color=hiddenBullColor if hiddenBullCond else noneColor)
    plotshape(osc[lbR] if hiddenBullCond else na, offset=-lbR, title='Hidden Bullish Label', text=' H Bull ', style=shape.labelup, location=location.absolute, color=color.new(bullColor, 0), textcolor=color.new(textColor, 0))
    _inRange_3 = _inRange(phFound[1])
    oscLH = osc[lbR] < ta.valuewhen(phFound, osc[lbR], 1) and _inRange_3 and (osc[lbR] > 0)
    priceLLZero = ta.lowest(osc, lbL + lbR + 5)
    bearzero = priceLLZero > 0 if donttouchzero else True
    priceHH = high[lbR] > ta.valuewhen(phFound, high[lbR], 1)
    bearCond = plotBear and priceHH and oscLH and phFound and bearzero
    plot(osc[lbR] if phFound else na, offset=-lbR, title='Regular Bearish', linewidth=2, color=bearColor if bearCond else noneColor)
    plotshape(osc[lbR] if bearCond else na, offset=-lbR, title='Regular Bearish Label', text=' Bear ', style=shape.labeldown, location=location.absolute, color=color.new(bearColor, 0), textcolor=color.new(textColor, 0))
    _inRange_4 = _inRange(phFound[1])
    oscHH = osc[lbR] > ta.valuewhen(phFound, osc[lbR], 1) and _inRange_4
    priceLH = high[lbR] < ta.valuewhen(phFound, high[lbR], 1)
    hiddenBearCond = plotHiddenBear and priceLH and oscHH and phFound
    plot(osc[lbR] if phFound else na, offset=-lbR, title='Hidden Bearish', linewidth=2, color=hiddenBearColor if hiddenBearCond else noneColor)
    plotshape(osc[lbR] if hiddenBearCond else na, offset=-lbR, title='Hidden Bearish Label', text=' H Bear ', style=shape.labeldown, location=location.absolute, color=color.new(bearColor, 0), textcolor=color.new(textColor, 0))
    alertcondition(bullCond, title='Bull', message='Regular Bull Div {{ticker}} XXmin')
    alertcondition(bearCond, title='Bear', message='Regular Bear Div {{ticker}} XXmin')
    alertcondition(hiddenBullCond, title='H Bull', message='Hidden Bull Div {{ticker}} XXmin')
    alertcondition(hiddenBearCond, title='H Bear', message='Hidden Bear Div {{ticker}} XXmin')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
