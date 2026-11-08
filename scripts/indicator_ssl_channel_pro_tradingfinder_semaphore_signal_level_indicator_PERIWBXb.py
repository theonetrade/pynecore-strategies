"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, bar_index, barmerge, barstate, close, color, fill, high,
    input, label, location, low, math, na, nz, open, plot, plotshape, request, script, shape, size,
    string, syminfo, ta, timeframe, volume, yloc
)
from pynecore.types import PersistentSeries, Series


@script.indicator("SSL Channel Pro [TradingFinder] Semaphore Signal Level Indicator", shorttitle="SSL Pro", overlay=True, max_labels_count=500)
def main(
    maType=input.string("EMA", "MA Type", options=("SMA", "EMA", "WMA", "HMA", "RMA", "VWMA"), group="SSL Setting"),
    sslLength=input.int(10, "SSL Length", minval=1, group="SSL Setting"),
    signalProfile=input.string("Balanced", "Signal Quality", options=("Responsive", "Balanced", "Selective"), group="Signal Setting", tooltip="Responsive shows more signals. Balanced is recommended. Selective keeps only stronger setups."),
    useHTF=input.bool(False, "Enable HTF Confirmation", group="Signal Setting", inline="htf"),
    htfTimeframe=input.timeframe("60", "Higher Timeframe", group="Signal Setting", inline="htf"),
    showSignals=input.bool(True, "Show Signals", group="Signal Setting")
):
    def MA(source: float, length: int, type: str):
        __block_result__ = na
        __switch__ = type
        if __switch__ == "SMA":
            __block_result__ = ta.sma(source, length)
        elif __switch__ == "EMA":
            __block_result__ = ta.ema(source, length)
        elif __switch__ == "WMA":
            __block_result__ = ta.wma(source, length)
        elif __switch__ == "HMA":
            __block_result__ = ta.hma(source, length)
        elif __switch__ == "RMA":
            __block_result__ = ta.rma(source, length)
        elif __switch__ == "VWMA":
            __block_result__ = ta.vwma(source, length)
        else:
            __block_result__ = ta.ema(source, length)
        return __block_result__

    highMA = MA(high, sslLength, maType)
    lowMA = MA(low, sslLength, maType)

    sslState__global__: PersistentSeries[int] = 1
    sslState__global__ = 1 if close > highMA else -1 if close < lowMA else nz(sslState__global__[1], 1)

    sslLine: Series = lowMA if sslState__global__ == 1 else highMA
    flipUp = barstate.isconfirmed and sslState__global__ == 1 and (sslState__global__[1] == -1)
    flipDown = barstate.isconfirmed and sslState__global__ == -1 and (sslState__global__[1] == 1)

    rsiValue: Series = ta.rsi(close, 14)
    adxValue: Series
    plusDI, minusDI, adxValue = ta.dmi(14, 14)
    volumeMA = ta.sma(volume, 20)
    atrValue = ta.atr(14)
    channelWidth = math.abs(highMA - lowMA)
    normalizedWidth: Series = channelWidth / atrValue if atrValue > 0.0 else 0.0

    buyRSI = rsiValue > 50
    sellRSI = rsiValue < 50
    buyADX = adxValue > (18.0 if signalProfile == 'Responsive' else 25.0 if signalProfile == 'Selective' else 20.0) and plusDI > minusDI
    sellADX = adxValue > (18.0 if signalProfile == 'Responsive' else 25.0 if signalProfile == 'Selective' else 20.0) and minusDI > plusDI
    channelStrong = normalizedWidth >= (0.14 if signalProfile == 'Responsive' else 0.28 if signalProfile == 'Selective' else 0.2)

    buyConfirmations = buyRSI and buyADX and channelStrong
    sellConfirmations = sellRSI and sellADX and channelStrong

    def clamp(value: float, minimum: float, maximum: float):
        return math.min(math.max(value, minimum), maximum)

    def scale01(value: float, minimum: float, maximum: float):
        return clamp((value - minimum) / (maximum - minimum), 0.0, 1.0) if maximum > minimum else 0.0

    def grade(score: int):
        return 'A+' if score >= 90 else 'A' if score >= 80 else 'B' if score >= 70 else 'C' if score >= 60 else 'D'

    candleRange = math.max(high - low, syminfo.mintick)
    bodyRatio = math.abs(close - open) / candleRange
    buyCloseLocation = clamp((close - low) / candleRange, 0.0, 1.0)
    sellCloseLocation = clamp((high - close) / candleRange, 0.0, 1.0)
    buyBreakoutDistance = math.max(close - highMA, 0.0) / atrValue if atrValue > 0.0 else 0.0
    sellBreakoutDistance = math.max(lowMA - close, 0.0) / atrValue if atrValue > 0.0 else 0.0

    buyTransitionScore = 12.0 + scale01(buyBreakoutDistance, 0.0, 0.4) * 6.0 + bodyRatio * 4.0 + buyCloseLocation * 3.0 if flipUp else 0.0
    sellTransitionScore = 12.0 + scale01(sellBreakoutDistance, 0.0, 0.4) * 6.0 + bodyRatio * 4.0 + sellCloseLocation * 3.0 if flipDown else 0.0

    buyRsiDelta = rsiValue - 50
    sellRsiDelta = 50 - rsiValue
    buyMomentumScore = scale01(buyRsiDelta, -10.0, 15.0) * 16.0 + (4.0 if rsiValue > rsiValue[1] else 0.0)
    sellMomentumScore = scale01(sellRsiDelta, -10.0, 15.0) * 16.0 + (4.0 if rsiValue < rsiValue[1] else 0.0)

    diTotal = math.max(plusDI + minusDI, 0.0001)
    buyDiDominance = clamp((plusDI - minusDI) / diTotal, 0.0, 1.0)
    sellDiDominance = clamp((minusDI - plusDI) / diTotal, 0.0, 1.0)
    buyTrendScore = 6.0 + scale01(adxValue, 18.0 if signalProfile == 'Responsive' else 25.0 if signalProfile == 'Selective' else 20.0, 18.0 if signalProfile == 'Responsive' else 25.0 if signalProfile == 'Selective' else 20.0 + 25.0) * 8.0 + buyDiDominance * 4.0 + (2.0 if adxValue > adxValue[1] else 0.0) if plusDI > minusDI else 0.0
    sellTrendScore = 6.0 + scale01(adxValue, 18.0 if signalProfile == 'Responsive' else 25.0 if signalProfile == 'Selective' else 20.0, 18.0 if signalProfile == 'Responsive' else 25.0 if signalProfile == 'Selective' else 20.0 + 25.0) * 8.0 + sellDiDominance * 4.0 + (2.0 if adxValue > adxValue[1] else 0.0) if minusDI > plusDI else 0.0

    weakRegimeScore = 0.14 if signalProfile == 'Responsive' else 0.28 if signalProfile == 'Selective' else scale01(normalizedWidth, 0.0, 0.14 if signalProfile == 'Responsive' else 0.28 if signalProfile == 'Selective' else 0.2) * 8.0 if 0.2 > 0.0 else 8.0
    strongRegimeScore = 8.0 + scale01(normalizedWidth, 0.14 if signalProfile == 'Responsive' else 0.28 if signalProfile == 'Selective' else 0.2, 0.14 if signalProfile == 'Responsive' else 0.28 if signalProfile == 'Selective' else 0.2 + math.max(0.14 if signalProfile == 'Responsive' else 0.28 if signalProfile == 'Selective' else 0.2 * 1.5, 0.25)) * 4.0 + (3.0 if normalizedWidth > normalizedWidth[1] else 0.0)
    regimeScore = strongRegimeScore if channelStrong else weakRegimeScore

    relativeVolume = volume / volumeMA if not na(volume) and (not na(volumeMA)) and (volumeMA > 0.0) else na
    participationScore = 5.0 if na(relativeVolume) else scale01(relativeVolume, 0.7, 1.7) * 10.0

    buyOpposingWick = (high - math.max(open, close)) / candleRange
    sellOpposingWick = (math.min(open, close) - low) / candleRange
    sslExtension = math.abs(close - sslLine) / atrValue if atrValue > 0.0 else 0.0
    buyRiskPenalty = buyOpposingWick * 4.0 + scale01(sslExtension, 1.75, 3.5) * 6.0
    sellRiskPenalty = sellOpposingWick * 4.0 + scale01(sslExtension, 1.75, 3.5) * 6.0

    def sslState(length: int, type: str):
        highMA = MA(high, length, type)
        lowMA = MA(low, length, type)
        state: PersistentSeries[int] = 1
        state = 1 if close > highMA else -1 if close < lowMA else nz(state[1], 1)
        return state

    htfValid = timeframe.in_seconds(htfTimeframe) > timeframe.in_seconds()

    htfState: int = request.security(syminfo.tickerid, htfTimeframe, inline_series(sslState(sslLength, maType), 1), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    buyHTFConfirmed = not useHTF or (htfValid and htfState == 1)
    sellHTFConfirmed = not useHTF or (htfValid and htfState == -1)

    buyLocalContext = (5.0 if sslLine > sslLine[1] else 0.0) + scale01(math.max(close - sslLine, 0.0) / atrValue if atrValue > 0.0 else 0.0, 0.0, 1.0) * 5.0
    sellLocalContext = (5.0 if sslLine < sslLine[1] else 0.0) + scale01(math.max(sslLine - close, 0.0) / atrValue if atrValue > 0.0 else 0.0, 0.0, 1.0) * 5.0
    buyContextScore = (10.0 if htfValid and htfState == 1 else 0.0) if useHTF else buyLocalContext
    sellContextScore = (10.0 if htfValid and htfState == -1 else 0.0) if useHTF else sellLocalContext

    buyRawScore = buyTransitionScore + buyMomentumScore + buyTrendScore + regimeScore + participationScore + buyContextScore - buyRiskPenalty
    sellRawScore = sellTransitionScore + sellMomentumScore + sellTrendScore + regimeScore + participationScore + sellContextScore - sellRiskPenalty
    buyScore = cast_int(math.round(clamp(buyRawScore, 0.0, 100.0)))
    sellScore = cast_int(math.round(clamp(sellRawScore, 0.0, 100.0)))
    bullishLiveRaw = buyMomentumScore + buyTrendScore + regimeScore + participationScore + buyContextScore - buyRiskPenalty
    bearishLiveRaw = sellMomentumScore + sellTrendScore + regimeScore + participationScore + sellContextScore - sellRiskPenalty
    currentQuality = cast_int(math.round(clamp((bullishLiveRaw if sslState__global__ == 1 else bearishLiveRaw) / 75.0 * 100.0, 0.0, 100.0)))

    buySignal = flipUp and buyConfirmations and buyHTFConfirmed and (buyScore >= (65 if signalProfile == 'Responsive' else 80 if signalProfile == 'Selective' else 70))
    sellSignal = flipDown and sellConfirmations and sellHTFConfirmed and (sellScore >= (65 if signalProfile == 'Responsive' else 80 if signalProfile == 'Selective' else 70))

    htfAligned: Series = useHTF and htfValid and (sslState__global__ == htfState)
    newHTFAlignment = barstate.isconfirmed and htfAligned and (not htfAligned[1])
    trendWeakening = barstate.isconfirmed and (ta.crossunder(normalizedWidth, 0.14 if signalProfile == 'Responsive' else 0.28 if signalProfile == 'Selective' else 0.2) or ta.crossunder(adxValue, 18.0 if signalProfile == 'Responsive' else 25.0 if signalProfile == 'Selective' else 20.0))

    stateColor = color.new('#00D5FF') if sslState__global__ == 1 else color.new('#FF477E')
    boundaryColor = color.from_gradient(math.min(normalizedWidth, 1.0), 0.0, 1.0, color.new(color.new('#765CF6'), 58), color.new(stateColor, 12))
    strongTransparency = math.max(82 - 18, 0)
    softTransparency = math.min(82 + 14, 100)
    gradientTop = color.new(color.new('#FF477E'), strongTransparency) if sslState__global__ == -1 else color.new(color.new('#765CF6'), softTransparency)
    gradientBottom = color.new(color.new('#00D5FF'), strongTransparency) if sslState__global__ == 1 else color.new(color.new('#765CF6'), softTransparency)
    trendTransition = not na(sslState__global__[1]) and sslState__global__ != sslState__global__[1]
    visualSSL = na if trendTransition else sslLine
    visualHighMA = na if trendTransition else highMA
    visualLowMA = na if trendTransition else lowMA

    plot(visualSSL, 'SSL Line', color=stateColor, linewidth=2, style=plot.style_linebr)
    plot(visualHighMA, 'High Boundary Glow', color=color.new(boundaryColor, 88), linewidth=5, style=plot.style_linebr)
    plot(visualLowMA, 'Low Boundary Glow', color=color.new(boundaryColor, 88), linewidth=5, style=plot.style_linebr)
    highPlot = plot(visualHighMA, 'High MA', color=color.new(boundaryColor, 12), linewidth=1, style=plot.style_linebr)
    lowPlot = plot(visualLowMA, 'Low MA', color=color.new(boundaryColor, 12), linewidth=1, style=plot.style_linebr)

    fill(highPlot, lowPlot, visualHighMA, visualLowMA, gradientTop, gradientBottom, title='SSL Native Gradient')

    buyMarkerY = low - atrValue * 1.05
    sellMarkerY = high + atrValue * 1.05
    buyLabelY = low - atrValue * (1.05 + 0.25)
    sellLabelY = high + atrValue * (1.05 + 0.25)

    plotshape(buyMarkerY if showSignals and buySignal else na, title='BUY Marker', style=shape.triangleup, location=location.absolute, color=color.new('#00D5FF'), size=size.small)
    plotshape(sellMarkerY if showSignals and sellSignal else na, title='SELL Marker', style=shape.triangledown, location=location.absolute, color=color.new('#FF477E'), size=size.small)

    if showSignals and buySignal:
        label.new(bar_index, buyLabelY, 'BUY  •  ' + grade(buyScore) + '  •  ' + string.tostring(buyScore) + '%', yloc=yloc.price, style=label.style_label_up, color=color.new(color.new('#00D5FF'), 8), textcolor=color.new('#06131A'), size=size.small)

    if showSignals and sellSignal:
        label.new(bar_index, sellLabelY, 'SELL  •  ' + grade(sellScore) + '  •  ' + string.tostring(sellScore) + '%', yloc=yloc.price, style=label.style_label_down, color=color.new(color.new('#FF477E'), 8), textcolor=color.white, size=size.small)

    alertcondition(flipUp, 'SSL Trend Flip Up', '{{ticker}} | {{interval}} | SSL Trend Flip Up | Confidence: {{plot("Trend Confidence")}}%')
    alertcondition(flipDown, 'SSL Trend Flip Down', '{{ticker}} | {{interval}} | SSL Trend Flip Down | Confidence: {{plot("Trend Confidence")}}%')
    alertcondition(buySignal, 'Confirmed BUY Signal', '{{ticker}} | {{interval}} | Confirmed BUY | Confidence: {{plot("Buy Score")}}%')
    alertcondition(sellSignal, 'Confirmed SELL Signal', '{{ticker}} | {{interval}} | Confirmed SELL | Confidence: {{plot("Sell Score")}}%')
    alertcondition(newHTFAlignment, 'HTF Alignment', '{{ticker}} | {{interval}} | HTF Alignment | Confidence: {{plot("Trend Confidence")}}%')
    alertcondition(trendWeakening, 'Trend Weakening', '{{ticker}} | {{interval}} | Trend Weakening | Confidence: {{plot("Trend Confidence")}}%')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)