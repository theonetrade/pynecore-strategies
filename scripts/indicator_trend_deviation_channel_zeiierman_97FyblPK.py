"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_float, cast_int
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, box, chart, close, color,
    extend, input, label, line, linefill, location, math, na, plotshape, script, shape, size,
    string, ta, xloc, yloc
)
from pynecore.types import Box, Color, Label, Line, LineFill, NA, Persistent, Series


@udt
class Rail:
    z: float = na(float)
    nm: str = na(str)
    lvl: int = na(int)
    ln: Line = na(Line)


@udt
class Prof:
    v: list[float] = na(list)
    bin: list[int] = na(list)
    bx: list[Box] = na(list)


t1: str = "Price series used to fit the trend model and measure deviation. Close is the default, but other price sources can be selected."
t2: str = "Number of historical bars used to estimate the trend. Higher values create a smoother, slower channel. Lower values react faster to recent price structure."
t3: str = "Base ATR-normalized trend strength required before the center trendline can enter an Up or Down state. Lower values classify trends more easily. Higher values require stronger directional movement."
t4: str = "Trend strength level below which an active Up or Down trend returns to Neutral. Lower values keep established trends active longer and create more hysteresis between entry and exit."
t5: str = "Controls how deviation width is measured. Asymmetric learns separate normal distances above and below trend. Symmetric uses the same deviation width on both sides."
t6: str = "Maximum residual size allowed to influence deviation-width calculations, measured in ATRs. This reduces the effect of isolated shocks or abnormal candles on the entire channel."
t7: str = "Minimum allowed deviation width as a fraction of ATR. Prevents the rails from collapsing too tightly around the trend during extremely low-volatility periods."
t8: str = "Minimum number of historical residuals required on one side of the trend before that side receives its own asymmetric deviation estimate. If there are too few samples, the shared deviation scale is used instead."
t9: str = "Distance of the first deviation rail from the trend baseline. This defines the normal Core region around trend and the point where Stretch begins."
t10: str = "Distance of the second deviation rail from the trend baseline. Crossing this level generates the optional 2D Expansion and Re-entry signals."
t11: str = "Distance of the outer deviation rail from the trend baseline. Crossing this level generates the 3D Expansion and Re-entry events."
t12: str = "Controls how slowly previous deviation stress fades. Higher values retain memory of repeated or persistent movement beyond the first deviation rail for longer. This does not change the rail positions."
t13: str = "Show the +1D, +2D, +3D, 0 TREND, -1D, -2D and -3D labels at the projected end of the trend channel."
t14: str = "Show a live label beside current price displaying its normalized distance from trend and current deviation zone, such as +1.25D STRETCH."
t15: str = "Show confirmed 2D Expansion markers when price closes beyond the upper or lower 2D deviation rail."
t16: str = "Show confirmed 2D Re-entry markers when price closes back inside the upper or lower 2D deviation rail."
t17: str = "Show confirmed 3D Expansion markers when price closes beyond the upper or lower 3D deviation rail. These use larger diamond markers to distinguish extreme displacement."
t18: str = "Show confirmed 3D Re-entry markers when price closes back inside the upper or lower 3D deviation rail. These use larger triangle markers to distinguish extreme re-entry."
t19: str = "Color of the center 0 TREND line when the trend model is classified as bullish."
t20: str = "Color of the center 0 TREND line when the trend model is classified as bearish."
t21: str = "Color of the center 0 TREND line when directional strength is insufficient for an active bullish or bearish trend state."
t22: str = "Color used for positive deviation rails, upper channel zones, upper profile bins and upside deviation events."
t23: str = "Color used for negative deviation rails, lower channel zones, lower profile bins and downside deviation events."
t24: str = "Show the rolling deviation distribution profile outside the projected trend channel. The profile measures how frequently price has occupied different normalized distances from trend."
t25: str = "Number of vertical buckets used to build the deviation profile. More bins provide finer distribution detail but can make the profile noisier. Fewer bins create a smoother distribution."
t26: str = "Maximum positive and negative deviation range displayed by the profile, measured in D units. Observations outside this range are not included in the visible histogram. The range will not be smaller than the outer deviation rail."
t27: str = "Horizontal distance in bars between the projected end of the trend channel and the beginning of the deviation profile."
t28: str = "Maximum horizontal width of the most populated profile bin, measured in bars. All other bins are scaled proportionally to their observation count."
gT: str = "1. Trend Model"
gD: str = "2. Deviation Engine"
gV: str = "3. Visuals"
gS: str = "4. Signal Markers"
gP: str = "5. Deviation Profile"
C: int = 0
U1: int = 1
U2: int = 2
U3: int = 3
D1: int = 4
D2: int = 5
D3: int = 6


@script.indicator("Trend Deviation Channel (Zeiierman)", overlay=True, max_lines_count=50, max_boxes_count=200, max_labels_count=100, max_bars_back=1500)
def main(
    s: Series[float] = input.source(close, "Source", group=gT, tooltip=t1),
    tl=input.int(200, "Trend Length", minval=20, maxval=400, group=gT, tooltip=t2),
    te=input.float(1.0, "Trend Enter Strength", minval=0.1, step=0.1, group=gT, tooltip=t3),
    tx=input.float(0.25, "Trend Exit Strength", minval=0.0, step=0.05, group=gT, tooltip=t4),
    dm=input.string("Asymmetric", "Deviation Shape", options=("Asymmetric", "Symmetric"), group=gD, tooltip=t5),
    cap=input.float(4.0, "Residual Shock Cap (ATR)", minval=1.0, maxval=20.0, step=0.25, group=gD, tooltip=t6),
    mn=input.float(0.05, "Minimum Deviation Width (ATR)", minval=0.01, maxval=1.0, step=0.01, group=gD, tooltip=t7),
    ns=input.int(12, "Minimum One-Side Samples", minval=3, maxval=100, group=gD, tooltip=t8),
    d1i=input.float(1.0, "Deviation 1", minval=0.25, step=0.25, group=gD, tooltip=t9),
    d2i=input.float(2.0, "Deviation 2", minval=0.5, step=0.25, group=gD, tooltip=t10),
    d3i=input.float(3.0, "Deviation 3", minval=0.75, step=0.25, group=gD, tooltip=t11),
    sd=input.float(0.9, "Stretch Memory", minval=0.5, maxval=0.99, step=0.01, group=gD, tooltip=t12),
    slb=input.bool(True, "Show Rail Labels", group=gV, tooltip=t13),
    sbd=input.bool(False, "Show Current Deviation", group=gV, tooltip=t14),
    cu=input.color(color.rgb(18, 209, 235), "Up Trend", group=gV, tooltip=t19),
    cd=input.color(color.rgb(250, 40, 86), "Down Trend", group=gV, tooltip=t20),
    cn=input.color(color.rgb(150, 150, 150), "Neutral Trend", group=gV, tooltip=t21),
    uc=input.color(color.rgb(255, 112, 67), "Upper Deviation", group=gV, tooltip=t22),
    dc=input.color(color.rgb(0, 188, 212), "Lower Deviation", group=gV, tooltip=t23),
    s2e=input.bool(True, "Show 2D Expansion", group=gS, tooltip=t15),
    s2r=input.bool(True, "Show 2D Re-entry", group=gS, tooltip=t16),
    s3e=input.bool(False, "Show 3D Expansion", group=gS, tooltip=t17),
    s3r=input.bool(False, "Show 3D Re-entry", group=gS, tooltip=t18),
    sp=input.bool(True, "Show Deviation Profile", group=gP, tooltip=t24),
    pb=input.int(20, "Bins", minval=11, maxval=61, group=gP, tooltip=t25),
    pr0=input.float(3.1, "Profile Range (D)", minval=1.0, maxval=6.0, step=0.25, group=gP, tooltip=t26),
    pg=input.int(12, "Profile Gap", minval=0, maxval=50, group=gP, tooltip=t27),
    pw=input.int(24, "Profile Max Width", minval=5, maxval=100, group=gP, tooltip=t28)
):
    d1 = math.max(0.25, d1i)
    d2 = math.max(d1 + 0.1, d2i)
    d3 = math.max(d2 + 0.1, d3i)
    pr = math.max(pr0, d3)

    rl: Persistent[list[Rail]] = array.new(0, NA(Rail))
    fl: Persistent[list[LineFill]] = array.new_linefill()
    lb: Persistent[list[Label]] = array.new_label()
    pf: Persistent[Prof] = Prof(array.new_float(), array.new_int(pb, 0), array.new_box())
    tr: Persistent[int] = 0
    st: Persistent[float] = 0.0

    def zPx(c: float, z: float, us: float, ds: float):
        return c + (z * us if z >= 0 else z * ds)

    def rlCol(z: float, tc: Color):
        return uc if z > 0 else dc if z < 0 else tc

    def rlSty(n: int):
        return line.style_dashed if n == 2 else line.style_dotted if n == 3 else line.style_solid

    def rlWid(n: int):
        return 3 if n == 0 else 2 if n == 2 else 1

    def rlTr(n: int):
        return 10 if n == 1 else 0 if n == 2 else 20 if n == 3 else 0

    def zone(z: float):
        return 'CORE' if math.abs(z) < d1 else 'STRETCH' if math.abs(z) < d2 else 'EXTREME' if math.abs(z) < d3 else 'DISLOCATED'

    def trTxt(x: int):
        return 'UP' if x == 1 else 'DOWN' if x == -1 else 'NEUTRAL'

    def clearLb(a: list[Label]):
        while array.size(a) > 0:
            label.delete(array.pop(a))
        return 0

    def hideBx(b: Box, x: int, y: float):
        box.set_left(b, x)
        box.set_right(b, x)
        box.set_top(b, y)
        box.set_bottom(b, y)
        box.set_bgcolor(b, color.new(chart.fg_color, 100))
        box.set_border_color(b, color.new(chart.fg_color, 100))
        return 0

    def addRail(a: list[Rail], z: float, nm: str, lvl: int):
        array.push(a, Rail(z, nm, lvl, line.new(na, na, na, na, xloc=xloc.bar_index, extend=extend.none)))
        return 0

    def initRails(a: list[Rail]):
        addRail(a, 0.0, '0 TREND', 0)
        addRail(a, d1, '+1D', 1)
        addRail(a, d2, '+2D', 2)
        addRail(a, d3, '+3D', 3)
        addRail(a, -d1, '-1D', 1)
        addRail(a, -d2, '-2D', 2)
        addRail(a, -d3, '-3D', 3)
        return 0

    def initFills(a: list[Rail], f: list[LineFill]):
        array.push(f, linefill.new(array.get(a, C).ln, array.get(a, U1).ln, color.new(uc, 96)))
        array.push(f, linefill.new(array.get(a, U1).ln, array.get(a, U2).ln, color.new(uc, 92)))
        array.push(f, linefill.new(array.get(a, U2).ln, array.get(a, U3).ln, color.new(uc, 87)))
        array.push(f, linefill.new(array.get(a, C).ln, array.get(a, D1).ln, color.new(dc, 96)))
        array.push(f, linefill.new(array.get(a, D1).ln, array.get(a, D2).ln, color.new(dc, 92)))
        array.push(f, linefill.new(array.get(a, D2).ln, array.get(a, D3).ln, color.new(dc, 87)))
        return 0

    @method
    def railPaint(r: Rail, x1: int, x2: int, c1: float, c2: float, us: float, ds: float, tc: Color):
        y1 = zPx(c1, r.z, us, ds)
        y2 = zPx(c2, r.z, us, ds)
        col = rlCol(r.z, tc)
        line.set_xy1(r.ln, x1, y1)
        line.set_xy2(r.ln, x2, y2)
        line.set_color(r.ln, col if r.lvl == 0 else color.new(col, rlTr(r.lvl)))
        line.set_width(r.ln, rlWid(r.lvl))
        line.set_style(r.ln, rlSty(r.lvl))
        return 0

    @method
    def railTag(r: Rail, a: list[Label], x: int, c: float, us: float, ds: float, tc: Color, ts: float, ef: float, req: float, tr: int):
        y = zPx(c, r.z, us, ds)
        col = rlCol(r.z, tc)
        tip = 'State: ' + trTxt(tr) + '\nTrend Strength: ' + string.tostring(ts, '#.##') + ' ATR\nRequired Strength: ' + string.tostring(req, '#.##') + ' ATR\nPath Efficiency: ' + string.tostring(ef * 100, '#.0') + '%' if r.lvl == 0 else 'Deviation rail: ' + r.nm
        array.push(a, label.new(x, y, r.nm, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_left, color=color.new(chart.bg_color, 100), textcolor=col, size=size.tiny, tooltip=tip))
        return 0

    def dev(_s: Series[float], len: int, re: float, sl: float, cp: float, minN: int):
        uss: float = 0.0
        dss: float = 0.0
        ass: float = 0.0
        un: int = 0
        dn: int = 0
        an: int = 0

        for i in pine_range(1, len):
            fit = re - sl * (i - 1)
            r = _s[i] - fit

            if not na(r):
                q = math.max(-cp, math.min(cp, r))
                ass += q * q
                an += 1

                if q >= 0:
                    uss += q * q
                    un += 1
                else:
                    dss += q * q
                    dn += 1

        av = math.sqrt(ass / an) if an > 1 else na
        up = math.sqrt(uss / un) if un >= minN else av
        dp = math.sqrt(dss / dn) if dn >= minN else av
        return (up, dp, av)

    def entryReq(ef: float):
        q = 1.0 if 0.18 <= 0 else math.max(0.0, math.min(1.0, ef / 0.18))
        return te * (1.5 - 0.5 * q)

    def nextTrend(x: int, ts: float, req: float):
        out = x

        if x == 0:
            if ts > req:
                out = 1
            elif ts < -req:
                out = -1
        elif x == 1:
            if ts < -req:
                out = -1
            elif ts < tx:
                out = 0
        else:
            if ts > req:
                out = 1
            elif ts > -tx:
                out = 0

        return out

    def drawRails(a: list[Rail], x1: int, x2: int, c1: float, c2: float, us: float, ds: float, tc: Color):
        for i in pine_range(0, array.size(a) - 1):
            method_call(railPaint, array.get(a, i), x1, x2, c1, c2, us, ds, tc)
        return 0

    def drawTags(a: list[Rail], out: list[Label], x: int, c: float, us: float, ds: float, tc: Color, ts: float, ef: float, req: float, tr: int):
        clearLb(out)

        if slb:
            for i in pine_range(0, array.size(a) - 1):
                method_call(railTag, array.get(a, i), out, x, c, us, ds, tc, ts, ef, req, tr)

        return 0

    def badge(a: list[Label], z: float, y: float, st: float, tc: Color):
        if sbd:
            sg0 = '+' if z >= 0 else ''
            bc = uc if z > 0 else dc if z < 0 else tc
            txt = sg0 + string.tostring(z, '#.##') + 'D  ' + zone(z)
            tip = 'Current price deviation from the trend projection. Stretch memory: ' + string.tostring(st, '#.##')
            array.push(a, label.new(bar_index + 1, y, txt, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_left, color=color.new(bc, 78), textcolor=chart.fg_color, size=size.small, tooltip=tip))
        return 0

    @method
    def profAdd(p: Prof, z: float, keep: int):
        if not na(z):
            array.push(p.v, z)

            while array.size(p.v) > keep:
                array.shift(p.v)
        return 0

    @method
    def profPut(p: Prof, z: float):
        if not na(z) and z >= -pr and (z <= pr):
            q = (z + pr) / (2.0 * pr)
            id = cast_int(math.floor(q * pb))
            id = math.max(0, math.min(pb - 1, id))
            array.set(p.bin, id, array.get(p.bin, id) + 1)
        return 0

    @method
    def profEnsure(p: Prof, x: int, y: float):
        while array.size(p.bx) < pb:
            array.push(p.bx, box.new(left=x, top=y, right=x, bottom=y, xloc=xloc.bar_index, bgcolor=color.new(chart.fg_color, 100), border_color=color.new(chart.fg_color, 100)))
        return 0

    @method
    def profBuild(p: Prof, liveZ: float, liveOn: bool):
        array.fill(p.bin, 0)

        if array.size(p.v) > 0:
            __loop_1__ = pine_loop(0)
            while __loop_1__.step(array.size(p.v) - 1):
                i = __loop_1__.value
                profPut(p, array.get(p.v, i))

        if liveOn:
            profPut(p, liveZ)

        return 0

    @method
    def profPaint(p: Prof, liveZ: float, liveOn: bool, x: int, pc: float, us: float, ds: float, tc: Color):
        profEnsure(p, x, pc)
        profBuild(p, liveZ, liveOn)

        mx: int = 0
        for i in pine_range(0, pb - 1):
            mx = math.max(mx, array.get(p.bin, i))

        dz = 2.0 * pr / pb

        for i in pine_range(0, pb - 1):
            b = array.get(p.bx, i)
            n = array.get(p.bin, i)

            if sp and n > 0 and (mx > 0):
                zl = -pr + dz * i
                zh = zl + dz
                zm = (zl + zh) * 0.5

                yl = zPx(pc, zl, us, ds)
                yh = zPx(pc, zh, us, ds)

                w = math.max(1, cast_int(math.round(pw * cast_float(n) / cast_float(mx))))
                c = tc if math.abs(zm) < 0.25 else uc if zm > 0 else dc

                box.set_left(b, x)
                box.set_right(b, x + w)
                box.set_top(b, yh)
                box.set_bottom(b, yl)
                box.set_bgcolor(b, color.new(c, 72))
                box.set_border_color(b, color.new(c, 88))
            else:
                hideBx(b, x, pc)

        return 0

    if barstate.isfirst:
        initRails(rl)
        initFills(rl, fl)

    re = ta.linreg(s[1], tl, 0)
    rp = ta.linreg(s[1], tl, 1)
    sg = re - rp
    at = inline_series(ta.atr(100), 1)

    ok = not na(re) and (not na(sg)) and (not na(at)) and (at > 0)
    cp = at * cap

    ur, dr, ar = dev(s, tl, re, sg, cp, ns)

    f0 = at * mn
    sh = math.max(ar, f0) if ok and (not na(ar)) else na
    us = sh if dm == 'Symmetric' else math.max(ur, f0) if ok and (not na(ur)) else sh
    ds = sh if dm == 'Symmetric' else math.max(dr, f0) if ok and (not na(dr)) else sh

    bs = re + sg if ok else na
    rr = s - bs if ok else na
    z = (rr / us if rr >= 0 else rr / ds) if ok else na

    path = inline_series(ta.sma(math.abs(ta.change(s)), tl - 1), 1) * (tl - 1)
    disp = math.abs(s[1] - s[tl])

    ef = disp / path if ok and path > 0 else 0.0
    ts = sg * (tl - 1) / at if ok else na
    req = entryReq(ef) if ok else na

    if barstate.isconfirmed and ok:
        tr = nextTrend(tr, ts, req)
        st = math.min(3.0, st * sd + math.max(math.abs(z) - d1, 0.0) * (1.0 - sd))
        profAdd(pf, z, tl)

    tc = cu if tr == 1 else cd if tr == -1 else cn

    if barstate.islast and ok:
        x1 = bar_index - tl
        x2 = bar_index + 5
        c1 = re - sg * (tl - 1)
        c2 = bs + sg * 5

        drawRails(rl, x1, x2, c1, c2, us, ds, tc)
        drawTags(rl, lb, x2, c2, us, ds, tc, ts, ef, req, tr)
        badge(lb, z, s, st, tc)

        px = x2 + pg
        pc = bs + sg * (5 + pg)

        profPaint(pf, z, barstate.isrealtime and (not barstate.isconfirmed), px, pc, us, ds, tc)

    xoU = ta.crossover(z, d2)
    xoD = ta.crossunder(z, -d2)
    xiU = ta.crossunder(z, d2)
    xiD = ta.crossover(z, -d2)

    xoU3 = ta.crossover(z, d3)
    xoD3 = ta.crossunder(z, -d3)
    xiU3 = ta.crossunder(z, d3)
    xiD3 = ta.crossover(z, -d3)

    uEx = barstate.isconfirmed and ok and xoU
    dEx = barstate.isconfirmed and ok and xoD
    uIn = barstate.isconfirmed and ok and xiU
    dIn = barstate.isconfirmed and ok and xiD

    uEx3 = barstate.isconfirmed and ok and xoU3
    dEx3 = barstate.isconfirmed and ok and xoD3
    uIn3 = barstate.isconfirmed and ok and xiU3
    dIn3 = barstate.isconfirmed and ok and xiD3

    plotshape(s2e and uEx and (not (s3e and uEx3)), 'Upper 2D Expansion', shape.circle, location.abovebar, uc, size=size.tiny, text='2D', textcolor=color.white)
    plotshape(s2e and dEx and (not (s3e and dEx3)), 'Lower 2D Expansion', shape.circle, location.belowbar, dc, size=size.tiny, text='2D', textcolor=color.white)

    plotshape(s3e and uEx3, 'Upper 3D Expansion', shape.diamond, location.abovebar, uc, size=size.small, text='3D', textcolor=color.white)
    plotshape(s3e and dEx3, 'Lower 3D Expansion', shape.diamond, location.belowbar, dc, size=size.small, text='3D', textcolor=color.white)

    plotshape(s2r and uIn, 'Upper 2D Re-entry', shape.triangledown, location.abovebar, uc, size=size.tiny)
    plotshape(s2r and dIn, 'Lower 2D Re-entry', shape.triangleup, location.belowbar, dc, size=size.tiny)

    plotshape(s3r and uIn3, 'Upper 3D Re-entry', shape.triangledown, location.abovebar, uc, size=size.small, text='3D', textcolor=color.white)
    plotshape(s3r and dIn3, 'Lower 3D Re-entry', shape.triangleup, location.belowbar, dc, size=size.small, text='3D', textcolor=color.white)

    alertcondition(uEx, 'Upper 2D Expansion', 'Price closed beyond the upper 2D trend-deviation rail.')
    alertcondition(dEx, 'Lower 2D Expansion', 'Price closed beyond the lower 2D trend-deviation rail.')
    alertcondition(uIn, 'Upper 2D Re-entry', 'Price closed back inside the upper 2D trend-deviation rail.')
    alertcondition(dIn, 'Lower 2D Re-entry', 'Price closed back inside the lower 2D trend-deviation rail.')

    alertcondition(uEx3, 'Upper 3D Expansion', 'Price closed beyond the upper 3D trend-deviation rail.')
    alertcondition(dEx3, 'Lower 3D Expansion', 'Price closed beyond the lower 3D trend-deviation rail.')
    alertcondition(uIn3, 'Upper 3D Re-entry', 'Price closed back inside the upper 3D trend-deviation rail.')
    alertcondition(dIn3, 'Lower 3D Re-entry', 'Price closed back inside the lower 3D trend-deviation rail.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
