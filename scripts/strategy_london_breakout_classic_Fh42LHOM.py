"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_import import shadowed_namespace
from pynecore.lib import (
    bar_index, bgcolor, box, close, color, high, hour, input, low, math, na,
    open, plot, script, strategy, syminfo, ta, time, timeframe, timestamp
)
from pynecore.types import Box, Persistent, Series
import lib.TradingView.ta.v5 as ta__ren____lib


ta__ren__ = shadowed_namespace(ta__ren____lib, ta)


@script.strategy(title='London BreakOut Classic', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    startDate=input.int(title='Start Date', defval=1, minval=1, maxval=31),
    startMonth=input.int(title='Start Month', defval=1, minval=1, maxval=12),
    startYear=input.int(title='Start Year', defval=2022, minval=1800, maxval=2100),
    endDate=input.int(title='End Date', defval=1, minval=1, maxval=31),
    endMonth=input.int(title='End Month', defval=7, minval=1, maxval=12),
    endYear=input.int(title='End Year', defval=2024, minval=1800, maxval=2100),
    FilterTradeTime=input.bool(defval=True, title='Filter Entrytime'),
    rangemalen=input(20, title='Avg Length Range'),
    rangemult=input(2, title='Avg Multiplier Range'),
    sessionTime=input.session('0000-0655', title='Session time Tokyo'),
    sessionZone=input.string('UTC', title='Session time zone'),
    boxBorderSize=input.int(2, title='Box border size', minval=0),
    upBoxColor=input.color(color.new(color.green, 85), title='Up box'),
    upBorderColor=input.color(color.green, title='Up border'),
    downBoxColor=input.color(color.new(color.red, 85), title='Down box'),
    downBorderColor=input.color(color.red, title='Down border'),
    CRV_Faktor=input.float(title='CRV', minval=0, maxval=10, defval=1.0, step=0.1)
):
    def InSession(sessionTime, sessionTimeZone = syminfo.timezone):
        return not na(time(timeframe.period, sessionTime, sessionTimeZone))

    sessionHighPrice: Persistent[float] = 0.0
    sessionLowPrice: Persistent[float] = 0.0
    sessionOpenPrice: Persistent[float] = 0.0
    sessionBox: Persistent[Box] = na(Box)
    inSession: Series = InSession(sessionTime, sessionZone) and timeframe.isintraday
    sessionStart = inSession and (not inSession[1])
    SessionEnd = inSession[1] and (not inSession)
    if sessionStart:
        sessionHighPrice = high
        sessionLowPrice = low
        sessionOpenPrice = open
    elif inSession:
        sessionHighPrice = math.max(sessionHighPrice, high)
        sessionLowPrice = math.min(sessionLowPrice, low)
    if sessionStart:
        sessionBox = box.new(left=bar_index, top=na, right=na, bottom=na, border_width=boxBorderSize)
    if inSession:
        box.set_top(sessionBox, sessionHighPrice)
        box.set_bottom(sessionBox, sessionLowPrice)
        box.set_right(sessionBox, bar_index + 1)
        if close > sessionOpenPrice:
            box.set_bgcolor(sessionBox, upBoxColor)
            box.set_border_color(sessionBox, upBorderColor)
        else:
            box.set_bgcolor(sessionBox, downBoxColor)
            box.set_border_color(sessionBox, downBorderColor)
    inDateRange = time >= timestamp(syminfo.timezone, startYear, startMonth, startDate, 0, 0) and time < timestamp(syminfo.timezone, endYear, endMonth, endDate, 0, 0)
    Minpreday = ta__ren__.valuewhen(SessionEnd, sessionLowPrice, 0)
    Maxpreday = ta__ren__.valuewhen(SessionEnd, sessionHighPrice, 0)
    Lastbarinbox = ta__ren__.valuewhen(SessionEnd, close, 0)
    __block_result__ = na
    if high >= Maxpreday:
        __block_result__ = 1
    else:
        __block_result__ = 0
    Conditionlong = __block_result__
    __block_result_1__ = na
    if low <= Minpreday:
        __block_result_1__ = 1
    else:
        __block_result_1__ = 0
    Conditionshort = __block_result_1__
    Stoploss = (Maxpreday - Minpreday) / 2 + Minpreday
    plot(Stoploss, title='Entryline', color=color.rgb(231, 10, 10), style=plot.style_line)
    lastEntryPrice = strategy.opentrades.entry_price(strategy.opentrades - 1)
    Tp_Long: float = 0.0
    Tp_Long = (lastEntryPrice - Stoploss) * CRV_Faktor + lastEntryPrice
    Tp_Short: float = 0.0
    Tp_Short = lastEntryPrice - (Stoploss - lastEntryPrice) * CRV_Faktor
    entry_long_before: Persistent[bool] = False
    entry_long_before = False if sessionStart else entry_long_before
    entry_short_before: Persistent[bool] = False
    entry_short_before = False if sessionStart else entry_short_before
    tradinghours = time(timeframe.period, '0700-1600', 'UTC')
    time_condition = not na(tradinghours) if FilterTradeTime else True
    bgcolor(color.rgb(73, 196, 78, 90) if not na(tradinghours) else na)
    if inDateRange and time_condition and (Conditionshort == 1) and (not entry_short_before) and (not entry_long_before):
        strategy.entry('Enter short', strategy.short, comment='entry short')
        entry_short_before = True
    strategy.exit('Exit short', from_entry='Enter short', comment_profit='TP Short', comment_loss='SL Short', limit=Tp_Short, stop=Stoploss)
    if hour == 0:
        strategy.close(id='Enter short', comment='Exit Time')
    if not time_condition:
        strategy.cancel('Enter short')
    if inDateRange and time_condition and (Conditionlong == 1) and (not entry_long_before) and (not entry_short_before):
        strategy.entry('Enter long', strategy.long, comment='entry long')
        entry_long_before = True
    strategy.exit('Exit long', from_entry='Enter long', comment_profit='TP Long', comment_loss='SL Long', limit=Tp_Long, stop=Stoploss)
    if hour == 0:
        strategy.close(id='Enter long', comment='Exit Time')
    if not time_condition:
        strategy.cancel('Enter long')
    if not inDateRange:
        strategy.close_all()


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
