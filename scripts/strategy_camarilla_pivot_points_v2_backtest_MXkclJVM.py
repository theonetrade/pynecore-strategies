"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, close, color, high, input, low, nz, request, script, strategy,
    syminfo
)
from pynecore.types import Series


@script.strategy(title='Camarilla Pivot Points V2 Backtest', shorttitle='CPP V2', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    res=input.timeframe(title='Resolution', defval='D'),
    width=input.int(1, minval=1),
    SellFrom=input.string(title='Sell from ', defval='R1', options=('R1', 'R2', 'R3', 'R4')),
    BuyFrom=input.string(title='Buu from ', defval='S1', options=('S1', 'S2', 'S3', 'S4')),
    reverse=input(False, title='Trade reverse')
):
    xHigh = request.security(syminfo.tickerid, res, high)
    xLow = request.security(syminfo.tickerid, res, low)
    xClose = request.security(syminfo.tickerid, res, close)
    H4 = 0.55 * (xHigh - xLow) + xClose
    H3 = 0.275 * (xHigh - xLow) + xClose
    H2 = 0.183 * (xHigh - xLow) + xClose
    H1 = 0.0916 * (xHigh - xLow) + xClose
    L1 = xClose - 0.0916 * (xHigh - xLow)
    L2 = xClose - 0.183 * (xHigh - xLow)
    L3 = xClose - 0.275 * (xHigh - xLow)
    L4 = xClose - 0.55 * (xHigh - xLow)
    pos: Series[int] = 0
    iff_1 = H4 if BuyFrom == 'S4' else 0
    iff_2 = H3 if BuyFrom == 'S3' else iff_1
    iff_3 = H2 if BuyFrom == 'S2' else iff_2
    S = H1 if BuyFrom == 'S1' else iff_3
    iff_4 = L4 if SellFrom == 'R4' else 0
    iff_5 = L3 if SellFrom == 'R3' else iff_4
    iff_6 = L2 if SellFrom == 'R2' else iff_5
    B = L1 if SellFrom == 'R1' else iff_6
    iff_7 = -1 if close < S else nz(pos[1], 0)
    pos = 1 if close > B else iff_7
    iff_8 = 1 if reverse and pos == -1 else pos
    possig = -1 if reverse and pos == 1 else iff_8
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
