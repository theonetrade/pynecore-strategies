"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, array, bar_index, close, color, display, high, input,
    label, line, low, math, na, plot, script, string, syminfo, ta, text
)
from pynecore.types import Label, Line, Persistent, Series


@script.indicator('Cup Finder', 'CF', overlay=True, max_lines_count=500, na_bool=True)
def main(
    loopback=input.int(defval=150, title='Number of Bars to search', minval=30, maxval=250),
    widthr=input.float(defval=5.0, title='Channel Width of the Cup', minval=1),
    check_hc=input.string(defval='Close', title='Source for Breakout', options=('Close', 'High/Low')),
    __input_3__=input.float(75.0, title='Contained Bar Rate %', minval=10, maxval=100),
    show_channel=input(False, title='Show Channels of Cups'),
    no_label=input(False, title='Don\'t Show Labels'),
    remove_old_lines=input(False, title='Remove Old Lines'),
    remove_old_labels=input(False, title='Remove Old Labels'),
    bullcolor=input.color(defval=color.lime, title='Colors', inline='colors'),
    bearcolor=input.color(defval=color.red, title='', inline='colors')
):
    include_rate = __input_3__ / 100
    width: float = (ta.highest(292) - ta.lowest(292)) / 100
    uwidth: float = width * widthr
    highestbar: Series[bool] = ta.highestbars(30) == 0
    lowestbar: Series[bool] = ta.lowestbars(30) == 0
    bullsrc: float = close if check_hc == 'Close' else high
    bearsrc: float = close if check_hc == 'Close' else low
    hh: float = 0.0
    lasthh: float = 0.0
    ind: int = 0
    bull: bool = False
    for x in pine_range(1, loopback, 1):
        lasthh = math.max(lasthh, high[x])
        if bullsrc <= lasthh:
            break
        if x >= 20 and bullsrc > high[x] and (close[1] < high[x]) and (high[x] >= lasthh) and highestbar[x]:
            hh = high[x]
            ind = x
            bull = True
    ll: float = 0.0
    lastll = ta.highest(292)
    if ind == 0:
        for x in pine_range(1, loopback, 1):
            lastll = math.min(lastll, low[x])
            if bearsrc >= lastll:
                break
            if x >= 20 and bearsrc < low[x] and (close[1] > low[x]) and (low[x] <= lastll) and lowestbar[x]:
                ll = low[x]
                ind = x
    def Round(val):
        return math.round(val / syminfo.mintick) * syminfo.mintick

    cup_lines: Persistent[list[Line]] = array.new_line(0)
    cup_label: Persistent[Label] = na(Label)
    levs: list[float] = array.new_float(0)
    bullish_cup: bool = False
    bearish_cup: bool = False
    included: int = na(int)
    if ind != 0:
        pow_radius: float = math.pow(ind / 2, 2)
        end = math.round((ind - ind % 2) / 2)
        if ind % 2 == 0:
            array.push(levs, hh - math.sqrt(pow_radius) * width if bull else ll + math.sqrt(pow_radius) * width)
        for x in pine_range(1, end, 1):
            ycoord = math.sqrt(pow_radius - math.pow(x, 2)) * width
            array.push(levs, hh - ycoord if bull else ll + ycoord)
            array.unshift(levs, hh - ycoord if bull else ll + ycoord)
        if ind % 2 == 1:
            array.push(levs, hh if bull else ll)
            array.unshift(levs, hh if bull else ll)
        in_cnt: int = 0
        for x in pine_range(0, array.size(levs) - 1, 1):
            if math.min(array.get(levs, x) + uwidth, high[x]) - math.max(array.get(levs, x) - uwidth, low[x]) > 0:
                in_cnt = in_cnt + 1
        if in_cnt / (ind + 1) >= include_rate:
            if not no_label:
                if remove_old_labels:
                    label.delete(cup_label)
                cup_label = label.new(bar_index, array.get(levs, 0), text='Cup\nRadius = ' + string.tostring(Round(width * ind / 2)) + '\nIncluded = ' + string.tostring(100 * in_cnt / (ind + 1), '#.#') + '%', color=bullcolor if bull else bearcolor, textcolor=color.black if bull else color.white, textalign=text.align_left, style=label.style_label_lower_right if bull else label.style_label_upper_right)
            if remove_old_lines and array.size(cup_lines) > 0:
                for x in pine_range(0, array.size(cup_lines) - 1, 1):
                    line.delete(array.get(cup_lines, x))
            array.push(cup_lines, line.new(x1=bar_index, y1=array.get(levs, 0), x2=bar_index - ind + 1, y2=array.get(levs, 0), color=bullcolor if bull else bearcolor, style=line.style_dashed))
            xloc__ren__ = ind
            for x in pine_range(0, array.size(levs) - 2, 1):
                array.push(cup_lines, line.new(x1=bar_index - xloc__ren__, y1=array.get(levs, x), x2=bar_index - xloc__ren__ + 1, y2=array.get(levs, x + 1), color=bullcolor if bull else bearcolor, width=3))
                if show_channel and x % 2 == 0 and (x > 0) and (x < array.size(levs) - 2):
                    array.push(cup_lines, line.new(x1=bar_index - xloc__ren__, y1=array.get(levs, x) + uwidth, x2=bar_index - xloc__ren__ + 1, y2=array.get(levs, x + 1) + uwidth, color=bullcolor if bull else bearcolor))
                    array.push(cup_lines, line.new(x1=bar_index - xloc__ren__, y1=array.get(levs, x) - uwidth, x2=bar_index - xloc__ren__ + 1, y2=array.get(levs, x + 1) - uwidth, color=bullcolor if bull else bearcolor))
                xloc__ren__ = xloc__ren__ - 1
            included = math.round(100 * in_cnt / (ind + 1))
            if bull:
                bullish_cup = True
            else:
                bearish_cup = True
    plot(included, title='included', display=display.none)
    alertcondition(bullish_cup, title='Bullish Cup Found', message='Bullish Cup Found, Included:{{plot("included")}}')
    alertcondition(bearish_cup, title='Bearish Cup Found', message='Bearish Cup Found, Included:{{plot("included")}}')
    alertcondition(bullish_cup or bearish_cup, title='Cup Found', message='Cup Found, Included:{{plot("included")}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)