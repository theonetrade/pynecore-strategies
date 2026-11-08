"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    alertcondition, array, chart, close, color, display, fill, input,
    location, math, na, nz, open, plot, plotshape, script, shape, size, ta, volume
)
from pynecore.types import Series

t1: str = 'Number of nearest neighbors in KNN algorithm (k): Increase to consider more neighbors, providing a more balanced view but possibly smoothing out local patterns. Decrease for fewer neighbors to make the algorithm more responsive to recent changes. \n\nNumber of data points to consider (n): Increase for more historical data, providing a broader context but possibly diluting recent trends. Decrease for less historical data to focus more on recent behavior.'
t2: str = 'Length of weighted moving average for price (KNN_PriceLen): Higher values create a smoother price line, influencing the KNN algorithm to be more stable but less sensitive to short-term price movements. Lower values enhance responsiveness in KNN predictions to recent price changes but may lead to more noise. \n\nLength of weighted moving average for SuperTrend (KNN_STLen): Higher values lead to a smoother SuperTrend line, affecting the KNN algorithm to emphasize long-term trends. Lower values make KNN predictions more sensitive to recent SuperTrend changes but may result in more volatility.'
t3: str = 'Length of the SuperTrend (len): Increase for a smoother trend line, ideal for identifying long-term trends but possibly ignoring short-term fluctuations. Decrease for more responsiveness to recent changes but risk of more false signals. \n\nMultiplier for ATR in SuperTrend calculation (factor): Increase for wider bands, capturing larger price movements but possibly missing subtle changes. Decrease for narrower bands, more sensitive to small shifts but risk of more noise.'
t4: str = 'Type of moving average for SuperTrend calculation (maSrc): Choose based on desired characteristics. SMA is simple and clear, EMA emphasizes recent prices, WMA gives more weight to recent data, RMA is less sensitive to recent changes, and VWMA considers volume.'
t5: str = 'Color for bullish trend (upCol): Select to visually identify upward trends. \n\nColor for bearish trend (dnCol): Select to visually identify downward trends.\n\nColor for neutral trend (neCol): Select to visually identify neutral trends.'
t6: str = 'Shows or hides the enhanced cloud between the active Volume SuperTrend AI line and the cloud reference.'
t7: str = 'Bullish cloud color used when the AI trend is bullish.'
t8: str = 'Bearish cloud color used when the AI trend is bearish.'
t9: str = 'Base transparency of the cloud. Lower values make the cloud stronger and more visible.'
t10: str = 'Length of the smoothing used for the hidden cloud reference. Higher values create a softer and steadier cloud.'
t11: str = 'Extra smoothing applied to the active SuperTrend line before the cloud is built. Higher values create a cleaner cloud but add lag.'
t12: str = 'Controls how many layered fill bands are used to simulate a richer gradient-like cloud.'


@script.indicator('Volume SuperTrend AI (Zeiierman)', overlay=True)
def main(
    k=input.int(3, title='Neighbors', minval=1, maxval=100, inline='AI', group='AI Settings'),
    n_=input.int(10, title='Data', minval=1, maxval=100, inline='AI', group='AI Settings', tooltip=t1),
    KNN_PriceLen=input.int(20, title='Price Trend', minval=2, maxval=500, step=10, inline='AITrend', group='AI Trend'),
    KNN_STLen=input.int(100, title='Prediction Trend', minval=2, maxval=500, step=10, inline='AITrend', group='AI Trend', tooltip=t2),
    aisignals=input.bool(True, title='AI Trend Signals', inline='signal', group='AI Trend'),
    Bullish_col=input.color(color.lime, '', inline='signal', group='AI Trend'),
    Bearish_col=input.color(color.red, '', inline='signal', group='AI Trend'),
    len=input.int(10, 'Length', minval=1, inline='SuperTrend', group='Super Trend Settings'),
    factor=input.float(3.0, step=0.1, inline='SuperTrend', group='Super Trend Settings', tooltip=t3),
    maSrc=input.string('WMA', 'Moving Average Source', options=('SMA', 'EMA', 'WMA', 'RMA', 'VWMA'), inline='', group='Super Trend Settings', tooltip=t4),
    upCol=input.color(color.lime, 'Bullish Color', inline='col', group='Super Trend Coloring'),
    dnCol=input.color(color.red, 'Bearish Color', inline='col', group='Super Trend Coloring'),
    neCol=input.color(color.blue, 'Neutral Color', inline='col', group='Super Trend Coloring', tooltip=t5),
    showCloud=input.bool(True, 'Show Cloud Fill', group='Cloud Fill', tooltip=t6),
    cloudBull=input.color(color.lime, 'Bull Cloud', inline='cloudcol', group='Cloud Fill', tooltip=t7),
    cloudBear=input.color(color.red, 'Bear Cloud', inline='cloudcol', group='Cloud Fill', tooltip=t8),
    cloudTransp=input.int(78, 'Cloud Transparency', minval=0, maxval=95, group='Cloud Fill', tooltip=t9),
    cloudRefLen=input.int(10, 'Cloud Reference Length', minval=1, group='Cloud Fill', tooltip=t10),
    cloudLineSmooth=input.int(2, 'Cloud Line Smoothing', minval=1, group='Cloud Fill', tooltip=t11),
    cloudLayers=input.int(3, 'Cloud Richness', minval=1, maxval=3, group='Cloud Fill', tooltip=t12)
):
    n = math.max(k, n_)

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

    lowerBand = lowerBand if lowerBand > prevLowerBand or close[1] < prevLowerBand else prevLowerBand
    upperBand = upperBand if upperBand < prevUpperBand or close[1] > prevUpperBand else prevUpperBand

    direction: Series[int] = na(int)
    superTrend: Series[float] = na(float)
    prevSuperTrend = superTrend[1]

    if na(atr[1]):
        direction = 1
    elif prevSuperTrend == prevUpperBand:
        direction = -1 if close > upperBand else 1
    else:
        direction = 1 if close < lowerBand else -1

    superTrend = lowerBand if direction == -1 else upperBand

    price: Series = ta.wma(close, KNN_PriceLen)
    sT: Series = ta.wma(superTrend, KNN_STLen)

    data: list[float] = array.new_float(n)
    labels: list[int] = array.new_int(n)

    for i in pine_range(0, n - 1, 1):
        array.set(data, i, superTrend[i])
        label_i = 1 if price[i] > sT[i] else 0
        array.set(labels, i, label_i)

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

    col: Series = upCol if label_ == 1 else dnCol if label_ == 0 else neCol
    plot(current_superTrend, color=col, title='Volume Super Trend AI')

    upTrend = plot(current_superTrend if superTrend == lowerBand else na, title='Up Volume Super Trend AI', color=col, style=plot.style_linebr)
    downTrend = plot(current_superTrend if superTrend == upperBand else na, title='Down Volume Super Trend AI', color=col, style=plot.style_linebr)

    cloudLine = ta.sma(current_superTrend, cloudLineSmooth)
    cloudRef = ta.ema((open + close) / 2, cloudRefLen)

    cloudA = cloudLine + (cloudRef - cloudLine) * 0.25 if not na(cloudLine) and (not na(cloudRef)) else na
    cloudB = cloudLine + (cloudRef - cloudLine) * 0.5 if not na(cloudLine) and (not na(cloudRef)) else na
    cloudC = cloudLine + (cloudRef - cloudLine) * 0.75 if not na(cloudLine) and (not na(cloudRef)) else na

    cloudBaseColor = cloudBull if label_ == 1 else cloudBear if label_ == 0 else neCol

    pCloudLine = plot(cloudLine if showCloud else na, title='Cloud Active Line', color=color.new(chart.fg_color, 100), display=display.none)
    pCloudA = plot(cloudA if showCloud and cloudLayers >= 1 else na, title='Cloud Layer A', color=color.new(chart.fg_color, 100), display=display.none)
    pCloudB = plot(cloudB if showCloud and cloudLayers >= 2 else na, title='Cloud Layer B', color=color.new(chart.fg_color, 100), display=display.none)
    pCloudC = plot(cloudC if showCloud and cloudLayers >= 3 else na, title='Cloud Layer C', color=color.new(chart.fg_color, 100), display=display.none)
    pCloudRef = plot(cloudRef if showCloud else na, title='Cloud Reference', color=color.new(chart.fg_color, 100), display=display.none)

    fill(pCloudLine, pCloudA, color=color.new(cloudBaseColor, math.max(0, cloudTransp - 18)) if showCloud and cloudLayers >= 1 else na, title='Cloud Fill 1')
    fill(pCloudA, pCloudB, color=color.new(cloudBaseColor, math.max(0, cloudTransp - 6)) if showCloud and cloudLayers >= 2 else na, title='Cloud Fill 2')
    fill(pCloudB, pCloudC, color=color.new(cloudBaseColor, math.min(95, cloudTransp + 6)) if showCloud and cloudLayers >= 3 else na, title='Cloud Fill 3')
    fill(pCloudC, pCloudRef, color=color.new(cloudBaseColor, math.min(95, cloudTransp + 18)) if showCloud and cloudLayers >= 3 else na, title='Cloud Fill 4')
    fill(pCloudB, pCloudRef, color=color.new(cloudBaseColor, math.min(95, cloudTransp + 10)) if showCloud and cloudLayers == 2 else na, title='Cloud Fill 2-Layer')
    fill(pCloudA, pCloudRef, color=color.new(cloudBaseColor, math.min(95, cloudTransp + 14)) if showCloud and cloudLayers == 1 else na, title='Cloud Fill 1-Layer')

    Start_TrendUp = col == upCol and (col[1] != upCol or col[1] == neCol) and aisignals
    Start_TrendDn = col == dnCol and (col[1] != dnCol or col[1] == neCol) and aisignals
    TrendUp = direction == -1 and direction[1] == 1 and (label_ == 1) and aisignals
    TrendDn = direction == 1 and direction[1] == -1 and (label_ == 0) and aisignals

    plotshape(superTrend if Start_TrendUp else na, location=location.absolute, style=shape.circle, size=size.tiny, color=Bullish_col, title='AI Bullish Trend Start')
    plotshape(superTrend if Start_TrendDn else na, location=location.absolute, style=shape.circle, size=size.tiny, color=Bearish_col, title='AI Bearish Trend Start')
    plotshape(superTrend if TrendUp else na, location=location.absolute, style=shape.triangleup, size=size.small, color=Bullish_col, title='AI Bullish Trend Signal')
    plotshape(superTrend if TrendDn else na, location=location.absolute, style=shape.triangledown, size=size.small, color=Bearish_col, title='AI Bearish Trend Signal')

    alertcondition(Start_TrendUp, title='1 Bullish Trend Start', message='AI Bullish Trend Start')
    alertcondition(Start_TrendDn, title='2 Bearish Trend Start', message='AI Bearish Trend Start')
    alertcondition(Start_TrendUp or Start_TrendDn, title='3 Any Trend Start', message='Any AI Trend Start')
    alertcondition(TrendUp, title='4 Bullish Trend Signal', message='AI Bullish Trend Signal')
    alertcondition(TrendDn, title='5 Bearish Trend Signal', message='AI Bearish Trend Signal')
    alertcondition(TrendUp or TrendDn, title='6 Any Trend Signal', message='Any AI Trend Signal')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
