"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, currency, high, hlc3, input, low, plot, script, strategy,
    ta, year
)
from pynecore.types import Series


@script.strategy(title='Fibonacci + RSI - Strategy', overlay=True, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=10000, currency=currency.USD, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    __input_0__=input.float(title='Stop Loss (%)', minval=0.0, step=0.1, defval=2),
    len=input.int(title='[RSI] Length', minval=0, step=1, defval=14),
    overSold=input(title='[RSI] Over Sold %', defval=30),
    overBought=input(title='[RSI] Over Bought %', defval=70),
    length=input.int(title='[Fibonacci] Length', defval=200, minval=1),
    src: Series[float] = input(hlc3, title='[Fibonacci] Source'),
    mult=input.float(title='[Fibonacci] Multiplier', defval=3.0, minval=0.001, maxval=50),
    level=input(title='[Fibonacci] Level', defval=764)
):
    timeFilter = year >= 2000
    loss_percent = __input_0__ * 0.001
    basis = ta.vwma(src, length)
    dev = mult * ta.stdev(src, length)
    fu764 = basis + 0.001 * level * dev
    fu1 = basis + 1 * dev
    fd764 = basis - 0.001 * level * dev
    fd1 = basis - 1 * dev
    vrsi: Series = ta.rsi(close, len)
    targetUp = fd764
    targetDown = fu764
    bought = strategy.position_size > strategy.position_size[1]
    exit_long = ta.valuewhen(bought, targetUp, 0)
    sold = strategy.position_size < strategy.position_size[1]
    exit_short = ta.valuewhen(sold, targetDown, 0)
    stop_long = strategy.position_avg_price * (1 - loss_percent)
    stop_short = strategy.position_avg_price * (1 + loss_percent)
    crossover_1 = ta.crossover(vrsi[1], overSold)
    openLong = low < fd1 and crossover_1
    crossunder_1 = ta.crossunder(vrsi[1], overBought)
    openShort = high > fu1 and crossunder_1
    closeLong = high > exit_long
    closeShort = low < exit_short
    plot(basis, color=color.new(color.blue, 0), linewidth=2, title='[Fibonacci Level] Basis')
    plot(fu764, color=color.new(color.white, 0), linewidth=1, title='[Fibonacci Level] Short Target')
    plot(fu1, color=color.new(color.red, 0), linewidth=2, title='[Fibonacci Level] Top')
    plot(fd764, color=color.new(color.white, 0), linewidth=1, title='[Fibonacci Level] Long Target')
    plot(fd1, color=color.new(color.green, 0), linewidth=2, title='[Fibonacci Level] Bottom')
    if timeFilter:
        if openLong and high < targetUp:
            strategy.entry(id='Long', direction=strategy.long, limit=close)
        if openShort and low > targetDown:
            strategy.entry(id='Short', direction=strategy.short, limit=close)
        if closeLong and strategy.position_size > 0:
            strategy.exit(id='Long', limit=exit_long, stop=stop_long)
        if closeShort and strategy.position_size < 0:
            strategy.exit(id='Short', limit=exit_short, stop=stop_short)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
