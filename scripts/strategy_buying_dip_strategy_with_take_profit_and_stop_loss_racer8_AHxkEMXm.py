"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.series import inline_series
from pynecore.lib import close, color, input, low, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy('BuyTheDip', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    atn=input(10, 'ATR Length'),
    tpm=input.float(2.0, 'ATR Take Profit', minval=0),
    slm=input.float(2.0, 'ATR Stop Loss', minval=0),
    n=input(7, 'Dip Length')
):
    atr = inline_series(ta.sma(ta.tr, atn), 1)
    bought = strategy.position_size > strategy.position_size[1]
    TakePrice = strategy.position_avg_price + tpm * atr
    FixedTakePrice = ta.valuewhen(bought, TakePrice, 0)
    plot(FixedTakePrice, 'ATR Take Profit', color=color.new(color.blue, 0), linewidth=1, style=plot.style_cross)
    StopPrice = strategy.position_avg_price - slm * atr
    FixedStopPrice = ta.valuewhen(bought, StopPrice, 0)
    plot(FixedStopPrice, 'ATR Stop Loss', color=color.new(color.yellow, 0), linewidth=1, style=plot.style_cross)
    Dip: Series = ta.lowest(low, n)
    if close < Dip[1]:
        strategy.entry('Buy', strategy.long)
    if strategy.position_size > 0:
        strategy.exit(id='Stop', stop=FixedStopPrice, limit=FixedTakePrice)
    plot(Dip, 'Dip Line', color=color.new(color.aqua, 0), linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
