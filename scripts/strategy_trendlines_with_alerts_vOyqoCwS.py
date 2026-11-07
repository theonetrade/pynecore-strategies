"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barstate, close, color, high, input, location, low, math, na, open, plot,
    plotshape, script, shape, size, strategy, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy('TrendLines with Alerts', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    length1=input(20),
    check=input(9),
    tp=input(0.2, title='Take Profit'),
    sl=input(0.2, title='Stop Loss'),
    tradeType=input.string('BOTH', title='What trades should be taken : ', options=('LONG', 'SHORT', 'BOTH', 'NONE')),
    slPoints=input.int(defval=0, title='Initial Stop Loss Points (zero to disable)', minval=0),
    tpPoints=input.int(defval=0, title='Initial Target Profit Points (zero for disable)', minval=0),
    testStartYear=input.int(2019, 'Backtest Start Year', minval=1980),
    testStartMonth=input.int(1, 'Backtest Start Month', minval=1, maxval=12),
    testStartDay=input.int(1, 'Backtest Start Day', minval=1, maxval=31),
    testStopYear=input.int(9999, 'Backtest Stop Year', minval=1980),
    testStopMonth=input.int(12, 'Backtest Stop Month', minval=1, maxval=12),
    testStopDay=input.int(31, 'Backtest Stop Day', minval=1, maxval=31)
):
    u: Series[float] = 0.0
    u = u[1]
    l: Series[float] = 0.0
    l = l[1]
    y: Series[float] = 0.0
    y = y[1]
    yl: Series[float] = 0.0
    yl = yl[1]
    angle: Series[float] = 0.0
    angle = angle[1]
    anglel: Series[float] = 0.0
    anglel = anglel[1]
    highest_1 = ta.highest(length1)
    highest_2: Series = ta.highest(length1)
    barssince_1 = ta.barssince(barstate.isfirst)
    if ta.highest(length1) == high[check] and highest_1 == highest_2[check] and (barssince_1 > check):
        u = high[check]
    lowest_1 = ta.lowest(length1)
    lowest_2: Series = ta.lowest(length1)
    barssince_2 = ta.barssince(barstate.isfirst)
    if ta.lowest(length1) == low[check] and lowest_1 == lowest_2[check] and (barssince_2 > check):
        l = low[check]
    p: Series = math.round(ta.barssince(u == high[check]))
    pl: Series = math.round(ta.barssince(l == low[check]))
    barssince_3 = ta.barssince(barstate.isfirst)
    if p == 0 and barssince_3 > check:
        y = high[math.abs(p[1] + 1 + check)]
    barssince_4 = ta.barssince(barstate.isfirst)
    if pl == 0 and barssince_4 > check:
        yl = low[math.abs(pl[1] + 1 + check)]
    if p == 0:
        angle = (u - y) / p[1]
    if pl == 0:
        anglel = (l - yl) / pl[1]
    uppertrend: Series = u + p * angle
    lowertrend: Series = l + pl * anglel
    __block_result__ = na
    if ta.barssince(barstate.isfirst) > check:
        __block_result__ = uppertrend[check] + angle[check] * check * 2
    extendup = __block_result__
    __block_result_1__ = na
    if ta.barssince(barstate.isfirst) > check:
        __block_result_1__ = lowertrend[check] + anglel[check] * check * 2
    extenddown = __block_result_1__
    plot(lowertrend, color=color.new(color.green, 30), offset=-check)
    plot(extenddown, color=color.new(color.green, 100))
    plot(uppertrend, color=color.new(color.red, 30), offset=-check)
    plot(extendup, color=color.new(color.red, 100))
    l1 = lowertrend
    l2 = extenddown
    u1 = uppertrend
    u2 = extendup
    l2sell = ta.crossunder(high, l2)
    u2buy = ta.crossover(low, u2)
    buy1 = low <= lowertrend and open > lowertrend and (high > lowertrend) and (close > lowertrend)
    buy2 = low <= extenddown and open > extenddown and (high > extenddown) and (close > extenddown)
    buy = buy1 or buy2 or u2buy
    plotshape(series=buy, title='Buy', style=shape.triangleup, size=size.tiny, color=color.new(color.lime, 0), location=location.belowbar)
    sell1 = high >= uppertrend and open < uppertrend and (low < uppertrend) and (close < uppertrend)
    sell2 = high >= extendup and open < extendup and (low < extendup) and (close < extendup)
    sell = sell1 or sell2 or l2sell
    plotshape(series=sell, title='Sell', style=shape.triangledown, size=size.tiny, color=color.new(color.red, 0), location=location.abovebar)
    longCond = buy
    shortCond = sell
    tpbuyval = ta.valuewhen(buy, close, 1) + tp / 100 * ta.valuewhen(buy, close, 1)
    tpsellval = ta.valuewhen(sell, close, 1) - tp / 100 * ta.valuewhen(sell, close, 1)
    slbuyval = ta.valuewhen(buy, close, 0) - sl / 100 * ta.valuewhen(buy, close, 0)
    slsellval = ta.valuewhen(sell, close, 0) + sl / 100 * ta.valuewhen(sell, close, 0)
    testPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, 0, 0)
    testPeriodStop = timestamp(testStopYear, testStopMonth, testStopDay, 0, 0)
    def testPeriod():
        return True if time >= testPeriodStart and time <= testPeriodStop else False

    TP = tpPoints if tpPoints > 0 else na
    SL = slPoints if slPoints > 0 else na
    if testPeriod() and tradeType != 'NONE':
        if longCond == True and tradeType != 'SHORT':
            strategy.entry('long', strategy.long)
        if shortCond == True and tradeType != 'LONG':
            strategy.entry('short', strategy.short)
        if shortCond == True and tradeType == 'LONG':
            strategy.close('long')
        if longCond == True and tradeType == 'SHORT':
            strategy.close('short')
        strategy.exit('XL', from_entry='long', profit=tpbuyval, loss=slbuyval)
        strategy.exit('XS', from_entry='short', profit=tpsellval, loss=slsellval)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
