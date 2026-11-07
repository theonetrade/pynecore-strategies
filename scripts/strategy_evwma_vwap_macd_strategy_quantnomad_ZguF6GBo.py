"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, math, nz, plot, script, strategy, ta, volume
from pynecore.types import Series


@script.strategy('EVWMA VWAP MACD Strategy [QuantNomad]', shorttitle='EVWMA_VWAP_MACD[QN]', overlay=False, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    sum_length=input(30, title='EVWMA Length'),
    signal_length1=input(5, title='Signal Smoothing 1'),
    signal_length2=input(20, title='Signal Smoothing 2')
):
    vol_period = math.sum(volume, sum_length)
    evwma: Series[float] = 0.0
    evwma = ((vol_period - volume) * nz(evwma[1], close) + volume * close) / vol_period
    diff = ta.vwap - evwma
    macd = ta.ema(diff, signal_length1)
    signal = ta.ema(diff, signal_length2)
    hist: Series = macd - signal
    plot(hist, title='Histogram', style=plot.style_columns, color=(color.new('#26A69A') if hist[1] < hist else color.new('#B2DFDB')) if hist >= 0 else color.new('#FFCDD2') if hist[1] < hist else color.new('#EF5350'))
    plot(macd, title='MACD', color=color.new(color.new('#0094FF'), 0))
    plot(signal, title='Signal', color=color.new(color.new('#FF6A00'), 0))
    if ta.crossunder(macd, signal):
        strategy.entry('short', strategy.short)
    if ta.crossover(macd, signal):
        strategy.entry('long', strategy.long)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
