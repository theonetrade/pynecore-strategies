"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, array, barstate, bgcolor, close, color, fill, format,
    high, input, location, low, math, na, nz, open, plot, plotcandle, plotshape, script, shape,
    size, ta
)
from pynecore.types import Color, NA, Persistent, Series

group1: str = "Use the Ultimate RSI indicator to visualize RSI settings"
group2: str = "Show/Hide ALL-----------------------------------------------------------------------------------"
group3: str = "Watch Signals------------------------------------------------------------------------------------"
group4: str = "RSI Settings------------------------------------------------------------------------------------"
group5: str = "Price Bollinger Bands Settings-----------------------------------------------------------------------------------"
group6: str = "Upper Bollinger Band Coloring (Uses Moving Average)------------------------------------------------------------------------------------"
group7: str = "Lower Bollinger Band Coloring (Uses Rate of Change)------------------------------------------------------------------------------------"
group8: str = "Moving Average Settings-----------------------------------------------------------------------------------"
group9: str = "Buy/Sell Signal Event Options------------------------------------------------------------------------------------"
group10: str = "Color candles in stages using these moving averages------------------------------------------------------------------------------------"
group11: str = "ATR Adjusted Bands-----------------------------------------------------------------------------------"
group12: str = "Alerts------------------------------------------------------------------------------------"
MACD_FAST_LENGTH: int = 12
MACD_SLOW_LENGTH: int = 26
MACD_SIGNAL_LENGTH: int = 9


@script.indicator(shorttitle="Ultimate", title="Ultimate Buy and Sell Indicator", format=format.inherit, overlay=True, timeframe="", timeframe_gaps=True)
def main(
    src: Series[float] = input(close, title="Data Source for Price", group=group1),
    showAllMA=input(False, title="Moving Averages", group=group2, tooltip="Moving average options are below"),
    showBollingerBands=input(True, title="Bollinger Bands", inline="bands", group=group2, tooltip="Bollinger bands are set to have two layers with different standard deviations to create a thicker band."),
    showBasisPlot=input(True, title="Bollinger Band Basis", inline="bands", group=group2, tooltip="Dedicated Bollinger Band basis line. Settings are in the Price Bollinger Band settings section below."),
    bandTransparency=input.int(70, step=10, minval=10, maxval=90, title="Band Transparency", inline="bands", group=group2, tooltip="Adjust this to scale how transparent the bands will be. 10 - 90%. Higher number fades the bands away."),
    showWatchSignals=input(True, title="Watch Signals", group=group2, tooltip="Watch signals are prerequisite Bollinger band events used for generating buy/sell signals. Beware of watch signals when Bollinger Bands are tighter than usual, periods of low volatility can quickly swing in the opposite direction triggering a false signal, so be cautious."),
    showSignals=input(True, title="Buy/Sell Signals", inline="Signals", group=group2, tooltip="While I am working to make them better, they are not always right or perfect, but they help give an indication of inflection points."),
    showCircles=input(True, title="Add Circles", inline="Signals", group=group2, tooltip="Draws circles around the buy and sell signals for easier identification."),
    showSignalBackground=input(True, title="Buy/Sell Signal Vertical Lines", group=group2, tooltip="Colors the background behind the bar before a buy/sell signal is officially set to act as a warning of a potential trade. This is allowed to 'repaint'."),
    showBSBackground=input(False, title="Bought/Sold Colored Background", group=group2, tooltip="Colors the background to represent a previous bought or sold state (always the first in the series). The state stays in effect until the next opposite signal. This can help keep you in a trade or inform you of the direction of the trade if you come in late."),
    showAtrFill=input(False, title="ATR-adjusted fill color zone", group=group2),
    showAtrLines=input(False, title="ATR-adjusted Moving Average and band lines", group=group2),
    showRSICandleColors=input(False, title="RSI Colored Candles", group=group2, tooltip="Be sure to turn off candle colors in main settings for this to work. This creates candles with colors based on zones of RSI values with red being downward momentum and green being upward momentum. Candles are also colored Orange for BUY and Fuschia for SELL. They follow incremental zones of RSI levels which you can view using my Ultimate RSI indicator. Yellow candles are between 45 and 55 RSI (market is choosing a direction if it hangs in this zone, check if higher timeframes are in this area as price tends to make big moves crossing the 50 RSI level. Red candles are below 45 and start darker and get brighter as RSI drops (acceleration downward). They start a darker green over 55 and turn brighter as RSI increases (acceleration upwards). In the extreme cases that RSI is over 80 or under 20 the candles turn white."),
    showMaCandleColors=input(True, title="MA Colored Candles", group=group2, tooltip="Be sure to turn off candle colors in main settings for this to work. This will color the candles based on the price being over, between, or under two selected moving averages. This helps you track price vs moving average crosses. For instance, if price is under both the 10 and 20, it will be red, once it crosses the 10, it would turn yellow, once it also crosses the 10, it would turn the candles green. (3 stages: Below both, between both, over both)"),
    watchSignalLookback=input.int(35, title="# of bars back to use Watch Signals", group=group3, step=5, tooltip="How many bars back to consider a Watch signal valid. Longer values tend to create more inaccurate B/S signals. The reasoning is that as volatility (range of price fluctuations) stabilizes, the bollinger bands tighten, and when price makes a sudden move, it generates a watch signal and then buy or sell signal, fails and then reverses suddenly. We don't want to count these down the road."),
    useRsiWatchSignals=input(True, title="Use RSI Watch Signals", inline="RSI Watch", group=group3, tooltip="If the RSI Crosses over the lower Bollinger Band it creates a buy watch signal. If it crosses under the upper band it creates a sell watch signal."),
    usePriceBandWatchSignals=input(False, title="Use Price Watch Signals", inline="Price Watch", group=group3, tooltip="If price crosses the Bollinger Bands this creates a watch signal"),
    useAtrWatchSignals=input(False, title="Use ATR Watch Signals", inline="ATR Watch", group=group3),
    showRsiWatchPlot=input(True, title="Show?", inline="RSI Watch", group=group3),
    showPriceWatchPlot=input(False, title="Show?", inline="Price Watch", group=group3),
    showAtrWatchPlot=input(False, title="Show?", inline="ATR Watch", group=group3),
    rsiLength=input.int(32, title="RSI Length", inline="RSI", minval=1, group=group4, tooltip="RSI is not visible, but is used for trade signals. RSI crossing various lines generates signals."),
    rsiMaCalcType=input.string("RMA", title="Calculate RSI with this moving average", options=("SMA", "EMA", "WMA", "RMA"), group=group4, tooltip="The moving average used to calculate the RSI. Will affect signals."),
    rsiMaType=input.string("SMA", title="RSI Bollinger Band Moving Average", inline="RSI MA", options=("SMA", "EMA", "WMA", "RMA"), group=group4, tooltip="The moving average used to calculate the RSI Bollinger Bands and basis lines. Will affect signals."),
    rsiMaLength=input.int(32, title="", inline="RSI MA", minval=1, group=group4),
    rsiMultiplier=input.float(2, minval=1, maxval=3, step=0.1, title="RSI Bollinger Bands Standard Deviation", group=group4, tooltip="This is the standard deviation, and affects Watch signals, which affect Buy and Sell signals."),
    useRsiSmoothing=input(False, title="RSI Smoothing", inline="smoothType", group=group4, tooltip="Uses the selected moving average type to smooth the RSI"),
    useHaSmoothing=input(False, title='Heiken Ashi Smoothing', inline='smoothType', group=group4),
    smoothingMaType=input.string("RMA", title="", inline="smooth", options=("SMA", "EMA", "WMA", "RMA"), group=group4),
    smoothingLength=input.int(3, title="", inline="smooth", minval=1, group=group4),
    priceBasisLength=input.int(20, title="Price BBand Basis Length", group=group5, tooltip="Sets the length to calculate the Price Bollinger Bands and corresponding basis line."),
    priceMaType=input.string("SMA", title="Moving Average Type", options=("SMA", "EMA", "WMA", "RMA"), group=group5, tooltip="The moving average used to calculate the Price BBands. Changes the shape and affects creation of watch signals (and therefore also B/S signals)"),
    priceInnerMultiplier=input.float(2.1, minval=1, maxval=4, step=0.1, title="Price Inner BB Multiplier", group=group5, tooltip="Standard deviation for the inner Price Bollinger Band which does NOT affect signals."),
    priceOuterMultiplier=input.float(2.4, minval=2, maxval=6, step=0.1, title="Price Outer BB Multiplier", group=group5, tooltip="Standard deviation for the outer Price Bollinger Band which DOES affect watch signals, which in turn allow Buy and Sell signals."),
    basisColor=input.color(color.orange, title="Bollinger Band Basis Color", group=group5),
    bullBearMaType=input.string("SMA", title="Upper Band MA Type", options=("SMA", "EMA", "WMA", "RMA"), group=group6, inline="Band Colors", tooltip="If price is over this moving average the upper Bollinger band will be colored the up color, if under, the down color."),
    bullBearMaLength=input.int(50, step=5, title="", group=group6, inline="Band Colors"),
    upperBbColorUp=input.color(color.green, title="Bull", group=group6, inline="Upper Band Colors"),
    upperBbColorDown=input.color(color.red, title="Bear", group=group6, inline="Upper Band Colors"),
    rocLength=input.int(10, title="ROC Length", group=group7),
    useRocFilter=input(False, title="Use ROC as a Filter", group=group7),
    lowerBbColorUp=input.color(color.green, title="Bull", group=group7, inline="Lower Band Colors"),
    lowerBbColorDown=input.color(color.red, title="Bear", group=group7, inline="Lower Band Colors"),
    showMA1=input(True, inline="ma1", title="MA1", group=group8),
    showMA2=input(True, inline="ma2", title="MA2", group=group8),
    showMA3=input(True, inline="ma3", title="MA3", group=group8),
    showMA4=input(True, inline="ma4", title="MA4", group=group8),
    showMA5=input(True, inline="ma5", title="MA5", group=group8),
    showMA6=input(True, inline="ma6", title="MA6", group=group8),
    showMA7=input(True, inline="ma7", title="MA7", group=group8),
    showMA8=input(True, inline="ma8", title="MA8", group=group8),
    maType1=input.string("WMA", inline="ma1", title="", options=("SMA", "EMA", "WMA", "RMA"), group=group8),
    maType2=input.string("WMA", inline="ma2", title="", options=("SMA", "EMA", "WMA", "RMA"), group=group8),
    maType3=input.string("WMA", inline="ma3", title="", options=("SMA", "EMA", "WMA", "RMA"), group=group8),
    maType4=input.string("WMA", inline="ma4", title="", options=("SMA", "EMA", "WMA", "RMA"), group=group8),
    maType5=input.string("WMA", inline="ma5", title="", options=("SMA", "EMA", "WMA", "RMA"), group=group8),
    maType6=input.string("WMA", inline="ma6", title="", options=("SMA", "EMA", "WMA", "RMA"), group=group8),
    maType7=input.string("WMA", inline="ma7", title="", options=("SMA", "EMA", "WMA", "RMA"), group=group8),
    maType8=input.string("WMA", inline="ma8", title="", options=("SMA", "EMA", "WMA", "RMA"), group=group8),
    ma1Length=input.int(10, inline="ma1", title="", group=group8),
    ma2Length=input.int(20, inline="ma2", title="", group=group8),
    ma3Length=input.int(50, inline="ma3", title="", group=group8),
    ma4Length=input.int(100, inline="ma4", title="", group=group8),
    ma5Length=input.int(200, inline="ma5", title="", group=group8),
    ma6Length=input.int(300, inline="ma6", title="", group=group8),
    ma7Length=input.int(400, inline="ma7", title="", group=group8),
    ma8Length=input.int(500, inline="ma8", title="", group=group8),
    ma1Color=input.color(color.yellow, inline="ma1", title="", group=group8),
    ma2Color=input.color(color.green, inline="ma2", title="", group=group8),
    ma3Color=input.color(color.red, inline="ma3", title="", group=group8),
    ma4Color=input.color(color.purple, inline="ma4", title="", group=group8),
    ma5Color=input.color(color.blue, inline="ma5", title="", group=group8),
    ma6Color=input.color(color.gray, inline="ma6", title="", group=group8),
    ma7Color=input.color(color.orange, inline="ma7", title="", group=group8),
    ma8Color=input.color(color.white, inline="ma8", title="", group=group8),
    useRsiSignals=input(True, title="RSI crossing Moving Average", group=group9, tooltip="Uses RSI crossing RSI basis."),
    usePriceSignals=input(False, title="Price crossing BBand basis", group=group9, tooltip="Signals from price crossing Price Bollinger Band Basis"),
    useMacdSignals=input(False, title="MACD Signals", group=group9, tooltip="Signals from MACD crossovers."),
    use75Signals=input(True, title="RSI crossing under 75", group=group9, tooltip="Sell signals from crossing under RSI 75"),
    use50Signals=input(False, title="RSI crossing over/under 50", group=group9, tooltip="Buy and sell signals from crossing over and under RSI 50"),
    use25Signals=input(True, title="RSI crossing over 25", group=group9, tooltip="Buy signals from crossing over RSI 25"),
    useRsiMa=input(False, title="Rsi Crossing a Moving Average", group=group9, tooltip="Signals based on RSI crossing a custom length moving average rather than the Basis of the Bollinger Bands. This allows you to change the Bollinger Band moving average type used in the calculation (which will change the shape of the bands) and cross a different moving average without changing watch signal generation. To see these effects, use the Ultimate RSI indicator."),
    rsiMaType2=input.string("WMA", title="MA Type", inline="rsiMa", options=("SMA", "EMA", "WMA", "RMA"), group=group9),
    rsiMaLength2=input.int(16, title="Length", inline="rsiMa", minval=1, group=group9, tooltip="Adds another moving average to the RSI that will not affect the Bollinger Bands. This can be used for signals without compromising the watch signals if using a WMA or other moving averages types for the Bands."),
    fastMaType=input.string("WMA", "Fast MA Type", inline="fastMA", options=("SMA", "EMA", "WMA", "RMA"), group=group10),
    fastMaLength=input.int(10, "Length", inline="fastMA", group=group10, tooltip="First level MA - price crossing above turns candles yellow"),
    slowMaType=input.string("WMA", "Slow MA Type", inline="slowMA", options=("SMA", "EMA", "WMA", "RMA"), group=group10),
    slowMaLength=input.int(20, "Length", inline="slowMA", group=group10, tooltip="Second level MA - price crossing above turns candles green"),
    overMaColor=input.color(color.green, title="Above Both MAs", group=group10, inline="colors"),
    midMaColor=input.color(color.yellow, title="Between MAs", group=group10, inline="colors"),
    underMaColor=input.color(color.red, title="Below Both MAs", group=group10, inline="colors"),
    atrPeriod=input.int(20, title="ATR Period", group=group11),
    maPeriod=input.int(20, title="ATR MA Period", group=group11),
    atrMult=input.float(1.5, minval=1, step=0.1, title="ATR Band multiplier", group=group11, tooltip="Can make the ATR bands wider."),
    atrMaType=input.string("WMA", title="ATR Moving Average Type", options=("SMA", "EMA", "WMA", "RMA"), group=group11, tooltip="The moving average used to calculate the ATR moving average."),
    atrFillColor=input.color(color.rgb(255, 59, 173), title="ATR-adjusted band fill color", group=group11),
    atrLineColor=input.color(color.rgb(255, 59, 173), title="ATR-adjusted band line color", group=group11),
    fillTransp=input.int(80, title="Fill transparency", group=group11),
    atrBollingerBands=input(True, title="ATR Bollinger Bands", group=group11, tooltip="Switches from ATR bands to ATR with Bollinger Bands for a different way to use the ATR."),
    enableAdvancedAlerts=input(True, title="Advance alerts one candle", group=group12, tooltip="This will use the warning background as the signal for buy/sell alerts.      On higher timeframes, this could lead to alerts for signals that end up failing      and price could reverse. On sub-1minute timeframes this should be more reliable.")
):
    ha_close: Series = (open + high + low + close) / 4
    ha_open: Series = NA(float)
    ha_open = (open + close) / 2 if na(ha_open[1]) else (nz(ha_open[1]) + nz(ha_close[1])) / 2
    ha_high = math.max(high, math.max(ha_open, ha_close))
    ha_low = math.min(low, math.min(ha_open, ha_close))
    initialSrc = ha_close if useHaSmoothing else src

    def MA(src, Length, type):
        __block_result__ = na
        __switch__ = type
        if __switch__ == "SMA":
            __block_result__ = ta.sma(src, Length)
        elif __switch__ == "EMA":
            __block_result__ = ta.ema(src, Length)
        elif __switch__ == "WMA":
            __block_result__ = ta.wma(src, Length)
        elif __switch__ == "RMA":
            __block_result__ = ta.rma(src, Length)
        return __block_result__

    atrValue = ta.atr(atrPeriod)
    atrMaValue = MA(src, maPeriod, atrMaType)
    upperAtrBand = atrMaValue + atrValue * atrMult
    middleAtrBand = atrMaValue
    lowerAtrBand = atrMaValue - atrValue * atrMult
    upperAtrBb = atrMaValue + atrValue + atrMult * ta.stdev(src, maPeriod)
    lowerAtrBb = atrMaValue - atrValue - atrMult * ta.stdev(src, maPeriod)
    lineTransparency = 0 if showAtrLines else 100

    adjustedLineColor = color.new(atrLineColor, lineTransparency)

    upperAtrPlot = plot(upperAtrBb if atrBollingerBands else upperAtrBand, color=adjustedLineColor)
    middleAtrPlot = plot(middleAtrBand, color=adjustedLineColor)
    lowerAtrPlot = plot(lowerAtrBb if atrBollingerBands else lowerAtrBand, color=adjustedLineColor)
    fillColor = color.new(atrFillColor, fillTransp) if showAtrFill else na
    fill(upperAtrPlot, lowerAtrPlot, color=fillColor, title='ATR-Adjusted Band Fill')

    previous = ta.valuewhen(True, src, rocLength)
    roc = (src - previous) / previous * 100
    rocBullish = roc > 0
    rocBearish = roc < 0
    rocColor = lowerBbColorUp if rocBullish else lowerBbColorDown

    macd = ta.ema(src, 12) - ta.ema(src, 26)
    signal = ta.ema(macd, 9)

    __block_result_1__ = na
    __switch__ = rsiMaCalcType
    if __switch__ == 'SMA':
        __block_result_1__ = ta.sma(math.max(ta.change(initialSrc), 0), rsiLength)
    elif __switch__ == 'EMA':
        __block_result_1__ = ta.ema(math.max(ta.change(initialSrc), 0), rsiLength)
    elif __switch__ == 'WMA':
        __block_result_1__ = ta.wma(math.max(ta.change(initialSrc), 0), rsiLength)
    elif __switch__ == 'RMA':
        __block_result_1__ = ta.rma(math.max(ta.change(initialSrc), 0), rsiLength)
    up = __block_result_1__
    __block_result_2__ = na
    __switch__ = rsiMaCalcType
    if __switch__ == 'SMA':
        __block_result_2__ = ta.sma(-math.min(ta.change(initialSrc), 0), rsiLength)
    elif __switch__ == 'EMA':
        __block_result_2__ = ta.ema(-math.min(ta.change(initialSrc), 0), rsiLength)
    elif __switch__ == 'WMA':
        __block_result_2__ = ta.wma(-math.min(ta.change(initialSrc), 0), rsiLength)
    elif __switch__ == 'RMA':
        __block_result_2__ = ta.rma(-math.min(ta.change(initialSrc), 0), rsiLength)
    down = __block_result_2__
    rsi = 100 if down == 0 else 0 if up == 0 else 100 - 100 / (1 + up / down)

    smoothedRsi = MA(rsi, smoothingLength, smoothingMaType) if useRsiSmoothing else rsi

    rsiMA1 = MA(smoothedRsi, rsiMaLength, rsiMaType)

    rsiMA2 = MA(smoothedRsi, rsiMaLength2, rsiMaType2)

    rsiDeviation = ta.stdev(smoothedRsi, rsiMaLength)

    upperRsi = rsiMA1 + rsiMultiplier * rsiDeviation
    lowerRsi = rsiMA1 - rsiMultiplier * rsiDeviation

    def calculateBollingerBands(src, priceBasisLength, priceInnerMultiplier, priceOuterMultiplier, priceMaType):
        priceBasis = MA(src, priceBasisLength, priceMaType)
        priceInnerDeviation = priceInnerMultiplier * ta.stdev(src, priceBasisLength)
        priceOuterDeviation = priceOuterMultiplier * ta.stdev(src, priceBasisLength)
        return (priceBasis, priceBasis + priceInnerDeviation, priceBasis - priceInnerDeviation, priceBasis + priceOuterDeviation, priceBasis - priceOuterDeviation)

    upperPriceOuter: Series
    lowerPriceOuter: Series
    priceBasis, upperPriceInner, lowerPriceInner, upperPriceOuter, lowerPriceOuter = calculateBollingerBands(src, priceBasisLength, priceInnerMultiplier, priceOuterMultiplier, priceMaType)

    bullOrBear = MA(src, bullBearMaLength, bullBearMaType)

    maBullish = src >= bullOrBear
    maBearish = src < bullOrBear
    transparency = bandTransparency
    upperBandColor: Persistent[Color] = na(Color)
    upperBandColor = (color.new(upperBbColorUp, transparency) if maBullish else color.new(upperBbColorDown, transparency)) if showBollingerBands else na
    lowerBandColor: Persistent[Color] = na(Color)
    lowerBandColor = (color.new(lowerBbColorUp, transparency) if rocBullish else color.new(lowerBbColorDown, transparency)) if showBollingerBands else na
    U1 = plot(upperPriceInner, color=na)
    L1 = plot(lowerPriceInner, color=na)
    U2 = plot(upperPriceOuter, color=na)
    L2 = plot(lowerPriceOuter, color=na)
    fill(U1, U2, title='Upper Bollinger Bands MA Based Fill', color=upperBandColor)
    fill(L1, L2, title='Lower Bollinger Bands ROC Based Fill', color=lowerBandColor)
    plot(priceBasis if showBasisPlot else na, title='Price Basis', color=basisColor)

    ma1 = MA(src, ma1Length, maType1)
    ma2 = MA(src, ma2Length, maType2)
    ma3 = MA(src, ma3Length, maType3)
    ma4 = MA(src, ma4Length, maType4)
    ma5 = MA(src, ma5Length, maType5)
    ma6 = MA(src, ma6Length, maType6)
    ma7 = MA(src, ma7Length, maType7)
    ma8 = MA(src, ma8Length, maType8)
    plot(ma1 if showAllMA and showMA1 else na, 'MA1', color=ma1Color)
    plot(ma2 if showAllMA and showMA2 else na, 'MA2', color=ma2Color)
    plot(ma3 if showAllMA and showMA3 else na, 'MA3', color=ma3Color)
    plot(ma4 if showAllMA and showMA4 else na, 'MA4', color=ma4Color)
    plot(ma5 if showAllMA and showMA5 else na, 'MA5', color=ma5Color)
    plot(ma6 if showAllMA and showMA6 else na, 'MA6', color=ma6Color)
    plot(ma7 if showAllMA and showMA7 else na, 'MA7', color=ma7Color)
    plot(ma8 if showAllMA and showMA8 else na, 'MA8', color=ma8Color)

    priceOverUpperOuter = high > upperPriceOuter[1]
    priceUnderLowerOuter = low < lowerPriceOuter[1]
    priceCrossOverBasis = ta.crossover(src, priceBasis)
    priceCrossUnderBasis = ta.crossunder(src, priceBasis)
    rsiCrossOverLower = ta.crossover(smoothedRsi, lowerRsi)
    rsiCrossUnderUpper = ta.crossunder(smoothedRsi, upperRsi)
    rsiCrossOverBasis = ta.crossover(smoothedRsi, rsiMA1)
    rsiCrossUnderBasis = ta.crossunder(smoothedRsi, rsiMA1)
    rsiCrossOverMa = ta.crossover(smoothedRsi, rsiMA2)
    rsiCrossUnderMa = ta.crossunder(smoothedRsi, rsiMA2)
    rsiCrossUnder75 = ta.crossunder(smoothedRsi, 75)
    rsiCrossOver70 = ta.crossover(smoothedRsi, 70)
    rsiCrossUnder50 = ta.crossunder(smoothedRsi, 49)
    rsiCrossOver50 = ta.crossover(smoothedRsi, 51)
    rsiCrossUnder30 = ta.crossunder(smoothedRsi, 30)
    rsiCrossOver25 = ta.crossover(smoothedRsi, 25)
    macdBuy = ta.crossover(macd, signal)
    macdSell = ta.crossunder(macd, signal)
    overAtrUpper = ta.crossover(src, upperAtrBb) if atrBollingerBands else ta.crossunder(src, upperAtrBand)
    underAtrLower = ta.crossunder(src, lowerAtrBb) if atrBollingerBands else ta.crossunder(src, lowerAtrBand)

    fastMa = MA(src, fastMaLength, fastMaType)
    slowMa = MA(src, slowMaLength, slowMaType)
    aboveFastMa = src >= fastMa
    aboveSlowMa = src >= slowMa
    belowFastMa = src < fastMa
    belowSlowMa = src < slowMa

    belowBoth: bool = src < fastMa and src < slowMa

    betweenBoth: bool = src >= fastMa and src < slowMa or (src < fastMa and src >= slowMa)

    aboveBoth: bool = src >= fastMa and src >= slowMa

    rocAllowBuy = rocBullish if useRocFilter else True
    rocAllowSell = rocBearish if useRocFilter else True

    bought: Persistent[bool] = False
    sold: Persistent[bool] = False
    buyWatchArray: Persistent[list[int]] = array.new_int(na)
    sellWatchArray: Persistent[list[int]] = array.new_int(na)
    plotBuy: bool = False
    plotSell: bool = False
    plotBuyBG: bool = False
    plotSellBG: bool = False

    buyWatch1 = usePriceBandWatchSignals and priceUnderLowerOuter and barstate.isconfirmed
    buyWatch2 = useRsiWatchSignals and rsiCrossOverLower and barstate.isconfirmed
    buyWatch3 = useRsiWatchSignals and rsiCrossUnder30 and barstate.isconfirmed
    buyWatch4 = useAtrWatchSignals and underAtrLower and barstate.isconfirmed
    sellWatch1 = usePriceBandWatchSignals and priceOverUpperOuter and barstate.isconfirmed
    sellWatch2 = useRsiWatchSignals and rsiCrossUnderUpper and barstate.isconfirmed
    sellWatch3 = useRsiWatchSignals and rsiCrossOver70 and barstate.isconfirmed
    sellWatch4 = useAtrWatchSignals and overAtrUpper and barstate.isconfirmed
    buyWatched: bool = buyWatch1 or buyWatch2 or buyWatch3 or buyWatch4
    sellWatched: bool = sellWatch1 or sellWatch2 or sellWatch3 or sellWatch4
    buySignal1 = useRsiSignals and rsiCrossOverBasis
    buySignal2 = usePriceSignals and priceCrossOverBasis
    buySignal3 = use50Signals and rsiCrossOver50
    buySignal4 = use25Signals and rsiCrossOver25
    buySignal5 = useMacdSignals and macdBuy
    buySignal6 = useRsiMa and rsiCrossOverMa
    sellSignal1 = useRsiSignals and rsiCrossUnderBasis
    sellSignal2 = use50Signals and rsiCrossUnder50
    sellSignal3 = usePriceSignals and priceCrossUnderBasis
    sellSignal4 = use75Signals and rsiCrossUnder75
    sellSignal5 = useMacdSignals and macdSell
    sellSignal6 = useRsiMa and rsiCrossUnderMa

    array.push(buyWatchArray, 1 if buyWatched else na)
    array.push(sellWatchArray, 1 if sellWatched else na)
    while array.size(buyWatchArray) > watchSignalLookback:
        array.shift(buyWatchArray)
    while array.size(sellWatchArray) > watchSignalLookback:
        array.shift(sellWatchArray)
    buyWatchSumMet = array.sum(buyWatchArray) >= 1
    sellWatchSumMet = array.sum(sellWatchArray) >= 1
    buyWatchMet = buyWatchSumMet
    sellWatchMet = sellWatchSumMet
    combinedBuySignals = buySignal1 or buySignal2 or buySignal3 or buySignal4 or buySignal5 or buySignal6
    combinedSellSignals = sellSignal1 or sellSignal2 or sellSignal3 or sellSignal4 or sellSignal5 or sellSignal6

    if combinedBuySignals and buyWatchMet and rocAllowBuy:
        plotBuyBG = True
    elif combinedSellSignals and sellWatchMet and rocAllowSell:
        plotSellBG = True
    else:
        plotBuyBG = False
        plotSellBG = False

    if combinedBuySignals and buyWatchMet and barstate.isconfirmed and rocAllowBuy:
        bought = True
        sold = False
        plotBuy = True
        array.clear(buyWatchArray)
        array.clear(sellWatchArray)
    elif combinedSellSignals and sellWatchMet and barstate.isconfirmed and rocAllowSell:
        sold = True
        bought = False
        plotSell = True
        array.clear(sellWatchArray)
        array.clear(buyWatchArray)
    else:
        plotBuy = False
        plotSell = False

    alertcondition(plotBuyBG if enableAdvancedAlerts else plotBuy, title='Buy signal', message='Buy signal detected')
    alertcondition(plotSellBG if enableAdvancedAlerts else plotSell, title='Sell signal', message='Sell signal detected')
    plotshape(True if showSignals and plotBuy else False, title='BUY/LONG', location=location.belowbar, color=color.new(color.orange, 0), style=shape.triangleup, size=size.tiny)
    plotshape(True if showSignals and plotSell else False, title='SELL/SHORT', location=location.abovebar, color=color.new(color.fuchsia, 0), style=shape.triangledown, size=size.tiny)
    bgcolor(color.new(color.orange, 80) if showSignalBackground and plotBuyBG else na)
    bgcolor(color.new(color.fuchsia, 80) if showSignalBackground and plotSellBG else na)
    B1 = color.new(color.orange, 50)
    B2 = color.new(color.orange, 65)
    B3 = color.new(color.orange, 85)
    S1 = color.new(color.fuchsia, 50)
    S2 = color.new(color.fuchsia, 65)
    S3 = color.new(color.fuchsia, 85)

    plotshape(low if showSignals and showCircles and plotBuy else na, color=B1, location=location.absolute, style=shape.circle, size=size.tiny)
    plotshape(low if showSignals and showCircles and plotBuy else na, color=B2, location=location.absolute, style=shape.circle, size=size.small)
    plotshape(low if showSignals and showCircles and plotBuy else na, color=B3, location=location.absolute, style=shape.circle, size=size.normal)
    plotshape(high if showSignals and showCircles and plotSell else na, color=S1, location=location.absolute, style=shape.circle, size=size.tiny)
    plotshape(high if showSignals and showCircles and plotSell else na, color=S2, location=location.absolute, style=shape.circle, size=size.small)
    plotshape(high if showSignals and showCircles and plotSell else na, color=S3, location=location.absolute, style=shape.circle, size=size.normal)
    bgcolor(color.new(color.green, 90) if showBSBackground and bought else na)
    bgcolor(color.new(color.red, 90) if showBSBackground and sold else na)
    buyWatchColor: Persistent[Color] = color.new(color.orange, 20)
    sellWatchColor: Persistent[Color] = color.new(color.fuchsia, 20)
    rsiWatchShape: Persistent[str] = "square"
    priceWatchShape: Persistent[str] = "diamond"
    atrWatchShape: Persistent[str] = "circle"
    def getWatchShape(watchType):
        __block_result_3__ = na
        __switch__ = watchType
        if __switch__ == "rsi":
            __block_result_3__ = shape.square
        elif __switch__ == "price":
            __block_result_3__ = shape.diamond
        elif __switch__ == "atr":
            __block_result_3__ = shape.circle
        return __block_result_3__

    plotshape(True if showWatchSignals and showRsiWatchPlot and (buyWatch2 or buyWatch3) else False, title='RSI Buy Watch', location=location.belowbar, color=buyWatchColor, style=getWatchShape('rsi'), size=size.tiny)
    plotshape(True if showWatchSignals and showRsiWatchPlot and (sellWatch2 or sellWatch3) else False, title='RSI Sell Watch', location=location.abovebar, color=sellWatchColor, style=getWatchShape('rsi'), size=size.tiny)
    plotshape(True if showWatchSignals and showPriceWatchPlot and buyWatch1 else False, title='Price Buy Watch', location=location.belowbar, color=buyWatchColor, style=getWatchShape('price'), size=size.tiny)
    plotshape(True if showWatchSignals and showPriceWatchPlot and sellWatch1 else False, title='Price Sell Watch', location=location.abovebar, color=sellWatchColor, style=getWatchShape('price'), size=size.tiny)
    plotshape(True if showWatchSignals and showAtrWatchPlot and buyWatch4 else False, title='ATR Buy Watch', location=location.belowbar, color=buyWatchColor, style=getWatchShape('atr'), size=size.tiny)
    plotshape(True if showWatchSignals and showAtrWatchPlot and sellWatch4 else False, title='ATR Sell Watch', location=location.abovebar, color=sellWatchColor, style=getWatchShape('atr'), size=size.tiny)

    showRSICandleColors = True if showRSICandleColors else False if showMaCandleColors else showRSICandleColors
    showMaCandleColors = True if showMaCandleColors else False if showRSICandleColors else showMaCandleColors
    oneHundredTo85 = showRSICandleColors and smoothedRsi <= 100 and (smoothedRsi >= 85)
    eightyFiveTo75 = showRSICandleColors and smoothedRsi < 85 and (smoothedRsi >= 75)
    seventyFiveTo70 = showRSICandleColors and smoothedRsi < 75 and (smoothedRsi >= 70)
    seventyTo65 = showRSICandleColors and smoothedRsi < 70 and (smoothedRsi >= 65)
    sixtyFiveTo60 = showRSICandleColors and smoothedRsi < 65 and (smoothedRsi >= 60)
    sixtyToYellowHigh = showRSICandleColors and smoothedRsi < 60 and (smoothedRsi >= 55)
    yellowHighToYellowLow = showRSICandleColors and smoothedRsi < 55 and (smoothedRsi >= 45)
    yellowLowTo40 = showRSICandleColors and smoothedRsi < 45 and (smoothedRsi >= 40)
    fourtyTo35 = showRSICandleColors and smoothedRsi < 40 and (smoothedRsi >= 35)
    thirtyFiveTo30 = showRSICandleColors and smoothedRsi < 35 and (smoothedRsi >= 30)
    thirtyTo25 = showRSICandleColors and smoothedRsi < 30 and (smoothedRsi >= 25)
    twentyFiveTo15 = showRSICandleColors and smoothedRsi < 25 and (smoothedRsi >= 15)
    fifteenTo0 = showRSICandleColors and smoothedRsi < 15 and (smoothedRsi >= 0)
    RsiCandleColor = color.new(color.white, 0) if oneHundredTo85 else color.new(color.lime, 0) if eightyFiveTo75 else color.new(color.lime, 0) if seventyFiveTo70 else color.new(color.green, 0) if seventyTo65 else color.new(color.green, 0) if sixtyFiveTo60 else color.new(color.green, 0) if sixtyToYellowHigh else color.new(color.yellow, 0) if yellowHighToYellowLow else color.new(color.red, 0) if yellowLowTo40 else color.new(color.red, 0) if fourtyTo35 else color.new(color.red, 0) if thirtyFiveTo30 else color.new(color.red, 0) if thirtyTo25 else color.new(color.red, 0) if twentyFiveTo15 else color.new(color.white, 0) if fifteenTo0 else na
    finalMaColor: Color = color.new(overMaColor, 0) if aboveBoth else color.new(midMaColor, 0) if betweenBoth else color.new(underMaColor, 0)

    maCandleColor = finalMaColor if showMaCandleColors else na
    buySignalCandle = showSignals and plotBuy
    sellSignalCandle = showSignals and plotSell
    CandleColor = color.new(color.orange, 0) if buySignalCandle else color.new(color.fuchsia, 0) if sellSignalCandle else RsiCandleColor if showRSICandleColors else maCandleColor if showMaCandleColors else na
    plotcandle(open, high, low, close, color=CandleColor, wickcolor=CandleColor, bordercolor=CandleColor)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
