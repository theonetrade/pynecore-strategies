"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barstate, bgcolor, close, color, currency, high, input, low, na, nz,
    open, plot, script, strategy, string, ta, time, timeframe, timestamp
)
from pynecore.types import NA, Persistent, PersistentSeries, Series

longTradesTip: str = 'Turn on/off long trades. Perhaps you are overall bearish and wish to exempt long trades on this asset'
shortTradesTip: str = 'Turn on/off short trades. Perhaps you are overall bullish and wish to exempt long trades on this asset'
useLimitTip: str = 'Turns on/off the limit exit method. eg: using trail and not setting a limit exit. Must use trail, or strategy has no exit criteria'
trailStopTip: str = 'Turns on/off the ATR trailing stop exit method.'
FLIPTip: str = 'Allows a reversal trade. eg. flipping short from a long pos. False will isolate trades from one another, while true allows an opposite bias entry while in a position already'
setMaxDrawdownTip: str = 'Enables max drawdown protection. Enabling this will stop the bot if the overall strategy drawdown drops below the defined risk appetite'
RnRTip: str = 'This sets your risk to reward as a multiple. 1 is stop/limit equal distance from entry'
RiskMTip: str = 'Multiplier as a function of the ATR value projected from the calculated swing high/low. This allows for a buffer for your stop placing it behind support/resistance for the lookback period'
swinglookbackTip: str = 'This is your swing lookback. The the number of bars within the period calculated for lowest or highest value to establish a swing pivot'
maxPercDdTip: str = 'Risk appetite. Every strategy sees downside. This is how much you could stomach to allow the bot to lose if you let it run. Strategy stops taking trades below this level'
atrLenTip: str = 'Length of the period for the ATR to average'
trailStopSizeTip: str = 'The ATR multiplier for ATR-based trailing stop. Higher number yields a higher volatility based risk adjustment from the swing low'
trailSourceTip: str = 'The price source for calculating ATR trailing stop'
rrExitTip: str = 'This is the % of reward (target price) that must hit in order to trigger the trail expressed as a decimal. eg. 0.5 = 50% to target.'
maType1Tip: str = 'Sets the moving average type for the first MA'
maType2Tip: str = 'Sets the moving average type for the second MA'
maLength1Tip: str = 'Sets the length for the first MA. (it is likely best to keep MA1 length less than MA2, or it may result in opposite trade bias desired depending on MA type'
maLength2Tip: str = 'Sets the length for the second MA. (it is likely best to keep MA2 length greater than MA2, or it may result in opposite trade bias desired depending on MA type'
drawEntryTip: str = 'Shows the trade entry level'
exitLvlTip: str = 'Shows the level that the trailing stop is triggered'
useTimeFilterTip: str = 'Turns on/off time session filter'
timeSessionTip: str = 'Time session to ignore trades (useful for ignoring trades during times you don\'t want to trade. eg. Markets are slow for a period of time in the night)'
startTimeTip: str = 'Start date & time to begin backtest period. Also useful for beginning new bot. eg. Set time to now to make broker emulator in a flat position before setting alerts'
endTimeTip: str = 'End date & time to stop searching for setups for back testing.'


@script.strategy('3Commas Bot', 'Bj Bot', True, precision=3, default_qty_type=strategy.cash, commission_value=0.05, commission_type=strategy.commission.percent, slippage=1, currency=currency.USD, default_qty_value=10000, initial_capital=10000, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    longTrades=input.bool(True, 'Detect Long Trades', group='Trade variables', tooltip=longTradesTip),
    shortTrades=input.bool(True, 'Detect Short Trades', group='Trade variables', tooltip=shortTradesTip),
    useLimit=input.bool(True, 'Use Limit exit', group='Trade variables', tooltip=useLimitTip),
    trailStop=input.bool(False, 'Use ATR Trailing Stop', group='Trade variables', tooltip=trailStopTip),
    FLIP=input.bool(False, 'Allow Reversal Trades', group='Trade variables', tooltip=FLIPTip),
    setMaxDrawdown=input.bool(False, 'Set Max Total DrawDown', group='Trade variables', tooltip=setMaxDrawdownTip),
    RnR=input.float(1, 'Reward to Risk Ratio', group='Risk Management', tooltip=RnRTip, minval=0),
    RiskM=input.float(1, 'Risk Adjustment', group='Risk Management', tooltip=RiskMTip, minval=0),
    swinglookback=input.int(5, 'Swing Lookback', group='Risk Management', tooltip=swinglookbackTip),
    maxPercDd=input.int(20, 'Max Drawdown (%)', group='Risk Management', tooltip=maxPercDdTip),
    atrLen=input.int(14, 'ATR length', group='Risk Management', tooltip=atrLenTip),
    trailStopSize=input.float(1.0, 'ATR Trailing Stop Multiplier', group='Trailing Stop', tooltip=trailStopSizeTip),
    trailSource=input.string('High/Low', 'ATR Trailing Stop Source', group='Trailing Stop', tooltip=trailSourceTip, options=('High/Low', 'Close', 'Open')),
    rrExit=input.float(0.0, 'R:R To Trigger Exit', group='Trailing Stop', tooltip=rrExitTip),
    maType1=input.string('EMA', 'MA Type #1', group='MA Type', tooltip=maType1Tip, options=('EMA', 'HEMA', 'SMA', 'HMA', 'WMA', 'DEMA', 'VWMA', 'VWAP', 'T3')),
    maType2=input.string('EMA', 'MA Type #2', group='MA Type', tooltip=maType2Tip, options=('EMA', 'HEMA', 'SMA', 'HMA', 'WMA', 'DEMA', 'VWMA', 'VWAP', 'T3')),
    maLength1=input.int(21, 'MA Length #1', group='MA Settings', tooltip=maLength1Tip, minval=1),
    maLength2=input.int(50, 'MA Length #2', group='MA Settings', tooltip=maLength2Tip, minval=1),
    maBull1=input.color(color.new('#64B5F6'), '', inline='1', group='MA Color/ Transp/ Linewidth'),
    maBear1=input.color(color.new('#EF5350'), '', inline='1', group='MA Color/ Transp/ Linewidth'),
    maBull2=input.color(color.new('#64B5F6'), '', inline='2', group='MA Color/ Transp/ Linewidth'),
    maBear2=input.color(color.new('#EF5350'), '', inline='2', group='MA Color/ Transp/ Linewidth'),
    drawEntry=input.bool(False, 'Draw entry price', group='Display', tooltip=drawEntryTip),
    exitLvl=input.bool(True, 'Draw trail trigger price', group='Display', tooltip=exitLvlTip),
    useTimeFilter=input.bool(False, 'Use Time Session Filter', group='Filters', tooltip=useTimeFilterTip),
    timeSession=input.session('0000-0300', 'Time Session To Ignore Trades', group='Filters', tooltip=timeSessionTip),
    startTime=input.time(timestamp('01 Jan 2000 00:00 GMT-7'), 'Start Filter', group='Filters', tooltip=startTimeTip),
    endTime=input.time(timestamp('01 Jan 2099 00:00 GMT-7'), 'End Filter', group='Filters', tooltip=endTimeTip)
):
    FLAT = strategy.position_size == 0
    LONG = strategy.position_size > 0
    SHORT = strategy.position_size < 0
    confirmed = barstate.isconfirmed
    entry = strategy.position_avg_price
    lookForExit: Persistent[bool] = False
    tradeStopPrice: Persistent[float] = 0.0
    tradeTargetPrice: Persistent[float] = 0.0
    trailingStop: Persistent[float] = 0.0
    tradeExitTriggerPrice: PersistentSeries[float] = 0.0
    tradeStopDistance: Persistent[float] = 0.0
    tradeTriggerPrice: Persistent[float] = 0.0
    def _haOpen():
        haClose: Series = (open + high + low + close) / 4
        haOpen: Series = NA(float)
        haOpen = (open + close) / 2 if na(haOpen[1]) else (nz(haOpen[1]) + nz(haClose[1])) / 2
        return haOpen

    HaOpen = _haOpen()
    def getMA(type, length):
        maPrice = ta.ema(close, length)
        if type == 'HEMA':
            maPrice = ta.ema(HaOpen, length)
        if type == 'SMA':
            maPrice = ta.sma(close, length)
        if type == 'HMA':
            maPrice = ta.hma(close, length)
        if type == 'WMA':
            maPrice = ta.wma(close, length)
        if type == 'VWMA':
            maPrice = ta.vwma(close, length)
        if type == 'VWAP':
            maPrice = ta.vwap
        if type == 'DEMA':
            e1 = ta.ema(close, length)
            e2 = ta.ema(e1, length)
            maPrice = 2 * e1 - e2
        if type == 'T3':
            axe1 = ta.ema(close, length)
            axe2 = ta.ema(axe1, length)
            axe3 = ta.ema(axe2, length)
            axe4 = ta.ema(axe3, length)
            axe5 = ta.ema(axe4, length)
            axe6 = ta.ema(axe5, length)
            ab: float = 0.7
            ac1 = -ab * ab * ab
            ac2 = 3 * ab * ab + 3 * ab * ab * ab
            ac3 = -6 * ab * ab - 3 * ab - 3 * ab * ab * ab
            ac4 = 1 + 3 * ab + ab * ab * ab + 3 * ab * ab
            maPrice = ac1 * axe6 + ac2 * axe5 + ac3 * axe4 + ac4 * axe3
        return maPrice

    def isInSession(sess):
        return na(time(timeframe.period, sess + ':1234567', 'GMT-6')) == False

    ma1: Series = getMA(maType1, maLength1)
    ma2: Series = getMA(maType2, maLength2)
    atr = ta.atr(atrLen)
    lowestLow = ta.lowest(low, swinglookback)
    highestHigh = ta.highest(high, swinglookback)
    isInSession_1 = isInSession(timeSession)
    timeFilter = useTimeFilter and (not isInSession_1) or not useTimeFilter
    dateFilter = time >= startTime and time <= endTime
    withinTime = timeFilter and dateFilter
    ma1CrossUp2 = ta.crossover(ma1, ma2)
    ma1CrossDn2 = ta.crossunder(ma1, ma2)
    validLongEntry = ma1CrossUp2 and (not na(atr))
    validShortEntry = ma1CrossDn2 and (not na(atr))
    condmaxdrawdown = maxPercDd if setMaxDrawdown else 100
    ma1Con = ma1 >= ma1[1]
    ma2Con = ma2 >= ma2[1]
    ma1Col = maBull1 if ma1Con else maBear1
    ma2Col = maBull2 if ma2Con else maBear2
    if LONG and trailStop and lookForExit and confirmed:
        trailSrcLong = close[1] if trailSource == 'Close' else open[1] if trailSource == 'Open' else lowestLow
        trail = trailSrcLong - atr * trailStopSize
        needsUpdate = trail > trailingStop
        trailingStop = trail if needsUpdate else trailingStop
    if SHORT and trailStop and lookForExit and confirmed:
        trailSrcShort = close[1] if trailSource == 'Close' else open[1] if trailSource == 'Open' else highestHigh
        trail = trailSrcShort + atr * trailStopSize
        needsUpdate = trail < trailingStop
        trailingStop = trail if needsUpdate else trailingStop
    longStop = lowestLow - atr * RiskM
    shortStop = highestHigh + atr * RiskM
    longRisk = close - longStop
    shortRisk = shortStop - close
    longlimit = close + RnR * longRisk
    shortlimit = close - RnR * shortRisk
    longLimitDist = close - longlimit
    shortLimitDist = shortlimit - close
    if validShortEntry and (FLAT or (LONG and FLIP)) and confirmed and withinTime and shortTrades:
        tradeStopPrice = shortStop
        tradeTargetPrice = shortlimit if useLimit else na
        tradeExitTriggerPrice = close + shortLimitDist * rrExit
        lookForExit = False
        trailingStop = tradeStopPrice
    else:
        validShortEntry = False
    if validLongEntry and (FLAT or (SHORT and FLIP)) and confirmed and withinTime and longTrades:
        tradeStopPrice = longStop
        tradeTargetPrice = longlimit if useLimit else na
        tradeExitTriggerPrice = close - longLimitDist * rrExit
        lookForExit = False
        trailingStop = tradeStopPrice
    else:
        validLongEntry = False
    if LONG and rrExit != 0.0 and (high >= tradeExitTriggerPrice) and trailStop or (rrExit == 0.0 and trailStop):
        lookForExit = True
    if SHORT and rrExit != 0.0 and (low <= tradeExitTriggerPrice) and trailStop or (rrExit == 0.0 and trailStop):
        lookForExit = True
    drawOrders: Series = validLongEntry or validShortEntry or (not FLAT)
    stopPrice: Series = trailingStop if trailStop else tradeStopPrice
    targetPrice: Series = na if lookForExit and (not useLimit) else tradeTargetPrice
    drawExit = SHORT and tradeExitTriggerPrice > targetPrice and (tradeExitTriggerPrice < entry) or (LONG and tradeExitTriggerPrice < targetPrice and (tradeExitTriggerPrice > entry))
    plotExitPrice = (tradeExitTriggerPrice if drawOrders else tradeExitTriggerPrice[1]) if (drawExit and trailStop or (trailStop and (not useLimit))) and (drawOrders or drawOrders[1]) and (not lookForExit) else na
    plotStopPrice = (stopPrice if drawOrders else stopPrice[1]) if drawOrders or drawOrders[1] else na
    plotTarget = (targetPrice if drawOrders else targetPrice[1]) if drawOrders or drawOrders[1] else na
    plot(entry if drawEntry else na, 'Entry Price', color.new('#9598A1'), style=plot.style_linebr)
    plot(plotExitPrice if exitLvl else na, 'Trigger Exit', color.blue, style=plot.style_linebr)
    plot(plotStopPrice, 'Stop Price', color.red, style=plot.style_linebr)
    plot(plotTarget, 'Target Price', color.green, style=plot.style_linebr)
    plot(ma1, 'Moving Average #1', ma1Col)
    plot(ma2, 'Moving Average #2', ma2Col)
    isInSession_2 = isInSession(timeSession)
    bgcolor(color=color.new(color.red, 80) if useTimeFilter and isInSession_2 or not dateFilter else na, title='Filter Color')
    Long: str = '    {  "message_type": "bot",  "bot_id": 4635591,  "email_token": "25byourtefcodeuufyd2-43314-ab98-bjorg224",  "delay_seconds": 1}  '
    ExitLong: str = '    {  "message_type": "bot",  "bot_id": 4635591,  "email_token": "25byourtefcodeuufyd2-43314-ab98-bjorg224",  "delay_seconds": 0,  "action": "close_at_market_price"}  '
    Goshort: str = '    {  "message_type": "bot",  "bot_id": 4635690,  "email_token": "25byourtefcodeuufyd2-43314-ab98-bjorg224",  "delay_seconds": 1}  '
    ExitShort: str = '    {  "message_type": "bot",  "bot_id": 4635690,  "email_token": "25byourtefcodeuufyd2-43314-ab98-bjorg224",  "delay_seconds": 0,  "action": "close_at_market_price"}  '
    enterLong = string.format('[{0}, {1}]', ExitShort, Long) if SHORT and validLongEntry else Long
    enterShort = string.format('[{0}, {1}]', ExitLong, Goshort) if LONG and validShortEntry else Goshort
    strategy.risk.max_drawdown(value=condmaxdrawdown, type=strategy.percent_of_equity)
    if validLongEntry:
        strategy.entry('Long', strategy.long, comment='Long', alert_message=enterLong)
    strategy.exit('Long Exit', from_entry='Long', stop=trailingStop if trailStop else tradeStopPrice, limit=tradeTargetPrice, comment='L Exit', alert_message=ExitLong)
    if validShortEntry:
        strategy.entry('Short', strategy.short, comment='Short', alert_message=enterShort)
    strategy.exit('Short Exit', from_entry='Short', stop=trailingStop if trailStop else tradeStopPrice, limit=tradeTargetPrice, comment='S Exit', alert_message=ExitShort)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
