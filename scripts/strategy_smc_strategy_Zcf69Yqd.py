"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, location, low, na, plot, plotshape, script,
    shape, strategy, ta
)
from pynecore.types import Persistent


@script.strategy('SMC Strategy with Premium, Equilibrium, and Discount Zones', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=10, margin_long=0, margin_short=0, initial_capital=1000000, close_by_id=True)
def main(
    swingHighLength=input.int(8, title='Swing High Length'),
    swingLowLength=input.int(8, title='Swing Low Length'),
    smaLength=input.int(50, title='SMA Length'),
    orderBlockLength=input.int(20, title='Order Block Length')
):
    swingHigh: Persistent[float] = na(float)
    swingLow: Persistent[float] = na(float)
    if ta.highestbars(high, swingHighLength) == 0:
        swingHigh = high
    if ta.lowestbars(low, swingLowLength) == 0:
        swingLow = low
    equilibrium = (swingHigh + swingLow) / 2
    premiumZone = swingHigh
    discountZone = swingLow
    plot(equilibrium, title='Equilibrium', color=color.blue, linewidth=2)
    plot(premiumZone, title='Premium Zone (Resistance)', color=color.red, linewidth=1)
    plot(discountZone, title='Discount Zone (Support)', color=color.green, linewidth=1)
    sma = ta.sma(close, smaLength)
    plot(sma, title='SMA', color=color.orange)
    buySignal = close < equilibrium and close > discountZone and (close > sma)
    sellSignal = close > equilibrium and close < premiumZone and (close < sma)
    orderBlockHigh = ta.highest(high, orderBlockLength)
    orderBlockLow = ta.lowest(low, orderBlockLength)
    buySignalOB = buySignal and close >= orderBlockLow
    sellSignalOB = sellSignal and close <= orderBlockHigh
    if buySignalOB:
        strategy.entry('Buy', strategy.long)
    if sellSignalOB:
        strategy.entry('Sell', strategy.short)
    plotshape(buySignalOB, title='Buy Signal', location=location.belowbar, color=color.green, style=shape.labelup, text='BUY')
    plotshape(sellSignalOB, title='Sell Signal', location=location.abovebar, color=color.red, style=shape.labeldown, text='SELL')
    liquidityZoneHigh = ta.valuewhen(high == swingHigh, high, 0)
    liquidityZoneLow = ta.valuewhen(low == swingLow, low, 0)
    plot(liquidityZoneHigh, title='Liquidity Zone High', color=color.red, linewidth=1, style=plot.style_cross)
    plot(liquidityZoneLow, title='Liquidity Zone Low', color=color.green, linewidth=1, style=plot.style_cross)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
