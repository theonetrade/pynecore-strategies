"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, bgcolor, chart, close, color,
    display, extend, high, input, last_bar_index, line, location, low, math, na, nz, open, plot,
    plotcandle, plotshape, script, shape, size, syminfo
)
from pynecore.types import Color, PersistentSeries, Series

calc: str = "Core Calculation Settings"
thres: str = "Signal Settings"
ui: str = "Plotting and Coloring"
GREEN: Color = color.new('#00FF00')
RED: Color = color.new('#FF0000')


@script.indicator("MAD Adaptive Trend Score [BackQuant]", shorttitle="MAD Trend Score [BackQuant]", overlay=False)
def main(
    src: Series[float] = input.source(close, "Source", group=calc),
    madLen=input.int(15, "MAD Length", minval=3, group=calc, tooltip="Length used for the rolling median and Median Absolute Deviation."),
    madMult=input.float(5.2, "MAD Multiplier", minval=0.1, step=0.1, group=calc, tooltip="Controls how far price may move away from the rolling median. Lower values suppress more noise. Higher values follow price more closely."),
    scoreStart=input.int(1, "Score Lookback Start", inline="SL", group=calc),
    scoreEnd=input.int(45, "End", maxval=50, inline="SL", group=calc, tooltip="Range of bars used for the directional persistence score."),
    showRefs=input.bool(True, "Show Reference Lines", group=thres),
    showSignals=input.bool(True, "Show Signals on Chart?", group=thres),
    longThres=input.int(40, "Long Threshold", group=thres, inline="TH"),
    shortThres=input.int(-6, "Short Threshold", group=thres, inline="TH"),
    longCol=input.color(GREEN, "Long Color", group=ui, inline="col"),
    shortCol=input.color(RED, "Short Color", group=ui, inline="col"),
    lineW=input.int(5, "Line Width", group=ui),
    showSmooth=input.bool(False, "Show MAD Filter on Chart?", group=ui),
    paintCandles=input.bool(True, "Paint Candles to Trend?", group=ui),
    bgCol=input.bool(False, "Background Color?", group=ui)
):
    @method
    def transp(x: Color, t: int):
        return color.new(x, t)

    def madStats(source: Series[float], length: int):
        values: list[float] = array.new_float()

        for i in pine_range(0, length - 1):
            if not na(source[i]):
                array.push(values, source[i])

        median: float = array.median(values) if array.size(values) > 0 else na
        deviations: list[float] = array.new_float()

        if not na(median):
            for i in pine_range(0, array.size(values) - 1):
                array.push(deviations, math.abs(array.get(values, i) - median))

        mad: float = array.median(deviations) if array.size(deviations) > 0 else na
        return (median, mad)

    medianValue, rawMad = madStats(src, madLen)

    scaledMad: float = math.max(rawMad * 1.4826, syminfo.mintick)

    deviation: float = src - medianValue
    maxDeviation: float = scaledMad * madMult
    clippedDeviation: float = math.max(-maxDeviation, math.min(maxDeviation, deviation))

    madFilt: Series[float] = medianValue + clippedDeviation

    scoreS: Series[float] = 0.0

    for i in pine_range(scoreStart, scoreEnd):
        scoreS += 1.0 if madFilt > madFilt[i] else -1.0

    signal: PersistentSeries[int] = 0

    prevScore: float = nz(scoreS[1], scoreS)
    longCond: bool = scoreS > longThres
    shortCond: bool = prevScore >= shortThres and scoreS < shortThres

    if longCond and (not shortCond):
        signal = 1
    elif shortCond:
        signal = -1

    col: Color = longCol if signal == 1 else shortCol

    plot(scoreS, 'Trend Score', col, lineW)

    if barstate.islast and showRefs:
        line.new(last_bar_index, longThres, bar_index - 1, longThres, color=transp(chart.fg_color, 50), style=line.style_dashed, extend=extend.right)
        line.new(last_bar_index, shortThres, bar_index - 1, shortThres, color=transp(chart.fg_color, 50), style=line.style_dashed, extend=extend.right)

    plot(madFilt, 'MAD Adaptive Filter', col, 2, plot.style_line, force_overlay=True, display=display.all if showSmooth else display.none)

    plotcandle(open, high, low, close, 'Trend Candles', col, col, True, bordercolor=col, display=display.all if paintCandles else display.none, force_overlay=True)

    bgcolor(transp(col, 80) if bgCol else na, force_overlay=True)

    plotshape(signal == 1 and signal[1] == -1, 'Long Signal', shape.triangleup, location.belowbar, longCol, 0, '𝕃', longCol, True, size.small, display=display.all if showSignals else display.none, force_overlay=True)

    plotshape(signal == -1 and signal[1] == 1, 'Short Signal', shape.triangledown, location.abovebar, shortCol, 0, '𝕊', shortCol, True, size.small, display=display.all if showSignals else display.none, force_overlay=True)

    plot(medianValue, 'Rolling Median', display=display.data_window)
    plot(rawMad, 'Raw MAD', display=display.data_window)
    plot(scaledMad, 'Scaled MAD', display=display.data_window)

    alertcondition(signal == 1 and signal[1] == -1, title='MAD Trend Score Long', message='MAD Adaptive Trend Score Long {{exchange}}:{{ticker}}')
    alertcondition(signal == -1 and signal[1] == 1, title='MAD Trend Score Short', message='MAD Adaptive Trend Score Short {{exchange}}:{{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
