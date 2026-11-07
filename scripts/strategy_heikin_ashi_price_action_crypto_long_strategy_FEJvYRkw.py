"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, high, input, low, open, request, script, strategy, syminfo,
    ticker, timeframe
)
from pynecore.types import Series


@script.strategy(title='random', shorttitle='random', overlay=True, initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.1, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    UseHAcandles=input(True, title='Use Heikin Ashi Candles in Algo Calculations')
):
    haClose = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, close) if UseHAcandles else close
    haOpen = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, open) if UseHAcandles else open
    haHigh: Series = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, high) if UseHAcandles else high
    haLow: Series = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, low) if UseHAcandles else low
    long = haClose > haHigh[1] and haClose > haOpen and (haHigh[1] > haHigh[2])
    short = haClose < haOpen and haClose < haLow[1]
    if long:
        strategy.entry('long', strategy.long)
    if short:
        strategy.close('long')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
