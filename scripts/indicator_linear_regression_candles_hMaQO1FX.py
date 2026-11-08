"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, format, high, input, low, na, open, plot, plotcandle,
    script, ta
)


@script.indicator(title='Humble LinReg Candles', shorttitle='LinReg Candles', format=format.price, precision=4, overlay=True, na_bool=True)
def main(
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=200, defval=11),
    sma_signal=input(title='Simple MA (Signal Line)', defval=True),
    lin_reg=input(title='Lin Reg', defval=True),
    linreg_length=input.int(title='Linear Regression Length', minval=1, maxval=200, defval=11)
):
    bopen = ta.linreg(open, linreg_length, 0) if lin_reg else open
    bhigh = ta.linreg(high, linreg_length, 0) if lin_reg else high
    blow = ta.linreg(low, linreg_length, 0) if lin_reg else low
    bclose = ta.linreg(close, linreg_length, 0) if lin_reg else close
    r = bopen < bclose
    signal = ta.sma(bclose, signal_length) if sma_signal else ta.ema(bclose, signal_length)
    plotcandle(bopen if r else na, bhigh if r else na, blow if r else na, bclose if r else na, title='LinReg Candles', color=color.green, wickcolor=color.green, bordercolor=color.green, editable=True)
    plotcandle(na if r else bopen, na if r else bhigh, na if r else blow, na if r else bclose, title='LinReg Candles', color=color.red, wickcolor=color.red, bordercolor=color.red, editable=True)
    plot(signal, color=color.new(color.white, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
