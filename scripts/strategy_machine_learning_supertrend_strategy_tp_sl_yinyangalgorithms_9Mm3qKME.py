"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt_copy
from pynecore.lib import (
    alert, array, barstate, close, color, display, fill, hl2, input, math,
    na, nz, open, plot, script, strategy, ta
)
from pynecore.types import Series


@script.strategy('Machine Learning: SuperTrend Strategy - Trailing Take Profit and Stop Loss [YinYangAlgorithms]', overlay=True, initial_capital=1000000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, process_orders_on_close=True, margin_long=0, margin_short=0, close_by_id=True)
def main(
    atrPeriod=input.int(4, 'ATR Length', minval=1, group='Supertrend', tooltip='ATR Length used to create the Original Supertrend.'),
    factor=input.float(2.94, 'Factor', minval=0.01, step=0.01, group='Supertrend', tooltip='Multiplier used to create the Original Supertrend.'),
    stoplossMult=input.float(2.5e-06, 'Stop Loss Multiplier', group='Supertrend', tooltip='0 = Don\'t use Stop Loss. Stop loss can be useful for helping to prevent false signals but also may result in more loss when hit and less profit when switching trends.'),
    takeprofitMult=input.float(0.022, 'Take Profit Multiplier', group='Supertrend', tooltip='Take Profits can be useful within the Supertrend Strategy to stop the price reverting all the way to the Stop Loss once it\'s been profitable.'),
    sameBarEntryAndExit=input.bool(False, 'Allow Same Bar Entry and Exit for Orders', group='Supertrend', tooltip='This allows you to enter and exit positions within the same bar.'),
    onlyUseSameTrendDirections=input.bool(True, 'Only Factor Same Trend Direction', group='Machine Learning', tooltip='Very useful for ensuring that data used in KNN is not manipulated by different SuperTrend Directional data. Please note, it doesn\'t effect KNN Exponential.'),
    useRationalQudratics=input.string('All', 'Rationalized Source Type', options=('All', 'Close', 'HL2', 'ATR', 'None'), group='Machine Learning', tooltip='Should we Rationalize only a specific source, All or None?'),
    useMachineLearning=input.string('KNN Average', 'Machine Learning Type', options=('KNN Average', 'KNN Exponential Average', 'Simple Average', 'None'), group='Machine Learning', tooltip='Are we using a Simple ML Average, KNN Mean Average, KNN Exponential Average or None?'),
    distanceType=input.string('Both', 'KNN Distance Type', options=('Both', 'Max', 'Min'), group='Machine Learning', tooltip='We need to check if distance is within the KNN Min/Max distance, which distance checks are we using.'),
    mlType=input.string('SMA', 'Machine Learning Smoothing Type', options=('SMA', 'EMA', 'VWMA'), group='Machine Learning', tooltip='How should we smooth our Fast and Slow ML Datas to be used in our KNN Distance calculation? SMA, EMA or VWMA?'),
    mlLength=input.int(100, 'Machine Learning Length', group='Machine Learning', tooltip='How far back is our Machine Learning going to keep data for.'),
    knnLength=input.int(2, 'k-Nearest Neighbour (KNN) Length', group='Machine Learning', tooltip='How many k-Nearest Neighbours will we account for?'),
    fastLength=input.int(3, 'Fast ML Data Length', group='Machine Learning', tooltip='What is our Fast ML Length?? This is used with our Slow Length to create our KNN Distance.'),
    slowLength=input.int(50, 'Slow ML Data Length', group='Machine Learning', tooltip='What is our Slow ML Length?? This is used with our Fast Length to create our KNN Distance.')
):
    rationalizeHL2 = useRationalQudratics == 'HL2' or useRationalQudratics == 'All'
    rationalizeClose = useRationalQudratics == 'Close' or useRationalQudratics == 'All'
    rationalizeATR = useRationalQudratics == 'ATR' or useRationalQudratics == 'All'
    distanceTypeMin = distanceType == 'Min' or distanceType == 'Both'
    distanceTypeMax = distanceType == 'Max' or distanceType == 'Both'
    def rationalQuadratic(_src: Series, _lookback, _relativeWeight, startAtBar):
        _currentWeight: float = 0.0
        _cumulativeWeight: float = 0.0
        _size = array.size(array.from_items(_src))
        for i in pine_range(0, _size + startAtBar, 1):
            y = _src[i]
            w = math.pow(1 + math.pow(i, 2) / (math.pow(_lookback, 2) * 2 * _relativeWeight), -_relativeWeight)
            _currentWeight = _currentWeight + y * w
            _cumulativeWeight = _cumulativeWeight + w
        yhat = _currentWeight / _cumulativeWeight
        return yhat

    def getSupertrend(factor, atrPeriod):
        src = rationalQuadratic(hl2, 8, 8.0, 25) if rationalizeHL2 else hl2
        atr: Series = rationalQuadratic(ta.atr(atrPeriod), 8, 8.0, 25) if rationalizeATR else ta.atr(atrPeriod)
        upperBand: Series = src + factor * atr
        lowerBand: Series = src - factor * atr
        prevLowerBand = nz(lowerBand[1])
        prevUpperBand = nz(upperBand[1])
        closeSrc: Series = rationalQuadratic(close, 8, 8.0, 25) if rationalizeClose else close
        lowerBand = lowerBand if lowerBand > prevLowerBand or closeSrc[1] < prevLowerBand else prevLowerBand
        upperBand = upperBand if upperBand < prevUpperBand or closeSrc[1] > prevUpperBand else prevUpperBand
        direction: Series[int] = na(int)
        superTrend: Series[float] = na(float)
        stoploss: float = lowerBand - lowerBand * stoplossMult if direction[1] == -1 else upperBand + upperBand * stoplossMult
        prevSuperTrend = superTrend[1]
        if na(atr[1]):
            direction = 1
        elif prevSuperTrend == prevUpperBand:
            direction = -1 if closeSrc > stoploss else 1
        else:
            direction = 1 if closeSrc < stoploss else -1
        superTrend = lowerBand if direction == -1 else upperBand
        return (superTrend, direction, stoploss)

    def getExponentialDataAverage(_data, _length):
        avg: float = 0.0
        maxLen = math.min(method_call('size', _data), _length)
        __block_result__ = na
        if maxLen > 0:
            for i in pine_range(0, maxLen - 1, 1):
                curData = method_call('get', _data, i)
                tempAvg = curData
                if i > 0:
                    for a in pine_range(0, i, 1):
                        tempAvg = tempAvg + array.get(_data, a)
                    tempAvg = math.avg(method_call('get', _data, 0), tempAvg / i)
                avg = avg + math.avg(method_call('get', _data, 0), math.avg(curData, tempAvg))
            __block_result__ = avg / _length
        else:
            __block_result__ = avg
        return __block_result__

    def knnAverage_fromDistance(_currentDirection, _dataFast, _dataSlow, _directions, _minDist, _maxDist):
        maxDist = True if not _minDist else _maxDist
        distances: list[float] = array.new_float(0)
        for i in pine_range(0, method_call('size', _dataSlow) - 1, 1):
            if not onlyUseSameTrendDirections or _currentDirection == method_call('get', _directions, i):
                distance = method_call('get', _dataSlow, i) - method_call('get', _dataFast, i)
                array.push(distances, distance)
        clonedDistances = udt_copy(distances)
        splicedDistances = method_call('slice', clonedDistances, 0, math.min(knnLength, method_call('size', clonedDistances)))
        maxDistanceAllowed = method_call('max', splicedDistances)
        minDistanceAllowed = method_call('min', splicedDistances)
        validDistances: list[float] = array.new_float(0)
        for i in pine_range(0, array.size(distances) - 1, 1):
            if (not maxDist or array.get(distances, i) <= maxDistanceAllowed) and (not _minDist or array.get(distances, i) >= minDistanceAllowed) and (not onlyUseSameTrendDirections or _currentDirection == method_call('get', _directions, i)):
                distAvg = (method_call('get', _dataSlow, i) + method_call('get', _dataFast, i)) / 2
                array.push(validDistances, distAvg)
        __block_result_1__ = na
        if useMachineLearning == 'KNN Exponential Average':
            __block_result_1__ = getExponentialDataAverage(validDistances, 1)
        else:
            __block_result_1__ = array.avg(validDistances)
        return __block_result_1__

    supertrendOG, directionOG, stoplossOG = getSupertrend(factor, atrPeriod)
    supertrend: Series[float] = supertrendOG
    direction: Series[int] = directionOG
    stoploss: Series[float] = stoplossOG
    if useMachineLearning != 'None':
        directions: list[int] = array.new_int(mlLength)
        for d in pine_range(0, mlLength - 1, 1):
            array.set(directions, d, direction[d])
        if useMachineLearning == 'Simple Average':
            supertrendData: list[float] = array.new_float(0)
            for i in pine_range(0, mlLength - 1, 1):
                if not onlyUseSameTrendDirections or direction == array.get(directions, i):
                    array.push(supertrendData, supertrend[i])
            supertrend = array.avg(supertrendData)
        else:
            supertrendFast: Series[float] = ta.sma(supertrend, fastLength) if mlType == 'SMA' else ta.ema(supertrend, fastLength) if mlType == 'EMA' else ta.vwma(supertrend, fastLength)
            supertrendSlow: Series[float] = ta.sma(supertrend, slowLength) if mlType == 'SMA' else ta.ema(supertrend, slowLength) if mlType == 'EMA' else ta.vwma(supertrend, slowLength)
            supertrendFastData: list[float] = array.new_float(mlLength)
            supertrendSlowData: list[float] = array.new_float(mlLength)
            for i in pine_range(0, mlLength - 1, 1):
                array.set(supertrendFastData, i, supertrendFast[i])
                array.set(supertrendSlowData, i, supertrendSlow[i])
            supertrend = knnAverage_fromDistance(direction, supertrendFastData, supertrendSlowData, directions, distanceTypeMin, distanceTypeMax)
        stoploss = supertrend - supertrend * stoplossMult if direction == -1 else supertrend + supertrend * stoplossMult
        direction = -1 if close > stoploss else 1
    takeprofit = supertrend + supertrend * takeprofitMult if direction == -1 else supertrend - supertrend * takeprofitMult
    supertrend = na if barstate.isfirst else supertrend
    bodyMiddle = plot(na if barstate.isfirst else (open + close) / 2, display=display.none)
    upTrend = plot(supertrend if direction < 0 else na, 'Up Trend', color=color.green, style=plot.style_linebr)
    downTrend = plot(na if direction < 0 else supertrend, 'Down Trend', color=color.red, style=plot.style_linebr)
    upTrendStoploss = plot((stoploss if direction < 0 else na) if stoplossMult != 0 else na, 'Stop Loss', color=color.green, style=plot.style_linebr)
    downTrendStoploss = plot((na if direction < 0 else stoploss) if stoplossMult != 0 else na, 'Stop Loss', color=color.red, style=plot.style_linebr)
    upTrendTakeprofit = plot((takeprofit if direction < 0 else na) if takeprofitMult != 0 else na, 'Take Profit', color=color.rgb(16, 105, 179), style=plot.style_linebr)
    downTrendTakeprofit = plot((na if direction < 0 else takeprofit) if takeprofitMult != 0 else na, 'Take Profit', color=color.rgb(206, 113, 1), style=plot.style_linebr)
    fill(bodyMiddle, upTrend, color.new(color.green, 90))
    fill(bodyMiddle, downTrend, color.new(color.red, 90))
    fill(upTrendStoploss, upTrend, color.new(color.green, 95))
    fill(downTrendStoploss, downTrend, color.new(color.red, 95))
    if direction != direction[1]:
        if direction == -1:
            strategy.entry('Buy', strategy.long, stop=stoploss, alert_message='Start LONG')
        else:
            strategy.entry('Sell', strategy.short, stop=stoploss, alert_message='Start SHORT')
    if takeprofitMult != 0:
        if direction == -1 and close > takeprofit:
            strategy.close('Buy', alert_message='Exit LONG')
        elif direction == 1 and close < takeprofit:
            strategy.close('Sell', alert_message='Exit LONG')
    if sameBarEntryAndExit and stoplossMult != 0:
        if direction[1] == -1 and close < stoploss[1]:
            strategy.close('Buy')
        elif direction[1] == 1 and close > stoploss[1]:
            strategy.close('Sell')
    if direction != direction[1] or (takeprofitMult != 0 and (direction == -1 and close > takeprofit or (direction == 1 and close < takeprofit))):
        alert('{{strategy.order.action}} | {{ticker}} | {{close}}', alert.freq_once_per_bar)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
