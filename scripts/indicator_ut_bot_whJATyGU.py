"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, barcolor, close, color, input, location, math, nz, plot,
    plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator(title='UT Bot', overlay=True, na_bool=True)
def main(
    keyvalue=input.float(3, title='Key Vaule. \'This changes the sensitivity\'', step=0.5),
    atrperiod=input(10, title='ATR Period')
):
    src: Series = close
    xATR = ta.atr(atrperiod)
    nLoss = keyvalue * xATR
    xATRTrailingStop: Series[float] = 0.0
    iff_1 = src - nLoss if src > nz(xATRTrailingStop[1], 0) else src + nLoss
    iff_2 = math.min(nz(xATRTrailingStop[1]), src + nLoss) if src < nz(xATRTrailingStop[1], 0) and src[1] < nz(xATRTrailingStop[1], 0) else iff_1
    xATRTrailingStop = math.max(nz(xATRTrailingStop[1]), src - nLoss) if src > nz(xATRTrailingStop[1], 0) and src[1] > nz(xATRTrailingStop[1], 0) else iff_2
    pos: Series[int] = 0
    iff_3 = -1 if src[1] > nz(xATRTrailingStop[1], 0) and src < nz(xATRTrailingStop[1], 0) else nz(pos[1], 0)
    pos = 1 if src[1] < nz(xATRTrailingStop[1], 0) and src > nz(xATRTrailingStop[1], 0) else iff_3
    xcolor = color.red if pos == -1 else color.green if pos == 1 else color.blue
    plot(xATRTrailingStop, color=xcolor, title='Trailing Stop')
    buy = ta.crossover(src, xATRTrailingStop)
    sell = ta.crossunder(src, xATRTrailingStop)
    barcolor__ren__ = src > xATRTrailingStop
    plotshape(buy, title='Buy', text='Buy', style=shape.labelup, location=location.belowbar, color=color.new(color.green, 0), textcolor=color.new(color.white, 0), size=size.tiny)
    plotshape(sell, title='Sell', text='Sell', style=shape.labeldown, color=color.new(color.red, 0), textcolor=color.new(color.white, 0), size=size.tiny)
    barcolor(color.green if barcolor__ren__ else color.red)
    alertcondition(buy, title='UT BOT Buy', message='UT BOT Buy')
    alertcondition(sell, title='UT BOT Sell', message='UT BOT Sell')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
