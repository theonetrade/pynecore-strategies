"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import color, high, hl2, hline, input, low, math, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy('scalping against trapped countertrend', overlay=False, precision=5, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    x_src: Series[float] = input(hl2, title='Source'),
    x_len_a=input.int(5, title='short term trend', minval=1),
    x_len_b=input.int(60, title='long term trend', minval=1),
    x_k_b=input.int(13, title='smooth long term trend', minval=1),
    x_changk=input.int(15, title='clear short term pullback appears recently', minval=1),
    x_rsi_ct=input.float(35.0, title='threshold of short term pullback clear', minval=0.0, maxval=100.0),
    x_rsi_ft=input.float(50.0, title='threshold of short term pullback end', minval=0.0, maxval=100.0),
    x_exit_if_reason_over=input(False)
):
    y_stoch = ta.stoch(x_src, high, low, x_len_b)
    y_k = ta.sma(y_stoch, x_k_b)
    y_rsi = ta.rsi(x_src, x_len_a)
    y_upper = math.min(y_k - 50, y_rsi - x_rsi_ft, x_rsi_ct - ta.lowest(y_rsi, x_changk) if x_changk > 1 else 50)
    if y_upper > 0:
        strategy.entry('LE', strategy.long)
    elif x_exit_if_reason_over and strategy.position_size > 0:
        strategy.close('LE', comment='x')
    y_lower = math.max(y_k - 50, y_rsi - x_rsi_ft, 100 - x_rsi_ct - ta.highest(y_rsi, x_changk) if x_changk > 1 else -50)
    if y_lower < 0:
        strategy.entry('SE', strategy.short)
    elif x_exit_if_reason_over and strategy.position_size < 0:
        strategy.close('SE', comment='x')
    plot(y_stoch, color=color.new(color.new('#FF3333'), 0))
    plot(y_k, color=color.new(color.new('#6666FF'), 0))
    plot(y_rsi, color=color.new(color.new('#CCCC00'), 0))
    hline(50)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
