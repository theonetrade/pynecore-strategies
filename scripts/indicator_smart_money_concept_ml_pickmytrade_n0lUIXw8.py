"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_float, cast_int
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barstate, box, chart, close,
    color, high, input, label, line, location, low, math, na, nz, open, order, plotshape, position,
    script, shape, size, string, syminfo, ta, table, text, time, timeframe, xloc
)
from pynecore.types import Box, Color, Label, Line, NA, Persistent, Table


@udt
class Cal:
    x: list[float] = na(list)
    y: list[int] = na(list)
    fixA: bool = False
    a: float = 0.0
    b: float = 1.0
    n: int = 0
    hit: int = 0
    sp: float = 0.0
    bsM: float = 0.0
    bsF: float = 0.0
    bsB: float = 0.0
    cut1: float = 0.7
    cut2: float = 0.9
    n1: float = 0.0
    h1: float = 0.0
    p1: float = 0.0
    n2: float = 0.0
    h2: float = 0.0
    p2: float = 0.0
    n3: float = 0.0
    h3: float = 0.0
    p3: float = 0.0


@udt
class Struct:
    len: int = 10
    hi: float = na(float)
    hiT: int = 0
    hiB: int = 0
    hiOpen: bool = False
    lo: float = na(float)
    loT: int = 0
    loB: int = 0
    loOpen: bool = False
    prevHi: float = na(float)
    prevLo: float = na(float)
    prevHiT: int = 0
    prevLoT: int = 0
    prevHiB: int = 0
    prevLoB: int = 0
    legLo: float = na(float)
    legLoB: int = 0
    legLoT: int = 0
    legHi: float = na(float)
    legHiB: int = 0
    legHiT: int = 0
    trend: int = 0
    newHi: bool = False
    newLo: bool = False
    ev: int = 0
    evChoch: bool = False
    evLvl: float = na(float)
    evLvlT: int = 0
    evProt: float = na(float)
    evProtB: int = 0
    evProtT: int = 0
    evSweep: bool = False


@udt
class Mark:
    t0: int = na(int)
    t1: int = na(int)
    lvl: float = na(float)
    dir: int = na(int)
    choch: bool = na(bool)
    pr: float = na(float)
    ret: int = 0
    tip: str = ""


@udt
class EqMark:
    t0: int = na(int)
    t1: int = na(int)
    lvl: float = na(float)
    side: int = na(int)
    confirmedAt: int = na(int)


@udt
class SwPt:
    t: int = na(int)
    p: float = na(float)
    txt: str = na(str)
    dir: int = na(int)


@udt
class Brk:
    dir: int = na(int)
    lvl: float = na(float)
    en: float = na(float)
    prot: float = na(float)
    r: float = na(float)
    bar0: int = na(int)
    choch: bool = na(bool)
    fvg: bool = na(bool)
    sweep: bool = na(bool)
    p0: float = na(float)
    pm: float = na(float)
    rtDone: bool = False
    ftDone: bool = False
    mk: 'Mark' = _dataclass_field(default_factory=lambda: na(Mark))


@udt
class Drw:
    up: float = na(float)
    dn: float = na(float)
    nUp: bool = na(bool)
    bar0: int = na(int)
    p0: float = na(float)
    pm: float = na(float)


@udt
class Zone:
    dir: int = na(int)
    top: float = na(float)
    bot: float = na(float)
    t0: int = na(int)
    kind: int = na(int)


@udt
class Liq:
    lvl: float = na(float)
    kind: int = na(int)
    tLine: int = na(int)
    tLabel: int = na(int)


@udt
class Trade:
    dir: int = 0
    entry: float = na(float)
    sl0: float = na(float)
    sl: float = na(float)
    tp1: float = na(float)
    tp2: float = na(float)
    bar0: int = 0
    t0: int = 0
    tBE: int = 0
    tEnd: int = 0
    px: float = na(float)
    tp1hit: bool = False
    open: bool = True
    res: str = ""
    how: str = ""


G_STR: str = "Structure"
G_ZON: str = "Zones & Liquidity"
G_AI: str = "Odds Engine"
G_SIG: str = "Signals & Automation"
G_VIS: str = "Display"
G_HIS: str = "Structure History"


@script.indicator("Smart Money Concept ML [PickMyTrade]", "SMC ML", overlay=True, max_boxes_count=50, max_labels_count=500, max_lines_count=500, max_bars_back=500)
def main(
    i_swing=input.int(10, "Swing Length", group=G_STR, minval=3, maxval=50, tooltip="Bars each side that confirm a swing high or low. A swing point is only known this many bars after the bar it marks, so the pivot is back-marked after confirmation. A break then requires a confirmed close through the standing pivot level. Swing breaks drive the odds, the edge test and the signals."),
    i_int=input.int(3, "Internal Length", group=G_STR, minval=2, maxval=10, tooltip="Bars each side for the internal (minor) structure. It forms the equal highs and lows. Internal breaks are display only."),
    show_int=input.bool(True, "Show Internal Structure", group=G_STR, tooltip="Dashed minor-structure BOS and CHoCH. These are display only; swing breaks still drive signals and odds."),
    show_swl=input.bool(False, "Show Swing Labels (HH · HL · LH · LL)", group=G_STR),
    i_history=input.string("Historical", "Structure View", options=("Historical", "Recent"), group=G_HIS, tooltip="Historical rebuilds confirmed events in the visible chart window when you scroll or zoom. Recent keeps the original six swing / twenty internal breaks. History is bounded by the limits below and the bars TradingView has loaded. The dashboard and active zones always describe the latest bar; use Bar Replay for an earlier as-of state."),
    i_hist_sw=input.int(120, "Swing breaks in view", minval=10, maxval=180, group=G_HIS, tooltip="Most recent swing breaks whose confirmation bars are inside the visible window. Zoom into an older period to recover its markings. This changes drawings only."),
    i_hist_in=input.int(160, "Internal breaks in view", minval=10, maxval=180, group=G_HIS, tooltip="Most recent minor-structure breaks in the visible window. Identical simultaneous swing/internal breaks are shown once, as swing structure."),
    i_hist_eq=input.int(40, "Equal-high/low pairs in view", minval=5, maxval=60, group=G_HIS, tooltip="Confirmed EQH/EQL pairs remain as dotted links between their two pivots, including after a sweep. These links mark historical formations, not currently resting liquidity. Confirmation must be inside the visible window."),
    i_label_size=input.string("Small", "Swing label size", options=("Tiny", "Small", "Normal"), group=G_HIS),
    i_label_anchor=input.string("Middle of level", "Break label position", options=("Middle of level", "Break bar"), group=G_HIS, tooltip="Middle of level centres text over the broken level. Break bar places it at the confirming close. In either case the event is known only at that close; line origins refer to earlier pivots."),
    i_latest_odds=input.bool(False, "Retest odds beside latest break", group=G_HIS, tooltip="Adds the fixed at-break odds to the latest swing label. Historical labels otherwise stay short; full details and later retest outcomes remain in tooltips and the dashboard."),
    show_ob=input.bool(True, "Order Blocks", group=G_ZON),
    i_ob_keep=input.int(2, "Order blocks per side", group=G_ZON, minval=1, maxval=10),
    show_fvg=input.bool(False, "Fair Value Gaps", group=G_ZON),
    i_fvg_min=input.float(0.3, "Minimum FVG (ATR)", group=G_ZON, minval=0.0, maxval=3.0, step=0.05, tooltip="Smallest gap counted, in ATR. A gap stays drawn until price trades back through it. Gaps are also used by the edge test whether or not they are drawn."),
    show_eq=input.bool(True, "Equal Highs / Lows", group=G_ZON),
    i_eq_tol=input.float(0.15, "Equal-high/low tolerance (ATR)", group=G_ZON, minval=0.02, maxval=1.0, step=0.01, tooltip="Two internal swing highs (or lows) within this distance, with no trade beyond them in between, form a liquidity pool. Recent view draws the nearest two active pools per side until swept. Historical view retains confirmed pairs as dotted links between their pivots; these links do not imply the liquidity is still resting."),
    show_sw=input.bool(True, "Strong / Weak High & Low", group=G_ZON, tooltip="The current dealing range. The extreme protected by the structure is Strong; the one the structure is pointing at is Weak."),
    show_pd=input.bool(False, "Premium / Discount Zones", group=G_ZON, tooltip="Shades the upper half of the dealing range as premium and the lower half as discount. The table always reports where price sits."),
    show_draw=input.bool(True, "Liquidity Odds", group=G_AI, tooltip="Labels the nearest untaken pool above and below price with the chance that it is traded through before the other one: the random-walk first-touch probability, calibrated on this chart's resolved setups."),
    i_rt_win=input.int(20, "Retest Window (bars)", group=G_AI, minval=3, maxval=200, tooltip="Bars after a swing break in which a return to the broken level counts as a retest. Used by the retest odds and by the Level Retest and Adaptive entries."),
    show_sig=input.bool(True, "Show Buy / Sell Signals", group=G_SIG, tooltip="BUY only from bullish swing structure, SELL only from bearish. Each signal carries its entry, stop and two targets, drawn on the chart and sent in the alert message."),
    i_entry=input.string("Break Close", "Entry", group=G_SIG, options=("Break Close", "Level Retest", "Adaptive"), tooltip="Break Close (default): enter on the close of the break bar. Its signals do not depend on how much history is loaded.\n\nLevel Retest: wait up to the Retest Window for a bar that trades back to the broken level and closes beyond it again; enter on that close. No trade if it does not come, or if the protected swing is closed through first.\n\nAdaptive: Level Retest when the break's retest odds are at or above the threshold below, Break Close otherwise.\n\nThe stop is beyond the protected swing in every mode."),
    i_adapt=input.float(0.8, "Adaptive: wait for the retest at odds ≥", group=G_SIG, minval=0.5, maxval=0.99, step=0.01, tooltip="Adaptive entry only. When a break's calibrated retest odds are at or above this value, wait for a Level Retest; below it, enter on the break close."),
    i_which=input.string("CHoCH + BOS", "Breaks That Signal", group=G_SIG, options=("CHoCH + BOS", "CHoCH only", "BOS only")),
    i_sl_buf=input.float(0.2, "Stop Buffer (ATR x)", group=G_SIG, minval=0.0, maxval=3.0, step=0.05, tooltip="Extra distance beyond the protected swing for the stop, in ATR(14)."),
    i_max_r=input.float(6.0, "Max Risk (ATR x)", group=G_SIG, minval=0.5, maxval=30.0, step=0.5, tooltip="A signal whose stop would sit further than this from entry is skipped."),
    i_tp1=input.float(1.0, "TP1 (R)", group=G_SIG, minval=0.25, maxval=10.0, step=0.25),
    i_tp2=input.float(2.0, "TP2 (R)", group=G_SIG, minval=0.5, maxval=20.0, step=0.25, tooltip="Targets as multiples of the risk (entry to stop). Half the position is scored at TP1, the rest at TP2 or the stop. If TP2 is set below TP1 the two are swapped."),
    i_be=input.bool(True, "Stop to Entry After TP1", group=G_SIG),
    i_tr_life=input.int(150, "Trade Timeout (bars)", group=G_SIG, minval=10, maxval=2000, tooltip="A signal still open after this many bars is closed at that bar's close, and that exit is scored in the Record."),
    i_fmt=input.string("Text", "Alert Message Format", group=G_SIG, options=("Text", "JSON"), tooltip="For automation, create ONE alert with the condition 'Any alert() function call'. Every entry and exit is then sent with side, symbol, timeframe, price, stop and targets."),
    bull_col=input.color(color.new(color.new('#246BFF'), 0), "Bullish Colour", group=G_VIS),
    bear_col=input.color(color.new(color.new('#FF8A18'), 0), "Bearish Colour", group=G_VIS),
    show_table=input.bool(True, "Show Info Table", group=G_VIS),
    i_tbl_pos=input.string("Top Right", "Info Table Position", group=G_VIS, options=("Top Right", "Bottom Right", "Top Left", "Bottom Left")),
    show_heading=input.bool(False, "Publication heading and key", group=G_VIS, tooltip="Adds a viewport-anchored heading and compact key. For a clean publication cover, hide the info table separately. Does not change calculations or alerts."),
    zen_mode=input.bool(False, "Zen Mode", group=G_VIS, tooltip="Hides labels and the table. Structure lines, zones and signal levels remain.")
):
    hist_view: bool = i_history == 'Historical'
    def f_inView(eventTime: int):
        return eventTime >= chart.left_visible_bar_time and eventTime <= chart.right_visible_bar_time

    def f_markTime(firstTime: int, breakTime: int):
        return breakTime if i_label_anchor == 'Break bar' else cast_int(math.round((cast_float(firstTime) + cast_float(breakTime)) / 2.0))

    swing_text_size: str = size.normal if i_label_size == 'Normal' else size.small if i_label_size == 'Small' else size.tiny

    TP1R: float = math.min(i_tp1, i_tp2)
    TP2R: float = math.max(i_tp1, i_tp2)

    CAL_CAP: int = 500
    CAL_LAMBDA: float = 50.0
    CAL_MIN: int = 30
    FT_WIN: int = 150
    DRAW_WIN: int = 1000
    Z_BONF: float = 2.39
    MARKS_KEEP: int = 6
    OB_MAX_ATR: float = 3.0
    LBL_GAP: float = 0.45

    atr: float = ta.atr(14)
    sd1: float = ta.stdev(ta.change(close), 100)
    confirmed: bool = barstate.isconfirmed
    atrOk: bool = not na(atr) and atr > 0
    bar_ms: int = math.max(nz(timeframe.in_seconds(timeframe.period), 60), 1) * 1000
    ph_sw: float = ta.pivothigh(high, i_swing, i_swing)
    pl_sw: float = ta.pivotlow(low, i_swing, i_swing)
    ph_in: float = ta.pivothigh(high, i_int, i_int)
    pl_in: float = ta.pivotlow(low, i_int, i_int)

    fvgBull: bool = atrOk and low > high[2] and (close[1] > high[2]) and (low - high[2] >= i_fvg_min * atr)
    fvgBear: bool = atrOk and high < low[2] and (close[1] < low[2]) and (low[2] - high >= i_fvg_min * atr)
    lastFvgBullBar: int = ta.valuewhen(fvgBull, bar_index, 0)
    lastFvgBearBar: int = ta.valuewhen(fvgBear, bar_index, 0)

    def f_role(dir: int):
        return bull_col if dir == 1 else bear_col

    def f_px(p: float):
        return '—' if na(p) else string.tostring(math.round_to_mintick(p))

    def f_pct(v: float):
        return '—' if na(v) else string.tostring(math.round(v * 100)) + '%'

    def f_sgn(v: float, fmt: str):
        return '—' if na(v) else ('+' if v >= 0 else '−') + string.tostring(math.abs(v), fmt)

    def f_phi(x: float):
        z: float = math.abs(x)
        t: float = 1.0 / (1.0 + 0.2316419 * z)
        d: float = 0.3989422804014327 * math.exp(-0.5 * z * z)
        p: float = 1.0 - d * t * (0.31938153 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
        return p if x >= 0 else 1.0 - p

    def f_clampP(p: float):
        return math.max(0.005, math.min(0.995, p))

    def f_logit(p: float):
        q: float = f_clampP(p)
        return math.log(q / (1.0 - q))

    def f_touch(d: float, sd: float, w: int):
        return na if na(sd) or sd <= 0 or na(d) else f_clampP(2.0 * (1.0 - f_phi(d / (sd * math.sqrt(w)))))


    c_rt: Persistent[Cal] = Cal(array.new_float(), array.new_int(), cut1=0.7, cut2=0.9)
    c_dr: Persistent[Cal] = Cal(array.new_float(), array.new_int(), True, cut1=0.65, cut2=0.8)

    def f_calP(c: Cal, p0: float):
        return na if na(p0) else 1.0 / (1.0 + math.exp(-(c.a + c.b * f_logit(p0))))

    def f_calFit(c: Cal):
        n: int = array.size(c.x)
        if n > 0:
            a: float = c.a
            b: float = c.b
            for iter in pine_range(0, 3):
                ga: float = CAL_LAMBDA * a
                gb: float = CAL_LAMBDA * (b - 1.0)
                haa: float = CAL_LAMBDA
                hab: float = 0.0
                hbb: float = CAL_LAMBDA
                for i in pine_range(0, n - 1):
                    x: float = array.get(c.x, i)
                    p: float = 1.0 / (1.0 + math.exp(-(a + b * x)))
                    e: float = p - array.get(c.y, i)
                    w: float = p * (1.0 - p)
                    ga += e
                    gb += e * x
                    haa += w
                    hab += w * x
                    hbb += w * x * x
                det: float = haa * hbb - hab * hab
                if c.fixA:
                    b -= gb / hbb
                elif det > 0:
                    a -= (hbb * ga - hab * gb) / det
                    b -= (haa * gb - hab * ga) / det
            c.a = a
            c.b = b
        return True

    def f_calScore(c: Cal, pm: float, p0: float, y: int):
        base: float = cast_float(c.hit) / c.n if c.n > 0 else 0.5
        c.bsB += math.pow(base - y, 2)
        c.bsM += math.pow(pm - y, 2)
        c.bsF += math.pow(p0 - y, 2)
        c.sp += pm
        c.n += 1
        c.hit += y
        if pm < c.cut1:
            c.n1 += 1
            c.h1 += y
            c.p1 += pm
        elif pm < c.cut2:
            c.n2 += 1
            c.h2 += y
            c.p2 += pm
        else:
            c.n3 += 1
            c.h3 += y
            c.p3 += pm
        array.push(c.x, f_logit(p0))
        array.push(c.y, y)
        if array.size(c.x) > CAL_CAP:
            array.shift(c.x)
            array.shift(c.y)
        return f_calFit(c)

    def f_bandOk(n: float, h: float, p: float, z: float):
        ok: bool = True
        if n >= 20:
            pr: float = p / n
            ok = math.abs(pr - h / n) <= z * math.sqrt(math.max(pr * (1.0 - pr), 0.0025) / n)
        return ok

    def f_calOk(c: Cal):
        ok: bool = False
        if c.n >= CAL_MIN:
            ok = f_bandOk(c.n, c.hit, c.sp, 1.96) and f_bandOk(c.n1, c.h1, c.p1, 2.39) and f_bandOk(c.n2, c.h2, c.p2, 2.39) and f_bandOk(c.n3, c.h3, c.p3, 2.39)
        return ok

    def f_calText(c: Cal):
        s: str = "—"
        if c.n > 0:
            s = string.tostring(math.round(c.sp / c.n * 100)) + '→' + f_pct(cast_float(c.hit) / c.n) + ((' ✓' if f_calOk(c) else ' ✗') if c.n >= CAL_MIN else ' (n ' + string.tostring(c.n) + ')')
        return s

    def f_band(lbl: str, n: float, h: float, p: float):
        return lbl + ' said ' + string.tostring(math.round(p / n * 100)) + ' → ' + f_pct(h / n) + ' (n ' + string.tostring(n, '#') + ')' if n > 0 else lbl + ' —'

    def f_bands(c: Cal):
        a: str = string.tostring(math.round(c.cut1 * 100))
        b: str = string.tostring(math.round(c.cut2 * 100))
        return f_band('under ' + a + '%:', c.n1, c.h1, c.p1) + '\n   ' + f_band(a + '–' + b + '%:', c.n2, c.h2, c.p2) + '\n   ' + f_band(b + '%+:', c.n3, c.h3, c.p3)

    def f_skill(bs: float, ref: float):
        return f_sgn(1.0 - bs / ref, '0.000') if ref > 0 else '—'


    def f_step(s: Struct, ph: float, pl: float):
        s.ev = 0
        s.newHi = False
        s.newLo = False
        if not na(s.legLo) and low < s.legLo:
            s.legLo = low
            s.legLoB = bar_index
            s.legLoT = time
        if not na(s.legHi) and high > s.legHi:
            s.legHi = high
            s.legHiB = bar_index
            s.legHiT = time

        if s.hiOpen and close > s.hi:
            s.ev = 1
            s.evChoch = s.trend == -1
            s.trend = 1
            s.evLvl = s.hi
            s.evLvlT = s.hiT
            s.evProt = low if na(s.legLo) else s.legLo
            s.evProtB = bar_index if na(s.legLo) else s.legLoB
            s.evProtT = time if na(s.legLo) else s.legLoT

            rf: float = s.lo if s.loB < s.evProtB else s.prevLo if s.prevLoB < s.evProtB else na
            s.evSweep = not na(rf) and s.evProt < rf
            s.hiOpen = False
        elif s.loOpen and close < s.lo:
            s.ev = -1
            s.evChoch = s.trend == 1
            s.trend = -1
            s.evLvl = s.lo
            s.evLvlT = s.loT
            s.evProt = high if na(s.legHi) else s.legHi
            s.evProtB = bar_index if na(s.legHi) else s.legHiB
            s.evProtT = time if na(s.legHi) else s.legHiT
            rf: float = s.hi if s.hiB < s.evProtB else s.prevHi if s.prevHiB < s.evProtB else na
            s.evSweep = not na(rf) and s.evProt > rf
            s.loOpen = False
        if not na(ph):
            s.prevHi = s.hi
            s.prevHiT = s.hiT
            s.prevHiB = s.hiB
            s.hi = ph
            s.hiT = time[s.len]
            s.hiB = bar_index - s.len
            s.hiOpen = True
            s.newHi = True

            m: float = low
            mb: int = 0
            __loop_1__ = pine_loop(0)
            while __loop_1__.step(s.len - 1):
                k = __loop_1__.value
                if low[k] < m:
                    m = low[k]
                    mb = k
            s.legLo = m
            s.legLoB = bar_index - mb
            s.legLoT = time[mb]
        if not na(pl):
            s.prevLo = s.lo
            s.prevLoT = s.loT
            s.prevLoB = s.loB
            s.lo = pl
            s.loT = time[s.len]
            s.loB = bar_index - s.len
            s.loOpen = True
            s.newLo = True
            m: float = high
            mb: int = 0
            __loop_1__ = pine_loop(0)
            while __loop_1__.step(s.len - 1):
                k = __loop_1__.value
                if high[k] > m:
                    m = high[k]
                    mb = k
            s.legHi = m
            s.legHiB = bar_index - mb
            s.legHiT = time[mb]
        return s

    sw: Persistent[Struct] = Struct(i_swing)
    it: Persistent[Struct] = Struct(i_int)

    if confirmed:
        f_step(sw, ph_sw, pl_sw)
        f_step(it, ph_in, pl_in)

    rng_hi: float = sw.hi if na(sw.legHi) else sw.legHi if na(sw.hi) else math.max(sw.hi, sw.legHi)
    rng_lo: float = sw.lo if na(sw.legLo) else sw.legLo if na(sw.lo) else math.min(sw.lo, sw.legLo)
    rng_pos: float = na if na(rng_hi) or na(rng_lo) or rng_hi <= rng_lo else (close - rng_lo) / (rng_hi - rng_lo)

    swMarks: Persistent[list[Mark]] = array.new(0, NA(Mark))
    inMarks: Persistent[list[Mark]] = array.new(0, NA(Mark))
    swHistory: Persistent[list[Mark]] = array.new(0, NA(Mark))

    eqHistory: Persistent[list[EqMark]] = array.new(0, NA(EqMark))
    def f_eqHistory(t0: int, t1: int, lvl: float, side: int):
        if hist_view and show_eq and f_inView(time):
            array.push(eqHistory, EqMark(t0, t1, lvl, side, time))
            while array.size(eqHistory) > i_hist_eq:
                array.shift(eqHistory)
        return True


    swPts: Persistent[list[SwPt]] = array.new(0, NA(SwPt))

    pend: Persistent[list[Brk]] = array.new(0, NA(Brk))

    d_pend: Persistent[list[Drw]] = array.new(0, NA(Drw))

    zones: Persistent[list[Zone]] = array.new(0, NA(Zone))

    liqUp: Persistent[list[Liq]] = array.new(0, NA(Liq))
    liqDn: Persistent[list[Liq]] = array.new(0, NA(Liq))

    et: Persistent[list[int]] = array.new_int(12, 0)

    def f_etAdd(k: int, y: int):
        array.set(et, k, array.get(et, k) + 1)
        array.set(et, k + 1, array.get(et, k + 1) + y)
        return True

    def f_z(n1: int, w1: int, n2: int, w2: int):
        z: float = na(float)
        if n1 >= 10 and n2 >= 10:
            p: float = cast_float(w1 + w2) / (n1 + n2)
            se: float = math.sqrt(p * (1.0 - p) * (1.0 / n1 + 1.0 / n2))
            z = (cast_float(w1) / n1 - cast_float(w2) / n2) / se if se > 0 else 0.0
        return z


    trades: Persistent[list[Trade]] = array.new(0, NA(Trade))

    rec: Persistent[list[float]] = array.from_items(0.0, 0.0, 0.0, 0.0, 0.0)

    def f_openDir():
        d: int = 0
        if array.size(trades) > 0:
            t: Trade = array.get(trades, array.size(trades) - 1)
            if t.open:
                d = t.dir
        return d

    def f_msg(kind: str, t: Trade, px: float):
        side: str = 'buy' if t.dir == 1 else 'sell'
        pos: str = 'long' if t.dir == 1 else 'short'
        act: str = side if kind == 'entry' else 'partial_close' if kind == 'tp1' else 'close'
        return '{"source":"SMC ML","event":"' + kind + '","action":"' + act + '","position":"' + pos + '","side":"' + side + '","symbol":"' + syminfo.ticker + '","timeframe":"' + timeframe.period + '","price":' + f_px(px) + ',"entry":' + f_px(t.entry) + ',"sl":' + f_px(t.sl) + ',"tp1":' + f_px(t.tp1) + ',"tp2":' + f_px(t.tp2) + '}' if i_fmt == 'JSON' else 'SMC ML: ' + string.upper(side) + ' ' + syminfo.ticker + ' @ ' + f_px(px) + '  |  SL ' + f_px(t.sl) + '  |  TP1 ' + f_px(t.tp1) + '  |  TP2 ' + f_px(t.tp2) if kind == 'entry' else 'SMC ML: ' + syminfo.ticker + ' ' + string.upper(pos) + ' ' + string.upper(kind) + ' @ ' + f_px(px) + ('  |  SL now ' + f_px(t.sl) if kind == 'tp1' else '')

    def f_R(t: Trade, px: float):
        rk: float = math.abs(t.entry - t.sl0)
        m: float = t.dir * (px - t.entry) / rk if rk > 0 else 0.0
        return 0.5 * TP1R + 0.5 * m if t.tp1hit else m

    def f_close(t: Trade, res: str, px: float):
        t.open = False
        t.res = res
        t.tEnd = time
        t.px = px
        R: float = f_R(t, px)
        array.set(rec, 0, array.get(rec, 0) + 1)
        array.set(rec, 1, array.get(rec, 1) + (1 if t.tp1hit else 0))
        array.set(rec, 2, array.get(rec, 2) + (1 if res == 'SL' else 0))
        array.set(rec, 3, array.get(rec, 3) + R)
        array.set(rec, 4, array.get(rec, 4) + R * R)
        while array.size(trades) > 1:
            array.shift(trades)
        return True

    def f_addZone(z: Zone):
        hit: int = -1
        if array.size(zones) > 0:
            for i in pine_range(0, array.size(zones) - 1):
                e: Zone = array.get(zones, i)
                fits: bool = z.kind == 1 or na(atr) or math.max(e.top, z.top) - math.min(e.bot, z.bot) <= OB_MAX_ATR * atr
                if hit < 0 and e.kind == z.kind and (e.dir == z.dir) and (z.bot <= e.top) and (z.top >= e.bot) and fits:
                    hit = i
        if hit >= 0:
            e: Zone = array.remove(zones, hit)
            e.top = math.max(e.top, z.top)
            e.bot = math.min(e.bot, z.bot)
            e.t0 = math.min(e.t0, z.t0)
            array.push(zones, e)
        else:
            array.push(zones, z)
        return True

    def f_capZones(kind: int, dir: int, keep: int):
        n: int = 0
        if array.size(zones) > 0:
            for i in pine_range(array.size(zones) - 1, 0):
                z: Zone = array.get(zones, i)
                if z.kind == kind and z.dir == dir:
                    n += 1
                    if n > keep:
                        array.remove(zones, i)
        return True

    def f_addLiq(a: list[Liq], side: int, lvl: float, kind: int, tLine: int, tLabel: int):
        pos: int = array.size(a)
        if array.size(a) > 0:
            for i in pine_range(0, array.size(a) - 1):
                v: float = array.get(a, i).lvl
                if lvl < v if side == 1 else lvl > v:
                    pos = i
                    break
        array.insert(a, pos, Liq(lvl, kind, tLine, tLabel))
        while array.size(a) > 20:
            array.pop(a)
        return True

    def f_sweep(a: list[Liq], side: int):
        eq: bool = False
        more: bool = array.size(a) > 0
        while more:
            l: Liq = array.get(a, 0)
            if high > l.lvl if side == 1 else low < l.lvl:
                eq = eq or l.kind == 1
                array.shift(a)
                more = array.size(a) > 0
            else:
                more = False
        return eq

    def f_eqClean(side: int, lv: float, fromB: int):
        span: int = math.min(bar_index - fromB - 1, 299)
        ok: bool = bar_index - fromB <= 300
        if ok and span >= 0:
            for k in pine_range(0, span):
                if high[k] > lv if side == 1 else low[k] < lv:
                    ok = False
                    break
        return ok

    def f_ring(a: list[Mark], m: Mark, cap: int):
        array.push(a, m)
        while array.size(a) > cap:
            array.shift(a)
        return True

    ev_bchoch: bool = False
    ev_schoch: bool = False
    ev_bbos: bool = False
    ev_sbos: bool = False
    ev_buy: bool = False
    ev_sell: bool = False
    ev_exit: bool = False
    ev_sweep: bool = False
    al_exit: str = ""
    al_entry: str = ""

    rt_dir: Persistent[int] = 0
    rt_bar: Persistent[int] = 0
    rt_lvl: Persistent[float] = na(float)
    rt_prot: Persistent[float] = na(float)
    rt_p: Persistent[float] = na(float)

    if confirmed and array.size(trades) > 0:
        t: Trade = array.get(trades, array.size(trades) - 1)
        if t.open and bar_index > t.bar0:
            L: bool = t.dir == 1
            hitSL: bool = low <= t.sl if L else high >= t.sl
            hitT2: bool = high >= t.tp2 if L else low <= t.tp2
            hitT1: bool = not t.tp1hit and (high >= t.tp1 if L else low <= t.tp1)
            if hitSL:
                how: str = 'SL' if not t.tp1hit else 'TP1, then stop at entry' if t.tBE > 0 else 'TP1, then SL'

                slPx: float = math.min(open, t.sl) if L else math.max(open, t.sl)
                f_close(t, how, slPx)
                ev_exit = True
                al_exit = f_msg('stop at entry' if t.tBE > 0 else 'sl', t, slPx)
            elif hitT2:
                t2Px: float = math.max(open, t.tp2) if L else math.min(open, t.tp2)
                t.tp1hit = True
                f_close(t, 'TP2', t2Px)
                ev_exit = True
                al_exit = f_msg('tp2', t, t2Px)
            else:
                if hitT1:
                    t.tp1hit = True
                    if i_be:
                        t.sl = t.entry
                        t.tBE = time
                    al_exit = f_msg('tp1', t, t.tp1)
                if bar_index - t.bar0 >= i_tr_life:
                    f_close(t, 'timeout', close)
                    ev_exit = True
                    al_exit = f_msg('timeout', t, close)

    if confirmed and array.size(pend) > 0:
        for i in pine_range(array.size(pend) - 1, 0):
            b: Brk = array.get(pend, i)
            if bar_index > b.bar0:
                L: bool = b.dir == 1
                if not b.rtDone:
                    touch: bool = low <= b.lvl if L else high >= b.lvl
                    if touch or bar_index - b.bar0 >= i_rt_win:
                        b.rtDone = True
                        b.mk.ret = 1 if touch else -1
                        if not na(b.p0):
                            f_calScore(c_rt, b.pm, b.p0, 1 if touch else 0)
                if not b.ftDone:
                    fail: bool = close < b.prot if L else close > b.prot
                    win: bool = close >= b.en + b.r if L else close <= b.en - b.r
                    if fail or win or bar_index - b.bar0 >= FT_WIN:
                        b.ftDone = True
                        if fail or win:
                            y: int = 0 if fail else 1
                            f_etAdd(2 if b.choch else 0, y)
                            f_etAdd(4 if b.fvg else 6, y)
                            f_etAdd(8 if b.sweep else 10, y)
                if b.rtDone and b.ftDone:
                    array.remove(pend, i)

    if confirmed and array.size(d_pend) > 0:
        for i in pine_range(array.size(d_pend) - 1, 0):
            w: Drw = array.get(d_pend, i)
            if bar_index > w.bar0:
                hu: bool = high > w.up
                hd: bool = low < w.dn
                if hu or hd or bar_index - w.bar0 >= DRAW_WIN:
                    if hu != hd:
                        f_calScore(c_dr, w.pm, w.p0, 1 if hu == w.nUp else 0)
                    array.remove(d_pend, i)

    if confirmed and array.size(zones) > 0:
        for i in pine_range(array.size(zones) - 1, 0):
            z: Zone = array.get(zones, i)
            gone: bool = (close < z.bot if z.dir == 1 else close > z.top) if z.kind == 0 else low <= z.bot if z.dir == 1 else high >= z.top
            if gone:
                array.remove(zones, i)

    if confirmed and show_fvg and (fvgBull or fvgBear):
        d: int = 1 if fvgBull else -1
        f_addZone(Zone(d, low if fvgBull else low[2], high[2] if fvgBull else high, time[2], 1))
        f_capZones(1, d, 4)

    if confirmed:
        sU: bool = f_sweep(liqUp, 1)
        sD: bool = f_sweep(liqDn, -1)
        ev_sweep = sU or sD

    if confirmed and atrOk:
        if sw.newHi:
            f_addLiq(liqUp, 1, sw.hi, 0, sw.hiT, sw.hiT)
        if sw.newLo:
            f_addLiq(liqDn, -1, sw.lo, 0, sw.loT, sw.loT)
        if it.newHi and (not na(it.prevHi)) and (math.abs(it.hi - it.prevHi) <= i_eq_tol * atr):
            lv: float = math.max(it.hi, it.prevHi)
            if f_eqClean(1, lv, it.prevHiB):
                f_addLiq(liqUp, 1, lv, 1, it.prevHiT, it.hiT)
                f_eqHistory(it.prevHiT, it.hiT, lv, 1)
        if it.newLo and (not na(it.prevLo)) and (math.abs(it.lo - it.prevLo) <= i_eq_tol * atr):
            lv: float = math.min(it.lo, it.prevLo)
            if f_eqClean(-1, lv, it.prevLoB):
                f_addLiq(liqDn, -1, lv, 1, it.prevLoT, it.loT)
                f_eqHistory(it.prevLoT, it.loT, lv, -1)

    if confirmed and show_swl and (not hist_view or f_inView(time)):
        if sw.newHi:
            array.push(swPts, SwPt(sw.hiT, sw.hi, 'H' if na(sw.prevHi) else 'HH' if sw.hi > sw.prevHi else 'LH', 1))
        if sw.newLo:
            array.push(swPts, SwPt(sw.loT, sw.lo, 'L' if na(sw.prevLo) else 'LL' if sw.lo < sw.prevLo else 'HL', -1))
        while array.size(swPts) > (40 if hist_view else 30):
            array.shift(swPts)

    if confirmed and show_int and (it.ev != 0) and (not (sw.ev == it.ev and sw.evLvl == it.evLvl)) and (not hist_view or f_inView(time)):
        f_ring(inMarks, Mark(it.evLvlT, time, it.evLvl, it.ev, it.evChoch, na), i_hist_in if hist_view else 20)

    sg_dir: int = 0
    sg_en: float = na(float)
    sg_sl: float = na(float)
    sg_how: str = ""

    if confirmed and atrOk and (sw.ev != 0):
        d: int = sw.ev
        L: bool = d == 1
        r: float = math.abs(close - sw.evProt)
        p0: float = f_touch(math.abs(close - sw.evLvl), sd1, i_rt_win)
        pm: float = f_calP(c_rt, p0)
        fb: int = lastFvgBullBar if L else lastFvgBearBar
        hasFvg: bool = not na(fb) and fb >= sw.evProtB
        if sw.evChoch:
            ev_bchoch = L
            ev_schoch = not L
        else:
            ev_bbos = L
            ev_sbos = not L

        tag: str = 'CHoCH' if sw.evChoch else 'BOS'
        tip: str = tag + (' up' if L else ' down') + ' · closed at ' + f_px(close) + ' through ' + f_px(sw.evLvl) + '\nProtected swing ' + f_px(sw.evProt) + '\n\n' + ('Retest odds: not enough bars yet to measure volatility.' if na(pm) else 'Retest odds ' + f_pct(pm) + ': the chance price trades back to ' + f_px(sw.evLvl) + ' within ' + string.tostring(i_rt_win) + ' bars. Random-walk formula for this distance and volatility: ' + f_pct(p0) + ', calibrated on ' + string.tostring(c_rt.n) + ' resolved breaks on this chart.')
        mk: Mark = Mark(sw.evLvlT, time, sw.evLvl, d, sw.evChoch, pm, 0, tip)
        f_ring(swMarks, mk, MARKS_KEEP)
        if hist_view and f_inView(time):
            f_ring(swHistory, mk, i_hist_sw)
        if r > 0:
            array.push(pend, Brk(d, sw.evLvl, close, sw.evProt, r, bar_index, sw.evChoch, hasFvg, sw.evSweep, p0, pm, False, False, mk))

        up: float = array.get(liqUp, 0).lvl if array.size(liqUp) > 0 else na
        dn: float = array.get(liqDn, 0).lvl if array.size(liqDn) > 0 else na
        if not na(up) and (not na(dn)) and (up > close) and (close > dn) and (not na(sd1)) and (sd1 > 0):
            dU: float = up - close
            dD: float = close - dn

            if dU + dD <= sd1 * math.sqrt(DRAW_WIN):
                nUp: bool = dU <= dD
                q0: float = f_clampP((dD if nUp else dU) / (dU + dD))
                array.push(d_pend, Drw(up, dn, nUp, bar_index, q0, f_calP(c_dr, q0)))

        back: int = math.min(math.max(bar_index - sw.evProtB, 0), 400)
        ob: int = back
        for k in pine_range(back, back + 3):
            if close[k] < open[k] if L else close[k] > open[k]:
                ob = k
                break
        if show_ob and high[ob] - low[ob] <= OB_MAX_ATR * atr:
            f_addZone(Zone(d, high[ob], low[ob], time[ob], 0))
            f_capZones(0, d, i_ob_keep)

        if d != rt_dir:
            rt_dir = 0
        which: bool = i_which == 'CHoCH + BOS' or (i_which == 'CHoCH only' and sw.evChoch) or (i_which == 'BOS only' and (not sw.evChoch))
        wait: bool = i_entry == 'Level Retest' or (i_entry == 'Adaptive' and (not na(pm)) and (pm >= i_adapt))
        slB: float = sw.evProt - i_sl_buf * atr if L else sw.evProt + i_sl_buf * atr
        if which:
            if wait:
                rt_dir = d
                rt_bar = bar_index
                rt_lvl = sw.evLvl
                rt_prot = sw.evProt
                rt_p = pm
            else:
                rt_dir = 0
                if f_openDir() != d and math.abs(close - slB) <= i_max_r * atr and (math.abs(close - slB) > 0):
                    sg_dir = d
                    sg_en = close
                    sg_sl = slB
                    sg_how = "break close"

    if confirmed and atrOk and (rt_dir != 0) and (bar_index > rt_bar) and (sg_dir == 0):
        L: bool = rt_dir == 1
        if bar_index - rt_bar > i_rt_win or (close < rt_prot if L else close > rt_prot):
            rt_dir = 0
        elif (low <= rt_lvl and close > rt_lvl if L else high >= rt_lvl and close < rt_lvl) and f_openDir() != rt_dir:
            slR: float = rt_prot - i_sl_buf * atr if L else rt_prot + i_sl_buf * atr
            if math.abs(close - slR) <= i_max_r * atr and math.abs(close - slR) > 0:
                sg_dir = rt_dir
                sg_en = close
                sg_sl = slR
                sg_how = "level retest"
            rt_dir = 0

    if confirmed and sg_dir != 0:
        od: int = f_openDir()
        if od != 0 and od != sg_dir:
            o: Trade = array.get(trades, array.size(trades) - 1)
            f_close(o, 'reversed', close)
            ev_exit = True
            al_exit = f_msg('reversed', o, close)
        R: float = math.abs(sg_en - sg_sl)
        nt: Trade = Trade(sg_dir, sg_en, sg_sl, sg_sl, sg_en + sg_dir * TP1R * R, sg_en + sg_dir * TP2R * R, bar_index, time)
        nt.how = sg_how
        array.push(trades, nt)
        ev_buy = sg_dir == 1
        ev_sell = sg_dir == -1
        al_entry = f_msg('entry', nt, sg_en)

    if al_exit != '':
        alert(al_exit, alert.freq_all)
    if al_entry != '':
        alert(al_entry, alert.freq_all)

    def f_liqIdx(a: list[Liq], side: int):
        idx: int = -1
        if array.size(a) > 0:
            for i in pine_range(0, array.size(a) - 1):
                lv: float = array.get(a, i).lvl
                if high <= lv if side == 1 else low >= lv:
                    idx = i
                    break
        return idx

    def f_liveDraw():
        iU: int = f_liqIdx(liqUp, 1)
        iD: int = f_liqIdx(liqDn, -1)
        up: float = array.get(liqUp, iU).lvl if iU >= 0 else na
        dn: float = array.get(liqDn, iD).lvl if iD >= 0 else na
        pUp: float = na(float)
        q0: float = na(float)
        if not na(up) and (not na(dn)) and (up > close) and (close > dn):
            dU: float = up - close
            dD: float = close - dn
            nUp: bool = dU <= dD
            q0 = f_clampP((dD if nUp else dU) / (dU + dD))
            pm: float = f_calP(c_dr, q0)
            pUp = pm if nUp else 1.0 - pm
            q0 = q0 if nUp else 1.0 - q0
        return (up, dn, pUp, q0)

    g_ln: Persistent[list[Line]] = array.new_line()
    g_lb: Persistent[list[Label]] = array.new_label()
    g_bx: Persistent[list[Box]] = array.new_box()

    def f_L(l: Line):
        array.push(g_ln, l)
        return l

    def f_B(b: Label):
        array.push(g_lb, b)
        return b

    q_p: Persistent[list[float]] = array.new_float()
    q_t: Persistent[list[str]] = array.new_string()
    q_c: Persistent[list[Color]] = array.new_color()
    q_x: Persistent[list[str]] = array.new_string()

    def f_q(p: float, txt: str, c: Color, tip: str):
        if not na(p):
            array.push(q_p, p)
            array.push(q_t, txt)
            array.push(q_c, c)
            array.push(q_x, tip)
        return True

    def f_qFlush(t: int):
        n: int = array.size(q_p)
        if n > 0:
            ix: list[int] = array.sort_indices(q_p, order.descending)
            gp: float = na(float)
            gt: str = ""
            gx: str = ""
            gc: Color = na(Color)
            for k in pine_range(0, n):
                last: bool = k == n
                i: int = -1 if last else array.get(ix, k)
                p: float = na if last else array.get(q_p, i)
                join: bool = not last and (not na(gp)) and (math.abs(gp - p) <= LBL_GAP * atr)
                if join:
                    gt = gt + '  ·  ' + array.get(q_t, i)
                    gx = gx + ('' if array.get(q_x, i) == '' else ('' if gx == '' else '\n\n') + array.get(q_x, i))
                else:
                    if not na(gp):
                        f_B(label.new(t, gp, gt, xloc=xloc.bar_time, style=label.style_label_left, color=color.new(gc, 88), textcolor=gc, size=size.small, tooltip=gx))
                    if not last:
                        gp = p
                        gt = array.get(q_t, i)
                        gx = array.get(q_x, i)
                        gc = array.get(q_c, i)
        array.clear(q_p)
        array.clear(q_t)
        array.clear(q_c)
        array.clear(q_x)
        return True

    if barstate.islast:
        while array.size(g_ln) > 0:
            line.delete(array.pop(g_ln))
        while array.size(g_lb) > 0:
            label.delete(array.pop(g_lb))
        while array.size(g_bx) > 0:
            box.delete(array.pop(g_bx))

        tR: int = time + 2 * bar_ms

        for z in zones:
            c: Color = f_role(z.dir)
            array.push(g_bx, box.new(z.t0, z.top, tR, z.bot, xloc=xloc.bar_time, border_color=color.new(c, 100) if z.kind == 1 else color.new(c, 50), bgcolor=color.new(c, 88 if z.kind == 1 else 85), text='FVG' if z.kind == 1 else 'OB', text_color=color.new(c, 30), text_size=size.tiny, text_halign=text.align_right if z.kind == 1 else text.align_left))

        if show_eq and hist_view:
            for e in eqHistory:
                c: Color = bear_col if e.side == 1 else bull_col
                f_L(line.new(e.t0, e.lvl, e.t1, e.lvl, xloc=xloc.bar_time, color=color.new(c, 20), style=line.style_dotted))
                if not zen_mode:
                    tip: str = 'Historical ' + ('equal highs' if e.side == 1 else 'equal lows') + ' at ' + f_px(e.lvl) + '. Confirmed ' + string.format_time(e.confirmedAt, 'yyyy-MM-dd HH:mm', syminfo.timezone) + ' (exchange time), ' + string.tostring(i_int) + ' bars after the second pivot. Retained after a sweep; not a statement that this pool is still resting.'
                    f_B(label.new(e.t1, e.lvl, 'EQH' if e.side == 1 else 'EQL', xloc=xloc.bar_time, style=label.style_label_down if e.side == 1 else label.style_label_up, color=color.new(c, 100), textcolor=c, size=size.tiny, tooltip=tip))

        if show_eq and (not hist_view):
            for side in pine_range(0, 1):
                a: list[Liq] = liqUp if side == 0 else liqDn
                nd: int = 0
                if array.size(a) > 0:
                    for i in pine_range(0, array.size(a) - 1):
                        l: Liq = array.get(a, i)

                        if l.kind == 1 and nd < 2 and (math.abs(l.lvl - close) <= 8.0 * atr):
                            nd += 1
                            c: Color = bear_col if side == 0 else bull_col
                            f_L(line.new(l.tLine, l.lvl, tR, l.lvl, xloc=xloc.bar_time, color=color.new(c, 30), style=line.style_dotted))
                            if not zen_mode:
                                f_B(label.new(l.tLabel, l.lvl, 'EQH' if side == 0 else 'EQL', xloc=xloc.bar_time, style=label.style_label_down if side == 0 else label.style_label_up, color=color.new(c, 100), textcolor=color.new(c, 20), size=size.tiny))

        if show_draw:
            lUp, lDn, pUp, qUp = f_liveDraw()
            for side in pine_range(0, 1):
                a: list[Liq] = liqUp if side == 0 else liqDn
                ix: int = f_liqIdx(a, 1 if side == 0 else -1)
                if ix >= 0:
                    l: Liq = array.get(a, ix)
                    c: Color = bear_col if side == 0 else bull_col
                    pS: float = na if na(pUp) else pUp if side == 0 else 1.0 - pUp
                    qS: float = na if na(qUp) else qUp if side == 0 else 1.0 - qUp
                    if l.kind == 0 or not show_eq or hist_view:
                        f_L(line.new(l.tLine, l.lvl, tR, l.lvl, xloc=xloc.bar_time, color=color.new(c, 45), style=line.style_dashed))
                    if not zen_mode:
                        nm: str = ('BSL ' if side == 0 else 'SSL ') + f_px(l.lvl)
                        ltp: str = ('Buy-side liquidity above: ' if side == 0 else 'Sell-side liquidity below: ') + ('equal ' + ('highs' if side == 0 else 'lows') if l.kind == 1 else 'untaken swing ' + ('high' if side == 0 else 'low')) + ' at ' + f_px(l.lvl) + '.' + ('' if na(pS) else '\n\nChance it is traded through before the ' + ('sell-side pool at ' + f_px(lDn) if side == 0 else 'buy-side pool at ' + f_px(lUp)) + ': ' + f_pct(pS) + '.\nRandom-walk first-touch formula: ' + f_pct(qS) + ', calibrated on ' + string.tostring(c_dr.n) + ' resolved setups on this chart. Updates with price.')
                        f_q(l.lvl, nm + ('' if na(pS) else '  ' + f_pct(pS)), c, ltp)

        if show_int:
            for m in inMarks:
                c: Color = color.new(f_role(m.dir), 20)
                f_L(line.new(m.t0, m.lvl, m.t1, m.lvl, xloc=xloc.bar_time, color=c, style=line.style_dashed))
                if not zen_mode:
                    f_B(label.new(f_markTime(m.t0, m.t1), m.lvl, 'i-CHoCH' if m.choch else 'i-BOS', xloc=xloc.bar_time, style=label.style_label_down if m.dir == 1 else label.style_label_up, color=color.new(c, 100), textcolor=c, size=size.tiny, tooltip='Internal ' + ('change of character' if m.choch else 'break of structure') + ' confirmed at the close of ' + string.format_time(m.t1, 'yyyy-MM-dd HH:mm', syminfo.timezone) + ' (exchange time), through ' + f_px(m.lvl) + '. Display only.'))

        drawnSwings: list[Mark] = swHistory if hist_view else swMarks
        nM: int = array.size(drawnSwings)
        if nM > 0:
            for j in pine_range(0, nM - 1):
                m: Mark = array.get(drawnSwings, j)
                latest: bool = array.size(swMarks) > 0 and m.t1 == array.last(swMarks).t1
                c: Color = f_role(m.dir)
                f_L(line.new(m.t0, m.lvl, m.t1, m.lvl, xloc=xloc.bar_time, color=color.new(c, 0 if latest else 15), width=2 if m.choch else 1))
                if not zen_mode:
                    g: str = '' if hist_view else ' ↺' if m.ret == 1 else ' →' if m.ret == -1 else ''
                    txt: str = ('CHoCH' if m.choch else 'BOS') + (' · retest ' + f_pct(m.pr) if latest and i_latest_odds and (not na(m.pr)) else '') + g
                    out: str = '\n\nOutcome: price came back to the level ↺' if m.ret == 1 else '\n\nOutcome: price did not come back within the window →' if m.ret == -1 else '\n\nOutcome: open'
                    f_B(label.new(f_markTime(m.t0, m.t1), m.lvl, txt, xloc=xloc.bar_time, style=label.style_label_down if m.dir == 1 else label.style_label_up, color=color.new(c, 80) if latest else color.new(c, 100), textcolor=c, size=swing_text_size, tooltip=m.tip + '\nBreak confirmed: ' + string.format_time(m.t1, 'yyyy-MM-dd HH:mm', syminfo.timezone) + ' (exchange time).' + out + '\nRetest outcome is evaluated after the break, through the latest loaded bar.'))

        if show_swl and (not zen_mode):
            for s in swPts:
                c: Color = bear_col if s.dir == 1 else bull_col
                f_B(label.new(s.t, s.p, s.txt, xloc=xloc.bar_time, style=label.style_label_down if s.dir == 1 else label.style_label_up, color=color.new(c, 100), textcolor=c, size=size.tiny))

        if show_sig:
            for t in trades:
                tc: Color = f_role(t.dir)
                sc: Color = f_role(-t.dir)
                te: int = tR if t.open else t.tEnd
                f_L(line.new(t.t0, t.entry, te, t.entry, xloc=xloc.bar_time, color=color.new(color.gray, 0), style=line.style_dashed))
                f_L(line.new(t.t0, t.sl0, t.tBE if t.tBE > 0 else te, t.sl0, xloc=xloc.bar_time, color=sc, width=2))
                if t.tBE > 0:
                    f_L(line.new(t.tBE, t.entry, te, t.entry, xloc=xloc.bar_time, color=sc, width=2, style=line.style_dotted))
                f_L(line.new(t.t0, t.tp1, te, t.tp1, xloc=xloc.bar_time, color=color.new(tc, 30)))
                f_L(line.new(t.t0, t.tp2, te, t.tp2, xloc=xloc.bar_time, color=tc, width=2))
                if not zen_mode:
                    if t.open:
                        if t.tBE == 0:
                            f_q(t.entry, ('BUY ' if t.dir == 1 else 'SELL ') + f_px(t.entry), color.new(color.gray, 0), 'Entry, ' + t.how + '.')
                        f_q(t.sl, 'SL at entry ' + f_px(t.sl) if t.tBE > 0 else 'SL ' + f_px(t.sl), sc, 'Stop beyond the protected swing.')
                        f_q(t.tp1, 'TP1 ' + f_px(t.tp1), tc, string.tostring(i_tp1) + ' R')
                        f_q(t.tp2, 'TP2 ' + f_px(t.tp2), tc, string.tostring(i_tp2) + ' R')
                    else:
                        win: bool = t.res == 'TP2' or t.res == 'TP1, then stop at entry'
                        c: Color = sc if t.res == 'SL' else tc
                        rt: str = 'TP2' if t.res == 'TP2' else 'SL' if t.res == 'SL' else t.res
                        f_B(label.new(t.tEnd, t.px, rt, xloc=xloc.bar_time, style=label.style_label_left, color=color.new(c, 20 if win else 70), textcolor=color.white if win else c, size=size.small))

        if not na(rng_hi) and (not na(rng_lo)):
            tE: int = tR
            tHi: int = sw.legHiT if sw.legHi >= nz(sw.hi, -1e+20) and (not na(sw.legHi)) else sw.hiT
            tLo: int = sw.legLoT if sw.legLo <= nz(sw.lo, 1e+20) and (not na(sw.legLo)) else sw.loT
            if show_sw:
                f_L(line.new(tHi, rng_hi, tE, rng_hi, xloc=xloc.bar_time, color=color.new(bear_col, 30)))
                f_L(line.new(tLo, rng_lo, tE, rng_lo, xloc=xloc.bar_time, color=color.new(bull_col, 30)))

                if not zen_mode:
                    f_B(label.new(tHi, rng_hi, 'Strong High' if sw.trend == -1 else 'Weak High', xloc=xloc.bar_time, style=label.style_label_down, color=color.new(bear_col, 100), textcolor=color.new(bear_col, 20), size=size.tiny))
                    f_B(label.new(tLo, rng_lo, 'Strong Low' if sw.trend == 1 else 'Weak Low', xloc=xloc.bar_time, style=label.style_label_up, color=color.new(bull_col, 100), textcolor=color.new(bull_col, 20), size=size.tiny))
            if show_pd:
                tL: int = math.min(tHi, tLo)
                mid: float = (rng_hi + rng_lo) / 2.0
                array.push(g_bx, box.new(tL, rng_hi, tE, mid, xloc=xloc.bar_time, border_color=color.new(bear_col, 100), bgcolor=color.new(bear_col, 92), text='Premium', text_color=color.new(bear_col, 30), text_size=size.small, text_halign=text.align_right, text_valign=text.align_top))
                array.push(g_bx, box.new(tL, mid, tE, rng_lo, xloc=xloc.bar_time, border_color=color.new(bull_col, 100), bgcolor=color.new(bull_col, 92), text='Discount', text_color=color.new(bull_col, 30), text_size=size.small, text_halign=text.align_right, text_valign=text.align_bottom))
                f_L(line.new(tL, mid, tE, mid, xloc=xloc.bar_time, color=color.new(color.gray, 30), style=line.style_dotted))

        f_qFlush(tR)

    tbl: Persistent[Table] = table.new(position.bottom_right if i_tbl_pos == 'Bottom Right' else position.top_left if i_tbl_pos == 'Top Left' else position.bottom_left if i_tbl_pos == 'Bottom Left' else position.top_right, 2, 12, bgcolor=color.new(color.black, 75), border_color=color.new(color.gray, 60), border_width=1, frame_color=color.new(color.gray, 50), frame_width=1)

    def f_cell(row: int, k: str, v: str, vc: Color, tip: str):
        table.cell(tbl, 0, row, k, text_color=color.new(color.white, 0), text_size=size.small, text_halign=text.align_left)
        table.cell(tbl, 1, row, v, text_color=vc, text_size=size.small, text_halign=text.align_left, tooltip=tip)
        return row + 1

    if barstate.islast and show_table and (not zen_mode):
        table.clear(tbl, 0, 0, 1, 11)
        gry: Color = color.new(color.gray, 20)
        wht: Color = color.new(color.white, 0)
        live: bool = c_rt.n >= CAL_MIN
        cOk: bool = f_calOk(c_rt) and (not show_draw or c_dr.n < CAL_MIN or f_calOk(c_dr))

        ot: Trade = na(Trade)
        if array.size(trades) > 0:
            lt: Trade = array.get(trades, array.size(trades) - 1)
            if lt.open:
                ot = lt

        st: str = '● LEARNING  ' + string.tostring(c_rt.n) + ' / ' + string.tostring(CAL_MIN) + ' resolved breaks' if not live else '● LIVE  ·  ' + string.tostring(c_rt.n) + ' breaks scored  ·  ' + ('calibrated' if cOk else 'check calibration')
        stc: Color = color.new(color.yellow, 0) if not live else color.new(color.lime, 0) if cOk else color.new(bear_col, 0)
        table.cell(tbl, 0, 0, 'SMC ML', text_color=color.new(color.gray, 0), text_size=size.small, bgcolor=color.new(color.black, 60), text_halign=text.align_left)
        table.cell(tbl, 1, 0, st, text_color=stc, text_size=size.small, bgcolor=color.new(color.black, 60), text_halign=text.align_left, tooltip="Every odds figure starts from random-walk probability and is recalibrated on this chart's resolved outcomes (Bayesian logistic calibration, prior centred on the formula). Every break, signal and recorded figure is fixed at bar close; the liquidity odds and the premium / discount % follow the live price. Swings confirm" + string.tostring(i_swing) + ' bars after the bar they mark.')

        bdir: int = sw.trend
        zoneS: str = '' if na(rng_pos) else '  ·  ' + ('PREMIUM ' if rng_pos > 0.5 else 'DISCOUNT ') + string.tostring(math.round(rng_pos * 100)) + '%'
        biasTx: str = '▲  BULLISH structure' + zoneS if bdir == 1 else '▼  BEARISH structure' + zoneS if bdir == -1 else '—  NO STRUCTURE YET'
        biasBg: Color = color.new(color.gray, 70) if bdir == 0 else color.new(f_role(bdir), 25)
        table.cell(tbl, 0, 1, 'Bias', text_color=wht, text_size=size.normal, bgcolor=biasBg, text_halign=text.align_left)
        table.cell(tbl, 1, 1, biasTx, text_color=color.white, text_size=size.normal, bgcolor=biasBg, text_halign=text.align_left, tooltip='Swing structure direction. Premium / discount is where price sits in the current dealing range (0% = its low, 100% = its high).')
        row: int = 2

        act: str = "Waiting for swing structure"
        acd: int = bdir
        nowTip: str = ""
        if not na(ot):
            acd = ot.dir
            act = ('LONG ' if ot.dir == 1 else 'SHORT ') + f_px(ot.entry) + '  ·  SL ' + f_px(ot.sl) + '  ·  TP1 ' + f_px(ot.tp1) + '  ·  TP2 ' + f_px(ot.tp2) + '  ·  ' + ('holding for TP2' if ot.tp1hit else 'holding for TP1')
            nowTip = 'Entered on the ' + ot.how + '. Half the position is scored at TP1, the rest at TP2 or the stop.'
        elif rt_dir != 0:
            acd = rt_dir
            act = ('BUY' if rt_dir == 1 else 'SELL') + ' if price comes back to ' + f_px(rt_lvl) + ' and closes ' + ('above' if rt_dir == 1 else 'below') + ' it  ·  ' + string.tostring(math.max(i_rt_win - (bar_index - rt_bar), 0)) + ' bars left'
        elif sw.trend == 1:
            act = 'Next BOS above ' + (f_px(sw.hi) if sw.hiOpen else 'the next swing high') + '  ·  CHoCH below ' + (f_px(sw.lo) if sw.loOpen else 'the next swing low')
        elif sw.trend == -1:
            act = 'Next BOS below ' + (f_px(sw.lo) if sw.loOpen else 'the next swing low') + '  ·  CHoCH above ' + (f_px(sw.hi) if sw.hiOpen else 'the next swing high')
        if na(ot) and array.size(trades) > 0:
            lt: Trade = array.get(trades, array.size(trades) - 1)
            nowTip = 'Last signal: ' + ('BUY' if lt.dir == 1 else 'SELL') + ' → ' + lt.res + '.'
        row = f_cell(row, 'Now', act, gry if acd == 0 else f_role(acd), nowTip)

        rTx: str = "—"
        rCl: Color = gry
        nM: int = array.size(swMarks)
        if nM > 0:
            m: Mark = array.get(swMarks, nM - 1)
            rCl = f_role(m.dir)
            rTx = 'measuring volatility' if na(m.pr) else (f_pct(m.pr) + ' that price comes back to ' + f_px(m.lvl) + ' within ' + string.tostring(i_rt_win) + ' bars' if m.ret == 0 else f_px(m.lvl) + (' retested ↺' if m.ret == 1 else ' not retested →') + '  ·  odds were ' + f_pct(m.pr)) + '  (n ' + string.tostring(c_rt.n) + ')'
        row = f_cell(row, 'Retest', rTx, rCl, 'Chance that price trades back to the latest broken swing level within the Retest Window. ↺ = it came back, → = it did not. n = resolved breaks the odds are calibrated on.')

        if show_draw:
            lUp, lDn, pUp, qUp = f_liveDraw()
            dTx: str = 'needs a pool on both sides' if na(lUp) or na(lDn) else 'price is at a pool' if na(pUp) else '▲ BSL ' + f_px(lUp) + ' ' + f_pct(pUp) + '  ·  ▼ SSL ' + f_px(lDn) + ' ' + f_pct(1.0 - pUp)
            dCl: Color = gry if na(pUp) else bull_col if pUp >= 0.5 else bear_col
            row = f_cell(row, 'Liquidity', dTx, dCl, 'Chance that each nearest untaken pool is traded through before the other, from the current price. Random-walk first-touch probability' + ('' if na(qUp) else ' (' + f_pct(qUp) + ' for the pool above)') + ', calibrated on ' + string.tostring(c_dr.n) + ' resolved setups here. Distance alone accounts for most of it.')

        nC: float = array.get(rec, 0)
        recT: str = "—"
        recP: str = "Hypothetical outcomes of the signals on the loaded history only: half the position at TP1, the rest at TP2, the stop, or the close of the bar where the signal timed out or was reversed. No commission or slippage. They change with the amount of history loaded and say nothing about future results."
        if nC > 0:
            mR: float = array.get(rec, 3) / nC
            sd: float = math.sqrt(math.max(array.get(rec, 4) - nC * mR * mR, 0.0) / (nC - 1)) if nC > 1 else na

            nu: float = nC - 1.0
            tq: float = 1.96 + (math.pow(1.96, 3) + 1.96) / (4.0 * nu) + (5.0 * math.pow(1.96, 5) + 16.0 * math.pow(1.96, 3) + 3.0 * 1.96) / (96.0 * nu * nu) if nC >= 10 else na
            ci: float = na if na(sd) or na(tq) else tq * sd / math.sqrt(nC)
            recT = string.tostring(nC, '#') + ' hypothetical  ·  avg ' + f_sgn(mR, '0.00') + 'R' + ('' if na(ci) else ' ± ' + string.tostring(ci, '0.00')) + ('  ·  too few to judge' if nC < 30 else '  ·  interval covers 0' if math.abs(mR) <= ci else '  ·  interval excludes 0')
            recP = recP + '\n\nTP1 reached ' + f_pct(array.get(rec, 1) / nC) + '  ·  full stop ' + f_pct(array.get(rec, 2) / nC) + '. The ± is a 95% interval on the average; when it covers zero the average is not distinguishable from no edge. No verdict is given below 30 signals.'
        row = f_cell(row, 'Record', recT, wht, recP)

        nmA: list[str] = array.from_items('BOS', 'FVG', 'sweep')
        nmB: list[str] = array.from_items('CHoCH', 'no FVG', 'no sweep')
        bz: float = na(float)
        bk: int = -1
        for k in pine_range(0, 2):
            o: int = k * 4
            z: float = f_z(array.get(et, o), array.get(et, o + 1), array.get(et, o + 2), array.get(et, o + 3))
            if not na(z) and (na(bz) or math.abs(z) > math.abs(bz)):
                bz = z
                bk = k
        nAll: int = array.get(et, 0) + array.get(et, 2)
        eTx: str = 'collecting  ·  ' + string.tostring(nAll) + ' breaks resolved'
        eCl: Color = gry
        eTip: str = ""
        if bk >= 0:
            o: int = bk * 4
            pa: float = cast_float(array.get(et, o + 1)) / array.get(et, o)
            pb: float = cast_float(array.get(et, o + 3)) / array.get(et, o + 2)
            pp: float = cast_float(array.get(et, o + 1) + array.get(et, o + 3)) / (array.get(et, o) + array.get(et, o + 2))
            dd: float = math.abs(pa - pb)
            need: float = math.pow(Z_BONF + 0.84, 2) * 2.0 * pp * (1.0 - pp) / (dd * dd) if dd > 0.005 else na
            sig: bool = math.abs(bz) >= Z_BONF
            eTx = array.get(nmA, bk) + ' ' + f_pct(pa) + ' / ' + array.get(nmB, bk) + ' ' + f_pct(pb) + '  ·  z ' + f_sgn(bz, '0.0') + '  ·  ' + ('beyond chance' if sig else 'within chance')
            eTip = '\n\nShown split: ' + array.get(nmA, bk) + ' n ' + string.tostring(array.get(et, o)) + ', ' + array.get(nmB, bk) + ' n ' + string.tostring(array.get(et, o + 2)) + '.' + ('' if sig or na(need) else ' Detecting a gap this size at the corrected level would need about ' + string.tostring(math.round(need)) + ' breaks of each kind.')
            eCl = wht if sig else gry
        fAll: float = cast_float(array.get(et, 1) + array.get(et, 3)) / nAll if nAll > 0 else na
        row = f_cell(row, 'Edge test', eTx, eCl, 'Share of swing breaks that closed one risk unit beyond the break before closing back through the protected swing (' + f_pct(fAll) + ' of ' + string.tostring(nAll) + ' resolved here; breaks unresolved after 150 bars are not counted), split three ways: BOS / CHoCH, leg left a fair value gap or not, leg swept liquidity first or not. Shown: the split with the largest z. A split counts only at |z| ≥ 2.39 (5% after correcting for three tests).' + eTip)

        cTx: str = 'retest ' + f_calText(c_rt) + ('  ·  liquidity ' + f_calText(c_dr) if show_draw else '')
        row = f_cell(row, 'Calibration', cTx, gry, 'Average odds shown → how often the event happened, scored with the odds each sample had when it printed (retest n ' + string.tostring(c_rt.n) + ', liquidity n ' + string.tostring(c_dr.n) + '). ✓ = the overall average and every band with 20+ samples sit inside a 95% interval (bands corrected for three tests).\n\nRetest odds by band:\n   ' + f_bands(c_rt) + '\nLiquidity odds by band:\n   ' + f_bands(c_dr) + '\n\nBrier skill, retest odds: vs base rate ' + f_skill(c_rt.bsM, c_rt.bsB) + ', vs formula alone ' + f_skill(c_rt.bsM, c_rt.bsF) + '.\nBrier skill, liquidity odds: vs base rate ' + f_skill(c_dr.bsM, c_dr.bsB) + ', vs formula alone ' + f_skill(c_dr.bsM, c_dr.bsF) + '.\nAbove zero = better than that reference. Consecutive samples overlap in time, so the intervals are somewhat optimistic.')
        row = f_cell(row, 'Structure view', 'visible window · ' + string.tostring(array.size(swHistory)) + '/' + string.tostring(i_hist_sw) + ' swing · ' + string.tostring(array.size(inMarks)) + '/' + string.tostring(i_hist_in) + ' internal · ' + string.tostring(array.size(eqHistory)) + '/' + string.tostring(i_hist_eq) + ' EQ' if hist_view else 'recent · 6 swing / 20 internal max', gry, 'Historical counts / display limits. At a limit, older drawings in the window are omitted; zoom into that period to rebuild them. Solid = swing, dashed = internal, dotted = EQH/EQL formation. Blue = bullish structure, orange = bearish structure. The rest of this dashboard and active zones describe the latest loaded bar, even when you pan back.')
        if not chart.is_standard:
            row = f_cell(row, 'Note', 'synthetic chart · OHLC is not traded price', color.new(color.yellow, 0), '')

    plotshape(show_sig and ev_buy, 'BUY', shape.triangleup, location.belowbar, bull_col, size=size.tiny, text='', textcolor=bull_col)
    plotshape(show_sig and ev_sell, 'SELL', shape.triangledown, location.abovebar, bear_col, size=size.tiny, text='', textcolor=bear_col)

    alertcondition(ev_buy, 'BUY signal', 'SMC ML: BUY signal on {{ticker}} at {{close}}.')
    alertcondition(ev_sell, 'SELL signal', 'SMC ML: SELL signal on {{ticker}} at {{close}}.')
    alertcondition(ev_exit, 'Signal closed', 'SMC ML: the open signal on {{ticker}} closed at {{close}}.')
    alertcondition(ev_bchoch, 'Bullish CHoCH', 'SMC ML: bullish change of character on {{ticker}} at {{close}}.')
    alertcondition(ev_schoch, 'Bearish CHoCH', 'SMC ML: bearish change of character on {{ticker}} at {{close}}.')
    alertcondition(ev_bbos, 'Bullish BOS', 'SMC ML: bullish break of structure on {{ticker}} at {{close}}.')
    alertcondition(ev_sbos, 'Bearish BOS', 'SMC ML: bearish break of structure on {{ticker}} at {{close}}.')
    alertcondition(ev_sweep, 'Liquidity swept', 'SMC ML: price traded through a liquidity pool on {{ticker}} at {{close}}.')

    cover_title: Persistent[Table] = table.new(position.top_center, 1, 3)
    cover_key: Persistent[Table] = table.new(position.bottom_center, 1, 3)
    if barstate.islast:
        table.clear(cover_title, 0, 0, 0, 2)
        table.clear(cover_key, 0, 0, 0, 2)
        if show_heading and (not zen_mode):
            table.cell(cover_title, 0, 0, '', height=3, bgcolor=color.new(color.black, 100))
            table.cell(cover_title, 0, 1, 'SMART MONEY CONCEPT ML', text_size=42, text_color=color.new('#E2E8F2'), bgcolor=color.new(color.black, 100))
            table.cell(cover_title, 0, 2, 'v2  ·  Historical structure  ·  Outcome-calibrated estimates', text_size=15, text_color=color.new('#A5B3C8'), bgcolor=color.new(color.black, 100))
            table.cell(cover_key, 0, 0, 'BLUE  bullish structure     ORANGE  bearish structure', text_size=13, text_color=color.new('#DCE6F2'), bgcolor=color.new('#101C2C'))
            table.cell(cover_key, 0, 1, 'SOLID  swing BOS / CHoCH     DASHED  internal     DOTTED  EQH / EQL', text_size=12, text_color=color.new('#A5B3C8'), bgcolor=color.new('#101C2C'))
            table.cell(cover_key, 0, 2, 'Confirmed-bar events · pivots marked after confirmation · estimates, not guarantees', text_size=11, text_color=color.new('#A5B3C8'), bgcolor=color.new('#101C2C'))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
