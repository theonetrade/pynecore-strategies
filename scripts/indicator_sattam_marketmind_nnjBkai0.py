"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt_copy
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, barmerge, barstate, box,
    chart, close, color, extend, format, high, hour, input, label, line, location, low, math, na,
    nz, open, plot, plotcandle, plotshape, position, request, script, shape, size, string, syminfo,
    ta, table, text, time, timeframe, volume, xloc, yloc
)
from pynecore.types import Box, Color, Label, Line, NA, Persistent, PersistentSeries, Series, Table
import lib.toodegrees.forex_factory_decoding.v46 as ffDec
import lib.toodegrees.forex_factory_utility.v17 as ffUtil

g1: str = "① MarketMind Signal / إشارات ماركت مايند"
g2: str = "② Signals Display / عرض الإشارات"
g3: str = "③ TP / SL / GE / الأهداف والوقف"
g4: str = "④ Support & Resistance / الدعوم والمقاومات"
g5: str = "⑤ Chart Drawing / أدوات الرسم"
g6: str = "⑥ Candles / الشموع"
g7: str = "⑦ Daily & Weekly / اليومي والأسبوعي"
g8: str = "⑧ Probability / احتمالية الشمعة"
g9: str = "⑨ HTF Candles / شموع الإطار الأعلى"
g10: str = "⑩ MarketMind Table / جدول ماركت مايند"
g11: str = "⑪ News / الأخبار"
g12: str = "⑫ Timezone / التوقيت"
g13: str = "⑬ External Data / بيانات خارجية"


@script.indicator("SATTAM | MarketMind", "SATTAM | MarketMind", overlay=True, max_boxes_count=500, max_labels_count=500, max_lines_count=500)
def main(
    i_mode=input.string("MarketMind + ", "MarketMind Mode / اسلوب ماركت مايند", options=("MarketMind", "MarketMind + ", "MarketMind + FILTER"), group=g1),
    i_multF=input.float(3.0, "Fast Multiplier / مضاعف سريع", minval=1.0, maxval=10.0, step=0.1, group=g1),
    i_multS=input.float(4.0, "Slow Multiplier / مضاعف بطيء", minval=1.0, maxval=10.0, step=0.1, group=g1),
    i_filtLook=input.int(120, "Filter Breakout Bars / نافذة اختراق الفلتر", minval=20, maxval=300, group=g1),
    i_sig=input.bool(True, "MarketMind Signals / اشارات ماركت مايند", group=g2),
    i_sigText=input.bool(False, "Show Buy/Sell Text / اظهار نص البيع والشراء", group=g2),
    i_confirm=input.bool(True, "Enable MarketMind Confirm Signals / تمكين إشارات MarketMind Confirm", group=g2),
    i_rrBox=input.bool(False, "Show Risk/Reward Boxes / عرض صناديق المخاطرة والمكافأة", group=g3),
    i_tsl=input.bool(True, "Enable TSL / تمكين وقف الخسارة المتحرك", group=g3),
    i_slLabel=input.bool(True, "Show Stop Loss Labels / عرض علامات وقف الخسارة", group=g3),
    i_tpHit=input.bool(True, "Show TP Hit Labels / عرض إشارات تحقيق الهدف", group=g3),
    i_tpShow=input.bool(True, "Show TP Targets / إظهار الأهداف TP1 TP2 TP3", group=g3),
    i_geShow=input.bool(True, "Show Golden Entry Label / إظهار علامة الدخول الذهبي GE", group=g3),
    i_slMult=input.float(4.0, "Stop × ATR / مضاعف الوقف", minval=0.5, maxval=15.0, step=0.1, group=g3),
    i_geM=input.float(1.0, "Golden Entry × ATR / الدخول الذهبي", minval=0.1, maxval=5.0, step=0.1, group=g3),
    i_tp1M=input.float(2.0, "TP1 × ATR", minval=0.5, maxval=20.0, step=0.1, group=g3),
    i_tp2M=input.float(4.0, "TP2 × ATR", minval=0.5, maxval=20.0, step=0.1, group=g3),
    i_tp3M=input.float(6.0, "TP3 × ATR", minval=0.5, maxval=20.0, step=0.1, group=g3),
    i_lblSize=input.int(3, "Labels Size / حجم الاهداف ووقف الخسارة والدخول الذهبي", minval=1, maxval=5, group=g3),
    i_sr=input.bool(True, "Support & Resistance / الدعوم والمقاومات", group=g4),
    i_srVol=input.bool(True, "Show Volume Info / معلومات حجم الدعوم والمقاومات", group=g4),
    i_srBreak=input.bool(False, "Show Break of S&R ($) / إظهار كسر الدعوم والمقاومات", group=g4),
    i_ma=input.bool(False, "MarketMind MA / متوسط ماركت مايند السعري", group=g5),
    i_channel=input.bool(True, "MarketMind Channel / قناة ماركت مايند السعرية", group=g5),
    i_fib=input.bool(False, "Fibonacci / فيبوناتشي", group=g5),
    i_fibType=input.string("Internal", "Fibonacci Type / نوع الفيبوناتشي", options=("Internal", "External", "Both"), group=g5),
    i_struct=input.bool(False, "Structure Breaks (CHoCH & BoS) / الهيكلية", group=g5),
    i_structTyp=input.string("Internal", "Structure Type / نوع الهيكلية", options=("Internal", "External", "Both"), group=g5),
    i_paint=input.bool(True, "Paint Bars / تلوين الشموع", group=g6),
    i_colDn=input.color(color.new('#E91E63'), "DownTrend Color / لون الشموع الهابطة", group=g6),
    i_colUp=input.color(color.new('#00BCD4'), "UpTrend Color / لون الشموع الصاعدة", group=g6),
    i_pdhl=input.bool(False, "Previous Day High/Low (PDH/PDL) / أعلى وأدنى اليوم السابق", group=g7),
    i_dayDiv=input.bool(False, "Daily Divider / الفاصل اليومي", group=g7),
    i_pwhl=input.bool(False, "Previous Week High/Low (PWH/PWL) / أعلى وأدنى الأسبوع السابق", group=g7),
    i_weekDiv=input.bool(False, "Weekly Divider / الفاصل الأسبوعي", group=g7),
    i_nextPct=input.bool(False, "Next Candles % / احتمالية الشمعة القادمة", group=g8),
    i_htf=input.bool(False, "Show HTF Candles / اظهار شموع الاطار الزمني الاكبر", group=g9),
    i_htfVP=input.bool(False, "Show Volume Profile / اظهار البروفايل", group=g9),
    i_htfTF=input.timeframe("D", "Timeframe / الإطار الزمني", group=g9),
    i_htfCount=input.int(1, "Amount of Candles / عدد الشموع", minval=1, maxval=10, group=g9),
    i_table=input.bool(True, "Show MarketMind Table / جدول ماركت مايند", group=g10),
    i_tblV=input.string("bottom", "Vertical Position / الموقع الرأسي", options=("top", "middle", "bottom"), group=g10),
    i_tblH=input.string("right", "Horizontal Position / الموقع الأفقي", options=("left", "center", "right"), group=g10),
    i_tblSize=input.string("Tiny / صغير جداً", "Table Size / حجم الجدول", options=("Tiny / صغير جداً", "Small / صغير", "Normal / عادي", "Large / كبير", "Huge / ضخم"), group=g10),
    i_tblTheme=input.string("Classic / كلاسيكي", "Table Colors / ألوان الجدول", options=("Classic / كلاسيكي", "Dark / خلفية سوداء"), group=g10),
    i_news=input.bool(True, "Show News / عرض الاخبار", group=g11),
    i_newsType=input.string("Today", "Table Type / نوع الجدول", options=("Today", "This Week"), group=g11),
    i_newsTime=input.string("AM/PM", "Time Format / تنسيق الوقت", options=("24H", "AM/PM"), group=g11),
    i_newsH=input.string("Right", "Horizontal Align / المحاذاة الأفقية", options=("Left", "Center", "Right"), group=g11),
    i_newsV=input.string("Top", "Vertical Align / المحاذاة العمودية", options=("Top", "Middle", "Bottom"), group=g11),
    i_newsSize=input.string("Tiny / صغير جداً", "Table Size / حجم الجدول", options=("Tiny / صغير جداً", "Small / صغير", "Normal / عادي", "Large / كبير", "Huge / ضخم"), group=g11),
    i_newsCur=input.bool(False, "Symbol currency only / أخبار عملة الرمز فقط", group=g11),
    i_newsHigh=input.bool(True, "🔴 High / عالي", group=g11, inline="imp"),
    i_newsMed=input.bool(True, "🟠 Medium / متوسط", group=g11, inline="imp"),
    i_newsLow=input.bool(False, "🟡 Low / منخفض", group=g11, inline="imp2"),
    i_newsHol=input.bool(False, "⚪ Holiday / عطلة", group=g11, inline="imp2"),
    i_tzOn=input.bool(True, "Custom Timezone (UTC) / التوقيت الزمني المخصص", group=g12),
    i_tzH=input.int(3, "Hours / الساعات", minval=-12, maxval=14, group=g12),
    i_tzM=input.int(0, "Minutes / دقيقة", minval=0, maxval=59, group=g12),
    i_nbOn=input.bool(False, "Block signals around news / حجب الإشارات حول الأخبار", group=g13),
    i_nbBefore=input.int(15, "Minutes before / دقائق قبل", minval=0, maxval=240, group=g13, inline="nb"),
    i_nbAfter=input.int(15, "Minutes after / دقائق بعد", minval=0, maxval=240, group=g13, inline="nb"),
    i_nbRedOnly=input.bool(True, "High impact only / الأحمر فقط", group=g13),
    i_macroOn=input.bool(False, "Macro filter (DXY / US10Y) / فلتر الدولار والعائد", group=g13),
    i_macroSrc=input.string("Both", "Source / المصدر", options=("DXY", "US10Y", "Both"), group=g13),
    i_macroLen=input.int(20, "MA length / طول المتوسط", minval=2, maxval=200, group=g13),
    i_cotOn=input.bool(False, "Show COT row / إظهار صف COT", group=g13),
    i_cotCode=input.string("088691", "CFTC code / رمز CFTC (ذهب 088691 · ناسداك 209742 · S&P 13874A)", group=g13),
    i_finOn=input.bool(False, "Show fundamentals row / إظهار صف أساسيات الشركة", group=g13),
    i_finField=input.string("Revenue", "Field / الحقل", options=("Revenue", "EPS", "Net income", "Debt/Equity"), group=g13)
):
    SIG_UP: Color = color.new('#61C1FD')
    SIG_DN: Color = color.new('#FF0000')
    CONF_UP: Color = color.new('#00DDFF')
    CONF_DN: Color = color.new('#FF0000')
    TP_COL: Color = color.new('#4CAF50')
    GE_COL: Color = color.new('#FDD835')
    SL_COL: Color = color.new('#F23645')
    TSL_COL: Color = color.new('#FF5252')
    ZONE_SUP: Color = color.new('#F02424')
    ZONE_DEM: Color = color.new('#00DDFB')

    haOpen: PersistentSeries[float] = na(float)
    haClose: Series = (open + high + low + close) / 4
    haOpen = (open + close) / 2 if na(haOpen[1]) else (haOpen[1] + haClose[1]) / 2
    haHigh = math.max(high, math.max(haOpen, haClose))
    haLow = math.min(low, math.min(haOpen, haClose))
    haUp: Series = haClose >= haOpen

    mmLine = (haOpen + haClose) / 2

    ATR_LEN: int = 14

    haTR = haHigh - haLow if na(haClose[1]) else math.max(haHigh - haLow, math.max(math.abs(haHigh - haClose[1]), math.abs(haLow - haClose[1])))
    haATR = ta.rma(haTR, ATR_LEN)

    def f_supertrend(_mult: float):
        __hist_haClose__: Series = haClose[0]
        src: float = (haHigh + haLow) / 2
        up: PersistentSeries[float] = na(float)
        dn: PersistentSeries[float] = na(float)
        tr: PersistentSeries[int] = 1
        u: float = src - _mult * haATR
        d: float = src + _mult * haATR
        up = u if na(up[1]) else math.max(u, up[1]) if __hist_haClose__[1] > up[1] else u
        dn = d if na(dn[1]) else math.min(d, dn[1]) if __hist_haClose__[1] < dn[1] else d
        tr = 1 if na(tr[1]) else 1 if tr[1] == -1 and haClose > dn[1] else -1 if tr[1] == 1 and haClose < up[1] else tr[1]
        return (up, dn, tr)

    upFast, dnFast, trFast = f_supertrend(i_multF)
    upSlow, dnSlow, trSlow = f_supertrend(i_multS)

    fastMode = i_mode == 'MarketMind'
    trendDir: Series = trFast if fastMode else trSlow
    trendLvl = (upFast if trFast == 1 else dnFast) if fastMode else upSlow if trSlow == 1 else dnSlow

    flipUp = trendDir == 1 and trendDir[1] == -1
    flipDn = trendDir == -1 and trendDir[1] == 1

    def f_tfBias():
        return -1 if close < ta.ema(close, 20) else 1

    def f_tfTrend(tf: str):
        return request.security(syminfo.tickerid, tf, f_tfBias(), lookahead=barmerge.lookahead_off)

    t3m = f_tfTrend('3')
    t5m = f_tfTrend('5')
    t15m = f_tfTrend('15')
    t1h = f_tfTrend('60')
    t4h = f_tfTrend('240')
    t1d = f_tfTrend('D')

    rsiV = ta.rsi(close, 14)
    rsiBull = rsiV > 55
    rsiBear = rsiV < 45
    momBull = haClose > haOpen
    momBear = haClose < haOpen

    bullCnt = (1 if t3m == 1 else 0) + (1 if t5m == 1 else 0) + (1 if t15m == 1 else 0) + (1 if t1h == 1 else 0) + (1 if t4h == 1 else 0) + (1 if t1d == 1 else 0) + (1 if rsiBull else 0) + (1 if momBull else 0)
    bearCnt = (1 if t3m == -1 else 0) + (1 if t5m == -1 else 0) + (1 if t15m == -1 else 0) + (1 if t1h == -1 else 0) + (1 if t4h == -1 else 0) + (1 if t1d == -1 else 0) + (1 if rsiBear else 0) + (1 if momBear else 0)

    bullPct = math.round(bullCnt / 8 * 100)
    bearPct = math.round(bearCnt / 8 * 100)

    def f_ffSeed(slot: str):
        return request.seed('seed_toodegrees_toogit', slot, string.tostring(open) + ',' + string.tostring(high) + ',' + string.tostring(low) + ',' + string.tostring(close) + ',' + string.tostring(volume))

    def f_ffRequest():
        return (f_ffSeed('TOODEGREES_FOREX_FACTORY_SLOT_1'), f_ffSeed('TOODEGREES_FOREX_FACTORY_SLOT_2'), f_ffSeed('TOODEGREES_FOREX_FACTORY_SLOT_3'), f_ffSeed('TOODEGREES_FOREX_FACTORY_SLOT_4'), f_ffSeed('TOODEGREES_FOREX_FACTORY_SLOT_5'), f_ffSeed('TOODEGREES_FOREX_FACTORY_SLOT_6'), f_ffSeed('TOODEGREES_FOREX_FACTORY_SLOT_7'), f_ffSeed('TOODEGREES_FOREX_FACTORY_SLOT_8'), f_ffSeed('TOODEGREES_FOREX_FACTORY_SLOT_9'))

    @method
    def ffRead(N: list[ffUtil.News], S1: str, S2: str, S3: str, S4: str, S5: str, S6: str, S7: str, S8: str, S9: str):
        ffDec.readNews(N, S1)
        ffDec.readNews(N, S2)
        ffDec.readNews(N, S3)
        ffDec.readNews(N, S4)
        ffDec.readNews(N, S5)
        ffDec.readNews(N, S6)
        ffDec.readNews(N, S7)
        ffDec.readNews(N, S8)
        return ffDec.readNews(N, S9)

    def f_ffSize(sz: str):
        return 'Tiny' if sz == 'Tiny / صغير جداً' else 'Small' if sz == 'Small / صغير' else 'Normal' if sz == 'Normal / عادي' else 'Large' if sz == 'Large / كبير' else 'Huge'

    newsOK = timeframe.in_seconds(timeframe.period) <= 86400 and timeframe.in_seconds(timeframe.period) >= 30

    ffMidnight: Persistent[bool] = False
    if hour(time, 'America/New_York') == 0 and hour(time[1], 'America/New_York') != 0 and (not ffMidnight):
        ffMidnight = True
    ffNewDay = hour(time, 'America/New_York') == 0 and hour(time[1], 'America/New_York') != 0 if ffMidnight else timeframe.change('D')

    ffCurr: Persistent[list[ffUtil.News]] = array.new(0, NA(ffUtil.News))
    ffNext: Persistent[list[ffUtil.News]] = array.new(0, NA(ffUtil.News))
    ffDay: Persistent[list[ffUtil.News]] = array.new(0, NA(ffUtil.News))
    ffLoc: Persistent = ffUtil.boxLoc(i_newsH, i_newsV)
    ffImp: Persistent = ffUtil.impFilter(i_newsHol, i_newsLow, i_newsMed, i_newsHigh)

    def f_curOn(c: str):
        return not i_newsCur or syminfo.currency == c or syminfo.basecurrency == c

    ffCurF: Persistent = ffUtil.curFilter(False, f_curOn('AUD'), f_curOn('CAD'), f_curOn('CHF'), f_curOn('CNY'), f_curOn('EUR'), f_curOn('GBP'), f_curOn('JPY'), f_curOn('NZD'), f_curOn('USD'))

    fs1, fs2, fs3, fs4, fs5, fs6, fs7, fs8, fs9 = f_ffRequest()

    if newsOK:
        if timeframe.change('W'):
            ffNext = ffUtil.bubbleSort_News(ffNext)
            if i_tzOn:
                ffNext = ffUtil.adjustTimezone(ffNext, i_tzH, i_tzM)
            if i_newsTime == 'AM/PM':
                ffNext = ffUtil.NewsAMPM_TOD(ffNext)
            ffCurr = udt_copy(ffNext)
            ffCurr = ffUtil.weekNews(ffCurr, ffCurF, ffImp)
            array.clear(ffNext)
        if ffNewDay:
            array.clear(ffDay)
            ffDay = ffUtil.todayNews(ffCurr, ffDay, ffMidnight)
        ffRead(ffNext, fs1, fs2, fs3, fs4, fs5, fs6, fs7, fs8, fs9)

    def f_newsBlackout():
        hit: bool = False
        if i_nbOn and array.size(ffCurr) > 0:
            for i in pine_range(0, array.size(ffCurr) - 1):
                n: ffUtil.News = array.get(ffCurr, i)
                impOK: bool = not i_nbRedOnly or n.imp == color.red
                if impOK and (not na(n.tmst)):
                    if time >= n.tmst - i_nbBefore * 60000 and time <= n.tmst + i_nbAfter * 60000:
                        hit = True
        return hit

    newsBlackout = f_newsBlackout()

    dxyD = request.security('TVC:DXY', 'D', close, ignore_invalid_symbol=True)
    us10D = request.security('TVC:US10Y', 'D', close, ignore_invalid_symbol=True)
    dxyEma = ta.ema(dxyD, i_macroLen)
    us10Ema = ta.ema(us10D, i_macroLen)
    dxyUp = not na(dxyD) and dxyD > dxyEma
    us10Up = not na(us10D) and us10D > us10Ema
    macroUp = dxyUp if i_macroSrc == 'DXY' else us10Up if i_macroSrc == 'US10Y' else dxyUp and us10Up
    macroDown = not dxyUp if i_macroSrc == 'DXY' else not us10Up if i_macroSrc == 'US10Y' else not dxyUp and (not us10Up)

    macroBlockBuy = i_macroOn and macroUp
    macroBlockSell = i_macroOn and macroDown

    cotLong = request.security('COT:' + i_cotCode + '_F_NCP_L', 'W', close, ignore_invalid_symbol=True)
    cotShort = request.security('COT:' + i_cotCode + '_F_NCP_S', 'W', close, ignore_invalid_symbol=True)
    cotNet: Series = nz(cotLong) - nz(cotShort)
    cotRise = cotNet > nz(cotNet[1], cotNet)

    finField = 'TOTAL_REVENUE' if i_finField == 'Revenue' else 'EARNINGS_PER_SHARE_BASIC' if i_finField == 'EPS' else 'NET_INCOME' if i_finField == 'Net income' else 'DEBT_TO_EQUITY'
    finVal = request.financial(syminfo.tickerid, finField, 'FQ', ignore_invalid_symbol=True)

    brkHi = inline_series(ta.highest(high, i_filtLook), 1)
    brkLo = inline_series(ta.lowest(low, i_filtLook), 1)
    filterUp = trendDir == 1 and high > brkHi
    filterDn = trendDir == -1 and low < brkLo

    lastFilt: Persistent[int] = 0
    filterBuy = filterUp and lastFilt != 1
    filterSell = filterDn and lastFilt != -1
    if filterBuy:
        lastFilt = 1
    elif filterSell:
        lastFilt = -1

    rawBuy: bool = False
    rawSell: bool = False
    if i_mode == 'MarketMind + FILTER':
        rawBuy = filterBuy
        rawSell = filterSell
    else:
        rawBuy = flipUp
        rawSell = flipDn

    buySignal: Series = i_sig and rawBuy and (not newsBlackout) and (not macroBlockBuy)
    sellSignal: Series = i_sig and rawSell and (not newsBlackout) and (not macroBlockSell)

    plotshape(low if buySignal and (not i_sigText) else na, 'Buy', shape.triangleup, location.belowbar, SIG_UP, size=size.small)
    plotshape(high if sellSignal and (not i_sigText) else na, 'Sell', shape.triangledown, location.abovebar, SIG_DN, size=size.small)
    plotshape(trendLvl if buySignal and i_sigText else na, 'Buy With Text', shape.labelup, location.absolute, color.new(color.new('#61C1FD'), 54), text='◈BUY', textcolor=chart.fg_color, size=size.small)
    plotshape(trendLvl if sellSignal and i_sigText else na, 'Sell With Text', shape.labeldown, location.absolute, color.new(color.new('#FF0000'), 80), text='◈SELL', textcolor=chart.fg_color, size=size.small)

    CONF_RUN: int = 3
    CONF_TAIL: float = 0.25
    CONF_BODYR: float = 0.3
    CONF_BODY: float = 0.7
    CONF_GAP: int = 6

    haRun: Persistent[int] = 1
    haRun = haRun + 1 if haUp == haUp[1] else 1
    haBody = math.abs(haClose - haOpen)
    haRng = math.max(haHigh - haLow, syminfo.mintick)
    haLowWick = math.min(haOpen, haClose) - haLow
    haUpWick = haHigh - math.max(haOpen, haClose)
    confBase = haRun <= CONF_RUN and haBody >= CONF_BODY * haATR and (haBody >= CONF_BODYR * haRng)
    pullbackUp = trendDir == 1 and haUp and confBase and (haLowWick <= CONF_TAIL * haRng)
    pullbackDn = trendDir == -1 and (not haUp) and confBase and (haUpWick <= CONF_TAIL * haRng)

    confBar: Persistent[int] = -10000
    rawConfUp = pullbackUp and bar_index - confBar >= CONF_GAP
    rawConfDn = pullbackDn and bar_index - confBar >= CONF_GAP
    if rawConfUp or rawConfDn:
        confBar = bar_index

    nearSignal = buySignal or sellSignal or buySignal[1] or sellSignal[1]
    confBuy = i_confirm and rawConfUp and (not nearSignal)
    confSell = i_confirm and rawConfDn and (not nearSignal)
    plotshape(confBuy, 'MarketMind Confirm Buy', shape.circle, location.belowbar, color.new(CONF_UP, 100), text='◆', textcolor=CONF_UP, size=size.tiny)
    plotshape(confSell, 'MarketMind Confirm Sell', shape.circle, location.abovebar, color.new(CONF_DN, 100), text='◆', textcolor=CONF_DN, size=size.tiny)

    alertcondition(confBuy, 'MarketMind Confirm Buy Alert', '{{interval}} - {{ticker}} 🔵 MarketMind Confirm Buy\n')
    alertcondition(confSell, 'MarketMind Confirm Sell Alert', '{{interval}} - {{ticker}} 🔴 MarketMind Confirm Sell\n')

    posDir: Persistent[int] = 0
    entry: Persistent[float] = na(float)
    slLvl: Persistent[float] = na(float)
    geLvl: Persistent[float] = na(float)
    tp1Lvl: Persistent[float] = na(float)
    tp2Lvl: Persistent[float] = na(float)
    tp3Lvl: Persistent[float] = na(float)
    tslLvl: Persistent[float] = na(float)
    tp1Hit: Persistent[bool] = False
    tp2Hit: Persistent[bool] = False
    tp3Hit: Persistent[bool] = False
    entryBar: Persistent[int] = na(int)
    lSL: Persistent[Label] = na(Label)

    if buySignal or sellSignal:
        posDir = 1 if buySignal else -1
        entry = close
        entryBar = bar_index
        slLvl = close - posDir * i_slMult * haATR
        geLvl = close - posDir * i_geM * haATR
        tp1Lvl = close + posDir * i_tp1M * haATR
        tp2Lvl = close + posDir * i_tp2M * haATR
        tp3Lvl = close + posDir * i_tp3M * haATR
        tslLvl = slLvl
        tp1Hit = False
        tp2Hit = False
        tp3Hit = False
        label.delete(lSL)
        if i_slLabel:
            lSL = label.new(bar_index, slLvl, 'SL · ' + string.tostring(slLvl, '#.####'), style=label.style_label_left, color=color.new(SL_COL, 100), textcolor=SL_COL, size=size.normal)

    if i_tsl and posDir != 0:
        trail: float = upSlow if posDir == 1 else dnSlow
        tslLvl = math.max(nz(tslLvl, trail), trail) if posDir == 1 else math.min(nz(tslLvl, trail), trail)

    if posDir == 1:
        if not tp1Hit and high >= tp1Lvl:
            tp1Hit = True
            if i_tpHit:
                label.new(bar_index, na, '✓' + '1', yloc=yloc.abovebar, style=label.style_label_up, color=color.new(TP_COL, 100), textcolor=TP_COL, size=size.tiny)
        if not tp2Hit and high >= tp2Lvl:
            tp2Hit = True
            if i_tpHit:
                label.new(bar_index, na, '✓' + '2', yloc=yloc.abovebar, style=label.style_label_up, color=color.new(TP_COL, 100), textcolor=TP_COL, size=size.tiny)
        if not tp3Hit and high >= tp3Lvl:
            tp3Hit = True
            if i_tpHit:
                label.new(bar_index, na, '✓' + '3', yloc=yloc.abovebar, style=label.style_label_up, color=color.new(TP_COL, 100), textcolor=TP_COL, size=size.tiny)
    if posDir == -1:
        if not tp1Hit and low <= tp1Lvl:
            tp1Hit = True
            if i_tpHit:
                label.new(bar_index, na, '✓' + '1', yloc=yloc.belowbar, style=label.style_label_down, color=color.new(TP_COL, 100), textcolor=TP_COL, size=size.tiny)
        if not tp2Hit and low <= tp2Lvl:
            tp2Hit = True
            if i_tpHit:
                label.new(bar_index, na, '✓' + '2', yloc=yloc.belowbar, style=label.style_label_down, color=color.new(TP_COL, 100), textcolor=TP_COL, size=size.tiny)
        if not tp3Hit and low <= tp3Lvl:
            tp3Hit = True
            if i_tpHit:
                label.new(bar_index, na, '✓' + '3', yloc=yloc.belowbar, style=label.style_label_down, color=color.new(TP_COL, 100), textcolor=TP_COL, size=size.tiny)

    def f_lblSize(n: int):
        return size.tiny if n <= 1 else size.small if n == 2 else size.normal if n == 3 else size.large if n == 4 else size.huge

    lTP1: Persistent[Label] = na(Label)
    lTP2: Persistent[Label] = na(Label)
    lTP3: Persistent[Label] = na(Label)
    lGE: Persistent[Label] = na(Label)
    lTSL: Persistent[Label] = na(Label)
    if barstate.islast and posDir != 0:
        label.delete(lTP1)
        label.delete(lTP2)
        label.delete(lTP3)
        label.delete(lGE)
        label.delete(lTSL)
        dash: str = ""
        if i_tpShow:
            lTP1 = label.new(bar_index, tp1Lvl, dash + 'TP1 · ' + string.tostring(tp1Lvl, '#.####'), style=label.style_label_left, color=color.new(color.white, 100), textcolor=TP_COL, size=f_lblSize(i_lblSize))
            lTP2 = label.new(bar_index, tp2Lvl, dash + 'TP2 · ' + string.tostring(tp2Lvl, '#.####'), style=label.style_label_left, color=color.new(color.white, 100), textcolor=TP_COL, size=f_lblSize(i_lblSize))
            lTP3 = label.new(bar_index, tp3Lvl, dash + 'TP3 · ' + string.tostring(tp3Lvl, '#.####'), style=label.style_label_left, color=color.new(color.white, 100), textcolor=TP_COL, size=f_lblSize(i_lblSize))
        if i_geShow:
            lGE = label.new(bar_index, geLvl, dash + 'GE · ' + string.tostring(geLvl, '#.####'), style=label.style_label_left, color=color.new(GE_COL, 100), textcolor=GE_COL, size=f_lblSize(i_lblSize))
        if i_tsl:
            lTSL = label.new(bar_index + 4, tslLvl, 'TSL · ' + string.tostring(tslLvl, '#.####'), style=label.style_label_left, color=color.new(color.white, 100), textcolor=TSL_COL, size=f_lblSize(i_lblSize))

    rrRisk: Persistent[Box] = na(Box)
    rrRew: Persistent[Box] = na(Box)
    if i_rrBox and barstate.islast and (posDir != 0):
        box.delete(rrRisk)
        box.delete(rrRew)
        rrRisk = box.new(entryBar, entry, bar_index, slLvl, bgcolor=color.new(color.new('#F23645'), 85), border_color=color.new(color.new('#F23645'), 60))
        rrRew = box.new(entryBar, entry, bar_index, tp3Lvl, bgcolor=color.new(color.new('#4CAF50'), 85), border_color=color.new(color.new('#4CAF50'), 60))

    SR_PIVOT: int = 10
    SR_HEIGHT: float = 0.4
    SR_MINGAP: float = 2.0
    SR_EXTEND: int = 50
    SR_LBLOFF: int = 50
    SR_VOLLEN: int = 50
    SR_MAXLIVE: int = 12

    atr50 = ta.atr(50)
    volSma20 = ta.sma(volume, 20)
    atrAvg50 = ta.sma(haATR, 50)

    zKind: Persistent[list[int]] = array.new_int()
    zLvl: Persistent[list[float]] = array.new_float()
    zBox: Persistent[list[Box]] = array.new_box()
    zLbl: Persistent[list[Label]] = array.new_label()
    zVolA: Persistent[list[Box]] = array.new_box()
    zVolB: Persistent[list[Box]] = array.new_box()

    def f_farEnough(kind: int, lvl: float, gap: float):
        ok: bool = True
        if array.size(zLvl) > 0:
            for i in pine_range(0, array.size(zLvl) - 1):
                if array.get(zKind, i) == kind and math.abs(lvl - array.get(zLvl, i)) < gap:
                    ok = False
        return ok

    def f_zoneDrop(i: int):
        box.delete(array.get(zBox, i))
        label.delete(array.get(zLbl, i))
        box.delete(array.get(zVolA, i))
        box.delete(array.get(zVolB, i))
        array.remove(zKind, i)
        array.remove(zLvl, i)
        array.remove(zBox, i)
        array.remove(zLbl, i)
        array.remove(zVolA, i)
        return array.remove(zVolB, i)

    ph = ta.pivothigh(high, SR_PIVOT, SR_PIVOT)
    pl = ta.pivotlow(low, SR_PIVOT, SR_PIVOT)

    upVol = math.sum(volume if close >= open else 0, SR_PIVOT * 2 + 1)
    dnVol = math.sum(volume if close < open else 0, SR_PIVOT * 2 + 1)
    totVol = NA(float) if na(volume) else upVol + dnVol
    sellSh = NA(float) if na(volume) else dnVol / totVol if totVol > 0 else 0.0
    sellLen = math.round(SR_VOLLEN * sellSh)
    buyLen = SR_VOLLEN - sellLen
    volTxtRes = string.tostring(totVol, format.volume) + '  ·  ' + string.tostring(math.round(sellSh * 100)) + '% Sell'
    volTxtSup = string.tostring(totVol, format.volume) + '  ·  ' + string.tostring(math.round((1 - sellSh) * 100)) + '% Buy'

    def f_volBars(piv: int, top: float, bot: float, kind: int):
        draw: bool = i_srVol and totVol > 0
        share: float = sellSh if kind == 1 else 1 - sellSh
        vc: Color = ZONE_SUP if kind == 1 else ZONE_DEM
        ln: int = math.max(math.round(SR_VOLLEN * share), 1)
        alph: int = math.round(84 - 44 * share)
        a: Box = box.new(piv, top, piv + ln, bot, border_color=color.new(vc, math.max(alph - 25, 0)), bgcolor=color.new(vc, alph)) if draw else na
        b: Box = na(Box)
        array.push(zVolA, a)
        return array.push(zVolB, b)

    if i_sr and (not na(atr50)):
        h: float = SR_HEIGHT * atr50
        if not na(ph) and f_farEnough(1, ph, SR_MINGAP * atr50):
            array.push(zKind, 1)
            array.push(zLvl, ph)
            array.push(zBox, box.new(bar_index - SR_PIVOT, ph, bar_index + SR_EXTEND, ph - h, border_color=color.new(ZONE_SUP, 79), bgcolor=color.new(ZONE_SUP, 79), border_width=1))
            array.push(zLbl, label.new(bar_index - SR_PIVOT + SR_LBLOFF, ph - h / 2, volTxtRes, style=label.style_label_left, color=color.new(color.new('#363A45'), 100), textcolor=ZONE_SUP, size=size.small) if i_srVol else na)
            f_volBars(bar_index - SR_PIVOT, ph, ph - h, 1)
        if not na(pl) and f_farEnough(-1, pl, SR_MINGAP * atr50):
            array.push(zKind, -1)
            array.push(zLvl, pl)
            array.push(zBox, box.new(bar_index - SR_PIVOT, pl + h, bar_index + SR_EXTEND, pl, border_color=color.new(color.new('#2AA6E8'), 71), bgcolor=color.new(ZONE_DEM, 78), border_width=1))
            array.push(zLbl, label.new(bar_index - SR_PIVOT + SR_LBLOFF, pl + h / 2, volTxtSup, style=label.style_label_left, color=color.new(color.new('#363A45'), 100), textcolor=ZONE_DEM, size=size.small) if i_srVol else na)
            f_volBars(bar_index - SR_PIVOT, pl + h, pl, -1)

    if array.size(zLvl) > 0:
        for i in pine_range(array.size(zLvl) - 1, 0):
            k: int = array.get(zKind, i)
            v: float = array.get(zLvl, i)
            if k == 1 and close > v or (k == -1 and close < v):
                if i_srBreak:
                    label.new(bar_index, v, '$', style=label.style_label_down if k == 1 else label.style_label_up, color=color.new(color.new('#F02424') if k == 1 else color.new('#2AA6E8'), 40), textcolor=color.white, size=size.tiny)
                f_zoneDrop(i)
            else:
                box.set_right(array.get(zBox, i), bar_index + SR_EXTEND)

    while array.size(zLvl) > SR_MAXLIVE:
        f_zoneDrop(0)

    CH_LEN: int = 100
    chMid = ta.linreg(close, CH_LEN, 0)
    chPrev = ta.linreg(close, CH_LEN, CH_LEN - 1)
    chDev: float = 0.0
    if i_channel and barstate.islast:
        sum: float = 0.0
        slope: float = (chMid - chPrev) / (CH_LEN - 1)
        for i in pine_range(0, CH_LEN - 1):
            fit: float = chMid - slope * i
            sum += math.pow(close[i] - fit, 2)
        chDev = 2 * math.sqrt(sum / CH_LEN)

    chUp: Persistent[Line] = na(Line)
    chLo: Persistent[Line] = na(Line)
    chMidL: Persistent[Line] = na(Line)
    if i_channel and barstate.islast:
        line.delete(chUp)
        line.delete(chLo)
        line.delete(chMidL)
        chUp = line.new(bar_index - CH_LEN + 1, chPrev + chDev, bar_index, chMid + chDev, color=color.new('#787878'), style=line.style_dashed, width=2, extend=extend.right)
        chLo = line.new(bar_index - CH_LEN + 1, chPrev - chDev, bar_index, chMid - chDev, color=color.new('#787878'), style=line.style_dashed, width=2, extend=extend.right)
        chMidL = line.new(bar_index - CH_LEN + 1, chPrev, bar_index, chMid, color=color.new(color.red, 100), width=2, extend=extend.right)

    MM_MA_LEN: int = 34
    plot(ta.ema(close, MM_MA_LEN) if i_ma else na, 'MarketMind MA', color=color.new('#2962FF'), linewidth=2)

    STRUCT_INT: int = 3
    STRUCT_EXT: int = 15
    STRUCT_KEEP: int = 30
    COL_BULL: Color = color.new('#00DDFF')
    COL_BEAR: Color = color.new('#FF004C')

    structLen = STRUCT_EXT if i_structTyp == 'External' else STRUCT_INT
    sPH = ta.pivothigh(high, structLen, structLen)
    sPL = ta.pivotlow(low, structLen, structLen)

    stHigh: Persistent[float] = na(float)
    stHighBar: Persistent[int] = na(int)
    stLow: Persistent[float] = na(float)
    stLowBar: Persistent[int] = na(int)
    lastBreak: Persistent[int] = 0
    STRUCT_STALE: int = 150
    if not na(sPH) and (na(stHigh) or sPH > stHigh or bar_index - nz(stHighBar, 0) > STRUCT_STALE):
        stHigh = sPH
        stHighBar = bar_index - structLen
    if not na(sPL) and (na(stLow) or sPL < stLow or bar_index - nz(stLowBar, 0) > STRUCT_STALE):
        stLow = sPL
        stLowBar = bar_index - structLen

    stLn: Persistent[list[Line]] = array.new_line()
    stLb1: Persistent[list[Label]] = array.new_label()
    stLb2: Persistent[list[Label]] = array.new_label()

    def f_structEvent(bull: bool, lvl: float, pivBar: int, prevDir: int, atrRef: float):
        x1: int = pivBar + 1
        x2: int = bar_index - 1
        col: Color = COL_BULL if bull else COL_BEAR
        txt: str = 'CHoCH' if prevDir != 0 and prevDir != (1 if bull else -1) else 'BoS'
        xm: int = math.floor((x1 + x2) / 2)
        array.push(stLn, line.new(x1, lvl, x2, lvl, color=col, style=line.style_solid, width=1))
        array.push(stLb1, label.new(xm, lvl, txt, style=label.style_none, color=color.new(color.white, 100), textcolor=col))
        array.push(stLb2, label.new(xm, lvl + (1 if bull else -1) * atrRef * 0.08, '●', style=label.style_none, color=color.new(color.white, 100), textcolor=col))
        while array.size(stLn) > STRUCT_KEEP:
            line.delete(array.shift(stLn))
            label.delete(array.shift(stLb1))
            label.delete(array.shift(stLb2))
        return 1 if bull else -1

    if i_struct:
        if not na(stHigh) and close > stHigh:
            lastBreak = f_structEvent(True, stHigh, stHighBar, lastBreak, haATR)
            stHigh = na
        if not na(stLow) and close < stLow:
            lastBreak = f_structEvent(False, stLow, stLowBar, lastBreak, haATR)
            stLow = na

    rngHi: Persistent[float] = na(float)
    rngLo: Persistent[float] = na(float)
    rngHi = rngHi if na(stHigh) else stHigh
    rngLo = rngLo if na(stLow) else stLow
    lb1: Persistent[Label] = na(Label)
    lb0: Persistent[Label] = na(Label)
    if (i_struct or i_fib) and barstate.islast and (not na(rngHi)) and (not na(rngLo)):
        label.delete(lb1)
        label.delete(lb0)
        lb1 = label.new(bar_index + 10, rngHi, '1', style=label.style_none, color=color.new(color.white, 100), textcolor=COL_BULL)
        lb0 = label.new(bar_index + 10, rngLo, '0', style=label.style_none, color=color.new(color.white, 100), textcolor=COL_BEAR)

    ePH = ta.pivothigh(high, STRUCT_EXT, STRUCT_EXT)
    ePL = ta.pivotlow(low, STRUCT_EXT, STRUCT_EXT)
    exHi: Persistent[float] = na(float)
    exHiBar: Persistent[int] = na(int)
    exLo: Persistent[float] = na(float)
    exLoBar: Persistent[int] = na(int)
    if not na(ePH) and (na(exHi) or ePH > exHi or bar_index - nz(exHiBar, 0) > STRUCT_STALE):
        exHi = ePH
        exHiBar = bar_index - STRUCT_EXT
    if not na(ePL) and (na(exLo) or ePL < exLo or bar_index - nz(exLoBar, 0) > STRUCT_STALE):
        exLo = ePL
        exLoBar = bar_index - STRUCT_EXT

    fibLn: Persistent[list[Line]] = array.new_line()
    fibLb: Persistent[list[Label]] = array.new_label()

    def f_drawFib(hi: float, lo: float, startBar: int):
        rng: float = hi - lo
        __block_result__ = na
        for k in pine_range(0, 4):
            ratio: float = array.get(array.from_items(0.236, 0.382, 0.5, 0.618, 0.786), k)
            col: Color = color.new('#FFBE3B') if ratio == 0.5 else color.new('#C4E600') if ratio == 0.382 or ratio == 0.618 else color.new(color.white, 100)
            lvl: float = lo + rng * ratio
            if ratio != 0.236 and ratio != 0.786:
                array.push(fibLn, line.new(startBar, lvl, bar_index + 10, lvl, color=col, style=line.style_dotted, width=1))
            __block_result__ = array.push(fibLb, label.new(bar_index + 10, lvl, string.tostring(ratio, '0.000' if ratio == 0.5 else '0.###'), style=label.style_none, color=color.new(color.white, 100), textcolor=col))
        return __block_result__

    if i_fib and barstate.islast:
        for ln in fibLn:
            line.delete(ln)
        for lx in fibLb:
            label.delete(lx)
        array.clear(fibLn)
        array.clear(fibLb)
        wantInt: bool = i_fibType == 'Internal' or i_fibType == 'Both'
        wantExt: bool = i_fibType == 'External' or i_fibType == 'Both'
        if wantInt and (not na(rngHi)) and (not na(rngLo)):
            f_drawFib(rngHi, rngLo, math.max(nz(stHighBar, bar_index), nz(stLowBar, bar_index)) - 1)
        if wantExt and (not na(exHi)) and (not na(exLo)):
            f_drawFib(exHi, exLo, math.max(nz(exHiBar, bar_index), nz(exLoBar, bar_index)) - 1)

    COL_PDHL: Color = color.new('#21D7F3')
    def f_prevExtreme(tf: str):
        prevHi, prevLo = request.security(syminfo.tickerid, tf, (high[1], low[1]), lookahead=barmerge.lookahead_on)
        return (prevHi, prevLo)

    pdh, pdl = f_prevExtreme('D')
    pwh, pwl = f_prevExtreme('W')

    lPDH: Persistent[Line] = na(Line)
    lPDL: Persistent[Line] = na(Line)
    lPWH: Persistent[Line] = na(Line)
    lPWL: Persistent[Line] = na(Line)
    tPDH: Persistent[Label] = na(Label)
    tPDL: Persistent[Label] = na(Label)
    tPWH: Persistent[Label] = na(Label)
    tPWL: Persistent[Label] = na(Label)
    def f_hline(ln: Line, lx: Label, on: bool, lvl: float, txt: str, back: int):
        line.delete(ln)
        label.delete(lx)
        nl: Line = line.new(bar_index - back, lvl, bar_index, lvl, color=color.new(COL_PDHL, 31), style=line.style_dashed, width=1) if on and (not na(lvl)) else na
        nx: Label = label.new(bar_index, lvl, txt, style=label.style_label_left, color=color.new(COL_PDHL, 100), textcolor=color.new(COL_PDHL, 31)) if on and (not na(lvl)) else na
        return (nl, nx)

    if barstate.islast:
        a1, a2 = f_hline(lPDH, tPDH, i_pdhl, pdh, 'PDH', 10)
        lPDH = a1
        tPDH = a2
        b1, b2 = f_hline(lPDL, tPDL, i_pdhl, pdl, 'PDL', 10)
        lPDL = b1
        tPDL = b2
        c1__0000022c__, c2__0000022c__ = f_hline(lPWH, tPWH, i_pwhl, pwh, 'PWH', 45)
        lPWH = c1__0000022c__
        tPWH = c2__0000022c__
        d1, d2 = f_hline(lPWL, tPWL, i_pwhl, pwl, 'PWL', 45)
        lPWL = d1
        tPWL = d2

    newDay = timeframe.change('D')
    newWeek = timeframe.change('W')
    if i_dayDiv and newDay or (i_weekDiv and newWeek):
        line.new(bar_index, 10000000000, bar_index, -10000000000, color=color.new('#DDDDDD'), style=line.style_dashed, width=1, xloc=xloc.bar_index)

    nxUp: Persistent[Label] = na(Label)
    nxDn: Persistent[Label] = na(Label)
    if i_nextPct and barstate.islast:
        label.delete(nxUp)
        label.delete(nxDn)
        win: int = 100
        hu: int = 0
        ld: int = 0
        for k in pine_range(1, win):
            hu += 1 if high[k] > high[k + 1] else 0
            ld += 1 if low[k] < low[k + 1] else 0
        nxUp = label.new(bar_index + 1, high[1], string.tostring(hu / win * 100, '#.##') + '%', style=label.style_label_left, color=color.new(color.new('#363A45'), 100), textcolor=color.new('#059AE4'))
        nxDn = label.new(bar_index + 1, low[1], string.tostring(ld / win * 100, '#.##') + '%', style=label.style_label_left, color=color.new(color.new('#363A45'), 100), textcolor=color.new('#F23645'))

    VP_ROWS: int = 8
    VP_MAXLEN: int = 50

    def f_htf10(src: Series[float]):
        return (src, src[1], src[2], src[3], src[4], src[5], src[6], src[7], src[8], src[9])

    o0, o1, o2, o3, o4, o5, o6, o7, o8, o9 = request.security(syminfo.tickerid, i_htfTF, f_htf10(open), lookahead=barmerge.lookahead_off)
    h0, h1, h2, h3, h4, h5, h6, h7, h8, h9 = request.security(syminfo.tickerid, i_htfTF, f_htf10(high), lookahead=barmerge.lookahead_off)
    l0, l1, l2, l3, l4, l5, l6, l7, l8, l9 = request.security(syminfo.tickerid, i_htfTF, f_htf10(low), lookahead=barmerge.lookahead_off)
    c0, c1, c2, c3, c4, c5, c6, c7, c8, c9 = request.security(syminfo.tickerid, i_htfTF, f_htf10(close), lookahead=barmerge.lookahead_off)
    htfOpens = array.from_items(o0, o1, o2, o3, o4, o5, o6, o7, o8, o9)
    htfHighs = array.from_items(h0, h1, h2, h3, h4, h5, h6, h7, h8, h9)
    htfLows = array.from_items(l0, l1, l2, l3, l4, l5, l6, l7, l8, l9)
    htfCloses = array.from_items(c0, c1, c2, c3, c4, c5, c6, c7, c8, c9)
    htfO2 = o0
    htfH2 = h0
    htfL2 = l0
    htfC2 = c0
    htfBx: Persistent[list[Box]] = array.new_box()
    if (i_htf or i_htfVP) and barstate.islast and (not na(htfH2)):
        for bx in htfBx:
            box.delete(bx)
        array.clear(htfBx)
        if i_htf:
            for k in pine_range(0, i_htfCount - 1):
                ko: float = array.get(htfOpens, k)
                kh: float = array.get(htfHighs, k)
                kl: float = array.get(htfLows, k)
                kc: float = array.get(htfCloses, k)
                if not na(kh):
                    x0: int = bar_index + 36 - k * 4
                    kcol: Color = color.new('#00C0E6') if kc >= ko else color.new('#FF5252')
                    array.push(htfBx, box.new(x0, math.max(ko, kc), x0 + 2, math.min(ko, kc), border_color=color.new(color.black, 100), bgcolor=color.new(kcol, 10)))
                    array.push(htfBx, box.new(x0 + 1, kh, x0 + 1, kl, border_color=color.new(kcol, 10), bgcolor=color.new(kcol, 10)))
        if i_htfVP:
            rowH: float = (htfH2 - htfL2) / VP_ROWS
            maxV: float = 0.0
            for r in pine_range(0, VP_ROWS - 1):
                lo2: float = htfL2 + rowH * r
                hi2: float = lo2 + rowH
                vv: float = 0.0
                for k in pine_range(0, 199):
                    if high[k] >= lo2 and low[k] <= hi2:
                        vv += nz(volume[k])
                maxV = math.max(maxV, vv)
            for r in pine_range(0, VP_ROWS - 1):
                lo2: float = htfL2 + rowH * r
                hi2: float = lo2 + rowH
                vv: float = 0.0
                for k in pine_range(0, 199):
                    if high[k] >= lo2 and low[k] <= hi2:
                        vv += nz(volume[k])
                sh: float = vv / maxV if maxV > 0 else 0
                array.push(htfBx, box.new(bar_index + 39, hi2, bar_index + 39 + math.round(VP_MAXLEN * sh), lo2, border_color=color.new('#161A25'), bgcolor=color.new(color.new('#00C0E6'), math.round(100 - 90 * sh))))

    plotcandle(haOpen if haUp else na, haHigh if haUp else na, haLow if haUp else na, haClose if haUp else na, 'MarketMind HA Up', color=color.new(color.new('#4CAF4F'), 100), wickcolor=color.new(color.new('#4CAF4F'), 100), bordercolor=color.new(color.new('#4CAF4F'), 100))
    plotcandle(haOpen if not haUp else na, haHigh if not haUp else na, haLow if not haUp else na, haClose if not haUp else na, 'MarketMind HA Down', color=color.new(color.new('#FF5252'), 100), wickcolor=color.new(color.new('#FF5252'), 100), bordercolor=color.new(color.new('#FF5252'), 100))
    barcolor((i_colUp if trendDir == 1 else i_colDn) if i_paint else na, title='Trend Bars')

    paintCol = i_colUp if trendDir == 1 else i_colDn
    plotcandle(open if i_paint else na, high if i_paint else na, low if i_paint else na, close if i_paint else na, 'Trend Candles', color=paintCol, wickcolor=paintCol, bordercolor=paintCol)

    plot(trendLvl if trendDir == 1 else na, 'Up Trend', color=color.new(color.new('#288CB1'), 100), linewidth=2, style=plot.style_linebr)
    plot(trendLvl if trendDir == -1 else na, 'Down Trend', color=color.new(color.new('#DC9FE0'), 100), linewidth=2, style=plot.style_linebr)

    def f_tblSize(s: str):
        return size.tiny if s == 'Tiny / صغير جداً' else size.small if s == 'Small / صغير' else size.normal if s == 'Normal / عادي' else size.large if s == 'Large / كبير' else size.huge

    def f_pos(v: str, h: str):
        return position.top_left if v == 'top' and h == 'left' else position.top_center if v == 'top' and h == 'center' else position.top_right if v == 'top' else position.middle_left if v == 'middle' and h == 'left' else position.middle_center if v == 'middle' and h == 'center' else position.middle_right if v == 'middle' else position.bottom_left if h == 'left' else position.bottom_center if h == 'center' else position.bottom_right

    TB_DARK: bool = i_tblTheme == 'Dark / خلفية سوداء'
    TB_BG: Color = color.new('#000000') if TB_DARK else color.new('#111111')
    TB_FRAME: Color = color.new('#3A4150') if TB_DARK else color.new('#2A2E39')
    TB_BORDER: Color = color.new('#0A0A0A') if TB_DARK else color.new('#1A1A1A')
    TB_TITLE: Color = color.new('#4DD0FF') if TB_DARK else color.new('#61C1FD')
    TB_HEAD: Color = color.new('#9AA4B2') if TB_DARK else color.new('#555555')
    TB_HEADBG: Color = color.new(color.new('#2A2E39'), 55) if TB_DARK else color.new(color.new('#1A1A1A'), 85)
    TB_DIM: Color = color.new('#C3C9D4') if TB_DARK else color.new('#787B86')
    TB_DIM2: Color = color.new('#C3C9D4') if TB_DARK else color.new('#555555')
    TB_LABEL: Color = color.new('#FFFFFF') if TB_DARK else color.new('#CCCCCC')
    TB_ROWBG: Color = color.new(color.new('#20242E'), 60) if TB_DARK else color.new(color.new('#1A1A1A'), 85)
    TB_DEEPBG: Color = color.new('#050505') if TB_DARK else color.new('#0D0D0D')
    TB_SEP: Color = color.new('#2F3542') if TB_DARK else color.new('#333333')
    TB_UP: Color = color.new('#00E676') if TB_DARK else color.new('#4CAF50')
    TB_DN: Color = color.new('#FF5252') if TB_DARK else color.new('#F23645')
    TB_ON: Color = color.new('#4DD0FF') if TB_DARK else color.new('#61C1FD')
    TB_OFF: Color = color.new('#8B93A1') if TB_DARK else color.new('#787B86')
    TB_OFF2: Color = color.new('#8B93A1') if TB_DARK else color.new('#FF5252')
    TB_SESS_A: int = 68 if TB_DARK else 85
    TB_SESS_I: int = 92 if TB_DARK else 85
    TB_SESSA2: int = 68 if TB_DARK else 88
    TB_SESSI2: int = 92 if TB_DARK else 88
    TB_BULLV: Color = color.new('#00E676') if TB_DARK else color.new(color.new('#888888'), 30)
    TB_BEARV: Color = color.new('#FF5252') if TB_DARK else color.new(color.new('#FF5252'), 50)
    TB_JUDGEA: int = 0 if TB_DARK else 40

    def f_moneyTxt():
        r: float = na if na(volume) or volSma20 <= 0 else volume / volSma20
        return '—' if na(r) else 'V.Low' if r < 0.2 else 'Low' if r < 0.6 else 'Normal' if r < 1.0 else 'High' if r < 1.25 else 'V.High'

    def f_volaTxt():
        r: float = na if atrAvg50 <= 0 else haATR / atrAvg50
        return '—' if na(r) else 'Low' if r < 0.7 else 'High' if r > 1.6 else 'Neutral'

    def f_arrow(t: int):
        return '▲' if t == 1 else '▼'

    def f_arrowCol(t: int):
        return TB_UP if t == 1 else TB_DN

    def f_bar(pct: int):
        filled: int = math.round(pct / 20.0)
        return string.repeat('▰', math.max(filled, 0)) + string.repeat('▱', math.max(5 - filled, 0))

    inNY = not na(time(timeframe.period, '1300-2200'))
    inLON = not na(time(timeframe.period, '0800-1700'))
    inTYO = not na(time(timeframe.period, '0000-0900'))
    inSYD = not na(time(timeframe.period, '2200-0700'))

    mmTbl: Persistent[Table] = na(Table)
    if i_table and barstate.islast:
        table.delete(mmTbl)
        extraRows: int = (1 if i_cotOn else 0) + (1 if i_finOn else 0)
        mmTbl = table.new(f_pos(i_tblV, i_tblH), 5, 10 + extraRows, bgcolor=TB_BG, frame_color=TB_FRAME, frame_width=1, border_color=TB_BORDER, border_width=1)
        sz = f_tblSize(i_tblSize)
        table.cell(mmTbl, 0, 0, 'SATTAM | MarketMind', text_color=TB_TITLE, bgcolor=TB_BG, text_size=sz, text_halign=text.align_center)
        table.merge_cells(mmTbl, 0, 0, 4, 0)
        for c in pine_range(0, 4):
            table.cell(mmTbl, c, 1, array.get(array.from_items('Frame', 'HTF', 'Gauge', 'Reading', 'Session'), c), text_color=TB_HEAD, bgcolor=TB_HEADBG, text_size=sz)
        table.cell(mmTbl, 0, 2, '3m ' + f_arrow(t3m), text_color=f_arrowCol(t3m), text_size=sz)
        table.cell(mmTbl, 1, 2, '1h ' + f_arrow(t1h), text_color=f_arrowCol(t1h), text_size=sz)
        table.cell(mmTbl, 2, 2, 'FIB', text_color=TB_DIM2, text_size=sz)
        table.cell(mmTbl, 3, 2, '—', text_color=TB_DIM2, text_size=sz)
        table.cell(mmTbl, 4, 2, 'NY', text_color=TB_ON if inNY else TB_OFF, bgcolor=color.new(TB_ON if inNY else TB_OFF, TB_SESS_A if inNY else TB_SESS_I), text_size=sz)
        table.cell(mmTbl, 0, 3, '5m ' + f_arrow(t5m), text_color=f_arrowCol(t5m), text_size=sz)
        table.cell(mmTbl, 1, 3, '4h ' + f_arrow(t4h), text_color=f_arrowCol(t4h), text_size=sz)
        table.cell(mmTbl, 2, 3, 'VOL', text_color=TB_DIM, text_size=sz)
        table.cell(mmTbl, 3, 3, f_volaTxt(), text_color=TB_DIM, text_size=sz)
        table.cell(mmTbl, 4, 3, 'LON', text_color=TB_ON if inLON else TB_OFF2, bgcolor=color.new(TB_ON if inLON else TB_OFF2, TB_SESSA2 if inLON else TB_SESSI2), text_size=sz)
        table.cell(mmTbl, 0, 4, '15m ' + f_arrow(t15m), text_color=f_arrowCol(t15m), text_size=sz)
        table.cell(mmTbl, 1, 4, 'D ' + f_arrow(t1d), text_color=f_arrowCol(t1d), text_size=sz)
        table.cell(mmTbl, 2, 4, 'RSI', text_color=TB_DIM, text_size=sz)
        table.cell(mmTbl, 3, 4, string.tostring(math.round(rsiV)) + (' OB' if rsiV > 70 else ' OS' if rsiV < 30 else ' Neutral'), text_color=TB_DIM, text_size=sz)
        table.cell(mmTbl, 4, 4, 'TYO', text_color=TB_ON if inTYO else TB_OFF2, bgcolor=color.new(TB_ON if inTYO else TB_OFF2, TB_SESSA2 if inTYO else TB_SESSI2), text_size=sz)
        shortAvg: int = 1 if t3m + t5m + t15m >= 0 else -1
        longAvg: int = 1 if t1h + t4h + t1d >= 0 else -1
        table.cell(mmTbl, 0, 5, 'AVG ' + f_arrow(shortAvg), text_color=f_arrowCol(shortAvg), bgcolor=TB_ROWBG, text_size=sz)
        table.cell(mmTbl, 1, 5, 'AVG ' + f_arrow(longAvg), text_color=f_arrowCol(longAvg), bgcolor=TB_ROWBG, text_size=sz)
        table.cell(mmTbl, 2, 5, '$$$', text_color=TB_DIM, bgcolor=TB_ROWBG, text_size=sz)
        table.cell(mmTbl, 3, 5, f_moneyTxt(), text_color=TB_DIM, bgcolor=TB_ROWBG, text_size=sz)
        table.cell(mmTbl, 4, 5, 'SYD', text_color=TB_ON if inSYD else TB_OFF2, bgcolor=color.new(TB_ON if inSYD else TB_OFF2, TB_SESSA2 if inSYD else TB_SESSI2), text_size=sz)
        table.cell(mmTbl, 0, 6, string.repeat('╌', 44), text_color=TB_SEP, text_size=sz)
        table.merge_cells(mmTbl, 0, 6, 4, 6)
        table.cell(mmTbl, 0, 7, 'BULL', text_color=TB_LABEL, text_size=sz)
        table.cell(mmTbl, 1, 7, string.tostring(bullCnt) + '/8 ' + string.tostring(bullPct) + '% ' + f_bar(bullPct), text_color=TB_BULLV, text_size=sz, text_halign=text.align_left)
        table.merge_cells(mmTbl, 1, 7, 4, 7)
        table.cell(mmTbl, 0, 8, 'BEAR', text_color=TB_LABEL, text_size=sz)
        table.cell(mmTbl, 1, 8, string.tostring(bearCnt) + '/8 ' + string.tostring(bearPct) + '% ' + f_bar(bearPct), text_color=TB_BEARV, text_size=sz, text_halign=text.align_left)
        table.merge_cells(mmTbl, 1, 8, 4, 8)
        dom: int = math.max(bullCnt, bearCnt)
        domDir: str = 'LONG' if bullCnt >= bearCnt else 'SHORT'
        arrow: str = '▲' if bullCnt >= bearCnt else '▼'
        side: str = 'BULL' if bullCnt >= bearCnt else 'BEAR'
        judge: str = arrow + ' STRONG ' + side if dom >= 7 else arrow + ' MODERATE ' + side if dom >= 5 else arrow + ' SLIGHT ' + side if dom >= 3 else '— NEUTRAL'
        table.cell(mmTbl, 0, 9, 'JUDGE', text_color=TB_LABEL, bgcolor=TB_DEEPBG, text_size=sz)
        table.cell(mmTbl, 1, 9, judge, text_color=color.new(TB_UP if bullCnt >= bearCnt else TB_DN, TB_JUDGEA), bgcolor=TB_DEEPBG, text_size=sz, text_halign=text.align_left)
        table.merge_cells(mmTbl, 1, 9, 4, 9)

        r: int = 10
        if i_cotOn:
            table.cell(mmTbl, 0, r, 'COT', text_color=TB_LABEL, bgcolor=TB_DEEPBG, text_size=sz)
            cotTxt: str = '— لا بيانات لهذا الرمز' if na(cotLong) or na(cotShort) else ('▲ ' if cotRise else '▼ ') + string.tostring(cotNet, format.volume) + ' net'
            table.cell(mmTbl, 1, r, cotTxt, text_color=TB_DIM if na(cotLong) else TB_UP if cotRise else TB_DN, bgcolor=TB_DEEPBG, text_size=sz, text_halign=text.align_left)
            table.merge_cells(mmTbl, 1, r, 4, r)
            r += 1
        if i_finOn:
            table.cell(mmTbl, 0, r, 'FIN', text_color=TB_LABEL, bgcolor=TB_DEEPBG, text_size=sz)
            finTxt: str = '— ليس سهماً' if na(finVal) else i_finField + ': ' + string.tostring(finVal, format.volume)
            table.cell(mmTbl, 1, r, finTxt, text_color=TB_DIM if na(finVal) else TB_ON, bgcolor=TB_DEEPBG, text_size=sz, text_halign=text.align_left)
            table.merge_cells(mmTbl, 1, r, 4, r)

    FF_HEAD_TXT = color.new(color.new('#DEE1E9'), 100)
    FF_HEAD_BG = color.new(color.new('#283C70'), 100)
    FF_ROW_TXT: Color = color.new('#00CCFF')
    FF_ROW_BG = color.new(color.new('#DEE1E9'), 100)
    FF_BORDER: Color = chart.fg_color
    ffTable: Persistent[Table] = ffUtil.newTable(ffLoc, FF_BORDER)
    if newsOK and i_news and (array.size(ffCurr) > 0):
        dailyType: str = 'This Week' if timeframe.period == 'D' else i_newsType
        if dailyType == 'Today':
            if ffNewDay:
                ffTable = ffUtil.FF_Table(ffDay, ffLoc, f_ffSize(i_newsSize), FF_HEAD_TXT, FF_HEAD_BG, FF_ROW_TXT, FF_ROW_BG, FF_BORDER)
            ffUtil.timeline(ffDay, ffTable, FF_ROW_TXT, i_tzH, i_tzM, True)
        else:
            if timeframe.change('W'):
                ffTable = ffUtil.FF_Table(ffCurr, ffLoc, f_ffSize(i_newsSize), FF_HEAD_TXT, FF_HEAD_BG, FF_ROW_TXT, FF_ROW_BG, FF_BORDER)
            ffUtil.timeline(ffCurr, ffTable, FF_ROW_TXT, i_tzH, i_tzM)
    else:
        table.delete(ffTable)

    alertcondition(buySignal, 'MarketMind Buy Alert', '{{interval}} - {{ticker}} 🔵 MarketMind Buy\n')
    alertcondition(sellSignal, 'MarketMind Sell Alert', '{{interval}} - {{ticker}} 🔴 MarketMind Sell\n')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)