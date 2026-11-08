"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_float
from pynecore.lib import (
    alertcondition, array, bar_index, box, chart, close, color, fill, high,
    hlc3, hline, input, location, low, math, na, nz, open, plot, plotshape, script, shape, size,
    syminfo, ta
)
from pynecore.types import Box, Color, Persistent, PersistentSeries

t1: str = "Primary range horizon for Z-Pulse. Lower values react faster to local range position."
t2: str = "Stochastic pulse applied to the primary range reading. Lower values make Z-Pulse more reactive."
t3: str = "EMA smoothing applied to Z-Pulse. A value of 1 keeps the pulse raw."
t4: str = "Medium horizon used by Z-Trend to measure structural range position."
t5: str = "Macro horizon that dominates Z-Trend and gives it its long trend-following character."
t6: str = "EMA smoothing applied to the Z-Trend target. Higher values make the line steadier."
t7: str = "Strengthens persistence when Z-Trend repeatedly occupies an outer range zone."
t8: str = "Base exhaustion zone. Sensitivity expands or contracts this zone around the default value."
t9: str = "Strong global exhaustion sensitivity. 1 is intentionally loose, fast and inconsistent. 5 is balanced. 10 is strict, selective and persistent."
t10: str = "Main smoothing control for Pressure Core. Higher values calm its reactive pressure component."
t11: str = "Controls the balance between the fixed macro regime and reactive pressure in Pressure Core."
t12: str = "Color of the reactive Z-Pulse line."
t13: str = "Color of the macro-weighted Z-Trend line."
t14: str = "Bull, bear and neutral colors used by Pressure Core."
t15: str = "Thickness of the Pressure Core line."
t16: str = "Fills the space between Z-Pulse and Z-Trend with fading hot and cold extreme gradients."
t17: str = "Draws persistent price boxes while Z-Pulse and Z-Trend remain in a pressure exhaustion state."
t18: str = "Colors of the upper and lower pressure levels shown in the oscillator pane."
t19: str = "Transparency of the upper and lower pressure levels. 0 is fully visible and 100 is invisible."
gP: str = "1. Z-Pulse"
gT: str = "2. Z-Trend"
gE: str = "3. Pressure Exhaustion"
gC: str = "4. Pressure Core"
gS: str = "5. Colors & Style"
sw: float = 0.18
mw: float = 0.72
th: float = 0.92
rl: int = 21
gl: int = 112
gm: int = 3


@script.indicator("Zeiierman Trend Pressure (Zeiierman)", precision=2, explicit_plot_zorder=True, max_boxes_count=500)
def main(
    fl=input.int(21, "Pulse Range", minval=3, group=gP, tooltip=t1),
    pl=input.int(9, "Pulse Stochastic", minval=3, group=gP, tooltip=t2),
    ps=input.int(7, "Pulse Smoothing", minval=1, maxval=50, group=gP, tooltip=t3),
    sl=input.int(55, "Trend Range", minval=5, group=gT, tooltip=t4),
    ml=input.int(120, "Macro Trend", minval=10, group=gT, tooltip=t5),
    ts=input.int(5, "Trend Smoothing", minval=1, maxval=30, group=gT, tooltip=t6),
    db=input.float(9.0, "Trend Persistence", minval=0.0, maxval=20.0, step=0.5, group=gT, tooltip=t7),
    zn=input.int(20, "Exhaustion Zone", minval=5, maxval=40, group=gE, tooltip=t8),
    sn=input.int(7, "Sensitivity", minval=1, maxval=10, group=gE, tooltip=t9),
    xc=input.bool(False, "Pulse / Trend Crosses", group=gE),
    rm=input.int(16, "Reactive Smoothing", minval=1, maxval=30, group=gC, tooltip=t10),
    gw=input.float(0.65, "Regime Weight", minval=0.0, maxval=1.0, step=0.05, group=gC, tooltip=t11),
    cc=input.color(color.new('#2962FF'), "Cold", inline="z", group=gS),
    hc=input.color(color.new('#E6283E'), "Hot", inline="z", group=gS),
    ulc=input.color(color.new('#E6283E'), "Upper Level", inline="lv", group=gS, tooltip=t18),
    llc=input.color(color.new('#2962FF'), "Lower Level", inline="lv", group=gS, tooltip=t18),
    lvt=input.int(20, "Level Transparency", minval=0, maxval=100, group=gS, tooltip=t19),
    pc=input.color(color.new('#E5E7EB'), "Z-Pulse", inline="l", group=gS, tooltip=t12),
    zc=input.color(color.rgb(139, 174, 255), "Z-Trend", inline="l", group=gS, tooltip=t13),
    cbc=input.color(color.new('#40E3C3'), "Core Bull", inline="tc", group=gS, tooltip=t14),
    csc=input.color(color.new('#DF5141'), "Core Bear", inline="tc", group=gS, tooltip=t14),
    cnc=input.color(color.silver, "Core Neutral", inline="tc", group=gS, tooltip=t14),
    cw=input.int(2, "Core Width", minval=1, maxval=4, group=gS, tooltip=t15),
    sf=input.bool(True, "Gradient Fill", group=gS, tooltip=t16),
    bx=input.bool(True, "Price Boxes", inline="b", group=gS, tooltip=t17),
    mb=input.int(60, "#", minval=1, maxval=300, inline="b", group=gS)
):
    F: int = 0
    S: int = 1
    M: int = 2

    bh: Persistent[list[Box]] = array.new_box()

    ud: PersistentSeries[float] = 0.0
    dd: PersistentSeries[float] = 0.0
    tz: PersistentSeries[float] = na(float)

    est: PersistentSeries[int] = 0
    ucn: Persistent[int] = 0
    lcn: Persistent[int] = 0

    ubx: Persistent[Box] = na(Box)
    lbx: Persistent[Box] = na(Box)

    ut: Persistent[float] = na(float)
    ub: Persistent[float] = na(float)
    lt: Persistent[float] = na(float)
    lb: Persistent[float] = na(float)

    def clp(v: float, lo: float, hi: float):
        return math.max(lo, math.min(hi, v))

    def sm(v: float, k: int):
        return ta.ema(v, k) if k > 1 else v

    def wr(k: int):
        hh = ta.highest(high, k)
        ll = ta.lowest(low, k)
        return 100.0 * (close - hh) / math.max(hh - ll, syminfo.mintick)

    def eff(k: int):
        p = ta.sma(math.abs(close - close[1]), k) * k
        n = na if na(close[k]) else math.abs(close - close[k])
        return na if na(p) or na(n) else clp(n / math.max(p, syminfo.mintick), 0.0, 1.0)

    def stk(x: float, k: int):
        hi = ta.highest(x, k)
        lo = ta.lowest(x, k)
        return -100.0 + 100.0 * (x - lo) / math.max(hi - lo, 1e-10)

    def con(a: list[float], w: list[float]):
        ws0 = array.get(w, F) + array.get(w, S) + array.get(w, M)
        return clp((array.get(a, F) * array.get(w, F) + array.get(a, S) * array.get(w, S) + array.get(a, M) * array.get(w, M)) / math.max(ws0, 1e-10), -100.0, 0.0)

    def agr(a: list[float]):
        d = math.abs(array.get(a, F) - array.get(a, S)) + math.abs(array.get(a, S) - array.get(a, M)) + math.abs(array.get(a, F) - array.get(a, M))
        return 1.0 - clp(d / 300.0, 0.0, 1.0)

    def prs(k: int):
        hh = ta.highest(high, k)
        ll = ta.lowest(low, k)
        rg = math.max(hh - ll, syminfo.mintick)
        cr = math.max(high - low, syminfo.mintick)
        bh0 = math.max(open, close)
        bl0 = math.min(open, close)
        uw = high - bh0
        lw = bl0 - low
        cl = (close - ll) / rg
        mn = (hlc3 - ll) / rg
        bd = ((close - open) / cr + 1.0) * 0.5
        wk = ((lw - uw) / cr + 1.0) * 0.5
        p5 = nz(close[5], close)
        im = ((close - p5) / rg + 1.0) * 0.5
        return clp((cl * 0.42 + mn * 0.23 + bd * 0.13 + wk * 0.12 + im * 0.1) * 100.0, 0.0, 100.0)

    def alpha(prev: float, trg: float, mac: float, ag: float, ef: float, base: float, hold: float):
        side = 1 if mac > -50.0 else -1 if mac < -50.0 else 0
        pull = side == 1 and trg < prev or (side == -1 and trg > prev)
        lk = clp(0.15 + ag * ef * hold, 0.0, 0.97)
        return math.max(0.015, base * (1.0 - lk)) if pull else math.max(base * 0.75, 0.03)

    def ccore(v: float, rg: float):
        return color.new(cbc, 15) if v > 50.0 and rg > 50.0 else color.new(csc, 15) if v < 50.0 and rg < 50.0 else color.new(cnc, 35)

    def keep(a: list[Box], b: Box, lim: int):
        array.push(a, b)
        if array.size(a) > lim:
            box.delete(array.shift(a))
        return 0

    def mkbox(t: float, b: float, c: Color, br: Color):
        return box.new(bar_index - 1, t, bar_index, b, bgcolor=color.new(c, 80), border_color=br, border_width=1, force_overlay=True)

    def grow(b: Box, t: float, d: float):
        nt = math.max(t, high)
        nd = math.min(d, low)
        box.set_right(b, bar_index)
        box.set_top(b, nt)
        box.set_bottom(b, nd)
        return (nt, nd)

    rz: list[float] = array.from_items(wr(fl), wr(sl), wr(ml))

    rf = array.get(rz, F)
    rp = stk(rf, pl)

    pr = clp(rf * 0.72 + rp * 0.28, -100.0, 0.0)
    pz = sm(pr, ps)

    fw = math.max(0.0, 1.0 - sw - mw)
    twt: list[float] = array.from_items(fw, sw, mw)

    cn = con(rz, twt)
    ag = agr(rz)
    ef = nz(eff(sl), 0.0)

    ud = math.min(1.0, nz(ud[1]) * 0.93 + 0.07) if cn > -30.0 else nz(ud[1]) * 0.94
    dd = math.min(1.0, nz(dd[1]) * 0.93 + 0.07) if cn < -70.0 else nz(dd[1]) * 0.94

    tg0 = clp(cn + db * (ud - dd), -100.0, 0.0)
    tg = sm(tg0, 2)

    ba = 2.0 / (ts + 1.0)
    pa = ba if na(tz[1]) else alpha(tz[1], tg, array.get(rz, M), ag, ef, ba, th)

    tz = tg if na(tz[1]) else clp(tz[1] + pa * (tg - tz[1]), -100.0, 0.0)

    cp = ta.ema(prs(rl), rm)
    cg = ta.ema(prs(gl), gm)

    c0 = cg * gw + cp * (1.0 - gw)
    cz = c0 - 100.0
    ccl = ccore(c0, cg)

    d = cast_float(sn - 5)

    ez = clp(cast_float(zn) - d * 4.0, 8.0, 42.0)
    rb = clp(8.0 + d * 1.75, 1.0, 18.0)
    cf = 1 if sn <= 5 else 2 if sn <= 7 else 3 if sn <= 9 else 4
    fastExit = sn <= 2

    up = -ez
    dn = -100.0 + ez
    ur = up - rb
    lr = dn + rb

    uc = pz >= up and tz >= up
    lc = pz <= dn and tz <= dn

    ucn = ucn + 1 if uc else 0
    lcn = lcn + 1 if lc else 0

    ux = pz < ur or tz < ur if fastExit else pz < ur and tz < ur
    lx = pz > lr or tz > lr if fastExit else pz > lr and tz > lr

    if est == 0:
        if ucn >= cf:
            est = 1
        elif lcn >= cf:
            est = -1
    elif est == 1 and ux:
        est = 0
    elif est == -1 and lx:
        est = 0

    ue = est == 1
    le = est == -1

    us = ue and nz(est[1], 0) != 1
    ls = le and nz(est[1], 0) != -1

    ubk = est == 0 and nz(est[1], 0) == 1
    lbk = est == 0 and nz(est[1], 0) == -1

    xup = ta.crossover(pz, tz)
    xdn = ta.crossunder(pz, tz)

    hm = color.new(hc, 60)
    cm = color.new(cc, 60)

    ul = color.new(ulc, lvt)
    ll = color.new(llc, lvt)

    inv = color.new(color.black, 100)

    hline(0, 'Upper Bound', ul)
    pU = plot(up, 'Upper Pressure Level', color=ul, linewidth=1)

    hline(-50, 'Equilibrium', color.new(chart.fg_color, 80))

    pD = plot(dn, 'Lower Pressure Level', color=ll, linewidth=1)
    hline(-100, 'Lower Bound', ll)

    pP = plot(pz, 'Z-Pulse', color=pc, linewidth=1)
    pT = plot(tz, 'Z-Trend', color=zc, linewidth=2)
    pC = plot(cz, 'Pressure Core', color=ccl, linewidth=cw)

    gh = color.new(hc, 100) if sf else inv
    gc = color.new(cc, 100) if sf else inv

    fill(pP, pT, 0, -30, top_color=color.new(gh, 0), bottom_color=gh, title='Upper Pressure Gradient')
    fill(pP, pT, -70, -100, top_color=gc, bottom_color=color.new(gc, 0), title='Lower Pressure Gradient')

    plotshape(5 if ue else na, title='Upper Pressure Active', style=shape.circle, location=location.absolute, color=hm, size=size.tiny)
    plotshape(-107 if le else na, title='Lower Pressure Active', style=shape.circle, location=location.absolute, color=cm, size=size.tiny)

    plotshape(5 if us else na, title='Upper Pressure Start', style=shape.triangledown, location=location.absolute, color=hc, size=size.tiny)
    plotshape(-107 if ls else na, title='Lower Pressure Start', style=shape.triangleup, location=location.absolute, color=cc, size=size.tiny)

    plotshape(5 if ubk else na, title='Upper Pressure Release', style=shape.circle, location=location.absolute, color=hc, size=size.tiny)
    plotshape(-107 if lbk else na, title='Lower Pressure Release', style=shape.circle, location=location.absolute, color=cc, size=size.tiny)

    plot(tz if xc and (xup or xdn) else na, 'Z-Pulse / Z-Trend Cross', style=plot.style_circles, color=cc if xup else hc, linewidth=5)

    if bx:
        if us:
            if not na(ubx):
                box.delete(ubx)

            ut = high
            ub = low
            ubx = mkbox(ut, ub, hc, hm)
            keep(bh, ubx, mb)
        elif ue and (not na(ubx)):
            nut, nub = grow(ubx, ut, ub)
            ut = nut
            ub = nub
        elif ubk and (not na(ubx)):
            box.set_right(ubx, bar_index - 1)
            ubx = na

        if ls:
            if not na(lbx):
                box.delete(lbx)

            lt = high
            lb = low
            lbx = mkbox(lt, lb, cc, cm)
            keep(bh, lbx, mb)
        elif le and (not na(lbx)):
            nlt, nlb = grow(lbx, lt, lb)
            lt = nlt
            lb = nlb
        elif lbk and (not na(lbx)):
            box.set_right(lbx, bar_index - 1)
            lbx = na

    plotshape(ut if bx and ubk and (not na(ut)) else na, title='Upper Pressure Release Price', style=shape.triangledown, location=location.absolute, color=hc, size=size.tiny, force_overlay=True)
    plotshape(lb if bx and lbk and (not na(lb)) else na, title='Lower Pressure Release Price', style=shape.triangleup, location=location.absolute, color=cc, size=size.tiny, force_overlay=True)

    alertcondition(ubk, 'Upper Pressure Release', 'Zeiierman Trend Pressure upper pressure released on {{ticker}} {{interval}}.')
    alertcondition(lbk, 'Lower Pressure Release', 'Zeiierman Trend Pressure lower pressure released on {{ticker}} {{interval}}.')

    alertcondition(xup, 'Bullish Z-Pulse / Z-Trend Cross', 'Z-Pulse crossed above Z-Trend on {{ticker}} {{interval}}.')
    alertcondition(xdn, 'Bearish Z-Pulse / Z-Trend Cross', 'Z-Pulse crossed below Z-Trend on {{ticker}} {{interval}}.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
