"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool, cast_int
from pynecore.core.series import inline_series
from pynecore.lib import (
    array, bar_index, barstate, close, color, high, input, label, location,
    low, math, na, nz, open, order, plotcandle, plotchar, position, request, runtime, script, size,
    string, syminfo, ta, table, text, time, timeframe, timenow, volume, xloc, yloc
)
from pynecore.types import Color, IBPersistent, Label, NA, Persistent, Series, Table

BLUE: Color = color.new('#013BCA')
BLUE_LITE: Color = color.new('#013BCA20')
GRAY: Color = color.new('#808080')
GRAY_LITE: Color = color.new('#80808020')
GREEN: Color = color.new('#008000')
LIME: Color = color.new('#00FF00')
PINK: Color = color.new('#FF0080')
RED: Color = color.new('#FF0000')
PROF1: str = '    🠇 Volume 🠅'
PROF2: str = '  🠇 Ticks 🠅'
PROF3: str = ' Ticks | Volume'
PROF4: str = 'Volume | Ticks'
PROF5: str = 'Volume |'
PROF6: str = ' Ticks |'
PROF7: str = '        | Volume'
PROF8: str = '        | Ticks'
RSET1: str = 'Timeframe'
RSET2: str = 'Supertrend'
RSET3: str = 'LazyBear\'s Weis Wave Trend Detection'
PFMT1: str = 'Total'
PFMT2: str = 'Delta'
CAND0: str = 'None'
CAND1: str = 'Polarity of update'
CAND2: str = 'Polarity of close vs open'
CAND3: str = 'Trend'
UP_COLOR: Color = LIME
DN_COLOR: Color = PINK
UP_COLOR_TOTAL: Color = GREEN
DN_COLOR_TOTAL: Color = RED
TT_CONFIG: str = "DOUBLE-SIDED PROFILES\nThe first two configurations are called 'double-sided' profiles. With them, the settings in this section control both sides.\n\n" + "SINGLE-SIDED PROFILES\nThe other configurations use 'single-sided' profiles. With those, the formatting choices in this section control the LEFT side of the profile, and the settings in the following section control its RIGHT side."
TT_DURATION: str = "Determines when a new profile is created. Use this when you don't want a new profile on each bar. You can change the profile on a higher timeframe or on trend changes. The 'Timeframe' setting has no effect when using trend-detection logic.\n\n" + "See the 'Trend Detection and Display' section further down for settings related to trend detection."
TT_LEVELS: str = "'Levels' (1 to 100) determines the maximum quantity of levels in the profile. If the profile's height is small enough for level increments to be smaller than minticks, then a smaller quantity of levels are used until the profile's height grows.\n\n" + 'The offset allows shifting the profile left/right by a −/+ number of bars.'
TT_CALC: str = "This only applies when you are using single-sided profiles.With 'Total', level values are the total volume/ticks at that level for the bar.\n" + "With 'Delta', level values represent the net values for the level (up values - down values)."
TT_SIZE: str = '\'Max line length\' (0 to 100) controls the length of lines. Use zero if you only need values.\n\'Profile size\' controls the overall size of the profile.'
GRP1: str = '🠆 Right format (single-sided profiles only)'
GRP2: str = 'Candles'
GRP3: str = 'Trend Detection and Display'


@script.indicator('Realtime 5D Profile [LucF]', 'VPAA', True, max_labels_count=500, precision=8)
def main(
    profileConfigInput=input.string(PROF1, 'Configuration', inline='00', options=(PROF1, PROF2, PROF3, PROF4, PROF5, PROF6, PROF7, PROF8), tooltip=TT_CONFIG),
    profileResetOnTfInput=input.string(RSET1, 'Resets on', inline='01', options=(RSET1, RSET2, RSET3)),
    profileResetTfInput=input.timeframe('', 'Timeframe', inline='01', tooltip=TT_DURATION),
    profileLevelsMaxQtyInput=input.int(20, 'Levels', inline='02', minval=1, maxval=100),
    profileOffsetInput=input.int(0, ' ↔ Offset (in bars)', inline='02', tooltip=TT_LEVELS),
    profileVolumePrecisionInput=input.int(2, 'Precision of volume values', inline='02a', minval=0),
    __input_6__=input.string(PFMT2, 'Calculation', inline='03', options=(PFMT1, PFMT2), tooltip=TT_CALC),
    profileLeftBullColorInput=input(UP_COLOR, 'Level Colors 🠅', inline='04'),
    profileLeftBearColorInput=input(DN_COLOR, '🠇', inline='04'),
    profileLeftBullTColorInput=input(UP_COLOR_TOTAL, '  Total Colors 🠅', inline='04'),
    profileLeftBearTColorInput=input(DN_COLOR_TOTAL, '🠇', inline='04'),
    profileLeftMaxWidthInput=input.int(15, 'Maximum line length', inline='05', minval=0, maxval=100),
    profileLeftSizeInput=input.string(size.small, 'Profile size', inline='05', options=(size.tiny, size.small, size.normal, size.large, size.huge), tooltip=TT_SIZE),
    profileLeftShowValuesInput=input.bool(True, 'Level values  ', inline='06'),
    profileLeftShowTotalsInput=input.bool(True, 'Total bar values using size', inline='06'),
    profileLeftTotalsSizeInput=input.string(size.normal, '', inline='06', options=(size.tiny, size.small, size.normal, size.large, size.huge)),
    __input_16__=input.string(PFMT2, 'Calculation', inline='11', group=GRP1, options=(PFMT1, PFMT2), tooltip=TT_CALC),
    profileRightBullColorInput=input(UP_COLOR, 'Level Colors 🠅', inline='12', group=GRP1),
    profileRightBearColorInput=input(DN_COLOR, '🠇', inline='12', group=GRP1),
    profileRightBullTColorInput=input(UP_COLOR_TOTAL, '  Total Colors 🠅', inline='12', group=GRP1),
    profileRightBearTColorInput=input(DN_COLOR_TOTAL, '🠇', inline='12', group=GRP1),
    profileRightMaxWidthInput=input.int(15, 'Maximum line length', inline='13', group=GRP1, minval=0, maxval=100),
    profileRightSizeInput=input.string(size.small, 'Profile size', inline='13', group=GRP1, options=(size.tiny, size.small, size.normal, size.large, size.huge), tooltip=TT_SIZE),
    profileRightShowValuesInput=input.bool(True, 'Show values  ', inline='14', group=GRP1),
    profileRightShowTotalsInput=input.bool(True, 'Show totals using size', inline='14', group=GRP1),
    profileRightTotalsSizeInput=input.string(size.normal, '', inline='14', group=GRP1, options=(size.tiny, size.small, size.normal, size.large, size.huge)),
    candleBorderModeInput=input.string(CAND0, 'Color borders on', inline='21', group=GRP2, options=(CAND0, CAND1, CAND2, CAND3)),
    candleBorderBullColorInput=input(GRAY, ' 🠅', inline='21', group=GRP2),
    candleBorderBearColorInput=input(BLUE, '🠇', inline='21', group=GRP2),
    candleBodyModeInput=input.string(CAND0, 'Color bodies on ', inline='22', group=GRP2, options=(CAND0, CAND1, CAND2, CAND3)),
    candleBodyBullTColorInput=input(GRAY_LITE, ' 🠅', inline='22', group=GRP2),
    candleBodyBearTColorInput=input(BLUE_LITE, '🠇', inline='22', group=GRP2),
    candleColoringRtInput=input.bool(True, 'On RT bars only', inline='23', group=GRP2),
    trendSTLengthInput=input.int(20, 'Supertrend length', inline='31', group=GRP3, minval=1),
    trendSTFactorInput=input.float(4.0, ' Factor', inline='31', group=GRP3, minval=0.0),
    trendWWSmoothingLengthInput=input.int(2, 'LB Weis Wave smoothing', inline='32', group=GRP3, minval=1),
    trendMarkerShowChangesInput=input.bool(True, 'Show trend changes', inline='33', group=GRP3),
    trendMarkerChangesRtInput=input.bool(True, 'On RT bars only', inline='33', group=GRP3),
    trendMarkerBullColorInput=input(UP_COLOR, ' 🠅', inline='33', group=GRP3),
    trendMarkerBearColorInput=input(DN_COLOR, '🠇', inline='33', group=GRP3),
    trendMarkerShowStatesInput=input.bool(True, 'Show trend state    ', inline='34', group=GRP3),
    trendMarkerStatesRtInput=input.bool(True, 'On RT bars only', inline='34', group=GRP3)
):
    GOLD: Persistent[Color] = color.new('#CCCC00')
    YELLOW: Persistent[Color] = color.new('#FFFF00')
    RIGHT_PROFILE: Persistent[bool] = True
    LEFT_PROFILE: Persistent[bool] = False
    VOLUME: Persistent[bool] = True
    TICKS: Persistent[bool] = False
    profileLeftCalcDeltaInput: bool = __input_6__ == PFMT2
    profileRightCalcDeltaInput: bool = __input_16__ == PFMT2
    profileDOUBLE_VOLUME: Persistent[bool] = profileConfigInput == PROF1
    profileDOUBLE_TICKS: Persistent[bool] = profileConfigInput == PROF2
    profileLEFT_VOLUME: Persistent[bool] = profileConfigInput == PROF4 or profileConfigInput == PROF5
    profileLEFT_TICKS: Persistent[bool] = profileConfigInput == PROF3 or profileConfigInput == PROF6
    profileRIGHT_VOLUME: Persistent[bool] = profileConfigInput == PROF3 or profileConfigInput == PROF7
    profileRIGHT_TICKS: Persistent[bool] = profileConfigInput == PROF4 or profileConfigInput == PROF8
    profileResetOnTF: Persistent[bool] = profileResetOnTfInput == RSET1
    profileResetOnST: Persistent[bool] = profileResetOnTfInput == RSET2
    profileResetOnWW: Persistent[bool] = profileResetOnTfInput == RSET3
    rtTimes_: IBPersistent[list[int]] = array.new_int()
    rtPrices_: IBPersistent[list[float]] = array.new_float()
    rtVolumes_: IBPersistent[list[float]] = array.new_float()
    rtUps_: IBPersistent[list[bool]] = array.new_bool()
    squashedVolumesUp_: IBPersistent[list[float]] = array.new_float()
    squashedVolumesDn_: IBPersistent[list[float]] = array.new_float()
    squashedTicksUp_: IBPersistent[list[int]] = array.new_int()
    squashedTicksDn_: IBPersistent[list[int]] = array.new_int()
    squashedTimesUp_: IBPersistent[list[float]] = array.new_float()
    squashedTimesDn_: IBPersistent[list[float]] = array.new_float()
    levelStringHeight1_: Persistent[list[str]] = array.new_string()
    levelStringHeight2_: Persistent[list[str]] = array.new_string()
    levelStringHeight3_: Persistent[list[str]] = array.new_string()
    levelStringHeight4_: Persistent[list[str]] = array.new_string()
    profilePrices_: IBPersistent[list[float]] = array.new_float()
    profileBarIndex_: IBPersistent[int] = na(int)
    profileHi_: IBPersistent[float] = low
    profileLo_: IBPersistent[float] = high
    beginNewProfile_: IBPersistent[bool] = True
    rescaleProfile_: IBPersistent[bool] = True
    qtyOfRtUpdates_: IBPersistent[int] = 0
    qtyOfRtVolumes_: IBPersistent[float] = 0.0
    qtyOfLevels_: IBPersistent[int] = array.size(profilePrices_)
    volumePrecision_: Persistent[str] = '#' + ('' if profileVolumePrecisionInput == 0 else '.') + array.join(array.new_string(profileVolumePrecisionInput, '#'))
    tickUp: Persistent[list[bool]] = array.new_bool(1, False)
    profileMaxWidth_: Persistent[int] = math.max(profileLeftMaxWidthInput, profileRightMaxWidthInput)
    def printMessage(txt: Series[str], bgColor: Series[Color] = color.yellow):
        t: Persistent[Table] = table.new(position.bottom_right, 1, 1)
        __block_result__ = na
        if barstate.islast:
            __block_result__ = table.cell(t, 0, 0, txt, text_color=color.white, bgcolor=bgColor)
        return __block_result__

    def tfInMinutes(tf: str = ''):
        __block_result_1__ = na
        if timeframe.isseconds:
            __block_result_1__ = 1.0 / 60
        elif timeframe.isminutes:
            __block_result_1__ = 1.0
        elif timeframe.isdaily:
            __block_result_1__ = 60.0 * 24
        elif timeframe.isweekly:
            __block_result_1__ = 60.0 * 24 * 7
        elif timeframe.ismonthly:
            __block_result_1__ = 60.0 * 24 * 30.4375
        tfUnitsInSeconds: float = __block_result_1__
        tfInSeconds: float = timeframe.multiplier * tfUnitsInSeconds
        result: float = tfInSeconds if tf == '' else request.security(syminfo.tickerid, tf, tfInSeconds)
        return result

    def nonRepaintingSecurity(sym: str, tf: str, src: Series):
        return inline_series(request.security(sym, tf, src[1 if barstate.isrealtime else 0]), 0 if barstate.isrealtime else 1)

    def wwLBTrend(src: Series[float], length: int):
        latestTrend: Persistent[int] = 0
        prevTrend: Persistent[int] = 0
        priceChange: int = cast_int(math.sign(ta.change(src)))
        change_1 = ta.change(priceChange)
        latestTrend = priceChange if cast_bool(priceChange) and cast_bool(change_1) else latestTrend
        falling_1 = ta.falling(src, length)
        wwConfirmation: bool = ta.rising(src, length) or falling_1
        prevTrend = latestTrend if latestTrend != prevTrend and wwConfirmation else prevTrend
        return prevTrend

    def profileInitLevelStrings(maxWidth: int):
        CHAR_1: Persistent[str] = '▂'
        CHAR_2: Persistent[str] = '▃'
        CHAR_3: Persistent[str] = '▅'
        CHAR_4: Persistent[str] = '▆'
        __block_result_2__ = na
        for qtyOfCharsInLine in pine_range(0, maxWidth, 1):
            lineOfChars1: str = array.join(array.new_string(qtyOfCharsInLine, CHAR_1))
            lineOfChars2: str = array.join(array.new_string(qtyOfCharsInLine, CHAR_2))
            lineOfChars3: str = array.join(array.new_string(qtyOfCharsInLine, CHAR_3))
            lineOfChars4: str = array.join(array.new_string(qtyOfCharsInLine, CHAR_4))
            array.push(levelStringHeight1_, lineOfChars1)
            array.push(levelStringHeight2_, lineOfChars2)
            array.push(levelStringHeight3_, lineOfChars3)
            __block_result_2__ = array.push(levelStringHeight4_, lineOfChars4)
        return __block_result_2__

    def profileGetLevelStr(width: Series[int], height: Series[int] = 1):
        __block_result_3__ = na
        __switch__ = height
        if __switch__ == 1:
            __block_result_3__ = array.get(levelStringHeight1_, width)
        elif __switch__ == 2:
            __block_result_3__ = array.get(levelStringHeight2_, width)
        elif __switch__ == 3:
            __block_result_3__ = array.get(levelStringHeight3_, width)
        elif __switch__ == 4:
            __block_result_3__ = array.get(levelStringHeight4_, width)
        else:
            __block_result_3__ = ''
        result: str = __block_result_3__
        return result

    def profileRecalcLevels(hi: Series[float], lo: Series[float], userQtyOfLevels: int):
        profileHeight: float = math.abs(hi - lo)
        tickLevels: int = cast_int(profileHeight / syminfo.mintick)
        levels: int = math.max(1, tickLevels if profileHeight / userQtyOfLevels < syminfo.mintick else userQtyOfLevels)
        profileIncrements: float = profileHeight / levels
        array.clear(profilePrices_)
        array.clear(squashedVolumesUp_)
        array.clear(squashedVolumesDn_)
        array.clear(squashedTicksUp_)
        array.clear(squashedTicksDn_)
        array.clear(squashedTimesUp_)
        array.clear(squashedTimesDn_)
        if levels == 1:
            array.push(profilePrices_, math.avg(hi, lo))
            array.push(squashedVolumesUp_, 0.0)
            array.push(squashedVolumesDn_, 0.0)
            array.push(squashedTicksUp_, 0)
            array.push(squashedTicksDn_, 0)
            array.push(squashedTimesUp_, 0.0)
            array.push(squashedTimesDn_, 0.0)
        else:
            for levelNo in pine_range(0, levels - 1, 1):
                array.push(profilePrices_, lo + (0.5 + levelNo) * profileIncrements)
                array.push(squashedVolumesUp_, 0.0)
                array.push(squashedVolumesDn_, 0.0)
                array.push(squashedTicksUp_, 0)
                array.push(squashedTicksDn_, 0)
                array.push(squashedTimesUp_, 0.0)
                array.push(squashedTimesDn_, 0.0)
        return levels

    def profileRemovePrevious(barIndex: Series[int]):
        __block_result_4__ = na
        while array.size(label.all) > 0:
            lbl: Label = array.pop(label.all)
            labelX: int = label.get_x(lbl)
            __block_result_5__ = na
            if labelX == barIndex:
                __block_result_5__ = label.delete(lbl)
            else:
                break
            __block_result_4__ = __block_result_5__
        return __block_result_4__

    def sortTwoArrays(keysArray, valuesArray, order__ren__ = order.ascending):
        qtyOfValues = array.size(keysArray)
        arrayKeysSorted = array.copy(keysArray)
        valuesArraySorted = array.copy(valuesArray)
        if qtyOfValues == array.size(valuesArray):
            array.sort(valuesArraySorted, order__ren__)
            for i in pine_range(0, qtyOfValues - 1, 1):
                sortedValue = array.get(valuesArraySorted, i)
                unsortedIndex = array.indexof(valuesArray, sortedValue)
                unsortedKey = array.get(keysArray, unsortedIndex)
                array.set(arrayKeysSorted, i, unsortedKey)
        return (arrayKeysSorted, valuesArraySorted)

    def profileBuildAgeOfLevels(leftHeights: Series[list[int]], rightHeights: Series[list[int]]):
        avgAgesDn: list[float] = array.new_float()
        avgAgesUp: list[float] = array.new_float()
        levelNosDn: list[int] = array.new_int()
        levelNosUp: list[int] = array.new_int()
        for levelNo in pine_range(0, qtyOfLevels_ - 1, 1):
            array.push(levelNosDn, levelNo)
            array.push(levelNosUp, levelNo)
            ticksInLevelDn = array.get(squashedTicksDn_, levelNo)
            ticksInLevelUp = array.get(squashedTicksUp_, levelNo)
            avgDn: float = nz(array.get(squashedTimesDn_, levelNo) / ticksInLevelDn)
            avgUp: float = nz(array.get(squashedTimesUp_, levelNo) / ticksInLevelUp)
            array.push(avgAgesDn, 0.001 * levelNo if avgDn == 0 else avgDn)
            array.push(avgAgesUp, 0.001 * levelNo if avgUp == 0 else avgUp)
        sortedLevelNosDn, sortedAgesDn = sortTwoArrays(levelNosDn, avgAgesDn, order.ascending)
        sortedLevelNosUp, sortedAgesUp = sortTwoArrays(levelNosUp, avgAgesUp, order.ascending)
        qtyOfZeroLevelsDn: int = 0
        qtyOfZeroLevelsUp: int = 0
        heightDn: int = na(int)
        heightUp: int = na(int)
        __block_result_6__ = na
        for decreasingAge in pine_range(0, qtyOfLevels_ - 1, 1):
            avgAgeDn: float = array.get(sortedAgesDn, decreasingAge)
            avgAgeUp: float = array.get(sortedAgesUp, decreasingAge)
            if avgAgeDn < 1:
                qtyOfZeroLevelsDn = qtyOfZeroLevelsDn + 1
                heightDn = 0
            else:
                heightDn = math.max(1, nz(math.ceil(4 * (decreasingAge - qtyOfZeroLevelsDn) / (qtyOfLevels_ - qtyOfZeroLevelsDn - 1)), 4))
            if avgAgeUp < 1:
                qtyOfZeroLevelsUp = qtyOfZeroLevelsUp + 1
                heightUp = 0
            else:
                heightUp = math.max(1, nz(math.ceil(4 * (decreasingAge - qtyOfZeroLevelsUp) / (qtyOfLevels_ - qtyOfZeroLevelsUp - 1)), 4))
            array.set(leftHeights, array.get(sortedLevelNosDn, decreasingAge), heightDn)
            __block_result_6__ = array.set(rightHeights, array.get(sortedLevelNosUp, decreasingAge), heightUp)
        return __block_result_6__

    def profileBuildOneSide(values: Series[list[float]], widths: Series[list[int]], colors: Series[list[Color]], doRightSide: bool, doVolume: bool, doDelta: bool):
        profileBullColor: Persistent[Color] = profileRightBullColorInput if doRightSide else profileLeftBullColorInput
        profileBearColor: Persistent[Color] = profileRightBearColorInput if doRightSide else profileLeftBearColorInput
        profileMaxWidth: Persistent[int] = profileRightMaxWidthInput if doRightSide else profileLeftMaxWidthInput
        sign: Persistent[int] = -1 if doDelta else 1
        squashedUp = squashedVolumesUp_ if doVolume else squashedTicksUp_
        squashedDn = squashedVolumesDn_ if doVolume else squashedTicksDn_
        absDeltas: list[float] = array.new_float(qtyOfLevels_)
        for levelNo in pine_range(0, qtyOfLevels_ - 1, 1):
            valueUp: float = array.get(squashedUp, levelNo)
            valueDn: float = array.get(squashedDn, levelNo)
            array.set(values, levelNo, valueUp + sign * valueDn)
            array.set(absDeltas, levelNo, math.abs(valueUp - valueDn))
        maxValueGross: float = qtyOfRtVolumes_ if doVolume else qtyOfRtUpdates_
        maxValueProfile: float = array.max(absDeltas)
        maxValue: float = maxValueProfile if doDelta else maxValueGross
        __block_result_7__ = na
        for levelNo in pine_range(0, qtyOfLevels_ - 1, 1):
            value: float = array.get(values, levelNo)
            lineWidth: int = math.min(profileMaxWidth_, nz(cast_int(math.ceil(profileMaxWidth * math.abs(value) / maxValue)), profileMaxWidth))
            array.set(widths, levelNo, lineWidth)
            lineColor: Color = profileBullColor if value > 0 else profileBearColor
            __block_result_7__ = array.set(colors, levelNo, lineColor)
        return __block_result_7__

    def profileBuildTwoSides(leftWidths: Series[list[int]], leftColors: Series[list[Color]], rightWidths: Series[list[int]], rightColors: Series[list[Color]], doVolume: bool):
        squashedUp = squashedVolumesUp_ if doVolume else squashedTicksUp_
        squashedDn = squashedVolumesDn_ if doVolume else squashedTicksDn_
        rangeOfValues: float = math.max(array.max(squashedDn), array.max(squashedUp))
        __block_result_8__ = na
        for levelNo in pine_range(0, qtyOfLevels_ - 1, 1):
            valueDn: float = array.get(squashedDn, levelNo)
            valueUp: float = array.get(squashedUp, levelNo)
            lineWidthDn: int = math.min(profileMaxWidth_, nz(cast_int(math.ceil(profileLeftMaxWidthInput * valueDn / rangeOfValues)), profileLeftMaxWidthInput))
            lineWidthUp: int = math.min(profileMaxWidth_, nz(cast_int(math.ceil(profileLeftMaxWidthInput * valueUp / rangeOfValues)), profileLeftMaxWidthInput))
            array.set(leftWidths, levelNo, lineWidthDn)
            array.set(rightWidths, levelNo, lineWidthUp)
            lineColorDn: Color = profileLeftBearColorInput if valueDn > valueUp else color.new(profileLeftBearColorInput, 50)
            lineColorUp: Color = profileLeftBullColorInput if valueUp > valueDn else color.new(profileLeftBullColorInput, 50)
            array.set(leftColors, levelNo, lineColorDn)
            __block_result_8__ = array.set(rightColors, levelNo, lineColorUp)
        return __block_result_8__

    def profileDrawOneSide(values: list[float], widths: Series[list[int]], leftHeights: Series[list[int]], rightHeights: Series[list[int]], colors: Series[list[Color]], doRightSide: bool, doVolume: bool):
        profileBullColor: Persistent[Color] = profileRightBullColorInput if doRightSide else profileLeftBullColorInput
        profileBearColor: Persistent[Color] = profileRightBearColorInput if doRightSide else profileLeftBearColorInput
        profileStyle: Persistent[str] = label.style_label_left if doRightSide else label.style_label_right
        profileTextalign: Persistent[str] = text.align_left if doRightSide else text.align_right
        profileSize: Persistent[str] = profileRightSizeInput if doRightSide else profileLeftSizeInput
        profileShowVals: Persistent[bool] = profileRightShowValuesInput if doRightSide else profileLeftShowValuesInput
        profileShowTots: Persistent[bool] = profileRightShowTotalsInput if doRightSide else profileLeftShowTotalsInput
        profileTotsSize: Persistent[str] = profileRightTotalsSizeInput if doRightSide else profileLeftTotalsSizeInput
        valueSpacing: Persistent[str] = '' if (profileRightMaxWidthInput if doRightSide else profileLeftMaxWidthInput) == 0 else '\u2007'
        formatString: Persistent[str] = valueSpacing + (volumePrecision_ if doVolume else '#') + valueSpacing
        squashedUp = squashedVolumesUp_ if doVolume else squashedTicksUp_
        squashedDn = squashedVolumesDn_ if doVolume else squashedTicksDn_
        for levelNo in pine_range(0, qtyOfLevels_ - 1, 1):
            labelY: float = array.get(profilePrices_, levelNo)
            value: float = array.get(values, levelNo)
            valueString: str = string.tostring(value, formatString) if profileShowVals and value != 0 else ''
            leftH: int = array.get(leftHeights, levelNo)
            rightH: int = array.get(rightHeights, levelNo)
            lineHeight: int = cast_int(math.ceil(rightH if leftH < 1 else leftH if rightH < 1 else math.avg(leftH, rightH)))
            labelTxt: str = ('' if doRightSide else valueString) + profileGetLevelStr(array.get(widths, levelNo), lineHeight) + (valueString if doRightSide else '')
            labelColor: Color = array.get(colors, levelNo)
            labelTooltip: str = string.tostring(array.get(values, levelNo))
            label.new(profileBarIndex_, labelY, labelTxt, xloc.bar_index, yloc.price, NA(Color), profileStyle, labelColor, profileSize, profileTextalign, labelTooltip)
        __block_result_9__ = na
        if profileShowTots:
            lastTotal: IBPersistent[float] = na(float)
            profileTotal: Persistent = qtyOfRtVolumes_ if doVolume else qtyOfRtUpdates_
            total: float = array.sum(values)
            labelY: float = profileHi_ + 2 * (profileHi_ - array.get(profilePrices_, qtyOfLevels_ - 1))
            labelTxt: str = string.tostring(total, formatString) + ('\u2009🠅' if total > lastTotal else '\u2009🠇' if total < lastTotal else '')
            labelColor: Color = profileBullColor if total >= 0 else profileBearColor
            labelTooltip: str = string.tostring(total) + ' / ' + string.tostring(profileTotal)
            label.new(profileBarIndex_, labelY, labelTxt, xloc.bar_index, yloc.price, NA(Color), profileStyle, labelColor, profileTotsSize, profileTextalign, labelTooltip)
            lastTotal = total
            __block_result_9__ = lastTotal
        return __block_result_9__

    def profileDrawTwoSides(leftWidths: Series[list[int]], leftHeights: Series[list[int]], leftColors: Series[list[Color]], rightWidths: Series[list[int]], rightHeights: Series[list[int]], rightColors: Series[list[Color]], doVolume: bool):
        valueSpacing: Persistent[str] = '' if profileLeftMaxWidthInput == 0 else '\u2007'
        formatString: Persistent[str] = valueSpacing + (volumePrecision_ if doVolume else '#') + valueSpacing
        squashedUp = squashedVolumesUp_ if doVolume else squashedTicksUp_
        squashedDn = squashedVolumesDn_ if doVolume else squashedTicksDn_
        for levelNo in pine_range(0, qtyOfLevels_ - 1, 1):
            labelY: float = array.get(profilePrices_, levelNo)
            value: float = array.get(squashedDn, levelNo)
            valueString: str = string.tostring(value, formatString) if profileLeftShowValuesInput and value != 0 else ''
            labelTxt: str = valueString + profileGetLevelStr(array.get(leftWidths, levelNo), array.get(leftHeights, levelNo))
            labelColor: Color = array.get(leftColors, levelNo)
            labelTooltip: str = string.tostring(value)
            label.new(profileBarIndex_, labelY, labelTxt, xloc.bar_index, yloc.price, NA(Color), label.style_label_right, labelColor, profileLeftSizeInput, text.align_right, labelTooltip)
            value = array.get(squashedUp, levelNo)
            valueString = string.tostring(value, formatString) if profileLeftShowValuesInput and value != 0 else ''
            labelTxt = profileGetLevelStr(array.get(rightWidths, levelNo), array.get(rightHeights, levelNo)) + valueString
            labelColor = array.get(rightColors, levelNo)
            labelTooltip = string.tostring(value)
            label.new(profileBarIndex_, labelY, labelTxt, xloc.bar_index, yloc.price, NA(Color), label.style_label_left, labelColor, profileLeftSizeInput, text.align_left, labelTooltip)
        __block_result_10__ = na
        if profileLeftShowTotalsInput:
            lastDn: IBPersistent[float] = na(float)
            lastUp: IBPersistent[float] = na(float)
            totalDn: float = array.sum(squashedDn)
            totalUp: float = array.sum(squashedUp)
            labelY: float = profileHi_ + 2 * (profileHi_ - array.get(profilePrices_, qtyOfLevels_ - 1))
            labelTxt: str = ('🠅\u2009' if totalDn > lastDn else '🠇\u2009' if totalDn < lastDn else '') + string.tostring(totalDn, formatString)
            labelColor: Color = profileLeftBearTColorInput if totalDn > totalUp else color.new(profileLeftBearTColorInput, 40)
            label.new(profileBarIndex_, labelY, labelTxt, xloc.bar_index, yloc.price, NA(Color), label.style_label_right, labelColor, profileLeftTotalsSizeInput, text.align_right)
            labelTxt = string.tostring(totalUp, formatString) + ('\u2009🠅' if totalUp > lastUp else '\u2009🠇' if totalUp < lastUp else '')
            labelColor = profileLeftBullTColorInput if totalUp > totalDn else color.new(profileLeftBullTColorInput, 40)
            label.new(profileBarIndex_, labelY, labelTxt, xloc.bar_index, yloc.price, NA(Color), label.style_label_left, labelColor, profileLeftTotalsSizeInput, text.align_left)
            lastDn = totalDn
            lastUp = totalUp
            __block_result_10__ = lastUp
        return __block_result_10__

    def getRtUpdate():
        updUp: IBPersistent[bool] = False
        updDn: IBPersistent[bool] = False
        prevClose: IBPersistent[float] = open
        flat: bool = close == prevClose
        updUp = updUp if flat else close > prevClose
        updDn = updDn if flat else close < prevClose
        prevClose = close
        lastVolume: IBPersistent[float] = volume
        if barstate.isnew:
            lastVolume = 0.0
        newVolume: float = nz(volume) - lastVolume
        lastVolume = nz(volume)
        array.push(rtTimes_, timenow)
        array.push(rtPrices_, close)
        array.push(rtVolumes_, newVolume)
        array.push(rtUps_, updUp)
        array.set(tickUp, 0, updUp)
        return newVolume

    def squashRtUpdates(profileWasRescaled: Series[bool]):
        rtUpdateNo: int = 0 if profileWasRescaled else qtyOfRtUpdates_ - 1
        levelToUpdate: int = 0
        __block_result_11__ = na
        while rtUpdateNo < qtyOfRtUpdates_:
            priceToSlot = array.get(rtPrices_, rtUpdateNo)
            if qtyOfLevels_ > 1:
                for levelNo in pine_range(0, qtyOfLevels_ - 1, 1):
                    if levelNo < qtyOfLevels_ - 1:
                        levelToMatch: float = math.avg(array.get(profilePrices_, levelNo), array.get(profilePrices_, levelNo + 1))
                        if priceToSlot <= levelToMatch:
                            levelToUpdate = levelNo
                            break
                    else:
                        levelToUpdate = levelNo
            tickWasUp = array.get(rtUps_, rtUpdateNo)
            squashedTicks = squashedTicksUp_ if tickWasUp else squashedTicksDn_
            array.set(squashedTicks, levelToUpdate, array.get(squashedTicks, levelToUpdate) + 1)
            squashedVolumes = squashedVolumesUp_ if tickWasUp else squashedVolumesDn_
            array.set(squashedVolumes, levelToUpdate, array.get(squashedVolumes, levelToUpdate) + array.get(rtVolumes_, rtUpdateNo))
            squashedTimes = squashedTimesUp_ if tickWasUp else squashedTimesDn_
            array.set(squashedTimes, levelToUpdate, array.get(squashedTimes, levelToUpdate) + array.get(rtTimes_, rtUpdateNo))
            rtUpdateNo = rtUpdateNo + 1
            __block_result_11__ = rtUpdateNo
        return __block_result_11__

    tfInMinutes_1 = tfInMinutes()
    tfInMinutes_2 = tfInMinutes(profileResetTfInput)
    if profileResetTfInput != '' and tfInMinutes_1 > tfInMinutes_2:
        runtime.error("The chart's timeframe must be >= " + profileResetTfInput)
    if na(volume):
        printMessage('No volume data for this symbol.', GRAY)
    newTf: bool = cast_bool(ta.change(time(profileResetTfInput)))
    _, stDirection = ta.supertrend(trendSTFactorInput, trendSTLengthInput)
    stChangedDirection = inline_series(ta.change(stDirection), 1)
    wwChangedDirection = inline_series(ta.change(wwLBTrend(close, trendWWSmoothingLengthInput)), 1)
    __block_result_12__ = na
    if profileResetOnTF:
        __block_result_12__ = newTf
    elif profileResetOnST:
        __block_result_12__ = stChangedDirection
    elif profileResetOnWW:
        __block_result_12__ = wwChangedDirection
    else:
        __block_result_12__ = barstate.isnew
    reset: bool = __block_result_12__
    if barstate.isfirst:
        profileInitLevelStrings(profileMaxWidth_)
    if barstate.isrealtime:
        scriptJustLoaded: IBPersistent[bool] = True
        beginNewProfile_ = scriptJustLoaded or (reset and barstate.isnew)
        rescaleProfile_ = high > profileHi_ or low < profileLo_
        profileWasRescaled: bool = False
        if beginNewProfile_:
            profileBarIndex_ = bar_index + profileOffsetInput
            profileHi_ = high
            profileLo_ = low
            qtyOfLevels_ = profileRecalcLevels(profileHi_, profileLo_, profileLevelsMaxQtyInput)
            array.clear(rtTimes_)
            array.clear(rtPrices_)
            array.clear(rtVolumes_)
            array.clear(rtUps_)
            qtyOfRtUpdates_ = 0
            qtyOfRtVolumes_ = 0.0
            profileWasRescaled = True
        elif rescaleProfile_:
            profileHi_ = math.max(high, profileHi_)
            profileLo_ = math.min(low, profileLo_)
            qtyOfLevels_ = profileRecalcLevels(profileHi_, profileLo_, profileLevelsMaxQtyInput)
            profileWasRescaled = True
        qtyOfRtVolumes_ = qtyOfRtVolumes_ + getRtUpdate()
        qtyOfRtUpdates_ = qtyOfRtUpdates_ + 1
        squashRtUpdates(profileWasRescaled)
        leftValues: list[float] = array.new_float(qtyOfLevels_, 0.0)
        leftWidths: list[int] = array.new_int(qtyOfLevels_, 0)
        leftHeights: list[int] = array.new_int(qtyOfLevels_, 0)
        leftColors: list[Color] = array.new_color(qtyOfLevels_)
        rightValues: list[float] = array.new_float(qtyOfLevels_, 0.0)
        rightWidths: list[int] = array.new_int(qtyOfLevels_, 0)
        rightHeights: list[int] = array.new_int(qtyOfLevels_, 0)
        rightColors: list[Color] = array.new_color(qtyOfLevels_)
        profileRemovePrevious(profileBarIndex_)
        if not scriptJustLoaded:
            profileBuildAgeOfLevels(leftHeights, rightHeights)
            if profileDOUBLE_VOLUME:
                profileBuildTwoSides(leftWidths, leftColors, rightWidths, rightColors, VOLUME)
                profileDrawTwoSides(leftWidths, leftHeights, leftColors, rightWidths, rightHeights, rightColors, VOLUME)
            elif profileDOUBLE_TICKS:
                profileBuildTwoSides(leftWidths, leftColors, rightWidths, rightColors, TICKS)
                profileDrawTwoSides(leftWidths, leftHeights, leftColors, rightWidths, rightHeights, rightColors, TICKS)
            else:
                if profileLEFT_VOLUME:
                    profileBuildOneSide(leftValues, leftWidths, leftColors, LEFT_PROFILE, VOLUME, profileLeftCalcDeltaInput)
                    profileDrawOneSide(leftValues, leftWidths, leftHeights, rightHeights, leftColors, LEFT_PROFILE, VOLUME)
                elif profileLEFT_TICKS:
                    profileBuildOneSide(leftValues, leftWidths, leftColors, LEFT_PROFILE, TICKS, profileLeftCalcDeltaInput)
                    profileDrawOneSide(leftValues, leftWidths, leftHeights, rightHeights, leftColors, LEFT_PROFILE, TICKS)
                if profileRIGHT_VOLUME:
                    profileBuildOneSide(rightValues, rightWidths, rightColors, RIGHT_PROFILE, VOLUME, profileRightCalcDeltaInput)
                    profileDrawOneSide(rightValues, rightWidths, leftHeights, rightHeights, rightColors, RIGHT_PROFILE, VOLUME)
                elif profileRIGHT_TICKS:
                    profileBuildOneSide(rightValues, rightWidths, rightColors, RIGHT_PROFILE, TICKS, profileRightCalcDeltaInput)
                    profileDrawOneSide(rightValues, rightWidths, leftHeights, rightHeights, rightColors, RIGHT_PROFILE, TICKS)
        scriptJustLoaded = False
    plotchar(qtyOfRtUpdates_, 'Updates', '', location.top)
    plotchar(qtyOfRtVolumes_, 'Volumes', '', location.top)
    plotchar(qtyOfLevels_, 'Levels', '', location.top)
    plotchar(na, '═══════', '', location.top)
    stChangedDirectionChanged: bool = cast_bool(ta.change(stChangedDirection))
    wwChangedDirectionChanged: bool = cast_bool(ta.change(wwChangedDirection))
    trendChangedUp: bool = profileResetOnST and stChangedDirection < 0 and stChangedDirectionChanged or (profileResetOnWW and wwChangedDirection > 0 and wwChangedDirectionChanged)
    trendChangedDn: bool = profileResetOnST and stChangedDirection > 0 and stChangedDirectionChanged or (profileResetOnWW and wwChangedDirection < 0 and wwChangedDirectionChanged)
    trendIsUp: Persistent[bool] = na(bool)
    trendIsDn: Persistent[bool] = na(bool)
    trendIsUp = trendChangedUp if not trendIsUp else not trendChangedDn
    trendIsDn = trendChangedDn if not trendIsDn else not trendChangedUp
    plotchar(trendMarkerShowChangesInput and (barstate.isrealtime or not trendMarkerChangesRtInput) and trendChangedUp, 'Trend change up', '🠅', location.top, trendMarkerBullColorInput, size=size.tiny)
    plotchar(trendMarkerShowChangesInput and (barstate.isrealtime or not trendMarkerChangesRtInput) and trendChangedDn, 'Trend change down', '🠇', location.top, trendMarkerBearColorInput, size=size.tiny)
    plotchar(low if trendMarkerShowStatesInput and (barstate.isrealtime or not trendMarkerStatesRtInput) and trendIsUp else na, 'Trend state up', '🠅', location.absolute, trendMarkerBullColorInput, size=size.tiny)
    plotchar(high if trendMarkerShowStatesInput and (barstate.isrealtime or not trendMarkerStatesRtInput) and trendIsDn else na, 'Trend state down', '🠇', location.absolute, trendMarkerBearColorInput, size=size.tiny)
    tickIsUp: bool = array.get(tickUp, 0)
    bodyColorModeNO: Persistent[bool] = candleBodyModeInput == CAND0
    bodyColorModeUP: Persistent[bool] = candleBodyModeInput == CAND1
    bodyColorModeOC: Persistent[bool] = candleBodyModeInput == CAND2
    bodyColorModeTR: Persistent[bool] = candleBodyModeInput == CAND3
    __block_result_13__ = na
    if bodyColorModeNO:
        __block_result_13__ = NA(Color)
    elif bodyColorModeOC:
        __block_result_13__ = candleBodyBullTColorInput if tickIsUp else candleBodyBearTColorInput
    elif bodyColorModeOC:
        __block_result_13__ = candleBodyBullTColorInput if close > open else candleBodyBearTColorInput
    elif bodyColorModeTR:
        __block_result_13__ = candleBodyBullTColorInput if trendIsUp else candleBodyBearTColorInput
    bodyColor: Color = __block_result_13__
    borderColorModeNO: Persistent[bool] = candleBorderModeInput == CAND0
    borderColorModeUP: Persistent[bool] = candleBorderModeInput == CAND1
    borderColorModeOC: Persistent[bool] = candleBorderModeInput == CAND2
    borderColorModeTR: Persistent[bool] = candleBorderModeInput == CAND3
    __block_result_14__ = na
    if borderColorModeNO:
        __block_result_14__ = NA(Color)
    elif borderColorModeUP:
        __block_result_14__ = candleBorderBullColorInput if tickIsUp else candleBorderBearColorInput
    elif borderColorModeOC:
        __block_result_14__ = candleBorderBullColorInput if close > open else candleBorderBearColorInput
    elif borderColorModeTR:
        __block_result_14__ = candleBorderBullColorInput if trendIsUp else candleBorderBearColorInput
    borderColor: Color = __block_result_14__
    colorCandles: bool = barstate.isrealtime or not candleColoringRtInput
    plotcandle(open, high, low, close, 'Candles', bodyColor if colorCandles else na, wickcolor=borderColor if colorCandles else na, bordercolor=borderColor if colorCandles else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)