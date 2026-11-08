"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, array, barmerge, barstate, box, chart, close, color,
    display, high, input, label, line, location, low, math, na, nz, plot, plotshape, position,
    request, runtime, script, shape, size, string, syminfo, ta, table, time, time_close, timeframe,
    xloc, yloc
)
from pynecore.types import Box, Color, Label, Line, Persistent, PersistentSeries, Series, Table

GROUP_TIMEFRAME: str = "Timeframes"
GROUP_STYLE: str = "Execution grid style"
GROUP_CONTEXT: str = "Context grid style"
GROUP_LEVELS: str = "Range levels"
GROUP_LABELS: str = "Labels"
GROUP_READING: str = "Range reading"
GROUP_STATS: str = "Statistics"
GROUP_ALERTS: str = "Breakouts"
MODE_SINGLE: str = "Single color"
MODE_TREND: str = "Bullish / bearish"


@script.indicator("Candle Range [MMT]", shorttitle="CR [MMT]", overlay=True, max_boxes_count=500, max_lines_count=500, max_labels_count=100)
def main(
    executionTimeframeInput=input.timeframe("", "Execution range timeframe", tooltip="Leave blank to use the chart timeframe.", group=GROUP_TIMEFRAME),
    contextTimeframeInput=input.timeframe("60", "Context range timeframe", tooltip="Higher timeframe used for directional context.", group=GROUP_TIMEFRAME),
    colorMode=input.string(MODE_TREND, "Color mode", options=(MODE_TREND, MODE_SINGLE), group=GROUP_STYLE),
    singleColor=input.color(color.white, "Single / initial color", group=GROUP_STYLE),
    bullishColor=input.color(color.lime, "Bullish reset color", group=GROUP_STYLE),
    bearishColor=input.color(color.red, "Bearish reset color", group=GROUP_STYLE),
    borderWidth=input.int(2, "Grid line width", minval=1, maxval=4, group=GROUP_STYLE),
    midpointWidth=input.int(1, "Midpoint width", minval=1, maxval=4, group=GROUP_STYLE),
    showFill=input.bool(False, "Fill execution grids", group=GROUP_STYLE),
    fillTransparency=input.int(92, "Fill transparency", minval=0, maxval=100, group=GROUP_STYLE),
    projectBars=input.int(2, "Project active grids", minval=0, maxval=499, group=GROUP_STYLE),
    gridsToKeep=input.int(300, "Historical execution grids", minval=1, maxval=450, group=GROUP_STYLE),
    showContextRange=input.bool(True, "Show context range", group=GROUP_CONTEXT),
    contextBorderWidth=input.int(1, "Context line width", minval=1, maxval=4, group=GROUP_CONTEXT),
    contextTransparency=input.int(55, "Context transparency", minval=0, maxval=100, group=GROUP_CONTEXT),
    showContextFill=input.bool(False, "Fill context range", group=GROUP_CONTEXT),
    contextFillTransparency=input.int(96, "Context fill transparency", minval=0, maxval=100, group=GROUP_CONTEXT),
    showQuarterLevels=input.bool(True, "Show execution 25% / 75%", group=GROUP_LEVELS),
    quarterWidth=input.int(1, "Quarter line width", minval=1, maxval=4, group=GROUP_LEVELS),
    quarterTransparency=input.int(40, "Quarter transparency", minval=0, maxval=100, group=GROUP_LEVELS),
    showContextMidpoint=input.bool(True, "Show context midpoint", group=GROUP_LEVELS),
    showExecutionLabels=input.bool(True, "Show execution labels", group=GROUP_LABELS),
    showQuarterLabels=input.bool(True, "Show 25% / 75% labels", group=GROUP_LABELS),
    showContextLabels=input.bool(True, "Show context labels", group=GROUP_LABELS),
    labelTransparency=input.int(70, "Label background transparency", minval=0, maxval=100, group=GROUP_LABELS),
    showSweepMarkers=input.bool(True, "Show execution range sweeps", group=GROUP_READING),
    showMidpointMarkers=input.bool(False, "Show execution midpoint reclaim / loss", group=GROUP_READING),
    showDashboard=input.bool(True, "Show range dashboard", group=GROUP_READING),
    showStatistics=input.bool(True, "Show transition statistics", tooltip="Calculated from confirmed historical range transitions available on the chart.", group=GROUP_STATS),
    minimumSamples=input.int(30, "Minimum samples", minval=1, tooltip="Statistics below this sample count are marked LOW N.", group=GROUP_STATS),
    showResetMarkers=input.bool(False, "Show execution reset markers", group=GROUP_ALERTS)
):
    executionTimeframe: str = timeframe.period if executionTimeframeInput == '' else executionTimeframeInput
    contextTimeframe: str = executionTimeframe if contextTimeframeInput == '' else contextTimeframeInput

    def calculateRange(waitForConfirmation: bool, previousBar: bool):
        stateHigh: PersistentSeries[float] = na(float)
        stateLow: PersistentSeries[float] = na(float)
        stateDirection: PersistentSeries[int] = 0
        stateSeedTime: PersistentSeries[int] = na(int)
        stateBreakStrength: PersistentSeries[float] = na(float)

        canProcess: bool = barstate.isconfirmed if waitForConfirmation else True

        if na(stateHigh) and canProcess:
            stateHigh = high
            stateLow = low
            stateDirection = 0
            stateSeedTime = time
            stateBreakStrength = na
        elif not na(stateHigh) and canProcess:
            closesAbove: bool = close > stateHigh
            closesBelow: bool = close < stateLow

            if closesAbove or closesBelow:
                previousRangeSize: float = stateHigh - stateLow
                breakoutDistance: float = close - stateHigh if closesAbove else stateLow - close

                stateBreakStrength = breakoutDistance / previousRangeSize * 100.0 if previousRangeSize > 0 else na
                stateHigh = high
                stateLow = low
                stateDirection = 1 if closesAbove else -1
                stateSeedTime = time

        __block_result__ = (na, na, na, na, na)
        if previousBar:
            __block_result__ = (stateHigh[1], stateLow[1], stateDirection[1], stateSeedTime[1], stateBreakStrength[1])
        else:
            __block_result__ = (stateHigh, stateLow, stateDirection, stateSeedTime, stateBreakStrength)
        return __block_result__

    def gridColor(direction: int):
        return singleColor if colorMode == MODE_SINGLE else bullishColor if direction > 0 else bearishColor if direction < 0 else singleColor

    def formatTimeframe(tf: str):
        seconds: int = cast_int(timeframe.in_seconds(tf))
        result: str = tf

        if seconds < 60:
            result = string.tostring(seconds) + 'S'
        elif seconds < 3600:
            result = string.tostring(cast_int(seconds / 60)) + 'm'
        elif seconds < 86400 and seconds % 3600 == 0:
            result = string.tostring(cast_int(seconds / 3600)) + 'H'
        elif seconds < 86400:
            result = string.tostring(cast_int(seconds / 60)) + 'm'
        elif seconds < 604800 and seconds % 86400 == 0:
            result = string.tostring(cast_int(seconds / 86400)) + 'D'
        elif seconds % 604800 == 0:
            result = string.tostring(cast_int(seconds / 604800)) + 'W'

        return result

    def getDirectionText(direction: int):
        return 'Bullish' if direction > 0 else 'Bearish' if direction < 0 else 'Initial'

    def getZone(price: float, bottom: float, q25: float, midpoint: float, q75: float, top: float):
        result: str = "—"

        if price > top:
            result = "Above range"
        elif price < bottom:
            result = "Below range"
        elif price >= q75:
            result = "75-100%"
        elif price >= midpoint:
            result = "50-75%"
        elif price >= q25:
            result = "25-50%"
        else:
            result = "0-25%"

        return result

    def getAlignment(contextDirection: int, executionDirection: int, price: float, contextBottom: float, contextMid: float, contextTop: float, executionMid: float):
        result: str = "Neutral"

        if price > contextTop:
            result = "Context break UP"
        elif price < contextBottom:
            result = "Context break DOWN"
        elif contextDirection > 0 and executionDirection > 0:
            result = 'STRONG BULL' if price >= contextMid and price >= executionMid else 'Bull aligned'
        elif contextDirection < 0 and executionDirection < 0:
            result = 'STRONG BEAR' if price <= contextMid and price <= executionMid else 'Bear aligned'
        elif contextDirection > 0 and executionDirection < 0:
            result = 'BULL PULLBACK' if price >= contextMid else 'Deep bull pullback'
        elif contextDirection < 0 and executionDirection > 0:
            result = 'BEAR PULLBACK' if price <= contextMid else 'Deep bear pullback'
        elif contextDirection > 0:
            result = "Bull context"
        elif contextDirection < 0:
            result = "Bear context"

        return result

    def getConfirmationRead(contextDirection: int, executionDirection: int, price: float, executionMid: float):
        result: str = "Wait"

        if contextDirection > 0:
            if executionDirection > 0:
                result = 'Long-side structure' if price >= executionMid else 'Wait for Exec Mid reclaim'
            elif executionDirection < 0:
                result = "Wait for bullish Exec shift"
            else:
                result = "Wait for Exec confirmation"
        elif contextDirection < 0:
            if executionDirection < 0:
                result = 'Short-side structure' if price <= executionMid else 'Wait for Exec Mid loss'
            elif executionDirection > 0:
                result = "Wait for bearish Exec shift"
            else:
                result = "Wait for Exec confirmation"

        return result

    def formatStat(outcome: str, successes: int, samples: int, minSamples: int):
        result: str = outcome + ' —'

        if samples > 0:
            probability: float = successes * 100.0 / samples
            sampleWarning: str = ' | LOW N' if samples < minSamples else ''
            result = outcome + ' ' + string.tostring(probability, '#.1') + '% | n=' + string.tostring(samples) + sampleWarning

        return result

    chartTimeframeSeconds: float = timeframe.in_seconds()
    executionTimeframeSeconds: float = timeframe.in_seconds(executionTimeframe)
    contextTimeframeSeconds: float = timeframe.in_seconds(contextTimeframe)

    executionUsesHigherTimeframe: bool = executionTimeframeSeconds > chartTimeframeSeconds
    contextUsesHigherTimeframe: bool = contextTimeframeSeconds > chartTimeframeSeconds

    if executionTimeframeSeconds < chartTimeframeSeconds:
        runtime.error('Candle Range [MMT]: Execution timeframe must be equal to or higher than the chart timeframe.')

    if contextTimeframeSeconds < executionTimeframeSeconds:
        runtime.error('Candle Range [MMT]: Context timeframe must be equal to or higher than the execution timeframe.')

    chartHigh, chartLow, chartDirection, chartSeedTime, chartBreakStrength = calculateRange(True, False)

    executionHtfHigh, executionHtfLow, executionHtfDirection, executionHtfSeedTime, executionHtfBreakStrength = request.security(syminfo.tickerid, executionTimeframe, calculateRange(False, True), lookahead=barmerge.lookahead_on)

    contextHtfHigh, contextHtfLow, contextHtfDirection, contextHtfSeedTime, contextHtfBreakStrength = request.security(syminfo.tickerid, contextTimeframe, calculateRange(False, True), lookahead=barmerge.lookahead_on)

    executionHigh: float = executionHtfHigh if executionUsesHigherTimeframe else chartHigh
    executionLow: float = executionHtfLow if executionUsesHigherTimeframe else chartLow
    executionDirection: int = executionHtfDirection if executionUsesHigherTimeframe else chartDirection
    executionSeedTime: Series[int] = executionHtfSeedTime if executionUsesHigherTimeframe else chartSeedTime
    executionBreakStrength: float = executionHtfBreakStrength if executionUsesHigherTimeframe else chartBreakStrength

    executionSize: float = executionHigh - executionLow
    executionQ25: float = executionLow + executionSize * 0.25
    executionMid: float = executionLow + executionSize * 0.5
    executionQ75: float = executionLow + executionSize * 0.75

    executionReady: bool = not na(executionHigh) and (not na(executionLow)) and (not na(executionSeedTime))

    newExecutionGrid: bool = executionReady and (na(executionSeedTime[1]) or executionSeedTime != executionSeedTime[1])

    bullishExecutionReset: bool = newExecutionGrid and executionDirection > 0
    bearishExecutionReset: bool = newExecutionGrid and executionDirection < 0

    contextHigh: float = contextHtfHigh if contextUsesHigherTimeframe else chartHigh
    contextLow: float = contextHtfLow if contextUsesHigherTimeframe else chartLow
    contextDirection: int = contextHtfDirection if contextUsesHigherTimeframe else chartDirection
    contextSeedTime: Series[int] = contextHtfSeedTime if contextUsesHigherTimeframe else chartSeedTime
    contextBreakStrength: float = contextHtfBreakStrength if contextUsesHigherTimeframe else chartBreakStrength

    contextSize: float = contextHigh - contextLow
    contextQ25: float = contextLow + contextSize * 0.25
    contextMid: float = contextLow + contextSize * 0.5
    contextQ75: float = contextLow + contextSize * 0.75

    contextReady: bool = not na(contextHigh) and (not na(contextLow)) and (not na(contextSeedTime))

    newContextGrid: bool = contextReady and (na(contextSeedTime[1]) or contextSeedTime != contextSeedTime[1])

    bullishContextReset: bool = newContextGrid and contextDirection > 0
    bearishContextReset: bool = newContextGrid and contextDirection < 0

    execBullSamples: Persistent[int] = 0
    execBullSuccesses: Persistent[int] = 0
    execBearSamples: Persistent[int] = 0
    execBearSuccesses: Persistent[int] = 0

    alignedBullSamples: Persistent[int] = 0
    alignedBullSuccesses: Persistent[int] = 0
    alignedBearSamples: Persistent[int] = 0
    alignedBearSuccesses: Persistent[int] = 0

    bullPullbackSamples: Persistent[int] = 0
    bullPullbackRecoveries: Persistent[int] = 0
    bearPullbackSamples: Persistent[int] = 0
    bearPullbackRecoveries: Persistent[int] = 0

    contextBullSamples: Persistent[int] = 0
    contextBullSuccesses: Persistent[int] = 0
    contextBearSamples: Persistent[int] = 0
    contextBearSuccesses: Persistent[int] = 0

    trackedExecutionDirection: Persistent[int] = 0
    trackedExecutionContextDirection: Persistent[int] = 0

    trackedContextDirection: Persistent[int] = 0

    if newExecutionGrid and executionDirection != 0:
        if trackedExecutionDirection != 0:
            if trackedExecutionDirection > 0:
                execBullSamples += 1

                if executionDirection > 0:
                    execBullSuccesses += 1
            else:
                execBearSamples += 1

                if executionDirection < 0:
                    execBearSuccesses += 1

            if trackedExecutionContextDirection > 0 and trackedExecutionDirection > 0:
                alignedBullSamples += 1

                if executionDirection > 0:
                    alignedBullSuccesses += 1
            elif trackedExecutionContextDirection < 0 and trackedExecutionDirection < 0:
                alignedBearSamples += 1

                if executionDirection < 0:
                    alignedBearSuccesses += 1
            elif trackedExecutionContextDirection > 0 and trackedExecutionDirection < 0:
                bullPullbackSamples += 1

                if executionDirection > 0:
                    bullPullbackRecoveries += 1
            elif trackedExecutionContextDirection < 0 and trackedExecutionDirection > 0:
                bearPullbackSamples += 1

                if executionDirection < 0:
                    bearPullbackRecoveries += 1

        trackedExecutionDirection = executionDirection
        trackedExecutionContextDirection = contextDirection if contextReady else 0

    if newContextGrid and contextDirection != 0:
        if trackedContextDirection != 0:
            if trackedContextDirection > 0:
                contextBullSamples += 1

                if contextDirection > 0:
                    contextBullSuccesses += 1
            else:
                contextBearSamples += 1

                if contextDirection < 0:
                    contextBearSuccesses += 1

        trackedContextDirection = contextDirection

    executionStatText: str = "—"

    if executionDirection > 0:
        executionStatText = formatStat('Next Bull', execBullSuccesses, execBullSamples, minimumSamples)
    elif executionDirection < 0:
        executionStatText = formatStat('Next Bear', execBearSuccesses, execBearSamples, minimumSamples)

    stateStatText: str = "—"

    if contextDirection > 0 and executionDirection > 0:
        stateStatText = formatStat('Next Bull', alignedBullSuccesses, alignedBullSamples, minimumSamples)
    elif contextDirection < 0 and executionDirection < 0:
        stateStatText = formatStat('Next Bear', alignedBearSuccesses, alignedBearSamples, minimumSamples)
    elif contextDirection > 0 and executionDirection < 0:
        stateStatText = formatStat('Recover Bull', bullPullbackRecoveries, bullPullbackSamples, minimumSamples)
    elif contextDirection < 0 and executionDirection > 0:
        stateStatText = formatStat('Recover Bear', bearPullbackRecoveries, bearPullbackSamples, minimumSamples)

    contextStatText: str = "—"

    if contextDirection > 0:
        contextStatText = formatStat('Next Bull', contextBullSuccesses, contextBullSamples, minimumSamples)
    elif contextDirection < 0:
        contextStatText = formatStat('Next Bear', contextBearSuccesses, contextBearSamples, minimumSamples)

    lowerExecutionSweep: bool = executionReady and (not newExecutionGrid) and (low < executionLow) and (close >= executionLow)
    upperExecutionSweep: bool = executionReady and (not newExecutionGrid) and (high > executionHigh) and (close <= executionHigh)

    executionMidReclaim: bool = executionReady and (not newExecutionGrid) and ta.crossover(close, executionMid)
    executionMidLoss: bool = executionReady and (not newExecutionGrid) and ta.crossunder(close, executionMid)

    executionPosition: float = (close - executionLow) / executionSize * 100.0 if executionReady and executionSize > 0 else na
    contextPosition: float = (close - contextLow) / contextSize * 100.0 if contextReady and contextSize > 0 else na

    executionZone: str = getZone(close, executionLow, executionQ25, executionMid, executionQ75, executionHigh) if executionReady else '—'
    contextZone: str = getZone(close, contextLow, contextQ25, contextMid, contextQ75, contextHigh) if contextReady else '—'

    alignmentRead: str = getAlignment(contextDirection, executionDirection, close, contextLow, contextMid, contextHigh, executionMid) if executionReady and contextReady else '—'

    confirmationRead: str = getConfirmationRead(contextDirection, executionDirection, close, executionMid) if executionReady and contextReady else '—'

    executionAge: int = nz(ta.barssince(newExecutionGrid))
    contextAge: int = nz(ta.barssince(newContextGrid))

    chartBarDuration: int = time_close - time
    activeRightTime: int = time_close + projectBars * chartBarDuration
    contextLabelRightTime: int = activeRightTime + chartBarDuration

    executionTimeframeText: str = formatTimeframe(executionTimeframe)
    contextTimeframeText: str = formatTimeframe(contextTimeframe)

    activeExecutionGrid: Persistent[Box] = na(Box)

    activeExecutionMid: Persistent[Line] = na(Line)
    activeExecutionQ25: Persistent[Line] = na(Line)
    activeExecutionQ75: Persistent[Line] = na(Line)

    executionGrids: Persistent[list[Box]] = array.new_box()
    executionMids: Persistent[list[Line]] = array.new_line()

    executionHighLabel: Persistent[Label] = na(Label)
    executionQ75Label: Persistent[Label] = na(Label)
    executionMidLabel: Persistent[Label] = na(Label)
    executionQ25Label: Persistent[Label] = na(Label)
    executionLowLabel: Persistent[Label] = na(Label)

    activeContextGrid: Persistent[Box] = na(Box)
    activeContextMid: Persistent[Line] = na(Line)

    contextHighLabel: Persistent[Label] = na(Label)
    contextMidLabel: Persistent[Label] = na(Label)
    contextLowLabel: Persistent[Label] = na(Label)

    if executionReady:
        executionColor: Color = gridColor(executionDirection)
        executionQuarterColor: Color = color.new(executionColor, quarterTransparency)

        if newExecutionGrid:
            if not na(activeExecutionGrid):
                box.set_right(activeExecutionGrid, executionSeedTime)

            if not na(activeExecutionMid):
                line.set_x2(activeExecutionMid, executionSeedTime)

            if not na(activeExecutionQ25):
                line.delete(activeExecutionQ25)

            if not na(activeExecutionQ75):
                line.delete(activeExecutionQ75)

            activeExecutionQ25 = na
            activeExecutionQ75 = na

            activeExecutionGrid = box.new(left=executionSeedTime, top=executionHigh, right=activeRightTime, bottom=executionLow, xloc=xloc.bar_time, border_color=executionColor, border_width=borderWidth, bgcolor=color.new(executionColor, fillTransparency) if showFill else na)

            activeExecutionMid = line.new(x1=executionSeedTime, y1=executionMid, x2=activeRightTime, y2=executionMid, xloc=xloc.bar_time, color=executionColor, style=line.style_dashed, width=midpointWidth)

            if showQuarterLevels:
                activeExecutionQ25 = line.new(x1=executionSeedTime, y1=executionQ25, x2=activeRightTime, y2=executionQ25, xloc=xloc.bar_time, color=executionQuarterColor, style=line.style_dotted, width=quarterWidth)

                activeExecutionQ75 = line.new(x1=executionSeedTime, y1=executionQ75, x2=activeRightTime, y2=executionQ75, xloc=xloc.bar_time, color=executionQuarterColor, style=line.style_dotted, width=quarterWidth)

            array.push(executionGrids, activeExecutionGrid)
            array.push(executionMids, activeExecutionMid)

            if array.size(executionGrids) > gridsToKeep:
                oldestGrid: Box = array.shift(executionGrids)
                oldestMid: Line = array.shift(executionMids)

                box.delete(oldestGrid)
                line.delete(oldestMid)
        else:
            if not na(activeExecutionGrid):
                box.set_right(activeExecutionGrid, activeRightTime)

            if not na(activeExecutionMid):
                line.set_x2(activeExecutionMid, activeRightTime)

            if showQuarterLevels:
                if not na(activeExecutionQ25):
                    line.set_x2(activeExecutionQ25, activeRightTime)

                if not na(activeExecutionQ75):
                    line.set_x2(activeExecutionQ75, activeRightTime)

    if contextReady and showContextRange:
        rawContextColor: Color = gridColor(contextDirection)
        contextColor: Color = color.new(rawContextColor, contextTransparency)

        if newContextGrid or na(activeContextGrid):
            if not na(activeContextGrid):
                box.delete(activeContextGrid)

            if not na(activeContextMid):
                line.delete(activeContextMid)

            activeContextGrid = box.new(left=contextSeedTime, top=contextHigh, right=activeRightTime, bottom=contextLow, xloc=xloc.bar_time, border_color=contextColor, border_width=contextBorderWidth, bgcolor=color.new(rawContextColor, contextFillTransparency) if showContextFill else na)

            if showContextMidpoint:
                activeContextMid = line.new(x1=contextSeedTime, y1=contextMid, x2=activeRightTime, y2=contextMid, xloc=xloc.bar_time, color=contextColor, style=line.style_dashed, width=contextBorderWidth)
        else:
            if not na(activeContextGrid):
                box.set_right(activeContextGrid, activeRightTime)

            if showContextMidpoint and (not na(activeContextMid)):
                line.set_x2(activeContextMid, activeRightTime)

    if executionReady and showExecutionLabels:
        executionColor: Color = gridColor(executionDirection)
        labelBackground: Color = color.new(executionColor, labelTransparency)

        if na(executionHighLabel):
            executionHighLabel = label.new(x=activeRightTime, y=executionHigh, text=executionTimeframeText + ' High', xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_left, color=labelBackground, textcolor=chart.fg_color, size=size.small)
        else:
            label.set_xy(executionHighLabel, activeRightTime, executionHigh)
            label.set_text(executionHighLabel, executionTimeframeText + ' High')
            label.set_color(executionHighLabel, labelBackground)

        if na(executionMidLabel):
            executionMidLabel = label.new(x=activeRightTime, y=executionMid, text=executionTimeframeText + ' Mid', xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_left, color=labelBackground, textcolor=chart.fg_color, size=size.small)
        else:
            label.set_xy(executionMidLabel, activeRightTime, executionMid)
            label.set_text(executionMidLabel, executionTimeframeText + ' Mid')
            label.set_color(executionMidLabel, labelBackground)

        if na(executionLowLabel):
            executionLowLabel = label.new(x=activeRightTime, y=executionLow, text=executionTimeframeText + ' Low', xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_left, color=labelBackground, textcolor=chart.fg_color, size=size.small)
        else:
            label.set_xy(executionLowLabel, activeRightTime, executionLow)
            label.set_text(executionLowLabel, executionTimeframeText + ' Low')
            label.set_color(executionLowLabel, labelBackground)

        if showQuarterLabels:
            if na(executionQ75Label):
                executionQ75Label = label.new(x=activeRightTime, y=executionQ75, text=executionTimeframeText + ' 75%', xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_left, color=labelBackground, textcolor=chart.fg_color, size=size.tiny)
            else:
                label.set_xy(executionQ75Label, activeRightTime, executionQ75)
                label.set_text(executionQ75Label, executionTimeframeText + ' 75%')
                label.set_color(executionQ75Label, labelBackground)

            if na(executionQ25Label):
                executionQ25Label = label.new(x=activeRightTime, y=executionQ25, text=executionTimeframeText + ' 25%', xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_left, color=labelBackground, textcolor=chart.fg_color, size=size.tiny)
            else:
                label.set_xy(executionQ25Label, activeRightTime, executionQ25)
                label.set_text(executionQ25Label, executionTimeframeText + ' 25%')
                label.set_color(executionQ25Label, labelBackground)

    if contextReady and showContextRange and showContextLabels:
        rawContextColor: Color = gridColor(contextDirection)
        labelBackground: Color = color.new(rawContextColor, math.min(labelTransparency + 15, 100))

        if na(contextHighLabel):
            contextHighLabel = label.new(x=contextLabelRightTime, y=contextHigh, text=contextTimeframeText + ' Context High', xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_left, color=labelBackground, textcolor=chart.fg_color, size=size.tiny)
        else:
            label.set_xy(contextHighLabel, contextLabelRightTime, contextHigh)
            label.set_text(contextHighLabel, contextTimeframeText + ' Context High')
            label.set_color(contextHighLabel, labelBackground)

        if na(contextMidLabel):
            contextMidLabel = label.new(x=contextLabelRightTime, y=contextMid, text=contextTimeframeText + ' Context Mid', xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_left, color=labelBackground, textcolor=chart.fg_color, size=size.tiny)
        else:
            label.set_xy(contextMidLabel, contextLabelRightTime, contextMid)
            label.set_text(contextMidLabel, contextTimeframeText + ' Context Mid')
            label.set_color(contextMidLabel, labelBackground)

        if na(contextLowLabel):
            contextLowLabel = label.new(x=contextLabelRightTime, y=contextLow, text=contextTimeframeText + ' Context Low', xloc=xloc.bar_time, yloc=yloc.price, style=label.style_label_left, color=labelBackground, textcolor=chart.fg_color, size=size.tiny)
        else:
            label.set_xy(contextLowLabel, contextLabelRightTime, contextLow)
            label.set_text(contextLowLabel, contextTimeframeText + ' Context Low')
            label.set_color(contextLowLabel, labelBackground)

    dashboard: Persistent[Table] = table.new(position.top_right, 2, 11, border_width=1)

    if barstate.islast and showDashboard and executionReady and contextReady:
        executionColor: Color = gridColor(executionDirection)
        contextColor: Color = gridColor(contextDirection)
        neutralBackground: Color = color.new(chart.bg_color, 10)
        stateColor: Color = bullishColor if contextDirection > 0 else bearishColor if contextDirection < 0 else chart.fg_color

        contextPositionText: str = '—' if na(contextPosition) else string.tostring(contextPosition, '#.0') + '%'
        executionPositionText: str = '—' if na(executionPosition) else string.tostring(executionPosition, '#.0') + '%'
        contextBreakText: str = '—' if na(contextBreakStrength) else string.tostring(contextBreakStrength, '#.1') + '%'
        executionBreakText: str = '—' if na(executionBreakStrength) else string.tostring(executionBreakStrength, '#.1') + '%'

        table.cell(dashboard, 0, 0, 'Context', text_color=chart.fg_color, bgcolor=neutralBackground)
        table.cell(dashboard, 1, 0, contextTimeframeText + ' ' + getDirectionText(contextDirection), text_color=contextColor, bgcolor=neutralBackground)

        table.cell(dashboard, 0, 1, 'Execution', text_color=chart.fg_color, bgcolor=neutralBackground)
        table.cell(dashboard, 1, 1, executionTimeframeText + ' ' + getDirectionText(executionDirection), text_color=executionColor, bgcolor=neutralBackground)

        table.cell(dashboard, 0, 2, 'Alignment', text_color=chart.fg_color, bgcolor=neutralBackground)
        table.cell(dashboard, 1, 2, alignmentRead, text_color=stateColor, bgcolor=neutralBackground)

        table.cell(dashboard, 0, 3, 'Read', text_color=chart.fg_color, bgcolor=neutralBackground)
        table.cell(dashboard, 1, 3, confirmationRead, text_color=stateColor, bgcolor=neutralBackground)

        table.cell(dashboard, 0, 4, 'Exec Stat', text_color=chart.fg_color, bgcolor=neutralBackground)
        table.cell(dashboard, 1, 4, executionStatText if showStatistics else 'Off', text_color=executionColor, bgcolor=neutralBackground)

        table.cell(dashboard, 0, 5, 'State Stat', text_color=chart.fg_color, bgcolor=neutralBackground)
        table.cell(dashboard, 1, 5, stateStatText if showStatistics else 'Off', text_color=stateColor, bgcolor=neutralBackground)

        table.cell(dashboard, 0, 6, 'Context Stat', text_color=chart.fg_color, bgcolor=neutralBackground)
        table.cell(dashboard, 1, 6, contextStatText if showStatistics else 'Off', text_color=contextColor, bgcolor=neutralBackground)

        table.cell(dashboard, 0, 7, 'Context Pos', text_color=chart.fg_color, bgcolor=neutralBackground)
        table.cell(dashboard, 1, 7, contextPositionText + ' | ' + contextZone, text_color=chart.fg_color, bgcolor=neutralBackground)

        table.cell(dashboard, 0, 8, 'Exec Pos', text_color=chart.fg_color, bgcolor=neutralBackground)
        table.cell(dashboard, 1, 8, executionPositionText + ' | ' + executionZone, text_color=chart.fg_color, bgcolor=neutralBackground)

        table.cell(dashboard, 0, 9, 'Break', text_color=chart.fg_color, bgcolor=neutralBackground)
        table.cell(dashboard, 1, 9, 'C ' + contextBreakText + ' | E ' + executionBreakText, text_color=chart.fg_color, bgcolor=neutralBackground)

        table.cell(dashboard, 0, 10, 'Age', text_color=chart.fg_color, bgcolor=neutralBackground)
        table.cell(dashboard, 1, 10, 'C ' + string.tostring(contextAge) + ' | E ' + string.tostring(executionAge), text_color=chart.fg_color, bgcolor=neutralBackground)

    plotshape(showSweepMarkers and lowerExecutionSweep, title='Lower execution range sweep', text='SWP', style=shape.triangleup, location=location.belowbar, color=bullishColor, textcolor=bullishColor, size=size.tiny)

    plotshape(showSweepMarkers and upperExecutionSweep, title='Upper execution range sweep', text='SWP', style=shape.triangledown, location=location.abovebar, color=bearishColor, textcolor=bearishColor, size=size.tiny)

    plotshape(showMidpointMarkers and executionMidReclaim, title='Execution midpoint reclaim', style=shape.circle, location=location.belowbar, color=bullishColor, size=size.tiny)

    plotshape(showMidpointMarkers and executionMidLoss, title='Execution midpoint loss', style=shape.circle, location=location.abovebar, color=bearishColor, size=size.tiny)

    plotshape(showResetMarkers and bullishExecutionReset, title='Bullish execution reset', style=shape.triangleup, location=location.belowbar, color=bullishColor, size=size.tiny)

    plotshape(showResetMarkers and bearishExecutionReset, title='Bearish execution reset', style=shape.triangledown, location=location.abovebar, color=bearishColor, size=size.tiny)

    plot(executionHigh, 'Execution range high', display=display.data_window)
    plot(executionQ75, 'Execution 75%', display=display.data_window)
    plot(executionMid, 'Execution midpoint', display=display.data_window)
    plot(executionQ25, 'Execution 25%', display=display.data_window)
    plot(executionLow, 'Execution range low', display=display.data_window)
    plot(executionPosition, 'Execution position %', display=display.data_window)
    plot(executionBreakStrength, 'Execution breakout strength %', display=display.data_window)

    plot(contextHigh, 'Context range high', display=display.data_window)
    plot(contextMid, 'Context midpoint', display=display.data_window)
    plot(contextLow, 'Context range low', display=display.data_window)
    plot(contextPosition, 'Context position %', display=display.data_window)
    plot(contextBreakStrength, 'Context breakout strength %', display=display.data_window)

    alertcondition(bullishExecutionReset, title='Bullish execution range reset', message='Candle Range [MMT]: execution range reset bullish.')

    alertcondition(bearishExecutionReset, title='Bearish execution range reset', message='Candle Range [MMT]: execution range reset bearish.')

    alertcondition(bullishContextReset, title='Bullish context range reset', message='Candle Range [MMT]: context range reset bullish.')

    alertcondition(bearishContextReset, title='Bearish context range reset', message='Candle Range [MMT]: context range reset bearish.')

    alertcondition(lowerExecutionSweep, title='Lower execution range sweep', message='Candle Range [MMT]: price swept below the execution range and closed back inside.')

    alertcondition(upperExecutionSweep, title='Upper execution range sweep', message='Candle Range [MMT]: price swept above the execution range and closed back inside.')

    alertcondition(executionMidReclaim, title='Execution midpoint reclaimed', message='Candle Range [MMT]: price reclaimed the execution-range midpoint.')

    alertcondition(executionMidLoss, title='Execution midpoint lost', message='Candle Range [MMT]: price lost the execution-range midpoint.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
