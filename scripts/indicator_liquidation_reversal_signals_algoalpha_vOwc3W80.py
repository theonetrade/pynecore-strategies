"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, chart, close, color, display, fill, high,
    input, location, low, math, na, open, plot, plotcandle, plotchar, plotshape, position, script,
    shape, size, ta, table, volume
)
from pynecore.types import Persistent, PersistentSeries, Table
import lib.TradingView.ta.v10 as tvta


@script.indicator("Liquidation Reversal Signals [AlgoAlpha]", "AlgoAlpha - Liquidation Reversal", True, max_lines_count=500, behind_chart=False)
def main(
    lowerTF=input.timeframe("15", title="Lower Timeframe", group="Data", tooltip="Lower timeframe used by the up/down volume request."),
    length=input.int(200, "Z Score Length", minval=1, group="Z-Score", tooltip="Lookback length for mean and standard deviation when computing z-scores of up/down volume."),
    zThresh=input.float(3.0, "Z-Score Threshold", minval=0.0, step=0.1, group="Z-Score", tooltip="Minimum z-score required to register a liquidation spike."),
    timeoutBars=input.int(50, "Liquidation Timeout Bars (0 = none)", minval=0, group="Detection", tooltip="Maximum bars between a qualifying liquidation and the Supertrend flip. Set 0 to disable the timeout."),
    green=input.color(color.new('#00FFBB'), title="Bullish Colour", group="Appearance", tooltip="Color used for bullish visuals and positive sentiment texts."),
    red=input.color(color.new('#FF1100'), title="Bearish Colour", group="Appearance", tooltip="Color used for bearish visuals and negative sentiment texts.")
):
    u, d, _ = tvta.requestUpAndDownVolume(lowerTF)
    d = -d

    meanU = ta.sma(u, length)
    stdevU = ta.stdev(u, length)
    zU = (u - meanU) / stdevU if stdevU != 0 else na

    meanD = ta.sma(d, length)
    stdevD = ta.stdev(d, length)
    zD = (d - meanD) / stdevD if stdevD != 0 else na

    supertrend, direction = ta.supertrend(2, 10)
    shortLiq = direction < 0 and zU > zThresh
    longLiq = direction > 0 and zD > zThresh

    lastliqdir: Persistent[int] = 0
    lastliqindex: Persistent[int] = 0
    valid: Persistent[int] = 0

    plottrnd: PersistentSeries[int] = 0
    if ta.cross(direction, 0):
        plottrnd = 0
    if ta.crossunder(direction, 0) and lastliqdir == 1 and (valid == 1):
        if bar_index - lastliqindex < timeoutBars:
            plottrnd = 1
        valid = 0
    if ta.crossover(direction, 0) and lastliqdir == -1 and (valid == 1):
        if bar_index - lastliqindex < timeoutBars:
            plottrnd = -1
        valid = 0

    if shortLiq:
        lastliqdir = -1
        lastliqindex = bar_index
        valid = 1
    if longLiq:
        lastliqdir = 1
        lastliqindex = bar_index
        valid = 1

    x: int = 7
    lw = ta.lowest(x)
    hg = ta.highest(x)
    newBullSt = plottrnd == -1 and plottrnd[1] != -1
    newBearSt = plottrnd == 1 and plottrnd[1] != 1

    vola = ta.atr(14)
    zMagShort = math.abs(zU)
    zMagLong = math.abs(zD)

    normShort = math.min(math.max((zMagShort - zThresh) / 5, 0), 1)
    normLong = math.min(math.max((zMagLong - zThresh) / 5, 0), 1)
    transpMax: int = 70
    transpMin: int = 30
    transpShort = math.round(transpMax - normShort * (transpMax - transpMin))
    transpLong = math.round(transpMax - normLong * (transpMax - transpMin))
    colShort = color.new(green, transpShort)
    colLong = color.new(red, transpLong)
    candleCol = color.from_gradient(50, 0, 100, red, chart.bg_color) if plottrnd == -1 else color.from_gradient(50, 0, 100, green, chart.bg_color) if plottrnd == 1 else color.new(green, 100)

    midBody = math.avg(open, close)
    midPlot = plot(midBody, title='Mid Body', display=display.none)

    stBull = plot(supertrend if plottrnd == -1 else na, 'Bullish Trend', red, style=plot.style_linebr)
    stBear = plot(supertrend if plottrnd == 1 else na, 'Bearish Trend', green, style=plot.style_linebr)

    fill(midPlot, stBull, color.new(red, 90), title='Bullish Fill')
    fill(midPlot, stBear, color.new(green, 90), title='Bearish Fill')
    plotshape(newBullSt, 'Bullish ST Start', shape.labeldown, location.abovebar, color.new(red, 30), text='▼', textcolor=chart.fg_color, size=size.tiny)
    plotshape(newBearSt, 'Bearish ST Start', shape.labelup, location.belowbar, color.new(green, 30), text='▲', textcolor=chart.fg_color, size=size.tiny)
    plotchar(high + vola if shortLiq else na, 'Short Liquidation', '●', location.absolute, colShort, size=size.tiny)
    plotchar(low - vola if longLiq else na, 'Long Liquidation', '●', location.absolute, colLong, size=size.tiny)
    plotcandle(open, high, low, close, 'Candles', candleCol, candleCol, bordercolor=candleCol)

    alertcondition(newBullSt, title='Bullish ST Start', message='Bullish supertrend became visible after qualifying liquidation and confirmation.')
    alertcondition(newBearSt, title='Bearish ST Start', message='Bearish supertrend became visible after qualifying liquidation and confirmation.')
    alertcondition(shortLiq, title='Short Liquidation Spike', message='Short-side liquidation detected (zU > threshold).')
    alertcondition(longLiq, title='Long Liquidation Spike', message='Long-side liquidation detected (zD > threshold).')

    warnTbl: Persistent[Table] = table.new(position.middle_right, 1, 1)
    noVol = na(volume) or volume == 0 or (na(u) and na(d))
    table.cell(warnTbl, 0, 0, 'No Volume' if noVol else '', text_color=color.white if noVol else color.new(chart.fg_color, 100), bgcolor=color.new(red, 0) if noVol else color.new(chart.bg_color, 100))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
