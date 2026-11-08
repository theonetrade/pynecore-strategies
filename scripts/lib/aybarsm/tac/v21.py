"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore import pine_range
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import array, bar_index, close, high, low, math, na, open, script, ta, time
from pynecore.types import NA, Persistent, Series
from typing import Protocol, Any
import lib.aybarsm.ToolsFluent.v6 as ToolsFluent


__all__ = ['BWFractal', 'BWFractals', 'eval', 'sar']


@udt
class BWFractal:
    price: float = na(float)
    when: int = na(int)
    index: int = na(int)
    markWhen: int = _dataclass_field(default_factory=lambda: time)
    markIndex: int = _dataclass_field(default_factory=lambda: bar_index)
    boPrice: float = na(float)
    boTime: int = na(int)
    boIndex: int = na(int)


@udt
class BWFractals:
    bar: ToolsFluent.Fluent = na(ToolsFluent.Fluent)
    hh: 'list[BWFractal]' = na(list)
    lh: 'list[BWFractal]' = na(list)
    hl: 'list[BWFractal]' = na(list)
    ll: 'list[BWFractal]' = na(list)


class _ProtocolSar(Protocol):
    def __call__(self, start: float, inc: float, max: float) -> Any: ...


class _ProtocolEval(Protocol):
    def __call__(self, this: BWFractals, srcHigh: float = high, srcLow: float = low, hhBoLb: int = 0, llBoLb: int = 0, hhBoLbStart: int = time, llBoLbStart: int = time) -> Any: ...


sar: _ProtocolSar = Exported()
eval: _ProtocolEval = Exported()


@script.library('tac', overlay=False)
def main():
    @export
    def sar(start: float, inc: float, max: float):
        result: Persistent[float] = na(float)
        lagging: Persistent[float] = na(float)
        fast: Persistent[float] = na(float)
        maxMin: Persistent[float] = na(float)
        acceleration: Persistent[float] = na(float)
        isBelow: Persistent[bool] = False
        isFirstTrendBar: bool = False
        stages: list[float] = array.new_float()

        if bar_index == 1:
            if close > close[1]:
                isBelow = True
                maxMin = high
                result = low[1]
            else:
                isBelow = False
                maxMin = low
                result = high[1]
            isFirstTrendBar = True
            acceleration = start

        result = result + acceleration * (maxMin - result)
        array.push(stages, result)

        if isBelow:
            if result > low:
                isFirstTrendBar = True
                isBelow = False
                result = math.max(high, maxMin)
                maxMin = low
                acceleration = start
        else:
            if result < high:
                isFirstTrendBar = True
                isBelow = True
                result = math.min(low, maxMin)
                maxMin = high
                acceleration = start

        array.push(stages, result)

        if not isFirstTrendBar:
            if isBelow:
                if high > maxMin:
                    maxMin = high
                    acceleration = math.min(acceleration + inc, max)
            else:
                if low < maxMin:
                    maxMin = low
                    acceleration = math.min(acceleration + inc, max)

        if isBelow:
            result = math.min(result, low[1])
            if bar_index > 1:
                result = math.min(result, low[2])
        else:
            result = math.max(result, high[1])
            if bar_index > 1:
                result = math.max(result, high[2])

        array.push(stages, result)

        lagging = array.get(stages, 0) if bar_index > 1 and isFirstTrendBar else array.get(stages, 2)
        fast = lagging + acceleration * (maxMin - lagging) if not na(lagging) else na

        return (result, lagging, fast)

    def isFracHighBW(srcHigh: Series[float] = high):
        return srcHigh[4] < srcHigh[2] and srcHigh[3] <= srcHigh[2] and (srcHigh[2] >= srcHigh[1]) and (srcHigh[2] > srcHigh)

    def isFracLowBW(srcLow: Series[float] = low):
        return srcLow[4] > srcLow[2] and srcLow[3] >= srcLow[2] and (srcLow[2] <= srcLow[1]) and (srcLow[2] < srcLow)

    def getFracMarkBW(srcHigh: Series[float] = high, srcLow: Series[float] = low):
        isBWHigh: bool = isFracHighBW(srcHigh)
        isBWLow: bool = isFracLowBW(srcLow)
        lastHigh: float = ta.valuewhen(isBWHigh, srcHigh[2], 1)
        lastLow: float = ta.valuewhen(isBWLow, srcLow[2], 1)

        __block_result__ = na
        if isBWHigh and srcHigh[2] > lastHigh:
            __block_result__ = 2
        elif isBWHigh and srcHigh[2] < lastHigh:
            __block_result__ = 1
        else:
            __block_result__ = 0
        highMark: int = __block_result__

        __block_result_1__ = na
        if isBWLow and srcLow[2] < lastLow:
            __block_result_1__ = -2
        elif isBWLow and srcLow[2] > lastLow:
            __block_result_1__ = -1
        else:
            __block_result_1__ = 0
        lowMark: int = __block_result_1__

        return (highMark, lowMark)



    @export
    @method
    def eval(this: BWFractals, srcHigh: Series[float] = high, srcLow: Series[float] = low, hhBoLb: int = 0, llBoLb: int = 0, hhBoLbStart: int = time, llBoLbStart: int = time):
        this.bar = ToolsFluent.Fluent.new()

        if na(this.hh):
            this.hh = array.new(0, NA(BWFractal))
        if na(this.lh):
            this.lh = array.new(0, NA(BWFractal))
        if na(this.hl):
            this.hl = array.new(0, NA(BWFractal))
        if na(this.ll):
            this.ll = array.new(0, NA(BWFractal))

        markHigh, markLow = getFracMarkBW(srcHigh, srcLow)

        method_call('set', this.bar, 'isHigh', markHigh > 0)
        method_call('set', this.bar, 'isLow', markLow < 0)
        method_call('set', this.bar, 'isHH', markHigh == 2)
        method_call('set', this.bar, 'isLH', markHigh == 1)
        method_call('set', this.bar, 'isHL', markLow == -1)
        method_call('set', this.bar, 'isLL', markLow == -2)
        method_call('set', this.bar, 'markHigh', markHigh)
        method_call('set', this.bar, 'markLow', markLow)

        if method_call('get', this.bar, 'isHigh', False) or method_call('get', this.bar, 'isLow', False):
            frac: BWFractal = BWFractal(srcHigh[2] if method_call('get', this.bar, 'isHigh', False) else srcLow[2], time[2], bar_index[2], time, bar_index)

            if method_call('get', this.bar, 'isHigh', False):
                if method_call('get', this.bar, 'isHH', False):
                    array.push(this.hh, frac)
                else:
                    array.push(this.lh, frac)

            if method_call('get', this.bar, 'isLow', False):
                if method_call('get', this.bar, 'isLL', False):
                    array.push(this.ll, frac)
                else:
                    array.push(this.hl, frac)

        if hhBoLb > 0 and array.size(this.hh) > 0:
            hhBoLbFrom: int = array.size(this.hh) - 1
            hhBoLbTo: int = 0
            hhBoTimeLimit: int = llBoLb + (1 if method_call('get', this.bar, 'isHH', False) else 0)
            hhBoTimeCounter: int = 0
            for i in pine_range(hhBoLbFrom, hhBoLbTo, 1):
                hhBoTimeCounter += 1
                fracHH: BWFractal = array.get(this.hh, i)
                if fracHH.when < hhBoLbStart and hhBoTimeCounter > hhBoTimeLimit:
                    break

                if na(fracHH.boPrice) and close[1] > open[1] and (close[1] > fracHH.price):
                    fracHH.boPrice = close[1]
                    fracHH.boTime = time[1]
                    fracHH.boIndex = bar_index[1]
                    array.insert(this.hh, i, fracHH)
                    if not method_call('get', this.bar, 'isBoHH', False):
                        method_call('set', this.bar, 'isBoHH', True)
                        method_call('set', this.bar, 'boHHPrice', fracHH.price)

        __block_result_2__ = na
        if llBoLb > 0 and array.size(this.ll) > 0:
            llBoLbFrom: int = array.size(this.ll) - 1
            llBoLbTo: int = 0
            llBoTimeLimit: int = llBoLb + (1 if method_call('get', this.bar, 'isLL', False) else 0)
            llBoTimeCounter: int = 0
            __block_result_3__ = na
            for i in pine_range(llBoLbFrom, llBoLbTo, 1):
                llBoTimeCounter += 1
                fracLL: BWFractal = array.get(this.ll, i)
                if fracLL.when < llBoLbStart and llBoTimeCounter > llBoTimeLimit:
                    break

                __block_result_4__ = na
                if na(fracLL.boPrice) and close[1] < open[1] and (close[1] < fracLL.price):
                    fracLL.boPrice = close[1]
                    fracLL.boTime = time[1]
                    fracLL.boIndex = bar_index[1]
                    array.insert(this.ll, i, fracLL)
                    __block_result_5__ = na
                    if not method_call('get', this.bar, 'isBoLL', False):
                        method_call('set', this.bar, 'isBoLL', True)
                        __block_result_5__ = method_call('set', this.bar, 'boLLPrice', fracLL.price)
                    __block_result_4__ = __block_result_5__
                __block_result_3__ = __block_result_4__
            __block_result_2__ = __block_result_3__
        return __block_result_2__


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
