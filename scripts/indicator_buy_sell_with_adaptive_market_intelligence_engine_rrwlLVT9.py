"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, barmerge, barstate, close,
    color, extend, fill, format, high, hlc3, input, label, line, linefill, low, math, na, nz, open,
    plot, position, request, runtime, script, size, string, syminfo, ta, table, timeframe, volume,
    xloc, yloc
)
from pynecore.types import Color, Label, Line, Persistent, Series, Table

GRP_TREND: str = "01. Trend Engine"
GRP_STRUCTURE: str = "02. Structure Engine"
GRP_REGIME: str = "03. Regime Filter"
GRP_MOMENTUM: str = "04. Momentum Engine"
GRP_VOLUME: str = "05. Participation"
GRP_SIGNAL: str = "06. New Trend Signal Engine"
GRP_VISUAL: str = "07. Visual Settings"


@script.indicator("Buy-SEll with Adaptive Market Intelligence Engine", shorttitle="Adaptive Market Intelligence Engine", overlay=True, max_lines_count=500, max_labels_count=500)
def main(
    fastLen=input.int(21, "Fast EMA", minval=2, group=GRP_TREND),
    slowLen=input.int(50, "Slow EMA", minval=3, group=GRP_TREND),
    meanLen=input.int(20, "Non-Intraday Mean EMA", minval=2, group=GRP_TREND),
    useHTF=input.bool(True, "Use Higher-Timeframe Confirmation", group=GRP_TREND),
    htfTf=input.timeframe("240", "Higher Timeframe", group=GRP_TREND),
    internalSwingLen=input.int(3, "Internal Swing Length", minval=2, maxval=20, group=GRP_STRUCTURE),
    majorSwingLen=input.int(8, "Major Swing Length", minval=4, maxval=50, group=GRP_STRUCTURE),
    structureBreakBuffer=input.float(0.05, "Structure Break Buffer ATR", minval=0.0, maxval=1.0, step=0.01, group=GRP_STRUCTURE),
    retestWindow=input.int(18, "Retest Window", minval=3, maxval=100, group=GRP_STRUCTURE),
    retestToleranceATR=input.float(0.18, "Retest Tolerance ATR", minval=0.02, maxval=1.0, step=0.01, group=GRP_STRUCTURE),
    retestMaxPenetrationATR=input.float(0.4, "Maximum Retest Penetration ATR", minval=0.05, maxval=2.0, step=0.05, group=GRP_STRUCTURE),
    minimumBandStrength=input.int(58, "Minimum Structure Band Strength", minval=40, maxval=90, group=GRP_STRUCTURE),
    minimumBandLegATR=input.float(0.7, "Minimum Band Leg Size ATR", minval=0.2, maxval=5.0, step=0.05, group=GRP_STRUCTURE),
    structureBandWidthATR=input.float(0.18, "Structure Band Width ATR", minval=0.05, maxval=0.6, step=0.01, group=GRP_STRUCTURE),
    requiredStructurePairs=input.int(2, "Consecutive Structure Pairs", minval=2, maxval=5, group=GRP_STRUCTURE),
    diLen=input.int(14, "DMI Length", minval=2, group=GRP_REGIME),
    adxSmooth=input.int(14, "ADX Smoothing", minval=2, group=GRP_REGIME),
    trendAdxThreshold=input.float(22.0, "Trending ADX", minval=5.0, step=0.5, group=GRP_REGIME),
    rangeAdxThreshold=input.float(18.0, "Range ADX", minval=5.0, step=0.5, group=GRP_REGIME),
    minEmaSeparationATR=input.float(0.2, "Minimum EMA Separation / ATR", minval=0.01, maxval=2.0, step=0.01, group=GRP_REGIME),
    structureRegimeSeparationATR=input.float(0.3, "Structure Activation Separation / ATR", minval=0.01, maxval=2.0, step=0.01, group=GRP_REGIME),
    atrLen=input.int(14, "ATR Length", minval=2, group=GRP_REGIME),
    atrBaselineLen=input.int(50, "ATR Baseline", minval=10, group=GRP_REGIME),
    expansionMultiplier=input.float(1.1, "Volatility Expansion Multiplier", minval=1.0, step=0.05, group=GRP_REGIME),
    bbLen=input.int(20, "Compression Length", minval=5, group=GRP_REGIME),
    bbMult=input.float(2.0, "BB Deviation", minval=0.5, step=0.1, group=GRP_REGIME),
    bbBaselineLen=input.int(50, "Bandwidth Baseline", minval=10, group=GRP_REGIME),
    compressionMultiplier=input.float(0.75, "Compression Threshold", minval=0.3, maxval=1.0, step=0.05, group=GRP_REGIME),
    rsiLen=input.int(14, "RSI Length", minval=2, group=GRP_MOMENTUM),
    macdFast=input.int(12, "MACD Fast", minval=2, group=GRP_MOMENTUM),
    macdSlow=input.int(26, "MACD Slow", minval=3, group=GRP_MOMENTUM),
    macdSignalLen=input.int(9, "MACD Signal", minval=2, group=GRP_MOMENTUM),
    useVolume=input.bool(True, "Use Volume", group=GRP_VOLUME),
    volumeLen=input.int(20, "Volume Average", minval=2, group=GRP_VOLUME),
    volumeMultiplier=input.float(1.0, "General Volume Multiplier", minval=0.5, step=0.05, group=GRP_VOLUME),
    minimumSignalScore=input.int(86, "New Trend Minimum Score", minval=75, maxval=100, group=GRP_SIGNAL),
    minimumScoreAdvantage=input.int(25, "Minimum Bull/Bear Advantage", minval=10, maxval=60, group=GRP_SIGNAL),
    requireHTFForSignals=input.bool(True, "Require HTF Alignment", group=GRP_SIGNAL),
    requireVolumeForSignals=input.bool(True, "Require Participation", group=GRP_SIGNAL),
    signalVolumeMultiplier=input.float(1.05, "Signal Volume Multiplier", minval=0.5, maxval=3.0, step=0.05, group=GRP_SIGNAL),
    trendResetBars=input.int(6, "Trend Reset Bars", minval=2, maxval=30, group=GRP_SIGNAL),
    requireStructureAlignment=input.bool(True, "Require Major Structure Alignment", group=GRP_SIGNAL),
    requireStrongADX=input.bool(True, "Require Strong ADX / DMI", group=GRP_SIGNAL),
    showTrendRibbon=input.bool(True, "EMA Trend Ribbon", group=GRP_VISUAL),
    showMean=input.bool(True, "VWAP / Mean", group=GRP_VISUAL),
    showStructureBands=input.bool(True, "Structure Gradient Bands", group=GRP_VISUAL),
    bullishBandColor=input.color(color.lime, "Uptrend Structure Band", group=GRP_VISUAL),
    bearishBandColor=input.color(color.red, "Downtrend Structure Band", group=GRP_VISUAL),
    bandCoreTransparency=input.int(87, "Structure Band Transparency", minval=70, maxval=96, group=GRP_VISUAL),
    showInternalLabels=input.bool(False, "Internal Structure Labels", group=GRP_VISUAL),
    showBreakLabels=input.bool(True, "BOS / CHOCH Labels", group=GRP_VISUAL),
    showBreakLines=input.bool(True, "BOS / CHOCH Dashed Lines", group=GRP_VISUAL),
    showRetests=input.bool(True, "Retest Labels", group=GRP_VISUAL),
    colorCandles=input.bool(True, "Confluence Candle Coloring", group=GRP_VISUAL),
    showDashboard=input.bool(True, "Market Intelligence Dashboard", group=GRP_VISUAL),
    drawingHistoryLimit=input.int(430, "Historical Drawing Lines", minval=100, maxval=470, group=GRP_VISUAL),
    labelHistoryLimit=input.int(250, "Historical Labels", minval=50, maxval=450, group=GRP_VISUAL)
):
    def f_storeLine(ids: list[Line], lineId: Line, maxCount: int):
        array.push(ids, lineId)
        if array.size(ids) > maxCount:
            line.delete(array.shift(ids))
        return 0

    def f_storeLabel(ids: list[Label], labelId: Label, maxCount: int):
        array.push(ids, labelId)
        if array.size(ids) > maxCount:
            label.delete(array.shift(ids))
        return 0

    def f_strength(reactionATR: float, legATR: float, volumeRatio: float, htfAligned: bool):
        reactionScore: float = math.min(math.max(reactionATR, 0.0), 2.0) / 2.0 * 30.0
        legScore: float = math.min(math.max(legATR, 0.0), 4.0) / 4.0 * 25.0
        volumeScore: float = math.min(math.max(volumeRatio, 0.0), 2.0) / 2.0 * 20.0
        htfScore: float = 10.0 if htfAligned else 0.0
        total: float = 15.0 + reactionScore + legScore + volumeScore + htfScore
        return cast_int(math.round(math.min(total, 100.0)))

    def f_drawStructureBand(lineStorage: list[Line], maxLines: int, x1: int, y1: float, x2: int, y2: float, referenceATR: float, bullish: bool, strength: int, widthATR: float, bullColor: Color, bearColor: Color, coreTransparency: int):
        baseColor: Color = bullColor if bullish else bearColor

        outerTransparency: int = coreTransparency + 8

        if outerTransparency > 99:
            outerTransparency = 99

        outerFill: Color = color.from_gradient(strength, 55, 100, color.new(baseColor, 99), color.new(baseColor, outerTransparency))

        innerFill: Color = color.from_gradient(strength, 55, 100, color.new(baseColor, 96), color.new(baseColor, coreTransparency))

        outerOffset: float = referenceATR * widthATR

        innerOffset: float = outerOffset * 0.52

        outerUpper: Line = line.new(x1, y1 + outerOffset, x2, y2 + outerOffset, xloc=xloc.bar_index, extend=extend.none, color=color.new(baseColor, 100), width=1)

        outerLower: Line = line.new(x1, y1 - outerOffset, x2, y2 - outerOffset, xloc=xloc.bar_index, extend=extend.none, color=color.new(baseColor, 100), width=1)

        linefill.new(outerUpper, outerLower, outerFill)

        f_storeLine(lineStorage, outerUpper, maxLines)

        f_storeLine(lineStorage, outerLower, maxLines)

        innerUpper: Line = line.new(x1, y1 + innerOffset, x2, y2 + innerOffset, xloc=xloc.bar_index, extend=extend.none, color=color.new(baseColor, 100), width=1)

        innerLower: Line = line.new(x1, y1 - innerOffset, x2, y2 - innerOffset, xloc=xloc.bar_index, extend=extend.none, color=color.new(baseColor, 100), width=1)

        linefill.new(innerUpper, innerLower, innerFill)

        f_storeLine(lineStorage, innerUpper, maxLines)

        f_storeLine(lineStorage, innerLower, maxLines)

        return 0

    def f_freshness(age: int):
        result: str = "AGED"

        if age <= 20:
            result = "FRESH"
        elif age <= 50:
            result = "ACTIVE"

        return result

    historicalLines: Persistent[list[Line]] = array.new_line()

    historicalLabels: Persistent[list[Label]] = array.new_label()

    emaFast: float = ta.ema(close, fastLen)

    emaSlow: float = ta.ema(close, slowLen)

    bullTrend: bool = emaFast > emaSlow and close > emaFast

    bearTrend: bool = emaFast < emaSlow and close < emaFast

    if useHTF and timeframe.in_seconds(htfTf) <= timeframe.in_seconds(timeframe.period):
        runtime.error('Higher Timeframe must be greater than current chart timeframe.')

    htfClose: float = close

    htfFast: float = emaFast

    htfSlow: float = emaSlow

    if useHTF:
        htfClose = request.security(syminfo.tickerid, htfTf, close[1], lookahead=barmerge.lookahead_on)

        htfFast = request.security(syminfo.tickerid, htfTf, inline_series(ta.ema(close, fastLen), 1), lookahead=barmerge.lookahead_on)

        htfSlow = request.security(syminfo.tickerid, htfTf, inline_series(ta.ema(close, slowLen), 1), lookahead=barmerge.lookahead_on)

    htfBull: bool = htfFast > htfSlow and htfClose > htfFast

    htfBear: bool = htfFast < htfSlow and htfClose < htfFast

    sessionVWAP: float = ta.vwap(hlc3)

    meanEMA: float = ta.ema(close, meanLen)

    meanLine: float = meanEMA

    if timeframe.isintraday and (not na(sessionVWAP)):
        meanLine = sessionVWAP

    aboveMean: bool = close > meanLine

    belowMean: bool = close < meanLine

    rsi: float = ta.rsi(close, rsiLen)

    macdLine, macdSignal, macdHistogram = ta.macd(close, macdFast, macdSlow, macdSignalLen)

    bullRSI: bool = rsi > 52

    bearRSI: bool = rsi < 48

    bullMACD: bool = macdHistogram > 0

    bearMACD: bool = macdHistogram < 0

    atr: Series[float] = ta.atr(atrLen)

    atrBaseline: float = ta.sma(atr, atrBaselineLen)

    volatilityExpansion: bool = not na(atrBaseline) and atr > atrBaseline * expansionMultiplier

    plusDI, minusDI, adx = ta.dmi(diLen, adxSmooth)

    bullishADX: bool = adx >= trendAdxThreshold and plusDI > minusDI

    bearishADX: bool = adx >= trendAdxThreshold and minusDI > plusDI

    bbBasis: float = ta.sma(close, bbLen)

    bbDeviation: float = ta.stdev(close, bbLen) * bbMult

    bbWidth: float = 0.0

    if bbBasis != 0:
        bbWidth = 2.0 * bbDeviation / bbBasis * 100.0

    bbWidthBaseline: float = ta.sma(bbWidth, bbBaselineLen)

    compression: bool = not na(bbWidthBaseline) and bbWidth < bbWidthBaseline * compressionMultiplier

    emaSeparationATR: float = 0.0

    if atr > 0:
        emaSeparationATR = math.abs(emaFast - emaSlow) / atr

    rangeBound: bool = compression or (adx < rangeAdxThreshold and emaSeparationATR < minEmaSeparationATR)

    directionalRegime: bool = not rangeBound and (adx >= trendAdxThreshold or emaSeparationATR >= structureRegimeSeparationATR or volatilityExpansion)

    structureAllowed: bool = barstate.isconfirmed and directionalRegime and (not rangeBound) and (not compression)

    marketRegime: str = "TRANSITION"

    if compression:
        marketRegime = "COMPRESSION"
    elif rangeBound:
        marketRegime = "RANGE"
    elif directionalRegime and volatilityExpansion:
        marketRegime = "TREND EXPANSION"
    elif directionalRegime:
        marketRegime = "TRENDING"
    elif volatilityExpansion:
        marketRegime = "VOL EXPANSION"

    avgVolume: Series[float] = ta.sma(volume, volumeLen)

    hasVolume: bool = not na(volume) and (not na(avgVolume)) and (avgVolume > 0)

    bullVolume: bool = hasVolume and volume > avgVolume * volumeMultiplier and (close > close[1])

    bearVolume: bool = hasVolume and volume > avgVolume * volumeMultiplier and (close < close[1])

    internalPivotHigh: float = ta.pivothigh(high, internalSwingLen, internalSwingLen)

    internalPivotLow: float = ta.pivotlow(low, internalSwingLen, internalSwingLen)

    previousInternalHigh: Persistent[float] = na(float)

    previousInternalLow: Persistent[float] = na(float)

    if not na(internalPivotHigh):
        pivotBar: int = bar_index - internalSwingLen

        internalText: str = "iH"

        if not na(previousInternalHigh):
            if internalPivotHigh > previousInternalHigh:
                internalText = "iHH"
            else:
                internalText = "iLH"

        if showInternalLabels:
            internalLabel: Label = label.new(pivotBar, internalPivotHigh, internalText, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_down, color=color.new(color.red, 88), textcolor=color.red, size=size.tiny)

            f_storeLabel(historicalLabels, internalLabel, labelHistoryLimit)

        previousInternalHigh = internalPivotHigh

    if not na(internalPivotLow):
        pivotBar: int = bar_index - internalSwingLen

        internalText: str = "iL"

        if not na(previousInternalLow):
            if internalPivotLow > previousInternalLow:
                internalText = "iHL"
            else:
                internalText = "iLL"

        if showInternalLabels:
            internalLabel: Label = label.new(pivotBar, internalPivotLow, internalText, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_up, color=color.new(color.green, 88), textcolor=color.lime, size=size.tiny)

            f_storeLabel(historicalLabels, internalLabel, labelHistoryLimit)

        previousInternalLow = internalPivotLow

    majorPivotHigh: float = ta.pivothigh(high, majorSwingLen, majorSwingLen)

    majorPivotLow: float = ta.pivotlow(low, majorSwingLen, majorSwingLen)

    previousMajorHigh: Persistent[float] = na(float)

    previousMajorLow: Persistent[float] = na(float)

    lastMajorHigh: Persistent[float] = na(float)

    lastMajorLow: Persistent[float] = na(float)

    lastMajorHighBar: Persistent[int] = na(int)

    lastMajorLowBar: Persistent[int] = na(int)

    lastMajorHighStrength: Persistent[int] = 0

    lastMajorLowStrength: Persistent[int] = 0

    lastMajorHighATR: Persistent[float] = na(float)

    lastMajorLowATR: Persistent[float] = na(float)

    lastMajorHighBroken: Persistent[bool] = False

    lastMajorLowBroken: Persistent[bool] = False

    lastHighType: Persistent[int] = 0

    lastLowType: Persistent[int] = 0

    bullPairCount: Persistent[int] = 0

    bearPairCount: Persistent[int] = 0

    if not na(majorPivotHigh):
        pivotBar: int = bar_index - majorSwingLen

        currentHighType: int = 0

        if not na(previousMajorHigh):
            if majorPivotHigh > previousMajorHigh:
                currentHighType = 1
            else:
                currentHighType = -1

        pivotATR: float = nz(atr[majorSwingLen], atr)

        reactionATR: float = 0.0

        if pivotATR > 0:
            reactionATR = math.max(majorPivotHigh - close, 0.0) / pivotATR

        legATR: float = 1.0

        if not na(lastMajorLow) and pivotATR > 0:
            legATR = math.abs(majorPivotHigh - lastMajorLow) / pivotATR

        volumeRatio: float = 1.0

        if not na(avgVolume[majorSwingLen]) and avgVolume[majorSwingLen] > 0:
            volumeRatio = volume[majorSwingLen] / avgVolume[majorSwingLen]

        strength: int = f_strength(reactionATR, legATR, volumeRatio, htfBear)

        bullishSequence: bool = currentHighType == 1 and lastLowType == 1

        bearishSequence: bool = currentHighType == -1 and lastLowType == -1

        if showStructureBands and (not na(lastMajorLow)) and (not na(lastMajorLowBar)) and (bullishSequence or bearishSequence):
            sequenceStrength: int = cast_int(math.round((strength + lastMajorLowStrength) / 2.0))

            sequenceATR: float = pivotATR

            if not na(lastMajorLowATR):
                sequenceATR = (pivotATR + lastMajorLowATR) / 2.0

            validBand: bool = sequenceStrength >= minimumBandStrength and legATR >= minimumBandLegATR

            if validBand:
                f_drawStructureBand(historicalLines, drawingHistoryLimit, lastMajorLowBar, lastMajorLow, pivotBar, majorPivotHigh, sequenceATR, bullishSequence, sequenceStrength, structureBandWidthATR, bullishBandColor, bearishBandColor, bandCoreTransparency)

        if currentHighType == 1:
            bearPairCount = 0
        elif currentHighType == -1:
            bullPairCount = 0

        lastMajorHigh = majorPivotHigh

        lastMajorHighBar = pivotBar

        lastMajorHighStrength = strength

        lastMajorHighATR = pivotATR

        lastMajorHighBroken = False

        lastHighType = currentHighType

        previousMajorHigh = majorPivotHigh

    if not na(majorPivotLow):
        pivotBar: int = bar_index - majorSwingLen

        currentLowType: int = 0

        if not na(previousMajorLow):
            if majorPivotLow > previousMajorLow:
                currentLowType = 1
            else:
                currentLowType = -1

        pivotATR: float = nz(atr[majorSwingLen], atr)

        reactionATR: float = 0.0

        if pivotATR > 0:
            reactionATR = math.max(close - majorPivotLow, 0.0) / pivotATR

        legATR: float = 1.0

        if not na(lastMajorHigh) and pivotATR > 0:
            legATR = math.abs(lastMajorHigh - majorPivotLow) / pivotATR

        volumeRatio: float = 1.0

        if not na(avgVolume[majorSwingLen]) and avgVolume[majorSwingLen] > 0:
            volumeRatio = volume[majorSwingLen] / avgVolume[majorSwingLen]

        strength: int = f_strength(reactionATR, legATR, volumeRatio, htfBull)

        bullishSequence: bool = currentLowType == 1 and lastHighType == 1

        bearishSequence: bool = currentLowType == -1 and lastHighType == -1

        if showStructureBands and (not na(lastMajorHigh)) and (not na(lastMajorHighBar)) and (bullishSequence or bearishSequence):
            sequenceStrength: int = cast_int(math.round((strength + lastMajorHighStrength) / 2.0))

            sequenceATR: float = pivotATR

            if not na(lastMajorHighATR):
                sequenceATR = (pivotATR + lastMajorHighATR) / 2.0

            validBand: bool = sequenceStrength >= minimumBandStrength and legATR >= minimumBandLegATR

            if validBand:
                f_drawStructureBand(historicalLines, drawingHistoryLimit, lastMajorHighBar, lastMajorHigh, pivotBar, majorPivotLow, sequenceATR, bullishSequence, sequenceStrength, structureBandWidthATR, bullishBandColor, bearishBandColor, bandCoreTransparency)

        completedBullPair: bool = currentLowType == 1 and lastHighType == 1

        completedBearPair: bool = currentLowType == -1 and lastHighType == -1

        if completedBullPair:
            bearPairCount = 0

            bullPairCount += 1
        elif completedBearPair:
            bullPairCount = 0

            bearPairCount += 1
        else:
            if currentLowType == -1:
                bullPairCount = 0

            if currentLowType == 1:
                bearPairCount = 0

        lastMajorLow = majorPivotLow

        lastMajorLowBar = pivotBar

        lastMajorLowStrength = strength

        lastMajorLowATR = pivotATR

        lastMajorLowBroken = False

        lastLowType = currentLowType

        previousMajorLow = majorPivotLow

    externalStructureDirection: Persistent[int] = 0

    bullBreak: bool = False

    bearBreak: bool = False

    bullBOS: bool = False

    bearBOS: bool = False

    bullCHOCH: bool = False

    bearCHOCH: bool = False

    bullishBreakCandidate: bool = not na(lastMajorHigh) and (not lastMajorHighBroken) and (close > lastMajorHigh + atr * structureBreakBuffer)

    bearishBreakCandidate: bool = not na(lastMajorLow) and (not lastMajorLowBroken) and (close < lastMajorLow - atr * structureBreakBuffer)

    if structureAllowed and bullishBreakCandidate:
        bullBreak = True

        bullCHOCH = externalStructureDirection == -1

        bullBOS = externalStructureDirection != -1

        lastMajorHighBroken = True

    if structureAllowed and bearishBreakCandidate:
        bearBreak = True

        bearCHOCH = externalStructureDirection == 1

        bearBOS = externalStructureDirection != 1

        lastMajorLowBroken = True

    lastBullBreakLevel: Persistent[float] = na(float)

    lastBearBreakLevel: Persistent[float] = na(float)

    lastBullBreakBar: Persistent[int] = na(int)

    lastBearBreakBar: Persistent[int] = na(int)

    bullRetestConsumed: Persistent[bool] = True

    bearRetestConsumed: Persistent[bool] = True

    if bullBreak:
        breakText: str = 'CHOCH' if bullCHOCH else 'BOS'

        breakColor: Color = color.aqua if bullCHOCH else color.lime

        if showBreakLines:
            breakLine: Line = line.new(lastMajorHighBar, lastMajorHigh, bar_index, lastMajorHigh, xloc=xloc.bar_index, extend=extend.none, color=color.new(breakColor, 20), style=line.style_dashed, width=2)

            f_storeLine(historicalLines, breakLine, drawingHistoryLimit)

        if showBreakLabels:
            breakLabel: Label = label.new(bar_index, lastMajorHigh, breakText, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_up, color=color.new(breakColor, 15), textcolor=color.white, size=size.small)

            f_storeLabel(historicalLabels, breakLabel, labelHistoryLimit)

        lastBullBreakLevel = lastMajorHigh

        lastBullBreakBar = bar_index

        bullRetestConsumed = False

        bearRetestConsumed = True

        externalStructureDirection = 1

    if bearBreak:
        breakText: str = 'CHOCH' if bearCHOCH else 'BOS'

        breakColor: Color = color.orange if bearCHOCH else color.red

        if showBreakLines:
            breakLine: Line = line.new(lastMajorLowBar, lastMajorLow, bar_index, lastMajorLow, xloc=xloc.bar_index, extend=extend.none, color=color.new(breakColor, 20), style=line.style_dashed, width=2)

            f_storeLine(historicalLines, breakLine, drawingHistoryLimit)

        if showBreakLabels:
            breakLabel: Label = label.new(bar_index, lastMajorLow, breakText, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_down, color=color.new(breakColor, 15), textcolor=color.white, size=size.small)

            f_storeLabel(historicalLabels, breakLabel, labelHistoryLimit)

        lastBearBreakLevel = lastMajorLow

        lastBearBreakBar = bar_index

        bearRetestConsumed = False

        bullRetestConsumed = True

        externalStructureDirection = -1

    bullRetest: bool = False

    bearRetest: bool = False

    bullRetestWindowActive: bool = not na(lastBullBreakBar) and bar_index > lastBullBreakBar and (bar_index <= lastBullBreakBar + retestWindow)

    bearRetestWindowActive: bool = not na(lastBearBreakBar) and bar_index > lastBearBreakBar and (bar_index <= lastBearBreakBar + retestWindow)

    bullRetestTouch: bool = bullRetestWindowActive and (not bullRetestConsumed) and (low <= lastBullBreakLevel + atr * retestToleranceATR) and (low >= lastBullBreakLevel - atr * retestMaxPenetrationATR)

    bearRetestTouch: bool = bearRetestWindowActive and (not bearRetestConsumed) and (high >= lastBearBreakLevel - atr * retestToleranceATR) and (high <= lastBearBreakLevel + atr * retestMaxPenetrationATR)

    if barstate.isconfirmed and (not rangeBound) and bullRetestTouch and (close > lastBullBreakLevel) and (close > open):
        bullRetest = True

        bullRetestConsumed = True

    if barstate.isconfirmed and (not rangeBound) and bearRetestTouch and (close < lastBearBreakLevel) and (close < open):
        bearRetest = True

        bearRetestConsumed = True

    if bullRetest and showRetests:
        retestLabel: Label = label.new(bar_index, low, 'R>S\nRETEST', xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_up, color=color.new(color.green, 30), textcolor=color.white, size=size.tiny)

        f_storeLabel(historicalLabels, retestLabel, labelHistoryLimit)

    if bearRetest and showRetests:
        retestLabel: Label = label.new(bar_index, high, 'S>R\nRETEST', xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_down, color=color.new(color.red, 30), textcolor=color.white, size=size.tiny)

        f_storeLabel(historicalLabels, retestLabel, labelHistoryLimit)

    validMajorRange: bool = not na(lastMajorHigh) and (not na(lastMajorLow)) and (lastMajorHigh > lastMajorLow)

    majorRange: float = na(float)

    equilibrium: float = na(float)

    equilibriumTolerance: float = na(float)

    if validMajorRange:
        majorRange = lastMajorHigh - lastMajorLow

        equilibrium = (lastMajorHigh + lastMajorLow) / 2.0

        equilibriumTolerance = majorRange * 0.05

    rangeLocation: str = "N/A"

    if validMajorRange:
        if close > equilibrium + equilibriumTolerance:
            rangeLocation = "PREMIUM"
        elif close < equilibrium - equilibriumTolerance:
            rangeLocation = "DISCOUNT"
        else:
            rangeLocation = "EQUILIBRIUM"

    bullishStructure: bool = externalStructureDirection == 1

    bearishStructure: bool = externalStructureDirection == -1

    bullTrendPoints: int = 15 if bullTrend else 0

    bearTrendPoints: int = 15 if bearTrend else 0

    bullHTFPoints: int = 20 if htfBull else 0

    bearHTFPoints: int = 20 if htfBear else 0

    bullStructurePoints: int = 20 if bullishStructure else 0

    bearStructurePoints: int = 20 if bearishStructure else 0

    bullMomentumPoints: int = 0

    if bullRSI:
        bullMomentumPoints += 10

    if bullMACD:
        bullMomentumPoints += 5

    bearMomentumPoints: int = 0

    if bearRSI:
        bearMomentumPoints += 10

    if bearMACD:
        bearMomentumPoints += 5

    bullLocationPoints: int = 10 if aboveMean else 0

    bearLocationPoints: int = 10 if belowMean else 0

    bullVolumePoints: int = 5

    bearVolumePoints: int = 5

    if useVolume and hasVolume:
        bullVolumePoints = 10 if bullVolume else 0

        bearVolumePoints = 10 if bearVolume else 0

    bullRegimePoints: int = 10 if bullishADX else 0

    bearRegimePoints: int = 10 if bearishADX else 0

    bullScore: int = bullTrendPoints + bullHTFPoints + bullStructurePoints + bullMomentumPoints + bullLocationPoints + bullVolumePoints + bullRegimePoints

    bearScore: int = bearTrendPoints + bearHTFPoints + bearStructurePoints + bearMomentumPoints + bearLocationPoints + bearVolumePoints + bearRegimePoints

    scoreDifference: int = bullScore - bearScore

    marketBias: str = "NEUTRAL"

    if scoreDifference >= 35:
        marketBias = "STRONG BULLISH"
    elif scoreDifference >= 15:
        marketBias = "BULLISH"
    elif scoreDifference <= -35:
        marketBias = "STRONG BEARISH"
    elif scoreDifference <= -15:
        marketBias = "BEARISH"

    bullHTFSignalOK: bool = True

    bearHTFSignalOK: bool = True

    if requireHTFForSignals and useHTF:
        bullHTFSignalOK = htfBull

        bearHTFSignalOK = htfBear

    bullParticipationOK: bool = True

    bearParticipationOK: bool = True

    if requireVolumeForSignals and useVolume and hasVolume:
        bullParticipationOK = volume >= avgVolume * signalVolumeMultiplier and close > open

        bearParticipationOK = volume >= avgVolume * signalVolumeMultiplier and close < open

    bullStructureOK: bool = True

    bearStructureOK: bool = True

    if requireStructureAlignment:
        bullStructureOK = bullishStructure

        bearStructureOK = bearishStructure

    bullADXOK: bool = True

    bearADXOK: bool = True

    if requireStrongADX:
        bullADXOK = bullishADX

        bearADXOK = bearishADX

    confirmedBullTrend: bool = barstate.isconfirmed and (not rangeBound) and (not compression) and directionalRegime and bullTrend and aboveMean and bullHTFSignalOK and bullStructureOK and bullADXOK and bullParticipationOK and (bullScore >= minimumSignalScore) and (scoreDifference >= minimumScoreAdvantage)

    confirmedBearTrend: bool = barstate.isconfirmed and (not rangeBound) and (not compression) and directionalRegime and bearTrend and belowMean and bearHTFSignalOK and bearStructureOK and bearADXOK and bearParticipationOK and (bearScore >= minimumSignalScore) and (scoreDifference <= -minimumScoreAdvantage)

    trendState: Persistent[int] = 0

    trendFailureCount: Persistent[int] = 0

    newBullTrend: bool = False

    newBearTrend: bool = False

    if barstate.isconfirmed:
        if trendState == 0:
            trendFailureCount = 0

            if confirmedBullTrend:
                trendState = 1

                newBullTrend = True
            elif confirmedBearTrend:
                trendState = -1

                newBearTrend = True
        elif trendState == 1:
            if confirmedBearTrend:
                trendState = -1

                trendFailureCount = 0

                newBearTrend = True
            else:
                bullTrendStillHealthy: bool = bullTrend and (not rangeBound) and (not compression) and (scoreDifference > 0)

                if bullTrendStillHealthy:
                    trendFailureCount = 0
                else:
                    trendFailureCount += 1

                if trendFailureCount >= trendResetBars:
                    trendState = 0

                    trendFailureCount = 0
        elif trendState == -1:
            if confirmedBullTrend:
                trendState = 1

                trendFailureCount = 0

                newBullTrend = True
            else:
                bearTrendStillHealthy: bool = bearTrend and (not rangeBound) and (not compression) and (scoreDifference < 0)

                if bearTrendStillHealthy:
                    trendFailureCount = 0
                else:
                    trendFailureCount += 1

                if trendFailureCount >= trendResetBars:
                    trendState = 0

                    trendFailureCount = 0

    bullSignalGrade: str = "A"

    bearSignalGrade: str = "A"

    if bullScore >= 92 and scoreDifference >= 35:
        bullSignalGrade = "A+"

    if bearScore >= 92 and scoreDifference <= -35:
        bearSignalGrade = "A+"

    if newBullTrend:
        signalColor: Color = color.green

        if bullSignalGrade == 'A+':
            signalColor = color.lime

        signalText: str = bullSignalGrade + ' BUY\nNEW TREND'

        buyLabel: Label = label.new(bar_index, low - atr * 0.25, signalText, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_up, color=signalColor, textcolor=color.white, size=size.normal)

        f_storeLabel(historicalLabels, buyLabel, labelHistoryLimit)

    if newBearTrend:
        signalColor: Color = color.maroon

        if bearSignalGrade == 'A+':
            signalColor = color.red

        signalText: str = bearSignalGrade + ' SELL\nNEW TREND'

        sellLabel: Label = label.new(bar_index, high + atr * 0.25, signalText, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_down, color=signalColor, textcolor=color.white, size=size.normal)

        f_storeLabel(historicalLabels, sellLabel, labelHistoryLimit)

    fastColor: Color = color.gray

    slowColor: Color = color.gray

    ribbonColor: Color = color.new(color.gray, 94)

    if bullTrend:
        fastColor = color.lime

        slowColor = color.new(color.green, 10)

        ribbonColor = color.new(color.lime, 89)
    elif bearTrend:
        fastColor = color.red

        slowColor = color.new(color.red, 10)

        ribbonColor = color.new(color.red, 89)

    fastPlot = plot(emaFast if showTrendRibbon else na, 'Fast EMA', color=fastColor, linewidth=1)

    slowPlot = plot(emaSlow if showTrendRibbon else na, 'Slow EMA', color=slowColor, linewidth=2)

    fill(fastPlot, slowPlot, color=ribbonColor if showTrendRibbon else na, title='Adaptive Trend Ribbon')

    plot(meanLine if showMean else na, 'VWAP / Mean', color=color.new(color.blue, 20), linewidth=2)

    candleColor: Color = color.from_gradient(scoreDifference, -100, 100, color.red, color.lime)

    barcolor(color.new(candleColor, 48) if colorCandles else na)

    resistanceAge: int = 9999

    if not na(lastMajorHighBar):
        resistanceAge = bar_index - lastMajorHighBar

    supportAge: int = 9999

    if not na(lastMajorLowBar):
        supportAge = bar_index - lastMajorLowBar

    resistanceFreshness: str = f_freshness(resistanceAge)

    supportFreshness: str = f_freshness(supportAge)

    structureText: str = "UNDEFINED"

    structureTextColor: Color = color.gray

    if bullishStructure:
        structureText = "BULLISH"

        structureTextColor = color.lime
    elif bearishStructure:
        structureText = "BEARISH"

        structureTextColor = color.red

    sequenceText: str = "MIXED"

    sequenceColor: Color = color.gray

    if bullPairCount >= requiredStructurePairs:
        sequenceText = 'BULL x' + string.tostring(bullPairCount)

        sequenceColor = color.lime
    elif bearPairCount >= requiredStructurePairs:
        sequenceText = 'BEAR x' + string.tostring(bearPairCount)

        sequenceColor = color.red
    elif bullPairCount > 0:
        sequenceText = 'BULL BUILD ' + string.tostring(bullPairCount) + '/' + string.tostring(requiredStructurePairs)

        sequenceColor = color.green
    elif bearPairCount > 0:
        sequenceText = 'BEAR BUILD ' + string.tostring(bearPairCount) + '/' + string.tostring(requiredStructurePairs)

        sequenceColor = color.maroon

    htfText: str = "NEUTRAL"

    htfTextColor: Color = color.gray

    if htfBull:
        htfText = "BULLISH"

        htfTextColor = color.lime
    elif htfBear:
        htfText = "BEARISH"

        htfTextColor = color.red

    trendStateText: str = "NEUTRAL / ARMED"

    trendStateColor: Color = color.orange

    if trendState == 1:
        trendStateText = "BULL TREND ACTIVE"

        trendStateColor = color.lime
    elif trendState == -1:
        trendStateText = "BEAR TREND ACTIVE"

        trendStateColor = color.red

    signalState: str = "WAIT"

    signalStateColor: Color = color.orange

    if rangeBound or compression:
        signalState = "WAIT - RANGE"
    elif trendState == 1:
        signalState = "BUY USED"

        signalStateColor = color.lime
    elif trendState == -1:
        signalState = "SELL USED"

        signalStateColor = color.red
    elif confirmedBullTrend:
        signalState = "BULL START READY"

        signalStateColor = color.lime
    elif confirmedBearTrend:
        signalState = "BEAR START READY"

        signalStateColor = color.red

    biasColor: Color = color.new(color.gray, 75)

    if marketBias == 'STRONG BULLISH' or marketBias == 'BULLISH':
        biasColor = color.new(color.green, 70)
    elif marketBias == 'STRONG BEARISH' or marketBias == 'BEARISH':
        biasColor = color.new(color.red, 70)

    regimeColor: Color = color.new(color.gray, 75)

    if marketRegime == 'RANGE' or marketRegime == 'COMPRESSION':
        regimeColor = color.new(color.orange, 65)
    elif marketRegime == 'TREND EXPANSION':
        regimeColor = color.new(color.blue, 55)

    resistanceText: str = "N/A"

    if not na(lastMajorHigh):
        resistanceText = string.tostring(lastMajorHigh, format.mintick) + ' | ' + string.tostring(lastMajorHighStrength) + ' | ' + resistanceFreshness

    supportText: str = "N/A"

    if not na(lastMajorLow):
        supportText = string.tostring(lastMajorLow, format.mintick) + ' | ' + string.tostring(lastMajorLowStrength) + ' | ' + supportFreshness

    dashboard: Persistent[Table] = table.new(position.top_right, 2, 13, border_width=1)

    if barstate.islast and showDashboard:
        table.cell(dashboard, 0, 0, 'MARKET ENGINE', text_color=color.white, bgcolor=color.new(color.black, 10))

        table.cell(dashboard, 1, 0, 'TEST 6', text_color=color.white, bgcolor=color.new(color.black, 10))

        table.cell(dashboard, 0, 1, 'Regime', text_color=color.white)

        table.cell(dashboard, 1, 1, marketRegime, text_color=color.white, bgcolor=regimeColor)

        table.cell(dashboard, 0, 2, 'Bias', text_color=color.white)

        table.cell(dashboard, 1, 2, marketBias, text_color=color.white, bgcolor=biasColor)

        table.cell(dashboard, 0, 3, 'Trend State', text_color=color.white)

        table.cell(dashboard, 1, 3, trendStateText, text_color=trendStateColor)

        table.cell(dashboard, 0, 4, 'Structure Build', text_color=color.white)

        table.cell(dashboard, 1, 4, sequenceText, text_color=sequenceColor)

        table.cell(dashboard, 0, 5, 'Bull Score', text_color=color.white)

        table.cell(dashboard, 1, 5, string.tostring(bullScore) + '/100', text_color=color.lime)

        table.cell(dashboard, 0, 6, 'Bear Score', text_color=color.white)

        table.cell(dashboard, 1, 6, string.tostring(bearScore) + '/100', text_color=color.red)

        table.cell(dashboard, 0, 7, 'Major Structure', text_color=color.white)

        table.cell(dashboard, 1, 7, structureText, text_color=structureTextColor)

        table.cell(dashboard, 0, 8, 'HTF', text_color=color.white)

        table.cell(dashboard, 1, 8, htfText, text_color=htfTextColor)

        table.cell(dashboard, 0, 9, 'Resistance', text_color=color.white)

        table.cell(dashboard, 1, 9, resistanceText, text_color=color.red)

        table.cell(dashboard, 0, 10, 'Support', text_color=color.white)

        table.cell(dashboard, 1, 10, supportText, text_color=color.lime)

        rangeTextColor: Color = color.gray

        if rangeLocation == 'DISCOUNT':
            rangeTextColor = color.lime
        elif rangeLocation == 'PREMIUM':
            rangeTextColor = color.orange

        table.cell(dashboard, 0, 11, 'Range Location', text_color=color.white)

        table.cell(dashboard, 1, 11, rangeLocation, text_color=rangeTextColor)

        table.cell(dashboard, 0, 12, 'Signal State', text_color=color.white)

        table.cell(dashboard, 1, 12, signalState, text_color=signalStateColor)

    alertcondition(newBullTrend, 'AMIE New Bull Trend', 'AMIE Test 6: New high-quality bullish trend confirmed.')

    alertcondition(newBearTrend, 'AMIE New Bear Trend', 'AMIE Test 6: New high-quality bearish trend confirmed.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
