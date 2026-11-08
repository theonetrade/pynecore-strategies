"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, box, chart, close, color,
    extend, format, high, input, label, last_bar_index, line, location, low, math, na, open,
    plotshape, position, script, shape, size, string, ta, table, time, timeframe, volume, xloc
)
from pynecore.types import Box, Color, Label, Line, Persistent, Series, Table

BULL_COLOR: Color = color.new('#089981')
BEAR_COLOR: Color = color.new('#F23645')
METRIC_COLOR: Color = color.new('#5B9CF6')
HVN_COLOR: Color = color.new('#B983FF')
MAX_BROKEN_OBJECTS: int = 450
coreGroup: str = "Core"
performanceGroup: str = "Performance"
brokenGroup: str = "Broken Structure"
labelGroup: str = "BOS/CHoCH Labels"
profileGroup: str = "Last CHoCH Volume Profile"
pocGroup: str = "POC"
hvnGroup: str = "High Volume Nodes"
lvnGroup: str = "Low Volume Nodes"
displayGroup: str = "Display"
debugGroup: str = "Debug"


@script.indicator("Structure Break Volume Profile", shorttitle="Structure Break Volume Profile", overlay=True, max_lines_count=500, max_labels_count=500, max_boxes_count=500, calc_bars_count=50000)
def main(
    fractalLengthInput=input.int(12, "Fractal Length (odd)", minval=3, maxval=51, group=coreGroup, tooltip="Pivot window length. Even values are automatically increased by one."),
    barsToRightInput=input.int(5, "Bars to Right", minval=1, maxval=300, group=coreGroup, tooltip="Number of chart bars used to project POC, HVN, and LVN elements to the right."),
    requireBodyInput=input.bool(True, "Break = Close Beyond Level", group=coreGroup, tooltip="When enabled, a close beyond the pivot level confirms a break. Otherwise, a wick through the level is sufficient."),
    calcLastBarsInput=input.int(20000, "Calc Only Last N Bars (0 = all)", minval=0, maxval=50000, group=performanceGroup, tooltip="Limits structure calculations to the latest bars. Use zero to process all bars made available to the script."),
    maxKeepInput=input.int(250, "Max Stored Broken", minval=100, maxval=MAX_BROKEN_OBJECTS, group=performanceGroup, tooltip="Maximum number of historical broken structure lines and labels retained on the chart."),
    showLastNInput=input.int(0, "Show Last N Broken (0 = all)", minval=0, maxval=MAX_BROKEN_OBJECTS, group=performanceGroup, tooltip="Deletes older broken structures so only the latest N remain. Zero uses the Max Stored Broken setting."),
    profileBarsInput=input.int(3000, "Profile Source Bars", minval=100, maxval=10000, group=performanceGroup, tooltip="Maximum number of recent chart bars retained for building the latest CHoCH volume profile."),
    brokenUpColorInput=input.color(BULL_COLOR, "Broken UP Color", group=brokenGroup, tooltip="Color of bullish broken structure levels."),
    brokenDownColorInput=input.color(BEAR_COLOR, "Broken DN Color", group=brokenGroup, tooltip="Color of bearish broken structure levels."),
    brokenWidthInput=input.int(1, "Broken Width", minval=1, maxval=5, group=brokenGroup, tooltip="Width of confirmed broken structure levels."),
    brokenStyleInput=input.string("Solid", "Broken Style", options=("Solid", "Dashed", "Dotted"), group=brokenGroup, tooltip="Line style of confirmed broken structure levels."),
    showBreakLabelsInput=input.bool(True, "Show BOS/CHoCH Labels", group=labelGroup, tooltip="Displays BOS and CHoCH labels together with their price levels."),
    structureLabelSizeInput=input.string("normal", "Structure Label Size", options=("tiny", "small", "normal"), group=labelGroup, tooltip="Size of BOS and CHoCH labels."),
    labelBackgroundInput=input.color(color.new('#00000000'), "Label Background", group=labelGroup, tooltip="Background color of structure labels. The default is fully transparent."),
    upLabelTextColorInput=input.color(BULL_COLOR, "UP Label Text Color", group=labelGroup, tooltip="Text color for bullish structure labels."),
    downLabelTextColorInput=input.color(BEAR_COLOR, "DN Label Text Color", group=labelGroup, tooltip="Text color for bearish structure labels."),
    showProfileInput=input.bool(True, "Show Volume Profile", group=profileGroup, tooltip="Draws volume at each price row across the completed structure preceding CHoCH."),
    profileArchitectureInput=input.string("Ask/Bid", "Visual Architecture", options=("Ask/Bid", "Total Volume"), group=profileGroup, tooltip="Ask/Bid estimates buyer and seller pressure from candle location. Total Volume uses one unified histogram color."),
    profileRowsInput=input.int(50, "Profile Rows", minval=8, maxval=100, group=profileGroup, tooltip="Number of price rows used by the CHoCH volume profile."),
    profileWidthInput=input.int(88, "Profile Width (% of structure span)", minval=10, maxval=100, group=profileGroup, tooltip="Maximum histogram width inside the completed structure area."),
    profilePositionInput=input.string("Left", "Volume Profile Position", options=("Right", "Left"), group=profileGroup, tooltip="Anchors profile columns to the right or left side of the completed structure area."),
    totalProfileColorInput=input.color(color.new(METRIC_COLOR, 30), "Total Volume Color", group=profileGroup, tooltip="Column color used by the Total Volume architecture."),
    askProfileColorInput=input.color(color.new(BULL_COLOR, 28), "Ask / Buyer Color", group=profileGroup, tooltip="Estimated buyer-volume color used by the Ask/Bid architecture."),
    bidProfileColorInput=input.color(color.new(BEAR_COLOR, 28), "Bid / Seller Color", group=profileGroup, tooltip="Estimated seller-volume color used by the Ask/Bid architecture."),
    profileAreaColorInput=input.color(color.new(METRIC_COLOR, 94), "Profile Area Fill", group=profileGroup, tooltip="Transparent background covering the completed structure profile area."),
    profileBorderColorInput=input.color(color.new(METRIC_COLOR, 55), "Profile Area Border", group=profileGroup, tooltip="Border color of the completed structure profile area."),
    showPocInput=input.bool(True, "Show POC", group=pocGroup, tooltip="Displays the highest-volume row from the latest CHoCH profile and projects it for retest tracking."),
    pocColorInput=input.color(METRIC_COLOR, "POC Color", group=pocGroup, tooltip="Color of the active POC line."),
    pocWidthInput=input.int(2, "POC Width", minval=1, maxval=5, group=pocGroup, tooltip="Width of the active POC line."),
    pocStyleInput=input.string("Dashed", "POC Style", options=("Solid", "Dashed", "Dotted"), group=pocGroup, tooltip="Line style of the active POC level."),
    showPocLabelInput=input.bool(True, "Show POC Label", group=pocGroup, tooltip="Displays the active POC direction and numerical price."),
    pocLabelSizeInput=input.string("normal", "POC Label Size", options=("tiny", "small", "normal"), group=pocGroup, tooltip="Size of the POC label."),
    pocLabelTextColorInput=input.color(METRIC_COLOR, "POC Label Text Color", group=pocGroup, tooltip="Text color of the POC label."),
    pocLabelBackgroundInput=input.color(color.new('#00000000'), "POC Label Background", group=pocGroup, tooltip="Background color of the POC label. The default is fully transparent."),
    showHvnInput=input.bool(True, "Show HVN Columns", group=hvnGroup, tooltip="Projects significant local volume peaks from their profile columns toward the latest bars."),
    hvnCountInput=input.int(3, "Maximum HVN Count", minval=1, maxval=8, group=hvnGroup, tooltip="Maximum number of strongest High Volume Node columns displayed."),
    hvnThresholdInput=input.float(55.0, "Minimum Volume (% of POC)", minval=10.0, maxval=95.0, step=5.0, group=hvnGroup, tooltip="A local volume peak must reach this percentage of POC row volume to qualify as an HVN."),
    hvnSpacingInput=input.int(3, "Minimum Row Spacing", minval=1, maxval=10, group=hvnGroup, tooltip="Minimum number of rows separating HVNs from each other and from the POC."),
    hvnColorInput=input.color(HVN_COLOR, "HVN Column Color", group=hvnGroup, tooltip="Color applied to High Volume Node projection columns and labels."),
    hvnOpacityInput=input.int(78, "HVN Column Transparency", minval=0, maxval=95, group=hvnGroup, tooltip="Transparency of projected HVN columns."),
    showHvnLabelsInput=input.bool(True, "Show HVN Labels", group=hvnGroup, tooltip="Displays each HVN rank and numerical price."),
    hvnLabelSizeInput=input.string("normal", "HVN Label Size", options=("tiny", "small", "normal"), group=hvnGroup, tooltip="Size of HVN labels."),
    hvnLabelOffsetInput=input.int(3, "HVN Label Offset (bars)", minval=1, maxval=50, group=hvnGroup, tooltip="Places HVN labels this many chart bars beyond the projected columns."),
    showLvnInput=input.bool(False, "Show LVN Columns", group=lvnGroup, tooltip="Projects significant local volume troughs as columns. Columns are green after bullish CHoCH and red after bearish CHoCH."),
    lvnCountInput=input.int(3, "Maximum LVN Count", minval=1, maxval=8, group=lvnGroup, tooltip="Maximum number of strongest Low Volume Node columns displayed."),
    lvnThresholdInput=input.float(45.0, "Maximum Volume (% of POC)", minval=5.0, maxval=90.0, step=5.0, group=lvnGroup, tooltip="A local volume trough must remain below this percentage of POC row volume to qualify as an LVN."),
    lvnSpacingInput=input.int(3, "Minimum Row Spacing", minval=1, maxval=10, group=lvnGroup, tooltip="Minimum number of rows separating LVNs from each other and from the POC."),
    lvnOpacityInput=input.int(88, "LVN Column Transparency", minval=0, maxval=95, group=lvnGroup, tooltip="Transparency of projected LVN columns."),
    showLvnLabelsInput=input.bool(True, "Show LVN Labels", group=lvnGroup, tooltip="Displays each LVN rank and numerical price."),
    lvnLabelSizeInput=input.string("normal", "LVN Label Size", options=("tiny", "small", "normal"), group=lvnGroup, tooltip="Size of LVN labels."),
    lvnLabelOffsetInput=input.int(3, "LVN Label Offset (bars)", minval=1, maxval=50, group=lvnGroup, tooltip="Places LVN labels this many chart bars beyond the projected columns."),
    showWatermarkInput=input.bool(True, "Show erdensedat Watermark", group=displayGroup, tooltip="Shows the erdensedat watermark at the bottom center of the chart."),
    showPivotMarksInput=input.bool(False, "Show Pivot Marks", group=debugGroup, tooltip="Marks confirmed pivot highs and lows for debugging.")
):
    def f_lineStyle(styleText: str):
        return line.style_solid if styleText == 'Solid' else line.style_dashed if styleText == 'Dashed' else line.style_dotted

    def f_labelSize(sizeText: str):
        return size.tiny if sizeText == 'tiny' else size.small if sizeText == 'small' else size.normal

    def f_clampFloat(value: float, minimum: float, maximum: float):
        return math.min(math.max(value, minimum), maximum)

    def f_clampInt(value: int, minimum: int, maximum: int):
        return math.min(math.max(value, minimum), maximum)

    inCalc: bool = calcLastBarsInput == 0 or bar_index >= last_bar_index - calcLastBarsInput
    oddLength: int = fractalLengthInput + 1 if fractalLengthInput % 2 == 0 else fractalLengthInput
    pivotStrength: int = cast_int(oddLength / 2)
    timeframeMilliseconds: int = cast_int(timeframe.in_seconds(timeframe.period) * 1000)
    extensionMilliseconds: int = timeframeMilliseconds * barsToRightInput
    brokenLineStyle = f_lineStyle(brokenStyleInput)
    pocLineStyle = f_lineStyle(pocStyleInput)
    structureLabelSize = f_labelSize(structureLabelSizeInput)
    pocLabelSize = f_labelSize(pocLabelSizeInput)
    hvnLabelSize = f_labelSize(hvnLabelSizeInput)
    lvnLabelSize = f_labelSize(lvnLabelSizeInput)

    pivotHighValue: float = ta.pivothigh(high, pivotStrength, pivotStrength)
    pivotLowValue: float = ta.pivotlow(low, pivotStrength, pivotStrength)
    pivotHighHit: bool = not na(pivotHighValue)
    pivotLowHit: bool = not na(pivotLowValue)

    plotshape(showPivotMarksInput and pivotHighHit, title='Pivot High', style=shape.triangledown, location=location.abovebar, offset=-pivotStrength, color=BEAR_COLOR, textcolor=chart.fg_color, size=size.tiny, text='PH')
    plotshape(showPivotMarksInput and pivotLowHit, title='Pivot Low', style=shape.triangleup, location=location.belowbar, offset=-pivotStrength, color=BULL_COLOR, textcolor=chart.fg_color, size=size.tiny, text='PL')

    upperLevel: Persistent[float] = na(float)
    upperPivotTime: Persistent[int] = na(int)
    upperBroken: Persistent[bool] = False
    lowerLevel: Persistent[float] = na(float)
    lowerPivotTime: Persistent[int] = na(int)
    lowerBroken: Persistent[bool] = False
    structureDirection: Persistent[int] = 0
    activeStructureHigh: Persistent[float] = na(float)
    activeStructureHighTime: Persistent[int] = na(int)
    activeStructureLow: Persistent[float] = na(float)
    activeStructureLowTime: Persistent[int] = na(int)

    brokenLinesArray: Persistent[list[Line]] = array.new_line()
    brokenLabelsArray: Persistent[list[Label]] = array.new_label()

    def f_trimBroken():
        if showLastNInput > 0:
            while array.size(brokenLinesArray) > showLastNInput:
                oldLineId: Line = array.shift(brokenLinesArray)
                oldLabelId: Label = array.shift(brokenLabelsArray)
                line.delete(oldLineId)
                if not na(oldLabelId):
                    label.delete(oldLabelId)
        __block_result__ = na
        while array.size(brokenLinesArray) > maxKeepInput:
            oldLineId: Line = array.shift(brokenLinesArray)
            oldLabelId: Label = array.shift(brokenLabelsArray)
            line.delete(oldLineId)
            __block_result_1__ = na
            if not na(oldLabelId):
                __block_result_1__ = label.delete(oldLabelId)
            __block_result__ = __block_result_1__
        return __block_result__

    def f_pushBroken(lineId: Line, labelId: Label):
        array.push(brokenLinesArray, lineId)
        array.push(brokenLabelsArray, labelId)
        return f_trimBroken()

    sourceTimeArray: Persistent[list[int]] = array.new_int()
    sourceOpenArray: Persistent[list[float]] = array.new_float()
    sourceHighArray: Persistent[list[float]] = array.new_float()
    sourceLowArray: Persistent[list[float]] = array.new_float()
    sourceCloseArray: Persistent[list[float]] = array.new_float()
    sourceVolumeArray: Persistent[list[float]] = array.new_float()

    if inCalc:
        array.push(sourceTimeArray, time)
        array.push(sourceOpenArray, open)
        array.push(sourceHighArray, high)
        array.push(sourceLowArray, low)
        array.push(sourceCloseArray, close)
        array.push(sourceVolumeArray, 1.0 if na(volume) or volume <= 0 else volume)
        while array.size(sourceTimeArray) > profileBarsInput:
            array.shift(sourceTimeArray)
            array.shift(sourceOpenArray)
            array.shift(sourceHighArray)
            array.shift(sourceLowArray)
            array.shift(sourceCloseArray)
            array.shift(sourceVolumeArray)

    profileStartTime: Persistent[int] = na(int)
    profileEndTime: Persistent[int] = na(int)
    latestChochTime: Persistent[int] = na(int)
    latestChochDirection: Persistent[int] = 0
    profileLowPrice: Persistent[float] = na(float)
    profileHighPrice: Persistent[float] = na(float)
    latestPocPrice: Persistent[float] = na(float)
    pocLineId: Persistent[Line] = na(Line)
    pocLabelId: Persistent[Label] = na(Label)
    profileBoxesArray: Persistent[list[Box]] = array.new_box()
    nodeLabelsArray: Persistent[list[Label]] = array.new_label()

    def f_clearProfileBoxes():
        __block_result_2__ = na
        if array.size(profileBoxesArray) > 0:
            for boxIndex in pine_range(0, array.size(profileBoxesArray) - 1):
                box.delete(array.get(profileBoxesArray, boxIndex))
            __block_result_2__ = array.clear(profileBoxesArray)
        return __block_result_2__

    def f_clearNodeLabels():
        __block_result_3__ = na
        if array.size(nodeLabelsArray) > 0:
            for labelIndex in pine_range(0, array.size(nodeLabelsArray) - 1):
                label.delete(array.get(nodeLabelsArray, labelIndex))
            __block_result_3__ = array.clear(nodeLabelsArray)
        return __block_result_3__

    def f_buildProfile(startTime: int, endTime: int, lowPrice: float, highPrice: float):
        totalVolumeArray: list[float] = array.new_float(profileRowsInput, 0.0)
        askVolumeArray: list[float] = array.new_float(profileRowsInput, 0.0)
        bidVolumeArray: list[float] = array.new_float(profileRowsInput, 0.0)
        rowHeight: float = (highPrice - lowPrice) / profileRowsInput

        if rowHeight > 0 and array.size(sourceTimeArray) > 0:
            for sourceIndex in pine_range(0, array.size(sourceTimeArray) - 1):
                sourceTime: int = array.get(sourceTimeArray, sourceIndex)
                if sourceTime >= startTime and sourceTime <= endTime:
                    sourceOpen: float = array.get(sourceOpenArray, sourceIndex)
                    sourceHigh: float = array.get(sourceHighArray, sourceIndex)
                    sourceLow: float = array.get(sourceLowArray, sourceIndex)
                    sourceClose: float = array.get(sourceCloseArray, sourceIndex)
                    sourceVolume: float = array.get(sourceVolumeArray, sourceIndex)
                    sourceRange: float = sourceHigh - sourceLow
                    askShare: float = f_clampFloat((sourceClose - sourceLow) / sourceRange, 0.0, 1.0) if sourceRange > 0 else 1.0 if sourceClose > sourceOpen else 0.0 if sourceClose < sourceOpen else 0.5
                    sourceAskVolume: float = sourceVolume * askShare
                    sourceBidVolume: float = sourceVolume - sourceAskVolume
                    clippedLow: float = math.max(sourceLow, lowPrice)
                    clippedHigh: float = math.min(sourceHigh, highPrice)

                    if clippedHigh > clippedLow:
                        firstRow: int = f_clampInt(cast_int(math.floor((clippedLow - lowPrice) / rowHeight)), 0, profileRowsInput - 1)
                        lastRow: int = f_clampInt(cast_int(math.floor((clippedHigh - lowPrice) / rowHeight)), 0, profileRowsInput - 1)
                        clippedRange: float = clippedHigh - clippedLow
                        for rowIndex in pine_range(firstRow, lastRow):
                            rowBottom: float = lowPrice + rowIndex * rowHeight
                            rowTop: float = rowBottom + rowHeight
                            overlap: float = math.max(math.min(clippedHigh, rowTop) - math.max(clippedLow, rowBottom), 0.0)
                            allocation: float = overlap / clippedRange if clippedRange > 0 else 0.0
                            array.set(totalVolumeArray, rowIndex, array.get(totalVolumeArray, rowIndex) + sourceVolume * allocation)
                            array.set(askVolumeArray, rowIndex, array.get(askVolumeArray, rowIndex) + sourceAskVolume * allocation)
                            array.set(bidVolumeArray, rowIndex, array.get(bidVolumeArray, rowIndex) + sourceBidVolume * allocation)
                    elif sourceClose >= lowPrice and sourceClose <= highPrice:
                        rowIndex: int = f_clampInt(cast_int(math.floor((sourceClose - lowPrice) / rowHeight)), 0, profileRowsInput - 1)
                        array.set(totalVolumeArray, rowIndex, array.get(totalVolumeArray, rowIndex) + sourceVolume)
                        array.set(askVolumeArray, rowIndex, array.get(askVolumeArray, rowIndex) + sourceAskVolume)
                        array.set(bidVolumeArray, rowIndex, array.get(bidVolumeArray, rowIndex) + sourceBidVolume)

        maximumRowVolume: float = 0.0
        pocRowIndex: int = 0
        for rowIndex in pine_range(0, profileRowsInput - 1):
            rowVolume: float = array.get(totalVolumeArray, rowIndex)
            if rowVolume > maximumRowVolume:
                maximumRowVolume = rowVolume
                pocRowIndex = rowIndex

        pocPrice: float = lowPrice + (pocRowIndex + 0.5) * rowHeight if maximumRowVolume > 0 else na
        profileSpan: int = math.max(endTime - startTime, timeframeMilliseconds * 2)
        horizontalPadding: int = cast_int(profileSpan * 0.04)
        profileLeftAnchor: int = startTime + horizontalPadding
        profileRightAnchor: int = endTime - horizontalPadding
        profileAvailableWidth: int = cast_int((profileSpan - horizontalPadding * 2) * profileWidthInput / 100.0)
        profileOnLeft: bool = profilePositionInput == 'Left'
        usePressureArchitecture: bool = profileArchitectureInput == 'Ask/Bid'

        if showProfileInput and maximumRowVolume > 0:
            areaBoxId: Box = box.new(left=startTime, top=highPrice, right=endTime, bottom=lowPrice, xloc=xloc.bar_time, border_color=profileBorderColorInput, border_width=1, border_style=line.style_dotted, bgcolor=profileAreaColorInput)
            array.push(profileBoxesArray, areaBoxId)

            pocRowBottom: float = lowPrice + pocRowIndex * rowHeight
            pocRowTop: float = pocRowBottom + rowHeight
            pocGlowBoxId: Box = box.new(left=startTime, top=pocRowTop, right=endTime, bottom=pocRowBottom, xloc=xloc.bar_time, border_color=color.new('#00000000'), border_width=0, bgcolor=color.new(pocColorInput, 86))
            array.push(profileBoxesArray, pocGlowBoxId)

            for rowIndex in pine_range(0, profileRowsInput - 1):
                rowVolume: float = array.get(totalVolumeArray, rowIndex)
                if rowVolume > 0:
                    rowWidth: int = math.max(cast_int(profileAvailableWidth * rowVolume / maximumRowVolume), 1)
                    rowLeft: int = profileLeftAnchor if profileOnLeft else profileRightAnchor - rowWidth
                    rowRight: int = rowLeft + rowWidth
                    rowBottom: float = lowPrice + rowIndex * rowHeight + rowHeight * 0.08
                    rowTop: float = lowPrice + (rowIndex + 1) * rowHeight - rowHeight * 0.08

                    if usePressureArchitecture:
                        rowAskVolume: float = array.get(askVolumeArray, rowIndex)
                        rowBidVolume: float = array.get(bidVolumeArray, rowIndex)
                        bidWidth: int = cast_int(rowWidth * rowBidVolume / rowVolume)
                        askWidth: int = rowWidth - bidWidth
                        splitPoint: int = rowLeft + bidWidth
                        if bidWidth > 0:
                            bidBoxId: Box = box.new(left=rowLeft, top=rowTop, right=splitPoint, bottom=rowBottom, xloc=xloc.bar_time, border_color=color.new(bidProfileColorInput, 15), border_width=1, bgcolor=bidProfileColorInput)
                            array.push(profileBoxesArray, bidBoxId)
                        if askWidth > 0:
                            askBoxId: Box = box.new(left=splitPoint, top=rowTop, right=rowRight, bottom=rowBottom, xloc=xloc.bar_time, border_color=color.new(askProfileColorInput, 15), border_width=1, bgcolor=askProfileColorInput)
                            array.push(profileBoxesArray, askBoxId)
                    else:
                        profileBoxId: Box = box.new(left=rowLeft, top=rowTop, right=rowRight, bottom=rowBottom, xloc=xloc.bar_time, border_color=color.new(totalProfileColorInput, 15), border_width=1, bgcolor=totalProfileColorInput)
                        array.push(profileBoxesArray, profileBoxId)

        if showHvnInput and maximumRowVolume > 0:
            selectedHvnRowsArray: list[int] = array.new_int()
            minimumHvnVolume: float = maximumRowVolume * hvnThresholdInput / 100.0
            projectionRight: int = time + extensionMilliseconds
            labelsTime: int = projectionRight + timeframeMilliseconds * hvnLabelOffsetInput

            for selectionIndex in pine_range(0, hvnCountInput - 1):
                bestRowIndex: int = -1
                bestRowVolume: float = 0.0
                for rowIndex in pine_range(1, profileRowsInput - 2):
                    nodeVolume: float = array.get(totalVolumeArray, rowIndex)
                    previousVolume: float = array.get(totalVolumeArray, rowIndex - 1)
                    nextVolume: float = array.get(totalVolumeArray, rowIndex + 1)
                    isLocalPeak: bool = nodeVolume >= previousVolume and nodeVolume > nextVolume
                    isFarFromPoc: bool = math.abs(rowIndex - pocRowIndex) >= hvnSpacingInput
                    isFarFromSelected: bool = True
                    if array.size(selectedHvnRowsArray) > 0:
                        for selectedIndex in pine_range(0, array.size(selectedHvnRowsArray) - 1):
                            if math.abs(rowIndex - array.get(selectedHvnRowsArray, selectedIndex)) < hvnSpacingInput:
                                isFarFromSelected = False
                    isQualifiedNode: bool = isLocalPeak and isFarFromPoc and isFarFromSelected and (nodeVolume >= minimumHvnVolume)
                    if isQualifiedNode and nodeVolume > bestRowVolume:
                        bestRowVolume = nodeVolume
                        bestRowIndex = rowIndex

                if bestRowIndex >= 0:
                    array.push(selectedHvnRowsArray, bestRowIndex)
                    hvnPrice: float = lowPrice + (bestRowIndex + 0.5) * rowHeight
                    sourceWidth: int = math.max(cast_int(profileAvailableWidth * bestRowVolume / maximumRowVolume), 1)
                    sourceEdge: int = profileLeftAnchor + sourceWidth if profileOnLeft else profileRightAnchor
                    nodeBottom: float = lowPrice + bestRowIndex * rowHeight + rowHeight * 0.08
                    nodeTop: float = lowPrice + (bestRowIndex + 1) * rowHeight - rowHeight * 0.08
                    hvnBoxId: Box = box.new(left=sourceEdge, top=nodeTop, right=projectionRight, bottom=nodeBottom, xloc=xloc.bar_time, border_color=color.new(hvnColorInput, 20), border_width=1, bgcolor=color.new(hvnColorInput, hvnOpacityInput))
                    array.push(profileBoxesArray, hvnBoxId)
                    if showHvnLabelsInput:
                        hvnText: str = 'HVN ' + string.tostring(selectionIndex + 1) + '  ' + string.tostring(hvnPrice, format.mintick)
                        hvnLabelId: Label = label.new(labelsTime, hvnPrice, hvnText, xloc=xloc.bar_time, style=label.style_label_left, textcolor=hvnColorInput, color=color.new('#00000000'), size=hvnLabelSize)
                        array.push(nodeLabelsArray, hvnLabelId)

        if showLvnInput and maximumRowVolume > 0:
            selectedLvnRowsArray: list[int] = array.new_int()
            maximumLvnVolume: float = maximumRowVolume * lvnThresholdInput / 100.0
            directionalLvnColor: Color = BULL_COLOR if latestChochDirection == 1 else BEAR_COLOR
            projectionRight: int = time + extensionMilliseconds
            labelsTime: int = projectionRight + timeframeMilliseconds * lvnLabelOffsetInput

            for selectionIndex in pine_range(0, lvnCountInput - 1):
                bestRowIndex: int = -1
                lowestRowVolume: float = 1e+20
                for rowIndex in pine_range(1, profileRowsInput - 2):
                    nodeVolume: float = array.get(totalVolumeArray, rowIndex)
                    previousVolume: float = array.get(totalVolumeArray, rowIndex - 1)
                    nextVolume: float = array.get(totalVolumeArray, rowIndex + 1)
                    isLocalTrough: bool = nodeVolume <= previousVolume and nodeVolume < nextVolume
                    hasNeighborVolume: bool = previousVolume > 0 or nextVolume > 0
                    isFarFromPoc: bool = math.abs(rowIndex - pocRowIndex) >= lvnSpacingInput
                    isFarFromSelected: bool = True
                    if array.size(selectedLvnRowsArray) > 0:
                        for selectedIndex in pine_range(0, array.size(selectedLvnRowsArray) - 1):
                            if math.abs(rowIndex - array.get(selectedLvnRowsArray, selectedIndex)) < lvnSpacingInput:
                                isFarFromSelected = False
                    isQualifiedNode: bool = isLocalTrough and hasNeighborVolume and isFarFromPoc and isFarFromSelected and (nodeVolume <= maximumLvnVolume)
                    if isQualifiedNode and nodeVolume < lowestRowVolume:
                        lowestRowVolume = nodeVolume
                        bestRowIndex = rowIndex

                if bestRowIndex >= 0:
                    array.push(selectedLvnRowsArray, bestRowIndex)
                    lvnPrice: float = lowPrice + (bestRowIndex + 0.5) * rowHeight
                    selectedRowVolume: float = array.get(totalVolumeArray, bestRowIndex)
                    sourceWidth: int = math.max(cast_int(profileAvailableWidth * selectedRowVolume / maximumRowVolume), 1)
                    sourceEdge: int = profileLeftAnchor + sourceWidth if profileOnLeft else profileRightAnchor
                    nodeBottom: float = lowPrice + bestRowIndex * rowHeight + rowHeight * 0.12
                    nodeTop: float = lowPrice + (bestRowIndex + 1) * rowHeight - rowHeight * 0.12
                    lvnBoxId: Box = box.new(left=sourceEdge, top=nodeTop, right=projectionRight, bottom=nodeBottom, xloc=xloc.bar_time, border_color=directionalLvnColor, border_width=1, border_style=line.style_dotted, bgcolor=color.new(directionalLvnColor, lvnOpacityInput))
                    array.push(profileBoxesArray, lvnBoxId)
                    if showLvnLabelsInput:
                        lvnText: str = 'LVN ' + string.tostring(selectionIndex + 1) + '  ' + string.tostring(lvnPrice, format.mintick)
                        lvnLabelId: Label = label.new(labelsTime, lvnPrice, lvnText, xloc=xloc.bar_time, style=label.style_label_left, textcolor=directionalLvnColor, color=color.new('#00000000'), size=lvnLabelSize)
                        array.push(nodeLabelsArray, lvnLabelId)

        return pocPrice

    if inCalc:
        if pivotHighHit:
            upperLevel = pivotHighValue
            upperPivotTime = time[pivotStrength]
            upperBroken = False
            if structureDirection != 0 and (na(activeStructureHigh) or pivotHighValue > activeStructureHigh):
                activeStructureHigh = pivotHighValue
                activeStructureHighTime = upperPivotTime

        if pivotLowHit:
            lowerLevel = pivotLowValue
            lowerPivotTime = time[pivotStrength]
            lowerBroken = False
            if structureDirection != 0 and (na(activeStructureLow) or pivotLowValue < activeStructureLow):
                activeStructureLow = pivotLowValue
                activeStructureLowTime = lowerPivotTime

    breakUp: bool = inCalc and (not na(upperLevel)) and (not upperBroken) and (close > upperLevel if requireBodyInput else high > upperLevel)
    breakDown: bool = inCalc and (not na(lowerLevel)) and (not lowerBroken) and (close < lowerLevel if requireBodyInput else low < lowerLevel)

    if breakUp:
        isChochBreak: bool = structureDirection == -1
        startsNewBullishStructure: bool = structureDirection != 1
        upperBroken = True

        breakLineId: Line = line.new(upperPivotTime, upperLevel, time, upperLevel, xloc=xloc.bar_time, extend=extend.none, color=brokenUpColorInput, style=brokenLineStyle, width=brokenWidthInput)
        breakLabelId: Label = na(Label)
        if showBreakLabelsInput:
            breakText: str = ('CHoCH' if isChochBreak else 'BOS') + '  ' + string.tostring(upperLevel, format.mintick)
            breakLabelId = label.new(cast_int(math.avg(time, upperPivotTime)), upperLevel, breakText, xloc=xloc.bar_time, style=label.style_label_down, textcolor=upLabelTextColorInput, color=labelBackgroundInput, size=structureLabelSize)
        f_pushBroken(breakLineId, breakLabelId)

        if isChochBreak:
            latestChochTime = time
            latestChochDirection = 1
            hasPreviousStructureExtremes: bool = not na(activeStructureHigh) and (not na(activeStructureHighTime)) and (not na(activeStructureLow)) and (not na(activeStructureLowTime))
            if hasPreviousStructureExtremes:
                profileStartTime = math.min(activeStructureHighTime, activeStructureLowTime)
                profileEndTime = time[1]
                profileLowPrice = activeStructureLow
                profileHighPrice = activeStructureHigh
            else:
                profileStartTime = na
                profileEndTime = na
                profileLowPrice = na
                profileHighPrice = na
                latestPocPrice = na

        if startsNewBullishStructure:
            activeStructureHigh = upperLevel
            activeStructureHighTime = upperPivotTime
            activeStructureLow = lowerLevel
            activeStructureLowTime = lowerPivotTime

        structureDirection = 1

    if breakDown:
        isChochBreak: bool = structureDirection == 1
        startsNewBearishStructure: bool = structureDirection != -1
        lowerBroken = True

        breakLineId: Line = line.new(lowerPivotTime, lowerLevel, time, lowerLevel, xloc=xloc.bar_time, extend=extend.none, color=brokenDownColorInput, style=brokenLineStyle, width=brokenWidthInput)
        breakLabelId: Label = na(Label)
        if showBreakLabelsInput:
            breakText: str = ('CHoCH' if isChochBreak else 'BOS') + '  ' + string.tostring(lowerLevel, format.mintick)
            breakLabelId = label.new(cast_int(math.avg(time, lowerPivotTime)), lowerLevel, breakText, xloc=xloc.bar_time, style=label.style_label_up, textcolor=downLabelTextColorInput, color=labelBackgroundInput, size=structureLabelSize)
        f_pushBroken(breakLineId, breakLabelId)

        if isChochBreak:
            latestChochTime = time
            latestChochDirection = -1
            hasPreviousStructureExtremes: bool = not na(activeStructureHigh) and (not na(activeStructureHighTime)) and (not na(activeStructureLow)) and (not na(activeStructureLowTime))
            if hasPreviousStructureExtremes:
                profileStartTime = math.min(activeStructureHighTime, activeStructureLowTime)
                profileEndTime = time[1]
                profileLowPrice = activeStructureLow
                profileHighPrice = activeStructureHigh
            else:
                profileStartTime = na
                profileEndTime = na
                profileLowPrice = na
                profileHighPrice = na
                latestPocPrice = na

        if startsNewBearishStructure:
            activeStructureHigh = upperLevel
            activeStructureHighTime = upperPivotTime
            activeStructureLow = lowerLevel
            activeStructureLowTime = lowerPivotTime

        structureDirection = -1

    if barstate.islast:
        f_clearProfileBoxes()
        f_clearNodeLabels()

        if not na(pocLineId):
            line.delete(pocLineId)
            pocLineId = na
        if not na(pocLabelId):
            label.delete(pocLabelId)
            pocLabelId = na

        validProfileRange: bool = not na(profileStartTime) and (not na(profileEndTime)) and (not na(profileLowPrice)) and (not na(profileHighPrice)) and (profileEndTime > profileStartTime) and (profileHighPrice > profileLowPrice)
        if validProfileRange:
            latestPocPrice = f_buildProfile(profileStartTime, profileEndTime, profileLowPrice, profileHighPrice)
            if showPocInput and (not na(latestPocPrice)):
                pocLineId = line.new(profileStartTime, latestPocPrice, time + extensionMilliseconds, latestPocPrice, xloc=xloc.bar_time, extend=extend.none, color=pocColorInput, style=pocLineStyle, width=pocWidthInput)
                if showPocLabelInput:
                    directionText: str = '↑' if latestChochDirection == 1 else '↓'
                    pocText: str = 'POC ' + directionText + '  ' + string.tostring(latestPocPrice, format.mintick)
                    pocLabelId = label.new(time + extensionMilliseconds + timeframeMilliseconds, latestPocPrice, pocText, xloc=xloc.bar_time, style=label.style_label_left, textcolor=pocLabelTextColorInput, color=pocLabelBackgroundInput, size=pocLabelSize)
        else:
            latestPocPrice = na

    pocTouched: Series[bool] = not na(latestPocPrice) and (not na(latestChochTime)) and (time > latestChochTime) and (low <= latestPocPrice) and (high >= latestPocPrice)
    firstPocTouch: bool = pocTouched and (not pocTouched[1])
    bullishPocRetest: bool = firstPocTouch and latestChochDirection == 1
    bearishPocRetest: bool = firstPocTouch and latestChochDirection == -1

    alertcondition(bullishPocRetest, title='Bullish CHoCH POC Retest', message='Price retested the active POC after a bullish CHoCH.')
    alertcondition(bearishPocRetest, title='Bearish CHoCH POC Retest', message='Price retested the active POC after a bearish CHoCH.')

    watermarkTable: Persistent[Table] = table.new(position.bottom_center, 1, 1)
    if barstate.islast:
        table.cell(watermarkTable, 0, 0, 'erdensedat' if showWatermarkInput else '', text_color=color.new(chart.fg_color, 55), text_size=size.normal, bgcolor=color.new('#00000000'))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)