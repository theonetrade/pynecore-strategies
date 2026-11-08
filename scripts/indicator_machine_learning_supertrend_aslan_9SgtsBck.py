"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_float, cast_int
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barcolor, barstate, close,
    color, display, fill, format, high, hl2, hlc3, hlcc4, input, label, location, low, math, na,
    nz, ohlc4, open, plot, plotshape, position, script, shape, size, string, syminfo, ta, table,
    text, volume, xloc, yloc
)
from pynecore.types import Color, Label, NA, Persistent, PersistentSeries, Series, Table


@udt
class GCell:
    mean: float = na(float)
    count: int = na(int)
    conf: float = na(float)
    dMult: float = na(float)
    dLen: float = na(float)


@udt
class Probe:
    entry: float = na(float)
    bar: int = na(int)
    dir: int = na(int)
    live: bool = na(bool)
    atr0: float = na(float)
    mae: float = na(float)


grpCol: str = "◇ 0 · Palette"
grpSig: str = "◆ 1 · Signal Engine"
grpEnv: str = "◆ 2 · Volatility Envelope"
grpFlt: str = "◆ 3 · Filters"
grpAdp: str = "◆ 4 · Adaptive Core"
grpCtx: str = "◆ 5 · Context Memory"
grpVis: str = "◆ 6 · Overlays"
grpDsh: str = "◆ 7 · Dashboard"
REG_LEN: int = 64
HOLD: int = 5
SLOTS: int = 5


@script.indicator("Machine Learning Supertrend [Aslan]", "Machine Learning Supertrend [Aslan]", overlay=True, max_bars_back=2000, max_labels_count=500, max_lines_count=500, max_boxes_count=500)
def main(
    bullCol=input.color(color.teal, "Bull", group=grpCol, inline="p1"),
    bearCol=input.color(color.red, "Bear", group=grpCol, inline="p1"),
    accentCol=input.color(color.new('#4D9FFF'), "Accent", group=grpCol, inline="p1", tooltip="Used for low-volatility and grid-confidence readouts on the dashboard."),
    neutCol=input.color(color.new('#787B86'), "Neutral", group=grpCol, inline="p1"),
    sigMode=input.string("Reversal", "Mode", options=("Reversal", "Breakout"), group=grpSig, tooltip="Reversal: fires when a trend exhausts at a fresh extreme and the band flips. Breakout: fires when price pushes into a new extreme WITH the trend. Opposite premises - pick one and tune for it."),
    pivotWin=input.int(30, "Pivot Window", minval=5, maxval=400, group=grpSig, tooltip="Bars scanned for new highs and lows. Lower reacts to minor swings, higher only to structural moves."),
    needFresh=input.bool(True, "Require Fresh Pivot", group=grpSig, tooltip="Reversal mode only. Demands a genuine new extreme during the trend before a flip counts as a signal."),
    sigSpacing=input.int(10, "Min Bars Between Signals", minval=1, maxval=500, group=grpSig),
    confirmOnly=input.bool(True, "Confirmed Bars Only", group=grpSig, tooltip="ON: signals only latch on bar close, nothing repaints intrabar. OFF: signals appear live and can vanish. Leave ON unless you have a reason."),
    showSigLabel=input.bool(True, "Show Signal Labels", group=grpSig),
    baseAtrLen=input.int(24, "ATR Period", minval=5, maxval=300, group=grpEnv),
    baseMult=input.float(1.4, "Band Width (xATR)", minval=0.3, maxval=6.0, step=0.05, group=grpEnv, tooltip="The single most impactful setting. Wider bands flip less often and give fewer, higher-conviction signals."),
    srcType=input.string("hlcc4", "Price Basis", options=("close", "hl2", "hlc3", "ohlc4", "hlcc4"), group=grpEnv),
    useRMA=input.bool(True, "RMA Smoothing", group=grpEnv, tooltip="OFF switches to EMA - faster reaction to volatility spikes, noisier bands."),
    showTrendLn=input.bool(True, "Show Trend Line", group=grpEnv),
    useRSI=input.bool(True, "Momentum Filter", group=grpFlt, tooltip="In Reversal mode a long needs RSI to have been recently oversold. In Breakout mode the polarity inverts - a long needs RSI to have been recently HOT, because you are buying strength, not exhaustion."),
    rsiLen=input.int(14, "  RSI Length", minval=2, maxval=50, group=grpFlt),
    rsiHi=input.int(70, "  Hot / Cold Level", minval=55, maxval=90, group=grpFlt, inline="rl"),
    rsiLo=input.int(30, "", minval=10, maxval=45, group=grpFlt, inline="rl"),
    rsiMem=input.int(50, "  Zone Memory (bars)", minval=1, maxval=400, group=grpFlt, tooltip="How far back RSI must have visited the hot or cold zone for the filter to pass."),
    useVol=input.bool(False, "Require Volume Surge", group=grpFlt, tooltip="Cuts signal count hard. Useless on synthetic symbols and most FX feeds, where volume is a tick count."),
    volLen=input.int(3, "  Baseline Depth", minval=1, maxval=300, group=grpFlt),
    volMult=input.float(1.2, "  Surge Threshold", minval=0.1, maxval=5.0, step=0.1, group=grpFlt),
    useMajor=input.bool(False, "Key Levels Only", group=grpFlt, tooltip="Only allows signals where the pivot-window range spans a large ATR multiple. Swing-trader setting."),
    majorATR=input.float(4.5, "  Key Level Depth (xATR)", minval=1.0, maxval=20.0, step=0.1, group=grpFlt),
    useBias=input.bool(False, "Require Trend Alignment", group=grpFlt, tooltip="Blocks counter-trend signals using the 200 EMA. In Reversal mode this is self-contradictory by construction and will suppress most turning points. Intended for Breakout mode."),
    adaptOn=input.bool(True, "Enable Auto-Tune", group=grpAdp, tooltip="OFF: a conventional fixed-parameter supertrend using your inputs verbatim, fully reproducible. ON: the probe engine drifts band width, ATR period, stop and target from rolling probe outcomes."),
    reactivity=input.int(10, "Reactivity (1-20)", minval=1, maxval=20, group=grpAdp, tooltip="Meta-dial. Sets per-update caps, deadband and blend alpha in one move. 1 = glacial, 20 = twitchy."),
    learnRate=input.float(0.25, "Step Size", minval=0.01, maxval=0.5, step=0.01, group=grpAdp),
    rollN=input.int(30, "Probe Memory (per side)", minval=5, maxval=500, group=grpAdp, tooltip="Rolling window of probe outcomes feeding win rate, mean return and Sortino. Longer is more stable and slower to react."),
    winHi=input.float(0.62, "Win Ceiling", minval=0.5, maxval=1.0, step=0.01, group=grpAdp, inline="w"),
    winLo=input.float(0.38, "Floor", minval=0.0, maxval=0.5, step=0.01, group=grpAdp, inline="w"),
    updEvery=input.int(3, "Update Cooldown (bars)", minval=1, maxval=100, group=grpAdp),
    deadband=input.float(0.01, "Deadband", minval=0, maxval=0.2, step=0.005, group=grpAdp, tooltip="A proposed band-width change must exceed this before it is applied. Kills micro-jitter."),
    revertEvery=input.int(200, "Anchor Revert Interval", minval=10, maxval=5000, group=grpAdp, tooltip="Every N bars the adapted parameters are pulled a fraction back toward your base inputs. Stops unbounded drift."),
    revertStep=input.float(0.02, "Anchor Revert Strength", minval=0.001, maxval=0.2, step=0.001, group=grpAdp),
    useGrid=input.bool(True, "Enable Regime Grid", group=grpCtx, tooltip="2D map of (trend regime x volatility). Remembers which parameter shifts worked in each cell and reapplies them when the market returns to a familiar state."),
    gridX=input.int(8, "Regime Bins", minval=4, maxval=16, group=grpCtx, inline="g"),
    gridY=input.int(8, "Vol Bins", minval=4, maxval=16, group=grpCtx, inline="g"),
    gridSigma=input.float(0.8, "Neighbour Blend", minval=0.2, maxval=2.0, step=0.05, group=grpCtx, tooltip="Gaussian sigma in bin units. Higher smooths across sparse neighbouring cells."),
    gridHalf=input.int(50, "Decay Half-Life (probes)", minval=10, maxval=400, group=grpCtx),
    gridConfN=input.int(20, "Confidence Ramp (probes)", minval=5, maxval=200, group=grpCtx, tooltip="Probes needed for a cell to reach roughly 63% confidence."),
    gridMaxW=input.float(0.65, "Max Grid Influence", minval=0.1, maxval=0.9, step=0.05, group=grpCtx),
    volCeil=input.float(2.5, "Vol Ratio Ceiling", minval=1.0, maxval=5.0, step=0.1, group=grpCtx),
    regEvery=input.int(7, "Regime Refresh (bars)", minval=1, maxval=50, group=grpCtx, tooltip="The Hurst and entropy loops are the most expensive thing in this script. Refreshing every bar buys almost nothing."),
    showCloud=input.bool(True, "Trend Cloud", group=grpVis, inline="v1"),
    cloudFade=input.int(78, "", minval=40, maxval=95, group=grpVis, inline="v1", tooltip="Transparency of the densest cloud layer. The gradient fades upward from here."),
    showBarCol=input.bool(True, "Gradient Bar Colour", group=grpVis, tooltip="Bar tint scales with distance from the trend line in ATR units. Driven by the same supertrend state, so it is part of the trend display rather than a separate overlay."),
    showRails=input.bool(True, "Pivot Rails", group=grpVis, inline="r1", tooltip="Plots pivHi[pivBack] and pivLo[pivBack] - the exact two levels newHigh and newLow test against. These lag the running extreme by pivBack bars, which is what makes them crossable. The un-offset ta.highest/ta.lowest series can never be broken by definition, so it is not what is drawn here."),
    railFade=input.int(30, "", minval=0, maxval=90, group=grpVis, inline="r1"),
    railDim=input.bool(True, "    Dim Dormant Side", group=grpVis, tooltip="Only one rail is armed at a time. In BOTH modes the upper rail is live during an uptrend and the lower during a downtrend - topLatch requires trendUp, botLatch requires not trendUp, and Breakout mode gates rawLong/rawShort identically. The dormant rail fades rather than disappears so you can still see where it sits."),
    showRailFill=input.bool(False, "    Key-Level Channel", group=grpVis, tooltip="Shades the pivot range, tinted when pivHi - pivLo clears majorATR x ATR. That span is an UPPER BOUND on the two per-side spans Key Levels Only actually tests, so grey means neither side can pass and tinted means one might. Only informative with that filter on."),
    showRailDot=input.bool(True, "    Mark Raw Breaks", group=grpVis, tooltip="Dots every newHigh / newLow - the raw trigger BEFORE the section 3 filters run. A dot with no signal label means a filter vetoed it."),
    showRailTag=input.bool(True, "    Price Tags", group=grpVis),
    showDash=input.bool(True, "Show Dashboard", group=grpDsh),
    dashPos=input.string("Bottom Right", "Position", options=("Top Right", "Middle Right", "Bottom Right", "Bottom Left", "Top Left"), group=grpDsh),
    dashSize=input.string("Small", "Text Size", options=("Tiny", "Small", "Normal"), group=grpDsh)
):
    def clamp(v, lo, hi):
        return math.max(lo, math.min(hi, v))

    def qz(x, s):
        return x if s <= 0 else math.round(x / s) * s

    def nz0(x):
        return 0.0 if na(x) else x

    def rmaV(x, len):
        a: float = 1.0 / math.max(1.0, len)
        y: PersistentSeries[float] = na(float)
        y = x if na(y[1]) else y[1] + a * (x - y[1])
        return y

    def emaV(x, len):
        a: float = 2.0 / (math.max(1.0, len) + 1.0)
        y: PersistentSeries[float] = na(float)
        y = x if na(y[1]) else a * x + (1.0 - a) * y[1]
        return y

    def rollPush(arr, v, cap):
        array.push(arr, v)
        while array.size(arr) > cap:
            array.shift(arr)
        return 0

    def rollWin(arr):
        n: int = array.size(arr)
        w: float = 0.0
        if n > 0:
            for i in pine_range(0, n - 1):
                w += 1 if array.get(arr, i) > 0 else 0
        return 0.5 if n == 0 else w / n

    def rollAvg(arr):
        n: int = array.size(arr)
        s: float = 0.0
        if n > 0:
            for i in pine_range(0, n - 1):
                s += array.get(arr, i)
        return 0.0 if n == 0 else s / n

    def rollSortino(arr):
        n: int = array.size(arr)
        out: float = na(float)
        if n > 2:
            m: float = 0.0
            dd: float = 0.0
            dc: int = 0
            for i in pine_range(0, n - 1):
                v = array.get(arr, i)
                m += v
                if v < 0:
                    dd += v * v
                    dc += 1
            m /= n
            d: float = math.sqrt(dd / dc) if dc > 0 else na
            out = na if na(d) or d == 0 else m / d
        return out

    def bucket(x, bins):
        return clamp(cast_int(math.floor(x * bins)), 0, bins - 1)

    def meter(v, n):
        f: int = clamp(cast_int(math.round(v * n)), 0, n)
        return string.repeat('█', f) + string.repeat('░', n - f)

    __block_result__ = na
    __switch__ = srcType
    if __switch__ == "close":
        __block_result__ = close
    elif __switch__ == "hl2":
        __block_result__ = hl2
    elif __switch__ == "hlc3":
        __block_result__ = hlc3
    elif __switch__ == "ohlc4":
        __block_result__ = ohlc4
    else:
        __block_result__ = hlcc4
    src = __block_result__

    atr14 = ta.atr(14)
    atrAvg = ta.sma(atr14, 100)
    ema200 = ta.ema(close, 200)
    rsiVal = ta.rsi(close, rsiLen)
    volAvg = ta.sma(volume, volLen)
    _dip, _dim, adxRaw = ta.dmi(14, 14)

    regMean = ta.sma(close, REG_LEN)
    regStd = ta.stdev(close, REG_LEN)
    regDev: Series = close - regMean

    barsColdRSI = ta.barssince(rsiVal < rsiLo)
    barsHotRSI = ta.barssince(rsiVal > rsiHi)

    pivHi: Series = ta.highest(high, pivotWin)
    pivLo: Series = ta.lowest(low, pivotWin)
    pivBack = math.max(1, cast_int(pivotWin / 10))

    def hurstRS():
        __hist_regDev__: Series = regDev[0]
        cum: float = 0.0
        mx: float = 0.0
        mn: float = 0.0
        for i in pine_range(0, REG_LEN - 1):
            cum += nz0(__hist_regDev__[i])
            mx = math.max(mx, cum)
            mn = math.min(mn, cum)
        R: float = mx - mn
        return 0.5 if na(regStd) or regStd == 0 else clamp(math.log(math.max(R, 1e-10) / regStd) / math.log(REG_LEN), 0.0, 1.0)

    def dirEntropy():
        u: float = 0.0
        d: float = 0.0
        for i in pine_range(1, REG_LEN):
            diff = nz0(close[i - 1] - close[i])
            u += 1 if diff > 0 else 0
            d += 1 if diff < 0 else 0
        t: float = u + d
        H: float = 1.0
        if t > 0:
            p1: float = u / t
            p2: float = d / t
            e: float = 0.0
            e += -p1 * math.log(p1) if p1 > 0 else 0.0
            e += -p2 * math.log(p2) if p2 > 0 else 0.0
            H = clamp(e / math.log(2), 0, 1)
        return H

    regimeScore: Persistent[float] = 0.5
    hurstV: Persistent[float] = 0.5
    entropyV: Persistent[float] = 1.0
    if barstate.isfirst or bar_index % regEvery == 0:
        hurstV = hurstRS()
        entropyV = dirEntropy()
        adxN: float = 0.5 if na(adxRaw) else clamp(adxRaw / 50.0, 0, 1)
        regimeScore = clamp(0.35 * (1 - entropyV) + 0.35 * clamp((hurstV - 0.5) * 2, 0, 1) + 0.3 * adxN, 0, 1)

    volRatio = 1.0 if na(atrAvg) or atrAvg == 0 else atr14 / atrAvg
    volNorm = clamp(volRatio / volCeil, 0.0, 1.0)

    grid: Persistent[list[GCell]] = array.new(0, NA(GCell))
    gridReady: Persistent[bool] = False
    if not gridReady:
        for i in pine_range(0, gridX * gridY - 1):
            array.push(grid, GCell(0.0, 0, 0.0, 0.0, 0.0))
        gridReady = True

    def cellIdx(ix, iy):
        return ix * gridY + iy

    def gauss(dx, dy, s):
        return math.exp(-(dx * dx + dy * dy) / (2 * s * s))

    def gridWrite(ix, iy, ret, dM, dL):
        idx: int = cellIdx(ix, iy)
        if idx >= 0 and idx < array.size(grid):
            c = array.get(grid, idx)
            a: float = 1.0 - math.exp(-math.log(2.0) / gridHalf)
            c.mean = c.mean * (1 - a) + ret * a
            c.count = c.count + 1
            c.conf = 1.0 - math.exp(-c.count / cast_float(gridConfN))
            c.dMult = c.dMult * (1 - a) + dM * a
            c.dLen = c.dLen * (1 - a) + dL * a
            array.set(grid, idx, c)
        return 0

    def gridRead(ix, iy):
        ws: float = 0.0
        wc: float = 0.0
        mM: float = 0.0
        mL: float = 0.0
        for dx in pine_range(-1, 1):
            for dy in pine_range(-1, 1):
                nx: int = clamp(ix + dx, 0, gridX - 1)
                ny: int = clamp(iy + dy, 0, gridY - 1)
                idx: int = cellIdx(nx, ny)
                if idx >= 0 and idx < array.size(grid):
                    c = array.get(grid, idx)
                    if c.count > 0:
                        w: float = gauss(dx, dy, gridSigma)
                        ws += w
                        wc += w * c.conf
                        mM += w * c.conf * c.dMult
                        mL += w * c.conf * c.dLen
        den: float = (1.0 if ws == 0 else ws) if wc == 0 else wc
        oM: float = 0.0 if ws == 0 else mM / den
        oL: float = 0.0 if ws == 0 else mL / den
        oC: float = 0.0 if ws == 0 else clamp(wc / ws, 0, 1)
        return (oM, oL, oC)



    bookL: Persistent[list[Probe]] = array.new(0, NA(Probe))
    bookS: Persistent[list[Probe]] = array.new(0, NA(Probe))
    retL: Persistent[list[float]] = array.new_float()
    retS: Persistent[list[float]] = array.new_float()
    maeRoll: Persistent[list[float]] = array.new_float()

    def probeTouch(bk):
        if array.size(bk) > 0:
            for i in pine_range(0, array.size(bk) - 1):
                p = array.get(bk, i)
                if p.live:
                    adverse: float = p.entry - low if p.dir == 1 else high - p.entry
                    p.mae = math.max(p.mae, math.max(0.0, adverse))
                    array.set(bk, i, p)
        return 0

    def probeOpen(bk, dir, a0):
        free: int = na(int)
        if array.size(bk) > 0:
            for i in pine_range(0, array.size(bk) - 1):
                if not array.get(bk, i).live:
                    free = i
                    break
        if na(free):
            array.push(bk, Probe(open, bar_index, dir, True, a0, 0.0))
        else:
            p = array.get(bk, free)
            p.entry = open
            p.bar = bar_index
            p.dir = dir
            p.live = True
            p.atr0 = a0
            p.mae = 0.0
            array.set(bk, free, p)
        return 0

    def probeLive(bk):
        c: int = 0
        if array.size(bk) > 0:
            for i in pine_range(0, array.size(bk) - 1):
                c += 1 if array.get(bk, i).live else 0
        return c

    def probeMature(bk):
        ret: float = na(float)
        mae: float = na(float)
        pick: int = na(int)
        oldest: int = 999999999
        if array.size(bk) > 0:
            for i in pine_range(0, array.size(bk) - 1):
                p = array.get(bk, i)
                if p.live and bar_index - p.bar + 1 >= HOLD and (p.bar < oldest):
                    oldest = p.bar
                    pick = i
            if not na(pick):
                q = array.get(bk, pick)
                raw: float = (close - q.entry) * q.dir
                ret = raw / q.atr0 if q.atr0 != 0 else 0.0
                mae = q.mae / q.atr0 if q.atr0 != 0 else 0.0
                q.live = False
                array.set(bk, pick, q)
        return (ret, mae)

    aMult: Persistent[float] = baseMult
    aLen: Persistent[float] = cast_float(baseAtrLen)
    lastUpdBar: Persistent[int] = na(int)
    nLong: Persistent[int] = 0
    nShort: Persistent[int] = 0

    def dialCaps(K):
        k: float = (K - 1.0) / 19.0
        return (0.02 + 0.1 * k, 0.5 + 2.5 * k, math.max(0.003, deadband * (1 - 0.6 * k)), clamp(0.2 + 0.45 * k, 0.2, 0.65))

    capM, capL, dbM, alphaEff = dialCaps(reactivity)

    def propose(wr, avgRet, sortino, avgMae, n):
        dM: float = 0.0
        dL: float = 0.0
        if adaptOn and n >= 5:
            conf: float = 1.0 / math.sqrt(math.max(1.0, cast_float(n)))
            step: float = learnRate * conf
            weak: bool = wr < winLo and avgRet < 0
            strong: bool = wr > winHi and avgRet > 0
            if weak:
                dM += 0.3 * step
                dL += 0.25 * step
            if strong:
                dM -= 0.2 * step
                dL -= 0.15 * step
            if avgMae > 0.6:
                dM += 0.15 * step
            if not na(sortino):
                dM += 0.18 * step if sortino < 0 else 0.0
                dM -= 0.14 * step if sortino > 1.2 else 0.0
        return (dM, dL)

    if adaptOn and barstate.isconfirmed:
        probeTouch(bookL)
        probeTouch(bookS)

        rL, mL = probeMature(bookL)
        rS, mS = probeMature(bookS)

        if not na(rL):
            rollPush(retL, rL, rollN)
            rollPush(maeRoll, mL, rollN * 2)
        if not na(rS):
            rollPush(retS, rS, rollN)
            rollPush(maeRoll, mS, rollN * 2)

        if probeLive(bookL) < SLOTS:
            probeOpen(bookL, 1, atr14)
        if probeLive(bookS) < SLOTS:
            probeOpen(bookS, -1, atr14)

        avgMae: float = rollAvg(maeRoll)
        dML, dLL = propose(rollWin(retL), rollAvg(retL), rollSortino(retL), avgMae, array.size(retL))
        dMS, dLS = propose(rollWin(retS), rollAvg(retS), rollSortino(retS), avgMae, array.size(retS))

        netM: float = clamp(dML + dMS, -capM, capM)
        netL: float = clamp(dLL + dLS, -capL, capL)

        ix: int = bucket(regimeScore, gridX)
        iy: int = bucket(volNorm, gridY)
        gM, gL, gConf = gridRead(ix, iy)
        wG: float = clamp(gConf, 0.0, gridMaxW) if useGrid else 0.0

        tgtM: float = baseMult * (1 + gM) * wG + aMult * (1 + netM) * (1 - wG)
        tgtL: float = (cast_float(baseAtrLen) + gL) * wG + (aLen + netL) * (1 - wG)

        cool: bool = na(lastUpdBar) or bar_index - lastUpdBar >= updEvery
        if cool and (math.abs(tgtM - aMult) > dbM or math.abs(tgtL - aLen) > 0.25):
            nM: float = clamp(qz(tgtM, 0.05), 0.3, 6.0)
            nL: float = clamp(math.round(tgtL), 5, 300)
            aMult = aMult + (nM - aMult) * alphaEff
            aLen = aLen + (nL - aLen) * alphaEff
            lastUpdBar = bar_index

        if revertEvery > 0 and bar_index % revertEvery == 0:
            aMult = aMult + (baseMult - aMult) * revertStep
            aLen = aLen + (cast_float(baseAtrLen) - aLen) * revertStep

        if useGrid:
            ixc: int = bucket(regimeScore, gridX)
            iyc: int = bucket(volNorm, gridY)
            if not na(rL):
                gridWrite(ixc, iyc, rL, netM, netL)
            if not na(rS):
                gridWrite(ixc, iyc, rS, netM, netL)

    effMult = aMult if adaptOn else baseMult
    effLen = aLen if adaptOn else cast_float(baseAtrLen)

    def aslanmlST(s, m, l, rmaOn):
        trR: float = rmaV(ta.tr(True), l)
        trE: float = emaV(ta.tr(True), l)
        trv: float = trR if rmaOn else trE
        lb: Series[float] = s - m * trv
        ub: Series[float] = s + m * trv
        lb = math.max(lb, nz(lb[1], lb)) if close[1] > nz(lb[1], lb) else lb
        ub = math.min(ub, nz(ub[1], ub)) if close[1] < nz(ub[1], ub) else ub
        t: Persistent[int] = 1
        t = 1 if t == -1 and close > nz(ub[1], ub) else -1 if t == 1 and close < nz(lb[1], lb) else t
        return (t, lb if t == 1 else ub, trv)

    trendDir: Series
    trendDir, stLine, atrAdp = aslanmlST(src, effMult, effLen, useRMA)
    trendUp: bool = trendDir == 1
    flipUp: bool = trendDir == 1 and trendDir[1] == -1
    flipDn: bool = trendDir == -1 and trendDir[1] == 1

    newHigh: bool = not na(pivHi[pivBack]) and pivHi != pivHi[pivBack] and (close > nz(pivHi[pivBack], close))
    newLow: bool = not na(pivLo[pivBack]) and pivLo != pivLo[pivBack] and (close < nz(pivLo[pivBack], close))

    majorSpan: float = atrAdp * majorATR
    freshHigh: bool = newHigh and high - pivLo > majorSpan if useMajor else newHigh
    freshLow: bool = newLow and pivHi - low > majorSpan if useMajor else newLow

    topLatch: PersistentSeries[int] = 0
    botLatch: PersistentSeries[int] = 0
    topLatch = 0 if not trendUp else 1 if freshHigh else nz(topLatch[1])
    botLatch = 0 if trendUp else 1 if freshLow else nz(botLatch[1])

    rsiCold: bool = not useRSI or barsColdRSI < rsiMem
    rsiHot: bool = not useRSI or barsHotRSI < rsiMem
    volOK: bool = not useVol or volume > volMult * nz(volAvg, volume)
    biasUp: bool = not useBias or close > ema200
    biasDn: bool = not useBias or close < ema200

    isRev: bool = sigMode == 'Reversal'

    longFilters: bool = (rsiCold if isRev else rsiHot) and volOK and biasUp
    shortFilters: bool = (rsiHot if isRev else rsiCold) and volOK and biasDn

    lastSigBar: Persistent[int] = -100000
    spaced: bool = bar_index - lastSigBar >= sigSpacing
    barReady: bool = not confirmOnly or barstate.isconfirmed

    rawLong: bool = False
    rawShort: bool = False
    if isRev:
        rawLong = nz(botLatch[1]) == 1 and botLatch == 0 or (not needFresh and flipUp)
        rawShort = nz(topLatch[1]) == 1 and topLatch == 0 or (not needFresh and flipDn)
    else:
        rawLong = freshHigh and trendUp
        rawShort = freshLow and (not trendUp)

    sigLong: bool = False
    sigShort: bool = False
    if barReady and spaced:
        if rawLong and longFilters:
            sigLong = True
        elif rawShort and shortFilters:
            sigShort = True

    if sigLong or sigShort:
        lastSigBar = bar_index

    gradeLong: bool = close > ema200 and regimeScore > 0.5
    gradeShort: bool = close < ema200 and regimeScore > 0.5

    if sigLong:
        nLong += 1
    if sigShort:
        nShort += 1

    if showSigLabel and sigLong:
        label.new(bar_index, low, '▲ Buy' if gradeLong else '▲ Buy', xloc.bar_index, yloc.belowbar, bullCol, label.style_label_up, color.white, size.normal, tooltip='ML Supertrenmd [Aslan] Long\nRegime ' + string.tostring(regimeScore * 100, '#') + '%   Vol ' + string.tostring(volRatio, '#.00') + 'x\nBand ' + string.tostring(effMult, '#.00') + '  ATR ' + string.tostring(effLen, '#'))

    if showSigLabel and sigShort:
        label.new(bar_index, high, '▼ Sell' if gradeShort else '▼ Sell', xloc.bar_index, yloc.abovebar, bearCol, label.style_label_down, color.white, size.normal, tooltip='ML Supertrenmd [Aslan] Short\nRegime ' + string.tostring(regimeScore * 100, '#') + '%   Vol ' + string.tostring(volRatio, '#.00') + 'x\nBand ' + string.tostring(effMult, '#.00') + '  ATR ' + string.tostring(effLen, '#'))

    cloudBase: Color = bullCol if trendUp else bearCol
    cloudSpan: float = close - stLine

    fadeStep: int = 3

    c0 = plot(stLine if showCloud else na, 'cloud0', display=display.none, editable=False)
    c1 = plot(stLine + cloudSpan * 0.1667 if showCloud else na, 'cloud1', display=display.none, editable=False)
    c2 = plot(stLine + cloudSpan * 0.3333 if showCloud else na, 'cloud2', display=display.none, editable=False)
    c3 = plot(stLine + cloudSpan * 0.5 if showCloud else na, 'cloud3', display=display.none, editable=False)
    c4 = plot(stLine + cloudSpan * 0.6667 if showCloud else na, 'cloud4', display=display.none, editable=False)
    c5 = plot(stLine + cloudSpan * 0.8333 if showCloud else na, 'cloud5', display=display.none, editable=False)
    c6 = plot(close if showCloud else na, 'cloud6', display=display.none, editable=False)

    fill(c0, c1, color.new(cloudBase, math.min(99, cloudFade)), 'Cloud L1')
    fill(c1, c2, color.new(cloudBase, math.min(99, cloudFade + fadeStep)), 'Cloud L2')
    fill(c2, c3, color.new(cloudBase, math.min(99, cloudFade + fadeStep * 2)), 'Cloud L3')
    fill(c3, c4, color.new(cloudBase, math.min(99, cloudFade + fadeStep * 3)), 'Cloud L4')
    fill(c4, c5, color.new(cloudBase, math.min(99, cloudFade + fadeStep * 4)), 'Cloud L5')
    fill(c5, c6, color.new(cloudBase, math.min(99, cloudFade + fadeStep * 5)), 'Cloud L6')

    plot(stLine if showTrendLn and trendUp else na, 'Trend ▲', color.new(bullCol, 0), 2, plot.style_linebr)
    plot(stLine if showTrendLn and (not trendUp) else na, 'Trend ▼', color.new(bearCol, 0), 2, plot.style_linebr)

    railHi: float = pivHi[pivBack]
    railLo: float = pivLo[pivBack]

    hiArmed: bool = trendUp
    loArmed: bool = not trendUp

    railHiBase: Color = bearCol if isRev else bullCol
    railLoBase: Color = bullCol if isRev else bearCol

    dormFade: int = math.min(92, railFade + 45)
    railHiCol: Color = color.new(railHiBase, railFade if not railDim or hiArmed else dormFade)
    railLoCol: Color = color.new(railLoBase, railFade if not railDim or loArmed else dormFade)

    railMajor: bool = pivHi - pivLo > atrAdp * majorATR
    railFillCol: Color = color.new(neutCol, 100) if not showRailFill else color.new(accentCol if railMajor else neutCol, 90 if railMajor else 94)

    pRailHi = plot(railHi if showRails else na, 'Rail ▲', railHiCol, 1, plot.style_stepline)
    pRailLo = plot(railLo if showRails else na, 'Rail ▼', railLoCol, 1, plot.style_stepline)
    fill(pRailHi, pRailLo, railFillCol, 'Rail Channel')

    plotshape(railHi if showRails and showRailDot and newHigh else na, 'Break ▲', shape.xcross, location.abovebar, railHiBase, size=size.tiny)
    plotshape(railLo if showRails and showRailDot and newLow else na, 'Break ▼', shape.xcross, location.belowbar, railLoBase, size=size.tiny)

    tagHi: Persistent[Label] = na(Label)
    tagLo: Persistent[Label] = na(Label)
    if showRails and showRailTag and barstate.islast:
        label.delete(tagHi)
        label.delete(tagLo)
        tagHi = label.new(bar_index + 2, railHi, string.tostring(railHi, format.mintick), xloc.bar_index, yloc.price, color.new(railHiBase, 15 if hiArmed else 62), label.style_label_left, color.white, size.small)
        tagLo = label.new(bar_index + 2, railLo, string.tostring(railLo, format.mintick), xloc.bar_index, yloc.price, color.new(railLoBase, 15 if loArmed else 62), label.style_label_left, color.white, size.small)

    distN: float = 0.0 if atrAdp == 0 or na(atrAdp) else clamp(math.abs(close - stLine) / (atrAdp * 2.5), 0, 1)
    barCol: Color = color.from_gradient(distN, 0, 1, color.new(bullCol if trendUp else bearCol, 62), color.new(bullCol if trendUp else bearCol, 0))
    barcolor(barCol if showBarCol else na, title='Gradient Bars')

    def posOf(p):
        __block_result_1__ = na
        __switch__ = p
        if __switch__ == "Top Right":
            __block_result_1__ = position.top_right
        elif __switch__ == "Middle Right":
            __block_result_1__ = position.middle_right
        elif __switch__ == "Bottom Right":
            __block_result_1__ = position.bottom_right
        elif __switch__ == "Bottom Left":
            __block_result_1__ = position.bottom_left
        else:
            __block_result_1__ = position.top_left
        return __block_result_1__

    def sizeOf(s):
        __block_result_2__ = na
        __switch__ = s
        if __switch__ == "Tiny":
            __block_result_2__ = size.tiny
        elif __switch__ == "Normal":
            __block_result_2__ = size.normal
        else:
            __block_result_2__ = size.small
        return __block_result_2__

    dash: Persistent[Table] = na(Table)
    if showDash and barstate.islast and na(dash):
        dash = table.new(posOf(dashPos), 2, 9, border_color=color.new(neutCol, 72), border_width=1, frame_color=color.new(neutCol, 55), frame_width=1)

    def rowKV(t, r, k, v, vc):
        table.cell(t, 0, r, k, text_color=color.new(neutCol, 12), text_size=sizeOf(dashSize), text_halign=text.align_left, bgcolor=color.new(color.new('#0D1117'), 10))
        table.cell(t, 1, r, v, text_color=vc, text_size=sizeOf(dashSize), text_halign=text.align_right, bgcolor=color.new(color.new('#0D1117'), 10))
        return 0

    if showDash and barstate.islast and (not na(dash)):
        hdr: Color = bullCol if trendUp else bearCol
        table.cell(dash, 0, 0, '  ML Supertrend [Aslan]  ', text_color=color.white, text_size=sizeOf(dashSize), text_halign=text.align_left, bgcolor=color.new(hdr, 20))
        table.cell(dash, 1, 0, '▲ BULLISH  ' if trendUp else '▼ BEARISH  ', text_color=color.white, text_size=sizeOf(dashSize), text_halign=text.align_right, bgcolor=color.new(hdr, 20))

        regTxt: str = 'TRENDING' if regimeScore >= 0.66 else 'TRANSITION' if regimeScore >= 0.36 else 'RANGING'
        regClr: Color = bullCol if regimeScore >= 0.66 else neutCol if regimeScore >= 0.36 else bearCol
        rowKV(dash, 1, 'Regime', meter(regimeScore, 8) + '  ' + regTxt, regClr)

        volTxt: str = 'EXTREME' if volRatio >= 1.8 else 'HIGH' if volRatio >= 1.25 else 'NORMAL' if volRatio >= 0.75 else 'LOW'
        volClr: Color = bearCol if volRatio >= 1.8 else color.new(bearCol, 30) if volRatio >= 1.25 else neutCol if volRatio >= 0.75 else accentCol
        rowKV(dash, 2, 'Volatility', meter(volNorm, 8) + '  ' + volTxt, volClr)

        rowKV(dash, 3, 'Hurst / Entropy', string.tostring(hurstV, '#.00') + '  /  ' + string.tostring(entropyV, '#.00'), color.new(neutCol, 8))

        mDrift: Color = bearCol if effMult > baseMult else bullCol if effMult < baseMult else neutCol
        rowKV(dash, 4, 'Band Width', string.tostring(baseMult, '#.00') + ' → ' + string.tostring(effMult, '#.00'), mDrift)
        rowKV(dash, 5, 'ATR Period', string.tostring(baseAtrLen) + ' → ' + string.tostring(effLen, '#'), color.new(neutCol, 8))

        wrL: float = rollWin(retL)
        wrS: float = rollWin(retS)
        rowKV(dash, 6, 'Probe WR L / S', string.tostring(wrL * 100, '#') + '%  /  ' + string.tostring(wrS * 100, '#') + '%', bullCol if (wrL + wrS) / 2 >= 0.5 else bearCol)

        ixd: int = bucket(regimeScore, gridX)
        iyd: int = bucket(volNorm, gridY)
        _m, _l, gcf = gridRead(ixd, iyd)
        rowKV(dash, 7, 'Grid Cell / Conf', '[' + string.tostring(ixd) + ',' + string.tostring(iyd) + ']  ' + string.tostring(gcf * 100, '#') + '%', color.new(accentCol, 8) if useGrid else color.new(neutCol, 55))

        rowKV(dash, 8, 'Signals L / S', string.tostring(nLong) + '  /  ' + string.tostring(nShort), color.new(neutCol, 8))

    alertcondition(sigLong, 'ML Supertrenmd [Aslan] Long', 'ML Supertrenmd [Aslan] Long signal on {{ticker}} @ {{close}}')
    alertcondition(sigShort, 'ML Supertrenmd [Aslan] Short', 'ML Supertrenmd [Aslan] Short signal on {{ticker}} @ {{close}}')
    alertcondition(flipUp, 'ML Supertrenmd [Aslan] Flip Up', 'ML Supertrenmd [Aslan] trend flipped bullish on {{ticker}}')
    alertcondition(flipDn, 'ML Supertrenmd [Aslan] Flip Down', 'ML Supertrenmd [Aslan] trend flipped bearish on {{ticker}}')

    if sigLong:
        alert('ML Supertrenmd [Aslan] LONG ' + syminfo.ticker + ' @ ' + string.tostring(close) + ' | band ' + string.tostring(effMult, '#.00') + ' x ATR' + string.tostring(effLen, '#') + ' | regime ' + string.tostring(regimeScore * 100, '#') + '%', alert.freq_once_per_bar_close)
    if sigShort:
        alert('ML Supertrenmd [Aslan] SHORT ' + syminfo.ticker + ' @ ' + string.tostring(close) + ' | band ' + string.tostring(effMult, '#.00') + ' x ATR' + string.tostring(effLen, '#') + ' | regime ' + string.tostring(regimeScore * 100, '#') + '%', alert.freq_once_per_bar_close)
    if flipUp:
        alert('ML Supertrenmd [Aslan] trend flipped bullish ' + syminfo.ticker, alert.freq_once_per_bar_close)
    if flipDn:
        alert('ML Supertrenmd [Aslan] trend flipped bearish ' + syminfo.ticker, alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
