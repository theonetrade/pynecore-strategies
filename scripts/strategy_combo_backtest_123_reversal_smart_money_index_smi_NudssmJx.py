"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, close, color, high, input, low, nz, open, request, script,
    strategy, syminfo, ta
)
from pynecore.types import Series


@script.strategy(title='Combo Backtest 123 Reversal & Smart Money Index (SMI)', shorttitle='Combo', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    line1=input(True, '---- 123 Reversal ----'),
    Length=input.int(14, minval=1),
    KSmoothing=input.int(1, minval=1),
    DLength=input.int(3, minval=1),
    Level=input.int(50, minval=1),
    line2=input(True, '---- Smart Money Index (SMI) ----'),
    LengthSMI=input.int(18, minval=1),
    res=input.timeframe(title='Resolution', defval='D'),
    reverse=input(False, title='Trade reverse')
):
    def Reversal123(Length, KSmoothing, DLength, Level):
        vFast = ta.sma(ta.stoch(close[1], high[1], low[1], Length), KSmoothing)
        vSlow = ta.sma(vFast, DLength)
        pos: Series[float] = 0.0
        iff_1 = -1 if close[3] > close[2] and close[1] < close[2] and (vFast > vSlow) and (vFast < Level) else nz(pos[1], 0)
        pos = 1 if close[3] < close[2] and close[1] > close[2] and (vFast < vSlow) and (vFast > Level) else iff_1
        return pos

    def SMI(Length, tf):
        pos: Series[float] = 0.0
        nRes: Series[float] = 0.0
        xcloseH1 = request.security(syminfo.tickerid, tf, close[1])
        xopenH1 = request.security(syminfo.tickerid, tf, open[1])
        nRes = nz(nRes[1], 1) - (open - close) + xopenH1 - xcloseH1
        xSmaRes = ta.sma(nRes, Length)
        iff_1 = -1 if xSmaRes < nRes else nz(pos[1], 0)
        pos = 1 if xSmaRes > nRes else iff_1
        return pos

    posReversal123 = Reversal123(Length, KSmoothing, DLength, Level)
    posSMI = SMI(LengthSMI, res)
    iff_1 = -1 if posReversal123 == -1 and posSMI == -1 else 0
    pos = 1 if posReversal123 == 1 and posSMI == 1 else iff_1
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
