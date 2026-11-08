"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, box, close, color, fill,
    high, input, label, line, low, na, open, plot, position, script, size, string, ta, table, yloc
)
from pynecore.types import Box, Color, Label, Line, Persistent, Series, Table

grp_mode: str = "Toggles & UI Mode"
grp_band: str = "Band Settings"
grp_rsi: str = "RSI Settings"
grp_signal: str = "Signal Settings"
grp_display: str = "Display"
grp_risk: str = "Risk & Reward"
grp_filters: str = "Execution Filters"
grp_dash: str = "Dashboard"


@script.indicator("3-Way Bollinger Trend [ZynAlgo]", shorttitle="3-Way Bollinger Trend [ZynAlgo]", overlay=True, max_lines_count=100, max_labels_count=200, max_boxes_count=200)
def main(
    tradeMode=input.bool(False, "Enable Trade Mode", group=grp_mode, tooltip="OFF: bands stay visible, signal marker still fires with a reason tooltip, Stability Mode / Smart Signal Filter are bypassed, no box/SL-TP tracking. ON: full position box + trailing SL + Win Rate/PF tracking activates, and Stability Mode / Smart Signal Filter start actually gating entries."),
    hmaLength=input.int(20, "HMA Length (center line)", minval=2, group=grp_band, tooltip="Hull MA reacts faster than a same-length SMA/TMA - chosen specifically to reduce lag while still smoothing price."),
    bandStdevMult=input.float(2.0, "Band Width (x StDev)", minval=0.5, step=0.1, group=grp_band, tooltip="Bands = HMA +/- this many standard deviations of price over the same length as the HMA - the same construction as a classic Bollinger Band, just centered on the HMA instead of an SMA."),
    rsiLength=input.int(14, "RSI Length", minval=2, group=grp_rsi),
    rsiColorUpper=input.float(55, "Bullish above (also used as trend filter)", minval=51, maxval=99, group=grp_rsi, tooltip="RSI above this turns the band/center line green (bullish) - this same threshold now also blocks Sell signals while active."),
    rsiColorLower=input.float(45, "Bearish below (also used as trend filter)", minval=1, maxval=49, group=grp_rsi, tooltip="RSI below this turns the band/center line red (bearish) - this same threshold now also blocks Buy signals while active. Between the two thresholds, the band is neutral gray and both directions are allowed."),
    confirmBars=input.int(2, "Confirmation Bars", minval=1, group=grp_signal, tooltip="After price closes back on the trend side of the HMA (the trigger), this many MORE consecutive bars must also stay on that side before the signal actually fires. If price crosses back to the wrong side at any point during this window, the setup is cancelled. This exists specifically to filter out whipsaw noise from price flickering across the HMA."),
    slAtrMult=input.float(1.5, "SL Distance (x ATR)", minval=0.1, step=0.1, group=grp_signal, tooltip="SL = entry price minus/plus this many ATR(14) - no longer based on any candle wick."),
    uiSizeInput=input.string("Small", "UI Text Size (chart + dashboard)", options=("Tiny", "Small", "Normal", "Large"), group=grp_display),
    tp1R=input.float(1.0, "TP1 (R)", minval=0.1, step=0.1, group=grp_risk),
    tp2R=input.float(2.0, "TP2 (R)", minval=0.1, step=0.1, group=grp_risk),
    tp3R=input.float(3.0, "TP3 (R)", minval=0.1, step=0.1, group=grp_risk),
    enableTP2=input.bool(True, "Enable TP2", group=grp_risk),
    enableTP3=input.bool(True, "Enable TP3", group=grp_risk),
    maxTradeDuration=input.int(200, "Max Trade Duration (Bars)", minval=10, group=grp_risk),
    maxStoredTrades=input.int(30, "Max Stored Trade Records (history)", minval=5, group=grp_risk),
    useStabilityMode=input.bool(True, "Stability Mode (no new signal while a trade is open)", group=grp_filters),
    useSmartFilter=input.bool(False, "Smart Signal Filter (force alternating Buy/Sell)", group=grp_filters),
    reversalLockBars=input.int(5, "Cooldown (Bars) - min bars before the next signal", minval=0, group=grp_filters, tooltip="After a signal fires, this many bars must pass before the next one is allowed - a simple spacing filter that keeps rapid back-to-back signals from firing."),
    dashCornerInput=input.string("Top Right", "Dashboard Position", options=("Top Right", "Top Left", "Bottom Right", "Bottom Left"), group=grp_dash)
):
    uiSize = size.tiny if uiSizeInput == 'Tiny' else size.normal if uiSizeInput == 'Normal' else size.large if uiSizeInput == 'Large' else size.small
    dashPos = position.top_left if dashCornerInput == 'Top Left' else position.bottom_right if dashCornerInput == 'Bottom Right' else position.bottom_left if dashCornerInput == 'Bottom Left' else position.top_right

    atrVal: float = ta.atr(14)

    hmaCenter: Series[float] = ta.hma(close, hmaLength)
    priceStdev: float = ta.stdev(close, hmaLength)
    bandUpper: float = hmaCenter + bandStdevMult * priceStdev
    bandLower: float = hmaCenter - bandStdevMult * priceStdev

    rsiValue: float = ta.rsi(close, rsiLength)

    bandColor: Color = color.new(color.new('#1A935B'), 0) if rsiValue > rsiColorUpper else color.new(color.new('#FF4757'), 0) if rsiValue < rsiColorLower else color.new(color.yellow, 0)

    plot(hmaCenter if not tradeMode else na, title='HMA Center', color=bandColor, linewidth=2)
    p1 = plot(bandUpper if not tradeMode else na, title='Upper Band', color=bandColor, linewidth=1)
    p2 = plot(bandLower if not tradeMode else na, title='Lower Band', color=bandColor, linewidth=1)
    fill(p1, p2, color=color.new(bandColor, 92), title='Band Fill')

    awaitingConfirmBuy: Persistent[bool] = False
    awaitingConfirmSell: Persistent[bool] = False
    confirmCounter: Persistent[int] = 0
    lastTrendDir: Persistent[int] = 0
    reversalBuyRaw: Persistent[bool] = False
    reversalSellRaw: Persistent[bool] = False

    if barstate.isconfirmed:
        bandBullish: bool = rsiValue > rsiColorUpper
        bandBearish: bool = rsiValue < rsiColorLower

        if bandBullish:
            lastTrendDir = 1
        elif bandBearish:
            lastTrendDir = -1

        triggerBuy: bool = close > hmaCenter and close[1] <= hmaCenter[1]
        triggerSell: bool = close < hmaCenter and close[1] >= hmaCenter[1]

        if triggerBuy:
            awaitingConfirmBuy = True
            awaitingConfirmSell = False
            confirmCounter = 0
        elif triggerSell:
            awaitingConfirmSell = True
            awaitingConfirmBuy = False
            confirmCounter = 0
        elif awaitingConfirmBuy:
            if close <= hmaCenter:
                awaitingConfirmBuy = False
                confirmCounter = 0
            else:
                confirmCounter += 1
        elif awaitingConfirmSell:
            if close >= hmaCenter:
                awaitingConfirmSell = False
                confirmCounter = 0
            else:
                confirmCounter += 1

        confirmedBuy: bool = awaitingConfirmBuy and confirmCounter >= confirmBars
        confirmedSell: bool = awaitingConfirmSell and confirmCounter >= confirmBars

        if confirmedBuy:
            awaitingConfirmBuy = False
            confirmCounter = 0
        if confirmedSell:
            awaitingConfirmSell = False
            confirmCounter = 0

        trendOkBuy: bool = lastTrendDir == 1
        trendOkSell: bool = lastTrendDir == -1

        reversalBuyRaw = confirmedBuy and trendOkBuy
        reversalSellRaw = confirmedSell and trendOkSell
    else:
        reversalBuyRaw = False
        reversalSellRaw = False

    lastSignalBar: Persistent[int] = na(int)
    lastSignalDir: Persistent[int] = 0
    anyTradeOpen: Persistent[bool] = False

    tEntry: Persistent[list[float]] = array.new_float(0)
    tSL: Persistent[list[float]] = array.new_float(0)
    tR: Persistent[list[float]] = array.new_float(0)
    tIsBuy: Persistent[list[bool]] = array.new_bool(0)
    tEntryBar: Persistent[list[int]] = array.new_int(0)
    tMaxTp: Persistent[list[int]] = array.new_int(0)
    tActive: Persistent[list[bool]] = array.new_bool(0)
    tHighestTpPrice: Persistent[list[float]] = array.new_float(0)
    tHighestTpBar: Persistent[list[int]] = array.new_int(0)
    tRewardBox: Persistent[list[Box]] = array.new_box(0)
    tRiskBox: Persistent[list[Box]] = array.new_box(0)
    tEntryLine: Persistent[list[Line]] = array.new_line(0)
    tStopLine: Persistent[list[Line]] = array.new_line(0)
    tEntryLabel: Persistent[list[Label]] = array.new_label(0)

    totalTrades: Persistent[int] = 0
    totalWins: Persistent[float] = 0.0
    totalLosses: Persistent[int] = 0
    totalProfitR: Persistent[float] = 0.0
    totalLossR: Persistent[float] = 0.0

    pendingDir: Persistent[int] = 0
    pendingEntryBar: Persistent[int] = na(int)

    sigFireBuy: Persistent[bool] = False
    sigFireSell: Persistent[bool] = False

    if barstate.isconfirmed:
        cooldownOk: bool = na(lastSignalBar) or bar_index - lastSignalBar >= reversalLockBars
        stabilityAllowed: bool = not tradeMode or not (useStabilityMode and anyTradeOpen)
        smartBuyAllowed: bool = not tradeMode or not (useSmartFilter and lastSignalDir == 1)
        smartSellAllowed: bool = not tradeMode or not (useSmartFilter and lastSignalDir == -1)

        fireBuy: bool = reversalBuyRaw and cooldownOk and stabilityAllowed and smartBuyAllowed
        fireSell: bool = reversalSellRaw and cooldownOk and stabilityAllowed and smartSellAllowed

        sigFireBuy = fireBuy
        sigFireSell = fireSell

        if fireBuy or fireSell:
            pendingDir = 1 if fireBuy else -1
            pendingEntryBar = bar_index + 1
            lastSignalBar = bar_index
            lastSignalDir = pendingDir

        if not na(pendingEntryBar) and bar_index == pendingEntryBar:
            entryPx: float = open
            isBuy: bool = pendingDir == 1
            slDist: float = slAtrMult * atrVal
            slPx: float = entryPx - slDist if isBuy else entryPx + slDist

            if slDist > 0:
                tp1Px: float = entryPx + tp1R * slDist if isBuy else entryPx - tp1R * slDist
                tp2Px: float = entryPx + tp2R * slDist if isBuy else entryPx - tp2R * slDist
                tp3Px: float = entryPx + tp3R * slDist if isBuy else entryPx - tp3R * slDist
                finalTargetPrice: float = tp3Px if enableTP3 else tp2Px if enableTP2 else tp1Px
                finalTargetR: float = tp3R if enableTP3 else tp2R if enableTP2 else tp1R

                labelText: str = '▲' if isBuy else '▼'
                labelColor: Color = color.new(color.new('#1A935B'), 0) if isBuy else color.new(color.new('#FF4757'), 0)
                labelStyle: str = label.style_label_up if isBuy else label.style_label_down
                labelY: float = low - atrVal * 1.0 if isBuy else high + atrVal * 1.0
                reasonText: str = 'Pullback ' + ('Buy' if isBuy else 'Sell') + ' (' + ('bullish band' if rsiValue > rsiColorUpper else 'bearish band' if rsiValue < rsiColorLower else 'sideway band, carrying over the last established trend') + '): price crossed back to the ' + ('bullish (above)' if isBuy else 'bearish (below)') + ' side of the HMA and held there for ' + string.tostring(confirmBars) + ' confirmation bar(s) without crossing back'
                newLbl: Label = label.new(bar_index, labelY, labelText, style=labelStyle, color=labelColor, textcolor=color.white, size=uiSize, tooltip=reasonText)

                if tradeMode:
                    array.push(tEntry, entryPx)
                    array.push(tSL, slPx)
                    array.push(tR, slDist)
                    array.push(tIsBuy, isBuy)
                    array.push(tEntryBar, bar_index)
                    array.push(tMaxTp, 0)
                    array.push(tActive, True)
                    array.push(tHighestTpPrice, entryPx)
                    array.push(tHighestTpBar, na)

                    riskBox: Box = box.new(bar_index, entryPx if isBuy else slPx, bar_index, slPx if isBuy else entryPx, border_color=color.new(color.new('#F5474A'), 100), bgcolor=color.new(color.new('#F5474A'), 82))
                    rewardBox: Box = box.new(bar_index, finalTargetPrice if isBuy else entryPx, bar_index, entryPx if isBuy else finalTargetPrice, border_color=color.new(color.new('#00D97E'), 100), bgcolor=color.new(color.new('#00D97E'), 86))
                    entryLine: Line = line.new(bar_index, entryPx, bar_index, entryPx, color=color.new(color.white, 65), width=1, style=line.style_dotted)
                    stopLine: Line = line.new(bar_index, slPx, bar_index, slPx, color=color.new(color.red, 65), width=1, style=line.style_dotted)
                    array.push(tRewardBox, rewardBox)
                    array.push(tRiskBox, riskBox)
                    array.push(tEntryLine, entryLine)
                    array.push(tStopLine, stopLine)
                    array.push(tEntryLabel, newLbl)

                    totalTrades += 1
                    anyTradeOpen = True

            pendingEntryBar = na
    else:
        sigFireBuy = False
        sigFireSell = False

    if barstate.isconfirmed and tradeMode and (array.size(tActive) > 0):
        for i in pine_range(array.size(tActive) - 1, 0):
            if array.get(tActive, i):
                isBuy: bool = array.get(tIsBuy, i)
                entryPx: float = array.get(tEntry, i)
                slOriginal: float = array.get(tSL, i)
                rDist: float = array.get(tR, i)
                maxTp: int = array.get(tMaxTp, i)
                entryBar: int = array.get(tEntryBar, i)

                tp1Px: float = entryPx + tp1R * rDist if isBuy else entryPx - tp1R * rDist
                tp2Px: float = entryPx + tp2R * rDist if isBuy else entryPx - tp2R * rDist
                finalTargetPrice: float = (entryPx + tp3R * rDist if isBuy else entryPx - tp3R * rDist) if enableTP3 else tp2Px if enableTP2 else tp1Px
                finalTargetR: float = tp3R if enableTP3 else tp2R if enableTP2 else tp1R

                currentSL: float = tp1Px if maxTp >= 2 else entryPx if maxTp >= 1 else slOriginal
                hitSL: bool = low <= currentSL if isBuy else high >= currentSL
                hitFinalTarget: bool = high >= finalTargetPrice if isBuy else low <= finalTargetPrice

                rb: Box = array.get(tRewardBox, i)
                rk: Box = array.get(tRiskBox, i)
                el: Line = array.get(tEntryLine, i)
                sl_line: Line = array.get(tStopLine, i)
                box.set_right(rb, bar_index)
                box.set_right(rk, bar_index)
                line.set_x2(el, bar_index)
                line.set_x2(sl_line, bar_index)
                line.set_y1(sl_line, currentSL)
                line.set_y2(sl_line, currentSL)

                closeNow: bool = False
                resultKind: str = ""
                justReachedNewTp: bool = False

                if hitSL:
                    closeNow = True
                    resultKind = 'TP' if maxTp > 0 else 'SL'
                elif hitFinalTarget:
                    closeNow = True
                    resultKind = "WIN"
                    array.set(tHighestTpPrice, i, finalTargetPrice)
                    array.set(tHighestTpBar, i, bar_index)
                else:
                    hitTp1: bool = high >= tp1Px if isBuy else low <= tp1Px
                    hitTp2: bool = enableTP2 and (high >= tp2Px if isBuy else low <= tp2Px)

                    if maxTp < 1 and hitTp1:
                        maxTp = 1
                        array.set(tMaxTp, i, 1)
                        array.set(tHighestTpPrice, i, tp1Px)
                        array.set(tHighestTpBar, i, bar_index)
                        justReachedNewTp = True
                    if maxTp == 1 and hitTp2:
                        maxTp = 2
                        array.set(tMaxTp, i, 2)
                        array.set(tHighestTpPrice, i, tp2Px)
                        array.set(tHighestTpBar, i, bar_index)
                        justReachedNewTp = True

                    timedOut: bool = bar_index - entryBar >= maxTradeDuration
                    if timedOut:
                        closeNow = True
                        resultKind = "TIMEOUT"

                if justReachedNewTp and (not closeNow):
                    label.new(bar_index, high if isBuy else low, 'TP' + string.tostring(array.get(tMaxTp, i)), style=label.style_none, textcolor=color.new(color.new('#00D97E'), 0), size=size.tiny, yloc=yloc.abovebar if isBuy else yloc.belowbar)

                if closeNow:
                    array.set(tActive, i, False)

                    cleanLoss: bool = resultKind == 'SL' and array.get(tMaxTp, i) == 0
                    rResult: float = finalTargetR if resultKind == 'WIN' else tp1R if array.get(tMaxTp, i) >= 2 else 0.0

                    if resultKind == 'SL' or resultKind == 'WIN' or resultKind == 'TP':
                        if cleanLoss:
                            totalLosses += 1
                            totalLossR += 1.0
                        else:
                            totalWins += 0.5 if rResult == 0.0 else 1.0
                            totalProfitR += rResult

                    rSign: str = '+' if rResult >= 0 else ''
                    resText: str = 'SL -1R' if resultKind == 'SL' else 'WIN +' + string.tostring(rResult, '#.#') + 'R' if resultKind == 'WIN' else 'TIMEOUT' if resultKind == 'TIMEOUT' else 'TP ' + rSign + string.tostring(rResult, '#.#') + 'R'
                    barsText: str = string.tostring(bar_index - entryBar) + ' bars'
                    entryLbl: Label = array.get(tEntryLabel, i)
                    if not na(entryLbl):
                        label.set_tooltip(entryLbl, resText + '\n' + barsText)

                    achievedBar: int = bar_index if na(array.get(tHighestTpBar, i)) else array.get(tHighestTpBar, i)
                    achievedPrice: float = array.get(tHighestTpPrice, i)
                    box.set_right(rb, achievedBar)
                    box.set_right(rk, achievedBar)
                    if isBuy:
                        box.set_top(rb, achievedPrice)
                        box.set_bottom(rb, entryPx)
                    else:
                        box.set_top(rb, entryPx)
                        box.set_bottom(rb, achievedPrice)

                    if resultKind == 'SL' and cleanLoss:
                        label.new(bar_index, low if isBuy else high, 'x', style=label.style_none, textcolor=color.new(color.new('#EF4444'), 0), size=size.small, yloc=yloc.belowbar if isBuy else yloc.abovebar)

        stillOpen: bool = False
        if array.size(tActive) > 0:
            for k in pine_range(0, array.size(tActive) - 1):
                if array.get(tActive, k):
                    stillOpen = True
        anyTradeOpen = stillOpen

        if array.size(tActive) > maxStoredTrades:
            if not array.get(tActive, 0):
                b1: Box = array.get(tRewardBox, 0)
                b2: Box = array.get(tRiskBox, 0)
                l1: Line = array.get(tEntryLine, 0)
                l2: Line = array.get(tStopLine, 0)
                if not na(b1):
                    box.delete(b1)
                if not na(b2):
                    box.delete(b2)
                if not na(l1):
                    line.delete(l1)
                if not na(l2):
                    line.delete(l2)
                array.shift(tEntry)
                array.shift(tSL)
                array.shift(tR)
                array.shift(tIsBuy)
                array.shift(tEntryBar)
                array.shift(tMaxTp)
                array.shift(tActive)
                array.shift(tHighestTpPrice)
                array.shift(tHighestTpBar)
                array.shift(tRewardBox)
                array.shift(tRiskBox)
                array.shift(tEntryLine)
                array.shift(tStopLine)
                array.shift(tEntryLabel)

    dash: Persistent[Table] = table.new(dashPos, 2, 6, bgcolor=color.new(color.new('#131722'), 10), border_width=1)

    if barstate.islast:
        rsiZoneText: str = 'BULLISH' if rsiValue > rsiColorUpper else 'BEARISH' if rsiValue < rsiColorLower else 'SIDEWAY'
        rsiZoneColor: Color = color.new(color.new('#1A935B'), 0) if rsiValue > rsiColorUpper else color.new(color.new('#FF4757'), 0) if rsiValue < rsiColorLower else color.new(color.yellow, 0)

        table.cell(dash, 0, 0, '3-WAY BOLL TREND', text_color=color.white, text_size=uiSize, bgcolor=color.new(color.new('#2962FF'), 20))
        table.cell(dash, 1, 0, '', bgcolor=color.new(color.new('#2962FF'), 20))

        table.cell(dash, 0, 1, 'RSI', text_color=color.gray, text_size=uiSize)
        table.cell(dash, 1, 1, string.tostring(rsiValue, '#.#'), text_color=rsiZoneColor, text_size=uiSize)

        table.cell(dash, 0, 2, 'Momentum Zone', text_color=color.gray, text_size=uiSize)
        table.cell(dash, 1, 2, rsiZoneText, text_color=rsiZoneColor, text_size=uiSize)

        if tradeMode:
            winRate: float = totalWins / (totalWins + totalLosses) * 100.0 if totalWins + totalLosses > 0 else 0.0
            pf: float = totalProfitR / totalLossR if totalLossR > 0 else 999.0 if totalProfitR > 0 else 0.0

            table.cell(dash, 0, 3, 'Trades', text_color=color.gray, text_size=uiSize)
            table.cell(dash, 1, 3, string.tostring(totalTrades), text_color=color.white, text_size=uiSize)

            table.cell(dash, 0, 4, 'Win Rate / PF', text_color=color.gray, text_size=uiSize)
            table.cell(dash, 1, 4, string.tostring(winRate, '#.#') + '% / ' + string.tostring(pf, '#.##'), text_color=color.new(color.new('#10B981'), 0) if winRate >= 50 else color.new(color.new('#EF4444'), 0), text_size=uiSize)

    alertcondition(sigFireBuy, title='3-Way Bollinger Trend Reversal Buy', message='3-Way Bollinger Trend [ZynAlgo]: Reversal BUY on {{ticker}} ({{interval}}) at {{close}}')
    alertcondition(sigFireSell, title='3-Way Bollinger Trend Reversal Sell', message='3-Way Bollinger Trend [ZynAlgo]: Reversal SELL on {{ticker}} ({{interval}}) at {{close}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
