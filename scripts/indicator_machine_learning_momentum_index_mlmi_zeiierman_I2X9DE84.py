"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt, udt_copy
from pynecore.lib import (
    alertcondition, array, close, color, display, fill, hline, input, math,
    na, plot, script, ta
)
from pynecore.types import Persistent


@udt
class Data:
    parameter1: list[float] = na(list)
    parameter2: list[float] = na(list)
    priceArray: list[float] = na(list)
    resultArray: list[float] = na(list)


t1: str = 'This parameter controls the number of neighbors to consider while making a prediction using the k-Nearest Neighbors (k-NN) algorithm. By modifying the value of k, you can change how sensitive the prediction is to local fluctuations in the data. \n\nA smaller value of k will make the prediction more sensitive to local variations and can lead to a more erratic prediction line. \n\nA larger value of k will consider more neighbors, thus making the prediction more stable but potentially less responsive to sudden changes.'
t2: str = 'The parameter controls the length of the trend used in computing the momentum. This length refers to the number of periods over which the momentum is calculated, affecting how quickly the indicator reacts to changes in the underlying price movements. \n\nA shorter trend length (smaller momentumWindow) will make the indicator more responsive to short-term price changes, potentially generating more signals but at the risk of more false alarms. \n\nA longer trend length (larger momentumWindow) will make the indicator smoother and less responsive to short-term noise, but it may lag in reacting to significant price changes.'


@script.indicator(title='Machine Learning Momentum Index (MLMI) [Zeiierman]', shorttitle='Machine Learning Momentum Index (MLMI)', overlay=False, precision=1)
def main(
    numNeighbors=input(200, title='Prediction Data (k)', tooltip=t1),
    momentumWindow=input.int(20, step=2, minval=10, maxval=200, title='Trend Length', tooltip=t2)
):
    MA_quick = ta.wma(close, 5)
    MA_slow = ta.wma(close, 20)
    rsi_quick = ta.wma(ta.rsi(close, 5), momentumWindow)
    rsi_slow = ta.wma(ta.rsi(close, 20), momentumWindow)
    pos = ta.crossover(MA_quick, MA_slow)
    neg = ta.crossunder(MA_quick, MA_slow)
    data: Persistent[Data] = Data(array.new_float(1, 0), array.new_float(1, 0), array.new_float(1, 0), array.new_float(1, 0))
    @method
    def storePreviousTrade(d: Data, p1, p2):
        array.push(d.parameter1, array.get(d.parameter1, array.size(d.parameter1) - 1))
        array.push(d.parameter2, array.get(d.parameter2, array.size(d.parameter2) - 1))
        array.push(d.priceArray, array.get(d.priceArray, array.size(d.priceArray) - 1))
        array.push(d.resultArray, 1 if close >= array.get(d.priceArray, array.size(d.priceArray) - 1) else -1)
        array.set(d.parameter1, array.size(d.parameter1) - 1, p1)
        array.set(d.parameter2, array.size(d.parameter2) - 1, p2)
        return array.set(d.priceArray, array.size(d.priceArray) - 1, close)

    @method
    def knnPredict(d: Data, p1, p2, k):
        distances: list[float] = array.new_float(0)
        n = array.size(d.parameter1) - 1
        for i in pine_range(0, n, 1):
            distance = math.sqrt(math.pow(p1 - array.get(d.parameter1, i), 2) + math.pow(p2 - array.get(d.parameter2, i), 2))
            array.push(distances, distance)
        sortedDistances = udt_copy(distances)
        method_call('sort', sortedDistances)
        selectedDistances = method_call('slice', sortedDistances, 0, math.min(k, method_call('size', sortedDistances)))
        maxDist = method_call('max', selectedDistances)
        neighbors: list[float] = array.new_float(0)
        for i in pine_range(0, array.size(distances) - 1, 1):
            if array.get(distances, i) <= maxDist:
                array.push(neighbors, array.get(d.resultArray, i))
        prediction = array.sum(neighbors)
        return prediction

    if pos or neg:
        storePreviousTrade(data, rsi_slow, rsi_quick)
    prediction = knnPredict(data, rsi_slow, rsi_quick, numNeighbors)
    prediction_ = plot(prediction, color=color.new(color.new('#426EFF'), 0), title='MLMI Prediction')
    prediction_ma = ta.wma(prediction, 20)
    plot(prediction_ma, color=color.new(color.new('#31FFC8'), 0), title='WMA of MLMI Prediction')
    hline(0, title='Mid Level')
    upper = ta.highest(prediction, 2000)
    lower = ta.lowest(prediction, 2000)
    upper_ = upper - ta.ema(ta.stdev(prediction, 20), 20)
    lower_ = lower + ta.ema(ta.stdev(prediction, 20), 20)
    channel_upper = plot(upper, color=na, editable=False, display=display.none)
    channel_lower = plot(lower, color=na, editable=False, display=display.none)
    channel_mid = plot(0, color=na, editable=False, display=display.none)
    fill(channel_mid, channel_upper, top_value=upper, bottom_value=0, bottom_color=na, top_color=color.new(color.lime, 75), title='Channel Gradient Fill')
    fill(channel_mid, channel_lower, top_value=0, bottom_value=lower, bottom_color=color.new(color.red, 75), top_color=na, title='Channel Gradient Fill')
    fill(prediction_, channel_mid, upper, upper_, top_color=color.new(color.lime, 0), bottom_color=color.new(color.green, 100), title='Overbought Gradient Fill')
    fill(prediction_, channel_mid, lower_, lower, top_color=color.new(color.red, 100), bottom_color=color.new(color.red, 0), title='Oversold Gradient Fill')
    P_OB_Over = ta.crossover(prediction, upper_)
    P_OB_Under = ta.crossunder(prediction, upper_)
    P_OS_Over = ta.crossover(prediction, lower_)
    P_OS_Under = ta.crossunder(prediction, lower_)
    P_Mid_Over = ta.crossover(prediction, 0)
    P_Mid_Under = ta.crossunder(prediction, 0)
    P_MA_Over = ta.crossover(prediction, prediction_ma)
    P_MA_Under = ta.crossunder(prediction, prediction_ma)
    alertcondition(P_OB_Over, title='MLMI Crossover OB', message='MLMI Crossover OB')
    alertcondition(P_OB_Under, title='MLMI Crossunder OB', message='MLMI Crossunder OB')
    alertcondition(P_OS_Over, title='MLMI Crossover OS', message='MLMI Crossover OS')
    alertcondition(P_OS_Under, title='MLMI Crossunder OS', message='MLMI Crossunder OS')
    alertcondition(P_Mid_Over, title='MLMI Crossover 50', message='MLMI Crossover 50')
    alertcondition(P_Mid_Under, title='MLMI Crossunder 50', message='MLMI Crossunder 50')
    alertcondition(P_MA_Over, title='MLMI Crossover Ma', message='MLMI Crossover Ma')
    alertcondition(P_MA_Under, title='MLMI Crossunder Ma', message='MLMI Crossunder Ma')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
