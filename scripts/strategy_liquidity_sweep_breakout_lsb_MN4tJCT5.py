"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, array, bar_index, barstate, box, close, color, high, hour, input,
    label, line, linefill, low, math, minute, na, script, strategy, string, syminfo, time,
    timeframe
)
from pynecore.types import Box, Label, Line, LineFill, Persistent, Series


@script.strategy('Liquidity Sweep Breakout - LSB', overlay=True, pyramiding=0, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    rrRatio=input.float(1.5, title='Reward:Risk Ratio', minval=0.1),
    riskModel=input.string('Fixed Dollar', title='Risk Model', options=('Fixed Dollar', 'Percentage of Equity', 'Conservative'), group='Risk Management'),
    riskDollarAmount=input.float(100, 'Risk Amount ($)', minval=1, tooltip='Exact dollar amount to risk on SL', group='Risk Management'),
    __input_3__=input.float(1.0, 'Risk % of Equity', minval=0.1, maxval=100, step=0.1, group='Risk Management'),
    accountBalance=input.float(10000, 'Account Balance ($)', minval=100, group='Risk Management'),
    profitPerPip=input.float(0.693, title='Profit per Pip (per 0.1 lot)', tooltip='Set profit per pip for your instrument (0.69 for JPY pairs)', group='Risk Management'),
    enableAlerts=input.bool(True, title='🔔 Enable Custom Alerts', group='Alert Settings', tooltip='Enable custom alert messages with visual values'),
    pineConnectorKey=input.string('123456789', title='Enter EA License Key:', group='Alert Settings', tooltip='Your EA license key for webhook alerts'),
    alertMessageBox=input.string('{{alert_message}}', title='Alert Messgae Box Text formate:', group='Alert Settings', tooltip='The default text code format to generate an alert.'),
    alertComment=input.string('AutoLSB', title='Alert Trade Comment:', group='Alert Settings', tooltip='This comment will be sent with each trade to appear in the comment section of every trade.'),
    magicLineStyle=input.string('Dashed', title='Magic Lines Style', options=('Solid', 'Dashed', 'Dotted')),
    tradeLineStyle=input.string('Solid', title='Trade Lines Style', options=('Solid', 'Dashed', 'Dotted')),
    showShadedAreas=input.bool(True, title='Show TP/SL Shaded Areas'),
    showExtendedTag=input.bool(True, title='Show Extended Tag'),
    showTPSTTag=input.bool(True, title='Show TP/SL Tags'),
    showMagicCandle=input.bool(True, title='Show Magic Candle Mark'),
    showTradeLines=input.bool(True, title='Show Trade Lines'),
    plotSessionBox=input.bool(True, title='Show Tokyo Session Box'),
    showBuySellTags=input.bool(True, title='Show Buy/Sell Tags'),
    keepOriginalStyle=input.bool(True, title='Keep Original Style After TP/SL'),
    useExtendedLines=input.bool(False, title='Extended Trade Lines', group='Visual Settings', tooltip='Extend trade lines further right on chart')
):
    riskPercentage = __input_3__ / 100
    tokyoHigh: Persistent[float] = na(float)
    tokyoLow: Persistent[float] = na(float)
    sessionBox: Persistent[Box] = na(Box)
    brkHigh: Persistent[float] = na(float)
    brkLow: Persistent[float] = na(float)
    brkHighLine: Persistent[Line] = na(Line)
    brkLowLine: Persistent[Line] = na(Line)
    inTrade: Persistent[bool] = False
    entryPrice: Persistent[float] = na(float)
    slPrice: Persistent[float] = na(float)
    tpPrice: Persistent[float] = na(float)
    lotSize: Persistent[float] = na(float)
    entryLine: Persistent[Line] = na(Line)
    slLine: Persistent[Line] = na(Line)
    tpLine: Persistent[Line] = na(Line)
    riskArea: Persistent[LineFill] = na(LineFill)
    rewardArea: Persistent[LineFill] = na(LineFill)
    tradeExecuted: Persistent[bool] = False
    tradeDirection: Persistent[int] = 0
    exitReached: Persistent[bool] = False
    entryBarIndex: Persistent[int] = na(int)
    noTrade: Persistent[bool] = False
    exitLabel: Persistent[Label] = na(Label)
    tokyoSession: Series = time(timeframe.period, '2000-0500:1234567')
    if cast_bool(tokyoSession) and (not tokyoSession[1]):
        tokyoHigh = high
        tokyoLow = low
        if plotSessionBox:
            sessionBox = box.new(left=bar_index, right=bar_index, top=high, bottom=low, bgcolor=color.new(color.new('#FF5272'), 93), border_color=color.new('#FF525253'))
    elif cast_bool(tokyoSession):
        tokyoHigh = math.max(tokyoHigh, high)
        tokyoLow = math.min(tokyoLow, low)
        if plotSessionBox and (not na(sessionBox)):
            box.set_right(sessionBox, bar_index)
            box.set_top(sessionBox, tokyoHigh)
            box.set_bottom(sessionBox, tokyoLow)
    isBreakoutTime = hour == 20 and minute == 54
    if isBreakoutTime and showMagicCandle:
        brkHigh = high
        brkLow = low
        magicStyleChoice = line.style_solid if magicLineStyle == 'Solid' else line.style_dashed if magicLineStyle == 'Dashed' else line.style_dotted
        brkHighLine = line.new(bar_index, brkHigh, bar_index + 36, brkHigh, color=color.new('#BEBEBE'), width=1, style=magicStyleChoice)
        brkLowLine = line.new(bar_index, brkLow, bar_index + 36, brkLow, color=color.new('#BEBEBE'), width=1, style=magicStyleChoice)
    def calculateTMBLotSize(entry, sl):
        __block_result__ = na
        if riskModel == 'Fixed Dollar':
            __block_result__ = riskDollarAmount
        elif riskModel == 'Percentage of Equity':
            __block_result__ = accountBalance * riskPercentage
        else:
            __block_result__ = math.min(riskDollarAmount, accountBalance * riskPercentage)
        riskAmount = __block_result__
        slPips = math.abs(entry - sl) * 10000
        calculatedLotSize = riskAmount / (slPips * profitPerPip) * 10
        finalLotSize = math.round(calculatedLotSize / 0.01) * 0.01
        return math.max(0.01, math.min(finalLotSize, 10.0))

    checkTimes: list[str] = array.from_items('21:30', '21:45', '22:00', '22:15', '22:30', '22:45', '23:00', '23:15', '23:30')
    currentTime = string.tostring(hour, '00') + ':' + string.tostring(minute, '00')
    isCheckTime = array.includes(checkTimes, currentTime) and barstate.isconfirmed
    if isCheckTime and (not na(brkHighLine)) and (currentTime != '23:30') and (not inTrade):
        line.set_x2(brkHighLine, bar_index + 36)
        line.set_x2(brkLowLine, bar_index + 36)
    if isCheckTime and currentTime == '23:30' and (not na(brkHighLine)) and (not inTrade):
        line.set_x2(brkHighLine, bar_index)
        line.set_x2(brkLowLine, bar_index)
    def getLineExtension():
        return 500 if useExtendedLines else 36

    if isCheckTime and (not inTrade) and (not tradeExecuted) and (not na(brkHigh)) and (high >= brkLow) and (low <= brkHigh) and (not noTrade) and showExtendedTag:
        if currentTime != '23:30':
            label.new(bar_index, tokyoLow, 'Extend', style=label.style_label_down, color=color.new('#EBBC76'))
    if isCheckTime and (not inTrade) and (currentTime == '23:30') and (not na(brkHigh)) and (high >= brkLow) and (low <= brkHigh) and (not tradeExecuted):
        noTrade = True
        label.new(bar_index, tokyoLow, 'NO TRADE DAY', style=label.style_label_down, color=color.gray, textcolor=color.white)
    validLongBreakout = not na(brkHigh) and close > brkHigh and (low > brkHigh)
    if isCheckTime and (not inTrade) and (not tradeExecuted) and validLongBreakout and (not noTrade):
        if showMagicCandle and (not na(brkHighLine)):
            line.set_x2(brkHighLine, bar_index)
            line.set_x2(brkLowLine, bar_index)
        entryPrice = close
        slPrice = tokyoLow
        tpPrice = entryPrice + (entryPrice - slPrice) * rrRatio
        lotSize = calculateTMBLotSize(entryPrice, slPrice)
        inTrade = True
        tradeExecuted = True
        tradeDirection = 1
        strategy.entry('LSB_Buy', strategy.long, qty=lotSize, comment='LSB_Long')
        strategy.exit('LSB_BuyExit', 'LSB_Buy', stop=slPrice, limit=tpPrice)
        lineExtension = getLineExtension()
        if showTradeLines:
            tradeStyleChoice = line.style_solid if tradeLineStyle == 'Solid' else line.style_dashed if tradeLineStyle == 'Dashed' else line.style_dotted
            entryLine = line.new(bar_index, entryPrice, bar_index + lineExtension, entryPrice, color=color.new('#D1FFFF'), width=1, style=tradeStyleChoice)
            slLine = line.new(bar_index, slPrice, bar_index + lineExtension, slPrice, color=color.new('#C7444E'), width=2, style=tradeStyleChoice)
            tpLine = line.new(bar_index, tpPrice, bar_index + lineExtension, tpPrice, color=color.new('#008954'), width=2, style=tradeStyleChoice)
            if showShadedAreas:
                riskArea = linefill.new(entryLine, slLine, color.new(color.new('#FF5252'), 90))
                rewardArea = linefill.new(entryLine, tpLine, color.new(color.new('#00AF6C'), 90))
        if showBuySellTags:
            labelY = high + (high - low) * 0.5
            label.new(bar_index, labelY, 'LSB BUY\nEntry: ' + string.tostring(entryPrice, '#.####') + '\nSL: ' + string.tostring(slPrice, '#.####') + '\nTP: ' + string.tostring(tpPrice, '#.####') + '\nLots: ' + string.tostring(lotSize, '#.##'), style=label.style_label_down, color=color.new('#008954'), textcolor=color.white)
        if enableAlerts:
            actionType: str = 'buy'
            currentTicker = syminfo.ticker
            alertMessage = pineConnectorKey + ',' + actionType + ',' + currentTicker + ',risk=' + string.tostring(lotSize, '#.##') + ',sl=' + string.tostring(slPrice, '#.####') + ',tp=' + string.tostring(tpPrice, '#.####') + ',comment=' + string.tostring(alertComment)
            alert(alertMessage, alert.freq_once_per_bar)
    validShortBreakout = not na(brkLow) and close < brkLow and (high < brkLow)
    if isCheckTime and (not inTrade) and (not tradeExecuted) and validShortBreakout and (not noTrade):
        if showMagicCandle and (not na(brkHighLine)):
            line.set_x2(brkHighLine, bar_index)
            line.set_x2(brkLowLine, bar_index)
        entryPrice = close
        slPrice = tokyoHigh
        tpPrice = entryPrice - (slPrice - entryPrice) * rrRatio
        lotSize = calculateTMBLotSize(entryPrice, slPrice)
        inTrade = True
        tradeExecuted = True
        tradeDirection = -1
        strategy.entry('LSB_Sell', strategy.short, qty=lotSize, comment='LSB_Short')
        strategy.exit('LSB_SellExit', 'LSB_Sell', stop=slPrice, limit=tpPrice)
        lineExtension = getLineExtension()
        if showTradeLines:
            tradeStyleChoice = line.style_solid if tradeLineStyle == 'Solid' else line.style_dashed if tradeLineStyle == 'Dashed' else line.style_dotted
            entryLine = line.new(bar_index, entryPrice, bar_index + lineExtension, entryPrice, color=color.new('#D1FFFF'), width=1, style=tradeStyleChoice)
            slLine = line.new(bar_index, slPrice, bar_index + lineExtension, slPrice, color=color.new('#C7444E'), width=2, style=tradeStyleChoice)
            tpLine = line.new(bar_index, tpPrice, bar_index + lineExtension, tpPrice, color=color.new('#008954'), width=2, style=tradeStyleChoice)
            if showShadedAreas:
                riskArea = linefill.new(entryLine, slLine, color.new(color.new('#FF5252'), 90))
                rewardArea = linefill.new(entryLine, tpLine, color.new(color.new('#00AF6C'), 90))
        if showBuySellTags:
            labelY = low - (high - low) * 0.5
            label.new(bar_index, labelY, 'LSB SELL\nEntry: ' + string.tostring(entryPrice, '#.####') + '\nSL: ' + string.tostring(slPrice, '#.####') + '\nTP: ' + string.tostring(tpPrice, '#.####') + '\nLots: ' + string.tostring(lotSize, '#.##'), style=label.style_label_up, color=color.new('#C7444E'), textcolor=color.white)
        if enableAlerts:
            actionType: str = 'sell'
            currentTicker = syminfo.ticker
            alertMessage = pineConnectorKey + ',' + actionType + ',' + currentTicker + ',risk=' + string.tostring(lotSize, '#.##') + ',sl=' + string.tostring(slPrice, '#.####') + ',tp=' + string.tostring(tpPrice, '#.####') + ',comment=' + string.tostring(alertComment)
            alert(alertMessage, alert.freq_once_per_bar)
    if inTrade:
        if showTradeLines:
            lineExtension = getLineExtension()
            line.set_x2(entryLine, bar_index + lineExtension)
            line.set_x2(slLine, bar_index + lineExtension)
            line.set_x2(tpLine, bar_index + lineExtension)
        tpHit = high >= tpPrice if tradeDirection == 1 else low <= tpPrice
        slHit = low <= slPrice if tradeDirection == 1 else high >= slPrice
        if tpHit or slHit:
            if showTradeLines:
                line.set_x2(entryLine, bar_index)
                line.set_x2(slLine, bar_index)
                line.set_x2(tpLine, bar_index)
                if not keepOriginalStyle:
                    if tpHit:
                        linefill.delete(riskArea)
                        line.set_color(tpLine, color.blue)
                    else:
                        linefill.delete(rewardArea)
                        line.set_color(slLine, color.new('#FF5252'))
            if showTPSTTag:
                exitText = ('LSB BUY TP' if tradeDirection == 1 else 'LSB SELL TP') if tpHit else 'LSB BUY SL' if tradeDirection == 1 else 'LSB SELL SL'
                labelColor = color.blue if tpHit else color.new('#FF5252')
                exitPrice = tpPrice if tpHit else slPrice
                labelStyle = label.style_label_down if tradeDirection == 1 else label.style_label_up
                exitLabel = label.new(bar_index, exitPrice, exitText, style=labelStyle, color=labelColor, textcolor=color.white)
            inTrade = False
            exitReached = True
    if hour == 15 and minute == 0:
        if inTrade:
            if showTradeLines:
                line.set_x2(entryLine, bar_index)
                line.set_x2(slLine, bar_index)
                line.set_x2(tpLine, bar_index)
                if not keepOriginalStyle:
                    linefill.delete(riskArea)
                    linefill.delete(rewardArea)
            if showTPSTTag:
                exitLabel = label.new(bar_index, close, 'LSB EOD Close', style=label.style_label_down, color=color.gray, textcolor=color.white)
            strategy.close_all(comment='LSB_EOD')
            inTrade = False
        tradeExecuted = False
        tradeDirection = 0
        noTrade = False
    if hour == 0 and minute == 0:
        inTrade = False
        noTrade = False
        tradeExecuted = False
        tradeDirection = 0


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
