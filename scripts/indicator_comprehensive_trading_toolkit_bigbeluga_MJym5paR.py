"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    array, bar_index, box, chart, close, color, display, extend, fill, high,
    hline, input, line, low, na, plot, script, ta
)
from pynecore.types import Box, Color, Line, NA, Persistent, Series


@script.indicator("Trading Toolkit (Michaël van de Poppe) [BigBeluga]", overlay=False, max_boxes_count=500, max_bars_back=500)
def main(
    show_sr=input.bool(True, "", group="Support & Resistance", inline="sr"),
    len=input.int(30, "Support/Resistance", group="Support & Resistance", inline="sr"),
    bul_col=input.color(color.rgb(0, 230, 119, 70), "", inline="sr"),
    ber_col=input.color(color.rgb(255, 82, 82, 70), "", inline="sr"),
    length=input.int(24, "RSI", group="Rsi", inline="lvl"),
    overs=input.int(30, "OS/OB", group="Rsi", inline="lvl"),
    overb=input.int(70, "", group="Rsi", inline="lvl"),
    show_div=input.bool(False, "", inline="div"),
    div_len=input.int(10, "Divergence", inline="div"),
    bull_col=input.color(color.rgb(0, 230, 211, 20), "", inline="div"),
    bear_col=input.color(color.rgb(255, 82, 82, 20), "", inline="div"),
    show_cor=input.bool(False, "", group="correction", inline="cor"),
    correction__global__=input.int(5, "Correction %", group="correction", inline="cor"),
    corr_col=input.color(color.new('#2195F32D'), "", group="correction", inline="cor")
):
    m_col: Color = chart.fg_color
    noneColor: Color = color.new(color.white, 100)

    rsi: Series[float] = ta.rsi(close, length)

    lookbackRight: int = div_len
    lookbackLeft: int = div_len
    rangeUpper: int = 60
    rangeLower: int = 5

    def _inRange(cond: bool):
        bars = ta.barssince(cond)
        return rangeLower <= bars and bars <= rangeUpper

    def rsi_divergence():
        __hist_rsi__: Series[float] = rsi[0]
        plFound: Series[bool] = False
        phFound: Series[bool] = False

        bullCond: bool = False
        bearCond: bool = False

        rsiLBR = __hist_rsi__[lookbackRight]

        pl_p = ta.pivotlow(low, lookbackLeft, lookbackRight)
        ph_p = ta.pivothigh(high, lookbackLeft, lookbackRight)

        inrangepl = _inRange(plFound[1])
        inrangeph = _inRange(phFound[1])

        pl = ta.pivotlow(rsi, lookbackLeft, lookbackRight)
        plFound = not na(pl)
        rsiHL = rsiLBR > ta.valuewhen(plFound, rsiLBR, 1) and inrangepl

        lowLBR = low[lookbackRight]
        priceLL = lowLBR < ta.valuewhen(plFound, lowLBR, 1)
        bullCond = priceLL and rsiHL and plFound

        ph = ta.pivothigh(rsi, lookbackLeft, lookbackRight)
        phFound = not na(ph)
        rsiLH = rsiLBR < ta.valuewhen(phFound, rsiLBR, 1) and inrangeph

        highLBR = high[lookbackRight]
        priceHH = highLBR > ta.valuewhen(phFound, highLBR, 1)
        bearCond = priceHH and rsiLH and phFound

        return (pl_p, ph_p, bearCond, bullCond, plFound, phFound, rsiLBR)

    def correction(correction__00000041__):
        boxes: Persistent[list[Box]] = array.new_box()
        roc = ta.roc(close, 15)
        roc_indx: Persistent = NA(int)
        roc_src: Persistent = NA(float)

        if ta.cross(roc, 0):
            roc_indx = bar_index
            roc_src = high

        if ta.crossunder(roc, -correction__00000041__):
            array.push(boxes, box.new(roc_indx, roc_src, bar_index + 1, low, na, 0, bgcolor=corr_col, force_overlay=True))

        __block_result__ = na
        if array.size(boxes) > 1:
            __block_result_1__ = na
            for i in pine_range(0, array.size(boxes) - 1):
                box_id = array.get(boxes, i)
                indx = i + 1 if i < array.size(boxes) - 1 else 0
                box_id_1 = array.get(boxes, indx)

                if method_call('get_left', box_id) == method_call('get_left', box_id_1):
                    box.delete(box_id_1)

                __block_result_2__ = na
                if method_call('get_right', box_id) - method_call('get_left', box_id) >= 10:
                    __block_result_2__ = box.delete(box_id)
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    def norm_candle_size():
        return (high - low) / ta.stdev(high - low, 200)

    def draw_levels():
        PH = ta.pivothigh(len, len)
        PL = ta.pivotlow(len, len)
        Atr = ta.atr(200) * 0.3

        candle_size: Series = norm_candle_size()

        big_candle = candle_size[len] > 1
        style = line.style_solid if candle_size[len] > 1.5 else line.style_dashed

        lines: Persistent[list[Line]] = array.new_line()
        boxes: Persistent[list[Box]] = array.new_box()

        if big_candle:
            if not na(PH):
                array.push(lines, line.new(bar_index - len, PH, bar_index, PH, extend=extend.right, style=style, color=m_col, force_overlay=True))
                array.push(boxes, box.new(bar_index - len, PH + Atr, bar_index + 5, PH - Atr, na, 0, bgcolor=ber_col, force_overlay=True))
            if not na(PL):
                array.push(lines, line.new(bar_index - len, PL, bar_index, PL, extend=extend.right, style=style, color=m_col, force_overlay=True))
                array.push(boxes, box.new(bar_index - len, PL + Atr, bar_index + 5, PL - Atr, na, 0, bgcolor=bul_col, force_overlay=True))

        for line_id in lines:
            level = line.get_y1(line_id)
            box_id = array.get(boxes, array.indexof(lines, line_id))
            method_call('set_right', box_id, bar_index + 10)

            if high[1] > level and high < level:
                box.set_lefttop(box_id, bar_index, level + Atr)
                box.set_rightbottom(box_id, bar_index + 5, level - Atr)
                box.set_bgcolor(box_id, ber_col)

            if low[1] < level and low > level:
                box.set_lefttop(box_id, bar_index, level + Atr)
                box.set_rightbottom(box_id, bar_index + 5, level - Atr)
                box.set_bgcolor(box_id, bul_col)

        __block_result_3__ = na
        if array.size(lines) > 0:
            __block_result_4__ = na
            if array.size(lines) > 6:
                line.delete(array.shift(lines))
                __block_result_4__ = box.delete(array.shift(boxes))
            __block_result_3__ = __block_result_4__
        return __block_result_3__

    if show_sr:
        draw_levels()

    if show_cor:
        correction(correction__global__)

    pl_p, ph_p, bearCond, bullCond, plFound, phFound, rsiLBR = rsi_divergence()

    pr = plot(rsi, color=m_col)
    p7 = plot(overb, display=display.none, editable=False)
    p3 = plot(overs, display=display.none, editable=False)

    h2 = hline(overs, 'Oversold', color=m_col)
    h1 = hline(overb, 'OverBought', color=m_col)
    hline(50, color=color.new(m_col, 50))

    fill(h1, h2, color.new(m_col, 85))
    fill(p3, pr, overs, 20, na, color.red if rsi < overs else na)
    fill(p7, pr, overb, 85, na, color.lime if rsi > overb else na)

    displ_div = display.pane if show_div else display.none
    plot(rsiLBR if plFound else na, offset=-lookbackRight, title='Regular Bullish', linewidth=2, color=bull_col if bullCond else noneColor, display=displ_div)

    plot(rsiLBR if phFound else na, offset=-lookbackRight, title='Regular Bearish', linewidth=2, color=bear_col if bearCond else noneColor, display=displ_div)

    plot(low[lookbackRight] if plFound else na, offset=-lookbackRight, title='Regular Bullish', linewidth=1, color=bull_col if bullCond else noneColor, display=displ_div, force_overlay=True)

    plot(high[lookbackRight] if phFound else na, offset=-lookbackRight, title='Regular Bearish', linewidth=1, color=bear_col if bearCond else noneColor, display=displ_div, force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
