"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    alertcondition, array, close, color, currency, display, fill, high,
    input, location, low, math, na, nz, open, plot, plotshape, request, script, shape, size,
    strategy, syminfo, ta, volume
)
from pynecore.types import Color, Persistent, Series


@script.strategy('AI SuperTrend x Pivot Percentile - Strategy [PresentTrading]', shorttitle='AI ST x Pivot Percentile - Strategy [PresentTrading]', overlay=True, precision=3, commission_value=0.1, commission_type=strategy.commission.percent, slippage=1, currency=currency.USD, default_qty_type=strategy.percent_of_equity, default_qty_value=10, initial_capital=10000, margin_long=0, margin_short=0, close_by_id=True)
def main(
    tradeDirection=input.string('Both', 'Select Trading Direction', options=('Long', 'Short', 'Both'), group='Trade Setup'),
    k=input.int(6, title='Neighbors', minval=1, maxval=100, group='AI Settings', inline='AI1', tooltip='Number of nearest neighbors in KNN algorithm.'),
    n_=input.int(48, title='Data Points', minval=1, maxval=100, group='AI Settings', inline='AI1', tooltip='Number of data points to consider for KNN.'),
    k2=input.int(6, title='2nd Neighbors', minval=1, maxval=100, group='AI Settings', inline='AI2', tooltip='Number of nearest neighbors for the second KNN algorithm.'),
    n2_=input.int(48, title='2nd Data Points', minval=1, maxval=100, group='AI Settings', inline='AI2', tooltip='Number of data points for the second KNN algorithm.'),
    higherTf1=input.timeframe('360', 'Higher Time Frame for 1st ST', group='Super Trend Settings'),
    higherTf2=input.timeframe('720', 'Higher Time Frame for 2nd ST', group='Super Trend Settings'),
    len=input.int(10, 'Length', minval=1, group='Super Trend Settings'),
    factor=input.float(3.5, 'Factor', step=0.1, group='Super Trend Settings'),
    maSrc=input.string('WMA', 'MA Source', options=('SMA', 'EMA', 'WMA', 'RMA', 'VWMA'), group='Super Trend Settings'),
    len2=input.int(5, '2nd Length', minval=1, group='Super Trend Settings'),
    factor2=input.float(3.0, '2nd Factor', step=0.1, group='Super Trend Settings'),
    KNN_PriceLen=input.int(10, 'Price Trend', minval=2, maxval=500, step=10, group='AI Trend Prediction', inline='AITrend1'),
    KNN_STLen=input.int(80, 'Prediction Trend', minval=2, maxval=500, step=10, group='AI Trend Prediction', inline='AITrend1'),
    KNN_PriceLen2=input.int(10, '2nd Price Trend', minval=2, maxval=500, step=10, group='AI Trend Prediction', inline='AITrend2'),
    KNN_STLen2=input.int(80, '2nd Prediction Trend', minval=2, maxval=500, step=10, group='AI Trend Prediction', inline='AITrend2'),
    length=input.int(14, 'Length for Pivot Percentile', minval=1, maxval=20, group='Pivot Percentile Settings'),
    adxLength=input.int(14, 'ADX Length', minval=1, group='ADX and DMI Settings'),
    adxTf=input.timeframe('D', 'Time Frame for ADX and DMI Filter', group='ADX and DMI Settings'),
    useAdxFilter=input.bool(True, 'Use ADX and DMI Filter?', group='ADX and DMI Settings'),
    aisignals=input.bool(True, 'Enable AI Trend Signals', group='Other Settings'),
    Bullish_col=input.color(color.lime, 'Bullish Color', group='Other Settings'),
    Bearish_col=input.color(color.red, 'Bearish Color', group='Other Settings'),
    upCol=input.color(color.lime, 'Bullish Color for SuperTrend', group='Other Settings'),
    dnCol=input.color(color.red, 'Bearish Color for SuperTrend', group='Other Settings'),
    neCol=input.color(color.blue, 'Neutral Color for SuperTrend', group='Other Settings')
):
    n = math.max(k, n_)
    n2 = math.max(k2, n2_)
    HTF_Close: Series = request.security(syminfo.tickerid, adxTf, close)
    HTF_High: Series = request.security(syminfo.tickerid, adxTf, high)
    HTF_Low: Series = request.security(syminfo.tickerid, adxTf, low)
    deltaHigh = HTF_High - HTF_High[1]
    deltaLow = HTF_Low[1] - HTF_Low
    plusDM = deltaHigh if deltaHigh > deltaLow and deltaHigh > 0 else 0
    minusDM = deltaLow if deltaLow > deltaHigh and deltaLow > 0 else 0
    ATR = ta.wma(math.abs(HTF_High - HTF_Low) + math.abs(HTF_High - HTF_Close[1]) + math.abs(HTF_Low - HTF_Close[1]), adxLength)
    plusDI = 100 * ta.wma(plusDM, adxLength) / ATR
    minusDI = 100 * ta.wma(minusDM, adxLength) / ATR
    DX = 100 * math.abs(plusDI - minusDI) / (plusDI + minusDI)
    ADX = ta.wma(DX, adxLength)
    TfClose1 = request.security(syminfo.tickerid, higherTf1, close)
    __block_result__ = na
    __switch__ = maSrc
    if __switch__ == 'SMA':
        __block_result__ = ta.sma(TfClose1 * volume, len) / ta.sma(volume, len)
    elif __switch__ == 'EMA':
        __block_result__ = ta.ema(TfClose1 * volume, len) / ta.ema(volume, len)
    elif __switch__ == 'WMA':
        __block_result__ = ta.wma(TfClose1 * volume, len) / ta.wma(volume, len)
    elif __switch__ == 'RMA':
        __block_result__ = ta.rma(TfClose1 * volume, len) / ta.rma(volume, len)
    elif __switch__ == 'VWMA':
        __block_result__ = ta.vwma(TfClose1 * volume, len) / ta.vwma(volume, len)
    vwma1 = __block_result__
    atr: Series = request.security(syminfo.tickerid, higherTf1, ta.atr(len))
    upperBand: Series = vwma1 + factor * atr
    lowerBand: Series = vwma1 - factor * atr
    prevLowerBand = nz(lowerBand[1])
    prevUpperBand = nz(upperBand[1])
    TfClose2 = request.security(syminfo.tickerid, higherTf2, close)
    __block_result_1__ = na
    __switch__ = maSrc
    if __switch__ == 'SMA':
        __block_result_1__ = ta.sma(TfClose2 * volume, len2) / ta.sma(volume, len2)
    elif __switch__ == 'EMA':
        __block_result_1__ = ta.ema(TfClose2 * volume, len2) / ta.ema(volume, len2)
    elif __switch__ == 'WMA':
        __block_result_1__ = ta.wma(TfClose2 * volume, len2) / ta.wma(volume, len2)
    elif __switch__ == 'RMA':
        __block_result_1__ = ta.rma(TfClose2 * volume, len2) / ta.rma(volume, len2)
    elif __switch__ == 'VWMA':
        __block_result_1__ = ta.vwma(TfClose2 * volume, len2) / ta.vwma(volume, len2)
    vwma2 = __block_result_1__
    atr2: Series = request.security(syminfo.tickerid, higherTf2, ta.atr(len2))
    upperBand2: Series = vwma2 + factor2 * atr2
    lowerBand2: Series = vwma2 - factor2 * atr2
    prevLowerBand2 = nz(lowerBand2[1])
    prevUpperBand2 = nz(upperBand2[1])
    lowerBand = lowerBand if lowerBand > prevLowerBand or close[1] < prevLowerBand else prevLowerBand
    upperBand = upperBand if upperBand < prevUpperBand or close[1] > prevUpperBand else prevUpperBand
    direction: Series[int] = na(int)
    superTrend: Series[float] = na(float)
    lowerBand2 = lowerBand2 if lowerBand2 > prevLowerBand2 or close[1] < prevLowerBand2 else prevLowerBand2
    upperBand2 = upperBand2 if upperBand2 < prevUpperBand2 or close[1] > prevUpperBand2 else prevUpperBand2
    direction2: Series[int] = na(int)
    superTrend2: Series[float] = na(float)
    prevSuperTrend = superTrend[1]
    if na(atr[1]):
        direction = 1
    elif prevSuperTrend == prevUpperBand:
        direction = -1 if close > upperBand else 1
    else:
        direction = 1 if close < lowerBand else -1
    superTrend = lowerBand if direction == -1 else upperBand
    prevSuperTrend2 = superTrend2[1]
    if na(atr2[1]):
        direction2 = 1
    elif prevSuperTrend2 == prevUpperBand2:
        direction2 = -1 if close > upperBand2 else 1
    else:
        direction2 = 1 if close < lowerBand2 else -1
    superTrend2 = lowerBand2 if direction2 == -1 else upperBand2
    price: Series = ta.wma(close, KNN_PriceLen)
    sT: Series = ta.wma(superTrend, KNN_STLen)
    data: list[float] = array.new_float(n)
    labels: list[int] = array.new_int(n)
    for i in pine_range(0, n - 1, 1):
        array.set(data, i, superTrend[i])
        label_i = 1 if price[i] > sT[i] else 0
        array.set(labels, i, label_i)
    price2: Series = ta.wma(close, KNN_PriceLen2)
    sT2: Series = ta.wma(superTrend2, KNN_STLen2)
    data2: list[float] = array.new_float(n)
    labels2: list[int] = array.new_int(n)
    for i in pine_range(0, n - 1, 1):
        array.set(data2, i, superTrend2[i])
        label_i2 = 1 if price2[i] > sT2[i] else 0
        array.set(labels2, i, label_i2)
    def distance(x1, x2):
        return math.abs(x1 - x2)

    def knn_weighted(data, labels, k, x):
        n1 = method_call('size', data)
        distances: list[float] = array.new_float(n1)
        indices: list[int] = array.new_int(n1)
        for i in pine_range(0, n1 - 1, 1):
            x_i = method_call('get', data, i)
            dist = distance(x, x_i)
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

    current_superTrend = superTrend
    label_ = knn_weighted(data, labels, k, current_superTrend)
    label_upTrend = 1 if label_ == 1 else 0
    label_downTrend = -1 if label_ == 0 else 0
    current_superTrend2 = superTrend2
    label2_ = knn_weighted(data2, labels2, k, current_superTrend2)
    label2_upTrend = 1 if label2_ == 1 else 0
    label2_downTrend = -1 if label2_ == 0 else 0
    col: Series = upCol if label_ == 1 else dnCol if label_ == 0 else neCol
    plot(current_superTrend, color=col, title='Volume Super Trend AI')
    upTrend = plot(current_superTrend if superTrend == lowerBand else na, title='Up Volume Super Trend AI', color=col, style=plot.style_linebr)
    Middle = plot((open + close) / 2, display=display.none, editable=False)
    downTrend = plot(current_superTrend if superTrend == upperBand else na, title='Down Volume Super Trend AI', color=col, style=plot.style_linebr)
    fill_col = color.new(col, 95)
    fill(Middle, upTrend, fill_col, fillgaps=False, title='Up Volume Super Trend AI')
    fill(Middle, downTrend, fill_col, fillgaps=False, title='Down Volume Super Trend AI')
    col2: Series = upCol if label2_ == 1 else dnCol if label2_ == 0 else neCol
    plot(current_superTrend2, color=col2, title='Volume Super Trend AI 2')
    upTrend2 = plot(current_superTrend2 if superTrend2 == lowerBand2 else na, title='Up Volume Super Trend AI 2', color=col2, style=plot.style_linebr)
    downTrend2 = plot(current_superTrend2 if superTrend2 == upperBand2 else na, title='Down Volume Super Trend AI 2', color=col2, style=plot.style_linebr)
    fill_col2 = color.new(col2, 95)
    fill(Middle, upTrend2, fill_col2, fillgaps=False, title='Up Volume Super Trend AI 2')
    fill(Middle, downTrend2, fill_col2, fillgaps=False, title='Down Volume Super Trend AI 2')
    Start_TrendUp = col == upCol and (col[1] != upCol or col[1] == neCol) and aisignals
    Start_TrendDn = col == dnCol and (col[1] != dnCol or col[1] == neCol) and aisignals
    Start_TrendUp2 = col2 == upCol and (col2[1] != upCol or col2[1] == neCol) and aisignals
    Start_TrendDn2 = col2 == dnCol and (col2[1] != dnCol or col2[1] == neCol) and aisignals
    TrendUp = direction == -1 and direction[1] == 1 and (label_ == 1) and aisignals
    TrendDn = direction == 1 and direction[1] == -1 and (label_ == 0) and aisignals
    TrendUp2 = direction2 == -1 and direction2[1] == 1 and (label2_ == 1) and aisignals
    TrendDn2 = direction2 == 1 and direction2[1] == -1 and (label2_ == 0) and aisignals
    plotshape(superTrend if Start_TrendUp else na, location=location.absolute, style=shape.circle, size=size.tiny, color=Bullish_col, title='AI Bullish Trend Start')
    plotshape(superTrend if Start_TrendDn else na, location=location.absolute, style=shape.circle, size=size.tiny, color=Bearish_col, title='AI Bearish Trend Start')
    plotshape(superTrend if TrendUp else na, location=location.absolute, style=shape.triangleup, size=size.small, color=Bullish_col, title='AI Bullish Trend Signal')
    plotshape(superTrend if TrendDn else na, location=location.absolute, style=shape.triangledown, size=size.small, color=Bearish_col, title='AI Bearish Trend Signal')
    plotshape(superTrend2 if Start_TrendUp2 else na, location=location.absolute, style=shape.circle, size=size.tiny, color=Bullish_col, title='AI Bullish Trend Start 2')
    plotshape(superTrend2 if Start_TrendDn2 else na, location=location.absolute, style=shape.circle, size=size.tiny, color=Bearish_col, title='AI Bearish Trend Start 2')
    plotshape(superTrend2 if TrendUp2 else na, location=location.absolute, style=shape.triangleup, size=size.small, color=Bullish_col, title='AI Bullish Trend Signal')
    plotshape(superTrend2 if TrendDn2 else na, location=location.absolute, style=shape.triangledown, size=size.small, color=Bearish_col, title='AI Bearish Trend Signal')
    def calculatePercentiles(src, lengths, percentile):
        result: list[float] = array.new_float(0)
        for length__000000bf__ in lengths:
            value = ta.percentile_nearest_rank(src, length__000000bf__, percentile)
            array.push(result, value)
        return result

    def calculateTrendCounts(highPercentiles, lowPercentiles, highest_high, lowest_low):
        countBull: int = 0
        countBear: int = 0
        weakBullCount: int = 0
        weakBearCount: int = 0
        for i in pine_range(0, array.size(highPercentiles) - 1, 1):
            trendBullHigh = array.get(highPercentiles, i) > highest_high
            trendBullLow = array.get(lowPercentiles, i) > highest_high
            trendBearHigh = array.get(highPercentiles, i) < lowest_low
            trendBearLow = array.get(lowPercentiles, i) < lowest_low
            weakBull = array.get(lowPercentiles, i) < highest_high and array.get(lowPercentiles, i) > lowest_low
            weakBear = array.get(highPercentiles, i) > lowest_low and array.get(highPercentiles, i) < highest_high
            countBull = countBull + (1 if trendBullHigh else 0) + (1 if trendBullLow else 0)
            countBear = countBear + (1 if trendBearHigh else 0) + (1 if trendBearLow else 0)
            weakBullCount = weakBullCount + (1 if weakBull else 0)
            weakBearCount = weakBearCount + (1 if weakBear else 0)
        return (countBull, countBear, weakBullCount, weakBearCount)

    lengths: list[int] = array.new_int(7)
    array.set(lengths, 0, length)
    array.set(lengths, 1, length * 2)
    array.set(lengths, 2, length * 3)
    array.set(lengths, 3, length * 4)
    array.set(lengths, 4, length * 5)
    array.set(lengths, 3, length * 6)
    array.set(lengths, 4, length * 7)
    percentilesHigh = calculatePercentiles(high, lengths, 75)
    percentilesLow = calculatePercentiles(low, lengths, 25)
    highest_high = ta.percentile_nearest_rank(high, 144, 75)
    lowest_low = ta.percentile_nearest_rank(low, 144, 25)
    countBull, countBear, weakBullCount, weakBearCount = calculateTrendCounts(percentilesHigh, percentilesLow, highest_high, lowest_low)
    bullStrength = countBull + 0.5 * weakBullCount - 0.5 * weakBearCount - countBear
    bearStrength = countBear + 0.5 * weakBearCount - 0.5 * weakBullCount - countBull
    currentTrendValue = bullStrength - bearStrength
    longAdxCondition = ADX > 20 and plusDI > minusDI if useAdxFilter else True
    shortAdxCondition = ADX > 20 and minusDI > plusDI if useAdxFilter else True
    AIST_longCondition = direction < 0 and label_ == 1 and (direction2 < 0) and (label2_ == 1) and longAdxCondition
    AIST_shortCondition = direction > 0 and label_ == 0 and (direction2 > 0) and (label2_ == 0) and shortAdxCondition
    longExitCondition1 = direction == -1 and label_ == 1
    longExitCondition2 = direction2 == -1 and label2_ == 1
    shortExitCondition1 = direction == 1 and label_ == 0
    shortExitCondition2 = direction2 == 1 and label2_ == 0
    AIST_longExitCondition = not (TrendUp or TrendUp2)
    AIST_shortExitCondition = not (TrendDn or TrendDn2)
    PPR_longCondition = currentTrendValue > 0
    PPR_shortCondition = currentTrendValue < 0
    longCondition = AIST_longCondition and PPR_longCondition
    shortCondition = AIST_shortCondition and PPR_shortCondition
    longExitCondition = AIST_longExitCondition or PPR_shortCondition
    shortExitCondition = AIST_shortExitCondition or PPR_longCondition
    longTrailingStop = superTrend - atr * factor
    shortTrailingStop = superTrend + atr * factor
    if tradeDirection == 'Long' or tradeDirection == 'Both':
        if longCondition:
            strategy.entry('Long', strategy.long)
        if longExitCondition:
            strategy.exit('Exit Long', 'Long', stop=longTrailingStop)
    if tradeDirection == 'Short' or tradeDirection == 'Both':
        if shortCondition:
            strategy.entry('Short', strategy.short)
        if shortExitCondition:
            strategy.exit('Exit Short', 'Short', stop=shortTrailingStop)
    alertcondition(longCondition, title='Long Entry Alert', message='Long Entry Signal Generated')
    alertcondition(shortCondition, title='Short Entry Alert', message='Short Entry Signal Generated')
    alertcondition(longExitCondition, title='Long Exit Alert', message='Long Exit Signal Generated')
    alertcondition(shortExitCondition, title='Short Exit Alert', message='Short Exit Signal Generated')
    plotshape(superTrend if Start_TrendUp else na, location=location.absolute, style=shape.circle, size=size.tiny, color=Bullish_col, title='AI Bullish Trend Start')
    plotshape(superTrend if Start_TrendDn else na, location=location.absolute, style=shape.circle, size=size.tiny, color=Bearish_col, title='AI Bearish Trend Start')
    plotshape(superTrend if TrendUp else na, location=location.absolute, style=shape.triangleup, size=size.small, color=Bullish_col, title='AI Bullish Trend Signal')
    plotshape(superTrend if TrendDn else na, location=location.absolute, style=shape.triangledown, size=size.small, color=Bearish_col, title='AI Bearish Trend Signal')
    plotshape(superTrend2 if Start_TrendUp2 else na, location=location.absolute, style=shape.circle, size=size.tiny, color=Bullish_col, title='AI Bullish Trend Start 2')
    plotshape(superTrend2 if Start_TrendDn2 else na, location=location.absolute, style=shape.circle, size=size.tiny, color=Bearish_col, title='AI Bearish Trend Start 2')
    plotshape(superTrend2 if TrendUp2 else na, location=location.absolute, style=shape.triangleup, size=size.small, color=Bullish_col, title='AI Bullish Trend Signal')
    plotshape(superTrend2 if TrendDn2 else na, location=location.absolute, style=shape.triangledown, size=size.small, color=Bearish_col, title='AI Bearish Trend Signal')
    plotLong: Persistent[bool] = False
    plotShort: Persistent[bool] = False
    plotLong = PPR_longCondition
    plotShort = PPR_shortCondition
    pivotPointColor: Persistent[Color] = color.new(color.rgb(33, 150, 243), 95)
    plotshape(series=plotLong and high, title='Long Pivot Entry Point', location=location.belowbar, color=pivotPointColor, style=shape.circle, size=size.tiny)
    plotshape(series=plotShort and low, title='Short Pivot Entry Point', location=location.abovebar, color=pivotPointColor, style=shape.circle, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
