"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from enum import StrEnum as Enum
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method, method_call
from pynecore.lib import close, color, high, input, math, na, plot, script, ta
from pynecore.types import Persistent, Series
from typing import Protocol, Any
import lib.jason5480.distance_ratio.v16 as dr


__all__ = ['higher_long_biased_price', 'higher_short_biased_price', 'lower_long_biased_price', 'lower_short_biased_price']


class Direction(Enum):
    below = 'BELOW'
    above = 'ABOVE'


class Bias(Enum):
    long = 'LONG'
    short = 'SHORT'


class _ProtocolHigherLongBiasedPrice(Protocol):
    def __call__(self, this: dr.DistSettings, reference: float, longBiasedAuxData: dr.AuxData, restrict: dr.RestrictSettings, bias: dr.DistSettings, custHigherPrice: float) -> Any: ...


class _ProtocolHigherShortBiasedPrice(Protocol):
    def __call__(self, this: dr.DistSettings, reference: float, shortBiasedAuxData: dr.AuxData, restrict: dr.RestrictSettings, bias: dr.DistSettings, custHigherPrice: float) -> Any: ...


class _ProtocolLowerLongBiasedPrice(Protocol):
    def __call__(self, this: dr.DistSettings, reference: float, longBiasedAuxData: dr.AuxData, restrict: dr.RestrictSettings, bias: dr.DistSettings, custLowerPrice: float) -> Any: ...


class _ProtocolLowerShortBiasedPrice(Protocol):
    def __call__(self, this: dr.DistSettings, reference: float, shortBiasedAuxData: dr.AuxData, restrict: dr.RestrictSettings, bias: dr.DistSettings, custLowerPrice: float) -> Any: ...


higher_long_biased_price: _ProtocolHigherLongBiasedPrice = Exported()
higher_short_biased_price: _ProtocolHigherShortBiasedPrice = Exported()
lower_long_biased_price: _ProtocolLowerLongBiasedPrice = Exported()
lower_short_biased_price: _ProtocolLowerShortBiasedPrice = Exported()


@script.library(title='biased_price_target')
def main(
    referencePrice: Series[float] = input.source(defval=high, title='Reference', tooltip='The price that will be used as a reference for the distance ratio calculation.', group='General'),
    direction=input.enum(defval=Direction.below, title='Direction', tooltip='Select the relative position of the distance price compared to the reference after distance calculation.', group='General'),
    __input_2__=input.float(defval=5.0, title='Risk %', minval=0.0, maxval=100.0, step=1.0, tooltip='The percentage to be used as a reference when the RR method is selected.', group='General'),
    __input_3__=input.float(defval=0.1, title='Commission %', minval=0.0, maxval=100.0, step=0.05, tooltip='Fees paid for each transaction entry and exit (percentagewise) when the PROF method is selected.', group='General'),
    baseQuantity=input.float(defval=1.0, title='Quantity', minval=0.0, step=0.05, tooltip='The base currency quantity to enter a trade.', group='General'),
    bias=input.enum(defval=Bias.long, title='Bias', tooltip='The bias you have about the market. For example if you are in a long trade and you want to exit (take profit, stop loss etc.) you have a short bias. However, if you are not onto a trade and you want to enter into a long position you have a long bias.', group='General'),
    len=input.int(defval=5, title='Length', minval=1, tooltip='The length to calculate the highest high and the lowest low.', group='General'),
    __input_7__=input.enum(defval=dr.DistMethod.perc, title='Tgt Dist Mtd', tooltip='The method to calculate the distance of the price. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV), Tick based (TICKS), Fixed Profit (PROF), Risk-Reward based (RR) or higest high / lowest low (CUST).', group='Distance'),
    __input_8__=input.float(defval=10.0, title='  Tgt Dist Mul', minval=0.1, step=0.05, tooltip='The distance multiplier to define the target price from the reference price. The multiplier will be applied to the unit price that is defeined by the distance method that is used.', group='Distance'),
    biasEnabled=input.bool(defval=True, title='Bias Dist Mtd​     ', inline='Bias Distance', group='Distance'),
    __input_10__=input.enum(defval=dr.DistMethod.atr, title='​​​​​​​​​​​​​​​​​​​​​​​​​', options=(dr.DistMethod.perc, dr.DistMethod.atr, dr.DistMethod.stdev, dr.DistMethod.ticks), tooltip='The method to calculate the bias to offset the distance of the desiered price target. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV) or Tick based (TICKS).', inline='Bias Distance', group='Distance'),
    __input_11__=input.float(defval=0.5, title='  Bias Dist Mul', step=0.5, tooltip='The bias multiplier to define the distance offset.', group='Distance'),
    minDistEnabled=input.bool(defval=False, title='', inline='Restr Distance', group='Distance'),
    maxDistEnabled=input.bool(defval=False, title='', inline='Restr Distance', group='Distance'),
    __input_14__=input.enum(defval=dr.DistMethod.perc, title='Min/Max Dist Mtd', tooltip='The method to calculate the maximum/minimum distance of the price. Percentage based (PERC), ATR based (ATR), Standard deviation based (STDEV), Tick based (TICKS), Profit based (PROF) or Risk-Reward based (RR).', inline='Restr Distance', group='Distance'),
    __input_15__=input.float(defval=1.0, title='  Min Dist Mul      ', minval=0.0, step=0.05, tooltip='Enable a minimum distance defined by this multiplier and the restrict distance method.', group='Distance'),
    __input_16__=input.float(defval=10.0, title='  Max Dist Mul    ', minval=0.0, step=0.05, tooltip='Enable a maximum distance defined by this multiplier and the restrict distance method.', group='Distance')
):
    @export
    @method
    def higher_long_biased_price(this: dr.DistSettings, reference: float, longBiasedAuxData: dr.AuxData, restrict: dr.RestrictSettings, bias: dr.DistSettings, custHigherPrice: float):
        distPrice: float = math.max(custHigherPrice - reference, 0.0) if this.distMethod == dr.DistMethod.cust else method_call('price', this, reference, longBiasedAuxData)
        distPrice = distPrice + method_call('price', bias, reference + distPrice, longBiasedAuxData) if not na(bias) else distPrice
        return reference + (method_call('restrict_price', distPrice, restrict, reference, longBiasedAuxData) if not na(restrict) else distPrice)

    @export
    @method
    def higher_short_biased_price(this: dr.DistSettings, reference: float, shortBiasedAuxData: dr.AuxData, restrict: dr.RestrictSettings, bias: dr.DistSettings, custHigherPrice: float):
        distPrice: float = math.max(custHigherPrice - reference, 0.0) if this.distMethod == dr.DistMethod.cust else method_call('price', this, reference, shortBiasedAuxData)
        distPrice = distPrice - method_call('price', bias, reference + distPrice, shortBiasedAuxData) if not na(bias) else distPrice
        return reference + (method_call('restrict_price', distPrice, restrict, reference, shortBiasedAuxData) if not na(restrict) else distPrice)

    @export
    @method
    def lower_long_biased_price(this: dr.DistSettings, reference: float, longBiasedAuxData: dr.AuxData, restrict: dr.RestrictSettings, bias: dr.DistSettings, custLowerPrice: float):
        distPrice: float = math.max(reference - custLowerPrice, 0.0) if this.distMethod == dr.DistMethod.cust else method_call('price', this, reference, longBiasedAuxData)
        distPrice = distPrice - method_call('price', bias, reference - distPrice, longBiasedAuxData) if not na(bias) else distPrice
        return reference - (method_call('restrict_price', distPrice, restrict, reference, longBiasedAuxData) if not na(restrict) else distPrice)

    @export
    @method
    def lower_short_biased_price(this: dr.DistSettings, reference: float, shortBiasedAuxData: dr.AuxData, restrict: dr.RestrictSettings, bias: dr.DistSettings, custLowerPrice: float):
        distPrice: float = math.max(reference - custLowerPrice, 0.0) if this.distMethod == dr.DistMethod.cust else method_call('price', this, reference, shortBiasedAuxData)
        distPrice = distPrice + method_call('price', bias, reference - distPrice, shortBiasedAuxData) if not na(bias) else distPrice
        return reference - (method_call('restrict_price', distPrice, restrict, reference, shortBiasedAuxData) if not na(restrict) else distPrice)


    riskRatio = __input_2__ / 100.0
    commissionRatio = __input_3__ / 100.0

    distSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=__input_7__, distMul=__input_8__, commissionRatio=commissionRatio)
    biasSettings: Persistent[dr.DistSettings] = dr.DistSettings.new(distMethod=__input_10__, distMul=__input_11__ if biasEnabled else na)
    restrict: Persistent[dr.RestrictSettings] = dr.RestrictSettings.new(restrDistMethod=__input_14__, minDistMul=__input_15__ if minDistEnabled else na, maxDistMul=__input_16__ if maxDistEnabled else na, commissionRatio=commissionRatio)

    auxData: dr.AuxData = dr.AuxData.new(atr=ta.atr(14), stdev=ta.stdev(close, 20), baseQuantity=baseQuantity, stopLossDist=referencePrice * riskRatio)
    custHigherPrice: float = ta.highest(len)
    custLowerPrice: float = ta.lowest(len)
    distPrice: float = (higher_long_biased_price(distSettings, reference=referencePrice, longBiasedAuxData=auxData, restrict=restrict, bias=biasSettings, custHigherPrice=custHigherPrice) if direction == Direction.above else lower_long_biased_price(distSettings, reference=referencePrice, longBiasedAuxData=auxData, restrict=restrict, bias=biasSettings, custLowerPrice=custLowerPrice)) if bias == Bias.long else higher_short_biased_price(distSettings, reference=referencePrice, shortBiasedAuxData=auxData, restrict=restrict, bias=biasSettings, custHigherPrice=custHigherPrice) if direction == Direction.above else lower_short_biased_price(distSettings, reference=referencePrice, shortBiasedAuxData=auxData, restrict=restrict, bias=biasSettings, custLowerPrice=custLowerPrice)

    plot(series=referencePrice, title='Reference Price', color=color.green, force_overlay=True)
    plot(series=distPrice, title='Distance Price', color=color.blue, force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
