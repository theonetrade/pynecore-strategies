"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, fill, input, location, math, na, nz, ohlc4,
    plot, plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator('ST0P', overlay=True, na_bool=True)
def main(
    Percent=input.float(title='Percent', defval=3),
    src: Series[float] = input(close, title='Source'),
    changeLONGSHORT=input.int(title='LONG=1 SHORT=2', minval=1, maxval=2, defval=1),
    KADEME=input.float(title='Unit', step=0.1, defval=0.0),
    showsignals=input(title='Show ST0P Signals ?', defval=True),
    highlighting=input(title='Highlighter On/Off ?', defval=True)
):
    SHORT: Series = src + KADEME + src * Percent / 100
    SHORTprev = nz(SHORT[1], SHORT)
    SUB: Series[float] = 0.0
    SUB = SHORT if SHORT < nz(SUB[1]) or src[1] > nz(SUB[1]) else nz(SUB[1])
    LONG: Series = src - KADEME - src * Percent / 100
    LONGprev = nz(LONG[1], LONG)
    SLB: Series[float] = 0.0
    SLB = LONG if LONG > nz(SLB[1]) or src[1] < nz(SLB[1]) else nz(SLB[1])
    ST0P: Series = SLB if changeLONGSHORT == 1 else SUB
    longFillColor = (color.green if changeLONGSHORT == 1 else color.white) if highlighting else color.white
    shortFillColor = (color.red if changeLONGSHORT == 2 else color.white) if highlighting else color.white
    col12 = ST0P > ST0P[1]
    col32 = ST0P < ST0P[1]
    color2 = color.green if col12 else color.red if col32 else color.new('#001AE1')
    fill(plot(ohlc4, title='', style=plot.style_circles, linewidth=math.max(1, 0)), plot(ST0P, color=color2, linewidth=3), title='LONG Highligter', color=longFillColor)
    fill(plot(ohlc4, title='', style=plot.style_circles, linewidth=math.max(1, 0)), plot(ST0P, color=color2, linewidth=3), title='SHORT Highligter', color=shortFillColor)
    crossunder_1 = ta.crossunder(src, ST0P)
    alertcondition(changeLONGSHORT == 1 and crossunder_1, title='LONG POSITION ST0P!', message='SELL!')
    crossover_1 = ta.crossover(src, ST0P)
    alertcondition(changeLONGSHORT == 2 and crossover_1, title='SHORT POSITION ST0P!', message='BUY!')
    crossover_2 = ta.crossover(src, ST0P)
    plotshape(SHORT if changeLONGSHORT == 2 and crossover_2 and showsignals else na, title='Buy', text='ST0P', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    crossunder_2 = ta.crossunder(src, ST0P)
    plotshape(LONG if changeLONGSHORT == 1 and crossunder_2 and showsignals else na, title='Sell', text='ST0P', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
