"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import color, input, low, plot, request, script, syminfo, ta


@script.indicator('Trailing Stop Loss', 'TSL', overlay=True, na_bool=True)
def main(
    res=input.timeframe(title='Time Frame', defval='D')
):
    K1 = ta.valuewhen(low > low[1], low[1], 1)
    TSL = request.security(syminfo.tickerid, res, K1)
    plot(TSL, linewidth=2, color=color.new(color.purple, 0), title='TSL')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
