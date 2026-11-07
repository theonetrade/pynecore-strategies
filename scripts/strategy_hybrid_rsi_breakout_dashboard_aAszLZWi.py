"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, high, input, label, na, plot, script, size,
    strategy, ta, time, timestamp, xloc, yloc
)
from pynecore.types import Label, Persistent


@script.strategy("Hybrid: RSI + Breakout + Dashboard", overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100)
def main(
    adxLen=input.int(14, "ADX Length"),
    adxSmooth=input.int(14, "ADX Smoothing"),
    adxThreshold=input.float(20, "ADX Threshold"),
    emaLen=input.int(200, "EMA Trend Filter"),
    rsiLen=input.int(14, "RSI Length"),
    rsiBuy=input.int(40, "RSI Buy Threshold"),
    rsiSell=input.int(60, "RSI Sell Threshold"),
    exitRSI=input.int(50, "RSI Exit Threshold"),
    breakoutLen=input.int(20, "Breakout Lookback"),
    atrLen=input.int(14, "ATR Length"),
    atrMult=input.float(2.0, "ATR Trailing Multiplier")
):
    startDate = timestamp(2017, 1, 1, 0, 0)
    isLive = time >= startDate
    plusDI, minusDI, adx = ta.dmi(adxLen, adxSmooth)
    isTrending = adx > adxThreshold
    isRanging = not isTrending
    regimeLabel = 'TRENDING' if isTrending else 'RANGING'
    ema = ta.ema(close, emaLen)
    bullish = close > ema
    bearish = close < ema
    biasLabel = 'Bullish' if bullish else 'Bearish'
    rsi = ta.rsi(close, rsiLen)

    rsiLong = isLive and isRanging and (rsi < rsiBuy) and bullish
    rsiShort = isLive and isRanging and (rsi > rsiSell) and bearish
    rsiLongExit = rsi > exitRSI
    rsiShortExit = rsi < exitRSI
    atr = ta.atr(atrLen)

    highestBreak = ta.highest(close[1], breakoutLen)
    lowestBreak = ta.lowest(close[1], breakoutLen)

    longBreak = isLive and isTrending and bullish and (close > highestBreak)
    shortBreak = isLive and isTrending and bearish and (close < lowestBreak)

    lastTradeType: Persistent[str] = "None"
    lastDirection: Persistent[str] = "None"
    if rsiLong:
        lastTradeType = "RSI"
        lastDirection = "Long"
    if rsiShort:
        lastTradeType = "RSI"
        lastDirection = "Short"
    if longBreak:
        lastTradeType = "Breakout"
        lastDirection = "Long"
    if shortBreak:
        lastTradeType = "Breakout"
        lastDirection = "Short"

    if rsiLong:
        strategy.entry('RSI Long', strategy.long)
    if rsiShort:
        strategy.entry('RSI Short', strategy.short)
    if longBreak:
        strategy.entry('Breakout Long', strategy.long)
    if shortBreak:
        strategy.entry('Breakout Short', strategy.short)

    if rsiLongExit:
        strategy.close('RSI Long')
    if rsiShortExit:
        strategy.close('RSI Short')
    strategy.exit('BO Long Exit', from_entry='Breakout Long', trail_points=atr * atrMult, trail_offset=atr * atrMult)
    strategy.exit('BO Short Exit', from_entry='Breakout Short', trail_points=atr * atrMult, trail_offset=atr * atrMult)

    plot(ema, '200 EMA', color=color.orange)

    dash: Persistent[Label] = na(Label)
    if bar_index % 5 == 0:
        label.delete(dash)
        dash = label.new(bar_index, high, 'Regime: ' + regimeLabel + ' | Bias: ' + biasLabel + ' | Last: ' + lastTradeType + ' ' + lastDirection, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_left, size=size.small, textcolor=color.white, color=color.black)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)