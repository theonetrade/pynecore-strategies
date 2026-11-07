"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    array, bar_index, color, label, line, math, matrix, na, script, size,
    string, ta, time, yloc
)
from pynecore.types import Color, Label, Line, Matrix, NA, Persistent, Series
from typing import Protocol, Any
import lib.HeWhoMustNotBeNamed._matrix.v5 as ma
import lib.HeWhoMustNotBeNamed.arrays.v1 as pa
import lib.HeWhoMustNotBeNamed.enhanced_ta.v14 as eta
import lib.HeWhoMustNotBeNamed.supertrend.v6 as st


__all__ = ['calculate', 'calculateplain', 'draw']


class _ProtocolCalculate(Protocol):
    def __call__(self, length: int, ohlc: list[float], indicatorHigh: list[float], indicatorLow: list[float], numberOfPivots: int = 20, supertrendLength: int = 5) -> Any: ...


class _ProtocolCalculateplain(Protocol):
    def __call__(self, length: int, ohlc: list[float], indicatorHigh: list[float], indicatorLow: list[float], numberOfPivots: int = 20, offset: int = 0) -> Any: ...


class _ProtocolDraw(Protocol):
    def __call__(self, valueMatrix: Matrix[float], directionMatrix: Matrix[int], ratioMatrix: Matrix[float], divergenceMatrix: Matrix[int], doubleDivergenceMatrix: Matrix[int], barArray: list[int], newZG: bool, doubleZG: bool, indicatorLabels: list[str], lineColor: Color = color.blue, lineWidth: int = 1, lineStyle: str = line.style_solid, showLabel: bool = True, showIndicators: bool = True) -> Any: ...


class _ProtocolDraw3(Protocol):
    def __call__(self, length: int, ohlc: list[float], indicatorLabels: list[str], indicatorHigh: list[float], indicatorLow: list[float], numberOfPivots: int = 20, lineColor: Color = color.blue, lineWidth: int = 1, lineStyle: str = line.style_solid, showLabel: bool = True, showIndicators: bool = True) -> Any: ...


calculate: _ProtocolCalculate = Exported()
calculateplain: _ProtocolCalculateplain = Exported()
draw: _ProtocolDraw = Exported()
draw: _ProtocolDraw3 = Exported()


@script.library('mZigzag', overlay=True)
def main():
    def pivots(length, ohlc: list[float]):
        highSource = array.max(ohlc)
        lowSource = array.min(ohlc)
        phighbar: int = ta.highestbars(highSource, length)
        plowbar: int = ta.lowestbars(lowSource, length)
        phigh: float = ta.highest(highSource, length)
        plow: float = ta.lowest(lowSource, length)
        return (phigh, phighbar, plow, plowbar)

    def calculateDivergence(oDir, pDir, sDir):
        divergence = (-sDir if sDir == pDir or sDir * 2 == -pDir else sDir * 4) if pDir == oDir else 0 if sDir == pDir or sDir == -oDir else (sDir if math.abs(oDir) > math.abs(pDir) else -sDir) * (2 if sDir == oDir else 3)
        return divergence

    def getSentimentDetails(sentiment):
        sentimentSymbol = '⬆' if sentiment == 4 else '⬇' if sentiment == -4 else '↗' if sentiment == 3 else '↘' if sentiment == -3 else '⤴' if sentiment == 2 else '⤵' if sentiment == -2 else '⤒' if sentiment == 1 else '⤓' if sentiment == -1 else '▣'
        sentimentColor = color.green if sentiment == 4 else color.red if sentiment == -4 else color.lime if sentiment == 3 else color.orange if sentiment == -3 else color.rgb(202, 224, 13, 0) if sentiment == 2 else color.rgb(250, 128, 114, 0) if sentiment == -2 else color.silver
        sentimentLabel = 'C' if math.abs(sentiment) == 4 else 'H' if math.abs(sentiment) == 3 else 'D' if math.abs(sentiment) == 2 else 'I'
        return (sentimentSymbol, sentimentLabel, sentimentColor)

    def addnewpivot(valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, trendArray, value, bar, dir, indicatorHigh: Series, indicatorLow: Series, numberOfPivots, supertrendDir):
        indicatorArray: list[float] = indicatorHigh[bar_index - bar] if dir > 0 else indicatorLow[bar_index - bar]
        if na(indicatorArray):
            indicatorArray = array.new_float(array.size(indicatorHigh))
        newValueArray = array.from_items(value)
        array.concat(newValueArray, indicatorArray)
        size__ren__ = array.size(newValueArray)
        newRatios: list[float] = array.new_float(size__ren__, 1.0)
        newDirections: list[int] = array.new_int(size__ren__, cast_int(dir))
        newDivergences: list[int] = array.new_int(size__ren__, 0)
        newDoubleDivergences: list[int] = array.new_int(size__ren__, 0)
        if matrix.rows(valueMatrix) >= 2:
            lastValues = matrix.row(valueMatrix, matrix.rows(valueMatrix) - 1)
            llastValues = matrix.row(valueMatrix, matrix.rows(valueMatrix) - 2)
            llastDivergence = matrix.row(divergenceMatrix, matrix.rows(divergenceMatrix) - 2)
            for i in pine_range(0, array.size(lastValues) - 1, 1):
                cValue = array.get(newValueArray, i)
                lastPoint = array.get(lastValues, i)
                llastPoint = array.get(llastValues, i)
                newDir = dir * 2 if dir * cValue > dir * llastPoint else dir
                newRatio = math.round(math.abs(cValue - lastPoint) / math.abs(llastPoint - lastPoint), 2)
                array.set(newDirections, i, cast_int(newDir))
                array.set(newRatios, i, newRatio)
                pDir = array.get(newDirections, 0)
                divergence = calculateDivergence(newDir, pDir, supertrendDir)
                array.set(newDivergences, i, divergence)
                doubleDivergence: int = 0
                if matrix.rows(valueMatrix) >= 4:
                    lastDivergence = array.get(llastDivergence, i)
                    doubleDivergence = divergence if divergence == lastDivergence else 0
                array.set(newDoubleDivergences, i, doubleDivergence)
        ma.push(valueMatrix, newValueArray, numberOfPivots)
        ma.push(directionMatrix, newDirections, numberOfPivots)
        ma.push(ratioMatrix, newRatios, numberOfPivots)
        ma.push(divergenceMatrix, newDivergences, numberOfPivots)
        ma.push(doubleDivergenceMatrix, newDoubleDivergences, numberOfPivots)
        pa.push(barArray, bar, numberOfPivots)
        return pa.push(trendArray, supertrendDir, numberOfPivots)

    def addnewpivotplain(valueMatrix, directionArray, barArray, value, bar, dir, indicatorHigh: Series, indicatorLow: Series, numberOfPivots):
        indicatorArray: list[float] = indicatorHigh[bar_index - bar] if dir > 0 else indicatorLow[bar_index - bar]
        if na(indicatorArray):
            indicatorArray = array.new_float(array.size(indicatorHigh))
        newValueArray = array.from_items(value)
        array.concat(newValueArray, indicatorArray)
        size__ren__ = array.size(newValueArray)
        newDir = dir
        if matrix.rows(valueMatrix) >= 2:
            llastValue = matrix.get(valueMatrix, 1, 0)
            newDir = dir * 2 if dir * value > dir * llastValue else dir
        ma.unshift(valueMatrix, newValueArray, numberOfPivots)
        pa.unshift(directionArray, newDir, numberOfPivots)
        return pa.unshift(barArray, bar, numberOfPivots)

    def zigzagcore(length: int, ohlc: list[float], indicatorHigh: list[float], indicatorLow: list[float], numberOfPivots: int = 20, supertrendLength: int = 5):
        valueMatrix: Persistent[Matrix[float]] = matrix.new(initial_value=NA(float))
        directionMatrix: Persistent[Matrix[int]] = matrix.new(initial_value=NA(int))
        ratioMatrix: Persistent[Matrix[float]] = matrix.new(initial_value=NA(float))
        divergenceMatrix: Persistent[Matrix[int]] = matrix.new(initial_value=NA(int))
        doubleDivergenceMatrix: Persistent[Matrix[int]] = matrix.new(initial_value=NA(int))
        barArray: Persistent[list[int]] = array.new_int()
        trendArray: Persistent[list[int]] = array.new_int()
        phigh, phighbar, plow, plowbar = pivots(length, ohlc)
        pDir: float = 1
        newPivot = phighbar == 0 or plowbar == 0
        doublePivot = phighbar == 0 and plowbar == 0
        updateLastPivot: bool = False
        supertrendDir: int = na(int)
        supertrend: float = na(float)
        if matrix.rows(valueMatrix) > supertrendLength * 2 + 1:
            zigzagpivotArray = array.copy(matrix.col(valueMatrix, 0))
            array.reverse(zigzagpivotArray)
            sDir, sTrend = st.zsupertrend(zigzagpivotArray, supertrendLength)
            supertrendDir = sDir
            supertrend = sTrend
        if matrix.columns(directionMatrix) >= 1:
            pDir = math.sign(matrix.get(directionMatrix, matrix.rows(directionMatrix) - 1, 0))
        newBar = bar_index
        if (pDir == 1 and phighbar == 0 or (pDir == -1 and plowbar == 0)) and matrix.rows(valueMatrix) >= 1:
            value = phigh if pDir == 1 else plow
            ipivot = plow if pDir == 1 else phigh
            pivotbar = array.get(barArray, matrix.rows(valueMatrix) - 1)
            pivot = matrix.get(valueMatrix, matrix.rows(valueMatrix) - 1, 0)
            pivotdir = matrix.get(directionMatrix, matrix.rows(directionMatrix) - 1, 0)
            removeOld = value * pivotdir > pivot * pivotdir
            addInverse: bool = False
            if removeOld:
                updateLastPivot = True
                ma.pop(valueMatrix)
                ma.pop(ratioMatrix)
                ma.pop(directionMatrix)
                ma.pop(divergenceMatrix)
                ma.pop(doubleDivergenceMatrix)
                pa.pop(barArray)
                pa.pop(trendArray)
                addnewpivot(valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, trendArray, value, newBar, pDir, indicatorHigh, indicatorLow, numberOfPivots, supertrendDir)
                if matrix.rows(valueMatrix) > 1 and doublePivot:
                    llastPivot = matrix.get(valueMatrix, matrix.rows(valueMatrix) - 2, 0)
                    if -pDir * llastPivot >= -pDir * ipivot:
                        addInverse = True
            elif not removeOld and (not doublePivot) or addInverse:
                ipivotbar = newBar + plowbar if pDir == 1 else newBar + phighbar
                ipivottime = time[newBar - ipivotbar]
                addnewpivot(valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, trendArray, ipivot, ipivotbar, -pDir, indicatorHigh, indicatorLow, numberOfPivots, supertrendDir)
                doublePivot = True
        if pDir == 1 and plowbar == 0 or (pDir == -1 and phighbar == 0):
            value = plow if pDir == 1 else phigh
            addnewpivot(valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, trendArray, value, newBar, -pDir, indicatorHigh, indicatorLow, numberOfPivots, supertrendDir)
        return (valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, trendArray, supertrendDir, supertrend, newPivot, doublePivot)

    def zigzagcoreplain(length: int, ohlc: list[float], indicatorHigh: list[float], indicatorLow: list[float], numberOfPivots: int = 20, offset: int = 0):
        valueMatrix: Persistent[Matrix[float]] = matrix.new(initial_value=NA(float))
        directionArray: Persistent[list[int]] = array.new_int()
        barArray: Persistent[list[int]] = array.new_int()
        phigh, phighbar, plow, plowbar = pivots(length, ohlc)
        pDir: float = 1
        newZG: bool = False
        doubleZG = phigh and plow
        if array.size(directionArray) > 0:
            pDir = math.sign(array.get(directionArray, 0))
        if (pDir == 1 and phigh or (pDir == -1 and plow)) and matrix.rows(valueMatrix) >= 1:
            pivotbar = array.shift(barArray)
            pivot = matrix.get(valueMatrix, 0, 0)
            pivotdir = array.shift(directionArray)
            ma.shift(valueMatrix)
            value = phigh if pDir == 1 else plow
            useNewValues = value * pivotdir > pivot * pivotdir
            value = value if useNewValues else pivot
            bar = bar_index - offset if useNewValues else pivotbar
            newZG = useNewValues
            addnewpivotplain(valueMatrix, directionArray, barArray, value, bar, pDir, indicatorHigh, indicatorLow, numberOfPivots)
        if pDir == 1 and plow or (pDir == -1 and phigh):
            value = plow if pDir == 1 else phigh
            bar = bar_index - offset
            dir = -1 if pDir == 1 else 1
            newZG = True
            addnewpivotplain(valueMatrix, directionArray, barArray, value, bar, dir, indicatorHigh, indicatorLow, numberOfPivots)
        return (valueMatrix, directionArray, barArray, newZG, doubleZG)

    def draw_zg_line(idx1, idx2, zigzaglines, zigzaglabels, valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, indicatorLabels, lineColor, lineWidth, lineStyle, showLabel, showIndicators):
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
            currentDir = 1 if y1 > y2 else -1
            zlabel: Label = na(Label)
            if showLabel:
                allLabels: list[str] = array.from_items('Price')
                array.concat(allLabels, indicatorLabels)
                lblColor: Color = na(Color)
                allLabelsArray: list[str] = array.new_string()
                for i in pine_range(0, array.size(allLabels) - 1, 1):
                    dir = array.get(lastDirections, i)
                    ratio = array.get(lastRatios, i)
                    __block_result_1__ = (na, na)
                    __switch_3__ = dir
                    if __switch_3__ == 1:
                        __block_result_1__ = ('LH', color.orange)
                    elif __switch_3__ == 2:
                        __block_result_1__ = ('HH', color.green)
                    elif __switch_3__ == -1:
                        __block_result_1__ = ('HL', color.lime)
                    elif __switch_3__ == -2:
                        __block_result_1__ = ('LL', color.red)
                    else:
                        __block_result_1__ = ('NA', color.silver)
                    hhllText, labelColor = __block_result_1__
                    lblColor = labelColor if na(lblColor) else lblColor
                    lbl = array.get(allLabels, i) + ' : ' + string.tostring(array.get(lastValues, i)) + (' - ' + string.tostring(array.get(lastRatios, i)) if i == 0 else '') + ' ( ' + hhllText + ' )'
                    if i != 0:
                        divergence = array.get(lastDivergence, i)
                        doubleDivergence = array.get(lastDoubleDivergence, i)
                        dSymbol, dLabel, dColor = getSentimentDetails(divergence)
                        ddSymbol, ddLabel, ddColor = getSentimentDetails(doubleDivergence)
                        lbl = lbl + ' ' + string.tostring(dSymbol) + ' ' + string.tostring(ddSymbol)
                    array.push(allLabelsArray, lbl)
                finalLabel = array.join(allLabelsArray, '\n') if showIndicators else array.get(allLabelsArray, 0)
                tooltip = '' if showIndicators else array.join(allLabelsArray, '\n')
                labelStyle = label.style_label_down if currentDir > 0 else label.style_label_up
                zlabel = label.new(x=x1, y=y1, yloc=yloc.price, color=lblColor, style=labelStyle, text=finalLabel, textcolor=color.black, size=size.small, tooltip=tooltip)
            if array.size(zigzaglines) > 0:
                lastLine = array.get(zigzaglines, array.size(zigzaglines) - 1)
                if line.get_x2(lastLine) == x2 and line.get_x1(lastLine) <= x1:
                    pa.pop(zigzaglines)
                    pa.pop(zigzaglabels)
            pa.push(zigzaglines, zline, 500)
            __block_result__ = pa.push(zigzaglabels, zlabel, 500)
        return __block_result__

    @export
    def calculate(length: int, ohlc: list[float], indicatorHigh: list[float], indicatorLow: list[float], numberOfPivots: int = 20, supertrendLength: int = 5):
        return zigzagcore(length, ohlc, indicatorHigh, indicatorLow, numberOfPivots, supertrendLength)

    @export
    def calculateplain(length: int, ohlc: list[float], indicatorHigh: list[float], indicatorLow: list[float], numberOfPivots: int = 20, offset: int = 0):
        return zigzagcoreplain(length, ohlc, indicatorHigh, indicatorLow, numberOfPivots, offset)

    @export
    @overload
    def draw(valueMatrix: Matrix[float], directionMatrix: Matrix[int], ratioMatrix: Matrix[float], divergenceMatrix: Matrix[int], doubleDivergenceMatrix: Matrix[int], barArray: list[int], newZG: bool, doubleZG: bool, indicatorLabels: list[str], lineColor: Color = color.blue, lineWidth: int = 1, lineStyle: str = line.style_solid, showLabel: bool = True, showIndicators: bool = True):
        zigzaglines: Persistent[list[Line]] = array.new_line(0)
        zigzaglabels: Persistent[list[Label]] = array.new_label(0)
        if newZG:
            if doubleZG:
                draw_zg_line(2, 3, zigzaglines, zigzaglabels, valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, indicatorLabels, lineColor, lineWidth, lineStyle, showLabel, showIndicators)
            if matrix.rows(valueMatrix) >= 2:
                draw_zg_line(1, 2, zigzaglines, zigzaglabels, valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, indicatorLabels, lineColor, lineWidth, lineStyle, showLabel, showIndicators)
        return (valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, zigzaglines, zigzaglabels)

    @export
    @overload
    def draw(length: int, ohlc: list[float], indicatorLabels: list[str], indicatorHigh: list[float], indicatorLow: list[float], numberOfPivots: int = 20, lineColor: Color = color.blue, lineWidth: int = 1, lineStyle: str = line.style_solid, showLabel: bool = True, showIndicators: bool = True):
        valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, trendArray, supertrendDir, supertrend, newZG, doubleZG = zigzagcore(length, ohlc, indicatorHigh, indicatorLow, numberOfPivots)
        return draw(valueMatrix, directionMatrix, ratioMatrix, divergenceMatrix, doubleDivergenceMatrix, barArray, newZG, doubleZG, indicatorLabels, lineColor, lineWidth, lineStyle, showLabel, showIndicators)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
