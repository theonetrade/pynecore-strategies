"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, bar_index, barmerge, box, close, color, high, input,
    label, line, location, low, math, na, open, plot, plotshape, request, script, shape, size,
    string, syminfo, ta, timeframe
)
from pynecore.types import Box, Label, Line, Persistent

grp_flt: str = "XAUUSD Distance Filters ($)"
grp_ob: str = "Order Block Settings"
grp_sr: str = "Support & Resistance Settings"
grp_piv: str = "Daily Pivots & Open Settings"
grp_fvg: str = "Fair Value Gap (FVG) Imbalances"
grp_sig: str = "Signals & Risk Management"
grp_vwap: str = "VWAP & EMA 9 Overlay Settings"


@script.indicator("XAUUSD Ultimate Trading Suite - by Siwon Battambang Cambodia", overlay=True, max_boxes_count=100, max_lines_count=50)
def main(
    minMove=input.float(15.0, "Min Gold Move ($) for Buy/Sell Signal", minval=1.0, group=grp_flt),
    majorMove=input.float(30.0, "Min Gold Move ($) for Double Diamond", minval=1.0, group=grp_flt),
    col_sup=input.color(color.new(color.red, 85), "Supply OB Color", group=grp_ob),
    col_dem=input.color(color.new(color.green, 85), "Demand OB Color", group=grp_ob),
    border_s=input.color(color.red, "Supply OB Border", group=grp_ob),
    border_d=input.color(color.green, "Demand OB Border", group=grp_ob),
    col_r=input.color(color.red, "Resistance Line Color", group=grp_sr),
    col_s=input.color(color.green, "Support Line Color", group=grp_sr),
    width_sr=input.int(1, "S/R Line Width", minval=1, maxval=4, group=grp_sr),
    col_p=input.color(color.blue, "Pivot (P) Color", group=grp_piv),
    col_op=input.color(color.orange, "Open Price (OP) Color", group=grp_piv),
    width_piv=input.int(2, "Pivot & OP Line Width", minval=1, maxval=4, group=grp_piv),
    showFVG=input.bool(True, "Plot Bullish/Bearish FVGs", group=grp_fvg),
    col_fvg_b=input.color(color.new(color.green, 90), "Bullish FVG Color", group=grp_fvg),
    col_fvg_s=input.color(color.new(color.red, 90), "Bearish FVG Color", group=grp_fvg),
    showTP_SL=input.bool(True, "Show TP/SL Target Lines", group=grp_sig),
    useEmaFlt=input.bool(False, "Filter Signals by 200 EMA Trend", group=grp_sig),
    showEmaLine=input.bool(True, "Plot 200 EMA Line on Chart", group=grp_sig),
    col_ema=input.color(color.purple, "200 EMA Line Color", group=grp_sig),
    width_ema=input.int(2, "200 EMA Line Width", minval=1, maxval=4, group=grp_sig),
    showVwapEma=input.bool(True, "Show VWAP & EMA 9", group=grp_vwap),
    col_vwap=input.color(color.red, "VWAP Color (Red Line)", group=grp_vwap),
    col_ema9=input.color(color.green, "EMA 9 Color (Green Line)", group=grp_vwap),
    arrowSizeInput=input.string("Normal", "Crossover Arrow Size", options=("Tiny", "Small", "Normal", "Large", "Huge"), group=grp_vwap)
):
    color_cyan = color.rgb(0, 229, 255)

    def f_get_tf_label():
        __block_result__ = na
        if timeframe.isminutes:
            m = timeframe.multiplier
            __block_result__ = '1h' if m == 60 else '4h' if m == 240 else string.tostring(m) + 'm'
        else:
            __block_result__ = timeframe.period
        return __block_result__

    tfLabel = f_get_tf_label()

    ema200 = ta.ema(close, 200)
    plot(ema200 if showEmaLine else na, title='200 EMA', color=col_ema, linewidth=width_ema)

    vwapVal = ta.vwap(close)
    ema9Val = ta.ema(close, 9)

    plot(vwapVal if showVwapEma else na, title='VWAP (Red Line)', color=col_vwap, linewidth=2)
    plot(ema9Val if showVwapEma else na, title='EMA 9 (Green Line)', color=col_ema9, linewidth=2)

    ema9CrossAboveVwap = ta.crossover(ema9Val, vwapVal)
    ema9CrossUnderVwap = ta.crossunder(ema9Val, vwapVal)

    plotshape(ema9CrossAboveVwap and arrowSizeInput == 'Tiny', title='Bullish Cross Tiny', style=shape.triangleup, location=location.belowbar, color=color.green, size=size.tiny)
    plotshape(ema9CrossAboveVwap and arrowSizeInput == 'Small', title='Bullish Cross Small', style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small)
    plotshape(ema9CrossAboveVwap and arrowSizeInput == 'Normal', title='Bullish Cross Normal', style=shape.triangleup, location=location.belowbar, color=color.green, size=size.normal)
    plotshape(ema9CrossAboveVwap and arrowSizeInput == 'Large', title='Bullish Cross Large', style=shape.triangleup, location=location.belowbar, color=color.green, size=size.large)
    plotshape(ema9CrossAboveVwap and arrowSizeInput == 'Huge', title='Bullish Cross Huge', style=shape.triangleup, location=location.belowbar, color=color.green, size=size.huge)

    plotshape(ema9CrossUnderVwap and arrowSizeInput == 'Tiny', title='Bearish Cross Tiny', style=shape.triangledown, location=location.abovebar, color=color.red, size=size.tiny)
    plotshape(ema9CrossUnderVwap and arrowSizeInput == 'Small', title='Bearish Cross Small', style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small)
    plotshape(ema9CrossUnderVwap and arrowSizeInput == 'Normal', title='Bearish Cross Normal', style=shape.triangledown, location=location.abovebar, color=color.red, size=size.normal)
    plotshape(ema9CrossUnderVwap and arrowSizeInput == 'Large', title='Bearish Cross Large', style=shape.triangledown, location=location.abovebar, color=color.red, size=size.large)
    plotshape(ema9CrossUnderVwap and arrowSizeInput == 'Huge', title='Bearish Cross Huge', style=shape.triangledown, location=location.abovebar, color=color.red, size=size.huge)

    pivotLen = 20 if timeframe.isminutes and timeframe.multiplier >= 60 else 15
    pHi = ta.pivothigh(high, pivotLen, pivotLen)
    pLo = ta.pivotlow(low, pivotLen, pivotLen)

    activeSupplyOB: Persistent[Box] = na(Box)
    activeDemandOB: Persistent[Box] = na(Box)

    if not na(pHi):
        box.delete(activeSupplyOB)
        activeSupplyOB = box.new(left=bar_index - pivotLen, top=high[pivotLen], right=bar_index + 5, bottom=low[pivotLen], bgcolor=col_sup, border_color=border_s)

    if not na(pLo):
        box.delete(activeDemandOB)
        activeDemandOB = box.new(left=bar_index - pivotLen, top=low[pivotLen], right=bar_index + 5, bottom=low[pivotLen], bgcolor=col_dem, border_color=border_d)

    if not na(activeSupplyOB):
        box.set_right(activeSupplyOB, bar_index + 5)
    if not na(activeDemandOB):
        box.set_right(activeDemandOB, bar_index + 5)

    sTop = box.get_top(activeSupplyOB) if not na(activeSupplyOB) else na
    sBot = box.get_bottom(activeSupplyOB) if not na(activeSupplyOB) else na
    dTop = box.get_top(activeDemandOB) if not na(activeDemandOB) else na
    dBot = box.get_bottom(activeDemandOB) if not na(activeDemandOB) else na

    activeResistance: Persistent[float] = na(float)
    activeSupport: Persistent[float] = na(float)

    srPivotHi = ta.pivothigh(high, 10, 10)
    srPivotLo = ta.pivotlow(low, 10, 10)

    if not na(srPivotHi):
        activeResistance = high[10]

    if not na(srPivotLo):
        activeSupport = low[10]

    if na(activeResistance):
        activeResistance = inline_series(ta.highest(high, 20), 1)

    if na(activeSupport):
        activeSupport = inline_series(ta.lowest(low, 20), 1)

    lineR: Persistent[Line] = na(Line)
    lineS: Persistent[Line] = na(Line)
    lblR: Persistent[Label] = na(Label)
    lblS: Persistent[Label] = na(Label)

    line.delete(lineR)
    line.delete(lineS)
    label.delete(lblR)
    label.delete(lblS)

    if not na(activeResistance):
        lineR = line.new(x1=bar_index - 15, y1=activeResistance, x2=bar_index + 5, y2=activeResistance, color=col_r, width=width_sr)
        lblR = label.new(x=bar_index + 3, y=activeResistance, text=tfLabel + ' R', color=color.new(color.white, 100), textcolor=col_r, style=label.style_label_left)

    if not na(activeSupport):
        lineS = line.new(x1=bar_index - 15, y1=activeSupport, x2=bar_index + 5, y2=activeSupport, color=col_s, width=width_sr)
        lblS = label.new(x=bar_index + 3, y=activeSupport, text=tfLabel + ' S', color=color.new(color.white, 100), textcolor=col_s, style=label.style_label_left)

    isBullFVG = low > high[2]
    isBearFVG = high < low[2]

    lastBullFvgTop: Persistent[float] = na(float)
    lastBullFvgBot: Persistent[float] = na(float)
    lastBearFvgTop: Persistent[float] = na(float)
    lastBearFvgBot: Persistent[float] = na(float)

    if showFVG and isBullFVG:
        box.new(left=bar_index - 2, top=low, right=bar_index + 5, bottom=high[2], bgcolor=col_fvg_b, border_color=color.new(color.green, 50))
        lastBullFvgTop = low
        lastBullFvgBot = high[2]

    if showFVG and isBearFVG:
        box.new(left=bar_index - 2, top=low[2], right=bar_index + 5, bottom=high, bgcolor=col_fvg_s, border_color=color.new(color.red, 50))
        lastBearFvgTop = low[2]
        lastBearFvgBot = high

    fillBullFvg = not na(lastBullFvgTop) and low <= lastBullFvgTop and (high >= lastBullFvgBot)
    fillBearFvg = not na(lastBearFvgTop) and high >= lastBearFvgBot and (low <= lastBearFvgTop)

    dOpen = request.security(syminfo.tickerid, 'D', open, barmerge.gaps_off, barmerge.lookahead_on)
    dHigh, dLow, dClose = request.security(syminfo.tickerid, 'D', (high[1], low[1], close[1]), barmerge.gaps_off, barmerge.lookahead_on)

    pivotPoint = (dHigh + dLow + dClose) / 3.0

    plot(pivotPoint, title='P', color=col_p, linewidth=width_piv, style=plot.style_linebr)
    plot(dOpen, title='OP', color=col_op, linewidth=width_piv, style=plot.style_linebr)

    lblP: Persistent[Label] = na(Label)
    lblOP: Persistent[Label] = na(Label)

    label.delete(lblP)
    label.delete(lblOP)

    lblP = label.new(x=bar_index + 3, y=pivotPoint, text='P', color=color.new(color.white, 100), textcolor=col_p, style=label.style_label_left)
    lblOP = label.new(x=bar_index + 3, y=dOpen, text='OP', color=color.new(color.white, 100), textcolor=col_op, style=label.style_label_left)

    extremeHigh: Persistent[float] = high
    extremeLow: Persistent[float] = low
    lastState: Persistent[int] = 0

    rawBuySignal: bool = False
    rawSellSignal: bool = False
    buySignal: bool = False
    sellSignal: bool = False
    bullDiamond: bool = False
    bearDiamond: bool = False

    if high > extremeHigh:
        extremeHigh = high

    if low < extremeLow:
        extremeLow = low

    if lastState <= 0 and extremeHigh - low >= minMove and (close > open):
        rawBuySignal = True
        lastState = 1
        if extremeHigh - low >= majorMove:
            bullDiamond = True
        extremeLow = low
        extremeHigh = high
    elif lastState >= 0 and high - extremeLow >= minMove and (close < open):
        rawSellSignal = True
        lastState = -1
        if high - extremeLow >= majorMove:
            bearDiamond = True
        extremeHigh = high
        extremeLow = low

    buySignal = rawBuySignal and (not useEmaFlt or close > ema200)
    sellSignal = rawSellSignal and (not useEmaFlt or close < ema200)

    bullDiamond = bullDiamond and buySignal
    bearDiamond = bearDiamond and sellSignal

    plotshape(buySignal, title='BUY Signal', style=shape.labelup, location=location.belowbar, color=color.green, text='BUY', textcolor=color.white, size=size.small)
    plotshape(sellSignal, title='SELL Signal', style=shape.labeldown, location=location.abovebar, color=color.red, text='SELL', textcolor=color.white, size=size.small)

    plotshape(bullDiamond, title='Bullish Double Diamond Top', style=shape.diamond, location=location.belowbar, color=color_cyan, size=size.normal)
    plotshape(bullDiamond, title='Bullish Double Diamond Bottom', style=shape.diamond, location=location.belowbar, color=color_cyan, size=size.small)

    plotshape(bearDiamond, title='Bearish Double Diamond Top', style=shape.diamond, location=location.abovebar, color=color.orange, size=size.normal)
    plotshape(bearDiamond, title='Bearish Double Diamond Bottom', style=shape.diamond, location=location.abovebar, color=color.orange, size=size.small)

    atrVal = ta.atr(14)
    l_sl: Persistent[Line] = na(Line)
    l_tp1: Persistent[Line] = na(Line)
    l_tp2: Persistent[Line] = na(Line)
    l_tp3: Persistent[Line] = na(Line)

    if showTP_SL and (buySignal or sellSignal):
        line.delete(l_sl)
        line.delete(l_tp1)
        line.delete(l_tp2)
        line.delete(l_tp3)

        entryPrice = close
        slDistance = atrVal * 1.5

        if buySignal:
            slPrice = entryPrice - slDistance
            tp1Price = entryPrice + slDistance * 1.5
            tp2Price = entryPrice + slDistance * 2.0
            tp3Price = entryPrice + slDistance * 3.0

            l_sl = line.new(bar_index, slPrice, bar_index + 10, slPrice, color=color.red, width=2)
            l_tp1 = line.new(bar_index, tp1Price, bar_index + 10, tp1Price, color=color.green, width=1, style=line.style_dashed)
            l_tp2 = line.new(bar_index, tp2Price, bar_index + 10, tp2Price, color=color.green, width=1, style=line.style_dashed)
            l_tp3 = line.new(bar_index, tp3Price, bar_index + 10, tp3Price, color=color.green, width=2)

        if sellSignal:
            slPrice = entryPrice + slDistance
            tp1Price = entryPrice - slDistance * 1.5
            tp2Price = entryPrice - slDistance * 2.0
            tp3Price = entryPrice - slDistance * 3.0

            l_sl = line.new(bar_index, slPrice, bar_index + 10, slPrice, color=color.red, width=2)
            l_tp1 = line.new(bar_index, tp1Price, bar_index + 10, tp1Price, color=color.green, width=1, style=line.style_dashed)
            l_tp2 = line.new(bar_index, tp2Price, bar_index + 10, tp2Price, color=color.green, width=1, style=line.style_dashed)
            l_tp3 = line.new(bar_index, tp3Price, bar_index + 10, tp3Price, color=color.green, width=2)

    candleRange = high - low
    bullWick = candleRange > 0 and math.min(open, close) - low >= candleRange * 0.35
    bearWick = candleRange > 0 and high - math.max(open, close) >= candleRange * 0.35

    touchResistance = not na(activeResistance) and high >= activeResistance and (low <= activeResistance)
    touchSupport = not na(activeSupport) and low <= activeSupport and (high >= activeSupport)
    touchSupplyOB = not na(sBot) and high >= sBot and (low <= sTop)
    touchDemandOB = not na(dTop) and low <= dTop and (high >= dBot)
    touchLevel = touchResistance or touchSupport or touchSupplyOB or touchDemandOB

    breakResistance = not na(activeResistance) and ta.crossover(close, activeResistance)
    breakSupport = not na(activeSupport) and ta.crossunder(close, activeSupport)
    breakSupplyOB = not na(sTop) and ta.crossover(close, sTop)
    breakDemandOB = not na(dBot) and ta.crossunder(close, dBot)
    breakLevel = breakResistance or breakSupport or breakSupplyOB or breakDemandOB

    rejectResistance = touchResistance and bearWick and (close < activeResistance)
    rejectSupport = touchSupport and bullWick and (close > activeSupport)
    rejectSupplyOB = touchSupplyOB and bearWick and (close < sBot)
    rejectDemandOB = touchDemandOB and bullWick and (close > dTop)
    rejectLevel = rejectResistance or rejectSupport or rejectSupplyOB or rejectDemandOB

    alertcondition(buySignal, '1. BUY Signal', 'XAUUSD: BUY Signal Triggered!')
    alertcondition(sellSignal, '2. SELL Signal', 'XAUUSD: SELL Signal Triggered!')
    alertcondition(bullDiamond or bearDiamond, '3. Double Diamond Signal', 'XAUUSD: Double Diamond Signal Triggered!')

    alertcondition(touchLevel, '4. Price Touch Level (S/R or OB)', 'XAUUSD Alert: Price touched S/R or Order Block!')
    alertcondition(breakLevel, '5. Price Break Level (S/R or OB)', 'XAUUSD Alert: Price BROKE S/R or Order Block!')
    alertcondition(rejectLevel, '6. Price REJECTION Level (S/R or OB)', 'XAUUSD Alert: Price REJECTED S/R or Order Block!')

    alertcondition(isBullFVG, '7. Bullish FVG Formed', 'XAUUSD Alert: New Bullish Fair Value Gap (FVG) Formed!')
    alertcondition(isBearFVG, '8. Bearish FVG Formed', 'XAUUSD Alert: New Bearish Fair Value Gap (FVG) Formed!')

    alertcondition(fillBullFvg, '9. Price Filling Bullish FVG', 'XAUUSD Alert: Price entered and started filling Bullish FVG!')
    alertcondition(fillBearFvg, '10. Price Filling Bearish FVG', 'XAUUSD Alert: Price entered and started filling Bearish FVG!')

    alertcondition(ema9CrossAboveVwap, '11. EMA 9 Cross Above VWAP (Bullish)', 'XAUUSD Alert: EMA 9 crossed ABOVE VWAP!')
    alertcondition(ema9CrossUnderVwap, '12. EMA 9 Cross Under VWAP (Bearish)', 'XAUUSD Alert: EMA 9 crossed UNDER VWAP!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)