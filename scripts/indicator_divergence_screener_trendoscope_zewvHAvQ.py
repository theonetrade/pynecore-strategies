"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from enum import StrEnum as Enum
from pynecore import pine_loop
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, array, bar_index, chart, close, color, display, extend, high,
    input, label, line, low, map, math, matrix, na, plot, script, size, string, ta, xloc, yloc
)
from pynecore.types import Color, Matrix, NA, Persistent, Series
from pynecore.types.chart import ChartPoint
import lib.Trendoscope.Drawing.v3 as dr
import lib.Trendoscope.Zigzag.v11 as zg
import lib.Trendoscope.oota.v1 as eta


class DivergenceType(Enum):
    BullishDivergence = 'Bullish Divergence'
    BearishDivergence = 'Bearish Divergence'
    BullishHiddenDivergence = 'Bullish Hidden Divergence'
    BearishHiddenDivergence = 'Bearish Hidden Divergence'
    None__ren__ = 'None'


@udt
class DivergenceObject:
    priceLine: dr.Line__ren__ = na(dr.Line__ren__)
    oscillatorLine: dr.Line__ren__ = na(dr.Line__ren__)
    priceLabel: dr.Label__ren__ = na(dr.Label__ren__)
    oscillatorLabel: dr.Label__ren__ = na(dr.Label__ren__)
    pricePoint: ChartPoint = na(ChartPoint)
    divergenceType: DivergenceType = na(DivergenceType)
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


trendTypeTooltip = 'Method to identify trend. \n' + '\tZigzag - HH, HL on the starting pivot of divergence line is considered as uptrend and LL, LH on the starting pivot of divergence line is considered as downtrend\n' + '\tMA Difference - Difference between moving average of divergence line pivot will define the trend\n' + '\tExternal - Use External Oscillator Input'


@script.indicator('Divergence Screener [Trendoscope®]', 'DS1.1[Trendoscope®]', overlay=False, max_lines_count=500, max_labels_count=500, max_polylines_count=100, calc_bars_count=500)
def main(
    oscillatorType=input.string('rsi', 'Oscillator', options=('rsi', 'cci', 'cmo', 'cog', 'mfi', 'roc', 'stoch', 'wpr'), inline='osc', group='Oscillator', display=display.none),
    length=input.int(14, '', group='Oscillator', inline='osc', tooltip='Built in Oscillator Type and Length', display=display.none),
    useExternalOscillator=input.bool(False, 'Use External Oscillator', inline='eosc', group='Oscillator', display=display.none),
    externalOscillator: Series[float] = input.source(close, '', tooltip='Use external oscillator instead of the built ins', inline='eosc', group='Oscillator', display=display.none),
    trendMethod=input.string('Zigzag', 'Trend Detection Method', options=('Zigzag', 'MA Difference', 'External'), group='Trend', display=display.none, tooltip=trendTypeTooltip),
    maType=input.enum(eta.CustomSeries.SMA, 'MA Filter', inline='ma', group='Trend', display=display.none),
    maLength=input.int(200, '', minval=5, step=50, inline='ma', group='Trend', display=display.none, tooltip='Moving Average to identify trend. Direction of moving average between the divergence pivots identify trend'),
    externalTrendSignal: Series[float] = input.source(close, 'External Trend Signal', tooltip='Use External trend signal instead of the built in. The external indicator should return positive value for uptrend and negative value for downtrend', group='Trend', display=display.none),
    zigzagLength=input.int(13, 'Length', group='Zigzag', tooltip='Zigzag Length', display=display.none),
    repaint=input.bool(True, 'Repaint', tooltip='If selected, divergence lines repaint as per the latest info. ' + 'If repaint is disabled, then the divergence is calculated based on confirmed pivots only. ' + 'Hence, the signals will be delayed till the pivot is confirmed.', group='Miscellaneous', display=display.none),
    bullishDivergenceAlert=input.bool(True, 'Bullish Divergence', tooltip='Alert on bullish divergence', group='Alerts', display=display.none),
    bullishHiddenDivergenceAlert=input.bool(True, 'Bullish Hidden Divergence', tooltip='Alert on bullish hidden divergence', group='Alerts', display=display.none),
    bearishDivergenceAlert=input.bool(True, 'Bearish Divergence', tooltip='Alert on bearish divergence', group='Alerts', display=display.none),
    bearishHiddenDivergenceAlert=input.bool(True, 'Bearish Hidden Divergence', tooltip='Alert on bearish hidden divergence', group='Alerts', display=display.none)
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

    textColor: Color = chart.bg_color

    trendMethodInt = 1 if trendMethod == 'Zigzag' else 3 if trendMethod == 'External' else 2
    priceMap: Persistent[dict[int, float]] = map.new()
    oscillatorMap: Persistent[dict[int, float]] = map.new()
    map.put(priceMap, bar_index, close)


    @method
    def delete(this: DivergenceObject):
        method_call('delete', this.priceLine)
        method_call('delete', this.oscillatorLine)
        method_call('delete', this.priceLabel)
        method_call('delete', this.oscillatorLabel)
        return this

    @method
    def draw(this: DivergenceObject):
        delete(this)
        method_call('draw', this.priceLine)
        method_call('draw', this.oscillatorLine)
        method_call('draw', this.priceLabel)
        method_call('draw', this.oscillatorLabel)
        return this



    def getDivergenceType(direction, divergence__00000035__):
        return (DivergenceType.BearishDivergence if divergence__00000035__ > 0 else DivergenceType.BearishHiddenDivergence) if direction > 0 else DivergenceType.BullishDivergence if divergence__00000035__ > 0 else DivergenceType.BullishHiddenDivergence

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

    def getAllowedDivergenceTypes():
        allowedDivergenceTypes: dict[DivergenceType, bool] = map.new()
        map.put(allowedDivergenceTypes, DivergenceType.BullishDivergence, bullishDivergenceAlert)
        map.put(allowedDivergenceTypes, DivergenceType.BullishHiddenDivergence, bullishHiddenDivergenceAlert)
        map.put(allowedDivergenceTypes, DivergenceType.BearishDivergence, bearishDivergenceAlert)
        map.put(allowedDivergenceTypes, DivergenceType.BearishHiddenDivergence, bearishHiddenDivergenceAlert)
        return allowedDivergenceTypes

    allowedDivergenceTypes: dict[DivergenceType, bool] = getAllowedDivergenceTypes()

    priceLinePropertiesMap: dict[DivergenceType, dr.LineProperties] = getLinePropertiesMap(True)
    oscillatorLinePropertiesMap: dict[DivergenceType, dr.LineProperties] = getLinePropertiesMap()

    priceLabelPropertiesMap: dict[DivergenceType, dr.LabelProperties] = getLabelPropertiesMap(True)
    oscillatorLabelPropertiesMap: dict[DivergenceType, dr.LabelProperties] = getLabelPropertiesMap()

    @method
    def divergence(this: zg.Zigzag, divergenceObjects: list[DivergenceObject], properties: ZigzagProperties):
        startIndex = 0 if properties.repaint else 1
        divergenceType: DivergenceType = DivergenceType.None__ren__
        if method_call('size', this.zigzagPivots) > 2 + startIndex:
            lastPivot = method_call('get', this.zigzagPivots, startIndex)
            llastPivot = method_call('get', this.zigzagPivots, startIndex + 2)
            skip: bool = False
            if this.flags.updateLastPivot:
                if array.size(divergenceObjects) > 0:
                    lastDivergence__0000005e__ = array.last(divergenceObjects)
                    divergenceStartBar = lastDivergence__0000005e__.priceLine.start.index
                    llastPivotBar = llastPivot.point.index

                    divergenceEndBar = lastDivergence__0000005e__.priceLine.end.index
                    lastPivotBar = lastPivot.point.index
                    if llastPivotBar == divergenceStartBar and lastPivotBar > divergenceEndBar:
                        method_call(delete, array.pop(divergenceObjects))
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

                pricePoint__00000095__ = chart.point.new(lastPivot.point.time, lastPivot.point.index, lastPrice)
                oscillatorPoint = chart.point.new(lastPivot.point.time, lastPivot.point.index, lastPivot.point.price)

                if priceDirection != oscillatorDirection and method_call('size', llastPivot.indicatorRatios) > 0:
                    llastPrice = method_call('get', llastPivot.indicatorValues, 0)
                    llastRatio = method_call('get', llastPivot.indicatorRatios, 0)
                    llastMa = method_call('get', llastPivot.indicatorValues, 1)
                    lastPricePoint = chart.point.new(llastPivot.point.time, llastPivot.point.index, llastPrice)
                    llastOscillatorPoint = chart.point.new(llastPivot.point.time, llastPivot.point.index, llastPivot.point.price)

                    sentiment = math.sign(oscRatio - priceRatio)
                    trend = math.sign(lastTrend) if properties.trendMethod == 3 else math.sign(dir * (llastRatio - 1)) if properties.trendMethod == 1 else math.sign(llastMa - lastMa)
                    divergence__00000094__ = 1 if trend == dir and sentiment < 0 else -1 if trend != dir and sentiment > 0 else 0
                    if divergence__00000094__ != 0:
                        divergenceType = getDivergenceType(dir, divergence__00000094__)
                        priceDivergenceLine: dr.Line__ren__ = dr.Line__ren__.new(lastPricePoint, pricePoint__00000095__, map.get(priceLinePropertiesMap, divergenceType))
                        oscillatorDivergenceLine: dr.Line__ren__ = dr.Line__ren__.new(llastOscillatorPoint, oscillatorPoint, map.get(oscillatorLinePropertiesMap, divergenceType))

                        validDivergence: bool = True
                        __loop_4__ = pine_loop(lastPricePoint.index + 1, 1)
                        while __loop_4__.step(pricePoint__00000095__.index - 1):
                            bar = __loop_4__.value
                            priceAtBar = map.get(priceMap, bar)
                            oscillatorAtBar = map.get(oscillatorMap, bar)
                            if priceAtBar * dir > method_call('get_price', priceDivergenceLine, bar) * dir or oscillatorAtBar * dir > method_call('get_price', oscillatorDivergenceLine, bar) * dir:
                                validDivergence = False
                                break

                        if validDivergence:
                            priceLabelText = 'D' if divergenceType == DivergenceType.BullishDivergence or divergenceType == DivergenceType.BearishDivergence else 'H'
                            priceTooltipText = string.tostring(divergenceType) + '\nPrice : ' + string.tostring(lastPrice) + ' ( ' + string.tostring(priceRatio) + ' ) - ' + string.tostring(priceDirection) + '\n' + 'Oscillator :' + string.tostring(lastMa) + ' ( ' + string.tostring(oscRatio) + ' ) - ' + string.tostring(oscillatorDirection)
                            priceDivergenceLabel: dr.Label__ren__ = dr.Label__ren__.new(pricePoint__00000095__, priceLabelText, priceTooltipText, map.get(priceLabelPropertiesMap, divergenceType))
                            oscillatorDivergenceLabel: dr.Label__ren__ = dr.Label__ren__.new(oscillatorPoint, priceLabelText, priceTooltipText, map.get(oscillatorLabelPropertiesMap, divergenceType))
                            if map.get(allowedDivergenceTypes, divergenceType):
                                alert('Alert : ' + priceTooltipText, alert.freq_once_per_bar_close)
                            divergenceObject: DivergenceObject = DivergenceObject(priceDivergenceLine, oscillatorDivergenceLine, priceDivergenceLabel, oscillatorDivergenceLabel, pricePoint__00000095__, divergenceType)
                            delete(divergenceObject)
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

    for divergence__000000ad__ in divergenceObjects:
        direction = 1 if divergence__000000ad__.divergenceType == DivergenceType.BullishDivergence or divergence__000000ad__.divergenceType == DivergenceType.BullishHiddenDivergence else -1
        if not divergence__000000ad__.broken and divergence__000000ad__.pricePoint.price * direction > close * direction:
            divergence__000000ad__.broken = True

    lastDivergence = DivergenceType.None__ren__ if array.size(divergenceObjects) == 0 or array.last(divergenceObjects).broken else array.last(divergenceObjects).divergenceType

    plot(1 if currentDivergence == DivergenceType.BullishDivergence else 0, 'Bullish Divergence (Current)', color.green, display=display.data_window)
    plot(1 if currentDivergence == DivergenceType.BearishDivergence else 0, 'Bearish Divergence (Current)', color.red, display=display.data_window)
    plot(1 if currentDivergence == DivergenceType.BullishHiddenDivergence else 0, 'Bullish Hidden Divergence (Current)', color.lime, display=display.data_window)
    plot(1 if currentDivergence == DivergenceType.BearishHiddenDivergence else 0, 'Bearish Hidden Divergence (Current)', color.red, display=display.data_window)

    plot(1 if lastDivergence == DivergenceType.BullishDivergence else 0, 'Bullish Divergence (Last)', color.green, display=display.data_window)
    plot(1 if lastDivergence == DivergenceType.BearishDivergence else 0, 'Bearish Divergence (Last)', color.red, display=display.data_window)
    plot(1 if lastDivergence == DivergenceType.BullishHiddenDivergence else 0, 'Bullish Hidden Divergence (Last)', color.lime, display=display.data_window)
    plot(1 if lastDivergence == DivergenceType.BearishHiddenDivergence else 0, 'Bearish Hidden Divergence (Last)', color.red, display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)