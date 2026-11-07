"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    array, close, color, fill, high, hl2, input, low, math, na, nz, plot,
    script, ta, timenow
)
from pynecore.types import Persistent, Series
from typing import Protocol, Any
import lib.HeWhoMustNotBeNamed.arrayutils.v17 as pa


__all__ = ['atr', 'atrpercent', 'bb', 'bbw', 'bpercentb', 'dc', 'dcw', 'dpercentd', 'kc', 'kcw', 'kpercentk', 'ma', 'mbandoscillator', 'multibands', 'oscillator', 'oscillatorRange', 'timer']


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


class _ProtocolTimer(Protocol):
    def __call__(self, timeStart: int, timeEnd: int = timenow) -> Any: ...


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
timer: _ProtocolTimer = Exported()


@script.library('enhanced_ta', overlay=True)
def main(
    display__ren__=input.string('multibands', title='Display Indicator', options=('all', 'ma', 'atr', 'multibands', 'band', 'bandwidth', 'bandpercent', 'oscillator')),
    overlay=input.bool(True, title='Overlay', inline='o'),
    nonOverlay=input.bool(True, title='NonOverlay', inline='o'),
    masource: Series[float] = input.source(close, title='Source', group='Moving Average'),
    matype=input.string('sma', title='Type', group='Moving Average', options=('sma', 'ema', 'hma', 'rma', 'wma', 'vwma', 'swma', 'linreg', 'median')),
    malength=input.int(20, title='Length', group='Moving Average'),
    amatype=input.string('sma', title='Type', group='ATR', options=('sma', 'ema', 'hma', 'rma', 'wma', 'vwma', 'swma', 'linreg', 'median')),
    amalength=input.int(20, title='Length', group='ATR'),
    displayPercent=input.bool(False, title='Display as Percent', group='ATR'),
    bandType=input.string('BB', title='Type', group='Bands/Bandwidth/BandPercent', options=('BB', 'KC', 'DC')),
    bmasource: Series[float] = input.source(close, title='Source', group='Bands/Bandwidth/BandPercent'),
    bmatype=input.string('sma', title='Type', group='Bands/Bandwidth/BandPercent', options=('sma', 'ema', 'hma', 'rma', 'wma', 'vwma', 'swma', 'linreg', 'median')),
    bmalength=input.int(20, title='Length', group='Bands/Bandwidth/BandPercent'),
    multiplier=input.float(2.0, step=0.5, title='Multiplier', group='Bands/Bandwidth/BandPercent'),
    useTrueRange=input.bool(True, title='Use True Range (KC)', group='Bands/Bandwidth/BandPercent'),
    useAlternateSource=input.bool(False, title='Use Alternate Source (DC)', group='Bands/Bandwidth/BandPercent'),
    bsticky=input.bool(True, title='Sticky', group='Bands/Bandwidth/BandPercent'),
    oscType=input.string('cci', title='Oscillator Type', group='Oscillator', options=('cci', 'cmo', 'cog', 'mfi', 'roc', 'rsi', 'stoch', 'tsi', 'wpr')),
    oLength=input.int(14, title='Length', group='Oscillator'),
    shortLength=input.int(9, title='Short Length (TSI)', group='Oscillator'),
    longLength=input.int(9, title='Long Length (TSI)', group='Oscillator'),
    method__ren__=input.string('highlow', title='Dynamic Overvought/Oversold Calculation method', group='Oscillator', options=('highlow', 'sma', 'ema', 'hma', 'rma', 'wma', 'vwma', 'swma', 'linreg', 'median')),
    highlowlength=input.int(50, title='Length', group='Oscillator'),
    osticky=input.bool(True, title='Sticky', group='Oscillator')
):
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
            multiplier__0000007b__ = multiplierStart + i * multiplierStep
            middle__0000007b__: float = 0.0
            upper__0000007b__: float = 0.0
            lower__0000007b__: float = 0.0
            if bandType == 'bb':
                bbmiddle__00000074__, bbupper__00000074__, bblower__00000074__ = bb(source, maType, length, multiplier__0000007b__, sticky)
                middle__0000007b__ = bbmiddle__00000074__
                upper__0000007b__ = bbupper__00000074__
                lower__0000007b__ = bblower__00000074__
            else:
                kcmiddle__00000076__, kcupper__00000076__, kclower__00000076__ = kc(source, maType, length, multiplier__0000007b__, useTrueRange, sticky)
                middle__0000007b__ = kcmiddle__00000076__
                upper__0000007b__ = kcupper__00000076__
                lower__0000007b__ = kclower__00000076__
            array.unshift(bands, lower__0000007b__)
            array.unshift(bands, upper__0000007b__)
            if i == 0:
                array.unshift(bands, middle__0000007b__)
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

    _ma = ma(masource, matype, malength)
    displayMa = display__ren__ == 'ma' or (display__ren__ == 'all' and overlay)
    plot(_ma if displayMa else na, title='Moving Average', color=color.blue)
    _atr = atr(amatype, amalength)
    _atrpercent = atrpercent(amatype, amalength)
    displayAtr = display__ren__ == 'atr' or (display__ren__ == 'all' and nonOverlay)
    plot((_atrpercent if displayPercent else _atr) if displayAtr else na, title='ATR (or Percent)', color=color.blue)
    displayBands = display__ren__ == 'band' or (display__ren__ == 'all' and overlay)
    cloudTransparency: Persistent[int] = 90
    bbmiddle, bbupper, bblower = bb(bmasource, bmatype, bmalength, multiplier, sticky=bsticky)
    kcmiddle, kcupper, kclower = kc(bmasource, bmatype, bmalength, multiplier, useTrueRange, sticky=bsticky)
    dcmiddle, dcupper, dclower = dc(bmalength, useAlternateSource, bmasource, sticky=bsticky)
    upper = bbupper if bandType == 'BB' else kcupper if bandType == 'KC' else dcupper
    lower = bblower if bandType == 'BB' else kclower if bandType == 'KC' else dclower
    middle = bbmiddle if bandType == 'BB' else kcmiddle if bandType == 'KC' else dcmiddle
    uPlot = plot(upper if displayBands else na, title='Upper', color=color.new(color.green, cloudTransparency))
    lPlot = plot(lower if displayBands else na, title='Lower', color=color.new(color.red, cloudTransparency))
    mPlot = plot(middle if displayBands else na, title='Middle', color=color.new(color.blue, cloudTransparency))
    fill(uPlot, mPlot, title='UpperRange', color=color.new(color.green, cloudTransparency))
    fill(lPlot, mPlot, title='LowerRange', color=color.new(color.red, cloudTransparency))
    _bbw = bbw(bmasource, bmatype, bmalength, multiplier, sticky=bsticky)
    _kcw = kcw(bmasource, bmatype, bmalength, multiplier, useTrueRange, sticky=bsticky)
    _dcw = dcw(bmalength, useAlternateSource, bmasource, sticky=bsticky)
    _bandwidth = _bbw if bandType == 'BB' else _kcw if bandType == 'KC' else _dcw
    _displayBandwidth = display__ren__ == 'bandwidth' or (display__ren__ == 'all' and nonOverlay)
    plot(_bandwidth if _displayBandwidth else na, title='Bandwidth', color=color.maroon)
    _bpercentb = bpercentb(bmasource, bmatype, bmalength, multiplier, sticky=bsticky)
    _kpercentk = kpercentk(bmasource, bmatype, bmalength, multiplier, useTrueRange, sticky=bsticky)
    _dpercentd = dpercentd(bmalength, useAlternateSource, bmasource, sticky=bsticky)
    _bandpercent = _bpercentb if bandType == 'BB' else _kpercentk if bandType == 'KC' else _dpercentd
    _displayBandPercent = display__ren__ == 'bandpercent' or (display__ren__ == 'all' and nonOverlay)
    plot(_bandpercent if _displayBandPercent else na, title='BandPercent', color=color.fuchsia)
    _oscillator, _overbought, _oversold = oscillator(oscType, oLength, shortLength, longLength, method__ren__=method__ren__, highlowLength=highlowlength, sticky=osticky)
    _displayOscillator = display__ren__ == 'oscillator' or (display__ren__ == 'all' and nonOverlay)
    plot(_oscillator if _displayOscillator else na, title='Oscillator', color=color.blue)
    plot(_overbought if _displayOscillator else na, title='Overbought', color=color.red)
    plot(_oversold if _displayOscillator else na, title='Oversold', color=color.green)
    bands = multibands()
    _displayMultibands = (display__ren__ == 'multibands' or (display__ren__ == 'all' and overlay)) and array.size(bands) == 15
    plot(array.get(bands, 0) if _displayMultibands else na, title='L7', color=color.red)
    plot(array.get(bands, 1) if _displayMultibands else na, title='L6', color=color.red)
    plot(array.get(bands, 2) if _displayMultibands else na, title='L5', color=color.red)
    plot(array.get(bands, 3) if _displayMultibands else na, title='L4', color=color.red)
    plot(array.get(bands, 4) if _displayMultibands else na, title='L3', color=color.red)
    plot(array.get(bands, 5) if _displayMultibands else na, title='L2', color=color.red)
    plot(array.get(bands, 6) if _displayMultibands else na, title='L1', color=color.red)
    plot(array.get(bands, 7) if _displayMultibands else na, title='M', color=color.blue)
    plot(array.get(bands, 8) if _displayMultibands else na, title='U1', color=color.green)
    plot(array.get(bands, 9) if _displayMultibands else na, title='U2', color=color.green)
    plot(array.get(bands, 10) if _displayMultibands else na, title='U3', color=color.green)
    plot(array.get(bands, 11) if _displayMultibands else na, title='U4', color=color.green)
    plot(array.get(bands, 12) if _displayMultibands else na, title='U5', color=color.green)
    plot(array.get(bands, 13) if _displayMultibands else na, title='U6', color=color.green)
    plot(array.get(bands, 14) if _displayMultibands else na, title='U7', color=color.green)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
