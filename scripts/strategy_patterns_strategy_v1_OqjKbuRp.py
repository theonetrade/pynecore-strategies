"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop
from pynecore.lib import (
    alert, alertcondition, bar_index, barcolor, barstate, close, color,
    format, high, input, label, location, low, math, na, nz, open, plot, plotcandle, plotshape,
    position, script, shape, size, strategy, string, syminfo, ta, table, time, timeframe, yloc
)
from pynecore.types import Persistent, Series, Table

gP: str = "① Patterns"
gE: str = "② Entry / SL / Target"
gL: str = "③ Limits & Filters"
gS: str = "④ Position Sizing"
gV: str = "⑤ Visuals"


@script.strategy(title="PA Patterns Strategy v2", shorttitle="PA Patterns v2", overlay=True, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, pyramiding=0, calc_on_order_fills=False, process_orders_on_close=False, commission_type=strategy.commission.percent, commission_value=0.03, slippage=1, margin_long=0, margin_short=0, max_labels_count=500, max_lines_count=500)
def main(
    useEngulf=input.bool(True, "Enable Engulfing patterns", group=gP),
    useStar=input.bool(True, "Enable Morning / Evening Star", group=gP),
    minEngBodyPct=input.float(50.0, "Engulfing: min body % of candle range", minval=10, maxval=100, step=5, group=gP),
    strictEngulf=input.bool(True, "Engulfing: body must FULLY engulf prior body", group=gP),
    engNeedClose=input.bool(True, "Engulfing: close beyond prior open", group=gP),
    smallBodyPct=input.float(35.0, "Star: middle candle max body %", minval=5, maxval=60, group=gP),
    strongBodyPct=input.float(55.0, "Star: outer candles min body %", minval=20, maxval=90, group=gP),
    penetrationPct=input.float(50.0, "Star: required penetration %", minval=20, maxval=100, group=gP),
    entryMode=input.string("Stop order", "Entry mode", options=("Stop order", "Market on break"), group=gE, tooltip="Stop order  = resting buy/sell stop at the trigger price (exact fills)\nMarket on break = waits for a bar to break the level, enters at next bar open (always executes)"),
    entryBufTicks=input.int(2, "Entry buffer (ticks beyond trigger)", minval=0, group=gE),
    slBufTicks=input.int(2, "SL buffer (ticks beyond pattern)", minval=0, group=gE),
    slWholePattern=input.bool(True, "Engulfing SL uses BOTH candles", group=gE),
    validBars=input.int(5, "Pending entry valid for N bars", minval=1, maxval=50, group=gE),
    cancelOnBreak=input.bool(False, "Cancel pending if SL level breaks first", group=gE),
    minStopTicks=input.int(5, "Minimum stop distance (ticks)", minval=1, group=gE),
    useTP1=input.bool(True, "Use partial TP1", group=gE),
    tp1R=input.float(1.5, "TP1 (R multiple)", minval=0.5, step=0.1, group=gE),
    tp1Qty=input.int(50, "TP1 size (% of position)", minval=1, maxval=99, group=gE),
    tp2R=input.float(2.0, "TP2 / final target (R multiple)", minval=0.5, step=0.1, group=gE),
    moveBE=input.bool(True, "Move SL to break-even after TP1", group=gE),
    beOffsetTicks=input.int(2, "Break-even offset (ticks)", minval=0, group=gE),
    maxTradesDay=input.int(1, "MAX TRADES PER DAY", minval=1, maxval=50, group=gL),
    maxLossesDay=input.int(0, "Stop trading after N losses (0 = off)", minval=0, maxval=20, group=gL),
    onePerDay=input.bool(False, "Only FIRST pattern of the day", group=gL),
    allowLong=input.bool(True, "Allow LONG trades", group=gL),
    allowShort=input.bool(True, "Allow SHORT trades", group=gL),
    useSession=input.bool(False, "Restrict to session", group=gL),
    sess=input.session("0915-1500", "Trading session", group=gL),
    closeEOD=input.bool(False, "Close open trade at session end", group=gL),
    useTrendFilter=input.bool(False, "Only trade with EMA trend", group=gL),
    emaLen=input.int(200, "Trend EMA length", minval=5, group=gL),
    useRiskSizing=input.bool(False, "Size position by risk %", group=gS),
    riskPct=input.float(1.0, "Risk per trade (% of equity)", minval=0.1, maxval=100, step=0.1, group=gS),
    lotSize=input.int(65, "Lot size (units per lot)", minval=1, group=gS, tooltip="NSE Nifty 50 lot size = 65 units (effective Jan 2026). Change if trading a different instrument."),
    fixedLots=input.int(1, "Fixed number of lots (used when risk sizing is OFF)", minval=1, group=gS),
    maxQty=input.float(0, "Max units per trade (0 = unlimited)", minval=0, group=gS),
    whiteCandles=input.bool(True, "Paint pattern candle body WHITE", group=gV),
    colorWhole=input.bool(True, "Paint ALL candles of the pattern", group=gV),
    whiteCol=input.color(color.white, "Body color", group=gV),
    borderCol=input.color(color.new(color.new('#787B86'), 0), "Border / wick color", group=gV),
    showMarkers=input.bool(True, "Show pattern markers", group=gV),
    showLabels=input.bool(True, "Show pattern name labels", group=gV),
    showLevels=input.bool(True, "Plot Entry / SL / TP levels", group=gV),
    showTable=input.bool(True, "Show dashboard", group=gV),
    debugMode=input.bool(True, "DEBUG: show engine counters", group=gV)
):
    tick = syminfo.mintick

    body0 = math.abs(close - open)
    body1 = math.abs(close[1] - open[1])
    body2 = math.abs(close[2] - open[2])
    rng0 = high - low
    rng1 = high[1] - low[1]
    rng2 = high[2] - low[2]

    bodyPct0 = body0 / rng0 * 100 if rng0 > 0 else 0.0
    bodyPct1 = body1 / rng1 * 100 if rng1 > 0 else 0.0
    bodyPct2 = body2 / rng2 * 100 if rng2 > 0 else 0.0

    bull0 = close > open
    bear0 = close < open
    bull1 = close[1] > open[1]
    bear1 = close[1] < open[1]
    bull2 = close[2] > open[2]
    bear2 = close[2] < open[2]

    engBodyOK = bodyPct0 >= minEngBodyPct

    bullEngRaw = useEngulf and bear1 and bull0 and engBodyOK and (open < close[1] and close > open[1] if strictEngulf else open <= close[1] and close >= open[1]) and (not engNeedClose or close > open[1])

    bearEngRaw = useEngulf and bull1 and bear0 and engBodyOK and (open > close[1] and close < open[1] if strictEngulf else open >= close[1] and close <= open[1]) and (not engNeedClose or close < open[1])

    smallMiddle = bodyPct1 <= smallBodyPct
    strongFirst = bodyPct2 >= strongBodyPct
    strongThird = bodyPct0 >= strongBodyPct
    midBull = open[2] - body2 * (penetrationPct / 100)
    midBear = open[2] + body2 * (penetrationPct / 100)

    morningRaw = useStar and bear2 and smallMiddle and strongFirst and bull0 and strongThird and (close > midBull)
    eveningRaw = useStar and bull2 and smallMiddle and strongFirst and bear0 and strongThird and (close < midBear)

    ema = ta.ema(close, emaLen)
    trendUp = not useTrendFilter or close > ema
    trendDn = not useTrendFilter or close < ema

    wasInSess: Series = not na(time(timeframe.period, sess))
    inSess = not useSession or wasInSess
    sessClosed = useSession and (not wasInSess) and wasInSess[1]

    newDay = ta.change(time('D')) != 0

    tradesToday: Persistent[int] = 0
    lossesToday: Persistent[int] = 0
    firedToday: Persistent[bool] = False
    lastClosedCnt: Persistent[int] = 0

    totalEntries: Series = strategy.opentrades + strategy.closedtrades
    newEntries = totalEntries - nz(totalEntries[1], totalEntries)

    if strategy.closedtrades > lastClosedCnt:
        __loop_1__ = pine_loop(lastClosedCnt)
        while __loop_1__.step(strategy.closedtrades - 1):
            i = __loop_1__.value
            if strategy.closedtrades.profit(i) < 0:
                lossesToday += 1
        lastClosedCnt = strategy.closedtrades

    if newEntries > 0:
        tradesToday += newEntries

    if newDay:
        tradesToday = 0
        lossesToday = 0
        firedToday = False

    lossLimitHit = maxLossesDay > 0 and lossesToday >= maxLossesDay
    dayLimitHit = tradesToday >= maxTradesDay or lossLimitHit or (onePerDay and firedToday)

    bullSig = (bullEngRaw or morningRaw) and trendUp and allowLong
    bearSig = (bearEngRaw or eveningRaw) and trendDn and allowShort

    patName = 'Morning Star' if morningRaw else 'Bullish Engulfing' if bullEngRaw else 'Evening Star' if eveningRaw else 'Bearish Engulfing' if bearEngRaw else ''

    sigTrig: float = na(float)
    sigStop: float = na(float)

    if bullSig:
        sigTrig = high + entryBufTicks * tick
        sigStop = (math.min(low, math.min(low[1], low[2])) if morningRaw else math.min(low, low[1]) if slWholePattern else low) - slBufTicks * tick

        if sigTrig - sigStop < minStopTicks * tick:
            sigStop = sigTrig - minStopTicks * tick

    if bearSig:
        sigTrig = low - entryBufTicks * tick
        sigStop = (math.max(high, math.max(high[1], high[2])) if eveningRaw else math.max(high, high[1]) if slWholePattern else high) + slBufTicks * tick
        if sigStop - sigTrig < minStopTicks * tick:
            sigStop = sigTrig + minStopTicks * tick

    pendDir: Persistent[int] = 0
    pTrig: Persistent[float] = na(float)
    pStop: Persistent[float] = na(float)
    pAge: Persistent[int] = 0
    pName: Persistent[str] = ""

    cSig: Persistent[int] = 0
    cPlaced: Persistent[int] = 0
    cFilled: Persistent[int] = 0
    cExp: Persistent[int] = 0
    cInv: Persistent[int] = 0
    cBlk: Persistent[int] = 0
    lastSkip: Persistent[str] = "-"

    flat = strategy.position_size == 0
    inLong = strategy.position_size > 0
    inShrt = strategy.position_size < 0

    actSL: Persistent[float] = na(float)
    actR: Persistent[float] = na(float)
    tp1Done: Persistent[bool] = False

    if newEntries > 0:
        cFilled += 1
        actSL = pStop
        actR = math.abs(strategy.position_avg_price - pStop)
        tp1Done = False
        pendDir = 0
        pAge = 0

    if pendDir != 0:
        pAge += 1
        expired: bool = pAge > validBars
        invalid: bool = cancelOnBreak and (low <= pStop if pendDir == 1 else high >= pStop)
        blockedNow: bool = dayLimitHit or not inSess or newDay or (not flat)
        if expired or invalid or blockedNow:
            strategy.cancel('Long')
            strategy.cancel('Short')
            if expired:
                cExp += 1
                lastSkip = "expired"
            elif invalid:
                cInv += 1
                lastSkip = "SL broke first"
            else:
                cBlk += 1
                lastSkip = "blocked"
            pendDir = 0
            pAge = 0

    def calcQty(stopDist: float):
        q: float = na(float)
        if useRiskSizing and stopDist > 0:
            rawLots = strategy.equity * riskPct / 100 / stopDist / lotSize
            lots = math.max(1, math.floor(rawLots))
            q = lots * lotSize
            if maxQty > 0 and q > maxQty:
                q = math.max(lotSize, math.floor(maxQty / lotSize) * lotSize)
        else:
            q = fixedLots * lotSize
        return q

    canArm = flat and pendDir == 0 and (not dayLimitHit) and inSess

    if bullSig or bearSig:
        cSig += 1
        if not canArm:
            lastSkip = 'in position' if not flat else 'day limit' if dayLimitHit else 'out of session' if not inSess else 'pending exists'

    if canArm and bullSig and (not na(sigTrig)):
        pendDir = 1
        pTrig = sigTrig
        pStop = sigStop
        pName = patName
        pAge = 0
        firedToday = True if onePerDay else firedToday

    if canArm and bearSig and (not na(sigTrig)) and (pendDir == 0):
        pendDir = -1
        pTrig = sigTrig
        pStop = sigStop
        pName = patName
        pAge = 0
        firedToday = True if onePerDay else firedToday

    if pendDir != 0 and flat:
        q: float = calcQty(math.abs(pTrig - pStop))
        if entryMode == 'Stop order':
            if pendDir == 1:
                strategy.entry('Long', strategy.long, qty=q, stop=pTrig, comment=pName)
            else:
                strategy.entry('Short', strategy.short, qty=q, stop=pTrig, comment=pName)
            if pAge == 0:
                cPlaced += 1
        else:
            hit: bool = high >= pTrig if pendDir == 1 else low <= pTrig
            if hit:
                if pendDir == 1:
                    strategy.entry('Long', strategy.long, qty=q, comment=pName)
                else:
                    strategy.entry('Short', strategy.short, qty=q, comment=pName)
                cPlaced += 1

    entryPx = strategy.position_avg_price
    rOK = not na(actR) and actR > 0
    tp1Px = entryPx + actR * tp1R if rOK and inLong else entryPx - actR * tp1R if rOK and inShrt else na
    tp2Px = entryPx + actR * tp2R if rOK and inLong else entryPx - actR * tp2R if rOK and inShrt else na

    if useTP1 and rOK and (not tp1Done) and (not flat):
        if inLong and high >= tp1Px or (inShrt and low <= tp1Px):
            tp1Done = True
            if moveBE:
                actSL = entryPx + beOffsetTicks * tick if inLong else entryPx - beOffsetTicks * tick

    if not flat and rOK:
        fromId: str = 'Long' if inLong else 'Short'
        if useTP1:
            strategy.exit('TP1', from_entry=fromId, qty_percent=tp1Qty, limit=tp1Px, stop=actSL, comment_profit='TP1', comment_loss='SL')
            strategy.exit('TP2', from_entry=fromId, limit=tp2Px, stop=actSL, comment_profit='TP2', comment_loss='SL')
        else:
            strategy.exit('TP', from_entry=fromId, limit=tp2Px, stop=actSL, comment_profit='TP', comment_loss='SL')

    if closeEOD and sessClosed:
        strategy.close_all(comment='EOD')
        strategy.cancel('Long')
        strategy.cancel('Short')

    sigBar = (bullSig or bearSig) and whiteCandles
    twoBar = sigBar and colorWhole
    threeBar = sigBar and colorWhole and (morningRaw or eveningRaw)

    plotcandle(open, high, low, close, title='Pattern Candle', color=whiteCol if sigBar else na, wickcolor=borderCol if sigBar else na, bordercolor=borderCol if sigBar else na)

    barcolor(whiteCol if twoBar else na, offset=-1, title='Pattern Candle -1')
    barcolor(whiteCol if threeBar else na, offset=-2, title='Pattern Candle -2')

    plotshape(showMarkers and bullSig, title='Bull Signal', style=shape.triangleup, location=location.belowbar, color=color.new(color.lime, 0), size=size.tiny)
    plotshape(showMarkers and bearSig, title='Bear Signal', style=shape.triangledown, location=location.abovebar, color=color.new(color.red, 0), size=size.tiny)

    if showLabels and (bullSig or bearSig):
        label.new(bar_index, low if bullSig else high, patName, yloc=yloc.belowbar if bullSig else yloc.abovebar, style=label.style_label_up if bullSig else label.style_label_down, color=color.new(color.black, 20), textcolor=color.white, size=size.small)

    plotTrig = pTrig if showLevels and pendDir != 0 else na
    plotEntr = entryPx if showLevels and (not flat) else na
    plotStop = (actSL if not flat else pStop if pendDir != 0 else na) if showLevels else na
    plotTP1 = tp1Px if showLevels and (not flat) and useTP1 else na
    plotTP2 = tp2Px if showLevels and (not flat) else na

    plot(plotTrig, 'Trigger', color=color.new(color.orange, 0), style=plot.style_linebr)
    plot(plotEntr, 'Entry', color=color.new(color.blue, 0), style=plot.style_linebr)
    plot(plotStop, 'Stop', color=color.new(color.red, 0), style=plot.style_linebr)
    plot(plotTP1, 'TP1', color=color.new(color.teal, 0), style=plot.style_linebr)
    plot(plotTP2, 'TP2', color=color.new(color.green, 0), style=plot.style_linebr)
    plot(ema if useTrendFilter else na, 'Trend EMA', color=color.new(color.gray, 40))

    dash: Persistent[Table] = table.new(position.top_right, 2, 12, border_width=1)

    if showTable and barstate.islast:
        stateTxt = 'LONG' if inLong else 'SHORT' if inShrt else 'Pending Long' if pendDir == 1 else 'Pending Short' if pendDir == -1 else 'Flat'
        stateCol = color.new(color.green, 70) if inLong else color.new(color.red, 70) if inShrt else color.new(color.orange, 70) if pendDir != 0 else color.new(color.gray, 70)

        table.cell(dash, 0, 0, 'PA PATTERNS v2', bgcolor=color.new(color.black, 20), text_color=color.white, text_size=size.small)
        table.cell(dash, 1, 0, stateTxt, bgcolor=stateCol, text_color=color.white, text_size=size.small)

        table.cell(dash, 0, 1, 'Trades today', text_size=size.small)
        table.cell(dash, 1, 1, string.tostring(tradesToday) + ' / ' + string.tostring(maxTradesDay), text_size=size.small)

        table.cell(dash, 0, 2, 'Losses today', text_size=size.small)
        table.cell(dash, 1, 2, string.tostring(lossesToday) + (' / ' + string.tostring(maxLossesDay) if maxLossesDay > 0 else ''), text_size=size.small)

        table.cell(dash, 0, 3, 'Last pattern', text_size=size.small)
        table.cell(dash, 1, 3, '-' if pName == '' else pName, text_size=size.small)

        table.cell(dash, 0, 4, 'Risk (1R)', text_size=size.small)
        table.cell(dash, 1, 4, string.tostring(actR, format.mintick) if rOK else '-', text_size=size.small)

        table.cell(dash, 0, 5, 'Net profit', text_size=size.small)
        table.cell(dash, 1, 5, string.tostring(strategy.netprofit, '#.##'), text_size=size.small, text_color=color.green if strategy.netprofit >= 0 else color.red)

        if debugMode:
            table.cell(dash, 0, 6, '— DEBUG —', bgcolor=color.new(color.black, 40), text_color=color.white, text_size=size.small)
            table.cell(dash, 1, 6, '', bgcolor=color.new(color.black, 40), text_size=size.small)

            table.cell(dash, 0, 7, 'Signals seen', text_size=size.small)
            table.cell(dash, 1, 7, string.tostring(cSig), text_size=size.small)

            table.cell(dash, 0, 8, 'Orders placed', text_size=size.small)
            table.cell(dash, 1, 8, string.tostring(cPlaced), text_size=size.small)

            table.cell(dash, 0, 9, 'Fills', text_size=size.small)
            table.cell(dash, 1, 9, string.tostring(cFilled), text_size=size.small)

            table.cell(dash, 0, 10, 'Exp / Inv / Blk', text_size=size.small)
            table.cell(dash, 1, 10, string.tostring(cExp) + ' / ' + string.tostring(cInv) + ' / ' + string.tostring(cBlk), text_size=size.small)

            table.cell(dash, 0, 11, 'Last skip reason', text_size=size.small)
            table.cell(dash, 1, 11, lastSkip, text_size=size.small)

    alertcondition(bullEngRaw, 'Bullish Engulfing', 'Bullish Engulfing detected')
    alertcondition(bearEngRaw, 'Bearish Engulfing', 'Bearish Engulfing detected')
    alertcondition(morningRaw, 'Morning Star', 'Morning Star detected')
    alertcondition(eveningRaw, 'Evening Star', 'Evening Star detected')
    alertcondition(bullSig, 'Any Long Setup', 'Long setup armed')
    alertcondition(bearSig, 'Any Short Setup', 'Short setup armed')

    if bullSig:
        alert('LONG setup: ' + patName + ' | Entry > ' + string.tostring(sigTrig, format.mintick) + ' | SL ' + string.tostring(sigStop, format.mintick), alert.freq_once_per_bar_close)
    if bearSig:
        alert('SHORT setup: ' + patName + ' | Entry < ' + string.tostring(sigTrig, format.mintick) + ' | SL ' + string.tostring(sigStop, format.mintick), alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)