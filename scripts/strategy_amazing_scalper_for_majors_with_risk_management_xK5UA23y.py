"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, string, ta, time, timeframe
from pynecore.types import Series


@script.strategy(title='Triple EMA Scalper', shorttitle='3EMA scalper', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    len1=input.int(25, minval=1, title='Length'),
    len2=input.int(50, minval=1, title='Length'),
    len3=input.int(100, minval=1, title='Length'),
    src: Series[float] = input(close, title='Source'),
    tp=input(50, title='TP'),
    sl=input(100, title='SL'),
    tradeLondon=input(title='Trade london session?', defval=True),
    tradeNewyork=input(title='Trade new york session?', defval=True),
    __input_8__=input.float(1, title='Risk % of equity ')
):
    fastemaOut = ta.sma(src, len1)
    standardemaOut = ta.sma(src, len2)
    slowemaOut = ta.sma(src, len3)
    plot(fastemaOut, color=color.new(color.white, 0), title='First EMA')
    plot(standardemaOut, color=color.new(color.yellow, 0), title='Second EMA')
    plot(slowemaOut, color=color.new(color.blue, 0), title='Third EMA')
    def timeinrange(res, sess):
        return time(res, sess if sess == '' else sess + ('23456' if string.endswith(sess, ':') else '' if string.contains(sess, ':') else ':23456')) != 0

    londopen = timeinrange(timeframe.period, '0300-1100')
    nyopen = timeinrange(timeframe.period, '0800-1600')
    crossover_1 = ta.crossover(fastemaOut, slowemaOut)
    longCondition = ta.crossover(fastemaOut, standardemaOut) and crossover_1 and londopen
    crossunder_1 = ta.crossunder(fastemaOut, slowemaOut)
    shortCondition = ta.crossunder(fastemaOut, standardemaOut) and crossunder_1 and londopen
    crossover_2 = ta.crossover(fastemaOut, slowemaOut)
    longCondition2 = ta.crossover(fastemaOut, standardemaOut) and crossover_2 and nyopen
    crossunder_2 = ta.crossunder(fastemaOut, slowemaOut)
    shortCondition2 = ta.crossunder(fastemaOut, standardemaOut) and crossunder_2 and nyopen
    balance = strategy.netprofit + strategy.initial_capital
    floating = strategy.openprofit
    risk__global__ = __input_8__ / 100
    temp01 = balance * risk__global__
    temp02 = temp01 / sl
    temp03 = temp02 * 100000
    size__ren__ = temp03 - temp03 % 1000
    if size__ren__ < 1000:
        size__ren__ = 1000
    if tradeLondon == True:
        if longCondition:
            strategy.entry('long', strategy.long, size__ren__)
        strategy.exit('tp/sl', 'long', profit=tp, loss=sl)
        if shortCondition:
            strategy.entry('short', strategy.short, size__ren__)
        strategy.exit('tp/sl', 'short', profit=tp, loss=sl)
    if tradeNewyork == True:
        if longCondition2:
            strategy.entry('long', strategy.long, size__ren__)
        strategy.exit('tp/sl', 'long', profit=tp, loss=sl)
        if shortCondition2:
            strategy.entry('short', strategy.short, size__ren__)
        strategy.exit('tp/sl', 'short', profit=tp, loss=sl)
    strategy.risk.max_intraday_filled_orders(2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
