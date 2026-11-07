"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import input, na, open, script, strategy, ta, time, timestamp
from pynecore.types import Series


@script.strategy('Range Strat - MACD/RSI', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=10, precision=2, initial_capital=1000, pyramiding=2, commission_value=0.05, margin_long=0, margin_short=0, close_by_id=True)
def main(
    StartDate=input.time(timestamp('13 Jun 2022'), title='Start Date'),
    EndDate=input.time(timestamp('13 Jun 2024'), title='Start Date'),
    rsisrc: Series[float] = input(title='RSI Source', defval=open, group='RSI Settings'),
    length=input(title='Length', defval=14, group='RSI Settings'),
    overSold=input(title='Over Sold Threshold', defval=55, group='RSI Settings'),
    overBought=input(title='Over Bought Threshold', defval=50, group='RSI Settings'),
    macdsrc: Series[float] = input(title='MACD Source', defval=open, group='MACD Settings'),
    fast_length=input(title='Fast Length', defval=12, group='MACD Settings'),
    slow_length=input(title='Slow Length', defval=26, group='MACD Settings'),
    signal_length=input.int(title='Signal Smoothing', minval=1, maxval=50, defval=9, group='MACD Settings'),
    sma_source=input.string(title='Oscillator MA Type', defval='EMA', options=('SMA', 'EMA'), group='MACD Settings'),
    sma_signal=input.string(title='Signal Line MA Type', defval='EMA', options=('SMA', 'EMA'), group='MACD Settings'),
    __input_12__=input(title='Long Stop Loss (%)', defval=15, group='Stop Loss Settings'),
    __input_13__=input(title='Short Stop Loss (%)', defval=15, group='Stop Loss Settings')
):
    inDateRange = time >= StartDate and time < EndDate
    vrsi = ta.rsi(rsisrc, length)
    RSIunder = vrsi <= overSold
    RSIover = vrsi >= overBought
    fast_ma = ta.sma(macdsrc, fast_length) if sma_source == 'SMA' else ta.ema(macdsrc, fast_length)
    slow_ma = ta.sma(macdsrc, slow_length) if sma_source == 'SMA' else ta.ema(macdsrc, slow_length)
    macd = fast_ma - slow_ma
    signal = ta.sma(macd, signal_length) if sma_signal == 'SMA' else ta.ema(macd, signal_length)
    delta = macd - signal
    MACDcrossover = ta.crossover(delta, 0)
    MACDcrossunder = ta.crossunder(delta, 0)
    longLossPerc = __input_12__ * 0.01
    shortLossPerc = __input_13__ * 0.01
    longStopPrice = strategy.position_avg_price * (1 - longLossPerc)
    shortStopPrice = strategy.position_avg_price * (1 + shortLossPerc)
    if not na(vrsi):
        if inDateRange and MACDcrossover and RSIunder:
            strategy.entry('LONG', strategy.long, comment='LONG')
        if inDateRange and MACDcrossunder and RSIover:
            strategy.entry('SHORT', strategy.short, comment='SHORT')
    if strategy.position_size > 0:
        strategy.exit(id='LONG STOP', stop=longStopPrice)
    if strategy.position_size < 0:
        strategy.exit(id='SHORT STOP', stop=shortStopPrice)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
