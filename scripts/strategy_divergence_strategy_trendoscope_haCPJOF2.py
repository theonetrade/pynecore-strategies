"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from enum import StrEnum as Enum
from pynecore import pine_loop
from pynecore.core.overload import overload
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, chart, close, color, display, extend, high, input,
    label, line, log, low, map, math, matrix, na, plot, script, size, strategy, string, ta, xloc,
    yloc
)
from pynecore.types import Color, Matrix, NA, Persistent, Series
from pynecore.types.chart import ChartPoint
import lib.HeWhoMustNotBeNamed.strategy.v5 as st
import lib.Trendoscope.Drawing.v4 as dr
import lib.Trendoscope.Zigzag.v11 as zg
import lib.Trendoscope.oota.v1 as eta


class TradeDirection(Enum):
    Long = 'Long'
    Short = 'Short'


class TradeDivergence(Enum):
    Regular = 'Regular'
    Hidden = 'Hidden'
    Both = 'Both'


class EntryType(Enum):
    Cautious = 'Cautious'
    Confident = 'Confident'
    Mixed = 'Mixed'


class DivergenceType(Enum):
    BullishDivergence = 'Bullish Divergence'
    BearishDivergence = 'Bearish Divergence'
    BullishHiddenDivergence = 'Bullish Hidden Divergence'
    BearishHiddenDivergence = 'Bearish Hidden Divergence'
    None__ren__ = 'None'


@udt
class TradeDrawing:
    targetBox: dr.Box__ren__ = na(dr.Box__ren__)
    stopBox: dr.Box__ren__ = na(dr.Box__ren__)
    progressBox: dr.Box__ren__ = na(dr.Box__ren__)


@udt
class DivergenceObject:
    id: int = na(int)
    priceLine: dr.Line__ren__ = na(dr.Line__ren__)
    oscillatorLine: dr.Line__ren__ = na(dr.Line__ren__)
    priceLabel: dr.Label__ren__ = na(dr.Label__ren__)
    oscillatorLabel: dr.Label__ren__ = na(dr.Label__ren__)
    pricePoint: ChartPoint = na(ChartPoint)
    pivotPoint: ChartPoint = na(ChartPoint)
    lastPoint: ChartPoint = na(ChartPoint)
    divergenceType: DivergenceType = na(DivergenceType)
    trade: 'TradeDrawing' = _dataclass_field(default_factory=lambda: na(TradeDrawing))
    broken: bool = False


@udt
class ZigzagProperties:
    textColor: Color = _dataclass_field(default_factory=lambda: color.black)
    trendMethod: int = 1
    repaint: bool = False


class PivotDirection(Enum):
    HH = 'Higher High'
    LH = 'Lower High'
    HL = 'Higher Low'
    LL = 'Lower Low'


trendTypeTooltip = 'Choose how trends are identified:\n' + '\tZigzag - HH, HL on the starting pivot of divergence line is considered as uptrend and LL, LH on the starting pivot of divergence line is considered as downtrend\n' + '\tMA Difference - Difference between moving average of divergence line pivot will define the trend\n' + '\tExternal - Use External Oscillator Input'


@script.strategy('Divergence Strategy [Trendoscope®]', 'DStr1.1[Trendoscope®]', overlay=False, max_lines_count=500, max_labels_count=500, max_polylines_count=100, calc_bars_count=5000, dynamic_requests=True, initial_capital=1000000, default_qty_type=strategy.percent_of_equity, default_qty_value=20, commission_type=strategy.commission.percent, pyramiding=4, commission_value=0.1, explicit_plot_zorder=True, margin_long=100.0, margin_short=100.0, max_bars_back=5000)
def main(
    tradeDirection=input.enum(TradeDirection.Long, 'Direction', tooltip='Choose to trade only long or short positions. Simultaneous long and short trades are disabled to avoid conflicts.', group='Trade', display=display.none),
    tradeDivergence=input.enum(TradeDivergence.Both, 'Divergence', tooltip='Select to trade regular divergences (reversals), hidden divergences (continuations), or both.', group='Trade', display=display.none),
    entryType=input.enum(EntryType.Cautious, 'Entry/Exit Type', tooltip='Cautious: Conservative entry, quick exit. \nConfident: Aggressive entry, delayed exit. \nMixed: Conservative entry, delayed exit.', group='Trade', display=display.none),
    riskReward=input.float(2.0, 'Risk/Reward', tooltip='Define the profit target as a multiple of the risk (stop-loss distance) for each trade.', group='Trade', display=display.none),
    marketEntry=input.bool(False, 'Use Market Order', tooltip='Enable to execute trades at the current market price; disable for stop orders at specific price levels.', group='Trade', display=display.none),
    cancelPendingOrders=input.bool(True, 'Cancel On Break', tooltip='If enabled, pending orders are canceled when price moves against the divergence. If disabled, orders remain active until entry is triggered', group='Trade', display=display.none),
    oscillatorType=input.string('rsi', 'Oscillator', options=('rsi', 'cci', 'cmo', 'cog', 'mfi', 'roc', 'stoch', 'wpr'), inline='osc', group='Oscillator', display=display.none),
    length=input.int(14, '', group='Oscillator', inline='osc', tooltip='Select the oscillator type and period, or use an external oscillator for divergence calculations.', display=display.none),
    useExternalOscillator=input.bool(False, 'Use External Oscillator', inline='eosc', group='Oscillator', display=display.none),
    externalOscillator: Series[float] = input.source(close, '', tooltip='Use external oscillator instead of the built ins', inline='eosc', group='Oscillator', display=display.none),
    trendMethod=input.string('Zigzag', 'Trend Detection Method', options=('Zigzag', 'MA Difference', 'External'), group='Trend', display=display.none, tooltip=trendTypeTooltip),
    maType=input.enum(eta.CustomSeries.SMA, 'MA Filter', inline='ma', group='Trend', display=display.none),
    maLength=input.int(200, '', minval=5, step=50, inline='ma', group='Trend', display=display.none, tooltip='Moving Average to identify trend. Direction of moving average between the divergence pivots identify trend'),
    externalTrendSignal: Series[float] = input.source(close, 'External Trend Signal', tooltip='Use External trend signal instead of the built in. The external indicator should return positive value for uptrend and negative value for downtrend', group='Trend', display=display.none),
    zigzagLength=input.int(13, 'Length', group='Zigzag', tooltip='Set the zigzag length to adjust pivot detection sensitivity for divergence signals.', display=display.none)
):
    def oscillator(type: str = 'rsi', length: int = 14, source: float = close, highSource: float = high, lowSource: float = low):
        __block_result__ = na
        __switch__ = type
        if __switch__ == 'cci':
            __block_result__ = ta.cci(source, length)
        elif __switch__ == 'cmo':
            __block_result__ = ta.cmo(source, length)
        elif __switch__ == 'cog':
            __block_result__ = ta.cog(source, length)
        elif __switch__ == 'mfi':
            __block_result__ = ta.mfi(source, length)
        elif __switch__ == 'roc':
            __block_result__ = ta.roc(source, length)
        elif __switch__ == 'rsi':
            __block_result__ = ta.rsi(source, length)
        elif __switch__ == 'stoch':
            __block_result__ = ta.stoch(source, highSource, lowSource, length)
        elif __switch__ == 'wpr':
            __block_result__ = ta.wpr(length)
        else:
            __block_result__ = ta.rsi(source, length)
        oscillator__00000014__ = __block_result__
        return oscillator__00000014__



    rsiColor = color.blue

    repaint: bool = True
    textColor: Color = chart.bg_color

    trendMethodInt = 1 if trendMethod == 'Zigzag' else 3 if trendMethod == 'External' else 2
    priceMap: Persistent[dict[int, float]] = map.new()
    oscillatorMap: Persistent[dict[int, float]] = map.new()
    map.put(priceMap, bar_index, close)



    @overload
    @method
    def delete(this: TradeDrawing):
        method_call('delete', this.targetBox)
        return method_call('delete', this.stopBox)

    @overload
    @method
    def draw(this: TradeDrawing):
        method_call('draw', this.targetBox)
        return method_call('draw', this.stopBox)

    @overload
    @method
    def delete(this: DivergenceObject):
        method_call('delete', this.priceLine)
        method_call('delete', this.oscillatorLine)
        method_call('delete', this.priceLabel)
        method_call('delete', this.oscillatorLabel)
        if not na(this.trade):
            delete(this.trade)
        return this

    @overload
    @method
    def draw(this: DivergenceObject):
        delete(this)
        method_call('draw', this.priceLine)
        method_call('draw', this.oscillatorLine)
        method_call('draw', this.priceLabel)
        method_call('draw', this.oscillatorLabel)
        if not na(this.trade):
            draw(this.trade)
        return this



    def getDivergenceType(direction, divergence__00000046__):
        return (DivergenceType.BearishDivergence if divergence__00000046__ > 0 else DivergenceType.BearishHiddenDivergence) if direction > 0 else DivergenceType.BullishDivergence if divergence__00000046__ > 0 else DivergenceType.BullishHiddenDivergence

    def getPivotDirection(dir, ratio):
        return (PivotDirection.HH if ratio > 1 else PivotDirection.LH) if dir > 0 else PivotDirection.LL if ratio > 1 else PivotDirection.HL

    def getLinePropertiesMap(force_overlay: bool = False):
        linePropertiesMap: dict[DivergenceType, dr.LineProperties] = map.new()
        map.put(linePropertiesMap, DivergenceType.BullishDivergence, dr.LineProperties.new(xloc.bar_time, extend.none, color.green, line.style_solid, 1, force_overlay))
        map.put(linePropertiesMap, DivergenceType.BearishDivergence, dr.LineProperties.new(xloc.bar_time, extend.none, color.red, line.style_solid, 1, force_overlay))
        map.put(linePropertiesMap, DivergenceType.BullishHiddenDivergence, dr.LineProperties.new(xloc.bar_time, extend.none, color.lime, line.style_solid, 1, force_overlay))
        map.put(linePropertiesMap, DivergenceType.BearishHiddenDivergence, dr.LineProperties.new(xloc.bar_time, extend.none, color.orange, line.style_solid, 1, force_overlay))
        return linePropertiesMap

    def getLabelPropertiesMap(force_overlay: bool = False):
        labelPropertiesMap: dict[DivergenceType, dr.LabelProperties] = map.new()
        map.put(labelPropertiesMap, DivergenceType.BullishDivergence, dr.LabelProperties.new(xloc.bar_time, yloc.price, color.green, label.style_label_up, chart.bg_color, size.small, force_overlay=force_overlay))
        map.put(labelPropertiesMap, DivergenceType.BearishDivergence, dr.LabelProperties.new(xloc.bar_time, yloc.price, color.red, label.style_label_down, chart.bg_color, size.small, force_overlay=force_overlay))
        map.put(labelPropertiesMap, DivergenceType.BullishHiddenDivergence, dr.LabelProperties.new(xloc.bar_time, yloc.price, color.lime, label.style_label_up, chart.bg_color, size.small, force_overlay=force_overlay))
        map.put(labelPropertiesMap, DivergenceType.BearishHiddenDivergence, dr.LabelProperties.new(xloc.bar_time, yloc.price, color.orange, label.style_label_down, chart.bg_color, size.small, force_overlay=force_overlay))
        return labelPropertiesMap

    def getDeniedDivergenceTypes(direction: TradeDirection = TradeDirection.Long, divergence__00000069__: TradeDivergence = TradeDivergence.Both):
        denyTrading: list[DivergenceType] = array.new(0, NA(DivergenceType))
        if direction == TradeDirection.Long:
            array.push(denyTrading, DivergenceType.BearishDivergence)
            array.push(denyTrading, DivergenceType.BearishHiddenDivergence)
        if direction == TradeDirection.Short:
            array.push(denyTrading, DivergenceType.BullishDivergence)
            array.push(denyTrading, DivergenceType.BullishHiddenDivergence)
        if divergence__00000069__ == TradeDivergence.Regular:
            array.push(denyTrading, DivergenceType.BullishHiddenDivergence)
            array.push(denyTrading, DivergenceType.BearishHiddenDivergence)
        if divergence__00000069__ == TradeDivergence.Hidden:
            array.push(denyTrading, DivergenceType.BullishDivergence)
            array.push(denyTrading, DivergenceType.BearishDivergence)
        return denyTrading

    denyTrading: list[DivergenceType] = getDeniedDivergenceTypes(tradeDirection, tradeDivergence)

    priceLinePropertiesMap: dict[DivergenceType, dr.LineProperties] = getLinePropertiesMap(True)
    oscillatorLinePropertiesMap: dict[DivergenceType, dr.LineProperties] = getLinePropertiesMap()

    priceLabelPropertiesMap: dict[DivergenceType, dr.LabelProperties] = getLabelPropertiesMap(True)
    oscillatorLabelPropertiesMap: dict[DivergenceType, dr.LabelProperties] = getLabelPropertiesMap()

    @method
    def createTradeDrawing(object: DivergenceObject, entry: float, stop: float, target: float, marketEntry: bool):
        newEntry = close if marketEntry else entry
        entryPoint = chart.point.now(newEntry)
        stopPoint = chart.point.from_index(bar_index + 10, stop)
        targetPoint = chart.point.from_index(bar_index + 10, target)
        targetProps: dr.BoxProperties = dr.BoxProperties.new(color.blue, color.new(color.lime, 80), 0, line.style_dotted, extend.none, xloc.bar_index, True)
        stopProps: dr.BoxProperties = dr.BoxProperties.new(color.blue, color.new(color.orange, 80), 0, line.style_dotted, extend.none, xloc.bar_index, True)
        object.trade = TradeDrawing(dr.Box__ren__.new(entryPoint, targetPoint, targetProps), dr.Box__ren__.new(entryPoint, stopPoint, stopProps))
        return object.trade

    @method
    def trade(object: DivergenceObject, denyTrading: list[DivergenceType], entryType: EntryType, marketEntry: bool, riskReward: float = 2.0):
        if not array.includes(denyTrading, object.divergenceType):
            if object.divergenceType == DivergenceType.BullishHiddenDivergence or object.divergenceType == DivergenceType.BearishHiddenDivergence:
                log.info('{0} Pivots : [{1}, {2}, {3}], Bars : [{4}, {5}, {6}]', object.id, object.pricePoint.price, object.pivotPoint.price, object.lastPoint.price, object.pricePoint.index, object.pivotPoint.index, object.lastPoint.index)
                entry = object.pivotPoint.price
                exit = object.pricePoint.price if entryType == EntryType.Cautious and (not marketEntry) else object.lastPoint.price
                target = entry + riskReward * (entry - exit)
                st.bracketOrderWithoutLeverage(string.tostring(object.id), entry, exit, target, marketEntry)
                createTradeDrawing(object, entry, exit, target, marketEntry)
            if object.divergenceType == DivergenceType.BullishDivergence or object.divergenceType == DivergenceType.BearishDivergence:
                entry = object.lastPoint.price if entryType == EntryType.Confident else object.pivotPoint.price
                exit = object.lastPoint.price if entryType == EntryType.Cautious or marketEntry else object.pricePoint.price
                target = entry + riskReward * (entry - exit)
                st.bracketOrderWithoutLeverage(string.tostring(object.id), entry, exit, target, marketEntry)
                createTradeDrawing(object, entry, exit, target, marketEntry)
        return object

    @method
    def cancelTrade(object: DivergenceObject):
        __block_result_1__ = na
        if cancelPendingOrders:
            strategy.close(string.tostring(object.id))
            __block_result_1__ = strategy.cancel(string.tostring(object.id))
        return __block_result_1__

    @method
    def divergence(this: zg.Zigzag, divergenceObjects: list[DivergenceObject], properties: ZigzagProperties):
        startIndex = 0 if properties.repaint else 1
        divergenceType: DivergenceType = DivergenceType.None__ren__
        if method_call('size', this.zigzagPivots) > 2 + startIndex:
            lastPivot = method_call('get', this.zigzagPivots, startIndex)
            oppositePivot = method_call('get', this.zigzagPivots, startIndex + 1)
            llastPivot = method_call('get', this.zigzagPivots, startIndex + 2)
            skip: bool = False
            if this.flags.updateLastPivot:
                if array.size(divergenceObjects) > 0:
                    lastDivergence = array.last(divergenceObjects)
                    divergenceStartBar = lastDivergence.priceLine.start.index
                    llastPivotBar = llastPivot.point.index

                    divergenceEndBar = lastDivergence.priceLine.end.index
                    lastPivotBar = lastPivot.point.index
                    if llastPivotBar == divergenceStartBar and lastPivotBar > divergenceEndBar:
                        method_call(cancelTrade, method_call(delete, array.pop(divergenceObjects)))
                    skip = llastPivotBar == divergenceStartBar and lastPivotBar == divergenceEndBar

            if this.flags.newPivot and (not skip):
                dir = math.sign(lastPivot.dir)
                lastOsc = lastPivot.point.price
                lastPrice = method_call('get', lastPivot.indicatorValues, 0)
                oscRatio = lastPivot.ratio
                priceRatio = method_call('get', lastPivot.indicatorRatios, 0)

                priceDirection = getPivotDirection(lastPivot.dir, priceRatio)
                oscillatorDirection = getPivotDirection(lastPivot.dir, oscRatio)

                lastTrend = method_call('get', lastPivot.indicatorValues, 2)
                lastMa = method_call('get', lastPivot.indicatorValues, 1)

                pricePoint__000000ce__ = chart.point.new(lastPivot.point.time, lastPivot.point.index, lastPrice)
                oscillatorPoint = chart.point.new(lastPivot.point.time, lastPivot.point.index, lastPivot.point.price)

                if priceDirection != oscillatorDirection and method_call('size', llastPivot.indicatorRatios) > 0:
                    midPrice = method_call('get', oppositePivot.indicatorValues, 0)
                    llastPrice = method_call('get', llastPivot.indicatorValues, 0)
                    llastRatio = method_call('get', llastPivot.indicatorRatios, 0)
                    llastMa = method_call('get', llastPivot.indicatorValues, 1)
                    lastPricePoint = chart.point.new(llastPivot.point.time, llastPivot.point.index, llastPrice)
                    pivotPoint__000000cd__ = chart.point.new(oppositePivot.point.time, oppositePivot.point.index, midPrice)
                    llastOscillatorPoint = chart.point.new(llastPivot.point.time, llastPivot.point.index, llastPivot.point.price)

                    sentiment = math.sign(oscRatio - priceRatio)
                    trend = math.sign(lastTrend) if properties.trendMethod == 3 else math.sign(dir * (llastRatio - 1)) if properties.trendMethod == 1 else math.sign(llastMa - lastMa)
                    divergence__000000cd__ = 1 if trend == dir and sentiment < 0 else -1 if trend != dir and sentiment > 0 else 0
                    if divergence__000000cd__ != 0:
                        divergenceType = getDivergenceType(dir, divergence__000000cd__)
                        priceDivergenceLine: dr.Line__ren__ = dr.Line__ren__.new(lastPricePoint, pricePoint__000000ce__, map.get(priceLinePropertiesMap, divergenceType))
                        oscillatorDivergenceLine: dr.Line__ren__ = dr.Line__ren__.new(llastOscillatorPoint, oscillatorPoint, map.get(oscillatorLinePropertiesMap, divergenceType))

                        validDivergence: bool = True
                        __loop_4__ = pine_loop(lastPricePoint.index + 1, 1)
                        while __loop_4__.step(pricePoint__000000ce__.index - 1):
                            bar = __loop_4__.value
                            priceAtBar = map.get(priceMap, bar)
                            oscillatorAtBar = map.get(oscillatorMap, bar)
                            if priceAtBar * dir > method_call('get_price', priceDivergenceLine, bar) * dir or oscillatorAtBar * dir > method_call('get_price', oscillatorDivergenceLine, bar) * dir:
                                validDivergence = False
                                break

                        if validDivergence:
                            id: Persistent[int] = 0
                            priceLabelText = ('D' if divergenceType == DivergenceType.BullishDivergence or divergenceType == DivergenceType.BearishDivergence else 'H') + ' : ' + string.tostring(id)
                            priceTooltipText = string.tostring(divergenceType) + ' ' + string.tostring(id) + '\nPrice : ' + string.tostring(lastPrice) + ' ( ' + string.tostring(priceRatio) + ' ) - ' + string.tostring(priceDirection) + '\n' + 'Oscillator :' + string.tostring(lastMa) + ' ( ' + string.tostring(oscRatio) + ' ) - ' + string.tostring(oscillatorDirection)
                            priceDivergenceLabel: dr.Label__ren__ = dr.Label__ren__.new(pricePoint__000000ce__, priceLabelText, priceTooltipText, map.get(priceLabelPropertiesMap, divergenceType))
                            oscillatorDivergenceLabel: dr.Label__ren__ = dr.Label__ren__.new(oscillatorPoint, priceLabelText, priceTooltipText, map.get(oscillatorLabelPropertiesMap, divergenceType))
                            divergenceObject: DivergenceObject = DivergenceObject(id, priceDivergenceLine, oscillatorDivergenceLine, priceDivergenceLabel, oscillatorDivergenceLabel, pricePoint__000000ce__, pivotPoint__000000cd__, lastPricePoint, divergenceType)
                            id += 1
                            trade(divergenceObject, denyTrading, entryType, marketEntry, riskReward)
                            array.push(divergenceObjects, draw(divergenceObject))
                        else:
                            method_call('delete', priceDivergenceLine)
        return divergenceType

    ma = method_call('ma', maType, maLength)
    oscillator__global__ = externalOscillator if useExternalOscillator else oscillator(oscillatorType, length)
    plot(oscillator__global__, 'Oscillator')

    map.put(oscillatorMap, bar_index, oscillator__global__)
    indicators: Matrix[float] = matrix.new(initial_value=NA(float))
    indicatorNames: list[str] = array.from_items('Price', string.tostring(maType) + '-' + string.tostring(maLength), 'External Trend')

    matrix.add_row(indicators, 0, array.from_items(close, close, close))
    matrix.add_row(indicators, 1, array.from_items(ma, ma, ma))
    matrix.add_row(indicators, 2, array.from_items(externalTrendSignal, externalTrendSignal, externalTrendSignal))

    zigzag: Persistent[zg.Zigzag] = zg.Zigzag.new(zigzagLength, 300, 0)
    properties: Persistent[ZigzagProperties] = ZigzagProperties(textColor, trendMethodInt, repaint)
    divergenceObjects: Persistent[list[DivergenceObject]] = array.new(0, NA(DivergenceObject))
    method_call('calculate', zigzag, array.from_items(oscillator__global__), indicators, indicatorNames)
    currentDivergence = divergence(zigzag, divergenceObjects, properties)

    for divergence__000000e7__ in divergenceObjects:
        direction = 1 if divergence__000000e7__.divergenceType == DivergenceType.BullishDivergence or divergence__000000e7__.divergenceType == DivergenceType.BullishHiddenDivergence else -1
        if not divergence__000000e7__.broken and divergence__000000e7__.pricePoint.price * direction > close * direction:
            divergence__000000e7__.broken = True
            cancelTrade(divergence__000000e7__)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
