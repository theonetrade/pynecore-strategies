"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, math, nz, plot, script, strategy, ta, volume
from pynecore.types import Series


@script.strategy('EVWMA VWAP Cross [QuantNomad]', shorttitle='EVWMA_VWAP_Cross[QN]', overlay=True, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    sum_length=input(30, title='EVWMA Length'),
    vwap_smoothing=input(1, title='VWAP Smoothing')
):
    vol_period = math.sum(volume, sum_length)
    evwma: Series[float] = 0.0
    evwma = ((vol_period - volume) * nz(evwma[1], close) + volume * close) / vol_period
    vwap_smooth = ta.ema(ta.vwap, vwap_smoothing)
    long = ta.crossover(vwap_smooth, evwma)
    short = ta.crossunder(vwap_smooth, evwma)
    plot(evwma, color=color.new(color.blue, 0))
    plot(vwap_smooth, color=color.new(color.red, 0))
    if long:
        strategy.entry('Long', strategy.long)
    if short:
        strategy.entry('Short', strategy.short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
