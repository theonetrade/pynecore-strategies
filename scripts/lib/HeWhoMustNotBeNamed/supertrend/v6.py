"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_export import Exported, export
from pynecore.lib import array, close, color, high, input, low, math, na, nz, plot, script, ta
from pynecore.types import Persistent, PersistentSeries, Series
from typing import Protocol, Any
import lib.HeWhoMustNotBeNamed.enhanced_ta.v10 as eta
import lib.HeWhoMustNotBeNamed.zigzag.v5 as zg


__all__ = ['msupertrend', 'supertrend_atr', 'supertrend_bands', 'supertrend_zigzag', 'zsupertrend', 'zupertrend']


class _ProtocolSupertrendAtr(Protocol):
    def __call__(self, length: int, multiplier: float, atrMaType: str = 'sma', source: float = close, highSource: float = high, lowSource: float = low, waitForClose: bool = False, delayed: bool = False) -> Any: ...


class _ProtocolSupertrendBands(Protocol):
    def __call__(self, bandType: str = 'bb', maType: str = 'sma', length: int = 20, multiplier: float = 2.0, source: float = close, highSource: float = high, lowSource: float = low, waitForClose: bool = False, useTrueRange: bool = True, useAlternateSource: bool = False, alternateSource: float = close, sticky: bool = False) -> Any: ...


class _ProtocolSupertrendZigzag(Protocol):
    def __call__(self, length: int, history: int = 1, useAlternativeSource: bool = False, alternativeSource: float = close, source: float = close, highSource: float = high, lowSource: float = low, waitForClose: bool = False, atrlength: int = 22, multiplier: float = 1.0, atrMaType: str = 'sma') -> Any: ...


class _ProtocolZupertrend(Protocol):
    def __call__(self, length: int, history: int = 1, useAlternativeSource: bool = False, alternativeSource: float = close, source: float = close, highSource: float = high, lowSource: float = low, waitForClose: bool = False, atrlength: int = 22, multiplier: float = 1.0, atrMaType: str = 'sma') -> Any: ...


class _ProtocolZsupertrend(Protocol):
    def __call__(self, zigzagpivots: list[float], history: int = 1, source: float = close, highSource: float = high, lowSource: float = low, waitForClose: bool = False, atrMaType: str = 'sma', atrlength: int = 22, multiplier: float = 1) -> Any: ...


class _ProtocolMsupertrend(Protocol):
    def __call__(self, bandType: str = 'bb', source: float = close, maType: str = 'sma', length: int = 60, useTrueRange: bool = False, highSource: float = high, lowSource: float = low, waitForClose: bool = False, numberOfBands: int = 20, multiplierStart: float = 0.5, multiplierStep: float = 0.5, trailingDistance: int = 10, trailStates: bool = False) -> Any: ...


supertrend_atr: _ProtocolSupertrendAtr = Exported()
supertrend_bands: _ProtocolSupertrendBands = Exported()
supertrend_zigzag: _ProtocolSupertrendZigzag = Exported()
zupertrend: _ProtocolZupertrend = Exported()
zsupertrend: _ProtocolZsupertrend = Exported()
msupertrend: _ProtocolMsupertrend = Exported()


@script.library('supertrend', overlay=True)
def main(
    type=input.string('zupertrend', 'Type', options=('atr', 'bands', 'zigzag', 'zsupertrend', 'msupertrend', 'zupertrend'), group='Supertrend'),
    source: Series[float] = input.source(close, 'Source', group='Supertrend'),
    highSource: Series[float] = input.source(high, 'High', group='Supertrend'),
    lowSource: Series[float] = input.source(low, 'Low', group='Supertrend'),
    waitForClose=input.bool(False, 'Wait For Close', group='Supertrend'),
    stepped=input.bool(False, 'Delayed/Sticky', group='Supertrend'),
    atrMaType=input.string('sma', 'MA Type', options=('sma', 'ema', 'hma', 'rma', 'wma', 'vwma', 'swma', 'highlow', 'linreg', 'median'), group='ATR'),
    atrLength=input.int(22, 'MA Length', group='ATR'),
    atrMultiplier=input.int(4, 'Multiplier', group='ATR'),
    bandType=input.string('bb', 'Band Type', options=('bb', 'kc', 'dc'), group='Bands'),
    bandMaType=input.string('sma', 'MA Type', options=('sma', 'ema', 'hma', 'rma', 'wma', 'vwma', 'swma', 'highlow', 'linreg', 'median'), group='Bands'),
    bandLength=input.int(20, 'MA Length', group='Bands'),
    bandMultiplier=input.int(2, 'Multiplier', group='Bands'),
    useTrueRange=input.bool(True, title='Use True Range (KC)', group='Bands'),
    useAlternateSource=input.bool(False, title='Use Alternate Source (DC)', group='Bands'),
    alternateSource: Series[float] = input.source(close, 'Alternate Source', group='Bands'),
    useSupertrendParamsForBands=input.bool(False, 'Use Supertrend and ATR Settings', group='Bands'),
    numberOfBands=input.int(20, 'Number of Bands', group='Multibands'),
    multiplierStart=input.float(0.5, 'Start', group='Multibands'),
    multiplierStep=input.float(0.5, 'Step', group='Multibands'),
    trailingDistance=input.int(10, 'Trailing Distance', group='Multibands'),
    trailStates=input.bool(False, 'Trail States', group='Multibands'),
    zigzagLength=input.int(5, 'Length', group='Zigzag'),
    history=input.int(1, 'Pivot History', group='Zigzag'),
    useAlternateSourceZigzag=input.bool(False, title='Use Alternate Source', group='Zigzag'),
    alternateSourceZigzag: Series[float] = input.source(close, 'Alternate Source', group='Zigzag'),
    useSupertrendAndAtrParamsForZigzag=input.bool(False, 'Use Supertrend and ATR Settings', group='Zigzag')
):
    def f_getCurrentState(source, states):
        currentState = array.size(states)
        for i in pine_range(0, array.size(states) - 1, 1):
            if source < array.get(states, i):
                currentState = i
                break
        return currentState

    @export
    def supertrend_atr(length: int, multiplier: float, atrMaType: str = 'sma', source: float = close, highSource: float = high, lowSource: float = low, waitForClose: bool = False, delayed: bool = False):
        atrDiff = nz(eta.atr(atrMaType, length), ta.tr) * multiplier
        buyStop: PersistentSeries = lowSource - atrDiff
        sellStop: PersistentSeries = highSource + atrDiff
        dir: Persistent[int] = 1
        buyStopCurrent = lowSource - atrDiff
        sellStopCurrent = highSource + atrDiff
        buyStopInverse = lowSource - atrDiff / 2
        sellStopInverse = highSource + atrDiff / 2
        highConfirmation: Series = source if waitForClose else highSource
        lowConfirmation: Series = source if waitForClose else lowSource
        dir = -1 if dir == 1 and lowConfirmation[1] < buyStop[1] else 1 if dir == -1 and highConfirmation[1] > sellStop[1] else dir
        targetReached = dir == 1 and nz(highConfirmation[1]) >= nz(sellStop[1]) or (dir == -1 and nz(lowConfirmation[1]) <= nz(buyStop[1])) or (not delayed)
        buyStop = (math.max(nz(buyStop, buyStopCurrent), buyStopCurrent) if targetReached else buyStop) if dir == 1 else buyStopCurrent if targetReached else math.max(nz(buyStop, buyStopInverse), buyStopInverse)
        sellStop = (math.min(nz(sellStop, sellStopCurrent), sellStopCurrent) if targetReached else sellStop) if dir == -1 else sellStopCurrent if targetReached else math.min(nz(sellStop, sellStopInverse), sellStopInverse)
        return (dir, buyStop if dir > 0 else sellStop)

    @export
    def supertrend_bands(bandType: str = 'bb', maType: str = 'sma', length: int = 20, multiplier: float = 2.0, source: float = close, highSource: float = high, lowSource: float = low, waitForClose: bool = False, useTrueRange: bool = True, useAlternateSource: bool = False, alternateSource: float = close, sticky: bool = False):
        bbmiddle, bbupper, bblower = eta.bb(source, maType, length, multiplier, sticky)
        kcmiddle, kcupper, kclower = eta.kc(source, maType, length, multiplier, useTrueRange, sticky)
        dcmiddle, dcupper, dclower = eta.dc(length, useAlternateSource, alternateSource, sticky)
        __block_result__ = na
        __switch__ = bandType
        if __switch__ == 'bb':
            __block_result__ = bblower
        elif __switch__ == 'kc':
            __block_result__ = kclower
        else:
            __block_result__ = dclower
        lower = __block_result__
        __block_result_1__ = na
        __switch__ = bandType
        if __switch__ == 'bb':
            __block_result_1__ = bbupper
        elif __switch__ == 'kc':
            __block_result_1__ = kcupper
        else:
            __block_result_1__ = dcupper
        upper = __block_result_1__
        buyStop: PersistentSeries = lower
        sellStop: PersistentSeries = upper
        dir: Persistent[int] = 1
        buyStopCurrent = lower
        sellStopCurrent = upper
        highConfirmation: Series = source if waitForClose else highSource
        lowConfirmation: Series = source if waitForClose else lowSource
        dir = -1 if dir == 1 and lowConfirmation[1] < buyStop[1] else 1 if dir == -1 and highConfirmation[1] > sellStop[1] else dir
        buyStop = math.max(nz(buyStop, buyStopCurrent), buyStopCurrent) if dir == 1 else buyStopCurrent
        sellStop = math.min(nz(sellStop, sellStopCurrent), sellStopCurrent) if dir == -1 else sellStopCurrent
        return (dir, buyStop if dir > 0 else sellStop)

    @export
    def supertrend_zigzag(length: int, history: int = 1, useAlternativeSource: bool = False, alternativeSource: float = close, source: float = close, highSource: float = high, lowSource: float = low, waitForClose: bool = False, atrlength: int = 22, multiplier: float = 1.0, atrMaType: str = 'sma'):
        zigzagHistory = history * 2 + 1
        zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagoscillators, zigzagoscillatordirs, zigzagtrendbias, zigzagdivergence, newPivot, doublePivot = zg.zigzag(length, zigzagHistory, useAlternativeSource, alternativeSource)
        atrDiff = nz(eta.atr(atrMaType, atrlength), ta.tr) * multiplier
        buyStop: PersistentSeries = array.min(zigzagpivots) - atrDiff
        sellStop: PersistentSeries = array.max(zigzagpivots) + atrDiff
        dir: Persistent[int] = 1
        buyStopCurrent = array.min(zigzagpivots) - atrDiff
        sellStopCurrent = array.max(zigzagpivots) + atrDiff
        highConfirmation: Series = source if waitForClose else highSource
        lowConfirmation: Series = source if waitForClose else lowSource
        dir = -1 if dir == 1 and lowConfirmation[1] < buyStop[1] else 1 if dir == -1 and highConfirmation[1] > sellStop[1] else dir
        buyStop = math.max(nz(buyStop, buyStopCurrent), buyStopCurrent) if dir == 1 else buyStopCurrent
        sellStop = math.min(nz(sellStop, sellStopCurrent), sellStopCurrent) if dir == -1 else sellStopCurrent
        return (dir, buyStop if dir > 0 else sellStop)

    @export
    def zupertrend(length: int, history: int = 1, useAlternativeSource: bool = False, alternativeSource: float = close, source: float = close, highSource: float = high, lowSource: float = low, waitForClose: bool = False, atrlength: int = 22, multiplier: float = 1.0, atrMaType: str = 'sma'):
        zigzagHistory = history * 2 + 1
        zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagoscillators, zigzagoscillatordirs, zigzagtrendbias, zigzagdivergence, newPivot, doublePivot = zg.czigzag(length, zigzagHistory, alternativeSource if useAlternativeSource else highSource, alternativeSource if useAlternativeSource else lowSource)
        atrDiff = nz(eta.atr(atrMaType, atrlength), ta.tr) * multiplier
        buyStop: PersistentSeries = array.min(zigzagpivots) - atrDiff
        sellStop: PersistentSeries = array.max(zigzagpivots) + atrDiff
        dir: Persistent[int] = 1
        buyStopCurrent = array.min(zigzagpivots) - atrDiff
        sellStopCurrent = array.max(zigzagpivots) + atrDiff
        highConfirmation: Series = source if waitForClose else highSource
        lowConfirmation: Series = source if waitForClose else lowSource
        dir = -1 if dir == 1 and lowConfirmation[1] < buyStop[1] else 1 if dir == -1 and highConfirmation[1] > sellStop[1] else dir
        buyStop = math.max(nz(buyStop, buyStopCurrent), buyStopCurrent) if dir == 1 else buyStopCurrent
        sellStop = math.min(nz(sellStop, sellStopCurrent), sellStopCurrent) if dir == -1 else sellStopCurrent
        return (dir, buyStop if dir > 0 else sellStop)

    @export
    def zsupertrend(zigzagpivots: list[float], history: int = 1, source: float = close, highSource: float = high, lowSource: float = low, waitForClose: bool = False, atrMaType: str = 'sma', atrlength: int = 22, multiplier: float = 1):
        zigzagHistory = history * 2 + 1
        shortArray = array.slice(zigzagpivots, 0, zigzagHistory) if array.size(zigzagpivots) > zigzagHistory else zigzagpivots
        atrDiff = nz(eta.atr(atrMaType, atrlength), ta.tr) * multiplier
        buyStop: PersistentSeries = array.min(shortArray) - atrDiff
        sellStop: PersistentSeries = array.max(shortArray) + atrDiff
        dir: Persistent[int] = 1
        buyStopCurrent = array.min(shortArray) - atrDiff
        sellStopCurrent = array.max(shortArray) + atrDiff
        highConfirmation: Series = source if waitForClose else highSource
        lowConfirmation: Series = source if waitForClose else lowSource
        dir = -1 if dir == 1 and lowConfirmation[1] < buyStop[1] else 1 if dir == -1 and highConfirmation[1] > sellStop[1] else dir
        buyStop = math.max(nz(buyStop, buyStopCurrent), buyStopCurrent) if dir == 1 else buyStopCurrent
        sellStop = math.min(nz(sellStop, sellStopCurrent), sellStopCurrent) if dir == -1 else sellStopCurrent
        return (dir, buyStop if dir > 0 else sellStop)

    @export
    def msupertrend(bandType: str = 'bb', source: float = close, maType: str = 'sma', length: int = 60, useTrueRange: bool = False, highSource: float = high, lowSource: float = low, waitForClose: bool = False, numberOfBands: int = 20, multiplierStart: float = 0.5, multiplierStep: float = 0.5, trailingDistance: int = 10, trailStates: bool = False):
        bands = eta.multibands(bandType, source, maType, length, useTrueRange, False, numberOfBands, multiplierStart, multiplierStep)
        currentState = f_getCurrentState(source, bands)
        dir: Persistent[int] = 1
        buyStopState: Persistent = math.max(currentState - trailingDistance, 0)
        sellStopState: Persistent = math.min(currentState + trailingDistance, numberOfBands * 2)
        buyStop: PersistentSeries = array.get(bands, buyStopState)
        sellStop: PersistentSeries = array.get(bands, sellStopState)
        currentBuyStopState = math.max(currentState - trailingDistance, 0)
        currentSellStopState = math.min(currentState + trailingDistance, numberOfBands * 2)
        highConfirmation: Series = source if waitForClose else highSource
        lowConfirmation: Series = source if waitForClose else lowSource
        dir = -1 if dir == 1 and lowConfirmation[1] < buyStop[1] else 1 if dir == -1 and highConfirmation[1] > sellStop[1] else dir
        buyStopState = math.max(nz(buyStopState, currentBuyStopState), currentBuyStopState) if trailStates and dir == 1 else currentBuyStopState
        sellStopState = math.min(nz(sellStopState, currentSellStopState), currentSellStopState) if trailStates and dir == -1 else currentSellStopState
        buyStopCurrent = array.get(bands, currentBuyStopState)
        sellStopCurrent = array.get(bands, currentSellStopState)
        buyStop = math.max(nz(buyStop, buyStopCurrent), buyStopCurrent) if dir == 1 else buyStopCurrent
        sellStop = math.min(nz(sellStop, sellStopCurrent), sellStopCurrent) if dir == -1 else sellStopCurrent
        return (dir, buyStop if dir > 0 else sellStop)

    dir: int = 1
    supertrend = close
    if type == 'atr':
        dir_atr, supertrenda = supertrend_atr(length=atrLength, multiplier=atrMultiplier, atrMaType=atrMaType, source=source, highSource=highSource, lowSource=lowSource, waitForClose=waitForClose, delayed=stepped)
        dir = dir_atr
        supertrend = supertrenda
    elif type == 'bands':
        if useSupertrendParamsForBands:
            dir_bands, supertrendb = supertrend_bands(bandType=bandType, maType=bandMaType, length=bandLength, multiplier=bandMultiplier, source=source, highSource=highSource, lowSource=lowSource, waitForClose=waitForClose, useTrueRange=useTrueRange, useAlternateSource=useAlternateSource, alternateSource=alternateSource, sticky=stepped)
            dir = dir_bands
            supertrend = supertrendb
        else:
            dir_bands, supertrendb = supertrend_bands(bandType=bandType, maType=bandMaType, length=bandLength, multiplier=bandMultiplier, useTrueRange=useTrueRange, useAlternateSource=useAlternateSource, alternateSource=alternateSource, sticky=stepped)
            dir = dir_bands
            supertrend = supertrendb
    elif type == 'zigzag':
        if useSupertrendAndAtrParamsForZigzag:
            dir_zigzag, supertrendz = supertrend_zigzag(length=zigzagLength, history=history, useAlternativeSource=useAlternateSourceZigzag, alternativeSource=alternateSourceZigzag, source=source, highSource=highSource, lowSource=lowSource, waitForClose=waitForClose, atrlength=atrLength, multiplier=atrMultiplier, atrMaType=atrMaType)
            dir = dir_zigzag
            supertrend = supertrendz
        else:
            dir_zigzag, supertrendz = supertrend_zigzag(length=zigzagLength, history=history, useAlternativeSource=useAlternateSourceZigzag, alternativeSource=alternateSourceZigzag)
            dir = dir_zigzag
            supertrend = supertrendz
    elif type == 'zsupertrend':
        zigzagpivots, zigzagpivotbars, zigzagpivotdirs, zigzagpivotratios, zigzagoscillators, zigzagoscillatordirs, zigzagtrendbias, zigzagdivergence, newPivot, doublePivot = zg.zigzag(zigzagLength)
        dir_zigzag, supertrendz = zsupertrend(zigzagpivots, history)
        dir = dir_zigzag
        supertrend = supertrendz
    elif type == 'zupertrend':
        dir_zigzag, supertrendz = zupertrend(length=zigzagLength, history=history, useAlternativeSource=useAlternateSourceZigzag, alternativeSource=alternateSourceZigzag, source=source, highSource=highSource, lowSource=lowSource, waitForClose=waitForClose, atrlength=atrLength, multiplier=atrMultiplier, atrMaType=atrMaType)
        dir = dir_zigzag
        supertrend = supertrendz
    else:
        dir_m, supertrend_m = msupertrend(bandType, source, bandMaType, bandLength, useTrueRange, highSource, lowSource, waitForClose, numberOfBands, multiplierStart, multiplierStep, trailingDistance)
        dir = dir_m
        supertrend = supertrend_m
    plot(supertrend, color=color.green if dir > 0 else color.red, title='supertrend')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
