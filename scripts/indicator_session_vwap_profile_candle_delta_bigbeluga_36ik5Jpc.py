"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barstate, box, chart, close, color, high, input, line,
    location, low, math, na, open, plotshape, polyline, script, shape, size, string, ta, text,
    timeframe, volume, xloc
)
from pynecore.types import Box, Color, Line, NA, Persistent, PersistentSeries, Polyline, Series
from pynecore.types.chart import ChartPoint


@udt
class SessionElements:
    fillPoly: Polyline = na(Polyline)
    vwapPoly: Polyline = na(Polyline)
    upperPoly: Polyline = na(Polyline)
    lowerPoly: Polyline = na(Polyline)
    profileLines: list[Line] = na(list)
    profileBoxes: list[Box] = na(list)
    pocLine: Line = na(Line)


@script.indicator("Session VWAP Profile & Candle Delta [BigBeluga]", overlay=True, max_boxes_count=500, max_lines_count=500, max_labels_count=500, max_polylines_count=100, calc_bars_count=2000, max_bars_back=500)
def main(
    autoHTF=input.bool(True, "Use Auto Timeframe", tooltip="Automatically selects an optimal Higher Timeframe (HTF) session duration targeting ~200 candles.", group="Timeframe Settings"),
    manualHTF=input.timeframe("1D", "Manual Timeframe", tooltip="Manual Higher Timeframe session duration used when Auto Timeframe is disabled.", group="Timeframe Settings"),
    stdevMult=input.float(2.0, "Band Multiplier (StdDev)", minval=0.1, step=0.1, tooltip="Multiplier for Standard Deviation bands around the central VWAP.", group="Profile Settings"),
    autoBins=input.bool(True, "Auto Bins Resolution", tooltip="Dynamically calculates bin counts based on ATR volatility.", group="Profile Settings"),
    manualBins=input.int(50, "Manual Bins Count", minval=10, maxval=250, tooltip="Fixed number of price bins when Auto Bins Resolution is disabled.", group="Profile Settings"),
    maxSessions=input.int(3, "Max Sessions Displayed", minval=1, maxval=50, tooltip="Maximum number of historical sessions retained on the chart before old drawings are removed.", group="Profile Settings"),
    rightOffset=input.int(35, "Real-Time Profile Offset (Bars)", minval=5, maxval=200, tooltip="Horizontal offset (in bars) to shift the live active profile to the right edge of the chart.", group="Visual Settings"),
    showLabels=input.bool(True, "Show Candle Count Labels", tooltip="Displays bullish and bearish candle count distribution boxes on profile bins.", group="Visual Settings"),
    showPoc=input.bool(True, "Show Point of Control (POC)", tooltip="Draws the Point of Control (POC) level representing the bin with highest volume.", group="Visual Settings"),
    showSignals=input.bool(True, "Show Outer Band Signals", tooltip="Displays triangle signals when price crosses and closes back inside the outer standard deviation bands.", group="Visual Settings"),
    upColor=input.color(color.blue, "Profile Up Color (Green)", tooltip="Color gradient target for bullish volume density and rising VWAP.", group="Palette Settings"),
    dnColor=input.color(color.red, "Profile Down Color (Purple)", tooltip="Color gradient target for bearish volume density and falling VWAP.", group="Palette Settings"),
    baseGray=input.color(color.new('#787B86'), "Base Color", tooltip="Base color for lower density volume bins and session band fill background.", group="Palette Settings"),
    pocColor=input.color(color.red, "POC Line Color", tooltip="Color used to draw the Point of Control (POC) dashed/solid line.", group="Palette Settings")
):
    def deleteSessionElements(inst: SessionElements):
        __block_result__ = na
        if not na(inst):
            if not na(inst.fillPoly):
                polyline.delete(inst.fillPoly)
            if not na(inst.vwapPoly):
                polyline.delete(inst.vwapPoly)
            if not na(inst.upperPoly):
                polyline.delete(inst.upperPoly)
            if not na(inst.lowerPoly):
                polyline.delete(inst.lowerPoly)
            if not na(inst.pocLine):
                line.delete(inst.pocLine)
            if not na(inst.profileLines):
                for l in inst.profileLines:
                    line.delete(l)
                array.clear(inst.profileLines)
            __block_result_1__ = na
            if not na(inst.profileBoxes):
                for b in inst.profileBoxes:
                    box.delete(b)
                __block_result_1__ = array.clear(inst.profileBoxes)
            __block_result__ = __block_result_1__
        return __block_result__

    def getAutoHTF():
        result: str = manualHTF
        if autoHTF:
            if timeframe.isseconds:
                s: int = timeframe.multiplier
                result = '15' if s <= 5 else '45' if s <= 15 else '120'
            elif timeframe.isintraday:
                m: int = timeframe.multiplier
                __switch_2__ = m
                if __switch_2__ == 1:
                    result = '200'
                elif __switch_2__ == 2:
                    result = '360'
                elif __switch_2__ == 5:
                    result = '720'
                elif __switch_2__ == 15:
                    result = '2D'
                elif __switch_2__ == 30:
                    result = '4D'
                elif __switch_2__ == 60:
                    result = 'W'
                elif __switch_2__ == 120:
                    result = '2W'
                else:
                    result = 'D' if m < 60 else 'M' if m < 360 else '3M'
            elif timeframe.isdaily:
                d: int = timeframe.multiplier
                result = '7M' if d == 1 else '12M' if d == 2 else '18M'
            elif timeframe.isweekly:
                result = '48M'
            elif timeframe.ismonthly:
                result = '240M'
        return result

    tfInput = getAutoHTF()
    tfChange = timeframe.change(tfInput)
    atrVal: Series = ta.atr(14)

    sumVol: PersistentSeries[float] = 0.0
    sumPV: PersistentSeries[float] = 0.0
    sumP2V: PersistentSeries[float] = 0.0
    startBar: Persistent[int] = 0

    vwapPoints: Persistent[list[ChartPoint]] = array.new(0, NA(ChartPoint))
    upperPoints: Persistent[list[ChartPoint]] = array.new(0, NA(ChartPoint))
    lowerPoints: Persistent[list[ChartPoint]] = array.new(0, NA(ChartPoint))

    sessionHistory: Persistent[list[SessionElements]] = array.new(0, NA(SessionElements))

    def trimSessionHistory():
        __block_result_2__ = na
        while array.size(sessionHistory) > maxSessions:
            oldest: SessionElements = array.shift(sessionHistory)
            __block_result_2__ = deleteSessionElements(oldest)
        return __block_result_2__

    def calcBins(uBand: float, lBand: float, currentAtr: float):
        numBins: int = manualBins
        if autoBins and currentAtr > 0 and (uBand > lBand):
            bandSpan = uBand - lBand
            calculatedBins = math.round(bandSpan / (currentAtr * 0.5))
            numBins = cast_int(math.min(250, math.max(10, calculatedBins)))
        return numBins

    def distributeBinVolume(binTotalVol: list[float], binBullCount: list[int], binBearCount: list[int], binIndex: int, v: float, isUp: bool, binCount: int):
        __block_result_3__ = na
        if binIndex >= 0 and binIndex < binCount:
            array.set(binTotalVol, binIndex, array.get(binTotalVol, binIndex) + v * 0.5)
            if isUp:
                array.set(binBullCount, binIndex, array.get(binBullCount, binIndex) + 1)
            else:
                array.set(binBearCount, binIndex, array.get(binBearCount, binIndex) + 1)

            if binIndex - 1 >= 0:
                array.set(binTotalVol, binIndex - 1, array.get(binTotalVol, binIndex - 1) + v * 0.25)

            __block_result_4__ = na
            if binIndex + 1 < binCount:
                __block_result_4__ = array.set(binTotalVol, binIndex + 1, array.get(binTotalVol, binIndex + 1) + v * 0.25)
            __block_result_3__ = __block_result_4__
        return __block_result_3__

    def getBinColor(binIdx: int, totalBins: int, currentBinVol: float, maxBinVol: float, isVwapUp: bool):
        selectedColor: Color = baseGray
        if maxBinVol > 0 and totalBins > 1:
            volWeight: float = currentBinVol / maxBinVol

            if isVwapUp:
                selectedColor = color.from_gradient(volWeight, 0.0, 1.0, baseGray, upColor)
            else:
                selectedColor = color.from_gradient(volWeight, 0.0, 1.0, baseGray, dnColor)

        return selectedColor

    def createFillPolygon(uPts: list[ChartPoint], lPts: list[ChartPoint]):
        fillPts: list[ChartPoint] = array.new(0, NA(ChartPoint))
        sz: int = array.size(uPts)
        if sz > 0:
            for i in pine_range(0, sz - 1):
                array.push(fillPts, array.get(uPts, i))
            for i in pine_range(sz - 1, 0):
                array.push(fillPts, array.get(lPts, i))
        return fillPts

    def renderProfile(uBand: float, lBand: float, sBar: int, eBar: int, binCount: int, isVwapUp: bool, sess: SessionElements):
        len: int = eBar - sBar
        __block_result_5__ = na
        if uBand > lBand and len >= 0:
            binStep = (uBand - lBand) / binCount

            binTotalVol: list[float] = array.new_float(binCount, 0.0)
            binBullCount: list[int] = array.new_int(binCount, 0)
            binBearCount: list[int] = array.new_int(binCount, 0)

            for i in pine_range(0, len):
                p = close[i + 1]
                v = volume[i + 1]
                isUp = close[i + 1] >= open[i + 1]

                if p >= lBand and p <= uBand:
                    binIndex = math.min(binCount - 1, math.floor((p - lBand) / binStep))
                    distributeBinVolume(binTotalVol, binBullCount, binBearCount, binIndex, v, isUp, binCount)

            maxBinVol: float = 0.0
            pocBinIndex: int = 0

            for b in pine_range(0, binCount - 1):
                totV = array.get(binTotalVol, b)
                if totV > maxBinVol:
                    maxBinVol = totV
                    pocBinIndex = b

            pocLeft: int = 0
            __block_result_6__ = na
            if maxBinVol > 0:
                for b in pine_range(0, binCount - 1):
                    totV = array.get(binTotalVol, b)
                    bullCount = array.get(binBullCount, b)
                    bearCount = array.get(binBearCount, b)

                    if totV > 0:
                        bLow = lBand + b * binStep
                        bHigh = bLow + binStep
                        bMid = (bLow + bHigh) / 2.0

                        barSpan = math.max(1, math.round(totV / maxBinVol * 30))
                        leftBar = math.max(sBar, eBar - barSpan)
                        rightBar = eBar

                        if b == pocBinIndex:
                            pocLeft = leftBar

                        binLineColor = getBinColor(b, binCount, totV, maxBinVol, isVwapUp)

                        pLine = line.new(x1=leftBar, y1=bMid, x2=rightBar, y2=bMid, xloc=xloc.bar_index, color=binLineColor, style=line.style_dotted, width=1)
                        array.push(sess.profileLines, pLine)

                        if showLabels:
                            bBox = box.new(left=rightBar, top=bHigh, right=rightBar + 7, bottom=bLow, xloc=xloc.bar_index, bgcolor=color.new(color.black, 100), border_color=color.new(color.black, 100), text='[+' + string.tostring(bullCount) + ' | -' + string.tostring(bearCount) + ']', text_size=size.auto, text_color=color.rgb(153, 161, 189), text_halign=text.align_left, text_valign=text.align_center)
                            array.push(sess.profileBoxes, bBox)

                __block_result_7__ = na
                if showPoc:
                    pocPrice = lBand + pocBinIndex * binStep + binStep / 2.0
                    sess.pocLine = line.new(x1=pocLeft, y1=pocPrice, x2=sBar, y2=pocPrice, xloc=xloc.bar_index, color=pocColor, style=line.style_dashed, width=2)
                    __block_result_7__ = sess.pocLine
                __block_result_6__ = __block_result_7__
            __block_result_5__ = __block_result_6__
        return __block_result_5__

    sumVol += volume
    sumPV += close * volume
    sumP2V += math.pow(close, 2) * volume

    vwapVal: Series = sumPV / sumVol
    variance = math.max(0.0, sumP2V / sumVol - math.pow(vwapVal, 2))
    stdevVal = math.sqrt(variance)

    upperBand: Series = vwapVal + stdevVal * stdevMult
    lowerBand: Series = vwapVal - stdevVal * stdevMult

    if not tfChange:
        upperBand = upperBand if barstate.isconfirmed else upperBand[1]
        lowerBand = lowerBand if barstate.isconfirmed else lowerBand[1]

    isVwapRising: bool = vwapVal >= vwapVal[1]

    if not tfChange:
        array.push(vwapPoints, chart.point.from_index(bar_index, vwapVal))
        array.push(upperPoints, chart.point.from_index(bar_index, upperBand))
        array.push(lowerPoints, chart.point.from_index(bar_index, lowerBand))

    if tfChange and bar_index > 0 and barstate.isconfirmed:
        prevVWAP = sumPV[1] / sumVol[1]
        prevVar = math.max(0.0, sumP2V[1] / sumVol[1] - math.pow(prevVWAP, 2))
        prevStdev = math.sqrt(prevVar)
        prevUpper = prevVWAP + prevStdev * stdevMult
        prevLower = prevVWAP - prevStdev * stdevMult
        prevBins = calcBins(prevUpper, prevLower, atrVal[1])

        histSession: SessionElements = SessionElements(fillPoly=na, vwapPoly=na, upperPoly=na, lowerPoly=na, profileLines=array.new_line(0), profileBoxes=array.new_box(0), pocLine=na)

        renderProfile(prevUpper, prevLower, startBar, bar_index - 1, prevBins, isVwapRising, histSession)

        if array.size(vwapPoints) > 1:
            fillPts: list[ChartPoint] = createFillPolygon(upperPoints, lowerPoints)
            histSession.fillPoly = polyline.new(fillPts, line_color=color.new(color.white, 100), fill_color=color.new(baseGray, 95))
            histSession.vwapPoly = polyline.new(vwapPoints, line_color=upColor if isVwapRising else dnColor, line_width=2)
            histSession.upperPoly = polyline.new(upperPoints, line_color=color.gray, line_width=1)
            histSession.lowerPoly = polyline.new(lowerPoints, line_color=color.gray, line_width=1)

        array.push(sessionHistory, histSession)
        trimSessionHistory()

        array.clear(vwapPoints)
        array.clear(upperPoints)
        array.clear(lowerPoints)

        sumVol = volume
        sumPV = close * volume
        sumP2V = math.pow(close, 2) * volume
        startBar = bar_index

        vwapVal = sumPV / sumVol
        upperBand = vwapVal
        lowerBand = vwapVal

        array.push(vwapPoints, chart.point.from_index(bar_index, vwapVal))
        array.push(upperPoints, chart.point.from_index(bar_index, upperBand))
        array.push(lowerPoints, chart.point.from_index(bar_index, lowerBand))

    activeBins = calcBins(upperBand, lowerBand, atrVal)

    rtLen: int = bar_index - startBar

    rtSession: Persistent[SessionElements] = na(SessionElements)

    if upperBand >= lowerBand and rtLen >= 0 and barstate.islast:
        deleteSessionElements(rtSession)

        rtSession = SessionElements(fillPoly=na, vwapPoly=na, upperPoly=na, lowerPoly=na, profileLines=array.new_line(0), profileBoxes=array.new_box(0), pocLine=na)

        if array.size(vwapPoints) > 1:
            fillPts: list[ChartPoint] = createFillPolygon(upperPoints, lowerPoints)
            rtSession.fillPoly = polyline.new(fillPts, line_color=color.new(color.white, 100), fill_color=color.new(baseGray, 95))
            rtSession.vwapPoly = polyline.new(vwapPoints, line_color=upColor if isVwapRising else dnColor, line_width=2)
            rtSession.upperPoly = polyline.new(upperPoints, line_color=color.gray, line_width=1)
            rtSession.lowerPoly = polyline.new(lowerPoints, line_color=color.gray, line_width=1)

        binStep = (upperBand - lowerBand) / activeBins if upperBand > lowerBand else 0.0

        binTotalVol: list[float] = array.new_float(activeBins, 0.0)
        binBullCount: list[int] = array.new_int(activeBins, 0)
        binBearCount: list[int] = array.new_int(activeBins, 0)

        if binStep > 0:
            for i in pine_range(0, rtLen):
                p = close[i]
                v = volume[i]
                isUp = close[i] >= open[i]

                if p >= lowerBand and p <= upperBand:
                    binIndex = math.min(activeBins - 1, math.floor((p - lowerBand) / binStep))
                    distributeBinVolume(binTotalVol, binBullCount, binBearCount, binIndex, v, isUp, activeBins)

        maxBinVol: float = 0.0
        pocBinIndex: int = 0

        for b in pine_range(0, activeBins - 1):
            totV = array.get(binTotalVol, b)
            if totV > maxBinVol:
                maxBinVol = totV
                pocBinIndex = b

        if maxBinVol > 0:
            rtRightEdge = bar_index + rightOffset
            rtPocLeft: int = 0

            for b in pine_range(0, activeBins - 1):
                totV = array.get(binTotalVol, b)
                bullCount = array.get(binBullCount, b)
                bearCount = array.get(binBearCount, b)

                if totV > 0:
                    bLow = lowerBand + b * binStep
                    bHigh = bLow + binStep
                    bMid = (bLow + bHigh) / 2.0

                    barSpan = math.max(1, math.round(totV / maxBinVol * 30))
                    leftBar = rtRightEdge - barSpan

                    if b == pocBinIndex:
                        rtPocLeft = leftBar

                    binLineColor = getBinColor(b, activeBins, totV, maxBinVol, isVwapRising)

                    pLine = line.new(x1=leftBar, y1=bMid, x2=rtRightEdge, y2=bMid, xloc=xloc.bar_index, color=binLineColor, style=line.style_solid, width=1)
                    array.push(rtSession.profileLines, pLine)

                    if showLabels:
                        bBox = box.new(left=rtRightEdge, top=bHigh, right=rtRightEdge + 12, bottom=bLow, xloc=xloc.bar_index, bgcolor=color.new(color.black, 100), border_color=color.new(color.black, 100), text='[+' + string.tostring(bullCount) + ' | -' + string.tostring(bearCount) + ']', text_size=size.auto, text_color=chart.fg_color, text_halign=text.align_left, text_valign=text.align_center)
                        array.push(rtSession.profileBoxes, bBox)

            if showPoc:
                pocPrice = lowerBand + pocBinIndex * binStep + binStep / 2.0
                rtSession.pocLine = line.new(x1=rtPocLeft, y1=pocPrice, x2=startBar, y2=pocPrice, xloc=xloc.bar_index, color=pocColor, style=line.style_solid, width=2)

    lastSignalBar: Persistent[int] = -9999
    gapMet: bool = bar_index - lastSignalBar >= 10

    upperSignal: bool = high > upperBand and close < upperBand and showSignals and gapMet and barstate.isconfirmed
    lowerSignal: bool = low < lowerBand and close > lowerBand and showSignals and gapMet and barstate.isconfirmed

    if upperSignal or lowerSignal:
        lastSignalBar = bar_index

    plotshape(high + atrVal if upperSignal else na, 'Upper Reversal', shape.triangledown, location.absolute, color=dnColor, size=size.small)
    plotshape(low - atrVal if lowerSignal else na, 'Lower Reversal', shape.triangleup, location.absolute, color=upColor, size=size.small)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)