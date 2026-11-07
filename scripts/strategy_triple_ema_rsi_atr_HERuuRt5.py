"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bgcolor, close, color, input, location, na, plot, plotshape, script,
    shape, size, strategy, syminfo, ta, volume
)
from pynecore.types import Persistent


@script.strategy('Triple EMA + RSI + ATR', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.1, slippage=3, margin_long=0, margin_short=0, initial_capital=1000000, close_by_id=True)
def main(
    fastLength=input.int(9, '快线 EMA', group='均线设置'),
    midLength=input.int(21, '中线 EMA', group='均线设置'),
    slowLength=input.int(55, '慢线 EMA', group='均线设置'),
    rsiLength=input.int(14, 'RSI 周期', group='RSI过滤'),
    rsiOverbought=input.int(65, 'RSI 超买线', group='RSI过滤'),
    rsiOversold=input.int(35, 'RSI 超卖线', group='RSI过滤'),
    atrLength=input.int(14, 'ATR 周期', group='止损止盈'),
    atrMultiplier=input.float(2.0, 'ATR 止损倍数', step=0.1, group='止损止盈'),
    rr1=input.float(2.0, '第一阶止盈 RR', group='止损止盈'),
    rr2=input.float(4.0, '第二阶止盈 RR（移动止盈触发）', group='止损止盈'),
    volLength=input.int(20, '成交量均线周期', group='放量确认'),
    volMultiplier=input.float(1.3, '放量倍数', step=0.1, group='放量确认')
):
    fastEMA = ta.ema(close, fastLength)
    midEMA = ta.ema(close, midLength)
    slowEMA = ta.ema(close, slowLength)
    rsi = ta.rsi(close, rsiLength)
    atr = ta.atr(atrLength)
    volMA = ta.sma(volume, volLength)
    longCondition = fastEMA > midEMA and midEMA > slowEMA and (close > fastEMA) and (rsi > 50) and (rsi < rsiOverbought) and (volume > volMA * volMultiplier)
    shortCondition = fastEMA < midEMA and midEMA < slowEMA and (close < fastEMA) and (rsi < 50) and (rsi > rsiOversold) and (volume > volMA * volMultiplier)
    if longCondition:
        strategy.entry('Long', strategy.long)
    if shortCondition:
        strategy.entry('Short', strategy.short)
    entryPrice: Persistent[float] = na(float)
    if strategy.position_size > 0:
        entryPrice = strategy.position_avg_price
    if strategy.position_size < 0:
        entryPrice = strategy.position_avg_price
    longStop = entryPrice - atr * atrMultiplier
    shortStop = entryPrice + atr * atrMultiplier
    longTake1 = entryPrice + (entryPrice - longStop) * rr1
    longTake2 = entryPrice + (entryPrice - longStop) * rr2
    shortTake1 = entryPrice - (shortStop - entryPrice) * rr1
    shortTake2 = entryPrice - (shortStop - entryPrice) * rr2
    strategy.exit('Long Exit', 'Long', stop=longStop, limit=longTake1, trail_points=(longTake2 - entryPrice) / syminfo.pointvalue)
    strategy.exit('Short Exit', 'Short', stop=shortStop, limit=shortTake1, trail_points=(entryPrice - shortTake2) / syminfo.pointvalue)
    plot(fastEMA, color=color.new(color.yellow, 0), title='快线 EMA')
    plot(midEMA, color=color.new(color.orange, 0), title='中线 EMA')
    plot(slowEMA, color=color.new(color.red, 0), title='慢线 EMA')
    plotshape(longCondition, title='多头信号', location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small)
    plotshape(shortCondition, title='空头信号', location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small)
    bgcolor(color.new(color.green, 90) if longCondition else na)
    bgcolor(color.new(color.red, 90) if shortCondition else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
