"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    bar_index, bgcolor, box, close, color, input, line, math, na, plot,
    script, ta
)
from pynecore.types import Box, Color, Line, Persistent, PersistentSeries, Series


@script.indicator('Range Detector [LuxAlgo]', 'LuxAlgo - Range Detector', overlay=True, max_boxes_count=500, max_lines_count=500)
def main(
    length=input.int(20, 'Minimum Range Length', minval=2),
    mult=input.float(1.0, 'Range Width', minval=0, step=0.1),
    atrLen=input.int(500, 'ATR Length', minval=1),
    upCss=input(color.new('#089981'), 'Broken Upward', group='Style'),
    dnCss=input(color.new('#F23645'), 'Broken Downward', group='Style'),
    unbrokenCss=input(color.new('#2157F3'), 'Unbroken', group='Style')
):
    bx: Persistent[Box] = na(Box)
    lvl: Persistent[Line] = na(Line)
    max: PersistentSeries[float] = na(float)
    min: PersistentSeries[float] = na(float)
    os: Persistent[int] = 0
    detect_css: Color = na(Color)
    n: Series = bar_index
    atr = ta.atr(atrLen) * mult
    ma = ta.sma(close, length)
    count: Series[int] = 0
    for i in pine_range(0, length - 1, 1):
        count = count + (1 if math.abs(close[i] - ma) > atr else 0)
    if count == 0 and count[1] != count:
        if n[length] <= box.get_right(bx):
            max = math.max(ma + atr, box.get_top(bx))
            min = math.min(ma - atr, box.get_bottom(bx))
            box.set_top(bx, max)
            box.set_rightbottom(bx, n, min)
            box.set_bgcolor(bx, color.new(unbrokenCss, 80))
            avg = math.avg(max, min)
            line.set_y1(lvl, avg)
            line.set_xy2(lvl, n, avg)
            line.set_color(lvl, unbrokenCss)
        else:
            max = ma + atr
            min = ma - atr
            bx = box.new(n[length], ma + atr, n, ma - atr, na, bgcolor=color.new(unbrokenCss, 80))
            lvl = line.new(n[length], ma, n, ma, color=unbrokenCss, style=line.style_dotted)
            detect_css = color.new(color.gray, 80)
            os = 0
    elif count == 0:
        box.set_right(bx, n)
        line.set_x2(lvl, n)
    if close > box.get_top(bx):
        box.set_bgcolor(bx, color.new(upCss, 80))
        line.set_color(lvl, upCss)
        os = 1
    elif close < box.get_bottom(bx):
        box.set_bgcolor(bx, color.new(dnCss, 80))
        line.set_color(lvl, dnCss)
        os = -1
    bgcolor(detect_css)
    plot(max, 'Range Top', na if max != max[1] else unbrokenCss if os == 0 else upCss if os == 1 else dnCss)
    plot(min, 'Range Bottom', na if min != min[1] else unbrokenCss if os == 0 else upCss if os == 1 else dnCss)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
