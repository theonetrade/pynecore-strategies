"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, syminfo, ta, time, timestamp


@script.strategy('RSI and SMA', overlay=True, initial_capital=1000, process_orders_on_close=True, default_qty_type=strategy.percent_of_equity, default_qty_value=30, commission_type=strategy.commission.percent, commission_value=0.1, margin_long=0, margin_short=0, close_by_id=True)
def main(
    showDate=input(defval=True, title='Show Date Range'),
    length=input(14)
):
    timePeriod = time >= timestamp(syminfo.timezone, 2022, 1, 1, 0, 0)
    notInTrade = strategy.position_size <= 0
    rsi = ta.rsi(close, length)
    fastEMA = ta.sma(close, 100)
    slowEMA = ta.sma(close, 150)
    plot(fastEMA, color=color.green)
    plot(slowEMA, color=color.blue)
    bullish = ta.crossover(fastEMA, slowEMA) and rsi > 50
    bearish = ta.crossover(slowEMA, fastEMA) and rsi < 50
    if bullish and timePeriod:
        strategy.entry('Long', strategy.long)
    if bearish:
        strategy.close('Exit')
    if bearish and timePeriod:
        strategy.entry('Short', strategy.short)
    if bullish:
        strategy.close('Exit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
