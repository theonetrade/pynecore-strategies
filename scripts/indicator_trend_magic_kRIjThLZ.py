"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, format, high, input, low, nz, plot, script,
    ta
)
from pynecore.types import Series


@script.indicator('Trend Magic', shorttitle='TM', overlay=True, format=format.price, precision=2, timeframe='', na_bool=True)
def main(
    period=input(20, 'CCI period'),
    coeff=input(1, 'ATR Multiplier'),
    AP=input(5, 'ATR Period'),
    src: Series[float] = input(close)
):
    ATR = ta.sma(ta.tr, AP)
    upT = low - ATR * coeff
    downT = high + ATR * coeff
    MagicTrend: Series[float] = 0.0
    MagicTrend = (nz(MagicTrend[1]) if upT < nz(MagicTrend[1]) else upT) if ta.cci(src, period) >= 0 else nz(MagicTrend[1]) if downT > nz(MagicTrend[1]) else downT
    color1 = color.new('#0022FC') if ta.cci(src, period) >= 0 else color.new('#FC0400')
    plot(MagicTrend, color=color1, linewidth=3)
    alertcondition(ta.cross(close, MagicTrend), title='Cross Alert', message='Price - MagicTrend Crossing!')
    alertcondition(ta.crossover(low, MagicTrend), title='CrossOver Alarm', message='BUY SIGNAL!')
    alertcondition(ta.crossunder(high, MagicTrend), title='CrossUnder Alarm', message='SELL SIGNAL!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
