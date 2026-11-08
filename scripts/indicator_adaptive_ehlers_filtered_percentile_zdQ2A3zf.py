"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, barcolor, close, color, fill, input, location, math, na,
    plot, plotshape, script, shape, size, ta
)
from pynecore.types import Color, PersistentSeries, Series

adaptivePeriodTip: str = "Minimum MA Period sets the fastest adaptive response used during higher volatility, while Maximum MA Period sets the slowest response used during calmer conditions. Lower the minimum for quicker reactions, and increase the maximum for a smoother baseline."
ehlersTip: str = "Filter Length controls how many Adaptive MA observations contribute to the nonlinear Ehlers filter, while Momentum Length controls how far apart those observations are compared when calculating their weights. Increase Filter Length for a smoother trendline, and increase Momentum Length to emphasize broader price displacement."
percentileTip: str = "Percentile Length sets how much historical price-to-filter displacement is ranked, while Percentile Level selects which ranked distance becomes the base band width. Increase the length for a broader sample and increase the percentile level for wider, more selective bands."
multiplierTip: str = "Upper Band Multiplier scales the percentile distance above the filtered trend, while Lower Band Multiplier scales the distance below it. Increase either multiplier to widen that side of the regime threshold and require a larger price move before a breakout."
colorTip: str = "Bullish Color is used for bullish regimes, LONG signals, the upper band, and bullish candle coloring, while Bearish Color is used for bearish regimes, SHORT signals, the lower band, and bearish candle coloring."


@script.indicator("Adaptive Ehlers Filtered Percentile", overlay=True)
def main(
    maSrc: Series[float] = input.source(title="Source", defval=close, group="Adaptive MA Settings", tooltip="Choose the price source used to calculate the volatility-adaptive moving average."),
    maMin=input.int(title="Minimum MA Period", defval=3, minval=1, group="Adaptive MA Settings", inline="AMA1", tooltip=adaptivePeriodTip),
    maMax=input.int(title="Maximum MA Period", defval=30, minval=2, group="Adaptive MA Settings", inline="AMA1", tooltip=adaptivePeriodTip),
    volLen=input.int(title="Volatility Period", defval=9, minval=2, group="Adaptive MA Settings", tooltip="Sets the lookback used to measure the standard deviation of price changes and adapt the moving average length. Increase it for steadier adaptation or decrease it for faster reactions to changing volatility."),
    ehlersLength=input.int(title="Filter Length", defval=9, minval=2, group="Ehlers Filter", inline="EF1", tooltip=ehlersTip),
    ehlersMomentum=input.int(title="Momentum Length", defval=15, minval=1, group="Ehlers Filter", inline="EF1", tooltip=ehlersTip),
    percentileLen=input.int(title="Percentile Length", defval=50, minval=2, group="Percentile Bands", inline="PB1", tooltip=percentileTip),
    percentileLevel=input.float(title="Percentile Level", defval=75.0, minval=1.0, maxval=99.0, step=1.0, group="Percentile Bands", inline="PB1", tooltip=percentileTip),
    upperMult=input.float(title="Upper Band Multiplier", defval=0.7, minval=0.1, step=0.1, group="Percentile Bands", inline="PB2", tooltip=multiplierTip),
    lowerMult=input.float(title="Lower Band Multiplier", defval=0.7, minval=0.1, step=0.1, group="Percentile Bands", inline="PB2", tooltip=multiplierTip),
    showMA=input.bool(title="Show Adaptive Filter", defval=True, group="Visualization", tooltip="Show or hide the Ehlers-filtered Adaptive MA. Turning this off only changes the chart display and does not affect the calculations or signals."),
    showBands=input.bool(title="Show Percentile Bands", defval=True, group="Visualization", tooltip="Show or hide the upper and lower percentile bands. Turning this off only changes the chart display and does not affect the regime calculations."),
    showFill=input.bool(title="Show Band Fill", defval=True, group="Visualization", tooltip="Show or hide the shaded area between the upper and lower percentile bands. This is visual only and does not change the indicator calculations."),
    showSignals=input.bool(title="Show Signals", defval=True, group="Visualization", tooltip="Show or hide LONG and SHORT markers whenever price establishes a new percentile-band regime. Turning this off does not change the underlying regime state."),
    colorBars=input.bool(title="Color Bars", defval=True, group="Visualization", tooltip="Color price candles according to the currently active regime. Turning this off only removes candle coloring and does not affect signals."),
    longColor=input.color(title="Bullish Color", defval=color.rgb(57, 255, 20), group="Color Settings", inline="C1", tooltip=colorTip),
    shortColor=input.color(title="Bearish Color", defval=color.rgb(138, 43, 226), group="Color Settings", inline="C1", tooltip=colorTip)
):
    deltaP: float = maSrc - maSrc[1]
    s: float = ta.stdev(deltaP, volLen)
    sAverage: float = ta.sma(s, volLen)

    sMin: float = sAverage * 0.25
    sMax: float = sAverage * 1.75
    volRange: float = sMax - sMin

    adaptiveLength: float = (maMax if s <= sMin else maMin if s >= sMax else maMax - (maMax - maMin) * (s - sMin) / volRange) if volRange > 0.0 else maMax
    alpha: float = 2.0 / (adaptiveLength + 1.0)

    adaptiveMA: PersistentSeries[float] = na(float)
    adaptiveMA = maSrc if na(adaptiveMA[1]) else adaptiveMA[1] + alpha * (maSrc - adaptiveMA[1])

    ehlersNumerator: float = 0.0
    ehlersCoefficientSum: float = 0.0

    for i in pine_range(0, ehlersLength - 1):
        currentSample: float = adaptiveMA[i]
        referenceSample: float = adaptiveMA[i + ehlersMomentum]
        if not na(currentSample) and (not na(referenceSample)):
            coefficient: float = math.abs(currentSample - referenceSample)
            ehlersNumerator += coefficient * currentSample
            ehlersCoefficientSum += coefficient

    ehlersFallback: float = ta.sma(adaptiveMA, ehlersLength)
    trendMA: float = ehlersNumerator / ehlersCoefficientSum if ehlersCoefficientSum > 0.0 else ehlersFallback

    deviation: float = math.abs(maSrc - trendMA)
    percentileDistance: float = ta.percentile_nearest_rank(deviation, percentileLen, percentileLevel)

    upperBand: float = trendMA + percentileDistance * upperMult
    lowerBand: float = trendMA - percentileDistance * lowerMult

    long: bool = maSrc > upperBand
    short: bool = maSrc < lowerBand

    SQ: PersistentSeries[int] = 0

    if long:
        SQ = 1
    elif short:
        SQ = -1

    longSignal: bool = SQ == 1 and SQ[1] != 1
    shortSignal: bool = SQ == -1 and SQ[1] != -1

    col: Color = longColor if SQ == 1 else shortColor

    plot(trendMA if showMA else na, title='Adaptive Ehlers Filter', color=col, linewidth=2)
    upperPlot = plot(upperBand if showBands else na, title='Upper Percentile Band', color=color.new(longColor, 35), linewidth=1)
    lowerPlot = plot(lowerBand if showBands else na, title='Lower Percentile Band', color=color.new(shortColor, 35), linewidth=1)
    fill(upperPlot, lowerPlot, title='Percentile Band Fill', color=color.new(col, 92) if showFill else na)
    plotshape(showSignals and longSignal, title='Long Signal', style=shape.triangleup, location=location.belowbar, color=longColor, size=size.small, text='LONG', textcolor=color.white)
    plotshape(showSignals and shortSignal, title='Short Signal', style=shape.triangledown, location=location.abovebar, color=shortColor, size=size.small, text='SHORT', textcolor=color.white)
    barcolor(col if colorBars else na)

    alertcondition(longSignal, title='Long Signal', message='Adaptive Ehlers Filtered Percentile Long Signal on {{ticker}}')
    alertcondition(shortSignal, title='Short Signal', message='Adaptive Ehlers Filtered Percentile Short Signal on {{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)