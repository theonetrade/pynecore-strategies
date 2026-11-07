"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, hl2, input, location, na, plot, plotshape,
    script, shape, size, strategy, ta, time, timestamp
)


@script.strategy(title='EMA Crossover Strategy', shorttitle='EMA COS', overlay=True, pyramiding=0, default_qty_type=strategy.percent_of_equity, default_qty_value=10, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0.1, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    start_year=input(defval=2020, title='Backtest Start Year'),
    length=input.int(defval=20, minval=1, title='Length'),
    ratio=input.int(defval=3, title='Multiplier (3x length, 4x length, etc)', options=(3, 4, 5, 6, 7, 8, 9, 10)),
    longOnly=input(defval=False, title='Long Only')
):
    fast = ta.ema(hl2, length)
    slow = ta.ema(hl2, length * ratio)
    plot(fast, linewidth=2, color=color.new(color.orange, 0), title='Fast')
    plot(slow, linewidth=2, color=color.new(color.blue, 0), title='Slow')
    longEntry = ta.crossover(fast, slow)
    shortEntry = ta.crossunder(fast, slow)
    plotshape(close if longEntry else na, style=shape.triangleup, color=color.new(color.green, 0), location=location.belowbar, size=size.small, title='Long Triangle')
    plotshape(close if shortEntry and (not longOnly) else na, style=shape.triangledown, color=color.new(color.red, 0), location=location.abovebar, size=size.small, title='Short Triangle')
    plotshape(close if shortEntry and longOnly else na, style=shape.xcross, color=color.new(color.black, 0), location=location.abovebar, size=size.small, title='Exit Sign')
    def enterLong():
        return ta.crossover(fast, slow) and time > timestamp(start_year, 1, 1, 1, 1)

    def exitLong():
        crossunder_1 = ta.crossunder(fast, slow)
        return longOnly and crossunder_1

    if enterLong():
        strategy.entry(id='Long', direction=strategy.long)
    if exitLong():
        strategy.close(id='Long')
    def enterShort():
        crossunder_1 = ta.crossunder(fast, slow)
        return not longOnly and crossunder_1 and (time > timestamp(start_year, 1, 1, 1, 1))

    def exitShort():
        return False

    if enterShort():
        strategy.entry(id='Short', direction=strategy.short)
    if exitShort():
        strategy.close(id='Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
