"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, barstate, bgcolor, close, color, fill, high, input, location, low,
    math, na, open, plot, plotshape, position, request, script, shape, size, strategy, string,
    syminfo, ta, table, time, timeframe, volume
)
from pynecore.types import Persistent, Table

g_av: str = 'AutoView Settings [OANDA]'
g_pc: str = 'PineConnector Settings'


@script.strategy(title='3LS | 3 Line Strike Strategy [Kintsugi Trading]', overlay=True, process_orders_on_close=True, calc_on_every_tick=True, initial_capital=10000, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    showRiskReward=input(True, title='Show Risk/Reward Area', group='Risk Management'),
    takeLong=input(True, title='Enter Long Position', group='Risk Management'),
    takeShort=input(True, title='Enter Short Position', group='Risk Management'),
    stopType=input.string('Fix PIP Size', title='Stop Loss Strategy', options=('ATR Trail', 'ATR Trail-Stop', 'Fix PIP Size'), group='Risk Management'),
    atrPeriod=input(14, title='ATR Period', group='Risk Management', tooltip='Uses on ATR Trail-stop'),
    atrMultip=input.float(2.0, step=0.1, title='ATR Multiplier', group='Risk Management', tooltip='Uses on ATR Trail-stop'),
    riskMultip=input.float(1.0, title='Risk/Reward Ratio', minval=0.1, step=0.1, group='Risk Management'),
    __input_7__=input(3, title='Additional Stop PIP Size', group='Risk Management'),
    isSessionFilterActive=input.bool(False, title='Session Filter Active?', group='Session'),
    i_tz=input.string('GMT', title='Timezone: ', tooltip='e.g. \'America/New_York\', \'Asia/Tokyo\', \'GMT-4\', \'GMT+9\'...', group='Session'),
    sessionOneRange=input.session(title='Trade Session: ', defval='0900-1600', group='Session'),
    maFill=input(True, title='MA Cloud Fill', group='MA'),
    maPeriod1=input.int(21, title='MA Period Fast', group='MA'),
    maPeriod2=input.int(55, title='MA Period Slow', group='MA'),
    showVsa=input.bool(True, title='Show VSA Status?', group='VSA'),
    ma0_length=input.int(30, 'Moving Average', minval=1, group='VSA'),
    ma1_length=input.float(0.5, step=0.1, title='MA-1 Multiplier', group='VSA'),
    ma2_length=input.float(1.5, step=0.1, title='MA-2 Multiplier', group='VSA'),
    ma3_length=input.float(3.0, step=0.1, title='MA-3 Multiplier', group='VSA'),
    showBear3LS=input.bool(title='Show Bearish KT Signal', defval=True, group='3 Line Strike'),
    showBull3LS=input.bool(title='Show Bullish KT Signal', defval=True, group='3 Line Strike'),
    useCustomRisk=input(True, title='Use Custom Risk', group='Risk Calculation'),
    __input_22__=input.float(2.0, step=0.1, minval=0.1, title='% Risk Per Trade', group='Risk Calculation', tooltip='This value used only for backtest results not for auto trading.'),
    av_use=input.bool(title='Use AutoView?', defval=False, group=g_av, tooltip='If turned on then the alerts this script generates will use AutoView syntax for auto-trading (WARNING: USE AT OWN RISK! RESEARCH THE DANGERS)'),
    av_oandaDemo=input.bool(title='Use Oanda Demo?', defval=True, group=g_av, tooltip='If turned on then oandapractice broker prefix will be used for AutoView alerts (demo account). If turned off then live account will be used'),
    av_limitOrder=input.bool(title='Use Limit Order?', defval=True, group=g_av, tooltip='If turned on then AutoView will use limit orders. If turned off then market orders will be used'),
    av_accountBalance=input.float(title='Account Balance', defval=1000.0, step=100, group=g_av, tooltip='Your account balance (used for calculating position size)'),
    av_accountCurrency=input.string(title='Account Currency', defval='USD', options=('AUD', 'CAD', 'CHF', 'EUR', 'GBP', 'JPY', 'NZD', 'USD'), group=g_av, tooltip='Your account balance currency (used for calculating position size)'),
    av_riskPerTrade=input.float(title='Risk Per Trade %', defval=2.0, step=0.5, group=g_av, tooltip='Your risk per trade as a % of your account balance'),
    pc_use=input.bool(title='Use PineConnector?', defval=True, group=g_pc, tooltip='Use PineConnector Alerts? (WARNING: USE AT OWN RISK! RESEARCH THE DANGERS)'),
    pc_id=input.string(title='License ID', defval='ID', group=g_pc, tooltip='This is your PineConnector license ID'),
    pc_risk=input.float(title='Risk Per Trade', defval=1, step=0.5, group=g_pc, tooltip='This is how much to risk per trade (% of balance or lots - based on PC settings)'),
    pc_prefix=input.string(title='MetaTrader Prefix', defval='', group=g_pc, tooltip='This is your broker\'s MetaTrader symbol prefix (leave blank if there is none)'),
    pc_suffix=input.string(title='MetaTrader Suffix', defval='', group=g_pc, tooltip='This is your broker\'s MetaTrader symbol suffix (leave blank if there is none)')
):
    stopTickSize = __input_7__ * syminfo.mintick * 10
    ma0 = ta.sma(volume, ma0_length)
    ma1 = ma0 * ma1_length
    ma2 = ma0 * ma2_length
    ma3 = ma0 * ma3_length
    histColor = color.navy if volume < ma1 else color.green if volume < ma2 else color.yellow if volume < ma3 else color.red if volume > ma3 else color.gray
    volumeEntryCond = volume > ma2
    plotshape(-1 if showVsa else na, color=histColor, style=shape.square, location=location.bottom, size=size.auto, title='VSA Status')
    plotshape(-1 if showVsa else na, color=histColor, textcolor=histColor, text='VSA Status', style=shape.square, location=location.bottom, size=size.auto, title='VSA Label', show_last=1, offset=0)
    def getCandleColorIndex(barIndex):
        ret: int = na(int)
        if close[barIndex] > open[barIndex]:
            ret = 1
        elif close[barIndex] < open[barIndex]:
            ret = -1
        else:
            ret = 0
        return ret

    def isEngulfing(checkBearish):
        ret: bool = False
        sizePrevCandle = close[1] - open[1]
        sizeCurrentCandle = close - open
        isCurrentLagerThanPrevious = True if math.abs(sizeCurrentCandle) > math.abs(sizePrevCandle) else False
        __switch__ = checkBearish
        if __switch__ == True:
            getCandleColorIndex_1 = getCandleColorIndex(1)
            isGreenToRed = True if getCandleColorIndex(0) < 0 and getCandleColorIndex_1 > 0 else False
            ret = True if isCurrentLagerThanPrevious and isGreenToRed else False
        elif __switch__ == False:
            getCandleColorIndex_1 = getCandleColorIndex(1)
            isRedToGreen = True if getCandleColorIndex(0) > 0 and getCandleColorIndex_1 < 0 else False
            ret = True if isCurrentLagerThanPrevious and isRedToGreen else False
        else:
            ret = False
        return ret

    def isBearishEngulfuing():
        ret = isEngulfing(True)
        return ret

    def isBullishEngulfuing():
        ret = isEngulfing(False)
        return ret

    def is3LSBear():
        ret: bool = False
        getCandleColorIndex_1 = getCandleColorIndex(2)
        getCandleColorIndex_2 = getCandleColorIndex(3)
        is3LineSetup = True if getCandleColorIndex(1) > 0 and getCandleColorIndex_1 > 0 and (getCandleColorIndex_2 > 0) else False
        isBearishEngulfuing_1 = isBearishEngulfuing()
        ret = True if is3LineSetup and isBearishEngulfuing_1 else False
        return ret

    def is3LSBull():
        ret: bool = False
        getCandleColorIndex_1 = getCandleColorIndex(2)
        getCandleColorIndex_2 = getCandleColorIndex(3)
        is3LineSetup = True if getCandleColorIndex(1) < 0 and getCandleColorIndex_1 < 0 and (getCandleColorIndex_2 < 0) else False
        isBullishEngulfuing_1 = isBullishEngulfuing()
        ret = True if is3LineSetup and isBullishEngulfuing_1 else False
        return ret

    is3LSBearSig = is3LSBear()
    is3LSBullSig = is3LSBull()
    plotshape(is3LSBullSig if showBull3LS else na, style=shape.triangleup, color=color.rgb(0, 255, 0, 0), location=location.belowbar, size=size.small, text='KT-Bull', title='3 Line Strike Up')
    plotshape(is3LSBearSig if showBear3LS else na, style=shape.triangledown, color=color.rgb(255, 0, 0, 0), location=location.abovebar, size=size.small, text='KT-Bear', title='3 Line Strike Down')
    maxPercRisk = __input_22__ / 100
    symbol: Persistent = pc_prefix + syminfo.ticker + pc_suffix
    broker: Persistent = 'oandapractice' if av_oandaDemo else 'oanda'
    pair: Persistent = syminfo.basecurrency + '/' + syminfo.currency
    def pc_entry_alert(direction, entry, sl, tp):
        order_price = entry
        tp_value = ',tp=' + string.tostring(tp) if na(tp) == False else ''
        price = 'price=' + string.tostring(order_price)
        return pc_id + ',' + direction + ',' + symbol + ',' + price + ',sl=' + string.tostring(sl) + tp_value + ',risk=' + string.tostring(pc_risk)

    def pc_exit_alert(direction):
        return pc_id + ',' + direction + ',' + symbol

    def av_entry_alert(side, qty, entry, sl, tp):
        tp_value = ' ftp=' + string.tostring(tp) if na(tp) == False else ''
        return 'e=' + broker + ' b=' + side + ' q=' + string.tostring(qty) + ' s=' + pair + ' t=' + ('limit fp=' + string.tostring(entry) if av_limitOrder else 'market') + ' fsl=' + string.tostring(sl) + tp_value

    def av_exit_alert(side):
        return 'e=' + broker + ' s=' + pair + ' c=position b=' + side

    atr = ta.atr(14)
    def toWhole(number):
        returnVal = number / syminfo.mintick / (10 / syminfo.pointvalue) if atr < 1.0 else number
        returnVal = returnVal * 100 if atr >= 1.0 and atr < 100.0 and (syminfo.currency == 'JPY') else returnVal
        return returnVal

    tradePositionSize: Persistent[float] = 0.0
    accountSameAsCounterCurrency = av_accountCurrency == syminfo.currency
    accountSameAsBaseCurrency = av_accountCurrency == syminfo.basecurrency
    accountNeitherCurrency = not accountSameAsCounterCurrency and (not accountSameAsBaseCurrency)
    conversionCurrencyPair = syminfo.tickerid if accountSameAsCounterCurrency else av_accountCurrency + syminfo.currency if accountNeitherCurrency else av_accountCurrency + syminfo.currency
    conversionCurrencyRate = request.security(symbol=conversionCurrencyPair if syminfo.type == 'forex' else 'AUDUSD', timeframe='D', expression=close)
    def getPositionSize(stopLossSizePoints):
        riskAmount = av_accountBalance * (av_riskPerTrade / 100) * (conversionCurrencyRate if accountSameAsBaseCurrency or accountNeitherCurrency else 1.0)
        riskPerPoint = stopLossSizePoints * syminfo.pointvalue
        positionSize = riskAmount / riskPerPoint / syminfo.mintick
        return math.round(positionSize)

    atrValue = ta.atr(atrPeriod)
    in_session_one = time(timeframe.period, sessionOneRange, i_tz)
    sessionOneActive = cast_bool(in_session_one) and timeframe.multiplier <= 1440
    sessionFilterResult = sessionOneActive if isSessionFilterActive else True
    maValue1 = ta.sma(close, maPeriod1)
    maValue2 = ta.sma(close, maPeriod2)
    longStop: Persistent[float] = na(float)
    longRisk: Persistent[float] = na(float)
    longTp: Persistent[float] = na(float)
    shortStop: Persistent[float] = na(float)
    shortRisk: Persistent[float] = na(float)
    shortTp: Persistent[float] = na(float)
    entryAlertString: str = ''
    exitAlertString: str = ''
    fix_long_exit: str = 'Exit LONG'
    fix_short_exit: str = 'Exit SHORT'
    positionSize: Persistent[float] = 1
    def calcPositionSize(unitRisk):
        __block_result__ = na
        if useCustomRisk == False:
            __block_result__ = 1
        else:
            totalRisk = strategy.equity * maxPercRisk
            __block_result__ = math.round(totalRisk / unitRisk, 6)
        return __block_result__

    def calcAtrTrailStop(side):
        __block_result_1__ = na
        if side == 'long':
            tempStop = close - atrValue * atrMultip
            __block_result_1__ = tempStop if tempStop > longStop and tempStop < close else longStop
        else:
            tempStop = close + atrValue * atrMultip
            __block_result_1__ = tempStop if tempStop < shortStop and tempStop > close else shortStop
        return __block_result_1__

    if (stopType == 'ATR Trail-Stop' or stopType == 'ATR Trail') and strategy.position_size > 0:
        longStop = calcAtrTrailStop('long')
        if av_use:
            exitAlertString = av_exit_alert('long')
        elif pc_use:
            exitAlertString = pc_exit_alert('closelong')
        strategy.exit('Long Exit', 'Long', comment='EXIT LONG', stop=longStop, limit=longTp, alert_message=exitAlertString)
    if (stopType == 'ATR Trail-Stop' or stopType == 'ATR Trail') and strategy.position_size < 0:
        shortStop = calcAtrTrailStop('short')
        if av_use:
            exitAlertString = av_exit_alert('short')
        elif pc_use:
            exitAlertString = pc_exit_alert('closeshort')
        strategy.exit('Short Exit', 'Short', comment='EXIT SHORT', stop=shortStop, limit=shortTp, alert_message=exitAlertString)
    longCond = is3LSBullSig and volumeEntryCond and (maValue1 > maValue2)
    shortCond = is3LSBearSig and volumeEntryCond and (maValue1 < maValue2)
    if longCond and takeLong and sessionFilterResult and (strategy.position_size == 0) and barstate.isconfirmed and (strategy.equity > 0):
        longStop = low - stopTickSize if stopType == 'Fix PIP Size' else close - atrValue * atrMultip
        longRisk = close - longStop
        longTp = close + riskMultip * longRisk if stopType != 'ATR Trail' else na
        longStopDistance = close - longStop
        positionSize = calcPositionSize(longRisk)
        if av_use:
            entryAlertString = av_entry_alert('long', tradePositionSize, close, longStop, longTp)
            exitAlertString = fix_long_exit
        elif pc_use:
            entryAlertString = pc_entry_alert('buy', close, longStop, longTp)
            exitAlertString = fix_long_exit
        strategy.entry('Long', strategy.long, comment='LONG', qty=positionSize, alert_message=entryAlertString)
        if stopType != 'ATR Trail':
            strategy.exit('Long Exit', 'Long', comment='EXIT LONG', stop=longStop, limit=longTp, alert_message=exitAlertString)
        tradePositionSize = getPositionSize(toWhole(longStopDistance) * 10)
        if av_use:
            setTp = ' ftp=' + string.tostring(longTp) if na(longTp) == False else ''
            alert(message='e=' + broker + ' b=long q=' + string.tostring(tradePositionSize) + ' s=' + pair + ' t=' + ('stop fp=' + string.tostring(close) if av_limitOrder else 'market') + ' fsl=' + string.tostring(longStop) + setTp, freq=alert.freq_once_per_bar)
        if pc_use:
            alertString = pc_entry_alert('buystop', close, longStop, longTp)
            alert(alertString, alert.freq_once_per_bar_close)
    if shortCond and takeShort and sessionFilterResult and (strategy.position_size == 0) and barstate.isconfirmed and (strategy.equity > 0):
        shortStop = high + stopTickSize if stopType == 'Fix PIP Size' else close + atrValue * atrMultip
        shortRisk = shortStop - close
        shortTp = close - riskMultip * shortRisk if stopType != 'ATR Trail' else na
        shortStopDistance = math.abs(close - shortStop)
        positionSize = calcPositionSize(shortRisk)
        if av_use:
            entryAlertString = av_entry_alert('short', tradePositionSize, close, shortStop, shortTp)
            exitAlertString = fix_short_exit
        elif pc_use:
            entryAlertString = pc_entry_alert('sell', close, shortStop, shortTp)
            exitAlertString = fix_short_exit
        strategy.entry('Short', strategy.short, comment='SHORT', qty=positionSize, alert_message=entryAlertString)
        if stopType != 'ATR Trail':
            strategy.exit('Short Exit', 'Short', comment='EXIT SHORT', stop=shortStop, limit=shortTp, alert_message=exitAlertString)
        tradePositionSize = getPositionSize(toWhole(shortStopDistance) * 10)
        if av_use:
            setTp = ' ftp=' + string.tostring(shortTp) if na(shortTp) == False else ''
            alert(message='e=' + broker + ' b=short q=' + string.tostring(tradePositionSize) + ' s=' + pair + ' t=' + ('stop fp=' + string.tostring(close) if av_limitOrder else 'market') + ' fsl=' + string.tostring(shortStop) + setTp, freq=alert.freq_once_per_bar)
        if pc_use:
            alertString = pc_entry_alert('sellstop', close, shortStop, shortTp)
            alert(alertString, alert.freq_once_per_bar_close)
    p1 = plot(maValue1, title='MA Fast', color=color.green, linewidth=1)
    p2 = plot(maValue2, title='MA Slow', color=color.red, linewidth=1)
    fill(p1, p2, color=(color.new(color.green, 90) if maValue1 > maValue2 else color.new(color.red, 90)) if maFill else color.new(color.black, 100))
    L1 = plot(strategy.position_avg_price if showRiskReward and strategy.position_size > 0 else na, color=color.green, linewidth=1, style=plot.style_linebr, title='Long Entry Price')
    L2 = plot(longTp if showRiskReward and strategy.position_size > 0 else na, color=color.green, linewidth=1, style=plot.style_linebr, title='Long TP Price')
    L3 = plot(longStop if showRiskReward and strategy.position_size > 0 else na, color=color.red, linewidth=1, style=plot.style_linebr, title='Long Stop Price')
    S1 = plot(strategy.position_avg_price if showRiskReward and strategy.position_size < 0 else na, color=color.teal, linewidth=1, style=plot.style_linebr, title='Short Entry Price')
    S2 = plot(shortTp if showRiskReward and strategy.position_size < 0 else na, color=color.teal, linewidth=1, style=plot.style_linebr, title='Short TP Price')
    S3 = plot(shortStop if showRiskReward and strategy.position_size < 0 else na, color=color.maroon, linewidth=1, style=plot.style_linebr, title='Short Stop Price')
    fill(L1, L2, color=color.new(color.green, 90))
    fill(L1, L3, color=color.new(color.red, 90))
    fill(S1, S2, color=color.new(color.teal, 90))
    fill(S1, S3, color=color.new(color.maroon, 90))
    bgcolor(color.new(color.orange, 90) if sessionOneActive and isSessionFilterActive else na, title='Trade Session')
    nameDisplay: Persistent[Table] = table.new(position.middle_center, 1, 1, bgcolor=color.white, frame_width=0)
    if barstate.isconfirmed and math.round(strategy.equity, 0) <= 0:
        table.cell(nameDisplay, 0, 0, 'Total Equity dropped below ZERO.\nThese parameters are not useful.', text_color=color.white, bgcolor=color.red)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
