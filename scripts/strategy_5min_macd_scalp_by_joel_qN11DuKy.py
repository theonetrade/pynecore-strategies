"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barstate, close, color, display, input, math, na, plot, position,
    request, script, strategy, string, ta, table, time, timestamp
)
from pynecore.types import Persistent, Series, Table
import lib.ZenAndTheArtOfTrading.ZenLibrary.v2 as l_zen

g_strategy: str = 'Strategy'
g_pause: str = 'Pause trades'
g_ema: str = 'EMAs trend'
g_macd: str = 'MACD settings'
g_hist: str = 'Histogram peak finder'
g_rsi: str = 'RSI filter'
g_additional: str = 'Pullback filter'
g_tester: str = 'Back tester table'
i_3Commas: str = '3Commas bot settings'


@script.strategy('5min MACD scalp by Joel (3commas)', shorttitle='5m MACD scalp', overlay=True, margin_long=100, margin_short=100, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    i_chkLong=input.bool(True, title='Long', inline='1', group=g_strategy),
    i_chkShort=input.bool(True, title='Short', inline='1', group=g_strategy),
    i_startTime=input.time(title='Start Date', defval=timestamp('01 Jan 2020 00:00 +0100'), group=g_strategy, tooltip='Date & time to begin trading from'),
    i_endTime=input.time(title='End Date', defval=timestamp('1 Jan 2099 00:00 +0100'), group=g_strategy, tooltip='Date & time to stop trading'),
    __input_4__=input.float(title='Long TP (%)', minval=0.0, step=0.1, defval=0.5, inline='2', group=g_strategy),
    __input_5__=input.float(title='Short TP (%)', minval=0.0, step=0.1, defval=0.5, inline='3', group=g_strategy),
    __input_6__=input.float(title='Long SL (%)', minval=0.0, step=0.1, defval=0.4, inline='2', group=g_strategy),
    __input_7__=input.float(title='Short SL (%)', minval=0.0, step=0.1, defval=0.4, inline='3', group=g_strategy),
    i_tradePause=input.int(title='For how many bars?', defval=0, minval=0, group=g_pause, tooltip='Pauses trades for X bars after a closed trade\n0 = OFF'),
    i_tradePauseLoss=input.bool(title='Only loosing trades', defval=True, inline='4', group=g_pause),
    i_tradeLossNum=input.int(title='| How much?', defval=1, minval=1, group=g_pause, inline='4', tooltip='Number of loosing trades in a row'),
    i_emaOpt=input.string(title='Trend type', defval='Ema cross', options=('Ema cross', 'Ema slow', 'Ema fast'), group=g_ema, tooltip='Ema cross - trend based on ema crosses, eg. fast above slow = long and vice versa,\nEma slow/fast - trend based on whether the close price is above/under selected ema'),
    i_emaFast=input.int(title='Ema fast lenght', defval=50, step=5, group=g_ema),
    i_emaSlow=input.int(title='Ema slow lenght', defval=200, step=5, group=g_ema),
    i_emaTrendBarsBack=input.int(title='Valid cross?', defval=350, step=5, tooltip='How many bars back is the cross still valid?\nWhen some of the Emas is selected as an Trend type then it counts the bars since the close price crossed above the selected ema', group=g_ema),
    i_macdRes=input.timeframe(title='MACD resolution', defval='', group=g_macd),
    i_macdFastLen=input.int(title='Fast Length', minval=1, defval=12, group=g_macd),
    i_macdSlowLen=input.int(title='Slow Length', minval=1, defval=26, group=g_macd),
    i_macdSignalLen=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9, group=g_macd),
    i_histMin=input.float(title='Min histogram value', defval=0.0, minval=0.0, group=g_hist, tooltip='Minimum for a positive/negative histogram value that is taken into account.\nSet to zero if you want to turn it off.'),
    i_histHighestLookback=input.int(title='Lookback period', defval=10, minval=1, group=g_hist),
    i_useHistChk=input.bool(False, title='Compare with histogram average?', group=g_hist, tooltip='Highest/Lowest hist bar - Current histogram value must be greater than 100% + X% times the average histogram'),
    i_histAvgLookback=input.int(title='Avg histogram lenght', defval=50, minval=1, step=5, tooltip='Length of the histogram average, similar to MA length', group=g_hist),
    __input_23__=input.int(title='% above avg', defval=50, minval=1, step=5, tooltip='Histogram positive/value must be above the average * %', group=g_hist),
    i_rsiChk=input.bool(False, 'Use RSI Filter', group=g_rsi),
    i_rsiRes=input.timeframe('', 'TimeFrame', group=g_rsi),
    i_rsiLen=input.int(14, 'Lenght', group=g_rsi),
    i_rsiMinLong=input.float(0.0, 'Min for Long', minval=0.0, maxval=100.0, step=0.5, group=g_rsi, inline='6'),
    i_rsiMaxLong=input.float(70.0, 'Max for Long', minval=0.0, maxval=100.0, step=0.5, group=g_rsi, inline='6'),
    i_rsiMinShort=input.float(30.0, 'Min for Short', minval=0.0, maxval=100.0, step=0.5, group=g_rsi, inline='7'),
    i_rsiMaxShort=input.float(100.0, 'Max for Short', minval=0.0, maxval=100.0, step=0.5, group=g_rsi, inline='7'),
    i_rsiDirectChk=input.bool(False, 'RSI direction confirmation', group=g_rsi, tooltip='Long only if its supported by rising RSI and Short only if its supported by falling RSI\nWorks only if Use RSI is ON'),
    i_rsiDirectLen=input.int(1, 'Bars back for direction', minval=1, group=g_rsi, tooltip='Lookback period for RSI values'),
    i_usePullbackChk=input.bool(False, title='Use Pullback filter', group=g_additional, tooltip='This aims to chatch a possible swing low/high for a better quality position\nFor a long position it checks how many candles were in the opposite direction, so you don\'t enter the trade when it\'s been going up for a long time and vice versa'),
    i_pullbackCount=input.int(title='Lookback period', defval=2, minval=1, group=g_additional),
    i_pullbackBigger=input.int(title='More than', defval=2, minval=1, group=g_additional, tooltip='How many candles should be in the opposite direction?\nCan\'t be bigger than the lookback period'),
    i_drawTester=input.bool(title='Show back tester', defval=True, group=g_tester, tooltip='Turn on/off inbuilt backtester display', inline='backtester1'),
    i_testerPosition=input.string(title='', defval='Top right', options=('Top right', 'Top left', 'Bottom right', 'Bottom left'), group=g_tester, tooltip='Position of the backtester table', inline='backtester1'),
    i_rr=input.float(title='R:R', defval=1.0, group=g_tester, tooltip='Risk:Reward profile'),
    startBalance=input.float(title='Starting Balance', defval=100.0, group=g_tester, tooltip='Your starting balance for the custom inbuilt tester system'),
    riskPerTrade=input.float(title='Risk Per Trade', defval=1.0, group=g_tester, tooltip='Your desired % risk per trade (as a whole number)'),
    i_useComments=input.bool(False, 'Show 3Commas bot comments', group=i_3Commas),
    i_botIDLong=input(title='Long Bot ID', defval='', group=i_3Commas),
    i_botIDShort=input(title='Short Bot ID', defval='', group=i_3Commas),
    i_tokenID=input(title='Email Token', defval='', group=i_3Commas)
):
    i_longProfitPerc = __input_4__ * 0.01
    i_shortProfitPerc = __input_5__ * 0.01
    i_longStopPerc = __input_6__ * 0.01
    i_shortStopPerc = __input_7__ * 0.01
    i_aboveHist = __input_23__ * 0.01 + 1
    strategy.risk.allow_entry_in(strategy.direction.all if i_chkLong and i_chkShort else strategy.direction.long if i_chkLong else strategy.direction.short)
    c_dateFilter = time >= i_startTime and time <= i_endTime
    c_emaFast = ta.ema(close, i_emaFast)
    c_emaSlow = ta.ema(close, i_emaSlow)
    c_emaCrossBull = ta.crossover(c_emaFast if i_emaOpt == 'Ema cross' else close, c_emaFast if i_emaOpt == 'Ema fast' else c_emaSlow)
    c_emaCrossBear = ta.crossunder(c_emaFast if i_emaOpt == 'Ema cross' else close, c_emaFast if i_emaOpt == 'Ema fast' else c_emaSlow)
    c_emaAbove = c_emaFast >= c_emaSlow if i_emaOpt == 'Ema cross' else close > c_emaSlow if i_emaOpt == 'Ema slow' else close > c_emaFast
    c_emaUnder = c_emaFast < c_emaSlow if i_emaOpt == 'Ema cross' else close < c_emaSlow if i_emaOpt == 'Ema slow' else close < c_emaFast
    c_crossBarsBackBull = ta.barssince(c_emaCrossBull)
    c_crossBarsBackBear = ta.barssince(c_emaCrossBear)
    def f_rpSecurity(_symbol, _res, _src: Series):
        return request.security(_symbol, _res, _src[1 if barstate.isrealtime else 0])

    c_hist: Series
    _, _, c_hist = ta.macd(f_rpSecurity('', i_macdRes, close), i_macdFastLen, i_macdSlowLen, i_macdSignalLen)
    c_histBear = math.sum((c_hist[1] if barstate.isrealtime else c_hist) if c_hist > 0 else 0, i_histAvgLookback)
    c_histBull = math.sum(math.abs(c_hist[1] if barstate.isrealtime else c_hist) if c_hist < 0 else 0, i_histAvgLookback)
    c_histBearAvg = c_histBear / math.sum(1 if c_hist > 0 else 0, i_histAvgLookback)
    c_histBullAvg = c_histBull / math.sum(1 if c_hist < 0 else 0, i_histAvgLookback)
    c_rsiSrc = f_rpSecurity('', i_rsiRes, close)
    c_rsi = ta.rsi(c_rsiSrc, i_rsiLen)
    c_histMinLong = math.abs(c_hist) > i_histMin
    c_histMinShort = c_hist > i_histMin
    c_aboveHistAvgLong = math.abs(c_hist) >= i_aboveHist * c_histBullAvg
    c_aboveHistAvgShort = c_hist >= i_aboveHist * c_histBearAvg
    highestbars_1: Series = ta.highestbars(c_hist, i_histHighestLookback)
    c_histHighest = ta.highestbars(c_hist, i_histHighestLookback) == 0 or highestbars_1[1] == 0
    lowestbars_1: Series = ta.lowestbars(math.abs(c_hist), i_histHighestLookback)
    c_histLowest = ta.highestbars(math.abs(c_hist), i_histHighestLookback) == 0 or lowestbars_1[1] == 0
    c_pullbackCountGreen = l_zen.getPullbackBarCount(i_pullbackCount, 1)
    c_pullbackCountRed = l_zen.getPullbackBarCount(i_pullbackCount, -1)
    c_rsiRising = ta.rising(c_rsi, i_rsiDirectLen)
    c_rsiFalling = ta.falling(c_rsi, i_rsiDirectLen)
    c_sinceLastTrade = ta.barssince(strategy.closedtrades > strategy.closedtrades[1])
    c_sinceLastLossTrade = ta.barssince(strategy.losstrades > strategy.losstrades[1])
    c_countLosstrades: Persistent[int] = 0
    if strategy.losstrades > strategy.losstrades[1]:
        c_countLosstrades = c_countLosstrades + 1
    elif strategy.wintrades > strategy.wintrades[1]:
        c_countLosstrades = 0
    elif c_countLosstrades == i_tradeLossNum and c_sinceLastLossTrade > i_tradePause:
        c_countLosstrades = 0
    elif c_emaCrossBull or c_emaCrossBear:
        c_countLosstrades = 0
    c_longCondition = c_dateFilter and ((c_countLosstrades < i_tradeLossNum if i_tradePause != 0 else True) and (c_sinceLastLossTrade >= i_tradePause if strategy.losstrades != 0 else True) if i_tradePauseLoss else c_sinceLastTrade >= i_tradePause if strategy.closedtrades != 0 else True) and c_emaAbove and (c_crossBarsBackBull <= i_emaTrendBarsBack) and (c_rsi >= i_rsiMinLong and c_rsi <= i_rsiMaxLong and (c_rsiRising if i_rsiDirectChk else True) if i_rsiChk else True) and (c_histLowest if c_hist < 0 and c_histMinLong else False) and (c_aboveHistAvgLong if i_useHistChk else True) and (c_pullbackCountRed >= i_pullbackBigger if i_usePullbackChk else True)
    c_shortCondition = c_dateFilter and ((c_countLosstrades < i_tradeLossNum if i_tradePause != 0 else True) and (c_sinceLastLossTrade >= i_tradePause if strategy.losstrades != 0 else True) if i_tradePauseLoss else c_sinceLastTrade >= i_tradePause if strategy.closedtrades != 0 else True) and c_emaUnder and (c_crossBarsBackBear <= i_emaTrendBarsBack) and (c_rsi >= i_rsiMinShort and c_rsi <= i_rsiMaxShort and (c_rsiFalling if i_rsiDirectChk else True) if i_rsiChk else True) and (c_histHighest if c_hist >= 0 and c_histMinShort else False) and (c_aboveHistAvgShort if i_useHistChk else True) and (c_pullbackCountGreen >= i_pullbackBigger if i_usePullbackChk else True)
    c_longExitPrice = strategy.position_avg_price * (1 + i_longProfitPerc)
    c_shortExitPrice = strategy.position_avg_price * (1 - i_shortProfitPerc)
    c_longStopPrice = strategy.position_avg_price * (1 - i_longStopPerc)
    c_shortStopPrice = strategy.position_avg_price * (1 + i_shortStopPerc)
    if c_longCondition and strategy.opentrades == 0:
        strategy.entry(id='LONG open', direction=strategy.long, comment='{\n  "action": "start_bot_and_start_deal",\n  "message_type": "bot",\n  "bot_id": ' + string.tostring(i_botIDLong) + ',\n  "email_token": "' + string.tostring(i_tokenID) + '",\n  "delay_seconds": 0}' if i_useComments else na)
    if strategy.opentrades != 0:
        strategy.exit(id='Long close', from_entry='LONG open', limit=c_longExitPrice, stop=c_longStopPrice, comment='{\n  "action": "close_at_market_price_all_and_stop_bot",\n  "message_type": "bot",\n  "bot_id": ' + string.tostring(i_botIDLong) + ',\n  "email_token": "' + string.tostring(i_tokenID) + '",\n  "delay_seconds": 0}' if i_useComments else na)
    if c_shortCondition and strategy.opentrades == 0:
        strategy.entry(id='SHORT open', direction=strategy.short, comment='{\n  "action": "start_bot_and_start_deal",\n  "message_type": "bot",\n  "bot_id": ' + string.tostring(i_botIDShort) + ',\n  "email_token": "' + string.tostring(i_tokenID) + '",\n  "delay_seconds": 0}' if i_useComments else na)
    if strategy.opentrades != 0:
        strategy.exit(id='Short close', from_entry='SHORT open', limit=c_shortExitPrice, stop=c_shortStopPrice, comment='{\n  "action": "close_at_market_price_all_and_stop_bot",\n  "message_type": "bot",\n  "bot_id": ' + string.tostring(i_botIDShort) + ',\n  "email_token": "' + string.tostring(i_tokenID) + '",\n  "delay_seconds": 0}' if i_useComments else na)
    plot(c_emaFast, 'Ema fast', color=color.new(color.new('#4DB6AC'), 40), linewidth=2, display=display.none)
    plot(c_emaSlow, 'Ema slow', color=color.new(color.new('#F57C00'), 40), linewidth=2, display=display.none)
    balance: Persistent = startBalance
    maxBalance: Persistent[float] = 0.0
    totalWins: Persistent[int] = 0
    totalLoss: Persistent[int] = 0
    if strategy.wintrades != strategy.wintrades[1]:
        balance = balance + riskPerTrade / 100 * balance * i_rr
        totalWins = totalWins + 1
        if balance > maxBalance:
            maxBalance = balance
    if strategy.losstrades != strategy.losstrades[1]:
        balance = balance - riskPerTrade / 100 * balance
        totalLoss = totalLoss + 1
    testTable: Persistent[Table] = table.new(position.top_right if i_testerPosition == 'Top right' else position.top_left if i_testerPosition == 'Top left' else position.bottom_right if i_testerPosition == 'Bottom right' else position.bottom_left, 5, 2, border_width=2)
    def f_fillCell(_table, _column, _row, _title, _value, _bgcolor, _txtcolor):
        _cellText = _title + '\n' + _value
        return table.cell(_table, _column, _row, _cellText, bgcolor=_bgcolor, text_color=_txtcolor)

    bgcolor__ren__: Persistent = color.new(color.black, 0)
    if i_drawTester:
        if barstate.islastconfirmedhistory:
            dollarReturn = balance - startBalance
            f_fillCell(testTable, 0, 0, 'Total Trades:', string.tostring(strategy.closedtrades), bgcolor__ren__, color.white)
            f_fillCell(testTable, 0, 1, 'Win Rate:', string.tostring(l_zen.truncate(strategy.wintrades / strategy.closedtrades * 100, 2)) + '%', color.green if strategy.wintrades / strategy.closedtrades * 100 >= 50 else bgcolor__ren__, color.white)
            f_fillCell(testTable, 1, 0, 'Starting:', '$' + string.tostring(startBalance), bgcolor__ren__, color.white)
            f_fillCell(testTable, 1, 1, 'Ending:', '$' + string.tostring(l_zen.truncate(balance, 2)), color.green if balance > startBalance else bgcolor__ren__, color.white)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
