"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore import pine_range
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barstate, close, color, display, extend, high, input,
    label, line, low, math, na, open, plotcandle, request, script, size, string, syminfo, time,
    timeframe, volume, xloc
)
from pynecore.types import Color, Line, NA, Persistent


@udt
class PxT:
    p: float = na(float)
    t: int = na(int)


@udt
class SwBar:
    h: 'PxT' = _dataclass_field(default_factory=lambda: na(PxT))
    l: 'PxT' = _dataclass_field(default_factory=lambda: na(PxT))


sTfTip: str = "Timeframe used to detect swing highs/lows."
volDelTip: str = "Lower timeframe used to estimate buy vs sell volume for the breakout candle."
brModeTip: str = "Choose whether a level is considered broken by candle wicks or by candle close."
showNeTip: str = "Limits how many most recent swing high/low levels shown on the chart."
brVolFiltTip: str = "Only count breakouts when the breakout candle has enough bull/bear volume dominance."
grpSw: str = "GENERAL CONFIGURATION"
grpLn: str = "Styling"
disp = display.none


@script.indicator("Breakout Volume Delta | Flux Charts", overlay=True, max_lines_count=500, max_labels_count=500, behind_chart=False)
def main(
    swLenL=input.int(10, "Swing Left", minval=1, group=grpSw, inline="sw", display=disp),
    swLenR=input.int(10, "Right", minval=1, group=grpSw, inline="sw", display=disp),
    swTfIn=input.timeframe("", "Swing Timeframe", tooltip=sTfTip, group=grpSw, display=disp),
    vdLtf=input.timeframe("1", "Volume Delta LTF", tooltip=volDelTip, group=grpSw, display=disp),
    brMode=input.string("Close", "Breakout by", options=("Close", "Wick"), tooltip=brModeTip, group=grpSw, display=disp),
    maxLvls=input.int(5, "Show Nearest", minval=1, tooltip=showNeTip, group=grpSw, display=disp),
    brVolFiltOn=input.bool(False, "Breakout Volume Filter", tooltip=brVolFiltTip, group=grpSw, inline="bv", display=disp),
    brVolFiltPctIn=input.float(60.0, "", minval=0.0, maxval=100.0, step=0.5, group=grpSw, inline="bv", display=disp),
    unmitStyleIn=input.string("Dotted", "Unmitigated Levels", options=("Solid", "Dashed", "Dotted"), group=grpLn, inline="unm", display=disp),
    unmitW=input.int(1, "", minval=1, maxval=4, group=grpLn, inline="unm", display=disp),
    unmitHiCol=input.color(color.new(color.lime, 0), "", group=grpLn, inline="unm", display=disp),
    unmitLoCol=input.color(color.new(color.red, 0), "", group=grpLn, inline="unm", display=disp),
    brkStyleIn=input.string("Solid", "Broken Levels", options=("Solid", "Dashed", "Dotted"), group=grpLn, inline="brk", display=disp),
    brkW=input.int(1, "", minval=1, maxval=4, group=grpLn, inline="brk", display=disp),
    brkHiCol=input.color(color.new(color.lime, 0), "", group=grpLn, inline="brk", display=disp),
    brkLoCol=input.color(color.new(color.red, 0), "", group=grpLn, inline="brk", display=disp),
    bullBase=input.color(color.new(color.new('#00FF6A'), 0), "Volume Delta", group=grpLn, inline="vd", display=disp),
    bearBase=input.color(color.new(color.new('#FF2D55'), 0), "", group=grpLn, inline="vd", display=disp),
    extendBars=input.int(5, "Extend Levels", minval=1, group=grpLn, inline="ext11", display=disp),
    extendRight=input.bool(False, "Extend Right", group=grpLn, inline="ext", display=disp),
    dbgShow=input.bool(True, "Volume Delta Labels", group=grpLn, inline="ext", display=disp)
):
    linesHi: Persistent[list[Line]] = array.new_line()
    pricesHi: Persistent[list[float]] = array.new_float()
    mitigHi: Persistent[list[bool]] = array.new_bool()

    linesLo: Persistent[list[Line]] = array.new_line()
    pricesLo: Persistent[list[float]] = array.new_float()
    mitigLo: Persistent[list[bool]] = array.new_bool()

    swHist: Persistent[list[SwBar]] = array.new(0, NA(SwBar))

    swTfPrev: Persistent[str] = ""
    swInited: Persistent[bool] = False
    swCur: Persistent[SwBar] = na(SwBar)

    lastPhT: Persistent[int] = na(int)
    lastPlT: Persistent[int] = na(int)

    fillOpen: float = na(float)
    fillHigh: float = na(float)
    fillLow: float = na(float)
    fillClose: float = na(float)
    fillCol: Color = na(Color)

    oppOpen: float = na(float)
    oppHigh: float = na(float)
    oppLow: float = na(float)
    oppClose: float = na(float)
    oppCol: Color = na(Color)

    breakOutlineCol: Color = na(Color)

    dbgDoLabel: Persistent[bool] = False
    dbgIsBull: Persistent[bool] = False
    dbgLblTxt: Persistent[str] = ""
    dbgLblY: Persistent[float] = na(float)

    def fLineStyle(s: str):
        return line.style_solid if s == 'Solid' else line.style_dashed if s == 'Dashed' else line.style_dotted

    def fFmt(v: float):
        av: float = math.abs(v)
        suf: str = 'B' if av >= 1000000000.0 else 'M' if av >= 1000000.0 else 'K' if av >= 1000.0 else ''
        div: float = 1000000000.0 if av >= 1000000000.0 else 1000000.0 if av >= 1000000.0 else 1000.0 if av >= 1000.0 else 1.0
        s: str = string.tostring(v / div, '#.##' if av >= 1000.0 else '#')
        return s + suf

    def fPctStr(pct01: float):
        p: float = math.max(0.0, math.min(1.0, pct01)) * 100.0
        return string.tostring(p, '#.#') + '%'

    def fBullVolSum(ltf: str):
        arr = request.security_lower_tf(syminfo.tickerid, ltf, volume if close > open else 0.0)
        sum: float = 0.0
        n: int = array.size(arr)
        if n > 0:
            for i in pine_range(0, n - 1):
                sum += array.get(arr, i)
        return sum

    def fBearVolSum(ltf: str):
        arr = request.security_lower_tf(syminfo.tickerid, ltf, volume if close < open else 0.0)
        sum: float = 0.0
        n: int = array.size(arr)
        if n > 0:
            for i in pine_range(0, n - 1):
                sum += array.get(arr, i)
        return sum

    def tfResolve(tfIn: str):
        tf: str = timeframe.period if tfIn == '' else tfIn
        chartSec: int = timeframe.in_seconds(timeframe.period)
        wantSec: int = timeframe.in_seconds(tf)
        return timeframe.period if not na(chartSec) and (not na(wantSec)) and (wantSec < chartSec) else tf

    def pxNew(p: float, t: int):
        return PxT(p, t)

    def swBarEmpty():
        return SwBar(pxNew(na, na), pxNew(na, na))

    def fTrim():
        while array.size(linesHi) > maxLvls:
            line.delete(array.shift(linesHi))
            array.shift(pricesHi)
            array.shift(mitigHi)
        __block_result__ = na
        while array.size(linesLo) > maxLvls:
            line.delete(array.shift(linesLo))
            array.shift(pricesLo)
            __block_result__ = array.shift(mitigLo)
        return __block_result__

    chartSec: int = timeframe.in_seconds(timeframe.period)
    barMs: int = 60000 if na(chartSec) else chartSec * 1000
    extX2: int = time + extendBars * barMs

    swTf: str = tfResolve(swTfIn)
    unmitStyle: str = fLineStyle(unmitStyleIn)

    if na(swCur):
        swCur = swBarEmpty()

    if barstate.isfirst or swTfPrev != swTf:
        swTfPrev = swTf
        swInited = False
        swCur = swBarEmpty()
        array.clear(swHist)

    swNewTf: bool = timeframe.change(swTf)

    if swNewTf and swInited:
        array.unshift(swHist, swCur)

        keepN: int = math.max(50, swLenL + swLenR + 10)
        while array.size(swHist) > keepN:
            array.pop(swHist)

        swInited = False
        swCur = swBarEmpty()

    if not swInited:
        swCur.h = pxNew(high, time)
        swCur.l = pxNew(low, time)
        swInited = True
    else:
        if na(swCur.h.p) or high > swCur.h.p:
            swCur.h = pxNew(high, time)
        if na(swCur.l.p) or low < swCur.l.p:
            swCur.l = pxNew(low, time)

    gotPivotEvent: bool = swNewTf and array.size(swHist) >= swLenL + swLenR + 1

    if gotPivotEvent:
        r: int = swLenR
        l: int = swLenL

        cand: SwBar = array.get(swHist, r)

        candH: float = cand.h.p
        candL: float = cand.l.p

        isPh: bool = not na(candH)
        isPl: bool = not na(candL)

        for j in pine_range(0, r - 1):
            b: SwBar = array.get(swHist, j)
            if isPh and (not na(b.h.p)) and (candH <= b.h.p):
                isPh = False
            if isPl and (not na(b.l.p)) and (candL >= b.l.p):
                isPl = False

        for j in pine_range(r + 1, r + l):
            b: SwBar = array.get(swHist, j)
            if isPh and (not na(b.h.p)) and (candH <= b.h.p):
                isPh = False
            if isPl and (not na(b.l.p)) and (candL >= b.l.p):
                isPl = False

        if isPh and (na(lastPhT) or cand.h.t != lastPhT):
            y: float = candH
            ln: Line = line.new(x1=cand.h.t, y1=y, x2=time if extendRight else extX2, y2=y, xloc=xloc.bar_time, extend=extend.right if extendRight else extend.none, style=unmitStyle, width=unmitW, color=unmitHiCol)
            array.push(linesHi, ln)
            array.push(pricesHi, y)
            array.push(mitigHi, False)
            fTrim()
            lastPhT = cand.h.t

        if isPl and (na(lastPlT) or cand.l.t != lastPlT):
            y: float = candL
            ln: Line = line.new(x1=cand.l.t, y1=y, x2=time if extendRight else extX2, y2=y, xloc=xloc.bar_time, extend=extend.right if extendRight else extend.none, style=unmitStyle, width=unmitW, color=unmitLoCol)
            array.push(linesLo, ln)
            array.push(pricesLo, y)
            array.push(mitigLo, False)
            fTrim()
            lastPlT = cand.l.t

    bullVol: float = fBullVolSum(vdLtf)
    bearVol: float = fBearVolSum(vdLtf)
    totalVol: float = bullVol + bearVol

    bullPct: float = bullVol / totalVol if totalVol > 0 else 0.5
    bullPct = math.max(0.0, math.min(1.0, bullPct))
    bearPct: float = 1.0 - bullPct if totalVol > 0 else 0.5
    bearPct = math.max(0.0, math.min(1.0, bearPct))

    brVolThr: float = math.max(0.0, math.min(1.0, brVolFiltPctIn / 100.0))

    useWick: bool = brMode == 'Wick'
    didHighBreak: bool = False
    didLowBreak: bool = False

    brkStyle: str = fLineStyle(brkStyleIn)

    hiCount: int = array.size(linesHi)
    if hiCount > 0:
        for i in pine_range(hiCount - 1, 0, 1):
            if not array.get(mitigHi, i):
                lvl: float = array.get(pricesHi, i)
                br: bool = high > lvl if useWick else close > lvl
                if br:
                    volOk: bool = not brVolFiltOn or bullPct > brVolThr
                    if brVolFiltOn and (not volOk):
                        lnDel: Line = array.get(linesHi, i)
                        line.delete(lnDel)
                        array.remove(linesHi, i)
                        array.remove(pricesHi, i)
                        array.remove(mitigHi, i)
                    else:
                        array.set(mitigHi, i, True)
                        ln: Line = array.get(linesHi, i)
                        line.set_style(ln, brkStyle)
                        line.set_width(ln, brkW)
                        line.set_color(ln, brkHiCol)
                        line.set_extend(ln, extend.none)
                        line.set_x2(ln, time)
                        line.set_y2(ln, lvl)
                        didHighBreak = True

    loCount: int = array.size(linesLo)
    if loCount > 0:
        for i in pine_range(loCount - 1, 0, 1):
            if not array.get(mitigLo, i):
                lvl: float = array.get(pricesLo, i)
                br: bool = low < lvl if useWick else close < lvl
                if br:
                    volOk: bool = not brVolFiltOn or bearPct > brVolThr
                    if brVolFiltOn and (not volOk):
                        lnDel: Line = array.get(linesLo, i)
                        line.delete(lnDel)
                        array.remove(linesLo, i)
                        array.remove(pricesLo, i)
                        array.remove(mitigLo, i)
                    else:
                        array.set(mitigLo, i, True)
                        ln: Line = array.get(linesLo, i)
                        line.set_style(ln, brkStyle)
                        line.set_width(ln, brkW)
                        line.set_color(ln, brkLoCol)
                        line.set_extend(ln, extend.none)
                        line.set_x2(ln, time)
                        line.set_y2(ln, lvl)
                        didLowBreak = True

    hiCount = array.size(linesHi)
    if hiCount > 0:
        for i in pine_range(0, hiCount - 1):
            if not array.get(mitigHi, i):
                lvl: float = array.get(pricesHi, i)
                ln: Line = array.get(linesHi, i)
                line.set_color(ln, unmitHiCol)
                line.set_width(ln, unmitW)
                line.set_style(ln, unmitStyle)
                line.set_y2(ln, lvl)
                if extendRight:
                    line.set_extend(ln, extend.right)
                    line.set_x2(ln, time)
                else:
                    line.set_extend(ln, extend.none)
                    line.set_x2(ln, extX2)

    loCount = array.size(linesLo)
    if loCount > 0:
        for i in pine_range(0, loCount - 1):
            if not array.get(mitigLo, i):
                lvl: float = array.get(pricesLo, i)
                ln: Line = array.get(linesLo, i)
                line.set_color(ln, unmitLoCol)
                line.set_width(ln, unmitW)
                line.set_style(ln, unmitStyle)
                line.set_y2(ln, lvl)
                if extendRight:
                    line.set_extend(ln, extend.right)
                    line.set_x2(ln, time)
                else:
                    line.set_extend(ln, extend.none)
                    line.set_x2(ln, extX2)

    fillOpen = na
    fillHigh = na
    fillLow = na
    fillClose = na
    fillCol = na

    oppOpen = na
    oppHigh = na
    oppLow = na
    oppClose = na
    oppCol = na

    breakOutlineCol = na

    dbgDoLabel = False

    breakBar: bool = didHighBreak or didLowBreak

    if breakBar:
        isBullBreak: bool = didHighBreak
        breakOutlineCol = bullBase if isBullBreak else bearBase

        bodyTop: float = math.max(open, close)
        bodyBtm: float = math.min(open, close)
        bodyRng: float = bodyTop - bodyBtm
        if bodyRng <= 0:
            pad0: float = math.max(high - low, syminfo.mintick) * 0.35
            bodyTop = close + pad0
            bodyBtm = close - pad0
            bodyRng = bodyTop - bodyBtm

        if isBullBreak:
            cut: float = bodyBtm + bodyRng * bullPct

            fillOpen = bodyBtm
            fillClose = cut
            fillHigh = math.max(fillOpen, fillClose)
            fillLow = math.min(fillOpen, fillClose)
            fillCol = bullBase

            oppOpen = cut
            oppClose = bodyTop
            oppHigh = math.max(oppOpen, oppClose)
            oppLow = math.min(oppOpen, oppClose)
            oppCol = bearBase
        else:
            cut: float = bodyTop - bodyRng * bearPct

            fillOpen = cut
            fillClose = bodyTop
            fillHigh = math.max(fillOpen, fillClose)
            fillLow = math.min(fillOpen, fillClose)
            fillCol = bearBase

            oppOpen = bodyBtm
            oppClose = cut
            oppHigh = math.max(oppOpen, oppClose)
            oppLow = math.min(oppOpen, oppClose)
            oppCol = bullBase

        if dbgShow:
            dbgLblTxt = fFmt(bullVol) + ' (' + fPctStr(bullPct) + ') | ' + fFmt(bearVol) + ' (' + fPctStr(bearPct) + ')'
            pad: float = math.max(high - low, syminfo.mintick) * 0.25
            dbgLblY = high + pad if isBullBreak else low - pad
            dbgIsBull = isBullBreak
            dbgDoLabel = True

    if dbgDoLabel:
        label.new(x=bar_index, y=dbgLblY, text=dbgLblTxt, style=label.style_label_down if dbgIsBull else label.style_label_up, textcolor=bullBase if dbgIsBull else bearBase, color=color.new(color.black, 100), size=size.small, force_overlay=True)

    plotcandle(oppOpen, oppHigh, oppLow, oppClose, title='Breakout Delta Top/Bottom (Opp Segment)', color=oppCol, wickcolor=na, bordercolor=na)

    plotcandle(fillOpen, fillHigh, fillLow, fillClose, title='Breakout Delta Top/Bottom (Main Segment)', color=fillCol, wickcolor=na, bordercolor=na)

    plotcandle(open, high, low, close, title='Breakout Outline', color=na, wickcolor=breakOutlineCol, bordercolor=breakOutlineCol)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)