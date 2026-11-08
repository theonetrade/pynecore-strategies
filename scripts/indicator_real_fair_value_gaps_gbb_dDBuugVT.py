"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_udt import udt
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, array, bar_index, barmerge, barstate, box, close, color,
    display, extend, format, high, input, label, line, low, math, na, plot, position, request,
    script, size, string, syminfo, ta, table, text, time, timeframe, xloc
)
from pynecore.types import Box, Color, Label, NA, Persistent, Table


@udt
class Gap:
    top: float = na(float)
    bottom: float = na(float)
    mid: float = na(float)
    dir: int = na(int)
    layer: int = na(int)
    createdBar: int = na(int)
    createdTime: int = na(int)
    leftBar: int = na(int)
    leftTime: int = na(int)
    state: int = na(int)
    inverted: bool = na(bool)
    maxPen: float = na(float)
    mitBar: int = na(int)
    mitTime: int = na(int)
    spot: bool = na(bool)
    lastT: float = na(float)
    dirty: bool = na(bool)
    bBase: Box = na(Box)
    bBand1: Box = na(Box)
    bBand2: Box = na(Box)
    bBand3: Box = na(Box)
    bBand4: Box = na(Box)
    bMid: Box = na(Box)
    bFill: Box = na(Box)
    bNotch: Box = na(Box)
    lChip: Label = na(Label)


@udt
class State:
    capHit: bool = na(bool)
    atSum0: float = na(float)
    atN0: int = na(int)
    atSum1: float = na(float)
    atN1: int = na(int)


g_det: str = "Detection"
g_mit: str = "Mitigation"
g_htf: str = "Higher timeframe"
g_look: str = "Look"
g_disp: str = "Display"
C_NEUTRAL: Color = color.new('#787B86')
C_BUY: Color = color.new('#00E676')
C_SELL: Color = color.new('#FF3D71')
C_CALM_UP: Color = color.new('#2979FF')
C_CALM_DN: Color = color.new('#FFB000')
C_AMBER_: Color = color.new('#FFB000')
C_RED_: Color = color.new('#FF3D71')
C_PANEL: Color = color.new('#1E222D')
ST_FRESH: int = 0
ST_TOUCHED: int = 1
ST_MIDTAP: int = 2
ST_MIT: int = 3
EV_NONE: int = 0
EV_NEW_BULL: int = 1
EV_NEW_BEAR: int = 2
EV_TOUCH: int = 3
EV_MIDTAP: int = 4
EV_MIT: int = 5
EV_INV: int = 6
T_BASE: float = 93.0
T_BAND1: float = 89.0
T_BAND2: float = 85.0
T_BAND3: float = 81.0
T_BAND4: float = 77.0
T_GHOST: float = 96.0
BIG: float = 1e+300


@script.indicator("Real Fair Value Gaps [GBB]", shorttitle="RFVG [GBB]", overlay=True, max_boxes_count=500, max_lines_count=100, max_labels_count=50, max_bars_back=500)
def main(
    sizeAtr=input.float(0.0, "Min size (ATR x)", minval=0, step=0.1, group=g_det, tooltip="Ignore gaps smaller than this multiple of ATR(14) on the gap's own timeframe. 0 = off."),
    autoThresh=input.bool(False, "Auto threshold", group=g_det, tooltip="Keep a gap only if its height relative to price is above the running mean of all candidates so far. Overrides Min size."),
    needDisp=input.bool(False, "Require displacement", group=g_det, tooltip="Candle 2 must close beyond candle 1's extreme (LuxAlgo rule)."),
    mitSource=input.string("Wick", "Source", options=("Wick", "Close"), group=g_mit),
    mitPoint=input.string("Far edge", "Point", options=("Near edge", "Midpoint", "Far edge"), group=g_mit, tooltip="A gap is mitigated when the source reaches this level. Far edge = fully filled."),
    trackInv=input.bool(True, "Track inversions", group=g_mit, tooltip="A close beyond the far edge flips the gap's colour and bias instead of retiring it."),
    htfOn=input.bool(True, "Enable", group=g_htf),
    htfIn=input.timeframe("", "Timeframe", group=g_htf, tooltip="Empty = one step above the chart (1m->15m, 5m->1H, 15m->4H, 1H->D, 4H->W, D->W)."),
    palette=input.string("GBB", "Palette", options=("GBB", "Calm blue-amber", "Custom"), group=g_look),
    customUp=input.color(color.new('#00E676'), "Custom up", inline="cc", group=g_look),
    customDn=input.color(color.new('#FF3D71'), "down", inline="cc", group=g_look),
    glowPct=input.int(100, "Glow intensity (%)", minval=0, maxval=150, group=g_look),
    spotN=input.int(6, "Spotlight gaps", minval=0, maxval=20, group=g_look, tooltip="Only the N active gaps nearest to price carry the full glow. Others keep a thin outline."),
    fadeBars=input.int(100, "Fade over (bars)", minval=1, group=g_look, tooltip="Glow decays to half strength over this many bars, then holds."),
    keepBars=input.int(500, "Keep mitigated (bars)", minval=0, group=g_look),
    labelMode=input.string("HTF badge", "Labels", options=("HTF badge", "All", "None"), group=g_look),
    showAtr=input.float(6.0, "Show gaps within (ATR x)", minval=0, step=1, group=g_look, tooltip="Gaps farther than this many ATR(14) from the close are tracked but not drawn, so far-away gaps do not stretch the price scale. 0 = draw everything."),
    showTable=input.bool(True, "Show info table", group=g_disp)
):
    MAX_RECORDS: int = 500 - 7 * spotN - 2

    cUp: Color = C_BUY if palette == 'GBB' else C_CALM_UP if palette == 'Calm blue-amber' else customUp
    cDn: Color = C_SELL if palette == 'GBB' else C_CALM_DN if palette == 'Calm blue-amber' else customDn


    gaps: Persistent[list[Gap]] = array.new(0, NA(Gap))
    S: Persistent[State] = State(False, 0.0, 0, 0.0, 0)
    cumMit: Persistent[int] = 0
    cumMit0: Persistent[int] = 0
    cumCreated: Persistent[int] = 0

    atr14: float = ta.atr(14)

    def f_reach(d: int, v: float, lvl: float):
        return v <= lvl if d > 0 else v >= lvl

    def f_beyond(d: int, v: float, lvl: float):
        return v < lvl if d > 0 else v > lvl

    def f_detect(h1: float, l1: float, c2: float, h3: float, l3: float, useDisp: bool):
        d: int = 0
        t: float = na(float)
        b: float = na(float)
        if l3 > h1 and (not useDisp or c2 > h1):
            d = 1
            t = l3
            b = h1
        elif h3 < l1 and (not useDisp or c2 < l1):
            d = -1
            t = l1
            b = h3
        return (d, t, b)

    def f_col(g: Gap):
        return cUp if g.dir > 0 else cDn

    def f_fresh(g: Gap):
        return math.max(0.5, 1.0 - 0.5 * (bar_index - g.createdBar) / fadeBars)

    def f_transp(g: Gap, base: float):
        mult: float = (0.8 if g.layer == 1 else 1.0) * (0.7 if g.inverted else 1.0)
        t: float = 100.0 - (100.0 - base) * (glowPct / 100.0) * f_fresh(g) * mult
        return math.max(0.0, math.min(100.0, t))

    def f_htfAuto(tf: str):
        s: int = timeframe.in_seconds(tf)
        return '15' if s <= 180 else '60' if s <= 300 else '240' if s <= 1800 else 'D' if s <= 7200 else 'W' if s <= 86400 else 'M'

    def f_tfLabel(tf: str):
        s: int = timeframe.in_seconds(tf)
        return string.tostring(s / 60) + 'm' if s < 3600 else string.tostring(s / 3600) + 'H' if s < 86400 else 'D' if s == 86400 else 'W' if s == 604800 else 'M'

    htf: str = f_htfAuto(timeframe.period) if htfIn == '' else htfIn
    htfValid: bool = htfOn and timeframe.in_seconds(htf) > timeframe.in_seconds(timeframe.period)
    htfLabel: str = f_tfLabel(htf)

    def f_newBox(g: Gap, t: float, b: float, bg: Color, bc: Color, bs: str):
        return box.new(g.leftTime, t, time, b, xloc=xloc.bar_time, border_color=bc, border_width=1, border_style=bs, bgcolor=bg, extend=extend.right)

    def f_fillBounds(g: Gap):
        ft: float = na(float)
        fb: float = na(float)
        if g.dir > 0:
            ft = g.top
            fb = g.top - g.maxPen
        else:
            ft = g.bottom + g.maxPen
            fb = g.bottom
        return (ft, fb)

    def f_remBounds(g: Gap):
        rt: float = g.top
        rb: float = g.bottom
        if g.state >= ST_TOUCHED and g.maxPen > 0:
            if g.dir > 0:
                rt = g.top - g.maxPen
            else:
                rb = g.bottom + g.maxPen
        return (rt, rb)

    def f_clip(bx: Box, t: float, b: float, rt: float, rb: float):
        ct: float = math.min(t, rt)
        cb: float = math.max(b, rb)
        if ct < cb:
            cb = ct
        box.set_top(bx, ct)
        return box.set_bottom(bx, cb)

    def f_borderStyle(g: Gap):
        return line.style_dotted if g.inverted else line.style_dashed if g.layer == 1 else line.style_solid

    def f_dist(g: Gap):
        return 0.0 if close >= g.bottom and close <= g.top else math.min(math.abs(close - g.top), math.abs(close - g.bottom))

    def f_visible(g: Gap):
        return showAtr <= 0 or na(atr14) or f_dist(g) <= showAtr * atr14

    def f_label(g: Gap):
        s: str = ""
        if g.state != ST_MIT and labelMode != 'None' and g.spot:
            if g.layer == 0 and labelMode == 'All':
                s = "FVG"
                if g.state >= ST_TOUCHED:
                    s = 'FVG · ' + string.tostring(100.0 * g.maxPen / (g.top - g.bottom), '0') + '%'
        box.set_text(g.bBase, s)
        box.set_text_size(g.bBase, size.small if g.layer == 1 else size.tiny)
        box.set_text_color(g.bBase, color.new(f_col(g), 20))
        box.set_text_halign(g.bBase, text.align_right)
        return box.set_text_valign(g.bBase, text.align_center)

    def f_chipTxt(g: Gap):
        pre: str = 'IFVG · ' if g.inverted else htfLabel + ' · ' if g.layer == 1 else ''
        return pre + string.tostring(g.mid, format.mintick)

    def f_spotOn(g: Gap):
        c: Color = f_col(g)
        h: float = g.top - g.bottom
        g.bBand1 = f_newBox(g, g.mid + 0.4 * h, g.mid - 0.4 * h, color.new(c, f_transp(g, T_BAND1)), color.new(c, 100), line.style_solid)
        g.bBand2 = f_newBox(g, g.mid + 0.3 * h, g.mid - 0.3 * h, color.new(c, f_transp(g, T_BAND2)), color.new(c, 100), line.style_solid)
        g.bBand3 = f_newBox(g, g.mid + 0.2 * h, g.mid - 0.2 * h, color.new(c, f_transp(g, T_BAND3)), color.new(c, 100), line.style_solid)
        g.bBand4 = f_newBox(g, g.mid + 0.1 * h, g.mid - 0.1 * h, color.new(c, f_transp(g, T_BAND4)), color.new(c, 100), line.style_solid)
        g.bMid = f_newBox(g, g.mid, g.mid, color.new(c, 100), color.new(c, 20), line.style_dotted)

        wMs: int = 1000 * timeframe.in_seconds(timeframe.period)
        g.bNotch = box.new(g.leftTime, g.top, g.leftTime + wMs, g.bottom, xloc=xloc.bar_time, border_color=color.new(c, 100), bgcolor=color.new(c, 30))

        if labelMode != 'None':
            g.lChip = label.new(bar_index, g.mid, f_chipTxt(g), style=label.style_label_left, color=color.new(C_PANEL, 15), textcolor=c, size=size.small)
        g.spot = True
        g.dirty = True
        return g.dirty

    def f_spotOff(g: Gap):
        box.delete(g.bBand1)
        box.delete(g.bBand2)
        box.delete(g.bBand3)
        box.delete(g.bBand4)
        box.delete(g.bMid)
        box.delete(g.bFill)
        box.delete(g.bNotch)
        label.delete(g.lChip)
        g.bBand1 = NA(Box)
        g.bBand2 = NA(Box)
        g.bBand3 = NA(Box)
        g.bBand4 = NA(Box)
        g.bMid = NA(Box)
        g.bFill = NA(Box)
        g.bNotch = NA(Box)
        g.lChip = NA(Label)
        g.spot = False
        g.dirty = True
        return g.dirty

    def f_style(g: Gap):
        c: Color = f_col(g)
        tb: float = f_transp(g, T_BASE) if g.spot else T_GHOST
        if g.dirty or math.abs(tb - g.lastT) >= 1.0:
            g.lastT = tb
            rt, rb = f_remBounds(g)
            h: float = g.top - g.bottom
            box.set_bgcolor(g.bBase, color.new(c, tb))
            box.set_border_color(g.bBase, color.new(c, 35 if g.spot else 75))
            box.set_border_style(g.bBase, f_borderStyle(g))
            f_clip(g.bBase, g.top, g.bottom, rt, rb)
            if g.spot:
                box.set_bgcolor(g.bBand1, color.new(c, f_transp(g, T_BAND1)))
                box.set_bgcolor(g.bBand2, color.new(c, f_transp(g, T_BAND2)))
                box.set_bgcolor(g.bBand3, color.new(c, f_transp(g, T_BAND3)))
                box.set_bgcolor(g.bBand4, color.new(c, f_transp(g, T_BAND4)))
                f_clip(g.bBand1, g.mid + 0.4 * h, g.mid - 0.4 * h, rt, rb)
                f_clip(g.bBand2, g.mid + 0.3 * h, g.mid - 0.3 * h, rt, rb)
                f_clip(g.bBand3, g.mid + 0.2 * h, g.mid - 0.2 * h, rt, rb)
                f_clip(g.bBand4, g.mid + 0.1 * h, g.mid - 0.1 * h, rt, rb)
                f_clip(g.bNotch, g.top, g.bottom, rt, rb)

                midLeft: bool = g.mid <= rt and g.mid >= rb
                box.set_border_color(g.bMid, color.new(c, 20 if midLeft else 100))
                box.set_bgcolor(g.bNotch, color.new(c, 30))
                if not na(g.lChip):
                    label.set_text(g.lChip, f_chipTxt(g))
                    label.set_color(g.lChip, color.new(C_PANEL, 15))
                    label.set_textcolor(g.lChip, c)
            if not na(g.bFill):
                box.set_border_color(g.bFill, color.new(c, 55))
            f_label(g)
            g.dirty = False
        if g.spot and g.state >= ST_TOUCHED and (g.maxPen > 0):
            ft, fb = f_fillBounds(g)
            if na(g.bFill):
                g.bFill = f_newBox(g, ft, fb, color.new(c, 100), color.new(c, 55), line.style_dashed)
            box.set_top(g.bFill, ft)
            box.set_bottom(g.bFill, fb)
        __block_result__ = na
        if g.spot and (not na(g.lChip)):
            __block_result__ = label.set_x(g.lChip, bar_index)
        return __block_result__

    def f_outline(g: Gap):
        f_spotOff(g)
        box.set_extend(g.bBase, extend.none)
        box.set_right(g.bBase, g.mitTime)
        box.set_top(g.bBase, g.top)
        box.set_bottom(g.bBase, g.bottom)
        box.set_bgcolor(g.bBase, color.new(C_NEUTRAL, 98))
        box.set_border_color(g.bBase, color.new(C_NEUTRAL, 85))
        box.set_border_style(g.bBase, line.style_dashed)
        return box.set_text(g.bBase, '')

    def f_baseOn(g: Gap):
        c: Color = f_col(g)
        g.bBase = f_newBox(g, g.top, g.bottom, color.new(c, 100), color.new(c, 100), f_borderStyle(g))
        g.lastT = -1.0
        g.dirty = True
        __block_result_1__ = na
        if g.state == ST_MIT:
            __block_result_1__ = f_outline(g)
        return __block_result_1__

    def f_baseOff(g: Gap):
        f_spotOff(g)
        box.delete(g.bBase)
        g.bBase = NA(Box)
        return g.bBase

    def f_drop(g: Gap):
        return f_baseOff(g)

    def f_passes(layer: int, h: float, atrV: float, price: float):
        ok: bool = True
        if autoThresh:
            rel: float = h / price
            mean: float = (S.atSum0 / S.atN0 if S.atN0 > 0 else 0.0) if layer == 0 else S.atSum1 / S.atN1 if S.atN1 > 0 else 0.0
            if layer == 0:
                S.atSum0 += rel
                S.atN0 += 1
            else:
                S.atSum1 += rel
                S.atN1 += 1
            ok = rel > mean
        elif sizeAtr > 0:
            ok = not na(atrV) and h >= sizeAtr * atrV
        return ok

    def f_mitigate(g: Gap):
        g.state = ST_MIT
        g.mitBar = bar_index
        g.mitTime = time
        __block_result_2__ = na
        if not na(g.bBase):
            __block_result_2__ = f_outline(g)
        return __block_result_2__

    def f_invert(g: Gap):
        g.dir = -g.dir
        g.inverted = True
        g.state = ST_FRESH
        g.maxPen = 0.0
        g.createdBar = bar_index
        g.createdTime = time
        box.delete(g.bFill)
        g.bFill = NA(Box)
        g.dirty = True
        return g.dirty

    def f_update(g: Gap, hi: float, lo: float, cl: float, closeValid: bool):
        ev: int = EV_NONE
        w: float = lo if g.dir > 0 else hi
        near: float = g.top if g.dir > 0 else g.bottom
        far: float = g.bottom if g.dir > 0 else g.top
        h: float = g.top - g.bottom
        if f_reach(g.dir, w, near):
            pen: float = g.top - lo if g.dir > 0 else hi - g.bottom
            np: float = math.min(h, math.max(g.maxPen, pen))
            if np != g.maxPen:
                g.maxPen = np
                g.dirty = True
            if g.state < ST_TOUCHED:
                g.state = ST_TOUCHED
                ev = EV_TOUCH
            if g.state < ST_MIDTAP and f_reach(g.dir, w, g.mid):
                g.state = ST_MIDTAP
                ev = EV_MIDTAP
        done: bool = False
        if closeValid and f_beyond(g.dir, cl, far):
            if trackInv and (not g.inverted):
                f_invert(g)
                ev = EV_INV
            else:
                f_mitigate(g)
                ev = EV_MIT
            done = True
        if not done:
            point: float = near if mitPoint == 'Near edge' else g.mid if mitPoint == 'Midpoint' else far
            src: float = w if mitSource == 'Wick' else cl if closeValid else na
            if not na(src) and f_reach(g.dir, src, point):
                f_mitigate(g)
                ev = EV_MIT
        return ev

    def f_budget():
        __block_result_3__ = na
        if array.size(gaps) >= MAX_RECORDS:
            victim: int = -1
            key: int = 0
            for i, g in enumerate(gaps):
                if g.state == ST_MIT and (victim < 0 or g.mitBar < key):
                    victim = i
                    key = g.mitBar
            if victim < 0:
                for i, g in enumerate(gaps):
                    if not g.spot and (victim < 0 or g.createdBar < key):
                        victim = i
                        key = g.createdBar
                if victim >= 0:
                    S.capHit = True
            __block_result_4__ = na
            if victim >= 0:
                f_drop(array.get(gaps, victim))
                __block_result_4__ = array.remove(gaps, victim)
            __block_result_3__ = __block_result_4__
        return __block_result_3__

    def f_add(d: int, t: float, b: float, layer: int, leftBar: int, leftTime: int):
        f_budget()
        g: Gap = Gap(top=t, bottom=b, mid=(t + b) / 2.0, dir=d, layer=layer, createdBar=bar_index, createdTime=time, leftBar=leftBar, leftTime=leftTime, state=ST_FRESH, inverted=False, maxPen=0.0, mitBar=-1, mitTime=-1, spot=False, lastT=-1.0, dirty=True, bBase=NA(Box), bBand1=NA(Box), bBand2=NA(Box), bMid=NA(Box), bFill=NA(Box))
        return array.push(gaps, g)

    def f_spotlight():
        n: int = array.size(gaps)
        __block_result_5__ = na
        if n > 0:
            dist: list[float] = array.new_float(n, BIG)
            chosen: list[bool] = array.new_bool(n, False)
            for i, g in enumerate(gaps):
                if g.state != ST_MIT and (not na(g.bBase)):
                    array.set(dist, i, f_dist(g))
            if spotN > 0:
                for k in pine_range(1, spotN):
                    best: int = -1
                    bd: float = BIG
                    for i in pine_range(0, n - 1):
                        if not array.get(chosen, i) and array.get(dist, i) < bd:
                            bd = array.get(dist, i)
                            best = i
                    if best >= 0 and bd < BIG:
                        array.set(chosen, best, True)
            __block_result_6__ = na
            for i, g in enumerate(gaps):
                want: bool = array.get(chosen, i)
                __block_result_7__ = na
                if want and (not g.spot):
                    __block_result_7__ = f_spotOn(g)
                elif not want and g.spot:
                    __block_result_7__ = f_spotOff(g)
                __block_result_6__ = __block_result_7__
            __block_result_5__ = __block_result_6__
        return __block_result_5__

    hH1, hL1, hH3, hL3, hC1, hC2, hT1, hT3, hAtr = request.security(syminfo.tickerid, htf, (high[1], low[1], high[3], low[3], close[1], close[2], time[1], time[3], inline_series(ta.atr(14), 1)), lookahead=barmerge.lookahead_on)
    htfNew: bool = ta.change(time(htf)) != 0

    evBar: int = 0
    evNewBull: bool = False
    evNewBear: bool = False
    evHtfBull: bool = False
    evHtfBear: bool = False
    evTouch: bool = False
    evMidtap: bool = False
    evMit: bool = False
    evInv: bool = False

    if barstate.isconfirmed:
        for g in gaps:
            if g.state != ST_MIT:
                cv: bool = True if g.layer == 0 else htfNew
                cl: float = close if g.layer == 0 else hC1
                ev: int = f_update(g, high, low, cl, cv)
                if g.layer == 0:
                    evBar = math.max(evBar, ev)
                if ev == EV_MIT:
                    cumMit += 1
                    if g.layer == 0:
                        cumMit0 += 1
                evTouch = evTouch or ev == EV_TOUCH
                evMidtap = evMidtap or ev == EV_MIDTAP
                evMit = evMit or ev == EV_MIT
                evInv = evInv or ev == EV_INV

        if array.size(gaps) > 0:
            for i in pine_range(array.size(gaps) - 1, 0):
                g: Gap = array.get(gaps, i)
                if g.state == ST_MIT and bar_index - g.mitBar > keepBars:
                    f_drop(g)
                    array.remove(gaps, i)

        if bar_index >= 2:
            d, t, b = f_detect(high[2], low[2], close[1], high, low, needDisp)
            if d != 0 and f_passes(0, t - b, atr14, close):
                f_add(d, t, b, 0, bar_index - 2, time[2])
                cumCreated += 1
                evBar = math.max(evBar, EV_NEW_BULL if d > 0 else EV_NEW_BEAR)
                evNewBull = evNewBull or d > 0
                evNewBear = evNewBear or d < 0

        if htfValid and htfNew:
            d2, t2, b2 = f_detect(hH3, hL3, hC2, hH1, hL1, needDisp)
            if d2 != 0 and f_passes(1, t2 - b2, hAtr, hC1):
                f_add(d2, t2, b2, 1, na, hT3)
                cumCreated += 1
                evHtfBull = evHtfBull or d2 > 0
                evHtfBear = evHtfBear or d2 < 0

        for g in gaps:
            vis: bool = f_visible(g)
            if vis and na(g.bBase):
                f_baseOn(g)
            elif not vis and (not na(g.bBase)):
                f_baseOff(g)
        f_spotlight()

        for g in gaps:
            if g.state != ST_MIT and (not na(g.bBase)):
                f_style(g)

    nBull: int = 0
    nBear: int = 0
    nHtf: int = 0
    nFar: int = 0
    for g in gaps:
        if g.state != ST_MIT:
            if na(g.bBase):
                nFar += 1
            if g.layer == 1:
                nHtf += 1
            elif g.dir > 0:
                nBull += 1
            else:
                nBear += 1

    plot(nBull, 'nBullActive', display=display.data_window)
    plot(nBear, 'nBearActive', display=display.data_window)
    plot(cumMit0, 'nMitigated', display=display.data_window)
    plot(nHtf, 'nHtfActive', display=display.data_window)
    plot(evBar, 'lastEvent', display=display.data_window)

    nearAbove: float = na(float)
    nearBelow: float = na(float)
    for g in gaps:
        if g.state != ST_MIT:
            if g.bottom > close and (na(nearAbove) or g.bottom < nearAbove):
                nearAbove = g.bottom
            if g.top < close and (na(nearBelow) or g.top > nearBelow):
                nearBelow = g.top

    tbl: Persistent[Table] = table.new(position.top_right, 2, 7, border_width=0, frame_color=color.new('#2A2F3A'), frame_width=1)
    if showTable and barstate.islast:
        warn: str = 'budget hit: oldest gaps dropped' if S.capHit else 'HTF off: not above chart TF' if htfOn and (not htfValid) else ''
        warnCol: Color = C_RED_ if S.capHit else C_AMBER_
        fillN: int = math.round(10.0 * cumMit / cumCreated) if cumCreated > 0 else 0
        fillTxt: str = string.repeat('▰', fillN) + string.repeat('▱', 10 - fillN) + ' ' + string.tostring(100.0 * cumMit / cumCreated, '0') + '%' if cumCreated > 0 else '—'
        bg: Color = color.new(C_PANEL, 0)
        hasWarn: bool = warn != ''
        table.cell(tbl, 0, 0, 'FVG · GBB', text_color=color.white, bgcolor=bg, text_size=size.small, text_halign=text.align_left)
        table.cell(tbl, 1, 0, htfLabel + ' · ' + string.tostring(nHtf) + ' active' if htfValid else 'HTF off: not above chart TF' if htfOn else 'HTF off', text_color=C_NEUTRAL, bgcolor=bg, text_size=size.tiny, text_halign=text.align_right)
        table.cell(tbl, 0, 1, 'Active', text_color=C_NEUTRAL, bgcolor=bg, text_size=size.small, text_halign=text.align_left)
        table.cell(tbl, 1, 1, string.tostring(nBull) + ' bull · ' + string.tostring(nBear) + ' bear · ' + string.tostring(nFar) + ' far', text_color=color.white, bgcolor=bg, text_size=size.small, text_halign=text.align_right)
        table.cell(tbl, 0, 2, 'Above', text_color=C_NEUTRAL, bgcolor=bg, text_size=size.small, text_halign=text.align_left)
        table.cell(tbl, 1, 2, '—' if na(nearAbove) else string.tostring(nearAbove, format.mintick), text_color=cDn, bgcolor=bg, text_size=size.small, text_halign=text.align_right)
        table.cell(tbl, 0, 3, 'Below', text_color=C_NEUTRAL, bgcolor=bg, text_size=size.small, text_halign=text.align_left)
        table.cell(tbl, 1, 3, '—' if na(nearBelow) else string.tostring(nearBelow, format.mintick), text_color=cUp, bgcolor=bg, text_size=size.small, text_halign=text.align_right)
        table.cell(tbl, 0, 4, 'Fill rate', text_color=C_NEUTRAL, bgcolor=bg, text_size=size.small, text_halign=text.align_left)
        table.cell(tbl, 1, 4, fillTxt, text_color=cUp, bgcolor=bg, text_size=size.small, text_halign=text.align_right)
        table.cell(tbl, 0, 5, 'Warning' if hasWarn else '', text_color=warnCol, bgcolor=bg, text_size=size.tiny, text_halign=text.align_left)
        table.cell(tbl, 1, 5, warn if hasWarn else '', text_color=warnCol, bgcolor=bg, text_size=size.tiny, text_halign=text.align_right)
        table.cell(tbl, 0, 6, 'running counts on loaded bars — not a backtest', text_color=color.new(C_NEUTRAL, 30), bgcolor=bg, text_size=size.tiny, text_halign=text.align_left)
        table.merge_cells(tbl, 0, 6, 1, 6)

    alertcondition(evNewBull, 'New bullish FVG', 'FVG [GBB] {{ticker}} {{interval}}: new bullish gap')
    alertcondition(evNewBear, 'New bearish FVG', 'FVG [GBB] {{ticker}} {{interval}}: new bearish gap')
    alertcondition(evHtfBull, 'New HTF bullish FVG', 'FVG [GBB] {{ticker}} {{interval}}: new higher-timeframe bullish gap')
    alertcondition(evHtfBear, 'New HTF bearish FVG', 'FVG [GBB] {{ticker}} {{interval}}: new higher-timeframe bearish gap')
    alertcondition(evTouch, 'Price entered a gap', 'FVG [GBB] {{ticker}} {{interval}}: price entered a gap')
    alertcondition(evMidtap, 'Midpoint tapped', 'FVG [GBB] {{ticker}} {{interval}}: gap midpoint tapped')
    alertcondition(evMit, 'Gap mitigated', 'FVG [GBB] {{ticker}} {{interval}}: gap mitigated')
    alertcondition(evInv, 'Gap inverted', 'FVG [GBB] {{ticker}} {{interval}}: gap inverted')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)