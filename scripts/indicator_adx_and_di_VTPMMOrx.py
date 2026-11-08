"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, high, hline, input, low, math, nz, plot, script, ta
from pynecore.types import Series


@script.indicator('ADX and DI for v4', na_bool=True)
def main(
    len=input(14),
    th=input(20)
):
    TrueRange = math.max(math.max(high - low, math.abs(high - nz(close[1]))), math.abs(low - nz(close[1])))
    DirectionalMovementPlus = math.max(high - nz(high[1]), 0) if high - nz(high[1]) > nz(low[1]) - low else 0
    DirectionalMovementMinus = math.max(nz(low[1]) - low, 0) if nz(low[1]) - low > high - nz(high[1]) else 0
    SmoothedTrueRange: Series[float] = 0.0
    SmoothedTrueRange = nz(SmoothedTrueRange[1]) - nz(SmoothedTrueRange[1]) / len + TrueRange
    SmoothedDirectionalMovementPlus: Series[float] = 0.0
    SmoothedDirectionalMovementPlus = nz(SmoothedDirectionalMovementPlus[1]) - nz(SmoothedDirectionalMovementPlus[1]) / len + DirectionalMovementPlus
    SmoothedDirectionalMovementMinus: Series[float] = 0.0
    SmoothedDirectionalMovementMinus = nz(SmoothedDirectionalMovementMinus[1]) - nz(SmoothedDirectionalMovementMinus[1]) / len + DirectionalMovementMinus
    DIPlus = SmoothedDirectionalMovementPlus / SmoothedTrueRange * 100
    DIMinus = SmoothedDirectionalMovementMinus / SmoothedTrueRange * 100
    DX = math.abs(DIPlus - DIMinus) / (DIPlus + DIMinus) * 100
    ADX = ta.sma(DX, len)
    plot(DIPlus, color=color.new(color.green, 0), title='DI+')
    plot(DIMinus, color=color.new(color.red, 0), title='DI-')
    plot(ADX, color=color.new(color.navy, 0), title='ADX')
    hline(th, color=color.black)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
