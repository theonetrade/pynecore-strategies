"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, fill, format, high, hlc3, input, low, nz, plot, script,
    strategy, ta
)
from pynecore.types import Series


@script.strategy('AlphaTrend', shorttitle='AT', overlay=True, format=format.price, precision=2, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    coeff=input.float(1, 'Multiplier', step=0.1),
    AP=input(14, 'Common Period'),
    src: Series[float] = input(close),
    showsignalsk=input(title='Show Signals?', defval=True),
    novolumedata=input(title='Change calculation (no volume data)?', defval=False)
):
    ATR = ta.sma(ta.tr, AP)
    upT = low - ATR * coeff
    downT = high + ATR * coeff
    AlphaTrend: Series[float] = 0.0
    AlphaTrend = (nz(AlphaTrend[1]) if upT < nz(AlphaTrend[1]) else upT) if (ta.rsi(src, AP) >= 50 if novolumedata else ta.mfi(hlc3, AP) >= 50) else nz(AlphaTrend[1]) if downT > nz(AlphaTrend[1]) else downT
    color1 = color.new('#00E60F') if AlphaTrend > AlphaTrend[2] else color.new('#80000B') if AlphaTrend < AlphaTrend[2] else color.new('#00E60F') if AlphaTrend[1] > AlphaTrend[3] else color.new('#80000B')
    k1 = plot(AlphaTrend, color=color.new(color.new('#0022FC'), 0), linewidth=3)
    k2 = plot(AlphaTrend[2], color=color.new(color.new('#FC0400'), 0), linewidth=3)
    fill(k1, k2, color=color1)
    buySignalk: Series = ta.crossover(AlphaTrend, AlphaTrend[2])
    sellSignalk: Series = ta.crossunder(AlphaTrend, AlphaTrend[2])
    K1 = ta.barssince(buySignalk)
    K2 = ta.barssince(sellSignalk)
    O1 = ta.barssince(buySignalk[1])
    O2 = ta.barssince(sellSignalk[1])
    longCondition = buySignalk and showsignalsk and (O1 > K2)
    if longCondition:
        strategy.entry('BUY', strategy.long, comment='BUY ENTRY')
    shortCondition = sellSignalk and showsignalsk and (O2 > K1)
    if shortCondition:
        strategy.entry('SELL', strategy.short, comment='SELL ENTRY')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
