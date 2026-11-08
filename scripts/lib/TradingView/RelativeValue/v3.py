"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.overload import overload
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, barstate, close, color, display, input, math, na, open, plot,
    script, time, time_close, timeframe, timenow, volume
)
from pynecore.types import Color, NA, Persistent, Series
from typing import Protocol, Any


__all__ = ['averageAtTime', 'calcCumulativeSeries']


@udt
class collectedData:
    data: list[float] = na(list)
    times: list[int] = na(list)
    startTime: int = na(int)


class _ProtocolCalccumulativeseries(Protocol):
    def __call__(self, source: Series[float], anchor: Series[bool], adjustRealtime: bool = False) -> Any: ...


class _ProtocolAverageattime(Protocol):
    def __call__(self, source: Series[float], length: int, anchor: Series[bool], isCumulative: bool = True) -> Any: ...


class _ProtocolAverageattime2(Protocol):
    def __call__(self, source: Series[float], length: int, timeframe__ren__: str, isCumulative: bool = True) -> Any: ...


calcCumulativeSeries: _ProtocolCalccumulativeseries = Exported()
averageAtTime: _ProtocolAverageattime = Exported()
averageAtTime: _ProtocolAverageattime2 = Exported()


MI01: str = "Cumulative"
MI02: str = "Regular"
EQ01: str = "On"
EQ02: str = "Off"
TT_RT: str = "The timeframe for the period reset condition. Default is 'D'."
TT_LI: str = "The number of periods in the average volume calculation. Default is 5."
TT_MI: str = "Choose between 'Cumulative' for a running total of volume since the last anchor point, or 'Regular' for non-cumulative volume. Default is 'Cumulative'"
TT_SR: str = "If enabled, the volume will be displayed as 'Relative Volume', which is the ratio of the current volume to the historical average volume."
TT_AR: str = "When activated in 'Cumulative' mode, this feature estimates the volume of the unclosed bar using the volume data from the current session."


@script.library("RelativeValue")
def main(
    resetTimeInput=input.timeframe("D", "Anchor Timeframe", tooltip=TT_RT),
    lengthInput=input.int(5, "No. of periods to avg.", tooltip=TT_LI),
    modeInput=input.string("Cumulative", "Calculation Mode", tooltip=TT_MI, options=(MI01, MI02)),
    __input_3__=input.string(EQ02, "Show as Relative Ratio", tooltip=TT_SR, options=(EQ01, EQ02)),
    __input_4__=input.string(EQ02, "Estimate Unconfirmed", tooltip=TT_AR, options=(EQ01, EQ02))
):
    @method
    def maintainArray(id: list[collectedData], maxSize: int, value: Series[collectedData]):
        array.push(id, value)
        __block_result__ = na
        if array.size(id) > maxSize:
            __block_result__ = array.shift(id)
        return __block_result__

    @method
    def calcAverageByTime(id: list[collectedData], timeOffset: Series[int]):
        sum: float = 0.0
        for eachItem in id:
            startTime: int = eachItem.startTime
            index: int = array.binary_search_leftmost(eachItem.times, startTime + timeOffset)
            adjData: float = array.get(eachItem.data, index) if array.size(eachItem.data) - 1 >= index else array.last(eachItem.data)
            sum += adjData
        return sum / array.size(id)

    @export
    def calcCumulativeSeries(source: Series[float], anchor: Series[bool], adjustRealtime: bool = False):
        sum: Persistent[float] = 0.0
        lastAnchor: Persistent[int] = na(int)
        if anchor:
            sum = 0.0
            lastAnchor = time
        sum += source
        if adjustRealtime and (not barstate.isconfirmed):
            timePassed: int = math.min(timenow, time_close) - lastAnchor
            timeTotal: int = time_close - lastAnchor
            currentRatio: float = sum / timePassed
            sum = currentRatio * timeTotal
        return sum

    @export
    @overload
    def averageAtTime(source: Series[float], length: int, anchor: Series[bool], isCumulative: bool = True):
        historicalData: Persistent[list[collectedData]] = array.new(0, NA(collectedData))
        newData: Persistent[collectedData] = collectedData(array.new_float(), array.new_int())
        src: float = calcCumulativeSeries(source, anchor) if isCumulative else source
        if anchor:
            maintainArray(historicalData, length, newData)
            newData = collectedData(array.new_float(), array.new_int(), time)
        array.push(newData.times, time)
        array.push(newData.data, src)
        return calcAverageByTime(historicalData, time - newData.startTime)

    @export
    @overload
    def averageAtTime(source: Series[float], length: int, timeframe__ren__: str, isCumulative: bool = True):
        historicalData: Persistent[list[collectedData]] = array.new(0, NA(collectedData))
        newData: Persistent[collectedData] = collectedData(array.new_float(), array.new_int(), time(timeframe__ren__))
        anchor: bool = timeframe.change(timeframe__ren__)
        src: float = calcCumulativeSeries(source, anchor) if isCumulative else source
        if anchor:
            maintainArray(historicalData, length, newData)
            newData = collectedData(array.new_float(), array.new_int(), time(timeframe__ren__))
        array.push(newData.times, time)
        array.push(newData.data, src)
        return calcAverageByTime(historicalData, time - newData.startTime)

    TEAL: Color = color.new(color.teal, 50)
    RED: Color = color.new(color.red, 50)
    GRAY: Color = color.new(color.gray, 70)

    showRvolInput: bool = __input_3__ == EQ01
    estimateInput: bool = __input_4__ == EQ01

    anchor: bool = timeframe.change(resetTimeInput)

    isCumulative: bool = modeInput == MI01

    pastVolume: float = averageAtTime(volume, lengthInput, resetTimeInput, isCumulative)

    currentVolume: float = calcCumulativeSeries(volume, anchor, estimateInput) if isCumulative else volume
    relativeValue: float = currentVolume / pastVolume

    def display__global__(show):
        return display.all if show else display.data_window

    plot(relativeValue, 'Relative Value', TEAL if relativeValue >= 1 else RED, 1, plot.style_columns, display=display__global__(showRvolInput), histbase=1)
    plot(pastVolume, 'Past Volume Avg', GRAY, 1, plot.style_columns, display=display__global__(not showRvolInput))
    plot(currentVolume, 'Current Volume', TEAL if close >= open else RED, 1, plot.style_columns, display=display__global__(not showRvolInput))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
