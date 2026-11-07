"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fixnan, input, location, math, na, nz, plot, plotshape,
    script, shape, size, strategy, syminfo, ta, time
)
from pynecore.types import NA, Persistent, PersistentSeries, Series


@script.strategy(title='SuperTREX strategy', overlay=True, pyramiding=1, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=25, calc_on_order_fills=False, slippage=0, commission_type=strategy.commission.percent, commission_value=0.075, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    strat_dir_input=input.string(title='Strategy Direction', defval='long', options=('long', 'short', 'all')),
    length=input(14),
    overSold=input(35),
    overBought=input(70),
    HTF=input.timeframe('W'),
    st_mult=input.float(4, title='SuperTrend Multiplier', minval=0, maxval=100, step=0.01),
    st_period=input.int(10, title='SuperTrend Period', minval=1),
    stoploss=input.float(title=' stop loss', defval=25, minval=0.01),
    q1=input.int(title=' qty_percent1', defval=25, minval=1),
    q2=input.int(title=' qty_percent2', defval=25, minval=1),
    q3=input.int(title=' qty_percent3', defval=25, minval=1),
    tp1=input.float(title=' Take profit1', defval=10, minval=0.01),
    tp2=input.float(title=' Take profit2', defval=20, minval=0.01),
    tp3=input.float(title=' Take profit3', defval=50, minval=0.01),
    tp4=input.float(title=' Take profit4', defval=100, minval=0.01)
):
    strat_dir_value = strategy.direction.long if strat_dir_input == 'long' else strategy.direction.short if strat_dir_input == 'short' else strategy.direction.all
    strategy.risk.allow_entry_in(strat_dir_value)
    ti = ta.change(time(HTF)) != 0
    p = fixnan(close if ti else na)
    vrsi = ta.rsi(p, length)
    price = close
    long: Persistent[bool] = na(bool)
    short: Persistent[bool] = na(bool)
    long = ta.crossover(vrsi, overSold)
    short = ta.crossunder(vrsi, overBought)
    last_open_long: PersistentSeries[float] = na(float)
    last_open_short: PersistentSeries[float] = na(float)
    last_open_long = close if long else nz(last_open_long[1])
    last_open_short = close if short else nz(last_open_short[1])
    entry_value: Series = last_open_long
    entry_value1: Series = last_open_short
    xy = (entry_value + entry_value) / 2
    up_lev = xy - st_mult * ta.atr(st_period)
    dn_lev = xy + st_mult * ta.atr(st_period)
    up_trend: Series[float] = 0.0
    up_trend = math.max(up_lev, up_trend[1]) if entry_value[1] > up_trend[1] else up_lev
    down_trend: Series[float] = 0.0
    down_trend = math.min(dn_lev, down_trend[1]) if entry_value1[1] < down_trend[1] else dn_lev
    trend: Series[int] = 0
    trend = 1 if close > down_trend[1] else -1 if close < up_trend[1] else nz(trend[1], 1)
    st_line = up_trend if trend == 1 else down_trend
    plot(xy, color=color.green if trend == 1 else color.red)
    buy = ta.crossover(close, st_line)
    sell1 = ta.crossunder(close, st_line)
    buy1 = buy
    sell = sell1
    plotshape(buy, title='buy', text='Buy', color=color.new(color.green, 0), style=shape.labelup, location=location.belowbar, size=size.small, textcolor=color.new(color.white, 0))
    plotshape(sell, title='sell', text='Sell', color=color.new(color.red, 0), style=shape.labeldown, location=location.abovebar, size=size.small, textcolor=color.new(color.white, 0))
    l = buy
    s1 = sell
    if l:
        strategy.entry('buy', strategy.long)
    if s1:
        strategy.entry('sell', strategy.short)
    def per(pcnt):
        return math.round(pcnt / 100 * strategy.position_avg_price / syminfo.mintick) if strategy.position_size != 0 else NA(float)

    los = per(stoploss)
    strategy.exit('x1', qty_percent=q1, profit=per(tp1), loss=los)
    strategy.exit('x2', qty_percent=q2, profit=per(tp2), loss=los)
    strategy.exit('x3', qty_percent=q3, profit=per(tp3), loss=los)
    strategy.exit('x4', profit=per(tp4), loss=los)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
