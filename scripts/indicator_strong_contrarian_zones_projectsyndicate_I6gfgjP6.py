"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alertcondition, array, bar_index, box, close, color, format, high, input,
    label, last_bar_index, line, location, low, math, na, nz, open, plotshape, script, shape, size,
    string, syminfo, ta, volume
)
from pynecore.types import Box, Color, Label, Line, NA, Persistent, Series


@udt
class czone:
    dir: int = 1
    top: float = na(float)
    bot: float = na(float)
    mid: float = na(float)
    anchor: float = na(float)
    bornBar: int = na(int)
    lastBar: int = na(int)
    touches: int = 0
    defends: int = 0
    phase: int = 0
    swBar: int = na(int)
    swExt: float = na(float)
    conv: float = 0.0
    convTxt: str = ""
    volSum: float = 0.0
    volN: int = 0
    wickSum: float = 0.0
    wickN: int = 0
    trig: float = 0.0
    state: int = 0
    score: float = 0.0
    bxOut: Box = na(Box)
    bxMid: Box = na(Box)
    bxCore: Box = na(Box)
    ln: Line = na(Line)
    tag: Label = na(Label)
    dead: bool = False


gD: str = "═══ Display ═══"
gS: str = "═══ Swing Detection ═══"
gH: str = "═══ Zone Height ═══"
gCv: str = "═══ Contrarian Conviction ═══"
gW: str = "═══ Conviction Weights ═══"
gSw: str = "═══ Sweep & Reclaim Trigger ═══"
gT: str = "═══ Reclaim Trigger Scoring (0–10) ═══"
gStr: str = "═══ Live Zone Strength ═══"
gC: str = "═══ Style ═══"
gA: str = "═══ Alerts ═══"


@script.indicator("Strong Contrarian Zones", overlay=True, max_labels_count=500, max_boxes_count=500, max_bars_back=2000)
def main(
    mode=input.string("Both", "Zone Side", options=("Both", "Bullish Only", "Bearish Only"), group=gD),
    showLabels=input.bool(True, "Show In-Zone Labels", group=gD),
    labSize=input.string("Normal", "Label Size", options=("Tiny", "Small", "Normal", "Large"), group=gD),
    lookbackBars=input.int(2500, "Lookback (bars, 0 = all loaded)", minval=0, group=gD, tooltip="Only build zones within this many recent bars. 0 = everything loaded."),
    maxZones=input.int(30, "Max Live Zones", minval=2, maxval=120, group=gD, tooltip="Oldest zones recycle past this so loading stays fast."),
    hideOverlap=input.bool(True, "Hide Overlapping Zones", group=gD),
    overlapThr=input.int(25, "Overlap Threshold (%)", minval=1, maxval=100, group=gD),
    leftBars=input.int(10, "Pivot Left", minval=1, group=gS),
    rightBars=input.int(3, "Pivot Right", minval=1, group=gS),
    maxLife=input.int(700, "Max Zone Life (bars)", minval=10, group=gS),
    normHeight=input.bool(True, "Normalize All Zone Heights", group=gH, tooltip="Force every zone to the same thickness, centered on the swing level."),
    heightMode=input.string("ATR Based", "Height Method", options=("ATR Based", "Fixed Percentage"), group=gH),
    heightATR=input.float(0.6, "Zone Height (ATR Mult)", minval=0.05, maxval=10.0, step=0.05, group=gH),
    heightPct=input.float(0.3, "Zone Height (% of Price)", minval=0.01, maxval=5.0, step=0.05, group=gH),
    atrLen=input.int(200, "ATR Length", minval=1, maxval=500, group=gH),
    minConv=input.float(4.5, "Min Conviction To Draw Zone", minval=0, maxval=10, step=0.5, group=gCv, tooltip="A swing pivot only becomes a zone when its birth conviction clears this. Higher = fewer, higher-odds contrarian zones."),
    rsiLen=input.int(14, "RSI Length", minval=2, maxval=100, group=gCv),
    rsiBuyRef=input.int(42, "Oversold Reference (RSI ≤)", minval=5, maxval=50, group=gCv, tooltip="RSI at/under this at a swing LOW = full oversold energy for a buy-dip."),
    rsiSellRef=input.int(58, "Overbought Reference (RSI ≥)", minval=50, maxval=95, group=gCv, tooltip="RSI at/over this at a swing HIGH = full overbought energy for a sell-rip."),
    zLen=input.int(50, "Mean-Reversion Length (z-score)", minval=5, maxval=400, group=gCv),
    zRef=input.float(2.2, "Stretch Reference (z σ)", minval=0.5, maxval=6.0, step=0.1, group=gCv, tooltip="How many σ from the mean counts as a full mean-reversion stretch."),
    bbLenC=input.int(20, "Bollinger Length", minval=2, maxval=200, group=gCv),
    bbMultC=input.float(2.0, "Bollinger StdDev", minval=0.5, maxval=5.0, step=0.1, group=gCv),
    bandRef=input.float(0.5, "Band-Pierce Reference (ATR)", minval=0.05, maxval=4.0, step=0.05, group=gCv, tooltip="How far the wick must pierce beyond the band (in ATR) for full pierce energy."),
    volLen=input.int(20, "Volume Baseline Length", minval=1, group=gCv),
    volClimax=input.float(2.2, "Volume Climax Reference (x)", minval=1.1, maxval=8.0, step=0.1, group=gCv, tooltip="Volume this many times its baseline = full capitulation/blow-off energy."),
    wickRef=input.float(0.45, "Rejection Wick Reference", minval=0.1, maxval=1.0, step=0.05, group=gCv, tooltip="Rejection-wick fraction of the pivot candle for full wick energy."),
    pressLen=input.int(20, "Order-Flow Pressure Lookback", minval=2, maxval=200, group=gCv),
    pressRef=input.float(18.0, "Pressure Reference (% past 50)", minval=2, maxval=50, step=1, group=gCv, tooltip="Absorption: buying pressure this far above 50% at a LOW (or selling below 50% at a HIGH) = full pressure energy."),
    divRef=input.float(8.0, "Divergence Reference (RSI pts)", minval=1, maxval=40, step=1, group=gCv, tooltip="RSI improvement vs the prior same-side pivot for full divergence energy."),
    wRsi=input.float(1.0, "Weight · RSI Extreme", minval=0, maxval=3, step=0.1, group=gW),
    wDiv=input.float(1.3, "Weight · Momentum Divergence", minval=0, maxval=3, step=0.1, group=gW),
    wWick=input.float(1.0, "Weight · Rejection Wick", minval=0, maxval=3, step=0.1, group=gW),
    wVolC=input.float(1.0, "Weight · Volume Climax", minval=0, maxval=3, step=0.1, group=gW),
    wStr=input.float(1.0, "Weight · Mean-Reversion Stretch", minval=0, maxval=3, step=0.1, group=gW),
    wPress=input.float(0.9, "Weight · Order-Flow Pressure", minval=0, maxval=3, step=0.1, group=gW),
    wBand=input.float(0.9, "Weight · Bollinger Pierce", minval=0, maxval=3, step=0.1, group=gW),
    alertRecl=input.bool(True, "Fire Reclaim Alerts", group=gSw, tooltip="Emit an alert when a zone is swept (liquidity grab) then reclaimed (failed break). The reclaim also strengthens the zone regardless of this toggle."),
    minDepth=input.float(0.15, "Min Sweep Depth (ATR)", minval=0.02, maxval=4.0, step=0.01, group=gSw, tooltip="A wick must pierce THIS far beyond a zone border to count as a sweep rather than a normal touch."),
    reclaimWin=input.int(6, "Max Reclaim Window (bars)", minval=1, maxval=40, group=gSw, tooltip="A swept zone must be reclaimed within this many bars. Longer = genuine acceptance (a real break)."),
    reclaimDpt=input.string("Border", "Reclaim Confirmation", options=("Border", "Midline", "Far Border"), group=gSw, tooltip="How far back through the zone price must CLOSE to confirm the reclaim. Deeper = stricter / fewer reclaims."),
    breakAtr=input.float(0.9, "Decisive Break Acceptance (ATR)", minval=0.1, maxval=8.0, step=0.1, group=gSw, tooltip="If a close accepts THIS far beyond the swept border, treat it as a genuine break immediately (no reclaim)."),
    flipBroken=input.bool(True, "Flip Broken Zones (breakers)", group=gSw, tooltip="On a genuine break, keep the zone and flip its side in place for break-and-retest continuation."),
    onlyStrongRec=input.bool(False, "Only Alert Strong Reclaims", group=gSw),
    strongRecThr=input.float(6.5, "Strong Reclaim Threshold", minval=0, maxval=10, step=0.5, group=gSw),
    showTrig=input.bool(False, "Show Reclaim Triggers", group=gSw, tooltip="Plot a small triangle on the reclaim bar. Off by default — enable here if you want the on-chart marker."),
    depthRef=input.float(1.0, "Grab Depth Ref (ATR)", minval=0.2, maxval=6.0, step=0.1, group=gT),
    dispRef=input.float(0.6, "Reclaim Displacement Ref (ATR)", minval=0.1, maxval=4.0, step=0.1, group=gT),
    volRef=input.float(2.0, "Volume Surge Ref (x)", minval=1.1, maxval=8.0, step=0.1, group=gT),
    twDepth=input.float(1.0, "Weight · Grab Depth", minval=0, maxval=3, step=0.1, group=gT),
    twSpeed=input.float(1.0, "Weight · Reclaim Speed", minval=0, maxval=3, step=0.1, group=gT),
    twWick=input.float(1.0, "Weight · Rejection Wick", minval=0, maxval=3, step=0.1, group=gT),
    twVol=input.float(1.0, "Weight · Volume Surge", minval=0, maxval=3, step=0.1, group=gT),
    twConv=input.float(1.2, "Weight · Zone Conviction", minval=0, maxval=3, step=0.1, group=gT),
    twDisp=input.float(1.0, "Weight · Reclaim Displacement", minval=0, maxval=3, step=0.1, group=gT),
    onlyStrong=input.bool(False, "Show Only Strong Zones", group=gStr),
    strongThr=input.float(5.0, "Strong Threshold (score)", minval=0, maxval=10, step=0.5, group=gStr),
    touchNorm=input.float(4.0, "Retests For Full Score", minval=1, step=0.5, group=gStr),
    defendNorm=input.float(2.0, "Defended Reclaims For Full Score", minval=1, step=0.5, group=gStr),
    sWConv=input.float(0.35, "Weight: Birth Conviction", minval=0, maxval=1, step=0.05, group=gStr),
    sWTouch=input.float(0.25, "Weight: Retests", minval=0, maxval=1, step=0.05, group=gStr),
    sWDefend=input.float(0.25, "Weight: Sweep Defense", minval=0, maxval=1, step=0.05, group=gStr),
    sWWick=input.float(0.075, "Weight: Rejection Wick", minval=0, maxval=1, step=0.025, group=gStr),
    sWVol=input.float(0.075, "Weight: Volume", minval=0, maxval=1, step=0.025, group=gStr),
    useDecay=input.bool(True, "Decay Strength While Ignored", group=gStr),
    decayBars=input.int(300, "Full Decay Over (idle bars)", minval=20, maxval=5000, group=gStr),
    decayFloor=input.float(0.65, "Decay Floor", minval=0.1, maxval=1.0, step=0.05, group=gStr),
    supCol=input.color(color.new('#21C997'), "Bullish Zone Tone", group=gC),
    resCol=input.color(color.new('#CC24E2'), "Bearish Zone Tone", group=gC),
    gradFill=input.bool(True, "Gradient (double-shaded) Fill", group=gC),
    fillTransp=input.int(84, "Zone Transparency", minval=50, maxval=96, group=gC),
    showBord=input.bool(True, "Show Zone Borders", group=gC),
    bordTransp=input.int(35, "Border Transparency", minval=0, maxval=100, group=gC),
    showMid=input.bool(True, "Show Zone Midline", group=gC),
    labPlace=input.string("Outside · Right", "Label Placement", options=("Outside · Right", "Inside · Right", "Inside · Center"), group=gC, tooltip="Outside · Right pushes the whole label off the right edge of the shaded zone (cleanest to read). Inside options keep it within the box."),
    labGap=input.int(3, "Label Gap From Zone (bars)", minval=0, maxval=50, group=gC, tooltip="Empty space between the zone's right edge and the label when placed outside."),
    labBgTransp=input.int(22, "Label Background Transparency", minval=0, maxval=100, group=gC),
    labTxtCol=input.color(color.new('#F2F7FF'), "Label Text Colour", group=gC),
    alertProx=input.float(0.1, "Proximity (% of price)", minval=0.0, step=0.01, group=gA),
    instThr=input.float(7.0, "Strong / Institutional Score", minval=0, maxval=10, step=0.5, group=gA)
):
    def f_size(s):
        __block_result__ = na
        __switch__ = s
        if __switch__ == "Tiny":
            __block_result__ = size.tiny
        elif __switch__ == "Small":
            __block_result__ = size.small
        elif __switch__ == "Normal":
            __block_result__ = size.normal
        elif __switch__ == "Large":
            __block_result__ = size.large
        else:
            __block_result__ = size.small
        return __block_result__

    def clamp01(x):
        return math.min(math.max(x, 0.0), 1.0)

    def f_stars(sc):
        return '★★★★★' if sc >= 8 else '★★★★' if sc >= 6.5 else '★★★' if sc >= 5 else '★★' if sc >= 3 else '★' if sc >= 1.5 else '·'

    def f_tier(sc):
        return 'ELITE' if sc >= 8 else 'STRONG' if sc >= 6.5 else 'PRIMED' if sc >= 5 else 'WEAK' if sc >= 3 else 'FORMING'

    def f_ageF(age):
        return 1.0 if not useDecay else math.max(1.0 - (1.0 - decayFloor) * math.min(age / math.max(decayBars, 1), 1.0), decayFloor)

    def f_vis(sc):
        return not onlyStrong or sc >= strongThr

    labStyle = label.style_label_center if labPlace == 'Inside · Center' else label.style_label_right if labPlace == 'Inside · Right' else label.style_label_left

    def f_rangeOverlap(t1: float, b1: float, t2: float, b2: float):
        ov: float = math.min(t1, t2) - math.max(b1, b2)
        minH: float = math.min(t1 - b1, t2 - b2)
        return ov > 0 and minH > 0 and (ov / minH >= overlapThr / 100.0)

    n = bar_index
    atrRaw: Series = math.max(nz(ta.atr(atrLen), ta.cum(high - low) / (n + 1)), syminfo.mintick)
    volBase = ta.sma(volume, volLen)
    rsiV: Series = ta.rsi(close, rsiLen)

    basisMA = ta.sma(close, zLen)
    sdV = ta.stdev(close, zLen)
    zScore: Series = (close - basisMA) / sdV if sdV > 0 else 0.0

    bbBasis = ta.sma(close, bbLenC)
    bbDev = bbMultC * ta.stdev(close, bbLenC)
    bbUpper: Series = bbBasis + bbDev
    bbLower: Series = bbBasis - bbDev

    relVol: Series = volume / volBase if volBase > 0 else 1.0

    bvBar = volume * (close - low) / (high - low) if high > low else volume * 0.5
    svBar = volume * (high - close) / (high - low) if high > low else volume * 0.5
    rollBuy = math.sum(bvBar, pressLen)
    rollSell = math.sum(svBar, pressLen)
    buyPct: Series = rollBuy / (rollBuy + rollSell) * 100.0 if rollBuy + rollSell > 0 else 50.0

    ph = ta.pivothigh(leftBars, rightBars)
    pl = ta.pivotlow(leftBars, rightBars)
    inWindow = lookbackBars <= 0 or last_bar_index - n <= lookbackBars

    zoneH = atrRaw * heightATR if heightMode == 'ATR Based' else close * (heightPct / 100.0)
    supOn = mode == 'Both' or mode == 'Bullish Only'
    resOn = mode == 'Both' or mode == 'Bearish Only'

    def f_fill(dir: int):
        return color.new(supCol if dir == 1 else resCol, fillTransp)

    def f_bord(dir: int):
        return color.new(supCol if dir == 1 else resCol, bordTransp) if showBord else NA(Color)

    def f_tone(dir: int):
        return supCol if dir == 1 else resCol


    zones: Persistent[list[czone]] = array.new(0, NA(czone))

    lastPLp: Persistent[float] = na(float)
    lastPLr: Persistent[float] = na(float)
    lastPHp: Persistent[float] = na(float)
    lastPHr: Persistent[float] = na(float)

    def f_zoneScore(z: czone):
        tF = math.min(z.touches / math.max(touchNorm, 1.0), 1.0)
        dF = math.min(z.defends / math.max(defendNorm, 1.0), 1.0)
        wF = math.min(z.wickSum / z.wickN / atrRaw, 1.0) if z.wickN > 0 else 0.0
        vF = math.min(z.volSum / z.volN / volBase, 1.0) if volBase > 0 and z.volN > 0 else 0.0
        cF = z.conv / 10.0
        wSum = sWConv + sWTouch + sWDefend + sWWick + sWVol
        raw = (cF * sWConv + tF * sWTouch + dF * sWDefend + wF * sWWick + vF * sWVol) / wSum if wSum > 0 else 0.0
        return math.min(math.max(raw * 10.0 * f_ageF(n - z.lastBar), 0.0), 10.0)

    def f_trigScore(depthAtr: float, barsUsed: int, wickFrac: float, volSurge: float, convSc: float, dispAtr: float):
        sD = clamp01(depthAtr / depthRef)
        sSp = clamp01((reclaimWin - barsUsed + 1.0) / reclaimWin)
        sW = clamp01(wickFrac)
        sV = clamp01((volSurge - 1.0) / math.max(volRef - 1.0, 0.1))
        sC = clamp01(convSc / 10.0)
        sDp = clamp01(dispAtr / dispRef)
        wSum = twDepth + twSpeed + twWick + twVol + twConv + twDisp
        raw = (twDepth * sD + twSpeed * sSp + twWick * sW + twVol * sV + twConv * sC + twDisp * sDp) / wSum if wSum > 0 else 0.0
        return math.min(math.max(raw * 10.0, 0.0), 10.0)

    def f_convTxt(sR: float, sDv: float, sW: float, sV: float, sSt: float, sP: float, sB: float):
        t: str = ""
        t = t + ('RSI ' if sR >= 0.5 else '')
        t = t + ('DIV ' if sDv >= 0.5 else '')
        t = t + ('WICK ' if sW >= 0.5 else '')
        t = t + ('VOL ' if sV >= 0.5 else '')
        t = t + ('STR ' if sSt >= 0.5 else '')
        t = t + ('PRS ' if sP >= 0.5 else '')
        t = t + ('BB ' if sB >= 0.5 else '')
        return '—' if t == '' else string.trim(t)

    @method
    def recolor(self: czone, vis: bool):
        tone: Color = f_tone(self.dir)
        sInt: int = cast_int(math.round(self.score))
        opOut: int = math.max(fillTransp - 2, 62) if gradFill else fillTransp
        opMid: int = math.max(fillTransp - 12 - sInt, 50) if gradFill else fillTransp
        opCor: int = math.max(fillTransp - 24 - sInt * 2, 36) if gradFill else fillTransp
        box.set_bgcolor(self.bxOut, color.new(tone, opOut) if vis else na)
        box.set_bgcolor(self.bxMid, color.new(tone, opMid) if vis and gradFill else na)
        box.set_bgcolor(self.bxCore, color.new(tone, opCor) if vis and gradFill else na)
        box.set_border_color(self.bxOut, f_bord(self.dir) if vis else na)
        return line.set_color(self.ln, color.new(tone, 20) if vis and showMid else na)

    @method
    def killZone(self: czone):
        box.delete(self.bxOut)
        box.delete(self.bxMid)
        box.delete(self.bxCore)
        line.delete(self.ln)
        label.delete(self.tag)
        self.dead = True
        return self.dead

    @method
    def refreshGeo(self: czone):
        box.set_right(self.bxOut, n)
        box.set_right(self.bxMid, n)
        box.set_right(self.bxCore, n)
        return line.set_x2(self.ln, n)

    @method
    def refreshTag(self: czone, vis: bool):
        __block_result_1__ = na
        if showLabels:
            __block_result_2__ = na
            if vis:
                dirTag: str = '▲ BUY-DIP' if self.dir == 1 else '▼ SELL-RIP'
                stTag: str = '  · SWEEPING' if self.state == 1 else '  · ⚡RECLAIM ' + string.tostring(math.round(self.trig * 10) / 10) if self.state == 2 else '  · BROKEN' if self.state == 3 else ''
                l1: str = dirTag + '  ' + f_stars(self.score) + '  ' + string.tostring(math.round(self.score * 10) / 10) + '/10  ' + f_tier(self.score)
                l2: str = 'Conv ' + string.tostring(math.round(self.conv * 10) / 10) + '/10  ·  ' + self.convTxt
                l3: str = 'Retest ' + string.tostring(self.touches) + '  ·  Defend ' + string.tostring(self.defends) + (' ⚡' if self.defends > 0 else '') + stTag
                l4: str = '@ ' + string.tostring(self.anchor, format.mintick)
                txt: str = l1 + '\n' + l2 + '\n' + l3 + '\n' + l4
                lx: int = cast_int(math.avg(self.bornBar, n)) if labStyle == label.style_label_center else n + labGap if labStyle == label.style_label_left else n
                if na(self.tag):
                    self.tag = label.new(lx, self.mid, txt, style=labStyle, color=color.new(f_tone(self.dir), labBgTransp), textcolor=labTxtCol, size=f_size(labSize))
                else:
                    label.set_text(self.tag, txt)
                    label.set_xy(self.tag, lx, self.mid)
                label.set_style(self.tag, labStyle)
                label.set_color(self.tag, color.new(f_tone(self.dir), labBgTransp))
                __block_result_2__ = label.set_textcolor(self.tag, labTxtCol)
            elif not na(self.tag):
                __block_result_2__ = label.set_text(self.tag, '')
            __block_result_1__ = __block_result_2__
        return __block_result_1__

    def f_overlapsActive(t: float, b: float):
        hit: bool = False
        if array.size(zones) > 0:
            for z in zones:
                if not z.dead and z.phase != 1 and f_rangeOverlap(t, b, z.top, z.bot):
                    hit = True
                    break
        return hit

    o = rightBars

    if not na(pl):
        rsiP: float = rsiV[o]
        lowP: float = low[o]
        rngP: float = high[o] - low[o]

        bullDiv: bool = not na(lastPLp) and pl < lastPLp and (rsiP > lastPLr)
        sDv: float = clamp01((rsiP - lastPLr) / divRef) if bullDiv else 0.0
        sR: float = clamp01((rsiBuyRef - rsiP) / math.max(rsiBuyRef, 1))
        sSt: float = clamp01(-zScore[o] / zRef)
        sV: float = clamp01((relVol[o] - 1.0) / math.max(volClimax - 1.0, 0.1))
        wF: float = (math.min(open[o], close[o]) - lowP) / rngP if rngP > 0 else 0.0
        sW: float = clamp01(wF / wickRef)
        sP: float = clamp01((buyPct[o] - 50.0) / pressRef)
        sB: float = clamp01((bbLower[o] - lowP) / math.max(bandRef * atrRaw[o], syminfo.mintick))
        wSum: float = wRsi + wDiv + wWick + wVolC + wStr + wPress + wBand
        conv: float = (sR * wRsi + sDv * wDiv + sW * wWick + sV * wVolC + sSt * wStr + sP * wPress + sB * wBand) / wSum * 10.0 if wSum > 0 else 0.0
        if supOn and inWindow and (conv >= minConv):
            nTop: float = pl + zoneH / 2.0 if normHeight else pl + zoneH
            nBot: float = pl - zoneH / 2.0 if normHeight else pl
            if not (hideOverlap and f_overlapsActive(nTop, nBot)):
                z: czone = czone()
                z.dir = 1
                z.top = nTop
                z.bot = nBot
                z.mid = (nTop + nBot) / 2.0
                z.anchor = pl
                z.bornBar = n - o
                z.lastBar = n - o
                z.conv = conv
                z.convTxt = f_convTxt(sR, sDv, sW, sV, sSt, sP, sB)
                z.volSum = nz(volume[o])
                z.volN = 1
                z.wickSum = math.max(math.min(open[o], close[o]) - lowP, 0)
                z.wickN = 1
                z.bxOut = box.new(n - o, nTop, n, nBot, border_width=1)
                z.bxMid = box.new(n - o, z.mid + (nTop - z.mid) * 0.5, n, z.mid + (nBot - z.mid) * 0.5, border_color=na, border_width=0)
                z.bxCore = box.new(n - o, z.mid + (nTop - z.mid) * 0.22, n, z.mid + (nBot - z.mid) * 0.22, border_color=na, border_width=0)
                z.ln = line.new(n - o, z.mid, n, z.mid, width=1, style=line.style_dotted)
                z.score = conv
                recolor(z, True)
                array.push(zones, z)

        lastPLp = pl
        lastPLr = rsiP

    if not na(ph):
        rsiP: float = rsiV[o]
        highP: float = high[o]
        rngP: float = high[o] - low[o]
        bearDiv: bool = not na(lastPHp) and ph > lastPHp and (rsiP < lastPHr)
        sDv: float = clamp01((lastPHr - rsiP) / divRef) if bearDiv else 0.0
        sR: float = clamp01((rsiP - rsiSellRef) / math.max(100 - rsiSellRef, 1))
        sSt: float = clamp01(zScore[o] / zRef)
        sV: float = clamp01((relVol[o] - 1.0) / math.max(volClimax - 1.0, 0.1))
        wF: float = (highP - math.max(open[o], close[o])) / rngP if rngP > 0 else 0.0
        sW: float = clamp01(wF / wickRef)
        sP: float = clamp01((50.0 - buyPct[o]) / pressRef)
        sB: float = clamp01((highP - bbUpper[o]) / math.max(bandRef * atrRaw[o], syminfo.mintick))
        wSum: float = wRsi + wDiv + wWick + wVolC + wStr + wPress + wBand
        conv: float = (sR * wRsi + sDv * wDiv + sW * wWick + sV * wVolC + sSt * wStr + sP * wPress + sB * wBand) / wSum * 10.0 if wSum > 0 else 0.0
        if resOn and inWindow and (conv >= minConv):
            nTop: float = ph + zoneH / 2.0 if normHeight else ph
            nBot: float = ph - zoneH / 2.0 if normHeight else ph - zoneH
            if not (hideOverlap and f_overlapsActive(nTop, nBot)):
                z: czone = czone()
                z.dir = -1
                z.top = nTop
                z.bot = nBot
                z.mid = (nTop + nBot) / 2.0
                z.anchor = ph
                z.bornBar = n - o
                z.lastBar = n - o
                z.conv = conv
                z.convTxt = f_convTxt(sR, sDv, sW, sV, sSt, sP, sB)
                z.volSum = nz(volume[o])
                z.volN = 1
                z.wickSum = math.max(highP - math.max(open[o], close[o]), 0)
                z.wickN = 1
                z.bxOut = box.new(n - o, nTop, n, nBot, border_width=1)
                z.bxMid = box.new(n - o, z.mid + (nTop - z.mid) * 0.5, n, z.mid + (nBot - z.mid) * 0.5, border_color=na, border_width=0)
                z.bxCore = box.new(n - o, z.mid + (nTop - z.mid) * 0.22, n, z.mid + (nBot - z.mid) * 0.22, border_color=na, border_width=0)
                z.ln = line.new(n - o, z.mid, n, z.mid, width=1, style=line.style_dotted)
                z.score = conv
                recolor(z, True)
                array.push(zones, z)
        lastPHp = ph
        lastPHr = rsiP

    while array.size(zones) > maxZones:
        method_call(killZone, array.shift(zones))

    evTouch: bool = False
    evSweep: bool = False
    evBreak: bool = False
    recBull: bool = False
    recBear: bool = False
    lastRecScore: float = na(float)

    reclaimDepthMul = 1.0 if reclaimDpt == 'Far Border' else 0.5 if reclaimDpt == 'Midline' else 0.0

    if array.size(zones) > 0:
        for i in pine_range(0, array.size(zones) - 1):
            z = array.get(zones, i)
            if not z.dead:
                refreshGeo(z)
                z.volSum += nz(volume)
                z.volN += 1

                if n - z.bornBar >= maxLife:
                    killZone(z)
                else:
                    if z.dir == 1:
                        if z.phase == 0:
                            if low <= z.top and low >= z.bot and (close > z.bot):
                                z.touches += 1
                                z.wickSum += math.max(z.top - low, 0)
                                z.wickN += 1
                                z.lastBar = n
                                z.state = 0
                                evTouch = True
                            elif low < z.bot - minDepth * atrRaw:
                                z.phase = 1
                                z.swBar = n
                                z.swExt = low
                                z.state = 1
                                evSweep = True
                        elif z.phase == 1:
                            z.swExt = math.min(z.swExt, low)
                            rcLvl = z.bot + reclaimDepthMul * (z.top - z.bot)
                            accepted = close < z.bot - breakAtr * atrRaw or (n - z.swBar >= reclaimWin and close < z.bot)
                            if close > rcLvl:
                                depthA = (z.bot - z.swExt) / atrRaw
                                wickFr = (math.min(open, close) - low) / math.max(high - low, syminfo.mintick)
                                volSurge = volume / math.max(nz(volBase, volume), 1)
                                dispA = (close - z.bot) / atrRaw
                                rsc = f_trigScore(depthA, n - z.swBar, wickFr, volSurge, z.conv, dispA)
                                if alertRecl and (not onlyStrongRec or rsc >= strongRecThr):
                                    recBull = True
                                    lastRecScore = rsc
                                z.defends += 1
                                z.trig = rsc
                                z.lastBar = n
                                z.phase = 0
                                z.state = 2
                            elif accepted:
                                evBreak = True
                                if flipBroken:
                                    z.dir = -1
                                    z.touches = 0
                                    z.defends = 0
                                    z.wickSum = 0.0
                                    z.wickN = 0
                                    z.phase = 0
                                    z.state = 3
                                    z.lastBar = n
                                else:
                                    killZone(z)
                    else:
                        if z.phase == 0:
                            if high >= z.bot and high <= z.top and (close < z.top):
                                z.touches += 1
                                z.wickSum += math.max(high - z.bot, 0)
                                z.wickN += 1
                                z.lastBar = n
                                z.state = 0
                                evTouch = True
                            elif high > z.top + minDepth * atrRaw:
                                z.phase = 1
                                z.swBar = n
                                z.swExt = high
                                z.state = 1
                                evSweep = True
                        elif z.phase == 1:
                            z.swExt = math.max(z.swExt, high)
                            rcLvl = z.top - reclaimDepthMul * (z.top - z.bot)
                            accepted = close > z.top + breakAtr * atrRaw or (n - z.swBar >= reclaimWin and close > z.top)
                            if close < rcLvl:
                                depthA = (z.swExt - z.top) / atrRaw
                                wickFr = (high - math.max(open, close)) / math.max(high - low, syminfo.mintick)
                                volSurge = volume / math.max(nz(volBase, volume), 1)
                                dispA = (z.top - close) / atrRaw
                                rsc = f_trigScore(depthA, n - z.swBar, wickFr, volSurge, z.conv, dispA)
                                if alertRecl and (not onlyStrongRec or rsc >= strongRecThr):
                                    recBear = True
                                    lastRecScore = rsc
                                z.defends += 1
                                z.trig = rsc
                                z.lastBar = n
                                z.phase = 0
                                z.state = 2
                            elif accepted:
                                evBreak = True
                                if flipBroken:
                                    z.dir = 1
                                    z.touches = 0
                                    z.defends = 0
                                    z.wickSum = 0.0
                                    z.wickN = 0
                                    z.phase = 0
                                    z.state = 3
                                    z.lastBar = n
                                else:
                                    killZone(z)

                    if not z.dead:
                        sc = f_zoneScore(z)
                        z.score = sc
                        vis = f_vis(sc) or z.phase == 1 or z.state == 2
                        box.set_top(z.bxOut, z.top)
                        box.set_bottom(z.bxOut, z.bot)
                        box.set_top(z.bxMid, z.mid + (z.top - z.mid) * 0.5)
                        box.set_bottom(z.bxMid, z.mid + (z.bot - z.mid) * 0.5)
                        box.set_top(z.bxCore, z.mid + (z.top - z.mid) * 0.22)
                        box.set_bottom(z.bxCore, z.mid + (z.bot - z.mid) * 0.22)
                        line.set_y1(z.ln, z.mid)
                        line.set_y2(z.ln, z.mid)
                        recolor(z, vis)
                        refreshTag(z, vis)

    if array.size(zones) > 0:
        for i in pine_range(array.size(zones) - 1, 0):
            if array.get(zones, i).dead:
                array.remove(zones, i)

    nearBull: bool = False
    nearBear: bool = False
    nearStrongBull: bool = False
    nearStrongBear: bool = False
    prox: float = close * alertProx / 100.0

    if array.size(zones) > 0:
        for z in zones:
            if not z.dead and (f_vis(z.score) or z.phase == 1) and (math.abs(close - z.mid) <= prox):
                if z.dir == 1:
                    nearBull = True
                    nearStrongBull = nearStrongBull or z.score >= instThr
                else:
                    nearBear = True
                    nearStrongBear = nearStrongBear or z.score >= instThr

    plotshape(showTrig and recBull, title='Bullish Reclaim', style=shape.triangleup, location=location.belowbar, color=supCol, size=size.small, text='RECLAIM', textcolor=supCol)
    plotshape(showTrig and recBear, title='Bearish Reclaim', style=shape.triangledown, location=location.abovebar, color=resCol, size=size.small, text='RECLAIM', textcolor=resCol)

    alertcondition(nearBull, 'Bullish Zone Proximity', 'Price approaching a bullish contrarian zone.')
    alertcondition(nearBear, 'Bearish Zone Proximity', 'Price approaching a bearish contrarian zone.')
    alertcondition(nearStrongBull, 'Strong Bullish Zone Proximity', 'Price approaching a strong bullish contrarian zone.')
    alertcondition(nearStrongBear, 'Strong Bearish Zone Proximity', 'Price approaching a strong bearish contrarian zone.')
    alertcondition(evTouch, 'Zone Touch / Retest', 'Price tested and held a contrarian zone.')
    alertcondition(evSweep, 'Zone Sweep (liquidity grab)', 'Price swept beyond a zone — watch for a reclaim.')
    alertcondition(evBreak, 'Zone Break (accepted)', 'A zone was genuinely broken and flipped.')
    alertcondition(recBull, 'Bullish Reclaim', 'Sweep below a contrarian zone was reclaimed — bullish reversal.')
    alertcondition(recBear, 'Bearish Reclaim', 'Sweep above a contrarian zone was reclaimed — bearish reversal.')
    alertcondition(recBull or recBear, 'Any Reclaim', 'A contrarian sweep-and-reclaim fired.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)