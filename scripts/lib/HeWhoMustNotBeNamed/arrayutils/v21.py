"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_export import Exported, export
from pynecore.lib import array, box, close, label, line, linefill, math, na, nz, script, ta, table
from pynecore.types import Box, Color, Label, Line, LineFill, Persistent, Table
from typing import Protocol, Any


__all__ = ['check_overflow', 'clear', 'delete', 'ema', 'getFibSeries', 'get_trend_series', 'hma', 'ma', 'pop', 'push', 'rma', 'shift', 'sma', 'unshift', 'wma']


class _ProtocolDelete(Protocol):
    def __call__(self, arr: list[Line], index: int) -> Any: ...


class _ProtocolDelete1(Protocol):
    def __call__(self, arr: list[Label], index: int) -> Any: ...


class _ProtocolDelete2(Protocol):
    def __call__(self, arr: list[Box], index: int) -> Any: ...


class _ProtocolDelete3(Protocol):
    def __call__(self, arr: list[Table], index: int) -> Any: ...


class _ProtocolDelete4(Protocol):
    def __call__(self, arr: list[LineFill], index: int) -> Any: ...


class _ProtocolDelete5(Protocol):
    def __call__(self, arr: list[int], index: int) -> Any: ...


class _ProtocolDelete6(Protocol):
    def __call__(self, arr: list[float], index: int) -> Any: ...


class _ProtocolDelete7(Protocol):
    def __call__(self, arr: list[bool], index: int) -> Any: ...


class _ProtocolDelete8(Protocol):
    def __call__(self, arr: list[str], index: int) -> Any: ...


class _ProtocolDelete9(Protocol):
    def __call__(self, arr: list[Color], index: int) -> Any: ...


class _ProtocolPop(Protocol):
    def __call__(self, arr: list[Line]) -> Any: ...


class _ProtocolPop11(Protocol):
    def __call__(self, arr: list[Label]) -> Any: ...


class _ProtocolPop12(Protocol):
    def __call__(self, arr: list[Box]) -> Any: ...


class _ProtocolPop13(Protocol):
    def __call__(self, arr: list[Table]) -> Any: ...


class _ProtocolPop14(Protocol):
    def __call__(self, arr: list[LineFill]) -> Any: ...


class _ProtocolPop15(Protocol):
    def __call__(self, arr: list[int]) -> Any: ...


class _ProtocolPop16(Protocol):
    def __call__(self, arr: list[float]) -> Any: ...


class _ProtocolPop17(Protocol):
    def __call__(self, arr: list[bool]) -> Any: ...


class _ProtocolPop18(Protocol):
    def __call__(self, arr: list[str]) -> Any: ...


class _ProtocolPop19(Protocol):
    def __call__(self, arr: list[Color]) -> Any: ...


class _ProtocolShift(Protocol):
    def __call__(self, arr: list[Line]) -> Any: ...


class _ProtocolShift21(Protocol):
    def __call__(self, arr: list[Label]) -> Any: ...


class _ProtocolShift22(Protocol):
    def __call__(self, arr: list[Box]) -> Any: ...


class _ProtocolShift23(Protocol):
    def __call__(self, arr: list[Table]) -> Any: ...


class _ProtocolShift24(Protocol):
    def __call__(self, arr: list[LineFill]) -> Any: ...


class _ProtocolShift25(Protocol):
    def __call__(self, arr: list[int]) -> Any: ...


class _ProtocolShift26(Protocol):
    def __call__(self, arr: list[float]) -> Any: ...


class _ProtocolShift27(Protocol):
    def __call__(self, arr: list[bool]) -> Any: ...


class _ProtocolShift28(Protocol):
    def __call__(self, arr: list[str]) -> Any: ...


class _ProtocolShift29(Protocol):
    def __call__(self, arr: list[Color]) -> Any: ...


class _ProtocolUnshift(Protocol):
    def __call__(self, arr: list[int], val: int, maxItems: int) -> Any: ...


class _ProtocolUnshift31(Protocol):
    def __call__(self, arr: list[float], val: float, maxItems: int) -> Any: ...


class _ProtocolUnshift32(Protocol):
    def __call__(self, arr: list[bool], val: bool, maxItems: int) -> Any: ...


class _ProtocolUnshift33(Protocol):
    def __call__(self, arr: list[str], val: str, maxItems: int) -> Any: ...


class _ProtocolUnshift34(Protocol):
    def __call__(self, arr: list[Color], val: Color, maxItems: int) -> Any: ...


class _ProtocolUnshift35(Protocol):
    def __call__(self, arr: list[Line], val: Line, maxItems: int) -> Any: ...


class _ProtocolUnshift36(Protocol):
    def __call__(self, arr: list[Label], val: Label, maxItems: int) -> Any: ...


class _ProtocolUnshift37(Protocol):
    def __call__(self, arr: list[Box], val: Box, maxItems: int) -> Any: ...


class _ProtocolUnshift38(Protocol):
    def __call__(self, arr: list[Table], val: Table, maxItems: int) -> Any: ...


class _ProtocolUnshift39(Protocol):
    def __call__(self, arr: list[LineFill], val: LineFill, maxItems: int) -> Any: ...


class _ProtocolClear(Protocol):
    def __call__(self, arr: list[Line]) -> Any: ...


class _ProtocolClear41(Protocol):
    def __call__(self, arr: list[Label]) -> Any: ...


class _ProtocolClear42(Protocol):
    def __call__(self, arr: list[Box]) -> Any: ...


class _ProtocolClear43(Protocol):
    def __call__(self, arr: list[Table]) -> Any: ...


class _ProtocolClear44(Protocol):
    def __call__(self, arr: list[LineFill]) -> Any: ...


class _ProtocolClear45(Protocol):
    def __call__(self, arr: list[int]) -> Any: ...


class _ProtocolClear46(Protocol):
    def __call__(self, arr: list[float]) -> Any: ...


class _ProtocolClear47(Protocol):
    def __call__(self, arr: list[bool]) -> Any: ...


class _ProtocolClear48(Protocol):
    def __call__(self, arr: list[str]) -> Any: ...


class _ProtocolClear49(Protocol):
    def __call__(self, arr: list[Color]) -> Any: ...


class _ProtocolPush(Protocol):
    def __call__(self, arr: list[int], val: int, maxItems: int) -> Any: ...


class _ProtocolPush51(Protocol):
    def __call__(self, arr: list[float], val: float, maxItems: int) -> Any: ...


class _ProtocolPush52(Protocol):
    def __call__(self, arr: list[bool], val: bool, maxItems: int) -> Any: ...


class _ProtocolPush53(Protocol):
    def __call__(self, arr: list[str], val: str, maxItems: int) -> Any: ...


class _ProtocolPush54(Protocol):
    def __call__(self, arr: list[Color], val: Color, maxItems: int) -> Any: ...


class _ProtocolPush55(Protocol):
    def __call__(self, arr: list[Line], val: Line, maxItems: int) -> Any: ...


class _ProtocolPush56(Protocol):
    def __call__(self, arr: list[Label], val: Label, maxItems: int) -> Any: ...


class _ProtocolPush57(Protocol):
    def __call__(self, arr: list[Box], val: Box, maxItems: int) -> Any: ...


class _ProtocolPush58(Protocol):
    def __call__(self, arr: list[Table], val: Table, maxItems: int) -> Any: ...


class _ProtocolPush59(Protocol):
    def __call__(self, arr: list[LineFill], val: LineFill, maxItems: int) -> Any: ...


class _ProtocolCheckOverflow(Protocol):
    def __call__(self, a: float, b: float, c: float, pivots: list[float], barArray: list[int]) -> Any: ...


class _ProtocolGetTrendSeries(Protocol):
    def __call__(self, pivots: list[float], length: int, highLow: int, trend: int) -> Any: ...


class _ProtocolGetTrendSeries62(Protocol):
    def __call__(self, pivots: list[float], firstIndex: int, lastIndex: int) -> Any: ...


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


class _ProtocolGetfibseries(Protocol):
    def __call__(self, numberOfFibs: int, start: int = 0) -> Any: ...


delete: _ProtocolDelete = Exported()
delete: _ProtocolDelete1 = Exported()
delete: _ProtocolDelete2 = Exported()
delete: _ProtocolDelete3 = Exported()
delete: _ProtocolDelete4 = Exported()
delete: _ProtocolDelete5 = Exported()
delete: _ProtocolDelete6 = Exported()
delete: _ProtocolDelete7 = Exported()
delete: _ProtocolDelete8 = Exported()
delete: _ProtocolDelete9 = Exported()
pop: _ProtocolPop = Exported()
pop: _ProtocolPop11 = Exported()
pop: _ProtocolPop12 = Exported()
pop: _ProtocolPop13 = Exported()
pop: _ProtocolPop14 = Exported()
pop: _ProtocolPop15 = Exported()
pop: _ProtocolPop16 = Exported()
pop: _ProtocolPop17 = Exported()
pop: _ProtocolPop18 = Exported()
pop: _ProtocolPop19 = Exported()
shift: _ProtocolShift = Exported()
shift: _ProtocolShift21 = Exported()
shift: _ProtocolShift22 = Exported()
shift: _ProtocolShift23 = Exported()
shift: _ProtocolShift24 = Exported()
shift: _ProtocolShift25 = Exported()
shift: _ProtocolShift26 = Exported()
shift: _ProtocolShift27 = Exported()
shift: _ProtocolShift28 = Exported()
shift: _ProtocolShift29 = Exported()
unshift: _ProtocolUnshift = Exported()
unshift: _ProtocolUnshift31 = Exported()
unshift: _ProtocolUnshift32 = Exported()
unshift: _ProtocolUnshift33 = Exported()
unshift: _ProtocolUnshift34 = Exported()
unshift: _ProtocolUnshift35 = Exported()
unshift: _ProtocolUnshift36 = Exported()
unshift: _ProtocolUnshift37 = Exported()
unshift: _ProtocolUnshift38 = Exported()
unshift: _ProtocolUnshift39 = Exported()
clear: _ProtocolClear = Exported()
clear: _ProtocolClear41 = Exported()
clear: _ProtocolClear42 = Exported()
clear: _ProtocolClear43 = Exported()
clear: _ProtocolClear44 = Exported()
clear: _ProtocolClear45 = Exported()
clear: _ProtocolClear46 = Exported()
clear: _ProtocolClear47 = Exported()
clear: _ProtocolClear48 = Exported()
clear: _ProtocolClear49 = Exported()
push: _ProtocolPush = Exported()
push: _ProtocolPush51 = Exported()
push: _ProtocolPush52 = Exported()
push: _ProtocolPush53 = Exported()
push: _ProtocolPush54 = Exported()
push: _ProtocolPush55 = Exported()
push: _ProtocolPush56 = Exported()
push: _ProtocolPush57 = Exported()
push: _ProtocolPush58 = Exported()
push: _ProtocolPush59 = Exported()
check_overflow: _ProtocolCheckOverflow = Exported()
get_trend_series: _ProtocolGetTrendSeries = Exported()
get_trend_series: _ProtocolGetTrendSeries62 = Exported()
sma: _ProtocolSma = Exported()
ema: _ProtocolEma = Exported()
rma: _ProtocolRma = Exported()
wma: _ProtocolWma = Exported()
hma: _ProtocolHma = Exported()
ma: _ProtocolMa = Exported()
getFibSeries: _ProtocolGetfibseries = Exported()


@script.library('arrayutils')
def main():
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
    def delete(arr: list[int], index: int):
        return array.remove(arr, index)

    @export
    @overload
    def delete(arr: list[float], index: int):
        return array.remove(arr, index)

    @export
    @overload
    def delete(arr: list[bool], index: int):
        return array.remove(arr, index)

    @export
    @overload
    def delete(arr: list[str], index: int):
        return array.remove(arr, index)

    @export
    @overload
    def delete(arr: list[Color], index: int):
        return array.remove(arr, index)

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

    @export
    @overload
    def pop(arr: list[int]):
        return array.pop(arr)

    @export
    @overload
    def pop(arr: list[float]):
        return array.pop(arr)

    @export
    @overload
    def pop(arr: list[bool]):
        return array.pop(arr)

    @export
    @overload
    def pop(arr: list[str]):
        return array.pop(arr)

    @export
    @overload
    def pop(arr: list[Color]):
        return array.pop(arr)

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

    @export
    @overload
    def shift(arr: list[int]):
        return array.shift(arr)

    @export
    @overload
    def shift(arr: list[float]):
        return array.shift(arr)

    @export
    @overload
    def shift(arr: list[bool]):
        return array.shift(arr)

    @export
    @overload
    def shift(arr: list[str]):
        return array.shift(arr)

    @export
    @overload
    def shift(arr: list[Color]):
        return array.shift(arr)

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
    def clear(arr: list[int]):
        return array.clear(arr)

    @export
    @overload
    def clear(arr: list[float]):
        return array.clear(arr)

    @export
    @overload
    def clear(arr: list[bool]):
        return array.clear(arr)

    @export
    @overload
    def clear(arr: list[str]):
        return array.clear(arr)

    @export
    @overload
    def clear(arr: list[Color]):
        return array.clear(arr)

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
    @overload
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
    @overload
    def get_trend_series(pivots: list[float], firstIndex: int, lastIndex: int):
        startIndex = firstIndex
        endIndex = math.min(array.size(pivots), lastIndex)
        trendIndexes: list[int] = array.new_int()
        if startIndex + 1 < endIndex:
            first = array.get(pivots, startIndex)
            sec = array.get(pivots, startIndex + 1)
            dir = 1 if first > sec else -1
            min = array.slice(pivots, startIndex, endIndex)
            while array.size(min) > 1:
                peak = array.min(min) if dir == 1 else array.max(min)
                peakIndex = array.lastindexof(min, peak)
                min = array.slice(pivots, startIndex, startIndex + peakIndex)
                reversePeak = array.max(min) if dir == 1 else array.min(min)
                if reversePeak == first:
                    array.push(trendIndexes, startIndex + peakIndex)
        return trendIndexes

    @export
    def sma(source: list[float]):
        return array.avg(source)

    @export
    def ema(source: list[float], length: int):
        ma__000000d7__: Persistent = close
        last = nz(array.get(source, 0))
        k = 2 / (length + 1)
        ma__000000d7__ = last * k + (1 - k) * ma__000000d7__
        return ma__000000d7__

    @export
    def rma(source: list[float], length: int):
        ma__000000da__: Persistent = close
        last = nz(array.get(source, 0))
        ma__000000da__ = (ma__000000da__ * (length - 1) + last) / length
        return ma__000000da__

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
        hma__000000e7__: float = na(float)
        if array.size(hmaRange) == length:
            hma__000000e7__ = wma(hmaRange, math.round(math.sqrt(length)))
        return hma__000000e7__

    @export
    def ma(source: list[float], matype: str, length: int):
        ma__000000f5__: Persistent[float] = ta.tr
        if array.size(source) >= length:
            sliced = array.slice(source, 0, length)
            if matype == 'sma':
                ma__000000f5__ = sma(sliced)
            if matype == 'ema':
                ma__000000f5__ = ema(sliced, length)
            if matype == 'rma':
                ma__000000f5__ = rma(sliced, length)
            if matype == 'wma':
                ma__000000f5__ = wma(sliced, length)
            if matype == 'hma':
                ma__000000f5__ = hma(sliced, length)
        return ma__000000f5__

    @export
    def getFibSeries(numberOfFibs: int, start: int = 0):
        fibArray: Persistent[list[int]] = array.new_int()
        if array.size(fibArray) == 0:
            next: int = 1
            prev: int = 1
            while array.size(fibArray) < numberOfFibs:
                fib = next + prev
                prev = next
                next = fib
                if fib >= start:
                    array.push(fibArray, fib)
        return fibArray


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
