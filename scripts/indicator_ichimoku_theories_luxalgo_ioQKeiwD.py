"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barstate, chart, close, color, fill, high, input,
    label, last_bar_index, line, location, low, math, na, plot, plotshape, polyline, script, shape,
    string, ta, time, xloc
)
from pynecore.types import Color, Label, Line, NA, Persistent
from pynecore.types.chart import ChartPoint


@udt
class swingPoint:
    barTime: int = na(int)
    barIndex: int = na(int)
    priceLevel: float = na(float)
    leg: int = na(int)


@udt
class timeCycle:
    firstBarTime: int = na(int)
    firstBarIndex: int = na(int)
    lastBarTime: int = na(int)
    lastBarIndex: int = na(int)
    cycleLine: Line = na(Line)
    cycleLabel: Label = na(Label)


@udt
class wave:
    points: list[ChartPoint] = na(list)
    tag: str = na(str)
    bias: str = na(str)
    waveLabel: Label = na(Label)
    line1: Line = na(Line)
    line2: Line = na(Line)


@udt
class priceTarget:
    targetLine: Line = na(Line)
    targetLabel: Label = na(Label)


KIHON: str = 'KIHON SUCHI'
TAITO: str = 'TAITO SUCHI'
HIGHS: str = 'HIGHS'
LOWS: str = 'LOWS'
SWINGS: str = 'SWINGS'
TENKAN: str = 'TENKAN CROSS'
KIJUN: str = 'KIJUN CROSS'
KUMO: str = 'KUMO CHANGE'
WAVE: str = 'WAVES'
WAVE_I: str = 'WAVE I'
WAVE_V: str = 'WAVE V'
WAVE_N: str = 'WAVE N'
WAVE_P: str = 'WAVE P'
WAVE_Y: str = 'WAVE Y'
WAVE_W: str = 'WAVE W'
EN_SPACE: str = ' '
EM_SPACE: str = ' '
FOUR_PER_EM_SPACE: str = ' '
SIX_PER_EM_SPACE: str = ' '
HAIR_SPACE: str = ' '
ICHIMOKU_GROUP: str = 'ICHIMOKU KINKŌ HYŌ'
TIME_GROUP: str = 'TIME THEORY'
WAVE_GROUP: str = 'WAVE THEORY'
PRICE_GROUP: str = 'PRICE THEORY'
showPivotMarksTooltip: str = 'Enable/Disable points on swing highs and swing lows.'
pivotLengthTooltip: str = 'Number of candles to confirm a swing high or swing low. A higher number detects larger swings.'
showIchimokuLinesTooltip: str = 'Enable/Disable the 5 Ichimoku lines: kijun sen, tenkan sen, senkou span A & B and chikou span.'
showIchimokuKumoTooltip: str = 'Enable/Disable the Kumo (cloud). The Kumo is formed by 2 lines: Senkou Span A and Senkou Span B.'
tenkanSenLengthTooltip: str = 'Number of candles for Tenkan Sen calculation.'
kinjuSenLengthTooltip: str = 'Number of candles for the Kijun Sen calculation.'
senkouSpanBLengthTooltip: str = 'Number of candles for Senkou Span B calculation.'
ichimokunOffsetTooltip: str = 'Number of candles for Chikou and Senkou Span calculation. Chikou Span is plotted in the past, Senkou Span A & B in the future.'
showTimeForecastTooltip: str = 'Enable/Disable time cycle forecast vertical lines. Disable for better performance.'
timePatternTooltip: str = 'Choose between two patterns: Kihon Suchi (basic numbers) or Taito Suchi (equal numbers).'
timeForecastAnchorTooltip: str = 'Number of time cycles in the past to anchor the time cycle forecast. The larger the number, the deeper in the past the anchor will be.'
timeCycleModeTooltip: str = 'Choose from 7 time cycle detection modes: Tenkan Sen cross, Kijun Sen cross, Kumo change between bullish & bearish, swing highs only, swing lows only, both swing highs & lows and wave detection.'
waveCyleTooltip: str = 'Choose which type of wave to detect from 6 different wave types when time cycle mode is set to WAVES.'
showTimeCyclesTooltip: str = 'Enable/Disable time cycle horizontal lines. Disable for better performance.'
maximumTimeCyclesTooltip: str = 'Maximum number of time cycles to display.'
basicWavesTooltip: str = 'Enable/Disable display of basic waves, all at once or one at a time. Disable for better performance.'
complexWavesTooltip: str = 'Enable/Disable complex wave display, all at once or one by one. Disable for better performance.'
overlappingWavesTooltip: str = 'Enable/Disable display of waves ending on the same swing point.'
maximumWavesTooltip: str = 'Maximum number of waves to display.'
basicTargetsTooltip: str = 'Enable/Disable horizontal price target lines. Disable for better performance.'
extendedTargetsTooltip: str = 'Enable/Disable extended price target horizontal lines. Disable for better performance.'


@script.indicator('Ichimoku Theories [LuxAlgo]', 'LuxAlgo - Ichimoku Theories', overlay=True, max_lines_count=500, max_labels_count=500, max_polylines_count=100, na_bool=True)
def main(
    showPivotMarksInput=input.bool(True, 'Show Swing Highs & Lows', group='', tooltip=showPivotMarksTooltip),
    pivotLengthInput=input.int(10, 'Swing Length', group='', tooltip=pivotLengthTooltip, minval=1),
    showIchimokuLinesInput=input.bool(True, 'Show Lines', group=ICHIMOKU_GROUP, tooltip=showIchimokuLinesTooltip),
    showIchimokuKumoInput=input.bool(True, 'Show Kumo', group=ICHIMOKU_GROUP, tooltip=showIchimokuKumoTooltip),
    tenkanSenLengthInput=input.int(9, 'Tenkan Sen Length', group=ICHIMOKU_GROUP, tooltip=tenkanSenLengthTooltip),
    kinjuSenLengthInput=input.int(26, 'Kinjun Sen Length', group=ICHIMOKU_GROUP, tooltip=kinjuSenLengthTooltip),
    senkouSpanBLengthInput=input.int(52, 'Senkou Span B Length', group=ICHIMOKU_GROUP, tooltip=senkouSpanBLengthTooltip),
    ichimokuOffsetInput=input.int(26, 'Chikou & Senkou Offset', group=ICHIMOKU_GROUP, tooltip=ichimokunOffsetTooltip),
    showTimeForecastInput=input.bool(True, 'Show Time Cycle Forecast', group=TIME_GROUP, tooltip=showTimeForecastTooltip),
    timePatternInput=input.string(KIHON, 'Forecast Pattern', group=TIME_GROUP, tooltip=timePatternTooltip, options=(KIHON, TAITO)),
    timeForecastAnchorInput=input.int(1, 'Anchor forecast on last X time cycle', group=TIME_GROUP, tooltip=timeForecastAnchorTooltip, minval=1),
    timeCycleModeInput=input.string(SWINGS, 'Time Cycle Mode', group=TIME_GROUP, tooltip=timeCycleModeTooltip, options=(TENKAN, KIJUN, KUMO, HIGHS, LOWS, SWINGS, WAVE)),
    waveCyleInput=input.string(WAVE_I, 'Wave Cycle', group=TIME_GROUP, tooltip=waveCyleTooltip, options=(WAVE_I, WAVE_V, WAVE_N, WAVE_P, WAVE_Y, WAVE_W)),
    showTimeCyclesInput=input.bool(True, 'Show Time Cycles', group=TIME_GROUP, tooltip=showTimeCyclesTooltip),
    maximumTimeCyclesInput=input.int(10, 'Show last X time cycles', group=TIME_GROUP, tooltip=maximumTimeCyclesTooltip, minval=1),
    showBasicWavesInput=input.bool(True, 'Basic Waves:' + EN_SPACE + EM_SPACE, group=WAVE_GROUP, tooltip='', inline='basic waves'),
    showWaveIInput=input.bool(False, 'I', group=WAVE_GROUP, tooltip='', inline='basic waves'),
    waveIColorInput=input.color(color.new('#E91E63'), FOUR_PER_EM_SPACE, group=WAVE_GROUP, tooltip='', inline='basic waves'),
    showWaveVInput=input.bool(False, 'V', group=WAVE_GROUP, tooltip='', inline='basic waves'),
    waveVColorInput=input.color(color.yellow, '', group=WAVE_GROUP, tooltip='', inline='basic waves'),
    showWaveNInput=input.bool(True, 'N', group=WAVE_GROUP, tooltip='', inline='basic waves'),
    waveNColorInput=input.color(color.new('#5B9CF6'), FOUR_PER_EM_SPACE, group=WAVE_GROUP, tooltip=basicWavesTooltip, inline='basic waves'),
    showComplexWavesInput=input.bool(False, 'Complex Waves:', group=WAVE_GROUP, tooltip='', inline='complex waves'),
    showWavePInput=input.bool(True, 'P', group=WAVE_GROUP, tooltip='', inline='complex waves'),
    wavePColorInput=input.color(color.aqua, '', group=WAVE_GROUP, tooltip='', inline='complex waves'),
    showWaveYInput=input.bool(True, 'Y', group=WAVE_GROUP, tooltip='', inline='complex waves'),
    waveYColorInput=input.color(color.new('#FF5D00'), SIX_PER_EM_SPACE, group=WAVE_GROUP, tooltip='', inline='complex waves'),
    showWaveWInput=input.bool(True, 'W', group=WAVE_GROUP, tooltip='', inline='complex waves'),
    waveWColorInput=input.color(color.lime, HAIR_SPACE, group=WAVE_GROUP, tooltip=complexWavesTooltip, inline='complex waves'),
    overlappingWavesInput=input.bool(False, 'Overlapping Waves', group=WAVE_GROUP, tooltip=overlappingWavesTooltip),
    maximumWavesInput=input.int(10, 'Show last X waves', group=WAVE_GROUP, tooltip=maximumWavesTooltip, minval=1),
    showBasicTargetsInput=input.bool(True, 'Basic Targets:' + EM_SPACE + EM_SPACE, group=PRICE_GROUP, tooltip='', inline='basic targets'),
    showTargetVInput=input.bool(True, 'V' + EM_SPACE + EN_SPACE, group=PRICE_GROUP, tooltip='', inline='basic targets'),
    showTargetEInput=input.bool(True, 'E' + EM_SPACE, group=PRICE_GROUP, tooltip='', inline='basic targets'),
    showTargetNInput=input.bool(True, 'N' + EM_SPACE, group=PRICE_GROUP, tooltip='', inline='basic targets'),
    showTargetNTInput=input.bool(True, 'NT', group=PRICE_GROUP, tooltip=basicTargetsTooltip, inline='basic targets'),
    showExtendedTargetsInput=input.bool(False, 'Extended Targets:', group=PRICE_GROUP, tooltip='', inline='extended targets'),
    showTarget2EInput=input.bool(True, '2E' + EM_SPACE, group=PRICE_GROUP, tooltip='', inline='extended targets'),
    showTarget3EInput=input.bool(True, '3E', group=PRICE_GROUP, tooltip=extendedTargetsTooltip, inline='extended targets')
):
    BULLISH_LEG: int = 1
    BEARISH_LEG: int = 0
    BULLISH: str = 'BULLISH'
    BEARISH: str = 'BEARISH'
    GREEN: Color = color.new('#089981')
    RED: Color = color.new('#F23645')
    swingPoints: Persistent[list[swingPoint]] = array.new(0, NA(swingPoint))
    timeCycles: Persistent[list[timeCycle]] = array.new(0, NA(timeCycle))
    timeCyclesForecast: Persistent[list[Line]] = array.new_line()
    waves: Persistent[list[wave]] = array.new(0, NA(wave))
    priceTargets: Persistent[list[priceTarget]] = array.new(0, NA(priceTarget))
    currentLeg: int = na(int)
    newPivot: bool = na(bool)
    pivotLow: bool = na(bool)
    pivotHigh: bool = na(bool)
    tenkanSen: float = na(float)
    kinjuSen: float = na(float)
    chikouSpan: float = close
    senkouSpanA: float = na(float)
    senkouSpanB: float = na(float)
    kumoChange: bool = na(bool)
    kumoColor: Color = na(Color)
    tenkanSenCross: bool = na(bool)
    kinjuSenCross: bool = na(bool)
    extremeHigh: float = na(float)
    extremeLow: float = na(float)
    newExtremeHigh: bool = na(bool)
    newExtremeLow: bool = na(bool)
    lowest: Persistent[float] = na(float)
    legIndex: int = bar_index[pivotLengthInput]
    legHigh: float = high[pivotLengthInput]
    legLow: float = low[pivotLengthInput]
    legTime: int = time[pivotLengthInput]
    atr200: float = ta.atr(200)
    def leg():
        leg__0000003b__: Persistent[int] = 0
        newLegHigh = legHigh > ta.highest(pivotLengthInput)
        newLegLow = legLow < ta.lowest(pivotLengthInput)
        if newLegHigh:
            leg__0000003b__ = BEARISH_LEG
        elif newLegLow:
            leg__0000003b__ = BULLISH_LEG
        return leg__0000003b__

    def startOfNewLeg(leg__0000003d__: int):
        return ta.change(leg__0000003d__) != 0

    def startOfBearishLeg(leg__0000003f__: int):
        return ta.change(leg__0000003f__) == -1

    def startOfBullishLeg(leg__00000041__: int):
        return ta.change(leg__00000041__) == 1

    def average(length: int):
        return math.round_to_mintick(0.5 * (ta.highest(length) + ta.lowest(length)))

    def extremesOnLastXBars(lastXBars: int):
        return (ta.highest(lastXBars) + atr200, ta.lowest(lastXBars) - atr200)

    def chartPoint(point__0000004a__: swingPoint):
        return chart.point.new(point__0000004a__.barTime, point__0000004a__.barIndex, point__0000004a__.priceLevel)

    def gatherWaveI():
        size__ren__ = array.size(swingPoints)
        __block_result__ = na
        if size__ren__ >= 2:
            A = array.get(swingPoints, size__ren__ - 2)
            B = array.get(swingPoints, size__ren__ - 1)
            waveSize = B.barIndex - A.barIndex
            minimumWaveSize = waveSize >= 9
            __block_result_1__ = na
            if minimumWaveSize:
                bias = BEARISH if B.leg == BULLISH_LEG else BULLISH
                __block_result_1__ = wave(array.from_items(chartPoint(A), chartPoint(B)), WAVE_I, bias)
            __block_result__ = __block_result_1__
        return __block_result__

    def gatherWaveV():
        size__ren__ = array.size(swingPoints)
        __block_result_2__ = na
        if size__ren__ >= 3:
            A = array.get(swingPoints, size__ren__ - 3)
            B = array.get(swingPoints, size__ren__ - 2)
            C = array.get(swingPoints, size__ren__ - 1)
            waveSize = C.barIndex - A.barIndex
            minimumWaveSize = waveSize >= 9
            threshold = math.abs(A.priceLevel - B.priceLevel) * 0.2
            isVWave = C.priceLevel >= A.priceLevel - threshold and C.priceLevel <= A.priceLevel + threshold
            __block_result_3__ = na
            if isVWave and minimumWaveSize:
                bias = BEARISH if C.leg == BULLISH_LEG else BULLISH
                __block_result_3__ = wave(array.from_items(chartPoint(A), chartPoint(B), chartPoint(C)), WAVE_V, bias)
            __block_result_2__ = __block_result_3__
        return __block_result_2__

    def gatherWaveN():
        size__ren__ = array.size(swingPoints)
        __block_result_4__ = na
        if size__ren__ >= 4:
            A = array.get(swingPoints, size__ren__ - 4)
            B = array.get(swingPoints, size__ren__ - 3)
            C = array.get(swingPoints, size__ren__ - 2)
            D = array.get(swingPoints, size__ren__ - 1)
            waveSize = D.barIndex - A.barIndex
            minimumWaveSize = waveSize >= 9
            threshold = math.abs(A.priceLevel - B.priceLevel) * 0.2
            isBullishWaveN = A.priceLevel < B.priceLevel and C.priceLevel > A.priceLevel + threshold and (C.priceLevel < B.priceLevel - threshold) and (D.priceLevel > B.priceLevel + threshold)
            isBearishWaveN = A.priceLevel > B.priceLevel and C.priceLevel < A.priceLevel - threshold and (C.priceLevel > B.priceLevel + threshold) and (D.priceLevel < B.priceLevel - threshold)
            isWaveN = isBullishWaveN or isBearishWaveN
            __block_result_5__ = na
            if isWaveN and minimumWaveSize:
                bias = BEARISH if D.leg == BULLISH_LEG else BULLISH
                __block_result_5__ = wave(array.from_items(chartPoint(A), chartPoint(B), chartPoint(C), chartPoint(D)), WAVE_N, bias)
            __block_result_4__ = __block_result_5__
        return __block_result_4__

    def gatherWaveP():
        size__ren__ = array.size(swingPoints)
        __block_result_6__ = na
        if size__ren__ >= 4:
            A = array.get(swingPoints, size__ren__ - 4)
            B = array.get(swingPoints, size__ren__ - 3)
            C = array.get(swingPoints, size__ren__ - 2)
            D = array.get(swingPoints, size__ren__ - 1)
            minimumDistance = math.min(math.abs(A.barIndex - C.barIndex), math.abs(B.barIndex - D.barIndex))
            threshold = 1.25 * minimumDistance
            goodShape = math.abs(A.barIndex - B.barIndex) <= threshold and math.abs(C.barIndex - D.barIndex) <= threshold
            waveSize = D.barIndex - A.barIndex
            minimumWaveSize = waveSize >= 9
            isBullishWaveP = math.max(A.priceLevel, B.priceLevel, C.priceLevel, D.priceLevel) == A.priceLevel and math.min(A.priceLevel, B.priceLevel, C.priceLevel, D.priceLevel) == B.priceLevel and (C.priceLevel > D.priceLevel)
            isBearishWaveP = math.min(A.priceLevel, B.priceLevel, C.priceLevel, D.priceLevel) == A.priceLevel and math.max(A.priceLevel, B.priceLevel, C.priceLevel, D.priceLevel) == B.priceLevel and (C.priceLevel < D.priceLevel)
            isWaveP = isBullishWaveP or isBearishWaveP
            __block_result_7__ = na
            if isWaveP and minimumWaveSize and goodShape:
                bias = BEARISH if D.leg == BULLISH_LEG else BULLISH
                __block_result_7__ = wave(array.from_items(chartPoint(A), chartPoint(B), chartPoint(C), chartPoint(D)), WAVE_P, bias)
            __block_result_6__ = __block_result_7__
        return __block_result_6__

    def gatherWaveY():
        size__ren__ = array.size(swingPoints)
        __block_result_8__ = na
        if size__ren__ >= 4:
            A = array.get(swingPoints, size__ren__ - 4)
            B = array.get(swingPoints, size__ren__ - 3)
            C = array.get(swingPoints, size__ren__ - 2)
            D = array.get(swingPoints, size__ren__ - 1)
            minimumDistance = math.min(math.abs(A.barIndex - C.barIndex), math.abs(B.barIndex - D.barIndex))
            threshold = 1.25 * minimumDistance
            goodShape = math.abs(A.barIndex - B.barIndex) <= threshold and math.abs(C.barIndex - D.barIndex) <= threshold
            waveSize = D.barIndex - A.barIndex
            minimumWaveSize = waveSize >= 9
            isBullishWaveY = math.max(A.priceLevel, B.priceLevel, C.priceLevel, D.priceLevel) == C.priceLevel and math.min(A.priceLevel, B.priceLevel, C.priceLevel, D.priceLevel) == D.priceLevel and (A.priceLevel > B.priceLevel)
            isBearishWaveY = math.min(A.priceLevel, B.priceLevel, C.priceLevel, D.priceLevel) == C.priceLevel and math.max(A.priceLevel, B.priceLevel, C.priceLevel, D.priceLevel) == D.priceLevel and (A.priceLevel < B.priceLevel)
            isWaveY = isBullishWaveY or isBearishWaveY
            __block_result_9__ = na
            if isWaveY and minimumWaveSize and goodShape:
                bias = BEARISH if D.leg == BULLISH_LEG else BULLISH
                __block_result_9__ = wave(array.from_items(chartPoint(A), chartPoint(B), chartPoint(C), chartPoint(D)), WAVE_Y, bias)
            __block_result_8__ = __block_result_9__
        return __block_result_8__

    def gatherWaveW():
        size__ren__ = array.size(swingPoints)
        __block_result_10__ = na
        if size__ren__ >= 5:
            A = array.get(swingPoints, size__ren__ - 5)
            B = array.get(swingPoints, size__ren__ - 4)
            C = array.get(swingPoints, size__ren__ - 3)
            D = array.get(swingPoints, size__ren__ - 2)
            E = array.get(swingPoints, size__ren__ - 1)
            waveSize = E.barIndex - A.barIndex
            minimumWaveSize = waveSize >= 9
            threshold = math.abs(A.priceLevel - B.priceLevel) * 0.2
            isBullishWaveW = C.priceLevel <= A.priceLevel - threshold and C.priceLevel >= B.priceLevel + threshold and (E.priceLevel >= A.priceLevel - threshold) and (E.priceLevel <= A.priceLevel + threshold) and (D.priceLevel >= B.priceLevel - threshold) and (D.priceLevel <= B.priceLevel + threshold)
            isBearishWaveW = C.priceLevel >= A.priceLevel + threshold and C.priceLevel <= B.priceLevel - threshold and (E.priceLevel >= B.priceLevel - threshold) and (E.priceLevel <= B.priceLevel + threshold) and (D.priceLevel >= A.priceLevel - threshold) and (D.priceLevel <= A.priceLevel + threshold)
            isWaveW = isBullishWaveW or isBearishWaveW
            __block_result_11__ = na
            if isWaveW and minimumWaveSize:
                bias = BEARISH if E.leg == BULLISH_LEG else BULLISH
                __block_result_11__ = wave(array.from_items(chartPoint(A), chartPoint(B), chartPoint(C), chartPoint(D), chartPoint(E)), WAVE_W, bias)
            __block_result_10__ = __block_result_11__
        return __block_result_10__

    def addWave(newWave: wave):
        if array.size(waves) >= maximumWavesInput:
            w_ave = array.shift(waves)
            label.delete(w_ave.waveLabel)
            line.delete(w_ave.line1)
            line.delete(w_ave.line2)
        return array.push(waves, newWave)

    def gatherWaves():
        waveI: wave = na(wave)
        waveV: wave = na(wave)
        waveN: wave = na(wave)
        waveP: wave = na(wave)
        waveY: wave = na(wave)
        waveW: wave = na(wave)
        if showBasicWavesInput and showWaveIInput:
            waveI = gatherWaveI()
        if showBasicWavesInput and showWaveVInput:
            waveV = gatherWaveV()
        if showBasicWavesInput and showWaveNInput:
            waveN = gatherWaveN()
        if showComplexWavesInput and showWavePInput:
            waveP = gatherWaveP()
        if showComplexWavesInput and showWaveYInput:
            waveY = gatherWaveY()
        if showComplexWavesInput and showWaveWInput:
            waveW = gatherWaveW()
        __block_result_12__ = na
        if overlappingWavesInput:
            if not na(waveI):
                addWave(waveI)
            if not na(waveV):
                addWave(waveV)
            if not na(waveN):
                addWave(waveN)
            if not na(waveP):
                addWave(waveP)
            if not na(waveY):
                addWave(waveY)
            __block_result_13__ = na
            if not na(waveW):
                __block_result_13__ = addWave(waveW)
            __block_result_12__ = __block_result_13__
        else:
            w_ave: wave = na(wave)
            if not na(waveN):
                w_ave = waveN
            elif not na(waveW):
                w_ave = waveW
            elif not na(waveP):
                w_ave = waveP
            elif not na(waveY):
                w_ave = waveY
            elif not na(waveV):
                w_ave = waveV
            elif not na(waveI):
                w_ave = waveI
            __block_result_14__ = na
            if not na(w_ave):
                __block_result_14__ = addWave(w_ave)
            __block_result_12__ = __block_result_14__
        return __block_result_12__

    def colorSelection(typeOfWave: str):
        __block_result_15__ = na
        __switch__ = typeOfWave
        if __switch__ == WAVE_I:
            __block_result_15__ = waveIColorInput
        elif __switch__ == WAVE_V:
            __block_result_15__ = waveVColorInput
        elif __switch__ == WAVE_N:
            __block_result_15__ = waveNColorInput
        elif __switch__ == WAVE_P:
            __block_result_15__ = wavePColorInput
        elif __switch__ == WAVE_Y:
            __block_result_15__ = waveYColorInput
        elif __switch__ == WAVE_W:
            __block_result_15__ = waveWColorInput
        return __block_result_15__

    def plotWaves():
        for eachPolyline in polyline.all:
            polyline.delete(eachPolyline)
        __block_result_16__ = na
        for index, eachWave in enumerate(waves):
            label.delete(eachWave.waveLabel)
            if eachWave.tag == WAVE_P or eachWave.tag == WAVE_Y:
                line.delete(eachWave.line1)
                line.delete(eachWave.line2)
                eachWave.line1 = line.new(array.get(eachWave.points, 0), array.get(eachWave.points, 2), xloc.bar_time, color=colorSelection(eachWave.tag), style=line.style_solid, width=2)
                eachWave.line2 = line.new(array.get(eachWave.points, 1), array.get(eachWave.points, 3), xloc.bar_time, color=colorSelection(eachWave.tag), style=line.style_solid, width=2)
            else:
                polyline.new(eachWave.points, False, False, xloc.bar_time, colorSelection(eachWave.tag), line_style=line.style_solid, line_width=2)
            overlappingLabel = array.last(eachWave.points).time == method_call('last', array.get(waves, index - 1).points).time if index > 0 else False
            style = label.style_label_down if eachWave.bias == BULLISH else label.style_label_up
            __block_result_17__ = na
            if overlappingLabel:
                eachWave.waveLabel = array.get(waves, index - 1).waveLabel
                label.set_text(eachWave.waveLabel, label.get_text(eachWave.waveLabel) + '\n' + eachWave.tag)
                __block_result_17__ = label.set_textcolor(eachWave.waveLabel, colorSelection(eachWave.tag))
            else:
                eachWave.waveLabel = label.new(array.last(eachWave.points), eachWave.tag, xloc.bar_time, color=NA(Color), style=style, textcolor=colorSelection(eachWave.tag))
                __block_result_17__ = label.delete(na)
            __block_result_16__ = __block_result_17__
        return __block_result_16__

    def drawPriceTarget(barIndex: int, priceLevel: float, tag: str):
        return array.push(priceTargets, priceTarget(line.new(barIndex, priceLevel, last_bar_index + ichimokuOffsetInput, priceLevel, color=chart.fg_color, style=line.style_dotted), label.new(last_bar_index + ichimokuOffsetInput, priceLevel, tag + ' (' + string.tostring(priceLevel) + ')', color=NA(Color), textcolor=chart.fg_color, style=label.style_label_left)))

    def priceTheoryTargets():
        size__ren__ = array.size(swingPoints)
        __block_result_18__ = na
        if size__ren__ >= 3:
            A = array.get(swingPoints, size__ren__ - 3)
            B = array.get(swingPoints, size__ren__ - 2)
            C = array.get(swingPoints, size__ren__ - 1)
            waveSize = C.barIndex - A.barIndex
            minimumWaveSize = waveSize >= 9
            threshold = math.abs(A.priceLevel - B.priceLevel) * 0.2
            isDevelopingBullishWaveN = A.priceLevel < B.priceLevel and C.priceLevel > A.priceLevel + threshold and (C.priceLevel < B.priceLevel - threshold)
            isDevelopingBearishWaveN = A.priceLevel > B.priceLevel and C.priceLevel < A.priceLevel - threshold and (C.priceLevel > B.priceLevel + threshold)
            isDevelopingWaveN = isDevelopingBullishWaveN or isDevelopingBearishWaveN
            calculationV: float = 0.0
            calculationE: float = 0.0
            calculationN: float = 0.0
            calculationNT: float = 0.0
            calculation2E: float = 0.0
            calculation3E: float = 0.0
            __block_result_19__ = na
            if isDevelopingWaveN and minimumWaveSize:
                for eachPriceTarget in priceTargets:
                    line.delete(eachPriceTarget.targetLine)
                    label.delete(eachPriceTarget.targetLabel)
                array.clear(priceTargets)
                if isDevelopingBullishWaveN:
                    calculationV = B.priceLevel + B.priceLevel - C.priceLevel
                    calculationE = B.priceLevel + B.priceLevel - A.priceLevel
                    calculationN = C.priceLevel + B.priceLevel - A.priceLevel
                    calculationNT = C.priceLevel + C.priceLevel - A.priceLevel
                    calculation2E = B.priceLevel + 2 * (B.priceLevel - A.priceLevel)
                    calculation3E = B.priceLevel + 3 * (B.priceLevel - A.priceLevel)
                if isDevelopingBearishWaveN:
                    calculationV = B.priceLevel - (C.priceLevel - B.priceLevel)
                    calculationE = B.priceLevel - (A.priceLevel - B.priceLevel)
                    calculationN = C.priceLevel - (A.priceLevel - B.priceLevel)
                    calculationNT = C.priceLevel - (A.priceLevel - C.priceLevel)
                    calculation2E = B.priceLevel - 2 * (A.priceLevel - B.priceLevel)
                    calculation3E = B.priceLevel - 3 * (A.priceLevel - B.priceLevel)
                if showBasicTargetsInput and showTargetVInput:
                    drawPriceTarget(C.barIndex, calculationV, 'V')
                if showBasicTargetsInput and showTargetEInput:
                    drawPriceTarget(C.barIndex, calculationE, 'E')
                if showBasicTargetsInput and showTargetNInput:
                    drawPriceTarget(C.barIndex, calculationN, 'N')
                if showBasicTargetsInput and showTargetNTInput:
                    drawPriceTarget(C.barIndex, calculationNT, 'NT')
                if showExtendedTargetsInput and showTarget2EInput:
                    drawPriceTarget(C.barIndex, calculation2E, '2E')
                __block_result_20__ = na
                if showExtendedTargetsInput and showTarget3EInput:
                    __block_result_20__ = drawPriceTarget(C.barIndex, calculation3E, '3E')
                __block_result_19__ = __block_result_20__
            __block_result_18__ = __block_result_19__
        return __block_result_18__

    def updatePriceTargets():
        __block_result_21__ = na
        for eachPriceTarget in priceTargets:
            line.set_x2(eachPriceTarget.targetLine, last_bar_index + ichimokuOffsetInput)
            __block_result_21__ = label.set_x(eachPriceTarget.targetLabel, last_bar_index + ichimokuOffsetInput)
        return __block_result_21__

    def updateLastTimeCycle(cycle: timeCycle):
        size__ren__ = array.size(timeCycles)
        __block_result_22__ = na
        if size__ren__ > 0:
            c_ycle = array.last(timeCycles)
            c_ycle.lastBarIndex = cycle.firstBarIndex
            c_ycle.lastBarTime = cycle.firstBarTime
            __block_result_22__ = c_ycle.lastBarTime
        return __block_result_22__

    def addTimeCycle(cycle: timeCycle):
        updateLastTimeCycle(cycle)
        size__ren__ = array.size(timeCycles)
        if size__ren__ >= maximumTimeCyclesInput + 1:
            c_ycle = array.shift(timeCycles)
            line.delete(c_ycle.cycleLine)
            label.delete(c_ycle.cycleLabel)
        return array.push(timeCycles, cycle)

    def parseWavesToTimeCycles():
        for eachCycle in timeCycles:
            label.delete(eachCycle.cycleLabel)
            line.delete(eachCycle.cycleLine)
        array.clear(timeCycles)
        __block_result_23__ = na
        for index in pine_range(array.size(waves) - 1, 0, 1):
            if array.size(timeCycles) >= maximumTimeCyclesInput:
                break
            __block_result_24__ = na
            if array.get(waves, index).tag == waveCyleInput:
                __block_result_24__ = array.unshift(timeCycles, timeCycle(method_call('first', array.get(waves, index).points).time, method_call('first', array.get(waves, index).points).index, method_call('last', array.get(waves, index).points).time, method_call('last', array.get(waves, index).points).index))
            __block_result_23__ = __block_result_24__
        return __block_result_23__

    def gatherTimeCycles():
        __block_result_25__ = na
        __switch__ = timeCycleModeInput
        if __switch__ == HIGHS:
            __block_result_25__ = timeCycle(legTime, legIndex) if pivotHigh else na
        elif __switch__ == LOWS:
            __block_result_25__ = timeCycle(legTime, legIndex) if pivotLow else na
        elif __switch__ == SWINGS:
            __block_result_25__ = timeCycle(legTime, legIndex) if newPivot else na
        elif __switch__ == TENKAN:
            __block_result_25__ = timeCycle(time, bar_index) if tenkanSenCross else na
        elif __switch__ == KIJUN:
            __block_result_25__ = timeCycle(time, bar_index) if kinjuSenCross else na
        elif __switch__ == KUMO:
            __block_result_25__ = timeCycle(time, bar_index) if kumoChange else na
        elif __switch__ == WAVE:
            __block_result_25__ = na
        newCycle: timeCycle = __block_result_25__
        __block_result_26__ = na
        if not na(newCycle):
            __block_result_26__ = addTimeCycle(newCycle)
        elif timeCycleModeInput == WAVE and array.size(waves) > 0:
            __block_result_26__ = parseWavesToTimeCycles()
        return __block_result_26__

    def plotTimeCycles():
        size__ren__ = array.size(timeCycles)
        __block_result_27__ = na
        if size__ren__ > 1:
            priceLevel = lowest
            __block_result_28__ = na
            for index, eachCycle in enumerate(timeCycles):
                line.delete(eachCycle.cycleLine)
                label.delete(eachCycle.cycleLabel)
                tagPosition = math.max(1, math.round(0.5 * (eachCycle.lastBarTime - eachCycle.firstBarTime)))
                if index == array.size(timeCycles) - 1 and timeCycleModeInput != WAVE:
                    break
                if timeCycleModeInput == WAVE and index > 0:
                    if eachCycle.firstBarIndex < array.get(timeCycles, index - 1).lastBarIndex:
                        priceLevel = priceLevel - atr200
                eachCycle.cycleLine = line.new(eachCycle.firstBarTime, priceLevel, eachCycle.lastBarTime, priceLevel, xloc.bar_time, color=chart.fg_color, style=line.style_arrow_right)
                eachCycle.cycleLabel = label.new(eachCycle.firstBarTime + tagPosition, priceLevel, string.tostring(eachCycle.lastBarIndex - eachCycle.firstBarIndex), xloc.bar_time, color=NA(Color), style=label.style_none, textcolor=chart.fg_color)
                __block_result_28__ = eachCycle.cycleLabel
            __block_result_27__ = __block_result_28__
        return __block_result_27__

    def plotTimeCyclesForecast():
        lastArrayIndex = array.size(timeCycles) - (0 if timeCycleModeInput == WAVE else 1)
        __block_result_29__ = na
        if lastArrayIndex >= timeForecastAnchorInput:
            cycle = array.get(timeCycles, lastArrayIndex - timeForecastAnchorInput)
            taitoCycle = cycle.lastBarIndex - cycle.firstBarIndex
            forecastAnchor = cycle.lastBarIndex
            __block_result_30__ = na
            __switch_1__ = timePatternInput
            if __switch_1__ == KIHON:
                __block_result_30__ = array.from_items(9, 17, 26, 33, 42, 51, 65, 76, 129, 172, 200, 257)
            elif __switch_1__ == TAITO:
                __block_result_30__ = array.from_items(taitoCycle, 2 * taitoCycle, 3 * taitoCycle, 4 * taitoCycle, 5 * taitoCycle, 6 * taitoCycle, 7 * taitoCycle, 8 * taitoCycle, 9 * taitoCycle)
            indexes: list[int] = __block_result_30__
            for eachLine in timeCyclesForecast:
                line.delete(eachLine)
            array.clear(timeCyclesForecast)
            array.push(timeCyclesForecast, line.new(forecastAnchor, extremeHigh, forecastAnchor, extremeLow, color=chart.fg_color, style=line.style_solid))
            __block_result_31__ = na
            for index in indexes:
                if forecastAnchor + index > last_bar_index + 500:
                    break
                __block_result_31__ = array.push(timeCyclesForecast, line.new(forecastAnchor + index, extremeHigh, forecastAnchor + index, extremeLow, color=chart.fg_color, style=line.style_dotted))
            __block_result_29__ = __block_result_31__
        return __block_result_29__

    def updateTimeCyclesForecast():
        __block_result_32__ = na
        if newExtremeHigh or newExtremeLow:
            __block_result_33__ = na
            for eachTimeCycle in timeCyclesForecast:
                if newExtremeHigh:
                    line.set_y1(eachTimeCycle, extremeHigh)
                __block_result_34__ = na
                if newExtremeLow:
                    __block_result_34__ = line.set_y2(eachTimeCycle, extremeLow)
                __block_result_33__ = __block_result_34__
            __block_result_32__ = __block_result_33__
        return __block_result_32__

    currentLeg = leg()
    newPivot = startOfNewLeg(currentLeg)
    pivotLow = startOfBullishLeg(currentLeg)
    pivotHigh = startOfBearishLeg(currentLeg)
    tenkanSen = average(tenkanSenLengthInput)
    kinjuSen = average(kinjuSenLengthInput)
    senkouSpanA = 0.5 * (tenkanSen + kinjuSen)
    senkouSpanB = average(senkouSpanBLengthInput)
    kumoChange = ta.change(senkouSpanA >= senkouSpanB)
    kumoColor = color.new(GREEN, 80) if senkouSpanA >= senkouSpanB else color.new(RED, 80)
    tenkanSenCross = ta.cross(close, tenkanSen)
    kinjuSenCross = ta.cross(close, kinjuSen)
    e_xtremeHigh, e_xtremeLow = extremesOnLastXBars(200)
    extremeHigh = e_xtremeHigh
    extremeLow = e_xtremeLow
    newExtremeHigh = ta.change(extremeHigh) != 0
    newExtremeLow = ta.change(extremeLow) != 0
    if array.size(timeCycles) > 0 and bar_index > 200:
        lowest = ta.lowest(bar_index - array.first(timeCycles).firstBarIndex) - atr200
    __block_result_35__ = na
    __switch__ = timeCycleModeInput
    if __switch__ == HIGHS:
        __block_result_35__ = pivotHigh
    elif __switch__ == LOWS:
        __block_result_35__ = pivotLow
    elif __switch__ == SWINGS:
        __block_result_35__ = newPivot
    elif __switch__ == TENKAN:
        __block_result_35__ = tenkanSenCross
    elif __switch__ == KIJUN:
        __block_result_35__ = kinjuSenCross
    elif __switch__ == KUMO:
        __block_result_35__ = kumoChange
    elif __switch__ == WAVE:
        __block_result_35__ = newPivot
    newTimeCycle: bool = __block_result_35__
    if barstate.isconfirmed:
        if newPivot:
            priceLevel = legHigh
            legBias = BEARISH_LEG
            if pivotLow:
                priceLevel = legLow
                legBias = BULLISH_LEG
            array.push(swingPoints, swingPoint(legTime, legIndex, priceLevel, legBias))
            gatherWaves()
            if showBasicWavesInput or showComplexWavesInput:
                plotWaves()
            if showBasicTargetsInput or showExtendedTargetsInput:
                priceTheoryTargets()
        if array.size(priceTargets) > 0:
            updatePriceTargets()
        if newTimeCycle:
            gatherTimeCycles()
            if showTimeCyclesInput:
                plotTimeCycles()
            if showTimeForecastInput:
                plotTimeCyclesForecast()
        else:
            if showTimeForecastInput:
                updateTimeCyclesForecast()
    plotshape((na if na(pivotLow) else 1 if pivotLow else 0) if showPivotMarksInput else na, 'Swing High', shape.circle, location.belowbar, GREEN, -pivotLengthInput)
    plotshape((na if na(pivotHigh) else 1 if pivotHigh else 0) if showPivotMarksInput else na, 'Swing Low', shape.circle, location.abovebar, RED, -pivotLengthInput)
    plot(tenkanSen if showIchimokuLinesInput else na, 'TenkanSen', color=RED)
    plot(kinjuSen if showIchimokuLinesInput else na, 'KinjuSen', color=color.blue)
    plot(chikouSpan if showIchimokuLinesInput else na, 'ChikouSpan', offset=-ichimokuOffsetInput, color=color.new(color.new('#787B86'), 50))
    kumoFast = plot(senkouSpanA if showIchimokuKumoInput else na, 'SenkouSpanA', kumoColor, offset=ichimokuOffsetInput)
    kumoSlow = plot(senkouSpanB if showIchimokuKumoInput else na, 'SenkouSpanB', kumoColor, offset=ichimokuOffsetInput)
    fill(kumoFast, kumoSlow, color=kumoColor, title='Kumo')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)