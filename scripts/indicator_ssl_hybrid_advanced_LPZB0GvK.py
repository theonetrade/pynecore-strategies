"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, barmerge, barstate, bgcolor,
    close, color, extend, fill, high, hlc3, input, label, line, location, low, math, na, nz, open,
    plot, plotarrow, plotshape, position, request, script, shape, size, string, syminfo, ta, table
)
from pynecore.types import Label, Line, NA, Persistent, Series


@script.indicator('SSL HYBRID ADVANCED', overlay=True)
def main(
    sslsignals=input.string(title='Buy Sell Signals', defval='SSL-HYBRID', options=('SSL-HYBRID', 'SSL+QQE+WAE', 'SSL-HYBRID+SuperTrend'), group='Settings: Signals', inline='Filter'),
    strend=input.string(title='Filter Buy Sell Signals', defval='NO-FILTER', options=('NO-FILTER', 'SUPERTREND', 'HULL'), group='Settings: Signals', inline='Filter'),
    squeezesignalfilter=input(False, title='Remove Alerts & Signals at BB-Squeeze', group='Settings: Signals', inline='Filter'),
    adxsignalfilter=input(False, title='Remove Alerts & Signals at LOW ADX/SIDEWAYS', group='Settings: Signals', inline='Filter'),
    strengthtreshold=input(8, 'Table Alert Strength', group='Strategy: Table Strength', inline='table'),
    showtable=input.bool(True, 'Show SSL Table', group='Strategy: Table Strength', inline='table'),
    merget=input.bool(True, 'Merge SSL Table', group='Strategy: Table Strength', inline='table'),
    showtable2=input.bool(True, 'Show Strength Table', group='Strategy: Table Strength', inline='table'),
    show_ema200=input.bool(False, title='show Ema200 with ADX', group='Settings: Indicators'),
    showbbsqueeze=input(True, title='Show Bollinger Squeeze', group='Settings: Indicators'),
    showadxbg=input.bool(True, title='show Low ADX as Background', group='Candles'),
    showadxcandles=input.bool(True, title='show Low ADX Candles', group='Candles'),
    showbb=input.string('BB', title='Show Bollinger/Keltner Band', options=('--', 'BB', 'Keltner'), group='Settings: Indicators'),
    showmtfma=input.bool(False, title='Show MTF EMA', group='Settings: Indicators'),
    showqqedot=input.bool(True, title='Show QQE MOD Support', group='Settings: Indicators'),
    showbg=input.bool(True, title='QQE Signal Background', group='Settings: Indicators'),
    qqeline=input(title='QQE Line', defval=False, group='Settings: Indicators'),
    showpp=input(False, title='Show Pivot Points', group='Settings: Indicators'),
    showsr=input(False, title='Show Support Resistance', group='Settings: Indicators'),
    show_Baseline=input(title='Show SSL Baseline', defval=True, group='SSL'),
    show_SSL1=input(title='Show SSL1 Support', defval=False, group='SSL'),
    showssl2=input(title='Show SSL2 Support', defval=False, group='SSL'),
    show_atr=input(title='Show ATR bands', defval=False, group='Settings: ATR'),
    atrlen=input(14, 'ATR Period', group='Settings: ATR'),
    mult=input.float(1.5, 'ATR Multi', step=0.1, group='Settings: ATR'),
    smoothing=input.string(title='ATR Smoothing', defval='WMA', options=('RMA', 'SMA', 'EMA', 'WMA'), group='Settings: ATR'),
    maType=input.string(title='SSL1 / Baseline Type', defval='HMA', options=('ZLSMA', 'SMA', 'EMA', 'DEMA', 'TEMA', 'LSMA', 'WMA', 'MF', 'VAMA', 'TMA', 'HMA', 'JMA', 'Kijun v2', 'EDSMA', 'McGinley'), group='Settings: SSL'),
    len=input(title='SSL1 / Baseline Length', defval=55, group='Settings: SSL'),
    SSL2Type=input.string(title='SSL2 / Continuation Type', defval='JMA', options=('SMA', 'EMA', 'DEMA', 'TEMA', 'WMA', 'MF', 'VAMA', 'TMA', 'HMA', 'JMA', 'McGinley'), group='Settings: SSL'),
    len2=input(title='SSL 2 Length', defval=5, group='Settings: SSL'),
    SSL3Type=input.string(title='EXIT Type', defval='HMA', options=('DEMA', 'TEMA', 'LSMA', 'VAMA', 'TMA', 'HMA', 'JMA', 'Kijun v2', 'McGinley', 'MF'), group='Settings: SSL'),
    len3=input(title='EXIT Length', defval=15),
    src: Series[float] = input(title='Source', defval=close),
    kidiv=input.int(defval=1, maxval=4, title='Kijun MOD Divider', group='Settings: SSL'),
    jurik_phase=input(title='* Jurik (JMA) Only - Phase', defval=3, group='Settings: SSL'),
    jurik_power=input(title='* Jurik (JMA) Only - Power', defval=1, group='Settings: SSL'),
    volatility_lookback=input(10, title='* Volatility Adjusted (VAMA) Only - Volatility lookback length', group='Settings: SSL'),
    beta=input.float(0.8, minval=0, maxval=1, step=0.1, title='Modular Filter, General Filter Only - Beta', group='Settings: SSL'),
    feedback=input(False, title='Modular Filter Only - Feedback', group='Settings: SSL'),
    z=input.float(0.5, title='Modular Filter Only - Feedback Weighting', step=0.1, minval=0, maxval=1, group='Settings: SSL'),
    ssfLength=input.int(title='EDSMA - Super Smoother Filter Length', minval=1, defval=20, group='Settings: SSL'),
    ssfPoles=input.int(title='EDSMA - Super Smoother Filter Poles', defval=2, options=(2, 3), group='Settings: SSL'),
    useTrueRange=input(True),
    multy=input.float(0.2, step=0.05, title='Base Channel Multiplier', group='Settings: SSL'),
    show_color_bar=input(title='Color Bars', defval=True, group='Candles'),
    atr_crit=input.float(0.9, step=0.1, title='Continuation ATR Criteria', group='Settings: SSL'),
    RSI_Period=input(6, title='RSI Length', group='Settings:QQE-MOD'),
    SF=input(5, title='RSI Smoothing', group='Settings:QQE-MOD'),
    QQE=input.float(3, title='Fast QQE Factor', group='Settings:QQE-MOD', step=0.1),
    ThreshHold=input(3, title='Thresh-hold', group='Settings:QQE-MOD'),
    qqsrc: Series[float] = input(close, title='RSI Source', group='Settings:QQE-MOD'),
    length=input.int(50, minval=1, title='Bollinger Length', group='Settings:QQE-MOD'),
    qqmult=input.float(0.35, minval=0.001, maxval=5, step=0.1, title='BB Multiplier', group='Settings:QQE-MOD'),
    RSI_Period2=input(6, title='RSI Length', group='Settings:QQE-MOD'),
    SF2=input(5, title='RSI Smoothing', group='Settings:QQE-MOD'),
    QQE2=input.float(1.61, title='Fast QQE2 Factor', group='Settings:QQE-MOD', step=0.1),
    ThreshHold2=input(3, title='Threshold', group='Settings:QQE-MOD'),
    src2: Series[float] = input(close, title='RSI Source', group='Settings:QQE-MOD'),
    sensitivity=input.int(150, title='Sensitivity', group='Indicators: Waddah Attar Explosion'),
    fastLength=input.int(20, title='FastEMA Length', group='Indicators: Waddah Attar Explosion'),
    slowLength=input.int(40, title='SlowEMA Length', group='Indicators: Waddah Attar Explosion'),
    channelLength=input.int(20, title='BB Channel Length', group='Indicators: Waddah Attar Explosion'),
    waeMult=input.float(2.0, title='BB Stdev Multiplier', group='Indicators: Waddah Attar Explosion'),
    adxl=input(14, title='ADX/DMI length', group='Settings: ADX'),
    adxs=input(14, title='ADX/DMI smooth length', group='Settings: ADX'),
    adxtreshold=input.int(20, 'ADX Treshold', group='Settings: ADX'),
    showhulltrend=input.bool(False, 'Show HULL MTF', group='Settings: Filters', inline='HULL'),
    showtrend=input.bool(False, 'Show Supertrend', group='Settings: Filters', inline='Supertrend'),
    showstc=input.bool(True, title='SuperTrend Color/Hull Color', group='Settings: Filters', inline='Supertrend'),
    mtf4=input.timeframe(title='HULL TIME FRAME', defval='', group='Settings: Filters', inline='HULL'),
    stf4=input.timeframe(title='SUPER TREND TIME FRAME', defval='', group='Settings: Filters', inline='Supertrend'),
    ma_length4=input(110, title='Hull TREND Length\n[Scalping:55,Floating S/R:100-300,]', group='Settings: Filters', inline='HULL'),
    __input_72__=input.float(3, title='Supertrend ATR Multiplier', step=0.1, group='Settings: Filters', inline='Supertrend'),
    __input_73__=input.int(10, title='Supertrend Length', group='Settings: Filters', inline='Supertrend'),
    __input_74__=input.int(5, title='FAST MACD', group='Settings: MACD'),
    __input_75__=input.int(50, title='SLOW MACD', group='Settings: MACD'),
    __input_76__=input.int(30, title='Signal', group='Settings: MACD'),
    matype=input.string('SMA', title='Bollinger MA type', options=('EMA', 'HMA', 'SMA')),
    kLength=input(20, title='Keltner Length'),
    kN=input(2, title='Keltner Deviation'),
    bbLength=input(20, title='Bollinger Length'),
    bbN=input(2, title='Bollinger Deviation'),
    mtf1=input.timeframe(title='EMA MTF1', defval='', group='Settings: EMA'),
    mtf2=input.timeframe(title='EMA MTF2', defval='', group='Settings: EMA'),
    ma_length1=input(20, title='EMA Period-1', group='Settings: EMA'),
    ma_length2=input(50, title='EMA Period-2', group='Settings: EMA'),
    __input_86__=input.int(7, minval=1, title='RSI Length', group='RSI'),
    __input_87__=input.int(18, minval=1, title='RSI SMA Length', group='RSI'),
    __input_88__=input.int(40, minval=1, title='CCI Length', group='CCI'),
    __input_89__: Series[float] = input(hlc3, title='CCI Source', group='CCI'),
    __input_90__=input(80, title='Stochastic OverBought Level', group='stochastic'),
    __input_91__=input(20, title='Stochastic OverBought Level', group='stochastic'),
    __input_92__=input.int(14, minval=1, title='Stochastic Length', group='stochastic'),
    __input_93__=input.int(3, minval=1, title='Stochastic Smooth Length K', group='stochastic'),
    __input_94__=input.int(3, minval=1, title='Stochastic Deviation Length D', group='stochastic'),
    start=input.float(title='PSAR Start', step=0.001, defval=0.02, group='PSAR'),
    increment=input.float(title='PSAR Increment', step=0.001, defval=0.02, group='PSAR'),
    maximum=input.float(title='PSAR Maximum', step=0.01, defval=0.2, group='PSAR'),
    prd=input.int(defval=10, title='Pivot Period', minval=4, maxval=30, group='S/R Settings'),
    ppsrc=input.string(defval='High/Low', title='Source', options=('High/Low', 'Close/Open'), group='S/R Settings'),
    maxnumpp=input.int(defval=20, title=' Maximum Number of Pivot', minval=5, maxval=100, group='S/R Settings'),
    ChannelW=input.int(defval=10, title='Maximum Channel Width %', minval=1, group='S/R Settings'),
    maxnumsr=input.int(defval=5, title=' Maximum Number of S/R', minval=1, maxval=10, group='S/R Settings'),
    min_strength=input.int(defval=2, title=' Minimum Strength', minval=1, maxval=10, group='S/R Settings'),
    labelloc=input.int(defval=20, title='Label Location', group='S/R Settings', tooltip='Positive numbers reference future bars, negative numbers reference histical bars'),
    linestyle=input.string(defval='Solid', title='Line Style', options=('Solid', 'Dotted', 'Dashed'), group='S/R Settings'),
    linewidth=input.int(defval=1, title='Line Width', minval=1, maxval=4, group='S/R Settings'),
    resistancecolor=input.color(defval=color.new(color.red, 0), title='Resistance Color', group='S/R Settings'),
    supportcolor=input.color(defval=color.new(color.lime, 0), title='Support Color', group='S/R Settings')
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
            b__00000063__: Series[float] = 0.0
            c: Series[float] = 0.0
            os: Series[float] = 0.0

            alpha = 2 / (len + 1)
            a__00000063__ = z * src + (1 - z) * nz(ts[1], src) if feedback else src

            b__00000063__ = a__00000063__ if a__00000063__ > alpha * a__00000063__ + (1 - alpha) * nz(b__00000063__[1], a__00000063__) else alpha * a__00000063__ + (1 - alpha) * nz(b__00000063__[1], a__00000063__)
            c = a__00000063__ if a__00000063__ < alpha * a__00000063__ + (1 - alpha) * nz(c[1], a__00000063__) else alpha * a__00000063__ + (1 - alpha) * nz(c[1], a__00000063__)
            os = 1 if a__00000063__ == b__00000063__ else 0 if a__00000063__ == c else os[1]

            upper__00000063__ = beta * b__00000063__ + (1 - beta) * c
            lower__00000063__ = beta * c + (1 - beta) * b__00000063__
            ts = os * upper__00000063__ + (1 - os) * lower__00000063__
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
            dev__00000078__ = src - mid
            vol_up = ta.highest(dev__00000078__, volatility_lookback)
            vol_down = ta.lowest(dev__00000078__, volatility_lookback)
            result = mid + math.avg(vol_up, vol_down)
        if type == 'HMA':
            result = ta.wma(2 * ta.wma(src, len / 2) - ta.wma(src, len), math.round(math.sqrt(len)))
        if type == 'JMA':
            phaseRatio = 0.5 if jurik_phase < -100 else 2.5 if jurik_phase > 100 else jurik_phase / 100 + 1.5
            beta__0000008c__ = 0.45 * (len - 1) / (0.45 * (len - 1) + 2)
            alpha = math.pow(beta__0000008c__, jurik_power)
            jma: Series[float] = 0.0
            e0: Series[float] = 0.0
            e0 = (1 - alpha) * src + alpha * nz(e0[1])
            e1__0000008c__: Series[float] = 0.0
            e1__0000008c__ = (src - e0) * (1 - beta__0000008c__) + beta__0000008c__ * nz(e1__0000008c__[1])
            e2: Series[float] = 0.0
            e2 = (e0 + phaseRatio * e1__0000008c__ - nz(jma[1])) * math.pow(1 - alpha, 2) + math.pow(alpha, 2) * nz(e2[1])
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
        if type == 'ZLSMA':
            lsma = ta.linreg(src, len, 0)
            lsma2 = ta.linreg(lsma, len, 0)
            eq = lsma - lsma2
            result = lsma + eq
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
    color_bar = color.new(color.new('#00C3FF'), 0) if close > upperk else color.new(color.new('#FF0062'), 0) if close < lowerk else color.new(color.gray, 0)
    color_ssl1 = color.new(color.new('#00C3FF'), 0) if close > sslDown else color.new(color.new('#FF0062'), 0) if close < sslDown else na
    color_bar2 = color.new(color.new('#0000FF'), 0) if close > upperk else color.new(color.new('#FF0000'), 0) if close < lowerk else color.new(color.gray, 0)

    plotarrow(codiff, colorup=color.new(color.new('#00C3FF'), 20), colordown=color.new(color.new('#FF0062'), 20), title='Exit Arrows', maxheight=20, offset=0)

    DownPlot = plot(sslDown if show_SSL1 else na, title='SSL1', linewidth=3, color=color_ssl1)
    upper_half = atr_slen * atr_crit + close
    lower_half = close - atr_slen * atr_crit
    buy_inatr = lower_half < sslDown2
    sell_inatr = upper_half > sslDown2
    sell_cont = close < BBMC and close < sslDown2
    buy_cont = close > BBMC and close > sslDown2
    sell_atr = sell_inatr and sell_cont
    buy_atr = buy_inatr and buy_cont
    atr_fill = color.new(color.green, 0) if buy_atr else color.new(color.purple, 0) if sell_atr else color.new(color.white, 0)
    LongPlot = plot(sslDown2 if showssl2 else na, title='SSL2', linewidth=2, color=atr_fill, style=plot.style_circles)
    u = plot(upper_band if show_atr else na, '+ATR', color=color.new(color.rgb(0, 255, 0, 50), 80), linewidth=2)
    l = plot(lower_band if show_atr else na, '-ATR', color=color.new(color.rgb(255, 0, 0, 50), 80), linewidth=2)
    Wilders_Period = RSI_Period * 2 - 1
    Rsi = ta.rsi(qqsrc, RSI_Period)
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
    dev = qqmult * ta.stdev(FastAtrRsiTL - 50, length)
    upper = basis + dev
    lower = basis - dev
    qqcolor_bar = color.new(color.new('#00C3FF'), 0) if RsiMa - 50 > upper else color.new(color.new('#FF0062'), 0) if RsiMa - 50 < lower else color.new(color.gray, 0)

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
    hcolor2 = color.new(color.new('#161B25'), 0) if RsiMa2 - 50 > ThreshHold2 else color.new(color.new('#161B25'), 0) if RsiMa2 - 50 < 0 - ThreshHold2 else color.new(color.new('#161B25'), 0)

    Greenbar1 = RsiMa2 - 50 > ThreshHold2
    Greenbar2 = RsiMa - 50 > upper
    Redbar1 = RsiMa2 - 50 < 0 - ThreshHold2
    Redbar2 = RsiMa - 50 < lower

    qqcolr = color.new(color.new('#002734'), 0) if FastAtrRsiTL - 50 < RsiMa - 50 else color.new(color.new('#3A0016'), 0) if FastAtrRsiTL - 50 > RsiMa - 50 else na
    bgcolor(qqcolr if showbg else na, title='QQE Bg')

    qqecolor = color.new(color.new('#00C3FF'), 0) if Greenbar1 and Greenbar2 == cast_bool(1) and (RsiMa2 - 50 > ThreshHold2) else color.new(color.new('#FF0062'), 0) if Redbar1 and Redbar2 == cast_bool(1) and (RsiMa2 - 50 < 0 - ThreshHold2) else color.new(color.gray, 0)
    plot(ta.ema(close + (FastAtrRsi2TL - 50) / 10000, 5) if qqeline else na, title='QQE Line', color=qqecolor, linewidth=2)

    qqxcolor = color.new(color.green, 0) if FastAtrRsiTL - 50 < RsiMa - 50 else color.new(color.red, 0) if FastAtrRsiTL - 50 > RsiMa - 50 else na

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

    trendUp = t1 if t1 >= 0 else 0
    trendDown = -1 * t1 if t1 < 0 else 0

    waeBuy = trendUp > 0 and trendUp > e1
    waeSell = trendDown > 0 and trendDown > e1
    waecol = color.new(color.new('#00C3FF'), 0) if waeBuy else color.new(color.new('#FF0062'), 0) if waeSell else color.new(color.gray, 0)
    plus, minus, adx = request.security(syminfo.tickerid, '', ta.dmi(adxl, adxs))
    em200 = ta.ema(open, 200)
    adxem200color = color.new(color.lime, 0) if adx > adxtreshold and plus > minus else color.new(color.maroon, 0) if adx > adxtreshold and plus < minus else color.new(color.yellow, 0)
    plot(em200 if show_ema200 else na, 'EMA200', color=adxem200color, linewidth=math.max(1, 3))
    adxcross = color.new(color.blue, 0) if ta.crossover(plus, minus) else color.new(color.red, 0) if ta.crossunder(plus, minus) else na
    plotshape(em200 if ta.cross(plus, minus) else na, color=adxcross, size=size.tiny, location=location.absolute, style=shape.diamond, title='ADX Cross')

    ma4 = request.security(syminfo.tickerid, mtf4, ta.hma(close, ma_length4), barmerge.gaps_on)
    color4 = color.new(color.new('#00FF00'), 0) if open > ma4 else color.new(color.new('#FF0000'), 0) if open < ma4 else color.new(color.gray, 0)
    pl4 = plot(ma4 if showhulltrend else na, title='MTF HULL TREND', color=color4, linewidth=4, offset=0)

    supertrend, direction = request.security(syminfo.tickerid, stf4, ta.supertrend(__input_72__, __input_73__), barmerge.gaps_off)
    supertrendup = supertrend if direction < 0 else na
    supertrenddn = supertrend if direction > 0 else na
    stc = color.new(color.new('#00C3FF'), 50) if cast_bool(supertrendup) else color.new(color.new('#FF0062'), 50)
    trendcolor = stc if showstc else qqxcolor
    plot(supertrendup if showtrend else na, title='Supertrend Up', color=trendcolor, linewidth=4, style=plot.style_linebr)
    plot(supertrenddn if showtrend else na, title='Supertrend Down', color=trendcolor, linewidth=4, style=plot.style_linebr)

    macd, signal, hist = ta.macd(close, __input_74__, __input_75__, __input_76__)
    plotshape(close if ta.crossover(macd, signal) else na, title='MACD Crossover Buy', text='', location=location.belowbar, style=shape.xcross, size=size.tiny, color=color.new(color.new('#00FF00'), 20), textcolor=color.new(color.white, 0))
    plotshape(close if ta.crossunder(macd, signal) else na, title='MACD Crossover Sell', text='', location=location.abovebar, style=shape.xcross, size=size.tiny, color=color.new(color.new('#FF0000'), 0), textcolor=color.new(color.white, 0))
    color_bars = color.new(color.purple, 90) if showadxbg and adx < adxtreshold else na
    bgcolor(color_bars if adx < adxtreshold else na)

    kma = ta.ema(close, kLength) if matype == 'EMA' else ta.hma(close, kLength) if matype == 'HMA' else ta.sma(close, kLength)
    kUpper = kma + kN * ta.atr(kLength)
    kLower = kma - kN * ta.atr(kLength)

    bma = ta.ema(close, bbLength) if matype == 'EMA' else ta.hma(close, bbLength) if matype == 'HMA' else ta.sma(close, bbLength)
    bbUpper = bma + bbN * ta.stdev(close, bbLength)
    bbLower = bma - bbN * ta.stdev(close, bbLength)
    bbMiddle = ta.ema(close, bbLength) if matype == 'EMA' else ta.hma(close, bbLength) if matype == 'HMA' else ta.sma(close, bbLength)

    squeeze = bbUpper <= kUpper and bbLower >= kLower

    plot(bbUpper if showbb == 'BB' else kUpper if showbb == 'Keltner' else na, style=plot.style_linebr, color=color.new(color.purple, 0), title=' Upper Band')
    plot(bbLower if showbb == 'BB' else kLower if showbb == 'Keltner' else na, style=plot.style_linebr, color=color.new(color.purple, 0), title=' Lower Band')

    a = plot(bbUpper if squeeze and showbbsqueeze else na, style=plot.style_linebr, color=na if cast_bool(bar_index) else color.new(color.white, 0), title='Squeezed Upper Band')
    b = plot(bbLower if squeeze and showbbsqueeze else na, style=plot.style_linebr, color=na if cast_bool(bar_index) else color.new(color.white, 0), title='Squeezed Lower Band')
    fill(a, b, color=color.new(color.purple, 90), title='Bollinger Squeezed Area')
    ma1 = request.security(syminfo.tickerid, mtf1, ta.ema(close, ma_length1), barmerge.gaps_on)
    color1 = color.new(color.new('#00FF00'), 60) if open > ma1 else color.new(color.new('#00FF00'), 60) if open < ma1 else color.new(color.gray, 0)

    pl1 = plot(ma1 if showmtfma else bbMiddle if showbb == 'BB' else bbMiddle if showbb == 'Keltner' else na, title='MTF EMA-1', color=color1 if showmtfma and cast_bool(ma1) else color.purple, linewidth=1, offset=0)

    ma2 = request.security(syminfo.tickerid, mtf2, ta.ema(close, ma_length2), barmerge.gaps_on)
    color2 = color.new(color.new('#FF0000'), 60) if open > ma2 else color.new(color.new('#FF0000'), 60) if open < ma2 else color.new(color.gray, 0)

    pl2 = plot(ma2 if showmtfma else na, title='MTF EMA-2', color=color2, linewidth=1, offset=0)

    plotshape(close if ta.crossover(ma1, ma2) else na, title='EMA Crossover Buy', text='', location=location.belowbar, style=shape.xcross, size=size.tiny, color=color.new(color.new('#00FF00'), 20), textcolor=color.new(color.white, 0))
    plotshape(close if ta.crossunder(ma1, ma2) else na, title='EMA Crossover Sell', text='', location=location.abovebar, style=shape.xcross, size=size.tiny, color=color.new(color.new('#FF0000'), 50), textcolor=color.new(color.white, 0))

    def rsi():
        srce = close
        len = __input_86__
        srs = __input_87__
        up = ta.rma(math.max(ta.change(srce), 0), len)
        down = ta.rma(-math.min(ta.change(srce), 0), len)
        rsi__000001ad__ = 100 if down == 0 else 0 if up == 0 else 100 - 100 / (1 + up / down)

        mr = ta.ema(ta.ema(ta.ema(rsi__000001ad__, srs), srs), srs)
        rsiupdn = 1 if rsi__000001ad__ > mr else -1 if rsi__000001ad__ < mr else 0
        return (rsiupdn,)

    def cci():
        ccilength = __input_88__
        ccisrc = __input_89__
        ccima = ta.sma(ccisrc, ccilength)
        cci__000001b2__ = (ccisrc - ccima) / (0.015 * ta.dev(ccisrc, ccilength))
        ccibg = 1 if cci__000001b2__ > 100 else -1 if cci__000001b2__ < -100 else 0
        return (ccibg,)

    def sto():
        OverBought = __input_90__
        OverSold = __input_91__
        k = ta.sma(ta.stoch(close, high, low, __input_92__), __input_93__)
        d = ta.sma(k, __input_94__)
        co = ta.crossover(k, d)
        cu = ta.crossunder(k, d)
        sup = k > OverBought or (cu and k > OverBought)
        sdn = k < OverSold or (co and k < OverSold)
        stobg = 1 if sup else -1 if sdn else 2 if co else -2 if cu else 0
        return (stobg,)

    psar = ta.sar(start, increment, maximum)
    psarDir = 1 if psar < close else -1
    colorPSAR = color.new(color.new('#00C3FF'), 0) if psarDir == 1 else color.new(color.new('#FF0062'), 0)

    exitsig = color.new(color.new('#00C3FF'), 0) if close > upperk and close > BBMC else color.new(color.new('#FF0062'), 0) if close < lowerk and close < BBMC else color.new(color.gray, 0)
    qqedot = color.new(color.new('#00C3FF'), 0) if Greenbar1 and Greenbar2 and waeBuy else color.new(color.new('#FF0062'), 0) if Redbar1 and Redbar2 and waeSell else color.new(color.gray, 0)

    adxcol = color.new(color.new('#00C3FF'), 0) if adx > 20 and plus > minus else color.new(color.new('#FF0062'), 0) if adx > 20 and minus > plus else color.new(color.gray, 0)
    emacol = color.new(color.new('#00C3FF'), 0) if ta.crossover(ma1, ma2) or close > ma2 else color.new(color.new('#FF0062'), 0) if ta.crossunder(ma1, ma2) or close < ma2 else color.new(color.gray, 0)

    psarn = 1 if psarDir == 1 else -1
    exitsign = 1 if close > upperk and close > 1 else -1 if close < lowerk and close < BBMC else 0
    qqedotn = 1 if Greenbar1 and Greenbar2 and waeBuy else -1 if Redbar1 and Redbar2 and waeSell else 0
    adxcoln = 1 if adx > 20 and plus > minus else -1 if adx > 20 and minus > plus else 0
    emacoln = 1 if ta.crossover(ma1, ma2) or close > ma2 else -1 if ta.crossunder(ma1, ma2) or close < ma2 else 0
    waen = 1 if waeBuy else -1 if waeSell else 0
    stval = 1 if direction < 0 else -1 if direction > 0 else 0

    sto__global__, = sto()
    rs, = rsi()
    cc, = cci()
    stocol = color.new(color.new('#00C3FF'), 0) if sto__global__ > 0 else color.new(color.new('#FF0062'), 0) if sto__global__ < 0 else color.new(color.gray, 0)
    rsicol = color.new(color.new('#00C3FF'), 0) if rs > 0 else color.new(color.new('#FF0062'), 0) if rs < 0 else color.new(color.gray, 0)
    ccicol = color.new(color.new('#00C3FF'), 0) if cc > 0 else color.new(color.new('#FF0062'), 0) if cc < 0 else color.new(color.gray, 0)
    sttrend = color.new(color.new('#00C3FF'), 0) if direction < 0 else color.new(color.new('#FF0062'), 0) if direction > 0 else color.new(color.gray, 0)

    qqeGreenBar: Series = Greenbar1 and Greenbar2
    qqeRedBar: Series = Redbar1 and Redbar2
    qqeBuy = qqeGreenBar and (not qqeGreenBar[1])
    qqeSell = qqeRedBar and (not qqeRedBar[1])
    p1 = plot(BBMC if show_Baseline else na, color=color_bar, linewidth=4, title='MA Baseline')
    barcolor(color_bar if show_color_bar else color.new(color.yellow, 90) if show_color_bar and adx < adxtreshold and showadxcandles else na)
    plotshape(qqeGreenBar if showqqedot else False, color=color.new(color.new('#00FF00'), 20), title='QQE Up', style=shape.triangleup, size=size.auto, location=location.belowbar)
    plotshape(qqeRedBar if showqqedot else False, color=color.new(color.new('#FF0000'), 20), title='QQE Dn', style=shape.triangledown, size=size.auto, location=location.abovebar)

    sslBuy = close > upperk and close > BBMC
    sslSell = close < lowerk and close < BBMC

    stratsslupsig = waeBuy and qqeBuy and sslBuy
    stratssldnsig = waeSell and qqeSell and sslSell

    sslup = ta.crossover(close, sslExit)
    ssldn = ta.crossover(sslExit, close)

    strendup = direction < 0 and cast_bool(ta.change(direction))
    strenddn = direction > 0 and cast_bool(ta.change(direction))

    sslupst = ta.crossover(close, sslExit) or strendup
    ssldnst = ta.crossover(sslExit, close) or strenddn

    hmadirection = 1 if close > ma4 else -1 if close < ma4 else 0
    signalup = sslup if strend == 'NO-FILTER' and sslsignals == 'SSL-HYBRID' else stratsslupsig if strend == 'NO-FILTER' and sslsignals == 'SSL+QQE+WAE' else sslupst if strend == 'NO-FILTER' and sslsignals == 'SSL-HYBRID+SuperTrend' else sslup if strend == 'SUPERTREND' and direction < 0 and (sslsignals == 'SSL-HYBRID') else stratsslupsig if strend == 'SUPERTREND' and direction < 0 and (sslsignals == 'SSL+QQE+WAE') else sslupst if strend == 'SUPERTREND' and direction < 0 and (sslsignals == 'SSL-HYBRID+SuperTrend') else sslup if strend == 'HULL' and hmadirection > 0 and (sslsignals == 'SSL-HYBRID') else stratsslupsig if strend == 'HULL' and hmadirection > 0 and (sslsignals == 'SSL+QQE+WAE') else sslupst if strend == 'HULL' and hmadirection > 0 and (sslsignals == 'SSL-HYBRID+SuperTrend') else sslup
    signalup = sslup if squeezesignalfilter and squeeze else signalup
    signalup = sslup if adxsignalfilter and adx < adxtreshold else signalup

    signaldn = ssldn if strend == 'NO-FILTER' and sslsignals == 'SSL-HYBRID' else stratssldnsig if strend == 'NO-FILTER' and sslsignals == 'SSL+QQE+WAE' else ssldnst if strend == 'NO-FILTER' and sslsignals == 'SSL-HYBRID+SuperTrend' else ssldn if strend == 'SUPERTREND' and direction > 0 and (sslsignals == 'SSL-HYBRID') else stratssldnsig if strend == 'SUPERTREND' and direction > 0 and (sslsignals == 'SSL+QQE+WAE') else ssldnst if strend == 'SUPERTREND' and direction > 0 and (sslsignals == 'SSL-HYBRID+SuperTrend') else sslup if strend == 'HULL' and hmadirection < 0 and (sslsignals == 'SSL-HYBRID') else stratsslupsig if strend == 'HULL' and hmadirection < 0 and (sslsignals == 'SSL+QQE+WAE') else sslupst if strend == 'HULL' and hmadirection < 0 and (sslsignals == 'SSL-HYBRID+SuperTrend') else ssldn
    signaldn = ssldn if squeezesignalfilter and squeeze else signaldn
    signaldn = ssldn if adxsignalfilter and adx < adxtreshold else signaldn

    plotshape(signalup, title='SSL Buy', text='Buy', location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.new(color.new('#00C3FF'), 50), textcolor=color.new(color.white, 0))
    plotshape(signaldn, title='SSL Sell', text='Sell', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.new(color.new('#FF0062'), 50), textcolor=color.new(color.white, 0))

    ssltable: Persistent = table.new(position.top_right, 2, 15, border_width=3, bgcolor=color.new(color.black, 0), border_color=color.new(color.new('#333333'), 0))
    if barstate.islast:
        if showtable:
            table.cell(ssltable, 0, 0, text='Checklist', text_color=color.new(color.white, 0), text_size=size.normal)

            table.cell(ssltable, 0, 1, text='SSL/EMA Signal', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=exitsig if merget else color.new(color.gray, 0))
            table.cell(ssltable, 0, 2, text='HMA open', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=color_bar if merget else color.new(color.gray, 0))
            table.cell(ssltable, 0, 3, text='Candle Color', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=colorPSAR if merget else color.new(color.gray, 0))
            table.cell(ssltable, 0, 4, text='QQE Color', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=qqecolor if merget else color.new(color.gray, 0))
            table.cell(ssltable, 0, 5, text='QQE WAE Dot', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=qqedot if merget else color.new(color.gray, 0))
            table.cell(ssltable, 0, 6, text='Supertrend', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=sttrend if merget else color.new(color.gray, 0))
            table.cell(ssltable, 0, 7, text='ADX Color', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=adxcol if merget else color.new(color.gray, 0))
            table.cell(ssltable, 0, 8, text='WAE Color', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=waecol if merget else color.new(color.gray, 0))
            table.cell(ssltable, 0, 8, text='EMA Color', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=emacol if merget else color.new(color.gray, 0))
            table.cell(ssltable, 0, 9, text='STO Color', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=stocol if merget else color.new(color.gray, 0))
            table.cell(ssltable, 0, 10, text='RSI Color', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=rsicol if merget else color.new(color.gray, 0))
            table.cell(ssltable, 0, 11, text='CCI Color', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=ccicol if merget else color.new(color.gray, 0))

            if not merget:
                table.cell(ssltable, 1, 0, text='Up/Down', text_color=color.new(color.white, 0), text_size=size.normal)
                table.cell(ssltable, 1, 1, text='Up/Down', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=exitsig)
                table.cell(ssltable, 1, 2, text='Above/Below', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=color_bar)
                table.cell(ssltable, 1, 3, text='Blue/Pink', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=colorPSAR)
                table.cell(ssltable, 1, 4, text='Blue/Pink', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=qqecolor)
                table.cell(ssltable, 1, 5, text='Below/Above', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=qqedot)
                table.cell(ssltable, 1, 6, text='Above/Below', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=sttrend)
                table.cell(ssltable, 1, 7, text='Blue/Pink', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=adxcol)
                table.cell(ssltable, 1, 8, text='Blue/Pink', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=waecol)
                table.cell(ssltable, 1, 9, text='Blue/Pink', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=stocol)
                table.cell(ssltable, 1, 10, text='Green/Red', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=rsicol)
                table.cell(ssltable, 1, 11, text='Blue/Pink', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=ccicol)

    sslstrength = psarn + exitsign + qqedotn + waen + adxcoln + emacoln + sto__global__ + rs + cc + stval
    strengthcol = color.new(color.new('#00C3FF'), 0) if sslstrength > strengthtreshold else color.new(color.new('#FF0062'), 0) if sslstrength < -1 * strengthtreshold else color.new(color.gray, 0)
    strengthtable: Persistent = table.new(position.top_center, 2, 15, border_width=3, bgcolor=color.new(color.black, 0), border_color=color.new(color.new('#333333'), 0))

    if barstate.islast:
        if showtable2:
            table.cell(strengthtable, 0, 0, text='Strength', text_color=color.new(color.white, 0), text_size=size.normal)
            table.cell(strengthtable, 1, 0, text='Up/Down', text_color=color.new(color.white, 0), text_size=size.normal)

            table.cell(strengthtable, 0, 1, text='10', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=color.new(color.gray, 0))
            table.cell(strengthtable, 1, 1, text=string.tostring(sslstrength), text_color=color.new(color.white, 0), text_size=size.small, bgcolor=strengthcol)

            table.cell(strengthtable, 0, 2, text='Signals', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=color.new(color.gray, 0))
            table.cell(strengthtable, 1, 2, text=string.tostring(sslsignals), text_color=color.new(color.white, 0), text_size=size.small, bgcolor=color.new(color.gray, 0))

            table.cell(strengthtable, 0, 3, text='Filter', text_color=color.new(color.white, 0), text_size=size.small, bgcolor=color.new(color.gray, 0))
            table.cell(strengthtable, 1, 3, text=string.tostring(strend), text_color=color.new(color.white, 0), text_size=size.small, bgcolor=color.new(color.gray, 0))

    sideways = squeezesignalfilter and squeeze or (adxsignalfilter and adx < adxtreshold)
    alertcondition(sslstrength > strengthtreshold or sslstrength < -1 * strengthtreshold, title='TABLE:Strength Alert', message='Table UP/DN Signal Strength')

    alertcondition(not sideways and ta.crossover(close, sslDown), title='SSL Hybrid:SSL Cross Alert', message='SSL1 has crossed.')
    alertcondition(not sideways and ta.crossover(close, sslDown2), title='SSL Hybrid:SSL2 Cross Alert', message='SSL2 has crossed.')

    alertcondition(not sideways and sell_atr, title='SSL Hybrid:Sell Continuation', message='Sell Continuation.')
    alertcondition(not sideways and buy_atr, title='SSL Hybrid:Buy Continuation', message='Buy Continuation.')

    alertcondition(not sideways and ta.crossover(close, sslExit), title='SSL Hybrid:Exit Sell', message='Exit Sell Alert.')
    alertcondition(not sideways and ta.crossover(sslExit, close), title='SSL Hybrid:Exit Buy', message='Exit Buy Alert.')

    alertcondition(not sideways and ta.crossover(close, upperk), title='SSL Hybrid:Baseline Buy Entry', message='Base Buy Alert.')
    alertcondition(not sideways and ta.crossover(lowerk, close), title='SSL Hybrid:Baseline Sell Entry', message='Base Sell Alert.')

    alertcondition(not sideways and ta.cross(ma1, ma2), title='Advanced:EMA20/50 Signal', message='Advanced:EMA20/50  Up/Dn  Signal')
    alertcondition(not sideways and qqeBuy or (not sideways and qqeSell), title='Advanced:QQE Crossover ', message='Advanced: QQE Crossing Zero')

    alertcondition(signalup or signaldn, title='FILTER:Buy/Sell Alert', message='FILTER:TREND FILTER Buy/Sell  Alert')
    alertcondition(signalup, title='FILTER:Buy Alert', message='FILTER:TREND FILTER- Buy Alert')
    alertcondition(signaldn, title='FILTER:Sell Alert', message='FILTER:TREND FILTER- Sell Alert')

    alertcondition(not sideways and ta.cross(close, sslExit), title='Advanced:SSL Buy Sell Alert', message='Advanced:SSL BUY / SELL / Alert.')
    alertcondition(squeeze or adx < adxtreshold, title='Advanced ADX:Volatile Sideways /Exit trade', message='Advanced:Low ADX / Dont Trade /Exit Trade')
    alertcondition(not sideways and ta.cross(open, ma4), title='Advanced: MTF/HMA Crossover', message='Advanced:MTF/HMA  Crossover Alert')

    alertcondition(not sideways and ta.cross(ma1, ma2) or (not sideways and ta.cross(open, ma4)) or (not sideways and ta.cross(close, sslExit)) or (not sideways and cast_bool(ta.change(direction))), title='MIXED:SSL/Channel or EMA Cross or HMA Buy/sell or SuperTrend', message='MIXED Signal:\nSSL/Channel\n EMA Crossover\n HMA Entry/Exit \n SuperTrend Direction Changed')

    src1: float = high if ppsrc == 'High/Low' else math.max(close, open)
    src12: float = low if ppsrc == 'High/Low' else math.min(close, open)
    ph: float = ta.pivothigh(src1, prd, prd)
    pl: float = ta.pivotlow(src12, prd, prd)

    plotshape(cast_bool(ph) and showpp, text='H', style=shape.triangledown, color=color.new(color.red, 0), textcolor=color.new(color.white, 0), location=location.abovebar, offset=-prd, size=size.auto)
    plotshape(cast_bool(pl) and showpp, text='L', style=shape.triangleup, color=color.new(color.lime, 0), textcolor=color.new(color.white, 0), location=location.belowbar, offset=-prd, size=size.auto)

    Lstyle = line.style_dashed if linestyle == 'Dashed' else line.style_solid if linestyle == 'Solid' else line.style_dotted

    prdhighest = ta.highest(300)
    prdlowest = ta.lowest(300)
    cwidth = (prdhighest - prdlowest) * ChannelW / 100

    pivotvals: Persistent[list[float]] = array.new_float(0)

    if cast_bool(ph) or cast_bool(pl):
        array.unshift(pivotvals, ph if cast_bool(ph) else pl)
        if array.size(pivotvals) > maxnumpp:
            array.pop(pivotvals)

    def get_sr_vals(ind):
        __block_result_3__ = (na, na, na)
        if showsr == True:
            lo: float = array.get(pivotvals, ind)
            hi: float = lo
            numpp: int = 0
            for y in pine_range(0, array.size(pivotvals) - 1, 1):
                cpp: float = array.get(pivotvals, y)
                wdth: float = hi - cpp if cpp <= lo else cpp - lo
                if wdth <= cwidth:
                    lo = cpp if cpp <= lo else lo
                    hi = cpp if cpp > lo else hi
                    numpp = numpp + 1
            __block_result_3__ = (hi, lo, numpp)
        return __block_result_3__

    sr_up_level: Persistent[list[float]] = array.new_float(0)
    sr_dn_level: Persistent[list[float]] = array.new_float(0)
    sr_strength: list[float] = array.new_float(0)

    def find_loc(strength):
        ret = array.size(sr_strength)
        for i in pine_range(array.size(sr_strength) - 1 if ret > 0 else na, 0, 1):
            if strength <= array.get(sr_strength, i):
                break
            ret = i
        return ret

    def check_sr(hi, lo, strength):
        ret: bool = True
        __loop_0__ = pine_loop(0, 1)
        while __loop_0__.step(array.size(sr_up_level) - 1 if array.size(sr_up_level) > 0 else na):
            i = __loop_0__.value
            if array.get(sr_up_level, i) >= lo and array.get(sr_up_level, i) <= hi or (array.get(sr_dn_level, i) >= lo and array.get(sr_dn_level, i) <= hi):
                if strength >= array.get(sr_strength, i):
                    array.remove(sr_strength, i)
                    array.remove(sr_up_level, i)
                    array.remove(sr_dn_level, i)
                else:
                    ret = False
                break
        return ret

    sr_lines: Persistent[list[Line]] = array.new_line(11, na)
    sr_labels: Persistent[list[Label]] = array.new_label(11, na)

    for x in pine_range(1, 10, 1):
        rate = 100 * (label.get_y(array.get(sr_labels, x)) - close) / close
        label.set_text(array.get(sr_labels, x), text=string.tostring(label.get_y(array.get(sr_labels, x))) + '(' + string.tostring(rate, '#.##') + '%)')
        label.set_x(array.get(sr_labels, x), x=bar_index + labelloc)
        label.set_color(array.get(sr_labels, x), color=color.new(color.red, 0) if label.get_y(array.get(sr_labels, x)) >= close else color.new(color.lime, 0))
        label.set_textcolor(array.get(sr_labels, x), textcolor=color.new(color.white, 0) if label.get_y(array.get(sr_labels, x)) >= close else color.new(color.black, 0))
        label.set_style(array.get(sr_labels, x), style=label.style_label_down if label.get_y(array.get(sr_labels, x)) >= close else label.style_label_up)
        line.set_color(array.get(sr_lines, x), color=resistancecolor if line.get_y1(array.get(sr_lines, x)) >= close else supportcolor)

    if cast_bool(ph) or cast_bool(pl):
        array.clear(sr_up_level)
        array.clear(sr_dn_level)
        array.clear(sr_strength)

        for x in pine_range(0, array.size(pivotvals) - 1, 1):
            hi, lo, strength = get_sr_vals(x)
            if check_sr(hi, lo, strength):
                loc = find_loc(strength)

                if loc < maxnumsr and strength >= min_strength:
                    array.insert(sr_strength, loc, strength)
                    array.insert(sr_up_level, loc, hi)
                    array.insert(sr_dn_level, loc, lo)

                    if array.size(sr_strength) > maxnumsr:
                        array.pop(sr_strength)
                        array.pop(sr_up_level)
                        array.pop(sr_dn_level)

        for x in pine_range(1, 10, 1):
            line.delete(array.get(sr_lines, x))
            label.delete(array.get(sr_labels, x))

        for x in pine_range(0, array.size(sr_up_level) - 1 if array.size(sr_up_level) > 0 else na, 1):
            mid: float = math.round_to_mintick((array.get(sr_up_level, x) + array.get(sr_dn_level, x)) / 2)
            rate = 100 * (mid - close) / close
            array.set(sr_labels, x + 1, label.new(x=bar_index + labelloc, y=mid, text=string.tostring(mid) + '(' + string.tostring(rate, '#.##') + '%)', color=color.new(color.red, 0) if mid >= close else color.new(color.lime, 0), textcolor=color.new(color.white, 0) if mid >= close else color.new(color.black, 0), style=label.style_label_down if mid >= close else label.style_label_up))

            array.set(sr_lines, x + 1, line.new(x1=bar_index, y1=mid, x2=bar_index - 1, y2=mid, extend=extend.both, color=resistancecolor if mid >= close else supportcolor, style=Lstyle, width=linewidth))

    def f_crossed_over():
        ret: bool = False
        for x in pine_range(0, array.size(sr_up_level) - 1 if array.size(sr_up_level) > 0 else na, 1):
            mid: float = math.round_to_mintick((array.get(sr_up_level, x) + array.get(sr_dn_level, x)) / 2)
            if close[1] <= mid and close > mid:
                ret = True
        return ret

    def f_crossed_under():
        ret: bool = False
        for x in pine_range(0, array.size(sr_up_level) - 1 if array.size(sr_up_level) > 0 else na, 1):
            mid: float = math.round_to_mintick((array.get(sr_up_level, x) + array.get(sr_dn_level, x)) / 2)
            if close[1] >= mid and close < mid:
                ret = True
        return ret

    alertcondition(f_crossed_over(), title='S/R:Resistance Broken', message='Resistance Broken')
    alertcondition(f_crossed_under(), title='S/R:Support Broken', message='Support Broken')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
