"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, bgcolor, box, chart, close,
    color, fill, high, input, label, low, map, math, na, nz, open, plot, position, script, size,
    string, syminfo, ta, table, text, time, timeframe, volume
)
from pynecore.types import Box, Color, Persistent, PersistentSeries, Series, Table

TOP_RIGHT: str = 'Top Right'
BOTTOM_RIGHT: str = 'Bottom Right'
BOTTOM_LEFT: str = 'Bottom Left'
TINY: str = 'Tiny'
SMALL: str = 'Small'
NORMAL: str = 'Normal'
LARGE: str = 'Large'
HUGE: str = 'Huge'
DASHBOARD_GROUP: str = 'Dashboard'
dashboardTooltip: str = 'Enable or disable the dashboard.'
dashboardPositionTooltip: str = 'Select the dashboard location.'
dashboardSizeTooltip: str = 'Select the dashboard size.'


@script.indicator("Ultimate Opening Range Breakout [LuxAlgo]", shorttitle="LuxAlgo - Ult ORB", overlay=True, max_labels_count=500, max_lines_count=500, max_boxes_count=500)
def main(
    sessionInput=input.session("0930-1000", "Opening Range Session", tooltip="Define the time range for the opening range calculation. Format: HHMM-HHMM"),
    sessionDays=input.string("1234567", "Days of Week", tooltip="Select days to apply the opening range (1=Sunday, 7=Saturday)"),
    timezoneInput=input.string("UTC-5", "Timezone", options=("UTC-12", "UTC-11", "UTC-10", "UTC-9", "UTC-8", "UTC-7", "UTC-6", "UTC-5", "UTC-4", "UTC-3", "UTC-2", "UTC-1", "UTC+0", "UTC+1", "UTC+2", "UTC+3", "UTC+4", "UTC+5", "UTC+6", "UTC+7", "UTC+8", "UTC+9", "UTC+10", "UTC+11", "UTC+12"), tooltip="Adjust the timezone for the session input."),
    srcInput=input.string("High/Low", "Range Source", options=("High/Low", "Close"), tooltip="Use the high/low of the session or the closing prices to define the range."),
    showExtensions=input.bool(True, "Show Extension Levels", group="Extensions"),
    extType=input.string("Multiples", "Extension Type", options=("Multiples", "Fibonacci"), group="Extensions"),
    mult1=input.float(1.0, "Multiplier 1", minval=0, group="Extensions"),
    mult2=input.float(2.0, "Multiplier 2", minval=0, group="Extensions"),
    mult3=input.float(3.0, "Multiplier 3", minval=0, group="Extensions"),
    bullColor=input.color(color.new('#089981'), "Bullish Color", group="Style", inline="Colors"),
    bearColor=input.color(color.new('#F23645'), "Bearish Color", group="Style", inline="Colors"),
    neutralColor=input.color(color.new('#5B9CF6'), "Range Color", group="Style", inline="Colors"),
    bgTransp=input.int(85, "Background Transparency", minval=0, maxval=100, group="Style"),
    showLabels=input.bool(True, "Show Level Labels", group="Style"),
    sigLabelSize=input.string("Small", "Signal Label Size", options=("Tiny", "Small", "Normal", "Large"), group="Style"),
    showVP=input.bool(True, "Show Volume Profile", group="Volume Profile"),
    vpRowsInput=input.int(14, "Number of Rows", minval=5, maxval=50, group="Volume Profile", tooltip="Number of blocks to divide the opening range into. Lower values make the profile more 'blocky'."),
    vpWidth=input.int(30, "Profile Width (%)", minval=1, maxval=100, group="Volume Profile", tooltip="Width of the volume profile relative to the session length."),
    vpColor=input.color(color.new(color.new('#5B9CF6'), 60), "Profile Color", group="Volume Profile"),
    stopPlotting=input.bool(True, "Limit Plotting Duration", group="Plotting Duration"),
    stopTimeType=input.string("New York Close", "End Plotting At", options=("New York Close", "London Close", "Manual Time", "End of Day"), group="Plotting Duration", tooltip="Choose when to stop drawing the levels on the chart."),
    manualEndTime=input.string("16:00", "Manual End Time (HH:MM)", group="Plotting Duration", tooltip="Format: HH:MM. Used if 'Manual Time' is selected."),
    showTrail=input.bool(False, "Show Trailing Stop", group="Trailing Stop"),
    trailMult=input.float(2.0, "ATR Multiplier", minval=0.1, step=0.1, group="Trailing Stop", tooltip="Multiplier for the ATR-based trailing stop."),
    trailAtrLen=input.int(14, "ATR Length", minval=1, group="Trailing Stop"),
    dashboardInput=input.bool(True, 'Show Hit Rate Dashboard', group=DASHBOARD_GROUP, tooltip=dashboardTooltip),
    showOptimizer=input.bool(False, 'Show Stop Optimizer', group=DASHBOARD_GROUP, tooltip="Simulates different ATR multipliers to find the most profitable distance."),
    dashboardPositionInput=input.string(TOP_RIGHT, 'Position', group=DASHBOARD_GROUP, tooltip=dashboardPositionTooltip, options=(TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT)),
    dashboardSizeInput=input.string(SMALL, 'Size', group=DASHBOARD_GROUP, tooltip=dashboardSizeTooltip, options=(TINY, SMALL, NORMAL, LARGE, HUGE))
):
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

    atrVal = ta.atr(200)
    dynamicTickSize: Persistent[float] = na(float)

    inSession: Series = not na(time(timeframe.period, sessionInput + ':' + sessionDays, timezoneInput))
    isNewDay = ta.change(time('D', '', timezoneInput)) != 0

    orHigh: Persistent[float] = na(float)
    orLow: Persistent[float] = na(float)
    sessionEnded: Persistent[bool] = False

    totalSessions: Persistent[int] = 0
    countU1: Persistent[int] = 0
    countU2: Persistent[int] = 0
    countU3: Persistent[int] = 0
    countD1: Persistent[int] = 0
    countD2: Persistent[int] = 0
    countD3: Persistent[int] = 0

    dayReachedU1: Persistent[bool] = False
    dayReachedU2: Persistent[bool] = False
    dayReachedU3: Persistent[bool] = False
    dayReachedD1: Persistent[bool] = False
    dayReachedD2: Persistent[bool] = False
    dayReachedD3: Persistent[bool] = False

    volMap: Persistent[dict[float, float]] = map.new()
    sessionStartBar: Persistent[int] = 0
    profileAnchor: Persistent[int] = 0
    activeVPBoxes: Persistent[list[Box]] = array.new_box()

    totalProfit: Persistent[float] = 0.0
    entryPrice: Persistent[float] = na(float)

    optProfits: Persistent[list[float]] = array.from_items(0.0, 0.0, 0.0, 0.0, 0.0)
    optMults: Persistent[list[float]] = array.from_items(1.0, 1.5, 2.0, 2.5, 3.0)
    optStops: Persistent[list[float]] = array.new_float(5, na)
    optActive: Persistent[list[int]] = array.new_int(5, 0)

    trailStop: PersistentSeries[float] = na(float)
    activeDir: Persistent[int] = 0

    canSignalUp: Persistent[bool] = True
    canSignalDn: Persistent[bool] = True

    def cell(t_able: Table, column: int, row: int, data: str, color__ren__ = color.new('#FFFFFF'), align = text.align_right, background: Color = na, height: float = 0):
        return table.cell(t_able, column, row, data, text_color=color__ren__, text_size=parsedDashboardSize, text_halign=align, bgcolor=background, height=height)

    def divider(t_able: Table, row: int, lastColumn: int):
        rowDivider: str = '━━━━━━━━━━━━━━'
        table.merge_cells(t_able, 0, row, lastColumn, row)
        return cell(t_able, 0, row, rowDivider, align=text.align_center, height=0.5, color__ren__=BORDERS)

    def getExt(multVal: float, rangeVal: float, highLvl: float, lowLvl: float):
        up: float = highLvl + rangeVal * multVal
        dn: float = lowLvl - rangeVal * multVal
        return (up, dn)

    if isNewDay or (inSession and (not inSession[1])):
        orHigh = na
        orLow = na
        sessionEnded = False
        dayReachedU1 = False
        dayReachedU2 = False
        dayReachedU3 = False
        dayReachedD1 = False
        dayReachedD2 = False
        dayReachedD3 = False
        map.clear(volMap)
        sessionStartBar = bar_index
        profileAnchor = bar_index
        array.clear(activeVPBoxes)
        entryPrice = na
        array.fill(optStops, na)
        array.fill(optActive, 0)
        dynamicTickSize = math.max(syminfo.mintick, nz(atrVal, high - low) / vpRowsInput)

    if inSession:
        currentHigh: float = high if srcInput == 'High/Low' else math.max(open, close)
        currentLow: float = low if srcInput == 'High/Low' else math.min(open, close)

        orHigh = currentHigh if na(orHigh) else math.max(orHigh, currentHigh)
        orLow = currentLow if na(orLow) else math.min(orLow, currentLow)
        profileAnchor = bar_index

        currentRange: float = orHigh - orLow
        if currentRange > 0:
            dynamicTickSize = math.max(syminfo.mintick, currentRange / vpRowsInput)

        priceLevel: float = math.round(close / dynamicTickSize) * dynamicTickSize
        map.put(volMap, priceLevel, (map.get(volMap, priceLevel) if map.contains(volMap, priceLevel) else 0) + volume)

    if not inSession and inSession[1]:
        sessionEnded = True
        totalSessions += 1

    orRange: float = orHigh - orLow

    f1: float = 0.382 if extType == 'Fibonacci' else mult1
    f2: float = 0.618 if extType == 'Fibonacci' else mult2
    f3: float = 1.0 if extType == 'Fibonacci' else mult3

    u1, d1 = getExt(f1, orRange, orHigh, orLow)
    u2, d2 = getExt(f2, orRange, orHigh, orLow)
    u3, d3 = getExt(f3, orRange, orHigh, orLow)

    if sessionEnded:
        if not na(u1) and high >= u1 and (not dayReachedU1):
            countU1 += 1
            dayReachedU1 = True
        if not na(u2) and high >= u2 and (not dayReachedU2):
            countU2 += 1
            dayReachedU2 = True
        if not na(u3) and high >= u3 and (not dayReachedU3):
            countU3 += 1
            dayReachedU3 = True

        if not na(d1) and low <= d1 and (not dayReachedD1):
            countD1 += 1
            dayReachedD1 = True
        if not na(d2) and low <= d2 and (not dayReachedD2):
            countD2 += 1
            dayReachedD2 = True
        if not na(d3) and low <= d3 and (not dayReachedD3):
            countD3 += 1
            dayReachedD3 = True

    orStartTime = string.substring(sessionInput, 0, 4)

    __block_result_2__ = na
    __switch__ = stopTimeType
    if __switch__ == "New York Close":
        __block_result_2__ = "1700"
    elif __switch__ == "London Close":
        __block_result_2__ = "1130"
    elif __switch__ == "Manual Time":
        __block_result_2__ = string.replace(manualEndTime, ':', '')
    else:
        __block_result_2__ = "2359"
    targetEndTime: str = __block_result_2__

    plottingSession = orStartTime + '-' + targetEndTime
    displayAllowed: bool = not stopPlotting or not na(time(timeframe.period, plottingSession + ':' + sessionDays, timezoneInput))

    plotHigh = orHigh if displayAllowed else na
    plotLow = orLow if displayAllowed else na
    plotU1 = u1 if displayAllowed and showExtensions else na
    plotU2 = u2 if displayAllowed and showExtensions else na
    plotU3 = u3 if displayAllowed and showExtensions else na
    plotD1 = d1 if displayAllowed and showExtensions else na
    plotD2 = d2 if displayAllowed and showExtensions else na
    plotD3 = d3 if displayAllowed and showExtensions else na

    atrTrail = ta.atr(trailAtrLen)

    volSMA = ta.sma(volume, 20)
    isHV = volume > volSMA
    volSuffix = ' (HV)' if isHV else ' (LV)'
    szSignal = size.tiny if sigLabelSize == 'Tiny' else size.small if sigLabelSize == 'Small' else size.normal if sigLabelSize == 'Normal' else size.large

    breakoutUp: bool = ta.crossover(close, orHigh) and (not inSession) and sessionEnded
    breakoutDn: bool = ta.crossunder(close, orLow) and (not inSession) and sessionEnded

    if isNewDay or inSession:
        canSignalUp = True
        canSignalDn = True
        activeDir = 0
        trailStop = na

    if breakoutUp and canSignalUp and displayAllowed:
        label.new(bar_index, high, 'BULL BREAK' + volSuffix, color=bullColor, style=label.style_label_down, textcolor=color.white, size=szSignal)
        canSignalUp = False
        if activeDir == 0:
            activeDir = 1
            entryPrice = orHigh
            trailStop = low - atrTrail * trailMult
            for i in pine_range(0, 4):
                array.set(optActive, i, 1)
                array.set(optStops, i, low - atrTrail * array.get(optMults, i))

    if breakoutDn and canSignalDn and displayAllowed:
        label.new(bar_index, low, 'BEAR BREAK' + volSuffix, color=bearColor, style=label.style_label_up, textcolor=color.white, size=szSignal)
        canSignalDn = False
        if activeDir == 0:
            activeDir = -1
            entryPrice = orLow
            trailStop = high + atrTrail * trailMult
            for i in pine_range(0, 4):
                array.set(optActive, i, -1)
                array.set(optStops, i, high + atrTrail * array.get(optMults, i))

    if activeDir == 1:
        trailStop = math.max(nz(trailStop[1], low - atrTrail * trailMult), low - atrTrail * trailMult)
        if close < trailStop or not displayAllowed:
            totalProfit += close - entryPrice
            activeDir = 0
            trailStop = na

    if activeDir == -1:
        trailStop = math.min(nz(trailStop[1], high + atrTrail * trailMult), high + atrTrail * trailMult)
        if close > trailStop or not displayAllowed:
            totalProfit += entryPrice - close
            activeDir = 0
            trailStop = na

    if showOptimizer:
        for i in pine_range(0, 4):
            m = array.get(optMults, i)
            a = array.get(optActive, i)
            s = array.get(optStops, i)
            if a == 1:
                newStop = math.max(nz(s, low - atrTrail * m), low - atrTrail * m)
                array.set(optStops, i, newStop)
                if close < newStop or not displayAllowed:
                    array.set(optProfits, i, array.get(optProfits, i) + (close - entryPrice))
                    array.set(optActive, i, 0)
            elif a == -1:
                newStop = math.min(nz(s, high + atrTrail * m), high + atrTrail * m)
                array.set(optStops, i, newStop)
                if close > newStop or not displayAllowed:
                    array.set(optProfits, i, array.get(optProfits, i) + (entryPrice - close))
                    array.set(optActive, i, 0)

    bgcolor(color.new(neutralColor, 90) if inSession else na, title='Session Background')

    pHigh = plot(plotHigh, 'OR High', color.new(neutralColor, 20), 2, plot.style_linebr)
    pLow = plot(plotLow, 'OR Low', color.new(neutralColor, 20), 2, plot.style_linebr)

    fill(pHigh, pLow, plotHigh, plotLow, color.new(neutralColor, bgTransp), color.new(neutralColor, bgTransp), 'Range Fill')

    pu1 = plot(plotU1, 'Upper Ext 1', color.new(bullColor, 40), 1, plot.style_linebr)
    pu2 = plot(plotU2, 'Upper Ext 2', color.new(bullColor, 40), 1, plot.style_linebr)
    pu3 = plot(plotU3, 'Upper Ext 3', color.new(bullColor, 40), 1, plot.style_linebr)

    pd1 = plot(plotD1, 'Lower Ext 1', color.new(bearColor, 40), 1, plot.style_linebr)
    pd2 = plot(plotD2, 'Lower Ext 2', color.new(bearColor, 40), 1, plot.style_linebr)
    pd3 = plot(plotD3, 'Lower Ext 3', color.new(bearColor, 40), 1, plot.style_linebr)

    fill(pHigh, pu1, plotU1, plotHigh, color.new(bullColor, bgTransp + 10), color.new(bullColor, bgTransp), 'Bull Zone 1')
    fill(pu1, pu2, plotU2, plotU1, color.new(bullColor, bgTransp + 5), color.new(bullColor, bgTransp + 10), 'Bull Zone 2')
    fill(pu2, pu3, plotU3, plotU2, color.new(bullColor, bgTransp), color.new(bullColor, bgTransp + 5), 'Bull Zone 3')

    fill(pLow, pd1, plotLow, plotD1, color.new(bearColor, bgTransp), color.new(bearColor, bgTransp + 10), 'Bear Zone 1')
    fill(pd1, pd2, plotD1, plotD2, color.new(bearColor, bgTransp + 10), color.new(bearColor, bgTransp + 5), 'Bear Zone 2')
    fill(pd2, pd3, plotD2, plotD3, color.new(bearColor, bgTransp + 5), color.new(bearColor, bgTransp), 'Bear Zone 3')

    pTrail = plot(trailStop if showTrail else na, 'Trailing Stop', bullColor if activeDir == 1 else bearColor, 2, plot.style_linebr)
    pPrice = plot(close if showTrail else na, 'Trail Price Ref', color.new(chart.fg_color, 100))
    fill(pTrail, pPrice, top_value=close if activeDir == 1 else trailStop, bottom_value=trailStop if activeDir == 1 else close, top_color=color.new(bullColor, 50) if activeDir == 1 else color.new(bearColor, 100), bottom_color=color.new(bullColor, 100) if activeDir == 1 else color.new(bearColor, 50), title='Trailing Stop Fill')

    if barstate.islast:
        if showVP and map.size(volMap) > 0:
            if array.size(activeVPBoxes) > 0:
                for b in activeVPBoxes:
                    box.delete(b)
                array.clear(activeVPBoxes)

            maxVol: float = 0.0
            prices: list[float] = map.keys(volMap)
            for p in prices:
                maxVol = math.max(maxVol, map.get(volMap, p))

            if array.size(prices) > 0:
                array.sort(prices)
                profileMaxBars: int = 15
                levelHeight: float = dynamicTickSize
                startX: int = bar_index + 25

                for i in pine_range(0, array.size(prices) - 1):
                    p: float = array.get(prices, i)
                    if p >= orLow - levelHeight / 2 and p <= orHigh + levelHeight / 2:
                        vol: float = map.get(volMap, p)
                        isPOC: bool = vol == maxVol
                        bars: int = math.max(1, math.round(vol / math.max(1e-10, maxVol) * profileMaxBars))
                        cellColor: Color = color.new(vpColor, 0) if isPOC else color.new(vpColor, 40)
                        nb: Box = box.new(startX, p + levelHeight / 2, startX + bars, p - levelHeight / 2, border_color=color.new(vpColor, 100), bgcolor=cellColor)
                        array.push(activeVPBoxes, nb)

        if showLabels:
            label.delete(inline_series(label.new(bar_index + 2, orHigh, 'OR High', color=neutralColor, style=label.style_label_left, textcolor=color.white, size=size.small), 1))
            label.delete(inline_series(label.new(bar_index + 2, orLow, 'OR Low', color=neutralColor, style=label.style_label_left, textcolor=color.white, size=size.small), 1))
            if showExtensions:
                lblU1: str = 'Target 1 (' + string.tostring(math.round(countU1 / totalSessions * 100) if totalSessions > 0 else 0) + '%)'
                lblD1: str = 'Target 1 (' + string.tostring(math.round(countD1 / totalSessions * 100) if totalSessions > 0 else 0) + '%)'
                lblU2: str = 'Target 2 (' + string.tostring(math.round(countU2 / totalSessions * 100) if totalSessions > 0 else 0) + '%)'
                lblD2: str = 'Target 2 (' + string.tostring(math.round(countD2 / totalSessions * 100) if totalSessions > 0 else 0) + '%)'
                lblU3: str = 'Target 3 (' + string.tostring(math.round(countU3 / totalSessions * 100) if totalSessions > 0 else 0) + '%)'
                lblD3: str = 'Target 3 (' + string.tostring(math.round(countD3 / totalSessions * 100) if totalSessions > 0 else 0) + '%)'

                label.delete(inline_series(label.new(bar_index + 2, u1, lblU1, color=bullColor, style=label.style_label_left, textcolor=color.white, size=size.small), 1))
                label.delete(inline_series(label.new(bar_index + 2, d1, lblD1, color=bearColor, style=label.style_label_left, textcolor=color.white, size=size.small), 1))
                label.delete(inline_series(label.new(bar_index + 2, u2, lblU2, color=bullColor, style=label.style_label_left, textcolor=color.white, size=size.small), 1))
                label.delete(inline_series(label.new(bar_index + 2, d2, lblD2, color=bearColor, style=label.style_label_left, textcolor=color.white, size=size.small), 1))
                label.delete(inline_series(label.new(bar_index + 2, u3, lblU3, color=bullColor, style=label.style_label_left, textcolor=color.white, size=size.small), 1))
                label.delete(inline_series(label.new(bar_index + 2, d3, lblD3, color=bearColor, style=label.style_label_left, textcolor=color.white, size=size.small), 1))

    if dashboardInput:
        rowsTotal: int = 13 + (2 if showTrail else 0) + (2 if showOptimizer else 0)
        dash: Persistent[Table] = table.new(parsedDashboardPosition, 4, rowsTotal, bgcolor=BACKGROUND, border_width=0, frame_color=BORDERS, frame_width=1, force_overlay=False)

        if barstate.isfirst:
            table.merge_cells(dash, 0, 0, 3, 0)
            cell(dash, 0, 0, 'ORB Hit Rate', color__ren__=DATA, align=text.align_center)

            divider(dash, 1, 3)

            cell(dash, 0, 2, 'Level', color__ren__=HEADERS, align=text.align_left)
            cell(dash, 1, 2, 'Hits', color__ren__=HEADERS)
            cell(dash, 2, 2, 'Total', color__ren__=HEADERS)
            cell(dash, 3, 2, 'Rate', color__ren__=HEADERS)

            divider(dash, 3, 3)
            divider(dash, 7, 3)
            divider(dash, 11, 3)

            table.merge_cells(dash, 0, 12, 3, 12)

            nextRow: int = 13
            if showTrail:
                divider(dash, nextRow, 3)
                nextRow += 1
                table.merge_cells(dash, 0, nextRow, 3, nextRow)
                nextRow += 1

            if showOptimizer:
                divider(dash, nextRow, 3)
                nextRow += 1
                table.merge_cells(dash, 0, nextRow, 3, nextRow)

        if barstate.islast:
            totalHits = math.max(1, totalSessions)

            cell(dash, 0, 4, 'Bull T1', color__ren__=HEADERS, align=text.align_left)
            cell(dash, 1, 4, string.tostring(countU1), color__ren__=bullColor)
            cell(dash, 2, 4, string.tostring(totalSessions), color__ren__=bullColor)
            cell(dash, 3, 4, string.tostring(math.round(countU1 / totalHits * 100)) + '%', color__ren__=bullColor)

            cell(dash, 0, 5, 'Bull T2', color__ren__=HEADERS, align=text.align_left)
            cell(dash, 1, 5, string.tostring(countU2), color__ren__=bullColor)
            cell(dash, 2, 5, string.tostring(totalSessions), color__ren__=bullColor)
            cell(dash, 3, 5, string.tostring(math.round(countU2 / totalHits * 100)) + '%', color__ren__=bullColor)

            cell(dash, 0, 6, 'Bull T3', color__ren__=HEADERS, align=text.align_left)
            cell(dash, 1, 6, string.tostring(countU3), color__ren__=bullColor)
            cell(dash, 2, 6, string.tostring(totalSessions), color__ren__=bullColor)
            cell(dash, 3, 6, string.tostring(math.round(countU3 / totalHits * 100)) + '%', color__ren__=bullColor)

            cell(dash, 0, 8, 'Bear T1', color__ren__=HEADERS, align=text.align_left)
            cell(dash, 1, 8, string.tostring(countD1), color__ren__=bearColor)
            cell(dash, 2, 8, string.tostring(totalSessions), color__ren__=bearColor)
            cell(dash, 3, 8, string.tostring(math.round(countD1 / totalHits * 100)) + '%', color__ren__=bearColor)

            cell(dash, 0, 9, 'Bear T2', color__ren__=HEADERS, align=text.align_left)
            cell(dash, 1, 9, string.tostring(countD2), color__ren__=bearColor)
            cell(dash, 2, 9, string.tostring(totalSessions), color__ren__=bearColor)
            cell(dash, 3, 9, string.tostring(math.round(countD2 / totalHits * 100)) + '%', color__ren__=bearColor)

            cell(dash, 0, 10, 'Bear T3', color__ren__=HEADERS, align=text.align_left)
            cell(dash, 1, 10, string.tostring(countD3), color__ren__=bearColor)
            cell(dash, 2, 10, string.tostring(totalSessions), color__ren__=bearColor)
            cell(dash, 3, 10, string.tostring(math.round(countD3 / totalHits * 100)) + '%', color__ren__=bearColor)

            cell(dash, 0, 12, 'Tracked: ' + string.tostring(totalSessions) + ' (' + sessionInput + ')', color__ren__=DATA, align=text.align_center)

            nextRow: int = 13
            if showTrail:
                nextRow += 1
                cell(dash, 0, nextRow, 'Cumulative Trail Profit: ' + string.tostring(totalProfit, '#.##'), color__ren__=DATA, align=text.align_center)
                nextRow += 1

            if showOptimizer:
                nextRow += 1
                bestIdx: int = 0
                maxP: float = -10000000000.0
                for i in pine_range(0, 4):
                    p = array.get(optProfits, i)
                    if p > maxP:
                        maxP = p
                        bestIdx = i
                bestMult = array.get(optMults, bestIdx)
                cell(dash, 0, nextRow, 'Best ATR Mult: ' + string.tostring(bestMult) + ' (Profit: ' + string.tostring(maxP, '#.##') + ')', color__ren__=color.new(color.new('#FFD700'), 0), align=text.align_center)

    alertcondition(breakoutUp, 'Bullish ORB', 'Price broke above the opening range.')
    alertcondition(breakoutDn, 'Bearish ORB', 'Price broke below the opening range.')
    alertcondition(ta.cross(close, u3), 'Target 3 Reached', 'Price reached the final bullish target.')
    alertcondition(ta.cross(close, d3), 'Target 3 Reached', 'Price reached the final bearish target.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
