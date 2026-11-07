"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, input, location, math, na, plotshape, script, shape, size,
    strategy, time, timestamp
)
from pynecore.types import Persistent


@script.strategy('TRAILING STOP LOSS TO LONG AND SHORT', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    backTestSectionFrom=input(title='═══════════════ FROM ═══════════════', defval=True),
    FromMonth=input.int(defval=1, title='Month', minval=1),
    FromDay=input.int(defval=1, title='Day', minval=1),
    FromYear=input.int(defval=2014, title='Year', minval=2014),
    backTestSectionTo=input(title='════════════════ TO ════════════════', defval=True),
    ToMonth=input.int(defval=31, title='Month', minval=1),
    ToDay=input.int(defval=12, title='Day', minval=1),
    ToYear=input.int(defval=9999, title='Year', minval=2014),
    parameterSection=input(title='═════════════ STRATEGY ═════════════', defval=True),
    positionType=input.string(defval='LONG', title='Position Type', options=('LONG', 'SHORT')),
    initialStopLossPercent=input.float(defval=3.0, minval=0.0, title='Initial Stop Loss')
):
    def hasEntryLongConditional():
        return 1 == 1

    def hasCloseLongConditional():
        return 1 != 1

    def backTestPeriod():
        return time > timestamp(FromYear, FromMonth, FromDay, 0, 0) and time < timestamp(ToYear, ToMonth, ToDay, 23, 59)

    stopLossPercent = initialStopLossPercent * -1 if positionType == 'LONG' else initialStopLossPercent
    entryPrice: Persistent[float] = 0.0
    updatedEntryPrice: Persistent[float] = 0.0
    stopLossPrice: Persistent[float] = 0.0
    def hasOpenTrade():
        return strategy.opentrades != 0

    def notHasOpenTrade():
        return strategy.opentrades == 0

    def strategyClose():
        __block_result__ = na
        if positionType == 'LONG':
            __block_result_1__ = na
            if True:
                __block_result_1__ = strategy.close('LONG')
            __block_result__ = __block_result_1__
        else:
            __block_result_2__ = na
            if True:
                __block_result_2__ = strategy.close('SHORT')
            __block_result__ = __block_result_2__
        return __block_result__

    def strategyOpen():
        __block_result_3__ = na
        if positionType == 'LONG':
            __block_result_4__ = na
            if True:
                __block_result_4__ = strategy.entry('LONG', strategy.long)
            __block_result_3__ = __block_result_4__
        else:
            __block_result_5__ = na
            if True:
                __block_result_5__ = strategy.entry('SHORT', strategy.short)
            __block_result_3__ = __block_result_5__
        return __block_result_3__

    def isLong():
        return True if positionType == 'LONG' else False

    def isShort():
        return True if positionType == 'SHORT' else False

    backTestPeriod_1 = backTestPeriod()
    if isLong() and backTestPeriod_1:
        crossedStopLoss = close <= stopLossPrice
        hasCloseLongConditional_1 = hasCloseLongConditional()
        terminateOperation = hasOpenTrade() and (crossedStopLoss or hasCloseLongConditional_1)
        if terminateOperation:
            entryPrice = 0.0
            updatedEntryPrice = entryPrice
            stopLossPrice = 0.0
            strategyClose()
        hasEntryLongConditional_1 = hasEntryLongConditional()
        startOperation = notHasOpenTrade() and hasEntryLongConditional_1
        if startOperation:
            entryPrice = close
            updatedEntryPrice = entryPrice
            stopLossPrice = entryPrice + entryPrice * stopLossPercent / 100
            strategyOpen()
        strategyPercentege = (close - updatedEntryPrice) / updatedEntryPrice * 100.0
        rideUpStopLoss = hasOpenTrade() and strategyPercentege > 1
        if isLong() and rideUpStopLoss:
            stopLossPercent = stopLossPercent + strategyPercentege - 1.0
            newStopLossPrice = updatedEntryPrice + updatedEntryPrice * stopLossPercent / 100
            stopLossPrice = math.max(stopLossPrice, newStopLossPrice)
            updatedEntryPrice = stopLossPrice
    backTestPeriod_2 = backTestPeriod()
    if isShort() and backTestPeriod_2:
        crossedStopLoss = close >= stopLossPrice
        hasCloseLongConditional_1 = hasCloseLongConditional()
        terminateOperation = hasOpenTrade() and (crossedStopLoss or hasCloseLongConditional_1)
        if terminateOperation:
            entryPrice = 0.0
            updatedEntryPrice = entryPrice
            stopLossPrice = 0.0
            strategyClose()
        hasEntryLongConditional_1 = hasEntryLongConditional()
        startOperation = notHasOpenTrade() and hasEntryLongConditional_1
        if startOperation:
            entryPrice = close
            updatedEntryPrice = entryPrice
            stopLossPrice = entryPrice + entryPrice * stopLossPercent / 100
            strategyOpen()
        strategyPercentege = (close - updatedEntryPrice) / updatedEntryPrice * 100.0
        rideDownStopLoss = hasOpenTrade() and strategyPercentege < -1
        if rideDownStopLoss:
            stopLossPercent = stopLossPercent + strategyPercentege + 1.0
            newStopLossPrice = updatedEntryPrice + updatedEntryPrice * stopLossPercent / 100
            stopLossPrice = math.min(stopLossPrice, newStopLossPrice)
            updatedEntryPrice = stopLossPrice
    entryPricePlotConditinal = na if entryPrice == 0.0 else entryPrice
    trailingStopLossPlotConditional = na if stopLossPrice == 0.0 else stopLossPrice
    plotshape(entryPricePlotConditinal, title='Entry Price', color=color.new(color.blue, 0), style=shape.circle, location=location.absolute, size=size.tiny)
    plotshape(trailingStopLossPlotConditional, title='Stop Loss', color=color.new(color.red, 0), style=shape.circle, location=location.absolute, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
