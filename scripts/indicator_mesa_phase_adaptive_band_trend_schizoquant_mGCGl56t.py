"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, barcolor, close, color, fill, hl2, input, location, math,
    na, nz, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Color, PersistentSeries, Series

phaseTip: str = "Fast Limit sets the quickest phase response the indicator can use, while Slow Limit sets the slowest. Increase Fast Limit for stronger reactions during rapid phase movement. Lower Slow Limit for more smoothing when phase activity is weak."
trendTip: str = "Trend Length controls the EMA centerline, while Volatility Length controls how much return history is used for the adaptive bands. Increase Trend Length for a smoother centerline and increase Volatility Length for steadier band width."
bandTip: str = "Active Multiplier controls band width when phase activity is strong, while Slow Multiplier controls band width when phase activity is weak. Lower Active Multiplier for faster regime changes during active markets, and increase Slow Multiplier to require larger moves during quieter conditions."
colorTip: str = "Bullish Color is used for bullish regimes and LONG signals, while Bearish Color is used for bearish regimes and SHORT signals."


@script.indicator("MESA Phase-Adaptive Band Trend", overlay=True)
def main(
    src: Series[float] = input.source(title="Source", defval=hl2, group="Phase Settings", tooltip="Choose the price source used to estimate Hilbert phase behavior and calculate the trend."),
    fastLimit=input.float(title="Fast Limit", defval=0.5, minval=0.01, maxval=1.0, step=0.01, group="Phase Settings", inline="P1", tooltip=phaseTip),
    slowLimit=input.float(title="Slow Limit", defval=0.05, minval=0.001, maxval=1.0, step=0.001, group="Phase Settings", inline="P1", tooltip=phaseTip),
    trendLength=input.int(title="Trend Length", defval=20, minval=2, group="Trend Settings", inline="T1", tooltip=trendTip),
    volLength=input.int(title="Volatility Length", defval=20, minval=2, group="Trend Settings", inline="T1", tooltip=trendTip),
    activeMult=input.float(title="Active Multiplier", defval=1.5, minval=0.1, step=0.1, group="Adaptive Bands", inline="B1", tooltip=bandTip),
    slowMult=input.float(title="Slow Multiplier", defval=3.0, minval=0.1, step=0.1, group="Adaptive Bands", inline="B1", tooltip=bandTip),
    showBands=input.bool(title="Show Bands", defval=True, group="Visualization", tooltip="Show or hide the phase-responsive volatility bands. Turning this off only changes the chart display and does not affect the trend or signal calculations."),
    showFill=input.bool(title="Show Fill", defval=True, group="Visualization", tooltip="Show or hide the shaded area between the upper and lower adaptive bands. This is visual only and does not change the indicator calculations."),
    showSignals=input.bool(title="Show Signals", defval=True, group="Visualization", tooltip="Show or hide LONG and SHORT markers when the active trend regime changes. Turning this off does not change the underlying regime calculation."),
    colorBars=input.bool(title="Color Bars", defval=True, group="Visualization", tooltip="Color the price candles according to the currently active trend regime. Turning this off only removes candle coloring and does not affect signals."),
    longColor=input.color(title="Bullish Color", defval=color.rgb(57, 255, 20), group="Color Settings", inline="C1", tooltip=colorTip),
    shortColor=input.color(title="Bearish Color", defval=color.rgb(138, 43, 226), group="Color Settings", inline="C1", tooltip=colorTip)
):
    smooth: Series[float] = (4.0 * src + 3.0 * nz(src[1], src) + 2.0 * nz(src[2], src) + nz(src[3], src)) / 10.0
    period: PersistentSeries[float] = 10.0
    periodFactor: float = 0.075 * nz(period[1], 10.0) + 0.54

    detrender: Series[float] = (0.0962 * smooth + 0.5769 * nz(smooth[2]) - 0.5769 * nz(smooth[4]) - 0.0962 * nz(smooth[6])) * periodFactor
    q1: Series[float] = (0.0962 * detrender + 0.5769 * nz(detrender[2]) - 0.5769 * nz(detrender[4]) - 0.0962 * nz(detrender[6])) * periodFactor
    i1: Series[float] = nz(detrender[3])

    jI: float = (0.0962 * i1 + 0.5769 * nz(i1[2]) - 0.5769 * nz(i1[4]) - 0.0962 * nz(i1[6])) * periodFactor
    jQ: float = (0.0962 * q1 + 0.5769 * nz(q1[2]) - 0.5769 * nz(q1[4]) - 0.0962 * nz(q1[6])) * periodFactor

    i2Raw: float = i1 - jQ
    q2Raw: float = q1 + jI

    i2: PersistentSeries[float] = 0.0
    q2: PersistentSeries[float] = 0.0

    i2 = 0.2 * i2Raw + 0.8 * nz(i2[1])
    q2 = 0.2 * q2Raw + 0.8 * nz(q2[1])

    reRaw: float = i2 * nz(i2[1]) + q2 * nz(q2[1])
    imRaw: float = i2 * nz(q2[1]) - q2 * nz(i2[1])

    re: PersistentSeries[float] = 0.0
    im: PersistentSeries[float] = 0.0

    re = 0.2 * reRaw + 0.8 * nz(re[1])
    im = 0.2 * imRaw + 0.8 * nz(im[1])

    angle: float = math.atan(im / re) * 180.0 / math.pi if re != 0.0 else 0.0
    rawPeriod: float = math.abs(360.0 / angle) if angle != 0.0 else nz(period[1], 10.0)
    previousPeriod: float = nz(period[1], 10.0)
    limitedPeriod: float = math.min(rawPeriod, 1.5 * previousPeriod)

    limitedPeriod = math.max(limitedPeriod, 0.67 * previousPeriod)
    limitedPeriod = math.max(6.0, math.min(50.0, limitedPeriod))
    period = 0.2 * limitedPeriod + 0.8 * previousPeriod

    phase: PersistentSeries[float] = 0.0
    phase = math.atan(q1 / i1) * 180.0 / math.pi if i1 != 0.0 else nz(phase[1])

    deltaPhase: float = nz(phase[1]) - phase
    deltaPhase = math.max(deltaPhase, 1.0)

    alphaPhase: float = fastLimit / deltaPhase
    alphaPhase = math.max(alphaPhase, slowLimit)

    phaseRange: float = math.max(fastLimit - slowLimit, 0.0001)
    phaseActivity: float = math.max(0.0, math.min(1.0, (alphaPhase - slowLimit) / phaseRange))

    trend: float = ta.ema(src, trendLength)
    priceReturn: float = (src - src[1]) / src[1] if src[1] != 0.0 else 0.0
    volatility: float = inline_series(ta.stdev(priceReturn, volLength), 1)

    adaptiveMult: float = slowMult - (slowMult - activeMult) * phaseActivity
    upperBand: float = trend + adaptiveMult * volatility * trend
    lowerBand: float = trend - adaptiveMult * volatility * trend

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

    plot(trend, title='Trend', color=col, linewidth=2)
    upperPlot = plot(upperBand if showBands else na, title='Upper Phase Band', color=color.new(longColor, 35), linewidth=1)
    lowerPlot = plot(lowerBand if showBands else na, title='Lower Phase Band', color=color.new(shortColor, 35), linewidth=1)
    fill(upperPlot, lowerPlot, title='Phase Band Fill', color=color.new(col, 90) if showFill else na)
    plotshape(showSignals and longSignal, title='Long Signal', style=shape.triangleup, location=location.belowbar, color=longColor, size=size.small, text='LONG', textcolor=color.white)
    plotshape(showSignals and shortSignal, title='Short Signal', style=shape.triangledown, location=location.abovebar, color=shortColor, size=size.small, text='SHORT', textcolor=color.white)
    barcolor(col if colorBars else na)

    alertcondition(longSignal, title='Long Signal', message='Phase-Responsive Band Trend Long Signal on {{ticker}}')
    alertcondition(shortSignal, title='Short Signal', message='Phase-Responsive Band Trend Short Signal on {{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)