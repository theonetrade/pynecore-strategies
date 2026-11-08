"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barmerge, barstate, box, close,
    color, font, format, high, input, label, line, location, low, math, na, open, plot, plotshape,
    position, request, script, shape, size, string, syminfo, ta, table, text, ticker, time,
    timeframe, xloc
)
from pynecore.types import Box, Color, IBPersistent, Line, Persistent, Series, Table

G1: str = "⚙ Signal Engine"
G5: str = "〰 47 MA Confirmation"
G2: str = "▣ Setup Zones"
G3: str = "⤵ Break of Structure"
G4: str = "◈ Visuals"


@script.indicator("CC First Red / Green Day", shorttitle="CC FRD/FGD", overlay=True, max_boxes_count=200, max_lines_count=300, max_labels_count=300)
def main(
    calcOn=input.string("Real Candles", "Calculate Signals On", options=("Real Candles", "Heikin Ashi"), group=G1, tooltip="Real Candles: always uses true OHLC, even when your chart is set to Heikin Ashi.\nHeikin Ashi: FRD/FGD are read from Heikin Ashi candles (pairs well with 'Candle Color')."),
    sigTF=input.timeframe("D", "Signal Timeframe", group=G1, tooltip="What counts as a 'day'. Keep on D for FRD/FGD."),
    redDef=input.string("Prior Close", "Red / Green Definition", options=("Prior Close", "Candle Color", "Both"), group=G1, tooltip="Prior Close: red = close below yesterday's close.\nCandle Color: red = close below open.\nBoth: must satisfy both."),
    minRun=input.int(3, "Min Higher / Lower Closes Into Extreme", minval=1, maxval=20, group=G1, tooltip="The rally into the peak (FRD) must contain at least this many higher closes. Mirror for FGD."),
    graceBars=input.int(2, "Allowed Pause Days In Rally", minval=0, maxval=10, group=G1, tooltip="Rally is counted over (Min Closes + this) days ending at the peak, so a doji or small pause inside the run doesn't kill it. Very common on Heikin Ashi."),
    locLen=input.int(10, "Extreme Lookback (Signal TF bars)", minval=2, maxval=500, group=G1, tooltip="The peak / trough must be the highest high / lowest low of at least this many days."),
    useMA=input.bool(True, "Require 47 MA Break", group=G5, tooltip="FRD fires on a close below the MA, FGD on a close above it — isolates the major turning points."),
    maTF=input.timeframe("240", "MA Timeframe", group=G5, tooltip="Blueprint default: 4H."),
    maLen=input.int(47, "MA Length", minval=1, group=G5),
    maType=input.string("SMA", "MA Type", options=("SMA", "EMA"), group=G5),
    armMax=input.int(15, "Max Days From Peak To MA Break", minval=2, maxval=60, group=G5, tooltip="The setup stays armed while the peak (FRD) / trough (FGD) is within this many days. Covers long topping/bottoming chop. A new high/low re-starts the setup."),
    armBars=input.int(3, "MA Break Before Signal Day: Max Gap (days)", minval=0, maxval=20, group=G5, tooltip="If the MA breaks first, the FRD/FGD day must follow within this many days."),
    useSlope=input.bool(True, "Ignore Breaks Against A Strong MA Slope", group=G5, tooltip="Skips FRDs while the MA is still rising steeply (a normal dip in an uptrend) and FGDs while it is falling steeply. Real turns happen after the MA flattens."),
    slopeLen=input.int(10, "Slope Lookback (MA TF bars)", minval=2, maxval=100, group=G5),
    slopeMax=input.float(1.0, "Max Slope (in ATRs)", minval=0.1, step=0.1, group=G5, tooltip="How far the MA may have moved over the slope lookback, measured in ATRs. Lower = stricter."),
    showArm=input.bool(True, "Mark Signal Days (armed)", group=G5),
    showMA=input.bool(False, "Plot MA", group=G5),
    showZones=input.bool(True, "Show Setup Zones", group=G2),
    zoneMode=input.string("Auto", "Zone Type", options=("Auto", "Signal Day", "MA Retest"), group=G2, tooltip="Signal Day: FRD close → FRD high (FGD low → FGD close).\nMA Retest: a tight zone around the 47 MA at the break.\nAuto: uses the signal-day zone when it is close to price, otherwise switches to the MA retest so the zone is never miles away."),
    zoneMaxAtr=input.float(1.5, "Auto: Max Distance To Signal-Day Zone (ATRs)", minval=0.1, step=0.1, group=G2),
    zoneAtrW=input.float(0.5, "MA Retest Zone Half-Width (ATRs)", minval=0.1, step=0.1, group=G2),
    showTrig=input.bool(True, "Show Trigger Line", group=G2, tooltip="Signal-day zone: FRD low / FGD high. MA retest zone: the break candle's low / high."),
    useTrigEntry=input.bool(True, "Trigger-Line Entry (no retrace)", group=G2, tooltip="If price never pulls back into the zone and instead CLOSES through the trigger line, fire FRD BRK / FGD BRK."),
    trigNoTouch=input.bool(True, "Only If Zone Was Never Tapped", group=G2),
    zoneLen=input.int(3, "Zone Length (days)", minval=1, maxval=20, group=G2),
    maxZones=input.int(10, "Max Zones Kept", minval=1, maxval=50, group=G2),
    showBOS=input.bool(True, "Show BOS", group=G3),
    pvLen=input.int(3, "Swing Strength", minval=1, maxval=20, group=G3),
    colBear=input.color(color.new('#FF1744'), "Bearish", group=G4),
    colBull=input.color(color.new('#00E676'), "Bullish", group=G4),
    colAcc=input.color(color.new('#00BCD4'), "Accent", group=G4),
    colBg=input.color(color.new('#0A1628'), "Panel Background", group=G4),
    showDash=input.bool(True, "Show Dashboard", group=G4),
    dashPos=input.string("Bottom Left", "Dashboard Position", options=("Top Right", "Top Left", "Bottom Right", "Bottom Left"), group=G4)
):
    chartSec: int = timeframe.in_seconds()
    sigSec: int = timeframe.in_seconds(sigTF)
    sameTF: bool = chartSec >= sigSec
    reqTF: str = timeframe.period if sameTF else sigTF
    effSec: int = chartSec if sameTF else sigSec
    tfLabel: str = reqTF + (' · HA' if calcOn == 'Heikin Ashi' else '')
    tkr: str = ticker.heikinashi(syminfo.tickerid) if calcOn == 'Heikin Ashi' else ticker.standard(syminfo.tickerid)

    def f_isRed(o: float, c: float, pc: float):
        return c < pc if redDef == 'Prior Close' else c < o if redDef == 'Candle Color' else c < pc and c < o

    def f_isGreen(o: float, c: float, pc: float):
        return c > pc if redDef == 'Prior Close' else c > o if redDef == 'Candle Color' else c > pc and c > o

    def f_core():
        upRun: Persistent[int] = 0
        dnRun: Persistent[int] = 0
        upRun = upRun + 1 if close > close[1] else 0
        dnRun = dnRun + 1 if close < close[1] else 0
        red: Series[bool] = f_isRed(open, close, close[1])
        green: Series[bool] = f_isGreen(open, close, close[1])

        W: int = math.max(armMax, locLen)
        pkOff: int = math.max(-ta.highestbars(high, W), 0)
        trOff: int = math.max(-ta.lowestbars(low, W), 0)
        cntLen: int = minRun + graceBars
        upCnt: Series[float] = math.sum(1 if close > close[1] else 0, cntLen)
        dnCnt: Series[float] = math.sum(1 if close < close[1] else 0, cntLen)

        frdOff: int = -1
        if bar_index > W:
            for i in pine_range(pkOff, 0):
                if red[i]:
                    frdOff = i
                    break
        frdArm: bool = bar_index > W and pkOff <= armMax and (upCnt[pkOff] >= minRun) and (frdOff >= 0)
        fo: int = math.max(frdOff, 0)
        frdDay: bool = frdArm and frdOff == 0

        fgdOff: int = -1
        if bar_index > W:
            for i in pine_range(trOff, 0):
                if green[i]:
                    fgdOff = i
                    break
        fgdArm: bool = bar_index > W and trOff <= armMax and (dnCnt[trOff] >= minRun) and (fgdOff >= 0)
        go: int = math.max(fgdOff, 0)
        fgdDay: bool = fgdArm and fgdOff == 0

        locHi: float = ta.highest(high, locLen)
        locLo: float = ta.lowest(low, locLen)
        curPeak: float = ta.highest(high, math.max(upRun, 1))
        curTrough: float = ta.lowest(low, math.max(dnRun, 1))

        ph: float = ta.pivothigh(high, pvLen, pvLen)
        pl: float = ta.pivotlow(low, pvLen, pvLen)
        swHi: Persistent[float] = na(float)
        swHiT: Persistent[int] = na(int)
        hiLive: Persistent[bool] = False
        swLo: Persistent[float] = na(float)
        swLoT: Persistent[int] = na(int)
        loLive: Persistent[bool] = False
        if not na(ph):
            swHi = ph
            swHiT = time[pvLen]
            hiLive = True
        if not na(pl):
            swLo = pl
            swLoT = time[pvLen]
            loLive = True
        bosUp: bool = False
        bosDn: bool = False
        if hiLive and close > swHi:
            bosUp = True
            hiLive = False
        if loLive and close < swLo:
            bosDn = True
            loLive = False

        return (frdArm, frdDay, high[fo], low[fo], close[fo], time[fo], high[pkOff], time[pkOff], fgdArm, fgdDay, high[go], low[go], close[go], time[go], low[trOff], time[trOff], upRun, dnRun, curPeak, curTrough, locHi, locLo, close, bosUp, bosDn, swHi, swHiT, swLo, swLoT)

    def f_confirmed():
        y1: Series
        y2: Series
        y3: Series
        y4: Series
        y5: Series
        y6: Series
        y7: Series
        y8: Series
        y9: Series
        y10: Series
        y11: Series
        y12: Series
        y13: Series
        y14: Series
        y15: Series
        y16: Series
        y17: Series
        y18: Series
        y19: Series
        y20: Series
        y21: Series
        y22: Series
        y23: Series
        y24: Series
        y25: Series
        y26: Series
        y27: Series
        y28: Series
        y29: Series
        y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y11, y12, y13, y14, y15, y16, y17, y18, y19, y20, y21, y22, y23, y24, y25, y26, y27, y28, y29 = f_core()
        return (y1[1], y2[1], y3[1], y4[1], y5[1], y6[1], y7[1], y8[1], y9[1], y10[1], y11[1], y12[1], y13[1], y14[1], y15[1], y16[1], y17[1], y18[1], y19[1], y20[1], y21[1], y22[1], y23[1], y24[1], y25[1], y26[1], y27[1], y28[1], y29[1])

    cArm, cDay, cFdH, cFdL, cFdC, cFdT, cPk, cPkT, cGArm, cGDay, cGdH, cGdL, cGdC, cGdT, cTr, cTrT, cUp, cDn, cCurPk, cCurTr, cLh, cLl, cC, cBu, cBd, cSh, cSht, cSl, cSlt = request.security(tkr, reqTF, f_core())
    pArm, pDay, pFdH, pFdL, pFdC, pFdT, pPk, pPkT, pGArm, pGDay, pGdH, pGdL, pGdC, pGdT, pTr, pTrT, pUp, pDn, pCurPk, pCurTr, pLh, pLl, pC, pBu, pBd, pSh, pSht, pSl, pSlt = request.security(tkr, reqTF, f_confirmed(), lookahead=barmerge.lookahead_on)
    dOpen: float = request.security(tkr, reqTF, open, lookahead=barmerge.lookahead_on)
    liveClose: float = request.security(tkr, timeframe.period, close)
    liveHigh: float = request.security(tkr, timeframe.period, high)
    liveLow: float = request.security(tkr, timeframe.period, low)
    liveAtr: float = request.security(tkr, timeframe.period, ta.atr(14))

    newSig: bool = timeframe.change(reqTF)

    sArm: bool = cArm if sameTF else pArm
    sFdH: float = cFdH if sameTF else pFdH
    sFdL: float = cFdL if sameTF else pFdL
    sFdC: float = cFdC if sameTF else pFdC
    sFdT: int = cFdT if sameTF else pFdT
    sPk: float = cPk if sameTF else pPk
    sPkT: int = cPkT if sameTF else pPkT
    sGArm: bool = cGArm if sameTF else pGArm
    sGdH: float = cGdH if sameTF else pGdH
    sGdL: float = cGdL if sameTF else pGdL
    sGdC: float = cGdC if sameTF else pGdC
    sGdT: int = cGdT if sameTF else pGdT
    sTr: float = cTr if sameTF else pTr
    sTrT: int = cTrT if sameTF else pTrT

    frdDayEvt: bool = cDay and barstate.isconfirmed if sameTF else newSig and pDay
    fgdDayEvt: bool = cGDay and barstate.isconfirmed if sameTF else newSig and pGDay
    armOkD: bool = barstate.isconfirmed if sameTF else True

    bosUpEvt: bool = showBOS and (cBu and barstate.isconfirmed if sameTF else newSig and pBu)
    bosDnEvt: bool = showBOS and (cBd and barstate.isconfirmed if sameTF else newSig and pBd)
    bUpLvl: float = cSh if sameTF else pSh
    bUpT0: int = cSht if sameTF else pSht
    bDnLvl: float = cSl if sameTF else pSl
    bDnT0: int = cSlt if sameTF else pSlt

    def f_ma(src: float):
        e: float = ta.ema(src, maLen)
        m: float = ta.sma(src, maLen)
        return e if maType == 'EMA' else m

    def f_maS():
        m: Series[float] = f_ma(close)
        return (m, (m - m[slopeLen]) / ta.atr(14))

    def f_maX():
        m: Series[float] = f_ma(close)
        return (m, ta.crossunder(close, m), ta.crossover(close, m), (m - m[slopeLen]) / ta.atr(14))

    def f_maXConf():
        a: Series
        b: Series
        c: Series
        d: Series
        a, b, c, d = f_maX()
        return (a[1], b[1], c[1], d[1])

    maSec: int = timeframe.in_seconds(maTF)
    maLower: bool = chartSec < maSec
    maLive, slLive = request.security(tkr, maTF, f_maS())
    mMa, mXdn, mXup, mSl = request.security(tkr, maTF, f_maXConf(), lookahead=barmerge.lookahead_on)
    maChg: bool = timeframe.change(maTF)
    cXdn: bool = ta.crossunder(liveClose, maLive)
    cXup: bool = ta.crossover(liveClose, maLive)
    xDnEvt: bool = maChg and mXdn if maLower else cXdn and barstate.isconfirmed
    xUpEvt: bool = maChg and mXup if maLower else cXup and barstate.isconfirmed
    maRef: float = mMa if maLower else maLive
    slRef: float = mSl if maLower else slLive
    slOkDn: bool = not useSlope or na(slRef) or slRef < slopeMax
    slOkUp: bool = not useSlope or na(slRef) or slRef > -slopeMax

    plot(maLive, '47 MA', color=colAcc if showMA else color.new(colAcc, 100), linewidth=2)

    xDnT: Persistent[int] = na(int)
    xUpT: Persistent[int] = na(int)
    lastFrdPkT: Persistent[int] = na(int)
    lastFgdTrT: Persistent[int] = na(int)
    winMs: int = (armBars + 1) * effSec * 1000

    if not na(xDnT) and time - xDnT > winMs:
        xDnT = na
    if not na(xUpT) and time - xUpT > winMs:
        xUpT = na
    if xDnEvt:
        xDnT = time
        xUpT = na
    if xUpEvt:
        xUpT = time
        xDnT = na

    frdLive: bool = sArm and armOkD and (na(lastFrdPkT) or sPkT != lastFrdPkT)
    fgdLive: bool = sGArm and armOkD and (na(lastFgdTrT) or sTrT != lastFgdTrT)

    frdFire: bool = frdLive and liveClose < maRef and slOkDn and (xDnEvt or (frdDayEvt and (not na(xDnT)))) if useMA else frdLive and frdDayEvt
    fgdFire: bool = fgdLive and liveClose > maRef and slOkUp and (xUpEvt or (fgdDayEvt and (not na(xUpT)))) if useMA else fgdLive and fgdDayEvt

    plotshape(useMA and showArm and frdDayEvt and frdLive, title='FRD Day (armed)', style=shape.triangledown, location=location.abovebar, color=color.new(colBear, 30), size=size.tiny)
    plotshape(useMA and showArm and fgdDayEvt and fgdLive, title='FGD Day (armed)', style=shape.triangleup, location=location.belowbar, color=color.new(colBull, 30), size=size.tiny)

    zoneBoxes: Persistent[list[Box]] = array.new_box()
    trigLines: Persistent[list[Line]] = array.new_line()
    lastSig: Persistent[str] = "—"
    lastCol: Persistent[Color] = color.gray

    def f_addZone(t1: int, top: float, bot: float, trig: float, col: Color, txt: str):
        t2: int = t1 + zoneLen * effSec * 1000
        if showZones:
            b: Box = box.new(t1, top, t2, bot, xloc=xloc.bar_time, border_color=color.new(col, 30), bgcolor=color.new(col, 85), text=txt, text_color=col, text_size=size.small, text_halign=text.align_left, text_valign=text.align_top)
            array.push(zoneBoxes, b)
            if array.size(zoneBoxes) > maxZones:
                method_call('delete', array.shift(zoneBoxes))
        __block_result__ = na
        if showTrig:
            ln: Line = line.new(t1, trig, t2, trig, xloc=xloc.bar_time, color=col, style=line.style_dashed, width=1)
            array.push(trigLines, ln)
            __block_result_1__ = na
            if array.size(trigLines) > maxZones:
                __block_result_1__ = method_call('delete', array.shift(trigLines))
            __block_result__ = __block_result_1__
        return __block_result__

    trD_on: Persistent[bool] = False
    trD_t: Persistent[int] = na(int)
    trD_lvl: Persistent[float] = na(float)
    trD_zone: Persistent[float] = na(float)
    trD_pk: Persistent[float] = na(float)
    trD_touch: Persistent[bool] = False
    trU_on: Persistent[bool] = False
    trU_t: Persistent[int] = na(int)
    trU_lvl: Persistent[float] = na(float)
    trU_zone: Persistent[float] = na(float)
    trU_tr: Persistent[float] = na(float)
    trU_touch: Persistent[bool] = False

    if frdFire:
        w: float = zoneAtrW * liveAtr
        sigFar: bool = liveClose > sFdH or sFdC - liveClose > zoneMaxAtr * liveAtr
        useSig: bool = zoneMode == 'Signal Day' or (zoneMode == 'Auto' and (not sigFar))
        zTop: float = sFdH if useSig else math.min(maRef + w, sPk)
        zBot: float = sFdC if useSig else math.min(maRef, math.max(liveClose, maRef - w))
        zTrig: float = sFdL if useSig else liveLow
        lastSig = 'FRD · ' + string.format_time(sFdT, 'MMM dd', syminfo.timezone)
        lastCol = colBear
        lastFrdPkT = sPkT
        xDnT = na
        f_addZone(time, zTop, zBot, zTrig, colBear, 'FRD SELL ZONE' if useSig else 'FRD SELL ZONE · MA')
        alert('🔴 CC FRD CONFIRMED' + (' + 47 MA BREAK' if useMA else '') + ' — ' + syminfo.ticker + ' (' + tfLabel + ') | Sell zone ' + string.tostring(zBot, format.mintick) + ' – ' + string.tostring(zTop, format.mintick) + ' | Trigger ' + string.tostring(zTrig, format.mintick), alert.freq_once_per_bar_close)
        trD_on = useTrigEntry and liveClose > zTrig
        trD_t = time
        trD_lvl = zTrig
        trD_zone = zBot
        trD_pk = sPk
        trD_touch = False

    if fgdFire:
        w: float = zoneAtrW * liveAtr
        sigFar: bool = liveClose < sGdL or liveClose - sGdC > zoneMaxAtr * liveAtr
        useSig: bool = zoneMode == 'Signal Day' or (zoneMode == 'Auto' and (not sigFar))
        zBot: float = sGdL if useSig else math.max(maRef - w, sTr)
        zTop: float = sGdC if useSig else math.max(maRef, math.min(liveClose, maRef + w))
        zTrig: float = sGdH if useSig else liveHigh
        lastSig = 'FGD · ' + string.format_time(sGdT, 'MMM dd', syminfo.timezone)
        lastCol = colBull
        lastFgdTrT = sTrT
        xUpT = na
        f_addZone(time, zTop, zBot, zTrig, colBull, 'FGD BUY ZONE' if useSig else 'FGD BUY ZONE · MA')
        alert('🟢 CC FGD CONFIRMED' + (' + 47 MA BREAK' if useMA else '') + ' — ' + syminfo.ticker + ' (' + tfLabel + ') | Buy zone ' + string.tostring(zBot, format.mintick) + ' – ' + string.tostring(zTop, format.mintick) + ' | Trigger ' + string.tostring(zTrig, format.mintick), alert.freq_once_per_bar_close)
        trU_on = useTrigEntry and liveClose < zTrig
        trU_t = time
        trU_lvl = zTrig
        trU_zone = zTop
        trU_tr = sTr
        trU_touch = False

    zoneMs: int = zoneLen * effSec * 1000
    frdBrk: bool = False
    fgdBrk: bool = False

    if trD_on and time > trD_t and barstate.isconfirmed:
        if time - trD_t > zoneMs or liveClose > trD_pk or fgdFire:
            trD_on = False
        else:
            if liveHigh >= trD_zone:
                trD_touch = True
            if liveClose < trD_lvl and (not trigNoTouch or not trD_touch):
                frdBrk = True
                trD_on = False

    if trU_on and time > trU_t and barstate.isconfirmed:
        if time - trU_t > zoneMs or liveClose < trU_tr or frdFire:
            trU_on = False
        else:
            if liveLow <= trU_zone:
                trU_touch = True
            if liveClose > trU_lvl and (not trigNoTouch or not trU_touch):
                fgdBrk = True
                trU_on = False

    if frdBrk:
        lastSig = 'FRD BRK · ' + string.format_time(time, 'MMM dd', syminfo.timezone)
        lastCol = colBear
        alert('🔻 CC FRD TRIGGER-LINE ENTRY — ' + syminfo.ticker + ' (' + tfLabel + ') closed below ' + string.tostring(trD_lvl, format.mintick) + ('' if trD_touch else ' without retracing to the sell zone'), alert.freq_once_per_bar_close)
    if fgdBrk:
        lastSig = 'FGD BRK · ' + string.format_time(time, 'MMM dd', syminfo.timezone)
        lastCol = colBull
        alert('🔺 CC FGD TRIGGER-LINE ENTRY — ' + syminfo.ticker + ' (' + tfLabel + ') closed above ' + string.tostring(trU_lvl, format.mintick) + ('' if trU_touch else ' without retracing to the buy zone'), alert.freq_once_per_bar_close)

    plotshape(frdBrk, title='FRD Trigger Entry', style=shape.labeldown, location=location.abovebar, color=color.new(colBear, 20), text='FRD BRK', textcolor=color.white, size=size.tiny)
    plotshape(fgdBrk, title='FGD Trigger Entry', style=shape.labelup, location=location.belowbar, color=color.new(colBull, 20), text='FGD BRK', textcolor=color.black, size=size.tiny)

    if bosDnEvt and (not na(bDnLvl)) and (not na(bDnT0)):
        line.new(bDnT0, bDnLvl, time, bDnLvl, xloc=xloc.bar_time, color=colBear, style=line.style_dotted, width=2)
        label.new(time, bDnLvl, 'BOS ↓', xloc=xloc.bar_time, style=label.style_label_left, color=colBg, textcolor=colBear, size=size.small)
        alert('⤵ CC BEARISH BOS — ' + syminfo.ticker + ' (' + tfLabel + ') closed below swing low ' + string.tostring(bDnLvl, format.mintick), alert.freq_once_per_bar_close)

    if bosUpEvt and (not na(bUpLvl)) and (not na(bUpT0)):
        line.new(bUpT0, bUpLvl, time, bUpLvl, xloc=xloc.bar_time, color=colBull, style=line.style_dotted, width=2)
        label.new(time, bUpLvl, 'BOS ↑', xloc=xloc.bar_time, style=label.style_label_left, color=colBg, textcolor=colBull, size=size.small)
        alert('⤴ CC BULLISH BOS — ' + syminfo.ticker + ' (' + tfLabel + ') closed above swing high ' + string.tostring(bUpLvl, format.mintick), alert.freq_once_per_bar_close)

    plotshape(frdFire, title='FRD', style=shape.labeldown, location=location.abovebar, color=colBear, text='FRD', textcolor=color.white, size=size.small)
    plotshape(fgdFire, title='FGD', style=shape.labelup, location=location.belowbar, color=colBull, text='FGD', textcolor=color.black, size=size.small)

    liveRed: bool = f_isRed(dOpen, liveClose, pC)
    liveGreen: bool = f_isGreen(dOpen, liveClose, pC)
    frdForming: bool = barstate.isrealtime and pUp >= minRun and liveRed and (pCurPk >= pLh)
    fgdForming: bool = barstate.isrealtime and pDn >= minRun and liveGreen and (pCurTr <= pLl)

    frdFired: IBPersistent[bool] = False
    fgdFired: IBPersistent[bool] = False
    if newSig:
        frdFired = False
        fgdFired = False
    if frdForming and (not frdFired):
        frdFired = True
        alert('⚠ CC FRD FORMING — ' + syminfo.ticker + ' (' + tfLabel + ') trading red vs prior close ' + string.tostring(pC, format.mintick) + ' after ' + string.tostring(pUp) + ' higher closes', alert.freq_once_per_bar)
    if fgdForming and (not fgdFired):
        fgdFired = True
        alert('⚠ CC FGD FORMING — ' + syminfo.ticker + ' (' + tfLabel + ') trading green vs prior close ' + string.tostring(pC, format.mintick) + ' after ' + string.tostring(pDn) + ' lower closes', alert.freq_once_per_bar)

    alertcondition(frdFire, 'CC FRD Confirmed', 'CC FRD confirmed on {{ticker}} — watch pullback into sell zone')
    alertcondition(fgdFire, 'CC FGD Confirmed', 'CC FGD confirmed on {{ticker}} — watch pullback into buy zone')
    alertcondition(frdBrk, 'CC FRD Trigger-Line Entry', 'CC FRD trigger-line entry on {{ticker}}')
    alertcondition(fgdBrk, 'CC FGD Trigger-Line Entry', 'CC FGD trigger-line entry on {{ticker}}')
    alertcondition(frdForming, 'CC FRD Forming', 'CC FRD forming on {{ticker}}')
    alertcondition(fgdForming, 'CC FGD Forming', 'CC FGD forming on {{ticker}}')
    alertcondition(bosDnEvt, 'CC Bearish BOS', 'CC bearish BOS on {{ticker}}')
    alertcondition(bosUpEvt, 'CC Bullish BOS', 'CC bullish BOS on {{ticker}}')

    def f_pos(s: str):
        __block_result_2__ = na
        __switch__ = s
        if __switch__ == "Top Left":
            __block_result_2__ = position.top_left
        elif __switch__ == "Top Right":
            __block_result_2__ = position.top_right
        elif __switch__ == "Bottom Right":
            __block_result_2__ = position.bottom_right
        else:
            __block_result_2__ = position.bottom_left
        return __block_result_2__

    dash: Persistent[Table] = table.new(f_pos(dashPos), 2, 8, bgcolor=colBg, frame_color=colAcc, frame_width=1, border_color=color.new(colAcc, 75), border_width=1)

    def f_row(r: int, k: str, v: str, vc: Color):
        table.cell(dash, 0, r, k, text_color=color.new(colAcc, 20), text_size=size.small, text_halign=text.align_left, text_font_family=font.family_monospace)
        return table.cell(dash, 1, r, v, text_color=vc, text_size=size.small, text_halign=text.align_right, text_font_family=font.family_monospace)

    if barstate.isfirst and showDash:
        table.merge_cells(dash, 0, 0, 1, 0)

    if showDash and barstate.islast:
        useCur: bool = sameTF and (not barstate.isrealtime)
        dUp: int = cUp if useCur else pUp
        dDn: int = cDn if useCur else pDn
        aboveMA: bool = liveClose > maRef
        status: str = '⚠ FRD FORMING' if frdForming else '⚠ FGD FORMING' if fgdForming else ('FRD zone tapped' if trD_touch else 'FRD live: zone / BRK') if trD_on else ('FGD zone tapped' if trU_touch else 'FGD live: zone / BRK') if trU_on else ('FRD armed → MA break' if slOkDn else 'FRD armed · MA too steep') if frdLive else ('FGD armed → MA break' if slOkUp else 'FGD armed · MA too steep') if fgdLive else 'Watching → FRD' if dUp >= minRun else 'Watching → FGD' if dDn >= minRun else 'No setup'
        stCol: Color = colBear if trD_on or frdForming or frdLive or (dUp >= minRun) else colBull if trU_on or fgdForming or fgdLive or (dDn >= minRun) else color.gray
        table.cell(dash, 0, 0, 'CC FIRST RED / GREEN DAY', text_color=colAcc, text_size=size.small, text_font_family=font.family_monospace)
        f_row(1, 'Signal TF', tfLabel, color.white)
        f_row(2, 'Definition', redDef, color.white)
        f_row(3, 'Higher Closes', string.tostring(dUp) + (' ✓' if dUp >= minRun else ''), colBull if dUp >= minRun else color.white)
        f_row(4, 'Lower Closes', string.tostring(dDn) + (' ✓' if dDn >= minRun else ''), colBear if dDn >= minRun else color.white)
        f_row(5, 'Last Signal', lastSig, lastCol)
        f_row(6, string.tostring(maLen) + ' ' + maType + ' (' + maTF + ')', '—' if na(maRef) else 'Above ▲' if aboveMA else 'Below ▼', colBull if aboveMA else colBear)
        f_row(7, 'Status', status, stCol)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)