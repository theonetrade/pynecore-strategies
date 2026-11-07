"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, bar_index, barcolor, close, color, display, fill, high, input,
    label, location, low, math, na, nz, open, plot, plotarrow, plotshape, script, shape, size,
    strategy, string, ta, time, timestamp, xloc, yloc
)
from pynecore.types import NA, Persistent, Series


@script.strategy('SSL Exit Arrow Strategy', overlay=True, initial_capital=5000, default_qty_value=10, default_qty_type=strategy.percent_of_equity, commission_type='percent', commission_value=0.04, max_labels_count=500, calc_on_every_tick=True, pyramiding=10, margin_long=0, margin_short=0, close_by_id=True)
def main(
    show_Baseline=input.bool(title='Show Baseline', defval=True, group='SSL Hybrid Indicator Settings'),
    show_SSL1=input.bool(title='Show SSL1', defval=True, group='SSL Hybrid Indicator Settings'),
    show_atr=input.bool(title='Show ATR bands', defval=False, group='SSL Hybrid Indicator Settings'),
    atrlen=input.int(14, 'ATR Period', group='SSL Hybrid Indicator Settings'),
    mult=input.float(1, 'ATR Multi', step=0.1, group='SSL Hybrid Indicator Settings'),
    smoothing=input.string(title='ATR Smoothing', defval='WMA', options=('RMA', 'SMA', 'EMA', 'WMA'), group='SSL Hybrid Indicator Settings'),
    maType=input.string(title='SSL1 / Baseline Type', defval='HMA', options=('SMA', 'EMA', 'DEMA', 'TEMA', 'LSMA', 'WMA', 'MF', 'VAMA', 'TMA', 'HMA', 'JMA', 'Kijun v2', 'EDSMA', 'McGinley'), group='SSL Hybrid Indicator Settings'),
    len=input.int(title='SSL1 / Baseline Length', defval=60, group='SSL Hybrid Indicator Settings'),
    SSL2Type=input.string(title='SSL2 / Continuation Type', defval='JMA', options=('SMA', 'EMA', 'DEMA', 'TEMA', 'WMA', 'MF', 'VAMA', 'TMA', 'HMA', 'JMA', 'McGinley'), group='SSL Hybrid Indicator Settings'),
    len2=input.int(title='SSL 2 Length', defval=5, group='SSL Hybrid Indicator Settings'),
    SSL3Type=input.string(title='EXIT Type', defval='HMA', options=('DEMA', 'TEMA', 'LSMA', 'VAMA', 'TMA', 'HMA', 'JMA', 'Kijun v2', 'McGinley', 'MF'), group='SSL Hybrid Indicator Settings'),
    len3=input.int(title='EXIT Length', defval=15, group='SSL Hybrid Indicator Settings'),
    src: Series[float] = input.source(title='Source', defval=close, group='SSL Hybrid Indicator Settings'),
    kidiv=input.int(defval=1, maxval=4, title='Kijun MOD Divider', group='SSL Hybrid Indicator Settings'),
    jurik_phase=input.int(title='* Jurik (JMA) Only - Phase', defval=3, group='SSL Hybrid Indicator Settings'),
    jurik_power=input.int(title='* Jurik (JMA) Only - Power', defval=1, group='SSL Hybrid Indicator Settings'),
    volatility_lookback=input.int(10, title='* Volatility Adjusted (VAMA) Only - Volatility lookback length', group='SSL Hybrid Indicator Settings'),
    beta=input.float(0.8, minval=0, maxval=1, step=0.1, title='Modular Filter, General Filter Only - Beta', group='SSL Hybrid Indicator Settings'),
    feedback=input.bool(False, title='Modular Filter Only - Feedback', group='SSL Hybrid Indicator Settings'),
    z=input.float(0.5, title='Modular Filter Only - Feedback Weighting', step=0.1, minval=0, maxval=1, group='SSL Hybrid Indicator Settings'),
    ssfLength=input.int(title='EDSMA - Super Smoother Filter Length', minval=1, defval=20, group='SSL Hybrid Indicator Settings'),
    ssfPoles=input.int(title='EDSMA - Super Smoother Filter Poles', defval=2, options=(2, 3), group='SSL Hybrid Indicator Settings'),
    useTrueRange=input.bool(True, group='SSL Hybrid Indicator Settings'),
    multy=input.float(0.2, step=0.05, title='Base Channel Multiplier', group='SSL Hybrid Indicator Settings'),
    show_color_bar=input.bool(title='Color Bars', defval=True, group='SSL Hybrid Indicator Settings'),
    atr_crit=input.float(0.9, step=0.1, title='Continuation ATR Criteria', group='SSL Hybrid Indicator Settings'),
    RSI_Period=input(6, title='RSI Length'),
    SF=input(5, title='RSI Smoothing'),
    QQE=input(3, title='Fast QQE Factor'),
    ThreshHold=input(3, title='Thresh-hold'),
    rsi_src: Series[float] = input(close, title='RSI Source'),
    length=input.int(50, minval=1, title='Bollinger Length'),
    bb_mult=input.float(0.35, minval=0.001, maxval=5, step=0.1, title='BB Multiplier'),
    RSI_Period2=input(6, title='RSI Length'),
    SF2=input(5, title='RSI Smoothing'),
    QQE2=input(1.61, title='Fast QQE2 Factor'),
    ThreshHold2=input(3, title='Thresh-hold'),
    src2: Series[float] = input(close, title='RSI Source'),
    atr_length=input.int(title='ATR Length', defval=14, inline='1', group='Strategy Back Test Settings'),
    from_date=input.time(title='From', defval=timestamp('01 Aug 2021 00:00 +0100'), inline='1', group='Date Range'),
    to_date=input.time(title='To', defval=timestamp('01 Sep 2100 00:00 +0100'), inline='1', group='Date Range'),
    use_ssl_filter=input.bool(title='SSL Flip as Filter', defval=False, inline='1', group='Entry Settings'),
    use_qqe_filter=input.bool(title='QQE MOD as Filter (Please add QQE MOD indicator to your chart separately)', defval=False, inline='2', group='Entry Settings'),
    dca1_atr_multiplier=input.float(title='DCA1 ATR Multiplier', defval=0.1, step=0.1, inline='3', group='Entry Settings'),
    dca1_exit_percentage=input.int(title='DCA1 Exit Percentage', defval=20, step=1, maxval=100, inline='3', group='Entry Settings'),
    dca2_atr_multiplier=input.float(title='DCA2 ATR Multiplier', defval=0.3, step=0.1, inline='4', group='Entry Settings'),
    dca2_exit_percentage=input.int(title='DCA2 Exit Percentage', defval=40, step=1, maxval=100, inline='4', group='Entry Settings'),
    dca3_atr_multiplier=input.float(title='DCA3 ATR Multiplier', defval=0.7, step=0.1, inline='5', group='Entry Settings'),
    dca3_exit_percentage=input.int(title='DCA3 Exit Percentage', defval=40, step=1, maxval=100, inline='5', group='Entry Settings'),
    sl_atr_multiplier=input.float(title='SL ATR Multiplier', defval=1.8, step=0.1, inline='2', group='Exit Settings')
):
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
            upper__0000004f__ = beta * b + (1 - beta) * c
            lower__0000004f__ = beta * c + (1 - beta) * b
            ts = os * upper__0000004f__ + (1 - os) * lower__0000004f__
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
            dev__00000064__ = src - mid
            vol_up = ta.highest(dev__00000064__, volatility_lookback)
            vol_down = ta.lowest(dev__00000064__, volatility_lookback)
            result = mid + math.avg(vol_up, vol_down)
        if type == 'HMA':
            result = ta.wma(2 * ta.wma(src, len / 2) - ta.wma(src, len), math.round(math.sqrt(len)))
        if type == 'JMA':
            phaseRatio = 0.5 if jurik_phase < -100 else 2.5 if jurik_phase > 100 else jurik_phase / 100 + 1.5
            beta__00000078__ = 0.45 * (len - 1) / (0.45 * (len - 1) + 2)
            alpha = math.pow(beta__00000078__, jurik_power)
            jma: Series[float] = 0.0
            e0: Series[float] = 0.0
            e0 = (1 - alpha) * src + alpha * nz(e0[1])
            e1: Series[float] = 0.0
            e1 = (src - e0) * (1 - beta__00000078__) + beta__00000078__ * nz(e1[1])
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
            ema = ta.ema(src, len)
            mg = ema if na(mg[1]) else mg[1] + (src - mg[1]) / (len * math.pow(src / mg[1], 4))
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
    candlesize_violation = atr_violation and InRange
    plotshape(candlesize_violation, color=color.new(color.white, transp=0), size=size.tiny, style=shape.diamond, location=location.top, title='Candle Size > 1xATR')
    Hlv: Series = NA(int)
    Hlv = 1 if close > emaHigh else -1 if close < emaLow else Hlv[1]
    sslDown = emaHigh if Hlv < 0 else emaLow
    Hlv2: Series = NA(int)
    Hlv2 = 1 if close > maHigh else -1 if close < maLow else Hlv2[1]
    sslDown2 = maHigh if Hlv2 < 0 else maLow
    Hlv3: Series = NA(int)
    Hlv3 = 1 if close > ExitHigh else -1 if close < ExitLow else Hlv3[1]
    sslExit = ExitHigh if Hlv3 < 0 else ExitLow
    base_cross_Long = ta.crossover(close, sslExit)
    base_cross_Short = ta.crossover(sslExit, close)
    codiff = 1 if base_cross_Long else -1 if base_cross_Short else na
    color_bar = color.new('#00C3FF') if close > upperk else color.new('#FF0062') if close < lowerk else color.gray
    color_ssl1 = color.new('#00C3FF') if close > sslDown else color.new('#FF0062') if close < sslDown else na
    plotarrow(codiff, colorup=color.rgb(0, 195, 255, transp=0), colordown=color.rgb(255, 0, 98, transp=0), title='Exit Arrows', maxheight=20, offset=0)
    p1 = plot(BBMC if show_Baseline else na, color=color.new(color_bar, transp=0), linewidth=4, title='MA Baseline')
    DownPlot = plot(sslDown if show_SSL1 else na, title='SSL1', linewidth=3, color=color.new(color_ssl1, transp=10))
    barcolor(color_bar if show_color_bar else na)
    up_channel = plot(upperk if show_Baseline else na, color=color_bar, title='Baseline Upper Channel')
    low_channel = plot(lowerk if show_Baseline else na, color=color_bar, title='Basiline Lower Channel')
    fill(up_channel, low_channel, color=color.new(color_bar, transp=90))
    upper_half = atr_slen * atr_crit + close
    lower_half = close - atr_slen * atr_crit
    buy_inatr = lower_half < sslDown2
    sell_inatr = upper_half > sslDown2
    sell_cont = close < BBMC and close < sslDown2
    buy_cont = close > BBMC and close > sslDown2
    sell_atr = sell_inatr and sell_cont
    buy_atr = buy_inatr and buy_cont
    atr_fill = color.green if buy_atr else color.purple if sell_atr else color.white
    LongPlot = plot(sslDown2, title='SSL2', linewidth=2, color=color.new(atr_fill, transp=0), style=plot.style_circles, display=display.none)
    u = plot(upper_band if show_atr else na, '+ATR', color=color.new(color.white, transp=80), display=display.none)
    l = plot(lower_band if show_atr else na, '-ATR', color=color.new(color.white, transp=80), display=display.none)
    Wilders_Period = RSI_Period * 2 - 1
    Rsi = ta.rsi(rsi_src, RSI_Period)
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
    dev = bb_mult * ta.stdev(FastAtrRsiTL - 50, length)
    upper = basis + dev
    lower = basis - dev
    rsi_ma_color_bar = color.new('#00C3FF') if RsiMa - 50 > upper else color.new('#FF0062') if RsiMa - 50 < lower else color.gray
    QQEzlong: Series[int] = 0
    QQEzlong = nz(QQEzlong[1])
    QQEzshort: Series[int] = 0
    QQEzshort = nz(QQEzshort[1])
    QQEzlong = QQEzlong + 1 if RSIndex >= 50 else 0
    QQEzshort = QQEzshort + 1 if RSIndex < 50 else 0
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
    Greenbar1 = RsiMa2 - 50 > ThreshHold2
    Greenbar2 = RsiMa - 50 > upper
    Redbar1 = RsiMa2 - 50 < 0 - ThreshHold2
    Redbar2 = RsiMa - 50 < lower
    qqe_line = FastAtrRsi2TL - 50
    qqe_blue_bar = Greenbar1 and Greenbar2 == cast_bool(1)
    qqe_red_bar = Redbar1 and Redbar2 == cast_bool(1)
    atr = ta.atr(atr_length)
    in_date = time >= from_date and time <= to_date
    long_sl: Persistent = NA(float)
    long_dca1: Persistent = NA(float)
    long_dca2: Persistent = NA(float)
    long_dca3: Persistent = NA(float)
    short_sl: Persistent = NA(float)
    short_dca1: Persistent = NA(float)
    short_dca2: Persistent = NA(float)
    short_dca3: Persistent = NA(float)
    is_open_long = strategy.position_size > 0
    is_open_short = strategy.position_size < 0
    in_ssl_long: Persistent[bool] = False
    in_ssl_short: Persistent[bool] = False
    ssl_long_entry: Persistent[bool] = False
    ssl_short_entry: Persistent[bool] = False
    ssl_long_exit: Persistent[bool] = False
    ssl_short_exit: Persistent[bool] = False
    did_prev_bar_ssl_flip: Persistent[bool] = False
    ssl_long = close > sslDown if use_ssl_filter else True
    ssl_short = close < sslDown if use_ssl_filter else True
    qqe_long = qqe_blue_bar and qqe_line > 0 if use_qqe_filter else True
    qqe_short = qqe_red_bar and qqe_line < 0 if use_qqe_filter else True
    ssl_long_entry = ssl_long and qqe_long and (codiff == 1)
    ssl_short_entry = ssl_short and qqe_short and (codiff == -1)
    ssl_long_exit = codiff == -1
    ssl_short_exit = codiff == 1
    remaining_percent: int = 100
    total_tokens: Persistent = strategy.equity * 0.1 / close
    dca1_percent = dca1_exit_percentage if dca1_exit_percentage <= remaining_percent else remaining_percent
    remaining_percent = remaining_percent - dca1_percent
    entry_1 = total_tokens * (dca1_percent / 100)
    dca2_percent = dca2_exit_percentage if dca2_exit_percentage <= remaining_percent else remaining_percent
    remaining_percent = remaining_percent - dca2_percent
    entry_2 = total_tokens * (dca2_percent / 100)
    dca3_percent = dca3_exit_percentage if dca3_exit_percentage <= remaining_percent else remaining_percent
    remaining_percent = remaining_percent - dca3_percent
    entry_3 = total_tokens * (dca3_percent / 100)
    if did_prev_bar_ssl_flip:
        did_prev_bar_ssl_flip = False
        position_value = math.abs(strategy.position_size * close)
        if in_ssl_long:
            label.new(x=bar_index, y=close, xloc=xloc.bar_index, yloc=yloc.abovebar, text=string.tostring(position_value), style=label.style_label_down, size=size.tiny)
        else:
            label.new(x=bar_index, y=close, xloc=xloc.bar_index, yloc=yloc.belowbar, text=string.tostring(position_value), style=label.style_label_up, size=size.tiny)
    if ssl_long_exit:
        strategy.cancel('LongEntry1')
        strategy.cancel('LongEntry2')
        strategy.cancel('LongEntry3')
        strategy.close(id='LongEntry1', comment='Close Long1')
        strategy.close(id='LongEntry2', comment='Close Long2')
        strategy.close(id='LongEntry3', comment='Close Long3')
        in_ssl_long = False
        in_ssl_short = False
    if ssl_short_exit:
        strategy.cancel('ShortEntry1')
        strategy.cancel('ShortEntry2')
        strategy.cancel('ShortEntry3')
        strategy.close(id='ShortEntry1', comment='Close Short1')
        strategy.close(id='ShortEntry2', comment='Close Short2')
        strategy.close(id='ShortEntry3', comment='Close Short3')
        in_ssl_long = False
        in_ssl_short = False
    if ssl_long_entry and in_date and (not in_ssl_long):
        strategy.cancel('LongEntry1')
        strategy.cancel('LongEntry2')
        strategy.cancel('LongEntry3')
        strategy.cancel('ShortEntry1')
        strategy.cancel('ShortEntry2')
        strategy.cancel('ShortEntry3')
        if in_ssl_short:
            strategy.close(id='ShortEntry1', comment='Close Short1')
            strategy.close(id='ShortEntry2', comment='Close Short2')
            strategy.close(id='ShortEntry3', comment='Close Short3')
        in_ssl_long = True
        in_ssl_short = False
        did_prev_bar_ssl_flip = True
        long_sl = close - atr * sl_atr_multiplier
        long_dca1 = close - atr * dca1_atr_multiplier
        long_dca2 = close - atr * dca2_atr_multiplier
        long_dca3 = close - atr * dca3_atr_multiplier
        strategy.entry('LongEntry1', strategy.long, limit=long_dca1)
        strategy.entry('LongEntry2', strategy.long, limit=long_dca2)
        strategy.entry('LongEntry3', strategy.long, limit=long_dca3)
        strategy.exit('LongExit1', 'LongEntry1', stop=long_sl)
        strategy.exit('LongExit2', 'LongEntry2', stop=long_sl)
        strategy.exit('LongExit3', 'LongEntry3', stop=long_sl)
        alert(message='SSL Exit Arrow Strat LONG', freq=alert.freq_once_per_bar_close)
    if ssl_short_entry and in_date and (not in_ssl_short):
        strategy.cancel('LongEntry1')
        strategy.cancel('LongEntry2')
        strategy.cancel('LongEntry3')
        strategy.cancel('ShortEntry1')
        strategy.cancel('ShortEntry2')
        strategy.cancel('ShortEntry3')
        if in_ssl_long:
            strategy.close(id='LongEntry1', comment='Close Long1')
            strategy.close(id='LongEntry2', comment='Close Long2')
            strategy.close(id='LongEntry3', comment='Close Long3')
        in_ssl_short = True
        in_ssl_long = False
        did_prev_bar_ssl_flip = True
        short_sl = close + atr * sl_atr_multiplier
        short_dca1 = close + atr * dca1_atr_multiplier
        short_dca2 = close + atr * dca2_atr_multiplier
        short_dca3 = close + atr * dca3_atr_multiplier
        strategy.entry('ShortEntry1', strategy.short, limit=short_dca1)
        strategy.entry('ShortEntry2', strategy.short, limit=short_dca2)
        strategy.entry('ShortEntry3', strategy.short, limit=short_dca3)
        strategy.exit('ShortExit1', 'ShortEntry1', stop=short_sl)
        strategy.exit('ShortExit2', 'ShortEntry2', stop=short_sl)
        strategy.exit('ShortExit3', 'ShortEntry3', stop=short_sl)
        alert(message='SSL Exit Arrow Strat SHORT', freq=alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
