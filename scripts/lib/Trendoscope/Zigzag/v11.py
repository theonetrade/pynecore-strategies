"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore import pine_loop, pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt, udt_copy
from pynecore.lib import (
    array, bar_index, barstate, chart, color, high, label, line, low, math,
    matrix, na, order, polyline, runtime, script, size, string, ta, time, xloc, yloc
)
from pynecore.types import Color, Label, Line, Matrix, NA, Persistent, Polyline, Series
from pynecore.types.chart import ChartPoint
from typing import Protocol, Any
import lib.Trendoscope.arrays.v2 as arrays


__all__ = ['Indicator', 'Pivot', 'PivotCandle', 'Zigzag', 'ZigzagDrawing', 'ZigzagDrawingPL', 'ZigzagFlags', 'ZigzagObject', 'ZigzagProperties', 'calculate', 'clear', 'drawcontinuous', 'drawfresh', 'drawplain', 'getBars', 'getPoints', 'getPrices', 'nextlevel', 'tostring']


@udt
class Indicator:
    indicatorHigh: float = na(float)
    indicatorLow: float = na(float)


@udt
class PivotCandle:
    _high: float = _dataclass_field(default_factory=lambda: high)
    _low: float = _dataclass_field(default_factory=lambda: low)
    length: int = 5
    pHighBar: int = na(int)
    pLowBar: int = na(int)
    pHigh: float = na(float)
    pLow: float = na(float)
    indicators: 'list[Indicator]' = na(list)


@udt
class Pivot:
    point: ChartPoint = na(ChartPoint)
    dir: int = na(int)
    level: int = 0
    componentIndex: int = 0
    subComponents: int = 0
    microComponents: int = 1
    ratio: float = 1.0
    sizeRatio: float = 1.0
    barRatio: float = 1.0
    subPivots: 'list[Pivot]' = na(list)
    micropivots: 'list[Pivot]' = na(list)
    indicatorNames: list[str] = na(list)
    indicatorValues: list[float] = na(list)
    indicatorRatios: list[float] = na(list)


@udt
class ZigzagFlags:
    newPivot: bool = False
    doublePivot: bool = False
    updateLastPivot: bool = False


@udt
class Zigzag:
    length: int = 5
    numberOfPivots: int = 20
    offset: int = 0
    level: int = 0
    zigzagPivots: 'list[Pivot]' = na(list)
    flags: 'ZigzagFlags' = _dataclass_field(default_factory=lambda: na(ZigzagFlags))


@udt
class ZigzagObject:
    zigzagLine: Line = na(Line)
    zigzagLabel: Label = na(Label)


@udt
class ZigzagProperties:
    lineColor: Color = _dataclass_field(default_factory=lambda: color.blue)
    lineWidth: int = 1
    lineStyle: str = _dataclass_field(default_factory=lambda: line.style_solid)
    showLabel: bool = False
    showLevels: bool = True
    showSubcomponents: bool = False
    textColor: Color = _dataclass_field(default_factory=lambda: color.black)
    maxObjects: int = 300
    xloc__ren__: str = _dataclass_field(default_factory=lambda: xloc.bar_time)
    curved: bool = False
    force_overlay: bool = False


@udt
class ZigzagDrawing:
    zigzag: 'Zigzag' = _dataclass_field(default_factory=lambda: na(Zigzag))
    properties: 'ZigzagProperties' = _dataclass_field(default_factory=lambda: na(ZigzagProperties))
    drawings: 'list[ZigzagObject]' = na(list)


@udt
class ZigzagDrawingPL:
    zigzag: 'Zigzag' = _dataclass_field(default_factory=lambda: na(Zigzag))
    properties: 'ZigzagProperties' = _dataclass_field(default_factory=lambda: na(ZigzagProperties))
    zigzagLabels: list[Label] = na(list)
    zigzagLine: Polyline = na(Polyline)


class _ProtocolTostring(Protocol):
    def __call__(self, this: Pivot, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na) -> Any: ...


class _ProtocolTostring1(Protocol):
    def __call__(self, this: list[Pivot], sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na) -> Any: ...


class _ProtocolTostring2(Protocol):
    def __call__(self, this: ZigzagFlags) -> Any: ...


class _ProtocolGetprices(Protocol):
    def __call__(self, pivots: list[Pivot]) -> Any: ...


class _ProtocolGetbars(Protocol):
    def __call__(self, pivots: list[Pivot]) -> Any: ...


class _ProtocolGetpoints(Protocol):
    def __call__(self, pivots: list[Pivot]) -> Any: ...


class _ProtocolGetpoints6(Protocol):
    def __call__(self, this: Zigzag) -> Any: ...


class _ProtocolTostring7(Protocol):
    def __call__(self, this: Zigzag, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na) -> Any: ...


class _ProtocolCalculate(Protocol):
    def __call__(self, this: Zigzag, ohlc: list[float], indicators__000000d8__: Matrix[float], indicatorNames: list[str], ltfHighTime: int = time, ltfLowTime: int = time) -> Any: ...


class _ProtocolCalculate9(Protocol):
    def __call__(self, this: Zigzag) -> Any: ...


class _ProtocolNextlevel(Protocol):
    def __call__(self, this: Zigzag) -> Any: ...


class _ProtocolClear(Protocol):
    def __call__(self, this: ZigzagDrawing) -> Any: ...


class _ProtocolClear12(Protocol):
    def __call__(self, this: ZigzagDrawingPL) -> Any: ...


class _ProtocolClear13(Protocol):
    def __call__(self, this: list[ZigzagDrawing]) -> Any: ...


class _ProtocolClear14(Protocol):
    def __call__(self, this: list[ZigzagDrawingPL]) -> Any: ...


class _ProtocolDrawplain(Protocol):
    def __call__(self, this: ZigzagDrawing) -> Any: ...


class _ProtocolDrawplain16(Protocol):
    def __call__(self, this: ZigzagDrawingPL) -> Any: ...


class _ProtocolDrawfresh(Protocol):
    def __call__(self, this: ZigzagDrawing, ohlc: list[float] = na, indicators__000001a0__: Matrix[float] = na, indicatorNames: list[str] = na) -> Any: ...


class _ProtocolDrawcontinuous(Protocol):
    def __call__(self, this: ZigzagDrawing, ohlc: list[float] = na, indicators__000001b3__: Matrix[float] = na, indicatorNames: list[str] = na) -> Any: ...


tostring: _ProtocolTostring = Exported()
tostring: _ProtocolTostring1 = Exported()
tostring: _ProtocolTostring2 = Exported()
getPrices: _ProtocolGetprices = Exported()
getBars: _ProtocolGetbars = Exported()
getPoints: _ProtocolGetpoints = Exported()
getPoints: _ProtocolGetpoints6 = Exported()
tostring: _ProtocolTostring7 = Exported()
calculate: _ProtocolCalculate = Exported()
calculate: _ProtocolCalculate9 = Exported()
nextlevel: _ProtocolNextlevel = Exported()
clear: _ProtocolClear = Exported()
clear: _ProtocolClear12 = Exported()
clear: _ProtocolClear13 = Exported()
clear: _ProtocolClear14 = Exported()
drawplain: _ProtocolDrawplain = Exported()
drawplain: _ProtocolDrawplain16 = Exported()
drawfresh: _ProtocolDrawfresh = Exported()
drawcontinuous: _ProtocolDrawcontinuous = Exported()


@script.library('Zigzag', overlay=True)
def main():
    @overload
    @method
    def init(indicators__00000014__: list[Indicator], indicatorValues: Matrix[float]):
        __loop_0__ = pine_loop(0, 1)
        while __loop_0__.step(na if na(indicatorValues) or matrix.rows(indicatorValues) == 0 else matrix.rows(indicatorValues) - 1):
            i = __loop_0__.value
            iRow = matrix.row(indicatorValues, i)
            indicator: Indicator = Indicator(method_call('first', iRow), method_call('last', iRow))
            array.push(indicators__00000014__, indicator)
        return indicators__00000014__

    @overload
    @method
    def init(candle: PivotCandle, indicators__0000001b__: Matrix[float] = na):
        candle.pHighBar = ta.highestbars(candle._high, candle.length)
        candle.pLowBar = ta.lowestbars(candle._low, candle.length)
        candle.pHigh = ta.highest(candle._high, candle.length)
        candle.pLow = ta.lowest(candle._low, candle.length)
        candle.indicators = array.new(0, NA(Indicator))
        init(candle.indicators, indicators__0000001b__)
        return candle

    @method
    def unshift(arr: list[Pivot], val: Pivot, maxItems: int):
        array.unshift(arr, val)
        __block_result__ = na
        if array.size(arr) > maxItems:
            __block_result__ = array.pop(arr)
        return __block_result__

    @method
    def update(this: Pivot, candle: PivotCandle, indicatorNames: list[str]):
        dir = math.sign(this.dir)
        _indicators: list[float] = array.new_float()
        for indicator in candle.indicators:
            indicatorValue = indicator.indicatorHigh if dir > 0 else indicator.indicatorLow
            array.push(_indicators, indicatorValue)
        this.indicatorNames = indicatorNames
        this.indicatorValues = _indicators
        this.indicatorRatios = array.new_float()
        return this

    @overload
    @method
    def tostring(this: ChartPoint):
        return string.tostring(this.price)

    @overload
    @method
    def get(this: Pivot, key: str):
        return tostring(this.point) if key == 'point' else string.tostring(this.dir) if key == 'dir' else string.tostring(this.level) if key == 'level' else string.tostring(this.componentIndex) if key == 'componentIndex' else string.tostring(this.subComponents) if key == 'subComponents' else string.tostring(this.microComponents) if key == 'microComponents' else string.tostring(this.ratio) if key == 'ratio' else string.tostring(this.sizeRatio) if key == 'sizeRatio' else string.tostring(this.barRatio) if key == 'barRatio' else ('[]' if na(this.indicatorNames) else string.tostring(this.indicatorNames)) if key == 'indicatorNames' else ('[]' if na(this.indicatorValues) else string.tostring(this.indicatorValues)) if key == 'indicatorValues' else ('[]' if na(this.indicatorRatios) else string.tostring(this.indicatorRatios)) if key == 'indicatorRatios' else na

    @export
    @overload
    @method
    def tostring(this: Pivot, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na):
        str__ren__: str = ''
        if not na(this):
            keys = array.from_items('point', 'dir', 'level', 'componentIndex', 'subComponents', 'microComponents', 'ratio', 'sizeRatio', 'barRatio', 'indicatorNames', 'indicatorValues', 'indicatorRatios') if na(includeKeys) else includeKeys
            keyValues: list[str] = array.new_string()
            if sortKeys and (not na(sortOrder)) and (sortOrder != 0):
                method_call('sort', keys, order.ascending if sortOrder > 0 else order.descending)

            for key in keys:
                array.push(keyValues, '"' + key + '":' + '"' + get(this, key) + '"')
            str__ren__ = '{' + array.join(keyValues, ',') + '}'
        return str__ren__

    @export
    @overload
    @method
    def tostring(this: list[Pivot], sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na):
        combinedStr: list[str] = array.new_string()
        if not na(this):
            for pivot in this:
                array.push(combinedStr, tostring(pivot, sortKeys, sortOrder, includeKeys))
        return '[' + array.join(combinedStr, ',') + ']'

    @export
    @overload
    @method
    def tostring(this: ZigzagFlags):
        return string.tostring(array.from_items(this.newPivot, this.doublePivot, this.updateLastPivot))

    @export
    @method
    def getPrices(pivots: list[Pivot]):
        values: list[float] = array.new_float()
        for pivot in pivots:
            array.push(values, pivot.point.price)
        return values

    @export
    @method
    def getBars(pivots: list[Pivot]):
        bars: list[int] = array.new_int()
        for pivot in pivots:
            array.push(bars, pivot.point.index)
        return bars

    @export
    @overload
    @method
    def getPoints(pivots: list[Pivot]):
        points: list[ChartPoint] = array.new(0, NA(ChartPoint))
        for pivot in pivots:
            array.push(points, pivot.point)
        return points

    @export
    @overload
    @method
    def getPoints(this: Zigzag):
        return getPoints(this.zigzagPivots)

    @overload
    @method
    def init(this: Zigzag):
        if na(this.zigzagPivots):
            this.zigzagPivots = array.new(0, NA(Pivot))
            this.flags = ZigzagFlags()
        return this

    @overload
    @method
    def addnewpivot(this: Zigzag, pivot: Pivot, components: list[Pivot] = na):
        dir = math.sign(pivot.dir)
        if array.size(this.zigzagPivots) >= 1:
            lastPivot = array.get(this.zigzagPivots, 0)
            lastValue = lastPivot.point.price
            pivot.subComponents = lastPivot.componentIndex - pivot.componentIndex
            if array.size(components) > lastPivot.componentIndex if not na(components) else False:
                pivot.subPivots = array.slice(components, pivot.componentIndex, lastPivot.componentIndex + 1)
                microComponents: int = 0
                for index, subPivot in enumerate(pivot.subPivots):
                    if index != array.size(pivot.subPivots) - 1:
                        microComponents = microComponents + subPivot.microComponents
                        if na(subPivot.micropivots) or array.size(subPivot.micropivots) == 0:
                            array.push(pivot.micropivots, subPivot)
                        else:
                            array.concat(pivot.micropivots, subPivot.micropivots)
                    elif pivot.level == 1:
                        array.push(pivot.micropivots, subPivot)
                pivot.microComponents = microComponents

            if math.sign(lastPivot.dir) == math.sign(dir):
                runtime.error('Direction mismatch')
            if array.size(this.zigzagPivots) >= 2:
                llastPivot = array.get(this.zigzagPivots, 1)
                value = pivot.point.price
                llastValue = llastPivot.point.price
                newDir = dir * 2 if dir * value > dir * llastValue else dir
                pivot.dir = cast_int(newDir)
                pivot.ratio = math.round(math.abs(lastValue - value) / math.abs(llastValue - lastValue), 3)
                pivot.barRatio = math.round(math.abs(lastPivot.point.index - pivot.point.index) / math.abs(llastPivot.point.index - lastPivot.point.index), 3)

                if array.size(this.zigzagPivots) >= 3:
                    lllastPivot = array.get(this.zigzagPivots, 2)
                    lllastValue = lllastPivot.point.price
                    pivot.sizeRatio = math.round(math.abs(lastValue - value) / math.abs(lllastValue - llastValue), 3)

                llastIndicators = llastPivot.indicatorValues
                indicators__00000090__: list[float] = pivot.indicatorValues
                lastIndicators = lastPivot.indicatorValues
                array.clear(pivot.indicatorRatios)
                for index, indicatorValue in enumerate(indicators__00000090__):
                    lastIndicatorValue = method_call(get, lastIndicators, index)
                    llastIndicatorValue = method_call(get, llastIndicators, index)
                    indicatorRatio = math.round(math.abs(lastIndicatorValue - indicatorValue) / math.abs(llastIndicatorValue - lastIndicatorValue), 3)
                    array.push(pivot.indicatorRatios, indicatorRatio)
        unshift(this.zigzagPivots, pivot, this.numberOfPivots)
        return this

    @overload
    @method
    def addnewpivot(this: Zigzag, pivot: Pivot, candle: PivotCandle, indicatorNames: list[str], components: list[Pivot] = na):
        update(pivot, candle, indicatorNames)
        return addnewpivot(this, pivot, components)

    @overload
    @method
    def get(this: Zigzag, key: str):
        return string.tostring(this.length) if key == 'length' else string.tostring(this.numberOfPivots) if key == 'numberOfPivots' else string.tostring(this.offset) if key == 'offset' else string.tostring(this.level) if key == 'level' else ('[]' if na(this.zigzagPivots) else tostring(this.zigzagPivots)) if key == 'zigzagPivots' else ('[]' if na(this.flags) else tostring(this.flags)) if key == 'flags' else na

    @export
    @overload
    @method
    def tostring(this: Zigzag, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na):
        keys = array.from_items('length', 'numberOfPivots', 'offset', 'level', 'zigzagPivots', 'flags') if na(includeKeys) else includeKeys
        keyValues: list[str] = array.new_string()
        if sortKeys and (not na(sortOrder)) and (sortOrder != 0):
            method_call('sort', keys, order.ascending if sortOrder > 0 else order.descending)

        for key in keys:
            array.push(keyValues, '"' + key + '":' + '"' + get(this, key) + '"')
        return '{' + array.join(keyValues, ',') + '}'

    @export
    @overload
    @method
    def calculate(this: Zigzag, ohlc: Series[list[float]], indicators__000000d8__: Series[Matrix[float]], indicatorNames: list[str], ltfHighTime: Series[int] = time, ltfLowTime: Series[int] = time):
        _ohlc = ohlc if na(ohlc[this.offset]) else ohlc[this.offset]
        _indicators = indicators__000000d8__ if na(indicators__000000d8__[this.offset]) else indicators__000000d8__[this.offset]
        init(this)
        candle: Series[PivotCandle] = PivotCandle(method_call('max', _ohlc), method_call('min', _ohlc), this.length)
        init(candle, _indicators)
        pDir: int = 1
        lastPivot: Pivot = na(Pivot)
        this.flags.updateLastPivot = False
        this.flags.newPivot = False
        this.flags.doublePivot = False
        newBar = bar_index - this.offset
        newbartime = time[this.offset]
        distanceFromLastPivot: int = 0
        counter: Persistent[int] = 0
        lastCounterBar: Persistent[int] = 0
        forceDoublePivot: bool = False

        if array.size(this.zigzagPivots) > 0:
            lastPivot = array.get(this.zigzagPivots, 0)
            pDir = cast_int(math.sign(lastPivot.dir))
            distanceFromLastPivot = newBar - lastPivot.point.index

        if array.size(this.zigzagPivots) > 1:
            llastPivot = array.get(this.zigzagPivots, 1)
            llastDir = cast_int(math.sign(llastPivot.dir))
            forceDoublePivot = candle.pLow < llastPivot.point.price if pDir == 1 and candle.pLowBar == 0 else candle.pHigh > llastPivot.point.price if pDir == -1 and candle.pHighBar == 0 else False

        overflow = distanceFromLastPivot >= this.length

        if (pDir == 1 and candle.pHighBar == 0 or (pDir == -1 and candle.pLowBar == 0)) and array.size(this.zigzagPivots) >= 1:
            value = candle.pHigh if pDir == 1 else candle.pLow
            ipivot = candle.pLow if pDir == 1 else candle.pHigh
            inewbartime = ltfHighTime[this.offset] if pDir == 1 else ltfLowTime[this.offset]
            removeOld = value * lastPivot.dir >= lastPivot.point.price * lastPivot.dir
            if removeOld:
                this.flags.updateLastPivot = True
                this.flags.newPivot = True
                array.shift(this.zigzagPivots)
                newPivotObject: Pivot = Pivot(chart.point.from_index(newBar, value), pDir, micropivots=array.new(0, NA(Pivot)))
                newPivotObject.point.time = inewbartime
                addnewpivot(this, newPivotObject, candle, indicatorNames)

        if pDir == 1 and candle.pLowBar == 0 or (pDir == -1 and candle.pHighBar == 0 and (not this.flags.newPivot or forceDoublePivot)):
            value = candle.pLow if pDir == 1 else candle.pHigh
            inewbartime = ltfLowTime[this.offset] if pDir == 1 else ltfHighTime[this.offset]
            newPivotObject: Pivot = Pivot(chart.point.from_index(newBar, value), -pDir, micropivots=array.new(0, NA(Pivot)))
            newPivotObject.point.time = inewbartime
            addnewpivot(this, newPivotObject, candle, indicatorNames)
            this.flags.doublePivot = this.flags.newPivot
            this.flags.newPivot = True

        if overflow and (not this.flags.newPivot):
            ipivot = candle.pLow if pDir == 1 else candle.pHigh
            ipivotbar = newBar + candle.pLowBar if pDir == 1 else newBar + candle.pHighBar
            ipivottime = ltfLowTime[newBar - ipivotbar + this.offset] if pDir == 1 else ltfHighTime[newBar - ipivotbar + this.offset]
            iCandle = candle[newBar - ipivotbar]
            newPivotObject: Pivot = Pivot(chart.point.from_index(ipivotbar, ipivot), -pDir, micropivots=array.new(0, NA(Pivot)))
            newPivotObject.point.time = ipivottime
            addnewpivot(this, newPivotObject, iCandle, indicatorNames)
            this.flags.newPivot = True
        return this

    @export
    @overload
    @method
    def calculate(this: Zigzag):
        return calculate(this, array.from_items(high, low), matrix.new(initial_value=NA(float)), array.new_string())

    @export
    @method
    def nextlevel(this: Zigzag):
        nextLevel: Zigzag = Zigzag(this.length, this.numberOfPivots, 0)
        nextLevel.level = this.level + 1
        init(nextLevel)
        if array.size(this.zigzagPivots) > 0:
            tempBullishPivot: Pivot = na(Pivot)
            tempBearishPivot: Pivot = na(Pivot)
            for i in pine_range(array.size(this.zigzagPivots) - 1, 0, 1):
                lPivot: Pivot = udt_copy(array.get(this.zigzagPivots, i))
                lPivot.micropivots = array.new(0, NA(Pivot))
                dir: int = lPivot.dir
                newDir = math.sign(dir)
                value = lPivot.point.price
                lPivot.level = lPivot.level + 1
                lPivot.componentIndex = i
                if array.size(nextLevel.zigzagPivots) > 0:
                    lastPivot = array.get(nextLevel.zigzagPivots, 0)
                    lastDir = math.sign(lastPivot.dir)
                    lastValue = lastPivot.point.price
                    if math.abs(dir) == 2:
                        if lastDir == newDir:
                            if dir * lastValue < dir * value:
                                array.shift(nextLevel.zigzagPivots)
                            else:
                                tempPivot = tempBearishPivot if newDir > 0 else tempBullishPivot
                                if not na(tempPivot):
                                    addnewpivot(nextLevel, tempPivot, components=this.zigzagPivots)
                                else:
                                    continue
                        else:
                            tempFirstPivot = tempBullishPivot if newDir > 0 else tempBearishPivot
                            tempSecondPivot = tempBearishPivot if newDir > 0 else tempBullishPivot
                            if not na(tempFirstPivot) and (not na(tempSecondPivot)):
                                tempVal = tempFirstPivot.point.price
                                val = lPivot.point.price
                                if newDir * tempVal > newDir * val:
                                    addnewpivot(nextLevel, tempFirstPivot, components=this.zigzagPivots)
                                    addnewpivot(nextLevel, tempSecondPivot, components=this.zigzagPivots)
                        addnewpivot(nextLevel, lPivot, components=this.zigzagPivots)
                        tempBullishPivot = na
                        tempBearishPivot = na
                    else:
                        tempPivot = tempBullishPivot if newDir > 0 else tempBearishPivot
                        if not na(tempPivot):
                            tempDir = tempPivot.dir
                            tempVal = tempPivot.point.price
                            val = lPivot.point.price
                            if val * dir > tempVal * dir:
                                if newDir > 0:
                                    tempBullishPivot = lPivot
                                else:
                                    tempBearishPivot = lPivot
                        else:
                            if newDir > 0:
                                tempBullishPivot = lPivot
                            else:
                                tempBearishPivot = lPivot
                elif math.abs(dir) == 2:
                    addnewpivot(nextLevel, lPivot, components=this.zigzagPivots)
        if array.size(nextLevel.zigzagPivots) >= array.size(this.zigzagPivots):
            array.clear(nextLevel.zigzagPivots)
        return nextLevel

    @method
    def push(arr: list[ZigzagObject], val, maxItems):
        array.push(arr, val)
        __block_result_1__ = na
        if array.size(arr) > maxItems:
            lastObject: ZigzagObject = array.shift(arr)
            line.delete(lastObject.zigzagLine)
            __block_result_1__ = label.delete(lastObject.zigzagLabel)
        return __block_result_1__

    @method
    def popr(arr: list[ZigzagObject]):
        lastObject: ZigzagObject = array.pop(arr)
        line.delete(lastObject.zigzagLine)
        return label.delete(lastObject.zigzagLabel)

    @overload
    @method
    def init(this: ZigzagDrawing):
        if na(this.drawings):
            this.drawings = array.new(0, NA(ZigzagObject))
        if na(this.zigzag):
            this.zigzag = Zigzag()
            init(this.zigzag)
        if na(this.properties):
            this.properties = ZigzagProperties()
        return this

    @overload
    @method
    def init(this: ZigzagDrawingPL):
        if na(this.zigzagLabels):
            this.zigzagLabels = array.new_label()
        if na(this.zigzag):
            this.zigzag = Zigzag()
            init(this.zigzag)
        if na(this.properties):
            this.properties = ZigzagProperties()
        return this

    @export
    @overload
    @method
    def clear(this: ZigzagDrawing):
        for zigzagObject in this.drawings:
            line.delete(zigzagObject.zigzagLine)
            label.delete(zigzagObject.zigzagLabel)
        array.clear(this.drawings)
        return this

    @export
    @overload
    @method
    def clear(this: ZigzagDrawingPL):
        method_call('flush', this.zigzagLabels)
        polyline.delete(this.zigzagLine)
        return this

    @method
    def draw_zg_line(this: ZigzagDrawing, idx1):
        idx2 = idx1 + 1
        if array.size(this.zigzag.zigzagPivots) > idx2:
            lastPivot: Pivot = array.get(this.zigzag.zigzagPivots, idx1)
            llastPivot: Pivot = array.get(this.zigzag.zigzagPivots, idx2)

            zline = line.new(lastPivot.point, llastPivot.point, xloc=this.properties.xloc__ren__, color=this.properties.lineColor, width=this.properties.lineWidth, style=this.properties.lineStyle, force_overlay=True) if this.properties.force_overlay else line.new(lastPivot.point, llastPivot.point, xloc=this.properties.xloc__ren__, color=this.properties.lineColor, width=this.properties.lineWidth, style=this.properties.lineStyle)

            zlabel: Label = na(Label)
            if this.properties.showLabel:
                __block_result_2__ = (na, na)
                __switch_2__ = lastPivot.dir
                if __switch_2__ == 1:
                    __block_result_2__ = ('LH', color.orange)
                elif __switch_2__ == 2:
                    __block_result_2__ = ('HH', color.green)
                elif __switch_2__ == -1:
                    __block_result_2__ = ('HL', color.lime)
                elif __switch_2__ == -2:
                    __block_result_2__ = ('LL', color.red)
                else:
                    __block_result_2__ = ('NA', color.silver)
                hhllText, labelColor = __block_result_2__

                labelStyle = label.style_label_down if lastPivot.dir > 0 else label.style_label_up
                zlabel = label.new(lastPivot.point, yloc=yloc.price, xloc=this.properties.xloc__ren__, color=labelColor, style=labelStyle, text=hhllText, textcolor=this.properties.textColor, size=size.small, force_overlay=True) if this.properties.force_overlay else label.new(lastPivot.point, yloc=yloc.price, xloc=this.properties.xloc__ren__, color=labelColor, style=labelStyle, text=hhllText, textcolor=this.properties.textColor, size=size.small)

            zigzagObject: ZigzagObject = ZigzagObject(zline, zlabel)
            push(this.drawings, zigzagObject, this.properties.maxObjects)
        return this

    @export
    @overload
    @method
    def clear(this: list[ZigzagDrawing]):
        for drawing in this:
            clear(drawing)
        return clear(this)

    @export
    @overload
    @method
    def clear(this: list[ZigzagDrawingPL]):
        for drawing in this:
            clear(drawing)
        return clear(this)

    @export
    @overload
    @method
    def drawplain(this: ZigzagDrawing):
        init(this)
        clear(this)
        if barstate.islast or barstate.islastconfirmedhistory:
            __loop_1__ = pine_loop(0, 1)
            while __loop_1__.step(array.size(this.zigzag.zigzagPivots) - 2 if array.size(this.zigzag.zigzagPivots) > 1 else na):
                i = __loop_1__.value
                lastPivot = array.get(this.zigzag.zigzagPivots, i)
                llastPivot = array.get(this.zigzag.zigzagPivots, i + 1)

                level = lastPivot.level
                components = llastPivot.componentIndex - lastPivot.componentIndex
                zline = line.new(lastPivot.point, llastPivot.point, xloc=this.properties.xloc__ren__, color=this.properties.lineColor, width=this.properties.lineWidth, style=this.properties.lineStyle, force_overlay=True) if this.properties.force_overlay else line.new(lastPivot.point, llastPivot.point, xloc=this.properties.xloc__ren__, color=this.properties.lineColor, width=this.properties.lineWidth, style=this.properties.lineStyle)
                dir = lastPivot.dir
                zlabel: Label = na(Label)
                if this.properties.showLabel:
                    labelStyle = label.style_label_down if dir > 0 else label.style_label_up
                    _indicators = lastPivot.indicatorValues
                    _indicatorNames = lastPivot.indicatorNames
                    indicatorRatios__0000016d__ = lastPivot.indicatorRatios
                    subPivotValues: list[float] = array.new_float()
                    if not na(lastPivot.subPivots):
                        for subPivot in lastPivot.subPivots:
                            array.push(subPivotValues, subPivot.point.price)

                    labelText = ('(Level ' + string.tostring(level) + ' : ' + string.tostring(lastPivot.ratio) + '/' + string.tostring(lastPivot.barRatio) + ')' if this.properties.showLevels else '') + (('\nSC :' + string.tostring(lastPivot.subComponents) + '/' if lastPivot.subComponents != 0 else '\nMC : ' if level > 0 else '') + (string.tostring(lastPivot.microComponents) if level > 0 else '') + (' (' + array.join(subPivotValues, ',') + ') ' if not na(lastPivot.subPivots) else '') if this.properties.showSubcomponents else '')

                    for index, indicatorName in enumerate(_indicatorNames):
                        indicatorValue = method_call(get, _indicators, index)
                        labelText = labelText + ('' if labelText == '' else '\n') + indicatorName + ' : ' + string.tostring(math.round(indicatorValue, 2)) + ' / ' + string.tostring(method_call(get, indicatorRatios__0000016d__, index))

                    lblColor = color.green if dir == 2 else color.orange if dir == 1 else color.lime if dir == -1 else color.red
                    zlabel = label.new(lastPivot.point, yloc=yloc.price, color=lblColor, style=labelStyle, text=labelText, textcolor=this.properties.textColor, size=size.small, xloc=this.properties.xloc__ren__, force_overlay=True) if this.properties.force_overlay else label.new(lastPivot.point, yloc=yloc.price, color=lblColor, style=labelStyle, text=labelText, textcolor=this.properties.textColor, size=size.small, xloc=this.properties.xloc__ren__)

                array.push(this.drawings, ZigzagObject(zline, zlabel))
        return this

    @export
    @overload
    @method
    def drawplain(this: ZigzagDrawingPL):
        init(this)
        clear(this)
        if barstate.islast or barstate.islastconfirmedhistory:
            this.zigzagLine = polyline.new(getPoints(this.zigzag), this.properties.curved, False, this.properties.xloc__ren__, this.properties.lineColor, line_style=this.properties.lineStyle, line_width=this.properties.lineWidth, force_overlay=True) if this.properties.force_overlay else polyline.new(getPoints(this.zigzag), this.properties.curved, False, this.properties.xloc__ren__, this.properties.lineColor, line_style=this.properties.lineStyle, line_width=this.properties.lineWidth)
            __loop_1__ = pine_loop(0, 1)
            while __loop_1__.step(array.size(this.zigzag.zigzagPivots) - 2 if array.size(this.zigzag.zigzagPivots) > 1 else na):
                i = __loop_1__.value
                lastPivot = array.get(this.zigzag.zigzagPivots, i)
                llastPivot = array.get(this.zigzag.zigzagPivots, i + 1)

                level = lastPivot.level
                components = llastPivot.componentIndex - lastPivot.componentIndex
                dir = lastPivot.dir
                zlabel: Label = na(Label)
                if this.properties.showLabel:
                    labelStyle = label.style_label_down if dir > 0 else label.style_label_up
                    _indicators = lastPivot.indicatorValues
                    _indicatorNames = lastPivot.indicatorNames
                    indicatorRatios__00000191__ = lastPivot.indicatorRatios
                    subPivotValues: list[float] = array.new_float()
                    if not na(lastPivot.subPivots):
                        for subPivot in lastPivot.subPivots:
                            array.push(subPivotValues, subPivot.point.price)

                    labelText = ('(Level ' + string.tostring(level) + ' : ' + string.tostring(lastPivot.ratio) + '/' + string.tostring(lastPivot.barRatio) + ')' if this.properties.showLevels else '') + (('\nSC :' + string.tostring(lastPivot.subComponents) + '/' if lastPivot.subComponents != 0 else '\nMC : ' if level > 0 else '' + (string.tostring(lastPivot.microComponents) if level > 0 else '') + (' (' + array.join(subPivotValues, ',') + ') ' if not na(lastPivot.subPivots) else '')) if this.properties.showSubcomponents else '')

                    for index, indicatorName in enumerate(_indicatorNames):
                        indicatorValue = method_call(get, _indicators, index)
                        labelText = labelText + ('' if labelText == '' else '\n') + indicatorName + ' : ' + string.tostring(math.round(indicatorValue, 2)) + ' / ' + string.tostring(method_call(get, indicatorRatios__00000191__, index))

                    lblColor = color.green if dir == 2 else color.orange if dir == 1 else color.lime if dir == -1 else color.red
                    zlabel = label.new(lastPivot.point, yloc=yloc.price, color=lblColor, style=labelStyle, text=labelText, textcolor=this.properties.textColor, size=size.small, xloc=this.properties.xloc__ren__, force_overlay=True) if this.properties.force_overlay else label.new(lastPivot.point, yloc=yloc.price, color=lblColor, style=labelStyle, text=labelText, textcolor=this.properties.textColor, size=size.small, xloc=this.properties.xloc__ren__)

                array.push(this.zigzagLabels, zlabel)
        return this

    @export
    @method
    def drawfresh(this: ZigzagDrawing, ohlc: list[float] = na, indicators__000001a0__: Matrix[float] = na, indicatorNames: list[str] = na):
        init(this)
        clear(this)
        calculate(this.zigzag, array.from_items(high, low) if na(ohlc) else ohlc, matrix.new(initial_value=NA(float)) if na(indicators__000001a0__) else indicators__000001a0__, array.new_string() if na(indicatorNames) else indicatorNames)
        return drawplain(this)

    @export
    @method
    def drawcontinuous(this: ZigzagDrawing, ohlc: list[float] = na, indicators__000001b3__: Matrix[float] = na, indicatorNames: list[str] = na):
        init(this)
        calculate(this.zigzag, array.from_items(high, low) if na(ohlc) else ohlc, matrix.new(initial_value=NA(float)) if na(indicators__000001b3__) else indicators__000001b3__, array.new_string() if na(indicatorNames) else indicatorNames)
        if array.size(this.drawings) > 0 and this.zigzag.flags.updateLastPivot:
            popr(this.drawings)

        if this.zigzag.flags.newPivot:
            if this.zigzag.flags.doublePivot and array.size(this.zigzag.zigzagPivots) >= 3:
                draw_zg_line(this, 1)

            if array.size(this.zigzag.zigzagPivots) >= 2:
                draw_zg_line(this, 0)
        return this


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
