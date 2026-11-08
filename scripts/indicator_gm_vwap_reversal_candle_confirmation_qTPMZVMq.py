"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alert, alertcondition, bar_index, barmerge, barstate, close, color, fill,
    format, hlc3, input, line, location, math, na, nz, open, plot, plotshape, position, request,
    runtime, script, shape, size, string, syminfo, ta, table, time, time_close, timeframe,
    timestamp, volume, xloc, year
)
from pynecore.types import Color, Line, Persistent, PersistentSeries, Series, Table


@script.indicator("GM VWAP Reversal - Candle Confirmation v1.2", shorttitle="GM VWAP Reversal", overlay=True, max_lines_count=20)
def main(
    anchorChoice=input.string("Session", "VWAP Anchor", options=("Session", "Week", "Month", "Quarter", "Year", "Decade", "Century"), group="VWAP and Zones", tooltip="Session resets at the symbol's daily session boundary. Quarter = Jan/Apr/Jul/Oct. Decade = 2020-2029, 2030-2039, etc. Century = 2000-2099, etc. VWAP, bands and setups share this anchor. Calculation uses a fixed timeframe independent of the chart. Source history may be partial; see VWAP from in the dashboard."),
    calcChoice=input.string("Auto", "Calculation Timeframe", options=("Auto", "1 minute", "5 minutes", "15 minutes", "1 hour", "4 hours", "1 day"), group="VWAP and Zones", tooltip="Auto depends only on the anchor, never on the chart: Session=1 minute; Week/Month/Quarter=1 hour; Year/Decade/Century=1 day. Use the same setting on all charts. Source candles must be shorter than the anchor. Daily-sampled VWAP is an approximation based on daily price and volume, not tick-by-tick VWAP."),
    updateMode=input.string("Confirmed", "VWAP Updates", options=("Confirmed", "Live"), group="VWAP and Zones", tooltip="Confirmed uses the previous closed calculation candle and updates at the next calculation candle's open. With daily calculations it updates once per trading day. Live includes the open calculation candle; historical bands and signals may change after reload. C1/C2 confirmations still use chart candles."),
    sourceChoice=input.string("Close", "VWAP Source", options=("Close", "HLC3"), group="VWAP and Zones", tooltip="Close is the default. HLC3 uses (high + low + close) / 3. Setup and entry conditions always use candle closes."),
    bandMultiplier=input.float(2.0, "Outer Band (Standard Deviations)", minval=0.2, step=0.1, group="VWAP and Zones", tooltip="A confirmed close outside this band starts the leading move."),
    entryZoneMultiplier=input.float(1.0, "Minimum Entry Distance from VWAP", minval=0.1, step=0.1, group="VWAP and Zones", tooltip="Standard deviations. SELL must close at/above the upper inner band; BUY at/below the lower inner band. Must be less than the outer band. This prevents signals near the middle."),
    minAnchorBars=input.int(10, "Minimum Bars after VWAP Reset", minval=2, maxval=500, group="VWAP and Zones", tooltip="Wait for this many chart candles in the anchor before starting setups."),
    maxWaitBars=input.int(30, "Max Bars After C1", minval=2, maxval=300, group="Setup", tooltip="Number of later candles allowed after the first reversal candle, including the wait for C2 and the entry close. The leading move itself may last longer."),
    useAdxFilter=input.bool(False, "Use ADX Filter", group="ADX Filter", tooltip="At the entry candle's close, block signals if ADX is above the threshold and rising. A blocked setup is consumed. Turn off to compare against the original candle-entry rules."),
    diLength=input.int(14, "DI Length", minval=1, maxval=100, group="ADX Filter"),
    adxSmoothing=input.int(14, "ADX Smoothing", minval=1, maxval=100, group="ADX Filter"),
    adxThreshold=input.float(25.0, "Strong ADX Threshold", minval=0.0, maxval=100.0, step=0.5, group="ADX Filter"),
    showMean=input.bool(True, "Show VWAP", group="Display"),
    showBands=input.bool(True, "Show VWAP Bands and Entry Zones", group="Display"),
    showEntryLevel=input.bool(True, "Show Entry Level", group="Display"),
    showTarget=input.bool(True, "Show VWAP Target at Signal", group="Display"),
    showInvalidation=input.bool(False, "Show Setup Invalidation Level", group="Display"),
    showSignals=input.bool(True, "Show BUY / SELL", group="Display"),
    showSetupMarks=input.bool(False, "Show Leading / C1 / C2 Marks", group="Display", tooltip="L = first close outside the band. C1 = first reversal candle. C2 = candle whose CLOSE supplies the fixed entry level. X = an entry blocked by the zone or ADX filter."),
    showDashboard=input.bool(False, "Show Dashboard", group="Display"),
    signalLineBars=input.int(20, "Keep Signal Lines for Bars", minval=1, maxval=200, group="Display", tooltip="Latest setup only. After a signal, its lines remain for this many bars, or until a new setup starts. Historical BUY/SELL markers remain visible."),
    buyColor=input.color(color.rgb(0, 200, 160), "BUY Color", group="Colors"),
    sellColor=input.color(color.rgb(240, 75, 110), "SELL Color", group="Colors"),
    meanColor=input.color(color.rgb(255, 183, 77), "VWAP Color", group="Colors")
):
    __block_result__ = na
    __switch__ = anchorChoice
    if __switch__ == "Session":
        __block_result__ = "1D"
    elif __switch__ == "Week":
        __block_result__ = "1W"
    elif __switch__ == "Month":
        __block_result__ = "1M"
    elif __switch__ == "Quarter":
        __block_result__ = "3M"
    else:
        __block_result__ = "12M"
    anchorTf: str = __block_result__
    anchorYears: int = 10 if anchorChoice == 'Decade' else 100 if anchorChoice == 'Century' else 1
    anchorSeconds: float = timeframe.in_seconds(anchorTf) * anchorYears

    __block_result_1__ = na
    __switch__ = anchorChoice
    if __switch__ == "Session":
        __block_result_1__ = "1"
    elif __switch__ == "Week":
        __block_result_1__ = "60"
    elif __switch__ == "Month":
        __block_result_1__ = "60"
    elif __switch__ == "Quarter":
        __block_result_1__ = "60"
    else:
        __block_result_1__ = "1D"
    autoCalcTf: str = __block_result_1__
    __block_result_2__ = na
    __switch__ = calcChoice
    if __switch__ == "1 minute":
        __block_result_2__ = "1"
    elif __switch__ == "5 minutes":
        __block_result_2__ = "5"
    elif __switch__ == "15 minutes":
        __block_result_2__ = "15"
    elif __switch__ == "1 hour":
        __block_result_2__ = "60"
    elif __switch__ == "4 hours":
        __block_result_2__ = "240"
    elif __switch__ == "1 day":
        __block_result_2__ = "1D"
    else:
        __block_result_2__ = autoCalcTf
    calcTf: str = __block_result_2__
    confirmedSource: bool = updateMode == 'Confirmed'
    sourceBelowChart: bool = timeframe.in_seconds(calcTf) < timeframe.in_seconds()

    if barstate.isfirst:
        if timeframe.in_seconds(calcTf) >= anchorSeconds:
            runtime.error('Calculation Timeframe must be shorter than VWAP Anchor. Use Auto, or choose a smaller calculation timeframe.')
        if entryZoneMultiplier >= bandMultiplier:
            runtime.error('Minimum Entry Distance must be smaller than Outer Band.')

    def f_anchorKey():
        annualYear: int = year(time_close('12M') - 1)
        calendarBlock: int = cast_int(math.floor(annualYear / anchorYears)) * anchorYears
        return timestamp(syminfo.timezone, calendarBlock, 1, 1, 0, 0) if anchorYears > 1 else time(anchorTf)

    def f_sourceVWAP(usePrevious: bool):
        key: Series[int] = f_anchorKey()
        reset: bool = barstate.isfirst or key != key[1]
        startedAt: PersistentSeries[int] = na(int)
        if reset:
            startedAt = time
        src: float = close if sourceChoice == 'Close' else hlc3
        v: Series
        v, hi, lo = ta.vwap(src, reset, 1.0)
        sd: Series[float] = math.max(hi - v, 0.0)
        allVolume: Series[float] = ta.cum(nz(volume))

        return (v[1] if usePrevious else v, sd[1] if usePrevious else sd, key[1] if usePrevious else key, startedAt[1] if usePrevious else startedAt, time_close[1] if usePrevious else time_close, allVolume[1] if usePrevious else allVolume)

    sourceKey: Series
    mean, sigma, sourceKey, sourceStart, sourceAsOf, sourceTotalVolume = request.security(syminfo.tickerid, calcTf, f_sourceVWAP(confirmedSource), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on if confirmedSource and (not sourceBelowChart) else barmerge.lookahead_off, calc_bars_count=100000)

    currentKey: Series[int] = f_anchorKey()
    chartAnchorChanged: bool = not na(currentKey[1]) and currentKey != currentKey[1]
    sourceAnchorChanged: bool = not na(sourceKey) and (na(sourceKey[1]) or sourceKey != sourceKey[1])
    newAnchor: bool = barstate.isfirst or chartAnchorChanged or sourceAnchorChanged

    sourceIsCurrent: bool = not na(sourceKey) and sourceKey == currentKey
    upperBand: float = mean + sigma * bandMultiplier
    lowerBand: float = mean - sigma * bandMultiplier
    upperEntry: float = mean + sigma * entryZoneMultiplier
    lowerEntry: float = mean - sigma * entryZoneMultiplier
    distanceSigma: float = (close - mean) / sigma if sigma > 0 else na
    anchorBars: int = ta.barssince(newAnchor) + 1
    hasVolume: bool = not na(volume) and volume > 0
    dataReady: bool = hasVolume and sourceIsCurrent and (not na(mean)) and (not na(sigma)) and (sigma >= syminfo.mintick) and (anchorBars >= minAnchorBars)
    bullish: bool = close > open
    bearish: bool = close < open

    if barstate.islast and (not na(sourceTotalVolume)) and (sourceTotalVolume == 0):
        runtime.error('This symbol has no usable volume on the calculation timeframe.')

    adx: Series
    diPlus, diMinus, adx = ta.dmi(diLength, adxSmoothing)
    adxReady: bool = not na(adx) and (not na(adx[1]))
    adxStrongRising: bool = adxReady and adx > adxThreshold and (adx > adx[1])
    adxAllowsEntry: bool = not useAdxFilter or (adxReady and (not adxStrongRising))

    meanPlot = plot(mean if showMean else na, 'VWAP', color=meanColor, linewidth=2)
    upperPlot = plot(upperBand if showBands else na, 'Upper Outer Band', color=color.new(sellColor, 20), linewidth=1)
    lowerPlot = plot(lowerBand if showBands else na, 'Lower Outer Band', color=color.new(buyColor, 20), linewidth=1)
    upperEntryPlot = plot(upperEntry if showBands else na, 'Upper Entry Limit', color=color.new(sellColor, 75), linewidth=1)
    lowerEntryPlot = plot(lowerEntry if showBands else na, 'Lower Entry Limit', color=color.new(buyColor, 75), linewidth=1)
    fill(upperEntryPlot, upperPlot, color=color.new(sellColor, 88) if showBands else na, title='Upper Reversal Zone')
    fill(lowerEntryPlot, lowerPlot, color=color.new(buyColor, 88) if showBands else na, title='Lower Reversal Zone')

    def f_price(price: float):
        return '-' if na(price) else string.tostring(price, format.mintick)

    phase: Persistent[int] = 0
    direction: Persistent[int] = 0
    leadingBar: Persistent[int] = na(int)

    leadingExtreme: Persistent[float] = na(float)
    c1Bar: Persistent[int] = na(int)
    c1Close: Persistent[float] = na(float)
    referenceBar: Persistent[int] = na(int)
    entryLevel: Persistent[float] = na(float)
    shortRearmed: Persistent[bool] = True
    longRearmed: Persistent[bool] = True

    lastMeanTarget: Persistent[float] = na(float)
    lastSignalClose: Persistent[float] = na(float)

    newLeading: bool = False
    newC1: bool = False
    newC2: bool = False
    setupCancelled: bool = False
    buySignal: bool = False
    sellSignal: bool = False
    buyBlocked: bool = False
    sellBlocked: bool = False

    if barstate.isconfirmed and (newAnchor or not dataReady):
        phase = 0
        direction = 0
        leadingBar = na
        leadingExtreme = na
        c1Bar = na
        c1Close = na
        referenceBar = na
        entryLevel = na
        setupCancelled = True
        if newAnchor:
            shortRearmed = True
            longRearmed = True
            lastMeanTarget = na
            lastSignalClose = na

    if barstate.isconfirmed and dataReady:
        if close <= mean:
            shortRearmed = True
        if close >= mean:
            longRearmed = True

        if phase > 0:
            meanReached: bool = False
            if direction == -1:
                meanReached = close <= mean
            else:
                meanReached = close >= mean

            expired: bool = not na(c1Bar) and bar_index - c1Bar > maxWaitBars
            invalidated: bool = False
            if phase == 3:
                if direction == -1:
                    invalidated = close > leadingExtreme
                else:
                    invalidated = close < leadingExtreme

            if meanReached or expired or invalidated:
                phase = 0
                direction = 0
                setupCancelled = True

        if phase == 0:
            if close > upperBand and shortRearmed:
                phase = 1
                direction = -1
                leadingBar = bar_index
                leadingExtreme = close
                c1Bar = na
                c1Close = na
                referenceBar = na
                entryLevel = na
                shortRearmed = False
                newLeading = True
            elif close < lowerBand and longRearmed:
                phase = 1
                direction = 1
                leadingBar = bar_index
                leadingExtreme = close
                c1Bar = na
                c1Close = na
                referenceBar = na
                entryLevel = na
                longRearmed = False
                newLeading = True

        if phase == 1:
            if direction == -1:
                leadingExtreme = math.max(leadingExtreme, close)
                if bar_index > leadingBar and bearish:
                    phase = 2
                    c1Bar = bar_index
                    c1Close = close
                    newC1 = True
            else:
                leadingExtreme = math.min(leadingExtreme, close)
                if bar_index > leadingBar and bullish:
                    phase = 2
                    c1Bar = bar_index
                    c1Close = close
                    newC1 = True
        elif phase == 2:
            leadingResumed: bool = False
            c2Ready: bool = False
            if direction == -1:
                leadingResumed = close > leadingExtreme
                leadingExtreme = math.max(leadingExtreme, close)
                c2Ready = bearish and close < c1Close
            else:
                leadingResumed = close < leadingExtreme
                leadingExtreme = math.min(leadingExtreme, close)
                c2Ready = bullish and close > c1Close

            if leadingResumed:
                phase = 1
                c1Bar = na
                c1Close = na
            elif bar_index > c1Bar and c2Ready:
                phase = 3
                referenceBar = bar_index
                entryLevel = close
                newC2 = True
        elif phase == 3:
            entryClose: bool = False
            if direction == -1:
                entryClose = close < entryLevel
            else:
                entryClose = close > entryLevel

            if bar_index > referenceBar and entryClose:
                entryInZone: bool = False
                if direction == -1:
                    entryInZone = close >= upperEntry
                else:
                    entryInZone = close <= lowerEntry
                if entryInZone and adxAllowsEntry:
                    buySignal = direction == 1
                    sellSignal = direction == -1
                    lastSignalClose = close
                    lastMeanTarget = mean
                else:
                    buyBlocked = direction == 1
                    sellBlocked = direction == -1
                phase = 0
                direction = 0

    entryLine: Persistent[Line] = na(Line)
    targetLine: Persistent[Line] = na(Line)
    invalidationLine: Persistent[Line] = na(Line)
    linesExpireBar: Persistent[int] = na(int)

    if barstate.isconfirmed:
        if newLeading or setupCancelled or buyBlocked or sellBlocked:
            if not na(entryLine):
                line.delete(entryLine)
            if not na(targetLine):
                line.delete(targetLine)
            if not na(invalidationLine):
                line.delete(invalidationLine)
            entryLine = na
            targetLine = na
            invalidationLine = na
            linesExpireBar = na

        if newC2:
            setupColor: Color = buyColor if direction == 1 else sellColor
            if showEntryLevel:
                entryLine = line.new(bar_index, entryLevel, bar_index + 1, entryLevel, xloc=xloc.bar_index, color=setupColor, width=2)
            if showInvalidation:
                invalidationLine = line.new(bar_index, leadingExtreme, bar_index + 1, leadingExtreme, xloc=xloc.bar_index, color=color.new(setupColor, 50), style=line.style_dotted)

        if phase == 3:
            if not na(entryLine):
                line.set_x2(entryLine, bar_index + 1)
            if not na(invalidationLine):
                line.set_x2(invalidationLine, bar_index + 1)

        if buySignal or sellSignal:
            linesExpireBar = bar_index + signalLineBars
            if not na(entryLine):
                line.set_x2(entryLine, linesExpireBar)
            if not na(invalidationLine):
                line.set_x2(invalidationLine, linesExpireBar)
            if showTarget:
                targetLine = line.new(bar_index, lastMeanTarget, linesExpireBar, lastMeanTarget, xloc=xloc.bar_index, color=meanColor, style=line.style_dashed, width=2)

        if not na(linesExpireBar) and bar_index > linesExpireBar:
            if not na(entryLine):
                line.delete(entryLine)
            if not na(targetLine):
                line.delete(targetLine)
            if not na(invalidationLine):
                line.delete(invalidationLine)
            entryLine = na
            targetLine = na
            invalidationLine = na
            linesExpireBar = na

    plotshape(showSignals and buySignal, title='BUY Mean Reversion', style=shape.triangleup, location=location.belowbar, color=buyColor, textcolor=buyColor, size=size.small, text='BUY')
    plotshape(showSignals and sellSignal, title='SELL Mean Reversion', style=shape.triangledown, location=location.abovebar, color=sellColor, textcolor=sellColor, size=size.small, text='SELL')

    plotshape(showSetupMarks and newLeading and (direction == -1), title='Leading Up', style=shape.circle, location=location.abovebar, color=sellColor, textcolor=sellColor, size=size.tiny, text='L')
    plotshape(showSetupMarks and newLeading and (direction == 1), title='Leading Down', style=shape.circle, location=location.belowbar, color=buyColor, textcolor=buyColor, size=size.tiny, text='L')
    plotshape(showSetupMarks and newC1 and (direction == -1), title='Bearish C1', style=shape.circle, location=location.abovebar, color=sellColor, textcolor=sellColor, size=size.tiny, text='C1')
    plotshape(showSetupMarks and newC1 and (direction == 1), title='Bullish C1', style=shape.circle, location=location.belowbar, color=buyColor, textcolor=buyColor, size=size.tiny, text='C1')
    plotshape(showSetupMarks and newC2 and (direction == -1), title='SELL Reference C2', style=shape.diamond, location=location.abovebar, color=sellColor, textcolor=sellColor, size=size.tiny, text='C2')
    plotshape(showSetupMarks and newC2 and (direction == 1), title='BUY Reference C2', style=shape.diamond, location=location.belowbar, color=buyColor, textcolor=buyColor, size=size.tiny, text='C2')
    plotshape(showSetupMarks and buyBlocked, title='BUY Blocked by Zone or ADX', style=shape.xcross, location=location.belowbar, color=color.gray, textcolor=color.gray, size=size.tiny, text='X')
    plotshape(showSetupMarks and sellBlocked, title='SELL Blocked by Zone or ADX', style=shape.xcross, location=location.abovebar, color=color.gray, textcolor=color.gray, size=size.tiny, text='X')

    dash: Persistent[Table] = table.new(position.top_right, 2, 10, bgcolor=color.new(color.black, 10), border_width=1)

    if barstate.islast:
        if showDashboard:
            stateText: str = 'Waiting for extension' if shortRearmed and longRearmed else 'Waiting for close at mean'
            stateColor: Color = meanColor
            if phase == 1:
                stateText = 'Leading up / wait C1' if direction == -1 else 'Leading down / wait C1'
            elif phase == 2:
                stateText = 'Bearish C1 / wait C2' if direction == -1 else 'Bullish C1 / wait C2'
            elif phase == 3:
                stateText = 'Wait close below level' if direction == -1 else 'Wait close above level'
            if direction != 0:
                stateColor = buyColor if direction == 1 else sellColor
            if not dataReady:
                stateText = 'Waiting for current anchor data' if not sourceIsCurrent else 'Waiting for VWAP / band width' if hasVolume else 'No volume on this candle'

            table.cell(dash, 0, 0, 'GM VWAP Reversal', text_color=color.white)
            table.cell(dash, 1, 0, 'v1.2 | ' + timeframe.period, text_color=meanColor)
            table.cell(dash, 0, 1, 'VWAP (' + anchorChoice + ')', text_color=color.white)
            table.cell(dash, 1, 1, f_price(mean), text_color=meanColor)
            table.cell(dash, 0, 2, 'Distance', text_color=color.white)
            table.cell(dash, 1, 2, string.tostring(distanceSigma, '#.00') + ' SD', text_color=color.white)
            table.cell(dash, 0, 3, 'Setup', text_color=color.white)
            table.cell(dash, 1, 3, stateText, text_color=stateColor)
            table.cell(dash, 0, 4, 'Entry level', text_color=color.white)
            table.cell(dash, 1, 4, f_price(entryLevel) if phase == 3 else '-', text_color=stateColor)
            table.cell(dash, 0, 5, 'Last VWAP target', text_color=color.white)
            table.cell(dash, 1, 5, f_price(lastMeanTarget), text_color=meanColor)
            adxText: str = "OFF"
            if useAdxFilter:
                adxText = 'Warming up' if not adxReady else string.tostring(adx, '#.0') + (' | Block' if adxStrongRising else ' | Allow')
            table.cell(dash, 0, 6, 'ADX filter (live)', text_color=color.white)
            table.cell(dash, 1, 6, adxText, text_color=meanColor if adxAllowsEntry else color.gray)
            table.cell(dash, 0, 7, 'Calculation', text_color=color.white)
            table.cell(dash, 1, 7, calcTf + ' | ' + updateMode, text_color=meanColor)
            table.cell(dash, 0, 8, 'VWAP from (feed)', text_color=color.white)
            table.cell(dash, 1, 8, 'No source history' if na(sourceStart) else string.format_time(sourceStart, 'yyyy-MM-dd HH:mm', syminfo.timezone), text_color=color.white)
            table.cell(dash, 0, 9, 'Source close (feed)' if confirmedSource else 'Live source closes', text_color=color.white)
            table.cell(dash, 1, 9, '-' if na(sourceAsOf) else string.format_time(sourceAsOf, 'yyyy-MM-dd HH:mm', syminfo.timezone), text_color=color.white)
        else:
            table.clear(dash, 0, 0, 1, 9)

    alertcondition(buySignal, 'GM VWAP Reversal BUY', '{{ticker}} {{interval}} | GM VWAP Reversal BUY | Close: {{close}}')
    alertcondition(sellSignal, 'GM VWAP Reversal SELL', '{{ticker}} {{interval}} | GM VWAP Reversal SELL | Close: {{close}}')
    alertcondition(buySignal or sellSignal, 'GM VWAP Reversal BUY / SELL', '{{ticker}} {{interval}} | GM VWAP Reversal signal | Close: {{close}}')

    if buySignal or sellSignal:
        sideText: str = 'BUY' if buySignal else 'SELL'
        alert(syminfo.tickerid + ' | TF ' + timeframe.period + ' | ' + sideText + ' GM VWAP REVERSAL\nSignal close: ' + f_price(lastSignalClose) + '\nC2 reference close: ' + f_price(entryLevel) + '\nVWAP target at signal: ' + f_price(lastMeanTarget) + '\nSetup close extreme: ' + f_price(leadingExtreme), alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
