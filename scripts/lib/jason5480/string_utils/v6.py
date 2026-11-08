"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method
from pynecore.lib import (
    bar_index, barstate, chart, close, color, label, log, map, math, na,
    open, position, script, size, string, syminfo, table, text, yloc
)
from pynecore.types import Color, Persistent, Table
from typing import Protocol, Any


__all__ = ['announce', 'desteganographize', 'fill__ren__', 'indent', 'legend', 'replace', 'replace_all']


class _ProtocolReplace(Protocol):
    def __call__(self, this: str, stringToStringMap: dict[str, str]) -> Any: ...


class _ProtocolReplace1(Protocol):
    def __call__(self, this: str, stringToStringMap: dict[str, str]) -> Any: ...


class _ProtocolReplace2(Protocol):
    def __call__(self, this: str, stringToNumMap: dict[str, float]) -> Any: ...


class _ProtocolReplace3(Protocol):
    def __call__(self, this: str, stringToNumMap: dict[str, float]) -> Any: ...


class _ProtocolReplaceAll(Protocol):
    def __call__(self, this: str, stringToStringMap: dict[str, str]) -> Any: ...


class _ProtocolReplaceAll5(Protocol):
    def __call__(self, this: str, stringToStringMap: dict[str, str]) -> Any: ...


class _ProtocolReplaceAll6(Protocol):
    def __call__(self, this: str, stringToNumMap: dict[str, float]) -> Any: ...


class _ProtocolReplaceAll7(Protocol):
    def __call__(self, this: str, stringToNumMap: dict[str, float]) -> Any: ...


class _ProtocolIndent(Protocol):
    def __call__(self, this: str, size__ren__: int) -> Any: ...


class _ProtocolIndent9(Protocol):
    def __call__(self, this: str, size__ren__: int) -> Any: ...


class _ProtocolFill(Protocol):
    def __call__(self, this: str, size__ren__: int) -> Any: ...


class _ProtocolFill11(Protocol):
    def __call__(self, this: str, size__ren__: int) -> Any: ...


class _ProtocolDesteganographize(Protocol):
    def __call__(self, this: str) -> Any: ...


class _ProtocolAnnounce(Protocol):
    def __call__(self, this: str, height: float = 0.0, textColor: Color = chart.fg_color, textSize: str = size.large, position__ren__: str = position.top_center) -> Any: ...


class _ProtocolAnnounce14(Protocol):
    def __call__(self, this: str, height: float = 0.0, textColor: Color = chart.fg_color, textSize: str = size.large, position__ren__: str = position.top_center) -> Any: ...


class _ProtocolLegend(Protocol):
    def __call__(self, this: dict[str, str], maxRows: int = 3, height: float = 0.0, textColor: Color = chart.fg_color, textSize: str = size.small, position__ren__: str = position.bottom_center) -> Any: ...


replace: _ProtocolReplace = Exported()
replace: _ProtocolReplace1 = Exported()
replace: _ProtocolReplace2 = Exported()
replace: _ProtocolReplace3 = Exported()
replace_all: _ProtocolReplaceAll = Exported()
replace_all: _ProtocolReplaceAll5 = Exported()
replace_all: _ProtocolReplaceAll6 = Exported()
replace_all: _ProtocolReplaceAll7 = Exported()
indent: _ProtocolIndent = Exported()
indent: _ProtocolIndent9 = Exported()
fill__ren__: _ProtocolFill = Exported()
fill__ren__: _ProtocolFill11 = Exported()
desteganographize: _ProtocolDesteganographize = Exported()
announce: _ProtocolAnnounce = Exported()
announce: _ProtocolAnnounce14 = Exported()
legend: _ProtocolLegend = Exported()

EMSP: str = ' '
ZWSP: str = '​'
ZWNJ: str = '‌'
WJ: str = '⁠'
ZWNBSP: str = '﻿'
greet: str = 'Hello my na‌​​‌​​‌⁠‌​​​​​⁠‌‌‌​‌​​⁠‌‌‌​​‌​⁠‌‌​‌​​‌⁠‌‌​​​‌‌⁠‌‌​‌​‌‌⁠‌‌​​‌​‌⁠‌‌​​‌​​⁠‌​​​​​⁠‌‌‌‌​​‌⁠‌‌​‌‌‌‌⁠‌‌‌​‌​‌⁠‌​‌‌​​⁠‌​​​​​⁠‌‌​‌‌​‌⁠‌‌‌‌​​‌⁠‌​​​​​⁠‌‌​‌‌‌​⁠‌‌​​​​‌⁠‌‌​‌‌​‌⁠‌‌​​‌​‌⁠‌​​​​​⁠‌‌​‌​​‌⁠‌‌‌​​‌‌⁠‌​​​​​⁠‌​​‌​‌​⁠‌‌​​​​‌⁠‌‌‌​​‌‌⁠‌‌​‌‌‌‌⁠‌‌​‌‌‌​⁠‌​​​​‌me is Nick!'


@script.library(title='string_utils')
def main():
    @export
    @overload
    @method
    def replace(this: str, stringToStringMap: dict[str, str]):
        outStr: str = this
        for key, value in stringToStringMap.items():
            if not na(value):
                outStr = string.replace(outStr, key, value)
        return outStr

    @export
    @overload
    @method
    def replace(this: str, stringToStringMap: dict[str, str]):
        outStr: str = this
        for key, value in stringToStringMap.items():
            if not na(value):
                outStr = string.replace(outStr, key, value)
        return outStr

    @export
    @overload
    @method
    def replace(this: str, stringToNumMap: dict[str, float]):
        outStr: str = this
        for key, value in stringToNumMap.items():
            if not na(value):
                outStr = string.replace(outStr, key, string.tostring(value))
        return outStr

    @export
    @overload
    @method
    def replace(this: str, stringToNumMap: dict[str, float]):
        outStr: str = this
        for key, value in stringToNumMap.items():
            if not na(value):
                outStr = string.replace(outStr, key, string.tostring(value))
        return outStr

    @export
    @overload
    @method
    def replace_all(this: str, stringToStringMap: dict[str, str]):
        outStr: str = this
        for key, value in stringToStringMap.items():
            if not na(value):
                outStr = string.replace_all(outStr, key, value)
        return outStr

    @export
    @overload
    @method
    def replace_all(this: str, stringToStringMap: dict[str, str]):
        outStr: str = this
        for key, value in stringToStringMap.items():
            if not na(value):
                outStr = string.replace_all(outStr, key, value)
        return outStr

    @export
    @overload
    @method
    def replace_all(this: str, stringToNumMap: dict[str, float]):
        outStr: str = this
        for key, value in stringToNumMap.items():
            if not na(value):
                outStr = string.replace_all(outStr, key, string.tostring(value))
        return outStr

    @export
    @overload
    @method
    def replace_all(this: str, stringToNumMap: dict[str, float]):
        outStr: str = this
        for key, value in stringToNumMap.items():
            if not na(value):
                outStr = string.replace_all(outStr, key, string.tostring(value))
        return outStr

    @overload
    @method
    def repeat(this: str, num: int):
        tempStr: str = ''
        for i in pine_range(0, num - 1 if num > 0 else na):
            tempStr = tempStr + this
        return tempStr

    @overload
    @method
    def repeat(this: str, num: int):
        tempStr: str = ''
        for i in pine_range(0, num - 1 if num > 0 else na):
            tempStr = tempStr + this
        return tempStr


    @export
    @overload
    @method
    def indent(this: str, size__ren__: int):
        return repeat(EMSP, size__ren__) + this

    @export
    @overload
    @method
    def indent(this: str, size__ren__: int):
        return repeat(EMSP, size__ren__) + this

    @export
    @overload
    @method
    def fill__ren__(this: str, size__ren__: int):
        return this + repeat(EMSP, size__ren__)

    @export
    @overload
    @method
    def fill__ren__(this: str, size__ren__: int):
        return this + repeat(EMSP, size__ren__)

    def getLexicon():
        LEXICON: dict[str, str] = map.new()

        map.put(LEXICON, '\u200c\u200c\u200b\u200b\u200b\u200b\u200c', 'a')
        map.put(LEXICON, '\u200c\u200c\u200b\u200b\u200b\u200c\u200b', 'b')
        map.put(LEXICON, '\u200c\u200c\u200b\u200b\u200b\u200c\u200c', 'c')
        map.put(LEXICON, '\u200c\u200c\u200b\u200b\u200c\u200b\u200b', 'd')
        map.put(LEXICON, '\u200c\u200c\u200b\u200b\u200c\u200b\u200c', 'e')
        map.put(LEXICON, '\u200c\u200c\u200b\u200b\u200c\u200c\u200b', 'f')
        map.put(LEXICON, '\u200c\u200c\u200b\u200b\u200c\u200c\u200c', 'g')
        map.put(LEXICON, '\u200c\u200c\u200b\u200c\u200b\u200b\u200b', 'h')
        map.put(LEXICON, '\u200c\u200c\u200b\u200c\u200b\u200b\u200c', 'i')
        map.put(LEXICON, '\u200c\u200c\u200b\u200c\u200b\u200c\u200b', 'j')
        map.put(LEXICON, '\u200c\u200c\u200b\u200c\u200b\u200c\u200c', 'k')
        map.put(LEXICON, '\u200c\u200c\u200b\u200c\u200c\u200b\u200b', 'l')
        map.put(LEXICON, '\u200c\u200c\u200b\u200c\u200c\u200b\u200c', 'm')
        map.put(LEXICON, '\u200c\u200c\u200b\u200c\u200c\u200c\u200b', 'n')
        map.put(LEXICON, '\u200c\u200c\u200b\u200c\u200c\u200c\u200c', 'o')
        map.put(LEXICON, '\u200c\u200c\u200c\u200b\u200b\u200b\u200b', 'p')
        map.put(LEXICON, '\u200c\u200c\u200c\u200b\u200b\u200b\u200c', 'q')
        map.put(LEXICON, '\u200c\u200c\u200c\u200b\u200b\u200c\u200b', 'r')
        map.put(LEXICON, '\u200c\u200c\u200c\u200b\u200b\u200c\u200c', 's')
        map.put(LEXICON, '\u200c\u200c\u200c\u200b\u200c\u200b\u200b', 't')
        map.put(LEXICON, '\u200c\u200c\u200c\u200b\u200c\u200b\u200c', 'u')
        map.put(LEXICON, '\u200c\u200c\u200c\u200b\u200c\u200c\u200b', 'v')
        map.put(LEXICON, '\u200c\u200c\u200c\u200b\u200c\u200c\u200c', 'w')
        map.put(LEXICON, '\u200c\u200c\u200c\u200c\u200b\u200b\u200b', 'x')

        map.put(LEXICON, '\u200c\u200b\u200b\u200b\u200b\u200b\u200c', 'A')
        map.put(LEXICON, '\u200c\u200b\u200b\u200b\u200b\u200c\u200b', 'B')
        map.put(LEXICON, '\u200c\u200b\u200b\u200b\u200b\u200c\u200c', 'C')
        map.put(LEXICON, '\u200c\u200b\u200b\u200b\u200c\u200b\u200b', 'D')
        map.put(LEXICON, '\u200c\u200b\u200b\u200b\u200c\u200b\u200c', 'E')
        map.put(LEXICON, '\u200c\u200b\u200b\u200b\u200c\u200c\u200b', 'F')
        map.put(LEXICON, '\u200c\u200b\u200b\u200b\u200c\u200c\u200c', 'G')
        map.put(LEXICON, '\u200c\u200b\u200b\u200c\u200b\u200b\u200b', 'H')
        map.put(LEXICON, '\u200c\u200b\u200b\u200c\u200b\u200b\u200c', 'I')
        map.put(LEXICON, '\u200c\u200b\u200b\u200c\u200b\u200c\u200b', 'J')
        map.put(LEXICON, '\u200c\u200b\u200b\u200c\u200b\u200c\u200c', 'K')
        map.put(LEXICON, '\u200c\u200b\u200b\u200c\u200c\u200b\u200b', 'L')
        map.put(LEXICON, '\u200c\u200b\u200b\u200c\u200c\u200b\u200c', 'M')
        map.put(LEXICON, '\u200c\u200b\u200b\u200c\u200c\u200c\u200b', 'N')
        map.put(LEXICON, '\u200c\u200b\u200b\u200c\u200c\u200c\u200c', 'O')
        map.put(LEXICON, '\u200c\u200b\u200c\u200b\u200b\u200b\u200b', 'P')
        map.put(LEXICON, '\u200c\u200b\u200c\u200b\u200b\u200b\u200c', 'Q')
        map.put(LEXICON, '\u200c\u200b\u200c\u200b\u200b\u200c\u200b', 'R')
        map.put(LEXICON, '\u200c\u200b\u200c\u200b\u200b\u200c\u200c', 'S')
        map.put(LEXICON, '\u200c\u200b\u200c\u200b\u200c\u200b\u200b', 'T')
        map.put(LEXICON, '\u200c\u200b\u200c\u200b\u200c\u200b\u200c', 'U')
        map.put(LEXICON, '\u200c\u200b\u200c\u200b\u200c\u200c\u200b', 'V')
        map.put(LEXICON, '\u200c\u200b\u200c\u200b\u200c\u200c\u200c', 'W')
        map.put(LEXICON, '\u200c\u200b\u200c\u200c\u200b\u200b\u200b', 'X')
        map.put(LEXICON, '\u200c\u200b\u200c\u200c\u200b\u200b\u200c', 'Y')
        map.put(LEXICON, '\u200c\u200b\u200c\u200c\u200b\u200c\u200b', 'Z')
        map.put(LEXICON, '\u200c\u200c\u200c\u200c\u200b\u200b\u200c', 'y')
        map.put(LEXICON, '\u200c\u200c\u200c\u200c\u200b\u200c\u200b', 'z')

        map.put(LEXICON, '\u200c\u200c\u200b\u200b\u200b\u200b', '0')
        map.put(LEXICON, '\u200c\u200c\u200b\u200b\u200b\u200c', '1')
        map.put(LEXICON, '\u200c\u200c\u200b\u200b\u200c\u200b', '2')
        map.put(LEXICON, '\u200c\u200c\u200b\u200b\u200c\u200c', '3')
        map.put(LEXICON, '\u200c\u200c\u200b\u200c\u200b\u200b', '4')
        map.put(LEXICON, '\u200c\u200c\u200b\u200c\u200b\u200c', '5')
        map.put(LEXICON, '\u200c\u200c\u200b\u200c\u200c\u200b', '6')
        map.put(LEXICON, '\u200c\u200c\u200b\u200c\u200c\u200c', '7')
        map.put(LEXICON, '\u200c\u200c\u200c\u200b\u200b\u200b', '8')
        map.put(LEXICON, '\u200c\u200c\u200c\u200b\u200b\u200c', '9')

        map.put(LEXICON, '\u200c\u200b\u200b\u200b\u200b\u200b', ' ')
        map.put(LEXICON, '\u200c\u200b\u200b\u200b\u200b\u200c', '!')
        map.put(LEXICON, '\u200c\u200b\u200b\u200b\u200c\u200b', '"')
        map.put(LEXICON, '\u200c\u200b\u200b\u200b\u200c\u200c', '#')
        map.put(LEXICON, '\u200c\u200b\u200b\u200c\u200b\u200b', '$')
        map.put(LEXICON, '\u200c\u200b\u200b\u200c\u200b\u200c', '%')
        map.put(LEXICON, '\u200c\u200b\u200b\u200c\u200c\u200b', '&')
        map.put(LEXICON, '\u200c\u200b\u200b\u200c\u200c\u200c', "'")
        map.put(LEXICON, '\u200c\u200b\u200c\u200b\u200b\u200b', '(')
        map.put(LEXICON, '\u200c\u200b\u200c\u200b\u200b\u200c', ')')
        map.put(LEXICON, '\u200c\u200b\u200c\u200b\u200c\u200b', '*')
        map.put(LEXICON, '\u200c\u200b\u200c\u200b\u200c\u200c', '+')
        map.put(LEXICON, '\u200c\u200b\u200c\u200c\u200b\u200b', ',')
        map.put(LEXICON, '\u200c\u200b\u200c\u200c\u200b\u200c', '-')
        map.put(LEXICON, '\u200c\u200b\u200c\u200c\u200c\u200b', '.')
        map.put(LEXICON, '\u200c\u200b\u200c\u200c\u200c\u200c', '/')
        map.put(LEXICON, '\u200c\u200c\u200c\u200b\u200c\u200b', ':')
        map.put(LEXICON, '\u200c\u200c\u200c\u200b\u200c\u200c', ';')
        map.put(LEXICON, '\u200c\u200c\u200c\u200c\u200b\u200b', '<')
        map.put(LEXICON, '\u200c\u200c\u200c\u200c\u200b\u200c', '=')
        map.put(LEXICON, '\u200c\u200c\u200c\u200c\u200c\u200b', '>')
        map.put(LEXICON, '\u200c\u200c\u200c\u200c\u200c\u200c', '?')
        map.put(LEXICON, '\u200c\u200b\u200b\u200b\u200b\u200b\u200b', '@')
        map.put(LEXICON, '\u200c\u200b\u200c\u200c\u200b\u200c\u200c', '[')
        map.put(LEXICON, '\u200c\u200b\u200c\u200c\u200c\u200b\u200b', '\\')
        map.put(LEXICON, '\u200c\u200b\u200c\u200c\u200c\u200b\u200c', ']')
        map.put(LEXICON, '\u200c\u200b\u200c\u200c\u200c\u200c\u200b', '^')
        map.put(LEXICON, '\u200c\u200b\u200c\u200c\u200c\u200c\u200c', '_')
        map.put(LEXICON, '\u200c\u200c\u200b\u200b\u200b\u200b\u200b', '`')
        map.put(LEXICON, '\u200c\u200c\u200c\u200c\u200b\u200c\u200c', '{')
        map.put(LEXICON, '\u200c\u200c\u200c\u200c\u200c\u200b\u200b', '|')
        map.put(LEXICON, '\u200c\u200c\u200c\u200c\u200c\u200b\u200c', '}')
        map.put(LEXICON, '\u200c\u200c\u200c\u200c\u200c\u200c\u200b', '~')
        map.put(LEXICON, '\u200c\u200c\u200c\u200c\u200c\u200c\u200c', 'DEL')

        map.put(LEXICON, '\u200c\u200c\u200b\u200b\u200b\u200b\u200c\u200b', '©')
        return LEXICON

    @export
    @method
    def desteganographize(this: str):
        message: str = this
        privStr: str = string.match(this, '[\u200b\u200c\u2060]+')
        if string.length(privStr) == 0:
            log.warning('No private message was detected in the given public message')
        else:
            LEXICON: Persistent[dict[str, str]] = getLexicon()
            privLetters: list[str] = string.split(privStr, WJ)
            message = ''
            for let in privLetters:
                message = message + map.get(LEXICON, let)
        return message

    @export
    @overload
    @method
    def announce(this: str, height: float = 0.0, textColor: Color = chart.fg_color, textSize: str = size.large, position__ren__: str = position.top_center):
        announceTable: Persistent[Table] = table.new(position=position__ren__, rows=1, columns=1, force_overlay=True)
        table.cell(announceTable, row=0, column=0, text=this, height=height, text_color=textColor, text_size=textSize)
        return announceTable

    @export
    @overload
    @method
    def announce(this: str, height: float = 0.0, textColor: Color = chart.fg_color, textSize: str = size.large, position__ren__: str = position.top_center):
        announceTable: Persistent[Table] = table.new(position=position__ren__, rows=1, columns=1, force_overlay=True)
        table.cell(announceTable, row=0, column=0, text=this, height=height, text_color=textColor, text_size=textSize if height == 0 else size.auto)
        return announceTable

    @export
    @method
    def legend(this: dict[str, str], maxRows: int = 3, height: float = 0.0, textColor: Color = chart.fg_color, textSize: str = size.small, position__ren__: str = position.bottom_center):
        rows: int = math.min(maxRows, map.size(this))
        columns: int = 2 * math.ceil(map.size(this) / rows)
        cellHeight: float = height / rows
        celTextSize: str = textSize if height == 0 else size.auto
        legendTable: Persistent[Table] = table.new(position=position__ren__, rows=rows, columns=columns, force_overlay=True)
        i: int = 0
        j: int = 0
        for sym, txt in this.items():
            table.cell(legendTable, row=i, column=j, text=sym, height=cellHeight, text_color=textColor, text_size=celTextSize, text_halign=text.align_right)
            table.cell(legendTable, row=i, column=j + 1, text=txt, height=cellHeight, text_color=textColor, text_size=celTextSize, text_halign=text.align_left)
            i += 1
            if i >= rows:
                i = 0
                j += 2
        return legendTable

    var1: float = 1.001
    var2: float = 2.999
    var3: int = bar_index
    var4: float = 0.02001

    stringToStringMap: Persistent[dict[str, str]] = map.new()
    map.put(stringToStringMap, '{{ticker}}', syminfo.ticker)
    stringToNumMap: Persistent[dict[str, float]] = map.new()
    map.put(stringToNumMap, '{{var1}}', var1)
    map.put(stringToNumMap, '{{var2}}', var2)
    map.put(stringToNumMap, '{{var3}}', var3)
    map.put(stringToNumMap, '{{var4}}', var4)

    message: Persistent[str] = 'Ticker = {{ticker}}\nVar1 = {{var1}}\n Var2 = {{var2}}\nVar3 = {{var3}}\n {{var4}}'
    varMessage: Persistent[str] = replace_all(message, stringToStringMap)
    outMessage: str = indent(replace(varMessage, stringToNumMap), 2)

    if barstate.isfirst:
        log.info('The public mesage is: "{0}", while the private message is: "{1}"', greet, desteganographize(greet))
        announce('Hello World!')
        numbersMap: dict[str, str] = map.new()
        map.put(numbersMap, '1', 'one')
        map.put(numbersMap, '2', 'two')
        map.put(numbersMap, '3', 'three')
        map.put(numbersMap, '4', 'four')
        map.put(numbersMap, '5', 'five')
        map.put(numbersMap, '6', 'six')
        legend(numbersMap)

    if barstate.islastconfirmedhistory:
        label.new(x=bar_index, y=na, text=message, yloc=yloc.abovebar, color=color.red, style=label.style_label_down, textcolor=color.new(color.white, 0), force_overlay=True)
        label.new(x=bar_index, y=close, text=varMessage, yloc=yloc.price, color=color.orange, style=label.style_label_up if close > open else label.style_label_down, textcolor=color.new(color.white, 0), force_overlay=True)
        label.new(x=bar_index, y=na, text=outMessage, yloc=yloc.belowbar, color=color.green, style=label.style_label_up, textcolor=color.new(color.white, 0), force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
