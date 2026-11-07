"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, fill, input, math, nz, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy('Grover Llorens Activator', margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    length=input(480),
    mult=input(14),
    src: Series[float] = input(close)
):
    ts: Series[float] = 0.0
    diff = src - nz(ts[1], src[1])
    atr = ta.atr(length)
    up = ta.crossover(diff, 0)
    dn = ta.crossunder(diff, 0)
    val = ta.valuewhen(up or dn, atr / length, 0)
    bars = ta.barssince(up or dn)
    ts = nz(ts[1], src) - atr * mult if up else nz(ts[1], src) + atr * mult if dn else nz(ts[1], src) + math.sign(diff) * val * bars
    if up:
        strategy.entry('Buy', strategy.long)
    if dn:
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
