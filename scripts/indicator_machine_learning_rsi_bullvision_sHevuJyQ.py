"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_import import shadowed_namespace
from pynecore.lib import (
    array, bar_index, barcolor, barstate, close, color, display, fill, input,
    math, na, plot, position, script, string, ta, table
)
from pynecore.types import Color, Persistent, Series, Table
import lib.TradingView.ta.v7 as ta__ren____lib


ta__ren__ = shadowed_namespace(ta__ren____lib, ta)

group_rsi: str = '📊 ================ RSI Base Settings ================'
group_threshold: str = '📏 ================ Threshold Settings ================'
group_knn: str = '🧠 ================ KNN Machine Learning ================'
group_filter: str = '🔍 ================ Advanced Filtering ================'
group_visual: str = '🎨 ================ Visual Settings ================'


@script.indicator(' Machine Learning RSI ║ BullVision', shorttitle='🤖🧠 Machine Learning RSI ║ BullVision🤖🧠', overlay=False)
def main(
    rsiLength=input.int(14, 'RSI Length', minval=1, group=group_rsi),
    useSmoothing=input.bool(True, 'Apply Moving Average', group=group_rsi),
    smoothingLength=input.int(3, 'MA Length', minval=1, group=group_rsi),
    maType=input.string('ALMA', 'Moving Average Type', options=('SMA', 'EMA', 'DEMA', 'TEMA', 'WMA', 'VWMA', 'SMMA', 'HMA', 'LSMA', 'ALMA'), group=group_rsi),
    almaSigma=input.int(4, 'ALMA Sigma', minval=1, group=group_rsi),
    rsiOverbought=input.int(70, ' Overbought Level', minval=50, maxval=100, group=group_threshold),
    rsiOversold=input.int(30, ' Oversold Level', minval=0, maxval=50, group=group_threshold),
    useKnn=input.bool(True, 'Enable KNN Machine Learning', group=group_knn),
    knnNeighbors=input.int(5, 'K - Number of Neighbors', minval=1, maxval=50, group=group_knn),
    knnLookback=input.int(100, 'Historical Period for KNN', minval=20, maxval=500, group=group_knn),
    knnWeight=input.float(0.4, 'ML Weight vs Standard RSI', minval=0.0, maxval=1.0, step=0.1, group=group_knn),
    featureCount=input.int(3, 'Number of Features', minval=1, maxval=5, tooltip='Number of characteristics for finding similar market conditions', group=group_knn),
    useFilter=input.bool(True, 'Apply Additional Smoothing', group=group_filter),
    filterMethod=input.string('Kalman', 'Smoothing Method', options=('None', 'Kalman', 'DoubleEMA', 'ALMA'), group=group_filter),
    filterStrength=input.float(0.3, 'Smoothing Parameter', minval=0.01, maxval=1.0, step=0.01, group=group_filter),
    neonEffect=input.bool(True, 'Neon Effect', tooltip='Enable vibrant neon-like colors', group=group_visual),
    colorScheme=input.string('Classic', 'Color Palette', options=('Classic', 'Deuteranopia', 'Protanopia', 'Tritanopia', 'Monochrome'), group=group_visual),
    colorMode=input.string('Trend Following', 'Coloring Mode', options=('None', 'Trend Following', 'Impulse'), group=group_visual)
):
    __block_result__ = (na, na)
    __switch__ = colorScheme
    if __switch__ == 'Classic':
        __block_result__ = (color.rgb(0, 255, 187) if neonEffect else color.rgb(0, 183, 18), color.rgb(255, 17, 0) if neonEffect else color.rgb(195, 0, 16))
    elif __switch__ == 'Deuteranopia':
        __block_result__ = (color.rgb(0, 170, 255), color.rgb(255, 204, 0))
    elif __switch__ == 'Protanopia':
        __block_result__ = (color.rgb(0, 170, 230), color.rgb(230, 175, 0))
    elif __switch__ == 'Tritanopia':
        __block_result__ = (color.rgb(255, 112, 0), color.rgb(0, 33, 171))
    elif __switch__ == 'Monochrome':
        __block_result__ = (color.rgb(222, 226, 230), color.rgb(73, 80, 87))
    bullColor, bearColor = __block_result__
    def calcMovingAverage(type, src: Series, length, sigma):
        result: float = na(float)
        if type == 'SMA':
            result = ta__ren__.sma(src, length)
        elif type == 'EMA':
            result = ta__ren__.ema(src, length)
        elif type == 'DEMA':
            e1 = ta__ren__.ema(src, length)
            e2 = ta__ren__.ema(e1, length)
            result = 2 * e1 - e2
        elif type == 'TEMA':
            e1 = ta__ren__.ema(src, length)
            e2 = ta__ren__.ema(e1, length)
            e3 = ta__ren__.ema(e2, length)
            result = 3 * (e1 - e2) + e3
        elif type == 'WMA':
            norm: float = 0.0
            sum: float = 0.0
            for i in pine_range(0, length - 1, 1):
                weight = length - i
                norm = norm + weight
                sum = sum + src[i] * weight
            result = sum / norm
        elif type == 'VWMA':
            result = ta__ren__.vwma(src, length)
        elif type == 'SMMA':
            result = ta__ren__.rma(src, length)
        elif type == 'HMA':
            result = ta__ren__.hma(src, length)
        elif type == 'LSMA':
            result = ta__ren__.linreg(src, length, 0)
        elif type == 'ALMA':
            result = ta__ren__.alma(src, length, 0.85, sigma)
        return result

    baseRsi = ta__ren__.rsi(close, rsiLength)
    smoothedRsi = calcMovingAverage(maType, baseRsi, smoothingLength, almaSigma)
    standardRsi: Series = smoothedRsi if useSmoothing else baseRsi
    def getMomentum(source: Series, length):
        return source - source[length]

    def getVolatility(source, length):
        return ta__ren__.stdev(source, length)

    def getSlope(source, length):
        return ta__ren__.linreg(source, length, 0) - ta__ren__.linreg(source, length, 1)

    def normalize(source, length):
        maxVal = ta__ren__.highest(source, length)
        minVal = ta__ren__.lowest(source, length)
        valueRange = maxVal - minVal
        return (source - minVal) / valueRange if valueRange != 0 else 0.5

    def euclideanDistance(v1, v2):
        sum: float = 0.0
        for i in pine_range(0, array.size(v1) - 1, 1):
            sum = sum + math.pow(array.get(v1, i) - array.get(v2, i), 2)
        return math.sqrt(sum)

    def calculateAdaptiveThresholds(src, period, percentile):
        rsiValues: Persistent[list[float]] = array.new_float(0)
        if barstate.isfirst or array.size(rsiValues) > period:
            array.clear(rsiValues)
        array.push(rsiValues, src)
        if array.size(rsiValues) > period:
            array.shift(rsiValues)
        sortedValues = array.copy(rsiValues)
        array.sort(sortedValues)
        lowIndex: int = math.floor(array.size(sortedValues) * percentile / 100)
        highIndex: int = math.floor(array.size(sortedValues) * (100 - percentile) / 100)
        lowVal = array.get(sortedValues, lowIndex) if array.size(sortedValues) > 0 and lowIndex < array.size(sortedValues) else 30
        highVal = array.get(sortedValues, highIndex) if array.size(sortedValues) > 0 and highIndex < array.size(sortedValues) else 70
        return (lowVal, highVal)

    def knnEnhancedRsi():
        __hist_standardRsi__: Series = standardRsi[0]
        enhancedRsi: float = standardRsi
        knnDivergence: float = 0.0
        effectiveK: int = 0
        overBoughtCandidates: Persistent[list[float]] = array.new_float(0)
        overSoldCandidates: Persistent[list[float]] = array.new_float(0)
        array.clear(overBoughtCandidates)
        array.clear(overSoldCandidates)
        currentPoint: Persistent[list[float]] = array.new_float(0)
        array.clear(currentPoint)
        array.push(currentPoint, normalize(standardRsi, knnLookback))
        if featureCount >= 2:
            array.push(currentPoint, normalize(getMomentum(standardRsi, 3), knnLookback))
        if featureCount >= 3:
            array.push(currentPoint, normalize(getVolatility(standardRsi, 10), knnLookback))
        if featureCount >= 4:
            array.push(currentPoint, normalize(getSlope(standardRsi, 5), knnLookback))
        if featureCount >= 5:
            array.push(currentPoint, normalize(getMomentum(close, 5), knnLookback))
        distances: Persistent[list[float]] = array.new_float(0)
        indices: Persistent[list[int]] = array.new_int(0)
        array.clear(distances)
        array.clear(indices)
        for i in pine_range(1, knnLookback, 1):
            if i < bar_index:
                historicalPoint: Persistent[list[float]] = array.new_float(0)
                array.clear(historicalPoint)
                array.push(historicalPoint, normalize(__hist_standardRsi__[i], knnLookback))
                if featureCount >= 2:
                    array.push(historicalPoint, normalize(getMomentum(__hist_standardRsi__[i], 3), knnLookback))
                if featureCount >= 3:
                    array.push(historicalPoint, normalize(getVolatility(__hist_standardRsi__[i], 10), knnLookback))
                if featureCount >= 4:
                    array.push(historicalPoint, normalize(getSlope(__hist_standardRsi__[i], 5), knnLookback))
                if featureCount >= 5:
                    array.push(historicalPoint, normalize(getMomentum(close[i], 5), knnLookback))
                if array.size(currentPoint) == array.size(historicalPoint):
                    dist = euclideanDistance(currentPoint, historicalPoint)
                    array.push(distances, dist)
                    array.push(indices, i)
                array.clear(historicalPoint)
        if array.size(distances) > 1:
            for i in pine_range(0, array.size(distances) - 2, 1):
                for j in pine_range(0, array.size(distances) - 2 - i, 1):
                    if array.get(distances, j) > array.get(distances, j + 1):
                        tempDist = array.get(distances, j)
                        array.set(distances, j, array.get(distances, j + 1))
                        array.set(distances, j + 1, tempDist)
                        tempIdx = array.get(indices, j)
                        array.set(indices, j, array.get(indices, j + 1))
                        array.set(indices, j + 1, tempIdx)
            weightedSum: float = 0.0
            weightSum: float = 0.0
            effectiveK = math.min(knnNeighbors, array.size(distances))
            if effectiveK > 0:
                for i in pine_range(0, effectiveK - 1, 1):
                    if i < array.size(distances):
                        idx = array.get(indices, i)
                        dist = array.get(distances, i)
                        weight = 1.0 if dist < 0.0001 else 1.0 / dist
                        neighborRsi: float = na(float)
                        if idx < bar_index:
                            neighborRsi = __hist_standardRsi__[idx - 1]
                            futureReturn: float = na(float)
                            if idx + 5 < bar_index + 1 and (not na(close[idx + 5])) and (not na(close[idx])):
                                futureReturn = close[idx + 5] - close[idx]
                            if not na(futureReturn):
                                if futureReturn > close[idx] * 0.02:
                                    array.push(overBoughtCandidates, __hist_standardRsi__[idx])
                                if futureReturn < close[idx] * -0.02:
                                    array.push(overSoldCandidates, __hist_standardRsi__[idx])
                        if not na(neighborRsi):
                            weightedSum = weightedSum + neighborRsi * weight
                            weightSum = weightSum + weight
                if weightSum > 0.0:
                    knnRsi__000000d9__ = weightedSum / weightSum
                    enhancedRsi = (1.0 - knnWeight) * standardRsi + knnWeight * knnRsi__000000d9__
                    enhancedRsi = math.max(0.0, math.min(100.0, enhancedRsi))
                    diffSum: float = 0.0
                    count: int = 0
                    for i in pine_range(0, effectiveK - 1, 1):
                        if i < array.size(distances):
                            idx = array.get(indices, i)
                            if idx < bar_index:
                                diffSum = diffSum + math.abs(standardRsi - __hist_standardRsi__[idx])
                                count = count + 1
                    knnDivergence = diffSum / count if count > 0 else 0.0
        adaptiveOverboughtML = array.avg(overBoughtCandidates) if array.size(overBoughtCandidates) > 0 else 70
        adaptiveOversoldML = array.avg(overSoldCandidates) if array.size(overSoldCandidates) > 0 else 30
        return (enhancedRsi, knnDivergence, effectiveK, adaptiveOversoldML, adaptiveOverboughtML)

    knnRsi, knnDivergence, kEffective, adaptiveOversoldML, adaptiveOverboughtML = knnEnhancedRsi()
    actualOversold = rsiOversold
    actualOverbought = rsiOverbought
    mlRsi = knnRsi if useKnn else standardRsi
    __block_result_1__ = na
    __switch__ = filterMethod
    if __switch__ == 'None':
        __block_result_1__ = mlRsi
    elif __switch__ == 'Kalman':
        kfRsi: Persistent[float] = na(float)
        kfRsi = mlRsi if na(kfRsi) else kfRsi + filterStrength * (mlRsi - kfRsi)
        __block_result_1__ = kfRsi
    elif __switch__ == 'DoubleEMA':
        ema1: Persistent[float] = na(float)
        ema2: Persistent[float] = na(float)
        ema1 = ta__ren__.ema(mlRsi, math.round(filterStrength * 10))
        ema2 = ta__ren__.ema(ema1, math.round(filterStrength * 5))
        __block_result_1__ = ema2
    elif __switch__ == 'ALMA':
        __block_result_1__ = ta__ren__.alma(mlRsi, math.round(filterStrength * 20), 0, 6)
    else:
        __block_result_1__ = mlRsi
    filteredRsi = __block_result_1__
    finalRsi = filteredRsi if useFilter else mlRsi
    __block_result_2__ = na
    __switch__ = colorMode
    if __switch__ == 'None':
        __block_result_2__ = na
    elif __switch__ == 'Trend Following':
        __block_result_2__ = bullColor if finalRsi > 50 else bearColor
    elif __switch__ == 'Impulse':
        __block_result_2__ = bullColor if finalRsi > actualOverbought else bearColor if finalRsi < actualOversold else color.white if finalRsi < 55 and finalRsi > 45 else color.gray
    indicatorColor: Color = __block_result_2__
    t_: int = 20
    rsiLine = plot(finalRsi, 'RSI KNN', indicatorColor if finalRsi > 50 else indicatorColor, 3)
    midLine = plot(50, '50 Level', color.new(color.white, 70), 1)
    fill(rsiLine, midLine, finalRsi if finalRsi > 50 else 50, 50 if finalRsi > 50 else finalRsi, (indicatorColor if finalRsi > 50 else color.new('#00000000')) if neonEffect else color.new('#00000000'), (color.new('#00000000') if finalRsi > 50 else indicatorColor) if neonEffect else color.new('#00000000'))
    obUpper = plot(100, '', color.new(bearColor, 0), display=display.none)
    obLower = plot(actualOverbought, '', color.new(bearColor, 0), 1)
    obMid = plot((100 + actualOverbought) / 2, '', display=display.none)
    osUpper = plot(actualOversold, '', color.new(bullColor, 0), 1)
    osLower = plot(0, '', color.new(bullColor, 0), display=display.none)
    osMid = plot(actualOversold / 2, '', display=display.none)
    barcolor(color.new(bullColor, t_) if finalRsi > 50 else color.new(bearColor, t_))
    modeUsed: str = colorMode
    __block_result_3__ = na
    __switch__ = colorMode
    if __switch__ == 'Trend Following':
        __block_result_3__ = 'Bullish Trend' if finalRsi > 50 else 'Bearish Trend'
    elif __switch__ == 'Impulse':
        __block_result_3__ = 'Bullish Impulse' if finalRsi > actualOverbought else 'Bearish Impulse' if finalRsi < actualOversold else 'None'
    else:
        __block_result_3__ = 'None'
    context: str = __block_result_3__
    mlStatus: str = 'YES' if useKnn else 'NO'
    tableColor: Color = color.new('#160D0DB3')
    myTable: Persistent[Table] = table.new(position=position.top_right, columns=4, rows=6, bgcolor=color.new('#160D0DB3'), border_color=color.new('#160D0DB3'), border_width=1, frame_color=color.new('#FFFFFF'), frame_width=1, force_overlay=True)
    if bar_index % 10 == 0:
        table.cell(myTable, 0, 0, 'Mode', text_color=color.white, bgcolor=tableColor)
        table.cell(myTable, 1, 0, modeUsed, text_color=color.white, bgcolor=tableColor)
        table.cell(myTable, 0, 1, 'Detected', text_color=color.white, bgcolor=tableColor)
        table.cell(myTable, 1, 1, context, text_color=color.white, bgcolor=tableColor)
        table.cell(myTable, 0, 2, 'Machine Learning', text_color=color.white, bgcolor=tableColor)
        table.cell(myTable, 1, 2, mlStatus, text_color=color.white, bgcolor=tableColor)
        table.cell(myTable, 0, 3, 'OB/OS Thresholds', text_color=color.white, bgcolor=tableColor)
        table.cell(myTable, 1, 3, string.tostring(actualOverbought) + ' / ' + string.tostring(actualOversold), text_color=color.white, bgcolor=color.new(color.black, 70))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)