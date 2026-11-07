"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, na, plot, script, strategy, ta


@script.strategy('Fixed Percent Stop Loss & Take Profit %', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    __input_0__=input(5.0, title='Stop Loss %'),
    __input_1__=input(10.0, title='Take Profit %')
):
    eg1 = ta.ema(close, 5)
    eg2 = ta.ema(close, 32)
    long = ta.crossover(eg1, eg2)
    short = ta.crossunder(eg1, eg2)
    if long:
        strategy.entry('LONG', strategy.long)
    if short:
        strategy.entry('SHORT', strategy.short)
    stopPer = __input_0__ / 100
    takePer = __input_1__ / 100
    longStop = strategy.position_avg_price * (1 - stopPer)
    shortStop = strategy.position_avg_price * (1 + stopPer)
    shortTake = strategy.position_avg_price * (1 - takePer)
    longTake = strategy.position_avg_price * (1 + takePer)
    if strategy.position_size > 0:
        strategy.exit(id='Close Long', stop=longStop, limit=longTake)
    if strategy.position_size < 0:
        strategy.exit(id='Close Short', stop=shortStop, limit=shortTake)
    plot(longStop if strategy.position_size > 0 else na, style=plot.style_linebr, color=color.new(color.red, 0), linewidth=1, title='Long Fixed SL')
    plot(shortStop if strategy.position_size < 0 else na, style=plot.style_linebr, color=color.new(color.red, 0), linewidth=1, title='Short Fixed SL')
    plot(longTake if strategy.position_size > 0 else na, style=plot.style_linebr, color=color.new(color.green, 0), linewidth=1, title='Long Take Profit')
    plot(shortTake if strategy.position_size < 0 else na, style=plot.style_linebr, color=color.new(color.green, 0), linewidth=1, title='Short Take Profit')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
