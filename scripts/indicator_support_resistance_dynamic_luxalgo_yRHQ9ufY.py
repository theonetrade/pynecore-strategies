"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barstate, box, close, color, fill, input, line, math,
    na, nz, plot, script, ta, time, xloc
)
from pynecore.types import Box, Line, NA, Persistent, PersistentSeries


@udt
class sr:
    y: float = na(float)
    area: float = na(float)
    x: int = na(int)
    support: bool = na(bool)


@script.indicator('Support & Resistance Dynamic [LuxAlgo]', 'LuxAlgo - Support & Resistance Dynamic', overlay=True)
def main(
    mult=input.float(8.0, 'Multiplicative Factor', minval=0, step=0.5),
    atrLen=input.int(50, 'ATR Length', minval=0),
    extLast=input.int(4, 'Extend Last', minval=0),
    supCss=input.color(color.new('#089981'), 'Support    ', inline='sup', group='Style'),
    supAreaCss=input(color.new(color.new('#089981'), 80), 'Areas', inline='sup', group='Style'),
    resCss=input.color(color.new('#F23645'), 'Resistance', inline='res', group='Style'),
    resAreaCss=input(color.new(color.new('#F23645'), 80), 'Areas', inline='res', group='Style'),
    extLvls=input(True, 'Extend Levels', group='Style'),
    extArea=input(True, 'Extend Areas', group='Style')
):
    records: Persistent[list[sr]] = array.new(0, NA(sr))
    avg: PersistentSeries[float] = close
    hold_atr: Persistent[float] = 0.0
    os: Persistent[int] = 0
    n = bar_index
    breakout_atr = nz(ta.atr(atrLen)) * mult
    avg = close if math.abs(close - avg) > breakout_atr else avg
    hold_atr = breakout_atr if avg == close else hold_atr
    os = 1 if avg > avg[1] else 0 if avg < avg[1] else os
    upper_res = avg + hold_atr / mult if os == 0 else na
    lower_res = avg + hold_atr / mult / 2 if os == 0 else na
    upper_sup = avg - hold_atr / mult / 2 if os == 1 else na
    lower_sup = avg - hold_atr / mult if os == 1 else na
    if close == avg:
        if os == 1:
            array.unshift(records, sr(lower_sup, upper_sup, time, True))
        else:
            array.unshift(records, sr(upper_res, lower_res, time, False))
    lines: Persistent[list[Line]] = array.new_line(0)
    boxes: Persistent[list[Box]] = array.new_box(0)
    if barstate.isfirst and extLast > 0:
        for i in pine_range(0, extLast - 1, 1):
            if extLvls:
                array.push(lines, line.new(na, na, na, na, xloc.bar_time, style=line.style_dashed))
            if extArea:
                array.push(boxes, box.new(na, na, na, na, na, xloc=xloc.bar_time))
    if barstate.islast and extLast > 0:
        for i in pine_range(0, extLast - 1, 1):
            get_sr = array.get(records, i)
            if extLvls:
                get_line = array.get(lines, i)
                method_call('set_xy1', get_line, get_sr.x, get_sr.y)
                method_call('set_xy2', get_line, time, get_sr.y)
                method_call('set_color', get_line, supCss if get_sr.support else resCss)
            if extArea:
                get_box = array.get(boxes, i)
                method_call('set_lefttop', get_box, get_sr.x, get_sr.area)
                method_call('set_rightbottom', get_box, time, get_sr.y)
                method_call('set_bgcolor', get_box, supAreaCss if get_sr.support else resAreaCss)
    plot_upper_sup = plot(upper_sup, 'Upper Support', na, style=plot.style_linebr)
    plot_lower_sup = plot(lower_sup, 'Lower Support', na if close == avg else supCss, style=plot.style_linebr)
    plot_upper_res = plot(upper_res, 'Upper Resistance', na if close == avg else resCss, style=plot.style_linebr)
    plot_lower_res = plot(lower_res, 'Lower Resistance', na, style=plot.style_linebr)
    fill(plot_upper_sup, plot_lower_sup, supAreaCss, 'Support Area')
    fill(plot_upper_res, plot_lower_res, resAreaCss, 'Resistance Area')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
