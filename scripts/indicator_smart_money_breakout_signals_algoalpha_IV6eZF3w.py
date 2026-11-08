"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barcolor, barstate, chart,
    close, color, high, input, label, line, linefill, location, low, math, na, nz, plotshape,
    position, script, shape, size, string, ta, table, text
)
from pynecore.types import Color, Line, Persistent, PersistentSeries, Series, Table


@script.indicator("Smart Money Breakout Signals [AlgoAlpha]", shorttitle="AlgoAlpha - Smart Money Breakout", overlay=True)
def main(
    swingSize=input.int(25, "Market Structure Time-Horizon", tooltip='Defines the number of candles used to determine market structure. Larger values smooth out market structure changes but may delay signals.', group="Inputs"),
    bosConfType=input.string('Candle Close', 'BOS Confirmation Type', options=('Candle Close', 'Wicks'), tooltip='Specifies whether a candle close or a wick surpassing the previous swing point is used to confirm a Break of Structure (BOS).', group="Inputs"),
    choch=input.bool(True, 'Show CHoCH', tooltip='Enables or disables the display of Change of Character (CHoCH) labels, highlighting the first structural break against the trend.', group="Inputs"),
    BULL: Series[Color] = input.color(color.new('#00FFBB'), "Bullish Color", group="Visualization", tooltip='Sets the color used to represent bullish signals and breakout lines.'),
    BEAR: Series[Color] = input.color(color.new('#FF1100'), "Bearish Color", group="Visualization", tooltip='Sets the color used to represent bearish signals and breakout lines.')
):
    def MS(swingSize: int, src_BI: int, bosConfType: str, enms: bool, src_close: float, src_high: float, src_low: float):
        pivHi = ta.pivothigh(src_high, swingSize, swingSize)
        pivLo = ta.pivotlow(src_low, swingSize, swingSize)
        prevHigh: Persistent[float] = na(float)
        prevLow: Persistent[float] = na(float)
        prevHighIndex: Persistent[int] = na(int)
        prevLowIndex: Persistent[int] = na(int)
        highActive: Persistent[bool] = False
        lowActive: Persistent[bool] = False
        hh: bool = False
        lh: bool = False
        hl: bool = False
        ll: bool = False
        prevSwing: Persistent[int] = 0
        if not na(pivHi) and enms:
            if pivHi >= prevHigh:
                hh = True
                prevSwing = 2
            else:
                lh = True
                prevSwing = 1
            prevHigh = pivHi
            highActive = True
            prevHighIndex = src_BI - swingSize
        if not na(pivLo) and enms:
            if pivLo >= prevLow:
                hl = True
                prevSwing = -1
            else:
                ll = True
                prevSwing = -2
            prevLow = pivLo
            lowActive = True
            prevLowIndex = src_BI - swingSize
        highBroken: bool = False
        lowBroken: bool = False
        highSrc: float = src_close if bosConfType == 'Candle Close' else src_high
        lowSrc: float = src_close if bosConfType == 'Candle Close' else src_low
        if highSrc > prevHigh and highActive and enms:
            highBroken = True
            highActive = False
        if lowSrc < prevLow and lowActive and enms:
            lowBroken = True
            lowActive = False
        return (hh, ll, lh, hl, highBroken, lowBroken, prevHighIndex, prevLowIndex, pivHi, pivLo, prevHigh, prevLow)

    hh, ll, lh, hl, highBroken, lowBroken, prevHighIndex, prevLowIndex, pivHi, pivLo, prevHigh, prevLow = MS(swingSize, bar_index, bosConfType, True, close, high, low)

    prevBreakoutDir: Persistent[int] = 0
    length: int = 0

    if highBroken:
        line.new(prevHighIndex, prevHigh, bar_index, prevHigh, color=BULL, width=1, force_overlay=True)
        label.new(math.floor(bar_index - (bar_index - prevHighIndex) / 2), prevHigh, 'CHoCH' if prevBreakoutDir == -1 and choch else 'BOS', color=color.rgb(0, 0, 0, 100), textcolor=BULL, size=size.tiny, force_overlay=True)
        alert('Bullish Breakout Detected', alert.freq_once_per_bar)
        prevBreakoutDir = 1
        length = bar_index - prevHighIndex
    if lowBroken:
        line.new(prevLowIndex, prevLow, bar_index, prevLow, color=BEAR, width=1, force_overlay=True)
        label.new(math.floor(bar_index - (bar_index - prevLowIndex) / 2), prevLow, 'CHoCH' if prevBreakoutDir == 1 and choch else 'BOS', color=color.rgb(0, 0, 0, 100), textcolor=BEAR, style=label.style_label_up, size=size.tiny, force_overlay=True)
        alert('Bearish Breakout Detected', alert.freq_once_per_bar)
        prevBreakoutDir = -1
        length = bar_index - prevLowIndex

    x = math.max(1, nz(length))
    v = ta.highest(x) - ta.lowest(x)
    dist = v / 3
    trigger: Series[int] = 0
    RR: int = 1
    active: PersistentSeries[int] = 0
    active1: Persistent[int] = 0
    active2: Persistent[int] = 0
    TP: Persistent[float] = 0.0
    TP1: Persistent[float] = 0.0
    TP2: Persistent[float] = 0.0
    SL: Persistent[float] = 0.0
    TPs: Persistent[list[Line]] = array.new_line()
    TPs1: Persistent[list[Line]] = array.new_line()
    TPs2: Persistent[list[Line]] = array.new_line()

    total: Persistent[int] = 0
    tp1s: Persistent[int] = 0
    tp2s: Persistent[int] = 0
    tp3s: Persistent[int] = 0

    if highBroken:
        active = 1
        active1 = 1
        active2 = 1
        trigger = 1
        total += 1
        TP = prevHigh + dist
        TP1 = prevHigh + dist * 2 / 3
        TP2 = prevHigh + dist * 1 / 3
        SL = prevHigh - dist / RR
        array.unshift(TPs, line.new(prevHighIndex, TP, bar_index, TP, color=color.new(BULL, 70), width=1, force_overlay=True, style=line.style_dashed))
        array.unshift(TPs1, line.new(prevHighIndex, TP1, bar_index, TP1, color=color.new(BULL, 50), width=1, force_overlay=True, style=line.style_dashed))
        array.unshift(TPs2, line.new(prevHighIndex, TP2, bar_index, TP2, color=color.new(BULL, 30), width=1, force_overlay=True, style=line.style_dashed))
        linefill.new(array.first(TPs), array.first(TPs1), color.new(BULL, 90))

    if lowBroken:
        active = -1
        active1 = -1
        active2 = -1
        trigger = 1
        total += 1
        TP = prevLow - dist
        TP1 = prevLow - dist * 2 / 3
        TP2 = prevLow - dist * 1 / 3
        SL = prevLow + dist / RR
        array.unshift(TPs, line.new(prevLowIndex, TP, bar_index, TP, color=color.new(BEAR, 70), width=1, force_overlay=True, style=line.style_dashed))
        array.unshift(TPs1, line.new(prevLowIndex, TP1, bar_index, TP1, color=color.new(BEAR, 50), width=1, force_overlay=True, style=line.style_dashed))
        array.unshift(TPs2, line.new(prevLowIndex, TP2, bar_index, TP2, color=color.new(BEAR, 30), width=1, force_overlay=True, style=line.style_dashed))
        linefill.new(array.first(TPs), array.first(TPs1), color.new(BEAR, 90))

    if active == 1 and high > TP:
        tp1s += 1
    if active1 == 1 and high > TP1:
        tp2s += 1
        active1 = 0
    if active2 == 1 and high > TP2:
        tp3s += 1
        active2 = 0

    if active == -1 and low < TP:
        tp1s += 1
    if active1 == -1 and low < TP1:
        tp2s += 1
        active1 = 0
    if active2 == -1 and low < TP2:
        tp3s += 1
        active2 = 0

    if (active == 1 and high > TP or (active == 1 and low < SL) or (active == -1 and low < TP) or (active == -1 and high > SL)) and (not (trigger != 0 and trigger[1] == 0)):
        active = 0

    if array.size(TPs) > 0:
        if active == 0 or (active != 0 and active[1] != 0 and (trigger == 1)):
            array.remove(TPs, math.min(1, array.size(TPs) - 1))
        else:
            method_call('set_x2', array.first(TPs), bar_index)

    if array.size(TPs1) > 0:
        if active == 0 or (active != 0 and active[1] != 0 and (trigger == 1)):
            array.remove(TPs1, math.min(1, array.size(TPs1) - 1))
        else:
            method_call('set_x2', array.first(TPs1), bar_index)

    if array.size(TPs2) > 0:
        if active == 0 or (active != 0 and active[1] != 0 and (trigger == 1)):
            array.remove(TPs2, math.min(1, array.size(TPs2) - 1))
        else:
            method_call('set_x2', array.first(TPs2), bar_index)

    barcolor(color.new(color.gray, 40) if active == 0 else color.new(BULL[1], 40) if active == 1 else color.new(BEAR[1], 40))

    plotshape(highBroken, 'Bullish Signal', shape.labelup, location.belowbar, BULL, size=size.small)
    plotshape(lowBroken, 'Bearish Signal', shape.labeldown, location.abovebar, BEAR, size=size.small)

    if barstate.islast:
        data_table: Persistent[Table] = table.new(position=position.top_right, columns=2, rows=5, bgcolor=chart.bg_color, border_width=1, border_color=chart.fg_color, frame_color=chart.fg_color, frame_width=1)

        t1_rate = tp1s / total * 100.0 if total > 0 else na
        t2_rate = tp2s / total * 100.0 if total > 0 else na
        t3_rate = tp3s / total * 100.0 if total > 0 else na

        table.cell(data_table, column=0, row=0, text='Smart Money Breakout Stats', text_size=size.tiny, text_color=chart.fg_color, text_halign=text.align_center)
        table.cell(data_table, column=1, row=0, text='Value', text_size=size.tiny, text_color=chart.fg_color, text_halign=text.align_center)

        table.cell(data_table, column=0, row=1, text='Total Signals', text_size=size.tiny, text_color=chart.fg_color)
        table.cell(data_table, column=1, row=1, text=string.tostring(total), text_size=size.tiny, text_color=chart.fg_color, text_halign=text.align_center)

        table.cell(data_table, column=0, row=2, text='TP1 Win Rate', text_size=size.tiny, text_color=chart.fg_color)
        table.cell(data_table, column=1, row=2, text=string.format('{0,number,#.##}%', t3_rate) if total > 0 else 'No Trades', text_size=size.tiny, text_color=chart.fg_color, text_halign=text.align_center)

        table.cell(data_table, column=0, row=3, text='TP2 Win Rate', text_size=size.tiny, text_color=chart.fg_color)
        table.cell(data_table, column=1, row=3, text=string.format('{0,number,#.##}%', t2_rate) if total > 0 else 'No Trades', text_size=size.tiny, text_color=chart.fg_color, text_halign=text.align_center)

        table.cell(data_table, column=0, row=4, text='TP3 Win Rate', text_size=size.tiny, text_color=chart.fg_color)
        table.cell(data_table, column=1, row=4, text=string.format('{0,number,#.##}%', t1_rate) if total > 0 else 'No Trades', text_size=size.tiny, text_color=chart.fg_color, text_halign=text.align_center)

    alertcondition(highBroken, 'Bullish Signal')
    alertcondition(lowBroken, 'Bearish Signal')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
