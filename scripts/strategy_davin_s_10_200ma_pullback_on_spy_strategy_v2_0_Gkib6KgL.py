"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, low, na, open, plot, script, strategy, ta,
    time, timestamp
)
from pynecore.types import Persistent, Series


@script.strategy('Davin\'s 10/200MA Pullback on SPY Strategy v2.0', overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.cash_per_contract, commission_value=0.1, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    i_ma1=input.int(title='MA Length 1', defval=200, step=10, group='Strategy Parameters', tooltip='Long-term MA 200'),
    i_ma2=input.int(title='MA Length 2', defval=10, step=10, group='Strategy Parameters', tooltip='Short-term MA 10'),
    i_ma3=input.int(title='MA Length 3', defval=50, step=1, group='Strategy Parameters', tooltip='MA for crossover signals`'),
    i_stopPercent=input.float(title='Stop Loss Percent', defval=0.15, step=0.01, group='Strategy Parameters', tooltip='Hard stop loss of 10%'),
    i_startTime=input.time(title='Start filter', defval=timestamp('01 Jan 2013 13:30 +0000'), group='Time filter', tooltip='Start date and time to begin'),
    i_endTime=input.time(title='End filter', defval=timestamp('01 Jan 2099 19:30 +0000'), group='Time filter', tooltip='End date and time to stop'),
    i_lowerClose=input.bool(title='Exit on lower close', defval=True, group='Strategy Parameters', tooltip='Wait for lower close after above 10SMA before exiting'),
    i_contrarianBuyTheDip=input.bool(title='Buy whenever more than x% drawdown', defval=True, group='Strategy Parameters', tooltip='Buy the dip! Whenever x% or more drawdown on SPY'),
    i_contrarianTrigger=input.int(title='Trigger % drop to buy the dip', defval=14, step=1, group='Strategy Parameters', tooltip='% drop to trigger contrarian Buy the Dip!'),
    i_stopByCrossover_MA2_3=input.bool(title='Include stop condition using MA crossover', defval=False, group='Strategy Parameters', tooltip='Sell when crossover of MA2/1 happens')
):
    ma1 = ta.sma(close, i_ma1)
    ma2 = ta.sma(close, i_ma2)
    ma3 = ta.sma(close, i_ma3)
    ma_9 = ta.ema(close, 9)
    ma_20 = ta.ema(close, 20)
    f_dateFilter = time > i_startTime and time <= i_endTime
    highest52 = ta.highest(high, 52)
    overall_change = (highest52 - close) / highest52 * 100
    buyPrice: Persistent[float] = 0
    buyCondition: Series = close > ma1 and close < ma2 and (strategy.position_size == 0) and f_dateFilter or (strategy.position_size == 0 and i_contrarianBuyTheDip == True and (overall_change > i_contrarianTrigger) and f_dateFilter)
    sellCondition = close > ma2 and strategy.position_size > 0 and (not i_lowerClose or close < low[1])
    stopDistance = (buyPrice - close) / close if strategy.position_size > 0 else na
    stopPrice = buyPrice - buyPrice * i_stopPercent if strategy.position_size > 0 else na
    stopCondition = strategy.position_size > 0 and stopDistance > i_stopPercent or (strategy.position_size > 0 and i_stopByCrossover_MA2_3 == True and (ma3 < ma1))
    if buyCondition:
        strategy.entry(id='Long', direction=strategy.long)
    if buyCondition[1]:
        buyPrice = open
    if sellCondition or stopCondition:
        strategy.close(id='Long', comment='Exit' + ('Stop loss=true' if stopCondition else ''))
        buyPrice = na
    plot(buyPrice, color=color.lime, style=plot.style_linebr)
    plot(stopPrice, color=color.red, style=plot.style_linebr, offset=-1)
    plot(ma1, color=color.blue)
    plot(ma2, color=color.white)
    plot(ma3, color=color.yellow)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
