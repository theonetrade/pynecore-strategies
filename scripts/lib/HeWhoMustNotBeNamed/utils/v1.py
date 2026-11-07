"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.lib import array, color, line, math, script, string, timenow
from typing import Protocol, Any


__all__ = ['check_overflow', 'getColors', 'getConsolidatedLabel', 'get_trend_series', 'timer']


class _ProtocolTimer(Protocol):
    def __call__(self, timeStart: int, timeEnd: int = timenow) -> Any: ...


class _ProtocolCheckOverflow(Protocol):
    def __call__(self, pivots: list[float], barArray: list[float], dir: int) -> Any: ...


class _ProtocolGetTrendSeries(Protocol):
    def __call__(self, pivots: list[float], length: int, highLow: int, trend: int) -> Any: ...


class _ProtocolGetTrendSeries3(Protocol):
    def __call__(self, pivots: list[float], firstIndex: int, lastIndex: int) -> Any: ...


class _ProtocolGetconsolidatedlabel(Protocol):
    def __call__(self, include: list[bool], labels: list[str], separator: str = '\n') -> Any: ...


class _ProtocolGetcolors(Protocol):
    def __call__(self, theme: str = 'dark') -> Any: ...


timer: _ProtocolTimer = Exported()
check_overflow: _ProtocolCheckOverflow = Exported()
get_trend_series: _ProtocolGetTrendSeries = Exported()
get_trend_series: _ProtocolGetTrendSeries3 = Exported()
getConsolidatedLabel: _ProtocolGetconsolidatedlabel = Exported()
getColors: _ProtocolGetcolors = Exported()


@script.library('utils')
def main():
    @export
    def timer(timeStart: int, timeEnd: int = timenow):
        timeDiff = math.abs(timeEnd - timeStart)
        mseconds = timeDiff
        seconds = mseconds / 1000
        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24
        tmSeconds = mseconds % 1000
        tSeconds = seconds % 60
        tMinutes = minutes % 60
        tHours = hours % 24
        return (days, tHours, tMinutes, tSeconds, tmSeconds)

    @export
    def check_overflow(pivots: list[float], barArray: list[float], dir: int):
        cBar = cast_int(array.get(barArray, 0))
        aBar = cast_int(array.get(barArray, array.size(barArray) - 1))
        c = array.get(pivots, 0)
        a = array.get(pivots, array.size(pivots) - 1)
        ln = line.new(aBar, a, cBar, c)
        overflow: bool = False
        for i, currentBar in enumerate(barArray):
            peak = array.get(pivots, i)
            linePrice = line.get_price(ln, cast_int(currentBar))
            if dir * peak > dir * linePrice:
                overflow = True
                break
        line.delete(ln)
        return overflow

    @export
    @overload
    def get_trend_series(pivots: list[float], length: int, highLow: int, trend: int):
        startLength: int = 1
        endLength = math.min(array.size(pivots), length)
        trendIndexes: list[int] = array.new_int()
        if startLength < endLength:
            first = array.get(pivots, 0)
            sec = array.get(pivots, 1)
            dir = 1 if first > sec else -1
            while startLength + (1 if dir == highLow else 0) < endLength:
                oTrend = trend * highLow
                min = array.slice(pivots, startLength, endLength)
                peak = array.max(min) if highLow == 1 else array.min(min)
                peakIndex = array.indexof(min, peak) if oTrend == 1 else array.lastindexof(min, peak)
                if oTrend == 1:
                    array.insert(trendIndexes, 0, startLength + peakIndex)
                else:
                    array.push(trendIndexes, startLength + peakIndex)
                if startLength + peakIndex == endLength if oTrend == 1 else peakIndex == 0:
                    break
                if oTrend == 1:
                    startLength = startLength + peakIndex + 1 + (1 if dir > 0 else 0)
                else:
                    endLength = peakIndex
        return trendIndexes

    @export
    @overload
    def get_trend_series(pivots: list[float], firstIndex: int, lastIndex: int):
        startIndex = firstIndex
        endIndex = math.min(array.size(pivots), lastIndex)
        trendIndexes: list[int] = array.new_int()
        if startIndex + 1 < endIndex:
            first = array.get(pivots, startIndex)
            sec = array.get(pivots, startIndex + 1)
            dir = 1 if first > sec else -1
            min = array.slice(pivots, startIndex, endIndex)
            while array.size(min) > 1:
                peak = array.min(min) if dir == 1 else array.max(min)
                peakIndex = array.lastindexof(min, peak)
                min = array.slice(pivots, startIndex, startIndex + peakIndex)
                reversePeak = array.max(min) if dir == 1 else array.min(min)
                if reversePeak == first:
                    array.push(trendIndexes, startIndex + peakIndex)
        return trendIndexes

    @export
    def getConsolidatedLabel(include: list[bool], labels: list[str], separator: str = '\n'):
        labelText: str = ''
        for i in pine_range(0, array.size(include) - 1, 1):
            labelText = labelText + (('' if labelText == '' else separator) + array.get(labels, i) if array.get(include, i) else '')
        return labelText

    @export
    def getColors(theme: str = 'dark'):
        return array.from_items(color.rgb(251, 244, 109), color.rgb(141, 186, 81), color.rgb(74, 159, 245), color.rgb(255, 153, 140), color.rgb(255, 149, 0), color.rgb(0, 234, 211), color.rgb(167, 153, 183), color.rgb(255, 210, 113), color.rgb(119, 217, 112), color.rgb(95, 129, 228), color.rgb(235, 146, 190), color.rgb(198, 139, 89), color.rgb(200, 149, 149), color.rgb(196, 182, 182), color.rgb(255, 190, 15), color.rgb(192, 226, 24), color.rgb(153, 140, 235), color.rgb(206, 31, 107), color.rgb(251, 54, 64), color.rgb(194, 255, 217), color.rgb(255, 219, 197), color.rgb(121, 180, 183)) if string.lower(theme) == 'dark' else array.from_items(color.rgb(61, 86, 178), color.rgb(57, 163, 136), color.rgb(250, 30, 14), color.rgb(169, 51, 58), color.rgb(225, 87, 138), color.rgb(62, 124, 23), color.rgb(244, 164, 66), color.rgb(134, 72, 121), color.rgb(113, 159, 176), color.rgb(170, 46, 230), color.rgb(161, 37, 104), color.rgb(189, 32, 0), color.rgb(16, 86, 82), color.rgb(200, 92, 92), color.rgb(63, 51, 81), color.rgb(114, 106, 149), color.rgb(171, 109, 35), color.rgb(247, 136, 18), color.rgb(51, 71, 86), color.rgb(12, 123, 147), color.rgb(195, 43, 173))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
