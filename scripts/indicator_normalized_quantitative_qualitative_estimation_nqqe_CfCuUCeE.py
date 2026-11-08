"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, hline, input, location, math, na, nz, plot,
    plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator(' Normalized Quantitative Qualitative Estimation', shorttitle='nQQE', precision=4, timeframe='', na_bool=True)
def main(
    src: Series[float] = input(close),
    length=input.int(14, 'RSI Length', minval=1),
    SSF=input.int(5, 'SF RSI SMoothing Factor', minval=1),
    showsignals=input(title='Show Crossing Signals?', defval=False)
):
    RSII: Series = ta.ema(ta.rsi(src, length), SSF)
    TR = math.abs(RSII - RSII[1])
    wwalpha = 1 / length
    WWMA: Series[float] = 0.0
    WWMA = wwalpha * TR + (1 - wwalpha) * nz(WWMA[1])
    ATRRSI: Series[float] = 0.0
    ATRRSI = wwalpha * WWMA + (1 - wwalpha) * nz(ATRRSI[1])
    QQEF: Series = ta.ema(ta.rsi(src, length), SSF)
    QUP = QQEF + ATRRSI * 4.236
    QDN = QQEF - ATRRSI * 4.236
    QQES: Series[float] = 0.0
    QQES = QUP if QUP < nz(QQES[1]) else QDN if QQEF > nz(QQES[1]) and QQEF[1] < nz(QQES[1]) else QDN if QDN > nz(QQES[1]) else QUP if QQEF < nz(QQES[1]) and QQEF[1] > nz(QQES[1]) else nz(QQES[1])
    Colorh = color.new('#007002') if QQEF - 50 > 10 else color.red if QQEF - 50 < -10 else color.new('#E8E81A')
    QQF = plot(QQEF - 50, 'FAST', color=color.new(color.maroon, 0), linewidth=2)
    plot(QQEF - 50, color=Colorh, linewidth=2, style=plot.style_columns)
    QQS = plot(QQES - 50, 'SLOW', color=color.new(color.new('#0007E1'), 0), linewidth=2)
    hline(10, color=color.gray, linestyle=hline.style_dashed)
    hline(-10, color=color.gray, linestyle=hline.style_dashed)
    buySignalr = ta.crossover(QQEF, QQES)
    plotshape((QQES - 50) * 0.995 if buySignalr and showsignals else na, title='Buy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))
    sellSignallr = ta.crossunder(QQEF, QQES)
    plotshape((QQES - 50) * 1.005 if sellSignallr and showsignals else na, title='Sell', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))
    alertcondition(ta.cross(QQEF, QQES), title='Cross Alert', message='QQE Crossing Signal!')
    alertcondition(ta.crossover(QQEF, QQES), title='Crossover Alarm', message='QQE BUY SIGNAL!')
    alertcondition(ta.crossunder(QQEF, QQES), title='Crossunder Alarm', message='QQE SELL SIGNAL!')
    alertcondition(ta.crossover(QQEF, 50), title='Cross 0 Up Alert', message='QQE FAST Crossing 0 UP!')
    alertcondition(ta.crossunder(QQEF, 50), title='Cross 0 Down Alert', message='QQE FAST Crossing 0 DOWN!')
    alertcondition(ta.crossover(QQEF, 60), title='Cross 10 Up Alert', message='QQE Above 10 UPTREND SIGNAL!')
    alertcondition(ta.crossunder(QQEF, 40), title='Cross -10 Down Alert', message='QQE Below -10 DOWNTREND SIGNAL!')
    crossover_1 = ta.crossover(QQEF, 40)
    alertcondition(ta.crossunder(QQEF, 60) or crossover_1, title='SIDEWAYS', message='QQE Entering Sideways Market!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
