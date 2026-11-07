"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alert, array, bar_index, barstate, bgcolor, box, close, color, display,
    format, high, input, label, last_bar_time, line, location, low, math, na, open, plot,
    plotshape, position, script, shape, size, strategy, string, ta, table, text, time, timeframe,
    timestamp, xloc
)
from pynecore.types import Box, Color, Label, Line, Persistent, PersistentSeries, Series, Table

Entry_Position: str = "========= Entry Condition ========="
Time_Filter: str = "========== Time Filter =========="
display_group: str = "========= Display FVG and iFVG ========="
liquidity: str = "===== Display Liquidity and Swing ====="
Internal: str = "=========== Display Structure ==========="
result_group: str = "========== Trading Result Table =========="
Display_Entry: str = "============= Display Entry Box ============="


@script.strategy("ICT Entry V2 [TS_Indie]", overlay=True, max_labels_count=500, max_lines_count=500, max_boxes_count=500, max_bars_back=5000, margin_long=0, margin_short=0, initial_capital=100000)
def main(
    rr_ratio=input.float(3, "Risk Reward Ratio", step=0.1, inline="0.1", group=Entry_Position),
    length_atr=input.int(title="Stop loss ATR", defval=50, minval=1, inline="0.2", group=Entry_Position),
    x_ATR=input.float(0.5, "X", step=0.1, inline="0.2", tooltip='Stop loss ATR 50 is the average ATR over 50 candles, which is then multiplied by the value in the second field to calculate the stop loss. \n\n (If the second field is set to 0, this function will be disabled.)', group=Entry_Position),
    fibo_entry=input.float(0, "Entry Zone", step=1, inline="0.21", tooltip='Set the entry zone within the FVG where the order will be placed. \n\n For example, if the value is set to 50, the order will be placed at the midpoint of the FVG.', group=Entry_Position),
    iFVG_be_FVG=input.bool(False, " iFVG Overlap FVGㅤㅤ", inline="0.212", group=Entry_Position),
    Con_FVG_mix=input.bool(False, "Mix ", inline="0.212", tooltip='"iFVG Overlap FVG is false" For example, on the Buy side: the lower iFVG box must be higher than the upper FVG box. \n\n When "iFVG Overlap FVG is false", the lower iFVG box must be lower than the upper FVG box. \n\n When “Mix is true” is enabled, both conditions will be accepted and filtered together.', group=Entry_Position),
    FVG_min_ATR=input.float(0.01, "Gap Min", step=0.1, inline="0.215", group=Entry_Position),
    FVG_max_ATR=input.float(0.2, "Max", step=0.1, inline="0.215", tooltip='Filter the gap between FVG and iFVG according to the trading system rules. \n\n The gap must be greater than Min x ATR[50] and less than Max x ATR[50].', group=Entry_Position),
    Filter_size_FVG=input.bool(False, 'Filter Size FVG for entry signals', inline="0.22", tooltip='Filter the size of FVG by setting Min and Max values below', group=Entry_Position),
    FVG_min=input.float(0.1, "Min", step=0.1, inline="0.23", group=Entry_Position),
    FVG_max=input.float(0.5, "Max", step=0.1, inline="0.23", tooltip='The Min & Max values will be multiplied by the ATR 50 average and compared with the FVG size. \n\n The FVG size must be greater than (Min x ATR[50]) and less than (Max x ATR[50]).', group=Entry_Position),
    Filter_size_iFVG=input.bool(False, 'Filter Size iFVG for entry signals', inline="0.232", tooltip='Filter the size of iFVG by setting Min and Max values below', group=Entry_Position),
    iFVG_min=input.float(0.1, "Min", step=0.1, inline="0.233", group=Entry_Position),
    iFVG_max=input.float(0.5, "Max", step=0.1, inline="0.233", tooltip='The Min & Max values will be multiplied by the ATR 50 average and compared with the iFVG size. \n\n The iFVG size must be greater than (Min x ATR[50]) and less than (Max x ATR[50]).', group=Entry_Position),
    Len=input.int(title="Liquidity Pivot Strength", defval=5, minval=1, inline="0.3", tooltip='This mechanism is derived from the indicator “Smallest Swing [Truth Indie]”. \n\n As the value increases, the strength of the swing increases, resulting in larger swings, which may also affect liquidity.', group=Entry_Position),
    Follow_trend=input.bool(True, "Trend Following Conditions", inline="0.35", tooltip='When enabled, orders are placed only in the direction of the trend (Buy in bullish trend, Sell in bearish trend). \n\n When disabled, orders are placed without trend filtering.', group=Entry_Position),
    Len_in=input.int(title="Strength", defval=10, minval=1, inline="0.4", group=Entry_Position),
    valid_con=input.string(defval='Close', title='Valid by', options=('Close', 'High/Low'), inline='0.4', tooltip='The Strength parameter represents the pivot length mechanism, used in combination with price action.\n\n It validates a swing by detecting a structure break formed by candles making new highs or new lows.\n\n The break can be defined using either the candle body or the wick.', group=Entry_Position),
    EQ_con=input.bool(False, "Premium / Discount Zone", inline="0.5", tooltip='When enabled, the system filters and allows only orders that are within the Premium and Discount zones.', group=Entry_Position),
    Pre_Dis=input.float(50, "Min", step=1, inline="0.55", group=Entry_Position),
    Pre_Dis2=input.float(80, "Max", step=1, inline="0.55", group=Entry_Position),
    cancel_pending_A=input.bool(True, "Cancel Pending Order [A]", inline="0.6", tooltip='Cancel the pending order when liquidity is swept on the opposite side.', group=Entry_Position),
    cancel_pending_B=input.bool(True, "Cancel Pending Order [B]", inline="0.7", tooltip='Cancel the pending order when new Buy and Sell signals appear.', group=Entry_Position),
    cancel_pending_C=input.bool(True, "Cancel Pending Order [C]", inline="0.8", tooltip='Cancel the pending order when exiting the selected time zone.', group=Entry_Position),
    B_long=input.bool(True, "Entry Longㅤㅤ", inline="1", group=Entry_Position),
    S_short=input.bool(True, "Entry Short", inline="1", group=Entry_Position),
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
    lbl_SnD=input.bool(True, "Show Label |", inline="0.4", group=display_group),
    Size_SnD=input.string('Tiny', 'Size', options=('Tiny', 'Small', 'Normal'), inline="0.4", group=display_group),
    Col_SnD=input(color.rgb(255, 255, 255), '|', inline="0.4", group=display_group),
    qty_pi=input.int(1, "Q'ty", inline="0.5", group=display_group),
    Mit_Pi=input.bool(True, "His", inline="0.5", group=display_group),
    qty_mit_pi=input.int(4, "", inline="0.5", tooltip='Quantity of Demand / Supply and Quantity of History', group=display_group),
    SD_fvg=input.bool(True, "FVG", inline="1", group=display_group),
    Col_fvg_d=input(color.rgb(76, 175, 79, 75), '', inline="1", group=display_group),
    Col_fvg_s=input(color.rgb(242, 54, 70, 75), '/', inline="1", group=display_group),
    Col_fvg_mit=input(color.rgb(76, 175, 79, 85), '||', inline="1", group=display_group),
    Col_fvg_mit2=input(color.rgb(242, 54, 70, 85), '/', inline="1", group=display_group, tooltip='Demand / Supply || History of Demand / Supply'),
    SD_i_fvg=input.bool(True, "iFVG", inline="2", group=display_group),
    Col_ifvg_d=input(color.rgb(41, 98, 255, 75), '', inline="2", group=display_group),
    Col_ifvg_s=input(color.rgb(155, 39, 176, 75), '/', inline="2", group=display_group),
    Col_ifvg_mit=input(color.rgb(41, 98, 255, 85), '||', inline="2", group=display_group),
    Col_ifvg_mit2=input(color.rgb(155, 39, 176, 85), '/', inline="2", group=display_group, tooltip='Demand / Supply || History of Demand / Supply'),
    gap_col_min=input(color.rgb(242, 255, 0, 5), 'Gap Min', inline="3", group=display_group),
    gap_col_max=input(color.rgb(255, 0, 238, 45), 'ㅤㅤMax', inline="3", group=display_group),
    show_swing_lid=input.bool(True, 'Show Swing', inline="3", group=liquidity),
    sw_line_style=input.string('⎯⎯⎯', 'ㅤㅤstyle', options=('⎯⎯⎯', '----', '····'), inline='3', group=liquidity),
    sw_Size=input.string('Small', 'Swing Size', options=('Tiny', 'Small', 'Normal'), inline="4", group=liquidity),
    Color_sw=input(title="", defval=color.rgb(255, 0, 0), inline="4", group=liquidity),
    txt_lid=input.string("$", 'Text', inline="5", group=liquidity),
    lbl_Size=input.string('Small', 'Label Size', options=('Tiny', 'Small', 'Normal'), inline="5", group=liquidity),
    Lid_show=input.int(2, "Q'ty", inline="6", minval=1, group=liquidity),
    mi_lid=input.bool(True, 'His', inline="6", group=liquidity),
    Lid_ss=input.int(4, "", inline="6", group=liquidity),
    show_lid=input.bool(True, 'Show Liquidity', inline="7", group=liquidity),
    Lid_style=input.string('····', 'ㅤㅤstyle', options=('⎯⎯⎯', '----', '····'), inline='7', group=liquidity),
    Lid_color=input(color.rgb(255, 255, 255), 'Line', inline="7.5", group=liquidity),
    Lid_txt_color=input(color.rgb(255, 255, 255), 'ㅤㅤText', inline="7.5", group=liquidity),
    Show_Structure=input.bool(True, "Show", inline="0.55", group=Internal),
    In_Size=input.string('Tiny', '', options=('Tiny', 'Small', 'Normal'), inline="0.55", group=Internal),
    In_Line_style=input.string('----', 'Line', options=('⎯⎯⎯', '----', '····'), inline='0.55', group=Internal),
    In_up_color=input(color.teal, 'Bullish', inline="0.6", group=Internal),
    In_down_color=input(color.new('#F23645'), 'ㅤㅤBearish', inline="0.6", group=Internal),
    Color_Mark_Swing=input(color.rgb(77, 208, 225), 'Swing', inline="0.7", group=Internal),
    color_Eq_In=input(color.new('#1848CC'), "ㅤㅤEquilibrium", inline="0.7", group=Internal),
    distance_bar_line=input.int(40, "Distance Line", inline="8", group=Internal),
    distance_bar_label=input.int(20, "Label", inline="8", group=Internal),
    Show_result=input.bool(True, "Show Result", inline="1", group=result_group, tooltip="The Profit Factor here is calculated using the formula:\n(Number of Wins x Risk-Reward Ratio) / Number of Losses\nThis formula is based on the assumption that the risk per losing trade is fixed — for example, every losing trade costs exactly 1% of the account.\nBecause of this assumption, the calculated Profit Factor will not match TradingView’s result, since TradingView uses:\nGross Profit / Gross Loss\nAnd in actual TradingView trades, the loss amount of each trade is not always equal, because the system doesn’t enforce a fixed-risk rule for every losing trade. "),
    select_position=input.string("bottom_right", "", options=("bottom_right", "bottom_center", "bottom_left", "top_center", "top_left", "top_right", "mid_center", "mid_left", "mid_right"), group=result_group, inline="1", display=display.data_window),
    Factor_up=input.float(1.3, "Profit Factor > ", step=0.1, inline="2", group=result_group),
    Factor_up_color=input(title="   ", defval=color.new('#A5D6A7'), inline="2", group=result_group),
    Factor_donw=input.float(1, "Profit Factor < ", step=0.1, inline="3", group=result_group),
    Factor_donw_color=input(title="   ", defval=color.new('#FAA1A4'), inline="3", group=result_group),
    Entry_box=input.bool(True, "Show Boxㅤㅤ", inline="1", group=Display_Entry),
    col_1=input(color.rgb(8, 153, 129, 80), 'TP', inline="1", group=Display_Entry),
    col_2=input(color.rgb(242, 54, 70, 80), 'ㅤㅤSL', inline="1", group=Display_Entry),
    close_all=input.bool(False, "Turn off all displays", inline="2", group=Display_Entry)
):
    def get_text_style(style):
        __block_result__ = na
        __switch__ = style
        if __switch__ == 'Auto':
            __block_result__ = size.auto
        elif __switch__ == 'Tiny':
            __block_result__ = size.tiny
        elif __switch__ == 'Small':
            __block_result__ = size.small
        elif __switch__ == 'Normal':
            __block_result__ = size.normal
        return __block_result__

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

    def add_int_unshift(array__ren__, new_value_to_add):
        array.remove(array__ren__, array.size(array__ren__) - 1)
        return array.unshift(array__ren__, new_value_to_add)

    def Delete_Box_Push(array__ren__, i):
        box.delete(array.get(array__ren__, i))
        array.remove(array__ren__, i)
        return array.push(array__ren__, na)

    def add_array_unshift(array__ren__, new_value_to_add):
        box.delete(array.get(array__ren__, array.size(array__ren__) - 1))
        array.remove(array__ren__, array.size(array__ren__) - 1)
        return array.unshift(array__ren__, new_value_to_add)

    def value_unshift_noremove(a1, v1, a2, v2, a3, v3):
        array.unshift(a1, v1)
        array.unshift(a2, v2)
        return array.unshift(a3, v3)

    def value_unshift(a1, v1, a2, v2, a3, v3):
        array.unshift(a1, v1)
        array.unshift(a2, v2)
        array.unshift(a3, v3)
        array.remove(a1, array.size(a1) - 1)
        array.remove(a2, array.size(a2) - 1)
        return array.remove(a3, array.size(a3) - 1)

    def value_remove(a1, a2, a3, i):
        array.remove(a1, i)
        array.push(a1, na)
        array.remove(a2, i)
        array.push(a2, na)
        array.remove(a3, i)
        return array.push(a3, na)

    def unshift_remove(array__ren__, new_value_to_add):
        array.unshift(array__ren__, new_value_to_add)
        return array.remove(array__ren__, array.size(array__ren__) - 1)

    def value_delet_Push1(a1, i):
        array.remove(a1, i)
        return array.push(a1, na)

    def Delete_line_lbl_Push(array__ren__, l_bel, i):
        line.delete(array.get(array__ren__, i))
        label.delete(array.get(l_bel, i))
        array.remove(array__ren__, i)
        array.remove(l_bel, i)
        array.push(array__ren__, na)
        return array.push(l_bel, na)

    def Line_mit_unshift(array__ren__, new_value_to_add):
        line.delete(array.get(array__ren__, array.size(array__ren__) - 1))
        array.remove(array__ren__, array.size(array__ren__) - 1)
        return array.unshift(array__ren__, new_value_to_add)

    def label_mit_unshift(array__ren__, new_value_to_add):
        label.delete(array.get(array__ren__, array.size(array__ren__) - 1))
        array.remove(array__ren__, array.size(array__ren__) - 1)
        return array.unshift(array__ren__, new_value_to_add)

    TRANSP: Color = color.new('#FFFFFF00')


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
        __block_result_2__ = na
        __switch__ = select
        if __switch__ == "bottom_right":
            __block_result_2__ = position.bottom_right
        elif __switch__ == "bottom_center":
            __block_result_2__ = position.bottom_center
        elif __switch__ == "bottom_left":
            __block_result_2__ = position.bottom_left
        elif __switch__ == "top_center":
            __block_result_2__ = position.top_center
        elif __switch__ == "top_left":
            __block_result_2__ = position.top_left
        elif __switch__ == "top_right":
            __block_result_2__ = position.top_right
        elif __switch__ == "mid_center":
            __block_result_2__ = position.middle_center
        elif __switch__ == "mid_left":
            __block_result_2__ = position.middle_left
        elif __switch__ == "mid_right":
            __block_result_2__ = position.middle_right
        return __block_result_2__



    In_Size_CF: Persistent = size.tiny if In_Size == 'Tiny' else size.small if In_Size == 'Small' else size.normal

    time_set = last_bar_time + (time - time[1]) * distance_bar_line
    time_lbl = last_bar_time + (time - time[1]) * distance_bar_label
    n_bar = timeframe.in_seconds(timeframe.period) * 1000 * 5
    gap_bar = timeframe.in_seconds(timeframe.period) * 1000

    Turn_off = True if not close_all else False

    atr_sl = ta.ema(ta.tr(True), length_atr)

    atr_check_FVG_min = atr_sl * FVG_min_ATR
    atr_check_FVG_max = atr_sl * FVG_max_ATR

    Check_min_FVG = FVG_min * atr_sl
    Check_max_FVG = FVG_max * atr_sl

    Check_min_iFVG = iFVG_min * atr_sl
    Check_max_iFVG = iFVG_max * atr_sl

    qty_fvg: int = 9000

    dfvg_top: Persistent[list[float]] = array.new_float(qty_fvg, na)
    dfvg_bot: Persistent[list[float]] = array.new_float(qty_fvg, na)
    dfvg_bar: Persistent[list[int]] = array.new_int(qty_fvg, na)
    dfvg_col: Persistent[list[Color]] = array.new_color(qty_fvg, na)
    sfvg_top: Persistent[list[float]] = array.new_float(qty_fvg, na)
    sfvg_bot: Persistent[list[float]] = array.new_float(qty_fvg, na)
    sfvg_bar: Persistent[list[int]] = array.new_int(qty_fvg, na)
    sfvg_col: Persistent[list[Color]] = array.new_color(qty_fvg, na)

    d_fvg_zone: Persistent[list[Box]] = array.new_box(qty_pi, na)
    s_fvg_zone: Persistent[list[Box]] = array.new_box(qty_pi, na)

    d_fvg_mit: Persistent[list[Box]] = array.new_box(qty_mit_pi, na)
    s_fvg_mit: Persistent[list[Box]] = array.new_box(qty_mit_pi, na)

    dfvg_R_top: Persistent[list[float]] = array.new_float(qty_fvg, na)
    dfvg_R_bot: Persistent[list[float]] = array.new_float(qty_fvg, na)
    dfvg_bar_R: Persistent[list[int]] = array.new_int(qty_fvg, na)
    sfvg_R_top: Persistent[list[float]] = array.new_float(qty_fvg, na)
    sfvg_R_bot: Persistent[list[float]] = array.new_float(qty_fvg, na)
    sfvg_bar_R: Persistent[list[int]] = array.new_int(qty_fvg, na)

    if bar_index > 1:
        if low <= array.get(dfvg_bot, 0):
            for i in pine_range(0, qty_fvg - 1):
                if SD_fvg and Turn_off:
                    if Mit_Pi:
                        lbl_sd = 'FVG' if lbl_SnD else ''
                        add_array_unshift(d_fvg_mit, box.new(xloc=xloc.bar_time, left=array.get(dfvg_bar, 0), top=array.get(dfvg_top, 0), right=time, bottom=array.get(dfvg_bot, 0), border_color=Col_fvg_mit, bgcolor=Col_fvg_mit, text=lbl_sd, text_size=get_text_style(Size_SnD), text_color=Col_SnD, text_halign=text.align_right, text_valign=text.align_center))
                value_remove(dfvg_top, dfvg_bot, dfvg_bar, 0)
                array.remove(dfvg_col, 0)
                array.push(dfvg_col, na)
                Delete_Box_Push(d_fvg_zone, 0)
                if low > array.get(dfvg_bot, 0) or na(array.get(dfvg_bot, 0)):
                    break

        if low <= array.get(dfvg_top, 0):
            for i in pine_range(0, qty_fvg - 1):
                if low <= array.get(dfvg_top, i):
                    array.set(dfvg_col, i, Col_fvg_mit)
                if low > array.get(dfvg_top, i) or na(array.get(dfvg_top, i)):
                    break

        if low > high[2] and barstate.isconfirmed:
            value_unshift(dfvg_top, low, dfvg_bot, high[2], dfvg_bar, time[2])
            add_int_unshift(dfvg_col, Col_fvg_d)
            value_unshift(dfvg_R_top, low, dfvg_R_bot, high[2], dfvg_bar_R, time[2])

        if high >= array.get(sfvg_top, 0):
            for i in pine_range(0, qty_fvg - 1):
                if SD_fvg and Turn_off:
                    if Mit_Pi:
                        lbl_sd = 'FVG' if lbl_SnD else ''
                        add_array_unshift(s_fvg_mit, box.new(xloc=xloc.bar_time, left=array.get(sfvg_bar, 0), top=array.get(sfvg_top, 0), right=time, bottom=array.get(sfvg_bot, 0), border_color=Col_fvg_mit2, bgcolor=Col_fvg_mit2, text=lbl_sd, text_size=get_text_style(Size_SnD), text_color=Col_SnD, text_halign=text.align_right, text_valign=text.align_center))
                value_remove(sfvg_top, sfvg_bot, sfvg_bar, 0)
                array.remove(sfvg_col, 0)
                array.push(sfvg_col, na)
                Delete_Box_Push(s_fvg_zone, 0)
                if high < array.get(sfvg_top, 0) or na(array.get(sfvg_top, 0)):
                    break

        if high >= array.get(sfvg_bot, 0):
            for i in pine_range(0, qty_fvg - 1):
                if high >= array.get(sfvg_bot, i):
                    array.set(sfvg_col, i, Col_fvg_mit2)
                if high < array.get(sfvg_bot, i) or na(array.get(sfvg_bot, i)):
                    break

        if high < low[2] and barstate.isconfirmed:
            value_unshift(sfvg_top, low[2], sfvg_bot, high, sfvg_bar, time[2])
            add_int_unshift(sfvg_col, Col_fvg_s)
            value_unshift(sfvg_R_top, low[2], sfvg_R_bot, high, sfvg_bar_R, time[2])

    if Turn_off and SD_fvg:
        if not na(array.get(dfvg_bot, 0)):
            for i in pine_range(0, qty_pi - 1):
                if na(array.get(dfvg_bot, i)):
                    break
                col_fvg = array.get(dfvg_col, i)
                lbl_sd = 'FVG' if lbl_SnD else ''
                box.delete(array.get(d_fvg_zone, i))
                array.set(d_fvg_zone, i, box.new(xloc=xloc.bar_time, left=array.get(dfvg_bar, i), top=array.get(dfvg_top, i), right=time_set, bottom=array.get(dfvg_bot, i), border_color=col_fvg, bgcolor=col_fvg, text=lbl_sd, text_size=get_text_style(Size_SnD), text_color=Col_SnD, text_halign=text.align_right, text_valign=text.align_center))

        if not na(array.get(sfvg_bot, 0)):
            for i in pine_range(0, qty_pi - 1):
                if na(array.get(sfvg_bot, i)):
                    break
                lbl_sd = 'FVG' if lbl_SnD else ''
                col_sfvg = array.get(sfvg_col, i)
                box.delete(array.get(s_fvg_zone, i))
                array.set(s_fvg_zone, i, box.new(xloc=xloc.bar_time, left=array.get(sfvg_bar, i), top=array.get(sfvg_top, i), right=time_set, bottom=array.get(sfvg_bot, i), border_color=col_sfvg, bgcolor=col_sfvg, text=lbl_sd, text_size=get_text_style(Size_SnD), text_color=Col_SnD, text_halign=text.align_right, text_valign=text.align_center))

    d_fvg_R_mit: Persistent[list[Box]] = array.new_box(qty_mit_pi, na)
    s_fvg_R_mit: Persistent[list[Box]] = array.new_box(qty_mit_pi, na)

    dfvg_R2_top: Persistent[list[float]] = array.new_float(qty_fvg, na)
    dfvg_R2_bot: Persistent[list[float]] = array.new_float(qty_fvg, na)
    dfvg_bar_R2: Persistent[list[int]] = array.new_int(qty_fvg, na)
    sfvg_R2_top: Persistent[list[float]] = array.new_float(qty_fvg, na)
    sfvg_R2_bot: Persistent[list[float]] = array.new_float(qty_fvg, na)
    sfvg_bar_R2: Persistent[list[int]] = array.new_int(qty_fvg, na)

    d_i_fvg_col: Persistent[list[Color]] = array.new_color(qty_fvg, na)
    s_i_fvg_col: Persistent[list[Color]] = array.new_color(qty_fvg, na)

    d_f_r_zone: Persistent[list[Box]] = array.new_box(qty_pi, na)
    s_f_r_zone: Persistent[list[Box]] = array.new_box(qty_pi, na)

    if bar_index > 1:
        if low <= array.get(dfvg_R2_bot, 0):
            for i in pine_range(0, qty_fvg - 1):
                if low <= array.get(dfvg_R2_bot, 0):
                    lbl_sd = 'iFVG' if lbl_SnD else ''
                    if Turn_off and Mit_Pi and SD_i_fvg:
                        add_array_unshift(d_fvg_R_mit, box.new(xloc=xloc.bar_time, left=array.get(dfvg_bar_R2, 0), top=array.get(dfvg_R2_top, 0), right=time, bottom=array.get(dfvg_R2_bot, 0), border_color=Col_ifvg_mit, bgcolor=Col_ifvg_mit, text=lbl_sd, text_size=get_text_style(Size_SnD), text_color=Col_SnD, text_halign=text.align_right, text_valign=text.align_center))
                    value_remove(dfvg_R2_top, dfvg_R2_bot, dfvg_bar_R2, 0)
                    array.remove(d_i_fvg_col, 0)
                    array.push(d_i_fvg_col, na)
                    Delete_Box_Push(d_f_r_zone, 0)
                if low > array.get(dfvg_R2_bot, 0) or na(array.get(dfvg_R2_bot, 0)):
                    break

        if low <= array.get(dfvg_R2_top, 0):
            for i in pine_range(0, qty_fvg - 1):
                if low > array.get(dfvg_R2_top, i) or na(array.get(dfvg_R2_top, i)):
                    break
                if low <= array.get(dfvg_R2_top, i):
                    array.set(d_i_fvg_col, i, Col_ifvg_mit)

        if close > array.get(sfvg_R_top, 0) and barstate.isconfirmed:
            for i in pine_range(0, qty_fvg - 1):
                if close > array.get(sfvg_R_top, 0):
                    value_unshift(dfvg_R2_top, array.get(sfvg_R_top, 0), dfvg_R2_bot, array.get(sfvg_R_bot, 0), dfvg_bar_R2, array.get(sfvg_bar_R, 0))
                    add_int_unshift(d_i_fvg_col, Col_ifvg_d)
                    value_remove(sfvg_R_top, sfvg_R_bot, sfvg_bar_R, 0)
                if close <= array.get(sfvg_R_top, 0) or na(array.get(sfvg_R_top, 0)):
                    break

        if high >= array.get(sfvg_R2_top, 0):
            for i in pine_range(0, qty_fvg - 1):
                if high >= array.get(sfvg_R2_top, 0):
                    lbl_sd = 'iFVG' if lbl_SnD else ''
                    if Turn_off and Mit_Pi and SD_i_fvg:
                        add_array_unshift(s_fvg_R_mit, box.new(xloc=xloc.bar_time, left=array.get(sfvg_bar_R2, 0), top=array.get(sfvg_R2_top, 0), right=time, bottom=array.get(sfvg_R2_bot, 0), border_color=Col_ifvg_mit2, bgcolor=Col_ifvg_mit2, text=lbl_sd, text_size=get_text_style(Size_SnD), text_color=Col_SnD, text_halign=text.align_right, text_valign=text.align_center))
                    value_remove(sfvg_R2_top, sfvg_R2_bot, sfvg_bar_R2, 0)
                    array.remove(s_i_fvg_col, 0)
                    array.push(s_i_fvg_col, na)
                    Delete_Box_Push(s_f_r_zone, 0)
                if high < array.get(sfvg_R2_top, 0) or na(array.get(sfvg_R2_top, 0)):
                    break

        if high >= array.get(sfvg_R2_bot, 0):
            for i in pine_range(0, qty_fvg - 1):
                if high < array.get(sfvg_R2_bot, i) or na(array.get(sfvg_R2_bot, i)):
                    break
                if high >= array.get(sfvg_R2_bot, i):
                    array.set(s_i_fvg_col, i, Col_ifvg_mit2)

        if close < array.get(dfvg_R_bot, 0) and barstate.isconfirmed:
            for i in pine_range(0, qty_fvg - 1):
                if close < array.get(dfvg_R_bot, 0):
                    value_unshift(sfvg_R2_top, array.get(dfvg_R_top, 0), sfvg_R2_bot, array.get(dfvg_R_bot, 0), sfvg_bar_R2, array.get(dfvg_bar_R, 0))
                    add_int_unshift(s_i_fvg_col, Col_ifvg_s)
                    value_remove(dfvg_R_top, dfvg_R_bot, dfvg_bar_R, 0)
                if close >= array.get(dfvg_R_bot, 0) or na(array.get(dfvg_R_bot, 0)):
                    break

    if SD_i_fvg and Turn_off:
        if not na(array.get(dfvg_R2_top, 0)):
            for i in pine_range(0, qty_pi - 1):
                col_fvg = array.get(d_i_fvg_col, i)
                lbl_sd = 'iFVG' if lbl_SnD else ''
                if na(array.get(dfvg_R2_top, i)):
                    break
                box.delete(array.get(d_f_r_zone, i))
                array.set(d_f_r_zone, i, box.new(xloc=xloc.bar_time, left=array.get(dfvg_bar_R2, i), top=array.get(dfvg_R2_top, i), right=time_set, bottom=array.get(dfvg_R2_bot, i), border_color=col_fvg, bgcolor=col_fvg, text=lbl_sd, text_size=get_text_style(Size_SnD), text_color=Col_SnD, text_halign=text.align_right, text_valign=text.align_center))

        if not na(array.get(sfvg_R2_bot, 0)):
            for i in pine_range(0, qty_pi - 1):
                col_sfvg = array.get(s_i_fvg_col, i)
                lbl_sd = 'iFVG' if lbl_SnD else ''
                if na(array.get(sfvg_R2_bot, i)):
                    break
                box.delete(array.get(s_f_r_zone, i))
                array.set(s_f_r_zone, i, box.new(xloc=xloc.bar_time, left=array.get(sfvg_bar_R2, i), top=array.get(sfvg_R2_top, i), right=time_set, bottom=array.get(sfvg_R2_bot, i), border_color=col_sfvg, bgcolor=col_sfvg, text=lbl_sd, text_size=get_text_style(Size_SnD), text_color=Col_SnD, text_halign=text.align_right, text_valign=text.align_center))

    sw_H: Series = ta.pivothigh(high, Len, Len)
    sw_L: Series = ta.pivotlow(low, Len, Len)

    sw_Dir_small: Persistent[int] = 0
    sw_high: PersistentSeries[float] = na(float)
    sw_low: PersistentSeries[float] = na(float)
    Bar_sw_high: PersistentSeries[int] = 0
    Bar_sw_low: PersistentSeries[int] = 0
    ss_high: PersistentSeries[float] = na(float)
    ss_low: PersistentSeries[float] = na(float)
    b_sw_high: PersistentSeries[int] = 0
    b_sw_low: PersistentSeries[int] = 0
    sw_skip: bool = False
    Ch_swh: bool = False
    Ch_swl: bool = False
    swh_check: bool = False
    swl_check: bool = False

    if na(sw_high) and (not na(sw_H)):
        sw_high = sw_H
        sw_Dir_small = -1
    if na(sw_low) and (not na(sw_L)):
        sw_low = sw_L
        sw_Dir_small = 1

    if (high > ss_high or na(ss_high)) and barstate.isconfirmed:
        ss_high = high
        b_sw_high = bar_index
    if (low < ss_low or na(ss_low)) and barstate.isconfirmed:
        ss_low = low
        b_sw_low = bar_index

    display_swing = show_swing_lid and Turn_off

    b_len = Len + 1
    if not na(sw_L) and (not na(sw_H)) and barstate.isconfirmed:
        if sw_Dir_small == 1:
            for i in pine_range(1, Len * 2):
                if not na(sw_L[i]):
                    swl_check = True
                    break
            sw_low = sw_L
            Bar_sw_low = bar_index[Len]
            sw_high = sw_H
            Bar_sw_high = bar_index[Len]
            ch = close[Len] > open[Len]
            s_h = ss_high[b_len] if ch else sw_H
            s_b = b_sw_high[b_len] if ch else bar_index[Len]
            ch2 = (sw_high < sw_low or (ss_high[b_len] > sw_high and (not swl_check))) and Len > 1
            s_l2 = sw_low if ch else sw_low[b_len]
            s_b2 = Bar_sw_low if ch else Bar_sw_low[b_len]
            if display_swing:
                sw_line = line.new(Bar_sw_low, sw_low, Bar_sw_high, sw_high, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                line.new(s_b2, s_l2, s_b, s_h, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
            if ch and (not ch2):
                if display_swing:
                    line.new(Bar_sw_low[b_len], sw_low[b_len], s_b, s_h, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                if display_swing:
                    label.new(s_b, s_h, text='●', style=label.style_label_center, color=TRANSP, textcolor=Color_sw, size=get_text_style(sw_Size))
            if ch2:
                if display_swing:
                    sw_line3 = line.new(Bar_sw_low[b_len], sw_low[b_len], b_sw_high[b_len], ss_high[b_len], xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                    if not ch:
                        line.new(b_sw_low[b_len], ss_low[b_len], b_sw_high[b_len], ss_high[b_len], xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                if display_swing:
                    if not ch:
                        label.new(b_sw_low[b_len], ss_low[b_len], text='●', style=label.style_label_center, color=TRANSP, textcolor=Color_sw, size=get_text_style(sw_Size))
                    label.new(b_sw_high[b_len], ss_high[b_len], text='●', style=label.style_label_center, color=TRANSP, textcolor=Color_sw, size=get_text_style(sw_Size))
            sw_Dir_small = -1 if ch else 1
            sw_skip = True
        if sw_Dir_small == -1 and (not sw_skip):
            if not na(sw_L):
                for i in pine_range(1, Len * 2):
                    if not na(sw_H[i]):
                        swh_check = True
                        break
            sw_low = sw_L
            Bar_sw_low = bar_index[Len]
            sw_high = sw_H
            Bar_sw_high = bar_index[Len]
            ch = close[Len] < open[Len]
            s_l = ss_low[b_len] if ch else sw_L
            s_b = b_sw_low[b_len] if ch else bar_index[Len]
            ch2 = (sw_high <= sw_low or (ss_low[b_len] < sw_low and (not swh_check))) and Len > 1
            s_h2 = sw_high if ch else sw_high[b_len]
            s_b2 = Bar_sw_high if ch else Bar_sw_high[b_len]
            if display_swing:
                sw_line = line.new(Bar_sw_low, sw_low, Bar_sw_high, sw_high, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                line.new(s_b, s_l, s_b2, s_h2, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
            if ch and (not ch2):
                if display_swing:
                    line.new(s_b, s_l, Bar_sw_high[b_len], sw_high[b_len], xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                if display_swing:
                    label.new(s_b, s_l, text='●', style=label.style_label_center, color=TRANSP, textcolor=Color_sw, size=get_text_style(sw_Size))
            if ch2:
                if display_swing:
                    sw_line3 = line.new(b_sw_low[b_len], ss_low[b_len], Bar_sw_high[b_len], sw_high[b_len], xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                    if not ch:
                        line.new(b_sw_low[b_len], ss_low[b_len], b_sw_high[b_len], ss_high[b_len], xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                if display_swing:
                    label.new(b_sw_low[b_len], ss_low[b_len], text='●', style=label.style_label_center, color=TRANSP, textcolor=Color_sw, size=get_text_style(sw_Size))
                    if not ch:
                        label.new(b_sw_high[b_len], ss_high[b_len], text='●', style=label.style_label_center, color=TRANSP, textcolor=Color_sw, size=get_text_style(sw_Size))
            sw_Dir_small = 1 if ch else -1
            sw_skip = True
        Ch_swl = True
        Ch_swh = True

    if sw_Dir_small == 1 and (not sw_skip) and barstate.isconfirmed:
        if not na(sw_H):
            for i in pine_range(0, Len * 2):
                if not na(sw_L[i]):
                    swl_check = True
                    break
            sw_high = sw_H
            Bar_sw_high = bar_index[Len]
            Ch_swh = True
            sw_Dir_small = -1
            ch = sw_high < sw_low or (ss_high[b_len] > sw_high and (not swl_check))
            s_l = ss_low[b_len] if ch else sw_low
            s_b = b_sw_low[b_len] if ch else Bar_sw_low
            if display_swing:
                line.new(s_b, s_l, Bar_sw_high, sw_high, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
            if ch:
                if display_swing:
                    sw_line1 = line.new(Bar_sw_low, sw_low, b_sw_high[b_len], ss_high[b_len], xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                    line.new(b_sw_low[b_len], ss_low[b_len], b_sw_high[b_len], ss_high[b_len], xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                if display_swing:
                    label.new(b_sw_low[b_len], ss_low[b_len], text='●', style=label.style_label_center, color=TRANSP, textcolor=Color_sw, size=get_text_style(sw_Size))
                    label.new(b_sw_high[b_len], ss_high[b_len], text='●', style=label.style_label_center, color=TRANSP, textcolor=Color_sw, size=get_text_style(sw_Size))
            sw_skip = True
        if not na(sw_L):
            sw_low = sw_L
            Bar_sw_low = bar_index[Len]
            sw_high = ss_high[b_len]
            Bar_sw_high = b_sw_high[b_len]
            Ch_swl = True
            Ch_swh = True
            sw_Dir_small = 1
            if display_swing:
                sw_line = line.new(Bar_sw_low[Len], sw_low[Len], Bar_sw_high, sw_high, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                line.new(Bar_sw_low, sw_low, Bar_sw_high, sw_high, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
            sw_skip = True

    if sw_Dir_small == -1 and (not sw_skip) and barstate.isconfirmed:
        if not na(sw_L):
            for i in pine_range(0, Len * 2):
                if not na(sw_H[i]):
                    swh_check = True
                    break
            sw_low = sw_L
            Bar_sw_low = bar_index[Len]
            Ch_swl = True
            sw_Dir_small = 1
            ch = sw_high <= sw_low or (ss_low[b_len] < sw_low and (not swh_check))
            s_h = ss_high[b_len] if ch else sw_high
            s_b = b_sw_high[b_len] if ch else Bar_sw_high
            if display_swing:
                line.new(Bar_sw_low, sw_low, s_b, s_h, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
            if ch:
                if display_swing:
                    sw_line1 = line.new(Bar_sw_high, sw_high, b_sw_low[b_len], ss_low[b_len], xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                    line.new(b_sw_low[b_len], ss_low[b_len], b_sw_high[b_len], ss_high[b_len], xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                if display_swing:
                    label.new(b_sw_low[b_len], ss_low[b_len], text='●', style=label.style_label_center, color=TRANSP, textcolor=Color_sw, size=get_text_style(sw_Size))
                    label.new(b_sw_high[b_len], ss_high[b_len], text='●', style=label.style_label_center, color=TRANSP, textcolor=Color_sw, size=get_text_style(sw_Size))
        if not na(sw_H):
            sw_high = sw_H
            Bar_sw_high = bar_index[Len]
            sw_low = ss_low[b_len]
            Bar_sw_low = b_sw_low[b_len]
            Ch_swl = True
            Ch_swh = True
            sw_Dir_small = -1
            if display_swing:
                sw_line = line.new(Bar_sw_low, sw_low, Bar_sw_high[Len], sw_high[Len], xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
                line.new(Bar_sw_low, sw_low, Bar_sw_high, sw_high, xloc=xloc.bar_index, color=Color_sw, style=get_line_style(sw_line_style))
    if display_swing:
        if Ch_swh:
            label.new(Bar_sw_high, sw_high, text='●', style=label.style_label_center, color=TRANSP, textcolor=Color_sw, size=get_text_style(sw_Size))
        if Ch_swl:
            label.new(Bar_sw_low, sw_low, text='●', style=label.style_label_center, color=TRANSP, textcolor=Color_sw, size=get_text_style(sw_Size))

    diff_ph = 0 if sw_Dir_small == 1 else 1
    diff_pl = 0 if sw_Dir_small == -1 else 1
    ph: Series = high if Len == 1 else ta.highest(Len - diff_ph)
    b_ph: Series = bar_index if Len == 1 else bar_index[math.abs(ta.highestbars(Len - diff_ph))]
    pl: Series = low if Len == 1 else ta.lowest(Len - diff_pl)
    b_pl: Series = bar_index if Len == 1 else bar_index[math.abs(ta.lowestbars(Len - diff_pl))]

    b_ss: int = 0
    if Ch_swh:
        ss_low = pl[b_ss]
        b_sw_low = b_pl[b_ss]
        ss_high = ph[b_ss]
        b_sw_high = b_ph[b_ss]
    if Ch_swl:
        ss_low = pl[b_ss]
        b_sw_low = b_pl[b_ss]
        ss_high = ph[b_ss]
        b_sw_high = b_ph[b_ss]

    ar_q: int = 9000
    line_lid_s: Persistent[list[Line]] = array.new_line(Lid_show, na)
    line_lid_d: Persistent[list[Line]] = array.new_line(Lid_show, na)
    label_lid_s: Persistent[list[Label]] = array.new_label(Lid_show, na)
    label_lid_d: Persistent[list[Label]] = array.new_label(Lid_show, na)

    mit_lid_s: Persistent[list[Line]] = array.new_line(Lid_ss, na)
    mit_lid_d: Persistent[list[Line]] = array.new_line(Lid_ss, na)
    mit_lid_lbl_s: Persistent[list[Label]] = array.new_label(Lid_ss, na)
    mit_lid_lbl_d: Persistent[list[Label]] = array.new_label(Lid_ss, na)

    lid_sup: Persistent[list[float]] = array.new_float(ar_q, na)
    lid_dem: Persistent[list[float]] = array.new_float(ar_q, na)
    lid_bar_sup: Persistent[list[int]] = array.new_int(ar_q, na)
    lid_bar_dem: Persistent[list[int]] = array.new_int(ar_q, na)

    value_dem_lid: Persistent[float] = na(float)
    pre_bar_Dlid_left: Persistent[int] = na(float)
    pre_bar_Dlid_right: Persistent[int] = na(float)
    value_sup_lid: Persistent[float] = na(float)
    pre_bar_Slid_left: Persistent[int] = na(float)
    pre_bar_Slid_right: Persistent[int] = na(float)

    pre_dem_lid: Persistent[float] = na(float)
    pre2_bar_Dlid_left: Persistent[int] = na(float)
    pre2_bar_Dlid_right: Persistent[int] = na(float)
    pre_sup_lid: Persistent[float] = na(float)
    pre2_bar_Slid_left: Persistent[int] = na(float)
    pre2_bar_Slid_right: Persistent[int] = na(float)

    break_dem: bool = False
    break_sup: bool = False
    con_buy: PersistentSeries[bool] = False
    con_sell: PersistentSeries[bool] = False

    FVG_gap_buy: Persistent[float] = na(float)
    FVG_gap_sell: Persistent[float] = na(float)
    Check_gap_buy: bool = False
    Check_gap_sell: bool = False

    if Ch_swh and sw_high >= ph:
        unshift_remove(lid_sup, sw_high)
        unshift_remove(lid_bar_sup, time[bar_index - Bar_sw_high])
    if Ch_swl and sw_low <= pl:
        unshift_remove(lid_dem, sw_low)
        unshift_remove(lid_bar_dem, time[bar_index - Bar_sw_low])

    txt_size = get_text_style(lbl_Size)

    if not na(array.get(lid_dem, 0)):
        if low <= array.get(lid_dem, 0):
            for i in pine_range(0, ar_q - 1):
                value_dem_lid = array.get(lid_dem, 0)
                pre_bar_Dlid_left = array.get(lid_bar_dem, 0)
                pre_bar_Dlid_right = time
                if show_lid and Turn_off:
                    x_value = array.get(lid_bar_dem, 0)
                    y_value = array.get(lid_dem, 0)
                    bar_lbl = (x_value + time) / 2
                    label_mit_unshift(mit_lid_lbl_d, label.new(bar_lbl, y_value, xloc=xloc.bar_time, text=txt_lid, color=TRANSP, textcolor=Lid_txt_color, size=txt_size, style=label.style_label_center))
                    Line_mit_unshift(mit_lid_d, line.new(x_value, y_value, time, y_value, xloc=xloc.bar_time, color=Lid_color, style=get_line_style(Lid_style)))
                value_delet_Push1(lid_dem, 0)
                value_delet_Push1(lid_bar_dem, 0)
                Delete_line_lbl_Push(line_lid_d, label_lid_d, 0)
                if low > array.get(lid_dem, 0) or na(array.get(lid_dem, 0)):
                    break
            break_dem = True

    if not na(array.get(lid_sup, 0)):
        if high >= array.get(lid_sup, 0):
            for i in pine_range(0, ar_q - 1):
                value_sup_lid = array.get(lid_sup, 0)
                pre_bar_Slid_left = array.get(lid_bar_sup, 0)
                pre_bar_Slid_right = time
                if show_lid and Turn_off:
                    x_value = array.get(lid_bar_sup, 0)
                    y_value = array.get(lid_sup, 0)
                    bar_lbl = (x_value + time) / 2
                    label_mit_unshift(mit_lid_lbl_s, label.new(bar_lbl, y_value, xloc=xloc.bar_time, text=txt_lid, color=TRANSP, textcolor=Lid_txt_color, size=txt_size, style=label.style_label_center))
                    Line_mit_unshift(mit_lid_s, line.new(x_value, y_value, time, y_value, xloc=xloc.bar_time, color=Lid_color, style=get_line_style(Lid_style)))
                value_delet_Push1(lid_sup, 0)
                value_delet_Push1(lid_bar_sup, 0)
                Delete_line_lbl_Push(line_lid_s, label_lid_s, 0)
                if high < array.get(lid_sup, 0) or na(array.get(lid_sup, 0)):
                    break
            break_sup = True

    if show_lid and Turn_off:
        if not na(array.get(lid_dem, 0)):
            for i in pine_range(0, Lid_show - 1):
                line.delete(array.get(line_lid_d, i))
                label.delete(array.get(label_lid_d, i))
                if na(array.get(lid_dem, i)):
                    break
                x_value = array.get(lid_bar_dem, i)
                y_value = array.get(lid_dem, i)
                array.set(line_lid_d, i, line.new(x_value, y_value, time_set, y_value, xloc=xloc.bar_time, color=Lid_color, style=get_line_style(Lid_style)))
                array.set(label_lid_d, i, label.new(time_lbl, y_value, xloc=xloc.bar_time, text=txt_lid, color=TRANSP, textcolor=Lid_txt_color, size=txt_size, style=label.style_label_center))

        if not na(array.get(lid_sup, 0)):
            for i in pine_range(0, Lid_show - 1):
                line.delete(array.get(line_lid_s, i))
                label.delete(array.get(label_lid_s, i))
                if na(array.get(lid_sup, i)):
                    break
                x_value = array.get(lid_bar_sup, i)
                y_value = array.get(lid_sup, i)
                array.set(line_lid_s, i, line.new(x_value, y_value, time_set, y_value, xloc=xloc.bar_time, color=Lid_color, style=get_line_style(Lid_style)))
                array.set(label_lid_s, i, label.new(time_lbl, y_value, xloc=xloc.bar_time, text=txt_lid, color=TRANSP, textcolor=Lid_txt_color, size=txt_size, style=label.style_label_center))

    In_Dir_Big: Persistent[int] = 0
    In_Dir_small: Persistent[int] = 0
    In_High: PersistentSeries[float] = na(float)
    In_Low: PersistentSeries[float] = na(float)
    Bar_In_High: PersistentSeries[int] = 0
    Bar_In_Low: PersistentSeries[int] = 0

    i_high: PersistentSeries[float] = na(float)
    i_low: PersistentSeries[float] = na(float)
    Bar_i_high: PersistentSeries[int] = 0
    Bar_i_low: PersistentSeries[int] = 0

    CF_In_High: PersistentSeries[bool] = False
    CF_In_low: PersistentSeries[bool] = False
    Ch_In_H: bool = False
    Ch_In_L: bool = False
    In_skip: bool = False
    In_ChoCH_Down: bool = False
    In_ChoCH_Up: bool = False
    I_BoS_Down: bool = False
    I_BoS_Up: bool = False

    valid_cf_high: Persistent[bool] = False
    valid_cf_low: Persistent[bool] = False
    valid_pivot_high: Persistent[bool] = False
    valid_pivot_low: Persistent[bool] = False

    line_in: Persistent[Line] = na(Line)
    label_in: Persistent[Label] = na(Line)

    cf_high_in = not na(ta.pivothigh(high, Len_in, Len_in))
    if cf_high_in:
        valid_pivot_high = True
    cf_low_in = not na(ta.pivotlow(low, Len_in, Len_in))
    if cf_low_in:
        valid_pivot_low = True

    if (high > i_high or na(i_high)) and barstate.isconfirmed:
        i_high = high
        Bar_i_high = bar_index
        valid_cf_high = False
        valid_pivot_high = False
    if (low < i_low or na(i_low)) and barstate.isconfirmed:
        i_low = low
        Bar_i_low = bar_index
        valid_cf_low = False
        valid_pivot_low = False

    if (close if valid_con == 'Close' else low) < low[bar_index - Bar_i_high]:
        valid_cf_high = True
    if (close if valid_con == 'Close' else high) > high[bar_index - Bar_i_low]:
        valid_cf_low = True

    if CF_In_High and CF_In_low:
        valid_cf_high = False
        valid_cf_low = False
        valid_pivot_high = False
        valid_pivot_low = False

    In_Break_Up = barstate.isconfirmed and close > In_High
    In_Break_Down = barstate.isconfirmed and close < In_Low

    con_first: Persistent[int] = 0

    if In_Dir_Big == 1 and barstate.isconfirmed:
        if In_Break_Down and CF_In_low or (In_Break_Up and CF_In_High):
            if Turn_off:
                txt = 'MSS' if In_Break_Down else 'BOS'
                Swingtrend = In_Low if In_Break_Down else In_High
                bar_trend = Bar_In_Low if In_Break_Down else Bar_In_High
                Time_Bar = time[bar_index - Bar_In_Low] if In_Break_Down else time[bar_index - Bar_In_High]
                txt_Collor = In_down_color if In_Break_Down else In_up_color
                line_in = line.new(Time_Bar, Swingtrend, time, Swingtrend, xloc=xloc.bar_time, color=txt_Collor, style=get_line_style(In_Line_style))
                label_in = label.new(cast_int(math.avg(bar_trend, bar_index)), Swingtrend, txt, xloc=xloc.bar_index, color=TRANSP, textcolor=txt_Collor, style=label.style_label_down if In_Break_Up else label.style_label_up, size=In_Size_CF)

        if In_Break_Down and CF_In_low:
            CF_In_High = True
            CF_In_low = False
            Ch_In_H = True
            In_ChoCH_Down = True

        if not na(In_High) and In_Dir_small == 1 and valid_cf_high and valid_pivot_high:
            CF_In_High = True
            Ch_In_H = True

        if In_Dir_small == -1 and In_Break_Up and CF_In_High:
            CF_In_High = False
            CF_In_low = True
            Ch_In_L = True
            I_BoS_Up = True

    if In_Dir_Big == -1 and barstate.isconfirmed:
        if In_Break_Down and CF_In_low or (In_Break_Up and CF_In_High):
            if Turn_off:
                txt = 'MSS' if In_Break_Up else 'BOS'
                Swingtrend = In_Low if In_Break_Down else In_High
                bar_trend = Bar_In_Low if In_Break_Down else Bar_In_High
                Time_Bar = time[bar_index - Bar_In_Low] if In_Break_Down else time[bar_index - Bar_In_High]
                txt_Collor = In_up_color if In_Break_Up else In_down_color
                line_in = line.new(Time_Bar, Swingtrend, time, Swingtrend, xloc=xloc.bar_time, color=txt_Collor, style=get_line_style(In_Line_style))
                label_in = label.new(cast_int(math.avg(bar_trend, bar_index)), Swingtrend, txt, xloc=xloc.bar_index, color=TRANSP, textcolor=txt_Collor, style=label.style_label_down if In_Break_Up else label.style_label_up, size=In_Size_CF)

        if In_Break_Up and CF_In_High:
            CF_In_High = False
            CF_In_low = True
            Ch_In_L = True
            In_ChoCH_Up = True

        if not na(In_Low) and In_Dir_small == -1 and valid_cf_low and valid_pivot_low:
            CF_In_low = True
            Ch_In_L = True

        if In_Dir_small == 1 and In_Break_Down and CF_In_low:
            CF_In_High = True
            CF_In_low = False
            Ch_In_H = True
            I_BoS_Down = True

    if Ch_In_L:
        In_Low = i_low
        Bar_In_Low = Bar_i_low
        In_Dir_small = 1

    if Ch_In_H:
        In_High = i_high
        Bar_In_High = Bar_i_high
        In_Dir_small = -1

    if na(In_High) and (not na(i_high)) and cf_high_in and barstate.isconfirmed:
        i_low = low
        Bar_i_low = bar_index
        CF_In_High = True
        con_first += 1
        Ch_In_H = True
        In_High = i_high
        Bar_In_High = Bar_i_high
        In_Dir_small = -1
        if con_first == 2:
            In_Dir_small = 1
        if not CF_In_low:
            In_Dir_Big = 1

    if na(In_Low) and (not na(i_low)) and cf_low_in and barstate.isconfirmed:
        i_high = high
        Bar_i_high = bar_index
        CF_In_low = True
        con_first += 1
        Ch_In_L = True
        In_Low = i_low
        Bar_In_Low = Bar_i_low
        In_Dir_small = 1
        if con_first == 2:
            In_Dir_small = -1
        if not CF_In_High:
            In_Dir_Big = -1

    if CF_In_High and CF_In_low and barstate.isconfirmed:
        con_first = 0

    if not CF_In_High and high >= i_high[1] or In_ChoCH_Up or I_BoS_Up:
        i_low = na
    if not CF_In_low and low <= i_low[1] or In_ChoCH_Down or I_BoS_Down:
        i_high = na

    if In_ChoCH_Up or I_BoS_Up:
        if Bar_In_Low > Bar_i_high[1]:
            i_high = high
            Bar_i_high = bar_index

    if In_ChoCH_Down or I_BoS_Down:
        if Bar_In_High > Bar_i_low[1]:
            i_low = low
            Bar_i_low = bar_index

    if In_Break_Down and CF_In_High and (In_Dir_Big == 1):
        In_Dir_Big = -1
        In_skip = True
    if not In_skip and In_Break_Up and CF_In_low and (In_Dir_Big == -1):
        In_Dir_Big = 1

    cf_ud = I_BoS_Up or In_ChoCH_Up or I_BoS_Down or In_ChoCH_Down
    if Turn_off and Show_Structure and (CF_In_low or CF_In_low[1]) and cf_ud:
        bar = Bar_In_Low if CF_In_low else Bar_In_Low[1]
        PP = In_Low if CF_In_low else In_Low[1]
        label.new(bar, PP, xloc=xloc.bar_index, text='●', color=TRANSP, style=label.style_label_center, textcolor=Color_Mark_Swing, size=get_text_style(sw_Size))
    if Turn_off and Show_Structure and (CF_In_High or CF_In_High[1]) and cf_ud:
        bar = Bar_In_High if CF_In_High else Bar_In_High[1]
        PP = In_High if CF_In_High else In_High[1]
        label.new(bar, PP, xloc=xloc.bar_index, text='●', color=TRANSP, style=label.style_label_center, textcolor=Color_Mark_Swing, size=get_text_style(sw_Size))

    In_H_line: PersistentSeries[Line] = na(Line)
    In_L_line: PersistentSeries[Line] = na(Line)
    In_H_lbl: PersistentSeries[Label] = na(Line)
    In_L_lbl: PersistentSeries[Label] = na(Line)

    if Turn_off and Show_Structure and CF_In_High:
        line.delete(In_H_line[1])
        In_H_line = line.new(time[bar_index - Bar_In_High], In_High, time_set, In_High, xloc=xloc.bar_time, color=In_up_color, style=get_line_style(In_Line_style))
        label.delete(In_H_lbl[1])
        txt = 'BOS' if In_Dir_Big == 1 else 'MSS'
        In_H_lbl = label.new(bar_index + distance_bar_label, In_High, txt, xloc=xloc.bar_index, color=TRANSP, textcolor=In_up_color, style=label.style_label_down, size=In_Size_CF, textalign=text.align_center)

    if Turn_off and Show_Structure and CF_In_low:
        line.delete(In_L_line[1])
        In_L_line = line.new(time[bar_index - Bar_In_Low], In_Low, time_set, In_Low, xloc=xloc.bar_time, color=In_down_color, style=get_line_style(In_Line_style))
        label.delete(In_L_lbl[1])
        txt = 'BOS' if In_Dir_Big == -1 else 'MSS'
        In_L_lbl = label.new(bar_index + distance_bar_label, In_Low, txt, xloc=xloc.bar_index, color=TRANSP, textcolor=In_down_color, style=label.style_label_up, size=In_Size_CF, textalign=text.align_center)

    if Turn_off and Show_Structure and (not CF_In_High):
        line.delete(In_H_line[1])
        label.delete(In_H_lbl)
    if not CF_In_low:
        line.delete(In_L_line[1])
        label.delete(In_L_lbl)

    In_line_Eq: PersistentSeries[Line] = na(Line)
    In_lbl_Eq: PersistentSeries[Label] = na(Line)
    Premium: Persistent[float] = na(float)
    Discount: Persistent[float] = na(float)
    In_line_Eq2: PersistentSeries[Line] = na(Line)
    In_lbl_Eq2: PersistentSeries[Label] = na(Line)
    Premium2: Persistent[float] = na(float)
    Discount2: Persistent[float] = na(float)

    Pre_Dis_Cal = Pre_Dis / 100
    Pre_Dis_Cal2 = Pre_Dis2 / 100
    if CF_In_low and (not CF_In_High):
        Discount = i_high - math.abs(Pre_Dis_Cal * (i_high - In_Low))
        text_pre_dis: str = "% Discount"
        if EQ_con:
            Discount2 = i_high - math.abs(Pre_Dis_Cal2 * (i_high - In_Low))
        if Turn_off and Show_Structure:
            line.delete(In_line_Eq[1])
            label.delete(In_lbl_Eq[1])
            Bar_Eq = Bar_In_High if Bar_In_High < Bar_In_Low else Bar_In_Low
            In_line_Eq = line.new(time[bar_index - Bar_Eq], Discount, time_set, Discount, xloc=xloc.bar_time, color=color_Eq_In, style=get_line_style(In_Line_style))
            In_lbl_Eq = label.new(bar_index + distance_bar_label, Discount, string.tostring(Pre_Dis) + text_pre_dis, xloc=xloc.bar_index, color=TRANSP, textcolor=In_up_color, style=label.style_label_up, size=In_Size_CF)
            if EQ_con:
                line.delete(In_line_Eq2[1])
                label.delete(In_lbl_Eq2[1])
                In_line_Eq2 = line.new(time[bar_index - Bar_Eq], Discount2, time_set, Discount2, xloc=xloc.bar_time, color=color_Eq_In, style=get_line_style(In_Line_style))
                In_lbl_Eq2 = label.new(bar_index + distance_bar_label, Discount2, string.tostring(Pre_Dis2) + text_pre_dis, xloc=xloc.bar_index, color=TRANSP, textcolor=In_up_color, style=label.style_label_up, size=In_Size_CF)

    if CF_In_High and (not CF_In_low):
        Premium = i_low + Pre_Dis_Cal * (In_High - i_low)
        text_pre_dis: str = "% Premium"
        if EQ_con:
            Premium2 = i_low + Pre_Dis_Cal2 * (In_High - i_low)
        if Turn_off and Show_Structure:
            line.delete(In_line_Eq[1])
            label.delete(In_lbl_Eq[1])
            Bar_Eq = Bar_In_High if Bar_In_High < Bar_In_Low else Bar_In_Low
            In_line_Eq = line.new(time[bar_index - Bar_Eq], Premium, time_set, Premium, xloc=xloc.bar_time, color=color_Eq_In, style=get_line_style(In_Line_style))
            In_lbl_Eq = label.new(bar_index + distance_bar_label, Premium, string.tostring(Pre_Dis) + text_pre_dis, xloc=xloc.bar_index, color=TRANSP, textcolor=In_down_color, style=label.style_label_down, size=In_Size_CF)
            if EQ_con:
                line.delete(In_line_Eq2[1])
                label.delete(In_lbl_Eq2[1])
                In_line_Eq2 = line.new(time[bar_index - Bar_Eq], Premium2, time_set, Premium2, xloc=xloc.bar_time, color=color_Eq_In, style=get_line_style(In_Line_style))
                In_lbl_Eq2 = label.new(bar_index + distance_bar_label, Premium2, string.tostring(Pre_Dis2) + text_pre_dis, xloc=xloc.bar_index, color=TRANSP, textcolor=In_down_color, style=label.style_label_down, size=In_Size_CF)

    if CF_In_low and CF_In_High:
        Premium = In_Low + Pre_Dis_Cal * (In_High - In_Low)
        Discount = In_High - math.abs(Pre_Dis_Cal * (In_High - In_Low))
        if EQ_con:
            Premium2 = In_Low + Pre_Dis_Cal2 * (In_High - In_Low)
            Discount2 = In_High - math.abs(Pre_Dis_Cal2 * (In_High - In_Low))
        if Turn_off and Show_Structure:
            Equilibrium = Discount if In_Dir_Big == 1 else Premium
            text_pre_dis = '% Premium' if In_Dir_Big == -1 else '% Discount'
            col_text = In_down_color if In_Dir_Big == -1 else In_up_color
            style_txt = label.style_label_down if In_Dir_Big == -1 else label.style_label_up
            line.delete(In_line_Eq[1])
            label.delete(In_lbl_Eq[1])
            Bar_Eq = Bar_In_High if Bar_In_High < Bar_In_Low else Bar_In_Low
            In_line_Eq = line.new(time[bar_index - Bar_Eq], Equilibrium, time_set, Equilibrium, xloc=xloc.bar_time, color=color_Eq_In, style=get_line_style(In_Line_style))
            In_lbl_Eq = label.new(bar_index + distance_bar_label, Equilibrium, string.tostring(Pre_Dis) + text_pre_dis, xloc=xloc.bar_index, color=TRANSP, textcolor=col_text, style=style_txt, size=In_Size_CF)
            if EQ_con:
                Equilibrium2 = Discount2 if In_Dir_Big == 1 else Premium2
                line.delete(In_line_Eq2[1])
                label.delete(In_lbl_Eq2[1])
                In_line_Eq2 = line.new(time[bar_index - Bar_Eq], Equilibrium2, time_set, Equilibrium2, xloc=xloc.bar_time, color=color_Eq_In, style=get_line_style(In_Line_style))
                In_lbl_Eq2 = label.new(bar_index + distance_bar_label, Equilibrium2, string.tostring(Pre_Dis2) + text_pre_dis, xloc=xloc.bar_index, color=TRANSP, textcolor=col_text, style=style_txt, size=In_Size_CF)

    if Turn_off and Show_Structure and (not CF_In_High) or not CF_In_low:
        line.delete(In_line_Eq[1])
        label.delete(In_lbl_Eq[1])
        if EQ_con:
            line.delete(In_line_Eq2[1])
            label.delete(In_lbl_Eq2[1])

    his_dem_lid: Persistent[list[float]] = array.new_float(0, na)
    his_Dbar_left: Persistent[list[int]] = array.new_int(0, na)
    his_Dbar_right: Persistent[list[int]] = array.new_int(0, na)
    his_sup_lid: Persistent[list[float]] = array.new_float(0, na)
    his_Sbar_left: Persistent[list[int]] = array.new_int(0, na)
    his_Sbar_right: Persistent[list[int]] = array.new_int(0, na)

    line_his_lid_s: Persistent[list[Line]] = array.new_line(10, na)
    line_his_lid_d: Persistent[list[Line]] = array.new_line(10, na)
    label_his_lid_s: Persistent[list[Label]] = array.new_label(10, na)
    label_his_lid_d: Persistent[list[Label]] = array.new_label(10, na)

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

    up_trend: Persistent[bool] = False
    down_trend: Persistent[bool] = False

    if Follow_trend and barstate.isconfirmed:
        if not up_trend and In_Dir_Big == 1:
            up_trend = True
            down_trend = False
        if not down_trend and In_Dir_Big == -1:
            down_trend = True
            up_trend = False

    if not Follow_trend and (not up_trend) and barstate.isconfirmed:
        up_trend = True
        down_trend = True

    if break_dem and close > value_dem_lid and (open > value_dem_lid) and barstate.isconfirmed and (strategy.position_size == 0):
        if B_long:
            con_buy = True
            pre_dem_lid = value_dem_lid
            pre2_bar_Dlid_left = pre_bar_Dlid_left
            pre2_bar_Dlid_right = pre_bar_Dlid_right
        if pending_sell and cancel_pending_A:
            strategy.cancel('Short ' + string.tostring(c_order_sell))
            alert('Cancel Pending Short', alert.freq_all)
            cencel_sell = True
            pending_sell = False
        con_sell = False

    if B_long and barstate.isconfirmed and (close < value_dem_lid or (not con_time and con_time[1])):
        con_buy = False

    if not na(array.get(dfvg_R2_bot, 0)) and value_dem_lid < array.get(dfvg_R2_bot, 0) and up_trend:
        FVG_gap_buy = math.abs(array.get(dfvg_R2_top, 0) - array.get(dfvg_bot, 0))
        Con_gap_buy = FVG_gap_buy >= atr_check_FVG_min and FVG_gap_buy <= atr_check_FVG_max
        if con_buy[1] and Con_gap_buy:
            EQ_entry_buy = array.get(dfvg_R2_bot, 0) <= Discount and array.get(dfvg_R2_bot, 0) >= Discount2 if Follow_trend and EQ_con else True
            Size_FVG_dem = math.abs(array.get(dfvg_top, 0) - array.get(dfvg_bot, 0))
            size_FVG_con_dem = not Filter_size_FVG or (Filter_size_FVG and Size_FVG_dem >= Check_min_FVG and (Size_FVG_dem <= Check_max_FVG))
            Size_iFVG_dem = math.abs(array.get(dfvg_R2_top, 0) - array.get(dfvg_R2_bot, 0))
            size_iFVG_con_dem = not Filter_size_iFVG or (Filter_size_iFVG and Size_iFVG_dem >= Check_min_iFVG and (Size_iFVG_dem <= Check_max_iFVG))

            con_mix_dem = True if Con_FVG_mix else array.get(dfvg_bot, 0) >= array.get(dfvg_R2_top, 0) if not iFVG_be_FVG else array.get(dfvg_bot, 0) < array.get(dfvg_R2_top, 0)
            if EQ_entry_buy and size_FVG_con_dem and size_iFVG_con_dem and con_mix_dem:
                Check_gap_buy = True

    if con_buy and Check_gap_buy:
        buy_signal = True
        con_buy = False
        if B_long:
            value_unshift_noremove(his_dem_lid, pre_dem_lid, his_Dbar_left, pre2_bar_Dlid_left, his_Dbar_right, pre2_bar_Dlid_right)
        if Turn_off:
            lbl_fvg = 'FVG' if lbl_SnD else ''
            lbl_ifvg = 'iFVG' if lbl_SnD else ''
            dfvg_his = box.new(xloc=xloc.bar_time, left=array.get(dfvg_bar, 0), top=array.get(dfvg_top, 0), right=time + n_bar, bottom=array.get(dfvg_bot, 0), border_color=Col_fvg_mit, bgcolor=Col_fvg_mit, text=lbl_fvg, text_size=get_text_style(Size_SnD), text_color=Col_SnD, text_halign=text.align_right, text_valign=text.align_center)
            d_ifvg_his = box.new(xloc=xloc.bar_time, left=array.get(dfvg_bar_R2, 0), top=array.get(dfvg_R2_top, 0), right=time + n_bar, bottom=array.get(dfvg_R2_bot, 0), border_color=Col_ifvg_mit, bgcolor=Col_ifvg_mit, text=lbl_ifvg, text_size=get_text_style(Size_SnD), text_color=Col_SnD, text_halign=text.align_right, text_valign=text.align_center)

            FVG_d_bot = array.get(dfvg_bot, 0)
            iFVG_d_top = array.get(dfvg_R2_top, 0)
            mid_d_both = (FVG_d_bot + iFVG_d_top) / 2
            gap_value_min = atr_check_FVG_min / 2
            gap_value_max = atr_check_FVG_max / 2
            if FVG_min_ATR > 0:
                box.new(xloc=xloc.bar_time, left=time - gap_bar, top=mid_d_both + gap_value_min, right=time + gap_bar, bottom=mid_d_both - gap_value_min, border_color=gap_col_min, bgcolor=gap_col_min)
            box.new(xloc=xloc.bar_time, left=time - gap_bar, top=mid_d_both + gap_value_max, right=time + gap_bar, bottom=mid_d_both - gap_value_max, border_color=gap_col_max, bgcolor=gap_col_max, text='Gap', text_size=size.tiny, text_color=Col_SnD, text_halign=text.align_center, text_valign=text.align_center)

    if break_sup and close < value_sup_lid and (open < value_sup_lid) and barstate.isconfirmed and (strategy.position_size == 0):
        if S_short:
            con_sell = True
            pre_sup_lid = value_sup_lid
            pre2_bar_Slid_left = pre_bar_Slid_left
            pre2_bar_Slid_right = pre_bar_Slid_right
        if pending_buy and cancel_pending_A:
            strategy.cancel('Long ' + string.tostring(c_order_buy))
            alert('Cancel Pending Long', alert.freq_all)
            cencel_buy = True
            pending_buy = False
        con_buy = False

    if S_short and barstate.isconfirmed and (close > value_sup_lid or (not con_time and con_time[1])):
        con_sell = False

    if not na(array.get(sfvg_R2_top, 0)) and value_sup_lid > array.get(sfvg_R2_top, 0) and down_trend:
        FVG_gap_sell = math.abs(array.get(sfvg_R2_bot, 0) - array.get(sfvg_top, 0))
        Con_gap_sell = FVG_gap_sell >= atr_check_FVG_min and FVG_gap_sell <= atr_check_FVG_max
        if con_sell[1] and Con_gap_sell:
            EQ_entry_sell = array.get(sfvg_R2_top, 0) >= Premium and array.get(sfvg_R2_top, 0) <= Premium2 if Follow_trend and EQ_con else True
            Size_FVG_sup = math.abs(array.get(sfvg_top, 0) - array.get(sfvg_bot, 0))
            size_FVG_con_sup = not Filter_size_FVG or (Filter_size_FVG and Size_FVG_sup >= Check_min_FVG and (Size_FVG_sup <= Check_max_FVG))
            Size_iFVG_sup = math.abs(array.get(sfvg_R2_top, 0) - array.get(sfvg_R2_bot, 0))
            size_iFVG_con_sup = not Filter_size_iFVG or (Filter_size_iFVG and Size_iFVG_sup >= Check_min_iFVG and (Size_iFVG_sup <= Check_max_iFVG))
            con_mix_sup = True if Con_FVG_mix else array.get(sfvg_top, 0) <= array.get(sfvg_R2_bot, 0) if not iFVG_be_FVG else array.get(sfvg_top, 0) > array.get(sfvg_R2_bot, 0)
            if EQ_entry_sell and size_FVG_con_sup and size_iFVG_con_sup and con_mix_sup:
                Check_gap_sell = True

    if con_sell and Check_gap_sell:
        sell_signal = True
        con_sell = False
        if S_short:
            value_unshift_noremove(his_sup_lid, pre_sup_lid, his_Sbar_left, pre2_bar_Slid_left, his_Sbar_right, pre2_bar_Slid_right)
        if Turn_off:
            lbl_fvg = 'FVG' if lbl_SnD else ''
            lbl_ifvg = 'iFVG' if lbl_SnD else ''
            sfvg_his = box.new(xloc=xloc.bar_time, left=array.get(sfvg_bar, 0), top=array.get(sfvg_top, 0), right=time + n_bar, bottom=array.get(sfvg_bot, 0), border_color=Col_fvg_mit2, bgcolor=Col_fvg_mit2, text=lbl_fvg, text_size=get_text_style(Size_SnD), text_color=Col_SnD, text_halign=text.align_right, text_valign=text.align_center)
            s_ifvg_his = box.new(xloc=xloc.bar_time, left=array.get(sfvg_bar_R2, 0), top=array.get(sfvg_R2_top, 0), right=time + n_bar, bottom=array.get(sfvg_R2_bot, 0), border_color=Col_ifvg_mit2, bgcolor=Col_ifvg_mit2, text=lbl_ifvg, text_size=get_text_style(Size_SnD), text_color=Col_SnD, text_halign=text.align_right, text_valign=text.align_center)

            FVG_s_top = array.get(sfvg_top, 0)
            iFVG_s_bot = array.get(sfvg_R2_bot, 0)
            mid_s_both = (FVG_s_top + iFVG_s_bot) / 2
            gap_value_min = atr_check_FVG_min / 2
            gap_value_max = atr_check_FVG_max / 2
            if FVG_min_ATR > 0:
                box.new(xloc=xloc.bar_time, left=time - gap_bar, top=mid_s_both + gap_value_min, right=time + gap_bar, bottom=mid_s_both - gap_value_min, border_color=gap_col_min, bgcolor=gap_col_min)
            box.new(xloc=xloc.bar_time, left=time - gap_bar, top=mid_s_both + gap_value_max, right=time + gap_bar, bottom=mid_s_both - gap_value_max, border_color=gap_col_max, bgcolor=gap_col_max, text='Gap', text_size=size.tiny, text_color=Col_SnD, text_halign=text.align_center, text_valign=text.align_center)

    if strategy.position_size > 0:
        pending_buy = False
    if strategy.closedtrades > strategy.closedtrades[1] and pending_buy and barstate.isconfirmed:
        im_buy_signal = True
        pending_buy = False

    if strategy.position_size < 0:
        pending_sell = False
    if strategy.closedtrades > strategy.closedtrades[1] and pending_sell and barstate.isconfirmed:
        im_sell_signal = True
        pending_sell = False

    if barstate.isconfirmed and cancel_pending_B and (buy_signal or sell_signal) or (cancel_pending_C and con_time[1] and (not con_time)):
        if pending_buy:
            strategy.cancel('Long ' + string.tostring(c_order_buy))
            alert('Cancel Pending Long', alert.freq_all)
            pending_buy = False
            cencel_buy = True
        if pending_sell:
            strategy.cancel('Short ' + string.tostring(c_order_sell))
            alert('Cancel Pending Short', alert.freq_all)
            pending_sell = False
            cencel_sell = True

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

    if buy_signal and up_trend and B_long and barstate.isconfirmed and con_time and con_date:
        sl_cal_long = array.get(dfvg_R2_bot, 0)
        entry_b = array.get(dfvg_R2_top, 0)
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
        time_buy = time
        array.unshift(tp_buy, take_profit_long)
        array.unshift(sl_buy, stop_loss_long)

    if sell_signal and down_trend and S_short and barstate.isconfirmed and con_time and con_date:
        sl_cal_short = array.get(sfvg_R2_top, 0)
        entry_s = array.get(sfvg_R2_bot, 0)
        open_short = entry_s + math.abs(fibo_entry / 100 * (sl_cal_short - entry_s))
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
        time_sell = time
        array.unshift(tp_sell, take_profit_short)
        array.unshift(sl_sell, stop_loss_short)

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

    In_Size_fibo = get_text_style(Size_SnD)

    if Entry_box and (strategy.position_size > 0 or im_buy_signal) and barstate.isconfirmed and Turn_off:
        if strategy.opentrades.entry_price(strategy.opentrades - 1) == open_long or cancel_pending_A or cancel_pending_B or im_buy_signal:
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
            box_entrybuy_1_his = box.new(xloc=xloc.bar_time, left=time_buy, top=take_profit_long, right=time + n_bar, bottom=open_long, border_color=col_1, bgcolor=col_1)
            box_entrybuy_2_his = box.new(xloc=xloc.bar_time, left=time_buy, top=open_long, right=time + n_bar, bottom=stop_loss_long, border_color=col_2, bgcolor=col_2)
            lbl_entry_his = label.new(bar_index + 5, open_long, string.tostring(open_long, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)
            lbl_tp_his = label.new(bar_index + 5, take_profit_long, string.tostring(take_profit_long, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)
            lbl_sl_his = label.new(bar_index + 5, stop_loss_long, string.tostring(stop_loss_long, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)
    if Entry_box and cencel_buy and barstate.isconfirmed and Turn_off:
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
        box_entrybuy_1_his = box.new(xloc=xloc.bar_time, left=time_buy[1], top=take_profit_long[1], right=time_buy[1] + n_bar, bottom=open_long[1], border_color=col_1, bgcolor=col_1)
        box_entrybuy_2_his = box.new(xloc=xloc.bar_time, left=time_buy[1], top=open_long[1], right=time_buy[1] + n_bar, bottom=stop_loss_long[1], border_color=col_2, bgcolor=col_2)
        lbl_entry_his = label.new(time_buy[1] + n_bar, open_long[1], string.tostring(open_long[1], format.mintick), xloc=xloc.bar_time, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)
        lbl_tp_his = label.new(time_buy[1] + n_bar, take_profit_long[1], string.tostring(take_profit_long[1], format.mintick), xloc=xloc.bar_time, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)
        lbl_sl_his = label.new(time_buy[1] + n_bar, stop_loss_long[1], string.tostring(stop_loss_long[1], format.mintick), xloc=xloc.bar_time, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)

    if Entry_box and (strategy.position_size < 0 or im_sell_signal) and barstate.isconfirmed and Turn_off:
        if strategy.opentrades.entry_price(strategy.opentrades - 1) == open_short or cancel_pending_A or cancel_pending_B or im_sell_signal:
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
            box_entrysell_1_his = box.new(xloc=xloc.bar_time, left=time_sell, top=take_profit_short, right=time + n_bar, bottom=open_short, border_color=col_1, bgcolor=col_1)
            box_entrysell_2_his = box.new(xloc=xloc.bar_time, left=time_sell, top=open_short, right=time + n_bar, bottom=stop_loss_short, border_color=col_2, bgcolor=col_2)
            lbl_entry_his = label.new(bar_index + 5, open_short, string.tostring(open_short, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)
            lbl_tp_his = label.new(bar_index + 5, take_profit_short, string.tostring(take_profit_short, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)
            lbl_sl_his = label.new(bar_index + 5, stop_loss_short, string.tostring(stop_loss_short, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)
    if Entry_box and cencel_sell and barstate.isconfirmed and Turn_off:
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
        box_entrysell_1_his = box.new(xloc=xloc.bar_time, left=time_sell[1], top=take_profit_short[1], right=time_sell[1] + n_bar, bottom=open_short[1], border_color=col_1, bgcolor=col_1)
        box_entrysell_2_his = box.new(xloc=xloc.bar_time, left=time_sell[1], top=open_short[1], right=time_sell[1] + n_bar, bottom=stop_loss_short[1], border_color=col_2, bgcolor=col_2)
        lbl_entry_his = label.new(time_sell[1] + n_bar, open_short[1], string.tostring(open_short[1], format.mintick), xloc=xloc.bar_time, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)
        lbl_tp_his = label.new(time_sell[1] + n_bar, take_profit_short[1], string.tostring(take_profit_short[1], format.mintick), xloc=xloc.bar_time, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)
        lbl_sl_his = label.new(time_sell[1] + n_bar, stop_loss_short[1], string.tostring(stop_loss_short[1], format.mintick), xloc=xloc.bar_time, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)

    if Entry_box and buy_signal and barstate.isconfirmed and Turn_off:
        box.delete(box_entry_t1[1])
        box.delete(box_entry_t2[1])
        label.delete(lbl_entry_t[1])
        label.delete(lbl_tp_t[1])
        label.delete(lbl_sl_t[1])
        box_entry_t1 = box.new(xloc=xloc.bar_time, left=time_buy, top=take_profit_long, right=time + n_bar, bottom=open_long, border_color=col_1, bgcolor=col_1)
        box_entry_t2 = box.new(xloc=xloc.bar_time, left=time_buy, top=open_long, right=time + n_bar, bottom=stop_loss_long, border_color=col_2, bgcolor=col_2)
        lbl_entry_t = label.new(bar_index + 5, open_long, string.tostring(open_long, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)
        lbl_tp_t = label.new(bar_index + 5, take_profit_long, string.tostring(take_profit_long, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)
        lbl_sl_t = label.new(bar_index + 5, stop_loss_long, string.tostring(stop_loss_long, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)
    if Entry_box and sell_signal and barstate.isconfirmed and Turn_off:
        box.delete(box_entrysell_1_his[1])
        box.delete(box_entry_t2[1])
        label.delete(lbl_entry_t[1])
        label.delete(lbl_tp_t[1])
        label.delete(lbl_sl_t[1])
        box_entry_t1 = box.new(xloc=xloc.bar_time, left=time_sell, top=take_profit_short, right=time + n_bar, bottom=open_short, border_color=col_1, bgcolor=col_1)
        box_entry_t2 = box.new(xloc=xloc.bar_time, left=time_sell, top=open_short, right=time + n_bar, bottom=stop_loss_short, border_color=col_2, bgcolor=col_2)
        lbl_entry_t = label.new(bar_index + 5, open_short, string.tostring(open_short, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)
        lbl_tp_t = label.new(bar_index + 5, take_profit_short, string.tostring(take_profit_short, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)
        lbl_sl_t = label.new(bar_index + 5, stop_loss_short, string.tostring(stop_loss_short, format.mintick), xloc=xloc.bar_index, color=TRANSP, textcolor=Col_SnD, style=label.style_label_center, size=In_Size_fibo)

    if Show_result and barstate.isconfirmed and Turn_off:
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
    if Show_result and Total_all > Total_all[1] and barstate.isconfirmed and Turn_off:
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

    if Turn_off:
        if B_long and array.size(his_dem_lid) > 0:
            for i in pine_range(0, array.size(his_dem_lid) - 1):
                if array.size(line_his_lid_d) - 1 < i or na(array.get(his_dem_lid, i)):
                    break
                line.delete(array.get(line_his_lid_d, i))
                label.delete(array.get(label_his_lid_d, i))
                x_value = array.get(his_Dbar_left, i)
                y_value = array.get(his_dem_lid, i)
                rigth_time = array.get(his_Dbar_right, i)
                lbl_time = (x_value + rigth_time) / 2
                array.set(line_his_lid_d, i, line.new(x_value, y_value, rigth_time, y_value, xloc=xloc.bar_time, color=Lid_color, style=get_line_style(Lid_style)))
                array.set(label_his_lid_d, i, label.new(lbl_time, y_value, xloc=xloc.bar_time, text=txt_lid, color=TRANSP, textcolor=Lid_txt_color, size=txt_size, style=label.style_label_center))

        if S_short and array.size(his_sup_lid) > 0:
            for i in pine_range(0, array.size(his_sup_lid) - 1):
                if array.size(line_his_lid_s) - 1 < i or na(array.get(his_sup_lid, i)):
                    break
                line.delete(array.get(line_his_lid_s, i))
                label.delete(array.get(label_his_lid_s, i))
                x_value = array.get(his_Sbar_left, i)
                y_value = array.get(his_sup_lid, i)
                rigth_time = array.get(his_Sbar_right, i)
                lbl_time = (x_value + rigth_time) / 2
                array.set(line_his_lid_s, i, line.new(x_value, y_value, rigth_time, y_value, xloc=xloc.bar_time, color=Lid_color, style=get_line_style(Lid_style)))
                array.set(label_his_lid_s, i, label.new(lbl_time, y_value, xloc=xloc.bar_time, text=txt_lid, color=TRANSP, textcolor=Lid_txt_color, size=txt_size, style=label.style_label_center))

    plot(In_Dir_Big, 'Trend', display=display.status_line)
    plot(Check_min_FVG if Filter_size_FVG else na, 'Filter Size FVG Min', color=color.rgb(0, 255, 98), display=display.status_line)
    plot(Check_max_FVG if Filter_size_FVG else na, 'Filter Size FVG Max', color=color.rgb(0, 255, 98), display=display.status_line)
    plot(Check_min_iFVG if Filter_size_iFVG else na, 'Filter Size iFVG Min', color=color.rgb(255, 0, 0), display=display.status_line)
    plot(Check_max_iFVG if Filter_size_iFVG else na, 'Filter Size iFVG Max', color=color.rgb(255, 0, 0), display=display.status_line)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
