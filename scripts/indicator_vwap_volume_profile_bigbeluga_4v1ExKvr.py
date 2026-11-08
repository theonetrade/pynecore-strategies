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
    array, bar_index, barcolor, barstate, box, chart, close, color, display,
    format, high, hl2, input, label, last_bar_index, low, na, open, plot, plotcandle, script, size,
    string, ta, text, volume
)
from pynecore.types import Box, Color, NA, Persistent, Series


@script.indicator("VWAP Volume Profile [BigBeluga]", overlay=True, max_bars_back=500, max_boxes_count=500)
def main(
    period=input.int(250),
    offset=input.int(10),
    bins=input.int(50),
    poc_type1=input.string("+/-VWAP", "POC", options=("+VWAP", "-VWAP", "+/-VWAP")),
    up_col=input.color(color.new('#42BDA8'), "+/-", inline="col"),
    dn_col=input.color(color.new('#FFB950'), "", inline="col"),
    bgcol=input.color(color.rgb(5, 38, 82, 80), "", inline="col")
):
    poc_type: int = 1 if poc_type1 == '+VWAP' else 2 if poc_type1 == '-VWAP' else 3

    vwap: Series[float] = ta.vwap(close)
    vwap_col: Color = up_col if vwap > vwap[5] else dn_col
    src: Series[float] = vwap

    def get_vol(vwap):
        __hist_src__: Series[float] = src[0]
        if ta.cum(volume) < 1 and barstate.islast:
            label.new(bar_index, hl2, 'No Volume Data Provided', size=size.huge)
        vol = volume
        sum = ta.highest(vol, 1000)

        volume_ = vol if src > __hist_src__[2] else -vol
        return volume_ / sum * 20

    def get_grid(period, bins):
        H = ta.highest(period)
        L = ta.lowest(period)
        step = (H - L) / bins

        return (H, L, step)

    def vwap_profile(src: Series, period, bins):
        H, L, step = get_grid(period, bins)
        volume_: Series[float] = get_vol(vwap)

        pos_poc: Series[Box] = NA(Box)
        neg_poc: Series[Box] = NA(Box)
        bg_col: Color = NA(Color)
        vp: Persistent[list[Box]] = array.new_box(bins, NA(Box))

        volume_1: list[int] = array.new_int(bins, 0)
        volume_2: list[float] = array.new_float(bins, 0.0)

        n: int = bar_index + offset

        __block_result__ = na
        if barstate.islast:
            for i in pine_range(0, array.size(vp) - 1):
                low_: float = L + step * i
                high_: float = low_ + step
                box_id: Box = array.get(vp, i)

                for j in pine_range(0, period - 1):
                    source: float = src[j]
                    value: int = cast_int(volume_[j])

                    if source >= low_ - step and source <= high_ + step:
                        array.set(volume_1, i, array.get(volume_1, i) + value)
                        array.set(volume_2, i, array.get(volume_2, i) + volume[j])

                bg_col = color.from_gradient(array.get(volume_1, i), 0, array.max(volume_1), color.new(up_col, 90), up_col) if array.get(volume_1, i) > 0 else color.from_gradient(array.get(volume_1, i), array.min(volume_1), 0, dn_col, color.new(dn_col, 90))

                if na(box_id):
                    array.set(vp, i, box.new(n, high_, n + array.get(volume_1, i), low_, border_color=chart.bg_color, bgcolor=bg_col, force_overlay=True))

                box.set_rightbottom(box_id, n + array.get(volume_1, i), low_)
                box.set_lefttop(box_id, n, high_)
                box.set_bgcolor(box_id, bg_col)

                if array.get(volume_1, i) == array.max(volume_1) and (poc_type == 1 or poc_type == 3):
                    box.delete(pos_poc)
                    pos_poc = box.new(bar_index - period, high_, n, low_, text_size=size.normal, force_overlay=True)

                    box.set_bgcolor(pos_poc, color.new(bg_col, 90))
                    box.set_border_color(pos_poc, color.new(bg_col, 50))
                    box.set_text(pos_poc, '+VWAP: ' + string.tostring(array.get(volume_2, i), format.volume))
                    box.set_text_color(pos_poc, bg_col)
                    box.set_text_halign(pos_poc, text.align_left)

                    box.delete(pos_poc[1])

                if array.get(volume_1, i) == array.min(volume_1) and (poc_type == 2 or poc_type == 3):
                    box.delete(neg_poc)
                    neg_poc = box.new(bar_index - period, high_, n, low_, text_size=size.normal, force_overlay=True)

                    box.set_bgcolor(neg_poc, color.new(bg_col, 90))
                    box.set_border_color(neg_poc, color.new(bg_col, 50))
                    box.set_text(neg_poc, '-VWAP: ' + string.tostring(array.get(volume_2, i), format.volume))
                    box.set_text_color(neg_poc, bg_col)
                    box.set_text_halign(neg_poc, text.align_left)

                    box.delete(neg_poc[1])

            __block_result__ = box.delete(inline_series(box.new(bar_index - period, H, n, L, border_color=na, bgcolor=bgcol, force_overlay=False), 1))
        return __block_result__

    vwap_profile(src, period, bins)

    vwap_col = vwap_col if last_bar_index - bar_index < period else na

    plot(vwap if last_bar_index - bar_index < period else na, 'VWAP', color=vwap_col, linewidth=3, force_overlay=True)
    plotcandle(open, high, low, close, title='Candles Color', color=vwap_col, wickcolor=vwap_col, bordercolor=vwap_col, force_overlay=True)
    barcolor(vwap_col, display=display.none)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
