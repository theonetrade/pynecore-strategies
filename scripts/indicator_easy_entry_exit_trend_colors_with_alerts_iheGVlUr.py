"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, bgcolor, close, color, fill, input, location, math, na, plot,
    plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator('Easy Entry/Exit Trend Colors (With Alerts)', overlay=False, na_bool=True)
def main(
    length=input.int(10, minval=1, title='BB Periods'),
    dev=input.float(1, minval=0.0001, title='Deviations'),
    fastLength=input.int(12, minval=1, title='FastLength'),
    slowLength=input.int(26, minval=1, title='SlowLength'),
    signalLength=input.int(9, minval=1, title='SignalLength'),
    multiscale=input.int(10000, minval=1, title='Scaling for ALTS'),
    __input_6__=input.int(30, '% of vertical space used', step=10, maxval=100),
    fast_period=input.int(50, minval=1, title='Short-Term SMA Length'),
    slow_period=input.int(200, minval=1, title='Long-Term SMA Length')
):
    fastMA = ta.ema(close, fastLength)
    slowMA = ta.ema(close, slowLength)
    macd = fastMA - slowMA
    scaleFactor = 100 / __input_6__
    fastMA1: Series = ta.sma(close, fast_period)
    slowMA1: Series = ta.sma(close, slow_period)
    golden_cross = ta.cross(slowMA1, fastMA1) and fastMA1[1] <= slowMA1[1]
    death_cross = ta.cross(slowMA1, fastMA1) and slowMA1[1] <= fastMA1[1]
    plotshape(fastMA1 if death_cross else na, color=color.new(color.new('#880E4F'), 0), text='Death Cross', textcolor=color.new(color.white, 0), style=shape.labeldown, location=location.top, title='Death Cross Text')
    plotshape(fastMA1 if golden_cross else na, color=color.new(color.lime, 0), text='Golden Cross', textcolor=color.new(color.black, 0), style=shape.labeldown, location=location.bottom, title='Golden Cross Text')
    colorpick = color.new('#880E4F') if ta.cross(slowMA1, fastMA1) and slowMA1[1] <= fastMA1[1] else na
    colorpick1 = color.lime if ta.cross(slowMA1, fastMA1) and fastMA1[1] <= slowMA1[1] else na
    bgcolor(colorpick)
    bgcolor(colorpick1)
    Std = ta.stdev(macd, length)
    Upper = Std * dev + ta.sma(macd, length)
    Lower = ta.sma(macd, length) - Std * dev
    Band1 = plot(Upper, color=color.new(color.gray, 0), style=plot.style_line, linewidth=2, title='Upper Band')
    Band2 = plot(Lower, color=color.new(color.gray, 0), style=plot.style_line, linewidth=2, title='Lower Band')
    fill(Band1, Band2, color=color.new(color.blue, 75), title='Fill')
    mcl = color.lime if macd >= Upper else na
    mcr = color.red if macd <= Upper else na
    crossoverBear = math.avg(macd, Upper) if ta.cross(macd, Upper) and macd < Upper else na
    crossoverBull = math.avg(macd, Upper) if ta.cross(macd, Upper) and macd > Upper else na
    plotshape(crossoverBear, title='Bear MACD', style=shape.xcross, text='Bear', location=location.absolute, color=color.new(color.red, 0), textcolor=color.new(color.red, 0), size=size.normal)
    plotshape(crossoverBull, title='Bull MACD', style=shape.diamond, text='Bull', location=location.absolute, color=color.new(color.lime, 0), textcolor=color.new(color.lime, 0), size=size.normal)
    plotshape(macd, color=mcl, style=shape.triangleup, title='Green Triangles', location=location.absolute, size=size.tiny)
    plotshape(macd, color=mcr, style=shape.triangledown, title='Red Triangles', location=location.absolute, size=size.tiny)
    zeroline: int = 0
    plot(zeroline, color=color.new(color.orange, 0), linewidth=1, title='Zeroline')
    barcolor(color.yellow if macd > Upper else na)
    barcolor(color.aqua if macd < Lower else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
