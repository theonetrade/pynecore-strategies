"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    close, color, high, input, low, math, na, plot, script, strategy, string,
    syminfo, ta
)
from pynecore.types import PersistentSeries, Series


@script.strategy(shorttitle='Trend Surfers - Breakout', title='Trend Surfers - Premium Breakout', overlay=True, calc_on_every_tick=False, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type='percent', commission_value=0.04, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    maxriskval=input.float(2, 'Max % risk', tooltip='Risk % over total equity / Position', group='Risk Management'),
    pairnumber=input.int(title='How many pairs', defval=1, tooltip='How many pairs are you trading with the strategy?', group='Risk Management'),
    highPeriod=input.int(title='Highest High Period', defval=168, tooltip='Highest High of X bars - This will trigger a Long Entry when close is above. (Thin Green Line)', group='Entry Condition'),
    lowPeriod=input.int(title='Lowest Low Period', defval=168, tooltip='Lowest low of X bars - This will trigger a Short Entry when close is under. (Thin Red Line)', group='Entry Condition'),
    trailingAtrPeriod=input.int(title='Trailing ATR Pediod', defval=10, tooltip='Average True Range for the Trailing Stop. (Thick Green Line) ', group='Exit Condition'),
    trailingAtrMultiplier=input.float(title='Trailing ATR Multiplier', defval=8, group='Exit Condition'),
    fixAtrPeriod=input.int(title='Fix ATR Pediod', defval=10, tooltip='Average True Range for the Fix Stoloss. (Thick Yellow Line)', group='Exit Condition'),
    fixAtrMultiplier=input.float(title='Fix ATR Multiplier', defval=2, group='Exit Condition')
):
    pair = syminfo.basecurrency + syminfo.currency
    highestHigh = inline_series(ta.highest(high, highPeriod), 1)
    lowestLow = inline_series(ta.lowest(low, lowPeriod), 1)
    trailingAtr = ta.atr(trailingAtrPeriod) * trailingAtrMultiplier
    longCondition = ta.crossover(close, highestHigh)
    shortCondition = ta.crossunder(close, lowestLow)
    fixAtr: Series = ta.atr(fixAtrPeriod) * fixAtrMultiplier
    stopvaluelong = close[1] - fixAtr[1]
    stopvalueshort = close[1] + fixAtr[1]
    maxpossize = strategy.equity / close
    positionsizelong = maxriskval / 100 * strategy.equity / (close - stopvaluelong)
    stopperclong = (close - stopvaluelong) / close * 100
    leveragelong = math.max(1, math.ceil(positionsizelong / maxpossize)) * 2
    posperclong = positionsizelong * close / strategy.equity * 100 / leveragelong / pairnumber
    realposlong = posperclong / 100 * strategy.equity * leveragelong / close
    positionsizeshort = maxriskval / 100 * strategy.equity / (stopvalueshort - close)
    stoppercshort = (close - stopvalueshort) / close * 100
    leverageshort = math.max(1, math.ceil(positionsizeshort / maxpossize)) * 2
    pospercshort = positionsizeshort * close / strategy.equity * 100 / leverageshort / pairnumber
    realposshort = pospercshort / 100 * strategy.equity * leverageshort / close
    entry_long_message = '\nGo Long for ' + pair + 'NOW!' + '\nPosition Size % =' + string.tostring(posperclong) + '\nLeverage' + string.tostring(leveragelong) + '\nStoploss Price =' + string.tostring(stopvaluelong) + '\nClose any Short position that are open for ' + pair + '!' + '\n\nVisit TrendSurfersSignals.com' + '\nFor automated premium signals (FREE)'
    entry_short_message = '\nGo Short for ' + pair + 'NOW!' + '\nPosition Size % =' + string.tostring(pospercshort) + '\nLeverage' + string.tostring(leverageshort) + '\nStoploss Price =' + string.tostring(stopvalueshort) + '\nClose any Long position that are open for ' + pair + '!' + '\n\nVisit TrendSurfersSignals.com' + '\nFor automated premium signals (FREE)'
    exit_short_message = '\nExit Short for ' + pair + 'NOW!' + '\n\nVisit TrendSurfersSignals.com' + '\nFor automated premium signals (FREE)'
    exit_long_message = '\nExit Long for ' + pair + 'NOW!' + '\n\nVisit TrendSurfersSignals.com' + '\nFor automated premium signals (FREE)'
    if longCondition:
        strategy.entry('Long', strategy.long, stop=highestHigh, comment='Long', qty=realposlong, alert_message=entry_long_message)
    if shortCondition:
        strategy.entry('Short', strategy.short, stop=lowestLow, comment='Short', qty=realposshort, alert_message=entry_short_message)
    longTrailing = close - trailingAtr
    shortTrailing = close + trailingAtr
    longTrailingStop: PersistentSeries[float] = 0.0
    shortTrailingStop: PersistentSeries[float] = 999999.9
    trailingStopLine: float = 0.0
    trailingStopLine = na
    fixedStopLine: Series[float] = 0.0
    fixedStopLine = na
    inTrade: PersistentSeries[int] = 0
    if longCondition or shortCondition:
        if 0 == inTrade:
            if longCondition:
                inTrade = 1
            else:
                inTrade = -1
    if 1 == inTrade and (shortCondition or low <= math.max(fixedStopLine[1], longTrailingStop)):
        inTrade = 0
    if -1 == inTrade and (longCondition or high >= math.min(fixedStopLine[1], shortTrailingStop)):
        inTrade = 0
    __block_result__ = na
    if 1 == inTrade:
        stopValue = longTrailing
        __block_result__ = math.max(stopValue, longTrailingStop[1])
    else:
        __block_result__ = 0
    longTrailingStop = __block_result__
    __block_result_1__ = na
    if -1 == inTrade:
        stopValue = shortTrailing
        __block_result_1__ = math.min(stopValue, shortTrailingStop[1])
    else:
        __block_result_1__ = 999999
    shortTrailingStop = __block_result_1__
    firstPrice: float = 0.0
    firstFixAtr: float = 0.0
    firstPrice = na
    firstFixAtr = na
    if 0 != inTrade:
        firstPrice = ta.valuewhen(inTrade != inTrade[1] and 0 != inTrade, close, 0)
        firstFixAtr = ta.valuewhen(inTrade != inTrade[1] and 0 != inTrade, fixAtr, 0)
        if 1 == inTrade:
            fixedStopLine = firstPrice - firstFixAtr
            trailingStopLine = longTrailingStop
        else:
            fixedStopLine = firstPrice + firstFixAtr
            trailingStopLine = shortTrailingStop
    if strategy.position_size > 0:
        strategy.exit(id='L Stop', stop=math.max(fixedStopLine, longTrailingStop), alert_message=exit_long_message)
    if strategy.position_size < 0:
        strategy.exit(id='S Stop', stop=math.min(fixedStopLine, shortTrailingStop), alert_message=exit_short_message)
    plot(highestHigh, color=color.new(color.green, 0), linewidth=1, title='Highest High')
    plot(lowestLow, color=color.new(color.red, 0), linewidth=1, title='Lowest Low')
    plot(trailingStopLine, color=color.new(color.lime, 0), linewidth=2, offset=1, title='Trailing Stop')
    plot(fixedStopLine, color=color.new(color.orange, 0), linewidth=2, offset=1, title='Fixed Stop')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)