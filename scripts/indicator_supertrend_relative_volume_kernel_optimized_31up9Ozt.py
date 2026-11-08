"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_import import shadowed_namespace
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, barstate, close, color,
    display, fill, high, input, label, last_bar_index, location, log, low, math, na, open, plot,
    plotshape, position, script, shape, size, string, syminfo, ta, table, volume, yloc
)
from pynecore.types import Color, Persistent, PersistentSeries, Table
import lib.TradingView.ta.v9 as ta__ren____lib


ta__ren__ = shadowed_namespace(ta__ren____lib, ta)


@udt
class KDE:
    mid: float = na(float)
    X: list[float] = na(list)
    Y: list[float] = na(list)
    YSum: list[float] = na(list)


DEBUG: bool = False


@script.indicator("SuperTrend + Relative Volume (Kernel Optimized) | Flux Charts", max_labels_count=500, overlay=True)
def main(
    atrLength=input.int(10, title="ATR Length", group="SuperTrend"),
    atrMultiplier=input.int(3, title="ATR Multiplier", group="SuperTrend"),
    supertrend_max_opacity=input.int(99, minval=0, maxval=100, title="SuperTrend Max Opacity", group="SuperTrend", tooltip="This setting sets the opacity of supertrend based on the KDE%. A higher value will increase the transparency."),
    supertrend_min_opacity=input.int(53, minval=0, maxval=100, title="SuperTrend Min Opacity", group="SuperTrend", tooltip="This setting sets the opacity of supertrend based on the KDE%. A lower value will decrease the transparency."),
    KDEBandwidth=input.float(0.1, "Bandwidth", minval=0.01, step=0.1, group="KDE", tooltip="This setting sets the smoothness of the KDE function output."),
    KDEStep=input.int(100, "Nº Bins", minval=1, group="KDE", tooltip="The number of elements the KDE Probability array will have. Higher settings will result in greater precision."),
    activationThresholdInput=input.float(70, "KDE Threshold %", minval=0, maxval=100, step=2.5, group="KDE", tooltip="This setting sets the KDE% threshold that must be exceeeded to indicate buy or sell signals."),
    barLength=input.int(25, "Relative Volume Length", minval=1, group="KDE", tooltip="This setting sets the number of candles back to calculate Relative Breakout Volume"),
    activationThresholdEnabled=input.bool(False, "Enable Activation Threshold", group="KDE", tooltip="Only trigger a supertrend direction change if the relative volume's percentile is above the KDE Threshold %"),
    bearishColor=input.color(color.new('#F23646'), "Bullish Break", group="Style", inline="col"),
    bullishColor=input.color(color.rgb(9, 209, 66), "Bearish Break", group="Style", inline="col"),
    textColor=input.color(color.white, 'Text', group='Style', inline="col", display=display.none),
    KDELabelsEnabled=input.bool(True, "KDE Labels", group="Style"),
    showSuperTrendLine=input.bool(True, "Display SuperTrend Line", group="Style"),
    showFillColors=input.bool(True, "Display Volume Gradient", group="Style"),
    showTrendColor=input.bool(False, "Display Trend Color", group="Style"),
    ShowErrors=input.bool(True, "Show Errors", group="Style")
):
    KDEKernel: str = "Gaussian"
    probMode: str = "Sum"
    activationThreshold = activationThresholdInput / 100

    def gaussian(distance: float, bandwidth: float = 1.0):
        return 1.0 / math.sqrt(2.0 * math.pi) * math.pow(math.e, -0.5 * math.pow(distance / bandwidth, 2.0))

    volumeProb: Persistent[float] = na(float)
    maxVolumeProb: float = na(float)

    def kde(arr: list[float], kernel: str, bandwidth: float, steps: int):
        arrSize = array.size(arr)
        arrMax: int = 3
        arrMin = -3
        arrRange = arrMax - arrMin
        stepCount = arrRange / steps

        densityRange: list[float] = array.new_float(steps)
        for i in pine_range(0, steps - 1):
            array.set(densityRange, i, arrMin + i * stepCount)

        xArr: list[float] = array.new_float()
        yArr: list[float] = array.new_float()
        for i in pine_range(0, array.size(densityRange) - 1):
            temp: float = 0
            for j in pine_range(0, array.size(arr) - 1):
                temp += gaussian(array.get(densityRange, i) - array.get(arr, j), bandwidth)
            array.push(xArr, array.get(densityRange, i))
            array.push(yArr, temp)
        totalDensity = array.sum(yArr)
        for k in pine_range(0, array.size(yArr) - 1):
            array.set(yArr, k, array.get(yArr, k) / totalDensity)
        return (xArr, yArr)

    Pine_Supertrend, pineDirection = ta__ren__.supertrend(atrMultiplier, atrLength)

    bullishBreak = ta__ren__.crossover(close, Pine_Supertrend) and barstate.isconfirmed
    bearishBreak = ta__ren__.crossunder(close, Pine_Supertrend) and barstate.isconfirmed

    buyVolumeTotal = volume * (close - low) / (high - low)
    sellVolumeTotal = volume * (high - close) / (high - low)
    buyVolumeTotalAverage = ta__ren__.ema(buyVolumeTotal, barLength)
    buyVolumeTotalAverageShort = ta__ren__.ema(buyVolumeTotal, 10)

    sellVolumeTotalAverage = ta__ren__.ema(sellVolumeTotal, barLength)
    sellVolumeTotalAverageShort = ta__ren__.ema(sellVolumeTotal, 10)

    buyVolume = buyVolumeTotalAverageShort / buyVolumeTotalAverage
    sellVolume = sellVolumeTotalAverageShort / sellVolumeTotalAverage

    volumeOnBullishBreak: Persistent[list[float]] = array.new_float()
    volumeOnBearishBreak: Persistent[list[float]] = array.new_float()

    bullishKDE: Persistent[KDE] = KDE(na, array.new_float(), array.new_float(), array.new_float())
    bearishKDE: Persistent[KDE] = KDE(na, array.new_float(), array.new_float(), array.new_float())

    if not na(volume):
        if bullishBreak and (not na(buyVolume)):
            if array.size(volumeOnBullishBreak) >= KDEStep:
                array.shift(volumeOnBullishBreak)
            array.push(volumeOnBullishBreak, buyVolume)
            normalizedVolumeOnBreak = array.standardize(volumeOnBullishBreak)
            bullishKDEX1, bullishKDEY1 = kde(normalizedVolumeOnBreak, KDEKernel, KDEBandwidth, KDEStep)

            bullishKDE.X = bullishKDEX1
            bullishKDE.Y = bullishKDEY1

            array.clear(bullishKDE.YSum)

            temp: float = 0.0
            __loop_2__ = pine_loop(0)
            while __loop_2__.step(array.size(bullishKDE.Y) - 1):
                i = __loop_2__.value
                temp += array.get(bullishKDE.Y, i)
                array.push(bullishKDE.YSum, temp)
            bullishKDE.mid = array.get(bullishKDE.X, array.indexof(bullishKDE.Y, array.max(bullishKDE.Y)))

        if bearishBreak and (not na(sellVolume)):
            if array.size(volumeOnBearishBreak) >= KDEStep:
                array.shift(volumeOnBearishBreak)
            array.push(volumeOnBearishBreak, sellVolume)
            normalizedVolumeOnBreak = array.standardize(volumeOnBearishBreak)
            bearishKDEX1, bearishKDEY1 = kde(normalizedVolumeOnBreak, KDEKernel, KDEBandwidth, KDEStep)
            bearishKDE.X = bearishKDEX1
            bearishKDE.Y = bearishKDEY1
            array.clear(bearishKDE.YSum)

            temp: float = 0.0
            __loop_2__ = pine_loop(0)
            while __loop_2__.step(array.size(bearishKDE.Y) - 1):
                i = __loop_2__.value
                temp += array.get(bearishKDE.Y, i)
                array.push(bearishKDE.YSum, temp)
            bearishKDE.mid = array.get(bearishKDE.X, array.indexof(bearishKDE.Y, array.max(bearishKDE.Y)))

    def prefixSum(arr: list[float], l: int, r: int):
        return array.get(arr, r) - (0 if l == 0 else array.get(arr, l - 1))

    def standardize(val: float, arr: list[float]):
        meanValue = array.avg(arr)
        stdDevArr = array.stdev(arr)
        stdVal = (val - meanValue) / stdDevArr
        return stdVal

    def getSupertrendTransparency(KDEProb):
        newValue = KDEProb * (supertrend_max_opacity - supertrend_min_opacity) + supertrend_min_opacity
        newValue = supertrend_max_opacity - newValue + supertrend_min_opacity
        return newValue

    def overKDEThreshold(KDEprob):
        __block_result__ = na
        if KDEprob >= activationThreshold:
            __block_result__ = True
        elif KDEprob < activationThreshold:
            __block_result__ = False
        return __block_result__

    bull = pineDirection < 0 and (not na(volume))
    bear = pineDirection > 0 and (not na(volume))

    if bull:
        vol = standardize(buyVolume, volumeOnBullishBreak)
        if array.size(volumeOnBullishBreak) > 0:
            volXIndexL = array.binary_search_leftmost(bullishKDE.X, vol)
            volXIndexR = math.min(array.binary_search_rightmost(bullishKDE.X, vol), array.size(bullishKDE.X) - 1)
            nearestIndex = volXIndexL if math.abs(vol - array.get(bullishKDE.X, volXIndexL)) < math.abs(vol - array.get(bullishKDE.X, volXIndexR)) else volXIndexR
            if probMode == 'Sum':
                volumeProb = prefixSum(bullishKDE.YSum, 0, nearestIndex)
    if bear:
        vol = standardize(sellVolume, volumeOnBearishBreak)
        if array.size(volumeOnBearishBreak) > 0:
            volXIndexL = array.binary_search_leftmost(bearishKDE.X, vol)
            volXIndexR = math.min(array.binary_search_rightmost(bearishKDE.X, vol), array.size(bearishKDE.X) - 1)
            nearestIndex = volXIndexL if math.abs(vol - array.get(bearishKDE.X, volXIndexL)) < math.abs(vol - array.get(bearishKDE.X, volXIndexR)) else volXIndexR
            if probMode == 'Sum':
                volumeProb = prefixSum(bearishKDE.YSum, 0, nearestIndex)

    threshold_condition = not activationThresholdEnabled or overKDEThreshold(volumeProb)

    bull_condition = bullishBreak and threshold_condition
    bear_condition = bearishBreak and threshold_condition

    direction: PersistentSeries[bool] = False
    direction = True if bull_condition else False if bear_condition else direction[1]

    trend_color: PersistentSeries[Color] = bearishColor
    trend_color = bullishColor if direction else bearishColor if not direction else trend_color[1]

    supertrend_color: Persistent[Color] = bearishColor
    supertrend_color = bullishColor if direction and bull else bearishColor if not direction and bear else color.gray

    table__ren__: Persistent[Table] = table.new(position=position.top_right, columns=1, rows=1)
    if (na(volume) or volume == 0) and ShowErrors:
        table.cell(table__ren__, row=0, column=0, text='⚠️ No Volume Data Available for ' + syminfo.tickerid, text_color=color.white, bgcolor=color.red)
    elif bar_index == last_bar_index and (array.size(volumeOnBullishBreak) != KDEStep or array.size(volumeOnBearishBreak) != KDEStep) and ShowErrors:
        log.info(string.tostring(array.size(volumeOnBearishBreak)))
        table.cell(table__ren__, row=0, column=0, text='⚠️ Not enough data. There were not enough SuperTrend Signals generated on this chart for the model. Lower bin value or change chart settings. ' + syminfo.tickerid, text_color=color.white, bgcolor=color.red)
    else:
        table.clear(table__ren__, 0, 0)

    upTrend = plot(Pine_Supertrend if bull else na, 'Up direction', supertrend_color if showSuperTrendLine else na, style=plot.style_linebr)
    downTrend = plot(Pine_Supertrend if bear else na, 'Down direction', supertrend_color if showSuperTrendLine else na, style=plot.style_linebr)
    bodyMiddle = plot(na if barstate.isfirst else (open + close) / 2, 'Body Middle', display=display.none)

    fill(bodyMiddle, upTrend, color.new(supertrend_color, getSupertrendTransparency(volumeProb) if showFillColors else 100), fillgaps=False)
    fill(bodyMiddle, downTrend, color.new(supertrend_color, getSupertrendTransparency(volumeProb) if showFillColors else 100), fillgaps=False)

    plotshape(Pine_Supertrend * 0.999 if bull_condition else na, 'Bullish Arrows', style=shape.arrowup, size=size.normal, location=location.absolute, color=bullishColor, force_overlay=True)
    plotshape(Pine_Supertrend * 1.001 if bear_condition else na, 'Bearish Arrows', style=shape.arrowdown, size=size.normal, location=location.absolute, color=bearishColor, force_overlay=True)

    alertcondition(bull_condition, 'Bullish Trend')
    alertcondition(bear_condition, 'Bearish Trend')

    txt: str = ""
    txt = 'Vol: ' + string.tostring(volumeProb * 100, '#.#') + '%'
    if bull_condition and KDELabelsEnabled:
        label.new(bar_index, y=Pine_Supertrend * 0.999, text=txt, yloc=yloc.price, color=color.new(color.blue, 100), style=label.style_label_up, textcolor=textColor, force_overlay=True)
    if bear_condition and KDELabelsEnabled:
        label.new(bar_index, y=Pine_Supertrend * 1.001, text=txt, yloc=yloc.price, color=color.new(color.blue, 100), style=label.style_label_down, textcolor=textColor, force_overlay=True)

    candleColor = bullishColor if bull else bearishColor if bear else na

    barcolor(trend_color if showTrendColor else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
