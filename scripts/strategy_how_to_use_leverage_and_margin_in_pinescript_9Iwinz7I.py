"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, fill, high, hline, input, low, plot, script, strategy, ta


@script.strategy(title='How to use Leverage and Margin in PineScript', overlay=False, pyramiding=100, default_qty_type=strategy.percent_of_equity, default_qty_value=3000, margin_long=1.0 / 30 * 50, margin_short=1.0 / 30 * 50, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    periodK=input.int(13, title='K', minval=1),
    periodD=input.int(3, title='D', minval=1),
    smoothK=input.int(4, title='Smooth', minval=1),
    TP=input(100, title='Take Profit (in ticks)')
):
    k = ta.sma(ta.stoch(close, high, low, periodK), smoothK)
    d = ta.sma(k, periodD)
    plot(k, title='%K', color=color.new(color.blue, 0))
    plot(d, title='%D', color=color.new(color.orange, 0))
    h0 = hline(80)
    h1 = hline(20)
    fill(h0, h1, color=color.new(color.purple, 75))
    GoLong = ta.crossover(k, d) and k < 80
    GoShort = ta.crossunder(k, d) and k > 20
    if GoLong:
        strategy.entry('Long', strategy.long)
    strategy.exit('tp_long', from_entry='Long', profit=TP)
    if GoShort:
        strategy.entry('Short', strategy.short)
    strategy.exit('tp_short', from_entry='Short', profit=TP)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
