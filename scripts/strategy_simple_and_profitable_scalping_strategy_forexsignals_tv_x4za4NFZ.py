"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    bar_index, barmerge, barstate, box, close, color, currency, extend, fill,
    high, input, label, line, low, math, na, plot, plotchar, request, script, strategy, string,
    syminfo, ta, time, timestamp
)
from pynecore.types import Color, Persistent, PersistentSeries, Series

INITIAL_CAPITAL: int = 1000
DEFAULT_COMMISSION: float = 0.02
MAX_DRAWINGS: int = 500
IS_OVERLAY: bool = True


@script.strategy('Simple and Profitable Scalping Strategy (ForexSignals TV)', 'Scalping Strategy', overlay=IS_OVERLAY, initial_capital=INITIAL_CAPITAL, currency=currency.NONE, max_labels_count=MAX_DRAWINGS, max_boxes_count=MAX_DRAWINGS, max_lines_count=MAX_DRAWINGS, default_qty_type=strategy.cash, commission_type=strategy.commission.percent, commission_value=DEFAULT_COMMISSION, margin_long=0, margin_short=0, default_qty_value=1, close_by_id=True)
def main(
    trendFilterTf=input.timeframe('60', 'Trend Timeframe        ', group='Strategy: Higher Timeframe Trend Filter', inline='TF1', tooltip='Higher timeframe to use for finding main trand direction'),
    trendFastEmaLen=input.int(8, 'Fast EMA Length        ', group='Strategy: Higher Timeframe Trend Filter', inline='TF2', minval=1, tooltip='Length of Fast EMA of higher timeframe'),
    trendSlowEmaLen=input.int(21, 'Slow EMA Length          ', group='Strategy: Higher Timeframe Trend Filter', inline='TF3', minval=1, tooltip='Length of Slow EMA of higher timeframe'),
    entryFastEmaLen=input.int(8, 'Fast EMA Length          ', group='Strategy: Trade Entry Conditions', inline='TE1', minval=1, tooltip='Fast EMA used to find entry candles when price pulls back into this line'),
    entryMedEmaLen=input.int(13, 'Medium EMA Length      ', group='Strategy: Trade Entry Conditions', inline='TE2', minval=1, tooltip='Medium EMA used to filter out entries when lines are not fanned out or not trending in the desired direction'),
    entrySlowEmaLen=input.int(21, 'Slow EMA Length         ', group='Strategy: Trade Entry Conditions', inline='TE3', minval=1, tooltip='Slow EMA used to filter out entries when lines are not fanned out or not trending in the desired direction.\n\nAlso used to cancel open orders which close below this EMA before entry has been triggered'),
    fanoutAtrMult=input.float(0.5, 'EMA Fanout ATR Multiplier    ', group='Strategy: Trade Entry Conditions', inline='TE4', step=0.1, tooltip='ATR multiplier to determine how but the fanout gap must be between the Fast EMA and Slow EMA over the specified number of candles'),
    fanoutLookback=input.int(3, 'EMA Fanout Lookback      ', group='Strategy: Trade Entry Conditions', inline='TE5', minval=1, tooltip='Number of candles over which the entry EMA lines must be fanned out by the specified amount'),
    priceBufferAtrMult=input.float(0.5, 'Price Buffer ATR Multiplier    ', group='Strategy: Trade Entry Conditions', inline='TE6', step=0.1, tooltip='ATR multiplier to determine how big of a butter should be set above/below trade entry and stop loss'),
    localHighLookback=input.int(5, 'Entry Price High/Low Lookback ', group='Strategy: Trade Entry Conditions', inline='TE7', minval=1, tooltip='Number of candles to lookback on to find the local high/low which is used to establish the stop order entry price'),
    riskReward=input.float(2, 'Risk : Reward        1 :', group='Strategy: Risk Management', inline='RM1', minval=0, step=0.1, tooltip='Previous high or low (long/short dependant) is used to determine TP level. \'Risk : Reward\' ratio is then used to calculate SL based of previous high/low level.\n\nIn short, the higher the R:R ratio, the smaller the SL since TP target is fixed by previous high/low price data.'),
    accountRiskPercent=input.float(1, 'Portfolio Risk %         ', group='Strategy: Risk Management', inline='RM2', minval=0, step=0.1, tooltip='Percentage of portfolio you lose if trade hits SL.\n\nYou then stand to gain\n  Portfolio Risk % * Risk : Reward\nif trade hits TP.'),
    startYear=input.int(2022, 'Start Date       ', group='Strategy: Date Range', inline='DR1', minval=1900, maxval=2100),
    startMonth=input.int(1, '', group='Strategy: Date Range', inline='DR1', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)),
    startDate=input.int(1, '', group='Strategy: Date Range', inline='DR1', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31)),
    endYear=input.int(2100, 'End Date      ', group='Strategy: Date Range', inline='DR2', minval=1900, maxval=2100),
    endMonth=input.int(1, '', group='Strategy: Date Range', inline='DR2', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)),
    endDate=input.int(1, '', group='Strategy: Date Range', inline='DR2', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31)),
    showTpSlBoxes=input.bool(True, 'Show TP / SL Boxes', group='Strategy: Drawings', inline='D1', tooltip='Show or hide TP and SL position boxes.\n\nNote: TradingView limits the maximum number of boxes that can be displayed to 500 so they may not appear for all price data under test.'),
    showLabels=input.bool(False, 'Show Trade Exit Labels', group='Strategy: Drawings', inline='D2', tooltip='Useful labels to identify Profit/Loss and cumulative portfolio capital after each trade closes.\n\nAlso note that TradingView limits the max number of \'boxes\' that can be displayed on a chart (max 500). This means when you lookback far enough on the chart you will not see the TP/SL boxes. However you can check this option to identify where trades exited.')
):
    currTrendFastEma: PersistentSeries[float] = na(float)
    currTrendSlowEma: PersistentSeries[float] = na(float)
    emaFillColor: PersistentSeries[Color] = na(Color)
    trendFastEma = ta.ema(close, trendFastEmaLen)
    trendSlowEma = ta.ema(close, trendSlowEmaLen)
    fastSec = request.security(syminfo.tickerid, trendFilterTf, trendFastEma, barmerge.gaps_off, barmerge.lookahead_off)
    slowSec = request.security(syminfo.tickerid, trendFilterTf, trendSlowEma, barmerge.gaps_off, barmerge.lookahead_off)
    currTrendFastEma = currTrendFastEma[1] if na(fastSec) else fastSec
    currTrendSlowEma = currTrendSlowEma[1] if na(slowSec) else slowSec
    fastEmaPlot = plot(fastSec, color=color.green)
    slowEmaPlot = plot(slowSec, color=color.red)
    emaFillColor = color.new(color.green, 80) if fastSec > slowSec else color.new(color.red, 80) if fastSec < slowSec else emaFillColor[1]
    fill(fastEmaPlot, slowEmaPlot, color=emaFillColor, fillgaps=True)
    entryFastEma: Series = ta.ema(close, entryFastEmaLen)
    entryMedEma = ta.ema(close, entryMedEmaLen)
    entrySlowEma: Series = ta.ema(close, entrySlowEmaLen)
    plot(entryFastEma, color=color.orange)
    plot(entryMedEma, color=color.yellow)
    plot(entrySlowEma, color=color.purple)
    def printLabel(barIndex, msg):
        return label.new(barIndex, close, msg)

    def percentAsPoints(pcnt):
        return math.round(pcnt / 100 * close / syminfo.mintick)

    def calcStopLossPrice(pointsOffset, entryPrice, isLong):
        priceOffset = pointsOffset * syminfo.mintick
        __block_result__ = na
        if isLong:
            __block_result__ = entryPrice - priceOffset
        else:
            __block_result__ = entryPrice + priceOffset
        return __block_result__

    def calcProfitTrgtPrice(pointsOffset, entryPrice, isLong):
        return calcStopLossPrice(-pointsOffset, entryPrice, isLong)

    def printTpSlHitBox(left, right, slHit, tpHit, entryPrice, slPrice, tpPrice):
        __block_result_1__ = na
        if showTpSlBoxes:
            box.new(left=left, top=entryPrice, right=right, bottom=slPrice, bgcolor=color.new(color.red, 60) if slHit else color.new(color.gray, 90), border_width=0)
            box.new(left=left, top=entryPrice, right=right, bottom=tpPrice, bgcolor=color.new(color.green, 60) if tpHit else color.new(color.gray, 90), border_width=0)
            line.new(x1=left, y1=entryPrice, x2=right, y2=entryPrice, color=color.new(color.yellow, 20))
            line.new(x1=left, y1=slPrice, x2=right, y2=slPrice, color=color.new(color.red, 20))
            __block_result_1__ = line.new(x1=left, y1=tpPrice, x2=right, y2=tpPrice, color=color.new(color.green, 20))
        return __block_result_1__

    def printTpSlNotHitBox(left, right, entryPrice, slPrice, tpPrice):
        __block_result_2__ = na
        if showTpSlBoxes:
            box.new(left=left, top=entryPrice, right=right, bottom=slPrice, bgcolor=color.new(color.orange, 90), border_width=0)
            box.new(left=left, top=entryPrice, right=right, bottom=tpPrice, bgcolor=color.new(color.orange, 90), border_width=0)
            line.new(x1=left, y1=entryPrice, x2=right, y2=entryPrice, color=color.new(color.yellow, 20))
            line.new(x1=left, y1=slPrice, x2=right, y2=slPrice, color=color.new(color.red, 20))
            __block_result_2__ = line.new(x1=left, y1=tpPrice, x2=right, y2=tpPrice, color=color.new(color.green, 20))
        return __block_result_2__

    def printTradeExitLabel(x, y, posSize, entryPrice, pnl):
        __block_result_3__ = na
        if showLabels:
            labelStr = 'Position Size: ' + string.tostring(math.abs(posSize), '#.##') + '\nPNL: ' + string.tostring(pnl, '#.##') + '\nCapital: ' + string.tostring(strategy.equity, '#.##') + '\nEntry Price: ' + string.tostring(entryPrice, '#.##') if pnl != 0 else 'Trade Cancelled'
            __block_result_3__ = label.new(x=x, y=y, text=labelStr, color=color.new(color.green, 60) if pnl > 0 else color.new(color.red, 60) if pnl < 0 else color.new(color.orange, 60), textcolor=color.white, style=label.style_label_down)
        return __block_result_3__

    def printVerticalLine(col):
        return line.new(bar_index, close, bar_index, close * 1.01, extend=extend.both, color=col)

    inDateRange = time >= timestamp(syminfo.timezone, startYear, startMonth, startDate, 0, 0) and time < timestamp(syminfo.timezone, endYear, endMonth, endDate, 0, 0)
    bullTrendDir = currTrendFastEma > currTrendSlowEma
    bearTrendDir = currTrendFastEma < currTrendSlowEma
    bullTrendPrice = close > currTrendFastEma
    bearTrendPrice = close < currTrendFastEma
    bullEmaOrder = entryFastEma > entryMedEma and entryMedEma > entrySlowEma
    bearEmaOrder = entryFastEma < entryMedEma and entryMedEma < entrySlowEma
    fanOutGap = ta.atr(14) * fanoutAtrMult
    bullFanOutGap: Persistent[bool] = False
    bearFanOutGap: Persistent[bool] = False
    bullFanOutGap = False
    bearFanOutGap = False
    for lookback in pine_range(0, fanoutLookback - 1, 1):
        bullFanOutGap = entryFastEma[lookback] - fanOutGap > entrySlowEma[lookback]
        if bullFanOutGap == False:
            break
    for lookback in pine_range(0, fanoutLookback - 1, 1):
        bearFanOutGap = entryFastEma[lookback] + fanOutGap < entrySlowEma[lookback]
        if bearFanOutGap == False:
            break
    bullBreakout = low[1] > entryFastEma[1]
    bearBreakout = high[1] < entryFastEma[1]
    bullPullback = low < entryFastEma
    bearPullback = high > entryFastEma
    goLong = inDateRange and bullTrendDir and bullTrendPrice and bullEmaOrder and bullFanOutGap and bullBreakout and bullPullback
    goShort = inDateRange and bearTrendDir and bearTrendPrice and bearEmaOrder and bearFanOutGap and bearBreakout and bearPullback
    tradeEntryBar: Persistent = bar_index
    profitPoints: Persistent[float] = 0.0
    lossPoints: Persistent[float] = 0.0
    slPrice: Persistent[float] = 0.0
    slAmount: Persistent[float] = 0.0
    slPercent: Persistent[float] = 0.0
    tpPrice: Persistent[float] = 0.0
    tpPercent: Persistent[float] = 0.0
    inLong: Persistent[bool] = False
    inShort: Persistent[bool] = False
    entryPrice: Persistent[float] = na(float)
    tradeCancelled: Persistent[bool] = False
    tradeActive: Persistent[bool] = False
    openLong = goLong and (not inLong)
    openShort = goShort and (not inShort)
    flippingSides = goLong and inShort or (goShort and inLong)
    enteringTrade = openLong or openShort
    inTrade = inLong or inShort
    priceBuffer = ta.atr(14) * priceBufferAtrMult
    localHigh = ta.highest(high, localHighLookback)
    localLow = ta.lowest(low, localHighLookback)
    if enteringTrade:
        entryPrice = localHigh + priceBuffer if goLong else localLow - priceBuffer if goShort else na
        slPrice = low - priceBuffer if openLong else high + priceBuffer if openShort else na
        slAmount = math.abs(entryPrice - slPrice)
        slPercent = math.abs((1 - (entryPrice - slAmount) / entryPrice) * 100)
        tpPercent = slPercent * riskReward
    riskAmt = strategy.equity * accountRiskPercent / 100
    entryQty = math.abs(riskAmt / slPercent * 100) / close
    if openLong:
        if strategy.position_size < 0:
            printTpSlNotHitBox(tradeEntryBar + 1, bar_index + 1, strategy.position_avg_price, slPrice, tpPrice)
            printTradeExitLabel(bar_index + 1, math.max(tpPrice, slPrice), strategy.position_size, strategy.position_avg_price, strategy.openprofit)
        strategy.entry('Long', strategy.long, stop=entryPrice, qty=entryQty, alert_message='Long Entry')
        enteringTrade = True
        inLong = True
        inShort = False
        printVerticalLine(color.new(color.green, 60))
    if openShort:
        if strategy.position_size > 0:
            printTpSlNotHitBox(tradeEntryBar + 1, bar_index + 1, strategy.position_avg_price, slPrice, tpPrice)
            printTradeExitLabel(bar_index + 1, math.max(tpPrice, slPrice), strategy.position_size, strategy.position_avg_price, strategy.openprofit)
        strategy.entry('Short', strategy.short, stop=entryPrice, qty=entryQty, alert_message='Short Entry')
        enteringTrade = True
        inShort = True
        inLong = False
        printVerticalLine(color.new(color.red, 60))
    longActive = strategy.position_size[1] > 0
    shortActive = strategy.position_size[1] < 0
    activeTrade = longActive or shortActive
    if not activeTrade and (inLong and close < entrySlowEma or (inShort and close > entrySlowEma)):
        printVerticalLine(color.new(color.silver, 60))
        inLong = False
        inShort = False
        strategy.cancel_all()
        tradeCancelled = True
    if enteringTrade:
        profitPoints = percentAsPoints(tpPercent)
        lossPoints = percentAsPoints(slPercent)
        tpPrice = calcProfitTrgtPrice(profitPoints, entryPrice, openLong)
        tradeEntryBar = bar_index
    strategy.exit('TP/SL', profit=profitPoints, loss=lossPoints, comment_profit='TP Hit', comment_loss='SL Hit', alert_profit='TP Hit Alert', alert_loss='SL Hit Alert')
    exitedOnCurrentBar = strategy.closedtrades.entry_bar_index(strategy.closedtrades - 1) == bar_index
    slHit = (shortActive or exitedOnCurrentBar) and high >= slPrice or ((longActive or exitedOnCurrentBar) and low <= slPrice)
    tpHit = (longActive or exitedOnCurrentBar) and high >= tpPrice or ((shortActive or exitedOnCurrentBar) and low <= tpPrice)
    exitTriggered = slHit or tpHit
    pnl = strategy.closedtrades.profit(strategy.closedtrades - 1)
    posSize = strategy.closedtrades.size(strategy.closedtrades - 1)
    if inTrade and exitTriggered and (not tradeCancelled) or exitedOnCurrentBar:
        inShort = False
        inLong = False
        printTpSlHitBox(tradeEntryBar, bar_index, slHit, tpHit, entryPrice, slPrice, tpPrice)
        printTradeExitLabel(bar_index, math.max(tpPrice, slPrice), posSize, entryPrice, pnl)
    elif barstate.islastconfirmedhistory and strategy.position_size != 0:
        printTpSlNotHitBox(tradeEntryBar + 1, bar_index + 1, strategy.position_avg_price, slPrice, tpPrice)
    elif tradeCancelled:
        tradeCancelled = False
        printTpSlNotHitBox(tradeEntryBar, bar_index, entryPrice, slPrice, tpPrice)
        printTradeExitLabel(bar_index + 1, math.max(tpPrice, slPrice), strategy.position_size, strategy.position_avg_price, strategy.openprofit)
    plotchar(currTrendFastEma, 'currTrendFastEma', '')
    plotchar(currTrendSlowEma, 'currTrendSlowEma', '')
    plotchar(fanOutGap, 'fanGap', '')
    plotchar(bullTrendDir, 'bullTrendDir', '')
    plotchar(bullTrendPrice, 'bullTrendPrice', '')
    plotchar(bullEmaOrder, 'bullEmaOrder', '')
    plotchar(bullFanOutGap, 'bullFanOutGap', '')
    plotchar(bullBreakout, 'bullBreakout', '')
    plotchar(bullPullback, 'bullPullback', '')
    plotchar(goLong, 'goLong', '')
    plotchar(inLong, 'inLong', '')
    plotchar(bearTrendDir, 'bearTrendDir', '')
    plotchar(bearTrendPrice, 'bearTrendPrice', '')
    plotchar(bearEmaOrder, 'bearEmaOrder', '')
    plotchar(bearFanOutGap, 'bearFanOutGap', '')
    plotchar(bearBreakout, 'bearBreakout', '')
    plotchar(bearPullback, 'bearPullback', '')
    plotchar(goShort, 'goShort', '')
    plotchar(inShort, 'inShort', '')
    plotchar(openLong, 'openLong', '')
    plotchar(openShort, 'openShort', '')
    plotchar(enteringTrade, 'enteringTrade', '')
    plotchar(entryPrice, 'entryPrice', '')
    plotchar(slPrice, 'slPrice', '')
    plotchar(tpPrice, 'tpPrice', '')
    plotchar(tpPercent, 'tpPercent', '')
    plotchar(slPercent, 'slPercent', '')
    plotchar(longActive, 'longActive', '')
    plotchar(shortActive, 'shortActive', '')
    plotchar(exitedOnCurrentBar, 'exitedOnCurrentBar', '')
    plotchar(strategy.position_size, 'position_size After', '')
    plotchar(slHit, 'slHit', '')
    plotchar(tpHit, 'tpHit', '')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
