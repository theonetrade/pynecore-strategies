"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_float
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barstate, box, close, color, currency, high, input,
    label, line, low, math, na, open, position, script, size, strategy, string, ta, table, text,
    time, timeframe, volume
)
from pynecore.types import Box, Color, Line, NA, Persistent, Table


@udt
class Level:
    price: float = na(float)
    bar: int = na(int)
    zone: Box = na(Box)
    mid: Line = na(Line)


@udt
class TradeVisual:
    enLine: Line = na(Line)
    slLine: Line = na(Line)
    tpLine: Line = na(Line)
    bornBar: int = na(int)
    isOpen: bool = na(bool)


grpCore: str = "Swing Detection"
grpTrade: str = "Trade Management"
grpFilt: str = "Filters"
grpVis: str = "Visuals"
grpDash: str = "Dashboard"


@script.strategy("Liquidity Sweep Reversal Strategy", "Sweep Reversal Strategy", overlay=True, max_boxes_count=600, max_lines_count=500, max_labels_count=300, default_qty_type=strategy.percent_of_equity, default_qty_value=10, initial_capital=10000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0.04, slippage=1)
def main(
    pivotLen=input.int(7, "Pivot Lookback (L/R bars)", minval=2, group=grpCore),
    maxAge=input.int(150, "Level Max Age (bars)", minval=20, group=grpCore),
    minGapATR=input.float(0.25, "Min Level Spacing (x ATR)", minval=0, step=0.05, group=grpCore),
    slAtrMult=input.float(1.2, "Stop Loss (x ATR beyond wick)", minval=0.1, step=0.1, group=grpTrade),
    minRiskATR=input.float(0.5, "Min Stop Distance (x ATR)", minval=0, step=0.1, group=grpTrade),
    rrRatio=input.float(1.5, "Reward:Risk Ratio", minval=0.5, step=0.25, group=grpTrade),
    useBreakeven=input.bool(True, "Move Stop to Breakeven", group=grpTrade),
    breakevenAtPct=input.float(50, "Breakeven Trigger (% to TP)", minval=10, maxval=90, group=grpTrade),
    allowLongs=input.bool(True, "Allow Longs (sweep-low)", group=grpTrade),
    allowShorts=input.bool(True, "Allow Shorts (sweep-high)", group=grpTrade),
    useVolFilt=input.bool(True, "Require Volume Spike on Sweep", group=grpFilt),
    volMult=input.float(1.3, "Volume SMA Multiplier", minval=1, step=0.1, group=grpFilt),
    useWickFilt=input.bool(True, "Require Strong Rejection Wick", group=grpFilt, tooltip="Sweep bar's wick beyond the level must be at least this many times its body size."),
    minWickRatio=input.float(1.5, "Min Wick:Body Ratio", minval=0.5, step=0.1, group=grpFilt),
    useConfirm=input.bool(True, "Require Next-Bar Confirmation", group=grpFilt, tooltip="Waits one extra bar after the sweep and only enters if price continues in the reversal direction past the sweep bar's midpoint. Reduces whipsaw entries."),
    useSession=input.bool(True, "Restrict to Session Window", group=grpFilt),
    sessWindow=input.session("1200-1600", "Session (Exchange TZ)", group=grpFilt, tooltip="Default is the London/NY overlap — the highest-liquidity window, not just 'business hours'."),
    bullCol=input.color(color.new('#26A69A'), "Bullish (Low) Sweep Color", group=grpVis),
    bearCol=input.color(color.new('#EF5350'), "Bearish (High) Sweep Color", group=grpVis),
    zoneTransp=input.int(85, "Zone Fill Transparency", minval=0, maxval=100, group=grpVis),
    showZones=input.bool(True, "Show Liquidity Zones", group=grpVis),
    showTradeLvls=input.bool(True, "Show Entry/SL/TP Lines (all trades)", group=grpVis),
    tradeLineMaxAge=input.int(200, "Trade Line Max Age (bars)", minval=20, group=grpVis, tooltip="How long a closed trade's entry/SL/TP lines remain on the chart before being removed."),
    showLabels=input.bool(True, "Show Trade Labels", group=grpVis),
    showDash=input.bool(True, "Show Dashboard", group=grpDash),
    dashPos=input.string("Top Right", "Position", options=("Top Right", "Bottom Right", "Bottom Left"), group=grpDash),
    dashSize=input.string("Small", "Size", options=("Tiny", "Small", "Normal", "Large"), group=grpDash)
):
    DATA: Color = color.new('#DBDBDB')
    HEADERS: Color = color.new('#808080')
    BG: Color = color.new('#161616')
    BORDERS: Color = color.new('#2E2E2E')
    GOLD: Color = color.new('#EAB308')

    atr = ta.atr(14)
    volSMA = ta.sma(volume, 20)

    pivH = ta.pivothigh(high, pivotLen, pivotLen)
    pivL = ta.pivotlow(low, pivotLen, pivotLen)

    inSession: bool = not na(time(timeframe.period, sessWindow))

    parsedPos: Persistent = position.top_right if dashPos == 'Top Right' else position.bottom_right if dashPos == 'Bottom Right' else position.bottom_left
    parsedSize: Persistent = size.tiny if dashSize == 'Tiny' else size.small if dashSize == 'Small' else size.normal if dashSize == 'Normal' else size.large

    highs: Persistent[list[Level]] = array.new(0, NA(Level))
    lows: Persistent[list[Level]] = array.new(0, NA(Level))

    tradeVisuals: Persistent[list[TradeVisual]] = array.new(0, NA(TradeVisual))
    openVisualIdx: Persistent[int] = -1

    wins: Persistent[int] = 0
    losses: Persistent[int] = 0
    totalTrades: Persistent[int] = 0
    activeSL: Persistent[float] = na(float)
    activeTP: Persistent[float] = na(float)
    activeEntry: Persistent[float] = na(float)
    beDone: Persistent[bool] = False

    pendingLong: Persistent[bool] = False
    pendingShort: Persistent[bool] = False
    pendingWick: Persistent[float] = na(float)
    pendingMid: Persistent[float] = na(float)

    def tooClose(arr: list[Level], px: float):
        close_: bool = False
        for lv in arr:
            if math.abs(lv.price - px) < atr * minGapATR:
                close_ = True
        return close_

    if not na(pivH):
        px: float = pivH
        if not tooClose(highs, px):
            bx = box.new(bar_index - pivotLen, px, bar_index, px - atr * 0.3, bgcolor=color.new(bearCol, zoneTransp), border_color=color.new(bearCol, 60), border_width=1) if showZones else na
            ml = line.new(bar_index - pivotLen, px, bar_index, px, color=color.new(bearCol, 25), style=line.style_dotted) if showZones else na
            array.push(highs, Level(px, bar_index - pivotLen, bx, ml))

    if not na(pivL):
        px: float = pivL
        if not tooClose(lows, px):
            bx = box.new(bar_index - pivotLen, px + atr * 0.3, bar_index, px, bgcolor=color.new(bullCol, zoneTransp), border_color=color.new(bullCol, 60), border_width=1) if showZones else na
            ml = line.new(bar_index - pivotLen, px, bar_index, px, color=color.new(bullCol, 25), style=line.style_dotted) if showZones else na
            array.push(lows, Level(px, bar_index - pivotLen, bx, ml))

    sweepHighSignal: bool = False
    sweepHighWick: float = na(float)

    hi: int = 0
    while hi < array.size(highs):
        lv = array.get(highs, hi)
        if showZones:
            box.set_right(lv.zone, bar_index)
            line.set_x2(lv.mid, bar_index)

        wicked: bool = high > lv.price and close < lv.price
        body: float = math.abs(close - open)
        wickSz: float = high - math.max(close, open)
        wickOK: bool = not useWickFilt or (body > 0 and wickSz / body >= minWickRatio) or (body == 0 and wickSz > 0)
        volOK: bool = not useVolFilt or volume > volSMA * volMult
        aged: bool = bar_index - lv.bar > maxAge

        if wicked and volOK and wickOK:
            sweepHighSignal = True
            sweepHighWick = math.max(high if na(sweepHighWick) else sweepHighWick, high)
            box.delete(lv.zone)
            line.delete(lv.mid)
            array.remove(highs, hi)
        elif aged:
            box.delete(lv.zone)
            line.delete(lv.mid)
            array.remove(highs, hi)
        else:
            hi += 1

    sweepLowSignal: bool = False
    sweepLowWick: float = na(float)

    li: int = 0
    while li < array.size(lows):
        lv = array.get(lows, li)
        if showZones:
            box.set_right(lv.zone, bar_index)
            line.set_x2(lv.mid, bar_index)

        wicked: bool = low < lv.price and close > lv.price
        body: float = math.abs(close - open)
        wickSz: float = math.min(close, open) - low
        wickOK: bool = not useWickFilt or (body > 0 and wickSz / body >= minWickRatio) or (body == 0 and wickSz > 0)
        volOK: bool = not useVolFilt or volume > volSMA * volMult
        aged: bool = bar_index - lv.bar > maxAge

        if wicked and volOK and wickOK:
            sweepLowSignal = True
            sweepLowWick = math.min(low if na(sweepLowWick) else sweepLowWick, low)
            box.delete(lv.zone)
            line.delete(lv.mid)
            array.remove(lows, li)
        elif aged:
            box.delete(lv.zone)
            line.delete(lv.mid)
            array.remove(lows, li)
        else:
            li += 1

    def calcTradeLevels(isLong: bool, wickLvl: float):
        sl: float = wickLvl - atr * slAtrMult if isLong else wickLvl + atr * slAtrMult
        risk: float = close - sl if isLong else sl - close
        qualifies: bool = risk >= atr * minRiskATR
        tp: float = (close + risk * rrRatio if isLong else close - risk * rrRatio) if qualifies else na
        return (qualifies, sl, tp)

    doLong: bool = False
    doShort: bool = False
    wickLvl: float = na(float)
    sessionOK: bool = not useSession or inSession

    if strategy.position_size == 0:
        if useConfirm:
            if pendingLong and close > pendingMid and allowLongs and sessionOK:
                doLong = True
                wickLvl = pendingWick
            if pendingShort and close < pendingMid and allowShorts and sessionOK:
                doShort = True
                wickLvl = pendingWick
            pendingLong = False
            pendingShort = False

            if sweepLowSignal:
                pendingLong = True
                pendingWick = sweepLowWick
                pendingMid = math.avg(sweepLowWick, close)
            if sweepHighSignal:
                pendingShort = True
                pendingWick = sweepHighWick
                pendingMid = math.avg(sweepHighWick, close)
        else:
            if sweepLowSignal and allowLongs and sessionOK:
                doLong = True
                wickLvl = sweepLowWick
            if sweepHighSignal and allowShorts and sessionOK:
                doShort = True
                wickLvl = sweepHighWick

    if doLong or doShort:
        isLong: bool = doLong
        qualifies, sl, tp = calcTradeLevels(isLong, wickLvl)
        if qualifies:
            strategy.entry('Long' if isLong else 'Short', strategy.long if isLong else strategy.short)
            strategy.exit('Long Exit' if isLong else 'Short Exit', 'Long' if isLong else 'Short', stop=sl, limit=tp)
            activeSL = sl
            activeTP = tp
            activeEntry = close
            beDone = False

            if showTradeLvls:
                enL = line.new(bar_index, close, bar_index, close, color=color.new(DATA, 20), style=line.style_dashed)
                slL = line.new(bar_index, sl, bar_index, sl, color=color.new(bearCol, 10), width=1)
                tpL = line.new(bar_index, tp, bar_index, tp, color=color.new(bullCol, 10), width=1)
                array.push(tradeVisuals, TradeVisual(enL, slL, tpL, bar_index, True))
                openVisualIdx = array.size(tradeVisuals) - 1
            if showLabels:
                label.new(bar_index, low if isLong else high, 'LONG' if isLong else 'SHORT', style=label.style_label_up if isLong else label.style_label_down, color=color.new(bullCol if isLong else bearCol, 10), textcolor=color.white, size=size.tiny)

    if showTradeLvls and openVisualIdx >= 0 and (openVisualIdx < array.size(tradeVisuals)):
        tv = array.get(tradeVisuals, openVisualIdx)
        if tv.isOpen:
            line.set_x2(tv.enLine, bar_index)
            line.set_x2(tv.slLine, bar_index)
            line.set_x2(tv.tpLine, bar_index)

    if strategy.position_size != 0 and useBreakeven and (not beDone) and (not na(activeEntry)):
        isLongPos: bool = strategy.position_size > 0
        triggerLvl: float = activeEntry + (activeTP - activeEntry) * (breakevenAtPct / 100.0) if isLongPos else activeEntry - (activeEntry - activeTP) * (breakevenAtPct / 100.0)
        hit: bool = high >= triggerLvl if isLongPos else low <= triggerLvl
        if hit:
            strategy.exit('Long Exit' if isLongPos else 'Short Exit', 'Long' if isLongPos else 'Short', stop=activeEntry, limit=activeTP)
            if showTradeLvls and openVisualIdx >= 0 and (openVisualIdx < array.size(tradeVisuals)):
                tv = array.get(tradeVisuals, openVisualIdx)
                line.set_y1(tv.slLine, activeEntry)
                line.set_y2(tv.slLine, activeEntry)
            beDone = True

    if strategy.position_size == 0 and openVisualIdx >= 0 and (openVisualIdx < array.size(tradeVisuals)):
        tv = array.get(tradeVisuals, openVisualIdx)
        if tv.isOpen and bar_index > tv.bornBar:
            tv.isOpen = False
            openVisualIdx = -1

    if showTradeLvls and barstate.isconfirmed:
        ti: int = 0
        while ti < array.size(tradeVisuals):
            tv = array.get(tradeVisuals, ti)
            tooOld: bool = not tv.isOpen and bar_index - tv.bornBar > tradeLineMaxAge
            if tooOld:
                line.delete(tv.enLine)
                line.delete(tv.slLine)
                line.delete(tv.tpLine)
                array.remove(tradeVisuals, ti)
                if ti < openVisualIdx:
                    openVisualIdx -= 1
            else:
                ti += 1

    if strategy.closedtrades > strategy.closedtrades[1]:
        totalTrades += 1
        lastPL: float = strategy.closedtrades.profit(strategy.closedtrades - 1)
        if lastPL > 0:
            wins += 1
        else:
            losses += 1

    def cell(t: Table, c: int, r: int, txt: str, clr: Color = color.new('#DBDBDB'), align = text.align_right, bg: Color = na, h: float = 0):
        return table.cell(t, c, r, txt, text_color=clr, text_size=parsedSize, text_halign=align, bgcolor=bg, height=h)

    def divider(t: Table, r: int):
        table.merge_cells(t, 0, r, 1, r)
        return cell(t, 0, r, '━━━━━━━━━━━━━━', align=text.align_center, h=0.5, clr=BORDERS)

    d: Persistent[Table] = table.new(parsedPos, 2, 9, bgcolor=BG, border_width=0, frame_color=BORDERS, frame_width=1)

    if showDash and barstate.islast:
        winRate: float = wins / cast_float(totalTrades) * 100 if totalTrades > 0 else 0

        table.merge_cells(d, 0, 0, 1, 0)
        cell(d, 0, 0, 'Sweep Reversal Strategy', align=text.align_center)
        divider(d, 1)

        cell(d, 0, 2, 'Total Trades', clr=HEADERS, align=text.align_left)
        cell(d, 1, 2, string.tostring(totalTrades))
        cell(d, 0, 3, 'Wins / Losses', clr=HEADERS, align=text.align_left)
        cell(d, 1, 3, string.tostring(wins) + ' / ' + string.tostring(losses))

        divider(d, 4)

        cell(d, 0, 5, 'Win Rate', clr=HEADERS, align=text.align_left)
        cell(d, 1, 5, string.tostring(math.round(winRate, 1)) + '%', clr=bullCol if winRate >= 50 else bearCol)
        cell(d, 0, 6, 'Net Profit', clr=HEADERS, align=text.align_left)
        cell(d, 1, 6, string.tostring(math.round(strategy.netprofit, 2)), clr=bullCol if strategy.netprofit >= 0 else bearCol)

        divider(d, 7)

        cell(d, 0, 8, 'Position', clr=HEADERS, align=text.align_left)
        cell(d, 1, 8, 'LONG' if strategy.position_size > 0 else 'SHORT' if strategy.position_size < 0 else 'FLAT', clr=bullCol if strategy.position_size > 0 else bearCol if strategy.position_size < 0 else GOLD)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
