"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_float, cast_int
from pynecore.lib import (
    alert, array, bar_index, barmerge, barstate, box, close, color, high,
    input, label, line, low, math, na, nz, open, order, plotcandle, position, request, script,
    size, string, syminfo, ta, table, text, timeframe
)
from pynecore.types import Box, Color, Label, Line, Persistent, Series, Table

gM: str = "Entry model"
gW1: str = "Watchlist  1 – 10"
gW2: str = "Watchlist  11 – 20"
gV: str = "Visuals"


@script.indicator("ICT Setup Screener, Liquidity Sweep, MSS & FVG Scanner [LunqFX]", "ICT Screener", overlay=True)
def main(
    scanTF=input.timeframe("", "Scan timeframe", group=gM, tooltip="Blank = the chart's timeframe. Set a fixed one (15, 60) so the table reads the same on any chart you open. Rows on a higher timeframe update when that timeframe's bar closes."),
    pivLen=input.int(8, "Liquidity swing length", minval=2, maxval=50, group=gM, tooltip="Which swings hold the stops that get swept. Higher = only major liquidity."),
    intLen=input.int(3, "Internal structure length", minval=1, maxval=20, group=gM, tooltip="The short-term swing whose break confirms the shift after the sweep."),
    maxWait=input.int(20, "Max bars sweep → MSS", minval=3, maxval=100, group=gM, tooltip="If structure does not shift within this many bars the sweep is discarded."),
    lifeN=input.int(30, "Max bars setup → entry", minval=3, maxval=200, group=gM, tooltip="A mapped setup that price never returns to within this many bars is dropped."),
    openN=input.int(80, "Max bars in trade", minval=5, maxval=500, group=gM, tooltip="An entered setup that has touched neither stop nor target within this many bars is retired from the table. The screener is for finding setups, not for babysitting a position for a week."),
    rrMult=input.float(2.0, "Take profit (R)", minval=0.5, maxval=10, step=0.5, group=gM),
    minRisk=input.float(0.2, "Min stop distance (× ATR)", minval=0.0, maxval=2.0, step=0.05, group=gM),
    minQual=input.int(0, "Hide setups below quality", minval=0, maxval=90, group=gM),
    s01=input.symbol("OANDA:EURUSD", "1", group=gW1),
    s02=input.symbol("OANDA:GBPUSD", "2", group=gW1),
    s03=input.symbol("OANDA:USDJPY", "3", group=gW1),
    s04=input.symbol("OANDA:AUDUSD", "4", group=gW1),
    s05=input.symbol("OANDA:USDCAD", "5", group=gW1),
    s06=input.symbol("OANDA:XAUUSD", "6", group=gW1),
    s07=input.symbol("OANDA:XAGUSD", "7", group=gW1),
    s08=input.symbol("OANDA:NZDUSD", "8", group=gW1),
    s09=input.symbol("OANDA:USDCHF", "9", group=gW1),
    s10=input.symbol("OANDA:EURGBP", "10", group=gW1),
    s11=input.symbol("BINANCE:BTCUSDT", "11", group=gW2),
    s12=input.symbol("BINANCE:ETHUSDT", "12", group=gW2),
    s13=input.symbol("BINANCE:SOLUSDT", "13", group=gW2),
    s14=input.symbol("CME_MINI:ES1!", "14", group=gW2),
    s15=input.symbol("CME_MINI:NQ1!", "15", group=gW2),
    s16=input.symbol("TVC:DXY", "16", group=gW2),
    s17=input.symbol("TVC:NDX", "17", group=gW2),
    s18=input.symbol("TVC:SPX", "18", group=gW2),
    s19=input.symbol("OANDA:EURJPY", "19", group=gW2),
    s20=input.symbol("OANDA:GBPJPY", "20", group=gW2),
    nRows=input.int(20, "Rows in use", minval=1, maxval=20, group=gW2, tooltip="Only the first N symbols are scanned and shown. Lower it for a shorter table."),
    candSty=input.string("Neon Bloom", "Candle palette", options=("Neon Bloom", "Midnight Cyan", "Vibrant Neon", "Classic Soft", "Cool Blue", "Off"), group=gV),
    hudPos=input.string("Top Right", "Table position", options=("Top Right", "Top Left", "Bottom Right", "Bottom Left", "Middle Right", "Middle Left"), group=gV),
    hudSize=input.string("Normal", "Table text", options=("Small", "Normal", "Large"), group=gV),
    drawMe=input.bool(True, "Draw this chart's setup", group=gV, tooltip="The sequence is also run on the chart you are looking at and its live stage is drawn on the candles: the swept level, the shift level, the entry with stop and target. Twenty rows in the table, one setup on the chart."),
    hideIdle=input.bool(False, "Hide SCANNING rows", group=gV, tooltip="Show only symbols with something in progress."),
    alertOn=input.bool(True, "Alert on new setup / entry", group=gV, tooltip="Fires one alert per bar naming the symbol and stage. Create the alert with 'Any alert() function call'."),
    alertSw=input.bool(True, "Also alert on sweep", group=gV, tooltip="An early heads-up when liquidity is swept, before the shift confirms. Not every sweep becomes a setup — it tells you which chart to open.")
):
    UP: Color = color.new('#00F5D4')
    DN: Color = color.new('#FF2E88')
    AMBER: Color = color.new('#FBBF24')
    INK: Color = color.new('#0B0E14')
    CARD: Color = color.new('#131A24')
    CARD2: Color = color.new('#1B2431')
    TXT: Color = color.new('#F1F5F9')
    MUTE: Color = color.new('#94A3B8')
    DIMTX: Color = color.new('#5B6B80')



    def scan():
        atr = ta.atr(14)
        ph = ta.pivothigh(pivLen, pivLen)
        pl = ta.pivotlow(pivLen, pivLen)
        iph = ta.pivothigh(intLen, intLen)
        ipl = ta.pivotlow(intLen, intLen)

        swHigh: Persistent[float] = na(float)
        swLow: Persistent[float] = na(float)
        hiTaken: Persistent[bool] = False
        loTaken: Persistent[bool] = False
        if not na(ph):
            swHigh = ph
            hiTaken = False
        if not na(pl):
            swLow = pl
            loTaken = False

        intHigh: Persistent[float] = na(float)
        intLow: Persistent[float] = na(float)
        if not na(iph):
            intHigh = iph
        if not na(ipl):
            intLow = ipl

        stage: Persistent[int] = 0
        dir: Persistent[int] = 0
        sweepExt: Persistent[float] = na(float)
        sweptLvl: Persistent[float] = na(float)
        mssLevel: Persistent[float] = na(float)
        waited: Persistent[int] = 0
        age: Persistent[int] = 0
        entry: Persistent[float] = na(float)
        sl: Persistent[float] = na(float)
        tp: Persistent[float] = na(float)
        qual: Persistent[int] = 0
        holdN: Persistent[int] = 0

        if barstate.isconfirmed:
            age += 1

            if stage >= 4:
                holdN += 1
                if holdN > 8:
                    stage = 0
                    dir = 0
                    age = 0

            if stage == 0:
                if not na(swLow) and (not loTaken) and (low < swLow) and (close > swLow) and (not na(intHigh)) and (intHigh > close):
                    loTaken = True
                    stage = 1
                    dir = 1
                    sweepExt = low
                    sweptLvl = swLow
                    mssLevel = intHigh
                    waited = 0
                    age = 0
                elif not na(swHigh) and (not hiTaken) and (high > swHigh) and (close < swHigh) and (not na(intLow)) and (intLow < close):
                    hiTaken = True
                    stage = 1
                    dir = -1
                    sweepExt = high
                    sweptLvl = swHigh
                    mssLevel = intLow
                    waited = 0
                    age = 0
            elif stage == 1:
                waited += 1

                failed = close < sweepExt if dir == 1 else close > sweepExt
                if waited > maxWait or failed:
                    stage = 0
                    dir = 0
                    age = 0
                elif dir == 1 and close > mssLevel or (dir == -1 and close < mssLevel):
                    fvgT: float = 0.0
                    fvgB: float = 0.0
                    fvgAt = -1
                    span = math.min(waited + 4, 18)
                    for j in pine_range(0, span):
                        if fvgAt < 0:
                            if dir == 1 and low[j] > high[j + 2]:
                                fvgT = low[j]
                                fvgB = high[j + 2]
                                fvgAt = j
                            if dir == -1 and high[j] < low[j + 2]:
                                fvgT = low[j + 2]
                                fvgB = high[j]
                                fvgAt = j
                    e = (fvgT if dir == 1 else fvgB) if fvgAt >= 0 else mssLevel
                    s = sweepExt
                    risk = math.abs(e - s)
                    a = math.max(nz(atr), syminfo.mintick)
                    depth = math.abs(sweepExt - sweptLvl) / a
                    disp = math.abs(close - mssLevel) / a
                    fSize = math.abs(fvgT - fvgB) / a if fvgAt >= 0 else 0.0
                    q = cast_int(math.round(0.3 * math.min(1.0, depth / 0.45) * 100 + 0.3 * math.min(1.0, disp / 1.2) * 100 + 0.25 * math.min(1.0, fSize / 0.4) * 100 + 0.15 * math.max(0.0, 1.0 - waited / cast_float(maxWait)) * 100))
                    valid = risk > a * minRisk and (e > s if dir == 1 else e < s) and (q >= minQual)
                    if valid:
                        stage = 2
                        entry = e
                        sl = s
                        tp = e + risk * rrMult if dir == 1 else e - risk * rrMult
                        qual = q
                        age = 0
                    else:
                        stage = 0
                        dir = 0
                        age = 0
            elif stage == 2:
                broken = close < sl if dir == 1 else close > sl
                if age > lifeN or broken:
                    stage = 0
                    dir = 0
                    age = 0
                elif dir == 1 and low <= entry or (dir == -1 and high >= entry):
                    stage = 3
                    age = 0
                    holdN = 0
            elif stage == 3:
                hitSL = low <= sl if dir == 1 else high >= sl
                hitTP = high >= tp if dir == 1 else low <= tp

                if hitSL:
                    stage = 5
                    holdN = 0
                    age = 0
                elif hitTP:
                    stage = 4
                    holdN = 0
                    age = 0
                elif age > openN:
                    stage = 0
                    dir = 0
                    age = 0

        risk0 = math.abs(entry - sl)
        toEn = close - entry if dir == 1 else entry - close
        prog = toEn / risk0 if stage == 3 and risk0 > 0 else na if na(entry) or na(atr) or atr == 0 else toEn / atr

        liqUp = na if na(swHigh) or hiTaken or close > swHigh or na(atr) or (atr == 0) else (swHigh - close) / atr
        liqDn = na if na(swLow) or loTaken or close < swLow or na(atr) or (atr == 0) else (close - swLow) / atr
        return (stage, dir, age, qual, entry, sl, tp, prog, liqUp, liqDn, sweptLvl, mssLevel)

    tf = timeframe.period if scanTF == '' else scanTF
    st01: Series
    st01, d01, a01, q01, e01, l01, t01, x01, u01, n01, w01, m01 = request.security(s01, tf, scan(), lookahead=barmerge.lookahead_off)
    st02: Series
    st02, d02, a02, q02, e02, l02, t02, x02, u02, n02, w02, m02 = request.security(s02, tf, scan(), lookahead=barmerge.lookahead_off)
    st03: Series
    st03, d03, a03, q03, e03, l03, t03, x03, u03, n03, w03, m03 = request.security(s03, tf, scan(), lookahead=barmerge.lookahead_off)
    st04: Series
    st04, d04, a04, q04, e04, l04, t04, x04, u04, n04, w04, m04 = request.security(s04, tf, scan(), lookahead=barmerge.lookahead_off)
    st05: Series
    st05, d05, a05, q05, e05, l05, t05, x05, u05, n05, w05, m05 = request.security(s05, tf, scan(), lookahead=barmerge.lookahead_off)
    st06: Series
    st06, d06, a06, q06, e06, l06, t06, x06, u06, n06, w06, m06 = request.security(s06, tf, scan(), lookahead=barmerge.lookahead_off)
    st07: Series
    st07, d07, a07, q07, e07, l07, t07, x07, u07, n07, w07, m07 = request.security(s07, tf, scan(), lookahead=barmerge.lookahead_off)
    st08: Series
    st08, d08, a08, q08, e08, l08, t08, x08, u08, n08, w08, m08 = request.security(s08, tf, scan(), lookahead=barmerge.lookahead_off)
    st09: Series
    st09, d09, a09, q09, e09, l09, t09, x09, u09, n09, w09, m09 = request.security(s09, tf, scan(), lookahead=barmerge.lookahead_off)
    st10: Series
    st10, d10, a10, q10, e10, l10, t10, x10, u10, n10, w10, m10 = request.security(s10, tf, scan(), lookahead=barmerge.lookahead_off)
    st11: Series
    st11, d11, a11, q11, e11, l11, t11, x11, u11, n11, w11, m11 = request.security(s11, tf, scan(), lookahead=barmerge.lookahead_off)
    st12: Series
    st12, d12, a12, q12, e12, l12, t12, x12, u12, n12, w12, m12 = request.security(s12, tf, scan(), lookahead=barmerge.lookahead_off)
    st13: Series
    st13, d13, a13, q13, e13, l13, t13, x13, u13, n13, w13, m13 = request.security(s13, tf, scan(), lookahead=barmerge.lookahead_off)
    st14: Series
    st14, d14, a14, q14, e14, l14, t14, x14, u14, n14, w14, m14 = request.security(s14, tf, scan(), lookahead=barmerge.lookahead_off)
    st15: Series
    st15, d15, a15, q15, e15, l15, t15, x15, u15, n15, w15, m15 = request.security(s15, tf, scan(), lookahead=barmerge.lookahead_off)
    st16: Series
    st16, d16, a16, q16, e16, l16, t16, x16, u16, n16, w16, m16 = request.security(s16, tf, scan(), lookahead=barmerge.lookahead_off)
    st17: Series
    st17, d17, a17, q17, e17, l17, t17, x17, u17, n17, w17, m17 = request.security(s17, tf, scan(), lookahead=barmerge.lookahead_off)
    st18: Series
    st18, d18, a18, q18, e18, l18, t18, x18, u18, n18, w18, m18 = request.security(s18, tf, scan(), lookahead=barmerge.lookahead_off)
    st19: Series
    st19, d19, a19, q19, e19, l19, t19, x19, u19, n19, w19, m19 = request.security(s19, tf, scan(), lookahead=barmerge.lookahead_off)
    st20: Series
    st20, d20, a20, q20, e20, l20, t20, x20, u20, n20, w20, m20 = request.security(s20, tf, scan(), lookahead=barmerge.lookahead_off)

    cSt: Series
    cSt, cDir, cAge, cQ, cEn, cSl, cTp, cPr, cLu, cLd, cSw, cMs = request.security(syminfo.tickerid, tf, scan(), lookahead=barmerge.lookahead_off)

    cStart: Persistent[int] = na(int)
    if cSt == 1 and cSt[1] != 1:
        cStart = bar_index
    if cSt == 0:
        cStart = na

    gSweep: Persistent[Line] = na(Line)
    gMss: Persistent[Line] = na(Line)
    gEntry: Persistent[Line] = na(Line)
    gRisk: Persistent[Box] = na(Box)
    gReward: Persistent[Box] = na(Box)
    gTag: Persistent[Label] = na(Label)

    if drawMe and barstate.islast:
        line.delete(gSweep)
        line.delete(gMss)
        line.delete(gEntry)
        box.delete(gRisk)
        box.delete(gReward)
        label.delete(gTag)
        if cSt >= 1 and cSt <= 3 and (not na(cStart)):
            col = UP if cDir == 1 else DN
            x0 = math.max(cStart, bar_index - 300)
            x1 = bar_index + 6
            gSweep = line.new(x0, cSw, x1, cSw, color=color.new(AMBER, 10), width=2, style=line.style_dotted)
            gMss = line.new(x0, cMs, x1, cMs, color=color.new(col, 0), width=2)
            if cSt >= 2:
                gEntry = line.new(x0, cEn, x1, cEn, color=color.new(TXT, 10), width=2, style=line.style_dashed)
                gRisk = box.new(x0, math.max(cEn, cSl), x1, math.min(cEn, cSl), border_color=color.new(DN, 55), bgcolor=color.new(DN, 90))
                gReward = box.new(x0, math.max(cEn, cTp), x1, math.min(cEn, cTp), border_color=color.new(UP, 55), bgcolor=color.new(UP, 90))
            arrow = '▲ ' if cDir == 1 else '▼ '
            tagTx = arrow + 'SWEPT · waiting MSS' if cSt == 1 else arrow + ('LONG' if cDir == 1 else 'SHORT') + ' SETUP · Q' + string.tostring(cQ) if cSt == 2 else arrow + 'OPEN  ' + ('+' if cPr >= 0 else '') + string.tostring(cPr, '0.0') + ' R'
            tagY = cSw if cSt == 1 else cEn
            gTag = label.new(x1, tagY, '  ' + tagTx + '  ', style=label.style_label_left, color=INK, textcolor=AMBER if cSt == 1 else col, size=size.normal)

    __block_result__ = na
    __switch__ = candSty
    if __switch__ == "Neon Bloom":
        __block_result__ = color.new('#00F5D4')
    elif __switch__ == "Midnight Cyan":
        __block_result__ = color.new('#34E89E')
    elif __switch__ == "Vibrant Neon":
        __block_result__ = color.new('#00E5B0')
    elif __switch__ == "Classic Soft":
        __block_result__ = color.new('#3FB68B')
    elif __switch__ == "Cool Blue":
        __block_result__ = color.new('#4C9AFF')
    else:
        __block_result__ = color.new('#00F5D4')
    cBull = __block_result__
    __block_result_1__ = na
    __switch__ = candSty
    if __switch__ == "Neon Bloom":
        __block_result_1__ = color.new('#FF2E88')
    elif __switch__ == "Midnight Cyan":
        __block_result_1__ = color.new('#FF4D7D')
    elif __switch__ == "Vibrant Neon":
        __block_result_1__ = color.new('#FF2E63')
    elif __switch__ == "Classic Soft":
        __block_result_1__ = color.new('#E0556B')
    elif __switch__ == "Cool Blue":
        __block_result_1__ = color.new('#8A94A6')
    else:
        __block_result_1__ = color.new('#FF2E88')
    cBear = __block_result_1__
    cEdge = cBull if close >= open else cBear
    plotcandle(na if candSty == 'Off' else open, high, low, close, 'Candles', color=color.new(cEdge, 24), wickcolor=color.new(cEdge, 18), bordercolor=cEdge)

    def hudP(s: str):
        __block_result_2__ = na
        __switch__ = s
        if __switch__ == "Top Right":
            __block_result_2__ = position.top_right
        elif __switch__ == "Top Left":
            __block_result_2__ = position.top_left
        elif __switch__ == "Bottom Right":
            __block_result_2__ = position.bottom_right
        elif __switch__ == "Bottom Left":
            __block_result_2__ = position.bottom_left
        elif __switch__ == "Middle Left":
            __block_result_2__ = position.middle_left
        else:
            __block_result_2__ = position.middle_right
        return __block_result_2__

    def tSize(s: str):
        __block_result_3__ = na
        __switch__ = s
        if __switch__ == "Small":
            __block_result_3__ = size.small
        elif __switch__ == "Large":
            __block_result_3__ = size.large
        else:
            __block_result_3__ = size.normal
        return __block_result_3__

    def shortName(s: str):
        p = string.pos(s, ':')
        return string.substring(s, p + 1) if p >= 0 else s

    def rankOf(stage: int, age: int):
        base = 0 if stage == 3 else 1 if stage == 2 else 2 if stage == 1 else 3 if stage == 4 else 4 if stage == 5 else 5
        return base * 100000 + age

    def stageText(stage: int, dir: int):
        arrow = '▲ ' if dir == 1 else '▼ ' if dir == -1 else ''
        __block_result_4__ = na
        __switch__ = stage
        if __switch__ == 1:
            __block_result_4__ = arrow + 'SWEPT · waiting MSS'
        elif __switch__ == 2:
            __block_result_4__ = arrow + ('LONG SETUP' if dir == 1 else 'SHORT SETUP')
        elif __switch__ == 3:
            __block_result_4__ = arrow + 'OPEN'
        elif __switch__ == 4:
            __block_result_4__ = arrow + 'TARGET HIT'
        elif __switch__ == 5:
            __block_result_4__ = arrow + 'STOPPED'
        else:
            __block_result_4__ = "scanning"
        return __block_result_4__

    def stageBg(stage: int, dir: int):
        __block_result_5__ = na
        __switch__ = stage
        if __switch__ == 1:
            __block_result_5__ = color.new('#5A3E0A')
        elif __switch__ == 2:
            __block_result_5__ = color.new('#0A5F55') if dir == 1 else color.new('#8E1148')
        elif __switch__ == 3:
            __block_result_5__ = color.new('#00A38B') if dir == 1 else color.new('#C21B5E')
        elif __switch__ == 4:
            __block_result_5__ = color.new('#14532D')
        elif __switch__ == 5:
            __block_result_5__ = color.new('#4A1020')
        else:
            __block_result_5__ = CARD
        return __block_result_5__

    hud: Persistent[Table] = table.new(position.top_right, 7, 22)

    if barstate.islast:
        syms: list[str] = array.from_items(s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20)
        stg = array.from_items(st01, st02, st03, st04, st05, st06, st07, st08, st09, st10, st11, st12, st13, st14, st15, st16, st17, st18, st19, st20)
        dirs = array.from_items(d01, d02, d03, d04, d05, d06, d07, d08, d09, d10, d11, d12, d13, d14, d15, d16, d17, d18, d19, d20)
        ages = array.from_items(a01, a02, a03, a04, a05, a06, a07, a08, a09, a10, a11, a12, a13, a14, a15, a16, a17, a18, a19, a20)
        quals = array.from_items(q01, q02, q03, q04, q05, q06, q07, q08, q09, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20)
        ents = array.from_items(e01, e02, e03, e04, e05, e06, e07, e08, e09, e10, e11, e12, e13, e14, e15, e16, e17, e18, e19, e20)
        sls = array.from_items(l01, l02, l03, l04, l05, l06, l07, l08, l09, l10, l11, l12, l13, l14, l15, l16, l17, l18, l19, l20)
        tps = array.from_items(t01, t02, t03, t04, t05, t06, t07, t08, t09, t10, t11, t12, t13, t14, t15, t16, t17, t18, t19, t20)
        dist = array.from_items(x01, x02, x03, x04, x05, x06, x07, x08, x09, x10, x11, x12, x13, x14, x15, x16, x17, x18, x19, x20)
        lqU = array.from_items(u01, u02, u03, u04, u05, u06, u07, u08, u09, u10, u11, u12, u13, u14, u15, u16, u17, u18, u19, u20)
        lqD = array.from_items(n01, n02, n03, n04, n05, n06, n07, n08, n09, n10, n11, n12, n13, n14, n15, n16, n17, n18, n19, n20)

        ranks: list[int] = array.new_int()
        for i in pine_range(0, nRows - 1):
            array.push(ranks, rankOf(array.get(stg, i), array.get(ages, i)))
        ord = array.sort_indices(ranks, order.ascending)

        nEntry: int = 0
        nSetup: int = 0
        nSweep: int = 0
        for i in pine_range(0, nRows - 1):
            s = array.get(stg, i)
            nEntry += 1 if s == 3 else 0
            nSetup += 1 if s == 2 else 0
            nSweep += 1 if s == 1 else 0

        table.delete(hud)
        hud = table.new(hudP(hudPos), 7, nRows + 2, bgcolor=CARD, border_color=color.new(color.new('#28323F'), 0), border_width=1)
        ts = tSize(hudSize)

        heroBg = color.new('#0A5F55') if nEntry > 0 else color.new('#1E2A38') if nSetup > 0 else CARD2
        heroTx = string.tostring(nEntry) + ' OPEN' if nEntry > 0 else string.tostring(nSetup) + ' SETUP' + ('S' if nSetup > 1 else '') + ' MAPPED' if nSetup > 0 else string.tostring(nSweep) + ' SWEEP' + ('S' if nSweep > 1 else '') + ' PENDING' if nSweep > 0 else 'NO SETUPS · scanning ' + string.tostring(nRows)
        table.cell(hud, 0, 0, '  ICT SETUP SCREENER  ·  ' + heroTx + '  ', text_color=color.white, text_size=size.large, text_halign=text.align_left, bgcolor=heroBg)
        table.merge_cells(hud, 0, 0, 4, 0)
        table.cell(hud, 5, 0, string.tostring(nSetup) + (' setup · ' if nSetup == 1 else ' setups · ') + string.tostring(nSweep) + (' sweep  ' if nSweep == 1 else ' sweeps  '), text_color=color.white, text_size=size.normal, text_halign=text.align_right, bgcolor=heroBg)
        table.merge_cells(hud, 5, 0, 6, 0)

        hdr: list[str] = array.from_items('  Symbol', 'Stage', 'Bars', 'Quality', 'Entry', 'Stop  /  Target', 'To entry · R · liquidity  ')
        for c in pine_range(0, 6):
            table.cell(hud, c, 1, array.get(hdr, c), text_color=MUTE, text_size=size.small, text_halign=text.align_left if c == 0 else text.align_right if c == 6 else text.align_center, bgcolor=CARD2)

        r: int = 2
        for k in pine_range(0, nRows - 1):
            i = array.get(ord, k)
            s = array.get(stg, i)
            d = array.get(dirs, i)
            if not (hideIdle and s == 0):
                live = s >= 1 and s <= 3
                fg = TXT if live else DIMTX if s == 0 else MUTE
                bg = stageBg(s, d)
                rowBg = CARD if s == 0 else CARD2
                en = array.get(ents, i)
                sp = array.get(sls, i)
                tg = array.get(tps, i)
                dx = array.get(dist, i)
                q = array.get(quals, i)
                isMe = syminfo.ticker == shortName(array.get(syms, i))

                table.cell(hud, 0, r, '  ' + shortName(array.get(syms, i)) + (' ◂' if isMe else ''), text_color=UP if isMe else fg, text_size=ts, text_halign=text.align_left, bgcolor=rowBg)
                table.cell(hud, 1, r, '  ' + stageText(s, d) + '  ', text_color=DIMTX if s == 0 else color.white, text_size=ts, text_halign=text.align_center, bgcolor=bg)
                table.cell(hud, 2, r, '' if s == 0 else string.tostring(array.get(ages, i)), text_color=fg, text_size=ts, text_halign=text.align_center, bgcolor=rowBg)
                table.cell(hud, 3, r, 'Q ' + string.tostring(q) if s >= 2 else '', text_color=(UP if q >= 70 else AMBER if q >= 45 else DN) if s >= 2 else fg, text_size=ts, text_halign=text.align_center, bgcolor=rowBg)
                table.cell(hud, 4, r, string.tostring(en, '#.#####') if s >= 2 and (not na(en)) else '', text_color=fg, text_size=ts, text_halign=text.align_center, bgcolor=rowBg)
                table.cell(hud, 5, r, string.tostring(sp, '#.#####') + '  /  ' + string.tostring(tg, '#.#####') if s >= 2 and (not na(sp)) else '', text_color=fg, text_size=ts, text_halign=text.align_center, bgcolor=rowBg)

                lu = array.get(lqU, i)
                ld = array.get(lqD, i)
                liqTx = '' if na(lu) and na(ld) else 'liq ▲ ' + string.tostring(lu, '0.0') + ' ATR' if na(ld) or (not na(lu) and lu < ld) else 'liq ▼ ' + string.tostring(ld, '0.0') + ' ATR'
                dxTx = ('+' if dx >= 0 else '') + string.tostring(dx, '0.0') + ' R' if s == 3 and (not na(dx)) else ('touching' if dx <= 0 else string.tostring(dx, '0.0') + ' ATR') if s == 2 and (not na(dx)) else liqTx if s == 0 else ''
                dxCol = (UP if dx >= 0 else DN) if s == 3 and (not na(dx)) else AMBER if s == 2 and (not na(dx)) and (dx <= 0.5) else DIMTX if s == 0 else fg
                table.cell(hud, 6, r, dxTx + '  ', text_color=dxCol, text_size=ts, text_halign=text.align_right, bgcolor=rowBg)
                r += 1

    if alertOn and barstate.isconfirmed:
        cur = array.from_items(st01, st02, st03, st04, st05, st06, st07, st08, st09, st10, st11, st12, st13, st14, st15, st16, st17, st18, st19, st20)
        prev = array.from_items(st01[1], st02[1], st03[1], st04[1], st05[1], st06[1], st07[1], st08[1], st09[1], st10[1], st11[1], st12[1], st13[1], st14[1], st15[1], st16[1], st17[1], st18[1], st19[1], st20[1])
        ds = array.from_items(d01, d02, d03, d04, d05, d06, d07, d08, d09, d10, d11, d12, d13, d14, d15, d16, d17, d18, d19, d20)
        qs = array.from_items(q01, q02, q03, q04, q05, q06, q07, q08, q09, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20)
        ss: list[str] = array.from_items(s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20)
        msg: str = ""
        for i in pine_range(0, nRows - 1):
            c = array.get(cur, i)
            if c != array.get(prev, i) and (c == 2 or c == 3 or (alertSw and c == 1)):
                side = 'long' if array.get(ds, i) == 1 else 'short'
                msg = msg + shortName(array.get(ss, i)) + (' swept, watch for ' + side if c == 1 else ' ' + side + ' setup mapped Q' + string.tostring(array.get(qs, i)) if c == 2 else ' ' + side + ' entered') + ' · '
        if msg != '':
            alert('LunqFX ICT Screener: ' + msg, alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)