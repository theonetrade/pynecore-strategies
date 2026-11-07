"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, bgcolor, close, color, fill, high, input, low, math, na,
    nz, plot, script, strategy, ta
)
from pynecore.types import Series


@script.strategy('LUBE', overlay=False, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    barsback=input.int(500, 'bars back to measure friction', step=100),
    flevel=input.int(50, '0-100 friction level to stop trade', step=2),
    tlevel=input.int(-10, 'pic lower than 0 to number selected above to initiate trade', step=2),
    range_1=input.int(100, 'bars back to measure lowest friction', step=10),
    src: Series[float] = input(title='Source', defval=close),
    leverage=input.float(2, 'leverage', step=0.5),
    enableshort=input(True, 'enable shorts?')
):
    friction: float = 0.0
    fl = flevel / 100
    tl = tlevel / 100
    for i in pine_range(1, barsback, 1):
        __block_result__ = na
        if high[i] >= close and low[i] <= close:
            __block_result__ = friction + (1 + barsback) / (i + barsback)
        else:
            __block_result__ = friction
        friction = __block_result__
    lowf = ta.lowest(friction, range_1)
    highf: Series = ta.highest(friction, range_1)
    midf: Series = lowf * (1 - fl) + highf * fl
    lowf2: Series = lowf * (1 - tl) + highf * tl
    plot(friction)
    m = plot(midf[5], color=color.new(color.red, 0))
    l = plot(lowf2[5], color=color.new(color.white, 0))
    h = plot(highf[5], color=color.new(color.white, 0))
    fill(l, h, color.new(color.white, 90))
    def _fir(src: Series):
        return (4 * src + 3 * nz(src[1]) + 2 * nz(src[2]) + nz(src[3])) / 10

    fir: Series = _fir(src)
    trend = 1 if fir > fir[1] else -1
    long = friction < lowf2[5] and trend == 1
    short = friction < lowf2[5] and trend == -1
    end = friction > midf[5]
    keeplong: Series[int] = 0
    keeplong = 1 if long else nz(keeplong[1])
    keeplong = 0 if short or end else keeplong
    keepshort: Series[int] = 0
    keepshort = 1 if short else nz(keepshort[1])
    keepshort = 0 if long or end else keepshort
    bgcolor(color.lime if keeplong == 1 else color.red if keepshort == 1 else na)
    barcount: Series[int] = 0
    barcount = nz(barcount[1]) + 1
    contracts = math.min(math.max(1e-06, strategy.equity / close * leverage), 1000000000)
    if long and barcount > 20:
        strategy.entry('Long', strategy.long, qty=contracts)
    if short or end:
        strategy.close('Long')
    if short and enableshort == True and (barcount > 20):
        strategy.entry('Short', strategy.short, qty=contracts)
    if (long or end) and enableshort == True:
        strategy.close('Short')
    alertcondition(keeplong == 1 and keeplong[1] == 0, 'LONG')
    alertcondition(keepshort == 1 and keepshort[1] == 0, 'SHORT')
    alertcondition((keeplong[1] == 1 or keepshort[1] == 1) and keeplong == 0 and (keepshort == 0), 'CLOSE TRADE')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
