"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bgcolor, close, color, display, high, location, low, na,
    plotshape, script, shape, size
)
from pynecore.types import Series


@script.indicator('CBC Flip', timeframe='', timeframe_gaps=True, overlay=True, na_bool=True)
def main():
    cbc: Series[bool] = False
    cbc = cbc[1]
    if cbc and close < low[1]:
        cbc = False
    if not cbc and close > high[1]:
        cbc = True
    plotshape(not cbc and cbc[1], style=shape.triangledown, location=location.abovebar, color=color.rgb(228, 102, 102), size=size.small, title='Bears', display=display.all - display.status_line)
    plotshape(cbc and (not cbc[1]), style=shape.triangleup, location=location.belowbar, color=color.rgb(120, 206, 176), size=size.small, title='Bulls', display=display.all - display.status_line)
    bgcolor(color.rgb(255, 235, 59, 71) if cbc and (not cbc[1]) else color.rgb(5, 185, 240, 59) if not cbc and cbc[1] else na)
    alertcondition(not cbc and cbc[1], 'Bears', 'Bears in Control')
    alertcondition(cbc and (not cbc[1]), 'Bulls', 'Bulls in Control')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
