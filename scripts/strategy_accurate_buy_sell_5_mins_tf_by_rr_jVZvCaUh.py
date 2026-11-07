"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool, cast_int
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, barmerge, close, color, display, dividends, earnings, fill, high,
    hlc3, input, location, low, math, na, nz, open, plot, plotshape, position, request, script,
    shape, size, splits, strategy, string, syminfo, ta, table, time, timeframe, volume, year
)
from pynecore.types import Color, Persistent, PersistentSeries, Series, Table

tttradetrend: str = 'Only place BUY or SELL orders with the direction of the Trend EMA.'
ttbuystring: str = 'Input your custom alert message here. In the Alert settings, choose "Accurate Buy & Sell" and "Alert() functionc calls only"\nIf you\'re using a 3Commas Bot, make sure to format your message correctly with forward slashes in front of each quotation, you can find videos about how to do this on YouTube. Or ask 3Commas support about how to format the message for PineScript.'
ttsellstring: str = 'Input your custom alert message here. In the Alert settings, choose "Accurate Buy & Sell" and "Alert() functionc calls only"\nIf you\'re using a 3Commas Bot, make sure to format your message correctly with forward slashes in front of each quotation, you can find videos about how to do this on YouTube. Or ask 3Commas support about how to format the message for PineScript.'
ttstopstring: str = 'Input your custom alert message here. In the Alert settings, choose "Accurate Buy & Sell" and "Alert() functionc calls only"\nIf you\'re using a 3Commas Bot, make sure to format your message correctly with forward slashes in front of each quotation, you can find videos about how to do this on YouTube. Or ask 3Commas support about how to format the message for PineScript.'


@script.strategy('Accurate BUY & SELL 5 mins TF by RR', overlay=True, initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=15, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    tradetrendoption=input.bool(False, title='Tade with Trend', tooltip=tttradetrend),
    len111=input.int(defval=200, minval=0, maxval=2000, title='Trend EMA Length'),
    alternatesignals=input(title='Alternate Signals', defval=True),
    longpositions=input(title='BUY Positions', defval=True),
    shortpositions=input(title='SELL Positions', defval=True),
    __input_5__=input.float(title='Stop Loss Warning (%)', defval=-2.5, minval=-50, maxval=0, step=0.1),
    stronglongscore=input.int(defval=10, minval=0, maxval=1000, title='Required Strong BUY Score'),
    strongshortscore=input.int(defval=10, minval=0, maxval=1000, title='Required Strong SELL Score'),
    weaklongscore=input.int(defval=8, minval=0, maxval=1000, title='Required Weak BUY Score'),
    weakshortscore=input.int(defval=8, minval=0, maxval=1000, title='Required Weak SELL Score'),
    emadirectionimportance=input.int(defval=2, minval=0, maxval=100, title='EMA Trend Direction Importance'),
    emapushpullimportance=input.int(defval=2, minval=0, maxval=100, title='EMA Pressure Importance'),
    supertrenddirimportance=input.int(defval=0, minval=0, maxval=100, title='SuperTrend Direction Importance'),
    supertrendrevimportance=input.int(defval=4, minval=0, maxval=100, title='SuperTrend Reversal Importance'),
    psardirimportance=input.int(defval=0, minval=0, maxval=100, title='Parabolic SAR Direction Importance'),
    psarrevimportance=input.int(defval=3, minval=0, maxval=100, title='Parabolic SAR Reversal Importance'),
    hmacloseposimportance=input.int(defval=1, minval=0, maxval=100, title='HMA Trend Direction Importance'),
    hmapivotimportance=input.int(defval=3, minval=0, maxval=100, title='HMA Pivot Importance'),
    rsidivimportance=input.int(defval=4, minval=0, maxval=100, title='RSI Divergence Importance'),
    rsilevelimportance=input.int(defval=0, minval=0, maxval=100, title='RSI Level Importance'),
    rsidirectionimportance=input.int(defval=1, minval=0, maxval=100, title='RSI Cross 50-Line Importance'),
    macddivimportance=input.int(defval=0, minval=0, maxval=100, title='MACD Divergence Importance'),
    histpivotimportance=input.int(defval=1, minval=0, maxval=100, title='MACD Histogram Pivot Importance'),
    macdcrosssignalimportance=input.int(defval=1, minval=0, maxval=100, title='MACD Cross Signal Importance'),
    wtdivimportance=input.int(defval=0, minval=0, maxval=100, title='WaveTrend Divergence Importance'),
    wtcrosssignalimportance=input.int(defval=4, minval=0, maxval=100, title='WaveTrend Cross Signal Importance'),
    sdivimportance=input.int(defval=1, minval=0, maxval=100, title='Stochastic Divergence Importance'),
    scrosssignalimportance=input.int(defval=1, minval=0, maxval=100, title='Stoch Cross Signal Importance'),
    bbcontimportance=input.int(defval=0, minval=0, maxval=100, title='BollingerBands Contact Importance'),
    atrrevimportance=input.int(defval=1, minval=0, maxval=100, title='ATR Reversal Importance'),
    rviposimportance=input.int(defval=3, minval=0, maxval=100, title='RVI Position Importance'),
    rvidivimportance=input.int(defval=4, minval=0, maxval=100, title='RVI Divergence Importance'),
    srcrossimportance=input.int(defval=0, minval=0, maxval=100, title='Support/Resistance Cross Importance'),
    obvdivimportance=input.int(defval=0, minval=0, maxval=100, title='OBV Divergence Importance'),
    cmfcrossimportance=input.int(defval=0, minval=0, maxval=100, title='CMF Cross 50-Line Importance'),
    cmflevimportance=input.int(defval=0, minval=0, maxval=100, title='CMF Level Importance'),
    vwapcrossimportance=input.int(defval=0, minval=0, maxval=100, title='VWAP Cross HMA Importance'),
    vwaptrendimportance=input.int(defval=0, minval=0, maxval=100, title='VWAP Trend Importance'),
    engulfingcandleimportance=input.int(defval=0, minval=0, maxval=100, title='Engulfing Candle Importance'),
    usebuyalert=input.bool(defval=True, title='Use BUY Alert', group='Alert Messages'),
    buystring=input.string(title='Buy Alert Message', defval='BUY', confirm=False, group='Alert Messages', tooltip=ttbuystring),
    usesellalert=input.bool(defval=True, title='Use SELL Alert', group='Alert Messages'),
    sellstring=input.string(title='Sell Alert Message', defval='SELL', confirm=False, group='Alert Messages', tooltip=ttsellstring),
    usestopalert=input.bool(defval=True, title='Use STOP Alert', group='Alert Messages'),
    stopstring=input.string(title='Stop Alert Message', defval='STOP', confirm=False, group='Alert Messages', tooltip=ttstopstring)
):
    price = plot(close, title='Close Line', color=color.new(color.blue, 0), display=display.none)
    src111 = close
    out111: Series = ta.ema(src111, len111)
    ma111 = plot(out111, title='EMA 200', linewidth=2, color=color.new(color.blue, 0), offset=0)
    mabuy = out111 > out111[1]
    masell = out111 < out111[1]
    len1: int = 9
    src1 = close
    out1: Series = ta.ema(src1, len1)
    ema1color = color.new('#00BCD4') if out1 > out1[1] else color.new('#E91E63')
    ema1 = plot(out1, title='EMA 9', linewidth=3, color=color.new(ema1color, 100), offset=0, display=display.none)
    fill(price, ema1, title='EMA 9 Fill', color=color.new(ema1color, 100), editable=True)
    len2: int = 21
    src2 = close
    out2: Series = ta.ema(src2, len2)
    ema2color = color.new('#00BCD4') if out2 > out2[1] else color.new('#E91E63')
    ema2 = plot(out2, title='EMA 21', linewidth=3, color=color.new(ema2color, 100), offset=0, display=display.none)
    fill(price, ema2, title='EMA 21 Fill', color=color.new(ema2color, 100), editable=True)
    len3: int = 55
    src3 = close
    out3: Series = ta.ema(src3, len3)
    ema3color = color.new('#00BCD4') if out3 > out3[1] else color.new('#E91E63')
    ema3 = plot(out3, title='EMA 55', linewidth=3, color=color.new(ema3color, 100), offset=0, display=display.none)
    fill(price, ema3, title='EMA 55 Fill', color=color.new(ema3color, 100), editable=True)
    len4: int = 100
    src4 = close
    out4: Series = ta.ema(src4, len4)
    ema4color = color.new('#00BCD4') if out4 > out4[1] else color.new('#E91E63')
    ema4 = plot(out4, title='EMA 100', linewidth=3, color=color.new(ema4color, 100), offset=0, display=display.none)
    fill(price, ema4, title='EMA 100 Fill', color=color.new(ema4color, 100), editable=True)
    len5: int = 200
    src5 = close
    out5: Series = ta.ema(src5, len5)
    ema5color = color.new('#00BCD4') if out5 > out5[1] else color.new('#E91E63')
    ema5 = plot(out5, title='EMA 200', linewidth=3, color=color.new(ema5color, 100), offset=0, display=display.none)
    fill(price, ema5, title='EMA 200 Fill', color=color.new(ema5color, 100), editable=True)
    atrPeriod: int = 10
    factor: int = 3
    direction: Series
    supertrend, direction = ta.supertrend(factor, atrPeriod)
    bodyMiddle = plot((open + close) / 2, display=display.none, title='Body Middle Line')
    uptrend = supertrend if direction < 0 and direction[1] > inline_series(0, 1) else na
    downtrend = supertrend if direction > 0 and direction[1] < inline_series(0, 1) else na
    len6: int = 100
    src6 = close
    hma: Series = ta.wma(2 * ta.wma(src6, cast_int(len6 / 2)) - ta.wma(src6, len6), math.floor(math.sqrt(len6)))
    hmacolor = color.new('#008000') if close > hma else color.new('#FF0000')
    plot(hma, title='HMA Line', color=color.new(hmacolor, 25), linewidth=3)
    start: float = 0.02
    increment: float = 0.01
    maximum: float = 0.2
    psar: Series = ta.sar(start, increment, maximum)
    len11: int = 14
    src11 = close
    lbR11: int = 2
    lbL11: int = 6
    rangeUpper11: int = 60
    rangeLower11: int = 5
    plotBull11: bool = True
    plotHiddenBull11: bool = False
    plotBear11: bool = True
    plotHiddenBear11: bool = False
    bearColor11 = color.red
    bullColor11 = color.green
    hiddenBullColor11 = color.new(color.green, 80)
    hiddenBearColor11 = color.new(color.red, 80)
    textColor11 = color.white
    noneColor11 = color.new(color.white, 100)
    osc11: Series = ta.rsi(src11, len11)
    plFound11: Series = False if na(ta.pivotlow(osc11, lbL11, lbR11)) else True
    phFound11: Series = False if na(ta.pivothigh(osc11, lbL11, lbR11)) else True
    def _inRange11(cond):
        bars11 = ta.barssince(cond == True)
        return rangeLower11 <= bars11 and bars11 <= rangeUpper11

    _inRange11_1 = _inRange11(plFound11[1])
    oscHL11 = osc11[lbR11] > ta.valuewhen(plFound11, osc11[lbR11], 1) and _inRange11_1
    priceLL11 = low[lbR11] < ta.valuewhen(plFound11, low[lbR11], 1)
    bullCond11: Series = plotBull11 and priceLL11 and oscHL11 and plFound11
    _inRange11_2 = _inRange11(plFound11[1])
    oscLL11 = osc11[lbR11] < ta.valuewhen(plFound11, osc11[lbR11], 1) and _inRange11_2
    priceHL11 = low[lbR11] > ta.valuewhen(plFound11, low[lbR11], 1)
    hiddenBullCond11 = plotHiddenBull11 and priceHL11 and oscLL11 and plFound11
    _inRange11_3 = _inRange11(phFound11[1])
    oscLH11 = osc11[lbR11] < ta.valuewhen(phFound11, osc11[lbR11], 1) and _inRange11_3
    priceHH11 = high[lbR11] > ta.valuewhen(phFound11, high[lbR11], 1)
    bearCond11: Series = plotBear11 and priceHH11 and oscLH11 and phFound11
    _inRange11_4 = _inRange11(phFound11[1])
    oscHH11 = osc11[lbR11] > ta.valuewhen(phFound11, osc11[lbR11], 1) and _inRange11_4
    priceLH11 = high[lbR11] < ta.valuewhen(phFound11, high[lbR11], 1)
    hiddenBearCond11 = plotHiddenBear11 and priceLH11 and oscHH11 and phFound11
    fast_length12: int = 12
    slow_length12: int = 26
    src12 = close
    signal_length12: int = 9
    sma_source12: str = 'EMA'
    sma_signal12: str = 'EMA'
    col_macd12: Color = color.new('#2962FF')
    col_signal12: Color = color.new('#FF6D00')
    col_grow_above12: Color = color.new('#26A69A')
    col_fall_above12: Color = color.new('#B2DFDB')
    col_grow_below12: Color = color.new('#FFCDD2')
    col_fall_below12: Color = color.new('#FF5252')
    fast_ma12 = ta.sma(src12, fast_length12) if sma_source12 == 'SMA' else ta.ema(src12, fast_length12)
    slow_ma12 = ta.sma(src12, slow_length12) if sma_source12 == 'SMA' else ta.ema(src12, slow_length12)
    macd: Series = fast_ma12 - slow_ma12
    signal: Series = ta.sma(macd, signal_length12) if sma_signal12 == 'SMA' else ta.ema(macd, signal_length12)
    hist: Series = macd - signal
    donttouchzero12: bool = True
    lbR12: int = 2
    lbL12: int = 6
    rangeUpper12: int = 60
    rangeLower12: int = 5
    plotBull12: bool = True
    plotHiddenBull12: bool = False
    plotBear12: bool = True
    plotHiddenBear12: bool = False
    bearColor12 = color.red
    bullColor12 = color.green
    hiddenBullColor12 = color.new(color.green, 80)
    hiddenBearColor12 = color.new(color.red, 80)
    textColor12 = color.white
    noneColor12 = color.new(color.white, 100)
    osc12: Series = macd
    plFound12: Series = False if na(ta.pivotlow(osc12, lbL12, lbR12)) else True
    phFound12: Series = False if na(ta.pivothigh(osc12, lbL12, lbR12)) else True
    def _inRange12(cond):
        bars12 = ta.barssince(cond == True)
        return rangeLower12 <= bars12 and bars12 <= rangeUpper12

    _inRange12_1 = _inRange12(plFound12[1])
    oscHL12 = osc12[lbR12] > ta.valuewhen(plFound12, osc12[lbR12], 1) and _inRange12_1 and (osc12[lbR12] < 0)
    priceLL12 = low[lbR12] < ta.valuewhen(plFound12, low[lbR12], 1)
    priceHHZero12 = ta.highest(osc12, lbL12 + lbR12 + 5)
    blowzero12 = priceHHZero12 < 0 if donttouchzero12 else True
    bullCond12: Series = plotBull12 and priceLL12 and oscHL12 and plFound12 and blowzero12
    _inRange12_2 = _inRange12(plFound12[1])
    oscLL12 = osc12[lbR12] < ta.valuewhen(plFound12, osc12[lbR12], 1) and _inRange12_2
    priceHL12 = low[lbR12] > ta.valuewhen(plFound12, low[lbR12], 1)
    hiddenBullCond12 = plotHiddenBull12 and priceHL12 and oscLL12 and plFound12
    _inRange12_3 = _inRange12(phFound12[1])
    oscLH12 = osc12[lbR12] < ta.valuewhen(phFound12, osc12[lbR12], 1) and _inRange12_3 and (osc12[lbR12] > 0)
    priceLLZero12 = ta.lowest(osc12, lbL12 + lbR12 + 5)
    bearzero12 = priceLLZero12 > 0 if donttouchzero12 else True
    priceHH12 = high[lbR12] > ta.valuewhen(phFound12, high[lbR12], 1)
    bearCond12: Series = plotBear12 and priceHH12 and oscLH12 and phFound12 and bearzero12
    _inRange12_4 = _inRange12(phFound12[1])
    oscHH12 = osc12[lbR12] > ta.valuewhen(phFound12, osc12[lbR12], 1) and _inRange12_4
    priceLH12 = high[lbR12] < ta.valuewhen(phFound12, high[lbR12], 1)
    hiddenBearCond12 = plotHiddenBear12 and priceLH12 and oscHH12 and phFound12
    n1: int = 9
    n2: int = 12
    ap = hlc3
    esa = ta.ema(ap, n1)
    d1 = ta.ema(math.abs(ap - esa), n1)
    ci = (ap - esa) / (0.015 * d1)
    tci = ta.ema(ci, n2)
    hline__ren__: int = 0
    wt1: Series = tci
    wt2: Series = ta.sma(wt1, 4)
    lbR13: int = 2
    lbL13: int = 6
    rangeUpper13: int = 60
    rangeLower13: int = 5
    plotBull13: bool = True
    plotHiddenBull13: bool = False
    plotBear13: bool = True
    plotHiddenBear13: bool = False
    bearColor13 = color.red
    bullColor13 = color.green
    hiddenBullColor13 = color.green
    hiddenBearColor13 = color.red
    textColor13 = color.white
    noneColor13 = color.new(color.white, 100)
    k13 = wt1
    d13 = wt2
    osc13: Series = k13
    plFound13: Series = False if na(ta.pivotlow(osc13, lbL13, lbR13)) else True
    phFound13: Series = False if na(ta.pivothigh(osc13, lbL13, lbR13)) else True
    def _inRange13(cond):
        bars13 = ta.barssince(cond == True)
        return rangeLower13 <= bars13 and bars13 <= rangeUpper13

    _inRange13_1 = _inRange13(plFound13[1])
    oscHL13 = osc13[lbR13] > ta.valuewhen(plFound13, osc13[lbR13], 1) and _inRange13_1
    priceLL13 = low[lbR13] < ta.valuewhen(plFound13, low[lbR13], 1)
    bullCond13: Series = plotBull13 and priceLL13 and oscHL13 and plFound13
    _inRange13_2 = _inRange13(plFound13[1])
    oscLL13 = osc13[lbR13] < ta.valuewhen(plFound13, osc13[lbR13], 1) and _inRange13_2
    priceHL13 = low[lbR13] > ta.valuewhen(plFound13, low[lbR13], 1)
    hiddenBullCond13 = plotHiddenBull13 and priceHL13 and oscLL13 and plFound13
    _inRange13_3 = _inRange13(phFound13[1])
    oscLH13 = osc13[lbR13] < ta.valuewhen(phFound13, osc13[lbR13], 1) and _inRange13_3
    priceHH13 = high[lbR13] > ta.valuewhen(phFound13, high[lbR13], 1)
    bearCond13: Series = plotBear13 and priceHH13 and oscLH13 and phFound13
    _inRange13_4 = _inRange13(phFound13[1])
    oscHH13 = osc13[lbR13] > ta.valuewhen(phFound13, osc13[lbR13], 1) and _inRange13_4
    priceLH13 = high[lbR13] < ta.valuewhen(phFound13, high[lbR13], 1)
    hiddenBearCond13 = plotHiddenBear13 and priceLH13 and oscHH13 and phFound13
    periodK14: int = 14
    smoothK14: int = 3
    periodD14: int = 3
    k14: Series = ta.sma(ta.stoch(close, high, low, periodK14), smoothK14)
    d14: Series = ta.sma(k14, periodD14)
    lbR14: int = 2
    lbL14: int = 6
    rangeUpper14: int = 60
    rangeLower14: int = 5
    plotBull14: bool = True
    plotHiddenBull14: bool = False
    plotBear14: bool = True
    plotHiddenBear14: bool = False
    bearColor14 = color.red
    bullColor14 = color.green
    hiddenBullColor14 = color.green
    hiddenBearColor14 = color.red
    textColor14 = color.white
    noneColor14 = color.new(color.white, 100)
    osc14: Series = k14
    plFound14: Series = False if na(ta.pivotlow(osc14, lbL14, lbR14)) else True
    phFound14: Series = False if na(ta.pivothigh(osc14, lbL14, lbR14)) else True
    def _inRange14(cond):
        bars14 = ta.barssince(cond == True)
        return rangeLower14 <= bars14 and bars14 <= rangeUpper14

    _inRange14_1 = _inRange14(plFound14[1])
    oscHL14 = osc14[lbR14] > ta.valuewhen(plFound14, osc14[lbR14], 1) and _inRange14_1
    priceLL14 = low[lbR14] < ta.valuewhen(plFound14, low[lbR14], 1)
    bullCond14: Series = plotBull14 and priceLL14 and oscHL14 and plFound14
    _inRange14_2 = _inRange14(plFound14[1])
    oscLL14 = osc14[lbR14] < ta.valuewhen(plFound14, osc14[lbR14], 1) and _inRange14_2
    priceHL14 = low[lbR14] > ta.valuewhen(plFound14, low[lbR14], 1)
    hiddenBullCond14 = plotHiddenBull14 and priceHL14 and oscLL14 and plFound14
    _inRange14_3 = _inRange14(phFound14[1])
    oscLH14 = osc14[lbR14] < ta.valuewhen(phFound14, osc14[lbR14], 1) and _inRange14_3
    priceHH14 = high[lbR14] > ta.valuewhen(phFound14, high[lbR14], 1)
    bearCond14: Series = plotBear14 and priceHH14 and oscLH14 and phFound14
    _inRange14_4 = _inRange14(phFound14[1])
    oscHH14 = osc14[lbR14] > ta.valuewhen(phFound14, osc14[lbR14], 1) and _inRange14_4
    priceLH14 = high[lbR14] < ta.valuewhen(phFound14, high[lbR14], 1)
    hiddenBearCond14 = plotHiddenBear14 and priceLH14 and oscHH14 and phFound14
    length1: int = 20
    src7 = close
    mult1: float = 2.0
    basis = ta.sma(src7, length1)
    dev = mult1 * ta.stdev(src7, length1)
    upper = basis + dev
    lower = basis - dev
    offset: int = 0
    length2: int = 1
    mult2: float = 1.85
    showLabels: bool = True
    useClose: bool = False
    highlightState: bool = False
    atr = mult2 * ta.atr(length2)
    longStop: Series = (ta.highest(close, length2) if useClose else ta.highest(length2)) - atr
    longStopPrev = nz(longStop[1], longStop)
    longStop = math.max(longStop, longStopPrev) if close[1] > longStopPrev else longStop
    shortStop: Series = (ta.lowest(close, length2) if useClose else ta.lowest(length2)) + atr
    shortStopPrev = nz(shortStop[1], shortStop)
    shortStop = math.min(shortStop, shortStopPrev) if close[1] < shortStopPrev else shortStop
    dir: PersistentSeries[int] = 1
    dir = 1 if close > shortStopPrev else -1 if close < longStopPrev else dir
    longColor: Persistent[Color] = color.white
    shortColor: Persistent[Color] = color.white
    buySignal = dir == 1 and dir[1] == -1
    sellSignal = dir == -1 and dir[1] == 1
    length15: int = 12
    src15 = close
    len15: int = 14
    stddev15 = ta.stdev(src15, length15)
    upper15 = ta.ema(0 if ta.change(src15) <= 0 else stddev15, len15)
    lower15 = ta.ema(0 if ta.change(src15) > 0 else stddev15, len15)
    rvi: Series = upper15 / (upper15 + lower15) * 100
    lbR15: int = 2
    lbL15: int = 6
    rangeUpper15: int = 60
    rangeLower15: int = 5
    plotBull15: bool = True
    plotHiddenBull15: bool = False
    plotBear15: bool = True
    plotHiddenBear15: bool = False
    bearColor15 = color.red
    bullColor15 = color.green
    hiddenBullColor15 = color.green
    hiddenBearColor15 = color.red
    textColor15 = color.white
    noneColor15 = color.new(color.white, 100)
    d15 = rvi
    osc15: Series = d15
    plFound15: Series = False if na(ta.pivotlow(osc15, lbL15, lbR15)) else True
    phFound15: Series = False if na(ta.pivothigh(osc15, lbL15, lbR15)) else True
    def _inRange15(cond):
        bars15 = ta.barssince(cond == True)
        return rangeLower15 <= bars15 and bars15 <= rangeUpper15

    _inRange15_1 = _inRange15(plFound15[1])
    oscHL15 = osc15[lbR15] > ta.valuewhen(plFound15, osc15[lbR15], 1) and _inRange15_1
    priceLL15 = low[lbR15] < ta.valuewhen(plFound15, low[lbR15], 1)
    bullCond15: Series = plotBull15 and priceLL15 and oscHL15 and plFound15
    _inRange15_2 = _inRange15(plFound15[1])
    oscLL15 = osc15[lbR15] < ta.valuewhen(plFound15, osc15[lbR15], 1) and _inRange15_2
    priceHL15 = low[lbR15] > ta.valuewhen(plFound15, low[lbR15], 1)
    hiddenBullCond15 = plotHiddenBull15 and priceHL15 and oscLL15 and plFound15
    _inRange15_3 = _inRange15(phFound15[1])
    oscLH15 = osc15[lbR15] < ta.valuewhen(phFound15, osc15[lbR15], 1) and _inRange15_3
    priceHH15 = high[lbR15] > ta.valuewhen(phFound15, high[lbR15], 1)
    bearCond15: Series = plotBear15 and priceHH15 and oscLH15 and phFound15
    _inRange15_4 = _inRange15(phFound15[1])
    oscHH15 = osc15[lbR15] > ta.valuewhen(phFound15, osc15[lbR15], 1) and _inRange15_4
    priceLH15 = high[lbR15] < ta.valuewhen(phFound15, high[lbR15], 1)
    hiddenBearCond15 = plotHiddenBear15 and priceLH15 and oscHH15 and phFound15
    left16: int = 200
    right16: int = 20
    quick_right16: int = 5
    src16: str = 'Close'
    pivothigh_1 = ta.pivothigh(close, left16, right16)
    pivothigh_2 = ta.pivothigh(high, left16, right16)
    pivot_high16 = pivothigh_1 if src16 == 'Close' else pivothigh_2
    pivotlow_1 = ta.pivotlow(close, left16, right16)
    pivotlow_2 = ta.pivotlow(low, left16, right16)
    pivot_lows16 = pivotlow_1 if src16 == 'Close' else pivotlow_2
    pivothigh_3 = ta.pivothigh(close, left16, quick_right16)
    pivothigh_4 = ta.pivothigh(high, left16, quick_right16)
    quick_pivot_high16 = pivothigh_3 if src16 == 'Close' else pivothigh_4
    pivotlow_3 = ta.pivotlow(close, left16, quick_right16)
    pivotlow_4 = ta.pivotlow(low, left16, quick_right16)
    quick_pivot_lows16 = pivotlow_3 if src16 == 'Close' else pivotlow_4
    valuewhen_1 = ta.valuewhen(cast_bool(quick_pivot_high16), close[quick_right16], 0)
    valuewhen_2 = ta.valuewhen(cast_bool(quick_pivot_high16), high[quick_right16], 0)
    level1: Series = valuewhen_1 if src16 == 'Close' else valuewhen_2
    valuewhen_3 = ta.valuewhen(cast_bool(quick_pivot_lows16), close[quick_right16], 0)
    valuewhen_4 = ta.valuewhen(cast_bool(quick_pivot_lows16), low[quick_right16], 0)
    level2: Series = valuewhen_3 if src16 == 'Close' else valuewhen_4
    valuewhen_5 = ta.valuewhen(cast_bool(pivot_high16), close[right16], 0)
    valuewhen_6 = ta.valuewhen(cast_bool(pivot_high16), high[right16], 0)
    level3: Series = valuewhen_5 if src16 == 'Close' else valuewhen_6
    valuewhen_7 = ta.valuewhen(cast_bool(pivot_lows16), close[right16], 0)
    valuewhen_8 = ta.valuewhen(cast_bool(pivot_lows16), low[right16], 0)
    level4: Series = valuewhen_7 if src16 == 'Close' else valuewhen_8
    valuewhen_9 = ta.valuewhen(cast_bool(pivot_high16), close[right16], 1)
    valuewhen_10 = ta.valuewhen(cast_bool(pivot_high16), high[right16], 1)
    level5: Series = valuewhen_9 if src16 == 'Close' else valuewhen_10
    valuewhen_11 = ta.valuewhen(cast_bool(pivot_lows16), close[right16], 1)
    valuewhen_12 = ta.valuewhen(cast_bool(pivot_lows16), low[right16], 1)
    level6: Series = valuewhen_11 if src16 == 'Close' else valuewhen_12
    valuewhen_13 = ta.valuewhen(cast_bool(pivot_high16), close[right16], 2)
    valuewhen_14 = ta.valuewhen(cast_bool(pivot_high16), high[right16], 2)
    level7: Series = valuewhen_13 if src16 == 'Close' else valuewhen_14
    valuewhen_15 = ta.valuewhen(cast_bool(pivot_lows16), close[right16], 2)
    valuewhen_16 = ta.valuewhen(cast_bool(pivot_lows16), low[right16], 2)
    level8: Series = valuewhen_15 if src16 == 'Close' else valuewhen_16
    level1_col = color.green if close >= level1 else color.red
    level2_col = color.green if close >= level2 else color.red
    level3_col = color.green if close >= level3 else color.red
    level4_col = color.green if close >= level4 else color.red
    level5_col = color.green if close >= level5 else color.red
    level6_col = color.green if close >= level6 else color.red
    level7_col = color.green if close >= level7 else color.red
    level8_col = color.green if close >= level8 else color.red
    length17: int = 9
    src17 = close
    hma17: Series = ta.wma(2 * ta.wma(src17, cast_int(length17 / 2)) - ta.wma(src17, length17), math.floor(math.sqrt(length17)))
    buy1 = hma17 > level1 and hma17[1] < level1[1] and (close > close[2])
    buy2 = hma17 > level2 and hma17[1] < level2[1] and (close > close[2])
    buy3 = hma17 > level3 and hma17[1] < level3[1] and (close > close[2])
    buy4 = hma17 > level4 and hma17[1] < level4[1] and (close > close[2])
    buy5 = hma17 > level5 and hma17[1] < level5[1] and (close > close[2])
    buy6 = hma17 > level6 and hma17[1] < level6[1] and (close > close[2])
    buy7 = hma17 > level7 and hma17[1] < level7[1] and (close > close[2])
    buy8 = hma17 > level8 and hma17[1] < level8[1] and (close > close[2])
    sell1 = hma17 < level1 and hma17[1] > level1[1] and (close < close[2])
    sell2 = hma17 < level2 and hma17[1] > level2[1] and (close < close[2])
    sell3 = hma17 < level3 and hma17[1] > level3[1] and (close < close[2])
    sell4 = hma17 < level4 and hma17[1] > level4[1] and (close < close[2])
    sell5 = hma17 < level5 and hma17[1] > level5[1] and (close < close[2])
    sell6 = hma17 < level6 and hma17[1] > level6[1] and (close < close[2])
    sell7 = hma17 < level7 and hma17[1] > level7[1] and (close < close[2])
    sell8 = hma17 < level8 and hma17[1] > level8[1] and (close < close[2])
    len18: int = 20
    src18 = close
    lbR18: int = 2
    lbL18: int = 6
    rangeUpper18: int = 60
    rangeLower18: int = 5
    plotBull18: bool = True
    plotHiddenBull18: bool = False
    plotBear18: bool = True
    plotHiddenBear18: bool = False
    bearColor18 = color.red
    bullColor18 = color.green
    hiddenBullColor18 = color.green
    hiddenBearColor18 = color.new(color.red, 80)
    textColor18 = color.white
    noneColor18 = color.new(color.white, 100)
    csrc = ta.change(src18)
    def obv1(src18):
        return ta.cum(volume if ta.change(src18) > 0 else -volume if csrc < 0 else 0 * volume)

    os = obv1(src18)
    obv_osc: Series = os - ta.ema(os, len18)
    obc_color = color.green if obv_osc > 0 else color.red
    plFound18: Series = False if na(ta.pivotlow(obv_osc, lbL18, lbR18)) else True
    phFound18: Series = False if na(ta.pivothigh(obv_osc, lbL18, lbR18)) else True
    def _inRange(cond):
        bars = ta.barssince(cond == True)
        return rangeLower18 <= bars and bars <= rangeUpper18

    _inRange_1 = _inRange(plFound18[1])
    oscHL18 = obv_osc[lbR18] > ta.valuewhen(plFound18, obv_osc[lbR18], 1) and _inRange_1
    priceLL18 = low[lbR18] < ta.valuewhen(plFound18, low[lbR18], 1)
    bullCond18: Series = plotBull18 and priceLL18 and oscHL18 and plFound18
    _inRange_2 = _inRange(plFound18[1])
    oscLL18 = obv_osc[lbR18] < ta.valuewhen(plFound18, obv_osc[lbR18], 1) and _inRange_2
    priceHL18 = low[lbR18] > ta.valuewhen(plFound18, low[lbR18], 1)
    hiddenBullCond18 = plotHiddenBull18 and priceHL18 and oscLL18 and plFound18
    _inRange_3 = _inRange(phFound18[1])
    oscLH18 = obv_osc[lbR18] < ta.valuewhen(phFound18, obv_osc[lbR18], 1) and _inRange_3
    priceHH18 = high[lbR18] > ta.valuewhen(phFound18, high[lbR18], 1)
    bearCond18: Series = plotBear18 and priceHH18 and oscLH18 and phFound18
    _inRange_4 = _inRange(phFound18[1])
    oscHH18 = obv_osc[lbR18] > ta.valuewhen(phFound18, obv_osc[lbR18], 1) and _inRange_4
    priceLH18 = high[lbR18] < ta.valuewhen(phFound18, high[lbR18], 1)
    hiddenBearCond18 = plotHiddenBear18 and priceLH18 and oscHH18 and phFound18
    length19: int = 50
    ad19 = 0 if close == high and close == low or high == low else (2 * close - low - high) / (high - low) * volume
    cmf: Series = math.sum(ad19, length19) / math.sum(volume, length19)
    def computeVWAP(src20, isNewPeriod, stDevMultiplier):
        sumSrcVol: PersistentSeries[float] = na(float)
        sumVol: PersistentSeries[float] = na(float)
        sumSrcSrcVol: PersistentSeries[float] = na(float)
        sumSrcVol = src20 * volume if isNewPeriod else src20 * volume + sumSrcVol[1]
        sumVol = volume if isNewPeriod else volume + sumVol[1]
        sumSrcSrcVol = volume * math.pow(src20, 2) if isNewPeriod else volume * math.pow(src20, 2) + sumSrcSrcVol[1]
        _vwap = sumSrcVol / sumVol
        variance = sumSrcSrcVol / sumVol - math.pow(_vwap, 2)
        variance = 0 if variance < 0 else variance
        stDev = math.sqrt(variance)
        lowerBand20 = _vwap - stDev * stDevMultiplier
        upperBand20 = _vwap + stDev * stDevMultiplier
        return (_vwap, lowerBand20, upperBand20)

    hideonDWM: bool = False
    anchor: Persistent[str] = 'Session'
    src20: Series = hlc3
    offset20: int = 0
    showBands: bool = True
    stdevMult: float = 1.0
    def timeChange(period):
        return ta.change(time(period))

    new_earnings = request.earnings(syminfo.tickerid, earnings.actual, barmerge.gaps_on, barmerge.lookahead_on)
    new_dividends = request.dividends(syminfo.tickerid, dividends.gross, barmerge.gaps_on, barmerge.lookahead_on)
    new_split = request.splits(syminfo.tickerid, splits.denominator, barmerge.gaps_on, barmerge.lookahead_on)
    tcD = timeChange('D')
    tcW = timeChange('W')
    tcM = timeChange('M')
    tc3M = timeChange('3M')
    tc12M = timeChange('12M')
    isNewPeriod = new_earnings if anchor == 'Earnings' else new_dividends if anchor == 'Dividends' else new_split if anchor == 'Splits' else True if na(src20[1]) else tcD if anchor == 'Session' else tcW if anchor == 'Week' else tcM if anchor == 'Month' else tc3M if anchor == 'Quarter' else tc12M if anchor == 'Year' else tc12M and year % 10 == 0 if anchor == 'Decade' else tc12M and year % 100 == 0 if anchor == 'Century' else False
    vwapValue: Series[float] = na(float)
    std: float = na(float)
    upperBandValue: float = na(float)
    lowerBandValue: float = na(float)
    if not (hideonDWM and timeframe.isdwm):
        _vwap, bottom, top = computeVWAP(src20, isNewPeriod, stdevMult)
        vwapValue = _vwap
        upperBandValue = top if showBands else na
        lowerBandValue = bottom if showBands else na
    C_DownTrend: bool = True
    C_UpTrend: bool = True
    trendRule1: Persistent[str] = 'SMA50'
    trendRule2: Persistent[str] = 'SMA50, SMA200'
    trendRule: Persistent = trendRule1
    if trendRule == trendRule1:
        priceAvg = ta.sma(close, 50)
        C_DownTrend = close < priceAvg
        C_UpTrend = close > priceAvg
    if trendRule == trendRule2:
        sma200 = ta.sma(close, 200)
        sma50 = ta.sma(close, 50)
        C_DownTrend = close < sma50 and sma50 < sma200
        C_UpTrend = close > sma50 and sma50 > sma200
    C_Len: int = 14
    C_ShadowPercent: float = 5.0
    C_ShadowEqualsPercent: float = 100.0
    C_DojiBodyPercent: float = 5.0
    C_Factor: float = 2.0
    C_BodyHi: Series = math.max(close, open)
    C_BodyLo: Series = math.min(close, open)
    C_Body = C_BodyHi - C_BodyLo
    C_BodyAvg = ta.ema(C_Body, C_Len)
    C_SmallBody: Series = C_Body < C_BodyAvg
    C_LongBody = C_Body > C_BodyAvg
    C_UpShadow = high - C_BodyHi
    C_DnShadow = C_BodyLo - low
    C_HasUpShadow = C_UpShadow > C_ShadowPercent / 100 * C_Body
    C_HasDnShadow = C_DnShadow > C_ShadowPercent / 100 * C_Body
    C_WhiteBody: Series = open < close
    C_BlackBody: Series = open > close
    C_Range = high - low
    C_IsInsideBar = C_BodyHi[1] > C_BodyHi and C_BodyLo[1] < C_BodyLo
    C_BodyMiddle = C_Body / 2 + C_BodyLo
    C_ShadowEquals = C_UpShadow == C_DnShadow or (math.abs(C_UpShadow - C_DnShadow) / C_DnShadow * 100 < C_ShadowEqualsPercent and math.abs(C_DnShadow - C_UpShadow) / C_UpShadow * 100 < C_ShadowEqualsPercent)
    C_IsDojiBody = C_Range > 0 and C_Body <= C_Range * C_DojiBodyPercent / 100
    C_Doji = C_IsDojiBody and C_ShadowEquals
    patternLabelPosLow = low - ta.atr(30) * 0.6
    patternLabelPosHigh = high + ta.atr(30) * 0.6
    label_color_bullish = color.blue
    C_EngulfingBullishNumberOfCandles: int = 2
    C_EngulfingBullish = C_DownTrend and C_WhiteBody and C_LongBody and C_BlackBody[1] and C_SmallBody[1] and (close >= open[1]) and (open <= close[1]) and (close > open[1] or open < close[1])
    if C_EngulfingBullish:
        'Engulfing\nAt the end of a given downward trend, there will most likely be a reversal pattern. To distinguish the first day, this candlestick pattern uses a small body, followed by a day where the candle body fully overtakes the body from the day before, and closes in the trend’s opposite direction. Although similar to the outside reversal chart pattern, it is not essential for this pattern to completely overtake the range (high to low), rather only the open and the close.'
    label_color_bearish = color.red
    C_EngulfingBearishNumberOfCandles: int = 2
    C_EngulfingBearish = C_UpTrend and C_BlackBody and C_LongBody and C_WhiteBody[1] and C_SmallBody[1] and (close <= open[1]) and (open >= close[1]) and (close < open[1] or open > close[1])
    if C_EngulfingBearish:
        'Engulfing\nAt the end of a given uptrend, a reversal pattern will most likely appear. During the first day, this candlestick pattern uses a small body. It is then followed by a day where the candle body fully overtakes the body from the day before it and closes in the trend’s opposite direction. Although similar to the outside reversal chart pattern, it is not essential for this pattern to fully overtake the range (high to low), rather only the open and the close.'
    stoplosspercent = __input_5__ / 100
    emadirectionup = emadirectionimportance if out5 < close else 0
    emadirectionupstatus = 'EMA Trend Direction Up' if cast_bool(emadirectionup) else na
    emadirectiondown = emadirectionimportance if out5 > close else 0
    emadirectiondownstatus = 'EMA Trend Direction Down' if cast_bool(emadirectiondown) else na
    emapushup = emapushpullimportance if out2 > out2[1] and out3 < out3[1] else 0
    emapushupstatus = 'EMA Pushing Up' if cast_bool(emapushup) else na
    emapulldown = emapushpullimportance if out2 < out2[1] and out3 > out3[1] else 0
    emapulldownstatus = 'EMA Pulling Down' if cast_bool(emapulldown) else na
    supertrendup = supertrenddirimportance if direction < 0 else 0
    supertrendupstatus = 'SuperTrend Direction Up' if cast_bool(supertrendup) else na
    supertrenddown = supertrenddirimportance if direction > 0 else 0
    supertrenddownstatus = 'SuperTrend Direction Down' if cast_bool(supertrenddown) else na
    supertrendrevup = supertrendrevimportance if direction < 0 and direction[1] > inline_series(0, 1) else 0
    supertrendrevupstatus = 'SuperTrend Reversed Up' if cast_bool(supertrendrevup) else na
    supertrendrevdown = supertrendrevimportance if direction > 0 and direction[1] < inline_series(0, 1) else 0
    supertrendrevdownstatus = 'SuperTrend Reversed Down' if cast_bool(supertrendrevdown) else na
    psardirup = psardirimportance if psar < close else 0
    psardirupstatus = 'PSAR Direction Up' if cast_bool(psardirup) else na
    psardirdown = psardirimportance if psar > close else 0
    psardirdownstatus = 'PSAR Direction Down' if cast_bool(psardirdown) else na
    psarrevup = psarrevimportance if psar < close and psar[1] > close[1] else 0
    psarrevupstatus = 'PSAR Reversed Up' if cast_bool(psarrevup) else na
    psarrevdown = psarrevimportance if psar > close and psar[1] < close else 0
    psarrevdownstatus = 'PSAR Reversed Down' if cast_bool(psarrevdown) else na
    hmacloseposup = hmacloseposimportance if hma < close and cast_bool(hma[1]) else 0
    hmacloseposupstatus = 'Price Crossed Over HMA' if cast_bool(hmacloseposup) else na
    hmacloseposdown = hmacloseposimportance if hma > close else 0
    hmacloseposdownstatus = 'Price Crossed Under HMA' if cast_bool(hmacloseposdown) else na
    hmapivotup = hmapivotimportance if hma > hma[1] and hma[1] < hma[2] else 0
    hmapivotupstatus = 'HMA Pivot Up' if cast_bool(hmapivotup) else na
    hmapivotdown = hmapivotimportance if hma < hma[1] and hma[1] > hma[2] else 0
    hmapivotdownstatus = 'HMA Pivot Down' if cast_bool(hmapivotdown) else na
    rsidivup = rsidivimportance if bullCond11 or bullCond11[1] or bullCond11[2] else 0
    rsidivupstatus = 'Bullish RSI Divergence' if rsidivup else na
    rsidivdown = rsidivimportance if bearCond11 or bearCond11[1] or bearCond11[2] else 0
    rsidivdownstatus = 'Bearish RSI Divergence' if rsidivdown else na
    rsioversold = rsilevelimportance if osc11 < 30 else 0
    rsioversoldstatus = 'RSI Oversold' if cast_bool(rsioversold) else na
    rsioverbought = rsilevelimportance if osc11 > 70 else 0
    rsioverboughtstatus = 'RSI Overbought' if cast_bool(rsioverbought) else na
    rsicrossup = rsidirectionimportance if osc11 > 50 and osc11[1] < 50 or (osc11 > 50 and osc11[2] < 50) else 0
    rsicrossupstatus = 'RSI Crossed 50-Line Up' if cast_bool(rsicrossup) else na
    rsicrossdown = rsidirectionimportance if osc11 < 50 and osc11[1] > 50 or (osc11 < 50 and osc11[2] > 50) else 0
    rsicrossdownstatus = 'RSI Crossed 50-Line Down' if cast_bool(rsicrossdown) else na
    macddivup = macddivimportance if bullCond12 or bullCond12[1] or bullCond12[2] else 0
    macddivupstatus = 'Bullish MACD Divergence' if macddivup else na
    macddivdown = macddivimportance if bearCond12 or bearCond12[1] or bearCond12[2] else 0
    macddivdownstatus = 'Bearish MACD Divergence' if macddivdown else na
    histpivotup = histpivotimportance if hist > hist[1] and hist[1] < hist[2] and (hist < 0) else 0
    histpivotupstatus = 'MACD Histogram Pivot Up' if cast_bool(histpivotup) else na
    histpivotdown = histpivotimportance if hist < hist[1] and hist[1] > hist[2] and (hist > 0) else 0
    histpivotdownstatus = 'MACD Histogram Pivot Down' if cast_bool(histpivotdown) else na
    macdcrosssignalup = macdcrosssignalimportance if macd > signal and macd[1] < signal[1] and (signal < 0) else 0
    macdcrosssignalupstatus = 'MACD Crossed Signal Up' if cast_bool(macdcrosssignalup) else na
    macdcrosssignaldown = macdcrosssignalimportance if macd < signal and macd[1] > signal[1] and (signal > 0) else 0
    macdcrosssignaldownstatus = 'MACD Crossed Signal Down' if cast_bool(macdcrosssignaldown) else na
    wtdivup = wtdivimportance if bullCond13 or bullCond13[1] or bullCond13[2] else 0
    wtdivupstatus = 'Bullish WaveTrend Divergence' if wtdivup else na
    wtdivdown = wtdivimportance if bearCond13 or bearCond13[1] or bearCond13[2] else 0
    wtdivdownstatus = 'Bearish WaveTrend Divergence' if wtdivdown else na
    wtcrosssignalup = wtcrosssignalimportance if wt1 > wt2 and wt1[1] < wt2[1] and (wt2 < -10) else 0
    wtcrosssignalupstatus = 'WaveTrend Crossed Signal Up' if cast_bool(wtcrosssignalup) else na
    wtcrosssignaldown = wtcrosssignalimportance if wt1 < wt2 and wt1[1] > wt2[1] and (wt2 > 10) else 0
    wtcrosssignaldownstatus = 'WaveTrend Crossed Signal Down' if cast_bool(wtcrosssignaldown) else na
    sdivup = sdivimportance if bullCond14 or bullCond14[1] or bullCond14[2] else 0
    sdivupstatus = 'Bullish Stoch Divergence' if sdivup else na
    sdivdown = sdivimportance if bearCond14 or bearCond14[1] or bearCond14[2] else 0
    sdivdownstatus = 'Bearish Stoch Divergence' if sdivdown else na
    scrosssignalup = scrosssignalimportance if k14 > d14 and k14[1] < d14[1] else 0
    scrosssignalupstatus = 'Stoch Crossed Signal Up' if cast_bool(scrosssignalup) else na
    scrosssignaldown = scrosssignalimportance if k14 < d14 and k14[1] > d14[1] else 0
    scrosssignaldownstatus = 'Stoch Crossed Signal Down' if cast_bool(scrosssignaldown) else na
    bbcontup = bbcontimportance if close < lower else 0
    bbcontupstatus = 'Price Contacted Lower BB' if cast_bool(bbcontup) else na
    bbcontdown = bbcontimportance if open > upper else 0
    bbcontdownstatus = 'Price Contacted Upper BB' if cast_bool(bbcontdown) else na
    atrrevup = atrrevimportance if buySignal else 0
    atrrevupstatus = 'ATR Reversed Up' if cast_bool(atrrevup) else na
    atrrevdown = atrrevimportance if sellSignal else 0
    atrrevdownstatus = 'ATR Reversed Down' if cast_bool(atrrevdown) else na
    rviposup = rviposimportance if rvi > 25 and rvi[1] < 40 else 0
    rviposupstatus = 'RVI Volatility Increasing' if cast_bool(rviposup) else na
    rviposdown = rviposimportance if rvi < 75 and rvi[1] > 60 else 0
    rviposdownstatus = 'RVI Volatility Decreasing' if cast_bool(rviposdown) else na
    rvidivup = rvidivimportance if bullCond15 or bullCond15[1] or bullCond15[2] else 0
    rvidivupstatus = 'Bullish RVI Divergence' if rvidivup else na
    rvidivdown = rvidivimportance if bearCond15 or bearCond15[1] or bearCond15[2] else 0
    rvidivdownstatus = 'Bearish RVI Divergence' if rvidivdown else na
    srcrossup = srcrossimportance if buy1 or buy2 or buy3 or buy4 or buy5 or buy6 or buy7 or buy8 else 0
    srcrossupstatus = 'Crossed Key Level Up' if cast_bool(srcrossup) else na
    srcrossdown = srcrossimportance if sell1 or sell2 or sell3 or sell4 or sell5 or sell6 or sell7 or sell8 else 0
    srcrossdownstatus = 'Crossed Key Level Down' if cast_bool(srcrossdown) else na
    obvdivup = obvdivimportance if bullCond18 or bullCond18[1] or bullCond18[2] else 0
    obvdivupstatus = 'Bullish OBV Divergence' if obvdivup else na
    obvdivdown = obvdivimportance if bearCond18 or bearCond18[1] or bearCond18[2] else 0
    obvdivdownstatus = 'Bearish OBV Divergence' if obvdivdown else na
    cmfcrossup = cmfcrossimportance if cmf > 0 and cmf[1] < 0 else 0
    cmfcrossupstatus = 'CMF Crossed 50-Line Up' if cast_bool(cmfcrossup) else na
    cmfcrossdown = cmfcrossimportance if cmf < 0 and cmf[1] > 0 else 0
    cmfcrossdownstatus = 'CMF Crossed 50-Line Down' if cast_bool(cmfcrossdown) else na
    cmflevup = cmflevimportance if cmf > 0 else 0
    cmflevupstatus = 'CMF Level Up' if cast_bool(cmflevup) else na
    cmflevdown = cmflevimportance if cmf < 0 else 0
    cmflevdownstatus = 'CMF Level Down' if cast_bool(cmflevdown) else na
    vwapcrossup = vwapcrossimportance if hma < vwapValue and hma[1] > vwapValue[1] else 0
    vwapcrossupstatus = 'VWAP Crossed Above HMA' if cast_bool(vwapcrossup) else na
    vwapcrossdown = vwapcrossimportance if hma > vwapValue and hma[1] < vwapValue[1] else 0
    vwapcrossdownstatus = 'VWAP Crossed Below HMA' if cast_bool(vwapcrossdown) else na
    vwaptrendup = vwaptrendimportance if out2 > vwapValue else 0
    vwaptrendupstatus = 'VWAP Up Trend' if cast_bool(vwaptrendup) else na
    vwaptrenddown = vwaptrendimportance if out2 < vwapValue else 0
    vwaptrenddownstatus = 'VWAP Down Trend' if cast_bool(vwaptrenddown) else na
    bulleng = engulfingcandleimportance if C_EngulfingBullish else 0
    bullengstatus = 'Bullish Engulfing Candle' if cast_bool(bulleng) else na
    beareng = engulfingcandleimportance if C_EngulfingBearish else 0
    bearengstatus = 'Bearish Engulfing Candle' if cast_bool(beareng) else na
    stronglongentrysignal = emadirectionup + emapushup + supertrendup + supertrendrevup + psardirup + psarrevup + hmacloseposup + hmapivotup + rsidivup + rsioversold + rsicrossup + macddivup + histpivotup + macdcrosssignalup + wtdivup + wtcrosssignalup + sdivup + scrosssignalup + bbcontup + atrrevup + rviposup + rvidivup + srcrossup + obvdivup + cmfcrossup + cmflevup + vwapcrossup + vwaptrendup + bulleng >= stronglongscore
    strongshortentrysignal = emadirectiondown + emapulldown + supertrenddown + supertrendrevdown + psardirdown + psarrevdown + hmacloseposdown + hmapivotdown + rsidivdown + rsioverbought + rsicrossdown + macddivdown + histpivotdown + macdcrosssignaldown + wtdivdown + wtcrosssignaldown + sdivdown + scrosssignaldown + bbcontdown + atrrevdown + rviposdown + rvidivdown + srcrossdown + obvdivdown + cmfcrossdown + cmflevdown + vwapcrossdown + vwaptrenddown + beareng >= strongshortscore
    weaklongentrysignal = emadirectionup + emapushup + supertrendup + supertrendrevup + psardirup + psarrevup + hmacloseposup + hmapivotup + rsidivup + rsioversold + rsicrossup + macddivup + histpivotup + macdcrosssignalup + wtdivup + wtcrosssignalup + sdivup + scrosssignalup + bbcontup + atrrevup + rviposup + rvidivup + srcrossup + obvdivup + cmfcrossup + cmflevup + vwapcrossup + vwaptrendup + bulleng >= weaklongscore
    weakshortentrysignal = emadirectiondown + emapulldown + supertrenddown + supertrendrevdown + psardirdown + psarrevdown + hmacloseposdown + hmapivotdown + rsidivdown + rsioverbought + rsicrossdown + macddivdown + histpivotdown + macdcrosssignaldown + wtdivdown + wtcrosssignaldown + sdivdown + scrosssignaldown + bbcontdown + atrrevdown + rviposdown + rvidivdown + srcrossdown + obvdivdown + cmfcrossdown + cmflevdown + vwapcrossdown + vwaptrenddown + beareng >= weakshortscore
    pos: Persistent[int] = 0
    if stronglongentrysignal and pos <= 0:
        pos = 1
    if strongshortentrysignal and pos >= 0:
        pos = -1
    longentry = pos == 1 and inline_series(pos != 1, 1)
    shortentry = pos == -1 and inline_series(pos != -1, 1)
    alternatelong = longentry if alternatesignals else stronglongentrysignal
    alternateshort = shortentry if alternatesignals else strongshortentrysignal
    plotshape(alternatelong and mabuy if tradetrendoption else alternatelong, title='Strong Long Label', style=shape.labelup, location=location.belowbar, color=color.new(color.new('#228B22'), 0), text='BUY', textcolor=color.new(color.white, 0), size=size.small)
    plotshape(alternateshort and masell if tradetrendoption else alternateshort, title='Strong Short Label', style=shape.labeldown, location=location.abovebar, color=color.new(color.new('#FF0000'), 0), text='SELL', textcolor=color.new(color.white, 0), size=size.small)
    plotshape(weaklongentrysignal, title='Weak Buy Triangle', style=shape.triangleup, location=location.belowbar, color=color.new(color.new('#228B22'), 100), size=size.small)
    plotshape(weakshortentrysignal, title='Weak Sell Triangle', style=shape.triangledown, location=location.abovebar, color=color.new(color.new('#FF0000'), 100), size=size.small)
    statuswindow: Persistent[Table] = table.new(position.top_right, 100, 100, border_width=2)
    txt1: str = '🡇            TREND             🡇'
    table.cell(statuswindow, 0, 0, text=txt1, bgcolor=color.new(color.new('#000000'), 100), text_color=color.white, text_size=size.small)
    if cast_bool(emadirectionup):
        table.cell(statuswindow, 0, 0, text=string.tostring(emadirectionupstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if cast_bool(emadirectiondown):
        table.cell(statuswindow, 0, 0, text=string.tostring(emadirectiondownstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    if 1 if cast_bool(emapushup) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(emapushupstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(emapushup) else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(emapulldown) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(emapulldownstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(emapulldown) else 1:
        table.clear(statuswindow, 0, 0)
    if cast_bool(hmacloseposup):
        table.cell(statuswindow, 0, 0, text=string.tostring(hmacloseposupstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if cast_bool(hmacloseposdown):
        table.cell(statuswindow, 0, 0, text=string.tostring(hmacloseposdownstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    if 1 if cast_bool(hmapivotup) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(hmapivotupstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(hmapivotup) else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(hmapivotdown) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(hmapivotdownstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(hmapivotdown) else 1:
        table.clear(statuswindow, 0, 0)
    txt2: str = '🡇         MOMENTUM         🡇'
    table.cell(statuswindow, 0, 0, text=txt2, bgcolor=color.new(color.new('#000000'), 100), text_color=color.white, text_size=size.small)
    if 1 if rsidivup else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(rsidivupstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if na if rsidivup else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if rsidivdown else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(rsidivdownstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    if na if rsidivdown else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(rsioversold) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(rsioversoldstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(rsioversold) else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(rsioverbought) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(rsioverboughtstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(rsioverbought) else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(rsicrossup) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(rsicrossupstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(rsicrossup) else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(rsicrossdown) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(rsicrossdownstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(rsicrossdown) else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if macddivup else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(macddivupstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if na if macddivup else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if macddivdown else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(macddivdownstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    if na if macddivdown else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(histpivotup) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(histpivotupstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(histpivotup) else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(histpivotdown) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(histpivotdownstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(histpivotdown) else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(macdcrosssignalup) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(macdcrosssignalupstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(macdcrosssignalup) else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(macdcrosssignaldown) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(macdcrosssignaldownstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(macdcrosssignaldown) else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if wtdivup else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(wtdivupstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if na if wtdivup else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if wtdivdown else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(wtdivdownstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    if na if wtdivdown else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(wtcrosssignalup) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(wtcrosssignalupstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(wtcrosssignalup) else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(wtcrosssignaldown) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(wtcrosssignaldownstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(wtcrosssignaldown) else 1:
        table.clear(statuswindow, 0, 0)
    txt3: str = '🡇         VOLATILITY         🡇'
    table.cell(statuswindow, 0, 0, text=txt3, bgcolor=color.new(color.new('#000000'), 100), text_color=color.white, text_size=size.small)
    if 1 if cast_bool(rviposup) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(rviposupstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(rviposup) else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(rviposdown) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(rviposdownstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(rviposdown) else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if rvidivup else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(rvidivupstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if na if rvidivup else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if rvidivdown else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(rvidivdownstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    if na if rvidivdown else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(vwapcrossup) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(vwapcrossupstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(vwapcrossup) else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(vwapcrossdown) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(vwapcrossdownstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    if na if cast_bool(vwapcrossdown) else 1:
        table.clear(statuswindow, 0, 0)
    if 1 if cast_bool(vwaptrendup) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(vwaptrendupstatus), bgcolor=color.new(color.new('#00BCD4'), 50), text_color=color.white, text_size=size.small)
    if 1 if cast_bool(vwaptrenddown) else False:
        table.cell(statuswindow, 0, 0, text=string.tostring(vwaptrenddownstatus), bgcolor=color.new(color.new('#E91E63'), 50), text_color=color.white, text_size=size.small)
    longstoploss: Series = strategy.position_avg_price * (1 + stoplosspercent)
    shortstoploss: Series = strategy.position_avg_price * (1 - stoplosspercent)
    printstoplong = longstoploss > close and longstoploss[1] < close[1] and (strategy.position_size > 0)
    printstopshort = shortstoploss < close and shortstoploss[1] > close[1] and (strategy.position_size < 0)
    plot(longstoploss if strategy.position_size > 0 else na, style=plot.style_line, color=color.new(color.yellow, 50), linewidth=1, title='Stop Long Line', display=display.none)
    plot(shortstoploss if strategy.position_size < 0 else na, style=plot.style_line, color=color.new(color.yellow, 50), linewidth=1, title='Stop Short Line', display=display.none)
    plotshape(printstoplong, title='Stop Long Label', style=shape.labelup, location=location.belowbar, color=color.new(color.yellow, 0), text='𝐒𝐓𝐎𝐏LOSS', textcolor=color.new(color.black, 0), size=size.tiny)
    plotshape(printstopshort, title='Stop Short Label', style=shape.labeldown, location=location.abovebar, color=color.new(color.yellow, 0), text='𝐒𝐓𝐎𝐏LOSS', textcolor=color.new(color.black, 0), size=size.tiny)
    if alternatelong and mabuy and longpositions if tradetrendoption else alternatelong and longpositions:
        strategy.entry('longposition', strategy.long, comment='Buy Entry')
    if (shortentry or printstoplong) and longpositions:
        strategy.close('longposition', comment='Exit Buy')
    if alternateshort and masell and shortpositions if tradetrendoption else alternateshort and shortpositions:
        strategy.entry('shortposition', strategy.short, comment=' Sell Entry')
    if (longentry or printstopshort) and shortpositions:
        strategy.close('shortposition', comment='Exit Sell')
    if longentry and longpositions and usebuyalert:
        alert(buystring, alert.freq_once_per_bar)
    if shortentry and shortpositions and usesellalert:
        alert(sellstring, alert.freq_once_per_bar)
    if printstoplong or (printstopshort and usestopalert):
        alert(stopstring, alert.freq_once_per_bar)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
