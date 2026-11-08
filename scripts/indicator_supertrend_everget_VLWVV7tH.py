"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, display, fill, high, hl2, input, location,
    low, math, na, nz, ohlc4, open, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Color, PersistentSeries, Series

calcGroup: str = 'Calculation'
visualGroup: str = 'Visuals'
textColor: Color = color.white
longColor: Color = color.green
shortColor: Color = color.red
longFillColor: Color = color.new(color.green, 85)
shortFillColor: Color = color.new(color.red, 85)


@script.indicator('SuperTrend', overlay=True)
def main(
    length=input.int(22, title='ATR Period', group=calcGroup),
    mult=input.float(3, step=0.1, title='ATR Multiplier', group=calcGroup),
    src: Series[float] = input.source(hl2, title='Source', group=calcGroup),
    wicks=input.bool(True, title='Take Wicks into Account', group=calcGroup),
    showLabels=input.bool(True, title='Show Buy/Sell Labels', group=visualGroup),
    highlightState=input.bool(True, title='Highlight State', group=visualGroup)
):
    atr = mult * ta.atr(length)

    highPrice: Series = high if wicks else close
    lowPrice: Series = low if wicks else close
    doji4price = open == close and open == low and (open == high)

    longStop: Series = src - atr
    longStopPrev = nz(longStop[1], longStop)

    if longStop > 0:
        if doji4price:
            longStop = longStopPrev
        else:
            longStop = math.max(longStop, longStopPrev) if lowPrice[1] > longStopPrev else longStop
    else:
        longStop = longStopPrev

    shortStop: Series = src + atr
    shortStopPrev = nz(shortStop[1], shortStop)

    if shortStop > 0:
        if doji4price:
            shortStop = shortStopPrev
        else:
            shortStop = math.min(shortStop, shortStopPrev) if highPrice[1] < shortStopPrev else shortStop
    else:
        shortStop = shortStopPrev

    dir: PersistentSeries[int] = 1
    dir = 1 if dir == -1 and highPrice > shortStopPrev else -1 if dir == 1 and lowPrice < longStopPrev else dir

    longStopPlot = plot(longStop if dir == 1 else na, title='Long Stop', style=plot.style_linebr, linewidth=2, color=longColor)
    buySignal = dir == 1 and dir[1] == -1
    plotshape(longStop if buySignal else na, title='Long Stop Start', location=location.absolute, style=shape.circle, size=size.tiny, color=longColor)
    plotshape(longStop if buySignal and showLabels else na, title='Buy Label', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=longColor, textcolor=textColor)

    shortStopPlot = plot(na if dir == 1 else shortStop, title='Short Stop', style=plot.style_linebr, linewidth=2, color=shortColor)
    sellSignal = dir == -1 and dir[1] == 1
    plotshape(shortStop if sellSignal else na, title='Short Stop Start', location=location.absolute, style=shape.circle, size=size.tiny, color=shortColor)
    plotshape(shortStop if sellSignal and showLabels else na, title='Sell Label', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=shortColor, textcolor=textColor)

    midPricePlot = plot(ohlc4, title='', display=display.none, editable=False)

    fill(midPricePlot, longStopPlot, title='Long State Filling', color=longFillColor if highlightState and dir == 1 else na)
    fill(midPricePlot, shortStopPlot, title='Short State Filling', color=shortFillColor if highlightState and dir == -1 else na)

    alertcondition(dir != dir[1], title='SuperTrend Direction Change', message='SuperTrend has changed direction, {{exchange}}:{{ticker}}')
    alertcondition(buySignal, title='SuperTrend Buy', message='SuperTrend Buy, {{exchange}}:{{ticker}}')
    alertcondition(sellSignal, title='SuperTrend Sell', message='SuperTrend Sell, {{exchange}}:{{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
