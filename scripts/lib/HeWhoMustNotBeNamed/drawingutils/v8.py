"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    array, bar_index, barstate, box, color, extend, label, line, linefill,
    math, na, position, script, size, string, table, text, time, xloc, yloc
)
from pynecore.types import Box, Color, Label, Line, LineFill, Persistent
from typing import Protocol, Any
import lib.HeWhoMustNotBeNamed.utils.v1 as ut


__all__ = ['draw_label', 'draw_labelled_box', 'draw_labelled_line', 'draw_line', 'draw_linefill', 'runTimer', 'watermark']


class _ProtocolDrawLine(Protocol):
    def __call__(self, y1: float, y2: float, x1: int, x2: int, lineColor: Color, width: int, style: str, linesArray: list[Line]) -> Any: ...


class _ProtocolDrawLabel(Protocol):
    def __call__(self, y: float, x: int, txt: str, textcolor: Color, style: str, yloc__ren__: str, size__ren__: str, labelsArray: list[Label]) -> Any: ...


class _ProtocolDrawLinefill(Protocol):
    def __call__(self, ln1: Line, ln2: Line, fillColor: Color, transparency: int, lineFillArray: list[LineFill]) -> Any: ...


class _ProtocolDrawLabelledLine(Protocol):
    def __call__(self, target: float, lblText: str, linecolor: Color, labelcolor: Color, index: int, highlight: bool, linesArray: list[Line], labelsArray: list[Label], normalSize: str = size.normal, tinySize: str = size.tiny, yloc__ren__: str = yloc.price) -> Any: ...


class _ProtocolDrawLabelledBox(Protocol):
    def __call__(self, y1: float, y2: float, labelColor: Color, labelText: str, index: int, boxArray: list[Box], labelArray: list[Label], borderColor: Color = color.blue, borderStyle: str = line.style_dotted, borderWidth: int = 1, textAlign: str = text.align_right, highlight: bool = True, highLightLabel: bool = False) -> Any: ...


class _ProtocolRuntimer(Protocol):
    def __call__(self, timerPosition: str = position.top_center, backgroundColor: Color = color.green, textColor: Color = color.white, lblSize: str = size.small) -> Any: ...


class _ProtocolWatermark(Protocol):
    def __call__(self, content: str, tblPosition: str = position.middle_center, textColor: Color = color.aqua, transparency: int = 80, textSize: str = size.huge) -> Any: ...


draw_line: _ProtocolDrawLine = Exported()
draw_label: _ProtocolDrawLabel = Exported()
draw_linefill: _ProtocolDrawLinefill = Exported()
draw_labelled_line: _ProtocolDrawLabelledLine = Exported()
draw_labelled_box: _ProtocolDrawLabelledBox = Exported()
runTimer: _ProtocolRuntimer = Exported()
watermark: _ProtocolWatermark = Exported()


@script.library('drawingutils')
def main():
    @export
    def draw_line(y1: float, y2: float, x1: int, x2: int, lineColor: Color, width: int, style: str, linesArray: list[Line]):
        targetLine = line.new(y1=y1, y2=y2, x1=x1, x2=x2, color=lineColor, width=width, style=style)
        array.push(linesArray, targetLine)
        return targetLine

    @export
    def draw_label(y: float, x: int, txt: str, textcolor: Color, style: str, yloc__ren__: str, size__ren__: str, labelsArray: list[Label]):
        targetLabel = label.new(y=y, x=x, text=txt, textcolor=textcolor, style=style, yloc=yloc__ren__, size=size__ren__)
        return array.push(labelsArray, targetLabel)

    @export
    def draw_linefill(ln1: Line, ln2: Line, fillColor: Color, transparency: int, lineFillArray: list[LineFill]):
        lnfl = linefill.new(ln1, ln2, color.new(fillColor, transparency))
        return array.push(lineFillArray, lnfl)

    @export
    def draw_labelled_line(target: float, lblText: str, linecolor: Color, labelcolor: Color, index: int, highlight: bool, linesArray: list[Line], labelsArray: list[Label], normalSize: str = size.normal, tinySize: str = size.tiny, yloc__ren__: str = yloc.price):
        x1 = bar_index + 20 * index * 2
        x2 = x1 + 20
        xloc__ren__ = xloc.bar_index
        style = label.style_none if yloc__ren__ == yloc.price else label.style_label_down if yloc__ren__ == yloc.abovebar else label.style_label_up
        targetLine = line.new(x1=x1, y1=target, x2=x2, y2=target, color=linecolor, xloc=xloc__ren__, extend=extend.none, style=line.style_solid if highlight else line.style_dotted)
        targetLabel = label.new(x=(x1 + x2) / 2, y=target, text=lblText + '\n' + string.tostring(math.round_to_mintick(target)), xloc=xloc__ren__, style=style, textcolor=labelcolor if highlight else color.new(labelcolor, 70), size=normalSize if highlight else tinySize, color=color.new(labelcolor, 100))
        array.push(linesArray, targetLine)
        return array.push(labelsArray, targetLabel)

    @export
    def draw_labelled_box(y1: float, y2: float, labelColor: Color, labelText: str, index: int, boxArray: list[Box], labelArray: list[Label], borderColor: Color = color.blue, borderStyle: str = line.style_dotted, borderWidth: int = 1, textAlign: str = text.align_right, highlight: bool = True, highLightLabel: bool = False):
        x1 = bar_index + 20 * index * 2
        x2 = x1 + 20
        y = (y1 + y2) / 2
        transp = 70 if highlight else 90
        transpLabel = 0 if highlight else 50
        labelSize = size.normal if highLightLabel else size.small
        bx = box.new(x1, y1, x2, y2, borderColor, borderWidth, borderStyle, bgcolor=color.new(labelColor, transp))
        lbl = label.new(x=x2, y=y, text=labelText, yloc=yloc.price, color=labelColor, style=label.style_none, textcolor=color.new(labelColor, transpLabel), size=labelSize, textalign=textAlign)
        array.push(labelArray, lbl)
        return array.push(boxArray, bx)

    @export
    def runTimer(timerPosition: str = position.top_center, backgroundColor: Color = color.green, textColor: Color = color.white, lblSize: str = size.small):
        startBar: Persistent = bar_index
        startTime: Persistent = time
        barDiff = bar_index - startBar
        days, tHours, tMinutes, tSeconds, tmSeconds = ut.timer(startTime)
        __block_result__ = na
        if barstate.islast:
            timer: Persistent = table.new(position=timerPosition, columns=12, rows=1, border_width=0)
            table.cell(table_id=timer, column=0, row=0, text=string.tostring(days, '00'), bgcolor=backgroundColor, text_color=textColor, text_size=lblSize)
            table.cell(table_id=timer, column=1, row=0, text='/', bgcolor=backgroundColor, text_color=textColor, text_size=lblSize)
            table.cell(table_id=timer, column=2, row=0, text=string.tostring(tHours, '00'), bgcolor=backgroundColor, text_color=textColor, text_size=lblSize)
            table.cell(table_id=timer, column=3, row=0, text=':', bgcolor=backgroundColor, text_color=textColor, text_size=lblSize)
            table.cell(table_id=timer, column=4, row=0, text=string.tostring(tMinutes, '00'), bgcolor=backgroundColor, text_color=textColor, text_size=lblSize)
            table.cell(table_id=timer, column=5, row=0, text=':', bgcolor=backgroundColor, text_color=textColor, text_size=lblSize)
            table.cell(table_id=timer, column=6, row=0, text=string.tostring(tSeconds, '00'), bgcolor=backgroundColor, text_color=textColor, text_size=lblSize)
            table.cell(table_id=timer, column=7, row=0, text='.', bgcolor=backgroundColor, text_color=textColor, text_size=lblSize)
            table.cell(table_id=timer, column=8, row=0, text=string.tostring(tmSeconds), bgcolor=backgroundColor, text_color=textColor, text_size=lblSize)
            table.cell(table_id=timer, column=9, row=0, text='[', bgcolor=backgroundColor, text_color=textColor, text_size=lblSize)
            table.cell(table_id=timer, column=10, row=0, text=string.tostring(barDiff), bgcolor=backgroundColor, text_color=textColor, text_size=lblSize)
            __block_result__ = table.cell(table_id=timer, column=11, row=0, text=']', bgcolor=backgroundColor, text_color=textColor, text_size=lblSize)
        return __block_result__

    @export
    def watermark(content: str, tblPosition: str = position.middle_center, textColor: Color = color.aqua, transparency: int = 80, textSize: str = size.huge):
        __block_result_1__ = na
        if barstate.islast:
            watermark__00000035__: Persistent = table.new(position=tblPosition, columns=1, rows=1, border_width=0)
            __block_result_1__ = table.cell(table_id=watermark__00000035__, column=0, row=0, text=content, text_color=color.new(textColor, transparency), text_size=textSize)
        return __block_result_1__


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
