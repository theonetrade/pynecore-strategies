"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, close, color, fill, high, input, low, math, na, plot, script,
    strategy, ta, volume
)
from pynecore.types import Persistent, PersistentSeries, Series


@script.strategy('YinYang RSI Volume Trend Strategy', shorttitle='YinYang RSVT Strategy', overlay=True, initial_capital=1000000, default_qty_type=strategy.cash, default_qty_value=1000000, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    len=input.int(80, 'Trend Length:', tooltip='How far back should we span this indicator?\nThis length effects all lengths of the indicator'),
    purchaseSrc: Series[float] = input.source(close, 'Purchase Source (Long and Short):', tooltip='What source needs to exit the purchase zone for a purchase to happen?'),
    exitSrc: Series[float] = input.source(close, 'Exit Source (Long and Short):', tooltip='What source needs to hit a exit condition to stop the trade (Take profit, Stop Loss or hitting the other sides Purchase Zone)?'),
    useTakeProfit=input.bool(True, 'Use Take Profit', tooltip='Should we take profit IF we cross the basis line and then cross it AGAIN?'),
    useStopLoss=input.bool(True, 'Use Stop Loss', tooltip='Stop loss will ensure you don\'t lose too much if its a bad call'),
    stopLossMult=input.float(0.1, 'Stoploss Multiplier %:', tooltip='How far from the purchase lines should the stop loss be'),
    resetCondition=input.string('Entry', 'Reset Purchase Availability After:', options=('Entry', 'Stop Loss', 'None'), tooltip='If we reset after a condition is hit, this means we can purchase again when the purchase condition is met. \n' + 'Otherwise, we will only purchase after an opposite signal has appeared.\n' + 'Entry: means when the close enters the purchase zone (buy or sell).\n' + 'Stop Loss: means when the close hits the stop loss location (even when were out of a trade)\n' + "This allows us to get more trades and also if our stop loss initally was hit but it WAS a good time to purchase, we don't lose that chance.")
):
    longStart: Persistent[bool] = na(bool)
    longAvailable: PersistentSeries[bool] = na(bool)
    longTakeProfitAvailable: PersistentSeries[bool] = na(bool)
    longStopLoss: Persistent[bool] = na(bool)
    shortStart: Persistent[bool] = na(bool)
    shortAvailable: PersistentSeries[bool] = na(bool)
    shortTakeProfitAvailable: PersistentSeries[bool] = na(bool)
    shortStopLoss: Persistent[bool] = na(bool)
    resetAfterStopLoss = resetCondition == 'Stop Loss'
    resetAfterEntry = resetCondition == 'Entry'
    midHigh = ta.vwma(ta.highest(high, len), len)
    midLow = ta.vwma(ta.lowest(low, len), len)
    mid = math.avg(midHigh, midLow)
    midSmoothed = ta.ema(mid, len)
    avgVol = ta.vwma(volume, len)
    volDiff = volume / avgVol
    midVolSmoothed = ta.vwma(midSmoothed * volDiff, 3)
    midDifference = ta.sma(midHigh - midLow, len)
    midRSI = ta.rsi(midVolSmoothed, len) * 0.01
    midAdd = midRSI * midDifference
    purchaseZoneHigh = midSmoothed + midAdd
    purchaseZoneLow = midSmoothed - midAdd
    purchaseZoneBasis = math.avg(purchaseZoneHigh, purchaseZoneLow)
    stopLossHigh = purchaseZoneHigh * (1 + stopLossMult * 0.01)
    stopLossLow = purchaseZoneLow * (1 - stopLossMult * 0.01)
    longEntry = ta.crossunder(purchaseSrc, purchaseZoneLow)
    longStart = ta.crossover(purchaseSrc, purchaseZoneLow) and longAvailable
    longAvailable = True if ta.crossunder(purchaseSrc, purchaseZoneHigh) or (resetAfterStopLoss and longStopLoss) or (resetAfterEntry and longEntry) else False if longStart else longAvailable[1]
    longEnd = ta.crossover(exitSrc, purchaseZoneHigh)
    longStopLoss = ta.crossunder(exitSrc, stopLossLow)
    longTakeProfitAvailable = True if ta.crossover(exitSrc, purchaseZoneBasis) else False if longEnd else longTakeProfitAvailable[1]
    longTakeProfit = ta.crossunder(exitSrc, purchaseZoneBasis) and longTakeProfitAvailable
    shortEntry = ta.crossover(purchaseSrc, purchaseZoneHigh)
    shortStart = ta.crossunder(purchaseSrc, purchaseZoneHigh) and shortAvailable
    shortAvailable = True if ta.crossover(purchaseSrc, purchaseZoneLow) or (resetAfterStopLoss and shortStopLoss) or (resetAfterEntry and shortEntry) else False if shortStart else shortAvailable[1]
    shortEnd = ta.crossunder(exitSrc, purchaseZoneLow)
    shortStopLoss = ta.crossover(exitSrc, stopLossHigh)
    shortTakeProfitAvailable = True if ta.crossunder(exitSrc, purchaseZoneBasis) else False if shortEnd else shortTakeProfitAvailable[1]
    shortTakeProfit = ta.crossover(exitSrc, purchaseZoneBasis) and shortTakeProfitAvailable
    shortLine = plot(purchaseZoneHigh, color=color.green)
    shortStopLossLine = plot(stopLossHigh, color=color.green)
    fill(shortLine, shortStopLossLine, color=color.new(color.green, 90))
    plot(purchaseZoneBasis, color=color.white)
    longLine = plot(purchaseZoneLow, color=color.red)
    longStopLossLine = plot(stopLossLow, color=color.red)
    fill(longLine, longStopLossLine, color=color.new(color.red, 90))
    if longStart:
        strategy.entry('buy', strategy.long)
    elif longEnd or (useStopLoss and longStopLoss) or (useTakeProfit and longTakeProfit):
        strategy.close('buy')
    if shortStart:
        strategy.entry('sell', strategy.short)
    elif shortEnd or (useStopLoss and shortStopLoss) or (useTakeProfit and shortTakeProfit):
        strategy.close('sell')
    if longStart or longEnd or (useStopLoss and longStopLoss) or (useTakeProfit and longTakeProfit) or shortStart or shortEnd or (useStopLoss and shortStopLoss) or (useTakeProfit and shortTakeProfit):
        alert('{{strategy.order.action}} | {{ticker}} | {{close}}', alert.freq_once_per_bar)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
