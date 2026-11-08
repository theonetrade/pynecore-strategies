"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    array, bar_index, box, chart, close, color, display, fill, high, input,
    low, math, na, nz, open, plot, script, ta
)
from pynecore.types import Box, Persistent


@script.indicator('FVG Positioning Average [LuxAlgo]', shorttitle='LuxAlgo - FVG Positioning Average', overlay=True)
def main(
    lb=input.int(30, title='FVG Lookback', tooltip='Determines how many FVGs to consider for calculating the averages.', group='Settings'),
    lbType=input.string('Bar Count', title='Lookback Type', options=('Bar Count', 'FVG Count'), tooltip='Bar Count => Uses any FVGs within this Bar Lookback\nFVG Count => Uses only this amount of recent FVGs', group='Settings'),
    atrMulti=input.float(0.25, step=0.25, title='ATR Multiplier', tooltip='Only uses FVGs that are greater than ATR * Multiplier.', group='Settings'),
    fvgTog=input.bool(True, title='Show FVGs on Chart', group='Style'),
    green=input.color(color.new('#089981'), title='Bullish Color', group='Style'),
    red=input.color(color.new('#F23645'), title='Bearish Color', group='Style'),
    showFill=input.bool(True, title='Show Gradient Areas', group='Style')
):
    invis = color.rgb(0, 0, 0, 100)
    atr = nz(ta.atr(200) * atrMulti, ta.cum(high - low) / (bar_index + 1))
    fvg_up = low > high[2] and close[1] > high[2] and (low - high[2] > atr)
    fvg_down = high < low[2] and close[1] < low[2] and (low[2] - high > atr)
    hst = ta.highest(high, 5)
    lst = ta.lowest(low, 5)
    up_ary: Persistent[list[Box]] = array.new_box(na)
    down_ary: Persistent[list[Box]] = array.new_box(na)
    if fvg_up:
        array.push(up_ary, box.new(bar_index[2], low, bar_index, high[2], border_color=color.new(green, 50) if fvgTog else na, bgcolor=color.new(green, 50) if fvgTog else na))
    if fvg_down:
        array.push(down_ary, box.new(bar_index[2], low[2], bar_index, high, border_color=color.new(red, 50) if fvgTog else na, bgcolor=color.new(red, 50) if fvgTog else na))
    if lbType == 'FVG Count':
        if array.size(up_ary) > lb:
            box.delete(array.shift(up_ary))
        if array.size(down_ary) > lb:
            box.delete(array.shift(down_ary))
    if lbType == 'Bar Count':
        for index, bx in enumerate(up_ary):
            left = box.get_left(bx)
            if left < bar_index - lb:
                box.delete(bx)
                array.remove(up_ary, index)
        for index, bx in enumerate(down_ary):
            left = box.get_left(bx)
            if left < bar_index - lb:
                box.delete(bx)
                array.remove(down_ary, index)
    up_vals: list[float] = array.new_float(na)
    down_vals: list[float] = array.new_float(na)
    for bx in up_ary:
        array.push(up_vals, box.get_bottom(bx))
    for bx in down_ary:
        array.push(down_vals, box.get_top(bx))
    up_avg = array.avg(up_vals)
    down_avg = array.avg(down_vals)
    c_mid_h = math.max(math.avg(open, close), up_avg)
    c_mid_l = math.min(math.avg(open, close), down_avg)
    ua = plot(up_avg, style=plot.style_linebr, color=invis if hst < up_avg else green, title='Bull Average')
    da = plot(down_avg, style=plot.style_linebr, color=invis if lst > down_avg else red, title='Bear Average')
    ul = plot(c_mid_h, display=display.none, editable=False)
    dl = plot(c_mid_l, display=display.none, editable=False)
    fill(ua, ul, c_mid_h, math.min(ta.sma(up_avg, 10), up_avg), color.new(chart.bg_color, 100), invis if c_mid_h <= up_avg else color.new(green, 50), display=display.all if showFill else display.none)
    fill(da, dl, math.max(ta.sma(down_avg, 10), down_avg), c_mid_l, invis if c_mid_l >= down_avg else color.new(red, 50), color.new(chart.bg_color, 100), display=display.all if showFill else display.none)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
