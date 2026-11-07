"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import alert, close, input, na, script, strategy, ta


@script.strategy('RSI Strategy with alerts via TradingConnector to Forex', overlay=True, default_qty_value=100000, margin_long=0, margin_short=0, initial_capital=100000, default_qty_type=strategy.fixed, close_by_id=True, na_bool=True)
def main(
    length=input(14),
    overSold=input(30),
    overBought=input(70)
):
    price = close
    vrsi = ta.rsi(price, length)
    co = ta.crossover(vrsi, overSold)
    cu = ta.crossunder(vrsi, overBought)
    if not na(vrsi):
        if co:
            strategy.entry('RsiLE', strategy.long, comment='RsiLE')
            alert(message='long', freq=alert.freq_once_per_bar_close)
        if cu:
            strategy.entry('RsiSE', strategy.short, comment='RsiSE')
            alert(message='short', freq=alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
