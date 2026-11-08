"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, bar_index, barstate, close, color, display, fill, high,
    hl2, input, label, location, low, math, na, open, plot, plotcandle, plotchar, script, size, ta,
    yloc
)
from pynecore.types import Persistent, PersistentSeries

gColors: str = "01 · Color Scheme"
gEngine: str = "02 · Adaptive Engine"
gTrend: str = "03 · Adaptive Trend"
gBasis: str = "04 · Adaptive Basis"
gSignals: str = "05 · Signals"
gTP: str = "06 · Take Profits"
gDisplay: str = "07 · Display"


@script.indicator("Uptrick: Adaptive Volatility Trend", shorttitle="Adaptive Vol Trend", overlay=True, max_labels_count=500)
def main(
    bullColor=input.color(color.new('#00FFE5'), "Bullish Color", group=gColors),
    bearColor=input.color(color.new('#FF00B5'), "Bearish Color", group=gColors),
    signalTextBull=input.color(color.new('#000000'), "Buy Text", group=gColors),
    signalTextBear=input.color(color.new('#FFFFFF'), "Sell Text", group=gColors),
    tpColor=input.color(color.new('#FFFFFF'), "TP X Color", group=gColors),
    efficiencyLength=input.int(12, "Efficiency Length", group=gEngine),
    volatilityLength=input.int(18, "Volatility Regime Length", group=gEngine),
    adaptSmooth=input.int(3, "Adaptation Smoothing", group=gEngine),
    atrLength=input.int(10, "ATR Length", group=gTrend),
    minATRMultiplier=input.float(1.4, "Minimum ATR Multiplier", step=0.1, group=gTrend),
    maxATRMultiplier=input.float(3.0, "Maximum ATR Multiplier", step=0.1, group=gTrend),
    volatilityInfluence=input.float(0.5, "Volatility Influence", step=0.05, group=gTrend),
    efficiencyInfluence=input.float(0.85, "Efficiency Influence", step=0.05, group=gTrend),
    basisLength=input.int(8, "Basis Length", group=gBasis),
    basisFastFactor=input.float(0.4, "Fast Regime Factor", step=0.05, group=gBasis),
    basisSlowFactor=input.float(1.35, "Slow Regime Factor", step=0.05, group=gBasis),
    showSignals=input.bool(True, "Show Buy / Sell", group=gSignals),
    signalATRDistance=input.float(1.0, "Signal Trail Distance", step=0.1, group=gSignals),
    tpMode=input.string("Static", "TP Mode", options=("Off", "Static", "Dynamic", "Both"), group=gTP),
    staticTP1ATR=input.float(1.0, "TP1 ATR", inline="ST1", step=0.1, group=gTP),
    staticTP2ATR=input.float(2.5, "TP2 ATR", inline="ST2", step=0.1, group=gTP),
    staticTP3ATR=input.float(3.0, "TP3 ATR", inline="ST3", step=0.1, group=gTP),
    tpXDistanceATR=input.float(0.75, "TP X Distance", step=0.05, group=gTP, tooltip='Long TP X = high + ATR distance.\n' + 'Short TP X = low - ATR distance.'),
    rsiLength=input.int(14, "Dynamic RSI Length", group=gTP),
    rsiUpper=input.float(75, "Long Exhaustion", inline="RSI", step=1, group=gTP),
    rsiLower=input.float(25, "Short Exhaustion", inline="RSI", step=1, group=gTP),
    showStaticTPXs=input.bool(True, "Static TP Xs", group=gTP),
    showDynamicTPXs=input.bool(True, "Dynamic TP Xs", group=gTP),
    showTrendLine=input.bool(True, "Show Adaptive Trail", group=gDisplay),
    trendLineWidth=input.int(1, "Trail Width", group=gDisplay),
    trendLineTransparency=input.int(35, "Trail Transparency", group=gDisplay),
    showBasis=input.bool(False, "Show Adaptive Basis", group=gDisplay),
    basisTransparency=input.int(80, "Basis Transparency", group=gDisplay),
    showGradient=input.bool(True, "Vertical Price Gradient", group=gDisplay),
    gradientTrailTransparency=input.int(70, "Gradient At Trail", group=gDisplay),
    showCandles=input.bool(True, "Trend Candles", group=gDisplay)
):
    safeEfficiencyLength = math.max(efficiencyLength, 1)

    safeVolatilityLength = math.max(volatilityLength, 1)

    safeAdaptSmooth = math.max(adaptSmooth, 1)

    safeATRLength = math.max(atrLength, 1)

    safeBasisLength = math.max(basisLength, 1)

    safeRSILength = math.max(rsiLength, 1)

    directionalMove = math.abs(close - close[safeEfficiencyLength])

    totalMove = math.sum(math.abs(close - close[1]), safeEfficiencyLength)

    efficiency = directionalMove / totalMove if totalMove != 0 else 0.0

    atr = ta.atr(safeATRLength)

    averageATR = ta.sma(atr, safeVolatilityLength)

    volatilityRatio = atr / averageATR if averageATR != 0 else 1.0

    volExpansion = math.max(volatilityRatio - 1.0, 0.0)

    volScoreRaw = volExpansion / (1.0 + volExpansion)

    volScore = ta.ema(volScoreRaw, safeAdaptSmooth)

    inefficiency = 1.0 - efficiency

    rawRegimeScore = inefficiency * efficiencyInfluence + volScore * volatilityInfluence

    regimeScore = ta.ema(rawRegimeScore, safeAdaptSmooth)

    normalizedRegime = math.max(math.min(regimeScore, 1.0), 0.0)

    adaptiveMultiplier = minATRMultiplier + (maxATRMultiplier - minATRMultiplier) * normalizedRegime

    adaptiveBasisFactor = basisFastFactor + (basisSlowFactor - basisFastFactor) * normalizedRegime

    adaptiveBasisLength = math.max(cast_int(math.round(safeBasisLength * adaptiveBasisFactor)), 1)

    basisAlpha = 2.0 / (adaptiveBasisLength + 1.0)

    adaptiveBasis: PersistentSeries[float] = na(float)

    adaptiveBasis = hl2 if na(adaptiveBasis[1]) else adaptiveBasis[1] + basisAlpha * (hl2 - adaptiveBasis[1])

    upperBasic = adaptiveBasis + atr * adaptiveMultiplier

    lowerBasic = adaptiveBasis - atr * adaptiveMultiplier

    finalUpper: PersistentSeries[float] = na(float)
    finalLower: PersistentSeries[float] = na(float)

    finalUpper = upperBasic if na(finalUpper[1]) else upperBasic if upperBasic < finalUpper[1] or close[1] > finalUpper[1] else finalUpper[1]

    finalLower = lowerBasic if na(finalLower[1]) else lowerBasic if lowerBasic > finalLower[1] or close[1] < finalLower[1] else finalLower[1]

    trend: Persistent[int] = na(int)

    if na(trend):
        trend = 1 if close >= adaptiveBasis else -1

    previousTrend = trend

    bullFlip = barstate.isconfirmed and trend == -1 and (close > finalUpper)

    bearFlip = barstate.isconfirmed and trend == 1 and (close < finalLower)

    if barstate.isconfirmed:
        if bullFlip:
            trend = 1
        elif bearFlip:
            trend = -1

    buySignal = previousTrend == -1 and trend == 1

    sellSignal = previousTrend == 1 and trend == -1

    activeTrendLine = finalLower if trend == 1 else finalUpper

    trendColor = bullColor if trend == 1 else bearColor

    tradeDirection: Persistent[int] = 0
    signalBar: Persistent[int] = na(int)

    entryPrice: Persistent[float] = na(float)
    entryATR: Persistent[float] = na(float)

    staticTP1: Persistent[float] = na(float)
    staticTP2: Persistent[float] = na(float)
    staticTP3: Persistent[float] = na(float)

    staticTP1Hit: Persistent[bool] = False
    staticTP2Hit: Persistent[bool] = False
    staticTP3Hit: Persistent[bool] = False

    dynamicTPHit: Persistent[bool] = False
    longRSIArmed: Persistent[bool] = False
    shortRSIArmed: Persistent[bool] = False

    if buySignal:
        tradeDirection = 1
        signalBar = bar_index

        entryPrice = close
        entryATR = atr

        staticTP1 = entryPrice + entryATR * staticTP1ATR

        staticTP2 = entryPrice + entryATR * staticTP2ATR

        staticTP3 = entryPrice + entryATR * staticTP3ATR

        staticTP1Hit = False
        staticTP2Hit = False
        staticTP3Hit = False

        dynamicTPHit = False
        longRSIArmed = False
        shortRSIArmed = False

    if sellSignal:
        tradeDirection = -1
        signalBar = bar_index

        entryPrice = close
        entryATR = atr

        staticTP1 = entryPrice - entryATR * staticTP1ATR

        staticTP2 = entryPrice - entryATR * staticTP2ATR

        staticTP3 = entryPrice - entryATR * staticTP3ATR

        staticTP1Hit = False
        staticTP2Hit = False
        staticTP3Hit = False

        dynamicTPHit = False
        longRSIArmed = False
        shortRSIArmed = False

    staticEnabled = tpMode == 'Static' or tpMode == 'Both'

    canCheckTP = barstate.isconfirmed and (not na(signalBar)) and (bar_index > signalBar)

    longStaticTP1Hit = staticEnabled and canCheckTP and (tradeDirection == 1) and (not staticTP1Hit) and (high >= staticTP1)

    longStaticTP2Hit = staticEnabled and canCheckTP and (tradeDirection == 1) and (not staticTP2Hit) and (high >= staticTP2)

    longStaticTP3Hit = staticEnabled and canCheckTP and (tradeDirection == 1) and (not staticTP3Hit) and (high >= staticTP3)

    shortStaticTP1Hit = staticEnabled and canCheckTP and (tradeDirection == -1) and (not staticTP1Hit) and (low <= staticTP1)

    shortStaticTP2Hit = staticEnabled and canCheckTP and (tradeDirection == -1) and (not staticTP2Hit) and (low <= staticTP2)

    shortStaticTP3Hit = staticEnabled and canCheckTP and (tradeDirection == -1) and (not staticTP3Hit) and (low <= staticTP3)

    longTPX = high + atr * tpXDistanceATR

    shortTPX = low - atr * tpXDistanceATR

    staticTP1X = longTPX if longStaticTP1Hit else shortTPX if shortStaticTP1Hit else na

    staticTP2X = longTPX if longStaticTP2Hit else shortTPX if shortStaticTP2Hit else na

    staticTP3X = longTPX if longStaticTP3Hit else shortTPX if shortStaticTP3Hit else na

    plotchar(staticTP1X if showStaticTPXs else na, 'Static TP1', char='X', location=location.absolute, color=tpColor, size=size.tiny)

    plotchar(staticTP2X if showStaticTPXs else na, 'Static TP2', char='X', location=location.absolute, color=tpColor, size=size.tiny)

    plotchar(staticTP3X if showStaticTPXs else na, 'Static TP3', char='X', location=location.absolute, color=tpColor, size=size.tiny)

    if barstate.isconfirmed:
        if longStaticTP1Hit or shortStaticTP1Hit:
            staticTP1Hit = True

        if longStaticTP2Hit or shortStaticTP2Hit:
            staticTP2Hit = True

        if longStaticTP3Hit or shortStaticTP3Hit:
            staticTP3Hit = True

    dynamicEnabled = tpMode == 'Dynamic' or tpMode == 'Both'

    rsi = ta.rsi(close, safeRSILength)

    if barstate.isconfirmed and dynamicEnabled and (not dynamicTPHit):
        if tradeDirection == 1 and rsi >= rsiUpper:
            longRSIArmed = True

        if tradeDirection == -1 and rsi <= rsiLower:
            shortRSIArmed = True

    rsiCrossDown = ta.crossunder(rsi, rsiUpper)

    rsiCrossUp = ta.crossover(rsi, rsiLower)

    longDynamicTP = dynamicEnabled and canCheckTP and (tradeDirection == 1) and longRSIArmed and (not dynamicTPHit) and rsiCrossDown

    shortDynamicTP = dynamicEnabled and canCheckTP and (tradeDirection == -1) and shortRSIArmed and (not dynamicTPHit) and rsiCrossUp

    dynamicTPX = longTPX if longDynamicTP else shortTPX if shortDynamicTP else na

    plotchar(dynamicTPX if showDynamicTPXs else na, 'Dynamic TP', char='X', location=location.absolute, color=tpColor, size=size.tiny)

    if barstate.isconfirmed and (longDynamicTP or shortDynamicTP):
        dynamicTPHit = True

    pTrend = plot(activeTrendLine if showTrendLine else na, 'Adaptive Volatility Trail', color=color.new(trendColor, trendLineTransparency), linewidth=trendLineWidth, style=plot.style_linebr)

    plot(adaptiveBasis if showBasis else na, 'Adaptive Basis', color=color.new(trendColor, basisTransparency), linewidth=1)

    pPrice = plot(close, 'Price Anchor', color=color.new(trendColor, 100), display=display.none)

    gradientTop = math.max(close, activeTrendLine)

    gradientBottom = math.min(close, activeTrendLine)

    priceAboveTrail = close >= activeTrendLine

    trailGradientColor = color.new(trendColor, gradientTrailTransparency)

    priceGradientColor = color.new(trendColor, 100)

    gradientTopColor = priceGradientColor if priceAboveTrail else trailGradientColor

    gradientBottomColor = trailGradientColor if priceAboveTrail else priceGradientColor

    fill(pTrend, pPrice, gradientTop, gradientBottom, gradientTopColor if showGradient else na, gradientBottomColor if showGradient else na, title='Adaptive Price Gradient')

    plotcandle(open if showCandles else na, high if showCandles else na, low if showCandles else na, close if showCandles else na, 'Adaptive Trend Candles', color=trendColor, wickcolor=trendColor, bordercolor=trendColor)

    buySignalAnchor = finalLower - atr * signalATRDistance

    sellSignalAnchor = finalUpper + atr * signalATRDistance

    if showSignals and buySignal:
        label.new(bar_index, buySignalAnchor, '𝓑𝓾𝔂', yloc=yloc.price, style=label.style_label_up, color=bullColor, textcolor=signalTextBull, size=size.normal)

    if showSignals and sellSignal:
        label.new(bar_index, sellSignalAnchor, '𝓢𝓮𝓵𝓵', yloc=yloc.price, style=label.style_label_down, color=bearColor, textcolor=signalTextBear, size=size.normal)

    plot(adaptiveMultiplier, 'Adaptive ATR Multiplier', display=display.data_window)

    plot(efficiency, 'Trend Efficiency', display=display.data_window)

    plot(volatilityRatio, 'Volatility Ratio', display=display.data_window)

    plot(normalizedRegime, 'Adaptive Regime Score', display=display.data_window)

    alertcondition(buySignal, 'Adaptive Volatility Buy', 'Uptrick Adaptive Volatility Trend switched bullish on {{ticker}}')

    alertcondition(sellSignal, 'Adaptive Volatility Sell', 'Uptrick Adaptive Volatility Trend switched bearish on {{ticker}}')

    alertcondition(longStaticTP1Hit or shortStaticTP1Hit, 'Static TP1', 'Static TP1 reached on {{ticker}}')

    alertcondition(longStaticTP2Hit or shortStaticTP2Hit, 'Static TP2', 'Static TP2 reached on {{ticker}}')

    alertcondition(longStaticTP3Hit or shortStaticTP3Hit, 'Static TP3', 'Static TP3 reached on {{ticker}}')

    alertcondition(longDynamicTP or shortDynamicTP, 'Dynamic RSI TP', 'Dynamic RSI target triggered on {{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)