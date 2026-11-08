"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, barstate, box, chart, close,
    color, high, input, location, low, math, na, nz, plotshape, position, runtime, script, shape,
    size, string, ta, table, text, volume
)
from pynecore.types import Box, Persistent, Series


@script.indicator("Machine Learning Price Target Prediction Signals [AlgoAlpha]", shorttitle="AlgoAlpha - ML Price Targets", overlay=True, max_bars_back=5000, precision=5, max_boxes_count=500)
def main(
    trndMethod=input.string("EMA Cross (Fast Slow)", "Trend Indicator for Signals", options=("SuperTrend", "HMA (Increasing or Decreasing)", "EMA Cross (Fast Slow)"), group="Trend Indicator Settings", tooltip="Select the method used to determine trend direction"),
    MAlen_roc=input.int(93, "Hull Moving Average Length", group="Trend Indicator Settings", tooltip="Length of the Hull Moving Average used for trend detection"),
    Ema_fast=input.int(50, "Fast EMA Length", group="Trend Indicator Settings", tooltip="Length of the faster Exponential Moving Average"),
    Ema_slow=input.int(200, "Slow EMA Length", group="Trend Indicator Settings", tooltip="Length of the slower Exponential Moving Average"),
    supertrend_factor=input.float(3, "SuperTrend Factor", group="Trend Indicator Settings", tooltip="Multiplier for the ATR in SuperTrend calculation"),
    atr_length=input.int(10, "ATR Length", group="Trend Indicator Settings", tooltip="Length of the Average True Range used in SuperTrend"),
    bandwidth=input.float(5, "Kernel Regression Bandwidth", tooltip="Controls how much weight is given to distant data points in the kernel regression. Higher values create smoother predictions but may potentially result in underfitting while smaller values give more weight to recent data points, potentially leading to overfitting if it's too small.", group="Kernel Regression Settings", minval=2),
    hide_na_sig=input.bool(True, "Hide NaN Predictions", tooltip="In some instances, the prediction might be NaN due to the input data resulting in very small results inside the internal calculations, which result in NaN predictions. This setting hides signals where there is no value for the predicted move size."),
    green=input.color(color.new('#00FFBB'), title="Bullish Color", group="Visuals", tooltip="Color used for bullish signals and indicators"),
    red=input.color(color.new('#FF1100'), title="Bearish Color", group="Visuals", tooltip="Color used for bearish signals and indicators")
):
    ST, Direction = ta.supertrend(supertrend_factor, atr_length)

    hull: Series = ta.hma(close, MAlen_roc)
    hmaSig = 1 if hull > hull[1] else -1

    ema1 = ta.ema(close, Ema_fast)
    ema2 = ta.ema(close, Ema_slow)
    emasig = 1 if ema1 > ema2 else -1

    def binarySignal(_method):
        __block_result__ = na
        __switch__ = _method
        if __switch__ == "SuperTrend":
            __block_result__ = -Direction
        elif __switch__ == "HMA (Increasing or Decreasing)":
            __block_result__ = hmaSig
        elif __switch__ == "EMA Cross (Fast Slow)":
            __block_result__ = emasig
        return __block_result__

    h1 = ta.highest(14)
    l1 = ta.lowest(14)
    v1 = (h1 - close) / h1
    vS1: Series = ta.rsi(v1, 14)

    h2 = ta.highest(14)
    l2 = ta.lowest(14)
    v2 = (close - l2) / l2
    vS2: Series = ta.rsi(v2, 14)

    v3 = ta.sma(high - low, 40)
    vs3 = ta.ema(v3, 20)
    x3 = v3 - vs3
    sLen3: int = 1000
    xS3: Series = (x3 - ta.lowest(x3, sLen3)) / (ta.highest(x3, sLen3) - ta.lowest(x3, sLen3)) * 100

    v4 = ta.sma(high - low, 40)
    vs4 = ta.ema(v4, 20)
    vss4 = ta.ema(v4 - vs4, 10)
    x4 = v4 - vs4 - vss4
    sLen4: int = 1000
    x_min4 = ta.lowest(x4, sLen4)
    x_max4 = ta.highest(x4, sLen4)
    x_scaled4: Series = (x4 - x_min4) / (x_max4 - x_min4) * 100

    cumVol: Persistent[float] = 0.0
    cumVol += nz(volume)
    if barstate.islast and cumVol == 0:
        runtime.error('No volume is provided by the data vendor.')

    shortlen5: int = 7
    longlen5: int = 14
    short5 = ta.ema(volume, shortlen5)
    long5 = ta.ema(volume, longlen5)
    osc5: Series = 100 * (short5 - long5) / long5

    length6: int = 14
    ci6: Series = 100 * math.log10(math.sum(ta.atr(1), length6) / (ta.highest(length6) - ta.lowest(length6))) / math.log10(length6)
    offset6: int = 0

    rsi7: Series = ta.rsi(close, 14)

    trendSignal: Series = binarySignal(trndMethod)
    scaled_trendSignal: Series = 1 if trendSignal == 1 else 0 if trendSignal == -1 else na

    duration: Series = ta.barssince(ta.cross(trendSignal, 0))
    signalMoveUp = (high - close[duration]) / close[duration]
    signalMoveDown = (low - close[duration]) / close[duration]

    runup = ta.highest(signalMoveUp, math.max(1, nz(duration)))
    drawdown = ta.lowest(signalMoveDown, math.max(1, nz(duration)))

    absoluteMove: Series = math.abs(runup if trendSignal > 0 else drawdown)

    target: Persistent[list[float]] = array.new_float()
    feature1: Persistent[list[float]] = array.new_float()
    feature2: Persistent[list[float]] = array.new_float()
    feature3: Persistent[list[float]] = array.new_float()
    feature4: Persistent[list[float]] = array.new_float()
    feature5: Persistent[list[float]] = array.new_float()
    feature6: Persistent[list[float]] = array.new_float()
    feature7: Persistent[list[float]] = array.new_float()
    feature8: Persistent[list[float]] = array.new_float()
    current_features: Persistent[list[float]] = array.new_float()

    look_back = duration[1] + 1

    if ta.cross(trendSignal, 0) and (trendSignal[1] != 0 or not na(trendSignal[1])):
        if not (na(absoluteMove[1]) or na(vS1[look_back]) or na(vS2[look_back]) or na(xS3[look_back]) or na(x_scaled4[look_back]) or na(osc5[look_back]) or na(ci6[look_back]) or na(rsi7[look_back])):
            array.unshift(target, absoluteMove[1])
            array.unshift(feature1, vS1[look_back])
            array.unshift(feature2, vS2[look_back])
            array.unshift(feature3, xS3[look_back])
            array.unshift(feature4, x_scaled4[look_back])
            array.unshift(feature5, osc5[look_back])
            array.unshift(feature6, ci6[look_back])
            array.unshift(feature7, rsi7[look_back])
            array.unshift(feature8, scaled_trendSignal[look_back])

    if ta.cross(trendSignal, 0):
        array.clear(current_features)
        array.push(current_features, vS1)
        array.push(current_features, vS2)
        array.push(current_features, xS3)
        array.push(current_features, x_scaled4)
        array.push(current_features, osc5)
        array.push(current_features, ci6)
        array.push(current_features, rsi7)
        array.push(current_features, scaled_trendSignal)

    def kernelRBF(distance: float, bandwidth: float):
        return math.exp(-math.pow(distance / bandwidth, 2))

    def predictKernelRegression(bandwidth):
        sumWeightedTargets: float = 0.0
        sumKernels: float = 0.0
        numPoints = array.size(target)

        if numPoints > 0:
            for i in pine_range(0, numPoints - 1):
                storedTarget = array.get(target, i)
                distSq: float = 0.0
                distSq += math.pow(array.get(feature1, i) - array.get(current_features, 0), 2)
                distSq += math.pow(array.get(feature2, i) - array.get(current_features, 1), 2)
                distSq += math.pow(array.get(feature3, i) - array.get(current_features, 2), 2)
                distSq += math.pow(array.get(feature4, i) - array.get(current_features, 3), 2)
                distSq += math.pow(array.get(feature5, i) - array.get(current_features, 4), 2)
                distSq += math.pow(array.get(feature6, i) - array.get(current_features, 5), 2)
                distSq += math.pow(array.get(feature7, i) - array.get(current_features, 6), 2)
                distSq += math.pow(array.get(feature8, i) - array.get(current_features, 7), 2)

                distance = math.sqrt(distSq)

                kernelValue = kernelRBF(distance, bandwidth)

                sumWeightedTargets += kernelValue * storedTarget
                sumKernels += kernelValue

        return sumWeightedTargets / sumKernels if sumKernels != 0 else na

    predictedMove: Series = predictKernelRegression(bandwidth)

    total_predictions: Persistent[int] = 0
    correct_predictions: Persistent[int] = 0

    if ta.cross(trendSignal, 0) and (not na(predictedMove[1])):
        total_predictions += 1
        if absoluteMove[1] > predictedMove[1]:
            correct_predictions += 1

    win_rate = correct_predictions / total_predictions

    recommended_RR = 1 / win_rate - 1

    tp: Persistent[list[Box]] = array.new_box()
    sl: Persistent[list[Box]] = array.new_box()
    in_trade: Persistent[int] = 0

    tp_level = close + close * predictedMove if trendSignal > 0 else close - close * predictedMove
    sl_level = close - close * predictedMove / recommended_RR if trendSignal > 0 else close + close * predictedMove / recommended_RR

    if ta.cross(trendSignal, 0) and (not na(predictedMove) if hide_na_sig else True):
        while array.size(tp) > 0:
            array.shift(tp)
        while array.size(sl) > 0:
            array.shift(sl)
        array.unshift(tp, box.new(bar_index, math.max(close, tp_level), bar_index + 1, math.min(close, tp_level), color.new(green, 100), bgcolor=color.new(green, 80), force_overlay=True))
        array.unshift(sl, box.new(bar_index, math.max(close, sl_level), bar_index + 1, math.min(close, sl_level), color.new(red, 100), bgcolor=color.new(red, 80), force_overlay=True))
        in_trade = 1

    is_not_first = trendSignal == trendSignal[1]

    tp_hit: Persistent[bool] = False
    sl_hit: Persistent[bool] = False

    if array.size(tp) > 0:
        Upper = method_call('get_top', array.first(tp))
        Lower = method_call('get_bottom', array.first(tp))
        if trendSignal > 0 and high < Upper or (trendSignal < 0 and low > Lower) or (not is_not_first):
            method_call('set_right', array.first(tp), bar_index)
        else:
            tp_hit = True
            method_call('set_right', array.first(tp), bar_index)
            method_call('set_right', array.first(sl), bar_index)
            array.shift(tp)
            array.shift(sl)
            in_trade = 0

    if array.size(sl) > 0:
        Upper = method_call('get_top', array.first(sl))
        Lower = method_call('get_bottom', array.first(sl))
        if trendSignal > 0 and low > Lower or (trendSignal < 0 and high < Upper) or (not is_not_first):
            method_call('set_right', array.first(sl), bar_index)
        else:
            sl_hit = True
            method_call('set_right', array.first(sl), bar_index)
            array.shift(tp)
            array.shift(sl)
            in_trade = 0

    barcolor(color.gray if in_trade == 0 else green if trendSignal > 0 else red, title='Trade Status')

    Volatility = ta.atr(14)

    plotshape(sl_level - Volatility if ta.crossover(trendSignal, 0) and (not na(predictedMove) if hide_na_sig else True) else na, title='Bullish Entry Signal', style=shape.labelup, location=location.absolute, color=green, text='▲', textcolor=chart.fg_color, size=size.small)

    plotshape(sl_level + Volatility if ta.crossunder(trendSignal, 0) and (not na(predictedMove) if hide_na_sig else True) else na, title='Bearish Entry Signal', style=shape.labeldown, location=location.absolute, color=red, text='▼', textcolor=chart.fg_color, size=size.small)

    if barstate.islast:
        data_table: Persistent = table.new(position=position.top_right, columns=2, rows=6, bgcolor=chart.bg_color, border_width=1, border_color=chart.fg_color, frame_color=chart.fg_color, frame_width=1)

        table.cell(data_table, text_halign=text.align_center, column=0, row=0, text='Indicator Metrics', text_size=size.tiny, text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=0, text='Value', text_size=size.tiny, text_color=chart.fg_color)

        table.cell(data_table, text_halign=text.align_left, column=0, row=1, text='Training Data Size', text_size=size.tiny, text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=1, text=string.tostring(array.size(target)), text_size=size.tiny, text_color=chart.fg_color)

        table.cell(data_table, text_halign=text.align_left, column=0, row=2, text='Predicted Move Size', text_size=size.tiny, text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=2, text=string.format('{0,number,#.##}%', predictedMove * 100), text_size=size.tiny, text_color=chart.fg_color)

        table.cell(data_table, text_halign=text.align_left, column=0, row=3, text='Success Rate (When price moves \nmore or equal to predicted amount)', text_size=size.tiny, text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=3, text=string.format('{0,number,#.##}%', win_rate * 100), text_size=size.tiny, text_color=chart.fg_color)

        table.cell(data_table, text_halign=text.align_left, column=0, row=4, text='Recommended Reward/Risk Ratio', text_size=size.tiny, text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=4, text=string.format('{0,number,#.##}', recommended_RR), text_size=size.tiny, text_color=chart.fg_color)

        table.cell(data_table, text_halign=text.align_left, column=0, row=5, text='In Trade', text_size=size.tiny, text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=5, text='Yes' if in_trade != 0 else 'No', text_size=size.tiny, bgcolor=color.gray if in_trade == 0 else color.new(green, 70) if trendSignal > 0 else color.new(red, 70), text_color=chart.fg_color)

    alertcondition(ta.crossover(trendSignal, 0), 'Bullish Signal', 'New bullish trend signal detected')
    alertcondition(ta.crossunder(trendSignal, 0), 'Bearish Signal', 'New bearish trend signal detected')
    alertcondition(tp_hit, 'Take Profit Hit', 'Take profit level has been reached')
    alertcondition(sl_hit, 'Stop Loss Hit', 'Stop loss level has been reached')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
