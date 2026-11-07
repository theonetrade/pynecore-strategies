"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    bar_index, close, color, display, fill, high, input, label, line,
    linefill, low, math, na, nz, open, plot, plotcandle, position, request, script, size, strategy,
    string, syminfo, ta, table, text, ticker, time, timeframe, timestamp, xloc
)
from pynecore.types import Color, Label, Line, LineFill, Persistent, Series, Table
import lib.jordanfray.obvFilter.v2 as obv
import lib.jordanfray.threengine_global_automation_library.v89 as bot

alertatronSecretTip: str = 'The key that is configured in Alertatron that selects which exchange integration you want to use.'
exchangeTooltip: str = 'Pick the exchange that your Alertatron API Secret is configured to. This is used to get the right divider between the pair and the base currency.'
exchangeCurrencyOverrideTip: str = 'If you want to use a different base currency than the current chart, you can override it here. Be sure it matches the exchange base currency. \n \n Do not include the currency/symbol divider in this.'
exchangeCurrencySymbolTip: str = 'If you want to use a different symbol than the current chart, you can override it here. Be sure it matches the exchange symbol. \n \n Do not include the currency/symbol divider in this.'
moveStopToolTip: str = 'If enabled, the stop loss will be moved to a price relative to the average entry price using a percentange as an offset after the price reaches the \'after\' threshold. \n 0 = break even.\n \n Default: .1'


@script.strategy('Heikin Ashi Supertrend', overlay=True, max_bars_back=5000, default_qty_type=strategy.cash, default_qty_value=100, initial_capital=100, commission_type=strategy.commission.percent, close_entries_rule='ANY', commission_value=0.035, backtest_fill_limits_assumption=0, process_orders_on_close=True, margin_long=0, margin_short=0, close_by_id=True)
def main(
    strategyIdentifier=input.string(defval='HASTXXXUSDT (Nm)', title='Strategy Identifier', group='Strategy Information'),
    supertrendAtrPeriod=input.int(defval=10, step=1, title='ATR Length', group='Supertrend'),
    supertrendAtrMultiplier=input.float(defval=2.7, step=0.1, title='ATR Multiplier', group='Supertrend'),
    lotSize=input.float(defval=100, title='Lot Size', group='Entry Settings'),
    lotSizeType=input.string(defval='Dollars', title='Lot Size Type', options=('Percent Of Account', 'Dollars', 'Contracts'), group='Entry Settings'),
    profitTargetPercent=input.float(defval=47.0, title='Profit Target (%)', step=0.25, group='Exit Settings'),
    stopLimitTrigger=input.float(defval=21, title='Stop Limit Trigger (%)', step=0.25, group='Exit Settings'),
    stopLimitOffset=input.float(defval=0.1, title='Stop Limit Offset (%)', step=0.01, group='Exit Settings'),
    enableMoveStopToBreakEven=input.bool(defval=True, title='Move Stop Loss', group='Move Stop Loss'),
    moveTo=input.float(defval=1.0, title='to (%)', tooltip=moveStopToolTip),
    moveAfter=input.float(defval=4.0, title='after (%)', tooltip=moveStopToolTip),
    manuallyCloseTrade=input.bool(defval=False, title='Manullay Close Trade?', group='Manually Close Trade'),
    dateTimeClosed=input.time(defval=timestamp('01 Jan 2022 00:00'), title='Date/Time When Trade Was Closed', group='Manually Close Trade'),
    priceClosed=input.price(defval=0.0, title='Price Trade Was Closed At', group='Manually Close Trade'),
    enableWebhookMessages=input.bool(defval=False, title='Enable Webook Messages', group='Automation Settings'),
    tradeAutomationExchange=input.string(defval='ByBit', options=('ByBit', 'FTX.us'), title='Exchange', group='Automation Settings', tooltip=exchangeTooltip),
    tradeAutomationSecret=input.string(defval='haStEthUsdt', title='Alertatron API Secret', group='Automation Settings', tooltip=alertatronSecretTip),
    tradeAutomationLeverage=input.int(defval=1, title='Leverage Amount', group='Automation Settings'),
    tradeAutomationLeverageType=input.string(defval='Cross', title='Leverage Type', options=('Cross', 'Isolated'), group='Automation Settings'),
    tradeAutomationCurrencyOverride=input.string(defval='', title='Currency Override', group='Automation Settings', tooltip=exchangeCurrencyOverrideTip),
    tradeAutomationSymbolOverride=input.string(defval='', title='Symbol Override', group='Automation Settings', tooltip=exchangeCurrencySymbolTip),
    exchangeQtyDecimals=input.int(defval=3, title='Order QTY Decimal Rounding', group='Automation Settings'),
    showDebugTable=input.bool(defval=False, title='Show Debug Table', group='Testing')
):
    green = color.new(color.new('#2DBD85'), 0)
    lightGreen = color.new(color.new('#2DBD85'), 90)
    red = color.new(color.new('#E02A4A'), 0)
    lightRed = color.new(color.new('#E02A4A'), 90)
    yellow = color.new(color.new('#FFED00'), 0)
    lightYellow = color.new(color.new('#FFED00'), 90)
    purple = color.new(color.new('#5A00FF'), 0)
    blue = color.new(color.new('#0C6090'), 0)
    oceanBlue = color.new(color.new('#0C6090'), 0)
    skyBlue = color.new(color.new('#00A5FF'), 0)
    lightBlue = color.new(color.new('#00A5FF'), 80)
    black = color.new(color.new('#000000'), 0)
    gray = color.new(color.new('#AAAAAA'), 0)
    white = color.new(color.new('#FFFFFF'), 0)
    transparent = color.new(color.new('#000000'), 100)
    currentlyInLongPosition = strategy.position_size > 0
    currentlyInShortPosition = strategy.position_size < 0
    currentlyInAPosition = strategy.position_size != 0
    haOpen = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, open)
    haHigh = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, high)
    haLow = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, low)
    haClose: Series = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, close)
    plotcandle(haOpen if haOpen < haClose else na, haHigh, haLow, haClose, title='Green Candles', color=green, wickcolor=green, bordercolor=green, display=display.pane)
    plotcandle(haOpen if haOpen >= haClose else na, haHigh, haLow, haClose, title='Red Candles', color=red, wickcolor=red, bordercolor=red, display=display.pane)
    plot(display=display.status_line, series=haOpen, color=green)
    plot(display=display.status_line, series=haHigh, color=green)
    plot(display=display.status_line, series=haLow, color=red)
    plot(display=display.status_line, series=haClose, color=red)
    haTrueRange = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, ta.atr(supertrendAtrPeriod))
    haSupertrendUp = (haHigh + haLow) / 2 - supertrendAtrMultiplier * haTrueRange
    haSupertrendDown = (haHigh + haLow) / 2 + supertrendAtrMultiplier * haTrueRange
    trendingUp: Series[float] = na(float)
    trendingDown: Series[float] = na(float)
    direction: Series[int] = 0
    trendingUp = math.max(haSupertrendUp, trendingUp[1]) if haClose[1] > trendingUp[1] else haSupertrendUp
    trendingDown = math.min(haSupertrendDown, trendingDown[1]) if haClose[1] < trendingDown[1] else haSupertrendDown
    direction = 1 if haClose > trendingDown[1] else -1 if haClose < trendingUp[1] else nz(direction[1], 1)
    supertrend = trendingUp if direction == 1 else trendingDown
    supertrendUp = ta.change(direction) < 0
    supertrendDown = ta.change(direction) > 0
    averageEntryPrice: float = strategy.position_avg_price if currentlyInAPosition else close
    justClosedPosition = ta.change(averageEntryPrice)
    barsSinceOpen = bar_index - strategy.opentrades.entry_bar_index(0) if currentlyInAPosition else 0
    profitAndLoss = strategy.opentrades.profit(0)
    profitAndLossPercent = math.round((close - averageEntryPrice) / averageEntryPrice * 100, 2)
    profitTarget = averageEntryPrice + averageEntryPrice * (profitTargetPercent / 100) if currentlyInLongPosition else averageEntryPrice - averageEntryPrice * (profitTargetPercent / 100)
    stopLossLimitPrice: float = math.round(averageEntryPrice - averageEntryPrice * stopLimitTrigger / 100, exchangeQtyDecimals) if currentlyInLongPosition else math.round(averageEntryPrice + averageEntryPrice * stopLimitTrigger / 100, exchangeQtyDecimals) if currentlyInShortPosition else na
    stopLossTriggerPrice: float = math.round(stopLossLimitPrice + stopLossLimitPrice * stopLimitOffset / 100, exchangeQtyDecimals) if currentlyInLongPosition else math.round(stopLossLimitPrice - stopLossLimitPrice * stopLimitOffset / 100, exchangeQtyDecimals) if currentlyInShortPosition else na
    moveStopLossAfter: float = math.round(averageEntryPrice + averageEntryPrice * (moveAfter / 100), exchangeQtyDecimals) if currentlyInLongPosition else math.round(averageEntryPrice - averageEntryPrice * (moveAfter / 100), exchangeQtyDecimals) if currentlyInShortPosition else na
    moveStopTriggered: Persistent[bool] = False
    moveStopLossTo = math.round(averageEntryPrice + averageEntryPrice * (moveTo / 100), exchangeQtyDecimals) if currentlyInLongPosition else math.round(averageEntryPrice - averageEntryPrice * (moveTo / 100), exchangeQtyDecimals) if currentlyInShortPosition else na
    if currentlyInLongPosition and high > moveStopLossAfter and enableMoveStopToBreakEven and (moveStopTriggered == False):
        moveStopTriggered = True
    if currentlyInShortPosition and low < moveStopLossAfter and enableMoveStopToBreakEven and (moveStopTriggered == False):
        moveStopTriggered = True
    if enableMoveStopToBreakEven and moveStopTriggered:
        stopLossLimitPrice = moveStopLossTo
        stopLossTriggerPrice = math.round(stopLossLimitPrice + stopLossLimitPrice * stopLimitOffset / 100, exchangeQtyDecimals) if currentlyInLongPosition else math.round(stopLossLimitPrice - stopLossLimitPrice * stopLimitOffset / 100, exchangeQtyDecimals) if currentlyInShortPosition else na
    if not currentlyInAPosition or cast_bool(justClosedPosition):
        moveStopTriggered = False
    openLong: bool = supertrendDown
    openShort: bool = supertrendUp
    exitLong: bool = currentlyInLongPosition and close > profitTarget
    exitShort: bool = currentlyInShortPosition and close < profitTarget
    longStopLoss: bool = currentlyInLongPosition and close < stopLossTriggerPrice and (barsSinceOpen > 2)
    shortStopLoss: bool = currentlyInShortPosition and close > stopLossTriggerPrice and (barsSinceOpen > 2)
    manuallyCloseShort: bool = currentlyInShortPosition and manuallyCloseTrade and (time == dateTimeClosed)
    manuallyCloseLong: bool = currentlyInLongPosition and manuallyCloseTrade and (time == dateTimeClosed)
    symbol, baseCurrency = bot.getPairOverrides(tradeAutomationSymbolOverride, tradeAutomationCurrencyOverride)
    contractCount, entryAmount = bot.getLotSize(lotSizeType, lotSize, tradeAutomationLeverage, exchangeQtyDecimals)
    enterLongAlertMessage: str = bot.getAlertatronMarketEntryMessage(secret=tradeAutomationSecret, symbol=symbol, baseCurrency=baseCurrency, pairDivider=bot.getPairDividerForExchange(tradeAutomationExchange), side='buy', symbolMaxDecimals=exchangeQtyDecimals, leverage=tradeAutomationLeverage, leverageType=tradeAutomationLeverageType, entryPrice=close, amount=lotSize, amountType=lotSizeType, stopTrigger=stopLimitTrigger, stopTriggerType='percent', stopLimitOffset=stopLimitOffset) if enableWebhookMessages else 'Webhooks disabled by strategy.'
    enterShortAlertMessage: str = bot.getAlertatronMarketEntryMessage(secret=tradeAutomationSecret, symbol=symbol, baseCurrency=baseCurrency, pairDivider=bot.getPairDividerForExchange(tradeAutomationExchange), side='sell', symbolMaxDecimals=exchangeQtyDecimals, leverage=tradeAutomationLeverage, leverageType=tradeAutomationLeverageType, entryPrice=close, amount=lotSize, amountType=lotSizeType, stopTrigger=stopLimitTrigger, stopTriggerType='percent', stopLimitOffset=stopLimitOffset) if enableWebhookMessages else 'Webhooks disabled by strategy.'
    exitLongAlertMessage: str = bot.getAlertatronMarketExitMessage(secret=tradeAutomationSecret, symbol=symbol, baseCurrency=baseCurrency, pairDivider=bot.getPairDividerForExchange(tradeAutomationExchange), side='sell') if enableWebhookMessages else 'Webhooks disabled by strategy.'
    exitShortAlertMessage: str = bot.getAlertatronMarketExitMessage(secret=tradeAutomationSecret, symbol=symbol, baseCurrency=baseCurrency, pairDivider=bot.getPairDividerForExchange(tradeAutomationExchange), side='buy') if enableWebhookMessages else 'Webhooks disabled by strategy.'
    if openLong:
        strategy.entry(id='Long', direction=strategy.long, qty=contractCount, alert_message=enterLongAlertMessage)
    if exitLong:
        strategy.close(id='Long', qty_percent=100, comment='Exit Long', alert_message=exitLongAlertMessage)
    if longStopLoss:
        strategy.exit(id='Moved Stop' if moveStopTriggered else 'Stop Loss', from_entry='Long', qty_percent=100, stop=stopLossLimitPrice)
    if manuallyCloseLong:
        strategy.exit(id='Manually Close Long', from_entry='Long', qty_percent=100, stop=priceClosed)
    if openShort:
        strategy.entry(id='Short', direction=strategy.short, qty=contractCount, alert_message=enterShortAlertMessage)
    if exitShort:
        strategy.close(id='Short', qty_percent=100, comment='Exit Short', alert_message=exitShortAlertMessage)
    if shortStopLoss:
        strategy.exit(id='Moved Stop' if moveStopTriggered else 'Stop Loss', from_entry='Short', qty_percent=100, stop=stopLossLimitPrice)
    if manuallyCloseShort:
        strategy.exit(id='Manually Close Short', from_entry='Short', qty_percent=100, stop=priceClosed)
    bodyMiddle = plot((haOpen + haClose) / 2, display=display.none)
    downTrend = plot(supertrend if direction < 0 else na, 'Down Trend', color=red, style=plot.style_linebr)
    upTrend = plot(na if direction < 0 else supertrend, 'Up Trend', color=green, style=plot.style_linebr)
    fill(bodyMiddle, upTrend, lightGreen, fillgaps=False)
    fill(bodyMiddle, downTrend, lightRed, fillgaps=False)
    stopLossColor: Color = red
    stopLossBackgroundColor: Color = red
    if currentlyInLongPosition and stopLossLimitPrice > averageEntryPrice:
        stopLossColor = green
        stopLossBackgroundColor = lightGreen
    else:
        if currentlyInShortPosition and stopLossLimitPrice < averageEntryPrice:
            stopLossColor = green
            stopLossBackgroundColor = lightGreen
        else:
            stopLossColor = red
            stopLossBackgroundColor = lightRed
    stopLossLabel: Persistent[Label] = na(Label)
    moveStopAfterLabel: Persistent[Label] = na(Label)
    averageEntryLabel: Persistent[Label] = na(Label)
    profitAndLossLabel: Persistent[Label] = na(Label)
    profitTargetLabel: Persistent[Label] = na(Label)
    stopLossTriggerLine: Persistent[Line] = na(Line)
    moveStopAfterLine: Persistent[Line] = na(Line)
    stopLossLimitLine: Persistent[Line] = na(Line)
    averageEntryLine: Persistent[Line] = na(Line)
    profitTargetLine: Persistent[Line] = na(Line)
    stopLossBackground: Persistent[LineFill] = na(LineFill)
    profitTargetBackground: Persistent[LineFill] = na(LineFill)
    label.delete(stopLossLabel)
    label.delete(moveStopAfterLabel)
    label.delete(averageEntryLabel)
    label.delete(profitAndLossLabel)
    label.delete(profitTargetLabel)
    line.delete(stopLossTriggerLine)
    line.delete(moveStopAfterLine)
    line.delete(stopLossLimitLine)
    line.delete(averageEntryLine)
    line.delete(profitTargetLine)
    linefill.delete(stopLossBackground)
    linefill.delete(profitTargetBackground)
    stopLossLabelText: str = na(str)
    if cast_bool(moveStopLossAfter) and (not moveStopTriggered):
        stopLossLabelText = '\u2002Stop Trigger\u2002|\u2002' + string.format('{0,number,currency}', stopLossTriggerPrice) + '\n' + '\u2002Stop Limit\u2002|\u2002' + string.format('{0,number,currency}' + '\u2002', stopLossLimitPrice) + '\n' + '\u2002Moving to ' + string.format('{0,number,currency}', moveStopLossTo) + ' after ' + string.tostring(moveAfter) + '%\u2002'
    else:
        stopLossLabelText = '\u2002Stop Trigger\u2002|\u2002' + string.format('{0,number,currency}', stopLossTriggerPrice) + '\n' + '\u2002Stop Limit\u2002|\u2002' + string.format('{0,number,currency}' + '\u2002', stopLossLimitPrice)
    xOffset = 2 * timeframe.in_seconds(timeframe.period) * 1000
    profitAndLossLabel = label.new(x=time + xOffset, xloc=xloc.bar_time, y=close, style=label.style_label_left, size=size.normal, color=green if profitAndLoss > 0 else red, textcolor=white, text='\u2002P&L | ' + string.format('{0,number,currency}', profitAndLoss) + ' (' + string.tostring(profitAndLossPercent) + '%)\u2002')
    averageEntryLabel = label.new(x=time + xOffset, xloc=xloc.bar_time, y=averageEntryPrice, style=label.style_label_left, size=size.normal, color=oceanBlue, textcolor=white, text='\u2002Entry | ' + string.format('{0,number,currency}' + '\u2002', averageEntryPrice))
    stopLossLabel = label.new(x=time + xOffset, xloc=xloc.bar_time, y=stopLossLimitPrice, style=label.style_label_left, textalign=text.align_left, size=size.normal, color=stopLossColor, textcolor=white, text=stopLossLabelText)
    averageEntryLine = line.new(x1=strategy.opentrades.entry_bar_index(0), y1=averageEntryPrice, x2=bar_index, y2=averageEntryPrice, color=oceanBlue, width=2, xloc=xloc.bar_index, style=line.style_solid)
    profitTargetLine = line.new(x1=strategy.opentrades.entry_bar_index(0), y1=profitTarget, x2=bar_index, y2=profitTarget, color=green, width=1, xloc=xloc.bar_index, style=line.style_solid)
    profitTargetLabel = label.new(x=time + xOffset, xloc=xloc.bar_time, y=profitTarget, style=label.style_label_left, size=size.normal, color=red, textcolor=white, text='\u2002ProfitTarget | ' + string.format('{0,number,currency}' + '\u2002', profitTarget))
    stopLossTriggerLine = line.new(x1=strategy.opentrades.entry_bar_index(0), y1=stopLossTriggerPrice, x2=bar_index, y2=stopLossTriggerPrice, color=stopLossColor, width=1, xloc=xloc.bar_index, style=line.style_solid)
    stopLossLimitLine = line.new(x1=strategy.opentrades.entry_bar_index(0), y1=stopLossLimitPrice, x2=bar_index, y2=stopLossLimitPrice, color=stopLossColor, width=1, xloc=xloc.bar_index, style=line.style_solid)
    stopLossBackground = linefill.new(averageEntryLine, stopLossLimitLine, stopLossBackgroundColor)
    profitTargetBackground = linefill.new(averageEntryLine, profitTargetLine, lightGreen)
    if enableMoveStopToBreakEven:
        moveStopAfterLabel = label.new(x=time + xOffset, xloc=xloc.bar_time, y=moveStopLossAfter, style=label.style_label_left, size=size.normal, color=purple, textcolor=white, text='\u2002Move Stop After ' + string.tostring(moveAfter) + '% | ' + string.format('{0,number,currency}' + '\u2002', moveStopLossAfter))
        moveStopAfterLine = line.new(x1=strategy.opentrades.entry_bar_index(0), y1=moveStopLossAfter, x2=bar_index, y2=moveStopLossAfter, color=purple, width=1, xloc=xloc.bar_index, style=line.style_solid)
    stopLimitStatus = plot(stopLossLimitPrice, color=stopLossColor, display=display.price_scale)
    stopTriggerStatus = plot(stopLossTriggerPrice, color=stopLossColor, display=display.price_scale)
    averageEntryStatus = plot(averageEntryPrice, color=oceanBlue, display=display.price_scale)
    if not currentlyInAPosition:
        label.delete(stopLossLabel)
        label.delete(moveStopAfterLabel)
        label.delete(averageEntryLabel)
        label.delete(profitAndLossLabel)
        label.delete(profitTargetLabel)
        line.delete(stopLossTriggerLine)
        line.delete(moveStopAfterLine)
        line.delete(stopLossLimitLine)
        line.delete(averageEntryLine)
        line.delete(profitTargetLine)
        linefill.delete(stopLossBackground)
        linefill.delete(profitTargetBackground)
    warning_color = red if enableWebhookMessages == True else green
    status: Persistent[Table] = table.new(position=position.top_right, columns=2, rows=100, bgcolor=warning_color, border_color=warning_color, border_width=1)
    rowCount2: int = 0
    table.cell(status, 0, rowCount2, text='\u2002' + strategyIdentifier, text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    table.cell(status, 1, rowCount2, text='\u2002', text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    rowCount2 = rowCount2 + 1
    table.cell(status, 0, rowCount2, text='\u2002' + 'Webhook Enabled', text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    table.cell(status, 1, rowCount2, text=string.tostring(enableWebhookMessages) + '\u2002', text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    rowCount2 = rowCount2 + 1
    table.cell(status, 0, rowCount2, text='\u2002' + 'Exchange', text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    table.cell(status, 1, rowCount2, text=tradeAutomationExchange + '\u2002', text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    rowCount2 = rowCount2 + 1
    table.cell(status, 0, rowCount2, text='\u2002' + 'Code', text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    table.cell(status, 1, rowCount2, text='N/A' if tradeAutomationSecret == '' else tradeAutomationSecret + '\u2002', text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    rowCount2 = rowCount2 + 1
    table.cell(status, 0, rowCount2, text='\u2002' + 'Leverage', text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    table.cell(status, 1, rowCount2, text=string.tostring(tradeAutomationLeverageType) + ' ' + string.tostring(tradeAutomationLeverage) + 'x', text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    rowCount2 = rowCount2 + 1
    table.cell(status, 0, rowCount2, text='\u2002' + 'Pair', text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    table.cell(status, 1, rowCount2, text=string.tostring(symbol) + bot.getPairDividerForExchange(tradeAutomationExchange) + string.tostring(baseCurrency), text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    rowCount2 = rowCount2 + 1
    lotSizeDisplay = string.format('{0,number,percent}' + ' of account\u2002', lotSize / 100) if lotSizeType == 'Percent Of Account' else string.format('{0,number,currency}', lotSize)
    table.cell(status, 0, rowCount2, text='\u2002' + 'Lot Size', text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    table.cell(status, 1, rowCount2, text=lotSizeDisplay + '\u2002', text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    rowCount2 = rowCount2 + 1
    table.cell(status, 0, rowCount2, text='\u2002' + 'Account Size', text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    table.cell(status, 1, rowCount2, text=string.format('{0,number,currency}' + '\u2002', strategy.initial_capital), text_color=white, text_halign=text.align_left, bgcolor=warning_color, text_size=size.small)
    rowCount2 = rowCount2 + 1
    if showDebugTable:
        debug: Persistent[Table] = table.new(position=position.bottom_left, columns=2, rows=100, bgcolor=gray, border_color=gray, border_width=2)
        rowCount: int = 0
        table.cell(debug, 0, rowCount, text='enterLongAlertMessage: ', text_color=white, text_halign=text.align_left, bgcolor=gray, text_size=size.small)
        table.cell(debug, 1, rowCount, text=string.tostring(enterLongAlertMessage), text_color=white, text_halign=text.align_left, bgcolor=gray, text_size=size.small)
        rowCount = rowCount + 1
        table.cell(debug, 0, rowCount, text='enterShortAlertMessage: ', text_color=white, text_halign=text.align_left, bgcolor=gray, text_size=size.small)
        table.cell(debug, 1, rowCount, text=string.tostring(enterShortAlertMessage), text_color=white, text_halign=text.align_left, bgcolor=gray, text_size=size.small)
        rowCount = rowCount + 1
        table.cell(debug, 0, rowCount, text='exitLongAlertMessage: ', text_color=white, text_halign=text.align_left, bgcolor=gray, text_size=size.small)
        table.cell(debug, 1, rowCount, text=string.tostring(exitLongAlertMessage), text_color=white, text_halign=text.align_left, bgcolor=gray, text_size=size.small)
        rowCount = rowCount + 1
        table.cell(debug, 0, rowCount, text='exitShortAlertMessage: ', text_color=white, text_halign=text.align_left, bgcolor=gray, text_size=size.small)
        table.cell(debug, 1, rowCount, text=string.tostring(exitShortAlertMessage), text_color=white, text_halign=text.align_left, bgcolor=gray, text_size=size.small)
        rowCount = rowCount + 1
        table.cell(debug, 0, rowCount, text='moveStopTriggered: ', text_color=white, text_halign=text.align_left, bgcolor=gray, text_size=size.small)
        table.cell(debug, 1, rowCount, text=string.tostring(moveStopTriggered), text_color=white, text_halign=text.align_left, bgcolor=gray, text_size=size.small)
        rowCount = rowCount + 1
        table.cell(debug, 0, rowCount, text='longStopLoss (stopLossTriggerPrice): ', text_color=white, text_halign=text.align_left, bgcolor=gray, text_size=size.small)
        table.cell(debug, 1, rowCount, text=string.tostring(longStopLoss) + ' | ' + string.tostring(stopLossTriggerPrice), text_color=white, text_halign=text.align_left, bgcolor=gray, text_size=size.small)
        rowCount = rowCount + 1
        table.cell(debug, 0, rowCount, text='barsSinceOpen', text_color=white, text_halign=text.align_left, bgcolor=gray, text_size=size.small)
        table.cell(debug, 1, rowCount, text=string.tostring(barsSinceOpen), text_color=white, text_halign=text.align_left, bgcolor=gray, text_size=size.small)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
