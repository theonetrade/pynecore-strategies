"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, hline, input, location, math, na, plot, plotshape, script,
    shape, size, strategy, syminfo, ta, time, timestamp
)
from pynecore.types import Persistent, Series

grpM: str = 'MACD'
grpF: str = 'Filters'
grpR: str = 'Risk'
grpG: str = 'General'


@script.strategy('MACD Pullback Sniper | Trend + ADX Filtered Strategy', overlay=False, initial_capital=10000, commission_type=strategy.commission.percent, commission_value=0.05, slippage=2, pyramiding=0, margin_long=100, margin_short=100)
def main(
    fastLen=input.int(12, 'Fast EMA', minval=1, group=grpM),
    slowLen=input.int(26, 'Slow EMA', minval=1, group=grpM),
    signalLen=input.int(9, 'Signal EMA', minval=1, group=grpM),
    useTrend=input.bool(True, 'Trend filter (price vs EMA)', group=grpF),
    trendLen=input.int(200, 'Trend EMA length', minval=2, group=grpF),
    useZero=input.bool(True, 'Zero-line filter', group=grpF, tooltip='Longs only when the cross happens below zero, shorts only above zero.'),
    useAdx=input.bool(True, 'ADX filter', group=grpF),
    adxLen=input.int(14, 'ADX length', minval=1, group=grpF),
    adxMin=input.float(20.0, 'ADX minimum', minval=1, group=grpF),
    atrLen=input.int(14, 'ATR length', minval=1, group=grpR),
    slMult=input.float(2.0, 'Stop distance (x ATR)', minval=0.1, step=0.1, group=grpR),
    rrRatio=input.float(2.0, 'Reward : Risk', minval=0.5, step=0.1, group=grpR),
    riskPct=input.float(1.0, 'Risk per trade (% of equity)', minval=0.1, maxval=10, step=0.1, group=grpR),
    maxLev=input.float(1.0, 'Max position size (x equity)', minval=0.1, step=0.1, group=grpR, tooltip='Caps position value so a tight stop cannot create an oversized trade.'),
    exitCross=input.bool(True, 'Exit on opposite MACD cross', group=grpR),
    allowShort=input.bool(True, 'Allow shorts', group=grpG),
    startDate=input.time(timestamp('01 Jan 2018 00:00 +0000'), 'Start date', group=grpG),
    endDate=input.time(timestamp('31 Dec 2069 23:59 +0000'), 'End date', group=grpG)
):
    hist: Series
    macdLine, signalLine, hist = ta.macd(close, fastLen, slowLen, signalLen)
    trendEma = ta.ema(close, trendLen)
    _, _, adx = ta.dmi(adxLen, adxLen)
    atr = ta.atr(atrLen)

    inRange = time >= startDate and time <= endDate
    bullCross = ta.crossover(macdLine, signalLine)
    bearCross = ta.crossunder(macdLine, signalLine)

    trendLongOk = not useTrend or close > trendEma
    trendShortOk = not useTrend or close < trendEma
    zeroLongOk = not useZero or macdLine < 0
    zeroShortOk = not useZero or macdLine > 0
    adxOk = not useAdx or adx > adxMin

    longSignal = bullCross and trendLongOk and zeroLongOk and adxOk and inRange
    shortSignal = bearCross and trendShortOk and zeroShortOk and adxOk and inRange and allowShort

    def f_qty(stopDist: float):
        riskAmt: float = strategy.equity * riskPct / 100
        q: float = riskAmt / stopDist if stopDist > 0 else 0.0
        q = math.min(q, strategy.equity * maxLev / close)
        step: float = syminfo.mincontract if syminfo.mincontract > 0 else 1.0
        return math.floor(q / step) * step

    entryAtr: Persistent[float] = na(float)
    slLvl: Persistent[float] = na(float)
    tpLvl: Persistent[float] = na(float)

    if strategy.position_size > 0:
        slLvl = strategy.position_avg_price - entryAtr * slMult
        tpLvl = strategy.position_avg_price + entryAtr * slMult * rrRatio
        strategy.exit('Long Exit', 'Long', stop=slLvl, limit=tpLvl)
    elif strategy.position_size < 0:
        slLvl = strategy.position_avg_price + entryAtr * slMult
        tpLvl = strategy.position_avg_price - entryAtr * slMult * rrRatio
        strategy.exit('Short Exit', 'Short', stop=slLvl, limit=tpLvl)
    else:
        slLvl = na
        tpLvl = na

    if exitCross and bearCross and (strategy.position_size > 0) and (not shortSignal):
        strategy.close('Long', comment='MACD cross')
    if exitCross and bullCross and (strategy.position_size < 0) and (not longSignal):
        strategy.close('Short', comment='MACD cross')

    if longSignal and strategy.position_size <= 0:
        q: float = f_qty(atr * slMult)
        if q > 0:
            entryAtr = atr
            strategy.entry('Long', strategy.long, qty=q)
            strategy.exit('Long Exit', 'Long', stop=close - atr * slMult, limit=close + atr * slMult * rrRatio)

    if shortSignal and strategy.position_size >= 0:
        q: float = f_qty(atr * slMult)
        if q > 0:
            entryAtr = atr
            strategy.entry('Short', strategy.short, qty=q)
            strategy.exit('Short Exit', 'Short', stop=close + atr * slMult, limit=close - atr * slMult * rrRatio)

    hColor = (color.new(color.teal, 0) if hist > hist[1] else color.new(color.teal, 60)) if hist >= 0 else color.new(color.red, 0) if hist < hist[1] else color.new(color.red, 60)
    plot(hist, 'Histogram', style=plot.style_columns, color=hColor)
    plot(macdLine, 'MACD', color=color.blue, linewidth=2)
    plot(signalLine, 'Signal', color=color.orange, linewidth=1)
    hline(0, 'Zero', color=color.gray, linestyle=hline.style_dashed)

    plot(trendEma, 'Trend EMA', color=color.new(color.gray, 20), linewidth=2, force_overlay=True)
    plot(slLvl, 'Stop', color=color.red, style=plot.style_linebr, force_overlay=True)
    plot(tpLvl, 'Target', color=color.green, style=plot.style_linebr, force_overlay=True)
    plotshape(longSignal, 'Long', style=shape.triangleup, location=location.belowbar, color=color.teal, size=size.small, force_overlay=True)
    plotshape(shortSignal, 'Short', style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small, force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)