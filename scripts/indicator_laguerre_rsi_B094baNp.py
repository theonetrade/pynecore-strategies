"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import alertcondition, close, color, input, nz, plot, script, ta
from pynecore.types import Series


@script.indicator('Laguerre RSI', shorttitle='LaRSI', overlay=False, timeframe='')
def main(
    src: Series[float] = input(title='Source', defval=close),
    alpha=input.float(title='Alpha', minval=0, maxval=1, step=0.1, defval=0.2),
    colorchange=input(title='Change Color ?', defval=False)
):
    gamma = 1 - alpha
    L0: Series[float] = 0.0
    L0 = (1 - gamma) * src + gamma * nz(L0[1])
    L1: Series[float] = 0.0
    L1 = -gamma * L0 + nz(L0[1]) + gamma * nz(L1[1])
    L2: Series[float] = 0.0
    L2 = -gamma * L1 + nz(L1[1]) + gamma * nz(L2[1])
    L3: Series[float] = 0.0
    L3 = -gamma * L2 + nz(L2[1]) + gamma * nz(L3[1])
    cu = (L0 - L1 if L0 > L1 else 0) + (L1 - L2 if L1 > L2 else 0) + (L2 - L3 if L2 > L3 else 0)
    cd = (L1 - L0 if L0 < L1 else 0) + (L2 - L1 if L1 < L2 else 0) + (L3 - L2 if L2 < L3 else 0)
    temp = -1 if cu + cd == 0 else cu + cd
    LaRSI: Series = 0 if temp == -1 else cu / temp
    Color__ren__ = (color.green if LaRSI > LaRSI[1] else color.red) if colorchange else color.blue
    plot(100 * LaRSI, title='LaRSI', linewidth=2, color=Color__ren__)
    plot(20, linewidth=1, color=color.new(color.maroon, 0))
    plot(80, linewidth=1, color=color.new(color.maroon, 0))
    alertcondition(ta.crossover(100 * LaRSI, 20), title='LaRSI Crossover Alarm', message='Laguerre RSI crosses OVER 20 - BUY SIGNAL!')
    alertcondition(ta.crossunder(100 * LaRSI, 80), title='Price Crossunder Alarm', message='Laguerre RSI crosses UNDER 80 - SELL SIGNAL!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)