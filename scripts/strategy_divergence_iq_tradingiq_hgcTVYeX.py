"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from enum import StrEnum as Enum
from pynecore import pine_range
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, array, bar_index, barstate, chart, close, color, display, fill,
    format, high, hl2, hlc3, hlcc4, input, label, line, low, map, math, na, nz, ohlc4, open, plot,
    position, request, script, size, strategy, string, syminfo, ta, table, time, xloc, yloc
)
from pynecore.types import Color, Label, Line, NA, Persistent, Series
from pynecore.types.chart import ChartPoint


class divInput(Enum):
    pivotPoints = 'Pivots'
    immediate = 'Immediate'


class normalizationInput(Enum):
    rollingMinMax = 'Rolling Min Max'
    rollingZscore = 'Rolling Z-score'
    robustScaling = 'Robust Scaling'
    none = 'None'


class exitInput(Enum):
    atr = 'ATR'
    percent = 'Percentage'


@udt
class pivotData:
    indicatorPiv: ChartPoint = na(ChartPoint)
    pricePiv: ChartPoint = na(ChartPoint)


@udt
class mapValuesString:
    direction: str = "Direction"
    trades: str = "Trades"
    wins: str = "Wins"
    profit: str = "Profit"
    grossGain: str = "Gross Gain"
    grossLoss: str = "Gross Loss"
    target: str = "Target"
    stop: str = "Stop"
    entry: str = "Entry"


@udt
class exitDrawings:
    targetPrice: float = na(float)
    stopPrice: float = na(float)
    exitLabel: Label = na(Label)


@script.strategy("Divergence IQ [TradingIQ]", overlay=False, precision=3, slippage=1, initial_capital=1000, process_orders_on_close=True, calc_on_every_tick=True, default_qty_value=5, default_qty_type=strategy.percent_of_equity, commission_type=strategy.commission.percent, commission_value=0.02, max_lines_count=500, max_labels_count=500, max_boxes_count=500, max_polylines_count=100)
def main(
    src: Series[float] = input.source(defval=close, title="Indicator", group="Divergence Detection Setup"),
    divMethod=input.enum(defval=divInput.pivotPoints, title="Divergence Detection Method", options=(divInput.pivotPoints, divInput.immediate)),
    useCloses=input.bool(defval=False, title="Use Closing Prices For Divergence Detection", group="Divergence Detection Setup"),
    leftLook=input.int(defval=6, minval=1, title="Left Lookback", group="Divergence Detection Setup"),
    rightLook=input.int(defval=6, minval=1, title="Right Lookahead", group="Divergence Detection Setup"),
    normMethod=input.enum(defval=normalizationInput.none, title="Normalize Indicator", group="Normalization", options=(normalizationInput.none, normalizationInput.robustScaling, normalizationInput.rollingZscore, normalizationInput.rollingMinMax)),
    window=input.int(defval=50, minval=2, title="Normalization Window", group="Normalization"),
    showFinal=input.bool(defval=True, title="Plot Indicator (Required When Using Normalization)", group="Normalization"),
    showPrice=input.bool(defval=True, title="Plot Price", group="Normalization"),
    onChart=input.bool(defval=True, title="Show Divergences On Price", group="Divergence Settings"),
    bullDivShow=input.bool(defval=True, title="Bullish Divergence Color", group="Divergence Settings", inline="BullDiv"),
    bearDivShow=input.bool(defval=True, title="Bearish Divergence Color", group="Divergence Settings", inline="BearDiv"),
    bullHDivShow=input.bool(defval=True, title="Bullish Hidden Divergence Color", group="Divergence Settings", inline="BullHDiv"),
    bearHDivShow=input.bool(defval=True, title="Bearish Hidden Divergence Color", group="Divergence Settings", inline="BearHDiv"),
    bullDivCol=input.color(defval=color.new('#74FFBC'), title="", group="Divergence Settings", inline="BullDiv"),
    bearDivCol=input.color(defval=color.rgb(255, 116, 116), title="", group="Divergence Settings", inline="BearDiv"),
    bullHDivCol=input.color(defval=color.new('#FFB674'), title="", group="Divergence Settings", inline="BullHDiv"),
    bearHDivCol=input.color(defval=color.rgb(223, 116, 255), title="", group="Divergence Settings", inline="BearHDiv"),
    bullDivTrade=input.bool(defval=True, title="Trade", group="Divergence Settings", inline="BullDiv"),
    bearDivTrade=input.bool(defval=True, title="Trade", group="Divergence Settings", inline="BearDiv"),
    bullHDivTrade=input.bool(defval=True, title="Trade", group="Divergence Settings", inline="BullHDiv"),
    bearHDivTrade=input.bool(defval=True, title="Trade", group="Divergence Settings", inline="BearHDiv"),
    exitType=input.enum(defval=exitInput.atr, title="Stop Loss & Target Type", options=(exitInput.atr, exitInput.percent), group="Strategy Settings"),
    profitTargetMult=input.float(defval=2, minval=0, title="Profit Target ATR Multiplier (Or Perecntage)", group="Strategy Settings"),
    stopLossMult=input.float(defval=2, minval=0, title="Stop Loss ATR Multiplier (Or Percentage)", group="Strategy Settings"),
    gradientFlow=input.bool(defval=True, title="Show Gradient Flow", group="Gradient Flow Settings"),
    gradientFlowCol=input.color(defval=color.new('#F23645'), title="Gradient Flow Color", group="Gradient Flow Settings")
):
    if not onChart and divMethod == divInput.immediate:
        bullDivCol = NA(Color)
        bearDivCol = NA(Color)
        bullHDivCol = NA(Color)
        bearHDivCol = NA(Color)



    tradeMap: Persistent[dict[str, float]] = map.new()
    mapValues: Persistent[mapValuesString] = mapValuesString()
    atr = ta.atr(14)

    def normalize():
        normSrc = src

        srcArr: Persistent[list[float]] = array.new_float()

        array.push(srcArr, src)

        if array.size(srcArr) > window:
            array.shift(srcArr)

        if normMethod == normalizationInput.rollingMinMax:
            srcMax = array.max(srcArr)
            srcMin = array.min(srcArr)

            normSrc = (src - srcMin) / (srcMax - srcMin)

        if normMethod == normalizationInput.rollingZscore:
            mean = array.avg(srcArr)
            stdDev = array.stdev(srcArr)

            __block_result__ = na
            __switch_1__ = stdDev
            if __switch_1__ == 0:
                __block_result__ = 0
            else:
                __block_result__ = (src - mean) / stdDev
            normSrc = __block_result__

        if normMethod == normalizationInput.robustScaling:
            median = array.median(srcArr)

            devArr: list[float] = array.new_float(array.size(srcArr), na)

            for i, data in enumerate(devArr):
                array.set(devArr, i, math.abs(array.get(srcArr, i) - median))

            mad = array.median(devArr)

            __block_result_1__ = na
            __switch_1__ = mad != 0
            if __switch_1__ == True:
                __block_result_1__ = 0.6745 * (src - median) / mad
            else:
                __block_result_1__ = 0
            normSrc = __block_result_1__

        return normSrc

    @method
    def appendPivot(id: list[pivotData], value: float, price: Series[float], upPivot: bool):
        __block_result_2__ = na
        if not na(value):
            __block_result_2__ = array.push(id, pivotData(chart.point.from_time(time[rightLook], value), chart.point.from_time(time[rightLook], price[rightLook])))
        return __block_result_2__

    @method
    def add(id: dict[str, float], key: str, value: float, isShort: bool):
        finalValue = value

        if isShort:
            finalValue *= -1

        return map.put(id, key, nz(map.get(id, key)) + finalValue)

    @method
    def addAll(id: dict[str, float], isProfit: bool, getTarget: float, getEntry: float, getStop: float, isShort: bool, exitData: exitDrawings):
        __block_result_3__ = (na, na, na, na)
        __switch__ = isShort
        if __switch__ == False:
            __block_result_3__ = (yloc.abovebar, "▽", "Long Exit At: ", 1)
        else:
            __block_result_3__ = (yloc.belowbar, "△", "Short Exit At: ", -1)
        ylocNow, textNow, tooltipNow, mult = __block_result_3__

        __block_result_4__ = na
        __switch__ = isProfit
        if __switch__ == True:
            add(id, mapValues.wins, 1, False)
            add(id, mapValues.trades, 1, False)
            add(id, mapValues.profit, (getTarget / getEntry - 1) * 100, isShort)
            add(id, mapValues.grossGain, math.abs(getTarget - getEntry), False)
            map.put(id, mapValues.direction, 0)
            exitData.stopPrice = NA(float)
            exitData.targetPrice = NA(float)
            exitData.exitLabel = label.new(bar_index, getTarget, yloc=ylocNow, color=color.new(color.rgb(128, 116, 255), 80), textcolor=color.rgb(128, 116, 255), text=textNow, style=label.style_text_outline, force_overlay=True, tooltip=tooltipNow + string.tostring(getTarget, format.mintick) + '\nReturn: ' + string.tostring((getTarget / getEntry - 1) * 100 * mult, format.percent))
            __block_result_4__ = exitData.exitLabel
        else:
            add(id, mapValues.trades, 1, False)
            add(id, mapValues.profit, (getStop / getEntry - 1) * 100, isShort)
            add(id, mapValues.grossLoss, math.abs(getStop - getEntry), False)
            map.put(id, mapValues.direction, 0)
            exitData.stopPrice = NA(float)
            exitData.targetPrice = NA(float)
            exitData.exitLabel = label.new(bar_index, getStop, yloc=ylocNow, color=color.new(color.rgb(128, 116, 255), 80), textcolor=color.rgb(128, 116, 255), text=textNow, style=label.style_text_outline, force_overlay=True, tooltip=tooltipNow + string.tostring(getStop, format.mintick) + '\nReturn: ' + string.tostring((getStop / getEntry - 1) * 100 * mult, format.percent))
            __block_result_4__ = exitData.exitLabel
        return __block_result_4__

    pivotsUp: Persistent[list[pivotData]] = array.new(0, NA(pivotData))
    pivotsDn: Persistent[list[pivotData]] = array.new(0, NA(pivotData))
    pivotsUpH: Persistent[list[pivotData]] = array.new(0, NA(pivotData))
    pivotsDnH: Persistent[list[pivotData]] = array.new(0, NA(pivotData))

    finalSrc: Series = normalize()

    getPH = ta.pivothigh(finalSrc, leftLook, rightLook)
    getPL = ta.pivotlow(finalSrc, leftLook, rightLook)

    __block_result_5__ = (na, na)
    __switch__ = useCloses
    if __switch__ == True:
        __block_result_5__ = (close, close)
    else:
        __block_result_5__ = (high, low)
    getHigh: Series
    getLow: Series
    getHigh, getLow = __block_result_5__

    appendPivot(pivotsUp, getPH, getHigh, True)
    appendPivot(pivotsDn, getPL, getLow, False)
    appendPivot(pivotsUpH, getPH, getHigh, True)
    appendPivot(pivotsDnH, getPL, getLow, False)

    o, h, l, c = request.security_lower_tf(syminfo.tickerid, '1', (open, high, low, close))
    exitData: Persistent[exitDrawings] = exitDrawings(NA(float), NA(float), NA(Label))

    @method
    def tradeExits(tradeMap: dict[str, float]):
        if na(map.get(tradeMap, mapValues.direction)):
            map.put(tradeMap, mapValues.direction, 0)

        if map.get(tradeMap, mapValues.direction) == 1:
            isShort: bool = False

            getTarget = map.get(tradeMap, mapValues.target)
            getStop = map.get(tradeMap, mapValues.stop)
            getEntry = map.get(tradeMap, mapValues.entry)

            if open >= getTarget:
                addAll(tradeMap, True, getTarget, getEntry, getStop, isShort, exitData)
            elif open <= getStop:
                addAll(tradeMap, False, getTarget, getEntry, getStop, isShort, exitData)
            elif high >= getTarget:
                if low > getStop:
                    addAll(tradeMap, True, getTarget, getEntry, getStop, isShort, exitData)
                else:
                    if method_call('size', h) > 0:
                        for i in pine_range(0, method_call('size', h) - 1):
                            ltfHigh = method_call('get', h, i)
                            ltfLow = method_call('get', l, i)
                            ltfClose = method_call('get', c, i)
                            ltfOpen = method_call('get', o, i)

                            if ltfHigh >= getTarget:
                                if ltfLow > getStop:
                                    addAll(tradeMap, True, getTarget, getEntry, getStop, isShort, exitData)
                                else:
                                    closer2low = math.abs(ltfOpen - ltfHigh) > math.abs(ltfOpen - ltfLow)

                                    __switch_7__ = closer2low
                                    if __switch_7__ == True:
                                        addAll(tradeMap, False, getTarget, getEntry, getStop, isShort, exitData)
                                    else:
                                        addAll(tradeMap, True, getTarget, getEntry, getStop, isShort, exitData)
                                break
                            elif ltfLow <= getStop:
                                addAll(tradeMap, False, getTarget, getEntry, getStop, isShort, exitData)

                                break
                    else:
                        closer2low = math.abs(open - high) > math.abs(open - low)

                        __switch_4__ = closer2low
                        if __switch_4__ == True:
                            addAll(tradeMap, False, getTarget, getEntry, getStop, isShort, exitData)
                        else:
                            addAll(tradeMap, True, getTarget, getEntry, getStop, isShort, exitData)
            elif low <= getStop:
                addAll(tradeMap, False, getTarget, getEntry, getStop, isShort, exitData)
        elif map.get(tradeMap, mapValues.direction) == -1:
            isShort: bool = True

            getTarget = map.get(tradeMap, mapValues.target)
            getStop = map.get(tradeMap, mapValues.stop)
            getEntry = map.get(tradeMap, mapValues.entry)

            if open <= getTarget:
                addAll(tradeMap, True, getTarget, getEntry, getStop, isShort, exitData)
            elif open >= getStop:
                addAll(tradeMap, False, getTarget, getEntry, getStop, isShort, exitData)
            elif low <= getTarget:
                if high < getStop:
                    addAll(tradeMap, True, getTarget, getEntry, getStop, isShort, exitData)
                else:
                    if method_call('size', h) > 0:
                        for i in pine_range(0, method_call('size', h) - 1):
                            ltfHigh = method_call('get', h, i)
                            ltfLow = method_call('get', l, i)
                            ltfClose = method_call('get', c, i)
                            ltfOpen = method_call('get', o, i)

                            if ltfLow <= getTarget:
                                if ltfHigh < getStop:
                                    addAll(tradeMap, True, getTarget, getEntry, getStop, isShort, exitData)
                                else:
                                    closer2low = math.abs(ltfOpen - ltfHigh) > math.abs(ltfOpen - ltfLow)

                                    __switch_7__ = closer2low
                                    if __switch_7__ == True:
                                        addAll(tradeMap, True, getTarget, getEntry, getStop, isShort, exitData)
                                    else:
                                        addAll(tradeMap, False, getTarget, getEntry, getStop, isShort, exitData)
                                break
                            elif ltfHigh >= getStop:
                                addAll(tradeMap, False, getTarget, getEntry, getStop, isShort, exitData)

                                break
                    else:
                        closer2low = math.abs(open - high) > math.abs(open - low)

                        __switch_4__ = closer2low
                        if __switch_4__ == True:
                            addAll(tradeMap, True, getTarget, getEntry, getStop, isShort, exitData)
                        else:
                            addAll(tradeMap, False, getTarget, getEntry, getStop, isShort, exitData)
            elif high >= getStop:
                addAll(tradeMap, False, getTarget, getEntry, getStop, isShort, exitData)

        return NA(float)

    def pivotsMethod():
        bearDiv: bool = False
        bearHdiv: bool = False

        tradeExits(tradeMap)

        if barstate.isconfirmed:
            if not na(getPH) and array.size(pivotsUp) > 1:
                recentPiv = array.last(pivotsUp)
                prevPiv = array.get(pivotsUp, -2)

                if bearDivShow or bearDivTrade:
                    if recentPiv.pricePiv.price > prevPiv.pricePiv.price:
                        if recentPiv.indicatorPiv.price < prevPiv.indicatorPiv.price:
                            bearDiv = True

                            if bearDivTrade and map.get(tradeMap, mapValues.direction) == 0 and (not na(atr)):
                                __block_result_6__ = (na, na)
                                __switch_6__ = exitType
                                if __switch_6__ == exitInput.atr:
                                    __block_result_6__ = (close + atr * stopLossMult, close - atr * profitTargetMult)
                                elif __switch_6__ == exitInput.percent:
                                    __block_result_6__ = (close * (1 + stopLossMult / 100), close * (1 - profitTargetMult / 100))
                                stop__000000ed__, target__000000ed__ = __block_result_6__

                                stop__000000ed__ = math.round_to_mintick(stop__000000ed__)
                                target__000000ed__ = math.round_to_mintick(target__000000ed__)

                                strategy.entry('Short Bearish Divergence', strategy.short)
                                strategy.exit('SB Exit', 'Short Bearish Divergence', stop=stop__000000ed__, limit=target__000000ed__)

                                label.new(bar_index, close, text='▽', textcolor=color.rgb(255, 116, 116), color=color.new(color.rgb(255, 116, 116), 80), style=label.style_text_outline, size=size.normal, tooltip='Bearish Divergence Short Entry At: ' + string.tostring(close, format.mintick) + '\nTarget: ' + string.tostring(target__000000ed__) + '\nStop: ' + string.tostring(stop__000000ed__), force_overlay=True, yloc=yloc.abovebar)

                                exitData.stopPrice = stop__000000ed__
                                exitData.targetPrice = target__000000ed__

                                map.put(tradeMap, mapValues.direction, -1)
                                map.put(tradeMap, mapValues.target, target__000000ed__)
                                map.put(tradeMap, mapValues.stop, stop__000000ed__)
                                map.put(tradeMap, mapValues.entry, close)

                            alert('Bearsih Divergence Detected', freq=alert.freq_once_per_bar_close)

                if bearHDivShow:
                    if recentPiv.pricePiv.price < prevPiv.pricePiv.price:
                        if recentPiv.indicatorPiv.price > prevPiv.indicatorPiv.price:
                            bearHdiv = True

                            if bearHDivTrade and map.get(tradeMap, mapValues.direction) == 0 and (not na(atr)):
                                __block_result_7__ = (na, na)
                                __switch_6__ = exitType
                                if __switch_6__ == exitInput.atr:
                                    __block_result_7__ = (close + atr * stopLossMult, close - atr * profitTargetMult)
                                elif __switch_6__ == exitInput.percent:
                                    __block_result_7__ = (close * (1 + stopLossMult / 100), close * (1 - profitTargetMult / 100))
                                stop__00000105__, target__00000105__ = __block_result_7__

                                stop__00000105__ = math.round_to_mintick(stop__00000105__)
                                target__00000105__ = math.round_to_mintick(target__00000105__)

                                strategy.entry('Short Hidden Bearish Divergence', strategy.short)
                                strategy.exit('SHB Exit', 'Short Hidden Bearish Divergence', stop=stop__00000105__, limit=target__00000105__)

                                label.new(bar_index, close, text='▽', textcolor=color.rgb(255, 116, 116), color=color.new(color.rgb(255, 116, 116), 80), style=label.style_text_outline, size=size.normal, tooltip='Hidden Bearish Divergence Short Entry At: ' + string.tostring(close, format.mintick) + '\nTarget: ' + string.tostring(target__00000105__) + '\nStop: ' + string.tostring(stop__00000105__), force_overlay=True, yloc=yloc.abovebar)

                                exitData.stopPrice = stop__00000105__
                                exitData.targetPrice = target__00000105__

                                map.put(tradeMap, mapValues.direction, -1)
                                map.put(tradeMap, mapValues.target, target__00000105__)
                                map.put(tradeMap, mapValues.stop, stop__00000105__)
                                map.put(tradeMap, mapValues.entry, close)

                            alert('Hidden Bearsih Divergence Detected', freq=alert.freq_once_per_bar_close)

        bullDiv: bool = False
        bullHdiv: bool = False

        if barstate.isconfirmed:
            if not na(getPL) and array.size(pivotsDn) > 1:
                recentPiv = array.last(pivotsDn)
                prevPiv = array.get(pivotsDn, -2)

                if bullDivShow:
                    if recentPiv.pricePiv.price < prevPiv.pricePiv.price:
                        if recentPiv.indicatorPiv.price > prevPiv.indicatorPiv.price:
                            bullDiv = True

                            if bullDivTrade and map.get(tradeMap, mapValues.direction) == 0 and (not na(atr)):
                                __block_result_8__ = (na, na)
                                __switch_6__ = exitType
                                if __switch_6__ == exitInput.atr:
                                    __block_result_8__ = (close - atr * stopLossMult, close + atr * profitTargetMult)
                                elif __switch_6__ == exitInput.percent:
                                    __block_result_8__ = (close * (1 - stopLossMult / 100), close * (1 + profitTargetMult / 100))
                                stop__00000121__, target__00000121__ = __block_result_8__

                                stop__00000121__ = math.round_to_mintick(stop__00000121__)
                                target__00000121__ = math.round_to_mintick(target__00000121__)

                                strategy.entry('Long Bullish Divergence', strategy.long)
                                strategy.exit('LB Exit', 'Long Bullish Divergence', stop=stop__00000121__, limit=target__00000121__)

                                label.new(bar_index, close, text='△', textcolor=color.new('#74FFBC'), color=color.new(color.new('#74FFBC'), 80), style=label.style_text_outline, size=size.normal, tooltip='Bullish Divergence Long Entry At: ' + string.tostring(close, format.mintick) + '\nTarget: ' + string.tostring(target__00000121__) + '\nStop: ' + string.tostring(stop__00000121__), force_overlay=True, yloc=yloc.belowbar)

                                exitData.stopPrice = stop__00000121__
                                exitData.targetPrice = target__00000121__

                                map.put(tradeMap, mapValues.direction, 1)
                                map.put(tradeMap, mapValues.target, target__00000121__)
                                map.put(tradeMap, mapValues.stop, stop__00000121__)
                                map.put(tradeMap, mapValues.entry, close)

                            alert('Bullish Divergence Detected', freq=alert.freq_once_per_bar_close)

                if bullHDivShow:
                    if recentPiv.pricePiv.price > prevPiv.pricePiv.price:
                        if recentPiv.indicatorPiv.price < prevPiv.indicatorPiv.price:
                            bullHdiv = True

                            if bullHDivTrade and map.get(tradeMap, mapValues.direction) == 0 and (not na(atr)):
                                __block_result_9__ = (na, na)
                                __switch_6__ = exitType
                                if __switch_6__ == exitInput.atr:
                                    __block_result_9__ = (close - atr * stopLossMult, close + atr * profitTargetMult)
                                elif __switch_6__ == exitInput.percent:
                                    __block_result_9__ = (close * (1 - stopLossMult / 100), close * (1 + profitTargetMult / 100))
                                stop__00000137__, target__00000137__ = __block_result_9__

                                stop__00000137__ = math.round_to_mintick(stop__00000137__)
                                target__00000137__ = math.round_to_mintick(target__00000137__)

                                strategy.entry('Long Hidden Bullish Divergence', strategy.long)
                                strategy.exit('LHB Exit', 'Long Hidden Bullish Divergence', stop=stop__00000137__, limit=target__00000137__)

                                label.new(bar_index, close, text='△', textcolor=color.new('#74FFBC'), color=color.new(color.new('#74FFBC'), 80), style=label.style_text_outline, size=size.normal, tooltip='Hidden Bullish Divergence Long Entry At: ' + string.tostring(close, format.mintick) + '\nTarget: ' + string.tostring(target__00000137__) + '\nStop: ' + string.tostring(stop__00000137__), force_overlay=True, yloc=yloc.belowbar)

                                exitData.stopPrice = stop__00000137__
                                exitData.targetPrice = target__00000137__

                                map.put(tradeMap, mapValues.direction, 1)
                                map.put(tradeMap, mapValues.target, target__00000137__)
                                map.put(tradeMap, mapValues.stop, stop__00000137__)
                                map.put(tradeMap, mapValues.entry, close)

                            alert('Hidden Bullish Divergence Detected', freq=alert.freq_once_per_bar_close)

        return (bearDiv, bearHdiv, bullDiv, bullHdiv)

    def immediateMethod():
        __hist_getLow__: Series[void] = getLow[0]
        __hist_finalSrc__: Series = finalSrc[0]
        __hist_getHigh__: Series[void] = getHigh[0]
        bearDiv: bool = False
        bearHdiv: bool = False
        bullDiv: bool = False
        bullHdiv: bool = False

        tradeExits(tradeMap)

        if barstate.isconfirmed:
            if array.size(pivotsUp) > 1:
                getRecent = array.last(pivotsUp)
                getRecentHidden = array.last(pivotsUpH)

                includesTime: Persistent[list[int]] = array.new_int()
                divLine: Persistent = NA(Line)
                priceLine: Persistent = NA(Line)

                includesTimeHidden: Persistent[list[int]] = array.new_int()
                divLineHidden: Persistent = NA(Line)
                priceLineHidden: Persistent = NA(Line)

                if finalSrc > getRecent.indicatorPiv.price:
                    array.push(pivotsUp, pivotData(chart.point.from_time(time, finalSrc), chart.point.from_time(time, getHigh)))

                if bearDivShow or bearDivTrade:
                    if not array.includes(includesTime, getRecent.indicatorPiv.time):
                        if __hist_finalSrc__[1] < getRecent.indicatorPiv.price and __hist_getHigh__[1] > getRecent.pricePiv.price:
                            if __hist_finalSrc__[1] > __hist_finalSrc__[2] and __hist_finalSrc__[1] > finalSrc:
                                if na(divLine):
                                    divLine = line.new(getRecent.indicatorPiv.time, getRecent.indicatorPiv.price, time[1], __hist_finalSrc__[1], xloc=xloc.bar_time, color=bearDivCol, style=line.style_dotted, width=2)

                                    priceLine = line.new(getRecent.pricePiv.time, getRecent.pricePiv.price, time[1], __hist_getHigh__[1], xloc=xloc.bar_time, color=bearDivCol, width=2, style=line.style_dotted, force_overlay=True)

                                    if map.get(tradeMap, mapValues.direction) == 0 and (not na(atr)):
                                        __block_result_10__ = (na, na)
                                        __switch_8__ = exitType
                                        if __switch_8__ == exitInput.atr:
                                            __block_result_10__ = (close + atr * stopLossMult, close - atr * profitTargetMult)
                                        elif __switch_8__ == exitInput.percent:
                                            __block_result_10__ = (close * (1 + stopLossMult / 100), close * (1 - profitTargetMult / 100))
                                        stop__0000016a__, target__0000016a__ = __block_result_10__

                                        stop__0000016a__ = math.round_to_mintick(stop__0000016a__)
                                        target__0000016a__ = math.round_to_mintick(target__0000016a__)

                                        strategy.entry('Short Bearish Divergence', strategy.short)
                                        strategy.exit('SB Exit', 'Short Bearish Divergence', stop=stop__0000016a__, limit=target__0000016a__)

                                        label.new(bar_index, close, text='▽', textcolor=color.rgb(255, 116, 116), color=color.new(color.rgb(255, 116, 116), 80), style=label.style_text_outline, size=size.normal, tooltip='Bearish Divergence Short Entry At: ' + string.tostring(close, format.mintick) + '\nTarget: ' + string.tostring(target__0000016a__) + '\nStop: ' + string.tostring(stop__0000016a__), force_overlay=True, yloc=yloc.abovebar)

                                        exitData.stopPrice = stop__0000016a__
                                        exitData.targetPrice = target__0000016a__

                                        map.put(tradeMap, mapValues.direction, -1)
                                        map.put(tradeMap, mapValues.target, target__0000016a__)
                                        map.put(tradeMap, mapValues.stop, stop__0000016a__)
                                        map.put(tradeMap, mapValues.entry, close)

                                    alert('Bearish Divergence Detected', freq=alert.freq_once_per_bar_close)

                                    bearDiv = True
                                else:
                                    if __hist_finalSrc__[1] > method_call('get_y2', divLine):
                                        method_call('set_xy2', divLine, time[1], __hist_finalSrc__[1])
                                        method_call('set_xy2', priceLine, time[1], __hist_getHigh__[1])
                        else:
                            if not na(divLine):
                                divLine = NA(Line)
                                priceLine = NA(Line)
                                array.push(includesTime, getRecent.indicatorPiv.time)

                if bearHDivShow or bearHDivTrade:
                    if not array.includes(includesTimeHidden, getRecentHidden.indicatorPiv.time):
                        if __hist_finalSrc__[1] > getRecentHidden.indicatorPiv.price and __hist_getHigh__[1] < getRecentHidden.pricePiv.price:
                            if __hist_finalSrc__[1] > __hist_finalSrc__[2] and __hist_finalSrc__[1] > finalSrc:
                                if na(divLineHidden):
                                    divLineHidden = line.new(getRecentHidden.indicatorPiv.time, getRecentHidden.indicatorPiv.price, time[1], __hist_finalSrc__[1], xloc=xloc.bar_time, color=bearHDivCol, style=line.style_dotted, width=2)

                                    priceLineHidden = line.new(getRecentHidden.pricePiv.time, getRecentHidden.pricePiv.price, time[1], __hist_getHigh__[1], xloc=xloc.bar_time, color=bearHDivCol, width=2, style=line.style_dotted, force_overlay=True)

                                    if map.get(tradeMap, mapValues.direction) == 0 and (not na(atr)):
                                        __block_result_11__ = (na, na)
                                        __switch_8__ = exitType
                                        if __switch_8__ == exitInput.atr:
                                            __block_result_11__ = (close + atr * stopLossMult, close - atr * profitTargetMult)
                                        elif __switch_8__ == exitInput.percent:
                                            __block_result_11__ = (close * (1 + stopLossMult / 100), close * (1 - profitTargetMult / 100))
                                        stop__0000019f__, target__0000019f__ = __block_result_11__

                                        stop__0000019f__ = math.round_to_mintick(stop__0000019f__)
                                        target__0000019f__ = math.round_to_mintick(target__0000019f__)

                                        strategy.entry('Short Hidden Bearish Divergence', strategy.short)
                                        strategy.exit('SHB Exit', 'Short Hidden Bearish Divergence', stop=stop__0000019f__, limit=target__0000019f__)

                                        label.new(bar_index, close, text='▽', textcolor=color.rgb(255, 116, 116), color=color.new(color.rgb(255, 116, 116), 80), style=label.style_text_outline, size=size.normal, tooltip='Bearish Hidden Divergence Short Entry At: ' + string.tostring(close, format.mintick) + '\nTarget: ' + string.tostring(target__0000019f__) + '\nStop: ' + string.tostring(stop__0000019f__), force_overlay=True, yloc=yloc.abovebar)

                                        exitData.stopPrice = stop__0000019f__
                                        exitData.targetPrice = target__0000019f__

                                        map.put(tradeMap, mapValues.direction, -1)
                                        map.put(tradeMap, mapValues.target, target__0000019f__)
                                        map.put(tradeMap, mapValues.stop, stop__0000019f__)
                                        map.put(tradeMap, mapValues.entry, close)

                                    alert('Bearish Hidden Divergence Detected', freq=alert.freq_once_per_bar_close)

                                    bearHdiv = True
                                else:
                                    if __hist_finalSrc__[1] > method_call('get_y2', divLineHidden):
                                        method_call('set_xy2', divLineHidden, time[1], __hist_finalSrc__[1])
                                        method_call('set_xy2', priceLineHidden, time[1], __hist_getHigh__[1])
                        else:
                            if not na(divLineHidden):
                                divLineHidden = NA(Line)
                                priceLineHidden = NA(Line)
                                array.push(includesTimeHidden, getRecentHidden.indicatorPiv.time)

            if array.size(pivotsDn) > 1:
                getRecent = array.last(pivotsDn)
                getRecentHidden = array.last(pivotsDnH)

                includesTime: Persistent[list[int]] = array.new_int()
                divLine: Persistent = NA(Line)
                priceLine: Persistent = NA(Line)

                includesTimeHidden: Persistent[list[int]] = array.new_int()
                divLineHidden: Persistent = NA(Line)
                priceLineHidden: Persistent = NA(Line)

                if finalSrc < getRecent.indicatorPiv.price:
                    getLast = array.last(pivotsDn)

                    getLast.indicatorPiv = chart.point.from_time(time, finalSrc)
                    getLast.pricePiv = chart.point.from_time(time, getLow)

                if bullDivShow or bullDivTrade:
                    if not array.includes(includesTime, getRecent.indicatorPiv.time):
                        if __hist_finalSrc__[1] > getRecent.indicatorPiv.price and __hist_getLow__[1] < getRecent.pricePiv.price:
                            if __hist_finalSrc__[1] < __hist_finalSrc__[2] and __hist_finalSrc__[1] < finalSrc:
                                if na(divLine):
                                    divLine = line.new(getRecent.indicatorPiv.time, getRecent.indicatorPiv.price, time[1], __hist_finalSrc__[1], xloc=xloc.bar_time, color=bullDivCol, style=line.style_dotted, width=2)

                                    priceLine = line.new(getRecent.pricePiv.time, getRecent.pricePiv.price, time[1], __hist_getLow__[1], xloc=xloc.bar_time, color=bullDivCol, width=2, style=line.style_dotted, force_overlay=True)

                                    if map.get(tradeMap, mapValues.direction) == 0 and (not na(atr)):
                                        __block_result_12__ = (na, na)
                                        __switch_8__ = exitType
                                        if __switch_8__ == exitInput.atr:
                                            __block_result_12__ = (close - atr * stopLossMult, close + atr * profitTargetMult)
                                        elif __switch_8__ == exitInput.percent:
                                            __block_result_12__ = (close * (1 - stopLossMult / 100), close * (1 + profitTargetMult / 100))
                                        stop__000001dc__, target__000001dc__ = __block_result_12__

                                        stop__000001dc__ = math.round_to_mintick(stop__000001dc__)
                                        target__000001dc__ = math.round_to_mintick(target__000001dc__)

                                        strategy.entry('Long Bullish Divergence', strategy.long)
                                        strategy.exit('LB Exit', 'Long Bullish Divergence', stop=stop__000001dc__, limit=target__000001dc__)

                                        label.new(bar_index, close, text='△', textcolor=color.new('#74FFBC'), color=color.new(color.new('#74FFBC'), 80), style=label.style_text_outline, size=size.normal, tooltip='Bullish Divergence Long Entry At: ' + string.tostring(close, format.mintick) + '\nTarget: ' + string.tostring(target__000001dc__) + '\nStop: ' + string.tostring(stop__000001dc__), force_overlay=True, yloc=yloc.belowbar)

                                        exitData.stopPrice = stop__000001dc__
                                        exitData.targetPrice = target__000001dc__

                                        map.put(tradeMap, mapValues.direction, 1)
                                        map.put(tradeMap, mapValues.target, target__000001dc__)
                                        map.put(tradeMap, mapValues.stop, stop__000001dc__)
                                        map.put(tradeMap, mapValues.entry, close)

                                    bullDiv = True

                                    alert('Bullish Divergence Detected', freq=alert.freq_once_per_bar_close)
                                else:
                                    if __hist_finalSrc__[1] < method_call('get_y2', divLine):
                                        method_call('set_xy2', divLine, time[1], __hist_finalSrc__[1])
                                        method_call('set_xy2', priceLine, time[1], __hist_getLow__[1])
                        else:
                            if not na(divLine):
                                divLine = NA(Line)
                                priceLine = NA(Line)
                                array.push(includesTime, getRecent.indicatorPiv.time)

                if bullHDivShow or bullHDivTrade:
                    if not array.includes(includesTimeHidden, getRecentHidden.indicatorPiv.time):
                        if __hist_finalSrc__[1] < getRecentHidden.indicatorPiv.price and __hist_getLow__[1] > getRecentHidden.pricePiv.price:
                            if __hist_finalSrc__[1] < __hist_finalSrc__[2] and __hist_finalSrc__[1] < finalSrc:
                                if na(divLineHidden):
                                    divLineHidden = line.new(getRecentHidden.indicatorPiv.time, getRecentHidden.indicatorPiv.price, time[1], __hist_finalSrc__[1], xloc=xloc.bar_time, color=bullHDivCol, style=line.style_dotted, width=2)

                                    priceLineHidden = line.new(getRecentHidden.pricePiv.time, getRecentHidden.pricePiv.price, time[1], __hist_getLow__[1], xloc=xloc.bar_time, color=bullHDivCol, width=2, style=line.style_dotted, force_overlay=True)

                                    if map.get(tradeMap, mapValues.direction) == 0 and (not na(atr)):
                                        __block_result_13__ = (na, na)
                                        __switch_8__ = exitType
                                        if __switch_8__ == exitInput.atr:
                                            __block_result_13__ = (close - atr * stopLossMult, close + atr * profitTargetMult)
                                        elif __switch_8__ == exitInput.percent:
                                            __block_result_13__ = (close * (1 - stopLossMult / 100), close * (1 + profitTargetMult / 100))
                                        stop__0000020f__, target__0000020f__ = __block_result_13__

                                        stop__0000020f__ = math.round_to_mintick(stop__0000020f__)
                                        target__0000020f__ = math.round_to_mintick(target__0000020f__)

                                        strategy.entry('Long Hidden Bullish Divergence', strategy.long)
                                        strategy.exit('LHB Exit', 'Long Hidden Bullish Divergence', stop=stop__0000020f__, limit=target__0000020f__)

                                        label.new(bar_index, close, text='△', textcolor=color.new('#74FFBC'), color=color.new(color.new('#74FFBC'), 80), style=label.style_text_outline, size=size.normal, tooltip='Bullish Hidden Divergence Long Entry At: ' + string.tostring(close, format.mintick) + '\nTarget: ' + string.tostring(target__0000020f__) + '\nStop: ' + string.tostring(stop__0000020f__), force_overlay=True, yloc=yloc.belowbar)

                                        exitData.stopPrice = stop__0000020f__
                                        exitData.targetPrice = target__0000020f__

                                        map.put(tradeMap, mapValues.direction, 1)
                                        map.put(tradeMap, mapValues.target, target__0000020f__)
                                        map.put(tradeMap, mapValues.stop, stop__0000020f__)
                                        map.put(tradeMap, mapValues.entry, close)

                                    bullHdiv = True

                                    alert('Bullish Hidden Divergence Detected', freq=alert.freq_once_per_bar_close)
                                else:
                                    if __hist_finalSrc__[1] < method_call('get_y2', divLineHidden):
                                        method_call('set_xy2', divLineHidden, time[1], __hist_finalSrc__[1])
                                        method_call('set_xy2', priceLineHidden, time[1], __hist_getLow__[1])
                        else:
                            if not na(divLineHidden):
                                divLineHidden = NA(Line)
                                priceLineHidden = NA(Line)
                                array.push(includesTimeHidden, getRecentHidden.indicatorPiv.time)

        return (bearDiv, bearHdiv, bullDiv, bullHdiv)

    __block_result_14__ = (na, na, na, na)
    __switch__ = divMethod
    if __switch__ == divInput.pivotPoints:
        __block_result_14__ = pivotsMethod()
    elif __switch__ == divInput.immediate:
        __block_result_14__ = immediateMethod()
    bearDiv, bearHdiv, bullDiv, bullHdiv = __block_result_14__

    if barstate.islast or barstate.islastconfirmedhistory:
        performanceTable: Persistent = table.new(position.bottom_right, 99, 99, bgcolor=color.new('#20222C'), border_color=color.new('#363843'), frame_color=color.new('#363843'), border_width=1, frame_width=1, force_overlay=True)

        __block_result_15__ = na
        __switch_1__ = math.sign(map.get(tradeMap, mapValues.profit))
        if __switch_1__ == 1:
            __block_result_15__ = color.new('#74FFBC')
        elif __switch_1__ == -1:
            __block_result_15__ = color.rgb(255, 116, 116)
        else:
            __block_result_15__ = color.white
        textCol = __block_result_15__

        method_call('cell', performanceTable, 0, 0, 'Divergence IQ', text_color=color.new('#F874FF'))

        method_call('cell', performanceTable, 0, 1, 'Profit: ', text_color=color.white)
        method_call('cell', performanceTable, 0, 2, 'Win Rate: ', text_color=color.white)
        method_call('cell', performanceTable, 0, 3, 'PF: ', text_color=color.white)
        method_call('cell', performanceTable, 0, 4, 'Trades: ', text_color=color.white)

        method_call('cell', performanceTable, 1, 1, string.tostring(map.get(tradeMap, mapValues.profit), format.percent), text_color=textCol)
        method_call('cell', performanceTable, 1, 2, string.tostring(map.get(tradeMap, mapValues.wins) / map.get(tradeMap, mapValues.trades) * 100, format.percent), text_color=color.white)
        method_call('cell', performanceTable, 1, 3, string.tostring(map.get(tradeMap, mapValues.grossGain) / map.get(tradeMap, mapValues.grossLoss), '###,###.##'), text_color=textCol)
        method_call('cell', performanceTable, 1, 4, string.tostring(map.get(tradeMap, mapValues.trades), '###,###.##'), text_color=textCol)

        method_call('merge_cells', performanceTable, 0, 0, 1, 0)

        pricesArr = array.from_items(close, high, low, open, hl2, hlc3, ohlc4, hlcc4)

        if method_call('includes', pricesArr, src):
            warningTable: Persistent = table.new(position.bottom_right, 99, 99, bgcolor=color.new('#20222C'), border_color=color.new('#363843'), frame_color=color.new('#363843'), border_width=1, frame_width=1)

            method_call('cell', warningTable, 0, 0, 'In The Divergence IQ Settings, Please Add An Indicator To Calculate Divergences On.\nThe Indicator Must Be On The Chart', text_color=color.white)

    plot(finalSrc if showFinal or normMethod != normalizationInput.none else na, color=gradientFlowCol)
    plot(finalSrc if showFinal or normMethod != normalizationInput.none else na, color=color.new(gradientFlowCol, 80), linewidth=5)

    showCond: Persistent = divMethod == divInput.pivotPoints

    plot(finalSrc[rightLook] if showCond and (not na(getPH)) else na, offset=-rightLook, color=bearDivCol if bearDiv else na, display=display.pane)
    plot(finalSrc[rightLook] if showCond and (not na(getPH)) else na, offset=-rightLook, color=color.new(bearDivCol, 80) if bearDiv else na, linewidth=5, display=display.pane)

    plot(finalSrc[rightLook] if showCond and (not na(getPH)) else na, offset=-rightLook, color=bearHDivCol if bearHdiv else na, display=display.pane)
    plot(finalSrc[rightLook] if showCond and (not na(getPH)) else na, offset=-rightLook, color=color.new(bearHDivCol, 80) if bearHdiv else na, linewidth=5, display=display.pane)

    plot(finalSrc[rightLook] if showCond and (not na(getPL)) else na, offset=-rightLook, color=bullDivCol if bullDiv else na, display=display.pane)
    plot(finalSrc[rightLook] if showCond and (not na(getPL)) else na, offset=-rightLook, color=color.new(bullDivCol, 80) if bullDiv else na, linewidth=5, display=display.pane)

    plot(finalSrc[rightLook] if showCond and (not na(getPL)) else na, offset=-rightLook, color=bullHDivCol if bullHdiv else na, display=display.pane)
    plot(finalSrc[rightLook] if showCond and (not na(getPL)) else na, offset=-rightLook, color=color.new(bullHDivCol, 80) if bullHdiv else na, linewidth=5, display=display.pane)

    plot(getHigh[rightLook] if showCond and (not na(getPH)) and onChart else na, offset=-rightLook, color=bearDivCol if bearDiv else na, display=display.pane, force_overlay=True)
    plot(getHigh[rightLook] if showCond and (not na(getPH)) and onChart else na, offset=-rightLook, color=color.new(bearDivCol, 80) if bearDiv else na, linewidth=5, display=display.pane, force_overlay=True)

    plot(getHigh[rightLook] if showCond and (not na(getPH)) and onChart else na, offset=-rightLook, color=bearHDivCol if bearHdiv else na, display=display.pane, force_overlay=True)
    plot(getHigh[rightLook] if showCond and (not na(getPH)) and onChart else na, offset=-rightLook, color=color.new(bearHDivCol, 80) if bearHdiv else na, linewidth=5, display=display.pane, force_overlay=True)

    plot(getLow[rightLook] if showCond and (not na(getPL)) and onChart else na, offset=-rightLook, color=bullDivCol if bullDiv else na, display=display.pane, force_overlay=True)
    plot(getLow[rightLook] if showCond and (not na(getPL)) and onChart else na, offset=-rightLook, color=color.new(bullDivCol, 80) if bullDiv else na, linewidth=5, display=display.pane, force_overlay=True)

    plot(getLow[rightLook] if showCond and (not na(getPL)) and onChart else na, offset=-rightLook, color=bullHDivCol if bullHdiv else na, display=display.pane, force_overlay=True)
    plot(getLow[rightLook] if showCond and (not na(getPL)) and onChart else na, offset=-rightLook, color=color.new(bullHDivCol, 80) if bullHdiv else na, linewidth=5, display=display.pane, force_overlay=True)

    plot(close if showPrice else na, color=gradientFlowCol, force_overlay=True)
    plot(close if showPrice else na, color=color.new(gradientFlowCol, 80), linewidth=5, force_overlay=True)

    targetCol: Persistent[Color] = color.new('#74FFBC')
    stopCol: Persistent = color.rgb(255, 116, 116)

    target = plot(exitData.targetPrice, force_overlay=True, style=plot.style_linebr, offset=1, color=targetCol)
    stop = plot(exitData.stopPrice, force_overlay=True, style=plot.style_linebr, offset=1, color=stopCol)

    plot(exitData.targetPrice, force_overlay=True, style=plot.style_linebr, offset=1, color=color.new(targetCol, 80), linewidth=5)
    plot(exitData.stopPrice, force_overlay=True, style=plot.style_linebr, offset=1, color=color.new(stopCol, 80), linewidth=5)

    getAvg = math.avg(exitData.targetPrice, exitData.stopPrice)

    avg = plot(getAvg, display=display.none, force_overlay=True, offset=1)

    getDir = math.sign(exitData.targetPrice - getAvg)

    __block_result_16__ = (na, na, na, na)
    __switch__ = getDir
    if __switch__ == 1:
        __block_result_16__ = (color.new(targetCol, 90), color.new(targetCol, 99), color.new(stopCol, 99), color.new(stopCol, 90))
    else:
        __block_result_16__ = (color.new(targetCol, 99), color.new(targetCol, 90), color.new(stopCol, 99), color.new(stopCol, 90))
    topCol, botCol, topColStop, botColStop = __block_result_16__

    fill(target, avg, top_value=math.max(exitData.targetPrice, getAvg), bottom_value=math.min(exitData.targetPrice, getAvg), top_color=topCol, bottom_color=botCol)

    fill(stop, avg, top_value=math.max(exitData.stopPrice, getAvg), bottom_value=math.min(exitData.stopPrice, getAvg), top_color=topColStop, bottom_color=botColStop)

    highest = ta.ema(ta.highest(finalSrc, 500), 500)
    lowest = ta.ema(ta.lowest(finalSrc, 500), 500)
    priceAvg = math.avg(highest, lowest)

    p1 = plot(highest if gradientFlow else na, display=display.none)
    p2 = plot(lowest if gradientFlow else na, display=display.none)
    p3 = plot(priceAvg if gradientFlow else na, display=display.none)

    fill(p1, p3, top_value=highest, bottom_value=priceAvg, bottom_color=color.new(gradientFlowCol, 90), top_color=color.new(gradientFlowCol, 99))
    fill(p2, p3, top_value=priceAvg, bottom_value=lowest, bottom_color=color.new(gradientFlowCol, 99), top_color=color.new(gradientFlowCol, 90))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
