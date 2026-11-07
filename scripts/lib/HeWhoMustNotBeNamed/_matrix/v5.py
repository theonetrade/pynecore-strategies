"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.overload import overload
from pynecore.core.pine_export import Exported, export
from pynecore.lib import matrix, na, script
from pynecore.types import Box, Color, Label, Line, LineFill, Matrix, Table
from typing import Protocol, Any
from pynecore.types import Box
from pynecore.types import Matrix
from pynecore.types import Color
from pynecore.types import Matrix
from pynecore.types import Label
from pynecore.types import Matrix
from pynecore.types import Line
from pynecore.types import Matrix
from pynecore.types import LineFill
from pynecore.types import Matrix
from pynecore.types import Table
from pynecore.types import Matrix
import lib.HeWhoMustNotBeNamed.arrays.v1 as pa


__all__ = ['clear', 'delete', 'pop', 'push', 'rclear', 'remove', 'rpop', 'rshift', 'shift', 'unshift']


class _ProtocolDelete(Protocol):
    def __call__(self, mtx: Matrix[Line], rowNumber: int) -> Any: ...


class _ProtocolDelete1(Protocol):
    def __call__(self, mtx: Matrix[Label], rowNumber: int) -> Any: ...


class _ProtocolDelete2(Protocol):
    def __call__(self, mtx: Matrix[Box], rowNumber: int) -> Any: ...


class _ProtocolDelete3(Protocol):
    def __call__(self, mtx: Matrix[LineFill], rowNumber: int) -> Any: ...


class _ProtocolDelete4(Protocol):
    def __call__(self, mtx: Matrix[Table], rowNumber: int) -> Any: ...


class _ProtocolDelete5(Protocol):
    def __call__(self, mtx: Matrix[int], rowNumber: int) -> Any: ...


class _ProtocolDelete6(Protocol):
    def __call__(self, mtx: Matrix[float], rowNumber: int) -> Any: ...


class _ProtocolDelete7(Protocol):
    def __call__(self, mtx: Matrix[bool], rowNumber: int) -> Any: ...


class _ProtocolDelete8(Protocol):
    def __call__(self, mtx: Matrix[str], rowNumber: int) -> Any: ...


class _ProtocolDelete9(Protocol):
    def __call__(self, mtx: Matrix[Color], rowNumber: int) -> Any: ...


class _ProtocolRemove(Protocol):
    def __call__(self, mtx: Matrix[Line], rowNumber: int) -> Any: ...


class _ProtocolRemove11(Protocol):
    def __call__(self, mtx: Matrix[Label], rowNumber: int) -> Any: ...


class _ProtocolRemove12(Protocol):
    def __call__(self, mtx: Matrix[Box], rowNumber: int) -> Any: ...


class _ProtocolRemove13(Protocol):
    def __call__(self, mtx: Matrix[LineFill], rowNumber: int) -> Any: ...


class _ProtocolRemove14(Protocol):
    def __call__(self, mtx: Matrix[Table], rowNumber: int) -> Any: ...


class _ProtocolRemove15(Protocol):
    def __call__(self, mtx: Matrix[int], rowNumber: int) -> Any: ...


class _ProtocolRemove16(Protocol):
    def __call__(self, mtx: Matrix[float], rowNumber: int) -> Any: ...


class _ProtocolRemove17(Protocol):
    def __call__(self, mtx: Matrix[bool], rowNumber: int) -> Any: ...


class _ProtocolRemove18(Protocol):
    def __call__(self, mtx: Matrix[str], rowNumber: int) -> Any: ...


class _ProtocolRemove19(Protocol):
    def __call__(self, mtx: Matrix[Color], rowNumber: int) -> Any: ...


class _ProtocolUnshift(Protocol):
    def __call__(self, mtx: Matrix[Line], row: list[Line], maxItems: int) -> Any: ...


class _ProtocolUnshift21(Protocol):
    def __call__(self, mtx: Matrix[Label], row: list[Label], maxItems: int) -> Any: ...


class _ProtocolUnshift22(Protocol):
    def __call__(self, mtx: Matrix[Box], row: list[Box], maxItems: int) -> Any: ...


class _ProtocolUnshift23(Protocol):
    def __call__(self, mtx: Matrix[LineFill], row: list[LineFill], maxItems: int) -> Any: ...


class _ProtocolUnshift24(Protocol):
    def __call__(self, mtx: Matrix[Table], row: list[Table], maxItems: int) -> Any: ...


class _ProtocolUnshift25(Protocol):
    def __call__(self, mtx: Matrix[int], row: list[int], maxItems: int) -> Any: ...


class _ProtocolUnshift26(Protocol):
    def __call__(self, mtx: Matrix[float], row: list[float], maxItems: int) -> Any: ...


class _ProtocolUnshift27(Protocol):
    def __call__(self, mtx: Matrix[bool], row: list[bool], maxItems: int) -> Any: ...


class _ProtocolUnshift28(Protocol):
    def __call__(self, mtx: Matrix[str], row: list[str], maxItems: int) -> Any: ...


class _ProtocolUnshift29(Protocol):
    def __call__(self, mtx: Matrix[Color], row: list[Color], maxItems: int) -> Any: ...


class _ProtocolPush(Protocol):
    def __call__(self, mtx: Matrix[Line], row: list[Line], maxItems: int) -> Any: ...


class _ProtocolPush31(Protocol):
    def __call__(self, mtx: Matrix[Label], row: list[Label], maxItems: int) -> Any: ...


class _ProtocolPush32(Protocol):
    def __call__(self, mtx: Matrix[Box], row: list[Box], maxItems: int) -> Any: ...


class _ProtocolPush33(Protocol):
    def __call__(self, mtx: Matrix[LineFill], row: list[LineFill], maxItems: int) -> Any: ...


class _ProtocolPush34(Protocol):
    def __call__(self, mtx: Matrix[Table], row: list[Table], maxItems: int) -> Any: ...


class _ProtocolPush35(Protocol):
    def __call__(self, mtx: Matrix[int], row: list[int], maxItems: int) -> Any: ...


class _ProtocolPush36(Protocol):
    def __call__(self, mtx: Matrix[float], row: list[float], maxItems: int) -> Any: ...


class _ProtocolPush37(Protocol):
    def __call__(self, mtx: Matrix[bool], row: list[bool], maxItems: int) -> Any: ...


class _ProtocolPush38(Protocol):
    def __call__(self, mtx: Matrix[str], row: list[str], maxItems: int) -> Any: ...


class _ProtocolPush39(Protocol):
    def __call__(self, mtx: Matrix[Color], row: list[Color], maxItems: int) -> Any: ...


class _ProtocolShift(Protocol):
    def __call__(self, mtx: Matrix[Line]) -> Any: ...


class _ProtocolShift41(Protocol):
    def __call__(self, mtx: Matrix[Label]) -> Any: ...


class _ProtocolShift42(Protocol):
    def __call__(self, mtx: Matrix[Box]) -> Any: ...


class _ProtocolShift43(Protocol):
    def __call__(self, mtx: Matrix[LineFill]) -> Any: ...


class _ProtocolShift44(Protocol):
    def __call__(self, mtx: Matrix[Table]) -> Any: ...


class _ProtocolShift45(Protocol):
    def __call__(self, mtx: Matrix[int]) -> Any: ...


class _ProtocolShift46(Protocol):
    def __call__(self, mtx: Matrix[float]) -> Any: ...


class _ProtocolShift47(Protocol):
    def __call__(self, mtx: Matrix[bool]) -> Any: ...


class _ProtocolShift48(Protocol):
    def __call__(self, mtx: Matrix[str]) -> Any: ...


class _ProtocolShift49(Protocol):
    def __call__(self, mtx: Matrix[Color]) -> Any: ...


class _ProtocolRshift(Protocol):
    def __call__(self, mtx: Matrix[Line]) -> Any: ...


class _ProtocolRshift51(Protocol):
    def __call__(self, mtx: Matrix[Label]) -> Any: ...


class _ProtocolRshift52(Protocol):
    def __call__(self, mtx: Matrix[Box]) -> Any: ...


class _ProtocolRshift53(Protocol):
    def __call__(self, mtx: Matrix[LineFill]) -> Any: ...


class _ProtocolRshift54(Protocol):
    def __call__(self, mtx: Matrix[Table]) -> Any: ...


class _ProtocolRshift55(Protocol):
    def __call__(self, mtx: Matrix[int]) -> Any: ...


class _ProtocolRshift56(Protocol):
    def __call__(self, mtx: Matrix[float]) -> Any: ...


class _ProtocolRshift57(Protocol):
    def __call__(self, mtx: Matrix[bool]) -> Any: ...


class _ProtocolRshift58(Protocol):
    def __call__(self, mtx: Matrix[str]) -> Any: ...


class _ProtocolRshift59(Protocol):
    def __call__(self, mtx: Matrix[Color]) -> Any: ...


class _ProtocolPop(Protocol):
    def __call__(self, mtx: Matrix[Line]) -> Any: ...


class _ProtocolPop61(Protocol):
    def __call__(self, mtx: Matrix[Label]) -> Any: ...


class _ProtocolPop62(Protocol):
    def __call__(self, mtx: Matrix[Box]) -> Any: ...


class _ProtocolPop63(Protocol):
    def __call__(self, mtx: Matrix[LineFill]) -> Any: ...


class _ProtocolPop64(Protocol):
    def __call__(self, mtx: Matrix[Table]) -> Any: ...


class _ProtocolPop65(Protocol):
    def __call__(self, mtx: Matrix[int]) -> Any: ...


class _ProtocolPop66(Protocol):
    def __call__(self, mtx: Matrix[float]) -> Any: ...


class _ProtocolPop67(Protocol):
    def __call__(self, mtx: Matrix[bool]) -> Any: ...


class _ProtocolPop68(Protocol):
    def __call__(self, mtx: Matrix[str]) -> Any: ...


class _ProtocolPop69(Protocol):
    def __call__(self, mtx: Matrix[Color]) -> Any: ...


class _ProtocolRpop(Protocol):
    def __call__(self, mtx: Matrix[Line]) -> Any: ...


class _ProtocolRpop71(Protocol):
    def __call__(self, mtx: Matrix[Label]) -> Any: ...


class _ProtocolRpop72(Protocol):
    def __call__(self, mtx: Matrix[Box]) -> Any: ...


class _ProtocolRpop73(Protocol):
    def __call__(self, mtx: Matrix[LineFill]) -> Any: ...


class _ProtocolRpop74(Protocol):
    def __call__(self, mtx: Matrix[Table]) -> Any: ...


class _ProtocolRpop75(Protocol):
    def __call__(self, mtx: Matrix[int]) -> Any: ...


class _ProtocolRpop76(Protocol):
    def __call__(self, mtx: Matrix[float]) -> Any: ...


class _ProtocolRpop77(Protocol):
    def __call__(self, mtx: Matrix[bool]) -> Any: ...


class _ProtocolRpop78(Protocol):
    def __call__(self, mtx: Matrix[str]) -> Any: ...


class _ProtocolRpop79(Protocol):
    def __call__(self, mtx: Matrix[Color]) -> Any: ...


class _ProtocolClear(Protocol):
    def __call__(self, mtx: Matrix[Line]) -> Any: ...


class _ProtocolClear81(Protocol):
    def __call__(self, mtx: Matrix[Label]) -> Any: ...


class _ProtocolClear82(Protocol):
    def __call__(self, mtx: Matrix[Box]) -> Any: ...


class _ProtocolClear83(Protocol):
    def __call__(self, mtx: Matrix[LineFill]) -> Any: ...


class _ProtocolClear84(Protocol):
    def __call__(self, mtx: Matrix[Table]) -> Any: ...


class _ProtocolClear85(Protocol):
    def __call__(self, mtx: Matrix[int]) -> Any: ...


class _ProtocolClear86(Protocol):
    def __call__(self, mtx: Matrix[float]) -> Any: ...


class _ProtocolClear87(Protocol):
    def __call__(self, mtx: Matrix[bool]) -> Any: ...


class _ProtocolClear88(Protocol):
    def __call__(self, mtx: Matrix[str]) -> Any: ...


class _ProtocolClear89(Protocol):
    def __call__(self, mtx: Matrix[Color]) -> Any: ...


class _ProtocolRclear(Protocol):
    def __call__(self, mtx: Matrix[Line]) -> Any: ...


class _ProtocolRclear91(Protocol):
    def __call__(self, mtx: Matrix[Label]) -> Any: ...


class _ProtocolRclear92(Protocol):
    def __call__(self, mtx: Matrix[Box]) -> Any: ...


class _ProtocolRclear93(Protocol):
    def __call__(self, mtx: Matrix[LineFill]) -> Any: ...


class _ProtocolRclear94(Protocol):
    def __call__(self, mtx: Matrix[Table]) -> Any: ...


class _ProtocolRclear95(Protocol):
    def __call__(self, mtx: Matrix[int]) -> Any: ...


class _ProtocolRclear96(Protocol):
    def __call__(self, mtx: Matrix[float]) -> Any: ...


class _ProtocolRclear97(Protocol):
    def __call__(self, mtx: Matrix[bool]) -> Any: ...


class _ProtocolRclear98(Protocol):
    def __call__(self, mtx: Matrix[str]) -> Any: ...


class _ProtocolRclear99(Protocol):
    def __call__(self, mtx: Matrix[Color]) -> Any: ...


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
remove: _ProtocolRemove = Exported()
remove: _ProtocolRemove11 = Exported()
remove: _ProtocolRemove12 = Exported()
remove: _ProtocolRemove13 = Exported()
remove: _ProtocolRemove14 = Exported()
remove: _ProtocolRemove15 = Exported()
remove: _ProtocolRemove16 = Exported()
remove: _ProtocolRemove17 = Exported()
remove: _ProtocolRemove18 = Exported()
remove: _ProtocolRemove19 = Exported()
unshift: _ProtocolUnshift = Exported()
unshift: _ProtocolUnshift21 = Exported()
unshift: _ProtocolUnshift22 = Exported()
unshift: _ProtocolUnshift23 = Exported()
unshift: _ProtocolUnshift24 = Exported()
unshift: _ProtocolUnshift25 = Exported()
unshift: _ProtocolUnshift26 = Exported()
unshift: _ProtocolUnshift27 = Exported()
unshift: _ProtocolUnshift28 = Exported()
unshift: _ProtocolUnshift29 = Exported()
push: _ProtocolPush = Exported()
push: _ProtocolPush31 = Exported()
push: _ProtocolPush32 = Exported()
push: _ProtocolPush33 = Exported()
push: _ProtocolPush34 = Exported()
push: _ProtocolPush35 = Exported()
push: _ProtocolPush36 = Exported()
push: _ProtocolPush37 = Exported()
push: _ProtocolPush38 = Exported()
push: _ProtocolPush39 = Exported()
shift: _ProtocolShift = Exported()
shift: _ProtocolShift41 = Exported()
shift: _ProtocolShift42 = Exported()
shift: _ProtocolShift43 = Exported()
shift: _ProtocolShift44 = Exported()
shift: _ProtocolShift45 = Exported()
shift: _ProtocolShift46 = Exported()
shift: _ProtocolShift47 = Exported()
shift: _ProtocolShift48 = Exported()
shift: _ProtocolShift49 = Exported()
rshift: _ProtocolRshift = Exported()
rshift: _ProtocolRshift51 = Exported()
rshift: _ProtocolRshift52 = Exported()
rshift: _ProtocolRshift53 = Exported()
rshift: _ProtocolRshift54 = Exported()
rshift: _ProtocolRshift55 = Exported()
rshift: _ProtocolRshift56 = Exported()
rshift: _ProtocolRshift57 = Exported()
rshift: _ProtocolRshift58 = Exported()
rshift: _ProtocolRshift59 = Exported()
pop: _ProtocolPop = Exported()
pop: _ProtocolPop61 = Exported()
pop: _ProtocolPop62 = Exported()
pop: _ProtocolPop63 = Exported()
pop: _ProtocolPop64 = Exported()
pop: _ProtocolPop65 = Exported()
pop: _ProtocolPop66 = Exported()
pop: _ProtocolPop67 = Exported()
pop: _ProtocolPop68 = Exported()
pop: _ProtocolPop69 = Exported()
rpop: _ProtocolRpop = Exported()
rpop: _ProtocolRpop71 = Exported()
rpop: _ProtocolRpop72 = Exported()
rpop: _ProtocolRpop73 = Exported()
rpop: _ProtocolRpop74 = Exported()
rpop: _ProtocolRpop75 = Exported()
rpop: _ProtocolRpop76 = Exported()
rpop: _ProtocolRpop77 = Exported()
rpop: _ProtocolRpop78 = Exported()
rpop: _ProtocolRpop79 = Exported()
clear: _ProtocolClear = Exported()
clear: _ProtocolClear81 = Exported()
clear: _ProtocolClear82 = Exported()
clear: _ProtocolClear83 = Exported()
clear: _ProtocolClear84 = Exported()
clear: _ProtocolClear85 = Exported()
clear: _ProtocolClear86 = Exported()
clear: _ProtocolClear87 = Exported()
clear: _ProtocolClear88 = Exported()
clear: _ProtocolClear89 = Exported()
rclear: _ProtocolRclear = Exported()
rclear: _ProtocolRclear91 = Exported()
rclear: _ProtocolRclear92 = Exported()
rclear: _ProtocolRclear93 = Exported()
rclear: _ProtocolRclear94 = Exported()
rclear: _ProtocolRclear95 = Exported()
rclear: _ProtocolRclear96 = Exported()
rclear: _ProtocolRclear97 = Exported()
rclear: _ProtocolRclear98 = Exported()
rclear: _ProtocolRclear99 = Exported()


@script.library('_matrix')
def main():
    def remove_row_from_matrix(mtx, rowNumber):
        return matrix.remove_row(mtx, rowNumber)

    def delete_row_from_matrix(mtx, rowNumber):
        return pa.clear(remove_row_from_matrix(mtx, rowNumber))

    def unshift_to_matrix(mtx, row, maxItems):
        matrix.add_row(mtx, 0, row)
        if matrix.rows(mtx) > maxItems:
            delete_row_from_matrix(mtx, matrix.rows(mtx) - 1)
        return mtx

    def push_to_matrix(mtx, row, maxItems):
        matrix.add_row(mtx, matrix.rows(mtx), row)
        if matrix.rows(mtx) > maxItems:
            delete_row_from_matrix(mtx, 0)
        return mtx

    @export
    @overload
    def delete(mtx: Matrix[Line], rowNumber: int):
        return delete_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def delete(mtx: Matrix[Label], rowNumber: int):
        return delete_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def delete(mtx: Matrix[Box], rowNumber: int):
        return delete_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def delete(mtx: Matrix[LineFill], rowNumber: int):
        return delete_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def delete(mtx: Matrix[Table], rowNumber: int):
        return delete_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def delete(mtx: Matrix[int], rowNumber: int):
        return delete_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def delete(mtx: Matrix[float], rowNumber: int):
        return delete_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def delete(mtx: Matrix[bool], rowNumber: int):
        return delete_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def delete(mtx: Matrix[str], rowNumber: int):
        return delete_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def delete(mtx: Matrix[Color], rowNumber: int):
        return delete_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def remove(mtx: Matrix[Line], rowNumber: int):
        return remove_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def remove(mtx: Matrix[Label], rowNumber: int):
        return remove_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def remove(mtx: Matrix[Box], rowNumber: int):
        return remove_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def remove(mtx: Matrix[LineFill], rowNumber: int):
        return remove_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def remove(mtx: Matrix[Table], rowNumber: int):
        return remove_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def remove(mtx: Matrix[int], rowNumber: int):
        return remove_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def remove(mtx: Matrix[float], rowNumber: int):
        return remove_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def remove(mtx: Matrix[bool], rowNumber: int):
        return remove_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def remove(mtx: Matrix[str], rowNumber: int):
        return remove_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def remove(mtx: Matrix[Color], rowNumber: int):
        return remove_row_from_matrix(mtx, rowNumber)

    @export
    @overload
    def unshift(mtx: Matrix[Line], row: list[Line], maxItems: int):
        return unshift_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def unshift(mtx: Matrix[Label], row: list[Label], maxItems: int):
        return unshift_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def unshift(mtx: Matrix[Box], row: list[Box], maxItems: int):
        return unshift_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def unshift(mtx: Matrix[LineFill], row: list[LineFill], maxItems: int):
        return unshift_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def unshift(mtx: Matrix[Table], row: list[Table], maxItems: int):
        return unshift_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def unshift(mtx: Matrix[int], row: list[int], maxItems: int):
        return unshift_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def unshift(mtx: Matrix[float], row: list[float], maxItems: int):
        return unshift_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def unshift(mtx: Matrix[bool], row: list[bool], maxItems: int):
        return unshift_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def unshift(mtx: Matrix[str], row: list[str], maxItems: int):
        return unshift_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def unshift(mtx: Matrix[Color], row: list[Color], maxItems: int):
        return unshift_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def push(mtx: Matrix[Line], row: list[Line], maxItems: int):
        return push_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def push(mtx: Matrix[Label], row: list[Label], maxItems: int):
        return push_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def push(mtx: Matrix[Box], row: list[Box], maxItems: int):
        return push_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def push(mtx: Matrix[LineFill], row: list[LineFill], maxItems: int):
        return push_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def push(mtx: Matrix[Table], row: list[Table], maxItems: int):
        return push_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def push(mtx: Matrix[int], row: list[int], maxItems: int):
        return push_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def push(mtx: Matrix[float], row: list[float], maxItems: int):
        return push_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def push(mtx: Matrix[bool], row: list[bool], maxItems: int):
        return push_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def push(mtx: Matrix[str], row: list[str], maxItems: int):
        return push_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def push(mtx: Matrix[Color], row: list[Color], maxItems: int):
        return push_to_matrix(mtx, row, maxItems)

    @export
    @overload
    def shift(mtx: Matrix[Line]):
        return delete(mtx, 0)

    @export
    @overload
    def shift(mtx: Matrix[Label]):
        return delete(mtx, 0)

    @export
    @overload
    def shift(mtx: Matrix[Box]):
        return delete(mtx, 0)

    @export
    @overload
    def shift(mtx: Matrix[LineFill]):
        return delete(mtx, 0)

    @export
    @overload
    def shift(mtx: Matrix[Table]):
        return delete(mtx, 0)

    @export
    @overload
    def shift(mtx: Matrix[int]):
        return delete(mtx, 0)

    @export
    @overload
    def shift(mtx: Matrix[float]):
        return delete(mtx, 0)

    @export
    @overload
    def shift(mtx: Matrix[bool]):
        return delete(mtx, 0)

    @export
    @overload
    def shift(mtx: Matrix[str]):
        return delete(mtx, 0)

    @export
    @overload
    def shift(mtx: Matrix[Color]):
        return delete(mtx, 0)

    @export
    @overload
    def rshift(mtx: Matrix[Line]):
        return remove(mtx, 0)

    @export
    @overload
    def rshift(mtx: Matrix[Label]):
        return remove(mtx, 0)

    @export
    @overload
    def rshift(mtx: Matrix[Box]):
        return remove(mtx, 0)

    @export
    @overload
    def rshift(mtx: Matrix[LineFill]):
        return remove(mtx, 0)

    @export
    @overload
    def rshift(mtx: Matrix[Table]):
        return remove(mtx, 0)

    @export
    @overload
    def rshift(mtx: Matrix[int]):
        return remove(mtx, 0)

    @export
    @overload
    def rshift(mtx: Matrix[float]):
        return remove(mtx, 0)

    @export
    @overload
    def rshift(mtx: Matrix[bool]):
        return remove(mtx, 0)

    @export
    @overload
    def rshift(mtx: Matrix[str]):
        return remove(mtx, 0)

    @export
    @overload
    def rshift(mtx: Matrix[Color]):
        return remove(mtx, 0)

    @export
    @overload
    def pop(mtx: Matrix[Line]):
        return delete(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def pop(mtx: Matrix[Label]):
        return delete(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def pop(mtx: Matrix[Box]):
        return delete(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def pop(mtx: Matrix[LineFill]):
        return delete(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def pop(mtx: Matrix[Table]):
        return delete(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def pop(mtx: Matrix[int]):
        return delete(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def pop(mtx: Matrix[float]):
        return delete(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def pop(mtx: Matrix[bool]):
        return delete(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def pop(mtx: Matrix[str]):
        return delete(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def pop(mtx: Matrix[Color]):
        return delete(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def rpop(mtx: Matrix[Line]):
        return remove(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def rpop(mtx: Matrix[Label]):
        return remove(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def rpop(mtx: Matrix[Box]):
        return remove(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def rpop(mtx: Matrix[LineFill]):
        return remove(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def rpop(mtx: Matrix[Table]):
        return remove(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def rpop(mtx: Matrix[int]):
        return remove(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def rpop(mtx: Matrix[float]):
        return remove(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def rpop(mtx: Matrix[bool]):
        return remove(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def rpop(mtx: Matrix[str]):
        return remove(mtx, matrix.rows(mtx) - 1)

    @export
    @overload
    def rpop(mtx: Matrix[Color]):
        return remove(mtx, matrix.rows(mtx) - 1)

    def clear_matrix(mtx):
        __block_result__ = na
        while matrix.rows(mtx) > 0:
            __block_result__ = delete(mtx, 0)
        return __block_result__

    def rclear_matrix(mtx):
        __block_result_1__ = na
        while matrix.rows(mtx) > 0:
            __block_result_1__ = remove(mtx, 0)
        return __block_result_1__

    @export
    @overload
    def clear(mtx: Matrix[Line]):
        return clear_matrix(mtx)

    @export
    @overload
    def clear(mtx: Matrix[Label]):
        return clear_matrix(mtx)

    @export
    @overload
    def clear(mtx: Matrix[Box]):
        return clear_matrix(mtx)

    @export
    @overload
    def clear(mtx: Matrix[LineFill]):
        return clear_matrix(mtx)

    @export
    @overload
    def clear(mtx: Matrix[Table]):
        return clear_matrix(mtx)

    @export
    @overload
    def clear(mtx: Matrix[int]):
        return clear_matrix(mtx)

    @export
    @overload
    def clear(mtx: Matrix[float]):
        return clear_matrix(mtx)

    @export
    @overload
    def clear(mtx: Matrix[bool]):
        return clear_matrix(mtx)

    @export
    @overload
    def clear(mtx: Matrix[str]):
        return clear_matrix(mtx)

    @export
    @overload
    def clear(mtx: Matrix[Color]):
        return clear_matrix(mtx)

    @export
    @overload
    def rclear(mtx: Matrix[Line]):
        return rclear_matrix(mtx)

    @export
    @overload
    def rclear(mtx: Matrix[Label]):
        return rclear_matrix(mtx)

    @export
    @overload
    def rclear(mtx: Matrix[Box]):
        return rclear_matrix(mtx)

    @export
    @overload
    def rclear(mtx: Matrix[LineFill]):
        return rclear_matrix(mtx)

    @export
    @overload
    def rclear(mtx: Matrix[Table]):
        return rclear_matrix(mtx)

    @export
    @overload
    def rclear(mtx: Matrix[int]):
        return rclear_matrix(mtx)

    @export
    @overload
    def rclear(mtx: Matrix[float]):
        return rclear_matrix(mtx)

    @export
    @overload
    def rclear(mtx: Matrix[bool]):
        return rclear_matrix(mtx)

    @export
    @overload
    def rclear(mtx: Matrix[str]):
        return rclear_matrix(mtx)

    @export
    @overload
    def rclear(mtx: Matrix[Color]):
        return rclear_matrix(mtx)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
