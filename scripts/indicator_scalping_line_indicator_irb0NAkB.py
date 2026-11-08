"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import alertcondition, close, color, fill, input, math, plot, script, ta
from pynecore.types import Series


@script.indicator('Scalping Line', overlay=False, na_bool=True)
def main(
    src: Series[float] = input(close, title='Source'),
    percent=input.float(1.0, 'Percent', step=0.1, minval=0),
    mainperiod=input(100, 'Main Period'),
    signalperiod=input(7, 'Signal Period')
):
    MA = ta.sma(ta.sma(src, math.ceil(mainperiod / 2)), math.floor(mainperiod / 2) + 1)
    ssMA = MA if MA > close + MA * percent / 100 else MA if MA < close - MA * percent / 100 else close
    signalline = ta.sma(close, signalperiod)
    ScalpLine = signalline - ssMA
    k1 = plot(ScalpLine, 'SLI', color.new(color.maroon, 0), 2)
    k2 = plot(0, '')
    color1 = color.green if ScalpLine >= 0 else color.red
    fill(k1, k2, color=color.new(color1, 80))
    alertcondition(ta.crossover(ScalpLine, 0), title='BUY ALARM!', message='SLI BUY Signal!')
    alertcondition(ta.crossunder(ScalpLine, 0), title='SELL ALARM!', message='SLI SELL Signal!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
