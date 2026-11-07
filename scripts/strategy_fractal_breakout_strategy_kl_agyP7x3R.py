"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool, cast_float
from pynecore.lib import (
    alert, close, color, high, input, low, math, plot, script, strategy,
    string, syminfo, ta, time, timestamp, volume
)
from pynecore.types import Persistent, Series

GROUP_ENTRY: str = 'Entry'
GROUP_TSL: str = 'Stop loss'
GROUP_ORDER: str = 'Order size and Profit taking'


@script.strategy('Fractal Strat [KL] ', overlay=True, pyramiding=1, initial_capital=1000000000, default_qty_type=strategy.percent_of_equity, default_qty_value=5, margin_long=0, margin_short=0, close_by_id=True)
def main(
    backtest_timeframe_start=input.time(defval=timestamp('01 Apr 2000 13:30 +0000'), title='Backtest Start Time'),
    _multiple=input(2.0, title='ATR Multiplier for trailing stop loss', group=GROUP_TSL),
    __input_2__=input(14, title='Length of ATR for trailing stop loss', group=GROUP_TSL, tooltip='Initial risk amount = atr(this length) x multiplier'),
    tp_mode__input=input(True, title='Take profit and different levels', group=GROUP_ORDER),
    FIRST_LVL_PROFIT__input=input.float(1, title='First level profit', tooltip='Relative to risk. Example: entry at $10 and inital stop loss at $9. Taking first level profit at 1R means taking profits at $11', group=GROUP_ORDER),
    SECOND_LVL_PROFIT__input=input.float(2, title='Second level profit', tooltip='Relative to risk. Example: entry at $10 and inital stop loss at $9. Taking second level profit at 2R means taking profits at $12', group=GROUP_ORDER),
    THIRD_LVL_PROFIT__input=input.float(3, title='Third level profit', tooltip='Relative to risk. Example: entry at $10 and inital stop loss at $9. Taking third level profit at 3R means taking profits at $13', group=GROUP_ORDER),
    len_fast=input(5, title='Length of ATR (fast) for diversion test', group=GROUP_ENTRY),
    __input_8__=input(50, title='Length of ATR (slow) for diversion test', group=GROUP_ENTRY, tooltip='This needs to be larger than Fast'),
    conf_interval=input.string(title='Confidence Interval', defval='95%', options=('90%', '95%', '99%'), tooltip='Critical values of 1.645, 1.96, 2.58, for CI=90%/95%/99%, respectively; Under 2-tailed test to compare atr_fast vs atr_slow. Null hypothesis (H0) is that both should equal. Based on the computed test statistic value, if absolute value of it is +/- critical value, then H0 will be rejected.')
):
    ENUM_LONG: Persistent[str] = 'Long'
    within_timeframe = time >= backtest_timeframe_start
    ATR_TSL = ta.atr(__input_2__) * _multiple
    TSL_source = low
    TSL_line_color = color.green
    TSL_transp: int = 100
    stop_loss_price: Persistent = cast_float(0)
    initial_entry_p: Persistent[float] = cast_float(0)
    risk_amt: Persistent[float] = cast_float(0)
    initial_order_size: Persistent[float] = cast_float(0)
    if strategy.position_size == 0 or not within_timeframe:
        TSL_line_color = color.black
        stop_loss_price = TSL_source - ATR_TSL
    elif strategy.position_size > 0:
        stop_loss_price = math.max(stop_loss_price, TSL_source - ATR_TSL)
        TSL_transp = 0
    plot(stop_loss_price, color=color.new(TSL_line_color, TSL_transp))
    tp_mode: Persistent[bool] = tp_mode__input
    FIRST_LVL_PROFIT: Persistent[float] = FIRST_LVL_PROFIT__input
    SECOND_LVL_PROFIT: Persistent[float] = SECOND_LVL_PROFIT__input
    THIRD_LVL_PROFIT: Persistent[float] = THIRD_LVL_PROFIT__input
    rel_vol_len: int = 6
    rel_vol: Series = ta.sma(volume, rel_vol_len)
    _up = high[3] > high[4] and high[4] > high[5] and (high[2] < high[3]) and (high[1] < high[2]) and (volume[3] > rel_vol[3])
    _down = low[3] < low[4] and low[4] < low[5] and (low[2] > low[3]) and (low[1] > low[2]) and (volume[3] > rel_vol[3])
    fractal_resistance: Series = high[3]
    fractal_support: Series = low[3]
    fractal_resistance = high[3] if _up else fractal_resistance[1]
    fractal_support = low[3] if _down else fractal_support[1]
    plot(fractal_resistance, 'fractal_resistance', color=color.new(color.red, 50), linewidth=2, style=plot.style_cross, offset=-3, join=False)
    plot(fractal_support, 'fractal_support', color=color.new(color.lime, 50), linewidth=2, style=plot.style_cross, offset=-3, join=False)
    atr_fast = ta.atr(len_fast)
    atr_slow = ta.atr(__input_8__)
    std_error = ta.stdev(ta.tr, len_fast) / math.pow(len_fast, 0.5)
    test_stat = (atr_fast - atr_slow) / std_error
    critical_value = 1.645 if conf_interval == '90%' else 1.96 if conf_interval == '95%' else 2.58
    reject_H0_lefttail = test_stat < -critical_value
    reject_H0_righttail = test_stat > critical_value
    entry_signal_long = close >= fractal_support and reject_H0_lefttail
    if strategy.position_size > 0:
        strategy.exit(ENUM_LONG, comment='SL', stop=stop_loss_price)
    if within_timeframe and entry_signal_long and (strategy.position_size == 0):
        initial_entry_p = close
        risk_amt = ATR_TSL
        strategy.entry(ENUM_LONG, strategy.long)
    TP_taken_count: Persistent[int] = 0
    if tp_mode and close > strategy.position_avg_price:
        if close >= initial_entry_p + THIRD_LVL_PROFIT * risk_amt and TP_taken_count == 2:
            strategy.close(ENUM_LONG, comment='TP Lvl3', qty=math.floor(strategy.position_size / 3))
            TP_taken_count = TP_taken_count + 1
        elif close >= initial_entry_p + SECOND_LVL_PROFIT * risk_amt and TP_taken_count == 1:
            strategy.close(ENUM_LONG, comment='TP Lvl2', qty=math.floor(strategy.position_size / 3))
            TP_taken_count = TP_taken_count + 1
        elif close >= initial_entry_p + FIRST_LVL_PROFIT * risk_amt and TP_taken_count == 0:
            strategy.close(ENUM_LONG, comment='TP Lvl1', qty=math.floor(strategy.position_size / 3))
            TP_taken_count = TP_taken_count + 1
    _atr = ta.atr(14)
    def alert_helper(msg):
        prefix = '[' + syminfo.root + '] '
        suffix = '(P=' + string.tostring(close, '#.##') + '; atr=' + string.tostring(_atr, '#.##') + ')'
        return alert(string.tostring(prefix) + string.tostring(msg) + string.tostring(suffix), alert.freq_once_per_bar)

    change_1 = ta.change(strategy.position_size)
    if strategy.position_size > 0 and cast_bool(change_1):
        if strategy.position_size > strategy.position_size[1]:
            alert_helper('BUY')
        elif strategy.position_size < strategy.position_size[1]:
            alert_helper('SELL')
    if cast_bool(ta.change(strategy.position_size)) and strategy.position_size == 0:
        TP_taken_count = 0
        initial_entry_p = cast_float(0)
        risk_amt = cast_float(0)
        initial_order_size = cast_float(0)
        stop_loss_price = cast_float(0)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
