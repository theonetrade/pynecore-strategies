"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import color, high, input, low, plot, request, script, syminfo, ta


@script.indicator(title='ADR% - Average Daily Range %', overlay=False, na_bool=True)
def main(
    Length=input(20, title='length')
):
    dhigh = request.security(syminfo.tickerid, 'D', high)
    dlow = request.security(syminfo.tickerid, 'D', low)
    ADR = 100 * (ta.sma(dhigh / dlow, Length) - 1)
    plot(ADR, color=color.new(color.orange, 0), title='ADR', linewidth=1)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
