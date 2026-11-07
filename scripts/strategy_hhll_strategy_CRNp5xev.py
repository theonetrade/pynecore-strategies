"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, color, high, hlc3, input, low, nz, plot, script, strategy, ta,
    time, timestamp
)
from pynecore.types import Series


@script.strategy(title='HHLL', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    Len=input(29),
    reverse=input(True, title='Trade reverse')
):
    m, xHH, xLL = ta.bb(hlc3, Len, 2)
    movevalue = (xHH - xLL) / 2
    xHHM: Series = xHH + movevalue
    xLLM: Series = xLL - movevalue
    pos: Series[int] = 0
    possig: Series[int] = 0
    iff_1 = -1 if high > xHHM[1] and time > timestamp(2018, 1, 1, 9, 30) else nz(pos[1], 0)
    pos = 1 if low < xLLM[1] and time > timestamp(2018, 1, 1, 9, 30) else iff_1
    iff_2 = 1 if reverse and pos == -1 else pos
    possig = -1 if reverse and pos == 1 else iff_2
    if possig == 1 and possig[1] != possig and (time > timestamp(2018, 1, 1, 9, 30)):
        strategy.entry('Long', strategy.long)
    if possig == -1 and possig[1] != possig and (time > timestamp(2018, 1, 1, 9, 30)):
        strategy.entry('Short', strategy.short)
    barcolor(color.red if possig == -1 else color.green if possig == 1 else color.blue)
    plot(xHHM, color=color.new(color.blue, 0), title='MA')
    plot(xLLM, color=color.new(color.blue, 0), title='MA')
    plot(xHH, color=color.new(color.red, 0), title='MA')
    plot(xLL, color=color.new(color.red, 0), title='MA')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
