"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fill, high, input, location, low, math, na, nz, plot,
    plotshape, script, shape, size, ta
)
from pynecore.types import Persistent, PersistentSeries

t1: str = "Trigger Threshold: Controls when a new trend step is triggered. It's a multiplier of the ATR — higher values require a stronger price move to flip the trend direction."
t2: str = "Max Step Size: Defines the maximum allowed size for each trend step, based on ATR. Use a negative number to scale down large step jumps in volatile conditions."
t3: str = "Band Multiplier: Expands or contracts the volatility bands around the trend line. A higher value creates wider channels to account for more price fluctuation."
t4: str = "Trend Hold: After a trend flip, the trend will hold for this many bars before another flip can occur. Useful for avoiding rapid flip-flopping in choppy markets."
t5: str = "Retest Signals: Enables triangle markers on the chart when price re-tests the upper or lower channel boundary. Helpful for spotting potential continuation or bounce zones."
t6: str = "Trend Filter: Only show retest signals if they align with the current trend direction (e.g., only show upper retests in a downtrend)."
t7: str = "Trend Step Signals: Shows circular markers each time a new step is taken in the trend direction. These mark every structural trend advancement."


@script.indicator("Trend Impulse Channels (Zeiierman)", overlay=True)
def main(
    flipMult=input.float(2.86, step=0.01, title="Trigger Threshold", group="", inline="", tooltip=t1),
    maxStepAtr=input.float(-0.034, step=0.001, title="Max Step Size", group="", inline="", tooltip=t2),
    bandMult=input.float(2.02, step=0.01, title="Band Multiplier", group="", inline="", tooltip=t3),
    holdBars=input.int(0, minval=0, title="Trend Hold", group="", inline="", tooltip=t4),
    colorUp=input.color(color.lime, title="", group="", inline="c", tooltip=""),
    colorDown=input.color(color.red, title="", group="", inline="c", tooltip=""),
    showFill=input.bool(True, title="Channel Fill", group="", inline="c", tooltip=""),
    ChannelRetestSignal=input.bool(True, title="Retest Signals", group="Retest Signals", inline="c22", tooltip=t5),
    TrendFilter=input.bool(True, title="Filter by Trend", group="Retest Signals", inline="c222", tooltip=t6),
    colorUp2=input.color(color.lime, title="", group="Retest Signals", inline="c2", tooltip=""),
    colorDown2=input.color(color.red, title="", group="Retest Signals", inline="c2", tooltip=""),
    TrendStepSignal=input.bool(False, title="Trend Step Signals", group="Trend Step Signals", inline="c33", tooltip=t7),
    colorUp3=input.color(color.lime, title="", group="Trend Step Signals", inline="c3", tooltip=""),
    colorDown3=input.color(color.red, title="", group="Trend Step Signals", inline="c3", tooltip="")
):
    atr = ta.atr(200)
    stepBase = atr * 2.52
    maxStep = atr * maxStepAtr
    trigger = atr * flipMult

    trend: PersistentSeries[float] = na(float)
    dir: Persistent[int] = 0
    barsInTrend: Persistent[int] = 0
    hold: Persistent[float] = na(float)
    extension: Persistent[int] = 0

    startLong = close > nz(trend) + trigger
    startShort = close < nz(trend) - trigger
    flip = (startLong or startShort) and barsInTrend >= 0
    stepSize = math.min(stepBase + 0.0093 * barsInTrend * atr, maxStep)

    if na(trend):
        trend = close
        dir = 0
        barsInTrend = 0
        hold = trigger
        extension = 0
    else:
        if flip and extension <= 0:
            trend = close
            dir = 1 if startLong else -1
            barsInTrend = 1
            hold = trigger
            extension = holdBars
        else:
            trend = trend + (stepSize if dir == 1 else -stepSize if dir == -1 else 0)
            barsInTrend += 1
            extension = math.max(extension - 1, 0)

    trendDirection = 1 if dir == 1 else -1 if dir == -1 else 0
    upper = trend + atr * bandMult
    lower = trend - atr * bandMult

    trendColor = colorUp if dir == 1 else colorDown if dir == -1 else color.gray
    trendStep = dir != 0 and trend != trend[1] and (trend > trend[1] and dir == 1 or (trend < trend[1] and dir == -1))

    plotMid = plot(trend, 'Trend Line', color=trendColor, linewidth=2)
    plotUpper = plot(upper if showFill else na, 'Upper Band', color=na)
    plotLower = plot(lower if showFill else na, 'Lower Band', color=na)
    fill(plotUpper, plotMid, upper, trend, color.new(trendColor, 60) if showFill else na, na)
    fill(plotLower, plotMid, lower, trend, color.new(trendColor, 60) if showFill else na, na)

    Crossunder = ta.crossunder(low, lower)
    Crossover = ta.crossover(high, upper)

    if TrendFilter:
        Crossunder = ta.crossunder(low, lower) and trendDirection == 1
        Crossover = ta.crossover(high, upper) and trendDirection == -1

    plotshape(low if Crossunder and ChannelRetestSignal else na, title='Lower Retest', color=colorUp2, style=shape.triangleup, size=size.tiny, location=location.belowbar)
    plotshape(high if Crossover and ChannelRetestSignal else na, title='Upper Retest', color=colorDown2, style=shape.triangledown, size=size.tiny, location=location.abovebar)

    plotshape(high if trendStep and dir == 1 and TrendStepSignal else na, title='Bullish Step', location=location.absolute, style=shape.circle, color=colorUp3, size=size.tiny)
    plotshape(low if trendStep and dir == -1 and TrendStepSignal else na, title='Bearish Step', location=location.absolute, style=shape.circle, color=colorDown3, size=size.tiny)
    plotshape(high if trendStep and dir == 1 and TrendStepSignal else na, title='Bullish Step', location=location.absolute, style=shape.circle, color=color.new(colorUp3, 50), size=size.small)
    plotshape(low if trendStep and dir == -1 and TrendStepSignal else na, title='Bearish Step', location=location.absolute, style=shape.circle, color=color.new(colorDown3, 50), size=size.small)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)