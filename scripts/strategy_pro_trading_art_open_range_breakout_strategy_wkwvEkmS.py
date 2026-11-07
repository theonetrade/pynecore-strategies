"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, close, color, high, hour, input, low, math, minute, na, plot,
    script, strategy
)
from pynecore.types import Persistent

alertGroup: str = '========= Alert Message Settings ========='


@script.strategy('Pro Trading Art Open Range Breakout Strategy', 'PTA - Open Range Breakout Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    openRange=input.float(0.4, 'Open Range %', step=0.1, group='=============== Indicator Settings ==============='),
    startH=input.int(9, 'Start Hour', inline='start', group='========= Start Trade AT ========='),
    startM=input.int(15, 'Start Minute', inline='start', group='========= Start Trade AT ========='),
    stopNewTrade=input.int(14, 'Stop Hour', inline='start', group='========= Stop New Trade At ========='),
    endH=input.int(15, 'End Hour', inline='end', group='========= Close All Trade At ========='),
    endM=input.int(0, 'End Minute', inline='end', group='========= Close All Trade At ========='),
    isCloseAll=input.bool(True, 'Close All Trade', group='========= Close All Trade At ========='),
    isHighV=input.bool(True, 'Show High', inline='range', group='========= Plot Range ========='),
    isLowV=input.bool(True, 'Show Low', inline='range', group='========= Plot Range ========='),
    buffer=input.float(0.0, 'Buffer', group='========= Strategy Settings ========='),
    tradeGap=input.float(100, 'Trade Gap', group='========= Strategy Settings ========='),
    gapBook=input.float(50, 'Min Profit Point After Trade Gap', group='========= Strategy Settings ========='),
    longMsg=input.string('Long', 'Long MSG', group=alertGroup),
    shortMsg=input.string('Short', 'Short SMG', group=alertGroup),
    longExitMsg=input.string('Long Exit', 'Long Exit SMG', group=alertGroup),
    shortExitMsg=input.string('Short Exit', 'Short Exit MSG', group=alertGroup),
    tradeMode=input.string('Percent', 'Trade Mode', options=('Point', 'Percent'), group='========= Strategy Settings ========='),
    sl=input.float(1, 'Stop Loss Point Or Percent', group='========= Strategy Settings ========='),
    target=input.float(2, 'Target Point Or Percent', group='========= Strategy Settings =========')
):
    isStart = hour == startH and minute == startM
    isEnd = hour == endH and minute == endM
    High: Persistent[float] = 0.0
    Low: Persistent[float] = 0.0
    if isStart:
        Low = low - buffer
        High = high + buffer
    plot(High if isHighV else na, color=color.lime)
    plot(Low if isLowV else na, color=color.red)
    validOpen = math.abs((High - Low) / Low * 100) >= openRange
    start: Persistent[bool] = False
    if isStart:
        start = True
    if isEnd:
        start = False
    longCondition: Persistent[bool] = False
    shortCondition: Persistent[bool] = False
    isLongTrade: Persistent[bool] = False
    isShortTrade: Persistent[bool] = False
    if strategy.position_size > 0:
        isLongTrade = True
    if strategy.position_size < 0:
        isShortTrade = True
    if close > High and start:
        longCondition = True
    if close < Low and start:
        shortCondition = True
    if isLongTrade:
        longCondition = False
    if isShortTrade:
        shortCondition = False
    if isEnd:
        isLongTrade = False
        isShortTrade = False
        longCondition = False
        shortCondition = False
    entry_price = strategy.opentrades.entry_price(strategy.opentrades - 1)
    longSL: float = 0.0
    shortSL: float = 0.0
    longTarget: float = 0.0
    shortTarget: float = 0.0
    if tradeMode == 'Percent':
        longSL = entry_price - entry_price * sl / 100
        shortSL = entry_price + entry_price * sl / 100
        longTarget = entry_price + entry_price * target / 100
        shortTarget = entry_price - entry_price * target / 100
    if tradeMode == 'Point':
        longSL = entry_price - sl
        shortSL = entry_price + sl
        longTarget = entry_price + target
        shortTarget = entry_price - target
    if strategy.position_size > 0 and close[1] > entry_price + tradeGap:
        longSL = entry_price + gapBook
    if strategy.position_size < 0 and close[1] < entry_price - tradeGap:
        shortSL = entry_price - gapBook
    if longCondition and validOpen:
        strategy.entry('Long', strategy.long, alert_message=longMsg)
    if shortCondition and validOpen:
        strategy.entry('Short', strategy.short, alert_message=shortMsg)
    if strategy.position_size > 0:
        strategy.exit('Long Exit', 'Long', stop=longSL, limit=longTarget, comment_loss='Long SL', comment_profit='Long Profit', alert_message=longExitMsg)
    if strategy.position_size < 0:
        strategy.exit('Short Exit', 'Short', stop=shortSL, limit=shortTarget, comment_loss='Short SL', comment_profit='Short Profit', alert_message=shortExitMsg)
    if isEnd and isCloseAll:
        strategy.close_all(comment='Closing Bell')
    if longCondition and validOpen:
        alert(longMsg, alert.freq_once_per_bar_close)
    if shortCondition and validOpen:
        alert(shortMsg, alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
