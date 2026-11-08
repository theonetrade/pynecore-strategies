"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, box, close, color,
    dayofmonth, dayofweek, display, format, high, input, label, line, location, low, math, month,
    na, nz, open, plot, plotshape, position, script, shape, size, string, ta, table, text, time,
    timestamp, year
)
from pynecore.types import Box, Label, Line, Persistent, PersistentSeries, Table

grpMkt: str = "Market"
grpTime: str = "Session / time window"
grpSig: str = "Break & signal logic"
grpNS: str = "NS ORB (0.125 limit)"
grpTgt: str = "Targets"
grpRisk: str = "Take profit / Stop loss"
grpVis: str = "Visuals"
grpAlert: str = "Alerts"


@script.indicator("Time Range ORB Detector [34ematrader]", shorttitle="TBR / ORB Detector", overlay=True, max_boxes_count=500, max_lines_count=500, max_labels_count=500)
def main(
    iMkt=input.string("NQ", "Market", options=("NQ", "MNQ", "ES", "MES", "YM", "MYM", "RTY", "M2K", "GC", "CL", "Custom"), group=grpMkt, tooltip="Sets the default fixed-point target. Override below if you want a different size."),
    iCustomPts=input.float(50.0, "Custom / override point target", minval=0.25, step=0.25, group=grpMkt),
    iUseMktPts=input.bool(True, "Use market default point target", group=grpMkt),
    iPreset=input.string("15-min ORB 9:30–9:45", "Session preset", options=("NY TBR 8:12–9:12", "15-min ORB 9:30–9:45", "5-min ORB 9:30–9:35", "30-min ORB 9:30–10:00", "Initial Balance 9:30–10:30", "London TBR 1:12–2:12", "Custom start + end", "Custom start + duration"), group=grpTime),
    iStartHIn=input.int(9, "Custom start hour", minval=0, maxval=23, group=grpTime),
    iStartMIn=input.int(30, "Custom start minute", minval=0, maxval=59, group=grpTime),
    iEndHIn=input.int(9, "Custom end hour", minval=0, maxval=23, group=grpTime),
    iEndMIn=input.int(45, "Custom end minute", minval=0, maxval=59, group=grpTime),
    iDurMin=input.int(15, "Custom duration (minutes)", minval=1, maxval=360, group=grpTime),
    iTz=input.string("America/New_York", "Timezone", options=("America/New_York", "America/Chicago", "America/Los_Angeles", "UTC", "Europe/London"), group=grpTime),
    iShowDays=input.int(10, "Historical sessions to keep", minval=1, maxval=40, group=grpTime),
    iSignalUntilH=input.int(14, "Stop new signals after hour", minval=0, maxval=23, group=grpTime),
    iSignalUntilM=input.int(30, "Stop new signals after minute", minval=0, maxval=59, group=grpTime),
    iStyle=input.string("NS ORB (0.125 limit)", "Trade style", options=("Reversal (fade first break)", "Breakout (trade first break)", "Breakout then reversal", "NS ORB (0.125 limit)"), group=grpSig, tooltip="Reversal: first side taken → fade toward the opposite end.\nBreakout: first side taken → trade WITH the break.\nBreakout then reversal: first signal WITH the break; opposite side later fires reversal.\nNS ORB: full-body close outside → limit at 0.125 pullback, SL at 95% of range, TP 0.4R (NomadaScalper rules)."),
    iBreakMode=input.string("Close", "Break detection", options=("Wick", "Close"), group=grpSig),
    iConfirm=input.string("Sweep only (first break)", "Entry confirmation", options=("Sweep only (first break)", "Sweep + reclaim close", "Sweep + opposing candle"), group=grpSig),
    iAllowRev=input.bool(True, "Allow second (reversal) signal after first break", group=grpSig, tooltip="Used by 'Breakout then reversal'. After the first side is taken and the first signal prints, a break of the opposite side prints the reversal."),
    iRequireAfterRange=input.bool(True, "Only detect breaks AFTER the window ends", group=grpSig),
    iNsEntry=input.float(0.125, "Entry pullback (fraction of range)", minval=0.01, maxval=0.5, step=0.005, group=grpNS, tooltip="0.125 = 12.5% pullback from the breakout extreme into the range."),
    iNsSlProt=input.float(0.95, "SL protect fraction of range", minval=0.5, maxval=1.0, step=0.01, group=grpNS, tooltip="0.95 = stop placed so it protects 95% of the range (near opposite extreme)."),
    iNsTpR=input.float(0.4, "Take profit (R multiple)", minval=0.1, maxval=5.0, step=0.05, group=grpNS),
    iNsShowExt50=input.bool(True, "Show 50% extension", group=grpNS),
    iNsShowInternals=input.bool(True, "Show 0.25 / 0.50 / 0.75 internals", group=grpNS),
    iNsFullBody=input.bool(True, "Require full body outside (open & close)", group=grpNS, tooltip="If true, both open and close must be outside the range. If false, close outside is enough."),
    iShowOpp=input.bool(True, "Target: opposing range end (high or low)", group=grpTgt),
    iShowEq=input.bool(True, "Target: 50% equilibrium", group=grpTgt),
    iShowPts=input.bool(True, "Target: fixed points", group=grpTgt),
    iShowMM=input.bool(False, "Target: measured move (1x range height)", group=grpTgt),
    iExtendHrs=input.int(6, "Extend levels (hours after window end)", minval=1, maxval=20, group=grpTgt),
    iAtrLen=input.int(14, "ATR length", minval=1, maxval=100, group=grpRisk),
    iTpAtr=input.float(1.0, "Take profit (ATR multiples)", minval=0.1, step=0.1, group=grpRisk),
    iSlAtr=input.float(0.5, "Stop loss (ATR multiples)", minval=0.1, step=0.1, group=grpRisk),
    iSlMode=input.string("ATR", "Stop loss type", options=("ATR", "Swing / pivot", "Tighter of ATR or swing", "Wider of ATR or swing"), group=grpRisk, tooltip="ATR: SL = entry ± SL ATR multiple.\nSwing / pivot: SL beyond the last confirmed pivot (or lookback swing if no pivot yet).\nTighter / wider: combine both."),
    iPivotL=input.int(5, "Pivot left bars", minval=1, maxval=50, group=grpRisk),
    iPivotR=input.int(5, "Pivot right bars", minval=1, maxval=50, group=grpRisk),
    iSwingLb=input.int(10, "Swing lookback (fallback)", minval=2, maxval=100, group=grpRisk, tooltip="Used when a confirmed pivot is not available yet, or as the swing reference."),
    iSwingBufAtr=input.float(0.1, "Swing SL buffer (ATR)", minval=0.0, step=0.05, group=grpRisk, tooltip="Extra room beyond the swing/pivot so the stop is not glued to the wick."),
    iShowTpsl=input.bool(True, "Draw TP / SL lines on the trade", group=grpRisk),
    iExpireEod=input.bool(True, "Expire open paper trade at next NY day", group=grpRisk),
    iStatsOnRev=input.bool(True, "Include reversal signals in win rate", group=grpRisk),
    iShowBox=input.bool(True, "Show range box", group=grpVis),
    iShowExt=input.bool(True, "Extend High / Low / Mid after window", group=grpVis),
    iShowMid=input.bool(True, "Show mid line", group=grpVis),
    iShowLabels=input.bool(True, "HIGH / LOW labels", group=grpVis),
    iShowSweeps=input.bool(True, "Mark first sweep", group=grpVis),
    iShowSignals=input.bool(True, "Buy / Sell shapes", group=grpVis),
    iShowTgtBox=input.bool(True, "Paint target zone after signal", group=grpVis),
    iShowTable=input.bool(True, "Session status table", group=grpVis),
    iTablePos=input.string("Top Right", "Table position", options=("Top Right", "Top Left", "Bottom Right", "Bottom Left"), group=grpVis),
    colBoxBg=input.color(color.new(color.new('#6B1212'), 78), "Box fill", group=grpVis),
    colBoxBd=input.color(color.new(color.new('#C43C3C'), 20), "Box border / range lines", group=grpVis),
    colMid=input.color(color.new(color.new('#FFFFFF'), 55), "Mid line", group=grpVis),
    colHighLbl=input.color(color.new('#FF6B6B'), "Range High label", group=grpVis),
    colLowLbl=input.color(color.new('#FF6B6B'), "Range Low label", group=grpVis),
    colBuy=input.color(color.new('#00E676'), "Buy color", group=grpVis),
    colSell=input.color(color.new('#FF1744'), "Sell color", group=grpVis),
    colSweep=input.color(color.new('#FFD54F'), "Sweep marker", group=grpVis),
    colRev=input.color(color.new('#FF9100'), "Reversal signal color", group=grpVis),
    colTgtLong=input.color(color.new(color.new('#1B5E20'), 72), "Long target zone", group=grpVis),
    colTgtShrt=input.color(color.new(color.new('#7F1D1D'), 72), "Short target zone", group=grpVis),
    colNsEntry=input.color(color.new('#00BCD4'), "NS entry line", group=grpVis),
    colNsExt=input.color(color.new('#AB47BC'), "NS 50% extension", group=grpVis),
    iAlertSweep=input.bool(True, "Alert on first sweep", group=grpAlert),
    iAlertSig=input.bool(True, "Alert on buy / sell", group=grpAlert),
    iAlertRev=input.bool(True, "Alert on reversal signal", group=grpAlert),
    iAlertTgt=input.bool(True, "Alert when opposing end is tagged", group=grpAlert),
    iAlertNs=input.bool(True, "Alert on NS ORB setup / fill", group=grpAlert)
):
    def f_mkt_pts():
        __block_result__ = na
        __switch__ = iMkt
        if __switch__ == "NQ":
            __block_result__ = 50.0
        elif __switch__ == "MNQ":
            __block_result__ = 50.0
        elif __switch__ == "ES":
            __block_result__ = 12.0
        elif __switch__ == "MES":
            __block_result__ = 12.0
        elif __switch__ == "YM":
            __block_result__ = 80.0
        elif __switch__ == "MYM":
            __block_result__ = 80.0
        elif __switch__ == "RTY":
            __block_result__ = 15.0
        elif __switch__ == "M2K":
            __block_result__ = 15.0
        elif __switch__ == "GC":
            __block_result__ = 8.0
        elif __switch__ == "CL":
            __block_result__ = 0.5
        else:
            __block_result__ = iCustomPts
        return __block_result__

    tgtPts = f_mkt_pts() if iUseMktPts and iMkt != 'Custom' else iCustomPts

    def f_win():
        sh: int = 8
        sm: int = 12
        eh: int = 9
        em: int = 12
        __switch__ = iPreset
        if __switch__ == "NY TBR 8:12–9:12":
            sh = 8
            sm = 12
            eh = 9
            em = 12
        elif __switch__ == "15-min ORB 9:30–9:45":
            sh = 9
            sm = 30
            eh = 9
            em = 45
        elif __switch__ == "5-min ORB 9:30–9:35":
            sh = 9
            sm = 30
            eh = 9
            em = 35
        elif __switch__ == "30-min ORB 9:30–10:00":
            sh = 9
            sm = 30
            eh = 10
            em = 0
        elif __switch__ == "Initial Balance 9:30–10:30":
            sh = 9
            sm = 30
            eh = 10
            em = 30
        elif __switch__ == "London TBR 1:12–2:12":
            sh = 1
            sm = 12
            eh = 2
            em = 12
        elif __switch__ == "Custom start + duration":
            sh = iStartHIn
            sm = iStartMIn
            total: int = iStartHIn * 60 + iStartMIn + iDurMin
            eh = cast_int(math.floor(total / 60.0)) % 24
            em = total % 60
        elif __switch__ == "Custom start + end":
            sh = iStartHIn
            sm = iStartMIn
            eh = iEndHIn
            em = iEndMIn
        else:
            sh = iStartHIn
            sm = iStartMIn
            eh = iEndHIn
            em = iEndMIn
        return (sh, sm, eh, em)

    iStartH, iStartM, iEndH, iEndM = f_win()





    nyY = year(time, iTz)
    nyMo = month(time, iTz)
    nyD = dayofmonth(time, iTz)
    nyDow = dayofweek(time, iTz)

    def f_ts(y, m, d, h, min):
        return timestamp(iTz, y, m, d, h, min)

    rangeStart = f_ts(nyY, nyMo, nyD, iStartH, iStartM)
    rangeEnd = f_ts(nyY, nyMo, nyD, iEndH, iEndM)

    rangeEnd = rangeEnd + 24 * 60 * 60 * 1000 if rangeEnd <= rangeStart else rangeEnd
    signalCut = f_ts(nyY, nyMo, nyD, iSignalUntilH, iSignalUntilM)
    signalCut = signalCut + 24 * 60 * 60 * 1000 if signalCut <= rangeEnd else signalCut

    inBuild = time >= rangeStart and time < rangeEnd
    afterRng = time >= rangeEnd
    inSignalWin = time >= rangeEnd and time < signalCut
    newNyDay = ta.change(nyD) != 0 or ta.change(nyY) != 0
    isWeekday = nyDow != dayofweek.saturday and nyDow != dayofweek.sunday

    def f_pad(n):
        return '0' + string.tostring(n) if n < 10 else string.tostring(n)

    winLabel = f_pad(iStartH) + ':' + f_pad(iStartM) + '–' + f_pad(iEndH) + ':' + f_pad(iEndM)

    rngHi: Persistent[float] = na(float)
    rngLo: Persistent[float] = na(float)
    rngStartBar: Persistent[int] = na(int)
    rngEndBar: Persistent[int] = na(int)
    locked: PersistentSeries[bool] = False
    firstSide: PersistentSeries[int] = 0
    secondSide: PersistentSeries[int] = 0
    sweepBar: Persistent[int] = na(int)
    sweepPx: Persistent[float] = na(float)
    secondBar: Persistent[int] = na(int)
    firstSigDone: PersistentSeries[bool] = False
    revSigDone: PersistentSeries[bool] = False
    firstDir: PersistentSeries[int] = 0
    revDir: PersistentSeries[int] = 0
    firstPx: Persistent[float] = na(float)
    revPx: Persistent[float] = na(float)
    oppHit: PersistentSeries[bool] = False
    ptsHit: Persistent[bool] = False
    eqHit: Persistent[bool] = False
    mmHit: Persistent[bool] = False

    nsSetup: PersistentSeries[bool] = False
    nsDir: Persistent[int] = 0
    nsEntry: Persistent[float] = na(float)
    nsSl: Persistent[float] = na(float)
    nsTp: Persistent[float] = na(float)
    nsExt50: Persistent[float] = na(float)
    nsFilled: Persistent[bool] = False
    nsSetupBar: Persistent[int] = na(int)
    lnNsEntry: Persistent[Line] = na(Line)
    lnNsSl: Persistent[Line] = na(Line)
    lnNsTp: Persistent[Line] = na(Line)
    lnNsExt: Persistent[Line] = na(Line)

    rngBox: Persistent[Box] = na(Box)
    lnHi: Persistent[Line] = na(Line)
    lnLo: Persistent[Line] = na(Line)
    lnMid: Persistent[Line] = na(Line)
    tgtBox: Persistent[Box] = na(Box)
    lnOpp: Persistent[Line] = na(Line)
    lnPts: Persistent[Line] = na(Line)
    lnMm: Persistent[Line] = na(Line)
    lnTp: Persistent[Line] = na(Line)
    lnSl: Persistent[Line] = na(Line)
    lbTp: Persistent[Label] = na(Label)
    lbSl: Persistent[Label] = na(Label)

    posDir: Persistent[int] = 0
    posEntry: Persistent[float] = na(float)
    posTp: Persistent[float] = na(float)
    posSl: Persistent[float] = na(float)
    posBar: Persistent[int] = na(int)
    posIsRev: Persistent[bool] = False
    statWins: Persistent[int] = 0
    statLoss: Persistent[int] = 0
    statExp: Persistent[int] = 0
    statWinR: Persistent[float] = 0.0
    statLossR: Persistent[float] = 0.0

    atrVal = ta.atr(iAtrLen)
    phConf = ta.pivothigh(high, iPivotL, iPivotR)
    plConf = ta.pivotlow(low, iPivotL, iPivotR)
    lastPh: Persistent[float] = na(float)
    lastPl: Persistent[float] = na(float)
    if not na(phConf):
        lastPh = phConf
    if not na(plConf):
        lastPl = plConf
    swingHiFb = ta.highest(high, iSwingLb)
    swingLoFb = ta.lowest(low, iSwingLb)

    histBoxes: Persistent[list[Box]] = array.new_box()
    histLines: Persistent[list[Line]] = array.new_line()
    histLbls: Persistent[list[Label]] = array.new_label()

    def f_cap():
        while array.size(histBoxes) > iShowDays:
            box.delete(array.shift(histBoxes))
        while array.size(histLines) > iShowDays * 10:
            line.delete(array.shift(histLines))
        __block_result_1__ = na
        while array.size(histLbls) > iShowDays * 10:
            __block_result_1__ = label.delete(array.shift(histLbls))
        return __block_result_1__

    def f_push_box(b):
        __block_result_2__ = na
        if not na(b):
            array.push(histBoxes, b)
            __block_result_2__ = f_cap()
        return __block_result_2__

    def f_push_line(l):
        __block_result_3__ = na
        if not na(l):
            __block_result_3__ = array.push(histLines, l)
        return __block_result_3__

    def f_push_lbl(l):
        __block_result_4__ = na
        if not na(l):
            __block_result_4__ = array.push(histLbls, l)
        return __block_result_4__

    if newNyDay and posDir != 0 and iExpireEod:
        statExp += 1
        posDir = 0
        posEntry = na
        posTp = na
        posSl = na
        posBar = na
        posIsRev = False
        lnTp = na
        lnSl = na
        if not na(lbTp):
            label.delete(lbTp)
            lbTp = na
        if not na(lbSl):
            label.delete(lbSl)
            lbSl = na

    if newNyDay and isWeekday:
        rngHi = na
        rngLo = na
        rngStartBar = na
        rngEndBar = na
        locked = False
        firstSide = 0
        secondSide = 0
        sweepBar = na
        sweepPx = na
        secondBar = na
        firstSigDone = False
        revSigDone = False
        firstDir = 0
        revDir = 0
        firstPx = na
        revPx = na
        oppHit = False
        ptsHit = False
        eqHit = False
        mmHit = False
        rngBox = na
        lnHi = na
        lnLo = na
        lnMid = na
        tgtBox = na
        lnOpp = na
        lnPts = na
        lnMm = na

        nsSetup = False
        nsDir = 0
        nsEntry = na
        nsSl = na
        nsTp = na
        nsExt50 = na
        nsFilled = False
        nsSetupBar = na
        lnNsEntry = na
        lnNsSl = na
        lnNsTp = na
        lnNsExt = na

    if isWeekday and inBuild:
        if na(rngHi):
            rngHi = high
            rngLo = low
            rngStartBar = bar_index
        else:
            rngHi = math.max(rngHi, high)
            rngLo = math.min(rngLo, low)
        locked = False

    justLocked = isWeekday and locked[1] == False and afterRng and (not na(rngHi))
    if justLocked:
        locked = True
        rngEndBar = bar_index

    if isWeekday and afterRng and (not na(rngHi)):
        locked = True
        if na(rngEndBar):
            rngEndBar = bar_index

    rngMid = math.avg(rngHi, rngLo) if not na(rngHi) and (not na(rngLo)) else na
    rngHgt = rngHi - rngLo if not na(rngHi) and (not na(rngLo)) else na

    if iShowBox and isWeekday and (not na(rngHi)) and (not na(rngStartBar)):
        if na(rngBox):
            rngBox = box.new(rngStartBar, rngHi, bar_index, rngLo, bgcolor=colBoxBg, border_color=colBoxBd, border_width=1, border_style=line.style_dotted)
            f_push_box(rngBox)
        else:
            box.set_top(rngBox, rngHi)
            box.set_bottom(rngBox, rngLo)
            box.set_right(rngBox, bar_index)

    if iShowExt and locked and (not na(rngHi)):
        extRight = bar_index
        if na(lnHi):
            lnHi = line.new(rngEndBar, rngHi, extRight, rngHi, color=colBoxBd, width=1, style=line.style_solid)
            lnLo = line.new(rngEndBar, rngLo, extRight, rngLo, color=colBoxBd, width=1, style=line.style_solid)
            f_push_line(lnHi)
            f_push_line(lnLo)
            if iShowMid:
                lnMid = line.new(rngStartBar, rngMid, extRight, rngMid, color=colMid, width=1, style=line.style_dashed)
                f_push_line(lnMid)
        else:
            line.set_xy2(lnHi, extRight, rngHi)
            line.set_xy2(lnLo, extRight, rngLo)
            if not na(lnMid):
                line.set_xy2(lnMid, extRight, rngMid)
                line.set_y1(lnMid, rngMid)
                line.set_y2(lnMid, rngMid)

    if iShowLabels and justLocked:
        hiName = 'OR HIGH' if string.contains(iPreset, 'ORB') or string.contains(iPreset, 'Balance') else 'TBR HIGH'
        loName = 'OR LOW' if string.contains(iPreset, 'ORB') or string.contains(iPreset, 'Balance') else 'TBR LOW'
        f_push_lbl(label.new(rngStartBar, rngHi, hiName, style=label.style_label_down, color=color.new(colHighLbl, 100), textcolor=colHighLbl, size=size.small))
        f_push_lbl(label.new(rngStartBar, rngLo, loName, style=label.style_label_up, color=color.new(colLowLbl, 100), textcolor=colLowLbl, size=size.small))
        if iShowEq:
            f_push_lbl(label.new(rngEndBar, rngMid, 'EQ 50%', style=label.style_none, textcolor=colMid, size=size.tiny))
        if iNsShowInternals and iStyle == 'NS ORB (0.125 limit)' and (not na(rngHgt)):
            f_push_lbl(label.new(rngEndBar, rngLo + 0.25 * rngHgt, '0.25', style=label.style_none, textcolor=color.gray, size=size.tiny))
            f_push_lbl(label.new(rngEndBar, rngLo + 0.75 * rngHgt, '0.75', style=label.style_none, textcolor=color.gray, size=size.tiny))

    brokeHiWick = locked and (not na(rngHi)) and (high > rngHi)
    brokeLoWick = locked and (not na(rngLo)) and (low < rngLo)
    brokeHiClose = locked and (not na(rngHi)) and (close > rngHi)
    brokeLoClose = locked and (not na(rngLo)) and (close < rngLo)
    brokeHi = brokeHiClose if iBreakMode == 'Close' else brokeHiWick
    brokeLo = brokeLoClose if iBreakMode == 'Close' else brokeLoWick

    nsStyle = iStyle == 'NS ORB (0.125 limit)'
    if nsStyle:
        brokeHi = brokeHiClose
        brokeLo = brokeLoClose
        if iNsFullBody:
            brokeHi = brokeHi and open > rngHi
            brokeLo = brokeLo and open < rngLo

    canDetect = locked and firstSide == 0 and (not na(rngHi))
    canDetect = canDetect and inSignalWin if iRequireAfterRange else canDetect and (inBuild or inSignalWin)

    if canDetect and (not nsStyle):
        if brokeHi and (not brokeLo):
            firstSide = 1
            sweepBar = bar_index
            sweepPx = high
        elif brokeLo and (not brokeHi):
            firstSide = -1
            sweepBar = bar_index
            sweepPx = low

    sweepNow = firstSide != 0 and firstSide[1] == 0

    canSecond = locked and firstSide != 0 and (secondSide == 0) and inSignalWin and (bar_index > sweepBar) and (not nsStyle)
    if canSecond:
        if firstSide == 1 and brokeLo:
            secondSide = -1
            secondBar = bar_index
        elif firstSide == -1 and brokeHi:
            secondSide = 1
            secondBar = bar_index

    secondNow = secondSide != 0 and secondSide[1] == 0

    if iShowSweeps and sweepNow and (not nsStyle):
        if firstSide == 1:
            f_push_lbl(label.new(bar_index, high, 'HIGH TAKEN', style=label.style_label_down, color=color.new(colSweep, 10), textcolor=color.black, size=size.small))
        else:
            f_push_lbl(label.new(bar_index, low, 'LOW TAKEN', style=label.style_label_up, color=color.new(colSweep, 10), textcolor=color.black, size=size.small))

    if iShowSweeps and secondNow:
        f_push_lbl(label.new(bar_index, high if secondSide == 1 else low, 'OPPOSITE TAKEN', style=label.style_label_down if secondSide == 1 else label.style_label_up, color=color.new(colRev, 10), textcolor=color.black, size=size.small))

    insideAfterSweep = firstSide != 0 and bar_index > sweepBar and (close <= rngHi) and (close >= rngLo)
    oppBear = firstSide == 1 and bar_index > sweepBar and (close < open)
    oppBull = firstSide == -1 and bar_index > sweepBar and (close > open)

    firstLongReady: bool = False
    firstShortReady: bool = False
    revLongReady: bool = False
    revShortReady: bool = False

    breakoutStyle = iStyle == 'Breakout (trade first break)' or iStyle == 'Breakout then reversal'
    fadeStyle = iStyle == 'Reversal (fade first break)'

    if firstSide != 0 and inSignalWin and (not firstSigDone) and (not nsStyle):
        rawLong = firstSide == -1 if fadeStyle else firstSide == 1
        rawShort = firstSide == 1 if fadeStyle else firstSide == -1
        __switch_1__ = iConfirm
        if __switch_1__ == "Sweep only (first break)":
            firstLongReady = rawLong and sweepNow
            firstShortReady = rawShort and sweepNow
        elif __switch_1__ == "Sweep + reclaim close":
            firstLongReady = rawLong and insideAfterSweep
            firstShortReady = rawShort and insideAfterSweep
        elif __switch_1__ == "Sweep + opposing candle":
            firstLongReady = rawLong and (oppBull if fadeStyle else close > open and bar_index > sweepBar)
            firstShortReady = rawShort and (oppBear if fadeStyle else close < open and bar_index > sweepBar)

    if firstLongReady:
        firstSigDone = True
        firstDir = 1
        firstPx = close

    if firstShortReady:
        firstSigDone = True
        firstDir = -1
        firstPx = close

    wantRev = (iStyle == 'Breakout then reversal' or iStyle == 'Reversal (fade first break)') and iAllowRev and (not nsStyle)
    if wantRev and firstSigDone and secondNow and (not revSigDone) and inSignalWin:
        if secondSide == 1:
            revShortReady = False
            revLongReady = True
        elif secondSide == -1:
            revLongReady = False
            revShortReady = True

    if revLongReady:
        revSigDone = True
        revDir = 1
        revPx = close

    if revShortReady:
        revSigDone = True
        revDir = -1
        revPx = close

    buyFirst = firstDir == 1 and firstDir[1] != 1 and firstSigDone and (not firstSigDone[1])
    sellFirst = firstDir == -1 and firstDir[1] != -1 and firstSigDone and (not firstSigDone[1])
    buyRev = revDir == 1 and revDir[1] != 1 and revSigDone and (not revSigDone[1])
    sellRev = revDir == -1 and revDir[1] != -1 and revSigDone and (not revSigDone[1])

    plotshape(iShowSignals and buyFirst, title='BUY', style=shape.labelup, location=location.belowbar, color=colBuy, textcolor=color.white, text='BUY', size=size.small)
    plotshape(iShowSignals and sellFirst, title='SELL', style=shape.labeldown, location=location.abovebar, color=colSell, textcolor=color.white, text='SELL', size=size.small)
    plotshape(iShowSignals and buyRev, title='REV BUY', style=shape.labelup, location=location.belowbar, color=colRev, textcolor=color.white, text='REV BUY', size=size.small)
    plotshape(iShowSignals and sellRev, title='REV SELL', style=shape.labeldown, location=location.abovebar, color=colRev, textcolor=color.white, text='REV SELL', size=size.small)

    nsSetupNow: bool = False
    nsFillNow: bool = False

    if nsStyle and locked and (not na(rngHgt)) and inSignalWin and (not nsSetup):
        longClose: bool = close > rngHi and (not iNsFullBody or open > rngHi)
        shortClose: bool = close < rngLo and (not iNsFullBody or open < rngLo)
        if longClose and (not shortClose):
            nsSetup = True
            nsDir = 1
            nsSetupBar = bar_index
            nsEntry = rngHi - iNsEntry * rngHgt
            nsSl = rngHi - iNsSlProt * rngHgt
            risk: float = nsEntry - nsSl
            nsTp = nsEntry + iNsTpR * risk
            nsExt50 = rngHi + 0.5 * rngHgt
            nsSetupNow = True
        elif shortClose and (not longClose):
            nsSetup = True
            nsDir = -1
            nsSetupBar = bar_index
            nsEntry = rngLo + iNsEntry * rngHgt
            nsSl = rngLo + iNsSlProt * rngHgt
            risk: float = nsSl - nsEntry
            nsTp = nsEntry - iNsTpR * risk
            nsExt50 = rngLo - 0.5 * rngHgt
            nsSetupNow = True

    if nsSetupNow and iShowSignals:
        setupTxt: str = 'NS SETUP LONG' if nsDir == 1 else 'NS SETUP SHORT'
        f_push_lbl(label.new(bar_index, high if nsDir == 1 else low, setupTxt, style=label.style_label_down if nsDir == 1 else label.style_label_up, color=color.new(colBuy if nsDir == 1 else colSell, 0), textcolor=color.white, size=size.small))

        lnNsEntry = line.new(bar_index, nsEntry, bar_index, nsEntry, color=colNsEntry, width=2, style=line.style_solid)
        lnNsSl = line.new(bar_index, nsSl, bar_index, nsSl, color=colSell, width=1, style=line.style_dashed)
        lnNsTp = line.new(bar_index, nsTp, bar_index, nsTp, color=colBuy, width=1, style=line.style_dashed)
        f_push_line(lnNsEntry)
        f_push_line(lnNsSl)
        f_push_line(lnNsTp)
        if iNsShowExt50:
            lnNsExt = line.new(bar_index, nsExt50, bar_index, nsExt50, color=colNsExt, width=1, style=line.style_dotted)
            f_push_line(lnNsExt)
        f_push_lbl(label.new(bar_index, nsEntry, '0.125 ENTRY', style=label.style_none, textcolor=colNsEntry, size=size.tiny))
        f_push_lbl(label.new(bar_index, nsSl, 'SL 95%', style=label.style_none, textcolor=colSell, size=size.tiny))
        f_push_lbl(label.new(bar_index, nsTp, 'TP 0.4R', style=label.style_none, textcolor=colBuy, size=size.tiny))
        if iNsShowExt50:
            f_push_lbl(label.new(bar_index, nsExt50, '50% EXT', style=label.style_none, textcolor=colNsExt, size=size.tiny))

    if nsSetup and (not nsFilled) and inSignalWin and (not na(lnNsEntry)):
        line.set_x2(lnNsEntry, bar_index)
        if not na(lnNsSl):
            line.set_x2(lnNsSl, bar_index)
        if not na(lnNsTp):
            line.set_x2(lnNsTp, bar_index)
        if not na(lnNsExt):
            line.set_x2(lnNsExt, bar_index)

    if nsSetup and (not nsFilled) and inSignalWin and (bar_index > nsSetupBar):
        filled: bool = low <= nsEntry if nsDir == 1 else high >= nsEntry
        if filled:
            nsFilled = True
            nsFillNow = True
            if iShowSignals:
                f_push_lbl(label.new(bar_index, nsEntry, 'NS FILLED LONG' if nsDir == 1 else 'NS FILLED SHORT', style=label.style_label_up if nsDir == 1 else label.style_label_down, color=color.new(colBuy if nsDir == 1 else colSell, 0), textcolor=color.white, size=size.small))

    if nsSetup and (not nsFilled) and (not inSignalWin) and nsSetup[1]:
        f_push_lbl(label.new(bar_index, nsEntry, 'NS EXPIRED', style=label.style_none, textcolor=color.gray, size=size.tiny))

    def f_swing_sl(dir, entry):
        buf = nz(atrVal, 0.0) * iSwingBufAtr
        slPx: float = na(float)
        if dir == 1:
            pv = lastPl if not na(lastPl) and lastPl < entry else swingLoFb
            slPx = pv - buf
        else:
            pv = lastPh if not na(lastPh) and lastPh > entry else swingHiFb
            slPx = pv + buf
        return slPx

    def f_final_sl(dir, entry):
        atrSl = entry - dir * iSlAtr * nz(atrVal, 0.0)
        swSl = f_swing_sl(dir, entry)
        slPx: float = atrSl
        if iSlMode == 'ATR':
            slPx = atrSl
        elif iSlMode == 'Swing / pivot':
            slPx = swSl
        elif iSlMode == 'Tighter of ATR or swing':
            slPx = math.max(atrSl, swSl) if dir == 1 else math.min(atrSl, swSl)
        else:
            slPx = math.min(atrSl, swSl) if dir == 1 else math.max(atrSl, swSl)

        if dir == 1 and slPx >= entry:
            slPx = atrSl
        if dir == -1 and slPx <= entry:
            slPx = atrSl
        return slPx

    tpHitNow: bool = False
    slHitNow: bool = False

    if posDir != 0 and bar_index > posBar and (not na(posTp)) and (not na(posSl)):
        slHitNow = low <= posSl if posDir == 1 else high >= posSl
        tpHitNow = high >= posTp if posDir == 1 else low <= posTp
        if slHitNow and tpHitNow:
            slHitNow = True
            tpHitNow = False
            statLoss += 1
            statLossR += 1.0
            if iShowTpsl and (not na(lbSl)):
                label.set_xy(lbSl, bar_index, posSl)
                label.set_text(lbSl, 'SL HIT  ' + string.tostring(posSl, format.mintick))
                label.set_style(lbSl, label.style_label_left)
                label.set_color(lbSl, color.new(colSell, 0))
                label.set_textcolor(lbSl, color.white)
                label.set_size(lbSl, size.small)
            if not na(lbTp):
                label.delete(lbTp)
                lbTp = na
            posDir = 0
        elif slHitNow:
            statLoss += 1
            statLossR += 1.0
            if iShowTpsl and (not na(lbSl)):
                label.set_xy(lbSl, bar_index, posSl)
                label.set_text(lbSl, 'SL HIT  ' + string.tostring(posSl, format.mintick))
                label.set_style(lbSl, label.style_label_left)
                label.set_color(lbSl, color.new(colSell, 0))
                label.set_textcolor(lbSl, color.white)
                label.set_size(lbSl, size.small)
            if not na(lbTp):
                label.delete(lbTp)
                lbTp = na
            posDir = 0
        elif tpHitNow:
            risk = math.abs(posEntry - posSl)
            reward = math.abs(posTp - posEntry)
            statWins += 1
            statWinR += reward / risk if risk > 0 else iTpAtr / iSlAtr
            if iShowTpsl and (not na(lbTp)):
                label.set_xy(lbTp, bar_index, posTp)
                label.set_text(lbTp, 'TP HIT  ' + string.tostring(posTp, format.mintick))
                label.set_style(lbTp, label.style_label_left)
                label.set_color(lbTp, color.new(colBuy, 0))
                label.set_textcolor(lbTp, color.white)
                label.set_size(lbTp, size.small)
            if not na(lbSl):
                label.delete(lbSl)
                lbSl = na
            posDir = 0

    openNow = buyFirst or sellFirst or (iStatsOnRev and (buyRev or sellRev)) or nsFillNow
    openDir = 1 if buyFirst or buyRev or (nsFillNow and nsDir == 1) else -1 if sellFirst or sellRev or (nsFillNow and nsDir == -1) else 0
    openIsRev = buyRev or sellRev

    if openNow and openDir != 0:
        if posDir != 0:
            statExp += 1
            posDir = 0

        if nsFillNow and nsStyle:
            posDir = nsDir
            posEntry = nsEntry
            posTp = nsTp
            posSl = nsSl
            posBar = bar_index
            posIsRev = False
            if iShowTpsl:
                lnTp = line.new(bar_index, posTp, bar_index, posTp, color=color.new(colBuy, 0), width=2, style=line.style_solid)
                lnSl = line.new(bar_index, posSl, bar_index, posSl, color=color.new(colSell, 0), width=2, style=line.style_solid)
                f_push_line(lnTp)
                f_push_line(lnSl)
                if not na(lbTp):
                    label.delete(lbTp)
                if not na(lbSl):
                    label.delete(lbSl)
                lbTp = label.new(bar_index, posTp, 'TP 0.4R  ' + string.tostring(posTp, format.mintick), style=label.style_label_left, color=color.new(colBuy, 0), textcolor=color.white, size=size.small, textalign=text.align_left, tooltip='NS Take profit')
                lbSl = label.new(bar_index, posSl, 'SL 95%  ' + string.tostring(posSl, format.mintick), style=label.style_label_left, color=color.new(colSell, 0), textcolor=color.white, size=size.small, textalign=text.align_left, tooltip='NS Stop loss')
        else:
            atrNow = nz(atrVal, 0.0)
            if atrNow > 0:
                posDir = openDir
                posEntry = close
                posTp = close + openDir * iTpAtr * atrNow
                posSl = f_final_sl(openDir, close)
                posBar = bar_index
                posIsRev = openIsRev
                if iShowTpsl:
                    lnTp = line.new(bar_index, posTp, bar_index, posTp, color=color.new(colBuy, 0), width=2, style=line.style_solid)
                    lnSl = line.new(bar_index, posSl, bar_index, posSl, color=color.new(colSell, 0), width=2, style=line.style_solid)
                    f_push_line(lnTp)
                    f_push_line(lnSl)
                    slTag = 'SL  ' + string.tostring(iSlAtr, '#.##') + '×ATR   ' + string.tostring(posSl, format.mintick) if iSlMode == 'ATR' else 'SL  SWING   ' + string.tostring(posSl, format.mintick)
                    tpTag = 'TP  ' + string.tostring(iTpAtr, '#.##') + '×ATR   ' + string.tostring(posTp, format.mintick)
                    if not na(lbTp):
                        label.delete(lbTp)
                    if not na(lbSl):
                        label.delete(lbSl)
                    lbTp = label.new(bar_index, posTp, tpTag, style=label.style_label_left, color=color.new(colBuy, 0), textcolor=color.white, size=size.small, textalign=text.align_left, tooltip='Take profit')
                    lbSl = label.new(bar_index, posSl, slTag, style=label.style_label_left, color=color.new(colSell, 0), textcolor=color.white, size=size.small, textalign=text.align_left, tooltip='Stop loss')

    if posDir != 0 and iShowTpsl:
        slTagLive = 'SL 95%  ' + string.tostring(posSl, format.mintick) if nsStyle and nsFilled else 'SL  ' + string.tostring(iSlAtr, '#.##') + '×ATR   ' + string.tostring(posSl, format.mintick) if iSlMode == 'ATR' else 'SL  SWING   ' + string.tostring(posSl, format.mintick)
        tpTagLive = 'TP 0.4R  ' + string.tostring(posTp, format.mintick) if nsStyle and nsFilled else 'TP  ' + string.tostring(iTpAtr, '#.##') + '×ATR   ' + string.tostring(posTp, format.mintick)
        if not na(lnTp):
            line.set_xy2(lnTp, bar_index, posTp)
            line.set_y1(lnTp, posTp)
            line.set_color(lnTp, color.new(colBuy, 0))
        if not na(lnSl):
            line.set_xy2(lnSl, bar_index, posSl)
            line.set_y1(lnSl, posSl)
            line.set_color(lnSl, color.new(colSell, 0))
        if not na(lbTp):
            label.set_xy(lbTp, bar_index, posTp)
            label.set_text(lbTp, tpTagLive)
            label.set_style(lbTp, label.style_label_left)
            label.set_color(lbTp, color.new(colBuy, 0))
            label.set_textcolor(lbTp, color.white)
            label.set_size(lbTp, size.small)
        if not na(lbSl):
            label.set_xy(lbSl, bar_index, posSl)
            label.set_text(lbSl, slTagLive)
            label.set_style(lbSl, label.style_label_left)
            label.set_color(lbSl, color.new(colSell, 0))
            label.set_textcolor(lbSl, color.white)
            label.set_size(lbSl, size.small)

    statClosed = statWins + statLoss
    winRate = 100.0 * statWins / statClosed if statClosed > 0 else na

    activeDir = revDir if revSigDone else firstDir
    activePx = revPx if revSigDone else firstPx
    justSig = buyFirst or sellFirst or buyRev or sellRev

    longTgtOpp = rngHi
    shortTgtOpp = rngLo
    longTgtPts = activePx + tgtPts
    shortTgtPts = activePx - tgtPts
    longTgtMm = rngHi + rngHgt
    shortTgtMm = rngLo - rngHgt

    if justSig and iShowTgtBox and (not na(rngHi)) and (not nsStyle):
        tgtTop = longTgtOpp if activeDir == 1 else activePx
        tgtBot = activePx if activeDir == 1 else shortTgtOpp
        if fadeStyle or buyRev or sellRev or (not breakoutStyle):
            tgtBox = box.new(bar_index, tgtTop, bar_index + 1, tgtBot, bgcolor=colTgtLong if activeDir == 1 else colTgtShrt, border_color=colBuy if activeDir == 1 else colSell, border_width=1, border_style=line.style_dotted)
            f_push_box(tgtBox)
        else:
            bt = math.max(longTgtPts, nz(longTgtMm, longTgtPts)) if activeDir == 1 else activePx
            bb = activePx if activeDir == 1 else math.min(shortTgtPts, nz(shortTgtMm, shortTgtPts))
            tgtBox = box.new(bar_index, bt, bar_index + 1, bb, bgcolor=colTgtLong if activeDir == 1 else colTgtShrt, border_color=colBuy if activeDir == 1 else colSell, border_width=1, border_style=line.style_dotted)
            f_push_box(tgtBox)

    if locked and firstSigDone and (not na(tgtBox)) and (not nsStyle):
        box.set_right(tgtBox, bar_index)

    if iShowOpp and justSig and (not nsStyle):
        oppY = longTgtOpp if activeDir == 1 else shortTgtOpp
        lnOpp = line.new(bar_index, oppY, bar_index + 1, oppY, color=colBuy if activeDir == 1 else colSell, width=2)
        f_push_line(lnOpp)
        f_push_lbl(label.new(bar_index, oppY, 'OPP END', style=label.style_label_down if activeDir == 1 else label.style_label_up, color=color.new(colBuy if activeDir == 1 else colSell, 0), textcolor=color.white, size=size.tiny))
    if not na(lnOpp):
        line.set_x2(lnOpp, bar_index)

    if iShowPts and justSig and (not nsStyle):
        ptsY = longTgtPts if activeDir == 1 else shortTgtPts
        lnPts = line.new(bar_index, ptsY, bar_index + 1, ptsY, color=colSweep, width=1, style=line.style_dashed)
        f_push_line(lnPts)
        f_push_lbl(label.new(bar_index, ptsY, string.tostring(tgtPts, '#.##') + ' PTS ' + iMkt, style=label.style_none, textcolor=colSweep, size=size.tiny))
    if not na(lnPts):
        line.set_x2(lnPts, bar_index)

    if iShowMM and justSig and (not na(rngHgt)) and (not nsStyle):
        mmY = longTgtMm if activeDir == 1 else shortTgtMm
        lnMm = line.new(bar_index, mmY, bar_index + 1, mmY, color=colRev, width=1, style=line.style_dotted)
        f_push_line(lnMm)
    if not na(lnMm):
        line.set_x2(lnMm, bar_index)

    if firstSigDone and (not oppHit) and (not na(rngHi)) and (not nsStyle):
        if firstDir == 1 and high >= rngHi:
            oppHit = True
            if iShowSignals:
                f_push_lbl(label.new(bar_index, rngHi, 'HIGH TGT', style=label.style_label_down, color=colBuy, textcolor=color.white, size=size.tiny))
        if firstDir == -1 and low <= rngLo:
            oppHit = True
            if iShowSignals:
                f_push_lbl(label.new(bar_index, rngLo, 'LOW TGT', style=label.style_label_up, color=colSell, textcolor=color.white, size=size.tiny))

    if firstSigDone and (not ptsHit) and iShowPts and (not nsStyle):
        if firstDir == 1 and high >= firstPx + tgtPts:
            ptsHit = True
        if firstDir == -1 and low <= firstPx - tgtPts:
            ptsHit = True

    if firstSigDone and (not eqHit) and (not na(rngMid)) and (not nsStyle):
        if firstDir == 1 and high >= rngMid:
            eqHit = True
        if firstDir == -1 and low <= rngMid:
            eqHit = True

    if firstSigDone and (not mmHit) and iShowMM and (not na(rngHgt)) and (not nsStyle):
        if firstDir == 1 and high >= rngHi + rngHgt:
            mmHit = True
        if firstDir == -1 and low <= rngLo - rngHgt:
            mmHit = True

    def f_pos():
        __block_result_5__ = na
        __switch__ = iTablePos
        if __switch__ == "Top Left":
            __block_result_5__ = position.top_left
        elif __switch__ == "Bottom Right":
            __block_result_5__ = position.bottom_right
        elif __switch__ == "Bottom Left":
            __block_result_5__ = position.bottom_left
        else:
            __block_result_5__ = position.top_right
        return __block_result_5__

    tbl: Persistent[Table] = table.new(f_pos(), 2, 13, bgcolor=color.new(color.new('#0D0D0D'), 12), border_color=color.new(color.new('#444444'), 0), border_width=1, frame_color=color.new(color.new('#333333'), 0), frame_width=1)

    def f_cell(c, r, txt, bg, tc):
        return table.cell(tbl, c, r, txt, text_color=tc, bgcolor=bg, text_size=size.small, text_halign=text.align_left)

    if iShowTable and barstate.islast:
        phase = 'Weekend' if not isWeekday else 'Building ' + winLabel if inBuild else 'Waiting for window' if not locked else 'NS setup — waiting fill' if nsStyle and nsSetup and (not nsFilled) else 'NS filled' if nsStyle and nsFilled else 'Locked — wait for break' if firstSide == 0 else 'Side taken — wait confirm' if not firstSigDone else 'Reversal printed' if secondSide != 0 and revSigDone else 'Opposite taken' if secondSide != 0 else 'Range target tagged' if oppHit else 'In trade / manage'
        sideTxt = 'HIGH first' + (' → LOW next' if secondSide == -1 else '') if firstSide == 1 else 'LOW first' + (' → HIGH next' if secondSide == 1 else '') if firstSide == -1 else ('NS LONG setup' if nsDir == 1 else 'NS SHORT setup') if nsStyle and nsSetup else '—'
        sigTxt = ('NS FILLED LONG' if nsDir == 1 else 'NS FILLED SHORT') if nsStyle and nsFilled else ('REV BUY' if revDir == 1 else 'REV SELL') if revSigDone else 'BUY' if firstDir == 1 else 'SELL' if firstDir == -1 else 'NS SETUP' if nsStyle and nsSetup else 'None yet'
        rngTxt = '—' if na(rngHi) else string.tostring(rngHi, format.mintick) + ' / ' + string.tostring(rngLo, format.mintick)
        hgtTxt = '—' if na(rngHgt) else string.tostring(rngHgt, format.mintick)
        hdrBg = color.new(color.new('#6B1212'), 20)
        f_cell(0, 0, iMkt + '  ' + winLabel, hdrBg, color.white)
        f_cell(1, 0, '34ematrader', hdrBg, color.new(color.new('#FFD54F'), 0))
        f_cell(0, 1, 'Preset / style', color.new(color.new('#1A1A1A'), 0), color.gray)
        f_cell(1, 1, iPreset + '  ·  ' + iStyle, color.new(color.new('#1A1A1A'), 0), color.white)
        f_cell(0, 2, 'Phase', color.new(color.new('#111111'), 0), color.gray)
        f_cell(1, 2, phase, color.new(color.new('#111111'), 0), color.white)
        f_cell(0, 3, 'Range Hi / Lo', color.new(color.new('#1A1A1A'), 0), color.gray)
        f_cell(1, 3, rngTxt, color.new(color.new('#1A1A1A'), 0), color.white)
        f_cell(0, 4, 'Height / pts', color.new(color.new('#111111'), 0), color.gray)
        f_cell(1, 4, hgtTxt + '   |   ' + string.tostring(tgtPts, '#.##') + ' ' + iMkt, color.new(color.new('#111111'), 0), color.white)
        f_cell(0, 5, 'Breaks', color.new(color.new('#1A1A1A'), 0), color.gray)
        f_cell(1, 5, sideTxt, color.new(color.new('#1A1A1A'), 0), colSell if firstSide == 1 else colBuy if firstSide == -1 else colBuy if nsDir == 1 else colSell if nsDir == -1 else color.gray)
        f_cell(0, 6, 'Signal', color.new(color.new('#111111'), 0), color.gray)
        f_cell(1, 6, sigTxt, color.new(color.new('#111111'), 0), colRev if revSigDone else colBuy if firstDir == 1 or nsDir == 1 else colSell if firstDir == -1 or nsDir == -1 else color.gray)
        f_cell(0, 7, 'Targets hit', color.new(color.new('#1A1A1A'), 0), color.gray)
        hitStr = ('END ✓  ' if oppHit else 'END ·  ') + ('PTS ✓  ' if ptsHit else 'PTS ·  ') + ('EQ ✓' if eqHit else 'EQ ·')
        f_cell(1, 7, hitStr, color.new(color.new('#1A1A1A'), 0), color.white)
        f_cell(0, 8, 'TP / SL', color.new(color.new('#111111'), 0), color.gray)
        slTxt = 'NS 95% / 0.4R' if nsStyle else string.tostring(iSlAtr, '#.##') + ' ATR' if iSlMode == 'ATR' else iSlMode
        f_cell(1, 8, '0.4R / 95% range' if nsStyle else string.tostring(iTpAtr, '#.##') + ' ATR  /  ' + slTxt, color.new(color.new('#111111'), 0), color.white)
        wrCol = color.gray if na(winRate) else colBuy if winRate >= 50 else colSell
        wrTxt = '—' if na(winRate) else string.tostring(winRate, '#.#') + '%'
        f_cell(0, 9, 'Win rate', color.new(color.new('#1A1A1A'), 0), color.gray)
        f_cell(1, 9, wrTxt + '   ' + string.tostring(statWins) + 'W / ' + string.tostring(statLoss) + 'L / ' + string.tostring(statExp) + 'exp', color.new(color.new('#1A1A1A'), 0), wrCol)
        avgR = (statWinR - statLossR) / statClosed if statClosed > 0 else na
        f_cell(0, 10, 'Avg R  (closed)', color.new(color.new('#111111'), 0), color.gray)
        f_cell(1, 10, '—' if na(avgR) else string.tostring(avgR, '#.##') + ' R', color.new(color.new('#111111'), 0), color.white)
        posTxt = 'Flat' if posDir == 0 else ('LONG @ ' if posDir == 1 else 'SHORT @ ') + string.tostring(posEntry, format.mintick)
        f_cell(0, 11, 'Paper trade', color.new(color.new('#1A1A1A'), 0), color.gray)
        f_cell(1, 11, posTxt, color.new(color.new('#1A1A1A'), 0), colBuy if posDir == 1 else colSell if posDir == -1 else color.gray)
        nsTxt = ('Filled' if nsFilled else 'Waiting fill until ' + f_pad(iSignalUntilH) + ':' + f_pad(iSignalUntilM)) if nsStyle and nsSetup else '—'
        f_cell(0, 12, 'NS status', color.new(color.new('#111111'), 0), color.gray)
        f_cell(1, 12, nsTxt, color.new(color.new('#111111'), 0), colBuy if nsFilled else color.gray)

    alertcondition(iAlertSweep and sweepNow and (firstSide == 1), title='Range HIGH taken', message='Range HIGH taken')
    alertcondition(iAlertSweep and sweepNow and (firstSide == -1), title='Range LOW taken', message='Range LOW taken')
    alertcondition(iAlertSig and buyFirst, title='BUY', message='Time-range BUY')
    alertcondition(iAlertSig and sellFirst, title='SELL', message='Time-range SELL')
    alertcondition(iAlertRev and buyRev, title='REV BUY', message='Reversal BUY — opposite side taken')
    alertcondition(iAlertRev and sellRev, title='REV SELL', message='Reversal SELL — opposite side taken')
    alertcondition(iAlertTgt and oppHit and (not oppHit[1]), title='Range end tagged', message='Opposing range end tagged')
    alertcondition(tpHitNow, title='ATR TP hit', message='Paper trade take profit hit')
    alertcondition(slHitNow, title='SL hit', message='Paper trade stop loss hit')
    alertcondition(iAlertNs and nsSetupNow, title='NS ORB Setup', message='NS ORB setup — limit placed at 0.125')
    alertcondition(iAlertNs and nsFillNow, title='NS ORB Fill', message='NS ORB limit filled')

    plot(rngHi, 'Range High', color=color.new(colBoxBd, 100), display=display.data_window)
    plot(rngLo, 'Range Low', color=color.new(colBoxBd, 100), display=display.data_window)
    plot(rngMid, 'Range Mid', color=color.new(colMid, 100), display=display.data_window)
    plot(firstDir, 'First Dir', display=display.data_window)
    plot(revDir, 'Rev Dir', display=display.data_window)
    plot(nsDir, 'NS Dir', display=display.data_window)
    plot(nsEntry, 'NS Entry', display=display.data_window)
    plot(nsTp, 'NS TP', display=display.data_window)
    plot(nsSl, 'NS SL', display=display.data_window)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)