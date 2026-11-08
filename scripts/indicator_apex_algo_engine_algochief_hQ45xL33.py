"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, barstate, bgcolor, box,
    close, color, fill, high, input, label, line, location, low, math, na, nz, open, plot,
    plotshape, position, script, shape, size, string, syminfo, ta, table
)
from pynecore.types import Box, Color, Line, Persistent, PersistentSeries, Table

grp_signals: str = "═══ SIGNAL CONTROLS (CLEAN & PROFESSIONAL) ═══"
grp_candles: str = "═══ FULL TREND CANDLE COLORING ═══"
grp_cloud: str = "═══ REVERSAL CLOUD (EQUILIBRIUM & DISPERSION) ═══"
grp_extra: str = "═══ OPTIONAL CONTRARIAN TOOLS (OFF BY DEFAULT) ═══"
grp_rm: str = "═══ RISK MANAGEMENT & DASHBOARD HUD ═══"


@script.indicator("Apex Algo Engine [AlgoChief]", overlay=True, max_lines_count=500, max_boxes_count=500, max_labels_count=500)
def main(
    signalMode=input.string("Strong Signals Only (Ultra Clean)", "Signal Display Mode", options=("Strong Signals Only (Ultra Clean)", "All Confirmed Trend Signals", "All Signals (Unfiltered)"), group=grp_signals, tooltip="Ultra Clean mode displays ONLY single high-probability 'Strong' badges per trend cycle (No clutter)"),
    filterSignalsByTrend=input.bool(True, "Strict Trend Tracker Alignment", group=grp_signals, tooltip="Buy signals only in Bull trends; Sell signals only in Bear trends"),
    trendMult=input.float(2.2, "Trend Sensitivity Multiplier", minval=0.5, step=0.1, group=grp_signals, tooltip="Higher = cleaner, longer-lasting trends; Lower = faster flips"),
    trendAtrLen=input.int(14, "Trend ATR Period", minval=1, group=grp_signals),
    showBarColors=input.bool(True, "Enable Full Trend Candle Colors", group=grp_candles, tooltip="Colors ALL candles Green in uptrends (even red candles), and ALL candles Red in downtrends (even green candles)"),
    solidTrendColors=input.bool(True, "Pure Solid Trend Color (Clean Flat Look)", group=grp_candles),
    showTrendBg=input.bool(True, "Enable Trend Background Tint", group=grp_candles),
    showCloud=input.bool(True, "Show Reversal Cloud", group=grp_cloud),
    eqLength=input.int(55, "Equilibrium Regression Length", minval=10, group=grp_cloud),
    smoothLength=input.int(8, "Cloud Smoothing Factor", minval=1, maxval=30, group=grp_cloud),
    atrCloudLen=input.int(21, "Weighted Volatility Length", minval=5, group=grp_cloud),
    cloudInnerDev=input.float(1.8, "Cloud Inner Band Deviation", step=0.1, group=grp_cloud),
    cloudOuterDev=input.float(3.3, "Cloud Outer Band Deviation", step=0.1, group=grp_cloud),
    showSniperSignals=input.bool(False, "Show Contrarian Sniper Badges", group=grp_extra, tooltip="Contrarian reversal badges. Keep OFF for a clean chart"),
    showExhaustionDots=input.bool(False, "Show Exhaustion Peak Dots", group=grp_extra, tooltip="Orange dots at extreme peaks. Keep OFF for a clean chart"),
    showSRZones=input.bool(False, "Show S/R Retest Zones", group=grp_extra, tooltip="Displays horizontal support/resistance boxes"),
    srPivotLen=input.int(20, "S/R Swing Pivot Length", minval=5, maxval=50, group=grp_extra),
    srZoneThicknessAtr=input.float(0.4, "Zone Thickness (ATR Mult)", step=0.05, group=grp_extra),
    showDashboard=input.bool(True, "Show Risk Management HUD", group=grp_rm),
    dashboardPos=input.string("Top Right", "Dashboard Position", options=("Top Right", "Bottom Right", "Top Left", "Bottom Left"), group=grp_rm),
    showTpSlLines=input.bool(True, "Show Active Trade SL / TP Lines", group=grp_rm),
    riskRewardRatio1=input.float(1.5, "Take Profit 1 (R:R)", minval=0.5, step=0.1, group=grp_rm),
    riskRewardRatio2=input.float(2.5, "Take Profit 2 (R:R)", minval=1.0, step=0.1, group=grp_rm),
    riskRewardRatio3=input.float(3.5, "Take Profit 3 (R:R)", minval=1.5, step=0.1, group=grp_rm)
):
    c_bull_bright: Color = color.new('#00E676')
    c_bull_dark: Color = color.new('#00A859')
    c_bear_bright: Color = color.new('#FF1744')
    c_bear_dark: Color = color.new('#B71C1C')
    c_sniper_buy: Color = color.new('#2962FF')
    c_sniper_sell: Color = color.new('#FFD600')
    c_exhaust_dot: Color = color.new('#FF9100')

    rawLinReg = ta.linreg(close, eqLength, 0)
    equilibrium = ta.wma(ta.wma(rawLinReg, smoothLength), smoothLength)

    weightedTr = ta.wma(ta.tr(True), atrCloudLen)
    priceChangeAbs = ta.wma(math.abs(close - close[1]), atrCloudLen)
    adaptiveVol = weightedTr * 0.65 + priceChangeAbs * 0.35

    cloudMidDev = (cloudInnerDev + cloudOuterDev) * 0.5
    cloudUpperInner = equilibrium + adaptiveVol * cloudInnerDev
    cloudUpperMid = equilibrium + adaptiveVol * cloudMidDev
    cloudUpperOuter = equilibrium + adaptiveVol * cloudOuterDev

    cloudLowerInner = equilibrium - adaptiveVol * cloudInnerDev
    cloudLowerMid = equilibrium - adaptiveVol * cloudMidDev
    cloudLowerOuter = equilibrium - adaptiveVol * cloudOuterDev

    p_uo = plot(cloudUpperOuter if showCloud else na, 'Cloud Upper Outer', color=color.new(c_bull_bright, 60), linewidth=1)
    p_um = plot(cloudUpperMid if showCloud else na, 'Cloud Upper Mid', color=color.new(c_bull_bright, 75), linewidth=1)
    p_ui = plot(cloudUpperInner if showCloud else na, 'Cloud Upper Inner', color=color.new(c_bull_dark, 70), linewidth=1)
    fill(p_uo, p_um, color=color.new(c_bull_bright, 70), title='Upper Cloud Outer Fill')
    fill(p_um, p_ui, color=color.new(c_bull_dark, 76), title='Upper Cloud Inner Fill')

    p_li = plot(cloudLowerInner if showCloud else na, 'Cloud Lower Inner', color=color.new(c_bear_dark, 70), linewidth=1)
    p_lm = plot(cloudLowerMid if showCloud else na, 'Cloud Lower Mid', color=color.new(c_bear_bright, 75), linewidth=1)
    p_lo = plot(cloudLowerOuter if showCloud else na, 'Cloud Lower Outer', color=color.new(c_bear_bright, 60), linewidth=1)
    fill(p_li, p_lm, color=color.new(c_bear_dark, 76), title='Lower Cloud Inner Fill')
    fill(p_lm, p_lo, color=color.new(c_bear_bright, 70), title='Lower Cloud Outer Fill')

    trendAtr = ta.wma(ta.tr, trendAtrLen)
    upperBound = high + trendAtr * trendMult
    lowerBound = low - trendAtr * trendMult

    trendTracker: PersistentSeries[float] = na(float)
    trendDirection: Persistent[int] = 1

    if na(trendTracker):
        trendTracker = lowerBound
        trendDirection = 1
    else:
        if trendDirection == 1:
            trendTracker = math.max(nz(trendTracker[1], lowerBound), lowerBound)
            if close < trendTracker:
                trendDirection = -1
                trendTracker = upperBound
        else:
            trendTracker = math.min(nz(trendTracker[1], upperBound), upperBound)
            if close > trendTracker:
                trendDirection = 1
                trendTracker = lowerBound

    plot(trendTracker if trendDirection == 1 else na, 'Trend Tracker (Bullish)', color=c_bull_bright, linewidth=2, style=plot.style_line)
    plot(trendTracker if trendDirection == -1 else na, 'Trend Tracker (Bearish)', color=c_bear_bright, linewidth=2, style=plot.style_line)

    bgCol: Color = color.new(c_bull_bright, 95) if trendDirection == 1 else color.new(c_bear_bright, 95)
    bgcolor(bgCol if showTrendBg else na, title='Trend Background Color')

    candleColor: Color = na(Color)

    if showBarColors:
        if trendDirection == 1:
            candleColor = c_bull_bright if solidTrendColors else c_bull_bright if close >= open else c_bull_dark
        else:
            candleColor = c_bear_bright if solidTrendColors else c_bear_bright if close <= open else c_bear_dark

    barcolor(candleColor if showBarColors else na, title='Full Trend Bar Color')

    trendFlippedBull = ta.crossover(close, trendTracker)
    trendFlippedBear = ta.crossunder(close, trendTracker)

    volMa = ta.sma(adaptiveVol, 20)
    isVolatilityExpanding = adaptiveVol > volMa * 1.05
    priceBreakoutBull = close > ta.highest(high[1], 5)
    priceBreakoutBear = close < ta.lowest(low[1], 5)

    activePosition: Persistent[int] = 0
    lastSignalBar: Persistent[int] = 0

    rawBullSignal: bool = trendFlippedBull or (trendDirection == 1 and activePosition != 1 and priceBreakoutBull and isVolatilityExpanding)
    rawBearSignal: bool = trendFlippedBear or (trendDirection == -1 and activePosition != -1 and priceBreakoutBear and isVolatilityExpanding)

    if filterSignalsByTrend:
        rawBullSignal = rawBullSignal and trendDirection == 1
        rawBearSignal = rawBearSignal and trendDirection == -1

    triggerBuy: bool = rawBullSignal and activePosition != 1
    triggerSell: bool = rawBearSignal and activePosition != -1

    tradeEntryPrice: Persistent[float] = na(float)
    tradeStopLoss: Persistent[float] = na(float)
    tradeTp1: Persistent[float] = na(float)
    tradeTp2: Persistent[float] = na(float)
    tradeTp3: Persistent[float] = na(float)

    if triggerBuy:
        activePosition = 1
        lastSignalBar = bar_index
        tradeEntryPrice = close
        tradeStopLoss = trendTracker if trendTracker < close else close - trendAtr * 1.5
        riskDist: float = math.max(tradeEntryPrice - tradeStopLoss, syminfo.mintick * 10)
        tradeTp1 = tradeEntryPrice + riskDist * riskRewardRatio1
        tradeTp2 = tradeEntryPrice + riskDist * riskRewardRatio2
        tradeTp3 = tradeEntryPrice + riskDist * riskRewardRatio3

        lblText: str = 'Strong' if signalMode == 'Strong Signals Only (Ultra Clean)' else 'Buy'
        label.new(bar_index, low - trendAtr * 0.5, text=lblText, color=c_bull_bright, textcolor=color.black, style=label.style_label_up, size=size.small, tooltip='[AlgoChief] Bullish Trend Entry')

    if triggerSell:
        activePosition = -1
        lastSignalBar = bar_index
        tradeEntryPrice = close
        tradeStopLoss = trendTracker if trendTracker > close else close + trendAtr * 1.5
        riskDist: float = math.max(tradeStopLoss - tradeEntryPrice, syminfo.mintick * 10)
        tradeTp1 = tradeEntryPrice - riskDist * riskRewardRatio1
        tradeTp2 = tradeEntryPrice - riskDist * riskRewardRatio2
        tradeTp3 = tradeEntryPrice - riskDist * riskRewardRatio3

        lblText: str = 'Strong' if signalMode == 'Strong Signals Only (Ultra Clean)' else 'Sell'
        label.new(bar_index, high + trendAtr * 0.5, text=lblText, color=c_bear_bright, textcolor=color.white, style=label.style_label_down, size=size.small, tooltip='[AlgoChief] Bearish Trend Entry')

    stdevEquilibrium = ta.stdev(close, eqLength)
    zScore = (close - equilibrium) / stdevEquilibrium if stdevEquilibrium > 0 else 0.0

    isExhaustionHigh: bool = showExhaustionDots and (high >= cloudUpperInner or zScore >= 2.2) and (high == ta.highest(high, 10))
    isExhaustionLow: bool = showExhaustionDots and (low <= cloudLowerInner or zScore <= -2.2) and (low == ta.lowest(low, 10))

    plotshape(isExhaustionHigh, title='Overbought Dot', style=shape.circle, location=location.abovebar, color=c_exhaust_dot, size=size.tiny)
    plotshape(isExhaustionLow, title='Oversold Dot', style=shape.circle, location=location.belowbar, color=c_exhaust_dot, size=size.tiny)

    if showSniperSignals:
        lastSniperBar: Persistent[int] = 0
        rawSniperBuy: bool = (low <= cloudLowerInner or zScore <= -2.2) and close > open and (close > low[1]) and (bar_index - lastSniperBar > 20)
        rawSniperSell: bool = (high >= cloudUpperInner or zScore >= 2.2) and close < open and (close < high[1]) and (bar_index - lastSniperBar > 20)
        if rawSniperBuy:
            lastSniperBar = bar_index
            label.new(bar_index, low - trendAtr * 0.4, text='Buy', color=c_sniper_buy, textcolor=color.white, style=label.style_label_up, size=size.small)
        if rawSniperSell:
            lastSniperBar = bar_index
            label.new(bar_index, high + trendAtr * 0.4, text='Sell', color=c_sniper_sell, textcolor=color.black, style=label.style_label_down, size=size.small)

    resBoxes: Persistent[list[Box]] = array.new_box()
    supBoxes: Persistent[list[Box]] = array.new_box()

    if showSRZones:
        pivotHighVal = ta.pivothigh(high, srPivotLen, srPivotLen)
        pivotLowVal = ta.pivotlow(low, srPivotLen, srPivotLen)

        if not na(pivotHighVal):
            topLvl: float = pivotHighVal
            botLvl: float = pivotHighVal - adaptiveVol * srZoneThicknessAtr
            startIdx: int = bar_index - srPivotLen
            newResBox: Box = box.new(left=startIdx, top=topLvl, right=bar_index + 20, bottom=botLvl, border_color=color.new(c_bear_bright, 35), border_width=1, bgcolor=color.new(c_bear_dark, 75))
            array.push(resBoxes, newResBox)
            if array.size(resBoxes) > 3:
                oldBox: Box = array.shift(resBoxes)
                box.delete(oldBox)

        if not na(pivotLowVal):
            botLvl: float = pivotLowVal
            topLvl: float = pivotLowVal + adaptiveVol * srZoneThicknessAtr
            startIdx: int = bar_index - srPivotLen
            newSupBox: Box = box.new(left=startIdx, top=topLvl, right=bar_index + 20, bottom=botLvl, border_color=color.new(c_bull_bright, 35), border_width=1, bgcolor=color.new(c_bull_dark, 75))
            array.push(supBoxes, newSupBox)
            if array.size(supBoxes) > 3:
                oldBox: Box = array.shift(supBoxes)
                box.delete(oldBox)

        if barstate.islast:
            if array.size(resBoxes) > 0:
                for i in pine_range(0, array.size(resBoxes) - 1):
                    b: Box = array.get(resBoxes, i)
                    box.set_right(b, bar_index + 20)

            if array.size(supBoxes) > 0:
                for i in pine_range(0, array.size(supBoxes) - 1):
                    b: Box = array.get(supBoxes, i)
                    box.set_right(b, bar_index + 20)

    slLine: Persistent[Line] = na(Line)
    tp1Line: Persistent[Line] = na(Line)
    tp2Line: Persistent[Line] = na(Line)
    tp3Line: Persistent[Line] = na(Line)

    if showTpSlLines and (not na(tradeEntryPrice)) and (activePosition != 0):
        if not na(slLine):
            line.delete(slLine)
        if not na(tp1Line):
            line.delete(tp1Line)
        if not na(tp2Line):
            line.delete(tp2Line)
        if not na(tp3Line):
            line.delete(tp3Line)

        lineStart: int = lastSignalBar
        lineEnd: int = bar_index + 12
        slLine = line.new(lineStart, tradeStopLoss, lineEnd, tradeStopLoss, color=color.new(c_bear_bright, 20), style=line.style_dashed, width=2)
        tp1Line = line.new(lineStart, tradeTp1, lineEnd, tradeTp1, color=color.new(c_bull_bright, 40), style=line.style_dotted, width=1)
        tp2Line = line.new(lineStart, tradeTp2, lineEnd, tradeTp2, color=color.new(c_bull_bright, 20), style=line.style_dashed, width=1)
        tp3Line = line.new(lineStart, tradeTp3, lineEnd, tradeTp3, color=color.new(c_bull_bright, 0), style=line.style_solid, width=2)

    hud: Persistent[Table] = table.new(position.top_right, 2, 6, bgcolor=color.new(color.new('#131722'), 10), border_color=color.new(color.new('#2A2E39'), 50), border_width=1)

    def f_setTablePosition(pos: str):
        __block_result__ = na
        __switch__ = pos
        if __switch__ == "Top Right":
            __block_result__ = position.top_right
        elif __switch__ == "Bottom Right":
            __block_result__ = position.bottom_right
        elif __switch__ == "Top Left":
            __block_result__ = position.top_left
        elif __switch__ == "Bottom Left":
            __block_result__ = position.bottom_left
        else:
            __block_result__ = position.top_right
        return __block_result__

    if barstate.islast and showDashboard:
        table.set_position(hud, f_setTablePosition(dashboardPos))

        table.merge_cells(hud, 0, 0, 1, 0)
        table.cell(hud, 0, 0, '[AlgoChief] Z-ALGO', bgcolor=color.new(color.new('#2962FF'), 20), text_color=color.white, text_size=size.tiny)

        trendText: str = 'BULLISH ▲' if trendDirection == 1 else 'BEARISH ▼'
        trendBg: Color = color.new(c_bull_bright, 80) if trendDirection == 1 else color.new(c_bear_bright, 80)
        table.cell(hud, 0, 1, 'Trend', text_color=color.silver, text_size=size.tiny)
        table.cell(hud, 1, 1, trendText, bgcolor=trendBg, text_color=color.white, text_size=size.tiny)

        sigText: str = 'LONG' if activePosition == 1 else 'SHORT' if activePosition == -1 else 'WAITING'
        sigBg: Color = color.new(c_bull_bright, 65) if activePosition == 1 else color.new(c_bear_bright, 65) if activePosition == -1 else color.new(color.gray, 65)
        table.cell(hud, 0, 2, 'Position', text_color=color.silver, text_size=size.tiny)
        table.cell(hud, 1, 2, sigText + (' @' + string.tostring(tradeEntryPrice, '#.##') if not na(tradeEntryPrice) else ''), bgcolor=sigBg, text_color=color.white, text_size=size.tiny)

        table.cell(hud, 0, 3, 'SL', text_color=color.silver, text_size=size.tiny)
        table.cell(hud, 1, 3, string.tostring(tradeStopLoss, '#.##') if not na(tradeStopLoss) else '-', bgcolor=color.new(c_bear_dark, 70), text_color=c_bear_bright, text_size=size.tiny)

        table.cell(hud, 0, 4, 'TP1 / TP2', text_color=color.silver, text_size=size.tiny)
        table.cell(hud, 1, 4, (string.tostring(tradeTp1, '#.##') if not na(tradeTp1) else '-') + ' | ' + (string.tostring(tradeTp2, '#.##') if not na(tradeTp2) else '-'), bgcolor=color.new(c_bull_dark, 70), text_color=c_bull_bright, text_size=size.tiny)

        table.cell(hud, 0, 5, 'TP3 Runner', text_color=color.silver, text_size=size.tiny)
        table.cell(hud, 1, 5, string.tostring(tradeTp3, '#.##') if not na(tradeTp3) else '-', bgcolor=color.new(c_bull_dark, 50), text_color=c_bull_bright, text_size=size.tiny)

    alertcondition(triggerBuy, title='[AlgoChief] Strong Buy Signal', message='Z-Algo [AlgoChief]: STRONG BUY Signal triggered on {{ticker}} at {{close}}')
    alertcondition(triggerSell, title='[AlgoChief] Strong Sell Signal', message='Z-Algo [AlgoChief]: STRONG SELL Signal triggered on {{ticker}} at {{close}}')
    alertcondition(trendFlippedBull, title='[AlgoChief] Trend Flipped Bullish', message='Z-Algo [AlgoChief]: Market Trend flipped BULLISH on {{ticker}}')
    alertcondition(trendFlippedBear, title='[AlgoChief] Trend Flipped Bearish', message='Z-Algo [AlgoChief]: Market Trend flipped BEARISH on {{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)