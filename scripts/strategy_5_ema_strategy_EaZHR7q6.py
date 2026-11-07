"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    close, color, high, input, low, math, na, open, plot, script, strategy,
    ta, time
)
from pynecore.types import NA, Persistent, PersistentSeries, Series

group_ma1: str = 'Ema Set'


@script.strategy('5 ema strategy', overlay=True, process_orders_on_close=True, commission_type=strategy.commission.cash_per_contract, commission_value=0.2, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    t_dir=input.string('Both', title='Trade Direction', options=('Long', 'Short', 'Both'), group='Trade Direction Set'),
    mx_num=input.int(4, title='number Of trade', group='Maximum Number Of Trade'),
    on_ma=input.bool(True, 'Enable EMa 1 Plot On/Off', group=group_ma1),
    ma_len=input.int(5, minval=1, title='Ema Length', group=group_ma1),
    ma_src: Series[float] = input.source(close, title='Ema Source', group=group_ma1),
    tpnew=input.float(title='take profit', step=0.1, defval=1.5, group='Tp/SL')
):
    long_side = t_dir == 'Long' or t_dir == 'Both'
    short_side = t_dir == 'Short' or t_dir == 'Both'
    hi: PersistentSeries = NA(float)
    lo: PersistentSeries = NA(float)
    ma_out = ta.ema(ma_src, ma_len)
    plot(ma_out if on_ma else na, color=color.white, title='MA')
    if close > ma_out and open > ma_out and (low > ma_out) and (high > ma_out):
        lo = low
    if close < ma_out and open < ma_out and (low < ma_out) and (high < ma_out):
        hi = high
    buyp_sl: Persistent = NA(float)
    sellp_sl: Persistent = NA(float)
    count_buysell: Persistent[int] = 0
    if high > hi[1]:
        if strategy.position_size == 0 and count_buysell < mx_num and long_side:
            strategy.entry('El', strategy.long, comment='Long')
            count_buysell = count_buysell + 1
            buyp_sl = math.min(low, low[1])
        hi = na
    if low < lo[1]:
        if strategy.position_size == 0 and count_buysell < mx_num and short_side:
            strategy.entry('Es', strategy.short, comment='short')
            count_buysell = count_buysell + 1
            sellp_sl = math.max(high, high[1])
        lo = na
    buy_sl = ta.valuewhen(strategy.position_size != 0 and strategy.position_size[1] == 0, buyp_sl, 0)
    sell_sl = ta.valuewhen(strategy.position_size != 0 and strategy.position_size[1] == 0, sellp_sl, 0)
    takeProfit_buy = strategy.position_avg_price - (buy_sl - strategy.position_avg_price) * tpnew
    takeProfit_sell = strategy.position_avg_price - (sell_sl - strategy.position_avg_price) * tpnew
    if strategy.position_size > 0:
        strategy.exit(id='XL', stop=buy_sl, limit=takeProfit_buy, comment_loss='Long Sl', comment_profit='Long Tp')
    if strategy.position_size < 0:
        strategy.exit(id='XS', stop=sell_sl, limit=takeProfit_sell, comment_loss='Short Sl', comment_profit='Short Tp')
    plot(series=sell_sl if strategy.position_size < 0 else na, style=plot.style_circles, color=color.red, linewidth=2, title='St red Stop')
    plot(series=buy_sl if strategy.position_size > 0 else na, style=plot.style_circles, color=color.green, linewidth=2, title='St green Stop')
    plot(series=takeProfit_sell if strategy.position_size < 0 else na, style=plot.style_circles, color=color.orange, linewidth=2, title='take profit sell')
    plot(series=takeProfit_buy if strategy.position_size > 0 else na, style=plot.style_circles, color=color.blue, linewidth=2, title='take profit buy')
    if cast_bool(ta.change(time('D'))):
        count_buysell = 0


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)