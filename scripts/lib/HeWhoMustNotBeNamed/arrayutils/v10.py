"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    array, box, close, label, line, linefill, math, na, nz, order, script,
    ta, table
)
from pynecore.types import Box, Color, Label, Line, LineFill, Persistent, Table
from typing import Protocol, Any


__all__ = ['check_overflow', 'clear', 'delete', 'ema', 'getLabel', 'get_sort_order', 'get_trend_series', 'getrange', 'hma', 'ma', 'pop', 'push', 'rma', 'shift', 'sma', 'unshift', 'wma']


class _ProtocolGetlabel(Protocol):
    def __call__(self, include: list[bool], labels: list[str]) -> Any: ...


class _ProtocolGetSortOrder(Protocol):
    def __call__(self, arr: list[float], order__ren__: int) -> Any: ...


class _ProtocolGetSortOrder2(Protocol):
    def __call__(self, arr: list[int], order__ren__: int) -> Any: ...


class _ProtocolDelete(Protocol):
    def __call__(self, arr: list[Line], index: int) -> Any: ...


class _ProtocolDelete4(Protocol):
    def __call__(self, arr: list[Label], index: int) -> Any: ...


class _ProtocolDelete5(Protocol):
    def __call__(self, arr: list[Box], index: int) -> Any: ...


class _ProtocolDelete6(Protocol):
    def __call__(self, arr: list[Table], index: int) -> Any: ...


class _ProtocolDelete7(Protocol):
    def __call__(self, arr: list[LineFill], index: int) -> Any: ...


class _ProtocolPop(Protocol):
    def __call__(self, arr: list[Line]) -> Any: ...


class _ProtocolPop9(Protocol):
    def __call__(self, arr: list[Label]) -> Any: ...


class _ProtocolPop10(Protocol):
    def __call__(self, arr: list[Box]) -> Any: ...


class _ProtocolPop11(Protocol):
    def __call__(self, arr: list[Table]) -> Any: ...


class _ProtocolPop12(Protocol):
    def __call__(self, arr: list[LineFill]) -> Any: ...


class _ProtocolShift(Protocol):
    def __call__(self, arr: list[Line]) -> Any: ...


class _ProtocolShift14(Protocol):
    def __call__(self, arr: list[Label]) -> Any: ...


class _ProtocolShift15(Protocol):
    def __call__(self, arr: list[Box]) -> Any: ...


class _ProtocolShift16(Protocol):
    def __call__(self, arr: list[Table]) -> Any: ...


class _ProtocolShift17(Protocol):
    def __call__(self, arr: list[LineFill]) -> Any: ...


class _ProtocolUnshift(Protocol):
    def __call__(self, arr: list[int], val: int, maxItems: int) -> Any: ...


class _ProtocolUnshift19(Protocol):
    def __call__(self, arr: list[float], val: float, maxItems: int) -> Any: ...


class _ProtocolUnshift20(Protocol):
    def __call__(self, arr: list[bool], val: bool, maxItems: int) -> Any: ...


class _ProtocolUnshift21(Protocol):
    def __call__(self, arr: list[str], val: str, maxItems: int) -> Any: ...


class _ProtocolUnshift22(Protocol):
    def __call__(self, arr: list[Color], val: Color, maxItems: int) -> Any: ...


class _ProtocolUnshift23(Protocol):
    def __call__(self, arr: list[Line], val: Line, maxItems: int) -> Any: ...


class _ProtocolUnshift24(Protocol):
    def __call__(self, arr: list[Label], val: Label, maxItems: int) -> Any: ...


class _ProtocolUnshift25(Protocol):
    def __call__(self, arr: list[Box], val: Box, maxItems: int) -> Any: ...


class _ProtocolUnshift26(Protocol):
    def __call__(self, arr: list[Table], val: Table, maxItems: int) -> Any: ...


class _ProtocolUnshift27(Protocol):
    def __call__(self, arr: list[LineFill], val: LineFill, maxItems: int) -> Any: ...


class _ProtocolClear(Protocol):
    def __call__(self, arr: list[Line]) -> Any: ...


class _ProtocolClear29(Protocol):
    def __call__(self, arr: list[Label]) -> Any: ...


class _ProtocolClear30(Protocol):
    def __call__(self, arr: list[Box]) -> Any: ...


class _ProtocolClear31(Protocol):
    def __call__(self, arr: list[Table]) -> Any: ...


class _ProtocolClear32(Protocol):
    def __call__(self, arr: list[LineFill]) -> Any: ...


class _ProtocolPush(Protocol):
    def __call__(self, arr: list[int], val: int, maxItems: int) -> Any: ...


class _ProtocolPush34(Protocol):
    def __call__(self, arr: list[float], val: float, maxItems: int) -> Any: ...


class _ProtocolPush35(Protocol):
    def __call__(self, arr: list[bool], val: bool, maxItems: int) -> Any: ...


class _ProtocolPush36(Protocol):
    def __call__(self, arr: list[str], val: str, maxItems: int) -> Any: ...


class _ProtocolPush37(Protocol):
    def __call__(self, arr: list[Color], val: Color, maxItems: int) -> Any: ...


class _ProtocolPush38(Protocol):
    def __call__(self, arr: list[Line], val: Line, maxItems: int) -> Any: ...


class _ProtocolPush39(Protocol):
    def __call__(self, arr: list[Label], val: Label, maxItems: int) -> Any: ...


class _ProtocolPush40(Protocol):
    def __call__(self, arr: list[Box], val: Box, maxItems: int) -> Any: ...


class _ProtocolPush41(Protocol):
    def __call__(self, arr: list[Table], val: Table, maxItems: int) -> Any: ...


class _ProtocolPush42(Protocol):
    def __call__(self, arr: list[LineFill], val: LineFill, maxItems: int) -> Any: ...


class _ProtocolCheckOverflow(Protocol):
    def __call__(self, a: float, b: float, c: float, pivots: list[float], barArray: list[int]) -> Any: ...


class _ProtocolGetTrendSeries(Protocol):
    def __call__(self, pivots: list[float], length: int, highLow: int, trend: int) -> Any: ...


class _ProtocolSma(Protocol):
    def __call__(self, source: list[float]) -> Any: ...


class _ProtocolEma(Protocol):
    def __call__(self, source: list[float], length: int) -> Any: ...


class _ProtocolRma(Protocol):
    def __call__(self, source: list[float], length: int) -> Any: ...


class _ProtocolWma(Protocol):
    def __call__(self, source: list[float], length: int) -> Any: ...


class _ProtocolHma(Protocol):
    def __call__(self, source: list[float], length: int) -> Any: ...


class _ProtocolMa(Protocol):
    def __call__(self, source: list[float], matype: str, length: int) -> Any: ...


class _ProtocolGetrange(Protocol):
    def __call__(self, p1: float, p2: float, min1: float, max1: float, p3: float, p4: float, min2: float, max2: float, pArray: list[bool], startRange: list[float], endRange: list[float], index: int) -> Any: ...


class _ProtocolGetrange52(Protocol):
    def __call__(self, p1: float, p2: float, min1: float, max1: float, p3: float, p4: float, min2: float, max2: float, ep1: float, ep2: float, adjs: float, adje: float, pArray: list[bool], startRange: list[float], endRange: list[float], index: int) -> Any: ...


getLabel: _ProtocolGetlabel = Exported()
get_sort_order: _ProtocolGetSortOrder = Exported()
get_sort_order: _ProtocolGetSortOrder2 = Exported()
delete: _ProtocolDelete = Exported()
delete: _ProtocolDelete4 = Exported()
delete: _ProtocolDelete5 = Exported()
delete: _ProtocolDelete6 = Exported()
delete: _ProtocolDelete7 = Exported()
pop: _ProtocolPop = Exported()
pop: _ProtocolPop9 = Exported()
pop: _ProtocolPop10 = Exported()
pop: _ProtocolPop11 = Exported()
pop: _ProtocolPop12 = Exported()
shift: _ProtocolShift = Exported()
shift: _ProtocolShift14 = Exported()
shift: _ProtocolShift15 = Exported()
shift: _ProtocolShift16 = Exported()
shift: _ProtocolShift17 = Exported()
unshift: _ProtocolUnshift = Exported()
unshift: _ProtocolUnshift19 = Exported()
unshift: _ProtocolUnshift20 = Exported()
unshift: _ProtocolUnshift21 = Exported()
unshift: _ProtocolUnshift22 = Exported()
unshift: _ProtocolUnshift23 = Exported()
unshift: _ProtocolUnshift24 = Exported()
unshift: _ProtocolUnshift25 = Exported()
unshift: _ProtocolUnshift26 = Exported()
unshift: _ProtocolUnshift27 = Exported()
clear: _ProtocolClear = Exported()
clear: _ProtocolClear29 = Exported()
clear: _ProtocolClear30 = Exported()
clear: _ProtocolClear31 = Exported()
clear: _ProtocolClear32 = Exported()
push: _ProtocolPush = Exported()
push: _ProtocolPush34 = Exported()
push: _ProtocolPush35 = Exported()
push: _ProtocolPush36 = Exported()
push: _ProtocolPush37 = Exported()
push: _ProtocolPush38 = Exported()
push: _ProtocolPush39 = Exported()
push: _ProtocolPush40 = Exported()
push: _ProtocolPush41 = Exported()
push: _ProtocolPush42 = Exported()
check_overflow: _ProtocolCheckOverflow = Exported()
get_trend_series: _ProtocolGetTrendSeries = Exported()
sma: _ProtocolSma = Exported()
ema: _ProtocolEma = Exported()
rma: _ProtocolRma = Exported()
wma: _ProtocolWma = Exported()
hma: _ProtocolHma = Exported()
ma: _ProtocolMa = Exported()
getrange: _ProtocolGetrange = Exported()
getrange: _ProtocolGetrange52 = Exported()


@script.library('arrayutils')
def main():
    @export
    def getLabel(include: list[bool], labels: list[str]):
        labelText: str = ''
        for i in pine_range(0, array.size(include) - 1, 1):
            labelText = labelText + (('' if labelText == '' else '\n') + array.get(labels, i) if array.get(include, i) else '')
        return labelText

    def unshift_to_array(arr, val, maxItems):
        array.insert(arr, 0, val)
        if array.size(arr) > maxItems:
            array.pop(arr)
        return arr

    def push_to_array(arr, val, maxItems):
        array.push(arr, val)
        if array.size(arr) > maxItems:
            array.remove(arr, 0)
        return arr

    def sort_order(arr, order__ren__):
        orderArray: list[int] = array.new_int()
        arrBase = array.copy(arr)
        arrCopy = array.copy(arr)
        sortOrder = order.ascending if order__ren__ > 0 else order.descending
        array.sort(arrCopy, sortOrder)
        for elem in arrCopy:
            firstIndex = array.indexof(arrBase, elem)
            array.push(orderArray, firstIndex)
            if firstIndex >= 0:
                array.set(arrBase, firstIndex, na)
        return orderArray

    @export
    @overload
    def get_sort_order(arr: list[float], order__ren__: int):
        return sort_order(arr, order__ren__)

    @export
    @overload
    def get_sort_order(arr: list[int], order__ren__: int):
        return sort_order(arr, order__ren__)

    @export
    @overload
    def delete(arr: list[Line], index: int):
        return line.delete(array.remove(arr, index))

    @export
    @overload
    def delete(arr: list[Label], index: int):
        return label.delete(array.remove(arr, index))

    @export
    @overload
    def delete(arr: list[Box], index: int):
        return box.delete(array.remove(arr, index))

    @export
    @overload
    def delete(arr: list[Table], index: int):
        return table.delete(array.remove(arr, index))

    @export
    @overload
    def delete(arr: list[LineFill], index: int):
        return linefill.delete(array.remove(arr, index))

    @export
    @overload
    def pop(arr: list[Line]):
        return line.delete(array.pop(arr))

    @export
    @overload
    def pop(arr: list[Label]):
        return label.delete(array.pop(arr))

    @export
    @overload
    def pop(arr: list[Box]):
        return box.delete(array.pop(arr))

    @export
    @overload
    def pop(arr: list[Table]):
        return table.delete(array.pop(arr))

    @export
    @overload
    def pop(arr: list[LineFill]):
        return linefill.delete(array.pop(arr))

    def unshift_to_object_array(arr, val, maxItems):
        array.insert(arr, 0, val)
        if array.size(arr) > maxItems:
            pop(arr)
        return arr

    @export
    @overload
    def shift(arr: list[Line]):
        return line.delete(array.shift(arr))

    @export
    @overload
    def shift(arr: list[Label]):
        return label.delete(array.shift(arr))

    @export
    @overload
    def shift(arr: list[Box]):
        return box.delete(array.shift(arr))

    @export
    @overload
    def shift(arr: list[Table]):
        return table.delete(array.shift(arr))

    @export
    @overload
    def shift(arr: list[LineFill]):
        return linefill.delete(array.shift(arr))

    def push_to_object_array(arr, val, maxItems):
        array.push(arr, val)
        if array.size(arr) > maxItems:
            shift(arr)
        return arr

    @export
    @overload
    def unshift(arr: list[int], val: int, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    def unshift(arr: list[float], val: float, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    def unshift(arr: list[bool], val: bool, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    def unshift(arr: list[str], val: str, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    def unshift(arr: list[Color], val: Color, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    def unshift(arr: list[Line], val: Line, maxItems: int):
        return unshift_to_object_array(arr, val, maxItems)

    @export
    @overload
    def unshift(arr: list[Label], val: Label, maxItems: int):
        return unshift_to_object_array(arr, val, maxItems)

    @export
    @overload
    def unshift(arr: list[Box], val: Box, maxItems: int):
        return unshift_to_object_array(arr, val, maxItems)

    @export
    @overload
    def unshift(arr: list[Table], val: Table, maxItems: int):
        return unshift_to_object_array(arr, val, maxItems)

    @export
    @overload
    def unshift(arr: list[LineFill], val: LineFill, maxItems: int):
        return unshift_to_object_array(arr, val, maxItems)

    def clear_array_objects(arr):
        len = array.size(arr) - 1
        __block_result__ = na
        for i in pine_range(0, len if len >= 0 else na, 1):
            __block_result__ = pop(arr)
        return __block_result__

    @export
    @overload
    def clear(arr: list[Line]):
        return clear_array_objects(arr)

    @export
    @overload
    def clear(arr: list[Label]):
        return clear_array_objects(arr)

    @export
    @overload
    def clear(arr: list[Box]):
        return clear_array_objects(arr)

    @export
    @overload
    def clear(arr: list[Table]):
        return clear_array_objects(arr)

    @export
    @overload
    def clear(arr: list[LineFill]):
        return clear_array_objects(arr)

    @export
    @overload
    def push(arr: list[int], val: int, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    def push(arr: list[float], val: float, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    def push(arr: list[bool], val: bool, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    def push(arr: list[str], val: str, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    def push(arr: list[Color], val: Color, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    def push(arr: list[Line], val: Line, maxItems: int):
        return push_to_object_array(arr, val, maxItems)

    @export
    @overload
    def push(arr: list[Label], val: Label, maxItems: int):
        return push_to_object_array(arr, val, maxItems)

    @export
    @overload
    def push(arr: list[Box], val: Box, maxItems: int):
        return push_to_object_array(arr, val, maxItems)

    @export
    @overload
    def push(arr: list[Table], val: Table, maxItems: int):
        return push_to_object_array(arr, val, maxItems)

    @export
    @overload
    def push(arr: list[LineFill], val: LineFill, maxItems: int):
        return push_to_object_array(arr, val, maxItems)

    @export
    def check_overflow(a: float, b: float, c: float, pivots: list[float], barArray: list[int]):
        cBar = array.get(barArray, 0)
        aBar = array.get(barArray, array.size(barArray) - 1)
        ln = line.new(aBar, a, cBar, c)
        overflow: bool = False
        dir = 1 if c > b else -1
        for i in pine_range(1, array.size(barArray) - 2, 1):
            currentBar = array.get(barArray, i)
            peak = array.get(pivots, i)
            linePrice = line.get_price(ln, currentBar)
            if dir * peak > dir * linePrice:
                overflow = True
                break
        line.delete(ln)
        return overflow

    @export
    def get_trend_series(pivots: list[float], length: int, highLow: int, trend: int):
        startLength: int = 1
        endLength = math.min(array.size(pivots), length)
        trendIndexes: list[int] = array.new_int()
        if startLength < endLength:
            first = array.get(pivots, 0)
            sec = array.get(pivots, 1)
            dir = 1 if first > sec else -1
            while startLength + (1 if dir == highLow else 0) < endLength:
                oTrend = trend * highLow
                min = array.slice(pivots, startLength, endLength)
                peak = array.max(min) if highLow == 1 else array.min(min)
                peakIndex = array.indexof(min, peak) if oTrend == 1 else array.lastindexof(min, peak)
                if oTrend == 1:
                    array.insert(trendIndexes, 0, startLength + peakIndex)
                else:
                    array.push(trendIndexes, startLength + peakIndex)
                if startLength + peakIndex == endLength if oTrend == 1 else peakIndex == 0:
                    break
                if oTrend == 1:
                    startLength = startLength + peakIndex + 1 + (1 if dir > 0 else 0)
                else:
                    endLength = peakIndex
        return trendIndexes

    @export
    def sma(source: list[float]):
        return array.avg(source)

    @export
    def ema(source: list[float], length: int):
        ma__000000b0__: Persistent = close
        last = nz(array.get(source, 0))
        k = 2 / (length + 1)
        ma__000000b0__ = last * k + (1 - k) * ma__000000b0__
        return ma__000000b0__

    @export
    def rma(source: list[float], length: int):
        ma__000000b3__: Persistent = close
        last = nz(array.get(source, 0))
        ma__000000b3__ = (ma__000000b3__ * (length - 1) + last) / length
        return ma__000000b3__

    @export
    def wma(source: list[float], length: int):
        masum: float = 0.0
        for i in pine_range(0, length - 1, 1):
            masum = masum + array.get(source, i) * (length - i)
        lenSum = length * (length + 1) / 2
        return masum / lenSum

    @export
    def hma(source: list[float], length: int):
        wma1 = wma(source, length / 2)
        wma2 = wma(source, length)
        hmaRange: Persistent[list[float]] = array.new_float(0)
        push(hmaRange, 2 * wma1 - wma2, length)
        hma__000000c0__: float = na(float)
        if array.size(hmaRange) == length:
            hma__000000c0__ = wma(hmaRange, math.round(math.sqrt(length)))
        return hma__000000c0__

    @export
    def ma(source: list[float], matype: str, length: int):
        ma__000000cd__: Persistent[float] = ta.tr
        if array.size(source) == length:
            if matype == 'sma':
                ma__000000cd__ = sma(source)
            if matype == 'ema':
                ma__000000cd__ = ema(source, length)
            if matype == 'rma':
                ma__000000cd__ = rma(source, length)
            if matype == 'wma':
                ma__000000cd__ = wma(source, length)
            if matype == 'hma':
                ma__000000cd__ = hma(source, length)
        return ma__000000cd__

    def getadj(p1, p2, adj):
        return math.abs(p2 - (p2 - p1) * adj)

    @export
    @overload
    def getrange(p1: float, p2: float, min1: float, max1: float, p3: float, p4: float, min2: float, max2: float, pArray: list[bool], startRange: list[float], endRange: list[float], index: int):
        __block_result_1__ = na
        if array.get(pArray, index):
            start1 = getadj(p1, p2, min1)
            end1 = getadj(p1, p2, max1)
            start2 = getadj(p3, p4, min2)
            end2 = getadj(p3, p4, max2)
            start = math.min(start1, start2) if start1 > end1 else math.max(start1, start2)
            end = math.max(end1, end2) if start1 > end1 else math.min(end1, end2)
            __block_result_2__ = na
            if (start1 - end1) * (start - end) > 0:
                array.set(startRange, index, start)
                __block_result_2__ = array.set(endRange, index, end)
            else:
                __block_result_2__ = array.set(pArray, index, False)
            __block_result_1__ = __block_result_2__
        return __block_result_1__

    @export
    @overload
    def getrange(p1: float, p2: float, min1: float, max1: float, p3: float, p4: float, min2: float, max2: float, ep1: float, ep2: float, adjs: float, adje: float, pArray: list[bool], startRange: list[float], endRange: list[float], index: int):
        __block_result_3__ = na
        if array.get(pArray, index):
            eamin1 = (100 - (ep1 + adjs)) / 100
            eamax1 = (100 + ep1 + adje) / 100
            eamin2 = (100 - (ep2 + adjs)) / 100
            eamax2 = (100 + ep2 + adje) / 100
            start1 = getadj(p1, p2, min1 * eamin1)
            end1 = getadj(p1, p2, max1 * eamax1)
            start2 = getadj(p3, p4, min2 * eamin2)
            end2 = getadj(p3, p4, max2 * eamax2)
            start = math.min(start1, start2) if start1 > end1 else math.max(start1, start2)
            end = math.max(end1, end2) if start1 > end1 else math.min(end1, end2)
            __block_result_4__ = na
            if (start1 - end1) * (start - end) > 0:
                array.set(startRange, index, start)
                __block_result_4__ = array.set(endRange, index, end)
            else:
                __block_result_4__ = array.set(pArray, index, False)
            __block_result_3__ = __block_result_4__
        return __block_result_3__


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
