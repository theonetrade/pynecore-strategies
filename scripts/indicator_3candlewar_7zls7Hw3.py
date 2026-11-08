"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barmerge, barstate, box, close,
    color, high, input, label, line, location, low, math, na, open, plot, plotchar, request,
    script, size, string, syminfo, ta, xloc
)
from pynecore.types import Box, Label, Line, Persistent, Series

grpLines: str = "C1 Lines"
grpSig: str = "Pattern Signals"
grpMA: str = "Moving Average Filter"
grpOB: str = "Order Block"
grpTouch: str = "OB Touch Label"
grpTrade: str = "Trade Levels (SL/TP)"
grpDbg: str = "Debug"


@script.indicator("3CandleWarEng", overlay=True, max_lines_count=500, max_labels_count=500, max_boxes_count=500)
def main(
    showLines=input.bool(True, "Show C1 High/Low lines", group=grpLines),
    maxHistory=input.int(50, "Confirmed setups (C1-C2-C3 completed) to keep on chart", minval=5, maxval=200, group=grpLines),
    lineColor=input.color(color.new(color.gray, 60), "Line color (C1 waiting for C2)", group=grpLines),
    setupColor=input.color(color.new(color.fuchsia, 0), "Line color (C2 valid, waiting for C3)", group=grpLines),
    showBuy=input.bool(True, "Show BUY signals", group=grpSig),
    showSell=input.bool(True, "Show SELL signals (mirrored)", group=grpSig),
    buyColor=input.color(color.yellow, "Buy star color", group=grpSig),
    sellColor=input.color(color.red, "Sell star color", group=grpSig),
    closeToleranceATR=input.float(0.01, "C3 close tolerance vs C1 (in ATR, 0 = clean close)", minval=0, step=0.01, group=grpSig),
    useMaFilter=input.bool(True, "Enable trend filter with moving average", group=grpMA),
    maTF=input.timeframe("5", "MA timeframe", group=grpMA),
    maLen=input.int(20, "SMA period", minval=1, group=grpMA),
    maSrc: Series[float] = input.source(close, "Source", group=grpMA),
    showMaPlot=input.bool(True, "Show MA on chart", group=grpMA),
    maDynamicColor=input.bool(True, "Dynamic MA color based on trend", group=grpMA),
    maColorUp=input.color(color.lime, "MA color (price above)", group=grpMA),
    maColorDown=input.color(color.red, "MA color (price below)", group=grpMA),
    maColorFlat=input.color(color.aqua, "MA color (fixed, if dynamic off)", group=grpMA),
    obEnable=input.bool(True, "Enable Order Block detection", group=grpOB),
    showObBoxes=input.bool(True, "Show Order Block boxes on chart", group=grpOB),
    obRealtimeDraw=input.bool(True, "Draw OB on forming candle too (repainting)", group=grpOB),
    useDisplacement=input.bool(True, "Require displacement (strong breakout)", group=grpOB),
    atrLen=input.int(14, "ATR period (displacement)", minval=1, group=grpOB),
    dispMult=input.float(1.2, "ATR multiplier for displacement", minval=0.1, step=0.1, group=grpOB),
    obBoxCount=input.int(5, "Max OB per side on chart", minval=1, maxval=20, group=grpOB),
    obMitigateOnClose=input.bool(True, "Mitigation on close (otherwise on wick)", group=grpOB),
    obProximityATR=input.float(0.5, "'Nearby' margin (in ATR)", minval=0, step=0.1, group=grpOB),
    obBypassMaOnTouch=input.bool(True, "Bypass MA filter if C1 or C2 touch a matching OB", group=grpOB),
    obBorderTransp=input.int(70, "OB border transparency (0 = solid, 100 = invisible)", minval=0, maxval=100, group=grpOB),
    bullObColor=input.color(color.new(color.teal, 80), "Bullish OB box color", group=grpOB),
    bearObColor=input.color(color.new(color.orange, 80), "Bearish OB box color", group=grpOB),
    warnColor=input.color(color.new(color.fuchsia, 0), "Warning label color (opposite OB)", group=grpOB),
    showOBTouchLabel=input.bool(True, "Show 'OB' only on first touch of an important Order Block", group=grpTouch),
    obTouchMinSizeATR=input.float(1.0, "Minimum OB size to be 'important' (in ATR)", minval=0, step=0.1, group=grpTouch),
    obTouchMaxLabels=input.int(100, "Max OB Touch labels on chart", minval=5, maxval=500, group=grpTouch),
    showTradeBox=input.bool(True, "Draw SL/TP boxes on confirmed signal", group=grpTrade),
    rrRatio=input.float(2.0, "Take Profit ratio (R:R)", minval=0.5, step=0.5, group=grpTrade),
    minAtrStopMult=input.float(0.5, "Minimum SL distance beyond C1 (in ATR)", minval=0, step=0.1, group=grpTrade),
    tradeBoxBars=input.int(30, "Box extension to the right (bars)", minval=1, group=grpTrade),
    maxTradeBoxes=input.int(10, "Max trade boxes on chart", minval=1, maxval=50, group=grpTrade),
    tpBoxColor=input.color(color.new(color.green, 85), "Take Profit box color", group=grpTrade),
    slBoxColor=input.color(color.new(color.red, 85), "Stop Loss box color", group=grpTrade),
    tradeBorderTransp=input.int(40, "SL/TP box border transparency (0 = solid, 100 = invisible)", minval=0, maxval=100, group=grpTrade),
    entryLineColor=input.color(color.new(color.white, 20), "Entry line color", group=grpTrade),
    showTradeLabel=input.bool(False, "Show Entry/SL/TP label", group=grpTrade),
    dbgOB=input.bool(False, "Debug: show OB touch state on C1/C2 and C3 tolerance", group=grpDbg)
):
    state: Persistent[int] = 0
    c1High: Persistent[float] = na(float)
    c1Low: Persistent[float] = na(float)
    c1HiLine: Persistent[Line] = na(Line)
    c1LoLine: Persistent[Line] = na(Line)
    isBuySetup: Persistent[bool] = False
    isSellSetup: Persistent[bool] = False

    c1c2TouchedBullOB: Persistent[bool] = False
    c1c2TouchedBearOB: Persistent[bool] = False

    lastBullOBBar: Persistent[int] = -1
    lastBearOBBar: Persistent[int] = -1

    histHi: Persistent[list[Line]] = array.new_line()
    histLo: Persistent[list[Line]] = array.new_line()

    tpBoxes: Persistent[list[Box]] = array.new_box()
    slBoxes: Persistent[list[Box]] = array.new_box()
    entryLines: Persistent[list[Line]] = array.new_line()
    rrLabels: Persistent[list[Label]] = array.new_label()

    obTouchLabels: Persistent[list[Label]] = array.new_label()

    buySignal: bool = False
    sellSignal: bool = False
    buyNearOB: bool = False
    sellNearOB: bool = False
    buyWarnOB: bool = False
    sellWarnOB: bool = False

    maValue = request.security(syminfo.tickerid, maTF, ta.sma(maSrc, maLen), lookahead=barmerge.lookahead_off)

    maPlotColor = (maColorUp if close > maValue else maColorDown if close < maValue else maColorFlat) if maDynamicColor else maColorFlat

    plot(maValue if showMaPlot else na, title='SMA Filter', color=maPlotColor, linewidth=2)

    aboveMa = not useMaFilter or close > maValue
    belowMa = not useMaFilter or close < maValue

    bullBoxes: Persistent[list[Box]] = array.new_box()
    bullTop: Persistent[list[float]] = array.new_float()
    bullBottom: Persistent[list[float]] = array.new_float()
    bullTouched: Persistent[list[bool]] = array.new_bool()

    bearBoxes: Persistent[list[Box]] = array.new_box()
    bearTop: Persistent[list[float]] = array.new_float()
    bearBottom: Persistent[list[float]] = array.new_float()
    bearTouched: Persistent[list[bool]] = array.new_bool()

    atrVal = ta.atr(atrLen)

    if barstate.isconfirmed and obEnable:
        if array.size(bullBoxes) > 0:
            for i in pine_range(array.size(bullBoxes) - 1, 0):
                bx = array.get(bullBoxes, i)
                bot = array.get(bullBottom, i)
                box.set_right(bx, bar_index)
                mitigated = close < bot if obMitigateOnClose else low < bot
                if mitigated:
                    box.delete(bx)
                    array.remove(bullBoxes, i)
                    array.remove(bullTop, i)
                    array.remove(bullBottom, i)
                    array.remove(bullTouched, i)

        if array.size(bearBoxes) > 0:
            for i in pine_range(array.size(bearBoxes) - 1, 0):
                bx = array.get(bearBoxes, i)
                top = array.get(bearTop, i)
                box.set_right(bx, bar_index)
                mitigated = close > top if obMitigateOnClose else high > top
                if mitigated:
                    box.delete(bx)
                    array.remove(bearBoxes, i)
                    array.remove(bearTop, i)
                    array.remove(bearBottom, i)
                    array.remove(bearTouched, i)

    if obEnable and (obRealtimeDraw or barstate.isconfirmed):
        bullishOB = close[1] < open[1] and close > high[1] and (not useDisplacement or close - open > atrVal * dispMult)
        if bullishOB and bar_index != lastBullOBBar:
            obTop = high[1]
            obBot = low[1]
            newBoxBull = box.new(left=bar_index[1], top=obTop, right=bar_index, bottom=obBot, border_color=color.new(bullObColor, obBorderTransp), bgcolor=bullObColor if showObBoxes else na)
            array.push(bullBoxes, newBoxBull)
            array.push(bullTop, obTop)
            array.push(bullBottom, obBot)
            array.push(bullTouched, False)
            lastBullOBBar = bar_index
            if array.size(bullBoxes) > obBoxCount:
                box.delete(array.shift(bullBoxes))
                array.shift(bullTop)
                array.shift(bullBottom)
                array.shift(bullTouched)

        bearishOB = close[1] > open[1] and close < low[1] and (not useDisplacement or open - close > atrVal * dispMult)
        if bearishOB and bar_index != lastBearOBBar:
            obTop = high[1]
            obBot = low[1]
            newBoxBear = box.new(left=bar_index[1], top=obTop, right=bar_index, bottom=obBot, border_color=color.new(bearObColor, obBorderTransp), bgcolor=bearObColor if showObBoxes else na)
            array.push(bearBoxes, newBoxBear)
            array.push(bearTop, obTop)
            array.push(bearBottom, obBot)
            array.push(bearTouched, False)
            lastBearOBBar = bar_index
            if array.size(bearBoxes) > obBoxCount:
                box.delete(array.shift(bearBoxes))
                array.shift(bearTop)
                array.shift(bearBottom)
                array.shift(bearTouched)

    def f_nearAnyBox(tops, bottoms, px, margin):
        found: bool = False
        if array.size(tops) > 0:
            for i in pine_range(0, array.size(tops) - 1):
                t = array.get(tops, i)
                b = array.get(bottoms, i)
                if px <= t + margin and px >= b - margin:
                    found = True
        return found

    def f_overlapsAnyBox(tops, bottoms, lo, hi, margin):
        found: bool = False
        if array.size(tops) > 0:
            for i in pine_range(0, array.size(tops) - 1):
                t = array.get(tops, i)
                b = array.get(bottoms, i)
                if hi >= b - margin and lo <= t + margin:
                    found = True
        return found

    def f_checkImportantTouch(tops, bottoms, touched, lo, hi, minSizeATR, atrV):
        anyNewTouch: bool = False
        if array.size(tops) > 0:
            for i in pine_range(0, array.size(tops) - 1):
                already = array.get(touched, i)
                if not already:
                    t = array.get(tops, i)
                    b = array.get(bottoms, i)
                    sizeOK = t - b >= atrV * minSizeATR
                    overlap = hi >= b and lo <= t
                    if sizeOK and overlap:
                        array.set(touched, i, True)
                        anyNewTouch = True
        return anyNewTouch

    if showOBTouchLabel and obEnable and showObBoxes:
        newBullTouch = f_checkImportantTouch(bullTop, bullBottom, bullTouched, low, high, obTouchMinSizeATR, atrVal)
        newBearTouch = f_checkImportantTouch(bearTop, bearBottom, bearTouched, low, high, obTouchMinSizeATR, atrVal)
        if newBullTouch or newBearTouch:
            obTouchLbl = label.new(bar_index, high, text='OB', style=label.style_label_down, color=color.new(color.white, 100), textcolor=color.white, size=size.tiny)
            array.push(obTouchLabels, obTouchLbl)
            if array.size(obTouchLabels) > obTouchMaxLabels:
                label.delete(array.shift(obTouchLabels))

    def f_drawTrade(isLong, entryPx, slPx):
        riskDist = math.abs(entryPx - slPx)
        tpPx = entryPx + riskDist * rrRatio if isLong else entryPx - riskDist * rrRatio
        boxRight = bar_index + tradeBoxBars

        tBox = box.new(left=bar_index, top=tpPx if isLong else entryPx, right=boxRight, bottom=entryPx if isLong else tpPx, border_color=color.new(color.green, tradeBorderTransp), bgcolor=tpBoxColor)
        sBox = box.new(left=bar_index, top=entryPx if isLong else slPx, right=boxRight, bottom=slPx if isLong else entryPx, border_color=color.new(color.red, tradeBorderTransp), bgcolor=slBoxColor)
        eLine = line.new(bar_index, entryPx, boxRight, entryPx, color=entryLineColor, width=1, style=line.style_dashed)
        rrTxt = 'Entry: ' + string.tostring(entryPx, '#.#####') + '\nSL: ' + string.tostring(slPx, '#.#####') + '\nTP: ' + string.tostring(tpPx, '#.#####') + '\nR:R = 1:' + string.tostring(rrRatio, '#.#')
        lbl = label.new(boxRight, entryPx, text=rrTxt, style=label.style_label_left, color=color.new(color.black, 100), textcolor=color.white if showTradeLabel else color.new(color.white, 100), size=size.tiny)

        array.push(tpBoxes, tBox)
        array.push(slBoxes, sBox)
        array.push(entryLines, eLine)
        array.push(rrLabels, lbl)

        __block_result__ = na
        if array.size(tpBoxes) > maxTradeBoxes:
            box.delete(array.shift(tpBoxes))
            box.delete(array.shift(slBoxes))
            line.delete(array.shift(entryLines))
            __block_result__ = label.delete(array.shift(rrLabels))
        return __block_result__

    if state == 2:
        margin = atrVal * obProximityATR
        tolC3 = atrVal * closeToleranceATR

        buyBase = isBuySetup and low >= c1Low and (high >= c1High) and (close > c1High - tolC3)
        sellBase = isSellSetup and high <= c1High and (low <= c1Low) and (close < c1Low + tolC3)

        buyNearOBcheck = obEnable and buyBase and f_nearAnyBox(bullTop, bullBottom, close, margin)
        sellNearOBcheck = obEnable and sellBase and f_nearAnyBox(bearTop, bearBottom, close, margin)

        buyWarnOBcheck = obEnable and buyBase and f_nearAnyBox(bearTop, bearBottom, close, margin)
        sellWarnOBcheck = obEnable and sellBase and f_nearAnyBox(bullTop, bullBottom, close, margin)

        buyBypassMa = obEnable and obBypassMaOnTouch and c1c2TouchedBullOB
        sellBypassMa = obEnable and obBypassMaOnTouch and c1c2TouchedBearOB

        buyConfirm = buyBase and (aboveMa or buyNearOBcheck or buyBypassMa)
        sellConfirm = sellBase and (belowMa or sellNearOBcheck or sellBypassMa)

        if buyConfirm and showBuy:
            buySignal = True
            buyNearOB = buyNearOBcheck
            buyWarnOB = buyWarnOBcheck
        if sellConfirm and showSell:
            sellSignal = True
            sellNearOB = sellNearOBcheck
            sellWarnOB = sellWarnOBcheck

    if barstate.isconfirmed:
        if state == 0:
            c1High = high
            c1Low = low
            c1c2TouchedBullOB = False
            c1c2TouchedBearOB = False
            if obEnable:
                marginC1 = atrVal * obProximityATR
                if f_overlapsAnyBox(bullTop, bullBottom, low, high, marginC1):
                    c1c2TouchedBullOB = True
                if f_overlapsAnyBox(bearTop, bearBottom, low, high, marginC1):
                    c1c2TouchedBearOB = True
            if showLines:
                c1HiLine = line.new(bar_index, high, bar_index + 2, high, xloc=xloc.bar_index, color=lineColor, width=1)
                c1LoLine = line.new(bar_index, low, bar_index + 2, low, xloc=xloc.bar_index, color=lineColor, width=1)
            state = 1
        elif state == 1:
            brokeDown = low < c1Low
            brokeUp = high > c1High
            reclaimed = close >= c1Low and close <= c1High
            buySetup = brokeDown and (not brokeUp) and reclaimed
            sellSetup = brokeUp and (not brokeDown) and reclaimed

            if obEnable and (buySetup or sellSetup):
                marginC2 = atrVal * obProximityATR
                if f_overlapsAnyBox(bullTop, bullBottom, low, high, marginC2):
                    c1c2TouchedBullOB = True
                if f_overlapsAnyBox(bearTop, bearBottom, low, high, marginC2):
                    c1c2TouchedBearOB = True

            if buySetup or sellSetup:
                isBuySetup = buySetup
                isSellSetup = sellSetup
                if showLines and (not na(c1HiLine)):
                    line.set_color(c1HiLine, setupColor)
                    line.set_color(c1LoLine, setupColor)
                state = 2
            else:
                if not na(c1HiLine):
                    line.delete(c1HiLine)
                    line.delete(c1LoLine)
                c1High = high
                c1Low = low
                c1c2TouchedBullOB = False
                c1c2TouchedBearOB = False
                if obEnable:
                    marginC1 = atrVal * obProximityATR
                    if f_overlapsAnyBox(bullTop, bullBottom, low, high, marginC1):
                        c1c2TouchedBullOB = True
                    if f_overlapsAnyBox(bearTop, bearBottom, low, high, marginC1):
                        c1c2TouchedBearOB = True
                if showLines:
                    c1HiLine = line.new(bar_index, high, bar_index + 2, high, xloc=xloc.bar_index, color=lineColor, width=1)
                    c1LoLine = line.new(bar_index, low, bar_index + 2, low, xloc=xloc.bar_index, color=lineColor, width=1)
                else:
                    c1HiLine = na
                    c1LoLine = na
                state = 1
        elif state == 2:
            margin = atrVal * obProximityATR
            tolC3F = atrVal * closeToleranceATR

            buyBaseFinal = isBuySetup and low >= c1Low and (high >= c1High) and (close > c1High - tolC3F)
            sellBaseFinal = isSellSetup and high <= c1High and (low <= c1Low) and (close < c1Low + tolC3F)

            buyNearOBFinal = obEnable and buyBaseFinal and f_nearAnyBox(bullTop, bullBottom, close, margin)
            sellNearOBFinal = obEnable and sellBaseFinal and f_nearAnyBox(bearTop, bearBottom, close, margin)

            buyBypassMaFinal = obEnable and obBypassMaOnTouch and c1c2TouchedBullOB
            sellBypassMaFinal = obEnable and obBypassMaOnTouch and c1c2TouchedBearOB

            buyConfirmFinal = buyBaseFinal and (aboveMa or buyNearOBFinal or buyBypassMaFinal)
            sellConfirmFinal = sellBaseFinal and (belowMa or sellNearOBFinal or sellBypassMaFinal)

            if dbgOB:
                label.new(bar_index, high, text='C1C2 BullOB=' + string.tostring(c1c2TouchedBullOB) + '\nC1C2 BearOB=' + string.tostring(c1c2TouchedBearOB) + '\nC1 low=' + string.tostring(c1Low, '#.#####') + ' C1 high=' + string.tostring(c1High, '#.#####') + '\nC3 low=' + string.tostring(low, '#.#####') + ' close=' + string.tostring(close, '#.#####') + '\ntol=' + string.tostring(tolC3F, '#.#####') + '\nsellBase=' + string.tostring(sellBaseFinal) + ' buyBase=' + string.tostring(buyBaseFinal) + '\nsellConfirm=' + string.tostring(sellConfirmFinal) + ' buyConfirm=' + string.tostring(buyConfirmFinal), style=label.style_label_down, color=color.new(color.blue, 60), textcolor=color.white, size=size.tiny)

            if showTradeBox and buyConfirmFinal:
                slPx = c1Low - atrVal * minAtrStopMult
                f_drawTrade(True, close, slPx)

            if showTradeBox and sellConfirmFinal:
                slPx = c1High + atrVal * minAtrStopMult
                f_drawTrade(False, close, slPx)

            if buyConfirmFinal or sellConfirmFinal:
                if not na(c1HiLine):
                    array.push(histHi, c1HiLine)
                    array.push(histLo, c1LoLine)
                    while array.size(histHi) > maxHistory:
                        line.delete(array.shift(histHi))
                        line.delete(array.shift(histLo))
                isBuySetup = False
                isSellSetup = False
                c1c2TouchedBullOB = False
                c1c2TouchedBearOB = False
                state = 0
            else:
                if not na(c1HiLine):
                    line.delete(c1HiLine)
                    line.delete(c1LoLine)
                isBuySetup = False
                isSellSetup = False
                c1High = high
                c1Low = low
                c1c2TouchedBullOB = False
                c1c2TouchedBearOB = False
                if obEnable:
                    marginC1 = atrVal * obProximityATR
                    if f_overlapsAnyBox(bullTop, bullBottom, low, high, marginC1):
                        c1c2TouchedBullOB = True
                    if f_overlapsAnyBox(bearTop, bearBottom, low, high, marginC1):
                        c1c2TouchedBearOB = True
                if showLines:
                    c1HiLine = line.new(bar_index, high, bar_index + 2, high, xloc=xloc.bar_index, color=lineColor, width=1)
                    c1LoLine = line.new(bar_index, low, bar_index + 2, low, xloc=xloc.bar_index, color=lineColor, width=1)
                else:
                    c1HiLine = na
                    c1LoLine = na
                state = 1

    plotchar(buySignal, title='Buy Star', char='★', location=location.belowbar, color=buyColor, size=size.small)
    plotchar(sellSignal, title='Sell Star', char='★', location=location.abovebar, color=sellColor, size=size.small)

    if buyNearOB:
        label.new(bar_index, low, text='OB', style=label.style_label_up, color=color.new(bullObColor, 0), textcolor=color.white, size=size.tiny)
    if sellNearOB:
        label.new(bar_index, high, text='OB', style=label.style_label_down, color=color.new(bearObColor, 0), textcolor=color.white, size=size.tiny)

    if buyWarnOB:
        label.new(bar_index, high, text='⚠OB', style=label.style_label_down, color=warnColor, textcolor=color.white, size=size.tiny)
    if sellWarnOB:
        label.new(bar_index, low, text='⚠OB', style=label.style_label_up, color=warnColor, textcolor=color.white, size=size.tiny)

    if buySignal:
        alert('BUY confirmed on ' + syminfo.ticker, alert.freq_once_per_bar)
    if sellSignal:
        alert('SELL confirmed on ' + syminfo.ticker, alert.freq_once_per_bar)
    if buyNearOB:
        alert('BUY confirmed + Order Block confluence on ' + syminfo.ticker, alert.freq_once_per_bar)
    if sellNearOB:
        alert('SELL confirmed + Order Block confluence on ' + syminfo.ticker, alert.freq_once_per_bar)
    if buyWarnOB:
        alert('WARNING: BUY near a bearish Order Block (possible reversal) on ' + syminfo.ticker, alert.freq_once_per_bar)
    if sellWarnOB:
        alert('WARNING: SELL near a bullish Order Block (possible reversal) on ' + syminfo.ticker, alert.freq_once_per_bar)

    alertcondition(isBuySetup and state == 2, title='Buy Setup Pending', message='Low sweep + reclaim: waiting for C3 confirmation')
    alertcondition(isSellSetup and state == 2, title='Sell Setup Pending', message='High sweep + reclaim: waiting for C3 confirmation')
    alertcondition(buySignal, title='Buy Confirmed', message='C3 confirmed: BUY pattern completed')
    alertcondition(sellSignal, title='Sell Confirmed', message='C3 confirmed: SELL pattern completed')
    alertcondition(buyNearOB, title='Buy + Order Block', message='BUY confirmed in confluence with Order Block')
    alertcondition(sellNearOB, title='Sell + Order Block', message='SELL confirmed in confluence with Order Block')
    alertcondition(buyWarnOB, title='Buy - Opposite OB Warning', message='BUY near a bearish Order Block: reversal risk')
    alertcondition(sellWarnOB, title='Sell - Opposite OB Warning', message='SELL near a bullish Order Block: reversal risk')
    alertcondition(showOBTouchLabel, title='Important OB Touch', message='First candle touching an important Order Block')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)