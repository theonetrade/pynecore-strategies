"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    array, bar_index, barstate, chart, close, color, extend, format, high,
    hlc3, label, line, low, math, na, nz, open, position, script, size, string, ta, table, time,
    volume, xloc, yloc
)
from pynecore.types import Color, Label, Line, NA, Persistent, Series, Table
from typing import Protocol, Any


__all__ = ['avg', 'barIsVisible', 'bars', 'chartXIndexPct', 'chartXTimePct', 'chartYPct', 'close__ren__', 'highBarIndex', 'highBarTime', 'high__ren__', 'isFirstVisibleBar', 'isLastVisibleBar', 'leftBarIndex', 'lowBarIndex', 'lowBarTime', 'low__ren__', 'median', 'ohlcv', 'open__ren__', 'rightBarIndex', 'vVwap', 'volume__ren__', 'whenVisible']


class _ProtocolBarisvisible(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolIsfirstvisiblebar(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolIslastvisiblebar(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolHigh(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolHighbarindex(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolHighbartime(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolLow(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolLowbarindex(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolLowbartime(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolOpen(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolClose(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolLeftbarindex(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolRightbarindex(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolBars(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolVolume(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolOhlcv(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolChartypct(Protocol):
    def __call__(self, pct: Series[float]) -> Any: ...


class _ProtocolChartxtimepct(Protocol):
    def __call__(self, pct: Series[float]) -> Any: ...


class _ProtocolChartxindexpct(Protocol):
    def __call__(self, pct: Series[float]) -> Any: ...


class _ProtocolWhenvisible(Protocol):
    def __call__(self, source: Series[float], whenCond: Series[bool] = True, length: int = na) -> Any: ...


class _ProtocolAvg(Protocol):
    def __call__(self, source: Series[float] = close) -> Any: ...


class _ProtocolMedian(Protocol):
    def __call__(self, src: Series[float] = close) -> Any: ...


class _ProtocolVvwap(Protocol):
    def __call__(self, src: Series[float] = hlc3) -> Any: ...


barIsVisible: _ProtocolBarisvisible = Exported()
isFirstVisibleBar: _ProtocolIsfirstvisiblebar = Exported()
isLastVisibleBar: _ProtocolIslastvisiblebar = Exported()
high__ren__: _ProtocolHigh = Exported()
highBarIndex: _ProtocolHighbarindex = Exported()
highBarTime: _ProtocolHighbartime = Exported()
low__ren__: _ProtocolLow = Exported()
lowBarIndex: _ProtocolLowbarindex = Exported()
lowBarTime: _ProtocolLowbartime = Exported()
open__ren__: _ProtocolOpen = Exported()
close__ren__: _ProtocolClose = Exported()
leftBarIndex: _ProtocolLeftbarindex = Exported()
rightBarIndex: _ProtocolRightbarindex = Exported()
bars: _ProtocolBars = Exported()
volume__ren__: _ProtocolVolume = Exported()
ohlcv: _ProtocolOhlcv = Exported()
chartYPct: _ProtocolChartypct = Exported()
chartXTimePct: _ProtocolChartxtimepct = Exported()
chartXIndexPct: _ProtocolChartxindexpct = Exported()
whenVisible: _ProtocolWhenvisible = Exported()
avg: _ProtocolAvg = Exported()
median: _ProtocolMedian = Exported()
vVwap: _ProtocolVvwap = Exported()


@script.library("VisibleChart", True)
def main():
    @export
    def barIsVisible():
        return time >= chart.left_visible_bar_time and time <= chart.right_visible_bar_time

    @export
    def isFirstVisibleBar():
        return time == chart.left_visible_bar_time

    @export
    def isLastVisibleBar():
        return time == chart.right_visible_bar_time

    @export
    def high__ren__():
        result: Persistent[float] = na(float)
        if barIsVisible() and high >= nz(result, high):
            result = high
        return result

    @export
    def highBarIndex():
        chartHigh: Persistent[float] = na(float)
        highBar: Persistent[int] = na(int)
        if barIsVisible() and high >= nz(chartHigh, high):
            highBar = bar_index
            chartHigh = high
        return highBar

    @export
    def highBarTime():
        chartHigh: Persistent[float] = na(float)
        highTime: Persistent[int] = na(int)
        if barIsVisible() and high >= nz(chartHigh, high):
            highTime = time
            chartHigh = high
        return highTime

    @export
    def low__ren__():
        result: Persistent[float] = na(float)
        if barIsVisible() and low <= nz(result, low):
            result = low
        return result

    @export
    def lowBarIndex():
        chartLow: Persistent[float] = na(float)
        lowBar: Persistent[int] = na(int)
        if barIsVisible() and low <= nz(chartLow, low):
            lowBar = bar_index
            chartLow = low
        return lowBar

    @export
    def lowBarTime():
        chartLow: Persistent[float] = na(float)
        lowTime: Persistent[int] = na(int)
        if barIsVisible() and low <= nz(chartLow, low):
            lowTime = time
            chartLow = low
        return lowTime

    @export
    def open__ren__():
        result: Persistent[float] = na(float)
        if isFirstVisibleBar():
            result = open
        return result

    @export
    def close__ren__():
        result: Persistent[float] = na(float)
        if barIsVisible():
            result = close
        return result

    @export
    def leftBarIndex():
        result: Persistent[int] = na(int)
        if isFirstVisibleBar():
            result = bar_index
        return result

    @export
    def rightBarIndex():
        result: Persistent[int] = na(int)
        if barIsVisible():
            result = bar_index
        return result

    @export
    def bars():
        result: Persistent[int] = 0
        if barIsVisible():
            result += 1
        return result

    @export
    def volume__ren__():
        result: Persistent[float] = 0
        if barIsVisible():
            result += volume
        return result

    @export
    def ohlcv():
        return (open__ren__(), high__ren__(), low__ren__(), close__ren__(), volume__ren__())

    @export
    def chartYPct(pct: Series[float]):
        return low__ren__() + (high__ren__() - low__ren__()) * (pct / 100)

    @export
    def chartXTimePct(pct: Series[float]):
        return chart.left_visible_bar_time + cast_int((chart.right_visible_bar_time - chart.left_visible_bar_time) * (pct / 100))

    @export
    def chartXIndexPct(pct: Series[float]):
        leftBarIndex__0000003c__: int = leftBarIndex()
        rightBarIndex__0000003c__: int = rightBarIndex()
        return leftBarIndex__0000003c__ + cast_int((rightBarIndex__0000003c__ - leftBarIndex__0000003c__) * (pct / 100))

    @export
    def whenVisible(source: Series[float], whenCond: Series[bool] = True, length: int = na):
        values: Persistent[list[float]] = array.new_float()
        cappedLen: int = math.max(1, length)
        if barIsVisible() and whenCond:
            array.push(values, source)
        if not na(cappedLen) and array.size(values) > cappedLen:
            array.shift(values)
        return values

    @export
    def avg(source: Series[float] = close):
        visible: bool = barIsVisible()
        cumTotal: float = ta.cum(source if visible else 0)
        cumCount: float = ta.cum(1 if visible else 0)
        return cumTotal / cumCount

    @export
    def median(src: Series[float] = close):
        return array.median(whenVisible(src))

    @export
    def vVwap(src: Series[float] = hlc3):
        startTime: bool = isFirstVisibleBar()
        return ta.vwap(src, startTime)

    chartHigh: float = high__ren__()
    chartLow: float = low__ren__()
    highTime: int = highBarTime()
    lowTime: int = lowBarTime()
    leftTime: int = math.min(highTime, lowTime)
    rightTime: int = math.max(highTime, lowTime)
    isBull: bool = lowTime < highTime
    bars__global__: int = bars()
    vol: float = volume__ren__()

    def fibLine(fibColor: Series[Color], fibLevel: Series[float]):
        fibRatio: float = fibLevel / 100
        fibPrice: float = chartHigh - (chartHigh - chartLow) * fibRatio if isBull else chartLow + (chartHigh - chartLow) * fibRatio
        fibLine__00000065__: Persistent[Line] = line.new(na, na, na, na, xloc.bar_time, extend.none, fibColor, line.style_solid, 1)
        fibLine2: Persistent[Line] = line.new(na, na, na, na, xloc.bar_time, extend.none, fibColor, line.style_dotted, 1)
        fibLabel: Persistent[Label] = label.new(na, na, '', xloc.bar_time, yloc.price, NA(Color), label.style_label_up, fibColor)
        line.set_xy1(fibLine__00000065__, leftTime, fibPrice)
        line.set_xy2(fibLine__00000065__, rightTime, fibPrice)
        line.set_xy1(fibLine2, rightTime, fibPrice)
        line.set_xy2(fibLine2, time, fibPrice)
        label.set_xy(fibLabel, cast_int(math.avg(leftTime, rightTime)), fibPrice)
        return label.set_text(fibLabel, string.format('{0, number, #.###} ({1})', fibRatio, string.tostring(fibPrice, format.mintick)))

    if barstate.islast:
        display__ren__: Persistent[Table] = table.new(position.top_right, 1, 1)

        displayString: str = 'Total Visible Bars: ' + string.tostring(bars__global__) + '\nTotal Visible Volume: ' + string.tostring(vol, format.volume)

        table.cell(display__ren__, 0, 0, displayString, bgcolor=color.yellow, text_color=color.black, text_size=size.normal)

        hiLabel: Persistent[Label] = label.new(na, na, na, xloc.bar_time, yloc.price, color.new(color.lime, 80), label.style_label_down, color.lime)
        loLabel: Persistent[Label] = label.new(na, na, na, xloc.bar_time, yloc.price, color.new(color.fuchsia, 80), label.style_label_up, color.fuchsia)

        label.set_xy(hiLabel, highTime, chartHigh)
        label.set_xy(loLabel, lowTime, chartLow)
        label.set_text(hiLabel, string.format('{0}\n{1}', string.tostring(chartHigh, format.mintick), string.format_time(highTime, "dd/MM/yy '@' HH:mm:ss")))
        label.set_text(loLabel, string.format('{0}\n{1}', string.tostring(chartLow, format.mintick), string.format_time(lowTime, "dd/MM/yy '@' HH:mm:ss")))

        fibLine(color.gray, 100)
        fibLine(color.new('#64B5F6'), 78.6)
        fibLine(color.new('#089981'), 61.8)
        fibLine(color.green, 50)
        fibLine(color.new('#81C784'), 38.2)
        fibLine(color.red, 23.6)
        fibLine(color.gray, 0)

        hiLoLine: Persistent[Line] = line.new(na, na, na, na, xloc.bar_time, extend.none, color.gray, line.style_dashed, 1)

        line.set_xy1(hiLoLine, highTime, chartHigh)
        line.set_xy2(hiLoLine, lowTime, chartLow)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
