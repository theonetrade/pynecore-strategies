"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    array, close, color, currency, display, fill, input, location, math, na,
    nz, open, plot, plotshape, script, shape, size, strategy, ta, volume
)
from pynecore.types import Series

t1: str = 'Number of nearest neighbors in KNN algorithm (k): Increase to consider more neighbors, providing a more balanced view but possibly smoothing out local patterns. Decrease for fewer neighbors to make the algorithm more responsive to recent changes. \n\nNumber of data points to consider (n): Increase for more historical data, providing a broader context but possibly diluting recent trends. Decrease for less historical data to focus more on recent behavior.'
t2: str = 'Length of weighted moving average for price (KNN_PriceLen): Higher values create a smoother price line, influencing the KNN algorithm to be more stable but less sensitive to short-term price movements. Lower values enhance responsiveness in KNN predictions to recent price changes but may lead to more noise. \n\nLength of weighted moving average for SuperTrend (KNN_STLen): Higher values lead to a smoother SuperTrend line, affecting the KNN algorithm to emphasize long-term trends. Lower values make KNN predictions more sensitive to recent SuperTrend changes but may result in more volatility.'
t3: str = 'Length of the SuperTrend (len): Increase for a smoother trend line, ideal for identifying long-term trends but possibly ignoring short-term fluctuations. Decrease for more responsiveness to recent changes but risk of more false signals. \n\nMultiplier for ATR in SuperTrend calculation (factor): Increase for wider bands, capturing larger price movements but possibly missing subtle changes. Decrease for narrower bands, more sensitive to small shifts but risk of more noise.'
t4: str = 'Type of moving average for SuperTrend calculation (maSrc): Choose based on desired characteristics. SMA is simple and clear, EMA emphasizes recent prices, WMA gives more weight to recent data, RMA is less sensitive to recent changes, and VWMA considers volume.'
t5: str = 'Color for bullish trend (upCol): Select to visually identify upward trends. \n\nColor for bearish trend (dnCol): Select to visually identify downward trends.\n\nColor for neutral trend (neCol): Select to visually identify neutral trends.'


@script.strategy('Double AI Super Trend Trading - Strategy [PresentTrading]', overlay=True, precision=3, default_qty_type=strategy.percent_of_equity, commission_value=0.1, commission_type=strategy.commission.percent, slippage=1, currency=currency.USD, default_qty_value=10, initial_capital=10000, margin_long=0, margin_short=0, close_by_id=True)
def main(
    tradeDirection=input.string('Both', 'Select Trading Direction', options=('Long', 'Short', 'Both')),
    k=input.int(3, title='Neighbors', minval=1, maxval=100, inline='AI', group='AI Settings'),
    n_=input.int(12, title='Data', minval=1, maxval=100, inline='AI', group='AI Settings', tooltip=t1),
    k2=input.int(5, title='2nd Neighbors', minval=1, maxval=100, inline='AI2', group='AI2 Settings'),
    n2_=input.int(20, title='2nd Data', minval=1, maxval=100, inline='AI2', group='AI2 Settings'),
    KNN_PriceLen=input.int(20, title='Price Trend', minval=2, maxval=500, step=10, inline='AITrend', group='AI Trend'),
    KNN_STLen=input.int(80, title='Prediction Trend', minval=2, maxval=500, step=10, inline='AITrend', group='AI Trend', tooltip=t2),
    KNN_PriceLen2=input.int(40, title='2nd Price Trend', minval=2, maxval=500, step=10, inline='AI2Trend', group='AI Trend'),
    KNN_STLen2=input.int(80, title='2nd Prediction Trend', minval=2, maxval=500, step=10, inline='AI2Trend', group='AI Trend'),
    aisignals=input.bool(True, title='AI Trend Signals', inline='signal', group='AI Trend'),
    Bullish_col=input.color(color.lime, '', inline='signal', group='AI Trend'),
    Bearish_col=input.color(color.red, '', inline='signal', group='AI Trend'),
    maSrc=input.string('WMA', 'Moving Average Source', options=('SMA', 'EMA', 'WMA', 'RMA', 'VWMA'), inline='', group='Super Trend Settings', tooltip=t4),
    len=input.int(10, 'Length', minval=1, inline='SuperTrend', group='Super Trend Settings'),
    factor=input.float(4.0, step=0.1, inline='SuperTrend', group='Super Trend Settings', tooltip=t3),
    len2=input.int(5, '2nd Length', minval=1, inline='SuperTrend', group='Super Trend Settings'),
    factor2=input.float(3.0, step=0.1, inline='SuperTrend', group='Super Trend Settings'),
    upCol=input.color(color.lime, 'Bullish Color', inline='col', group='Super Trend Coloring'),
    dnCol=input.color(color.red, 'Bearish Color', inline='col', group='Super Trend Coloring'),
    neCol=input.color(color.blue, 'Neutral Color', inline='col', group='Super Trend Coloring', tooltip=t5)
):
    n = math.max(k, n_)
    n2 = math.max(k2, n2_)
    __block_result__ = na
    __switch__ = maSrc
    if __switch__ == 'SMA':
        __block_result__ = ta.sma(close * volume, len) / ta.sma(volume, len)
    elif __switch__ == 'EMA':
        __block_result__ = ta.ema(close * volume, len) / ta.ema(volume, len)
    elif __switch__ == 'WMA':
        __block_result__ = ta.wma(close * volume, len) / ta.wma(volume, len)
    elif __switch__ == 'RMA':
        __block_result__ = ta.rma(close * volume, len) / ta.rma(volume, len)
    elif __switch__ == 'VWMA':
        __block_result__ = ta.vwma(close * volume, len) / ta.vwma(volume, len)
    vwma = __block_result__
    atr: Series = ta.atr(len)
    upperBand: Series = vwma + factor * atr
    lowerBand: Series = vwma - factor * atr
    prevLowerBand = nz(lowerBand[1])
    prevUpperBand = nz(upperBand[1])
    atr2: Series = ta.atr(len2)
    upperBand2: Series = vwma + factor2 * atr2
    lowerBand2: Series = vwma - factor2 * atr2
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
    longCondition = direction == -1 and label_ == 1 and (direction2 == -1) and (label2_ == 1)
    shortCondition = direction == 1 and label_ == 0 and (direction2 == 1) and (label2_ == 0)
    longExitCondition1 = direction == -1 and label_ == 1
    longExitCondition2 = direction2 == -1 and label2_ == 1
    shortExitCondition1 = direction == 1 and label_ == 0
    shortExitCondition2 = direction2 == 1 and label2_ == 0
    longExitCondition = not (TrendUp or TrendUp2)
    shortExitCondition = not (TrendDn or TrendDn2)
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


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
