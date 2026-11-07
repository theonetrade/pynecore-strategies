"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import alertcondition, close, color, input, low, ohlc4, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy('Double Exponential Moving Average 8-20-63 Strategy', shorttitle='DEMA-8-20-63', overlay=True, max_bars_back=5000, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.1, pyramiding=0, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    short=input.int(8, minval=1),
    srcShort: Series[float] = input(ohlc4, title='Source Dema 1'),
    long=input.int(20, minval=1),
    srcLong: Series[float] = input(low, title='Source Dema 2'),
    long2=input.int(63, minval=1),
    srcLong2: Series[float] = input(close, title='Source Dema 3')
):
    e1 = ta.ema(srcShort, short)
    e2 = ta.ema(e1, short)
    dema1 = 2 * e1 - e2
    plot(dema1, color=color.new(color.green, 0), linewidth=2)
    e3 = ta.ema(srcLong, long)
    e4 = ta.ema(e3, long)
    dema2 = 2 * e3 - e4
    plot(dema2, color=color.new(color.blue, 0), linewidth=2)
    e5 = ta.ema(srcLong2, long2)
    e6 = ta.ema(e5, long2)
    dema3 = 2 * e5 - e6
    plot(dema3, color=color.new(color.black, 0), linewidth=2)
    longC: Series = dema1 > dema2 and dema1 > dema3
    shortC: Series = dema1 < dema2 and dema1 < dema3
    alertlong = longC and (not longC[1])
    alertshort = shortC and (not shortC[1])
    if longC:
        strategy.entry('Long', strategy.long, comment='Long')
    if shortC:
        strategy.entry('Short', strategy.short, comment='Short')
    alertcondition(longC, title='Long', message=' Buy  Signal ')
    alertcondition(shortC, title='Short', message=' Sell Signal ')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)