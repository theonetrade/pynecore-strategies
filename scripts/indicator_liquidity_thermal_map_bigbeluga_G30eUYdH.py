"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    array, bar_index, barstate, box, chart, close, color, fill, format, hl2,
    hlc3, input, label, line, linefill, math, na, open, plot, script, string, ta, volume
)
from pynecore.types import Box, Color, Label, Line, Persistent


@script.indicator("Liquidity Thermal Map [BigBeluga]", overlay=True, max_lines_count=500, calc_bars_count=1500)
def main(
    profileType=input.string("Balanced Profile", "Profile Depth", options=("Shallow Profile", "Balanced Profile", "Deep Profile"), tooltip='Controls how much historical data is used to build the liquidity profile.\n\n' + 'Shallow Profile  → Short-term structure\n' + 'Balanced Profile → Medium-term structure\n' + 'Deep Profile     → Broad structural distribution'),
    sensitivityMode=input.string("Balanced", "Thermal Sensitivity", options=("High Contrast", "Balanced", "Smooth"), tooltip='Controls heatmap intensity.\n\n' + 'High Contrast → Strong color separation\n' + 'Balanced      → Default behavior\n' + 'Smooth        → Softer gradient blending'),
    pocCol1=input.color(color.rgb(189, 43, 43), "Upper Liquidity Color", tooltip='Color used for liquidity located above current price.\n' + 'Typically represents overhead resistance zones.'),
    pocCol2=input.color(color.rgb(41, 180, 83), "Lower Liquidity Color", tooltip='Color used for liquidity located below current price.\n' + 'Typically represents structural support zones.'),
    removeCol=input.bool(True, "Hide Active Candle Color", tooltip='Removes heatmap coloring around the active candle\n' + 'to improve real-time price visibility.')
):
    period = 100 if profileType == 'Shallow Profile' else 300 if profileType == 'Balanced Profile' else 600

    min = 0.5 if sensitivityMode == 'High Contrast' else 0.25 if sensitivityMode == 'Balanced' else 0.0

    colorNA: Color = color.new('#44444400')

    H = ta.highest(period)
    L = ta.lowest(period)

    step = (H - L) / 31

    levels: list[float] = array.new_float(31)
    volBins: list[float] = array.new_float(31, 0.0)

    def gradient(volBins, number):
        val = method_call('get', volBins, number) / method_call('max', volBins)
        loww = array.get(levels, number)
        upp = array.get(levels, 29 if number + 1 > 29 else number + 1)

        pocCol = pocCol1 if close <= loww else pocCol2

        if removeCol:
            if open >= loww and open <= upp or (close >= loww and close <= upp) or (hl2 >= loww and hl2 <= upp) or (hlc3 >= loww and hlc3 <= upp):
                pocCol = colorNA

        return color.new(pocCol, 20) if method_call('get', volBins, number) == method_call('max', volBins) else color.from_gradient(val, min, 1, colorNA, color.new(pocCol, 50))

    for i in pine_range(0, 31 - 1):
        ll = L + step * i
        hh = ll + step
        mid = ll + step / 2

        array.set(levels, i, ll)

        for k in pine_range(0, period - 1):
            c = close[k]

            if math.abs(c - mid) < step:
                array.set(volBins, i, array.get(volBins, i) + volume[k])

    if barstate.islast:
        binsCount: int = 31
        lastIdx: int = binsCount - 1
        buyVol: float = 0.0
        sellVol: float = 0.0

        boxes: Persistent[list[Box]] = array.new_box()
        labels: Persistent[list[Label]] = array.new_label()

        for b in boxes:
            box.delete(b)

        array.clear(boxes)

        for l in labels:
            label.delete(l)

        array.clear(labels)

        splitIdx: int = cast_int(math.floor((close - L) / step))
        splitIdx = math.max(0, math.min(lastIdx, splitIdx))

        for i in pine_range(0, lastIdx):
            mid: float = L + step * i + step / 2
            vol: float = array.get(volBins, i)

            if mid < close:
                buyVol += vol
            else:
                sellVol += vol

        totalVol: float = buyVol + sellVol
        buyPct: float = buyVol / totalVol if totalVol > 0 else 0
        sellPct: float = sellVol / totalVol if totalVol > 0 else 0
        imbalance: float = buyVol - sellVol if sellVol > 0 else na

        buyLabel: Label = label.new(bar_index + 40, L + (close - L) / 2, 'BUY LIQ\n' + string.tostring(buyVol, format.volume) + '\n' + string.tostring(buyPct * 100, '#.0') + '%', style=label.style_label_left, textcolor=pocCol2, color=colorNA, tooltip='Liquidity Below Price\n\n' + 'Total Volume Below Current Price:\n' + string.tostring(buyVol, format.volume) + '\n\n' + 'Represents accumulated volume Below Current Price')

        sellLabel: Label = label.new(bar_index + 40, close + (H - close) / 2, 'SELL LIQ\n' + string.tostring(sellVol, format.volume) + '\n' + string.tostring(sellPct * 100, '#.0') + '%', style=label.style_label_left, textcolor=pocCol1, color=colorNA, tooltip='Liquidity Above Price\n\n' + 'Total Volume Above Current Price:\n' + string.tostring(sellVol, format.volume) + '\n\n' + 'Represents accumulated volume Above Current Price')

        ratioLabel: Label = label.new(bar_index + 40, H + step, 'Imbalance: ' + string.tostring(imbalance, format.volume), style=label.style_label_left, textcolor=chart.fg_color, color=colorNA, tooltip='Liquidity Imbalance\n\n' + 'Difference Between Below and Above Liquidity:\n' + string.tostring(imbalance, format.volume) + '\n\n' + 'Positive → More liquidity below price\n' + 'Negative → More liquidity above price.')

        array.push(labels, buyLabel)
        array.push(labels, sellLabel)
        array.push(labels, ratioLabel)

        for i in pine_range(0, lastIdx):
            ll: float = L + step * i
            hh: float = ll + step
            mid: float = ll + step / 2

            vol = array.get(volBins, i)

            baseCol: Color = pocCol2 if close > mid else pocCol1

            dist: int = math.abs(i - splitIdx)

            maxDist: int = math.max(splitIdx, lastIdx - splitIdx)
            fade: float = dist / maxDist if maxDist > 0 else 0.0

            alpha: int = cast_int(10 + fade * 85)
            col: Color = color.new(baseCol, alpha)

            b = box.new(bar_index + 25, hh, bar_index + 35, ll, bgcolor=col, border_color=na)

            if array.get(volBins, i) == array.max(volBins):
                method_call('set_text', b, '>' + string.tostring(array.max(volBins), format.volume) + '<')

                method_call('set_left', b, bar_index + 10)
                method_call('set_bgcolor', b, pocCol2 if close > mid else pocCol1)

            array.push(boxes, b)

    p0 = plot(array.get(levels, 0), color=colorNA, editable=False)
    p1 = plot(array.get(levels, 1), color=colorNA, editable=False)
    p2 = plot(array.get(levels, 2), color=colorNA, editable=False)
    p3 = plot(array.get(levels, 3), color=colorNA, editable=False)
    p4 = plot(array.get(levels, 4), color=colorNA, editable=False)
    p5 = plot(array.get(levels, 5), color=colorNA, editable=False)
    p6 = plot(array.get(levels, 6), color=colorNA, editable=False)
    p7 = plot(array.get(levels, 7), color=colorNA, editable=False)
    p8 = plot(array.get(levels, 8), color=colorNA, editable=False)
    p9 = plot(array.get(levels, 9), color=colorNA, editable=False)
    p10 = plot(array.get(levels, 10), color=colorNA, editable=False)
    p11 = plot(array.get(levels, 11), color=colorNA, editable=False)
    p12 = plot(array.get(levels, 12), color=colorNA, editable=False)
    p13 = plot(array.get(levels, 13), color=colorNA, editable=False)
    p14 = plot(array.get(levels, 14), color=colorNA, editable=False)
    p15 = plot(array.get(levels, 15), color=colorNA, editable=False)
    p16 = plot(array.get(levels, 16), color=colorNA, editable=False)
    p17 = plot(array.get(levels, 17), color=colorNA, editable=False)
    p18 = plot(array.get(levels, 18), color=colorNA, editable=False)
    p19 = plot(array.get(levels, 19), color=colorNA, editable=False)
    p20 = plot(array.get(levels, 20), color=colorNA, editable=False)
    p21 = plot(array.get(levels, 21), color=colorNA, editable=False)
    p22 = plot(array.get(levels, 22), color=colorNA, editable=False)
    p23 = plot(array.get(levels, 23), color=colorNA, editable=False)
    p24 = plot(array.get(levels, 24), color=colorNA, editable=False)
    p25 = plot(array.get(levels, 25), color=colorNA, editable=False)
    p26 = plot(array.get(levels, 26), color=colorNA, editable=False)
    p27 = plot(array.get(levels, 27), color=colorNA, editable=False)
    p28 = plot(array.get(levels, 28), color=colorNA, editable=False)
    p29 = plot(array.get(levels, 29), color=colorNA, editable=False)
    p30 = plot(array.get(levels, 30), color=colorNA, editable=False)

    HH = plot(H, color=colorNA, editable=False)

    col0 = gradient(volBins, 0)
    col1 = gradient(volBins, 1)
    col2 = gradient(volBins, 2)
    col3 = gradient(volBins, 3)
    col4 = gradient(volBins, 4)
    col5 = gradient(volBins, 5)
    col6 = gradient(volBins, 6)
    col7 = gradient(volBins, 7)
    col8 = gradient(volBins, 8)
    col9 = gradient(volBins, 9)
    col10 = gradient(volBins, 10)
    col11 = gradient(volBins, 11)
    col12 = gradient(volBins, 12)
    col13 = gradient(volBins, 13)
    col14 = gradient(volBins, 14)
    col15 = gradient(volBins, 15)
    col16 = gradient(volBins, 16)
    col17 = gradient(volBins, 17)
    col18 = gradient(volBins, 18)
    col19 = gradient(volBins, 19)
    col20 = gradient(volBins, 20)
    col21 = gradient(volBins, 21)
    col22 = gradient(volBins, 22)
    col23 = gradient(volBins, 23)
    col24 = gradient(volBins, 24)
    col25 = gradient(volBins, 25)
    col26 = gradient(volBins, 26)
    col27 = gradient(volBins, 27)
    col28 = gradient(volBins, 28)
    col29 = gradient(volBins, 29)
    col30 = gradient(volBins, 30)

    fill(p0, p1, col0)
    fill(p1, p2, col1)
    fill(p2, p3, col2)
    fill(p3, p4, col3)
    fill(p4, p5, col4)
    fill(p5, p6, col5)
    fill(p6, p7, col6)
    fill(p7, p8, col7)
    fill(p8, p9, col8)
    fill(p9, p10, col9)
    fill(p10, p11, col10)
    fill(p11, p12, col11)
    fill(p12, p13, col12)
    fill(p13, p14, col13)
    fill(p14, p15, col14)
    fill(p15, p16, col15)
    fill(p16, p17, col16)
    fill(p17, p18, col17)
    fill(p18, p19, col18)
    fill(p19, p20, col19)
    fill(p20, p21, col20)
    fill(p21, p22, col21)
    fill(p22, p23, col22)
    fill(p23, p24, col23)
    fill(p24, p25, col24)
    fill(p25, p26, col25)
    fill(p26, p27, col26)
    fill(p27, p28, col27)
    fill(p28, p29, col28)
    fill(p29, p30, col29)
    fill(p30, HH, col30)

    if barstate.islast:
        lines: Persistent[list[Line]] = array.new_line()

        for l in lines:
            line.delete(l)

        array.clear(lines)

        for i in pine_range(0, 29):
            level1: float = array.get(levels, i)
            level2: float = array.get(levels, i + 1)

            l1: Line = line.new(bar_index, level1, bar_index + 10, level1, color=colorNA)

            l2: Line = line.new(bar_index, level2, bar_index + 10, level2, color=colorNA)

            array.push(lines, l1)
            array.push(lines, l2)

            linefill.new(l1, l2, gradient(volBins, i))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)