"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import color, high, input, low, na, plot, script, ta
from pynecore.types import Series


@script.indicator('Support and Resistance', overlay=True, na_bool=True)
def main(
    left=input(10),
    right=input(10)
):
    hih = ta.pivothigh(high, left, right)
    lol = ta.pivotlow(low, left, right)
    top: Series = ta.valuewhen(cast_bool(hih), high[right], 0)
    bot: Series = ta.valuewhen(cast_bool(lol), low[right], 0)
    res = plot(top, color=na if top != top[1] else color.new('#00CED1'), offset=-left)
    sup = plot(bot, color=na if bot != bot[1] else color.new('#DC143C'), offset=-left)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
