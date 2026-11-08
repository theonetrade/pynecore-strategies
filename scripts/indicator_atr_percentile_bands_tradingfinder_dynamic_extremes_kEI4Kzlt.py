"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barstate, close, color, fill,
    high, input, location, low, math, na, nz, open, plot, plotshape, position, script, shape, size,
    string, syminfo, ta, table
)
from pynecore.types import Persistent, Series, Table


@script.indicator("ATR Percentile Bands [TradingFinder] Dynamic Extremes", "Dynamic Percentile", overlay=True, behind_chart=True, max_labels_count=200)
def main(
    movingAverageType=input.string("EMA", "Moving Average Type", options=("EMA", "SMA", "RMA", "WMA", "HMA"), group="Logical Settings"),
    movingAveragePeriod=input.int(50, "Moving Average Period", minval=2, maxval=500, group="Logical Settings"),
    atrPeriod=input.int(14, "ATR Period", minval=2, maxval=500, group="Logical Settings"),
    atrMultiplier=input.float(2.8, "ATR Multiplier", minval=0.5, maxval=10.0, step=0.1, group="Logical Settings"),
    smoothPeriod=input.int(5, "Smooth Period", minval=1, maxval=100, group="Logical Settings"),
    signalGap=input.int(10, "Signal Gap", minval=0, maxval=500, group="Logical Settings"),
    showMovingAverage=input.bool(True, "Moving Average", group="Display Settings"),
    showSignals=input.bool(True, "Signals", group="Display Settings"),
    showTable=input.bool(True, "Show Table", group="Table Settings"),
    tableSizeInput=input.string(size.small, "Table Size", options=(size.tiny, size.small, size.normal, size.large), group="Table Settings"),
    tablePositionInput=input.string(position.top_right, "Table Position", options=(position.top_left, position.top_center, position.top_right, position.middle_left, position.middle_center, position.middle_right, position.bottom_left, position.bottom_center, position.bottom_right), group="Table Settings"),
    alertEnabled=input.bool(True, "Alert", group="Alert Settings"),
    messageFrequency=input.string("Once Per Bar Close", "Message Frequency", options=("All", "Once Per Bar", "Once Per Bar Close"), group="Alert Settings")
):
    def movingAverage(source: float, period: int, averageType: str):
        return ta.ema(source, period) if averageType == 'EMA' else ta.sma(source, period) if averageType == 'SMA' else ta.rma(source, period) if averageType == 'RMA' else ta.wma(source, period) if averageType == 'WMA' else ta.hma(source, period)

    average: Series = movingAverage(close, movingAveragePeriod, movingAverageType)
    atr = ta.ema(ta.atr(atrPeriod), smoothPeriod)
    atrDistance = atr * atrMultiplier

    priceDeviation = math.abs(close - average)
    percentileDistance = ta.percentile_linear_interpolation(priceDeviation, 200, 95)
    rawOuterDistance = math.max(atrDistance, nz(percentileDistance, atrDistance))
    outerDistance = ta.ema(rawOuterDistance, smoothPeriod)
    innerDistance = outerDistance * 0.62
    volatilityRank = ta.percentrank(atr, 200)

    upperInnerBand = average + innerDistance
    upperOuterBand = average + outerDistance
    lowerInnerBand = average - innerDistance
    lowerOuterBand = average - outerDistance

    upperStop1 = upperInnerBand + (upperOuterBand - upperInnerBand) * 0.25
    upperStop2 = upperInnerBand + (upperOuterBand - upperInnerBand) * 0.5
    upperStop3 = upperInnerBand + (upperOuterBand - upperInnerBand) * 0.75
    lowerStop1 = lowerInnerBand + (lowerOuterBand - lowerInnerBand) * 0.25
    lowerStop2 = lowerInnerBand + (lowerOuterBand - lowerInnerBand) * 0.5
    lowerStop3 = lowerInnerBand + (lowerOuterBand - lowerInnerBand) * 0.75

    longSetup = low <= lowerInnerBand and close > lowerInnerBand and (close > open)
    shortSetup = high >= upperInnerBand and close < upperInnerBand and (close < open)

    pendingDirection: Persistent[int] = 0
    confirmationCount: Persistent[int] = 0
    lastPublishedSignal: Persistent[int] = na(int)

    longSignal: bool = False
    shortSignal: bool = False
    signalGapQualified = na(lastPublishedSignal) or bar_index - lastPublishedSignal >= signalGap

    if barstate.isconfirmed:
        if pendingDirection == 0:
            if signalGapQualified and longSetup:
                pendingDirection = 1
                confirmationCount = 1
            elif signalGapQualified and shortSetup:
                pendingDirection = -1
                confirmationCount = 1
        elif pendingDirection == 1:
            if shortSetup:
                pendingDirection = -1
                confirmationCount = 1
            elif close > lowerInnerBand and close > open:
                confirmationCount += 1
            else:
                pendingDirection = 0
                confirmationCount = 0
        elif pendingDirection == -1:
            if longSetup:
                pendingDirection = 1
                confirmationCount = 1
            elif close < upperInnerBand and close < open:
                confirmationCount += 1
            else:
                pendingDirection = 0
                confirmationCount = 0

        if pendingDirection == 1 and confirmationCount >= 3:
            longSignal = True
            lastPublishedSignal = bar_index
            pendingDirection = 0
            confirmationCount = 0
        elif pendingDirection == -1 and confirmationCount >= 3:
            shortSignal = True
            lastPublishedSignal = bar_index
            pendingDirection = 0
            confirmationCount = 0

    upperInnerPlot = plot(upperInnerBand, 'Upper Band Inner', color=color.new(color.new('#E91E63'), 82), linewidth=1)
    upperStop1Plot = plot(upperStop1, 'Upper Band Gradient 1', color=color.new(color.new('#E91E63'), 100), editable=False)
    upperStop2Plot = plot(upperStop2, 'Upper Band Center', color=color.new(color.new('#E91E63'), 12), linewidth=1)
    upperStop3Plot = plot(upperStop3, 'Upper Band Gradient 3', color=color.new(color.new('#E91E63'), 100), editable=False)
    upperOuterPlot = plot(upperOuterBand, 'Upper Band Outer', color=color.new(color.new('#E91E63'), 4), linewidth=1)

    lowerInnerPlot = plot(lowerInnerBand, 'Lower Band Inner', color=color.new(color.new('#00C6A2'), 82), linewidth=1)
    lowerStop1Plot = plot(lowerStop1, 'Lower Band Gradient 1', color=color.new(color.new('#00C6A2'), 100), editable=False)
    lowerStop2Plot = plot(lowerStop2, 'Lower Band Center', color=color.new(color.new('#00C6A2'), 12), linewidth=1)
    lowerStop3Plot = plot(lowerStop3, 'Lower Band Gradient 3', color=color.new(color.new('#00C6A2'), 100), editable=False)
    lowerOuterPlot = plot(lowerOuterBand, 'Lower Band Outer', color=color.new(color.new('#00C6A2'), 4), linewidth=1)

    plot(average if showMovingAverage else na, 'Moving Average', color=color.new(color.new('#A8B0BE'), 55), linewidth=1)

    fill(upperInnerPlot, upperStop1Plot, color=color.new(color.new('#E91E63'), 94), title='Upper Band Layer 1')
    fill(upperStop1Plot, upperStop2Plot, color=color.new(color.new('#E91E63'), 86), title='Upper Band Layer 2')
    fill(upperStop2Plot, upperStop3Plot, color=color.new(color.new('#E91E63'), 73), title='Upper Band Layer 3')
    fill(upperStop3Plot, upperOuterPlot, color=color.new(color.new('#E91E63'), 53), title='Upper Band Layer 4')

    fill(lowerInnerPlot, lowerStop1Plot, color=color.new(color.new('#00C6A2'), 94), title='Lower Band Layer 1')
    fill(lowerStop1Plot, lowerStop2Plot, color=color.new(color.new('#00C6A2'), 86), title='Lower Band Layer 2')
    fill(lowerStop2Plot, lowerStop3Plot, color=color.new(color.new('#00C6A2'), 73), title='Lower Band Layer 3')
    fill(lowerStop3Plot, lowerOuterPlot, color=color.new(color.new('#00C6A2'), 53), title='Lower Band Layer 4')

    plotshape(showSignals and longSignal, 'Long Signal', shape.triangleup, location.belowbar, color.new('#00C600'), 0, 'Long Signal', color.new('#00C600'), True, size.small)
    plotshape(showSignals and shortSignal, 'Short Signal', shape.triangledown, location.abovebar, color.new('#E91E1E'), 0, 'Short Signal', color.new('#E91E1E'), True, size.small)

    marketState = 'Buy Signal' if longSignal else 'Sell Signal' if shortSignal else 'Buy Setup' if pendingDirection == 1 else 'Sell Setup' if pendingDirection == -1 else 'No Signal'
    marketStateColor = color.new('#26D6AD') if longSignal or pendingDirection == 1 else color.new('#F16B82') if shortSignal or pendingDirection == -1 else color.new('#B5C3D8')

    extremeZone = 'Above Upper Band' if close > upperOuterBand else 'Upper Band' if close >= upperInnerBand else 'Below Lower Band' if close < lowerOuterBand else 'Lower Band' if close <= lowerInnerBand else 'Above Average' if close >= average else 'Below Average'
    extremeZoneColor = color.new('#F16B82') if close >= upperInnerBand else color.new('#26D6AD') if close <= lowerInnerBand else color.new('#56CFE0')

    bullishTrend = close > average and average > average[1]
    bearishTrend = close < average and average < average[1]
    trendState = 'Bullish' if bullishTrend else 'Bearish' if bearishTrend else 'Sideways'
    trendStateColor = color.new('#26D6AD') if bullishTrend else color.new('#F16B82') if bearishTrend else color.new('#FFBF69')

    bandsReady = not na(upperInnerBand) and (not na(lowerInnerBand))
    distanceToUpperPercent = math.abs(upperInnerBand - close) / math.abs(close) * 100 if bandsReady and close != 0 else na
    distanceToLowerPercent = math.abs(close - lowerInnerBand) / math.abs(close) * 100 if bandsReady and close != 0 else na
    upperBandIsNearest = bandsReady and distanceToUpperPercent <= distanceToLowerPercent
    nearestBand = 'Loading' if not bandsReady else 'At Upper Band' if close >= upperInnerBand else 'At Lower Band' if close <= lowerInnerBand else string.tostring(distanceToUpperPercent, '#.##') + '% to Upper' if upperBandIsNearest else string.tostring(distanceToLowerPercent, '#.##') + '% to Lower'
    nearestBandColor = color.new('#B5C3D8') if not bandsReady else color.new('#F16B82') if close >= upperInnerBand else color.new('#26D6AD') if close <= lowerInnerBand else color.new('#F16B82') if upperBandIsNearest else color.new('#26D6AD')

    volatilityState = 'Loading' if na(volatilityRank) else 'High' if volatilityRank >= 80 else 'Low' if volatilityRank <= 20 else 'Normal'
    volatilityStateColor = color.new('#B5C3D8') if na(volatilityRank) else color.new('#F16B82') if volatilityRank >= 80 else color.new('#56CFE0') if volatilityRank <= 20 else color.new('#26D6AD')

    nextStep = 'Buy Confirmed' if longSignal else 'Sell Confirmed' if shortSignal else 'Wait for Buy' if pendingDirection == 1 else 'Wait for Sell' if pendingDirection == -1 else 'Look for Sell' if close >= upperInnerBand else 'Look for Buy' if close <= lowerInnerBand else 'Wait'
    nextStepColor = color.new('#26D6AD') if longSignal or pendingDirection == 1 or close <= lowerInnerBand else color.new('#F16B82') if shortSignal or pendingDirection == -1 or close >= upperInnerBand else color.new('#B5C3D8')

    decisionTable: Persistent[Table] = table.new(tablePositionInput, 6, 3, bgcolor=color.new('#0D1A3F'), frame_color=color.new('#1C306D'), frame_width=1, border_color=color.new('#1C306D'), border_width=1)

    if barstate.isfirst:
        table.merge_cells(decisionTable, 0, 0, 5, 0)

    if barstate.islast:
        if showTable:
            table.cell(decisionTable, 0, 0, '♦ TradingFinder ♦', bgcolor=color.new('#0D1A3F'), text_color=color.new('#56CFE0'), text_size=tableSizeInput)

            A: list[str] = array.from_items('Signal', 'Price Zone', 'Trend', 'Nearest Band', 'Volatility', 'Next Action')
            for column in pine_range(0, 5):
                table.cell(decisionTable, column, 1, array.get(A, column), bgcolor=color.new('#1C306D'), text_color=color.white, text_size=tableSizeInput)

            table.cell(decisionTable, 0, 2, marketState, bgcolor=color.new(marketStateColor, 84), text_color=marketStateColor, text_size=tableSizeInput)
            table.cell(decisionTable, 1, 2, extremeZone, bgcolor=color.new('#0D1732'), text_color=extremeZoneColor, text_size=tableSizeInput)
            table.cell(decisionTable, 2, 2, trendState, bgcolor=color.new(trendStateColor, 88), text_color=trendStateColor, text_size=tableSizeInput)
            table.cell(decisionTable, 3, 2, nearestBand, bgcolor=color.new('#0D1732'), text_color=nearestBandColor, text_size=tableSizeInput, tooltip='Shows which inner band is closest and the remaining distance as a percentage of price.')
            table.cell(decisionTable, 4, 2, volatilityState, bgcolor=color.new(volatilityStateColor, 90), text_color=volatilityStateColor, text_size=tableSizeInput)
            table.cell(decisionTable, 5, 2, nextStep, bgcolor=color.new(nextStepColor, 86), text_color=nextStepColor, text_size=tableSizeInput)
        else:
            table.clear(decisionTable, 0, 0, 5, 2)

    longAlert = alertEnabled and longSignal
    shortAlert = alertEnabled and shortSignal

    alertcondition(longAlert, ' Long Signal', ' Long Signal on {{ticker}} after three consecutive confirmations.')
    alertcondition(shortAlert, ' Short Signal', ' Short Signal on {{ticker}} after three consecutive confirmations.')
    alertcondition(longAlert or shortAlert, ' Any Signal', ' confirmed signal on {{ticker}}.')

    alertFrequency = alert.freq_all if messageFrequency == 'All' else alert.freq_once_per_bar if messageFrequency == 'Once Per Bar' else alert.freq_once_per_bar_close
    if longAlert:
        alert('LONG SIGNAL ' + syminfo.ticker + ' 3 consecutive confirmations', alertFrequency)
    if shortAlert:
        alert('SHORT SIGNAL ' + syminfo.ticker + ' 3 consecutive confirmations', alertFrequency)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)