"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    array, bar_index, close, color, location, math, na, nz, open, plot,
    plotchar, script, size, ta, time, timeframe, volume
)
from pynecore.types import Color, Persistent, Series
from typing import Protocol, Any


__all__ = ['avgSince', 'avgWhen', 'avgWhenInLast', 'avgWhenLast', 'totalForTimeWhen']


class _ProtocolAvgwhen(Protocol):
    def __call__(self, source: Series[float], condition: Series[bool]) -> Any: ...


class _ProtocolAvgwhenlast(Protocol):
    def __call__(self, source: Series[float], condition: Series[bool], count: Series[int]) -> Any: ...


class _ProtocolAvgwheninlast(Protocol):
    def __call__(self, source: Series[float], condition: Series[bool], length: Series[int]) -> Any: ...


class _ProtocolAvgsince(Protocol):
    def __call__(self, source: Series[float], condition: Series[bool]) -> Any: ...


class _ProtocolTotalfortimewhen(Protocol):
    def __call__(self, source: Series[float], ms: int, condition: Series[bool] = True, minBars: int = 1) -> Any: ...


avgWhen: _ProtocolAvgwhen = Exported()
avgWhenLast: _ProtocolAvgwhenlast = Exported()
avgWhenInLast: _ProtocolAvgwheninlast = Exported()
avgSince: _ProtocolAvgsince = Exported()
totalForTimeWhen: _ProtocolTotalfortimewhen = Exported()


@script.library("ConditionalAverages")
def main():
    @export
    def avgWhen(source: Series[float], condition: Series[bool]):
        return ta.cum(source if condition else 0.0) / ta.cum(1 if condition else 0)

    @export
    def avgWhenLast(source: Series[float], condition: Series[bool], count: Series[int]):
        return ta.sma(source if condition else na, count)

    @export
    def avgWhenInLast(source: Series[float], condition: Series[bool], length: Series[int]):
        cond: bool = condition and (not na(source))
        return math.sum(source if cond else 0.0, length) / math.sum(1 if cond else 0, length)

    @export
    def avgSince(source: Series[float], condition: Series[bool]):
        lastTotal: Persistent[float] = 0.0
        lastIndex: Persistent[int] = na(int)
        lastNaCt: Persistent[float] = na(float)
        total: Series[float] = ta.cum(nz(source))
        naBars: Series[float] = ta.cum(1 if na(source) else 0)
        __block_result__ = na
        if condition:
            lastTotal = nz(total[1])
            lastIndex = bar_index - 1
            lastNaCt = nz(naBars[1])
            __block_result__ = source
        else:
            __block_result__ = (total - lastTotal) / (bar_index - lastIndex - naBars + lastNaCt)
        return __block_result__

    def avgForTimeWhen(source: Series[float], ms: int, condition: Series[bool] = True, minBars: int = 1):
        sources: Persistent[list[float]] = array.new_float()
        times: Persistent[list[int]] = array.new_int()
        result: Persistent[float] = na(float)
        numerator: Persistent[float] = 0.0
        if condition and (not na(source)):
            array.push(sources, source)
            array.push(times, time)
            numerator += source
            while array.size(sources) > math.max(minBars, 0) and time - array.first(times) >= ms:
                numerator -= array.shift(sources)
                array.shift(times)
            result = numerator / array.size(sources)
        return na if array.size(sources) < minBars else result

    @export
    def totalForTimeWhen(source: Series[float], ms: int, condition: Series[bool] = True, minBars: int = 1):
        sources: Persistent[list[float]] = array.new_float(0)
        times: Persistent[list[int]] = array.new_int(0)
        result: Persistent[float] = 0.0
        if condition and (not na(source)):
            array.push(sources, source)
            array.push(times, time)
            result += source
            while array.size(sources) > math.max(minBars, 0) and time - array.first(times) >= ms:
                result -= array.shift(sources)
                array.shift(times)
        return na if array.size(sources) < minBars else result

    MAGENTA: Color = color.new('#FF00FF')
    GREEN1: Color = color.new('#00FF00')
    LINK_WATER: Color = color.new('#D1D4DC')
    STORM_GREY: Color = color.new('#787B86')

    LAST_OCCURRENCES: int = 20

    LAST_BARS: int = 20

    MS_IN_1D: int = 24 * 60 * 60 * 1000

    MIN_BARS: int = 10

    source: float = volume

    condition: bool = close > open

    volumeColor: Color = LINK_WATER if condition else STORM_GREY

    plot(volume, 'volume', color.new(volumeColor, 65), 4, plot.style_histogram)

    plot(avgWhen(source, condition), 'avgWhen()', color.navy)

    plot(avgWhenLast(source, condition, LAST_OCCURRENCES), 'avgWhenLast()', color.orange)

    plot(avgWhenInLast(source, condition, LAST_BARS), 'avgWhenInLast()', color.aqua)

    plot(avgSince(source, timeframe.change('D')), 'avgSince()', MAGENTA)

    plot(avgForTimeWhen(source, MS_IN_1D, True, MIN_BARS), 'avgForTimeWhen()', GREEN1)

    plotchar(totalForTimeWhen(source, MS_IN_1D, True, MIN_BARS), 'totalForTimeWhen()', '', location.top, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
