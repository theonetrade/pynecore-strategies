"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore import pine_loop
from pynecore.core.pine_cast import cast_bool
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import bar_index, close, line, na, runtime, script, ta
from pynecore.types import Line, Persistent, Series
from typing import Protocol, Any


__all__ = ['Trendline', 'TrendlineData', 'TrendlineLines', 'TrendlineSettings', 'drawLine', 'drawTrendline', 'new']


@udt
class TrendlineSettings:
    x_axis: int = na(int)
    offset: int = na(int)
    strictMode: bool = na(bool)
    strictType: int = na(int)


@udt
class TrendlineData:
    slope: float = na(float)
    x1: int = na(int)
    x2: int = na(int)
    changeInX: int = na(int)


@udt
class TrendlineLines:
    startline: Line = na(Line)
    trendline: Line = na(Line)


@udt
class Trendline:
    info: 'TrendlineSettings' = _dataclass_field(default_factory=lambda: na(TrendlineSettings))
    values: 'TrendlineData' = _dataclass_field(default_factory=lambda: na(TrendlineData))
    lines: 'TrendlineLines' = _dataclass_field(default_factory=lambda: na(TrendlineLines))


class _ProtocolNew(Protocol):
    def __call__(self, x_axis: int, offset: int = 0, strictMode: bool = False, strictType: int = na) -> Any: ...


class _ProtocolDrawline(Protocol):
    def __call__(self, this: Trendline, condition: bool, y1: float, y2: float, src: float = na) -> Any: ...


class _ProtocolDrawtrendline(Protocol):
    def __call__(self, this: Trendline, condition: bool) -> Any: ...


new: _ProtocolNew = Exported()
drawLine: _ProtocolDrawline = Exported()
drawTrendline: _ProtocolDrawtrendline = Exported()


@script.library('SimpleTrendlines', overlay=True, na_bool=True)
def main():
    @export
    def new(x_axis: int, offset: int = 0, strictMode: bool = False, strictType: int = na):
        l1: Persistent[Line] = line.new(na, na, na, na)
        l2: Persistent[Line] = line.new(na, na, na, na)
        this: Trendline = Trendline(TrendlineSettings(x_axis, offset, strictMode, strictType), TrendlineData(na, bar_index - (x_axis + offset), bar_index - offset, na), TrendlineLines(l1, l2))
        if strictType > 1:
            runtime.error('strictType must be a value of 0 or 1.')
        elif strictType > 0 and (na(strictMode) or not strictMode):
            runtime.error("strictType can't have an assigned value without strictMode being true.")
        elif strictMode and offset < 1:
            runtime.error('Offset must be over 0 in order to use strictMode.')
        return this

    @export
    @method
    def drawLine(this: Trendline, condition: bool, y1: float, y2: float, src: Series[float] = na):
        savedSlope: Persistent[float] = na(float)
        if condition and (na(this.info.strictMode) or not this.info.strictMode):
            line.set_xy1(this.lines.startline, this.values.x1, y1)
            line.set_xy2(this.lines.startline, this.values.x2, y2)
            savedSlope = (line.get_y2(this.lines.startline) - line.get_y1(this.lines.startline)) / this.info.x_axis
        if condition and this.info.strictMode:
            this.values.slope = (y2 - y1) / this.info.x_axis
            validElements: bool = na(bool)
            __loop_1__ = pine_loop(0, 1)
            while __loop_1__.step(this.info.offset):
                i = __loop_1__.value
                j = this.info.offset - i
                if (close[j] if na(src) else src[j]) >= y2 + this.values.slope * i if this.info.strictType == 0 else (close[j] if na(src) else src[j]) <= y2 + this.values.slope * i:
                    validElements = True
                else:
                    validElements = na
                    break
            if not na(validElements):
                line.set_xy1(this.lines.startline, this.values.x1, y1)
                line.set_xy2(this.lines.startline, this.values.x2, y2)
                savedSlope = (line.get_y2(this.lines.startline) - line.get_y1(this.lines.startline)) / this.info.x_axis
        this.values.slope = savedSlope
        this.values.changeInX = ta.barssince(cast_bool(ta.change(line.get_y2(this.lines.startline)))) + this.info.offset
        return this.values.changeInX

    @export
    @method
    def drawTrendline(this: Trendline, condition: bool):
        __block_result__ = na
        if condition:
            line.set_xy1(this.lines.trendline, line.get_x2(this.lines.startline), line.get_y2(this.lines.startline))
            __block_result__ = line.set_xy2(this.lines.trendline, bar_index, line.get_y2(this.lines.startline) + this.values.slope * this.values.changeInX)
        return __block_result__


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
