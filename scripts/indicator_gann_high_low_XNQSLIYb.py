"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import alertcondition, close, color, high, input, low, nz, plot, script, ta


@script.indicator('Gann High Low', overlay=True)
def main(
    HPeriod=input(13, 'HIGH Period'),
    LPeriod=input(21, 'LOW Period')
):
    iff_1 = -1 if close < inline_series(nz(ta.sma(low, LPeriod)), 1) else 0
    HLd = 1 if close > inline_series(nz(ta.sma(high, HPeriod)), 1) else iff_1
    HLv = ta.valuewhen(HLd != 0, HLd, 0)
    sma_1 = ta.sma(high, HPeriod)
    sma_2 = ta.sma(low, LPeriod)
    HiLo = sma_1 if HLv == -1 else sma_2
    HLcolor = color.maroon if HLv == -1 else color.blue
    plot(HiLo, linewidth=2, color=HLcolor)
    alertcondition(ta.cross(close, HiLo), title='Price Cross Alert', message='Price - HiLo Crossing!')
    alertcondition(ta.crossover(close, HiLo), title='PRICE CrossOver Alarm', message='LAST PRICE is ABOVE HiLo')
    alertcondition(ta.crossunder(close, HiLo), title='PRICE CrossUnder Alarm', message='LAST PRICE is BELOW HiLo!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
