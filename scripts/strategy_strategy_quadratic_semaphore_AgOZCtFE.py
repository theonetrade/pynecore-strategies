"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    bar_index, color, currency, high, input, location, low, math, plotshape,
    script, shape, size, strategy, ta, time, timestamp
)
from pynecore.types import Series


@script.strategy(title=' Strategy Quadratic Semaphore ', shorttitle='SQS', overlay=True, precision=8, calc_on_order_fills=True, calc_on_every_tick=True, backtest_fill_limits_assumption=0, default_qty_type=strategy.fixed, default_qty_value=2, initial_capital=10000, pyramiding=5, currency=currency.USD, linktoseries=True, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    backTestSectionFrom=input(title='═══════════════ From ═══════════════', defval=True),
    FromMonth=input.int(defval=1, title='Month', minval=1),
    FromDay=input.int(defval=1, title='Day', minval=1),
    FromYear=input.int(defval=2019, title='Year', minval=2014),
    backTestSectionTo=input(title='════════════════ To ════════════════', defval=True),
    ToMonth=input.int(defval=31, title='Month', minval=1),
    ToDay=input.int(defval=12, title='Day', minval=1),
    ToYear=input.int(defval=9999, title='Year', minval=2014),
    Config=input(title='══════════════ Config ══════════════', defval=True),
    p=input(6),
    length=input(30)
):
    def backTestPeriod():
        return time > timestamp(FromYear, FromMonth, FromDay, 0, 0) and time < timestamp(ToYear, ToMonth, ToDay, 23, 59)

    x1 = bar_index
    x2 = math.sqrt(x1)
    y = high
    S11 = math.sum(x2, length) - math.sqrt(math.sum(x1, length)) / length
    S12 = math.sum(x1 * x2, length) - math.sum(x1, length) * math.sum(x2, length) / length
    S22 = math.sum(math.sqrt(x2), length) - math.sqrt(math.sum(x2, length)) / length
    Sy1 = math.sum(y * x1, length) - math.sum(y, length) * math.sum(x1, length) / length
    Sy2 = math.sum(y * x2, length) - math.sum(y, length) * math.sum(x2, length) / length
    max1 = ta.sma(x1, length)
    max2 = ta.sma(x2, length)
    may = ta.sma(y, length)
    b2 = (Sy1 * S22 - Sy2 * S12) / (S22 * S11 - math.sqrt(S12))
    b3 = (Sy2 * S11 - Sy1 * S12) / (S22 * S11 - math.sqrt(S12))
    b1 = may - b2 * max1 - b3 * max2
    qr: Series = b1 + b2 * x1 + b3 * x2
    yl = low
    Sy1l = math.sum(yl * x1, length) - math.sum(yl, length) * math.sum(x1, length) / length
    Sy2l = math.sum(yl * x2, length) - math.sum(yl, length) * math.sum(x2, length) / length
    mayl = ta.sma(yl, length)
    b2l = (Sy1l * S22 - Sy2l * S12) / (S22 * S11 - math.sqrt(S12))
    b3l = (Sy2l * S11 - Sy1l * S12) / (S22 * S11 - math.sqrt(S12))
    b1l = mayl - b2l * max1 - b3l * max2
    qrl: Series = b1l + b2l * x1 + b3l * x2
    period = math.round(p / 2) + 1
    hh = qr[period]
    ll = qrl[period]
    countH: int = 0
    countL: int = 0
    buy: int = 0
    sell: int = 0
    for i in pine_range(1, period - 1, 1):
        if qr[i] < hh:
            countH = countH + 1
        if qrl[i] > ll:
            countL = countL + 1
    for i in pine_range(period + 1, p + 1, 1):
        if qr[i] < hh:
            countH = countH + 1
        if qrl[i] > ll:
            countL = countL + 1
    if countH == p:
        pivotH = high[period]
        buy = 1
    if countL == p:
        pivotL = low[period]
        sell = 1
    plotshape(buy == 1, text='💣', style=shape.arrowup, location=location.belowbar, color=color.new(color.new('#32CD32'), 0), textcolor=color.new(color.white, 0), offset=0, size=size.auto)
    plotshape(sell == 1, text='🔨', style=shape.arrowdown, location=location.abovebar, color=color.new(color.new('#FF0000'), 0), textcolor=color.new(color.white, 0), offset=0, size=size.auto)
    if backTestPeriod():
        if buy == 1:
            strategy.entry('long', strategy.long, 1)
        if sell == 1:
            strategy.entry('short', strategy.short, 1)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
