"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt, udt_copy
from pynecore.lib import (
    array, chart, close, color, dayofmonth, dayofweek, extend, font, high,
    hour, label, line, low, map, math, matrix, minute, month, na, open, position, script, size,
    string, syminfo, table, time, time_close, timeframe, timenow, xloc, year
)
from pynecore.types import Color, Label, Line, Matrix, NA, Persistent, Table
from typing import Protocol, Any


__all__ = ['FF_OnChartLabel', 'FF_OnChartLine', 'FF_Table', 'MMM', 'News', 'NewsAMPM_TOD', 'adjustTimezone', 'boxLoc', 'bubbleSort_News', 'bubbleSort_NewsTOD', 'curFilter', 'daysMonth', 'dow', 'historical', 'impFilter', 'isLeapYear', 'lineStyle', 'lineTrnsp', 'logNews', 'newTable', 'resetTable', 'size__ren__', 'timeline', 'todayNews', 'updateStringMatrix', 'weekNews']


@udt
class News:
    dow: str = na(str)
    dat: str = na(str)
    _t: int = na(int)
    tod: str = na(str)
    cur: str = na(str)
    imp: Color = na(Color)
    ttl: str = na(str)
    tmst: int = na(int)
    ln: Line = na(Line)


class _ProtocolIsleapyear(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolDaysmonth(Protocol):
    def __call__(self, M: int) -> Any: ...


class _ProtocolMmm(Protocol):
    def __call__(self, M: int) -> Any: ...


class _ProtocolDow(Protocol):
    def __call__(self, D: str) -> Any: ...


class _ProtocolSize(Protocol):
    def __call__(self, S: str, N: int = na) -> Any: ...


class _ProtocolLinestyle(Protocol):
    def __call__(self, S: str) -> Any: ...


class _ProtocolLinetrnsp(Protocol):
    def __call__(self, S: str) -> Any: ...


class _ProtocolBoxloc(Protocol):
    def __call__(self, X: str, Y: str) -> Any: ...


class _ProtocolBubblesortNewstod(Protocol):
    def __call__(self, N: list[News]) -> Any: ...


class _ProtocolBubblesortNews(Protocol):
    def __call__(self, N: list[News]) -> Any: ...


class _ProtocolWeeknews(Protocol):
    def __call__(self, N: list[News], C: list[str], I: list[Color]) -> Any: ...


class _ProtocolTodaynews(Protocol):
    def __call__(self, W: list[News], D: list[News], M: bool) -> Any: ...


class _ProtocolAdjusttimezone(Protocol):
    def __call__(self, N: list[News], TZH: int, TZM: int) -> Any: ...


class _ProtocolNewsampmTod(Protocol):
    def __call__(self, N: list[News]) -> Any: ...


class _ProtocolImpfilter(Protocol):
    def __call__(self, X: bool, L: bool, M: bool, H: bool) -> Any: ...


class _ProtocolCurfilter(Protocol):
    def __call__(self, A: bool, C1: bool, C2: bool, C3: bool, C4: bool, C5: bool, C6: bool, C7: bool, C8: bool, C9: bool) -> Any: ...


class _ProtocolFfOnchartline(Protocol):
    def __call__(self, N: list[News], T: int, S: str) -> Any: ...


class _ProtocolUpdatestringmatrix(Protocol):
    def __call__(self, M: Matrix[str], P: int, V: str) -> Any: ...


class _ProtocolFfOnchartlabel(Protocol):
    def __call__(self, N: list[News], Y: str, S: str, O: bool) -> Any: ...


class _ProtocolHistorical(Protocol):
    def __call__(self, T: int, D: bool, W: bool, X: str) -> Any: ...


class _ProtocolNewtable(Protocol):
    def __call__(self, P: str, B: Color = chart.fg_color) -> Any: ...


class _ProtocolResettable(Protocol):
    def __call__(self, P: str, S: str, headTextC: Color, headBgC: Color, B: Color) -> Any: ...


class _ProtocolLognews(Protocol):
    def __call__(self, N: News, TBL: Table, R: int, S: str, rowTextC: Color, rowBgC: Color) -> Any: ...


class _ProtocolFfTable(Protocol):
    def __call__(self, N: list[News], P: str, S: str, headTextC: Color, headBgC: Color, rowTextC: Color, rowBgC: Color, B: Color = chart.fg_color) -> Any: ...


class _ProtocolTimeline(Protocol):
    def __call__(self, N: list[News], T: Table, F: Color, TZH: int = na, TZM: int = na, D: bool = False) -> Any: ...


isLeapYear: _ProtocolIsleapyear = Exported()
daysMonth: _ProtocolDaysmonth = Exported()
MMM: _ProtocolMmm = Exported()
dow: _ProtocolDow = Exported()
size__ren__: _ProtocolSize = Exported()
lineStyle: _ProtocolLinestyle = Exported()
lineTrnsp: _ProtocolLinetrnsp = Exported()
boxLoc: _ProtocolBoxloc = Exported()
bubbleSort_NewsTOD: _ProtocolBubblesortNewstod = Exported()
bubbleSort_News: _ProtocolBubblesortNews = Exported()
weekNews: _ProtocolWeeknews = Exported()
todayNews: _ProtocolTodaynews = Exported()
adjustTimezone: _ProtocolAdjusttimezone = Exported()
NewsAMPM_TOD: _ProtocolNewsampmTod = Exported()
impFilter: _ProtocolImpfilter = Exported()
curFilter: _ProtocolCurfilter = Exported()
FF_OnChartLine: _ProtocolFfOnchartline = Exported()
updateStringMatrix: _ProtocolUpdatestringmatrix = Exported()
FF_OnChartLabel: _ProtocolFfOnchartlabel = Exported()
historical: _ProtocolHistorical = Exported()
newTable: _ProtocolNewtable = Exported()
resetTable: _ProtocolResettable = Exported()
logNews: _ProtocolLognews = Exported()
FF_Table: _ProtocolFfTable = Exported()
timeline: _ProtocolTimeline = Exported()


@script.library("forex_factory_utility")
def main():
    @export
    def isLeapYear():
        Y = year(time, 'America/New_York')
        return Y == 1980 or Y == 1984 or Y == 1988 or (Y == 1992) or (Y == 1996) or (Y == 2000) or (Y == 2004) or (Y == 2008) or (Y == 2012) or (Y == 2016) or (Y == 2020) or (Y == 2024) or (Y == 2028) or (Y == 2032) or (Y == 2036) or (Y == 2040) or (Y == 2044) or (Y == 2048) or (Y == 2052) or (Y == 2056) or (Y == 2060) or (Y == 2064) or (Y == 2068) or (Y == 2072) or (Y == 2076) or (Y == 2080) or (Y == 2084) or (Y == 2088) or (Y == 2092)

    @export
    def daysMonth(M: int):
        __block_result__ = na
        __switch__ = M
        if __switch__ == 1:
            __block_result__ = 31
        elif __switch__ == 2:
            __block_result__ = 29 if isLeapYear() else 28
        elif __switch__ == 3:
            __block_result__ = 31
        elif __switch__ == 4:
            __block_result__ = 30
        elif __switch__ == 5:
            __block_result__ = 31
        elif __switch__ == 6:
            __block_result__ = 30
        elif __switch__ == 7:
            __block_result__ = 31
        elif __switch__ == 8:
            __block_result__ = 31
        elif __switch__ == 9:
            __block_result__ = 30
        elif __switch__ == 10:
            __block_result__ = 31
        elif __switch__ == 11:
            __block_result__ = 30
        elif __switch__ == 12:
            __block_result__ = 31
        D = __block_result__
        return D

    @export
    def MMM(M: int):
        __block_result_1__ = na
        __switch__ = M
        if __switch__ == 1:
            __block_result_1__ = "Jan"
        elif __switch__ == 2:
            __block_result_1__ = "Feb"
        elif __switch__ == 3:
            __block_result_1__ = "Mar"
        elif __switch__ == 4:
            __block_result_1__ = "Apr"
        elif __switch__ == 5:
            __block_result_1__ = "May"
        elif __switch__ == 6:
            __block_result_1__ = "Jun"
        elif __switch__ == 7:
            __block_result_1__ = "Jul"
        elif __switch__ == 8:
            __block_result_1__ = "Aug"
        elif __switch__ == 9:
            __block_result_1__ = "Sep"
        elif __switch__ == 10:
            __block_result_1__ = "Oct"
        elif __switch__ == 11:
            __block_result_1__ = "Nov"
        elif __switch__ == 12:
            __block_result_1__ = "Dec"
        mmm = __block_result_1__
        return mmm

    @export
    def dow(D: str):
        __block_result_2__ = na
        __switch__ = D
        if __switch__ == "1":
            __block_result_2__ = "Sun"
        elif __switch__ == "2":
            __block_result_2__ = "Mon"
        elif __switch__ == "3":
            __block_result_2__ = "Tue"
        elif __switch__ == "4":
            __block_result_2__ = "Wed"
        elif __switch__ == "5":
            __block_result_2__ = "Thu"
        elif __switch__ == "6":
            __block_result_2__ = "Fri"
        elif __switch__ == "7":
            __block_result_2__ = "Sat"
        DOW = __block_result_2__
        return DOW


    @export
    def size__ren__(S: str, N: int = na):
        sizes: list[str] = array.new_string()
        array.push(sizes, size.tiny)
        array.push(sizes, size.small)
        array.push(sizes, size.normal)
        array.push(sizes, size.large)
        array.push(sizes, size.huge)
        __block_result_3__ = na
        __switch__ = S
        if __switch__ == "Tiny":
            __block_result_3__ = 0
        elif __switch__ == "Small":
            __block_result_3__ = 1
        elif __switch__ == "Normal":
            __block_result_3__ = 2
        elif __switch__ == "Large":
            __block_result_3__ = 3
        elif __switch__ == "Huge":
            __block_result_3__ = 4
        size__ren____00000038__ = __block_result_3__
        if not na(N):
            size__ren____00000038__ += N
            if size__ren____00000038__ > 4:
                size__ren____00000038__ = 4
            elif size__ren____00000038__ < 0:
                size__ren____00000038__ = 0

        return array.get(sizes, size__ren____00000038__)

    @export
    def lineStyle(S: str):
        __block_result_4__ = na
        __switch__ = S
        if __switch__ == "Dashed":
            __block_result_4__ = line.style_dashed
        elif __switch__ == "Dotted":
            __block_result_4__ = line.style_dotted
        elif __switch__ == "Solid":
            __block_result_4__ = line.style_solid
        style = __block_result_4__
        return style

    @export
    def lineTrnsp(S: str):
        __block_result_5__ = na
        __switch__ = S
        if __switch__ == "Light":
            __block_result_5__ = 80
        elif __switch__ == "Medium":
            __block_result_5__ = 50
        elif __switch__ == "Heavy":
            __block_result_5__ = 0
        transp = __block_result_5__
        return transp

    @export
    def boxLoc(X: str, Y: str):
        __block_result_6__ = na
        __switch__ = Y + X
        if __switch__ == "TopLeft":
            __block_result_6__ = position.top_left
        elif __switch__ == "TopCenter":
            __block_result_6__ = position.top_center
        elif __switch__ == "TopRight":
            __block_result_6__ = position.top_right
        elif __switch__ == "MiddleLeft":
            __block_result_6__ = position.middle_left
        elif __switch__ == "MiddleCenter":
            __block_result_6__ = position.middle_center
        elif __switch__ == "MiddleRight":
            __block_result_6__ = position.middle_right
        elif __switch__ == "BottomLeft":
            __block_result_6__ = position.bottom_left
        elif __switch__ == "BottomCenter":
            __block_result_6__ = position.bottom_center
        elif __switch__ == "BottomRight":
            __block_result_6__ = position.bottom_right
        loc = __block_result_6__
        return loc

    @export
    @method
    def bubbleSort_NewsTOD(N: list[News]):
        __block_result_7__ = na
        if array.size(N) > 2:
            __block_result_8__ = na
            for i in pine_range(0, array.size(N) - 2):
                __block_result_9__ = na
                for j in pine_range(0, array.size(N) - i - 2):
                    __block_result_10__ = na
                    if array.get(N, j)._t > array.get(N, j + 1)._t:
                        temp = array.get(N, j)
                        array.set(N, j, array.get(N, j + 1))
                        __block_result_10__ = array.set(N, j + 1, temp)
                    __block_result_9__ = __block_result_10__
                __block_result_8__ = __block_result_9__
            __block_result_7__ = __block_result_8__
        return __block_result_7__

    @export
    def bubbleSort_News(N: list[News]):
        sorted: list[News] = array.new(0, NA(News))
        temp: list[News] = array.new(0, NA(News))

        date: str = ""
        if array.size(N) > 0:
            for i in pine_range(0, array.size(N) - 1):
                n = array.get(N, i)
                if i == 0:
                    date = n.dat
                    array.push(temp, n)
                else:
                    if date == n.dat:
                        array.push(temp, n)
                    else:
                        date = n.dat
                        bubbleSort_NewsTOD(temp)
                        for j in pine_range(0, array.size(temp) - 1):
                            array.push(sorted, array.get(temp, j))
                        array.clear(temp)
                        array.push(temp, n)

        if array.size(temp) > 0:
            bubbleSort_NewsTOD(temp)
            for j in pine_range(0, array.size(temp) - 1):
                array.push(sorted, array.get(temp, j))
        return sorted

    @export
    def weekNews(N: list[News], C: list[str], I: list[Color]):
        W: list[News] = array.new(0, NA(News))
        if array.size(N) > 0:
            for i in pine_range(array.size(N) - 1, 0):
                n = array.get(N, i)
                if array.indexof(C, n.cur) != -1 and array.indexof(I, n.imp) != -1:
                    array.unshift(W, n)
        return W

    @export
    def todayNews(W: list[News], D: list[News], M: bool):
        if array.size(W) > 0:
            for i in pine_range(0, array.size(W) - 1):
                n = array.get(W, i)
                date = string.split(n.dat, '')
                if method_call('size', date) > 1:
                    tmp = method_call('slice', date, 3, method_call('size', date))
                    day = method_call('join', tmp)
                    if dayofmonth(time, 'America/New_York') + (0 if M else 1) == string.tonumber(day):
                        array.push(D, n)
        return D

    @export
    def adjustTimezone(N: list[News], TZH: int, TZM: int):
        tz = 'UTC' + ('+' if TZH > 0 else '-') + string.tostring(math.abs(TZH)) + (string.tostring(TZM) if TZM != 0 else '')
        if array.size(N) > 0:
            for i in pine_range(0, array.size(N) - 1):
                n = array.get(N, i)
                tmstmp = n.tmst
                tz_h = string.tostring(hour(tmstmp, tz))
                tz_m = string.tostring(minute(tmstmp, tz))
                n.dow = dow(string.tostring(dayofweek(tmstmp, tz)))
                n.dat = MMM(month(tmstmp, tz)) + ' ' + string.tostring(dayofmonth(tmstmp, tz))
                n.tod = tz_h + ':' + ('00' if tz_m == '0' else tz_m)
        return N

    @export
    def NewsAMPM_TOD(N: list[News]):
        if array.size(N) > 0:
            for i in pine_range(0, array.size(N) - 1):
                n = array.get(N, i)
                tod = string.split(n.tod, ':')
                if method_call('size', tod) > 1:
                    h = cast_int(string.tonumber(method_call('get', tod, 0)))
                    if h < 12:
                        n.tod = n.tod + 'am'
                    else:
                        n.tod = string.tostring(12 if h - 12 == 0 else h - 12) + ':' + method_call('get', tod, 1) + 'pm'
        return N

    @export
    def impFilter(X: bool, L: bool, M: bool, H: bool):
        I: list[Color] = array.new_color()
        if X:
            array.push(I, color.white)
        if L:
            array.push(I, color.yellow)
        if M:
            array.push(I, color.orange)
        if H:
            array.push(I, color.red)
        return I

    @export
    def curFilter(A: bool, C1: bool, C2: bool, C3: bool, C4: bool, C5: bool, C6: bool, C7: bool, C8: bool, C9: bool):
        C: list[str] = array.new_string()
        if A:
            if not na(syminfo.basecurrency):
                array.push(C, syminfo.basecurrency)
            if not na(syminfo.currency):
                array.push(C, syminfo.currency)
        else:
            if C1:
                array.push(C, 'AUD')
            if C2:
                array.push(C, 'CAD')
            if C3:
                array.push(C, 'CHF')
            if C4:
                array.push(C, 'CNY')
            if C5:
                array.push(C, 'EUR')
            if C6:
                array.push(C, 'GBP')
            if C7:
                array.push(C, 'JPY')
            if C8:
                array.push(C, 'NZD')
            if C9:
                array.push(C, 'USD')
        return C

    @export
    def FF_OnChartLine(N: list[News], T: int, S: str):
        tfms = timeframe.in_seconds(timeframe.period) * 1000
        lineColor: dict[int, Color] = map.new()
        colors: list[Color] = array.new_color()
        array.push(colors, color.white)
        array.push(colors, color.yellow)
        array.push(colors, color.orange)
        array.push(colors, color.red)
        __block_result_11__ = na
        if array.size(N) > 0:
            for i in pine_range(array.size(N) - 1, 0):
                n = array.get(N, i)
                adj = n.tmst - tfms if (n.tmst - time) % tfms != 0 else n.tmst
                if map.contains(lineColor, adj):
                    if array.indexof(colors, map.get(lineColor, adj)) < array.indexof(colors, n.imp):
                        map.put(lineColor, adj, n.imp)
                else:
                    map.put(lineColor, adj, n.imp)
            __block_result_12__ = na
            for i in pine_range(array.size(N) - 1, 0):
                n = array.get(N, i)
                adj = n.tmst - tfms if (n.tmst - time) % tfms != 0 else n.tmst
                n.ln = line.new(adj, low, adj, high, xloc.bar_time, extend.both, color.new(map.get(lineColor, adj), T), style=S)
                __block_result_12__ = n.ln
            __block_result_11__ = __block_result_12__
        return __block_result_11__

    @export
    @method
    def updateStringMatrix(M: Matrix[str], P: int, V: str):
        __block_result_13__ = na
        if matrix.rows(M) > P:
            _r = matrix.row(M, P)
            __block_result_14__ = na
            for i in pine_range(0, method_call('size', _r) - 1):
                __block_result_15__ = na
                if na(method_call('get', _r, i)):
                    matrix.set(M, P, i, V)
                    break
                __block_result_14__ = __block_result_15__
            __block_result_13__ = __block_result_14__
        return __block_result_13__

    @export
    def FF_OnChartLabel(N: list[News], Y: str, S: str, O: bool):
        checked: list[int] = array.new_int()
        __block_result_16__ = na
        if array.size(N) > 0:
            __block_result_17__ = na
            for i in pine_range(0, array.size(N) - 1):
                n = array.get(N, i)
                __block_result_18__ = na
                if n.tmst >= time and n.tmst < time_close:
                    events: Matrix[str] = matrix.new(4, 45, NA(str))
                    draw: bool = False
                    for k in pine_range(0, array.size(N) - 1):
                        b = array.get(N, k)
                        if array.indexof(checked, k) == -1 and b.tmst >= time and (b.tmst < time_close):
                            draw = True
                            array.push(checked, k)
                            __block_result_19__ = (na, na)
                            __switch_5__ = b.imp
                            if __switch_5__ == color.white:
                                __block_result_19__ = ("⚪ ", 0)
                            elif __switch_5__ == color.yellow:
                                __block_result_19__ = ("🟡 ", 1)
                            elif __switch_5__ == color.orange:
                                __block_result_19__ = ("🟠 ", 2)
                            elif __switch_5__ == color.red:
                                __block_result_19__ = ("🔴 ", 3)
                            imp, pos = __block_result_19__
                            if pos == 0:
                                updateStringMatrix(events, 0, imp + b.ttl + ' (' + b.cur + ')')
                            if pos == 1:
                                updateStringMatrix(events, 1, imp + b.ttl + ' (' + b.cur + ')')
                            if pos == 2:
                                updateStringMatrix(events, 2, imp + b.ttl + ' (' + b.cur + ')')
                            if pos == 3:
                                updateStringMatrix(events, 3, imp + b.ttl + ' (' + b.cur + ')')
                    __block_result_20__ = na
                    if draw:
                        txt: str = ""
                        _W: int = 0
                        _Y: int = 0
                        _O: int = 0
                        _R: int = 0
                        __loop_4__ = pine_loop(0)
                        while __loop_4__.step(matrix.rows(events) - 1):
                            r = __loop_4__.value
                            a = matrix.row(events, r)
                            if method_call('size', a) > 0:
                                for e in pine_range(0, method_call('size', a) - 1):
                                    if na(method_call('get', a, e)):
                                        break
                                    else:
                                        _W = 1 if r == 0 and _W == 0 else _W
                                        _Y = 1 if r == 1 and _Y == 0 else _Y
                                        _O = 1 if r == 2 and _O == 0 else _O
                                        _R = 1 if r == 3 and _R == 0 else _R
                                        txt = method_call('get', a, e) + '\n' + txt
                        L = _W + _Y + _O + _R
                        side = False if Y == 'Above' else True if Y == 'Below' else open < close
                        __block_result_21__ = na
                        if L == 0:
                            label.new(time, low if side else high, '●', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=color.white, text_font_family=font.family_monospace, tooltip=na if O else txt)
                            __block_result_21__ = label.new(time, low if side else high, '◯', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=color.new(chart.fg_color, 30), text_font_family=font.family_monospace, tooltip=txt) if O else na
                        elif L == 1:
                            c = color.white if _W == 1 else color.yellow if _Y == 1 else color.orange if _O == 1 else color.red
                            label.new(time, low if side else high, '●', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=c, text_font_family=font.family_monospace, tooltip=na if O else txt)
                            __block_result_21__ = label.new(time, low if side else high, '◯', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=color.new(chart.fg_color, 30), text_font_family=font.family_monospace, tooltip=txt) if O else na
                        elif L == 2:
                            c1 = color.white if _W == 1 else color.yellow if _Y == 1 else color.orange if _O == 1 else color.red
                            c2 = color.white if _W == 1 and c1 != color.white else color.yellow if _Y == 1 and c1 != color.yellow else color.orange if _O == 1 and c1 != color.orange else color.red
                            label.new(time, low if side else high, '◐', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=c1, text_font_family=font.family_monospace)
                            label.new(time, low if side else high, '◑', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=c2, text_font_family=font.family_monospace, tooltip=na if O else txt)
                            __block_result_21__ = label.new(time, low if side else high, '◯', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=color.new(chart.fg_color, 30), text_font_family=font.family_monospace, tooltip=txt) if O else na
                        elif L == 3:
                            c1 = color.white if _W == 1 else color.yellow if _Y == 1 else color.orange if _O == 1 else color.red
                            c2 = color.white if _W == 1 and c1 != color.white else color.yellow if _Y == 1 and c1 != color.yellow else color.orange if _O == 1 and c1 != color.orange else color.red
                            c3 = color.white if _W == 1 and c1 != color.white and (c2 != color.white) else color.yellow if _Y == 1 and c1 != color.yellow and (c2 != color.yellow) else color.orange if _O == 1 and c1 != color.orange and (c2 != color.orange) else color.red
                            label.new(time, low if side else high, '◐', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=color.yellow, text_font_family=font.family_monospace)
                            label.new(time, low if side else high, '◑', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=color.orange, text_font_family=font.family_monospace)
                            label.new(time, low if side else high, '◓', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=color.red, text_font_family=font.family_monospace, tooltip=na if O else txt)
                            __block_result_21__ = label.new(time, low if side else high, '◯', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=color.new(chart.fg_color, 30), text_font_family=font.family_monospace, tooltip=txt) if O else na
                        elif L == 4:
                            label.new(time, low if side else high, '◐', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=color.white, text_font_family=font.family_monospace)
                            label.new(time, low if side else high, '◑', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=color.yellow, text_font_family=font.family_monospace)
                            label.new(time, low if side else high, '◓', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=color.orange, text_font_family=font.family_monospace)
                            label.new(time, low if side else high, '◔', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=color.red, text_font_family=font.family_monospace, tooltip=na if O else txt)
                            __block_result_21__ = label.new(time, low if side else high, '◯', xloc.bar_time, color=color.new(color.new('#000000'), 100), size=S, style=label.style_label_up if side else label.style_label_down, textcolor=color.new(chart.fg_color, 30), text_font_family=font.family_monospace, tooltip=txt) if O else na
                        __block_result_20__ = __block_result_21__
                    __block_result_18__ = __block_result_20__
                __block_result_17__ = __block_result_18__
            __block_result_16__ = __block_result_17__
        return __block_result_16__

    @export
    def historical(T: int, D: bool, W: bool, X: str):
        daysLB: Persistent[int] = na(int)
        newDay: Persistent[int] = na(int)
        newWeek: Persistent[int] = na(int)
        delimiter: Persistent[int] = na(int)
        daysLB = time - T * timeframe.in_seconds('D') * 1000
        newDay = time if timeframe.change('D') else newDay
        newWeek = time if timeframe.change('W') else newWeek
        __block_result_22__ = na
        if D:
            __block_result_22__ = newDay
        elif W:
            __block_result_22__ = newWeek
        else:
            __block_result_22__ = daysLB
        delimiter = __block_result_22__

        __block_result_23__ = na
        if not na(delimiter):
            lines: list[Line] = line.all
            if array.size(lines) > 0:
                for i in pine_range(0, array.size(lines) - 1):
                    l = array.get(lines, i)
                    if method_call('get_x1', l) < delimiter:
                        method_call('delete', l)
                    if X == 'Future':
                        if method_call('get_x1', l) <= time:
                            method_call('delete', l)
            labels: list[Label] = label.all
            __block_result_24__ = na
            if array.size(labels) > 0:
                __block_result_25__ = na
                for i in pine_range(0, array.size(labels) - 1):
                    l = array.get(labels, i)
                    __block_result_26__ = na
                    if method_call('get_x', l) < delimiter:
                        __block_result_26__ = method_call('delete', l)
                    __block_result_25__ = __block_result_26__
                __block_result_24__ = __block_result_25__
            __block_result_23__ = __block_result_24__
        return __block_result_23__

    @export
    def newTable(P: str, B: Color = chart.fg_color):
        return table.new(P, 5, 1000, chart.bg_color, B, 1, B, 1)

    @export
    def resetTable(P: str, S: str, headTextC: Color, headBgC: Color, B: Color):
        _table = newTable(P, B)
        method_call('cell', _table, 0, 0, 'Date', text_color=headTextC, text_size=size__ren__(S), bgcolor=headBgC, text_font_family=font.family_monospace)
        method_call('cell', _table, 1, 0, 'Time', text_color=headTextC, text_size=size__ren__(S), bgcolor=headBgC, text_font_family=font.family_monospace)
        method_call('cell', _table, 2, 0, 'Currency', text_color=headTextC, text_size=size__ren__(S), bgcolor=headBgC, text_font_family=font.family_monospace)
        method_call('cell', _table, 3, 0, 'Impact', text_color=headTextC, text_size=size__ren__(S), bgcolor=headBgC, text_font_family=font.family_monospace)
        method_call('cell', _table, 4, 0, 'Forex Factory News', text_color=headTextC, text_size=size__ren__(S), bgcolor=headBgC, text_font_family=font.family_monospace)
        return _table

    @export
    def logNews(N: News, TBL: Table, R: int, S: str, rowTextC: Color, rowBgC: Color):
        table.cell(TBL, 0, R, N.dow + ' ' + N.dat, text_color=rowTextC, bgcolor=rowBgC, text_size=size__ren__(S), text_font_family=font.family_monospace)
        table.cell(TBL, 1, R, N.tod, text_color=rowTextC, bgcolor=rowBgC, text_size=size__ren__(S), text_font_family=font.family_monospace)
        table.cell(TBL, 2, R, N.cur, text_color=rowTextC, bgcolor=rowBgC, text_size=size__ren__(S), text_font_family=font.family_monospace)
        table.cell(TBL, 3, R, '⬤', text_color=N.imp, bgcolor=rowBgC, text_size=size__ren__(S), text_font_family=font.family_monospace)
        return table.cell(TBL, 4, R, N.ttl, text_color=rowTextC, bgcolor=rowBgC, text_size=size__ren__(S), text_font_family=font.family_monospace)

    @export
    def FF_Table(N: list[News], P: str, S: str, headTextC: Color, headBgC: Color, rowTextC: Color, rowBgC: Color, B: Color = chart.fg_color):
        _table: Table = na(Table)
        rows: int = 1
        _table = resetTable(P, S, headTextC, headBgC, B)
        if array.size(N) > 0:
            start_d: int = 1
            end_d: int = 1
            pDate: str = ""
            start_t: int = 1
            end_t: int = 1
            pTime: str = ""
            for i in pine_range(0, array.size(N) - 1):
                n = array.get(N, i)
                logNews(n, _table, rows, S, rowTextC, rowBgC)
                if i == 0:
                    pDate = n.dat
                    pTime = n.tod
                else:
                    if pDate == n.dat:
                        n.dow = ""
                        n.dat = ""
                        end_d = rows
                    else:
                        pDate = n.dat
                        if start_d != end_d:
                            table.merge_cells(_table, 0, start_d, 0, end_d)
                        start_d = rows
                        end_d = rows
                        if start_t != end_t:
                            table.merge_cells(_table, 1, start_t, 1, end_t)
                        start_t = rows
                        end_t = rows
                    if pTime == n.tod:
                        n.tod = ""
                        end_t = rows
                    else:
                        pTime = n.tod
                        if start_t != end_t:
                            table.merge_cells(_table, 1, start_t, 1, end_t)
                        start_t = rows
                        end_t = rows
                rows += 1
            if not start_d >= end_d:
                table.merge_cells(_table, 0, start_d, 0, end_d)
            if not start_t >= end_t:
                table.merge_cells(_table, 1, start_t, 1, end_t)

        if rows == 1:
            table.cell(_table, 0, rows, 'No News', text_color=rowTextC, text_size=size__ren__(S), bgcolor=rowBgC, text_font_family=font.family_monospace)
            table.cell(_table, 1, rows, '', text_color=rowTextC, text_size=size__ren__(S), bgcolor=rowBgC, text_font_family=font.family_monospace)
            table.cell(_table, 2, rows, '', text_color=rowTextC, text_size=size__ren__(S), bgcolor=rowBgC, text_font_family=font.family_monospace)
            table.cell(_table, 3, rows, '', text_color=rowTextC, text_size=size__ren__(S), bgcolor=rowBgC, text_font_family=font.family_monospace)
            table.cell(_table, 4, rows, '', text_color=rowTextC, text_size=size__ren__(S), bgcolor=rowBgC, text_font_family=font.family_monospace)
            table.merge_cells(_table, 0, rows, 4, rows)
            rows += 1

        table.cell(_table, 0, rows, '@toodegrees', text_color=headTextC, text_size=size__ren__(S), bgcolor=headBgC, text_font_family=font.family_monospace)
        table.cell(_table, 1, rows, '', text_color=headTextC, text_size=size__ren__(S), bgcolor=headBgC, text_font_family=font.family_monospace)
        table.cell(_table, 2, rows, '', text_color=headTextC, text_size=size__ren__(S), bgcolor=headBgC, text_font_family=font.family_monospace)
        table.cell(_table, 3, rows, '', text_color=headTextC, text_size=size__ren__(S), bgcolor=headBgC, text_font_family=font.family_monospace)
        table.cell(_table, 4, rows, '', text_color=headTextC, text_size=size__ren__(S), bgcolor=headBgC, text_font_family=font.family_monospace)
        table.merge_cells(_table, 0, rows, 4, rows)
        return _table

    @export
    def timeline(N: list[News], T: Table, F: Color, TZH: int = na, TZM: int = na, D: bool = False):
        events: list[News] = array.new(0, NA(News))
        tz: str = "America/New_York"
        if not na(TZH):
            tz = 'UTC' + ('+' if TZH > 0 else '-') + string.tostring(math.abs(TZH)) + (string.tostring(TZM) if TZM != 0 else '')
        tfms = timeframe.in_seconds(timeframe.period) * 1000
        if not D:
            if array.size(N) > 0:
                for i in pine_range(0, array.size(N) - 1):
                    n = array.get(N, i)
                    array.push(events, n)
        else:
            events = udt_copy(N)

        __block_result_27__ = na
        if array.size(events) > 0:
            dat: int = 1
            __block_result_28__ = na
            for i in pine_range(0, array.size(events) - 1):
                n = array.get(events, i)
                __block_result_29__ = na
                if timenow >= n.tmst:
                    table.cell_set_text_color(T, 1, i + 1, F)
                    table.cell_set_text_color(T, 2, i + 1, F)
                    table.cell_set_text_color(T, 4, i + 1, F)

                    if i != array.size(events) - 1 and (not D):
                        p = array.get(events, i + 1)
                        if dayofmonth(n.tmst, tz) != dayofmonth(p.tmst, tz):
                            table.cell_set_text_color(T, 0, dat, F)
                            dat = i + 2

                    __block_result_30__ = na
                    if i == array.size(events) - 1:
                        table.cell_set_text_color(T, 0, dat, F)
                        dat = i + 1
                        __block_result_30__ = table.cell_set_text_color(T, 0, dat, F)
                    __block_result_29__ = __block_result_30__
                __block_result_28__ = __block_result_29__
            __block_result_27__ = __block_result_28__
        return __block_result_27__


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
