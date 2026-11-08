"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, bar_index, barstate, close, color, fill, format, high,
    hline, input, label, line, location, low, math, na, nz, plot, plotshape, script, shape, size,
    ta
)
from pynecore.types import Persistent, PersistentSeries, Series


@script.indicator("Fisher Transform of Williams %R - Divergence", shorttitle="Fish%R Div", format=format.price, precision=2, overlay=False, max_lines_count=500, max_labels_count=500)
def main(
    length=input.int(14, title="Williams %R Length", minval=1, group="Core Settings"),
    fisherLength=input.int(10, title="Fisher Transform Length", minval=1, group="Core Settings"),
    src: Series[float] = input.source(close, title="Source", group="Core Settings"),
    obLevel=input.float(1.5, title="Overbought Level", group="Core Settings"),
    osLevel=input.float(-1.5, title="Oversold Level", group="Core Settings"),
    lbR=input.int(5, title="Pivot Right Lookback", minval=1, group="Divergence Settings", tooltip="Number of bars to the right required to confirm a pivot"),
    lbL=input.int(5, title="Pivot Left Lookback", minval=1, group="Divergence Settings", tooltip="Number of bars to the left used to detect a pivot"),
    rangeUpper=input.int(60, title="Max Lookback Range", minval=1, group="Divergence Settings", tooltip="Maximum bar distance between two pivots when searching for a divergence"),
    rangeLower=input.int(5, title="Min Lookback Range", minval=1, group="Divergence Settings", tooltip="Minimum bar distance between two pivots when searching for a divergence"),
    minBarsBetween=input.int(0, title="Min Bars Between Same-Type Signals", minval=0, group="Divergence Settings", tooltip="Minimum number of bars between the pivots of two same-type divergence signals. Values at or below Min Lookback Range have no practical effect (0 = off)"),
    minFishDiff=input.float(0.1, title="Min Fisher Difference", minval=0.0, step=0.05, group="Divergence Settings", tooltip="Minimum Fisher difference between two pivots. Filters out negligible divergences (0 = off)"),
    showRegular=input.bool(True, title="Show Regular Divergence", group="Divergence Toggle"),
    showHidden=input.bool(True, title="Show Hidden Divergence", group="Divergence Toggle"),
    zoneFilter=input.bool(False, title="Require OB/OS Zone for Divergence", group="Divergence Toggle", tooltip="If enabled, divergences are only generated when the Fisher pivot is inside the overbought/oversold zone"),
    showCross=input.bool(True, title="Show Fisher/Trigger Cross Signals", group="Cross Signals", tooltip="Standalone confirmation signals generated when the Fisher line crosses its trigger line"),
    trigLen=input.int(3, title="Trigger EMA Length (1 = Prev Bar)", minval=1, group="Cross Signals", tooltip="1 = classic Fisher[1] trigger (very noisy). 2+ = an EMA of Fisher is used as the trigger, which makes crosses less frequent"),
    zoneGate=input.bool(True, title="Require Recent OB/OS Extreme", group="Cross Signals", tooltip="Buy requires Fisher to have reached the oversold zone recently; Sell requires the overbought zone"),
    extLookback=input.int(8, title="Extreme Lookback Bars", minval=1, group="Cross Signals", tooltip="Number of bars to look back for an overbought/oversold extreme"),
    zeroSide=input.bool(True, title="Buy Below / Sell Above Zero Line", group="Cross Signals", tooltip="Buy crosses must occur below the zero line, Sell crosses above it"),
    altOnly=input.bool(True, title="Alternate Signals Only", group="Cross Signals", tooltip="Prevents repeated signals in the same direction (Buy-Sell-Buy)"),
    crossMinBars=input.int(3, title="Min Bars Between Cross Signals", minval=0, group="Cross Signals", tooltip="Minimum number of bars between two cross signals (0 = off)"),
    bullColor=input.color(color.new('#00E676'), "Bullish Divergence Color", group="Style & Colors"),
    bearColor=input.color(color.new('#FF5252'), "Bearish Divergence Color", group="Style & Colors"),
    hiddenBull=input.color(color.new(color.new('#00E676'), 40), "Hidden Bullish Color", group="Style & Colors"),
    hiddenBear=input.color(color.new(color.new('#FF5252'), 40), "Hidden Bearish Color", group="Style & Colors"),
    fisherColor=input.color(color.new('#2962FF'), "Fisher Line Color", group="Style & Colors"),
    trigColor=input.color(color.new('#FF6D00'), "Trigger Line Color", group="Style & Colors")
):
    hh = ta.highest(high, length)
    ll = ta.lowest(low, length)

    percentR = -50.0 if na(hh) or na(ll) or hh == ll else 100 * (src - hh) / (hh - ll)

    highestPR = ta.highest(percentR, fisherLength)
    lowestPR = ta.lowest(percentR, fisherLength)

    rawVal = 0.5 if highestPR == lowestPR else (percentR - lowestPR) / (highestPR - lowestPR)
    normVal = 2 * (rawVal - 0.5)

    val: PersistentSeries[float] = 0.0
    val = math.max(math.min(0.33 * normVal + 0.67 * nz(val[1]), 0.999), -0.999)

    fisher: PersistentSeries[float] = 0.0
    fisher = 0.5 * math.log((1 + val) / (1 - val)) + 0.5 * nz(fisher[1])

    emaTrig = ta.ema(fisher, trigLen)
    trigger = fisher[1] if trigLen == 1 else emaTrig

    plot(fisher, title='Fisher %R', color=fisherColor, linewidth=2)
    plot(trigger, title='Trigger Line', color=trigColor, linewidth=1)

    h1 = hline(obLevel, title='Overbought Level', color=color.gray, linestyle=hline.style_dashed)
    h0 = hline(0, title='Zero Line', color=color.new(color.gray, 50), linestyle=hline.style_dotted)
    h2 = hline(osLevel, title='Oversold Level', color=color.gray, linestyle=hline.style_dashed)
    fill(h1, h2, color=color.new(color.new('#2962FF'), 93), title='OB/OS Background')

    crossUp = ta.crossover(fisher, trigger)
    crossDown = ta.crossunder(fisher, trigger)

    wasOS = ta.lowest(fisher, extLookback) <= osLevel
    wasOB = ta.highest(fisher, extLookback) >= obLevel

    rawBuy = crossUp and (not zoneGate or wasOS) and (not zeroSide or trigger < 0)
    rawSell = crossDown and (not zoneGate or wasOB) and (not zeroSide or trigger > 0)

    lastCrossDir: Persistent[int] = 0
    lastCrossBar: Persistent[int] = na(int)

    cooldownOk = na(lastCrossBar) or bar_index - lastCrossBar >= crossMinBars

    buySig = showCross and barstate.isconfirmed and rawBuy and cooldownOk and (not altOnly or lastCrossDir != 1)
    sellSig = showCross and barstate.isconfirmed and rawSell and cooldownOk and (not altOnly or lastCrossDir != -1)

    if buySig:
        lastCrossDir = 1
        lastCrossBar = bar_index
    if sellSig:
        lastCrossDir = -1
        lastCrossBar = bar_index

    plotshape(fisher if buySig else na, title='Buy Cross Signal', style=shape.triangleup, location=location.absolute, color=bullColor, size=size.tiny)
    plotshape(fisher if sellSig else na, title='Sell Cross Signal', style=shape.triangledown, location=location.absolute, color=bearColor, size=size.tiny)

    pl: Series = ta.pivotlow(fisher, lbL, lbR)
    ph: Series = ta.pivothigh(fisher, lbL, lbR)

    lastBullBar: Persistent[int] = na(int)
    lastBearBar: Persistent[int] = na(int)

    regBullSig: bool = False
    hdnBullSig: bool = False
    regBearSig: bool = False
    hdnBearSig: bool = False

    pivotBar = bar_index[lbR]

    if not na(pl) and barstate.isconfirmed:
        prevPlIndex: int = na(int)
        for i in pine_range(rangeLower, rangeUpper):
            if not na(pl[i]):
                prevPlIndex = i
                break

        if not na(prevPlIndex):
            currentFisherLow: float = fisher[lbR]
            prevFisherLow: float = fisher[prevPlIndex + lbR]
            currentPriceLow: float = low[lbR]
            prevPriceLow: float = low[prevPlIndex + lbR]

            inZone: bool = not zoneFilter or currentFisherLow <= osLevel
            spacingOk: bool = na(lastBullBar) or pivotBar - lastBullBar >= minBarsBetween
            diffOk: bool = math.abs(currentFisherLow - prevFisherLow) >= minFishDiff

            if showRegular and inZone and spacingOk and diffOk and (currentPriceLow < prevPriceLow) and (currentFisherLow > prevFisherLow):
                line.new(bar_index[prevPlIndex + lbR], prevFisherLow, pivotBar, currentFisherLow, color=bullColor, width=2)
                label.new(pivotBar, currentFisherLow, 'Reg Bull', color=bullColor, style=label.style_label_up, textcolor=color.white, size=size.tiny)
                lastBullBar = pivotBar
                regBullSig = True
            elif showHidden and inZone and spacingOk and diffOk and (currentPriceLow > prevPriceLow) and (currentFisherLow < prevFisherLow):
                line.new(bar_index[prevPlIndex + lbR], prevFisherLow, pivotBar, currentFisherLow, color=hiddenBull, width=2, style=line.style_dashed)
                label.new(pivotBar, currentFisherLow, 'Hdn Bull', color=hiddenBull, style=label.style_label_up, textcolor=color.white, size=size.tiny)
                lastBullBar = pivotBar
                hdnBullSig = True

    if not na(ph) and barstate.isconfirmed:
        prevPhIndex: int = na(int)
        for i in pine_range(rangeLower, rangeUpper):
            if not na(ph[i]):
                prevPhIndex = i
                break

        if not na(prevPhIndex):
            currentFisherHigh: float = fisher[lbR]
            prevFisherHigh: float = fisher[prevPhIndex + lbR]
            currentPriceHigh: float = high[lbR]
            prevPriceHigh: float = high[prevPhIndex + lbR]

            inZone: bool = not zoneFilter or currentFisherHigh >= obLevel
            spacingOk: bool = na(lastBearBar) or pivotBar - lastBearBar >= minBarsBetween
            diffOk: bool = math.abs(currentFisherHigh - prevFisherHigh) >= minFishDiff

            if showRegular and inZone and spacingOk and diffOk and (currentPriceHigh > prevPriceHigh) and (currentFisherHigh < prevFisherHigh):
                line.new(bar_index[prevPhIndex + lbR], prevFisherHigh, pivotBar, currentFisherHigh, color=bearColor, width=2)
                label.new(pivotBar, currentFisherHigh, 'Reg Bear', color=bearColor, style=label.style_label_down, textcolor=color.white, size=size.tiny)
                lastBearBar = pivotBar
                regBearSig = True
            elif showHidden and inZone and spacingOk and diffOk and (currentPriceHigh < prevPriceHigh) and (currentFisherHigh > prevFisherHigh):
                line.new(bar_index[prevPhIndex + lbR], prevFisherHigh, pivotBar, currentFisherHigh, color=hiddenBear, width=2, style=line.style_dashed)
                label.new(pivotBar, currentFisherHigh, 'Hdn Bear', color=hiddenBear, style=label.style_label_down, textcolor=color.white, size=size.tiny)
                lastBearBar = pivotBar
                hdnBearSig = True

    alertcondition(regBullSig, title='Regular Bullish Divergence', message='Fish%R Div: Regular Bullish Divergence Confirmed')
    alertcondition(hdnBullSig, title='Hidden Bullish Divergence', message='Fish%R Div: Hidden Bullish Divergence Confirmed')
    alertcondition(regBearSig, title='Regular Bearish Divergence', message='Fish%R Div: Regular Bearish Divergence Confirmed')
    alertcondition(hdnBearSig, title='Hidden Bearish Divergence', message='Fish%R Div: Hidden Bearish Divergence Confirmed')
    alertcondition(buySig, title='Fisher Buy Cross', message='Fish%R Div: Filtered BUY cross')
    alertcondition(sellSig, title='Fisher Sell Cross', message='Fish%R Div: Filtered SELL cross')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)