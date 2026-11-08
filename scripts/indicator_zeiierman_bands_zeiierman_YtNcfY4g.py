"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    alertcondition, array, bar_index, barmerge, barstate, close, color, fill,
    high, input, location, low, math, na, nz, open, plot, plotshape, request, script, shape, size,
    syminfo, ta, timeframe, volume
)
from pynecore.types import Persistent, PersistentSeries, Series

t1: str = "Rolling window used by the custom liquidity mean, stress deviation, sweep horizon and OU model."
t2: str = "Outer band distance. Higher values place the outer bands farther from the custom mean."
t3: str = "Places the inner reclaim bands as a fraction of the outer deviation."
t4: str = "Enables the OU mean-reversion regime filter for reclaim triangles."
t5: str = "Controls how selective the OU filter is. Higher values require faster reversion and lower equilibrium drift."
t6: str = "Base timeframe used by the Liquidity Warp color engine. When Auto color timeframe is on and the chart timeframe equals this base timeframe, coloring steps up using the fixed auto map."
t7: str = "Measures how directly price travelled. Exact Liquidity Warp path-efficiency input."
t8: str = "Controls how quickly persistent liquidity separation builds into the color state."
t9: str = "Controls how quickly the color tension releases or reverses."
t10: str = "Caps the Liquidity Warp tension state."
t11: str = "Tension required before the bands switch from neutral to bull or bear coloring."
t12: str = "Colors used by the Liquidity Warp neutral, bull and bear states."
t13: str = "Color of confirmed reclaim triangles."
t14: str = "Enables or disables reclaim triangles and reclaim alerts."
t15: str = "When enabled, long reclaims require the bullish liquidity color regime and short reclaims require the bearish liquidity color regime."
gB: str = "1. Band Behavior"
gO: str = "2. OU Filter"
gC: str = "3. Liquidity Color Engine"
gS: str = "4. Colors & Style"


@script.indicator("Zeiierman Bands (Zeiierman)", overlay=True, behind_chart=False, dynamic_requests=True)
def main(
    n=input.int(20, "Length", minval=10, group=gB, tooltip=t1),
    m=input.float(2.0, "Deviation", minval=0.5, step=0.1, group=gB, tooltip=t2),
    r=input.float(0.75, "Reclaim Ratio", minval=0.25, maxval=0.95, step=0.05, group=gB, tooltip=t3),
    ou=input.bool(True, "Use OU Filter", group=gO, tooltip=t4),
    os=input.float(0.5, "OU Strictness", minval=0.1, maxval=2.0, step=0.1, group=gO, tooltip=t5),
    ct=input.timeframe("60", "Color timeframe", group=gC, tooltip=t6),
    at=input.bool(True, "Auto color timeframe", group=gC),
    el=input.int(3, "Path efficiency length", minval=2, maxval=200, group=gC, tooltip=t7),
    bl=input.int(6, "Tension build length", minval=1, maxval=100, group=gC, tooltip=t8),
    rl=input.int(20, "Tension release length", minval=1, maxval=100, group=gC, tooltip=t9),
    mt=input.float(8.25, "Maximum tension", minval=0.25, maxval=10.0, step=0.25, group=gC, tooltip=t10),
    rt=input.float(0.2, "Trend tension threshold", minval=0.05, maxval=2.0, step=0.05, group=gC, tooltip=t11),
    nc=input.color(color.silver, "Neutral color", group=gS, tooltip=t12),
    bc=input.color(color.aqua, "Bull color", group=gS, tooltip=t12),
    sc=input.color(color.orange, "Bear color", group=gS, tooltip=t12),
    sf=input.bool(True, "Fill bands", group=gS),
    rs=input.bool(True, "Reclaim signals", group=gS, tooltip=t14),
    trn=input.bool(False, "Align reclaims with trend", group=gS, tooltip=t15),
    lc=input.color(color.lime, "Long reclaim", inline="rec", group=gS, tooltip=t13),
    rc=input.color(color.red, "Short reclaim", inline="rec", group=gS, tooltip=t13)
):
    L: int = 0
    S: int = 1
    fm: Persistent = array.from_items(timeframe.in_seconds('1'), timeframe.in_seconds('5'), timeframe.in_seconds('15'), timeframe.in_seconds('30'), timeframe.in_seconds('60'), timeframe.in_seconds('240'), timeframe.in_seconds('1D'), timeframe.in_seconds('1W'))
    tm: Persistent[list[str]] = array.from_items('60', '60', '240', '240', '1D', '1D', '1W', '1M')
    arm: Persistent[list[bool]] = array.new_bool(2, False)

    def clp(v, lo, hi):
        return math.max(lo, math.min(hi, v))

    def avg(src: Series, k):
        s: float = 0.0
        c: float = 0.0
        for i in pine_range(0, k - 1):
            v = src[i]
            if not na(v):
                s += v
                c += 1.0
        return s / c if c > 0 else na

    def wavg(src: Series, wg: Series, k):
        s: float = 0.0
        w: float = 0.0
        for i in pine_range(0, k - 1):
            v = src[i]
            q = nz(wg[i], 0.0)
            if not na(v) and q > 0:
                s += v * q
                w += q
        return s / w if w > 0 else na

    def rdev(src: Series, md, k):
        s: float = 0.0
        c: float = 0.0
        for i in pine_range(0, k - 1):
            v = src[i]
            if not na(v) and (not na(md)):
                d = v - md
                s += d * d
                c += 1.0
        return math.sqrt(s / c) if c > 0 else na

    def rms(src: Series, k):
        s: float = 0.0
        c: float = 0.0
        for i in pine_range(0, k - 1):
            v = src[i]
            if not na(v):
                s += v * v
                c += 1.0
        return math.sqrt(s / c) if c > 0 else na

    def ar1(src: Series, k):
        sx: float = 0.0
        sy: float = 0.0
        sxy: float = 0.0
        sxx: float = 0.0
        c: float = 0.0
        for i in pine_range(0, k - 1):
            x__00000042__ = src[i + 1]
            y = src[i]
            if not na(x__00000042__) and (not na(y)):
                sx += x__00000042__
                sy += y
                sxy += x__00000042__ * y
                sxx += x__00000042__ * x__00000042__
                c += 1.0
        mx = sx / c if c > 0 else na
        my = sy / c if c > 0 else na
        cv = sxy / c - mx * my if c > 1 else na
        vx = sxx / c - mx * mx if c > 1 else na
        return cv / vx if not na(vx) and vx > 1e-12 else na

    def atf(tf):
        out = tf
        s = timeframe.in_seconds(tf)
        for i in pine_range(0, method_call('size', fm) - 1):
            if s == method_call('get', fm, i):
                out = array.get(tm, i)
                break
        return out

    def etf(tf, use, cs):
        ts = timeframe.in_seconds(tf)
        return atf(tf) if use and (not na(cs)) and (not na(ts)) and (cs == ts) else tf

    def pe(src: Series, k):
        st = math.abs(ta.change(src))
        av = ta.sma(st, k)
        tt = av * k
        nt = math.abs(src - src[k])
        return math.min(nt / tt, 1.0) if not na(tt) and (not na(nt)) and (tt > syminfo.mintick) else 0.0

    def ten(pr, tg, b, r, c):
        sd = pr == 0 or tg == 0 or math.sign(pr) == math.sign(tg)
        bd = sd and math.abs(tg) > math.abs(pr)
        a = 2.0 / (b + 1.0) if bd else 2.0 / (r + 1.0)
        return clp(pr + a * (tg - pr), -c, c)

    def armU(ok, z, lrq, srq):
        if barstate.isconfirmed:
            if not ok or lrq or srq:
                array.set(arm, L, False)
                array.set(arm, S, False)
            else:
                if z <= -m:
                    array.set(arm, L, True)
                    array.set(arm, S, False)
                if z >= m:
                    array.set(arm, S, True)
                    array.set(arm, L, False)
                if z >= 0:
                    array.set(arm, L, False)
                if z <= 0:
                    array.set(arm, S, False)
        return 0

    im = m * r
    sw = math.max(3, cast_int(math.round(n * 0.5)))
    al = math.max(30, n * 6)
    cs = timeframe.in_seconds(timeframe.period)
    tf = etf(ct, at, cs)

    c = math.max(close, syminfo.mintick)
    pc = math.max(nz(close[1], close), syminfo.mintick)
    tr = math.max(high - low, math.max(math.abs(high - pc), math.abs(low - pc)))
    va = avg(volume, n)
    ra = avg(tr, n)
    hv = not na(volume) and volume > 0 and (not na(va)) and (va > 0)
    vr = volume / va if hv else 1.0
    rr = tr / ra if not na(ra) and ra > syminfo.mintick else 1.0
    ab = clp(vr / math.max(rr, 0.2) if hv else 1.0, 0.15, 6.0)
    wt = math.pow(ab, 1.1)

    uw = math.max(0.0, high - math.max(open, close))
    dw = math.max(0.0, math.min(open, close) - low)
    ap = close + 0.105 * (dw - uw)
    pm = avg(close, n)
    lm = wavg(ap, wt, n)
    md: Series = pm + 0.1 * (lm - pm) if not na(pm) and (not na(lm)) else pm

    ph = ta.highest(high[1], sw)
    pl = ta.lowest(low[1], sw)
    us = not na(ph) and high > ph and (close < ph)
    ls = not na(pl) and low < pl and (close > pl)
    bf = ra * 0.35 if not na(ra) else tr * 0.35
    un = not na(ph) and high >= ph - bf
    ln = not na(pl) and low <= pl + bf
    ue = uw + (2.0 * (high - ph) + 0.5 * (high - close) if us else 0.0) if un else 0.0
    le = dw + (2.0 * (pl - low) + 0.5 * (close - low) if ls else 0.0) if ln else 0.0

    bs = rdev(close, md, n)
    ur = rms(uw, n)
    lr = rms(dw, n)
    uer = rms(ue, n)
    ler = rms(le, n)
    ug = math.sqrt(bs * bs + math.pow(0.3 * ur, 2) + math.pow(0.3 * uer, 2)) if not na(bs) else na
    lg = math.sqrt(bs * bs + math.pow(0.3 * lr, 2) + math.pow(0.3 * ler, 2)) if not na(bs) else na
    up = md + m * ug
    dn = md - m * lg
    ui = md + im * ug
    li = md - im * lg
    z = ((close - md) / ug if not na(ug) and ug > 1e-10 else na) if close >= md else (close - md) / lg if not na(lg) and lg > 1e-10 else na

    x = math.log(c / md) if not na(md) and md > 0 else na
    p = ar1(x, al)
    hl = math.log(0.5) / math.log(p) if not na(p) and p > 0 and (p < 1) else na
    sg = (ug + lg) * 0.5 if not na(ug) and (not na(lg)) else na
    dz = math.abs(md - md[n]) / sg if not na(sg) and sg > 1e-10 and (not na(md[n])) else na
    mh = n * 2.0 / os
    mz = 1.0 / os
    rd = bar_index > al + n and (not na(z)) and (not na(hl)) and (not na(dz))
    oo = rd and hl >= 2 and (hl <= mh) and (dz <= mz)
    ok = oo if ou else not na(z)

    hh, ll = request.security(syminfo.tickerid, tf, (high[1], low[1]), lookahead=barmerge.lookahead_on)
    hr = hh - ll
    sr = math.max(hr, syminfo.mintick)
    hm = (hh + ll) * 0.5
    ar = not na(hh) and (not na(ll)) and (hr > 0)
    np = 2.0 * (close - hm) / sr if ar else na
    ef = pe(close, el)
    rw = np * ef if not na(np) else 0.0
    tg = clp(rw, -mt, mt)
    t: PersistentSeries[float] = 0.0
    pt = nz(t[1], 0.0)
    t = ten(pt, tg, bl, rl, mt)
    rg: Series = 1 if t >= rt else -1 if t <= -rt else 0
    ac = bc if rg == 1 else sc if rg == -1 else nc
    bu = rg == 1 and nz(rg[1]) != 1
    be = rg == -1 and nz(rg[1]) != -1
    ne = rg == 0 and nz(rg[1]) != 0

    lx = ta.crossover(z, -im)
    sx = ta.crossunder(z, im)
    lrq = ok and array.get(arm, L) and lx and (z < 0) and (not trn or rg == 1)
    srq = ok and array.get(arm, S) and sx and (z > 0) and (not trn or rg == -1)
    armU(ok, z, lrq, srq)

    mp = plot(md, 'Liquidity Mean', color=color.new(ac, 10), linewidth=2)
    upP = plot(up, 'Upper Band', color=ac, linewidth=1)
    dnP = plot(dn, 'Lower Band', color=ac, linewidth=1)
    uiP = plot(ui, 'Upper Reclaim', color=color.new(ac, 70), linewidth=1)
    liP = plot(li, 'Lower Reclaim', color=color.new(ac, 70), linewidth=1)
    fill(upP, dnP, color=color.new(ac, 90) if sf else na, title='Liquidity Warp Fill')
    pa = ta.ema(ta.atr(14), 200)
    plotshape(low - pa if rs and barstate.isconfirmed and lrq else na, title='Long Reclaim', style=shape.triangleup, location=location.absolute, size=size.tiny, color=lc)
    plotshape(high + pa if rs and barstate.isconfirmed and srq else na, title='Short Reclaim', style=shape.triangledown, location=location.absolute, size=size.tiny, color=rc)
    plotshape(low - pa if rs and barstate.isconfirmed and lrq else na, title='UI Long Reclaim', style=shape.triangleup, location=location.absolute, size=size.small, color=color.new(lc, 80))
    plotshape(high + pa if rs and barstate.isconfirmed and srq else na, title='UI Short Reclaim', style=shape.triangledown, location=location.absolute, size=size.small, color=color.new(rc, 80))
    alertcondition(rs and barstate.isconfirmed and lrq, 'OU Liquidity Long Reclaim', 'Lower liquidity stress extreme reclaimed while OU regime is valid.')
    alertcondition(rs and barstate.isconfirmed and srq, 'OU Liquidity Short Reclaim', 'Upper liquidity stress extreme reclaimed while OU regime is valid.')
    alertcondition(bu, 'Bullish Liquidity Regime', 'Liquidity color engine entered the bullish tension regime.')
    alertcondition(be, 'Bearish Liquidity Regime', 'Liquidity color engine entered the bearish tension regime.')
    alertcondition(ne, 'Neutral Liquidity Regime', 'Liquidity color engine returned to the neutral tension regime.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
