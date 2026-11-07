"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, plot, script, strategy, ta
from pynecore.types import Series


@script.strategy('State-aware MA Cross Strategy', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, initial_capital=1000000, close_by_id=True)
def main():
    s00_short = ta.ema(close, 15)
    s00_long = ta.hma(close, 24)
    s01_short = ta.sma(close, 19)
    s01_long = ta.rma(close, 45)
    s10_short = ta.rma(close, 16)
    s10_long = ta.hma(close, 59)
    s11_short = ta.rma(close, 12)
    s11_long = ta.rma(close, 36)
    base_ma: Series = ta.ema(close, 20)
    ma_slope = base_ma - base_ma[1]
    above_ma = close > base_ma
    slope_up = ma_slope > 0
    state = ('11' if above_ma else '10') if slope_up else '01' if above_ma else '00'
    short_ma = s00_short if state == '00' else s01_short if state == '01' else s10_short if state == '10' else s11_short
    long_ma = s00_long if state == '00' else s01_long if state == '01' else s10_long if state == '10' else s11_long
    long_signal = ta.crossover(short_ma, long_ma)
    short_signal = ta.crossunder(short_ma, long_ma)
    if long_signal:
        strategy.entry('Long', strategy.long)
    if short_signal:
        strategy.close_all()
    plot(short_ma, color=color.green, title='Short MA')
    plot(long_ma, color=color.red, title='Long MA')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
