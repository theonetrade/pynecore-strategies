"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    bar_index, barcolor, barstate, chart, close, color, high, hl2, hlc3,
    hlcc4, input, location, low, na, ohlc4, open, plot, plotshape, position, script, shape,
    strategy, string, ta, table, time, timenow, timestamp
)
from pynecore.types import Persistent, Series, Table

tt_l: str = 'If you don\'t have any long conditions, deactivate this parameter.'
tt_s: str = 'If you don\'t have any short conditions, deactivate this parameter.'
tt_0: str = 'To test your own system, you must enter your conditions as a series of integers (1 or 0). ' + 'In this context, 1 represents true and 0 represents false for each condition. ' + 'You can obtain the inputs from another indicator by utilizing those parameters. ' + "For more detailed information, please refer to the description of the 'Backtesting Module'."
gr_l: str = 'ENTER YOUR LONG CONDITIONS'
gr_s: str = 'ENTER YOUR SHORT CONDITIONS'
grc: str = 'CONFIGURATION'
tt1: str = 'Enter your time zone\'s offset.\nE.g. GMT+3 for Istanbul'
start_ts = timestamp('01 Jan 1980 03:00')
end_ts = timestamp('31 Dec 2050 03:00')
grt: str = 'TABLE SETTINGS'


@script.strategy('Backtesting Module', overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, commission_type=strategy.commission.percent, commission_value=0.04, margin_long=0, margin_short=0, close_by_id=True)
def main(
    go_long=input.bool(group=gr_l, inline='l1', tooltip=tt_l, defval=True, title='Long '),
    go_short=input.bool(group=gr_s, inline='s1', tooltip=tt_s, defval=True, title='Short '),
    long_entry: Series[float] = input(group=gr_l, inline='l2', tooltip=tt_0, defval=close, title='Entry '),
    long_exit: Series[float] = input(group=gr_l, inline='l2', tooltip=tt_0, defval=close, title='   Exit '),
    short_entry: Series[float] = input(group=gr_s, inline='s2', tooltip=tt_0, defval=close, title='Entry '),
    short_exit: Series[float] = input(group=gr_s, inline='s2', tooltip=tt_0, defval=close, title='   Exit'),
    trade_mode=input.string(title='Trade ', defval='Both ', options=('Both ', 'Long ', 'Short '), group=grc),
    set_gmt=input.int(title='GMT+', defval=3, minval=-12, maxval=14, tooltip=tt1, group=grc),
    start_i=input.time(group=grc, defval=start_ts, title='Start '),
    end_i=input.time(group=grc, defval=end_ts, title='End '),
    sh_entry=input.bool(defval=False, title='Entry Price '),
    sh_avg=input.bool(defval=False, title='Average Entry Price '),
    sh_barc=input.bool(defval=False, title='Barcolor '),
    tb_pos=input.string(title='Position', defval='Right 1', group=grt, options=('Left 1', 'Left 2', 'Center 1', 'Center 2', 'Right 1', 'Right 2')),
    c1=input.color(color.new('#686868'), '', group=grt, inline='c'),
    c2=input.color(color.new('#8C00FF'), '', group=grt, inline='c'),
    c3=input.color(color.new('#00FF00'), '', group=grt, inline='c'),
    c4=input.color(color.new('#FF4242'), '', group=grt, inline='c'),
    c5=input.color(color.new('#00BBFF'), '', group=grt, inline='c'),
    c6=input.color(color.new('#FF9800'), '', group=grt, inline='c')
):
    default_long = ta.crossover(ta.sma(close, 50), ta.sma(close, 200))
    default_short = ta.crossunder(ta.sma(close, 50), ta.sma(close, 200))
    strategy.risk.allow_entry_in(strategy.direction.long if trade_mode == 'Long ' else strategy.direction.short if trade_mode == 'Short ' else strategy.direction.all)
    offset = set_gmt * 1000 * 60 * 60
    start = ta.valuewhen(bar_index == 0, time, 0) + offset if start_i == start_ts else start_i + offset
    end = timenow + offset if end_i == end_ts else end_i + offset
    interval = start <= time + offset and end >= time + offset
    def f_run(x):
        return not (x == open or x == high or x == low or (x == close) or (x == hl2) or (x == hlc3) or (x == ohlc4) or (x == hlcc4))

    f_run_1 = f_run(long_entry)
    f_run_2 = f_run(long_exit)
    run_long = go_long and f_run_1 and f_run_2
    f_run_3 = f_run(short_entry)
    f_run_4 = f_run(short_exit)
    run_short = go_short and f_run_3 and f_run_4
    none = not (run_long or run_short)
    if interval:
        if none:
            if default_long:
                strategy.entry(id='Long', direction=strategy.long, comment='Golden Cross')
            if default_short:
                strategy.entry(id='Short', direction=strategy.short, comment='Death Cross')
        if run_long:
            if long_exit == 1:
                strategy.close(id='Long', comment='Long Exit')
            if long_entry == 1:
                strategy.close(id='Short', comment='Short Exit')
                strategy.entry(id='Long', direction=strategy.long, comment='Long Entry')
        if run_short:
            if short_exit == 1:
                strategy.close(id='Short', comment='Short Exit')
            if short_entry == 1:
                strategy.close(id='Long', comment='Long Exit')
                strategy.entry(id='Short', direction=strategy.short, comment='Short Entry')
    else:
        strategy.close(id='Long', comment='Long Exit')
        strategy.close(id='Short', comment='Short Exit')
    twl: Persistent[int] = 0
    tws: Persistent[int] = 0
    tll: Persistent[int] = 0
    tls: Persistent[int] = 0
    das_capital = strategy.initial_capital
    profit = strategy.netprofit
    equity = strategy.equity
    in_long = strategy.position_size > 0
    in_short = strategy.position_size < 0
    in_position = strategy.position_size != 0
    trades = strategy.closedtrades
    trades_win: Series = strategy.wintrades
    trades_loss: Series = strategy.losstrades
    bars = ta.cum(1 if interval else 0)
    r_pnl_p = profit / das_capital * 100
    unr_pnl_p = (equity - das_capital) / das_capital * 100
    st_dir: Series = 1 if in_long else -1 if in_short else 0
    st_exit_l = st_dir != 1 and st_dir[1] == 1
    st_exit_s = st_dir != -1 and st_dir[1] == -1
    diff_win = trades_win - trades_win[1]
    diff_loss = trades_loss - trades_loss[1]
    if st_exit_l:
        twl = twl + diff_win
        tll = tll + diff_loss
    if st_exit_s:
        tws = tws + diff_win
        tls = tls + diff_loss
    win_ratio_l = twl / (twl + tll) * 100
    win_ratio_s = tws / (tws + tls) * 100
    win_ratio = trades_win / trades * 100
    r_pnl_c = c3 if r_pnl_p >= 0 else c4
    unr_pnl_c = c3 if unr_pnl_p >= 0 else c4
    plot(na if not sh_entry else strategy.opentrades.entry_price(strategy.opentrades - 1), 'Entry price', chart.fg_color, 2, plot.style_circles)
    plot(na if not sh_avg else strategy.position_avg_price, 'Average Entry price', color.new('#2962FF'), 2, plot.style_circles)
    barcolor(na if not sh_barc else color.new('#00FF00') if st_dir == 1 else color.new('#FF0000') if st_dir == -1 else color.new('#333333'), title='Barcolor')
    pos = position.top_left if tb_pos == 'Left 1' else position.bottom_left if tb_pos == 'Left 2' else position.top_center if tb_pos == 'Center 1' else position.bottom_center if tb_pos == 'Center 2' else position.top_right if tb_pos == 'Right 1' else position.bottom_right
    tb: Persistent[Table] = table.new(pos, 5, 15, na, color.new('#5D606B'), 3, color.new('#5D606B'), 1)
    def f_print(x, y, c, t):
        return table.cell(tb, x - 1, y - 1, t, text_color=c)

    def f_merge(x, y):
        return table.merge_cells(tb, x - 1, y - 1, 4, y - 1)

    def f_txt_l(x):
        return '─' if trade_mode == 'Short ' or not run_long else x

    def f_txt_s(x):
        return '─' if trade_mode == 'Long ' or not run_short else x

    if barstate.islastconfirmedhistory or barstate.isrealtime:
        f_print(1, 1, c1, 'PNL')
        f_print(1, 2, c1, 'Realized')
        f_print(1, 3, c1, 'Unrealized')
        f_print(1, 4, c1, 'REPORT')
        f_print(1, 5, c1, 'Trades')
        f_print(2, 5, c1, '  Σ  ')
        f_print(3, 5, c1, ' Win ')
        f_print(4, 5, c1, 'Loss')
        f_print(5, 5, c1, 'Win Rate')
        f_print(1, 6, c1, 'Long')
        f_print(1, 7, c1, 'Short')
        f_print(1, 8, c1, 'Total')
        f_print(1, 9, c1, 'INTERVAL [GMT+' + string.tostring(cast_int(set_gmt)) + ']')
        f_print(1, 10, c1, 'Start')
        f_print(1, 11, c1, 'End')
        f_print(1, 12, c1, 'Bars')
        f_print(2, 2, r_pnl_c, '% ' + string.tostring(r_pnl_p, '#.##'))
        f_print(2, 3, unr_pnl_c, '─' if not in_position else '% ' + string.tostring(unr_pnl_p, '#.##'))
        f_print(2, 6, c2, f_txt_l(string.tostring(twl + tll)))
        f_print(3, 6, c3, f_txt_l(string.tostring(twl)))
        f_print(4, 6, c4, f_txt_l(string.tostring(tll)))
        f_print(5, 6, c5, f_txt_l('% ' + string.tostring(win_ratio_l, '#.##')))
        f_print(2, 7, c2, f_txt_s(string.tostring(tws + tls)))
        f_print(3, 7, c3, f_txt_s(string.tostring(tws)))
        f_print(4, 7, c4, f_txt_s(string.tostring(tls)))
        f_print(5, 7, c5, f_txt_s('% ' + string.tostring(win_ratio_s, '#.##')))
        f_print(2, 8, c2, string.tostring(trades_win + trades_loss))
        f_print(3, 8, c3, string.tostring(trades_win))
        f_print(4, 8, c4, string.tostring(trades_loss))
        f_print(5, 8, c5, '% ' + string.tostring(win_ratio, '#.##'))
        f_print(2, 10, c6, string.format_time(start, 'dd.MM.yyyy - HH:mm'))
        f_print(2, 11, c6, string.format_time(end, 'dd.MM.yyyy - HH:mm'))
        f_print(2, 12, c6, string.tostring(bars))
        f_merge(1, 1)
        f_merge(1, 9)
        f_merge(2, 3)
        f_merge(2, 11)
        f_merge(1, 4)
        f_merge(2, 2)
        f_merge(2, 10)
        f_merge(2, 12)
        if none:
            table.cell(tb, 0, 12, '\n// Deafult Test : Golden & Death Cross\n ', text_color=c1, tooltip='When you enter your own conditions the default test will be neutralized.')
            f_merge(1, 13)
    plotshape(barstate.isfirst, '@ dg_factor', shape.flag, location.bottom, color.new('#00000000'), editable=False)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
