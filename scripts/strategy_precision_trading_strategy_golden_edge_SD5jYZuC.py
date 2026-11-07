"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, low, position, script, strategy, ta, table,
    text, time, timestamp
)
from pynecore.types import Persistent, Series, Table


@script.strategy('PTS: Golden Edge', shorttitle='PTS: GE', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    fastEMA=input(3, title='Fast EMA'),
    slowEMA=input(33, title='Slow EMA'),
    hmaLength=input(66, title='HMA Length for Trend Filter'),
    rsiLength=input(12, title='RSI Length'),
    atrLength=input(14, title='ATR Length'),
    atrThreshold=input.float(0.1, title='Minimum ATR Threshold (Volatility)'),
    rangeFilterMultiplier=input.float(0.5, title='Range Filter Multiplier (ATR)'),
    startTestTime=input.time(timestamp('2023-01-01 00:00'), title='Backtest Start Time'),
    endTestTime=input.time(timestamp('2024-12-31 23:59'), title='Backtest End Time')
):
    isInBacktestRange = time >= startTestTime and time <= endTestTime
    fastEMAValue = ta.ema(close, fastEMA)
    slowEMAValue = ta.ema(close, slowEMA)
    hma: Series = ta.hma(close, hmaLength)
    rsi = ta.rsi(close, rsiLength)
    atr = ta.atr(atrLength)
    trendUp = hma > hma[1]
    trendDown = hma < hma[1]
    rangeFilter = ta.highest(high, atrLength) - ta.lowest(low, atrLength) > atr * rangeFilterMultiplier
    buySignal = ta.crossover(fastEMAValue, slowEMAValue) and rsi > 56 and trendUp and rangeFilter
    sellSignal = ta.crossunder(fastEMAValue, slowEMAValue) and rsi < 45 and trendDown and rangeFilter
    if isInBacktestRange:
        if buySignal:
            strategy.entry('Buy', strategy.long)
        if sellSignal:
            strategy.entry('Sell', strategy.short)
    trendTable: Persistent[Table] = table.new(position.top_right, 2, 2, frame_color=color.black, border_color=color.new(color.white, 90), border_width=2, bgcolor=color.gray, frame_width=2, force_overlay=True)
    currentPosition: Persistent[str] = 'NONE'
    if strategy.position_size > 0:
        currentPosition = 'BUY'
    elif strategy.position_size < 0:
        currentPosition = 'SELL'
    table.cell(trendTable, 0, 0, 'PTS: Golden Edge', text_color=color.new('#FFD815'), bgcolor=color.new(color.black, 40), text_halign=text.align_center)
    table.cell(trendTable, 1, 0, currentPosition, text_color=color.new('#3DA8FF') if currentPosition == 'BUY' else color.new(color.red, 0) if currentPosition == 'SELL' else color.new(color.gray, 0), bgcolor=color.new(color.black, 0), text_halign=text.align_center)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
