"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import alert, close, high, input, low, math, script, strategy, ta
from pynecore.types import Persistent


@script.strategy(title='ATR_RSI_Strategy v2[liwei666]', shorttitle='ATR_RSI_Strategy', overlay=True, max_lines_count=500, max_labels_count=500, max_boxes_count=500, max_bars_back=5000, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, pyramiding=1, commission_value=0.05, margin_long=0, margin_short=0, close_by_id=True)
def main(
    atr_length=input.int(26, 'atr_length', minval=6, maxval=100, step=1),
    atr_ma_length=input.int(45, 'atr_ma_length', minval=6, maxval=100, step=1),
    rsi_length=input.int(15, 'rsi_length', minval=6, maxval=100, step=1),
    rsi_entry=input.int(10, 'rsi_entry', minval=6, maxval=100, step=1),
    atr_ma_norm_min=input.float(0.3, 'atr_ma_norm_min', minval=0.1, maxval=0.5, step=0.1),
    atr_ma_norm_max=input.float(0.7, 'atr_ma_norm_max', minval=0.5, maxval=1, step=0.1),
    trailing_percent=input.float(1.5, 'trailing_stop_percent', minval=0.1, maxval=2, step=0.1)
):
    rsi_buy: Persistent = 50 + rsi_entry
    rsi_sell: Persistent = 50 - rsi_entry
    def sma_norm_h_45():
        source = high
        n: int = 45
        sma = ta.sma(source, n)
        sma_norm = (sma - ta.lowest(sma, n)) / (ta.highest(sma, n) - ta.lowest(sma, n))
        return sma_norm

    atr_value = ta.atr(atr_length)
    atr_ma = ta.sma(atr_value, atr_ma_length)
    rsi_value = ta.rsi(close, length=rsi_length)
    atr_ma_norm = atr_ma / close * 100
    sma_norm = sma_norm_h_45()
    intra_trade_high: Persistent[float] = 0.0
    intra_trade_low: Persistent[float] = 0.0
    long_sl: Persistent[float] = 0.0
    long_tp: Persistent[float] = 0.0
    short_sl: Persistent[float] = 0.0
    short_tp: Persistent[float] = 0.0
    if strategy.position_size == 0:
        intra_trade_high = high
        intra_trade_low = low
        if atr_ma_norm >= atr_ma_norm_min and atr_ma_norm <= atr_ma_norm_max:
            if atr_value > atr_ma:
                if rsi_value > rsi_buy:
                    strategy.entry('B1', strategy.long, limit=close + 5)
                    alert('Long B1', alert.freq_once_per_bar_close)
                elif rsi_value < rsi_sell:
                    strategy.entry('S1', strategy.short, limit=close - 5)
                    alert('Short S1', alert.freq_once_per_bar_close)
    elif strategy.position_size > 0:
        intra_trade_high = math.max(intra_trade_high, high)
        intra_trade_low = low
        long_sl = intra_trade_high * (1 - trailing_percent / 100)
        long_tp = strategy.position_avg_price * 1.03
        strategy.exit('Exit B1', from_entry='B1', stop=long_sl, limit=long_tp)
    elif strategy.position_size < 0:
        intra_trade_high = high
        intra_trade_low = math.min(intra_trade_low, low)
        short_sl = intra_trade_low * (1 + trailing_percent / 100)
        short_tp = strategy.position_avg_price * 0.94
        strategy.exit('Exit S1', from_entry='S1', stop=short_sl, limit=short_tp)
    if strategy.position_size > 0 and low < long_sl:
        alert('B1 Stop_loss', alert.freq_once_per_bar)
    elif strategy.position_size > 0 and high > long_tp:
        alert('B1 Take_profit', alert.freq_once_per_bar)
    if strategy.position_size < 0 and high > short_sl:
        alert('S1 Stop_loss', alert.freq_once_per_bar)
    elif strategy.position_size > 0 and low < short_tp:
        alert('S1 Take_profit', alert.freq_once_per_bar)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)