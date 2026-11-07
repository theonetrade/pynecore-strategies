"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    color, fill, input, math, na, open, plot, script, strategy, ta, time,
    timestamp
)
from pynecore.types import Series


@script.strategy('Hull Moving Average Swing Trader', shorttitle='HMA_Swing_Trader', default_qty_type=strategy.percent_of_equity, default_qty_value=100, calc_on_order_fills=True, calc_on_every_tick=True, pyramiding=0, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    hullperiod=input.int(title='HullMA Period', defval=210, minval=1),
    price: Series[float] = input(open, title='Price data'),
    FromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    FromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    FromYear=input.int(defval=2020, title='From Year', minval=2017),
    ToMonth=input.int(defval=1, title='To Month', minval=1, maxval=12),
    ToDay=input.int(defval=1, title='To Day', minval=1, maxval=31),
    ToYear=input.int(defval=9999, title='To Year', minval=2017)
):
    start = timestamp(FromYear, FromMonth, FromDay, 0, 0)
    finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    n2ma = 2 * ta.wma(price, math.round(hullperiod / 2))
    nma = ta.wma(price, hullperiod)
    diff = n2ma - nma
    sqn = math.round(math.sqrt(hullperiod))
    n2ma1 = 2 * ta.wma(price[1], math.round(hullperiod / 2))
    nma1 = ta.wma(price[1], hullperiod)
    diff1 = n2ma1 - nma1
    n1 = ta.wma(diff, sqn)
    n2 = ta.wma(diff1, sqn)
    Hull_Line = n1 / n1 * n2
    __block_result__ = na
    if n1 > n2:
        Hull_retracted__00000019__ = Hull_Line - 2
        __block_result__ = Hull_retracted__00000019__
    else:
        Hull_retracted__0000001a__ = Hull_Line + 2
        __block_result__ = Hull_retracted__0000001a__
    Hull_retracted = __block_result__
    c1 = Hull_retracted + n1 - price
    c2 = Hull_retracted - n2 + price
    c4 = color.green if n1 > n2 else color.red
    c2p = plot(c2, color=color.new(color.black, 0), linewidth=1)
    c3p = plot(price, color=color.new(color.black, 0), linewidth=1)
    fill(c3p, c2p, color=color.new(c4, 75))
    if price < c2:
        if window():
            strategy.close('BUY')
    if price > c2:
        if window():
            strategy.close('SELL')
    if price > c2 and price[1] > c1:
        if window():
            strategy.entry('BUY', strategy.long)
    if price < c1 and price[1] < c2:
        if window():
            strategy.entry('SELL', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
