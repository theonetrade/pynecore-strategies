"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, bar_index, bgcolor, close, color, fill, fixnan, high, hl2, hlc3,
    input, label, location, low, math, na, nz, ohlc4, open, plot, plotchar, request, script, size,
    syminfo, ta, timeframe, yloc
)
from pynecore.types import Color, NA, Series


@script.indicator(shorttitle='Multiple strategies [LPWN]', title='Multpile strategies [LUPOWN]', overlay=False, na_bool=True)
def main(
    show_Momen=input(True, title='-----------Show squeeze momentum-------'),
    lengthM=input.int(20, title='MOM Length', minval=1, step=1),
    srcM: Series[float] = input(close, title='MOM Source'),
    length=input.int(20, title='SQZ Length', minval=1, step=1),
    src: Series[float] = input(close, title='SQZ Source'),
    lengths=input(20, title='BB Length'),
    mult=input(2.0, title='BB MultFactor'),
    lengthKC=input(20, title='KC Length'),
    multKC=input(1.5, title='KC MultFactor'),
    scale__ren__=input(75.0, title='General scale'),
    show_ADX=input(True, title='------------Show ADX------------'),
    scaleADX=input(2.0, title='ADX scale'),
    show_di=input(False, title='    Show +DI -DI'),
    show_aa=input.bool(False, 'Mostrar punto 23 aparte', inline='adx line'),
    far=input.int(-7, 'Separacion', inline='adx line'),
    adxlen=input(14, title='ADX Smoothing'),
    dilen=input(14, title='DI Length'),
    keyLevel=input(23, title='Key level for ADX'),
    show_bg=input(False, title='Show bg color'),
    show_whale=input(False, title='Show Whale detector'),
    show_rsi=input(True, title='------------Show RSI---------'),
    show_RSIfondo=input(True, title='Show RSI background'),
    rsiApart=input(0, title='RSI separation'),
    len=input.int(14, minval=1, title='Length RSI '),
    upperR=input(70, title='Upper band'),
    middleR=input(50, title='Middle band'),
    lowerR=input(30, title='Lower band'),
    show_rsi2=input(True, title='Show RSI DIVERGENCE'),
    farRSI=input(70, title='Adjust RSI DIVERGENCE'),
    len_fast=input.int(5, minval=1, title='Length Fast RSI'),
    len_slow=input.int(14, minval=1, title='Length Slow RSI'),
    show_stoch=input(False, title='-------Show Stochastic------'),
    periodK=input.int(14, title='%K Length', minval=1),
    smoothK=input.int(1, title='%K Smoothing', minval=1),
    periodD=input.int(3, title='%D Smoothing', minval=1),
    upS=input(80, title='Upper band'),
    lowS=input(20, title='Lower band'),
    show_ao=input(False, title='-----------Show AO-------'),
    show_aoF=input(True, title='Show ao away 0 point'),
    farAO=input(-30, title='Away from 0 point'),
    fastLength=input(5, title='Fast Length'),
    slowLength=input(34, title='Slow Length'),
    show_macd=input(False, title='-----------Show MACD-------'),
    show_macdF=input(True, title='Show MACD area away 0 point'),
    show_macdLF=input(True, title='Show MACD lines away 0 point'),
    macdF=input(-30, title='Away 0 point'),
    show_macdL=input(False, title='Show MACD lines'),
    fast_length=input(title='Fast Length', defval=12),
    slow_length=input(title='Slow Length', defval=26),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9),
    sma_source=input.string(title='Oscillator MA Type', defval='EMA', options=('SMA', 'EMA')),
    sma_signal=input.string(title='Signal Line MA Type', defval='EMA', options=('SMA', 'EMA')),
    macdScale=input(2, title='MACD scale'),
    show_K=input(False, title='---------------Show Koncorde-------------'),
    scaleK=input(8, title='Koncorde scale'),
    showKF=input(True, title='Show Koncorde away 0 point'),
    fark=input(-30, title='Away from 0 point'),
    show_KD=input(False, title='Show Koncorde Diamond'),
    kon_pos=input(30, title='Position diamonds Bull'),
    kon_posn=input(-30, title='Position diamonds Bear'),
    srcTprice: Series[float] = input(ohlc4, title='Fuente para Precio Total'),
    srcMfi: Series[float] = input.source(hlc3, title='Fuente MFI', group='Money Flow Index'),
    m=input(15, title='Media Exponencial'),
    longitudPVI=input(90, title='Longitud PVI'),
    longitudNVI=input(90, title='Longitud NVI'),
    longitudMFI=input(14, title='Longitud MFI'),
    multK=input.float(2.0, title='Multiplicador para derivacion estandar', group='Bollinger Oscillator'),
    boLength=input.int(25, title='Calculation length ', group='Bollinger Oscillator'),
    show_cci=input(False, title='------------Show CCI---------'),
    cci_len=input(14, 'CCI length'),
    cci_src: Series[float] = input(close, 'CCI source'),
    upperCCI=input(100, 'CCI Upper band'),
    lowerCCI=input(-100, 'CCI lower band'),
    rsiMFIShow=input(True, title='----------Show MFI---------'),
    rsiMFIperiod=input(60, title='MFI Period'),
    rsiMFIMultiplier=input.float(150, title='MFI Area multiplier'),
    rsiMFIPosY=input(2.5, title='MFI Area Y Pos'),
    show_cphr=input(True, title='------------Show Cipher dots---------'),
    n1=input(9, title='Channel Length'),
    n2=input(12, title='Average Length'),
    smooth=input(3, title='Smooth Factor'),
    show_status=input(True, title='------Show STATUS----------'),
    dist=input(10, title='Distancia del monitor'),
    dashColor=input.color(color.new(color.new('#696969'), 90), 'label Color', inline='Dash Line'),
    dashTextColor=input.color(color.new(color.new('#FFFFFF'), 0), 'Text Color', inline='Dash Line'),
    show_div=input(True, title='------Divergencias--------'),
    lbR=input(title='Pivot Lookback Right', defval=1),
    lbL=input(title='Pivot Lookback Left', defval=1),
    rangeUpper=input(title='Max of Lookback Range', defval=60),
    rangeLower=input(title='Min of Lookback Range', defval=1),
    plotBull=input(title='Plot Bullish', defval=True),
    plotHiddenBull=input(title='Plot Hidden Bullish', defval=True),
    plotBear=input(title='Plot Bearish', defval=True),
    plotHiddenBear=input(title='Plot Hidden Bearish', defval=True)
):
    sz: Series = ta.linreg(srcM - math.avg(math.avg(ta.highest(high, lengthM), ta.lowest(low, lengthM)), ta.sma(close, lengthM)), lengthM, 0)
    sc1 = sz >= 0
    sc2 = sz < 0
    sc3 = sz >= sz[1]
    sc4 = sz < sz[1]
    clr = color.new('#00FF00') if sc1 and sc3 else color.new('#008000') if sc1 and sc4 else color.new('#FF0000') if sc2 and sc4 else color.new('#800000') if sc2 and sc3 else color.gray
    plot(sz if show_Momen else na, title='Squeeze Momentum', color=clr, style=plot.style_area)
    useTrueRange: bool = True
    source = close
    basis = ta.sma(source, lengths)
    dev = multKC * ta.stdev(source, lengths)
    upperBB = basis + dev
    lowerBB = basis - dev
    ma = ta.sma(source, lengthKC)
    range_1 = ta.tr if useTrueRange else high - low
    rangema = ta.sma(range_1, lengthKC)
    upperKC = ma + rangema * multKC
    lowerKC = ma - rangema * multKC
    sqzOn = lowerBB > lowerKC and upperBB < upperKC
    sqzOff = lowerBB < lowerKC and upperBB > upperKC
    noSqz = sqzOn == False and sqzOff == False
    scolor = color.blue if noSqz else color.new('#000000') if sqzOn else color.gray
    plot(0 if show_Momen else na, title='Squeeze Zero Line', color=scolor, linewidth=2, style=plot.style_cross)
    def dirmov(len):
        up = ta.change(high)
        down = -ta.change(low)
        truerange = ta.rma(ta.tr, len)
        plus = fixnan(100 * ta.rma(up if up > down and up > 0 else 0, len) / truerange)
        minus = fixnan(100 * ta.rma(down if down > up and down > 0 else 0, len) / truerange)
        return (plus, minus)

    def adx(dilen, adxlen):
        plus, minus = dirmov(dilen)
        sum = plus + minus
        adx__0000002e__ = 100 * ta.rma(math.abs(plus - minus) / (1 if sum == 0 else sum), adxlen)
        return (adx__0000002e__, plus, minus)

    adxValue: Series
    adxValue, diplus, diminus = adx(dilen, adxlen)
    def biggest(series):
        max: Series[float] = 0.0
        max = nz(max[1], series)
        if series > max:
            max = series
        return max

    ni = biggest(sz)
    far1 = far * ni / scale__ren__
    adx_scale = (adxValue - keyLevel) * ni / scale__ren__
    adx_scale2 = (adxValue - keyLevel + far) * ni / scale__ren__
    dip = (diplus - keyLevel) * ni / scale__ren__
    dim = (diminus - keyLevel) * ni / scale__ren__
    plot(dip * scaleADX if show_di else na, color=color.new(color.green, 0), title='DI+')
    plot(dim * scaleADX if show_di else na, color=color.new(color.red, 0), title='DI-')
    color_ADX = color.new('#FFFFFF') if adxValue > adxValue[1] else color.new('#A09A9A')
    bgcolor(clr if adxValue > adxValue[1] and adxValue > 23 and show_Momen and show_bg else na)
    def xrf(values: Series, length):
        r_val = NA(float)
        if length >= 1:
            for i in pine_range(0, length, 1):
                if na(r_val) or not na(values[i]):
                    r_val = values[i]
        return r_val

    def xsa(src: Series, len, wei):
        sumf: Series[float] = 0.0
        ma: float = 0.0
        out: Series[float] = 0.0
        sumf = nz(sumf[1]) - nz(src[len]) + src
        ma = na if na(src[len]) else sumf / len
        out = ma if na(out[1]) else (src * wei + out[1] * (len - wei)) / len
        return out

    var2 = xrf(low, 1)
    var3 = xsa(math.abs(low - var2), 3, 1) / xsa(math.max(low - var2, 0), 3, 1) * 100
    var4 = ta.ema(var3 * 10 if close * 1.2 else var3 / 10, 3)
    var5 = ta.lowest(low, 30)
    var6 = ta.highest(var4, 30)
    lowest_1 = ta.lowest(low, 58)
    var7 = 1 if cast_bool(lowest_1) else 0
    var8 = ta.ema((var4 + var6 * 2) / 2 if low <= var5 else 0, 3) / 618 * var7
    plot(var8 * (ni / scale__ren__) if show_whale else na, title='whale', style=plot.style_columns, color=color.new(color.yellow, 80))
    rsi = ta.rsi(src, len)
    rsiColor = color.green if rsi <= lowerR else color.red if rsi >= upperR else color.new('#DA00FF')
    rsi_scale: Series = (rsi + rsiApart) * ni / scale__ren__
    b1s = (rsiApart + upperR) * ni / scale__ren__
    bm = (rsiApart + middleR) * ni / scale__ren__
    b0s = (rsiApart + lowerR) * ni / scale__ren__
    src_fast = close
    src_slow = close
    up_fast = ta.rma(math.max(ta.change(src_fast), 0), len_fast)
    down_fast = ta.rma(-math.min(ta.change(src_fast), 0), len_fast)
    rsi_fast = 100 if down_fast == 0 else 0 if up_fast == 0 else 100 - 100 / (1 + up_fast / down_fast)
    up_slow = ta.rma(math.max(ta.change(src_slow), 0), len_slow)
    down_slow = ta.rma(-math.min(ta.change(src_slow), 0), len_slow)
    rsi_slow = 100 if down_slow == 0 else 0 if up_slow == 0 else 100 - 100 / (1 + up_slow / down_slow)
    divergence = rsi_fast - rsi_slow
    divergence_scale = divergence * (ni / scale__ren__)
    rsiColor2 = color.lime if divergence > 0 else color.red
    plot(rsi_scale if show_rsi else divergence_scale + farRSI * ni / scale__ren__ if show_rsi2 else na, 'RSI', color=rsiColor if show_rsi else rsiColor2 if show_rsi2 else na)
    k = ta.sma(ta.stoch(close, high, low, periodK), smoothK)
    d = ta.sma(k, periodD)
    k1 = k * ni / scale__ren__
    d1 = d * ni / scale__ren__
    plot(k1 if show_stoch else na, title='%K', color=color.new(color.new('#2962FF'), 0))
    plot(d1 if show_stoch else na, title='%D', color=color.new(color.new('#FF6D00'), 0))
    h1s = upS * ni / scale__ren__
    h0s = lowS * ni / scale__ren__
    ao: Series = ta.sma(hl2, fastLength) - ta.sma(hl2, slowLength)
    ao_f = ao + farAO * ni / scale__ren__
    aoColor = (color.new('#26A69A') if ao[1] < ao else color.new('#B2DFDB')) if ao >= 0 else color.new('#FFCDD2') if ao[1] < ao else color.new('#EF5350')
    aoPlot = plot(ao_f if show_aoF and show_ao else ao if show_ao else na, title='AO', style=plot.style_line if show_aoF else plot.style_area if show_ao else plot.style_area, color=aoColor)
    bandA = plot(farAO * ni / scale__ren__ if show_aoF and show_ao else na, color=color.new(color.white, 60))
    fill(aoPlot, bandA, color=color.new(aoColor if show_aoF and show_ao else na, 90), title='AO Fill')
    fast_ma = ta.sma(src, fast_length) if sma_source == 'SMA' else ta.ema(src, fast_length)
    slow_ma = ta.sma(src, slow_length) if sma_source == 'SMA' else ta.ema(src, slow_length)
    macd1 = fast_ma - slow_ma
    signal = ta.sma(macd1, signal_length) if sma_signal == 'SMA' else ta.ema(macd1, signal_length)
    hist: Series = macd1 - signal
    macdColor = (color.new('#26A69A') if hist[1] < hist else color.new('#B2DFDB')) if hist >= 0 else color.new('#FFCDD2') if hist[1] < hist else color.new('#EF5350')
    histo = hist * macdScale
    macd = macd1 * macdScale
    sign = signal * macdScale
    histo_f = histo + macdF * ni / scale__ren__
    colorlineMACD = color.green if macd > sign else color.red
    histoA = plot(histo_f if show_macdF and show_macd else histo if show_macd else na, title='Histogram', style=plot.style_line if show_macdF and show_macd else plot.style_columns if show_macd else plot.style_columns, color=macdColor)
    plot(macd + macdF * ni / scale__ren__ if show_macdLF and show_macdL else macd if show_macdL else na, title='MACD', color=colorlineMACD)
    plot(sign + macdF * ni / scale__ren__ if show_macdLF and show_macdL else sign if show_macdL else na, title='Signal', color=color.new(color.orange, 0))
    band_macd = plot(macdF * ni / scale__ren__ if show_macdF and show_macd else na, color=color.new(color.white, 60))
    fill(histoA, band_macd, color=color.new(macdColor if show_macdF and show_macd else na, 90), title='MACD Fill')
    tprice = srcTprice
    pvim = ta.ema(ta.pvi, m)
    pvimax = ta.highest(pvim, longitudPVI)
    pvimin = ta.lowest(pvim, longitudPVI)
    oscp = (ta.pvi - pvim) * 100 / (pvimax - pvimin)
    nvim = ta.ema(ta.nvi, m)
    nvimax = ta.highest(nvim, longitudNVI)
    nvimin = ta.lowest(nvim, longitudNVI)
    azul = (ta.nvi - nvim) * 100 / (nvimax - nvimin)
    xmf = ta.mfi(srcMfi, longitudMFI)
    basisK = ta.sma(tprice, boLength)
    devK = mult * ta.stdev(tprice, boLength)
    upper = basisK + devK
    lower = basisK - devK
    OB1 = (upper + lower) / 2.0
    OB2 = upper - lower
    BollOsc = (tprice - OB1) / OB2 * 100
    xrsi = ta.rsi(tprice, 14)
    def calc_stoch(src, length, smoothFastD):
        ll = ta.lowest(low, length)
        hh = ta.highest(high, length)
        k = 100 * (src - ll) / (hh - ll)
        return ta.sma(k, smoothFastD)

    stoc = calc_stoch(tprice, 21, 3)
    marron = (xrsi + xmf + BollOsc + stoc / 3) / 2
    verde = marron + oscp
    media = ta.ema(marron, m)
    bandacero = fark * ni / scale__ren__ if showKF else 0
    scaleK1 = ni / scale__ren__ / scaleK
    lk1 = plot(marron * scaleK1 + fark * ni / scale__ren__ if show_K and showKF else marron * scaleK1 if show_K else na, color=color.new(color.new('#330000'), 0), style=plot.style_line, linewidth=3, title='lmarron')
    lk2 = plot(verde * scaleK1 + fark * ni / scale__ren__ if show_K and showKF else verde * scaleK1 if show_K else na, color=color.new(color.new('#006600'), 0), style=plot.style_line, linewidth=3, title='lineav')
    lk3 = plot(azul * scaleK1 + fark * ni / scale__ren__ if show_K and showKF else azul * scaleK1 if show_K else na, color=color.new(color.new('#000066'), 0), style=plot.style_line, title='lazul')
    plot(media * scaleK1 + fark * ni / scale__ren__ if show_K and showKF else media * scaleK1 if show_K else na, color=color.new(color.red, 0), title='media', style=plot.style_line, linewidth=2)
    band0k = plot(bandacero if show_K else na, color=color.new(color.black, 0), title='cero')
    fill(lk2, band0k, color=color.new(color.new('#66FF66') if show_K else na, 50), title='verde')
    fill(lk1, band0k, color=color.new(color.new('#FFCC99') if show_K else na, 50), title='marron')
    fill(lk3, band0k, color=color.new(color.new('#00FFFF') if show_K else na, 50), title='azul')
    konBull = ta.crossover(marron, media) and show_KD
    konBear = ta.crossunder(marron, media) and show_KD
    konlBull = kon_pos * ni / scale__ren__
    konlBear = kon_posn * ni / scale__ren__
    plotchar(konlBull if konBull else konlBear if konBear else na, title='Koncorde diamond', char='◆', color=color.lime if konBull else color.maroon if konBear else color.white, location=location.absolute, size=size.tiny)
    b1cci = upperCCI * ni / scale__ren__ * 30 / 100
    b0cci = lowerCCI * ni / scale__ren__ * 30 / 100
    cci = ta.cci(cci_src, cci_len)
    cci_scale = 30 * (cci * ni / scale__ren__) / 100
    plot(cci_scale if show_cci else na, color=color.new(color.blue, 0), linewidth=2, title='CCI')
    colorcm = color.blue if show_cci else color.white
    band1 = plot(b1s if show_rsi else h1s if show_stoch else na, color=color.white if bar_index % 2 == 0 else color.new('#00000000'))
    band0 = plot(b0s if show_rsi else h0s if show_stoch else b0cci if show_cci else na, color=color.white if bar_index % 2 == 0 else color.new('#00000000'))
    bandm = plot(b1cci if show_cci else bm if show_rsi else farRSI * ni / scale__ren__ if show_rsi2 else na, color=colorcm if bar_index % 2 == 0 else color.new('#00000000'))
    band00 = plot(b0cci if show_cci else na, color=color.blue if bar_index % 2 == 0 else color.new('#00000000'))
    fill(band1, band0, color=color.new(color.purple if show_rsi and show_RSIfondo else na, 90), title='RSI background')
    def f_rsimfi(_period, _multiplier, _tf):
        return request.security(syminfo.tickerid, _tf, ta.sma((close - open) / (high - low) * _multiplier, _period) - rsiMFIPosY)

    rsiMFI = f_rsimfi(rsiMFIperiod, rsiMFIMultiplier, timeframe.period)
    rsiMFIColor1: Color = color.new('#FFFFFF')
    rsiMFIColor2: Color = color.new('#D1D4DC')
    rsiMFIColor = rsiMFIColor1 if rsiMFI >= 0 else rsiMFIColor2 if rsiMFI < 0 else na
    rsiMFIplot = plot(rsiMFI * ni / scale__ren__ if rsiMFIShow else na, title='RSI+MFI Area', color=rsiMFIColor, style=plot.style_area)
    def CALC(n1, n2, smooth):
        ap = hlc3
        esa = ta.ema(ap, n1)
        dw = ta.ema(math.abs(ap - esa), n1)
        ci = (ap - esa) / (0.015 * dw)
        tci = ta.ema(ci, n2)
        wt1 = tci
        wt2 = ta.sma(wt1, smooth)
        wave = wt1 - wt2
        wavecolor = color.lime if wave >= 0 else color.red
        return (wave, wavecolor)

    wave, wavecolor = CALC(n1, n2, smooth)
    middle: int = 0
    condWt = True if ta.cross(wave, middle) else False
    wtjeje = sz if show_Momen else ao if show_ao else macd if show_macd else na
    plot(wtjeje if condWt and show_cphr else na, title='Buy and sell circle', color=wavecolor, style=plot.style_circles, linewidth=3)
    plot(far1 * scaleADX if show_aa else na, color=color.new(color.white, 0), title='Punto 23')
    p1 = plot(adx_scale2 * scaleADX if show_aa else adx_scale * scaleADX if show_ADX else na, color=color_ADX, title='ADX', linewidth=2)
    if adxValue > adxValue[1] and adxValue > 23:
        'ADX con pendiente positiva por encima punto 23'
    if adxValue > adxValue[1] and adxValue < 23:
        'ADX con pendiente positiva por debajo punto 23'
    if adxValue < adxValue[1] and adxValue < 23:
        'ADX con pendiente negativa por debajo punto 23'
    if adxValue < adxValue[1] and adxValue > 23:
        'ADX con pendiente negativa por encima punto 23'
    a1 = adxValue >= 23
    a2 = adxValue < 23
    a3 = adxValue >= adxValue[1]
    a4 = adxValue < adxValue[1]
    iAdx = 'Pendiente positiva ↑ 23' if a1 and a3 else 'Pendiente negativa ↑ 23' if a1 and a4 else 'Pendiente negativa ↓ 23' if a2 and a4 else 'Pendiente positiva ↓ 23' if a2 and a3 else '-'
    iMom = 'Direccionalidad alcista' if sc1 and sc3 else 'Direccionalidad bajista' if sc1 and sc4 else 'Direccionalidad bajista' if sc2 and sc4 else 'Direccinalidad alcista' if sc2 and sc3 else '-'
    igral = 'Fuerte movimiento alcista' if a1 and a3 and sc1 and sc3 else 'Monitor muestra rango-caida pero\nel movimiento tiene fuerza' if a1 and a3 and sc1 and sc4 else 'Fuerte movimiento bajista' if a1 and a3 and sc2 and sc4 else 'Monitor muestra rango-subida pero\nel movimiento tiene fuerza' if a1 and a3 and sc2 and sc3 else 'Movimiento alcista sin fuerza' if a1 and a4 and sc1 and sc3 else 'Monitor muestra rango-caida\n pendiente negativa en ADX ' if a1 and a4 and sc1 and sc4 else 'Movimiento bajista sin fuerza' if a1 and a4 and sc2 and sc4 else 'Monitor muestra rango-subida con \npendiente negativa en ADX ' if a1 and a4 and sc2 and sc3 else 'Movimiento alcista sin fuerza' if a2 and a4 and sc1 and sc3 else 'Monitor muestra rango-caida sin fuerza ' if a2 and a4 and sc1 and sc4 else 'Movimiento bajista sin fuerza' if a2 and a4 and sc2 and sc4 else 'Monitor muestra rango-subida sin fuerza ' if a2 and a4 and sc2 and sc3 else 'Movimiento alcista que \n quiere agarrar fuerza' if a2 and a3 and sc1 and sc3 else 'Monitor muestra rango-caida,\n el movimiento quiere agarrar fuerza' if a2 and a3 and sc1 and sc4 else 'Movimiento bajista que \n quiere agarrar fuerza' if a2 and a3 and sc2 and sc4 else 'Monitor muestra rango-subida,\n el movimiento quiere agarrar fuerza' if a2 and a3 and sc2 and sc3 else '-'
    s: str = '\n'
    scr_label = 'Info ADX: ' + iAdx + s + 'Info monitor: ' + iMom + s + 'Info general:' + s + igral
    if show_status:
        lab_l: Series = label.new(bar_index + dist, 0, '\t Estatus segun estrategia\n\t' + scr_label, color=dashColor, textcolor=dashTextColor, style=label.style_label_left, yloc=yloc.price)
        label.delete(lab_l[1])
    if scr_label != '':
        alert('Estatus segun estrategia\n' + scr_label, freq=alert.freq_once_per_bar_close)
    bearColor: Color = color.new('#FF0000')
    bullColor: Color = color.new('#1BFF00')
    hiddenBullColor: Color = color.new('#A4FF99')
    hiddenBearColor: Color = color.new('#FF9E9E')
    textColor = color.white
    noneColor = color.new(color.white, 100)
    def plFound(osc):
        return False if na(ta.pivotlow(osc, lbL, lbR)) else True

    def phFound(osc):
        return False if na(ta.pivothigh(osc, lbL, lbR)) else True

    def _inRange(cond):
        bars = ta.barssince(cond == True)
        return rangeLower <= bars and bars <= rangeUpper

    def _findDivRB(osc: Series):
        plFound_1: Series = plFound(osc)
        _inRange_1 = _inRange(plFound_1[1])
        oscHL = osc[lbR] > ta.valuewhen(plFound(osc), osc[lbR], 1) and _inRange_1
        priceLL = low[lbR] < ta.valuewhen(plFound(osc), low[lbR], 1)
        plFound_2 = plFound(osc)
        bullCond = plotBull and priceLL and oscHL and plFound_2
        plFound_3: Series = plFound(osc)
        _inRange_2 = _inRange(plFound_3[1])
        oscLL = osc[lbR] < ta.valuewhen(plFound(osc), osc[lbR], 1) and _inRange_2
        priceHL = low[lbR] > ta.valuewhen(plFound(osc), low[lbR], 1)
        plFound_4 = plFound(osc)
        hiddenBullCond = plotHiddenBull and priceHL and oscLL and plFound_4
        phFound_1: Series = phFound(osc)
        _inRange_3 = _inRange(phFound_1[1])
        oscLH = osc[lbR] < ta.valuewhen(phFound(osc), osc[lbR], 1) and _inRange_3
        priceHH = high[lbR] > ta.valuewhen(phFound(osc), high[lbR], 1)
        phFound_2 = phFound(osc)
        bearCond = plotBear and priceHH and oscLH and phFound_2
        phFound_3: Series = phFound(osc)
        _inRange_4 = _inRange(phFound_3[1])
        oscHH = osc[lbR] > ta.valuewhen(phFound(osc), osc[lbR], 1) and _inRange_4
        priceLH = high[lbR] < ta.valuewhen(phFound(osc), high[lbR], 1)
        phFound_4 = phFound(osc)
        hiddenBearCond = plotHiddenBear and priceLH and oscHH and phFound_4
        return (bullCond, hiddenBullCond, bearCond, hiddenBearCond)

    sz_bullCond, sz_hiddenBullCond, sz_bearCond, sz_hiddenBearCond = _findDivRB(sz)
    foundDivBSZ = True if plFound(sz) and show_Momen and show_div else False
    colordivBSZ = bullColor if sz_bullCond else hiddenBullColor if sz_hiddenBullCond else noneColor
    foundDivBeSZ = True if phFound(sz) and show_Momen and show_div else False
    colordivBeSZ = bearColor if sz_bearCond else hiddenBearColor if sz_hiddenBearCond else noneColor
    plot(sz[lbR] if foundDivBSZ else na, offset=-lbR, title='Regular Bullish', linewidth=1, color=colordivBSZ)
    plot(sz[lbR] if foundDivBeSZ else na, offset=-lbR, title='Regular Bullish', linewidth=1, color=colordivBeSZ)
    rsi_bullCond, rsi_hiddenBullCond, rsi_bearCond, rsi_hiddenBearCond = _findDivRB(rsi_scale)
    foundDivBRSI = True if plFound(rsi_scale) and show_rsi and show_div else False
    colordivBRSI = bullColor if rsi_bullCond else hiddenBullColor if rsi_hiddenBullCond else noneColor
    foundDivBeRSI = True if phFound(rsi_scale) and show_rsi and show_div else False
    colordivBeRSI = bearColor if rsi_bearCond else hiddenBearColor if rsi_hiddenBearCond else noneColor
    plot(rsi_scale[lbR] if foundDivBRSI else na, offset=-lbR, title='Regular Bullish', linewidth=1, color=colordivBRSI)
    plot(rsi_scale[lbR] if foundDivBeRSI else na, offset=-lbR, title='Regular Bullish', linewidth=1, color=colordivBeRSI)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
