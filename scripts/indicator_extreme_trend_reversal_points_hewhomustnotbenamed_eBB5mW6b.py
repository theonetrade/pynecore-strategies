"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_float
from pynecore.lib import (
    alertcondition, array, barstate, close, color, display, input, location,
    math, matrix, order, plot, plotshape, script, shape, size, string, ta
)
from pynecore.types import Label, Line, Matrix, Persistent, Series
import lib.HeWhoMustNotBeNamed._matrix.v5 as ma
import lib.HeWhoMustNotBeNamed.arrays.v1 as pa
import lib.HeWhoMustNotBeNamed.arrayutils.v21 as ar
import lib.HeWhoMustNotBeNamed.drawingutils.v8 as dr
import lib.HeWhoMustNotBeNamed.enhanced_ta.v14 as eta


@script.indicator('Extreme Trend Reversal Points [HeWhoMustNotBeNamed]', shorttitle='ETRP[HWMNBN]', overlay=True, na_bool=True)
def main(
    source: Series[float] = input.source(close, 'Source', group='Moving Average'),
    type=input.string('sma', 'Type', options=('sma', 'ema', 'rma', 'wma'), group='Moving Average'),
    length=input.int(20, 'Length', step=5, group='Moving Average'),
    level=input.int(10, 'Level', minval=5, step=5, group='Moving Average'),
    minMaxRangePercentile=input.int(20, 'Range Percentile', minval=5, maxval=45, step=5),
    extremeMinMaxRangePercentile=input.int(45, 'Extreme Range Percentile', minval=40, maxval=48, step=2),
    history=input.int(1000, 'Percentile History', minval=1000, maxval=5000, step=500),
    realTimeAlerts=input.bool(False, 'Real Time Alerts', tooltip='If set to true, alerts are fired on latest candle - which may repaint. For safer option set this to false')
):
    maxHistory = length - 1
    def ema(currentEma: float, source: float, length: int):
        k = 2 / (length + 1)
        ema__0000000a__ = source * k + (1 - k) * currentEma
        return ema__0000000a__

    def rma(currentRma: float, source: float, length: int):
        k = 2 / (length + 1)
        rma__0000000b__ = (currentRma * (length - 1) + source) / length
        return rma__0000000b__

    maMatrix: Persistent[Matrix[float]] = matrix.new(1, level + 1, cast_float(source))
    if type == 'ema':
        emaArray: list[float] = array.new_float(1, source)
        for i in pine_range(1, matrix.columns(maMatrix) - 1, 1):
            ema__00000014__ = ema(matrix.get(maMatrix, 0, i), array.get(emaArray, array.size(emaArray) - 1), length)
            array.push(emaArray, ema__00000014__)
        ma.unshift(maMatrix, emaArray, maxHistory)
    if type == 'rma':
        rmaArray: list[float] = array.new_float(1, source)
        for i in pine_range(1, matrix.columns(maMatrix) - 1, 1):
            rma__0000001e__ = rma(matrix.get(maMatrix, 0, i), array.get(rmaArray, array.size(rmaArray) - 1), length)
            array.push(rmaArray, rma__0000001e__)
        ma.unshift(maMatrix, rmaArray, maxHistory)
    if type == 'sma' or type == 'wma':
        maArray: list[float] = array.new_float(1, source)
        __loop_1__ = pine_loop(1, 1)
        while __loop_1__.step(matrix.columns(maMatrix) - 1):
            i = __loop_1__.value
            values = matrix.col(maMatrix, i - 1)
            tmpArray: list[float] = array.new_float(1, array.get(maArray, i - 1))
            tmpArray = array.concat(tmpArray, values)
            array.push(maArray, ar.ma(tmpArray, type, length))
        ma.unshift(maMatrix, maArray, maxHistory)
    strength: Series[int] = 0
    bearishStrength: int = 0
    diffMatrix: Matrix[float] = matrix.new(level + 1, level + 1, 0.0)
    linesArray: Persistent[list[Line]] = array.new_line()
    labelsArray: Persistent[list[Label]] = array.new_label()
    ar.clear(linesArray)
    ar.clear(labelsArray)
    for i in pine_range(0, level, 1):
        for j in pine_range(0, level, 1):
            pma = matrix.get(maMatrix, 0, i)
            nma = matrix.get(maMatrix, 0, j)
            if j > i:
                strength = strength + 1 if pma > nma else strength
            matrix.set(diffMatrix, i, j, math.sign(pma - nma))
    lastRow = matrix.row(maMatrix, 0)
    lastRowIndex = array.sort_indices(array.slice(lastRow, 1, array.size(lastRow)), order.descending)
    if barstate.islast:
        for i in pine_range(1, level, 1):
            levelColor = color.from_gradient(i, 1, level, color.green, color.red)
            dr.draw_labelled_line(array.get(lastRow, i), type + '(' + string.tostring(i) + ')', levelColor, levelColor, 0, True, linesArray, labelsArray)
    minRange = ta.percentile_nearest_rank(strength, history, 50 - minMaxRangePercentile)
    maxRange = ta.percentile_nearest_rank(strength, history, 50 + minMaxRangePercentile)
    extremeMinRange = ta.percentile_nearest_rank(strength, history, 50 - extremeMinMaxRangePercentile)
    extremeMaxRange = ta.percentile_nearest_rank(strength, history, 50 + extremeMinMaxRangePercentile)
    plotColor = color.green if strength > extremeMaxRange else color.lime if strength > maxRange else color.red if strength < extremeMinRange else color.orange if strength < minRange else color.silver
    strengthRange = 2 if strength > extremeMaxRange else 1 if strength > maxRange else 0 if strength > minRange else -1 if strength < extremeMinRange else -2
    maxStrength = level * (level + 1) / 2
    ma__global__ = eta.ma(source, type, length)
    crossunder_1 = ta.crossunder(source, ma__global__)
    bullishTrendReversalPoint: Series = strength[1] == maxStrength and crossunder_1
    crossover_1 = ta.crossover(source, ma__global__)
    bearishTrendReversalPoint: Series = strength[1] == 0 and crossover_1
    plotshape(bullishTrendReversalPoint, 'Bullish Trend Reversal Point', style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small)
    plotshape(bearishTrendReversalPoint, 'Bearish Trend Reversal Point', style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small)
    plot(strength, 'Strength', color=color.silver, display=display.data_window)
    plot(minRange, 'Min Range', color=color.orange, display=display.data_window)
    plot(maxRange, 'Max Range', color=color.lime, display=display.data_window)
    plot(extremeMinRange, 'Extreme Min Range', color=color.red, display=display.data_window)
    plot(extremeMaxRange, 'Extreme Max Range', color=color.green, display=display.data_window)
    plot(strengthRange, 'Strength Range', color=color.blue, display=display.data_window)
    plot(ma__global__, 'Moving Average', plotColor)
    alertcondition(bullishTrendReversalPoint[0 if realTimeAlerts else 1], 'Bullish Trend Reversal', 'Possible reversal of bullish trend')
    alertcondition(bearishTrendReversalPoint[0 if realTimeAlerts else 1], 'Bearish Trend Reversal', 'Possible reversal of bearish trend')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)