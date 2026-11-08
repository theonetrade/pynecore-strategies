"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, barstate, close, color, high, hl2, hlc3,
    hlcc4, input, label, location, low, math, na, open, plot, plotshape, script, shape, size, ta,
    xloc, yloc
)
from pynecore.types import Persistent, Series

groupTma: str = "TMA"
groupVisual: str = "VISUAL"
groupTrade: str = "TRADE SIGNALS"


@script.indicator("Colored TMA Trend Signals [josseliani]", overlay=True, max_labels_count=500)
def main(
    halfLength=input.int(12, "Half Length", minval=1, group=groupTma),
    priceMode=input.string("Weighted Price", "Price Source", options=("Close", "Open", "High", "Low", "Median Price", "Typical Price", "Weighted Price"), group=groupTma),
    bandsDeviation=input.float(2.0, "Band Deviation", minval=0.1, step=0.1, group=groupTma, tooltip="Standard-deviation multiplier for the bands around TMA."),
    useSmoothing=input.bool(False, "Use Source Smoothing", group=groupTma),
    smoothingPeriod=input.int(12, "Smoothing Period", minval=1, group=groupTma),
    showBands=input.bool(True, "Show Bands", group=groupVisual),
    showTrendSignals=input.bool(True, "Show TMA Color-Change Signals", group=groupVisual),
    lineWidth=input.int(2, "TMA Line Width", minval=1, maxval=5, group=groupVisual),
    showTradeSignals=input.bool(True, "Show BUY/SELL Labels", group=groupTrade, tooltip="Visual option only. Trade alerts remain active when labels are hidden."),
    tradeLevel=input.string("TMA", "Break Level", options=("TMA", "Bands"), group=groupTrade),
    confirmBars=input.int(3, "Confirm Bars", minval=1, maxval=10, group=groupTrade, tooltip="Confirmation is checked exactly on the Nth consecutive close beyond the selected level. If blocked, the sequence must reset before another confirmation is checked."),
    tradeOnlyWithTrend=input.bool(True, "Only With TMA Trend", group=groupTrade, tooltip="BUY only while TMA is green, SELL only while red."),
    onePerColor=input.bool(True, "One Trade Per Color", group=groupTrade, tooltip="A bullish turn unlocks one BUY and blocks SELL. A bearish turn unlocks one SELL and blocks BUY. After a signal, that direction stays locked until a new matching color turn.")
):
    __block_result__ = na
    __switch__ = priceMode
    if __switch__ == "Open":
        __block_result__ = open
    elif __switch__ == "High":
        __block_result__ = high
    elif __switch__ == "Low":
        __block_result__ = low
    elif __switch__ == "Median Price":
        __block_result__ = hl2
    elif __switch__ == "Typical Price":
        __block_result__ = hlc3
    elif __switch__ == "Weighted Price":
        __block_result__ = hlcc4
    else:
        __block_result__ = close
    src = __block_result__

    base = ta.ema(src, smoothingPeriod) if useSmoothing else src

    tmaLen = halfLength * 2 - 1
    tma: Series = ta.sma(ta.sma(base, halfLength), halfLength)
    deviation = ta.stdev(base, tmaLen)
    upperBand = tma + deviation * bandsDeviation
    lowerBand = tma - deviation * bandsDeviation
    atr = ta.atr(14)

    trendUp = tma > tma[1]
    trendDown = tma < tma[1]
    tmaColor = color.lime if trendUp else color.red if trendDown else color.gray

    lastSolidTrend: Persistent[int] = 0
    currTrend = 1 if trendUp else -1 if trendDown else 0
    bullishTurn: bool = False
    bearishTurn: bool = False

    if barstate.isconfirmed and currTrend != 0:
        bullishTurn = currTrend == 1 and lastSolidTrend == -1
        bearishTurn = currTrend == -1 and lastSolidTrend == 1
        lastSolidTrend = currTrend

    bullBreakLevel = upperBand if tradeLevel == 'Bands' else tma
    bearBreakLevel = lowerBand if tradeLevel == 'Bands' else tma

    barsAbove: Persistent[int] = 0
    barsBelow: Persistent[int] = 0
    barsAbove = barsAbove + 1 if close > bullBreakLevel else 0
    barsBelow = barsBelow + 1 if close < bearBreakLevel else 0

    longUsedThisColor: Persistent[bool] = False
    shortUsedThisColor: Persistent[bool] = False

    if bullishTurn:
        longUsedThisColor = False
        shortUsedThisColor = True

    if bearishTurn:
        shortUsedThisColor = False
        longUsedThisColor = True

    trendAllowsLong = not tradeOnlyWithTrend or trendUp
    trendAllowsShort = not tradeOnlyWithTrend or trendDown
    longSlotFree = not onePerColor or not longUsedThisColor
    shortSlotFree = not onePerColor or not shortUsedThisColor
    tradeBull: bool = False
    tradeBear: bool = False

    if barstate.isconfirmed:
        if barsAbove == confirmBars and trendAllowsLong and longSlotFree:
            tradeBull = True
            longUsedThisColor = True

        if barsBelow == confirmBars and trendAllowsShort and shortSlotFree:
            tradeBear = True
            shortUsedThisColor = True

    plot(tma, title='TMA', color=tmaColor, linewidth=lineWidth)
    plot(upperBand if showBands else na, title='Upper Band', color=color.new(color.gray, 50))
    plot(lowerBand if showBands else na, title='Lower Band', color=color.new(color.gray, 50))

    plotshape(tma if showTrendSignals and bullishTurn else na, title='TMA Bullish Color Change', style=shape.triangleup, location=location.absolute, color=color.lime, size=size.tiny)
    plotshape(tma if showTrendSignals and bearishTurn else na, title='TMA Bearish Color Change', style=shape.triangledown, location=location.absolute, color=color.red, size=size.tiny)

    labelGapAtr: float = 1.5
    gap = math.max(atr * labelGapAtr, high - low)

    if showTradeSignals and tradeBull:
        label.new(bar_index, low - gap, 'BUY', xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_up, color=color.new(color.lime, 70), textcolor=color.lime, size=size.small)

    if showTradeSignals and tradeBear:
        label.new(bar_index, high + gap, 'SELL', xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_down, color=color.new(color.red, 70), textcolor=color.red, size=size.small)

    alertcondition(bullishTurn, title='TMA Bullish Color Change', message='Colored TMA: bullish color change on {{ticker}} {{interval}}')
    alertcondition(bearishTurn, title='TMA Bearish Color Change', message='Colored TMA: bearish color change on {{ticker}} {{interval}}')
    alertcondition(bullishTurn or bearishTurn, title='Any TMA Color Change', message='Colored TMA: color changed on {{ticker}} {{interval}}')
    alertcondition(tradeBull, title='Trade Long', message='Colored TMA: trade long on {{ticker}} {{interval}}')
    alertcondition(tradeBear, title='Trade Short', message='Colored TMA: trade short on {{ticker}} {{interval}}')
    alertcondition(tradeBull or tradeBear, title='Any Trade Signal', message='Colored TMA: trade signal on {{ticker}} {{interval}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)