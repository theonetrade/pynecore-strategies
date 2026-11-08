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
    array, bar_index, barstate, chart, close, color, display, fill, format,
    high, input, label, line, linefill, low, math, na, open, plot, script, string, ta, volume
)
from pynecore.types import Color, Label, Line, LineFill, NA, Persistent


@udt
class level:
    indx: int = na(int)
    upper: float = na(float)
    lower: float = na(float)
    mid: float = na(float)
    vol: float = na(float)


@udt
class draw:
    upper: Line = na(Line)
    lower: Line = na(Line)
    mid: Line = na(Line)
    fill__ren__: LineFill = na(LineFill)
    vol: Label = na(Label)


@script.indicator("Volume Order Blocks [BigBeluga]", overlay=True, max_lines_count=500, max_labels_count=500, max_bars_back=5000)
def main(
    length1=input.int(5, "Sensitivity Detection: "),
    mid_l=input.bool(True, "Mid Line"),
    trend_shadow=input.bool(True, "Trend Shadow"),
    col1=input.color(color.new('#26BA9F'), "", inline="col"),
    col2=input.color(color.new('#6626BA'), "", inline="col")
):
    length2: int = length1 + 13

    ema1: float = ta.ema(close, length1)
    ema2: float = ta.ema(close, length2)

    cross_up: bool = ta.crossover(ema1, ema2) and barstate.isconfirmed
    cross_dn: bool = ta.crossunder(ema1, ema2) and barstate.isconfirmed
    lowest: float = ta.lowest(length2)
    highest: float = ta.highest(length2)

    upper_draw: Persistent[list[draw]] = array.new(0, NA(draw))
    lower_draw: Persistent[list[draw]] = array.new(0, NA(draw))

    upper_lvl: Persistent[list[level]] = array.new(0, NA(level))
    lower_lvl: Persistent[list[level]] = array.new(0, NA(level))

    array_vol_upper: list[float] = array.new_float()
    array_vol_lower: list[float] = array.new_float()

    difff = ema2 - ema1
    color_trend = (color.from_gradient(difff, 0, ta.highest(difff, 100), NA(Color), col2) if difff > 0 else color.from_gradient(difff, ta.lowest(difff, 100), 0, col1, NA(Color))) if trend_shadow else NA(Color)

    p1 = plot(ema1, '', display=display.none, editable=False)
    p2 = plot(ema2, '', display=display.none, editable=False)
    fill(p1, p2, color_trend)

    atr = ta.highest(ta.atr(200), 200) * 3
    atr1 = ta.highest(ta.atr(200), 200) * 2

    def f_clear_previous_lines(draw__):
        __block_result__ = na
        if method_call('size', draw__) > 0:
            for l in draw__:
                line.delete(l.upper)
                line.delete(l.lower)
                line.delete(l.mid)
                linefill.delete(l.fill__ren__)
                label.delete(l.vol)
            __block_result__ = array.clear(draw__)
        return __block_result__

    if cross_up:
        vol: Persistent[float] = 0.0
        vol = 0
        for i in pine_range(1, length2):
            if low[i] == lowest:
                index = bar_index - i

                for k in pine_range(0, i):
                    vol += volume[k]

                src = math.min(open[bar_index - index], close[bar_index - index])

                src = lowest + atr1 * 0.5 if src - lowest < atr1 * 0.5 else src

                mid = math.avg(src, lowest)

                l: level = level(index, src, lowest, mid, vol)
                array.push(lower_lvl, l)

    if cross_dn:
        vol: Persistent[float] = 0.0
        vol = 0
        for i in pine_range(1, length2):
            if high[i] == highest:
                index = bar_index - i

                for k in pine_range(0, i):
                    vol += volume[k]

                src = math.max(open[bar_index - index], close[bar_index - index])

                src = highest - atr1 * 0.5 if highest - src < atr1 * 0.5 else src

                mid = math.avg(src, highest)

                l: level = level(index, highest, src, mid, vol)
                array.push(upper_lvl, l)

    if array.size(lower_lvl) > 0:
        for i in pine_range(0, array.size(lower_lvl) - 1):
            l = array.get(lower_lvl, i)
            l1 = array.get(lower_lvl, i - 1)

            mid = l.mid
            mid1 = l1.mid

            if math.abs(mid - mid1) < atr:
                l_: level = level(na, na, na, na, na)
                array.set(lower_lvl, i - 1, l_)

            if close < l.lower:
                l_: level = level(na, na, na, na, na)
                array.set(lower_lvl, i, l_)

        if array.size(lower_lvl) > 15:
            array.shift(lower_lvl)

    if array.size(upper_lvl) > 0:
        for i in pine_range(0, array.size(upper_lvl) - 1):
            l = array.get(upper_lvl, i)
            l1 = array.get(upper_lvl, i - 1)

            upper = l.upper

            mid = l.mid
            mid1 = l1.mid

            if math.abs(mid - mid1) < atr:
                l_: level = level(na, na, na, na, na)
                array.set(upper_lvl, i - 1, l_)

            if close > upper:
                l_: level = level(na, na, na, na, na)
                array.set(upper_lvl, i, l_)

        if array.size(upper_lvl) > 15:
            array.shift(upper_lvl)

    if array.size(lower_lvl) > 0 and barstate.islast:
        f_clear_previous_lines(lower_draw)

        for i in pine_range(0, array.size(lower_lvl) - 1):
            l = array.get(lower_lvl, i)
            array.push(array_vol_lower, l.vol)
        for i in pine_range(0, array.size(lower_lvl) - 1):
            l = array.get(lower_lvl, i)

            txt = '⮜ ' + string.tostring(l.vol / array.sum(array_vol_lower) * 100, format.percent) + ' (' + string.tostring(l.vol, format.volume) + ')'

            l_1 = line.new(l.indx, l.upper, bar_index, l.upper, color=col1, width=2)
            l_2 = line.new(l.indx, l.lower, bar_index, l.lower, color=col1, width=2)
            l_mid = line.new(l.indx, l.mid, bar_index, l.mid, color=col1 if mid_l else NA(Color), style=line.style_dashed)
            vol_l = label.new(bar_index, l.mid, txt, style=label.style_label_left, color=NA(Color), textcolor=chart.fg_color)

            fill__ren__ = linefill.new(l_1, l_2, color.new(col1, 90))

            draw_: draw = draw(l_1, l_2, l_mid, fill__ren__, vol_l)
            array.push(lower_draw, draw_)

    if array.size(upper_lvl) > 0 and barstate.islast:
        f_clear_previous_lines(upper_draw)
        for i in pine_range(0, array.size(upper_lvl) - 1):
            l = array.get(upper_lvl, i)
            array.push(array_vol_upper, l.vol)

        for i in pine_range(0, array.size(upper_lvl) - 1):
            l = array.get(upper_lvl, i)

            txt = '⮜ ' + string.tostring(l.vol / array.sum(array_vol_upper) * 100, format.percent) + ' (' + string.tostring(l.vol, format.volume) + ')'

            l_1 = line.new(l.indx, l.upper, bar_index, l.upper, color=col2, width=2)
            l_2 = line.new(l.indx, l.lower, bar_index, l.lower, color=col2, width=2)
            l_mid = line.new(l.indx, l.mid, bar_index, l.mid, color=col2 if mid_l else NA(Color), style=line.style_dashed)
            vol_l = label.new(bar_index, l.mid, txt, style=label.style_label_left, color=NA(Color), textcolor=chart.fg_color)

            fill__ren__ = linefill.new(l_1, l_2, color.new(col2, 90))

            draw_: draw = draw(l_1, l_2, l_mid, fill__ren__, vol_l)
            array.push(upper_draw, draw_)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
