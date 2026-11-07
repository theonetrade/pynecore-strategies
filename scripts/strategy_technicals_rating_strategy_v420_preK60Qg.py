"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barmerge, high, input, low, math, na, open, request, script, strategy,
    syminfo, ta
)
from pynecore.types import Series


@script.strategy(title='Ichi HMA RSI Stoch CCI MACD Technicals Rating Strategy', shorttitle='TRSv420', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=50, commission_type=strategy.commission.percent, commission_value=0.05, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    res=input.timeframe('', title='Indicator Timeframe'),
    Period=input.int(defval=14, title='Period Length', minval=2),
    MinSignalStrength=input.float(title='Minimum Signal Strength', defval=1.1, minval=0.0, maxval=2.0, step=0.1),
    Price: Series[float] = input(defval=open, title='Price Source'),
    Use_Only_Buy=input(False, title='Use ONLY BUY mode'),
    Use_Only_Sell=input(False, title='Use ONLY SELL mode'),
    Use_ATR_SL_TP=input(True, title='Use ATR for TP & SL'),
    Use_Ichimoku=input(True, title='Use Ichimoku'),
    Use_HMA=input(True, title='Use Hull MA'),
    Use_RSI=input(True, title='Use RSI'),
    Use_Stoch=input(True, title='Use Stoch'),
    Use_CCI=input(True, title='Use CCI'),
    Use_MACD=input(True, title='Use MacD')
):
    def donchian(len):
        return math.avg(ta.lowest(len), ta.highest(len))

    def ichimoku_cloud():
        conversionLine = donchian(9)
        baseLine = donchian(26)
        leadLine1 = math.avg(conversionLine, baseLine)
        leadLine2 = donchian(52)
        return (conversionLine, baseLine, leadLine1, leadLine2)

    IC_CLine, IC_BLine, IC_Lead1, IC_Lead2 = ichimoku_cloud()
    def calcRatingMA(ma, src):
        return na if na(ma) or na(src) else 0 if ma == src else 1 if ma < src else -1

    def calcRating(buy, sell):
        return 1 if buy else -1 if sell else 0

    def calcRatingAll():
        __hist_Price__: Series = Price[0]
        HMA10 = ta.hma(Price, Period)
        HMA20 = ta.hma(Price, 20)
        HMA30 = ta.hma(Price, 30)
        HMA50 = ta.hma(Price, 50)
        HMA100 = ta.hma(Price, 100)
        HMA200 = ta.hma(Price, 200)
        RSI = ta.rsi(Price, 14)
        lengthStoch: int = 14
        smoothKStoch: int = 3
        smoothDStoch: int = 3
        kStoch: Series = ta.sma(ta.stoch(Price, high, low, lengthStoch), smoothKStoch)
        dStoch: Series = ta.sma(kStoch, smoothDStoch)
        CCI = ta.cci(Price, 20)
        macdMACD, signalMACD, _ = ta.macd(Price, 12, 26, 9)
        PriceAvg = ta.hma(Price, Period)
        DownTrend = Price < PriceAvg
        UpTrend = Price > PriceAvg
        ratingMA: float = 0
        ratingMAC: float = 0
        if Use_HMA:
            if not na(HMA10):
                ratingMA = ratingMA + calcRatingMA(HMA10, Price)
                ratingMAC = ratingMAC + 1
            if not na(HMA20):
                ratingMA = ratingMA + calcRatingMA(HMA20, Price)
                ratingMAC = ratingMAC + 1
            if not na(HMA30):
                ratingMA = ratingMA + calcRatingMA(HMA30, Price)
                ratingMAC = ratingMAC + 1
            if not na(HMA50):
                ratingMA = ratingMA + calcRatingMA(HMA50, Price)
                ratingMAC = ratingMAC + 1
            if not na(HMA100):
                ratingMA = ratingMA + calcRatingMA(HMA100, Price)
                ratingMAC = ratingMAC + 1
            if not na(HMA200):
                ratingMA = ratingMA + calcRatingMA(HMA200, Price)
                ratingMAC = ratingMAC + 1
        if Use_Ichimoku:
            ratingIC: float = na(float)
            if not (na(IC_Lead1) or na(IC_Lead2) or na(Price) or na(__hist_Price__[1]) or na(IC_BLine) or na(IC_CLine)):
                ratingIC = calcRating(IC_Lead1 > IC_Lead2 and Price > IC_Lead1 and (Price < IC_BLine) and (__hist_Price__[1] < IC_CLine) and (Price > IC_CLine), IC_Lead2 > IC_Lead1 and Price < IC_Lead2 and (Price > IC_BLine) and (__hist_Price__[1] > IC_CLine) and (Price < IC_CLine))
            if not na(ratingIC):
                ratingMA = ratingMA + ratingIC
                ratingMAC = ratingMAC + 1
        ratingMA = ratingMA / ratingMAC if ratingMAC > 0 else na
        ratingOther: float = 0
        ratingOtherC: float = 0
        if Use_RSI:
            ratingRSI: Series = RSI
            if not (na(ratingRSI) or na(ratingRSI[1])):
                ratingOtherC = ratingOtherC + 1
                ratingOther = ratingOther + calcRating(ratingRSI < 30 and ratingRSI[1] < ratingRSI, ratingRSI > 70 and ratingRSI[1] > ratingRSI)
        if Use_Stoch:
            if not (na(kStoch) or na(dStoch) or na(kStoch[1]) or na(dStoch[1])):
                ratingOtherC = ratingOtherC + 1
                ratingOther = ratingOther + calcRating(kStoch < 20 and dStoch < 20 and (kStoch > dStoch) and (kStoch[1] < dStoch[1]), kStoch > 80 and dStoch > 80 and (kStoch < dStoch) and (kStoch[1] > dStoch[1]))
        if Use_CCI:
            ratingCCI: Series = CCI
            if not (na(ratingCCI) or na(ratingCCI[1])):
                ratingOtherC = ratingOtherC + 1
                ratingOther = ratingOther + calcRating(ratingCCI < -100 and ratingCCI > ratingCCI[1], ratingCCI > 100 and ratingCCI < ratingCCI[1])
        if Use_MACD:
            if not (na(macdMACD) or na(signalMACD)):
                ratingOtherC = ratingOtherC + 1
                ratingOther = ratingOther + calcRating(macdMACD > signalMACD, macdMACD < signalMACD)
        ratingOther = ratingOther / ratingOtherC if ratingOtherC > 0 else na
        ratingTotal: float = 0
        ratingTotalC: float = 0
        if not na(ratingMA):
            ratingTotal = ratingTotal + ratingMA
            ratingTotalC = ratingTotalC + 1
            ratingTotal = ratingTotal + ratingOther
            ratingTotalC = ratingTotalC + 1
        ratingTotal = ratingTotal / ratingTotalC if ratingTotalC > 0 else na
        return (ratingTotal, ratingOther, ratingMA, ratingOtherC, ratingMAC)

    ratingTotal, ratingOther, ratingMA, ratingOtherC, ratingMAC = request.security(syminfo.tickerid, res, calcRatingAll(), lookahead=barmerge.lookahead_off)
    tradeSignal = ratingTotal + ratingOther + ratingMA
    def dynSLpoints(factor):
        return factor * ta.atr(14) / syminfo.mintick

    if not Use_Only_Sell:
        if tradeSignal > MinSignalStrength:
            strategy.entry('long', strategy.long)
    if not Use_Only_Buy:
        if tradeSignal < -MinSignalStrength:
            strategy.entry('short', strategy.short)
    if Use_ATR_SL_TP:
        strategy.exit('sl/tp', loss=dynSLpoints(3), trail_points=dynSLpoints(5), trail_offset=dynSLpoints(2))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
