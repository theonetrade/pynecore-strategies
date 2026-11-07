"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alert, bar_index, barcolor, barstate, box, close, color, currency, high,
    hlc3, input, label, line, low, math, na, nz, open, plot, plotchar, script, strategy, string,
    syminfo, ta, time, timestamp
)
from pynecore.types import Persistent, PersistentSeries, Series

INITIAL_CAPITAL: int = 1000
DEFAULT_COMMISSION: float = 0.02
MAX_DRAWINGS: int = 500
IS_OVERLAY: bool = True


@script.strategy('SSL + Wave Trend Strategy', overlay=IS_OVERLAY, initial_capital=INITIAL_CAPITAL, currency=currency.NONE, max_labels_count=MAX_DRAWINGS, max_boxes_count=MAX_DRAWINGS, max_lines_count=MAX_DRAWINGS, default_qty_type=strategy.cash, commission_type=strategy.commission.percent, commission_value=DEFAULT_COMMISSION, margin_long=0, margin_short=0, default_qty_value=1, close_by_id=True)
def main(
    useSslHybrid=input.bool(True, 'Use SSL Hybrid Condition', group='Strategy: Entry Conditions', inline='SC1'),
    useKeltnerCh=input.bool(True, 'Use Keltner Channel Condition   ', group='Strategy: Entry Conditions', inline='SC2'),
    keltnerChWicks=input.bool(True, 'Keltner Channel Include Wicks', group='Strategy: Entry Conditions', inline='SC2'),
    useEma=input.bool(True, 'Target not touch EMA Condition', group='Strategy: Entry Conditions', inline='SC3'),
    useCandleHeight=input.bool(True, 'Use Candle Height Condition', group='Strategy: Entry Conditions', inline='SC4'),
    candleHeight=input.float(1.0, 'Candle Height Threshold     ', group='Strategy: Entry Conditions', inline='SC5', minval=0, step=0.1, tooltip='Percentage difference between high and low of a candle. Expressed as a decimal. Lowering this value will filter out trades on volatile candles.'),
    slAtrMultiplier=input.float(1.7, 'Stop Loss ATR Multiplier     ', group='Strategy: Exit Conditions', inline='EC1', minval=0, step=0.1, tooltip='Size of StopLoss is determined by multiplication of ATR value. Take Profit is derived from this also by multiplying the StopLoss value by the Risk:Reward multiplier.'),
    riskReward=input.float(2.5, 'Risk : Reward        1 :', group='Strategy: Risk Management', inline='RM1', minval=0, step=0.1, tooltip='Used to determine Take Profit level. Take Profit will be Stop Loss multiplied by this value.'),
    accountRiskPercent=input.float(1, 'Portfolio Risk %         ', group='Strategy: Risk Management', inline='RM2', minval=0, step=0.1, tooltip='Percentage of portfolio you lose if trade hits SL.\n\nYou then stand to gain\n  Portfolio Risk % * Risk : Reward\nif trade hits TP.'),
    startYear=input.int(2022, 'Start Date       ', group='Strategy: Date Range', inline='DR1', minval=1900, maxval=2100),
    startMonth=input.int(1, '', group='Strategy: Date Range', inline='DR1', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)),
    startDate=input.int(1, '', group='Strategy: Date Range', inline='DR1', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31)),
    endYear=input.int(2100, 'End Date      ', group='Strategy: Date Range', inline='DR2', minval=1900, maxval=2100),
    endMonth=input.int(1, '', group='Strategy: Date Range', inline='DR2', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)),
    endDate=input.int(1, '', group='Strategy: Date Range', inline='DR2', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31)),
    showTpSlBoxes=input.bool(True, 'Show TP / SL Boxes', group='Strategy: Drawings', inline='D1', tooltip='Show or hide TP and SL position boxes.\n\nNote: TradingView limits the maximum number of boxes that can be displayed to 500 so they may not appear for all price data under test.'),
    showLabels=input.bool(False, 'Show Trade Exit Labels', group='Strategy: Drawings', inline='D2', tooltip='Useful labels to identify Profit/Loss and cumulative portfolio capital after each trade closes.\n\nAlso note that TradingView limits the max number of \'boxes\' that can be displayed on a chart (max 500). This means when you lookback far enough on the chart you will not see the TP/SL boxes. However you can check this option to identify where trades exited.'),
    showSslHybrid=input.bool(True, 'Show SSL Hybrid', group='Indicators: Drawings', inline='ID1'),
    showSslChannel=input.bool(True, 'Show SSL Channel', group='Indicators: Drawings', inline='ID2'),
    showEma=input.bool(True, 'Show EMA', group='Indicators: Drawings', inline='ID3'),
    showKeltner=input.bool(True, 'Show Keltner Channel', group='Indicators: Drawings', inline='ID4'),
    showWaveTrend=input.bool(True, 'Show Wave Trend Flip Candles', group='Indicators: Drawings', inline='ID5'),
    showAtrSl=input.bool(True, 'Show ATR Stop Loss Bands', group='Indicators: Drawings', inline='ID6'),
    n1=input.int(10, 'Channel Length         ', group='Indicators: Wave Trend', inline='WT1'),
    n2=input.int(21, 'Average Length         ', group='Indicators: Wave Trend', inline='WT2'),
    obLevel1=input.int(60, 'Over Bought Level 1       ', group='Indicators: Wave Trend', inline='WT3'),
    obLevel2=input.int(53, 'Over Bought Level 2       ', group='Indicators: Wave Trend', inline='WT4'),
    osLevel1=input.int(-60, 'Over Sold Level 1         ', group='Indicators: Wave Trend', inline='WT5'),
    osLevel2=input.int(-53, 'Over Sold Level 2         ', group='Indicators: Wave Trend', inline='WT6'),
    sslChLen=input.int(10, 'Period             ', group='Indicators: SSL Channel', inline='SC1'),
    show_color_bar=input.bool(False, 'Show Color Bars', group='Indicators: SSL Hybrid', inline='SH2'),
    maType=input.string('HMA', 'Baseline Type                       ', group='Indicators: SSL Hybrid', inline='SH3', options=('SMA', 'EMA', 'DEMA', 'TEMA', 'LSMA', 'WMA', 'MF', 'VAMA', 'TMA', 'HMA', 'JMA', 'Kijun v2', 'EDSMA', 'McGinley')),
    len=input.int(60, 'Baseline Length                      ', group='Indicators: SSL Hybrid', inline='SH4'),
    src: Series[float] = input.source(close, 'Source                          ', group='Indicators: SSL Hybrid', inline='SH5'),
    kidiv=input.int(1, 'Kijun MOD Divider                     ', group='Indicators: SSL Hybrid', inline='SH6', maxval=4),
    jurik_phase=input.int(3, '* Jurik (JMA) Only - Phase                 ', group='Indicators: SSL Hybrid', inline='SH7'),
    jurik_power=input.int(1, '* Jurik (JMA) Only - Power                 ', group='Indicators: SSL Hybrid', inline='SH8'),
    volatility_lookback=input.int(10, '* Volatility Adjusted (VAMA) Only - Volatility lookback length', group='Indicators: SSL Hybrid', inline='SH9'),
    beta=input.float(0.8, 'Modular Filter, General Filter Only - Beta               ', group='Indicators: SSL Hybrid', inline='SH10', minval=0, maxval=1, step=0.1),
    feedback=input.bool(False, 'Modular Filter Only - Feedback', group='Indicators: SSL Hybrid', inline='SH11'),
    z=input.float(0.5, 'Modular Filter Only - Feedback Weighting               ', group='Indicators: SSL Hybrid', inline='SH12', step=0.1, minval=0, maxval=1),
    ssfLength=input.int(20, 'EDSMA - Super Smoother Filter Length               ', group='Indicators: SSL Hybrid', inline='SH13', minval=1),
    ssfPoles=input.int(2, 'EDSMA - Super Smoother Filter Poles               ', group='Indicators: SSL Hybrid', inline='SH14', options=(2, 3)),
    useTrueRange=input.bool(True, 'Use True Range?', group='Indicators: SSL Hybrid', inline='SH15'),
    multy=input.float(0.2, 'Base Channel Multiplier                   ', group='Indicators: SSL Hybrid', inline='SH16', step=0.05),
    emaLength=input.int(200, 'EMA Length          ', group='Indicators: EMA', inline='E1', minval=1),
    kcLength=input.int(20, 'Length              ', group='Indicators: Keltner Channel', inline='KC1', minval=1),
    kcMult=input.float(1.5, 'Multiplier             ', group='Indicators: Keltner Channel', inline='KC2'),
    kcSrc: Series[float] = input.source(close, 'Source              ', group='Indicators: Keltner Channel', inline='KC3'),
    alen=input.int(10, 'ATR Length            ', group='Indicators: Keltner Channel', inline='KC4', minval=1),
    chPeriod=input.int(20, 'Period             ', group='Indicators: Candle Height', inline='CH1'),
    nnfxAtrLength=input.int(14, 'Length              ', group='Indicators: NNFX ATR (Stop Loss Settings)', inline='ATR1', minval=1),
    nnfxSmoothing=input.string('RMA', 'Smoothing            ', group='Indicators: NNFX ATR (Stop Loss Settings)', inline='ATR3', options=('RMA', 'SMA', 'EMA', 'WMA'))
):
    ap = hlc3
    esa = ta.ema(ap, n1)
    d = ta.ema(math.abs(ap - esa), n1)
    ci = (ap - esa) / (0.015 * d)
    tci = ta.ema(ci, n2)
    wt1 = tci
    wt2 = ta.sma(wt1, 4)
    wtBreakUp = ta.crossover(wt1, wt2)
    wtBreakDown = ta.crossunder(wt1, wt2)
    barColour = (color.fuchsia if wtBreakUp else color.orange if wtBreakDown else na) if showWaveTrend else na
    barcolor(color=barColour)
    smaHigh = ta.sma(high, sslChLen)
    smaLow = ta.sma(low, sslChLen)
    sslChHlv: PersistentSeries[int] = na(int)
    sslChHlv = 1 if close > smaHigh else -1 if close < smaLow else sslChHlv[1]
    sslChDown = smaHigh if sslChHlv < 0 else smaLow
    sslChUp = smaLow if sslChHlv < 0 else smaHigh
    plot(sslChDown if showSslChannel else na, 'SSL Channel Down', linewidth=1, color=color.new(color.red, 30))
    plot(sslChUp if showSslChannel else na, 'SSL Channel Up', linewidth=1, color=color.new(color.lime, 30))
    def get2PoleSSF(src, length):
        PI = 2 * math.asin(1)
        arg = math.sqrt(2) * PI / length
        a1 = math.exp(-arg)
        b1 = 2 * a1 * math.cos(arg)
        c2 = b1
        c3 = -math.pow(a1, 2)
        c1 = 1 - c2 - c3
        ssf: Series[float] = 0.0
        ssf = c1 * src + c2 * nz(ssf[1]) + c3 * nz(ssf[2])
        return ssf

    def get3PoleSSF(src, length):
        PI = 2 * math.asin(1)
        arg = PI / length
        a1 = math.exp(-arg)
        b1 = 2 * a1 * math.cos(1.738 * arg)
        c1 = math.pow(a1, 2)
        coef2 = b1 + c1
        coef3 = -(c1 + b1 * c1)
        coef4 = math.pow(c1, 2)
        coef1 = 1 - coef2 - coef3 - coef4
        ssf: Series[float] = 0.0
        ssf = coef1 * src + coef2 * nz(ssf[1]) + coef3 * nz(ssf[2]) + coef4 * nz(ssf[3])
        return ssf

    def ma(type, src: Series, len):
        result: float = 0
        if type == 'TMA':
            result = ta.sma(ta.sma(src, math.ceil(len / 2)), math.floor(len / 2) + 1)
        if type == 'MF':
            ts: Series[float] = 0.0
            b: Series[float] = 0.0
            c: Series[float] = 0.0
            os: Series[float] = 0.0
            alpha = 2 / (len + 1)
            a = z * src + (1 - z) * nz(ts[1], src) if feedback else src
            b = a if a > alpha * a + (1 - alpha) * nz(b[1], a) else alpha * a + (1 - alpha) * nz(b[1], a)
            c = a if a < alpha * a + (1 - alpha) * nz(c[1], a) else alpha * a + (1 - alpha) * nz(c[1], a)
            os = 1 if a == b else 0 if a == c else os[1]
            upper = beta * b + (1 - beta) * c
            lower = beta * c + (1 - beta) * b
            ts = os * upper + (1 - os) * lower
            result = ts
        if type == 'LSMA':
            result = ta.linreg(src, len, 0)
        if type == 'SMA':
            result = ta.sma(src, len)
        if type == 'EMA':
            result = ta.ema(src, len)
        if type == 'DEMA':
            e = ta.ema(src, len)
            result = 2 * e - ta.ema(e, len)
        if type == 'TEMA':
            e = ta.ema(src, len)
            result = 3 * (e - ta.ema(e, len)) + ta.ema(ta.ema(e, len), len)
        if type == 'WMA':
            result = ta.wma(src, len)
        if type == 'VAMA':
            mid = ta.ema(src, len)
            dev = src - mid
            vol_up = ta.highest(dev, volatility_lookback)
            vol_down = ta.lowest(dev, volatility_lookback)
            result = mid + math.avg(vol_up, vol_down)
        if type == 'HMA':
            result = ta.wma(2 * ta.wma(src, len / 2) - ta.wma(src, len), math.round(math.sqrt(len)))
        if type == 'JMA':
            phaseRatio = 0.5 if jurik_phase < -100 else 2.5 if jurik_phase > 100 else jurik_phase / 100 + 1.5
            beta__00000095__ = 0.45 * (len - 1) / (0.45 * (len - 1) + 2)
            alpha = math.pow(beta__00000095__, jurik_power)
            jma: Series[float] = 0.0
            e0: Series[float] = 0.0
            e0 = (1 - alpha) * src + alpha * nz(e0[1])
            e1: Series[float] = 0.0
            e1 = (src - e0) * (1 - beta__00000095__) + beta__00000095__ * nz(e1[1])
            e2: Series[float] = 0.0
            e2 = (e0 + phaseRatio * e1 - nz(jma[1])) * math.pow(1 - alpha, 2) + math.pow(alpha, 2) * nz(e2[1])
            jma = e2 + nz(jma[1])
            result = jma
        if type == 'Kijun v2':
            kijun = math.avg(ta.lowest(len), ta.highest(len))
            conversionLine = math.avg(ta.lowest(len / kidiv), ta.highest(len / kidiv))
            delta = (kijun + conversionLine) / 2
            result = delta
        if type == 'McGinley':
            mg: Series[float] = 0.0
            mg = ta.ema(src, len) if na(mg[1]) else mg[1] + (src - mg[1]) / (len * math.pow(src / mg[1], 4))
            result = mg
        if type == 'EDSMA':
            zeros: Series = src - nz(src[2])
            avgZeros = (zeros + zeros[1]) / 2
            ssf = get2PoleSSF(avgZeros, ssfLength) if ssfPoles == 2 else get3PoleSSF(avgZeros, ssfLength)
            stdev = ta.stdev(ssf, len)
            scaledFilter = ssf / stdev if stdev != 0 else 0
            alpha = 5 * math.abs(scaledFilter) / len
            edsma: Series[float] = 0.0
            edsma = alpha * src + (1 - alpha) * nz(edsma[1])
            result = edsma
        return result

    BBMC = ma(maType, close, len)
    Keltma = ma(maType, src, len)
    range_1 = ta.tr if useTrueRange else high - low
    rangema = ta.ema(range_1, len)
    upperk = Keltma + rangema * multy
    lowerk = Keltma - rangema * multy
    color_bar = color.new('#00C3FF') if close > upperk else color.new('#FF0062') if close < lowerk else color.gray
    p1 = plot(BBMC if showSslHybrid else na, color=color.new(color_bar, 0), linewidth=4, title='MA Baseline')
    barcolor(color_bar if show_color_bar else na)
    ema = ta.ema(close, emaLength)
    plot(ema if showEma else na, 'EMA Trend Line', color.white)
    kcMa = ta.ema(kcSrc, kcLength)
    KTop2 = kcMa + kcMult * ta.atr(alen)
    KBot2 = kcMa - kcMult * ta.atr(alen)
    upperPlot = plot(KTop2 if showKeltner else na, color=color.new(color.blue, 0), title='Upper', style=plot.style_stepline)
    lowerPlot = plot(KBot2 if showKeltner else na, color=color.new(color.blue, 0), title='Lower', style=plot.style_stepline)
    percentHL = (high - low) / low * 100
    percentRed = (open - close) / close * 100 if open > close else 0
    percentGreen = (close - open) / open * 100 if open < close else 0
    def function(source, length):
        __block_result__ = na
        if nnfxSmoothing == 'RMA':
            __block_result__ = ta.rma(source, nnfxAtrLength)
        else:
            __block_result_1__ = na
            if nnfxSmoothing == 'SMA':
                __block_result_1__ = ta.sma(source, nnfxAtrLength)
            else:
                __block_result_2__ = na
                if nnfxSmoothing == 'EMA':
                    __block_result_2__ = ta.ema(source, nnfxAtrLength)
                else:
                    __block_result_2__ = ta.wma(source, nnfxAtrLength)
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    def formula(number, decimals):
        factor = math.pow(10, decimals)
        return cast_int(number * factor) / factor

    nnfxAtr = formula(function(ta.tr(True), nnfxAtrLength), 5) * slAtrMultiplier
    longSlAtr = close - nnfxAtr if nnfxAtrLength else close + nnfxAtr
    shortSlAtr = close + nnfxAtr if nnfxAtrLength else close - nnfxAtr
    plot(longSlAtr if showAtrSl else na, 'Long SL', color=color.new(color.red, 35), linewidth=1, trackprice=True, editable=True, style=plot.style_stepline)
    plot(shortSlAtr if showAtrSl else na, 'Short SL', color=color.new(color.red, 35), linewidth=1, trackprice=True, editable=True, style=plot.style_stepline)
    def percentAsPoints(pcnt):
        return math.round(pcnt / 100 * close / syminfo.mintick)

    def calcStopLossPrice(pointsOffset, isLong):
        priceOffset = pointsOffset * syminfo.mintick
        __block_result_3__ = na
        if isLong:
            __block_result_3__ = close - priceOffset
        else:
            __block_result_3__ = close + priceOffset
        return __block_result_3__

    def calcProfitTrgtPrice(pointsOffset, isLong):
        return calcStopLossPrice(-pointsOffset, isLong)

    def printLabel(barIndex, msg):
        return label.new(barIndex, close, msg)

    def printTpSlHitBox(left, right, slHit, tpHit, entryPrice, slPrice, tpPrice):
        __block_result_4__ = na
        if showTpSlBoxes:
            box.new(left=left, top=entryPrice, right=right, bottom=slPrice, bgcolor=color.new(color.red, 60) if slHit else color.new(color.gray, 90), border_width=0)
            box.new(left=left, top=entryPrice, right=right, bottom=tpPrice, bgcolor=color.new(color.green, 60) if tpHit else color.new(color.gray, 90), border_width=0)
            line.new(x1=left, y1=entryPrice, x2=right, y2=entryPrice, color=color.new(color.yellow, 20))
            line.new(x1=left, y1=slPrice, x2=right, y2=slPrice, color=color.new(color.red, 20))
            __block_result_4__ = line.new(x1=left, y1=tpPrice, x2=right, y2=tpPrice, color=color.new(color.green, 20))
        return __block_result_4__

    def printTpSlNotHitBox(left, right, entryPrice, slPrice, tpPrice):
        __block_result_5__ = na
        if showTpSlBoxes:
            box.new(left=left, top=entryPrice, right=right, bottom=slPrice, bgcolor=color.new(color.gray, 90), border_width=0)
            box.new(left=left, top=entryPrice, right=right, bottom=tpPrice, bgcolor=color.new(color.gray, 90), border_width=0)
            line.new(x1=left, y1=entryPrice, x2=right, y2=entryPrice, color=color.new(color.yellow, 20))
            line.new(x1=left, y1=slPrice, x2=right, y2=slPrice, color=color.new(color.red, 20))
            __block_result_5__ = line.new(x1=left, y1=tpPrice, x2=right, y2=tpPrice, color=color.new(color.green, 20))
        return __block_result_5__

    def printTradeExitLabel(x, y, posSize, entryPrice, pnl):
        __block_result_6__ = na
        if showLabels:
            labelStr = 'Position Size: ' + string.tostring(math.abs(posSize), '#.##') + '\nPNL: ' + string.tostring(pnl, '#.##') + '\nCapital: ' + string.tostring(strategy.equity, '#.##') + '\nEntry Price: ' + string.tostring(entryPrice, '#.##')
            __block_result_6__ = label.new(x=x, y=y, text=labelStr, color=color.new(color.green, 60) if pnl > 0 else color.new(color.red, 60), textcolor=color.white, style=label.style_label_down)
        return __block_result_6__

    tradeEntryBar: Persistent = bar_index
    profitPoints: Persistent[float] = 0.0
    lossPoints: Persistent[float] = 0.0
    slPrice: Persistent[float] = 0.0
    tpPrice: Persistent[float] = 0.0
    inLong: Persistent[bool] = False
    inShort: Persistent[bool] = False
    slAmount = nnfxAtr
    slPercent = math.abs((1 - (close - slAmount) / close) * 100)
    tpPercent = slPercent * riskReward
    tpPoints = percentAsPoints(tpPercent)
    tpTarget = calcProfitTrgtPrice(tpPoints, wtBreakUp)
    inDateRange = time >= timestamp(syminfo.timezone, startYear, startMonth, startDate, 0, 0) and time < timestamp(syminfo.timezone, endYear, endMonth, endDate, 0, 0)
    bullSslHybrid = close > upperk if useSslHybrid else True
    bearSslHybrid = close < lowerk if useSslHybrid else True
    bullSslChannel = ta.crossover(sslChUp, sslChDown)
    bearSslChannel = ta.crossover(sslChDown, sslChUp)
    bullWaveTrend = wtBreakUp
    bearWaveTrend = wtBreakDown
    candleHeightValid = percentGreen <= candleHeight and percentRed <= candleHeight if useCandleHeight else True
    withinCh = high < KTop2 and low > KBot2 if keltnerChWicks else open < KTop2 and close < KTop2 and (open > KBot2) and (close > KBot2)
    insideKeltnerCh = withinCh if useKeltnerCh else True
    bullTpValid = not (close < ema and tpTarget > ema) if useEma else True
    bearTpValid = not (close > ema and tpTarget < ema) if useEma else True
    goLong = inDateRange and bullSslHybrid and bullSslChannel and bullWaveTrend and candleHeightValid and insideKeltnerCh and bullTpValid
    goShort = inDateRange and bearSslHybrid and bearSslChannel and bearWaveTrend and candleHeightValid and insideKeltnerCh and bearTpValid
    openLong = goLong and (not inLong)
    openShort = goShort and (not inShort)
    flippingSides = goLong and inShort or (goShort and inLong)
    enteringTrade = openLong or openShort
    inTrade = inLong or inShort
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
        alert(message='BUY Trade Entry Alert', freq=alert.freq_once_per_bar_close)
    if openShort:
        if strategy.position_size > 0:
            printTpSlNotHitBox(tradeEntryBar + 1, bar_index + 1, strategy.position_avg_price, slPrice, tpPrice)
            printTradeExitLabel(bar_index + 1, math.max(tpPrice, slPrice), strategy.position_size, strategy.position_avg_price, strategy.openprofit)
        strategy.entry('Short', strategy.short, qty=entryQty, alert_message='Short Entry')
        enteringTrade = True
        inShort = True
        inLong = False
        alert(message='SELL Trade Entry Alert', freq=alert.freq_once_per_bar_close)
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
    entryPrice = strategy.closedtrades.entry_price(strategy.closedtrades - 1)
    pnl = strategy.closedtrades.profit(strategy.closedtrades - 1)
    posSize = strategy.closedtrades.size(strategy.closedtrades - 1)
    if inTrade and exitTriggered:
        inShort = False
        inLong = False
        printTpSlHitBox(tradeEntryBar + 1, bar_index, slHit, tpHit, entryPrice, slPrice, tpPrice)
        printTradeExitLabel(bar_index, math.max(tpPrice, slPrice), posSize, entryPrice, pnl)
    if barstate.islastconfirmedhistory and strategy.position_size != 0:
        printTpSlNotHitBox(tradeEntryBar + 1, bar_index + 1, strategy.position_avg_price, slPrice, tpPrice)
    plotchar(goLong, 'Enter Long', '')
    plotchar(goShort, 'Enter Short', '')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
