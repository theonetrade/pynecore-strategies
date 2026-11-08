"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, fill, format, high, hlc3, input, location,
    low, na, nz, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Series


@script.indicator('AlphaTrend', shorttitle='AT', overlay=True, format=format.price, precision=2, timeframe='', na_bool=True)
def main(
    coeff=input.float(1, 'Multiplier', step=0.1),
    AP=input(14, 'Common Period'),
    src: Series[float] = input(close),
    showsignalsk=input(title='Show Signals?', defval=True),
    novolumedata=input(title='Change calculation (no volume data)?', defval=False)
):
    ATR = ta.sma(ta.tr, AP)
    upT = low - ATR * coeff
    downT = high + ATR * coeff
    AlphaTrend: Series[float] = 0.0
    AlphaTrend = (nz(AlphaTrend[1]) if upT < nz(AlphaTrend[1]) else upT) if (ta.rsi(src, AP) >= 50 if novolumedata else ta.mfi(hlc3, AP) >= 50) else nz(AlphaTrend[1]) if downT > nz(AlphaTrend[1]) else downT
    color1 = color.new('#00E60F') if AlphaTrend > AlphaTrend[2] else color.new('#80000B') if AlphaTrend < AlphaTrend[2] else color.new('#00E60F') if AlphaTrend[1] > AlphaTrend[3] else color.new('#80000B')
    k1 = plot(AlphaTrend, color=color.new(color.new('#0022FC'), 0), linewidth=3)
    k2 = plot(AlphaTrend[2], color=color.new(color.new('#FC0400'), 0), linewidth=3)
    fill(k1, k2, color=color1)
    buySignalk: Series = ta.crossover(AlphaTrend, AlphaTrend[2])
    sellSignalk: Series = ta.crossunder(AlphaTrend, AlphaTrend[2])
    K1 = ta.barssince(buySignalk)
    K2 = ta.barssince(sellSignalk)
    O1: Series = ta.barssince(buySignalk[1])
    O2: Series = ta.barssince(sellSignalk[1])
    plotshape(AlphaTrend[2] * 0.9999 if buySignalk and showsignalsk and (O1 > K2) else na, title='BUY', text='BUY', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.new('#0022FC'), 0), textcolor=color.new(color.white, 0))
    plotshape(AlphaTrend[2] * 1.0001 if sellSignalk and showsignalsk and (O2 > K1) else na, title='SELL', text='SELL', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.maroon, 0), textcolor=color.new(color.white, 0))
    alertcondition(buySignalk and O1 > K2, title='Potential BUY Alarm', message='BUY SIGNAL!')
    alertcondition(sellSignalk and O2 > K1, title='Potential SELL Alarm', message='SELL SIGNAL!')
    alertcondition(buySignalk[1] and O1[1] > K2, title='Confirmed BUY Alarm', message='BUY SIGNAL APPROVED!')
    alertcondition(sellSignalk[1] and O2[1] > K1, title='Confirmed SELL Alarm', message='SELL SIGNAL APPROVED!')
    alertcondition(ta.cross(close, AlphaTrend), title='Price Cross Alert', message='Price - AlphaTrend Crossing!')
    alertcondition(ta.crossover(low, AlphaTrend), title='Candle CrossOver Alarm', message='LAST BAR is ABOVE ALPHATREND')
    alertcondition(ta.crossunder(high, AlphaTrend), title='Candle CrossUnder Alarm', message='LAST BAR is BELOW ALPHATREND!')
    alertcondition(ta.cross(close[1], AlphaTrend[1]), title='Price Cross Alert After Bar Close', message='Price - AlphaTrend Crossing!')
    alertcondition(ta.crossover(low[1], AlphaTrend[1]), title='Candle CrossOver Alarm After Bar Close', message='LAST BAR is ABOVE ALPHATREND!')
    alertcondition(ta.crossunder(high[1], AlphaTrend[1]), title='Candle CrossUnder Alarm After Bar Close', message='LAST BAR is BELOW ALPHATREND!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
