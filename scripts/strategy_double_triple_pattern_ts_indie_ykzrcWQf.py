"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, array, bar_index, barstate, bgcolor, box, close, color, display,
    format, high, input, label, line, location, low, math, na, open, plotshape, position, script,
    shape, size, strategy, string, ta, table, time, timeframe, timestamp, xloc
)
from pynecore.types import Box, Color, Label, Line, Persistent, PersistentSeries, Series, Table

Entry_Position: str = "====== Entry Condition ====== "
Time_Filter: str = "====== Time Filter ======"
result_group: str = "====== Trading Result Table ======"
display_group: str = "====== Display ======"


@script.strategy("Double&Triple Pattern[TS_Indie]", overlay=True, max_labels_count=500, max_lines_count=500, max_boxes_count=500, max_bars_back=5000, margin_long=0, margin_short=0, initial_capital=100000)
def main(
    rr_ratio=input.float(2, "Risk Reward Ratio", step=0.1, inline="0.1", group=Entry_Position),
    length_atr=input.int(title="Stop loss ATR", defval=14, minval=1, inline="0.2", group=Entry_Position),
    x_ATR=input.float(0, "X", step=0.1, inline="0.2", group=Entry_Position),
    B_long=input.bool(True, "Entry Longㅤㅤ", inline="0.3", group=Entry_Position),
    S_short=input.bool(True, "Entry Short", inline="0.3", group=Entry_Position),
    fibo_entry=input.float(0, "Fibo Entry Zone", step=1, inline="0.5", group=Entry_Position),
    Sl_change=input.bool(True, "Change SL", inline="0.5", group=Entry_Position),
    stxt1=input.string("Swing 1", "✅ [ Fibo1 ]", inline="0.6", group=Entry_Position),
    Swing1_more=input.float(55, "Min", step=1, inline="1", group=Entry_Position),
    Swing1_less=input.float(75, "Max", step=1, inline="1", group=Entry_Position),
    use_Swing2=input.bool(True, "[ Fibo2 ]", inline="2", group=Entry_Position),
    stxt2=input.string("Swing 2", "", inline="2", group=Entry_Position),
    Swing2_more=input.float(50, "Min", step=1, inline="2.1", group=Entry_Position),
    Swing2_less=input.float(75, "Max", step=1, inline="2.1", group=Entry_Position),
    use_Swing3=input.bool(True, "[ Fibo3 ]", inline="2.5", group=Entry_Position),
    stxt3=input.string("Swing 3", "", inline="2.5", group=Entry_Position),
    Swing3_more=input.float(65, "Min", step=1, inline="3", group=Entry_Position),
    Swing3_less=input.float(110, "Max", step=1, inline="3", group=Entry_Position),
    use_size=input.bool(False, " [ Control Size Swing : xATR]", inline="4", group=Entry_Position),
    Size_candle_more=input.float(0, "Min", step=1, inline="5", group=Entry_Position),
    Size_candle_less=input.float(3, "Max", step=1, inline="5", group=Entry_Position),
    s_date=input.time(timestamp('01 Jan 1970'), "Start", inline="1", group=Time_Filter),
    en_date=input.time(timestamp('01 Jan 2500'), "End ", inline="2", group=Time_Filter),
    s_New_York=input.bool(False, "New York", inline="3", group=Time_Filter),
    t_New=input.session('1300-2200', "", inline="3", group=Time_Filter),
    s_London=input.bool(False, "London", inline="4", group=Time_Filter),
    t_Lon=input.session('0700-1600', "", inline="4", group=Time_Filter),
    s_Tokyo=input.bool(False, "Tokyo", inline="5", group=Time_Filter),
    t_Tokyo=input.session('0000-0900', "", inline="5", group=Time_Filter),
    s_Sydney=input.bool(False, "Sydney", inline="6", group=Time_Filter),
    t_Syd=input.session('2100-0600', "", inline="6", group=Time_Filter),
    Show_result=input.bool(True, "Show Result", inline="1", group=result_group, tooltip="The Profit Factor here is calculated using the formula:\n(Number of Wins x Risk-Reward Ratio) / Number of Losses\nThis formula is based on the assumption that the risk per losing trade is fixed — for example, every losing trade costs exactly 1% of the account.\nBecause of this assumption, the calculated Profit Factor will not match TradingView’s result, since TradingView uses:\nGross Profit / Gross Loss\nAnd in actual TradingView trades, the loss amount of each trade is not always equal, because the system doesn’t enforce a fixed-risk rule for every losing trade. "),
    select_position=input.string("bottom_right", "", options=("bottom_right", "bottom_center", "bottom_left", "top_center", "top_left", "top_right", "mid_center", "mid_left", "mid_right"), group=result_group, inline="1", display=display.data_window),
    Factor_up=input.float(1.3, "Profit Factor > ", step=0.1, inline="2", group=result_group),
    Factor_up_color=input(title="   ", defval=color.new('#A5D6A7'), inline="2", group=result_group),
    Factor_donw=input.float(1, "Profit Factor < ", step=0.1, inline="3", group=result_group),
    Factor_donw_color=input(title="   ", defval=color.new('#FAA1A4'), inline="3", group=result_group),
    show_line=input.bool(True, 'Line', inline="1", group=display_group),
    sw_line_style=input.string('⎯⎯⎯', '', options=('⎯⎯⎯', '----', '····'), inline='1', group=display_group),
    Color_sw=input(title=" ", defval=color.new('#F700FF'), inline="1", group=display_group),
    text_line2_col=input(title="Text", defval=color.new('#FFFFFF'), inline="1.5", group=display_group),
    Color_Mark_Swing_i1=input(color.new('#FFEE58'), 'Swing', inline="1.5", group=display_group),
    Color_Mark_Swing_i2=input(color.new('#00BCD4'), '/ ', inline="1.5", group=display_group),
    show_CF_fibo=input.bool(True, 'Box Confirm Fibo', inline="3", group=display_group),
    Size_fibo=input.string('Small', '', options=('Tiny', 'Small', 'Normal'), inline="3", group=display_group),
    col_cf_con1=input(title="Fibo Buy", defval=color.rgb(187, 217, 251, 70), inline="4", group=display_group),
    col_cf_con2=input(title="Fibo Sell", defval=color.rgb(225, 190, 231, 70), inline="4", group=display_group),
    show_CF_line=input.bool(True, 'Confirm Line', inline="5", group=display_group),
    Size_CF_line=input.string('Normal', '', options=('Small', 'Normal', 'Large'), inline="5", group=display_group),
    Color_tesst_1=input(title="Break", defval=color.new('#00AAFF'), inline="6", group=display_group),
    Color_tesst_2=input(title="Cancel", defval=color.new('#FFEE58'), inline="6", group=display_group),
    show_CF_candle=input.bool(True, 'Control Size Swing', inline="7", group=display_group),
    Size_CF_candle=input.string('Small', '', options=('Small', 'Normal', 'Large'), inline="7", group=display_group),
    Color_candle_txt=input(title="Text", defval=color.new('#000000'), inline="8", group=display_group),
    Color_candle_1=input(title="Max", defval=color.new('#00AAFF'), inline="8", group=display_group),
    Color_candle_2=input(title="Min", defval=color.new('#FFEE58'), inline="8", group=display_group)
):
    con_date = time >= s_date and time <= en_date

    def _session(sess):
        return not na(time(timeframe.period, sess, 'UTC+0'))

    Session_1 = _session(t_New)
    cf_ses1: Series = Session_1 if s_New_York else False
    Session_2 = _session(t_Lon)
    cf_ses2: Series = Session_2 if s_London else False
    Session_3 = _session(t_Tokyo)
    cf_ses3: Series = Session_3 if s_Tokyo else False
    Session_4 = _session(t_Syd)
    cf_ses4: Series = Session_4 if s_Sydney else False

    ses_check = s_New_York or s_London or s_Tokyo or s_Sydney
    time_con = cf_ses1 or cf_ses2 or cf_ses3 or cf_ses4
    con_time: Series = time_con if ses_check else True

    def position__global__(select):
        __block_result__ = na
        __switch__ = select
        if __switch__ == "bottom_right":
            __block_result__ = position.bottom_right
        elif __switch__ == "bottom_center":
            __block_result__ = position.bottom_center
        elif __switch__ == "bottom_left":
            __block_result__ = position.bottom_left
        elif __switch__ == "top_center":
            __block_result__ = position.top_center
        elif __switch__ == "top_left":
            __block_result__ = position.top_left
        elif __switch__ == "top_right":
            __block_result__ = position.top_right
        elif __switch__ == "mid_center":
            __block_result__ = position.middle_center
        elif __switch__ == "mid_left":
            __block_result__ = position.middle_left
        elif __switch__ == "mid_right":
            __block_result__ = position.middle_right
        return __block_result__


    In_Size_fibo: Persistent = size.tiny if Size_fibo == 'Tiny' else size.small if Size_fibo == 'Small' else size.normal
    In_Size_CF_line: Persistent = size.large if Size_CF_line == 'Large' else size.small if Size_CF_line == 'Small' else size.normal
    In_Size_CF_candle: Persistent = size.large if Size_CF_candle == 'Large' else size.small if Size_CF_candle == 'Small' else size.normal

    TRANSP: Color = color.new('#FFFFFF00')

    def get_line_style(style):
        __block_result_1__ = na
        __switch__ = style
        if __switch__ == '⎯⎯⎯':
            __block_result_1__ = line.style_solid
        elif __switch__ == '----':
            __block_result_1__ = line.style_dashed
        elif __switch__ == '····':
            __block_result_1__ = line.style_dotted
        return __block_result_1__

    big_high: PersistentSeries[float] = na(float)
    big_low: PersistentSeries[float] = na(float)
    Bar_big_high: PersistentSeries[int] = 0
    Bar_big_low: PersistentSeries[int] = 0
    s_high: Persistent[float] = na(float)
    s_low: Persistent[float] = na(float)
    Bar_s_high: Persistent[int] = 0
    Bar_s_low: Persistent[int] = 0

    Structure_Trend: Persistent[bool] = False
    Change_up: bool = False
    Change_down: bool = False

    H_bar_ary: Persistent[list[int]] = array.new_int(0, na)
    L_bar_ary: Persistent[list[int]] = array.new_int(0, na)
    High_ary: Persistent[list[float]] = array.new_float(0, na)
    Low_ary: Persistent[list[float]] = array.new_float(0, na)

    def value_array_unshift(array__ren__, new_value_to_add):
        if array.size(array__ren__) > 10:
            array.remove(array__ren__, 10)
        return array.unshift(array__ren__, new_value_to_add)

    if na(s_high) and barstate.isconfirmed:
        if close > open:
            Structure_Trend = True
        s_high = high
        s_low = low

    if not Structure_Trend and (not na(s_high)) and barstate.isconfirmed:
        if close > s_high:
            if low <= s_low:
                big_low = low
                Bar_big_low = bar_index
            if low > s_low:
                big_low = s_low
                Bar_big_low = Bar_s_low

            value_array_unshift(Low_ary, big_low)
            value_array_unshift(L_bar_ary, Bar_big_low)

            Structure_Trend = True
            Change_up = True
            s_high = high
            s_low = low
            Bar_s_high = bar_index
            Bar_s_low = bar_index

        if not Change_up and low <= s_low:
            s_high = high
            s_low = low
            Bar_s_high = bar_index
            Bar_s_low = bar_index

    if Structure_Trend and (not na(s_high)) and barstate.isconfirmed:
        if close < s_low:
            if high >= s_high:
                big_high = high
                Bar_big_high = bar_index
            if high < s_high:
                big_high = s_high
                Bar_big_high = Bar_s_high

            value_array_unshift(High_ary, big_high)
            value_array_unshift(H_bar_ary, Bar_big_high)

            Structure_Trend = False
            Change_down = True
            s_high = high
            s_low = low
            Bar_s_high = bar_index
            Bar_s_low = bar_index

        if not Change_down and high >= s_high:
            s_high = high
            s_low = low
            Bar_s_high = bar_index
            Bar_s_low = bar_index

    sm_line: PersistentSeries[Line] = na(Line)
    sm_line2: PersistentSeries[Line] = na(Line)
    big_line: Persistent[list[Line]] = array.new_line(7, na)

    def add_array_unshift(array__ren__, new_value_to_add):
        line.delete(array.get(array__ren__, 6))
        array.remove(array__ren__, 6)
        return array.unshift(array__ren__, new_value_to_add)

    if show_line:
        if Change_up:
            add_array_unshift(big_line, line.new(Bar_big_high[1], big_high[1], Bar_big_low, big_low, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style)))
        if Change_down:
            add_array_unshift(big_line, line.new(Bar_big_high, big_high, Bar_big_low[1], big_low[1], xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style)))

        line.delete(sm_line[1])
        line.delete(sm_line2[1])
        bb_bar = Bar_big_low if Structure_Trend else Bar_big_high
        bb_price = big_low if Structure_Trend else big_high
        cc_bar = Bar_s_high if Structure_Trend else Bar_s_low
        cc_price = s_high if Structure_Trend else s_low
        sm_line = line.new(bb_bar, bb_price, cc_bar, cc_price, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
        sm_line2 = line.new(cc_bar, cc_price, bar_index, close, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))

    atr_sl = ta.ema(ta.tr(True), length_atr)

    c_order_buy: Persistent[int] = 0
    c_order_sell: Persistent[int] = 0
    stop_loss_long: PersistentSeries[float] = 0
    stop_loss_short: PersistentSeries[float] = 0
    take_profit_long: PersistentSeries[float] = 0
    take_profit_short: PersistentSeries[float] = 0
    open_long: PersistentSeries[float] = 0
    open_short: PersistentSeries[float] = 0
    time_buy: PersistentSeries[int] = 0
    time_sell: PersistentSeries[int] = 0

    cencel_buy: bool = False
    cencel_sell: bool = False
    im_buy_signal: bool = False
    im_sell_signal: bool = False
    buy_signal: bool = False
    sell_signal: bool = False
    pending_buy: Persistent[bool] = False
    pending_sell: Persistent[bool] = False

    Fibo_1: Persistent[float] = na(float)
    Fibo_2: Persistent[float] = na(float)
    Fibo_3: Persistent[float] = na(float)
    cf_con_buy: Persistent[bool] = False
    cf_con_sell: Persistent[bool] = False
    bar_plus1: int = 1
    bar_plus: int = 2

    sl_b: Persistent[float] = na(float)
    entry_b: Persistent[float] = na(float)
    sl2_b: Persistent[float] = na(float)
    bar_sl_b: Persistent[int] = 0
    bar_entry_b: Persistent[int] = 0
    bar_sl2_b: Persistent[int] = 0
    bar_last_b: Persistent[int] = 0
    last_b: Persistent[float] = na(float)

    if strategy.position_size > 0:
        pending_buy = False
    if strategy.closedtrades > strategy.closedtrades[1] and pending_buy and barstate.isconfirmed:
        im_buy_signal = True
        pending_buy = False
    if pending_buy and con_time[1] and (not con_time) and barstate.isconfirmed:
        strategy.cancel('Long ' + string.tostring(c_order_buy))
        pending_buy = False
        cencel_buy = True

    if Change_up and array.size(High_ary) > 4:
        H_0 = array.get(High_ary, 0)
        H_1 = array.get(High_ary, 1)
        H_2 = array.get(High_ary, 2)
        L_0 = array.get(Low_ary, 0)
        L_1 = array.get(Low_ary, 1)
        L_2 = array.get(Low_ary, 2)
        L_3 = array.get(Low_ary, 3)
        L_4 = array.get(Low_ary, 4)
        bar_H_0 = array.get(H_bar_ary, 0)
        bar_H_1 = array.get(H_bar_ary, 1)
        bar_H_2 = array.get(H_bar_ary, 2)
        bar_L_0 = array.get(L_bar_ary, 0)
        bar_L_1 = array.get(L_bar_ary, 1)
        bar_L_2 = array.get(L_bar_ary, 2)

        Fibo1_more = H_0 - Swing1_more / 100 * (H_0 - L_1)
        Fibo1_less = H_0 - Swing1_less / 100 * (H_0 - L_1)
        Fibo2_more = H_0 - Swing2_more / 100 * (H_0 - L_1)
        Fibo2_less = H_0 - Swing2_less / 100 * (H_0 - L_1)
        Fibo3_more = L_1 + Swing3_more / 100 * (H_0 - L_1)
        Fibo3_less = L_1 + Swing3_less / 100 * (H_0 - L_1)
        Price_more = Size_candle_more * atr_sl + L_1
        Price_less = Size_candle_less * atr_sl + L_1

        cf_buy1 = L_0 <= Fibo1_more and L_0 >= Fibo1_less
        cf_buy2 = L_2 <= Fibo2_more and L_2 >= Fibo2_less if use_Swing2 else True
        cf_buy3 = H_1 >= Fibo3_more and H_1 <= Fibo3_less if use_Swing3 else True
        cf_buy4 = H_0 > Price_more and H_0 < Price_less if use_size else True

        if cf_buy1 and cf_buy2 and cf_buy3 and cf_buy4:
            if cf_con_sell:
                cf_con_sell = False
            if pending_sell:
                strategy.cancel('Short ' + string.tostring(c_order_sell))
                pending_sell = False
                cencel_sell = True
            if pending_buy:
                strategy.cancel('Long ' + string.tostring(c_order_buy))
                pending_buy = False
                cencel_buy = True
            if B_long and strategy.position_size == 0:
                cf_con_buy = True
                sl_b = L_0 if L_0 < L_1 else L_1
                bar_sl_b = bar_L_0 if L_0 < L_1 else bar_L_1
                sl2_b = L_1 if L_0 < L_1 else L_0
                bar_sl2_b = bar_L_1 if L_0 < L_1 else bar_L_0
                last_b = L_0
                bar_last_b = bar_L_0
                entry_b = H_0
                bar_entry_b = bar_H_0

            if B_long:
                if show_CF_fibo:
                    lbl_swing1_a = label.new(bar_L_0 + bar_plus, Fibo1_more, 'Fibo' + string.tostring(Swing1_more), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
                    lbl_swing1_b = label.new(bar_L_0 + bar_plus, Fibo1_less, 'Fibo' + string.tostring(Swing1_less), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
                    lbl_swing1_c = label.new(bar_L_0, L_0, stxt1, xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_up, size=In_Size_fibo)
                    box.new(xloc=xloc.bar_index, left=bar_L_0 - bar_plus1, top=Fibo1_more, right=bar_L_0 + bar_plus1, bottom=Fibo1_less, border_color=col_cf_con1, bgcolor=col_cf_con1)
                if use_Swing2:
                    i_Mark_2 = label.new(bar_L_2, L_2, xloc=xloc.bar_index, text='●', color=TRANSP, style=label.style_label_center, textcolor=Color_Mark_Swing_i1, size=size.small)
                    if show_CF_fibo:
                        lbl_swing2_a = label.new(bar_L_2 + bar_plus, Fibo2_more, 'Fibo' + string.tostring(Swing2_more), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
                        lbl_swing2_b = label.new(bar_L_2 + bar_plus, Fibo2_less, 'Fibo' + string.tostring(Swing2_less), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
                        lbl_swing2_c = label.new(bar_L_2, L_2, stxt2, xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_up, size=In_Size_fibo)
                        box.new(xloc=xloc.bar_index, left=bar_L_2 - bar_plus1, top=Fibo2_more, right=bar_L_2 + bar_plus1, bottom=Fibo2_less, border_color=col_cf_con1, bgcolor=col_cf_con1)
                if use_Swing3:
                    i_Mark_3 = label.new(bar_H_1, H_1, xloc=xloc.bar_index, text='●', color=TRANSP, style=label.style_label_center, textcolor=Color_Mark_Swing_i1, size=size.small)
                    if show_CF_fibo:
                        lbl_swing3_a = label.new(bar_H_1 + bar_plus, Fibo3_more, 'Fibo' + string.tostring(Swing3_more), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
                        lbl_swing3_b = label.new(bar_H_1 + bar_plus, Fibo3_less, 'Fibo' + string.tostring(Swing3_less), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
                        lbl_swing3_c = label.new(bar_H_1, H_1, stxt3, xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_down, size=In_Size_fibo)
                        box.new(xloc=xloc.bar_index, left=bar_H_1 - bar_plus1, top=Fibo3_more, right=bar_H_1 + bar_plus1, bottom=Fibo3_less, border_color=col_cf_con1, bgcolor=col_cf_con1)

                line_1 = line.new(bar_L_0, L_0, bar_H_0, H_0, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                line_2 = line.new(bar_L_1, L_1, bar_H_0, H_0, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                line_3 = line.new(bar_L_1, L_1, bar_H_1, H_1, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                line_4 = line.new(bar_L_2, L_2, bar_H_1, H_1, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                line_5 = line.new(bar_L_2, L_2, bar_H_2, H_2, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                i_Mark_1 = label.new(bar_L_0, L_0, xloc=xloc.bar_index, text='●', color=TRANSP, style=label.style_label_center, textcolor=Color_Mark_Swing_i1, size=size.small)
                i_Mark_4 = label.new(bar_H_0, H_0, xloc=xloc.bar_index, text='●', color=TRANSP, style=label.style_label_center, textcolor=Color_Mark_Swing_i2, size=size.normal)
                i_Mark_5 = label.new(bar_L_1, L_1, xloc=xloc.bar_index, text='●', color=TRANSP, style=label.style_label_center, textcolor=Color_Mark_Swing_i2, size=size.normal)
                lbl_swing_A = label.new(bar_L_1, L_1, 'Swing A', xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_up, size=In_Size_fibo)
                lbl_swing_B = label.new(bar_H_0, H_0, 'Swing B', xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_down, size=In_Size_fibo)

                if use_size and show_CF_candle:
                    line_size_1 = line.new(bar_L_1, Price_more, bar_H_0, Price_more, xloc=xloc.bar_index, color=Color_candle_2, style=get_line_style(sw_line_style))
                    line_size_2 = line.new(bar_L_1, Price_less, bar_H_0, Price_less, xloc=xloc.bar_index, color=Color_candle_1, style=get_line_style(sw_line_style))
                    lbl_size_a = label.new((bar_L_1 + bar_H_0) / 2, Price_more, 'Min', xloc=xloc.bar_index, color=Color_candle_2, textcolor=Color_candle_txt, style=label.style_label_center, size=In_Size_CF_candle)
                    label.new((bar_L_1 + bar_H_0) / 2, Price_less, 'Max', xloc=xloc.bar_index, color=Color_candle_1, textcolor=Color_candle_txt, style=label.style_label_center, size=In_Size_CF_candle)

    Line_draw_buy: bool = False
    wait_b_line: Persistent[bool] = False
    if cf_con_buy and B_long and (close >= entry_b) and barstate.isconfirmed and (strategy.position_size == 0):
        cf_con_buy = False
        Line_draw_buy = True
        wait_b_line = True
        if con_time and con_date:
            buy_signal = True

    if cf_con_buy and B_long and (close <= sl_b) and barstate.isconfirmed and (strategy.position_size == 0):
        cf_con_buy = False
        Line_draw_buy = True
        line.new(Bar_big_high, big_high, bar_last_b, last_b, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))

    if wait_b_line and Change_down and barstate.isconfirmed:
        line_last = line.new(Bar_big_high, big_high, bar_last_b, last_b, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
        wait_b_line = False

    lineB_to_CF: PersistentSeries[Line] = na(Line)
    lineB_to_cancel: PersistentSeries[Line] = na(Line)
    lblB_to_CF: PersistentSeries[Label] = na(Label)
    lblB_to_cancel: PersistentSeries[Label] = na(Label)

    if cf_con_buy and show_CF_line and barstate.isconfirmed:
        line.delete(lineB_to_CF[1])
        line.delete(lineB_to_cancel[1])
        label.delete(lblB_to_CF[1])
        label.delete(lblB_to_cancel[1])
        lineB_to_CF = line.new(bar_entry_b, entry_b, bar_index, entry_b, xloc=xloc.bar_index, color=Color_tesst_1, style=line.style_dashed)
        lineB_to_cancel = line.new(bar_sl_b, sl_b, bar_index, sl_b, xloc=xloc.bar_index, color=Color_tesst_2, style=line.style_dashed)
        lblB_to_CF = label.new(bar_index, entry_b, 'Break to confitm', xloc=xloc.bar_index, color=TRANSP, textcolor=Color_tesst_1, style=label.style_label_down, size=In_Size_CF_line)
        lblB_to_cancel = label.new(bar_index, sl_b, 'Cancel Line', xloc=xloc.bar_index, color=TRANSP, textcolor=Color_tesst_2, style=label.style_label_up, size=In_Size_CF_line)
    if Line_draw_buy and show_CF_line and barstate.isconfirmed:
        line.delete(lineB_to_CF[1])
        line.delete(lineB_to_cancel[1])
        label.delete(lblB_to_CF[1])
        label.delete(lblB_to_cancel[1])
        lineB_CF = line.new(bar_entry_b, entry_b, bar_index, entry_b, xloc=xloc.bar_index, color=Color_tesst_1, style=line.style_dashed)
        lineB_cancel = line.new(bar_sl_b, sl_b, bar_index, sl_b, xloc=xloc.bar_index, color=Color_tesst_2, style=line.style_dashed)
        lblB_cf = label.new(bar_index, entry_b, 'Break to confitm', xloc=xloc.bar_index, color=color.new('#FFFFFF00'), textcolor=Color_tesst_1, style=label.style_label_down, size=In_Size_CF_line)
        label.new(bar_index, sl_b, 'Cancel Line', xloc=xloc.bar_index, color=color.new('#FFFFFF00'), textcolor=Color_tesst_2, style=label.style_label_up, size=In_Size_CF_line)

    sl_s: Persistent[float] = na(float)
    entry_s: Persistent[float] = na(float)
    sl2_s: Persistent[float] = na(float)
    bar_sl_s: Persistent[int] = 0
    bar_entry_s: Persistent[int] = 0
    bar_sl2_s: Persistent[int] = 0
    last_s: Persistent[float] = na(float)
    bar_last_s: Persistent[int] = 0

    if strategy.position_size < 0:
        pending_sell = False
    if strategy.closedtrades > strategy.closedtrades[1] and pending_sell and barstate.isconfirmed:
        im_sell_signal = True
        pending_sell = False
    if pending_sell and con_time[1] and (not con_time) and barstate.isconfirmed:
        strategy.cancel('Short ' + string.tostring(c_order_sell))
        pending_sell = False
        cencel_sell = True

    if Change_down and array.size(Low_ary) > 4:
        H_0 = array.get(High_ary, 0)
        H_1 = array.get(High_ary, 1)
        H_2 = array.get(High_ary, 2)
        H_3 = array.get(High_ary, 3)
        H_4 = array.get(High_ary, 4)
        L_0 = array.get(Low_ary, 0)
        L_1 = array.get(Low_ary, 1)
        L_2 = array.get(Low_ary, 2)
        bar_H_0 = array.get(H_bar_ary, 0)
        bar_H_1 = array.get(H_bar_ary, 1)
        bar_H_2 = array.get(H_bar_ary, 2)
        bar_L_0 = array.get(L_bar_ary, 0)
        bar_L_1 = array.get(L_bar_ary, 1)
        bar_L_2 = array.get(L_bar_ary, 2)

        Fibo1_more = L_0 + Swing1_more / 100 * (H_1 - L_0)
        Fibo1_less = L_0 + Swing1_less / 100 * (H_1 - L_0)
        Fibo2_more = L_0 + Swing2_more / 100 * (H_1 - L_0)
        Fibo2_less = L_0 + Swing2_less / 100 * (H_1 - L_0)
        Fibo3_more = H_1 - Swing3_more / 100 * (H_1 - L_0)
        Fibo3_less = H_1 - Swing3_less / 100 * (H_1 - L_0)
        Price_more = H_1 - Size_candle_more * atr_sl
        Price_less = H_1 - Size_candle_less * atr_sl

        cf_sell1 = H_0 >= Fibo1_more and H_0 <= Fibo1_less
        cf_sell2 = H_2 >= Fibo2_more and H_2 <= Fibo2_less if use_Swing2 else True
        cf_sell3 = L_1 <= Fibo3_more and L_1 >= Fibo3_less if use_Swing3 else True
        cf_sell4 = L_0 <= Price_more and L_0 >= Price_less if use_size else True

        if cf_sell1 and cf_sell2 and cf_sell3 and cf_sell4:
            if cf_con_buy:
                cf_con_buy = False
            if pending_buy:
                strategy.cancel('Long ' + string.tostring(c_order_buy))
                pending_buy = False
                cencel_buy = True
            if pending_sell:
                strategy.cancel('Short ' + string.tostring(c_order_sell))
                pending_sell = False
                cencel_sell = True
            if S_short and strategy.position_size == 0:
                cf_con_sell = True
                sl_s = H_0 if H_0 > H_1 else H_1
                bar_sl_s = bar_H_0 if H_0 > H_1 else bar_H_1
                sl2_s = H_1 if H_0 > H_1 else H_0
                bar_sl2_s = bar_H_1 if H_0 > H_1 else bar_H_0
                last_s = H_0
                bar_last_s = bar_H_0
                entry_s = L_0
                bar_entry_s = bar_L_0

            if S_short:
                if show_CF_fibo:
                    lbl_swing1_a = label.new(bar_H_0 + bar_plus, Fibo1_more, 'Fibo' + string.tostring(Swing1_more), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
                    lbl_swing1_b = label.new(bar_H_0 + bar_plus, Fibo1_less, 'Fibo' + string.tostring(Swing1_less), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
                    lbl_swing1_c = label.new(bar_H_0, H_0, stxt1, xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_down, size=In_Size_fibo)
                    box.new(xloc=xloc.bar_index, left=bar_H_0 - bar_plus1, top=Fibo1_more, right=bar_H_0 + bar_plus1, bottom=Fibo1_less, border_color=col_cf_con2, bgcolor=col_cf_con2)
                if use_Swing2:
                    i_Mark_2 = label.new(bar_H_2, H_2, xloc=xloc.bar_index, text='●', color=TRANSP, style=label.style_label_center, textcolor=Color_Mark_Swing_i1, size=size.small)
                    if show_CF_fibo:
                        lbl_swing2_a = label.new(bar_H_2 + bar_plus, Fibo2_more, 'Fibo' + string.tostring(Swing2_more), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
                        lbl_swing2_b = label.new(bar_H_2 + bar_plus, Fibo2_less, 'Fibo' + string.tostring(Swing2_less), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
                        lbl_swing2_c = label.new(bar_H_2, H_2, stxt2, xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_down, size=In_Size_fibo)
                        box.new(xloc=xloc.bar_index, left=bar_H_2 - bar_plus1, top=Fibo2_more, right=bar_H_2 + bar_plus1, bottom=Fibo2_less, border_color=col_cf_con2, bgcolor=col_cf_con2)
                if use_Swing3:
                    i_Mark_3 = label.new(bar_L_1, L_1, xloc=xloc.bar_index, text='●', color=TRANSP, style=label.style_label_center, textcolor=Color_Mark_Swing_i1, size=size.small)
                    if show_CF_fibo:
                        lbl_swing3_a = label.new(bar_L_1 + bar_plus, Fibo3_more, 'Fibo' + string.tostring(Swing3_more), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
                        lbl_swing3_b = label.new(bar_L_1 + bar_plus, Fibo3_less, 'Fibo' + string.tostring(Swing3_less), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
                        lbl_swing3_c = label.new(bar_L_1, L_1, stxt3, xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_up, size=In_Size_fibo)
                        box.new(xloc=xloc.bar_index, left=bar_L_1 - bar_plus1, top=Fibo3_more, right=bar_L_1 + bar_plus1, bottom=Fibo3_less, border_color=col_cf_con2, bgcolor=col_cf_con2)

                line_1 = line.new(bar_H_0, H_0, bar_L_0, L_0, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                line_2 = line.new(bar_H_1, H_1, bar_L_0, L_0, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                line_3 = line.new(bar_H_1, H_1, bar_L_1, L_1, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                line_4 = line.new(bar_H_2, H_2, bar_L_1, L_1, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                line_5 = line.new(bar_H_2, H_2, bar_L_2, L_2, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))

                i_Mark_1 = label.new(bar_H_0, H_0, xloc=xloc.bar_index, text='●', color=TRANSP, style=label.style_label_center, textcolor=Color_Mark_Swing_i1, size=size.small)
                i_Mark_4 = label.new(bar_L_0, L_0, xloc=xloc.bar_index, text='●', color=TRANSP, style=label.style_label_center, textcolor=Color_Mark_Swing_i2, size=size.normal)
                i_Mark_5 = label.new(bar_H_1, H_1, xloc=xloc.bar_index, text='●', color=TRANSP, style=label.style_label_center, textcolor=Color_Mark_Swing_i2, size=size.normal)

                lbl_swing_A = label.new(bar_H_1, H_1, 'Swing A', xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_down, size=In_Size_fibo)
                lbl_swing_B = label.new(bar_L_0, L_0, 'Swing B', xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_up, size=In_Size_fibo)

                if use_size and show_CF_candle:
                    line_size_1 = line.new(bar_H_1, Price_more, bar_L_0, Price_more, xloc=xloc.bar_index, color=Color_candle_2, style=get_line_style(sw_line_style))
                    line_size_2 = line.new(bar_H_1, Price_less, bar_L_0, Price_less, xloc=xloc.bar_index, color=Color_candle_1, style=get_line_style(sw_line_style))
                    lbl_size_a = label.new((bar_H_1 + bar_L_0) / 2, Price_more, 'Min', xloc=xloc.bar_index, color=Color_candle_2, textcolor=Color_candle_txt, style=label.style_label_center, size=In_Size_CF_candle)
                    label.new((bar_H_1 + bar_L_0) / 2, Price_less, 'Max', xloc=xloc.bar_index, color=Color_candle_1, textcolor=Color_candle_txt, style=label.style_label_center, size=In_Size_CF_candle)

    Line_draw_sell: bool = False
    wait_s_line: Persistent[bool] = False
    if cf_con_sell and S_short and (close <= entry_s) and barstate.isconfirmed and (strategy.position_size == 0):
        cf_con_sell = False
        Line_draw_sell = True
        wait_s_line = True
        if con_time and con_date:
            sell_signal = True

    if cf_con_sell and S_short and (close >= sl_s) and barstate.isconfirmed and (strategy.position_size == 0):
        cf_con_sell = False
        Line_draw_sell = True
        line.new(Bar_big_low, big_low, bar_last_s, last_s, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))

    if wait_s_line and Change_up and barstate.isconfirmed:
        line_last = line.new(Bar_big_low, big_low, bar_last_s, last_s, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
        wait_s_line = False

    lineS_to_CF: PersistentSeries[Line] = na(Line)
    lineS_to_cancel: PersistentSeries[Line] = na(Line)
    lblS_to_CF: PersistentSeries[Label] = na(Label)
    lblS_to_cancel: PersistentSeries[Label] = na(Label)
    if cf_con_sell and show_CF_line and barstate.isconfirmed:
        line.delete(lineS_to_CF[1])
        line.delete(lineS_to_cancel[1])
        label.delete(lblS_to_CF[1])
        label.delete(lblS_to_cancel[1])
        lineS_to_CF = line.new(bar_entry_s, entry_s, bar_index, entry_s, xloc=xloc.bar_index, color=Color_tesst_1, style=line.style_dashed)
        lineS_to_cancel = line.new(bar_sl_s, sl_s, bar_index, sl_s, xloc=xloc.bar_index, color=Color_tesst_2, style=line.style_dashed)
        lblS_to_CF = label.new(bar_index, entry_s, 'Break to confitm', xloc=xloc.bar_index, color=TRANSP, textcolor=Color_tesst_1, style=label.style_label_up, size=In_Size_CF_line)
        lblS_to_cancel = label.new(bar_index, sl_s, 'Cancel Line', xloc=xloc.bar_index, color=TRANSP, textcolor=Color_tesst_2, style=label.style_label_down, size=In_Size_CF_line)
    if Line_draw_sell and show_CF_line and barstate.isconfirmed:
        line.delete(lineS_to_CF[1])
        line.delete(lineS_to_cancel[1])
        label.delete(lblS_to_CF[1])
        label.delete(lblS_to_cancel[1])
        lineS_CF = line.new(bar_entry_s, entry_s, bar_index, entry_s, xloc=xloc.bar_index, color=Color_tesst_1, style=line.style_dashed)
        lineS_cancel = line.new(bar_sl_s, sl_s, bar_index, sl_s, xloc=xloc.bar_index, color=Color_tesst_2, style=line.style_dashed)
        lblS_cf = label.new(bar_index, entry_s, 'Break to confitm', xloc=xloc.bar_index, color=TRANSP, textcolor=Color_tesst_1, style=label.style_label_up, size=In_Size_CF_line)
        label.new(bar_index, sl_s, 'Cancel Line', xloc=xloc.bar_index, color=TRANSP, textcolor=Color_tesst_2, style=label.style_label_down, size=In_Size_CF_line)

    risk_pips = atr_sl * x_ATR
    def value_remove2(va1, va2, size__ren__):
        array.remove(va1, size__ren__)
        return array.remove(va2, size__ren__)

    tp_buy: Persistent[list[float]] = array.new_float(0, na)
    sl_buy: Persistent[list[float]] = array.new_float(0, na)
    tp_sell: Persistent[list[float]] = array.new_float(0, na)
    sl_sell: Persistent[list[float]] = array.new_float(0, na)

    Loss_Buy: Persistent[int] = 0
    Win_Buy: Persistent[int] = 0
    sl_trade_buy: Persistent[float] = na(float)
    tp_trade_buy: Persistent[float] = na(float)
    Loss_Sell: Persistent[int] = 0
    Win_Sell: Persistent[int] = 0
    sl_trade_sell: Persistent[float] = na(float)
    tp_trade_sell: Persistent[float] = na(float)

    if cencel_buy and array.size(tp_buy) > 0:
        tp_trade_buy = na
        sl_trade_buy = na
        for i in pine_range(array.size(tp_buy) - 1, 0):
            value_remove2(tp_buy, sl_buy, i)
    if cencel_sell and array.size(tp_sell) > 0:
        tp_trade_sell = na
        sl_trade_sell = na
        for i in pine_range(array.size(tp_sell) - 1, 0):
            value_remove2(tp_sell, sl_sell, i)

    if buy_signal and con_time and con_date and barstate.isconfirmed:
        sl_cal_long = sl2_b if Sl_change else sl_b
        open_long = entry_b - math.abs(fibo_entry / 100 * (entry_b - sl_cal_long))
        stop_loss_long = sl_cal_long - risk_pips
        take_profit_long = open_long + (open_long - stop_loss_long) * rr_ratio
        c_order_buy += 1
        cs_buy = string.tostring(c_order_buy)
        strategy.entry('Long ' + cs_buy, strategy.long, na, limit=open_long)
        strategy.exit('Long Exit ' + cs_buy, 'Long ' + cs_buy, stop=stop_loss_long, limit=take_profit_long, comment_profit='Long(Tp) ' + cs_buy, comment_loss='Long(SL) ' + cs_buy)
        p_entry = '\n\nEntry price = ' + string.tostring(open_long, format.mintick)
        p_sl = '\n\nStop loss = ' + string.tostring(stop_loss_long, format.mintick)
        p_tp = '\n\nTarget profit = ' + string.tostring(take_profit_long, format.mintick)
        alert('Long_' + p_entry + p_sl + p_tp, alert.freq_all)
        pending_buy = True
        time_buy = bar_index
        array.unshift(tp_buy, take_profit_long)
        array.unshift(sl_buy, stop_loss_long)

    if sell_signal and con_time and con_date and barstate.isconfirmed:
        sl_cal_short = sl2_s if Sl_change else sl_s
        open_short = entry_s + fibo_entry / 100 * (sl_cal_short - entry_s)
        stop_loss_short = sl_cal_short + risk_pips
        take_profit_short = open_short - (stop_loss_short - open_short) * rr_ratio
        c_order_sell += 1
        cs_sell = string.tostring(c_order_sell)
        strategy.entry('Short ' + cs_sell, strategy.short, na, limit=open_short)
        strategy.exit('Short Exit ' + cs_sell, 'Short ' + cs_sell, stop=stop_loss_short, limit=take_profit_short, comment_profit='Short(Tp) ' + cs_sell, comment_loss='Short(SL) ' + cs_sell)
        p_entry = '\n\nEntry price = ' + string.tostring(open_short, format.mintick)
        p_sl = '\n\nStop loss = ' + string.tostring(stop_loss_short, format.mintick)
        p_tp = '\n\nTarget profit = ' + string.tostring(take_profit_short, format.mintick)
        alert('Short_' + p_entry + p_sl + p_tp, alert.freq_all)
        pending_sell = True
        time_sell = bar_index
        array.unshift(tp_sell, take_profit_short)
        array.unshift(sl_sell, stop_loss_short)

    n_bar: int = 5
    col_1 = color.rgb(8, 153, 129, 80)
    col_2 = color.rgb(242, 54, 70, 80)

    box_entrybuy_1_his: Series[Box] = na(Box)
    box_entrybuy_2_his: Series[Box] = na(Box)
    box_entrysell_1_his: Series[Box] = na(Box)
    box_entrysell_2_his: Series[Box] = na(Box)
    lbl_entry_his: Series[Label] = na(Label)
    lbl_tp_his: Series[Label] = na(Label)
    lbl_sl_his: Series[Label] = na(Label)

    lbl_entry_t: PersistentSeries[Label] = na(Label)
    lbl_tp_t: PersistentSeries[Label] = na(Label)
    lbl_sl_t: PersistentSeries[Label] = na(Label)
    box_entry_t1: PersistentSeries[Box] = na(Box)
    box_entry_t2: PersistentSeries[Box] = na(Box)

    if strategy.position_size > 0 or (im_buy_signal and barstate.isconfirmed):
        box.delete(box_entry_t1[1])
        box.delete(box_entry_t2[1])
        label.delete(lbl_entry_t[1])
        label.delete(lbl_tp_t[1])
        label.delete(lbl_sl_t[1])
        box.delete(box_entrybuy_1_his[1])
        box.delete(box_entrybuy_2_his[1])
        label.delete(lbl_entry_his[1])
        label.delete(lbl_tp_his[1])
        label.delete(lbl_sl_his[1])
        box_entrybuy_1_his = box.new(xloc=xloc.bar_index, left=time_buy, top=take_profit_long, right=bar_index + n_bar, bottom=open_long, border_color=col_1, bgcolor=col_1)
        box_entrybuy_2_his = box.new(xloc=xloc.bar_index, left=time_buy, top=open_long, right=bar_index + n_bar, bottom=stop_loss_long, border_color=col_2, bgcolor=col_2)
        lbl_entry_his = label.new(bar_index + n_bar, open_long, string.tostring(open_long, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
        lbl_tp_his = label.new(bar_index + n_bar, take_profit_long, string.tostring(take_profit_long, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
        lbl_sl_his = label.new(bar_index + n_bar, stop_loss_long, string.tostring(stop_loss_long, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
    if cencel_buy and barstate.isconfirmed:
        box.delete(box_entry_t1[1])
        box.delete(box_entry_t2[1])
        label.delete(lbl_entry_t[1])
        label.delete(lbl_tp_t[1])
        label.delete(lbl_sl_t[1])
        box.delete(box_entrybuy_1_his[1])
        box.delete(box_entrybuy_2_his[1])
        label.delete(lbl_entry_his[1])
        label.delete(lbl_tp_his[1])
        label.delete(lbl_sl_his[1])
        box_entrybuy_1_his = box.new(xloc=xloc.bar_index, left=time_buy[1], top=take_profit_long[1], right=time_buy[1] + n_bar, bottom=open_long[1], border_color=col_1, bgcolor=col_1)
        box_entrybuy_2_his = box.new(xloc=xloc.bar_index, left=time_buy[1], top=open_long[1], right=time_buy[1] + n_bar, bottom=stop_loss_long[1], border_color=col_2, bgcolor=col_2)
        lbl_entry_his = label.new(time_buy[1] + n_bar, open_long[1], string.tostring(open_long[1], format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
        lbl_tp_his = label.new(time_buy[1] + n_bar, take_profit_long[1], string.tostring(take_profit_long[1], format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
        lbl_sl_his = label.new(time_buy[1] + n_bar, stop_loss_long[1], string.tostring(stop_loss_long[1], format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)

    if strategy.position_size < 0 or (im_sell_signal and barstate.isconfirmed):
        box.delete(box_entry_t1[1])
        box.delete(box_entry_t2[1])
        label.delete(lbl_entry_t[1])
        label.delete(lbl_tp_t[1])
        label.delete(lbl_sl_t[1])
        box.delete(box_entrysell_1_his[1])
        box.delete(box_entrysell_2_his[1])
        label.delete(lbl_entry_his[1])
        label.delete(lbl_tp_his[1])
        label.delete(lbl_sl_his[1])
        box_entrysell_1_his = box.new(xloc=xloc.bar_index, left=time_sell, top=take_profit_short, right=bar_index + n_bar, bottom=open_short, border_color=col_1, bgcolor=col_1)
        box_entrysell_2_his = box.new(xloc=xloc.bar_index, left=time_sell, top=open_short, right=bar_index + n_bar, bottom=stop_loss_short, border_color=col_2, bgcolor=col_2)
        lbl_entry_his = label.new(bar_index + n_bar, open_short, string.tostring(open_short, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
        lbl_tp_his = label.new(bar_index + n_bar, take_profit_short, string.tostring(take_profit_short, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
        lbl_sl_his = label.new(bar_index + n_bar, stop_loss_short, string.tostring(stop_loss_short, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
    if cencel_sell and barstate.isconfirmed:
        box.delete(box_entry_t1[1])
        box.delete(box_entry_t2[1])
        label.delete(lbl_entry_t[1])
        label.delete(lbl_tp_t[1])
        label.delete(lbl_sl_t[1])
        box.delete(box_entrysell_1_his[1])
        box.delete(box_entrysell_2_his[1])
        label.delete(lbl_entry_his[1])
        label.delete(lbl_tp_his[1])
        label.delete(lbl_sl_his[1])
        box_entrysell_1_his = box.new(xloc=xloc.bar_index, left=time_sell[1], top=take_profit_short[1], right=time_sell[1] + n_bar, bottom=open_short[1], border_color=col_1, bgcolor=col_1)
        box_entrysell_2_his = box.new(xloc=xloc.bar_index, left=time_sell[1], top=open_short[1], right=time_sell[1] + n_bar, bottom=stop_loss_short[1], border_color=col_2, bgcolor=col_2)
        lbl_entry_his = label.new(time_sell[1] + n_bar, open_short[1], string.tostring(open_short[1], format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
        lbl_tp_his = label.new(time_sell[1] + n_bar, take_profit_short[1], string.tostring(take_profit_short[1], format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
        lbl_sl_his = label.new(time_sell[1] + n_bar, stop_loss_short[1], string.tostring(stop_loss_short[1], format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)

    if buy_signal and barstate.isconfirmed:
        box.delete(box_entry_t1[1])
        box.delete(box_entry_t2[1])
        label.delete(lbl_entry_t[1])
        label.delete(lbl_tp_t[1])
        label.delete(lbl_sl_t[1])
        box_entry_t1 = box.new(xloc=xloc.bar_index, left=time_buy, top=take_profit_long, right=bar_index + n_bar, bottom=open_long, border_color=col_1, bgcolor=col_1)
        box_entry_t2 = box.new(xloc=xloc.bar_index, left=time_buy, top=open_long, right=bar_index + n_bar, bottom=stop_loss_long, border_color=col_2, bgcolor=col_2)
        lbl_entry_t = label.new(bar_index + n_bar, open_long, string.tostring(open_long, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
        lbl_tp_t = label.new(bar_index + n_bar, take_profit_long, string.tostring(take_profit_long, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
        lbl_sl_t = label.new(bar_index + n_bar, stop_loss_long, string.tostring(stop_loss_long, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
    if sell_signal and barstate.isconfirmed:
        box.delete(box_entrysell_1_his[1])
        box.delete(box_entry_t2[1])
        label.delete(lbl_entry_t[1])
        label.delete(lbl_tp_t[1])
        label.delete(lbl_sl_t[1])
        box_entry_t1 = box.new(xloc=xloc.bar_index, left=time_sell, top=take_profit_short, right=bar_index + n_bar, bottom=open_short, border_color=col_1, bgcolor=col_1)
        box_entry_t2 = box.new(xloc=xloc.bar_index, left=time_sell, top=open_short, right=bar_index + n_bar, bottom=stop_loss_short, border_color=col_2, bgcolor=col_2)
        lbl_entry_t = label.new(bar_index + n_bar, open_short, string.tostring(open_short, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
        lbl_tp_t = label.new(bar_index + n_bar, take_profit_short, string.tostring(take_profit_short, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)
        lbl_sl_t = label.new(bar_index + n_bar, stop_loss_short, string.tostring(stop_loss_short, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=text_line2_col, style=label.style_label_center, size=In_Size_fibo)

    if Show_result and barstate.isconfirmed:
        if array.size(sl_buy) > 0 and (not na(array.get(sl_buy, 0))):
            sl_trade_buy = array.get(sl_buy, 0)
        if low <= sl_trade_buy and (strategy.position_size[1] > 0 or im_buy_signal) and (array.size(sl_buy) > 0):
            sl_trade_buy = na
            tp_trade_buy = na
            for i in pine_range(array.size(sl_buy) - 1, 0):
                if low <= array.get(sl_buy, i) and (not na(array.get(sl_buy, i))):
                    Loss_Buy += 1
                    value_remove2(tp_buy, sl_buy, i)

        if array.size(tp_buy) > 0 and (not na(array.get(tp_buy, 0))):
            tp_trade_buy = array.get(tp_buy, 0)
        if high >= tp_trade_buy and (strategy.position_size[1] > 0 or im_buy_signal) and (array.size(tp_buy) > 0):
            tp_trade_buy = na
            sl_trade_buy = na
            for i in pine_range(array.size(tp_buy) - 1, 0):
                if high >= array.get(tp_buy, i) and (not na(array.get(tp_buy, i))):
                    Win_Buy += 1
                    value_remove2(tp_buy, sl_buy, i)

        if array.size(sl_sell) > 0 and (not na(array.get(sl_sell, 0))):
            sl_trade_sell = array.get(sl_sell, 0)
        if high >= sl_trade_sell and (strategy.position_size[1] < 0 or im_sell_signal) and (array.size(sl_sell) > 0):
            sl_trade_sell = na
            tp_trade_sell = na
            for i in pine_range(array.size(sl_sell) - 1, 0):
                if high >= array.get(sl_sell, i) and (not na(array.get(sl_sell, i))):
                    Loss_Sell += 1
                    value_remove2(tp_sell, sl_sell, i)

        if array.size(tp_sell) > 0 and (not na(array.get(tp_sell, 0))):
            tp_trade_sell = array.get(tp_sell, 0)
        if low <= tp_trade_sell and (strategy.position_size[1] < 0 or im_sell_signal) and (array.size(tp_sell) > 0):
            tp_trade_sell = na
            sl_trade_sell = na
            for i in pine_range(array.size(tp_sell) - 1, 0):
                if low <= array.get(tp_sell, i) and (not na(array.get(tp_sell, i))):
                    Win_Sell += 1
                    value_remove2(tp_sell, sl_sell, i)

    bgcolor(color.rgb(255, 251, 0, 92) if s_New_York and cf_ses1 else na, title='New York')
    bgcolor(color.rgb(255, 0, 255, 92) if s_London and cf_ses2 else na, title='London')
    bgcolor(color.rgb(111, 255, 82, 92) if s_Tokyo and cf_ses3 else na, title='Tokyo')
    bgcolor(color.rgb(82, 122, 255, 92) if s_Sydney and cf_ses4 else na, title='Sydney')

    Location_session = 9 * 60 * 60 / timeframe.in_seconds(timeframe.period) / 2
    Lbl_New_York = not cf_ses1 and cf_ses1 != cf_ses1[1] and s_New_York and (t_New == '1300-2200') and (timeframe.in_seconds(timeframe.period) <= 32400)
    plotshape(Lbl_New_York, 'Session New York', shape.labeldown, location.bottom, na, offset=-Location_session, text='New York', textcolor=color.new('#FFFB00'), size=size.tiny, display=display.all - display.status_line, editable=False)
    Lbl_London = not cf_ses2 and cf_ses2 != cf_ses2[1] and s_London and (t_Lon == '0700-1600') and (timeframe.in_seconds(timeframe.period) <= 32400)
    plotshape(Lbl_London, 'Session London', shape.labeldown, location.bottom, na, offset=-Location_session, text='London', textcolor=color.new('#FF00FF'), size=size.tiny, display=display.all - display.status_line, editable=False)
    Lbl_Tokyo = not cf_ses3 and cf_ses3 != cf_ses3[1] and s_Tokyo and (t_Tokyo == '0000-0900') and (timeframe.in_seconds(timeframe.period) <= 32400)
    plotshape(Lbl_Tokyo, 'Session Tokyo', shape.labeldown, location.bottom, na, offset=-Location_session, text='Tokyo', textcolor=color.new('#6FFF52'), size=size.tiny, display=display.all - display.status_line, editable=False)
    Lbl_Sydney = not cf_ses4 and cf_ses4 != cf_ses4[1] and s_Sydney and (t_Syd == '2100-0600') and (timeframe.in_seconds(timeframe.period) <= 32400)
    plotshape(Lbl_Sydney, 'Session Sydney', shape.labeldown, location.bottom, na, offset=-Location_session, text='Sydney', textcolor=color.new('#527AFF'), size=size.tiny, display=display.all - display.status_line, editable=False)

    Balane_status: Persistent[Table] = table.new(position__global__(select_position), 6, 6, border_width=1)

    Total_all: Series = Win_Buy + Loss_Buy + Win_Sell + Loss_Sell
    if Show_result and Total_all > Total_all[1] and barstate.isconfirmed:
        Long_all = Win_Buy + Loss_Buy
        Short_all = Win_Sell + Loss_Sell
        Total_win = Win_Buy + Win_Sell
        Total_loss = Loss_Buy + Loss_Sell
        Factor_all = Total_win * rr_ratio / Total_loss
        Factor_buy = Win_Buy * rr_ratio / Loss_Buy
        Factor_sell = Win_Sell * rr_ratio / Loss_Sell
        txt1_1 = string.tostring(Total_all, format.volume)
        txt1_2 = string.tostring(Long_all, format.volume)
        txt1_3 = string.tostring(Short_all, format.volume)
        txt2_1 = string.tostring(Total_win, format.volume)
        txt3_1 = string.tostring(Total_loss, format.volume)
        txt4_1 = string.tostring(Total_win / Total_all * 100, format.percent)
        txt5_1 = string.format('{0,number,#.##}', Factor_all)

        txt2_2 = string.tostring(Win_Buy, format.volume)
        txt3_2 = string.tostring(Loss_Buy, format.volume)
        txt4_2 = string.tostring(Win_Buy / Long_all * 100, format.percent)
        txt5_2 = string.format('{0,number,#.##}', Factor_buy)

        txt2_3 = string.tostring(Win_Sell, format.volume)
        txt3_3 = string.tostring(Loss_Sell, format.volume)
        txt4_3 = string.tostring(Win_Sell / Short_all * 100, format.percent)
        txt5_3 = string.format('{0,number,#.##}', Factor_sell)

        Factor_all_color = Factor_up_color if Factor_all > Factor_up else Factor_donw_color if Factor_all < Factor_donw else color.white
        Factor_buy_color = Factor_up_color if Factor_buy > Factor_up else Factor_donw_color if Factor_buy < Factor_donw else color.white
        Factor_sell_color = Factor_up_color if Factor_sell > Factor_up else Factor_donw_color if Factor_sell < Factor_donw else color.white

        table.cell(Balane_status, 1, 1, txt1_1, bgcolor=color.black, text_color=Factor_all_color)
        table.cell(Balane_status, 2, 1, txt2_1, bgcolor=color.black, text_color=Factor_all_color)
        table.cell(Balane_status, 3, 1, txt3_1, bgcolor=color.black, text_color=Factor_all_color)
        table.cell(Balane_status, 4, 1, txt4_1, bgcolor=color.black, text_color=Factor_all_color)
        table.cell(Balane_status, 5, 1, txt5_1, bgcolor=color.black, text_color=Factor_all_color)

        table.cell(Balane_status, 1, 2, txt1_2, bgcolor=color.black, text_color=Factor_buy_color)
        table.cell(Balane_status, 2, 2, txt2_2, bgcolor=color.black, text_color=Factor_buy_color)
        table.cell(Balane_status, 3, 2, txt3_2, bgcolor=color.black, text_color=Factor_buy_color)
        table.cell(Balane_status, 4, 2, txt4_2, bgcolor=color.black, text_color=Factor_buy_color)
        table.cell(Balane_status, 5, 2, txt5_2, bgcolor=color.black, text_color=Factor_buy_color)

        table.cell(Balane_status, 1, 3, txt1_3, bgcolor=color.black, text_color=Factor_sell_color)
        table.cell(Balane_status, 2, 3, txt2_3, bgcolor=color.black, text_color=Factor_sell_color)
        table.cell(Balane_status, 3, 3, txt3_3, bgcolor=color.black, text_color=Factor_sell_color)
        table.cell(Balane_status, 4, 3, txt4_3, bgcolor=color.black, text_color=Factor_sell_color)
        table.cell(Balane_status, 5, 3, txt5_3, bgcolor=color.black, text_color=Factor_sell_color)

        table.cell(Balane_status, 0, 1, 'Total', bgcolor=color.black, text_color=color.white)
        table.cell(Balane_status, 0, 2, 'Long', bgcolor=color.black, text_color=color.white)
        table.cell(Balane_status, 0, 3, 'Short', bgcolor=color.black, text_color=color.white)
        table.cell(Balane_status, 1, 0, 'All', bgcolor=color.black, text_color=color.white)
        table.cell(Balane_status, 2, 0, 'Win', bgcolor=color.black, text_color=color.white)
        table.cell(Balane_status, 3, 0, 'Loss', bgcolor=color.black, text_color=color.white)
        table.cell(Balane_status, 4, 0, 'Winrate', bgcolor=color.black, text_color=color.white)
        table.cell(Balane_status, 5, 0, 'Profit\nFactor', bgcolor=color.black, text_color=color.white)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
