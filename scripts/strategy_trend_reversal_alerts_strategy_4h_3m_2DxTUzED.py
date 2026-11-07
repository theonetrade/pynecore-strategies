"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, high, input, low, open, plot, script, strategy


@script.strategy(title='Trend Reversal Alerts Strategy PRO by @nocachy', shorttitle='T-RAS-PRO', overlay=False)
def main(
    delta=input.float(title='Delta', minval=0.01, maxval=1, step=0.01, defval=1),
    buyResistance=input.float(title='Buy Resistance', minval=0, maxval=10, step=0.01, defval=0),
    sellResistance=input.float(title='Sell Resistance', minval=-10, maxval=10, step=0.01, defval=0)
):
    topSource = close if close > open else open
    bottomSource = close if close < open else open
    body = high - low
    spirit = topSource - bottomSource
    resistance = -(body / spirit) if open > close else body / spirit
    buy_signal = close[1] * delta > close[2] and close * delta > close[1] and (resistance > buyResistance)
    sell_signal = close[1] * (2 - delta) < close[2] and close * (2 - delta) < close[1] and (resistance < sellResistance)
    if buy_signal:
        strategy.entry('buy', strategy.long)
    if sell_signal:
        strategy.close('buy')
    plot(strategy.position_size)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
