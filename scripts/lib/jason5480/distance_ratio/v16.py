"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from enum import StrEnum as Enum
from pynecore.core.overload import overload
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    close, color, high, input, math, na, plot, runtime, script, string,
    syminfo, ta
)
from pynecore.types import Persistent, Series
from typing import Protocol, Any


__all__ = ['AuxData', 'DistMethod', 'DistSettings', 'RestrictSettings', 'price', 'ratio', 'restrict_price', 'restrict_ratio', 'restrict_ticks', 'ticks', 'unit_price']


class DistMethod(Enum):
    perc = 'PERC'
    atr = 'ATR'
    stdev = 'STDEV'
    ticks = 'TICKS'
    prof = 'PROF'
    rr = 'RR'
    cust = 'CUST'


@udt
class DistSettings:
    distMethod: DistMethod = na(DistMethod)
    distMul: float = na(float)
    commissionRatio: float = na(float)


@udt
class RestrictSettings:
    restrDistMethod: DistMethod = na(DistMethod)
    minDistMul: float = na(float)
    maxDistMul: float = na(float)
    commissionRatio: float = na(float)


@udt
class AuxData:
    atr: float = na(float)
    stdev: float = na(float)
    baseQuantity: float = na(float)
    stopLossDist: float = na(float)


class Direction(Enum):
    below = 'BELOW'
    above = 'ABOVE'


class CalcMethod(Enum):
    ratio = 'RATIO'
    price = 'PRICE'
    ticks = 'TICKS'


class _ProtocolUnitPrice(Protocol):
    def __call__(self, this: DistSettings, reference: float, aux: AuxData) -> Any: ...


class _ProtocolRestrictRatio(Protocol):
    def __call__(self, this: float, restr: RestrictSettings, reference: float, aux: AuxData) -> Any: ...


class _ProtocolRestrictPrice(Protocol):
    def __call__(self, this: float, restr: RestrictSettings, reference: float, aux: AuxData) -> Any: ...


class _ProtocolRestrictTicks(Protocol):
    def __call__(self, this: int, restr: RestrictSettings, reference: float, aux: AuxData) -> Any: ...


class _ProtocolRatio(Protocol):
    def __call__(self, this: DistSettings, reference: float, aux: AuxData) -> Any: ...


class _ProtocolPrice(Protocol):
    def __call__(self, this: DistSettings, reference: float, aux: AuxData) -> Any: ...


class _ProtocolTicks(Protocol):
    def __call__(self, this: DistSettings, reference: float, aux: AuxData) -> Any: ...


unit_price: _ProtocolUnitPrice = Exported()
restrict_ratio: _ProtocolRestrictRatio = Exported()
restrict_price: _ProtocolRestrictPrice = Exported()
restrict_ticks: _ProtocolRestrictTicks = Exported()
ratio: _ProtocolRatio = Exported()
price: _ProtocolPrice = Exported()
ticks: _ProtocolTicks = Exported()


@script.library(title='distance_ratio')
def main(
    referencePrice: Series[float] = input.source(defval=high, title='Reference', tooltip='The price that will be used as a reference for the distance ratio calculation.', group='General'),
    direction=input.enum(defval=Direction.below, title='Direction', tooltip='Select the relative position of the distance price compared to the reference after distance calculation.', group='General'),
    __input_2__=input.float(defval=5.0, title='Risk %', minval=0.0, maxval=100.0, step=1.0, tooltip='The percentage to be used as a reference when the RR method is selected.', group='General'),
    __input_3__=input.float(defval=0.1, title='Commission %', minval=0.0, maxval=100.0, step=0.05, tooltip='Fees paid for each transaction entry and exit (percentagewise) when the PROF method is selected.', group='General'),
    baseQuantity=input.float(defval=1.0, title='Quantity', minval=0.0, step=0.05, tooltip='The base currency quantity to enter a trade.', group='General'),
    calcMethod=input.enum(defval=CalcMethod.ratio, title='Calc Method', tooltip='Select the target distance price calculation method it will use ratio (RATIO), or the price (PRICE) or the ticks (TICKS).', group='General'),
    __input_6__=input.enum(defval=DistMethod.perc, title='Tgt Dist Mtd', options=(DistMethod.perc, DistMethod.atr, DistMethod.stdev, DistMethod.prof, DistMethod.ticks, DistMethod.rr), tooltip='The method to calculate the distance of the price. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV), Fixed Profit (PROF), Tick based (TICKS), or Risk-Reward based (RR).', group='Distance'),
    __input_7__=input.float(defval=10.0, title='  Tgt Dist Mul', minval=0.1, step=0.05, tooltip='The distance multiplier to define the target price from the reference price. The multiplier will be applied to the unit price that is defeined by the distance method that is used.', group='Distance'),
    minDistEnabled=input.bool(defval=False, title='', inline='Restr Distance', group='Distance'),
    maxDistEnabled=input.bool(defval=False, title='', inline='Restr Distance', group='Distance'),
    __input_10__=input.enum(defval=DistMethod.perc, title='Min/Max Dist Mtd', tooltip='The method to calculate the maximum/minimum distance of the price. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV), Profit based (PROF), Tick based (TICKS) or Risk-Reward based (RR).', inline='Restr Distance', group='Distance'),
    __input_11__=input.float(defval=1.0, title='  Min Dist Mul      ', minval=0.0, step=0.05, tooltip='Enable a minimum distance defined by this multiplier and the restrict distance method.', group='Distance'),
    __input_12__=input.float(defval=10.0, title='  Max Dist Mul    ', minval=0.0, step=0.05, tooltip='Enable a maximum distance defined by this multiplier and the restrict distance method.', group='Distance')
):
    @overload
    @method
    def unit_price(distMethod: DistMethod, commissionRatio: float, reference: float, aux: AuxData):
        __block_result__ = na
        __switch__ = distMethod
        if __switch__ == DistMethod.perc:
            __block_result__ = reference / 100.0
        elif __switch__ == DistMethod.atr:
            __block_result__ = aux.atr
        elif __switch__ == DistMethod.stdev:
            __block_result__ = aux.stdev
        elif __switch__ == DistMethod.prof:
            __block_result__ = (1.0 - commissionRatio) / aux.baseQuantity
        elif __switch__ == DistMethod.ticks:
            __block_result__ = syminfo.mintick
        elif __switch__ == DistMethod.rr:
            __block_result__ = aux.stopLossDist
        else:
            runtime.error(string.tostring(distMethod) + ' is not a supported distance method. The supported methods are [PERC, ATR, STDEV, PROF, TICKS, RR]')
            __block_result__ = na
        return __block_result__

    @export
    @overload
    @method
    def unit_price(this: DistSettings, reference: float, aux: AuxData):
        return unit_price(this.distMethod, this.commissionRatio, reference, aux)

    @overload
    @method
    def unit_price(this: RestrictSettings, reference: float, aux: AuxData):
        return unit_price(this.restrDistMethod, this.commissionRatio, reference, aux)

    @method
    def min_ratio(this: RestrictSettings, reference: float, aux: AuxData):
        return this.minDistMul * unit_price(this, reference, aux) / reference

    @method
    def max_ratio(this: RestrictSettings, reference: float, aux: AuxData):
        return this.maxDistMul * unit_price(this, reference, aux) / reference

    @method
    def min_price(this: RestrictSettings, reference: float, aux: AuxData):
        return math.round_to_mintick(this.minDistMul * unit_price(this, reference, aux))

    @method
    def max_price(this: RestrictSettings, reference: float, aux: AuxData):
        return math.round_to_mintick(this.maxDistMul * unit_price(this, reference, aux))

    @method
    def min_ticks(this: RestrictSettings, reference: float, aux: AuxData):
        return math.floor(min_price(this, reference, aux) / syminfo.mintick)

    @method
    def max_ticks(this: RestrictSettings, reference: float, aux: AuxData):
        return math.floor(max_price(this, reference, aux) / syminfo.mintick)

    @export
    @method
    def restrict_ratio(this: float, restr: RestrictSettings, reference: float, aux: AuxData):
        distRatio: float = this
        distRatio = math.max(distRatio, min_ratio(restr, reference, aux)) if not na(restr.minDistMul) else distRatio
        distRatio = math.min(distRatio, max_ratio(restr, reference, aux)) if not na(restr.maxDistMul) else distRatio
        return distRatio

    @export
    @method
    def restrict_price(this: float, restr: RestrictSettings, reference: float, aux: AuxData):
        distPrice: float = this
        distPrice = math.max(distPrice, min_price(restr, reference, aux)) if not na(restr.minDistMul) else distPrice
        distPrice = math.min(distPrice, max_price(restr, reference, aux)) if not na(restr.maxDistMul) else distPrice
        return distPrice

    @export
    @method
    def restrict_ticks(this: int, restr: RestrictSettings, reference: float, aux: AuxData):
        distTicks: int = this
        distTicks = math.max(distTicks, min_ticks(restr, reference, aux)) if not na(restr.minDistMul) else distTicks
        distTicks = math.min(distTicks, max_ticks(restr, reference, aux)) if not na(restr.maxDistMul) else distTicks
        return distTicks

    @export
    @method
    def ratio(this: DistSettings, reference: float, aux: AuxData):
        __block_result_1__ = na
        __switch__ = this.distMethod
        if __switch__ == DistMethod.perc:
            __block_result_1__ = this.distMul / 100.0
        elif __switch__ == DistMethod.atr:
            __block_result_1__ = this.distMul * aux.atr / reference
        elif __switch__ == DistMethod.stdev:
            __block_result_1__ = this.distMul * aux.stdev / reference
        elif __switch__ == DistMethod.ticks:
            __block_result_1__ = cast_int(this.distMul) * syminfo.mintick / reference
        elif __switch__ == DistMethod.prof:
            if na(this.commissionRatio):
                runtime.error('PROF method needs the commission fees ratio [0, 1] to function properly')
            entryQuoteQuantity: float = reference * aux.baseQuantity
            entryQuoteCommissionFee: float = entryQuoteQuantity * this.commissionRatio
            exitQuoteCommissionFee: float = (entryQuoteQuantity + this.distMul) * this.commissionRatio * (1.0 - this.commissionRatio)
            __block_result_1__ = this.commissionRatio + (this.distMul + exitQuoteCommissionFee) / (entryQuoteQuantity - entryQuoteCommissionFee)
        elif __switch__ == DistMethod.rr:
            __block_result_1__ = this.distMul * aux.stopLossDist / reference
        else:
            runtime.error(string.tostring(this.distMethod) + ' is not a supported distance method. The supported methods are [PERC, ATR, STDEV, TICKS, PROF, RR]')
            __block_result_1__ = na
        distRatio: float = __block_result_1__
        return distRatio if not na(distRatio) else 0.0

    @export
    @method
    def price(this: DistSettings, reference: float, aux: AuxData):
        return math.round_to_mintick(reference * ratio(this, reference, aux))

    @export
    @method
    def ticks(this: DistSettings, reference: float, aux: AuxData):
        return math.floor(price(this, reference, aux) / syminfo.mintick)


    riskRatio = __input_2__ / 100.0
    commissionRatio = __input_3__ / 100.0

    distSettings: Persistent[DistSettings] = DistSettings(distMethod=__input_6__, distMul=__input_7__, commissionRatio=commissionRatio)
    restrict: Persistent[RestrictSettings] = RestrictSettings(restrDistMethod=__input_10__, minDistMul=__input_11__ if minDistEnabled else na, maxDistMul=__input_12__ if maxDistEnabled else na, commissionRatio=commissionRatio)

    auxData: AuxData = AuxData(atr=ta.atr(14), stdev=ta.stdev(close, 20), baseQuantity=baseQuantity, stopLossDist=referencePrice * riskRatio)
    __block_result_2__ = na
    __switch__ = calcMethod
    if __switch__ == CalcMethod.ratio:
        distRatio: float = restrict_ratio(ratio(distSettings, reference=referencePrice, aux=auxData), restr=restrict, reference=referencePrice, aux=auxData)
        __block_result_2__ = referencePrice * (1 + distRatio if direction == Direction.above else 1 - distRatio)
    elif __switch__ == CalcMethod.price:
        distPrice__00000066__: float = restrict_price(price(distSettings, reference=referencePrice, aux=auxData), restr=restrict, reference=referencePrice, aux=auxData)
        __block_result_2__ = referencePrice + (distPrice__00000066__ if direction == Direction.above else -distPrice__00000066__)
    elif __switch__ == CalcMethod.ticks:
        distTicks: int = restrict_ticks(ticks(distSettings, reference=referencePrice, aux=auxData), restr=restrict, reference=referencePrice, aux=auxData)
        __block_result_2__ = referencePrice + syminfo.mintick * (distTicks if direction == Direction.above else -distTicks)
    else:
        runtime.error(string.tostring(calcMethod) + ' is not a supported calculation method. The supported methods are [RATIO, PRICE, TICKS]')
        __block_result_2__ = na
    distPrice: float = __block_result_2__

    plot(series=referencePrice, title='Reference Price', color=color.green, force_overlay=True)
    plot(series=distPrice, title='Distance Price', color=color.blue, force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
