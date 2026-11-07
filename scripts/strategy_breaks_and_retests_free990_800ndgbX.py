"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barstate, box, close, color,
    dayofmonth, extend, fixnan, high, input, label, line, low, math, month, na, plot, position,
    script, size, strategy, string, ta, table, text, time, timestamp, year
)
from pynecore.types import Box, Color, Label, Persistent, Series, Table

g_sr: str = 'Support and Resistance'
g_c: str = 'Conditions'
g_st: str = 'Styling'
t_r: str = 'Bar Confirmation: Generates alerts when candle closes. (1 Candle Later) \n\nHigh & Low: By default, the Break & Retest system uses the current close value to determine a condition, selecting High & Low will make the script utilize these two values instead of the close value. In return, the script won\'t repaint and will yield different results.'
t_rv: str = 'Whenever a potential retest is detected, the indicator knows that a retest is about to happen. In that given situation, this input grants the ability to raise the limit on how many bars are allowed to be actively checked while a potential retest event is active.\n\nExample, if you see the potential retest label, how many bars do you want that potential retest label to be active for to eventually confirm a retest? This system was implemented to prevent retest alerts from going off 10+ bars later from the potential retest point leading to inaccurate results.'


@script.strategy('Breaks and Retests - Free990', shorttitle='BnR Free990', overlay=True, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    input_lookback=input.int(defval=20, title='Lookback Range', minval=1, tooltip='How many bars for a pivot event to occur.', group=g_sr),
    input_retSince=input.int(defval=2, title='Bars Since Breakout', minval=1, tooltip='How many bars since breakout in order to detect a retest.', group=g_sr),
    input_retValid=input.int(defval=2, title='Retest Detection Limiter', minval=1, tooltip=t_rv, group=g_sr),
    input_breakout=input.bool(defval=True, title='Breakouts', group=g_c),
    input_retest=input.bool(defval=True, title='Retests', group=g_c),
    input_repType=input.string(defval='On', title='Repainting', options=('On', 'Off: Candle Confirmation', 'Off: High & Low'), tooltip=t_r, group=g_c),
    input_outL=input.string(defval=line.style_dotted, title='Outline', group=g_st, options=(line.style_dotted, line.style_dashed, line.style_solid)),
    input_extend=input.string(defval=extend.none, title='Extend', group=g_st, options=(extend.none, extend.right, extend.left, extend.both)),
    input_labelType=input.string(defval='Full', title='Label Type', options=('Full', 'Simple'), group=g_st),
    input_labelSize=input.string(defval=size.small, title='Label Size', options=(size.tiny, size.small, size.normal, size.large, size.huge), group=g_st),
    input_plColor=input.color(defval=color.red, title='Support', inline='Color', group=g_st),
    input_phColor=input.color(defval=color.new('#089981'), title='Resistance', inline='Color', group=g_st),
    input_override=input.bool(defval=False, title='Override Text Color ', inline='Override', group=g_st),
    input_textColor=input.color(defval=color.white, title='', inline='Override', group=g_st),
    profit_threshold_percent=input.float(5.0, title='Profit Threshold (%)', step=0.1),
    trailing_stop_gap_percent=input.float(1.0, title='Trailing Stop Gap (%)', step=0.1),
    stop_loss_percent=input.float(2.0, title='Initial Stop Loss (%)', step=0.1),
    trade_direction=input.string('Both', title='Trade Direction', options=('Long Only', 'Short Only', 'Both')),
    show_performance=input.bool(True, 'Show Daily Performance ?', group='Daily Performance'),
    dash_loc_mp=input.string('Bottom Right', 'Location', options=('Top Right', 'Bottom Right', 'Top Left', 'Bottom Left', 'Middle Right', 'Bottom Center'), group='Daily Performance', inline='performance'),
    text_size_mp=input.string('Small', 'Size', options=('Tiny', 'Small', 'Normal', 'Large'), group='Daily Performance', inline='performance'),
    bg_c=input.color(color.new(color.rgb(7, 226, 242), 38), 'Background Color', group='Daily Performance'),
    text_head_color=input.color(color.rgb(0, 0, 0), 'Heading Color', group='Daily Performance'),
    tab_text_c=input.color(color.white, 'Data Text Color', group='Daily Performance'),
    border_c=input.color(color.white, 'Table Border Color', group='Daily Performance')
):
    bb = input_lookback
    rTon = input_repType == 'On'
    rTcc = input_repType == 'Off: Candle Confirmation'
    rThv = input_repType == 'Off: High & Low'
    breakText = 'Br' if input_labelType == 'Simple' else 'Break'
    pl = fixnan(ta.pivotlow(low, bb, bb))
    ph = fixnan(ta.pivothigh(high, bb, bb))
    s_yLoc = low[bb - 1] if low[bb + 1] > low[bb - 1] else low[bb + 1]
    r_yLoc = high[bb + 1] if high[bb + 1] > high[bb - 1] else high[bb - 1]
    def drawBox(condition, y1, y2, color__ren__):
        drawBox__00000025__: Persistent[Box] = na(Box)
        if condition:
            box.set_right(drawBox__00000025__, bar_index - bb)
            box.set_extend(drawBox__00000025__, extend.none)
            drawBox__00000025__ = box.new(bar_index - bb, y1, bar_index, y2, color__ren__, bgcolor=color.new(color__ren__, 90), border_style=input_outL, extend=input_extend)
        return (drawBox__00000025__,)

    def updateBox(box__ren__):
        __block_result__ = na
        if barstate.isconfirmed:
            __block_result__ = box.set_right(box__ren__, bar_index + 5)
        return __block_result__

    def breakLabel(y, color__ren__, style, textform):
        return label.new(bar_index, y, textform, textcolor=input_textColor if input_override else color__ren__, style=style, color=color.new(color__ren__, 50), size=input_labelSize)

    def retestCondition(breakout, condition):
        return ta.barssince(na(breakout)) > input_retSince and condition

    def repaint(c1, c2, c3):
        return c1 if rTon else c2 if rThv else c3 if rTcc else na

    sBox: Series
    sBox, = drawBox(ta.change(pl), s_yLoc, pl, input_plColor)
    rBox: Series
    rBox, = drawBox(ta.change(ph), ph, r_yLoc, input_phColor)
    sTop = box.get_top(sBox)
    rTop = box.get_top(rBox)
    sBot = box.get_bottom(sBox)
    rBot = box.get_bottom(rBox)
    updateBox(sBox)
    updateBox(rBox)
    sBreak: Persistent[bool] = na(bool)
    rBreak: Persistent[bool] = na(bool)
    cu = repaint(ta.crossunder(close, box.get_bottom(sBox)), ta.crossunder(low, box.get_bottom(sBox)), ta.crossunder(close, box.get_bottom(sBox)) and barstate.isconfirmed)
    co = repaint(ta.crossover(close, box.get_top(rBox)), ta.crossover(high, box.get_top(rBox)), ta.crossover(close, box.get_top(rBox)) and barstate.isconfirmed)
    if cu and na(sBreak):
        sBreak = True
        if input_breakout:
            breakLabel(sBot, input_plColor, label.style_label_upper_right, breakText)
    elif co and na(rBreak):
        rBreak = True
        if input_breakout:
            breakLabel(rTop, input_phColor, label.style_label_lower_right, breakText)
    if cast_bool(ta.change(pl)):
        if na(sBreak):
            box.delete(sBox[1])
        sBreak = na
    if cast_bool(ta.change(ph)):
        if na(rBreak):
            box.delete(rBox[1])
        rBreak = na
    s1 = retestCondition(sBreak, high >= sTop and close <= sBot)
    s2 = retestCondition(sBreak, high >= sTop and close >= sBot and (close <= sTop))
    s3 = retestCondition(sBreak, high >= sBot and high <= sTop)
    s4 = retestCondition(sBreak, high >= sBot and high <= sTop and (close < sBot))
    r1 = retestCondition(rBreak, low <= rBot and close >= rTop)
    r2 = retestCondition(rBreak, low <= rBot and close <= rTop and (close >= rBot))
    r3 = retestCondition(rBreak, low <= rTop and low >= rBot)
    r4 = retestCondition(rBreak, low <= rTop and low >= rBot and (close > rTop))
    def retestEvent(c1, c2, c3, c4, y1, y2: Series, col, style, pType):
        __hist_sBox__: Series[void] = sBox[0]
        __hist_rBox__: Series[void] = rBox[0]
        __block_result_1__ = (na, na, na)
        if input_retest:
            retOccurred: Persistent[bool] = na(bool)
            retActive: Series = c1 or c2 or c3 or c4
            retEvent = retActive and (not retActive[1])
            retValue = ta.valuewhen(retEvent, y1, 0)
            if y2 < ta.valuewhen(retEvent, y2, 0) if pType == 'ph' else y2 > ta.valuewhen(retEvent, y2, 0):
                retEvent = retActive
            retValue = ta.valuewhen(retEvent, y1, 0)
            retSince = ta.barssince(retEvent)
            retLabel: Persistent[list[Label]] = array.new_label()
            if retEvent:
                retOccurred = na
                array.push(retLabel, label.new(bar_index - retSince, y2[retSince], text='P. Re' if input_labelType == 'Simple' else 'Potential Retest', color=color.new(col, 50), style=style, textcolor=input_textColor if input_override else col, size=input_labelSize))
            if array.size(retLabel) == 2:
                label.delete(array.first(retLabel))
                array.shift(retLabel)
            retConditions = repaint(close >= retValue, high >= retValue, close >= retValue and barstate.isconfirmed) if pType == 'ph' else repaint(close <= retValue, low <= retValue, close <= retValue and barstate.isconfirmed)
            barssince_1 = ta.barssince(retEvent)
            retValid = ta.barssince(retEvent) > 0 and barssince_1 <= input_retValid and retConditions and (not retOccurred)
            if retValid:
                label.new(bar_index - retSince, y2[retSince], text='Re' if input_labelType == 'Simple' else 'Retest', color=color.new(col, 50), style=style, textcolor=input_textColor if input_override else col, size=input_labelSize)
                retOccurred = True
            barssince_2 = ta.barssince(retEvent)
            if retValid or barssince_2 > input_retValid:
                label.delete(array.first(retLabel))
            change_1__0000008a__ = ta.change(ph)
            if pType == 'ph' and change_1__0000008a__ and retOccurred:
                box.set_right(__hist_rBox__[1], bar_index - retSince)
                retOccurred = na
            change_2__0000008a__ = ta.change(pl)
            if pType == 'pl' and change_2__0000008a__ and retOccurred:
                box.set_right(__hist_sBox__[1], bar_index - retSince)
                retOccurred = na
            __block_result_1__ = (retValid, retEvent, retValue)
        return __block_result_1__

    rRetValid, rRetEvent = retestEvent(r1, r2, r3, r4, high, low, input_phColor, label.style_label_upper_left, 'ph')[:2]
    sRetValid, sRetEvent = retestEvent(s1, s2, s3, s4, low, high, input_plColor, label.style_label_lower_left, 'pl')[:2]
    buy_condition = (ta.barssince(na(rBreak)) == 1 or rRetValid) and (trade_direction == 'Long Only' or trade_direction == 'Both')
    sell_condition = (ta.barssince(na(sBreak)) == 1 or sRetValid) and (trade_direction == 'Short Only' or trade_direction == 'Both')
    trailing_stop_active: Persistent[bool] = False
    stop_loss_price: Persistent[float] = na(float)
    highest_price_since_trailing: Persistent[float] = na(float)
    lowest_price_since_trailing: Persistent[float] = na(float)
    if buy_condition and strategy.position_size == 0:
        strategy.entry('Buy', strategy.long)
    if sell_condition and strategy.position_size == 0:
        strategy.entry('Sell', strategy.short)
    if strategy.position_size > 0:
        profit_percent = (close - strategy.position_avg_price) / strategy.position_avg_price * 100
        if not trailing_stop_active and profit_percent >= profit_threshold_percent:
            trailing_stop_active = True
            highest_price_since_trailing = close
        if trailing_stop_active:
            highest_price_since_trailing = math.max(highest_price_since_trailing, close)
            stop_loss_price = highest_price_since_trailing * (1 - trailing_stop_gap_percent / 100)
        else:
            stop_loss_price = strategy.position_avg_price * (1 - stop_loss_percent / 100)
        strategy.exit('Exit Long', from_entry='Buy', stop=stop_loss_price)
    elif strategy.position_size < 0:
        profit_percent = (strategy.position_avg_price - close) / strategy.position_avg_price * 100
        if not trailing_stop_active and profit_percent >= profit_threshold_percent:
            trailing_stop_active = True
            lowest_price_since_trailing = close
        if trailing_stop_active:
            lowest_price_since_trailing = math.min(lowest_price_since_trailing, close)
            stop_loss_price = lowest_price_since_trailing * (1 + trailing_stop_gap_percent / 100)
        else:
            stop_loss_price = strategy.position_avg_price * (1 + stop_loss_percent / 100)
        strategy.exit('Exit Short', from_entry='Sell', stop=stop_loss_price)
    else:
        trailing_stop_active = False
        highest_price_since_trailing = na
        lowest_price_since_trailing = na
    plot(stop_loss_price if not na(stop_loss_price) else na, title='Stop Loss', color=color.red, linewidth=2, style=plot.style_line)
    alertcondition(cast_bool(ta.change(pl)), 'New Support Level')
    alertcondition(cast_bool(ta.change(ph)), 'New Resistance Level')
    alertcondition(ta.barssince(na(sBreak)) == 1, 'Support Breakout')
    alertcondition(ta.barssince(na(rBreak)) == 1, 'Resistance Breakout')
    alertcondition(sRetValid, 'Support Retest')
    alertcondition(sRetEvent, 'Potential Support Retest')
    alertcondition(rRetValid, 'Resistance Retest')
    alertcondition(rRetEvent, 'Potential Resistance Retest')
    def AllAlerts(condition, message):
        __block_result_2__ = na
        if condition:
            __block_result_2__ = alert(message)
        return __block_result_2__

    AllAlerts(ta.change(pl), 'New Support Level')
    AllAlerts(ta.change(ph), 'New Resistance Level')
    AllAlerts(ta.barssince(na(sBreak)) == 1, 'Support Breakout')
    AllAlerts(ta.barssince(na(rBreak)) == 1, 'Resistance Breakout')
    AllAlerts(sRetValid, 'Support Retest')
    AllAlerts(sRetEvent, 'Potential Support Retest')
    AllAlerts(rRetValid, 'Resistance Retest')
    AllAlerts(rRetEvent, 'Potential Resistance Retest')
    table_position_mp: Persistent = position.top_left if dash_loc_mp == 'Top Left' else position.bottom_left if dash_loc_mp == 'Bottom Left' else position.middle_right if dash_loc_mp == 'Middle Right' else position.bottom_center if dash_loc_mp == 'Bottom Center' else position.top_right if dash_loc_mp == 'Top Right' else position.bottom_right
    table_text_size_mp: Persistent = size.tiny if text_size_mp == 'Tiny' else size.small if text_size_mp == 'Small' else size.normal if text_size_mp == 'Normal' else size.large
    month_1 = month(time)
    change_1 = ta.change(month_1)
    year_1 = year(time)
    change_2 = ta.change(year_1)
    new_day = cast_bool(ta.change(dayofmonth(time))) or cast_bool(change_1) or cast_bool(change_2)
    newest_day = new_day and strategy.closedtrades >= 1
    only_profit = strategy.netprofit
    initial_balance = strategy.initial_capital
    net_profit_start_of_day: Persistent[float] = strategy.initial_capital
    daily_pnl_array: Persistent[list[float]] = array.new_float()
    day_time_array: Persistent[list[int]] = array.new_int()
    if new_day and barstate.isconfirmed:
        prev_day_pnl = only_profit - net_profit_start_of_day
        array.push(daily_pnl_array, prev_day_pnl)
        curr_day = dayofmonth(time)
        curr_month = month(time)
        curr_year = year(time)
        correct_timestamp = timestamp(curr_year, curr_month, curr_day, 0, 0)
        array.push(day_time_array, correct_timestamp)
        net_profit_start_of_day = only_profit
    curr_d_pnl = only_profit - net_profit_start_of_day
    N: Persistent[int] = 30
    testTable: Persistent[Table] = table.new(position=table_position_mp, columns=N + 1, rows=4, bgcolor=bg_c, border_color=border_c, border_width=1)
    if barstate.islastconfirmedhistory and show_performance:
        table.cell(table_id=testTable, column=0, row=0, text='Date', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=0, row=1, text='P&L', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=0, row=2, text='P&L %', text_color=text_head_color, text_size=table_text_size_mp)
        table.cell(table_id=testTable, column=0, row=3, text='Total P&L', text_color=text_head_color, text_size=table_text_size_mp)
        num_days: int = array.size(daily_pnl_array)
        column_counter: int = 1
        total_pnl: float = 0.0
        __loop_1__ = pine_loop(0, 1)
        while __loop_1__.step(math.min(N - 1, num_days - 1)):
            i = __loop_1__.value
            if column_counter < N + 1:
                index: int = num_days - 1 - i
                daily_pnl: float = array.get(daily_pnl_array, index)
                total_pnl = total_pnl + daily_pnl
                date_time: int = array.get(day_time_array, index)
                date_str: str = string.format('{0,date,yyyy-MM-dd}', date_time)
                pnl_str: str = string.tostring(daily_pnl, '#.##')
                pnl_pct_str: str = string.tostring(daily_pnl * 100 / initial_balance, '#.##') + ' %'
                bgcolor__ren__: Color = color.new(color.green, 0) if daily_pnl > 0 else color.new(color.red, 0) if daily_pnl < 0 else color.new(color.gray, 0)
                table.cell(table_id=testTable, column=column_counter, row=0, text=date_str, text_color=tab_text_c, text_size=table_text_size_mp)
                table.cell(table_id=testTable, column=column_counter, row=1, text=pnl_str, text_color=tab_text_c, bgcolor=bgcolor__ren__, text_size=table_text_size_mp)
                table.cell(table_id=testTable, column=column_counter, row=2, text=pnl_pct_str, text_color=tab_text_c, text_size=table_text_size_mp)
                column_counter = column_counter + 1
        if column_counter < N + 1:
            daily_pnl: float = curr_d_pnl
            total_pnl = total_pnl + daily_pnl
            curr_day = dayofmonth(time)
            curr_month = month(time)
            curr_year = year(time)
            correct_timestamp = timestamp(curr_year, curr_month, curr_day, 0, 0)
            date_str: str = string.format('{0,date,yyyy-MM-dd}', correct_timestamp)
            pnl_str: str = string.tostring(daily_pnl, '#.##')
            pnl_pct_str: str = string.tostring(daily_pnl * 100 / initial_balance, '#.##') + ' %'
            bgcolor__ren__: Color = color.new(color.green, 0) if daily_pnl > 0 else color.new(color.red, 0) if daily_pnl < 0 else color.new(color.gray, 0)
            table.cell(table_id=testTable, column=column_counter, row=0, text=date_str, text_color=tab_text_c, text_size=table_text_size_mp)
            table.cell(table_id=testTable, column=column_counter, row=1, text=pnl_str, text_color=tab_text_c, bgcolor=bgcolor__ren__, text_size=table_text_size_mp)
            table.cell(table_id=testTable, column=column_counter, row=2, text=pnl_pct_str, text_color=tab_text_c, text_size=table_text_size_mp)
        total_pnl_str: str = string.tostring(total_pnl, '#.##')
        table.cell(table_id=testTable, column=1, row=3, text=total_pnl_str, text_color=tab_text_c, text_size=table_text_size_mp)
    T_dataWindow: Persistent = table.new(position.top_right, 2, 13, color.rgb(255, 255, 255, 55), border_width=1)
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


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
