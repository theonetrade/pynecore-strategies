"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import close, color, currency, high, input, low, math, plot, script, strategy, ta


@script.strategy('SuperATR 7-Step Profit - Strategy [presentTrading] ', overlay=True, precision=3, commission_value=0.1, commission_type=strategy.commission.percent, slippage=1, currency=currency.USD, default_qty_type=strategy.percent_of_equity, default_qty_value=10, initial_capital=10000, margin_long=0, margin_short=0, close_by_id=True)
def main(
    short_period=input.int(3, minval=1, title='Short Period'),
    long_period=input.int(7, minval=1, title='Long Period'),
    momentum_period=input.int(7, minval=1, title='Momentum Period'),
    atr_sma_period=input.int(7, minval=1, title='ATR SMA Period for Confirmation'),
    trend_strength_threshold=input.float(1.618, minval=0.0, title='Trend Strength Threshold', step=0.1),
    useMultiStepTP=input.bool(True, title='Enable Multi-Step Take Profit'),
    atrLengthTP=input.int(14, minval=1, title='ATR Length for Take Profit'),
    atrMultiplierTP1=input.float(2.618, minval=0.1, title='ATR Multiplier for TP Level 1'),
    atrMultiplierTP2=input.float(5.0, minval=0.1, title='ATR Multiplier for TP Level 2'),
    atrMultiplierTP3=input.float(10.0, minval=0.1, title='ATR Multiplier for TP Level 3'),
    atrMultiplierTP4=input.float(13.82, minval=0.1, title='ATR Multiplier for TP Level 4'),
    tp_level_percent1=input.float(3.0, minval=0.1, title='Fixed TP Level 1 (%)'),
    tp_level_percent2=input.float(8.0, minval=0.1, title='Fixed TP Level 2 (%)'),
    tp_level_percent3=input.float(17.0, minval=0.1, title='Fixed TP Level 3 (%)'),
    tp_percent_atr=input.float(10.0, minval=0.1, maxval=100, title='Percentage to Exit at Each ATR TP Level'),
    tp_percent_fixed=input.float(10.0, minval=0.1, maxval=100, title='Percentage to Exit at Each Fixed TP Level')
):
    def calculate_true_range():
        prev_close = close[1]
        tr1 = high - low
        tr2 = math.abs(high - prev_close)
        tr3 = math.abs(low - prev_close)
        true_range = math.max(tr1, tr2, tr3)
        return true_range

    true_range = calculate_true_range()
    momentum = close - close[momentum_period]
    stdev_close = ta.stdev(close, momentum_period)
    normalized_momentum = momentum / stdev_close if stdev_close != 0 else 0
    momentum_factor = math.abs(normalized_momentum)
    short_atr = ta.sma(true_range, short_period)
    long_atr = ta.sma(true_range, long_period)
    adaptive_atr = (short_atr * momentum_factor + long_atr) / (1 + momentum_factor)
    price_change = close - close[momentum_period]
    atr_multiple = price_change / adaptive_atr if adaptive_atr != 0 else 0
    trend_strength = ta.sma(atr_multiple, momentum_period)
    short_ma = ta.sma(close, short_period)
    long_ma = ta.sma(close, long_period)
    trend_signal = 1 if short_ma > long_ma and trend_strength > trend_strength_threshold else -1 if short_ma < long_ma and trend_strength < -trend_strength_threshold else 0
    adaptive_atr_sma = ta.sma(adaptive_atr, atr_sma_period)
    trend_confirmed = trend_signal == 1 and close > short_ma and (adaptive_atr > adaptive_atr_sma) or (trend_signal == -1 and close < short_ma and (adaptive_atr > adaptive_atr_sma))
    long_entry = trend_confirmed and trend_signal == 1
    short_entry = trend_confirmed and trend_signal == -1
    long_exit = strategy.position_size > 0 and short_entry
    short_exit = strategy.position_size < 0 and long_entry
    if long_entry:
        strategy.entry('Long Entry', strategy.long)
    if long_exit:
        strategy.close('Long Entry')
    if short_entry:
        strategy.entry('Short Entry', strategy.short)
    if short_exit:
        strategy.close('Short Entry')
    if useMultiStepTP:
        atrValueTP = ta.atr(atrLengthTP)
        if strategy.position_size > 0:
            tp_priceATR1_long = strategy.position_avg_price + atrMultiplierTP1 * atrValueTP
            tp_priceATR2_long = strategy.position_avg_price + atrMultiplierTP2 * atrValueTP
            tp_priceATR3_long = strategy.position_avg_price + atrMultiplierTP3 * atrValueTP
            tp_priceATR4_long = strategy.position_avg_price + atrMultiplierTP4 * atrValueTP
            tp_pricePercent1_long = strategy.position_avg_price * (1 + tp_level_percent1 / 100)
            tp_pricePercent2_long = strategy.position_avg_price * (1 + tp_level_percent2 / 100)
            tp_pricePercent3_long = strategy.position_avg_price * (1 + tp_level_percent3 / 100)
            strategy.exit('TP ATR 1 Long', from_entry='Long Entry', qty_percent=tp_percent_atr, limit=tp_priceATR1_long)
            strategy.exit('TP ATR 2 Long', from_entry='Long Entry', qty_percent=tp_percent_atr, limit=tp_priceATR2_long)
            strategy.exit('TP ATR 3 Long', from_entry='Long Entry', qty_percent=tp_percent_atr, limit=tp_priceATR3_long)
            strategy.exit('TP ATR 4 Long', from_entry='Long Entry', qty_percent=tp_percent_atr, limit=tp_priceATR4_long)
            strategy.exit('TP Percent 1 Long', from_entry='Long Entry', qty_percent=tp_percent_fixed, limit=tp_pricePercent1_long)
            strategy.exit('TP Percent 2 Long', from_entry='Long Entry', qty_percent=tp_percent_fixed, limit=tp_pricePercent2_long)
            strategy.exit('TP Percent 3 Long', from_entry='Long Entry', qty_percent=tp_percent_fixed, limit=tp_pricePercent3_long)
        if strategy.position_size < 0:
            tp_priceATR1_short = strategy.position_avg_price - atrMultiplierTP1 * atrValueTP
            tp_priceATR2_short = strategy.position_avg_price - atrMultiplierTP2 * atrValueTP
            tp_priceATR3_short = strategy.position_avg_price - atrMultiplierTP3 * atrValueTP
            tp_priceATR4_short = strategy.position_avg_price - atrMultiplierTP4 * atrValueTP
            tp_pricePercent1_short = strategy.position_avg_price * (1 - tp_level_percent1 / 100)
            tp_pricePercent2_short = strategy.position_avg_price * (1 - tp_level_percent2 / 100)
            tp_pricePercent3_short = strategy.position_avg_price * (1 - tp_level_percent3 / 100)
            strategy.exit('TP ATR 1 Short', from_entry='Short Entry', qty_percent=tp_percent_atr, limit=tp_priceATR1_short)
            strategy.exit('TP ATR 2 Short', from_entry='Short Entry', qty_percent=tp_percent_atr, limit=tp_priceATR2_short)
            strategy.exit('TP ATR 3 Short', from_entry='Short Entry', qty_percent=tp_percent_atr, limit=tp_priceATR3_short)
            strategy.exit('TP ATR 4 Short', from_entry='Short Entry', qty_percent=tp_percent_atr, limit=tp_priceATR4_short)
            strategy.exit('TP Percent 1 Short', from_entry='Short Entry', qty_percent=tp_percent_fixed, limit=tp_pricePercent1_short)
            strategy.exit('TP Percent 2 Short', from_entry='Short Entry', qty_percent=tp_percent_fixed, limit=tp_pricePercent2_short)
            strategy.exit('TP Percent 3 Short', from_entry='Short Entry', qty_percent=tp_percent_fixed, limit=tp_pricePercent3_short)
    plot(short_ma, color=color.blue, title='Short MA')
    plot(long_ma, color=color.orange, title='Long MA')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
