"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method, method_call
from pynecore.lib import (
    array, color, dayofmonth, dayofweek, month, na, script, string, time,
    timestamp, year
)
from typing import Protocol, Any
import lib.toodegrees.forex_factory_events_id_A.v12 as ffEventA
import lib.toodegrees.forex_factory_events_id_B.v36 as ffEventB
import lib.toodegrees.forex_factory_utility.v17 as ffUtil


__all__ = ['MMM', 'array2string', 'daysMonth', 'decode', 'ff_currency', 'ff_dow', 'ff_impact', 'ff_t', 'ff_tmst', 'ff_tod', 'isLeapYear', 'month2number', 'pullNews', 'readNews', 'shiftFWD_Days']


class _ProtocolIsleapyear(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolDaysmonth(Protocol):
    def __call__(self, M: int) -> Any: ...


class _ProtocolMmm(Protocol):
    def __call__(self, M: int) -> Any: ...


class _ProtocolArray2string(Protocol):
    def __call__(self, S: list[str], FWD: bool = True) -> Any: ...


class _ProtocolMonth2number(Protocol):
    def __call__(self, M: str) -> Any: ...


class _ProtocolShiftfwdDays(Protocol):
    def __call__(self, D: int = 7) -> Any: ...


class _ProtocolFfDow(Protocol):
    def __call__(self, D: str) -> Any: ...


class _ProtocolFfCurrency(Protocol):
    def __call__(self, C: str) -> Any: ...


class _ProtocolFfT(Protocol):
    def __call__(self, T: str) -> Any: ...


class _ProtocolFfTod(Protocol):
    def __call__(self, T: int) -> Any: ...


class _ProtocolFfImpact(Protocol):
    def __call__(self, I: str) -> Any: ...


class _ProtocolFfTmst(Protocol):
    def __call__(self, D: str, T: str) -> Any: ...


class _ProtocolDecode(Protocol):
    def __call__(self, ID: int) -> Any: ...


class _ProtocolPullnews(Protocol):
    def __call__(self, N: list[ffUtil.News], n: float) -> Any: ...


class _ProtocolReadnews(Protocol):
    def __call__(self, N: list[ffUtil.News], S: str) -> Any: ...


isLeapYear: _ProtocolIsleapyear = Exported()
daysMonth: _ProtocolDaysmonth = Exported()
MMM: _ProtocolMmm = Exported()
array2string: _ProtocolArray2string = Exported()
month2number: _ProtocolMonth2number = Exported()
shiftFWD_Days: _ProtocolShiftfwdDays = Exported()
ff_dow: _ProtocolFfDow = Exported()
ff_currency: _ProtocolFfCurrency = Exported()
ff_t: _ProtocolFfT = Exported()
ff_tod: _ProtocolFfTod = Exported()
ff_impact: _ProtocolFfImpact = Exported()
ff_tmst: _ProtocolFfTmst = Exported()
decode: _ProtocolDecode = Exported()
pullNews: _ProtocolPullnews = Exported()
readNews: _ProtocolReadnews = Exported()


@script.library("forex_factory_decoding")
def main():
    @export
    def isLeapYear():
        Y = year(time, 'America/New_York')
        return Y % 4 == 0 and Y % 100 != 0 or Y % 400 == 0

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
    def array2string(S: list[str], FWD: bool = True):
        s: str = ""
        if array.size(S) > 0:
            if FWD:
                for i in pine_range(0, array.size(S) - 1):
                    s += array.get(S, i)
            else:
                for i in pine_range(array.size(S) - 1, 0):
                    s += array.get(S, i)
        return s

    @export
    def month2number(M: str):
        __block_result_2__ = na
        __switch__ = M
        if __switch__ == "Jan":
            __block_result_2__ = 1
        elif __switch__ == "Feb":
            __block_result_2__ = 2
        elif __switch__ == "Mar":
            __block_result_2__ = 3
        elif __switch__ == "Apr":
            __block_result_2__ = 4
        elif __switch__ == "May":
            __block_result_2__ = 5
        elif __switch__ == "Jun":
            __block_result_2__ = 6
        elif __switch__ == "Jul":
            __block_result_2__ = 7
        elif __switch__ == "Aug":
            __block_result_2__ = 8
        elif __switch__ == "Sep":
            __block_result_2__ = 9
        elif __switch__ == "Oct":
            __block_result_2__ = 10
        elif __switch__ == "Nov":
            __block_result_2__ = 11
        elif __switch__ == "Dec":
            __block_result_2__ = 12
        m = __block_result_2__
        return m

    @export
    def shiftFWD_Days(D: int = 7):
        _day = dayofmonth(time + 86400000 * (D + 1), 'America/New_York')
        _month = month(time + 86400000 * (D + 1), 'America/New_York')
        return MMM(_month) + ' ' + string.tostring(_day)

    @export
    def ff_dow(D: str):
        __block_result_3__ = na
        __switch__ = D
        if __switch__ == "1":
            __block_result_3__ = "Sun"
        elif __switch__ == "2":
            __block_result_3__ = "Mon"
        elif __switch__ == "3":
            __block_result_3__ = "Tue"
        elif __switch__ == "4":
            __block_result_3__ = "Wed"
        elif __switch__ == "5":
            __block_result_3__ = "Thu"
        elif __switch__ == "6":
            __block_result_3__ = "Fri"
        elif __switch__ == "7":
            __block_result_3__ = "Sat"
        DOW = __block_result_3__
        return DOW

    @export
    def ff_currency(C: str):
        __block_result_4__ = na
        __switch__ = C
        if __switch__ == "1":
            __block_result_4__ = "AUD"
        elif __switch__ == "2":
            __block_result_4__ = "CAD"
        elif __switch__ == "3":
            __block_result_4__ = "CHF"
        elif __switch__ == "4":
            __block_result_4__ = "CNY"
        elif __switch__ == "5":
            __block_result_4__ = "EUR"
        elif __switch__ == "6":
            __block_result_4__ = "GBP"
        elif __switch__ == "7":
            __block_result_4__ = "JPY"
        elif __switch__ == "8":
            __block_result_4__ = "NZD"
        elif __switch__ == "9":
            __block_result_4__ = "USD"
        CURRENCY = __block_result_4__
        return CURRENCY

    @export
    def ff_t(T: str):
        __block_result_5__ = na
        if T == '9999':
            __block_result_5__ = -1
        else:
            _tod: list[str] = string.split(T, '')
            TOD: str = ""
            __block_result_6__ = na
            if array.size(_tod) > 0:
                for i in pine_range(0, array.size(_tod) - 1):
                    TOD += array.get(_tod, i)
                __block_result_6__ = cast_int(string.tonumber(TOD))
            __block_result_5__ = __block_result_6__
        return __block_result_5__

    @export
    def ff_tod(T: int):
        __block_result_7__ = na
        if T == -1:
            __block_result_7__ = "All Day"
        else:
            _tod: list[str] = string.split(string.tostring(T), '')
            while array.size(_tod) != 4:
                array.unshift(_tod, '0')
            TOD: str = ""
            for j in pine_range(0, array.size(_tod) - 1):
                if j == 2:
                    TOD += ":"
                TOD += array.get(_tod, j)
            __block_result_7__ = TOD
        return __block_result_7__

    @export
    def ff_impact(I: str):
        __block_result_8__ = na
        __switch__ = I
        if __switch__ == "1":
            __block_result_8__ = color.white
        elif __switch__ == "2":
            __block_result_8__ = color.yellow
        elif __switch__ == "3":
            __block_result_8__ = color.orange
        elif __switch__ == "4":
            __block_result_8__ = color.red
        return __block_result_8__

    @export
    def ff_tmst(D: str, T: str):
        _date = string.split(D, ' ')
        _time = string.split(T, ':')
        _M = month2number(method_call('get', _date, 0))
        _d = cast_int(string.tonumber(method_call('get', _date, 1)))
        _h = 0 if method_call('size', _time) == 1 else cast_int(string.tonumber(method_call('get', _time, 0)))
        _m = 0 if method_call('size', _time) == 1 else cast_int(string.tonumber(method_call('get', _time, 1)))
        curr_y = year(time, 'America/New_York')
        curr_m = month(time, 'America/New_York')
        _Y = (curr_y if curr_m == 1 else curr_y + 1) if _M == 1 else curr_y
        return timestamp('America/New_York', _Y, _M, _d, _h, _m, 0)

    @export
    def decode(ID: int):
        __block_result_9__ = na
        if na(ID):
            __block_result_9__ = na
        else:
            D: list[str] = string.split(string.tostring(ID), '')
            __block_result_10__ = na
            if array.size(D) > 0:
                decoded_dow = ff_dow(array.get(D, 0))
                decoded_date = shiftFWD_Days(6) if array.get(D, 0) != string.tostring(dayofweek(time + 86400000 * 8, 'America/New_York')) else shiftFWD_Days()
                decoded_currency = ff_currency(array.get(D, 1))
                decoded_t = ff_t(array2string(array.slice(D, 2, 6)))
                decoded_tod = ff_tod(decoded_t)
                decoded_impact = ff_impact(array2string(array.slice(D, 6, 7)))
                title = array2string(array.slice(D, 7, array.size(D)))
                decoded_title = ffEventA.ff_titleA(title) if string.tonumber(title) < 500 else ffEventB.ff_titleB(title)
                decoded_tmst = ff_tmst(decoded_date, decoded_tod)

                __block_result_10__ = ffUtil.News.new(decoded_dow, decoded_date, decoded_t, decoded_tod, decoded_currency, decoded_impact, decoded_title, decoded_tmst)
            else:
                __block_result_10__ = na
            __block_result_9__ = __block_result_10__
        return __block_result_9__

    @export
    @method
    def pullNews(N: list[ffUtil.News], n: float):
        __block_result_11__ = na
        if not na(n):
            __block_result_12__ = na
            if cast_int(n) != 999:
                __block_result_12__ = array.push(N, decode(cast_int(n)))
            __block_result_11__ = __block_result_12__
        return __block_result_11__

    @export
    @method
    def readNews(N: list[ffUtil.News], S: str):
        news = string.split(S, ',')
        __block_result_13__ = na
        if method_call('size', news) > 0:
            __block_result_14__ = na
            for i in pine_range(0, method_call('size', news) - 1):
                __block_result_14__ = pullNews(N, string.tonumber(method_call('get', news, i)))
            __block_result_13__ = __block_result_14__
        return __block_result_13__


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
