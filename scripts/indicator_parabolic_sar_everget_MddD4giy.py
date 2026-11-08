"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, display, fill, input, location, math, na,
    ohlc4, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Color, Series

calcGroup: str = 'Calculation'
visualGroup: str = 'Visuals'
textColor: Color = color.white
longColor: Color = color.green
shortColor: Color = color.red
longFillColor: Color = color.new(color.green, 85)
shortFillColor: Color = color.new(color.red, 85)


@script.indicator('Parabolic SAR', shorttitle='PSAR', overlay=True)
def main(
    start=input.float(0.02, step=0.001, title='Start', group=calcGroup),
    increment=input.float(0.02, step=0.001, title='Increment', group=calcGroup),
    maximum=input.float(0.2, step=0.01, title='Maximum', group=calcGroup),
    width=input.int(2, minval=1, title='Point Width', group=visualGroup),
    showLabels=input.bool(True, title='Show Buy/Sell Labels', group=visualGroup),
    highlightStartPoints=input.bool(True, title='Highlight Start Points', group=visualGroup),
    highlightState=input.bool(True, title='Highlight State', group=visualGroup)
):
    psar = ta.sar(start, increment, maximum)
    dir: Series = 1 if psar < close else -1

    psarColor = color.new('#3388BB') if dir == 1 else color.new('#FDCC02')
    psarPlot = plot(psar, title='PSAR', style=plot.style_circles, linewidth=math.max(1, width), color=psarColor)

    buySignal = dir == 1 and dir[1] == -1
    plotshape(psar if buySignal and highlightStartPoints else na, title='Long Start', location=location.absolute, style=shape.circle, size=size.tiny, color=longColor)
    plotshape(psar if buySignal and showLabels else na, title='Buy Label', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=longColor, textcolor=textColor)

    sellSignal = dir == -1 and dir[1] == 1
    plotshape(psar if sellSignal and highlightStartPoints else na, title='Short Start', location=location.absolute, style=shape.circle, size=size.tiny, color=shortColor)
    plotshape(psar if sellSignal and showLabels else na, title='Sell Label', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=shortColor, textcolor=textColor)

    midPricePlot = plot(ohlc4, title='', display=display.none, editable=False)

    fillColor = (longFillColor if dir == 1 else shortFillColor if dir == -1 else na) if highlightState else na
    fill(midPricePlot, psarPlot, title='Trade State Filling', color=fillColor)

    alertcondition(dir != dir[1], title='Direction Change', message='PSAR has changed direction, {{exchange}}:{{ticker}}')
    alertcondition(buySignal, title='Long', message='PSAR Long, {{exchange}}:{{ticker}}')
    alertcondition(sellSignal, title='Short', message='PSAR Sell, {{exchange}}:{{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
