"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    alertcondition, array, bar_index, box, chart, close, color, extend,
    format, high, input, label, line, location, low, math, na, plotchar, script, size, string, ta,
    text, volume
)
from pynecore.types import Box, Label, Persistent
import lib.PineCoders.VisibleChart.v4 as VisibleChart


@script.indicator('Dynamic Supply and Demand Zones [AlgoAlpha]', 'AlgoAlpha - 📦Dynamic Supply/Demand', overlay=True, max_boxes_count=500, max_bars_back=4999)
def main(
    dynamic=input.bool(True, 'Use Dynamic Look-Back', tooltip='If true, the indicator adjusts its lookback such that it considers data from the previous major pivot point to present', group='Main Calculation'),
    len=input.int(100, 'Look-back (For Non-Dynamic Look-Back)', group='Main Calculation', tooltip='If Dynamic Look-Back is disabled, the indicator will use this fixed look-back instead'),
    plen=input.int(200, 'Pivot Point Detection Period', tooltip='The look-back period of pivot points detection, pivots are detected with delay(depending on user imput, 100 by default)', group='Main Calculation'),
    res=input.int(40, 'Resolution', group='Main Calculation', tooltip='The profile resolution'),
    scale__ren__=input.int(33, 'Profile Horizontal Width', tooltip='The Horizontal Width of the profile, a smaller value will make the profile thinner', maxval=100, minval=1, group='Main Calculation'),
    tolerance=input.float(0.93, 'Zone Tolerance', tooltip='The tolerance for zone detection, the lower the value the less zones will be marked', maxval=1, minval=0.01, group='Main Calculation'),
    h=input.bool(True, 'Show Profile', group='Appearance'),
    h1=input.bool(True, 'Show Background Box', group='Appearance'),
    neut=input.color(color.gray, 'Levels Color', group='Appearance'),
    green=input.color(color.new('#00FFBB'), 'Bullish Color', group='Appearance'),
    red=input.color(color.new('#FF1100'), 'Bearish Color', group='Appearance')
):
    ph = ta.pivothigh(plen, plen)
    pl = ta.pivotlow(plen, plen)
    pivotindex: Persistent[int] = 0
    if not na(ph) or not na(pl):
        pivotindex = bar_index - plen
    len1 = bar_index - pivotindex if dynamic else len
    left: Persistent[int] = 0
    top_boundaries: list[float] = array.new_float(res)
    bottom_boundaries: list[float] = array.new_float(res)
    binlen: list[float] = array.new_float(res)
    boxes: Persistent[list[Box]] = array.new_box()
    highs: list[float] = array.new_float()
    lows: list[float] = array.new_float()
    volumes: list[float] = array.new_float()
    for i in pine_range(0, bar_index - (bar_index - len1), 1):
        array.push(highs, high[i])
        array.push(lows, low[i])
        array.push(volumes, volume[i])
    maxx = array.max(highs)
    minn = array.min(lows)
    size__ren__ = array.size(highs)
    t: Persistent[list[Box]] = array.new_box()
    lab: Persistent[list[Label]] = array.new_label()
    while array.size(t) > 0:
        method_call('delete', array.shift(t))
    while array.size(boxes) > 0:
        method_call('delete', array.shift(boxes))
    while array.size(lab) > 0:
        method_call('delete', array.shift(lab))
    if size__ren__ > 0:
        step = (maxx - minn) / res
        granularity = res
        for i in pine_range(0, granularity - 1, 1):
            bin_size: float = 0.0
            bottom = minn + i * step
            top = minn + (i + 1) * step
            array.insert(bottom_boundaries, i, bottom)
            array.insert(top_boundaries, i, top)
            for j in pine_range(0, array.size(highs) - 1, 1):
                candle_above_hbar = array.get(lows, j) > top
                candle_below_hbar = array.get(highs, j) < bottom
                is_candle_in_bucket = not (candle_above_hbar or candle_below_hbar)
                bin_size = bin_size + (array.get(volumes, j) if is_candle_in_bucket else 0)
            array.insert(binlen, i, bin_size)
    for i in pine_range(0, res - 1, 1):
        iskey = (True if i == res - 1 else array.get(binlen, i) < array.get(binlen, i + 1) * tolerance) and (True if i == 0 else array.get(binlen, i) < array.get(binlen, i - 1) * tolerance)
        box_right = bar_index
        box_left = bar_index - len1 if iskey else bar_index
        box_top = array.get(top_boundaries, i)
        box_bottom = array.get(bottom_boundaries, i)
        left = box_left
        if iskey:
            array.push(boxes, box.new(box_left, box_top, box_right, box_bottom, border_style=line.style_solid, border_color=color.new(neut, 70), border_width=1, bgcolor=color.new(neut, 80)))
            array.push(lab, label.new(box_left, math.avg(box_top, box_bottom), string.tostring((1 - array.get(binlen, i) / array.max(binlen)) * 100, format.percent), color=chart.fg_color, textcolor=chart.bg_color, style=label.style_label_right))
    for i in pine_range(0, res - 1, 1):
        box_right = bar_index + 7 + scale__ren__
        box_left = box_right - math.round(array.get(binlen, i)) / math.round(array.max(binlen)) * scale__ren__
        box_top = array.get(top_boundaries, i)
        box_bottom = array.get(bottom_boundaries, i)
        left = box_left
        array.push(boxes, box.new(box_left, box_top, box_right, box_bottom, border_style=line.style_solid, border_color=color.black, border_width=1, bgcolor=color.gray) if h else na)
    if h1:
        array.push(t, box.new(bar_index - len1, array.max(top_boundaries), bar_index, array.min(bottom_boundaries), color.new(color.blue, 70), 1, line.style_solid, extend.none, bgcolor=color.new(color.blue, 90), text='Total Look-Back Data', text_size=size.tiny, text_color=color.gray, text_halign=text.align_center, text_valign=text.align_top))
    if array.size(boxes) > 0:
        qt = array.size(boxes)
        for ln in pine_range(qt - 1, 0, 1):
            if ln < array.size(boxes):
                cL = array.get(boxes, ln)
                yL = method_call('get_top', cL)
                yLa = method_call('get_bottom', cL)
                if close > yL:
                    method_call('set_border_color', cL, color.new(green, 50))
                    method_call('set_bgcolor', cL, color.new(green, 50))
                elif close < yLa:
                    method_call('set_border_color', cL, color.new(red, 50))
                    method_call('set_bgcolor', cL, color.new(red, 50))
    plotchar(True if ph != 0 else False, 'Pivot Highs', '●', location.abovebar, chart.fg_color, size=size.tiny, offset=-plen)
    plotchar(True if pl != 0 else False, 'Pivot Lows', '●', location.belowbar, chart.fg_color, size=size.tiny, offset=-plen)
    alertcondition(not na(ph) or not na(pl), 'New Pivot Detected!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
