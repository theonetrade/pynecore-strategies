"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_export import Exported, export
from pynecore.lib import close, high, low, math, na, nz, open, script, ta
from pynecore.types import Series
from typing import Protocol, Any


__all__ = ['atr_anysource', 'fusion', 'rngfilt', 'selective_ma', 'smoothrng', 'supertrend_anysource', 'trendUp', 'zonestrength']


class _ProtocolSelectiveMa(Protocol):
    def __call__(self, condition: bool, source: float, length: int) -> Any: ...


class _ProtocolTrendup(Protocol):
    def __call__(self, source: float) -> Any: ...


class _ProtocolSmoothrng(Protocol):
    def __call__(self, source: float, sampling_period: int = 50, range_mult: float = 3) -> Any: ...


class _ProtocolRngfilt(Protocol):
    def __call__(self, source: float, smoothrng__0000001e__: float) -> Any: ...


class _ProtocolFusion(Protocol):
    def __call__(self, overallLength: int = 3, rsiLength: int = 14, mfiLength: int = 14, macdLength: int = 12, cciLength: int = 12, tsiLength: int = 13, rviLength: int = 10, atrLength: int = 14, adxLength: int = 14) -> Any: ...


class _ProtocolZonestrength(Protocol):
    def __call__(self, amplitude: int, wavelength: int) -> Any: ...


class _ProtocolAtrAnysource(Protocol):
    def __call__(self, source: float, atr_length: int) -> Any: ...


class _ProtocolSupertrendAnysource(Protocol):
    def __call__(self, source: float, factor: float, atr_length: int) -> Any: ...


selective_ma: _ProtocolSelectiveMa = Exported()
trendUp: _ProtocolTrendup = Exported()
smoothrng: _ProtocolSmoothrng = Exported()
rngfilt: _ProtocolRngfilt = Exported()
fusion: _ProtocolFusion = Exported()
zonestrength: _ProtocolZonestrength = Exported()
atr_anysource: _ProtocolAtrAnysource = Exported()
supertrend_anysource: _ProtocolSupertrendAnysource = Exported()


@script.library('wbburgin_utils')
def main():
    @export
    def selective_ma(condition: bool, source: float, length: int):
        selective_data: Series = source if condition else na
        sum_selective_data: float = 0.0
        count: int = 0
        for i in pine_range(0, length - 1, 1):
            if not na(selective_data[i]):
                sum_selective_data = sum_selective_data + selective_data[i]
                count = count + 1
        selma = sum_selective_data / count if count > 0 else na
        return selma

    @export
    def trendUp(source: Series[float]):
        upward: Series[float] = 0.0
        upward = nz(upward[1]) + 1 if source > source[1] else 0 if source < source[1] else nz(upward[1])
        return upward

    @export
    def smoothrng(source: Series[float], sampling_period: int = 50, range_mult: float = 3):
        wper = sampling_period * 2 - 1
        avrng = ta.ema(math.abs(source - source[1]), sampling_period)
        smoothrng__00000013__ = ta.ema(avrng, wper) * range_mult
        return smoothrng__00000013__

    @export
    def rngfilt(source: float, smoothrng__0000001e__: float):
        rngfilt__0000001e__: Series = source
        rngfilt__0000001e__ = (nz(rngfilt__0000001e__[1]) if source - smoothrng__0000001e__ < nz(rngfilt__0000001e__[1]) else source - smoothrng__0000001e__) if source > nz(rngfilt__0000001e__[1]) else nz(rngfilt__0000001e__[1]) if source + smoothrng__0000001e__ > nz(rngfilt__0000001e__[1]) else source + smoothrng__0000001e__
        return rngfilt__0000001e__

    @export
    def fusion(overallLength: int = 3, rsiLength: int = 14, mfiLength: int = 14, macdLength: int = 12, cciLength: int = 12, tsiLength: int = 13, rviLength: int = 10, atrLength: int = 14, adxLength: int = 14):
        rsi = (ta.rsi(close, rsiLength) - 50) / 20
        mfi = (ta.mfi(close, mfiLength) - 50) / 20
        macdRaw, _, _ = ta.macd(close, macdLength * overallLength, macdLength * 2 * overallLength, 9)
        mHighest = ta.highest(macdRaw, macdLength * overallLength)
        mLowest = ta.lowest(macdRaw, macdLength * overallLength)
        __block_result__ = na
        if macdRaw > 0:
            __block_result__ = macdRaw / mHighest
        elif macdRaw < 0:
            __block_result__ = macdRaw / math.abs(mLowest)
        else:
            __block_result__ = 0
        macd = __block_result__
        cci = ta.cci(close, cciLength * overallLength) / 100
        tsiRaw = ta.tsi(close, tsiLength * overallLength, tsiLength * 2 * overallLength)
        tHighest = ta.highest(tsiRaw, tsiLength * overallLength)
        tLowest = ta.lowest(tsiRaw, tsiLength * overallLength)
        __block_result_1__ = na
        if tsiRaw > 0:
            __block_result_1__ = tsiRaw / tHighest
        elif tsiRaw < 0:
            __block_result_1__ = tsiRaw / math.abs(tLowest)
        else:
            __block_result_1__ = 0
        tsi = __block_result_1__
        src = close
        len: int = 14
        stddev = ta.stdev(src, rviLength * overallLength)
        upper = ta.ema(0 if ta.change(src) <= 0 else stddev, len)
        lower = ta.ema(0 if ta.change(src) > 0 else stddev, len)
        rvi = (upper / (upper + lower) * 100 - 50) / 20
        super_dir = math.avg(rsi, mfi, macd, cci, tsi, rvi)
        atrRaw = ta.atr(atrLength)
        atrStdev = ta.stdev(atrRaw, atrLength)
        atrEMA = ta.ema(atrRaw, atrLength)
        atr = (atrRaw / atrEMA - 1) * (1 + atrStdev) - 1
        _, _, adxRaw = ta.dmi(17, adxLength)
        adxStdev = ta.stdev(adxRaw, adxLength)
        adxEMA = ta.ema(adxRaw, adxLength)
        adx = (adxRaw / adxEMA - 1) * (1 + adxStdev)
        super_nondirRough = math.avg(atr, adx)
        highestNondir = ta.highest(super_nondirRough, 200)
        lowestNondir = ta.lowest(super_nondirRough, 200)
        __block_result_2__ = na
        if super_nondirRough > 0:
            __block_result_2__ = super_nondirRough / highestNondir
        elif super_nondirRough < 0:
            __block_result_2__ = super_nondirRough / math.abs(lowestNondir)
        else:
            __block_result_2__ = 0
        super_nondir = __block_result_2__
        return (super_dir, super_nondir)

    @export
    def zonestrength(amplitude: int, wavelength: int):
        ohlc_avg = 0.25 * (open + high + low + close)
        ocp_avg = 0.5 * (open[1] + close[1])
        g = math.avg(ohlc_avg, ocp_avg)
        h = g * (1 + ((high - ohlc_avg + high - ocp_avg if high > ohlc_avg else high - ocp_avg) if ohlc_avg > ocp_avg else low - ocp_avg - ohlc_avg + low if low < ohlc_avg else low - ocp_avg) * -1 / g)
        amp_highest = ta.highest(h, amplitude)
        amp_lowest = ta.lowest(h, amplitude)
        high_deviation = amp_highest - high
        low_deviation = low - amp_lowest
        m = amp_lowest if high_deviation > low_deviation else amp_highest
        n = amp_lowest if high_deviation < low_deviation else amp_highest
        o = math.avg(amp_highest, amp_lowest)
        q4 = math.avg(o, m)
        q2 = math.avg(o, n)
        s = ta.ema(amp_lowest, wavelength)
        t = ta.ema(amp_highest, wavelength)
        u = (ohlc_avg - s) / (t - s) - 0.5
        zonestrength__0000004e__ = u
        return zonestrength__0000004e__

    @export
    def atr_anysource(source: Series[float], atr_length: int):
        highest: Series = ta.highest(source, atr_length)
        lowest = ta.lowest(source, atr_length)
        trueRange = highest - lowest if na(highest[1]) else math.max(math.max(highest - lowest, math.abs(highest - source[1])), math.abs(lowest - source[1]))
        return ta.rma(trueRange, atr_length)

    @export
    def supertrend_anysource(source: Series[float], factor: float, atr_length: int):
        atr: Series = atr_anysource(source, atr_length)
        upperBand: Series = source + factor * atr
        lowerBand: Series = source - factor * atr
        prevLowerBand = nz(lowerBand[1])
        prevUpperBand = nz(upperBand[1])
        lowerBand = lowerBand if lowerBand > prevLowerBand or source[1] < prevLowerBand else prevLowerBand
        upperBand = upperBand if upperBand < prevUpperBand or source[1] > prevUpperBand else prevUpperBand
        direction: int = na(int)
        superTrend: Series[float] = na(float)
        prevSuperTrend = superTrend[1]
        if na(atr[1]):
            direction = 1
        elif prevSuperTrend == prevUpperBand:
            direction = -1 if source > upperBand else 1
        else:
            direction = 1 if source < lowerBand else -1
        superTrend = lowerBand if direction == -1 else upperBand
        return (superTrend, direction)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
