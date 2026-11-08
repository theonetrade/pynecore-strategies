"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.overload import overload
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method, method_call
from pynecore.lib import array, na, script
from pynecore.types import Box, Color, Label, Line, LineFill, Polyline, Table
from pynecore.types.chart import ChartPoint
from typing import Protocol, Any


__all__ = ['delete', 'flush', 'isEmpty', 'isNotEmpty', 'popr', 'push', 'shiftr', 'unshift']


class _ProtocolDelete(Protocol):
    def __call__(self, arr: list[int], index: int) -> Any: ...


class _ProtocolDelete1(Protocol):
    def __call__(self, arr: list[float], index: int) -> Any: ...


class _ProtocolDelete2(Protocol):
    def __call__(self, arr: list[bool], index: int) -> Any: ...


class _ProtocolDelete3(Protocol):
    def __call__(self, arr: list[str], index: int) -> Any: ...


class _ProtocolDelete4(Protocol):
    def __call__(self, arr: list[Color], index: int) -> Any: ...


class _ProtocolDelete5(Protocol):
    def __call__(self, arr: list[ChartPoint], index: int) -> Any: ...


class _ProtocolDelete6(Protocol):
    def __call__(self, arr: list[Line], index: int) -> Any: ...


class _ProtocolDelete7(Protocol):
    def __call__(self, arr: list[Label], index: int) -> Any: ...


class _ProtocolDelete8(Protocol):
    def __call__(self, arr: list[Box], index: int) -> Any: ...


class _ProtocolDelete9(Protocol):
    def __call__(self, arr: list[Table], index: int) -> Any: ...


class _ProtocolDelete10(Protocol):
    def __call__(self, arr: list[LineFill], index: int) -> Any: ...


class _ProtocolDelete11(Protocol):
    def __call__(self, arr: list[Polyline], index: int) -> Any: ...


class _ProtocolPopr(Protocol):
    def __call__(self, arr: list[int]) -> Any: ...


class _ProtocolPopr13(Protocol):
    def __call__(self, arr: list[float]) -> Any: ...


class _ProtocolPopr14(Protocol):
    def __call__(self, arr: list[bool]) -> Any: ...


class _ProtocolPopr15(Protocol):
    def __call__(self, arr: list[str]) -> Any: ...


class _ProtocolPopr16(Protocol):
    def __call__(self, arr: list[Color]) -> Any: ...


class _ProtocolPopr17(Protocol):
    def __call__(self, arr: list[ChartPoint]) -> Any: ...


class _ProtocolPopr18(Protocol):
    def __call__(self, arr: list[Line]) -> Any: ...


class _ProtocolPopr19(Protocol):
    def __call__(self, arr: list[Label]) -> Any: ...


class _ProtocolPopr20(Protocol):
    def __call__(self, arr: list[Box]) -> Any: ...


class _ProtocolPopr21(Protocol):
    def __call__(self, arr: list[Table]) -> Any: ...


class _ProtocolPopr22(Protocol):
    def __call__(self, arr: list[LineFill]) -> Any: ...


class _ProtocolPopr23(Protocol):
    def __call__(self, arr: list[Polyline]) -> Any: ...


class _ProtocolShiftr(Protocol):
    def __call__(self, arr: list[int]) -> Any: ...


class _ProtocolShiftr25(Protocol):
    def __call__(self, arr: list[float]) -> Any: ...


class _ProtocolShiftr26(Protocol):
    def __call__(self, arr: list[bool]) -> Any: ...


class _ProtocolShiftr27(Protocol):
    def __call__(self, arr: list[str]) -> Any: ...


class _ProtocolShiftr28(Protocol):
    def __call__(self, arr: list[Color]) -> Any: ...


class _ProtocolShiftr29(Protocol):
    def __call__(self, arr: list[ChartPoint]) -> Any: ...


class _ProtocolShiftr30(Protocol):
    def __call__(self, arr: list[Line]) -> Any: ...


class _ProtocolShiftr31(Protocol):
    def __call__(self, arr: list[Label]) -> Any: ...


class _ProtocolShiftr32(Protocol):
    def __call__(self, arr: list[Box]) -> Any: ...


class _ProtocolShiftr33(Protocol):
    def __call__(self, arr: list[Table]) -> Any: ...


class _ProtocolShiftr34(Protocol):
    def __call__(self, arr: list[LineFill]) -> Any: ...


class _ProtocolShiftr35(Protocol):
    def __call__(self, arr: list[Polyline]) -> Any: ...


class _ProtocolPush(Protocol):
    def __call__(self, arr: list[int], val: int, maxItems: int) -> Any: ...


class _ProtocolPush37(Protocol):
    def __call__(self, arr: list[float], val: float, maxItems: int) -> Any: ...


class _ProtocolPush38(Protocol):
    def __call__(self, arr: list[bool], val: bool, maxItems: int) -> Any: ...


class _ProtocolPush39(Protocol):
    def __call__(self, arr: list[str], val: str, maxItems: int) -> Any: ...


class _ProtocolPush40(Protocol):
    def __call__(self, arr: list[Color], val: Color, maxItems: int) -> Any: ...


class _ProtocolPush41(Protocol):
    def __call__(self, arr: list[ChartPoint], val: ChartPoint, maxItems: int) -> Any: ...


class _ProtocolPush42(Protocol):
    def __call__(self, arr: list[Line], val: Line, maxItems: int) -> Any: ...


class _ProtocolPush43(Protocol):
    def __call__(self, arr: list[Label], val: Label, maxItems: int) -> Any: ...


class _ProtocolPush44(Protocol):
    def __call__(self, arr: list[Box], val: Box, maxItems: int) -> Any: ...


class _ProtocolPush45(Protocol):
    def __call__(self, arr: list[Table], val: Table, maxItems: int) -> Any: ...


class _ProtocolPush46(Protocol):
    def __call__(self, arr: list[LineFill], val: LineFill, maxItems: int) -> Any: ...


class _ProtocolPush47(Protocol):
    def __call__(self, arr: list[Polyline], val: Polyline, maxItems: int) -> Any: ...


class _ProtocolUnshift(Protocol):
    def __call__(self, arr: list[int], val: int, maxItems: int) -> Any: ...


class _ProtocolUnshift49(Protocol):
    def __call__(self, arr: list[float], val: float, maxItems: int) -> Any: ...


class _ProtocolUnshift50(Protocol):
    def __call__(self, arr: list[bool], val: bool, maxItems: int) -> Any: ...


class _ProtocolUnshift51(Protocol):
    def __call__(self, arr: list[str], val: str, maxItems: int) -> Any: ...


class _ProtocolUnshift52(Protocol):
    def __call__(self, arr: list[Color], val: Color, maxItems: int) -> Any: ...


class _ProtocolUnshift53(Protocol):
    def __call__(self, arr: list[ChartPoint], val: ChartPoint, maxItems: int) -> Any: ...


class _ProtocolUnshift54(Protocol):
    def __call__(self, arr: list[Line], val: Line, maxItems: int) -> Any: ...


class _ProtocolUnshift55(Protocol):
    def __call__(self, arr: list[Label], val: Label, maxItems: int) -> Any: ...


class _ProtocolUnshift56(Protocol):
    def __call__(self, arr: list[Box], val: Box, maxItems: int) -> Any: ...


class _ProtocolUnshift57(Protocol):
    def __call__(self, arr: list[Table], val: Table, maxItems: int) -> Any: ...


class _ProtocolUnshift58(Protocol):
    def __call__(self, arr: list[LineFill], val: LineFill, maxItems: int) -> Any: ...


class _ProtocolUnshift59(Protocol):
    def __call__(self, arr: list[Polyline], val: Polyline, maxItems: int) -> Any: ...


class _ProtocolIsempty(Protocol):
    def __call__(self, arr: list[int]) -> Any: ...


class _ProtocolIsempty61(Protocol):
    def __call__(self, arr: list[float]) -> Any: ...


class _ProtocolIsempty62(Protocol):
    def __call__(self, arr: list[str]) -> Any: ...


class _ProtocolIsempty63(Protocol):
    def __call__(self, arr: list[bool]) -> Any: ...


class _ProtocolIsempty64(Protocol):
    def __call__(self, arr: list[Color]) -> Any: ...


class _ProtocolIsempty65(Protocol):
    def __call__(self, arr: list[ChartPoint]) -> Any: ...


class _ProtocolIsempty66(Protocol):
    def __call__(self, arr: list[Line]) -> Any: ...


class _ProtocolIsempty67(Protocol):
    def __call__(self, arr: list[Label]) -> Any: ...


class _ProtocolIsempty68(Protocol):
    def __call__(self, arr: list[Box]) -> Any: ...


class _ProtocolIsempty69(Protocol):
    def __call__(self, arr: list[LineFill]) -> Any: ...


class _ProtocolIsempty70(Protocol):
    def __call__(self, arr: list[Polyline]) -> Any: ...


class _ProtocolIsempty71(Protocol):
    def __call__(self, arr: list[Table]) -> Any: ...


class _ProtocolIsnotempty(Protocol):
    def __call__(self, arr: list[int]) -> Any: ...


class _ProtocolIsnotempty73(Protocol):
    def __call__(self, arr: list[float]) -> Any: ...


class _ProtocolIsnotempty74(Protocol):
    def __call__(self, arr: list[str]) -> Any: ...


class _ProtocolIsnotempty75(Protocol):
    def __call__(self, arr: list[bool]) -> Any: ...


class _ProtocolIsnotempty76(Protocol):
    def __call__(self, arr: list[Color]) -> Any: ...


class _ProtocolIsnotempty77(Protocol):
    def __call__(self, arr: list[ChartPoint]) -> Any: ...


class _ProtocolIsnotempty78(Protocol):
    def __call__(self, arr: list[Line]) -> Any: ...


class _ProtocolIsnotempty79(Protocol):
    def __call__(self, arr: list[Label]) -> Any: ...


class _ProtocolIsnotempty80(Protocol):
    def __call__(self, arr: list[Box]) -> Any: ...


class _ProtocolIsnotempty81(Protocol):
    def __call__(self, arr: list[LineFill]) -> Any: ...


class _ProtocolIsnotempty82(Protocol):
    def __call__(self, arr: list[Polyline]) -> Any: ...


class _ProtocolIsnotempty83(Protocol):
    def __call__(self, arr: list[Table]) -> Any: ...


class _ProtocolFlush(Protocol):
    def __call__(self, arr: list[int]) -> Any: ...


class _ProtocolFlush85(Protocol):
    def __call__(self, arr: list[float]) -> Any: ...


class _ProtocolFlush86(Protocol):
    def __call__(self, arr: list[bool]) -> Any: ...


class _ProtocolFlush87(Protocol):
    def __call__(self, arr: list[str]) -> Any: ...


class _ProtocolFlush88(Protocol):
    def __call__(self, arr: list[Color]) -> Any: ...


class _ProtocolFlush89(Protocol):
    def __call__(self, arr: list[ChartPoint]) -> Any: ...


class _ProtocolFlush90(Protocol):
    def __call__(self, arr: list[Line]) -> Any: ...


class _ProtocolFlush91(Protocol):
    def __call__(self, arr: list[Label]) -> Any: ...


class _ProtocolFlush92(Protocol):
    def __call__(self, arr: list[Box]) -> Any: ...


class _ProtocolFlush93(Protocol):
    def __call__(self, arr: list[Table]) -> Any: ...


class _ProtocolFlush94(Protocol):
    def __call__(self, arr: list[LineFill]) -> Any: ...


class _ProtocolFlush95(Protocol):
    def __call__(self, arr: list[Polyline]) -> Any: ...


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
delete: _ProtocolDelete10 = Exported()
delete: _ProtocolDelete11 = Exported()
popr: _ProtocolPopr = Exported()
popr: _ProtocolPopr13 = Exported()
popr: _ProtocolPopr14 = Exported()
popr: _ProtocolPopr15 = Exported()
popr: _ProtocolPopr16 = Exported()
popr: _ProtocolPopr17 = Exported()
popr: _ProtocolPopr18 = Exported()
popr: _ProtocolPopr19 = Exported()
popr: _ProtocolPopr20 = Exported()
popr: _ProtocolPopr21 = Exported()
popr: _ProtocolPopr22 = Exported()
popr: _ProtocolPopr23 = Exported()
shiftr: _ProtocolShiftr = Exported()
shiftr: _ProtocolShiftr25 = Exported()
shiftr: _ProtocolShiftr26 = Exported()
shiftr: _ProtocolShiftr27 = Exported()
shiftr: _ProtocolShiftr28 = Exported()
shiftr: _ProtocolShiftr29 = Exported()
shiftr: _ProtocolShiftr30 = Exported()
shiftr: _ProtocolShiftr31 = Exported()
shiftr: _ProtocolShiftr32 = Exported()
shiftr: _ProtocolShiftr33 = Exported()
shiftr: _ProtocolShiftr34 = Exported()
shiftr: _ProtocolShiftr35 = Exported()
push: _ProtocolPush = Exported()
push: _ProtocolPush37 = Exported()
push: _ProtocolPush38 = Exported()
push: _ProtocolPush39 = Exported()
push: _ProtocolPush40 = Exported()
push: _ProtocolPush41 = Exported()
push: _ProtocolPush42 = Exported()
push: _ProtocolPush43 = Exported()
push: _ProtocolPush44 = Exported()
push: _ProtocolPush45 = Exported()
push: _ProtocolPush46 = Exported()
push: _ProtocolPush47 = Exported()
unshift: _ProtocolUnshift = Exported()
unshift: _ProtocolUnshift49 = Exported()
unshift: _ProtocolUnshift50 = Exported()
unshift: _ProtocolUnshift51 = Exported()
unshift: _ProtocolUnshift52 = Exported()
unshift: _ProtocolUnshift53 = Exported()
unshift: _ProtocolUnshift54 = Exported()
unshift: _ProtocolUnshift55 = Exported()
unshift: _ProtocolUnshift56 = Exported()
unshift: _ProtocolUnshift57 = Exported()
unshift: _ProtocolUnshift58 = Exported()
unshift: _ProtocolUnshift59 = Exported()
isEmpty: _ProtocolIsempty = Exported()
isEmpty: _ProtocolIsempty61 = Exported()
isEmpty: _ProtocolIsempty62 = Exported()
isEmpty: _ProtocolIsempty63 = Exported()
isEmpty: _ProtocolIsempty64 = Exported()
isEmpty: _ProtocolIsempty65 = Exported()
isEmpty: _ProtocolIsempty66 = Exported()
isEmpty: _ProtocolIsempty67 = Exported()
isEmpty: _ProtocolIsempty68 = Exported()
isEmpty: _ProtocolIsempty69 = Exported()
isEmpty: _ProtocolIsempty70 = Exported()
isEmpty: _ProtocolIsempty71 = Exported()
isNotEmpty: _ProtocolIsnotempty = Exported()
isNotEmpty: _ProtocolIsnotempty73 = Exported()
isNotEmpty: _ProtocolIsnotempty74 = Exported()
isNotEmpty: _ProtocolIsnotempty75 = Exported()
isNotEmpty: _ProtocolIsnotempty76 = Exported()
isNotEmpty: _ProtocolIsnotempty77 = Exported()
isNotEmpty: _ProtocolIsnotempty78 = Exported()
isNotEmpty: _ProtocolIsnotempty79 = Exported()
isNotEmpty: _ProtocolIsnotempty80 = Exported()
isNotEmpty: _ProtocolIsnotempty81 = Exported()
isNotEmpty: _ProtocolIsnotempty82 = Exported()
isNotEmpty: _ProtocolIsnotempty83 = Exported()
flush: _ProtocolFlush = Exported()
flush: _ProtocolFlush85 = Exported()
flush: _ProtocolFlush86 = Exported()
flush: _ProtocolFlush87 = Exported()
flush: _ProtocolFlush88 = Exported()
flush: _ProtocolFlush89 = Exported()
flush: _ProtocolFlush90 = Exported()
flush: _ProtocolFlush91 = Exported()
flush: _ProtocolFlush92 = Exported()
flush: _ProtocolFlush93 = Exported()
flush: _ProtocolFlush94 = Exported()
flush: _ProtocolFlush95 = Exported()


@script.library('arrays', overlay=True, na_bool=True)
def main():
    @export
    @overload
    @method
    def delete(arr: list[int], index: int):
        return array.remove(arr, index)

    @export
    @overload
    @method
    def delete(arr: list[float], index: int):
        return array.remove(arr, index)

    @export
    @overload
    @method
    def delete(arr: list[bool], index: int):
        return array.remove(arr, index)

    @export
    @overload
    @method
    def delete(arr: list[str], index: int):
        return array.remove(arr, index)

    @export
    @overload
    @method
    def delete(arr: list[Color], index: int):
        return array.remove(arr, index)

    @export
    @overload
    @method
    def delete(arr: list[ChartPoint], index: int):
        return array.remove(arr, index)

    @export
    @overload
    @method
    def delete(arr: list[Line], index: int):
        return delete(array.remove(arr, index))

    @export
    @overload
    @method
    def delete(arr: list[Label], index: int):
        return delete(array.remove(arr, index))

    @export
    @overload
    @method
    def delete(arr: list[Box], index: int):
        return delete(array.remove(arr, index))

    @export
    @overload
    @method
    def delete(arr: list[Table], index: int):
        return delete(array.remove(arr, index))

    @export
    @overload
    @method
    def delete(arr: list[LineFill], index: int):
        return delete(array.remove(arr, index))

    @export
    @overload
    @method
    def delete(arr: list[Polyline], index: int):
        return delete(array.remove(arr, index))

    @export
    @overload
    @method
    def popr(arr: list[int]):
        return array.pop(arr)

    @export
    @overload
    @method
    def popr(arr: list[float]):
        return array.pop(arr)

    @export
    @overload
    @method
    def popr(arr: list[bool]):
        return array.pop(arr)

    @export
    @overload
    @method
    def popr(arr: list[str]):
        return array.pop(arr)

    @export
    @overload
    @method
    def popr(arr: list[Color]):
        return array.pop(arr)

    @export
    @overload
    @method
    def popr(arr: list[ChartPoint]):
        return array.pop(arr)

    @export
    @overload
    @method
    def popr(arr: list[Line]):
        return delete(array.pop(arr))

    @export
    @overload
    @method
    def popr(arr: list[Label]):
        return delete(array.pop(arr))

    @export
    @overload
    @method
    def popr(arr: list[Box]):
        return delete(array.pop(arr))

    @export
    @overload
    @method
    def popr(arr: list[Table]):
        return delete(array.pop(arr))

    @export
    @overload
    @method
    def popr(arr: list[LineFill]):
        return delete(array.pop(arr))

    @export
    @overload
    @method
    def popr(arr: list[Polyline]):
        return delete(array.pop(arr))

    @export
    @overload
    @method
    def shiftr(arr: list[int]):
        return array.shift(arr)

    @export
    @overload
    @method
    def shiftr(arr: list[float]):
        return array.shift(arr)

    @export
    @overload
    @method
    def shiftr(arr: list[bool]):
        return array.shift(arr)

    @export
    @overload
    @method
    def shiftr(arr: list[str]):
        return array.shift(arr)

    @export
    @overload
    @method
    def shiftr(arr: list[Color]):
        return array.shift(arr)

    @export
    @overload
    @method
    def shiftr(arr: list[ChartPoint]):
        return array.shift(arr)

    @export
    @overload
    @method
    def shiftr(arr: list[Line]):
        return delete(array.shift(arr))

    @export
    @overload
    @method
    def shiftr(arr: list[Label]):
        return delete(array.shift(arr))

    @export
    @overload
    @method
    def shiftr(arr: list[Box]):
        return delete(array.shift(arr))

    @export
    @overload
    @method
    def shiftr(arr: list[Table]):
        return delete(array.shift(arr))

    @export
    @overload
    @method
    def shiftr(arr: list[LineFill]):
        return delete(array.shift(arr))

    @export
    @overload
    @method
    def shiftr(arr: list[Polyline]):
        return delete(array.shift(arr))

    def push_to_array(arr, val, maxItems):
        method_call('push', arr, val)
        while method_call('size', arr) > maxItems:
            method_call('shiftr', arr)
        return arr

    def unshift_to_array(arr, val, maxItems):
        method_call('unshift', arr, val)
        while method_call('size', arr) > maxItems:
            method_call('popr', arr)
        return arr

    @export
    @overload
    @method
    def push(arr: list[int], val: int, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def push(arr: list[float], val: float, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def push(arr: list[bool], val: bool, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def push(arr: list[str], val: str, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def push(arr: list[Color], val: Color, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def push(arr: list[ChartPoint], val: ChartPoint, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def push(arr: list[Line], val: Line, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def push(arr: list[Label], val: Label, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def push(arr: list[Box], val: Box, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def push(arr: list[Table], val: Table, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def push(arr: list[LineFill], val: LineFill, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def push(arr: list[Polyline], val: Polyline, maxItems: int):
        return push_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def unshift(arr: list[int], val: int, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def unshift(arr: list[float], val: float, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def unshift(arr: list[bool], val: bool, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def unshift(arr: list[str], val: str, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def unshift(arr: list[Color], val: Color, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def unshift(arr: list[ChartPoint], val: ChartPoint, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def unshift(arr: list[Line], val: Line, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def unshift(arr: list[Label], val: Label, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def unshift(arr: list[Box], val: Box, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def unshift(arr: list[Table], val: Table, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def unshift(arr: list[LineFill], val: LineFill, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    @export
    @overload
    @method
    def unshift(arr: list[Polyline], val: Polyline, maxItems: int):
        return unshift_to_array(arr, val, maxItems)

    def is_empty(arr):
        return na(arr) or method_call('size', arr) == 0

    @export
    @overload
    @method
    def isEmpty(arr: list[int]):
        return is_empty(arr)

    @export
    @overload
    @method
    def isEmpty(arr: list[float]):
        return is_empty(arr)

    @export
    @overload
    @method
    def isEmpty(arr: list[str]):
        return is_empty(arr)

    @export
    @overload
    @method
    def isEmpty(arr: list[bool]):
        return is_empty(arr)

    @export
    @overload
    @method
    def isEmpty(arr: list[Color]):
        return is_empty(arr)

    @export
    @overload
    @method
    def isEmpty(arr: list[ChartPoint]):
        return is_empty(arr)

    @export
    @overload
    @method
    def isEmpty(arr: list[Line]):
        return is_empty(arr)

    @export
    @overload
    @method
    def isEmpty(arr: list[Label]):
        return is_empty(arr)

    @export
    @overload
    @method
    def isEmpty(arr: list[Box]):
        return is_empty(arr)

    @export
    @overload
    @method
    def isEmpty(arr: list[LineFill]):
        return is_empty(arr)

    @export
    @overload
    @method
    def isEmpty(arr: list[Polyline]):
        return is_empty(arr)

    @export
    @overload
    @method
    def isEmpty(arr: list[Table]):
        return is_empty(arr)

    def is_not_empty(arr):
        return not na(arr) and method_call('size', arr) > 0

    @export
    @overload
    @method
    def isNotEmpty(arr: list[int]):
        return is_not_empty(arr)

    @export
    @overload
    @method
    def isNotEmpty(arr: list[float]):
        return is_not_empty(arr)

    @export
    @overload
    @method
    def isNotEmpty(arr: list[str]):
        return is_not_empty(arr)

    @export
    @overload
    @method
    def isNotEmpty(arr: list[bool]):
        return is_not_empty(arr)

    @export
    @overload
    @method
    def isNotEmpty(arr: list[Color]):
        return is_not_empty(arr)

    @export
    @overload
    @method
    def isNotEmpty(arr: list[ChartPoint]):
        return is_not_empty(arr)

    @export
    @overload
    @method
    def isNotEmpty(arr: list[Line]):
        return is_not_empty(arr)

    @export
    @overload
    @method
    def isNotEmpty(arr: list[Label]):
        return is_not_empty(arr)

    @export
    @overload
    @method
    def isNotEmpty(arr: list[Box]):
        return is_not_empty(arr)

    @export
    @overload
    @method
    def isNotEmpty(arr: list[LineFill]):
        return is_not_empty(arr)

    @export
    @overload
    @method
    def isNotEmpty(arr: list[Polyline]):
        return is_not_empty(arr)

    @export
    @overload
    @method
    def isNotEmpty(arr: list[Table]):
        return is_not_empty(arr)

    def clear_array_objects(arr):
        while method_call('isNotEmpty', arr):
            method_call('popr', arr)
        return arr

    def clear(arr):
        method_call('clear', arr)
        return arr

    @export
    @overload
    @method
    def flush(arr: list[int]):
        return clear(arr)

    @export
    @overload
    @method
    def flush(arr: list[float]):
        return clear(arr)

    @export
    @overload
    @method
    def flush(arr: list[bool]):
        return clear(arr)

    @export
    @overload
    @method
    def flush(arr: list[str]):
        return clear(arr)

    @export
    @overload
    @method
    def flush(arr: list[Color]):
        return clear(arr)

    @export
    @overload
    @method
    def flush(arr: list[ChartPoint]):
        return clear(arr)

    @export
    @overload
    @method
    def flush(arr: list[Line]):
        return clear_array_objects(arr)

    @export
    @overload
    @method
    def flush(arr: list[Label]):
        return clear_array_objects(arr)

    @export
    @overload
    @method
    def flush(arr: list[Box]):
        return clear_array_objects(arr)

    @export
    @overload
    @method
    def flush(arr: list[Table]):
        return clear_array_objects(arr)

    @export
    @overload
    @method
    def flush(arr: list[LineFill]):
        return clear_array_objects(arr)

    @export
    @overload
    @method
    def flush(arr: list[Polyline]):
        return clear_array_objects(arr)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
