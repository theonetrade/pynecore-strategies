"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barstate, box, chart, close,
    color, display, extend, format, high, input, label, line, linefill, low, math, na, plot,
    position, script, size, string, syminfo, ta, table, text, time, timeframe, xloc, yloc
)
from pynecore.types import Box, Color, Label, Line, LineFill, NA, Persistent, Table


@udt
class Pivot:
    bar: int = na(int)
    stamp: int = na(int)
    price: float = na(float)
    side: int = na(int)


@udt
class Wave:
    longer: bool = False
    points: 'list[Pivot]' = na(list)
    side: int = na(int)
    key: str = na(str)
    admitBar: int = na(int)
    admitTime: int = na(int)
    atr: float = na(float)
    ageBars: int = na(int)
    apexBar: float = na(float)
    state: int = na(int)
    reason: int = na(int)
    endBar: int = na(int)
    entry: float = na(float)
    entryBar: int = na(int)
    stop: float = na(float)
    unit: float = na(float)
    tiers: list[float] = na(list)
    reachedBars: list[int] = na(list)
    stopBar: int = na(int)
    dirty: bool = na(bool)
    geometry: list[Line] = na(list)
    pointLabels: list[Label] = na(list)
    levelLines: list[Line] = na(list)
    levelTags: list[Label] = na(list)
    levelZones: list[Box] = na(list)
    wedge: LineFill = na(LineFill)


@udt
class Forming:
    points: 'list[Pivot]' = na(list)
    side: int = na(int)
    atr: float = na(float)
    apexBar: float = na(float)


G_DETECT: str = "Detection"
G_LEVELS: str = "Trade levels"
G_LIFECYCLE: str = "Waves"
G_STYLE: str = "Lines and fill"
G_DISPLAY: str = "Display"
G_ALERTS: str = "Alerts"
PRESET_SCALP: str = "Scalp"
PRESET_DAY: str = "Day"
PRESET_SWING: str = "Swing"
PRESET_CUSTOM: str = "Custom"
DIR_BOTH: str = "Both"
DIR_BULL: str = "Bullish only"
DIR_BEAR: str = "Bearish only"
STYLE_SOLID: str = "Solid"
STYLE_DASHED: str = "Dashed"
STYLE_DOTTED: str = "Dotted"
POS_AUTO: str = "Auto"
POS_TOP_RIGHT: str = "Top right"
POS_TOP_LEFT: str = "Top left"
POS_BOTTOM_RIGHT: str = "Bottom right"
POS_BOTTOM_LEFT: str = "Bottom left"
SIZE_TINY: str = "Tiny"
SIZE_SMALL: str = "Small"
SIZE_NORMAL: str = "Normal"
EVENTS_ALL: str = "All events"
EVENTS_FORMED: str = "Formed and Entry"
EVENTS_ENDINGS: str = "Endings"
EVENTS_OFF: str = "Off"
DETAIL_BRIEF: str = "Brief"
DETAIL_FULL: str = "Full"
DETAIL_JSON: str = "JSON"
PIVOT_HORIZON: int = 500
VOLATILITY_LENGTH: int = 14
OVERSHOOT_ATR: float = 1.0
STOP_BEYOND_ATR: float = 0.1
MIN_STOP_ATR: float = 0.5
MINOR_FRAC: float = 0.382
LINE_EPS: float = 1e-10
ACTIVE_MAX: int = 4
SEEN_MAX: int = 64
CHAIN_MAX: int = 13
DRAW_MAX_BACK: int = 4500
POINTS: int = 5
LEGS: int = 4
MASKS: int = 16
ST_WAITING: int = 1
ST_ENTERED: int = 2
ST_ENDED: int = 3
END_BEYOND_FIVE: int = 1
END_NO_ENTRY: int = 2
END_STOP: int = 3
END_FINAL: int = 4
END_SAME_BAR: int = 5
END_AGED: int = 6
END_PAST_24: int = 7
EV_FORMED: int = 0
EV_ENTRY: int = 1
EV_LEVEL: int = 2
EV_ENDED: int = 3
LINE_L13: int = 4
LINE_L24: int = 5
LINE_L14: int = 6
PANEL_ROWS: int = 12
PANEL_WAVES: int = 3
ENDED_FADE: int = 40
GUIDE_FADE: int = 25
REACHED_TRANSP: int = 25
FORMING_FADE: int = 40
ENTRY_LINE_TRANSP: int = 30
LEVEL_LINE_TRANSP: int = 35
TAG_TRANSP: int = 85
TAG_REACHED_TRANSP: int = 60
ZONE_TRANSP: int = 92
ZONE_REACHED_TRANSP: int = 80
FORMING_ZONE_TRANSP: int = 85
BUILD_ID: str = "AWW-PREPUB-20260930N"
DISCLOSURE: str = "T1–T3 are user-set multiples of R, this wave's own Entry-to-Stop distance; Entry and Stop come from its own bars and ATR. They describe chart geometry, not a measured outcome."
GUIDE_DARK: Color = color.new('#7D8896')
GUIDE_LIGHT: Color = color.new('#55606E')
LEVEL_TEXT: Color = color.new('#FFFFFF')
INK_DARK: Color = color.new('#C7CFD9')
INK_LIGHT: Color = color.new('#1A212B')
FILL_DARK: Color = color.new('#0E1218')
FILL_LIGHT: Color = color.new('#FFFFFF')
PLOT_TINT: Color = color.new('#26A69A')
CLEAR: Color = color.new('#00000000')


@script.indicator("Auto Wolfe Waves [AFD]", "AWW [AFD]", overlay=True, behind_chart=False, max_lines_count=190, max_labels_count=130, max_boxes_count=60, max_bars_back=5000)
def main(
    presetInput=input.string(PRESET_DAY, "Preset", options=(PRESET_SCALP, PRESET_DAY, PRESET_SWING, PRESET_CUSTOM), group=G_DETECT, tooltip="• Scalp: swing 3, Entry window 5.\n• Day: swing 5, Entry window 10.\n• Swing: swing 8, Entry window 15.\n• Custom: set both below.", display=display.none),
    directionInput=input.string(DIR_BOTH, "Direction", options=(DIR_BOTH, DIR_BULL, DIR_BEAR), group=G_DETECT, tooltip="• Which waves are found and drawn, developing ones included.", display=display.none),
    swingCustomInput=input.int(5, "Swing strength", minval=2, maxval=30, group=G_DETECT, tooltip="• Bars on each side of a pivot.\n• Point 5 is confirmed after this many further bars; detection then checks the count.\n• Custom preset only.", display=display.none),
    windowCustomInput=input.int(10, "Entry window (bars)", minval=1, maxval=50, group=G_DETECT, tooltip="• Bars, from the one a wave appears on, for a close back inside the 1–3 line.\n• None: the wave ends without levels.\n• Custom preset only.", display=display.none),
    skipInput=input.bool(True, "Allow one skipped swing per leg", group=G_DETECT, tooltip="• A leg may step over one smaller swing inside it.\n• Counts with the fewest skips are tried first."),
    longerInput=input.bool(False, "Longer swing waves", group=G_DETECT, tooltip="Adds an independent Wolfe layer on this timeframe using Swing strength times Longer swing multiple. It is separate from skipped legs; four live waves per layer and one shared ended-wave allowance. Longer counts can be excluded by the fixed 500-bar pivot horizon."),
    multipleInput=input.int(3, "Longer swing multiple", minval=2, maxval=4, group=G_DETECT, display=display.none, tooltip="Multiplies the preset or Custom Swing strength; Day with 3 uses 15 bars on each side. Confirmation waits that many bars after point 5. Entry window and the 14-bar volatility window remain the same for both layers."),
    levelsInput=input.bool(True, "Show Entry, Stop and levels", group=G_LEVELS, tooltip="• Entry, Stop and T1–T3 with zones and tags.\n• Entry: the first close back inside the 1–3 line from the bar the wave appears, not already past the 2–4 line.\n• Off hides them on the chart; the panel and alerts still list them."),
    onCloseInput=input.string("Clear", "Once reached", options=("Clear", "Keep"), group=G_LEVELS, display=display.none, tooltip="Clear: a definitively reached T target loses its line, zone and name; the tag lists the remaining targets. Keep: all targets stay, with reached marks. Order unknown stays visible in either mode. Entry, Stop and the panel record remain."),
    t1Input=input.float(0.5, "T1 (R)", minval=0.1, maxval=10.0, step=0.05, group=G_LEVELS, inline="tiers", display=display.none),
    t2Input=input.float(0.75, "T2 (R)", minval=0.1, maxval=10.0, step=0.05, group=G_LEVELS, inline="tiers", display=display.none),
    t3Input=input.float(1.0, "T3 (R)", minval=0.1, maxval=10.0, step=0.05, group=G_LEVELS, inline="tiers", tooltip="• Multiples of R, the Entry-to-Stop distance.\n• Must rise from T1 to T3; otherwise only Entry and Stop are built.", display=display.none),
    targetColorInput=input.color(color.new('#8C66FF'), "T level colour", group=G_LEVELS, inline="levelColours"),
    stopColorInput=input.color(color.new('#D9453D'), "Stop colour", group=G_LEVELS, inline="levelColours", tooltip="• Colours of the T1–T3 and Stop lines, zones and tags."),
    formingInput=input.bool(True, "Show developing waves", group=G_LIFECYCLE, tooltip="• Points 1–4 confirmed, no point 5 yet: drawn dashed.\n• The band is the 1–3 line to 1 ATR beyond it, using volatility frozen when this candidate is selected.\n• ATR is a 14-bar simple mean of true range; admission uses its then-current value.\n• Hidden intrabar beyond the band or at the apex; confirmed invalidation clears it."),
    keptInput=input.int(2, "Ended waves kept", minval=0, maxval=5, group=G_LIFECYCLE, tooltip="• Ended waves left on the chart, newest first.\n• Removed whole, and once point 1 is over 4,500 bars back.", display=display.none),
    bullInput=input.color(color.new('#26A69A'), "Bullish", group=G_STYLE, inline="colours"),
    bearInput=input.color(color.new('#EF5350'), "Bearish", group=G_STYLE, inline="colours"),
    brokenInput=input.color(color.new('#787B86'), "Beyond point 5", group=G_STYLE, inline="colours", tooltip="• Bullish and Bearish: colours of each wave.\n• Beyond point 5: a wave whose ending bar traded beyond point 5, a Stop included."),
    widthInput=input.int(2, "Zigzag", minval=1, maxval=4, group=G_STYLE, inline="zigzag", display=display.none),
    zigzagStyleInput=input.string(STYLE_SOLID, "", options=(STYLE_SOLID, STYLE_DASHED, STYLE_DOTTED), group=G_STYLE, inline="zigzag", tooltip="• Width and style of the 1-2-3-4-5 zigzag.", display=display.none),
    guideWidthInput=input.int(1, "1–3 and 2–4 lines", minval=1, maxval=4, group=G_STYLE, inline="guides", display=display.none),
    guideStyleInput=input.string(STYLE_SOLID, "", options=(STYLE_SOLID, STYLE_DASHED, STYLE_DOTTED), group=G_STYLE, inline="guides", tooltip="• Width and style of the 1–3 and 2–4 lines.", display=display.none),
    l14WidthInput=input.int(1, "1–4 line", minval=1, maxval=4, group=G_STYLE, inline="l14", display=display.none),
    l14StyleInput=input.string(STYLE_DOTTED, "", options=(STYLE_SOLID, STYLE_DASHED, STYLE_DOTTED), group=G_STYLE, inline="l14", tooltip="• Width and style of the 1–4 line, drawn as a reference only.", display=display.none),
    fillInput=input.bool(True, "Wedge fill", group=G_STYLE, inline="fill"),
    fillTranspInput=input.int(88, "Transparency", minval=50, maxval=100, group=G_STYLE, inline="fill", tooltip="• Shades the wedge between the 1–3 and 2–4 lines in the wave's colour.\n• 100 is fully clear.", display=display.none),
    pointsInput=input.bool(True, "Point labels", group=G_DISPLAY, tooltip="• Labels 1–5 on each wave.\n• Point 5's hover lists all five prices."),
    panelInput=input.bool(True, "Panel", group=G_DISPLAY, tooltip="• The newest three waves, newest first: direction, state, Entry, Stop and T1–T3.\n• Notices stay visible when it is off."),
    positionInput=input.string(POS_AUTO, "Panel position", options=(POS_AUTO, POS_TOP_RIGHT, POS_TOP_LEFT, POS_BOTTOM_RIGHT, POS_BOTTOM_LEFT), group=G_DISPLAY, tooltip="• Auto: bottom left after a Conventionally Bullish wave; top right otherwise.\n• A bottom panel ends in a blank row, so TradingView's logo or badge covers that row, not a level.", display=display.none),
    textSizeInput=input.string(SIZE_SMALL, "Text size", options=(SIZE_TINY, SIZE_SMALL, SIZE_NORMAL), group=G_DISPLAY, tooltip="• Point labels, level tags and the panel.", display=display.none),
    eventsInput=input.string(EVENTS_ALL, "Alert events", options=(EVENTS_ALL, EVENTS_FORMED, EVENTS_ENDINGS, EVENTS_OFF), group=G_ALERTS, tooltip="• All events: formed, Entry, each level reached, each ending.\n• Formed and Entry: those two only.\n• Endings: each ending with its reason.\n• The four alert conditions are set separately.", display=display.none),
    detailInput=input.string(DETAIL_BRIEF, "Detail", options=(DETAIL_BRIEF, DETAIL_FULL, DETAIL_JSON), group=G_ALERTS, tooltip="• Brief: event, direction, times of points 2–4.\n• Full: adds prices, multiples and the level note.\n• JSON: the same fields as structured records.\n• One message per bar carries all its events.", display=display.none)
):
    swingInput: int = 3 if presetInput == PRESET_SCALP else 5 if presetInput == PRESET_DAY else 8 if presetInput == PRESET_SWING else swingCustomInput
    longerStrengthInput: int = swingInput * multipleInput
    windowInput: int = 5 if presetInput == PRESET_SCALP else 10 if presetInput == PRESET_DAY else 15 if presetInput == PRESET_SWING else windowCustomInput



    def acceptPivot(chain: list[Pivot], pivot: Pivot):
        n: int = array.size(chain)
        changed: bool = True
        if n > 0 and array.get(chain, n - 1).side == pivot.side:
            lastPrice: float = array.get(chain, n - 1).price
            changed = pivot.price >= lastPrice if pivot.side == 1 else pivot.price <= lastPrice
            if changed:
                array.set(chain, n - 1, pivot)
        else:
            array.push(chain, pivot)
            while array.size(chain) > CHAIN_MAX:
                array.shift(chain)
        return changed

    def trimAge(chain: list[Pivot], barNow: int):
        while array.size(chain) > 0 and barNow - array.first(chain).bar > PIVOT_HORIZON:
            array.shift(chain)
        return 0

    def spanOf(mask: int, leg: int):
        return 3 if math.floor(mask / math.pow(2, LEGS - 1 - leg)) % 2 == 1 else 1

    def skippedOf(mask: int):
        skipped: int = 0
        for leg in pine_range(0, LEGS - 1):
            skipped += 1 if spanOf(mask, leg) == 3 else 0
        return skipped

    def directedLeg(chain: list[Pivot], iOld: int, iNew: int):
        older: Pivot = array.get(chain, iOld)
        newer: Pivot = array.get(chain, iNew)
        return newer.bar > older.bar and newer.side * (newer.price - older.price) > 0

    def dominant(chain: list[Pivot], iOld: int, iNew: int):
        pOld: float = array.get(chain, iOld).price
        pNew: float = array.get(chain, iNew).price
        lo: float = math.min(pOld, pNew)
        hi: float = math.max(pOld, pNew)
        ok: bool = True
        if iNew - iOld > 1:
            for k in pine_range(iOld + 1, iNew - 1):
                pk: float = array.get(chain, k).price
                if pk <= lo or pk >= hi:
                    ok = False
            if ok and iNew - iOld > 2:
                cap: float = MINOR_FRAC * (hi - lo)
                for k in pine_range(iOld + 1, iNew - 2):
                    if math.abs(array.get(chain, k + 1).price - array.get(chain, k).price) > cap:
                        ok = False
        return ok

    def candidateIdx(chain: list[Pivot], mask: int):
        idx: list[int] = array.new_int(POINTS, 0)
        at: int = array.size(chain) - 1
        ok: bool = at >= 0
        array.set(idx, LEGS, at)
        for leg in pine_range(LEGS - 1, 0):
            at -= spanOf(mask, leg)
            ok = ok and at >= 0
            if at >= 0:
                array.set(idx, leg, at)
        if ok:
            for leg in pine_range(0, LEGS - 1):
                if not directedLeg(chain, array.get(idx, leg), array.get(idx, leg + 1)) or not dominant(chain, array.get(idx, leg), array.get(idx, leg + 1)):
                    ok = False
        return (ok, idx)

    def lineAt(p: Pivot, q: Pivot, x: int):
        return p.price + (q.price - p.price) * (x - p.bar) / (q.bar - p.bar)

    def onLine(gap: float, price: float, step: float):
        return 0.0 if math.abs(gap) <= math.min(LINE_EPS * math.abs(price), 0.25 * step) else gap

    def lineStep(p: Pivot, q: Pivot):
        return syminfo.mintick / (q.bar - p.bar)

    def directionOf(pts: list[Pivot]):
        return 1 if array.get(pts, 4).side == -1 else -1

    def wolfeRulesPass(pts: list[Pivot], atr: float):
        p1: Pivot = array.get(pts, 0)
        p2: Pivot = array.get(pts, 1)
        p3: Pivot = array.get(pts, 2)
        p4: Pivot = array.get(pts, 3)
        p5: Pivot = array.get(pts, 4)
        s: int = directionOf(pts)
        gapStep: float = lineStep(p1, p3) / (p4.bar - p2.bar)
        widthAt5: float = onLine(s * (lineAt(p2, p4, p5.bar) - lineAt(p1, p3, p5.bar)), p5.price, gapStep)
        widthAt4: float = s * (p4.price - lineAt(p1, p3, p4.bar))
        overshoot: float = onLine(s * (lineAt(p1, p3, p5.bar) - p5.price), p5.price, lineStep(p1, p3))
        w1: bool = s * (p1.price - p3.price) > 0
        w2: bool = s * (p4.price - p1.price) > 0
        w3: bool = widthAt5 > 0 and onLine(widthAt4 - widthAt5, p5.price, gapStep) > 0
        w4: bool = overshoot >= 0
        w5: bool = overshoot <= OVERSHOOT_ATR * atr
        return w1 and w2 and w3 and w4 and w5

    def keyOf(pts: list[Pivot]):
        return string.tostring(directionOf(pts)) + ':' + string.tostring(array.get(pts, 1).bar) + ',' + string.tostring(array.get(pts, 2).bar) + ',' + string.tostring(array.get(pts, 3).bar)

    def sideAllowed(side: int):
        return directionInput == DIR_BOTH or (directionInput == DIR_BULL and side == 1) or (directionInput == DIR_BEAR and side == -1)

    def selectWave(chain: list[Pivot], atr: float, seenKeys: list[str]):
        chosen: list[Pivot] = na(list[Pivot])

        allowed: bool = array.size(chain) > 0 and sideAllowed(-array.last(chain).side)
        maxSkipped: int = LEGS if skipInput else 0
        for skipped in pine_range(0, maxSkipped):
            for mask in pine_range(0, MASKS - 1):
                if allowed and na(chosen) and (skippedOf(mask) == skipped):
                    ok, idx = candidateIdx(chain, mask)
                    if ok:
                        pts: list[Pivot] = array.new(0, NA(Pivot))
                        for i in idx:
                            array.push(pts, array.get(chain, i))
                        if wolfeRulesPass(pts, atr) and (not array.includes(seenKeys, keyOf(pts))):
                            chosen = pts
        return chosen

    def formingSpanOf(mask: int, leg: int):
        return 3 if math.floor(mask / math.pow(2, LEGS - 2 - leg)) % 2 == 1 else 1

    def formingIdx(chain: list[Pivot], mask: int):
        idx: list[int] = array.new_int(LEGS, 0)
        at: int = array.size(chain) - 1
        ok: bool = at >= 0
        array.set(idx, LEGS - 1, at)
        for leg in pine_range(LEGS - 2, 0):
            at -= formingSpanOf(mask, leg)
            ok = ok and at >= 0
            if at >= 0:
                array.set(idx, leg, at)
        if ok:
            for leg in pine_range(0, LEGS - 2):
                if not directedLeg(chain, array.get(idx, leg), array.get(idx, leg + 1)) or not dominant(chain, array.get(idx, leg), array.get(idx, leg + 1)):
                    ok = False
        return (ok, idx)

    def formingApex(pts: list[Pivot]):
        p1: Pivot = array.get(pts, 0)
        p2: Pivot = array.get(pts, 1)
        p3: Pivot = array.get(pts, 2)
        p4: Pivot = array.get(pts, 3)
        s: int = p4.side
        slope13: float = (p3.price - p1.price) / (p3.bar - p1.bar)
        slope24: float = (p4.price - p2.price) / (p4.bar - p2.bar)
        widthAt4: float = s * (p4.price - lineAt(p1, p3, p4.bar))
        narrowing: float = onLine(s * (slope13 - slope24), p4.price, lineStep(p1, p3) / (p4.bar - p2.bar))
        rules: bool = s * (p1.price - p3.price) > 0 and s * (p4.price - p1.price) > 0 and (widthAt4 > 0) and (narrowing > 0)
        return p4.bar + widthAt4 / narrowing if rules else na

    def formingLineAt(f: Forming, x: int):
        return lineAt(array.get(f.points, 0), array.get(f.points, 2), x)

    def formingFarAt(f: Forming, x: int):
        return formingLineAt(f, x) - f.side * OVERSHOOT_ATR * f.atr

    def formingHolds(f: Forming, barNow: int, fromBar: int):
        holds: bool = barNow < f.apexBar and barNow - array.get(f.points, 0).bar <= PIVOT_HORIZON
        if holds and fromBar <= barNow:
            for x in pine_range(fromBar, barNow):
                back: int = barNow - x
                against: float = low[back] if f.side > 0 else high[back]
                if not na(against) and f.side * (against - formingFarAt(f, x)) < 0:
                    holds = False
        return holds

    def selectForming(chain: list[Pivot], atr: float, seenKeys: list[str], barNow: int):
        chosen: Forming = na(Forming)

        if not na(atr) and atr > 0 and (array.size(chain) > 0) and sideAllowed(array.last(chain).side):
            maxSkipped: int = LEGS - 1 if skipInput else 0
            for skipped in pine_range(0, maxSkipped):
                for mask in pine_range(0, MASKS / 2 - 1):
                    if na(chosen) and skippedOf(mask) == skipped:
                        ok, idx = formingIdx(chain, mask)
                        if ok:
                            pts: list[Pivot] = array.new(0, NA(Pivot))
                            for i in idx:
                                array.push(pts, array.get(chain, i))
                            apex: float = formingApex(pts)
                            key: str = string.tostring(array.get(pts, 3).side) + ':' + string.tostring(array.get(pts, 1).bar) + ',' + string.tostring(array.get(pts, 2).bar) + ',' + string.tostring(array.get(pts, 3).bar)
                            if not na(apex) and (not array.includes(seenKeys, key)):
                                candidate: Forming = Forming(pts, array.get(pts, 3).side, atr, apex)
                                if formingHolds(candidate, barNow, array.get(pts, 3).bar + 1):
                                    chosen = candidate
        return chosen

    def remember(seenKeys: list[str], key: str):
        array.push(seenKeys, key)
        while array.size(seenKeys) > SEEN_MAX:
            array.shift(seenKeys)
        return 0

    def apexOf(pts: list[Pivot]):
        p4: Pivot = array.get(pts, 3)
        p5: Pivot = array.get(pts, 4)
        widthAt4: float = p4.price - lineAt(array.get(pts, 0), array.get(pts, 2), p4.bar)
        widthAt5: float = lineAt(array.get(pts, 1), p4, p5.bar) - lineAt(array.get(pts, 0), array.get(pts, 2), p5.bar)
        return p4.bar + widthAt4 * (p5.bar - p4.bar) / (widthAt4 - widthAt5)

    def guideRight(w: Wave, x: int):
        return cast_int(math.min(x, math.floor(w.apexBar)))

    def line13At(w: Wave, x: int):
        return lineAt(array.get(w.points, 0), array.get(w.points, 2), x)

    def line24At(w: Wave, x: int):
        return lineAt(array.get(w.points, 1), array.get(w.points, 3), x)

    def line14At(w: Wave, x: int):
        return lineAt(array.get(w.points, 0), array.get(w.points, 3), x)

    def tickValid():
        return not na(syminfo.mintick) and syminfo.mintick > 0

    def priceFormatOf():
        out: str = format.mintick
        if tickValid():
            step: float = syminfo.mintick
            places: int = 0
            while places < 15 and math.abs(step - math.round(step)) > step * 1e-06:
                step *= 10
                places += 1
            out = "0"
            if places > 0:
                out += "."
                for k in pine_range(1, places):
                    out += "0"
        return out

    priceFormat: Persistent[str] = priceFormatOf()

    def gridPrice(price: float):
        return math.round(price / syminfo.mintick) * syminfo.mintick if tickValid() else price

    def outwardTick(value: float, upward: bool, reference: float):
        out: float = value
        if tickValid():
            mt: float = syminfo.mintick
            units: float = value / mt
            nearest: int = math.round(units)
            if math.abs(units - nearest) <= math.max(1e-09, math.abs(units) * 2e-15, math.abs(reference / mt) * 2e-15):
                units = nearest
            out = (math.ceil(units) if upward else math.floor(units)) * mt
        return out

    def multsValid():
        return t1Input > 0 and t2Input > 0 and (t3Input > 0) and (t1Input < t2Input) and (t2Input < t3Input)

    def multOf(tier: int):
        return t1Input if tier == 0 else t2Input if tier == 1 else t3Input

    def setLevels(w: Wave):
        rawStop: float = array.get(w.points, 4).price - w.side * STOP_BEYOND_ATR * w.atr
        dist: float = math.max(w.side * (w.entry - rawStop), MIN_STOP_ATR * w.atr)
        stopPrice: float = w.entry - w.side * dist
        if tickValid():
            stopPrice = outwardTick(math.min(stopPrice, w.entry - syminfo.mintick), False, w.entry) if w.side > 0 else outwardTick(math.max(stopPrice, w.entry + syminfo.mintick), True, w.entry)
        w.stop = stopPrice
        w.unit = math.abs(w.entry - stopPrice)

        if multsValid():
            for tier in pine_range(0, 2):
                price: float = outwardTick(w.entry + w.side * multOf(tier) * w.unit, w.side > 0, w.entry)
                if tier > 0 and tickValid():
                    before: float = array.get(w.tiers, tier - 1)
                    if w.side * (price - before) < syminfo.mintick / 2:
                        price = before + w.side * syminfo.mintick
                array.push(w.tiers, price)
                array.push(w.reachedBars, na)
        return 0

    def layerPrefix(longer: bool):
        return 'Longer ' if longer else ''

    def strokeOf(base: int, longer: bool):
        return math.min(base + 1, 4) if longer else base

    def directionWord(side: int):
        return 'Conventionally Bullish' if side == 1 else 'Conventionally Bearish'

    def reasonWord(reason: int):
        __block_result__ = na
        __switch__ = reason
        if __switch__ == END_BEYOND_FIVE:
            __block_result__ = "traded beyond point 5"
        elif __switch__ == END_NO_ENTRY:
            __block_result__ = "no close inside the 1–3 line"
        elif __switch__ == END_STOP:
            __block_result__ = "Stop reached"
        elif __switch__ == END_FINAL:
            __block_result__ = "T3 reached"
        elif __switch__ == END_SAME_BAR:
            __block_result__ = "order unknown"
        elif __switch__ == END_AGED:
            __block_result__ = "aged out"
        elif __switch__ == END_PAST_24:
            __block_result__ = "closed past the 2–4 line"
        else:
            __block_result__ = ""
        return __block_result__

    def multText(mult: float):
        return string.tostring(mult, '0.0##') + 'R'

    def tierName(tier: int):
        return 'T' + string.tostring(tier + 1) + ' ' + multText(multOf(tier))

    def priceText(price: float):
        return string.tostring(price, priceFormat)

    def stampText(stamp: int):
        return string.format_time(stamp, 'yyyy-MM-dd HH:mm:ss' if timeframe.isseconds else 'yyyy-MM-dd HH:mm', syminfo.timezone)

    def keyText(w: Wave):
        return 'points 2–4 opened ' + stampText(array.get(w.points, 1).stamp) + ', ' + stampText(array.get(w.points, 2).stamp) + ', ' + stampText(array.get(w.points, 3).stamp)

    def eventWord(kind: int, w: Wave, fresh: list[int]):
        word: str = 'Formed' if kind == EV_FORMED else 'Entry' if kind == EV_ENTRY else 'Ended: ' + reasonWord(w.reason)
        if kind == EV_LEVEL:
            names: list[str] = array.new_string()
            for tier in fresh:
                array.push(names, 'T' + string.tostring(tier + 1) + ' reached')
            word = array.join(names, ', ')
        return word

    def pointsText(w: Wave):
        parts: list[str] = array.new_string()
        for k, p in enumerate(w.points):
            array.push(parts, string.tostring(k + 1) + ' ' + priceText(p.price))
        return array.join(parts, ' · ')

    def levelsText(w: Wave):
        out: str = "no Entry"
        if not na(w.entry):
            out = 'Entry ' + priceText(w.entry) + ' · Stop ' + multText(1.0) + ' ' + priceText(w.stop) + ' · R ' + priceText(w.unit)
            for tier, price in enumerate(w.tiers):
                out += ' · ' + tierName(tier) + ' ' + priceText(price)
        return out

    def jsonNumber(value: float):
        return 'null' if na(value) else string.tostring(value, '0.###############')

    def jsonString(value: str):
        escaped: str = string.replace_all(value, '\\', '\\\\')
        escaped = string.replace_all(escaped, '"', '\\"')
        escaped = string.replace_all(escaped, '\n', '\\n')
        return '"' + escaped + '"'

    def jsonPrice(value: float):
        return 'null' if na(value) else string.tostring(value, priceFormat) if tickValid() else jsonNumber(value)

    def configurationJson():
        return '{"swing":' + string.tostring(swingInput) + ',"skip":' + string.tostring(skipInput) + ',"window":' + string.tostring(windowInput) + ',"t1":' + jsonNumber(t1Input) + ',"t2":' + jsonNumber(t2Input) + ',"t3":' + jsonNumber(t3Input) + ',"direction":' + jsonString(directionInput) + ',"kept":' + string.tostring(keptInput) + ',"events":' + jsonString(eventsInput) + ',"detail":' + jsonString(detailInput) + (',"longer":true,"multiple":' + string.tostring(multipleInput) if longerInput else '') + '}'

    def eventJson(kind: int, w: Wave, fresh: list[int]):
        prices: list[str] = array.new_string()
        for p in w.points:
            array.push(prices, jsonPrice(p.price))
        tierPrices: list[str] = array.new_string()
        for price in w.tiers:
            array.push(tierPrices, jsonPrice(price))
        freshText: list[str] = array.new_string()
        for tier in fresh:
            array.push(freshText, string.tostring(tier + 1))
        return '{"event":' + jsonString(eventWord(kind, w, fresh)) + (',"layer":' + jsonString('Longer' if w.longer else 'Main') if longerInput else '') + ',"direction":' + jsonString(directionWord(w.side)) + ',"side":' + string.tostring(w.side) + ',"key":[' + string.tostring(array.get(w.points, 1).stamp) + ',' + string.tostring(array.get(w.points, 2).stamp) + ',' + string.tostring(array.get(w.points, 3).stamp) + '],"time":' + string.tostring(time) + ',"points":[' + array.join(prices, ',') + '],"entry":' + jsonPrice(w.entry) + ',"stop":' + jsonPrice(w.stop) + ',"r":' + jsonPrice(w.unit) + ',"tiers":[' + array.join(tierPrices, ',') + '],"multiples":[' + jsonNumber(t1Input) + ',' + jsonNumber(t2Input) + ',' + jsonNumber(t3Input) + '],"reached":[' + array.join(freshText, ',') + '],"note":' + jsonString(DISCLOSURE) + '}'

    def eventMessage(kind: int, w: Wave, fresh: list[int]):
        out: str = layerPrefix(w.longer) + eventWord(kind, w, fresh) + ' | ' + directionWord(w.side) + ' | ' + keyText(w)
        if detailInput == DETAIL_FULL:
            out += ' | points ' + pointsText(w) + ' | ' + levelsText(w) + ' | multiples ' + multText(t1Input) + ', ' + multText(t2Input) + ', ' + multText(t3Input) + ' | ' + DISCLOSURE
        elif detailInput == DETAIL_JSON:
            out = eventJson(kind, w, fresh)
        return out

    def eventEnabled(kind: int):
        return eventsInput == EVENTS_ALL or (eventsInput == EVENTS_FORMED and (kind == EV_FORMED or kind == EV_ENTRY)) or (eventsInput == EVENTS_ENDINGS and kind == EV_ENDED)

    def recordEvent(kind: int, w: Wave, fresh: list[int], flags: list[int], messages: list[str]):
        array.set(flags, kind, 1)
        w.dirty = True

        if barstate.isrealtime and eventEnabled(kind):
            array.push(messages, eventMessage(kind, w, fresh))
        return 0

    def newWave(pts: list[Pivot], barNow: int, atr: float, longer: bool = False):
        return Wave(longer=longer, points=pts, side=directionOf(pts), key=keyOf(pts), admitBar=barNow, admitTime=time, atr=atr, ageBars=array.get(pts, 4).bar - array.get(pts, 0).bar, apexBar=apexOf(pts), state=ST_WAITING, reason=0, tiers=array.new_float(), reachedBars=array.new_int(), dirty=True, geometry=array.new_line(), pointLabels=array.new_label(), levelLines=array.new_line(), levelTags=array.new_label(), levelZones=array.new_box())

    def endWave(w: Wave, barNow: int, why: int, flags: list[int], messages: list[str]):
        w.state = ST_ENDED
        w.reason = why
        w.endBar = barNow
        return recordEvent(EV_ENDED, w, array.new_int(), flags, messages)

    def stepWaiting(w: Wave, barNow: int, flags: list[int], messages: list[str]):
        against: float = low if w.side > 0 else high
        inside13: float = onLine(w.side * (close - line13At(w, barNow)), close, lineStep(array.get(w.points, 0), array.get(w.points, 2)))
        past24: float = onLine(w.side * (close - line24At(w, barNow)), close, lineStep(array.get(w.points, 1), array.get(w.points, 3)))
        __block_result_1__ = na
        if w.side * (array.get(w.points, 4).price - against) > 0:
            __block_result_1__ = endWave(w, barNow, END_BEYOND_FIVE, flags, messages)
        elif inside13 > 0 and past24 > 0:
            __block_result_1__ = endWave(w, barNow, END_PAST_24, flags, messages)
        elif inside13 > 0:
            w.entry = gridPrice(close)
            w.entryBar = barNow
            setLevels(w)
            w.state = ST_ENTERED
            __block_result_1__ = recordEvent(EV_ENTRY, w, array.new_int(), flags, messages)
        elif barNow - w.admitBar + 1 >= windowInput:
            __block_result_1__ = endWave(w, barNow, END_NO_ENTRY, flags, messages)
        else:
            __block_result_1__ = 0
        return __block_result_1__

    def stepEntered(w: Wave, barNow: int, flags: list[int], messages: list[str]):
        tolerance: float = syminfo.mintick / 2 if tickValid() else 0.0
        favour: float = high if w.side > 0 else low
        against: float = low if w.side > 0 else high
        stopHit: bool = w.side * (w.stop - against) >= -tolerance
        fresh: list[int] = array.new_int()
        for tier, price in enumerate(w.tiers):
            if na(array.get(w.reachedBars, tier)) and w.side * (favour - price) >= -tolerance:
                array.set(w.reachedBars, tier, barNow)
                array.push(fresh, tier)
        __block_result_2__ = na
        if stopHit:
            w.stopBar = barNow

            __block_result_3__ = na
            if array.size(fresh) > 0:
                __block_result_3__ = endWave(w, barNow, END_SAME_BAR, flags, messages)
            else:
                __block_result_3__ = endWave(w, barNow, END_STOP, flags, messages)
            __block_result_2__ = __block_result_3__
        else:
            if array.size(fresh) > 0:
                recordEvent(EV_LEVEL, w, fresh, flags, messages)
            __block_result_4__ = na
            if array.size(fresh) > 0 and (not na(array.get(w.reachedBars, array.size(w.tiers) - 1))):
                __block_result_4__ = endWave(w, barNow, END_FINAL, flags, messages)
            elif barNow - w.entryBar >= w.ageBars:
                __block_result_4__ = endWave(w, barNow, END_AGED, flags, messages)
            else:
                __block_result_4__ = 0
            __block_result_2__ = __block_result_4__
        return __block_result_2__

    def liveCount(live: list[Wave], longer: bool = False):
        n: int = 0
        for w in live:
            n += 1 if w.state != ST_ENDED and w.longer == longer else 0
        return n

    def tryAdmit(chain: list[Pivot], seenKeys: list[str], refusedKeys: list[str], live: list[Wave], barNow: int, atr: float, flags: list[int], messages: list[str], longer: bool = False):
        status: int = 0
        admitted: Wave = na(Wave)
        if not na(atr) and atr > 0:
            pts: list[Pivot] = selectWave(chain, atr, seenKeys)
            if not na(pts):
                key: str = keyOf(pts)
                beyond: bool = barNow - array.get(pts, 0).bar > DRAW_MAX_BACK
                refused: bool = beyond or liveCount(live, longer) >= ACTIVE_MAX
                if refused and (not array.includes(refusedKeys, key)):
                    remember(refusedKeys, key)
                    status = 3 if beyond else 2
                elif not refused:
                    admitted = newWave(pts, barNow, atr, longer)
                    remember(seenKeys, admitted.key)
                    array.push(live, admitted)
                    recordEvent(EV_FORMED, admitted, array.new_int(), flags, messages)
                    stepWaiting(admitted, barNow, flags, messages)
                    status = 1
        return (status, admitted)

    def addTransparency(selected: Color, extra: float):
        return color.new(selected, 100.0 - (100.0 - color.t(selected)) * (100.0 - math.min(100.0, math.max(0.0, extra))) / 100.0)

    def lightChart():
        bg: Color = chart.bg_color
        return color.r(bg) * 0.299 + color.g(bg) * 0.587 + color.b(bg) * 0.114 > 140

    def brokenOf(w: Wave):
        return w.reason == END_BEYOND_FIVE or w.reason == END_STOP or w.reason == END_SAME_BAR

    def waveBase(w: Wave):
        return brokenInput if brokenOf(w) else bullInput if w.side == 1 else bearInput

    def waveColor(w: Wave):
        base: Color = waveBase(w)
        return addTransparency(base, ENDED_FADE) if w.state == ST_ENDED else base

    def guideColor():
        return GUIDE_LIGHT if lightChart() else GUIDE_DARK

    def inkColor():
        return INK_LIGHT if lightChart() else INK_DARK

    def lineStyleOf(chosen: str):
        __block_result_5__ = na
        __switch__ = chosen
        if __switch__ == STYLE_DASHED:
            __block_result_5__ = line.style_dashed
        elif __switch__ == STYLE_DOTTED:
            __block_result_5__ = line.style_dotted
        else:
            __block_result_5__ = line.style_solid
        return __block_result_5__

    def levelTint(w: Wave, base: Color, transp: int):
        used: float = 100.0 - (100.0 - transp) * (100.0 - ENDED_FADE) / 100.0 if w.state == ST_ENDED else transp
        return addTransparency(base, used)

    def textSizeOf(chosen: str):
        __block_result_6__ = na
        __switch__ = chosen
        if __switch__ == SIZE_NORMAL:
            __block_result_6__ = size.normal
        elif __switch__ == SIZE_SMALL:
            __block_result_6__ = size.small
        else:
            __block_result_6__ = size.tiny
        return __block_result_6__

    def levelPriceOf(w: Wave, role: int):
        return w.entry if role == 0 else w.stop if role == 1 else array.get(w.tiers, role - 2)

    def levelColorOf(role: int):
        return chart.fg_color if role == 0 else stopColorInput if role == 1 else targetColorInput

    def levelMarkOf(w: Wave, role: int):
        markBar: int = w.stopBar if role == 1 else array.get(w.reachedBars, role - 2) if role >= 2 else na
        return '' if na(markBar) else ' order unknown' if w.reason == END_SAME_BAR and markBar == w.stopBar else ' reached'

    def levelNameOf(role: int):
        return 'Entry' if role == 0 else 'Stop ' + multText(1.0) if role == 1 else tierName(role - 2)

    def levelHoverOf(w: Wave, role: int):
        rText: str = 'R = Entry to Stop = ' + priceText(w.unit) + '.'
        formula: str = 'The first close back inside the 1–3 line from the bar the wave appears, not already past the 2–4 line, rounded to the tick.' if role == 0 else 'Point 5 beyond by ' + string.tostring(STOP_BEYOND_ATR, '0.##########') + ' × ATR, at least ' + string.tostring(MIN_STOP_ATR, '0.##########') + ' × ATR from Entry, rounded outward to the tick; ATR is the ' + string.tostring(VOLATILITY_LENGTH) + '-bar simple mean of true range when the wave formed. ' + rText if role == 1 else ('Entry plus ' if w.side > 0 else 'Entry minus ') + multText(multOf(role - 2)) + ', rounded outward to the tick and at least one tick beyond the level before it. ' + rText
        return layerPrefix(w.longer) + levelNameOf(role) + ': ' + priceText(levelPriceOf(w, role)) + '\n' + formula + '\n' + DISCLOSURE

    def tiersHoverOf(w: Wave):
        out: str = ""
        for tier, price in enumerate(w.tiers):
            out += tierName(tier) + ': ' + priceText(price) + levelMarkOf(w, tier + 2) + '\n'
        return layerPrefix(w.longer) + out + ('Entry plus' if w.side > 0 else 'Entry minus') + ' each multiple of R, rounded outward to the tick and at least one tick beyond the level before it. R = Entry to Stop = ' + priceText(w.unit) + '.\n' + DISCLOSURE

    def targetCleared(w: Wave, role: int):
        return role >= 2 and onCloseInput == 'Clear' and (levelMarkOf(w, role) == ' reached')

    def firstRemaining(w: Wave):
        found: int = -1
        for tier, price in enumerate(w.tiers):
            if found == -1 and (not targetCleared(w, tier + 2)):
                found = tier
        return found

    def opaqueTag(tint: Color):
        weight: float = 1.0 - color.t(tint) / 100.0
        bg: Color = chart.bg_color
        return color.rgb(math.round(color.r(tint) * weight + color.r(bg) * (1.0 - weight)), math.round(color.g(tint) * weight + color.g(bg) * (1.0 - weight)), math.round(color.b(tint) * weight + color.b(bg) * (1.0 - weight)), 0)

    def tagTextOf(w: Wave, k: int):
        out: str = levelNameOf(k) + levelMarkOf(w, k) if k <= 1 else ''
        if k == 2:
            for tier, price in enumerate(w.tiers):
                if not targetCleared(w, tier + 2):
                    mark: str = levelMarkOf(w, tier + 2)
                    out += (' · ' if out != '' else '') + 'T' + string.tostring(tier + 1) + (' ✓' if mark == ' reached' else mark)
        return '' if out == '' else layerPrefix(w.longer) + out

    def tagReachedOf(w: Wave, k: int):
        reached: bool = k <= 1 and levelMarkOf(w, k) != ''
        if k == 2:
            __loop_1__ = pine_loop(0)
            while __loop_1__.step(array.size(w.tiers) - 1):
                tier = __loop_1__.value
                reached = reached or levelMarkOf(w, tier + 2) != ''
        return reached

    def pointHoverOf(w: Wave, k: int):
        p: Pivot = array.get(w.points, k)
        return layerPrefix(w.longer) + directionWord(w.side) + ' Wolfe Wave\n' + pointsText(w) if k == 4 else 'Point ' + string.tostring(k + 1) + ': ' + priceText(p.price)

    def drawGeometry(w: Wave, barNow: int):
        tint: Color = waveColor(w)
        guide: Color = addTransparency(tint, GUIDE_FADE)
        for k in pine_range(0, LEGS - 1):
            a: Pivot = array.get(w.points, k)
            b: Pivot = array.get(w.points, k + 1)
            array.push(w.geometry, line.new(a.bar, a.price, b.bar, b.price, xloc=xloc.bar_index, extend=extend.none, color=tint, style=lineStyleOf(zigzagStyleInput), width=strokeOf(widthInput, w.longer)))
        p1: Pivot = array.get(w.points, 0)
        p2: Pivot = array.get(w.points, 1)
        guideX: int = guideRight(w, barNow)
        array.push(w.geometry, line.new(p1.bar, p1.price, guideX, line13At(w, guideX), xloc=xloc.bar_index, extend=extend.none, color=guide, style=lineStyleOf(guideStyleInput), width=strokeOf(guideWidthInput, w.longer)))
        array.push(w.geometry, line.new(p2.bar, p2.price, guideX, line24At(w, guideX), xloc=xloc.bar_index, extend=extend.none, color=guide, style=lineStyleOf(guideStyleInput), width=strokeOf(guideWidthInput, w.longer)))
        array.push(w.geometry, line.new(p1.bar, p1.price, barNow, line14At(w, barNow), xloc=xloc.bar_index, extend=extend.none, color=guide, style=lineStyleOf(l14StyleInput), width=strokeOf(l14WidthInput, w.longer)))
        if fillInput:
            w.wedge = linefill.new(array.get(w.geometry, LINE_L13), array.get(w.geometry, LINE_L24), levelTint(w, waveBase(w), fillTranspInput))
        if pointsInput:
            for k, p in enumerate(w.points):
                array.push(w.pointLabels, label.new(p.bar, p.price, (layerPrefix(w.longer) if k == 4 else '') + string.tostring(k + 1), xloc=xloc.bar_index, yloc=yloc.price, color=CLEAR, style=label.style_label_down if (p.side == 1) != w.longer else label.style_label_up, textcolor=tint, size=textSizeOf(textSizeInput), tooltip=pointHoverOf(w, k)))
        return 0

    def zoneFromOf(w: Wave, role: int):
        return w.entry if role <= 2 else array.get(w.tiers, role - 3)

    def styleLevels(w: Wave):
        for role, id in enumerate(w.levelLines):
            reached: bool = levelMarkOf(w, role) != ''
            cleared: bool = targetCleared(w, role)
            base: Color = levelColorOf(role)
            line.set_color(id, levelTint(w, base, 100 if cleared else ENTRY_LINE_TRANSP if role == 0 else 0 if reached else LEVEL_LINE_TRANSP))
            if role >= 1:
                box.set_bgcolor(array.get(w.levelZones, role - 1), levelTint(w, base, 100 if cleared else ZONE_REACHED_TRANSP if reached else ZONE_TRANSP))
        for k, tag in enumerate(w.levelTags):
            tagCopy: str = tagTextOf(w, k)
            label.set_text(tag, tagCopy)
            reached: bool = tagReachedOf(w, k) and (k != 2 or onCloseInput == 'Keep')
            label.set_color(tag, CLEAR if tagCopy == '' else opaqueTag(levelTint(w, levelColorOf(k), TAG_REACHED_TRANSP if reached else TAG_TRANSP)))
            label.set_textcolor(tag, chart.fg_color)
            if k == 2:
                remaining: int = firstRemaining(w) if onCloseInput == 'Clear' else 0
                if remaining >= 0:
                    label.set_y(tag, array.get(w.tiers, remaining))
                label.set_tooltip(tag, '' if tagCopy == '' else tiersHoverOf(w))
        return 0

    def drawLevels(w: Wave, barNow: int):
        __loop_0__ = pine_loop(0)
        while __loop_0__.step(1 + array.size(w.tiers)):
            role = __loop_0__.value
            price: float = levelPriceOf(w, role)
            array.push(w.levelLines, line.new(w.entryBar, price, barNow, price, xloc=xloc.bar_index, extend=extend.none, color=CLEAR, style=line.style_dotted, width=1))
            if role <= 2:
                array.push(w.levelTags, label.new(barNow, price, '', xloc=xloc.bar_index, yloc=yloc.price, color=CLEAR, style=label.style_label_left, textcolor=chart.fg_color, size=textSizeOf(textSizeInput), tooltip=levelHoverOf(w, role) if role <= 1 else ''))
            if role >= 1:
                zoneStart: float = zoneFromOf(w, role)
                array.push(w.levelZones, box.new(w.entryBar, math.max(zoneStart, price), barNow, math.min(zoneStart, price), border_color=CLEAR, border_width=0, xloc=xloc.bar_index, bgcolor=CLEAR))
        return styleLevels(w)

    def syncDrawings(w: Wave, barNow: int):
        if array.size(w.geometry) == 0:
            drawGeometry(w, barNow)
        if levelsInput and (not na(w.entry)) and (array.size(w.levelLines) == 0):
            drawLevels(w, barNow)
        if w.dirty:
            styleLevels(w)
            w.dirty = False
        return 0

    def extendTo(w: Wave, x: int):
        guideX: int = guideRight(w, x)
        line.set_xy2(array.get(w.geometry, LINE_L13), guideX, line13At(w, guideX))
        line.set_xy2(array.get(w.geometry, LINE_L24), guideX, line24At(w, guideX))
        line.set_xy2(array.get(w.geometry, LINE_L14), x, line14At(w, x))
        for id in w.levelLines:
            line.set_x2(id, x)
        for id in w.levelTags:
            label.set_x(id, x)
        for id in w.levelZones:
            box.set_right(id, x)
        return 0

    def cutWave(w: Wave):
        extendTo(w, w.endBar)
        tint: Color = waveColor(w)
        for k, id in enumerate(w.geometry):
            line.set_color(id, tint if k < LEGS else addTransparency(tint, GUIDE_FADE))
        for id in w.pointLabels:
            label.set_textcolor(id, tint)
        if not na(w.wedge):
            linefill.set_color(w.wedge, levelTint(w, waveBase(w), fillTranspInput))
        return styleLevels(w)

    def deleteDrawings(w: Wave):
        if not na(w.wedge):
            linefill.delete(w.wedge)
            w.wedge = na
        for id in w.geometry:
            line.delete(id)
        for id in w.levelLines:
            line.delete(id)
        for id in w.pointLabels:
            label.delete(id)
        for id in w.levelTags:
            label.delete(id)
        for id in w.levelZones:
            box.delete(id)
        array.clear(w.geometry)
        array.clear(w.levelLines)
        array.clear(w.pointLabels)
        array.clear(w.levelTags)
        array.clear(w.levelZones)
        return 0

    def formingHoverOf(f: Forming, longer: bool = False):
        return layerPrefix(longer) + 'Developing ' + directionWord(f.side) + ' Wolfe Wave: points 1–4 confirmed, no point 5 yet.\nThe band runs from the 1–3 line to ' + string.tostring(OVERSHOOT_ATR, '0.0##') + ' × ATR beyond it at candidate selection; ATR is a 14-bar simple mean of true range. A pivot ' + ('low' if f.side > 0 else 'high') + ' would sit on or beyond the 1–3 line, no more than that far past it at this frozen volatility. Admission uses its then-current volatility.\nDrawn to the latest bar only; hidden intrabar beyond the band or at the apex, and cleared on confirmed invalidation.\nIt says nothing about what price will do there.'

    def sameForming(a: Forming, b: Forming):
        same: bool = not na(a) and (not na(b))
        if same:
            same = a.side == b.side and a.atr == b.atr
            for k in pine_range(0, LEGS - 1):
                p: Pivot = array.get(a.points, k)
                q: Pivot = array.get(b.points, k)
                same = same and p.bar == q.bar and (p.price == q.price)
        return same

    def clearForming(lines: list[Line], labels: list[Label], fills: list[LineFill]):
        for id in fills:
            linefill.delete(id)
        for id in lines:
            line.delete(id)
        for id in labels:
            label.delete(id)
        array.clear(fills)
        array.clear(lines)
        array.clear(labels)
        return 0

    def drawForming(f: Forming, x: int, lines: list[Line], labels: list[Label], fills: list[LineFill], longer: bool = False, bandFill: bool = True):
        tint: Color = addTransparency(bullInput if f.side == 1 else bearInput, FORMING_FADE)
        guide: Color = addTransparency(tint, GUIDE_FADE)
        for k in pine_range(0, LEGS - 2):
            a: Pivot = array.get(f.points, k)
            b: Pivot = array.get(f.points, k + 1)
            array.push(lines, line.new(a.bar, a.price, b.bar, b.price, xloc=xloc.bar_index, extend=extend.none, color=tint, style=line.style_dashed, width=strokeOf(widthInput, longer)))
        p1: Pivot = array.get(f.points, 0)
        p2: Pivot = array.get(f.points, 1)
        p4: Pivot = array.get(f.points, 3)
        slope24: float = (p4.price - p2.price) / (p4.bar - p2.bar)
        array.push(lines, line.new(p1.bar, p1.price, x, formingLineAt(f, x), xloc=xloc.bar_index, extend=extend.none, color=guide, style=line.style_dashed, width=strokeOf(guideWidthInput, longer)))
        array.push(lines, line.new(p2.bar, p2.price, x, p2.price + slope24 * (x - p2.bar), xloc=xloc.bar_index, extend=extend.none, color=guide, style=line.style_dashed, width=strokeOf(guideWidthInput, longer)))
        nearEdge: Line = line.new(p4.bar, formingLineAt(f, p4.bar), x, formingLineAt(f, x), xloc=xloc.bar_index, extend=extend.none, color=CLEAR, width=1)
        farEdge: Line = line.new(p4.bar, formingFarAt(f, p4.bar), x, formingFarAt(f, x), xloc=xloc.bar_index, extend=extend.none, color=guide, style=line.style_dotted, width=1)
        array.push(lines, nearEdge)
        array.push(lines, farEdge)
        if bandFill:
            array.push(fills, linefill.new(nearEdge, farEdge, addTransparency(bullInput if f.side == 1 else bearInput, FORMING_ZONE_TRANSP)))
        if pointsInput:
            for k, p in enumerate(f.points):
                array.push(labels, label.new(p.bar, p.price, string.tostring(k + 1), xloc=xloc.bar_index, yloc=yloc.price, color=CLEAR, style=label.style_label_down if (p.side == 1) != longer else label.style_label_up, textcolor=tint, size=textSizeOf(textSizeInput)))
        mid: float = (formingLineAt(f, x) + formingFarAt(f, x)) / 2
        array.push(labels, label.new(x, mid, layerPrefix(longer) + 'Developing · point 5 band', xloc=xloc.bar_index, yloc=yloc.price, color=addTransparency(bullInput if f.side == 1 else bearInput, TAG_TRANSP), style=label.style_label_right if longer else label.style_label_left, textcolor=chart.fg_color, size=textSizeOf(textSizeInput), tooltip=formingHoverOf(f, longer)))
        return 0

    def retireEnded(live: list[Wave], kept: list[Wave]):
        n: int = array.size(live)
        if n > 0:
            ended: list[Wave] = array.new(0, NA(Wave))
            for idx in pine_range(n - 1, 0):
                if array.get(live, idx).state == ST_ENDED:
                    array.unshift(ended, array.remove(live, idx))
            for w in ended:
                array.unshift(kept, w)
        return 0

    def evictKept(kept: list[Wave], barNow: int):
        n: int = array.size(kept)
        if n > 0:
            for idx in pine_range(n - 1, 0):
                w: Wave = array.get(kept, idx)
                if idx >= keptInput or barNow - array.get(w.points, 0).bar > DRAW_MAX_BACK:
                    deleteDrawings(w)
                    array.remove(kept, idx)
        return 0

    def panelPosition(newest: Wave):
        chosen: str = positionInput
        if chosen == POS_AUTO:
            chosen = POS_BOTTOM_LEFT if not na(newest) and newest.side == 1 else POS_TOP_RIGHT
        __block_result_7__ = na
        __switch__ = chosen
        if __switch__ == POS_TOP_LEFT:
            __block_result_7__ = position.top_left
        elif __switch__ == POS_BOTTOM_RIGHT:
            __block_result_7__ = position.bottom_right
        elif __switch__ == POS_BOTTOM_LEFT:
            __block_result_7__ = position.bottom_left
        else:
            __block_result_7__ = position.top_right
        return __block_result_7__

    def panelCell(panel: Table, column: int, row: int, body: str, tint: Color, hover: str, back: Color):
        table.cell(panel, column, row, body, text_color=tint, text_size=textSizeOf(textSizeInput), text_halign=text.align_left, tooltip=hover, bgcolor=back)
        return 0

    def panelNote(panel: Table, row: int, body: str):
        back: Color = FILL_LIGHT if lightChart() else FILL_DARK
        panelCell(panel, 0, row, body, guideColor(), '', back)
        for column in pine_range(1, PANEL_WAVES):
            panelCell(panel, column, row, '', guideColor(), '', back)
        table.merge_cells(panel, 0, row, PANEL_WAVES, row)
        return row + 1

    def panelSpacer(panel: Table, row: int):
        for column in pine_range(0, PANEL_WAVES):
            table.cell(panel, column, row, ' ', text_size=textSizeOf(textSizeInput))
        return row + 1

    def reasonShort(reason: int):
        __block_result_8__ = na
        __switch__ = reason
        if __switch__ == END_BEYOND_FIVE:
            __block_result_8__ = "beyond point 5"
        elif __switch__ == END_NO_ENTRY:
            __block_result_8__ = "no Entry"
        elif __switch__ == END_PAST_24:
            __block_result_8__ = "past 2–4 line"
        else:
            __block_result_8__ = reasonWord(reason)
        return __block_result_8__

    def stateText(w: Wave):
        return 'Waiting' if w.state == ST_WAITING else 'Entry set' if w.state == ST_ENTERED else 'Ended · ' + reasonShort(w.reason)

    def stateHoverOf(w: Wave):
        now: str = 'No close back inside the 1–3 line yet.' if w.state == ST_WAITING else 'Entry set; levels tracked.' if w.state == ST_ENTERED else 'Ended: ' + reasonWord(w.reason) + (', as many bars after Entry as the wave took to form' if w.reason == END_AGED else '') + '.'
        return layerPrefix(w.longer) + now + ('\nPoint 5 confirmed ' + string.tostring(w.admitBar - array.get(w.points, 4).bar) + ' bars after its bar.' if w.longer else '') + '\nFormed ' + stampText(w.admitTime) + ' · ' + keyText(w)

    def panelWaves(panel: Table, waves: list[Wave]):
        back: Color = FILL_LIGHT if lightChart() else FILL_DARK
        rows: int = 2 + (5 if multsValid() else 2)
        for role in pine_range(-2, rows - 3):
            name: str = 'Wolfe Wave' if role == -2 else 'State' if role == -1 else levelNameOf(role)
            panelCell(panel, 0, role + 2, name, guideColor(), 'Newest first.' if role == -2 else '', back)
        for column, w in enumerate(waves):
            x: int = column + 1
            panelCell(panel, x, 0, layerPrefix(w.longer) + directionWord(w.side), waveColor(w), pointsText(w), back)
            panelCell(panel, x, 1, stateText(w), inkColor(), stateHoverOf(w), back)
            for role in pine_range(0, rows - 3):
                has: bool = not na(w.entry) and role <= 1 + array.size(w.tiers)
                mark: str = levelMarkOf(w, role) if has else ''
                marked: bool = mark != ''
                panelCell(panel, x, role + 2, priceText(levelPriceOf(w, role)) + mark if has else '—', LEVEL_TEXT if marked else inkColor(), levelHoverOf(w, role) if has else 'No Entry yet.' if w.state == ST_WAITING else 'No Entry was set.', addTransparency(levelColorOf(role), REACHED_TRANSP) if marked else back)
        return rows

    chain: Persistent[list[Pivot]] = array.new(0, NA(Pivot))
    seenKeys: Persistent[list[str]] = array.new_string()
    refusedKeys: Persistent[list[str]] = array.new_string()
    liveWaves: Persistent[list[Wave]] = array.new(0, NA(Wave))
    keptWaves: Persistent[list[Wave]] = array.new(0, NA(Wave))
    newestWave: Persistent[Wave] = na(Wave)
    capacitySkipped: Persistent[int] = 0
    reachSkipped: Persistent[int] = 0
    forming: Persistent[Forming] = na(Forming)
    formingLines: Persistent[list[Line]] = array.new_line()
    formingLabels: Persistent[list[Label]] = array.new_label()
    formingFills: Persistent[list[LineFill]] = array.new_linefill()
    longerChain: Persistent[list[Pivot]] = array.new(0, NA(Pivot))
    longerSeenKeys: Persistent[list[str]] = array.new_string()
    longerRefusedKeys: Persistent[list[str]] = array.new_string()
    longerCapacitySkipped: Persistent[int] = 0
    longerReachSkipped: Persistent[int] = 0
    longerForming: Persistent[Forming] = na(Forming)
    longerFormingLines: Persistent[list[Line]] = array.new_line()
    longerFormingLabels: Persistent[list[Label]] = array.new_label()
    longerFormingFills: Persistent[list[LineFill]] = array.new_linefill()
    recentWaves: Persistent[list[Wave]] = array.new(0, NA(Wave))
    panel: Persistent[Table] = table.new(position.top_right, PANEL_WAVES + 1, PANEL_ROWS, border_width=0)

    flags: list[int] = array.new_int(4, 0)
    messages: list[str] = array.new_string()

    supported: bool = chart.is_standard and (not timeframe.isticks)
    pricesValid: bool = not na(high) and (not na(low)) and (not na(close))

    pivotHigh: float = ta.pivothigh(high, swingInput, swingInput)
    pivotLow: float = ta.pivotlow(low, swingInput, swingInput)
    pivotStamp: int = time[swingInput]
    longerPivotHigh: float = ta.pivothigh(high, longerStrengthInput, longerStrengthInput)
    longerPivotLow: float = ta.pivotlow(low, longerStrengthInput, longerStrengthInput)
    longerPivotStamp: int = time[longerStrengthInput]
    trueRange: float = ta.tr(True)
    volatility: float = ta.sma(trueRange, VOLATILITY_LENGTH)

    if barstate.isconfirmed and supported and pricesValid:
        for w in liveWaves:
            if w.state == ST_WAITING:
                stepWaiting(w, bar_index, flags, messages)
            elif w.state == ST_ENTERED and bar_index > w.entryBar:
                stepEntered(w, bar_index, flags, messages)
        trimAge(chain, bar_index)

        offered: list[Pivot] = array.new(0, NA(Pivot))
        if not na(pivotHigh):
            array.push(offered, Pivot(bar_index - swingInput, pivotStamp, pivotHigh, 1))
        if not na(pivotLow):
            array.push(offered, Pivot(bar_index - swingInput, pivotStamp, pivotLow, -1))
        chainChanged: bool = False
        for pivot in offered:
            if acceptPivot(chain, pivot):
                chainChanged = True
                status, admitted = tryAdmit(chain, seenKeys, refusedKeys, liveWaves, bar_index, volatility, flags, messages)
                if status == 1:
                    newestWave = admitted
                    array.unshift(recentWaves, admitted)
                    if array.size(recentWaves) > PANEL_WAVES:
                        array.pop(recentWaves)
                elif status == 2:
                    capacitySkipped += 1
                elif status == 3:
                    reachSkipped += 1

        if chainChanged:
            forming = selectForming(chain, volatility, seenKeys, bar_index)
        elif not na(forming):
            forming = forming if formingHolds(forming, bar_index, bar_index) else na
        if longerInput:
            trimAge(longerChain, bar_index)

            longerOffered: list[Pivot] = array.new(0, NA(Pivot))
            if not na(longerPivotHigh):
                array.push(longerOffered, Pivot(bar_index - longerStrengthInput, longerPivotStamp, longerPivotHigh, 1))
            if not na(longerPivotLow):
                array.push(longerOffered, Pivot(bar_index - longerStrengthInput, longerPivotStamp, longerPivotLow, -1))
            longerChainChanged: bool = False
            for longerPivot in longerOffered:
                if acceptPivot(longerChain, longerPivot):
                    longerChainChanged = True
                    longerStatus, longerAdmitted = tryAdmit(longerChain, longerSeenKeys, longerRefusedKeys, liveWaves, bar_index, volatility, flags, messages, True)
                    if longerStatus == 1:
                        newestWave = longerAdmitted
                        array.unshift(recentWaves, longerAdmitted)
                        if array.size(recentWaves) > PANEL_WAVES:
                            array.pop(recentWaves)
                    elif longerStatus == 2:
                        longerCapacitySkipped += 1
                    elif longerStatus == 3:
                        longerReachSkipped += 1

            if longerChainChanged:
                longerForming = selectForming(longerChain, volatility, longerSeenKeys, bar_index)
            elif not na(longerForming):
                longerForming = longerForming if formingHolds(longerForming, bar_index, bar_index) else na

        retireEnded(liveWaves, keptWaves)
        evictKept(keptWaves, bar_index)
        for w in liveWaves:
            syncDrawings(w, bar_index)
        for w in keptWaves:
            if w.endBar == bar_index:
                syncDrawings(w, bar_index)
                cutWave(w)

    if barstate.islast:
        if supported:
            for w in liveWaves:
                extendTo(w, bar_index)
        clearForming(formingLines, formingLabels, formingFills)
        clearForming(longerFormingLines, longerFormingLabels, longerFormingFills)
        if supported and formingInput and (not na(forming)) and formingHolds(forming, bar_index, bar_index):
            drawForming(forming, bar_index, formingLines, formingLabels, formingFills)
        if supported and longerInput and formingInput and (not na(longerForming)) and formingHolds(longerForming, bar_index, bar_index):
            drawForming(longerForming, bar_index, longerFormingLines, longerFormingLabels, longerFormingFills, True, not sameForming(forming, longerForming))
        notes: list[str] = array.new_string()
        if not supported:
            array.push(notes, 'This chart type is not supported: Auto Wolfe Waves reads standard bars on a time-based timeframe, so nothing is drawn.')
        else:
            if not multsValid():
                array.push(notes, 'T1 (R), T2 (R) and T3 (R) do not increase, so no T levels are built; Entry and Stop still are.')
            if not tickValid():
                array.push(notes, 'Tick size unavailable: levels are not rounded to the tick.')
            if capacitySkipped > 0 or longerCapacitySkipped > 0:
                array.push(notes, 'Waves skipped while four were live: ' + ('Main: ' if longerInput else '') + string.tostring(capacitySkipped) + (' · Longer: ' + string.tostring(longerCapacitySkipped) if longerInput else ''))
            if reachSkipped > 0 or longerReachSkipped > 0:
                array.push(notes, 'Waves not drawn on the loaded bars because point 1 was over 4,500 bars back: ' + ('Main: ' if longerInput else '') + string.tostring(reachSkipped) + (' · Longer: ' + string.tostring(longerReachSkipped) if longerInput else ''))
        table.clear(panel, 0, 0, PANEL_WAVES, PANEL_ROWS - 1)
        where: str = panelPosition(newestWave)
        table.set_position(panel, where)
        row: int = 0
        if panelInput and supported and (array.size(recentWaves) > 0):
            row = panelWaves(panel, recentWaves)
        for note in notes:
            row = panelNote(panel, row, note)
        if row > 0 and (where == position.bottom_left or where == position.bottom_right):
            row = panelSpacer(panel, row)

    plot(na if na(newestWave) else newestWave.side, 'Direction', color=PLOT_TINT, display=display.data_window)
    plot(na if na(newestWave) else newestWave.state, 'State', color=PLOT_TINT, display=display.data_window)

    alertcondition(array.get(flags, EV_FORMED) == 1, 'Wolfe Wave formed', 'Auto Wolfe Waves [AFD]: a Wolfe Wave formed on this confirmed bar.')
    alertcondition(array.get(flags, EV_ENTRY) == 1, 'Wolfe Wave Entry', "Auto Wolfe Waves [AFD]: a Wolfe Wave's Entry was set on this confirmed bar.")
    alertcondition(array.get(flags, EV_LEVEL) == 1, 'Wolfe Wave level reached', "Auto Wolfe Waves [AFD]: a bar traded to a Wolfe Wave's T level on this confirmed bar.")
    alertcondition(array.get(flags, EV_ENDED) == 1, 'Wolfe Wave ended', 'Auto Wolfe Waves [AFD]: a Wolfe Wave ended on this confirmed bar.')

    if array.size(messages) > 0:
        batch: str = 'Auto Wolfe Waves [AFD] | ' + syminfo.tickerid + ' | ' + timeframe.period + '\n' + array.join(messages, '\n')
        if detailInput == DETAIL_JSON:
            batch = '{"schema":1,"build":' + jsonString(BUILD_ID) + ',"product":"Auto Wolfe Waves [AFD]","ticker":' + jsonString(syminfo.tickerid) + ',"timeframe":' + jsonString(timeframe.period) + ',"config":' + configurationJson() + ',"events":[' + array.join(messages, ',') + ']}'
        alert(batch, alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)