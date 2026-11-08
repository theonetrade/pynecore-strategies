"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.overload import overload
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import array, map, na, script
from pynecore.types import Box, Color, Label, Line, LineFill, Table
from typing import Protocol, Any


__all__ = ['Fluent', 'append', 'get', 'init', 'prepend', 'set']


@udt
class Fluent:
    msi: dict[str, int] = na(dict)
    msf: dict[str, float] = na(dict)
    msb: dict[str, bool] = na(dict)
    mss: dict[str, str] = na(dict)
    msc: dict[str, Color] = na(dict)
    aii: list[int] = na(list)
    aif: list[float] = na(list)
    aib: list[bool] = na(list)
    ais: list[str] = na(list)
    aic: list[Color] = na(list)
    aibx: list[Box] = na(list)
    ail: list[Line] = na(list)
    ailb: list[Label] = na(list)
    ait: list[Table] = na(list)
    ailf: list[LineFill] = na(list)


class _ProtocolInit(Protocol):
    def __call__(self, this: Fluent, msi__00000030__: dict[str, int] = na, msf__00000030__: dict[str, float] = na, msb__00000030__: dict[str, bool] = na, mss__00000030__: dict[str, str] = na, msc__00000030__: dict[str, Color] = na, aii__00000030__: list[int] = na, aif__00000030__: list[float] = na, aib__00000030__: list[bool] = na, ais__00000030__: list[str] = na, aic__00000030__: list[Color] = na, aibx__00000030__: list[Box] = na, ail__00000030__: list[Line] = na, ailb__00000030__: list[Label] = na, ait__00000030__: list[Table] = na, ailf__00000030__: list[LineFill] = na) -> Any: ...


class _ProtocolGet(Protocol):
    def __call__(self, this: Fluent, key: str, default: int) -> Any: ...


class _ProtocolGet2(Protocol):
    def __call__(self, this: Fluent, key: str, default: float) -> Any: ...


class _ProtocolGet3(Protocol):
    def __call__(self, this: Fluent, key: str, default: bool) -> Any: ...


class _ProtocolGet4(Protocol):
    def __call__(self, this: Fluent, key: str, default: str) -> Any: ...


class _ProtocolGet5(Protocol):
    def __call__(self, this: Fluent, key: str, default: Color) -> Any: ...


class _ProtocolGet6(Protocol):
    def __call__(self, this: Fluent, key: int, default: int) -> Any: ...


class _ProtocolGet7(Protocol):
    def __call__(self, this: Fluent, key: int, default: float) -> Any: ...


class _ProtocolGet8(Protocol):
    def __call__(self, this: Fluent, key: int, default: bool) -> Any: ...


class _ProtocolGet9(Protocol):
    def __call__(self, this: Fluent, key: int, default: str) -> Any: ...


class _ProtocolGet10(Protocol):
    def __call__(self, this: Fluent, key: int, default: Color) -> Any: ...


class _ProtocolGet11(Protocol):
    def __call__(self, this: Fluent, key: int, default: Box) -> Any: ...


class _ProtocolGet12(Protocol):
    def __call__(self, this: Fluent, key: int, default: Line) -> Any: ...


class _ProtocolGet13(Protocol):
    def __call__(self, this: Fluent, key: int, default: Label) -> Any: ...


class _ProtocolGet14(Protocol):
    def __call__(self, this: Fluent, key: int, default: Table) -> Any: ...


class _ProtocolGet15(Protocol):
    def __call__(self, this: Fluent, key: int, default: LineFill) -> Any: ...


class _ProtocolSet(Protocol):
    def __call__(self, this: Fluent, key: str, value: int) -> Any: ...


class _ProtocolSet17(Protocol):
    def __call__(self, this: Fluent, key: str, value: float) -> Any: ...


class _ProtocolSet18(Protocol):
    def __call__(self, this: Fluent, key: str, value: bool) -> Any: ...


class _ProtocolSet19(Protocol):
    def __call__(self, this: Fluent, key: str, value: str) -> Any: ...


class _ProtocolSet20(Protocol):
    def __call__(self, this: Fluent, key: str, value: Color) -> Any: ...


class _ProtocolSet21(Protocol):
    def __call__(self, this: Fluent, key: int, value: int) -> Any: ...


class _ProtocolSet22(Protocol):
    def __call__(self, this: Fluent, key: int, value: float) -> Any: ...


class _ProtocolSet23(Protocol):
    def __call__(self, this: Fluent, key: int, value: bool) -> Any: ...


class _ProtocolSet24(Protocol):
    def __call__(self, this: Fluent, key: int, value: str) -> Any: ...


class _ProtocolSet25(Protocol):
    def __call__(self, this: Fluent, key: int, value: Color) -> Any: ...


class _ProtocolSet26(Protocol):
    def __call__(self, this: Fluent, key: int, value: Box) -> Any: ...


class _ProtocolSet27(Protocol):
    def __call__(self, this: Fluent, key: int, value: Line) -> Any: ...


class _ProtocolSet28(Protocol):
    def __call__(self, this: Fluent, key: int, value: Label) -> Any: ...


class _ProtocolSet29(Protocol):
    def __call__(self, this: Fluent, key: int, value: Table) -> Any: ...


class _ProtocolSet30(Protocol):
    def __call__(self, this: Fluent, key: int, value: LineFill) -> Any: ...


class _ProtocolAppend(Protocol):
    def __call__(self, this: Fluent, value: int) -> Any: ...


class _ProtocolAppend32(Protocol):
    def __call__(self, this: Fluent, value: float) -> Any: ...


class _ProtocolAppend33(Protocol):
    def __call__(self, this: Fluent, value: bool) -> Any: ...


class _ProtocolAppend34(Protocol):
    def __call__(self, this: Fluent, value: str) -> Any: ...


class _ProtocolAppend35(Protocol):
    def __call__(self, this: Fluent, value: Color) -> Any: ...


class _ProtocolAppend36(Protocol):
    def __call__(self, this: Fluent, value: Box) -> Any: ...


class _ProtocolAppend37(Protocol):
    def __call__(self, this: Fluent, value: Line) -> Any: ...


class _ProtocolAppend38(Protocol):
    def __call__(self, this: Fluent, value: Label) -> Any: ...


class _ProtocolAppend39(Protocol):
    def __call__(self, this: Fluent, value: Table) -> Any: ...


class _ProtocolAppend40(Protocol):
    def __call__(self, this: Fluent, value: LineFill) -> Any: ...


class _ProtocolPrepend(Protocol):
    def __call__(self, this: Fluent, value: int) -> Any: ...


class _ProtocolPrepend42(Protocol):
    def __call__(self, this: Fluent, value: float) -> Any: ...


class _ProtocolPrepend43(Protocol):
    def __call__(self, this: Fluent, value: bool) -> Any: ...


class _ProtocolPrepend44(Protocol):
    def __call__(self, this: Fluent, value: str) -> Any: ...


class _ProtocolPrepend45(Protocol):
    def __call__(self, this: Fluent, value: Color) -> Any: ...


class _ProtocolPrepend46(Protocol):
    def __call__(self, this: Fluent, value: Box) -> Any: ...


class _ProtocolPrepend47(Protocol):
    def __call__(self, this: Fluent, value: Line) -> Any: ...


class _ProtocolPrepend48(Protocol):
    def __call__(self, this: Fluent, value: Label) -> Any: ...


class _ProtocolPrepend49(Protocol):
    def __call__(self, this: Fluent, value: Table) -> Any: ...


class _ProtocolPrepend50(Protocol):
    def __call__(self, this: Fluent, value: LineFill) -> Any: ...


init: _ProtocolInit = Exported()
get: _ProtocolGet = Exported()
get: _ProtocolGet2 = Exported()
get: _ProtocolGet3 = Exported()
get: _ProtocolGet4 = Exported()
get: _ProtocolGet5 = Exported()
get: _ProtocolGet6 = Exported()
get: _ProtocolGet7 = Exported()
get: _ProtocolGet8 = Exported()
get: _ProtocolGet9 = Exported()
get: _ProtocolGet10 = Exported()
get: _ProtocolGet11 = Exported()
get: _ProtocolGet12 = Exported()
get: _ProtocolGet13 = Exported()
get: _ProtocolGet14 = Exported()
get: _ProtocolGet15 = Exported()
set: _ProtocolSet = Exported()
set: _ProtocolSet17 = Exported()
set: _ProtocolSet18 = Exported()
set: _ProtocolSet19 = Exported()
set: _ProtocolSet20 = Exported()
set: _ProtocolSet21 = Exported()
set: _ProtocolSet22 = Exported()
set: _ProtocolSet23 = Exported()
set: _ProtocolSet24 = Exported()
set: _ProtocolSet25 = Exported()
set: _ProtocolSet26 = Exported()
set: _ProtocolSet27 = Exported()
set: _ProtocolSet28 = Exported()
set: _ProtocolSet29 = Exported()
set: _ProtocolSet30 = Exported()
append: _ProtocolAppend = Exported()
append: _ProtocolAppend32 = Exported()
append: _ProtocolAppend33 = Exported()
append: _ProtocolAppend34 = Exported()
append: _ProtocolAppend35 = Exported()
append: _ProtocolAppend36 = Exported()
append: _ProtocolAppend37 = Exported()
append: _ProtocolAppend38 = Exported()
append: _ProtocolAppend39 = Exported()
append: _ProtocolAppend40 = Exported()
prepend: _ProtocolPrepend = Exported()
prepend: _ProtocolPrepend42 = Exported()
prepend: _ProtocolPrepend43 = Exported()
prepend: _ProtocolPrepend44 = Exported()
prepend: _ProtocolPrepend45 = Exported()
prepend: _ProtocolPrepend46 = Exported()
prepend: _ProtocolPrepend47 = Exported()
prepend: _ProtocolPrepend48 = Exported()
prepend: _ProtocolPrepend49 = Exported()
prepend: _ProtocolPrepend50 = Exported()


@script.library('ToolsFluent', overlay=False, na_bool=True)
def main():
    @export
    @method
    def init(this: Fluent, msi__00000030__: dict[str, int] = na, msf__00000030__: dict[str, float] = na, msb__00000030__: dict[str, bool] = na, mss__00000030__: dict[str, str] = na, msc__00000030__: dict[str, Color] = na, aii__00000030__: list[int] = na, aif__00000030__: list[float] = na, aib__00000030__: list[bool] = na, ais__00000030__: list[str] = na, aic__00000030__: list[Color] = na, aibx__00000030__: list[Box] = na, ail__00000030__: list[Line] = na, ailb__00000030__: list[Label] = na, ait__00000030__: list[Table] = na, ailf__00000030__: list[LineFill] = na):
        this.msi = msi__00000030__ if not na(msi__00000030__) else this.msi if not na(this.msi) else map.new()
        this.msf = msf__00000030__ if not na(msf__00000030__) else this.msf if not na(this.msf) else map.new()
        this.msb = msb__00000030__ if not na(msb__00000030__) else this.msb if not na(this.msb) else map.new()
        this.mss = mss__00000030__ if not na(mss__00000030__) else this.mss if not na(this.mss) else map.new()
        this.msc = msc__00000030__ if not na(msc__00000030__) else this.msc if not na(this.msc) else map.new()
        this.aii = aii__00000030__ if not na(aii__00000030__) else this.aii if not na(this.aii) else array.new_int()
        this.aif = aif__00000030__ if not na(aif__00000030__) else this.aif if not na(this.aif) else array.new_float()
        this.aib = aib__00000030__ if not na(aib__00000030__) else this.aib if not na(this.aib) else array.new_bool()
        this.ais = ais__00000030__ if not na(ais__00000030__) else this.ais if not na(this.ais) else array.new_string()
        this.aic = aic__00000030__ if not na(aic__00000030__) else this.aic if not na(this.aic) else array.new_color()
        this.aibx = aibx__00000030__ if not na(aibx__00000030__) else this.aibx if not na(this.aibx) else array.new_box()
        this.ail = ail__00000030__ if not na(ail__00000030__) else this.ail if not na(this.ail) else array.new_line()
        this.ailb = ailb__00000030__ if not na(ailb__00000030__) else this.ailb if not na(this.ailb) else array.new_label()
        this.ait = ait__00000030__ if not na(ait__00000030__) else this.ait if not na(this.ait) else array.new_table()
        this.ailf = ailf__00000030__ if not na(ailf__00000030__) else this.ailf if not na(this.ailf) else array.new_linefill()
        return this.ailf

    @export
    @overload
    @method
    def get(this: Fluent, key: str, default: int):
        __block_result__ = na
        if not na(this.msi) and map.contains(this.msi, key):
            __block_result__ = map.get(this.msi, key)
        else:
            __block_result__ = default
        return __block_result__

    @export
    @overload
    @method
    def get(this: Fluent, key: str, default: float):
        __block_result_1__ = na
        if not na(this.msf) and map.contains(this.msf, key):
            __block_result_1__ = map.get(this.msf, key)
        else:
            __block_result_1__ = default
        return __block_result_1__

    @export
    @overload
    @method
    def get(this: Fluent, key: str, default: bool):
        __block_result_2__ = na
        if not na(this.msb) and map.contains(this.msb, key):
            __block_result_2__ = map.get(this.msb, key)
        else:
            __block_result_2__ = default
        return __block_result_2__

    @export
    @overload
    @method
    def get(this: Fluent, key: str, default: str):
        __block_result_3__ = na
        if not na(this.mss) and map.contains(this.mss, key):
            __block_result_3__ = map.get(this.mss, key)
        else:
            __block_result_3__ = default
        return __block_result_3__

    @export
    @overload
    @method
    def get(this: Fluent, key: str, default: Color):
        __block_result_4__ = na
        if not na(this.msc) and map.contains(this.msc, key):
            __block_result_4__ = map.get(this.msc, key)
        else:
            __block_result_4__ = default
        return __block_result_4__

    @export
    @overload
    @method
    def get(this: Fluent, key: int, default: int):
        __block_result_5__ = na
        if not na(this.aii) and key <= array.size(this.aii) - 1:
            __block_result_5__ = array.get(this.aii, key)
        else:
            __block_result_5__ = default
        return __block_result_5__

    @export
    @overload
    @method
    def get(this: Fluent, key: int, default: float):
        __block_result_6__ = na
        if not na(this.aif) and key <= array.size(this.aif) - 1:
            __block_result_6__ = array.get(this.aif, key)
        else:
            __block_result_6__ = default
        return __block_result_6__

    @export
    @overload
    @method
    def get(this: Fluent, key: int, default: bool):
        __block_result_7__ = na
        if not na(this.aib) and key <= array.size(this.aib) - 1:
            __block_result_7__ = array.get(this.aib, key)
        else:
            __block_result_7__ = default
        return __block_result_7__

    @export
    @overload
    @method
    def get(this: Fluent, key: int, default: str):
        __block_result_8__ = na
        if not na(this.ais) and key <= array.size(this.ais) - 1:
            __block_result_8__ = array.get(this.ais, key)
        else:
            __block_result_8__ = default
        return __block_result_8__

    @export
    @overload
    @method
    def get(this: Fluent, key: int, default: Color):
        __block_result_9__ = na
        if not na(this.aic) and key <= array.size(this.aic) - 1:
            __block_result_9__ = array.get(this.aic, key)
        else:
            __block_result_9__ = default
        return __block_result_9__

    @export
    @overload
    @method
    def get(this: Fluent, key: int, default: Box):
        __block_result_10__ = na
        if not na(this.aibx) and key <= array.size(this.aibx) - 1:
            __block_result_10__ = array.get(this.aibx, key)
        else:
            __block_result_10__ = default
        return __block_result_10__

    @export
    @overload
    @method
    def get(this: Fluent, key: int, default: Line):
        __block_result_11__ = na
        if not na(this.ail) and key <= array.size(this.ail) - 1:
            __block_result_11__ = array.get(this.ail, key)
        else:
            __block_result_11__ = default
        return __block_result_11__

    @export
    @overload
    @method
    def get(this: Fluent, key: int, default: Label):
        __block_result_12__ = na
        if not na(this.ailb) and key <= array.size(this.ailb) - 1:
            __block_result_12__ = array.get(this.ailb, key)
        else:
            __block_result_12__ = default
        return __block_result_12__

    @export
    @overload
    @method
    def get(this: Fluent, key: int, default: Table):
        __block_result_13__ = na
        if not na(this.ait) and key <= array.size(this.ait) - 1:
            __block_result_13__ = array.get(this.ait, key)
        else:
            __block_result_13__ = default
        return __block_result_13__

    @export
    @overload
    @method
    def get(this: Fluent, key: int, default: LineFill):
        __block_result_14__ = na
        if not na(this.ailf) and key <= array.size(this.ailf) - 1:
            __block_result_14__ = array.get(this.ailf, key)
        else:
            __block_result_14__ = default
        return __block_result_14__

    @export
    @overload
    @method
    def set(this: Fluent, key: str, value: int):
        if na(this.msi):
            this.msi = map.new()
        return map.put(this.msi, key, value)

    @export
    @overload
    @method
    def set(this: Fluent, key: str, value: float):
        if na(this.msf):
            this.msf = map.new()
        return map.put(this.msf, key, value)

    @export
    @overload
    @method
    def set(this: Fluent, key: str, value: bool):
        if na(this.msb):
            this.msb = map.new()
        return map.put(this.msb, key, value)

    @export
    @overload
    @method
    def set(this: Fluent, key: str, value: str):
        if na(this.mss):
            this.mss = map.new()
        return map.put(this.mss, key, value)

    @export
    @overload
    @method
    def set(this: Fluent, key: str, value: Color):
        if na(this.msc):
            this.msc = map.new()
        return map.put(this.msc, key, value)

    @export
    @overload
    @method
    def set(this: Fluent, key: int, value: int):
        if na(this.aii):
            this.aii = array.new_int()
        return array.set(this.aii, key, value)

    @export
    @overload
    @method
    def set(this: Fluent, key: int, value: float):
        if na(this.aif):
            this.aif = array.new_float()
        return array.set(this.aif, key, value)

    @export
    @overload
    @method
    def set(this: Fluent, key: int, value: bool):
        if na(this.aib):
            this.aib = array.new_bool()
        return array.set(this.aib, key, value)

    @export
    @overload
    @method
    def set(this: Fluent, key: int, value: str):
        if na(this.ais):
            this.ais = array.new_string()
        return array.set(this.ais, key, value)

    @export
    @overload
    @method
    def set(this: Fluent, key: int, value: Color):
        if na(this.aic):
            this.aic = array.new_color()
        return array.set(this.aic, key, value)

    @export
    @overload
    @method
    def set(this: Fluent, key: int, value: Box):
        if na(this.aibx):
            this.aibx = array.new_box()
        return array.set(this.aibx, key, value)

    @export
    @overload
    @method
    def set(this: Fluent, key: int, value: Line):
        if na(this.ail):
            this.ail = array.new_line()
        return array.set(this.ail, key, value)

    @export
    @overload
    @method
    def set(this: Fluent, key: int, value: Label):
        if na(this.ailb):
            this.ailb = array.new_label()
        return array.set(this.ailb, key, value)

    @export
    @overload
    @method
    def set(this: Fluent, key: int, value: Table):
        if na(this.ait):
            this.ait = array.new_table()
        return array.set(this.ait, key, value)

    @export
    @overload
    @method
    def set(this: Fluent, key: int, value: LineFill):
        if na(this.ailf):
            this.ailf = array.new_linefill()
        return array.set(this.ailf, key, value)

    @export
    @overload
    @method
    def append(this: Fluent, value: int):
        if na(this.aii):
            this.aii = array.from_items(value)
        return array.push(this.aii, value)

    @export
    @overload
    @method
    def append(this: Fluent, value: float):
        if na(this.aif):
            this.aif = array.from_items(value)
        return array.push(this.aif, value)

    @export
    @overload
    @method
    def append(this: Fluent, value: bool):
        if na(this.aib):
            this.aib = array.from_items(value)
        return array.push(this.aib, value)

    @export
    @overload
    @method
    def append(this: Fluent, value: str):
        if na(this.ais):
            this.ais = array.from_items(value)
        return array.push(this.ais, value)

    @export
    @overload
    @method
    def append(this: Fluent, value: Color):
        if na(this.aic):
            this.aic = array.from_items(value)
        return array.push(this.aic, value)

    @export
    @overload
    @method
    def append(this: Fluent, value: Box):
        if na(this.aibx):
            this.aibx = array.from_items(value)
        return array.push(this.aibx, value)

    @export
    @overload
    @method
    def append(this: Fluent, value: Line):
        if na(this.ail):
            this.ail = array.from_items(value)
        return array.push(this.ail, value)

    @export
    @overload
    @method
    def append(this: Fluent, value: Label):
        if na(this.ailb):
            this.ailb = array.from_items(value)
        return array.push(this.ailb, value)

    @export
    @overload
    @method
    def append(this: Fluent, value: Table):
        if na(this.ait):
            this.ait = array.from_items(value)
        return array.push(this.ait, value)

    @export
    @overload
    @method
    def append(this: Fluent, value: LineFill):
        if na(this.ailf):
            this.ailf = array.from_items(value)
        return array.push(this.ailf, value)

    @export
    @overload
    @method
    def prepend(this: Fluent, value: int):
        if na(this.aii):
            this.aii = array.from_items(value)
        return array.unshift(this.aii, value)

    @export
    @overload
    @method
    def prepend(this: Fluent, value: float):
        if na(this.aif):
            this.aif = array.from_items(value)
        return array.unshift(this.aif, value)

    @export
    @overload
    @method
    def prepend(this: Fluent, value: bool):
        if na(this.aib):
            this.aib = array.from_items(value)
        return array.unshift(this.aib, value)

    @export
    @overload
    @method
    def prepend(this: Fluent, value: str):
        if na(this.ais):
            this.ais = array.from_items(value)
        return array.unshift(this.ais, value)

    @export
    @overload
    @method
    def prepend(this: Fluent, value: Color):
        if na(this.aic):
            this.aic = array.from_items(value)
        return array.unshift(this.aic, value)

    @export
    @overload
    @method
    def prepend(this: Fluent, value: Box):
        if na(this.aibx):
            this.aibx = array.from_items(value)
        return array.unshift(this.aibx, value)

    @export
    @overload
    @method
    def prepend(this: Fluent, value: Line):
        if na(this.ail):
            this.ail = array.from_items(value)
        return array.unshift(this.ail, value)

    @export
    @overload
    @method
    def prepend(this: Fluent, value: Label):
        if na(this.ailb):
            this.ailb = array.from_items(value)
        return array.unshift(this.ailb, value)

    @export
    @overload
    @method
    def prepend(this: Fluent, value: Table):
        if na(this.ait):
            this.ait = array.from_items(value)
        return array.unshift(this.ait, value)

    @export
    @overload
    @method
    def prepend(this: Fluent, value: LineFill):
        if na(this.ailf):
            this.ailf = array.from_items(value)
        return array.unshift(this.ailf, value)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
