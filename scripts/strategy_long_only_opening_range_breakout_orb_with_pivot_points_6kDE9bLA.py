"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import (
    barmerge, close, color, high, input, low, math, na, nz, open, plot,
    request, script, strategy, syminfo, time, time_close, timeframe, timestamp
)
from pynecore.types import Color, Persistent, PersistentSeries, Series

SL_TYPE_PCT: str = "Percentage"
SL_TYPE_PREV: str = "Previous Low"
BULL_COLOR: Color = color.new('#26A69A')
NEUTRAL_COLOR: Color = color.new('#787B86')
STOP_COLOR: Color = color.new('#FF0000')
sessionGroupInput: str = "Session Settings"
riskGroupInput: str = "Risk Settings"
tradeGroupInput: str = "Trade Limits"
backtestGroupInput: str = "Backtest Window"
displayGroupInput: str = "Display"


@script.strategy(title="Volume Vigilante | Long-Only Opening Range Breakout (ORB) with Pivot Points", shorttitle="", overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=10000, pyramiding=0, process_orders_on_close=True)
def main(
    openingSessionInput=input.session(defval="0930-0945", title="Opening Session", group=sessionGroupInput, tooltip="Opening range window used to calculate the ORB high. Default: 09:30–09:45 (exchange time)."),
    maxTradesPerDayInput=input.int(defval=1, title="Max Trades per Day", minval=0, group=tradeGroupInput, tooltip="Maximum number of entries allowed per day."),
    initialSlTypeInput=input.string(defval=SL_TYPE_PCT, title="Initial SL Type", options=(SL_TYPE_PCT, SL_TYPE_PREV), group=riskGroupInput, tooltip="Percentage: stop from entry price. Previous Low: stop uses the prior bar's low from the setup."),
    stopLossPctInput=input.float(defval=3.0, title="Stop Loss %", minval=0.0, step=0.1, group=riskGroupInput, tooltip="Stop loss percent used when Initial SL Type = Percentage."),
    startTimeInput=input.time(defval=timestamp('01 Sep 2000 13:30 +0000'), title="Backtesting Start Time", group=backtestGroupInput, tooltip="Trades will only be taken after this timestamp."),
    endTimeInput=input.time(defval=timestamp('30 Sep 2099 19:30 +0000'), title="Backtesting End Time", group=backtestGroupInput, tooltip="Trades will only be taken before this timestamp."),
    showPivotsInput=input.bool(defval=True, title="Show Pivot Levels", group=displayGroupInput, tooltip="Plots daily pivot resistance levels (R1–R5) and mid-levels."),
    showOrbInput=input.bool(defval=True, title="Show ORB High", group=displayGroupInput, tooltip="Plots the opening range high after the opening session ends."),
    showStopInput=input.bool(defval=True, title="Show Stop Line", group=displayGroupInput, tooltip="Plots the active stop level while in position.")
):
    def isNewBar(res: str):
        t: Series[int] = time(res)
        return not na(t) and (na(t[1]) or t > t[1])

    newDay: bool = isNewBar('D')
    isExchangeDayEnd: bool = time_close == time_close('D')
    timeOk: bool = time > startTimeInput and time < endTimeInput

    orbSessionString: str = openingSessionInput + ':1234567'
    inOrbSession: Series[bool] = not na(time(timeframe.period, orbSessionString))
    orbSessionStart: bool = inOrbSession and (not inOrbSession[1])
    orbSessionJustEnded: bool = not inOrbSession and inOrbSession[1]

    inPosition: Series[bool] = strategy.position_size > 0
    justEntered: bool = inPosition and (not inPosition[1])

    orbHigh: Persistent[float] = na(float)
    orbBuiltToday: Persistent[bool] = False

    if newDay:
        orbHigh = na
        orbBuiltToday = False

    if orbSessionStart:
        orbHigh = high
    elif inOrbSession:
        orbHigh = high if na(orbHigh) else math.max(orbHigh, high)

    if orbSessionJustEnded and (not na(orbHigh)):
        orbBuiltToday = True

    orbReadyToday: bool = orbBuiltToday and (not na(orbHigh))

    prevCloseD: float = request.security(syminfo.tickerid, 'D', close[1], lookahead=barmerge.lookahead_on)
    prevHighD: float = request.security(syminfo.tickerid, 'D', high[1], lookahead=barmerge.lookahead_on)
    prevLowD: float = request.security(syminfo.tickerid, 'D', low[1], lookahead=barmerge.lookahead_on)

    pivot: float = (prevHighD + prevLowD + prevCloseD) / 3.0
    range1: float = prevHighD - prevLowD

    r1: float = pivot + pivot - prevLowD
    r2: float = pivot + range1
    r3: float = pivot * 2.0 + prevHighD - 2.0 * prevLowD
    r4: float = pivot * 3.0 + prevHighD - 3.0 * prevLowD
    r5: float = pivot * 4.0 + prevHighD - 4.0 * prevLowD

    r0_5: float = orbHigh + math.abs(r1 - orbHigh) / 2.0
    r1_5: float = r1 + math.abs(r1 - r2) / 2.0
    r2_5: float = r2 + math.abs(r2 - r3) / 2.0
    r3_5: float = r3 + math.abs(r3 - r4) / 2.0
    r4_5: float = r4 + math.abs(r4 - r5) / 2.0

    longSignal: bool = orbReadyToday and open < orbHigh and (high > orbHigh) and (r1 > orbHigh)

    tradesCounter: PersistentSeries[int] = 0
    tradesCounter = 0 if inOrbSession else tradesCounter[1] + 1 if longSignal and (not inPosition) else tradesCounter[1]

    canEnter: bool = not inPosition and tradesCounter[1] < maxTradesPerDayInput

    prevLowAtSetup: Persistent[float] = na(float)
    if longSignal and canEnter:
        prevLowAtSetup = low[1]

    entryPrice: Persistent[float] = na(float)
    if justEntered:
        entryPrice = strategy.position_avg_price
    elif not inPosition:
        entryPrice = na

    slPct: float = stopLossPctInput / 100.0 if stopLossPctInput > 0 else 99999.0

    initialStopRaw: float = entryPrice * (1.0 - slPct) if initialSlTypeInput == SL_TYPE_PCT else prevLowAtSetup if initialSlTypeInput == SL_TYPE_PREV else na

    initialStop: float = math.min(initialStopRaw, entryPrice) if inPosition and (not na(entryPrice)) and (not na(initialStopRaw)) else na

    trailLong: PersistentSeries[float] = 0.0

    if justEntered:
        trailLong = 0.0
    elif not inPosition:
        trailLong = 0.0
    else:
        prevTrail: float = nz(trailLong[1], 0.0)
        trailLong = r4 if high > r5 and r4 > prevTrail else r3_5 if high > r4_5 and r3_5 > prevTrail else r3 if high > r4 and r3 > prevTrail else r2_5 if high > r3_5 and r2_5 > prevTrail else r2 if high > r3 and r2 > prevTrail else r1_5 if high > r2_5 and r1_5 > prevTrail else r1 if high > r2 and r1 > prevTrail else r0_5 if high > r1_5 and r0_5 > prevTrail else orbHigh if high > r0_5 and orbHigh > prevTrail else prevTrail

    slLong: float = math.max(initialStop, trailLong) if inPosition else na

    if isExchangeDayEnd:
        strategy.close_all(comment='DayEnd', alert_message='EndofDay SELL ALERT')
        strategy.cancel('long')
        orbHigh = na
        orbBuiltToday = False
        trailLong = 0.0
        tradesCounter = 0
        prevLowAtSetup = na
        entryPrice = na

    if orbReadyToday and canEnter and timeOk and (open < orbHigh):
        strategy.entry('long', strategy.long, stop=orbHigh, alert_message='BUY ALERT')

    if inline_series(longSignal and canEnter, 1):
        strategy.cancel('long')

    strategy.exit('SL/TP', from_entry='long', stop=slLong if inPosition else na, alert_message='SELL ALERT')

    r1Plot: float = r1 if showPivotsInput and (not newDay) else na
    r2Plot: float = r2 if showPivotsInput and (not newDay) else na
    r3Plot: float = r3 if showPivotsInput and (not newDay) else na
    r4Plot: float = r4 if showPivotsInput and (not newDay) else na
    r5Plot: float = r5 if showPivotsInput and (not newDay) else na

    r05Plot: float = r0_5 if showPivotsInput and (not newDay) else na
    r15Plot: float = r1_5 if showPivotsInput and (not newDay) else na
    r25Plot: float = r2_5 if showPivotsInput and (not newDay) else na
    r35Plot: float = r3_5 if showPivotsInput and (not newDay) else na
    r45Plot: float = r4_5 if showPivotsInput and (not newDay) else na

    orbPlot: float = orbHigh if showOrbInput and orbReadyToday else na
    stopPlot: float = slLong if showStopInput and inPosition else na

    plot(r1Plot, style=plot.style_linebr, title='R1')
    plot(r2Plot, style=plot.style_linebr, title='R2')
    plot(r3Plot, style=plot.style_linebr, title='R3')
    plot(r4Plot, style=plot.style_linebr, title='R4')
    plot(r5Plot, style=plot.style_linebr, title='R5')

    plot(r05Plot, style=plot.style_linebr, color=color.new(NEUTRAL_COLOR, 0), title='R0.5')
    plot(r15Plot, style=plot.style_linebr, color=color.new(NEUTRAL_COLOR, 0), title='R1.5')
    plot(r25Plot, style=plot.style_linebr, color=color.new(NEUTRAL_COLOR, 0), title='R2.5')
    plot(r35Plot, style=plot.style_linebr, color=color.new(NEUTRAL_COLOR, 0), title='R3.5')
    plot(r45Plot, style=plot.style_linebr, color=color.new(NEUTRAL_COLOR, 0), title='R4.5')

    plot(orbPlot, title='ORB High', style=plot.style_linebr, color=color.new(BULL_COLOR, 0), linewidth=2)
    plot(stopPlot, title='Stop', style=plot.style_linebr, color=color.new(STOP_COLOR, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
