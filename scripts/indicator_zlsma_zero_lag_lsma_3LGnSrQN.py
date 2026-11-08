"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, ta
from pynecore.types import Series


@script.indicator(title='ZLSMA - Zero Lag LSMA', shorttitle='ZLSMA', overlay=True, timeframe='', na_bool=True)
def main(
    length=input(title='Length', defval=32),
    offset=input(title='Offset', defval=0),
    src: Series[float] = input(close, title='Source')
):
    lsma = ta.linreg(src, length, offset)
    lsma2 = ta.linreg(lsma, length, offset)
    eq = lsma - lsma2
    zlsma = lsma + eq
    plot(zlsma, color=color.new(color.yellow, 0), linewidth=3)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
