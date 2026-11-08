"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_udt import udt
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, box, close, color, display,
    format, high, input, label, line, low, math, na, plot, position, script, size, string, syminfo,
    ta, table
)
from pynecore.types import Box, Color, Label, Line, NA, Persistent, Table


@udt
class Map:
    born: int = na(int)
    dir: int = na(int)
    origin: float = na(float)
    tip: float = na(float)
    atrSize: float = na(float)
    retained: float = na(float)
    worst: float = na(float)
    age: int = na(int)
    halfSeen: bool = na(bool)
    active: bool = na(bool)
    status: str = na(str)
    strong: Box = na(Box)
    weak: Box = na(Box)
    mid: Line = na(Line)
    tag: Label = na(Label)


G1: str = "Detection"
G2: str = "Display"


@script.indicator("Impulse Retention Map [MQLSoftware]", shorttitle="MQLSoftware - Impulse Retention Map", overlay=True, behind_chart=False, max_bars_back=500, max_boxes_count=60, max_lines_count=60, max_labels_count=120)
def main(
    span=input.int(3, "Impulse window (bars)", minval=1, maxval=12, group=G1),
    minMove=input.float(2.0, "Minimum move / pre-impulse ATR", minval=0.5, maxval=8, step=0.1, group=G1),
    minEff=input.float(0.75, "Minimum path efficiency", minval=0.3, maxval=1.0, step=0.05, group=G1, tooltip="Absolute net close-to-close move divided by the sum of absolute close changes. 1 means no closing-price retracement inside the window."),
    atrLen=input.int(20, "ATR baseline", minval=5, maxval=100, group=G1),
    life=input.int(60, "Track for at most (bars)", minval=5, maxval=250, group=G1),
    keep=input.int(6, "Maps to keep", minval=1, maxval=20, group=G2),
    marks=input.bool(True, "Outcome labels", group=G2),
    panelOn=input.bool(True, "Status panel", group=G2),
    panelPlace=input.string("Bottom left", "Panel position", options=("Bottom left", "Top right", "Bottom right"), group=G2),
    rails=input.bool(True, "Latest map price labels", group=G2),
    upCol=input.color(color.new('#26C6AD'), "Up impulse", group=G2, inline="c"),
    dnCol=input.color(color.new('#EA7884'), "Down impulse", group=G2, inline="c"),
    halfCol=input.color(color.new('#D8AE63'), "Half returned", group=G2, inline="c")
):
    textCol: Color = color.new('#DDE3EC')
    muted: Color = color.new('#8794A8')
    bg: Color = color.new('#101722')

    maps: Persistent[list[Map]] = array.new(0, NA(Map))
    events: Persistent[list[Label]] = array.new_label()
    lastBorn: Persistent[int] = na(int)
    priorCandidate: Persistent[int] = 0
    baseAtr: float = inline_series(ta.atr(atrLen), span)
    delta: float = close - close[span]
    path: float = math.sum(math.abs(ta.change(close)), span)
    winHigh: float = ta.highest(high, span)
    winLow: float = ta.lowest(low, span)
    winRange: float = winHigh - winLow
    valid: bool = not na(close) and (not na(high)) and (not na(low)) and (not na(close[span])) and (not na(path))
    ready: bool = valid and (not na(baseAtr)) and (baseAtr > 0) and (winRange > 0)
    eff: float = math.abs(delta) / path if ready and path > 0 else 0.0
    direction: int = 1 if delta > 0 else -1 if delta < 0 else 0
    location__ren__: float = (close - winLow if direction > 0 else winHigh - close) / winRange if ready else 0.0
    qualified: bool = ready and math.abs(delta) >= math.max(minMove * baseAtr, syminfo.mintick * 2) and (eff >= minEff) and (location__ren__ >= 0.7)
    candidate: int = direction if qualified else 0

    newUp: bool = False
    newDn: bool = False
    halfEvent: bool = False
    unwindEvent: bool = False
    recoverEvent: bool = False
    expireEvent: bool = False
    replaceEvent: bool = False

    def eventMark(y: float, msg: str, col: Color, above: bool):
        __block_result__ = na
        if marks:
            e: Label = label.new(bar_index, y, msg, style=label.style_label_down if above else label.style_label_up, color=color.new(bg, 8), textcolor=col, size=size.small)
            array.push(events, e)
            __block_result_1__ = na
            if array.size(events) > 60:
                __block_result_1__ = label.delete(array.shift(events))
            __block_result__ = __block_result_1__
        return __block_result__

    def retire(m: Map):
        box.set_bgcolor(m.strong, color.new(upCol if m.dir > 0 else dnCol, 94))
        box.set_bgcolor(m.weak, color.new(halfCol, 96))
        box.set_border_color(m.strong, color.new(upCol if m.dir > 0 else dnCol, 75))
        box.set_border_color(m.weak, color.new(halfCol, 82))
        line.set_color(m.mid, color.new(halfCol, 72))
        return label.set_tooltip(m.tag, m.status + ' | Final retained: ' + string.tostring(m.retained * 100, '#.0') + '% of original move | Worst close: ' + string.tostring(m.worst * 100, '#.0') + '% | Bars: ' + string.tostring(m.age))

    if barstate.isconfirmed:
        if array.size(maps) > 0:
            m: Map = array.last(maps)
            if m.active:
                m.age = bar_index - m.born
                box.set_right(m.strong, bar_index)
                box.set_right(m.weak, bar_index)
                line.set_x2(m.mid, bar_index)
                if valid:
                    m.retained = (close - m.origin) / (m.tip - m.origin)
                    m.worst = math.min(m.worst, m.retained)
                    if m.retained <= 0:
                        m.status = "UNWOUND"
                        m.active = False
                        unwindEvent = True
                        eventMark(close, 'UNWOUND', dnCol, m.dir > 0)
                    elif m.halfSeen and m.retained >= 1:
                        m.status = "RECOVERED"
                        m.active = False
                        recoverEvent = True
                        eventMark(close, 'RECOVERED', upCol, m.dir < 0)
                    elif not m.halfSeen and m.retained <= 0.5:
                        m.halfSeen = True
                        halfEvent = True
                        eventMark(close, 'HALF BACK', halfCol, m.dir > 0)
                    if m.active:
                        m.status = 'DEEP RETRACE' if m.retained <= 0.5 else 'REBUILDING' if m.halfSeen else 'EXTENDED' if m.retained >= 1 else 'HOLDING'
                if m.active and m.age >= life:
                    m.status = "EXPIRED"
                    m.active = False
                    expireEvent = True
                if not m.active:
                    retire(m)

        fresh: bool = candidate != 0 and candidate != priorCandidate
        spaced: bool = na(lastBorn) or bar_index - lastBorn >= span
        if fresh and spaced:
            if array.size(maps) > 0:
                old: Map = array.last(maps)
                if old.active:
                    old.active = False
                    old.status = "REPLACED"
                    replaceEvent = True
                    retire(old)
            origin: float = close[span]
            tip: float = close
            middle: float = (origin + tip) * 0.5
            col: Color = upCol if direction > 0 else dnCol
            strong: Box = box.new(bar_index, math.max(tip, middle), bar_index, math.min(tip, middle), border_color=color.new(col, 35), bgcolor=color.new(col, 86))
            weak: Box = box.new(bar_index, math.max(origin, middle), bar_index, math.min(origin, middle), border_color=color.new(halfCol, 55), bgcolor=color.new(halfCol, 94))
            mid: Line = line.new(bar_index, middle, bar_index, middle, color=color.new(halfCol, 20), style=line.style_dashed)
            tag: Label = label.new(bar_index, tip, ('UP ' if direction > 0 else 'DOWN ') + string.tostring(math.abs(delta) / baseAtr, '#.0') + ' ATR', style=label.style_label_down if direction > 0 else label.style_label_up, color=color.new(col, 12), textcolor=bg, size=size.small)
            m: Map = Map(bar_index, direction, origin, tip, math.abs(delta) / baseAtr, 1.0, 1.0, 0, False, True, 'NEW IMPULSE', strong, weak, mid, tag)
            array.push(maps, m)
            if array.size(maps) > keep:
                first: Map = array.shift(maps)
                box.delete(first.strong)
                box.delete(first.weak)
                line.delete(first.mid)
                label.delete(first.tag)
                oldest: int = array.first(maps).born
                while array.size(events) > 0:
                    if label.get_x(array.first(events)) < oldest:
                        label.delete(array.shift(events))
                    else:
                        break
            lastBorn = bar_index
            newUp = direction > 0
            newDn = direction < 0
        priorCandidate = candidate

    tipLabel: Persistent[Label] = label.new(na, na, '', style=label.style_label_right, color=color.new(bg, 10), size=size.small)
    midLabel: Persistent[Label] = label.new(na, na, '', style=label.style_label_right, color=color.new(bg, 10), size=size.small)
    originLabel: Persistent[Label] = label.new(na, na, '', style=label.style_label_right, color=color.new(bg, 10), size=size.small)
    hud: Persistent[Table] = table.new(position.top_right if panelPlace == 'Top right' else position.bottom_right if panelPlace == 'Bottom right' else position.bottom_left, 2, 7, bgcolor=bg, border_color=color.new('#253143'), border_width=1)

    if barstate.islast:
        if panelOn:
            table.cell(hud, 0, 0, 'IMPULSE RETENTION', text_color=textCol, text_size=size.small)
            table.cell(hud, 1, 0, 'CLOSED BARS', text_color=muted, text_size=size.tiny)
        if array.size(maps) > 0:
            m: Map = array.last(maps)
            col: Color = upCol if m.dir > 0 else dnCol
            if panelOn:
                table.cell(hud, 0, 1, 'UP IMPULSE' if m.dir > 0 else 'DOWN IMPULSE', text_color=col, text_size=size.small)
                table.cell(hud, 1, 1, m.status, text_color=(halfCol if m.retained <= 0.5 else col) if m.active else muted, text_size=size.small)
                table.cell(hud, 0, 2, 'Move retained', text_color=textCol, text_size=size.small)
                table.cell(hud, 1, 2, string.tostring(m.retained * 100, '#.0') + '%', text_color=halfCol if m.retained <= 0.5 else col, text_size=size.large)
                table.cell(hud, 0, 3, 'Worst close', text_color=muted, text_size=size.small)
                table.cell(hud, 1, 3, string.tostring(m.worst * 100, '#.0') + '% retained', text_color=muted, text_size=size.small)
                table.cell(hud, 0, 4, 'Original ' + string.tostring(span) + '-bar move', text_color=muted, text_size=size.small)
                table.cell(hud, 1, 4, string.tostring(math.abs(m.tip - m.origin), format.mintick) + ' / ' + string.tostring(m.atrSize, '#.0') + ' ATR', text_color=textCol, text_size=size.small)
                table.cell(hud, 0, 5, 'Bars tracked', text_color=muted, text_size=size.small)
                table.cell(hud, 1, 5, string.tostring(m.age) + ' / ' + string.tostring(life), text_color=textCol, text_size=size.small)
                table.cell(hud, 0, 6, '100% = original move', text_color=muted, text_size=size.tiny)
                table.cell(hud, 1, 6, '0% = fully returned' if m.active else 'FINAL SNAPSHOT', text_color=muted, text_size=size.tiny)
            if rails and m.active:
                label.set_xy(tipLabel, bar_index + 3, m.tip)
                label.set_text(tipLabel, '100%  Impulse close')
                label.set_tooltip(tipLabel, string.tostring(m.tip, format.mintick))
                label.set_textcolor(tipLabel, col)
                label.set_xy(midLabel, bar_index + 3, (m.tip + m.origin) * 0.5)
                label.set_text(midLabel, '50%  Half back')
                label.set_tooltip(midLabel, string.tostring((m.tip + m.origin) * 0.5, format.mintick))
                label.set_textcolor(midLabel, halfCol)
                label.set_xy(originLabel, bar_index + 3, m.origin)
                label.set_text(originLabel, '0%  Origin')
                label.set_tooltip(originLabel, string.tostring(m.origin, format.mintick))
                label.set_textcolor(originLabel, muted)
            else:
                label.set_xy(tipLabel, na, na)
                label.set_xy(midLabel, na, na)
                label.set_xy(originLabel, na, na)
        elif panelOn:
            emptyState: str = 'WARMING UP' if na(baseAtr) else 'MISSING PRICE DATA' if not valid else 'NO PRICE RANGE' if not ready else 'WAITING FOR IMPULSE'
            table.cell(hud, 0, 1, emptyState, text_color=halfCol, text_size=size.small)
            table.cell(hud, 1, 1, string.tostring(atrLen + span) + ' bars needed' if na(baseAtr) else '>= ' + string.tostring(minMove, '#.0') + ' ATR', text_color=muted, text_size=size.small)
            table.cell(hud, 0, 6, 'No qualifying move yet', text_color=muted, text_size=size.tiny)
            table.cell(hud, 1, 6, 'Chart timeframe', text_color=muted, text_size=size.tiny)

    latest: Map = array.last(maps) if array.size(maps) > 0 else na
    plot(latest.origin if not na(latest) else na, 'Map origin', display=display.data_window)
    plot(latest.tip if not na(latest) else na, 'Map impulse close', display=display.data_window)
    plot(latest.retained * 100 if not na(latest) else na, 'Move retained (%)', display=display.data_window)
    plot(1 if newUp else -1 if newDn else 0, 'New impulse direction', display=display.data_window)
    plot(1 if halfEvent else 0, 'Half back event', display=display.data_window)
    plot(1 if unwindEvent else 0, 'Unwound event', display=display.data_window)
    plot(1 if recoverEvent else 0, 'Recovered event', display=display.data_window)
    plot(1 if expireEvent else 0, 'Expired event', display=display.data_window)
    plot(1 if replaceEvent else 0, 'Replaced event', display=display.data_window)
    alertcondition(newUp, 'New up impulse', 'New confirmed up impulse on {{ticker}} {{interval}}.')
    alertcondition(newDn, 'New down impulse', 'New confirmed down impulse on {{ticker}} {{interval}}.')
    alertcondition(halfEvent, 'Half of impulse returned', 'Confirmed close returned at least half of the mapped impulse on {{ticker}} {{interval}}.')
    alertcondition(unwindEvent, 'Impulse fully unwound', 'Confirmed close reached or crossed the impulse origin on {{ticker}} {{interval}}.')
    alertcondition(recoverEvent, 'Impulse recovered', 'After returning at least half, a confirmed close recovered the original impulse on {{ticker}} {{interval}}.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
