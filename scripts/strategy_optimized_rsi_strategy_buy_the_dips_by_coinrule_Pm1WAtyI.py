"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, input, plot, script, strategy, ta, time, timestamp


@script.strategy(shorttitle='Optimized RSI Strategy', title='Optimized RSI Strategy - Buy The Dips (by Coinrule)', overlay=True, initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=30, commission_type=strategy.commission.percent, commission_value=0.1, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    fromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    fromDay=input.int(defval=1, title='From Day', minval=1, maxval=31),
    fromYear=input.int(defval=2020, title='From Year', minval=1970),
    thruMonth=input.int(defval=1, title='Thru Month', minval=1, maxval=12),
    thruDay=input.int(defval=1, title='Thru Day', minval=1, maxval=31),
    thruYear=input.int(defval=2112, title='Thru Year', minval=1970),
    showDate=input(defval=True, title='Show Date Range'),
    RSI_entry=input.int(35, title='RSI Entry', minval=1),
    RSI_exit=input.int(65, title='RSI Close', minval=1),
    __input_9__=input(100)
):
    start = timestamp(fromYear, fromMonth, fromDay, 0, 0)
    finish = timestamp(thruYear, thruMonth, thruDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    lengthRSI: int = 14
    RSI = ta.rsi(close, lengthRSI)
    movingaverage_signal = ta.sma(close, __input_9__)
    window_1 = window()
    if RSI < RSI_entry and close < movingaverage_signal and window_1:
        strategy.entry(id='long', direction=strategy.long)
    window_2 = window()
    if RSI > RSI_exit and window_2:
        strategy.close('long')
    plot(movingaverage_signal)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
