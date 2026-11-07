"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, na, nz, script, strategy, ta
from pynecore.types import NA, Persistent, PersistentSeries, Series


@script.strategy('Crypto ZigZag RSI strategy 15min', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    length=input(5, title='RSI Length'),
    overSold=input(25),
    overBought=input(75),
    ZZPercent=input.float(1, title='Minimum % Change'),
    longa=input(True),
    shorta=input(False)
):
    p = close
    vrsi = ta.rsi(p, length)
    long: Persistent[bool] = na(bool)
    short: Persistent[bool] = na(bool)
    long = ta.crossover(vrsi, overSold)
    short = ta.crossunder(vrsi, overBought)
    last_open_long: PersistentSeries[float] = na(float)
    last_open_short: PersistentSeries[float] = na(float)
    last_open_long = close if long else nz(last_open_long[1])
    last_open_short = close if short else nz(last_open_short[1])
    entry_value = last_open_long
    entry_value1 = last_open_short
    r1Level: Series = entry_value
    s1Level: Series = entry_value1
    trend: Series[int] = 0
    trend = 1 if na(trend[1]) else trend[1]
    LL: Series[float] = 0.0
    LL = s1Level if na(LL[1]) else LL[1]
    HH: Series[float] = 0.0
    HH = r1Level if na(HH[1]) else HH[1]
    Pi = ZZPercent * 0.01
    zigzag = NA(float)
    if trend > 0:
        if r1Level >= HH:
            HH = r1Level
        else:
            if s1Level < HH * (1 - Pi):
                zigzag = r1Level[1]
                trend = -1
                LL = s1Level
    else:
        if s1Level <= LL:
            LL = s1Level
        else:
            if r1Level > LL * (1 + Pi):
                zigzag = s1Level[1]
                trend = 1
                HH = s1Level
    shortc = ta.crossunder(trend, 0)
    longc = ta.crossover(trend, 0)
    if longa:
        if longc:
            strategy.entry('long', strategy.long)
        if shortc:
            strategy.close('long')
    if shorta:
        if shortc:
            strategy.entry('short', strategy.short)
        if longc:
            strategy.close('long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
