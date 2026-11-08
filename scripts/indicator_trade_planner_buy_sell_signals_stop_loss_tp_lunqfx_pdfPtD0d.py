"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barstate, box, close, color,
    fill, format, high, input, label, line, low, math, na, open, plot, plotcandle, position,
    request, script, size, string, syminfo, ta, table, text, yloc
)
from pynecore.types import Box, Color, Label, Line, Persistent, Series, Table

gA: str = "Account & risk"
gS: str = "Setup"
gT: str = "Targets & management"
gV: str = "Visuals"


@script.indicator("Trade Planner Buy Sell Signals, Stop Loss, TP & Lot Size [LunqFX]", "Trade Planner", overlay=True, max_boxes_count=60, max_lines_count=120, max_labels_count=200)
def main(
    balance=input.float(10000, "Account balance", minval=1, step=100, group=gA),
    riskPct=input.float(1.0, "Risk per trade %", minval=0.01, maxval=10, step=0.1, group=gA, tooltip="The share of the account the stop is allowed to cost. The position size is calculated from this and the stop distance."),
    accCur=input.string("USD", "Account currency", options=("USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD", "USDT"), group=gA),
    lotOver=input.float(0, "Units per lot (0 = automatic)", minval=0, step=1, group=gA, tooltip="Automatic: forex 100,000 · gold 100 oz · silver 5,000 oz · futures in contracts · everything else in units. Set your broker's figure here if it differs."),
    fastLen=input.int(21, "Fast EMA (value zone)", minval=2, maxval=200, group=gS),
    slowLen=input.int(50, "Slow EMA (trend)", minval=5, maxval=400, group=gS),
    rsiLen=input.int(14, "Momentum (RSI length)", minval=2, maxval=50, group=gS),
    zoneW=input.float(0.25, "Value zone width (× ATR)", minval=0.0, maxval=2.0, step=0.05, group=gS, tooltip="How close to the fast EMA price has to come for the move to count as a pullback."),
    slBuf=input.float(0.2, "Stop buffer beyond pullback (× ATR)", minval=0.0, maxval=2.0, step=0.05, group=gS),
    minStop=input.float(0.5, "Minimum stop distance (× ATR)", minval=0.1, maxval=3.0, step=0.05, group=gS, tooltip="A stop tighter than this is widened to it, so one noisy candle does not end the trade."),
    maxStop=input.float(3.0, "Maximum stop distance (× ATR)", minval=0.5, maxval=10.0, step=0.25, group=gS, tooltip="A setup whose stop would be wider than this is skipped rather than printed. A plan with a stop five ATR away is not a pullback trade any more."),
    pbBars=input.int(10, "Pullback lookback (bars)", minval=2, maxval=50, group=gS, tooltip="The stop is anchored on the lowest low (highest high for shorts) of this many recent bars — the pullback itself, not an old swing from before it."),
    r1=input.float(1.0, "TP1 (R)", minval=0.25, maxval=20, step=0.25, group=gT),
    r2=input.float(2.0, "TP2 (R)", minval=0.25, maxval=20, step=0.25, group=gT),
    r3=input.float(3.0, "TP3 (R)", minval=0.25, maxval=20, step=0.25, group=gT),
    beOn=input.bool(False, "Move stop to entry after TP1", group=gT),
    oppOn=input.bool(True, "Close on opposite signal", group=gT),
    candSty=input.string("Neon Bloom", "Candle palette", options=("Neon Bloom", "Midnight Cyan", "Vibrant Neon", "Classic Soft", "Cool Blue", "Off"), group=gV),
    showZone=input.bool(True, "Show value zone", group=gV),
    tagSize=input.string("Normal", "Level tag size", options=("Small", "Normal", "Large", "Huge"), group=gV, tooltip="Size of the SL / TP1 / TP2 / TP3 tags and of the entry label."),
    keepN=input.int(2, "Plans kept on chart", minval=1, maxval=10, group=gV),
    showHUD=input.bool(True, "Show panel", group=gV),
    hudPos=input.string("Top Right", "Panel position", options=("Top Right", "Top Left", "Bottom Right", "Bottom Left", "Middle Right"), group=gV),
    hudSize=input.string("Normal", "Panel text", options=("Small", "Normal", "Large"), group=gV)
):
    UP: Color = color.new('#00F5D4')
    DN: Color = color.new('#FF2E88')
    RISK: Color = color.new('#FF4D6D')
    GOLD: Color = color.new('#FFD250')
    CARD: Color = color.new('#131A24')
    CARD2: Color = color.new('#1B2431')
    HEAD: Color = color.new('#0E141D')
    TXT: Color = color.new('#F1F5F9')
    MUTE: Color = color.new('#94A3B8')



    __block_result__ = na
    __switch__ = tagSize
    if __switch__ == "Small":
        __block_result__ = size.small
    elif __switch__ == "Large":
        __block_result__ = size.large
    elif __switch__ == "Huge":
        __block_result__ = size.huge
    else:
        __block_result__ = size.normal
    tagSz = __block_result__
    __block_result_1__ = na
    __switch__ = tagSize
    if __switch__ == "Small":
        __block_result_1__ = size.normal
    elif __switch__ == "Normal":
        __block_result_1__ = size.large
    else:
        __block_result_1__ = size.huge
    entSz = __block_result_1__

    atr = ta.atr(14)
    emaF = ta.ema(close, fastLen)
    emaS: Series = ta.ema(close, slowLen)
    rsi: Series = ta.rsi(close, rsiLen)
    zone = atr * zoneW

    trendUp = emaF > emaS and close > emaS and (emaS >= emaS[3])
    trendDn = emaF < emaS and close < emaS and (emaS <= emaS[3])

    anchorL = ta.lowest(low, pbBars)
    anchorH = ta.highest(high, pbBars)
    stopL0 = anchorL - atr * slBuf
    stopS0 = anchorH + atr * slBuf
    stopL = close - atr * minStop if close - stopL0 < atr * minStop else stopL0
    stopS = close + atr * minStop if stopS0 - close < atr * minStop else stopS0
    okL = close - stopL <= atr * maxStop
    okS = stopS - close <= atr * maxStop

    tk = string.upper(syminfo.ticker)
    autoUnits = 100000.0 if syminfo.type == 'forex' else 100.0 if string.contains(tk, 'XAU') else 5000.0 if string.contains(tk, 'XAG') else 1.0
    lotUnits = lotOver if lotOver > 0 else autoUnits
    sizeWord = 'contracts' if syminfo.type == 'futures' else 'lots' if lotUnits > 1 else 'units'
    fxRate = request.currency_rate(syminfo.currency, accCur, ignore_invalid_currency=True)
    rate = 1.0 if na(fxRate) or fxRate <= 0 else fxRate
    riskMoney = balance * riskPct / 100.0

    def sizeFor(dist: float):
        perUnit = dist * syminfo.pointvalue * rate
        return riskMoney / perUnit / lotUnits if perUnit > 0 else na

    def money(v: float):
        return ('$' if accCur == 'USD' or accCur == 'USDT' else accCur + ' ') + string.tostring(v, '#,##0')

    def sizeTxt(s: float):
        return '—' if na(s) else string.tostring(s, '0.00' if s < 10 else '#,##0.0') + ' ' + sizeWord

    __block_result_2__ = na
    __switch__ = candSty
    if __switch__ == "Neon Bloom":
        __block_result_2__ = color.new('#00F5D4')
    elif __switch__ == "Midnight Cyan":
        __block_result_2__ = color.new('#34E89E')
    elif __switch__ == "Vibrant Neon":
        __block_result_2__ = color.new('#00E5B0')
    elif __switch__ == "Classic Soft":
        __block_result_2__ = color.new('#3FB68B')
    elif __switch__ == "Cool Blue":
        __block_result_2__ = color.new('#4C9AFF')
    else:
        __block_result_2__ = color.new('#00F5D4')
    cBull = __block_result_2__
    __block_result_3__ = na
    __switch__ = candSty
    if __switch__ == "Neon Bloom":
        __block_result_3__ = color.new('#FF2E88')
    elif __switch__ == "Midnight Cyan":
        __block_result_3__ = color.new('#FF4D7D')
    elif __switch__ == "Vibrant Neon":
        __block_result_3__ = color.new('#FF2E63')
    elif __switch__ == "Classic Soft":
        __block_result_3__ = color.new('#E0556B')
    elif __switch__ == "Cool Blue":
        __block_result_3__ = color.new('#8A94A6')
    else:
        __block_result_3__ = color.new('#FF2E88')
    cBear = __block_result_3__
    cEdge = cBull if close >= open else cBear
    plotcandle(na if candSty == 'Off' else open, high, low, close, 'Candles', color=color.new(cEdge, 24), wickcolor=color.new(cEdge, 18), bordercolor=cEdge)

    zCol = UP if trendUp else DN if trendDn else MUTE
    zTop = plot(emaF + zone if showZone else na, 'Value zone top', color=color.new(zCol, 70), linewidth=1)
    zBot = plot(emaF - zone if showZone else na, 'Value zone bottom', color=color.new(zCol, 70), linewidth=1)
    fill(zTop, zBot, color=color.new(zCol, 88), title='Value zone')
    plot(emaS if showZone else na, 'Trend EMA', color=color.new(zCol, 40), linewidth=2)

    pbL: Persistent[bool] = False
    pbLow: Persistent[float] = na(float)
    pbS: Persistent[bool] = False
    pbHigh: Persistent[float] = na(float)

    tDir: Persistent[int] = 0
    tEntry: Persistent[float] = na(float)
    tSL: Persistent[float] = na(float)
    tSL0: Persistent[float] = na(float)
    tTP1: Persistent[float] = na(float)
    tTP2: Persistent[float] = na(float)
    tTP3: Persistent[float] = na(float)
    tBar: Persistent[int] = na(int)
    tStage: Persistent[int] = 0
    tSize: Persistent[float] = na(float)
    lastOut: Persistent[str] = ""

    bRisk: Persistent[Box] = na(Box)
    bRew: Persistent[Box] = na(Box)
    l1: Persistent[Line] = na(Line)
    l2: Persistent[Line] = na(Line)
    l3: Persistent[Line] = na(Line)
    kSL: Persistent[Label] = na(Label)
    k1: Persistent[Label] = na(Label)
    k2: Persistent[Label] = na(Label)
    k3: Persistent[Label] = na(Label)

    allB: Persistent[list[Box]] = array.new_box()
    allL: Persistent[list[Line]] = array.new_line()
    allK: Persistent[list[Label]] = array.new_label()

    longSig: bool = False
    shortSig: bool = False
    hitTP1: bool = False
    hitTP2: bool = False
    hitTP3: bool = False
    hitSL: bool = False

    def px(v: float):
        return string.tostring(v, format.mintick)

    def closePlan(how: str):
        box.set_right(bRisk, bar_index)
        box.set_right(bRew, bar_index)
        line.set_x2(l1, bar_index)
        line.set_x2(l2, bar_index)
        line.set_x2(l3, bar_index)
        for k in array.from_items(kSL, k1, k2, k3):
            label.set_x(k, bar_index)
        return how

    if barstate.isconfirmed:
        if tDir != 0 and bar_index > tBar:
            slHit = low <= tSL if tDir == 1 else high >= tSL
            h1 = tStage < 1 and (high >= tTP1 if tDir == 1 else low <= tTP1)
            h2 = tStage < 2 and (high >= tTP2 if tDir == 1 else low <= tTP2)
            h3 = high >= tTP3 if tDir == 1 else low <= tTP3

            if slHit:
                hitSL = True
                atEntry = tSL == tEntry
                label.set_text(kSL, ('EXIT AT ENTRY  ' if atEntry else 'STOPPED  ') + px(tSL))
                lastOut = closePlan('exit at entry' if atEntry else 'stopped')
                tDir = 0
            else:
                if h1:
                    tStage = 1
                    hitTP1 = True
                    label.set_text(k1, 'TP1 ✓  ' + px(tTP1))
                    if beOn:
                        tSL = tEntry
                        box.set_bottom(bRisk, tEntry)
                        box.set_top(bRisk, tEntry)
                        label.set_y(kSL, tEntry)
                        label.set_text(kSL, 'STOP AT ENTRY  ' + px(tEntry))
                if h2:
                    tStage = 2
                    hitTP2 = True
                    label.set_text(k2, 'TP2 ✓  ' + px(tTP2))
                if h3:
                    hitTP3 = True
                    label.set_text(k3, 'TP3 ✓  ' + px(tTP3))
                    lastOut = closePlan('TP3 reached')
                    tDir = 0

            if tDir != 0:
                xr = bar_index + 3
                box.set_right(bRisk, xr)
                box.set_right(bRew, xr)
                line.set_x2(l1, xr)
                line.set_x2(l2, xr)
                line.set_x2(l3, xr)
                for k in array.from_items(kSL, k1, k2, k3):
                    label.set_x(k, xr)

        if trendUp:
            if low <= emaF + zone:
                pbL = True
            if pbL:
                pbLow = low if na(pbLow) else math.min(pbLow, low)
        else:
            pbL = False
            pbLow = na
        if trendDn:
            if high >= emaF - zone:
                pbS = True
            if pbS:
                pbHigh = high if na(pbHigh) else math.max(pbHigh, high)
        else:
            pbS = False
            pbHigh = na

        goLong = trendUp and pbL and (close > emaF) and (close > open) and (rsi > 50) and (rsi > rsi[1]) and okL and (tDir != 1) and (tDir == 0 or oppOn)
        goShort = trendDn and pbS and (close < emaF) and (close < open) and (rsi < 50) and (rsi < rsi[1]) and okS and (tDir != -1) and (tDir == 0 or oppOn)

        if goLong or goShort:
            if tDir != 0:
                lastOut = closePlan('closed on opposite signal')
            d = 1 if goLong else -1
            e = close
            s = stopL if goLong else stopS
            risk = math.abs(e - s)
            tDir = d
            tEntry = e
            tSL = s
            tSL0 = s
            tTP1 = e + d * risk * r1
            tTP2 = e + d * risk * r2
            tTP3 = e + d * risk * r3
            tBar = bar_index
            tStage = 0
            tSize = sizeFor(risk)
            longSig = goLong
            shortSig = goShort
            pbL = False
            pbLow = na
            pbS = False
            pbHigh = na

            col = UP if d == 1 else DN
            xr = bar_index + 3
            tpHi = tTP3 if d == 1 else e
            tpLo = e if d == 1 else tTP3
            bRisk = box.new(bar_index, math.max(e, s), xr, math.min(e, s), border_color=color.new(RISK, 45), border_width=1, bgcolor=color.new(RISK, 84))
            bRew = box.new(bar_index, tpHi, xr, tpLo, border_color=color.new(col, 55), border_width=1, bgcolor=color.new(col, 90))
            l1 = line.new(bar_index, tTP1, xr, tTP1, color=color.new(GOLD, 20), style=line.style_dotted, width=2)
            l2 = line.new(bar_index, tTP2, xr, tTP2, color=color.new(GOLD, 35), style=line.style_dotted, width=2)
            l3 = line.new(bar_index, tTP3, xr, tTP3, color=color.new(GOLD, 50), style=line.style_dotted, width=2)
            rew1 = riskMoney * r1
            kSL = label.new(xr, s, 'SL  ' + px(s) + '   −' + money(riskMoney), style=label.style_label_left, color=HEAD, textcolor=RISK, size=tagSz)
            k1 = label.new(xr, tTP1, 'TP1 · ' + string.tostring(r1, '#.##') + 'R  ' + px(tTP1) + '   +' + money(rew1), style=label.style_label_left, color=HEAD, textcolor=GOLD, size=tagSz)
            k2 = label.new(xr, tTP2, 'TP2 · ' + string.tostring(r2, '#.##') + 'R  ' + px(tTP2), style=label.style_label_left, color=HEAD, textcolor=color.new(GOLD, 20), size=tagSz)
            k3 = label.new(xr, tTP3, 'TP3 · ' + string.tostring(r3, '#.##') + 'R  ' + px(tTP3), style=label.style_label_left, color=HEAD, textcolor=color.new(GOLD, 35), size=tagSz)
            kE = label.new(bar_index, low if d == 1 else high, ('▲ BUY  ' if d == 1 else '▼ SELL  ') + sizeTxt(tSize), yloc=yloc.belowbar if d == 1 else yloc.abovebar, style=label.style_label_up if d == 1 else label.style_label_down, color=col, textcolor=color.new('#04211D'), size=entSz)
            if d == -1:
                label.set_textcolor(kE, color.new('#2B0716'))

            for b in array.from_items(bRisk, bRew):
                array.push(allB, b)
            for l in array.from_items(l1, l2, l3):
                array.push(allL, l)
            for k in array.from_items(kSL, k1, k2, k3, kE):
                array.push(allK, k)

            while array.size(allB) > keepN * 2:
                box.delete(array.shift(allB))
            while array.size(allL) > keepN * 3:
                line.delete(array.shift(allL))
            while array.size(allK) > keepN * 5:
                label.delete(array.shift(allK))

    def hudP(s: str):
        __block_result_4__ = na
        __switch__ = s
        if __switch__ == "Top Right":
            __block_result_4__ = position.top_right
        elif __switch__ == "Top Left":
            __block_result_4__ = position.top_left
        elif __switch__ == "Bottom Right":
            __block_result_4__ = position.bottom_right
        elif __switch__ == "Bottom Left":
            __block_result_4__ = position.bottom_left
        else:
            __block_result_4__ = position.middle_right
        return __block_result_4__

    def tSz(s: str):
        __block_result_5__ = na
        __switch__ = s
        if __switch__ == "Small":
            __block_result_5__ = size.small
        elif __switch__ == "Large":
            __block_result_5__ = size.large
        else:
            __block_result_5__ = size.normal
        return __block_result_5__

    def rowL(tb: Table, r: int, k: str, v: str, c: Color, bg: Color, ts: str):
        table.cell(tb, 0, r, '  ' + k, text_color=MUTE, text_size=ts, text_halign=text.align_left, bgcolor=bg)
        return table.cell(tb, 1, r, v + '  ', text_color=c, text_size=ts, text_halign=text.align_right, bgcolor=bg)

    hud: Persistent[Table] = table.new(position.top_right, 2, 11)
    if showHUD and barstate.islast:
        table.delete(hud)
        hud = table.new(hudP(hudPos), 2, 11, bgcolor=CARD, border_color=color.new(color.new('#28323F'), 0), border_width=1)
        ts = tSz(hudSize)
        active = tDir != 0
        riskNow = math.abs(tEntry - tSL0) if active else na
        liveR = (close - tEntry) * tDir / riskNow if active and riskNow > 0 else na

        planTx = ('▲ LONG PLAN' if tDir == 1 else '▼ SHORT PLAN') + ('  ·  TP2 ✓' if tStage == 2 else '  ·  TP1 ✓' if tStage == 1 else '')
        trendTx = ('▲ UPTREND · in value zone' if pbL else '▲ UPTREND · waiting for pullback') if trendUp else ('▼ DOWNTREND · in value zone' if pbS else '▼ DOWNTREND · waiting for pullback') if trendDn else 'NO TREND · no plan'
        hTx = planTx if active else trendTx
        hBg = (color.new('#0A5F55') if tDir == 1 else color.new('#8E1148')) if active else CARD2
        table.cell(hud, 0, 0, '  TRADE PLANNER  ', text_color=UP, text_size=size.small, text_halign=text.align_left, bgcolor=HEAD)
        table.cell(hud, 1, 0, '' if riskPct == 0 else string.tostring(riskPct, '#.##') + '% risk  ', text_color=MUTE, text_size=size.small, text_halign=text.align_right, bgcolor=HEAD)
        table.cell(hud, 0, 1, '  ' + hTx + '  ', text_color=color.white, text_size=size.large, text_halign=text.align_left, bgcolor=hBg)
        table.merge_cells(hud, 0, 1, 1, 1)

        rowL(hud, 2, 'Entry', px(tEntry) if active else '—', TXT, CARD, ts)
        rowL(hud, 3, 'Stop', px(tSL) + '   −' + money(riskMoney) if active else '—', RISK, CARD2, ts)

        rowL(hud, 4, 'TP1 · ' + string.tostring(r1, '#.##') + 'R', ('✓  ' if tStage >= 1 else '') + px(tTP1) if active else '—', GOLD, CARD, ts)
        rowL(hud, 5, 'TP2 · ' + string.tostring(r2, '#.##') + 'R', ('✓  ' if tStage >= 2 else '') + px(tTP2) if active else '—', GOLD, CARD2, ts)
        rowL(hud, 6, 'TP3 · ' + string.tostring(r3, '#.##') + 'R', px(tTP3) if active else '—', GOLD, CARD, ts)
        rowL(hud, 7, 'Position', sizeTxt(tSize) if active else '—', UP, CARD2, ts)
        rowL(hud, 8, 'Risk', money(riskMoney) + '  ·  ' + string.tostring(riskPct, '#.##') + '%', TXT, CARD, ts)
        rowL(hud, 9, 'Now', ('+' if liveR >= 0 else '') + string.tostring(liveR, '0.0') + ' R' if active and (not na(liveR)) else '—', (UP if liveR >= 0 else RISK) if active and (not na(liveR)) else MUTE, CARD2, ts)
        rowL(hud, 10, 'Last plan', '—' if lastOut == '' else lastOut, MUTE, CARD, ts)

    def planMsg(side: str):
        return syminfo.ticker + ' ' + side + ' @ ' + px(tEntry) + ' | SL ' + px(tSL) + ' | TP1 ' + px(tTP1) + ' | TP2 ' + px(tTP2) + ' | TP3 ' + px(tTP3) + ' | size ' + sizeTxt(tSize)

    if longSig:
        alert('LunqFX Trade Planner: ' + planMsg('BUY'), alert.freq_once_per_bar_close)
    if shortSig:
        alert('LunqFX Trade Planner: ' + planMsg('SELL'), alert.freq_once_per_bar_close)
    if hitTP1 or hitTP2 or hitTP3:
        alert('LunqFX Trade Planner: ' + syminfo.ticker + (' TP3' if hitTP3 else ' TP2' if hitTP2 else ' TP1') + ' reached', alert.freq_once_per_bar_close)
    if hitSL:
        alert('LunqFX Trade Planner: ' + syminfo.ticker + ' stop reached', alert.freq_once_per_bar_close)

    alertcondition(longSig, 'Buy plan', 'LunqFX Trade Planner: new BUY plan')
    alertcondition(shortSig, 'Sell plan', 'LunqFX Trade Planner: new SELL plan')
    alertcondition(hitTP1 or hitTP2 or hitTP3, 'Target reached', 'LunqFX Trade Planner: a target was reached')
    alertcondition(hitSL, 'Stop reached', 'LunqFX Trade Planner: the stop was reached')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)