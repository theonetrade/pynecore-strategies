"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, close, color, display, fixnan, high, input, label,
    line, location, low, math, na, open, plotcandle, plotchar, script, size, ta
)
from pynecore.types import Color, Line, NA, Persistent, Series


@udt
class breaker:
    level: Line = na(Line)
    breaks: int = 0


@script.indicator('Market Structure (Breakers) [LuxAlgo]', overlay=True, max_lines_count=500, max_labels_count=500)
def main(
    length=input.int(20, 'Swings Period', minval=2),
    breaks=input.int(1, 'Maximum Breaks', minval=1),
    maxDuration=input(1000, 'Breaker Maximum Duration'),
    bullCss=input(color.new('#089981'), 'Bullish MS', inline='bull', group='Style'),
    bullBreakCss=input(color.new('#F23645'), 'Breaker', inline='bull', group='Style'),
    bearCss=input(color.new('#F23645'), 'Bearish MS', inline='bear', group='Style'),
    bearBreakCss=input(color.new('#089981'), 'Breaker', inline='bear', group='Style')
):
    phx: Persistent[int] = 0
    phcross: Persistent[bool] = False
    bullms: Persistent[list[breaker]] = array.new(0, NA(breaker))
    os: Persistent[int] = 0
    n = bar_index
    ph: Series = fixnan(ta.pivothigh(length, length))
    if ph != ph[1]:
        phx = n - length
        phcross = False
    if close > ph and (not phcross):
        line.new(phx, ph, n, ph, color=bullCss)
        label.new(cast_int(math.avg(phx, n)), ph, 'MSS' if os == -1 else 'MSB', textcolor=bullCss, color=NA(Color), size=size.small, style=label.style_label_down)
        array.unshift(bullms, breaker(line.new(n, ph, n, ph, color=bullBreakCss, style=line.style_dotted)))
        phcross = True
        if array.size(bullms) > 100:
            array.pop(bullms)
        os = 1
    break_down: bool = False
    if array.size(bullms) > 0:
        for i in pine_range(array.size(bullms) - 1, 0, 1):
            get = array.get(bullms, i)
            method_call('set_x2', get.level, n)
            if close < method_call('get_y2', get.level) and open > method_call('get_y2', get.level):
                get.breaks = get.breaks + 1
                if get.breaks == breaks:
                    array.remove(bullms, i)
                    break_down = True
            elif n - method_call('get_x1', get.level) >= maxDuration:
                method_call('delete', array.remove(bullms, i).level)
    support: bool = False
    if array.size(bullms) > 0:
        lvl = method_call('get_y2', array.get(bullms, 0).level)
        support = low < lvl and math.min(close, open) > lvl
    plx: Persistent[int] = 0
    plcross: Persistent[bool] = False
    bearms: Persistent[list[breaker]] = array.new(0, NA(breaker))
    pl: Series = fixnan(ta.pivotlow(length, length))
    if pl != pl[1]:
        plx = n - length
        plcross = False
    if close < pl and (not plcross):
        line.new(plx, pl, n, pl, color=bearCss)
        label.new(cast_int(math.avg(plx, n)), pl, 'MSS' if os == 1 else 'MSB', textcolor=bearCss, color=NA(Color), size=size.small, style=label.style_label_up)
        array.unshift(bearms, breaker(line.new(n, pl, n, pl, color=bearBreakCss, style=line.style_dotted)))
        plcross = True
        if array.size(bearms) > 100:
            array.pop(bearms)
        os = -1
    break_up: bool = False
    if array.size(bearms) > 0:
        for i in pine_range(array.size(bearms) - 1, 0, 1):
            get = array.get(bearms, i)
            method_call('set_x2', get.level, n)
            if close > method_call('get_y2', get.level) and open < method_call('get_y2', get.level):
                get.breaks = get.breaks + 1
                if get.breaks == breaks:
                    array.remove(bearms, i)
                    break_up = True
            elif n - method_call('get_x1', get.level) >= maxDuration:
                method_call('delete', array.remove(bearms, i).level)
    resistance: bool = False
    if array.size(bearms) > 0:
        lvl = method_call('get_y2', array.get(bearms, 0).level)
        resistance = high > lvl and math.max(close, open) < lvl
    plotchar(break_up, 'Bull MSB Breakout', '▲', location.belowbar, color.new('#089981'))
    plotchar(break_down, 'Bear MSB Breakout', '▼', location.abovebar, color.new('#F23645'))
    plotcandle(high, high, low, low, 'Support Events', na, na, bordercolor=color.new('#089981') if support else na, display=display.all - display.status_line)
    plotcandle(high, high, low, low, 'Resistance Events', na, na, bordercolor=color.new('#F23645') if resistance else na, display=display.all - display.status_line)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
