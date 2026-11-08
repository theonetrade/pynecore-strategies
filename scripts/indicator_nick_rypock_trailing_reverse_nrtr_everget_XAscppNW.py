"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, display, fill, input, location, na, ohlc4,
    plot, plotshape, script, shape, size
)
from pynecore.types import Color, Persistent, PersistentSeries

calcGroup: str = 'Calculation'
visualGroup: str = 'Visuals'
textColor: Color = color.white
longColor: Color = color.green
shortColor: Color = color.red
longFillColor: Color = color.new(color.green, 85)
shortFillColor: Color = color.new(color.red, 85)


@script.indicator('Nick Rypock Trailing Reverse', shorttitle='NRTR', overlay=True)
def main(
    __input_0__=input.float(2, minval=0, maxval=100, step=0.1, title='Coefficient of Correction, %', group=calcGroup),
    showLabels=input.bool(True, title='Show Buy/Sell Labels', group=visualGroup),
    highlightState=input.bool(True, title='Highlight State', group=visualGroup)
):
    percentage = __input_0__ / 100

    trend: PersistentSeries[int] = 0
    hp: Persistent[float] = close
    lp: Persistent[float] = close
    nrtr = close

    if trend >= 0:
        if close > hp:
            hp = close
        nrtr = hp * (1 - percentage)
        if close <= nrtr:
            trend = -1
            lp = close
            nrtr = lp * (1 + percentage)
    else:
        if close < lp:
            lp = close
        nrtr = lp * (1 + percentage)
        if close > nrtr:
            trend = 1
            hp = close
            nrtr = hp * (1 - percentage)

    longStopPlot = plot(nrtr if trend == 1 else na, title='Long Stop', style=plot.style_linebr, linewidth=2, color=longColor)
    buySignal = trend == 1 and trend[1] == -1
    plotshape(nrtr if buySignal else na, title='Long Stop Start', location=location.absolute, style=shape.circle, size=size.tiny, color=longColor)
    plotshape(nrtr if buySignal and showLabels else na, title='Buy Label', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=longColor, textcolor=textColor)

    shortStopPlot = plot(na if trend == 1 else nrtr, title='Short Stop', style=plot.style_linebr, linewidth=2, color=shortColor)
    sellSignal = trend == -1 and trend[1] == 1
    plotshape(nrtr if sellSignal else na, title='Short Stop Start', location=location.absolute, style=shape.circle, size=size.tiny, color=shortColor)
    plotshape(nrtr if sellSignal and showLabels else na, title='Sell Label', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=shortColor, textcolor=textColor)

    midPricePlot = plot(ohlc4, title='', display=display.none, editable=False)

    fill(midPricePlot, longStopPlot, title='Long State Filling', color=longFillColor if highlightState and trend == 1 else na)
    fill(midPricePlot, shortStopPlot, title='Short State Filling', color=shortFillColor if highlightState and trend == -1 else na)

    alertcondition(trend != trend[1], title='NRTR Direction Change', message='NRTR has changed direction, {{exchange}}:{{ticker}}')
    alertcondition(buySignal, title='NRTR Buy', message='NRTR Buy, {{exchange}}:{{ticker}}')
    alertcondition(sellSignal, title='NRTR Sell', message='NRTR Sell, {{exchange}}:{{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)