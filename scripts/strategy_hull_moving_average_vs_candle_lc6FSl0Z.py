"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    barmerge, color, fill, input, open, plot, request, script, strategy,
    syminfo, ta
)
from pynecore.types import Series


@script.strategy('Hull Moving Average vs Candle', shorttitle='HMA-vs-Candle', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.cash_per_order, commission_value=1.0, slippage=1, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    Period=input.int(title='Hull MA Period', defval=50, minval=1),
    Resolution=input.timeframe(title='Candle Resolution', defval='D'),
    Price: Series[float] = input(title='Source of Price', defval=open)
):
    HMA: Series = ta.hma(Price, Period)
    Candle = request.security(syminfo.tickerid, Resolution, Price, barmerge.gaps_off, barmerge.lookahead_off)
    change_color = color.green if HMA > Candle else color.red
    plot1 = plot(Candle, color=change_color, title='Candle Line', linewidth=2)
    plot2 = plot(HMA[1], color=change_color, title='Hull MA Line', linewidth=2)
    fill(plot1, plot2, color=color.new(change_color, 50))
    if Price < HMA and HMA < Candle:
        strategy.close('BUY', comment='close buy entry')
    if Price > HMA and HMA > Candle:
        strategy.close('SELL', comment='close sell entry')
    if Price > HMA and HMA > Candle and (Price > Price[1]):
        strategy.entry('BUY', strategy.long)
    if Price < HMA and HMA < Candle and (Price < Price[1]):
        strategy.entry('SELL', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
