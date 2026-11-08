"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    alertcondition, array, bar_index, box, chart, close, color, display,
    fill, format, high, input, line, location, low, math, na, nz, open, plot, plotchar, script,
    size, string, ta, volume
)
from pynecore.types import Box, Line, NA, Persistent


@script.indicator("Volume Sentiment Breakout Channels [AlgoAlpha]", shorttitle="AlgoAlpha - Sentiment Breakout", max_boxes_count=500, overlay=True, max_bars_back=5000, behind_chart=False)
def main(
    length_=input.int(100, title="Normalization Length", minval=1, group="Main Settings", tooltip="The number of bars used to calculate the highest high and lowest low for price normalization. Higher values create more stable normalization but may be less responsive to recent price changes."),
    length=input.int(14, "Box Detection Length", minval=1, group="Main Settings", tooltip="The number of bars used to detect channel formation patterns. Lower values create more frequent channels but may be more sensitive to noise. Higher values create fewer but potentially more significant channels."),
    strong=input.bool(True, "Strong Closes Only", group="Main Settings", tooltip="When enabled, breakouts only trigger when more than 50% of the candle body is outside the channel. This reduces false signals from wicks. When disabled, any price movement outside the channel triggers a breakout."),
    green=input.color(color.new('#00FFBB'), title="Bullish Colour", group="Appearance", tooltip="Color used for bullish visuals and positive sentiment texts."),
    red=input.color(color.new('#FF1100'), title="Bearish Colour", group="Appearance", tooltip="Color used for bearish visuals and negative sentiment texts.")
):
    overlap: bool = False
    res: int = 20
    scale__ren__: int = 30

    lowestLow = ta.lowest(low, length_)
    highestHigh = ta.highest(high, length_)
    normalizedPrice = (close - lowestLow) / (highestHigh - lowestLow)
    vol = ta.stdev(normalizedPrice, 14)

    boxes: Persistent[list[Box]] = array.new_box()
    boxes_u: Persistent[list[Box]] = array.new_box()
    boxes_l: Persistent[list[Box]] = array.new_box()
    centerLines: Persistent[list[Line]] = array.new_line()
    sentiments: Persistent[list[Box]] = array.new_box()

    upperTopLines: Persistent[list[Line]] = array.new_line()
    upperBottomLines: Persistent[list[Line]] = array.new_line()
    lowerTopLines: Persistent[list[Line]] = array.new_line()
    lowerBottomLines: Persistent[list[Line]] = array.new_line()

    def f_can_create(tNew: float, bNew: float):
        ok: bool = True
        if array.size(boxes) > 0:
            for j in pine_range(0, array.size(boxes) - 1):
                if tNew > method_call('get_bottom', array.get(boxes, j)) and bNew < method_call('get_top', array.get(boxes, j)):
                    ok = False
                    break
        return ok

    def profileCalculation(start_index, end_index, res, scale__ren__, top_truncation, bottom_truncation):
        top_boundaries: list[float] = array.new_float(res)
        bottom_boundaries: list[float] = array.new_float(res)
        binlen: list[float] = array.new_float(res)
        bintype: list[float] = array.new_float(res)
        highs: list[float] = array.new_float()
        lows: list[float] = array.new_float()
        volumes: list[float] = array.new_float()
        dirs: list[int] = array.new_int()

        for i in pine_range(bar_index - start_index, bar_index - end_index):
            array.push(highs, high[i])
            array.push(lows, low[i])
            array.push(volumes, volume[i])
            array.push(dirs, 1 if close[i] > open[i] else -1)

        maxx = array.max(highs)
        minn = array.min(lows)
        size__ren__ = array.size(highs)

        poc: float = 0.0

        if not na(top_truncation):
            maxx = math.min(maxx, top_truncation)
        if not na(bottom_truncation):
            minn = math.max(minn, bottom_truncation)

        if size__ren__ > 0 and maxx > minn:
            step = (maxx - minn) / res
            granularity = res
            for i in pine_range(0, granularity - 1):
                bin_size: float = 0.0
                bin_signed: float = 0.0
                bottom = minn + i * step
                top = minn + (i + 1) * step
                array.insert(bottom_boundaries, i, bottom)
                array.insert(top_boundaries, i, top)
                for j in pine_range(0, array.size(highs) - 1):
                    candle_above_hbar = array.get(lows, j) > top
                    candle_below_hbar = array.get(highs, j) < bottom
                    is_candle_in_bucket = not (candle_above_hbar or candle_below_hbar)
                    if is_candle_in_bucket:
                        v = array.get(volumes, j)
                        bin_size += v
                        bin_signed += v * array.get(dirs, j)
                array.insert(binlen, i, bin_size)
                array.insert(bintype, i, bin_signed)
            boc = array.max(binlen)
            boci = array.indexof(binlen, boc) if array.indexof(binlen, boc) > 0 else 0
            poc = math.avg(array.get(top_boundaries, boci), array.get(bottom_boundaries, boci))

        return (top_boundaries, bottom_boundaries, binlen, bintype, poc)

    upper = vol
    lower = ta.wma(vol, length)

    duration = math.max(nz(ta.barssince(ta.crossover(lower, upper))), 1)
    h = ta.highest(duration)
    l = ta.lowest(duration)

    vola = ta.atr(length) / 2

    newChannel: bool = False

    if ta.crossover(upper, lower) and duration > 10:
        if overlap or f_can_create(h, l):
            array.unshift(boxes, box.new(bar_index - duration, h, bar_index, l, bgcolor=color.new(chart.fg_color, 90), border_color=na))
            array.unshift(boxes_u, box.new(bar_index - duration, h, bar_index, h - vola, bgcolor=color.new(red, 70), border_color=na))
            array.unshift(boxes_l, box.new(bar_index - duration, l + vola, bar_index, l, bgcolor=color.new(green, 70), border_color=na))
            start_index = method_call('get_left', array.first(boxes))
            end_index = bar_index
            top_boundaries, bottom_boundaries, binlen, bintype, poc = profileCalculation(start_index, end_index, res, scale__ren__, method_call('get_top', array.first(boxes)), method_call('get_bottom', array.first(boxes)))
            for i_ in pine_range(0, res - 1):
                box_right = method_call('get_left', array.first(boxes))
                box_left = cast_int(box_right - (method_call('get_right', array.first(boxes)) - box_right) * 0.15)
                box_top = array.get(top_boundaries, i_)
                box_bottom = array.get(bottom_boundaries, i_)
                gradient_color = color.from_gradient(method_call('get', binlen, i_), 0, method_call('max', binlen), color.new(green, 90), green) if method_call('get', bintype, i_) > 0 else color.from_gradient(method_call('get', binlen, i_), 0, method_call('max', binlen), color.new(red, 90), red)
                array.push(sentiments, box.new(box_left, box_top, box_right, box_bottom, border_style=line.style_solid, border_color=gradient_color, border_width=1, bgcolor=gradient_color, text_size=size.auto))

            centerY: float = (h + l) / 2
            array.unshift(centerLines, line.new(bar_index - duration, centerY, bar_index, centerY, color=color.new(chart.fg_color, 50), width=1, style=line.style_dashed))

            array.unshift(upperTopLines, line.new(bar_index - duration, h, bar_index, h, color=color.new(red, 0), width=2))
            array.unshift(upperBottomLines, line.new(bar_index - duration, h - vola, bar_index, h - vola, color=color.new(red, 20), width=1, style=line.style_dotted))
            array.unshift(lowerTopLines, line.new(bar_index - duration, l + vola, bar_index, l + vola, color=color.new(green, 20), width=1, style=line.style_dotted))
            array.unshift(lowerBottomLines, line.new(bar_index - duration, l, bar_index, l, color=color.new(green, 0), width=2))
            curIdx = NA(int)
            if array.size(top_boundaries) > 0 and array.size(bottom_boundaries) > 0 and (array.size(bintype) > 0):
                for ii in pine_range(0, res - 1):
                    bb = array.get(bottom_boundaries, ii)
                    tb = array.get(top_boundaries, ii)
                    if close >= bb and close <= tb:
                        curIdx = ii
                        break
            if not na(curIdx):
                maxAbsBt = math.max(math.abs(method_call('max', bintype)), math.abs(method_call('min', bintype)))
                curBt = method_call('get', bintype, curIdx)
                sentimentText = 'Current Sentiment: ' + string.tostring(curBt / maxAbsBt * 100) + '%'
                channelSum: float = 0.0
                if array.size(bintype) > 0:
                    for jj in pine_range(0, res - 1):
                        channelSum += method_call('get', bintype, jj)
                channelText = 'Overall Sentiment: ' + ('Bullish' if channelSum > 0 else 'Bearish')
                if close > centerY:
                    method_call('set_text', array.first(boxes_l), sentimentText)
                    method_call('set_text_color', array.first(boxes_l), green if curBt >= 0 else red)
                    method_call('set_text', array.first(boxes_u), channelText)
                    method_call('set_text_color', array.first(boxes_u), chart.fg_color)
                else:
                    method_call('set_text', array.first(boxes_u), sentimentText)
                    method_call('set_text_color', array.first(boxes_u), green if curBt >= 0 else red)
                    method_call('set_text', array.first(boxes_l), channelText)
                    method_call('set_text_color', array.first(boxes_l), chart.fg_color)
            newChannel = True

    boxes_: Persistent[list[Box]] = array.new_box()

    while array.size(boxes_) > 0:
        method_call('delete', array.shift(boxes_))

    channelBreak: bool = False
    channelBreak_: bool = False

    if array.size(boxes) > 0:
        __loop_1__ = pine_loop(0)
        while __loop_1__.step(array.size(boxes) - 1):
            i = __loop_1__.value
            priceToCompare: float = math.avg(close, open) if strong else close
            if priceToCompare > method_call('get_top', array.get(boxes, i)):
                array.remove(boxes, i)
                array.remove(boxes_u, i)
                array.remove(boxes_l, i)
                array.remove(centerLines, i)
                array.remove(upperTopLines, i)
                array.remove(upperBottomLines, i)
                array.remove(lowerTopLines, i)
                array.remove(lowerBottomLines, i)
                array.clear(sentiments)
                channelBreak = True
            elif priceToCompare < method_call('get_bottom', array.get(boxes, i)):
                array.remove(boxes, i)
                array.remove(boxes_u, i)
                array.remove(boxes_l, i)
                array.remove(centerLines, i)
                array.remove(upperTopLines, i)
                array.remove(upperBottomLines, i)
                array.remove(lowerTopLines, i)
                array.remove(lowerBottomLines, i)
                array.clear(sentiments)
                channelBreak_ = True
            else:
                method_call('set_right', array.get(boxes, i), bar_index)
                method_call('set_right', array.get(boxes_u, i), bar_index)
                method_call('set_right', array.get(boxes_l, i), bar_index)
                method_call('set_x2', array.get(centerLines, i), bar_index)
                method_call('set_x2', array.get(upperTopLines, i), bar_index)
                method_call('set_x2', array.get(upperBottomLines, i), bar_index)
                method_call('set_x2', array.get(lowerTopLines, i), bar_index)
                method_call('set_x2', array.get(lowerBottomLines, i), bar_index)
                start_index = method_call('get_left', array.get(boxes, i))
                end_index = bar_index

                top_boundaries, bottom_boundaries, binlen, bintype, poc = profileCalculation(start_index, end_index, res, scale__ren__, method_call('get_top', array.get(boxes, i)), method_call('get_bottom', array.get(boxes, i)))
                max_abs_bt = math.max(math.abs(method_call('max', bintype)), math.abs(method_call('min', bintype)))
                for i_ in pine_range(0, res - 1):
                    box_right = bar_index + 7 + scale__ren__
                    box_left = box_right - math.round(method_call('get', binlen, i_)) / math.round(method_call('max', binlen)) * scale__ren__
                    box_top = array.get(top_boundaries, i_)
                    box_bottom = array.get(bottom_boundaries, i_)
                    gradient_color = color.from_gradient(method_call('get', binlen, i_), 0, method_call('max', binlen), color.new(green, 90), green) if method_call('get', bintype, i_) > 0 else color.from_gradient(method_call('get', binlen, i_), 0, method_call('max', binlen), color.new(red, 90), red)
                    array.push(boxes_, box.new(box_left, box_top, box_right, box_bottom, border_style=line.style_solid, border_color=gradient_color, border_width=1, bgcolor=gradient_color))
                    cLeft = method_call('get_left', array.get(boxes, i))
                    cRight = method_call('get_right', array.get(boxes, i))
                    method_call('set_left', array.get(sentiments, i_), cast_int(cLeft - (cRight - cLeft) * 0.15))
                    signed_v = method_call('get', bintype, i_)
                    mag = math.abs(signed_v)
                    ratio = mag / max_abs_bt if max_abs_bt > 0 else 0.0
                    tr = cast_int(100 - math.round(ratio * 100))
                    colBase = green if signed_v > 0 else red
                    col = color.from_gradient(tr, 0, 100, colBase, chart.bg_color)
                    method_call('set_bgcolor', array.get(sentiments, i_), col)
                    method_call('set_border_color', array.get(sentiments, i_), col)
                    method_call('set_text', array.get(sentiments, i_), string.tostring(100 * math.abs(signed_v) / math.abs(method_call('max', bintype)), format.percent))
                    if i_ == res - 1:
                        method_call('set_x1', array.get(centerLines, i), cast_int(cLeft - (cRight - cLeft) * 0.15))
                        method_call('set_x1', array.get(upperTopLines, i), cast_int(cLeft - (cRight - cLeft) * 0.15))
                        method_call('set_x1', array.get(upperBottomLines, i), cast_int(cLeft - (cRight - cLeft) * 0.15))
                        method_call('set_x1', array.get(lowerTopLines, i), cast_int(cLeft - (cRight - cLeft) * 0.15))
                        method_call('set_x1', array.get(lowerBottomLines, i), cast_int(cLeft - (cRight - cLeft) * 0.15))

                curIdx_ = NA(int)
                if array.size(top_boundaries) > 0 and array.size(bottom_boundaries) > 0 and (array.size(bintype) > 0):
                    for kk in pine_range(0, res - 1):
                        bb_ = array.get(bottom_boundaries, kk)
                        tb_ = array.get(top_boundaries, kk)
                        if close >= bb_ and close <= tb_:
                            curIdx_ = kk
                            break
                if not na(curIdx_):
                    maxAbsBt_ = math.max(math.abs(method_call('max', bintype)), math.abs(method_call('min', bintype)))
                    curBt_ = method_call('get', bintype, curIdx_)
                    sentimentText_ = 'Current Sentiment: ' + string.tostring(curBt_ / maxAbsBt_ * 100, format.percent) + '%'
                    channelSum_: float = 0.0
                    if array.size(bintype) > 0:
                        for mm in pine_range(0, res - 1):
                            channelSum_ += method_call('get', bintype, mm)
                    channelText_ = 'Overall Sentiment: ' + ('Bullish' if channelSum_ > 0 else 'Bearish')
                    centerY_ = (method_call('get_top', array.get(boxes, i)) + method_call('get_bottom', array.get(boxes, i))) / 2.0
                    if close > centerY_:
                        method_call('set_text', array.get(boxes_l, i), sentimentText_)
                        method_call('set_text_color', array.get(boxes_l, i), green if curBt_ >= 0 else red)
                        method_call('set_text', array.get(boxes_u, i), channelText_)
                        method_call('set_text_color', array.get(boxes_u, i), chart.fg_color)
                    else:
                        method_call('set_text', array.get(boxes_u, i), sentimentText_)
                        method_call('set_text_color', array.get(boxes_u, i), green if curBt_ >= 0 else red)
                        method_call('set_text', array.get(boxes_l, i), channelText_)
                        method_call('set_text_color', array.get(boxes_l, i), chart.fg_color)

    midp = math.avg(close, open)
    mid = plot(midp, display=display.none)

    trnd_up = ta.sma(low, math.max(nz(ta.barssince(channelBreak), 0), 1))
    activeUp: Persistent[bool] = False

    if channelBreak:
        activeUp = True

    if activeUp and ta.crossunder(close, trnd_up):
        activeUp = False

    b1 = plot(trnd_up if activeUp else na, 'Bullish Trend', color=green, style=plot.style_linebr)

    trnd_dn = ta.sma(high, math.max(nz(ta.barssince(channelBreak_), 0), 1))
    activeDn: Persistent[bool] = False

    if channelBreak_:
        activeDn = True

    if activeDn and ta.crossover(close, trnd_dn):
        activeDn = False

    b2 = plot(trnd_dn if activeDn else na, 'Bearish Trend', color=red, style=plot.style_linebr)

    fill(mid, b1, midp, trnd_up, color.new(chart.bg_color, 70), color.new(green, 70), 'Bullish Fill')
    fill(mid, b2, trnd_dn, midp, color.new(red, 70), color.new(chart.bg_color, 70), 'Bearish Fill')

    plotchar(math.min(low, low[1], low[2]) if channelBreak else na, 'Bullish Breakout', '▲', location.absolute, green, size=size.tiny)
    plotchar(math.max(high, high[1], high[2]) if channelBreak_ else na, 'Bearish Breakout', '▼', location.absolute, red, size=size.tiny)

    alertcondition(newChannel, 'Channel Formed', 'A new channel has formed.')
    alertcondition(channelBreak, 'Bullish Channel Break', 'Price broke above the channel.')
    alertcondition(channelBreak_, 'Bearish Channel Break', 'Price broke below the channel.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
