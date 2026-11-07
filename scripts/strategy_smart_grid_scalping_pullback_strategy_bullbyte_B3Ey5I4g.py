"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, bar_index, close, color, high, input, line, location, low, open,
    plotshape, script, shape, strategy, ta
)
from pynecore.types import Persistent


@script.strategy("Smart Grid Scalping(Pullback) Strategy[BullByte]", overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=30, commission_type=strategy.commission.percent, commission_value=0.04, slippage=1)
def main(
    atrLen=input.int(10, "ATR Length"),
    gridFactor=input.float(0.35, "Grid Factor"),
    profitTarget=input.float(0.004, "Profit Target", step=0.0001),
    noTradeZone=input.float(0.003, "No-Trade Zone (%)", step=0.0001),
    shortLevel=input.int(5, "Short Trigger Level", minval=0, maxval=14),
    longLevel=input.int(5, "Long Trigger Level", minval=0, maxval=14),
    minRSIShort=input.int(70, "Min RSI for Short"),
    maxRSILong=input.int(30, "Max RSI for Long")
):
    atr = ta.atr(atrLen)
    rsi = ta.rsi(close, 14)
    basePrice = close[20]

    gridUp: Persistent[list[float]] = array.new_float(15)
    gridDown: Persistent[list[float]] = array.new_float(15)

    if bar_index > 20:
        for i in pine_range(0, 14):
            array.set(gridUp, i, basePrice + (i + 1) * atr * gridFactor)
            array.set(gridDown, i, basePrice - (i + 1) * atr * gridFactor)

    for i in pine_range(0, 14):
        lineColorUp = color.red if i == shortLevel else color.new(color.red, 80)
        lineColorDown = color.green if i == longLevel else color.new(color.green, 80)
        line.new(bar_index - 1, array.get(gridUp, i), bar_index, array.get(gridUp, i), color=lineColorUp, width=2 if i == shortLevel else 1)
        line.new(bar_index - 1, array.get(gridDown, i), bar_index, array.get(gridDown, i), color=lineColorDown, width=2 if i == longLevel else 1)

    shortCond = close > array.get(gridUp, shortLevel) and (high - low) / high > noTradeZone and (rsi > minRSIShort) and (close < open)
    longCond = close < array.get(gridDown, longLevel) and (high - low) / low > noTradeZone and (rsi < maxRSILong) and (close > open)

    if shortCond:
        strategy.entry('Short', strategy.short)

    if longCond:
        strategy.entry('Long', strategy.long)

    if strategy.position_size > 0:
        strategy.exit('Exit Long', 'Long', limit=close * (1 + profitTarget), trail_price=close * (1 + profitTarget * 0.5), trail_offset=atr)

    if strategy.position_size < 0:
        strategy.exit('Exit Short', 'Short', limit=close * (1 - profitTarget), trail_price=close * (1 - profitTarget * 0.5), trail_offset=atr)

    plotshape(strategy.position_size > 0 and strategy.position_size[1] <= 0, location=location.belowbar, style=shape.labelup, color=color.green, text='LONG', textcolor=color.white)
    plotshape(strategy.position_size < 0 and strategy.position_size[1] >= 0, location=location.abovebar, style=shape.labeldown, color=color.red, text='SHORT', textcolor=color.white)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
