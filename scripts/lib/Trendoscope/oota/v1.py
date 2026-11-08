"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from enum import StrEnum as Enum
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    bar_index, close, high, low, math, na, nz, open, script, ta, time,
    time_close, volume
)
from pynecore.types import Persistent, PersistentSeries, Series
from typing import Protocol, Any


__all__ = ['Candle', 'CustomSeries', 'OscillatorType', 'atr', 'atrpercent', 'bb', 'bbw', 'bpercentb', 'dc', 'dcw', 'dpercentd', 'kc', 'kcw', 'kpercentk', 'ma', 'oscillator', 'oscillatorRange', 'oscillatorWithRange', 'supertrend', 'tr']


@udt
class Candle:
    o: float = _dataclass_field(default_factory=lambda: open)
    h: float = _dataclass_field(default_factory=lambda: high)
    l: float = _dataclass_field(default_factory=lambda: low)
    c: float = _dataclass_field(default_factory=lambda: close)
    barindex: int = _dataclass_field(default_factory=lambda: bar_index)
    bartime: int = _dataclass_field(default_factory=lambda: time)
    bartimeclose: int = _dataclass_field(default_factory=lambda: time_close)
    v: float = _dataclass_field(default_factory=lambda: volume)


class CustomSeries(Enum):
    EMA = 'EMA'
    SMA = 'SMA'
    RMA = 'RMA'
    HMA = 'HMA'
    WMA = 'WMA'
    VWMA = 'VWMA'
    SWMA = 'SWMA'
    LINREG = 'LINREG'
    MEDIAN = 'MEDIAN'
    MOM = 'MOM'
    HIGH = 'HIGH'
    LOW = 'LOW'
    MEDIAN_HIGH = 'MEDIAN_HIGH'
    MEDIAN_LOW = 'MEDIAN_LOW'
    PERCENTRANK = 'PERCENTRANK'
    HIGHLOW = 'HIGHLOW'


class OscillatorType(Enum):
    CCI = 'CCI'
    CMO = 'CMO'
    COG = 'COG'
    MFI = 'MFI'
    ROC = 'ROC'
    RSI = 'RSI'
    STOCH = 'STOCH'
    TSI = 'TSI'
    WPR = 'WPR'


class _ProtocolTr(Protocol):
    def __call__(self, c: Candle, useTrueRange: bool = True) -> Any: ...


class _ProtocolMa(Protocol):
    def __call__(self, maType: CustomSeries = CustomSeries.SMA, length: int = ..., source: float = close) -> Any: ...


class _ProtocolAtr(Protocol):
    def __call__(self, maType: CustomSeries = CustomSeries.SMA, length: int = ..., useTrueRange: bool = True, c: Candle = na) -> Any: ...


class _ProtocolAtrpercent(Protocol):
    def __call__(self, maType: CustomSeries = CustomSeries.SMA, length: int = ..., useTrueRange: bool = True, c: Candle = na) -> Any: ...


class _ProtocolBb(Protocol):
    def __call__(self, maType: CustomSeries = CustomSeries.SMA, length: int = 20, multiplier: float = 2.0, sticky: bool = False, c: Candle = na) -> Any: ...


class _ProtocolBbw(Protocol):
    def __call__(self, maType: CustomSeries = CustomSeries.SMA, length: int = 20, multiplier: float = 2.0, sticky: bool = False, c: Candle = na) -> Any: ...


class _ProtocolBpercentb(Protocol):
    def __call__(self, maType: CustomSeries = CustomSeries.SMA, length: int = 20, multiplier: float = 2.0, sticky: bool = False, c: Candle = na) -> Any: ...


class _ProtocolKc(Protocol):
    def __call__(self, maType: CustomSeries = CustomSeries.EMA, length: int = 20, multiplier: float = 2, useTrueRange: bool = True, sticky: bool = False, c: Candle = na) -> Any: ...


class _ProtocolKcw(Protocol):
    def __call__(self, maType: CustomSeries = CustomSeries.EMA, length: int = 20, multiplier: float = 2, useTrueRange: bool = True, sticky: bool = False, c: Candle = na) -> Any: ...


class _ProtocolKpercentk(Protocol):
    def __call__(self, maType: CustomSeries = CustomSeries.EMA, length: int = 20, multiplier: float = 2, useTrueRange: bool = True, sticky: bool = False, c: Candle = na) -> Any: ...


class _ProtocolDc(Protocol):
    def __call__(self, c: Candle = na, length: int = 20, sticky: bool = False) -> Any: ...


class _ProtocolDcw(Protocol):
    def __call__(self, c: Candle = na, length: int = 20, sticky: bool = False) -> Any: ...


class _ProtocolDpercentd(Protocol):
    def __call__(self, c: Candle = na, length: int = 20, sticky: bool = False) -> Any: ...


class _ProtocolSupertrend(Protocol):
    def __call__(self, maType: CustomSeries, length: int, multiplier: float, useTrueRange: bool = True, waitForClose: bool = False, delayed: bool = False, c: Candle = na) -> Any: ...


class _ProtocolOscillatorrange(Protocol):
    def __call__(self, seriesType: CustomSeries, source: float, highlowLength: int = 50, rangeLength: int = 14, sticky: bool = False) -> Any: ...


class _ProtocolOscillator(Protocol):
    def __call__(self, oscillatorType: OscillatorType = OscillatorType.RSI, length: int = 14, shortLength: int = 13, longLength: int = 25, c: Candle = na) -> Any: ...


class _ProtocolOscillatorwithrange(Protocol):
    def __call__(self, oscillatorType: OscillatorType = OscillatorType.RSI, length: int = 14, shortLength: int = 13, longLength: int = 25, seriesType: CustomSeries = CustomSeries.HIGHLOW, highlowLength: int = 50, sticky: bool = False, c: Candle = na) -> Any: ...


tr: _ProtocolTr = Exported()
ma: _ProtocolMa = Exported()
atr: _ProtocolAtr = Exported()
atrpercent: _ProtocolAtrpercent = Exported()
bb: _ProtocolBb = Exported()
bbw: _ProtocolBbw = Exported()
bpercentb: _ProtocolBpercentb = Exported()
kc: _ProtocolKc = Exported()
kcw: _ProtocolKcw = Exported()
kpercentk: _ProtocolKpercentk = Exported()
dc: _ProtocolDc = Exported()
dcw: _ProtocolDcw = Exported()
dpercentd: _ProtocolDpercentd = Exported()
supertrend: _ProtocolSupertrend = Exported()
oscillatorRange: _ProtocolOscillatorrange = Exported()
oscillator: _ProtocolOscillator = Exported()
oscillatorWithRange: _ProtocolOscillatorwithrange = Exported()


@script.library('oota', overlay=True)
def main():
    def bandwidth(middle: float, upper: float, lower: float):
        return 100 * (upper - lower) / middle

    def percentb(source: float, upper: float, lower: float):
        return 100 * (source - lower) / (upper - lower)

    def customseries(source: float = close, maType: CustomSeries = CustomSeries.SMA, length: int = na):
        __block_result__ = na
        __switch__ = maType
        if __switch__ == CustomSeries.EMA:
            __block_result__ = ta.ema(source, length)
        elif __switch__ == CustomSeries.SMA:
            __block_result__ = ta.sma(source, length)
        elif __switch__ == CustomSeries.RMA:
            __block_result__ = ta.rma(source, length)
        elif __switch__ == CustomSeries.HMA:
            __block_result__ = ta.hma(source, length)
        elif __switch__ == CustomSeries.WMA:
            __block_result__ = ta.wma(source, length)
        elif __switch__ == CustomSeries.VWMA:
            __block_result__ = ta.vwma(source, length)
        elif __switch__ == CustomSeries.SWMA:
            __block_result__ = ta.swma(source)
        elif __switch__ == CustomSeries.LINREG:
            __block_result__ = ta.linreg(source, length, 0)
        elif __switch__ == CustomSeries.MEDIAN:
            __block_result__ = ta.median(source, length)
        elif __switch__ == CustomSeries.MOM:
            __block_result__ = ta.mom(source, length)
        elif __switch__ == CustomSeries.HIGH:
            __block_result__ = ta.highest(source, length)
        elif __switch__ == CustomSeries.LOW:
            __block_result__ = ta.lowest(source, length)
        elif __switch__ == CustomSeries.MEDIAN_HIGH:
            __block_result__ = ta.median(ta.highest(source, length), length)
        elif __switch__ == CustomSeries.MEDIAN_LOW:
            __block_result__ = ta.median(ta.lowest(source, length), length)
        elif __switch__ == CustomSeries.PERCENTRANK:
            __block_result__ = ta.percentrank(source, length)
        else:
            __block_result__ = (ta.highest(length) + ta.lowest(length)) / 2
        return __block_result__

    def getStickyRange(highsource: Series[float], lowsource: Series[float], upper: float, lower: float, sticky: bool = False):
        newUpper: Series = upper
        newLower: Series = lower
        highBreakout = highsource[1] >= newUpper[1]
        lowBreakout = lowsource[1] <= newLower[1]
        newUpper = newUpper if highBreakout or lowBreakout or (not sticky) else nz(newUpper[1], newUpper)
        newLower = newLower if highBreakout or lowBreakout or (not sticky) else nz(newLower[1], newLower)
        return (newUpper, newLower)

    @export
    @method
    def tr(c: Candle, useTrueRange: bool = True):
        cl: Series[float] = c.c
        return math.max(c.h, nz(cl[1], c.h)) - math.min(c.l, nz(cl[1], c.l)) if useTrueRange else c.h - c.l

    @export
    @method
    def ma(maType: CustomSeries = CustomSeries.SMA, length: int = na, source: float = close):
        return customseries(source, maType, length)

    @export
    @method
    def atr(maType: CustomSeries = CustomSeries.SMA, length: int = na, useTrueRange: bool = True, c: Candle = na):
        candle = Candle() if na(c) else c
        tr__00000041__ = method_call('tr', candle, useTrueRange)
        return nz(customseries(tr__00000041__, maType, length), tr__00000041__)

    @export
    @method
    def atrpercent(maType: CustomSeries = CustomSeries.SMA, length: int = na, useTrueRange: bool = True, c: Candle = na):
        candle = Candle() if na(c) else c
        return 100 * atr(maType, length, useTrueRange, candle) / candle.c

    @export
    @method
    def bb(maType: CustomSeries = CustomSeries.SMA, length: int = 20, multiplier: float = 2.0, sticky: bool = False, c: Candle = na):
        candle = Candle() if na(c) else c
        middle: float = ma(maType, length, candle.c)
        upper: float = middle + ta.stdev(candle.c, length) * multiplier
        lower: float = middle - ta.stdev(candle.c, length) * multiplier
        newUpper, newLower = getStickyRange(candle.h, candle.l, upper, lower, sticky)
        upper = newUpper
        lower = newLower
        return (middle, upper, lower)

    @export
    @method
    def bbw(maType: CustomSeries = CustomSeries.SMA, length: int = 20, multiplier: float = 2.0, sticky: bool = False, c: Candle = na):
        middle, upper, lower = bb(maType, length, multiplier, sticky, c)
        return bandwidth(middle, upper, lower)

    @export
    @method
    def bpercentb(maType: CustomSeries = CustomSeries.SMA, length: int = 20, multiplier: float = 2.0, sticky: bool = False, c: Candle = na):
        candle = Candle() if na(c) else c
        middle, upper, lower = bb(maType, length, multiplier, sticky, candle)
        return percentb(candle.c, upper, lower)

    @export
    @method
    def kc(maType: CustomSeries = CustomSeries.EMA, length: int = 20, multiplier: float = 2, useTrueRange: bool = True, sticky: bool = False, c: Candle = na):
        candle = Candle() if na(c) else c
        middle: float = ma(maType, length, candle.c)
        span: float = ta.tr if useTrueRange else high - low
        rangeMa: float = atr(maType, length, useTrueRange, candle)
        upper: float = middle + rangeMa * multiplier
        lower: float = middle - rangeMa * multiplier
        newUpper, newLower = getStickyRange(high, low, upper, lower, sticky)
        upper = newUpper
        lower = newLower
        return (middle, upper, lower)

    @export
    @method
    def kcw(maType: CustomSeries = CustomSeries.EMA, length: int = 20, multiplier: float = 2, useTrueRange: bool = True, sticky: bool = False, c: Candle = na):
        middle, upper, lower = kc(maType, length, multiplier, useTrueRange, sticky, c)
        return bandwidth(middle, upper, lower)

    @export
    @method
    def kpercentk(maType: CustomSeries = CustomSeries.EMA, length: int = 20, multiplier: float = 2, useTrueRange: bool = True, sticky: bool = False, c: Candle = na):
        candle = Candle() if na(c) else c
        middle, upper, lower = kc(maType, length, multiplier, useTrueRange, sticky, candle)
        return percentb(candle.c, upper, lower)

    @export
    @method
    def dc(c: Candle = na, length: int = 20, sticky: bool = False):
        candle = Candle() if na(c) else c
        upper, lower = getStickyRange(candle.h, candle.l, ta.highest(candle.h, length), ta.lowest(candle.l, length), sticky)
        middle = (upper + lower) / 2
        return (middle, upper, lower)

    @export
    @method
    def dcw(c: Candle = na, length: int = 20, sticky: bool = False):
        middle, upper, lower = dc(c, length, sticky)
        return bandwidth(middle, upper, lower)

    @export
    @method
    def dpercentd(c: Candle = na, length: int = 20, sticky: bool = False):
        candle = Candle() if na(c) else c
        middle, upper, lower = method_call('dc', candle, length, sticky)
        return percentb(candle.c, upper, lower)

    @export
    @method
    def supertrend(maType: CustomSeries, length: int, multiplier: float, useTrueRange: bool = True, waitForClose: bool = False, delayed: bool = False, c: Candle = na):
        candle = Candle() if na(c) else c
        atrDiff = atr(maType, length, useTrueRange, candle) * multiplier
        buyStop: PersistentSeries = candle.l - atrDiff
        sellStop: PersistentSeries = candle.h + atrDiff
        dir: Persistent[int] = 1

        buyStopCurrent = candle.l - atrDiff
        sellStopCurrent = candle.h + atrDiff

        buyStopInverse = candle.l - atrDiff / 2
        sellStopInverse = candle.h + atrDiff / 2

        highConfirmation: Series = candle.c if waitForClose else candle.h
        lowConfirmation: Series = candle.c if waitForClose else candle.l
        dir = -1 if dir == 1 and lowConfirmation[1] < buyStop[1] else 1 if dir == -1 and highConfirmation[1] > sellStop[1] else dir
        targetReached = dir == 1 and nz(highConfirmation[1]) >= nz(sellStop[1]) or (dir == -1 and nz(lowConfirmation[1]) <= nz(buyStop[1])) or (not delayed)
        buyStop = (math.max(nz(buyStop, buyStopCurrent), buyStopCurrent) if targetReached else buyStop) if dir == 1 else buyStopCurrent if targetReached else math.max(nz(buyStop, buyStopInverse), buyStopInverse)
        sellStop = (math.min(nz(sellStop, sellStopCurrent), sellStopCurrent) if targetReached else sellStop) if dir == -1 else sellStopCurrent if targetReached else math.min(nz(sellStop, sellStopInverse), sellStopInverse)
        return (dir, buyStop if dir > 0 else sellStop)

    @export
    @method
    def oscillatorRange(seriesType: CustomSeries, source: float, highlowLength: int = 50, rangeLength: int = 14, sticky: bool = False):
        oscillatorHighest = customseries(source, CustomSeries.HIGH, highlowLength)
        oscillatorLowest = customseries(source, CustomSeries.LOW, highlowLength)

        oscOverbought = customseries(oscillatorHighest, CustomSeries.LOW if seriesType == CustomSeries.HIGHLOW else seriesType, rangeLength)
        oscOversold = customseries(oscillatorLowest, CustomSeries.HIGH if seriesType == CustomSeries.HIGHLOW else seriesType, rangeLength)

        return getStickyRange(source, source, oscOverbought, oscOversold, sticky)


    @export
    @method
    def oscillator(oscillatorType: OscillatorType = OscillatorType.RSI, length: int = 14, shortLength: int = 13, longLength: int = 25, c: Candle = na):
        candle = Candle() if na(c) else c
        __block_result_1__ = na
        __switch__ = oscillatorType
        if __switch__ == OscillatorType.CCI:
            __block_result_1__ = ta.cci(candle.c, length)
        elif __switch__ == OscillatorType.CMO:
            __block_result_1__ = ta.cmo(candle.c, length)
        elif __switch__ == OscillatorType.COG:
            __block_result_1__ = ta.cog(candle.c, length)
        elif __switch__ == OscillatorType.MFI:
            __block_result_1__ = ta.mfi(candle.c, length)
        elif __switch__ == OscillatorType.ROC:
            __block_result_1__ = ta.roc(candle.c, length)
        elif __switch__ == OscillatorType.RSI:
            __block_result_1__ = ta.rsi(candle.c, length)
        elif __switch__ == OscillatorType.STOCH:
            __block_result_1__ = ta.stoch(candle.c, candle.h, candle.l, length)
        elif __switch__ == OscillatorType.TSI:
            __block_result_1__ = ta.tsi(candle.c, shortLength, longLength)
        elif __switch__ == OscillatorType.WPR:
            __block_result_1__ = ta.wpr(length)
        else:
            __block_result_1__ = ta.rsi(candle.c, length)
        return __block_result_1__

    @export
    @method
    def oscillatorWithRange(oscillatorType: OscillatorType = OscillatorType.RSI, length: int = 14, shortLength: int = 13, longLength: int = 25, seriesType: CustomSeries = CustomSeries.HIGHLOW, highlowLength: int = 50, sticky: bool = False, c: Candle = na):
        oscillator__000000a9__ = oscillator(oscillatorType, length, shortLength, longLength, c)
        overbought, oversold = oscillatorRange(seriesType, oscillator__000000a9__, highlowLength, length, sticky)
        return (oscillator__000000a9__, overbought, oversold)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
