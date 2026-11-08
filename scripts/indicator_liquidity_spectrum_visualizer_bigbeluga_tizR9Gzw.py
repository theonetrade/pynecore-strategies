"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.series import inline_series
from pynecore.lib import (
    array, bar_index, barstate, box, chart, close, color, display, format,
    high, hlc3, input, label, last_bar_index, line, location, low, math, na, open, plotshape,
    script, shape, size, string, ta, volume, xloc, yloc
)
from pynecore.types import Box, Color, Line, NA, Persistent


@script.indicator("Liquidity Spectrum Visualizer [BigBeluga]", overlay=True, max_boxes_count=500, max_labels_count=500)
def main(
    lookback=input.int(200, "LookBack"),
    vol_bubles=input.bool(True, "Display Volume Bubles"),
    volume_pr=input.bool(True, "Volume Profile"),
    liq_levels=input.bool(True, "Liquidity Levels"),
    col_up=input.color(color.new('#22B16C'), "", inline="colors"),
    col_dn=input.color(color.new('#DD7E2A'), "", inline="colors")
):
    allow = last_bar_index - bar_index < lookback

    display__ren__ = display.all if allow else display.none

    n_vol = volume / ta.stdev(volume, 200)

    size__ren__ = size.small if n_vol >= 1 and n_vol < 2 else size.normal if n_vol >= 2 and n_vol < 3 else size.large if n_vol >= 3 and n_vol < 4 else size.huge if n_vol >= 4 else size.tiny

    cond0 = n_vol < 1
    cond1 = n_vol >= 1 and n_vol < 2
    cond2 = n_vol >= 2 and n_vol < 3
    cond3 = n_vol >= 3 and n_vol < 4
    cond4 = n_vol >= 4

    offset = -lookback - (50 if volume_pr else 0)

    if barstate.islast:
        h_l: list[float] = array.new_float()

        for j in pine_range(0, lookback - 1):
            array.push(h_l, high[j])
            array.push(h_l, low[j])

        bins: list[float] = array.new_float(100)

        step = (array.max(h_l) - array.min(h_l)) / 100
        boxes_bins: Persistent[list[Box]] = array.new_box()
        poc_lvls: Persistent[list[Line]] = array.new_line()

        for b in boxes_bins:
            box.delete(b)

        for l in poc_lvls:
            line.delete(l)

        array.clear(boxes_bins)
        array.clear(poc_lvls)

        for i in pine_range(0, 100 - 1):
            array.set(bins, i, 0)

        for i in pine_range(0, array.size(bins) - 1):
            lower = array.min(h_l) + step * i
            upper = lower + step

            for j in pine_range(0, lookback - 1):
                if high[j] == array.max(h_l):
                    label.new(bar_index - j, high[j], style=label.style_label_down, text=string.tostring(high[j]), color=col_dn)

                if low[j] == array.min(h_l):
                    label.new(bar_index - j, low[j], style=label.style_label_up, text=string.tostring(low[j]), color=col_up)

                c = close[j]

                if c >= lower - step and c <= upper + step:
                    array.set(bins, i, array.get(bins, i) + volume[j])

        for i in pine_range(0, array.size(bins) - 1):
            lower = array.min(h_l) + step * i
            upper = lower + step
            val = cast_int(array.get(bins, i) / array.max(bins) * 50)

            col_res_sup = col_up if close > math.avg(upper, lower) else col_dn

            if volume_pr:
                vp_col = color.from_gradient(val, 0, 50, color.new(col_res_sup, 90), col_res_sup)

                array.push(boxes_bins, box.new(bar_index + offset, upper, bar_index + val + offset, lower, bgcolor=vp_col, border_color=NA(Color)))

            if val > 25 and liq_levels:
                color_pocs = color.from_gradient(val, 25, 50, color.new(col_res_sup, 90), col_res_sup)
                width = 1 if val < 35 else 2 if val > 35 else 3 if val > 45 else 1
                array.push(poc_lvls, line.new(bar_index + offset, math.avg(upper, lower), bar_index + 5, math.avg(upper, lower), color=color_pocs, width=width))

        box.delete(inline_series(box.new(bar_index + offset, array.max(h_l), bar_index + 5, array.min(h_l), color.new(chart.fg_color, 50), 1, bgcolor=na), 1))

    colorr = col_up if close > open else col_dn
    gradient_col = color.from_gradient(n_vol, 0, 5, color.new(colorr, 50), colorr)

    display_vol = display.all if vol_bubles else display.none
    plotshape(hlc3 if allow and cond0 else na, '', shape.circle, location.absolute, gradient_col, 0, '', na, size=size.tiny, show_last=lookback, force_overlay=True, editable=False, display=display_vol)
    plotshape(hlc3 if allow and cond1 else na, '', shape.circle, location.absolute, gradient_col, 0, '', na, size=size.small, show_last=lookback, force_overlay=True, editable=False, display=display_vol)
    plotshape(hlc3 if allow and cond2 else na, '', shape.circle, location.absolute, gradient_col, 0, '', na, size=size.normal, show_last=lookback, force_overlay=True, editable=False, display=display_vol)
    plotshape(hlc3 if allow and cond3 else na, '', shape.circle, location.absolute, gradient_col, 0, '', na, size=size.large, show_last=lookback, force_overlay=True, editable=False, display=display_vol)
    plotshape(hlc3 if allow and cond4 else na, '', shape.circle, location.absolute, gradient_col, 0, '', na, size=size.huge, show_last=lookback, force_overlay=True, editable=False, display=display_vol)

    if cond4 and allow and vol_bubles:
        label.new(bar_index, hlc3, string.tostring(volume, format.volume), xloc.bar_index, yloc.price, color.new('#00000000'), label.style_label_center, chart.fg_color, force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
