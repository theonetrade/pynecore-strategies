"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from enum import StrEnum as Enum
from pynecore import pine_loop, pine_range
from pynecore.core.overload import overload
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt, udt_copy
from pynecore.lib import (
    array, barstate, chart, close, color, fixnan, input, log, math, na, plot,
    runtime, script, string, ta, volume
)
from pynecore.types import Persistent, Series
from typing import Protocol, Any


__all__ = ['ClockBuffer', 'RingBuffer', 'SeriesType', 'alma', 'alma_back', 'alma_front', 'cust_series', 'cust_series_back', 'cust_series_front', 'dema', 'dema_back', 'dema_front', 'ema', 'ema_back', 'ema_front', 'get_curVal', 'get_shrinked_data', 'hma', 'hma_back', 'hma_front', 'index_after', 'index_before', 'init', 'linreg', 'linreg_back', 'linreg_front', 'newClockBuffer', 'newRingBuffer', 'next_index', 'prev_index', 'push_back_shift', 'push_front_pop', 'push_newVal', 'push_newVal_pop_oldVal', 'rma', 'rma_back', 'rma_front', 'rotate', 'rotate_ccw', 'rotate_cw', 'rotate_left', 'rotate_right', 'set_curVal', 'size_inc', 'sma', 'swma', 'swma_back', 'swma_front', 'vwma', 'vwma_back', 'vwma_front', 'wma', 'wma_back', 'wma_front']


class SeriesType(Enum):
    alma = 'ALMA'
    dema = 'DEMA'
    ema = 'EMA'
    hma = 'HMA'
    rma = 'RMA'
    sma = 'SMA'
    swma = 'SWMA'
    vwma = 'VWMA'
    wma = 'WMA'
    highest = 'HIGHEST'
    lowest = 'LOWEST'
    hiloestavg = 'HILOESTAVG'
    median = 'MEDIAN'
    medianHighest = 'MEDIANHIGHEST'
    medianLowest = 'MEDIANLOWEST'
    linreg = 'LINREG'
    pivotHigh = 'PIVOTHIGH'
    pivotLow = 'PIVOTLOW'
    source = 'SOURCE'


@udt
class RingBuffer:
    curIndex: int = na(int)
    size__ren__: int = na(int)
    data: list[float] = na(list)


@udt
class ClockBuffer:
    curIndex: int = na(int)
    size__ren__: int = na(int)
    data: list[float] = na(list)


class _ProtocolCustSeries(Protocol):
    def __call__(self, length: int, seriesType: SeriesType = SeriesType.sma, source: float = close) -> Any: ...


class _ProtocolCustSeries1(Protocol):
    def __call__(self, length: float, seriesType: SeriesType = SeriesType.sma, source: float = close) -> Any: ...


class _ProtocolPushFrontPop(Protocol):
    def __call__(self, this: list[float], val: float, maxItems: int) -> Any: ...


class _ProtocolRotateLeft(Protocol):
    def __call__(self, this: list[float], newFirstPos: int) -> Any: ...


class _ProtocolRotateRight(Protocol):
    def __call__(self, this: list[float], newFirstPos: int) -> Any: ...


class _ProtocolAlmaFront(Protocol):
    def __call__(self, this: list[float], offset: float = 0.85, sigma: int = 6) -> Any: ...


class _ProtocolEmaFront(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolDemaFront(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolRmaFront(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolWmaFront(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolSwmaFront(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolVwmaFront(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolHmaFront(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolLinregFront(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolCustSeriesFront(Protocol):
    def __call__(self, this: list[float], seriesType: SeriesType) -> Any: ...


class _ProtocolPushBackShift(Protocol):
    def __call__(self, this: list[float], val: float, maxItems: int) -> Any: ...


class _ProtocolAlmaBack(Protocol):
    def __call__(self, this: list[float], offset: float = 0.85, sigma: int = 6) -> Any: ...


class _ProtocolEmaBack(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolDemaBack(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolRmaBack(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolWmaBack(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolSwmaBack(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolVwmaBack(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolHmaBack(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolLinregBack(Protocol):
    def __call__(self, this: list[float]) -> Any: ...


class _ProtocolCustSeriesBack(Protocol):
    def __call__(self, this: list[float], seriesType: SeriesType) -> Any: ...


class _ProtocolNewringbuffer(Protocol):
    def __call__(self, capacity: int) -> Any: ...


class _ProtocolInit(Protocol):
    def __call__(self, this: RingBuffer, capacity: int) -> Any: ...


class _ProtocolSizeInc(Protocol):
    def __call__(self, this: RingBuffer) -> Any: ...


class _ProtocolIndexAfter(Protocol):
    def __call__(self, this: RingBuffer, index: int) -> Any: ...


class _ProtocolNextIndex(Protocol):
    def __call__(self, this: RingBuffer) -> Any: ...


class _ProtocolIndexBefore(Protocol):
    def __call__(self, this: RingBuffer, index: int) -> Any: ...


class _ProtocolPrevIndex(Protocol):
    def __call__(self, this: RingBuffer) -> Any: ...


class _ProtocolSetCurval(Protocol):
    def __call__(self, this: RingBuffer, val: float) -> Any: ...


class _ProtocolGetCurval(Protocol):
    def __call__(self, this: RingBuffer) -> Any: ...


class _ProtocolPushNewval(Protocol):
    def __call__(self, this: RingBuffer, newVal: float) -> Any: ...


class _ProtocolPushNewvalPopOldval(Protocol):
    def __call__(self, this: RingBuffer, newVal: float) -> Any: ...


class _ProtocolRotateCw(Protocol):
    def __call__(self, this: RingBuffer, position__ren__: int) -> Any: ...


class _ProtocolRotate(Protocol):
    def __call__(self, this: RingBuffer) -> Any: ...


class _ProtocolGetShrinkedData(Protocol):
    def __call__(self, this: RingBuffer) -> Any: ...


class _ProtocolSma(Protocol):
    def __call__(self, this: RingBuffer) -> Any: ...


class _ProtocolAlma(Protocol):
    def __call__(self, this: RingBuffer, offset: float = 0.85, sigma: int = 6) -> Any: ...


class _ProtocolEma(Protocol):
    def __call__(self, this: RingBuffer) -> Any: ...


class _ProtocolDema(Protocol):
    def __call__(self, this: RingBuffer) -> Any: ...


class _ProtocolRma(Protocol):
    def __call__(self, this: RingBuffer) -> Any: ...


class _ProtocolWma(Protocol):
    def __call__(self, this: RingBuffer) -> Any: ...


class _ProtocolSwma(Protocol):
    def __call__(self, this: RingBuffer) -> Any: ...


class _ProtocolVwma(Protocol):
    def __call__(self, this: RingBuffer) -> Any: ...


class _ProtocolHma(Protocol):
    def __call__(self, this: RingBuffer) -> Any: ...


class _ProtocolLinreg(Protocol):
    def __call__(self, this: RingBuffer) -> Any: ...


class _ProtocolCustSeries50(Protocol):
    def __call__(self, this: RingBuffer, seriesType: SeriesType) -> Any: ...


class _ProtocolNewclockbuffer(Protocol):
    def __call__(self, capacity: int) -> Any: ...


class _ProtocolInit52(Protocol):
    def __call__(self, this: ClockBuffer, capacity: int) -> Any: ...


class _ProtocolSizeInc53(Protocol):
    def __call__(self, this: ClockBuffer) -> Any: ...


class _ProtocolIndexAfter54(Protocol):
    def __call__(self, this: ClockBuffer, index: int) -> Any: ...


class _ProtocolNextIndex55(Protocol):
    def __call__(self, this: ClockBuffer) -> Any: ...


class _ProtocolIndexBefore56(Protocol):
    def __call__(self, this: ClockBuffer, index: int) -> Any: ...


class _ProtocolPrevIndex57(Protocol):
    def __call__(self, this: ClockBuffer) -> Any: ...


class _ProtocolSetCurval58(Protocol):
    def __call__(self, this: ClockBuffer, val: float) -> Any: ...


class _ProtocolGetCurval59(Protocol):
    def __call__(self, this: ClockBuffer) -> Any: ...


class _ProtocolPushNewval60(Protocol):
    def __call__(self, this: ClockBuffer, newVal: float) -> Any: ...


class _ProtocolPushNewvalPopOldval61(Protocol):
    def __call__(self, this: ClockBuffer, newVal: float) -> Any: ...


class _ProtocolRotateCcw(Protocol):
    def __call__(self, this: ClockBuffer, position__ren__: int) -> Any: ...


class _ProtocolRotate63(Protocol):
    def __call__(self, this: ClockBuffer) -> Any: ...


class _ProtocolGetShrinkedData64(Protocol):
    def __call__(self, this: ClockBuffer) -> Any: ...


class _ProtocolSma65(Protocol):
    def __call__(self, this: ClockBuffer) -> Any: ...


class _ProtocolAlma66(Protocol):
    def __call__(self, this: ClockBuffer, offset: float = 0.85, sigma: int = 6) -> Any: ...


class _ProtocolEma67(Protocol):
    def __call__(self, this: ClockBuffer) -> Any: ...


class _ProtocolDema68(Protocol):
    def __call__(self, this: ClockBuffer) -> Any: ...


class _ProtocolRma69(Protocol):
    def __call__(self, this: ClockBuffer) -> Any: ...


class _ProtocolWma70(Protocol):
    def __call__(self, this: ClockBuffer) -> Any: ...


class _ProtocolSwma71(Protocol):
    def __call__(self, this: ClockBuffer) -> Any: ...


class _ProtocolVwma72(Protocol):
    def __call__(self, this: ClockBuffer) -> Any: ...


class _ProtocolHma73(Protocol):
    def __call__(self, this: ClockBuffer) -> Any: ...


class _ProtocolLinreg74(Protocol):
    def __call__(self, this: ClockBuffer) -> Any: ...


class _ProtocolCustSeries75(Protocol):
    def __call__(self, this: ClockBuffer, seriesType: SeriesType) -> Any: ...


cust_series: _ProtocolCustSeries = Exported()
cust_series: _ProtocolCustSeries1 = Exported()
push_front_pop: _ProtocolPushFrontPop = Exported()
rotate_left: _ProtocolRotateLeft = Exported()
rotate_right: _ProtocolRotateRight = Exported()
alma_front: _ProtocolAlmaFront = Exported()
ema_front: _ProtocolEmaFront = Exported()
dema_front: _ProtocolDemaFront = Exported()
rma_front: _ProtocolRmaFront = Exported()
wma_front: _ProtocolWmaFront = Exported()
swma_front: _ProtocolSwmaFront = Exported()
vwma_front: _ProtocolVwmaFront = Exported()
hma_front: _ProtocolHmaFront = Exported()
linreg_front: _ProtocolLinregFront = Exported()
cust_series_front: _ProtocolCustSeriesFront = Exported()
push_back_shift: _ProtocolPushBackShift = Exported()
alma_back: _ProtocolAlmaBack = Exported()
ema_back: _ProtocolEmaBack = Exported()
dema_back: _ProtocolDemaBack = Exported()
rma_back: _ProtocolRmaBack = Exported()
wma_back: _ProtocolWmaBack = Exported()
swma_back: _ProtocolSwmaBack = Exported()
vwma_back: _ProtocolVwmaBack = Exported()
hma_back: _ProtocolHmaBack = Exported()
linreg_back: _ProtocolLinregBack = Exported()
cust_series_back: _ProtocolCustSeriesBack = Exported()
newRingBuffer: _ProtocolNewringbuffer = Exported()
init: _ProtocolInit = Exported()
size_inc: _ProtocolSizeInc = Exported()
index_after: _ProtocolIndexAfter = Exported()
next_index: _ProtocolNextIndex = Exported()
index_before: _ProtocolIndexBefore = Exported()
prev_index: _ProtocolPrevIndex = Exported()
set_curVal: _ProtocolSetCurval = Exported()
get_curVal: _ProtocolGetCurval = Exported()
push_newVal: _ProtocolPushNewval = Exported()
push_newVal_pop_oldVal: _ProtocolPushNewvalPopOldval = Exported()
rotate_cw: _ProtocolRotateCw = Exported()
rotate: _ProtocolRotate = Exported()
get_shrinked_data: _ProtocolGetShrinkedData = Exported()
sma: _ProtocolSma = Exported()
alma: _ProtocolAlma = Exported()
ema: _ProtocolEma = Exported()
dema: _ProtocolDema = Exported()
rma: _ProtocolRma = Exported()
wma: _ProtocolWma = Exported()
swma: _ProtocolSwma = Exported()
vwma: _ProtocolVwma = Exported()
hma: _ProtocolHma = Exported()
linreg: _ProtocolLinreg = Exported()
cust_series: _ProtocolCustSeries50 = Exported()
newClockBuffer: _ProtocolNewclockbuffer = Exported()
init: _ProtocolInit52 = Exported()
size_inc: _ProtocolSizeInc53 = Exported()
index_after: _ProtocolIndexAfter54 = Exported()
next_index: _ProtocolNextIndex55 = Exported()
index_before: _ProtocolIndexBefore56 = Exported()
prev_index: _ProtocolPrevIndex57 = Exported()
set_curVal: _ProtocolSetCurval58 = Exported()
get_curVal: _ProtocolGetCurval59 = Exported()
push_newVal: _ProtocolPushNewval60 = Exported()
push_newVal_pop_oldVal: _ProtocolPushNewvalPopOldval61 = Exported()
rotate_ccw: _ProtocolRotateCcw = Exported()
rotate: _ProtocolRotate63 = Exported()
get_shrinked_data: _ProtocolGetShrinkedData64 = Exported()
sma: _ProtocolSma65 = Exported()
alma: _ProtocolAlma66 = Exported()
ema: _ProtocolEma67 = Exported()
dema: _ProtocolDema68 = Exported()
rma: _ProtocolRma69 = Exported()
wma: _ProtocolWma70 = Exported()
swma: _ProtocolSwma71 = Exported()
vwma: _ProtocolVwma72 = Exported()
hma: _ProtocolHma73 = Exported()
linreg: _ProtocolLinreg74 = Exported()
cust_series: _ProtocolCustSeries75 = Exported()


@script.library(title='series_collection')
def main(
    seriesType=input.enum(defval=SeriesType.sma, title='Series Type/Src/Len', inline='Series'),
    seriesSource: Series[float] = input.source(defval=close, title='​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​', inline='Series'),
    seriesLength=input.int(defval=9, title='', minval=1, tooltip='The type, source and the length of the custom series.', inline='Series'),
    showFrontArr=input.bool(defval=True, title='Front Array'),
    showBackArr=input.bool(defval=True, title='Back Array'),
    showBufCyclic=input.bool(defval=True, title='Cyclic Buffer'),
    showBufClock=input.bool(defval=True, title='Clock Buffer'),
    offsetRot=input.int(defval=1, title='Rotate offset')
):
    @export
    @overload
    def cust_series(length: int, seriesType: SeriesType = SeriesType.sma, source: float = close):
        __block_result__ = na
        __switch__ = seriesType
        if __switch__ == SeriesType.alma:
            __block_result__ = ta.alma(source, length, 0.85, 6)
        elif __switch__ == SeriesType.dema:
            ema__00000007__ = ta.ema(source, length)
            __block_result__ = 2 * ema__00000007__ - ta.ema(ema__00000007__, length)
        elif __switch__ == SeriesType.ema:
            __block_result__ = ta.ema(source, length)
        elif __switch__ == SeriesType.hma:
            __block_result__ = ta.hma(source, length)
        elif __switch__ == SeriesType.rma:
            __block_result__ = ta.rma(source, length)
        elif __switch__ == SeriesType.sma:
            __block_result__ = ta.sma(source, length)
        elif __switch__ == SeriesType.swma:
            __block_result__ = ta.swma(source)
        elif __switch__ == SeriesType.vwma:
            __block_result__ = ta.vwma(source, length)
        elif __switch__ == SeriesType.wma:
            __block_result__ = ta.wma(source, length)
        elif __switch__ == SeriesType.highest:
            __block_result__ = ta.highest(source, length)
        elif __switch__ == SeriesType.lowest:
            __block_result__ = ta.lowest(source, length)
        elif __switch__ == SeriesType.hiloestavg:
            __block_result__ = (ta.lowest(source, length) + ta.highest(source, length)) / 2
        elif __switch__ == SeriesType.median:
            __block_result__ = ta.median(source, length)
        elif __switch__ == SeriesType.medianHighest:
            __block_result__ = ta.median(ta.highest(source, length), length)
        elif __switch__ == SeriesType.medianLowest:
            __block_result__ = ta.median(ta.lowest(source, length), length)
        elif __switch__ == SeriesType.linreg:
            __block_result__ = ta.linreg(source, length, 0)
        elif __switch__ == SeriesType.pivotHigh:
            __block_result__ = fixnan(ta.pivothigh(source, length, 2))
        elif __switch__ == SeriesType.pivotLow:
            __block_result__ = fixnan(ta.pivotlow(source, length, 2))
        elif __switch__ == SeriesType.source:
            __block_result__ = source
        else:
            runtime.error(string.tostring(seriesType) + ' is not a supported series type. The supported types are [ALMA, DEMA, EMA, HMA, RMA, SMA, SWMA, VWMA, WMA, HIGHEST, LOWEST, HILOESTAVG, MEDIAN, MEDIANHIGHEST, MEDIANLOWEST, LINREG, PIVOTHIGH, PIVOTLOW, SOURCE]')
            __block_result__ = na
        return __block_result__

    @export
    @overload
    def cust_series(length: float, seriesType: SeriesType = SeriesType.sma, source: float = close):
        return cust_series(math.ceil(length), seriesType, source)

    @export
    @method
    def push_front_pop(this: list[float], val: float, maxItems: int):
        array.unshift(this, val)
        __block_result_1__ = na
        while array.size(this) > maxItems:
            __block_result_1__ = array.pop(this)
        return __block_result_1__

    @method
    def normalize_index(this: list[float], index):
        size__ren__: int = array.size(this)
        i: int = index
        while i < 0:
            i += size__ren__
        while i >= size__ren__:
            i -= size__ren__
        return i

    @overload
    @method
    def rotate(this: list[float], newFirstPos: int):
        return array.concat(udt_copy(array.slice(this, newFirstPos, array.size(this))), array.slice(this, 0, newFirstPos))

    @export
    @method
    def rotate_left(this: list[float], newFirstPos: int):
        pos: int = normalize_index(this, newFirstPos)
        return rotate(this, pos)

    @export
    @method
    def rotate_right(this: list[float], newFirstPos: int):
        return rotate_left(this, array.size(this) - newFirstPos)

    @export
    @method
    def alma_front(this: list[float], offset: float = 0.85, sigma: int = 6):
        length: int = array.size(this)
        m: float = offset * (length - 1)
        s: float = length / sigma
        norm: float = 0.0
        sum: float = 0.0
        for i, src in enumerate(this):
            weight: float = math.exp(-1 * math.pow(i - m, 2) / (2 * math.pow(s, 2)))
            norm += weight
            sum += array.get(this, length - 1 - i) * weight
        return sum / norm

    @export
    @method
    def ema_front(this: list[float]):
        mostRecent: float = array.first(this)
        k: float = 2 / (array.size(this) + 1)
        ema__00000053__: Persistent[float] = mostRecent
        ema__00000053__ = mostRecent * k + (1 - k) * ema__00000053__
        return ema__00000053__

    @export
    @method
    def dema_front(this: list[float]):
        mostRecent: float = array.first(this)
        k: float = 2 / (array.size(this) + 1)
        ema__00000056__: Persistent[float] = mostRecent
        ema__00000056__ = mostRecent * k + (1 - k) * ema__00000056__
        dema__00000056__: Persistent[float] = ema__00000056__
        dema__00000056__ = ema__00000056__ * k + (1 - k) * dema__00000056__
        return 2 * ema__00000056__ - dema__00000056__

    @export
    @method
    def rma_front(this: list[float]):
        mostRecent: float = array.first(this)
        length: int = array.size(this)
        ma: Persistent[float] = mostRecent
        ma = (ma * (length - 1) + mostRecent) / length
        return ma

    @export
    @method
    def wma_front(this: list[float]):
        length: int = array.size(this)
        lenSum: float = length * (length + 1) / 2
        maSum: float = 0.0
        for i, src in enumerate(this):
            maSum += src * (length - i)
        return maSum / lenSum

    @export
    @method
    def swma_front(this: list[float]):
        __block_result_2__ = na
        if array.size(this) >= 4:
            __block_result_2__ = array.get(this, 3) / 6 + array.get(this, 2) / 3 + array.get(this, 1) / 3 + array.get(this, 0) / 6
        else:
            __block_result_2__ = na
        return __block_result_2__

    @export
    @method
    def vwma_front(this: list[float]):
        length: int = array.size(this)
        volWeighted: Persistent[list[float]] = array.new_float()
        push_front_pop(volWeighted, array.get(this, 0) * volume, length)
        return array.sum(volWeighted) / math.sum(volume, array.size(this))

    @export
    @method
    def hma_front(this: list[float]):
        length: int = array.size(this)
        wmaSlow: float = wma_front(this)
        wmaFast: float = wma_front(array.slice(this, 0, math.max(cast_int(length / 2), 1)))
        rawHmaRange: Persistent[list[float]] = array.new_float()
        push_front_pop(rawHmaRange, 2 * wmaFast - wmaSlow, cast_int(math.sqrt(length)))
        return wma_front(rawHmaRange)

    @export
    @method
    def linreg_front(this: list[float]):
        length: int = array.size(this)
        sumX: float = length * (length + 1) / 2
        sumY: float = array.sum(this)
        sumXY: float = 0.0
        sumX2: float = 0.0
        for i, src in enumerate(this):
            j: int = length - i
            sumXY += j * src
            sumX2 += math.pow(j, 2)

        den: float = length * sumX2 - math.pow(sumX, 2)
        a: float = (length * sumXY - sumX * sumY) / den
        b: float = (sumY * sumX2 - sumX * sumXY) / den

        return a * length + b

    @export
    @method
    def cust_series_front(this: list[float], seriesType: SeriesType):
        __block_result_3__ = na
        __switch__ = seriesType
        if __switch__ == SeriesType.alma:
            __block_result_3__ = alma_front(this)
        elif __switch__ == SeriesType.dema:
            __block_result_3__ = dema_front(this)
        elif __switch__ == SeriesType.ema:
            __block_result_3__ = ema_front(this)
        elif __switch__ == SeriesType.hma:
            __block_result_3__ = hma_front(this)
        elif __switch__ == SeriesType.rma:
            __block_result_3__ = rma_front(this)
        elif __switch__ == SeriesType.sma:
            __block_result_3__ = array.avg(this)
        elif __switch__ == SeriesType.swma:
            __block_result_3__ = swma_front(this)
        elif __switch__ == SeriesType.vwma:
            __block_result_3__ = vwma_front(this)
        elif __switch__ == SeriesType.wma:
            __block_result_3__ = wma_front(this)
        elif __switch__ == SeriesType.highest:
            __block_result_3__ = array.max(this)
        elif __switch__ == SeriesType.lowest:
            __block_result_3__ = array.min(this)
        elif __switch__ == SeriesType.hiloestavg:
            __block_result_3__ = (array.min(this) + array.max(this)) / 2
        elif __switch__ == SeriesType.median:
            __block_result_3__ = array.median(this)
        elif __switch__ == SeriesType.medianHighest:
            __block_result_3__ = ta.median(array.max(this), array.size(this))
        elif __switch__ == SeriesType.medianLowest:
            __block_result_3__ = ta.median(array.min(this), array.size(this))
        elif __switch__ == SeriesType.linreg:
            __block_result_3__ = linreg_front(this)
        else:
            runtime.error(string.tostring(seriesType) + ' is not a supported series type. The supported types are [ALMA, DEMA, EMA, HMA, RMA, SMA, SWMA, VWMA, WMA, HIGHEST, LOWEST, HILOESTAVG, MEDIAN, MEDIANHIGHEST, MEDIANLOWEST, LINREG]')
            __block_result_3__ = na
        return __block_result_3__

    @export
    @method
    def push_back_shift(this: list[float], val: float, maxItems: int):
        array.push(this, val)
        __block_result_4__ = na
        while array.size(this) > maxItems:
            __block_result_4__ = array.shift(this)
        return __block_result_4__

    @export
    @method
    def alma_back(this: list[float], offset: float = 0.85, sigma: int = 6):
        length: int = array.size(this)
        m: float = offset * (length - 1)
        s: float = length / sigma
        norm: float = 0.0
        sum: float = 0.0
        for i, src in enumerate(this):
            weight: float = math.exp(-1 * math.pow(i - m, 2) / (2 * math.pow(s, 2)))
            norm += weight
            sum += src * weight
        return sum / norm

    @export
    @method
    def ema_back(this: list[float]):
        mostRecent: float = array.last(this)
        k: float = 2 / (array.size(this) + 1)
        ma: Persistent[float] = mostRecent
        ma = mostRecent * k + (1 - k) * ma
        return ma

    @export
    @method
    def dema_back(this: list[float]):
        mostRecent: float = array.last(this)
        k: float = 2 / (array.size(this) + 1)
        ema__000000b6__: Persistent[float] = mostRecent
        ema__000000b6__ = mostRecent * k + (1 - k) * ema__000000b6__
        dema__000000b6__: Persistent[float] = ema__000000b6__
        dema__000000b6__ = ema__000000b6__ * k + (1 - k) * dema__000000b6__
        return 2 * ema__000000b6__ - dema__000000b6__

    @export
    @method
    def rma_back(this: list[float]):
        mostRecent: float = array.last(this)
        length: int = array.size(this)
        ma: Persistent[float] = mostRecent
        ma = (ma * (length - 1) + mostRecent) / length
        return ma

    @export
    @method
    def wma_back(this: list[float]):
        length: int = array.size(this)
        lenSum: float = length * (length + 1) / 2
        maSum: float = 0.0
        for i, src in enumerate(this):
            maSum += src * (i + 1)
        return maSum / lenSum

    @export
    @method
    def swma_back(this: list[float]):
        __block_result_5__ = na
        if array.size(this) >= 4:
            __block_result_5__ = array.get(this, array.size(this) - 1) / 6 + array.get(this, array.size(this) - 2) / 3 + array.get(this, array.size(this) - 3) / 3 + array.get(this, array.size(this) - 4) / 6
        else:
            __block_result_5__ = na
        return __block_result_5__

    @export
    @method
    def vwma_back(this: list[float]):
        length: int = array.size(this)
        volWeighted: Persistent[list[float]] = array.new_float()
        push_back_shift(volWeighted, array.get(this, array.size(this) - 1) * volume, length)
        return array.sum(volWeighted) / math.sum(volume, array.size(this))

    @export
    @method
    def hma_back(this: list[float]):
        length: int = array.size(this)
        wmaSlow: float = wma_back(this)
        wmaFast: float = wma_back(array.slice(this, math.min(length - cast_int(length / 2), length - 1), length))
        rawHmaRange: Persistent[list[float]] = array.new_float()
        push_back_shift(rawHmaRange, 2 * wmaFast - wmaSlow, cast_int(math.sqrt(length)))
        return wma_back(rawHmaRange)

    @export
    @method
    def linreg_back(this: list[float]):
        length: int = array.size(this)
        sumX: float = length * (length + 1) / 2
        sumY: float = array.sum(this)
        sumXY: float = 0.0
        sumX2: float = 0.0
        for i, src in enumerate(this):
            j: int = i + 1
            sumXY += j * src
            sumX2 += math.pow(j, 2)

        den: float = length * sumX2 - math.pow(sumX, 2)
        a: float = (length * sumXY - sumX * sumY) / den
        b: float = (sumY * sumX2 - sumX * sumXY) / den

        return a * length + b

    @export
    @method
    def cust_series_back(this: list[float], seriesType: SeriesType):
        __block_result_6__ = na
        __switch__ = seriesType
        if __switch__ == SeriesType.alma:
            __block_result_6__ = alma_back(this)
        elif __switch__ == SeriesType.dema:
            __block_result_6__ = dema_back(this)
        elif __switch__ == SeriesType.ema:
            __block_result_6__ = ema_back(this)
        elif __switch__ == SeriesType.hma:
            __block_result_6__ = hma_back(this)
        elif __switch__ == SeriesType.rma:
            __block_result_6__ = rma_back(this)
        elif __switch__ == SeriesType.sma:
            __block_result_6__ = array.avg(this)
        elif __switch__ == SeriesType.swma:
            __block_result_6__ = swma_back(this)
        elif __switch__ == SeriesType.vwma:
            __block_result_6__ = vwma_back(this)
        elif __switch__ == SeriesType.wma:
            __block_result_6__ = wma_back(this)
        elif __switch__ == SeriesType.highest:
            __block_result_6__ = array.max(this)
        elif __switch__ == SeriesType.lowest:
            __block_result_6__ = array.min(this)
        elif __switch__ == SeriesType.hiloestavg:
            __block_result_6__ = (array.min(this) + array.max(this)) / 2
        elif __switch__ == SeriesType.median:
            __block_result_6__ = array.median(this)
        elif __switch__ == SeriesType.medianHighest:
            __block_result_6__ = ta.median(array.max(this), array.size(this))
        elif __switch__ == SeriesType.medianLowest:
            __block_result_6__ = ta.median(array.min(this), array.size(this))
        elif __switch__ == SeriesType.linreg:
            __block_result_6__ = linreg_back(this)
        else:
            runtime.error(string.tostring(seriesType) + ' is not a supported series type. The supported types are [ALMA, DEMA, EMA, HMA, RMA, SMA, SWMA, VWMA, WMA, HIGHEST, LOWEST, HILOESTAVG, MEDIAN, MEDIANHIGHEST, MEDIANLOWEST, LINREG]')
            __block_result_6__ = na
        return __block_result_6__


    @export
    def newRingBuffer(capacity: int):
        return RingBuffer(capacity, 0, array.new_float(capacity))

    @export
    @overload
    @method
    def init(this: RingBuffer, capacity: int):
        this.curIndex = capacity
        this.size__ren__ = 0
        this.data = array.new_float(capacity)
        return this

    @export
    @overload
    @method
    def size_inc(this: RingBuffer):
        this.size__ren__ = this.size__ren__ if this.size__ren__ == array.size(this.data) else this.size__ren__ + 1
        return this.size__ren__

    @export
    @overload
    @method
    def index_after(this: RingBuffer, index: int):
        return array.size(this.data) - 1 if index <= array.size(this.data) - this.size__ren__ else index - 1

    @export
    @overload
    @method
    def next_index(this: RingBuffer):
        return index_after(this, this.curIndex)

    @export
    @overload
    @method
    def index_before(this: RingBuffer, index: int):
        return array.size(this.data) - this.size__ren__ if index >= array.size(this.data) - 1 else index + 1

    @export
    @overload
    @method
    def prev_index(this: RingBuffer):
        return index_before(this, this.curIndex)

    @export
    @overload
    @method
    def set_curVal(this: RingBuffer, val: float):
        return array.set(this.data, this.curIndex, val)

    @export
    @overload
    @method
    def get_curVal(this: RingBuffer):
        return array.get(this.data, this.curIndex)

    @export
    @overload
    @method
    def push_newVal(this: RingBuffer, newVal: float):
        size_inc(this)
        this.curIndex = next_index(this)
        return set_curVal(this, newVal)

    @export
    @overload
    @method
    def push_newVal_pop_oldVal(this: RingBuffer, newVal: float):
        size_inc(this)
        this.curIndex = next_index(this)
        oldVal = get_curVal(this)
        set_curVal(this, newVal)
        return oldVal

    @export
    @method
    def rotate_cw(this: RingBuffer, position__ren__: int):
        this.data = rotate(this.data, normalize_index(this.data, array.size(this.data) - position__ren__))
        this.curIndex = normalize_index(this.data, this.curIndex + position__ren__)
        return this

    @export
    @overload
    @method
    def rotate(this: RingBuffer):
        this.data = array.concat(udt_copy(array.slice(this.data, this.curIndex, array.size(this.data))), array.slice(this.data, 0, this.curIndex))
        this.curIndex = 0
        return this

    @export
    @overload
    @method
    def get_shrinked_data(this: RingBuffer):
        return method_call('slice', rotate(this).data, 0, this.size__ren__)

    @export
    @overload
    @method
    def sma(this: RingBuffer):
        return array.avg(this.data)

    @export
    @overload
    @method
    def alma(this: RingBuffer, offset: float = 0.85, sigma: int = 6):
        arr: list[float] = get_shrinked_data(this)
        return alma_front(arr, offset, sigma)

    @export
    @overload
    @method
    def ema(this: RingBuffer):
        mostRecent: float = get_curVal(this)
        k: float = 2 / (this.size__ren__ + 1)
        ma: Persistent[float] = mostRecent
        ma = mostRecent * k + (1 - k) * ma
        return ma

    @export
    @overload
    @method
    def dema(this: RingBuffer):
        mostRecent: float = get_curVal(this)
        k: float = 2 / (this.size__ren__ + 1)
        ema__00000140__: Persistent[float] = mostRecent
        ema__00000140__ = mostRecent * k + (1 - k) * ema__00000140__
        dema__00000140__: Persistent[float] = ema__00000140__
        dema__00000140__ = ema__00000140__ * k + (1 - k) * dema__00000140__
        return 2 * ema__00000140__ - dema__00000140__

    @export
    @overload
    @method
    def rma(this: RingBuffer):
        mostRecent: float = get_curVal(this)
        length: int = this.size__ren__
        ma: Persistent[float] = mostRecent
        ma = (ma * (length - 1) + mostRecent) / length
        return ma

    @export
    @overload
    @method
    def wma(this: RingBuffer):
        length: int = this.size__ren__
        lenSum: float = length * (length + 1) / 2
        maSum: float = 0.0
        __loop_0__ = pine_loop(array.size(this.data) - length)
        while __loop_0__.step(array.size(this.data) - 1):
            i = __loop_0__.value
            j: int = this.curIndex - i
            maSum += array.get(this.data, i) * (length + j if j <= 0 else j)
        return maSum / lenSum

    @export
    @overload
    @method
    def swma(this: RingBuffer):
        index0: int = this.curIndex
        index1: int = index_before(this, index0)
        index2: int = index_before(this, index1)
        index3: int = index_before(this, index2)
        return array.get(this.data, index0) / 6 + array.get(this.data, index1) / 3 + array.get(this.data, index2) / 3 + array.get(this.data, index3) / 6

    @export
    @overload
    @method
    def vwma(this: RingBuffer):
        volWeighted: Persistent = newRingBuffer(array.size(this.data))
        method_call('push_newVal', volWeighted, get_curVal(this) * volume)
        return method_call('sum', volWeighted.data) / math.sum(volume, this.size__ren__)

    @export
    @overload
    @method
    def hma(this: RingBuffer):
        arr: list[float] = get_shrinked_data(this)
        return hma_front(arr)

    @export
    @overload
    @method
    def linreg(this: RingBuffer):
        arr: list[float] = get_shrinked_data(this)
        return linreg_front(arr)

    @export
    @overload
    @method
    def cust_series(this: RingBuffer, seriesType: SeriesType):
        __block_result_7__ = na
        __switch__ = seriesType
        if __switch__ == SeriesType.alma:
            __block_result_7__ = alma(this)
        elif __switch__ == SeriesType.dema:
            __block_result_7__ = dema(this)
        elif __switch__ == SeriesType.ema:
            __block_result_7__ = ema(this)
        elif __switch__ == SeriesType.hma:
            __block_result_7__ = hma(this)
        elif __switch__ == SeriesType.rma:
            __block_result_7__ = rma(this)
        elif __switch__ == SeriesType.sma:
            __block_result_7__ = sma(this)
        elif __switch__ == SeriesType.swma:
            __block_result_7__ = swma(this)
        elif __switch__ == SeriesType.vwma:
            __block_result_7__ = vwma(this)
        elif __switch__ == SeriesType.wma:
            __block_result_7__ = wma(this)
        elif __switch__ == SeriesType.highest:
            __block_result_7__ = array.max(this.data)
        elif __switch__ == SeriesType.lowest:
            __block_result_7__ = array.min(this.data)
        elif __switch__ == SeriesType.hiloestavg:
            __block_result_7__ = (array.min(this.data) + array.max(this.data)) / 2
        elif __switch__ == SeriesType.median:
            __block_result_7__ = array.median(this.data)
        elif __switch__ == SeriesType.medianHighest:
            __block_result_7__ = ta.median(array.max(this.data), this.size__ren__)
        elif __switch__ == SeriesType.medianLowest:
            __block_result_7__ = ta.median(array.min(this.data), this.size__ren__)
        elif __switch__ == SeriesType.linreg:
            __block_result_7__ = linreg(this)
        else:
            runtime.error(string.tostring(seriesType) + ' is not a supported series type. The supported types are [ALMA, DEMA, EMA, HMA, RMA, SMA, SWMA, VWMA, WMA, HIGHEST, LOWEST, HILOESTAVG, MEDIAN, MEDIANHIGHEST, MEDIANLOWEST, LINREG]')
            __block_result_7__ = na
        return __block_result_7__


    @export
    def newClockBuffer(capacity: int):
        return ClockBuffer(-1, 0, array.new_float(capacity))

    @export
    @overload
    @method
    def init(this: ClockBuffer, capacity: int):
        this.curIndex = -1
        this.size__ren__ = 0
        this.data = array.new_float(capacity)
        return this

    @export
    @overload
    @method
    def size_inc(this: ClockBuffer):
        this.size__ren__ = this.size__ren__ if this.size__ren__ == array.size(this.data) else this.size__ren__ + 1
        return this.size__ren__

    @export
    @overload
    @method
    def index_after(this: ClockBuffer, index: int):
        return 0 if index >= this.size__ren__ - 1 else index + 1

    @export
    @overload
    @method
    def next_index(this: ClockBuffer):
        return index_after(this, this.curIndex)

    @export
    @overload
    @method
    def index_before(this: ClockBuffer, index: int):
        return this.size__ren__ - 1 if index <= 0 else index - 1

    @export
    @overload
    @method
    def prev_index(this: ClockBuffer):
        return index_before(this, this.curIndex)

    @export
    @overload
    @method
    def set_curVal(this: ClockBuffer, val: float):
        return array.set(this.data, this.curIndex, val)

    @export
    @overload
    @method
    def get_curVal(this: ClockBuffer):
        return array.get(this.data, this.curIndex)

    @export
    @overload
    @method
    def push_newVal(this: ClockBuffer, newVal: float):
        size_inc(this)
        this.curIndex = next_index(this)
        return set_curVal(this, newVal)

    @export
    @overload
    @method
    def push_newVal_pop_oldVal(this: ClockBuffer, newVal: float):
        size_inc(this)
        this.curIndex = next_index(this)
        oldVal = get_curVal(this)
        set_curVal(this, newVal)
        return oldVal

    @export
    @method
    def rotate_ccw(this: ClockBuffer, position__ren__: int):
        this.data = rotate(this.data, normalize_index(this.data, position__ren__))
        this.curIndex = normalize_index(this.data, this.curIndex - position__ren__)
        return this

    @export
    @overload
    @method
    def rotate(this: ClockBuffer):
        capacity: int = array.size(this.data)
        i: int = this.curIndex + 1 - capacity if this.curIndex + 1 >= capacity else this.curIndex + 1
        this.data = array.concat(udt_copy(array.slice(this.data, i, capacity)), array.slice(this.data, 0, i))
        this.curIndex = capacity - 1
        return this

    @export
    @overload
    @method
    def get_shrinked_data(this: ClockBuffer):
        return method_call('slice', rotate(this).data, array.size(this.data) - this.size__ren__, array.size(this.data))

    @export
    @overload
    @method
    def sma(this: ClockBuffer):
        return array.avg(this.data)

    @export
    @overload
    @method
    def alma(this: ClockBuffer, offset: float = 0.85, sigma: int = 6):
        arr: list[float] = get_shrinked_data(this)
        return alma_back(arr, offset, sigma)

    @export
    @overload
    @method
    def ema(this: ClockBuffer):
        mostRecent: float = get_curVal(this)
        k: float = 2 / (this.size__ren__ + 1)
        ma: Persistent[float] = mostRecent
        ma = mostRecent * k + (1 - k) * ma
        return ma

    @export
    @overload
    @method
    def dema(this: ClockBuffer):
        mostRecent: float = get_curVal(this)
        k: float = 2 / (this.size__ren__ + 1)
        ema__000001b6__: Persistent[float] = mostRecent
        ema__000001b6__ = mostRecent * k + (1 - k) * ema__000001b6__
        dema__000001b6__: Persistent[float] = ema__000001b6__
        dema__000001b6__ = ema__000001b6__ * k + (1 - k) * dema__000001b6__
        return 2 * ema__000001b6__ - dema__000001b6__

    @export
    @overload
    @method
    def rma(this: ClockBuffer):
        mostRecent: float = get_curVal(this)
        length: int = this.size__ren__
        ma: Persistent[float] = mostRecent
        ma = (ma * (length - 1) + mostRecent) / length
        return ma

    @export
    @overload
    @method
    def wma(this: ClockBuffer):
        length: int = this.size__ren__
        lenSum: float = length * (length + 1) / 2
        maSum: float = 0.0
        for i in pine_range(0, length - 1):
            j: int = i - this.curIndex
            maSum += array.get(this.data, i) * (j if j > 0 else length + j)
        return maSum / lenSum

    @export
    @overload
    @method
    def swma(this: ClockBuffer):
        index0: int = this.curIndex
        index1: int = index_before(this, index0)
        index2: int = index_before(this, index1)
        index3: int = index_before(this, index2)
        return array.get(this.data, index0) / 6 + array.get(this.data, index1) / 3 + array.get(this.data, index2) / 3 + array.get(this.data, index3) / 6

    @export
    @overload
    @method
    def vwma(this: ClockBuffer):
        volWeighted: Persistent = newClockBuffer(array.size(this.data))
        method_call('push_newVal', volWeighted, get_curVal(this) * volume)
        return method_call('sum', volWeighted.data) / math.sum(volume, this.size__ren__)

    @export
    @overload
    @method
    def hma(this: ClockBuffer):
        arr: list[float] = get_shrinked_data(this)
        return hma_back(arr)

    @export
    @overload
    @method
    def linreg(this: ClockBuffer):
        arr: list[float] = get_shrinked_data(this)
        return linreg_back(arr)

    @export
    @overload
    @method
    def cust_series(this: ClockBuffer, seriesType: SeriesType):
        __block_result_8__ = na
        __switch__ = seriesType
        if __switch__ == SeriesType.alma:
            __block_result_8__ = alma(this)
        elif __switch__ == SeriesType.dema:
            __block_result_8__ = dema(this)
        elif __switch__ == SeriesType.ema:
            __block_result_8__ = ema(this)
        elif __switch__ == SeriesType.hma:
            __block_result_8__ = hma(this)
        elif __switch__ == SeriesType.rma:
            __block_result_8__ = rma(this)
        elif __switch__ == SeriesType.sma:
            __block_result_8__ = sma(this)
        elif __switch__ == SeriesType.swma:
            __block_result_8__ = swma(this)
        elif __switch__ == SeriesType.vwma:
            __block_result_8__ = vwma(this)
        elif __switch__ == SeriesType.wma:
            __block_result_8__ = wma(this)
        elif __switch__ == SeriesType.highest:
            __block_result_8__ = array.max(this.data)
        elif __switch__ == SeriesType.lowest:
            __block_result_8__ = array.min(this.data)
        elif __switch__ == SeriesType.hiloestavg:
            __block_result_8__ = (array.min(this.data) + array.max(this.data)) / 2
        elif __switch__ == SeriesType.median:
            __block_result_8__ = array.median(this.data)
        elif __switch__ == SeriesType.medianHighest:
            __block_result_8__ = ta.median(array.max(this.data), this.size__ren__)
        elif __switch__ == SeriesType.medianLowest:
            __block_result_8__ = ta.median(array.min(this.data), this.size__ren__)
        elif __switch__ == SeriesType.linreg:
            __block_result_8__ = linreg(this)
        else:
            runtime.error(string.tostring(seriesType) + ' is not a supported series type. The supported types are [ALMA, DEMA, EMA, HMA, RMA, SMA, SWMA, VWMA, WMA, HIGHEST, LOWEST, HILOESTAVG, MEDIAN, MEDIANHIGHEST, MEDIANLOWEST, LINREG]')
            __block_result_8__ = na
        return __block_result_8__

    seriesLine: float = cust_series(seriesLength, seriesType, seriesSource)

    arrFrontLine: float = na(float)
    if showFrontArr:
        arrFront: Persistent[list[float]] = array.new_float()
        valPopped: float = push_front_pop(arrFront, close, seriesLength)
        arrFrontLine = cust_series_front(arrFront, seriesType)

    arrBackLine: float = na(float)
    if showBackArr:
        arrBack: Persistent[list[float]] = array.new_float()
        valShifted: float = push_back_shift(arrBack, close, seriesLength)
        arrBackLine = cust_series_back(arrBack, seriesType)

    ringBufLine: float = na(float)
    if showBufCyclic:
        bufCyclic: Persistent = newRingBuffer(seriesLength)
        method_call('push_newVal', bufCyclic, close)
        ringBufLine = method_call('cust_series', bufCyclic, seriesType)

    clockBufLine: float = na(float)
    if showBufClock:
        bufClock: Persistent = newClockBuffer(seriesLength)
        method_call('push_newVal', bufClock, close)
        clockBufLine = method_call('cust_series', bufClock, seriesType)

    if barstate.islastconfirmedhistory:
        testArr: Persistent[list[float]] = array.from_items(0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0)
        log.info('testArr rot LEFT: {0}', rotate_left(testArr, offsetRot))
        log.info('testArr: {0}', testArr)
        log.info('testArr rot RIGHT: {0}', rotate_right(testArr, offsetRot))

        testClockBuf: Persistent = newClockBuffer(10)
        method_call('push_newVal', testClockBuf, 0)
        method_call('push_newVal', testClockBuf, 1)
        method_call('push_newVal', testClockBuf, 2)
        method_call('push_newVal', testClockBuf, 3)
        method_call('push_newVal', testClockBuf, 4)
        method_call('push_newVal', testClockBuf, 5)
        method_call('push_newVal', testClockBuf, 6)
        method_call('push_newVal', testClockBuf, 7)
        method_call('push_newVal', testClockBuf, 8)
        log.info('testClockBuf: {0}, curIndex: {1}', testClockBuf.data, testClockBuf.curIndex)
        log.info('testClockBuf rot CCW: {0}, curIndex: {1}', rotate_ccw(testClockBuf, offsetRot).data, testClockBuf.curIndex)
        log.info('testClockBuf rot ALL: {0}, curIndex: {1}', rotate(testClockBuf).data, testClockBuf.curIndex)

        testRingBuf: Persistent = newRingBuffer(10)
        method_call('push_newVal', testRingBuf, 0)
        method_call('push_newVal', testRingBuf, 1)
        method_call('push_newVal', testRingBuf, 2)
        method_call('push_newVal', testRingBuf, 3)
        method_call('push_newVal', testRingBuf, 4)
        method_call('push_newVal', testRingBuf, 5)
        method_call('push_newVal', testRingBuf, 6)
        method_call('push_newVal', testRingBuf, 7)
        method_call('push_newVal', testRingBuf, 8)
        log.info('testRingBuf: {0}, curIndex: {1}', testRingBuf.data, testRingBuf.curIndex)
        log.info('testRingBuf rot CW: {0}, curIndex: {1}', rotate_cw(testRingBuf, offsetRot).data, testRingBuf.curIndex)
        log.info('testRingBuf rot ALL: {0}, curIndex: {1}', rotate(testRingBuf).data, testRingBuf.curIndex)

    plot(series=seriesLine, color=chart.fg_color, style=plot.style_linebr, linewidth=2, title='Custom Series', force_overlay=True)

    plot(series=arrFrontLine, color=color.aqua, style=plot.style_linebr, linewidth=2, title='Front Array Series', force_overlay=True)
    plot(series=arrBackLine, color=color.yellow, style=plot.style_linebr, linewidth=2, title='Back Array Series', force_overlay=True)

    plot(series=ringBufLine, color=color.green, style=plot.style_linebr, linewidth=2, title='Ring Buffer Series', force_overlay=True)
    plot(series=clockBufLine, color=color.red, style=plot.style_linebr, linewidth=2, title='Clock Buffer Series', force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
