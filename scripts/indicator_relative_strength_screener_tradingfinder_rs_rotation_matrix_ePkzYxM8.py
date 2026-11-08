"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barmerge, barstate, close,
    color, display, fill, hline, input, label, math, na, nz, order, plot, position, request,
    script, size, string, ta, table, text, time, timeframe
)
from pynecore.types import Color, Label, Persistent, Series, Table


@script.indicator("Relative Strength Screener [TradingFinder] RS Rotation Matrix", "RS Rotation", overlay=False, max_bars_back=5000, dynamic_requests=True)
def main(
    symbolLimitInput=input.int(10, "Number of Symbols", options=(2, 3, 4, 5, 6, 7, 8, 9, 10), group="Symbols"),
    symbol01=input.symbol("AMEX:XLK", "Symbol 1", group="Symbols"),
    symbol02=input.symbol("AMEX:XLF", "Symbol 2", group="Symbols"),
    symbol03=input.symbol("AMEX:XLE", "Symbol 3", group="Symbols"),
    symbol04=input.symbol("AMEX:XLV", "Symbol 4", group="Symbols"),
    symbol05=input.symbol("AMEX:XLY", "Symbol 5", group="Symbols"),
    symbol06=input.symbol("AMEX:XLP", "Symbol 6", group="Symbols"),
    symbol07=input.symbol("AMEX:XLI", "Symbol 7", group="Symbols"),
    symbol08=input.symbol("AMEX:XLB", "Symbol 8", group="Symbols"),
    symbol09=input.symbol("AMEX:XLU", "Symbol 9", group="Symbols"),
    symbol10=input.symbol("AMEX:XLRE", "Symbol 10", group="Symbols"),
    benchmarkInput=input.symbol("AMEX:SPY", "Benchmark", group="Calculation Settings"),
    scanTfInput=input.timeframe("D", "Scan Timeframe", tooltip="Can be above, equal to, or below the chart timeframe. Lower settings use intrabar data.", group="Calculation Settings"),
    rsLookbackInput=input.int(63, "Performance Length", minval=5, maxval=500, tooltip="Number of Scan Timeframe bars used to compare each symbol with the benchmark.", group="Calculation Settings"),
    momentumLookbackInput=input.int(21, "Momentum Length", minval=1, maxval=250, tooltip="Measures how benchmark-relative performance changed over this many Scan Timeframe bars.", group="Calculation Settings"),
    momentumWeightPctInput=input.float(35.0, "Momentum Weight %", minval=0.0, maxval=100.0, step=5.0, tooltip="The remaining weight is assigned to relative strength.", group="Calculation Settings"),
    persistenceThresholdInput=input.int(3, "Leadership Confirmation", minval=1, maxval=50, tooltip="Number of consecutive top-group checks required for Sustained Leadership.", group="Calculation Settings"),
    focusSymbolInput=input.symbol("AMEX:XLK", "Symbol", tooltip="Choose one of the active screener symbols. Otherwise, Symbol 1 is used.", group="Oscillator Settings"),
    oscLookbackInput=input.int(63, "Performance Length", minval=5, maxval=500, tooltip="Oscillator length in chart bars.", group="Oscillator Settings"),
    oscSmoothInput=input.int(5, "Smoothing", minval=1, maxval=50, group="Oscillator Settings"),
    oscSignalInput=input.int(13, "Signal Length", minval=2, maxval=100, group="Oscillator Settings"),
    oscShowSignalInput=input.bool(True, "Show Signal", group="Oscillator Settings"),
    oscShowLabelInput=input.bool(True, "Show Last Value", group="Oscillator Settings"),
    sendAlertsInput=input.bool(True, "Send Alerts", group="Alert Settings"),
    alertRankLevelInput=input.int(3, "Leader Rank", minval=1, maxval=10, tooltip="Alerts when a symbol enters or leaves this leader group.", group="Alert Settings"),
    showDashboardInput=input.bool(True, "Show Ranking Table", group="Table Settings"),
    dashboardSizeInput=input.string(size.small, "Ranking Table Size", options=(size.tiny, size.small, size.normal, size.large), group="Table Settings"),
    dashboardPositionInput=input.string(position.top_right, "Ranking Table Position", options=(position.top_left, position.top_center, position.top_right, position.middle_left, position.middle_center, position.middle_right, position.bottom_left, position.bottom_center, position.bottom_right), tooltip="Choose a different position from the Rotation Matrix to prevent overlap.", group="Table Settings"),
    showMatrixInput=input.bool(True, "Show Rotation Matrix", group="Table Settings"),
    matrixSizeInput=input.string(size.small, "Matrix Table Size", options=(size.tiny, size.small, size.normal, size.large), group="Table Settings"),
    matrixPositionInput=input.string(position.bottom_right, "Matrix Table Position", options=(position.top_left, position.top_center, position.top_right, position.middle_left, position.middle_center, position.middle_right, position.bottom_left, position.bottom_center, position.bottom_right), tooltip="Choose a different position from the Ranking Table to prevent overlap.", group="Table Settings")
):
    def f_shortSymbol(tickerId: str):
        parts = string.split(tickerId, ':')
        return array.get(parts, array.size(parts) - 1) if array.size(parts) > 1 else tickerId

    def f_timeframeLabel(timeframeValue):
        label__ren__ = timeframeValue
        if string.contains(timeframeValue, 'S'):
            amountS = string.replace_all(timeframeValue, 'S', '')
            label__ren__ = ('1' if amountS == '' else amountS) + 's'
        elif string.contains(timeframeValue, 'D'):
            amountD = string.replace_all(timeframeValue, 'D', '')
            label__ren__ = ('1' if amountD == '' else amountD) + 'D'
        elif string.contains(timeframeValue, 'W'):
            amountW = string.replace_all(timeframeValue, 'W', '')
            label__ren__ = ('1' if amountW == '' else amountW) + 'W'
        elif string.contains(timeframeValue, 'M'):
            amountM = string.replace_all(timeframeValue, 'M', '')
            label__ren__ = ('1' if amountM == '' else amountM) + 'M'
        else:
            totalSeconds: float = timeframe.in_seconds(timeframeValue)
            if not na(totalSeconds):
                totalMinutes: int = cast_int(totalSeconds / 60)
                label__ren__ = string.tostring(cast_int(totalMinutes / 1440)) + 'D' if totalMinutes >= 1440 and totalMinutes % 1440 == 0 else string.tostring(cast_int(totalMinutes / 60)) + 'h' if totalMinutes >= 60 and totalMinutes % 60 == 0 else string.tostring(totalMinutes) + 'm'
        return label__ren__

    def f_percentile(values: list[float], index: int):
        target: float = array.get(values, index)
        valid: int = 0
        below: int = 0
        tiedOthers: int = 0
        if not na(target):
            for j in pine_range(0, array.size(values) - 1):
                candidate: float = array.get(values, j)
                if not na(candidate):
                    valid += 1
                    if candidate < target:
                        below += 1
                    elif j != index and candidate == target:
                        tiedOthers += 1
        return (na if na(target) else 50.0) if valid <= 1 or na(target) else 100.0 * (below + 0.5 * tiedOthers) / (valid - 1)

    def f_ordinalRank(values: list[float], index: int):
        target: float = array.get(values, index)
        rank: int = na(int)
        if not na(target):
            rank = 1
            for j in pine_range(0, array.size(values) - 1):
                candidate: float = array.get(values, j)
                if not na(candidate) and candidate > target:
                    rank += 1
        return rank

    def f_state(strengthPct: float, momentumPct: float, strengthCut: float, momentumCut: float):
        state: str = "N/A"
        if not na(strengthPct) and (not na(momentumPct)):
            state = 'Leading' if strengthPct >= strengthCut and momentumPct >= momentumCut else 'Improving' if strengthPct < strengthCut and momentumPct >= momentumCut else 'Weakening' if strengthPct >= strengthCut and momentumPct < momentumCut else 'Lagging'
        return state

    def f_stateColor(state: str):
        return color.rgb(0, 145, 110) if state == 'Leading' else color.rgb(20, 105, 190) if state == 'Improving' else color.rgb(224, 145, 0) if state == 'Weakening' else color.rgb(185, 50, 65) if state == 'Lagging' else color.rgb(90, 95, 105)

    def f_lastFloat(values: list[float]):
        return array.last(values) if array.size(values) > 0 else na

    def f_lastInt(values: list[int]):
        return array.last(values) if array.size(values) > 0 else na

    def f_heatColor(value: float):
        return color.new(color.gray, 80) if na(value) else color.new(color.rgb(0, 145, 110), 15) if value >= 75 else color.new(color.rgb(85, 150, 95), 30) if value >= 50 else color.new(color.rgb(210, 145, 30), 30) if value >= 25 else color.new(color.rgb(185, 50, 65), 15)

    def f_appendEvent(message: str, eventText: str):
        return eventText if message == '' else message + '\n' + eventText

    symbols: Persistent[list[str]] = array.new_string()
    if barstate.isfirst:
        array.push(symbols, symbol01)
        array.push(symbols, symbol02)
        if symbolLimitInput >= 3:
            array.push(symbols, symbol03)
        if symbolLimitInput >= 4:
            array.push(symbols, symbol04)
        if symbolLimitInput >= 5:
            array.push(symbols, symbol05)
        if symbolLimitInput >= 6:
            array.push(symbols, symbol06)
        if symbolLimitInput >= 7:
            array.push(symbols, symbol07)
        if symbolLimitInput >= 8:
            array.push(symbols, symbol08)
        if symbolLimitInput >= 9:
            array.push(symbols, symbol09)
        if symbolLimitInput >= 10:
            array.push(symbols, symbol10)

    symbolCount = array.size(symbols)
    scanIsLower = timeframe.in_seconds(scanTfInput) < timeframe.in_seconds(timeframe.period)
    leaderCount = math.min(alertRankLevelInput, symbolCount)
    topQuartile = math.max(1, cast_int(math.ceil(symbolCount * 0.25)))
    momentumWeight = momentumWeightPctInput / 100.0
    strengthWeight = 1.0 - momentumWeight
    strengthCut: float = 50.0
    momentumCut: float = 50.0

    benchNow: float = na(float)
    benchPast: float = na(float)
    benchMom: float = na(float)
    benchMomPast: float = na(float)
    scanStamp: Series[int] = na(int)

    if scanIsLower:
        benchNowBars, benchPastBars, benchMomBars, benchMomPastBars, benchTimeBars = request.security_lower_tf(benchmarkInput, scanTfInput, (close, close[rsLookbackInput], close[momentumLookbackInput], close[rsLookbackInput + momentumLookbackInput], time), ignore_invalid_symbol=True, ignore_invalid_timeframe=True, calc_bars_count=5000)
        benchNow = f_lastFloat(benchNowBars)
        benchPast = f_lastFloat(benchPastBars)
        benchMom = f_lastFloat(benchMomBars)
        benchMomPast = f_lastFloat(benchMomPastBars)
        scanStamp = f_lastInt(benchTimeBars)
    else:
        benchNowHtf, benchPastHtf, benchMomHtf, benchMomPastHtf, benchTimeHtf = request.security(benchmarkInput, scanTfInput, (close[1], close[rsLookbackInput + 1], close[momentumLookbackInput + 1], close[rsLookbackInput + momentumLookbackInput + 1], time[1]), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on, ignore_invalid_symbol=True, calc_bars_count=5000)
        benchNow = benchNowHtf
        benchPast = benchPastHtf
        benchMom = benchMomHtf
        benchMomPast = benchMomPastHtf
        scanStamp = benchTimeHtf

    newScan: bool = not na(scanStamp) and (not scanIsLower or barstate.isconfirmed) and (na(scanStamp[1]) or scanStamp != scanStamp[1])

    relativeReturns: list[float] = array.new_float(symbolCount, na)
    relativeMomentum: list[float] = array.new_float(symbolCount, na)

    for i in pine_range(0, symbolCount - 1):
        symbolId: str = array.get(symbols, i)
        symbolNow: float = na(float)
        symbolPast: float = na(float)
        symbolMom: float = na(float)
        symbolMomPast: float = na(float)
        symbolStamp: int = na(int)
        if scanIsLower:
            symbolNowBars, symbolPastBars, symbolMomBars, symbolMomPastBars, symbolTimeBars = request.security_lower_tf(symbolId, scanTfInput, (close, close[rsLookbackInput], close[momentumLookbackInput], close[rsLookbackInput + momentumLookbackInput], time), ignore_invalid_symbol=True, ignore_invalid_timeframe=True, calc_bars_count=5000)
            symbolNow = f_lastFloat(symbolNowBars)
            symbolPast = f_lastFloat(symbolPastBars)
            symbolMom = f_lastFloat(symbolMomBars)
            symbolMomPast = f_lastFloat(symbolMomPastBars)
            symbolStamp = f_lastInt(symbolTimeBars)
        else:
            symbolNowHtf, symbolPastHtf, symbolMomHtf, symbolMomPastHtf, symbolTimeHtf = request.security(symbolId, scanTfInput, (close[1], close[rsLookbackInput + 1], close[momentumLookbackInput + 1], close[rsLookbackInput + momentumLookbackInput + 1], time[1]), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on, ignore_invalid_symbol=True, calc_bars_count=5000)
            symbolNow = symbolNowHtf
            symbolPast = symbolPastHtf
            symbolMom = symbolMomHtf
            symbolMomPast = symbolMomPastHtf
            symbolStamp = symbolTimeHtf

        timestampsMatch = not na(scanStamp) and symbolStamp == scanStamp
        validNow = timestampsMatch and (not na(symbolNow)) and (not na(symbolPast)) and (not na(benchNow)) and (not na(benchPast)) and (symbolPast != 0) and (benchPast != 0) and (benchNow != 0)
        validPrevious = timestampsMatch and (not na(symbolMom)) and (not na(symbolMomPast)) and (not na(benchMom)) and (not na(benchMomPast)) and (symbolMomPast != 0) and (benchMomPast != 0) and (benchMom != 0)
        currentRelativeReturn = 100.0 * (symbolNow / symbolPast / (benchNow / benchPast) - 1.0) if validNow else na
        previousRelativeReturn = 100.0 * (symbolMom / symbolMomPast / (benchMom / benchMomPast) - 1.0) if validPrevious else na
        momentum = currentRelativeReturn - previousRelativeReturn if not na(currentRelativeReturn) and (not na(previousRelativeReturn)) else na
        array.set(relativeReturns, i, currentRelativeReturn)
        array.set(relativeMomentum, i, momentum)

    strengthPercentiles: list[float] = array.new_float(symbolCount, na)
    momentumPercentiles: list[float] = array.new_float(symbolCount, na)
    compositeScores: list[float] = array.new_float(symbolCount, na)

    for i in pine_range(0, symbolCount - 1):
        strengthPct = f_percentile(relativeReturns, i)
        momentumPct = f_percentile(relativeMomentum, i)
        score = strengthPct * strengthWeight + momentumPct * momentumWeight if not na(strengthPct) and (not na(momentumPct)) else na
        array.set(strengthPercentiles, i, strengthPct)
        array.set(momentumPercentiles, i, momentumPct)
        array.set(compositeScores, i, score)

    currentRanks: list[int] = array.new_int(symbolCount, na)
    currentStates: list[str] = array.new_string(symbolCount, 'N/A')

    for i in pine_range(0, symbolCount - 1):
        array.set(currentRanks, i, f_ordinalRank(compositeScores, i))
        array.set(currentStates, i, f_state(array.get(strengthPercentiles, i), array.get(momentumPercentiles, i), strengthCut, momentumCut))

    previousRanks: Persistent[list[int]] = array.new_int()
    previousStates: Persistent[list[str]] = array.new_string()
    persistenceCounts: Persistent[list[int]] = array.new_int()
    latestRankChanges: Persistent[list[int]] = array.new_int()

    if barstate.isfirst:
        for i in pine_range(0, symbolCount - 1):
            array.push(previousRanks, na)
            array.push(previousStates, 'N/A')
            array.push(persistenceCounts, 0)
            array.push(latestRankChanges, na)

    anyLeaderEntry: bool = False
    anyQuadrantTransition: bool = False
    anyLeadershipLoss: bool = False
    anyPersistenceHit: bool = False
    eventMessage: str = ""

    if newScan:
        for i in pine_range(0, symbolCount - 1):
            symbolName: str = f_shortSymbol(array.get(symbols, i))
            rankNow: int = array.get(currentRanks, i)
            rankBefore: int = array.get(previousRanks, i)
            stateNow: str = array.get(currentStates, i)
            stateBefore: str = array.get(previousStates, i)
            persistenceBefore: int = array.get(persistenceCounts, i)
            persistenceNow: int = persistenceBefore + 1 if not na(rankNow) and rankNow <= topQuartile else 0
            array.set(persistenceCounts, i, persistenceNow)
            array.set(latestRankChanges, i, rankBefore - rankNow if not na(rankNow) and (not na(rankBefore)) else na)

            leaderEntry: bool = sendAlertsInput and (not na(rankBefore)) and (not na(rankNow)) and (rankBefore > leaderCount) and (rankNow <= leaderCount)
            quadrantTransition: bool = sendAlertsInput and stateBefore != 'N/A' and (stateNow != 'N/A') and (stateBefore != stateNow)
            leadershipLoss: bool = sendAlertsInput and (not na(rankBefore)) and (not na(rankNow)) and (rankBefore <= leaderCount) and (rankNow > leaderCount)
            persistenceHit: bool = sendAlertsInput and persistenceBefore < persistenceThresholdInput and (persistenceNow >= persistenceThresholdInput)

            if leaderEntry:
                anyLeaderEntry = True
                eventMessage = f_appendEvent(eventMessage, symbolName + ' entered Top ' + string.tostring(leaderCount))
            if quadrantTransition:
                anyQuadrantTransition = True
                eventMessage = f_appendEvent(eventMessage, symbolName + ': ' + stateBefore + ' → ' + stateNow)
            if leadershipLoss:
                anyLeadershipLoss = True
                eventMessage = f_appendEvent(eventMessage, symbolName + ' left Top ' + string.tostring(leaderCount))
            if persistenceHit:
                anyPersistenceHit = True
                eventMessage = f_appendEvent(eventMessage, symbolName + ' reached ' + string.tostring(persistenceThresholdInput) + ' top-quartile scans')

            array.set(previousRanks, i, rankNow)
            array.set(previousStates, i, stateNow)

        if eventMessage != '':
            alert('TF Relative Strength Screener | ' + string.format_time(scanStamp, 'yyyy-MM-dd HH:mm') + '\n' + eventMessage, alert.freq_once_per_bar)

    anyEvent: bool = anyLeaderEntry or anyQuadrantTransition or anyLeadershipLoss or anyPersistenceHit
    alertcondition(anyLeaderEntry, 'RS leader entry', "A symbol entered the selected leader group. Use an 'Any alert() function call' alert for symbol details.")
    alertcondition(anyQuadrantTransition, 'RS rotation change', "A symbol changed rotation state. Use an 'Any alert() function call' alert for symbol details.")
    alertcondition(anyLeadershipLoss, 'RS leadership loss', "A symbol left the Top-N group. Use an 'Any alert() function call' alert for symbol details.")
    alertcondition(anyPersistenceHit, 'RS leadership confirmed', "A symbol reached the selected leadership-confirmation count. Use an 'Any alert() function call' alert for symbol details.")
    alertcondition(anyEvent, 'Any RS screener event', "The Relative Strength Screener generated an event. Use an 'Any alert() function call' alert for symbol details.")

    requestedFocusIndex: int = array.indexof(symbols, focusSymbolInput)
    focusIndex: int = requestedFocusIndex if requestedFocusIndex >= 0 else 0
    oscSymbol: str = array.get(symbols, focusIndex)
    oscClose, oscTime = request.security(oscSymbol, timeframe.period, (close[1], time[1]), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off, ignore_invalid_symbol=True)
    oscBenchmark, oscBenchTime = request.security(benchmarkInput, timeframe.period, (close[1], time[1]), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off, ignore_invalid_symbol=True)

    oscAligned: bool = not na(oscClose) and (not na(oscBenchmark)) and (oscBenchmark > 0) and (oscTime == oscBenchTime)
    oscRatio: Series[float] = oscClose / oscBenchmark if oscAligned else na
    oscRaw: float = 100.0 * (oscRatio / oscRatio[oscLookbackInput] - 1.0) if not na(oscRatio[oscLookbackInput]) and oscRatio[oscLookbackInput] > 0 else na
    oscSmoothed: float = ta.ema(oscRaw, oscSmoothInput)
    oscSignalBase: float = ta.ema(oscSmoothed, oscSignalInput)
    oscValue: float = oscSmoothed if not na(oscRaw) else na
    oscSignal: float = oscSignalBase if not na(oscRaw) else na
    oscColor: Color = color.new('#26D6AD') if oscValue >= 0 else color.new('#F16B82')
    ribbonColor: Color = color.new(color.new('#26D6AD'), 88) if oscValue >= oscSignal else color.new(color.new('#F16B82'), 88)
    hline(0, 'Benchmark parity • 0%', color=color.new(color.new('#B0BEC5'), 45), linestyle=hline.style_dashed)
    oscPlot = plot(oscValue, 'Relative performance % (smoothed)', color=oscColor, linewidth=3, style=plot.style_linebr)
    signalPlot = plot(oscSignal if oscShowSignalInput else na, 'Relative performance signal', color=color.new(color.new('#C8D0DF'), 35), linewidth=1, style=plot.style_linebr, display=display.pane)
    fill(oscPlot, signalPlot, color=ribbonColor if oscShowSignalInput else na, title='Relative acceleration ribbon', fillgaps=False)
    plot(oscRaw, 'Unsmoothed benchmark-relative return %', display=display.data_window)
    oscEndLabel: Persistent[Label] = na(Label)
    if barstate.islast:
        label.delete(oscEndLabel)
        if oscShowLabelInput:
            oscName: str = f_shortSymbol(oscSymbol) + ' / ' + f_shortSymbol(benchmarkInput)
            oscText: str = oscName + (' • No aligned data' if na(oscValue) else '  ' + string.tostring(oscValue, '+#.##;-#.##') + '%')
            oscEndLabel = label.new(bar_index + 2, nz(oscValue, 0), oscText, style=label.style_label_left, color=color.new(color.new('#0D1A3F'), 100), textcolor=color.gray if na(oscValue) else oscColor, size=size.small, tooltip='Smoothed relative return over ' + string.tostring(oscLookbackInput) + ' chart bars. Above zero: outperforming the benchmark. Below zero: underperforming. Ribbon: line versus EMA signal, not a buy/sell recommendation. Confirmed data: one chart bar late.')

    dashboard: Persistent[Table] = table.new(dashboardPositionInput, 7, 14, bgcolor=color.new('#0D1A3F'), border_width=1, frame_width=1, frame_color=color.new('#1C306D'), border_color=color.new('#1C306D'), force_overlay=True)
    matrix__ren__: Persistent[Table] = table.new(matrixPositionInput, 2, 5, bgcolor=color.new('#0D1A3F'), border_width=1, frame_width=1, frame_color=color.new('#1C306D'), border_color=color.new('#1C306D'), force_overlay=True)

    if barstate.islast:
        table.clear(dashboard, 0, 0, 6, 13)
        table.clear(matrix__ren__, 0, 0, 1, 4)

        if showDashboardInput:
            headerBg: Color = color.new('#1C306D')
            headerFg: Color = color.white
            rankedCount: int = 0
            for i in pine_range(0, symbolCount - 1):
                if not na(array.get(compositeScores, i)):
                    rankedCount += 1
            completeUniverse: bool = rankedCount == symbolCount
            lowerTfNoData: bool = scanIsLower and rankedCount == 0
            lowerTfLimited: bool = scanIsLower and rankedCount > 0 and (not completeUniverse)
            scanLabel: str = f_timeframeLabel(scanTfInput)
            chartLabel: str = f_timeframeLabel(timeframe.period)
            table.cell(dashboard, 0, 0, '♦ TradingFinder ♦', text_color=color.new('#56CFE0'), text_size=dashboardSizeInput, bgcolor=color.new('#0D1A3F'))
            table.merge_cells(dashboard, 0, 0, 6, 0)
            checkUnit: str = 'chart checks' if scanIsLower else 'scans'
            scanMode: str = 'Intrabar snapshot' if scanIsLower else 'Confirmed bars'
            contextText: str = string.tostring(symbolCount) + ' symbols vs ' + f_shortSymbol(benchmarkInput) + ' | Scan ' + scanLabel + ' | ' + scanMode
            if scanIsLower:
                contextText = 'Scan ' + scanLabel + ' < Chart ' + chartLabel + ' | ' + scanMode
            if lowerTfNoData:
                contextText = 'NO DATA — Scan ' + scanLabel + ' is below Chart ' + chartLabel
            elif lowerTfLimited:
                contextText = 'LIMITED DATA — Scan ' + scanLabel + ' is below Chart ' + chartLabel + ' | ' + string.tostring(rankedCount) + '/' + string.tostring(symbolCount) + ' symbols'
            elif not completeUniverse:
                contextText += ' | Data: ' + string.tostring(rankedCount) + '/' + string.tostring(symbolCount)
            contextTip: str = 'The table uses the latest available lower-timeframe intrabar. Historical rank changes and streaks advance once per completed chart bar.' if scanIsLower else 'The table uses the previous confirmed Scan Timeframe bar.'
            if lowerTfNoData or lowerTfLimited:
                contextTip = "The Scan Timeframe is lower than the Chart Timeframe. TradingView may have limited lower-timeframe intrabar history, so the request did not return usable data for every selected symbol. Use a lower chart timeframe for fuller history."
            table.cell(dashboard, 0, 1, contextText, text_color=color.new('#C6D4EB') if completeUniverse else color.new('#FFBF69'), text_size=dashboardSizeInput, bgcolor=color.new(color.new('#B93241'), 35) if lowerTfNoData else color.new(color.new('#E09100'), 50) if lowerTfLimited else color.new('#111D3A'), tooltip=contextTip + ' Latest data: ' + ('Waiting' if na(scanStamp) else string.format_time(scanStamp, 'yyyy-MM-dd HH:mm')))
            table.merge_cells(dashboard, 0, 1, 6, 1)
            headers: list[str] = array.from_items('Rank', 'Symbol', 'Takeaway / Evidence', 'vs Benchmark', 'Score / 100', 'Top-group streak', 'Rank change')
            tips: list[str] = array.from_items('Position among symbols with valid scores. Ties share a rank.', 'Selected watchlist symbol.', 'Descriptive screening conclusion, not an entry or exit signal. Momentum below is the change in benchmark-relative return over the configured Momentum Length, in percentage points.', 'Relative wealth-factor return. Positive = ahead of benchmark; negative = behind.', 'Weighted strength and momentum percentiles. A comparison score, NOT a probability of profit.', 'Consecutive ' + checkUnit + ' ranked in the top ' + string.tostring(topQuartile) + ' of ' + string.tostring(symbolCount) + ' selected symbols. This does not count benchmark outperformance.', 'Change since the previous ' + ('completed chart check' if scanIsLower else 'confirmed scan') + '. Up means a better rank.')
            for col in pine_range(0, 6):
                table.cell(dashboard, col, 2, array.get(headers, col), text_color=headerFg, text_size=dashboardSizeInput, bgcolor=headerBg, tooltip=array.get(tips, col))
            sortableScores: list[float] = array.copy(compositeScores)
            for i in pine_range(0, symbolCount - 1):
                if na(array.get(sortableScores, i)):
                    array.set(sortableScores, i, -10000000000.0)
            sortedIndices: list[int] = array.sort_indices(sortableScores, order.descending)
            for row in pine_range(0, symbolCount - 1):
                i: int = array.get(sortedIndices, row)
                rankNow: int = array.get(currentRanks, i)
                rel: float = array.get(relativeReturns, i)
                mom: float = array.get(relativeMomentum, i)
                score: float = array.get(compositeScores, i)
                persistence: int = array.get(persistenceCounts, i)
                deltaRank: int = array.get(latestRankChanges, i)
                valid: bool = not na(rankNow) and (not na(rel)) and (not na(mom))

                fading: bool = valid and rel > 0 and (mom < 0)
                durable: bool = valid and rel > 0 and (mom >= 0) and (rankNow <= topQuartile) and (persistence >= persistenceThresholdInput)
                improving: bool = valid and mom > 0 and (not na(deltaRank)) and (deltaRank > 0)
                behind: bool = valid and rel < 0 and (mom <= 0) and (na(deltaRank) or deltaRank <= 0)
                takeaway: str = "Mixed evidence"
                conclusionColor: Color = color.new('#B5C3D8')
                if not valid:
                    takeaway = "Insufficient data"
                elif not completeUniverse:
                    takeaway = "Incomplete comparison"
                    conclusionColor = color.new('#FFBF69')
                elif fading:
                    takeaway = "Outperforming, fading"
                    conclusionColor = color.new('#FFBF69')
                elif durable:
                    takeaway = "Sustained leadership"
                    conclusionColor = color.new('#26D6AD')
                elif improving:
                    takeaway = 'Recovering, still behind' if rel < 0 else 'Climbing the ranks'
                    conclusionColor = color.new('#56CFE0')
                elif behind:
                    takeaway = "Behind, no recovery"
                    conclusionColor = color.new('#F16B82')
                evidence: str = 'More history required' if not valid else 'Relative change ' + string.tostring(mom, '+#.##;-#.##') + ' pp'
                explanation: str = 'Classification priority: incomplete data; outperforming with negative relative momentum; positive relative return + nonnegative momentum + top-group rank for at least ' + string.tostring(persistenceThresholdInput) + ' ' + checkUnit + "; positive momentum + rising rank; negative relative return without improvement; otherwise mixed. These summaries differ from the matrix's cross-sectional quadrants."
                relativeText: str = 'No data' if na(rel) else string.tostring(math.abs(rel), '#.##') + ('% ahead' if rel > 0 else '% behind' if rel < 0 else '% · On par')
                deltaText: str = 'No prior check' if na(deltaRank) else '↑ ' + string.tostring(deltaRank) + ' places' if deltaRank > 0 else '↓ ' + string.tostring(math.abs(deltaRank)) + ' places' if deltaRank < 0 else 'Unchanged'
                rowBg: Color = color.new('#111D3A') if row % 2 == 0 else color.new('#0D1732')
                deltaColor: Color = color.new('#B5C3D8') if na(deltaRank) or deltaRank == 0 else color.new('#26D6AD') if deltaRank > 0 else color.new('#F16B82')
                tableRow: int = row + 3
                table.cell(dashboard, 0, tableRow, '—' if na(rankNow) else string.tostring(rankNow) + ' of ' + string.tostring(rankedCount), text_color=headerFg, text_size=dashboardSizeInput, bgcolor=rowBg)
                table.cell(dashboard, 1, tableRow, f_shortSymbol(array.get(symbols, i)), text_color=headerFg, text_size=dashboardSizeInput, bgcolor=rowBg)
                table.cell(dashboard, 2, tableRow, takeaway + '\n' + evidence, text_color=conclusionColor, text_size=dashboardSizeInput, bgcolor=color.new(conclusionColor, 90), text_halign=text.align_left, tooltip=explanation)
                table.cell(dashboard, 3, tableRow, relativeText, text_color=color.new('#B5C3D8') if na(rel) or rel == 0 else color.new('#26D6AD') if rel > 0 else color.new('#F16B82'), text_size=dashboardSizeInput, bgcolor=rowBg)
                table.cell(dashboard, 4, tableRow, '—' if na(score) else string.tostring(score, '#.0') + ' / 100', text_color=headerFg, text_size=dashboardSizeInput, bgcolor=f_heatColor(score), tooltip='Comparison score only. Not win rate or confidence.')
                table.cell(dashboard, 5, tableRow, '—' if not valid else string.tostring(persistence) + ' ' + checkUnit, text_color=color.new('#26D6AD') if valid and persistence >= persistenceThresholdInput else color.new('#B5C3D8'), text_size=dashboardSizeInput, bgcolor=rowBg)
                table.cell(dashboard, 6, tableRow, deltaText, text_color=deltaColor, text_size=dashboardSizeInput, bgcolor=rowBg)
            footerRow: int = symbolCount + 3
            table.cell(dashboard, 0, footerRow, 'Compare → Shortlist → Check price setup | Score ≠ win probability', text_color=color.new('#B5C3D8'), text_size=dashboardSizeInput, bgcolor=color.new('#0D1A3F'))
            table.merge_cells(dashboard, 0, footerRow, 6, footerRow)

        if showMatrixInput:
            improvingList: str = ""
            leadingList: str = ""
            laggingList: str = ""
            weakeningList: str = ""
            matrixSortableScores: list[float] = array.copy(compositeScores)
            for i in pine_range(0, symbolCount - 1):
                if na(array.get(matrixSortableScores, i)):
                    array.set(matrixSortableScores, i, -10000000000.0)
            matrixOrder: list[int] = array.sort_indices(matrixSortableScores, order.descending)
            for row in pine_range(0, symbolCount - 1):
                i: int = array.get(matrixOrder, row)
                name: str = f_shortSymbol(array.get(symbols, i))
                state: str = array.get(currentStates, i)
                if state == 'Improving':
                    improvingList += ('' if improvingList == '' else '\n') + name
                elif state == 'Leading':
                    leadingList += ('' if leadingList == '' else '\n') + name
                elif state == 'Lagging':
                    laggingList += ('' if laggingList == '' else '\n') + name
                elif state == 'Weakening':
                    weakeningList += ('' if weakeningList == '' else '\n') + name
            table.cell(matrix__ren__, 0, 0, 'ROTATION MATRIX', text_color=color.new('#56CFE0'), text_size=matrixSizeInput, bgcolor=color.new('#0D1A3F'))
            table.merge_cells(matrix__ren__, 0, 0, 1, 0)
            table.cell(matrix__ren__, 0, 1, 'IMPROVING  ↑', text_color=f_stateColor('Improving'), text_size=matrixSizeInput, bgcolor=color.new('#0D1732'))
            table.cell(matrix__ren__, 1, 1, 'LEADING  ◆', text_color=f_stateColor('Leading'), text_size=matrixSizeInput, bgcolor=color.new('#0D1732'))
            table.cell(matrix__ren__, 0, 2, '—' if improvingList == '' else improvingList, text_color=color.white, text_size=matrixSizeInput, bgcolor=color.new(f_stateColor('Improving'), 58), text_halign=text.align_left)
            table.cell(matrix__ren__, 1, 2, '—' if leadingList == '' else leadingList, text_color=color.white, text_size=matrixSizeInput, bgcolor=color.new(f_stateColor('Leading'), 58), text_halign=text.align_left)
            table.cell(matrix__ren__, 0, 3, 'LAGGING  ↓', text_color=f_stateColor('Lagging'), text_size=matrixSizeInput, bgcolor=color.new('#0D1732'))
            table.cell(matrix__ren__, 1, 3, 'WEAKENING  ◇', text_color=f_stateColor('Weakening'), text_size=matrixSizeInput, bgcolor=color.new('#0D1732'))
            table.cell(matrix__ren__, 0, 4, '—' if laggingList == '' else laggingList, text_color=color.white, text_size=matrixSizeInput, bgcolor=color.new(f_stateColor('Lagging'), 58), text_halign=text.align_left)
            table.cell(matrix__ren__, 1, 4, '—' if weakeningList == '' else weakeningList, text_color=color.white, text_size=matrixSizeInput, bgcolor=color.new(f_stateColor('Weakening'), 58), text_halign=text.align_left)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
