"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, close, color, high, hl2, input, low, math, nz, script,
    strategy, ta, time, timestamp
)
from pynecore.types import Series

I1: str = '●═════ 2/20 EMA ═════●'
I2: str = '●═════ Accelerator Oscillator  ═════●'
misc: str = '●═════ MISC ═════●'
timePeriodHeader: str = '●═════ Time Start ═════●'


@script.strategy(title='Combo 2/20 EMA & Accelerator Oscillator (AC)', shorttitle='Combo', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    Length=input.int(14, minval=1, group=I1),
    nLengthSlow=input(33, title='Length Slow', group=I2),
    nLengthFast=input(6, title='Length Fast', group=I2),
    reverse=input.bool(False, title='Trade reverse', group=misc),
    d=input.int(1, title='From Day', minval=1, maxval=31, group=timePeriodHeader),
    m=input.int(1, title='From Month', minval=1, maxval=12, group=timePeriodHeader),
    y=input.int(2005, title='From Year', minval=0, group=timePeriodHeader)
):
    def EMA20(Length):
        pos: Series[float] = 0.0
        xPrice = close
        xXA = ta.ema(xPrice, Length)
        nHH = math.max(high, high[1])
        nLL = math.min(low, low[1])
        nXS = nLL if nLL > xXA or nHH < xXA else nHH
        iff_1 = 1 if nXS < close[1] else nz(pos[1], 0)
        pos = -1 if nXS > close[1] else iff_1
        return pos

    def AC(nLengthSlow, nLengthFast):
        pos: Series[float] = 0.0
        xSMA1_hl2 = ta.sma(hl2, nLengthFast)
        xSMA2_hl2 = ta.sma(hl2, nLengthSlow)
        xSMA1_SMA2 = xSMA1_hl2 - xSMA2_hl2
        xSMA_hl2 = ta.sma(xSMA1_SMA2, nLengthFast)
        nRes: Series = xSMA1_SMA2 - xSMA_hl2
        cClr = color.blue if nRes > nRes[1] else color.red
        iff_1 = 1 if nRes > 0 else nz(pos[1], 0)
        pos = -1 if nRes < 0 else iff_1
        return pos

    StartTrade = True if time > timestamp(y, m, d, 0, 0) else False
    posEMA20 = EMA20(Length)
    prePosAC = AC(nLengthSlow, nLengthFast)
    iff_1 = -1 if posEMA20 == -1 and prePosAC == -1 and StartTrade else 0
    pos = 1 if posEMA20 == 1 and prePosAC == 1 and StartTrade else iff_1
    iff_2 = 1 if reverse and pos == -1 else pos
    possig = -1 if reverse and pos == 1 else iff_2
    if possig == 1:
        strategy.entry('Long', strategy.long)
    if possig == -1:
        strategy.entry('Short', strategy.short)
    if possig == 0:
        strategy.close_all()
    barcolor(color.new('#B50404') if possig == -1 else color.new('#079605') if possig == 1 else color.new('#0536B3'))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
