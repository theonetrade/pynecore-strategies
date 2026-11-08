"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, barcolor, bgcolor, close, color, high, input, location,
    low, na, plot, plotshape, script, shape, ta
)
from pynecore.types import Series


@script.indicator('Accurate Swing Trading System', overlay=True, na_bool=True)
def main(
    no=input(3, title='Swing'),
    Barcolor=input(True, title='Barcolor'),
    Bgcolor=input(False, title='Bgcolor')
):
    res: Series = ta.highest(high, no)
    sup: Series = ta.lowest(low, no)
    iff_1 = -1 if close < sup[1] else 0
    avd = 1 if close > res[1] else iff_1
    avn = ta.valuewhen(avd != 0, avd, 0)
    tsl = sup if avn == 1 else res
    Buy = ta.crossover(close, tsl)
    Sell = ta.crossunder(close, tsl)
    plotshape(Buy, 'BUY', shape.labelup, location.belowbar, color.new(color.green, 0), text='BUY', textcolor=color.new(color.black, 0))
    plotshape(Sell, 'SELL', shape.labeldown, location.abovebar, color.new(color.red, 0), text='SELL', textcolor=color.new(color.black, 0))
    colr = color.green if close >= tsl else color.red if close <= tsl else na
    plot(tsl, color=colr, linewidth=3, title='TSL')
    barcolor(colr if Barcolor else na)
    bgcolor(colr if Bgcolor else na)
    alertcondition(Buy, title='Buy Signal', message='Buy')
    alertcondition(Sell, title='Sell Signal', message='Sell')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
