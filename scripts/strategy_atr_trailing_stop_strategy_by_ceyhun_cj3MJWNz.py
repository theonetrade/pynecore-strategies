"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    barcolor, close, color, display, fill, high, input, low, math, na, nz,
    plot, script, strategy, ta
)
from pynecore.types import Series


@script.strategy('ATR Trailing Stop Strategy by ceyhun', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    SC: Series[float] = input(close, 'Source'),
    AP1=input(5, 'Fast ATR period'),
    AF1=input(0.5, 'Fast ATR multiplier'),
    AP2=input(10, 'Slow ATR period'),
    AF2=input.float(3, 'Slow ATR multiplier'),
    plotcolor=input(True, 'Paint color on chart')
):
    SL1 = AF1 * ta.atr(AP1)
    Trail1: Series[float] = 0.0
    iff_1 = SC - SL1 if SC > nz(Trail1[1], 0) else SC + SL1
    iff_2 = math.min(nz(Trail1[1], 0), SC + SL1) if SC < nz(Trail1[1], 0) and SC[1] < nz(Trail1[1], 0) else iff_1
    Trail1 = math.max(nz(Trail1[1], 0), SC - SL1) if SC > nz(Trail1[1], 0) and SC[1] > nz(Trail1[1], 0) else iff_2
    SL2 = AF2 * ta.atr(AP2)
    Trail2: Series[float] = 0.0
    iff_3 = SC - SL2 if SC > nz(Trail2[1], 0) else SC + SL2
    iff_4 = math.min(nz(Trail2[1], 0), SC + SL2) if SC < nz(Trail2[1], 0) and SC[1] < nz(Trail2[1], 0) else iff_3
    Trail2 = math.max(nz(Trail2[1], 0), SC - SL2) if SC > nz(Trail2[1], 0) and SC[1] > nz(Trail2[1], 0) else iff_4
    Green = Trail1 > Trail2 and close > Trail2 and (low > Trail2)
    Blue = Trail1 > Trail2 and close > Trail2 and (low < Trail2)
    Red = Trail2 > Trail1 and close < Trail2 and (high < Trail2)
    Yellow = Trail2 > Trail1 and close < Trail2 and (high > Trail2)
    Bull = ta.barssince(Green) < ta.barssince(Red)
    Bear = ta.barssince(Red) < ta.barssince(Green)
    Buy = ta.crossover(Trail1, Trail2)
    Sell = ta.crossunder(Trail1, Trail2)
    TS1 = plot(Trail1, 'Fast Trail', style=plot.style_line, color=color.blue if Trail1 > Trail2 else color.yellow, linewidth=2, display=display.none)
    TS2 = plot(Trail2, 'Slow Trail', style=plot.style_line, color=color.green if Trail1 > Trail2 else color.red, linewidth=2)
    fill(TS1, TS2, color.new(color.green, 90) if Bull else color.new(color.red, 90))
    bcl = (color.blue if Blue else color.lime if Green else color.yellow if Yellow else color.red if Red else color.white) if plotcolor == cast_bool(1) else na
    barcolor(bcl)
    if Buy:
        strategy.entry('Buy', strategy.long, comment='Buy')
    if Sell:
        strategy.entry('Sell', strategy.short, comment='Sell')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
