"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    bar_index, barmerge, bgcolor, close, color, dayofmonth, dayofweek, input,
    label, math, month, na, nz, plot, request, script, size, strategy, string, syminfo, ta, ticker,
    time, timenow, timestamp, xloc, year, yloc
)
from pynecore.types import Label, Persistent, Series

DAILY: str = 'DAILY'
WEEKLY: str = 'WEEKLY'
MONTHLY: str = 'MONTHLY'
EXIT_NONE: str = 'NONE'
EXIT_GAIN_THRESHOLD: str = 'GAIN THRESHOLD'


@script.strategy('dca', overlay=True, pyramiding=10000, calc_on_every_tick=True, process_orders_on_close=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    month_day=input.int(15, minval=1, maxval=28),
    week_day=input.int(dayofweek.monday, options=(dayofweek.monday, dayofweek.tuesday, dayofweek.wednesday, dayofweek.thursday, dayofweek.friday, dayofweek.saturday, dayofweek.sunday)),
    dca_period=input.string(MONTHLY, options=(DAILY, MONTHLY, WEEKLY)),
    dca_sigle_size=input(100.0, title='sigle operation size in quote currency ( ex: USD on ticker EUR/USD )'),
    dca_long=input(True),
    exit_strategy=input.string(EXIT_NONE, options=(EXIT_NONE, EXIT_GAIN_THRESHOLD)),
    exit_gain_threshold=input(1000.0),
    exit_close_perc=input(25),
    __input_8__=input(2018, 'start year'),
    __input_9__=input(1, 'start month'),
    __input_10__=input(1, 'start day'),
    __input_11__=input(2100, 'end year'),
    __input_12__=input(1, 'end month'),
    __input_13__=input(1, 'end day')
):
    def fn_plot_label_below(txt, offset_x):
        x = time + (time - time[1]) * offset_x
        lab: Persistent[Label] = na(Label)
        label.delete(lab)
        lab = label.new(x=x, y=0, text=txt, xloc=xloc.bar_time, yloc=yloc.belowbar, color=color.red, textcolor=color.black, size=size.normal, style=label.style_label_up)
        return label.set_x(lab, x)

    def fn_plot_label_above(txt, offset_x):
        x = time + (time - time[1]) * offset_x
        lab: Persistent[Label] = na(Label)
        label.delete(lab)
        lab = label.new(x=x, y=0, text=txt, xloc=xloc.bar_time, yloc=yloc.abovebar, color=color.green, textcolor=color.black, size=size.normal, style=label.style_label_down)
        return label.set_x(lab, x)

    start = timestamp(__input_8__, __input_9__, __input_10__, 0, 0)
    end = timestamp(__input_11__, __input_12__, __input_13__, 0, 0)
    daily_close = request.security(ticker.new(syminfo.prefix, syminfo.ticker), 'D', close, gaps=barmerge.gaps_on)
    new_day = ta.change(dayofweek)
    month_1 = month(timenow)
    month_2 = month(time)
    dayofmonth_1 = dayofmonth(timenow)
    dayofmonth_2 = dayofmonth(time)
    is_today = year(timenow) == year(time) and month_1 == month_2 and (dayofmonth_1 == dayofmonth_2)
    is_buy_day = dca_period == WEEKLY and dayofweek == week_day or (dca_period == MONTHLY and month_day == dayofmonth) or dca_period == DAILY
    position_cost = strategy.opentrades * dca_sigle_size
    position_value = strategy.position_size * close
    profit = position_value - position_cost
    max_dd: Series[float] = 0
    max_dd = math.min(profit, nz(max_dd[1]))
    trigger = time > start and time < end and is_buy_day and cast_bool(new_day)
    close_dca = time > end or is_today
    if trigger:
        strategy.entry('DCA', direction=strategy.long if dca_long else strategy.short, qty=dca_sigle_size / close)
        if dca_long:
            label.new(x=bar_index, y=0, yloc=yloc.belowbar, size=size.tiny, style=label.style_triangleup, color=color.green)
        else:
            label.new(x=bar_index, y=0, yloc=yloc.abovebar, size=size.tiny, style=label.style_triangledown, color=color.red)
    crossover_1 = ta.crossover(profit, exit_gain_threshold)
    if exit_strategy == EXIT_GAIN_THRESHOLD and crossover_1:
        strategy.close('DCA', qty_percent=exit_close_perc)
        label.new(x=bar_index, y=0, yloc=yloc.abovebar, size=size.tiny, style=label.style_triangledown, color=color.purple)
    if close_dca:
        strategy.close('DCA', qty_percent=100)
    plot(strategy.position_avg_price, title='average position entry price')
    bgcolor((color.red if close < strategy.position_avg_price else color.green) if dca_long else color.green if close < strategy.position_avg_price else color.red)
    if ta.change(max_dd) != 0:
        fn_plot_label_below('max drowdown: ' + string.tostring(max_dd, '#.##'), 0)
    if not close_dca:
        fn_plot_label_above('profit: ' + string.tostring(profit, '#.##') + '\n' + 'cost:   ' + string.tostring(position_cost, '#.##'), 0)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)