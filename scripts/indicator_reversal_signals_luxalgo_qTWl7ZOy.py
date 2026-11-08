"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, bar_index, close, color, display, format, high, input, label,
    location, low, math, na, open, plot, plotshape, script, shape, size, string, syminfo, ta, text,
    xloc, yloc
)
from pynecore.types import Color, Persistent, PersistentSeries, Series


@udt
class bar:
    o: float = _dataclass_field(default_factory=lambda: open)
    h: float = _dataclass_field(default_factory=lambda: high)
    l: float = _dataclass_field(default_factory=lambda: low)
    c: float = _dataclass_field(default_factory=lambda: close)
    i: int = _dataclass_field(default_factory=lambda: bar_index)


@udt
class trb:
    bSC: int = na(int)
    bSH: float = na(float)
    bSL: float = na(float)
    sSC: int = na(int)
    sSH: float = na(float)
    sSL: float = na(float)


@udt
class tre:
    bCC: int = na(int)
    bC8: float = na(float)
    bCHt: float = na(float)
    bCH: float = na(float)
    bCL: float = na(float)
    bCLt: float = na(float)
    bCD: float = na(float)
    sCC: int = na(int)
    sC8: float = na(float)
    sCHt: float = na(float)
    sCH: float = na(float)
    sCL: float = na(float)
    sCLt: float = na(float)
    sCT: float = na(float)


bGR: str = 'Momentum Phase'
bTP = "Momentum phase provides an indication of the initial trend's momentum and identifies a point of a likely top or bottom in the ranging markets\n\n" + 'Completed - dislays only completed momentum phases\n' + 'Detailed - displays all counting process of the momentum phases\nNone - disables the display of the momentum phases'
eGR: str = 'Trend Exhaustion Phase'
eTP = 'Trend exhaustion phase aims to identify when the trend is fading/exhausting and possibly starting to reverse. The trend exhaustion phase starts only if a momentum phase is already established\n\n' + 'Completed - dislays only completed trend exhaustion phases\n' + 'Detailed - displays all counting process of the trend exhaustion phases\nNone - disables the display of the trend exhaustion phases'
tGR: str = 'Trade Setups'
tTP = 'All phase specific trade setups, presented as options, are triggered once the selected phase is completed and folowed by a price flip in the direction of the trade setup. Please pay attention to the phase specific risk levels as well as the overall trend direction\n' + '⚠️ Trading is subject to high risk, look first then leap\n\n' + 'Tips : \n' + ' - Momentum trade setups are not recommended setups, and in case applied they best fit in ranging market\n' + '    a trade signal, followed immediately by a warning indication can be assumed as continuation of the underlying trend and can be traded in the opposite direction of the suggested signal\n\n' + ' -  Exhaustion / Qualified trade setups best fits in trending market\n' + '    Exhaustion, suggested type of trade setup, buy (sell) when buy (sell) trend exhaustion phase is complete\n' + '    Qualified, trend exhaustion phase followed by momentum phase is assumed as qualified trade setup'


@script.indicator('Reversal Signals [LuxAlgo]', 'LuxAlgo - Reversal Signals', True, max_labels_count=500, max_bars_back=5000, na_bool=True)
def main(
    bSh=input.string('Completed', 'Display Phases', options=('Completed', 'Detailed', 'None'), group=bGR, tooltip=bTP),
    srL=input.bool(True, 'Support & Resistance Levels', inline='bSh', group=bGR),
    ptLT=input.string('Step Line w/ Diamonds', '', options=('Circles', 'Step Line', 'Step Line w/ Diamonds'), inline='bSh', group=bGR),
    rsB=input.bool(False, 'Momentum Phase Risk Levels', inline='bSh2', group=bGR),
    ptSR=input.string('Circles', '', options=('Circles', 'Step Line'), inline='bSh2', group=bGR),
    eSh=input.string('Completed', 'Display Phases', options=('Completed', 'Detailed', 'None'), group=eGR, tooltip=eTP),
    rsE=input.bool(False, 'Trend Exhaustion Phase Risk Levels', group=eGR),
    ttE=input.bool(False, 'Trend Exhaustion Phase Target Levels', group=eGR),
    tso=input.string('None', 'Phase Specific Trade Setup Options', options=('Momentum', 'Exhaustion', 'Qualified', 'None'), group=tGR, tooltip=tTP),
    war=input.bool(False, 'Price Flips against the Phase Specific Trade Setups', group=tGR)
):
    BnoShw: Persistent[bool] = False
    Bcmpltd = bSh == 'Completed'
    BnoShw = False if bSh == 'None' else True
    noShw: Persistent[bool] = False
    cmpltd = eSh == 'Completed'
    noShw = False if eSh == 'None' else True
    b: bar = bar()
    S: Persistent[trb] = trb()
    C: Persistent[tre] = tre()
    noC: Color = color.new('#00000000')
    rdC: Color = color.new('#F23645')
    gnC: Color = color.new('#089981')
    whC: Color = color.new('#FFFFFF')
    blC: Color = color.new('#2962FF')
    grC: Color = color.new('#787B86')
    bgC: Color = color.new('#00BCD4')
    shpD = shape.labeldown
    shpU = shape.labelup
    locA = location.abovebar
    locB = location.belowbar
    dspN: bool = False
    pltL = plot.style_circles
    pltS = size.tiny
    def f_xLX(_p: Series, _l):
        return _l > _p and _l < _p[1] or (_l < _p and _l > _p[1])

    def f_lnS(_s):
        __block_result__ = na
        __switch__ = _s
        if __switch__ == 'Circles':
            __block_result__ = plot.style_circles
        elif __switch__ == 'Step Line':
            __block_result__ = plot.style_steplinebr
        elif __switch__ == 'Step Line w/ Diamonds':
            __block_result__ = plot.style_steplinebr
        s = __block_result__
        return s

    ptLB = f_lnS(ptLT)
    ptRS = f_lnS(ptSR)
    field_0: Series[float] = b.c
    con = b.c < field_0[4]
    if con:
        S.bSC = 1 if S.bSC == 9 else S.bSC + 1
        S.sSC = 0
    else:
        S.sSC = 1 if S.sSC == 9 else S.sSC + 1
        S.bSC = 0
    field_1: Series[float] = b.l
    field_2: Series[float] = b.l
    field_3: Series[float] = b.l
    field_4: Series[float] = b.l
    field_5: Series[float] = b.l
    field_6: Series[float] = b.l
    pbS: Series = b.l <= field_1[3] and b.l <= field_2[2] or (field_3[1] <= field_4[3] and field_5[1] <= field_6[2])
    plotshape(BnoShw and (not Bcmpltd) and (S.bSC == 1), '', shpD, locA, noC, 0, '₁', gnC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.bSC == 2), '', shpD, locA, noC, 0, '₂', gnC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.bSC == 3), '', shpD, locA, noC, 0, '₃', gnC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.bSC == 4), '', shpD, locA, noC, 0, '₄', gnC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.bSC == 5), '', shpD, locA, noC, 0, '₅', gnC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.bSC == 6), '', shpD, locA, noC, 0, '₆', gnC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.bSC == 7), '', shpD, locA, noC, 0, '₇', gnC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.bSC == 8) and (not pbS), '', shpD, locA, noC, 0, '₈', gnC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.bSC == 8) and pbS, '', shpD, locA, color.new(gnC, 75), 0, 'ᵖ\n₈', whC, dspN)
    plotshape(BnoShw and S.bSC == 9 and (not pbS), 'Bullish Momentum Phases', shpU, locB, color.new(gnC, 25), 0, '', whC, not dspN, pltS)
    plotshape(BnoShw and S.bSC == 9 and pbS, 'Perfect Bullish Momentum Phases', shpU, locB, color.new(gnC, 25), 0, 'ᵖ', whC, not dspN, pltS)
    field_7: Series[int] = S.bSC
    plotshape(BnoShw and field_7[1] == 8 and (S.sSC == 1), 'Early Bullish Momentum Phases', shpU, locB, color.new(gnC, 25), 0, '', whC, not dspN, pltS)
    field_8: Series[int] = S.bSC
    bC8 = field_8[1] == 8 and S.sSC == 1
    sR = ta.highest(9)
    bSR: Series[float] = 0.0
    bSR = sR if S.bSC == 9 or bC8 else 0 if b.c > bSR[1] else bSR[1]
    plot(bSR if srL and bSR > 0 else na, 'Resistance Levels', color.new(rdC, 50), 2, ptLB)
    plotshape(bSR if srL and bSR > 0 and (bSR != bSR[1]) and string.contains(ptLT, 'Diamonds') else na, '', shape.diamond, location.absolute, rdC, editable=dspN, size=size.tiny)
    if S.bSC == 1:
        S.bSL = b.l
    if S.bSC > 0:
        S.bSL = math.min(b.l, S.bSL)
        if b.l == S.bSL:
            S.bSH = b.h
    bSD: Series[float] = 0.0
    bSD = 2 * S.bSL - S.bSH if S.bSC == 9 else 0 if b.c < bSD[1] or S.sSC == 9 else bSD[1]
    plot(bSD if rsB and bSD > 0 else na, 'Bullish Momentum Risk Levels', blC, 1, ptRS)
    field_9: Series[float] = b.h
    field_10: Series[float] = b.h
    field_11: Series[float] = b.h
    field_12: Series[float] = b.h
    field_13: Series[float] = b.h
    field_14: Series[float] = b.h
    psS: Series = b.h >= field_9[3] and b.h >= field_10[2] or (field_11[1] >= field_12[3] and field_13[1] >= field_14[2])
    plotshape(BnoShw and (not Bcmpltd) and (S.sSC == 1), '', shpD, locA, noC, 0, '₁', rdC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.sSC == 2), '', shpD, locA, noC, 0, '₂', rdC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.sSC == 3), '', shpD, locA, noC, 0, '₃', rdC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.sSC == 4), '', shpD, locA, noC, 0, '₄', rdC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.sSC == 5), '', shpD, locA, noC, 0, '₅', rdC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.sSC == 6), '', shpD, locA, noC, 0, '₆', rdC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.sSC == 7), '', shpD, locA, noC, 0, '₇', rdC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.sSC == 8) and (not psS), '', shpD, locA, noC, 0, '₈', rdC, dspN)
    plotshape(BnoShw and (not Bcmpltd) and (S.sSC == 8) and psS, '', shpD, locA, color.new(rdC, 75), 0, 'ᵖ\n₈', whC, dspN)
    plotshape(BnoShw and S.sSC == 9 and (not psS), 'Completed Bearish Momentum Phases', shpD, locA, color.new(rdC, 25), 0, '', whC, not dspN, pltS)
    plotshape(BnoShw and S.sSC == 9 and psS, 'Perfect Bearish Momentum Phases', shpD, locA, color.new(rdC, 25), 0, 'ᵖ', whC, not dspN, pltS)
    field_15: Series[int] = S.sSC
    plotshape(BnoShw and field_15[1] == 8 and (S.bSC == 1), 'Early Bearish Momentum Phases', shpD, locA, color.new(rdC, 25), 0, '', whC, not dspN, pltS)
    field_16: Series[int] = S.sSC
    sC8 = field_16[1] == 8 and S.bSC == 1
    sS = ta.lowest(9)
    sSS: Series[float] = 0.0
    sSS = sS if S.sSC == 9 or sC8 else 0 if b.c < sSS[1] else sSS[1]
    plot(sSS if srL and sSS > 0 else na, 'Support Levels', color.new(gnC, 50), 2, ptLB)
    plotshape(sSS if srL and sSS > 0 and (sSS != sSS[1]) and string.contains(ptLT, 'Diamonds') else na, '', shape.diamond, location.absolute, gnC, editable=dspN, size=size.tiny)
    if S.sSC == 1:
        S.sSH = b.h
    if S.sSC > 0:
        S.sSH = math.max(b.h, S.sSH)
        if b.h == S.sSH:
            S.sSL = b.l
    sSD: Series[float] = 0.0
    sSD = 2 * S.sSH - S.sSL if S.sSC == 9 else 0 if b.c > sSD[1] or S.bSC == 9 else sSD[1]
    plot(sSD if rsB and sSD > 0 else na, 'Bearish Momentum Risk Levels', blC, 1, ptRS)
    field_17: Series[float] = b.l
    bCC = b.c <= field_17[2]
    field_18: Series[float] = b.l
    b13 = b.c <= field_18[2] and b.l >= C.bC8
    sbC: PersistentSeries[bool] = False
    __block_result_1__ = na
    if S.bSC == 9 and C.bCC == 0 and (pbS or pbS[1]):
        __block_result_1__ = True
    else:
        __block_result_2__ = na
        if S.sSC == 9 or C.bCC == 13 or b.c > bSR:
            __block_result_2__ = False
        else:
            __block_result_2__ = sbC[1]
        __block_result_1__ = __block_result_2__
    sbC = __block_result_1__
    C.bCC = ((1 if bCC else 0) if S.bSC == 9 else C.bCC + 1 if bCC else C.bCC) if sbC else 0
    C.bCC = C.bCC - 1 if C.bCC == 13 and b13 else C.bCC
    field_19: Series[int] = C.bCC
    if C.bCC == 8 and C.bCC != field_19[1]:
        C.bC8 = b.c
    field_20: Series[int] = C.bCC
    shwBC = noShw and (not cmpltd) and sbC and (C.bCC != field_20[1])
    plotshape(shwBC and C.bCC == 1, '', shpD, locB, noC, 0, '₁', gnC, dspN)
    plotshape(shwBC and C.bCC == 2, '', shpD, locB, noC, 0, '₂', gnC, dspN)
    plotshape(shwBC and C.bCC == 3, '', shpD, locB, noC, 0, '₃', gnC, dspN)
    plotshape(shwBC and C.bCC == 4, '', shpD, locB, noC, 0, '₄', gnC, dspN)
    plotshape(shwBC and C.bCC == 5, '', shpD, locB, noC, 0, '₅', gnC, dspN)
    plotshape(shwBC and C.bCC == 6, '', shpD, locB, noC, 0, '₆', gnC, dspN)
    plotshape(shwBC and C.bCC == 7, '', shpD, locB, noC, 0, '₇', gnC, dspN)
    plotshape(shwBC and C.bCC == 8, '', shpD, locB, noC, 0, '₈', gnC, dspN)
    plotshape(shwBC and C.bCC == 9, '', shpD, locB, noC, 0, '₉', gnC, dspN)
    plotshape(shwBC and C.bCC == 10, '', shpD, locB, noC, 0, '₁₀', gnC, dspN)
    plotshape(shwBC and C.bCC == 11, '', shpD, locB, noC, 0, '₁₁', gnC, dspN)
    plotshape(shwBC and C.bCC == 12, '', shpD, locB, noC, 0, '₁₂', gnC, dspN)
    field_21: Series[int] = C.bCC
    plotshape(noShw and (not cmpltd) and sbC and (C.bCC == field_21[1]) and (C.bCC == 12) and b13, '', shpD, locB, noC, 0, '₊', gnC, dspN)
    field_22: Series[int] = C.bCC
    plotshape(noShw and sbC and (C.bCC != field_22[1]) and (C.bCC == 13), 'Completed Bullish Exhaustions', shpU, locB, color.new(color.new('#006400'), 25), 0, 'E', whC, not dspN, pltS)
    if C.bCC == 1:
        C.bCLt = b.l
        C.bCHt = b.h
    if sbC:
        C.bCHt = math.max(b.h, C.bCHt)
        C.bCLt = math.min(b.l, C.bCLt)
        if b.h == C.bCHt:
            C.bCL = b.l
        if b.l == C.bCLt:
            C.bCH = b.h
    bCT: Series = 2 * C.bCHt - C.bCL
    bCT = bCT if C.bCC == 13 else 0.0 if b.c > bCT[1] or (C.bCD == 0 and C.sCC == 13) else bCT[1]
    plot(bCT if ttE and bCT > 0 else na, 'Bullish Exhaustion Target Levels', grC, 1, pltL)
    bCD: Series = 2 * C.bCLt - C.bCH
    bCD = bCD if C.bCC == 13 else 0.0 if b.c < bCD[1] or (bCT == 0 and C.sCC == 13) else bCD[1]
    C.bCD = bCD
    plot(bCD if rsE and bCD > 0 else na, 'Bullish Exhaustion Risk Levels', bgC, 1, pltL)
    field_23: Series[float] = b.h
    sCC = b.c >= field_23[2]
    field_24: Series[float] = b.h
    s13 = b.c >= field_24[2] and b.h <= C.sC8
    ssC: PersistentSeries[bool] = False
    __block_result_3__ = na
    if S.sSC == 9 and C.sCC == 0 and (psS or psS[1]):
        __block_result_3__ = True
    else:
        __block_result_4__ = na
        if S.bSC == 9 or C.sCC == 13 or b.c < sSS:
            __block_result_4__ = False
        else:
            __block_result_4__ = ssC[1]
        __block_result_3__ = __block_result_4__
    ssC = __block_result_3__
    C.sCC = ((1 if sCC else 0) if S.sSC == 9 else C.sCC + 1 if sCC else C.sCC) if ssC else 0
    C.sCC = C.sCC - 1 if C.sCC == 13 and s13 else C.sCC
    field_25: Series[int] = C.sCC
    if C.sCC == 8 and C.sCC != field_25[1]:
        C.sC8 = b.c
    field_26: Series[int] = C.sCC
    shwSC = noShw and (not cmpltd) and ssC and (C.sCC != field_26[1])
    plotshape(shwSC and C.sCC == 1, '', shpD, locB, noC, 0, '₁', rdC, dspN)
    plotshape(shwSC and C.sCC == 2, '', shpD, locB, noC, 0, '₂', rdC, dspN)
    plotshape(shwSC and C.sCC == 3, '', shpD, locB, noC, 0, '₃', rdC, dspN)
    plotshape(shwSC and C.sCC == 4, '', shpD, locB, noC, 0, '₄', rdC, dspN)
    plotshape(shwSC and C.sCC == 5, '', shpD, locB, noC, 0, '₅', rdC, dspN)
    plotshape(shwSC and C.sCC == 6, '', shpD, locB, noC, 0, '₆', rdC, dspN)
    plotshape(shwSC and C.sCC == 7, '', shpD, locB, noC, 0, '₇', rdC, dspN)
    plotshape(shwSC and C.sCC == 8, '', shpD, locB, noC, 0, '₈', rdC, dspN)
    plotshape(shwSC and C.sCC == 9, '', shpD, locB, noC, 0, '₉', rdC, dspN)
    plotshape(shwSC and C.sCC == 10, '', shpD, locB, noC, 0, '₁₀', rdC, dspN)
    plotshape(shwSC and C.sCC == 11, '', shpD, locB, noC, 0, '₁₁', rdC, dspN)
    plotshape(shwSC and C.sCC == 12, '', shpD, locB, noC, 0, '₁₂', rdC, dspN)
    field_27: Series[int] = C.sCC
    plotshape(noShw and (not cmpltd) and ssC and (C.sCC == field_27[1]) and (C.sCC == 12) and s13, '', shpD, locB, noC, 0, '₊', rdC, dspN)
    field_28: Series[int] = C.sCC
    plotshape(noShw and ssC and (C.sCC != field_28[1]) and (C.sCC == 13), 'Completed Bearish Exhaustions', shpD, locA, color.new(color.new('#910000'), 25), 0, 'E', whC, not dspN, pltS)
    if C.sCC == 1:
        C.sCLt = b.l
        C.sCHt = b.h
    if ssC:
        C.sCHt = math.max(b.h, C.sCHt)
        C.sCLt = math.min(b.l, C.sCLt)
        if b.h == C.sCHt:
            C.sCL = b.l
        if b.l == C.sCLt:
            C.sCH = b.h
    sCD: Series = 2 * C.sCHt - C.sCL
    sCD = 2 * C.sCHt - C.sCL if C.sCC == 13 else 0.0 if b.c > sCD[1] or (C.sCT == 0 and C.bCC == 13) else sCD[1]
    plot(sCD if rsE and sCD > 0 else na, 'Bearish Exhaustion Risk Levels', bgC, 1, pltL)
    sCT: Series = 2 * C.sCLt - C.sCH
    sCT = sCT if C.sCC == 13 else 0.0 if b.c < sCT[1] or (sCD == 0 and C.bCC == 13) else sCT[1]
    C.sCT = sCT
    plot(sCT if ttE and sCT > 0 else na, 'Bearish Exhaustion Target Levels', grC, 1, pltL)
    plotshape(bSR if bSR > 0 and bSR[1] == 0 else na, 'Overall Bearish Trend Mark', shpD, location.absolute, noC, 0, '⇩', rdC, not dspN, size=size.small, display=display.none)
    plotshape(sSS if sSS > 0 and sSS[1] == 0 else na, 'Overall Bullish Trend Mark', shpU, location.absolute, noC, 0, '⇧', gnC, not dspN, size=size.small, display=display.none)
    sbPF: PersistentSeries[bool] = False
    bPFc: Persistent[bool] = False
    ssPF: PersistentSeries[bool] = False
    sPFc: Persistent[bool] = False
    lTrd: Persistent[bool] = False
    sTrd: Persistent[bool] = False
    bBl9 = ta.valuewhen(S.bSC == 9, b.i, 0)
    bBp9 = ta.valuewhen(S.bSC == 9, b.i, 1)
    bB13 = ta.valuewhen(C.bCC == 13, b.i, 0)
    sBl9 = ta.valuewhen(S.sSC == 9, b.i, 0)
    sBp9 = ta.valuewhen(S.sSC == 9, b.i, 1)
    sB13 = ta.valuewhen(C.sCC == 13, b.i, 0)
    trdS = tso != 'None'
    sQC = sBl9 > sB13 and sB13 > sBp9 and (sBp9 > bBl9)
    field_29: Series[int] = C.sCC
    sPFO = S.sSC == 9 or sC8 if tso == 'Momentum' else field_29[5] == 13 if tso == 'Exhaustion' else S.sSC == 9 and sQC
    __block_result_5__ = na
    if sPFO:
        __block_result_5__ = True
    else:
        __block_result_6__ = na
        if sPFc:
            __block_result_6__ = False
        else:
            __block_result_6__ = ssPF[1]
        __block_result_5__ = __block_result_6__
    ssPF = __block_result_5__
    field_30: Series[float] = b.c
    field_31: Series[float] = b.c
    field_32: Series[float] = b.c
    sPFc = ssPF and b.c < field_30[4] and (field_31[1] > field_32[5])
    __block_result_7__ = (na, na)
    if tso == 'Exhaustion':
        __block_result_8__ = (na, na)
        if sCD == 0:
            __block_result_8__ = (' - Risky', string.tostring(b.h, format.mintick))
        else:
            __block_result_8__ = ('', string.tostring(sCD, format.mintick))
        __block_result_7__ = __block_result_8__
    else:
        __block_result_9__ = (na, na)
        if sSD == 0:
            __block_result_9__ = (' - Risky', string.tostring(b.h, format.mintick))
        else:
            __block_result_9__ = ('', string.tostring(sSD, format.mintick))
        __block_result_7__ = __block_result_9__
    sTR, sST = __block_result_7__
    sTT = 'Short Trade Setup' + sTR + '\n Signal : Completed ' + tso + ' plus Bearish Price Flip\n' + ' Stop    : ' + sST + '\n Target : ' + string.tostring(sCT if tso == 'Exhaustion' else sSS, format.mintick)
    if sPFc and trdS:
        label.new(bar_index, b.h, 'S', xloc.bar_index, yloc.price, color.new(color.yellow, 25), label.style_label_down, color.white, size.small, text.align_center, sTT + '\n\nnot a finacial advice, subject to high risk')
        alert(syminfo.ticker + ' : ' + sTT + '\n Price    : ' + string.tostring(close, format.mintick) + '\n\nnot a finacial advice, subject to high risk')
        sTrd = True
        lTrd = False
    if war and sTrd and (b.o < b.c) and (S.sSC == 2) and (not lTrd):
        label.new(bar_index, b.l, '⚠️', xloc.bar_index, yloc.price, color.new(color.yellow, 100), label.style_label_up, color.yellow, size.large, text.align_center, 'Warning\nbullish price flip detected')
        sTrd = False
    if war and sTrd and (b.o < b.c) and (sSD[1] != 0 and b.c > sSD[1] or (sCD[1] != 0 and b.c > sCD[1])):
        label.new(bar_index, b.l, '⚠️', xloc.bar_index, yloc.price, color.new(color.yellow, 100), label.style_label_up, color.yellow, size.large, text.align_center, 'Critical Warning\nstop/risk level breached')
        sTrd = False
    bQC = bBl9 > bB13 and bB13 > bBp9 and (bBp9 > sBl9)
    field_33: Series[int] = C.bCC
    bPFO = S.bSC == 9 or bC8 if tso == 'Momentum' else field_33[5] == 13 if tso == 'Exhaustion' else S.bSC == 9 and bQC
    __block_result_10__ = na
    if bPFO:
        __block_result_10__ = True
    else:
        __block_result_11__ = na
        if bPFc:
            __block_result_11__ = False
        else:
            __block_result_11__ = sbPF[1]
        __block_result_10__ = __block_result_11__
    sbPF = __block_result_10__
    field_34: Series[float] = b.c
    field_35: Series[float] = b.c
    field_36: Series[float] = b.c
    bPFc = sbPF and b.c > field_34[4] and (field_35[1] < field_36[5])
    __block_result_12__ = (na, na)
    if tso == 'Exhaustion':
        __block_result_13__ = (na, na)
        if bCD == 0:
            __block_result_13__ = (' - Risky', string.tostring(b.l, format.mintick))
        else:
            __block_result_13__ = ('', string.tostring(bCD, format.mintick))
        __block_result_12__ = __block_result_13__
    else:
        __block_result_14__ = (na, na)
        if bSD == 0:
            __block_result_14__ = (' - Risky', string.tostring(b.l, format.mintick))
        else:
            __block_result_14__ = ('', string.tostring(bSD, format.mintick))
        __block_result_12__ = __block_result_14__
    bTR, bST = __block_result_12__
    lTT = 'Long Trade Setup' + bTR + '\n Signal : Completed ' + tso + ' plus Bullish Price Flip\n' + ' Stop    : ' + bST + '\n Target : ' + string.tostring(bCT if tso == 'Exhaustion' else bSR, format.mintick)
    if bPFc and trdS:
        label.new(bar_index, b.l, 'L', xloc.bar_index, yloc.price, color.new(color.blue, 25), label.style_label_up, color.white, size.small, text.align_center, lTT + '\n\nnot a finacial advice, subject to high risk')
        alert(syminfo.ticker + ' : ' + lTT + '\n Price    : ' + string.tostring(close, format.mintick) + '\n\nnot a finacial advice, subject to high risk')
        lTrd = True
        sTrd = False
    if war and lTrd and (b.o > b.c) and (S.bSC == 2) and (not sTrd):
        label.new(bar_index, b.h, '⚠️', xloc.bar_index, yloc.price, color.new(color.blue, 100), label.style_label_down, color.yellow, size.large, text.align_center, 'Warning\nbearish price flip detected')
        lTrd = False
    if war and lTrd and (b.o > b.c) and (b.c < bSD[1] or b.c < bCD[1]):
        label.new(bar_index, b.h, '⚠️', xloc.bar_index, yloc.price, color.new(color.blue, 100), label.style_label_down, color.yellow, size.large, text.align_center, 'Critical Warning\nstop/risk level breached')
        lTrd = False
    pTxt = string.tostring(b.c, format.mintick)
    tTxt = syminfo.ticker
    if f_xLX(b.c, bSR) and srL:
        alert(tTxt + ' crossing resistance level detected, price ' + string.tostring(bSR, format.mintick))
    f_xLX_1 = f_xLX(b.c, sSD)
    if f_xLX(b.c, bSD) or (f_xLX_1 and rsB):
        alert(tTxt + ' crossing momentum risk level detected, price ' + string.tostring(bSD, format.mintick))
    if f_xLX(b.c, sSS) and srL:
        alert(tTxt + ' crossing support level detected, price ' + string.tostring(sSS, format.mintick))
    f_xLX_2 = f_xLX(b.c, sCD)
    if f_xLX(b.c, bCD) or (f_xLX_2 and rsE):
        alert(tTxt + ' crossing trend exhaustion risk level detected, price ' + string.tostring(bCD, format.mintick))
    if S.bSC == 9 and cmpltd:
        alert(tTxt + ' bullish momentum phase completion detected, price ' + pTxt)
    if S.sSC == 9 and cmpltd:
        alert(tTxt + ' bearish momentum phase completion detected, price ' + pTxt)
    if C.bCC == 13 and cmpltd:
        alert(tTxt + ' bullish trend exhaustion phase completion detected, price ' + pTxt)
    if C.sCC == 13 and cmpltd:
        alert(tTxt + ' bearish trend exhaustion phase completion detected, price ' + pTxt)
    if bSR > 0 and bSR[1] == 0:
        alert(tTxt + ' bearish momentum detected, price ' + pTxt)
    if sSS > 0 and sSS[1] == 0:
        alert(tTxt + ' bullish momentum detected, price ' + pTxt)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
