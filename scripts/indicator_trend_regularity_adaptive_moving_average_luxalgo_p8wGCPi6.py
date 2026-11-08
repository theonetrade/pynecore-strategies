"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import close, color, input, math, nz, plot, script, ta
from pynecore.types import Series


@script.indicator('Trend Regularity Adaptive Moving Average', 'TRAMA [LuxAlgo]', overlay=True, na_bool=True)
def main(
    length=input(99),
    src: Series[float] = input(close)
):
    ama: Series[float] = 0.0
    hh = math.max(math.sign(ta.change(ta.highest(length))), 0)
    ll = math.max(math.sign(ta.change(ta.lowest(length)) * -1), 0)
    tc = math.pow(ta.sma(1 if cast_bool(hh) or cast_bool(ll) else 0, length), 2)
    ama = nz(ama[1] + tc * (src - ama[1]), src)
    plot(ama, 'Plot', color.new(color.new('#FF1100'), 0), 2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
