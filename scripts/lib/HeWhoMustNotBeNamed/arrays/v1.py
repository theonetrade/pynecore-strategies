"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_export import Exported, export
from pynecore.lib import array, box, label, line, linefill, na, script, table
from pynecore.types import Box, Color, Label, Line, LineFill, Table
from typing import Protocol, Any


__all__ = ['clear', 'delete', 'pop', 'push', 'shift', 'unshift']


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


@script.library('arrays')
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


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
