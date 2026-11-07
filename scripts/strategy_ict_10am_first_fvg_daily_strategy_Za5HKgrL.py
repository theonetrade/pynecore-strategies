"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barstate, box, color, dayofmonth, dayofweek, extend, high,
    hour, input, line, low, math, minute, month, na, open, position, script, size, strategy,
    syminfo, table, time, year
)
from pynecore.types import (
    Box, Color, IBPersistent, Line, Persistent, PersistentSeries, Series,
    Table
)

GROUP_SESSION: str = "Session"
GROUP_ORDER: str = "Order"
GROUP_FVG: str = "FVG Filter"
GROUP_TARGET: str = "Take Profit"
GROUP_VISUAL: str = "Visual"


@script.strategy("ICT 10AM First FVG Daily Strategy", overlay=True, pyramiding=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, commission_type=strategy.commission.cash_per_contract, commission_value=0, calc_on_order_fills=True, process_orders_on_close=False, margin_long=1, margin_short=1, max_boxes_count=100, max_lines_count=500, max_labels_count=500)
def main(
    timezoneInput=input.string("America/New_York", "Timezone", group=GROUP_SESSION),
    startHour=input.int(10, "Setup start hour", minval=0, maxval=23, group=GROUP_SESSION),
    endHour=input.int(16, "Cancel/close hour", minval=1, maxval=23, group=GROUP_SESSION),
    closeAtEnd=input.bool(True, "Close open position at session end", group=GROUP_SESSION),
    enableWeekendProtection=input.bool(True, "Friday/weekend lock", group=GROUP_SESSION),
    fridayCloseHour=input.int(15, "Friday close hour", minval=0, maxval=23, group=GROUP_SESSION),
    fridayCloseMinute=input.int(45, "Friday close minute", minval=0, maxval=59, group=GROUP_SESSION),
    orderQty=input.float(1.0, "Contracts", minval=0.001, step=1.0, group=GROUP_ORDER),
    enableLong=input.bool(True, "Enable long", group=GROUP_ORDER),
    enableShort=input.bool(True, "Enable short", group=GROUP_ORDER),
    minFvgSize=input.float(0.0, "Min FVG Size", minval=0.0, group=GROUP_FVG, tooltip="Minimum gap between the first and third candles. Zero disables this filter. Smaller FVGs are skipped until the first qualifying FVG forms."),
    fvgSizeUnit=input.string("Points", "FVG size unit", options=("Points", "Ticks"), group=GROUP_FVG, tooltip="Points are price units. Ticks are the symbol's minimum price increments; for a 0.25 tick size, 4 ticks = 1 point."),
    targetMode=input.string("Session extreme", "Exit Type", options=("Session extreme", "Fixed RR"), group=GROUP_TARGET, tooltip="Session extreme preserves the original target. Fixed RR uses the entry-to-stop distance multiplied by Risk to Reward."),
    riskReward=input.float(2.0, "Risk to Reward", minval=0.1, step=0.1, group=GROUP_TARGET, tooltip="Used only with Fixed RR. 2 means risk 1 to target 2. The stop stays at the generator candle extreme; the target is rounded to the nearest tick, at least one tick from entry."),
    showFvg=input.bool(True, "Show first FVG", group=GROUP_VISUAL),
    showLevels=input.bool(True, "Show open / entry / stop / target", group=GROUP_VISUAL)
):
    nyHour: int = hour(time, timezoneInput)
    nyMinute: int = minute(time, timezoneInput)
    nyDay: Series[int] = dayofmonth(time, timezoneInput)
    nyMonth: Series[int] = month(time, timezoneInput)
    nyYear: Series[int] = year(time, timezoneInput)
    nyDayOfWeek: int = dayofweek(time, timezoneInput)
    nyMinutes: int = nyHour * 60 + nyMinute

    def f_tick(price: float):
        return math.round(price / syminfo.mintick) * syminfo.mintick

    def f_target(entry: float, stop: float, direction: int, sessionExtreme: float):
        rewardDistance: float = math.max(syminfo.mintick, f_tick(math.abs(entry - stop) * riskReward))
        return f_tick(entry + direction * rewardDistance) if targetMode == 'Fixed RR' else f_tick(sessionExtreme)

    minFvgSizePrice: float = minFvgSize * syminfo.mintick if fvgSizeUnit == 'Ticks' else minFvgSize

    newCalendarDay: bool = bar_index > 0 and (nyDay != nyDay[1] or nyMonth != nyMonth[1] or nyYear != nyYear[1])
    atStart: bool = nyHour == startHour and nyMinute == 0
    inSetupWindow: bool = nyHour >= startHour and nyHour < endHour
    atOrAfterEnd: bool = nyHour >= endHour
    weekendDay: bool = nyDayOfWeek == dayofweek.saturday or nyDayOfWeek == dayofweek.sunday
    fridayCutoff: bool = nyDayOfWeek == dayofweek.friday and nyMinutes >= fridayCloseHour * 60 + fridayCloseMinute
    marketTransitionLock: bool = enableWeekendProtection and (weekendDay or fridayCutoff)
    canCreateSetup: bool = inSetupWindow and (not marketTransitionLock)
    fvgGeneratorInsideWindow: bool = hour(time[1], timezoneInput) >= startHour and hour(time[1], timezoneInput) < endHour

    sessionOpen: Persistent[float] = na(float)
    sessionHigh: PersistentSeries[float] = na(float)
    sessionLow: PersistentSeries[float] = na(float)
    fvgFound: Persistent[bool] = False

    orderPending: IBPersistent[bool] = False
    tradedToday: IBPersistent[bool] = False
    tradeFinished: IBPersistent[bool] = False
    entryConfirmed: IBPersistent[bool] = False
    marginErrorDetected: IBPersistent[bool] = False
    unfilledTouchBar: IBPersistent[int] = na(int)
    handledClosedTrades: IBPersistent[int] = 0
    setupDirection: Persistent[int] = 0
    fvgCreatedBar: Persistent[int] = na(int)
    fvgLow: Persistent[float] = na(float)
    fvgHigh: Persistent[float] = na(float)
    entryPrice: Persistent[float] = na(float)
    stopPrice: Persistent[float] = na(float)
    targetPrice: Persistent[float] = na(float)

    fvgBox: Persistent[Box] = na(Box)
    openLine: Persistent[Line] = na(Line)
    entryLine: Persistent[Line] = na(Line)
    stopLine: Persistent[Line] = na(Line)
    targetLine: Persistent[Line] = na(Line)
    marginWarningTable: Persistent[Table] = table.new(position.bottom_right, 1, 1)

    if newCalendarDay:
        strategy.cancel('Daily Long')
        strategy.cancel('Daily Short')
        sessionOpen = na
        sessionHigh = na
        sessionLow = na
        fvgFound = False
        orderPending = False
        tradedToday = False
        tradeFinished = False
        entryConfirmed = False
        unfilledTouchBar = na
        handledClosedTrades = strategy.closedtrades
        setupDirection = 0
        fvgCreatedBar = na
        fvgLow = na
        fvgHigh = na
        entryPrice = na
        stopPrice = na
        targetPrice = na
        fvgBox = na
        openLine = na
        entryLine = na
        stopLine = na
        targetLine = na

    if atStart:
        sessionOpen = open
        sessionHigh = high
        sessionLow = low
        if showLevels:
            openLine = line.new(bar_index, sessionOpen, bar_index + 1, sessionOpen, extend=extend.none, color=color.black, width=2)
    elif inSetupWindow and (not na(sessionOpen)):
        sessionHigh = math.max(sessionHigh, high)
        sessionLow = math.min(sessionLow, low)

    bearishFvg: bool = canCreateSetup and fvgGeneratorInsideWindow and (high < low[2]) and (low[2] - high + syminfo.mintick * 1e-06 >= minFvgSizePrice)
    bullishFvg: bool = canCreateSetup and fvgGeneratorInsideWindow and (low > high[2]) and (low - high[2] + syminfo.mintick * 1e-06 >= minFvgSizePrice)

    if not fvgFound and (not na(sessionOpen)) and barstate.isconfirmed:
        if bearishFvg:
            fvgFound = True
            setupDirection = -1
            fvgCreatedBar = bar_index
            fvgLow = high
            fvgHigh = low[2]
            entryPrice = f_tick(fvgLow)
            stopPrice = f_tick(high[1])
            targetPrice = f_target(entryPrice, stopPrice, setupDirection, sessionLow)
        elif bullishFvg:
            fvgFound = True
            setupDirection = 1
            fvgCreatedBar = bar_index
            fvgLow = high[2]
            fvgHigh = low
            entryPrice = f_tick(fvgHigh)
            stopPrice = f_tick(low[1])
            targetPrice = f_target(entryPrice, stopPrice, setupDirection, sessionHigh)

        if fvgFound:
            setupColor: Color = color.teal if setupDirection == 1 else color.orange
            if showFvg:
                fvgBox = box.new(bar_index - 2, fvgHigh, bar_index + 1, fvgLow, extend=extend.none, border_color=color.new(setupColor, 100), bgcolor=color.new(setupColor, 80))
            if showLevels:
                entryLine = line.new(bar_index, entryPrice, bar_index + 1, entryPrice, extend=extend.none, color=color.orange, style=line.style_dashed, width=2)
                stopLine = line.new(bar_index - 1, stopPrice, bar_index + 1, stopPrice, extend=extend.none, color=color.orange, style=line.style_dashed, width=2)
                targetLine = line.new(bar_index, targetPrice, bar_index + 1, targetPrice, extend=extend.none, color=color.new(color.teal, 25), style=line.style_dashed, width=2)

    if fvgFound and (not tradedToday) and (strategy.position_size == 0) and (bar_index >= fvgCreatedBar) and inSetupWindow and (not marketTransitionLock):
        candidateTarget: float = f_target(entryPrice, stopPrice, setupDirection, sessionLow if setupDirection == -1 else sessionHigh)
        validGeometry: bool = stopPrice > entryPrice and candidateTarget < entryPrice if setupDirection == -1 else stopPrice < entryPrice and candidateTarget > entryPrice
        if validGeometry:
            targetPrice = candidateTarget
            if showLevels and (not na(targetLine)):
                line.set_y1(targetLine, targetPrice)
                line.set_y2(targetLine, targetPrice)
            if not orderPending:
                if setupDirection == 1 and enableLong:
                    strategy.entry('Daily Long', strategy.long, qty=orderQty, limit=entryPrice)
                    orderPending = True
                elif setupDirection == -1 and enableShort:
                    strategy.entry('Daily Short', strategy.short, qty=orderQty, limit=entryPrice)
                    orderPending = True

    pendingLimitTouched: bool = orderPending and bar_index > fvgCreatedBar and (not na(entryPrice)) and (low <= entryPrice if setupDirection == 1 else high >= entryPrice)
    if pendingLimitTouched and strategy.position_size == 0 and (strategy.closedtrades == handledClosedTrades) and na(unfilledTouchBar):
        unfilledTouchBar = bar_index
    touchStillUnfilled: bool = not na(unfilledTouchBar) and bar_index > unfilledTouchBar and orderPending and (not tradedToday) and (strategy.position_size == 0)
    if touchStillUnfilled:
        marginErrorDetected = True

    justEnteredLong: bool = strategy.position_size > 0 and strategy.position_size[1] <= 0
    justEnteredShort: bool = strategy.position_size < 0 and strategy.position_size[1] >= 0

    if (justEnteredLong or justEnteredShort) and (not entryConfirmed):
        orderPending = False
        unfilledTouchBar = na
        tradedToday = True
        entryConfirmed = True
        entryPrice = f_tick(strategy.position_avg_price)
        targetPrice = f_target(entryPrice, stopPrice, setupDirection, sessionLow[1] if setupDirection == -1 else sessionHigh[1])
        if showLevels:
            if not na(entryLine):
                line.set_y1(entryLine, entryPrice)
                line.set_y2(entryLine, entryPrice)
                line.set_color(entryLine, color.black)
                line.set_style(entryLine, line.style_solid)
                line.set_width(entryLine, 2)
            if not na(stopLine):
                line.set_color(stopLine, color.red)
                line.set_style(stopLine, line.style_solid)
                line.set_width(stopLine, 2)
            if not na(targetLine):
                line.set_y1(targetLine, targetPrice)
                line.set_y2(targetLine, targetPrice)
                line.set_color(targetLine, color.teal)
                line.set_style(targetLine, line.style_solid)
                line.set_width(targetLine, 2)

    longBracketReady: bool = fvgFound and (not tradeFinished) and (setupDirection == 1) and enableLong and (not na(stopPrice)) and (not na(targetPrice))
    shortBracketReady: bool = fvgFound and (not tradeFinished) and (setupDirection == -1) and enableShort and (not na(stopPrice)) and (not na(targetPrice))
    if longBracketReady:
        strategy.exit('Daily Long Exit', 'Daily Long', stop=stopPrice, limit=targetPrice)
    if shortBracketReady:
        strategy.exit('Daily Short Exit', 'Daily Short', stop=stopPrice, limit=targetPrice)

    setupVisualActive: bool = fvgFound and (not tradeFinished) and (inSetupWindow or strategy.position_size != 0)
    if setupVisualActive:
        if showLevels:
            if not na(openLine):
                line.set_x2(openLine, bar_index + 1)
            if not na(entryLine):
                line.set_x2(entryLine, bar_index + 1)
            if not na(stopLine):
                line.set_x2(stopLine, bar_index + 1)
            if not na(targetLine):
                line.set_x2(targetLine, bar_index + 1)
        if showFvg and (not na(fvgBox)):
            box.set_right(fvgBox, bar_index + 1)

    cancelPendingNow: bool = (atOrAfterEnd or marketTransitionLock) and orderPending and (strategy.position_size == 0)
    if cancelPendingNow:
        strategy.cancel('Daily Long')
        strategy.cancel('Daily Short')
        orderPending = False

    forceCloseNow: bool = strategy.position_size != 0 and (marketTransitionLock or (closeAtEnd and atOrAfterEnd))
    if forceCloseNow:
        strategy.close_all(comment='Friday/Weekend Lock' if marketTransitionLock else 'Session End')

    tradeClosedThisBar: bool = strategy.closedtrades > handledClosedTrades
    if tradeClosedThisBar:
        handledClosedTrades = strategy.closedtrades
        orderPending = False
        unfilledTouchBar = na
        tradedToday = True
        tradeFinished = True
        lastTrade: int = strategy.closedtrades - 1

        if not entryConfirmed:
            entryConfirmed = True
            entryPrice = f_tick(strategy.closedtrades.entry_price(lastTrade))
            if showLevels:
                if not na(entryLine):
                    line.set_y1(entryLine, entryPrice)
                    line.set_y2(entryLine, entryPrice)
                    line.set_color(entryLine, color.black)
                    line.set_style(entryLine, line.style_solid)
                if not na(stopLine):
                    line.set_color(stopLine, color.red)
                    line.set_style(stopLine, line.style_solid)
                if not na(targetLine):
                    line.set_color(targetLine, color.teal)
                    line.set_style(targetLine, line.style_solid)
    if tradeClosedThisBar and showLevels:
        lastTrade: int = strategy.closedtrades - 1
        actualExitBar: int = strategy.closedtrades.exit_bar_index(lastTrade)

        if not na(openLine):
            line.set_extend(openLine, extend.none)
            line.set_x2(openLine, actualExitBar + 1)
        if not na(entryLine):
            line.set_extend(entryLine, extend.none)
            line.set_x2(entryLine, actualExitBar + 1)
        if not na(stopLine):
            line.set_extend(stopLine, extend.none)
            line.set_x2(stopLine, actualExitBar + 1)
        if not na(targetLine):
            line.set_extend(targetLine, extend.none)
            line.set_x2(targetLine, actualExitBar + 1)
        if not na(fvgBox):
            box.set_extend(fvgBox, extend.none)
            box.set_right(fvgBox, actualExitBar + 1)

    table.cell(marginWarningTable, 0, 0, 'Insufficient margin' if marginErrorDetected else '', text_color=color.white, text_size=size.tiny, bgcolor=color.new(color.red, 15) if marginErrorDetected else color.new(color.black, 100))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
