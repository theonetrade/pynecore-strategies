"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, fill, high, input, low, math, na, open, plot,
    script, strategy, syminfo, ta
)
from pynecore.types import Series


@script.strategy('Bollinger Bands + EMA 9', overlay=True, initial_capital=1000, process_orders_on_close=True, default_qty_type=strategy.fixed, margin_long=0, margin_short=0, default_qty_value=1, close_by_id=True)
def main(
    max_risk_percentage=input.float(1, 'Max Risk (%)', minval=0.01, maxval=99, step=0.01, group='Risk Management'),
    riskType=input.string('%', title='Risk Type', options=('%', '$'), group='Risk Management')
):
    bb_upper = ta.sma(close, 20) + 2 * ta.stdev(close, 20)
    bb_lower = ta.sma(close, 20) - 2 * ta.stdev(close, 20)
    ema: Series = ta.ema(close, 9)
    bull_candle = close > open
    bear_candle = close < open
    def barsSinceLastEntry():
        return bar_index - strategy.opentrades.entry_bar_index(strategy.opentrades - 1) if strategy.opentrades > 0 else na

    def percent2money(price, percent):
        return price * percent / 100 * syminfo.pointvalue

    def calcPositionSize(entry, stop_size):
        __block_result__ = na
        if riskType == '% from equity':
            __block_result__ = strategy.equity * max_risk_percentage / 100
        else:
            __block_result__ = max_risk_percentage
        risk = __block_result__
        return risk / percent2money(entry, stop_size)

    stop: float = 0.0
    entry: float = 0.0
    tp: float = 0.0
    if close[1] < bb_lower and bull_candle and (strategy.position_size == 0):
        stop = low[1]
        entry = close
        tp = ema
        stop_size = (entry - stop) / stop
        order_size = calcPositionSize(close, stop_size)
        strategy.entry('LONG', strategy.long, math.abs(order_size))
    if close[1] > bb_upper and bear_candle and (strategy.position_size == 0):
        stop = high[1]
        entry = close
        tp = ema
        stop_size = (stop - entry) / stop
        order_size = calcPositionSize(close, stop_size)
        strategy.entry('SHORT', strategy.short, math.abs(order_size))
    if strategy.position_size > 0:
        strategy.exit('LONG', limit=ema[barsSinceLastEntry()], stop=low[barsSinceLastEntry() + 1], comment_profit='✅', comment_loss='❌')
    if strategy.position_size < 0:
        strategy.exit('SHORT', limit=ema[barsSinceLastEntry()], stop=high[barsSinceLastEntry() + 1], comment_profit='✅', comment_loss='❌')
    plot(bb_upper, color=color.red)
    plot(bb_lower, color=color.green)
    plot(ema, color=color.white)
    longEntryPlot = plot(strategy.position_avg_price if strategy.position_size > 0 else na, color=color.new(color.white, 85), style=plot.style_linebr)
    longTargetPlot = plot(ema[barsSinceLastEntry()] if strategy.position_size > 0 else na, color=color.new(color.green, 85), style=plot.style_linebr)
    longStopPlot = plot(low[barsSinceLastEntry() + 1] if strategy.position_size > 0 else na, color=color.new(color.red, 85), style=plot.style_linebr)
    fill(longEntryPlot, longTargetPlot, color=color.new(color.green, 85), editable=True)
    fill(longEntryPlot, longStopPlot, color=color.new(color.red, 85), editable=True)
    shortEntryPlot = plot(strategy.position_avg_price if strategy.position_size < 0 else na, color=color.new(color.white, 85), style=plot.style_linebr)
    shortTargetPlot = plot(ema[barsSinceLastEntry()] if strategy.position_size < 0 else na, color=color.new(color.green, 85), style=plot.style_linebr)
    shortStopPlot = plot(high[barsSinceLastEntry() + 1] if strategy.position_size < 0 else na, color=color.new(color.red, 85), style=plot.style_linebr)
    fill(shortEntryPlot, shortTargetPlot, color=color.new(color.green, 85), editable=True)
    fill(shortEntryPlot, shortStopPlot, color=color.new(color.red, 85), editable=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
