"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    array, barstate, close, color, currency, input, math, month, na, nz,
    open, plot, position, script, size, strategy, string, ta, table, text, time, year
)
from pynecore.types import Persistent, Series

stratGroup: str = 'Strategy'


@script.strategy(title='v.5 - 3 EMA + RSI with Trail Stop', shorttitle='v.5 - 3 EMA + RSI + Trail Stop', overlay=True, pyramiding=0, currency=currency.USD, default_qty_type=strategy.percent_of_equity, initial_capital=1000, default_qty_value=20, commission_type=strategy.commission.percent, commission_value=0.05, margin_long=0, margin_short=0, close_by_id=True)
def main(
    len=input.int(14, minval=1, title='Length', group='RSI'),
    src: Series[float] = input.source(close, 'Source', group='RSI'),
    long_rsi=input.int(30, minval=1, title='Exit Short RSI', group='RSI'),
    short_rsi=input.int(70, minval=1, title='Exit Long RSI', group='RSI'),
    len_a=input.int(10, minval=1, title='EMA A Length', group='Moving Averages'),
    len_b=input.int(20, minval=1, title='EMA B Length', group='Moving Averages'),
    len_c=input.int(100, minval=1, title='EMA C Length', group='Moving Averages'),
    trail_point=input.float(50, title='Trail Points', group='Trailing Stop'),
    trail_offset=input.float(10, title='Trail Offset', group='Trailing Stop'),
    fixStopLossPerc=input.float(5.0, title='Fixed Stop Loss (%)', group='Stop Loss'),
    showLong=input.bool(True, title='Long entries', group=stratGroup),
    showShort=input.bool(False, title='Short entries', group=stratGroup),
    closeAfterXBars=input.bool(True, title='Close after X # bars', tooltip='If trade is in profit', group=stratGroup),
    xBars=input.int(24, title='# bars'),
    show_performance=input.bool(True, 'Show Monthly Monthly Performance ?', group='Monthly Performance'),
    dash_loc_mp=input.session('Bottom Right', 'Location', options=('Top Right', 'Bottom Right', 'Top Left', 'Bottom Left', 'Middle Right', 'Bottom Center'), group='Monthly Performance', inline='performance'),
    text_size_mp=input.session('Small', 'Size', options=('Tiny', 'Small', 'Normal', 'Large'), group='Monthly Performance', inline='performance'),
    bg_c=input.color(color.rgb(7, 226, 242, 38), 'Background Color', group='Monthly Performance'),
    text_head_color=input.color(color.rgb(0, 0, 0), 'Month/Year Heading Color', group='Monthly Performance'),
    tab_month_c=input.color(color.white, 'Month PnL Data Color', group='Monthly Performance'),
    tab_year_c=input.color(color.rgb(0, 0, 0), 'Year PnL Data Color', group='Monthly Performance'),
    border_c=input.color(color.white, 'Table Border Color', group='Monthly Performance')
):
    rsi = ta.rsi(src, len)
    out_a = ta.ema(close, len_a)
    plot(out_a, title='EMA A', color=color.purple)
    out_b = ta.ema(close, len_b)
    plot(out_b, title='EMA B', color=color.orange)
    out_c = ta.ema(close, len_c)
    plot(out_c, title='EMA B', color=color.green)
    entryLong = ta.crossover(out_a, out_b) and out_a > out_c and (close > open)
    exitLong = rsi > short_rsi
    entryShort = ta.crossunder(out_a, out_b) and out_a < out_c and (close < open)
    exitShort = rsi < long_rsi
    bought = strategy.opentrades == 1 and strategy.position_size > strategy.position_size[1]
    entry_price = ta.valuewhen(bought, open, 0)
    nPastBars: Persistent[int] = 0
    if strategy.position_size > 0:
        nPastBars = nPastBars + 1
    if strategy.position_size == 0:
        nPastBars = 0
    if closeAfterXBars:
        exitLong = True if nPastBars >= xBars and close > entry_price else exitLong
        exitLong
        exitShort = True if nPastBars >= xBars and close < entry_price else exitShort
    if entryLong and showLong:
        if strategy.position_size < 0:
            strategy.close('Short', comment='Close Short → New Long')
        strategy.entry('Long', strategy.long)
    if entryShort and showShort:
        if strategy.position_size > 0:
            strategy.close('Long', comment='Close Long → New Short')
        strategy.entry('Short', strategy.short)
    if strategy.position_size > 0:
        if exitLong:
            strategy.close('Long', comment='RSI Exit Long')
    if strategy.position_size < 0:
        if exitShort:
            strategy.close('Short', comment='RSI Exit Short')
    if strategy.position_size > 0:
        longStopPrice: float = strategy.position_avg_price * (1 - fixStopLossPerc / 100.0)
        strategy.exit('Trail Stop Long', from_entry='Long', stop=longStopPrice, trail_points=trail_point, trail_offset=trail_offset)
    if strategy.position_size < 0:
        shortStopPrice: float = strategy.position_avg_price * (1 + fixStopLossPerc / 100.0)
        strategy.exit('Trail Stop Short', from_entry='Short', stop=shortStopPrice, trail_points=trail_point, trail_offset=trail_offset)
    table_position_mp: Persistent = position.top_left if dash_loc_mp == 'Top Left' else position.bottom_left if dash_loc_mp == 'Bottom Left' else position.middle_right if dash_loc_mp == 'Middle Right' else position.bottom_center if dash_loc_mp == 'Bottom Center' else position.top_right if dash_loc_mp == 'Top Right' else position.bottom_right
    table_text_size_mp: Persistent = size.tiny if text_size_mp == 'Tiny' else size.small if text_size_mp == 'Small' else size.normal if text_size_mp == 'Normal' else size.large
    new_month = ta.change(month)
    newest_month = cast_bool(new_month) and strategy.closedtrades >= 1
    only_profit = strategy.netprofit
    initial_balance = strategy.initial_capital
    month_number: Persistent[int] = na(int)
    month_number = ta.valuewhen(newest_month, month(time), 0)
    month_time: Persistent[int] = na(int)
    month_time = ta.valuewhen(newest_month, time, 0) - 2419200000
    m_counter: Persistent[int] = 0
    if newest_month:
        m_counter = m_counter + 1
    new_year: Persistent[bool] = na(bool)
    new_year = True if cast_bool(ta.change(year)) else False
    curr_m_pnl = only_profit - nz(ta.valuewhen(newest_month, only_profit, 0), 0)
    curr_m_number = ta.valuewhen(newest_month, month(time), 0) if newest_month else month(time)
    curr_y_pnl = only_profit - nz(ta.valuewhen(new_year, only_profit, 0), 0)
    net_profit_array: Persistent[list[float]] = array.new_float()
    month_array: Persistent[list[int]] = array.new_int()
    month_time_array: Persistent[list[int]] = array.new_int()
    if newest_month:
        array.push(net_profit_array, only_profit)
        array.push(month_array, month_number)
        array.push(month_time_array, month_time)
    y_pnl_array: Persistent[list[float]] = array.new_float()
    y_number_array: Persistent[list[int]] = array.new_int()
    y_time_array: Persistent[list[int]] = array.new_int()
    newest_year = new_year and strategy.closedtrades >= 1
    get_yearly_pnl = nz(ta.valuewhen(newest_year, strategy.netprofit, 0) - nz(ta.valuewhen(newest_year, strategy.netprofit, 1), 0), 0)
    get_m_year = ta.valuewhen(newest_year, year(time), 2)
    get_y_time = ta.valuewhen(newest_year, time, 0)
    if newest_year:
        array.push(y_pnl_array, get_yearly_pnl)
        array.push(y_number_array, get_m_year)
        array.push(y_time_array, get_y_time)
    monthly_profit: Persistent[float] = na(float)
    column_month_number: Persistent[int] = na(int)
    row_month_time: Persistent[int] = na(int)
    row_y: Persistent[int] = na(int)
    total_trades = strategy.closedtrades
    wintrades = strategy.wintrades
    perc_profitable = wintrades / total_trades * 100
    gross_profit = strategy.grossprofit
    gross_loss = strategy.grossloss
    profit_factor = gross_profit / gross_loss
    testTable: Persistent = table.new(position=table_position_mp, columns=20, rows=40, bgcolor=bg_c, border_color=border_c, border_width=1)
    if barstate.islastconfirmedhistory and show_performance:
        table.cell(table_id=testTable, column=0, row=0, text='YEAR', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=1, row=0, text='JAN', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=2, row=0, text='FEB', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=3, row=0, text='MAR', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=4, row=0, text='APR', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=5, row=0, text='MAY', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=6, row=0, text='JUN', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=7, row=0, text='JUL', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=8, row=0, text='AUG', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=9, row=0, text='SEP', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=10, row=0, text='OCT', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=11, row=0, text='NOV', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=12, row=0, text='DEC', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=13, row=0, text='YEAR P/L', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=14, row=0, text='% Profitable     =>', text_color=text_head_color, text_size=table_text_size_mp, bgcolor=color.orange, text_halign=text.align_left)
        table.cell(table_id=testTable, column=14, row=1, text='Profit Factor    =>', text_color=text_head_color, text_size=table_text_size_mp, bgcolor=color.orange, text_halign=text.align_left)
        table.cell(table_id=testTable, column=14, row=2, text='Total Trades     =>', text_color=text_head_color, text_size=table_text_size_mp, bgcolor=color.orange, text_halign=text.align_left)
        table.cell(table_id=testTable, column=14, row=3, text='Max Drawdown =>', text_color=text_head_color, text_size=table_text_size_mp, bgcolor=color.orange, text_halign=text.align_left)
        table.cell(table_id=testTable, column=14, row=4, text='Max Run-Up   =>', text_color=text_head_color, text_size=table_text_size_mp, bgcolor=color.orange, text_halign=text.align_left)
        table.cell(table_id=testTable, column=14, row=5, text='Initial Capital  =>', text_color=text_head_color, text_size=table_text_size_mp, bgcolor=color.orange, text_halign=text.align_left)
        for i in pine_range(0, na if array.size(y_number_array) == 0 else array.size(y_number_array) - 1, 1):
            row_y = year(array.get(y_time_array, i)) - year(array.get(y_time_array, 0)) + 1
            table.cell(table_id=testTable, column=13, row=row_y, text=string.tostring(array.get(y_pnl_array, i), '##.##') + '\n' + '(' + string.tostring(array.get(y_pnl_array, i) * 100 / initial_balance, '##.##') + ' %)', bgcolor=color.green if array.get(y_pnl_array, i) > 0 else color.red if array.get(y_pnl_array, i) < 0 else color.gray, text_color=tab_year_c, text_size=table_text_size_mp)
        curr_row_y = 1 if array.size(month_time_array) == 0 else year(array.get(month_time_array, array.size(month_time_array) - 1)) - year(array.get(month_time_array, 0)) + 1
        table.cell(table_id=testTable, column=13, row=row_y + 1 if row_y >= 0 else 1, text=string.tostring(curr_y_pnl, '##.##') + '\n' + '(' + string.tostring(curr_y_pnl * 100 / initial_balance, '##.##') + ' %)', bgcolor=color.green if curr_y_pnl > 0 else color.red if curr_y_pnl < 0 else color.gray, text_color=tab_year_c, text_size=table_text_size_mp)
        for i in pine_range(0, na if array.size(net_profit_array) == 0 else array.size(net_profit_array) - 1, 1):
            monthly_profit = array.get(net_profit_array, i) - array.get(net_profit_array, i - 1) if i > 0 else array.get(net_profit_array, i)
            column_month_number = month(array.get(month_time_array, i))
            row_month_time = year(array.get(month_time_array, i)) - year(array.get(month_time_array, 0)) + 1
            table.cell(table_id=testTable, column=column_month_number, row=row_month_time, text=string.tostring(monthly_profit, '##.##') + '\n' + '(' + string.tostring(monthly_profit * 100 / initial_balance, '##.##') + ' %)', bgcolor=color.green if monthly_profit > 0 else color.red if monthly_profit < 0 else color.gray, text_color=tab_month_c, text_size=table_text_size_mp)
            table.cell(table_id=testTable, column=0, row=row_month_time, text=string.tostring(year(array.get(month_time_array, i)), '##.##'), text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=curr_m_number, row=1 if nz(row_month_time) <= 0 else row_month_time + 1, text=string.tostring(curr_m_pnl, '##.##') + '\n' + '(' + string.tostring(curr_m_pnl * 100 / initial_balance, '##.##') + ' %)', bgcolor=color.green if curr_m_pnl > 0 else color.red if curr_m_pnl < 0 else color.gray, text_color=tab_month_c, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=0, row=1 if nz(row_month_time) <= 0 else row_month_time + 1, text=string.tostring(year(time), '##.##'), text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=15, row=0, text=string.tostring(perc_profitable, '##.##') + ' %', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=15, row=1, text=string.tostring(profit_factor, '##.##'), text_color=text_head_color, text_size=table_text_size_mp, bgcolor=color.green if profit_factor >= 1 else color.red)
        table.cell(table_id=testTable, column=15, row=2, text=string.tostring(total_trades, '##') + '\n' + '(' + string.tostring(wintrades, '##') + 'W + ' + string.tostring(total_trades - wintrades, '##') + 'L' + ')', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=15, row=3, text=string.tostring(strategy.max_drawdown, '##.##') + '\n' + '(' + string.tostring(strategy.max_drawdown_percent, '##.##') + ' %' + ')', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=15, row=4, text=string.tostring(strategy.max_runup, '##.##') + '\n' + '(' + string.tostring(strategy.max_runup_percent, '##.##') + ' %' + ')', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=15, row=5, text=string.tostring(strategy.initial_capital, '##.##') + ' ' + string.tostring(strategy.account_currency), text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=12, row=row_y + 2 if row_y >= 0 else 2, text='Net Profit =>', text_color=text_head_color, text_size=table_text_size_mp, bgcolor=color.yellow)
        table.cell(table_id=testTable, column=13, row=row_y + 2 if row_y >= 0 else 2, text=string.tostring(strategy.netprofit, '##.##') + '\n' + '(' + string.tostring(strategy.netprofit_percent, '##.##') + ' %)', bgcolor=color.green if strategy.netprofit > 0 else color.red if strategy.netprofit < 0 else color.gray, text_color=tab_month_c, text_size=table_text_size_mp)
    currConsecWins: Persistent[int] = 0
    currConsecLosses: Persistent[int] = 0
    maxConsecWins: Persistent[int] = 0
    maxConsecLosses: Persistent[int] = 0
    prev_closed_trades: Persistent[int] = 0
    prev_netprofit: Persistent[float] = 0.0
    if strategy.closedtrades > prev_closed_trades:
        trade_profit = strategy.netprofit - prev_netprofit
        if trade_profit > 0:
            currConsecWins = currConsecWins + 1
            currConsecLosses = 0
            maxConsecWins = math.max(maxConsecWins, currConsecWins)
        elif trade_profit < 0:
            currConsecLosses = currConsecLosses + 1
            currConsecWins = 0
            maxConsecLosses = math.max(maxConsecLosses, currConsecLosses)
        else:
            currConsecWins = 0
            currConsecLosses = 0
        prev_netprofit = strategy.netprofit
        prev_closed_trades = strategy.closedtrades
    T_dataWindow: Persistent = table.new(position.top_right, 2, 14, color.rgb(255, 255, 255, 55), border_width=1)
    if barstate.islast or barstate.islastconfirmedhistory:
        table.cell(T_dataWindow, 0, 0, 'Info', text_size=size.auto, text_color=color.white, bgcolor=color.gray, text_halign=text.align_left)
        table.cell(T_dataWindow, 0, 1, 'Initial Capital', text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 0, 2, 'Equity', text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 0, 3, 'Net Profit', text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 0, 4, 'Open Profit', text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 0, 5, 'Gross Profit', text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 0, 6, 'Gross Loss', text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 0, 7, 'Open Trades', text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 0, 8, 'Closed Trades', text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 0, 9, 'Winning Trades', text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 0, 10, 'Losing Trades', text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 0, 11, 'Break Even Trades', text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 0, 12, 'Max Consecutive Wins', text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 0, 13, 'Max Consecutive Losses', text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 1, 0, 'Value', text_size=size.auto, text_color=color.white, bgcolor=color.gray, text_halign=text.align_left)
        table.cell(T_dataWindow, 1, 1, string.tostring(strategy.initial_capital, '#.##'), text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 1, 2, string.tostring(strategy.equity, '#.##'), text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 1, 3, string.tostring(strategy.netprofit, '#.##'), text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 1, 4, string.tostring(strategy.openprofit, '#.##'), text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 1, 5, string.tostring(strategy.grossprofit, '#.##'), text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 1, 6, string.tostring(strategy.grossloss, '#.##'), text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 1, 7, string.tostring(strategy.opentrades), text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 1, 8, string.tostring(strategy.closedtrades), text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 1, 9, string.tostring(strategy.wintrades), text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 1, 10, string.tostring(strategy.losstrades), text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 1, 11, string.tostring(strategy.eventrades), text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 1, 12, string.tostring(maxConsecWins), text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)
        table.cell(T_dataWindow, 1, 13, string.tostring(maxConsecLosses), text_size=size.auto, text_color=color.white, bgcolor=color.black, text_halign=text.align_left)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
