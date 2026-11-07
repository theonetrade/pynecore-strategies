"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, bgcolor, close, color, currency, high, hline, input, line,
    location, low, math, na, plot, plotshape, script, shape, size, strategy, ta
)
from pynecore.types import Line, Persistent, PersistentSeries, Series


@script.strategy(title="RSI Divergence Strategy", shorttitle="RSI Divergence Strategy", overlay=False, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, commission_value=0.1, slippage=0, initial_capital=100000, currency=currency.USD, process_orders_on_close=False)
def main(
    rsiLengthInput=input.int(14, minval=1, title="RSI Length", group="RSI Settings"),
    rsiSourceInput: Series[float] = input.source(close, "Source", group="RSI Settings"),
    calculateDivergence=input.bool(True, title="Calculate Divergence", group="RSI Settings", tooltip="Required for divergence signals"),
    longEntryLevel=input.float(35.0, "Long Entry RSI", minval=0, maxval=100, step=0.1, group="RSI Levels"),
    shortEntryLevel=input.float(76.0, "Short Entry RSI", minval=0, maxval=100, step=0.1, group="RSI Levels"),
    longExitLevel=input.float(80.0, "Long Exit RSI", minval=0, maxval=100, step=0.1, group="RSI Levels"),
    shortExitLevel=input.float(54.1, "Short Exit RSI", minval=0, maxval=100, step=0.1, group="RSI Levels")
):
    change = ta.change(rsiSourceInput)
    up = ta.rma(math.max(change, 0), rsiLengthInput)
    down = ta.rma(-math.min(change, 0), rsiLengthInput)
    rsi: Series = 100 if down == 0 else 0 if up == 0 else 100 - 100 / (1 + up / down)

    lookbackRight: int = 5
    lookbackLeft: int = 5
    rangeUpper: int = 60
    rangeLower: int = 5

    def _inRange(cond: bool):
        bars = ta.barssince(cond)
        return rangeLower <= bars and bars <= rangeUpper

    plFound: PersistentSeries[bool] = False
    phFound: PersistentSeries[bool] = False
    bullCond: Persistent[bool] = False
    bearCond: Persistent[bool] = False

    inRangePlFound: Persistent[bool] = False
    inRangePhFound: Persistent[bool] = False

    rsiLBR = rsi[lookbackRight]

    inRangePlFound = _inRange(plFound[1])
    inRangePhFound = _inRange(phFound[1])

    if calculateDivergence:
        plFound = not na(ta.pivotlow(rsi, lookbackLeft, lookbackRight))
        rsiHL = rsiLBR > ta.valuewhen(plFound, rsiLBR, 1) and inRangePlFound
        lowLBR = low[lookbackRight]
        priceLL = lowLBR < ta.valuewhen(plFound, lowLBR, 1)
        bullCond = priceLL and rsiHL and plFound

        phFound = not na(ta.pivothigh(rsi, lookbackLeft, lookbackRight))
        rsiLH = rsiLBR < ta.valuewhen(phFound, rsiLBR, 1) and inRangePhFound
        highLBR = high[lookbackRight]
        priceHH = highLBR > ta.valuewhen(phFound, highLBR, 1)
        bearCond = priceHH and rsiLH and phFound

    if bullCond and rsi < longEntryLevel:
        strategy.entry('Long', strategy.long)

    if bearCond and rsi > shortEntryLevel:
        strategy.entry('Short', strategy.short)

    if rsi >= longExitLevel:
        strategy.close('Long')

    if rsi <= shortExitLevel:
        strategy.close('Short')

    rsiColor = color.new(color.new('#FF5252'), 0) if rsi > 70 else color.new(color.new('#4BF335'), 0) if rsi < 30 else color.new(color.new('#B8B8B8'), 0)
    plot(rsi, title='RSI', color=rsiColor, linewidth=2, style=plot.style_line)

    hline(longEntryLevel, 'Long Entry', color=color.new(color.new('#4BF335'), 0), linestyle=hline.style_solid)
    hline(shortEntryLevel, 'Short Entry', color=color.new(color.new('#ED1404'), 0), linestyle=hline.style_solid)
    hline(longExitLevel, 'Long Exit', color=color.new(color.new('#4BF335'), 0), linestyle=hline.style_dashed)
    hline(shortExitLevel, 'Short Exit', color=color.new(color.new('#ED1404'), 0), linestyle=hline.style_dashed)

    ob: int = 70
    os: int = 30
    hline(ob, 'Overbought', color=color.new(color.new('#FF5252'), 70), linestyle=hline.style_dotted)
    hline(os, 'Oversold', color=color.new(color.new('#4BF335'), 70), linestyle=hline.style_dotted)

    bgcolor(color.new(color.new('#FF5252'), 90) if rsi >= ob else na)
    bgcolor(color.new(color.new('#4BF335'), 90) if rsi <= os else na)
    bgcolor(color.new(color.new('#424242'), 95) if rsi > os and rsi < ob else na)

    bullLabelY = math.max(0, rsi[lookbackRight] - 15)
    bearLabelY = math.min(100, rsi[lookbackRight] + 15)

    plotshape(bullLabelY if bullCond else na, title='Bullish Divergence', text='BULL', style=shape.labelup, location=location.absolute, color=color.new(color.new('#4BF335'), 50), textcolor=color.white, size=size.tiny, offset=-lookbackRight)

    plotshape(bearLabelY if bearCond else na, title='Bearish Divergence', text='BEAR', style=shape.labeldown, location=location.absolute, color=color.new(color.new('#ED1404'), 50), textcolor=color.white, size=size.tiny, offset=-lookbackRight)

    lastBullLine: PersistentSeries[Line] = na(Line)
    lastBearLine: PersistentSeries[Line] = na(Line)

    if bullCond:
        prevLowIndex = ta.valuewhen(plFound, bar_index, 1)
        prevLowValue = ta.valuewhen(plFound, rsi[lookbackRight], 1)

        if not na(prevLowIndex):
            lastBullLine = line.new(x1=prevLowIndex, y1=prevLowValue, x2=bar_index - lookbackRight, y2=rsi[lookbackRight], color=color.new(color.new('#4BF335'), 70), width=1, style=line.style_dotted)
            line.delete(lastBullLine[1])

    if bearCond:
        prevHighIndex = ta.valuewhen(phFound, bar_index, 1)
        prevHighValue = ta.valuewhen(phFound, rsi[lookbackRight], 1)

        if not na(prevHighIndex):
            lastBearLine = line.new(x1=prevHighIndex, y1=prevHighValue, x2=bar_index - lookbackRight, y2=rsi[lookbackRight], color=color.new(color.new('#ED1404'), 70), width=1, style=line.style_dotted)
            line.delete(lastBearLine[1])


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
