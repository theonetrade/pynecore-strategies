"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bgcolor, close, color, currency, input, na, plot, script, strategy,
    syminfo, ta, time, timestamp
)
from pynecore.types import Color, NA, Persistent, Series


@script.strategy(title='3 EMA + Stochastic RSI + ATR', shorttitle='3ESRA', overlay=True, pyramiding=1, process_orders_on_close=True, calc_on_every_tick=True, initial_capital=1000, currency=currency.USD, default_qty_value=10, default_qty_type=strategy.percent_of_equity, commission_type=strategy.commission.percent, commission_value=0.1, slippage=2, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    startDate=input.int(title='Start Date', defval=1, minval=1, maxval=31, group='Backtesting range'),
    startMonth=input.int(title='Start Month', defval=1, minval=1, maxval=12, group='Backtesting range'),
    startYear=input.int(title='Start Year', defval=1900, minval=1800, maxval=2100, group='Backtesting range'),
    endDate=input.int(title='End Date', defval=1, minval=1, maxval=31, group='Backtesting range'),
    endMonth=input.int(title='End Month', defval=1, minval=1, maxval=12, group='Backtesting range'),
    endYear=input.int(title='End Year', defval=2040, minval=1800, maxval=2100, group='Backtesting range'),
    fast=input.int(8, minval=8, title='Fast EMA', group='EMAs'),
    medium=input.int(14, minval=8, title='Medium EMA', group='EMAs'),
    slow=input.int(50, minval=8, title='Slow EMA', group='EMAs'),
    src: Series[float] = input(close, title='Source'),
    smoothK=input.int(3, 'K', minval=1, group='Stoch-RSI', inline='K&D'),
    smoothD=input.int(3, 'D', minval=1, group='Stoch-RSI', inline='K&D'),
    lengthRSI=input.int(14, 'RSI Length', minval=1, group='Stoch-RSI', inline='length'),
    lengthStoch=input.int(14, 'Stochastic Length', minval=1, group='Stoch-RSI', inline='length'),
    rsiSrc: Series[float] = input.source(close, title='RSI Source', group='Stoch-RSI'),
    length=input.int(title='Length', defval=14, minval=1, group='ATR'),
    smoothing=input.string(title='Smoothing', defval='RMA', options=('RMA', 'SMA', 'EMA', 'WMA'), group='ATR')
):
    inDateRange = time >= timestamp(syminfo.timezone, startYear, startMonth, startDate, 0, 0) and time < timestamp(syminfo.timezone, endYear, endMonth, endDate, 23, 59)
    fastema = ta.ema(src, fast)
    mediumema = ta.ema(src, medium)
    slowema = ta.ema(src, slow)
    rsi1 = ta.rsi(rsiSrc, lengthRSI)
    k: Series = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)
    d: Series = ta.sma(k, smoothD)
    sRsiCrossOver = k[1] < d[1] and k > d
    sRsiCrossUnder = k[1] > d[1] and k < d
    def ma_function(source, length):
        __block_result__ = na
        if smoothing == 'RMA':
            __block_result__ = ta.rma(source, length)
        else:
            __block_result_1__ = na
            if smoothing == 'SMA':
                __block_result_1__ = ta.sma(source, length)
            else:
                __block_result_2__ = na
                if smoothing == 'EMA':
                    __block_result_2__ = ta.ema(source, length)
                else:
                    __block_result_2__ = ta.wma(source, length)
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    atr = ma_function(ta.tr(True), length)
    longCond1 = fastema > mediumema and mediumema > slowema
    longCond2: bool = True
    longCond3 = close > fastema
    longCond4 = strategy.position_size <= 0
    longCond = longCond1 and longCond2 and longCond3 and longCond4 and inDateRange
    shortCond1 = fastema < mediumema and mediumema < slowema
    shortCond2: bool = True
    shortCond3 = close < fastema
    shortCond4 = strategy.position_size >= 0
    shortCond = shortCond1 and shortCond2 and shortCond3 and shortCond4 and inDateRange
    takeProfit: Persistent = NA(float)
    stopLoss: Persistent = NA(float)
    if longCond and strategy.position_size <= 0:
        takeProfit = close + 4 * atr
        stopLoss = close - 1 * atr
    elif shortCond and strategy.position_size >= 0:
        takeProfit = close - 4 * atr
        stopLoss = close + 1 * atr
    if longCond and strategy.position_size <= 0:
        strategy.entry('3ESRA', strategy.long, comment='Long')
    if shortCond and strategy.position_size >= 0:
        strategy.entry('3ESRA', strategy.short, comment='Short')
    strategy.exit(id='TP-SL', from_entry='3ESRA', limit=takeProfit, stop=stopLoss)
    if not inDateRange:
        strategy.close_all()
    plot(fastema, color=color.new(color.purple, 0), linewidth=2, title='Fast EMA')
    plot(mediumema, color=color.new(color.teal, 0), linewidth=2, title='Medium EMA')
    plot(slowema, color=color.new(color.yellow, 0), linewidth=2, title='Slow EMA')
    bgcolor(color.new(color.green, 75) if strategy.position_size > 0 else color.new(color.red, 75) if strategy.position_size < 0 else NA(Color))
    plot(takeProfit if strategy.position_size != 0 else na, style=plot.style_linebr, color=color.new(color.green, 0), title='TP')
    plot(stopLoss if strategy.position_size != 0 else na, style=plot.style_linebr, color=color.new(color.red, 0), title='SL')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
