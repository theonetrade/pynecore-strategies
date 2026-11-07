"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, high, input, low, plot, script, strategy, ta


@script.strategy(title='Stochastic Trend', overlay=False, pyramiding=1, commission_value=0.2, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, initial_capital=100000, close_by_id=True, na_bool=True)
def main(
    periodK=input.int(200, title='K', minval=1, step=10),
    periodD=input.int(3, title='D', minval=1),
    smoothK=input.int(100, title='Smooth', minval=1, step=10),
    Enter=input(50),
    Exit=input(60)
):
    k = ta.sma(ta.stoch(close, high, low, periodK), smoothK)
    d = ta.sma(k, periodD)
    plot(k, title='%K', color=color.new(color.blue, 0))
    plot(d, title='%D', color=color.new(color.blue, 0))
    plot(Enter, 'Upper Band', color=color.new(color.green, 0))
    plot(Exit, 'Lower Band', color=color.new(color.red, 0))
    long = ta.crossover(k, Enter)
    longclose = ta.crossunder(k, Exit)
    LongAlert: str = 'LONG'
    CloseAlert: str = 'Close Position'
    if long:
        strategy.entry('long', strategy.long, alert_message=LongAlert)
    if longclose:
        strategy.close('long', alert_message=CloseAlert)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
