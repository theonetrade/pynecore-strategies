"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, display, fill, input, location, math, na, plot,
    plotshape, script, shape, size, strategy, syminfo, ta
)
from pynecore.types import Color, Persistent, PersistentSeries, Series

G1: str = "KAMA Settings"
G2: str = "Trend Confirmation"
G3: str = "Trade Management"
G4: str = "Risk Management"


@script.strategy("Aurora KAMA Trend", shorttitle="Aurora-KAMA", overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=25, commission_type=strategy.commission.percent, commission_value=0.05, slippage=1, pyramiding=1, calc_on_order_fills=False, max_labels_count=500)
def main(
    src: Series[float] = input.source(close, "Source", group=G1),
    kamaLen=input.int(10, "Efficiency Ratio Length", minval=2, group=G1),
    fastLen=input.int(2, "Fast EMA Length", minval=1, group=G1),
    slowLen=input.int(30, "Slow EMA Length", minval=1, group=G1),
    risingLen=input.int(3, "KAMA Rising Persistence (bars)", minval=1, group=G2),
    fallingLen=input.int(3, "KAMA Falling Persistence (bars)", minval=1, group=G2),
    useSmaFilter=input.bool(True, "Use Long-Term Trend Filter", group=G2),
    smaLen=input.int(200, "Trend Filter SMA Length", group=G2),
    direction=input.string("Long and Short", "Trade Direction", options=("Long", "Short", "Long and Short"), group=G3),
    barsBetween=input.int(5, "Minimum Bars Between Entries", minval=0, group=G3),
    useStop=input.bool(True, "Use Fixed Stop Loss %", group=G4),
    stopPct=input.float(4.0, "Stop Loss %", minval=0.1, group=G4),
    useTrail=input.bool(True, "Use Delayed Trailing Stop", group=G4),
    trailPct=input.float(6.0, "Trailing Stop %", minval=0.1, group=G4),
    trailDelay=input.int(5, "Delay Trailing by N Bars", minval=0, group=G4)
):
    def kama(source: Series[float], len: int, fLen: int, sLen: int):
        change: float = math.abs(source - source[len])
        volatility: float = math.sum(math.abs(source - source[1]), len)
        er: float = change / volatility if volatility != 0 else 0.0
        fastSC: float = 2.0 / (fLen + 1)
        slowSC: float = 2.0 / (sLen + 1)
        sc: float = math.pow(er * (fastSC - slowSC) + slowSC, 2)
        result: PersistentSeries[float] = na(float)
        result = source if na(result[1]) else result[1] + sc * (source - result[1])
        return result

    kamaVal: float = kama(src, kamaLen, fastLen, slowLen)
    trendSma: float = ta.sma(close, smaLen)

    kamaRising: bool = ta.rising(kamaVal, risingLen)
    kamaFalling: bool = ta.falling(kamaVal, fallingLen)

    longTrendOk: bool = not useSmaFilter or close > trendSma
    shortTrendOk: bool = not useSmaFilter or close < trendSma

    allowLong: bool = direction == 'Long' or direction == 'Long and Short'
    allowShort: bool = direction == 'Short' or direction == 'Long and Short'

    lastTradeBar: Persistent[int] = na(int)
    cooldownOk: bool = na(lastTradeBar) or bar_index - lastTradeBar >= barsBetween

    longSignal: bool = kamaRising and longTrendOk and allowLong and cooldownOk
    shortSignal: bool = kamaFalling and shortTrendOk and allowShort and cooldownOk

    longEntry: bool = False
    shortEntry: bool = False

    if longSignal and strategy.position_size <= 0:
        strategy.close('Short')
        strategy.entry('Long', strategy.long)
        lastTradeBar = bar_index
        longEntry = True

    if shortSignal and strategy.position_size >= 0:
        strategy.close('Long')
        strategy.entry('Short', strategy.short)
        lastTradeBar = bar_index
        shortEntry = True

    inPosition: bool = strategy.opentrades > 0
    barsInPosition: int = bar_index - strategy.opentrades.entry_bar_index(0) if inPosition else 0
    trailArmed: bool = inPosition and barsInPosition >= trailDelay

    stopDist: float = strategy.position_avg_price * stopPct / 100
    trailDist: float = strategy.position_avg_price * trailPct / 100

    if strategy.position_size > 0:
        strategy.exit('Exit Long', from_entry='Long', stop=strategy.position_avg_price - stopDist if useStop else na, trail_points=trailDist / syminfo.mintick if useTrail and trailArmed else na, trail_offset=trailDist / syminfo.mintick if useTrail and trailArmed else na)

    if strategy.position_size < 0:
        strategy.exit('Exit Short', from_entry='Short', stop=strategy.position_avg_price + stopDist if useStop else na, trail_points=trailDist / syminfo.mintick if useTrail and trailArmed else na, trail_offset=trailDist / syminfo.mintick if useTrail and trailArmed else na)

    posJustClosed: bool = strategy.position_size[1] != 0 and strategy.position_size == 0
    wasShort: bool = strategy.position_size[1] < 0
    wasLong: bool = strategy.position_size[1] > 0

    closedFromShort: bool = posJustClosed and wasShort
    closedFromLong: bool = posJustClosed and wasLong

    kamaColor: Color = color.new('#00E676') if kamaRising else color.new('#FF5252') if kamaFalling else color.gray

    plotKama = plot(kamaVal, 'KAMA', color=kamaColor, linewidth=2)
    plotClose = plot(close, 'Close', display=display.none)

    fill(plotKama, plotClose, math.max(kamaVal, close), kamaVal, color.new(color.new('#00E676'), 80), color.new(color.new('#00E676'), 60), title='Bullish Glow')
    fill(plotKama, plotClose, kamaVal, math.min(kamaVal, close), color.new(color.new('#FF5252'), 60), color.new(color.new('#FF5252'), 80), title='Bearish Glow')

    smaSlope: float = ta.change(trendSma, 5)
    smaCoreColor: Color = (color.new('#FFD600') if smaSlope > 0 else color.new('#FF9100') if smaSlope < 0 else color.new('#FFE082')) if useSmaFilter else na

    plot(trendSma if useSmaFilter else na, 'SMA Glow Outer', color=color.new(smaCoreColor, 88), linewidth=6)
    plot(trendSma if useSmaFilter else na, 'SMA Glow Mid', color=color.new(smaCoreColor, 72), linewidth=4)
    plot(trendSma if useSmaFilter else na, 'SMA Glow Inner', color=color.new(smaCoreColor, 45), linewidth=2)
    plot(trendSma if useSmaFilter else na, 'SMA Core', color=smaCoreColor, linewidth=1)

    plotshape(longEntry, 'Buy', style=shape.triangleup, location=location.belowbar, color=color.new('#00E676'), size=size.tiny)
    plotshape(shortEntry, 'Sell', style=shape.triangledown, location=location.abovebar, color=color.new('#FF5252'), size=size.tiny)
    plotshape(closedFromLong, 'Exit Long', style=shape.xcross, location=location.abovebar, color=color.new(color.gray, 20), size=size.tiny)
    plotshape(closedFromShort, 'Exit Short', style=shape.xcross, location=location.belowbar, color=color.new(color.gray, 20), size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)