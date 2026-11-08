"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore import pine_loop, pine_range
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barstate, chart, close, color,
    display, extend, format, high, input, label, line, linefill, low, math, na, plot, position,
    script, size, string, syminfo, table, text, time, timeframe, xloc, yloc
)
from pynecore.types import Color, Label, Line, LineFill, NA, Persistent, Table


@udt
class BarData:
    index: int = na(int)
    stamp: int = na(int)
    hi: float = na(float)
    lo: float = na(float)
    last: float = na(float)
    valid: bool = na(bool)


@udt
class Pivot:
    index: int = na(int)
    stamp: int = na(int)
    price: float = na(float)


@udt
class Channel:
    a: 'Pivot' = _dataclass_field(default_factory=lambda: na(Pivot))
    b: 'Pivot' = _dataclass_field(default_factory=lambda: na(Pivot))
    c: 'Pivot' = _dataclass_field(default_factory=lambda: na(Pivot))
    direction: int = na(int)
    layer: int = na(int)
    slope: float = na(float)
    width: float = na(float)
    volatility: float = na(float)
    containment: float = na(float)
    allowance: float = na(float)
    constructed: int = na(int)
    key: str = na(str)
    available: int = -1
    availableTime: int = -1
    state: int = 0
    breakBar: int = -1
    breakTime: int = -1
    breakSide: int = 0
    returnBar: int = -1
    returnTime: int = -1
    retestBar: int = -1
    retestTime: int = -1
    endBar: int = -1
    retired: int = -1


@udt
class Layer:
    highsArray: 'list[Pivot]' = na(list)
    lowsArray: 'list[Pivot]' = na(list)
    pendingArray: 'list[Channel]' = na(list)


@udt
class AcceptedKey:
    key: str = na(str)
    anchor: int = na(int)


@udt
class Drawing:
    channel: 'Channel' = _dataclass_field(default_factory=lambda: na(Channel))
    linesArray: list[Line] = na(list)
    labelsArray: list[Label] = na(list)
    fill__ren__: LineFill = na(LineFill)


DETECTION: str = "Detection"
LIFECYCLE: str = "Lifecycle"
DISPLAY: str = "Display"
ALERTS: str = "Alerts"
PENDING: int = 0
ACTIVE: int = 1
WATCH: int = 2
RETURNED: int = 3
ENDED: int = 4
AGED: int = 5
FORMED: int = 1
ABOVE: int = 2
BELOW: int = 3
RETURN: int = 4
RETEST: int = 5
HORIZON_MAX: int = 2000
RING_SIZE: int = HORIZON_MAX + 1
PENDING_CAP: int = 32
PENDING_WAIT: int = 20
PANEL_FULL: str = "Full"
PANEL_NOTICE: str = "Disclosure only"
PANEL_OFF: str = "Off"
THEME_SIGNATURE: str = "Signature"
THEME_CONTRAST: str = "High contrast"
THEME_PAPER: str = "Paper (light chart)"
THEME_MUTED: str = "Muted"
THEME_CBSAFE: str = "Colourblind safe"
THEME_MONO: str = "Monochrome"
THEME_WARM: str = "Warm"
THEME_COOL: str = "Cool"
THEME_CUSTOM: str = "Custom"
LABEL_ON_LINE: str = "On line"
LABEL_RIGHT: str = "Right of line"
SIZE_TINY: str = "Tiny"
SIZE_SMALL: str = "Small"
SIZE_NORMAL: str = "Normal"
LABEL_LEAD_BARS: int = 6
LABEL_CLEARANCE: float = 0.35
PANEL_ROWS: int = 13
SIG_RISING: Color = color.new('#26A69A')
SIG_FALLING: Color = color.new('#EF5350')
SIG_HISTORY: Color = color.new('#9AA0A6')
HC_RISING: Color = color.new('#00E676')
HC_FALLING: Color = color.new('#FF1744')
HC_HISTORY: Color = color.new('#FFFFFF')
PAP_RISING: Color = color.new('#00695C')
PAP_FALLING: Color = color.new('#B71C1C')
PAP_HISTORY: Color = color.new('#546E7A')
MUT_RISING: Color = color.new('#4C9A8F')
MUT_FALLING: Color = color.new('#B0645F')
MUT_HISTORY: Color = color.new('#78808A')
CB_RISING: Color = color.new('#0072B2')
CB_FALLING: Color = color.new('#D55E00')
CB_HISTORY: Color = color.new('#999999')
MON_RISING: Color = color.new('#FFFFFF')
MON_FALLING: Color = color.new('#9E9E9E')
MON_HISTORY: Color = color.new('#5F6A6A')
WRM_RISING: Color = color.new('#F9A825')
WRM_FALLING: Color = color.new('#C62828')
WRM_HISTORY: Color = color.new('#8D6E63')
COL_RISING: Color = color.new('#26C6DA')
COL_FALLING: Color = color.new('#5C6BC0')
COL_HISTORY: Color = color.new('#78909C')


@script.indicator("Auto Trend Channels [AFD]", "ATCH [AFD]", overlay=True, max_lines_count=100, max_labels_count=125, max_bars_back=2002)
def main(
    swingInput=input.int(8, "Swing length", minval=2, maxval=30, group=DETECTION, tooltip="Bars required either side of a pivot.\n• A pivot confirms this many bars after it prints\n• Equal extrema never anchor, nor does a bar that is both a pivot high and a pivot low\n• Raise 8 to 16: pivots confirm 8 bars later, fewer and larger channels. Lower to 4: more, smaller ones, sooner", display=display.none),
    longerInput=input.bool(False, "Longer swing channel", group=DETECTION, tooltip="Adds a second, larger channel over the swing layer.\n• Same timeframe; a longer swing length set by the multiple below\n• Draws thicker and fainter to stay distinguishable\n• On: roughly doubles the work per bar and adds one live slot to the drawn ceiling, unless the horizon is under 3 × its swing length, when the layer stays off and the panel says so"),
    multipleInput=input.int(3, "Longer swing multiple", minval=2, maxval=4, group=DETECTION, tooltip="Scale of the second layer.\n• Multiplies the swing length above; chart timeframe throughout, no higher-timeframe request\n• At swing length 8, multiple 3 gives a 24-bar pivot; 4 gives 32, so its channels confirm later and span more", display=display.none),
    poolInput=input.int(10, "Pivots searched", minval=3, maxval=12, group=DETECTION, tooltip="Recent pivots considered per construction.\n• Limited to pivots inside the horizon below\n• Raise 10 to 12: reaches further back, finds more geometry, costs more per bar. Lower to 5: only the latest pivots pair", display=display.none),
    horizonInput=input.int(600, "Search and age horizon", minval=100, maxval=HORIZON_MAX, group=DETECTION, tooltip="Maximum reach and age of a channel, in bars.\n• Measured from the first anchor; older channels are retired\n• The longer swing layer needs at least 3 × its own swing length\n• Raise 600 to 1200: channels may reach and live twice as far back. Lower to 200: a channel retires 200 bars after its first anchor", display=display.none),
    volatilityInput=input.int(14, "Volatility window", minval=5, maxval=100, group=DETECTION, tooltip="Average range that sizes every allowance below.\n• Simple average true range, not Wilder smoothing; frozen at construction, so geometry never shifts\n• A gap in the window prevents construction\n• Raise 14 to 50: allowances follow a slower average and react less to one volatile week", display=display.none),
    containmentInput=input.float(0.1, "Containment allowance", minval=0.0, maxval=0.5, step=0.05, group=DETECTION, tooltip="Tolerance for price outside the boundaries.\n• A multiple of the frozen average range; the full span between anchors must fit\n• 0 requires an exact fit\n• Raise 0.10 to 0.30: a wick poking 0.3 ranges past a boundary no longer rejects the channel, so more channels pass", display=display.none),
    minWidthInput=input.float(0.5, "Minimum width", minval=0.1, maxval=5.0, step=0.1, group=DETECTION, tooltip="Rejects channels narrower than this.\n• A multiple of the frozen average range\n• Raise 0.5 to 1.5: a channel narrower than 1.5 average ranges is rejected, so tight consolidation is excluded", display=display.none),
    maxWidthInput=input.float(8.0, "Maximum width", minval=1.0, maxval=20.0, step=0.5, group=DETECTION, tooltip="Rejects channels wider than this.\n• A multiple of the frozen average range\n• Lower 8 to 4: a channel wider than 4 average ranges is rejected, so a drawing spanning unrelated ranges is excluded", display=display.none),
    closeInput=input.float(0.0, "Close allowance", minval=0.0, maxval=1.0, step=0.05, group=LIFECYCLE, tooltip="Distance a close must clear a boundary to break it.\n• A multiple of the frozen average range; 0 accepts any close beyond\n• A close on the boundary counts as inside\n• Raise 0 to 0.25: a close 0.1 ranges past the boundary is still inside, so marginal closes no longer start a watch", display=display.none),
    watchInput=input.int(20, "Return watch", minval=1, maxval=50, group=LIFECYCLE, tooltip="Bars a channel is watched after a close outside.\n• Counted in closed bars from that first close; a return on the final watched bar counts\n• The channel is finished afterwards and does not restart\n• Raise 20 to 40: a close back inside up to 40 bars later still ends as Returned inside. Lower to 5: after 5 bars it reads Watch ended", display=display.none),
    retainedInput=input.int(3, "Retained channels", minval=0, maxval=10, group=DISPLAY, tooltip="Finished channels kept on the chart, across both layers.\n• Ceiling is this figure plus one live slot per enabled layer; the panel Drawn row reports the total\n• A hidden channel still runs its watch and still alerts\n• 0: live channels only. Raise 3 to 6: the six most recently finished channels stay drawn", display=display.none),
    midpointInput=input.bool(True, "Midpoint", group=DISPLAY, tooltip="Halfway line between the boundaries.\n• Dotted, fainter than the boundaries; no additional drawing budget\n• Off: the two boundaries and the fill alone"),
    quartersInput=input.bool(False, "Quarter lines", group=DISPLAY, tooltip="Quarter and three-quarter lines inside the channel.\n• With the midpoint, divides the channel into four bands\n• On: two extra lines per channel, so with the midpoint each channel draws five lines"),
    labelsInput=input.bool(True, "Channel labels", group=DISPLAY, tooltip="Draws every label the script produces.\n• Off removes the Known marker, endpoint, event, anchor and forming labels\n• The dotted acceptance line and the stroke styles still draw\n• Off: a channel carries no text saying which bar it became usable at or whether it is active"),
    anchorsInput=input.bool(False, "Anchor markers", group=DISPLAY, tooltip="Marks the three source pivots as A, B and C.\n• Shows where the geometry came from, not when it became usable\n• Drawn only while Channel labels is on\n• On: three extra labels per channel, at the pivot high and low prices"),
    formingInput=input.bool(False, "Forming channel", group=DISPLAY, tooltip="Draws the candidate a layer is currently building.\n• Dotted, faint and labelled: not an accepted channel\n• A channel becomes usable only once a bar closes inside it; the candidate can change or be replaced before then\n• On: while a layer has no active channel, its best pending candidate shows for up to 20 bars"),
    tableInput=input.bool(True, "Corner table", group=DISPLAY, tooltip="Draws the corner table that carries the panel and the disclosure.\n• Off removes the table, including the linear-price and confirmed-pivot notice\n• An unsupported-chart or invalid-settings warning still shows in the corner\n• Off: Status panel and Panel position have no effect"),
    panelInput=input.string(PANEL_OFF, "Status panel", options=(PANEL_FULL, PANEL_NOTICE, PANEL_OFF), group=DISPLAY, tooltip="Extent of the corner panel.\n• Full: the title, per-layer rows, drawn count and disclosure\n• Disclosure only: the title above the disclosure\n• Off: the disclosure alone, pinned in the chosen corner\n• Corner table off removes all three; a blocking warning is never hidden", display=display.none),
    positionInput=input.string("Top right", "Panel position", options=("Top right", "Top left", "Bottom right", "Bottom left"), group=DISPLAY, tooltip="Corner the panel occupies.\n• Applied as soon as the setting is confirmed\n• Top left sits under the chart's own symbol and indicator legends, which the script cannot move; the other three corners are clear of them\n• Bottom left: the table moves under the price action on the left, clear of the price axis", display=display.none),
    boundaryInput=input.int(2, "Boundary width", minval=1, maxval=4, group=DISPLAY, tooltip="Stroke weight of the two boundaries.\n• The longer swing layer draws one step heavier\n• Raise 2 to 3: swing boundaries draw at 3 and longer swing at 4. At 4 both draw at 4 and the difference is lost", display=display.none),
    fillInput=input.bool(True, "Channel fill", group=DISPLAY, tooltip="Shades the inside of the active channel.\n• Off draws the boundaries and inner lines alone, in their usual colours\n• Finished channels are never shaded either way\n• Off: the fill transparency below has no effect"),
    transparencyInput=input.int(80, "Fill transparency", minval=0, maxval=100, group=DISPLAY, tooltip="Shading between the boundaries.\n• 0 is solid, 100 is invisible; added to the direction colour\n• Live channels only; finished channels are unshaded\n• Lower 80 to 60: the active channel's shading darkens. 100: boundaries only", display=display.none),
    themeInput=input.string(THEME_SIGNATURE, "Colour theme", options=(THEME_SIGNATURE, THEME_CONTRAST, THEME_PAPER, THEME_MUTED, THEME_CBSAFE, THEME_MONO, THEME_WARM, THEME_COOL, THEME_CUSTOM), group=DISPLAY, tooltip="Sets the rising, falling and history colours together.\n• Paper is built for a light background; the others for dark\n• Colourblind safe uses the published Okabe-Ito blue and vermilion\n• History is the neutral for any channel that is not the active one, under watch or finished\n• Custom: the three pickers below take over", display=display.none),
    risingInput=input.color(color.new('#26A69A'), "Rising", group=DISPLAY, tooltip="Colour for a live channel sloping up.\n• Applies only when the theme is Custom\n• Also tints that channel's labels and shading"),
    fallingInput=input.color(color.new('#EF5350'), "Falling", group=DISPLAY, tooltip="Colour for a live channel sloping down.\n• Applies only when the theme is Custom\n• Also tints that channel's labels and shading"),
    historyInput=input.color(color.new('#9AA0A6'), "History", group=DISPLAY, tooltip="Colour for a finished channel, either direction.\n• Applies only when the theme is Custom\n• Keep it muted: it marks what is no longer live\n• A channel under watch or finished takes this colour whatever its direction"),
    labelPosInput=input.string(LABEL_ON_LINE, "Label position", options=(LABEL_ON_LINE, LABEL_RIGHT), group=DISPLAY, tooltip="Placement of the channel's state label.\n• On line: at the right edge of the drawing\n• Right of line: six bars past the edge, in open space, so the label clears the stroke\n• Event labels stay at their bars, clear of the candles, in either position", display=display.none),
    labelSizeInput=input.string(SIZE_TINY, "Label size", options=(SIZE_TINY, SIZE_SMALL, SIZE_NORMAL), group=DISPLAY, tooltip="Text size for every label the script draws.\n• Tiny keeps a busy chart readable\n• Normal: each label roughly doubles in height and covers more candles when several channels are retained", display=display.none),
    formationAlertInput=input.bool(True, "Formation", group=ALERTS, tooltip="Fires when a channel is accepted and begins drawing.\n• At the confirmed close of the bar it became usable, not at the pivot\n• The combined alert message carries the channel identity and geometry; the named condition is a fixed message\n• Off: no formation entry in either alert; the Data Window flag still reads 1"),
    outsideAlertInput=input.bool(True, "Close outside", group=ALERTS, tooltip="Fires on the first confirmed close beyond a boundary.\n• Subject to the Close allowance above\n• Starts the return watch; describes the close only\n• Off: the watch still runs and Return inside still fires; only this message is silent"),
    retestAlertInput=input.bool(True, "Boundary retouch", group=ALERTS, tooltip="Fires when price returns to the boundary it closed beyond.\n• The high or low reaches the boundary while the close stays outside\n• Recorded once per channel; never counted, rated or compared\n• Several watched channels retouching on one bar fire this condition once; the combined alert lists each"),
    returnAlertInput=input.bool(True, "Return inside", group=ALERTS, tooltip="Fires when a watched channel closes back inside.\n• Ends the watch; the channel is finished and does not restart\n• Hidden channels still alert\n• Several watched channels returning on one bar fire this condition once; the combined alert lists each")
):
    def getBar(ringArray: list[BarData], index: int):
        result: BarData = na(BarData)
        if index >= 0:
            slot: BarData = array.get(ringArray, index % RING_SIZE)
            if not na(slot) and slot.index == index:
                result = slot
        return result

    def lowerAt(ch: Channel, index: int):
        baseline: float = ch.a.price + ch.slope * (index - ch.a.index)
        return baseline if ch.direction == 1 else baseline - ch.width

    def upperAt(ch: Channel, index: int):
        baseline: float = ch.a.price + ch.slope * (index - ch.a.index)
        return baseline + ch.width if ch.direction == 1 else baseline

    def isInside(ch: Channel, bar: BarData, buffer: float):
        return bar.last >= lowerAt(ch, bar.index) - buffer and bar.last <= upperAt(ch, bar.index) + buffer

    def channelKey(direction: int, a: Pivot, b: Pivot, c: Pivot):
        return string.tostring(direction) + ':' + string.tostring(a.stamp) + ':' + string.tostring(b.stamp) + ':' + string.tostring(c.stamp)

    def strictPivot(ringArray: list[BarData], now: int, strength: int):
        hi: Pivot = na(Pivot)
        lo: Pivot = na(Pivot)
        centerIndex: int = now - strength
        if centerIndex - strength >= 0:
            center: BarData = getBar(ringArray, centerIndex)
            highPivot: bool = not na(center) and center.valid
            lowPivot: bool = highPivot
            if highPivot:
                for index in pine_range(centerIndex - strength, now):
                    neighbor: BarData = getBar(ringArray, index)
                    if na(neighbor) or not neighbor.valid:
                        highPivot = False
                        lowPivot = False
                        break
                    if index != centerIndex:
                        highPivot = highPivot and center.hi > neighbor.hi
                        lowPivot = lowPivot and center.lo < neighbor.lo
            if highPivot != lowPivot:
                if highPivot:
                    hi = Pivot(centerIndex, center.stamp, center.hi)
                else:
                    lo = Pivot(centerIndex, center.stamp, center.lo)
        return (hi, lo)

    def trimPivots(poolArray: list[Pivot], now: int):
        while array.size(poolArray) > 0:
            first: Pivot = array.get(poolArray, 0)
            if now - first.index > horizonInput or array.size(poolArray) > poolInput:
                array.shift(poolArray)
            else:
                break
        return 0

    def constructChannel(ringArray: list[BarData], a: Pivot, c: Pivot, oppositesArray: list[Pivot], direction: int, layer: int, strength: int, now: int, volatility: float):
        result: Channel = na(Channel)
        valid: bool = not na(volatility) and volatility > 0 and (c.index - a.index >= 2 * strength) and (now - a.index <= horizonInput) and (direction * (c.price - a.price) > 0)
        if valid:
            slope: float = (c.price - a.price) / (c.index - a.index)
            b: Pivot = na(Pivot)
            width: float = 0.0
            if array.size(oppositesArray) > 0:
                for p in oppositesArray:
                    if p.index > a.index and p.index < c.index:
                        residual: float = direction * (p.price - (a.price + slope * (p.index - a.index)))
                        if residual > width:
                            width = residual
                            b = p
            if not na(b) and width >= minWidthInput * volatility and (width <= maxWidthInput * volatility):
                candidate: Channel = Channel(a, b, c, direction, layer, slope, width, volatility, containmentInput * volatility, closeInput * volatility, now, channelKey(direction, a, b, c))
                __loop_2__ = pine_loop(a.index)
                while __loop_2__.step(c.index):
                    index = __loop_2__.value
                    bar: BarData = getBar(ringArray, index)
                    if na(bar) or not bar.valid:
                        valid = False
                        break
                    if bar.hi > upperAt(candidate, index) + candidate.containment or bar.lo < lowerAt(candidate, index) - candidate.containment:
                        valid = False
                        break
                if valid:
                    result = candidate
        return result

    def updatePending(pendingArray: list[Channel], bar: BarData):
        index: int = array.size(pendingArray) - 1
        while index >= 0:
            ch: Channel = array.get(pendingArray, index)
            if bar.index - ch.a.index > horizonInput or not bar.valid or bar.index - ch.constructed > PENDING_WAIT:
                array.remove(pendingArray, index)
            index -= 1
        return 0

    def layerName(layer: int):
        return 'Swing' if layer == 0 else 'Longer swing'

    def recordEvent(kind: int, ch: Channel, bar: BarData, flagsArray: list[int], messagesArray: list[str]):
        array.set(flagsArray, ch.layer * 5 + kind - 1, 1)
        enabled: bool = formationAlertInput if kind == FORMED else returnAlertInput if kind == RETURN else retestAlertInput if kind == RETEST else outsideAlertInput
        if enabled:
            eventName: str = 'Formed' if kind == FORMED else 'Close above' if kind == ABOVE else 'Close below' if kind == BELOW else 'Boundary retouch' if kind == RETEST else 'Returned inside'
            message: str = layerName(ch.layer) + ' | ' + ch.key + ' | ' + eventName + ' | confirmed close of bar opened ' + string.format_time(bar.stamp, 'yyyy-MM-dd HH:mm:ss', syminfo.timezone) + ' ' + syminfo.timezone + ' | lower ' + string.tostring(lowerAt(ch, bar.index), format.mintick) + ' | upper ' + string.tostring(upperAt(ch, bar.index), format.mintick)
            array.push(messagesArray, message)
        return 0

    def advanceChannel(ch: Channel, bar: BarData, flagsArray: list[int], messagesArray: list[str]):
        if bar.index - ch.a.index > horizonInput:
            ch.state = AGED
            ch.endBar = bar.index
            if ch.retired < 0:
                ch.retired = bar.index
        elif ch.state == ACTIVE and bar.index > ch.available and bar.valid:
            side: int = 1 if bar.last > upperAt(ch, bar.index) + ch.allowance else -1 if bar.last < lowerAt(ch, bar.index) - ch.allowance else 0
            if side != 0:
                ch.state = WATCH
                ch.breakBar = bar.index
                ch.breakTime = bar.stamp
                ch.breakSide = side
                ch.retired = bar.index
                recordEvent(ABOVE if side == 1 else BELOW, ch, bar, flagsArray, messagesArray)
        elif ch.state == WATCH and bar.index > ch.breakBar:
            if bar.index <= ch.breakBar + watchInput and bar.valid and isInside(ch, bar, 0.0):
                ch.state = RETURNED
                ch.returnBar = bar.index
                ch.returnTime = bar.stamp
                ch.endBar = bar.index
                recordEvent(RETURN, ch, bar, flagsArray, messagesArray)
            else:
                if ch.retestBar < 0 and bar.valid:
                    reached: bool = bar.lo <= upperAt(ch, bar.index) if ch.breakSide == 1 else bar.hi >= lowerAt(ch, bar.index)
                    if reached:
                        ch.retestBar = bar.index
                        ch.retestTime = bar.stamp
                        recordEvent(RETEST, ch, bar, flagsArray, messagesArray)
                if bar.index >= ch.breakBar + watchInput:
                    ch.state = ENDED
                    ch.endBar = bar.index
        return 0

    def wasUsed(usedArray: list[AcceptedKey], key: str):
        found: bool = False
        if array.size(usedArray) > 0:
            for entry in usedArray:
                if entry.key == key:
                    found = True
                    break
        return found

    def activeChannel(recordsArray: list[Channel], layer: int):
        result: Channel = na(Channel)
        if array.size(recordsArray) > 0:
            for ch in recordsArray:
                if ch.layer == layer and ch.state == ACTIVE:
                    result = ch
                    break
        return result

    def betterCandidate(candidate: Channel, incumbent: Channel, bar: BarData):
        distance: float = math.abs(bar.last - (lowerAt(candidate, bar.index) + candidate.width * 0.5)) / candidate.width
        incumbentDistance: float = math.abs(bar.last - (lowerAt(incumbent, bar.index) + incumbent.width * 0.5)) / incumbent.width
        better: bool = candidate.c.index > incumbent.c.index
        if candidate.c.index == incumbent.c.index:
            better = distance < incumbentDistance
            if distance == incumbentDistance:
                span: int = candidate.c.index - candidate.a.index
                incumbentSpan: int = incumbent.c.index - incumbent.a.index
                better = span > incumbentSpan
                if span == incumbentSpan:
                    better = candidate.b.index < incumbent.b.index or (candidate.b.index == incumbent.b.index and candidate.direction > incumbent.direction)
        return better

    def ingestLayer(layerData: Layer, layer: int, strength: int, ringArray: list[BarData], bar: BarData, volatility: float, recordsArray: list[Channel], usedArray: list[AcceptedKey], flagsArray: list[int], messagesArray: list[str]):
        hi, lo = strictPivot(ringArray, bar.index, strength)
        if not na(hi):
            array.push(layerData.highsArray, hi)
        if not na(lo):
            array.push(layerData.lowsArray, lo)
        trimPivots(layerData.highsArray, bar.index)
        trimPivots(layerData.lowsArray, bar.index)
        for side in pine_range(0, 1):
            pivot: Pivot = hi if side == 0 else lo
            sameArray: list[Pivot] = layerData.highsArray if side == 0 else layerData.lowsArray
            oppositeArray: list[Pivot] = layerData.lowsArray if side == 0 else layerData.highsArray
            if not na(pivot) and array.size(sameArray) > 1:
                for index in pine_range(0, array.size(sameArray) - 2):
                    candidate: Channel = constructChannel(ringArray, array.get(sameArray, index), pivot, oppositeArray, -1 if side == 0 else 1, layer, strength, bar.index, volatility)
                    if not na(candidate):
                        array.push(layerData.pendingArray, candidate)
        while array.size(layerData.pendingArray) > PENDING_CAP:
            array.shift(layerData.pendingArray)
        if na(activeChannel(recordsArray, layer)) and bar.valid:
            bestIndex: int = -1
            best: Channel = na(Channel)
            if array.size(layerData.pendingArray) > 0:
                __loop_2__ = pine_loop(0)
                while __loop_2__.step(array.size(layerData.pendingArray) - 1):
                    index = __loop_2__.value
                    candidate: Channel = array.get(layerData.pendingArray, index)
                    if not wasUsed(usedArray, candidate.key) and isInside(candidate, bar, 0.0):
                        if na(best):
                            best = candidate
                            bestIndex = index
                        elif betterCandidate(candidate, best, bar):
                            best = candidate
                            bestIndex = index
            if bestIndex >= 0:
                array.remove(layerData.pendingArray, bestIndex)
                best.state = ACTIVE
                best.available = bar.index
                best.availableTime = bar.stamp
                array.push(recordsArray, best)
                array.push(usedArray, AcceptedKey(best.key, best.a.index))
                recordEvent(FORMED, best, bar, flagsArray, messagesArray)
        return 0

    def newerRetirement(left: Channel, right: Channel):
        return left.retired > right.retired or (left.retired == right.retired and (left.available > right.available or (left.available == right.available and left.layer > right.layer)))

    def trimTerminal(recordsArray: list[Channel]):
        count: int = 0
        if array.size(recordsArray) > 0:
            for ch in recordsArray:
                if ch.state == RETURNED or ch.state == ENDED:
                    count += 1
        while count > 10:
            oldestIndex: int = -1
            oldest: Channel = na(Channel)
            for index in pine_range(0, array.size(recordsArray) - 1):
                ch: Channel = array.get(recordsArray, index)
                if ch.state == RETURNED or ch.state == ENDED:
                    if na(oldest):
                        oldest = ch
                        oldestIndex = index
                    elif newerRetirement(oldest, ch):
                        oldest = ch
                        oldestIndex = index
            array.remove(recordsArray, oldestIndex)
            count -= 1
        return 0

    def watchCount(recordsArray: list[Channel], layer: int):
        count: int = 0
        if array.size(recordsArray) > 0:
            for ch in recordsArray:
                if ch.layer == layer and ch.state == WATCH:
                    count += 1
        return count

    def hasMember(membersArray: list[Channel], key: str):
        found: bool = False
        if array.size(membersArray) > 0:
            for ch in membersArray:
                if ch.key == key:
                    found = True
                    break
        return found

    def displayedChannels(recordsArray: list[Channel]):
        result: list[Channel] = array.new(0, NA(Channel))
        if array.size(recordsArray) > 0:
            for ch in recordsArray:
                if ch.state == ACTIVE:
                    array.push(result, ch)
            if retainedInput > 0:
                for slot in pine_range(1, retainedInput):
                    newest: Channel = na(Channel)
                    for ch in recordsArray:
                        if ch.state != ACTIVE and (not hasMember(result, ch.key)):
                            if na(newest):
                                newest = ch
                            elif newerRetirement(ch, newest):
                                newest = ch
                    if na(newest):
                        break
                    array.push(result, newest)
        return result

    def stateName(ch: Channel):
        return 'Active' if ch.state == ACTIVE else ('Watching above' if ch.breakSide == 1 else 'Watching below') if ch.state == WATCH else 'Returned inside' if ch.state == RETURNED else 'Watch ended'

    def addTransparency(selected: Color, extra: float):
        return color.new(selected, math.min(100.0, math.max(0.0, color.t(selected) + extra)))

    def risingColor():
        __block_result__ = na
        __switch__ = themeInput
        if __switch__ == THEME_CONTRAST:
            __block_result__ = HC_RISING
        elif __switch__ == THEME_PAPER:
            __block_result__ = PAP_RISING
        elif __switch__ == THEME_MUTED:
            __block_result__ = MUT_RISING
        elif __switch__ == THEME_CBSAFE:
            __block_result__ = CB_RISING
        elif __switch__ == THEME_MONO:
            __block_result__ = MON_RISING
        elif __switch__ == THEME_WARM:
            __block_result__ = WRM_RISING
        elif __switch__ == THEME_COOL:
            __block_result__ = COL_RISING
        elif __switch__ == THEME_CUSTOM:
            __block_result__ = risingInput
        else:
            __block_result__ = SIG_RISING
        return __block_result__

    def fallingColor():
        __block_result_1__ = na
        __switch__ = themeInput
        if __switch__ == THEME_CONTRAST:
            __block_result_1__ = HC_FALLING
        elif __switch__ == THEME_PAPER:
            __block_result_1__ = PAP_FALLING
        elif __switch__ == THEME_MUTED:
            __block_result_1__ = MUT_FALLING
        elif __switch__ == THEME_CBSAFE:
            __block_result_1__ = CB_FALLING
        elif __switch__ == THEME_MONO:
            __block_result_1__ = MON_FALLING
        elif __switch__ == THEME_WARM:
            __block_result_1__ = WRM_FALLING
        elif __switch__ == THEME_COOL:
            __block_result_1__ = COL_FALLING
        elif __switch__ == THEME_CUSTOM:
            __block_result_1__ = fallingInput
        else:
            __block_result_1__ = SIG_FALLING
        return __block_result_1__

    def historyColor():
        __block_result_2__ = na
        __switch__ = themeInput
        if __switch__ == THEME_CONTRAST:
            __block_result_2__ = HC_HISTORY
        elif __switch__ == THEME_PAPER:
            __block_result_2__ = PAP_HISTORY
        elif __switch__ == THEME_MUTED:
            __block_result_2__ = MUT_HISTORY
        elif __switch__ == THEME_CBSAFE:
            __block_result_2__ = CB_HISTORY
        elif __switch__ == THEME_MONO:
            __block_result_2__ = MON_HISTORY
        elif __switch__ == THEME_WARM:
            __block_result_2__ = WRM_HISTORY
        elif __switch__ == THEME_COOL:
            __block_result_2__ = COL_HISTORY
        elif __switch__ == THEME_CUSTOM:
            __block_result_2__ = historyInput
        else:
            __block_result_2__ = SIG_HISTORY
        return __block_result_2__

    def textSizeOf(name: str):
        __block_result_3__ = na
        __switch__ = name
        if __switch__ == SIZE_NORMAL:
            __block_result_3__ = size.normal
        elif __switch__ == SIZE_SMALL:
            __block_result_3__ = size.small
        else:
            __block_result_3__ = size.tiny
        return __block_result_3__

    def deleteDrawing(drawing: Drawing):
        if not na(drawing.fill__ren__):
            linefill.delete(drawing.fill__ren__)
            drawing.fill__ren__ = na
        for id in drawing.linesArray:
            if not na(id):
                line.delete(id)
        for id in drawing.labelsArray:
            if not na(id):
                label.delete(id)
        return 0

    def updateLine(drawing: Drawing, slot: int, left: int, leftPrice: float, right: int, rightPrice: float, tint: Color, style: str, width: int):
        id: Line = array.get(drawing.linesArray, slot)
        if na(id):
            id = line.new(left, leftPrice, right, rightPrice, xloc=xloc.bar_index, extend=extend.none, color=tint, style=style, width=width)
            array.set(drawing.linesArray, slot, id)
        else:
            line.set_xy1(id, left, leftPrice)
            line.set_xy2(id, right, rightPrice)
            line.set_color(id, tint)
            line.set_style(id, style)
            line.set_width(id, width)
        return 0

    def updateLabel(drawing: Drawing, slot: int, index: int, price: float, labelText: str, tint: Color, style: str):
        id: Label = array.get(drawing.labelsArray, slot)
        if na(id):
            id = label.new(index, price, labelText, xloc=xloc.bar_index, yloc=yloc.price, color=addTransparency(chart.bg_color, 15), style=style, textcolor=tint, size=textSizeOf(labelSizeInput))
            array.set(drawing.labelsArray, slot, id)
        else:
            label.set_xy(id, index, price)
            label.set_text(id, labelText)
            label.set_color(id, addTransparency(chart.bg_color, 15))
            label.set_textcolor(id, tint)
            label.set_size(id, textSizeOf(labelSizeInput))
        return 0

    def labelAnchor(ringArray: list[BarData], ch: Channel, index: int, side: int, clearance: float):
        edge: float = upperAt(ch, index) if side == 1 else lowerAt(ch, index)
        bar: BarData = getBar(ringArray, index)
        if not na(bar) and bar.valid:
            edge = math.max(edge, bar.hi) if side == 1 else math.min(edge, bar.lo)
        return edge + side * clearance

    def drawChannel(drawing: Drawing, ringArray: list[BarData], now: int):
        ch: Channel = drawing.channel
        live: bool = ch.state == ACTIVE
        running: bool = live or ch.state == WATCH
        right: int = now if running else ch.endBar
        tint: Color = (risingColor() if ch.direction == 1 else fallingColor()) if live else historyColor()
        if ch.layer == 1:
            tint = addTransparency(tint, 15)
        weight: int = boundaryInput if ch.layer == 0 else boundaryInput + 1 if boundaryInput < 4 else 4
        style: str = line.style_solid if ch.state == ACTIVE else line.style_dashed
        updateLine(drawing, 0, ch.a.index, lowerAt(ch, ch.a.index), right, lowerAt(ch, right), tint, style, weight)
        updateLine(drawing, 1, ch.a.index, upperAt(ch, ch.a.index), right, upperAt(ch, right), tint, style, weight)
        if midpointInput:
            updateLine(drawing, 2, ch.a.index, lowerAt(ch, ch.a.index) + ch.width * 0.5, right, lowerAt(ch, right) + ch.width * 0.5, addTransparency(tint, 20), line.style_dotted, 1)
        if quartersInput:
            updateLine(drawing, 3, ch.a.index, lowerAt(ch, ch.a.index) + ch.width * 0.25, right, lowerAt(ch, right) + ch.width * 0.25, addTransparency(tint, 35), line.style_dotted, 1)
            updateLine(drawing, 4, ch.a.index, lowerAt(ch, ch.a.index) + ch.width * 0.75, right, lowerAt(ch, right) + ch.width * 0.75, addTransparency(tint, 35), line.style_dotted, 1)
        updateLine(drawing, 5, ch.available, lowerAt(ch, ch.available), ch.available, upperAt(ch, ch.available), tint, line.style_dotted, 1)
        if live and fillInput:
            if na(drawing.fill__ren__):
                drawing.fill__ren__ = linefill.new(array.get(drawing.linesArray, 0), array.get(drawing.linesArray, 1), addTransparency(tint, transparencyInput))
            else:
                linefill.set_color(drawing.fill__ren__, addTransparency(tint, transparencyInput))
        elif not na(drawing.fill__ren__):
            linefill.delete(drawing.fill__ren__)
            drawing.fill__ren__ = na
        if labelsInput:
            clearance: float = ch.volatility * LABEL_CLEARANCE
            updateLabel(drawing, 0, ch.available, labelAnchor(ringArray, ch, ch.available, 1, clearance), 'Known', tint, label.style_label_down)
            direction: str = 'Rising' if ch.direction == 1 else 'Falling'
            endpoint: str = ('' if ch.layer == 0 else layerName(ch.layer) + ' · ') + direction + '\n' + stateName(ch)
            labelRight: bool = labelPosInput == LABEL_RIGHT
            labelBar: int = right + LABEL_LEAD_BARS if labelRight else right
            labelPrice: float = lowerAt(ch, labelBar) + ch.width * 0.5 + (0.0 if labelRight else clearance)
            updateLabel(drawing, 1, labelBar, labelPrice, endpoint, tint, label.style_label_center if labelRight else label.style_label_left)
            if anchorsInput:
                updateLabel(drawing, 2, ch.a.index, ch.a.price, 'A', tint, label.style_label_up)
                updateLabel(drawing, 3, ch.b.index, ch.b.price, 'B', tint, label.style_label_down)
                updateLabel(drawing, 4, ch.c.index, ch.c.price, 'C', tint, label.style_label_up)
            if ch.breakBar >= 0:
                eventName: str = 'Close above' if ch.breakSide == 1 else 'Close below'
                eventPrice: float = labelAnchor(ringArray, ch, ch.breakBar, ch.breakSide, clearance)
                updateLabel(drawing, 5, ch.breakBar, eventPrice, eventName, tint, label.style_label_down if ch.breakSide == 1 else label.style_label_up)
            if ch.retestBar >= 0:
                retestPrice: float = labelAnchor(ringArray, ch, ch.retestBar, ch.breakSide, clearance)
                updateLabel(drawing, 7, ch.retestBar, retestPrice, 'Boundary retouch', tint, label.style_label_down if ch.breakSide == 1 else label.style_label_up)
            if ch.returnBar >= 0:
                returnPrice: float = labelAnchor(ringArray, ch, ch.returnBar, ch.breakSide, clearance)
                updateLabel(drawing, 6, ch.returnBar, returnPrice, 'Returned inside', tint, label.style_label_down if ch.breakSide == 1 else label.style_label_up)
        return 0

    def renderChannels(drawingsArray: list[Drawing], membersArray: list[Channel], ringArray: list[BarData], now: int):
        index: int = array.size(drawingsArray) - 1
        while index >= 0:
            drawing: Drawing = array.get(drawingsArray, index)
            if not hasMember(membersArray, drawing.channel.key):
                deleteDrawing(drawing)
                array.remove(drawingsArray, index)
            index -= 1
        if array.size(membersArray) > 0:
            for ch in membersArray:
                selected: Drawing = na(Drawing)
                if array.size(drawingsArray) > 0:
                    for drawing in drawingsArray:
                        if drawing.channel.key == ch.key:
                            selected = drawing
                            break
                if na(selected):
                    selected = Drawing(ch, array.new_line(6), array.new_label(8), na)
                    array.push(drawingsArray, selected)
                drawChannel(selected, ringArray, now)
        return 0

    def formingPick(layerData: Layer, usedArray: list[AcceptedKey], recordsArray: list[Channel], layer: int, bar: BarData):
        best: Channel = na(Channel)
        if na(activeChannel(recordsArray, layer)) and (not na(bar)) and bar.valid and (array.size(layerData.pendingArray) > 0):
            for candidate in layerData.pendingArray:
                if not wasUsed(usedArray, candidate.key):
                    if na(best) or betterCandidate(candidate, best, bar):
                        best = candidate
        return best

    def renderForming(formingLinesArray: list[Line], formingLabelsArray: list[Label], layer: int, ch: Channel, now: int, tint: Color):
        upperSlot: int = layer * 2
        lowerSlot: int = upperSlot + 1
        upperLine: Line = array.get(formingLinesArray, upperSlot)
        lowerLine: Line = array.get(formingLinesArray, lowerSlot)
        mark: Label = array.get(formingLabelsArray, layer)
        if na(ch):
            if not na(upperLine):
                line.delete(upperLine)
                array.set(formingLinesArray, upperSlot, na)
            if not na(lowerLine):
                line.delete(lowerLine)
                array.set(formingLinesArray, lowerSlot, na)
            if not na(mark):
                label.delete(mark)
                array.set(formingLabelsArray, layer, na)
        else:
            left: int = ch.a.index
            upperLeft: float = upperAt(ch, left)
            upperRight: float = upperAt(ch, now)
            lowerLeft: float = lowerAt(ch, left)
            lowerRight: float = lowerAt(ch, now)
            if na(upperLine):
                array.set(formingLinesArray, upperSlot, line.new(left, upperLeft, now, upperRight, xloc=xloc.bar_index, style=line.style_dotted, color=tint, width=1))
            else:
                line.set_xy1(upperLine, left, upperLeft)
                line.set_xy2(upperLine, now, upperRight)
                line.set_color(upperLine, tint)
                line.set_style(upperLine, line.style_dotted)
                line.set_width(upperLine, 1)
            if na(lowerLine):
                array.set(formingLinesArray, lowerSlot, line.new(left, lowerLeft, now, lowerRight, xloc=xloc.bar_index, style=line.style_dotted, color=tint, width=1))
            else:
                line.set_xy1(lowerLine, left, lowerLeft)
                line.set_xy2(lowerLine, now, lowerRight)
                line.set_color(lowerLine, tint)
                line.set_style(lowerLine, line.style_dotted)
                line.set_width(lowerLine, 1)
            markPrice: float = math.max(upperRight, high) + ch.volatility * LABEL_CLEARANCE
            if not labelsInput:
                if not na(mark):
                    label.delete(mark)
                    array.set(formingLabelsArray, layer, na)
            elif na(mark):
                array.set(formingLabelsArray, layer, label.new(now, markPrice, 'Forming · not accepted', xloc=xloc.bar_index, style=label.style_label_down, color=addTransparency(chart.bg_color, 25), textcolor=tint, size=textSizeOf(labelSizeInput)))
            else:
                label.set_xy(mark, now, markPrice)
                label.set_textcolor(mark, tint)
                label.set_color(mark, addTransparency(chart.bg_color, 25))
                label.set_size(mark, textSizeOf(labelSizeInput))
        return 0

    def layerState(active: Channel, idle: str):
        return idle if na(active) else 'Rising · Active' if active.direction == 1 else 'Falling · Active'

    def panelRow(target: Table, row: int, name: str, value: str, tone: Color, back: Color):
        table.cell(target, 0, row, name, text_color=tone, bgcolor=back, text_size=size.small, text_halign=text.align_left)
        return table.cell(target, 1, row, value, text_color=tone, bgcolor=back, text_size=size.small, text_halign=text.align_right)

    def panelBanner(target: Table, row: int, body: str, tone: Color, back: Color):
        return table.cell(target, 0, row, body, text_color=tone, bgcolor=back, text_size=size.small, text_halign=text.align_left)

    ringArray: Persistent[list[BarData]] = array.new(RING_SIZE, NA(BarData))
    trueRangesArray: Persistent[list[float]] = array.new_float()
    previous: Persistent[BarData] = na(BarData)
    layersArray: Persistent[list[Layer]] = array.new(0, NA(Layer))
    recordsArray: Persistent[list[Channel]] = array.new(0, NA(Channel))
    usedArray: Persistent[list[AcceptedKey]] = array.new(0, NA(AcceptedKey))
    drawingsArray: Persistent[list[Drawing]] = array.new(0, NA(Drawing))
    volatility: Persistent[float] = na(float)
    panelTable: Persistent[Table] = table.new(position.top_right if positionInput == 'Top right' else position.top_left if positionInput == 'Top left' else position.bottom_right if positionInput == 'Bottom right' else position.bottom_left, 2, PANEL_ROWS)
    formingLinesArray: Persistent[list[Line]] = array.new_line(4)
    formingLabelsArray: Persistent[list[Label]] = array.new_label(2)

    if array.size(layersArray) == 0:
        array.push(layersArray, Layer(array.new(0, NA(Pivot)), array.new(0, NA(Pivot)), array.new(0, NA(Channel))))
        array.push(layersArray, Layer(array.new(0, NA(Pivot)), array.new(0, NA(Pivot)), array.new(0, NA(Channel))))

    flagsArray: list[int] = array.new_int(10, 0)
    messagesArray: list[str] = array.new_string()
    supported: bool = chart.is_standard and (not timeframe.isticks)
    configurationValid: bool = minWidthInput <= maxWidthInput
    longerEnabled: bool = longerInput and horizonInput >= 3 * swingInput * multipleInput
    pricesValid: bool = not na(high) and (not na(low)) and (not na(close)) and (low <= close) and (close <= high)

    if barstate.isconfirmed:
        bar: BarData = BarData(bar_index, time, high, low, close, pricesValid)
        array.set(ringArray, bar_index % RING_SIZE, bar)
        tr: float = na(float)
        if bar.valid:
            if na(previous):
                tr = bar.hi - bar.lo
            elif previous.valid:
                tr = math.max(bar.hi - bar.lo, math.abs(bar.hi - previous.last), math.abs(bar.lo - previous.last))
        previous = bar
        array.push(trueRangesArray, tr)
        if array.size(trueRangesArray) > volatilityInput:
            array.shift(trueRangesArray)
        total: float = 0.0
        for value in trueRangesArray:
            total += value
        volatility = total / volatilityInput if array.size(trueRangesArray) == volatilityInput else na
        if supported and configurationValid:
            keyIndex: int = array.size(usedArray) - 1
            while keyIndex >= 0:
                entry: AcceptedKey = array.get(usedArray, keyIndex)
                if bar_index - entry.anchor > horizonInput:
                    array.remove(usedArray, keyIndex)
                keyIndex -= 1
            for layerData in layersArray:
                updatePending(layerData.pendingArray, bar)
            if array.size(recordsArray) > 0:
                for ch in recordsArray:
                    advanceChannel(ch, bar, flagsArray, messagesArray)
            recordIndex: int = array.size(recordsArray) - 1
            while recordIndex >= 0:
                ch: Channel = array.get(recordsArray, recordIndex)
                if ch.state == AGED:
                    array.remove(recordsArray, recordIndex)
                recordIndex -= 1
            ingestLayer(array.get(layersArray, 0), 0, swingInput, ringArray, bar, volatility, recordsArray, usedArray, flagsArray, messagesArray)
            if longerEnabled:
                ingestLayer(array.get(layersArray, 1), 1, swingInput * multipleInput, ringArray, bar, volatility, recordsArray, usedArray, flagsArray, messagesArray)
            trimTerminal(recordsArray)

    swingChannel: Channel = activeChannel(recordsArray, 0)
    longer: Channel = activeChannel(recordsArray, 1)
    swingWatches: int = watchCount(recordsArray, 0)
    longerWatches: int = watchCount(recordsArray, 1)

    if barstate.islast:
        membersArray: list[Channel] = displayedChannels(recordsArray)
        renderChannels(drawingsArray, membersArray, ringArray, bar_index)
        formingTint: Color = addTransparency(historyColor(), 40)
        formingSwing: Channel = formingPick(array.get(layersArray, 0), usedArray, recordsArray, 0, previous) if formingInput and supported and configurationValid else na
        formingLonger: Channel = formingPick(array.get(layersArray, 1), usedArray, recordsArray, 1, previous) if formingInput and longerEnabled and supported and configurationValid else na
        renderForming(formingLinesArray, formingLabelsArray, 0, formingSwing, bar_index, formingTint)
        renderForming(formingLinesArray, formingLabelsArray, 1, formingLonger, bar_index, formingTint)
        blocking: str = 'Unsupported chart: standard time-based charts only.' if not supported else 'Invalid settings: minimum width exceeds maximum width.' if not configurationValid else ''
        notice: str = "Linear-price geometry · confirmed-pivot delay\nAnchor history, not a forecast"
        if blocking != '':
            notice += '\n' + blocking
        else:
            if longerInput and (not longerEnabled):
                notice += "\nLonger swing disabled: horizon must be at least 3 × its swing length."
            if not pricesValid:
                notice += "\nMissing price data: no price events or new construction."
            elif na(volatility) or volatility <= 0:
                notice += "\nVolatility unavailable: no new construction."
            if na(swingChannel) and na(longer):
                swingLayer: Layer = array.get(layersArray, 0)
                fewPivots: bool = array.size(swingLayer.highsArray) < 2 and array.size(swingLayer.lowsArray) < 2
                notice += '\nInsufficient confirmed pivots.' if fewPivots else '\nNo active valid channel.'
        drawnCeiling: int = retainedInput + 1 + (1 if longerEnabled else 0)
        drawnText: str = string.tostring(array.size(membersArray)) + ' of ' + string.tostring(drawnCeiling) + ' sets'

        panelTone: Color = chart.fg_color
        panelDim: Color = addTransparency(chart.fg_color, 35)
        panelBack: Color = chart.bg_color
        panelBanded: Color = addTransparency(chart.fg_color, 92)
        panelDetail: bool = tableInput and panelInput == PANEL_FULL
        panelShown: bool = tableInput and panelInput != PANEL_OFF
        noticeShown: bool = tableInput or blocking != ''

        if panelShown:
            panelBanner(panelTable, 0, 'AUTO TREND CHANNELS', panelTone, panelBanded)
            if panelDetail:
                panelRow(panelTable, 1, 'Swing', layerState(swingChannel, 'No active channel'), panelTone, panelBack)
                panelRow(panelTable, 2, 'Upper', '' if na(swingChannel) else string.tostring(upperAt(swingChannel, bar_index), format.mintick), panelTone, panelBack)
                panelRow(panelTable, 3, 'Mid', '' if na(swingChannel) else string.tostring(lowerAt(swingChannel, bar_index) + swingChannel.width * 0.5, format.mintick), panelTone, panelBack)
                panelRow(panelTable, 4, 'Lower', '' if na(swingChannel) else string.tostring(lowerAt(swingChannel, bar_index), format.mintick), panelTone, panelBack)
                panelRow(panelTable, 5, 'Watches', string.tostring(swingWatches), panelDim, panelBack)
                panelRow(panelTable, 6, 'Longer swing', layerState(longer, 'No active channel' if longerEnabled else 'Off · Longer swing channel'), panelTone, panelBanded)
                panelRow(panelTable, 7, 'Upper', '' if na(longer) else string.tostring(upperAt(longer, bar_index), format.mintick), panelTone, panelBack)
                panelRow(panelTable, 8, 'Mid', '' if na(longer) else string.tostring(lowerAt(longer, bar_index) + longer.width * 0.5, format.mintick), panelTone, panelBack)
                panelRow(panelTable, 9, 'Lower', '' if na(longer) else string.tostring(lowerAt(longer, bar_index), format.mintick), panelTone, panelBack)
                panelRow(panelTable, 10, 'Watches', string.tostring(longerWatches), panelDim, panelBack)
                panelRow(panelTable, 11, 'Drawn', drawnText, panelTone, panelBanded)
            else:
                table.clear(panelTable, 0, 1, 1, 11)
        else:
            table.clear(panelTable, 0, 0, 1, 11)
        if noticeShown:
            panelBanner(panelTable, 12, notice if tableInput else blocking, panelDim, panelBack)
        else:
            table.clear(panelTable, 0, 12, 1, 12)

    plot(upperAt(swingChannel, bar_index) if not na(swingChannel) else na, 'Swing upper', color=color.new('#26A69A'), display=display.data_window)
    plot(lowerAt(swingChannel, bar_index) + swingChannel.width * 0.5 if not na(swingChannel) else na, 'Swing midpoint', color=color.new('#26A69A'), display=display.data_window)
    plot(lowerAt(swingChannel, bar_index) if not na(swingChannel) else na, 'Swing lower', color=color.new('#26A69A'), display=display.data_window)
    plot(swingChannel.available if not na(swingChannel) else na, 'Swing available bar', color=color.new('#26A69A'), display=display.data_window)
    plot(array.get(flagsArray, 0), 'Swing formed', color=color.new('#26A69A'), display=display.data_window)
    plot(array.get(flagsArray, 1), 'Swing close above', color=color.new('#26A69A'), display=display.data_window)
    plot(array.get(flagsArray, 2), 'Swing close below', color=color.new('#26A69A'), display=display.data_window)
    plot(array.get(flagsArray, 3), 'Swing returned inside', color=color.new('#26A69A'), display=display.data_window)
    plot(array.get(flagsArray, 4), 'Swing boundary retouch', color=color.new('#26A69A'), display=display.data_window)
    plot(swingWatches, 'Swing return watches', color=color.new('#26A69A'), display=display.data_window)
    plot(upperAt(longer, bar_index) if not na(longer) else na, 'Longer swing upper', color=color.new('#EF5350'), display=display.data_window)
    plot(lowerAt(longer, bar_index) + longer.width * 0.5 if not na(longer) else na, 'Longer swing midpoint', color=color.new('#EF5350'), display=display.data_window)
    plot(lowerAt(longer, bar_index) if not na(longer) else na, 'Longer swing lower', color=color.new('#EF5350'), display=display.data_window)
    plot(longer.available if not na(longer) else na, 'Longer swing available bar', color=color.new('#EF5350'), display=display.data_window)
    plot(array.get(flagsArray, 5), 'Longer swing formed', color=color.new('#EF5350'), display=display.data_window)
    plot(array.get(flagsArray, 6), 'Longer swing close above', color=color.new('#EF5350'), display=display.data_window)
    plot(array.get(flagsArray, 7), 'Longer swing close below', color=color.new('#EF5350'), display=display.data_window)
    plot(array.get(flagsArray, 8), 'Longer swing returned inside', color=color.new('#EF5350'), display=display.data_window)
    plot(array.get(flagsArray, 9), 'Longer swing boundary retouch', color=color.new('#EF5350'), display=display.data_window)
    plot(longerWatches, 'Longer swing return watches', color=color.new('#EF5350'), display=display.data_window)

    alertcondition(array.get(flagsArray, 0) == 1 and formationAlertInput, 'Swing formed', 'Auto Trend Channels [AFD]: swing channel formed.')
    alertcondition(array.get(flagsArray, 1) == 1 and outsideAlertInput, 'Swing close above', 'Auto Trend Channels [AFD]: swing channel closed above its upper boundary.')
    alertcondition(array.get(flagsArray, 2) == 1 and outsideAlertInput, 'Swing close below', 'Auto Trend Channels [AFD]: swing channel closed below its lower boundary.')
    alertcondition(array.get(flagsArray, 3) == 1 and returnAlertInput, 'Swing returned inside', 'Auto Trend Channels [AFD]: swing channel returned inside.')
    alertcondition(array.get(flagsArray, 4) == 1 and retestAlertInput, 'Swing boundary retouch', 'Auto Trend Channels [AFD]: a bar reached the broken boundary of a swing channel.')
    alertcondition(array.get(flagsArray, 5) == 1 and formationAlertInput, 'Longer swing formed', 'Auto Trend Channels [AFD]: longer swing channel formed.')
    alertcondition(array.get(flagsArray, 6) == 1 and outsideAlertInput, 'Longer swing close above', 'Auto Trend Channels [AFD]: longer swing channel closed above its upper boundary.')
    alertcondition(array.get(flagsArray, 7) == 1 and outsideAlertInput, 'Longer swing close below', 'Auto Trend Channels [AFD]: longer swing channel closed below its lower boundary.')
    alertcondition(array.get(flagsArray, 8) == 1 and returnAlertInput, 'Longer swing returned inside', 'Auto Trend Channels [AFD]: longer swing channel returned inside.')
    alertcondition(array.get(flagsArray, 9) == 1 and retestAlertInput, 'Longer swing boundary retouch', 'Auto Trend Channels [AFD]: a bar reached the broken boundary of a longer swing channel.')

    if barstate.isconfirmed and array.size(messagesArray) > 0:
        batch: str = 'Auto Trend Channels [AFD] | ' + syminfo.tickerid
        for message in messagesArray:
            batch += '\n' + message
        alert(batch, alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
