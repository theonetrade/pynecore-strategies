"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, close, color, dayofmonth, high, input, math, nz, script,
    strategy, ta
)
from pynecore.types import PersistentSeries


@script.strategy(title='Elder Ray (Bull Power) TP and SL', shorttitle='Bull Power', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    Profit=input.float(7, title='Take Profit %', minval=0.01),
    Stop=input.float(7, title='Stop Loss %', minval=0.01),
    Length=input.int(14, minval=1),
    Trigger=input.float(-200),
    reverse=input.bool(True, title='Trade reverse')
):
    xPrice = close
    xMA = ta.ema(xPrice, Length)
    DayHigh: PersistentSeries = high
    DayHigh = high if dayofmonth != dayofmonth[1] else math.max(high, nz(DayHigh[1]))
    nRes = DayHigh - xMA
    pos: int = 0
    pos = 1 if nRes < Trigger else 0
    possig = -1 if reverse and pos == 1 else 1 if reverse and pos == -1 else pos
    if possig == 1 and strategy.position_size == 0:
        strategy.entry('Long', strategy.long, comment='Market Long')
        strategy.exit('ExitLong', 'Long', stop=close - close * Stop / 100, limit=close + close * Profit / 100, qty_percent=100)
    if possig == -1 and strategy.position_size == 0:
        strategy.entry('Short', strategy.short, comment='Market Long')
        strategy.exit('ExitShort', 'Short', stop=close + close * Stop / 100, limit=close - close * Profit / 100, qty_percent=100)
    barcolor(color.red if strategy.position_size == -1 else color.green if strategy.position_size == 1 else color.blue)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
