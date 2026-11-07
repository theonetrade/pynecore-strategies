"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    barstate, close, color, input, math, na, plot, request, script, strategy,
    syminfo, ta, ticker, timeframe
)
from pynecore.types import Color, Persistent, Series


@script.strategy('RSI Trend Reversal', overlay=True, max_bars_back=4999, calc_on_every_tick=False, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    rsi_length=input.int(title='Lenght', defval=8),
    rsi_mult=input.float(title='Multiplier', defval=1.5, step=0.05),
    lookback=input.int(title='Delay to prevent idealization', defval=1),
    sltp=input.float(title='Minimum Difference', defval=10),
    src: Series[float] = input.source(title='Source Input', defval=close)
):
    hclose = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, src)
    def highest_custom(src: Series, length):
        x = src
        for i in pine_range(0, length, 1):
            if src[i] > x:
                x = src[i]
        return x

    def lowest_custom(src: Series, length):
        x = src
        for i in pine_range(0, length, 1):
            if src[i] < x:
                x = src[i]
        return x

    def rsilev(src, length, mult, sltp):
        sl = (100 - sltp) / 100
        tp = (100 + sltp) / 100
        crossup: Persistent[bool] = na(bool)
        crossdown: Persistent[bool] = na(bool)
        dir: Persistent[float] = na(float)
        BearGuy: Persistent[float] = 0
        BullGuy = ta.barssince(crossup or crossdown)
        if na(BullGuy):
            BearGuy = BearGuy + 1
        else:
            BearGuy = BullGuy
        upper: Persistent[float] = na(float)
        lower: Persistent[float] = na(float)
        rsilower = ta.rsi(src, length)
        rsiupper = math.abs(ta.rsi(src, length) - 100)
        atr = ta.atr(length) / src
        lower = highest_custom(math.max(highest_custom(highest_custom(src, BearGuy) * (1 - (atr + 1 / rsilower * mult)), BearGuy), src * sl), BearGuy)
        upper = lowest_custom(math.min(lowest_custom(lowest_custom(src, BearGuy) * (1 + atr + 1 / rsiupper * mult), BearGuy), src * tp), BearGuy)
        thresh: Persistent[float] = na(float)
        if na(thresh):
            thresh = lower
        if na(dir):
            dir = 1
        if crossdown:
            dir = -1
        if crossup:
            dir = 1
        if dir == 1:
            thresh = lower
        if dir == -1:
            thresh = upper
        crossup = ta.crossover(src, thresh)
        crossdown = ta.crossunder(src, thresh)
        return thresh

    rsiclose = rsilev(hclose, rsi_length, rsi_mult, sltp)
    col: Persistent[Color] = color.lime
    col = color.lime if hclose > rsiclose else color.red
    plot(rsiclose, linewidth=2, color=col)
    buy: Series = ta.crossover(hclose, rsiclose) and barstate.isconfirmed
    sell: Series = ta.crossunder(hclose, rsiclose) and barstate.isconfirmed
    if buy[lookback]:
        strategy.entry('long', strategy.long)
    if sell[lookback]:
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
