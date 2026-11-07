"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fixnan, high, hline, input, location, low, math, na, plot,
    plotshape, script, shape, strategy, ta, time, timestamp
)
from pynecore.types import Persistent

adxGroup: str = "Trend Conditions"
emaGroup: str = "EMA Conditions"
riskGroup: str = "Risk Management"
backtestGroup: str = "Backtesting"


@script.strategy("Triple EMA Trend", overlay=False, fill_orders_on_standard_ohlc=True, default_qty_type=strategy.percent_of_equity, default_qty_value=5, commission_type=strategy.commission.percent, commission_value=0.075)
def main(
    adxLen=input.int(14, "ADX Length", group=adxGroup),
    adxThresh=input.float(43.0, "ADX Threshold", group=adxGroup),
    emaFastLen=input.int(30, "EMA Fast Length", group=emaGroup),
    emaMidLen=input.int(46, "EMA Mid Length", group=emaGroup),
    emaSlowLen=input.int(80, "EMA Slow Length", group=emaGroup),
    atrLen=input.int(14, "ATR Length", group=riskGroup),
    slMult=input.float(1.8, "Stop Loss ATR Multiplier", group=riskGroup),
    tpMult=input.float(3.3, "Take Profit ATR Multiplier", group=riskGroup),
    startDate=input.time(timestamp('01 Jan 2021 00:00 +0300'), 'Start Date', group=backtestGroup),
    endDate=input.time(timestamp('20 Jul 2030 00:00 +0300'), 'End Date', group=backtestGroup),
    enableLongs=input.bool(True, 'Go Long', group=backtestGroup),
    enableShorts=input.bool(False, 'Go Short', group=backtestGroup)
):
    def dirmov(len):
        up = ta.change(high)
        down = -ta.change(low)
        plusDM = na if na(up) else up if up > down and up > 0 else 0
        minusDM = na if na(down) else down if down > up and down > 0 else 0
        truerange = ta.rma(ta.tr, len)
        plus = fixnan(100 * ta.rma(plusDM, len) / truerange)
        minus = fixnan(100 * ta.rma(minusDM, len) / truerange)
        return (plus, minus)

    def adx(dilen, adxlen):
        plus, minus = dirmov(dilen)
        sum = plus + minus
        return 100 * ta.rma(math.abs(plus - minus) / (1 if sum == 0 else sum), adxlen)

    isLong: Persistent[bool] = False
    isShort: Persistent[bool] = False
    entryPrice: Persistent[float] = na(float)
    stoplossPrice: Persistent[float] = na(float)
    takeprofitPrice: Persistent[float] = na(float)
    stoplossHit: bool = False
    takeprofitHit: bool = False

    emaFast = ta.ema(close, emaFastLen)
    emaMid = ta.ema(close, emaMidLen)
    emaSlow = ta.ema(close, emaSlowLen)
    adx__global__ = adx(adxLen, adxLen)
    atr = ta.atr(atrLen)

    longCondition = adx__global__ > adxThresh and emaFast > emaMid and (emaMid > emaSlow) and (close > emaFast)
    shortCondition = adx__global__ > adxThresh and emaFast < emaMid and (emaMid < emaSlow) and (close < emaFast)

    entryLong = longCondition and (not (isLong or isShort))
    entryShort = shortCondition and (not (isLong or isShort))

    isLong = True if entryLong else isLong
    isShort = True if entryShort else isShort

    newTrade = entryLong or entryShort

    crossoverTP = ta.crossover(high, takeprofitPrice)
    crossunderSL = ta.crossunder(low, stoplossPrice)
    crossunderTP = ta.crossunder(low, takeprofitPrice)
    crossoverSL = ta.crossover(high, stoplossPrice)

    if newTrade:
        entryPrice = close
        if isLong:
            stoplossPrice = entryPrice - slMult * atr
            takeprofitPrice = entryPrice + tpMult * atr
        if isShort:
            stoplossPrice = entryPrice + slMult * atr
            takeprofitPrice = entryPrice - tpMult * atr
    else:
        if isLong:
            if crossoverTP:
                takeprofitHit = True
            elif crossunderSL:
                stoplossHit = True
        if isShort:
            if crossunderTP:
                takeprofitHit = True
            elif crossoverSL:
                stoplossHit = True

        if takeprofitHit or stoplossHit:
            isLong = False
            isShort = False

    if time > startDate and time < endDate:
        if entryLong and enableLongs:
            strategy.entry('Long Entry', strategy.long)
            strategy.exit('Exit Long', 'Long Entry', limit=takeprofitPrice, stop=stoplossPrice)

        if entryShort and enableShorts:
            strategy.entry('Short Entry', strategy.short)
            strategy.exit('Exit Short', 'Short Entry', limit=takeprofitPrice, stop=stoplossPrice)

    plot(adx__global__, color=color.red, title='ADX')
    hline(adxThresh, 'ADX Threshold', color.white)
    plot(emaFast, 'EMA Fast', color.blue, force_overlay=True)
    plot(emaMid, 'EMA Mid', color.white, 2, force_overlay=True)
    plot(emaSlow, 'EMA Slow', color.yellow, 3, force_overlay=True)
    plot(takeprofitPrice if isLong or isShort else na, 'TP Price', color.lime, 1, plot.style_linebr, force_overlay=True)
    plot(stoplossPrice if isLong or isShort else na, 'SL Price', color.red, 1, plot.style_linebr, force_overlay=True)
    plotshape(entryLong, 'Long Entry', shape.labelup, location.belowbar, color.lime, text='Long', textcolor=color.black, force_overlay=True)
    plotshape(entryShort, 'Short Entry', shape.labeldown, location.abovebar, color.red, text='Short', textcolor=color.white, force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
