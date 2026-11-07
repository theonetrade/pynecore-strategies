"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import barcolor, close, color, high, input, low, math, nz, script, strategy, ta
from pynecore.types import Series


@script.strategy(title='Combo Backtest 123 Reversal & Statistical Volatility', shorttitle='Combo', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    line1=input(True, '---- 123 Reversal ----'),
    Length=input.int(14, minval=1),
    KSmoothing=input.int(1, minval=1),
    DLength=input.int(3, minval=1),
    Level=input.int(50, minval=1),
    line2=input(True, '---- Statistical Volatility ----'),
    LengthSV=input.int(30, minval=1),
    TopBand=input.float(0.005, step=0.001),
    LowBand=input.float(0.0016, step=0.001),
    reverse=input(False, title='Trade reverse')
):
    def Reversal123(Length, KSmoothing, DLength, Level):
        vFast = ta.sma(ta.stoch(close, high, low, Length), KSmoothing)
        vSlow = ta.sma(vFast, DLength)
        pos: Series[float] = 0.0
        iff_1 = -1 if close[2] > close[1] and close < close[1] and (vFast > vSlow) and (vFast < Level) else nz(pos[1], 0)
        pos = 1 if close[2] < close[1] and close > close[1] and (vFast < vSlow) and (vFast > Level) else iff_1
        return pos

    def SV(Length, TopBand, LowBand):
        pos: Series[float] = 0.0
        xMaxC = ta.highest(close, Length)
        xMaxH = ta.highest(high, Length)
        xMinC = ta.lowest(close, Length)
        xMinL = ta.lowest(low, Length)
        SqrTime = math.sqrt(253 / Length)
        Vol = (0.6 * math.log(xMaxC / xMinC) * SqrTime + 0.6 * math.log(xMaxH / xMinL) * SqrTime) * 0.5
        iff_1 = 2.99 if Vol > 2.99 else Vol
        nRes = 0 if Vol < 0 else iff_1
        iff_2 = -1 if nRes < LowBand else nz(pos[1], 0)
        pos = 1 if nRes > TopBand else iff_2
        return pos

    posReversal123 = Reversal123(Length, KSmoothing, DLength, Level)
    posSV = SV(LengthSV, TopBand, LowBand)
    iff_1 = -1 if posReversal123 == -1 and posSV == -1 else 0
    pos = 1 if posReversal123 == 1 and posSV == 1 else iff_1
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
