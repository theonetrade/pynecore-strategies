"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, currency, input, plot, script, strategy, ta, time, timestamp


@script.strategy('EMA Cross Strategy', overlay=True, calc_on_every_tick=True, currency=currency.USD, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    emaFast=input.int(title='Fast EMA', defval=10, minval=1, maxval=9999),
    emaSlow=input.int(title='Slow EMA', defval=20, minval=1, maxval=9999),
    tradeDirection=input.string(title='Trade Direction', options=('Long', 'Short', 'Both'), defval='Both'),
    startDate=input.time(title='Start Date', defval=timestamp('01 Jan 1970 00:00')),
    endDate=input.time(title='End Date', defval=timestamp('31 Dec 2170 23:59'))
):
    fastEMA = ta.ema(close, emaFast)
    slowEMA = ta.ema(close, emaSlow)
    plot(series=fastEMA, color=color.new(color.orange, 0), linewidth=2)
    plot(series=slowEMA, color=color.new(color.blue, 0), linewidth=2)
    inDateRange = time >= startDate and time < endDate
    longOK = tradeDirection == 'Long' or tradeDirection == 'Both'
    shortOK = tradeDirection == 'Short' or tradeDirection == 'Both'
    longCondition = ta.crossover(fastEMA, slowEMA)
    shortCondition = ta.crossunder(fastEMA, slowEMA)
    if longCondition and inDateRange:
        if longOK:
            strategy.entry(id='long', direction=strategy.long)
    if shortCondition and inDateRange:
        if shortOK:
            strategy.entry(id='short', direction=strategy.short)
    if strategy.position_size > 0 and shortCondition:
        strategy.exit(id='exit long', stop=close)
    if strategy.position_size < 0 and longCondition:
        strategy.exit(id='exit short', stop=close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)