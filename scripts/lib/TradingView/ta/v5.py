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
    time, volume
)
from pynecore.types import Persistent, Series
from typing import Protocol, Any


__all__ = ['allTimeHigh', 'allTimeLow', 'ao', 'aroon', 'cagr', 'coppock', 'dema', 'dema2', 'dm', 'donchian', 'ema2', 'eom', 'frama', 'ft', 'ht', 'ichimoku', 'ift', 'kvo', 'pzo', 'rms', 'rwi', 'stc', 'stochFull', 'stochRsi', 'supertrend', 'szo', 't3', 't3Alt', 'tema', 'tema2', 'trima', 'trima2', 'trix', 'uo', 'vhf', 'vi', 'vzo', 'williamsFractal', 'wpo']


class _ProtocolCagr(Protocol):
    def __call__(self, entryTime: Series[int], entryPrice: Series[float], exitTime: Series[int], exitPrice: Series[float]) -> Any: ...


class _ProtocolAlltimehigh(Protocol):
    def __call__(self, src: Series[float] = high) -> Any: ...


class _ProtocolAlltimelow(Protocol):
    def __call__(self, src: Series[float] = low) -> Any: ...


class _ProtocolEma2(Protocol):
    def __call__(self, src: Series[float], length: Series[float]) -> Any: ...


class _ProtocolDema(Protocol):
    def __call__(self, src: Series[float], length: int) -> Any: ...


class _ProtocolDema2(Protocol):
    def __call__(self, src: Series[float], length: Series[float]) -> Any: ...


class _ProtocolTema(Protocol):
    def __call__(self, src: Series[float], length: int) -> Any: ...


class _ProtocolTema2(Protocol):
    def __call__(self, src: Series[float], length: Series[float]) -> Any: ...


class _ProtocolTrima(Protocol):
    def __call__(self, src: Series[float], length: int) -> Any: ...


class _ProtocolTrima2(Protocol):
    def __call__(self, src: Series[float], length: Series[int]) -> Any: ...


class _ProtocolT3(Protocol):
    def __call__(self, src: Series[float], length: int, alpha: float = 0.7) -> Any: ...


class _ProtocolT3alt(Protocol):
    def __call__(self, src: Series[float], length: Series[float], alpha: float = 0.7) -> Any: ...


class _ProtocolFrama(Protocol):
    def __call__(self, src: Series[float], length: Series[int]) -> Any: ...


class _ProtocolDonchian(Protocol):
    def __call__(self, length: Series[int]) -> Any: ...


class _ProtocolIchimoku(Protocol):
    def __call__(self, conLength: Series[int] = 9, baseLength: Series[int] = 26, senkouLength: Series[int] = 52) -> Any: ...


class _ProtocolStochfull(Protocol):
    def __call__(self, periodK: int, smoothK: int, periodD: int) -> Any: ...


class _ProtocolStochrsi(Protocol):
    def __call__(self, lengthRsi: int, periodK: int, smoothK: int, periodD: int, src: Series[float] = close) -> Any: ...


class _ProtocolDm(Protocol):
    def __call__(self, length: int) -> Any: ...


class _ProtocolUo(Protocol):
    def __call__(self, fastLen: int, midLen: int, slowLen: int) -> Any: ...


class _ProtocolAo(Protocol):
    def __call__(self, src: Series[float] = hl2, shortLength: Series[int] = 5, longLength: Series[int] = 34) -> Any: ...


class _ProtocolKvo(Protocol):
    def __call__(self, fastLen: int, slowLen: int, trigLen: int) -> Any: ...


class _ProtocolVhf(Protocol):
    def __call__(self, src: Series[float], length: int) -> Any: ...


class _ProtocolStc(Protocol):
    def __call__(self, src: Series[float], fast: int, slow: int, cycle: int, d1: int, d2: int) -> Any: ...


class _ProtocolVi(Protocol):
    def __call__(self, length: int) -> Any: ...


class _ProtocolRwi(Protocol):
    def __call__(self, length: int) -> Any: ...


class _ProtocolVzo(Protocol):
    def __call__(self, length: int) -> Any: ...


class _ProtocolPzo(Protocol):
    def __call__(self, length: int) -> Any: ...


class _ProtocolSzo(Protocol):
    def __call__(self, src: Series[float], length: int) -> Any: ...


class _ProtocolWpo(Protocol):
    def __call__(self, length: int) -> Any: ...


class _ProtocolCoppock(Protocol):
    def __call__(self, src: Series[float], longLength: int, shortLength: int, smoothLength: int) -> Any: ...


class _ProtocolTrix(Protocol):
    def __call__(self, src: Series[float], length: int, signalLength: int, exponential: bool = True) -> Any: ...


class _ProtocolAroon(Protocol):
    def __call__(self, length: int) -> Any: ...


class _ProtocolEom(Protocol):
    def __call__(self, length: int, div: int = 10000) -> Any: ...


class _ProtocolFt(Protocol):
    def __call__(self, src: Series[float], length: int) -> Any: ...


class _ProtocolIft(Protocol):
    def __call__(self, src: Series[float]) -> Any: ...


class _ProtocolHt(Protocol):
    def __call__(self, src: Series[float]) -> Any: ...


class _ProtocolSupertrend(Protocol):
    def __call__(self, factor: Series[float], atrPeriod: int, wicks: bool = False) -> Any: ...


class _ProtocolRms(Protocol):
    def __call__(self, src: Series[float], length: int) -> Any: ...


class _ProtocolWilliamsfractal(Protocol):
    def __call__(self, period: Series[int]) -> Any: ...


cagr: _ProtocolCagr = Exported()
allTimeHigh: _ProtocolAlltimehigh = Exported()
allTimeLow: _ProtocolAlltimelow = Exported()
ema2: _ProtocolEma2 = Exported()
dema: _ProtocolDema = Exported()
dema2: _ProtocolDema2 = Exported()
tema: _ProtocolTema = Exported()
tema2: _ProtocolTema2 = Exported()
trima: _ProtocolTrima = Exported()
trima2: _ProtocolTrima2 = Exported()
t3: _ProtocolT3 = Exported()
t3Alt: _ProtocolT3alt = Exported()
frama: _ProtocolFrama = Exported()
donchian: _ProtocolDonchian = Exported()
ichimoku: _ProtocolIchimoku = Exported()
stochFull: _ProtocolStochfull = Exported()
stochRsi: _ProtocolStochrsi = Exported()
dm: _ProtocolDm = Exported()
uo: _ProtocolUo = Exported()
ao: _ProtocolAo = Exported()
kvo: _ProtocolKvo = Exported()
vhf: _ProtocolVhf = Exported()
stc: _ProtocolStc = Exported()
vi: _ProtocolVi = Exported()
rwi: _ProtocolRwi = Exported()
vzo: _ProtocolVzo = Exported()
pzo: _ProtocolPzo = Exported()
szo: _ProtocolSzo = Exported()
wpo: _ProtocolWpo = Exported()
coppock: _ProtocolCoppock = Exported()
trix: _ProtocolTrix = Exported()
aroon: _ProtocolAroon = Exported()
eom: _ProtocolEom = Exported()
ft: _ProtocolFt = Exported()
ift: _ProtocolIft = Exported()
ht: _ProtocolHt = Exported()
supertrend: _ProtocolSupertrend = Exported()
rms: _ProtocolRms = Exported()
williamsFractal: _ProtocolWilliamsfractal = Exported()


@script.library('ta', na_bool=True)
def main():
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
    def allTimeHigh(src: Series[float] = high):
        result: Persistent[float] = src
        result = math.max(nz(result, src), nz(src, result))
        return result

    @export
    def allTimeLow(src: Series[float] = low):
        result: Persistent[float] = src
        result = math.min(nz(result, src), nz(src, result))
        return result

    @export
    def ema2(src: Series[float], length: Series[float]):
        result: Series[float] = na(float)
        alpha: float = 2.0 / (math.max(1.0, length) + 1.0)
        beta: float = 1.0 - alpha
        result = alpha * src + beta * nz(result[1], src)
        return result

    @export
    def dema(src: Series[float], length: int):
        ema1: float = ta.ema(src, length)
        ema2__00000016__: float = ta.ema(ema1, length)
        result: float = 2 * ema1 - ema2__00000016__
        return result

    @export
    def dema2(src: Series[float], length: Series[float]):
        ema1: float = ema2(src, length)
        ema2__00000019__: float = ema2(ema1, length)
        result: float = 2 * ema1 - ema2__00000019__
        return result

    @export
    def tema(src: Series[float], length: int):
        ema1: float = ta.ema(src, length)
        ema2__0000001d__: float = ta.ema(ema1, length)
        ema3: float = ta.ema(ema2__0000001d__, length)
        result: float = 3 * (ema1 - ema2__0000001d__) + ema3
        return result

    @export
    def tema2(src: Series[float], length: Series[float]):
        ema1: float = ema2(src, length)
        ema2__00000021__: float = ema2(ema1, length)
        ema3: float = ema2(ema2__00000021__, length)
        result: float = 3 * (ema1 - ema2__00000021__) + ema3
        return result

    @export
    def trima(src: Series[float], length: int):
        result: float = ta.sma(ta.sma(src, math.ceil(length / 2)), math.floor(length / 2) + 1)
        return result

    @export
    def trima2(src: Series[float], length: Series[int]):
        lenCeil: float = math.ceil(length / 2)
        lenFloor: float = math.floor(length / 2)
        sma1: Series[float] = 0.0
        sma2: float = 0.0
        for i in pine_range(0, lenCeil - 1, 1):
            sma1 = sma1 + nz(src[i])
        sma1 = sma1 / lenCeil
        for i in pine_range(0, lenFloor, 1):
            sma2 = sma2 + sma1[i]
        result: float = sma2 / (lenFloor + 1)
        return result

    def gd(src: Series[float], length: int, alpha: float):
        result: float = ta.ema(src, length) * (1 + alpha) - ta.ema(ta.ema(src, length), length) * alpha
        return result

    @export
    def t3(src: Series[float], length: int, alpha: float = 0.7):
        result: float = gd(gd(gd(src, length, alpha), length, alpha), length, alpha)
        return result

    def gd2(src: Series[float], length: Series[float], alpha: float):
        result: float = ema2(src, length) * (1 + alpha) - ema2(ema2(src, length), length) * alpha
        return result

    @export
    def t3Alt(src: Series[float], length: Series[float], alpha: float = 0.7):
        result: float = gd2(gd2(gd2(src, length, alpha), length, alpha), length, alpha)
        return result

    @export
    def frama(src: Series[float], length: Series[int]):
        len: int = math.round(length / 2)
        hh: Series[float] = ta.highest(len)
        ll: Series[float] = ta.lowest(len)
        n1: float = (hh - ll) / len
        n2: float = (hh[len] - ll[len]) / len
        n3: float = (ta.highest(length) - ta.lowest(length)) / length
        D: float = math.log((n1 + n2) / n3) / math.log(2)
        alpha: float = math.exp(-4.6 * (D - 1))
        frama__0000004d__: Series[float] = src
        frama__0000004d__ = alpha * src + (1 - alpha) * nz(frama__0000004d__[1], nz(src[1], src))
        result: float = frama__0000004d__
        return result

    @export
    def donchian(length: Series[int]):
        result: float = math.avg(ta.lowest(length), ta.highest(length))
        return result

    @export
    def ichimoku(conLength: Series[int] = 9, baseLength: Series[int] = 26, senkouLength: Series[int] = 52):
        tenkan: float = donchian(conLength)
        kijun: float = donchian(baseLength)
        senkouSpan1: float = math.avg(tenkan, kijun)
        senkouSpan2: float = donchian(senkouLength)
        chikou: float = close
        return (tenkan, kijun, senkouSpan1, senkouSpan2, chikou)

    @export
    def stochFull(periodK: int, smoothK: int, periodD: int):
        k: float = ta.sma(ta.stoch(close, high, low, periodK), smoothK)
        d: float = ta.sma(k, periodD)
        return (k, d)

    @export
    def stochRsi(lengthRsi: int, periodK: int, smoothK: int, periodD: int, src: Series[float] = close):
        rsi: float = ta.rsi(src, lengthRsi)
        k: float = ta.sma(ta.stoch(rsi, rsi, rsi, periodK), smoothK)
        d: float = ta.sma(k, periodD)
        return (k, d)

    @export
    def dm(length: int):
        demax: float = math.max(ta.change(high), 0)
        demin: float = -math.min(ta.change(low), 0)
        result: float = ta.sma(demax, length) / (ta.sma(demax, length) + ta.sma(demin, length))
        return result

    def uoAverage(bp, trange, length):
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
    def ao(src: Series[float] = hl2, shortLength: Series[int] = 5, longLength: Series[int] = 34):
        result: float = ta.sma(src, shortLength) - ta.sma(src, longLength)
        return result

    @export
    def kvo(fastLen: int, slowLen: int, trigLen: int):
        trend: float = math.sign(ta.change(hlc3)) * volume * 100
        fast: float = ta.ema(trend, fastLen)
        slow: float = ta.ema(trend, slowLen)
        kvo__0000007b__: float = fast - slow
        trigger: float = ta.ema(kvo__0000007b__, trigLen)
        return (kvo__0000007b__, trigger)

    @export
    def vhf(src: Series[float], length: int):
        result: float = math.abs(ta.highest(src, length) - ta.lowest(src, length)) / math.sum(math.abs(ta.change(src)), length)
        return result

    @export
    def stc(src: Series[float], fast: int, slow: int, cycle: int, d1: int, d2: int):
        macd: float = ta.ema(src, fast) - ta.ema(src, slow)
        k: float = nz(fixnan(ta.stoch(macd, macd, macd, cycle)))
        d: float = ta.ema(k, d1)
        kd: float = nz(fixnan(ta.stoch(d, d, d, cycle)))
        stc__0000008f__: float = ta.ema(kd, d2)
        result: float = math.max(math.min(stc__0000008f__, 100), 0)
        return result

    @export
    def vi(length: int):
        divisor = math.sum(ta.atr(1), length)
        viPlus = math.sum(math.abs(high - nz(low[1])), length) / divisor
        viMinus = math.sum(math.abs(low - nz(high[1])), length) / divisor
        return (viPlus, viMinus)

    @export
    def rwi(length: int):
        divisor: float = ta.atr(length) * math.sqrt(length)
        rwiHigh: float = (high - nz(low[length])) / divisor
        rwiLow: float = (nz(high[length]) - low) / divisor
        return (rwiHigh, rwiLow)

    def zone(src: Series[float], length: int):
        result: float = 100 * nz(ta.ema(math.sign(ta.change(close)) * src, length) / ta.ema(src, length))
        return result

    @export
    def vzo(length: int):
        result: float = zone(volume, length)
        return result

    @export
    def pzo(length: int):
        result: float = zone(close, length)
        return result

    @export
    def szo(src: Series[float], length: int):
        trend: float = math.sign(ta.change(src))
        sentPos: float = tema(trend, length)
        result: float = 100 * sentPos / length
        return result

    @export
    def wpo(length: int):
        tt: float = 2 * math.pi / math.asin(close[1] / high)
        ti: float = math.sign(ta.change(close)) * tt
        result: float = ta.ema(ti, length)
        return result

    @export
    def coppock(src: Series[float], longLength: int, shortLength: int, smoothLength: int):
        result: float = ta.wma(ta.roc(src, longLength) + ta.roc(src, shortLength), smoothLength)
        return result

    @export
    def trix(src: Series[float], length: int, signalLength: int, exponential: bool = True):
        triple: float = ta.ema(ta.ema(ta.ema(src, length), length), length)
        trix__000000c0__: float = ta.roc(triple, 1)
        signal: float = ta.ema(trix__000000c0__, signalLength) if exponential else ta.sma(trix__000000c0__, signalLength)
        hist: float = trix__000000c0__ - signal
        return (trix__000000c0__, signal, hist)

    @export
    def aroon(length: int):
        aroonDown: float = 100 * (ta.lowestbars(low, length) + length) / length
        aroonUp: float = 100 * (ta.highestbars(high, length) + length) / length
        return (aroonUp, aroonDown)

    @export
    def eom(length: int, div: int = 10000):
        result: float = ta.sma(div * ta.change(hl2) * (high - low) / volume, length)
        return result

    @export
    def ft(src: Series[float], length: int):
        value1: Series[float] = 0.0
        fish: Series[float] = 0.0
        hh: float = ta.highest(src, length)
        ll: float = ta.lowest(src, length)
        value1 = 0.66 * ((src - ll) / (hh - ll) - 0.5) + 0.67 * nz(value1[1])
        value2: float = 0.999 if value1 > 0.99 else -0.999 if value1 < -0.99 else value1
        fish = 0.5 * math.log((1 + value2) / (1 - value2)) + 0.5 * nz(fish[1])
        result: float = fish
        return result

    @export
    def ift(src: Series[float]):
        exp: float = math.exp(2.0 * src)
        result: float = (exp - 1.0) / (1.0 + exp)
        return result

    @export
    def ht(src: Series[float]):
        result: float = 0.0962 * src + 0.5769 * nz(src[2]) - 0.5769 * nz(src[4]) - 0.0962 * nz(src[6])
        return result

    @export
    def supertrend(factor: Series[float], atrPeriod: int, wicks: bool = False):
        src: float = hl2
        direction: int = na(int)
        superTrend: Series[float] = na(float)
        atr: Series[float] = ta.atr(atrPeriod) * factor
        upperBand: Series[float] = src + atr
        lowerBand: Series[float] = src - atr
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
    def rms(src: Series[float], length: int):
        result: float = math.sqrt(math.sum(math.pow(src, 2), length) / length)
        return result

    def flag(source: Series[float], n: Series[int], direction: int):
        src: Series[float] = source * direction
        flag__0000010b__: bool = True
        flag0: bool = True
        flag1: bool = True
        flag2: bool = True
        flag3: bool = True
        flag4: bool = True
        for i in pine_range(1, n, 1):
            flag__0000010b__ = flag__0000010b__ and src[n - i] < src[n]
            flag0 = flag0 and src[n + i] < src[n]
            flag1 = flag1 and src[n + 1] <= src[n] and (src[n + i + 1] < src[n])
            flag2 = flag2 and src[n + 1] <= src[n] and (src[n + 2] <= src[n]) and (src[n + i + 2] < src[n])
            flag3 = flag3 and src[n + 1] <= src[n] and (src[n + 2] <= src[n]) and (src[n + 3] <= src[n]) and (src[n + i + 3] < src[n])
            flag4 = flag4 and src[n + 1] <= src[n] and (src[n + 2] <= src[n]) and (src[n + 3] <= src[n]) and (src[n + 4] <= src[n]) and (src[n + i + 4] < src[n])
        flags: bool = flag0 or flag1 or flag2 or flag3 or flag4
        result: bool = flag__0000010b__ and flags
        return result

    @export
    def williamsFractal(period: Series[int]):
        upFractal: bool = flag(high, period, 1)
        downFractal: bool = flag(low, period, -1)
        return (upFractal, downFractal)

    plot(cagr(time[1], close[1], time, close))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
