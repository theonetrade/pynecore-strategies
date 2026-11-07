"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, array, barstate, bgcolor, close, color, high, hlc3,
    hline, input, location, low, math, na, open, plot, plotshape, position, script, shape, size,
    strategy, string, syminfo, ta, table, time, timeframe, volume
)
from pynecore.types import Persistent, Series, Table


@script.strategy('Fabio Valentini Pro Scalper', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=100000)
def main(
    sessionStart=input.session('0930-1600', 'Trading Session (NY)', group='Session'),
    useSessionFilter=input.bool(True, 'Only Trade During Session', group='Session'),
    vpLength=input.int(50, 'Volume Profile Lookback', minval=10, group='Volume Profile'),
    vpResolution=input.int(24, 'VP Row Resolution', minval=10, maxval=50, group='Volume Profile'),
    absorbVolMult=input.float(2.0, 'Absorption Volume Multiplier', minval=1.0, step=0.1, group='Absorption'),
    absorbPriceThresh=input.float(0.3, 'Absorption Max Price Move (ATR %)', minval=0.1, step=0.1, group='Absorption'),
    deltaLookback=input.int(5, 'Delta Smoothing', minval=1, group='Delta'),
    useVWAP=input.bool(True, 'Use VWAP Filter', group='VWAP'),
    vwapBand=input.float(0.5, 'VWAP Band (ATR Multiplier)', minval=0.1, group='VWAP'),
    riskPercent=input.float(1.0, 'Risk Per Trade (%)', minval=0.1, maxval=5.0, group='Risk'),
    rrRatio=input.float(2.0, 'Risk:Reward Ratio', minval=1.0, maxval=5.0, group='Risk'),
    maxDailyLosses=input.int(3, 'Max Losses Before Stop (Fabio\'s 3-stop rule)', minval=1, maxval=10, group='Risk'),
    trailingStop=input.bool(True, 'Use Trailing Stop', group='Risk'),
    trailATRMult=input.float(1.5, 'Trailing Stop ATR Multiplier', minval=0.5, group='Risk'),
    orbMinutes=input.int(30, 'Opening Range Minutes', minval=5, maxval=60, group='ORB'),
    useORB=input.bool(True, 'Use ORB Breakout', group='ORB'),
    showVALevels=input.bool(True, 'Show Value Area Levels', group='Visuals'),
    showAbsorption=input.bool(True, 'Show Absorption Signals', group='Visuals'),
    showDelta=input.bool(True, 'Show Delta Histogram', group='Visuals')
):
    atr = ta.atr(14)

    vwapValue = ta.vwap(hlc3)
    vwapUpper = vwapValue + atr * vwapBand
    vwapLower = vwapValue - atr * vwapBand

    inSession: Series = not na(time(timeframe.period, sessionStart))
    sessionChange = inSession and (not inSession[1])

    poc: Persistent[float] = na(float)
    vah: Persistent[float] = na(float)
    val: Persistent[float] = na(float)

    sessionHigh = ta.highest(high, vpLength)
    sessionLow = ta.lowest(low, vpLength)
    priceRange = sessionHigh - sessionLow
    rowHeight = priceRange / vpResolution

    volumeAtPrice: Persistent[list[float]] = array.new_float(vpResolution, 0.0)

    if barstate.isconfirmed:
        for i in pine_range(0, vpResolution - 1, 1):
            array.set(volumeAtPrice, i, 0.0)

        for j in pine_range(0, vpLength - 1, 1):
            priceLevel = math.floor((close[j] - sessionLow) / rowHeight)
            if priceLevel >= 0 and priceLevel < vpResolution:
                currentVol = array.get(volumeAtPrice, cast_int(priceLevel))
                array.set(volumeAtPrice, cast_int(priceLevel), currentVol + volume[j])

        maxVol: float = 0.0
        pocIndex: int = 0
        for i in pine_range(0, vpResolution - 1, 1):
            if array.get(volumeAtPrice, i) > maxVol:
                maxVol = array.get(volumeAtPrice, i)
                pocIndex = i

        poc = sessionLow + pocIndex * rowHeight + rowHeight / 2

        totalVol = array.sum(volumeAtPrice)
        targetVol = totalVol * 0.7

        accumulatedVol = array.get(volumeAtPrice, pocIndex)
        vahIndex = pocIndex
        valIndex = pocIndex

        while accumulatedVol < targetVol and (vahIndex < vpResolution - 1 or valIndex > 0):
            aboveVol = array.get(volumeAtPrice, vahIndex + 1) if vahIndex < vpResolution - 1 else 0.0
            belowVol = array.get(volumeAtPrice, valIndex - 1) if valIndex > 0 else 0.0

            if aboveVol >= belowVol and vahIndex < vpResolution - 1:
                vahIndex = vahIndex + 1
                accumulatedVol = accumulatedVol + aboveVol
            elif valIndex > 0:
                valIndex = valIndex - 1
                accumulatedVol = accumulatedVol + belowVol
            else:
                break

        vah = sessionLow + vahIndex * rowHeight + rowHeight
        val = sessionLow + valIndex * rowHeight

    buyVolume = volume if close > open else volume * 0.5 if close == open else volume * ((high - close) / (high - low + 0.0001))
    sellVolume = volume - buyVolume

    delta = buyVolume - sellVolume
    smoothDelta: Series = ta.sma(delta, deltaLookback)
    cumulativeDelta = ta.cum(delta)
    deltaMomentum = ta.change(cumulativeDelta, deltaLookback)

    buyersControl = smoothDelta > 0 and smoothDelta > smoothDelta[1]
    sellersControl = smoothDelta < 0 and smoothDelta < smoothDelta[1]

    avgVolume = ta.sma(volume, 20)
    priceMove = math.abs(close - open) / atr
    highVolume = volume > avgVolume * absorbVolMult
    smallMove = priceMove < absorbPriceThresh

    absorption = highVolume and smallMove
    absorptionUp: Series = absorption and close > open
    absorptionDown: Series = absorption and close < open

    absorptionCount: Persistent[int] = 0
    if absorption:
        absorptionCount = absorptionCount + 1
    else:
        absorptionCount = 0

    strongAbsorption = absorptionCount >= 2

    rangeSize = ta.highest(high, 10) - ta.lowest(low, 10)
    avgRange = ta.sma(rangeSize, 50)
    contraction: Series = rangeSize < avgRange * 0.6

    expansion = rangeSize > avgRange * 1.2 and volume > avgVolume * 1.5
    aggressiveBuy = expansion and close > open and (smoothDelta > 0)
    aggressiveSell = expansion and close < open and (smoothDelta < 0)

    tripleALong = absorptionUp[3] or absorptionUp[4] or absorptionUp[5]
    tripleALongSetup = tripleALong and contraction[1] and aggressiveBuy

    tripleAShort = absorptionDown[3] or absorptionDown[4] or absorptionDown[5]
    tripleAShortSetup = tripleAShort and contraction[1] and aggressiveSell

    orbHigh: Persistent[float] = na(float)
    orbLow: Persistent[float] = na(float)
    orbDefined: Persistent[bool] = False

    if sessionChange:
        orbHigh = na
        orbLow = na
        orbDefined = False

    orbBars = orbMinutes / timeframe.in_seconds(timeframe.period) * 60
    sessionBars = ta.barssince(sessionChange)

    if inSession and sessionBars <= orbBars:
        orbHigh = high if na(orbHigh) else math.max(orbHigh, high)
        orbLow = low if na(orbLow) else math.min(orbLow, low)
        orbDefined = sessionBars == orbBars

    orbBreakoutLong = useORB and orbDefined and (close > orbHigh) and (close[1] <= orbHigh)
    orbBreakoutShort = useORB and orbDefined and (close < orbLow) and (close[1] >= orbLow)

    atVAL = not na(val) and low <= val * 1.001 and (low >= val * 0.999)
    atVAH = not na(vah) and high >= vah * 0.999 and (high <= vah * 1.001)

    valBounce = atVAL and absorptionUp and buyersControl
    vahBounce = atVAH and absorptionDown and sellersControl

    longSignal = (tripleALongSetup or orbBreakoutLong or valBounce) and (not useVWAP or close > vwapLower)
    shortSignal = (tripleAShortSetup or orbBreakoutShort or vahBounce) and (not useVWAP or close < vwapUpper)

    sessionOK = not useSessionFilter or inSession

    dailyLosses: Persistent[int] = 0
    if sessionChange:
        dailyLosses = 0

    canTrade = dailyLosses < maxDailyLosses

    if longSignal and sessionOK and canTrade and (strategy.position_size == 0):
        stopLoss = low - atr
        takeProfit = close + (close - stopLoss) * rrRatio

        strategy.entry('Long', strategy.long)
        strategy.exit('Long Exit', 'Long', stop=stopLoss, limit=takeProfit, trail_points=atr * trailATRMult / syminfo.mintick if trailingStop else na, trail_offset=atr * 0.5 / syminfo.mintick if trailingStop else na)

    if shortSignal and sessionOK and canTrade and (strategy.position_size == 0):
        stopLoss = high + atr
        takeProfit = close - (stopLoss - close) * rrRatio

        strategy.entry('Short', strategy.short)
        strategy.exit('Short Exit', 'Short', stop=stopLoss, limit=takeProfit, trail_points=atr * trailATRMult / syminfo.mintick if trailingStop else na, trail_offset=atr * 0.5 / syminfo.mintick if trailingStop else na)

    if strategy.closedtrades.profit(strategy.closedtrades - 1) < 0 and strategy.closedtrades > strategy.closedtrades[1]:
        dailyLosses = dailyLosses + 1

    plot(vwapValue if useVWAP else na, 'VWAP', color=color.orange, linewidth=2)
    plot(vwapUpper if useVWAP else na, 'VWAP Upper', color=color.orange, linewidth=1, style=plot.style_circles)
    plot(vwapLower if useVWAP else na, 'VWAP Lower', color=color.orange, linewidth=1, style=plot.style_circles)

    plot(poc if showVALevels else na, 'POC', color=color.yellow, linewidth=2, style=plot.style_stepline)
    plot(vah if showVALevels else na, 'VAH', color=color.red, linewidth=1, style=plot.style_stepline)
    plot(val if showVALevels else na, 'VAL', color=color.green, linewidth=1, style=plot.style_stepline)

    plot(orbHigh if useORB and orbDefined else na, 'ORB High', color=color.teal, linewidth=1, style=plot.style_stepline)
    plot(orbLow if useORB and orbDefined else na, 'ORB Low', color=color.teal, linewidth=1, style=plot.style_stepline)

    plotshape(showAbsorption and absorptionUp, 'Buy Absorption', shape.circle, location.belowbar, color=color.new(color.green, 50), size=size.small)
    plotshape(showAbsorption and absorptionDown, 'Sell Absorption', shape.circle, location.abovebar, color=color.new(color.red, 50), size=size.small)
    plotshape(strongAbsorption and close > open, 'Strong Buy Absorption', shape.diamond, location.belowbar, color=color.green, size=size.normal)
    plotshape(strongAbsorption and close < open, 'Strong Sell Absorption', shape.diamond, location.abovebar, color=color.red, size=size.normal)

    plotshape(tripleALongSetup, 'Triple-A Long', shape.triangleup, location.belowbar, color=color.lime, size=size.large)
    plotshape(tripleAShortSetup, 'Triple-A Short', shape.triangledown, location.abovebar, color=color.fuchsia, size=size.large)

    hline(0, 'Zero', color=color.gray, linestyle=hline.style_dotted)

    plotshape(longSignal and canTrade and sessionOK, 'Long Entry', shape.arrowup, location.belowbar, color=color.green, size=size.large, text='LONG')
    plotshape(shortSignal and canTrade and sessionOK, 'Short Entry', shape.arrowdown, location.abovebar, color=color.red, size=size.large, text='SHORT')

    bgcolor(color.new(color.blue, 95) if inSession else na, title='Trading Session')

    bgcolor(color.new(color.red, 90) if dailyLosses >= maxDailyLosses else na, title='Max Losses - Stop Trading')

    infoTable: Persistent[Table] = table.new(position.top_right, 2, 8, bgcolor=color.new(color.black, 80), border_width=1)

    if barstate.islast:
        table.cell(infoTable, 0, 0, 'Fabio Valentini Pro Scalper', text_color=color.white, text_size=size.small)
        table.cell(infoTable, 1, 0, '', text_color=color.white)

        table.cell(infoTable, 0, 1, 'Delta', text_color=color.gray, text_size=size.tiny)
        table.cell(infoTable, 1, 1, 'BUYERS ↑' if buyersControl else 'SELLERS ↓' if sellersControl else 'NEUTRAL', text_color=color.green if buyersControl else color.red if sellersControl else color.gray, text_size=size.tiny)

        table.cell(infoTable, 0, 2, 'Absorption', text_color=color.gray, text_size=size.tiny)
        table.cell(infoTable, 1, 2, 'STRONG' if strongAbsorption else 'ACTIVE' if absorption else 'NONE', text_color=color.yellow if strongAbsorption else color.orange if absorption else color.gray, text_size=size.tiny)

        table.cell(infoTable, 0, 3, 'Phase', text_color=color.gray, text_size=size.tiny)
        table.cell(infoTable, 1, 3, 'EXPANSION' if expansion else 'CONTRACTION' if contraction else 'NORMAL', text_color=color.lime if expansion else color.orange if contraction else color.gray, text_size=size.tiny)

        table.cell(infoTable, 0, 4, 'Daily Losses', text_color=color.gray, text_size=size.tiny)
        table.cell(infoTable, 1, 4, string.tostring(dailyLosses) + '/' + string.tostring(maxDailyLosses), text_color=color.red if dailyLosses >= maxDailyLosses - 1 else color.white, text_size=size.tiny)

        table.cell(infoTable, 0, 5, 'POC', text_color=color.gray, text_size=size.tiny)
        table.cell(infoTable, 1, 5, string.tostring(poc, '#.##'), text_color=color.yellow, text_size=size.tiny)

        table.cell(infoTable, 0, 6, 'VAH/VAL', text_color=color.gray, text_size=size.tiny)
        table.cell(infoTable, 1, 6, string.tostring(vah, '#.##') + ' / ' + string.tostring(val, '#.##'), text_color=color.white, text_size=size.tiny)

        table.cell(infoTable, 0, 7, 'Session', text_color=color.gray, text_size=size.tiny)
        table.cell(infoTable, 1, 7, 'ACTIVE' if inSession else 'CLOSED', text_color=color.green if inSession else color.red, text_size=size.tiny)

    alertcondition(longSignal and canTrade, 'Long Signal', 'Fabio Valentini Pro Scalper: Long Entry Signal')
    alertcondition(shortSignal and canTrade, 'Short Signal', 'Fabio Valentini Pro Scalper: Short Entry Signal')
    alertcondition(strongAbsorption, 'Strong Absorption', 'Strong absorption detected - watch for breakout')
    alertcondition(tripleALongSetup, 'Triple-A Long', 'Triple-A Long Setup: Absorption → Accumulation → Aggression UP')
    alertcondition(tripleAShortSetup, 'Triple-A Short', 'Triple-A Short Setup: Absorption → Accumulation → Aggression DOWN')
    alertcondition(dailyLosses >= maxDailyLosses, 'Max Losses', 'Daily loss limit reached - STOP TRADING')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
