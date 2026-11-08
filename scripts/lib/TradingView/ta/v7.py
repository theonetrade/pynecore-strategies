"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    close, fixnan, high, hl2, hlc3, low, math, na, nz, plot, script, ta,
    time, timeframe, volume
)
from pynecore.types import Persistent, PersistentSeries, Series
from typing import Protocol, Any
import lib.TradingView.RelativeValue.v2 as TVrv


__all__ = ['ao', 'aroon', 'atr2', 'cagr', 'changePercent', 'coppock', 'dema', 'dema2', 'dm', 'donchian', 'ema2', 'eom', 'frama', 'ft', 'highestSince', 'ht', 'ichimoku', 'ift', 'kvo', 'lowestSince', 'pzo', 'relativeVolume', 'rma2', 'rms', 'rwi', 'stc', 'stochFull', 'stochRsi', 'supertrend', 'supertrend2', 'szo', 't3', 't3Alt', 'tema', 'tema2', 'trima', 'trix', 'uo', 'vStop', 'vStop2', 'vhf', 'vi', 'vzo', 'williamsFractal', 'wpo']


class _ProtocolAo(Protocol):
    def __call__(self, source: Series[float] = hl2, shortLength: int = 5, longLength: int = 34) -> Any: ...


class _ProtocolAroon(Protocol):
    def __call__(self, length: int) -> Any: ...


class _ProtocolAtr2(Protocol):
    def __call__(self, length: Series[float]) -> Any: ...


class _ProtocolCagr(Protocol):
    def __call__(self, entryTime: Series[int], entryPrice: Series[float], exitTime: Series[int], exitPrice: Series[float]) -> Any: ...


class _ProtocolChangepercent(Protocol):
    def __call__(self, newValue: Series[float], oldValue: Series[float]) -> Any: ...


class _ProtocolCoppock(Protocol):
    def __call__(self, source: Series[float], longLength: int, shortLength: int, smoothLength: int) -> Any: ...


class _ProtocolDema(Protocol):
    def __call__(self, source: Series[float], length: int) -> Any: ...


class _ProtocolEma2(Protocol):
    def __call__(self, source: Series[float], length: Series[float]) -> Any: ...


class _ProtocolDema2(Protocol):
    def __call__(self, source: Series[float], length: Series[float]) -> Any: ...


class _ProtocolDm(Protocol):
    def __call__(self, length: int) -> Any: ...


class _ProtocolDonchian(Protocol):
    def __call__(self, length: Series[int]) -> Any: ...


class _ProtocolEom(Protocol):
    def __call__(self, length: int, div: int = 10000) -> Any: ...


class _ProtocolFrama(Protocol):
    def __call__(self, source: Series[float], length: Series[int]) -> Any: ...


class _ProtocolFt(Protocol):
    def __call__(self, source: Series[float], length: int) -> Any: ...


class _ProtocolHighestsince(Protocol):
    def __call__(self, cond: Series[bool], source: Series[float] = high) -> Any: ...


class _ProtocolHt(Protocol):
    def __call__(self, source: Series[float]) -> Any: ...


class _ProtocolIchimoku(Protocol):
    def __call__(self, conLength: Series[int] = 9, baseLength: Series[int] = 26, senkouLength: Series[int] = 52) -> Any: ...


class _ProtocolIft(Protocol):
    def __call__(self, source: Series[float]) -> Any: ...


class _ProtocolKvo(Protocol):
    def __call__(self, fastLen: int, slowLen: int, trigLen: int) -> Any: ...


class _ProtocolLowestsince(Protocol):
    def __call__(self, cond: Series[bool], source: Series[float] = low) -> Any: ...


class _ProtocolPzo(Protocol):
    def __call__(self, length: int) -> Any: ...


class _ProtocolRelativevolume(Protocol):
    def __call__(self, length: int, anchorTimeframe: str = 'D', isCumulative: bool = True, adjustRealtime: bool = True) -> Any: ...


class _ProtocolRma2(Protocol):
    def __call__(self, source: Series[float], length: Series[float]) -> Any: ...


class _ProtocolRms(Protocol):
    def __call__(self, source: Series[float], length: Series[int]) -> Any: ...


class _ProtocolRwi(Protocol):
    def __call__(self, length: int) -> Any: ...


class _ProtocolStc(Protocol):
    def __call__(self, source: Series[float], fast: int, slow: int, cycle: int, d1: int, d2: int) -> Any: ...


class _ProtocolStochfull(Protocol):
    def __call__(self, periodK: int, smoothK: int, periodD: int) -> Any: ...


class _ProtocolStochrsi(Protocol):
    def __call__(self, lengthRsi: int, periodK: int, smoothK: int, periodD: int, source: Series[float] = close) -> Any: ...


class _ProtocolSupertrend(Protocol):
    def __call__(self, factor: Series[float], atrLength: int, wicks: bool = False) -> Any: ...


class _ProtocolSupertrend2(Protocol):
    def __call__(self, factor: Series[float], atrLength: Series[float], wicks: bool = False) -> Any: ...


class _ProtocolT3(Protocol):
    def __call__(self, source: Series[float], length: int, vf: float = 0.7) -> Any: ...


class _ProtocolT3alt(Protocol):
    def __call__(self, source: Series[float], length: Series[float], vf: float = 0.7) -> Any: ...


class _ProtocolTema(Protocol):
    def __call__(self, source: Series[float], length: int) -> Any: ...


class _ProtocolTema2(Protocol):
    def __call__(self, source: Series[float], length: Series[float]) -> Any: ...


class _ProtocolTrima(Protocol):
    def __call__(self, source: Series[float], length: Series[int]) -> Any: ...


class _ProtocolTrix(Protocol):
    def __call__(self, source: Series[float], length: int, signalLength: int, exponential: bool = True) -> Any: ...


class _ProtocolSzo(Protocol):
    def __call__(self, source: Series[float], length: int) -> Any: ...


class _ProtocolUo(Protocol):
    def __call__(self, fastLen: int, midLen: int, slowLen: int) -> Any: ...


class _ProtocolVhf(Protocol):
    def __call__(self, source: Series[float], length: int) -> Any: ...


class _ProtocolVi(Protocol):
    def __call__(self, length: int) -> Any: ...


class _ProtocolVstop(Protocol):
    def __call__(self, source: Series[float], atrLength: int, atrFactor: Series[float] = 1) -> Any: ...


class _ProtocolVstop2(Protocol):
    def __call__(self, source: Series[float], atrLength: Series[float], atrFactor: Series[float] = 1) -> Any: ...


class _ProtocolVzo(Protocol):
    def __call__(self, length: int) -> Any: ...


class _ProtocolWilliamsfractal(Protocol):
    def __call__(self, period: Series[int]) -> Any: ...


class _ProtocolWpo(Protocol):
    def __call__(self, length: int) -> Any: ...


ao: _ProtocolAo = Exported()
aroon: _ProtocolAroon = Exported()
atr2: _ProtocolAtr2 = Exported()
cagr: _ProtocolCagr = Exported()
changePercent: _ProtocolChangepercent = Exported()
coppock: _ProtocolCoppock = Exported()
dema: _ProtocolDema = Exported()
ema2: _ProtocolEma2 = Exported()
dema2: _ProtocolDema2 = Exported()
dm: _ProtocolDm = Exported()
donchian: _ProtocolDonchian = Exported()
eom: _ProtocolEom = Exported()
frama: _ProtocolFrama = Exported()
ft: _ProtocolFt = Exported()
highestSince: _ProtocolHighestsince = Exported()
ht: _ProtocolHt = Exported()
ichimoku: _ProtocolIchimoku = Exported()
ift: _ProtocolIft = Exported()
kvo: _ProtocolKvo = Exported()
lowestSince: _ProtocolLowestsince = Exported()
pzo: _ProtocolPzo = Exported()
relativeVolume: _ProtocolRelativevolume = Exported()
rma2: _ProtocolRma2 = Exported()
rms: _ProtocolRms = Exported()
rwi: _ProtocolRwi = Exported()
stc: _ProtocolStc = Exported()
stochFull: _ProtocolStochfull = Exported()
stochRsi: _ProtocolStochrsi = Exported()
supertrend: _ProtocolSupertrend = Exported()
supertrend2: _ProtocolSupertrend2 = Exported()
t3: _ProtocolT3 = Exported()
t3Alt: _ProtocolT3alt = Exported()
tema: _ProtocolTema = Exported()
tema2: _ProtocolTema2 = Exported()
trima: _ProtocolTrima = Exported()
trix: _ProtocolTrix = Exported()
szo: _ProtocolSzo = Exported()
uo: _ProtocolUo = Exported()
vhf: _ProtocolVhf = Exported()
vi: _ProtocolVi = Exported()
vStop: _ProtocolVstop = Exported()
vStop2: _ProtocolVstop2 = Exported()
vzo: _ProtocolVzo = Exported()
williamsFractal: _ProtocolWilliamsfractal = Exported()
wpo: _ProtocolWpo = Exported()


@script.library('ta', na_bool=True)
def main():
    def ewma(source: Series[float], alpha: Series[float]):
        result: Series[float] = na(float)
        result = alpha * source + (1.0 - alpha) * nz(result[1], source)
        return result

    @export
    def ao(source: Series[float] = hl2, shortLength: int = 5, longLength: int = 34):
        result: float = ta.sma(source, shortLength) - ta.sma(source, longLength)
        return result

    @export
    def aroon(length: int):
        aroonDown: float = 100 * (ta.lowestbars(low, length) + length) / length
        aroonUp: float = 100 * (ta.highestbars(high, length) + length) / length
        return (aroonUp, aroonDown)

    @export
    def atr2(length: Series[float]):
        alpha: float = 1.0 / math.max(1.0, length)
        result: float = ewma(ta.tr(True), alpha)
        return result

    @export
    def cagr(entryTime: Series[int], entryPrice: Series[float], exitTime: Series[int], exitPrice: Series[float]):
        MS_IN_ONE_DAY: int = 24 * 60 * 60 * 1000
        daysBetween: float = (exitTime - entryTime) / MS_IN_ONE_DAY
        __block_result__ = na
        if daysBetween >= 1 and (not (na(entryPrice) or na(exitPrice))):
            years: float = daysBetween / 365.0
            rate: float = exitPrice / entryPrice
            __block_result__ = 100 * (math.pow(rate, 1 / years) - 1)
        else:
            __block_result__ = na
        return __block_result__

    @export
    def changePercent(newValue: Series[float], oldValue: Series[float]):
        result: float = 100 * (newValue - oldValue) / oldValue
        return result

    @export
    def coppock(source: Series[float], longLength: int, shortLength: int, smoothLength: int):
        result: float = ta.wma(ta.roc(source, longLength) + ta.roc(source, shortLength), smoothLength)
        return result

    @export
    def dema(source: Series[float], length: int):
        ema1: float = ta.ema(source, length)
        ema2__0000001c__: float = ta.ema(ema1, length)
        result: float = 2 * ema1 - ema2__0000001c__
        return result

    @export
    def ema2(source: Series[float], length: Series[float]):
        alpha: float = 2.0 / (math.max(1.0, length) + 1.0)
        result: float = ewma(source, alpha)
        return result

    @export
    def dema2(source: Series[float], length: Series[float]):
        ema1: float = ema2(source, length)
        ema2__00000022__: float = ema2(ema1, length)
        result: float = 2 * ema1 - ema2__00000022__
        return result

    @export
    def dm(length: int):
        demax: float = math.max(ta.change(high), 0)
        demin: float = -math.min(ta.change(low), 0)
        result: float = ta.sma(demax, length) / (ta.sma(demax, length) + ta.sma(demin, length))
        return result

    @export
    def donchian(length: Series[int]):
        highest: float = ta.highest(length)
        lowest: float = ta.lowest(length)
        return (highest, lowest, math.avg(highest, lowest))

    @export
    def eom(length: int, div: int = 10000):
        result: float = ta.sma(div * ta.change(hl2) * (high - low) / volume, length)
        return result

    @export
    def frama(source: Series[float], length: Series[int]):
        len: int = math.round(length / 2)
        hh: Series[float] = ta.highest(len)
        ll: Series[float] = ta.lowest(len)
        n1: float = (hh - ll) / len
        n2: float = (hh[len] - ll[len]) / len
        n3: float = (ta.highest(length) - ta.lowest(length)) / length
        D: float = math.log((n1 + n2) / n3) / math.log(2)
        alpha: float = math.exp(-4.6 * (D - 1))
        result: float = ewma(source, alpha)
        return result

    @export
    def ft(source: Series[float], length: int):
        value1: Series[float] = 0.0
        fish: Series[float] = 0.0
        hh: float = ta.highest(source, length)
        ll: float = ta.lowest(source, length)
        value1 = 0.66 * ((source - ll) / (hh - ll) - 0.5) + 0.67 * nz(value1[1])
        value2: float = 0.999 if value1 > 0.99 else -0.999 if value1 < -0.99 else value1
        fish = 0.5 * math.log((1 + value2) / (1 - value2)) + 0.5 * nz(fish[1])
        result: float = fish
        return result

    @export
    def highestSince(cond: Series[bool], source: Series[float] = high):
        result: Persistent[float] = na(float)
        if cond:
            result = source
        result = math.max(nz(source, result), nz(result, source))
        return result

    @export
    def ht(source: Series[float]):
        result: float = 0.0962 * source + 0.5769 * nz(source[2]) - 0.5769 * nz(source[4]) - 0.0962 * nz(source[6])
        return result

    def midpoint(length: Series[int]):
        result: float = math.avg(ta.highest(length), ta.lowest(length))
        return result

    @export
    def ichimoku(conLength: Series[int] = 9, baseLength: Series[int] = 26, senkouLength: Series[int] = 52):
        tenkan: float = midpoint(conLength)
        kijun: float = midpoint(baseLength)
        senkouSpan1: float = math.avg(tenkan, kijun)
        senkouSpan2: float = midpoint(senkouLength)
        chikou: float = close
        return (tenkan, kijun, senkouSpan1, senkouSpan2, chikou)

    @export
    def ift(source: Series[float]):
        exp: float = math.exp(2.0 * source)
        result: float = (exp - 1.0) / (1.0 + exp)
        return result

    @export
    def kvo(fastLen: int, slowLen: int, trigLen: int):
        trend: float = math.sign(ta.change(hlc3)) * volume * 100
        fast: float = ta.ema(trend, fastLen)
        slow: float = ta.ema(trend, slowLen)
        kvo__00000062__: float = fast - slow
        trigger: float = ta.ema(kvo__00000062__, trigLen)
        return (kvo__00000062__, trigger)

    @export
    def lowestSince(cond: Series[bool], source: Series[float] = low):
        result: Persistent[float] = na(float)
        if cond:
            result = source
        result = math.min(nz(source, result), nz(result, source))
        return result

    def zone(source: Series[float], length: int):
        result: float = 100 * nz(ta.ema(math.sign(ta.change(close)) * source, length) / ta.ema(source, length))
        return result

    @export
    def pzo(length: int):
        result: float = zone(close, length)
        return result

    @export
    def relativeVolume(length: int, anchorTimeframe: str = 'D', isCumulative: bool = True, adjustRealtime: bool = True):
        anchor: bool = timeframe.change(anchorTimeframe)
        currVol: float = TVrv.calcCumulativeSeries(volume, anchor, adjustRealtime) if isCumulative else volume
        pastVol: float = TVrv.averageAtTime(volume, length, anchorTimeframe, isCumulative)
        volRatio: float = currVol / pastVol
        return (currVol, pastVol, volRatio)

    @export
    def rma2(source: Series[float], length: Series[float]):
        alpha: float = 1.0 / math.max(1.0, length)
        result: float = ewma(source, alpha)
        return result

    @export
    def rms(source: Series[float], length: Series[int]):
        result: float = math.sqrt(math.sum(math.pow(source, 2), length) / length)
        return result

    @export
    def rwi(length: int):
        divisor: float = ta.atr(length) * math.sqrt(length)
        rwiHigh: float = (high - nz(low[length])) / divisor
        rwiLow: float = (nz(high[length]) - low) / divisor
        return (rwiHigh, rwiLow)

    @export
    def stc(source: Series[float], fast: int, slow: int, cycle: int, d1: int, d2: int):
        macd: float = ta.ema(source, fast) - ta.ema(source, slow)
        k: float = nz(fixnan(ta.stoch(macd, macd, macd, cycle)))
        d: float = ta.ema(k, d1)
        kd: float = nz(fixnan(ta.stoch(d, d, d, cycle)))
        stc__0000008e__: float = ta.ema(kd, d2)
        result: float = math.max(math.min(stc__0000008e__, 100), 0)
        return result

    @export
    def stochFull(periodK: int, smoothK: int, periodD: int):
        k: float = ta.sma(ta.stoch(close, high, low, periodK), smoothK)
        d: float = ta.sma(k, periodD)
        return (k, d)

    @export
    def stochRsi(lengthRsi: int, periodK: int, smoothK: int, periodD: int, source: Series[float] = close):
        rsi: float = ta.rsi(source, lengthRsi)
        k: float = ta.sma(ta.stoch(rsi, rsi, rsi, periodK), smoothK)
        d: float = ta.sma(k, periodD)
        return (k, d)

    @export
    def supertrend(factor: Series[float], atrLength: int, wicks: bool = False):
        source: float = hl2
        direction: int = na(int)
        superTrend: Series[float] = na(float)
        atr: Series[float] = ta.atr(atrLength) * factor
        upperBand: Series[float] = source + atr
        lowerBand: Series[float] = source - atr
        highPrice: Series[float] = high if wicks else close
        lowPrice: Series[float] = low if wicks else close
        prevLowerBand: float = nz(lowerBand[1])
        prevUpperBand: float = nz(upperBand[1])
        lowerBand = lowerBand if lowerBand > prevLowerBand or lowPrice[1] < prevLowerBand else prevLowerBand
        upperBand = upperBand if upperBand < prevUpperBand or highPrice[1] > prevUpperBand else prevUpperBand
        prevSuperTrend: float = superTrend[1]
        if na(atr[1]):
            direction = 1
        elif prevSuperTrend == prevUpperBand:
            direction = -1 if highPrice > upperBand else 1
        else:
            direction = 1 if lowPrice < lowerBand else -1
        superTrend = lowerBand if direction == -1 else upperBand
        return (superTrend, direction)

    @export
    def supertrend2(factor: Series[float], atrLength: Series[float], wicks: bool = False):
        source: float = hl2
        direction: int = na(int)
        superTrend: Series[float] = na(float)
        atr: Series[float] = atr2(atrLength) * factor
        upperBand: Series[float] = source + atr
        lowerBand: Series[float] = source - atr
        highPrice: Series[float] = high if wicks else close
        lowPrice: Series[float] = low if wicks else close
        prevLowerBand: float = nz(lowerBand[1])
        prevUpperBand: float = nz(upperBand[1])
        lowerBand = lowerBand if lowerBand > prevLowerBand or lowPrice[1] < prevLowerBand else prevLowerBand
        upperBand = upperBand if upperBand < prevUpperBand or highPrice[1] > prevUpperBand else prevUpperBand
        prevSuperTrend: float = superTrend[1]
        if na(atr[1]):
            direction = 1
        elif prevSuperTrend == prevUpperBand:
            direction = -1 if highPrice > upperBand else 1
        else:
            direction = 1 if lowPrice < lowerBand else -1
        superTrend = lowerBand if direction == -1 else upperBand
        return (superTrend, direction)

    def gd(source: Series[float], length: int, vf: float):
        result: float = ta.ema(source, length) * (1 + vf) - ta.ema(ta.ema(source, length), length) * vf
        return result

    @export
    def t3(source: Series[float], length: int, vf: float = 0.7):
        result: float = gd(gd(gd(source, length, vf), length, vf), length, vf)
        return result

    def gd2(source: Series[float], length: Series[float], vf: float):
        result: float = ema2(source, length) * (1 + vf) - ema2(ema2(source, length), length) * vf
        return result

    @export
    def t3Alt(source: Series[float], length: Series[float], vf: float = 0.7):
        result: float = gd2(gd2(gd2(source, length, vf), length, vf), length, vf)
        return result

    @export
    def tema(source: Series[float], length: int):
        ema1: float = ta.ema(source, length)
        ema2__000000c7__: float = ta.ema(ema1, length)
        ema3: float = ta.ema(ema2__000000c7__, length)
        result: float = 3 * (ema1 - ema2__000000c7__) + ema3
        return result

    @export
    def tema2(source: Series[float], length: Series[float]):
        ema1: float = ema2(source, length)
        ema2__000000cb__: float = ema2(ema1, length)
        ema3: float = ema2(ema2__000000cb__, length)
        result: float = 3 * (ema1 - ema2__000000cb__) + ema3
        return result

    @export
    def trima(source: Series[float], length: Series[int]):
        result: float = ta.sma(ta.sma(source, math.ceil(length / 2)), math.floor(length / 2) + 1)
        return result

    @export
    def trix(source: Series[float], length: int, signalLength: int, exponential: bool = True):
        triple: float = ta.ema(ta.ema(ta.ema(source, length), length), length)
        trix__000000d7__: float = ta.roc(triple, 1)
        signal: float = ta.ema(trix__000000d7__, signalLength) if exponential else ta.sma(trix__000000d7__, signalLength)
        hist: float = trix__000000d7__ - signal
        return (trix__000000d7__, signal, hist)

    @export
    def szo(source: Series[float], length: int):
        trend: float = math.sign(ta.change(source))
        sentPos: float = tema(trend, length)
        result: float = 100 * sentPos / length
        return result

    def uoAverage(bp: Series[float], trange: Series[float], length: int):
        result: float = math.sum(bp, length) / math.sum(trange, length)
        return result

    @export
    def uo(fastLen: int, midLen: int, slowLen: int):
        tMax: float = math.max(high, close[1])
        tMin: float = math.min(low, close[1])
        tr: float = tMax - tMin
        bp: float = close - tMin
        avg1: float = uoAverage(bp, tr, fastLen)
        avg2: float = uoAverage(bp, tr, midLen)
        avg3: float = uoAverage(bp, tr, slowLen)
        result: float = 100 * (4 * avg1 + 2 * avg2 + avg3) / 7
        return result

    @export
    def vhf(source: Series[float], length: int):
        sumChanges: float = math.sum(math.abs(ta.change(source)), length)
        result: float = math.abs(ta.highest(source, length) - ta.lowest(source, length)) / sumChanges
        return result

    @export
    def vi(length: int):
        divisor = math.sum(ta.atr(1), length)
        viPlus = math.sum(math.abs(high - nz(low[1])), length) / divisor
        viMinus = math.sum(math.abs(low - nz(high[1])), length) / divisor
        return (viPlus, viMinus)

    @export
    def vStop(source: Series[float], atrLength: int, atrFactor: Series[float] = 1):
        src: float = nz(source, close)
        atrM: float = nz(ta.atr(atrLength) * atrFactor, ta.tr(True))
        trendUp: PersistentSeries[bool] = True
        max: Persistent[float] = src
        min: Persistent[float] = src
        stop: Persistent[float] = 0.0
        max = math.max(max, src)
        min = math.min(min, src)
        stop = nz(math.max(stop, max - atrM) if trendUp else math.min(stop, min + atrM), src)
        trendUp = src - stop >= 0.0
        if trendUp != nz(trendUp[1], True):
            max = src
            min = src
            stop = max - atrM if trendUp else min + atrM
        return (stop, trendUp)

    @export
    def vStop2(source: Series[float], atrLength: Series[float], atrFactor: Series[float] = 1):
        src: float = nz(source, close)
        atrM: float = nz(atr2(atrLength) * atrFactor, ta.tr(True))
        trendUp: PersistentSeries[bool] = True
        max: Persistent[float] = src
        min: Persistent[float] = src
        stop: Persistent[float] = 0.0
        max = math.max(max, src)
        min = math.min(min, src)
        stop = nz(math.max(stop, max - atrM) if trendUp else math.min(stop, min + atrM), src)
        trendUp = src - stop >= 0.0
        if trendUp != nz(trendUp[1], True):
            max = src
            min = src
            stop = max - atrM if trendUp else min + atrM
        return (stop, trendUp)

    @export
    def vzo(length: int):
        result: float = zone(volume, length)
        return result

    def flag(source: Series[float], n: Series[int], direction: int):
        src: Series[float] = source * direction
        flag__00000136__: bool = True
        flag0: bool = True
        flag1: bool = True
        flag2: bool = True
        flag3: bool = True
        flag4: bool = True
        for i in pine_range(1, n, 1):
            flag__00000136__ = flag__00000136__ and src[n - i] < src[n]
            flag0 = flag0 and src[n + i] < src[n]
            flag1 = flag1 and src[n + 1] <= src[n] and (src[n + i + 1] < src[n])
            flag2 = flag2 and src[n + 1] <= src[n] and (src[n + 2] <= src[n]) and (src[n + i + 2] < src[n])
            flag3 = flag3 and src[n + 1] <= src[n] and (src[n + 2] <= src[n]) and (src[n + 3] <= src[n]) and (src[n + i + 3] < src[n])
            flag4 = flag4 and src[n + 1] <= src[n] and (src[n + 2] <= src[n]) and (src[n + 3] <= src[n]) and (src[n + 4] <= src[n]) and (src[n + i + 4] < src[n])
        flags: bool = flag0 or flag1 or flag2 or flag3 or flag4
        result: bool = flag__00000136__ and flags
        return result

    @export
    def williamsFractal(period: Series[int]):
        upFractal: bool = flag(high, period, 1)
        downFractal: bool = flag(low, period, -1)
        return (upFractal, downFractal)

    @export
    def wpo(length: int):
        tt: float = 2 * math.pi / math.asin(close[1] / high)
        ti: float = math.sign(ta.change(close)) * tt
        result: float = ta.ema(ti, length)
        return result

    plot(cagr(time[1], close[1], time, close))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
