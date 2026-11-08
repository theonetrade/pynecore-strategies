"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barstate, box, chart, close, color, fill, high, input,
    label, line, low, math, na, open, plot, script, size, string, ta, text, time, volume, xloc
)
from pynecore.types import Box, Color, Label, NA, Persistent, Series


@udt
class OrderBlock:
    top: float = na(float)
    bottom: float = na(float)
    startTime: int = na(int)
    strength: float = na(float)
    isBullish: bool = na(bool)
    boxId: Box = na(Box)
    labelId: Label = na(Label)
    mitigated: bool = na(bool)


BULL_COLOR: Color = color.new('#089981')
BEAR_COLOR: Color = color.new('#F23645')
OB_GROUP: str = "Order Block Settings"
VIS_GROUP: str = "Visualization"


@script.indicator("Institutional Order Flow Strength Classifier [LuxAlgo]", "LuxAlgo - Institutional Order Flow Strength Classifier", overlay=True, max_boxes_count=100, max_labels_count=100)
def main(
    pivotLenInput=input.int(5, "Pivot Lookback", minval=2, group=OB_GROUP),
    maxOBsInput=input.int(5, "Max Unmitigated OBs", minval=1, maxval=50, group=OB_GROUP),
    bullColorInput=input.color(color.new(BULL_COLOR, 80), "Bullish OB Color", group=VIS_GROUP),
    bearColorInput=input.color(color.new(BEAR_COLOR, 80), "Bearish OB Color", group=VIS_GROUP),
    hideOverlappedInput=input.bool(True, "Hide Overlapped Zones", group=VIS_GROUP),
    showLabelsInput=input.bool(True, "Show Strength Labels", group=VIS_GROUP),
    showStrongestInput=input.bool(True, "Show Strongest OB Plot", group=VIS_GROUP),
    bufferSizeInput=input.int(5, "Strongest OB Buffer Size", minval=1, maxval=100, group=VIS_GROUP)
):
    TEXT_COLOR: Color = chart.fg_color



    def calculateStrength(obRange: float, breakoutDist: float, relVol: float):
        dispFactor: float = math.min(breakoutDist / (obRange * 5), 1.0)
        volFactor: float = math.min(relVol / 2.0, 1.0)
        score: float = (dispFactor * 0.6 + volFactor * 0.4) * 100
        return math.round(score, 1)

    obArray: Persistent[list[OrderBlock]] = array.new(0, NA(OrderBlock))
    volSMA: Series[float] = ta.sma(volume, 20)

    hi: float = ta.pivothigh(pivotLenInput, pivotLenInput)
    lo: float = ta.pivotlow(pivotLenInput, pivotLenInput)

    lastHi: Persistent[float] = na(float)
    lastLo: Persistent[float] = na(float)
    lastHiIdx: Persistent[int] = na(int)
    lastLoIdx: Persistent[int] = na(int)

    if not na(hi):
        lastHi = hi
        lastHiIdx = bar_index - pivotLenInput
    if not na(lo):
        lastLo = lo
        lastLoIdx = bar_index - pivotLenInput

    bullBOS: bool = ta.crossover(close, lastHi)
    bearBOS: bool = ta.crossunder(close, lastLo)

    if bullBOS or bearBOS:
        searchLen: int = bar_index - (lastHiIdx if bullBOS else lastLoIdx)
        obTop: float = na(float)
        obBtm: float = na(float)
        obIdx: int = na(int)
        obVol: float = na(float)

        if bullBOS:
            minLow: float = na(float)
            for i in pine_range(1, searchLen):
                if close[i] < open[i]:
                    if na(minLow) or low[i] < minLow:
                        minLow = low[i]
                        obTop = high[i]
                        obBtm = low[i]
                        obIdx = i
                        obVol = volume[i]
            lastHi = na
        else:
            maxHigh: float = na(float)
            for i in pine_range(1, searchLen):
                if close[i] > open[i]:
                    if na(maxHigh) or high[i] > maxHigh:
                        maxHigh = high[i]
                        obTop = high[i]
                        obBtm = low[i]
                        obIdx = i
                        obVol = volume[i]
            lastLo = na

        if not na(obIdx):
            obHeight: float = obTop - obBtm
            breakoutDist: float = close - obTop if bullBOS else obBtm - close
            avgVol: float = volSMA[obIdx]
            strength: float = calculateStrength(obHeight, breakoutDist, obVol / avgVol)

            newOB: OrderBlock = OrderBlock(obTop, obBtm, time[obIdx], strength, bullBOS, na, na, False)
            array.unshift(obArray, newOB)

    if array.size(obArray) > 0:
        for i in pine_range(0, array.size(obArray) - 1):
            ob: OrderBlock = array.get(obArray, i)
            if not ob.mitigated:
                isMitigated: bool = low < ob.bottom if ob.isBullish else high > ob.top
                if isMitigated:
                    ob.mitigated = True

    strongestTop: float = na(float)
    strongestBottom: float = na(float)
    strongestAvgPrice: Series[float] = na(float)
    strongestIsBullish: bool = False
    maxStrength: float = -1.0

    if array.size(obArray) > 0:
        checkedCount: int = 0
        for i in pine_range(0, array.size(obArray) - 1):
            ob: OrderBlock = array.get(obArray, i)
            if not ob.mitigated:
                if ob.strength > maxStrength:
                    maxStrength = ob.strength
                    strongestTop = ob.top
                    strongestBottom = ob.bottom
                    strongestAvgPrice = (ob.top + ob.bottom) / 2
                    strongestIsBullish = ob.isBullish

                checkedCount += 1
                if checkedCount >= bufferSizeInput:
                    break

    plotCol: Color = na if na(strongestAvgPrice) else bullColorInput if strongestIsBullish else bearColorInput
    hasChanged: bool = strongestAvgPrice != strongestAvgPrice[1]

    plotTop = plot(strongestTop if showStrongestInput else na, 'Strongest OB Top', color=na if hasChanged else color.new(plotCol, 70))
    plotBtm = plot(strongestBottom if showStrongestInput else na, 'Strongest OB Bottom', color=na if hasChanged else color.new(plotCol, 70))
    fill(plotTop, plotBtm, na if hasChanged else color.new(plotCol, 90), 'Strongest OB Zone Fill')

    plot(strongestAvgPrice if showStrongestInput else na, 'Strongest OB Median', color=na if hasChanged else color.new(plotCol, 40), linewidth=2)

    if barstate.islast:
        activeCount: int = 0
        occupiedTops: Persistent[list[float]] = array.new_float(0)
        occupiedBtms: Persistent[list[float]] = array.new_float(0)
        array.clear(occupiedTops)
        array.clear(occupiedBtms)

        if array.size(obArray) > 0:
            for i in pine_range(0, array.size(obArray) - 1):
                ob: OrderBlock = array.get(obArray, i)

                isOverlapped: bool = False
                if not ob.mitigated and hideOverlappedInput and (array.size(occupiedTops) > 0):
                    for j in pine_range(0, array.size(occupiedTops) - 1):
                        otherTop: float = array.get(occupiedTops, j)
                        otherBtm: float = array.get(occupiedBtms, j)
                        if ob.top <= otherTop and ob.top >= otherBtm or (ob.bottom <= otherTop and ob.bottom >= otherBtm) or (ob.top >= otherTop and ob.bottom <= otherBtm):
                            isOverlapped = True
                            break

                if not ob.mitigated and (not isOverlapped) and (activeCount < maxOBsInput):
                    activeCount += 1
                    array.push(occupiedTops, ob.top)
                    array.push(occupiedBtms, ob.bottom)

                    obCol: Color = bullColorInput if ob.isBullish else bearColorInput
                    labelCol: Color = BULL_COLOR if ob.isBullish else BEAR_COLOR

                    if na(ob.boxId):
                        ob.boxId = box.new(ob.startTime, ob.top, time, ob.bottom, bgcolor=obCol, border_color=obCol, border_style=line.style_dashed, xloc=xloc.bar_time)

                    if showLabelsInput:
                        if na(ob.labelId):
                            ob.labelId = label.new(time, (ob.top + ob.bottom) / 2, text=string.format('{0}%', ob.strength), style=label.style_label_left, textcolor=labelCol, color=color.new('#00000000'), size=size.small, textalign=text.align_center, xloc=xloc.bar_time)
                else:
                    if not na(ob.boxId):
                        box.delete(ob.boxId)
                        ob.boxId = na
                    if not na(ob.labelId):
                        label.delete(ob.labelId)
                        ob.labelId = na

    if array.size(obArray) > 100:
        for i in pine_range(array.size(obArray) - 1, 0):
            ob: OrderBlock = array.get(obArray, i)
            if ob.mitigated and array.size(obArray) > 50:
                array.remove(obArray, i)
            elif array.size(obArray) > 100:
                array.pop(obArray)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
