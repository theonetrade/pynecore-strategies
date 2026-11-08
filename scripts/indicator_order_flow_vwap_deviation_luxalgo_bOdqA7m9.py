"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, bar_index, barstate, bgcolor, box, chart, close, color, fill,
    high, hlc3, input, label, line, location, low, math, na, open, plot, plotshape, script, shape,
    size, string, syminfo, ta, time, timeframe, volume, xloc, yloc
)
from pynecore.types import Box, Label, Line, Persistent, Series

G_VWAP: str = "VWAP Settings"
G_STOP: str = "Stop Zones (Pivots)"
G_VP: str = "Volume Profile & Stop Zones"
G_IFVG: str = "Inversion Fair Value Gaps (IFVGs)"


@script.indicator("Order Flow VWAP Deviation [LuxAlgo]", "LuxAlgo - Order Flow VWAP Deviation", overlay=True, max_boxes_count=500, max_lines_count=500, max_labels_count=500)
def main(
    vwapAnchor=input.string("Session", "VWAP Anchor", options=("Session", "Week", "Month", "Year"), group=G_VWAP),
    stdDevMult=input.float(2.0, "Std. Dev Multiplier", minval=0.5, step=0.1, group=G_VWAP),
    pivotLookback=input.int(50, "Pivot Lookback (Stop Zones)", minval=10, group=G_STOP),
    maxActiveLines=input.int(10, "Max Active Lines", minval=1, maxval=50, group=G_STOP),
    vpRows=input.int(50, "Profile Rows", minval=10, maxval=100, group=G_VP),
    vpWidth=input.int(30, "Profile Max Width (Bars)", minval=5, group=G_VP),
    vpOffset=input.int(10, "Profile Right Offset", minval=0, group=G_VP),
    sessionAnchor=input.string("1800-1801", "Anchor Time Range (HHMM-HHMM)", group=G_VP),
    sessionTz=input.string("GMT-4", "Timezone", options=("GMT-5", "GMT-4", "UTC"), group=G_VP),
    stopThreshold=input.float(1.5, "Stop Zone Volume Multiplier", minval=1.0, step=0.1, group=G_VP),
    showIFVG=input.bool(False, "Show IFVGs", group=G_IFVG),
    ifvgVolFilter=input.float(1.2, "IFVG Volatility Filter", minval=0.5, step=0.1, group=G_IFVG),
    ifvgHistory=input.int(5, "Max Active IFVGs", minval=1, maxval=20, group=G_IFVG)
):
    __block_result__ = na
    __switch__ = vwapAnchor
    if __switch__ == "Session":
        __block_result__ = timeframe.change('D')
    elif __switch__ == "Week":
        __block_result__ = timeframe.change('W')
    elif __switch__ == "Month":
        __block_result__ = timeframe.change('M')
    elif __switch__ == "Year":
        __block_result__ = timeframe.change('12M')
    else:
        __block_result__ = False
    isNewVwapPeriod = __block_result__

    vValue, vUpper, vLower = ta.vwap(hlc3, isNewVwapPeriod, stdDevMult)

    ph = ta.pivothigh(high, pivotLookback, pivotLookback)
    pl = ta.pivotlow(low, pivotLookback, pivotLookback)

    upperLines: Persistent[list[Line]] = array.new_line()
    lowerLines: Persistent[list[Line]] = array.new_line()

    if not na(ph):
        newLine = line.new(bar_index - pivotLookback, ph, bar_index, ph, color=color.new(color.new('#F23645'), 60), style=line.style_dashed)
        array.unshift(upperLines, newLine)
        if array.size(upperLines) > maxActiveLines:
            line.delete(array.pop(upperLines))

    if not na(pl):
        newLine = line.new(bar_index - pivotLookback, pl, bar_index, pl, color=color.new(color.new('#089981'), 60), style=line.style_dashed)
        array.unshift(lowerLines, newLine)
        if array.size(lowerLines) > maxActiveLines:
            line.delete(array.pop(lowerLines))

    avgVol20 = ta.sma(volume, 20)
    stopTriggeredUpper: Persistent[bool] = False
    stopTriggeredLower: Persistent[bool] = False
    stopTriggeredUpper = False
    stopTriggeredLower = False

    if array.size(upperLines) > 0:
        for i in pine_range(array.size(upperLines) - 1, 0):
            l = array.get(upperLines, i)
            if high >= line.get_y1(l):
                if volume > avgVol20 * 1.2:
                    stopTriggeredUpper = True
                line.set_x2(l, bar_index)
                array.remove(upperLines, i)
            else:
                line.set_x2(l, bar_index)

    if array.size(lowerLines) > 0:
        for i in pine_range(array.size(lowerLines) - 1, 0):
            l = array.get(lowerLines, i)
            if low <= line.get_y1(l):
                if volume > avgVol20 * 1.2:
                    stopTriggeredLower = True
                line.set_x2(l, bar_index)
                array.remove(lowerLines, i)
            else:
                line.set_x2(l, bar_index)

    avgBody = ta.sma(math.abs(close - open), 50)
    volatilityValid = math.abs(close[1] - open[1]) > avgBody * ifvgVolFilter

    bearFVG = volatilityValid and high < low[2]
    bullFVG = volatilityValid and low > high[2]

    activeBearFvgTop: Persistent[list[float]] = array.new_float()
    activeBearFvgBtm: Persistent[list[float]] = array.new_float()
    activeBearFvgBar: Persistent[list[int]] = array.new_int()

    activeBullFvgTop: Persistent[list[float]] = array.new_float()
    activeBullFvgBtm: Persistent[list[float]] = array.new_float()
    activeBullFvgBar: Persistent[list[int]] = array.new_int()

    if showIFVG:
        if bearFVG:
            array.unshift(activeBearFvgTop, low[2])
            array.unshift(activeBearFvgBtm, high)
            array.unshift(activeBearFvgBar, bar_index[1])
        if bullFVG:
            array.unshift(activeBullFvgTop, low)
            array.unshift(activeBullFvgBtm, high[2])
            array.unshift(activeBullFvgBar, bar_index[1])

    ifvgBoxes: Persistent[list[Box]] = array.new_box()
    ifvgLabels: Persistent[list[Label]] = array.new_label()
    ifvgIsBull: Persistent[list[bool]] = array.new_bool()

    if showIFVG:
        if array.size(activeBearFvgTop) > 0:
            for i in pine_range(array.size(activeBearFvgTop) - 1, 0):
                top = array.get(activeBearFvgTop, i)
                btm = array.get(activeBearFvgBtm, i)
                if close > top:
                    startBar = array.get(activeBearFvgBar, i)
                    newBox = box.new(startBar, top, bar_index + 10, btm, bgcolor=color.new(color.new('#089981'), 85), border_color=color.new(color.new('#089981'), 60))
                    newLabel = label.new(bar_index, (top + btm) / 2, 'IFVG', color=color.new('#00000000'), textcolor=color.new('#089981'), style=label.style_label_center, size=size.small)
                    array.unshift(ifvgBoxes, newBox)
                    array.unshift(ifvgLabels, newLabel)
                    array.unshift(ifvgIsBull, True)
                    array.remove(activeBearFvgTop, i)
                    array.remove(activeBearFvgBtm, i)
                    array.remove(activeBearFvgBar, i)
                    if array.size(ifvgBoxes) > ifvgHistory:
                        box.delete(array.pop(ifvgBoxes))
                        label.delete(array.pop(ifvgLabels))
                        array.pop(ifvgIsBull)

        if array.size(activeBullFvgTop) > 0:
            for i in pine_range(array.size(activeBullFvgTop) - 1, 0):
                top = array.get(activeBullFvgTop, i)
                btm = array.get(activeBullFvgBtm, i)
                if close < btm:
                    startBar = array.get(activeBullFvgBar, i)
                    newBox = box.new(startBar, top, bar_index + 10, btm, bgcolor=color.new(color.new('#F23645'), 85), border_color=color.new(color.new('#F23645'), 60))
                    newLabel = label.new(bar_index, (top + btm) / 2, 'IFVG', color=color.new('#00000000'), textcolor=color.new('#F23645'), style=label.style_label_center, size=size.small)
                    array.unshift(ifvgBoxes, newBox)
                    array.unshift(ifvgLabels, newLabel)
                    array.unshift(ifvgIsBull, False)
                    array.remove(activeBullFvgTop, i)
                    array.remove(activeBullFvgBtm, i)
                    array.remove(activeBullFvgBar, i)
                    if array.size(ifvgBoxes) > ifvgHistory:
                        box.delete(array.pop(ifvgBoxes))
                        label.delete(array.pop(ifvgLabels))
                        array.pop(ifvgIsBull)

    if array.size(ifvgBoxes) > 0:
        for i in pine_range(array.size(ifvgBoxes) - 1, 0):
            b = array.get(ifvgBoxes, i)
            l = array.get(ifvgLabels, i)
            isBull = array.get(ifvgIsBull, i)
            top = box.get_top(b)
            btm = box.get_bottom(b)

            mitigated = close < btm if isBull else close > top

            if mitigated:
                box.delete(b)
                label.delete(l)
                array.remove(ifvgBoxes, i)
                array.remove(ifvgLabels, i)
                array.remove(ifvgIsBull, i)
            else:
                if bar_index < box.get_right(b):
                    box.set_right(b, bar_index + 5)

    t: Series = time(timeframe.period, sessionAnchor, sessionTz)
    isAnchorBar = not na(t) and na(t[1])
    sessionPrices: Persistent[list[float]] = array.new_float()
    sessionVolumes: Persistent[list[float]] = array.new_float()
    sessionBuyVols: Persistent[list[float]] = array.new_float()
    sessionSellVols: Persistent[list[float]] = array.new_float()

    if isAnchorBar:
        array.clear(sessionPrices)
        array.clear(sessionVolumes)
        array.clear(sessionBuyVols)
        array.clear(sessionSellVols)

    range_val: float = math.max(high - low, syminfo.mintick)
    bVol: float = volume * (close - low) / range_val
    sVol: float = volume * (high - close) / range_val

    array.push(sessionPrices, close)
    array.push(sessionVolumes, volume)
    array.push(sessionBuyVols, bVol)
    array.push(sessionSellVols, sVol)

    bgcolor(color.new(color.yellow, 80) if isAnchorBar else na)

    profileBoxes: Persistent[list[Box]] = array.new_box()
    profileLabels: Persistent[list[Label]] = array.new_label()

    if barstate.islast and array.size(sessionPrices) > 0:
        sHigh: float = array.get(sessionPrices, 0)
        sLow: float = array.get(sessionPrices, 0)
        for p in sessionPrices:
            sHigh = math.max(sHigh, p)
            sLow = math.min(sLow, p)

        binVols: list[float] = array.new_float(vpRows, 0.0)
        binBuyVols: list[float] = array.new_float(vpRows, 0.0)
        binSellVols: list[float] = array.new_float(vpRows, 0.0)
        bSize: float = (sHigh - sLow) / vpRows

        if bSize > 0:
            for i in pine_range(0, array.size(sessionPrices) - 1):
                p: float = array.get(sessionPrices, i)
                v: float = array.get(sessionVolumes, i)
                bv: float = array.get(sessionBuyVols, i)
                sv: float = array.get(sessionSellVols, i)
                bIdx: int = math.min(vpRows - 1, math.max(0, math.floor((p - sLow) / bSize)))
                array.set(binVols, bIdx, array.get(binVols, bIdx) + v)
                array.set(binBuyVols, bIdx, array.get(binBuyVols, bIdx) + bv)
                array.set(binSellVols, bIdx, array.get(binSellVols, bIdx) + sv)

            if array.size(profileBoxes) > 0:
                for i in pine_range(0, array.size(profileBoxes) - 1):
                    box.delete(array.get(profileBoxes, i))
                array.clear(profileBoxes)
            if array.size(profileLabels) > 0:
                for i in pine_range(0, array.size(profileLabels) - 1):
                    label.delete(array.get(profileLabels, i))
                array.clear(profileLabels)

            maxV: float = 0.0
            totalV: float = 0.0
            pIdx: int = 0
            for i in pine_range(0, vpRows - 1):
                v = array.get(binVols, i)
                totalV += v
                if v > maxV:
                    maxV = v
                    pIdx = i

            avgV = totalV / vpRows
            for i in pine_range(0, vpRows - 1):
                v = array.get(binVols, i)
                if v > 0:
                    nW = v / maxV * vpWidth
                    isStop = v > avgV * stopThreshold
                    binColor = color.new(color.new('#FFEB3B'), 10) if i == pIdx else color.new(color.new('#FF9800'), 30) if isStop else color.new(color.new('#5B9CF6'), 60)

                    t_box = sLow + (i + 1) * bSize
                    b_box = sLow + i * bSize
                    l_box = bar_index + vpOffset
                    r_box = l_box + math.round(nW)
                    array.push(profileBoxes, box.new(l_box, t_box, r_box, b_box, border_color=color.new(chart.bg_color, 100), bgcolor=binColor))

                    if isStop or i == pIdx:
                        diffMult = v / avgV
                        bv = array.get(binBuyVols, i)
                        sv = array.get(binSellVols, i)

                        y_center = (t_box + b_box) / 2
                        multColor = color.new('#FFEB3B') if i == pIdx else color.new('#FF9800')

                        multTxt = string.format('{0,number,#.#}x', diffMult)
                        multLabel = label.new(r_box, y_center, multTxt, xloc.bar_index, yloc.price, color.new(chart.bg_color, 100), label.style_label_left, multColor, size.tiny)
                        array.push(profileLabels, multLabel)

                        sideTxt = 'B' if bv > sv else 'S'
                        sideColor = color.new('#089981') if bv > sv else color.new('#F23645')

                        sideLabel = label.new(r_box + 3, y_center, sideTxt, xloc.bar_index, yloc.price, color.new(chart.bg_color, 100), label.style_label_left, sideColor, size.tiny)
                        array.push(profileLabels, sideLabel)

    plot(vValue, 'VWAP', color.new(chart.fg_color, 50))
    pUp = plot(vUpper, 'Upper Band', color.new(color.new('#F23645'), 0))
    pLo = plot(vLower, 'Lower Band', color.new(color.new('#089981'), 0))
    fill(pUp, plot(vValue), vUpper, vValue, color.new(color.new('#F23645'), 90), color.new(color.new('#F23645'), 100))
    fill(pLo, plot(vValue), vLower, vValue, color.new(color.new('#089981'), 90), color.new(color.new('#089981'), 100))

    plotshape(stopTriggeredUpper, 'Stops Triggered High', shape.circle, location.abovebar, color.new(color.new('#F23645'), 50), size=size.tiny)
    plotshape(stopTriggeredLower, 'Stops Triggered Low', shape.circle, location.belowbar, color.new(color.new('#089981'), 50), size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
