"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import color, fill, high, input, low, na, plot, script, strategy, ta
from pynecore.types import PersistentSeries, Series


@script.strategy('Grab Trading System', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    flb=input.int(defval=80, title='Longterm Period', minval=1),
    slb=input.int(defval=21, title='Shortterm Period', minval=1),
    showtarget=input(defval=True, title='Show Target'),
    showtrend=input(defval=True, title='Show Trend')
):
    major_resistance: Series = ta.highest(flb)
    major_support: Series = ta.lowest(flb)
    minor_resistance: Series = ta.highest(slb)
    minor_support: Series = ta.lowest(slb)
    trend: PersistentSeries[int] = 0
    trend = 1 if high > major_resistance[1] else -1 if low < major_support[1] else trend
    if trend == 1 and low[1] == minor_support[1] and (low > minor_support):
        strategy.entry('Buy', strategy.long)
    if trend == -1 and high[1] == minor_resistance[1] and (high < minor_resistance):
        strategy.entry('Sell', strategy.short)
    if strategy.position_size > 0:
        strategy.exit('Buy', stop=major_support, comment='Stop Buy')
        if high[1] == minor_resistance[1] and high < minor_resistance:
            strategy.close('Buy', comment='Close Buy')
    if strategy.position_size < 0:
        strategy.exit('Sell', stop=major_resistance, comment='Stop Sell')
        if low[1] == minor_support[1] and low > minor_support:
            strategy.close('Sell', comment='Close Sell')
    change_1 = ta.change(trend)
    if strategy.position_size != 0 and cast_bool(change_1):
        strategy.close_all()
    majr = plot(major_resistance, color=color.red if showtrend and trend == -1 and (trend[1] == -1) else na)
    majs = plot(major_support, color=color.lime if showtrend and trend == 1 and (trend[1] == 1) else na)
    minr = plot(minor_resistance, color=color.yellow if showtarget and trend == 1 and (strategy.position_size > 0) else na, style=plot.style_circles)
    mins = plot(minor_support, color=color.yellow if showtarget and trend == -1 and (strategy.position_size < 0) else na, style=plot.style_circles)
    fill(majs, mins, color=color.new(color.lime, 85) if showtrend and trend == 1 and (trend[1] == 1) else na)
    fill(majr, minr, color=color.new(color.red, 85) if showtrend and trend == -1 and (trend[1] == -1) else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
