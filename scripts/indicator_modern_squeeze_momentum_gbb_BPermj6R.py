"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, bar_index, barmerge, barstate, bgcolor, close, color,
    display, high, input, label, location, low, math, na, nz, open, plot, plotshape, position,
    request, script, shape, size, string, syminfo, ta, table, text, timeframe
)
from pynecore.types import Color, Label, Persistent, Series, Table

grpG: str = "General"
grpA: str = "Adaptive length (Layer 1)"
grpB: str = "Bands"
grpC: str = "Compression (Layer 2)"
grpM: str = "Momentum (Layer 3)"
grpR: str = "Release (Layer 4)"
grpK: str = "Context (Layer 5)"
grpV: str = "Visual"


@script.indicator("Modern Squeeze Momentum [GBB]", "MSqueeze", overlay=False, precision=8, max_labels_count=1, max_bars_back=2000)
def main(
    classicMode=input.bool(False, "Classic mode (LazyBear; forces Layers 1-4 off)", group=grpG),
    inAdaptive=input.bool(True, "Adaptive length", group=grpA),
    lenMin=input.int(12, "Min length", minval=1, group=grpA),
    lenMax=input.int(40, "Max length", minval=1, group=grpA),
    fixedLen=input.int(20, "Fixed length (Layer 1 off / Classic)", minval=1, group=grpA),
    bbMult=input.float(2.0, "BB multiplier", minval=0.0, step=0.1, group=grpB),
    kcMult=input.float(1.5, "KC multiplier", minval=0.0, step=0.1, group=grpB),
    inPercentile=input.bool(True, "Percentile ranking", group=grpC),
    rankWindow=input.int(150, "Rank window", minval=1, group=grpC),
    lightPct=input.int(30, "Light pct", minval=0, maxval=100, group=grpC),
    mediumPct=input.int(15, "Medium pct", minval=0, maxval=100, group=grpC),
    tightPct=input.int(5, "Tight pct", minval=0, maxval=100, group=grpC),
    minSqzBars=input.int(3, "Min squeeze bars", minval=1, group=grpC),
    inNormalise=input.bool(True, "Normalised momentum (momentum / Keltner range)", group=grpM),
    momThr=input.float(0.5, "Momentum threshold", minval=0.0, step=0.1, group=grpM, tooltip="Keltner-range units while Layer 3 is on; price units when it is off."),
    inQualified=input.bool(True, "Qualified release filter", group=grpR),
    reqRangeBreak=input.bool(True, "Require range break", group=grpR),
    showRaw=input.bool(True, "Show unqualified releases", group=grpR),
    inHtf=input.bool(True, "HTF wash", group=grpK),
    htfSel=input.timeframe("", "HTF (blank = auto, 4x chart)", group=grpK),
    showTable=input.bool(True, "Stats table", group=grpK),
    statsH=input.int(10, "Stats horizon (bars)", minval=1, maxval=500, group=grpK),
    paletteSel=input.string("GBB", "Palette", options=("GBB", "LazyBear", "Mono"), group=grpV)
):
    useL1 = not classicMode and inAdaptive
    useL2 = not classicMode and inPercentile
    useL3 = not classicMode and inNormalise
    useL4 = not classicMode and inQualified

    def f_hilbert(x: Series[float], f: float):
        return (0.0962 * x + 0.5769 * nz(x[2]) - 0.5769 * nz(x[4]) - 0.0962 * nz(x[6])) * f

    def f_homodyne():
        src: Series[float] = (high + low) / 2
        period: Series[float] = 0.0
        prevP: float = nz(period[1])
        f: float = 0.075 * prevP + 0.54
        smooth: float = (4 * src + 3 * nz(src[1]) + 2 * nz(src[2]) + nz(src[3])) / 10
        det: Series[float] = f_hilbert(smooth, f)
        q1: float = f_hilbert(det, f)
        i1: float = nz(det[3])
        jI: float = f_hilbert(i1, f)
        jQ: float = f_hilbert(q1, f)
        i2: Series[float] = 0.0
        q2: Series[float] = 0.0
        i2 = 0.2 * (i1 - jQ) + 0.8 * nz(i2[1])
        q2 = 0.2 * (q1 + jI) + 0.8 * nz(q2[1])
        re: Series[float] = 0.0
        im: Series[float] = 0.0
        re = 0.2 * (i2 * nz(i2[1]) + q2 * nz(q2[1])) + 0.8 * nz(re[1])
        im = 0.2 * (i2 * nz(q2[1]) - q2 * nz(i2[1])) + 0.8 * nz(im[1])
        p: float = prevP
        if im != 0 and re != 0:
            p = 2 * math.pi / math.atan(im / re)
        if p > 1.5 * prevP:
            p = 1.5 * prevP
        if p < 0.67 * prevP:
            p = 0.67 * prevP
        if p < 6:
            p = 6
        if p > 50:
            p = 50
        period = 0.2 * p + 0.8 * prevP
        return period

    def f_length(period: float):
        periodS: Series[float] = na(float)
        periodS = period if na(periodS[1]) else 0.4 * period + 0.6 * periodS[1]
        cyc: float = math.min(math.max(periodS, lenMin), lenMax)
        lenAd: int = lenMin if na(periodS) else math.round(cyc)
        return (periodS, lenAd)

    def f_bands(n: int):
        src: float = close
        basis: float = ta.sma(src, n)
        dev: float = bbMult * ta.stdev(src, n)
        bbU: float = basis + dev
        bbL: float = basis - dev
        kcRange: float = ta.sma(ta.tr(True), n)
        kcU: float = basis + kcMult * kcRange
        kcL: float = basis - kcMult * kcRange
        sqzOnC: bool = bbL > kcL and bbU < kcU
        mid: float = ((ta.highest(high, n) + ta.lowest(low, n)) / 2 + ta.sma(close, n)) / 2
        momRaw: float = ta.linreg(src - mid, n, 0)
        return (basis, bbU, bbL, kcRange, kcU, kcL, sqzOnC, mid, momRaw)

    def f_compression(bbU: float, bbL: float, kcU: float, kcL: float, sqzOnC: bool):
        den: float = kcU - kcL
        ratio: float = na if den == 0 else (bbU - bbL) / den
        pctAll: float = ta.percentrank(ratio, rankWindow)
        pct: float = pctAll if useL2 else na
        gradePct: int = 0 if na(pct) else 3 if pct <= tightPct else 2 if pct <= mediumPct else 1 if pct <= lightPct else 0
        grade: int = gradePct if useL2 else 1 if sqzOnC else 0
        sqzOn: bool = grade >= 1
        sqzBars: Series[int] = 0
        sqzBars = nz(sqzBars[1]) + 1 if sqzOn else 0
        return (ratio, pct, grade, sqzOn, sqzBars)

    def f_momentum(momRaw: float, kcRange: float):
        momA: float = na if kcRange == 0 else momRaw / kcRange
        return momA if useL3 else momRaw

    def f_release(sqzOn: bool, sqzBars: Series[int], momentum: float):
        onI: Series[int] = 1 if sqzOn else 0
        fireRaw: bool = nz(onI[1]) == 1 and (not sqzOn)
        dir: int = 0 if na(momentum) else cast_int(math.sign(momentum))
        barDir: int = cast_int(math.sign(close - open))
        dur: int = nz(sqzBars[1])
        agree: bool = dir != 0 and dir == barDir
        strong: bool = not na(momentum) and math.abs(momentum) >= momThr
        longEnough: bool = dur >= minSqzBars

        durW: int = math.max(dur, 1)
        hiPrev: float = ta.highest(high[1], durW)
        loPrev: float = ta.lowest(low[1], durW)
        broke: bool = not reqRangeBreak or (dir > 0 and close > hiPrev) or (dir < 0 and close < loPrev)
        fireQ: bool = fireRaw and agree and strong and longEnough and broke if useL4 else fireRaw
        fireQDir: int = dir if fireQ else 0
        return (fireRaw, fireQ, fireQDir, dir)

    def f_state():
        periodRaw: float = f_homodyne()
        periodS, lenAd = f_length(periodRaw)
        length: int = lenAd if useL1 else fixedLen
        basis, bbU, bbL, kcRange, kcU, kcL, sqzOnC, mid, momRaw = f_bands(length)
        ratio, pct, grade, sqzOn, sqzBars = f_compression(bbU, bbL, kcU, kcL, sqzOnC)
        momentum: float = f_momentum(momRaw, kcRange)
        fireRaw, fireQ, fireQDir, dir = f_release(sqzOn, sqzBars, momentum)
        period: float = periodRaw if useL1 else na
        return (period, length, basis, bbU, bbL, kcRange, kcU, kcL, mid, momRaw, ratio, pct, grade, sqzBars, momentum, fireRaw, fireQ, fireQDir, sqzOn, periodS, dir)

    momentum: Series
    fireQDir: Series
    period, length, basis, bbU, bbL, kcRange, kcU, kcL, mid, momRaw, ratio, pct, grade, sqzBars, momentum, fireRaw, fireQ, fireQDir, sqzOn, periodS, dir = f_state()

    onI: Series[int] = 1 if sqzOn else 0
    prevOn: bool = nz(onI[1]) == 1
    sqzStart: bool = sqzOn and (not prevOn)

    cPosUp: Color = color.lime if paletteSel == 'LazyBear' else color.new('#E0E0E0') if paletteSel == 'Mono' else color.new('#26C6DA')
    cPosDn: Color = color.green if paletteSel == 'LazyBear' else color.new('#9E9E9E') if paletteSel == 'Mono' else color.new('#00838F')
    cNegDn: Color = color.red if paletteSel == 'LazyBear' else color.new('#616161') if paletteSel == 'Mono' else color.new('#FF5252')
    cNegUp: Color = color.maroon if paletteSel == 'LazyBear' else color.new('#424242') if paletteSel == 'Mono' else color.new('#B71C1C')
    cDot0: Color = color.blue if paletteSel == 'LazyBear' else color.new('#757575') if paletteSel == 'Mono' else color.new('#546E7A')
    cDot1: Color = color.black if paletteSel == 'LazyBear' else color.new('#BDBDBD') if paletteSel == 'Mono' else color.new('#FFD54F')
    cDot2: Color = color.black if paletteSel == 'LazyBear' else color.new('#E0E0E0') if paletteSel == 'Mono' else color.new('#FF9800')
    cDot3: Color = color.black if paletteSel == 'LazyBear' else color.new('#FFFFFF') if paletteSel == 'Mono' else color.new('#F44336')
    cLong: Color = color.new('#FFFFFF') if paletteSel == 'Mono' else color.new('#00E676')
    cShort: Color = color.new('#BDBDBD') if paletteSel == 'Mono' else color.new('#FF1744')
    cRaw: Color = color.new(color.new('#9E9E9E'), 40)
    cWash: Color = color.new('#9E9E9E') if paletteSel == 'Mono' else color.new('#FFB300')

    momUp: bool = momentum > nz(momentum[1])
    histCol: Color = na if na(momentum) else (cPosUp if momUp else cPosDn) if momentum > 0 else cNegUp if momUp else cNegDn
    plot(momentum, 'Momentum', color=histCol, style=plot.style_columns)

    plot(0, 'Squeeze none', color=cDot0 if grade == 0 else na, linewidth=1, style=plot.style_circles, display=display.pane)
    plot(0, 'Squeeze light', color=cDot1 if grade == 1 else na, linewidth=2, style=plot.style_circles, display=display.pane)
    plot(0, 'Squeeze medium', color=cDot2 if grade == 2 else na, linewidth=3, style=plot.style_circles, display=display.pane)
    plot(0, 'Squeeze tight', color=cDot3 if grade == 3 else na, linewidth=4, style=plot.style_circles, display=display.pane)

    plotshape(fireQ and fireQDir > 0, 'Qualified release long', style=shape.triangleup, location=location.bottom, color=cLong, size=size.small)
    plotshape(fireQ and fireQDir < 0, 'Qualified release short', style=shape.triangledown, location=location.top, color=cShort, size=size.small)
    plotshape(showRaw and fireRaw and (not fireQ), 'Unqualified release', style=shape.circle, location=location.bottom, color=cRaw, size=size.tiny)

    plot(0.5 if useL3 else na, 'Ref +0.5', color=color.new(color.gray, 60), style=plot.style_linebr, display=display.pane)
    plot(-0.5 if useL3 else na, 'Ref -0.5', color=color.new(color.gray, 60), style=plot.style_linebr, display=display.pane)
    plot(1.0 if useL3 else na, 'Ref +1.0', color=color.new(color.gray, 75), style=plot.style_linebr, display=display.pane)
    plot(-1.0 if useL3 else na, 'Ref -1.0', color=color.new(color.gray, 75), style=plot.style_linebr, display=display.pane)

    plot(grade, 'Grade', display=display.none)
    plot(fireQDir, 'Release direction', display=display.none)

    def f_htf():
        hGrade: Series
        hPeriod, hLength, hBasis, hBbU, hBbL, hKcRange, hKcU, hKcL, hMid, hMomRaw, hRatio, hPct, hGrade, hSqzBars, hMomentum, hFireRaw, hFireQ, hFireQDir, hSqzOn, hPeriodS, hDir = f_state()
        hOnI: Series[int] = 1 if hSqzOn else 0
        return (nz(hOnI[1]), nz(hGrade[1]))

    htfTf: str = timeframe.from_seconds(4 * timeframe.in_seconds()) if htfSel == '' else htfSel
    htfActive: bool = inHtf and timeframe.in_seconds(htfTf) > timeframe.in_seconds()
    htfOnI: Series
    htfOnI, htfGrade = request.security(syminfo.tickerid, htfTf, f_htf(), lookahead=barmerge.lookahead_off)
    htfOn: bool = htfActive and htfOnI == 1
    htfWash: Color = color.new(cWash, 75 if htfGrade >= 3 else 82 if htfGrade == 2 else 90) if htfOn else na
    bgcolor(htfWash, title='HTF wash')

    htfNote: Persistent[Label] = na(Label)
    if inHtf and (not htfActive) and barstate.islast:
        if na(htfNote):
            htfNote = label.new(bar_index, 0, 'HTF wash off: HTF ' + htfTf + ' is not above the chart timeframe', style=label.style_label_left, color=color.new(color.gray, 70), textcolor=color.white, size=size.small)
        else:
            label.set_x(htfNote, bar_index)

    nSqz: Persistent[int] = 0
    nRaw: Persistent[int] = 0
    nQ: Persistent[int] = 0
    nScored: Persistent[int] = 0
    nHit: Persistent[int] = 0
    sumFwdAll: Persistent[float] = 0.0
    nFwdAll: Persistent[int] = 0
    sumFwdEv: Persistent[float] = 0.0
    nFwdEv: Persistent[int] = 0
    qI: Series[int] = 1 if fireQ else 0
    atr14: Series[float] = ta.atr(14)
    atrH: float = atr14[statsH]
    hiH: float = ta.highest(high, statsH)
    loH: float = ta.lowest(low, statsH)
    fwdRange: float = na if na(atrH) or atrH == 0 else (hiH - loH) / atrH
    if barstate.isconfirmed:
        if sqzStart:
            nSqz += 1
        if fireRaw:
            nRaw += 1
        if fireQ:
            nQ += 1
        if bar_index >= statsH:
            evH: bool = nz(qI[statsH]) == 1
            dirH: int = nz(fireQDir[statsH])
            if evH:
                nScored += 1
                if math.sign(close - close[statsH]) == dirH:
                    nHit += 1
            if not na(fwdRange):
                sumFwdAll += fwdRange
                nFwdAll += 1
                if evH:
                    sumFwdEv += fwdRange
                    nFwdEv += 1

    stats: Persistent[Table] = na(Table)
    footerMerged: Persistent[bool] = False
    if showTable and barstate.islast:
        if na(stats):
            stats = table.new(position.top_right, 2, 6, bgcolor=color.new(color.black, 70), border_width=1, border_color=color.new(color.gray, 60))
        hitRate: float = 100.0 * nHit / nScored if nScored > 0 else na
        rangeMult: float = sumFwdEv / nFwdEv / (sumFwdAll / nFwdAll) if nFwdEv > 0 and nFwdAll > 0 and (sumFwdAll > 0) else na
        hStr: str = string.tostring(statsH)
        table.cell(stats, 0, 0, 'Squeezes', text_color=color.white, text_size=size.small, text_halign=text.align_left)
        table.cell(stats, 1, 0, string.tostring(nSqz), text_color=color.white, text_size=size.small)
        table.cell(stats, 0, 1, 'Releases raw / qualified', text_color=color.white, text_size=size.small, text_halign=text.align_left)
        table.cell(stats, 1, 1, string.tostring(nRaw) + ' / ' + string.tostring(nQ), text_color=color.white, text_size=size.small)
        table.cell(stats, 0, 2, 'Hit rate @' + hStr, text_color=color.white, text_size=size.small, text_halign=text.align_left)
        table.cell(stats, 1, 2, '-' if na(hitRate) else string.tostring(hitRate, '0.0') + '% (' + string.tostring(nScored) + ')', text_color=color.white, text_size=size.small)
        table.cell(stats, 0, 3, 'Range multiple @' + hStr, text_color=color.white, text_size=size.small, text_halign=text.align_left)
        table.cell(stats, 1, 3, '-' if na(rangeMult) else string.tostring(rangeMult, '0.00') + 'x', text_color=color.white, text_size=size.small)
        table.cell(stats, 0, 4, 'HTF ' + htfTf, text_color=color.white, text_size=size.small, text_halign=text.align_left)
        table.cell(stats, 1, 4, 'off' if not htfActive else 'squeeze ' + string.tostring(htfGrade) if htfOn else 'no squeeze', text_color=color.white, text_size=size.small)
        table.cell(stats, 0, 5, 'Running counts on loaded bars, not a backtest. Reset on settings change and reload. No costs.', text_color=color.new(color.white, 30), text_size=size.tiny, text_halign=text.align_left)
        if not footerMerged:
            footerMerged = True
            table.merge_cells(stats, 0, 5, 1, 5)

    alSqzStart: bool = barstate.isconfirmed and sqzStart
    alRaw: bool = barstate.isconfirmed and fireRaw
    alQLong: bool = barstate.isconfirmed and fireQ and (fireQDir > 0)
    alQShort: bool = barstate.isconfirmed and fireQ and (fireQDir < 0)
    alHtf: bool = barstate.isconfirmed and htfActive and (htfOnI != nz(htfOnI[1]))
    alertcondition(alSqzStart, 'Squeeze started', 'MSqueeze {{ticker}} {{interval}}: squeeze started, grade {{plot("Grade")}}')
    alertcondition(alRaw, 'Squeeze released (raw)', 'MSqueeze {{ticker}} {{interval}}: squeeze released (raw)')
    alertcondition(alQLong, 'Qualified release - long', 'MSqueeze {{ticker}} {{interval}}: qualified release LONG')
    alertcondition(alQShort, 'Qualified release - short', 'MSqueeze {{ticker}} {{interval}}: qualified release SHORT')
    alertcondition(alHtf, 'HTF squeeze started / released', 'MSqueeze {{ticker}} {{interval}}: HTF squeeze state changed')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
