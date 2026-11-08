"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, box, close, color, display,
    extend, high, hl2, input, line, low, math, na, plot, script, ta, time, volume, xloc
)
from pynecore.types import Box, Line, Persistent, PersistentSeries


@script.indicator('Order Block Detector [LuxAlgo]', overlay=True, max_boxes_count=500, max_labels_count=500, max_lines_count=500)
def main(
    length=input.int(5, 'Volume Pivot Length', minval=1),
    bull_ext_last=input.int(3, 'Bullish OB ', minval=1, inline='bull'),
    bg_bull_css=input.color(color.new(color.new('#169400'), 80), '', inline='bull'),
    bull_css=input.color(color.new('#169400'), '', inline='bull'),
    bull_avg_css=input.color(color.new(color.new('#9598A1'), 37), '', inline='bull'),
    bear_ext_last=input.int(3, 'Bearish OB', minval=1, inline='bear'),
    bg_bear_css=input.color(color.new(color.new('#FF1100'), 80), '', inline='bear'),
    bear_css=input.color(color.new('#FF1100'), '', inline='bear'),
    bear_avg_css=input.color(color.new(color.new('#9598A1'), 37), '', inline='bear'),
    line_style=input.string('⎯⎯⎯', 'Average Line Style', options=('⎯⎯⎯', '----', '····')),
    line_width=input.int(1, 'Average Line Width', minval=1),
    mitigation=input.string('Wick', 'Mitigation Methods', options=('Wick', 'Close'))
):
    def get_line_style(style):
        __block_result__ = na
        __switch__ = style
        if __switch__ == '⎯⎯⎯':
            __block_result__ = line.style_solid
        elif __switch__ == '----':
            __block_result__ = line.style_dashed
        elif __switch__ == '····':
            __block_result__ = line.style_dotted
        out = __block_result__
        return out

    def get_coordinates(condition, top, btm, ob_val):
        ob_top: Persistent[list[float]] = array.new_float(0)
        ob_btm: Persistent[list[float]] = array.new_float(0)
        ob_avg: Persistent[list[float]] = array.new_float(0)
        ob_left: Persistent[list[int]] = array.new_int(0)
        ob: float = na(float)
        if condition:
            avg = math.avg(top, btm)
            array.unshift(ob_top, top)
            array.unshift(ob_btm, btm)
            array.unshift(ob_avg, avg)
            array.unshift(ob_left, time[length])
            ob = ob_val
        return (ob_top, ob_btm, ob_avg, ob_left, ob)

    def remove_mitigated(ob_top, ob_btm, ob_left, ob_avg, target, bull):
        mitigated: bool = False
        target_array = ob_btm if bull else ob_top
        for element in target_array:
            idx = array.indexof(target_array, element)
            if target < element if bull else target > element:
                mitigated = True
                array.remove(ob_top, idx)
                array.remove(ob_btm, idx)
                array.remove(ob_avg, idx)
                array.remove(ob_left, idx)
        return mitigated

    def set_order_blocks(ob_top, ob_btm, ob_left, ob_avg, ext_last, bg_css, border_css, lvl_css):
        ob_box: Persistent[list[Box]] = array.new_box(0)
        ob_lvl: Persistent[list[Line]] = array.new_line(0)
        if barstate.isfirst:
            for i in pine_range(0, ext_last - 1, 1):
                array.unshift(ob_box, box.new(na, na, na, na, xloc=xloc.bar_time, extend=extend.right, bgcolor=bg_css, border_color=color.new(border_css, 70)))
                array.unshift(ob_lvl, line.new(na, na, na, na, xloc=xloc.bar_time, extend=extend.right, color=lvl_css, style=get_line_style(line_style), width=line_width))
        __block_result_1__ = na
        if barstate.islast:
            __block_result_2__ = na
            if array.size(ob_top) > 0:
                __block_result_3__ = na
                __loop_2__ = pine_loop(0, 1)
                while __loop_2__.step(math.min(ext_last - 1, array.size(ob_top) - 1)):
                    i = __loop_2__.value
                    get_box = array.get(ob_box, i)
                    get_lvl = array.get(ob_lvl, i)
                    box.set_lefttop(get_box, array.get(ob_left, i), array.get(ob_top, i))
                    box.set_rightbottom(get_box, array.get(ob_left, i), array.get(ob_btm, i))
                    line.set_xy1(get_lvl, array.get(ob_left, i), array.get(ob_avg, i))
                    __block_result_3__ = line.set_xy2(get_lvl, array.get(ob_left, i) + 1, array.get(ob_avg, i))
                __block_result_2__ = __block_result_3__
            __block_result_1__ = __block_result_2__
        return __block_result_1__

    os: PersistentSeries[int] = 0
    target_bull: Persistent[float] = 0.0
    target_bear: Persistent[float] = 0.0
    n = bar_index
    upper = ta.highest(length)
    lower = ta.lowest(length)
    if mitigation == 'Close':
        target_bull = ta.lowest(close, length)
        target_bear = ta.highest(close, length)
    else:
        target_bull = lower
        target_bear = upper
    os = 0 if high[length] > upper else 1 if low[length] < lower else os[1]
    phv = ta.pivothigh(volume, length, length)
    bull_top, bull_btm, bull_avg, bull_left, bull_ob = get_coordinates(cast_bool(phv) and os == 1, hl2[length], low[length], low[length])
    bear_top, bear_btm, bear_avg, bear_left, bear_ob = get_coordinates(cast_bool(phv) and os == 0, high[length], hl2[length], high[length])
    mitigated_bull = remove_mitigated(bull_top, bull_btm, bull_left, bull_avg, target_bull, True)
    mitigated_bear = remove_mitigated(bear_top, bear_btm, bear_left, bear_avg, target_bear, False)
    set_order_blocks(bull_top, bull_btm, bull_left, bull_avg, bull_ext_last, bg_bull_css, bull_css, bull_avg_css)
    set_order_blocks(bear_top, bear_btm, bear_left, bear_avg, bear_ext_last, bg_bear_css, bear_css, bear_avg_css)
    plot(bull_ob, 'Bull OB', bull_css, 2, plot.style_linebr, offset=-length, display=display.none)
    plot(bear_ob, 'Bear OB', bear_css, 2, plot.style_linebr, offset=-length, display=display.none)
    alertcondition(bull_ob, 'Bullish OB Formed', 'Bullish order block detected')
    alertcondition(bear_ob, 'Bearish OB Formed', 'bearish order block detected')
    alertcondition(mitigated_bull, 'Bullish OB Mitigated', 'Bullish order block mitigated')
    alertcondition(mitigated_bear, 'Bearish OB Mitigated', 'bearish order block mitigated')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
