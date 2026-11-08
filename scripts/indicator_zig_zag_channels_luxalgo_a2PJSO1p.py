"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.series import inline_series
from pynecore.lib import (
    bar_index, barstate, close, color, extend, high, input, label, line, low,
    math, na, open, plot, script, size, string, ta, text
)
from pynecore.types import Persistent, Series


@script.indicator('Zig Zag Channels [LuxAlgo]', overlay=True, max_bars_back=5000, max_lines_count=500, max_labels_count=500, na_bool=True)
def main(
    length=input(100),
    extend__ren__=input(True, 'Extend To Last Bar'),
    show_ext=input(True, 'Show Extremities'),
    show_labels=input(True, 'Show Labels'),
    upcol=input.color(color.new('#FF1100'), 'Upper Extremity Color', group='Style'),
    midcol=input.color(color.new('#FF5D00'), 'Zig Zag Color', group='Style'),
    dncol=input.color(color.new('#2157F3'), 'Lower Extremity Color', group='Style')
):
    os: Series[int] = 0
    src: Series = close
    n: Series = bar_index
    valtop: Persistent[float] = na(float)
    valbtm: Persistent[float] = na(float)
    upper = ta.highest(src, length)
    lower = ta.lowest(src, length)
    os = 0 if src[length] > upper else 1 if src[length] < lower else os[1]
    btm = os == 1 and os[1] != 1
    top = os == 0 and os[1] != 0
    btm_n = ta.valuewhen(btm, n, 0)
    top_n = ta.valuewhen(top, n, 0)
    len = math.abs(btm_n - top_n)
    if btm:
        max_diff_up: float = 0.0
        max_diff_dn: float = 0.0
        valbtm = low[length]
        for i in pine_range(0, len - 1, 1):
            point = low[length] + i / (len - 1) * (valtop - low[length])
            max_diff_up = math.max(math.max(src[length + i], open[length + i]) - point, max_diff_up)
            max_diff_dn = math.max(point - math.min(src[length + i], open[length + i]), max_diff_dn)
        line.new(n[len + length], valtop, n[length], low[length], color=midcol)
        if show_ext:
            line.new(n[len + length], valtop + max_diff_up, n[length], low[length] + max_diff_up, color=upcol, style=line.style_dotted)
            line.new(n[len + length], valtop - max_diff_dn, n[length], low[length] - max_diff_dn, color=dncol, style=line.style_dotted)
        if show_labels:
            label.new(n[length], low[length], string.tostring(low[length], '#.####'), color=color.new('#00000000'), style=label.style_label_up, textcolor=dncol, textalign=text.align_left, size=size.small)
    if top:
        max_diff_up: float = 0.0
        max_diff_dn: float = 0.0
        valtop = high[length]
        for i in pine_range(0, len - 1, 1):
            point = high[length] + i / (len - 1) * (valbtm - high[length])
            max_diff_up = math.max(math.max(src[length + i], open[length + i]) - point, max_diff_up)
            max_diff_dn = math.max(point - math.min(src[length + i], open[length + i]), max_diff_dn)
        line.new(n[len + length], valbtm, n[length], high[length], color=midcol)
        if show_ext:
            line.new(n[len + length], valbtm + max_diff_up, n[length], high[length] + max_diff_up, color=upcol, style=line.style_dotted)
            line.new(n[len + length], valbtm - max_diff_dn, n[length], high[length] - max_diff_dn, color=dncol, style=line.style_dotted)
        if show_labels:
            label.new(n[length], high[length], string.tostring(high[length], '#.####'), color=color.new('#00000000'), style=label.style_label_down, textcolor=upcol, textalign=text.align_left, size=size.small)
    if barstate.islast and extend__ren__:
        max_diff_up: float = 0.0
        max_diff_dn: float = 0.0
        x1: int = 0
        y1: float = 0.0
        if os == 1:
            x1 = btm_n - length
            y1 = valbtm
            for i in pine_range(0, n - btm_n + length - 1, 1):
                point = src + i / (n - btm_n + length - 1) * (valbtm - src)
                max_diff_up = math.max(math.max(src[i], open[i]) - point, max_diff_up)
                max_diff_dn = math.max(point - math.min(src[i], open[i]), max_diff_dn)
        else:
            x1 = top_n - length
            y1 = valtop
            for i in pine_range(0, n - top_n + length - 1, 1):
                point = src + i / (n - top_n + length - 1) * (valtop - src)
                max_diff_up = math.max(math.max(src[i], open[i]) - point, max_diff_up)
                max_diff_dn = math.max(point - math.min(src[i], open[i]), max_diff_dn)
        line.delete(inline_series(line.new(x1, y1, n, src, color=midcol, extend=extend.right), 1))
        if show_ext:
            line.delete(inline_series(line.new(x1, y1 + max_diff_up, n, src + max_diff_up, color=upcol, style=line.style_dotted, extend=extend.right), 1))
            line.delete(inline_series(line.new(x1, y1 - max_diff_dn, n, src - max_diff_dn, color=dncol, style=line.style_dotted, extend=extend.right), 1))
    plot(low[length] if btm else high[length] if top else na, 'Circles', color=dncol if btm else upcol, style=plot.style_circles, offset=-length)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
