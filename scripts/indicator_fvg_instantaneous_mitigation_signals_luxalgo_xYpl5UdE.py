"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barcolor, box, close, color, high, input, label, line, low,
    math, na, nz, plot, script, size, ta
)
from pynecore.types import Box, Color, Line, NA, Persistent, PersistentSeries


@script.indicator('FVG Instantaneous Mitigation Signals [LuxAlgo]', 'LuxAlgo - FVG Instantaneous Mitigation Signals', overlay=True, max_boxes_count=500, max_lines_count=500, max_labels_count=500)
def main(
    filterWidth=input.float(0.0, 'FVG Width Filter', minval=0, step=0.1),
    showTp=input(False, 'TP Area', inline='tp', group='TP/SL'),
    tpMult=input.float(4.0, 'Multiplier', minval=0, inline='tp', group='TP/SL'),
    tpCss=input(color.new(color.new('#5B9CF6'), 80), '', inline='tp', group='TP/SL'),
    showSl=input(False, 'SL Area', inline='sl', group='TP/SL'),
    slMult=input.float(2.0, 'Multiplier', minval=0, inline='sl', group='TP/SL'),
    slCss=input(color.new(color.gray, 80), '', inline='sl', group='TP/SL'),
    tsReset=input.string('Every Signals', 'Reset Trailing Stop', options=('Every Signals', 'Inverse Signals'), group='Trailing Stop'),
    tsMult=input(3.0, 'Multiplier', group='Trailing Stop'),
    showBull=input(True, 'Bullish IMFVG', inline='bull', group='Style'),
    bullCss=input(color.teal, '', inline='bull', group='Style'),
    bullAvg=input(True, 'Average', inline='bull', group='Style'),
    showBear=input(True, 'Bearish IMFVG', inline='bear', group='Style'),
    bearCss=input(color.new('#F23645'), '', inline='bear', group='Style'),
    bearAvg=input(True, 'Average', inline='bear', group='Style')
):
    n = bar_index
    atr = nz(ta.atr(200))
    def tpsl(condition, opposite_condition, level, islong):
        tp_area: Persistent[Box] = na(Box)
        sl_area: Persistent[Box] = na(Box)
        reached: Persistent[bool] = False
        if condition:
            if islong:
                if showTp:
                    tp_area = box.new(n, level + atr * tpMult, n, level, na, bgcolor=tpCss)
                if showSl:
                    sl_area = box.new(n, level, n, level - atr * slMult, na, bgcolor=slCss)
            else:
                if showTp:
                    tp_area = box.new(n, level, n, level - atr * tpMult, na, bgcolor=tpCss)
                if showSl:
                    sl_area = box.new(n, level + atr * slMult, n, level, na, bgcolor=slCss)
            reached = False
        elif opposite_condition:
            reached = True
        if not reached:
            box.set_right(tp_area, n)
            box.set_right(sl_area, n)
            if islong:
                if high > box.get_top(tp_area) or low < box.get_bottom(sl_area):
                    reached = True
            else:
                if low < box.get_bottom(tp_area) or high > box.get_top(sl_area):
                    reached = True
        return reached

    def trailing_stop(trigger, trend, mult):
        ts: Persistent[float] = na(float)
        reached: Persistent[bool] = False
        if trigger:
            __block_result__ = na
            __switch_1__ = trend
            if __switch_1__ == 1:
                __block_result__ = close - atr * mult
            elif __switch_1__ == 0:
                __block_result__ = close + atr * mult
            ts = __block_result__
            reached = False
        else:
            __block_result_1__ = na
            __switch_1__ = trend
            if __switch_1__ == 1:
                __block_result_1__ = close - atr * mult if close - ts > atr * mult else ts
            elif __switch_1__ == 0:
                __block_result_1__ = close + atr * mult if ts - close > atr * mult else ts
            ts = __block_result_1__
            if close < ts and trend == 1:
                reached = True
            elif close > ts and trend == 0:
                reached = True
        return (ts, reached)

    def filter(a, b):
        return a - b > atr * filterWidth

    bull_line: Persistent[Line] = na(Line)
    bull_lvl_reached: Persistent[bool] = na(bool)
    bear_line: Persistent[Line] = na(Line)
    bear_lvl_reached: Persistent[bool] = na(bool)
    os: PersistentSeries[int] = 0
    filter_1 = filter(low[3], high[1])
    bull = low[3] > high[1] and close[2] < low[3] and (close > low[3]) and filter_1 and showBull
    if bull:
        box.new(n - 3, low[3], n, high[1], na, bgcolor=color.new(bullCss, 50))
        avg = math.avg(low[3], high[1])
        if bullAvg:
            bull_line = line.new(n, avg, n, avg, color=bullCss, style=line.style_dashed)
        label.new(n, low, '▲', color=NA(Color), textcolor=bullCss, style=label.style_label_up, size=size.small)
        os = 1
        bull_lvl_reached = False
    filter_2 = filter(low[1], high[3])
    bear = low[1] > high[3] and close[2] > high[3] and (close < high[3]) and filter_2 and showBear
    if bear:
        box.new(n - 3, low[1], n, high[3], na, bgcolor=color.new(bearCss, 50))
        avg = math.avg(low[1], high[3])
        if bearAvg:
            bear_line = line.new(n, avg, n, avg, color=bearCss, style=line.style_dashed)
        label.new(n, high, '▼', color=NA(Color), textcolor=bearCss, style=label.style_label_down, size=size.small)
        os = 0
        bear_lvl_reached = False
    if not bull_lvl_reached:
        line.set_x2(bull_line, n)
    if not bear_lvl_reached:
        line.set_x2(bear_line, n)
    if close < line.get_y2(bull_line):
        bull_lvl_reached = True
    if close > line.get_y2(bear_line):
        bear_lvl_reached = True
    bull_reached = tpsl(bull, bear, math.avg(low[3], high[1]), True)
    bear_reached = tpsl(bear, bull, math.avg(low[1], high[3]), False)
    ts_reset = bull or bear if tsReset == 'Every Signals' else os != os[1]
    ts, ts_reached = trailing_stop(ts_reset, os, tsMult)
    barcolor(na if ts_reached else bullCss if os == 1 and (not bull_reached) else bearCss if os == 0 and (not bear_reached) else na)
    plot(ts, 'Trailing Stop', na if ts_reached or bull or bear else bullCss if os else bearCss)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
