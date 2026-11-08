"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barcolor, barstate, chart,
    close, color, display, high, hour, input, label, line, low, math, minute, na, nz, open, plot,
    position, request, runtime, script, size, string, syminfo, ta, table, text, time, timeframe,
    volume, yloc
)
from pynecore.types import Color, Line, Persistent, Series, Table

gD: str = "Delta"
gC: str = "Calibration"
gL: str = "Look"
gE: str = "Candles"
gA: str = "Alerts"
gS: str = "Scale"
gP: str = "Panel"


@script.indicator("Delta Flow Ribbon [AlgoNorth]", overlay=False, precision=2, max_bars_back=1000, max_lines_count=500, max_labels_count=500, calc_bars_count=10000)
def main(
    deltaSrc=input.string("Intrabar", "Delta source", options=("Intrabar", "Bar shape"), group=gD, tooltip="How each bar's volume delta is estimated. Intrabar signs the volume of the smaller bars inside each chart bar by the direction price moved, the way an intrabar volume-delta reading is normally built. Bar shape uses where the close sits in the range and is the fallback; the panel shows which is in use. On symbols whose feed reports tick counts rather than traded size — most spot forex and CFD feeds — the reading is a net tick count, not a volume delta."),
    ltfMode=input.string("Auto", "Intrabar timeframe", options=("Auto", "1", "5", "15"), group=gD, tooltip="The smaller timeframe read inside each chart bar. It must be smaller than the chart's own timeframe; if it is not, the bar-shape fallback is used and the panel says so. Auto uses 1-minute bars on intraday charts up to an hour, 5-minute bars above that, hourly bars on daily charts and daily bars on weekly and monthly charts."),
    calMode=input.string("Time of day", "Calibrate against", options=("Time of day", "Recent bars"), group=gC, tooltip="What each bar's flow is compared with. Time of day compares it with the same time slot on previous sessions, so the open, the cash session and the overnight each have their own idea of normal and a busy open never swamps the rest of the day. Recent bars compares it with a rolling window of the last few hundred bars instead. Time of day needs an intraday chart of four hours or less; on other charts the recent-bars window is used and the panel header says so."),
    todDays=input.int(20, "Sessions per time slot", minval=3, maxval=100, group=gC, tooltip="How many previous sessions set what is normal for each time slot. More sessions give a steadier normal; fewer adapt faster to a change in the market. Time of day needs an intraday chart of four hours or less; on longer timeframes this setting has no effect."),
    calLen=input.int(300, "Recent bars window", minval=50, maxval=1000, group=gC, tooltip="How many recent bars set what is normal when calibrating against recent bars, and whenever time-of-day calibration is unavailable: on charts above four hours, and while a time slot's own history builds up."),
    quietLvl=input.float(0.6, "Quiet below (× normal volume)", minval=0.1, maxval=1.5, step=0.05, group=gC, tooltip="When a bar trades less than this multiple of its normal volume, both ribbons are eased towards 1.0× in proportion, so thin trade cannot produce a dramatic swing."),
    fastLen=input.int(5, "Fastest strand", minval=2, maxval=60, group=gL, tooltip="Smoothing length of the innermost, brightest strand of each ribbon. Lower values make the ribbon react faster and fan wider on turns; higher values make it calmer."),
    spanLen=input.int(25, "Strand span", minval=2, maxval=120, group=gL, tooltip="How much slower the outermost strand is than the fastest one. Wider spans make the fan open further when flow is changing and take longer to close."),
    passes=input.int(3, "Smoothing passes", minval=1, maxval=3, group=gL, tooltip="How many times each strand is smoothed. Each pass is an exponential average: one pass keeps most of the bar-to-bar bump, two passes remove the jitter, and three — the default — give the smoothest, slowest fan."),
    strands=input.int(14, "Strands per ribbon", minval=6, maxval=14, group=gL, tooltip="Number of strands drawn in each ribbon. More strands give a finer, denser texture. Fewer strands lighten both the drawing and the calculation on slower machines."),
    cPrs=input.color(color.new('#F2456B'), "Downside flow", group=gL, tooltip="Colour of the ribbon showing downside flow: negative volume delta as a multiple of what is normal for this bar under the calibration in use — the panel says which. Each side is measured up to 5× normal; anything heavier reads as 5×."),
    cMov=input.color(color.new('#2AD4E8'), "Upside flow", group=gL, tooltip="Colour of the ribbon showing upside flow: positive volume delta as a multiple of what is normal for this bar under the calibration in use. Each side is measured up to 5× normal; anything heavier reads as 5×."),
    showSurge=input.bool(True, "Colour flow surges", group=gE, tooltip="Colours candles when net flow over three bars runs well above normal in one direction and price travels with it. Each candle takes the Upside candles or Downside candles colour set below."),
    surgeLvl=input.float(2.0, "Surge at least (× normal net flow)", minval=1.0, maxval=6.0, step=0.1, group=gE, tooltip="How strong net flow over three bars must be, as a multiple of normal under the calibration in use, to count as a surge."),
    showAbs=input.bool(True, "Colour absorbed flow", group=gE, tooltip="Colours candles in a lighter shade of the flow's colour when heavy one-way flow went in and price travelled far less in that direction than the flow would normally carry it. Flow meeting size on the other side is one common reason; the script measures only the mismatch, not the order book."),
    absFlow=input.float(1.5, "Absorbed flow at least (× normal net flow)", minval=0.5, maxval=6.0, step=0.1, group=gE, tooltip="How heavy net flow over three bars must be before its lack of movement counts as absorption."),
    lowResp=input.float(0.35, "Price response at or below (× expected)", minval=-2.0, maxval=0.9, step=0.05, group=gE, tooltip="How little price must travel in the flow's direction, compared with what that flow would normally produce, for the flow to count as absorbed. Zero means price finished where it started; a negative value means price finished in the opposite direction to the flow, which is a reversal rather than absorption."),
    expB=input.float(0.5, "Flow-to-movement exponent", minval=0.2, maxval=1.0, step=0.05, group=gE, tooltip="How much travel a given amount of flow is expected to produce. Price does not usually travel twice as far for twice the flow, so 0.5 expects travel to grow with roughly the square root of flow. Raise it to expect more travel from heavy flow, which makes absorbed flow trigger more often; lower it to expect less."),
    showGlow=input.bool(False, "Glow on coloured candles", group=gE, tooltip="Draws a soft glow around each coloured candle, in the candle's own colour, so surges and absorbed flow stand out on a busy chart. The most recent 70 or so coloured candles carry the glow."),
    glowW=input.int(18, "Glow width", minval=4, maxval=40, group=gE, tooltip="How wide the glow spreads around each coloured candle, in pixels. Match it roughly to your candle width: wider when zoomed in, narrower when zoomed out."),
    showArr=input.bool(True, "Arrows on coloured candles", group=gE, tooltip="Places a small arrow on coloured candles, in that candle's own colour. The arrow is hollow on absorbed-flow candles. Arrow placement below controls whether every candle is marked or only the first of each run."),
    arrMode=input.string("First of each run", "Arrow placement", options=("First of each run", "Every coloured candle"), group=gE, tooltip="First of each run places one arrow where a surge or absorbed-flow run begins, so a long run shows a single marker. Every coloured candle marks each candle in the run. A new arrow also appears when the run changes side, or changes between surge and absorbed flow."),
    arrSize=input.string("Normal", "Arrow size", options=("Tiny", "Small", "Normal", "Large"), group=gE, tooltip="Size of the arrows on coloured candles. Normal and Large are easier to see when zoomed out."),
    cUpC=input.color(color.new('#2AD4E8'), "Upside candles", group=gE, tooltip="Colour of upside-flow candles and their arrows. Kept separate from the ribbon colours so candles can be tuned to stand out against your own candle colours without changing the ribbon."),
    cDnC=input.color(color.new('#FF5FD2'), "Downside candles", group=gE, tooltip="Colour of downside-flow candles and their arrows. The default is a pink chosen to stand apart from standard red candles; change it if your chart uses different candle colours."),
    absShade=input.int(35, "Absorbed shade lightness", minval=20, maxval=85, group=gE, tooltip="How much lighter absorbed-flow candles are than surge candles, in percent, so the two can be told apart at a glance. On a light chart background they are darkened by the same amount instead."),
    alCtl=input.bool(True, "Alert on control change", group=gA, tooltip="Fires once per bar close when the two core lines cross. Create the alert with the named 'Control change' condition, or with 'Any alert() function call' to receive all three in one alert."),
    alSurge=input.bool(True, "Alert on flow surge", group=gA, tooltip="Fires once per bar close when a flow surge begins. Create the alert with the named 'Flow surge' condition, or with 'Any alert() function call' to receive all three in one alert."),
    alAbs=input.bool(True, "Alert on absorbed flow", group=gA, tooltip="Fires once per bar close when absorbed flow begins. Create the alert with the named 'Absorbed flow' condition, or with 'Any alert() function call' to receive all three in one alert."),
    scaleMode=input.string("Soft", "Vertical scale", options=("Soft", "Log", "None"), group=gS, tooltip="How the ribbons are placed on the pane's vertical axis. Soft eases values towards a limit one knee away from 1.0×, Log keeps large multiples growing but slowly, and None draws the raw multiple and ignores the knee. Both ribbons are multiples of normal, and 1.0× always sits at 1.0."),
    knee=input.float(1.0, "Compression knee", minval=0.1, maxval=5.0, step=0.1, group=gS, tooltip="How hard readings away from 1.0× are squeezed. At this distance from 1.0× a reading is drawn at about half its true distance, and further readings are squeezed harder. Raise it if the ribbons look flattened, lower it if a few spikes dominate. Has no effect when the vertical scale is None."),
    showPanel=input.bool(True, "Show panel", group=gP, tooltip="Turns the readout off if you want the ribbons alone."),
    panelSize=input.string("Compact", "Panel size", options=("Compact", "Full"), group=gP, tooltip="Compact shows who is in control, the last three bars of flow and the last event in four small rows. Full adds the raw readings, the delta source and the event counts."),
    panelPane=input.string("Price chart", "Panel pane", options=("Price chart", "Indicator pane"), group=gP, tooltip="Where the panel is drawn. Price chart puts it on the main candles; Indicator pane keeps it beside the ribbons."),
    panelPos=input.string("Top right", "Panel position", options=("Top left", "Top centre", "Top right", "Middle left", "Middle centre", "Middle right", "Bottom left", "Bottom centre", "Bottom right"), group=gP, tooltip="Move the panel if it overlaps another script or the candles. Each loaded copy can sit in its own spot.")
):
    cumVol = ta.cum(nz(volume))
    if barstate.islast and cumVol == 0:
        runtime.error('This symbol has no volume data, so delta cannot be estimated.')

    rng = high - low
    barShape = volume * (close - low - (high - close)) / rng if rng > 0 else 0.0

    def f_tick():
        dir: Persistent[float] = 0.0
        ch = close - nz(close[1], open)
        dir = 1.0 if ch > 0 else -1.0 if ch < 0 else dir
        return dir * nz(volume)

    tfMin = timeframe.in_seconds() / 60.0
    ltfAuto = ('1' if tfMin <= 60 else '5') if timeframe.isintraday else '60' if timeframe.isdaily else 'D'
    ltfUse = ltfAuto if ltfMode == 'Auto' else ltfMode
    ltfOk = deltaSrc == 'Intrabar' and (not timeframe.isseconds) and (not timeframe.isintraday or timeframe.multiplier > string.tonumber(ltfUse))
    ltfReqTf = ltfUse if ltfOk else timeframe.period
    ltfArr = request.security_lower_tf(syminfo.tickerid, ltfReqTf, f_tick(), ignore_invalid_timeframe=True)
    ltfDelta = array.sum(ltfArr) if ltfOk and (not na(ltfArr)) and (array.size(ltfArr) > 0) else na

    useIntra: Series = not na(ltfDelta)
    delta = ltfDelta if useIntra else barShape
    upF = math.max(delta, 0.0)
    dnF = math.max(-delta, 0.0)
    chg = close - nz(close[1], open)

    intraFrom: Persistent[int] = na(int)
    fbAfter: Persistent[int] = 0
    if useIntra and na(intraFrom):
        intraFrom = time
    if not na(intraFrom) and (not useIntra) and barstate.isconfirmed:
        fbAfter += 1
    intraSeen = not na(intraFrom)

    todOk = timeframe.isintraday and (not timeframe.isseconds) and (tfMin <= 240)
    nSlot = cast_int(math.ceil(1440.0 / tfMin)) if todOk else 1
    slot = cast_int(math.floor((hour(time, syminfo.timezone) * 60 + minute(time, syminfo.timezone)) / tfMin)) % nSlot if todOk else 0
    aTd = 2.0 / (todDays + 1.0)

    sV: Persistent[list[float]] = array.new_float(nSlot, na)
    sU: Persistent[list[float]] = array.new_float(nSlot, na)
    sD: Persistent[list[float]] = array.new_float(nSlot, na)
    sC: Persistent[list[float]] = array.new_float(nSlot, na)
    sN: Persistent[list[int]] = array.new_int(nSlot, 0)
    if useIntra and intraFrom == time and barstate.isconfirmed:
        array.fill(sV, na)
        array.fill(sU, na)
        array.fill(sD, na)
        array.fill(sC, na)
        array.fill(sN, 0)

    pV = array.get(sV, slot)
    pU = array.get(sU, slot)
    pD = array.get(sD, slot)
    pC = array.get(sC, slot)
    pN = array.get(sN, slot)

    estSw = bar_index > 0 and useIntra != useIntra[1]
    aC = 2.0 / (calLen + 1.0)
    rbV: Persistent[float] = na(float)
    rbU: Persistent[float] = na(float)
    rbD: Persistent[float] = na(float)
    rbC: Persistent[float] = na(float)
    rbN: Persistent[int] = 0
    if estSw:
        rbV = na
        rbU = na
        rbD = na
        rbC = na
        rbN = 0
    rbV = volume if na(rbV) else rbV + (volume - rbV) * aC
    rbU = upF if na(rbU) else rbU + (upF - rbU) * aC
    rbD = dnF if na(rbD) else rbD + (dnF - rbD) * aC
    rbC = math.abs(chg) if na(rbC) else rbC + (math.abs(chg) - rbC) * aC
    rbN = rbN + 1
    rbReady = rbN >= math.max(cast_int(calLen / 4), 1)

    useTod = calMode == 'Time of day' and todOk and (pN >= math.min(todDays, 10)) and (pV > 0) and (pU > 0) and (pD > 0) and (pC > 0) and (useIntra == intraSeen)
    uV = pV if useTod else rbV
    uU = pU if useTod else rbU
    uD = pD if useTod else rbD
    uC = pC if useTod else rbC
    baseOk = useTod or rbReady

    aEff = math.max(aTd, 1.0 / (pN + 1))
    if barstate.isconfirmed and useIntra == intraSeen:
        array.set(sV, slot, volume if na(pV) else pV + (volume - pV) * aEff)
        array.set(sU, slot, upF if na(pU) else pU + (upF - pU) * aEff)
        array.set(sD, slot, dnF if na(pD) else pD + (dnF - pD) * aEff)
        array.set(sC, slot, math.abs(chg) if na(pC) else pC + (math.abs(chg) - pC) * aEff)
        array.set(sN, slot, pN + 1)

    volX = volume / uV if uV > 0 else na
    upX = math.min(upF / uU, 5.0) if baseOk and uU > 0 else na
    dnX = math.min(dnF / uD, 5.0) if baseOk and uD > 0 else na

    wQ = 1.0 if na(volX) else math.min(1.0, volX / quietLvl)
    effN = na if na(upX) else 1.0 + (upX - 1.0) * wQ
    prsN = na if na(dnX) else 1.0 + (dnX - 1.0) * wQ

    uAbs = uU + uD
    dEma = ta.ema(delta, 3)
    netS = dEma / uAbs * wQ if uAbs > 0 else na
    movS = ta.ema(chg, 3)
    flowA = math.abs(nz(netS))
    dirS = 1.0 if nz(netS) >= 0 else -1.0
    respS = movS / uC * dirS if uC > 0 else na
    expS = math.pow(math.max(flowA, 0.05), expB)
    respX = na if na(respS) else respS / expS
    absorbed: Series = not na(netS) and (not na(respX)) and (flowA >= absFlow) and (respX <= lowResp)
    surge: Series = not na(netS) and flowA >= surgeLvl and (not absorbed) and (nz(respX, 1.0) > lowResp)
    flowUp = nz(netS) > 0

    eM1: Persistent[list[float]] = array.new_float(14, na)
    eM2: Persistent[list[float]] = array.new_float(14, na)
    eM3: Persistent[list[float]] = array.new_float(14, na)
    eP1: Persistent[list[float]] = array.new_float(14, na)
    eP2: Persistent[list[float]] = array.new_float(14, na)
    eP3: Persistent[list[float]] = array.new_float(14, na)
    dM: Persistent[list[float]] = array.new_float(14, na)
    dP: Persistent[list[float]] = array.new_float(14, na)

    ratio = (fastLen + spanLen) / math.max(fastLen, 1.0)
    for k in pine_range(0, strands - 1):
        len = fastLen * math.pow(ratio, k / 13.0)
        a = 2.0 / (len + 1.0)
        if not na(effN):
            p1 = array.get(eM1, k)
            v1 = effN if na(p1) else p1 + (effN - p1) * a
            v2: float = na(float)
            v3: float = na(float)
            vS = v1
            if passes >= 2:
                p2 = array.get(eM2, k)
                v2 = v1 if na(p2) else p2 + (v1 - p2) * a
                vS = v2
                if passes == 3:
                    p3 = array.get(eM3, k)
                    v3 = v2 if na(p3) else p3 + (v2 - p3) * a
                    vS = v3
            array.set(dM, k, vS)
            if barstate.isconfirmed:
                array.set(eM1, k, v1)
                if passes >= 2:
                    array.set(eM2, k, v2)
                    if passes == 3:
                        array.set(eM3, k, v3)
        if not na(prsN):
            q1 = array.get(eP1, k)
            w1 = prsN if na(q1) else q1 + (prsN - q1) * a
            w2: float = na(float)
            w3: float = na(float)
            wS = w1
            if passes >= 2:
                q2 = array.get(eP2, k)
                w2 = w1 if na(q2) else q2 + (w1 - q2) * a
                wS = w2
                if passes == 3:
                    q3 = array.get(eP3, k)
                    w3 = w2 if na(q3) else q3 + (w2 - q3) * a
                    wS = w3
            array.set(dP, k, wS)
            if barstate.isconfirmed:
                array.set(eP1, k, w1)
                if passes >= 2:
                    array.set(eP2, k, w2)
                    if passes == 3:
                        array.set(eP3, k, w3)

    def f_y(v):
        d = v - 1.0
        c = d / (1.0 + math.abs(d) / knee) if scaleMode == 'Soft' else math.sign(d) * knee * math.log(1.0 + math.abs(d) / knee) if scaleMode == 'Log' else d
        return na if na(v) else 1.0 + c

    def f_m(k):
        return f_y(array.get(dM, k)) if k < strands else na

    def f_p(k):
        return f_y(array.get(dP, k)) if k < strands else na

    mov0 = array.get(dM, 0)
    prs0 = array.get(dP, 0)

    bgLum = 0.2126 * color.r(chart.bg_color) + 0.7152 * color.g(chart.bg_color) + 0.0722 * color.b(chart.bg_color)
    isLight = bgLum > 140
    hiT = 0.0 if isLight else 255.0
    loT = 255.0 if isLight else 0.0

    def f_in(c, f):
        return color.rgb(color.r(c) + (hiT - color.r(c)) * f, color.g(c) + (hiT - color.g(c)) * f, color.b(c) + (hiT - color.b(c)) * f)

    def f_out(c, f):
        return color.rgb(color.r(c) + (loT - color.r(c)) * f, color.g(c) + (loT - color.g(c)) * f, color.b(c) + (loT - color.b(c)) * f)

    coreP = f_in(cPrs, 0.85)
    coreM = f_in(cMov, 0.85)

    cP01 = color.new(f_in(cPrs, 0.5969), 9)
    cP02 = color.new(f_in(cPrs, 0.4738), 14)
    cP03 = color.new(f_in(cPrs, 0.3506), 18)
    cP04 = color.new(f_in(cPrs, 0.2282), 23)
    cP05 = color.new(f_in(cPrs, 0.1051), 28)
    cP06 = color.new(f_out(cPrs, 0.014), 33)
    cP07 = color.new(f_out(cPrs, 0.1), 37)
    cP08 = color.new(f_out(cPrs, 0.186), 42)
    cP09 = color.new(f_out(cPrs, 0.273), 47)
    cP10 = color.new(f_out(cPrs, 0.36), 52)
    cP11 = color.new(f_out(cPrs, 0.447), 56)
    cP12 = color.new(f_out(cPrs, 0.533), 61)
    cP13 = color.new(f_out(cPrs, 0.62), 66)

    cM01 = color.new(f_in(cMov, 0.5969), 9)
    cM02 = color.new(f_in(cMov, 0.4738), 14)
    cM03 = color.new(f_in(cMov, 0.3506), 18)
    cM04 = color.new(f_in(cMov, 0.2282), 23)
    cM05 = color.new(f_in(cMov, 0.1051), 28)
    cM06 = color.new(f_out(cMov, 0.014), 33)
    cM07 = color.new(f_out(cMov, 0.1), 37)
    cM08 = color.new(f_out(cMov, 0.186), 42)
    cM09 = color.new(f_out(cMov, 0.273), 47)
    cM10 = color.new(f_out(cMov, 0.36), 52)
    cM11 = color.new(f_out(cMov, 0.447), 56)
    cM12 = color.new(f_out(cMov, 0.533), 61)
    cM13 = color.new(f_out(cMov, 0.62), 66)

    pnlTx: Color = chart.fg_color
    cMovV = f_in(cMov, 0.35 if isLight else 0.0)
    cPrsV = f_in(cPrs, 0.35 if isLight else 0.0)
    cUpV = f_in(cUpC, 0.35 if isLight else 0.0)
    cDnV = f_in(cDnC, 0.35 if isLight else 0.0)

    plot(f_p(13), 'Downside s13', color=cP13, linewidth=1, display=display.pane)
    plot(f_p(12), 'Downside s12', color=cP12, linewidth=1, display=display.pane)
    plot(f_p(11), 'Downside s11', color=cP11, linewidth=1, display=display.pane)
    plot(f_p(10), 'Downside s10', color=cP10, linewidth=1, display=display.pane)
    plot(f_p(9), 'Downside s9', color=cP09, linewidth=1, display=display.pane)
    plot(f_p(8), 'Downside s8', color=cP08, linewidth=1, display=display.pane)
    plot(f_p(7), 'Downside s7', color=cP07, linewidth=1, display=display.pane)
    plot(f_p(6), 'Downside s6', color=cP06, linewidth=1, display=display.pane)
    plot(f_p(5), 'Downside s5', color=cP05, linewidth=1, display=display.pane)
    plot(f_p(4), 'Downside s4', color=cP04, linewidth=1, display=display.pane)
    plot(f_p(3), 'Downside s3', color=cP03, linewidth=1, display=display.pane)
    plot(f_p(2), 'Downside s2', color=cP02, linewidth=1, display=display.pane)
    plot(f_p(1), 'Downside s1', color=cP01, linewidth=1, display=display.pane)

    plot(f_m(13), 'Upside s13', color=cM13, linewidth=1, display=display.pane)
    plot(f_m(12), 'Upside s12', color=cM12, linewidth=1, display=display.pane)
    plot(f_m(11), 'Upside s11', color=cM11, linewidth=1, display=display.pane)
    plot(f_m(10), 'Upside s10', color=cM10, linewidth=1, display=display.pane)
    plot(f_m(9), 'Upside s9', color=cM09, linewidth=1, display=display.pane)
    plot(f_m(8), 'Upside s8', color=cM08, linewidth=1, display=display.pane)
    plot(f_m(7), 'Upside s7', color=cM07, linewidth=1, display=display.pane)
    plot(f_m(6), 'Upside s6', color=cM06, linewidth=1, display=display.pane)
    plot(f_m(5), 'Upside s5', color=cM05, linewidth=1, display=display.pane)
    plot(f_m(4), 'Upside s4', color=cM04, linewidth=1, display=display.pane)
    plot(f_m(3), 'Upside s3', color=cM03, linewidth=1, display=display.pane)
    plot(f_m(2), 'Upside s2', color=cM02, linewidth=1, display=display.pane)
    plot(f_m(1), 'Upside s1', color=cM01, linewidth=1, display=display.pane)

    plot(f_y(prs0), 'Downside core', color=coreP, linewidth=2, display=display.pane)
    plot(f_y(mov0), 'Upside core', color=coreM, linewidth=2, display=display.pane)

    upLeads = ta.crossover(mov0, prs0)
    dnLeads = ta.crossunder(mov0, prs0)
    anyCross = upLeads or dnLeads

    nCross: Persistent[int] = 0
    lastCross: Persistent[int] = na(int)
    if anyCross and barstate.isconfirmed:
        nCross += 1
        lastCross = bar_index

    def f_light(c):
        return f_in(c, absShade / 100.0)

    cUpA = f_light(cUpC)
    cDnA = f_light(cDnC)

    barCol = (cUpA if flowUp else cDnA) if showAbs and absorbed else (cUpV if flowUp else cDnV) if showSurge and surge else na
    barcolor(barCol, title='Flow candles')

    glowPad = ta.atr(14) * 0.18
    glowL: Persistent[list[Line]] = array.new_line()
    def f_glow(c, wf, tr, padF):
        return line.new(bar_index, high + glowPad * padF, bar_index, low - glowPad * padF, color=color.new(c, tr), width=math.max(cast_int(glowW * wf), 1), force_overlay=True)

    if showGlow and (not na(barCol)):
        array.push(glowL, f_glow(barCol, 1.0, 95, 1.0))
        array.push(glowL, f_glow(barCol, 0.8, 92, 0.75))
        array.push(glowL, f_glow(barCol, 0.62, 88, 0.5))
        array.push(glowL, f_glow(barCol, 0.46, 82, 0.3))
        array.push(glowL, f_glow(barCol, 0.32, 74, 0.12))
        array.push(glowL, f_glow(barCol, 0.2, 62, 0.0))
        hot = f_in(barCol, 0.45)
        array.push(glowL, line.new(bar_index, math.max(open, close), bar_index, math.min(open, close), color=color.new(hot, 35), width=math.max(cast_int(glowW * 0.1), 1), force_overlay=True))
        while array.size(glowL) > 490:
            line.delete(array.shift(glowL))

    arrSz = size.tiny if arrSize == 'Tiny' else size.small if arrSize == 'Small' else size.normal if arrSize == 'Normal' else size.large
    evKey: Series = 0 if na(barCol) else (2 if absorbed else 1) * (1 if flowUp else -1)
    evStart = evKey != 0 and evKey != nz(evKey[1])
    if showArr and (not na(barCol)) and (arrMode == 'Every coloured candle' or evStart):
        arrTx = ('△' if flowUp else '▽') if absorbed else '▲' if flowUp else '▼'
        if flowUp:
            label.new(bar_index, high, arrTx, yloc=yloc.abovebar, style=label.style_none, textcolor=barCol, size=arrSz, force_overlay=True)
        else:
            label.new(bar_index, low, arrTx, yloc=yloc.belowbar, style=label.style_none, textcolor=barCol, size=arrSz, force_overlay=True)

    nSurge: Persistent[int] = 0
    lastSurge: Persistent[int] = na(int)
    lastSurUp: Persistent[bool] = False
    nAbs: Persistent[int] = 0
    lastAbs: Persistent[int] = na(int)
    lastAbsUp: Persistent[bool] = False
    if barstate.isconfirmed:
        if surge:
            if not surge[1]:
                nSurge += 1
            lastSurge = bar_index
            lastSurUp = flowUp
        if absorbed:
            if not absorbed[1]:
                nAbs += 1
            lastAbs = bar_index
            lastAbsUp = flowUp

    def f_pos(s):
        return position.top_left if s == 'Top left' else position.top_center if s == 'Top centre' else position.top_right if s == 'Top right' else position.middle_left if s == 'Middle left' else position.middle_center if s == 'Middle centre' else position.middle_right if s == 'Middle right' else position.bottom_left if s == 'Bottom left' else position.bottom_center if s == 'Bottom centre' else position.bottom_right

    def f_bars(n):
        return string.tostring(n) + (' bar' if n == 1 else ' bars')

    def f_ago(b):
        return 'none yet' if na(b) else f_bars(bar_index - b) + ' ago'

    tbOver: Persistent[Table] = table.new(f_pos(panelPos), 2, 13, border_width=1, frame_width=1, frame_color=color.new(chart.fg_color, 65), force_overlay=True)
    tbPane: Persistent[Table] = table.new(f_pos(panelPos), 2, 13, border_width=1, frame_width=1, frame_color=color.new(chart.fg_color, 65))
    tb: Persistent[Table] = tbOver if panelPane == 'Price chart' else tbPane

    def f_row(r, k, v, cK, cV, bgT):
        bg = color.new(chart.bg_color, bgT)
        table.cell(tb, 0, r, k, text_size=size.small, text_color=cK, text_halign=text.align_left, bgcolor=bg)
        return table.cell(tb, 1, r, v, text_size=size.small, text_color=cV, text_halign=text.align_right, bgcolor=bg)

    upTop = not na(mov0) and (not na(prs0)) and (mov0 > prs0)
    slowLen = math.round(fastLen * math.pow(ratio, (strands - 1) / 13.0))
    tickVol = syminfo.type == 'forex' or syminfo.type == 'cfd'
    evLive = (surge or absorbed) and barstate.isrealtime

    if showPanel and barstate.islast and (panelSize == 'Compact'):
        grey = color.new(chart.fg_color, 25)
        dimc = color.new(chart.fg_color, 50)
        hdrC = 'DELTA FLOW RIBBON  ·  ' + ('intrabar ' + ltfUse + ('' if na(intraFrom) else ' since ' + string.format_time(intraFrom, 'yyyy-MM-dd', syminfo.timezone)) if useIntra else 'bar shape') + '  ·  ' + ('tod ' + string.tostring(todDays) + ' sessions' if useTod else string.tostring(calLen) + ' bars')
        table.cell(tb, 0, 0, hdrC, text_size=size.small, text_color=pnlTx, text_halign=text.align_left, bgcolor=color.new(chart.bg_color, 0))
        table.cell(tb, 1, 0, syminfo.ticker + ' ' + timeframe.period, text_size=size.small, text_color=grey, text_halign=text.align_right, bgcolor=color.new(chart.bg_color, 0))
        ctlC = '—' if na(mov0) or na(prs0) else ('upside' if upTop else 'downside') + '  ·  ' + ('this bar' if anyCross else 'none yet' if na(lastCross) else 'for ' + f_bars(bar_index - lastCross))
        netC = '—' if na(netS) else 'balanced' if math.abs(netS) < 0.25 else ('upside ' if netS > 0 else 'downside ') + string.tostring(math.abs(netS), '0.0') + '×'
        lastIsAbs = not na(lastAbs) and (na(lastSurge) or lastAbs >= lastSurge)
        evB = lastAbs if lastIsAbs else lastSurge
        evUp = lastAbsUp if lastIsAbs else lastSurUp
        evC = ('upside ' if flowUp else 'downside ') + ('absorbed' if absorbed else 'surge') + '  ·  forming now' if evLive else 'none yet' if na(evB) else ('upside ' if evUp else 'downside ') + ('absorbed' if lastIsAbs else 'surge') + '  ·  ' + f_ago(evB)
        evCol = (cUpV if flowUp else cDnV) if evLive else pnlTx if na(evB) else cUpV if evUp else cDnV
        f_row(1, 'In control', ctlC, grey, cMovV if upTop else cPrsV, 0)
        f_row(2, 'Net flow, 3 bars', netC, grey, pnlTx, 0)
        f_row(3, 'Last event', evC, grey, evCol, 0)
        f_row(4, f_bars(bar_index + 1), string.format_time(time, 'yyyy-MM-dd HH:mm', syminfo.timezone), dimc, dimc, 0)

    if showPanel and barstate.islast and (panelSize == 'Full'):
        grey = color.new(chart.fg_color, 20)
        dimc = color.new(chart.fg_color, 45)
        srcTx = 'intrabar ' + ltfUse if useIntra else 'bar shape'
        hdr = 'DELTA FLOW RIBBON  ·  ' + srcTx + '  ·  ' + ('cal time of day ' + string.tostring(todDays) + ' sessions' if useTod else 'cal ' + string.tostring(calLen) + ' bars') + '  ·  surge ≥ ' + string.tostring(surgeLvl, '0.0') + '×  ·  absorbed ≥ ' + string.tostring(absFlow, '0.0') + '× / ≤ ' + string.tostring(lowResp, '0.00') + '×  ·  ' + string.tostring(fastLen) + '–' + string.tostring(slowLen) + ' ×' + string.tostring(passes) + '  ·  ' + string.tostring(strands) + ' strands'
        table.cell(tb, 0, 0, hdr, text_size=size.small, text_color=pnlTx, text_halign=text.align_left, bgcolor=color.new(chart.bg_color, 0))
        table.cell(tb, 1, 0, syminfo.ticker + ' ' + timeframe.period, text_size=size.small, text_color=grey, text_halign=text.align_right, bgcolor=color.new(chart.bg_color, 0))
        ctlTx = '—' if na(mov0) or na(prs0) else ('upside flow' if upTop else 'downside flow') + '  ·  ' + ('this bar' if anyCross else 'none yet' if na(lastCross) else 'for ' + f_bars(bar_index - lastCross))
        netTx = '—' if na(netS) else 'balanced' if math.abs(netS) < 0.25 else ('upside ' if netS > 0 else 'downside ') + string.tostring(math.abs(netS), '0.0') + ' × normal'
        respTx = '—' if na(respX) or flowA < 0.25 else string.tostring(respX, '0.00') + ' × expected' + ('  (against the flow)' if respX < 0 else '')
        surTx = 'forming now  ·  ' + ('upside' if flowUp else 'downside') if surge and barstate.isrealtime else 'none yet' if na(lastSurge) else f_ago(lastSurge) + '  ·  ' + ('upside' if lastSurUp else 'downside')
        absTx = 'forming now  ·  ' + ('upside flow absorbed' if flowUp else 'downside flow absorbed') if absorbed and barstate.isrealtime else 'none yet' if na(lastAbs) else f_ago(lastAbs) + '  ·  ' + ('upside flow absorbed' if lastAbsUp else 'downside flow absorbed')
        srcRow = ('intrabar ' + ltfUse + ('' if na(intraFrom) else '  ·  since ' + string.format_time(intraFrom, 'yyyy-MM-dd', syminfo.timezone)) + ('  ·  ' + string.tostring(fbAfter) + ' bars fell back' if fbAfter > 0 else '') if useIntra else 'bar shape' + ('  (intrabar unavailable here)' if deltaSrc == 'Intrabar' else '')) + ('  ·  tick-count feed' if tickVol else '')
        nowCol = pnlTx if na(barCol) else barCol
        f_row(1, 'Upside flow', '—' if na(mov0) else string.tostring(mov0, '0.00') + ' × normal', cMovV, pnlTx, 0)
        f_row(2, 'Downside flow', '—' if na(prs0) else string.tostring(prs0, '0.00') + ' × normal', cPrsV, pnlTx, 0)
        f_row(3, 'In control', ctlTx, grey, cMovV if upTop else cPrsV, 0)
        f_row(4, 'Net flow, 3 bars', netTx, grey, nowCol, 0)
        f_row(5, 'Price response, 3 bars', respTx, grey, nowCol, 0)
        f_row(6, 'Last surge', surTx, grey, pnlTx, 0)
        f_row(7, 'Last absorbed flow', absTx, grey, pnlTx, 0)
        f_row(8, 'Delta source', srcRow, grey, pnlTx, 0)
        f_row(9, 'Activity, bar so far', '—' if na(volX) else string.tostring(volX, '0.00') + ' × normal volume', grey, pnlTx, 0)
        f_row(10, 'Surges · absorbed · control changes', string.tostring(nSurge) + '  ·  ' + string.tostring(nAbs) + '  ·  ' + string.tostring(nCross), grey, pnlTx, 0)
        f_row(11, 'Bars loaded', string.tostring(bar_index + 1), dimc, dimc, 0)
        f_row(12, 'Last bar', string.format_time(time, 'yyyy-MM-dd HH:mm', syminfo.timezone), dimc, dimc, 0)

    alertcondition(alCtl and anyCross, 'Control change', 'Delta Flow Ribbon: control passed to the other side')
    alertcondition(alSurge and surge and (not surge[1]), 'Flow surge', 'Delta Flow Ribbon: a flow surge began')
    alertcondition(alAbs and absorbed and (not absorbed[1]), 'Absorbed flow', 'Delta Flow Ribbon: absorbed flow began')

    if barstate.isconfirmed and barstate.isrealtime:
        if alCtl and anyCross:
            alert(syminfo.ticker + ' ' + timeframe.period + ': control passed to ' + ('upside' if upLeads else 'downside') + ' flow', alert.freq_once_per_bar_close)
        if alSurge and surge and (not surge[1]):
            alert(syminfo.ticker + ' ' + timeframe.period + ': ' + ('upside' if flowUp else 'downside') + ' flow surge, ' + string.tostring(flowA, '0.0') + '× normal net flow', alert.freq_once_per_bar_close)
        if alAbs and absorbed and (not absorbed[1]):
            alert(syminfo.ticker + ' ' + timeframe.period + ': ' + ('upside' if flowUp else 'downside') + ' flow absorbed, ' + string.tostring(flowA, '0.0') + '× normal net flow, price response ' + string.tostring(respX, '0.00') + '× expected', alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)