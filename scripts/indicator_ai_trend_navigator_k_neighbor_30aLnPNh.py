"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, array, bgcolor, close, color, hl2, input, math, na, plot,
    script, ta
)
from pynecore.types import Series

t1: str = 'PriceValue selects the method of price computation. \n\nSets the smoothing period for the PriceValue. \n\nAdjusting these settings will change the input values for the K-Nearest Neighbors algorithm, influencing how the trend is calculated.'
t2: str = 'TargetValue specifies the target to evaluate. \n\nSets the smoothing period for the TargetValue.'
t3: str = 'numberOfClosestValues sets the number of closest values that are considered when calculating the KNN Moving Average. Adjusting this number will affect the sensitivity of the trend line, with a higher value leading to a smoother line and a lower value resulting in a line that is more responsive to recent price changes.'
t4: str = 'smoothingPeriod sets the period for the moving average applied to the KNN classifier. Adjusting the smoothing period will affect how rapidly the trend line responds to price changes, with a larger smoothing period leading to a smoother line that may lag recent price movements, and a smaller smoothing period resulting in a line that more closely tracks recent changes.'
t5: str = 'This option controls the background color for the trend prediction. Enabling it will change the background color based on the prediction, providing visual cues on the direction of the trend. A green color indicates a positive prediction, while red indicates a negative prediction.'


@script.indicator('AI Trend Navigator', overlay=True, na_bool=True)
def main(
    PriceValue=input.string('hl2', options=('hl2', 'VWAP', 'sma', 'wma', 'ema', 'hma'), group='', inline='Value'),
    maLen=input.int(5, minval=2, maxval=200, title='', group='', inline='Value', tooltip=t1),
    TargetValue=input.string('Price Action', options=('Price Action', 'VWAP', 'Volatility', 'sma', 'wma', 'ema', 'hma'), group='', inline='Target'),
    maLen_=input.int(5, minval=2, maxval=200, title='', group='', inline='Target', tooltip=t2),
    numberOfClosestValues=input.int(3, 'Number of Closest Values', minval=2, maxval=200, tooltip=t3),
    smoothingPeriod=input.int(50, 'Smoothing Period', minval=2, maxval=500, tooltip=t4),
    Upknn_col=input.color(color.lime, title='', group='KNN Color', inline='knn col'),
    Dnknn_col=input.color(color.red, title='', group='KNN Color', inline='knn col'),
    Neuknn_col=input.color(color.orange, title='', group='KNN Color', inline='knn col'),
    Maknn_col=input.color(color.teal, title='', group='MA KNN Color', inline='MA knn col'),
    bgcolor__ren__=input.bool(False, title='Trend Prediction Color', group='BG Color', inline='bg', tooltip=t5),
    Up_col=input.color(color.lime, title='', group='BG Color', inline='bg'),
    Dn_col=input.color(color.red, title='', group='BG Color', inline='bg')
):
    windowSize = math.max(numberOfClosestValues, 30)
    __block_result__ = na
    __switch__ = PriceValue
    if __switch__ == 'hl2':
        __block_result__ = ta.sma(hl2, maLen)
    elif __switch__ == 'VWAP':
        __block_result__ = ta.vwap(close[maLen])
    elif __switch__ == 'sma':
        __block_result__ = ta.sma(close, maLen)
    elif __switch__ == 'wma':
        __block_result__ = ta.wma(close, maLen)
    elif __switch__ == 'ema':
        __block_result__ = ta.ema(close, maLen)
    elif __switch__ == 'hma':
        __block_result__ = ta.hma(close, maLen)
    value_in = __block_result__
    def meanOfKClosest(value_: Series, target_):
        closestDistances: list[float] = array.new_float(numberOfClosestValues, 10000000000.0)
        closestValues: list[float] = array.new_float(numberOfClosestValues, 0.0)
        for i in pine_range(1, windowSize, 1):
            value = value_[i]
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

    __block_result_1__ = na
    __switch__ = TargetValue
    if __switch__ == 'Price Action':
        __block_result_1__ = ta.rma(close, maLen_)
    elif __switch__ == 'VWAP':
        __block_result_1__ = ta.vwap(close[maLen_])
    elif __switch__ == 'Volatility':
        __block_result_1__ = ta.atr(14)
    elif __switch__ == 'sma':
        __block_result_1__ = ta.sma(close, maLen_)
    elif __switch__ == 'wma':
        __block_result_1__ = ta.wma(close, maLen_)
    elif __switch__ == 'ema':
        __block_result_1__ = ta.ema(close, maLen_)
    elif __switch__ == 'hma':
        __block_result_1__ = ta.hma(close, maLen_)
    target_in = __block_result_1__
    knnMA: Series = meanOfKClosest(value_in, target_in)
    price = math.avg(knnMA, close)
    c: Series = ta.rma(knnMA[1], smoothingPeriod)
    o: Series = ta.rma(knnMA, smoothingPeriod)
    def knn(price: Series):
        __hist_o__: Series = o[0]
        __hist_c__: Series = c[0]
        Pos_count: int = 0
        Neg_count: int = 0
        min_distance: float = 100000000000.0
        nearest_index: int = 0
        for j in pine_range(1, 10, 1):
            distance = math.sqrt(math.pow(price[j] - price, 2))
            if distance < min_distance:
                min_distance = distance
                nearest_index = j
                Neg = __hist_c__[nearest_index] > __hist_o__[nearest_index]
                Pos = __hist_c__[nearest_index] < __hist_o__[nearest_index]
                if Pos:
                    Pos_count = Pos_count + 1
                if Neg:
                    Neg_count = Neg_count + 1
        output = 1 if Pos_count > Neg_count else -1
        return output

    knn_prediction_raw = knn(price)
    knn_prediction = ta.wma(knn_prediction_raw, 3)
    knnMA_: Series = ta.wma(knnMA, 5)
    knnMA_col: Series = Upknn_col if knnMA_ > knnMA_[1] else Dnknn_col if knnMA_ < knnMA_[1] else Neuknn_col
    Classifier_Line = plot(knnMA_, 'Knn Classifier Line', knnMA_col)
    MAknn_ = ta.rma(knnMA, smoothingPeriod)
    plot(MAknn_, 'Average Knn Classifier Line', Maknn_col)
    green: Series = knn_prediction < 0.5
    red: Series = knn_prediction > -0.5
    bgcolor(color.new(Dn_col, 80) if green and bgcolor__ren__ else color.new(Up_col, 80) if red and bgcolor__ren__ else na)
    knnMA_cross_Over_Ma = ta.crossover(knnMA_, MAknn_)
    knnMA_cross_Under_Ma = ta.crossunder(knnMA_, MAknn_)
    knnMA_cross_Over_Close = ta.crossover(knnMA_, close)
    knnMA_cross_Under_Close = ta.crossunder(knnMA_, close)
    knnMA_Switch_Up = knnMA_[1] < knnMA_ and knnMA_[1] <= knnMA_[2]
    knnMA_Switch_Dn = knnMA_[1] > knnMA_ and knnMA_[1] >= knnMA_[2]
    knnMA_Neutral = knnMA_col == Neuknn_col and knnMA_col[1] != Neuknn_col
    greenBG = green and (not green[1])
    redBG = red and (not red[1])
    alertcondition(knnMA_cross_Over_Ma, title='Knn Crossover Average Knn', message='Knn Crossover Average Knn')
    alertcondition(knnMA_cross_Under_Ma, title='Knn Crossunder Average Knn', message='Knn Crossunder Average Knn')
    alertcondition(knnMA_cross_Over_Close, title='Knn Crossover Close', message='Knn Crossover Close')
    alertcondition(knnMA_cross_Under_Close, title='Knn Crossunder Close', message='Knn Crossunder Close')
    alertcondition(knnMA_Switch_Up, title='Knn Switch Up', message='Knn Switch Up')
    alertcondition(knnMA_Switch_Dn, title='Knn Switch Dn', message='Knn Switch Dn')
    alertcondition(knnMA_Neutral, title='Knn is Neutral', message='Knn is Neutral')
    alertcondition(greenBG, title='Positive Prediction', message='Positive Prediction')
    alertcondition(redBG, title='Negative Prediction', message='Negative Prediction')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
