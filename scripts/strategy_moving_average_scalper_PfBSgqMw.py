"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, input, plot, script, strategy, ta, time, timestamp


@script.strategy(shorttitle='Moving Average Scalper (by Coinrule)', title='Moving Average Scalper', overlay=True, initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=30, commission_type=strategy.commission.percent, commission_value=0.1, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
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
    __input_9__=input(200),
    __input_10__=input(100),
    __input_11__=input(2),
    __input_12__=input(8)
):
    start = timestamp(fromYear, fromMonth, fromDay, 0, 0)
    finish = timestamp(thruYear, thruMonth, thruDay, 23, 59)
    def window():
        return True if time >= start and time <= finish else False

    movingaverage_signal = ta.sma(close, __input_7__)
    movingaverage_fast = ta.sma(close, __input_8__)
    movingaverage_slow = ta.sma(close, __input_9__)
    movingaverage_mid = ta.sma(close, __input_10__)
    bullish = ta.crossover(movingaverage_signal, movingaverage_fast)
    window_1 = window()
    if bullish and movingaverage_fast < movingaverage_mid and (movingaverage_mid < movingaverage_slow) and window_1:
        strategy.entry(id='long', direction=strategy.long)
    bearish = ta.crossover(movingaverage_signal, movingaverage_slow)
    Stop_loss = __input_11__ / 100
    Take_profit = __input_12__ / 100
    longStopPrice = strategy.position_avg_price * (1 - Stop_loss)
    longTakeProfit = strategy.position_avg_price * (1 + Take_profit)
    if bearish:
        strategy.close('long')
    plot(movingaverage_signal, color=color.new(color.black, 0), linewidth=2)
    plot(movingaverage_fast, color=color.new(color.orange, 0), linewidth=2)
    plot(movingaverage_slow, color=color.new(color.purple, 0), linewidth=2)
    plot(movingaverage_mid, color=color.new(color.blue, 0), linewidth=2)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
