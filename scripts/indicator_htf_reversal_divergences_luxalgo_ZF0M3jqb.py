"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, array, bar_index, barstate, box, chart, close, color, fill,
    format, high, hline, input, label, last_bar_index, line, low, math, na, nz, open, plot,
    request, script, size, string, syminfo, ta, time, time_close, timeframe, volume, xloc, yloc
)
from pynecore.types import Box, Color, Label, Line, NA, Persistent, Series


@udt
class HTFData:
    o: float = na(float)
    h: float = na(float)
    l: float = na(float)
    c: float = na(float)
    oIdx: int = na(int)
    hIdx: int = na(int)
    lIdx: int = na(int)
    delta: float = na(float)
    startTime: int = na(int)


@udt
class HTFCandleUI:
    body: Box = na(Box)
    wick: Line = na(Line)
    oM: Line = na(Line)
    hM: Line = na(Line)
    lM: Line = na(Line)
    cM: Line = na(Line)
    oL: Label = na(Label)
    hL: Label = na(Label)
    lL: Label = na(Label)
    cL: Label = na(Label)
    dL: Label = na(Label)
    tL: Label = na(Label)


BULL_COLOR: Color = color.new('#089981')
BEAR_COLOR: Color = color.new('#F23645')
NEUTRAL_COLOR: Color = color.new('#787B86')


@script.indicator("HTF Reversal Divergences [LuxAlgo]", "LuxAlgo - HTF Reversal Divergences", overlay=False, max_labels_count=500, max_boxes_count=500, max_lines_count=500)
def main(
    htfInput=input.timeframe("15", "High Timeframe", group="HTF Reversal Patterns", tooltip="The timeframe to check for reversal patterns."),
    showEngulfingInput=input.bool(True, "Show Engulfing Patterns", group="HTF Reversal Patterns"),
    showPinBarsInput=input.bool(True, "Show Pin Bars", group="HTF Reversal Patterns", tooltip="Includes Hammer and Shooting Star patterns."),
    bullPatternColInput=input.color(BULL_COLOR, "Bullish Pattern Color", group="HTF Reversal Patterns", inline="Colors"),
    bearPatternColInput=input.color(BEAR_COLOR, "Bearish Pattern Color", group="HTF Reversal Patterns", inline="Colors"),
    showDivInput=input.bool(True, "Show RSI Divergences", group="RSI Divergence"),
    rsiLenInput=input.int(14, "RSI Length", group="RSI Divergence", minval=1),
    lbRInput=input.int(5, "Pivot Right Lookback", group="RSI Divergence"),
    lbLInput=input.int(5, "Pivot Left Lookback", group="RSI Divergence"),
    bullDivColInput=input.color(BULL_COLOR, "Bullish Div Color", group="RSI Divergence", inline="Div Colors"),
    bearDivColInput=input.color(BEAR_COLOR, "Bearish Div Color", group="RSI Divergence", inline="Div Colors"),
    showPo3Input=input.bool(False, "Show HTF PO3", group="Advanced: HTF PO3", tooltip="Displays projected HTF candles to the right of price on the main chart."),
    candleCountInput=input.int(1, "Candles to Show", group="Advanced: HTF PO3", minval=1, maxval=10),
    po3OffsetInput=input.int(15, "Right Offset (Bars)", group="Advanced: HTF PO3", minval=5),
    showPo3LabelsInput=input.bool(True, "Show PO3 Price Labels", group="Advanced: HTF PO3"),
    showPo3DeltaInput=input.bool(True, "Show PO3 Running Delta", group="Advanced: HTF PO3"),
    alertBullDivInput=input.bool(True, "Bullish Divergence", group="Alerts"),
    alertBearDivInput=input.bool(True, "Bearish Divergence", group="Alerts"),
    alertBullEngInput=input.bool(True, "Bullish Engulfing", group="Alerts"),
    alertBearEngInput=input.bool(True, "Bearish Engulfing", group="Alerts"),
    alertHammerInput=input.bool(True, "Hammer", group="Alerts"),
    alertStarInput=input.bool(True, "Shooting Star", group="Alerts")
):
    def formatDelta(val: float):
        sign: str = '+' if val > 0 else ''
        absVal: float = math.abs(val)
        return sign + string.format('{0,number,#.#}M', val / 1000000) if absVal >= 1000000 else sign + string.format('{0,number,#.#}K', val / 1000) if absVal >= 1000 else sign + string.tostring(val)

    def drawHtfPattern(name: str, h: float, l: float, o: float, c: float, tStart: int, tEnd: int, col: Color, isBullish: bool):
        timeStr: str = string.format_time(tStart, 'HH:mm', syminfo.timezone)
        labelTxt: str = name + '\n' + timeStr
        midTime: int = math.round((tStart + tEnd) / 2)
        timeInset: int = math.round((tEnd - tStart) * 0.1)

        box.new(tStart, h, tEnd, l, xloc=xloc.bar_time, bgcolor=color.new(col, 90), border_color=color.new(col, 50), border_width=1, force_overlay=True)
        box.new(tStart + timeInset, math.max(o, c), tEnd - timeInset, math.min(o, c), xloc=xloc.bar_time, bgcolor=color.new(col, 60), border_color=color.new(col, 20), border_width=1, force_overlay=True)
        line.new(midTime, h, midTime, l, xloc=xloc.bar_time, color=color.new(col, 20), width=1, force_overlay=True)
        return label.new(midTime, l if isBullish else h, labelTxt, xloc=xloc.bar_time, yloc=yloc.price, color=color.new('#00000000'), textcolor=col, style=label.style_label_up if isBullish else label.style_label_down, size=size.small, force_overlay=True)

    htfNewBar: bool = nz(ta.change(time(htfInput))) != 0

    hOpen, hHigh, hLow, hClose, hPrevOpen, hPrevClose, hTimeStart, hTimeEnd = request.security(syminfo.tickerid, htfInput, (open[1], high[1], low[1], close[1], open[2], close[2], time[1], time_close[1]))

    htfHistory: Persistent[list[HTFData]] = array.new(0, NA(HTFData))
    curO: Persistent[float] = na(float)
    curH: Persistent[float] = na(float)
    curL: Persistent[float] = na(float)
    curOIdx: Persistent[int] = na(int)
    curHIdx: Persistent[int] = na(int)
    curLIdx: Persistent[int] = na(int)
    curDelta: Persistent[float] = 0.0
    curStartTime: Persistent[int] = na(int)

    if showPo3Input:
        if htfNewBar:
            if not na(curO):
                array.unshift(htfHistory, HTFData(curO, curH, curL, close[1], curOIdx, curHIdx, curLIdx, curDelta, curStartTime))
                if array.size(htfHistory) > 10:
                    array.pop(htfHistory)
            curO = open
            curH = high
            curL = low
            curOIdx = bar_index
            curHIdx = bar_index
            curLIdx = bar_index
            curDelta = volume if close > open else -volume if close < open else 0
            curStartTime = time
        else:
            if high > curH or na(curH):
                curH = high
                curHIdx = bar_index
            if low < curL or na(curL):
                curL = low
                curLIdx = bar_index
            curDelta += volume if close > open else -volume if close < open else 0

    isBullEngulfing: bool = showEngulfingInput and hClose > hOpen and (hPrevClose < hPrevOpen) and (hClose >= hPrevOpen) and (hOpen <= hPrevClose)
    isBearEngulfing: bool = showEngulfingInput and hClose < hOpen and (hPrevClose > hPrevOpen) and (hClose <= hPrevOpen) and (hOpen >= hPrevClose)
    isHammer: bool = showPinBarsInput and math.min(hOpen, hClose) - hLow > (hHigh - hLow) * 0.6 and (math.abs(hClose - hOpen) < (hHigh - hLow) * 0.3)
    isShootingStar: bool = showPinBarsInput and hHigh - math.max(hOpen, hClose) > (hHigh - hLow) * 0.6 and (math.abs(hClose - hOpen) < (hHigh - hLow) * 0.3)

    isBullPattern: bool = isBullEngulfing or isHammer
    isBearPattern: bool = isBearEngulfing or isShootingStar

    rsiValue: Series[float] = ta.rsi(close, rsiLenInput)
    rsiColor: Color = bullDivColInput if rsiValue > 50 else bearDivColInput

    phRsi: float = ta.pivothigh(rsiValue, lbLInput, lbRInput)
    plRsi: float = ta.pivotlow(rsiValue, lbLInput, lbRInput)
    bullDivConfirmed: bool = False
    bearDivConfirmed: bool = False

    plPriceMem: Persistent[float] = na(float)
    plRsiMem: Persistent[float] = na(float)
    plIndexMem: Persistent[int] = na(float)
    if not na(plRsi):
        if not na(plPriceMem) and rsiValue[lbRInput] > plRsiMem and (low[lbRInput] < plPriceMem):
            bullDivConfirmed = True
            if showDivInput:
                line.new(plIndexMem, plPriceMem, bar_index - lbRInput, low[lbRInput], color=bullDivColInput, width=2, force_overlay=True)
                label.new(bar_index - lbRInput, low[lbRInput], 'Bull Div', yloc=yloc.belowbar, textcolor=bullDivColInput, color=color.new('#00000000'), size=size.small, style=label.style_label_up, force_overlay=True)
                line.new(plIndexMem, plRsiMem, bar_index - lbRInput, rsiValue[lbRInput], color=bullDivColInput, width=2)
        plPriceMem = low[lbRInput]
        plRsiMem = rsiValue[lbRInput]
        plIndexMem = bar_index - lbRInput

    phPriceMem: Persistent[float] = na(float)
    phRsiMem: Persistent[float] = na(float)
    phIndexMem: Persistent[int] = na(float)
    if not na(phRsi):
        if not na(phPriceMem) and rsiValue[lbRInput] < phRsiMem and (high[lbRInput] > phPriceMem):
            bearDivConfirmed = True
            if showDivInput:
                line.new(phIndexMem, phPriceMem, bar_index - lbRInput, high[lbRInput], color=bearDivColInput, width=2, force_overlay=True)
                label.new(bar_index - lbRInput, high[lbRInput], 'Bear Div', yloc=yloc.abovebar, textcolor=bearDivColInput, color=color.new('#00000000'), size=size.small, style=label.style_label_down, force_overlay=True)
                line.new(phIndexMem, phRsiMem, bar_index - lbRInput, rsiValue[lbRInput], color=bearDivColInput, width=2)
        phPriceMem = high[lbRInput]
        phRsiMem = rsiValue[lbRInput]
        phIndexMem = bar_index - lbRInput

    rsiPlot = plot(rsiValue, 'RSI', color=rsiColor, linewidth=2)
    midPlot = plot(50, 'Mid Line', color=color.new(chart.fg_color, 80), style=plot.style_linebr)
    fill(midPlot, rsiPlot, 50, rsiValue, color.new(bullDivColInput, 100) if rsiValue > 50 else color.new(bearDivColInput, 50), color.new(bullDivColInput, 50) if rsiValue > 50 else color.new(bearDivColInput, 100))
    hline(70, 'OB', color=color.new(bearDivColInput, 50), linestyle=hline.style_dashed)
    hline(30, 'OS', color=color.new(bullDivColInput, 50), linestyle=hline.style_dashed)

    if htfNewBar and (not na(hTimeStart)):
        if isBullPattern:
            drawHtfPattern('Bull Engulfing' if isBullEngulfing else 'Hammer', hHigh, hLow, hOpen, hClose, hTimeStart, hTimeEnd, bullPatternColInput, True)
        if isBearPattern:
            drawHtfPattern('Bear Engulfing' if isBearEngulfing else 'Shooting Star', hHigh, hLow, hOpen, hClose, hTimeStart, hTimeEnd, bearPatternColInput, False)

    uiElements: Persistent[list[HTFCandleUI]] = array.new(0, NA(HTFCandleUI))
    if barstate.islast and showPo3Input:
        if array.size(uiElements) > 0:
            for i in pine_range(0, array.size(uiElements) - 1):
                ui: HTFCandleUI = array.get(uiElements, i)
                box.delete(ui.body)
                line.delete(ui.wick)
                if not na(ui.oM):
                    line.delete(ui.oM)
                if not na(ui.hM):
                    line.delete(ui.hM)
                if not na(ui.lM):
                    line.delete(ui.lM)
                if not na(ui.cM):
                    line.delete(ui.cM)
                if not na(ui.oL):
                    label.delete(ui.oL)
                if not na(ui.hL):
                    label.delete(ui.hL)
                if not na(ui.lL):
                    label.delete(ui.lL)
                if not na(ui.cL):
                    label.delete(ui.cL)
                if not na(ui.dL):
                    label.delete(ui.dL)
                if not na(ui.tL):
                    label.delete(ui.tL)
        array.clear(uiElements)

        candleWidth: int = 6
        candleGap: int = 10
        for p in pine_range(0, candleCountInput - 1):
            isLive: bool = p == candleCountInput - 1
            data: HTFData = HTFData(curO, curH, curL, close, curOIdx, curHIdx, curLIdx, curDelta, curStartTime) if isLive else array.get(htfHistory, candleCountInput - 2 - p) if array.size(htfHistory) > candleCountInput - 2 - p else na

            if not na(data):
                startIdx: int = last_bar_index + po3OffsetInput + p * (candleWidth + candleGap)
                endIdx: int = startIdx + candleWidth
                midIdx: int = (startIdx + endIdx) / 2
                baseColor: Color = bullPatternColInput if data.c >= data.o else bearPatternColInput
                wickColor: Color = baseColor if isLive else color.new(baseColor, 70)
                wLine: Line = line.new(midIdx, data.h, midIdx, data.l, color=wickColor, width=2, force_overlay=True)
                bBox: Box = box.new(startIdx, math.max(data.o, data.c), endIdx, math.min(data.o, data.c), border_color=wickColor, bgcolor=color.new(baseColor, 20 if isLive else 85), force_overlay=True)
                oM__000000cd__: Line = na(Line)
                hM__000000cd__: Line = na(Line)
                lM__000000cd__: Line = na(Line)
                cM__000000cd__: Line = na(Line)
                oL__000000cd__: Label = na(Line)
                hL__000000cd__: Label = na(Line)
                lL__000000cd__: Label = na(Line)
                cL__000000cd__: Label = na(Line)
                dL__000000cd__: Label = na(Line)
                if isLive:
                    oM__000000cd__ = line.new(data.oIdx, data.o, startIdx, data.o, color=NEUTRAL_COLOR, style=line.style_dashed, force_overlay=True)
                    hM__000000cd__ = line.new(data.hIdx, data.h, midIdx, data.h, color=bullPatternColInput, style=line.style_dashed, force_overlay=True)
                    lM__000000cd__ = line.new(data.lIdx, data.l, midIdx, data.l, color=bearPatternColInput, style=line.style_dashed, force_overlay=True)
                    cM__000000cd__ = line.new(bar_index, data.c, endIdx, data.c, color=baseColor, style=line.style_dashed, force_overlay=True)
                    if showPo3LabelsInput:
                        oL__000000cd__ = label.new(endIdx + 1, data.o, 'Open: ' + string.tostring(data.o, format.mintick), color=color.new('#00000000'), textcolor=NEUTRAL_COLOR, style=label.style_label_left, size=size.small, force_overlay=True)
                        hL__000000cd__ = label.new(endIdx + 1, data.h, 'High: ' + string.tostring(data.h, format.mintick), color=color.new('#00000000'), textcolor=bullPatternColInput, style=label.style_label_left, size=size.small, force_overlay=True)
                        lL__000000cd__ = label.new(endIdx + 1, data.l, 'Low: ' + string.tostring(data.l, format.mintick), color=color.new('#00000000'), textcolor=bearPatternColInput, style=label.style_label_left, size=size.small, force_overlay=True)
                        cL__000000cd__ = label.new(endIdx + 1, data.c, 'Close: ' + string.tostring(data.c, format.mintick), color=color.new('#00000000'), textcolor=baseColor, style=label.style_label_left, size=size.small, force_overlay=True)
                totalMins: int = timeframe.in_seconds(htfInput) / 60
                tfStr: str = string.tostring(totalMins / 1440) + 'D' if totalMins >= 1440 else string.tostring(totalMins / 60) + 'H' if totalMins >= 60 else string.tostring(totalMins) + 'm'
                tL__000000cd__: Label = label.new(midIdx, data.h, tfStr + ('\n' + string.format_time(data.startTime, 'HH:mm', syminfo.timezone) if not isLive else ''), color=color.new('#00000000'), textcolor=NEUTRAL_COLOR if isLive else color.new(NEUTRAL_COLOR, 60), style=label.style_label_down, size=size.normal, force_overlay=True)
                if showPo3DeltaInput:
                    dL__000000cd__ = label.new(midIdx, data.l, 'Delta: ' + formatDelta(data.delta), color=color.new('#00000000'), textcolor=(bullPatternColInput if data.delta >= 0 else bearPatternColInput) if isLive else color.new(NEUTRAL_COLOR, 60), style=label.style_label_up, size=size.normal, force_overlay=True)
                array.push(uiElements, HTFCandleUI(bBox, wLine, oM__000000cd__, hM__000000cd__, lM__000000cd__, cM__000000cd__, oL__000000cd__, hL__000000cd__, lL__000000cd__, cL__000000cd__, dL__000000cd__, tL__000000cd__))

    if alertBullDivInput and bullDivConfirmed:
        alert('Bullish RSI Divergence on ' + syminfo.ticker, alert.freq_once_per_bar_close)
    if alertBearDivInput and bearDivConfirmed:
        alert('Bearish RSI Divergence on ' + syminfo.ticker, alert.freq_once_per_bar_close)
    if alertBullEngInput and htfNewBar and isBullEngulfing:
        alert('HTF Bullish Engulfing on ' + syminfo.ticker, alert.freq_once_per_bar_close)
    if alertBearEngInput and htfNewBar and isBearEngulfing:
        alert('HTF Bearish Engulfing on ' + syminfo.ticker, alert.freq_once_per_bar_close)
    if alertHammerInput and htfNewBar and isHammer:
        alert('HTF Hammer on ' + syminfo.ticker, alert.freq_once_per_bar_close)
    if alertStarInput and htfNewBar and isShootingStar:
        alert('HTF Shooting Star on ' + syminfo.ticker, alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
