"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, math, na, script, strategy, syminfo, ta
from pynecore.types import Label, Line, Persistent


@script.strategy("LANZ Strategy 4.0 [Backtest]", overlay=True, default_qty_type=strategy.cash, default_qty_value=100)
def main(
    swingLength=input.int(180, "Swing Length", minval=10),
    slBufferPoints=input.float(50.0, "SL Buffer (Points)", minval=0.1),
    rr=input.float(1.0, "TP Risk-Reward (RR)", minval=0.1),
    riskPercent=input.float(1.0, "Risk per Trade (%)", minval=0.1, maxval=100),
    pipValueUSD=input.float(10.0, "Pip Value in USD (1 lot)", minval=0.01)
):
    pivotHigh = ta.pivothigh(high, swingLength, swingLength)
    pivotLow = ta.pivotlow(low, swingLength, swingLength)

    lastTop: Persistent[float] = na(float)
    lastBottom: Persistent[float] = na(float)
    prevHigh: Persistent[float] = na(float)
    prevLow: Persistent[float] = na(float)
    trendDir: Persistent[int] = na(int)
    topCrossed: Persistent[bool] = False
    bottomCrossed: Persistent[bool] = False
    topWasStrong: Persistent[bool] = False
    bottomWasStrong: Persistent[bool] = False

    if not na(pivotHigh):
        prevHigh = lastTop
        lastTop = pivotHigh
        trendDir = -1 if not na(prevHigh) and pivotHigh < prevHigh else trendDir
        topWasStrong = trendDir == -1
        topCrossed = False

    if not na(pivotLow):
        prevLow = lastBottom
        lastBottom = pivotLow
        trendDir = 1 if not na(prevLow) and pivotLow > prevLow else trendDir
        bottomWasStrong = trendDir == 1
        bottomCrossed = False

    buySignal = not topCrossed and close > lastTop
    sellSignal = not bottomCrossed and close < lastBottom

    entryPriceBuy: Persistent[float] = na(float)
    entryPriceSell: Persistent[float] = na(float)
    signalTriggeredBuy: Persistent[bool] = False
    signalTriggeredSell: Persistent[bool] = False

    if strategy.opentrades == 0:
        signalTriggeredBuy = False
        signalTriggeredSell = False
        entryPriceBuy = na
        entryPriceSell = na

    if buySignal and (not signalTriggeredBuy) and (strategy.opentrades == 0):
        entryPriceBuy = close
        signalTriggeredBuy = True

    if sellSignal and (not signalTriggeredSell) and (strategy.opentrades == 0):
        entryPriceSell = close
        signalTriggeredSell = True

    pip = syminfo.mintick * 10
    buffer = slBufferPoints * pip

    sl: Persistent[float] = na(float)
    tp: Persistent[float] = na(float)
    qty: Persistent[float] = na(float)

    epLine: Persistent[Line] = na(Line)
    slLine: Persistent[Line] = na(Line)
    tpLine: Persistent[Line] = na(Line)
    epLabel: Persistent[Label] = na(Label)
    slLabel: Persistent[Label] = na(Label)
    tpLabel: Persistent[Label] = na(Label)

    if signalTriggeredBuy and strategy.opentrades == 0:
        sl = low - buffer
        tp = entryPriceBuy + (entryPriceBuy - sl) * rr
        slPips = math.abs(entryPriceBuy - sl) / pip
        riskUSD = strategy.equity * (riskPercent / 100)
        qty = riskUSD / (slPips * pipValueUSD) if slPips > 0 else na
        strategy.entry('BUY', strategy.long, qty=qty)
        strategy.exit('TP/SL BUY', from_entry='BUY', stop=sl, limit=tp)
        topCrossed = True

    if signalTriggeredSell and strategy.opentrades == 0:
        sl = high + buffer
        tp = entryPriceSell - (sl - entryPriceSell) * rr
        slPips = math.abs(entryPriceSell - sl) / pip
        riskUSD = strategy.equity * (riskPercent / 100)
        qty = riskUSD / (slPips * pipValueUSD) if slPips > 0 else na
        strategy.entry('SELL', strategy.short, qty=qty)
        strategy.exit('TP/SL SELL', from_entry='SELL', stop=sl, limit=tp)
        bottomCrossed = True


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
