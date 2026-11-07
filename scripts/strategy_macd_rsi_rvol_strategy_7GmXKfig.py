"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, na, script, strategy, ta, volume


@script.strategy('MACD, RSI, & RVOL Strategy', overlay=True, max_bars_back=5000, default_qty_type=strategy.cash, calc_on_order_fills=False, calc_on_every_tick=False, pyramiding=0, default_qty_value=100000, initial_capital=100000, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    length=input(14),
    overSold=input(30),
    overBought=input(70),
    fastLength=input(12),
    slowlength=input(26),
    MACDLength=input(9),
    RVOLlen=input.int(14, minval=1, title='RVOL Length')
):
    strategy.risk.allow_entry_in(strategy.direction.long)
    price = close
    vrsi = ta.rsi(price, length)
    co = ta.crossover(vrsi, overSold)
    cu = ta.crossunder(vrsi, overBought)
    MACD = ta.ema(close, fastLength) - ta.ema(close, slowlength)
    aMACD = ta.ema(MACD, MACDLength)
    delta = MACD - aMACD
    av = ta.sma(volume, RVOLlen)
    RVOL = volume / av
    if not na(vrsi):
        crossover_1 = ta.crossover(delta, 0)
        crossover_2 = ta.crossover(RVOL, 2)
        crossover_3 = ta.crossover(delta, 0)
        crossover_4 = ta.crossover(RVOL, 2)
        if co and crossover_1 or (co and crossover_2) or (crossover_3 and crossover_4):
            strategy.entry('MACD & RSI BUY Long', strategy.long, comment='BUY LONG')
        crossunder_1 = ta.crossunder(delta, 0)
        crossunder_2 = ta.crossunder(RVOL, 5)
        crossunder_3 = ta.crossunder(delta, 0)
        crossunder_4 = ta.crossunder(RVOL, 5)
        if cu and crossunder_1 or (cu and crossunder_2) or (crossunder_3 and crossunder_4):
            strategy.entry('MACD & RSI SELL Short', strategy.short, comment='SELL LONG')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
