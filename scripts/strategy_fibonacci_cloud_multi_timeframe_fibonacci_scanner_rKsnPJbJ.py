"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bgcolor, close, color, fill, high, input, location, low, math, na, plot,
    plotshape, script, shape, size, strategy, ta
)


@script.strategy("Fib Confluence Scanner", overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.05)
def main(
    lenA=input.int(20, "Lookback A (short)", minval=2, group="Fibonacci Lookbacks"),
    lenB=input.int(50, "Lookback B (medium)", minval=2, group="Fibonacci Lookbacks"),
    lenC=input.int(100, "Lookback C (long)", minval=2, group="Fibonacci Lookbacks"),
    __input_3__=input.float(0.5, "Confluence Tolerance (%)", minval=0.01, step=0.01, group="Confluence Settings"),
    minConfluence=input.int(1, "Minimum Confluent Levels", minval=1, maxval=15, group="Confluence Settings"),
    useTrendFilter=input.bool(True, "Use EMA Trend Filter", group="Trend Filter"),
    trendLen=input.int(50, "Trend EMA Length", minval=1, group="Trend Filter"),
    useRsiFilter=input.bool(False, "Use RSI Momentum Filter", group="RSI Filter"),
    rsiLen=input.int(14, "RSI Length", minval=1, group="RSI Filter"),
    rsiLongMin=input.int(45, "RSI Min for Longs", minval=0, maxval=100, group="RSI Filter"),
    rsiShortMax=input.int(55, "RSI Max for Shorts", minval=0, maxval=100, group="RSI Filter"),
    tradeDirection=input.string("Both", "Trade Direction", options=("Both", "Long Only", "Short Only"), group="Trade Management"),
    __input_12__=input.float(1.5, "Stop Loss (%)", minval=0.1, step=0.1, group="Trade Management"),
    tpRR=input.float(2.0, "Take Profit R:R", minval=0.1, step=0.1, group="Trade Management"),
    oneTradeAtTime=input.bool(True, "Only One Position At A Time", group="Trade Management"),
    showBg=input.bool(True, "Confluence background", group="Display"),
    showMarks=input.bool(True, "Entry markers", group="Display"),
    msg_open_long=input.string("Open Long", "Alert: Open Long", group="Alerts"),
    msg_open_short=input.string("Open Short", "Alert: Open Short", group="Alerts"),
    msg_close_long=input.string("Close Long", "Alert: Close Long", group="Alerts"),
    msg_close_short=input.string("Close Short", "Alert: Close Short", group="Alerts")
):
    tolerancePct = __input_3__ / 100
    slPct = __input_12__ / 100

    def fibLevels(len):
        hi = ta.highest(high, len)
        lo = ta.lowest(low, len)
        rng = hi - lo
        l236 = hi - 0.236 * rng
        l382 = hi - 0.382 * rng
        l500 = hi - 0.5 * rng
        l618 = hi - 0.618 * rng
        l786 = hi - 0.786 * rng
        return (l236, l382, l500, l618, l786)

    a236, a382, a500, a618, a786 = fibLevels(lenA)
    b236, b382, b500, b618, b786 = fibLevels(lenB)
    c236, c382, c500, c618, c786 = fibLevels(lenC)

    def isNear(level):
        return math.abs(close - level) / close <= tolerancePct

    confluenceCount = (1 if isNear(a236) else 0) + (1 if isNear(a382) else 0) + (1 if isNear(a500) else 0) + (1 if isNear(a618) else 0) + (1 if isNear(a786) else 0) + (1 if isNear(b236) else 0) + (1 if isNear(b382) else 0) + (1 if isNear(b500) else 0) + (1 if isNear(b618) else 0) + (1 if isNear(b786) else 0) + (1 if isNear(c236) else 0) + (1 if isNear(c382) else 0) + (1 if isNear(c500) else 0) + (1 if isNear(c618) else 0) + (1 if isNear(c786) else 0)

    confluence = confluenceCount >= minConfluence

    emaTrend = ta.ema(close, trendLen)
    trendUp = close > emaTrend
    trendDn = close < emaTrend

    rsiVal = ta.rsi(close, rsiLen)
    rsiLongOK = not useRsiFilter or rsiVal >= rsiLongMin
    rsiShortOK = not useRsiFilter or rsiVal <= rsiShortMax

    longAllowed = tradeDirection != 'Short Only'
    shortAllowed = tradeDirection != 'Long Only'
    positionFree = strategy.position_size == 0 if oneTradeAtTime else True

    longCondition = confluence and (not useTrendFilter or trendUp) and rsiLongOK and longAllowed and positionFree
    shortCondition = confluence and (not useTrendFilter or trendDn) and rsiShortOK and shortAllowed and positionFree

    colUp = color.new(color.new('#26A69A'), 0)
    colDown = color.new(color.new('#EF5350'), 0)
    colMid = color.new(color.gray, 40)

    trendCol = colUp if trendUp else colDown

    pMid = plot(emaTrend if useTrendFilter else na, 'Trend EMA', color=colMid, linewidth=1)
    pFast = plot(b500, 'Fib 0.5 (medium)', color=trendCol, linewidth=2)

    fill(pFast, pMid, color=color.new(colUp if trendUp else colDown, 88), title='Trend fill')

    bgcolor(color.new(colUp if confluenceCount >= minConfluence + 1 else colMid, 90) if showBg and confluence else na, title='Confluence background')

    plotshape(showMarks and longCondition, 'Long', shape.triangleup, location.belowbar, colUp, size=size.small)
    plotshape(showMarks and shortCondition, 'Short', shape.triangledown, location.abovebar, colDown, size=size.small)

    if longCondition:
        strategy.entry('Long', strategy.long, alert_message=msg_open_long)

    if shortCondition:
        strategy.entry('Short', strategy.short, alert_message=msg_open_short)

    longStop = strategy.position_avg_price * (1 - slPct)
    longTP = strategy.position_avg_price * (1 + slPct * tpRR)
    shortStop = strategy.position_avg_price * (1 + slPct)
    shortTP = strategy.position_avg_price * (1 - slPct * tpRR)

    if strategy.position_size > 0:
        strategy.exit('Exit Long', 'Long', stop=longStop, limit=longTP, alert_message=msg_close_long)

    if strategy.position_size < 0:
        strategy.exit('Exit Short', 'Short', stop=shortStop, limit=shortTP, alert_message=msg_close_short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
