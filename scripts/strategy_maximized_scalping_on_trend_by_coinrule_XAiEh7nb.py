"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta, time, timestamp


@script.strategy(shorttitle='Maximized Scalping On Trend', title='Maximized Scalping On Trend (by Coinrule)', overlay=True, initial_capital=1000, process_orders_on_close=True, default_qty_type=strategy.percent_of_equity, default_qty_value=30, commission_type=strategy.commission.percent, commission_value=0.1, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    fromMonth=input.int(defval=1, title='From Month', minval=1, maxval=12),
    fromDay=input.int(defval=10, title='From Day', minval=1, maxval=31),
    fromYear=input.int(defval=2019, title='From Year', minval=1970),
    thruMonth=input.int(defval=1, title='Thru Month', minval=1, maxval=12),
    thruDay=input.int(defval=1, title='Thru Day', minval=1, maxval=31),
    thruYear=input.int(defval=2112, title='Thru Year', minval=1970),
    showDate=input(defval=True, title='Show Date Range'),
    __input_7__=input(9),
    __input_8__=input(50),
    __input_9__=input(100),
    TP=input(70),
    SL=input(30)
):
    start = timestamp(fromYear, fromMonth, fromDay, 0, 0)
    finish = timestamp(thruYear, thruMonth, thruDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    movingaverage_fast = ta.sma(close, __input_7__)
    movingaverage_mid = ta.sma(close, __input_8__)
    movingaverage_slow = ta.sma(close, __input_9__)
    Bullish = ta.crossunder(close, movingaverage_fast)
    Momentum = movingaverage_mid > movingaverage_slow
    lengthRSI: int = 14
    RSI = ta.rsi(close, lengthRSI)
    window_1 = window()
    if Bullish and Momentum and (RSI > 50) and window_1:
        strategy.entry(id='long', direction=strategy.long)
    longTakeProfit = RSI > TP
    longStopPrice = RSI < SL
    window_2 = window()
    if longStopPrice or (longTakeProfit and window_2):
        strategy.close('long')
    plot(movingaverage_fast, color=color.new(color.black, 0), linewidth=2)
    plot(movingaverage_mid, color=color.new(color.orange, 0), linewidth=2)
    plot(movingaverage_slow, color=color.new(color.purple, 0), linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
