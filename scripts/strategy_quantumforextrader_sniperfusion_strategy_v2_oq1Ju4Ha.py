"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.series import inline_series
from pynecore.lib import (
    bar_index, barcolor, barmerge, barstate, close, color, extend, fill,
    format, high, hlc3, hour, input, label, line, location, low, math, na, nz, open, plot,
    plotshape, position, request, script, shape, size, strategy, string, syminfo, ta, table, text,
    time, timeframe, volume
)
from pynecore.types import Label, Line, Persistent, Series, Table

group_analysis: str = "=== Quantum Core ==="
group_filters: str = "=== Trend Filters ==="
group_sniper: str = "=== Sniper Logic ==="
group_signal: str = "=== Signal Generation ==="
group_hold: str = "=== Trade Lifecycle Gates ==="
group_risk: str = "=== Risk Management ==="
group_tsl: str = "=== Trailing Stop Loss ==="
group_exits: str = "=== Responsive Exits ==="
group_visual: str = "=== Visuals ==="
group_time: str = "=== Trading Schedule ==="


@script.strategy("QuantumForexTrader_SOLUSDT_SniperFusion_Strategy_v2", overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.05, slippage=2, pyramiding=0, calc_on_every_tick=False, process_orders_on_close=True, max_labels_count=500, max_lines_count=500, max_boxes_count=100, max_bars_back=5000)
def main(
    historyBars=input.int(72, "History bars for analysis", group=group_analysis, minval=32, maxval=4096),
    confThreshold=input.float(0.54, "Minimum confidence", group=group_analysis, step=0.01),
    momentumThreshold=input.float(0.08, "Minimum momentum", group=group_analysis, step=0.01),
    memoryDecay=input.float(0.88, "Memory decay", group=group_analysis, minval=0.5, maxval=0.99, step=0.01),
    memoryThreshold=input.float(0.05, "Memory threshold", group=group_analysis, minval=0.01, maxval=1.0, step=0.01),
    useEMAfilter=input.bool(True, "Use EMA Trend Filter", group=group_filters),
    useMTFfilter=input.bool(True, "Use higher timeframe trend filter", group=group_filters),
    useVolFilter=input.bool(True, "Use Volume Filter", group=group_filters),
    useATRfilter=input.bool(True, "Use ATR Volatility Filter", group=group_filters),
    useCandleFilter=input.bool(True, "Use Candle Body Filter", group=group_filters),
    trendEmaLen=input.int(34, "Trend EMA Length", group=group_filters),
    mtfTf=input.timeframe("5", "MTF Trend TF", group=group_filters),
    volLookback=input.int(24, "Volume SMA Length", group=group_filters),
    volMultiplier=input.float(1.0, "Min Relative Volume", group=group_filters, step=0.05),
    atrLen=input.int(14, "ATR Length", group=group_filters),
    atrMaLen=input.int(21, "ATR SMA Length", group=group_filters),
    atrMultiplier=input.float(0.95, "Min ATR vs ATR-SMA", group=group_filters, step=0.05),
    bodyRatioMin=input.float(0.35, "Min Candle Body Ratio", group=group_filters, step=0.05),
    useSniperBiasFilter=input.bool(True, "Require sniper bias alignment", group=group_sniper),
    sniperMinPct=input.float(57.0, "Minimum sniper score %", group=group_sniper, minval=40, maxval=100, step=1),
    useSniperCrossTrigger=input.bool(True, "Allow EMA 9/21 cross trigger", group=group_sniper),
    strongBiasDiff=input.float(40.0, "Strong bias difference", group=group_sniper, minval=10, maxval=100, step=5),
    signalIntervalMin=input.int(3, "Signal interval (minutes)", group=group_signal, minval=1, maxval=240),
    signalScoreMin=input.int(8, "Minimum total score", group=group_signal, minval=1, maxval=20),
    signalEdgeMin=input.int(2, "Minimum score edge", group=group_signal, minval=0, maxval=20),
    minMoveAtr=input.float(0.3, "Min move from last signal (ATR)", group=group_signal, step=0.05),
    includePriceInAlert=input.bool(True, "Include price in webhook", group=group_signal),
    useCloseActionForExit=input.bool(True, "Use close instead of reverse-open", group=group_signal),
    allowLongs=input.bool(True, "Allow long entries", group=group_signal),
    allowShorts=input.bool(False, "Allow short entries (PF short was 1.002 in audit)", group=group_signal),
    minHoldBars=input.int(3, "Min bars in trade before any signal-based exit", group=group_hold, minval=0),
    earlyExitAfterTP1=input.bool(True, "Early exits only after TP1 hit", group=group_hold),
    slAtrMultiplier=input.float(1.5, "SL ATR Multiplier", group=group_risk, minval=0.1, step=0.1),
    useTakeProfits=input.bool(True, "Use TP1-TP5 partial exits (20% each)", group=group_risk),
    tpStepR=input.float(1.0, "TP step (R multiples of initial risk)", group=group_risk, minval=0.5, step=0.25),
    useTrailingStop=input.bool(True, "Use Trailing Stop Loss", group=group_tsl),
    tslAtrMultiplier=input.float(1.5, "TSL ATR Multiplier", group=group_tsl, minval=0.1, step=0.1),
    tslActivationAtr=input.float(0.5, "TSL Activation (ATR)", group=group_tsl, minval=0.0, step=0.1, tooltip="Profit in ATR needed to activate trailing stop. 0 = active immediately."),
    useEarlyExit=input.bool(True, "Enable Early Reversal Exits", group=group_exits),
    exitEmaLength=input.int(9, "Fast EMA Length for Exit", group=group_exits),
    useRsiExit=input.bool(True, "Use RSI Exhaustion Exit", group=group_exits),
    rsiLength=input.int(14, "RSI Length", group=group_exits),
    rsiOverbought=input.int(75, "RSI Overbought (Long Exit)", group=group_exits),
    rsiOversold=input.int(25, "RSI Oversold (Short Exit)", group=group_exits),
    showDashboard=input.bool(True, "Show sniper dashboard", group=group_visual),
    showRibbon=input.bool(True, "Show EMA ribbon", group=group_visual),
    showTargets=input.bool(True, "Show ATR targets", group=group_visual),
    showSignalLabels=input.bool(True, "Show entry/exit markers", group=group_visual),
    showVwap=input.bool(True, "Show VWAP", group=group_visual),
    ribbonOpacity=input.int(75, "EMA Ribbon Opacity", group=group_visual, minval=0, maxval=100),
    dashTextSizeStr=input.string("small", "Dashboard font size", options=("tiny", "small", "normal", "large", "huge"), group=group_visual),
    tradeTextSizeStr=input.string("small", "Trade label size", options=("tiny", "small", "normal", "large", "huge"), group=group_visual),
    labelOffset=input.int(12, "Label right offset (bars)", minval=1, group=group_visual),
    useTimeFilter=input.bool(False, "Use time filter", group=group_time),
    startHour=input.int(7, "Start trading hour", group=group_time, minval=0, maxval=23),
    endHour=input.int(23, "End trading hour", group=group_time, minval=0, maxval=23)
):
    def getTextSize(s: str):
        __block_result__ = na
        __switch__ = s
        if __switch__ == "tiny":
            __block_result__ = size.tiny
        elif __switch__ == "normal":
            __block_result__ = size.normal
        elif __switch__ == "large":
            __block_result__ = size.large
        elif __switch__ == "huge":
            __block_result__ = size.huge
        else:
            __block_result__ = size.small
        return __block_result__

    def inSession():
        __block_result_1__ = na
        if not useTimeFilter:
            __block_result_1__ = True
        else:
            h: int = hour(time, syminfo.timezone)
            __block_result_1__ = h >= startHour and h < endHour if startHour <= endHour else h >= startHour or h < endHour
        return __block_result_1__

    def f_addDashRow(_table, _row, _title, _value, _textColor, _size):
        table.cell(_table, 0, _row, _title, text_color=color.black, text_halign=text.align_left, text_size=_size)
        return table.cell(_table, 1, _row, _value, text_color=_textColor, text_halign=text.align_right, text_size=_size)

    sessionOK = inSession()

    ema9 = ta.ema(close, 9)
    ema21 = ta.ema(close, 21)
    vwapValue = ta.vwap(hlc3)
    atrValue = ta.atr(atrLen)
    rsiValue: Series = ta.rsi(close, rsiLength)

    rsi5m = request.security(syminfo.tickerid, '5', inline_series(ta.rsi(close, rsiLength), 1), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    macdMain, macdSignal, macdHist = ta.macd(close, 12, 26, 9)
    dmiPlus, dmiMinus, adxValue = ta.dmi(14, 14)
    volAvg = ta.sma(volume, 20)

    maxHist: int = 4096
    histLen: int = maxHist if historyBars > maxHist else historyBars

    upCount: float = 0.0
    downCount: float = 0.0

    for i in pine_range(1, histLen):
        if not na(close[i]) and (not na(close[i + 1])):
            chg: float = close[i] - close[i + 1]
            weight: float = 1.0 + (histLen - i) / histLen
            if chg > 0:
                upCount += weight
            elif chg < 0:
                downCount += weight

    totalMoves = upCount + downCount
    bullProb = upCount / totalMoves if totalMoves > 0 else 0.0
    bearProb = downCount / totalMoves if totalMoves > 0 else 0.0

    trendDir = 1 if bullProb > bearProb else -1 if bearProb > bullProb else 0

    stateMomentum = bullProb - bearProb if bullProb > bearProb else bearProb - bullProb if bearProb > bullProb else 0.0

    confidence = math.max(bullProb, bearProb)
    confidenceScore = 1 if confidence >= confThreshold else 0
    momentumScore = 1 if stateMomentum >= momentumThreshold else 0

    trendEmaValue: Series = ta.ema(close, trendEmaLen)
    trendEmaSlope = trendEmaValue - trendEmaValue[1]
    emaBull = close > trendEmaValue and trendEmaSlope > 0
    emaBear = close < trendEmaValue and trendEmaSlope < 0

    mtfBull = request.security(syminfo.tickerid, mtfTf, inline_series(close > ta.ema(close, trendEmaLen) and ta.ema(close, trendEmaLen) > inline_series(ta.ema(close, trendEmaLen), 1), 1), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    mtfBear = request.security(syminfo.tickerid, mtfTf, inline_series(close < ta.ema(close, trendEmaLen) and ta.ema(close, trendEmaLen) < inline_series(ta.ema(close, trendEmaLen), 1), 1), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)

    volSMA = ta.sma(volume, volLookback)
    volOK = not na(volSMA) and volume > volSMA * volMultiplier

    atrBase = ta.sma(atrValue, atrMaLen)
    atrOK = not useATRfilter or (not na(atrBase) and atrValue >= atrBase * atrMultiplier)

    candleRange = math.max(high - low, syminfo.mintick)
    bodyRatio = math.abs(close - open) / candleRange
    bullCandle = close > open and bodyRatio >= bodyRatioMin
    bearCandle = close < open and bodyRatio >= bodyRatioMin

    bullScoreSniper: float = 0
    bullScoreSniper += 1 if close > vwapValue else 0
    bullScoreSniper += 1 if rsiValue > 50 else 0
    bullScoreSniper += 1 if macdMain > macdSignal else 0
    bullScoreSniper += 1 if ema9 > ema21 else 0
    bullScoreSniper += 1 if adxValue > 25 and close > ema9 else 0
    bullScoreSniper += 1 if volume > volAvg and close > open else 0
    bullScoreSniper += 1 if rsi5m > 50 else 0
    bullPct = bullScoreSniper / 7.0 * 100.0

    bearScoreSniper: float = 0
    bearScoreSniper += 1 if close < vwapValue else 0
    bearScoreSniper += 1 if rsiValue < 50 else 0
    bearScoreSniper += 1 if macdMain < macdSignal else 0
    bearScoreSniper += 1 if ema9 < ema21 else 0
    bearScoreSniper += 1 if adxValue > 25 and close < ema9 else 0
    bearScoreSniper += 1 if volume > volAvg and close < open else 0
    bearScoreSniper += 1 if rsi5m < 50 else 0
    bearPct = bearScoreSniper / 7.0 * 100.0

    biasDiff = bullPct - bearPct
    biasText = 'STRONG BULL' if biasDiff >= strongBiasDiff else 'STRONG BEAR' if -biasDiff >= strongBiasDiff else 'MILD BULL' if bullPct > bearPct else 'MILD BEAR' if bearPct > bullPct else 'NEUTRAL'

    biasColor = color.green if biasText == 'STRONG BULL' else color.red if biasText == 'STRONG BEAR' else color.gray

    sniperLongBias = bullPct > bearPct and bullPct >= sniperMinPct
    sniperShortBias = bearPct > bullPct and bearPct >= sniperMinPct

    sniperLongTrigger = useSniperCrossTrigger and ta.crossover(ema9, ema21) and sniperLongBias and (close > vwapValue) and (macdMain > macdSignal) and (rsi5m > 50)
    sniperShortTrigger = useSniperCrossTrigger and ta.crossunder(ema9, ema21) and sniperShortBias and (close < vwapValue) and (macdMain < macdSignal) and (rsi5m < 50)

    lastSignalBarIndex: Persistent[int] = na(int)
    lastSignalType: Persistent[int] = 0
    lastSignalPrice: Persistent[float] = na(float)
    qMemory: Persistent[float] = 0.0
    orderSeq: Persistent[int] = 0
    openLongOrderId: Persistent[str] = ""
    openShortOrderId: Persistent[str] = ""

    entryPrice: Persistent[float] = na(float)
    stopPrice: Persistent[float] = na(float)
    trailingStopPrice: Persistent[float] = na(float)
    highestPriceSinceEntry: Persistent[float] = na(float)
    lowestPriceSinceEntry: Persistent[float] = na(float)
    tslActive: Persistent[bool] = False
    anchored: Persistent[bool] = False
    entryBarNum: Persistent[int] = na(int)

    tp1Price: Persistent[float] = na(float)
    tp2Price: Persistent[float] = na(float)
    tp3Price: Persistent[float] = na(float)
    tp4Price: Persistent[float] = na(float)
    tp5Price: Persistent[float] = na(float)
    tp1Hit: Persistent[bool] = False
    tp2Hit: Persistent[bool] = False
    tp3Hit: Persistent[bool] = False
    tp4Hit: Persistent[bool] = False
    tp5Hit: Persistent[bool] = False

    entryLine: Persistent[Line] = na(Line)
    stopLine: Persistent[Line] = na(Line)
    tp1Line: Persistent[Line] = na(Line)
    tp2Line: Persistent[Line] = na(Line)
    tp3Line: Persistent[Line] = na(Line)
    tp4Line: Persistent[Line] = na(Line)
    tp5Line: Persistent[Line] = na(Line)

    entryLabel: Persistent[Label] = na(Label)
    tp1Label: Persistent[Label] = na(Label)
    tp2Label: Persistent[Label] = na(Label)
    tp3Label: Persistent[Label] = na(Label)
    tp4Label: Persistent[Label] = na(Label)
    tp5Label: Persistent[Label] = na(Label)

    chartSecondsRaw = timeframe.in_seconds(timeframe.period)
    chartSeconds = 60 if na(chartSecondsRaw) else chartSecondsRaw
    intervalBars = math.max(1, cast_int(math.ceil(signalIntervalMin * 60.0 / chartSeconds)))
    newCheck = True if na(lastSignalBarIndex) else bar_index - lastSignalBarIndex >= intervalBars

    memoryInput = 0.18 + stateMomentum * 0.3 if trendDir == 1 else -(0.18 + stateMomentum * 0.3) if trendDir == -1 else 0.0

    qMemory = math.max(-1.0, math.min(1.0, qMemory * memoryDecay + memoryInput))
    memoryBias = 1 if qMemory > memoryThreshold else -1 if qMemory < -memoryThreshold else 0

    preferredDir = trendDir if trendDir != 0 else memoryBias

    longScore = (2 if preferredDir == 1 else 0) + (1 if trendDir == 1 else 0) + (1 if memoryBias == 1 else 0) + confidenceScore + momentumScore + (1 if not useEMAfilter or emaBull else 0) + (1 if not useMTFfilter or mtfBull else 0) + (1 if not useVolFilter or volOK else 0) + (1 if atrOK else 0) + (1 if not useCandleFilter or bullCandle else 0) + (2 if bullPct > bearPct else 0) + (1 if biasDiff >= strongBiasDiff else 0) + (1 if close > vwapValue else 0) + (1 if macdMain > macdSignal else 0) + (1 if adxValue > 25 else 0) + (1 if rsi5m > 50 else 0)

    shortScore = (2 if preferredDir == -1 else 0) + (1 if trendDir == -1 else 0) + (1 if memoryBias == -1 else 0) + confidenceScore + momentumScore + (1 if not useEMAfilter or emaBear else 0) + (1 if not useMTFfilter or mtfBear else 0) + (1 if not useVolFilter or volOK else 0) + (1 if atrOK else 0) + (1 if not useCandleFilter or bearCandle else 0) + (2 if bearPct > bullPct else 0) + (1 if -biasDiff >= strongBiasDiff else 0) + (1 if close < vwapValue else 0) + (1 if macdMain < macdSignal else 0) + (1 if adxValue > 25 else 0) + (1 if rsi5m < 50 else 0)

    longEdge = longScore - shortScore
    shortEdge = shortScore - longScore

    longRearmOK = na(lastSignalPrice) or lastSignalType != 1 or close >= lastSignalPrice + atrValue * minMoveAtr
    shortRearmOK = na(lastSignalPrice) or lastSignalType != -1 or close <= lastSignalPrice - atrValue * minMoveAtr

    longBiasGate = not useSniperBiasFilter or sniperLongBias or biasText == 'STRONG BULL'
    shortBiasGate = not useSniperBiasFilter or sniperShortBias or biasText == 'STRONG BEAR'

    rawLongSignal: bool = sessionOK and newCheck and longRearmOK and longBiasGate and (longScore >= signalScoreMin) and (longEdge >= signalEdgeMin)
    rawShortSignal: bool = sessionOK and newCheck and shortRearmOK and shortBiasGate and (shortScore >= signalScoreMin) and (shortEdge >= signalEdgeMin)

    rawLongSignal = rawLongSignal or sniperLongTrigger
    rawShortSignal = rawShortSignal or sniperShortTrigger

    if rawLongSignal and rawShortSignal:
        if bullPct >= bearPct:
            rawShortSignal = False
        else:
            rawLongSignal = False

    inLong: bool = strategy.position_size > 0
    inShort: bool = strategy.position_size < 0
    isFlat: bool = strategy.position_size == 0

    fastExitEma = ta.ema(close, exitEmaLength)
    priceCrossesBelowEma = ta.crossunder(close, fastExitEma)
    priceCrossesAboveEma = ta.crossover(close, fastExitEma)

    rsiExhaustionLong = rsiValue[1] > rsiOverbought and rsiValue < rsiOverbought
    rsiExhaustionShort = rsiValue[1] < rsiOversold and rsiValue > rsiOversold

    bullishEngulfing = close > open and close[1] < open[1] and (close > open[1]) and (open < close[1])
    bearishEngulfing = close < open and close[1] > open[1] and (close < open[1]) and (open > close[1])

    earlyLongExitRaw: bool = useEarlyExit and (priceCrossesBelowEma or (useRsiExit and rsiExhaustionLong) or bearishEngulfing)
    earlyShortExitRaw: bool = useEarlyExit and (priceCrossesAboveEma or (useRsiExit and rsiExhaustionShort) or bullishEngulfing)

    barsInTrade: int = 0 if na(entryBarNum) else bar_index - entryBarNum
    holdGatePassed: bool = barsInTrade >= minHoldBars
    earlyLongExit: bool = earlyLongExitRaw and inLong and holdGatePassed and (not earlyExitAfterTP1 or tp1Hit)
    earlyShortExit: bool = earlyShortExitRaw and inShort and holdGatePassed and (not earlyExitAfterTP1 or tp1Hit)

    enterLong: bool = barstate.isconfirmed and rawLongSignal and isFlat and allowLongs
    enterShort: bool = barstate.isconfirmed and rawShortSignal and isFlat and allowShorts

    if enterLong or enterShort:
        lastSignalBarIndex = bar_index
        lastSignalType = 1 if enterLong else -1
        lastSignalPrice = close

    pionexOrderPrefix: str = "QF_SOLUSDT_SNIPE"

    def makeOrderId(action, seq):
        return pionexOrderPrefix + '_' + timeframe.period + '_' + string.tostring(bar_index) + '_' + string.tostring(seq) + '_' + action

    def makeAlertMessage(action, orderId):
        priceField = ',"price":' + string.tostring(close, format.mintick) if includePriceInAlert else ''
        return '{"action":"' + action + '","symbol":"' + syminfo.ticker + '"' + priceField + ',"order_id":"' + orderId + '"}'

    if enterLong:
        risk: float = atrValue * slAtrMultiplier
        entryPrice = close
        stopPrice = close - risk
        highestPriceSinceEntry = high
        lowestPriceSinceEntry = na
        trailingStopPrice = na
        tslActive = False
        anchored = False
        entryBarNum = bar_index
        tp1Price = close + risk * tpStepR
        tp2Price = close + risk * tpStepR * 2.0
        tp3Price = close + risk * tpStepR * 3.0
        tp4Price = close + risk * tpStepR * 4.0
        tp5Price = close + risk * tpStepR * 5.0
        tp1Hit = False
        tp2Hit = False
        tp3Hit = False
        tp4Hit = False
        tp5Hit = False
        orderSeq += 1
        openLongOrderId = makeOrderId('buy', orderSeq)
        strategy.entry('L', strategy.long, alert_message=makeAlertMessage('buy', openLongOrderId))

    if enterShort:
        risk: float = atrValue * slAtrMultiplier
        entryPrice = close
        stopPrice = close + risk
        highestPriceSinceEntry = na
        lowestPriceSinceEntry = low
        trailingStopPrice = na
        tslActive = False
        anchored = False
        entryBarNum = bar_index
        tp1Price = close - risk * tpStepR
        tp2Price = close - risk * tpStepR * 2.0
        tp3Price = close - risk * tpStepR * 3.0
        tp4Price = close - risk * tpStepR * 4.0
        tp5Price = close - risk * tpStepR * 5.0
        tp1Hit = False
        tp2Hit = False
        tp3Hit = False
        tp4Hit = False
        tp5Hit = False
        orderSeq += 1
        openShortOrderId = makeOrderId('sell', orderSeq)
        strategy.entry('S', strategy.short, alert_message=makeAlertMessage('sell', openShortOrderId))

    if inLong and (not anchored):
        riskA: float = atrValue * slAtrMultiplier
        entryPrice = strategy.position_avg_price
        stopPrice = strategy.position_avg_price - riskA
        tp1Price = strategy.position_avg_price + riskA * tpStepR
        tp2Price = strategy.position_avg_price + riskA * tpStepR * 2.0
        tp3Price = strategy.position_avg_price + riskA * tpStepR * 3.0
        tp4Price = strategy.position_avg_price + riskA * tpStepR * 4.0
        tp5Price = strategy.position_avg_price + riskA * tpStepR * 5.0
        anchored = True

    if inShort and (not anchored):
        riskB: float = atrValue * slAtrMultiplier
        entryPrice = strategy.position_avg_price
        stopPrice = strategy.position_avg_price + riskB
        tp1Price = strategy.position_avg_price - riskB * tpStepR
        tp2Price = strategy.position_avg_price - riskB * tpStepR * 2.0
        tp3Price = strategy.position_avg_price - riskB * tpStepR * 3.0
        tp4Price = strategy.position_avg_price - riskB * tpStepR * 4.0
        tp5Price = strategy.position_avg_price - riskB * tpStepR * 5.0
        anchored = True

    if inLong and useTrailingStop:
        highestPriceSinceEntry = math.max(nz(highestPriceSinceEntry, high), high)
        if highestPriceSinceEntry - entryPrice >= atrValue * tslActivationAtr:
            tslActive = True
        if tslActive:
            newTslL: float = highestPriceSinceEntry - atrValue * tslAtrMultiplier
            trailingStopPrice = newTslL if na(trailingStopPrice) else math.max(trailingStopPrice, newTslL)

    if inShort and useTrailingStop:
        lowestPriceSinceEntry = math.min(nz(lowestPriceSinceEntry, low), low)
        if entryPrice - lowestPriceSinceEntry >= atrValue * tslActivationAtr:
            tslActive = True
        if tslActive:
            newTslS: float = lowestPriceSinceEntry + atrValue * tslAtrMultiplier
            trailingStopPrice = newTslS if na(trailingStopPrice) else math.min(trailingStopPrice, newTslS)

    effStopLong: float = math.max(stopPrice, trailingStopPrice) if useTrailingStop and tslActive and (not na(trailingStopPrice)) else stopPrice
    effStopShort: float = math.min(stopPrice, trailingStopPrice) if useTrailingStop and tslActive and (not na(trailingStopPrice)) else stopPrice

    if inLong:
        strategy.exit('L_SL', from_entry='L', stop=effStopLong, alert_message=makeAlertMessage('close', openLongOrderId))
        if useTakeProfits:
            strategy.exit('L_TP1', from_entry='L', qty_percent=20, limit=tp1Price)
            strategy.exit('L_TP2', from_entry='L', qty_percent=20, limit=tp2Price)
            strategy.exit('L_TP3', from_entry='L', qty_percent=20, limit=tp3Price)
            strategy.exit('L_TP4', from_entry='L', qty_percent=20, limit=tp4Price)
            strategy.exit('L_TP5', from_entry='L', qty_percent=20, limit=tp5Price)

    if inShort:
        strategy.exit('S_SL', from_entry='S', stop=effStopShort, alert_message=makeAlertMessage('close', openShortOrderId))
        if useTakeProfits:
            strategy.exit('S_TP1', from_entry='S', qty_percent=20, limit=tp1Price)
            strategy.exit('S_TP2', from_entry='S', qty_percent=20, limit=tp2Price)
            strategy.exit('S_TP3', from_entry='S', qty_percent=20, limit=tp3Price)
            strategy.exit('S_TP4', from_entry='S', qty_percent=20, limit=tp4Price)
            strategy.exit('S_TP5', from_entry='S', qty_percent=20, limit=tp5Price)

    closeLongNow: bool = barstate.isconfirmed and inLong and (earlyLongExit or (useCloseActionForExit and rawShortSignal and holdGatePassed))
    closeShortNow: bool = barstate.isconfirmed and inShort and (earlyShortExit or (useCloseActionForExit and rawLongSignal and holdGatePassed))

    if closeLongNow:
        strategy.close('L', comment='EARLY_OPP', alert_message=makeAlertMessage('close', openLongOrderId))

    if closeShortNow:
        strategy.close('S', comment='EARLY_OPP', alert_message=makeAlertMessage('close', openShortOrderId))

    if isFlat and (not na(entryPrice)):
        entryPrice = na
        stopPrice = na
        trailingStopPrice = na
        highestPriceSinceEntry = na
        lowestPriceSinceEntry = na
        tslActive = False
        anchored = False
        entryBarNum = na
        tp1Price = na
        tp2Price = na
        tp3Price = na
        tp4Price = na
        tp5Price = na
        tp1Hit = False
        tp2Hit = False
        tp3Hit = False
        tp4Hit = False
        tp5Hit = False
        openLongOrderId = ""
        openShortOrderId = ""

    if inLong:
        tp1Hit = tp1Hit or high >= tp1Price
        tp2Hit = tp2Hit or high >= tp2Price
        tp3Hit = tp3Hit or high >= tp3Price
        tp4Hit = tp4Hit or high >= tp4Price
        tp5Hit = tp5Hit or high >= tp5Price
    elif inShort:
        tp1Hit = tp1Hit or low <= tp1Price
        tp2Hit = tp2Hit or low <= tp2Price
        tp3Hit = tp3Hit or low <= tp3Price
        tp4Hit = tp4Hit or low <= tp4Price
        tp5Hit = tp5Hit or low <= tp5Price

    dashTextSize = getTextSize(dashTextSizeStr)
    tradeTextSize = getTextSize(tradeTextSizeStr)

    pFast = plot(ema9 if showRibbon else na, color=color.new(color.green, 20), title='EMA 9')
    pSlow = plot(ema21 if showRibbon else na, color=color.new(color.red, 20), title='EMA 21')
    fill(pFast, pSlow, color=color.new(color.green, 100 - ribbonOpacity) if ema9 > ema21 else color.new(color.red, 100 - ribbonOpacity))
    plot(vwapValue if showVwap else na, color=color.green if close > vwapValue else color.red, linewidth=2, title='VWAP')

    plot(effStopLong if inLong and (not na(effStopLong)) else effStopShort if inShort and (not na(effStopShort)) else na, color=color.fuchsia, style=plot.style_stepline, linewidth=2, title='Active Stop')

    plotshape(showSignalLabels and enterLong, title='Buy Open', style=shape.labelup, location=location.belowbar, color=color.green, textcolor=color.white, text='BUY')
    plotshape(showSignalLabels and enterShort, title='Sell Open', style=shape.labeldown, location=location.abovebar, color=color.red, textcolor=color.white, text='SELL')
    plotshape(showSignalLabels and closeLongNow, title='Close Long', style=shape.xcross, location=location.belowbar, color=color.orange, text='X-L')
    plotshape(showSignalLabels and closeShortNow, title='Close Short', style=shape.xcross, location=location.abovebar, color=color.orange, text='X-S')

    isRetest = inLong and low <= ema9 and (low > ema21) or (inShort and high >= ema9 and (high < ema21))
    barcolor(color.orange if isRetest else na)

    justEntered: bool = (enterLong or enterShort) and showTargets
    justWentFlat: bool = isFlat and strategy.position_size[1] != 0

    if justEntered:
        line.delete(entryLine)
        line.delete(stopLine)
        line.delete(tp1Line)
        line.delete(tp2Line)
        line.delete(tp3Line)
        line.delete(tp4Line)
        line.delete(tp5Line)
        label.delete(entryLabel)
        label.delete(tp1Label)
        label.delete(tp2Label)
        label.delete(tp3Label)
        label.delete(tp4Label)
        label.delete(tp5Label)
        entryLine = line.new(bar_index, entryPrice, bar_index + 20, entryPrice, color=color.blue, width=2, extend=extend.right)
        stopLine = line.new(bar_index, stopPrice, bar_index + 20, stopPrice, color=color.red, width=2, extend=extend.right)
        tp1Line = line.new(bar_index, tp1Price, bar_index + 20, tp1Price, color=color.green, style=line.style_dashed, extend=extend.right)
        tp2Line = line.new(bar_index, tp2Price, bar_index + 20, tp2Price, color=color.green, style=line.style_dashed, extend=extend.right)
        tp3Line = line.new(bar_index, tp3Price, bar_index + 20, tp3Price, color=color.green, style=line.style_dashed, extend=extend.right)
        tp4Line = line.new(bar_index, tp4Price, bar_index + 20, tp4Price, color=color.rgb(0, 100, 0), width=2, extend=extend.right)
        tp5Line = line.new(bar_index, tp5Price, bar_index + 20, tp5Price, color=color.rgb(0, 70, 0), width=3, extend=extend.right)
        entryLabel = label.new(bar_index + labelOffset, entryPrice, 'ENTRY: ' + string.tostring(entryPrice, format.mintick), color=color.blue, textcolor=color.white, style=label.style_label_left, size=tradeTextSize)
        tp1Label = label.new(bar_index + labelOffset, tp1Price, 'TP1: ' + string.tostring(tp1Price, format.mintick), color=color.green, textcolor=color.white, style=label.style_label_left, size=tradeTextSize)
        tp2Label = label.new(bar_index + labelOffset, tp2Price, 'TP2: ' + string.tostring(tp2Price, format.mintick), color=color.green, textcolor=color.white, style=label.style_label_left, size=tradeTextSize)
        tp3Label = label.new(bar_index + labelOffset, tp3Price, 'TP3: ' + string.tostring(tp3Price, format.mintick), color=color.green, textcolor=color.white, style=label.style_label_left, size=tradeTextSize)
        tp4Label = label.new(bar_index + labelOffset, tp4Price, 'TP4: ' + string.tostring(tp4Price, format.mintick), color=color.rgb(0, 100, 0), textcolor=color.white, style=label.style_label_left, size=tradeTextSize)
        tp5Label = label.new(bar_index + labelOffset, tp5Price, 'TP5: ' + string.tostring(tp5Price, format.mintick), color=color.rgb(0, 70, 0), textcolor=color.white, style=label.style_label_left, size=tradeTextSize)

    if justWentFlat or not showTargets:
        line.delete(entryLine)
        line.delete(stopLine)
        line.delete(tp1Line)
        line.delete(tp2Line)
        line.delete(tp3Line)
        line.delete(tp4Line)
        line.delete(tp5Line)
        label.delete(entryLabel)
        label.delete(tp1Label)
        label.delete(tp2Label)
        label.delete(tp3Label)
        label.delete(tp4Label)
        label.delete(tp5Label)

    if showTargets and (not isFlat) and (not na(entryLine)):
        labelX: int = bar_index + labelOffset
        liveStop: float = effStopLong if inLong else effStopShort
        line.set_y1(stopLine, liveStop)
        line.set_y2(stopLine, liveStop)
        line.set_color(tp1Line, color.new('#40E0D0') if tp1Hit else color.green)
        line.set_color(tp2Line, color.new('#40E0D0') if tp2Hit else color.green)
        line.set_color(tp3Line, color.new('#40E0D0') if tp3Hit else color.green)
        line.set_color(tp4Line, color.new('#40E0D0') if tp4Hit else color.rgb(0, 100, 0))
        line.set_color(tp5Line, color.new('#40E0D0') if tp5Hit else color.rgb(0, 70, 0))
        label.set_xy(entryLabel, labelX, entryPrice)
        label.set_xy(tp1Label, labelX, tp1Price)
        label.set_xy(tp2Label, labelX, tp2Price)
        label.set_xy(tp3Label, labelX, tp3Price)
        label.set_xy(tp4Label, labelX, tp4Price)
        label.set_xy(tp5Label, labelX, tp5Price)
        label.set_text(entryLabel, 'ENTRY: ' + string.tostring(entryPrice, format.mintick))
        label.set_text(tp1Label, 'TP1: ' + string.tostring(tp1Price, format.mintick) + (' hit' if tp1Hit else ''))
        label.set_text(tp2Label, 'TP2: ' + string.tostring(tp2Price, format.mintick) + (' hit' if tp2Hit else ''))
        label.set_text(tp3Label, 'TP3: ' + string.tostring(tp3Price, format.mintick) + (' hit' if tp3Hit else ''))
        label.set_text(tp4Label, 'TP4: ' + string.tostring(tp4Price, format.mintick) + (' hit' if tp4Hit else ''))
        label.set_text(tp5Label, 'TP5: ' + string.tostring(tp5Price, format.mintick) + (' hit' if tp5Hit else ''))

    dash: Persistent[Table] = table.new(position.middle_left, 2, 17, bgcolor=color.new(color.new('#FFF9C4'), 10), border_width=1, border_color=color.new(color.gray, 60))
    if showDashboard and barstate.islast:
        openPnl: float = strategy.openprofit
        winRate: float = strategy.wintrades / strategy.closedtrades * 100.0 if strategy.closedtrades > 0 else 0.0
        table.cell(dash, 0, 0, 'BULL SCORE', text_color=color.white, bgcolor=color.green, text_size=dashTextSize)
        table.cell(dash, 1, 0, string.tostring(bullPct, '#') + '%', text_color=color.white, bgcolor=color.green, text_size=dashTextSize)
        table.cell(dash, 0, 1, 'BEAR SCORE', text_color=color.white, bgcolor=color.red, text_size=dashTextSize)
        table.cell(dash, 1, 1, string.tostring(bearPct, '#') + '%', text_color=color.white, bgcolor=color.red, text_size=dashTextSize)
        table.cell(dash, 0, 2, 'MARKET BIAS', text_color=color.white, bgcolor=color.black, text_size=dashTextSize)
        table.cell(dash, 1, 2, biasText, text_color=color.white, bgcolor=biasColor, text_size=dashTextSize)
        f_addDashRow(dash, 3, 'Quantum', 'LONG' if preferredDir == 1 else 'SHORT' if preferredDir == -1 else 'NEUTRAL', color.green if preferredDir == 1 else color.red if preferredDir == -1 else color.gray, dashTextSize)
        f_addDashRow(dash, 4, 'VWAP', 'ABOVE' if close > vwapValue else 'BELOW', color.green if close > vwapValue else color.red, dashTextSize)
        f_addDashRow(dash, 5, 'RSI 14', string.tostring(rsiValue, '#.#'), color.green if rsiValue > 50 else color.red, dashTextSize)
        f_addDashRow(dash, 6, 'RSI 5m', string.tostring(rsi5m, '#.#'), color.green if rsi5m > 50 else color.red, dashTextSize)
        f_addDashRow(dash, 7, 'MACD', 'BULL' if macdMain > macdSignal else 'BEAR', color.green if macdMain > macdSignal else color.red, dashTextSize)
        f_addDashRow(dash, 8, 'ADX', string.tostring(adxValue, '#.#'), color.green if adxValue > 25 else color.gray, dashTextSize)
        f_addDashRow(dash, 9, 'Score L/S', string.tostring(longScore, '#') + ' / ' + string.tostring(shortScore, '#'), color.green if longScore > shortScore else color.red if shortScore > longScore else color.gray, dashTextSize)
        f_addDashRow(dash, 10, 'Signal', 'BUY' if enterLong else 'SELL' if enterShort else 'CLOSE' if closeLongNow or closeShortNow else 'WAIT', color.green if enterLong else color.red if enterShort else color.orange if closeLongNow or closeShortNow else color.gray, dashTextSize)
        f_addDashRow(dash, 11, 'Position', 'LONG' if inLong else 'SHORT' if inShort else 'FLAT', color.green if inLong else color.red if inShort else color.gray, dashTextSize)
        f_addDashRow(dash, 12, 'ATR', string.tostring(atrValue, '#.##'), color.black, dashTextSize)
        f_addDashRow(dash, 13, 'Open PnL', string.tostring(openPnl, '#.##'), color.green if openPnl >= 0 else color.red, dashTextSize)
        f_addDashRow(dash, 14, 'Net PnL', string.tostring(strategy.netprofit, '#.##'), color.green if strategy.netprofit >= 0 else color.red, dashTextSize)
        f_addDashRow(dash, 15, 'Trades', string.tostring(strategy.closedtrades), color.black, dashTextSize)
        f_addDashRow(dash, 16, 'Win Rate', string.tostring(winRate, '#.#') + '%', color.green if winRate >= 50 else color.red, dashTextSize)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
