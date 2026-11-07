"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, barcolor, barstate, bgcolor, close, color,
    high, input, label, location, low, na, open, plotshape, script, shape, size, strategy, string,
    ta, time, timeframe, volume
)
from pynecore.types import Label, Persistent, Series


@script.strategy("v2.0—Tristan's Multi-Indicator Reversal Strategy", overlay=True, margin_long=100, margin_short=100, default_qty_type=strategy.percent_of_equity, default_qty_value=100, pyramiding=10)
def main(
    rsiLength=input.int(14, "RSI Length", minval=1, group="RSI Settings"),
    rsiOverbought=input.float(70, "RSI Overbought", minval=50, group="RSI Settings"),
    rsiOversold=input.float(30, "RSI Oversold", maxval=50, group="RSI Settings"),
    macdFast=input.int(12, "MACD Fast Length", minval=1, group="MACD Settings"),
    macdSlow=input.int(26, "MACD Slow Length", minval=1, group="MACD Settings"),
    macdSignal=input.int(9, "MACD Signal Length", minval=1, group="MACD Settings"),
    wrLength=input.int(14, "Williams %R Length", minval=1, group="Williams %R Settings"),
    wrOverbought=input.float(-20, "Williams %R Overbought", group="Williams %R Settings"),
    wrOversold=input.float(-80, "Williams %R Oversold", group="Williams %R Settings"),
    volumeMA=input.int(20, "Volume MA Length", minval=1, group="Volume Settings"),
    volumeMultiplier=input.float(1.5, "Volume Spike Multiplier", minval=1.0, step=0.1, group="Volume Settings"),
    bbLength=input.int(20, "BB Length", minval=1, group="Bollinger Bands"),
    bbMult=input.float(2.0, "BB Std Dev", minval=0.1, step=0.1, group="Bollinger Bands"),
    divergenceLookback=input.int(5, "Divergence Lookback", minval=3, maxval=20, group="Divergence Settings"),
    minDivergenceStrength=input.float(0.5, "Min Divergence Strength", minval=0.1, step=0.1, group="Divergence Settings"),
    sessionChoice=input.string("New York", "Trading Session", options=("Asian", "London", "New York", "24/7"), group="Session Filter"),
    requireDivergence=input.bool(False, "Require Divergence", tooltip="Turn OFF for more signals", group="Signal Requirements"),
    requireVolumeConfirmation=input.bool(False, "Require Volume Spike", tooltip="Turn OFF for more signals", group="Signal Requirements"),
    requireReversalCandle=input.bool(False, "Require Reversal Candle Pattern", tooltip="Turn OFF for more signals", group="Signal Requirements"),
    minIndicatorsAligned=input.int(2, "Min Indicators Aligned", minval=2, maxval=4, tooltip="Lower number = more signals", group="Signal Requirements"),
    flipSignals=input.bool(False, "⚡ FLIP ALL SIGNALS", tooltip="ON = Completely reverses buy/sell logic. If losing, try toggling this!", group="Signal Requirements"),
    useStopLoss=input.bool(False, "Use Stop Loss", group="Risk Management"),
    stopLossPercent=input.float(2.5, "Stop Loss %", minval=0.1, step=0.1, group="Risk Management"),
    useTakeProfit=input.bool(False, "Use Take Profit", group="Risk Management"),
    takeProfitPercent=input.float(5.0, "Take Profit %", minval=0.1, step=0.1, group="Risk Management"),
    allowPyramiding=input.bool(True, "Allow Multiple Entries (Pyramiding)", tooltip="If OFF, only one position at a time", group="Risk Management"),
    pyramidingMax=input.int(10, "Max Pyramid Entries", minval=1, maxval=20, tooltip="Maximum number of entries in same direction", group="Risk Management")
):
    asianSession: str = "2000-0400"
    londonSession: str = "0300-1130"
    nySession: str = "0930-1600"

    rsi: Series = ta.rsi(close, rsiLength)

    macdLine, signalLine, macdHist = ta.macd(close, macdFast, macdSlow, macdSignal)

    wr: Series = ta.wpr(wrLength)

    vol = volume
    volMA = ta.sma(volume, volumeMA)
    volumeSpike = vol > volMA * volumeMultiplier

    bbUpper: Series
    bbLower: Series
    bbMiddle, bbUpper, bbLower = ta.bb(close, bbLength, bbMult)

    selectedSession = asianSession if sessionChoice == 'Asian' else londonSession if sessionChoice == 'London' else nySession if sessionChoice == 'New York' else '0000-2359'

    inSession = sessionChoice == '24/7' or not na(time(timeframe.period, selectedSession))
    inNYSession = inSession

    pivotHigh = ta.pivothigh(high, divergenceLookback, divergenceLookback)
    pivotLow = ta.pivotlow(low, divergenceLookback, divergenceLookback)

    rsiPivotHigh = ta.pivothigh(rsi, divergenceLookback, divergenceLookback)
    rsiPivotLow = ta.pivotlow(rsi, divergenceLookback, divergenceLookback)

    prevPriceHigh: Persistent[float] = na(float)
    prevPriceLow: Persistent[float] = na(float)
    prevRSIHigh: Persistent[float] = na(float)
    prevRSILow: Persistent[float] = na(float)
    barsFromLastHighPivot: Persistent[int] = 0
    barsFromLastLowPivot: Persistent[int] = 0

    if not na(pivotHigh):
        prevPriceHigh = pivotHigh
        barsFromLastHighPivot = 0
    else:
        barsFromLastHighPivot += 1

    if not na(pivotLow):
        prevPriceLow = pivotLow
        barsFromLastLowPivot = 0
    else:
        barsFromLastLowPivot += 1

    if not na(rsiPivotHigh):
        prevRSIHigh = rsiPivotHigh

    if not na(rsiPivotLow):
        prevRSILow = rsiPivotLow

    bullishDivergence: bool = False
    if not na(pivotLow) and (not na(prevPriceLow)) and (not na(prevRSILow)):
        priceLowerLow = low[divergenceLookback] < prevPriceLow
        rsiHigherLow = rsiPivotLow > prevRSILow
        bullishDivergence = priceLowerLow and rsiHigherLow

    bearishDivergence: bool = False
    if not na(pivotHigh) and (not na(prevPriceHigh)) and (not na(prevRSIHigh)):
        priceHigherHigh = high[divergenceLookback] > prevPriceHigh
        rsiLowerHigh = rsiPivotHigh < prevRSIHigh
        bearishDivergence = priceHigherHigh and rsiLowerHigh

    activeBullishDiv: Persistent[bool] = False
    activeBearishDiv: Persistent[bool] = False
    bullDivBars: Persistent[int] = 0
    bearDivBars: Persistent[int] = 0

    if bullishDivergence:
        activeBullishDiv = True
        bullDivBars = 0
    else:
        bullDivBars += 1
        if bullDivBars > 10:
            activeBullishDiv = False

    if bearishDivergence:
        activeBearishDiv = True
        bearDivBars = 0
    else:
        bearDivBars += 1
        if bearDivBars > 10:
            activeBearishDiv = False

    rsiOversoldSignal = rsi < rsiOversold and rsi > rsi[1]
    macdBullish = macdHist > 0 or ta.crossover(macdLine, signalLine)
    wrOversoldSignal = wr < wrOversold and wr > wr[1]
    priceBelowBB = close < bbLower or close[1] < bbLower[1]

    rsiOverboughtSignal = rsi > rsiOverbought and rsi < rsi[1]
    macdBearish = macdHist < 0 or ta.crossunder(macdLine, signalLine)
    wrOverboughtSignal = wr > wrOverbought and wr < wr[1]
    priceAboveBB = close > bbUpper or close[1] > bbUpper[1]

    bullishCount: int = 0
    if rsiOversoldSignal:
        bullishCount += 1
    if macdBullish:
        bullishCount += 1
    if wrOversoldSignal:
        bullishCount += 1
    if priceBelowBB:
        bullishCount += 1

    bearishCount: int = 0
    if rsiOverboughtSignal:
        bearishCount += 1
    if macdBearish:
        bearishCount += 1
    if wrOverboughtSignal:
        bearishCount += 1
    if priceAboveBB:
        bearishCount += 1

    bullishCandle = close > open and close - open > (high - close) * 2 and (open - low > (high - low) * 0.6)

    bearishCandle = close < open and open - close > (close - low) * 2 and (high - open > (high - low) * 0.6)

    standardBuyConditions = bullishCount >= minIndicatorsAligned and (not requireDivergence or activeBullishDiv) and (not requireVolumeConfirmation or volumeSpike) and (not requireReversalCandle or bullishCandle) and inNYSession

    standardSellConditions = bearishCount >= minIndicatorsAligned and (not requireDivergence or activeBearishDiv) and (not requireVolumeConfirmation or volumeSpike) and (not requireReversalCandle or bearishCandle) and inNYSession

    buySignal = standardSellConditions if flipSignals else standardBuyConditions
    sellSignal = standardBuyConditions if flipSignals else standardSellConditions

    buySignalConfirmed = buySignal and barstate.isconfirmed
    sellSignalConfirmed = sellSignal and barstate.isconfirmed

    longEntryCount: Persistent[int] = 0
    shortEntryCount: Persistent[int] = 0
    lastLongEntry: Persistent[float] = na(float)
    lastShortEntry: Persistent[float] = na(float)

    canEnterLong = longEntryCount < pyramidingMax if allowPyramiding else strategy.position_size <= 0
    canEnterShort = shortEntryCount < pyramidingMax if allowPyramiding else strategy.position_size >= 0

    if buySignalConfirmed and canEnterLong:
        strategy.entry('Long', strategy.long)

        if useStopLoss or useTakeProfit:
            stopPrice = close * (1 - stopLossPercent / 100) if useStopLoss else na
            targetPrice = close * (1 + takeProfitPercent / 100) if useTakeProfit else na
            strategy.exit('Exit Long', 'Long', stop=stopPrice, limit=targetPrice)

        if strategy.position_size[1] <= 0:
            longEntryCount = 1
            lastLongEntry = close
        else:
            longEntryCount += 1

    if sellSignalConfirmed and canEnterShort:
        strategy.entry('Short', strategy.short)

        if useStopLoss or useTakeProfit:
            stopPrice = close * (1 + stopLossPercent / 100) if useStopLoss else na
            targetPrice = close * (1 - takeProfitPercent / 100) if useTakeProfit else na
            strategy.exit('Exit Short', 'Short', stop=stopPrice, limit=targetPrice)

        if strategy.position_size[1] >= 0:
            shortEntryCount = 1
            lastShortEntry = close
        else:
            shortEntryCount += 1

    wasLong = strategy.position_size[1] > 0
    wasShort = strategy.position_size[1] < 0
    isFlat = strategy.position_size == 0
    justReversedToShort = wasLong and strategy.position_size < 0
    justReversedToLong = wasShort and strategy.position_size > 0

    exitedLong = wasLong and isFlat or justReversedToShort
    exitedShort = wasShort and isFlat or justReversedToLong

    displayLongExits: Persistent[int] = 0
    displayShortExits: Persistent[int] = 0

    if exitedLong:
        displayLongExits = longEntryCount
        longEntryCount = 0

    if exitedShort:
        displayShortExits = shortEntryCount
        shortEntryCount = 0

    showBullishSetups = bullishCount >= 2 and (not buySignal)
    showBearishSetups = bearishCount >= 2 and (not sellSignal)

    plotshape(buySignalConfirmed, title='Buy Signal', location=location.belowbar, color=color.new(color.lime, 0), style=shape.triangleup, size=size.large, text='BUY')
    plotshape(sellSignalConfirmed, title='Sell Signal', location=location.abovebar, color=color.new(color.red, 0), style=shape.triangledown, size=size.large, text='SELL')

    if exitedLong and barstate.isconfirmed:
        exitLongText = 'Exit Long\nx' + string.tostring(displayLongExits) if displayLongExits > 1 else 'Exit Long'
        label.new(bar_index, low, exitLongText, color=color.new(color.purple, 0), textcolor=color.white, style=label.style_label_up, size=size.small)

    if exitedShort and barstate.isconfirmed:
        exitShortText = 'Exit Short\nx' + string.tostring(displayShortExits) if displayShortExits > 1 else 'Exit Short'
        label.new(bar_index, high, exitShortText, color=color.new(color.purple, 0), textcolor=color.white, style=label.style_label_down, size=size.small)

    plotshape(showBullishSetups and inNYSession, title='Bullish Setup', location=location.belowbar, color=color.new(color.green, 50), style=shape.circle, size=size.tiny)
    plotshape(showBearishSetups and inNYSession, title='Bearish Setup', location=location.abovebar, color=color.new(color.orange, 50), style=shape.circle, size=size.tiny)

    plotshape(activeBullishDiv and barsFromLastLowPivot < 5 and barstate.isconfirmed, title='Bullish Divergence', location=location.bottom, color=color.new(color.aqua, 0), style=shape.diamond, size=size.small, text='DIV')
    plotshape(activeBearishDiv and barsFromLastHighPivot < 5 and barstate.isconfirmed, title='Bearish Divergence', location=location.top, color=color.new(color.fuchsia, 0), style=shape.diamond, size=size.small, text='DIV')

    bgcolor(color.new(color.blue, 95) if inSession else na, title='Active Trading Session')

    barcolor(color.new(color.yellow, 70) if volumeSpike else na, title='Volume Spike')

    scoreLabel: Persistent[Label] = na(Label)
    if barstate.islast:
        label.delete(scoreLabel)
        modeText = '\n(FLIPPED)' if flipSignals else '\n(STANDARD)'
        sessionText = '\nSession: ' + sessionChoice
        labelText = 'Bull: ' + string.tostring(bullishCount) + '/4\nBear: ' + string.tostring(bearishCount) + '/4' + modeText + sessionText
        labelColor = color.green if bullishCount >= minIndicatorsAligned else color.red if bearishCount >= minIndicatorsAligned else color.gray
        scoreLabel = label.new(bar_index, high, labelText, color=color.new(labelColor, 70), textcolor=color.white, style=label.style_label_down, size=size.small)

    alertcondition(buySignalConfirmed, title='Reversal Buy', message='Multi-Indicator Buy Signal - Reversal Detected!')
    alertcondition(sellSignalConfirmed, title='Reversal Sell', message='Multi-Indicator Sell Signal - Reversal Detected!')

    alertcondition(exitedLong and barstate.isconfirmed, title='Long Exit', message='Long Position Exited')
    alertcondition(exitedShort and barstate.isconfirmed, title='Short Exit', message='Short Position Exited')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)