"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, bar_index, barcolor, close, color, currency, display, high, hline,
    input, label, location, low, math, na, nz, open, plot, plotarrow, plotchar, script, strategy,
    string, syminfo, ta, time, timestamp
)
from pynecore.types import NA, Series


@script.strategy('QQE MOD + SSL Hybrid + Waddah Attar Explosion', overlay=False, initial_capital=1000, currency=currency.NONE, max_labels_count=500, default_qty_type=strategy.cash, commission_type=strategy.commission.percent, commission_value=0.01, margin_long=0, margin_short=0, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    swingLength=input.int(10, 'Swing High/Low Lookback Length', group='Strategy: Risk Management', tooltip='Stop Loss is calculated by the swing high or low over the previous X candles'),
    accountRiskPercent=input.float(2, 'Account percent loss per trade', step=0.1, group='Strategy: Risk Management', tooltip='Each trade will risk X% of the account balance'),
    start_year=input.int(title='Start Date', defval=2022, minval=2010, maxval=3000, group='Strategy: Date Range', inline='1'),
    start_month=input.int(title='', defval=1, group='Strategy: Date Range', inline='1', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)),
    start_date=input.int(title='', defval=1, group='Strategy: Date Range', inline='1', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31)),
    end_year=input.int(title='End Date', defval=2030, minval=1800, maxval=3000, group='Strategy: Date Range', inline='2'),
    end_month=input.int(title='', defval=1, group='Strategy: Date Range', inline='2', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)),
    end_date=input.int(title='', defval=1, group='Strategy: Date Range', inline='2', options=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31)),
    RSI_Period=input.int(6, title='RSI Length', group='Indicators: QQE Mod Settings'),
    SF=input.int(6, title='RSI Smoothing', group='Indicators: QQE Mod Settings'),
    QQE=input.int(3, title='Fast QQE Factor', group='Indicators: QQE Mod Settings'),
    ThreshHold=input.int(3, title='Thresh-hold', group='Indicators: QQE Mod Settings'),
    qqeSrc: Series[float] = input(close, title='RSI Source', group='Indicators: QQE Mod Settings'),
    length=input.int(50, minval=1, title='Bollinger Length', group='Indicators: QQE Mod Settings'),
    qqeMult=input.float(0.35, minval=0.001, maxval=5, step=0.1, title='BB Multiplier', group='Indicators: QQE Mod Settings'),
    RSI_Period2=input.int(6, title='RSI Length', group='Indicators: QQE Mod Settings'),
    SF2=input.int(5, title='RSI Smoothing', group='Indicators: QQE Mod Settings'),
    QQE2=input.float(1.61, title='Fast QQE2 Factor', group='Indicators: QQE Mod Settings'),
    ThreshHold2=input.int(3, title='Thresh-hold', group='Indicators: QQE Mod Settings'),
    src2: Series[float] = input(close, title='RSI Source', group='Indicators: QQE Mod Settings'),
    show_Baseline=input(title='Show Baseline', defval=True),
    show_SSL1=input(title='Show SSL1', defval=False),
    show_atr=input(title='Show ATR bands', defval=True),
    atrlen=input(14, 'ATR Period'),
    mult=input.float(1, 'ATR Multi', step=0.1),
    smoothing=input.string(title='ATR Smoothing', defval='WMA', options=('RMA', 'SMA', 'EMA', 'WMA')),
    maType=input.string(title='SSL1 / Baseline Type', defval='HMA', options=('SMA', 'EMA', 'DEMA', 'TEMA', 'LSMA', 'WMA', 'MF', 'VAMA', 'TMA', 'HMA', 'JMA', 'Kijun v2', 'EDSMA', 'McGinley')),
    len=input(title='SSL1 / Baseline Length', defval=60),
    SSL2Type=input.string(title='SSL2 / Continuation Type', defval='JMA', options=('SMA', 'EMA', 'DEMA', 'TEMA', 'WMA', 'MF', 'VAMA', 'TMA', 'HMA', 'JMA', 'McGinley')),
    len2=input(title='SSL 2 Length', defval=5),
    SSL3Type=input.string(title='EXIT Type', defval='HMA', options=('DEMA', 'TEMA', 'LSMA', 'VAMA', 'TMA', 'HMA', 'JMA', 'Kijun v2', 'McGinley', 'MF')),
    len3=input(title='EXIT Length', defval=15),
    src: Series[float] = input(title='Source', defval=close),
    kidiv=input.int(defval=1, maxval=4, title='Kijun MOD Divider'),
    jurik_phase=input(title='* Jurik (JMA) Only - Phase', defval=3),
    jurik_power=input(title='* Jurik (JMA) Only - Power', defval=1),
    volatility_lookback=input(10, title='* Volatility Adjusted (VAMA) Only - Volatility lookback length'),
    beta=input.float(0.8, minval=0, maxval=1, step=0.1, title='Modular Filter, General Filter Only - Beta'),
    feedback=input(False, title='Modular Filter Only - Feedback'),
    z=input.float(0.5, title='Modular Filter Only - Feedback Weighting', step=0.1, minval=0, maxval=1),
    ssfLength=input.int(title='EDSMA - Super Smoother Filter Length', minval=1, defval=20),
    ssfPoles=input.int(title='EDSMA - Super Smoother Filter Poles', defval=2, options=(2, 3)),
    useTrueRange=input(True),
    multy=input.float(0.2, step=0.05, title='Base Channel Multiplier'),
    show_color_bar=input(title='Color Bars', defval=True),
    sensitivity=input.int(180, title='Sensitivity', group='Indicators: Waddah Attar Explosion'),
    fastLength=input.int(20, title='FastEMA Length', group='Indicators: Waddah Attar Explosion'),
    slowLength=input.int(40, title='SlowEMA Length', group='Indicators: Waddah Attar Explosion'),
    channelLength=input.int(20, title='BB Channel Length', group='Indicators: Waddah Attar Explosion'),
    waeMult=input.float(2.0, title='BB Stdev Multiplier', group='Indicators: Waddah Attar Explosion')
):
    in_date_range = time >= timestamp(syminfo.timezone, start_year, start_month, start_date, 0, 0) and time < timestamp(syminfo.timezone, end_year, end_month, end_date, 0, 0)
    Wilders_Period = RSI_Period * 2 - 1
    Rsi = ta.rsi(qqeSrc, RSI_Period)
    RsiMa: Series = ta.ema(Rsi, SF)
    AtrRsi = math.abs(RsiMa[1] - RsiMa)
    MaAtrRsi = ta.ema(AtrRsi, Wilders_Period)
    dar = ta.ema(MaAtrRsi, Wilders_Period) * QQE
    longband: Series[float] = 0.0
    shortband: Series[float] = 0.0
    trend: Series[int] = 0
    DeltaFastAtrRsi = dar
    RSIndex: Series = RsiMa
    newshortband = RSIndex + DeltaFastAtrRsi
    newlongband = RSIndex - DeltaFastAtrRsi
    longband = math.max(longband[1], newlongband) if RSIndex[1] > longband[1] and RSIndex > longband[1] else newlongband
    shortband = math.min(shortband[1], newshortband) if RSIndex[1] < shortband[1] and RSIndex < shortband[1] else newshortband
    cross_1 = ta.cross(longband[1], RSIndex)
    trend = 1 if ta.cross(RSIndex, shortband[1]) else -1 if cross_1 else nz(trend[1], 1)
    FastAtrRsiTL = longband if trend == 1 else shortband
    basis = ta.sma(FastAtrRsiTL - 50, length)
    dev = qqeMult * ta.stdev(FastAtrRsiTL - 50, length)
    upper = basis + dev
    lower = basis - dev
    QQEzlong: Series[int] = 0
    QQEzlong = nz(QQEzlong[1])
    QQEzshort: Series[int] = 0
    QQEzshort = nz(QQEzshort[1])
    QQEzlong = QQEzlong + 1 if RSIndex >= 50 else 0
    QQEzshort = QQEzshort + 1 if RSIndex < 50 else 0
    Zero = hline(0, color=color.white, linestyle=hline.style_dotted, linewidth=1, display=display.none)
    Wilders_Period2 = RSI_Period2 * 2 - 1
    Rsi2 = ta.rsi(src2, RSI_Period2)
    RsiMa2: Series = ta.ema(Rsi2, SF2)
    AtrRsi2 = math.abs(RsiMa2[1] - RsiMa2)
    MaAtrRsi2 = ta.ema(AtrRsi2, Wilders_Period2)
    dar2 = ta.ema(MaAtrRsi2, Wilders_Period2) * QQE2
    longband2: Series[float] = 0.0
    shortband2: Series[float] = 0.0
    trend2: Series[int] = 0
    DeltaFastAtrRsi2 = dar2
    RSIndex2: Series = RsiMa2
    newshortband2 = RSIndex2 + DeltaFastAtrRsi2
    newlongband2 = RSIndex2 - DeltaFastAtrRsi2
    longband2 = math.max(longband2[1], newlongband2) if RSIndex2[1] > longband2[1] and RSIndex2 > longband2[1] else newlongband2
    shortband2 = math.min(shortband2[1], newshortband2) if RSIndex2[1] < shortband2[1] and RSIndex2 < shortband2[1] else newshortband2
    cross_2 = ta.cross(longband2[1], RSIndex2)
    trend2 = 1 if ta.cross(RSIndex2, shortband2[1]) else -1 if cross_2 else nz(trend2[1], 1)
    FastAtrRsi2TL = longband2 if trend2 == 1 else shortband2
    QQE2zlong: Series[int] = 0
    QQE2zlong = nz(QQE2zlong[1])
    QQE2zshort: Series[int] = 0
    QQE2zshort = nz(QQE2zshort[1])
    QQE2zlong = QQE2zlong + 1 if RSIndex2 >= 50 else 0
    QQE2zshort = QQE2zshort + 1 if RSIndex2 < 50 else 0
    hcolor2 = color.silver if RsiMa2 - 50 > ThreshHold2 else color.silver if RsiMa2 - 50 < 0 - ThreshHold2 else na
    plot(RsiMa2 - 50, color=hcolor2, title='Histo2', style=plot.style_columns)
    Greenbar1 = RsiMa2 - 50 > ThreshHold2
    Greenbar2 = RsiMa - 50 > upper
    Redbar1 = RsiMa2 - 50 < 0 - ThreshHold2
    Redbar2 = RsiMa - 50 < lower
    plot(RsiMa2 - 50 if Greenbar1 and Greenbar2 == cast_bool(1) else na, title='QQE Up', style=plot.style_columns, color=color.new(color.new('#00C3FF'), 0))
    plot(RsiMa2 - 50 if Redbar1 and Redbar2 == cast_bool(1) else na, title='QQE Down', style=plot.style_columns, color=color.new(color.new('#FF0062'), 0))
    def ma_function(source, atrlen):
        __block_result__ = na
        if smoothing == 'RMA':
            __block_result__ = ta.rma(source, atrlen)
        else:
            __block_result_1__ = na
            if smoothing == 'SMA':
                __block_result_1__ = ta.sma(source, atrlen)
            else:
                __block_result_2__ = na
                if smoothing == 'EMA':
                    __block_result_2__ = ta.ema(source, atrlen)
                else:
                    __block_result_2__ = ta.wma(source, atrlen)
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    atr_slen = ma_function(ta.tr(True), atrlen)
    upper_band = atr_slen * mult + close
    lower_band = close - atr_slen * mult
    def tema(src, len):
        ema1 = ta.ema(src, len)
        ema2 = ta.ema(ema1, len)
        ema3 = ta.ema(ema2, len)
        return 3 * ema1 - 3 * ema2 + ema3

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
            upper__000000a1__ = beta * b + (1 - beta) * c
            lower__000000a1__ = beta * c + (1 - beta) * b
            ts = os * upper__000000a1__ + (1 - os) * lower__000000a1__
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
            dev__000000b6__ = src - mid
            vol_up = ta.highest(dev__000000b6__, volatility_lookback)
            vol_down = ta.lowest(dev__000000b6__, volatility_lookback)
            result = mid + math.avg(vol_up, vol_down)
        if type == 'HMA':
            result = ta.wma(2 * ta.wma(src, len / 2) - ta.wma(src, len), math.round(math.sqrt(len)))
        if type == 'JMA':
            phaseRatio = 0.5 if jurik_phase < -100 else 2.5 if jurik_phase > 100 else jurik_phase / 100 + 1.5
            beta__000000ca__ = 0.45 * (len - 1) / (0.45 * (len - 1) + 2)
            alpha = math.pow(beta__000000ca__, jurik_power)
            jma: Series[float] = 0.0
            e0: Series[float] = 0.0
            e0 = (1 - alpha) * src + alpha * nz(e0[1])
            e1__000000ca__: Series[float] = 0.0
            e1__000000ca__ = (src - e0) * (1 - beta__000000ca__) + beta__000000ca__ * nz(e1__000000ca__[1])
            e2: Series[float] = 0.0
            e2 = (e0 + phaseRatio * e1__000000ca__ - nz(jma[1])) * math.pow(1 - alpha, 2) + math.pow(alpha, 2) * nz(e2[1])
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

    emaHigh = ma(maType, high, len)
    emaLow = ma(maType, low, len)
    maHigh = ma(SSL2Type, high, len2)
    maLow = ma(SSL2Type, low, len2)
    ExitHigh = ma(SSL3Type, high, len3)
    ExitLow = ma(SSL3Type, low, len3)
    BBMC = ma(maType, close, len)
    Keltma = ma(maType, src, len)
    range_1 = ta.tr if useTrueRange else high - low
    rangema = ta.ema(range_1, len)
    upperk = Keltma + rangema * multy
    lowerk = Keltma - rangema * multy
    open_pos = open * 1
    close_pos = close * 1
    difference = math.abs(close_pos - open_pos)
    atr_violation = difference > atr_slen
    InRange = upper_band > BBMC and lower_band < BBMC
    Hlv: Series = NA(int)
    Hlv = 1 if close > emaHigh else -1 if close < emaLow else Hlv[1]
    sslDown = emaHigh if Hlv < 0 else emaLow
    Hlv3: Series = NA(int)
    Hlv3 = 1 if close > ExitHigh else -1 if close < ExitLow else Hlv3[1]
    sslExit = ExitHigh if Hlv3 < 0 else ExitLow
    base_cross_Long = ta.crossover(close, sslExit)
    base_cross_Short = ta.crossover(sslExit, close)
    codiff = 1 if base_cross_Long else -1 if base_cross_Short else na
    color_bar = color.new('#00C3FF') if close > upperk else color.new('#FF0062') if close < lowerk else color.gray
    color_ssl1 = color.new('#00C3FF') if close > sslDown else color.new('#FF0062') if close < sslDown else na
    plotarrow(codiff, colorup=color.new(color.new('#00C3FF'), 20), colordown=color.new(color.new('#FF0062'), 20), title='Exit Arrows', maxheight=20, offset=0, display=display.none)
    p1 = plot(0, color=color_bar, linewidth=3, title='MA Baseline')
    barcolor(color_bar if show_color_bar else na)
    def calc_macd(source, fastLength, slowLength):
        fastMA = ta.ema(source, fastLength)
        slowMA = ta.ema(source, slowLength)
        return fastMA - slowMA

    def calc_BBUpper(source, length, mult):
        basis = ta.sma(source, length)
        dev = mult * ta.stdev(source, length)
        return basis + dev

    def calc_BBLower(source, length, mult):
        basis = ta.sma(source, length)
        dev = mult * ta.stdev(source, length)
        return basis - dev

    t1 = (calc_macd(close, fastLength, slowLength) - calc_macd(close[1], fastLength, slowLength)) * sensitivity
    e1 = calc_BBUpper(close, channelLength, waeMult) - calc_BBLower(close, channelLength, waeMult)
    trendUp: Series = t1 if t1 >= 0 else 0
    trendDown: Series = -1 * t1 if t1 < 0 else 0
    plot(trendUp, style=plot.style_columns, linewidth=1, color=color.lime if trendUp < trendUp[1] else color.green, title='UpTrend', display=display.none)
    plot(trendDown, style=plot.style_columns, linewidth=1, color=color.orange if trendDown < trendDown[1] else color.red, title='DownTrend', display=display.none)
    plot(e1, style=plot.style_line, linewidth=2, color=color.yellow, title='ExplosionLine', display=display.none)
    qqeGreenBar: Series = Greenbar1 and Greenbar2
    qqeRedBar: Series = Redbar1 and Redbar2
    qqeBuy = qqeGreenBar and (not qqeGreenBar[1])
    qqeSell = qqeRedBar and (not qqeRedBar[1])
    sslBuy = close > upperk and close > BBMC
    sslSell = close < lowerk and close < BBMC
    waeBuy = trendUp > 0 and trendUp > e1
    waeSell = trendDown > 0 and trendDown > e1
    inLong = strategy.position_size > 0
    inShort = strategy.position_size < 0
    longCondition = qqeBuy and sslBuy and waeBuy and in_date_range
    shortCondition = qqeSell and sslSell and waeSell and in_date_range
    swingLow = ta.lowest(source=low, length=swingLength)
    swingHigh = ta.highest(source=high, length=swingLength)
    longStopPercent = math.abs((1 - swingLow / close) * 100)
    shortStopPercent = math.abs((1 - swingHigh / close) * 100)
    riskAmt = strategy.equity * accountRiskPercent / 100
    longQty = math.abs(riskAmt / longStopPercent * 100) / close
    shortQty = math.abs(riskAmt / shortStopPercent * 100) / close
    if longCondition and (not inShort) and (not inLong):
        strategy.entry('Long', strategy.long, qty=longQty)
        strategy.exit('Long  SL/TP', from_entry='Long', stop=swingLow, alert_message='Long SL Hit')
        buyLabel = label.new(x=bar_index, y=high[1], color=color.green, style=label.style_label_up)
        label.set_y(id=buyLabel, y=0)
        label.set_tooltip(id=buyLabel, tooltip='Risk Amt: ' + string.tostring(riskAmt) + ' Qty: ' + string.tostring(longQty) + ' Swing low: ' + string.tostring(swingLow) + ' Stop Percent: ' + string.tostring(longStopPercent))
        alert(message='BUY Trade Entry Alert', freq=alert.freq_once_per_bar_close)
    if shortCondition and (not inLong) and (not inShort):
        strategy.entry('Short', strategy.short, qty=shortQty)
        strategy.exit('Short  SL/TP', from_entry='Short', stop=swingHigh, alert_message='Short SL Hit')
        sellLabel = label.new(x=bar_index, y=high[1], color=color.red, style=label.style_label_up)
        label.set_y(id=sellLabel, y=0)
        label.set_tooltip(id=sellLabel, tooltip='Risk Amt: ' + string.tostring(riskAmt) + ' Qty: ' + string.tostring(shortQty) + ' Swing high: ' + string.tostring(swingHigh) + ' Stop Percent: ' + string.tostring(shortStopPercent))
        alert(message='SELL Trade Entry Alert', freq=alert.freq_once_per_bar_close)
    def openTradesInProfit():
        result: float = 0.0
        __loop_0__ = pine_loop(0, 1)
        while __loop_0__.step(strategy.opentrades - 1):
            i = __loop_0__.value
            result = result + strategy.opentrades.profit(i)
        return result > 0

    openTradesInProfit_1 = openTradesInProfit()
    exitLong = inLong and base_cross_Short and openTradesInProfit_1
    if exitLong:
        strategy.close(id='Long', comment='Closing Long', alert_message='Long TP Hit')
    openTradesInProfit_2 = openTradesInProfit()
    exitShort = inShort and base_cross_Long and openTradesInProfit_2
    if exitShort:
        strategy.close(id='Short', comment='Closing Short', alert_message='Short TP Hit')
    plotchar(0, '===========', '', location=location.top, color=color.new('#141823'))
    plotchar(0, 'BUY SIGNALS:', '', location=location.top, color=color.new('#141823'))
    plotchar(0, '===========', '', location=location.top, color=color.new('#141823'))
    plotchar(qqeBuy, 'QQE Mod: Buy Signal', '', location=location.top, color=color.green if qqeBuy else color.orange)
    plotchar(sslBuy, 'SSL Hybrid: Buy Signal', '', location=location.top, color=color.green if sslBuy else color.orange)
    plotchar(waeBuy, 'Waddah Attar Explosion: Buy Signal', '', location=location.top, color=color.green if waeBuy else color.orange)
    plotchar(inLong, 'inLong', '', location=location.top, color=color.green if inLong else color.orange)
    plotchar(exitLong, 'Exit Long', '', location=location.top, color=color.green if exitLong else color.orange)
    plotchar(0, '============', '', location=location.top, color=color.new('#141823'))
    plotchar(0, 'SELL SIGNALS:', '', location=location.top, color=color.new('#141823'))
    plotchar(0, '============', '', location=location.top, color=color.new('#141823'))
    plotchar(qqeSell, 'QQE Mod: Sell Signal', '', location=location.top, color=color.red if qqeSell else color.orange)
    plotchar(sslSell, 'SSL Hybrid: Sell Signal', '', location=location.top, color=color.red if sslSell else color.orange)
    plotchar(waeSell, 'Waddah Attar Explosion: Sell Signal', '', location=location.top, color=color.red if waeSell else color.orange)
    plotchar(inShort, 'inShort', '', location=location.top, color=color.red if inShort else color.orange)
    plotchar(exitShort, 'Exit Short', '', location=location.top, color=color.red if exitShort else color.orange)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
