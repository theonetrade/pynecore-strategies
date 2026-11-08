"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    array, bar_index, barstate, box, close, color, dayofweek, high, hl2,
    hlc3, label, line, linefill, low, math, na, nz, ohlc4, open, position, script, size, string,
    syminfo, ta, table, time_close, timeframe, timenow, volume, yloc
)
from pynecore.types import Box, Label, Line, LineFill, Persistent, Series
from typing import Protocol, Any
import lib.boitoki.Heikinashi.v6 as heikinashi


__all__ = ['QQE', 'auto_htf', 'clear_boxes', 'clear_labels', 'clear_lines', 'countdown', 'get_day', 'price_range', 'qqe_func', 'remove_boxes', 'remove_labels', 'remove_linefills', 'remove_lines', 'round', 'rounded_price', 'source', 'toPips', 'toPrice', 'to_pips', 'to_price']


class _ProtocolToPips(Protocol):
    def __call__(self, _v: float) -> Any: ...


class _ProtocolTopips(Protocol):
    def __call__(self, _v: float) -> Any: ...


class _ProtocolToPrice(Protocol):
    def __call__(self, _p: float) -> Any: ...


class _ProtocolToprice(Protocol):
    def __call__(self, _p: float) -> Any: ...


class _ProtocolRound(Protocol):
    def __call__(self, _x: float, _type: str = 'round') -> Any: ...


class _ProtocolRoundedPrice(Protocol):
    def __call__(self, _price: float, _unit: float, _type: str = 'ceil', is_up: bool = True, _index: int = 0) -> Any: ...


class _ProtocolPriceRange(Protocol):
    def __call__(self, _a: float = open, _b: float = close) -> Any: ...


class _ProtocolGetDay(Protocol):
    def __call__(self, _n: int, _lang: str = 'en') -> Any: ...


class _ProtocolAutoHtf(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolSource(Protocol):
    def __call__(self, _name: str) -> Any: ...


class _ProtocolClearLines(Protocol):
    def __call__(self, _arr: list[Line], _min: int = 0) -> Any: ...


class _ProtocolClearLabels(Protocol):
    def __call__(self, _arr: list[Label], _min: int = 0) -> Any: ...


class _ProtocolClearBoxes(Protocol):
    def __call__(self, _arr: list[Box], _min: int = 0) -> Any: ...


class _ProtocolRemoveLines(Protocol):
    def __call__(self, _arr: list[Line], _max: int, _start: int, _step: int) -> Any: ...


class _ProtocolRemoveLinefills(Protocol):
    def __call__(self, _arr: list[LineFill], _max: int, _start: int, _step: int) -> Any: ...


class _ProtocolRemoveBoxes(Protocol):
    def __call__(self, _arr: list[Box], _max: int, _start: int, _step: int) -> Any: ...


class _ProtocolRemoveLabels(Protocol):
    def __call__(self, _arr: list[Label], _max: int, _start: int, _step: int) -> Any: ...


class _ProtocolCountdown(Protocol):
    def __call__(self, tf: str) -> Any: ...


class _ProtocolQqeFunc(Protocol):
    def __call__(self, _src: float, _period: int, _s_factor: int, _f_factor: float, _threshold: float) -> Any: ...


class _ProtocolQqe(Protocol):
    def __call__(self, _src: float, _period: int, _s_factor: int, _f_factor: float, _threshold: float) -> Any: ...


to_pips: _ProtocolToPips = Exported()
toPips: _ProtocolTopips = Exported()
to_price: _ProtocolToPrice = Exported()
toPrice: _ProtocolToprice = Exported()
round: _ProtocolRound = Exported()
rounded_price: _ProtocolRoundedPrice = Exported()
price_range: _ProtocolPriceRange = Exported()
get_day: _ProtocolGetDay = Exported()
auto_htf: _ProtocolAutoHtf = Exported()
source: _ProtocolSource = Exported()
clear_lines: _ProtocolClearLines = Exported()
clear_labels: _ProtocolClearLabels = Exported()
clear_boxes: _ProtocolClearBoxes = Exported()
remove_lines: _ProtocolRemoveLines = Exported()
remove_linefills: _ProtocolRemoveLinefills = Exported()
remove_boxes: _ProtocolRemoveBoxes = Exported()
remove_labels: _ProtocolRemoveLabels = Exported()
countdown: _ProtocolCountdown = Exported()
qqe_func: _ProtocolQqeFunc = Exported()
QQE: _ProtocolQqe = Exported()


@script.library('Utilities')
def main():
    @export
    def to_pips(_v: float):
        return _v / (syminfo.mintick * 10)

    @export
    def toPips(_v: float):
        return _v / (syminfo.mintick * 10)

    @export
    def to_price(_p: float):
        return _p * syminfo.mintick * 10

    @export
    def toPrice(_p: float):
        return _p * syminfo.mintick * 10

    @export
    def round(_x: float, _type: str = 'round'):
        __block_result__ = na
        __switch__ = _type
        if __switch__ == 'ceil':
            __block_result__ = math.ceil(_x)
        elif __switch__ == 'floor':
            __block_result__ = math.floor(_x)
        elif __switch__ == 'round':
            __block_result__ = math.round(_x)
        elif __switch__ == 'int':
            __block_result__ = cast_int(_x)
        else:
            __block_result__ = _x
        return __block_result__

    @export
    def rounded_price(_price: float, _unit: float, _type: str = 'ceil', is_up: bool = True, _index: int = 0):
        unit = _unit * syminfo.mintick
        tick = _price / unit
        price = round(tick, _type)
        index = math.max(_index, 0)
        __block_result_1__ = na
        if _index > 0:
            arr: list[float] = array.new_float()
            for i in pine_range(0, _index, 1):
                p = price + unit * i if is_up else price - unit * i
                array.push(arr, p)
            __block_result_1__ = array.get(arr, _index)
        else:
            __block_result_1__ = price * unit
        return __block_result_1__

    @export
    def price_range(_a: float = open, _b: float = close):
        return math.abs(_a - _b)

    @export
    def get_day(_n: int, _lang: str = 'en'):
        _day = _n + 10 if _lang == 'ja' else _n
        __block_result_2__ = na
        __switch__ = _day
        if __switch__ == 1:
            __block_result_2__ = 'Sun'
        elif __switch__ == 2:
            __block_result_2__ = 'Mon'
        elif __switch__ == 3:
            __block_result_2__ = 'Tue'
        elif __switch__ == 4:
            __block_result_2__ = 'Wed'
        elif __switch__ == 5:
            __block_result_2__ = 'Thu'
        elif __switch__ == 6:
            __block_result_2__ = 'Fri'
        elif __switch__ == 7:
            __block_result_2__ = 'Sat'
        elif __switch__ == 11:
            __block_result_2__ = '日'
        elif __switch__ == 12:
            __block_result_2__ = '月'
        elif __switch__ == 13:
            __block_result_2__ = '火'
        elif __switch__ == 14:
            __block_result_2__ = '水'
        elif __switch__ == 15:
            __block_result_2__ = '木'
        elif __switch__ == 16:
            __block_result_2__ = '金'
        elif __switch__ == 17:
            __block_result_2__ = '土'
        return __block_result_2__

    @export
    def auto_htf():
        return ('D' if timeframe.multiplier <= 60 else 'W' if timeframe.multiplier <= 240 else 'M') if timeframe.isintraday else '6M' if timeframe.period == 'D' else '12M'

    @export
    def source(_name: str):
        name = string.lower(_name)
        hopen: float = 0.0
        hclose: float = 0.0
        if string.contains(name, 'heikinashi:'):
            _hopen, _, _, _hclose = heikinashi.calc(open, high, low, close)
            hopen = _hopen
            hclose = hclose
        __block_result_3__ = na
        __switch__ = name
        if __switch__ == 'open':
            __block_result_3__ = open
        elif __switch__ == 'high':
            __block_result_3__ = high
        elif __switch__ == 'low':
            __block_result_3__ = low
        elif __switch__ == 'close':
            __block_result_3__ = close
        elif __switch__ == 'oc2':
            __block_result_3__ = math.avg(open, close)
        elif __switch__ == 'hl2':
            __block_result_3__ = hl2
        elif __switch__ == 'hlc3':
            __block_result_3__ = hlc3
        elif __switch__ == 'ohlc4':
            __block_result_3__ = ohlc4
        elif __switch__ == 'hlcc4':
            __block_result_3__ = math.avg(high, low, close, close)
        elif __switch__ == 'volume':
            __block_result_3__ = volume
        elif __switch__ == 'heikinashi: open':
            __block_result_3__ = hopen
        elif __switch__ == 'heikinashi: close':
            __block_result_3__ = hclose
        elif __switch__ == 'heikinashi: oc2':
            __block_result_3__ = math.avg(hopen, hclose)
        else:
            __block_result_3__ = close
        return __block_result_3__

    @export
    def clear_lines(_arr: list[Line], _min: int = 0):
        __block_result_4__ = na
        if array.size(_arr) > math.max(0, _min):
            __block_result_5__ = na
            __loop_1__ = pine_loop(0 + _min, 1)
            while __loop_1__.step(array.size(_arr)):
                i = __loop_1__.value
                __block_result_5__ = line.delete(array.shift(_arr))
            __block_result_4__ = __block_result_5__
        return __block_result_4__

    @export
    def clear_labels(_arr: list[Label], _min: int = 0):
        __block_result_6__ = na
        if array.size(_arr) > math.max(0, _min):
            __block_result_7__ = na
            __loop_1__ = pine_loop(0 + _min, 1)
            while __loop_1__.step(array.size(_arr)):
                i = __loop_1__.value
                __block_result_7__ = label.delete(array.shift(_arr))
            __block_result_6__ = __block_result_7__
        return __block_result_6__

    @export
    def clear_boxes(_arr: list[Box], _min: int = 0):
        __block_result_8__ = na
        if array.size(_arr) > math.max(0, _min):
            __block_result_9__ = na
            __loop_1__ = pine_loop(0 + _min, 1)
            while __loop_1__.step(array.size(_arr)):
                i = __loop_1__.value
                __block_result_9__ = box.delete(array.shift(_arr))
            __block_result_8__ = __block_result_9__
        return __block_result_8__

    @export
    def remove_lines(_arr: list[Line], _max: int, _start: int, _step: int):
        __block_result_10__ = na
        if array.size(_arr) > _max * _step:
            __block_result_11__ = na
            __loop_1__ = pine_loop(_start, 1)
            while __loop_1__.step(array.size(_arr) - 1):
                i = __loop_1__.value
                __block_result_11__ = line.delete(array.shift(_arr))
            __block_result_10__ = __block_result_11__
        return __block_result_10__

    @export
    def remove_linefills(_arr: list[LineFill], _max: int, _start: int, _step: int):
        __block_result_12__ = na
        if array.size(_arr) > _max * _step:
            __block_result_13__ = na
            __loop_1__ = pine_loop(_start, 1)
            while __loop_1__.step(array.size(_arr) - 1):
                i = __loop_1__.value
                __block_result_13__ = linefill.delete(array.shift(_arr))
            __block_result_12__ = __block_result_13__
        return __block_result_12__

    @export
    def remove_boxes(_arr: list[Box], _max: int, _start: int, _step: int):
        __block_result_14__ = na
        if array.size(_arr) > _max * _step:
            __block_result_15__ = na
            __loop_1__ = pine_loop(_start, 1)
            while __loop_1__.step(array.size(_arr) - 1):
                i = __loop_1__.value
                __block_result_15__ = box.delete(array.shift(_arr))
            __block_result_14__ = __block_result_15__
        return __block_result_14__

    @export
    def remove_labels(_arr: list[Label], _max: int, _start: int, _step: int):
        __block_result_16__ = na
        if array.size(_arr) > _max * _step:
            __block_result_17__ = na
            __loop_1__ = pine_loop(_start, 1)
            while __loop_1__.step(array.size(_arr) - 1):
                i = __loop_1__.value
                __block_result_17__ = label.delete(array.shift(_arr))
            __block_result_16__ = __block_result_17__
        return __block_result_16__

    @export
    def countdown(tf: str):
        til_next = time_close(tf) / 1000 - math.floor(timenow / 1000)
        next_day = math.floor(til_next / 60 / 60 / 24)
        next_hour = math.floor(til_next / 60 / 60) - next_day * 24
        next_min = math.floor(til_next / 60) - math.floor(til_next / 60 / 60) * 60
        next_sec = til_next - math.floor(til_next / 60) * 60
        place0 = '' if next_day == 0 else string.tostring(next_day, '00') + ':'
        place1 = '' if next_hour == 0 else string.tostring(next_hour, '00') + ':'
        place2 = string.tostring(next_min, '00') + ':'
        place3 = string.tostring(next_sec, '00')
        return place0 + place1 + place2 + place3

    @export
    def qqe_func(_src: float, _period: int, _s_factor: int, _f_factor: float, _threshold: float):
        Wilders_Period = _period * 2 - 1
        Rsi = ta.rsi(_src, _period)
        RsiMa: Series = ta.ema(Rsi, _s_factor)
        AtrRsi = math.abs(RsiMa[1] - RsiMa)
        MaAtrRsi = ta.ema(AtrRsi, Wilders_Period)
        dar = ta.ema(MaAtrRsi, Wilders_Period) * _f_factor
        longband: Series[float] = 0.0
        shortband: Series[float] = 0.0
        trend: Series[int] = 0
        DeltaFastAtrRsi = dar
        RSIndex: Series = RsiMa
        newshortband = RSIndex + DeltaFastAtrRsi
        newlongband = RSIndex - DeltaFastAtrRsi
        longband = math.max(longband[1], newlongband) if RSIndex[1] > longband[1] and RSIndex > longband[1] else newlongband
        shortband = math.min(shortband[1], newshortband) if RSIndex[1] < shortband[1] and RSIndex < shortband[1] else newshortband
        cross = ta.cross(longband[1], RSIndex)
        trend = 1 if ta.cross(RSIndex, shortband[1]) else -1 if cross else nz(trend[1], 1)
        FastAtrRsiTL = longband if trend == 1 else shortband
        osc = RsiMa - 50
        mod = osc if osc > _threshold or osc < 0 - _threshold else 0
        qqe = FastAtrRsiTL - 50
        return (osc, mod, qqe)

    @export
    def QQE(_src: float, _period: int, _s_factor: int, _f_factor: float, _threshold: float):
        return qqe_func(_src, _period, _s_factor, _f_factor, _threshold)

    testTable: Persistent = table.new(position=position.top_right, columns=2, rows=10, bgcolor=color.yellow, border_width=1)
    if barstate.islast:
        table.cell(table_id=testTable, column=0, row=0, text='Open-Close is')
        table.cell(table_id=testTable, column=1, row=0, text=string.format('{0,number,#.#}', toPips(open - close)) + 'pips', bgcolor=color.white)
        table.cell(table_id=testTable, column=0, row=1, text='10pips is')
        table.cell(table_id=testTable, column=1, row=1, text=string.tostring(toPrice(10)) + ' ' + syminfo.currency, bgcolor=color.white)
        table.cell(table_id=testTable, column=0, row=2, text='Today is')
        table.cell(table_id=testTable, column=1, row=2, text=get_day(dayofweek), bgcolor=color.white)
        table.cell(table_id=testTable, column=0, row=3, text='今日は')
        table.cell(table_id=testTable, column=1, row=3, text=get_day(dayofweek, 'ja') + '曜日', bgcolor=color.white)
        table.cell(table_id=testTable, column=0, row=4, text='平均足')
        table.cell(table_id=testTable, column=1, row=4, text=string.format('{0,number,#.##}', source('heikinashi-open')) + ', ' + string.format('{0,number,#.##}', source('heikinashi-close')), bgcolor=color.white)
        table.cell(table_id=testTable, column=0, row=5, text='HTF')
        table.cell(table_id=testTable, column=1, row=5, text=auto_htf(), bgcolor=color.white)
        table.cell(table_id=testTable, column=0, row=6, text='カウントダウン')
        table.cell(table_id=testTable, column=1, row=6, text=countdown(auto_htf()), bgcolor=color.white)
    a: Persistent[list[Label]] = array.new_label()
    b: Persistent[list[Line]] = array.new_line()
    array.push(a, label.new(bar_index, na, string.tostring(dayofweek), yloc=yloc.abovebar, size=size.tiny))
    array.push(b, line.new(bar_index, high + ta.sma(high - low, 10), bar_index, low - ta.sma(high - low, 10)))
    clear_labels(a, 3)
    clear_lines(b, 20)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
