"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fill, high, input, location, low, math, na, plot,
    plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator(title='Turtle Trade Channels Indicator', shorttitle='TuTCI', overlay=True, timeframe='', na_bool=True)
def main(
    length=input.int(20, 'Entry Length', minval=1),
    len2=input.int(10, 'Exit Length', minval=1),
    showsignals=input(title='Show Entry/Exit Signals ?', defval=True),
    highlighting=input(title='Highlighter On/Off ?', defval=True)
):
    lower: Series = ta.lowest(length)
    upper: Series = ta.highest(length)
    u = plot(upper, 'Upper', color=color.new(color.new('#0094FF'), 0))
    l = plot(lower, 'Lower', color=color.new(color.new('#0094FF'), 0))
    up: Series = ta.highest(high, length)
    down: Series = ta.lowest(low, length)
    sup: Series = ta.highest(high, len2)
    sdown: Series = ta.lowest(low, len2)
    K1 = down if ta.barssince(high >= up[1]) <= ta.barssince(low <= down[1]) else up
    barssince_1 = ta.barssince(high >= up[1])
    barssince_2 = ta.barssince(low <= down[1])
    K2 = sdown if barssince_1 <= barssince_2 else sup
    K3 = down if close > K1 else na
    K4 = up if close < K1 else na
    plot(K1, title='Trend Line', color=color.new(color.red, 0), linewidth=2)
    e = plot(K2, title='Exit Line', color=color.new(color.blue, 0), linewidth=1, style=plot.style_circles)
    crossover_1 = ta.crossover(high, upper[1])
    buySignal: Series = high == upper[1] or crossover_1
    crossover_2 = ta.crossover(lower[1], low)
    sellSignal: Series = low == lower[1] or crossover_2
    crossover_3 = ta.crossover(sdown[1], low)
    buyExit: Series = low == sdown[1] or crossover_3
    crossover_4 = ta.crossover(high, sup[1])
    sellExit: Series = high == sup[1] or crossover_4
    O1: Series = ta.barssince(buySignal)
    O2: Series = ta.barssince(sellSignal)
    O3: Series = ta.barssince(buyExit)
    O4: Series = ta.barssince(sellExit)
    E1 = ta.barssince(buySignal[1])
    E2 = ta.barssince(sellSignal[1])
    E3 = ta.barssince(buyExit[1])
    E4 = ta.barssince(sellExit[1])
    plotshape(down if buySignal and O3 < O1[1] else na, title='Long Entry', location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(color.green, 0))
    plotshape(down if buySignal and showsignals and (O3 < O1[1]) else na, title='Long', text='Long Entry', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    plotshape(up if sellSignal and O4 < O2[1] else na, title='Short Entry', location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(color.red, 0))
    plotshape(up if sellSignal and showsignals and (O4 < O2[1]) else na, title='Short', text='Short Entry', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    plotshape(up if buyExit and O1 < O3[1] else na, title='Long Exit', location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(color.blue, 0))
    plotshape(up if buyExit and showsignals and (O1 < O3[1]) else na, title='Long Exit', text='Exit Long', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.blue, 0), textcolor=color.new(color.white, 0))
    plotshape(down if sellExit and O2 < O4[1] else na, title='Short Exit', location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(color.blue, 0))
    plotshape(down if sellExit and showsignals and (O2 < O4[1]) else na, title='Short', text='Exit Short', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.blue, 0), textcolor=color.new(color.white, 0))
    color1 = color.green if highlighting and math.min(O1, O2, O3) == O1 else na
    color2 = color.red if highlighting and math.min(O1, O2, O4) == O2 else na
    fill(u, e, color=color.new(color1, 88), title='Background')
    fill(l, e, color=color.new(color2, 88), title='Background')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
