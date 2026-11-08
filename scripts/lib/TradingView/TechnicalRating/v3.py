"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_import import shadowed_namespace
from pynecore.lib import (
    array, bar_index, barstate, chart, close, color, high, label, low, math,
    na, nz, plot, script, ta
)
from pynecore.types import Color, Label, Persistent, Series
from typing import Protocol, Any
import lib.TradingView.ta.v9 as ta__ren____lib


__all__ = ['calcRatingAll', 'countRising', 'ratingStatus']


ta__ren__ = shadowed_namespace(ta__ren____lib, ta)


class _ProtocolCalcratingall(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolCountrising(Protocol):
    def __call__(self, plot__ren__: Series[float]) -> Any: ...


class _ProtocolRatingstatus(Protocol):
    def __call__(self, ratingValue: Series[float], strongBound: Series[float] = 0.5, weakBound: Series[float] = 0.1) -> Any: ...


calcRatingAll: _ProtocolCalcratingall = Exported()
countRising: _ProtocolCountrising = Exported()
ratingStatus: _ProtocolRatingstatus = Exported()


@script.library("TechnicalRating")
def main():
    def calcRatingMA(ma: Series[float], src: Series[float]):
        return math.sign(src - ma)

    def calcRating(src, bullCond: Series[bool], bearCond: Series[bool]):
        return na if na(src) else 1 if bullCond else -1 if bearCond else 0

    @export
    def calcRatingAll():
        lead1: Series
        lead2: Series
        con, base, lead1, lead2, _ = ta__ren__.ichimoku()
        dStoch: Series
        kStoch, dStoch = ta__ren__.stochFull(14, 3, 3)
        kStochRsi, dStochRsi = ta__ren__.stochRsi(14, 14, 3, 3)
        adx: Series
        diP, diN, adx = ta__ren__.dmi(14, 14)
        macd, signal, _ = ta__ren__.macd(close, 12, 26, 9)
        bullPower: Series[float] = high - ta__ren__.ema(close, 13)
        bearPower: Series[float] = low - ta__ren__.ema(close, 13)
        rsi: Series[float] = ta__ren__.rsi(close, 14)
        cci: Series[float] = ta__ren__.cci(close, 20)
        mom: Series[float] = ta__ren__.mom(close, 10)
        priceAvg: float = ta__ren__.ema(close, 50)
        downTrend: bool = close < priceAvg
        upTrend: bool = close > priceAvg
        uo: float = ta__ren__.uo(7, 14, 28)
        wr: Series[float] = ta__ren__.wpr(14)
        ao: Series[float] = ta__ren__.ao()

        indRatings: Persistent[list[float]] = array.new_float()
        array.clear(indRatings)
        array.push(indRatings, calcRatingMA(ta__ren__.sma(close, 10), close))
        array.push(indRatings, calcRatingMA(ta__ren__.sma(close, 20), close))
        array.push(indRatings, calcRatingMA(ta__ren__.sma(close, 30), close))
        array.push(indRatings, calcRatingMA(ta__ren__.sma(close, 50), close))
        array.push(indRatings, calcRatingMA(ta__ren__.sma(close, 100), close))
        array.push(indRatings, calcRatingMA(ta__ren__.sma(close, 200), close))
        array.push(indRatings, calcRatingMA(ta__ren__.ema(close, 10), close))
        array.push(indRatings, calcRatingMA(ta__ren__.ema(close, 20), close))
        array.push(indRatings, calcRatingMA(ta__ren__.ema(close, 30), close))
        array.push(indRatings, calcRatingMA(ta__ren__.ema(close, 50), close))
        array.push(indRatings, calcRatingMA(ta__ren__.ema(close, 100), close))
        array.push(indRatings, calcRatingMA(ta__ren__.ema(close, 200), close))
        array.push(indRatings, calcRatingMA(ta__ren__.hma(close, 9), close))
        array.push(indRatings, calcRatingMA(ta__ren__.vwma(close, 20), close))
        array.push(indRatings, calcRating(lead2, lead1[26] > lead2[26] and base > lead1[26] and (con > base) and (close > con), lead1[26] < lead2[26] and base < lead1[26] and (con < base) and (close < con)))

        ratingMA: float = array.avg(indRatings)

        array.clear(indRatings)
        array.push(indRatings, calcRating(rsi[1], rsi < 30 and rsi[1] < rsi, rsi > 70 and rsi[1] > rsi))
        array.push(indRatings, calcRating(dStoch[1], kStoch < 20 and dStoch < 20 and (kStoch > dStoch), kStoch > 80 and dStoch > 80 and (kStoch < dStoch)))
        array.push(indRatings, calcRating(cci[1], cci < -100 and cci > cci[1], cci > 100 and cci < cci[1]))
        array.push(indRatings, calcRating(adx, adx > 20 and adx > adx[1] and (diP > diN), adx > 20 and adx > adx[1] and (diP < diN)))
        array.push(indRatings, calcRating(ao[1], ta__ren__.crossover(ao, 0) or (ao > 0 and ao[1] > 0 and (ao > ao[1]) and (ao[2] > ao[1])), ta__ren__.crossunder(ao, 0) or (ao < 0 and ao[1] < 0 and (ao < ao[1]) and (ao[2] < ao[1]))))
        array.push(indRatings, calcRating(mom[1], mom > mom[1], mom < mom[1]))
        array.push(indRatings, calcRating(signal, macd > signal, macd < signal))
        array.push(indRatings, calcRating(priceAvg, downTrend and kStochRsi < 20 and (dStochRsi < 20) and (kStochRsi > dStochRsi), upTrend and kStochRsi > 80 and (dStochRsi > 80) and (kStochRsi < dStochRsi)))
        array.push(indRatings, calcRating(wr[1], wr < -80 and wr > wr[1], wr > -20 and wr < wr[1]))
        array.push(indRatings, calcRating(priceAvg, upTrend and bearPower < 0 and (bearPower > bearPower[1]), downTrend and bullPower > 0 and (bullPower < bullPower[1])))
        array.push(indRatings, calcRating(uo, uo > 70, uo < 30))
        ratingOther: float = array.avg(indRatings)

        total: float = nz(ratingMA, 0) + nz(ratingOther, 0)
        __block_result__ = na
        if not na(ratingMA) and (not na(ratingOther)):
            __block_result__ = total / 2
        elif not na(ratingMA) or not na(ratingOther):
            __block_result__ = total
        else:
            __block_result__ = na
        ratingTotal: float = __block_result__

        return (ratingTotal, ratingOther, ratingMA)

    @export
    def countRising(plot__ren__: Series[float]):
        vPlot: Series[float] = math.abs(plot__ren__)
        result: Persistent[int] = 0
        __block_result_1__ = na
        if vPlot == 0:
            __block_result_1__ = 0
        elif vPlot >= vPlot[1]:
            __block_result_1__ = math.min(5, result + 1)
        elif vPlot < vPlot[1]:
            __block_result_1__ = math.max(1, result - 1)
        result = __block_result_1__
        return result

    @export
    def ratingStatus(ratingValue: Series[float], strongBound: Series[float] = 0.5, weakBound: Series[float] = 0.1):
        __block_result_2__ = na
        if na(ratingValue):
            __block_result_2__ = "-"
        elif ratingValue < -strongBound:
            __block_result_2__ = "Strong\nSell"
        elif ratingValue < -weakBound:
            __block_result_2__ = "Sell"
        elif ratingValue > strongBound:
            __block_result_2__ = "Strong\nBuy "
        elif ratingValue > weakBound:
            __block_result_2__ = "Buy"
        else:
            __block_result_2__ = "Neutral"
        return __block_result_2__

    SOFT: Color = color.new('#5B9CF6')
    ROYAL: Color = color.new('#2962FF')
    MISCHKA: Color = color.new('#A8ADBC')
    PINK: Color = color.new('#EF9A9A')
    RED: Color = color.new('#F44336')

    STRONG_BOUND: float = 0.5
    WEAK_BOUND: float = 0.1
    BAND: float = 0.2
    ZERO: float = 0.0

    ratingTotal, _, _ = calcRatingAll()

    buyColor: Color = color.from_gradient(ratingTotal, ZERO, BAND, MISCHKA, ROYAL)
    sellColor: Color = color.from_gradient(ratingTotal, -BAND, ZERO, RED, MISCHKA)
    gradColor: Color = color.from_gradient(ratingTotal, -BAND, BAND, sellColor, buyColor)

    posCond: bool = ratingTotal > WEAK_BOUND
    negCond: bool = ratingTotal < -WEAK_BOUND
    posSeries: float = ratingTotal if posCond else ZERO
    negSeries: float = ratingTotal if negCond else ZERO

    posCount: int = countRising(posSeries)
    negCount: int = countRising(negSeries)
    perc: int = posCount if posCond else negCount if negCond else 0
    curColor: Color = color.new(gradColor, 50 - perc * 10)

    plot(ratingTotal, 'Rating', curColor, 1, plot.style_columns)

    if barstate.islast:
        signal: Persistent[Label] = label.new(bar_index, 0, '', textcolor=chart.fg_color, style=label.style_label_left)
        label.set_xy(signal, bar_index + 1, ratingTotal)
        label.set_text(signal, ratingStatus(ratingTotal, STRONG_BOUND, WEAK_BOUND))
        label.set_color(signal, curColor)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
