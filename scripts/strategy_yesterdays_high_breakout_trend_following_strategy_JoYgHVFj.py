"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.series import inline_series
from pynecore.lib import (
    bar_index, barstate, bgcolor, close, color, high, input, low, na, open,
    plot, request, script, strategy, syminfo, ta, time, timeframe
)
from pynecore.types import Persistent, PersistentSeries, Series


@script.strategy('Yesterday\'s High', overlay=True, pyramiding=1, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, slippage=1, backtest_fill_limits_assumption=1, use_bar_magnifier=True, commission_type=strategy.commission.percent, commission_value=0.075, margin_long=0, margin_short=0, close_by_id=True)
def main(
    roc_enable=input.bool(False, '', group='ROC Filter from CloseD', inline='roc'),
    roc_threshold=input.float(1, 'Treshold', step=0.5, group='ROC Filter from CloseD', inline='roc'),
    Gap=input.float(1, 'Gap%', step=0.5, tooltip='Gap di entrata su entry_price -n anticipa entrata, con +n posticipa entrata', group='Entry'),
    sl=input.float(3, 'Stop-loss', step=0.5, group='Entry'),
    tp=input.float(9, 'Take-profit', step=0.5, group='Entry'),
    sl_trl=input.float(2, 'Trailing-stop', step=0.5, tooltip='Attiva trailing stop dopo che ha raggiunto...', group='Trailing Stop Settings'),
    Atrl=input.float(1, 'Offset Trailing', step=0.5, tooltip='Distanza dal prezzo', group='Trailing Stop Settings'),
    ts_n=input.bool(True, 'Trailing-stop', tooltip='Attiva o disattiva trailing-stop', group='Trailing Stop Settings'),
    close_ema=input.bool(False, 'Close EMA', tooltip='Attiva o disattiva chiusura su EMA', group='Trailing Stop Settings'),
    len1=input.int(10, 'EMA length', step=1, group='Trailing Stop Settings')
):
    def f_security(_sym, _res, _src: Series, _rep):
        return inline_series(request.security(_sym, _res, _src[1 if not _rep and barstate.isrealtime else 0]), 0 if _rep or barstate.isrealtime else 1)

    high_daily = f_security(syminfo.tickerid, 'D', high, False)
    closed = f_security(syminfo.tickerid, '1D', close, False)
    roc_filter = (close - closed) / closed * 100 > roc_threshold if roc_enable else True
    open_session = ta.change(time('D'))
    price_session = ta.valuewhen(cast_bool(open_session), open, 0)
    tf_session = timeframe.multiplier <= 60
    bgcolor(color.new(color.blue, 80) if cast_bool(open_session) and tf_session else na, title='Session')
    first_bar: int = 0
    if cast_bool(open_session):
        first_bar = bar_index
    max_today: Persistent[float] = 0.0
    min_today: Persistent[float] = 0.0
    high_daily1: Persistent[float] = 0.0
    low_daily1: Persistent[float] = 0.0
    today_open: PersistentSeries[float] = 0.0
    if cast_bool(first_bar):
        high_daily1 = max_today
        low_daily1 = min_today
        today_open = open
        max_today = high
        min_today = low
    if high >= max_today:
        max_today = high
    if low < min_today:
        min_today = low
    same_day = today_open == today_open[1]
    plot(high_daily1 if timeframe.multiplier <= 240 and same_day else na, color=color.yellow, style=plot.style_linebr, linewidth=1, title='High line')
    plot(low_daily1 if timeframe.multiplier <= 240 and same_day else na, color=color.new('#E8000D'), style=plot.style_linebr, linewidth=1, title='Low line')
    Gap2 = high_daily1 * Gap / 100
    stop_loss_price = strategy.position_avg_price * (1 - sl / 100)
    take_price = strategy.position_avg_price * (1 + tp / 100)
    stop_trl_price_cond = sl_trl * high / syminfo.mintick / 100
    stop_trl_price_offset_cond = Atrl * high / syminfo.mintick / 100
    stop_tick = sl * high / syminfo.mintick / 100
    profit_tick = tp * high / syminfo.mintick / 100
    mess_buy: str = 'buy'
    mess_sell: str = 'sell'
    if close < high_daily1 and roc_filter:
        strategy.entry('Entry', strategy.long, stop=high_daily1 + Gap2, alert_message=mess_buy)
    ma1 = ta.ema(close, len1)
    plot(ma1, title='EMA', color=color.new(color.yellow, 0))
    if ts_n == True:
        strategy.exit('Trailing-Stop', 'Entry', loss=stop_tick + (0.0 if na(stop_loss_price) else na), stop=stop_loss_price, limit=take_price, trail_points=stop_trl_price_cond, trail_offset=stop_trl_price_offset_cond, comment_loss='Stop-Loss!!', comment_profit='CASH!!', comment_trailing='TRL-Stop!!', alert_message=mess_sell)
    else:
        strategy.exit('TP-SL', 'Entry', loss=stop_tick + (0.0 if na(stop_loss_price) else na), stop=stop_loss_price, limit=take_price, comment_loss='Stop-loss!!!', comment_profit='CASH!!', alert_message=mess_sell)
    crossunder_1 = ta.crossunder(close, ma1)
    if close_ema == True and crossunder_1:
        strategy.close('Entry', comment='Close', alert_message=mess_sell)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
