"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, high, input, low, math, na, nz, open, plot, script,
    strategy, syminfo, ta, time, timestamp
)
from pynecore.types import Persistent, PersistentSeries, Series


@script.strategy('SL1 Pips after TP1 (MA)', commission_type=strategy.commission.cash_per_order, overlay=True, default_qty_value=1000, initial_capital=100, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, close_by_id=True, na_bool=True)
def main(
    Buy=input(True),
    Sell=input(True),
    start_year=input(title='Start year', defval=2020),
    start_month=input(title='Start month', defval=1),
    start_day=input(title='Start day', defval=1),
    start_hour=input(title='Start hour', defval=0),
    start_minute=input(title='Start minute', defval=0),
    end_time=input(title='set end time?', defval=False),
    end_year=input(title='end year', defval=2019),
    end_month=input(title='end month', defval=12),
    end_day=input(title='end day', defval=31),
    end_hour=input(title='end hour', defval=23),
    end_minute=input(title='end minute', defval=59),
    ema_period=input(title='EMA period', defval=10),
    wma_period=input(title='WMA period', defval=20),
    __input_15__=input(20)
):
    ema = ta.ema(close, ema_period)
    wma = ta.wma(close, wma_period)
    buy = ta.crossover(ema, wma) and nz(strategy.position_size) == 0 and Buy and (time > timestamp(start_year, start_month, start_day, start_hour, start_minute)) and (time < timestamp(end_year, end_month, end_day, end_hour, end_minute) if end_time else True)
    sell = ta.crossunder(ema, wma) and nz(strategy.position_size) == 0 and Sell and (time > timestamp(start_year, start_month, start_day, start_hour, start_minute)) and (time < timestamp(end_year, end_month, end_day, end_hour, end_minute) if end_time else True)
    pip: Series = __input_15__ * 10 * syminfo.mintick
    LS: Persistent[bool] = na(bool)
    SS: Persistent[bool] = na(bool)
    EP: Persistent[float] = na(float)
    TVL: Persistent[float] = na(float)
    TVS: Persistent[float] = na(float)
    TSL: PersistentSeries[float] = na(float)
    TSS: PersistentSeries[float] = na(float)
    TP1: Persistent[float] = na(float)
    TP2: Persistent[float] = na(float)
    SL1: Persistent[float] = na(float)
    SL2: Persistent[float] = na(float)
    if buy or (sell and strategy.position_size == 0):
        EP = close
        SL1 = EP - pip * (-1 if sell else 1)
        SL2 = EP - pip * (-1 if sell else 1)
        TP1 = EP + pip * (-1 if sell else 1)
        TP2 = EP + pip * 2 * (-1 if sell else 1)
    LS = buy or strategy.position_size > 0
    SS = sell or strategy.position_size < 0
    TVL = math.max(TP1, open) - pip[1]
    TVS = math.min(TP1, open) + pip[1]
    TSL = math.max(TVL, TSL[1]) if open[1] > TSL[1] else TVL
    TSS = math.min(TVS, TSS[1]) if open[1] < TSS[1] else TVS
    if LS and high > TP1:
        if open <= TP1:
            SL2 = math.min(EP, TSL)
    if SS and low < TP1:
        if open >= TP1:
            SL2 = math.max(EP, TSS)
    close_long = LS and open < SL2
    close_short = SS and open > SL2
    if buy and (not SS):
        strategy.entry('buy', strategy.long)
    strategy.exit('exit1', from_entry='buy', stop=SL1, limit=TP1, qty_percent=50)
    strategy.exit('exit2', from_entry='buy', stop=SL2, limit=TP2)
    if sell and (not LS):
        strategy.entry('sell', strategy.short)
    strategy.exit('exit3', from_entry='sell', stop=SL1, limit=TP1, qty_percent=50)
    strategy.exit('exit4', from_entry='sell', stop=SL2, limit=TP2)
    a = plot(SL1 if strategy.position_size > 0 else na, color=color.new(color.new('#DC143C'), 0), style=plot.style_linebr)
    b = plot(SL1 if strategy.position_size < 0 else na, color=color.new(color.new('#DC143C'), 0), style=plot.style_linebr)
    c = plot(TP1 if strategy.position_size > 0 else na, color=color.new(color.new('#00CED1'), 0), style=plot.style_linebr)
    d = plot(TP1 if strategy.position_size < 0 else na, color=color.new(color.new('#00CED1'), 0), style=plot.style_linebr)
    e = plot(TP2 if strategy.position_size > 0 else na, color=color.new(color.new('#00CED1'), 0), style=plot.style_linebr)
    f = plot(TP2 if strategy.position_size < 0 else na, color=color.new(color.new('#00CED1'), 0), style=plot.style_linebr)
    g = plot(na if strategy.position_size >= 0 else EP, color=color.new(color.new('#FFFFFF'), 0), style=plot.style_linebr)
    h = plot(na if strategy.position_size <= 0 else EP, color=color.new(color.new('#FFFFFF'), 0), style=plot.style_linebr)
    plot(ema, title='ema', color=color.new(color.new('#FFF176'), 0))
    plot(wma, title='wma', color=color.new(color.new('#00CED1'), 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
