"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    array, bar_index, close, color, high, hl2, hlc3, hlcc4, low, math, na,
    nz, ohlc4, open, script, ta, volume
)
from pynecore.types import Color, Persistent, Series
from typing import Protocol, Any


__all__ = ['addTextIf', 'buoyancy', 'divergenceChannel', 'efficientWork', 'gradientAdvDecPro', 'ma', 'sott', 'sourceStrToFloat', 'upDnIntrabarVolumesByPolarity', 'zeroOne']


class _ProtocolBuoyancy(Protocol):
    def __call__(self, src: Series[float], targetPeriod: Series[int], maxLookback: int) -> Any: ...


class _ProtocolEfficientwork(Protocol):
    def __call__(self, length: int) -> Any: ...


class _ProtocolMa(Protocol):
    def __call__(self, type: str, src: Series[float], length: int) -> Any: ...


class _ProtocolDivergencechannel(Protocol):
    def __call__(self, divergence: Series[bool], hiSrc: Series[float], loSrc: Series[float], breachHiSrc: Series[float], breachLoSrc: Series[float]) -> Any: ...


class _ProtocolSourcestrtofloat(Protocol):
    def __call__(self, srcString: Series[str]) -> Any: ...


class _ProtocolSott(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolZeroone(Protocol):
    def __call__(self, cond: bool) -> Any: ...


class _ProtocolAddtextif(Protocol):
    def __call__(self, cond: bool, msg: str, txt: str, sep: str) -> Any: ...


class _ProtocolGradientadvdecpro(Protocol):
    def __call__(self, source: float, center: float, steps: float, bearWeakColor: Color, bearStrongColor: Color, bullWeakColor: Color, bullStrongColor: Color) -> Any: ...


class _ProtocolUpdnintrabarvolumesbypolarity(Protocol):
    def __call__(self, ) -> Any: ...


buoyancy: _ProtocolBuoyancy = Exported()
efficientWork: _ProtocolEfficientwork = Exported()
ma: _ProtocolMa = Exported()
divergenceChannel: _ProtocolDivergencechannel = Exported()
sourceStrToFloat: _ProtocolSourcestrtofloat = Exported()
sott: _ProtocolSott = Exported()
zeroOne: _ProtocolZeroone = Exported()
addTextIf: _ProtocolAddtextif = Exported()
gradientAdvDecPro: _ProtocolGradientadvdecpro = Exported()
upDnIntrabarVolumesByPolarity: _ProtocolUpdnintrabarvolumesbypolarity = Exported()


@script.library('ta', na_bool=True)
def main():
    @export
    def buoyancy(src: Series[float], targetPeriod: Series[int], maxLookback: int):
        barUp: Series[bool] = ta.rising(close, 1)
        barDn: Series[bool] = ta.falling(close, 1)
        targetSum: float = math.sum(nz(src), targetPeriod)
        slotUp: float = 0.0
        slotDn: float = 0.0
        barOffsetsUp: list[int] = array.new_int(0)
        barOffsetsDn: list[int] = array.new_int(0)
        targetFound: bool = False
        overrun: bool = False
        bar: int = 0
        while bar <= maxLookback and (not (targetFound or overrun)):
            if barUp[bar] and slotUp < targetSum:
                slotUp = slotUp + nz(src[bar])
                array.push(barOffsetsUp, bar)
            elif barDn[bar] and slotDn < targetSum:
                slotDn = slotDn + nz(src[bar])
                array.push(barOffsetsDn, bar)
            overrun = bar >= bar_index
            targetFound = slotUp >= targetSum and slotDn >= targetSum
            bar = bar + 1
        delta: float = array.avg(barOffsetsDn) - array.avg(barOffsetsUp)
        barsAnalyzed: int = bar - 1
        result: float = 0.0 if not targetFound else nz(delta / barsAnalyzed)
        return result

    @export
    def efficientWork(length: int):
        workUp: float = high - math.min(open, nz(close[1], close))
        workDn: float = math.max(open, nz(close[1])) - low
        work: float = workUp + workDn
        ew: float = nz((close - nz(close[1], open)) / work)
        result: float = ta.alma(ew, length, 0.85, 6)
        return result

    MA01: str = 'Simple MA'
    MA02: str = 'Exponential MA'
    MA03: str = 'Wilder MA'
    MA04: str = 'Weighted MA'
    MA05: str = 'Volume-weighted MA'
    MA06: str = 'Arnaud Legoux MA'
    MA07: str = 'Hull MA'
    MA08: str = 'Symmetrically-weighted MA'
    @export
    def ma(type: str, src: Series[float], length: int):
        __block_result__ = na
        __switch__ = type
        if __switch__ == MA01:
            __block_result__ = ta.sma(src, length)
        elif __switch__ == MA02:
            __block_result__ = ta.ema(src, length)
        elif __switch__ == MA03:
            __block_result__ = ta.rma(src, length)
        elif __switch__ == MA04:
            __block_result__ = ta.wma(src, length)
        elif __switch__ == MA05:
            __block_result__ = ta.vwma(src, length)
        elif __switch__ == MA06:
            __block_result__ = ta.alma(src, length, 0.85, 6)
        elif __switch__ == MA07:
            __block_result__ = ta.hma(src, length)
        elif __switch__ == MA08:
            __block_result__ = ta.swma(src)
        else:
            __block_result__ = na
        result: float = __block_result__
        return result

    @export
    def divergenceChannel(divergence: Series[bool], hiSrc: Series[float], loSrc: Series[float], breachHiSrc: Series[float], breachLoSrc: Series[float]):
        channelHi: Persistent[float] = na(float)
        channelLo: Persistent[float] = na(float)
        preBreachUpChanges: Persistent[int] = 0
        preBreachDnChanges: Persistent[int] = 0
        channelIsBull: bool = breachHiSrc > channelHi and (not divergence)
        channelIsBear: bool = breachLoSrc < channelLo and (not divergence)
        channelWasBreached: Persistent[bool] = False
        priceBreachesChannel: bool = not divergence and (not channelWasBreached) and (breachHiSrc > channelHi or breachLoSrc < channelLo)
        channelWasBreached = channelWasBreached or priceBreachesChannel
        newChannel: bool = False
        if divergence:
            if channelWasBreached and (not divergence[1]):
                channelHi = hiSrc
                channelLo = loSrc
                channelIsBull = False
                channelIsBear = False
                channelWasBreached = False
                newChannel = True
                preBreachUpChanges = 0
                preBreachDnChanges = 0
            else:
                channelHi = math.max(nz(channelHi, hiSrc), hiSrc)
                channelLo = math.min(nz(channelLo, loSrc), loSrc)
        levelChangeUp: int = cast_int(math.abs(math.sign(ta.change(channelHi))))
        levelChangeDn: int = cast_int(math.abs(math.sign(ta.change(channelLo))))
        if not (channelWasBreached or newChannel):
            preBreachUpChanges = preBreachUpChanges + levelChangeUp
            preBreachDnChanges = preBreachDnChanges + levelChangeDn
        return (channelHi, channelLo, channelIsBull, channelIsBear, channelWasBreached, newChannel, preBreachUpChanges, preBreachDnChanges)

    @export
    def sourceStrToFloat(srcString: Series[str]):
        __block_result_1__ = na
        __switch__ = srcString
        if __switch__ == 'open':
            __block_result_1__ = open
        elif __switch__ == 'high':
            __block_result_1__ = high
        elif __switch__ == 'low':
            __block_result_1__ = low
        elif __switch__ == 'close':
            __block_result_1__ = close
        elif __switch__ == 'hl2':
            __block_result_1__ = hl2
        elif __switch__ == 'hlc3':
            __block_result_1__ = hlc3
        elif __switch__ == 'ohlc4':
            __block_result_1__ = ohlc4
        elif __switch__ == 'hlcc4':
            __block_result_1__ = hlcc4
        elif __switch__ == 'volume':
            __block_result_1__ = volume
        result: float = __block_result_1__
        return result

    @export
    def sott():
        barUp: bool = close > open
        barDn: bool = close < open
        body: float = math.abs(close - open)
        wicks: float = high - low - body
        risingVolume: bool = ta.change(volume, 1) > 0
        rising_1 = ta.rising(body, 1)
        up: float = (1 if barUp else 0) + (1 if ta.rising(open, 1) else 0) + (1 if ta.rising(high, 1) else 0) + (1 if ta.rising(low, 1) else 0) + (1 if ta.rising(close, 1) else 0) + (1 if barUp and rising_1 else 0) + (1 if barUp and body > wicks else 0) + (2 if open > close[1] else 0) + math.max(0, efficientWork(1)) * 2 + (2 if barUp and risingVolume else 0)
        rising_2 = ta.rising(body, 1)
        dn: float = (1 if barDn else 0) + (1 if ta.falling(open, 1) else 0) + (1 if ta.falling(high, 1) else 0) + (1 if ta.falling(low, 1) else 0) + (1 if ta.falling(close, 1) else 0) + (1 if barDn and rising_2 else 0) + (1 if barDn and body > wicks else 0) + (2 if open < close[1] else 0) + math.abs(math.min(0, efficientWork(1))) * 2 + (2 if barDn and risingVolume else 0)
        weightRange: float = 11.0 if na(risingVolume) else 13.0
        result: float = (up - dn) / weightRange
        return result

    @export
    def zeroOne(cond: bool):
        result: int = 1 if cond else 0
        return result

    @export
    def addTextIf(cond: bool, msg: str, txt: str, sep: str):
        result: str = msg + (sep if msg != '' else '') + txt if cond else msg
        return result

    @export
    def gradientAdvDecPro(source: float, center: float, steps: float, bearWeakColor: Color, bearStrongColor: Color, bullWeakColor: Color, bullStrongColor: Color):
        qtyAdvDec: Persistent[float] = 0.0
        maxSteps: Persistent[float] = math.max(1, steps)
        xUp: bool = ta.crossover(source, center)
        xDn: bool = ta.crossunder(source, center)
        chg: float = ta.change(source)
        up: bool = chg > 0
        dn: bool = chg < 0
        srcBull: bool = source > center
        srcBear: bool = source < center
        qtyAdvDec = (1 if xUp else math.min(maxSteps, qtyAdvDec + 1) if up else math.max(1, qtyAdvDec - 1) if dn else qtyAdvDec) if srcBull else (1 if xDn else math.min(maxSteps, qtyAdvDec + 1) if dn else math.max(1, qtyAdvDec - 1) if up else qtyAdvDec) if srcBear else qtyAdvDec
        result: Persistent[Color] = na(Color)
        result = color.from_gradient(qtyAdvDec, 1, maxSteps, bullWeakColor, bullStrongColor) if srcBull else color.from_gradient(qtyAdvDec, 1, maxSteps, bearWeakColor, bearStrongColor) if srcBear else result
        return result

    @export
    def upDnIntrabarVolumesByPolarity():
        upVol: Series[float] = 0.0
        dnVol: Series[float] = 0.0
        if close > open:
            upVol = upVol + volume
        elif close < open:
            dnVol = dnVol - volume
        elif close > nz(close[1]):
            upVol = upVol + volume
        elif close < nz(close[1]):
            dnVol = dnVol - volume
        elif nz(upVol[1]) > 0:
            upVol = upVol + volume
        elif nz(dnVol[1]) < 0:
            dnVol = dnVol - volume
        return (upVol, dnVol)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
