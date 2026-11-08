"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, barstate, chart, close, color, fill, high, input, label, line,
    low, math, na, open, plot, position, request, script, session, size, string, ta, table, text,
    time, time_close, timeframe, xloc, yloc
)
from pynecore.types import Color, Label, Line, NA, Persistent, Table


@udt
class session__ren__:
    startTime: int = na(int)
    endTime: int = na(int)
    openPrice: float = na(float)
    closePrice: float = na(float)
    top: float = na(float)
    bottom: float = na(float)
    labelTop: float = na(float)
    labelBottom: float = na(float)
    timeClose: int = na(int)
    tag: Label = na(Label)
    topLine: Line = na(Line)
    bottomLine: Line = na(Line)


@udt
class streak:
    bias: str = na(str)
    number: int = na(int)


GREEN: Color = color.new('#089981')
RED: Color = color.new('#F23645')
HORIZONTAL: str = 'Horizontal'
VERTICAL: str = 'Vertical'
TOP_RIGHT: str = 'Top Right'
BOTTOM_RIGHT: str = 'Bottom Right'
BOTTOM_LEFT: str = 'Bottom Left'
TINY: str = 'Tiny'
SMALL: str = 'Small'
NORMAL: str = 'Normal'
LARGE: str = 'Large'
HUGE: str = 'Huge'
DASHBOARD_GROUP: str = 'Dashboard'
STYLE_GROUP: str = 'Style'
dashboardTooltip: str = 'Enable or disable the dashboard.'
dashboardPositionTooltip: str = 'Select the dashboard location.'
dashboardSizeTooltip: str = 'Select the dashboard size.'


@script.indicator('Session Streaks [LuxAlgo]', 'LuxAlgo - Session Streaks', overlay=True, max_lines_count=500, max_labels_count=500, behind_chart=False)
def main(
    dashboardInput=input.bool(False, 'Dashboard', group=DASHBOARD_GROUP, tooltip=dashboardTooltip),
    dashboardPositionInput=input.string(TOP_RIGHT, 'Position', group=DASHBOARD_GROUP, tooltip=dashboardPositionTooltip, options=(TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT)),
    dashboardSizeInput=input.string(NORMAL, 'Size', group=DASHBOARD_GROUP, tooltip=dashboardSizeTooltip, options=(TINY, SMALL, NORMAL, LARGE, HUGE)),
    bullishColorInput=input.color(GREEN, 'Bullish', group=STYLE_GROUP),
    bearishColorInput=input.color(RED, 'Bearish', group=STYLE_GROUP),
    transparencyInput=input.int(80, 'Transparency', group=STYLE_GROUP),
    gradientTypeInput=input.string(HORIZONTAL, 'Gradient', group=STYLE_GROUP, options=(HORIZONTAL, VERTICAL))
):
    BULLISH: str = 'Bullish'
    BEARISH: str = 'Bearish'





    sessions: Persistent[list[session__ren__]] = array.new(0, NA(session__ren__))
    bullishStreaks: Persistent[list[int]] = array.new_int()
    bearishStreaks: Persistent[list[int]] = array.new_int()
    currentStreak: Persistent[streak] = streak('', 0)
    sessionStart: bool = session.isfirstbar_regular
    largerThanDailyTimeframe: bool = timeframe.in_seconds() > 86400

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

    t_able: Persistent[Table] = table.new(parsedDashboardPosition, 3, 12, bgcolor=color.new('#1E222D'), border_color=color.new('#373A46'), border_width=1, frame_color=color.new('#373A46'), frame_width=1)

    def gatherStatistics():
        wasLastBullish: Persistent[bool] = True

        __block_result_2__ = na
        if array.size(sessions) > 0:
            currentSession: session__ren__ = array.last(sessions)
            bullishSession: bool = currentSession.closePrice >= currentSession.openPrice

            if bullishSession:
                if array.size(bullishStreaks) != 0 and wasLastBullish:
                    array.set(bullishStreaks, -1, array.get(bullishStreaks, -1) + 1)
                else:
                    array.push(bullishStreaks, 1)
            else:
                if array.size(bearishStreaks) != 0 and (not wasLastBullish):
                    array.set(bearishStreaks, -1, array.get(bearishStreaks, -1) + 1)
                else:
                    array.push(bearishStreaks, 1)

            wasLastBullish = bullishSession
            __block_result_2__ = wasLastBullish
        return __block_result_2__

    def gatherData():
        if sessionStart:
            gatherStatistics()

            if array.size(sessions) > 500:
                array.shift(sessions)

            array.push(sessions, session__ren__(time, time, open, close, high, low))

        __block_result_3__ = na
        if array.size(sessions) > 0:
            currentSession: session__ren__ = array.last(sessions)
            currentSession.endTime = time
            currentSession.closePrice = close
            currentSession.top = math.max(currentSession.top, high)
            currentSession.bottom = math.min(currentSession.bottom, low)
            currentSession.labelTop = currentSession.top
            currentSession.labelBottom = currentSession.bottom
            __block_result_3__ = currentSession.labelBottom
        return __block_result_3__

    def getHTFSession():
        return session__ren__(time, time, open, close, high, low, time_close)

    def gatherDataHTF():
        gatherStatistics()

        if array.size(sessions) > 500:
            array.shift(sessions)

        lastSession: session__ren__ = request.security('', 'D', getHTFSession())
        lastSession.startTime = time
        lastSession.endTime = time
        lastSession.labelTop = high
        lastSession.labelBottom = low
        return array.push(sessions, lastSession)

    def cell(t_able: Table, column: int, row: int, data: str, color__ren__ = color.white, align = text.align_right):
        return table.cell(t_able, column, row, data, text_color=color__ren__, text_size=parsedDashboardSize, text_halign=align)

    def cellBG(t_able: Table, column: int, row: int, data: str, background: Color, color__ren__ = color.white, align = text.align_right):
        return table.cell(t_able, column, row, data, text_color=color__ren__, text_size=parsedDashboardSize, text_halign=align, bgcolor=background)

    def updateDashboard():
        currentColor: Color = (bullishColorInput if array.last(sessions).closePrice >= array.last(sessions).openPrice else bearishColorInput) if array.size(sessions) > 0 else NA(Color)
        currentTag: str = method_call('get_text', array.last(sessions).tag) if array.size(sessions) > 0 else ''
        return cellBG(t_able, 1, 0, currentTag, color.new(currentColor, transparencyInput), currentColor, align=text.align_center)

    def drawDashboard():
        table.merge_cells(t_able, 1, 0, 2, 0)
        cell(t_able, 0, 0, 'Current', align=text.align_center)

        table.merge_cells(t_able, 0, 1, 2, 1)
        cell(t_able, 0, 1, 'Streaks', align=text.align_center)
        cell(t_able, 1, 2, 'Bullish', align=text.align_center)
        cell(t_able, 2, 2, 'Bearish', align=text.align_center)
        cell(t_able, 0, 3, 'Number', align=text.align_left)
        cell(t_able, 0, 4, 'Median', align=text.align_left)
        cell(t_able, 0, 5, 'Mode', align=text.align_left)

        updateDashboard()

        parsedBullishStreaks: list[int] = array.new_int()
        for eachStreak in bullishStreaks:
            if eachStreak > 1:
                array.push(parsedBullishStreaks, eachStreak)

        parsedBearishStreaks: list[int] = array.new_int()
        for eachStreak in bearishStreaks:
            if eachStreak > 1:
                array.push(parsedBearishStreaks, eachStreak)

        cell(t_able, 1, 3, string.format('{0, number, 0}', array.size(parsedBullishStreaks)))
        cell(t_able, 2, 3, string.format('{0, number, 0}', array.size(parsedBearishStreaks)))
        cell(t_able, 1, 4, string.format('{0, number, 0.00}', array.median(parsedBullishStreaks)))
        cell(t_able, 2, 4, string.format('{0, number, 0.00}', array.median(parsedBearishStreaks)))
        cell(t_able, 1, 5, string.format('{0, number, 0.00}', array.mode(parsedBullishStreaks)))
        return cell(t_able, 2, 5, string.format('{0, number, 0.00}', array.mode(parsedBearishStreaks)))

    def drawSession(currentSession: session__ren__):
        bullishArea: bool = currentSession.closePrice >= currentSession.openPrice

        if bullishArea:
            if currentStreak.bias == BULLISH:
                currentStreak.number += 1
            else:
                currentStreak.bias = BULLISH
                currentStreak.number = 1
        else:
            if currentStreak.bias == BEARISH:
                currentStreak.number += 1
            else:
                currentStreak.bias = BEARISH
                currentStreak.number = 1

        currentTag: str = currentStreak.bias + ' (' + string.tostring(currentStreak.number) + ')'
        currentColor: Color = bullishColorInput if bullishArea else bearishColorInput

        label.delete(currentSession.tag)
        line.delete(currentSession.topLine)
        line.delete(currentSession.bottomLine)
        currentSession.tag = label.new(chart.point.new(currentSession.startTime + math.round(0.5 * (currentSession.endTime - currentSession.startTime)), na, currentSession.labelBottom if bullishArea else currentSession.labelTop), currentTag, xloc.bar_time, yloc.price, NA(Color), label.style_label_up if bullishArea else label.style_label_down, currentColor, size.normal)
        currentSession.topLine = line.new(chart.point.new(currentSession.startTime, na, currentSession.top), chart.point.new(currentSession.endTime, na, currentSession.top), xloc.bar_time, color=color.new(currentColor, 50))
        currentSession.bottomLine = line.new(chart.point.new(currentSession.startTime, na, currentSession.bottom), chart.point.new(currentSession.endTime, na, currentSession.bottom), xloc.bar_time, color=color.new(currentColor, 50))
        return currentSession.bottomLine

    def drawSessions():
        __block_result_4__ = na
        for eachSession in sessions:
            __block_result_4__ = drawSession(eachSession)
        return __block_result_4__

    if timeframe.isintraday:
        gatherData()
    else:
        gatherDataHTF()

    if barstate.islastconfirmedhistory:
        drawSessions()

        if dashboardInput:
            drawDashboard()

    if barstate.islast:
        if timeframe.isintraday:
            currentStreak.number -= 1

        drawSession(array.last(sessions))

        if dashboardInput:
            updateDashboard()

    existingSessions: bool = array.size(sessions) > 0
    topLevel: float = array.last(sessions).top if existingSessions else na
    bottomLevel: float = array.last(sessions).bottom if existingSessions else na
    fillColor: Color = (na if sessionStart else bullishColorInput if array.last(sessions).closePrice >= array.last(sessions).openPrice else bearishColorInput) if existingSessions else NA(Color)
    delta: float = close - array.last(sessions).openPrice if existingSessions else na
    smooth: float = ta.sma(math.sign(delta), 10)
    smoothGradient: Color = color.from_gradient(smooth, -1, 1, color.new(bearishColorInput, transparencyInput), color.new(bullishColorInput, transparencyInput))

    topPlot = plot(topLevel, 'Top', color.new(fillColor, transparencyInput), style=plot.style_linebr)
    bottomPlot = plot(bottomLevel, 'Bottom', color.new(fillColor, transparencyInput), style=plot.style_linebr)

    fill(topPlot, bottomPlot, smoothGradient if gradientTypeInput == VERTICAL else NA(Color))
    fill(topPlot, bottomPlot, topLevel, bottomLevel, color.new(bullishColorInput, transparencyInput) if gradientTypeInput == HORIZONTAL else NA(Color), color.new(bearishColorInput, transparencyInput) if gradientTypeInput == HORIZONTAL else NA(Color))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
