"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barmerge, barstate, box, chart,
    close, color, format, high, hlc3, input, label, last_bar_index, line, location, low, math, na,
    nz, open, plot, plotshape, position, request, script, shape, size, string, syminfo, ta, table,
    text, time, timeframe, volume, xloc, yloc
)
from pynecore.types import Box, Color, Label, Line, Persistent, Series, Table

CORE_GROUP: str = "Core"
FILTERS_GROUP: str = "Optional Filters"
HUD_GROUP: str = "Asset Zone HUD"
PERFORMANCE_GROUP: str = "Performance"
MAX_SAFE_ZONE_SETS: int = 19
CHOCH_GROUP: str = "CHOCH Levels"
DEVIATION_GROUP: str = "Deviation Marker"
ALERTS_GROUP: str = "Alerts"


@script.indicator("Buy/Sell Zones", shorttitle="Buy/Sell Zones", overlay=True, max_lines_count=500, max_labels_count=500, max_boxes_count=200)
def main(
    structureModeInput=input.string("Fractal Odd", "Structure Mode", options=("Fractal Odd", "Real Time Internal Structure"), group=CORE_GROUP, tooltip="Choose symmetric odd-length fractal pivots or internal leg pivots with close-cross structure breaks. Both modes create zones only on CHoCH."),
    lengthInput=input.int(7, "Fractal Length", minval=3, maxval=501, group=CORE_GROUP, tooltip="Odd fractal window length; used only in Fractal Odd mode. Even values round up to the next odd value."),
    internalLengthInput=input.int(7, "Internal Structure Length", minval=2, maxval=100, group=CORE_GROUP, tooltip="Bars needed to confirm a new internal leg; default 7. Used only in Real Time Internal Structure mode."),
    barsToRightInput=input.int(10, "Bars to Right", minval=1, maxval=300, group=CORE_GROUP, tooltip="Number of chart bars used to project the active CHOCH levels to the right."),
    requireBodyInput=input.bool(True, "Break = Close Beyond Level", group=CORE_GROUP, tooltip="When enabled, a close must break the pivot. When disabled, a wick can break it."),
    useVwapFilterInput=input.bool(False, "Use VWAP Direction Filter", group=FILTERS_GROUP, tooltip="Bullish CHOCH zones require a close above the selected anchored VWAP; bearish zones require a close below it. Disabled by default."),
    vwapAnchorInput=input.string("Monthly", "VWAP Reset Period", options=("Daily", "Weekly", "Monthly"), group=FILTERS_GROUP, tooltip="Resets VWAP at the start of each day, week, or month. Monthly by default; applies to both the chart VWAP and reference-asset filter."),
    showVwapInput=input.bool(False, "Show VWAP", group=FILTERS_GROUP, tooltip="Displays the daily, weekly, or monthly VWAP used by the optional direction filter."),
    useEmaFilterInput=input.bool(False, "Use EMA Trend Filter", group=FILTERS_GROUP, tooltip="Bullish CHOCH zones require a close above the EMA; bearish zones require a close below it."),
    emaLengthInput=input.int(200, "EMA Length", minval=1, group=FILTERS_GROUP, tooltip="Length of the EMA used by the optional trend filter."),
    showEmaInput=input.bool(False, "Show EMA", group=FILTERS_GROUP, tooltip="Displays the EMA used by the optional trend filter."),
    useVolumeFilterInput=input.bool(False, "Use Relative Volume Filter", group=FILTERS_GROUP, tooltip="Skips a CHOCH zone if current volume is below average volume multiplied by the selected factor."),
    volumeLengthInput=input.int(20, "Volume Average Length", minval=1, group=FILTERS_GROUP, tooltip="Lookback used to calculate average volume."),
    volumeMultiplierInput=input.float(1.0, "Minimum Relative Volume", minval=0.0, step=0.1, group=FILTERS_GROUP, tooltip="Current volume must be at least average volume multiplied by this value."),
    useAtrRangeFilterInput=input.bool(False, "Use ATR Zone-Size Filter", group=FILTERS_GROUP, tooltip="Skips CHOCH zones whose signal-candle range is too small or too large relative to ATR."),
    atrLengthInput=input.int(14, "ATR Length", minval=1, group=FILTERS_GROUP, tooltip="Length of the ATR used to normalize the signal-candle range."),
    minAtrRangeInput=input.float(0.5, "Minimum Range in ATR", minval=0.0, step=0.1, group=FILTERS_GROUP, tooltip="Minimum accepted signal-candle range expressed as an ATR multiple."),
    maxAtrRangeInput=input.float(3.0, "Maximum Range in ATR", minval=0.1, step=0.1, group=FILTERS_GROUP, tooltip="Maximum accepted signal-candle range expressed as an ATR multiple."),
    requireConfirmedInput=input.bool(False, "Require Confirmed Bar", group=FILTERS_GROUP, tooltip="Creates a CHOCH zone only after the signal bar closes. Useful for preventing intrabar signals."),
    minimumBarsInput=input.int(0, "Minimum Bars Between CHOCH Zones", minval=0, maxval=5000, group=FILTERS_GROUP, tooltip="Skips new CHOCH zones until this many bars have elapsed since the last accepted zone. Zero disables the filter."),
    showHudInput=input.bool(True, "Show Asset Zone HUD", group=HUD_GROUP, tooltip="Displays the latest structural zone of the selected asset and its mapped signal for the chart."),
    hudAssetInput=input.symbol("CRYPTOCAP:USDT.D", "Reference Asset", group=HUD_GROUP, tooltip="Asset whose latest BUY/SELL zone will be monitored on the chart timeframe."),
    hudSizeInput=input.string("normal", "HUD Size", options=("tiny", "small", "normal", "large"), group=HUD_GROUP, tooltip="Controls the text size of the Asset Zone HUD. Default is normal."),
    calcLastBarsInput=input.int(20000, "Calc Only Last N Bars (0=all)", minval=0, maxval=50000, group=PERFORMANCE_GROUP, tooltip="Restricts object-creation logic to the latest N bars. Zero processes all loaded bars."),
    chochShowLastInput=input.int(1, "CHOCH Show Last N Zones (0=safe max)", minval=0, maxval=MAX_SAFE_ZONE_SETS, group=PERFORMANCE_GROUP, tooltip="Limits retained CHOCH sets to prevent TradingView drawing-limit failures. Zero uses the safe maximum of 19 zones."),
    chochLineUpInput=input.color(color.new('#089981'), "CHOCH Lines UP Color", group=CHOCH_GROUP, tooltip="Color of bullish CHOCH levels."),
    chochLineDownInput=input.color(color.new('#F23645'), "CHOCH Lines DN Color", group=CHOCH_GROUP, tooltip="Color of bearish CHOCH levels."),
    chochHighLowWidthInput=input.int(2, "CHOCH H/L Width", minval=1, maxval=5, group=CHOCH_GROUP, tooltip="Width of the signal candle's high and low levels."),
    chochStepWidthInput=input.int(1, "CHOCH Step Width (+/- levels)", minval=1, maxval=5, group=CHOCH_GROUP, tooltip="Width of the projected range-multiple levels."),
    halfStepColorInput=input.color(color.new('#FFFFFF'), "±0.5 Level Color", group=CHOCH_GROUP, tooltip="Solid color of +0.5 and -0.5 levels; default white."),
    minSweepDepthInput=input.float(0.7, "Min ±0.5 Sweep Strength (0–1)", minval=0.0, maxval=1.0, step=0.01, group=CHOCH_GROUP, tooltip="Minimum penetration AND exposed wick, scaled to a usable 0–1 sensitivity: 0.30 = 3%, 0.70 = 7% (default), 1.00 = 10% of the distance between ±0.5 and ±1. Higher values require clearer sweeps; 1 is not an impossible 100% band breach."),
    showPreviousSignalInput=input.bool(True, "Show Previous Setup Signal", group=CHOCH_GROUP, tooltip="When a new zone forms, keep only the latest confirmed direction triangle from the immediately preceding setup, annotated LONG or SHORT. Older setup triangles are removed; defaults to on."),
    rejectedLabelSizeInput=input.string("normal", "Rejected Label Size", options=("tiny", "small", "normal"), group=CHOCH_GROUP, tooltip="Size of the active wall's REJECTED label; small by default."),
    chochStyleInput=input.string("Dotted", "CHOCH Level Style", options=("Solid", "Dashed", "Dotted"), group=CHOCH_GROUP, tooltip="Line style used by the projected range-multiple levels."),
    boxFillUpInput=input.color(color.new(color.new('#089981'), 88), "CHOCH Box Fill UP", group=CHOCH_GROUP, tooltip="Fill color of bullish CHOCH signal-candle zones."),
    boxFillDownInput=input.color(color.new(color.new('#F23645'), 88), "CHOCH Box Fill DN", group=CHOCH_GROUP, tooltip="Fill color of bearish CHOCH signal-candle zones."),
    showWallFillInput=input.bool(True, "Shade Buyers/Sellers Wall", group=CHOCH_GROUP, tooltip="Subtly shades the area between H and L without changing the dashed center line."),
    buyersWallFillInput=input.color(color.new(color.new('#089981'), 94), "Buyers Wall Shading", group=CHOCH_GROUP, tooltip="Translucent fill between H and L of bullish zones."),
    sellersWallFillInput=input.color(color.new(color.new('#F23645'), 94), "Sellers Wall Shading", group=CHOCH_GROUP, tooltip="Translucent fill between H and L of bearish zones."),
    boxBorderUpInput=input.color(color.new('#089981'), "CHOCH Box Border UP", group=CHOCH_GROUP, tooltip="Border color of bullish CHOCH zones."),
    boxBorderDownInput=input.color(color.new('#F23645'), "CHOCH Box Border DN", group=CHOCH_GROUP, tooltip="Border color of bearish CHOCH zones."),
    showLevelLabelsInput=input.bool(True, "Show Level Labels (right side)", group=CHOCH_GROUP, tooltip="Displays H, L, EQ, and range-multiple labels at the right edge."),
    levelLabelTextInput=input.color(color.new('#D1D4DC'), "Level Label Text Color", group=CHOCH_GROUP, tooltip="Text color used by the right-side level labels."),
    labelSizeInput=input.string("normal", "Label Size", options=("tiny", "small", "normal"), group=CHOCH_GROUP, tooltip="Size of CHOCH zone and level labels."),
    zoneLabelAtrGapInput=input.float(0.35, "Zone Label Distance (ATR)", minval=0.05, maxval=5.0, step=0.05, group=CHOCH_GROUP, tooltip="Direct ATR multiplier used for the vertical distance between the broken structure line and the BUY/SELL ZONE label. Every change now directly moves the label."),
    showDeviationInput=input.bool(False, "Mark Candle Returning into Range", group=DEVIATION_GROUP, tooltip="Marks the first close returning inside the -4 to +4 range after price traded beyond it. Disabled by default."),
    deviationUpInput=input.color(color.new('#089981'), "Deviation UP Color", group=DEVIATION_GROUP, tooltip="Color of bullish return-to-range markers."),
    deviationDownInput=input.color(color.new('#F23645'), "Deviation DN Color", group=DEVIATION_GROUP, tooltip="Color of bearish return-to-range markers."),
    longTriangleAlertInput=input.bool(True, "LONG Triangle Alerts", group=ALERTS_GROUP, tooltip="Enable alerts on a newly confirmed or updated LONG sweep triangle. On by default; also included in the combined alert stream."),
    shortTriangleAlertInput=input.bool(True, "SHORT Triangle Alerts", group=ALERTS_GROUP, tooltip="Enable alerts on a newly confirmed or updated SHORT sweep triangle. On by default; also included in the combined alert stream."),
    buyZoneAlertInput=input.bool(False, "Include BUY in Combined Alert", group=ALERTS_GROUP, tooltip="Optional: includes BUY ZONE events when using TradingView's Any alert() function call condition. The separate named BUY Zone Created condition works without this toggle."),
    sellZoneAlertInput=input.bool(False, "Include SELL in Combined Alert", group=ALERTS_GROUP, tooltip="Optional: includes SELL ZONE events when using TradingView's Any alert() function call condition. The separate named SELL Zone Created condition works without this toggle."),
    returnToRangeAlertInput=input.bool(False, "Include Return-to-Range in Combined Alert", group=ALERTS_GROUP, tooltip="Optional: includes return-to-range events when using TradingView's Any alert() function call condition. The separate named Price Returning to Range condition works without this toggle.")
):
    vwapPeriod: str = 'D' if vwapAnchorInput == 'Daily' else 'W' if vwapAnchorInput == 'Weekly' else 'M'

    def f_lineStyle(styleText: str):
        return line.style_solid if styleText == 'Solid' else line.style_dashed if styleText == 'Dashed' else line.style_dotted

    def f_labelSize(sizeText: str):
        return size.tiny if sizeText == 'tiny' else size.small if sizeText == 'small' else size.large if sizeText == 'large' else size.normal

    def f_levelLabel(x: int, y: float, labelText: str, labelSize, prominent: bool):
        return label.new(x, y, labelText, xloc=xloc.bar_time, style=label.style_label_left, textcolor=color.new(levelLabelTextInput, 0 if prominent else 50), color=color.new('#00000000'), size=labelSize)

    activeLines: Persistent[list[Line]] = array.new_line()
    activeLabels: Persistent[list[Label]] = array.new_label()
    storedLines: Persistent[list[Line]] = array.new_line()
    storedLabels: Persistent[list[Label]] = array.new_label()
    storedBoxes: Persistent[list[Box]] = array.new_box()
    storedWallBoxes: Persistent[list[Box]] = array.new_box()
    storedLineCounts: Persistent[list[int]] = array.new_int()
    storedLabelCounts: Persistent[list[int]] = array.new_int()
    storedLowTriangles: Persistent[list[Label]] = array.new_label()
    storedHighTriangles: Persistent[list[Label]] = array.new_label()
    repeatedHighTriangles: Persistent[list[Label]] = array.new_label()
    repeatedHighZoneIds: Persistent[list[int]] = array.new_int()
    storedZoneIds: Persistent[list[int]] = array.new_int()
    currentZoneId: Persistent[int] = 0
    previousTriangle: Persistent[Label] = na(Label)
    previousSignalText: Persistent[Label] = na(Label)
    pendingBrokenLevel: Persistent[float] = na(float)
    pendingStructureStartTime: Persistent[int] = na(int)
    pendingZoneLabelGap: Persistent[float] = na(float)
    pendingRangeBoxTop: Persistent[float] = na(float)
    pendingRangeBoxBottom: Persistent[float] = na(float)

    def f_addLevel(linesArray: list[Line], labelsArray: list[Label], leftTime: int, rightTime: int, level: float, labelText: str, lineColor: Color, lineStyle: str, lineWidth: int, labelSize, prominent: bool):
        levelLine: Line = line.new(leftTime, level, rightTime, level, xloc=xloc.bar_time, color=lineColor, style=lineStyle, width=lineWidth)
        array.push(linesArray, levelLine)
        levelLabel: Label = na(Label)
        if showLevelLabelsInput:
            levelLabel = f_levelLabel(rightTime, level, labelText, labelSize, prominent)
            if labelText == '+0.5' or labelText == '-0.5':
                label.set_textcolor(levelLabel, halfStepColorInput)
            if labelText == 'BUYERS WALL' or labelText == 'SELLERS WALL':
                label.set_textcolor(levelLabel, lineColor)
                label.set_text_formatting(levelLabel, text.format_bold)
        return array.push(labelsArray, levelLabel)

    def f_trimStoredSets():
        effectiveZoneLimit: int = MAX_SAFE_ZONE_SETS if chochShowLastInput == 0 else math.min(chochShowLastInput, MAX_SAFE_ZONE_SETS)
        __block_result__ = na
        while array.size(storedBoxes) > effectiveZoneLimit:
            oldBox: Box = array.shift(storedBoxes)
            if not na(oldBox):
                box.delete(oldBox)
            oldWallBox: Box = array.shift(storedWallBoxes)
            if not na(oldWallBox):
                box.delete(oldWallBox)
            oldZoneId: int = array.shift(storedZoneIds)
            repeatedCount: int = array.size(repeatedHighZoneIds)
            if repeatedCount > 0:
                for offset in pine_range(0, repeatedCount - 1):
                    repeatIndex: int = repeatedCount - 1 - offset
                    if array.get(repeatedHighZoneIds, repeatIndex) == oldZoneId:
                        label.delete(array.remove(repeatedHighTriangles, repeatIndex))
                        array.remove(repeatedHighZoneIds, repeatIndex)
            oldLowTriangle: Label = array.shift(storedLowTriangles)
            oldHighTriangle: Label = array.shift(storedHighTriangles)
            if not na(oldLowTriangle):
                label.delete(oldLowTriangle)
            if not na(oldHighTriangle):
                label.delete(oldHighTriangle)
            lineCount: int = array.shift(storedLineCounts)
            if lineCount > 0:
                for index in pine_range(0, lineCount - 1):
                    oldLine: Line = array.shift(storedLines)
                    if not na(oldLine):
                        line.delete(oldLine)
            labelCount: int = array.shift(storedLabelCounts)
            __block_result_1__ = na
            if labelCount > 0:
                __block_result_2__ = na
                for index in pine_range(0, labelCount - 1):
                    oldLabel: Label = array.shift(storedLabels)
                    __block_result_3__ = na
                    if not na(oldLabel):
                        __block_result_3__ = label.delete(oldLabel)
                    __block_result_2__ = __block_result_3__
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    def f_keepPreviousSignal(lowTriangle: Label, highTriangle: Label, oldPrevious: Label, oldText: Label, textGap: float):
        if not na(oldPrevious):
            label.delete(oldPrevious)
        if not na(oldText):
            label.delete(oldText)

        while array.size(repeatedHighTriangles) > 0:
            label.delete(array.pop(repeatedHighTriangles))
            array.pop(repeatedHighZoneIds)
        keptTriangle: Label = lowTriangle
        if not na(highTriangle) and (na(keptTriangle) or label.get_x(highTriangle) >= label.get_x(keptTriangle)):
            keptTriangle = highTriangle
        storedCount: int = array.size(storedLowTriangles)
        if storedCount > 0:
            for index in pine_range(0, storedCount - 1):
                olderLow: Label = array.get(storedLowTriangles, index)
                olderHigh: Label = array.get(storedHighTriangles, index)
                if not na(olderLow) and olderLow != keptTriangle:
                    label.delete(olderLow)
                if not na(olderHigh) and olderHigh != keptTriangle:
                    label.delete(olderHigh)
                array.set(storedLowTriangles, index, na)
                array.set(storedHighTriangles, index, na)
        keptText: Label = na(Label)
        if not na(keptTriangle):
            label.set_size(keptTriangle, size.normal)
            wasLong: bool = keptTriangle == lowTriangle
            keptText = label.new(label.get_x(keptTriangle), label.get_y(keptTriangle) + (-textGap if wasLong else textGap), 'LONG' if wasLong else 'SHORT', xloc=xloc.bar_time, yloc=yloc.price, color=color.new(chart.bg_color, 10), style=label.style_label_center, textcolor=color.new('#089981') if wasLong else color.new('#F23645'), size=size.normal)
        return (keptTriangle, keptText)

    def f_storeActiveSet(zoneBox: Box):
        lineCount: int = array.size(activeLines)
        labelCount: int = array.size(activeLabels)
        if lineCount > 0:
            for index in pine_range(0, lineCount - 1):
                array.push(storedLines, array.get(activeLines, index))
        if labelCount > 0:
            for index in pine_range(0, labelCount - 1):
                array.push(storedLabels, array.get(activeLabels, index))
        array.push(storedBoxes, zoneBox)
        array.push(storedZoneIds, currentZoneId)
        array.push(storedLineCounts, lineCount)
        array.push(storedLabelCounts, labelCount)
        array.push(storedLowTriangles, na)
        array.push(storedHighTriangles, na)
        return f_trimStoredSets()

    def f_freezeActive(freezeTime: int):
        if array.size(storedWallBoxes) > 0:
            wallBox: Box = array.get(storedWallBoxes, array.size(storedWallBoxes) - 1)
            if not na(wallBox):
                box.set_right(wallBox, freezeTime)
        lineCount: int = math.min(23, array.size(activeLines))
        if lineCount > 0:
            for index in pine_range(0, lineCount - 1):
                activeLine: Line = array.get(activeLines, index)
                if not na(activeLine):
                    line.set_x2(activeLine, freezeTime)
        levelLabelCount: int = math.min(23, array.size(activeLabels))
        __block_result_4__ = na
        if levelLabelCount > 0:
            __block_result_5__ = na
            for index in pine_range(0, levelLabelCount - 1):
                activeLabel: Label = array.get(activeLabels, index)
                __block_result_6__ = na
                if not na(activeLabel):
                    __block_result_6__ = label.set_x(activeLabel, freezeTime)
                __block_result_5__ = __block_result_6__
            __block_result_4__ = __block_result_5__
        return __block_result_4__

    def f_hideActiveLevel(index: int):
        if array.size(activeLines) > index:
            levelLine: Line = array.get(activeLines, index)
            if not na(levelLine):
                line.set_color(levelLine, na)
        __block_result_7__ = na
        if array.size(activeLabels) > index:
            levelLabel: Label = array.get(activeLabels, index)
            __block_result_8__ = na
            if not na(levelLabel):
                __block_result_8__ = label.set_textcolor(levelLabel, na)
            __block_result_7__ = __block_result_8__
        return __block_result_7__

    def f_showExtendedLevels(firstIndex: int, lastIndex: int, directionColor: Color):
        __block_result_9__ = na
        for index in pine_range(firstIndex, lastIndex):
            if array.size(activeLines) > index:
                extendedLine: Line = array.get(activeLines, index)
                if not na(extendedLine):
                    line.set_color(extendedLine, color.new(directionColor, 50))
            __block_result_10__ = na
            if array.size(activeLabels) > index:
                extendedLabel: Label = array.get(activeLabels, index)
                __block_result_11__ = na
                if not na(extendedLabel):
                    __block_result_11__ = label.set_textcolor(extendedLabel, color.new(levelLabelTextInput, 50))
                __block_result_10__ = __block_result_11__
            __block_result_9__ = __block_result_10__
        return __block_result_9__

    def f_createChochSet(direction: int, zoneHigh: float, zoneLow: float, extensionMilliseconds: int, oneBarMilliseconds: int):
        array.clear(activeLines)
        array.clear(activeLabels)

        zoneRange: float = math.max(syminfo.mintick, zoneHigh - zoneLow)
        equilibrium: float = zoneHigh - zoneRange * 0.5
        leftTime: int = time
        rightTime: int = time + extensionMilliseconds
        directionColor: Color = chochLineUpInput if direction == 1 else chochLineDownInput
        stepColor: Color = color.new(directionColor, 50)
        lineStyle = f_lineStyle(chochStyleInput)
        labelSize = f_labelSize(labelSizeInput)

        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneHigh, 'H', directionColor, line.style_solid, chochHighLowWidthInput, labelSize, True)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneLow, 'L', directionColor, line.style_solid, chochHighLowWidthInput, labelSize, True)
        entryText: str = 'BUYERS WALL' if direction == 1 else 'SELLERS WALL'
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, equilibrium, entryText, directionColor, line.style_dashed, 2, labelSize, True)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneHigh + zoneRange * 0.5, '+0.5', halfStepColorInput, line.style_solid, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneHigh + zoneRange, '+1', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneHigh + zoneRange * 1.5, '+1.5', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneHigh + zoneRange * 2.0, '+2', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneHigh + zoneRange * 3.0, '+3', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneHigh + zoneRange * 4.0, '+4', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneLow - zoneRange * 0.5, '-0.5', halfStepColorInput, line.style_solid, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneLow - zoneRange, '-1', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneLow - zoneRange * 1.5, '-1.5', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneLow - zoneRange * 2.0, '-2', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneLow - zoneRange * 3.0, '-3', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneLow - zoneRange * 4.0, '-4', stepColor, lineStyle, chochStepWidthInput, labelSize, False)

        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneHigh + zoneRange * 5.0, '+5', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneHigh + zoneRange * 6.0, '+6', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneHigh + zoneRange * 7.0, '+7', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneHigh + zoneRange * 8.0, '+8', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneLow - zoneRange * 5.0, '-5', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneLow - zoneRange * 6.0, '-6', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneLow - zoneRange * 7.0, '-7', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        f_addLevel(activeLines, activeLabels, leftTime, rightTime, zoneLow - zoneRange * 8.0, '-8', stepColor, lineStyle, chochStepWidthInput, labelSize, False)
        for hiddenIndex in pine_range(15, 22):
            f_hideActiveLevel(hiddenIndex)

        safeStructureStart: int = leftTime if na(pendingStructureStartTime) else pendingStructureStartTime
        safeBrokenLevel: float = equilibrium if na(pendingBrokenLevel) else pendingBrokenLevel
        structureMiddleTime: int = safeStructureStart + cast_int((leftTime - safeStructureStart) / 2)
        structureLine: Line = line.new(safeStructureStart, safeBrokenLevel, leftTime, safeBrokenLevel, xloc=xloc.bar_time, color=directionColor, style=line.style_solid, width=2)
        array.push(activeLines, structureLine)

        labelGap: float = math.max(nz(pendingZoneLabelGap, zoneRange * 0.5), syminfo.mintick * 20.0)
        zoneLabelY: float = safeBrokenLevel + labelGap if direction == 1 else safeBrokenLevel - labelGap
        zoneText: str = 'BUY ZONE' if direction == 1 else 'SELL ZONE'
        zoneLabelStyle = label.style_label_down if direction == 1 else label.style_label_up
        zoneLabel: Label = label.new(structureMiddleTime, zoneLabelY, zoneText, xloc=xloc.bar_time, style=zoneLabelStyle, textcolor=directionColor, color=color.new(chart.bg_color, 5), size=labelSize, textalign=text.align_center)
        array.push(activeLabels, zoneLabel)

        borderColor: Color = boxBorderUpInput if direction == 1 else boxBorderDownInput
        fillColor: Color = boxFillUpInput if direction == 1 else boxFillDownInput
        rawRangeTop: float = nz(pendingRangeBoxTop, zoneHigh)
        rawRangeBottom: float = nz(pendingRangeBoxBottom, zoneLow)
        rangeBoxTop: float = math.max(rawRangeTop, rawRangeBottom)
        rangeBoxBottom: float = math.min(rawRangeTop, rawRangeBottom)
        zoneBox: Box = box.new(safeStructureStart, rangeBoxTop, leftTime + oneBarMilliseconds, rangeBoxBottom, xloc=xloc.bar_time, border_color=borderColor, bgcolor=fillColor, border_width=1, border_style=line.style_dotted)
        f_storeActiveSet(zoneBox)
        wallFillColor: Color = buyersWallFillInput if direction == 1 else sellersWallFillInput
        wallBox: Box = box.new(leftTime, zoneHigh, rightTime, zoneLow, xloc=xloc.bar_time, border_color=color.new('#00000000'), bgcolor=wallFillColor if showWallFillInput else color.new('#00000000'))
        return array.push(storedWallBoxes, wallBox)

    def f_internalLeg(lookback: int):
        currentLeg: Persistent[int] = 0
        foundHigh: bool = not na(high[lookback]) and high[lookback] > ta.highest(high, lookback)
        foundLow: bool = not na(low[lookback]) and low[lookback] < ta.lowest(low, lookback)
        if foundHigh:
            currentLeg = 0
        elif foundLow:
            currentLeg = 1
        return currentLeg

    def f_referenceZoneState(strength: int):
        referencePivotHigh: float = ta.pivothigh(high, strength, strength)
        referencePivotLow: float = ta.pivotlow(low, strength, strength)
        referenceVwap: float = ta.vwap(hlc3, timeframe.change(vwapPeriod))
        referenceEma: float = ta.ema(close, emaLengthInput)
        referenceAverageVolume: float = ta.sma(volume, volumeLengthInput)
        referenceAtr: float = ta.atr(atrLengthInput)

        referenceUpLevel: Persistent[float] = na(float)
        referenceDownLevel: Persistent[float] = na(float)
        referenceUpBroken: Persistent[bool] = False
        referenceDownBroken: Persistent[bool] = False
        referenceBreakDirection: Persistent[int] = 0
        referenceZoneDirection: Persistent[int] = 0
        referenceLastZoneBar: Persistent[int] = na(int)

        referenceLeg: Series[int] = f_internalLeg(internalLengthInput)
        referenceNewHigh: bool = referenceLeg == 0 and referenceLeg[1] == 1
        referenceNewLow: bool = referenceLeg == 1 and referenceLeg[1] == 0
        internalMode: bool = structureModeInput == 'Real Time Internal Structure'
        if referenceNewHigh if internalMode else not na(referencePivotHigh):
            referenceUpLevel = high[internalLengthInput] if internalMode else referencePivotHigh
            referenceUpBroken = False
        if referenceNewLow if internalMode else not na(referencePivotLow):
            referenceDownLevel = low[internalLengthInput] if internalMode else referencePivotLow
            referenceDownBroken = False

        referenceCloseCrossUp: bool = ta.crossover(close, referenceUpLevel)
        referenceCloseCrossDown: bool = ta.crossunder(close, referenceDownLevel)
        referenceBreakUp: bool = not na(referenceUpLevel) and (not referenceUpBroken) and (referenceCloseCrossUp if internalMode else close > referenceUpLevel if requireBodyInput else high > referenceUpLevel)
        referenceBreakDown: bool = not na(referenceDownLevel) and (not referenceDownBroken) and (referenceCloseCrossDown if internalMode else close < referenceDownLevel if requireBodyInput else low < referenceDownLevel)
        referenceVolumePass: bool = not useVolumeFilterInput or (not na(volume) and (not na(referenceAverageVolume)) and (volume >= referenceAverageVolume * volumeMultiplierInput))
        referenceMinAtr: float = math.min(minAtrRangeInput, maxAtrRangeInput)
        referenceMaxAtr: float = math.max(minAtrRangeInput, maxAtrRangeInput)
        referenceAtrPass: bool = not useAtrRangeFilterInput or (not na(referenceAtr) and high - low >= referenceAtr * referenceMinAtr and (high - low <= referenceAtr * referenceMaxAtr))
        referenceConfirmedPass: bool = not requireConfirmedInput or barstate.isconfirmed
        referenceBullPass: bool = (not useVwapFilterInput or (not na(referenceVwap) and close > referenceVwap)) and (not useEmaFilterInput or (not na(referenceEma) and close > referenceEma))
        referenceBearPass: bool = (not useVwapFilterInput or (not na(referenceVwap) and close < referenceVwap)) and (not useEmaFilterInput or (not na(referenceEma) and close < referenceEma))

        if referenceBreakUp:
            referenceCooldownPass: bool = minimumBarsInput == 0 or na(referenceLastZoneBar) or bar_index - referenceLastZoneBar >= minimumBarsInput
            referenceIsBullishChoch: bool = referenceBreakDirection == -1
            referenceUpBroken = True
            if referenceIsBullishChoch and referenceVolumePass and referenceAtrPass and referenceConfirmedPass and referenceBullPass and referenceCooldownPass:
                referenceZoneDirection = 1
                referenceLastZoneBar = bar_index
            referenceBreakDirection = 1

        if referenceBreakDown:
            referenceCooldownPass: bool = minimumBarsInput == 0 or na(referenceLastZoneBar) or bar_index - referenceLastZoneBar >= minimumBarsInput
            referenceIsBearishChoch: bool = referenceBreakDirection == 1
            referenceDownBroken = True
            if referenceIsBearishChoch and referenceVolumePass and referenceAtrPass and referenceConfirmedPass and referenceBearPass and referenceCooldownPass:
                referenceZoneDirection = -1
                referenceLastZoneBar = bar_index
            referenceBreakDirection = -1

        return referenceZoneDirection

    inCalculationWindow: bool = calcLastBarsInput == 0 or bar_index >= last_bar_index - calcLastBarsInput
    oddLength: int = lengthInput + 1 if lengthInput % 2 == 0 else lengthInput
    pivotStrength: int = cast_int(oddLength / 2)
    internalMode: bool = structureModeInput == 'Real Time Internal Structure'
    internalLeg: Series[int] = f_internalLeg(internalLengthInput)
    internalPivotHigh: bool = internalLeg == 0 and internalLeg[1] == 1
    internalPivotLow: bool = internalLeg == 1 and internalLeg[1] == 0
    timeframeSeconds: int = timeframe.in_seconds(timeframe.period)
    extensionMilliseconds: int = timeframeSeconds * 1000 * barsToRightInput
    oneBarMilliseconds: int = timeframeSeconds * 1000

    pivotHighValue: float = ta.pivothigh(high, pivotStrength, pivotStrength)
    pivotLowValue: float = ta.pivotlow(low, pivotStrength, pivotStrength)
    pivotWindowLow: float = ta.lowest(low, pivotStrength + 1)
    pivotWindowHigh: float = ta.highest(high, pivotStrength + 1)
    internalWindowLow: float = ta.lowest(low, internalLengthInput + 1)
    internalWindowHigh: float = ta.highest(high, internalLengthInput + 1)
    vwapValue: float = ta.vwap(hlc3, timeframe.change(vwapPeriod))
    emaValue: float = ta.ema(close, emaLengthInput)
    averageVolume: float = ta.sma(volume, volumeLengthInput)
    atrValue: float = ta.atr(atrLengthInput)
    referenceZoneState: int = request.security(hudAssetInput, timeframe.period, f_referenceZoneState(pivotStrength), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off, ignore_invalid_symbol=True)

    volumeFilterPass: bool = not useVolumeFilterInput or (not na(volume) and (not na(averageVolume)) and (volume >= averageVolume * volumeMultiplierInput))
    lowerAtrMultiple: float = math.min(minAtrRangeInput, maxAtrRangeInput)
    upperAtrMultiple: float = math.max(minAtrRangeInput, maxAtrRangeInput)
    signalRange: float = high - low
    atrRangeFilterPass: bool = not useAtrRangeFilterInput or (not na(atrValue) and signalRange >= atrValue * lowerAtrMultiple and (signalRange <= atrValue * upperAtrMultiple))
    confirmedFilterPass: bool = not requireConfirmedInput or barstate.isconfirmed
    commonFilterPass: bool = volumeFilterPass and atrRangeFilterPass and confirmedFilterPass
    bullishDirectionPass: bool = not useVwapFilterInput or (not na(vwapValue) and close > vwapValue)
    bullishDirectionPass = bullishDirectionPass and (not useEmaFilterInput or (not na(emaValue) and close > emaValue))
    bearishDirectionPass: bool = not useVwapFilterInput or (not na(vwapValue) and close < vwapValue)
    bearishDirectionPass = bearishDirectionPass and (not useEmaFilterInput or (not na(emaValue) and close < emaValue))

    bullishBreakLevel: Persistent[float] = na(float)
    bullishLevelStartTime: Persistent[int] = na(int)
    bullishRangeLow: Persistent[float] = na(float)
    bullishLevelBroken: Persistent[bool] = False
    bearishBreakLevel: Persistent[float] = na(float)
    bearishLevelStartTime: Persistent[int] = na(int)
    bearishRangeHigh: Persistent[float] = na(float)
    bearishLevelBroken: Persistent[bool] = False
    lastBreakDirection: Persistent[int] = 0
    chochActive: Persistent[bool] = False
    activeChochDirection: Persistent[int] = 0
    currentChochHigh: Persistent[float] = na(float)
    currentChochLow: Persistent[float] = na(float)
    currentChochRange: Persistent[float] = na(float)
    lastAcceptedChochBar: Persistent[int] = na(int)
    outOfRangeUp: Persistent[bool] = False
    outOfRangeDown: Persistent[bool] = False
    upperExtensionShown: Persistent[bool] = False
    lowerExtensionShown: Persistent[bool] = False

    lowestConfirmedSweep: Persistent[float] = na(float)
    highestConfirmedSweep: Persistent[float] = na(float)
    highSweepArmed: Persistent[bool] = True
    pendingLowSweep: Persistent[float] = na(float)
    pendingHighSweep: Persistent[float] = na(float)
    pendingLowBodyTop: Persistent[float] = na(float)
    pendingHighBodyBottom: Persistent[float] = na(float)
    pendingLowBar: Persistent[int] = na(int)
    pendingHighBar: Persistent[int] = na(int)
    pendingLowTime: Persistent[int] = na(int)
    pendingHighTime: Persistent[int] = na(int)
    activeLowTriangle: Persistent[Label] = na(Label)
    activeHighTriangle: Persistent[Label] = na(Label)

    activeWallRejectedLabel: Persistent[Label] = na(Label)
    activeWallRejectedWick: Persistent[float] = na(float)

    if inCalculationWindow:
        if internalPivotHigh if internalMode else not na(pivotHighValue):
            bullishBreakLevel = high[internalLengthInput] if internalMode else pivotHighValue
            bullishLevelStartTime = time[internalLengthInput] if internalMode else time[pivotStrength]
            bullishRangeLow = internalWindowLow if internalMode else pivotWindowLow
            bullishLevelBroken = False
            if chochActive and activeChochDirection == -1:
                if bullishBreakLevel <= currentChochHigh + currentChochRange * 4.0:
                    f_hideActiveLevel(8)
                if bullishBreakLevel <= currentChochHigh + currentChochRange * 3.0:
                    f_hideActiveLevel(7)
                if bullishBreakLevel <= currentChochHigh + currentChochRange * 2.0:
                    f_hideActiveLevel(6)
                if bullishBreakLevel <= currentChochHigh + currentChochRange * 1.5:
                    f_hideActiveLevel(5)
                if bullishBreakLevel <= currentChochHigh + currentChochRange:
                    f_hideActiveLevel(4)

        if internalPivotLow if internalMode else not na(pivotLowValue):
            bearishBreakLevel = low[internalLengthInput] if internalMode else pivotLowValue
            bearishLevelStartTime = time[internalLengthInput] if internalMode else time[pivotStrength]
            bearishRangeHigh = internalWindowHigh if internalMode else pivotWindowHigh
            bearishLevelBroken = False
            if chochActive and activeChochDirection == 1:
                if bearishBreakLevel >= currentChochLow - currentChochRange * 4.0:
                    f_hideActiveLevel(14)
                if bearishBreakLevel >= currentChochLow - currentChochRange * 3.0:
                    f_hideActiveLevel(13)
                if bearishBreakLevel >= currentChochLow - currentChochRange * 2.0:
                    f_hideActiveLevel(12)
                if bearishBreakLevel >= currentChochLow - currentChochRange * 1.5:
                    f_hideActiveLevel(11)
                if bearishBreakLevel >= currentChochLow - currentChochRange:
                    f_hideActiveLevel(10)

    if inCalculationWindow:
        if not na(bullishBreakLevel) and (not bullishLevelBroken):
            bullishRangeLow = math.min(nz(bullishRangeLow, low), low)
        if not na(bearishBreakLevel) and (not bearishLevelBroken):
            bearishRangeHigh = math.max(nz(bearishRangeHigh, high), high)

    internalCrossUp: bool = ta.crossover(close, bullishBreakLevel)
    internalCrossDown: bool = ta.crossunder(close, bearishBreakLevel)
    bullishBreak: bool = inCalculationWindow and (not na(bullishBreakLevel)) and (not bullishLevelBroken) and (internalCrossUp if internalMode else close > bullishBreakLevel if requireBodyInput else high > bullishBreakLevel)
    bearishBreak: bool = inCalculationWindow and (not na(bearishBreakLevel)) and (not bearishLevelBroken) and (internalCrossDown if internalMode else close < bearishBreakLevel if requireBodyInput else low < bearishBreakLevel)

    if inCalculationWindow and chochActive and barstate.isconfirmed:
        failureLow: float = currentChochLow - currentChochRange
        failureHigh: float = currentChochHigh + currentChochRange
        if not na(activeLowTriangle) and close < failureLow:
            label.delete(activeLowTriangle)
            activeLowTriangle = na
            if array.size(storedLowTriangles) > 0:
                array.set(storedLowTriangles, array.size(storedLowTriangles) - 1, na)
            lowestConfirmedSweep = na
            pendingLowSweep = na
            pendingLowTime = na
            pendingLowBar = na
            pendingLowBodyTop = na
        if not na(activeHighTriangle) and close > failureHigh:
            label.delete(activeHighTriangle)
            activeHighTriangle = na
            if array.size(storedHighTriangles) > 0:
                array.set(storedHighTriangles, array.size(storedHighTriangles) - 1, na)
            repeatedCount: int = array.size(repeatedHighZoneIds)
            if repeatedCount > 0:
                for offset in pine_range(0, repeatedCount - 1):
                    repeatIndex: int = repeatedCount - 1 - offset
                    if array.get(repeatedHighZoneIds, repeatIndex) == currentZoneId:
                        label.delete(array.remove(repeatedHighTriangles, repeatIndex))
                        array.remove(repeatedHighZoneIds, repeatIndex)
            highestConfirmedSweep = na
            pendingHighSweep = na
            pendingHighTime = na
            pendingHighBar = na
            pendingHighBodyBottom = na
            highSweepArmed = False

    buyZoneCreatedSignal: bool = False
    sellZoneCreatedSignal: bool = False

    if bullishBreak:
        isBullishChoch: bool = lastBreakDirection == -1
        bullishLevelBroken = True
        cooldownPass: bool = minimumBarsInput == 0 or na(lastAcceptedChochBar) or bar_index - lastAcceptedChochBar >= minimumBarsInput
        if isBullishChoch and commonFilterPass and bullishDirectionPass and cooldownPass:
            if chochActive:
                f_freezeActive(time)
                if showPreviousSignalInput:
                    previousTagGap: float = math.max(syminfo.mintick * 20.0, math.min(nz(atrValue, currentChochRange) * 0.35, currentChochRange * 0.6))
                    keptTriangle, keptText = f_keepPreviousSignal(activeLowTriangle, activeHighTriangle, previousTriangle, previousSignalText, previousTagGap)
                    previousTriangle = keptTriangle
                    previousSignalText = keptText
            currentChochHigh = high
            currentChochLow = low
            currentChochRange = math.max(syminfo.mintick, high - low)
            pendingBrokenLevel = bullishBreakLevel
            pendingStructureStartTime = bullishLevelStartTime
            pendingZoneLabelGap = math.max(syminfo.mintick * 20.0, nz(atrValue, currentChochRange) * zoneLabelAtrGapInput)
            pendingRangeBoxTop = bullishBreakLevel
            pendingRangeBoxBottom = math.min(nz(bullishRangeLow, low), low)
            currentZoneId += 1
            f_createChochSet(1, currentChochHigh, currentChochLow, extensionMilliseconds, oneBarMilliseconds)
            buyZoneCreatedSignal = True
            chochActive = True
            activeChochDirection = 1
            lastAcceptedChochBar = bar_index
            outOfRangeUp = False
            outOfRangeDown = False
            upperExtensionShown = False
            lowerExtensionShown = False
            lowestConfirmedSweep = na
            highestConfirmedSweep = na
            highSweepArmed = True
            pendingLowSweep = na
            pendingHighSweep = na
            pendingLowBodyTop = na
            pendingHighBodyBottom = na
            pendingLowBar = na
            pendingHighBar = na
            pendingLowTime = na
            pendingHighTime = na
            activeLowTriangle = na
            activeHighTriangle = na
        lastBreakDirection = 1

    if bearishBreak:
        isBearishChoch: bool = lastBreakDirection == 1
        bearishLevelBroken = True
        cooldownPass: bool = minimumBarsInput == 0 or na(lastAcceptedChochBar) or bar_index - lastAcceptedChochBar >= minimumBarsInput
        if isBearishChoch and commonFilterPass and bearishDirectionPass and cooldownPass:
            if chochActive:
                f_freezeActive(time)
                if showPreviousSignalInput:
                    previousTagGap: float = math.max(syminfo.mintick * 20.0, math.min(nz(atrValue, currentChochRange) * 0.35, currentChochRange * 0.6))
                    keptTriangle, keptText = f_keepPreviousSignal(activeLowTriangle, activeHighTriangle, previousTriangle, previousSignalText, previousTagGap)
                    previousTriangle = keptTriangle
                    previousSignalText = keptText
            currentChochHigh = high
            currentChochLow = low
            currentChochRange = math.max(syminfo.mintick, high - low)
            pendingBrokenLevel = bearishBreakLevel
            pendingStructureStartTime = bearishLevelStartTime
            pendingZoneLabelGap = math.max(syminfo.mintick * 20.0, nz(atrValue, currentChochRange) * zoneLabelAtrGapInput)
            pendingRangeBoxTop = math.max(nz(bearishRangeHigh, high), high)
            pendingRangeBoxBottom = bearishBreakLevel
            currentZoneId += 1
            f_createChochSet(-1, currentChochHigh, currentChochLow, extensionMilliseconds, oneBarMilliseconds)
            sellZoneCreatedSignal = True
            chochActive = True
            activeChochDirection = -1
            lastAcceptedChochBar = bar_index
            outOfRangeUp = False
            outOfRangeDown = False
            upperExtensionShown = False
            lowerExtensionShown = False
            lowestConfirmedSweep = na
            highestConfirmedSweep = na
            highSweepArmed = True
            pendingLowSweep = na
            pendingHighSweep = na
            pendingLowBodyTop = na
            pendingHighBodyBottom = na
            pendingLowBar = na
            pendingHighBar = na
            pendingLowTime = na
            pendingHighTime = na
            activeLowTriangle = na
            activeHighTriangle = na
        lastBreakDirection = -1

    if buyZoneCreatedSignal or sellZoneCreatedSignal:
        if not na(activeWallRejectedLabel):
            label.delete(activeWallRejectedLabel)
        activeWallRejectedLabel = na
        activeWallRejectedWick = na

    if inCalculationWindow and chochActive:
        rightTime: int = time + extensionMilliseconds
        if array.size(storedWallBoxes) > 0:
            wallBox: Box = array.get(storedWallBoxes, array.size(storedWallBoxes) - 1)
            if not na(wallBox):
                box.set_right(wallBox, rightTime)
        activeLineCount: int = math.min(23, array.size(activeLines))
        if activeLineCount > 0:
            for index in pine_range(0, activeLineCount - 1):
                activeLine: Line = array.get(activeLines, index)
                if not na(activeLine):
                    line.set_x2(activeLine, rightTime)
        if showLevelLabelsInput:
            levelLabelCount: int = math.min(23, array.size(activeLabels))
            if levelLabelCount > 0:
                for index in pine_range(0, levelLabelCount - 1):
                    activeLabel: Label = array.get(activeLabels, index)
                    if not na(activeLabel):
                        label.set_x(activeLabel, rightTime)

    if inCalculationWindow and chochActive:
        upperFourTrigger: float = currentChochHigh + currentChochRange * 4.0
        lowerFourTrigger: float = currentChochLow - currentChochRange * 4.0
        activeDirectionColor: Color = chochLineUpInput if activeChochDirection == 1 else chochLineDownInput
        if not upperExtensionShown and high > upperFourTrigger:
            f_showExtendedLevels(15, 18, activeDirectionColor)
            upperExtensionShown = True
        if not lowerExtensionShown and low < lowerFourTrigger:
            f_showExtendedLevels(19, 22, activeDirectionColor)
            lowerExtensionShown = True

    if inCalculationWindow and chochActive and barstate.isconfirmed and (bar_index > lastAcceptedChochBar):
        wallMid: float = math.avg(currentChochHigh, currentChochLow)
        isSellerWall: bool = activeChochDirection == -1
        wallRejected: bool = high >= wallMid + syminfo.mintick and high <= currentChochHigh and (high - math.max(open, close) >= syminfo.mintick) and (close < open) and (close < wallMid) if isSellerWall else low <= wallMid - syminfo.mintick and low >= currentChochLow and (math.min(open, close) - low >= syminfo.mintick) and (close > open) and (close > wallMid)
        moreExtreme: bool = na(activeWallRejectedWick) or (high > activeWallRejectedWick if isSellerWall else low < activeWallRejectedWick)
        if wallRejected and moreExtreme:
            wickPrice: float = high if isSellerWall else low
            labelGap: float = math.max(syminfo.mintick * 5.0, math.min(nz(atrValue, currentChochRange) * 0.12, currentChochRange * 0.15))
            labelY: float = wickPrice + (labelGap if isSellerWall else -labelGap)
            rejectedColor: Color = color.new('#F23645') if isSellerWall else color.new('#089981')
            if na(activeWallRejectedLabel):
                activeWallRejectedLabel = label.new(time, labelY, 'REJECTED', xloc=xloc.bar_time, yloc=yloc.price, color=color.new('#00000000'), style=label.style_label_down if isSellerWall else label.style_label_up, textcolor=rejectedColor, size=f_labelSize(rejectedLabelSizeInput))
            else:
                label.set_xy(activeWallRejectedLabel, time, labelY)
            activeWallRejectedWick = wickPrice

    longTriangleSignal: bool = False
    shortTriangleSignal: bool = False

    if inCalculationWindow and chochActive and barstate.isconfirmed:
        lowerHalf: float = currentChochLow - currentChochRange * 0.5
        lowerOne: float = currentChochLow - currentChochRange
        upperHalf: float = currentChochHigh + currentChochRange * 0.5
        upperOne: float = currentChochHigh + currentChochRange
        minWickDepth: float = math.max(syminfo.mintick, currentChochRange * 0.5 * minSweepDepthInput * 0.1)

        lowInBand: bool = low >= lowerOne and low <= lowerHalf - minWickDepth and (math.min(open, close) - low >= minWickDepth)
        highRejectedInBand: bool = high <= upperOne and high >= upperHalf + minWickDepth and (high - math.max(open, close) >= minWickDepth)

        confirmLow: bool = not na(pendingLowSweep) and bar_index == pendingLowBar + 1 and (close > open) and (close > pendingLowBodyTop) and (close > lowerHalf)
        if confirmLow:
            lowestConfirmedSweep = pendingLowSweep
            triangleY: float = math.min(low, pendingLowSweep) - math.max(syminfo.mintick * 10.0, math.min(nz(atrValue, currentChochRange) * 0.45, currentChochRange * 0.5))
            if na(activeLowTriangle):
                activeLowTriangle = label.new(time, triangleY, '', xloc=xloc.bar_time, yloc=yloc.price, color=color.new('#089981'), style=label.style_triangleup, textcolor=color.new('#089981'), size=5)
                array.set(storedLowTriangles, array.size(storedLowTriangles) - 1, activeLowTriangle)
            else:
                label.set_xy(activeLowTriangle, time, triangleY)
            longTriangleSignal = True
        if not na(pendingLowSweep) and bar_index > pendingLowBar:
            pendingLowSweep = na
            pendingLowTime = na
            pendingLowBar = na
            pendingLowBodyTop = na
        if lowInBand and (na(lowestConfirmedSweep) or low < lowestConfirmedSweep):
            pendingLowSweep = low
            pendingLowTime = time
            pendingLowBar = bar_index
            pendingLowBodyTop = math.max(open, close)

        if not highSweepArmed and high < upperHalf and (close < upperHalf):
            highSweepArmed = True

        confirmHigh: bool = highSweepArmed and (not na(pendingHighSweep)) and (bar_index == pendingHighBar + 1) and (close < open) and (close < pendingHighBodyBottom) and (close < upperHalf)
        if confirmHigh:
            highestConfirmedSweep = pendingHighSweep
            triangleY: float = highestConfirmedSweep + math.max(syminfo.mintick * 10.0, math.min(nz(atrValue, currentChochRange) * 0.45, currentChochRange * 0.5))
            if not na(activeHighTriangle):
                array.push(repeatedHighTriangles, activeHighTriangle)
                array.push(repeatedHighZoneIds, currentZoneId)
            activeHighTriangle = label.new(pendingHighTime, triangleY, '', xloc=xloc.bar_time, yloc=yloc.price, color=color.new('#F23645'), style=label.style_triangledown, textcolor=color.new('#F23645'), size=5)
            array.set(storedHighTriangles, array.size(storedHighTriangles) - 1, activeHighTriangle)
            safeZoneLimit: int = MAX_SAFE_ZONE_SETS if chochShowLastInput == 0 else chochShowLastInput
            maxRetests: int = math.min(15, math.max(0, 500 - 26 * safeZoneLimit - 5))
            while array.size(repeatedHighTriangles) > maxRetests:
                label.delete(array.shift(repeatedHighTriangles))
                array.shift(repeatedHighZoneIds)
            shortTriangleSignal = True
            highSweepArmed = False
        if not na(pendingHighSweep) and bar_index > pendingHighBar:
            pendingHighSweep = na
            pendingHighTime = na
            pendingHighBar = na
            pendingHighBodyBottom = na
        if highSweepArmed and highRejectedInBand:
            pendingHighSweep = high
            pendingHighTime = time
            pendingHighBar = bar_index
            pendingHighBodyBottom = math.min(open, close)

    deviationUpSignal: bool = False
    deviationDownSignal: bool = False
    if inCalculationWindow and chochActive:
        upperFourLevel: float = currentChochHigh + currentChochRange * 4.0
        lowerFourLevel: float = currentChochLow - currentChochRange * 4.0
        if high > upperFourLevel:
            outOfRangeUp = True
        if outOfRangeUp and close < upperFourLevel and (close > lowerFourLevel):
            deviationDownSignal = True
            outOfRangeUp = False
        if low < lowerFourLevel:
            outOfRangeDown = True
        if outOfRangeDown and close > lowerFourLevel and (close < upperFourLevel):
            deviationUpSignal = True
            outOfRangeDown = False

    plot(vwapValue if showVwapInput else na, 'Session VWAP', color=color.new('#5B9CF6'), linewidth=2)
    plot(emaValue if showEmaInput else na, 'Trend EMA', color=color.new('#F59E0B'), linewidth=2)
    plotshape(showDeviationInput and deviationDownSignal, 'Dev Down', style=shape.triangledown, location=location.abovebar, color=deviationDownInput, size=size.small)
    plotshape(showDeviationInput and deviationUpSignal, 'Dev Up', style=shape.triangleup, location=location.belowbar, color=deviationUpInput, size=size.small)

    alertcondition(buyZoneCreatedSignal, 'BUY Zone Created', 'BUY ZONE created on {{ticker}} ({{interval}}). Price: {{close}}')
    alertcondition(sellZoneCreatedSignal, 'SELL Zone Created', 'SELL ZONE created on {{ticker}} ({{interval}}). Price: {{close}}')
    alertcondition(deviationUpSignal or deviationDownSignal, 'Price Returning to Range', 'Price returned inside the active -4 to +4 range on {{ticker}} ({{interval}}). Price: {{close}}')
    alertcondition(longTriangleAlertInput and longTriangleSignal, 'LONG Triangle Confirmed', 'LONG sweep triangle confirmed or moved to a deeper sweep on {{ticker}} ({{interval}}). Price: {{close}}')
    alertcondition(shortTriangleAlertInput and shortTriangleSignal, 'SHORT Triangle Confirmed', 'SHORT sweep triangle confirmed or moved to a higher sweep on {{ticker}} ({{interval}}). Price: {{close}}')

    if buyZoneAlertInput and buyZoneCreatedSignal:
        alert('BUY ZONE created | ' + syminfo.ticker + ' | ' + timeframe.period + ' | Price: ' + string.tostring(close, format.mintick), alert.freq_once_per_bar_close)
    if sellZoneAlertInput and sellZoneCreatedSignal:
        alert('SELL ZONE created | ' + syminfo.ticker + ' | ' + timeframe.period + ' | Price: ' + string.tostring(close, format.mintick), alert.freq_once_per_bar_close)
    if returnToRangeAlertInput and (deviationUpSignal or deviationDownSignal):
        alert('Price returned inside the active -4 to +4 range | ' + syminfo.ticker + ' | ' + timeframe.period + ' | Price: ' + string.tostring(close, format.mintick), alert.freq_once_per_bar_close)
    if longTriangleAlertInput and longTriangleSignal:
        alert('LONG triangle confirmed | ' + syminfo.ticker + ' | ' + timeframe.period + ' | Price: ' + string.tostring(close, format.mintick), alert.freq_once_per_bar_close)
    if shortTriangleAlertInput and shortTriangleSignal:
        alert('SHORT triangle confirmed | ' + syminfo.ticker + ' | ' + timeframe.period + ' | Price: ' + string.tostring(close, format.mintick), alert.freq_once_per_bar_close)

    hudTextSize = f_labelSize(hudSizeInput)
    zoneHudTable: Persistent[Table] = table.new(position.top_right, 2, 4, frame_color=color.new(chart.fg_color, 70), frame_width=1, border_color=color.new(chart.fg_color, 85), border_width=1)
    watermarkTable: Persistent[Table] = table.new(position.bottom_right, 1, 1)

    if barstate.islast:
        referenceZoneText: str = 'NO DATA' if na(referenceZoneState) else 'BUY ZONE' if referenceZoneState == 1 else 'SELL ZONE' if referenceZoneState == -1 else 'NEUTRAL'
        referenceZoneColor: Color = color.new(chart.fg_color, 35) if na(referenceZoneState) else color.new('#089981') if referenceZoneState == 1 else color.new('#F23645') if referenceZoneState == -1 else color.new('#5B9CF6')
        hudBackground: Color = color.new(chart.bg_color, 15)

        if showHudInput:
            table.cell(zoneHudTable, 0, 0, 'REFERENCE ZONE HUD', text_color=chart.fg_color, bgcolor=color.new(color.new('#5B9CF6'), 75), text_size=hudTextSize)
            table.cell(zoneHudTable, 1, 0, 'STATUS', text_color=chart.fg_color, bgcolor=color.new(color.new('#5B9CF6'), 75), text_size=hudTextSize)
            table.cell(zoneHudTable, 0, 1, 'Asset', text_color=color.new(chart.fg_color, 25), bgcolor=hudBackground, text_size=hudTextSize)
            table.cell(zoneHudTable, 1, 1, hudAssetInput, text_color=chart.fg_color, bgcolor=hudBackground, text_size=hudTextSize)
            table.cell(zoneHudTable, 0, 2, 'Asset Zone', text_color=color.new(chart.fg_color, 25), bgcolor=hudBackground, text_size=hudTextSize)
            table.cell(zoneHudTable, 1, 2, referenceZoneText, text_color=referenceZoneColor, bgcolor=hudBackground, text_size=hudTextSize)
            table.cell(zoneHudTable, 0, 3, 'Timeframe', text_color=color.new(chart.fg_color, 25), bgcolor=hudBackground, text_size=hudTextSize)
            table.cell(zoneHudTable, 1, 3, timeframe.period, text_color=chart.fg_color, bgcolor=hudBackground, text_size=hudTextSize)
        else:
            table.clear(zoneHudTable, 0, 0, 1, 3)

        table.cell(watermarkTable, 0, 0, 'erdensedat', text_color=color.new(chart.fg_color, 70), bgcolor=color.new('#00000000'), text_size=size.small)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
