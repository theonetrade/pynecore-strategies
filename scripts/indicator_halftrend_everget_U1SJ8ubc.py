"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, fill, high, input, location, low, math, na,
    nz, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Color, Persistent, PersistentSeries

calcGroup: str = 'Calculation'
visualGroup: str = 'Visuals'
buyColor: Color = color.blue
sellColor: Color = color.red
textColor: Color = color.white
buyFillColor: Color = color.new(buyColor, 85)
sellFillColor: Color = color.new(sellColor, 85)


@script.indicator('HalfTrend', overlay=True)
def main(
    amplitude=input.int(2, title='Amplitude', group=calcGroup),
    channelDeviation=input.int(2, title='Channel Deviation', group=calcGroup),
    showArrows=input.bool(True, title='Show Arrows', group=visualGroup),
    showChannels=input.bool(True, title='Show Channels', group=visualGroup),
    showLabels=input.bool(True, title='Show Buy/Sell Labels', group=visualGroup)
):
    trend: PersistentSeries[int] = 0
    nextTrend: Persistent[int] = 0
    maxLowPrice: Persistent[float] = nz(low[1], low)
    minHighPrice: Persistent[float] = nz(high[1], high)

    up: PersistentSeries[float] = 0.0
    down: PersistentSeries[float] = 0.0
    atrHigh: float = 0.0
    atrLow: float = 0.0
    arrowUp: float = na(float)
    arrowDown: float = na(float)

    atr2 = ta.atr(100) / 2
    dev = channelDeviation * atr2

    highPrice = high[math.abs(ta.highestbars(amplitude))]
    lowPrice = low[math.abs(ta.lowestbars(amplitude))]
    highma = ta.sma(high, amplitude)
    lowma = ta.sma(low, amplitude)

    if nextTrend == 1:
        maxLowPrice = math.max(lowPrice, maxLowPrice)

        if highma < maxLowPrice and close < nz(low[1], low):
            trend = 1
            nextTrend = 0
            minHighPrice = highPrice
    else:
        minHighPrice = math.min(highPrice, minHighPrice)

        if lowma > minHighPrice and close > nz(high[1], high):
            trend = 0
            nextTrend = 1
            maxLowPrice = lowPrice

    if trend == 0:
        if not na(trend[1]) and trend[1] != 0:
            up = down if na(down[1]) else down[1]
            arrowUp = up - atr2
        else:
            up = maxLowPrice if na(up[1]) else math.max(maxLowPrice, up[1])
        atrHigh = up + dev
        atrLow = up - dev
    else:
        if not na(trend[1]) and trend[1] != 1:
            down = up if na(up[1]) else up[1]
            arrowDown = down + atr2
        else:
            down = minHighPrice if na(down[1]) else math.min(minHighPrice, down[1])
        atrHigh = down + dev
        atrLow = down - dev

    ht = up if trend == 0 else down

    htColor = buyColor if trend == 0 else sellColor
    htPlot = plot(ht, title='HalfTrend', linewidth=2, color=htColor)

    atrHighPlot = plot(atrHigh if showChannels else na, title='ATR High', style=plot.style_circles, color=sellColor)
    atrLowPlot = plot(atrLow if showChannels else na, title='ATR Low', style=plot.style_circles, color=buyColor)

    fill(htPlot, atrHighPlot, title='ATR High Ribbon', color=sellFillColor)
    fill(htPlot, atrLowPlot, title='ATR Low Ribbon', color=buyFillColor)

    buySignal = not na(arrowUp) and trend == 0 and (trend[1] == 1)
    sellSignal = not na(arrowDown) and trend == 1 and (trend[1] == 0)

    plotshape(atrLow if showArrows and buySignal else na, title='Arrow Up', style=shape.triangleup, location=location.absolute, size=size.tiny, color=buyColor)
    plotshape(atrHigh if showArrows and sellSignal else na, title='Arrow Down', style=shape.triangledown, location=location.absolute, size=size.tiny, color=sellColor)

    plotshape(atrLow if showLabels and buySignal else na, title='Buy Label', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=buyColor, textcolor=textColor)
    plotshape(atrHigh if showLabels and sellSignal else na, title='Sell Label', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=sellColor, textcolor=textColor)

    alertcondition(buySignal, title='HalfTrend Buy', message='HalfTrend Buy, {{exchange}}:{{ticker}}')
    alertcondition(sellSignal, title='HalfTrend Sell', message='HalfTrend Sell, {{exchange}}:{{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
