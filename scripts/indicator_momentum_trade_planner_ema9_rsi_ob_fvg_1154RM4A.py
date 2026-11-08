"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barcolor, barstate, box, close,
    color, format, high, input, label, line, low, math, na, plot, position, script, size, string,
    syminfo, ta, table, text, timeframe, yloc
)
from pynecore.types import Box, Color, Label, Line, NA, Persistent, Series, Table


@script.indicator("9 EMA + RSI Signals (SL + 3 TPs) + OB/FVG [15m]", shorttitle="Premium GOLD Signal", overlay=True, max_lines_count=500, max_labels_count=500, max_boxes_count=500, max_bars_back=500)
def main(
    emaLen=input.int(9, "EMA Length", minval=1, group="Signal"),
    rsiLen=input.int(14, "RSI Length", minval=1, group="Signal"),
    rsiLevel=input.float(50, "RSI Level", group="Signal"),
    oneAtATime=input.bool(False, "Hide same-direction signals while a trade is active", group="Signal"),
    slLookback=input.int(4, "SL Lookback (previous candles)", minval=1, group="Risk"),
    slBuffer=input.float(0.0, "SL Buffer (price)", minval=0, step=0.1, group="Risk", tooltip="Extra distance added beyond the swing low/high. 0 = exactly at the low/high."),
    tpStep=input.float(10.0, "TP Step (price)", minval=0.01, step=0.5, group="Targets", tooltip="TP1 = entry ± 1×step, TP2 = ± 2×step, TP3 = ± 3×step. For XAUUSD, 10.0 = $10 (4000 → 4010 / 4020 / 4030)."),
    showLevels=input.bool(True, "Show Entry / SL / TP zones", group="Display"),
    showHits=input.bool(True, "Mark TP / SL hits", group="Display"),
    extBars=input.int(10, "Extend beyond current bar", minval=1, maxval=100, group="Display"),
    zoneTransp=input.int(80, "Zone transparency", minval=0, maxval=100, group="Display"),
    fadeBars=input.int(15, "Fade length on right (bars)", minval=0, maxval=100, group="Display"),
    colorBars=input.bool(True, "Color candles by trend", group="Display"),
    showEma=input.bool(True, "Show EMA", group="Display"),
    slCol=input.color(color.new('#F44336'), "Stop Loss color", group="Colors"),
    tpCol=input.color(color.new('#43D443'), "Take Profit color", group="Colors"),
    entryCol=input.color(color.new('#9E9E9E'), "Entry color", group="Colors"),
    emaCol=input.color(color.new('#2962FF'), "EMA color", group="Colors"),
    showOB=input.bool(True, "Show Order Blocks", group="Order Blocks"),
    swingLen=input.int(10, "Swing length", minval=2, maxval=50, group="Order Blocks", tooltip="Bars on each side used to confirm a swing high/low. Higher = fewer, stronger OBs."),
    maxOB=input.int(3, "Max OBs per side", minval=1, maxval=20, group="Order Blocks"),
    obBullCol=input.color(color.new('#2962FF'), "Bullish OB", group="Order Blocks"),
    obBearCol=input.color(color.new('#E040FB'), "Bearish OB", group="Order Blocks"),
    showFVG=input.bool(True, "Show Fair Value Gaps", group="FVG"),
    fvgMinAtr=input.float(0.25, "Min FVG size (× ATR)", minval=0, step=0.05, group="FVG", tooltip="Filters out tiny gaps. 0 = show all."),
    maxFVG=input.int(3, "Max FVGs per side", minval=1, maxval=20, group="FVG"),
    fvgBullCol=input.color(color.new('#00BCD4'), "Bullish FVG", group="FVG"),
    fvgBearCol=input.color(color.new('#FF9800'), "Bearish FVG", group="FVG"),
    removeMitigated=input.bool(True, "Remove mitigated OBs / filled FVGs", group="OB / FVG")
):
    emaVal = ta.ema(close, emaLen)
    rsiVal = ta.rsi(close, rsiLen)
    atrVal = ta.atr(14)

    prevLow = inline_series(ta.lowest(low, slLookback), 1)
    prevHigh = inline_series(ta.highest(high, slLookback), 1)

    bullCond: Series = close > emaVal and rsiVal > rsiLevel
    bearCond: Series = close < emaVal and rsiVal < rsiLevel

    dir: Persistent[int] = 0
    entryBar: Persistent[int] = na(int)
    entry: Persistent[float] = na(float)
    sl: Persistent[float] = na(float)
    tp1: Persistent[float] = na(float)
    tp2: Persistent[float] = na(float)
    tp3: Persistent[float] = na(float)
    hit1: Persistent[bool] = False
    hit2: Persistent[bool] = False
    hit3: Persistent[bool] = False

    zoneBoxes: Persistent[list[Box]] = array.new_box()
    lvlLines: Persistent[list[Line]] = array.new_line()
    lvlLabels: Persistent[list[Label]] = array.new_label()
    markLabels: Persistent[list[Label]] = array.new_label()

    bullOBs: Persistent[list[Box]] = array.new_box()
    bearOBs: Persistent[list[Box]] = array.new_box()
    bullFVGs: Persistent[list[Box]] = array.new_box()
    bearFVGs: Persistent[list[Box]] = array.new_box()

    FADE_SEGS: int = 6

    def clearTrade():
        for b in zoneBoxes:
            box.delete(b)
        for l in lvlLines:
            line.delete(l)
        for lb in lvlLabels:
            label.delete(lb)
        array.clear(zoneBoxes)
        array.clear(lvlLines)
        return array.clear(lvlLabels)

    def clearMarks():
        for lb in markLabels:
            label.delete(lb)
        return array.clear(markLabels)

    def drawZone(x1: int, x2: int, top: float, bot: float, col: Color):
        fadeStart = math.max(x1, x2 - fadeBars)
        if fadeStart > x1:
            array.push(zoneBoxes, box.new(x1, top, fadeStart, bot, border_color=NA(Color), border_width=0, bgcolor=color.new(col, zoneTransp)))
        span = x2 - fadeStart
        __block_result__ = na
        for i in pine_range(0, FADE_SEGS - 1):
            a = fadeStart + math.round(span * i * 1.0 / FADE_SEGS)
            b = fadeStart + math.round(span * (i + 1) * 1.0 / FADE_SEGS)
            __block_result_1__ = na
            if b > a:
                t = zoneTransp + (100.0 - zoneTransp) * (i + 1) / (FADE_SEGS + 1)
                __block_result_1__ = array.push(zoneBoxes, box.new(a, top, b, bot, border_color=NA(Color), border_width=0, bgcolor=color.new(col, t)))
            __block_result__ = __block_result_1__
        return __block_result__

    def drawLevel(x1: int, x2: int, price: float, col: Color, txt: str):
        array.push(lvlLines, line.new(x1, price, x2, price, color=col, width=1))
        return array.push(lvlLabels, label.new(x2, price, txt + ': ' + string.tostring(price, format.mintick), style=label.style_label_left, color=col, textcolor=color.white, size=size.small))

    def drawTrade(xEnd: int):
        clearTrade()
        drawZone(entryBar, xEnd, math.max(entry, sl), math.min(entry, sl), slCol)
        drawZone(entryBar, xEnd, math.max(entry, tp3), math.min(entry, tp3), tpCol)
        drawLevel(entryBar, xEnd, sl, slCol, 'Stop Loss')
        drawLevel(entryBar, xEnd, entry, entryCol, 'Entry')
        drawLevel(entryBar, xEnd, tp1, tpCol, 'Take Profit 1')
        drawLevel(entryBar, xEnd, tp2, tpCol, 'Take Profit 2')
        return drawLevel(entryBar, xEnd, tp3, tpCol, 'Take Profit 3')

    def addDot(above: bool, col: Color):
        return array.push(markLabels, label.new(bar_index, high if above else low, '', yloc=yloc.abovebar if above else yloc.belowbar, style=label.style_circle, color=col, size=size.tiny))

    def newZone(x1: int, top: float, bot: float, col: Color, txt: str):
        return box.new(x1, top, bar_index + extBars, bot, border_color=color.new(col, 40), border_width=1, bgcolor=color.new(col, 82), text=txt, text_color=col, text_size=size.tiny, text_halign=text.align_left)

    def pushZone(arr: list[Box], b: Box, maxN: int):
        array.push(arr, b)
        __block_result_2__ = na
        if array.size(arr) > maxN:
            __block_result_2__ = box.delete(array.shift(arr))
        return __block_result_2__

    def updateZones(arr: list[Box], isBull: bool, priceDown: float, priceUp: float):
        n = array.size(arr)
        __block_result_3__ = na
        if n > 0:
            __block_result_4__ = na
            for i in pine_range(n - 1, 0):
                b = array.get(arr, i)
                broken = priceDown < box.get_bottom(b) if isBull else priceUp > box.get_top(b)
                __block_result_5__ = na
                if broken:
                    array.remove(arr, i)
                    __block_result_6__ = na
                    if removeMitigated:
                        __block_result_6__ = box.delete(b)
                    else:
                        __block_result_6__ = box.set_right(b, bar_index)
                    __block_result_5__ = __block_result_6__
                else:
                    __block_result_5__ = box.set_right(b, bar_index + extBars)
                __block_result_4__ = __block_result_5__
            __block_result_3__ = __block_result_4__
        return __block_result_3__

    ph = ta.pivothigh(high, swingLen, swingLen)
    pl = ta.pivotlow(low, swingLen, swingLen)

    swHigh: Persistent[float] = na(float)
    swHighBar: Persistent[int] = na(int)
    swHighUsed: Persistent[bool] = True
    swLow: Persistent[float] = na(float)
    swLowBar: Persistent[int] = na(int)
    swLowUsed: Persistent[bool] = True

    if not na(ph):
        swHigh = ph
        swHighBar = bar_index - swingLen
        swHighUsed = False
    if not na(pl):
        swLow = pl
        swLowBar = bar_index - swingLen
        swLowUsed = False

    updateZones(bullOBs, True, close, close)
    updateZones(bearOBs, False, close, close)

    if showOB and (not swHighUsed) and (close > swHigh) and barstate.isconfirmed:
        swHighUsed = True
        span = math.min(bar_index - swHighBar, 200)
        obTop: float = high[1]
        obBot: float = low[1]
        obIdx: int = 1
        for i in pine_range(1, span):
            if low[i] < obBot:
                obBot = low[i]
                obTop = high[i]
                obIdx = i
        pushZone(bullOBs, newZone(bar_index - obIdx, obTop, obBot, obBullCol, 'Bull OB'), maxOB)

    if showOB and (not swLowUsed) and (close < swLow) and barstate.isconfirmed:
        swLowUsed = True
        span = math.min(bar_index - swLowBar, 200)
        obTop: float = high[1]
        obBot: float = low[1]
        obIdx: int = 1
        for i in pine_range(1, span):
            if high[i] > obTop:
                obTop = high[i]
                obBot = low[i]
                obIdx = i
        pushZone(bearOBs, newZone(bar_index - obIdx, obTop, obBot, obBearCol, 'Bear OB'), maxOB)

    updateZones(bullFVGs, True, low, high)
    updateZones(bearFVGs, False, low, high)

    minGap = atrVal * fvgMinAtr

    if showFVG and barstate.isconfirmed and (low > high[2]) and (low - high[2] >= minGap):
        pushZone(bullFVGs, newZone(bar_index - 2, low, high[2], fvgBullCol, 'FVG'), maxFVG)

    if showFVG and barstate.isconfirmed and (high < low[2]) and (low[2] - high >= minGap):
        pushZone(bearFVGs, newZone(bar_index - 2, low[2], high, fvgBearCol, 'FVG'), maxFVG)

    buySignal = bullCond and (not bullCond[1]) and barstate.isconfirmed and (not oneAtATime or dir != 1)
    sellSignal = bearCond and (not bearCond[1]) and barstate.isconfirmed and (not oneAtATime or dir != -1)

    tp1Hit: bool = False
    tp2Hit: bool = False
    tp3Hit: bool = False
    slHit: bool = False

    if dir != 0 and bar_index > entryBar:
        isLong = dir == 1
        if low <= sl if isLong else high >= sl:
            slHit = True
        else:
            if not hit1 and (high >= tp1 if isLong else low <= tp1):
                hit1 = True
                tp1Hit = True
            if not hit2 and (high >= tp2 if isLong else low <= tp2):
                hit2 = True
                tp2Hit = True
            if not hit3 and (high >= tp3 if isLong else low <= tp3):
                hit3 = True
                tp3Hit = True
        if showHits:
            if tp1Hit or tp2Hit or tp3Hit:
                addDot(isLong, tpCol)
            if slHit:
                addDot(not isLong, slCol)
        if slHit or hit3:
            dir = 0
            if showLevels:
                drawTrade(bar_index)

    if buySignal or sellSignal:
        clearTrade()
        clearMarks()
        dir = 1 if buySignal else -1
        entryBar = bar_index
        entry = close
        sl = prevLow - slBuffer if buySignal else prevHigh + slBuffer
        tp1 = entry + dir * tpStep
        tp2 = entry + dir * tpStep * 2
        tp3 = entry + dir * tpStep * 3
        hit1 = False
        hit2 = False
        hit3 = False

        if buySignal:
            array.push(markLabels, label.new(bar_index, low, 'Buy', yloc=yloc.belowbar, style=label.style_label_up, color=color.new(tpCol, 10), textcolor=color.white, size=size.small))
        else:
            array.push(markLabels, label.new(bar_index, high, 'Sell', yloc=yloc.abovebar, style=label.style_label_down, color=color.new(slCol, 10), textcolor=color.white, size=size.small))

        if showLevels:
            drawTrade(bar_index + extBars)

        alert(('BUY ' if buySignal else 'SELL ') + syminfo.ticker + ' @ ' + string.tostring(entry, format.mintick) + ' | SL ' + string.tostring(sl, format.mintick) + ' | TP1 ' + string.tostring(tp1, format.mintick) + ' | TP2 ' + string.tostring(tp2, format.mintick) + ' | TP3 ' + string.tostring(tp3, format.mintick), alert.freq_once_per_bar_close)

    if barstate.islast and dir != 0 and showLevels:
        drawTrade(bar_index + extBars)

    plot(emaVal if showEma else na, 'EMA', color=emaCol, linewidth=2)
    barcolor((tpCol if bullCond else slCol if bearCond else color.gray) if colorBars else na)

    alertcondition(buySignal, 'Buy Signal', 'EMA9 + RSI BUY on {{ticker}} @ {{close}}')
    alertcondition(sellSignal, 'Sell Signal', 'EMA9 + RSI SELL on {{ticker}} @ {{close}}')
    alertcondition(tp1Hit or tp2Hit or tp3Hit, 'TP Hit', 'TP hit on {{ticker}}')
    alertcondition(slHit, 'SL Hit', 'SL hit on {{ticker}}')

    tfWarn: Persistent[Table] = table.new(position.top_right, 1, 1)
    if barstate.islast and timeframe.period != '15':
        table.cell(tfWarn, 0, 0, 'Designed for 15m — current TF: ' + timeframe.period, bgcolor=color.new(color.orange, 20), text_color=color.white, text_size=size.small)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)