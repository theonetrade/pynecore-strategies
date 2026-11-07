"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barcolor, close, color, high, low, na, nz, open, plot, request, script,
    strategy, syminfo, ta, timeframe
)
from pynecore.types import Series


@script.strategy('Previous Day High and Low Breakout Strategy', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main():
    D_High = request.security(syminfo.tickerid, 'D', high[1])
    D_Low = request.security(syminfo.tickerid, 'D', low[1])
    D_Close = request.security(syminfo.tickerid, 'D', close[1])
    D_Open = request.security(syminfo.tickerid, 'D', open[1])
    plot(D_High if timeframe.isintraday else na, title='Daily High', style=plot.style_line, color=color.new(color.new('#0000FF'), 0), linewidth=2)
    plot(D_Low if timeframe.isintraday else na, title='Daily Low', style=plot.style_line, color=color.new(color.new('#FF0000'), 0), linewidth=2)
    pos: Series[float] = 0.0
    iff_1 = -1 if D_Low > low else nz(pos[1], 0)
    pos = 1 if high > D_High else iff_1
    barcolor(color.new('#FF0000') if pos == -1 else color.new('#008000') if pos == 1 else color.new('#000000'))
    Buy = ta.crossover(high, D_High)
    Sell = ta.crossunder(low, D_Low)
    if ta.crossover(high, D_High):
        strategy.entry('Long', strategy.long, comment='Long')
    if ta.crossunder(low, D_Low):
        strategy.entry('Short', strategy.short, comment='Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
