"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, barcolor, close, color, fill, hlc3, input, location,
    math, na, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Color, PersistentSeries, Series

adaptiveTrendTip: str = "Volatility Length controls how far back the indicator measures ATR and directional price movement, while Normalization Length sets the reference window used to judge whether current conditions are unusually active or quiet. Lower either value for faster adaptation, or increase them for a steadier response."
smoothingLimitTip: str = "Minimum Smoothing sets the slowest response the adaptive trend can use, while Maximum Smoothing sets the fastest. Lower Minimum Smoothing for more filtering during quiet conditions, and increase Maximum Smoothing for quicker reactions during stronger movement."
ehlersTip: str = "Filter Length controls how many recent EMA-smoothed adaptive trend observations contribute to the displacement-weighted filter, while Momentum Length controls how far apart those observations are compared when calculating their weights. Increase Filter Length for a smoother trendline, and increase Momentum Length to emphasize movement across a broader span of bars."
bandMultiplierTip: str = "Upper Multiplier controls how far the bullish threshold sits above the filtered trendline, while Lower Multiplier controls how far the bearish threshold sits below it. Increase either multiplier to widen that side of the bands and require a larger price move before a regime change."
colorTip: str = "Bullish Color is used for bullish regimes, LONG signals, the upper band, and bullish candle coloring, while Bearish Color is used for bearish regimes, SHORT signals, the lower band, and bearish candle coloring."


@script.indicator("Volatility Adaptive Filtered Trend", overlay=True)
def main(
    src: Series[float] = input.source(title="Source", defval=hlc3, group="Adaptive Trend Settings", tooltip="Choose the price source used throughout the adaptive trend calculation. HLC3 provides a balanced view of each candle by averaging the high, low, and close."),
    volLength=input.int(title="Volatility Length", defval=15, minval=2, group="Adaptive Trend Settings", inline="AT1", tooltip=adaptiveTrendTip),
    normalLength=input.int(title="Normalization Length", defval=30, minval=5, group="Adaptive Trend Settings", inline="AT1", tooltip=adaptiveTrendTip),
    minSC=input.float(title="Minimum Smoothing", defval=0.084, minval=0.001, maxval=1.0, step=0.001, group="Smoothing Limits", inline="SL1", tooltip=smoothingLimitTip),
    maxSC=input.float(title="Maximum Smoothing", defval=0.33, minval=0.001, maxval=1.0, step=0.001, group="Smoothing Limits", inline="SL1", tooltip=smoothingLimitTip),
    emaLength=input.int(title="EMA Smoothing", defval=5, minval=1, group="Smoothing", tooltip="Adds an extra smoothing step to the adaptive trend before the final filter is applied. Increase it to reduce short-term noise or decrease it to preserve more responsiveness."),
    ehlersLength=input.int(title="Filter Length", defval=9, minval=2, group="Ehlers Filter", inline="EF1", tooltip=ehlersTip),
    ehlersMomentum=input.int(title="Momentum Length", defval=2, minval=1, group="Ehlers Filter", inline="EF1", tooltip=ehlersTip),
    bandVolLength=input.int(title="Volatility Length", defval=22, minval=2, group="Volatility Bands", tooltip="Sets how much return history is used to estimate band volatility. Lower values make the bands adjust faster to changing volatility, while higher values create a steadier band width."),
    upperMult=input.float(title="Upper Multiplier", defval=2.0, minval=0.1, step=0.1, group="Volatility Bands", inline="VB1", tooltip=bandMultiplierTip),
    lowerMult=input.float(title="Lower Multiplier", defval=2.0, minval=0.1, step=0.1, group="Volatility Bands", inline="VB1", tooltip=bandMultiplierTip),
    showBands=input.bool(title="Show Bands", defval=True, group="Visualization", tooltip="Show or hide the upper and lower volatility bands around the filtered trendline. Turning this off only changes the chart display and does not affect the trend calculations or signals."),
    showFill=input.bool(title="Show Fill", defval=True, group="Visualization", tooltip="Show or hide the shaded area between the upper and lower volatility bands. This is visual only and does not change the indicator calculations."),
    showSignals=input.bool(title="Show Signals", defval=True, group="Visualization", tooltip="Show or hide LONG and SHORT markers when the active trend regime changes. Turning this off does not change the underlying regime calculation."),
    colorBars=input.bool(title="Color Bars", defval=True, group="Visualization", tooltip="Color price candles according to the currently active trend regime. Turning this off only removes candle coloring and does not affect the signals."),
    longColor=input.color(title="Bullish Color", defval=color.rgb(57, 255, 20), group="Color Settings", inline="COL1", tooltip=colorTip),
    shortColor=input.color(title="Bearish Color", defval=color.rgb(138, 43, 226), group="Color Settings", inline="COL1", tooltip=colorTip)
):
    atr: float = ta.atr(volLength)
    netChange: float = math.abs(src - src[volLength])
    atrBaseline: float = ta.sma(atr, normalLength)
    changeBaseline: float = ta.sma(netChange, normalLength)

    atrFactor: float = atr / atrBaseline if atrBaseline != 0.0 else 1.0
    changeFactor: float = netChange / changeBaseline if changeBaseline != 0.0 else 1.0
    combinedFactor: float = (atrFactor + changeFactor) * 0.5
    normalizedFactor: float = math.max(0.0, math.min(1.0, combinedFactor / 2.0))

    adaptiveSC: float = minSC + (maxSC - minSC) * normalizedFactor

    adaptiveTrend: PersistentSeries[float] = na(float)
    adaptiveTrend = src if na(adaptiveTrend[1]) else adaptiveTrend[1] + adaptiveSC * (src - adaptiveTrend[1])

    emaTrend: Series[float] = ta.ema(adaptiveTrend, emaLength)

    ehlersNumerator: float = 0.0
    ehlersCoefficientSum: float = 0.0

    for i in pine_range(0, ehlersLength - 1):
        currentSample: float = emaTrend[i]
        referenceSample: float = emaTrend[i + ehlersMomentum]

        if not na(currentSample) and (not na(referenceSample)):
            coefficient: float = math.abs(currentSample - referenceSample)
            ehlersNumerator += coefficient * currentSample
            ehlersCoefficientSum += coefficient

    ehlersFallback: float = ta.sma(emaTrend, ehlersLength)
    trendMA: float = ehlersNumerator / ehlersCoefficientSum if ehlersCoefficientSum > 0.0 else ehlersFallback

    priceReturn: float = (src - src[1]) / src[1] if src[1] != 0.0 else 0.0
    volatility: float = inline_series(ta.stdev(priceReturn, bandVolLength), 1)

    upperBand: float = trendMA + upperMult * volatility * trendMA
    lowerBand: float = trendMA - lowerMult * volatility * trendMA

    long: bool = close > upperBand
    short: bool = close < lowerBand

    SQ: PersistentSeries[int] = 0

    if long:
        SQ = 1
    elif short:
        SQ = -1

    longSignal: bool = SQ == 1 and SQ[1] != 1
    shortSignal: bool = SQ == -1 and SQ[1] != -1

    col: Color = longColor if SQ == 1 else shortColor

    plot(trendMA, title='Filtered Adaptive Trend', color=col, linewidth=2)
    upperPlot = plot(upperBand if showBands else na, title='Upper Volatility Band', color=color.new(longColor, 35), linewidth=1)
    lowerPlot = plot(lowerBand if showBands else na, title='Lower Volatility Band', color=color.new(shortColor, 35), linewidth=1)
    fill(upperPlot, lowerPlot, title='Volatility Band Fill', color=color.new(col, 90) if showFill else na)
    plotshape(showSignals and longSignal, title='Long Signal', style=shape.triangleup, location=location.belowbar, size=size.small, color=longColor, text='LONG', textcolor=color.white)
    plotshape(showSignals and shortSignal, title='Short Signal', style=shape.triangledown, location=location.abovebar, size=size.small, color=shortColor, text='SHORT', textcolor=color.white)
    barcolor(col if colorBars else na)

    alertcondition(longSignal, title='Long Signal', message='Volatility Adaptive Filtered Trend Long Signal on {{ticker}}')
    alertcondition(shortSignal, title='Short Signal', message='Volatility Adaptive Filtered Trend Short Signal on {{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)