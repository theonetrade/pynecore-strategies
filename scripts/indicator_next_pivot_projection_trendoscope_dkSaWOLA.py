"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    array, color, display, fill, format, high, input, label, line, low, math,
    matrix, na, order, plot, position, script, size, string, ta, table, xloc, yloc
)
from pynecore.types import Color, Label, Line, Matrix, Persistent
import lib.HeWhoMustNotBeNamed.arrays.v1 as pa
import lib.HeWhoMustNotBeNamed.enhanced_ta.v14 as eta
import lib.HeWhoMustNotBeNamed.mZigzag.v12 as zg


@script.indicator('Next Pivot Projection [Trendoscope]', 'NPP[Trendoscope]', overlay=True, max_lines_count=500, max_labels_count=500)
def main(
    length=input.int(8, 'Length', group='Zigzag', display=display.none),
    oscillatorType=input.string('rsi', title='Oscillator', inline='osc', options=('cci', 'cmo', 'cog', 'mfi', 'roc', 'rsi'), group='Oscillator', display=display.none),
    oscLength=input.int(14, title='', inline='osc', group='Oscillator', display=display.none),
    supertrendLength=input.int(5, 'History', inline='st', group='Supertrend', display=display.none),
    drawSupertrend=input.bool(False, 'Draw Zigzag Supertrend', inline='st2', group='Supertrend', display=display.none),
    showTable=input.bool(False, 'Detailed Stats', inline='txt', group='Stats and Display', display=display.none),
    txtSize=input.string(size.tiny, '', options=(size.tiny, size.small, size.normal, size.large, size.huge), inline='txt', group='Stats and Display', display=display.none),
    txtColor=input.color(color.white, '', inline='txt', group='Stats and Display', display=display.none),
    showPivotLines=input.bool(True, 'Pivot Lines', inline='pli', group='Stats and Display', display=display.none),
    showPivotLabel=input.bool(False, 'Pivot Label', inline='pla', group='Stats and Display', display=display.none),
    fillAreas=input.bool(True, 'Fill Bullish/Bearish Sentiments', inline='fil', group='Stats and Display', display=display.none)
):
    def increment(mtx, row, col, val = 1):
        return matrix.set(mtx, row, col, matrix.get(mtx, row, col) + val)

    def gettrendindex(price: int, osc: int, trend: int):
        trendFactor = 0 if trend > 0 else 1
        priceFactor = 1 if math.abs(price) > 1 else 0
        oscFactor = 1 if math.abs(osc) > 1 else 0
        return trendFactor * 4 + priceFactor * 2 + oscFactor

    def getSentimentDetails(pDir, oDir, sDir):
        sentiment = (-sDir if sDir == pDir or sDir * 2 == -pDir else sDir * 4) if pDir == oDir else 0 if sDir == pDir or sDir == -oDir else (sDir if math.abs(oDir) > math.abs(pDir) else -sDir) * (2 if sDir == oDir else 3)
        sentimentSymbol = '⬆' if sentiment == 4 else '⬇' if sentiment == -4 else '↗' if sentiment == 3 else '↘' if sentiment == -3 else '⤴' if sentiment == 2 else '⤵' if sentiment == -2 else '⤒' if sentiment == 1 else '⤓' if sentiment == -1 else '▣'
        sentimentColor = color.green if sentiment == 4 else color.red if sentiment == -4 else color.lime if sentiment == 3 else color.orange if sentiment == -3 else color.rgb(202, 224, 13, 0) if sentiment == 2 else color.rgb(250, 128, 114, 0) if sentiment == -2 else color.silver
        sentimentLabel = 'C' if math.abs(sentiment) == 4 else 'H' if math.abs(sentiment) == 3 else 'D' if math.abs(sentiment) == 2 else 'I'
        return (sentimentSymbol, sentimentLabel, sentimentColor)

    def getStatus(trendIndex: int, pivotDir: int):
        trendFactor = cast_int(trendIndex / 4)
        remainder = trendIndex % 4
        priceFactor = cast_int(remainder / 2) + 1
        oscFactor = remainder % 2 + 1
        trendChar = 'U' if trendFactor == 0 else 'D'
        priceChar = ('HH' if priceFactor == 2 else 'LH') if pivotDir > 0 else 'LL' if priceFactor == 2 else 'HL'
        oscChar = ('HH' if oscFactor == 2 else 'LH') if pivotDir > 0 else 'LL' if oscFactor == 2 else 'HL'
        return trendChar + ' - ' + priceChar + '/' + oscChar

    def draw_zg_line(idx1, idx2, zigzaglines, zigzaglabels, valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, trendArray, lineColor, lineWidth, lineStyle):
        __block_result__ = na
        if matrix.rows(valueMatrix) > 2:
            idxLen1 = matrix.rows(valueMatrix) - idx1
            idxLen2 = matrix.rows(valueMatrix) - idx2
            lastValues = matrix.row(valueMatrix, idxLen1)
            llastValues = matrix.row(valueMatrix, idxLen2)
            lastDirections = matrix.row(directionMatrix, idxLen1)
            lastRatios = matrix.row(ratioMatrix, idxLen1)
            lastDivergence = matrix.row(divergenceMatrix, idxLen1)
            lastDoubleDivergence = matrix.row(doubleDivergenceMatrix, idxLen1)
            y1 = array.get(lastValues, 0)
            y2 = array.get(llastValues, 0)
            x1 = array.get(barArray, idxLen1)
            x2 = array.get(barArray, idxLen2)
            zline = line.new(x1=x1, y1=y1, x2=x2, y2=y2, color=lineColor, width=lineWidth, style=lineStyle)
            currentDir__0000003c__ = 1 if y1 > y2 else -1
            priceDir = array.get(lastDirections, 0)
            oscDir = array.get(lastDirections, 1)
            trendDir = array.get(trendArray, idxLen1)
            trendIndex = gettrendindex(priceDir, oscDir, trendDir)
            trendLabel = getStatus(trendIndex, currentDir__0000003c__)
            sentimentSymbol, sentimentLabel, sentimentColor = getSentimentDetails(priceDir, oscDir, trendDir)
            labelStyle = label.style_label_down if currentDir__0000003c__ > 0 else label.style_label_up
            zlabel = label.new(x=x1, y=y1, yloc=yloc.price, color=sentimentColor, style=labelStyle, text=sentimentSymbol + ' ' + trendLabel, textcolor=color.black, size=size.small, tooltip=sentimentLabel) if showPivotLabel else na
            if array.size(zigzaglines) > 0:
                lastLine = array.get(zigzaglines, array.size(zigzaglines) - 1)
                if line.get_x2(lastLine) == x2 and line.get_x1(lastLine) <= x1:
                    pa.pop(zigzaglines)
                    pa.pop(zigzaglabels)
            pa.push(zigzaglines, zline, 500)
            __block_result__ = pa.push(zigzaglabels, zlabel, 500)
        return __block_result__

    def draw(valueMatrix: Matrix[float], directionMatrix: Matrix[int], ratioMatrix: Matrix[float], divergenceMatrix: Matrix[int], doubleDivergenceMatrix: Matrix[int], barArray: list[int], trendArray: list[int], newZG: bool, doubleZG: bool, lineColor: Color = color.blue, lineWidth: int = 1, lineStyle: str = line.style_solid):
        zigzaglines: Persistent[list[Line]] = array.new_line(0)
        zigzaglabels: Persistent[list[Label]] = array.new_label(0)
        if newZG:
            if doubleZG:
                draw_zg_line(2, 3, zigzaglines, zigzaglabels, valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, trendArray, lineColor, lineWidth, lineStyle)
            if matrix.rows(valueMatrix) >= 2:
                draw_zg_line(1, 2, zigzaglines, zigzaglabels, valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, trendArray, lineColor, lineWidth, lineStyle)
        return (valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, zigzaglines, zigzaglabels)

    indicatorHigh: list[float] = array.new_float()
    indicatorLow: list[float] = array.new_float()
    indicatorLabels: list[str] = array.new_string()
    oscHigh, _, _ = eta.oscillator(oscillatorType, oscLength, oscLength, oscLength, high)
    oscLow, _, _ = eta.oscillator(oscillatorType, oscLength, oscLength, oscLength, low)
    array.push(indicatorHigh, math.round(oscHigh, 2))
    array.push(indicatorLow, math.round(oscLow, 2))
    array.push(indicatorLabels, oscillatorType + string.tostring(oscLength))
    valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, trendArray, supertrendDir, supertrend, newZG, doubleZG = zg.calculate(length, array.from_items(high, low), indicatorHigh, indicatorLow, supertrendLength=supertrendLength)
    nextDirection = matrix.row(directionMatrix, matrix.rows(directionMatrix) - 1) if matrix.rows(directionMatrix) > 0 else array.new_int()
    lastDirection = matrix.row(directionMatrix, matrix.rows(directionMatrix) - 2) if matrix.rows(directionMatrix) > 1 else array.new_int()
    llastDirection = matrix.row(directionMatrix, matrix.rows(directionMatrix) - 3) if matrix.rows(directionMatrix) > 2 else array.new_int()
    lllastDirection = matrix.row(directionMatrix, matrix.rows(directionMatrix) - 4) if matrix.rows(directionMatrix) > 3 else array.new_int()
    pivotHighStats: Persistent[Matrix[int]] = matrix.new(64, 3, 0)
    pivotLowStats: Persistent[Matrix[int]] = matrix.new(64, 3, 0)
    pivotHighRatios: Persistent[Matrix[float]] = matrix.new(64, 3, 0.0)
    pivotLowRatios: Persistent[Matrix[float]] = matrix.new(64, 3, 0.0)
    pivotHighBars: Persistent[Matrix[float]] = matrix.new(64, 3, 0.0)
    pivotLowBars: Persistent[Matrix[float]] = matrix.new(64, 3, 0.0)
    currentTotalTrendIndex: int = 0
    nextTotalTrendIndex: int = 0
    currentDir = matrix.get(directionMatrix, matrix.rows(directionMatrix) - 1, 0) if matrix.rows(directionMatrix) > 0 else 0
    currentPDir = method_call('first', lastDirection) if method_call('size', lastDirection) > 0 else na
    changePriceDirection = ta.change(math.sign(currentPDir))
    if array.size(lllastDirection) > 0:
        priceDirection = array.get(lastDirection, 0)
        priceRatio = matrix.get(ratioMatrix, matrix.rows(ratioMatrix) - 2, 0)
        numberOfBars = array.get(barArray, array.size(barArray) - 2) - array.get(barArray, array.size(barArray) - 3)
        currentPriceDirection = array.get(lastDirection, 0)
        currentOscDirection = array.get(lastDirection, 1)
        currentTrend = array.get(trendArray, array.size(trendArray) - 2)
        nextPriceDirection = array.get(nextDirection, 0)
        nextOscDirection = array.get(nextDirection, 1)
        nextTrend = array.get(trendArray, array.size(trendArray) - 1)
        lastPriceDirection = array.get(llastDirection, 0)
        lastOscDirection = array.get(llastDirection, 1)
        lastTrend = array.get(trendArray, array.size(trendArray) - 3)
        llastPriceDirection = array.get(lllastDirection, 0)
        llastOscDirection = array.get(lllastDirection, 1)
        llastTrend = array.get(trendArray, array.size(trendArray) - 4)
        colLast = math.abs(priceDirection) % 2
        nextTrendIndex = gettrendindex(nextPriceDirection, nextOscDirection, nextTrend)
        currentTrendIndex = gettrendindex(currentPriceDirection, currentOscDirection, currentTrend)
        lastTrendIndex = gettrendindex(lastPriceDirection, lastOscDirection, lastTrend)
        llastTrendIndex = gettrendindex(llastPriceDirection, llastOscDirection, llastTrend)
        totalIndex = lastTrendIndex * 8 + llastTrendIndex
        currentTotalTrendIndex = currentTrendIndex * 8 + lastTrendIndex
        nextTotalTrendIndex = nextTrendIndex * 8 + currentTrendIndex
        matrixToSet = pivotHighStats if math.sign(priceDirection) > 0 else pivotLowStats
        ratioMatrixToSet = pivotHighRatios if math.sign(priceDirection) > 0 else pivotLowRatios
        barMatrixToSet = pivotHighBars if math.sign(priceDirection) > 0 else pivotLowBars
        if not na(currentPDir) and changePriceDirection != 0:
            increment(matrixToSet, totalIndex, colLast)
            increment(ratioMatrixToSet, totalIndex, colLast, priceRatio)
            increment(barMatrixToSet, totalIndex, colLast, numberOfBars)
            increment(matrixToSet, totalIndex, 2)
            increment(ratioMatrixToSet, totalIndex, 2, priceRatio)
            increment(barMatrixToSet, totalIndex, 2, numberOfBars)
    hhValue: Persistent[float] = na(float)
    lhValue: Persistent[float] = na(float)
    llValue: Persistent[float] = na(float)
    hlValue: Persistent[float] = na(float)
    hhProbability: Persistent[float] = na(float)
    llProbability: Persistent[float] = na(float)
    htRatio: Persistent[float] = na(float)
    ltRatio: Persistent[float] = na(float)
    if array.size(barArray) > 10:
        currentBar = array.get(barArray, array.size(barArray) - 1)
        lastBar = array.get(barArray, array.size(barArray) - 2)
        currentPrice = matrix.get(valueMatrix, matrix.rows(valueMatrix) - 1, 0)
        lastPrice = matrix.get(valueMatrix, matrix.rows(valueMatrix) - 2, 0)
        llastPrice = matrix.get(valueMatrix, matrix.rows(valueMatrix) - 3, 0)
        startRow: int = 2
        statsTable: Persistent = table.new(position=position.top_right, columns=10, rows=64 + startRow, border_color=color.black, border_width=2) if showTable else na
        phSortIndices = array.sort_indices(matrix.col(pivotHighStats, 2), order.descending)
        phColStart = 0 if currentDir > 0 else 5
        if showTable:
            table.clear(statsTable, 0, 0, 9, 64 + startRow - 1)
            table.cell(statsTable, phColStart, 0, 'Pivot High Projection', text_color=txtColor, text_size=txtSize, bgcolor=color.maroon)
            table.cell(statsTable, phColStart, 1, 'Last Two Pivots', text_color=txtColor, text_size=txtSize, bgcolor=color.maroon)
            table.cell(statsTable, phColStart + 2, 1, 'HH', text_color=txtColor, text_size=txtSize, bgcolor=color.maroon)
            table.cell(statsTable, phColStart + 3, 1, 'LH', text_color=txtColor, text_size=txtSize, bgcolor=color.maroon)
            table.cell(statsTable, phColStart + 4, 1, 'T', text_color=txtColor, text_size=txtSize, bgcolor=color.maroon)
            table.merge_cells(statsTable, phColStart, 0, phColStart + 4, 0)
            table.merge_cells(statsTable, phColStart, 1, phColStart + 1, 1)
        hlr = startRow
        for i in pine_range(0, 63, 1):
            si = array.get(phSortIndices, i)
            lastTrendIndex = cast_int(si / 8)
            llastTrendIndex = si % 8
            lastPivotStatus = getStatus(lastTrendIndex, -1)
            llastPivotStatus = getStatus(llastTrendIndex, 1)
            hhStats = matrix.get(pivotHighStats, si, 0)
            lhStats = matrix.get(pivotHighStats, si, 1)
            tStats = matrix.get(pivotHighStats, si, 2)
            hhRatio = math.round(matrix.get(pivotHighRatios, si, 0) / hhStats, 3)
            lhRatio = math.round(matrix.get(pivotHighRatios, si, 1) / lhStats, 3)
            tRatio = math.round(matrix.get(pivotHighRatios, si, 2) / tStats, 3)
            hhBars = math.round(matrix.get(pivotHighBars, si, 0) / hhStats)
            lhBars = math.round(matrix.get(pivotHighBars, si, 1) / lhStats)
            tBars = math.round(matrix.get(pivotHighBars, si, 2) / tStats)
            highlight = nextTotalTrendIndex == si if math.sign(currentDir) < 0 else currentTotalTrendIndex == si
            hhTooltip = 'Average Ratio - ' + string.tostring(hhRatio) + '\n' + 'Average Bars - ' + string.tostring(hhBars)
            lhTooltip = 'Average Ratio - ' + string.tostring(lhRatio) + '\n' + 'Average Bars - ' + string.tostring(lhBars)
            tTooltip = 'Average Ratio - ' + string.tostring(tRatio) + '\n' + 'Average Bars - ' + string.tostring(tBars)
            if highlight:
                hhLine: Persistent[Line] = na(Line)
                lhLine: Persistent[Line] = na(Line)
                tLine: Persistent[Line] = na(Line)
                hhLabel: Persistent[Label] = na(Label)
                lhLabel: Persistent[Label] = na(Label)
                tLabel: Persistent[Label] = na(Label)
                line.delete(hhLine)
                line.delete(lhLine)
                line.delete(tLine)
                label.delete(hhLabel)
                label.delete(lhLabel)
                label.delete(tLabel)
                x1 = currentBar if math.sign(currentDir) < 0 else lastBar
                hhX2 = x1 + hhBars
                lhX2 = x1 + lhBars
                tX2 = x1 + tBars
                y1 = currentPrice if math.sign(currentDir) < 0 else lastPrice
                prev = lastPrice if math.sign(currentDir) < 0 else llastPrice
                hhY2 = math.round_to_mintick(y1 + math.abs(y1 - prev) * hhRatio)
                lhY2 = math.round_to_mintick(y1 + math.abs(y1 - prev) * lhRatio)
                tY2 = math.round_to_mintick(y1 + math.abs(y1 - prev) * tRatio)
                hhLine = line.new(x1, y1, hhX2, hhY2, xloc=xloc.bar_index, color=color.green, style=line.style_arrow_right)
                lhLine = line.new(x1, y1, lhX2, lhY2, xloc=xloc.bar_index, color=color.lime, style=line.style_arrow_right)
                tLine = line.new(x1, y1, tX2, tY2, xloc=xloc.bar_index, color=color.yellow, style=line.style_arrow_right)
                hhPercent = string.tostring(hhStats * 100 / tStats, format.percent)
                lhPercent = string.tostring(lhStats * 100 / tStats, format.percent)
                hhText = 'Number of Historical References :' + string.tostring(hhStats) + '/' + string.tostring(tStats) + '\nProbability of Higher High :' + hhPercent + '\nAverage Higher High Ratio :' + string.tostring(hhRatio) + '\nAverage Higher High Bars :' + string.tostring(hhBars)
                lhText = 'Number of Historical References :' + string.tostring(lhStats) + '/' + string.tostring(tStats) + '\nProbability of Lower High :' + lhPercent + '\nAverage Lower High Ratio :' + string.tostring(lhRatio) + '\nAverage Lower High Bars :' + string.tostring(lhBars)
                tText = 'Number of Historical References :' + string.tostring(tStats) + '\nAverage Fib Ratio :' + string.tostring(tRatio) + '\nAverage Bars :' + string.tostring(tBars)
                hhLabel = label.new(hhX2, hhY2, string.tostring(hhY2) + ' - ' + hhPercent, style=label.style_label_lower_left, color=color.new(color.green, 70), textcolor=color.white, size=size.small, tooltip=hhText)
                lhLabel = label.new(lhX2, lhY2, string.tostring(lhY2) + ' - ' + lhPercent, style=label.style_label_upper_left, color=color.new(color.lime, 70), textcolor=color.white, size=size.small, tooltip=lhText)
                tLabel = label.new(tX2, tY2, string.tostring(tY2) + '@' + string.tostring(tRatio), style=label.style_label_left, color=color.new(color.yellow, 70), textcolor=color.white, size=size.small, tooltip=tText)
                hhValue = hhY2
                lhValue = lhY2
                hhProbability = hhStats * 100 / tStats
                htRatio = tRatio
            if hhStats != 0 and lhStats != 0 and showTable:
                table.cell(statsTable, phColStart, hlr, llastPivotStatus, text_color=txtColor, text_size=txtSize, bgcolor=color.new(color.lime, 60))
                table.cell(statsTable, phColStart + 1, hlr, lastPivotStatus, text_color=txtColor, text_size=txtSize, bgcolor=color.new(color.orange, 60))
                table.cell(statsTable, phColStart + 2, hlr, string.tostring(hhStats) + ' - ' + string.tostring(hhRatio), text_color=txtColor, text_size=txtSize, bgcolor=color.new(color.green, 50 if highlight else 90), tooltip=hhTooltip)
                table.cell(statsTable, phColStart + 3, hlr, string.tostring(lhStats) + ' - ' + string.tostring(lhRatio), text_color=txtColor, text_size=txtSize, bgcolor=color.new(color.red, 50 if highlight else 90), tooltip=lhTooltip)
                table.cell(statsTable, phColStart + 4, hlr, string.tostring(tStats) + ' - ' + string.tostring(tRatio), text_color=txtColor, text_size=txtSize, bgcolor=color.from_gradient(hhStats / tStats, 0, 1, color.red, color.green), tooltip=tTooltip)
                hlr = hlr + 1
        plColStart = 0 if currentDir < 0 else 5
        if showTable:
            table.cell(statsTable, plColStart, 0, 'Pivot Low Projection', text_color=txtColor, text_size=txtSize, bgcolor=color.maroon)
            table.cell(statsTable, plColStart, 1, 'Last Two Pivots', text_color=txtColor, text_size=txtSize, bgcolor=color.maroon)
            table.cell(statsTable, plColStart + 2, 1, 'LL', text_color=txtColor, text_size=txtSize, bgcolor=color.maroon)
            table.cell(statsTable, plColStart + 3, 1, 'HL', text_color=txtColor, text_size=txtSize, bgcolor=color.maroon)
            table.cell(statsTable, plColStart + 4, 1, 'T', text_color=txtColor, text_size=txtSize, bgcolor=color.maroon)
            table.merge_cells(statsTable, plColStart, 0, plColStart + 4, 0)
            table.merge_cells(statsTable, plColStart, 1, plColStart + 1, 1)
        plSortIndices = array.sort_indices(matrix.col(pivotLowStats, 2), order.descending)
        llr = startRow
        for i in pine_range(0, 63, 1):
            si = array.get(plSortIndices, i)
            lastTrendIndex = cast_int(si / 8)
            llastTrendIndex = si % 8
            lastPivotStatus = getStatus(lastTrendIndex, 1)
            llastPivotStatus = getStatus(llastTrendIndex, -1)
            llStats = matrix.get(pivotLowStats, si, 0)
            hlStats = matrix.get(pivotLowStats, si, 1)
            tStats = matrix.get(pivotLowStats, si, 2)
            llRatio = math.round(matrix.get(pivotLowRatios, si, 0) / llStats, 3)
            hlRatio = math.round(matrix.get(pivotLowRatios, si, 1) / hlStats, 3)
            tRatio = math.round(matrix.get(pivotLowRatios, si, 2) / tStats, 3)
            llBars = math.round(matrix.get(pivotLowBars, si, 0) / llStats)
            hlBars = math.round(matrix.get(pivotLowBars, si, 1) / hlStats)
            tBars = math.round(matrix.get(pivotLowBars, si, 2) / tStats)
            highlight = nextTotalTrendIndex == si if math.sign(currentDir) > 0 else currentTotalTrendIndex == si
            llTooltip = 'Average Ratio - ' + string.tostring(llRatio) + '\n' + 'Average Bars - ' + string.tostring(llBars)
            hlTooltip = 'Average Ratio - ' + string.tostring(hlRatio) + '\n' + 'Average Bars - ' + string.tostring(hlBars)
            tTooltip = 'Average Ratio - ' + string.tostring(tRatio) + '\n' + 'Average Bars - ' + string.tostring(tBars)
            if highlight:
                llLine: Persistent[Line] = na(Line)
                hlLine: Persistent[Line] = na(Line)
                tLine: Persistent[Line] = na(Line)
                llLabel: Persistent[Label] = na(Label)
                hlLabel: Persistent[Label] = na(Label)
                tLabel: Persistent[Label] = na(Label)
                line.delete(llLine)
                line.delete(hlLine)
                line.delete(tLine)
                label.delete(llLabel)
                label.delete(hlLabel)
                label.delete(tLabel)
                x1 = currentBar if math.sign(currentDir) > 0 else lastBar
                llX2 = x1 + llBars
                hlX2 = x1 + hlBars
                tX2 = x1 + tBars
                y1 = currentPrice if math.sign(currentDir) > 0 else lastPrice
                prev = lastPrice if math.sign(currentDir) > 0 else llastPrice
                llY2 = math.round_to_mintick(y1 - math.abs(y1 - prev) * llRatio)
                hlY2 = math.round_to_mintick(y1 - math.abs(y1 - prev) * hlRatio)
                tY2 = math.round_to_mintick(y1 - math.abs(y1 - prev) * tRatio)
                llLine = line.new(x1, y1, llX2, llY2, xloc=xloc.bar_index, color=color.red, style=line.style_arrow_right)
                hlLine = line.new(x1, y1, hlX2, hlY2, xloc=xloc.bar_index, color=color.orange, style=line.style_arrow_right)
                tLine = line.new(x1, y1, tX2, tY2, xloc=xloc.bar_index, color=color.yellow, style=line.style_arrow_right)
                llPercent = string.tostring(llStats * 100 / tStats, format.percent)
                hlPercent = string.tostring(hlStats * 100 / tStats, format.percent)
                llText = 'Number of Historical References :' + string.tostring(llStats) + '/' + string.tostring(tStats) + '\nProbability of Lower Low :' + llPercent + '\nAverage Lower Low Ratio :' + string.tostring(llRatio) + '\nAverage Lower Low Bars :' + string.tostring(llBars)
                hlText = 'Number of Historical References :' + string.tostring(hlStats) + '/' + string.tostring(tStats) + '\nProbability of Higher Low :' + hlPercent + '\nAverage Higher Low Ratio :' + string.tostring(hlRatio) + '\nAverage Higher Low Bars :' + string.tostring(hlBars)
                tText = 'Number of Historical References :' + string.tostring(tStats) + '\nAverage Fib Ratio :' + string.tostring(tRatio) + '\nAverage Bars :' + string.tostring(tBars)
                llLabel = label.new(llX2, llY2, string.tostring(llY2) + ' - ' + llPercent, style=label.style_label_upper_left, color=color.new(color.red, 70), textcolor=color.white, size=size.small, tooltip=llText)
                hlLabel = label.new(hlX2, hlY2, string.tostring(hlY2) + ' - ' + hlPercent, style=label.style_label_lower_left, color=color.new(color.orange, 70), textcolor=color.white, size=size.small, tooltip=hlText)
                tLabel = label.new(tX2, tY2, string.tostring(tY2) + '@' + string.tostring(tRatio), style=label.style_label_left, color=color.new(color.yellow, 70), textcolor=color.white, size=size.small, tooltip=tText)
                llValue = llY2
                hlValue = hlY2
                llProbability = llStats * 100 / tStats
                ltRatio = tRatio
            if llStats != 0 and hlStats != 0 and showTable:
                table.cell(statsTable, plColStart, llr, llastPivotStatus, text_color=txtColor, text_size=txtSize, bgcolor=color.new(color.orange, 60))
                table.cell(statsTable, plColStart + 1, llr, lastPivotStatus, text_color=txtColor, text_size=txtSize, bgcolor=color.new(color.lime, 60))
                table.cell(statsTable, plColStart + 2, llr, string.tostring(llStats) + ' - ' + string.tostring(llRatio), text_color=txtColor, text_size=txtSize, bgcolor=color.new(color.red, 50 if highlight else 90), tooltip=llTooltip)
                table.cell(statsTable, plColStart + 3, llr, string.tostring(hlStats) + ' - ' + string.tostring(hlRatio), text_color=txtColor, text_size=txtSize, bgcolor=color.new(color.green, 50 if highlight else 90), tooltip=hlTooltip)
                table.cell(statsTable, plColStart + 4, llr, string.tostring(tStats) + ' - ' + string.tostring(tRatio), text_color=txtColor, text_size=txtSize, bgcolor=color.from_gradient(llStats / tStats, 0, 1, color.green, color.red), tooltip=tTooltip)
                llr = llr + 1
    if showPivotLines:
        draw(valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, trendArray, newZG, doubleZG)
    plot(supertrend if drawSupertrend else na, color=color.green if supertrendDir > 0 else color.red, style=plot.style_linebr)
    hhp = plot(hhValue if fillAreas else na, 'Higher High Range', color.new(color.green, 100), 1)
    lhp = plot(lhValue if fillAreas else na, 'Lower High Range', color.new(color.lime, 100), 1)
    llp = plot(llValue if fillAreas else na, 'Lower Low Range', color.new(color.red, 100), 1)
    hlp = plot(hlValue if fillAreas else na, 'Higher Low Range', color.new(color.orange, 100), 1)
    fill(hhp, lhp, color=color.new(color.green if hhProbability > 50 else color.red if hhProbability < 50 else color.silver, 90))
    fill(llp, hlp, color=color.new(color.red if llProbability > 50 else color.green if llProbability < 50 else color.silver, 90))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)