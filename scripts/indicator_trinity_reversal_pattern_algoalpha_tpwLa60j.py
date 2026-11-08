"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, chart, close, color, extend,
    fill, high, input, label, line, location, low, math, na, open, plot, plotshape, runtime,
    script, shape, size, string, ta, text, xloc, yloc
)
from pynecore.types import Label, Line, NA, Persistent, Series

calcGR: str = "Calculation"
trendGR: str = "Trend Filter"
appearanceGR: str = "Appearance"


@script.indicator("Trinity Reversal Pattern [AlgoAlpha]", "AlgoAlpha - Trinity Reversal", overlay=True, max_lines_count=500, max_labels_count=500, max_bars_back=5000)
def main(
    strengthLookback=input.int(100, "Strength Lookback", minval=2, maxval=5000, tooltip="Number of recent candle bodies stored in the array, including the current candle. Strength is the signal candle body divided by the largest stored body, multiplied by 100. It is not a win probability.", group=calcGR),
    minimumStrength=input.float(0.0, "Minimum Signal Strength (%)", minval=0.0, maxval=100.0, step=1.0, tooltip="Filters out patterns below this body-strength score. Set to 0 to accept all pattern strengths.", group=calcGR),
    expiryInput=input.int(100, "Level Expiry Bars", minval=1, maxval=5000, tooltip="Number of chart bars after the signal candle before an untouched level expires. Expiry occurs at that bar's close. Touch checks start on the candle after the signal.", group=calcGR),
    confirmClose=input.bool(True, "Confirm Signals on Close", tooltip="Waits for the signal candle to close before confirming a pattern. When disabled, signals, levels, and scores can change before the candle closes.", group=calcGR),
    useTrend=input.bool(False, "Use EMA Trend Filter", tooltip="Shows the EMA gradient and filters opposing signals. A fast EMA cross above the slow EMA starts a bullish trend. A cross below starts a bearish trend. When disabled, both pattern directions are allowed.", group=trendGR),
    fastLength=input.int(21, "Fast EMA", minval=1, maxval=500, group=trendGR, inline="ema"),
    slowLength=input.int(50, "Slow EMA", minval=2, maxval=1000, tooltip="Lengths of the fast and slow EMAs. The fast length must be less than the slow length when the trend filter is enabled.", group=trendGR, inline="ema"),
    trendSource: Series[float] = input.source(close, "EMA Source", tooltip="Price source used by both trend EMAs.", group=trendGR),
    showSignals=input.bool(True, "Show Signals", group=appearanceGR, inline="visuals"),
    showLevels=input.bool(True, "Show Levels", tooltip="Shows the signal markers and reversal levels. Hiding these visuals does not disable signal or level-touch alerts.", group=appearanceGR, inline="visuals"),
    showStrength=input.bool(True, "Show Strength", group=appearanceGR, inline="labels"),
    labelSizeInput=input.string("Small", "Text Size", options=("Tiny", "Small", "Normal", "Large"), tooltip="Shows a fixed strength score at the midpoint of each active level. Labels use the chart background color and are deleted when levels are touched or expire.", group=appearanceGR, inline="labels"),
    levelExtension=input.int(5, "Active Level Extension", minval=1, maxval=100, tooltip="Number of chart bars to project active levels ahead. Touched or expired lines end at the touch or expiry bar.", group=appearanceGR),
    inactiveTransparency=input.int(75, "Inactive Level Transparency", minval=0, maxval=100, tooltip="Transparency of stopped levels. These lines remain on the chart as dotted lines until the storage limit requires removal.", group=appearanceGR),
    maxLevels=input.int(500, "Maximum Stored Levels", minval=10, maxval=500, tooltip="Maximum number of active and stopped lines retained. At the limit, the oldest stopped line is removed first. If every stored line is still active, the oldest active line and its label are removed instead.", group=appearanceGR),
    showCrosses=input.bool(True, "Show EMA Crosses", tooltip="Shows a dot when the fast EMA crosses the slow EMA. Requires the EMA trend filter.", group=appearanceGR),
    gradientTransparency=input.int(70, "Trend Gradient Transparency", minval=0, maxval=100, tooltip="Transparency at the stronger edge of the EMA gradient. The opposite edge is more transparent.", group=appearanceGR),
    bullColor=input.color(color.new('#00FFBB'), "Bullish Color", group=appearanceGR, inline="colors"),
    bearColor=input.color(color.new('#FF1100'), "", tooltip="Colors used for bullish and bearish signals, levels, strength text, and the EMA gradient.", group=appearanceGR, inline="colors")
):
    bodySamples: Persistent[list[float]] = array.new_float()
    activeLines: Persistent[list[Line]] = array.new_line()
    activeLabels: Persistent[list[Label]] = array.new_label()
    activeDirections: Persistent[list[int]] = array.new_int()
    activeStartBars: Persistent[list[int]] = array.new_int()
    inactiveLines: Persistent[list[Line]] = array.new_line()
    trend: Persistent[int] = 0

    def sizeFromString(txt):
        __block_result__ = na
        __switch__ = txt
        if __switch__ == "Tiny":
            __block_result__ = size.tiny
        elif __switch__ == "Small":
            __block_result__ = size.small
        elif __switch__ == "Normal":
            __block_result__ = size.normal
        else:
            __block_result__ = size.large
        return __block_result__

    def removeActiveLevel(index):
        levelLine = array.remove(activeLines, index)
        label.delete(array.remove(activeLabels, index))
        array.remove(activeDirections, index)
        array.remove(activeStartBars, index)
        return levelLine

    if barstate.isfirst and useTrend and (fastLength >= slowLength):
        runtime.error('Fast EMA length must be less than Slow EMA length.')

    candleBody = math.abs(close - open)
    array.push(bodySamples, candleBody)

    if array.size(bodySamples) > strengthLookback:
        array.shift(bodySamples)

    largestBody = array.max(bodySamples)
    strength = math.min(100.0, candleBody / largestBody * 100.0) if largestBody > 0 else 0.0

    fastEMA = ta.ema(trendSource, fastLength)
    slowEMA = ta.ema(trendSource, slowLength)
    bullCross = ta.crossover(fastEMA, slowEMA)
    bearCross = ta.crossunder(fastEMA, slowEMA)

    if bullCross:
        trend = 1
    elif bearCross:
        trend = -1
    elif trend == 0:
        trend = 1 if fastEMA > slowEMA else -1 if fastEMA < slowEMA else 0

    bull = close > open and high > high[2] and (low[1] < low[2]) and (high[1] < high[2]) and (close[1] < open[1]) and (close[2] < open[2])
    bear = close < open and low < low[2] and (high[1] > high[2]) and (low[1] > low[2]) and (close[1] > open[1]) and (close[2] > open[2])

    signalReady = bar_index >= 2 and (not confirmClose or barstate.isconfirmed)
    bullSignal = bull and signalReady and (strength >= minimumStrength) and (not useTrend or trend == 1)
    bearSignal = bear and signalReady and (strength >= minimumStrength) and (not useTrend or trend == -1)

    patternLow = math.min(low, low[1], low[2])
    patternHigh = math.max(high, high[1], high[2])
    lowOffset = 0 if low == patternLow else 1 if low[1] == patternLow else 2
    highOffset = 0 if high == patternHigh else 1 if high[1] == patternHigh else 2

    bullLevelTouched: bool = False
    bearLevelTouched: bool = False
    levelExpired: bool = False

    if array.size(activeLines) > 0:
        for i in pine_range(array.size(activeLines) - 1, 0):
            activeLine = array.get(activeLines, i)
            activeLabel = array.get(activeLabels, i)
            direction = array.get(activeDirections, i)
            startBar = array.get(activeStartBars, i)
            level = line.get_y1(activeLine)
            age = bar_index - startBar

            if age > 0:
                wickTouch = low <= level if direction == 1 else high >= level
                expired = age >= expiryInput and barstate.isconfirmed
                endBar = bar_index if wickTouch or expired else bar_index + levelExtension
                line.set_x2(activeLine, endBar)

                if wickTouch or expired:
                    levelColor = bullColor if direction == 1 else bearColor
                    line.set_color(activeLine, color.new(levelColor, inactiveTransparency) if showLevels else na)
                    line.set_style(activeLine, line.style_dotted)
                    array.push(inactiveLines, removeActiveLevel(i))
                    bullLevelTouched = bullLevelTouched or (wickTouch and direction == 1)
                    bearLevelTouched = bearLevelTouched or (wickTouch and direction == -1)
                    levelExpired = levelExpired or (expired and (not wickTouch))
                elif not na(activeLabel):
                    midpoint = cast_int(math.floor((line.get_x1(activeLine) + endBar) * 0.5))
                    label.set_x(activeLabel, midpoint)

    if bullSignal or bearSignal:
        while array.size(activeLines) + array.size(inactiveLines) >= maxLevels:
            if array.size(inactiveLines) > 0:
                line.delete(array.shift(inactiveLines))
            else:
                line.delete(removeActiveLevel(0))

        direction = 1 if bullSignal else -1
        level = patternLow if bullSignal else patternHigh
        startBar = bar_index - (lowOffset if bullSignal else highOffset)
        endBar = bar_index + levelExtension
        levelColor = bullColor if bullSignal else bearColor
        midpoint = cast_int(math.floor((startBar + endBar) * 0.5))
        levelText = string.tostring(strength, '#.#') + '% Strength'

        newLine = line.new(x1=startBar, y1=level, x2=endBar, y2=level, xloc=xloc.bar_index, extend=extend.none, color=levelColor if showLevels else na, width=3)
        newLabel = NA(Label)

        if showLevels and showStrength:
            newLabel = label.new(x=midpoint, y=level, text=levelText, xloc=xloc.bar_index, yloc=yloc.price, color=chart.bg_color, style=label.style_label_center, textcolor=levelColor, size=sizeFromString(labelSizeInput), textalign=text.align_center)

        array.push(activeLines, newLine)
        array.push(activeLabels, newLabel)
        array.push(activeDirections, direction)
        array.push(activeStartBars, bar_index)

    trendColor = bullColor if trend == 1 else bearColor if trend == -1 else color.gray
    trendTop = math.max(fastEMA, slowEMA)
    trendBottom = math.min(fastEMA, slowEMA)
    fadeTransparency = math.min(100, gradientTransparency + 25)
    topColor = color.new(trendColor, fadeTransparency) if trend == 1 else color.new(trendColor, gradientTransparency)
    bottomColor = color.new(trendColor, gradientTransparency) if trend == 1 else color.new(trendColor, fadeTransparency)

    fastPlot = plot(fastEMA if useTrend else na, title='Fast Trend EMA', color=color.new(trendColor, 15), linewidth=2, style=plot.style_linebr)
    slowPlot = plot(slowEMA if useTrend else na, title='Slow Trend EMA', color=color.new(trendColor, 45), linewidth=2, style=plot.style_linebr)
    fill(fastPlot, slowPlot, trendTop, trendBottom, topColor if useTrend else na, bottomColor if useTrend else na, title='EMA Trend Gradient', fillgaps=False)

    plot(slowEMA if useTrend and showCrosses and (bullCross or bearCross) else na, title='EMA Cross', color=trendColor, linewidth=4, style=plot.style_circles)

    plotshape(showSignals and bullSignal, title='Bullish Trinity Reversal', style=shape.labelup, location=location.belowbar, color=bullColor, text='▲', textcolor=chart.fg_color, size=size.tiny)
    plotshape(showSignals and bearSignal, title='Bearish Trinity Reversal', style=shape.labeldown, location=location.abovebar, color=bearColor, text='▼', textcolor=chart.fg_color, size=size.tiny)

    alertcondition(bullSignal, title='Bullish Trinity Reversal')
    alertcondition(bearSignal, title='Bearish Trinity Reversal')
    alertcondition(bullLevelTouched, title='Bullish Trinity Level Touched')
    alertcondition(bearLevelTouched, title='Bearish Trinity Level Touched')
    alertcondition(levelExpired, title='Trinity Level Expired')
    alertcondition(useTrend and bullCross and signalReady, title='Bullish EMA Cross')
    alertcondition(useTrend and bearCross and signalReady, title='Bearish EMA Cross')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)