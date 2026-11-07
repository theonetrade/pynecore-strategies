"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barstate, box, close, color, currency, extend, high, hl2,
    input, label, line, low, math, na, nz, plot, plotchar, script, strategy, string, syminfo, ta,
    time, timestamp, volume
)
from pynecore.types import Persistent, PersistentSeries, Series

INITIAL_CAPITAL: int = 1000
DEFAULT_COMMISSION: float = 0.02
MAX_DRAWINGS: int = 500
IS_OVERLAY: bool = True


@script.strategy('Coral Trend Pullback Strategy (TradeIQ)', 'Coral Trend Pullback', overlay=IS_OVERLAY, initial_capital=INITIAL_CAPITAL, currency=currency.NONE, max_labels_count=MAX_DRAWINGS, max_boxes_count=MAX_DRAWINGS, max_lines_count=MAX_DRAWINGS, default_qty_type=strategy.cash, commission_type=strategy.commission.percent, commission_value=DEFAULT_COMMISSION, margin_long=0, margin_short=0, default_qty_value=1, close_by_id=True)
def main(
    riskReward=input.float(1.5, 'Risk : Reward        1 :', group='Strategy: Risk Management', inline='RM1', minval=0, step=0.1, tooltip='Previous high or low (long/short dependant) is used to determine TP level. \'Risk : Reward\' ratio is then used to calculate SL based of previous high/low level.\n\nIn short, the higher the R:R ratio, the smaller the SL since TP target is fixed by previous high/low price data.'),
    accountRiskPercent=input.float(1, 'Portfolio Risk %        ', group='Strategy: Risk Management', inline='RM2', minval=0, step=0.1, tooltip='Percentage of portfolio you lose if trade hits SL.\n\nYou then stand to gain\n  Portfolio Risk % * Risk : Reward\nif trade hits TP.'),
    localHlLookback=input.int(5, 'Local High/Low Lookback     ', group='Strategy: Stop Loss Settings', inline='SL1', minval=1, tooltip='This strategy calculates the Stop Loss value from the recent local high/low. This lookback period determines the number of candles to include for the local high/low.'),
    startYear=input.int(2010, 'Start Date  ', group='Strategy: Date Range', inline='DR1', minval=1900, maxval=2100),
    startMonth=input.int(1, '', group='Strategy: Date Range', inline='DR1', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)),
    startDate=input.int(1, '', group='Strategy: Date Range', inline='DR1', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31)),
    endYear=input.int(2100, 'End Date    ', group='Strategy: Date Range', inline='DR2', minval=1900, maxval=2100),
    endMonth=input.int(1, '', group='Strategy: Date Range', inline='DR2', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)),
    endDate=input.int(1, '', group='Strategy: Date Range', inline='DR2', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31)),
    showTpSlBoxes=input.bool(True, 'Show TP / SL Boxes', group='Strategy: Drawings', inline='D1', tooltip='Show or hide TP and SL position boxes.\n\nNote: TradingView limits the maximum number of boxes that can be displayed to 500 so they may not appear for all price data under test.'),
    showLabels=input.bool(False, 'Show Trade Exit Labels', group='Strategy: Drawings', inline='D2', tooltip='Useful labels to identify Profit/Loss and cumulative portfolio capital after each trade closes.\n\nAlso note that TradingView limits the max number of \'boxes\' that can be displayed on a chart (max 500). This means when you lookback far enough on the chart you will not see the TP/SL boxes. However you can check this option to identify where trades exited.'),
    ctSm=input.int(25, 'Smoothing Period       ', group='Leading Indicator: Coral Trand Settings', inline='CT1'),
    ctCd=input.float(0.4, 'Constant D          ', group='Leading Indicator: Coral Trand Settings', inline='CT2', step=0.1),
    confirmationInd=input.string('ADX and DI', 'Entry Confirmation Method    ', group='Confirmation Indicator: Indicator Selection', inline='IS1', options=('None', 'ADX and DI', 'Absolute Strength Histogram + HawkEye Volume'), tooltip='Select one of the possible confirmation indicator(s) which can be used to confirm entry signals from the main Coral Trend indicator conditions. See strategy conditions to understand the logic behind each confirmation indicator'),
    adxLen=input.int(14, 'ADX Length           ', group='Confirmation Indicator: ADX and DI Settings', inline='AD1'),
    midLine=input.int(20, 'Mid Line            ', group='Confirmation Indicator: ADX and DI Settings', inline='AD2', tooltip='Mid line on standard ADX and DI indicator. In this strategy the DI must be above this line for entry confirmation.'),
    ashLength=input.int(9, 'Period of Evaluation       ', group='Confirmation Indicator: Absolute Strength Histogram Settings', inline='ASH1'),
    ashSmooth=input.int(6, 'Period of Smoothing      ', group='Confirmation Indicator: Absolute Strength Histogram Settings', inline='ASH2'),
    ashSrc: Series[float] = input.source(close, 'Source             ', group='Confirmation Indicator: Absolute Strength Histogram Settings', inline='ASH3'),
    ashMode=input.string('RSI', 'Indicator Method       ', group='Confirmation Indicator: Absolute Strength Histogram Settings', inline='ASH4', options=('RSI', 'STOCHASTIC', 'ADX')),
    sahMaType=input.string('SMA', 'MA              ', group='Confirmation Indicator: Absolute Strength Histogram Settings', inline='ASH5', options=('ALMA', 'EMA', 'WMA', 'SMA', 'SMMA', 'HMA')),
    ashAlmaOffset=input.float(0.85, '* Arnaud Legoux (ALMA) Offset', group='Confirmation Indicator: Absolute Strength Histogram Settings', inline='ASH6', minval=0, step=0.01),
    ashAlmaSigma=input.int(6, '* Arnaud Legoux (ALMA) Sigma', group='Confirmation Indicator: Absolute Strength Histogram Settings', inline='ASH7', minval=0),
    hevLength=input.int(200, 'Length             ', group='Confirmation Indicator: HawkEye Volume Settings', inline='HV1'),
    hevDivisor=input.float(1.6, 'Divisor             ', group='Confirmation Indicator: HawkEye Volume Settings', inline='HV2', step=0.1)
):
    src = close
    di = (ctSm - 1.0) / 2.0 + 1.0
    c1 = 2 / (di + 1.0)
    c2 = 1 - c1
    c3 = 3.0 * (ctCd * ctCd + ctCd * ctCd * ctCd)
    c4 = -3.0 * (2.0 * ctCd * ctCd + ctCd + ctCd * ctCd * ctCd)
    c5 = 3.0 * ctCd + 1.0 + ctCd * ctCd * ctCd + 3.0 * ctCd * ctCd
    i1: PersistentSeries[float] = na(float)
    i2: PersistentSeries[float] = na(float)
    i3: PersistentSeries[float] = na(float)
    i4: PersistentSeries[float] = na(float)
    i5: PersistentSeries[float] = na(float)
    i6: PersistentSeries[float] = na(float)
    i1 = c1 * src + c2 * nz(i1[1])
    i2 = c1 * i1 + c2 * nz(i2[1])
    i3 = c1 * i2 + c2 * nz(i3[1])
    i4 = c1 * i3 + c2 * nz(i4[1])
    i5 = c1 * i4 + c2 * nz(i5[1])
    i6 = c1 * i5 + c2 * nz(i6[1])
    bfr: Series = -ctCd * ctCd * ctCd * i6 + c3 * i5 + c4 * i4 + c5 * i3
    bfrC = color.new(color.green, 50) if bfr > nz(bfr[1]) else color.new(color.red, 50) if bfr < nz(bfr[1]) else color.new(color.blue, 50)
    plot(bfr, 'Trend', linewidth=3, style=plot.style_stepline, color=bfrC)
    TrueRange = math.max(math.max(high - low, math.abs(high - nz(close[1]))), math.abs(low - nz(close[1])))
    DirectionalMovementPlus = math.max(high - nz(high[1]), 0) if high - nz(high[1]) > nz(low[1]) - low else 0
    DirectionalMovementMinus = math.max(nz(low[1]) - low, 0) if nz(low[1]) - low > high - nz(high[1]) else 0
    SmoothedTrueRange: Series[float] = 0.0
    SmoothedTrueRange = nz(SmoothedTrueRange[1]) - nz(SmoothedTrueRange[1]) / adxLen + TrueRange
    SmoothedDirectionalMovementPlus: Series[float] = 0.0
    SmoothedDirectionalMovementPlus = nz(SmoothedDirectionalMovementPlus[1]) - nz(SmoothedDirectionalMovementPlus[1]) / adxLen + DirectionalMovementPlus
    SmoothedDirectionalMovementMinus: Series[float] = 0.0
    SmoothedDirectionalMovementMinus = nz(SmoothedDirectionalMovementMinus[1]) - nz(SmoothedDirectionalMovementMinus[1]) / adxLen + DirectionalMovementMinus
    DIPlus = SmoothedDirectionalMovementPlus / SmoothedTrueRange * 100
    DIMinus = SmoothedDirectionalMovementMinus / SmoothedTrueRange * 100
    DX = math.abs(DIPlus - DIMinus) / (DIPlus + DIMinus) * 100
    ADX: Series = ta.sma(DX, adxLen)
    def ashMa(ashType, ashSrc, ashLen):
        result: float = 0
        if ashType == 'SMA':
            result = ta.sma(ashSrc, ashLen)
        if ashType == 'EMA':
            result = ta.ema(ashSrc, ashLen)
        if ashType == 'WMA':
            result = ta.wma(ashSrc, ashLen)
        if ashType == 'SMMA':
            ashWma: Series = ta.wma(ashSrc, ashLen)
            ashSma = ta.sma(ashSrc, ashLen)
            result = ashSma if na(ashWma[1]) else (ashWma[1] * (ashLen - 1) + ashSrc) / ashLen
        if ashType == 'HMA':
            result = ta.wma(2 * ta.wma(ashSrc, ashLen / 2) - ta.wma(ashSrc, ashLen), math.round(math.sqrt(ashLen)))
        if ashType == 'ALMA':
            result = ta.alma(ashSrc, ashLen, ashAlmaOffset, ashAlmaSigma)
        return result

    Price: Series = ashSrc
    Price1 = ashMa('SMA', Price, 1)
    Price2 = ashMa('SMA', Price[1], 1)
    Bulls0 = 0.5 * (math.abs(Price1 - Price2) + Price1 - Price2)
    Bears0 = 0.5 * (math.abs(Price1 - Price2) - (Price1 - Price2))
    Bulls1 = Price1 - ta.lowest(Price1, ashLength)
    Bears1 = ta.highest(Price1, ashLength) - Price1
    Bulls2 = 0.5 * (math.abs(high - high[1]) + high - high[1])
    Bears2 = 0.5 * (math.abs(low[1] - low) + low[1] - low)
    Bulls = Bulls0 if ashMode == 'RSI' else Bulls1 if ashMode == 'STOCHASTIC' else Bulls2
    Bears = Bears0 if ashMode == 'RSI' else Bears1 if ashMode == 'STOCHASTIC' else Bears2
    AvgBulls = ashMa(sahMaType, Bulls, ashLength)
    AvgBears = ashMa(sahMaType, Bears, ashLength)
    SmthBulls = ashMa(sahMaType, AvgBulls, ashSmooth)
    SmthBears = ashMa(sahMaType, AvgBears, ashSmooth)
    isTrendBullish = True if SmthBulls > SmthBears else False
    hevRange1 = high - low
    hevRangeAvg = ta.sma(hevRange1, hevLength)
    hevVolumeA = ta.sma(volume, hevLength)
    hevHigh1 = high[1]
    hevLow1 = low[1]
    hevMid1 = hl2[1]
    hevU1 = hevMid1 + (hevHigh1 - hevLow1) / hevDivisor
    hevD1 = hevMid1 - (hevHigh1 - hevLow1) / hevDivisor
    rEnabled1 = hevRange1 > hevRangeAvg and close < hevD1 and (volume > hevVolumeA)
    rEnabled2 = close < hevMid1
    rEnabled = rEnabled1 or rEnabled2
    gEnabled1 = close > hevMid1
    gEnabled2 = hevRange1 > hevRangeAvg and close > hevU1 and (volume > hevVolumeA)
    gEnabled3 = high > hevHigh1 and hevRange1 < hevRangeAvg / 1.5 and (volume < hevVolumeA)
    gEnabled4 = low < hevLow1 and hevRange1 < hevRangeAvg / 1.5 and (volume > hevVolumeA)
    gEnabled = gEnabled1 or gEnabled2 or gEnabled3 or gEnabled4
    grEnabled1 = hevRange1 > hevRangeAvg and close > hevD1 and (close < hevU1) and (volume > hevVolumeA) and (volume < hevVolumeA * 1.5) and (volume > volume[1])
    grEnabled2 = hevRange1 < hevRangeAvg / 1.5 and volume < hevVolumeA / 1.5
    grEnabled3 = close > hevD1 and close < hevU1
    grEnabled = grEnabled1 or grEnabled2 or grEnabled3
    def percentAsPoints(pcnt):
        return math.round(pcnt / 100 * close / syminfo.mintick)

    def calcStopLossPrice(pointsOffset, isLong):
        priceOffset = pointsOffset * syminfo.mintick
        __block_result__ = na
        if isLong:
            __block_result__ = close - priceOffset
        else:
            __block_result__ = close + priceOffset
        return __block_result__

    def calcProfitTrgtPrice(pointsOffset, isLong):
        return calcStopLossPrice(-pointsOffset, isLong)

    def printLabel(barIndex, msg):
        return label.new(barIndex, close, msg)

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
            box.new(left=left, top=entryPrice, right=right, bottom=slPrice, bgcolor=color.new(color.gray, 90), border_width=0)
            box.new(left=left, top=entryPrice, right=right, bottom=tpPrice, bgcolor=color.new(color.gray, 90), border_width=0)
            line.new(x1=left, y1=entryPrice, x2=right, y2=entryPrice, color=color.new(color.yellow, 20))
            line.new(x1=left, y1=slPrice, x2=right, y2=slPrice, color=color.new(color.red, 20))
            __block_result_2__ = line.new(x1=left, y1=tpPrice, x2=right, y2=tpPrice, color=color.new(color.green, 20))
        return __block_result_2__

    def printTradeExitLabel(x, y, posSize, entryPrice, pnl):
        __block_result_3__ = na
        if showLabels:
            labelStr = 'Position Size: ' + string.tostring(math.abs(posSize), '#.##') + '\nPNL: ' + string.tostring(pnl, '#.##') + '\nCapital: ' + string.tostring(strategy.equity, '#.##') + '\nEntry Price: ' + string.tostring(entryPrice, '#.##')
            __block_result_3__ = label.new(x=x, y=y, text=labelStr, color=color.new(color.green, 60) if pnl > 0 else color.new(color.red, 60), textcolor=color.white, style=label.style_label_down)
        return __block_result_3__

    def printVerticalLine(col):
        return line.new(bar_index, close, bar_index, close * 1.01, extend=extend.both, color=col)

    inDateRange = time >= timestamp(syminfo.timezone, startYear, startMonth, startDate, 0, 0) and time < timestamp(syminfo.timezone, endYear, endMonth, endDate, 0, 0)
    isCoralBullish = bfr > nz(bfr[1])
    isCoralBearish = bfr < nz(bfr[1])
    sincePrePullbackBullBreakout: Series = ta.barssince(ta.crossover(close, bfr))
    sincePrePullbackBearBreakout: Series = ta.barssince(ta.crossunder(close, bfr))
    prePullbackBullBreakout = ta.barssince(low > bfr and high > bfr) < sincePrePullbackBullBreakout[1]
    prePullbackBearBreakout = ta.barssince(low < bfr and high < bfr) < sincePrePullbackBearBreakout[1]
    barssinceBullPullbackStart = ta.barssince(ta.crossunder(close, bfr))
    barssinceBearPullbackStart = ta.barssince(ta.crossover(close, bfr))
    barssincePullbackStart = barssinceBullPullbackStart if isCoralBullish else barssinceBearPullbackStart if isCoralBearish else na
    sinceBullish = ta.barssince(ta.crossover(bfr, nz(bfr[1])))
    sinceBearish = ta.barssince(ta.crossunder(bfr, nz(bfr[1])))
    barssinceCoralflip = sinceBullish if isCoralBullish else sinceBearish if isCoralBearish else na
    isPullbackValid = barssincePullbackStart < barssinceCoralflip
    crossover_1 = ta.crossover(close, bfr)
    crossunder_1 = ta.crossunder(close, bfr)
    entryBreakout = isCoralBullish and crossover_1 or (isCoralBearish and crossunder_1)
    longTradeConfirmed: Persistent[bool] = False
    shortTradeConfirmed: Persistent[bool] = False
    if confirmationInd == 'ADX and DI':
        isAdxUp = ADX > ADX[1]
        isAdxValid = ADX > midLine and isAdxUp
        longTradeConfirmed = DIPlus > DIMinus and isAdxValid
        shortTradeConfirmed = DIMinus > DIPlus and isAdxValid
    elif confirmationInd == 'Absolute Strength Histogram + HawkEye Volume':
        isAshBullish = True if SmthBulls > SmthBears else False
        isHevBullish = True if not grEnabled and gEnabled else False
        isHevBearish = True if not grEnabled and rEnabled else False
        longTradeConfirmed = isAshBullish and isHevBullish
        shortTradeConfirmed = not isAshBullish and isHevBearish
    elif confirmationInd == 'None':
        longTradeConfirmed = True
        shortTradeConfirmed = True
    goLong = inDateRange and isCoralBullish and prePullbackBullBreakout and isPullbackValid and entryBreakout and longTradeConfirmed
    goShort = inDateRange and isCoralBearish and prePullbackBearBreakout and isPullbackValid and entryBreakout and shortTradeConfirmed
    tradeEntryBar: Persistent = bar_index
    profitPoints: Persistent[float] = 0.0
    lossPoints: Persistent[float] = 0.0
    slPrice: Persistent[float] = 0.0
    tpPrice: Persistent[float] = 0.0
    inLong: Persistent[bool] = False
    inShort: Persistent[bool] = False
    entryPrice: Persistent[float] = 0.0
    openLong = goLong and (not inLong)
    openShort = goShort and (not inShort)
    flippingSides = goLong and inShort or (goShort and inLong)
    enteringTrade = openLong or openShort
    inTrade = inLong or inShort
    entryPrice = close
    longSlPrice = ta.lowest(localHlLookback)
    shortSlPrice = ta.highest(localHlLookback)
    slAmount = entryPrice - longSlPrice if isCoralBullish else shortSlPrice - entryPrice
    slPercent = math.abs((1 - (entryPrice - slAmount) / entryPrice) * 100)
    tpPercent = slPercent * riskReward
    riskAmt = strategy.equity * accountRiskPercent / 100
    entryQty = math.abs(riskAmt / slPercent * 100) / close
    if openLong:
        if strategy.position_size < 0:
            printTpSlNotHitBox(tradeEntryBar + 1, bar_index + 1, strategy.position_avg_price, slPrice, tpPrice)
            printTradeExitLabel(bar_index + 1, math.max(tpPrice, slPrice), strategy.position_size, strategy.position_avg_price, strategy.openprofit)
        strategy.entry('Long', strategy.long, qty=entryQty, alert_message='Long Entry')
        enteringTrade = True
        inLong = True
        inShort = False
    if openShort:
        if strategy.position_size > 0:
            printTpSlNotHitBox(tradeEntryBar + 1, bar_index + 1, strategy.position_avg_price, slPrice, tpPrice)
            printTradeExitLabel(bar_index + 1, math.max(tpPrice, slPrice), strategy.position_size, strategy.position_avg_price, strategy.openprofit)
        strategy.entry('Short', strategy.short, qty=entryQty, alert_message='Short Entry')
        enteringTrade = True
        inShort = True
        inLong = False
    if enteringTrade:
        profitPoints = percentAsPoints(tpPercent)
        lossPoints = percentAsPoints(slPercent)
        slPrice = calcStopLossPrice(lossPoints, openLong)
        tpPrice = calcProfitTrgtPrice(profitPoints, openLong)
        tradeEntryBar = bar_index
    strategy.exit('TP/SL', profit=profitPoints, loss=lossPoints, comment_profit='TP Hit', comment_loss='SL Hit', alert_profit='TP Hit Alert', alert_loss='SL Hit Alert')
    slHit = inShort and high >= slPrice or (inLong and low <= slPrice)
    tpHit = inLong and high >= tpPrice or (inShort and low <= tpPrice)
    exitTriggered = slHit or tpHit
    ctEntryPrice = strategy.closedtrades.entry_price(strategy.closedtrades - 1)
    pnl = strategy.closedtrades.profit(strategy.closedtrades - 1)
    posSize = strategy.closedtrades.size(strategy.closedtrades - 1)
    if inTrade and exitTriggered:
        inShort = False
        inLong = False
        printTpSlHitBox(tradeEntryBar, bar_index, slHit, tpHit, ctEntryPrice, slPrice, tpPrice)
        printTradeExitLabel(bar_index, math.max(tpPrice, slPrice), posSize, ctEntryPrice, pnl)
    if barstate.islastconfirmedhistory and strategy.position_size != 0:
        printTpSlNotHitBox(tradeEntryBar + 1, bar_index + 1, strategy.position_avg_price, slPrice, tpPrice)
    plotchar(prePullbackBullBreakout, 'prePullbackBullBreakout', '')
    plotchar(prePullbackBearBreakout, 'prePullbackBearBreakout', '')
    plotchar(barssincePullbackStart, 'barssincePullbackStart', '')
    plotchar(isCoralBullish, 'isCoralBullish', '')
    plotchar(isCoralBearish, 'isCoralBearish', '')
    plotchar(barssinceCoralflip, 'barssinceCoralflip', '')
    plotchar(isPullbackValid, 'isPullbackValid', '')
    plotchar(entryBreakout, 'entryBreakout', '')
    plotchar(slHit, 'slHit', '')
    plotchar(tpHit, 'tpHit', '')
    plotchar(slPrice, 'slPrice', '')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
