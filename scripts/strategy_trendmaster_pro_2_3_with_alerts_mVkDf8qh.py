"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from enum import StrEnum as Enum
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, array, bar_index, barmerge, barstate, close, color, fill, format,
    high, hour, input, label, line, low, math, matrix, minute, na, plot, request, runtime, script,
    strategy, string, syminfo, ta, time, time_close, timeframe, xloc, year
)
from pynecore.types import Color, Label, Line, Matrix, NA, Persistent, Series


class SLOption(Enum):
    Percent = '%'
    MACross = 'MA Cross'
    Band = 'Band'


class TSOption(Enum):
    Percent = '%'
    Ticks = 'Ticks'


@udt
class graphicSettings:
    levelName: str = na(str)
    levelColor: Color = na(Color)
    showLevel: bool = na(bool)


@udt
class pivotGraphic:
    pivotLine: Line = na(Line)
    pivotLabel: Label = na(Label)


DEFAULT_COLOR: Color = color.new('#FB8C00')
tpslGroup: str = 'TP | SL'


@script.strategy("TrendMaster Pro 2.3 with Alerts", max_lines_count=500, overlay=True)
def main(
    maType=input.string("SMA", title="MA Type", options=("EMA", "SMA", "SMMA"), group="MA Settings", tooltip="Select the type of Moving Average: EMA, SMA, or SMMA."),
    enableTrendFilter=input.bool(False, title="Enable Higher Timeframe Trend", group="Higher Timeframe Trend", tooltip="If enabled, only trades in the trend direction will be executed."),
    trendMaType=input.string("EMA", title="Trend MA Type", options=("EMA", "SMA", "SMMA"), group="Higher Timeframe Trend", tooltip="Select the type of Moving Average for the higher timeframe trend."),
    trendMaLength=input.int(50, title="Trend MA Length", group="Higher Timeframe Trend", tooltip="The length of the Moving Average for the higher timeframe trend."),
    shortMALength=input.int(9, title="Short-Term MA Length", group="MA Settings", tooltip="The length of the short Moving Average used for signal generation."),
    longMALength=input.int(21, title="Long-Term MA Length", group="MA Settings", tooltip="The length of the long Moving Average used for signal generation."),
    bandLength=input.int(20, title="Band Length", minval=1, group="Band Power", tooltip="The length of the bands. A higher length smooths the bands more but reacts slower to price changes."),
    bandType=input.int(2, title="Band Type", options=(1, 2, 3), group="Band Power", tooltip="1 = Fast, more noise, good for volatile markets.\n2 = Medium, balanced, good for general use.\n3 = Slow, very smooth, good for calm markets."),
    showSupportResistance=input.bool(False, title="Show Support & Resistance", group="Support & Resistance"),
    pivotTypeInput=input.string(title="Calculation Method", defval="Traditional", options=("Traditional", "Fibonacci", "Woodie", "Classic", "DM", "Camarilla"), group="Support & Resistance"),
    pivotAnchorInput=input.string(title="Timeframe", defval="Auto", options=("Auto", "Daily", "Weekly", "Monthly", "Quarterly", "Yearly", "Biyearly", "Triyearly", "Quinquennially", "Decennially"), group="Support & Resistance"),
    isDailyBasedInput=input.bool(title="Use Daily-Based Values", defval=True, group="Support & Resistance", tooltip="If disabled, the support/resistance levels use intraday data for calculations on intraday charts."),
    maxHistoricalPivotsInput=input.int(title="Number of Historical Levels", defval=1, minval=1, maxval=200, group="Support & Resistance"),
    showLabelsInput=input.bool(title="Show Labels", defval=True, group="Display Options"),
    showPricesInput=input.bool(title="Show Prices", defval=True, group="Display Options"),
    positionLabelsInput=input.string("Left", "Label Position", options=("Left", "Right"), group="Display Options"),
    linewidthInput=input.int(title="Line Width", defval=1, minval=1, maxval=100, group="Display Options"),
    pColorInput=input.color(DEFAULT_COLOR, "Midline", inline="Midline", group="Colors"),
    pShowInput=input.bool(True, "", inline="Midline", group="Colors"),
    s1ColorInput=input.color(DEFAULT_COLOR, "S1", inline="S1/R1", group="Colors"),
    s1ShowInput=input.bool(True, "", inline="S1/R1", group="Colors"),
    r1ColorInput=input.color(DEFAULT_COLOR, "R1", inline="S1/R1", group="Colors"),
    r1ShowInput=input.bool(True, "", inline="S1/R1", group="Colors"),
    s2ColorInput=input.color(DEFAULT_COLOR, "S2", inline="S2/R2", group="Colors"),
    s2ShowInput=input.bool(True, "", inline="S2/R2", group="Colors"),
    r2ColorInput=input.color(DEFAULT_COLOR, "R2", inline="S2/R2", group="Colors"),
    r2ShowInput=input.bool(True, "", inline="S2/R2", group="Colors"),
    s3ColorInput=input.color(DEFAULT_COLOR, "S3", inline="S3/R3", group="Colors"),
    s3ShowInput=input.bool(True, "", inline="S3/R3", group="Colors"),
    r3ColorInput=input.color(DEFAULT_COLOR, "R3", inline="S3/R3", group="Colors"),
    r3ShowInput=input.bool(True, "", inline="S3/R3", group="Colors"),
    s4ColorInput=input.color(DEFAULT_COLOR, "S4", inline="S4/R4", group="Colors"),
    s4ShowInput=input.bool(True, "", inline="S4/R4", group="Colors"),
    r4ColorInput=input.color(DEFAULT_COLOR, "R4", inline="S4/R4", group="Colors"),
    r4ShowInput=input.bool(True, "", inline="S4/R4", group="Colors"),
    s5ColorInput=input.color(DEFAULT_COLOR, "S5", inline="S5/R5", group="Colors"),
    s5ShowInput=input.bool(True, "", inline="S5/R5", group="Colors"),
    r5ColorInput=input.color(DEFAULT_COLOR, "R5", inline="S5/R5", group="Colors"),
    r5ShowInput=input.bool(True, "", inline="S5/R5", group="Colors"),
    asiaEnabled=input.bool(True, title='Asia  ', inline='Asia'),
    sessionAsiaTime=input.session('1800-0000', title='', inline='Asia'),
    colorAsia=input.color(color.new(color.yellow, 90), title='', inline='Asia'),
    londonEnabled=input.bool(True, title='London ', inline='London'),
    sessionLondonTime=input.session('0000-0800', title='', inline='London'),
    colorLondon=input.color(color.new(color.blue, 90), title='', inline='London'),
    nyAmEnabled=input.bool(True, title='NY AM ', inline='NYAM'),
    sessionNYAMTime=input.session('0800-1300', title='', inline='NYAM'),
    colorNYAM=input.color(color.new(color.orange, 90), title='', inline='NYAM'),
    nyPmEnabled=input.bool(True, title='NY PM ', inline='NYPM'),
    sessionNYPMTime=input.session('1300-1800', title='', inline='NYPM'),
    colorNYPM=input.color(color.new(color.purple, 90), title='', inline='NYPM'),
    showMon=input.bool(True, title='Mon', inline='Session Weekdays'),
    showTue=input.bool(True, title='Tue', inline='Session Weekdays'),
    showWed=input.bool(True, title='Wed', inline='Session Weekdays'),
    showThu=input.bool(True, title='Thur', inline='Session Weekdays'),
    showFri=input.bool(True, title='Fri', inline='Session Weekdays'),
    maxTradesPerSessionAsia=input.int(5, minval=0, title='Asia: Max Trades Per Session'),
    maxTradesPerSessionLondon=input.int(5, minval=0, title='London: Max Trades Per Session'),
    maxTradesPerSessionNYAM=input.int(5, minval=0, title='NY AM: Max Trades Per Session'),
    maxTradesPerSessionNYPM=input.int(5, minval=0, title='NY PM: Max Trades Per Session'),
    marketCloseHour=input.int(18, minval=0, maxval=23, title='Market Close Hour/Minute', inline='MarketClose'),
    marketCloseMinute=input.int(0, minval=0, maxval=59, title='', inline='MarketClose'),
    useAutoRisk=input.bool(False, title='Auto Risk, Min/Max $:', inline='AutoRisk'),
    autoRiskAmountMin=input.int(150, title='', inline='AutoRisk'),
    autoRiskAmountMax=input.int(250, title='', inline='AutoRisk'),
    fixedContactSize=input.float(5, title='Fixed Contact Size'),
    tpReachedLimit=input.int(3, minval=0, title='TP Reached Limit'),
    slReachedLimit=input.int(3, minval=0, title='SL Reached Limit'),
    rrRatio=input.float(title='Risk/Reward Ratio (1 : *)', step=0.1, defval=2, group=tpslGroup),
    useSL=input.bool(True, title='SL Option | %', inline='SL', group=tpslGroup),
    slOption=input.enum(SLOption.Percent, title='', inline='SL', group=tpslGroup),
    slPercent=input.float(1, minval=0.1, step=0.1, title='', inline='SL', group=tpslGroup),
    useTP=input.bool(True, title='TP', inline='TP', group=tpslGroup),
    alertEnabled=input.bool(True, title="Enable Alerts", group="Alert Settings"),
    alertMessageBuy=input.text_area("Buy Signal", title="Buy Alert Message", group="Alert Settings"),
    alertMessageSell=input.text_area("Sell Signal", title="Sell Alert Message", group="Alert Settings")
):
    atrLength: int = 14
    useAtrMultiplier: bool = True
    atrMultiplierSL: float = 2.0

    useVolatilityFilter: bool = True
    useTrendFilter: bool = True
    bbLength: int = 20
    bbMultiplier: float = 2.0

    useRSI: bool = True
    rsiLength: int = 14
    rsiLongThreshold: int = 55
    rsiShortThreshold: int = 45

    useMACD: bool = True
    macdFastLength: int = 12
    macdSlowLength: int = 26
    macdSignalSmoothing: int = 9

    useStochastic: bool = True
    stochLength: int = 14
    stochSmoothing: int = 3
    stochOverbought: int = 80
    stochOversold: int = 20

    useADX: bool = True
    adxLength: int = 14
    adxThreshold: int = 25

    riskRewardRatio: float = 2.0
    slTicksOffset: int = 5

    atr = ta.atr(atrLength)

    stopLossOffset = atr * atrMultiplierSL if useAtrMultiplier else atr

    def smma(src, len):
        smma__0000002e__: Series[float] = 0.0
        smma__0000002e__ = ta.sma(src, len) if na(smma__0000002e__[1]) else (smma__0000002e__[1] * (len - 1) + src) / len
        return smma__0000002e__

    shortMA = ta.ema(close, shortMALength) if maType == 'EMA' else ta.sma(close, shortMALength) if maType == 'SMA' else smma(close, shortMALength)
    longMA = ta.ema(close, longMALength) if maType == 'EMA' else ta.sma(close, longMALength) if maType == 'SMA' else smma(close, longMALength)
    buyCondition = ta.crossover(shortMA, longMA)
    sellCondition = ta.crossunder(shortMA, longMA)

    def _getSlopes(source1: float, source2: float):
        m1 = ta.change(source1)
        m2 = ta.change(source2)
        return (m1, m2)

    def _commonScalingFactor(source1: float, source2: float, m1: float, m2: float):
        return (source1 - source2) / (m1 - m2)

    def _crossingValue(source1: float, source2: float):
        out: float = na(float)
        m1, m2 = _getSlopes(source1, source2)
        if ta.cross(source1, source2):
            out = source1 - m1 * _commonScalingFactor(source1, source2, m1, m2)
        return out

    maCrossValue: Persistent[float] = na(float)
    if ta.cross(shortMA, longMA):
        maCrossValue = _crossingValue(shortMA, longMA)

    trendMA = ta.ema(close, trendMaLength) if trendMaType == 'EMA' else ta.sma(close, trendMaLength) if trendMaType == 'SMA' else smma(close, trendMaLength)

    trendFilterLong = not enableTrendFilter or close > trendMA
    trendFilterShort = not enableTrendFilter or close < trendMA

    basis: Persistent[float] = na(float)
    upperBand: Persistent[float] = na(float)
    lowerBand: Persistent[float] = na(float)
    if useVolatilityFilter or useTrendFilter:
        basis = ta.sma(close, bbLength)
        dev = ta.stdev(close, bbLength)
        upperBand = basis + bbMultiplier * dev
        lowerBand = basis - bbMultiplier * dev

    atrValue = ta.atr(bbLength)
    volatilityFilter = not useVolatilityFilter or upperBand - lowerBand > atrValue * bbMultiplier

    bbTrendFilterLong = not useTrendFilter or close > basis
    bbTrendFilterShort = not useTrendFilter or close < basis

    rsi = ta.rsi(close, rsiLength)

    rsiFilterLong = not useRSI or rsi > rsiLongThreshold
    rsiFilterShort = not useRSI or rsi < rsiShortThreshold

    macdLine, signalLine, _ = ta.macd(close, macdFastLength, macdSlowLength, macdSignalSmoothing)

    macdFilterLong = not useMACD or macdLine > signalLine
    macdFilterShort = not useMACD or macdLine < signalLine

    k = ta.sma(ta.stoch(close, high, low, stochLength), stochSmoothing)
    d = ta.sma(k, stochSmoothing)

    stochFilterLong = not useStochastic or (k > stochOversold and k > d)
    stochFilterShort = not useStochastic or (k < stochOverbought and k < d)

    plusDI, minusDI, adx = ta.dmi(adxLength, adxLength)

    adxFilter = not useADX or adx > adxThreshold

    buyConditionFiltered = buyCondition and volatilityFilter and bbTrendFilterLong and rsiFilterLong and macdFilterLong and stochFilterLong and adxFilter and trendFilterLong
    sellConditionFiltered = sellCondition and volatilityFilter and bbTrendFilterShort and rsiFilterShort and macdFilterShort and stochFilterShort and adxFilter and trendFilterShort

    __block_result__ = na
    if bandType == 1:
        __block_result__ = ta.ema(high, bandLength)
    elif bandType == 2:
        __block_result__ = ta.sma(high, bandLength)
    else:
        __block_result__ = smma(high, bandLength)
    maHigh = __block_result__

    __block_result_1__ = na
    if bandType == 1:
        __block_result_1__ = ta.ema(low, bandLength)
    elif bandType == 2:
        __block_result_1__ = ta.sma(low, bandLength)
    else:
        __block_result_1__ = smma(low, bandLength)
    maLow = __block_result_1__

    plot(maHigh, color=color.green, title='High Band', linewidth=1)
    plot(maLow, color=color.red, title='Low Band', linewidth=1)

    def isInSession(sess: str, res: str = timeframe.period):
        out = not na(time(res, sess))
        return out

    def _addSessionWeekdays(sessionString):
        out = sessionString
        hasAnySelected = showMon or showTue or showWed or showThu or showFri
        if hasAnySelected:
            out = sessionString + ':'
            if showMon:
                out += '2'
            if showTue:
                out += '3'
            if showWed:
                out += '4'
            if showThu:
                out += '5'
            if showFri:
                out += '6'
        return out

    sessionAsia = _addSessionWeekdays(sessionAsiaTime)
    sessionLondon = _addSessionWeekdays(sessionLondonTime)
    sessionNYAM = _addSessionWeekdays(sessionNYAMTime)
    sessionNYPM = _addSessionWeekdays(sessionNYPMTime)

    inAsiaSession: Series = asiaEnabled and isInSession(sessionAsia)
    inLondonSession: Series = londonEnabled and isInSession(sessionLondon)
    inNYAMSession: Series = nyAmEnabled and isInSession(sessionNYAM)
    inNYPMSession: Series = nyPmEnabled and isInSession(sessionNYPM)



    def _bracketPercentage(price, sign, value):
        return price * (1 + sign * value / 100)

    def _tp(p, s, sl, rrr):
        return p + math.sign(s) * rrr * math.abs(p - sl)

    def _sl(p, s):
        sign = math.sign(s)
        __block_result_2__ = na
        __switch__ = slOption
        if __switch__ == SLOption.MACross:
            __block_result_2__ = maCrossValue
        elif __switch__ == SLOption.Band:
            __block_result_2__ = maLow if sign == 1 else maHigh if sign == -1 else na
        else:
            __block_result_2__ = _bracketPercentage(p, -sign, slPercent)
        return __block_result_2__

    longQty: Persistent[float] = na(float)
    longEntry: Persistent[float] = na(float)
    longTP: Persistent[float] = na(float)
    longSL: Persistent[float] = na(float)
    longTPTriggered: Persistent[int] = 0
    longSLTriggered: Persistent[int] = 0

    shortQty: Persistent[float] = na(float)
    shortEntry: Persistent[float] = na(float)
    shortTP: Persistent[float] = na(float)
    shortSL: Persistent[float] = na(float)
    shortTPTriggered: Persistent[int] = 0
    shortSLTriggered: Persistent[int] = 0

    entryPrice: Persistent[float] = na(float)
    isInTradingSession = False or inAsiaSession or inLondonSession or inNYAMSession or inNYPMSession

    tradesPerSessionCounterAsia: Persistent[int] = 0
    tradesPerSessionCounterLondon: Persistent[int] = 0
    tradesPerSessionCounterNYAM: Persistent[int] = 0
    tradesPerSessionCounterNYPM: Persistent[int] = 0

    if inAsiaSession and (not inAsiaSession[1]):
        tradesPerSessionCounterAsia = strategy.closedtrades

    if inLondonSession and (not inLondonSession[1]):
        tradesPerSessionCounterLondon = strategy.closedtrades

    if inNYAMSession and (not inNYAMSession[1]):
        tradesPerSessionCounterNYAM = strategy.closedtrades

    if inNYPMSession and (not inNYPMSession[1]):
        tradesPerSessionCounterNYPM = strategy.closedtrades

    def canGoLong():
        return True and isInTradingSession and (False or (inAsiaSession and strategy.closedtrades < tradesPerSessionCounterAsia + maxTradesPerSessionAsia) or (inLondonSession and strategy.closedtrades < tradesPerSessionCounterLondon + maxTradesPerSessionLondon) or (inNYAMSession and strategy.closedtrades < tradesPerSessionCounterNYAM + maxTradesPerSessionNYAM) or (inNYPMSession and strategy.closedtrades < tradesPerSessionCounterNYPM + maxTradesPerSessionNYPM)) and (longSLTriggered < slReachedLimit) and (longTPTriggered < tpReachedLimit)

    def canGoShort():
        return True and isInTradingSession and (False or (inAsiaSession and strategy.closedtrades < tradesPerSessionCounterAsia + maxTradesPerSessionAsia) or (inLondonSession and strategy.closedtrades < tradesPerSessionCounterLondon + maxTradesPerSessionLondon) or (inNYAMSession and strategy.closedtrades < tradesPerSessionCounterNYAM + maxTradesPerSessionNYAM) or (inNYPMSession and strategy.closedtrades < tradesPerSessionCounterNYPM + maxTradesPerSessionNYPM)) and (shortSLTriggered < slReachedLimit) and (shortTPTriggered < tpReachedLimit)

    longEntrySignal = buyConditionFiltered
    shortEntrySignal = sellConditionFiltered

    longExitSignal = shortEntrySignal
    shortExitSignal = longEntrySignal

    def _calcEntryQty(sl):
        slInTicks = sl / syminfo.mintick
        slInMoney = slInTicks * syminfo.pointvalue
        contracts = math.round(autoRiskAmountMax / slInMoney, 0)

        riskPerContracts = contracts * slInMoney

        out = contracts if autoRiskAmountMin <= riskPerContracts and riskPerContracts <= autoRiskAmountMax else 0
        return out

    if hour == marketCloseHour and minute == marketCloseMinute:
        longSLTriggered = 0
        longTPTriggered = 0
        shortSLTriggered = 0
        shortTPTriggered = 0
        strategy.cancel_all()
        strategy.close_all('End of Session', immediately=True)

    if (strategy.position_size == 0 or strategy.position_size < 0) and longEntrySignal and canGoLong():
        if strategy.position_size < 0:
            strategy.close('Short Entry', comment='Close Position Short', immediately=True)

        entryPrice = close
        longSL = _sl(entryPrice, 1) if useSL else na
        longQty = _calcEntryQty(longSL) if useAutoRisk else fixedContactSize
        if longQty > 0:
            strategy.entry('Long Entry', strategy.long, qty=longQty, comment='Long')

    if strategy.position_size[1] <= 0 and strategy.position_size > 0:
        longEntry = entryPrice
        longTP = _tp(strategy.position_avg_price, strategy.position_size, longSL, rrRatio) if useTP else na
        strategy.exit('Long Exit', from_entry='Long Entry', limit=longTP if useTP else na, stop=longSL if useSL else na, comment_profit='Long TP', comment_loss='Long SL')

    if (strategy.position_size == 0 or strategy.position_size > 0) and shortEntrySignal and canGoShort():
        if strategy.position_size > 0:
            strategy.close('Long Entry', comment='Close Position Long', immediately=True)

        entryPrice = close
        shortSL = _sl(entryPrice, -1) if useSL else na
        shortQty = _calcEntryQty(shortSL) if useAutoRisk else fixedContactSize
        if shortQty > 0:
            strategy.entry('Short Entry', strategy.short, qty=shortQty, comment='Short')

    if strategy.position_size[1] >= 0 and strategy.position_size < 0:
        shortEntry = entryPrice
        shortTP = _tp(strategy.position_avg_price, strategy.position_size, shortSL, rrRatio) if useTP else na
        strategy.exit('Short Exit', from_entry='Short Entry', limit=shortTP if useTP else na, stop=shortSL if useSL else na, comment_profit='Short TP', comment_loss='Short SL')

    if strategy.position_size > 0 and longExitSignal:
        strategy.close('Long Entry', comment='Close Position Long', immediately=True)

    if strategy.position_size < 0 and shortExitSignal:
        strategy.close('Short Entry', comment='Close Position Short', immediately=True)

    if strategy.position_size[1] > 0 and strategy.position_size <= 0:
        longEntry = na
        longQty = na
        longTP = na
        longSL = na

        if low <= longSL:
            longSLTriggered += 1
        elif high >= longTP:
            longTPTriggered += 1

    if strategy.position_size[1] < 0 and strategy.position_size >= 0:
        shortEntry = na
        shortQty = na
        shortTP = na
        shortSL = na

        if high >= shortSL:
            shortSLTriggered += 1
        elif low <= shortTP:
            shortTPTriggered += 1

    slPlot1 = plot(longSL if strategy.position_size > 0 else na, title='Long SL', color=color.red, linewidth=1, style=plot.style_steplinebr, force_overlay=True)
    entryPlot1 = plot(longEntry if strategy.position_size > 0 else na, title='Long Entry', color=color.blue, linewidth=1, style=plot.style_steplinebr, force_overlay=True)
    tpPlot1 = plot(longTP if strategy.position_size > 0 else na, title='Long TP', color=color.green, linewidth=1, style=plot.style_steplinebr, force_overlay=True)

    slPlot2 = plot(shortSL if strategy.position_size < 0 else na, title='Short SL', color=color.red, linewidth=1, style=plot.style_steplinebr, force_overlay=True)
    entryPlot2 = plot(shortEntry if strategy.position_size < 0 else na, title='Short Entry', color=color.blue, linewidth=1, style=plot.style_steplinebr, force_overlay=True)
    tpPlot2 = plot(shortTP if strategy.position_size < 0 else na, title='Short TP', color=color.green, linewidth=1, style=plot.style_steplinebr, force_overlay=True)

    fill(slPlot1, entryPlot1, color=color.new(color.red, 85))
    fill(slPlot2, entryPlot2, color=color.new(color.red, 85))
    fill(entryPlot1, tpPlot1, color=color.new(color.green, 85))
    fill(entryPlot2, tpPlot2, color=color.new(color.green, 85))

    if alertEnabled and buyConditionFiltered:
        alert(alertMessageBuy, alert.freq_once_per_bar)

    if alertEnabled and sellConditionFiltered:
        alert(alertMessageSell, alert.freq_once_per_bar)

    graphicSettingsArray: Persistent = array.from_items(graphicSettings('Midline', pColorInput, pShowInput and showSupportResistance), graphicSettings('R1', r1ColorInput, r1ShowInput and showSupportResistance), graphicSettings('S1', s1ColorInput, s1ShowInput and showSupportResistance), graphicSettings('R2', r2ColorInput, r2ShowInput and showSupportResistance), graphicSettings('S2', s2ColorInput, s2ShowInput and showSupportResistance), graphicSettings('R3', r3ColorInput, r3ShowInput and showSupportResistance), graphicSettings('S3', s3ColorInput, s3ShowInput and showSupportResistance), graphicSettings('R4', r4ColorInput, r4ShowInput and showSupportResistance), graphicSettings('S4', s4ColorInput, s4ShowInput and showSupportResistance), graphicSettings('R5', r5ColorInput, r5ShowInput and showSupportResistance), graphicSettings('S5', s5ColorInput, s5ShowInput and showSupportResistance))

    __block_result_3__ = na
    if timeframe.isintraday:
        __block_result_3__ = '1D' if timeframe.multiplier <= 15 else '1W'
    elif timeframe.isdaily:
        __block_result_3__ = "1M"
    else:
        __block_result_3__ = "12M"
    autoAnchor = __block_result_3__

    __block_result_4__ = na
    __switch__ = pivotAnchorInput
    if __switch__ == "Auto":
        __block_result_4__ = autoAnchor
    elif __switch__ == "Daily":
        __block_result_4__ = "1D"
    elif __switch__ == "Weekly":
        __block_result_4__ = "1W"
    elif __switch__ == "Monthly":
        __block_result_4__ = "1M"
    elif __switch__ == "Quarterly":
        __block_result_4__ = "3M"
    else:
        __block_result_4__ = "12M"
    pivotTimeframe = __block_result_4__

    __block_result_5__ = na
    __switch__ = pivotAnchorInput
    if __switch__ == "Biyearly":
        __block_result_5__ = 2
    elif __switch__ == "Triyearly":
        __block_result_5__ = 3
    elif __switch__ == "Quinquennially":
        __block_result_5__ = 5
    elif __switch__ == "Decennially":
        __block_result_5__ = 10
    else:
        __block_result_5__ = 1
    pivotYearMultiplier = __block_result_5__

    __block_result_6__ = na
    __switch__ = pivotTypeInput
    if __switch__ == "Traditional":
        __block_result_6__ = 11
    elif __switch__ == "Camarilla":
        __block_result_6__ = 11
    elif __switch__ == "Woodie":
        __block_result_6__ = 9
    elif __switch__ == "Classic":
        __block_result_6__ = 9
    elif __switch__ == "Fibonacci":
        __block_result_6__ = 7
    elif __switch__ == "DM":
        __block_result_6__ = 3
    numOfPivotLevels = __block_result_6__

    @method
    def delete(graphic: pivotGraphic):
        line.delete(graphic.pivotLine)
        return label.delete(graphic.pivotLabel)

    drawnGraphics: Persistent[Matrix[pivotGraphic]] = matrix.new(initial_value=NA(pivotGraphic))

    localPivotTimeframeChange = timeframe.change(pivotTimeframe) and year % pivotYearMultiplier == 0
    securityPivotTimeframeChange = timeframe.change(timeframe.period) and year % pivotYearMultiplier == 0

    def pivotTimeframeChangeCounter(condition):
        count: Persistent[int] = 0
        if condition and bar_index > 0:
            count += 1
        return count

    localPivots = ta.pivot_point_levels(pivotTypeInput, localPivotTimeframeChange)
    securityPivotPointsArray = ta.pivot_point_levels(pivotTypeInput, securityPivotTimeframeChange)

    securityTimeframe = '1D' if timeframe.isintraday else timeframe.period
    securityPivotCounter: Series
    securityPivots, securityPivotCounter = request.security(syminfo.tickerid, pivotTimeframe, (securityPivotPointsArray, pivotTimeframeChangeCounter(securityPivotTimeframeChange)), lookahead=barmerge.lookahead_on)
    pivotPointsArray = securityPivots if isDailyBasedInput else localPivots

    def affixOldPivots(endTime):
        __block_result_7__ = na
        if matrix.rows(drawnGraphics) > 0:
            lastGraphics = matrix.row(drawnGraphics, matrix.rows(drawnGraphics) - 1)

            __block_result_8__ = na
            for graphic in lastGraphics:
                method_call('set_x2', graphic.pivotLine, endTime)
                __block_result_9__ = na
                if positionLabelsInput == 'Right':
                    __block_result_9__ = method_call('set_x', graphic.pivotLabel, endTime)
                __block_result_8__ = __block_result_9__
            __block_result_7__ = __block_result_8__
        return __block_result_7__

    def drawNewPivots(startTime):
        newGraphics: list[pivotGraphic] = array.new(0, NA(pivotGraphic))

        for index, coord in enumerate(pivotPointsArray):
            levelSettings = method_call('get', graphicSettingsArray, index)
            if not na(coord) and levelSettings.showLevel:
                lineEndTime = startTime + timeframe.in_seconds(pivotTimeframe) * 1000 * pivotYearMultiplier
                pivotLine__0000012a__ = line.new(startTime, coord, lineEndTime, coord, xloc=xloc.bar_time, color=levelSettings.levelColor, width=linewidthInput)
                pivotLabel__0000012a__ = label.new(x=startTime if positionLabelsInput == 'Left' else lineEndTime, y=coord, text=(levelSettings.levelName + ' ' if showLabelsInput else '') + ('(' + string.tostring(coord, format.mintick) + ')' if showPricesInput else ''), style=label.style_label_right if positionLabelsInput == 'Left' else label.style_label_left, textcolor=levelSettings.levelColor, color=color.new('#00000000'), xloc=xloc.bar_time)

                array.push(newGraphics, pivotGraphic(pivotLine__0000012a__, pivotLabel__0000012a__))

        matrix.add_row(drawnGraphics, array_id=newGraphics)

        __block_result_10__ = na
        if matrix.rows(drawnGraphics) > maxHistoricalPivotsInput:
            oldGraphics = matrix.remove_row(drawnGraphics, 0)

            __block_result_11__ = na
            for graphic in oldGraphics:
                __block_result_11__ = method_call(delete, graphic)
            __block_result_10__ = __block_result_11__
        return __block_result_10__

    localPivotDrawConditionStatic = not isDailyBasedInput and localPivotTimeframeChange
    securityPivotDrawConditionStatic = isDailyBasedInput and securityPivotCounter != securityPivotCounter[1]

    isMultiYearly: Persistent[list[str]] = method_call('includes', array.from_items('Biyearly', 'Triyearly', 'Quinquennially', 'Decennially'), pivotAnchorInput)
    localPivotDrawConditionDeveloping = not isDailyBasedInput and time_close == time_close(pivotTimeframe) and (not isMultiYearly)
    securityPivotDrawConditionDeveloping: bool = False

    if securityPivotDrawConditionStatic or localPivotDrawConditionStatic:
        affixOldPivots(time)
        drawNewPivots(time)

    FIRST_BAR_TIME: Persistent = time
    if barstate.islastconfirmedhistory and matrix.columns(drawnGraphics) == 0:
        if not na(securityPivots) and securityPivotCounter > 0:
            if isDailyBasedInput:
                drawNewPivots(FIRST_BAR_TIME)
            else:
                runtime.error("Not enough intraday data to calculate Support/Resistance Levels. Lower the Timeframe or turn on the 'Use Daily-based Values' option in the indicator settings.")
        else:
            runtime.error('Not enough data to calculate Support/Resistance Levels. Lower the Timeframe in the indicator settings.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
