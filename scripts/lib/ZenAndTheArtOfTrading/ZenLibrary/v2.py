"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    close, dayofweek, high, low, math, na, open, script, syminfo, ta, table,
    time, timeframe
)
from pynecore.types import Color, Table
from typing import Protocol, Any


__all__ = ['atrFilter', 'av_getPositionSize', 'barsAboveMA', 'barsBelowMA', 'barsCrossedMA', 'dateFilter', 'dayFilter', 'fillCell', 'getBodyPercent', 'getBodySize', 'getBottomWickSize', 'getDecimals', 'getEAP', 'getMA', 'getPullbackBarCount', 'getTopWickSize', 'isBearishEC', 'isBullishEC', 'isDoji', 'isHammer', 'isStar', 'timeFilter', 'toPips', 'toWhole', 'truncate']


class _ProtocolGetdecimals(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolTruncate(Protocol):
    def __call__(self, _number: float, _decimalPlaces: float = 2.0) -> Any: ...


class _ProtocolTowhole(Protocol):
    def __call__(self, _number: float) -> Any: ...


class _ProtocolTopips(Protocol):
    def __call__(self, _number: float) -> Any: ...


class _ProtocolAvGetpositionsize(Protocol):
    def __call__(self, _balance: float, _risk: float, _stopPoints: float, _conversionRate: float) -> Any: ...


class _ProtocolGetma(Protocol):
    def __call__(self, _length: int, _maType: str) -> Any: ...


class _ProtocolGeteap(Protocol):
    def __call__(self, _atr: float) -> Any: ...


class _ProtocolBarsabovema(Protocol):
    def __call__(self, _lookback: int, _ma: float) -> Any: ...


class _ProtocolBarsbelowma(Protocol):
    def __call__(self, _lookback: int, _ma: float) -> Any: ...


class _ProtocolBarscrossedma(Protocol):
    def __call__(self, _lookback: int, _ma: float) -> Any: ...


class _ProtocolGetpullbackbarcount(Protocol):
    def __call__(self, _lookback: int, _direction: int) -> Any: ...


class _ProtocolGetbodysize(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolGettopwicksize(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolGetbottomwicksize(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolGetbodypercent(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolIshammer(Protocol):
    def __call__(self, _fib: float = 0.382, _colorMatch: bool = False) -> Any: ...


class _ProtocolIsstar(Protocol):
    def __call__(self, _fib: float = 0.382, _colorMatch: bool = False) -> Any: ...


class _ProtocolIsdoji(Protocol):
    def __call__(self, _wickSize: float = 2.0, _bodySize: float = 0.05) -> Any: ...


class _ProtocolIsbullishec(Protocol):
    def __call__(self, _allowance: float = 0.0, _rejectionWickSize: float = 0.0, _engulfWick: bool = False) -> Any: ...


class _ProtocolIsbearishec(Protocol):
    def __call__(self, _allowance: float = 0.0, _rejectionWickSize: float = 0.0, _engulfWick: bool = False) -> Any: ...


class _ProtocolTimefilter(Protocol):
    def __call__(self, _sess: str, _useFilter: bool = False) -> Any: ...


class _ProtocolDatefilter(Protocol):
    def __call__(self, _startTime: int, _endTime: int) -> Any: ...


class _ProtocolDayfilter(Protocol):
    def __call__(self, _monday: bool, _tuesday: bool, _wednesday: bool, _thursday: bool, _friday: bool, _saturday: bool, _sunday: bool) -> Any: ...


class _ProtocolAtrfilter(Protocol):
    def __call__(self, _atr: float = 1111, _maxSize: float = ...) -> Any: ...


class _ProtocolFillcell(Protocol):
    def __call__(self, _table: Table, _column: int, _row: int, _title: str, _value: str, _bgcolor: Color, _txtcolor: Color) -> Any: ...


getDecimals: _ProtocolGetdecimals = Exported()
truncate: _ProtocolTruncate = Exported()
toWhole: _ProtocolTowhole = Exported()
toPips: _ProtocolTopips = Exported()
av_getPositionSize: _ProtocolAvGetpositionsize = Exported()
getMA: _ProtocolGetma = Exported()
getEAP: _ProtocolGeteap = Exported()
barsAboveMA: _ProtocolBarsabovema = Exported()
barsBelowMA: _ProtocolBarsbelowma = Exported()
barsCrossedMA: _ProtocolBarscrossedma = Exported()
getPullbackBarCount: _ProtocolGetpullbackbarcount = Exported()
getBodySize: _ProtocolGetbodysize = Exported()
getTopWickSize: _ProtocolGettopwicksize = Exported()
getBottomWickSize: _ProtocolGetbottomwicksize = Exported()
getBodyPercent: _ProtocolGetbodypercent = Exported()
isHammer: _ProtocolIshammer = Exported()
isStar: _ProtocolIsstar = Exported()
isDoji: _ProtocolIsdoji = Exported()
isBullishEC: _ProtocolIsbullishec = Exported()
isBearishEC: _ProtocolIsbearishec = Exported()
timeFilter: _ProtocolTimefilter = Exported()
dateFilter: _ProtocolDatefilter = Exported()
dayFilter: _ProtocolDayfilter = Exported()
atrFilter: _ProtocolAtrfilter = Exported()
fillCell: _ProtocolFillcell = Exported()


@script.library('ZenLibrary')
def main():
    @export
    def getDecimals():
        return math.abs(math.log(syminfo.mintick) / math.log(10))

    @export
    def truncate(_number: float, _decimalPlaces: float = 2.0):
        _factor = math.pow(10, _decimalPlaces)
        return cast_int(_number * _factor) / _factor

    @export
    def toWhole(_number: float):
        _return = _number / syminfo.mintick / (10 / syminfo.pointvalue) if _number < 1.0 else _number
        _return = _return * 100 if _number >= 1.0 and _number <= 100.0 else _return
        return _return

    @export
    def toPips(_number: float):
        return _number * syminfo.mintick * 10

    @export
    def av_getPositionSize(_balance: float, _risk: float, _stopPoints: float, _conversionRate: float):
        riskAmount = _balance * (_risk / 100) * _conversionRate
        riskPerPoint = _stopPoints * syminfo.pointvalue
        positionSize = riskAmount / riskPerPoint / syminfo.mintick
        return math.round(positionSize)

    @export
    def getMA(_length: int, _maType: str):
        __block_result__ = na
        __switch__ = _maType
        if __switch__ == 'EMA':
            __block_result__ = ta.ema(close, _length)
        elif __switch__ == 'SMA':
            __block_result__ = ta.sma(close, _length)
        elif __switch__ == 'HMA':
            __block_result__ = ta.hma(close, _length)
        elif __switch__ == 'WMA':
            __block_result__ = ta.wma(close, _length)
        elif __switch__ == 'VWMA':
            __block_result__ = ta.vwma(close, _length)
        elif __switch__ == 'VWAP':
            __block_result__ = ta.vwap
        else:
            e1 = ta.ema(close, _length)
            e2 = ta.ema(e1, _length)
            __block_result__ = 2 * e1 - e2
        return __block_result__

    @export
    def getEAP(_atr: float):
        atrWhole = toWhole(_atr)
        eapStopWhole = atrWhole
        if atrWhole >= 20.0 and atrWhole < 30.0:
            eapStopWhole = 20.0
        if atrWhole >= 30.0 and atrWhole < 50.0:
            eapStopWhole = 30.0
        if atrWhole >= 50.0 and atrWhole < 100.0:
            eapStopWhole = 50.0
        if atrWhole >= 100.0:
            eapStopWhole = 100.0
        return toPips(eapStopWhole)

    @export
    def barsAboveMA(_lookback: int, _ma: float):
        _counter: int = 0
        for i in pine_range(1, _lookback, 1):
            if close[i] > _ma:
                _counter = _counter + 1
        return _counter

    @export
    def barsBelowMA(_lookback: int, _ma: float):
        _counter: int = 0
        for i in pine_range(1, _lookback, 1):
            if close[i] < _ma:
                _counter = _counter + 1
        return _counter

    @export
    def barsCrossedMA(_lookback: int, _ma: float):
        _counter: int = 0
        for i in pine_range(1, _lookback, 1):
            if open[i] > _ma and close[i] < _ma or (open[i] < _ma and close[i] > _ma):
                _counter = _counter + 1
        return _counter

    @export
    def getPullbackBarCount(_lookback: int, _direction: int):
        _recentCandles: int = 0
        for i in pine_range(1, _lookback, 1):
            if _direction == 1 and close[i] > open[i]:
                _recentCandles = _recentCandles + 1
            if _direction == -1 and close[i] < open[i]:
                _recentCandles = _recentCandles + 1
        return _recentCandles

    @export
    def getBodySize():
        return math.abs(close - open) / syminfo.mintick

    @export
    def getTopWickSize():
        return math.abs(high - (close if close > open else open)) / syminfo.mintick

    @export
    def getBottomWickSize():
        return math.abs((close if close < open else open) - low) / syminfo.mintick

    @export
    def getBodyPercent():
        return math.abs(open - close) / math.abs(high - low)

    @export
    def isHammer(_fib: float = 0.382, _colorMatch: bool = False):
        bullFib = (low - high) * _fib + high
        lowestBody = close if close < open else open
        return lowestBody >= bullFib and (not _colorMatch or close > open)

    @export
    def isStar(_fib: float = 0.382, _colorMatch: bool = False):
        bearFib = (high - low) * _fib + low
        highestBody = close if close > open else open
        return highestBody <= bearFib and (not _colorMatch or close < open)

    @export
    def isDoji(_wickSize: float = 2.0, _bodySize: float = 0.05):
        getBottomWickSize_1 = getBottomWickSize()
        getTopWickSize_1 = getTopWickSize()
        getBodyPercent_1 = getBodyPercent()
        return getTopWickSize() <= getBottomWickSize() * _wickSize and getBottomWickSize_1 <= getTopWickSize_1 * _wickSize and (getBodyPercent_1 <= _bodySize)

    @export
    def isBullishEC(_allowance: float = 0.0, _rejectionWickSize: float = 0.0, _engulfWick: bool = False):
        getTopWickSize_1 = getTopWickSize()
        getBodySize_1 = getBodySize()
        return close[1] <= open[1] and close >= open[1] and (open <= close[1] + _allowance) and (not _engulfWick or close >= high[1]) and (_rejectionWickSize == 0.0 or getTopWickSize_1 / getBodySize_1 < _rejectionWickSize)

    @export
    def isBearishEC(_allowance: float = 0.0, _rejectionWickSize: float = 0.0, _engulfWick: bool = False):
        getBottomWickSize_1 = getBottomWickSize()
        getBodySize_1 = getBodySize()
        return close[1] >= open[1] and close <= open[1] and (open >= close[1] - _allowance) and (not _engulfWick or close <= low[1]) and (_rejectionWickSize == 0.0 or getBottomWickSize_1 / getBodySize_1 < _rejectionWickSize)

    @export
    def timeFilter(_sess: str, _useFilter: bool = False):
        return na(time(timeframe.period, _sess + ':1234567')) or not _useFilter

    @export
    def dateFilter(_startTime: int, _endTime: int):
        return time >= _startTime and time <= _endTime

    @export
    def dayFilter(_monday: bool, _tuesday: bool, _wednesday: bool, _thursday: bool, _friday: bool, _saturday: bool, _sunday: bool):
        return dayofweek == dayofweek.monday and _monday or (dayofweek == dayofweek.tuesday and _tuesday) or (dayofweek == dayofweek.wednesday and _wednesday) or (dayofweek == dayofweek.thursday and _thursday) or (dayofweek == dayofweek.friday and _friday) or (dayofweek == dayofweek.saturday and _saturday) or (dayofweek == dayofweek.sunday and _sunday)

    @export
    def atrFilter(_atr: float = 1111, _maxSize: float = na):
        atr_1 = ta.atr(14)
        return _maxSize == 0.0 or math.abs(high - low) <= (atr_1 if _atr == 1111 else _atr) * _maxSize

    @export
    def fillCell(_table: Table, _column: int, _row: int, _title: str, _value: str, _bgcolor: Color, _txtcolor: Color):
        _cellText = _title + '\n' + _value
        return table.cell(_table, _column, _row, _cellText, bgcolor=_bgcolor, text_color=_txtcolor)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
