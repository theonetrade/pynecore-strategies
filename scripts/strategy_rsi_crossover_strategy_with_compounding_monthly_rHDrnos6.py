"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, math, plot, request, script, strategy, syminfo, ta
from pynecore.types import Persistent


@script.strategy('RSI Crossover Strategy with Compounding (Monthly)', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main():
    initialCapital: Persistent[float] = 100000
    capital: Persistent[float] = initialCapital
    investedCapital: Persistent[float] = 0.0
    rsiLength: int = 14
    rsiMonthly = request.security(syminfo.tickerid, 'M', ta.rsi(close, rsiLength))
    rsiSmaMonthly = request.security(syminfo.tickerid, 'M', ta.sma(rsiMonthly, rsiLength))
    rsiMonthlyHigher = rsiMonthly > rsiSmaMonthly
    rsiMonthlyLower = rsiMonthly < rsiSmaMonthly
    maxQuantity = math.floor(capital / close) if capital > 0 else 0
    if rsiMonthlyHigher and strategy.position_size == 0 and (maxQuantity > 0):
        strategy.entry('Long', strategy.long, qty=maxQuantity)
        investedCapital = maxQuantity * close
    if rsiMonthlyLower and strategy.position_size > 0:
        strategy.close('Long')
        capital = capital + strategy.netprofit
        investedCapital = 0.0
    plot(rsiMonthly, color=color.blue, title='RSI (Monthly)')
    plot(rsiSmaMonthly, color=color.red, title='RSI SMA (Monthly)')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
