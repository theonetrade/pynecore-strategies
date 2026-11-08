"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    array, bar_index, box, chart, close, color, high, input, line, low, math,
    na, plot, script, ta
)
from pynecore.types import Box, Line, NA, Persistent, Series

t1: str = 'Number of neighbors used in the KNN algorithm. Increasing \'k\' can make the prediction more resilient to noise but may decrease sensitivity to local variations.\n\nNumber of data points considered in the AI analysis. This affects how the AI interprets patterns in the price data.'
t2: str = 'Type of moving average to be applied. Various options allow for different smoothing techniques which can emphasize or dampen certain aspects of the price movement. \n\nLength of the moving average. A greater length will create a smoother curve but might lag behind recent price changes.'
t3: str = 'Source data used to classify price as bullish or bearish. Can be adjusted to consider different aspects of the price information.'
t4: str = 'Source data used to calculate the moving average for comparison. Different selections may emphasize different aspects of price movement.'
t5: str = 'Toggle to show or hide the AI-generated moving average line.'
t6: str = 'Toggle to show or hide the AI-calculated slope of the trend.'
t7: str = 'Option to remove or retain historical boxes.'
t8: str = 'Smoothing period for the initial moving average in the AI(2) algorithm.'
t9: str = 'Toggle to remove all boxes from the chart.'
t10: str = 'Toggle to remove all lines from the chart.'
t11: str = 'Number of closest values used for the calculation of AI(2) Moving Averages. A higher number may provide a smoother but less sensitive curve.'


@script.indicator('AI Moving Average (Expo)', overlay=True, na_bool=True)
def main(
    aiMa=input.bool(False, title='Show AI(1) Moving Average', group='AI(1) Average', tooltip=t5),
    aiSlope=input.bool(True, title='Show AI(1) Slope', group='AI(1) Average', tooltip=t6),
    maType=input.string('SMA', title='Select MA', options=('SMA', 'EMA', 'WMA', 'RMA', 'HMA', 'VWMA'), inline='MA', group='AI(1) Average'),
    length=input.int(50, title='', minval=1, inline='MA', group='AI(1) Average', tooltip=t2),
    k=input.int(5, title='Neighbors', minval=1, maxval=100, inline='AI', group='AI(1) Settings'),
    n_=input.int(10, title='DataPoints', minval=1, maxval=100, inline='AI', group='AI(1) Settings', tooltip=t1),
    aiMa_2=input.bool(False, title='Show AI(2) Moving Average 1', group='AI(2) Average', tooltip=t5),
    aiMa_3=input.bool(True, title='Show AI(2) Moving Average 2', group='AI(2) Average', tooltip=t6),
    numberOfClosestValues=input.int(15, 'Number of Closest Values', minval=2, maxval=200, inline='AI2', group='AI(2) Settings', tooltip=t11),
    smoothingPeriod=input.int(20, 'Smoothing Period', minval=2, maxval=500, inline='aiMa_2', group='AI(2) Settings', tooltip=t8),
    dataToClassify: Series[float] = input.source(close, title='Data To Classify', group='AI(1) Settings', tooltip=t3),
    dataForMovingAverage: Series[float] = input.source(close, title='Data For Moving Average (DataForComparison)', group='AI(1) Settings', tooltip=t4),
    negBox_col=input.color(color.new(color.red, 75), title='', group='Style', inline='box'),
    posBox_col=input.color(color.new(color.lime, 75), title='', group='Style', inline='box'),
    line_col=input.color(color.rgb(255, 169, 39), title='', group='Style', inline='box'),
    line_width=input.int(2, title='', group='Style', inline='box', tooltip='Box & Line coloring'),
    del__ren__=input.bool(False, title='Remove Historical Boxes', group='Style', tooltip=t7),
    del_boxes=input.bool(True, title='Remove All Boxes', group='Style', tooltip=t9),
    del_line=input.bool(True, title='Remove All Line', group='Style', tooltip=t10)
):
    n = math.max(k, n_)
    windowSize = math.max(numberOfClosestValues, 30)
    __block_result__ = na
    __switch__ = maType
    if __switch__ == 'SMA':
        __block_result__ = ta.sma(dataForMovingAverage, length)
    elif __switch__ == 'EMA':
        __block_result__ = ta.ema(dataForMovingAverage, length)
    elif __switch__ == 'WMA':
        __block_result__ = ta.wma(dataForMovingAverage, length)
    elif __switch__ == 'RMA':
        __block_result__ = ta.rma(dataForMovingAverage, length)
    elif __switch__ == 'HMA':
        __block_result__ = ta.hma(dataForMovingAverage, length)
    elif __switch__ == 'VWMA':
        __block_result__ = ta.vwma(dataForMovingAverage, length)
    ma: Series = __block_result__
    labels: list[float] = array.new_float(n)
    data: list[float] = array.new_float(n)
    for i in pine_range(0, n - 1, 1):
        array.set(data, i, ma[i])
        label_i = 1 if dataToClassify[i] > ma[i] else 0
        label_j = 1 if ma[i] > ma[i + 1] else 0
        lab = cast_int(math.avg(label_i, label_j))
        array.set(labels, i, lab)
    def knn_weighted(data, labels, k, x):
        n1 = method_call('size', data)
        distances: list[float] = array.new_float(n1)
        indices: list[int] = array.new_int(n1)
        for i in pine_range(0, n1 - 1, 1):
            x_i = method_call('get', data, i)
            dist = math.abs(x - x_i)
            array.set(distances, i, dist)
            array.set(indices, i, i)
        for i in pine_range(0, n1 - 2, 1):
            for j in pine_range(0, n1 - i - 2, 1):
                if array.get(distances, j) > array.get(distances, j + 1):
                    tempDist = array.get(distances, j)
                    array.set(distances, j, array.get(distances, j + 1))
                    array.set(distances, j + 1, tempDist)
                    tempIndex = array.get(indices, j)
                    array.set(indices, j, array.get(indices, j + 1))
                    array.set(indices, j + 1, tempIndex)
        weighted_sum: float = 0.0
        total_weight: float = 0.0
        for i in pine_range(0, k - 1, 1):
            index = array.get(indices, i)
            label_i = method_call('get', labels, index)
            weight_i = 1 / (array.get(distances, i) + 1e-06)
            weighted_sum = weighted_sum + weight_i * label_i
            total_weight = total_weight + weight_i
        return weighted_sum / total_weight

    label_ = knn_weighted(data, labels, k, ma)
    def meanOfKClosest(value_in_: Series, target_):
        closestDistances: list[float] = array.new_float(numberOfClosestValues, 10000000000.0)
        closestValues: list[float] = array.new_float(numberOfClosestValues, 0.0)
        for i in pine_range(1, windowSize, 1):
            value = value_in_[i]
            distance = math.abs(target_ - value)
            maxDistIndex: int = 0
            maxDistValue = array.get(closestDistances, 0)
            for j in pine_range(1, numberOfClosestValues - 1, 1):
                if array.get(closestDistances, j) > maxDistValue:
                    maxDistIndex = j
                    maxDistValue = array.get(closestDistances, j)
            if distance < maxDistValue:
                array.set(closestDistances, maxDistIndex, distance)
                array.set(closestValues, maxDistIndex, value)
        return array.sum(closestValues) / numberOfClosestValues

    ma_ = ta.sma(close, smoothingPeriod)
    knnMA_price_ma = meanOfKClosest(close, ma_)
    KnnMA_ma_ma = meanOfKClosest(ma_, ma_)
    red: Series = label_ == 0
    green: Series = label_ == 1
    blue: Series = not red and (not green)
    prevRed = red[1]
    prevGreen = green[1]
    prevBlue = blue[1]
    switchdown = (prevBlue or prevGreen) and red
    switchup = (prevBlue or prevRed) and green
    redtoblue = prevRed and blue
    greentoblue = prevGreen and blue
    x_values: Persistent[list[float]] = array.new_float(0)
    y_values: Persistent[list[float]] = array.new_float(0)
    if switchdown or switchup:
        array.clear(x_values)
        array.clear(y_values)
    array.push(x_values, bar_index)
    array.push(y_values, ma)
    slope: float = na(float)
    intercept: float = na(float)
    if array.size(x_values) > 1:
        sum_x: float = array.sum(x_values)
        sum_y: float = array.sum(y_values)
        sum_xy: float = 0.0
        sum_x2: float = 0.0
        count: int = array.size(x_values)
        for i in pine_range(0, count - 1, 1):
            x: float = array.get(x_values, i)
            y: float = array.get(y_values, i)
            sum_xy = sum_xy + x * y
            sum_x2 = sum_x2 + x * x
        slope = (count * sum_xy - sum_x * sum_y) / (count * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / count
    line_eq = na if na(slope) else slope * bar_index + intercept
    bo: Persistent = NA(Box)
    li: Persistent = NA(Line)
    maxHi: Persistent = NA(float)
    minLo: Persistent = NA(float)
    highPoint = ta.highest(high, 20)
    lowPoint = ta.lowest(low, 20)
    if switchdown or switchup:
        if del__ren__:
            method_call('delete', bo)
        maxHi = high if na(highPoint) else math.max(highPoint, high)
        minLo = low if na(lowPoint) else math.min(lowPoint, low)
        bo = box.new(bar_index, maxHi, bar_index + 1, minLo, na, bgcolor=posBox_col if label_ > 0 else negBox_col)
        mid = chart.point.now(math.avg(maxHi, minLo))
        li = line.new(mid, mid, color=line_col, style=line.style_dotted, width=line_width)
    maxHi = math.max(maxHi, high)
    minLo = math.min(minLo, low)
    method_call('set_top', bo, maxHi)
    method_call('set_rightbottom', bo, bar_index, minLo)
    method_call('set_y1', li, math.avg(maxHi, minLo))
    method_call('set_xy2', li, bar_index, math.avg(maxHi, minLo))
    if del_boxes:
        method_call('delete', bo)
    if del_line:
        method_call('delete', li)
    plot(ma if aiMa else na, title='AI(1) Bullish Trend', color=color.lime if label_ == 1 else na, linewidth=2)
    plot(ma if aiMa else na, title='AI(1) Bearish Trend', color=color.red if label_ == 0 else na, linewidth=2)
    plot(ma if aiMa else na, title='AI(1) Moving Average', color=na if label_ == 1 else na if label_ == 0 else color.rgb(0, 136, 255))
    plot(line_eq if aiSlope else na, title='AI(1) Box Slope', color=color.lime if slope > 0 else color.red, linewidth=1)
    plot(ta.wma(knnMA_price_ma, 5) if aiMa_2 else na, color=color.rgb(31, 199, 255), title='AI(2) Moving Average 1')
    plot(ta.wma(KnnMA_ma_ma, 5) if aiMa_3 else na, color=color.yellow, title='AI(2) Moving Average 2')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
