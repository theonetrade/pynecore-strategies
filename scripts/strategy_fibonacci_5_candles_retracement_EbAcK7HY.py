"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, bar_index, barstate, chart, close, color, extend, format, high,
    input, label, line, low, math, na, open, script, size, strategy, string, syminfo, ta, xloc,
    yloc
)
from pynecore.types import Color, Label, Line, Persistent


@script.strategy('Fibonacci 5 Candles Retracement VERSION 2 - Close Bar', 'Fib5CClose', overlay=True, max_labels_count=500, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100)
def main(
    showLabelsInput=input.bool(True, 'Show Start/End Labels', group='VISUALIZATION'),
    labelSizeInput=input.string('small', 'Label Size', group='VISUALIZATION', options=('tiny', 'small', 'normal', 'large', 'huge')),
    showStartEndLinesInput=input.bool(True, 'Show Start/End Lines', group='VISUALIZATION'),
    show50LineInput=input.bool(True, 'Show 50% Line', group='VISUALIZATION'),
    show25LineInput=input.bool(True, 'Show 25% Line', group='VISUALIZATION'),
    show618LineInput=input.bool(True, 'Show 60% Line', group='VISUALIZATION'),
    show786LineInput=input.bool(True, 'Show 70% Line', group='VISUALIZATION'),
    showPendingOrdersInput=input.bool(True, 'Show Pending Orders', group='VISUALIZATION'),
    colorStartEndLineInput=input.color(color.white, 'Start/End Line Color', group='LINE COLORS'),
    color50LineInput=input.color(color.new('#FFD700'), '50% Line Color', group='LINE COLORS'),
    color25LineInput=input.color(color.new('#00FF00'), '25% Line Color', group='LINE COLORS'),
    color60LineInput=input.color(color.new('#00CED1'), '60% Line Color', group='LINE COLORS'),
    color70LineInput=input.color(color.new('#F23645'), '70% Line Color', group='LINE COLORS'),
    pendingOrderLevelInput=input.string('50%', 'Pending Order Level', group='STRATEGY', options=('25%', '50%', '60%', '70%')),
    tpMultiplierInput=input.float(0.0, 'Extended TP (%)', group='STRATEGY', minval=0.0, step=0.1),
    minTrendPipsInput=input.float(0.0, 'Minimum Trend (pips)', group='FILTERS', minval=0.0, step=1.0, tooltip='If trend is below this value, start/end will be gray and pending order will not be placed'),
    useEmaFilterInput=input.bool(False, 'Use EMA Filter', group='FILTERS', tooltip='If active, open LONG only if EMA50 > EMA200, SHORT only if EMA50 < EMA200'),
    extendedTrendInput=input.bool(False, 'Extended Trend', group='FILTERS', tooltip='If active, trend remains in formation until a candle closes beyond the dynamic 50%. When this happens, end freezes but trend can continue.'),
    enableAlertsInput=input.bool(False, 'Enable Alerts', group='ALERTS', tooltip='If active, sends alerts when a pending order is created/updated or when filled')
):
    GREEN: Color = color.new('#7BFF23')
    RED: Color = color.new('#F23645')
    YELLOW: Color = color.new('#FFD700')
    ORANGE: Color = color.new('#FFA500')
    AZURE: Color = color.new('#00CED1')
    GREEN_FIB: Color = color.new('#00FF00')

    def getPendingOrderLevel(pointA, pointB):
        level: float = na(float)
        if pendingOrderLevelInput == '25%':
            level = pointB + (pointA - pointB) * 0.25
        elif pendingOrderLevelInput == '50%':
            level = pointB + (pointA - pointB) * 0.5
        elif pendingOrderLevelInput == '60%':
            level = pointB + (pointA - pointB) * 0.6
        elif pendingOrderLevelInput == '70%':
            level = pointB + (pointA - pointB) * 0.7
        return level

    def getExtendedTP(pointA, pointB, isBullish):
        tp: float = na(float)
        if tpMultiplierInput > 0.0:
            if isBullish:
                tp = pointA + (pointB - pointA) * (1.0 + tpMultiplierInput / 100.0)
            else:
                tp = pointB - (pointA - pointB) * (tpMultiplierInput / 100.0)
        else:
            tp = pointB
        return tp

    def calculatePips(price1, price2):
        diff: float = math.abs(price1 - price2)
        pipValue: float = 0.0001
        if syminfo.type == 'forex':
            if string.contains(syminfo.ticker, 'JPY') or string.contains(syminfo.tickerid, 'JPY'):
                pipValue = 0.01
            else:
                pipValue = 0.0001
        else:
            pipValue = syminfo.mintick
        return diff / pipValue

    def isTrendValid(pointA, pointB):
        __block_result__ = na
        if minTrendPipsInput <= 0.0:
            __block_result__ = True
        else:
            trendPips: float = calculatePips(pointA, pointB)
            __block_result__ = trendPips >= minTrendPipsInput
        return __block_result__

    ema50 = ta.ema(close, 50)
    ema200 = ta.ema(close, 200)

    def isEmaFilterValid(isBullish):
        __block_result_1__ = na
        if not useEmaFilterInput:
            __block_result_1__ = True
        else:
            __block_result_2__ = na
            if isBullish:
                __block_result_2__ = ema50 > ema200
            else:
                __block_result_2__ = ema50 < ema200
            __block_result_1__ = __block_result_2__
        return __block_result_1__

    def sendPendingOrderAlert(direction, entryPrice, slPrice, tpPrice, isUpdate):
        __block_result_3__ = na
        if enableAlertsInput:
            message: str = 'Pending Updated - ' if isUpdate else 'Pending Created - '
            message += direction + '\n'
            message += 'Entry: ' + string.tostring(entryPrice, format.mintick) + '\n'
            message += 'SL: ' + string.tostring(slPrice, format.mintick) + '\n'
            message += 'TP: ' + string.tostring(tpPrice, format.mintick)
            __block_result_3__ = alert(message, alert.freq_once_per_bar)
        return __block_result_3__

    def sendOrderFilledAlert(direction, entryPrice):
        __block_result_4__ = na
        if enableAlertsInput:
            message: str = 'Order Opened - ' + direction + '\n'
            message += 'Entry: ' + string.tostring(entryPrice, format.mintick)
            __block_result_4__ = alert(message, alert.freq_once_per_bar)
        return __block_result_4__

    def isRedCandle(index):
        return close[index] < open[index]

    def isGreenCandle(index):
        return close[index] > open[index]

    def isBearishTrend():
        return isRedCandle(0) and isRedCandle(1) and isRedCandle(2) and isRedCandle(3) and isRedCandle(4)

    def isBullishTrend():
        return isGreenCandle(0) and isGreenCandle(1) and isGreenCandle(2) and isGreenCandle(3) and isGreenCandle(4)

    activeBearishTrend: Persistent[bool] = False
    activeBullishTrend: Persistent[bool] = False
    pointA: Persistent[float] = na(float)
    pointB: Persistent[float] = na(float)
    barA: Persistent[int] = na(int)
    barB: Persistent[int] = na(int)
    labelA: Persistent[Label] = na(Label)
    labelB: Persistent[Label] = na(Label)
    pendingOrderLabel: Persistent[Label] = na(Label)
    lineStart: Persistent[Line] = na(Line)
    lineEnd: Persistent[Line] = na(Line)
    line50: Persistent[Line] = na(Line)
    line25: Persistent[Line] = na(Line)
    line618: Persistent[Line] = na(Line)
    line786: Persistent[Line] = na(Line)
    trendCompleted: Persistent[bool] = False
    pendingOrderId: Persistent[str] = na(str)
    isBullishOrder: Persistent[bool] = False
    finalPointA: Persistent[float] = na(float)
    finalPointB: Persistent[float] = na(float)
    lastLevel50: Persistent[float] = na(float)
    lastOpenTrades: Persistent[int] = 0
    currentTrendValid: Persistent[bool] = True
    endFrozen: Persistent[bool] = False

    pendingShortEntry: Persistent[bool] = False
    pendingLongEntry: Persistent[bool] = False
    pendingEntryPrice: Persistent[float] = na(float)
    pendingStopLoss: Persistent[float] = na(float)
    pendingTakeProfit: Persistent[float] = na(float)

    if isBearishTrend() and (not inline_series(isBearishTrend(), 1)) and (not activeBearishTrend or trendCompleted):
        activeBearishTrend = True
        activeBullishTrend = False
        trendCompleted = False
        lastOpenTrades = 0
        endFrozen = False

        if high[4] >= high[5]:
            pointA = high[4]
            barA = bar_index - 4
        else:
            pointA = high[5]
            barA = bar_index - 5

        pointB = math.min(low, math.min(low[1], math.min(low[2], math.min(low[3], low[4]))))

        if pointB == low:
            barB = bar_index
        elif pointB == low[1]:
            barB = bar_index - 1
        elif pointB == low[2]:
            barB = bar_index - 2
        elif pointB == low[3]:
            barB = bar_index - 3
        elif pointB == low[4]:
            barB = bar_index - 4

        currentTrendValid = isTrendValid(pointA, pointB)

        if showLabelsInput:
            labelAColor: Color = RED if currentTrendValid else color.gray
            labelA = label.new(barA, pointA, 'start', xloc.bar_index, yloc.price, labelAColor, textcolor=color.white, size=size.tiny if labelSizeInput == 'tiny' else size.small if labelSizeInput == 'small' else size.normal if labelSizeInput == 'normal' else size.large if labelSizeInput == 'large' else size.huge, style=label.style_label_down)
            labelBColor: Color = RED if currentTrendValid else color.gray
            labelB = label.new(barB, pointB, 'end', xloc.bar_index, yloc.price, labelBColor, textcolor=color.white, size=size.tiny if labelSizeInput == 'tiny' else size.small if labelSizeInput == 'small' else size.normal if labelSizeInput == 'normal' else size.large if labelSizeInput == 'large' else size.huge, style=label.style_label_up)

        if showStartEndLinesInput:
            lineStart = line.new(chart.point.from_index(barA, pointA), chart.point.from_index(bar_index, pointA), color=colorStartEndLineInput, width=1, style=line.style_solid, extend=extend.none)
            lineEnd = line.new(chart.point.from_index(barB, pointB), chart.point.from_index(bar_index, pointB), color=colorStartEndLineInput, width=1, style=line.style_solid, extend=extend.none)

        if show50LineInput:
            level50: float = pointB + (pointA - pointB) * 0.5
            line50 = line.new(chart.point.from_index(barA, level50), chart.point.from_index(bar_index, level50), color=color50LineInput, width=1, style=line.style_solid, extend=extend.none)

        if show25LineInput:
            level25: float = pointB + (pointA - pointB) * 0.25
            line25 = line.new(chart.point.from_index(barA, level25), chart.point.from_index(bar_index, level25), color=color25LineInput, width=1, style=line.style_solid, extend=extend.none)

        if show618LineInput:
            level618: float = pointB + (pointA - pointB) * 0.6
            line618 = line.new(chart.point.from_index(barA, level618), chart.point.from_index(bar_index, level618), color=color60LineInput, width=1, style=line.style_solid, extend=extend.none)

        if show786LineInput:
            level786: float = pointB + (pointA - pointB) * 0.7
            line786 = line.new(chart.point.from_index(barA, level786), chart.point.from_index(bar_index, level786), color=color70LineInput, width=1, style=line.style_solid, extend=extend.none)

    if activeBearishTrend and (not trendCompleted):
        level50: float = pointB + (pointA - pointB) * 0.5
        shouldComplete: bool = False

        if extendedTrendInput:
            if barstate.isconfirmed and close[1] > level50:
                shouldComplete = True
                endFrozen = True
        else:
            if barstate.isconfirmed and close[1] > open[2]:
                shouldComplete = True

        if shouldComplete:
            if not endFrozen:
                trendCompleted = True

            if not endFrozen and low[1] < pointB:
                pointB = low[1]
                barB = bar_index - 1
                currentTrendValid = isTrendValid(pointA, pointB)
                if showLabelsInput:
                    if not na(labelA):
                        label.delete(labelA)
                        labelAColor: Color = RED if currentTrendValid else color.gray
                        labelA = label.new(barA, pointA, 'start', xloc.bar_index, yloc.price, labelAColor, textcolor=color.white, size=size.tiny if labelSizeInput == 'tiny' else size.small if labelSizeInput == 'small' else size.normal if labelSizeInput == 'normal' else size.large if labelSizeInput == 'large' else size.huge, style=label.style_label_down)
                    if not na(labelB):
                        label.delete(labelB)
                        labelBColor: Color = RED if currentTrendValid else color.gray
                        labelB = label.new(barB, pointB, 'end', xloc.bar_index, yloc.price, labelBColor, textcolor=color.white, size=size.tiny if labelSizeInput == 'tiny' else size.small if labelSizeInput == 'small' else size.normal if labelSizeInput == 'normal' else size.large if labelSizeInput == 'large' else size.huge, style=label.style_label_up)
                if show50LineInput and (not na(line50)):
                    level50 = pointB + (pointA - pointB) * 0.5
                    line.set_xy1(line50, barA, level50)
                    line.set_xy2(line50, bar_index, level50)
                if show25LineInput and (not na(line25)):
                    level25: float = pointB + (pointA - pointB) * 0.25
                    line.set_xy1(line25, barA, level25)
                    line.set_xy2(line25, bar_index, level25)
                if show618LineInput and (not na(line618)):
                    level618: float = pointB + (pointA - pointB) * 0.6
                    line.set_xy1(line618, barA, level618)
                    line.set_xy2(line618, bar_index, level618)
                if show786LineInput and (not na(line786)):
                    level786: float = pointB + (pointA - pointB) * 0.7
                    line.set_xy1(line786, barA, level786)
                    line.set_xy2(line786, bar_index, level786)

            finalPointA = pointA
            finalPointB = pointB

            if currentTrendValid and isEmaFilterValid(False) and barstate.isconfirmed:
                if not na(pendingOrderId):
                    strategy.cancel(pendingOrderId)
                    pendingOrderId = na

                entryLevel: float = getPendingOrderLevel(pointA, pointB)
                pendingShortEntry = True
                pendingLongEntry = False
                pendingEntryPrice = entryLevel
                pendingStopLoss = pointA
                pendingTakeProfit = pointB
                pendingOrderId = "FibShort"
                isBullishOrder = False
                lastLevel50 = entryLevel

                sendPendingOrderAlert('SHORT', entryLevel, pointA, pointB, False)

                if showPendingOrdersInput:
                    if not na(pendingOrderLabel):
                        label.delete(pendingOrderLabel)
                    shortPendingOffset: float = (pointA - pointB) * 0.25
                    shortPendingPrice: float = pointB - shortPendingOffset
                    pendingOrderLabel = label.new(bar_index, shortPendingPrice, 'SHORT Pending\nEntry: ' + string.tostring(entryLevel, format.mintick) + '\nSL: ' + string.tostring(pointA, format.mintick) + '\nTP: ' + string.tostring(pointB, format.mintick), xloc.bar_index, yloc.price, color.red, textcolor=color.white, style=label.style_label_up, size=size.small)

            activeBearishTrend = False
        else:
            if not endFrozen and low < pointB:
                pointB = low
                barB = bar_index
                currentTrendValid = isTrendValid(pointA, pointB)
                if showLabelsInput:
                    if not na(labelA):
                        label.delete(labelA)
                        labelAColor: Color = RED if currentTrendValid else color.gray
                        labelA = label.new(barA, pointA, 'start', xloc.bar_index, yloc.price, labelAColor, textcolor=color.white, size=size.tiny if labelSizeInput == 'tiny' else size.small if labelSizeInput == 'small' else size.normal if labelSizeInput == 'normal' else size.large if labelSizeInput == 'large' else size.huge, style=label.style_label_down)
                    if not na(labelB):
                        label.delete(labelB)
                        labelBColor: Color = RED if currentTrendValid else color.gray
                        labelB = label.new(barB, pointB, 'end', xloc.bar_index, yloc.price, labelBColor, textcolor=color.white, size=size.tiny if labelSizeInput == 'tiny' else size.small if labelSizeInput == 'small' else size.normal if labelSizeInput == 'normal' else size.large if labelSizeInput == 'large' else size.huge, style=label.style_label_up)
                if showStartEndLinesInput and (not na(lineStart)):
                    line.set_xy1(lineStart, barA, pointA)
                    line.set_xy2(lineStart, bar_index, pointA)
                if showStartEndLinesInput and (not na(lineEnd)):
                    line.set_xy1(lineEnd, barB, pointB)
                    line.set_xy2(lineEnd, bar_index, pointB)
                if show50LineInput and (not na(line50)):
                    level50 = pointB + (pointA - pointB) * 0.5
                    line.set_xy1(line50, barA, level50)
                    line.set_xy2(line50, bar_index, level50)
                    if showPendingOrdersInput and (not na(pendingOrderLabel)) and (not isBullishOrder):
                        label.delete(pendingOrderLabel)
                        pendingLevel: float = getPendingOrderLevel(pointA, pointB)
                        shortPendingOffset: float = (pointA - pointB) * 0.25
                        shortPendingPrice: float = pointB - shortPendingOffset
                        pendingOrderLabel = label.new(bar_index, shortPendingPrice, 'SHORT Pending\nEntry: ' + string.tostring(pendingLevel, format.mintick) + '\nSL: ' + string.tostring(pointA, format.mintick) + '\nTP: ' + string.tostring(pointB, format.mintick), xloc.bar_index, yloc.price, color.red, textcolor=color.white, style=label.style_label_up, size=size.small)
                        sendPendingOrderAlert('SHORT', pendingLevel, pointA, pointB, True)
                if show25LineInput and (not na(line25)):
                    level25: float = pointB + (pointA - pointB) * 0.25
                    line.set_xy1(line25, barA, level25)
                    line.set_xy2(line25, bar_index, level25)
                if show618LineInput and (not na(line618)):
                    level618: float = pointB + (pointA - pointB) * 0.6
                    line.set_xy1(line618, barA, level618)
                    line.set_xy2(line618, bar_index, level618)
                if show786LineInput and (not na(line786)):
                    level786: float = pointB + (pointA - pointB) * 0.7
                    line.set_xy1(line786, barA, level786)
                    line.set_xy2(line786, bar_index, level786)
            else:
                if showStartEndLinesInput and (not na(lineStart)):
                    line.set_xy1(lineStart, barA, pointA)
                    line.set_xy2(lineStart, bar_index, pointA)
                if showStartEndLinesInput and (not na(lineEnd)):
                    line.set_xy1(lineEnd, barB, pointB)
                    line.set_xy2(lineEnd, bar_index, pointB)
                if show50LineInput and (not na(line50)):
                    level50 = pointB + (pointA - pointB) * 0.5
                    line.set_xy1(line50, barA, level50)
                    line.set_xy2(line50, bar_index, level50)
                if show25LineInput and (not na(line25)):
                    level25: float = pointB + (pointA - pointB) * 0.25
                    line.set_xy1(line25, barA, level25)
                    line.set_xy2(line25, bar_index, level25)
                if show618LineInput and (not na(line618)):
                    level618: float = pointB + (pointA - pointB) * 0.6
                    line.set_xy1(line618, barA, level618)
                    line.set_xy2(line618, bar_index, level618)
                if show786LineInput and (not na(line786)):
                    level786: float = pointB + (pointA - pointB) * 0.7
                    line.set_xy1(line786, barA, level786)
                    line.set_xy2(line786, bar_index, level786)

    if isBullishTrend() and (not inline_series(isBullishTrend(), 1)) and (not activeBullishTrend or trendCompleted):
        activeBullishTrend = True
        activeBearishTrend = False
        trendCompleted = False
        lastOpenTrades = 0
        endFrozen = False

        if low[4] <= low[5]:
            pointA = low[4]
            barA = bar_index - 4
        else:
            pointA = low[5]
            barA = bar_index - 5

        pointB = math.max(high, math.max(high[1], math.max(high[2], math.max(high[3], high[4]))))

        if pointB == high:
            barB = bar_index
        elif pointB == high[1]:
            barB = bar_index - 1
        elif pointB == high[2]:
            barB = bar_index - 2
        elif pointB == high[3]:
            barB = bar_index - 3
        elif pointB == high[4]:
            barB = bar_index - 4

        currentTrendValid = isTrendValid(pointA, pointB)

        if showLabelsInput:
            labelAOffset: float = (pointB - pointA) * 0.1
            labelAPrice: float = pointA - labelAOffset
            labelAColor: Color = GREEN if currentTrendValid else color.gray
            labelA = label.new(barA, labelAPrice, 'start', xloc.bar_index, yloc.price, labelAColor, textcolor=color.black, size=size.tiny if labelSizeInput == 'tiny' else size.small if labelSizeInput == 'small' else size.normal if labelSizeInput == 'normal' else size.large if labelSizeInput == 'large' else size.huge, style=label.style_label_up)
            labelBOffset: float = (pointB - pointA) * 0.15
            labelBPrice: float = pointB + labelBOffset
            labelBColor: Color = GREEN if currentTrendValid else color.gray
            labelB = label.new(barB, labelBPrice, 'end', xloc.bar_index, yloc.price, labelBColor, textcolor=color.black, size=size.tiny if labelSizeInput == 'tiny' else size.small if labelSizeInput == 'small' else size.normal if labelSizeInput == 'normal' else size.large if labelSizeInput == 'large' else size.huge, style=label.style_label_down)

        if showStartEndLinesInput:
            lineStart = line.new(chart.point.from_index(barA, pointA), chart.point.from_index(bar_index, pointA), color=colorStartEndLineInput, width=1, style=line.style_solid, extend=extend.none)
            lineEnd = line.new(chart.point.from_index(barB, pointB), chart.point.from_index(bar_index, pointB), color=colorStartEndLineInput, width=1, style=line.style_solid, extend=extend.none)

        if show50LineInput:
            level50: float = pointB + (pointA - pointB) * 0.5
            line50 = line.new(chart.point.from_index(barA, level50), chart.point.from_index(bar_index, level50), color=color50LineInput, width=1, style=line.style_solid, extend=extend.none)

        if show25LineInput:
            level25: float = pointB + (pointA - pointB) * 0.25
            line25 = line.new(chart.point.from_index(barA, level25), chart.point.from_index(bar_index, level25), color=color25LineInput, width=1, style=line.style_solid, extend=extend.none)

        if show618LineInput:
            level618: float = pointB + (pointA - pointB) * 0.6
            line618 = line.new(chart.point.from_index(barA, level618), chart.point.from_index(bar_index, level618), color=color60LineInput, width=1, style=line.style_solid, extend=extend.none)

        if show786LineInput:
            level786: float = pointB + (pointA - pointB) * 0.7
            line786 = line.new(chart.point.from_index(barA, level786), chart.point.from_index(bar_index, level786), color=color70LineInput, width=1, style=line.style_solid, extend=extend.none)

    if activeBullishTrend and (not trendCompleted):
        level50: float = pointB + (pointA - pointB) * 0.5
        shouldComplete: bool = False

        if extendedTrendInput:
            if barstate.isconfirmed and close[1] < level50:
                shouldComplete = True
                endFrozen = True
        else:
            if barstate.isconfirmed and close[1] < open[2]:
                shouldComplete = True

        if shouldComplete:
            if not endFrozen:
                trendCompleted = True

            if not endFrozen and high[1] > pointB:
                pointB = high[1]
                barB = bar_index - 1
                currentTrendValid = isTrendValid(pointA, pointB)
                if showLabelsInput:
                    if not na(labelA):
                        label.delete(labelA)
                        labelAOffset: float = (pointB - pointA) * 0.1
                        labelAPrice: float = pointA - labelAOffset
                        labelAColor: Color = GREEN if currentTrendValid else color.gray
                        labelA = label.new(barA, labelAPrice, 'start', xloc.bar_index, yloc.price, labelAColor, textcolor=color.black, size=size.tiny if labelSizeInput == 'tiny' else size.small if labelSizeInput == 'small' else size.normal if labelSizeInput == 'normal' else size.large if labelSizeInput == 'large' else size.huge, style=label.style_label_up)
                    if not na(labelB):
                        label.delete(labelB)
                        labelBOffset: float = (pointB - pointA) * 0.15
                        labelBPrice: float = pointB + labelBOffset
                        labelBColor: Color = GREEN if currentTrendValid else color.gray
                        labelB = label.new(barB, labelBPrice, 'end', xloc.bar_index, yloc.price, labelBColor, textcolor=color.black, size=size.tiny if labelSizeInput == 'tiny' else size.small if labelSizeInput == 'small' else size.normal if labelSizeInput == 'normal' else size.large if labelSizeInput == 'large' else size.huge, style=label.style_label_down)
                if showStartEndLinesInput and (not na(lineStart)):
                    line.set_xy1(lineStart, barA, pointA)
                    line.set_xy2(lineStart, bar_index, pointA)
                if showStartEndLinesInput and (not na(lineEnd)):
                    line.set_xy1(lineEnd, barB, pointB)
                    line.set_xy2(lineEnd, bar_index, pointB)
                if show50LineInput and (not na(line50)):
                    level50 = pointB + (pointA - pointB) * 0.5
                    line.set_xy1(line50, barA, level50)
                    line.set_xy2(line50, bar_index, level50)
                if show25LineInput and (not na(line25)):
                    level25: float = pointB + (pointA - pointB) * 0.25
                    line.set_xy1(line25, barA, level25)
                    line.set_xy2(line25, bar_index, level25)
                if show618LineInput and (not na(line618)):
                    level618: float = pointB + (pointA - pointB) * 0.6
                    line.set_xy1(line618, barA, level618)
                    line.set_xy2(line618, bar_index, level618)
                if show786LineInput and (not na(line786)):
                    level786: float = pointB + (pointA - pointB) * 0.7
                    line.set_xy1(line786, barA, level786)
                    line.set_xy2(line786, bar_index, level786)

            finalPointA = pointA
            finalPointB = pointB

            if currentTrendValid and isEmaFilterValid(True) and barstate.isconfirmed:
                if not na(pendingOrderId):
                    strategy.cancel(pendingOrderId)
                    pendingOrderId = na

                entryLevel: float = getPendingOrderLevel(pointA, pointB)
                pendingLongEntry = True
                pendingShortEntry = False
                pendingEntryPrice = entryLevel
                pendingStopLoss = pointA
                pendingTakeProfit = pointB
                pendingOrderId = "FibLong"
                isBullishOrder = True
                lastLevel50 = entryLevel

                sendPendingOrderAlert('LONG', entryLevel, pointA, pointB, False)

                if showPendingOrdersInput:
                    if not na(pendingOrderLabel):
                        label.delete(pendingOrderLabel)
                    longPendingOffset: float = (pointB - pointA) * 0.5
                    longPendingPrice: float = pointB + longPendingOffset
                    pendingOrderLabel = label.new(bar_index, longPendingPrice, 'LONG Pending\nEntry: ' + string.tostring(entryLevel, format.mintick) + '\nSL: ' + string.tostring(pointA, format.mintick) + '\nTP: ' + string.tostring(pointB, format.mintick), xloc.bar_index, yloc.price, GREEN, textcolor=color.black, style=label.style_label_down, size=size.small)

            activeBullishTrend = False
        else:
            if not endFrozen and high > pointB:
                pointB = high
                barB = bar_index
                currentTrendValid = isTrendValid(pointA, pointB)
                if showLabelsInput:
                    if not na(labelA):
                        label.delete(labelA)
                        labelAOffset: float = (pointB - pointA) * 0.1
                        labelAPrice: float = pointA - labelAOffset
                        labelAColor: Color = GREEN if currentTrendValid else color.gray
                        labelA = label.new(barA, labelAPrice, 'start', xloc.bar_index, yloc.price, labelAColor, textcolor=color.black, size=size.tiny if labelSizeInput == 'tiny' else size.small if labelSizeInput == 'small' else size.normal if labelSizeInput == 'normal' else size.large if labelSizeInput == 'large' else size.huge, style=label.style_label_up)
                    if not na(labelB):
                        label.delete(labelB)
                        labelBOffset: float = (pointB - pointA) * 0.15
                        labelBPrice: float = pointB + labelBOffset
                        labelBColor: Color = GREEN if currentTrendValid else color.gray
                        labelB = label.new(barB, labelBPrice, 'end', xloc.bar_index, yloc.price, labelBColor, textcolor=color.black, size=size.tiny if labelSizeInput == 'tiny' else size.small if labelSizeInput == 'small' else size.normal if labelSizeInput == 'normal' else size.large if labelSizeInput == 'large' else size.huge, style=label.style_label_down)
                if showStartEndLinesInput and (not na(lineStart)):
                    line.set_xy1(lineStart, barA, pointA)
                    line.set_xy2(lineStart, bar_index, pointA)
                if showStartEndLinesInput and (not na(lineEnd)):
                    line.set_xy1(lineEnd, barB, pointB)
                    line.set_xy2(lineEnd, bar_index, pointB)
                if show50LineInput and (not na(line50)):
                    level50 = pointB + (pointA - pointB) * 0.5
                    line.set_xy1(line50, barA, level50)
                    line.set_xy2(line50, bar_index, level50)
                    if showPendingOrdersInput and (not na(pendingOrderLabel)) and isBullishOrder:
                        label.delete(pendingOrderLabel)
                        pendingLevel: float = getPendingOrderLevel(pointA, pointB)
                        longPendingOffset: float = (pointB - pointA) * 0.5
                        longPendingPrice: float = pointB + longPendingOffset
                        pendingOrderLabel = label.new(bar_index, longPendingPrice, 'LONG Pending\nEntry: ' + string.tostring(pendingLevel, format.mintick) + '\nSL: ' + string.tostring(pointA, format.mintick) + '\nTP: ' + string.tostring(pointB, format.mintick), xloc.bar_index, yloc.price, GREEN, textcolor=color.black, style=label.style_label_down, size=size.small)
                        sendPendingOrderAlert('LONG', pendingLevel, pointA, pointB, True)
                if show25LineInput and (not na(line25)):
                    level25: float = pointB + (pointA - pointB) * 0.25
                    line.set_xy1(line25, barA, level25)
                    line.set_xy2(line25, bar_index, level25)
                if show618LineInput and (not na(line618)):
                    level618: float = pointB + (pointA - pointB) * 0.6
                    line.set_xy1(line618, barA, level618)
                    line.set_xy2(line618, bar_index, level618)
                if show786LineInput and (not na(line786)):
                    level786: float = pointB + (pointA - pointB) * 0.7
                    line.set_xy1(line786, barA, level786)
                    line.set_xy2(line786, bar_index, level786)
            else:
                if showStartEndLinesInput and (not na(lineStart)):
                    line.set_xy1(lineStart, barA, pointA)
                    line.set_xy2(lineStart, bar_index, pointA)
                if showStartEndLinesInput and (not na(lineEnd)):
                    line.set_xy1(lineEnd, barB, pointB)
                    line.set_xy2(lineEnd, bar_index, pointB)
                if show50LineInput and (not na(line50)):
                    level50 = pointB + (pointA - pointB) * 0.5
                    line.set_xy1(line50, barA, level50)
                    line.set_xy2(line50, bar_index, level50)
                if show25LineInput and (not na(line25)):
                    level25: float = pointB + (pointA - pointB) * 0.25
                    line.set_xy1(line25, barA, level25)
                    line.set_xy2(line25, bar_index, level25)
                if show618LineInput and (not na(line618)):
                    level618: float = pointB + (pointA - pointB) * 0.6
                    line.set_xy1(line618, barA, level618)
                    line.set_xy2(line618, bar_index, level618)
                if show786LineInput and (not na(line786)):
                    level786: float = pointB + (pointA - pointB) * 0.7
                    line.set_xy1(line786, barA, level786)
                    line.set_xy2(line786, bar_index, level786)

    if barstate.isconfirmed:
        if pendingShortEntry and strategy.opentrades == 0:
            strategy.entry('FibShort', strategy.short, limit=pendingEntryPrice, comment='Fib ' + pendingOrderLevelInput)
            strategy.exit('FibShortExit', 'FibShort', stop=pendingStopLoss, limit=pendingTakeProfit, comment='Fib Exit')
            pendingShortEntry = False
            sendOrderFilledAlert('SHORT', pendingEntryPrice)

        if pendingLongEntry and strategy.opentrades == 0:
            strategy.entry('FibLong', strategy.long, limit=pendingEntryPrice, comment='Fib ' + pendingOrderLevelInput)
            strategy.exit('FibLongExit', 'FibLong', stop=pendingStopLoss, limit=pendingTakeProfit, comment='Fib Exit')
            pendingLongEntry = False
            sendOrderFilledAlert('LONG', pendingEntryPrice)

        if strategy.opentrades > 0 and lastOpenTrades > 0:
            if strategy.position_size < 0:
                if tpMultiplierInput > 0.0 and (not na(finalPointA)) and (not na(finalPointB)):
                    extendedTP: float = getExtendedTP(finalPointA, finalPointB, False)
                    strategy.exit('FibShortExit', 'FibShort', stop=finalPointA, limit=extendedTP, comment='Fib Exit')
            elif strategy.position_size > 0:
                if tpMultiplierInput > 0.0 and (not na(finalPointA)) and (not na(finalPointB)):
                    extendedTP: float = getExtendedTP(finalPointA, finalPointB, True)
                    strategy.exit('FibLongExit', 'FibLong', stop=finalPointA, limit=extendedTP, comment='Fib Exit')

    if strategy.opentrades > 0 and lastOpenTrades == 0:
        entryPrice: float = strategy.position_avg_price
        if strategy.position_size < 0:
            sendOrderFilledAlert('SHORT', entryPrice)
        elif strategy.position_size > 0:
            sendOrderFilledAlert('LONG', entryPrice)

    lastOpenTrades = strategy.opentrades


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
