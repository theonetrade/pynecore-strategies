"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, high, hour, input, low, math, minute, na, script, strategy,
    syminfo, time
)
from pynecore.types import Persistent


@script.strategy("LANZ Strategy 2.0 [Backtest]", overlay=True, default_qty_type=strategy.cash, default_qty_value=100)
def main(
    accountSizeUSD=input.int(100000000, title="Account Size (USD)", minval=1),
    riskPercent=input.float(1.0, title="Risk (%)", minval=0.1, maxval=100),
    slProtectionMode=input.string(title="SL Protection Mode", defval="Full Coverage", options=("First Swing", "Second Swing", "Full Coverage")),
    fullCoveragePips=input.int(12, title="Full Coverage Pips", minval=1),
    minBosBreakPips=input.float(0.5, title="Minimum Break of Structure (Pips)", minval=0.1, step=0.1),
    rrMultiplier=input.float(5.5, title="TP Risk Reward (RR)", minval=0.5, step=0.1)
):
    pipSize = syminfo.mintick * 10
    minBosBreakDist = minBosBreakPips * pipSize

    prevHigh: Persistent[float] = na(float)
    prevLow: Persistent[float] = na(float)
    lastSwingHigh: Persistent[float] = na(float)
    lastSwingLow: Persistent[float] = na(float)
    olderSwingHigh: Persistent[float] = na(float)
    olderSwingLow: Persistent[float] = na(float)
    trendDir: Persistent[int] = na(int)

    hh = high[2] > high[3] and high[3] > high[4]
    ll = low[2] < low[3] and low[3] < low[4]

    if hh:
        olderSwingHigh = prevHigh
        prevHigh = lastSwingHigh
        lastSwingHigh = high[2]
    if ll:
        olderSwingLow = prevLow
        prevLow = lastSwingLow
        lastSwingLow = low[2]

    if not na(prevHigh) and (not na(lastSwingHigh)) and (not na(prevLow)) and (not na(lastSwingLow)):
        isBullish = lastSwingHigh > prevHigh and lastSwingLow > prevLow
        isBearish = lastSwingHigh < prevHigh and lastSwingLow < prevLow
        trendDir = 1 if isBullish else -1 if isBearish else trendDir

    bosLevel: Persistent[float] = na(float)
    bosDir: Persistent[int] = na(int)

    newBosUp = not na(lastSwingHigh) and close > lastSwingHigh + minBosBreakDist
    newBosDown = not na(lastSwingLow) and close < lastSwingLow - minBosBreakDist

    if newBosUp:
        bosLevel = lastSwingHigh
        bosDir = 1
    elif newBosDown:
        bosLevel = lastSwingLow
        bosDir = -1

    lastBosDir: Persistent[int] = na(int)
    lastTrendDir: Persistent[int] = na(int)

    if not na(bosDir):
        lastBosDir = bosDir
    if not na(trendDir):
        lastTrendDir = trendDir

    isAnalysisBar = hour(time, 'America/New_York') == 2 and minute(time, 'America/New_York') == 0

    enterLong = isAnalysisBar and lastBosDir == 1 and (lastTrendDir == 1)
    enterShort = isAnalysisBar and lastBosDir == -1 and (lastTrendDir == -1)
    enterFallbackLong = isAnalysisBar and lastBosDir == 1 and (lastTrendDir != 1)
    enterFallbackShort = isAnalysisBar and lastBosDir == -1 and (lastTrendDir != -1)

    entryPrice = close
    fallbackSL_Long = entryPrice - 5 * pipSize
    fallbackSL_Short = entryPrice + 5 * pipSize

    __block_result__ = na
    __switch__ = slProtectionMode
    if __switch__ == "First Swing":
        __block_result__ = fallbackSL_Long if na(lastSwingLow) else lastSwingLow
    elif __switch__ == "Second Swing":
        __block_result__ = fallbackSL_Long if na(prevLow) else prevLow
    elif __switch__ == "Full Coverage":
        __block_result__ = fallbackSL_Long if na(olderSwingLow) or na(prevLow) or na(lastSwingLow) else math.min(olderSwingLow, prevLow, lastSwingLow) - fullCoveragePips * pipSize
    slBase_Long = __block_result__

    __block_result_1__ = na
    __switch__ = slProtectionMode
    if __switch__ == "First Swing":
        __block_result_1__ = fallbackSL_Short if na(lastSwingHigh) else lastSwingHigh
    elif __switch__ == "Second Swing":
        __block_result_1__ = fallbackSL_Short if na(prevHigh) else prevHigh
    elif __switch__ == "Full Coverage":
        __block_result_1__ = fallbackSL_Short if na(olderSwingHigh) or na(prevHigh) or na(lastSwingHigh) else math.max(olderSwingHigh, prevHigh, lastSwingHigh) + fullCoveragePips * pipSize
    slBase_Short = __block_result_1__

    slPrice_Long = entryPrice - 10 * pipSize if entryPrice - slBase_Long < 10 * pipSize else slBase_Long
    slPrice_Short = entryPrice + 10 * pipSize if slBase_Short - entryPrice < 10 * pipSize else slBase_Short

    tpPrice_Long = entryPrice + rrMultiplier * (entryPrice - slPrice_Long)
    tpPrice_Short = entryPrice - rrMultiplier * (slPrice_Short - entryPrice)

    slPips_Long = math.abs(entryPrice - slPrice_Long) / pipSize
    slPips_Short = math.abs(entryPrice - slPrice_Short) / pipSize

    riskUSD = accountSizeUSD * (riskPercent / 100)
    lotSize_Long = riskUSD / (slPips_Long * 10)
    lotSize_Short = riskUSD / (slPips_Short * 10)

    alreadyInTrade = strategy.opentrades > 0
    enterLong = enterLong and (not alreadyInTrade)
    enterShort = enterShort and (not alreadyInTrade)
    enterFallbackLong = enterFallbackLong and (not alreadyInTrade)
    enterFallbackShort = enterFallbackShort and (not alreadyInTrade)

    if enterLong:
        strategy.entry('BUY', strategy.long, qty=lotSize_Long, limit=entryPrice)
        strategy.exit('TP/SL BUY', from_entry='BUY', stop=slPrice_Long, limit=tpPrice_Long)

    if enterShort:
        strategy.entry('SELL', strategy.short, qty=lotSize_Short, limit=entryPrice)
        strategy.exit('TP/SL SELL', from_entry='SELL', stop=slPrice_Short, limit=tpPrice_Short)

    if enterFallbackLong:
        strategy.entry('BUY_FB', strategy.long, qty=lotSize_Long, limit=entryPrice)
        strategy.exit('TP/SL BUY_FB', from_entry='BUY_FB', stop=slPrice_Long, limit=tpPrice_Long)

    if enterFallbackShort:
        strategy.entry('SELL_FB', strategy.short, qty=lotSize_Short, limit=entryPrice)
        strategy.exit('TP/SL SELL_FB', from_entry='SELL_FB', stop=slPrice_Short, limit=tpPrice_Short)

    manualClose = hour(time, 'America/New_York') == 11 and minute(time, 'America/New_York') == 45
    if strategy.opentrades > 0 and manualClose:
        strategy.close_all(comment='Manual Close 11:45 NY')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
