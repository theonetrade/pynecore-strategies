"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, input, math, na, nz, plot, script, strategy,
    syminfo, ta, time, timestamp
)
from pynecore.types import NA, Series


@script.strategy('FS ATR & PS (MA)', overlay=True, default_qty_type=strategy.percent_of_equity, initial_capital=100, currency=currency.NONE, calc_on_every_tick=True, margin_long=0, margin_short=0, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    Buy=input(True),
    Sell=input(True),
    start_year=input(title='Start year', defval=2019),
    start_month=input(title='Start month', defval=1),
    start_day=input(title='Start day', defval=1),
    start_hour=input(title='Start hour ', defval=0),
    start_minute=input(title='Start minute', defval=0),
    end_time=input(title='set end time?', defval=False),
    end_year=input(title='end year', defval=2019),
    end_month=input(title='end month', defval=12),
    end_day=input(title='end day', defval=31),
    end_hour=input(title='end hour', defval=23),
    end_minute=input(title='end minute', defval=59),
    ema_period=input(title='EMA period', defval=10),
    wma_period=input(title='WMA period', defval=20),
    __input_15__=input(20),
    __input_16__=input(40),
    __input_17__=input.int(defval=10, title='Risk per trade%', step=1, minval=0, maxval=100)
):
    ema = ta.ema(close, ema_period)
    wma = ta.wma(close, wma_period)
    longCondition = ta.crossover(ema, wma) and Buy and (nz(strategy.position_size) == 0) and (time > timestamp(start_year, start_month, start_day, start_hour, start_minute)) and (time < timestamp(end_year, end_month, end_day, end_hour, end_minute) if end_time else True)
    shortCondition = ta.crossunder(ema, wma) and Sell and (nz(strategy.position_size) == 0) and (time > timestamp(start_year, start_month, start_day, start_hour, start_minute)) and (time < timestamp(end_year, end_month, end_day, end_hour, end_minute) if end_time else True)
    a = __input_15__ * 10
    b = __input_16__ * 10
    c = a * syminfo.mintick
    d = b * syminfo.mintick
    long_stop_level: Series = NA(float)
    long_profit_level1: Series = NA(float)
    long_profit_level2: Series = NA(float)
    long_even_level: Series = NA(float)
    short_stop_level: Series = NA(float)
    short_profit_level1: Series = NA(float)
    short_profit_level2: Series = NA(float)
    short_even_level: Series = NA(float)
    long_stop_level = close - c if longCondition else long_stop_level[1]
    long_profit_level1 = close + c if longCondition else long_profit_level1[1]
    long_profit_level2 = close + d if longCondition else long_profit_level2[1]
    long_even_level = close + 0 if longCondition else long_even_level[1]
    short_stop_level = close + c if shortCondition else short_stop_level[1]
    short_profit_level1 = close - c if shortCondition else short_profit_level1[1]
    short_profit_level2 = close - d if shortCondition else short_profit_level2[1]
    short_even_level = close + 0 if shortCondition else short_even_level[1]
    Risk = __input_17__ / 100
    size__ren__ = math.floor(strategy.equity * Risk / c)
    if longCondition:
        strategy.entry('Buy', strategy.long, qty=size__ren__)
        strategy.exit('Exit1', stop=long_stop_level, limit=long_profit_level1, qty=size__ren__ / 2)
        strategy.exit('Exit2', stop=long_stop_level, limit=long_profit_level2)
    if shortCondition:
        strategy.entry('Sell', strategy.short, qty=size__ren__)
        strategy.exit('Exit3', stop=short_stop_level, limit=short_profit_level1, qty=size__ren__ / 2)
        strategy.exit('Exit4', stop=short_stop_level, limit=short_profit_level2)
    plot(na if strategy.position_size <= 0 else long_stop_level, color=color.new(color.new('#DC143C'), 0), style=plot.style_linebr, linewidth=1)
    plot(na if strategy.position_size <= 0 else long_profit_level1, color=color.new(color.new('#00CED1'), 0), style=plot.style_linebr, linewidth=1)
    plot(na if strategy.position_size <= 0 else long_profit_level2, color=color.new(color.new('#00CED1'), 0), style=plot.style_linebr, linewidth=1)
    plot(na if strategy.position_size <= 0 else long_even_level, color=color.new(color.new('#FFFFFF'), 0), style=plot.style_linebr, linewidth=1)
    plot(na if strategy.position_size >= 0 else short_stop_level, color=color.new(color.new('#DC143C'), 0), style=plot.style_linebr, linewidth=1)
    plot(na if strategy.position_size >= 0 else short_profit_level1, color=color.new(color.new('#00CED1'), 0), style=plot.style_linebr, linewidth=1)
    plot(na if strategy.position_size >= 0 else short_profit_level2, color=color.new(color.new('#00CED1'), 0), style=plot.style_linebr, linewidth=1)
    plot(na if strategy.position_size >= 0 else short_even_level, color=color.new(color.new('#FFFFFF'), 0), style=plot.style_linebr, linewidth=1)
    plot(ema, color=color.new(color.new('#00CED1'), 0))
    plot(wma, color=color.new(color.new('#DC143C'), 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
