"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import alert, barcolor, close, color, input, nz, plot, script, ta
from pynecore.types import Series


@script.indicator(title='Trend Trader Strategy', overlay=True)
def main(
    Length=input.int(21, minval=1),
    Multiplier=input.float(3, minval=1e-06)
):
    avgTR: Series = ta.wma(ta.atr(1), Length)
    highestC: Series = ta.highest(Length)
    lowestC: Series = ta.lowest(Length)
    hiLimit = highestC[1] - avgTR[1] * Multiplier
    loLimit = lowestC[1] + avgTR[1] * Multiplier
    ret: Series[float] = 0.0
    pos: Series[float] = 0.0
    ret = hiLimit if close > hiLimit and close > loLimit else loLimit if close < loLimit and close < hiLimit else nz(ret[1], close)
    pos = 1 if close > ret else -1 if close < ret else nz(pos[1], 0)
    if pos != pos[1] and pos == 1:
        alert('Color changed - Buy', alert.freq_once_per_bar_close)
    if pos != pos[1] and pos == -1:
        alert('Color changed - Sell', alert.freq_once_per_bar_close)
    barcolor(color.red if pos == -1 else color.green if pos == 1 else color.blue)
    plot(ret, color=color.new(color.blue, 0), title='Trend Trader Strategy')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
