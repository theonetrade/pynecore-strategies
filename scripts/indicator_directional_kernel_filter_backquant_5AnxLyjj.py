"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, bgcolor, chart, close, color, display, fill, high, input,
    low, math, na, nz, open, plot, plotcandle, script, syminfo, ta
)
from pynecore.types import Color, PersistentSeries, Series

calc: str = "Core Calculation Settings"
ui: str = "Plotting and Coloring"
GREEN: Color = color.new('#00FF00')
RED: Color = color.new('#FF0000')


@script.indicator("Directional Kernel Filter [BackQuant]", shorttitle="Directional Kernel [BackQuant]", overlay=True)
def main(
    src: Series[float] = input.source(close, "Source", group=calc),
    fastLen=input.int(18, "Fast Kernel Length", minval=3, group=calc, inline="LEN"),
    slowLen=input.int(35, "Slow", minval=5, group=calc, inline="LEN"),
    kernelWidth=input.float(0.35, "Kernel Width", minval=0.05, maxval=1.0, step=0.05, group=calc, tooltip="Controls the Gaussian kernel bandwidth relative to the filter length. Lower values concentrate weight near the current bar."),
    directionStrength=input.float(3.5, "Directional Weight", minval=0.0, maxval=5.0, step=0.1, group=calc, tooltip="Controls how strongly observations agreeing with the previously estimated direction are favored. 0 disables directional weighting."),
    normLen=input.int(14, "Normalization Length", minval=2, group=calc, tooltip="ATR length used to normalize directional price movement across assets and volatility regimes."),
    longCol=input.color(GREEN, "Long Color", group=ui, inline="COL"),
    shortCol=input.color(RED, "Short Color", group=ui, inline="COL"),
    lineW=input.int(3, "Line Width", minval=1, maxval=6, group=ui),
    showRibbon=input.bool(True, "Show Trend Ribbon?", group=ui),
    showBase=input.bool(False, "Show Base Kernel?", group=ui),
    paintCandles=input.bool(False, "Paint Candles to Trend?", group=ui),
    bgCol=input.bool(False, "Background Color?", group=ui)
):
    def directionalKernel(source: Series[float], length: int, width: float, strength: float, norm: Series[float]):
        bandwidth: float = math.max(1.0, length * width)

        baseWeighted: float = 0.0
        baseWeights: float = 0.0

        for i in pine_range(0, length - 1):
            if not na(source[i]):
                distance: float = i / bandwidth
                kernelWeight: float = math.exp(-0.5 * distance * distance)
                baseWeighted += source[i] * kernelWeight
                baseWeights += kernelWeight

        base: Series[float] = baseWeighted / baseWeights if baseWeights > 0.0 else na

        priorDirection: float = nz(base[1] - base[2])
        priorNorm: float = priorDirection / math.max(nz(norm[1], norm), syminfo.mintick)
        priorNorm = math.max(-1.0, math.min(1.0, priorNorm))

        weightedPrice: float = 0.0
        totalWeight: float = 0.0

        for i in pine_range(0, length - 1):
            if not na(source[i]):
                distance: float = i / bandwidth
                kernelWeight: float = math.exp(-0.5 * distance * distance)

                localMove: float = source[i] - source[i + 1] if i < length - 1 else 0.0
                localNorm: float = localMove / math.max(nz(norm[i], norm), syminfo.mintick)
                localNorm = math.max(-1.0, math.min(1.0, localNorm))

                alignment: float = priorNorm * localNorm
                exponent: float = math.max(-3.0, math.min(3.0, strength * alignment))
                directionWeight: float = math.exp(exponent)

                weight: float = kernelWeight * directionWeight

                weightedPrice += source[i] * weight
                totalWeight += weight

        filtered: float = weightedPrice / totalWeight if totalWeight > 0.0 else base

        return (filtered, base, priorNorm)

    atr: float = ta.atr(normLen)

    fastKernel, fastBase, fastDirection = directionalKernel(src, fastLen, kernelWidth, directionStrength, atr)
    slowKernel, slowBase, slowDirection = directionalKernel(src, slowLen, kernelWidth, directionStrength, atr)

    bullish: bool = fastKernel > slowKernel
    bearish: bool = fastKernel < slowKernel

    trend: PersistentSeries[int] = 0

    if bullish:
        trend = 1
    elif bearish:
        trend = -1

    col: Color = longCol if trend == 1 else shortCol

    pFast = plot(fastKernel, 'Fast Directional Kernel', col, lineW)
    pSlow = plot(slowKernel if showRibbon else na, 'Slow Directional Kernel', color.new(col, 60), 2)

    fill(pFast, pSlow, color.new(col, 82) if showRibbon else na, title='Directional Kernel Ribbon')

    plot(fastBase if showBase else na, 'Base Gaussian Kernel', color.new(chart.fg_color, 60), 1)

    plotcandle(open, high, low, close, 'Trend Candles', col, col, True, bordercolor=col, display=display.all if paintCandles else display.none)

    bgcolor(color.new(col, 90) if bgCol else na)

    plot(fastDirection, 'Fast Reference Direction', display=display.data_window)
    plot(slowDirection, 'Slow Reference Direction', display=display.data_window)
    plot(fastKernel - fastBase, 'Directional Adjustment', display=display.data_window)
    plot(fastKernel - slowKernel, 'Kernel Spread', display=display.data_window)

    bullFlip: bool = trend == 1 and trend[1] == -1
    bearFlip: bool = trend == -1 and trend[1] == 1

    alertcondition(bullFlip, title='Directional Kernel Bullish', message='Directional Kernel Trend Filter turned bullish {{exchange}}:{{ticker}}')
    alertcondition(bearFlip, title='Directional Kernel Bearish', message='Directional Kernel Trend Filter turned bearish {{exchange}}:{{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)