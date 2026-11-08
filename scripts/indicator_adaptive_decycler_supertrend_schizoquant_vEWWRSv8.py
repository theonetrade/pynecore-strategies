"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_float
from pynecore.lib import (
    alertcondition, barcolor, close, color, display, fill, input, location,
    math, na, nz, plot, plotshape, script, shape, size, syminfo, ta
)
from pynecore.types import Color, PersistentSeries, Series

cutoffTip: str = "Minimum Cutoff sets the fastest Decycler response used during cleaner directional movement, while Maximum Cutoff sets the slowest response used during noisier conditions. Lower the minimum for faster reactions or increase the maximum for stronger smoothing."
efficiencyTip: str = "Sets the lookback used to measure directional efficiency by comparing net price movement with the total distance travelled. Higher efficiency moves the adaptive Decycler toward the faster cutoff, while lower efficiency moves it toward the slower cutoff."
rmsTip: str = "Sets the lookback used to measure the root-mean-square energy of price displacement from the adaptive Decycler. Increase it for steadier bands or decrease it for faster adaptation to changes in residual movement."
bandTip: str = "Upper Multiplier controls the RMS distance above the adaptive Decycler, while Lower Multiplier controls the distance below it. Increase either multiplier to widen that side of the Supertrend structure and require a larger move before a reversal."
colorTip: str = "Bullish Color represents bullish Supertrend regimes, LONG signals, and bullish visual elements, while Bearish Color represents bearish Supertrend regimes, SHORT signals, and bearish visual elements."


@script.indicator("Adaptive Decycler Supertrend", overlay=True)
def main(
    src: Series[float] = input.source(title="Source", defval=close, group="Adaptive Decycler", tooltip="Choose the price source used by the adaptive Decycler, efficiency calculation, residual measurement, and Supertrend regime logic."),
    minimumCutoff=input.int(title="Minimum Cutoff", defval=15, minval=6, group="Adaptive Decycler", inline="D1", tooltip=cutoffTip),
    maximumCutoff=input.int(title="Maximum Cutoff", defval=50, minval=7, group="Adaptive Decycler", inline="D1", tooltip=cutoffTip),
    efficiencyLength=input.int(title="Efficiency Length", defval=10, minval=2, group="Adaptive Decycler", tooltip=efficiencyTip),
    rmsLength=input.int(title="Residual RMS Length", defval=20, minval=2, group="Supertrend Bands", tooltip=rmsTip),
    upperMultiplier=input.float(title="Upper Multiplier", defval=2.0, minval=0.1, step=0.1, group="Supertrend Bands", inline="B1", tooltip=bandTip),
    lowerMultiplier=input.float(title="Lower Multiplier", defval=2.6, minval=0.1, step=0.1, group="Supertrend Bands", inline="B1", tooltip=bandTip),
    showDecycler=input.bool(title="Show Decycler", defval=True, group="Visualization", tooltip="Show or hide the adaptive Decycler baseline. Turning this off only changes the chart display and does not affect the Supertrend calculations or signals."),
    showEnvelope=input.bool(title="Show RMS Envelope", defval=False, group="Visualization", tooltip="Show or hide the upper and lower residual RMS bands. Turning this off only changes the chart display and does not affect regime calculations."),
    showFill=input.bool(title="Show Envelope Fill", defval=True, group="Visualization", tooltip="Show or hide the shaded region between the RMS bands when the envelope is visible. This is visual only and does not affect the indicator calculations."),
    showSignals=input.bool(title="Show Signals", defval=True, group="Visualization", tooltip="Show or hide LONG and SHORT markers whenever the active Supertrend regime changes. Turning this off does not change the underlying regime calculation."),
    colorBars=input.bool(title="Color Bars", defval=True, group="Visualization", tooltip="Color price candles according to the active Supertrend regime. Turning this off only removes candle coloring and does not affect signals."),
    longColor=input.color(title="Bullish Color", defval=color.rgb(57, 255, 20), group="Color Settings", inline="C1", tooltip=colorTip),
    shortColor=input.color(title="Bearish Color", defval=color.rgb(138, 43, 226), group="Color Settings", inline="C1", tooltip=colorTip)
):
    fastLimit: int = math.min(minimumCutoff, maximumCutoff)
    slowLimit: int = math.max(minimumCutoff, maximumCutoff)

    direction: float = math.abs(src - nz(src[efficiencyLength], src))
    noise: float = 0.0

    for i in pine_range(0, efficiencyLength - 1):
        noise += math.abs(nz(src[i], src) - nz(src[i + 1], src))

    efficiency: float = direction / noise if noise > 0.0 else 0.0
    efficiency = math.max(0.0, math.min(1.0, efficiency))

    adaptiveCutoff: float = cast_float(slowLimit) - efficiency * cast_float(slowLimit - fastLimit)

    angle: float = 2.0 * math.pi / adaptiveCutoff
    cosineValue: float = math.cos(angle)
    alpha: float = (cosineValue + math.sin(angle) - 1.0) / cosineValue if math.abs(cosineValue) > 1e-06 else 1.0
    alpha = math.max(0.0, math.min(1.0, alpha))

    decycler: PersistentSeries[float] = na(float)
    decycler = src if na(decycler[1]) else alpha * 0.5 * (src + nz(src[1], src)) + (1.0 - alpha) * decycler[1]

    residual: float = src - decycler
    residualEnergy: float = ta.sma(residual * residual, rmsLength)
    residualRMS: float = math.sqrt(math.max(nz(residualEnergy, 0.0), 0.0))
    residualRMS = math.max(residualRMS, syminfo.mintick)

    upperEnvelope: float = decycler + residualRMS * upperMultiplier
    lowerEnvelope: float = decycler - residualRMS * lowerMultiplier

    SQ: PersistentSeries[int] = 1 if src >= decycler else -1
    trendTrail: PersistentSeries[float] = na(float)

    previousSQ: int = nz(SQ[1], SQ)
    previousTrail: float = nz(trendTrail[1], lowerEnvelope if previousSQ == 1 else upperEnvelope)

    long: bool = previousSQ == -1 and src > previousTrail
    short: bool = previousSQ == 1 and src < previousTrail

    if long:
        SQ = 1
    elif short:
        SQ = -1
    else:
        SQ = previousSQ

    if SQ == 1:
        trendTrail = lowerEnvelope if long else math.max(lowerEnvelope, previousTrail)
    else:
        trendTrail = upperEnvelope if short else math.min(upperEnvelope, previousTrail)

    longSignal: bool = SQ == 1 and nz(SQ[1], SQ) != 1
    shortSignal: bool = SQ == -1 and nz(SQ[1], SQ) != -1

    col: Color = longColor if SQ == 1 else shortColor

    plot(trendTrail if SQ == 1 else na, title='Bullish Supertrend', color=longColor, linewidth=2, style=plot.style_linebr)
    plot(trendTrail if SQ == -1 else na, title='Bearish Supertrend', color=shortColor, linewidth=2, style=plot.style_linebr)
    plot(decycler if showDecycler else na, title='Adaptive Decycler', color=color.new(col, 35), linewidth=2)
    upperPlot = plot(upperEnvelope if showEnvelope else na, title='Upper RMS Band', color=color.new(shortColor, 70), linewidth=1)
    lowerPlot = plot(lowerEnvelope if showEnvelope else na, title='Lower RMS Band', color=color.new(longColor, 70), linewidth=1)
    fill(upperPlot, lowerPlot, title='RMS Band Fill', color=color.new(col, 93) if showFill and showEnvelope else na)
    plot(efficiency, title='Efficiency', display=display.data_window)
    plot(adaptiveCutoff, title='Adaptive Cutoff', display=display.data_window)
    plot(residual, title='Decycler Residual', display=display.data_window)
    plot(residualRMS, title='Residual RMS', display=display.data_window)
    plotshape(showSignals and longSignal, title='Long Signal', style=shape.triangleup, location=location.belowbar, size=size.small, color=longColor, text='LONG', textcolor=color.white)
    plotshape(showSignals and shortSignal, title='Short Signal', style=shape.triangledown, location=location.abovebar, size=size.small, color=shortColor, text='SHORT', textcolor=color.white)
    barcolor(col if colorBars else na)

    alertcondition(longSignal, title='Long Signal', message='Adaptive Decycler Supertrend Long Signal on {{ticker}}')
    alertcondition(shortSignal, title='Short Signal', message='Adaptive Decycler Supertrend Short Signal on {{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)