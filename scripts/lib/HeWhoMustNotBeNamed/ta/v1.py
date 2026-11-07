"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_export import Exported, export
from pynecore.lib import array, close, high, hl2, low, na, nz, script, ta
from pynecore.types import Series
from typing import Protocol, Any
import lib.HeWhoMustNotBeNamed.arrays.v1 as pa


__all__ = ['atr', 'atrpercent', 'bb', 'bbw', 'bpercentb', 'dc', 'dcw', 'dpercentd', 'kc', 'kcw', 'kpercentk', 'ma', 'mbandoscillator', 'multibands', 'oscillator', 'oscillatorRange']


class _ProtocolMa(Protocol):
    def __call__(self, source: float = close, maType: str = 'sma', length: int = ...) -> Any: ...


class _ProtocolAtr(Protocol):
    def __call__(self, maType: str = 'sma', length: int = ...) -> Any: ...


class _ProtocolAtrpercent(Protocol):
    def __call__(self, maType: str = 'sma', length: int = ...) -> Any: ...


class _ProtocolBb(Protocol):
    def __call__(self, source: float = close, maType: str = 'sma', length: int = 20, multiplier: float = 2.0, sticky: bool = False) -> Any: ...


class _ProtocolBbw(Protocol):
    def __call__(self, source: float = close, maType: str = 'sma', length: int = 20, multiplier: float = 2.0, sticky: bool = False) -> Any: ...


class _ProtocolBpercentb(Protocol):
    def __call__(self, source: float = close, maType: str = 'sma', length: int = 20, multiplier: float = 2.0, sticky: bool = False) -> Any: ...


class _ProtocolKc(Protocol):
    def __call__(self, source: float = close, maType: str = 'ema', length: int = 20, multiplier: float = 2, useTrueRange: bool = True, sticky: bool = False) -> Any: ...


class _ProtocolKcw(Protocol):
    def __call__(self, source: float = close, maType: str = 'ema', length: int = 20, multiplier: float = 2, useTrueRange: bool = True, sticky: bool = False) -> Any: ...


class _ProtocolKpercentk(Protocol):
    def __call__(self, source: float = close, maType: str = 'ema', length: int = 20, multiplier: float = 2, useTrueRange: bool = True, sticky: bool = False) -> Any: ...


class _ProtocolDc(Protocol):
    def __call__(self, length: int = 20, useAlternateSource: bool = False, alternateSource: float = close, sticky: bool = False) -> Any: ...


class _ProtocolDcw(Protocol):
    def __call__(self, length: int = 20, useAlternateSource: bool = False, alternateSource: float = close, sticky: bool = False) -> Any: ...


class _ProtocolDpercentd(Protocol):
    def __call__(self, length: int = 20, useAlternateSource: bool = False, alternateSource: float = close, sticky: bool = False) -> Any: ...


class _ProtocolOscillatorrange(Protocol):
    def __call__(self, source: float, method__ren__: str = 'highlow', highlowLength: int = 50, rangeLength: int = 14, sticky: bool = False) -> Any: ...


class _ProtocolOscillator(Protocol):
    def __call__(self, type: str = 'rsi', length: int = 14, shortLength: int = 13, longLength: int = 25, source: float = close, highSource: float = high, lowSource: float = low, method__ren__: str = 'highlow', highlowLength: int = 50, sticky: bool = False) -> Any: ...


class _ProtocolMultibands(Protocol):
    def __call__(self, bandType: str = 'bb', source: float = close, maType: str = 'sma', length: int = 60, useTrueRange: bool = True, sticky: bool = False, numberOfBands: int = 7, multiplierStart: float = 0.5, multiplierStep: float = 0.5) -> Any: ...


class _ProtocolMbandoscillator(Protocol):
    def __call__(self, bandType: str = 'kc', source: float = close, maType: str = 'sma', length: int = 60, useTrueRange: bool = False, stickyBands: bool = False, numberOfBands: int = 100, multiplierStart: float = 0.5, multiplierStep: float = 0.5) -> Any: ...


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
oscillatorRange: _ProtocolOscillatorrange = Exported()
oscillator: _ProtocolOscillator = Exported()
multibands: _ProtocolMultibands = Exported()
mbandoscillator: _ProtocolMbandoscillator = Exported()


@script.library('ta', overlay=True)
def main():
    def bandwidth(middle: float, upper: float, lower: float):
        return 100 * (upper - lower) / middle

    def percentb(source: float, upper: float, lower: float):
        return 100 * (source - lower) / (upper - lower)

    def customseries(source: float = close, type: str = 'sma', length: int = na):
        __block_result__ = na
        __switch__ = type
        if __switch__ == 'ema':
            __block_result__ = ta.ema(source, length)
        elif __switch__ == 'sma':
            __block_result__ = ta.sma(source, length)
        elif __switch__ == 'rma':
            __block_result__ = ta.rma(source, length)
        elif __switch__ == 'hma':
            __block_result__ = ta.hma(source, length)
        elif __switch__ == 'wma':
            __block_result__ = ta.wma(source, length)
        elif __switch__ == 'vwma':
            __block_result__ = ta.vwma(source, length)
        elif __switch__ == 'swma':
            __block_result__ = ta.swma(source)
        elif __switch__ == 'linreg':
            __block_result__ = ta.linreg(source, length, 0)
        elif __switch__ == 'median':
            __block_result__ = ta.median(source, length)
        elif __switch__ == 'mom':
            __block_result__ = ta.mom(source, length)
        elif __switch__ == 'high':
            __block_result__ = ta.highest(source, length)
        elif __switch__ == 'low':
            __block_result__ = ta.lowest(source, length)
        elif __switch__ == 'medianHigh':
            __block_result__ = ta.median(ta.highest(source, length), length)
        elif __switch__ == 'medianLow':
            __block_result__ = ta.median(ta.lowest(source, length), length)
        elif __switch__ == 'percentrank':
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
    def ma(source: float = close, maType: str = 'sma', length: int = na):
        return customseries(source, maType, length)

    @export
    def atr(maType: str = 'sma', length: int = na):
        return customseries(ta.tr, maType, length)

    @export
    def atrpercent(maType: str = 'sma', length: int = na):
        return 100 * atr(maType, length) / close

    @export
    def bb(source: float = close, maType: str = 'sma', length: int = 20, multiplier: float = 2.0, sticky: bool = False):
        middle: float = ma(source, maType, length)
        upper: float = middle + ta.stdev(source, length) * multiplier
        lower: float = middle - ta.stdev(source, length) * multiplier
        newUpper, newLower = getStickyRange(high, low, upper, lower, sticky)
        upper = newUpper
        lower = newLower
        return (middle, upper, lower)

    @export
    def bbw(source: float = close, maType: str = 'sma', length: int = 20, multiplier: float = 2.0, sticky: bool = False):
        middle, upper, lower = bb(source, maType, length, multiplier, sticky)
        return bandwidth(middle, upper, lower)

    @export
    def bpercentb(source: float = close, maType: str = 'sma', length: int = 20, multiplier: float = 2.0, sticky: bool = False):
        middle, upper, lower = bb(source, maType, length, multiplier, sticky)
        return percentb(source, upper, lower)

    @export
    def kc(source: float = close, maType: str = 'ema', length: int = 20, multiplier: float = 2, useTrueRange: bool = True, sticky: bool = False):
        middle: float = ma(source, maType, length)
        span: float = ta.tr if useTrueRange else high - low
        rangeMa: float = ma(span, maType, length)
        upper: float = middle + rangeMa * multiplier
        lower: float = middle - rangeMa * multiplier
        newUpper, newLower = getStickyRange(high, low, upper, lower, sticky)
        upper = newUpper
        lower = newLower
        return (middle, upper, lower)

    @export
    def kcw(source: float = close, maType: str = 'ema', length: int = 20, multiplier: float = 2, useTrueRange: bool = True, sticky: bool = False):
        middle, upper, lower = kc(source, maType, length, multiplier, useTrueRange, sticky)
        return bandwidth(middle, upper, lower)

    @export
    def kpercentk(source: float = close, maType: str = 'ema', length: int = 20, multiplier: float = 2, useTrueRange: bool = True, sticky: bool = False):
        middle, upper, lower = kc(source, maType, length, multiplier, useTrueRange, sticky)
        return percentb(source, upper, lower)

    @export
    def dc(length: int = 20, useAlternateSource: bool = False, alternateSource: float = close, sticky: bool = False):
        highSource = alternateSource if useAlternateSource else high
        lowSource = alternateSource if useAlternateSource else low
        upper, lower = getStickyRange(highSource, lowSource, ta.highest(highSource, length), ta.lowest(lowSource, length), sticky)
        middle = (upper + lower) / 2
        return (middle, upper, lower)

    @export
    def dcw(length: int = 20, useAlternateSource: bool = False, alternateSource: float = close, sticky: bool = False):
        middle, upper, lower = dc(length, useAlternateSource, alternateSource, sticky)
        return bandwidth(middle, upper, lower)

    @export
    def dpercentd(length: int = 20, useAlternateSource: bool = False, alternateSource: float = close, sticky: bool = False):
        middle, upper, lower = dc(length, useAlternateSource, alternateSource, sticky)
        return percentb(alternateSource if useAlternateSource else hl2, upper, lower)

    @export
    def oscillatorRange(source: float, method__ren__: str = 'highlow', highlowLength: int = 50, rangeLength: int = 14, sticky: bool = False):
        oscillatorHighest = customseries(source, 'high', highlowLength)
        oscillatorLowest = customseries(source, 'low', highlowLength)
        oscOverbought = customseries(oscillatorHighest, 'low' if method__ren__ == 'highlow' else method__ren__, rangeLength)
        oscOversold = customseries(oscillatorLowest, 'high' if method__ren__ == 'highlow' else method__ren__, rangeLength)
        return getStickyRange(source, source, oscOverbought, oscOversold, sticky)

    @export
    def oscillator(type: str = 'rsi', length: int = 14, shortLength: int = 13, longLength: int = 25, source: float = close, highSource: float = high, lowSource: float = low, method__ren__: str = 'highlow', highlowLength: int = 50, sticky: bool = False):
        __block_result_1__ = na
        __switch__ = type
        if __switch__ == 'cci':
            __block_result_1__ = ta.cci(source, length)
        elif __switch__ == 'cmo':
            __block_result_1__ = ta.cmo(source, length)
        elif __switch__ == 'cog':
            __block_result_1__ = ta.cog(source, length)
        elif __switch__ == 'mfi':
            __block_result_1__ = ta.mfi(source, length)
        elif __switch__ == 'roc':
            __block_result_1__ = ta.roc(source, length)
        elif __switch__ == 'rsi':
            __block_result_1__ = ta.rsi(source, length)
        elif __switch__ == 'stoch':
            __block_result_1__ = ta.stoch(source, highSource, lowSource, length)
        elif __switch__ == 'tsi':
            __block_result_1__ = ta.tsi(source, shortLength, longLength)
        elif __switch__ == 'wpr':
            __block_result_1__ = ta.wpr(length)
        else:
            __block_result_1__ = ta.rsi(source, length)
        oscillator__00000071__ = __block_result_1__
        overbought, oversold = oscillatorRange(oscillator__00000071__, method__ren__, highlowLength, length, sticky)
        return (oscillator__00000071__, overbought, oversold)

    @export
    def multibands(bandType: str = 'bb', source: float = close, maType: str = 'sma', length: int = 60, useTrueRange: bool = True, sticky: bool = False, numberOfBands: int = 7, multiplierStart: float = 0.5, multiplierStep: float = 0.5):
        bands: list[float] = array.new_float()
        for i in pine_range(0, numberOfBands - 1, 1):
            multiplier = multiplierStart + i * multiplierStep
            middle: float = 0.0
            upper: float = 0.0
            lower: float = 0.0
            if bandType == 'bb':
                bbmiddle, bbupper, bblower = bb(source, maType, length, multiplier, sticky)
                middle = bbmiddle
                upper = bbupper
                lower = bblower
            else:
                kcmiddle, kcupper, kclower = kc(source, maType, length, multiplier, useTrueRange, sticky)
                middle = kcmiddle
                upper = kcupper
                lower = kclower
            array.unshift(bands, lower)
            array.unshift(bands, upper)
            if i == 0:
                array.unshift(bands, middle)
        array.sort(bands)
        return bands

    @export
    def mbandoscillator(bandType: str = 'kc', source: float = close, maType: str = 'sma', length: int = 60, useTrueRange: bool = False, stickyBands: bool = False, numberOfBands: int = 100, multiplierStart: float = 0.5, multiplierStep: float = 0.5):
        states = multibands(bandType, source, maType, length, useTrueRange, stickyBands, numberOfBands, multiplierStart, multiplierStep)
        currentState = array.size(states)
        for i in pine_range(0, array.size(states) - 1, 1):
            if source < array.get(states, i):
                currentState = i
                break
        return currentState


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
