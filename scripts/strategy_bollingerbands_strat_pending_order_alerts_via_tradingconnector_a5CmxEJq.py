"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import alert, close, input, script, strategy, string, ta


@script.strategy('Bollinger Bands Strategy with alerts (incl. pending orders) via TradingConnector to Forex', overlay=True, default_qty_value=1000, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, close_by_id=True)
def main(
    length=input.int(20, minval=1),
    mult=input.float(2.0, minval=0.001, maxval=50)
):
    source = close
    basis = ta.sma(source, length)
    dev = mult * ta.stdev(source, length)
    upper = basis + dev
    lower = basis - dev
    buyEntry = ta.crossover(source, lower)
    sellEntry = ta.crossunder(source, upper)
    if ta.crossover(source, lower):
        strategy.entry('BBandLE', strategy.long, stop=lower, oca_name='BollingerBands', oca_type=strategy.oca.cancel, comment='BBandLE')
        alert(message='long price=' + string.tostring(lower), freq=alert.freq_once_per_bar_close)
    else:
        strategy.cancel(id='BBandLE')
        alert(message='cancel long', freq=alert.freq_once_per_bar_close)
    if ta.crossunder(source, upper):
        strategy.entry('BBandSE', strategy.short, stop=upper, oca_name='BollingerBands', oca_type=strategy.oca.cancel, comment='BBandSE')
        alert(message='short price=' + string.tostring(upper), freq=alert.freq_once_per_bar_close)
    else:
        strategy.cancel(id='BBandSE')
        alert(message='cancel short', freq=alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
