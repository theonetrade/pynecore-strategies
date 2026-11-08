"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, array, bar_index, barstate, chart, close, color, display, fill,
    format, high, input, label, line, linefill, location, low, math, na, nz, open, plot, plotshape,
    position, script, shape, size, string, syminfo, ta, table, text, timeframe, volume
)
from pynecore.types import Color, Label, Line, LineFill, NA, Persistent, Table


@udt
class Trade:
    sigBar: int = na(int)
    closeBar: int = na(int)
    isLong: bool = na(bool)
    signalType: str = na(str)
    entry: float = na(float)
    targetOne: float = na(float)
    targetTwo: float = na(float)
    invalidation: float = na(float)
    active: bool = na(bool)
    extensionCount: int = na(int)
    entryLine: Line = na(Line)
    targetOneLine: Line = na(Line)
    targetTwoLine: Line = na(Line)
    invalidationLine: Line = na(Line)
    signalLabel: Label = na(Label)
    pathUpperOne: Line = na(Line)
    pathUpperTwo: Line = na(Line)
    pathUpperThree: Line = na(Line)
    pathLowerOne: Line = na(Line)
    pathLowerTwo: Line = na(Line)
    pathLowerThree: Line = na(Line)
    pathCenterOne: Line = na(Line)
    pathCenterTwo: Line = na(Line)
    pathCenterThree: Line = na(Line)
    pathFillOne: LineFill = na(LineFill)
    pathFillTwo: LineFill = na(LineFill)
    pathFillThree: LineFill = na(LineFill)


GRP_PATH: str = "Trade Geometry"
GRP_VIS: str = "Visual System"
GRP_DASH: str = "Dashboard"
GRP_ENGINE: str = "Engine Sensitivity"


@script.indicator("Reaction Path [BullByte]", overlay=False, max_lines_count=500, max_labels_count=500, max_bars_back=500)
def main(
    signalModeInput=input.string("Both", "Signal Mode", options=("Reaction Only", "Continuation Only", "Both"), group=GRP_ENGINE, tooltip="Choose which signal family the engine is allowed to open: Reaction setups (mean-reversion off fair value), Continuation setups (trend persistence), or both."),
    sensitivityInput=input.float(0.75, "Setup Sensitivity", minval=0.5, maxval=1.5, step=0.05, group=GRP_ENGINE, tooltip="Adjusts the overall qualification balance. Lower values tighten distance and expansion requirements while relaxing several quality thresholds; higher values do the opposite. Use this control to adapt overall setup selectivity."),
    t1AtrInput=input.float(1.2, "Path Level 1", minval=0.3, maxval=8.0, step=0.1, group=GRP_PATH, tooltip="Distance from the setup entry reference to Path Level 1, measured in ATR units."),
    t2AtrInput=input.float(2.4, "Path Level 2", minval=0.5, maxval=12.0, step=0.1, group=GRP_PATH, tooltip="Distance from the setup entry reference to Path Level 2, measured in ATR units. This is the primary projected objective used by the indicator's trade geometry."),
    invalidationAtrInput=input.float(1.2, "Invalidation", minval=0.3, maxval=8.0, step=0.1, group=GRP_PATH, tooltip="Distance beyond the reaction extreme used to define the setup invalidation boundary. It is a reference level, not a guarantee of execution or outcome."),
    showHistoryInput=input.bool(True, "Show Historical Setups", group=GRP_VIS, tooltip="When enabled, completed setups stay visible on the chart (up to the Maximum Historical Setups limit below) instead of disappearing once they close, so you can review how past setups played out. When disabled, a setup's drawings are removed as soon as it closes."),
    maxHistoryInput=input.int(20, "Maximum Historical Setups", minval=3, maxval=25, group=GRP_VIS, tooltip="Caps how many completed setups stay drawn on the chart at once. The oldest setup is automatically removed once this limit is reached. This is kept intentionally bounded to stay comfortably within TradingView's per-script drawing-object limits."),
    showFairBandInput=input.bool(True, "Show Reaction Band", group=GRP_VIS, tooltip="Displays the Fair Price zone as three nested bands on the price chart, showing the current wick-weighted value area and its deviation range. Turn off for a cleaner chart if you only want the pane readout and trade markers."),
    showPathInput=input.bool(True, "Show Projected Path", group=GRP_VIS, tooltip="Displays the Projected Path corridor running from the setup's entry toward Path Level 2. This is a visual route built from current market conditions, not a price forecast or guarantee. Turn off to show only the entry, target and invalidation lines without the corridor."),
    showDashboardInput=input.bool(True, "Show Dashboard", group=GRP_DASH, tooltip="Displays the on-chart panel summarising the current market state, path direction, price location relative to fair value, and the active setup's levels (if any)."),
    dashboardSizeInput=input.string("Small", "Dashboard Size", options=("Small", "Medium", "Large"), group=GRP_DASH, tooltip="Controls the text size of the on-chart dashboard panel."),
    dashboardPositionInput=input.string("Top Right", "Dashboard Position", options=("Top Left", "Top Right", "Bottom Left", "Bottom Right"), group=GRP_DASH, tooltip="Controls which corner of the chart the dashboard panel is anchored to.")
):
    N: int = 20
    M: int = 5
    K: int = 10
    J: int = 5
    ATR_LENGTH: int = 14

    MIN_DISPLACEMENT: float = 0.8
    MIN_DIRECTIONAL_EFFICIENCY: float = 0.55
    MIN_SPEED: float = 0.9
    MIN_VOLUME: float = 0.8
    MIN_DEPTH: float = 0.5

    SPIKE_MULTIPLIER: float = 3.0
    SPIKE_EFFICIENCY: float = 0.2
    CONTINUATION_MAX_WICK: float = 0.35

    EXHAUSTION_HIGH: float = 0.8
    EXHAUSTION_LOW: float = 0.2
    STALL_THRESHOLD: float = 0.015
    BUILD_THRESHOLD: float = 0.7
    APPROACH_MINIMUM: float = 0.02

    MIGRATION_SCALE: float = 3.0

    TREND_WINDOW: int = 15
    MIN_TREND_EFFICIENCY: float = 0.38

    displacementThreshold: float = MIN_DISPLACEMENT / sensitivityInput
    directionalEfficiencyThreshold: float = MIN_DIRECTIONAL_EFFICIENCY * sensitivityInput
    speedThreshold: float = MIN_SPEED * sensitivityInput
    depthThreshold: float = MIN_DEPTH / sensitivityInput
    continuationWickThreshold: float = CONTINUATION_MAX_WICK / sensitivityInput
    volumeThresholdSensitivity: float = MIN_VOLUME * sensitivityInput
    stallThreshold: float = STALL_THRESHOLD * sensitivityInput
    expansionAtrFloor: float = 0.7 / sensitivityInput
    trendEfficiencyThreshold: float = MIN_TREND_EFFICIENCY * sensitivityInput

    reactionSignalsEnabled: bool = signalModeInput != 'Continuation Only'
    continuationSignalsEnabled: bool = signalModeInput != 'Reaction Only'

    COLOR_UP_REACTION: Color = color.new('#38D9C4')
    COLOR_UP_TRAVEL: Color = color.new('#5B8CFF')
    COLOR_DOWN_REACTION: Color = color.new('#FF708A')
    COLOR_DOWN_TRAVEL: Color = color.new('#B56CFF')

    COLOR_REACTION: Color = color.new('#38D9C4')
    COLOR_CONTINUATION: Color = color.new('#6F8CFF')
    COLOR_SHIFT: Color = color.new('#FFC857')
    COLOR_BUILDING: Color = color.new('#55D8FF')
    COLOR_EXHAUSTION: Color = color.new('#B974FF')
    COLOR_NEUTRAL: Color = color.new('#9BA8B5')
    COLOR_INVALIDATION: Color = color.new('#FFAA4A')
    COLOR_PATH_LEVEL_ONE: Color = color.new('#4CAF50')
    COLOR_PATH_LEVEL_TWO: Color = color.new('#D6249F')
    COLOR_WHITE: Color = color.new('#F4F7FA')

    COLOR_PANEL: Color = color.new('#11161D')
    COLOR_PANEL_BORDER: Color = color.new('#2A323C')

    def safeDiv(numerator: float, denominator: float, fallback: float):
        return fallback if denominator == 0.0 or na(denominator) else numerator / denominator

    def clamp(value: float, minimum: float, maximum: float):
        return math.max(minimum, math.min(value, maximum))

    def volumeReliable():
        volumeSum: float = 0.0
        volumeSquares: float = 0.0

        for i in pine_range(0, N - 1):
            currentVolume: float = nz(volume[i], 0.0)
            volumeSum += currentVolume
            volumeSquares += currentVolume * currentVolume

        meanVolume: float = safeDiv(volumeSum, N, 0.0)
        variance: float = safeDiv(volumeSquares, N, 0.0) - meanVolume * meanVolume
        coefficient: float = safeDiv(math.sqrt(math.max(variance, 0.0)), meanVolume, 0.0)

        return coefficient > 0.05

    def dashboardTextSize(value: str):
        return size.normal if value == 'Large' else size.small if value == 'Medium' else size.tiny

    def dashboardPosition(value: str):
        return position.top_left if value == 'Top Left' else position.bottom_left if value == 'Bottom Left' else position.bottom_right if value == 'Bottom Right' else position.top_right

    def stateColor(value: str):
        return COLOR_REACTION if value == 'REACTION' else COLOR_CONTINUATION if value == 'TRAVEL' else COLOR_BUILDING if value == 'BUILDING' else COLOR_SHIFT if value == 'SHIFT' else COLOR_EXHAUSTION if value == 'EXHAUSTION' else COLOR_UP_REACTION if value == 'MOVING UP' else COLOR_DOWN_REACTION if value == 'MOVING DOWN' else COLOR_NEUTRAL

    def buildAlertMessage(eventLabel: str, signalType: str, priceLevel: float):
        return syminfo.prefix + ':' + syminfo.ticker + ' | ' + timeframe.period + ' | ' + eventLabel + ' | ' + signalType + ' | Price: ' + string.tostring(priceLevel, format.mintick)

    atrValue: float = ta.atr(ATR_LENGTH)

    engineReady: bool = chart.is_standard and bar_index > N + J + M + ATR_LENGTH

    nonStandardWarning: Persistent[Label] = na(Label)

    if not chart.is_standard and barstate.islast:
        label.delete(nonStandardWarning)
        nonStandardWarning = label.new(bar_index, high, 'Reaction Path requires a standard chart.\nSignals are disabled on non-standard chart types.', color=COLOR_INVALIDATION, textcolor=COLOR_WHITE, style=label.style_label_left, size=size.normal, force_overlay=True)

    def fairCalc(offset: int):
        weightedBase: float = 0.0
        totalWeight: float = 0.0

        for i in pine_range(offset, offset + N - 1):
            basePrice: float = (high[i] + low[i] + 2.0 * close[i]) / 4.0
            candleRange: float = high[i] - low[i]
            candleBody: float = math.abs(close[i] - open[i])
            weight: float = 1.0 - safeDiv(candleBody, candleRange, 1.0)

            weightedBase += basePrice * weight
            totalWeight += weight

        fallbackFair: float = (high[offset] + low[offset] + 2.0 * close[offset]) / 4.0
        fair: float = safeDiv(weightedBase, totalWeight, fallbackFair)

        weightedDeviation: float = 0.0
        deviationWeight: float = 0.0

        for i in pine_range(offset, offset + N - 1):
            basePrice: float = (high[i] + low[i] + 2.0 * close[i]) / 4.0
            candleRange: float = high[i] - low[i]
            candleBody: float = math.abs(close[i] - open[i])
            weight: float = 1.0 - safeDiv(candleBody, candleRange, 1.0)

            weightedDeviation += math.abs(basePrice - fair) * weight
            deviationWeight += weight

        fallbackHalf: float = math.abs(close[offset] - fair) * 0.5

        halfBand: float = math.max(safeDiv(weightedDeviation, deviationWeight, fallbackHalf), syminfo.mintick * 2.0)

        return (fair, halfBand)

    fairPrice, fairHalf = fairCalc(0)
    previousFair, previousHalf = fairCalc(1)

    fairUpper: float = fairPrice + fairHalf
    fairLower: float = fairPrice - fairHalf

    previousUpper: float = previousFair + previousHalf
    previousLower: float = previousFair - previousHalf

    aboveFair: bool = close > fairUpper
    belowFair: bool = close < fairLower

    previousAboveFair: bool = close[1] > previousUpper
    previousBelowFair: bool = close[1] < previousLower

    acceptingAbove: bool = aboveFair and previousAboveFair
    acceptingBelow: bool = belowFair and previousBelowFair

    def pressureCentreAt(offset: int):
        pressureSum: float = 0.0
        pressureWeight: float = 0.0

        for i in pine_range(offset, offset + K - 1):
            candleRange: float = high[i] - low[i]
            candleBody: float = math.abs(close[i] - open[i])
            weight: float = 1.0 - safeDiv(candleBody, candleRange, 1.0)
            closeLocation: float = safeDiv(close[i] - low[i], candleRange, 0.5)

            pressureSum += closeLocation * weight
            pressureWeight += weight

        return safeDiv(pressureSum, pressureWeight, 0.5)

    pressureNow: float = pressureCentreAt(0)
    pressurePrior: float = pressureCentreAt(J)
    pressurePrevious: float = pressureCentreAt(1)
    pressurePreviousPrior: float = pressureCentreAt(J + 1)

    migration: float = pressureNow - pressurePrior
    previousMigration: float = pressurePrevious - pressurePreviousPrior

    approachingBuild: bool = pressureNow >= BUILD_THRESHOLD - APPROACH_MINIMUM and pressureNow < BUILD_THRESHOLD and (pressureNow > pressurePrior)

    exhaustion: bool = pressureNow >= EXHAUSTION_HIGH or pressureNow <= EXHAUSTION_LOW

    reversing: bool = not exhaustion and (migration >= stallThreshold and previousMigration <= -stallThreshold or (migration <= -stallThreshold and previousMigration >= stallThreshold))

    building: bool = not exhaustion and (not reversing) and (approachingBuild or pressureNow >= BUILD_THRESHOLD) and (migration > 0.0)

    migratingUp: bool = not exhaustion and (not reversing) and (not building) and (migration > stallThreshold)

    migratingDown: bool = not exhaustion and (not reversing) and (not building) and (not migratingUp) and (migration < -stallThreshold)

    pressureUp: bool = migration > 0.0 and (migratingUp or building or reversing)

    pressureDown: bool = migration < 0.0 and (migratingDown or reversing)

    continuationLong: bool = migration > 0.0 and (building or migratingUp)

    continuationShort: bool = migration < 0.0 and migratingDown

    trendNetDisplacement: float = close - close[TREND_WINDOW]

    trendPathLength: float = 0.0

    for i in pine_range(0, TREND_WINDOW - 1):
        trendPathLength += math.abs(close[i] - close[i + 1])

    trendEfficiencyRatio: float = safeDiv(math.abs(trendNetDisplacement), trendPathLength, 0.0)

    trendAlignedLong: bool = trendNetDisplacement > 0.0 and trendEfficiencyRatio >= trendEfficiencyThreshold
    trendAlignedShort: bool = trendNetDisplacement < 0.0 and trendEfficiencyRatio >= trendEfficiencyThreshold

    barRange: float = high - low
    barBody: float = math.abs(close - open)

    efficiency: float = safeDiv(barBody, barRange, 1.0)

    upperWick: float = high - math.max(open, close)
    lowerWick: float = math.min(open, close) - low

    upperWickRatio: float = safeDiv(upperWick, barRange, 0.0)
    lowerWickRatio: float = safeDiv(lowerWick, barRange, 0.0)

    averageRange: float = 0.0

    for i in pine_range(1, M):
        averageRange += high[i] - low[i]

    averageRange = safeDiv(averageRange, M, barRange)

    speedRatio: float = safeDiv(barRange, averageRange, 1.0)

    reliableVolume: bool = volumeReliable()

    averageVolume: float = 0.0

    for i in pine_range(1, N):
        averageVolume += nz(volume[i], 0.0)

    averageVolume = safeDiv(averageVolume, N, 0.0)

    volumeRatio: float = safeDiv(volume, averageVolume, 1.0) if reliableVolume else 1.0

    directionalEfficiencyLong: float = 0.0
    directionalEfficiencyShort: float = 0.0

    directionalCountLong: int = 0
    directionalCountShort: int = 0

    for i in pine_range(0, M - 1):
        historicalRange: float = high[i] - low[i]
        historicalBody: float = math.abs(close[i] - open[i])
        historicalEfficiency: float = safeDiv(historicalBody, historicalRange, 1.0)

        if close[i] > open[i]:
            directionalEfficiencyLong += historicalEfficiency
            directionalCountLong += 1
        elif close[i] < open[i]:
            directionalEfficiencyShort += historicalEfficiency
            directionalCountShort += 1

    meanDirectionalEfficiencyLong: float = safeDiv(directionalEfficiencyLong, directionalCountLong, 0.0)
    meanDirectionalEfficiencyShort: float = safeDiv(directionalEfficiencyShort, directionalCountShort, 0.0)

    directionalDominanceLong: float = safeDiv(directionalCountLong, M, 0.0)
    directionalDominanceShort: float = safeDiv(directionalCountShort, M, 0.0)

    displacement: float = safeDiv(close - fairPrice, fairHalf, 0.0)

    depthBelowFair: float = 0.0
    depthAboveFair: float = 0.0

    for i in pine_range(1, M):
        depthBelowFair = math.max(depthBelowFair, safeDiv(fairPrice - low[i], fairHalf, 0.0))
        depthAboveFair = math.max(depthAboveFair, safeDiv(high[i] - fairPrice, fairHalf, 0.0))

    currentSpike: bool = barRange > SPIKE_MULTIPLIER * averageRange and efficiency < SPIKE_EFFICIENCY

    previousSpikeReversal: bool = high[1] - low[1] > SPIKE_MULTIPLIER * averageRange and safeDiv(math.abs(close[1] - open[1]), math.max(high[1] - low[1], syminfo.mintick), 1.0) < SPIKE_EFFICIENCY and (close >= low[1]) and (close <= high[1])

    normalBar: bool = not currentSpike and (not previousSpikeReversal)

    previousMaximumRange: float = 0.0

    for i in pine_range(1, M):
        previousMaximumRange = math.max(previousMaximumRange, high[i] - low[i])

    newExpansion: bool = barRange >= previousMaximumRange and barRange >= atrValue * expansionAtrFloor

    longReactionGate: bool = displacement < -displacementThreshold and meanDirectionalEfficiencyLong >= directionalEfficiencyThreshold and (directionalDominanceLong >= 0.4) and (lowerWickRatio > upperWickRatio) and (lowerWick > upperWick) and (speedRatio >= speedThreshold) and (volumeRatio >= volumeThresholdSensitivity) and (depthBelowFair >= depthThreshold) and normalBar

    shortReactionGate: bool = displacement > displacementThreshold and meanDirectionalEfficiencyShort >= directionalEfficiencyThreshold and (directionalDominanceShort >= 0.4) and (upperWickRatio > lowerWickRatio) and (upperWick > lowerWick) and (speedRatio >= speedThreshold) and (volumeRatio >= volumeThresholdSensitivity) and (depthAboveFair >= depthThreshold) and normalBar

    longContinuationGate: bool = (aboveFair or acceptingAbove) and newExpansion and (upperWickRatio < continuationWickThreshold) and (efficiency > 0.5) and (speedRatio >= speedThreshold) and (volumeRatio >= volumeThresholdSensitivity) and trendAlignedLong and normalBar

    shortContinuationGate: bool = (belowFair or acceptingBelow) and newExpansion and (lowerWickRatio < continuationWickThreshold) and (efficiency > 0.5) and (speedRatio >= speedThreshold) and (volumeRatio >= volumeThresholdSensitivity) and trendAlignedShort and normalBar

    rearmReady: Persistent[bool] = True
    rearmPending: Persistent[bool] = False
    tradeClosedThisBar: Persistent[bool] = False

    activeTrade: Persistent[Trade] = na(Trade)
    historicalTrades: Persistent[list[Trade]] = array.new(0, NA(Trade))
    signalEventLocked: Persistent[bool] = False
    signalEventDirection: Persistent[int] = 0
    signalEventFamily: Persistent[int] = 0
    liveTargetOneLabel: Persistent[Label] = na(Label)
    liveTargetTwoLabel: Persistent[Label] = na(Label)
    liveEntryLabel: Persistent[Label] = na(Label)
    liveInvalidationLabel: Persistent[Label] = na(Label)

    failureMemoryActive: Persistent[bool] = False
    failureMemoryBar: Persistent[int] = na(int)
    lastFailureBar: Persistent[int] = na(int)
    failureCount: Persistent[int] = 0
    failedDirectionLong: Persistent[bool] = False
    failedSignalFamily: Persistent[int] = 0

    failedDisplacement: Persistent[float] = na(float)
    failedMigration: Persistent[float] = na(float)
    failedEfficiency: Persistent[float] = na(float)
    failedSpeedRatio: Persistent[float] = na(float)
    failedDepth: Persistent[float] = na(float)
    failedVolumeRatio: Persistent[float] = na(float)
    failedPressure: Persistent[float] = na(float)
    failedRangeRatio: Persistent[float] = na(float)

    FAILURE_MEMORY_LIMIT: Persistent[int] = 30
    FAILURE_MAX_COUNT: Persistent[int] = 3
    MAX_TARGET_EXTENSIONS: Persistent[int] = 3

    def featureSimilarity(currentValue: float, referenceValue: float, tolerance: float):
        similarity: float = 0.0
        if not na(referenceValue):
            similarity = 1.0 - clamp(math.abs(currentValue - referenceValue) / tolerance, 0.0, 1.0)
        return similarity

    def currentFailureSimilarity(isLong: bool):
        currentEfficiency: float = meanDirectionalEfficiencyLong if isLong else meanDirectionalEfficiencyShort
        currentDepth: float = depthBelowFair if isLong else depthAboveFair
        similarityDisplacement: float = featureSimilarity(math.abs(displacement), failedDisplacement, 0.8)
        similarityMigration: float = featureSimilarity(migration, failedMigration, 0.12)
        similarityEfficiency: float = featureSimilarity(currentEfficiency, failedEfficiency, 0.25)
        similaritySpeed: float = featureSimilarity(speedRatio, failedSpeedRatio, 0.8)
        similarityDepth: float = featureSimilarity(currentDepth, failedDepth, 1.0)
        similarityVolume: float = featureSimilarity(volumeRatio, failedVolumeRatio, 0.75)
        similarityPressure: float = featureSimilarity(pressureNow, failedPressure, 0.2)
        currentRangeRatio: float = safeDiv(barRange, atrValue, 1.0)
        similarityRange: float = featureSimilarity(currentRangeRatio, failedRangeRatio, 0.8)
        similarityTotal: float = similarityDisplacement + similarityMigration + similarityEfficiency + similaritySpeed + similarityDepth + similarityVolume + similarityPressure + similarityRange
        return similarityTotal / 8.0

    def failureMemoryExpired():
        expired: bool = False
        if failureMemoryActive and (not na(failureMemoryBar)):
            expired = bar_index - failureMemoryBar > FAILURE_MEMORY_LIMIT
        return expired

    def failureBehaviourReset():
        resetDetected: bool = False

        if failureMemoryActive:
            displacementReset: bool = math.abs(displacement) < 0.35
            pressureReset: bool = math.abs(migration) < 0.025
            directionReset: bool = False

            if failedDirectionLong and migration < -0.025:
                directionReset = True

            if not failedDirectionLong and migration > 0.025:
                directionReset = True

            currentRangeRatio: float = safeDiv(barRange, atrValue, 1.0)
            rangeExpansionReset: bool = False

            if not na(failedRangeRatio):
                rangeExpansionReset = currentRangeRatio > failedRangeRatio * 1.25

            resetDetected = displacementReset or pressureReset or directionReset or rangeExpansionReset

        return resetDetected

    def signalBehaviourReset(direction: int, family: int):
        resetDetected: bool = False

        if family == 1:
            if direction == 1:
                resetDetected = displacement > 0.15 and migration <= 0.0
            else:
                resetDetected = displacement < -0.15 and migration >= 0.0
        else:
            if direction == 1:
                acceptanceBroken: bool = not aboveFair and (not acceptingAbove)
                pressureReversed: bool = migration <= -stallThreshold
                resetDetected = acceptanceBroken and pressureReversed
            else:
                acceptanceBroken: bool = not belowFair and (not acceptingBelow)
                pressureReversed: bool = migration >= stallThreshold
                resetDetected = acceptanceBroken and pressureReversed

        return resetDetected

    def computeLevels(isLong: bool, isReaction: bool, atr: float):
        direction: float = 1.0 if isLong else -1.0

        computedTargetOne: float = close + direction * t1AtrInput * atr
        computedTargetTwo: float = close + direction * t2AtrInput * atr

        computedInvalidation: float = (low - invalidationAtrInput * atr if isLong else high + invalidationAtrInput * atr) if isReaction else fairPrice

        return (computedTargetOne, computedTargetTwo, computedInvalidation)

    def tradeColor(trade: Trade):
        return COLOR_UP_REACTION if trade.signalType == 'LONG_REACTION' else COLOR_DOWN_REACTION if trade.signalType == 'SHORT_REACTION' else COLOR_UP_TRAVEL if trade.signalType == 'LONG_CONT' else COLOR_DOWN_TRAVEL

    def createPath(trade: Trade):
        direction: float = 1.0 if trade.isLong else -1.0
        totalTravel: float = math.abs(trade.targetTwo - trade.entry)

        pressureDrive: float = clamp(math.abs(migration) * 7.0, 0.0, 1.0)
        directionalDrive: float = clamp(math.abs(displacement) * 0.12, 0.0, 0.5)

        stateDrive: float = 0.35 if continuationLong or continuationShort else 0.22 if building else -0.18 if reversing else 0.0

        routeDrive: float = clamp(pressureDrive + directionalDrive + stateDrive, -0.25, 1.0)
        routeCurve: float = direction * totalTravel * 0.18 * routeDrive

        pointOne: float = trade.entry + direction * totalTravel * 0.3 + routeCurve * 0.45
        pointTwo: float = trade.entry + direction * totalTravel * 0.65 + routeCurve

        uncertainty: float = 0.34 if exhaustion or reversing else 0.27 if building else 0.2 if pressureUp or pressureDown else 0.24

        corridor: float = math.max(atrValue * uncertainty, syminfo.mintick * 12.0)

        upperEntry: float = trade.entry + corridor
        upperOne: float = pointOne + corridor * 0.82
        upperTwo: float = pointTwo + corridor * 0.64
        upperThree: float = trade.targetTwo + corridor * 0.38

        lowerEntry: float = trade.entry - corridor
        lowerOne: float = pointOne - corridor * 0.82
        lowerTwo: float = pointTwo - corridor * 0.64
        lowerThree: float = trade.targetTwo - corridor * 0.38

        x0: int = trade.sigBar
        x1: int = trade.sigBar + 4
        x2: int = trade.sigBar + 9
        x3: int = trade.sigBar + 16

        pathColor: Color = tradeColor(trade)

        trade.pathUpperOne = line.new(x0, upperEntry, x1, upperOne, color=color.new(pathColor, 78), width=1, force_overlay=True)
        trade.pathUpperTwo = line.new(x1, upperOne, x2, upperTwo, color=color.new(pathColor, 78), width=1, force_overlay=True)
        trade.pathUpperThree = line.new(x2, upperTwo, x3, upperThree, color=color.new(pathColor, 82), width=1, force_overlay=True)

        trade.pathLowerOne = line.new(x0, lowerEntry, x1, lowerOne, color=color.new(pathColor, 78), width=1, force_overlay=True)
        trade.pathLowerTwo = line.new(x1, lowerOne, x2, lowerTwo, color=color.new(pathColor, 78), width=1, force_overlay=True)
        trade.pathLowerThree = line.new(x2, lowerTwo, x3, lowerThree, color=color.new(pathColor, 82), width=1, force_overlay=True)

        trade.pathCenterOne = line.new(x0, trade.entry, x1, pointOne, color=color.new(pathColor, 22), width=2, force_overlay=True)
        trade.pathCenterTwo = line.new(x1, pointOne, x2, pointTwo, color=color.new(pathColor, 22), width=2, force_overlay=True)
        trade.pathCenterThree = line.new(x2, pointTwo, x3, trade.targetTwo, color=color.new(pathColor, 16), width=2, force_overlay=True)

        trade.pathFillOne = linefill.new(trade.pathUpperOne, trade.pathLowerOne, color.new(pathColor, 94))
        trade.pathFillTwo = linefill.new(trade.pathUpperTwo, trade.pathLowerTwo, color.new(pathColor, 94))
        trade.pathFillThree = linefill.new(trade.pathUpperThree, trade.pathLowerThree, color.new(pathColor, 96))
        return trade.pathFillThree

    def updatePath(trade: Trade):
        __block_result__ = na
        if not na(trade.pathCenterOne):
            direction: float = 1.0 if trade.isLong else -1.0
            totalTravel: float = math.abs(trade.targetTwo - trade.entry)

            pressureDrive: float = clamp(math.abs(migration) * 7.0, 0.0, 1.0)
            directionalDrive: float = clamp(math.abs(displacement) * 0.12, 0.0, 0.5)

            stateDrive: float = 0.35 if continuationLong or continuationShort else 0.22 if building else -0.18 if reversing else 0.0

            routeDrive: float = clamp(pressureDrive + directionalDrive + stateDrive, -0.25, 1.0)
            routeCurve: float = direction * totalTravel * 0.18 * routeDrive

            pointOne: float = trade.entry + direction * totalTravel * 0.3 + routeCurve * 0.45
            pointTwo: float = trade.entry + direction * totalTravel * 0.65 + routeCurve

            uncertainty: float = 0.34 if exhaustion or reversing else 0.27 if building else 0.2 if pressureUp or pressureDown else 0.24

            corridor: float = math.max(atrValue * uncertainty, syminfo.mintick * 12.0)

            upperEntry: float = trade.entry + corridor
            upperOne: float = pointOne + corridor * 0.82
            upperTwo: float = pointTwo + corridor * 0.64
            upperThree: float = trade.targetTwo + corridor * 0.38

            lowerEntry: float = trade.entry - corridor
            lowerOne: float = pointOne - corridor * 0.82
            lowerTwo: float = pointTwo - corridor * 0.64
            lowerThree: float = trade.targetTwo - corridor * 0.38

            line.set_xy1(trade.pathUpperOne, trade.sigBar, upperEntry)
            line.set_xy2(trade.pathUpperOne, trade.sigBar + 4, upperOne)
            line.set_xy1(trade.pathUpperTwo, trade.sigBar + 4, upperOne)
            line.set_xy2(trade.pathUpperTwo, trade.sigBar + 9, upperTwo)
            line.set_xy1(trade.pathUpperThree, trade.sigBar + 9, upperTwo)
            line.set_xy2(trade.pathUpperThree, trade.sigBar + 16, upperThree)

            line.set_xy1(trade.pathLowerOne, trade.sigBar, lowerEntry)
            line.set_xy2(trade.pathLowerOne, trade.sigBar + 4, lowerOne)
            line.set_xy1(trade.pathLowerTwo, trade.sigBar + 4, lowerOne)
            line.set_xy2(trade.pathLowerTwo, trade.sigBar + 9, lowerTwo)
            line.set_xy1(trade.pathLowerThree, trade.sigBar + 9, lowerTwo)
            line.set_xy2(trade.pathLowerThree, trade.sigBar + 16, lowerThree)

            line.set_xy1(trade.pathCenterOne, trade.sigBar, trade.entry)
            line.set_xy2(trade.pathCenterOne, trade.sigBar + 4, pointOne)
            line.set_xy1(trade.pathCenterTwo, trade.sigBar + 4, pointOne)
            line.set_xy2(trade.pathCenterTwo, trade.sigBar + 9, pointTwo)
            line.set_xy1(trade.pathCenterThree, trade.sigBar + 9, pointTwo)
            __block_result__ = line.set_xy2(trade.pathCenterThree, trade.sigBar + 16, trade.targetTwo)
        return __block_result__

    def deletePath(trade: Trade):
        __block_result_1__ = na
        if not na(trade.pathUpperOne):
            line.delete(trade.pathUpperOne)
            line.delete(trade.pathUpperTwo)
            line.delete(trade.pathUpperThree)
            line.delete(trade.pathLowerOne)
            line.delete(trade.pathLowerTwo)
            line.delete(trade.pathLowerThree)
            line.delete(trade.pathCenterOne)
            line.delete(trade.pathCenterTwo)
            line.delete(trade.pathCenterThree)
            linefill.delete(trade.pathFillOne)
            linefill.delete(trade.pathFillTwo)
            __block_result_1__ = linefill.delete(trade.pathFillThree)
        return __block_result_1__

    def drawTrade(trade: Trade):
        directionColor: Color = tradeColor(trade)

        primaryReaction: bool = trade.signalType == 'LONG_REACTION' or trade.signalType == 'SHORT_REACTION'

        trade.entryLine = line.new(trade.sigBar, trade.entry, trade.sigBar + 1, trade.entry, color=directionColor, width=3, style=line.style_solid, force_overlay=True)

        trade.targetOneLine = line.new(trade.sigBar, trade.targetOne, trade.sigBar + 1, trade.targetOne, color=COLOR_PATH_LEVEL_ONE, width=2, style=line.style_solid, force_overlay=True)

        trade.targetTwoLine = line.new(trade.sigBar, trade.targetTwo, trade.sigBar + 1, trade.targetTwo, color=COLOR_PATH_LEVEL_TWO, width=2, style=line.style_solid, force_overlay=True)

        trade.invalidationLine = line.new(trade.sigBar, trade.invalidation, trade.sigBar + 1, trade.invalidation, color=COLOR_INVALIDATION, width=3, style=line.style_solid, force_overlay=True)

        markerText: str = 'REACTION LONG' if trade.signalType == 'LONG_REACTION' else 'REACTION SHORT' if trade.signalType == 'SHORT_REACTION' else 'CONTINUATION LONG' if trade.signalType == 'LONG_CONT' else 'CONTINUATION SHORT'

        markerPrice: float = trade.invalidation - fairHalf * 0.35 if trade.isLong else trade.invalidation + fairHalf * 0.35

        trade.signalLabel = label.new(trade.sigBar, markerPrice, markerText, color=directionColor if primaryReaction else color.new(directionColor, 28), textcolor=COLOR_WHITE, style=label.style_label_up if trade.isLong else label.style_label_down, size=size.small if primaryReaction else size.tiny, force_overlay=True)

        if showPathInput:
            createPath(trade)

        return alert(buildAlertMessage('NEW SIGNAL', trade.signalType, trade.entry), alert.freq_once_per_bar_close)

    def freezeTrade(trade: Trade, closingBar: int):
        trade.closeBar = closingBar
        trade.active = False

        line.set_x2(trade.entryLine, closingBar)
        line.set_x2(trade.targetOneLine, closingBar)
        line.set_x2(trade.targetTwoLine, closingBar)
        return line.set_x2(trade.invalidationLine, closingBar)

    def deleteTradeVisuals(trade: Trade):
        if not na(trade.entryLine):
            line.delete(trade.entryLine)

        if not na(trade.targetOneLine):
            line.delete(trade.targetOneLine)

        if not na(trade.targetTwoLine):
            line.delete(trade.targetTwoLine)

        if not na(trade.invalidationLine):
            line.delete(trade.invalidationLine)

        if not na(trade.signalLabel):
            label.delete(trade.signalLabel)

        return deletePath(trade)

    def pruneHistory():
        __block_result_2__ = na
        while array.size(historicalTrades) > maxHistoryInput:
            oldTrade: Trade = array.shift(historicalTrades)

            if not na(oldTrade.entryLine):
                line.delete(oldTrade.entryLine)

            if not na(oldTrade.targetOneLine):
                line.delete(oldTrade.targetOneLine)

            if not na(oldTrade.targetTwoLine):
                line.delete(oldTrade.targetTwoLine)

            if not na(oldTrade.invalidationLine):
                line.delete(oldTrade.invalidationLine)

            if not na(oldTrade.signalLabel):
                label.delete(oldTrade.signalLabel)

            __block_result_2__ = deletePath(oldTrade)
        return __block_result_2__

    if barstate.isconfirmed and engineReady:
        tradeClosedThisBar = False

        memoryExpired: bool = failureMemoryExpired()
        behaviourReset: bool = failureBehaviourReset()

        if failureMemoryActive and (memoryExpired or behaviourReset):
            failureMemoryActive = False
            failureMemoryBar = na

            failedDisplacement = na
            failedMigration = na
            failedEfficiency = na
            failedSpeedRatio = na
            failedDepth = na
            failedVolumeRatio = na
            failedPressure = na
            failedRangeRatio = na

            failedSignalFamily = 0

        if failureCount > 0 and (not na(lastFailureBar)) and (bar_index - lastFailureBar > FAILURE_MEMORY_LIMIT):
            failureCount = 0
            lastFailureBar = na

        if signalEventLocked:
            signalReset: bool = signalBehaviourReset(signalEventDirection, signalEventFamily)

            if signalReset:
                signalEventLocked = False
                signalEventDirection = 0
                signalEventFamily = 0

        if rearmPending and behaviourReset:
            rearmReady = True
            rearmPending = False

        if not na(activeTrade) and activeTrade.active:
            longTrade: bool = activeTrade.isLong

            invalidationHit: bool = False
            targetTwoHit: bool = False

            if longTrade:
                invalidationHit = low <= activeTrade.invalidation
                targetTwoHit = high >= activeTrade.targetTwo
            else:
                invalidationHit = high >= activeTrade.invalidation
                targetTwoHit = low <= activeTrade.targetTwo

            if invalidationHit or targetTwoHit:
                tradeSucceeded: bool = targetTwoHit and (not invalidationHit)

                freezeTrade(activeTrade, bar_index)
                deletePath(activeTrade)

                if showHistoryInput:
                    array.push(historicalTrades, activeTrade)
                    pruneHistory()
                else:
                    deleteTradeVisuals(activeTrade)

                if tradeSucceeded:
                    failureMemoryActive = False
                    failureMemoryBar = na
                    failureCount = 0
                    lastFailureBar = na

                    failedDisplacement = na
                    failedMigration = na
                    failedEfficiency = na
                    failedSpeedRatio = na
                    failedDepth = na
                    failedVolumeRatio = na
                    failedPressure = na
                    failedRangeRatio = na

                    failedSignalFamily = 0

                    rearmReady = True
                    rearmPending = False

                    alert(buildAlertMessage('TARGET REACHED', activeTrade.signalType, activeTrade.targetTwo), alert.freq_once_per_bar_close)
                else:
                    failureMemoryActive = True
                    failureMemoryBar = bar_index
                    lastFailureBar = bar_index

                    failureCount = math.min(failureCount + 1, FAILURE_MAX_COUNT)

                    failedDirectionLong = activeTrade.isLong

                    if activeTrade.signalType == 'LONG_REACTION' or activeTrade.signalType == 'SHORT_REACTION':
                        failedSignalFamily = 1
                    else:
                        failedSignalFamily = 2

                    failedDisplacement = math.abs(displacement)
                    failedMigration = migration

                    if activeTrade.isLong:
                        failedEfficiency = meanDirectionalEfficiencyLong
                        failedDepth = depthBelowFair
                    else:
                        failedEfficiency = meanDirectionalEfficiencyShort
                        failedDepth = depthAboveFair

                    failedSpeedRatio = speedRatio
                    failedVolumeRatio = volumeRatio
                    failedPressure = pressureNow
                    failedRangeRatio = safeDiv(barRange, atrValue, 1.0)

                    rearmReady = False
                    rearmPending = True

                    alert(buildAlertMessage('INVALIDATED', activeTrade.signalType, activeTrade.invalidation), alert.freq_once_per_bar_close)

                activeTrade = na
                tradeClosedThisBar = True
            else:
                extensionLong: bool = longContinuationGate and continuationLong and longTrade and continuationSignalsEnabled
                extensionShort: bool = shortContinuationGate and continuationShort and (not longTrade) and continuationSignalsEnabled

                if (extensionLong or extensionShort) and activeTrade.extensionCount < MAX_TARGET_EXTENSIONS:
                    direction: float = 1.0 if longTrade else -1.0
                    newTargetTwo: float = activeTrade.targetTwo + direction * t1AtrInput * atrValue

                    activeTrade.targetTwo = newTargetTwo
                    activeTrade.extensionCount = activeTrade.extensionCount + 1

                    line.set_y1(activeTrade.targetTwoLine, newTargetTwo)
                    line.set_y2(activeTrade.targetTwoLine, newTargetTwo)

                if showPathInput:
                    updatePath(activeTrade)

        if na(activeTrade) and rearmReady and (not tradeClosedThisBar):
            adaptiveDisplacementThreshold: float = displacementThreshold
            adaptiveEfficiencyThreshold: float = directionalEfficiencyThreshold
            adaptiveSpeedThreshold: float = speedThreshold
            adaptiveDepthThreshold: float = depthThreshold
            adaptiveVolumeThreshold: float = volumeThresholdSensitivity

            if failureCount > 0:
                adaptiveDisplacementThreshold = displacementThreshold + failureCount * 0.08
                adaptiveEfficiencyThreshold = directionalEfficiencyThreshold + failureCount * 0.03
                adaptiveSpeedThreshold = speedThreshold + failureCount * 0.04
                adaptiveDepthThreshold = depthThreshold + failureCount * 0.05
                adaptiveVolumeThreshold = volumeThresholdSensitivity + failureCount * 0.05

            blockThreshold: float = 0.74 - failureCount * 0.06

            longReactionMemoryBlock: bool = False
            longContinuationMemoryBlock: bool = False
            shortReactionMemoryBlock: bool = False
            shortContinuationMemoryBlock: bool = False

            if failureMemoryActive and failedDirectionLong:
                simLong: float = currentFailureSimilarity(True)
                if simLong >= blockThreshold:
                    if failedSignalFamily == 1:
                        longReactionMemoryBlock = True
                    else:
                        longContinuationMemoryBlock = True

            if failureMemoryActive and (not failedDirectionLong):
                simShort: float = currentFailureSimilarity(False)
                if simShort >= blockThreshold:
                    if failedSignalFamily == 1:
                        shortReactionMemoryBlock = True
                    else:
                        shortContinuationMemoryBlock = True

            adaptiveLongReactionGate: bool = longReactionGate
            adaptiveShortReactionGate: bool = shortReactionGate
            adaptiveLongContinuationGate: bool = longContinuationGate
            adaptiveShortContinuationGate: bool = shortContinuationGate

            if math.abs(displacement) < adaptiveDisplacementThreshold:
                adaptiveLongReactionGate = False
                adaptiveShortReactionGate = False

            if meanDirectionalEfficiencyLong < adaptiveEfficiencyThreshold:
                adaptiveLongReactionGate = False

            if meanDirectionalEfficiencyShort < adaptiveEfficiencyThreshold:
                adaptiveShortReactionGate = False

            if speedRatio < adaptiveSpeedThreshold:
                adaptiveLongReactionGate = False
                adaptiveShortReactionGate = False
                adaptiveLongContinuationGate = False
                adaptiveShortContinuationGate = False

            if volumeRatio < adaptiveVolumeThreshold:
                adaptiveLongReactionGate = False
                adaptiveShortReactionGate = False
                adaptiveLongContinuationGate = False
                adaptiveShortContinuationGate = False

            if depthBelowFair < adaptiveDepthThreshold:
                adaptiveLongReactionGate = False

            if depthAboveFair < adaptiveDepthThreshold:
                adaptiveShortReactionGate = False

            if longReactionMemoryBlock:
                adaptiveLongReactionGate = False

            if longContinuationMemoryBlock:
                adaptiveLongContinuationGate = False

            if shortReactionMemoryBlock:
                adaptiveShortReactionGate = False

            if shortContinuationMemoryBlock:
                adaptiveShortContinuationGate = False

            candidateLongReaction: bool = adaptiveLongReactionGate and pressureUp and reactionSignalsEnabled
            candidateShortReaction: bool = adaptiveShortReactionGate and pressureDown and reactionSignalsEnabled
            candidateLongContinuation: bool = adaptiveLongContinuationGate and continuationLong and continuationSignalsEnabled
            candidateShortContinuation: bool = adaptiveShortContinuationGate and continuationShort and continuationSignalsEnabled

            longReactionBlocked: bool = signalEventLocked and signalEventDirection == 1 and (signalEventFamily == 1)
            shortReactionBlocked: bool = signalEventLocked and signalEventDirection == -1 and (signalEventFamily == 1)
            longContinuationBlocked: bool = signalEventLocked and signalEventDirection == 1 and (signalEventFamily == 2)
            shortContinuationBlocked: bool = signalEventLocked and signalEventDirection == -1 and (signalEventFamily == 2)

            signalType: str = ""
            signalLong: bool = False

            if candidateLongReaction and (not longReactionBlocked):
                signalType = "LONG_REACTION"
                signalLong = True
            elif candidateShortReaction and (not shortReactionBlocked):
                signalType = "SHORT_REACTION"
                signalLong = False
            elif candidateLongContinuation and (not longContinuationBlocked):
                signalType = "LONG_CONT"
                signalLong = True
            elif candidateShortContinuation and (not shortContinuationBlocked):
                signalType = "SHORT_CONT"
                signalLong = False

            if signalType != '':
                reactionSignal: bool = signalType == 'LONG_REACTION' or signalType == 'SHORT_REACTION'

                newTargetOne, newTargetTwo, newInvalidation = computeLevels(signalLong, reactionSignal, atrValue)

                newTrade: Trade = Trade(bar_index, na, signalLong, signalType, close, newTargetOne, newTargetTwo, newInvalidation, True, 0, na, na, na, na, na, na, na, na, na, na, na, na, na, na, na, na, na)

                drawTrade(newTrade)

                activeTrade = newTrade
                rearmPending = False

                signalEventLocked = True
                signalEventDirection = 1 if signalLong else -1
                signalEventFamily = 1 if reactionSignal else 2

    if barstate.islast:
        label.delete(liveTargetOneLabel)
        label.delete(liveTargetTwoLabel)
        label.delete(liveEntryLabel)
        label.delete(liveInvalidationLabel)

        liveTargetOneLabel = na
        liveTargetTwoLabel = na
        liveEntryLabel = na
        liveInvalidationLabel = na

        if not na(activeTrade) and activeTrade.active:
            directionColor: Color = tradeColor(activeTrade)
            labelBar: int = bar_index + 2

            line.set_x2(activeTrade.entryLine, labelBar)
            line.set_x2(activeTrade.targetOneLine, labelBar)
            line.set_x2(activeTrade.targetTwoLine, labelBar)
            line.set_x2(activeTrade.invalidationLine, labelBar)

            liveTargetTwoLabel = label.new(labelBar, activeTrade.targetTwo, 'PATH LEVEL 2', color=COLOR_PATH_LEVEL_TWO, textcolor=COLOR_WHITE, style=label.style_label_left, size=size.small, force_overlay=True)

            liveTargetOneLabel = label.new(labelBar, activeTrade.targetOne, 'PATH LEVEL 1', color=COLOR_PATH_LEVEL_ONE, textcolor=COLOR_WHITE, style=label.style_label_left, size=size.small, force_overlay=True)

            liveEntryLabel = label.new(labelBar, activeTrade.entry, 'ENTRY', color=directionColor, textcolor=COLOR_WHITE, style=label.style_label_left, size=size.small, force_overlay=True)

            liveInvalidationLabel = label.new(labelBar, activeTrade.invalidation, 'INVALIDATION', color=COLOR_INVALIDATION, textcolor=COLOR_WHITE, style=label.style_label_left, size=size.small, force_overlay=True)

    marketState: str = 'EXHAUSTION' if exhaustion else 'SHIFT' if reversing else 'BUILDING' if building else 'TRAVEL' if continuationLong and aboveFair else 'TRAVEL' if continuationShort and belowFair else 'MOVING UP' if migratingUp else 'MOVING DOWN' if migratingDown else 'NEUTRAL'

    pathState: str = 'UP OPEN' if pressureUp else 'DOWN OPEN' if pressureDown else 'WAIT'

    locationState: str = 'ABOVE FAIR' if aboveFair else 'BELOW FAIR' if belowFair else 'AT FAIR'

    currentStateColor: Color = stateColor(marketState)

    bandAccent: Color = COLOR_EXHAUSTION if exhaustion else COLOR_SHIFT if reversing else COLOR_UP_REACTION if pressureUp else COLOR_DOWN_REACTION if pressureDown else COLOR_NEUTRAL

    bandInnerHalf: float = fairHalf * 0.58
    bandInnerUpper: float = fairPrice + bandInnerHalf
    bandInnerLower: float = fairPrice - bandInnerHalf

    bandPressure: float = clamp(math.abs(migration) * 8.0, 0.0, 1.0)

    outerTransparency: int = 92 - cast_int(bandPressure * 10.0)
    innerTransparency: int = 86 - cast_int(bandPressure * 14.0)

    plotBandCore = plot(fairPrice if showFairBandInput and chart.is_standard else na, 'Reaction Core', color.new(bandAccent, 8), 2, force_overlay=True, display=display.all - display.price_scale)

    plotBandInnerUpper = plot(bandInnerUpper if showFairBandInput and chart.is_standard else na, 'Reaction Inner Upper', color.new(bandAccent, 48), 1, force_overlay=True, display=display.all - display.price_scale)

    plotBandInnerLower = plot(bandInnerLower if showFairBandInput and chart.is_standard else na, 'Reaction Inner Lower', color.new(bandAccent, 48), 1, force_overlay=True, display=display.all - display.price_scale)

    plotBandOuterUpper = plot(fairUpper if showFairBandInput and chart.is_standard else na, 'Reaction Outer Upper', color.new(bandAccent, 72), 1, force_overlay=True, display=display.all - display.price_scale)

    plotBandOuterLower = plot(fairLower if showFairBandInput and chart.is_standard else na, 'Reaction Outer Lower', color.new(bandAccent, 72), 1, force_overlay=True, display=display.all - display.price_scale)

    fill(plotBandOuterUpper, plotBandInnerUpper, color.new(bandAccent, outerTransparency))
    fill(plotBandInnerUpper, plotBandInnerLower, color.new(bandAccent, innerTransparency))
    fill(plotBandInnerLower, plotBandOuterLower, color.new(bandAccent, outerTransparency))

    rawField: float = migration * MIGRATION_SCALE
    fieldCore: float = clamp(rawField, -5.5, 5.5)

    fieldEnergy: float = clamp(math.abs(fieldCore) * 0.75 + math.max(speedRatio - 1.0, 0.0) * 0.55, 0.15, 2.5)
    fieldHalfWidth: float = clamp(0.32 + fieldEnergy * 0.28, 0.32, 1.45)

    fieldUpper: float = clamp(fieldCore + fieldHalfWidth, -6.0, 6.0)
    fieldLower: float = clamp(fieldCore - fieldHalfWidth, -6.0, 6.0)

    reactionFieldColor: Color = COLOR_EXHAUSTION if exhaustion else COLOR_SHIFT if reversing else COLOR_UP_REACTION if fieldCore > 0.0 else COLOR_DOWN_REACTION if fieldCore < 0.0 else COLOR_NEUTRAL

    plotFieldUpper = plot(fieldUpper if chart.is_standard else na, 'Reaction Field Upper', color.new(reactionFieldColor, 100), 1, display=display.pane)
    plotFieldLower = plot(fieldLower if chart.is_standard else na, 'Reaction Field Lower', color.new(reactionFieldColor, 100), 1, display=display.pane)

    fill(plotFieldUpper, plotFieldLower, color.new(reactionFieldColor, 89))

    plot(fieldCore if chart.is_standard else na, 'Reaction Spine', color.new(reactionFieldColor, 0), linewidth=2)
    plot(fieldCore * 0.48 if chart.is_standard else na, 'Reaction Flow', color.new(reactionFieldColor, 72), linewidth=1, display=display.pane)

    plot(0.0 if chart.is_standard else na, 'Reaction Centre', color.new(COLOR_NEUTRAL, 68), style=plot.style_line, display=display.pane)

    transitionPulse: bool = (reversing or exhaustion) and chart.is_standard

    plotshape(fieldCore if transitionPulse else na, title='Reaction Transition', style=shape.circle, location=location.absolute, color=color.new(reactionFieldColor, 0), size=size.tiny)

    dashboard: Persistent[Table] = table.new(dashboardPosition(dashboardPositionInput), 2, 5, bgcolor=COLOR_PANEL, frame_color=COLOR_PANEL_BORDER, frame_width=1, border_color=COLOR_PANEL_BORDER, border_width=1, force_overlay=True)

    if barstate.islast:
        if showDashboardInput and chart.is_standard:
            tradeActive: bool = not na(activeTrade) and activeTrade.active

            tradeStateText: str = ('REACTION LONG' if activeTrade.signalType == 'LONG_REACTION' else 'REACTION SHORT' if activeTrade.signalType == 'SHORT_REACTION' else 'CONTINUATION LONG' if activeTrade.signalType == 'LONG_CONT' else 'CONTINUATION SHORT') if tradeActive else 'WAITING'

            tradeStateColor: Color = tradeColor(activeTrade) if tradeActive else COLOR_NEUTRAL

            levelText: str = 'ENTRY  ' + string.tostring(activeTrade.entry, format.mintick) + '\nPATH LEVEL 1  ' + string.tostring(activeTrade.targetOne, format.mintick) + '\nPATH LEVEL 2  ' + string.tostring(activeTrade.targetTwo, format.mintick) + '\nINVALIDATION  ' + string.tostring(activeTrade.invalidation, format.mintick) if tradeActive else 'No active setup'

            table.cell(dashboard, 0, 0, 'REACTION PATH', bgcolor=COLOR_PANEL, text_color=COLOR_WHITE, text_size=dashboardTextSize(dashboardSizeInput), text_halign=text.align_left)

            table.cell(dashboard, 1, 0, syminfo.prefix + ':' + syminfo.ticker + ' | ' + timeframe.period, bgcolor=COLOR_PANEL, text_color=COLOR_NEUTRAL, text_size=dashboardTextSize(dashboardSizeInput), text_halign=text.align_right)

            table.cell(dashboard, 0, 1, 'STATE', bgcolor=COLOR_PANEL, text_color=COLOR_NEUTRAL, text_size=dashboardTextSize(dashboardSizeInput), text_halign=text.align_left)

            table.cell(dashboard, 1, 1, marketState, bgcolor=COLOR_PANEL, text_color=currentStateColor, text_size=dashboardTextSize(dashboardSizeInput), text_halign=text.align_right)

            table.cell(dashboard, 0, 2, 'PATH', bgcolor=COLOR_PANEL, text_color=COLOR_NEUTRAL, text_size=dashboardTextSize(dashboardSizeInput), text_halign=text.align_left)

            table.cell(dashboard, 1, 2, pathState, bgcolor=COLOR_PANEL, text_color=reactionFieldColor, text_size=dashboardTextSize(dashboardSizeInput), text_halign=text.align_right)

            table.cell(dashboard, 0, 3, 'LOCATION', bgcolor=COLOR_PANEL, text_color=COLOR_NEUTRAL, text_size=dashboardTextSize(dashboardSizeInput), text_halign=text.align_left)

            table.cell(dashboard, 1, 3, locationState, bgcolor=COLOR_PANEL, text_color=COLOR_WHITE, text_size=dashboardTextSize(dashboardSizeInput), text_halign=text.align_right)

            table.cell(dashboard, 0, 4, 'TRADE' if tradeActive else 'STATUS', bgcolor=COLOR_PANEL, text_color=COLOR_NEUTRAL, text_size=dashboardTextSize(dashboardSizeInput), text_halign=text.align_left)

            table.cell(dashboard, 1, 4, tradeStateText + '\n' + levelText if tradeActive else 'WAITING\nNo active setup', bgcolor=COLOR_PANEL, text_color=tradeStateColor, text_size=dashboardTextSize(dashboardSizeInput), text_halign=text.align_right)
        else:
            table.clear(dashboard, 0, 0, 1, 4)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)