"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    bar_index, barstate, box, close, color, dayofweek, display, extend,
    format, high, input, label, line, location, low, math, na, plot, plotshape, position, script,
    shape, size, string, syminfo, table, text, time, timeframe, volume, xloc
)
from pynecore.types import Box, Color, Label, Line, Persistent, Series, Table

TOP_RIGHT: str = "Top Right"
BOTTOM_RIGHT: str = "Bottom Right"
BOTTOM_LEFT: str = "Bottom Left"
TINY: str = "Tiny"
SMALL: str = "Small"
NORMAL: str = "Normal"
LARGE: str = "Large"
HUGE: str = "Huge"
SESSION_A_GROUP: str = "Session A"
SESSION_B_GROUP: str = "Session B"
SESSION_C_GROUP: str = "Session C"
SESSION_D_GROUP: str = "Session D"
TIMEZONE_GROUP: str = "Timezone"
RANGES_GROUP: str = "Ranges Settings"
STYLE_GROUP: str = "Style"
DASHBOARD_GROUP: str = "Dashboard"
DIVIDERS_GROUP: str = "Dividers"
showSessionTooltip: str = "Enable or disable this session and all of its optional displays."
sessionNameTooltip: str = "Set the name displayed for this session."
sessionTimeTooltip: str = "Set the session's start and end times."
sessionRangeTooltip: str = "Draw a box around the high-to-low range formed during the session."
sessionTrendlineTooltip: str = "Draw a linear-regression trendline during the session."
sessionMeanTooltip: str = "Draw the running arithmetic mean during the session."
sessionVwapTooltip: str = "Plot the running volume-weighted average price during the session."
sessionMaxMinTooltip: str = "Extend the completed session's maximum and minimum until the next session begins."
sessionColorTooltip: str = "Select the color used for this session's visuals."
timezoneOffsetTooltip: str = "Set the fixed UTC offset used to interpret all session times."
exchangeTimezoneTooltip: str = "Use the symbol's exchange timezone instead of the fixed UTC offset."
rangeTransparencyTooltip: str = "Set the transparency of session range boxes from 0 (opaque) to 100 (invisible)."
rangeOutlineTooltip: str = "Show a dotted outline around each session range box."
rangeLabelTooltip: str = "Show the session name above each range box."
dashboardTooltip: str = "Enable or disable the dashboard."
advancedDashboardTooltip: str = "Add trend, cumulative volume, and volatility statistics to the dashboard."
dashboardPositionTooltip: str = "Select the dashboard location."
dashboardSizeTooltip: str = "Select the dashboard text size."
sessionDividerTooltip: str = "Mark active session bars and session boundaries along the bottom of the chart."
dayDividerTooltip: str = "Draw a dashed divider and weekday label when a new day begins."


@script.indicator("Sessions [LuxAlgo]", "LuxAlgo - Sessions", overlay=True, max_bars_back=500, max_lines_count=500, max_boxes_count=500, max_labels_count=500)
def main(
    showSessionAInput=input.bool(True, "Enable", group=SESSION_A_GROUP, tooltip=showSessionTooltip, inline="sessionA"),
    sessionANameInput=input.string("New York", "Name", group=SESSION_A_GROUP, tooltip=sessionNameTooltip, inline="sessionA"),
    sessionATimeInput=input.session("1300-2200", "Hours", group=SESSION_A_GROUP, tooltip=sessionTimeTooltip),
    sessionARangeInput=input.bool(True, "Range", group=SESSION_A_GROUP, tooltip=sessionRangeTooltip, inline="sessionAOverlays"),
    sessionATrendlineInput=input.bool(False, "Trendline", group=SESSION_A_GROUP, tooltip=sessionTrendlineTooltip, inline="sessionAOverlays"),
    sessionAMeanInput=input.bool(False, "Mean", group=SESSION_A_GROUP, tooltip=sessionMeanTooltip, inline="sessionAOverlays"),
    sessionAVwapInput=input.bool(False, "VWAP", group=SESSION_A_GROUP, tooltip=sessionVwapTooltip, inline="sessionAOverlays"),
    sessionAMaxMinInput=input.bool(False, "Max/Min", group=SESSION_A_GROUP, tooltip=sessionMaxMinTooltip, inline="sessionAOverlays"),
    showSessionBInput=input.bool(True, "Enable", group=SESSION_B_GROUP, tooltip=showSessionTooltip, inline="sessionB"),
    sessionBNameInput=input.string("London", "Name", group=SESSION_B_GROUP, tooltip=sessionNameTooltip, inline="sessionB"),
    sessionBTimeInput=input.session("0700-1600", "Hours", group=SESSION_B_GROUP, tooltip=sessionTimeTooltip),
    sessionBRangeInput=input.bool(True, "Range", group=SESSION_B_GROUP, tooltip=sessionRangeTooltip, inline="sessionBOverlays"),
    sessionBTrendlineInput=input.bool(False, "Trendline", group=SESSION_B_GROUP, tooltip=sessionTrendlineTooltip, inline="sessionBOverlays"),
    sessionBMeanInput=input.bool(False, "Mean", group=SESSION_B_GROUP, tooltip=sessionMeanTooltip, inline="sessionBOverlays"),
    sessionBVwapInput=input.bool(False, "VWAP", group=SESSION_B_GROUP, tooltip=sessionVwapTooltip, inline="sessionBOverlays"),
    sessionBMaxMinInput=input.bool(False, "Max/Min", group=SESSION_B_GROUP, tooltip=sessionMaxMinTooltip, inline="sessionBOverlays"),
    showSessionCInput=input.bool(True, "Enable", group=SESSION_C_GROUP, tooltip=showSessionTooltip, inline="sessionC"),
    sessionCNameInput=input.string("Tokyo", "Name", group=SESSION_C_GROUP, tooltip=sessionNameTooltip, inline="sessionC"),
    sessionCTimeInput=input.session("0000-0900", "Hours", group=SESSION_C_GROUP, tooltip=sessionTimeTooltip),
    sessionCRangeInput=input.bool(True, "Range", group=SESSION_C_GROUP, tooltip=sessionRangeTooltip, inline="sessionCOverlays"),
    sessionCTrendlineInput=input.bool(False, "Trendline", group=SESSION_C_GROUP, tooltip=sessionTrendlineTooltip, inline="sessionCOverlays"),
    sessionCMeanInput=input.bool(False, "Mean", group=SESSION_C_GROUP, tooltip=sessionMeanTooltip, inline="sessionCOverlays"),
    sessionCVwapInput=input.bool(False, "VWAP", group=SESSION_C_GROUP, tooltip=sessionVwapTooltip, inline="sessionCOverlays"),
    sessionCMaxMinInput=input.bool(False, "Max/Min", group=SESSION_C_GROUP, tooltip=sessionMaxMinTooltip, inline="sessionCOverlays"),
    showSessionDInput=input.bool(True, "Enable", group=SESSION_D_GROUP, tooltip=showSessionTooltip, inline="sessionD"),
    sessionDNameInput=input.string("Sydney", "Name", group=SESSION_D_GROUP, tooltip=sessionNameTooltip, inline="sessionD"),
    sessionDTimeInput=input.session("2100-0600", "Hours", group=SESSION_D_GROUP, tooltip=sessionTimeTooltip),
    sessionDRangeInput=input.bool(True, "Range", group=SESSION_D_GROUP, tooltip=sessionRangeTooltip, inline="sessionDOverlays"),
    sessionDTrendlineInput=input.bool(False, "Trendline", group=SESSION_D_GROUP, tooltip=sessionTrendlineTooltip, inline="sessionDOverlays"),
    sessionDMeanInput=input.bool(False, "Mean", group=SESSION_D_GROUP, tooltip=sessionMeanTooltip, inline="sessionDOverlays"),
    sessionDVwapInput=input.bool(False, "VWAP", group=SESSION_D_GROUP, tooltip=sessionVwapTooltip, inline="sessionDOverlays"),
    sessionDMaxMinInput=input.bool(False, "Max/Min", group=SESSION_D_GROUP, tooltip=sessionMaxMinTooltip, inline="sessionDOverlays"),
    timezoneOffsetInput=input.int(0, "UTC (+/-)", group=TIMEZONE_GROUP, tooltip=timezoneOffsetTooltip, minval=-12, maxval=14),
    useExchangeTimezoneInput=input.bool(False, "Use Exchange Timezone", group=TIMEZONE_GROUP, tooltip=exchangeTimezoneTooltip),
    rangeTransparencyInput=input.int(90, "Range Area Transparency", group=RANGES_GROUP, tooltip=rangeTransparencyTooltip, minval=0, maxval=100),
    showRangeOutlineInput=input.bool(True, "Range Outline", group=RANGES_GROUP, tooltip=rangeOutlineTooltip),
    showRangeLabelInput=input.bool(True, "Range Label", group=RANGES_GROUP, tooltip=rangeLabelTooltip),
    sessionAColorInput=input.color(color.new('#FF5D00'), "New York", group=STYLE_GROUP, tooltip=sessionColorTooltip, inline="sessionColors"),
    sessionBColorInput=input.color(color.new('#2157F3'), "London", group=STYLE_GROUP, tooltip=sessionColorTooltip, inline="sessionColors"),
    sessionCColorInput=input.color(color.new('#E91E63'), "Tokyo", group=STYLE_GROUP, tooltip=sessionColorTooltip, inline="sessionColors2"),
    sessionDColorInput=input.color(color.new('#FFEB3B'), "Sydney", group=STYLE_GROUP, tooltip=sessionColorTooltip, inline="sessionColors2"),
    dashboardInput=input.bool(False, "Dashboard", group=DASHBOARD_GROUP, tooltip=dashboardTooltip),
    advancedDashboardInput=input.bool(False, "Advanced", group=DASHBOARD_GROUP, tooltip=advancedDashboardTooltip),
    dashboardPositionInput=input.string(TOP_RIGHT, "Position", group=DASHBOARD_GROUP, tooltip=dashboardPositionTooltip, options=(TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT)),
    dashboardSizeInput=input.string(SMALL, "Size", group=DASHBOARD_GROUP, tooltip=dashboardSizeTooltip, options=(TINY, SMALL, NORMAL, LARGE, HUGE)),
    showSessionDividerInput=input.bool(False, "Show Sessions Divider", group=DIVIDERS_GROUP, tooltip=sessionDividerTooltip),
    showDayDividerInput=input.bool(True, "Show Daily Divider", group=DIVIDERS_GROUP, tooltip=dayDividerTooltip)
):
    BULL_COLOR: Color = color.new('#089981')
    BEAR_COLOR: Color = color.new('#F23645')
    DATA: Color = color.new('#DBDBDB')
    HEADERS: Color = color.new('#808080')
    BACKGROUND: Color = color.new('#161616')
    BORDERS: Color = color.new('#2E2E2E')



    __block_result__ = na
    __switch__ = dashboardPositionInput
    if __switch__ == TOP_RIGHT:
        __block_result__ = position.top_right
    elif __switch__ == BOTTOM_RIGHT:
        __block_result__ = position.bottom_right
    elif __switch__ == BOTTOM_LEFT:
        __block_result__ = position.bottom_left
    parsedDashboardPosition: Persistent = __block_result__

    __block_result_1__ = na
    __switch__ = dashboardSizeInput
    if __switch__ == TINY:
        __block_result_1__ = size.tiny
    elif __switch__ == SMALL:
        __block_result_1__ = size.small
    elif __switch__ == NORMAL:
        __block_result_1__ = size.normal
    elif __switch__ == LARGE:
        __block_result_1__ = size.large
    elif __switch__ == HUGE:
        __block_result_1__ = size.huge
    parsedDashboardSize: Persistent = __block_result_1__

    sessionTimezone: str = syminfo.timezone if useExchangeTimezoneInput else string.format('UTC{0}{1}', '+' if timezoneOffsetInput >= 0 else '-', math.abs(timezoneOffsetInput))
    barNumber: int = bar_index

    def cell(tableId: Table, column: int, row: int, data: str, textColor: Color = color.new('#DBDBDB'), alignment: str = text.align_right, background: Color = na, height: float = 0.0):
        return table.cell(tableId, column, row, data, text_color=textColor, text_size=parsedDashboardSize, text_halign=alignment, bgcolor=background, height=height)

    def divider(tableId: Table, row: int, lastColumn: int):
        rowDivider: str = "━━━━━━━━━━━━━━"
        table.merge_cells(tableId, 0, row, lastColumn, row)
        return cell(tableId, 0, row, rowDivider, textColor=BORDERS, alignment=text.align_center, height=0.5)

    def getSessionAverage(sessionActive: Series[bool]):
        length: Persistent[int] = 0
        cumulativeClose: Persistent[float] = na(float)
        average: Persistent[float] = na(float)
        sessionStarted: bool = sessionActive and (not sessionActive[1])

        if sessionStarted:
            length = 1
            cumulativeClose = close
            average = close
        elif sessionActive:
            length += 1
            cumulativeClose += close
            average = cumulativeClose / length
        else:
            average = na

        return average

    def getSessionLinearRegression(sessionActive: Series[bool]):
        length: Persistent[int] = 0
        cumulativeWeightedClose: Persistent[float] = na(float)
        cumulativeClose: Persistent[float] = na(float)
        cumulativeSquaredClose: Persistent[float] = na(float)
        firstValue: Persistent[float] = na(float)
        lastValue: Persistent[float] = na(float)
        deviation: Persistent[float] = na(float)
        correlation: Persistent[float] = na(float)
        sessionStarted: bool = sessionActive and (not sessionActive[1])

        if sessionStarted:
            length = 1
            cumulativeWeightedClose = close
            cumulativeClose = close
            cumulativeSquaredClose = close * close
            firstValue = close
            lastValue = close
            deviation = 0.0
            correlation = na
        elif sessionActive:
            length += 1
            cumulativeClose += close
            cumulativeSquaredClose += close * close
            cumulativeWeightedClose += close * length

            average: float = cumulativeClose / length
            weightedAverage: float = cumulativeWeightedClose / (length * (length + 1) / 2.0)
            covariance: float = (weightedAverage - average) * (length + 1) / 2.0
            variance: float = math.max(cumulativeSquaredClose / length - average * average, 0.0)
            correlationDenominator: float = math.sqrt(variance) * (math.sqrt(length * length - 1.0) / (2.0 * math.sqrt(3.0)))

            deviation = math.sqrt(variance)
            correlation = covariance / correlationDenominator if correlationDenominator != 0.0 else na
            firstValue = 4.0 * average - 3.0 * weightedAverage
            lastValue = 3.0 * weightedAverage - 2.0 * average

        return (firstValue, lastValue, deviation, correlation)

    def getSessionVwap(sessionActive: Series[bool]):
        numerator: Persistent[float] = na(float)
        denominator: Persistent[float] = na(float)
        sessionStarted: bool = sessionActive and (not sessionActive[1])

        if sessionStarted:
            numerator = close * volume
            denominator = volume
        elif sessionActive:
            numerator += close * volume
            denominator += volume
        else:
            numerator = na

        return (numerator, denominator)

    def setSessionLine(sessionActive: Series[bool], firstValue: float, lastValue: float, sessionColor: Color):
        lineId: Persistent[Line] = na(Line)
        sessionStarted: bool = sessionActive and (not sessionActive[1])

        if sessionStarted:
            lineId = line.new(barNumber, firstValue, barNumber, lastValue, color=sessionColor)
        elif sessionActive and (not na(lineId)):
            line.set_y1(lineId, firstValue)
            line.set_xy2(lineId, barNumber, lastValue)

        return lineId

    def getSessionRange(sessionActive: Series[bool], sessionName: str, sessionColor: Color, drawRange: bool):
        sessionStartTime: Persistent[int] = 0
        sessionHigh: Persistent[float] = na(float)
        sessionLow: Persistent[float] = na(float)
        rangeBoxId: Persistent[Box] = na(Box)
        rangeLabelId: Persistent[Label] = na(Label)
        sessionStarted: bool = sessionActive and (not sessionActive[1])

        if sessionStarted:
            sessionStartTime = time
            sessionHigh = high
            sessionLow = low

            if drawRange:
                rangeBoxId = box.new(barNumber, sessionHigh, barNumber, sessionLow, bgcolor=color.new(sessionColor, rangeTransparencyInput), border_color=sessionColor if showRangeOutlineInput else na, border_style=line.style_dotted)

                if showRangeLabelInput:
                    rangeLabelId = label.new(sessionStartTime, sessionHigh, sessionName, xloc=xloc.bar_time, textcolor=sessionColor, style=label.style_label_down, color=color.new('#00000000'), size=size.tiny)
        elif sessionActive:
            sessionHigh = math.max(high, sessionHigh)
            sessionLow = math.min(low, sessionLow)

            if drawRange and (not na(rangeBoxId)):
                box.set_top(rangeBoxId, sessionHigh)
                box.set_rightbottom(rangeBoxId, barNumber, sessionLow)

                if showRangeLabelInput and (not na(rangeLabelId)):
                    label.set_xy(rangeLabelId, cast_int(math.avg(sessionStartTime, time)), sessionHigh)

        return (na if sessionActive else sessionHigh, na if sessionActive else sessionLow)

    sessionAActive: Series[bool] = not na(time(timeframe.period, sessionATimeInput, sessionTimezone))
    sessionBActive: Series[bool] = not na(time(timeframe.period, sessionBTimeInput, sessionTimezone))
    sessionCActive: Series[bool] = not na(time(timeframe.period, sessionCTimeInput, sessionTimezone))
    sessionDActive: Series[bool] = not na(time(timeframe.period, sessionDTimeInput, sessionTimezone))

    dashboardColumnCount: int = 5 if advancedDashboardInput else 2
    dashboardLastColumn: int = dashboardColumnCount - 1
    dashboardTable: Persistent[Table] = table.new(parsedDashboardPosition, dashboardColumnCount, 7, bgcolor=BACKGROUND, border_width=0, frame_color=BORDERS, frame_width=1, force_overlay=True)

    if barstate.isfirst and dashboardInput:
        table.merge_cells(dashboardTable, 0, 0, dashboardLastColumn, 0)
        cell(dashboardTable, 0, 0, 'Sessions [LuxAlgo]', textColor=DATA, alignment=text.align_center)
        divider(dashboardTable, 1, dashboardLastColumn)
        cell(dashboardTable, 0, 2, 'Session', textColor=HEADERS, alignment=text.align_left)
        cell(dashboardTable, 1, 2, 'Status', textColor=HEADERS)

        if advancedDashboardInput:
            cell(dashboardTable, 2, 2, 'Trend', textColor=HEADERS)
            cell(dashboardTable, 3, 2, 'Volume', textColor=HEADERS)
            cell(dashboardTable, 4, 2, 'σ', textColor=HEADERS)

        cell(dashboardTable, 0, 3, sessionANameInput, textColor=sessionAColorInput, alignment=text.align_left)
        cell(dashboardTable, 0, 4, sessionBNameInput, textColor=sessionBColorInput, alignment=text.align_left)
        cell(dashboardTable, 0, 5, sessionCNameInput, textColor=sessionCColorInput, alignment=text.align_left)
        cell(dashboardTable, 0, 6, sessionDNameInput, textColor=sessionDColorInput, alignment=text.align_left)

    if barstate.islast and dashboardInput:
        sessionAStatus: str = ('Active' if sessionAActive else 'Inactive') if showSessionAInput else 'Disabled'
        sessionBStatus: str = ('Active' if sessionBActive else 'Inactive') if showSessionBInput else 'Disabled'
        sessionCStatus: str = ('Active' if sessionCActive else 'Inactive') if showSessionCInput else 'Disabled'
        sessionDStatus: str = ('Active' if sessionDActive else 'Inactive') if showSessionDInput else 'Disabled'

        sessionAStatusColor: Color = (BULL_COLOR if sessionAActive else BEAR_COLOR) if showSessionAInput else HEADERS
        sessionBStatusColor: Color = (BULL_COLOR if sessionBActive else BEAR_COLOR) if showSessionBInput else HEADERS
        sessionCStatusColor: Color = (BULL_COLOR if sessionCActive else BEAR_COLOR) if showSessionCInput else HEADERS
        sessionDStatusColor: Color = (BULL_COLOR if sessionDActive else BEAR_COLOR) if showSessionDInput else HEADERS

        cell(dashboardTable, 1, 3, sessionAStatus, textColor=DATA, background=sessionAStatusColor)
        cell(dashboardTable, 1, 4, sessionBStatus, textColor=DATA, background=sessionBStatusColor)
        cell(dashboardTable, 1, 5, sessionCStatus, textColor=DATA, background=sessionCStatusColor)
        cell(dashboardTable, 1, 6, sessionDStatus, textColor=DATA, background=sessionDStatusColor)

    sessionAMaximum: Persistent[float] = na(float)
    sessionAMinimum: Persistent[float] = na(float)
    sessionBMaximum: Persistent[float] = na(float)
    sessionBMinimum: Persistent[float] = na(float)
    sessionCMaximum: Persistent[float] = na(float)
    sessionCMinimum: Persistent[float] = na(float)
    sessionDMaximum: Persistent[float] = na(float)
    sessionDMinimum: Persistent[float] = na(float)

    if showSessionAInput and (sessionARangeInput or sessionAMaxMinInput):
        sessionMaximum, sessionMinimum = getSessionRange(sessionAActive, sessionANameInput, sessionAColorInput, sessionARangeInput)
        sessionAMaximum = sessionMaximum
        sessionAMinimum = sessionMinimum

    if showSessionBInput and (sessionBRangeInput or sessionBMaxMinInput):
        sessionMaximum, sessionMinimum = getSessionRange(sessionBActive, sessionBNameInput, sessionBColorInput, sessionBRangeInput)
        sessionBMaximum = sessionMaximum
        sessionBMinimum = sessionMinimum

    if showSessionCInput and (sessionCRangeInput or sessionCMaxMinInput):
        sessionMaximum, sessionMinimum = getSessionRange(sessionCActive, sessionCNameInput, sessionCColorInput, sessionCRangeInput)
        sessionCMaximum = sessionMaximum
        sessionCMinimum = sessionMinimum

    if showSessionDInput and (sessionDRangeInput or sessionDMaxMinInput):
        sessionMaximum, sessionMinimum = getSessionRange(sessionDActive, sessionDNameInput, sessionDColorInput, sessionDRangeInput)
        sessionDMaximum = sessionMaximum
        sessionDMinimum = sessionMinimum

    calculateAdvancedDashboard: bool = dashboardInput and advancedDashboardInput

    if showSessionAInput and (sessionATrendlineInput or calculateAdvancedDashboard):
        firstValue, lastValue, deviation, correlation = getSessionLinearRegression(sessionAActive)

        if calculateAdvancedDashboard:
            trendColor: Color = na if na(correlation) else BULL_COLOR if correlation >= 0.0 else BEAR_COLOR
            cell(dashboardTable, 2, 3, string.tostring(correlation, '#.##'), textColor=DATA, background=trendColor)
            cell(dashboardTable, 4, 3, string.tostring(deviation, '#.####'), textColor=DATA)

        if sessionATrendlineInput:
            setSessionLine(sessionAActive, firstValue, lastValue, sessionAColorInput)

    if showSessionBInput and (sessionBTrendlineInput or calculateAdvancedDashboard):
        firstValue, lastValue, deviation, correlation = getSessionLinearRegression(sessionBActive)

        if calculateAdvancedDashboard:
            trendColor: Color = na if na(correlation) else BULL_COLOR if correlation >= 0.0 else BEAR_COLOR
            cell(dashboardTable, 2, 4, string.tostring(correlation, '#.##'), textColor=DATA, background=trendColor)
            cell(dashboardTable, 4, 4, string.tostring(deviation, '#.####'), textColor=DATA)

        if sessionBTrendlineInput:
            setSessionLine(sessionBActive, firstValue, lastValue, sessionBColorInput)

    if showSessionCInput and (sessionCTrendlineInput or calculateAdvancedDashboard):
        firstValue, lastValue, deviation, correlation = getSessionLinearRegression(sessionCActive)

        if calculateAdvancedDashboard:
            trendColor: Color = na if na(correlation) else BULL_COLOR if correlation >= 0.0 else BEAR_COLOR
            cell(dashboardTable, 2, 5, string.tostring(correlation, '#.##'), textColor=DATA, background=trendColor)
            cell(dashboardTable, 4, 5, string.tostring(deviation, '#.####'), textColor=DATA)

        if sessionCTrendlineInput:
            setSessionLine(sessionCActive, firstValue, lastValue, sessionCColorInput)

    if showSessionDInput and (sessionDTrendlineInput or calculateAdvancedDashboard):
        firstValue, lastValue, deviation, correlation = getSessionLinearRegression(sessionDActive)

        if calculateAdvancedDashboard:
            trendColor: Color = na if na(correlation) else BULL_COLOR if correlation >= 0.0 else BEAR_COLOR
            cell(dashboardTable, 2, 6, string.tostring(correlation, '#.##'), textColor=DATA, background=trendColor)
            cell(dashboardTable, 4, 6, string.tostring(deviation, '#.####'), textColor=DATA)

        if sessionDTrendlineInput:
            setSessionLine(sessionDActive, firstValue, lastValue, sessionDColorInput)

    if showSessionAInput and sessionAMeanInput:
        sessionAverage: float = getSessionAverage(sessionAActive)
        setSessionLine(sessionAActive, sessionAverage, sessionAverage, sessionAColorInput)

    if showSessionBInput and sessionBMeanInput:
        sessionAverage: float = getSessionAverage(sessionBActive)
        setSessionLine(sessionBActive, sessionAverage, sessionAverage, sessionBColorInput)

    if showSessionCInput and sessionCMeanInput:
        sessionAverage: float = getSessionAverage(sessionCActive)
        setSessionLine(sessionCActive, sessionAverage, sessionAverage, sessionCColorInput)

    if showSessionDInput and sessionDMeanInput:
        sessionAverage: float = getSessionAverage(sessionDActive)
        setSessionLine(sessionDActive, sessionAverage, sessionAverage, sessionDColorInput)

    sessionAVwap: Persistent[float] = na(float)
    sessionBVwap: Persistent[float] = na(float)
    sessionCVwap: Persistent[float] = na(float)
    sessionDVwap: Persistent[float] = na(float)

    if showSessionAInput and (sessionAVwapInput or calculateAdvancedDashboard):
        numerator, denominator = getSessionVwap(sessionAActive)

        if sessionAVwapInput:
            sessionAVwap = numerator / denominator if denominator != 0.0 else na

        if calculateAdvancedDashboard:
            cell(dashboardTable, 3, 3, string.tostring(denominator, format.volume), textColor=DATA)

    if showSessionBInput and (sessionBVwapInput or calculateAdvancedDashboard):
        numerator, denominator = getSessionVwap(sessionBActive)

        if sessionBVwapInput:
            sessionBVwap = numerator / denominator if denominator != 0.0 else na

        if calculateAdvancedDashboard:
            cell(dashboardTable, 3, 4, string.tostring(denominator, format.volume), textColor=DATA)

    if showSessionCInput and (sessionCVwapInput or calculateAdvancedDashboard):
        numerator, denominator = getSessionVwap(sessionCActive)

        if sessionCVwapInput:
            sessionCVwap = numerator / denominator if denominator != 0.0 else na

        if calculateAdvancedDashboard:
            cell(dashboardTable, 3, 5, string.tostring(denominator, format.volume), textColor=DATA)

    if showSessionDInput and (sessionDVwapInput or calculateAdvancedDashboard):
        numerator, denominator = getSessionVwap(sessionDActive)

        if sessionDVwapInput:
            sessionDVwap = numerator / denominator if denominator != 0.0 else na

        if calculateAdvancedDashboard:
            cell(dashboardTable, 3, 6, string.tostring(denominator, format.volume), textColor=DATA)

    plot(sessionAMaximum if showSessionAInput and sessionAMaxMinInput else na, 'Session A Maximum', sessionAColorInput, 1, plot.style_linebr)
    plot(sessionAMinimum if showSessionAInput and sessionAMaxMinInput else na, 'Session A Minimum', sessionAColorInput, 1, plot.style_linebr)
    plot(sessionBMaximum if showSessionBInput and sessionBMaxMinInput else na, 'Session B Maximum', sessionBColorInput, 1, plot.style_linebr)
    plot(sessionBMinimum if showSessionBInput and sessionBMaxMinInput else na, 'Session B Minimum', sessionBColorInput, 1, plot.style_linebr)
    plot(sessionCMaximum if showSessionCInput and sessionCMaxMinInput else na, 'Session C Maximum', sessionCColorInput, 1, plot.style_linebr)
    plot(sessionCMinimum if showSessionCInput and sessionCMaxMinInput else na, 'Session C Minimum', sessionCColorInput, 1, plot.style_linebr)
    plot(sessionDMaximum if showSessionDInput and sessionDMaxMinInput else na, 'Session D Maximum', sessionDColorInput, 1, plot.style_linebr)
    plot(sessionDMinimum if showSessionDInput and sessionDMaxMinInput else na, 'Session D Minimum', sessionDColorInput, 1, plot.style_linebr)

    plot(sessionAVwap if sessionAVwapInput else na, 'Session A VWAP', sessionAColorInput, 1, plot.style_linebr)
    plot(sessionBVwap if sessionBVwapInput else na, 'Session B VWAP', sessionBColorInput, 1, plot.style_linebr)
    plot(sessionCVwap if sessionCVwapInput else na, 'Session C VWAP', sessionCColorInput, 1, plot.style_linebr)
    plot(sessionDVwap if sessionDVwapInput else na, 'Session D VWAP', sessionDColorInput, 1, plot.style_linebr)

    plotshape(sessionAActive and showSessionDividerInput and showSessionAInput, title='Session A Active', style=shape.square, location=location.bottom, color=na, text='.', textcolor=sessionAColorInput, size=size.tiny, display=display.all - display.status_line, editable=False)
    plotshape(sessionAActive != sessionAActive[1] and showSessionDividerInput and showSessionAInput, title='Session A Boundary', style=shape.labelup, location=location.bottom, color=na, text='❚', textcolor=sessionAColorInput, size=size.tiny, display=display.all - display.status_line, editable=False)

    plotshape(sessionBActive and showSessionDividerInput and showSessionBInput, title='Session B Active', style=shape.labelup, location=location.bottom, color=na, text='.', textcolor=sessionBColorInput, size=size.tiny, display=display.all - display.status_line, editable=False)
    plotshape(sessionBActive != sessionBActive[1] and showSessionDividerInput and showSessionBInput, title='Session B Boundary', style=shape.labelup, location=location.bottom, color=na, text='❚', textcolor=sessionBColorInput, size=size.tiny, display=display.all - display.status_line, editable=False)

    plotshape(sessionCActive and showSessionDividerInput and showSessionCInput, title='Session C Active', style=shape.square, location=location.bottom, color=na, text='.', textcolor=sessionCColorInput, size=size.tiny, display=display.all - display.status_line, editable=False)
    plotshape(sessionCActive != sessionCActive[1] and showSessionDividerInput and showSessionCInput, title='Session C Boundary', style=shape.labelup, location=location.bottom, color=na, text='❚', textcolor=sessionCColorInput, size=size.tiny, display=display.all - display.status_line, editable=False)

    plotshape(sessionDActive and showSessionDividerInput and showSessionDInput, title='Session D Active', style=shape.labelup, location=location.bottom, color=na, text='.', textcolor=sessionDColorInput, size=size.tiny, display=display.all - display.status_line, editable=False)
    plotshape(sessionDActive != sessionDActive[1] and showSessionDividerInput and showSessionDInput, title='Session D Boundary', style=shape.labelup, location=location.bottom, color=na, text='❚', textcolor=sessionDColorInput, size=size.tiny, display=display.all - display.status_line, editable=False)

    currentDay: Series[int] = dayofweek
    newDay: bool = currentDay != currentDay[1]

    if newDay and showDayDividerInput:
        line.new(barNumber, close + syminfo.mintick, barNumber, close - syminfo.mintick, color=color.gray, extend=extend.both, style=line.style_dashed)

    plotshape(newDay and currentDay == dayofweek.sunday and showDayDividerInput, title='Sunday', style=shape.labeldown, location=location.top, color=na, text='Sunday', textcolor=color.gray, size=size.tiny, display=display.all - display.status_line, editable=False)
    plotshape(newDay and currentDay == dayofweek.monday and showDayDividerInput, title='Monday', style=shape.labeldown, location=location.top, color=na, text='Monday', textcolor=color.gray, size=size.tiny, display=display.all - display.status_line, editable=False)
    plotshape(newDay and currentDay == dayofweek.tuesday and showDayDividerInput, title='Tuesday', style=shape.labeldown, location=location.top, color=na, text='Tuesday', textcolor=color.gray, size=size.tiny, display=display.all - display.status_line, editable=False)
    plotshape(newDay and currentDay == dayofweek.wednesday and showDayDividerInput, title='Wednesday', style=shape.labeldown, location=location.top, color=na, text='Wednesday', textcolor=color.gray, size=size.tiny, display=display.all - display.status_line, editable=False)
    plotshape(newDay and currentDay == dayofweek.thursday and showDayDividerInput, title='Thursday', style=shape.labeldown, location=location.top, color=na, text='Thursday', textcolor=color.gray, size=size.tiny, display=display.all - display.status_line, editable=False)
    plotshape(newDay and currentDay == dayofweek.friday and showDayDividerInput, title='Friday', style=shape.labeldown, location=location.top, color=na, text='Friday', textcolor=color.gray, size=size.tiny, display=display.all - display.status_line, editable=False)
    plotshape(newDay and currentDay == dayofweek.saturday and showDayDividerInput, title='Saturday', style=shape.labeldown, location=location.top, color=na, text='Saturday', textcolor=color.gray, size=size.tiny, display=display.all - display.status_line, editable=False)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
