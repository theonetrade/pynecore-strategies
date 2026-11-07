"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    array, bar_index, color, label, line, math, matrix, na, order, runtime,
    script, size, string, ta, time, xloc, yloc
)
from pynecore.types import Color, Label, Line, Matrix, NA, Persistent, Series
from typing import Protocol, Any
import lib.HeWhoMustNotBeNamed._matrix.v5 as ma
import lib.HeWhoMustNotBeNamed.arrays.v1 as pa


__all__ = ['draw', 'drawfresh', 'iZigzag', 'nextlevel', 'zigzag']


class _ProtocolZigzag(Protocol):
    def __call__(self, length: int, ohlc: list[float], numberOfPivots: int = 20, offset: int = 0) -> Any: ...


class _ProtocolIzigzag(Protocol):
    def __call__(self, length: int, h: list[float], l: list[float], numberOfPivots: int = 500) -> Any: ...


class _ProtocolNextlevel(Protocol):
    def __call__(self, zigzagmatrix: Matrix[float], numberOfPivots: int = 20) -> Any: ...


class _ProtocolDraw(Protocol):
    def __call__(self, zigzagmatrix: Matrix[float], flags: list[bool], lineColor: Color = color.blue, lineWidth: int = 1, lineStyle: str = line.style_solid, showLabel: bool = False, xloc__ren__: str = xloc.bar_time) -> Any: ...


class _ProtocolDraw4(Protocol):
    def __call__(self, length: int, ohlc: list[float], numberOfPivots: int = 20, offset: int = 0, lineColor: Color = color.blue, lineWidth: int = 1, lineStyle: str = line.style_solid, showLabel: bool = False, xloc__ren__: str = xloc.bar_time) -> Any: ...


class _ProtocolDrawfresh(Protocol):
    def __call__(self, zigzagmatrix: Matrix[float], zigzaglines: list[Line], zigzaglabels: list[Label], lineColor: Color = color.blue, lineWidth: int = 1, lineStyle: str = line.style_solid, showLabel: bool = False, xloc__ren__: str = xloc.bar_time) -> Any: ...


zigzag: _ProtocolZigzag = Exported()
iZigzag: _ProtocolIzigzag = Exported()
nextlevel: _ProtocolNextlevel = Exported()
draw: _ProtocolDraw = Exported()
draw: _ProtocolDraw4 = Exported()
drawfresh: _ProtocolDrawfresh = Exported()


@script.library('rzigzag', overlay=True)
def main():
    def pivots(ohlc: list[float], length):
        highSource = array.max(ohlc)
        lowSource = array.min(ohlc)
        phighbar: int = ta.highestbars(highSource, length)
        plowbar: int = ta.lowestbars(lowSource, length)
        phigh: float = ta.highest(highSource, length)
        plow: float = ta.lowest(lowSource, length)
        return (phigh, phighbar, plow, plowbar)

    def iPivots(h: list[float], l: list[float], i: int, length: int):
        startIndex = math.max(0, i - length + 1)
        highSource = array.slice(h, startIndex, i + 1)
        lowSource = array.slice(l, startIndex, i + 1)
        highIndex = array.sort_indices(highSource, order.descending)
        lowIndex = array.sort_indices(lowSource, order.ascending)
        pHighIndex: int = array.get(highIndex, 0)
        pLowIndex: int = array.get(lowIndex, 0)
        phigh: float = array.get(highSource, pHighIndex)
        plow: float = array.get(lowSource, pLowIndex)
        return (phigh, startIndex + pHighIndex, plow, startIndex + pLowIndex)

    def addNewIPivot(zigzagmatrix, zigzagpivot, numberOfPivots):
        dir = math.sign(array.get(zigzagpivot, 1))
        if matrix.rows(zigzagmatrix) >= 1:
            lastpivotDir = matrix.get(zigzagmatrix, 0, 1)
            if math.sign(lastpivotDir) == math.sign(dir):
                runtime.error('Direction mismatch')
            if matrix.rows(zigzagmatrix) >= 2:
                value = array.get(zigzagpivot, 0)
                llastValue = matrix.get(zigzagmatrix, 1, 0)
                newDir = dir * 2 if dir * value > dir * llastValue else dir
                array.set(zigzagpivot, 1, newDir)
        return ma.unshift(zigzagmatrix, zigzagpivot, numberOfPivots)

    def addnewpivot(zigzagmatrix, zigzagpivot, numberOfPivots):
        dir = math.sign(array.get(zigzagpivot, 3))
        if matrix.rows(zigzagmatrix) >= 1:
            lastpivotDir = matrix.get(zigzagmatrix, 0, 3)
            if math.sign(lastpivotDir) == math.sign(dir):
                runtime.error('Direction mismatch')
            if matrix.rows(zigzagmatrix) >= 2:
                value = array.get(zigzagpivot, 0)
                llastValue = matrix.get(zigzagmatrix, 1, 0)
                newDir = dir * 2 if dir * value > dir * llastValue else dir
                array.set(zigzagpivot, 3, newDir)
        return ma.unshift(zigzagmatrix, zigzagpivot, numberOfPivots)

    def draw_zg_line(idx1, zigzaglines, zigzaglabels, zigzagmatrix, lineColor, lineWidth, lineStyle, showLabel, xloc__ren__):
        idx2 = idx1 + 1
        __block_result__ = na
        if matrix.rows(zigzagmatrix) > idx2:
            lastValues = matrix.row(zigzagmatrix, idx1)
            llastValues = matrix.row(zigzagmatrix, idx2)
            y1 = array.get(lastValues, 0)
            y2 = array.get(llastValues, 0)
            x1 = array.get(lastValues, 1 if xloc__ren__ == xloc.bar_index else 2)
            x2 = array.get(llastValues, 1 if xloc__ren__ == xloc.bar_index else 2)
            zline = line.new(x1=cast_int(x1), y1=y1, x2=cast_int(x2), y2=y2, xloc=xloc__ren__, color=lineColor, width=lineWidth, style=lineStyle)
            dir = array.get(lastValues, 3)
            zlabel: Label = na(Label)
            if showLabel:
                __block_result_1__ = (na, na)
                __switch_2__ = dir
                if __switch_2__ == 1:
                    __block_result_1__ = ('LH', color.orange)
                elif __switch_2__ == 2:
                    __block_result_1__ = ('HH', color.green)
                elif __switch_2__ == -1:
                    __block_result_1__ = ('HL', color.lime)
                elif __switch_2__ == -2:
                    __block_result_1__ = ('LL', color.red)
                else:
                    __block_result_1__ = ('NA', color.silver)
                hhllText, labelColor = __block_result_1__
                labelStyle = label.style_label_down if dir > 0 else label.style_label_up
                zlabel = label.new(x=cast_int(x1), y=y1, yloc=yloc.price, xloc=xloc__ren__, color=labelColor, style=labelStyle, text=hhllText, textcolor=color.black, size=size.small)
            pa.push(zigzaglines, zline, 500)
            __block_result__ = pa.push(zigzaglabels, zlabel, 500)
        return __block_result__

    @export
    def zigzag(length: int, ohlc: Series[list[float]], numberOfPivots: int = 20, offset: int = 0):
        phigh, phighbar, plow, plowbar = pivots(ohlc if na(ohlc[offset]) else ohlc[offset], length)
        newBar = bar_index - offset
        newBarTime = time[offset]
        forceDoublePivot: bool = False
        distanceFromLastPivot: float = 0.0
        pDir: float = 1
        zigzagmatrix: Persistent[Matrix[float]] = matrix.new(initial_value=NA(float))
        if matrix.rows(zigzagmatrix) > 0:
            pDir = math.sign(matrix.get(zigzagmatrix, 0, 3))
            distanceFromLastPivot = newBar - matrix.get(zigzagmatrix, 0, 1)
        if matrix.rows(zigzagmatrix) > 1:
            llastPrice = matrix.get(zigzagmatrix, 1, 0)
            forceDoublePivot = plow < llastPrice if pDir == 1 and plowbar == 0 else phigh > llastPrice if pDir == -1 and phighbar == 0 else False
        overflow = distanceFromLastPivot >= length
        newPivot: bool = False
        doublePivot: bool = False
        updateLastPivot: bool = False
        if (pDir == 1 and phighbar == 0 or (pDir == -1 and plowbar == 0)) and matrix.rows(zigzagmatrix) >= 1:
            value = phigh if pDir == 1 else plow
            ipivot = plow if pDir == 1 else phigh
            pivot = matrix.get(zigzagmatrix, 0, 0)
            pivotbar = matrix.get(zigzagmatrix, 0, 1)
            pivottime = matrix.get(zigzagmatrix, 0, 2)
            pivotdir = matrix.get(zigzagmatrix, 0, 3)
            removeOld = value * pivotdir > pivot * pivotdir
            if removeOld:
                updateLastPivot = True
                ma.shift(zigzagmatrix)
                addnewpivot(zigzagmatrix, array.from_items(value, newBar, newBarTime, pDir, 0), numberOfPivots)
                newPivot = True
        if pDir == 1 and plowbar == 0 or (pDir == -1 and phighbar == 0 and (not newPivot or forceDoublePivot)):
            value = plow if pDir == 1 else phigh
            addnewpivot(zigzagmatrix, array.from_items(value, newBar, newBarTime, -pDir, 0), numberOfPivots)
            doublePivot = newPivot
            newPivot = True
        if overflow and (not newPivot):
            ipivot = plow if pDir == 1 else phigh
            ipivotbar = newBar + plowbar if pDir == 1 else newBar + phighbar
            ipivottime = time[newBar - ipivotbar + offset]
            addnewpivot(zigzagmatrix, array.from_items(ipivot, ipivotbar, ipivottime, -pDir, 0), numberOfPivots)
            newPivot = True
        return (zigzagmatrix, array.from_items(updateLastPivot, newPivot, doublePivot))

    @export
    def iZigzag(length: int, h: list[float], l: list[float], numberOfPivots: int = 500):
        zigzagmatrix: Matrix[float] = matrix.new(initial_value=NA(float))
        __loop_0__ = pine_loop(0, 1)
        while __loop_0__.step(array.size(h) - 1 if array.size(h) > 0 else na):
            i = __loop_0__.value
            phigh, phighbar, plow, plowbar = iPivots(h, l, i, length)
            pDir: float = 1
            newPivot = phighbar == i or plowbar == i
            doublePivot = phighbar == i and plowbar == i
            updateLastPivot: bool = False
            if matrix.rows(zigzagmatrix) > 0:
                pDir = math.sign(matrix.get(zigzagmatrix, 0, 1))
            if (pDir == 1 and phighbar == i or (pDir == -1 and plowbar == i)) and matrix.rows(zigzagmatrix) >= 1:
                value = phigh if pDir == 1 else plow
                ipivot = plow if pDir == 1 else phigh
                pivot = matrix.get(zigzagmatrix, 0, 0)
                pivotdir = matrix.get(zigzagmatrix, 0, 1)
                removeOld = value * pivotdir > pivot * pivotdir
                addInverse: bool = False
                if removeOld:
                    updateLastPivot = True
                    ma.shift(zigzagmatrix)
                    addNewIPivot(zigzagmatrix, array.from_items(value, pDir, i), numberOfPivots)
                    if matrix.rows(zigzagmatrix) > 1 and doublePivot:
                        llastPivot = matrix.get(zigzagmatrix, 1, 0)
                        if -pDir * llastPivot >= -pDir * ipivot:
                            addInverse = True
                elif not removeOld and (not doublePivot) or addInverse:
                    ipivotbar = plowbar if pDir == 1 else phighbar
                    addNewIPivot(zigzagmatrix, array.from_items(ipivot, -pDir, ipivotbar), numberOfPivots)
                    doublePivot = True
            if pDir == 1 and plowbar == i or (pDir == -1 and phighbar == i):
                value = plow if pDir == 1 else phigh
                addNewIPivot(zigzagmatrix, array.from_items(value, -pDir, i), numberOfPivots)
        return zigzagmatrix

    @export
    def nextlevel(zigzagmatrix: Matrix[float], numberOfPivots: int = 20):
        mlZigzagMatrix: Matrix[float] = matrix.new(initial_value=NA(float))
        if matrix.rows(zigzagmatrix) > 0:
            tempRowBullish: list[float] = array.new_float()
            tempRowBearish: list[float] = array.new_float()
            for i in pine_range(matrix.rows(zigzagmatrix) - 1, 0, 1):
                row = array.copy(matrix.row(zigzagmatrix, i))
                dir = array.get(row, 3)
                newDir = math.sign(dir)
                value = array.get(row, 0)
                array.set(row, 4, array.get(row, 4) + 1)
                if matrix.rows(mlZigzagMatrix) > 0:
                    lastDir = math.sign(matrix.get(mlZigzagMatrix, 0, 3))
                    lastPivot = matrix.get(mlZigzagMatrix, 0, 0)
                    if math.abs(dir) == 2:
                        if lastDir == newDir:
                            if dir * lastPivot < dir * value:
                                ma.shift(mlZigzagMatrix)
                            else:
                                tempRow = tempRowBearish if newDir > 0 else tempRowBullish
                                if array.size(tempRow) > 0:
                                    addnewpivot(mlZigzagMatrix, array.copy(tempRow), numberOfPivots)
                                else:
                                    continue
                        else:
                            tempRowFirst = tempRowBullish if newDir > 0 else tempRowBearish
                            tempRowSecond = tempRowBearish if newDir > 0 else tempRowBullish
                            if array.size(tempRowFirst) > 0 and array.size(tempRowSecond) > 0:
                                tempVal = array.get(tempRowFirst, 0)
                                val = array.get(row, 0)
                                if newDir * tempVal > newDir * val:
                                    addnewpivot(mlZigzagMatrix, array.copy(tempRowFirst), numberOfPivots)
                                    addnewpivot(mlZigzagMatrix, array.copy(tempRowSecond), numberOfPivots)
                        addnewpivot(mlZigzagMatrix, row, numberOfPivots)
                        array.clear(tempRowBearish)
                        array.clear(tempRowBullish)
                    else:
                        tempRow = tempRowBullish if newDir > 0 else tempRowBearish
                        if array.size(tempRow) != 0:
                            tempDir = array.get(tempRow, 3)
                            tempVal = array.get(tempRow, 0)
                            val = array.get(row, 0)
                            if val * dir > tempVal * dir:
                                array.clear(tempRow)
                                array.concat(tempRow, row)
                        else:
                            array.concat(tempRow, row)
                elif math.abs(dir) == 2:
                    addnewpivot(mlZigzagMatrix, row, numberOfPivots)
        if matrix.rows(mlZigzagMatrix) >= matrix.rows(zigzagmatrix):
            ma.clear(mlZigzagMatrix)
        return mlZigzagMatrix

    @export
    @overload
    def draw(zigzagmatrix: Matrix[float], flags: list[bool], lineColor: Color = color.blue, lineWidth: int = 1, lineStyle: str = line.style_solid, showLabel: bool = False, xloc__ren__: str = xloc.bar_time):
        zigzaglines: Persistent[list[Line]] = array.new_line()
        zigzaglabels: Persistent[list[Label]] = array.new_label()
        if array.size(zigzaglines) > 0 and array.get(flags, 0):
            pa.pop(zigzaglines)
            pa.pop(zigzaglabels)
        if array.get(flags, 1):
            if array.get(flags, 2) and matrix.rows(zigzagmatrix) >= 3:
                draw_zg_line(1, zigzaglines, zigzaglabels, zigzagmatrix, lineColor, lineWidth, lineStyle, showLabel, xloc__ren__)
            if matrix.rows(zigzagmatrix) >= 2:
                draw_zg_line(0, zigzaglines, zigzaglabels, zigzagmatrix, lineColor, lineWidth, lineStyle, showLabel, xloc__ren__)
        return (zigzaglines, zigzaglabels)

    @export
    @overload
    def draw(length: int, ohlc: list[float], numberOfPivots: int = 20, offset: int = 0, lineColor: Color = color.blue, lineWidth: int = 1, lineStyle: str = line.style_solid, showLabel: bool = False, xloc__ren__: str = xloc.bar_time):
        zigzagmatrix, flags = zigzag(length, ohlc, numberOfPivots, offset)
        zigzaglines, zigzaglabels = draw(zigzagmatrix, flags, lineColor, lineWidth, lineStyle, showLabel, xloc__ren__)
        return (zigzagmatrix, zigzaglines, zigzaglabels, flags)

    @export
    def drawfresh(zigzagmatrix: Matrix[float], zigzaglines: list[Line], zigzaglabels: list[Label], lineColor: Color = color.blue, lineWidth: int = 1, lineStyle: str = line.style_solid, showLabel: bool = False, xloc__ren__: str = xloc.bar_time):
        rows = matrix.rows(zigzagmatrix)
        for i in pine_range(1, rows - 1 if rows > 1 else na, 1):
            lastValues = matrix.row(zigzagmatrix, i)
            llastValues = matrix.row(zigzagmatrix, i - 1)
            y1 = array.get(lastValues, 0)
            y2 = array.get(llastValues, 0)
            x1 = array.get(lastValues, 2 if xloc__ren__ == xloc.bar_time else 1)
            x2 = array.get(llastValues, 2 if xloc__ren__ == xloc.bar_time else 1)
            level = array.get(lastValues, 4)
            zline = line.new(x1=cast_int(x1), y1=y1, x2=cast_int(x2), y2=y2, xloc=xloc__ren__, color=lineColor, width=lineWidth, style=lineStyle)
            dir = array.get(lastValues, 2)
            zlabel: Label = na(Label)
            if showLabel:
                labelStyle = label.style_label_down if dir > 0 else label.style_label_up
                zlabel = label.new(x=cast_int(x1), y=y1, yloc=yloc.price, color=lineColor, style=labelStyle, text=string.tostring(level), textcolor=color.black, size=size.small, xloc=xloc__ren__)
            pa.push(zigzaglines, zline, 500)
            pa.push(zigzaglabels, zlabel, 500)
        return (zigzaglines, zigzaglabels)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
