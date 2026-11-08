"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, close, color, display,
    format, high, input, label, last_bar_index, last_bar_time, line, location, low, math, na, nz,
    plot, plotshape, position, runtime, script, session, shape, size, string, ta, table, time,
    timeframe
)
from pynecore.types import Color, Label, Line, NA, Persistent, Series, Table


@udt
class Breakout:
    isBullish: bool = na(bool)
    startIndex: int = na(int)
    endIndex: int = na(int)
    failed: bool = False
    retests: int = 0


@udt
class ORB:
    h: float = na(float)
    l: float = na(float)
    startTime: int = na(int)
    startIndex: int = na(int)
    endIndex: int = na(int)
    isLastSession: bool = na(bool)

    state: str = 'Opening Range'
    breakouts: 'list[Breakout]' = na(list)
    foundEntryTick: bool = False
    entryBullish: bool = na(bool)
    entryIndex: int = na(int)
    entryPrice: float = na(float)
    entryATR: float = na(float)

    tp1Index: int = na(int)
    tp1Price: float = na(float)
    tp1FoundTick: bool = False

    tp2Index: int = na(int)
    tp2Price: float = na(float)
    tp2FoundTick: bool = False

    tp3Index: int = na(int)
    tp3Price: float = na(float)
    tp3FoundTick: bool = False

    slIndex: int = na(int)
    slPrice: float = na(float)
    slFoundTick: bool = False

    isExitTrade: bool = False
    exitTradeFoundTick: bool = False

    hLine: Line = na(Line)
    lLine: Line = na(Line)
    entryLabel: Label = na(Label)


DEBUG: bool = False
minimumProfitPercent: float = 0.2
minimumProfitIncrementPercent: float = 0.075
stopLossPercent: float = 1.0
atrTP1Mult: float = 0.75
atrTP2Mult: float = 1.5
atrTP3Mult: float = 2.25
atrTotalMult: float = 1.0


@script.indicator('ORB Algo | Flux Charts', overlay=True, max_boxes_count=500, max_labels_count=500, max_lines_count=500, max_bars_back=5000)
def main(
    orbTimeStr=input.timeframe('30', 'ORB Timeframe', group='Algorithm', display=display.none),
    sensitivity=input.string('Medium', 'Sensitivity', options=('High', 'Medium', 'Low', 'Lowest'), group='Algorithm', display=display.none),
    breakoutCondition=input.string('Close', 'Breakout Condition', options=('Close', 'EMA'), group='Algorithm', display=display.none),
    tpMethod=input.string('Dynamic', 'TP Method', options=('Dynamic', 'ATR'), group='Algorithm', display=display.none),
    emaLength=input.int(9, 'EMA Length', options=(4, 9, 13, 20, 34), group='Algorithm', display=display.none),
    slMethod=input.string('Balanced', 'Stop-Loss', options=('Safer', 'Balanced', 'Risky'), group='Algorithm', display=display.none),
    adaptiveSL=input.bool(True, 'Adaptive SL', group='Algorithm', display=display.none),
    customSessionEnabled=input.bool(False, 'Enabled', group='Custom Session', display=display.none),
    customSessionTime=input.session('1000-1100', 'Session', group='Custom Session', display=display.none),
    orbDisplayEnabled=input.bool(True, 'Enabled', group='ORB Dashboard', display=display.none),
    orbLocation=input.string('Top Right', 'Position', options=('Top Right', 'Right Center', 'Top Center'), group='ORB Dashboard', display=display.none),
    backtestDisplayEnabled=input.bool(True, 'Enabled', group='Backtesting', display=display.none),
    backtestingLocation=input.string('Top Center', 'Position', options=('Top Right', 'Right Center', 'Top Center'), group='Backtesting', display=display.none),
    backtestingExitRatios=input.string('90% | 5% | 5%', 'Backtesting Exit Ratios', options=('75% | 15% | 10%', '50% | 25% | 25%', '34% | 33% | 33%', '90% | 5% | 5%', '100% | 0% | 0%', '0% | 100% | 0%', '0% | 0% | 100%'), tooltip='TP 1 | TP 2 | TP 3', group='Backtesting', display=display.none),
    showORBZones=input.bool(True, 'Draw ORB Zones', group='Visuals', display=display.none, inline='group1'),
    plotEMA=input.bool(False, 'Plot EMA', group='Visuals', display=display.none, inline='group1'),
    __input_16__=input.bool(True, 'Show Historic Zones', group='Visuals', display=display.none),
    highColor=input.color(color.green, 'High', inline='colors', group='Visuals'),
    lowColor=input.color(color.red, 'Low', inline='colors', group='Visuals')
):
    maxBarsBack: int = last_bar_index
    renderMaxBarsBack: int = 5000

    showHistoricZones = __input_16__ if DEBUG else True

    backtestTP1Exit: float = 0.0
    backtestTP2Exit: float = 0.0
    backtestTP3Exit: float = 0.0

    backtestTP1Exit = string.tonumber(string.replace(array.get(string.split(backtestingExitRatios, ' | '), 0), '%', '')) / 100.0
    backtestTP2Exit = string.tonumber(string.replace(array.get(string.split(backtestingExitRatios, ' | '), 1), '%', '')) / 100.0
    backtestTP3Exit = string.tonumber(string.replace(array.get(string.split(backtestingExitRatios, ' | '), 2), '%', '')) / 100.0

    retestsNeededForEntry = 0 if sensitivity == 'High' else 1 if sensitivity == 'Medium' else 2 if sensitivity == 'Low' else 3

    if timeframe.in_seconds() > timeframe.in_seconds('15'):
        runtime.error('ORB Algo only works on timeframes lower than 15 min.')


    def getPosition(positionText):
        __block_result__ = na
        if positionText == 'Top Right':
            __block_result__ = position.top_right
        elif positionText == 'Top Center':
            __block_result__ = position.top_center
        elif positionText == 'Right Center':
            __block_result__ = position.middle_right
        else:
            __block_result__ = position.middle_left
        return __block_result__

    def createORB(h: float, l: float, sT: int, sI: int, eI: int):
        newORB: ORB = ORB(h, l, sT, sI, eI)
        newORB.breakouts = array.new(0, NA(Breakout))
        return newORB

    def safeDeleteORB(orb: ORB):
        line.delete(orb.hLine)
        line.delete(orb.lLine)
        return label.delete(orb.entryLabel)

    orbColor: Color = color.new('#3B3B3B43')
    orbList: Persistent[list[ORB]] = array.new(0, NA(ORB))

    ema = ta.ema((high + low) / 2.0, emaLength)
    atr = ta.atr(12)
    plot(ema if plotEMA else na)

    def diffPercent(val1: float, val2: float):
        return math.abs(val1 - val2) / val2 * 100.0

    def renderORB(orb: ORB):
        __block_result_1__ = na
        if orb.startIndex > last_bar_index - renderMaxBarsBack:
            if showORBZones:
                orb.hLine = line.new(orb.startIndex, orb.h, nz(orb.endIndex, last_bar_index), orb.h, color=highColor, width=2)
                orb.lLine = line.new(orb.startIndex, orb.l, nz(orb.endIndex, last_bar_index), orb.l, color=lowColor, width=2)
            __block_result_2__ = na
            if not na(orb.entryIndex):
                orb.entryLabel = label.new(orb.entryIndex, orb.entryPrice + orb.entryATR * 3 * (-1 if orb.entryBullish else 1), 'Buy' if orb.entryBullish else 'Sell', color=color.green if orb.entryBullish else color.red, textcolor=color.white, style=label.style_label_up if orb.entryBullish else label.style_label_down)
                __block_result_2__ = orb.entryLabel
            __block_result_1__ = __block_result_2__
        return __block_result_1__

    lastORB: ORB = na(ORB)
    previousORB: ORB = na(ORB)
    if array.size(orbList) > 0:
        lastORB = array.get(orbList, 0)

        lastORB.tp1FoundTick = False
        lastORB.tp2FoundTick = False
        lastORB.tp3FoundTick = False
        lastORB.slFoundTick = False
        lastORB.foundEntryTick = False
        lastORB.exitTradeFoundTick = False

        if last_bar_time - time < 60 * 60 * 8 * 1000:
            lastORB.isLastSession = True
        else:
            lastORB.isLastSession = False

    def sessionBegins(sess):
        t: Series = time('1440', sess)
        is_first = na(t[1]) and (not na(t)) or t[1] < t
        return is_first

    lastClose = close[1]
    if barstate.isconfirmed and last_bar_index - bar_index < maxBarsBack:
        if not customSessionEnabled and session.isfirstbar_regular or (customSessionEnabled and sessionBegins(customSessionTime)):
            if not na(lastORB):
                lastORB.endIndex = bar_index - 1

                if not na(lastORB.entryIndex) and na(lastORB.slIndex):
                    lastORB.slPrice = lastClose
                    lastORB.slIndex = bar_index - 1
                    lastORB.exitTradeFoundTick = True
                    previousORB = lastORB

            newORB = createORB(na, na, time, bar_index, na)
            array.unshift(orbList, newORB)
            lastORB = array.get(orbList, 0)

        if not na(lastORB):
            if lastORB.state == 'Opening Range' and time < lastORB.startTime + timeframe.in_seconds(orbTimeStr) * 1000:
                lastORB.h = math.max(nz(lastORB.h, 0), high)
                lastORB.l = math.min(nz(lastORB.l, low), low)

            if lastORB.state == 'Opening Range' and time >= lastORB.startTime + timeframe.in_seconds(orbTimeStr) * 1000:
                lastORB.state = 'Waiting For Breakouts'

        if not na(lastORB):
            if lastORB.state == 'Waiting For Breakouts':
                conditionPrice = ema if breakoutCondition == 'EMA' else close
                if conditionPrice > lastORB.h or conditionPrice < lastORB.l:
                    newBreakout: Breakout = Breakout(conditionPrice > lastORB.h, bar_index, na)
                    array.unshift(lastORB.breakouts, newBreakout)
                    lastORB.state = 'In Breakout'

        if not na(lastORB):
            if lastORB.state == 'In Breakout':
                curBreakout = array.get(lastORB.breakouts, 0)

                if curBreakout.isBullish and close < lastORB.h or (not curBreakout.isBullish and close > lastORB.l):
                    curBreakout.failed = True
                    curBreakout.endIndex = bar_index
                    lastORB.state = 'Waiting For Breakouts'

                if bar_index > curBreakout.startIndex and (curBreakout.isBullish and close > lastORB.h and (low < lastORB.h) or (not curBreakout.isBullish and close < lastORB.l and (high > lastORB.l))):
                    curBreakout.retests = curBreakout.retests + 1

                if curBreakout.retests >= retestsNeededForEntry:
                    curBreakout.endIndex = bar_index
                    lastORB.state = 'Entry Taken'
                    lastORB.entryATR = atr
                    lastORB.foundEntryTick = True
                    lastORB.entryIndex = bar_index
                    lastORB.entryPrice = close
                    lastORB.entryBullish = curBreakout.isBullish

                    if slMethod == 'Fixed':
                        if curBreakout.isBullish:
                            lastORB.slPrice = lastORB.entryPrice * ((100.0 - stopLossPercent) / 100.0)
                        else:
                            lastORB.slPrice = lastORB.entryPrice * ((100.0 + stopLossPercent) / 100.0)

                    center = (lastORB.h + lastORB.l) / 2.0
                    if slMethod == 'Safer':
                        lastORB.slPrice = (center + lastORB.h) / 2.0 if lastORB.entryBullish else (center + lastORB.l) / 2.0
                    if slMethod == 'Balanced':
                        lastORB.slPrice = center
                    if slMethod == 'Risky':
                        lastORB.slPrice = (center + lastORB.l) / 2.0 if lastORB.entryBullish else (center + lastORB.h) / 2.0

        if not na(lastORB):
            if lastORB.state == 'Entry Taken':
                isProfitable = lastORB.entryBullish and ema > lastORB.entryPrice or (not lastORB.entryBullish and ema < lastORB.entryPrice)
                if tpMethod == 'Dynamic':
                    if isProfitable and diffPercent(ema, lastORB.entryPrice) >= minimumProfitPercent:
                        if na(lastORB.slIndex) and na(lastORB.tp1Index) and (lastORB.entryBullish and close < ema or (not lastORB.entryBullish and close > ema)):
                            lastORB.tp1Index = bar_index
                            lastORB.tp1Price = ema
                            lastORB.tp1FoundTick = True
                            if adaptiveSL:
                                lastORB.slPrice = lastORB.entryPrice
                        elif na(lastORB.slIndex) and (not na(lastORB.tp1Index)) and na(lastORB.tp2Index) and (lastORB.entryBullish and close < ema or (not lastORB.entryBullish and close > ema)):
                            if (lastORB.entryBullish and ema > lastORB.tp1Price or (not lastORB.entryBullish and ema < lastORB.tp1Price)) and diffPercent(ema, lastORB.tp1Price) >= minimumProfitIncrementPercent:
                                lastORB.tp2Index = bar_index
                                lastORB.tp2Price = ema
                                lastORB.tp2FoundTick = True
                        elif na(lastORB.slIndex) and (not na(lastORB.tp2Index)) and na(lastORB.tp3Index) and (lastORB.entryBullish and close < ema or (not lastORB.entryBullish and close > ema)):
                            if (lastORB.entryBullish and ema > lastORB.tp2Price or (not lastORB.entryBullish and ema < lastORB.tp2Price)) and diffPercent(ema, lastORB.tp2Price) >= minimumProfitIncrementPercent:
                                lastORB.tp3Index = bar_index
                                lastORB.tp3Price = ema
                                lastORB.tp3FoundTick = True
                                lastORB.slIndex = -1
                if tpMethod == 'ATR':
                    tp1Price: float = lastORB.entryPrice + lastORB.entryATR * atrTP1Mult * atrTotalMult * (1 if lastORB.entryBullish else -1)
                    tp2Price: float = lastORB.entryPrice + lastORB.entryATR * atrTP2Mult * atrTotalMult * (1 if lastORB.entryBullish else -1)
                    tp3Price: float = lastORB.entryPrice + lastORB.entryATR * atrTP3Mult * atrTotalMult * (1 if lastORB.entryBullish else -1)
                    if na(lastORB.slIndex) and na(lastORB.tp1Index) and (lastORB.entryBullish and high >= tp1Price or (not lastORB.entryBullish and low <= tp1Price)):
                        lastORB.tp1Index = bar_index
                        lastORB.tp1Price = tp1Price
                        lastORB.tp1FoundTick = True
                        if adaptiveSL:
                            lastORB.slPrice = lastORB.entryPrice
                    elif na(lastORB.slIndex) and (not na(lastORB.tp1Index)) and na(lastORB.tp2Index) and (lastORB.entryBullish and high >= tp2Price or (not lastORB.entryBullish and low <= tp2Price)):
                        lastORB.tp2Index = bar_index
                        lastORB.tp2Price = tp2Price
                        lastORB.tp2FoundTick = True
                    elif na(lastORB.slIndex) and (not na(lastORB.tp2Index)) and na(lastORB.tp3Index) and (lastORB.entryBullish and high >= tp3Price or (not lastORB.entryBullish and low <= tp3Price)):
                        lastORB.tp3Index = bar_index
                        lastORB.tp3Price = tp3Price
                        lastORB.tp3FoundTick = True
                        lastORB.slIndex = -1

                if not na(lastORB.slPrice) and na(lastORB.slIndex) and (lastORB.entryBullish and low < lastORB.slPrice or (not lastORB.entryBullish and high > lastORB.slPrice)):
                    if not (bar_index == lastORB.tp1Index or bar_index == lastORB.tp2Index or bar_index == lastORB.tp3Index):
                        lastORB.slFoundTick = True
                        lastORB.slIndex = bar_index

    isClose = bar_index > last_bar_index - renderMaxBarsBack
    plotshape(na if na(lastORB) else close if lastORB.tp1FoundTick and lastORB.entryBullish and isClose and (showHistoricZones or lastORB.isLastSession) else na, 'TP 1', shape.xcross, size=size.tiny, text='TP 1', textcolor=color.white, location=location.abovebar)
    plotshape(na if na(lastORB) else close if lastORB.tp1FoundTick and (not lastORB.entryBullish) and isClose and (showHistoricZones or lastORB.isLastSession) else na, 'TP 1', shape.xcross, size=size.tiny, text='TP 1', textcolor=color.white, location=location.belowbar)

    plotshape(na if na(lastORB) else close if lastORB.tp2FoundTick and lastORB.entryBullish and isClose and (showHistoricZones or lastORB.isLastSession) else na, 'TP 2', shape.xcross, size=size.tiny, text='TP 2', textcolor=color.white, location=location.abovebar)
    plotshape(na if na(lastORB) else close if lastORB.tp2FoundTick and (not lastORB.entryBullish) and isClose and (showHistoricZones or lastORB.isLastSession) else na, 'TP 2', shape.xcross, size=size.tiny, text='TP 2', textcolor=color.white, location=location.belowbar)

    plotshape(na if na(lastORB) else close if lastORB.tp3FoundTick and lastORB.entryBullish and isClose and (showHistoricZones or lastORB.isLastSession) else na, 'TP 3', shape.xcross, size=size.tiny, text='TP 3', textcolor=color.white, location=location.abovebar)
    plotshape(na if na(lastORB) else close if lastORB.tp3FoundTick and (not lastORB.entryBullish) and isClose and (showHistoricZones or lastORB.isLastSession) else na, 'TP 3', shape.xcross, size=size.tiny, text='TP 3', textcolor=color.white, location=location.belowbar)

    plotshape(na if na(lastORB) else close if lastORB.slFoundTick and lastORB.entryBullish and isClose and (showHistoricZones or lastORB.isLastSession) else na, 'SL', shape.xcross, size=size.tiny, text='SL', color=color.red, textcolor=color.white, location=location.belowbar)
    plotshape(na if na(lastORB) else close if lastORB.slFoundTick and (not lastORB.entryBullish) and isClose and (showHistoricZones or lastORB.isLastSession) else na, 'SL', shape.xcross, size=size.tiny, text='SL', color=color.red, textcolor=color.white, location=location.abovebar)

    plotshape(na if na(previousORB) else close if previousORB.exitTradeFoundTick and previousORB.entryBullish and isClose and (showHistoricZones or previousORB.isLastSession) else na, 'Exit', shape.xcross, size=size.tiny, text='Exit', color=color.red, textcolor=color.white, location=location.belowbar, offset=-1)
    plotshape(na if na(previousORB) else close if previousORB.exitTradeFoundTick and (not previousORB.entryBullish) and isClose and (showHistoricZones or previousORB.isLastSession) else na, 'Exit', shape.xcross, size=size.tiny, text='Exit', color=color.red, textcolor=color.white, location=location.abovebar, offset=-1)

    foundEntryTick: bool = False
    foundTPTick: bool = False
    foundSLTick: bool = False
    if not na(lastORB):
        if lastORB.foundEntryTick:
            foundEntryTick = True
        if lastORB.tp1FoundTick or lastORB.tp2FoundTick or lastORB.tp3FoundTick:
            foundTPTick = True
        if lastORB.slFoundTick:
            foundSLTick = True

    alertcondition(foundEntryTick, 'Buy / Sell')
    alertcondition(foundTPTick, 'Take Profit')
    alertcondition(foundSLTick, 'Stop Loss')

    if barstate.islast:
        if array.size(orbList) > 0:
            for i in pine_range(0, array.size(orbList) - 1 if showHistoricZones else 0, 1):
                curORB = array.get(orbList, i)
                safeDeleteORB(curORB)
                renderORB(curORB)

    if barstate.islast and orbDisplayEnabled:
        ORBDisplay: Persistent[Table] = table.new(getPosition(orbLocation), 4, 5, bgcolor=orbColor, frame_width=2, frame_color=color.black, border_width=1, border_color=color.black) if orbDisplayEnabled else na
        lastORBD: ORB = na(ORB)
        foundEntryPrice: float = na(float)
        isEntryBullish: bool = False
        if array.size(orbList) > 0:
            lastORBD = array.get(orbList, 0)
            foundEntryPrice = lastORBD.entryPrice
            isEntryBullish = lastORBD.entryBullish

        table.merge_cells(ORBDisplay, 0, 0, 3, 0)
        table.cell(ORBDisplay, 0, 0, 'ORB Dashboard', text_color=color.white, bgcolor=orbColor)

        table.merge_cells(ORBDisplay, 0, 1, 0, 2)
        table.cell(ORBDisplay, 0, 1, 'No Signal' if na(foundEntryPrice) else 'Bullish' if isEntryBullish else 'Bearish', text_color=color.white, bgcolor=orbColor if na(foundEntryPrice) else color.green if isEntryBullish else color.red)

        table.cell(ORBDisplay, 1, 1, 'Buy Price' if isEntryBullish else 'Sell Price', text_color=color.white, bgcolor=orbColor if na(foundEntryPrice) else color.new('#4CAF50') if isEntryBullish else color.red)
        table.cell(ORBDisplay, 1, 2, 'No Signal' if na(foundEntryPrice) else string.tostring(foundEntryPrice, format.mintick), text_color=color.white, bgcolor=orbColor if na(foundEntryPrice) else color.green if isEntryBullish else color.red)

        table.merge_cells(ORBDisplay, 2, 1, 3, 1)
        table.merge_cells(ORBDisplay, 2, 2, 3, 2)
        curProfit = close - foundEntryPrice
        if not isEntryBullish:
            curProfit = curProfit * -1

        curProfitPercent = curProfit / foundEntryPrice * 100.0
        table.cell(ORBDisplay, 2, 1, 'Current Profit %', text_color=color.white, bgcolor=orbColor if na(foundEntryPrice) else color.green if curProfit > 0 else color.red)
        profitPercentText: str = ''

        profitPercentText = profitPercentText + string.tostring(curProfitPercent, '#.##') + '%'
        if na(curProfitPercent):
            profitPercentText = 'No Signal'
        table.cell(ORBDisplay, 2, 2, profitPercentText, text_color=color.white, bgcolor=orbColor if na(foundEntryPrice) else color.green if curProfit > 0 else color.red)

        if not na(foundEntryPrice) and tpMethod == 'ATR':
            table.cell(ORBDisplay, 0, 3, 'TP 1', text_color=color.white)
            table.cell(ORBDisplay, 1, 3, 'TP 2', text_color=color.white)
            table.cell(ORBDisplay, 2, 3, 'TP 3', text_color=color.white)
            table.cell(ORBDisplay, 3, 3, 'SL', text_color=color.white)

            tp1Price: float = lastORBD.entryPrice + lastORBD.entryATR * atrTP1Mult * atrTotalMult * (1 if lastORBD.entryBullish else -1)
            tp2Price: float = lastORBD.entryPrice + lastORBD.entryATR * atrTP2Mult * atrTotalMult * (1 if lastORBD.entryBullish else -1)
            tp3Price: float = lastORBD.entryPrice + lastORBD.entryATR * atrTP3Mult * atrTotalMult * (1 if lastORBD.entryBullish else -1)
            table.cell(ORBDisplay, 0, 4, string.tostring(tp1Price, format.mintick), text_color=color.white)
            table.cell(ORBDisplay, 1, 4, string.tostring(tp2Price, format.mintick), text_color=color.white)
            table.cell(ORBDisplay, 2, 4, string.tostring(tp3Price, format.mintick), text_color=color.white)
            table.cell(ORBDisplay, 3, 4, string.tostring(lastORBD.slPrice, format.mintick), text_color=color.white)
        elif not na(foundEntryPrice):
            table.merge_cells(ORBDisplay, 0, 3, 3, 3)
            table.merge_cells(ORBDisplay, 0, 4, 3, 4)
            table.cell(ORBDisplay, 0, 3, 'SL', text_color=color.white)
            table.cell(ORBDisplay, 0, 4, string.tostring(lastORBD.slPrice, format.mintick), text_color=color.white)

    if barstate.islast and backtestDisplayEnabled:
        backtestDisplay: Persistent[Table] = table.new(getPosition(backtestingLocation), 2, 10, bgcolor=orbColor, frame_width=2, frame_color=color.black, border_width=1, border_color=color.black) if backtestDisplayEnabled else na
        totalORBProfitPercent: float = 0
        successfulTrades: int = 0
        unsuccessfulTrades: int = 0

        if array.size(orbList) > 0:
            for i in pine_range(0, array.size(orbList) - 1, 1):
                curORB = array.get(orbList, i)
                if not na(curORB.entryIndex):
                    isSuccess: bool = False
                    totalProfitTaken: float = 0.0
                    if not na(curORB.tp1Price):
                        isSuccess = True
                        totalORBProfitPercent = totalORBProfitPercent + diffPercent(curORB.tp1Price, curORB.entryPrice) * backtestTP1Exit
                        totalProfitTaken = totalProfitTaken + backtestTP1Exit
                    if not na(curORB.tp2Price):
                        isSuccess = True
                        totalORBProfitPercent = totalORBProfitPercent + diffPercent(curORB.tp2Price, curORB.entryPrice) * backtestTP2Exit
                        totalProfitTaken = totalProfitTaken + backtestTP2Exit
                    if not na(curORB.tp3Price):
                        isSuccess = True
                        totalORBProfitPercent = totalORBProfitPercent + diffPercent(curORB.tp3Price, curORB.entryPrice) * backtestTP3Exit
                        totalProfitTaken = totalProfitTaken + backtestTP3Exit
                    if not na(curORB.slIndex):
                        if curORB.slIndex != -1:
                            totalORBProfitPercent = totalORBProfitPercent - diffPercent(curORB.slPrice, curORB.entryPrice) * (1.0 - totalProfitTaken)
                            if totalProfitTaken == 0.0:
                                unsuccessfulTrades = unsuccessfulTrades + 1
                    if isSuccess:
                        successfulTrades = successfulTrades + 1

        table.merge_cells(backtestDisplay, 0, 0, 1, 0)
        table.cell(backtestDisplay, 0, 0, 'ORB Backtesting', text_color=color.white, bgcolor=orbColor)

        table.cell(backtestDisplay, 0, 1, 'Total Days', text_color=color.white, bgcolor=orbColor)
        table.cell(backtestDisplay, 1, 1, string.tostring(array.size(orbList)), text_color=color.white, bgcolor=orbColor)

        table.cell(backtestDisplay, 0, 2, 'Wins', text_color=color.white, bgcolor=orbColor)
        table.cell(backtestDisplay, 1, 2, string.tostring(successfulTrades), text_color=color.white, bgcolor=orbColor)

        table.cell(backtestDisplay, 0, 3, 'Losses', text_color=color.white, bgcolor=orbColor)
        table.cell(backtestDisplay, 1, 3, string.tostring(unsuccessfulTrades), text_color=color.white, bgcolor=orbColor)

        table.cell(backtestDisplay, 0, 4, 'Winrate', text_color=color.white, bgcolor=orbColor)
        table.cell(backtestDisplay, 1, 4, string.tostring(100.0 * (successfulTrades / (successfulTrades + unsuccessfulTrades)), '#.##') + '%', text_color=color.white, bgcolor=orbColor)

        table.cell(backtestDisplay, 0, 5, 'Average Profit', text_color=color.white, bgcolor=orbColor)
        table.cell(backtestDisplay, 1, 5, string.tostring(totalORBProfitPercent / (successfulTrades + unsuccessfulTrades), '#.##') + '%', text_color=color.white, bgcolor=orbColor)

        table.cell(backtestDisplay, 0, 6, 'Total Profit', text_color=color.white, bgcolor=orbColor)
        table.cell(backtestDisplay, 1, 6, string.tostring(totalORBProfitPercent, '#.##') + '%', text_color=color.white, bgcolor=orbColor)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
