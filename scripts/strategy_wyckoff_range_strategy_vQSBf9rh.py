"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, close, color, high, input, location, low, plotshape, script,
    shape, strategy, ta
)


@script.strategy('Wyckoff Range Strategy by deperp', overlay=True, initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, margin_long=0, margin_short=0, close_by_id=True)
def main(
    AccumulationLength=input(32, 'Accumulation'),
    DistributionLength=input(35, 'Distribution'),
    SpringLength=input(10, 'Spring'),
    UpthrustLength=input(20, 'Upthrust'),
    stopPercentage=input(10, 'Stop Percentage')
):
    isAccumulation = ta.crossover(close, ta.sma(close, AccumulationLength))
    isDistribution = ta.crossunder(close, ta.sma(close, DistributionLength))
    isSpring = ta.crossover(low, ta.sma(low, SpringLength))
    isUpthrust = ta.crossunder(high, ta.sma(high, UpthrustLength))
    enterLong = isAccumulation and isSpring
    enterShort = isDistribution and isUpthrust
    if enterLong:
        strategy.close('Short')
        strategy.entry('Long', strategy.long, comment='Enter Long')
        alert('Enter Long Position')
    if enterShort:
        strategy.close('Long')
        strategy.entry('Short', strategy.short, comment='Enter Short')
        alert('Enter Short Position')
    stopLossLevelLong = close * (1 - stopPercentage / 100)
    stopLossLevelShort = close * (1 + stopPercentage / 100)
    strategy.exit('Stop Loss Long', 'Long', stop=stopLossLevelLong)
    strategy.exit('Stop Loss Short', 'Short', stop=stopLossLevelShort)
    plotshape(isAccumulation, title='Accumulation Phase', location=location.belowbar, color=color.green, style=shape.labelup, text='Accumulation')
    plotshape(isDistribution, title='Distribution Phase', location=location.abovebar, color=color.red, style=shape.labeldown, text='Distribution')
    plotshape(isSpring, title='Spring', location=location.belowbar, color=color.blue, style=shape.triangleup)
    plotshape(isUpthrust, title='Upthrust', location=location.abovebar, color=color.orange, style=shape.triangledown)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)