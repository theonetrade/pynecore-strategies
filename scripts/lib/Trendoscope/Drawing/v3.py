"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore.core.overload import overload
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, box, color, extend, font, label, line, linefill, math, na, order,
    polyline, script, size, string, text, xloc, yloc
)
from pynecore.types import Box, Color, Label, Line, LineFill, Polyline
from pynecore.types.chart import ChartPoint
from typing import Protocol, Any


__all__ = ['BoxProperties', 'BoxText', 'Box__ren__', 'LabelProperties', 'Label__ren__', 'LineProperties', 'Line__ren__', 'Linefill__ren__', 'PolyLine', 'PolyLineProperties', 'clear', 'createBox', 'createLabel', 'createLine', 'createLinefill', 'delete', 'draw', 'get_price', 'init', 'tostring']


@udt
class LineProperties:
    xloc__ren__: str = _dataclass_field(default_factory=lambda: xloc.bar_index)
    extend__ren__: str = _dataclass_field(default_factory=lambda: extend.none)
    color__ren__: Color = _dataclass_field(default_factory=lambda: color.blue)
    style: str = _dataclass_field(default_factory=lambda: line.style_solid)
    width: int = 1
    force_overlay: bool = False


@udt
class Line__ren__:
    start: ChartPoint = na(ChartPoint)
    end: ChartPoint = na(ChartPoint)
    properties: 'LineProperties' = _dataclass_field(default_factory=lambda: na(LineProperties))
    object: Line = na(Line)


@udt
class LabelProperties:
    xloc__ren__: str = _dataclass_field(default_factory=lambda: xloc.bar_index)
    yloc__ren__: str = _dataclass_field(default_factory=lambda: yloc.price)
    color__ren__: Color = _dataclass_field(default_factory=lambda: color.blue)
    style: str = _dataclass_field(default_factory=lambda: label.style_none)
    textcolor: Color = _dataclass_field(default_factory=lambda: color.black)
    size__ren__: str = _dataclass_field(default_factory=lambda: size.normal)
    textalign: str = _dataclass_field(default_factory=lambda: text.align_center)
    text_font_family: str = _dataclass_field(default_factory=lambda: font.family_default)
    force_overlay: bool = False


@udt
class Label__ren__:
    point: ChartPoint = na(ChartPoint)
    lblText: str = na(str)
    tooltip: str = na(str)
    properties: 'LabelProperties' = _dataclass_field(default_factory=lambda: na(LabelProperties))
    object: Label = na(Label)


@udt
class Linefill__ren__:
    line1: 'Line__ren__' = _dataclass_field(default_factory=lambda: na(Line__ren__))
    line2: 'Line__ren__' = _dataclass_field(default_factory=lambda: na(Line__ren__))
    fillColor: Color = _dataclass_field(default_factory=lambda: color.blue)
    transparency: int = 80
    object: LineFill = na(LineFill)


@udt
class BoxProperties:
    border_color: Color = _dataclass_field(default_factory=lambda: color.blue)
    bgcolor__ren__: Color = _dataclass_field(default_factory=lambda: color.blue)
    border_width: int = 1
    border_style: str = _dataclass_field(default_factory=lambda: line.style_solid)
    extend__ren__: str = _dataclass_field(default_factory=lambda: extend.none)
    xloc__ren__: str = _dataclass_field(default_factory=lambda: xloc.bar_index)
    force_overlay: bool = False


@udt
class BoxText:
    boxText: str = na(str)
    text_size: str = _dataclass_field(default_factory=lambda: size.auto)
    text_color: Color = _dataclass_field(default_factory=lambda: color.yellow)
    text_halign: str = _dataclass_field(default_factory=lambda: text.align_center)
    text_valign: str = _dataclass_field(default_factory=lambda: text.align_center)
    text_wrap: str = _dataclass_field(default_factory=lambda: text.wrap_auto)
    text_font_family: str = _dataclass_field(default_factory=lambda: font.family_default)


@udt
class Box__ren__:
    p1: ChartPoint = na(ChartPoint)
    p2: ChartPoint = na(ChartPoint)
    properties: 'BoxProperties' = _dataclass_field(default_factory=lambda: na(BoxProperties))
    textProperties: 'BoxText' = _dataclass_field(default_factory=lambda: na(BoxText))
    object: Box = na(Box)


@udt
class PolyLineProperties:
    curved: bool = False
    closed: bool = False
    xloc__ren__: str = _dataclass_field(default_factory=lambda: xloc.bar_index)
    lineColor: Color = _dataclass_field(default_factory=lambda: color.blue)
    fillColor: Color = na(Color)
    lineStyle: str = _dataclass_field(default_factory=lambda: line.style_solid)
    lineWidth: int = 1
    force_overlay: bool = False


@udt
class PolyLine:
    points: list[ChartPoint] = na(list)
    properties: 'PolyLineProperties' = _dataclass_field(default_factory=lambda: na(PolyLineProperties))
    object: Polyline = na(Polyline)


class _ProtocolGetPrice(Protocol):
    def __call__(self, this: Line__ren__, bar: int) -> Any: ...


class _ProtocolInit(Protocol):
    def __call__(self, this: PolyLine) -> Any: ...


class _ProtocolTostring(Protocol):
    def __call__(self, this: ChartPoint, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na) -> Any: ...


class _ProtocolTostring3(Protocol):
    def __call__(self, this: LineProperties, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na) -> Any: ...


class _ProtocolTostring4(Protocol):
    def __call__(self, this: Line__ren__, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na) -> Any: ...


class _ProtocolTostring5(Protocol):
    def __call__(self, this: LabelProperties, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na) -> Any: ...


class _ProtocolTostring6(Protocol):
    def __call__(self, this: Label__ren__, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na) -> Any: ...


class _ProtocolTostring7(Protocol):
    def __call__(self, this: Linefill__ren__, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na) -> Any: ...


class _ProtocolTostring8(Protocol):
    def __call__(self, this: BoxProperties, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na) -> Any: ...


class _ProtocolTostring9(Protocol):
    def __call__(self, this: BoxText, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na) -> Any: ...


class _ProtocolTostring10(Protocol):
    def __call__(self, this: Box__ren__, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na) -> Any: ...


class _ProtocolDelete(Protocol):
    def __call__(self, this: Line__ren__) -> Any: ...


class _ProtocolDelete12(Protocol):
    def __call__(self, this: Label__ren__) -> Any: ...


class _ProtocolDelete13(Protocol):
    def __call__(self, this: Linefill__ren__) -> Any: ...


class _ProtocolDelete14(Protocol):
    def __call__(self, this: Box__ren__) -> Any: ...


class _ProtocolDelete15(Protocol):
    def __call__(self, this: list[Line__ren__]) -> Any: ...


class _ProtocolDelete16(Protocol):
    def __call__(self, this: list[Label__ren__]) -> Any: ...


class _ProtocolDelete17(Protocol):
    def __call__(self, this: list[Linefill__ren__]) -> Any: ...


class _ProtocolDelete18(Protocol):
    def __call__(self, this: list[Box__ren__]) -> Any: ...


class _ProtocolClear(Protocol):
    def __call__(self, this: list[Line__ren__]) -> Any: ...


class _ProtocolClear20(Protocol):
    def __call__(self, this: list[Label__ren__]) -> Any: ...


class _ProtocolClear21(Protocol):
    def __call__(self, this: list[Linefill__ren__]) -> Any: ...


class _ProtocolClear22(Protocol):
    def __call__(self, this: list[Box__ren__]) -> Any: ...


class _ProtocolDraw(Protocol):
    def __call__(self, this: Line__ren__) -> Any: ...


class _ProtocolDraw24(Protocol):
    def __call__(self, this: list[Line__ren__]) -> Any: ...


class _ProtocolDraw25(Protocol):
    def __call__(self, this: Label__ren__) -> Any: ...


class _ProtocolDraw26(Protocol):
    def __call__(self, this: list[Label__ren__]) -> Any: ...


class _ProtocolDraw27(Protocol):
    def __call__(self, this: Linefill__ren__) -> Any: ...


class _ProtocolDraw28(Protocol):
    def __call__(self, this: list[Linefill__ren__]) -> Any: ...


class _ProtocolDraw29(Protocol):
    def __call__(self, this: Box__ren__) -> Any: ...


class _ProtocolDraw30(Protocol):
    def __call__(self, this: list[Box__ren__]) -> Any: ...


class _ProtocolCreatelabel(Protocol):
    def __call__(self, this: ChartPoint, lblText: str, tooltip: str = na, properties: LabelProperties = na) -> Any: ...


class _ProtocolCreateline(Protocol):
    def __call__(self, this: ChartPoint, other: ChartPoint, properties: LineProperties = na) -> Any: ...


class _ProtocolCreatelinefill(Protocol):
    def __call__(self, this: Line__ren__, other: Line__ren__, fillColor: Color = color.blue, transparency: int = 80) -> Any: ...


class _ProtocolCreatebox(Protocol):
    def __call__(self, this: ChartPoint, other: ChartPoint, properties: BoxProperties = na, textProperties: BoxText = na) -> Any: ...


class _ProtocolCreatebox35(Protocol):
    def __call__(self, this: Line__ren__, properties: BoxProperties = na, textProperties: BoxText = na) -> Any: ...


get_price: _ProtocolGetPrice = Exported()
init: _ProtocolInit = Exported()
tostring: _ProtocolTostring = Exported()
tostring: _ProtocolTostring3 = Exported()
tostring: _ProtocolTostring4 = Exported()
tostring: _ProtocolTostring5 = Exported()
tostring: _ProtocolTostring6 = Exported()
tostring: _ProtocolTostring7 = Exported()
tostring: _ProtocolTostring8 = Exported()
tostring: _ProtocolTostring9 = Exported()
tostring: _ProtocolTostring10 = Exported()
delete: _ProtocolDelete = Exported()
delete: _ProtocolDelete12 = Exported()
delete: _ProtocolDelete13 = Exported()
delete: _ProtocolDelete14 = Exported()
delete: _ProtocolDelete15 = Exported()
delete: _ProtocolDelete16 = Exported()
delete: _ProtocolDelete17 = Exported()
delete: _ProtocolDelete18 = Exported()
clear: _ProtocolClear = Exported()
clear: _ProtocolClear20 = Exported()
clear: _ProtocolClear21 = Exported()
clear: _ProtocolClear22 = Exported()
draw: _ProtocolDraw = Exported()
draw: _ProtocolDraw24 = Exported()
draw: _ProtocolDraw25 = Exported()
draw: _ProtocolDraw26 = Exported()
draw: _ProtocolDraw27 = Exported()
draw: _ProtocolDraw28 = Exported()
draw: _ProtocolDraw29 = Exported()
draw: _ProtocolDraw30 = Exported()
createLabel: _ProtocolCreatelabel = Exported()
createLine: _ProtocolCreateline = Exported()
createLinefill: _ProtocolCreatelinefill = Exported()
createBox: _ProtocolCreatebox = Exported()
createBox: _ProtocolCreatebox35 = Exported()


@script.library('Drawing', overlay=True)
def main():
    @export
    @method
    def get_price(this: Line__ren__, bar: int):
        stepPerBar = (this.end.price - this.start.price) / (this.end.index - this.start.index)
        distance = bar - this.start.index
        return this.start.price + distance * stepPerBar







    @export
    @method
    def init(this: PolyLine):
        if na(this.properties):
            this.properties = PolyLineProperties()
        return this

    @overload
    @method
    def delete(this: PolyLine):
        polyline.delete(this.object)
        return this

    @overload
    @method
    def draw(this: PolyLine):
        polyline.delete(this.object)
        this.object = polyline.new(this.points, this.properties.curved, this.properties.closed, this.properties.xloc__ren__, this.properties.lineColor, this.properties.fillColor, this.properties.lineStyle, this.properties.lineWidth)
        return this

    @overload
    @method
    def get(this: ChartPoint, key: str):
        return string.tostring(this.price) if key == 'price' else string.tostring(this.index) if key == 'bar' else string.tostring(this.time) if key == 'bartime' else na

    @export
    @overload
    @method
    def tostring(this: ChartPoint, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na):
        str__ren__: str = ''
        if not na(this):
            keys = array.from_items('price', 'bar', 'bartime') if na(includeKeys) else includeKeys
            keyValues: list[str] = array.new_string()
            if sortKeys and (not na(sortOrder)) and (sortOrder != 0):
                method_call('sort', keys, order.ascending if sortOrder > 0 else order.descending)

            for key in keys:
                array.push(keyValues, '"' + key + '":' + '"' + get(this, key) + '"')
            str__ren__ = '{' + array.join(keyValues, ',') + '}'
        return str__ren__

    @overload
    @method
    def get(this: LineProperties, key: str):
        return this.xloc__ren__ if key == 'xloc' else this.extend__ren__ if key == 'extend' else this.style if key == 'style' else string.tostring(this.width) if key == 'width' else na

    @export
    @overload
    @method
    def tostring(this: LineProperties, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na):
        str__ren__: str = ''
        if not na(this):
            keys = array.from_items('xloc', 'extend', 'style', 'width') if na(includeKeys) else includeKeys
            keyValues: list[str] = array.new_string()
            if sortKeys and (not na(sortOrder)) and (sortOrder != 0):
                method_call('sort', keys, order.ascending if sortOrder > 0 else order.descending)

            for key in keys:
                array.push(keyValues, '"' + key + '":' + '"' + get(this, key) + '"')
            str__ren__ = '{' + array.join(keyValues, ',') + '}'
        return str__ren__

    @overload
    @method
    def get(this: Line__ren__, key: str):
        return tostring(this.start) if key == 'start' else tostring(this.end) if key == 'end' else tostring(this.properties) if key == 'properties' else na

    @export
    @overload
    @method
    def tostring(this: Line__ren__, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na):
        str__ren__: str = ''
        if not na(this):
            keys = array.from_items('start', 'end', 'properties') if na(includeKeys) else includeKeys
            keyValues: list[str] = array.new_string()
            if sortKeys and (not na(sortOrder)) and (sortOrder != 0):
                method_call('sort', keys, order.ascending if sortOrder > 0 else order.descending)

            for key in keys:
                array.push(keyValues, '"' + key + '":' + '"' + get(this, key) + '"')
            str__ren__ = '{' + array.join(keyValues, ',') + '}'
        return str__ren__

    @overload
    @method
    def get(this: LabelProperties, key: str):
        return this.xloc__ren__ if key == 'xloc' else this.yloc__ren__ if key == 'yloc' else this.style if key == 'style' else string.tostring(this.size__ren__) if key == 'size' else this.textalign if key == 'textalign' else this.text_font_family if key == 'text_font_family' else na

    @export
    @overload
    @method
    def tostring(this: LabelProperties, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na):
        str__ren__: str = ''
        if not na(this):
            keys = array.from_items('xloc', 'yloc', 'style', 'size', 'textalign', 'text_font_family') if na(includeKeys) else includeKeys
            keyValues: list[str] = array.new_string()
            if sortKeys and (not na(sortOrder)) and (sortOrder != 0):
                method_call('sort', keys, order.ascending if sortOrder > 0 else order.descending)

            for key in keys:
                array.push(keyValues, '"' + key + '":' + '"' + get(this, key) + '"')
            str__ren__ = '{' + array.join(keyValues, ',') + '}'
        return str__ren__

    @overload
    @method
    def get(this: Label__ren__, key: str):
        return tostring(this.point) if key == 'point' else this.lblText if key == 'lblText' else this.tooltip if key == 'tooltip' else tostring(this.properties) if key == 'properties' else na

    @export
    @overload
    @method
    def tostring(this: Label__ren__, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na):
        str__ren__: str = ''
        if not na(this):
            keys = array.from_items('point', 'lblText', 'tooltip', 'properties') if na(includeKeys) else includeKeys
            keyValues: list[str] = array.new_string()
            if sortKeys and (not na(sortOrder)) and (sortOrder != 0):
                method_call('sort', keys, order.ascending if sortOrder > 0 else order.descending)

            for key in keys:
                array.push(keyValues, '"' + key + '":' + '"' + get(this, key) + '"')
            str__ren__ = '{' + array.join(keyValues, ',') + '}'
        return str__ren__

    @overload
    @method
    def get(this: Linefill__ren__, key: str):
        return tostring(this.line1) if key == 'line1' else tostring(this.line2) if key == 'line2' else string.tostring(this.transparency) if key == 'transparency' else na

    @export
    @overload
    @method
    def tostring(this: Linefill__ren__, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na):
        str__ren__: str = ''
        if not na(this):
            keys = array.from_items('line1', 'line2', 'transparency') if na(includeKeys) else includeKeys
            keyValues: list[str] = array.new_string()
            if sortKeys and (not na(sortOrder)) and (sortOrder != 0):
                method_call('sort', keys, order.ascending if sortOrder > 0 else order.descending)

            for key in keys:
                array.push(keyValues, '"' + key + '":' + '"' + get(this, key) + '"')
            str__ren__ = '{' + array.join(keyValues, ',') + '}'
        return str__ren__

    @overload
    @method
    def get(this: BoxProperties, key: str):
        return string.tostring(this.border_width) if key == 'border_width' else this.border_style if key == 'border_style' else this.extend__ren__ if key == 'extend' else this.xloc__ren__ if key == 'xloc' else na

    @export
    @overload
    @method
    def tostring(this: BoxProperties, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na):
        str__ren__: str = ''
        if not na(this):
            keys = array.from_items('border_width', 'border_style', 'extend', 'xloc') if na(includeKeys) else includeKeys
            keyValues: list[str] = array.new_string()
            if sortKeys and (not na(sortOrder)) and (sortOrder != 0):
                method_call('sort', keys, order.ascending if sortOrder > 0 else order.descending)

            for key in keys:
                array.push(keyValues, '"' + key + '":' + '"' + get(this, key) + '"')
            str__ren__ = '{' + array.join(keyValues, ',') + '}'
        return str__ren__

    @overload
    @method
    def get(this: BoxText, key: str):
        return this.boxText if key == 'boxText' else this.text_size if key == 'text_size' else this.text_halign if key == 'text_halign' else this.text_valign if key == 'text_valign' else this.text_wrap if key == 'text_wrap' else this.text_font_family if key == 'text_font_family' else na

    @export
    @overload
    @method
    def tostring(this: BoxText, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na):
        str__ren__: str = ''
        if not na(this):
            keys = array.from_items('boxText', 'text_size', 'text_halign', 'text_valign', 'text_wrap', 'text_font_family') if na(includeKeys) else includeKeys
            keyValues: list[str] = array.new_string()
            if sortKeys and (not na(sortOrder)) and (sortOrder != 0):
                method_call('sort', keys, order.ascending if sortOrder > 0 else order.descending)

            for key in keys:
                array.push(keyValues, '"' + key + '":' + '"' + get(this, key) + '"')
            str__ren__ = '{' + array.join(keyValues, ',') + '}'
        return str__ren__

    @overload
    @method
    def get(this: Box__ren__, key: str):
        return tostring(this.p1) if key == 'p1' else tostring(this.p2) if key == 'p2' else tostring(this.properties) if key == 'properties' else tostring(this.textProperties) if key == 'textProperties' else na

    @export
    @overload
    @method
    def tostring(this: Box__ren__, sortKeys: bool = False, sortOrder: int = 1, includeKeys: list[str] = na):
        str__ren__: str = ''
        if not na(this):
            keys = array.from_items('p1', 'p2', 'properties', 'textProperties') if na(includeKeys) else includeKeys
            keyValues: list[str] = array.new_string()
            if sortKeys and (not na(sortOrder)) and (sortOrder != 0):
                method_call('sort', keys, order.ascending if sortOrder > 0 else order.descending)

            for key in keys:
                array.push(keyValues, '"' + key + '":' + '"' + get(this, key) + '"')
            str__ren__ = '{' + array.join(keyValues, ',') + '}'
        return str__ren__

    def deleteObj(this):
        method_call(delete, this.object)
        return this

    @export
    @overload
    @method
    def delete(this: Line__ren__):
        return deleteObj(this)

    @export
    @overload
    @method
    def delete(this: Label__ren__):
        return deleteObj(this)

    @export
    @overload
    @method
    def delete(this: Linefill__ren__):
        return deleteObj(this)

    @export
    @overload
    @method
    def delete(this: Box__ren__):
        return deleteObj(this)

    def deleteAll(this):
        if not na(this):
            for obj in this:
                method_call(delete, obj)
        return this

    @export
    @overload
    @method
    def delete(this: list[Line__ren__]):
        return deleteAll(this)

    @export
    @overload
    @method
    def delete(this: list[Label__ren__]):
        return deleteAll(this)

    @export
    @overload
    @method
    def delete(this: list[Linefill__ren__]):
        return deleteAll(this)

    @export
    @overload
    @method
    def delete(this: list[Box__ren__]):
        return deleteAll(this)

    @export
    @overload
    @method
    def clear(this: list[Line__ren__]):
        return clear(delete(this))

    @export
    @overload
    @method
    def clear(this: list[Label__ren__]):
        return clear(delete(this))

    @export
    @overload
    @method
    def clear(this: list[Linefill__ren__]):
        return clear(delete(this))

    @export
    @overload
    @method
    def clear(this: list[Box__ren__]):
        return clear(delete(this))

    @export
    @overload
    @method
    def draw(this: Line__ren__):
        line.delete(this.object)
        this.properties = LineProperties() if na(this.properties) else this.properties
        if this.properties.force_overlay:
            this.object = line.new(this.start.index if this.properties.xloc__ren__ == xloc.bar_index else this.start.time, this.start.price, this.end.index if this.properties.xloc__ren__ == xloc.bar_index else this.end.time, this.end.price, this.properties.xloc__ren__, this.properties.extend__ren__, this.properties.color__ren__, this.properties.style, this.properties.width, True)
        else:
            this.object = line.new(this.start.index if this.properties.xloc__ren__ == xloc.bar_index else this.start.time, this.start.price, this.end.index if this.properties.xloc__ren__ == xloc.bar_index else this.end.time, this.end.price, this.properties.xloc__ren__, this.properties.extend__ren__, this.properties.color__ren__, this.properties.style, this.properties.width)
        return this.object

    @export
    @overload
    @method
    def draw(this: list[Line__ren__]):
        if not na(this):
            for ln in this:
                draw(ln)
        return this

    @export
    @overload
    @method
    def draw(this: Label__ren__):
        label.delete(this.object)
        this.properties = LabelProperties() if na(this.properties) else this.properties
        if this.properties.force_overlay:
            this.object = label.new(this.point.index if this.properties.xloc__ren__ == xloc.bar_index else this.point.time, this.point.price, this.lblText, this.properties.xloc__ren__, this.properties.yloc__ren__, this.properties.color__ren__, this.properties.style, this.properties.textcolor, this.properties.size__ren__, this.properties.textalign, this.tooltip, this.properties.text_font_family, True)
        else:
            this.object = label.new(this.point.index if this.properties.xloc__ren__ == xloc.bar_index else this.point.time, this.point.price, this.lblText, this.properties.xloc__ren__, this.properties.yloc__ren__, this.properties.color__ren__, this.properties.style, this.properties.textcolor, this.properties.size__ren__, this.properties.textalign, this.tooltip, this.properties.text_font_family)
        return this.object

    @export
    @overload
    @method
    def draw(this: list[Label__ren__]):
        if not na(this):
            for lbl in this:
                draw(lbl)
        return this

    @export
    @overload
    @method
    def draw(this: Linefill__ren__):
        if not na(this.line1) and (not na(this.line2)) and (not na(this.line1.object)) and (not na(this.line2.object)):
            this.object = linefill.new(this.line1.object, this.line2.object, color.new(this.fillColor, this.transparency))
        return this.object

    @export
    @overload
    @method
    def draw(this: list[Linefill__ren__]):
        if not na(this):
            for lfl in this:
                draw(lfl)
        return this

    @export
    @overload
    @method
    def draw(this: Box__ren__):
        box.delete(this.object)
        this.properties = BoxProperties() if na(this.properties) else this.properties
        top = math.max(this.p1.price, this.p2.price)
        bottom = math.min(this.p1.price, this.p2.price)
        left = math.min(this.p1.index, this.p2.index) if this.properties.xloc__ren__ == xloc.bar_index else math.min(this.p1.time, this.p2.time)
        right = math.max(this.p1.index, this.p2.index) if this.properties.xloc__ren__ == xloc.bar_index else math.max(this.p1.time, this.p2.time)

        if this.properties.force_overlay:
            this.object = box.new(left, top, right, bottom, this.properties.border_color, this.properties.border_width, this.properties.border_style, this.properties.extend__ren__, this.properties.xloc__ren__, this.properties.bgcolor__ren__) if na(this.textProperties) else box.new(left, top, right, bottom, this.properties.border_color, this.properties.border_width, this.properties.border_style, this.properties.extend__ren__, this.properties.xloc__ren__, this.properties.bgcolor__ren__, this.textProperties.boxText, this.textProperties.text_size, this.textProperties.text_color, this.textProperties.text_halign, this.textProperties.text_valign, this.textProperties.text_wrap, this.textProperties.text_font_family, True)
        else:
            this.object = box.new(left, top, right, bottom, this.properties.border_color, this.properties.border_width, this.properties.border_style, this.properties.extend__ren__, this.properties.xloc__ren__, this.properties.bgcolor__ren__) if na(this.textProperties) else box.new(left, top, right, bottom, this.properties.border_color, this.properties.border_width, this.properties.border_style, this.properties.extend__ren__, this.properties.xloc__ren__, this.properties.bgcolor__ren__, this.textProperties.boxText, this.textProperties.text_size, this.textProperties.text_color, this.textProperties.text_halign, this.textProperties.text_valign, this.textProperties.text_wrap, this.textProperties.text_font_family)

        return this.object

    @export
    @overload
    @method
    def draw(this: list[Box__ren__]):
        if not na(this):
            for bx in this:
                draw(bx)
        return this

    @export
    @method
    def createLabel(this: ChartPoint, lblText: str, tooltip: str = na, properties: LabelProperties = na):
        return Label__ren__(this, lblText, tooltip, LabelProperties() if na(properties) else properties)

    @export
    @method
    def createLine(this: ChartPoint, other: ChartPoint, properties: LineProperties = na):
        return Line__ren__(this, other, LineProperties() if na(properties) else properties)

    @export
    @method
    def createLinefill(this: Line__ren__, other: Line__ren__, fillColor: Color = color.blue, transparency: int = 80):
        return Linefill__ren__(this, other, fillColor, transparency)

    @export
    @overload
    @method
    def createBox(this: ChartPoint, other: ChartPoint, properties: BoxProperties = na, textProperties: BoxText = na):
        return Box__ren__(this, other, BoxProperties() if na(properties) else properties, textProperties)

    @export
    @overload
    @method
    def createBox(this: Line__ren__, properties: BoxProperties = na, textProperties: BoxText = na):
        return Box__ren__(this.start, this.end, BoxProperties() if na(properties) else properties, textProperties)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
