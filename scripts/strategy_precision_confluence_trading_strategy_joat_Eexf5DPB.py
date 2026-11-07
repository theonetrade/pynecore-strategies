"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    bar_index, barmerge, barstate, bgcolor, close, color, fill, high, hlc3,
    input, label, location, low, math, na, open, plot, plotshape, position, request, script, shape,
    size, strategy, string, syminfo, ta, table, time, timeframe, volume
)
from pynecore.types import Persistent, Series, Table

strategyGroup: str = "Strategy Settings"
riskGroup: str = "Risk Management"
indicatorGroup: str = "Indicator Parameters"
sessionGroup: str = "Session Settings"


@script.strategy("Precision Confluence Trading Strategy [JOAT]", shorttitle="PCT [JOAT]", overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, commission_value=0.1, slippage=2, max_bars_back=5000)
def main(
    useMultiTimeframe=input.bool(False, "Use Multi-Timeframe Confirmation", group=strategyGroup),
    useDivergence=input.bool(True, "Use Divergence Signals", group=strategyGroup),
    useSMC=input.bool(True, "Use Smart Money Concepts", group=strategyGroup),
    useVolume=input.bool(True, "Use Volume Confirmation", group=strategyGroup),
    useCPR=input.bool(True, "Use CPR Levels", group=strategyGroup),
    useWaveTrend=input.bool(True, "Use WaveTrend Signals", group=strategyGroup),
    useHMAAlignment=input.bool(True, "Use HMA Ribbon Alignment", group=strategyGroup),
    useSessionFilter=input.bool(False, "Use Session Filters", group=strategyGroup),
    minConfluenceScore=input.int(50, "Minimum Confluence Score %", minval=30, maxval=100, group=strategyGroup),
    riskPercent=input.float(2.0, "Risk Per Trade %", minval=0.1, maxval=10, step=0.1, group=riskGroup),
    rewardRatio=input.float(2.5, "Reward:Risk Ratio", minval=1.0, maxval=5.0, step=0.1, group=riskGroup),
    useTrailingStop=input.bool(True, "Use Trailing Stop", group=riskGroup),
    trailOffset=input.float(2.0, "Trailing Stop %", minval=0.1, maxval=5.0, step=0.1, group=riskGroup),
    useBreakeven=input.bool(True, "Move to Breakeven", group=riskGroup),
    breakevenTrigger=input.float(1.2, "Breakeven Trigger R:R", minval=0.5, maxval=3.0, step=0.1, group=riskGroup),
    atrMultiplier=input.float(1.5, "ATR Stop Multiplier", minval=0.5, maxval=5.0, step=0.1, group=riskGroup),
    rsiLength=input.int(14, "RSI Length", minval=2, group=indicatorGroup),
    adxLength=input.int(14, "ADX Length", minval=1, group=indicatorGroup),
    adxThreshold=input.int(20, "ADX Threshold", minval=10, group=indicatorGroup),
    volMaLength=input.int(20, "Volume MA Length", minval=1, group=indicatorGroup),
    hmaLength=input.int(21, "HMA Length", minval=1, group=indicatorGroup),
    wtChannelLen=input.int(10, "WaveTrend Channel Length", minval=1, group=indicatorGroup),
    wtAverageLen=input.int(21, "WaveTrend Average Length", minval=1, group=indicatorGroup),
    londonSession=input.session("0300-1200", "London Session", group=sessionGroup),
    nySession=input.session("0830-1700", "NY Session", group=sessionGroup)
):
    strongBullColor = color.rgb(0, 255, 0)
    weakBullColor = color.rgb(129, 199, 132)
    strongBearColor = color.rgb(255, 0, 0)
    weakBearColor = color.rgb(229, 115, 115)
    neutralColor = color.rgb(158, 158, 158)
    entryColor = color.rgb(0, 255, 0)
    exitColor = color.rgb(255, 0, 0)
    cprColor = color.rgb(255, 235, 59)
    volumeColor = color.rgb(255, 152, 0)

    def calcCPR(h, l, c):
        pivot = (h + l + c) / 3
        bc = (h + l) / 2
        tc = pivot - bc + pivot
        return (pivot, bc, tc)

    dHigh = request.security(syminfo.tickerid, 'D', high[1], lookahead=barmerge.lookahead_on)
    dLow = request.security(syminfo.tickerid, 'D', low[1], lookahead=barmerge.lookahead_on)
    dClose = request.security(syminfo.tickerid, 'D', close[1], lookahead=barmerge.lookahead_on)
    dPivot, dBC, dTC = calcCPR(dHigh, dLow, dClose)

    wHigh = request.security(syminfo.tickerid, 'W', high[1], lookahead=barmerge.lookahead_on)
    wLow = request.security(syminfo.tickerid, 'W', low[1], lookahead=barmerge.lookahead_on)
    wClose = request.security(syminfo.tickerid, 'W', close[1], lookahead=barmerge.lookahead_on)
    wPivot, wBC, wTC = calcCPR(wHigh, wLow, wClose)

    dCPRWidth = (dTC - dBC) / dPivot * 100
    wCPRWidth = (wTC - wBC) / wPivot * 100

    cprBullish = close > dPivot and close > wPivot
    cprBearish = close < dPivot and close < wPivot
    cprNarrow = dCPRWidth < 0.5
    cprWide = dCPRWidth > 1.5

    distFromDailyPivot = (close - dPivot) / dPivot * 100
    distFromWeeklyPivot = (close - wPivot) / wPivot * 100

    def hullMA(src, length):
        wma1 = ta.wma(src, length / 2)
        wma2 = ta.wma(src, length)
        return ta.wma(2 * wma1 - wma2, cast_int(math.sqrt(length)))

    hma8 = hullMA(close, 8)
    hma13 = hullMA(close, 13)
    hma21: Series = hullMA(close, 21)
    hma34 = hullMA(close, 34)
    hma55 = hullMA(close, 55)

    hmaFullBullish = hma8 > hma13 and hma13 > hma21 and (hma21 > hma34) and (hma34 > hma55)
    hmaFullBearish = hma8 < hma13 and hma13 < hma21 and (hma21 < hma34) and (hma34 < hma55)
    hmaBullish = close > hma21 and hma21 > hma21[1]
    hmaBearish = close < hma21 and hma21 < hma21[1]

    emaFast = ta.ema(close, 9)
    emaSlow = ta.ema(close, 21)
    emaCloudBullish = emaFast > emaSlow
    emaCloudBearish = emaFast < emaSlow

    sma50 = ta.sma(close, 50)
    sma200 = ta.sma(close, 200)
    goldenCross = sma50 > sma200
    deathCross = sma50 < sma200

    def calcWaveTrend(src, chlen, avglen):
        esa = ta.ema(src, chlen)
        d = ta.ema(math.abs(src - esa), chlen)
        ci = (src - esa) / (0.015 * d)
        tci = ta.ema(ci, avglen)
        wt1 = tci
        wt2 = ta.sma(wt1, 4)
        return (wt1, wt2)

    wt1: Series
    wt1, wt2 = calcWaveTrend(hlc3, wtChannelLen, wtAverageLen)

    wtCross = ta.cross(wt1, wt2)
    wtCrossUp = ta.crossover(wt1, wt2)
    wtCrossDown = ta.crossunder(wt1, wt2)
    wtOverbought = wt1 > 60
    wtOversold = wt1 < -60
    wtExtremeOverbought = wt1 > 80
    wtExtremeOversold = wt1 < -80

    wtPivotHigh = ta.pivothigh(wt1, 5, 5)
    wtPivotLow = ta.pivotlow(wt1, 5, 5)

    lastWTPivotHighVal: Persistent[float] = na(float)
    lastWTPivotHighPrice: Persistent[float] = na(float)
    lastWTPivotLowVal: Persistent[float] = na(float)
    lastWTPivotLowPrice: Persistent[float] = na(float)

    wtBullDiv: bool = False
    wtBearDiv: bool = False

    if not na(wtPivotHigh):
        currentHighPrice = high[5]
        currentHighWT = wt1[5]
        if not na(lastWTPivotHighPrice):
            wtBearDiv = currentHighPrice > lastWTPivotHighPrice and currentHighWT < lastWTPivotHighVal
        lastWTPivotHighVal = currentHighWT
        lastWTPivotHighPrice = currentHighPrice

    if not na(wtPivotLow):
        currentLowPrice = low[5]
        currentLowWT = wt1[5]
        if not na(lastWTPivotLowPrice):
            wtBullDiv = currentLowPrice < lastWTPivotLowPrice and currentLowWT > lastWTPivotLowVal
        lastWTPivotLowVal = currentLowWT
        lastWTPivotLowPrice = currentLowPrice

    wtMomentum: Series = wt1 - wt2
    wtMomentumBullish = wtMomentum > 0 and wtMomentum > wtMomentum[1]
    wtMomentumBearish = wtMomentum < 0 and wtMomentum < wtMomentum[1]

    rsi: Series = ta.rsi(close, rsiLength)
    rsiOversold = rsi < 30
    rsiOverbought = rsi > 70

    stochRSI = ta.stoch(rsi, rsi, rsi, 14)

    macdLine, macdSignal, macdHist = ta.macd(close, 12, 26, 9)

    cci = ta.cci(close, 20)

    compositeOsc = (rsi + stochRSI + (macdHist + 100) / 2 + (cci + 200) / 4) / 4

    pivotLookback: int = 5
    rsiPivotHigh = ta.pivothigh(rsi, pivotLookback, pivotLookback)
    rsiPivotLow = ta.pivotlow(rsi, pivotLookback, pivotLookback)

    lastRSIPivotHighVal: Persistent[float] = na(float)
    lastRSIPivotHighPrice: Persistent[float] = na(float)
    lastRSIPivotLowVal: Persistent[float] = na(float)
    lastRSIPivotLowPrice: Persistent[float] = na(float)

    rsiBullDiv: bool = False
    rsiBearDiv: bool = False

    if not na(rsiPivotHigh):
        currentHighPrice = high[pivotLookback]
        currentHighRSI = rsi[pivotLookback]
        if not na(lastRSIPivotHighPrice):
            rsiBearDiv = currentHighPrice > lastRSIPivotHighPrice and currentHighRSI < lastRSIPivotHighVal
        lastRSIPivotHighVal = currentHighRSI
        lastRSIPivotHighPrice = currentHighPrice

    if not na(rsiPivotLow):
        currentLowPrice = low[pivotLookback]
        currentLowRSI = rsi[pivotLookback]
        if not na(lastRSIPivotLowPrice):
            rsiBullDiv = currentLowPrice < lastRSIPivotLowPrice and currentLowRSI > lastRSIPivotLowVal
        lastRSIPivotLowVal = currentLowRSI
        lastRSIPivotLowPrice = currentLowPrice

    bullishDivergence = rsiBullDiv or wtBullDiv
    bearishDivergence = rsiBearDiv or wtBearDiv
    strongBullDiv = rsiBullDiv and wtBullDiv
    strongBearDiv = rsiBearDiv and wtBearDiv

    plus, minus, adx = ta.dmi(adxLength, adxLength)
    strongTrend = adx > adxThreshold
    trendBullish = plus > minus
    trendBearish = minus > plus

    volMA = ta.sma(volume, volMaLength)
    highVolume = volume > volMA * 1.5
    climaxVolume = volume > volMA * 3.0
    bullishVolume = close > open and highVolume
    bearishVolume = close < open and highVolume

    buyVolume = volume if close > open else 0
    sellVolume = volume if close < open else 0
    volumeDelta = ta.cum(buyVolume) - ta.cum(sellVolume)
    volumeDeltaMA = ta.sma(volumeDelta, 20)
    deltaRising = volumeDelta > volumeDeltaMA
    deltaFalling = volumeDelta < volumeDeltaMA

    volConfirmedBull = bullishVolume and deltaRising
    volConfirmedBear = bearishVolume and deltaFalling

    bullishFVG = low > high[2] and close[1] > high[2]
    fvgBullSize = (low - high[2]) / high[2] * 100 if bullishFVG else 0
    bearishFVG = high < low[2] and close[1] < low[2]
    fvgBearSize = (low[2] - high) / high * 100 if bearishFVG else 0

    significantBullFVG = bullishFVG and fvgBullSize > 0.3
    significantBearFVG = bearishFVG and fvgBearSize > 0.3

    bullishOB = close[2] < open[2] and close[1] < open[1] and (close > open) and highVolume
    bearishOB = close[2] > open[2] and close[1] > open[1] and (close < open) and highVolume

    lastBullOBHigh: Persistent[float] = na(float)
    lastBearOBLow: Persistent[float] = na(float)

    if bullishOB:
        lastBullOBHigh = high[1]
    if bearishOB:
        lastBearOBLow = low[1]

    breakerBull = not na(lastBearOBLow) and close > lastBearOBLow and (close[1] <= lastBearOBLow)
    breakerBear = not na(lastBullOBHigh) and close < lastBullOBHigh and (close[1] >= lastBullOBHigh)

    lookbackBars: int = 20
    recentHigh: Series = ta.highest(high, lookbackBars)
    recentLow: Series = ta.lowest(low, lookbackBars)
    liquiditySweepHigh = high > recentHigh[1] and close < recentHigh[1]
    liquiditySweepLow = low < recentLow[1] and close > recentLow[1]
    volConfirmedSweepHigh = liquiditySweepHigh and highVolume
    volConfirmedSweepLow = liquiditySweepLow and highVolume

    atr = ta.atr(14)
    displacement = math.abs(close - open) > atr * 2 and climaxVolume
    bullishDisplacement = displacement and close > open
    bearishDisplacement = displacement and close < open

    smcBullScore = (2 if significantBullFVG else 0) + (2 if bullishOB else 0) + (1 if breakerBull else 0) + (2 if volConfirmedSweepLow else 0) + (3 if bullishDisplacement else 0)
    smcBearScore = (2 if significantBearFVG else 0) + (2 if bearishOB else 0) + (1 if breakerBear else 0) + (2 if volConfirmedSweepHigh else 0) + (3 if bearishDisplacement else 0)

    inLondonSession = not na(time(timeframe.period, londonSession))
    inNYSession = not na(time(timeframe.period, nySession))
    inTradingSession = inLondonSession or inNYSession

    def htfTrend():
        htfClose = close
        htfHMA = hullMA(htfClose, 21)
        htfPlus, htfMinus, htfADX = ta.dmi(14, 14)
        htfTrendDir = 1 if htfClose > htfHMA else -1
        htfStrong = htfADX > 20
        return (htfTrendDir, htfStrong)

    htf15mDir, htf15mStrong = request.security(syminfo.tickerid, '15', htfTrend())
    htf1hDir, htf1hStrong = request.security(syminfo.tickerid, '60', htfTrend())
    htf4hDir, htf4hStrong = request.security(syminfo.tickerid, '240', htfTrend())

    mtfBullish = htf15mDir == 1 and htf1hDir == 1 and (htf4hDir == 1)
    mtfBearish = htf15mDir == -1 and htf1hDir == -1 and (htf4hDir == -1)
    mtfStrongBullish = mtfBullish and htf15mStrong and htf1hStrong and htf4hStrong
    mtfStrongBearish = mtfBearish and htf15mStrong and htf1hStrong and htf4hStrong

    cprBullScore: int = 0
    cprBullScore = cprBullScore + (10 if cprBullish else 0)
    cprBullScore = cprBullScore + (3 if close > dTC else 0)
    cprBullScore = cprBullScore + (2 if cprNarrow else 0)

    cprBearScore: int = 0
    cprBearScore = cprBearScore + (10 if cprBearish else 0)
    cprBearScore = cprBearScore + (3 if close < dBC else 0)
    cprBearScore = cprBearScore + (2 if cprNarrow else 0)

    hmaRibbonBullScore: int = 0
    hmaRibbonBullScore = hmaRibbonBullScore + (5 if hmaBullish else 0)
    hmaRibbonBullScore = hmaRibbonBullScore + (7 if hmaFullBullish else 0)
    hmaRibbonBullScore = hmaRibbonBullScore + (3 if emaCloudBullish else 0)

    hmaRibbonBearScore: int = 0
    hmaRibbonBearScore = hmaRibbonBearScore + (5 if hmaBearish else 0)
    hmaRibbonBearScore = hmaRibbonBearScore + (7 if hmaFullBearish else 0)
    hmaRibbonBearScore = hmaRibbonBearScore + (3 if emaCloudBearish else 0)

    wtBullScore: int = 0
    wtBullScore = wtBullScore + (8 if wtCrossUp and wtOversold else 5 if wtCrossUp else 0)
    wtBullScore = wtBullScore + (5 if wtBullDiv else 0)
    wtBullScore = wtBullScore + (2 if wtMomentumBullish else 0)

    wtBearScore: int = 0
    wtBearScore = wtBearScore + (8 if wtCrossDown and wtOverbought else 5 if wtCrossDown else 0)
    wtBearScore = wtBearScore + (5 if wtBearDiv else 0)
    wtBearScore = wtBearScore + (2 if wtMomentumBearish else 0)

    divBullScore: int = 0
    divBullScore = divBullScore + (5 if rsiBullDiv else 0)
    divBullScore = divBullScore + (5 if strongBullDiv else 0)

    divBearScore: int = 0
    divBearScore = divBearScore + (5 if rsiBearDiv else 0)
    divBearScore = divBearScore + (5 if strongBearDiv else 0)

    adxBullScore = 10 if strongTrend and trendBullish else 5 if trendBullish else 0
    adxBearScore = 10 if strongTrend and trendBearish else 5 if trendBearish else 0

    volBullScore: int = 0
    volBullScore = volBullScore + (7 if volConfirmedBull else 5 if bullishVolume else 0)
    volBullScore = volBullScore + (3 if climaxVolume and close > open else 0)

    volBearScore: int = 0
    volBearScore = volBearScore + (7 if volConfirmedBear else 5 if bearishVolume else 0)
    volBearScore = volBearScore + (3 if climaxVolume and close < open else 0)

    mtfBullScore: int = 0
    mtfBullScore = mtfBullScore + (15 if mtfStrongBullish else 10 if mtfBullish else 5 if htf1hDir == 1 else 0)

    mtfBearScore: int = 0
    mtfBearScore = mtfBearScore + (15 if mtfStrongBearish else 10 if mtfBearish else 5 if htf1hDir == -1 else 0)

    maBullScore: int = 0
    maBullScore = maBullScore + (3 if close > sma50 else 0)
    maBullScore = maBullScore + (4 if close > sma200 else 0)
    maBullScore = maBullScore + (3 if goldenCross else 0)

    maBearScore: int = 0
    maBearScore = maBearScore + (3 if close < sma50 else 0)
    maBearScore = maBearScore + (4 if close < sma200 else 0)
    maBearScore = maBearScore + (3 if deathCross else 0)

    bullConfluenceScore = (cprBullScore if useCPR else 0) + (hmaRibbonBullScore if useHMAAlignment else 0) + (wtBullScore if useWaveTrend else 0) + (divBullScore if useDivergence else 0) + adxBullScore + (volBullScore if useVolume else 0) + (smcBullScore if useSMC else 0) + (mtfBullScore if useMultiTimeframe else 0) + maBullScore

    bearConfluenceScore = (cprBearScore if useCPR else 0) + (hmaRibbonBearScore if useHMAAlignment else 0) + (wtBearScore if useWaveTrend else 0) + (divBearScore if useDivergence else 0) + adxBearScore + (volBearScore if useVolume else 0) + (smcBearScore if useSMC else 0) + (mtfBearScore if useMultiTimeframe else 0) + maBearScore

    sessionFilter = inTradingSession if useSessionFilter else True

    strongLongSignal = bullConfluenceScore >= 70 and bearConfluenceScore < 40 and sessionFilter
    strongShortSignal = bearConfluenceScore >= 70 and bullConfluenceScore < 40 and sessionFilter

    mediumLongSignal = bullConfluenceScore >= 55 and bullConfluenceScore > bearConfluenceScore + 15 and sessionFilter and (not strongLongSignal)
    mediumShortSignal = bearConfluenceScore >= 55 and bearConfluenceScore > bullConfluenceScore + 15 and sessionFilter and (not strongShortSignal)

    longSignal = (strongLongSignal or mediumLongSignal) and bullConfluenceScore >= minConfluenceScore
    shortSignal = (strongShortSignal or mediumShortSignal) and bearConfluenceScore >= minConfluenceScore

    ultraLongSignal = bullConfluenceScore >= 85 and bearConfluenceScore < 25 and (wtCrossUp or rsiBullDiv or bullishDisplacement)
    ultraShortSignal = bearConfluenceScore >= 85 and bullConfluenceScore < 25 and (wtCrossDown or rsiBearDiv or bearishDisplacement)

    stopLossDistance = atr * atrMultiplier

    dynamicStopMultiplier = atrMultiplier * 0.8 if ultraLongSignal or ultraShortSignal else atrMultiplier if strongLongSignal or strongShortSignal else atrMultiplier * 1.2

    accountSize = strategy.equity
    riskAmount = accountSize * (riskPercent / 100)
    positionSize = riskAmount / stopLossDistance

    swingLowLookback: int = 10
    swingHighLookback: int = 10
    recentSwingLow = ta.lowest(low, swingLowLookback)
    recentSwingHigh = ta.highest(high, swingHighLookback)

    dynamicStopBull = math.min(close - atr * dynamicStopMultiplier, recentSwingLow - atr * 0.2)
    dynamicStopBear = math.max(close + atr * dynamicStopMultiplier, recentSwingHigh + atr * 0.2)

    entryPrice: Persistent[float] = na(float)
    movedToBreakeven: Persistent[bool] = False

    if longSignal and strategy.position_size == 0:
        stopLoss = dynamicStopBull
        stopDistance = close - stopLoss
        takeProfit = close + stopDistance * rewardRatio
        strategy.entry('Long', strategy.long)
        strategy.exit('Long Exit', 'Long', stop=stopLoss, limit=takeProfit)

        entryPrice = close
        movedToBreakeven = False

        labelText = 'ULTRA LONG\n' + string.tostring(bullConfluenceScore) if ultraLongSignal else 'STRONG LONG\n' + string.tostring(bullConfluenceScore) if strongLongSignal else 'LONG\n' + string.tostring(bullConfluenceScore)
        labelColor = color.new(strongBullColor, 0) if ultraLongSignal else color.new(weakBullColor, 0) if strongLongSignal else color.new(entryColor, 20)
        labelSize = size.large if ultraLongSignal else size.normal if strongLongSignal else size.small

        label.new(bar_index, low, labelText, style=label.style_label_up, color=labelColor, textcolor=color.white, size=labelSize)

    if shortSignal and strategy.position_size == 0:
        stopLoss = dynamicStopBear
        stopDistance = stopLoss - close
        takeProfit = close - stopDistance * rewardRatio
        strategy.entry('Short', strategy.short)
        strategy.exit('Short Exit', 'Short', stop=stopLoss, limit=takeProfit)

        entryPrice = close
        movedToBreakeven = False

        labelText = 'ULTRA SHORT\n' + string.tostring(bearConfluenceScore) if ultraShortSignal else 'STRONG SHORT\n' + string.tostring(bearConfluenceScore) if strongShortSignal else 'SHORT\n' + string.tostring(bearConfluenceScore)
        labelColor = color.new(strongBearColor, 0) if ultraShortSignal else color.new(weakBearColor, 0) if strongShortSignal else color.new(exitColor, 20)
        labelSize = size.large if ultraShortSignal else size.normal if strongShortSignal else size.small

        label.new(bar_index, high, labelText, style=label.style_label_down, color=labelColor, textcolor=color.white, size=labelSize)

    if useBreakeven and strategy.position_size > 0 and (not movedToBreakeven):
        stopDistance = entryPrice - dynamicStopBull
        if close >= entryPrice + stopDistance * breakevenTrigger:
            newStop = entryPrice + stopDistance * 0.1
            newTP = entryPrice + stopDistance * rewardRatio
            strategy.exit('Long Exit', 'Long', stop=newStop, limit=newTP)
            movedToBreakeven = True
            label.new(bar_index, low, 'BE', style=label.style_label_up, color=color.new(color.blue, 0), textcolor=color.white, size=size.tiny)

    if useBreakeven and strategy.position_size < 0 and (not movedToBreakeven):
        stopDistance = dynamicStopBear - entryPrice
        if close <= entryPrice - stopDistance * breakevenTrigger:
            newStop = entryPrice - stopDistance * 0.1
            newTP = entryPrice - stopDistance * rewardRatio
            strategy.exit('Short Exit', 'Short', stop=newStop, limit=newTP)
            movedToBreakeven = True
            label.new(bar_index, high, 'BE', style=label.style_label_down, color=color.new(color.blue, 0), textcolor=color.white, size=size.tiny)

    plot(dPivot if useCPR else na, 'Daily Pivot', color.new(cprColor, 0), 2, plot.style_line)
    plot(dTC if useCPR else na, 'Daily TC', color.new(cprColor, 60), 1, plot.style_line)
    plot(dBC if useCPR else na, 'Daily BC', color.new(cprColor, 60), 1, plot.style_line)

    hmaColor1 = color.rgb(0, 255, 0)
    hmaColor2 = color.rgb(102, 255, 102)
    hmaColor3 = color.rgb(255, 255, 0)
    hmaColor4 = color.rgb(255, 153, 0)
    hmaColor5 = color.rgb(255, 0, 0)

    hma8Plot = plot(hma8, 'HMA 8', color.new(hmaColor1, 50), 2)
    hma13Plot = plot(hma13, 'HMA 13', color.new(hmaColor2, 50), 2)
    hma21Plot = plot(hma21, 'HMA 21', color.new(hmaColor3, 50), 2)
    hma34Plot = plot(hma34, 'HMA 34', color.new(hmaColor4, 50), 2)
    hma55Plot = plot(hma55, 'HMA 55', color.new(hmaColor5, 50), 2)

    ribbonTransparency: int = 85
    fill(hma8Plot, hma13Plot, color.new(hmaColor1, ribbonTransparency), title='HMA Fill 1-2')
    fill(hma13Plot, hma21Plot, color.new(hmaColor2, ribbonTransparency), title='HMA Fill 2-3')
    fill(hma21Plot, hma34Plot, color.new(hmaColor3, ribbonTransparency), title='HMA Fill 3-4')
    fill(hma34Plot, hma55Plot, color.new(hmaColor4, ribbonTransparency), title='HMA Fill 4-5')

    emaFastPlot = plot(emaFast, 'EMA 9', color.new(strongBullColor if emaCloudBullish else strongBearColor, 60), 1)
    emaSlowPlot = plot(emaSlow, 'EMA 21', color.new(strongBullColor if emaCloudBullish else strongBearColor, 60), 1)
    fill(emaFastPlot, emaSlowPlot, color.new(strongBullColor if emaCloudBullish else strongBearColor, 90), title='EMA Cloud')

    plot(sma50, 'SMA 50', color.new(color.blue, 40), 2)
    plot(sma200, 'SMA 200', color.new(color.orange, 40), 3)

    confluenceGradient = color.from_gradient(bullConfluenceScore, 50, 100, color.new(weakBullColor, 95), color.new(strongBullColor, 85)) if bullConfluenceScore > bearConfluenceScore else color.from_gradient(bearConfluenceScore, 50, 100, color.new(weakBearColor, 95), color.new(strongBearColor, 85))

    bgcolor(confluenceGradient if longSignal or shortSignal else na, title='Signal BG')

    plotshape(low if ultraLongSignal else na, 'ULTRA Long', shape.diamond, location.belowbar, color.new(strongBullColor, 0), size=size.large)
    plotshape(high if ultraShortSignal else na, 'ULTRA Short', shape.diamond, location.abovebar, color.new(strongBearColor, 0), size=size.large)

    perfTable: Persistent[Table] = table.new(position.bottom_right, 3, 12, bgcolor=color.new(color.black, 85), frame_color=color.new(color.gray, 50), frame_width=2, border_width=1, border_color=color.new(color.gray, 50))

    if barstate.islast:
        table.cell(perfTable, 0, 0, 'Component', bgcolor=color.new(color.gray, 70), text_color=color.white, text_size=size.small)
        table.cell(perfTable, 1, 0, 'Bull', bgcolor=color.new(color.gray, 70), text_color=color.white, text_size=size.small)
        table.cell(perfTable, 2, 0, 'Bear', bgcolor=color.new(color.gray, 70), text_color=color.white, text_size=size.small)

        table.cell(perfTable, 0, 1, 'Position', text_color=color.white, text_size=size.small)
        posText = 'LONG' if strategy.position_size > 0 else 'SHORT' if strategy.position_size < 0 else 'FLAT'
        posColor = color.new(strongBullColor, 30) if strategy.position_size > 0 else color.new(strongBearColor, 30) if strategy.position_size < 0 else color.new(neutralColor, 70)
        table.cell(perfTable, 1, 1, posText, bgcolor=posColor, text_color=color.white, text_size=size.small)
        table.merge_cells(perfTable, 1, 1, 2, 1)

        table.cell(perfTable, 0, 2, 'CONFLUENCE', text_color=color.yellow, text_size=size.small)
        bullScoreColor = color.new(strongBullColor, 20) if bullConfluenceScore >= 90 else color.new(weakBullColor, 30) if bullConfluenceScore >= 70 else color.new(neutralColor, 70)
        bearScoreColor = color.new(strongBearColor, 20) if bearConfluenceScore >= 90 else color.new(weakBearColor, 30) if bearConfluenceScore >= 70 else color.new(neutralColor, 70)
        table.cell(perfTable, 1, 2, string.tostring(bullConfluenceScore, '#'), bgcolor=bullScoreColor, text_color=color.white, text_size=size.normal)
        table.cell(perfTable, 2, 2, string.tostring(bearConfluenceScore, '#'), bgcolor=bearScoreColor, text_color=color.white, text_size=size.normal)

        table.cell(perfTable, 0, 3, 'CPR', text_color=cprColor, text_size=size.tiny)
        table.cell(perfTable, 1, 3, string.tostring(cprBullScore), text_color=color.white, text_size=size.tiny)
        table.cell(perfTable, 2, 3, string.tostring(cprBearScore), text_color=color.white, text_size=size.tiny)

        table.cell(perfTable, 0, 4, 'HMA Ribbon', text_color=color.white, text_size=size.tiny)
        table.cell(perfTable, 1, 4, string.tostring(hmaRibbonBullScore), text_color=color.white, text_size=size.tiny)
        table.cell(perfTable, 2, 4, string.tostring(hmaRibbonBearScore), text_color=color.white, text_size=size.tiny)

        table.cell(perfTable, 0, 5, 'WaveTrend', text_color=color.white, text_size=size.tiny)
        table.cell(perfTable, 1, 5, string.tostring(wtBullScore), text_color=color.white, text_size=size.tiny)
        table.cell(perfTable, 2, 5, string.tostring(wtBearScore), text_color=color.white, text_size=size.tiny)

        table.cell(perfTable, 0, 6, 'Divergence', text_color=color.white, text_size=size.tiny)
        table.cell(perfTable, 1, 6, string.tostring(divBullScore), text_color=color.white, text_size=size.tiny)
        table.cell(perfTable, 2, 6, string.tostring(divBearScore), text_color=color.white, text_size=size.tiny)

        table.cell(perfTable, 0, 7, 'ADX', text_color=color.white, text_size=size.tiny)
        table.cell(perfTable, 1, 7, string.tostring(adxBullScore), text_color=color.white, text_size=size.tiny)
        table.cell(perfTable, 2, 7, string.tostring(adxBearScore), text_color=color.white, text_size=size.tiny)

        table.cell(perfTable, 0, 8, 'Volume', text_color=volumeColor, text_size=size.tiny)
        table.cell(perfTable, 1, 8, string.tostring(volBullScore), text_color=color.white, text_size=size.tiny)
        table.cell(perfTable, 2, 8, string.tostring(volBearScore), text_color=color.white, text_size=size.tiny)

        table.cell(perfTable, 0, 9, 'SMC', text_color=color.white, text_size=size.tiny)
        table.cell(perfTable, 1, 9, string.tostring(smcBullScore), text_color=color.white, text_size=size.tiny)
        table.cell(perfTable, 2, 9, string.tostring(smcBearScore), text_color=color.white, text_size=size.tiny)

        table.cell(perfTable, 0, 10, 'MTF', text_color=color.white, text_size=size.tiny)
        table.cell(perfTable, 1, 10, string.tostring(mtfBullScore), text_color=color.white, text_size=size.tiny)
        table.cell(perfTable, 2, 10, string.tostring(mtfBearScore), text_color=color.white, text_size=size.tiny)

        table.cell(perfTable, 0, 11, 'Equity', text_color=color.white, text_size=size.small)
        equityText = '$' + string.tostring(strategy.equity, '#,###')
        equityColor = color.new(strongBullColor, 30) if strategy.equity > strategy.initial_capital else color.new(strongBearColor, 30)
        pnlPercent = (strategy.equity - strategy.initial_capital) / strategy.initial_capital * 100
        pnlText = string.tostring(pnlPercent, '#.##') + '%'
        table.cell(perfTable, 1, 11, equityText + '\n' + pnlText, bgcolor=equityColor, text_color=color.white, text_size=size.small)
        table.merge_cells(perfTable, 1, 11, 2, 11)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
