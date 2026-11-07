"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, fill, input, math, nz, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy('Uhl MA System - Strategy Analysis', margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    length=input(100),
    mult=input(1.0),
    src: Series[float] = input(close)
):
    out: float = 0.0
    cma: Series[float] = 0.0
    cts: Series[float] = 0.0
    Var = ta.variance(src, length)
    sma = ta.sma(src, length)
    secma = math.pow(nz(sma - cma[1]), 2)
    sects = math.pow(nz(src - cts[1]), 2)
    ka = 1 - Var / secma if Var < secma else 0
    kb = 1 - Var / sects if Var < sects else 0
    cma = ka * sma + (1 - ka) * nz(cma[1], src)
    cts = kb * src + (1 - kb) * nz(cts[1], src)
    if ta.crossover(cts, cma):
        strategy.entry('Buy', strategy.long)
    if ta.crossunder(cts, cma):
        strategy.entry('Sell', strategy.short)
    cap = strategy.initial_capital
    eq = strategy.equity
    rmax: Series[float] = 0.0
    rmax = math.max(eq, nz(rmax[1]))
    css = color.new('#0CB51A') if eq > cap else color.new('#E65100')
    a = plot(eq, 'Equity', color.new(color.new('#2196F3'), 0), 2)
    b = plot(rmax, 'Maximum', css, 2)
    fill(a, b, color.new(css, 80))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
