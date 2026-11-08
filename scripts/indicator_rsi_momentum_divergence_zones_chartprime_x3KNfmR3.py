"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, close, color, display, fill, format, high, input, line,
    location, low, na, plot, plotshape, script, shape, ta
)
from pynecore.types import Line, NA, Persistent, Series


@udt
class divLevel:
    primaryLine: Line = na(Line)
    bgLine: Line = na(Line)


@script.indicator('RSI Momentum Divergence Zones [ChartPrime]', "RSIM DivergenceZones [ChartPrime]", format=format.price, precision=2, max_lines_count=500)
def main(
    rsiLength=input.int(14, 'RSI Length', group='Settings'),
    enableDivCheck=input.bool(True, title='Enable Divergence Detection', group='Divergence'),
    showDivLevels=input.bool(True, "Show Divergence Zones", group='Divergence'),
    qtyDivLevels=input.int(10, "Qty Divergence Zones", group='Divergence'),
    divBearColor=input.color(color.new('#AE4CE6'), "Bearish Color", group='Divergence'),
    divBullColor=input.color(color.new('#33C570'), "Bullish Color", group='Divergence')
):
    divLookbackR: int = 5
    divLookbackL: int = 5
    minBarsInRange: int = 5
    maxBarsInRange: int = 50

    textCol = color.white
    noneCol = color.new(color.white, 100)

    bearDivLines: Persistent[list[divLevel]] = array.new(0, NA(divLevel))
    bullDivLines: Persistent[list[divLevel]] = array.new(0, NA(divLevel))

    rsiSrc = ta.mom(close, 10)
    rsiVal: Series = ta.rsi(rsiSrc, rsiLength)
    rsiRight = rsiVal[divLookbackR]

    def _inRange(pivotCond):
        barCount = ta.barssince(pivotCond)
        return minBarsInRange <= barCount and barCount <= maxBarsInRange

    def detectDivergence(doCheck):
        bullDiv: bool = False
        bearDiv: bool = False
        foundPL: Series[bool] = False
        foundPH: Series[bool] = False

        if doCheck:
            foundPL = not na(ta.pivotlow(rsiVal, divLookbackL, divLookbackR))
            rsiHL = rsiRight > ta.valuewhen(foundPL, rsiRight, 1) and _inRange(foundPL[1])
            priceLL = low[divLookbackR] < ta.valuewhen(foundPL, low[divLookbackR], 1)
            bullDiv = foundPL and rsiHL and priceLL

            foundPH = not na(ta.pivothigh(rsiVal, divLookbackL, divLookbackR))
            rsiLH = rsiRight < ta.valuewhen(foundPH, rsiRight, 1) and _inRange(foundPH[1])
            priceHH = high[divLookbackR] > ta.valuewhen(foundPH, high[divLookbackR], 1)
            bearDiv = foundPH and rsiLH and priceHH

        return (foundPL, foundPH, bullDiv, bearDiv, high[divLookbackR], low[divLookbackR])

    def plotDivergenceLevels(arr, cond, isBull):
        levelY = low[divLookbackR] if isBull else high[divLookbackR]
        if cond:
            l1 = line.new(bar_index - 5, levelY, bar_index, levelY, color=divBullColor if isBull else divBearColor, force_overlay=True)
            l2 = line.new(bar_index - 5, levelY, bar_index, levelY, color=color.new(divBullColor if isBull else divBearColor, 70), width=6, force_overlay=True)
            method_call('push', arr, divLevel(l1, l2))

        if method_call('size', arr) > qtyDivLevels:
            expired = method_call('shift', arr)
            method_call('delete', expired.primaryLine)
            method_call('delete', expired.bgLine)

        if method_call('size', arr) > 0:
            for dl in arr:
                line1 = dl.primaryLine
                line2 = dl.bgLine
                if high > method_call('get_y1', line1) if isBull else low < method_call('get_y1', line1):
                    method_call('set_x2', line1, bar_index + 15)
                    method_call('set_x2', line2, bar_index + 15)
                else:
                    method_call('set_x2', line1, bar_index)
                    method_call('set_style', line1, line.style_dashed)
                    method_call('delete', line2)
                    method_call('remove', arr, method_call('indexof', arr, dl))
        return 0

    foundPL, foundPH, isBullDiv, isBearDiv, highLevel, lowLevel = detectDivergence(enableDivCheck)

    rsiLine = plot(rsiVal, title='RSI', color=color.from_gradient(rsiVal, 30, 70, divBullColor, divBearColor))
    p50 = plot(50, color=color.gray)
    fill(rsiLine, p50, 70, 30, divBearColor, na)
    fill(rsiLine, p50, 70, 30, na, divBullColor)

    plot(rsiRight if foundPL else na, offset=-divLookbackR, title='Bullish RSI HL', color=divBullColor if isBullDiv else noneCol, linewidth=2)
    plotshape(rsiRight if isBullDiv else na, offset=-divLookbackR, title='Bullish Label', style=shape.labelup, text=' Bull ', color=divBullColor, textcolor=textCol, location=location.absolute)

    plot(rsiRight if foundPH else na, offset=-divLookbackR, title='Bearish RSI LH', color=divBearColor if isBearDiv else noneCol, linewidth=2)
    plotshape(rsiRight if isBearDiv else na, offset=-divLookbackR, title='Bearish Label', style=shape.labeldown, text=' Bear ', color=divBearColor, textcolor=textCol, location=location.absolute)

    plot(lowLevel if foundPL else na, offset=-divLookbackR, title='Bullish Price LL', color=divBullColor if isBullDiv else noneCol, linewidth=1, display=display.pane, force_overlay=True)
    plot(lowLevel if foundPL else na, offset=-divLookbackR, title='Bullish Price LL BG', color=color.new(divBullColor, 70) if isBullDiv else noneCol, linewidth=6, display=display.pane, force_overlay=True)
    plotshape(low[divLookbackR] if isBullDiv else na, offset=-divLookbackR, title='Bullish Price LL Label', style=shape.labelup, text='▲\nBull', color=noneCol, textcolor=divBullColor, force_overlay=True, location=location.absolute)

    plot(highLevel if foundPH else na, offset=-divLookbackR, title='Bearish Price HH', color=divBearColor if isBearDiv else noneCol, linewidth=1, display=display.pane, force_overlay=True)
    plot(highLevel if foundPH else na, offset=-divLookbackR, title='Bearish Price HH BG', color=color.new(divBearColor, 70) if isBearDiv else noneCol, linewidth=6, display=display.pane, force_overlay=True)
    plotshape(highLevel if isBearDiv else na, offset=-divLookbackR, title='Bearish Price HH Label', style=shape.labeldown, text='Bear\n▼', color=noneCol, textcolor=divBearColor, force_overlay=True, location=location.absolute)

    if showDivLevels:
        plotDivergenceLevels(bearDivLines, isBearDiv, False)
        plotDivergenceLevels(bullDivLines, isBullDiv, True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
