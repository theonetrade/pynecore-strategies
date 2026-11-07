"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    array, bar_index, box, chart, close, color, extend, high, input, label,
    line, location, low, math, na, open, plotshape, script, shape, size, strategy, string, time,
    timeframe, xloc
)
from pynecore.types import Box, Line, Persistent, PersistentSeries, Series

g_SET: str = 'Time'
g_STRAT: str = 'Strategy'
g_VIS: str = 'Visuals'


@script.strategy('Captain Backtest Model [TFO]', 'Captain Backtest Model [TFO]', True, max_lines_count=500, max_labels_count=500, max_boxes_count=500, margin_long=0, margin_short=0, initial_capital=1000000, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    prev_range=input.session('0600-1000', 'Price Range', tooltip='The range from which the high and low will be tracked for bias', group=g_SET),
    take_by=input.session('1000-1115', 'Window to Determine Bias', tooltip='Price must take the high or low of the price range within this time window. Otherwise, will not determine a bias and will not trade for that session', group=g_SET),
    trade_window=input.session('1000-1600', 'Trade Window', tooltip='Time window to take trades', group=g_SET),
    retrace_1=input.bool(True, 'Wait for Retracement - Opposite Close Candles', tooltip='Wait for down close candles after long bias has been determined, or up close candles after short bias has been determined', group=g_STRAT),
    retrace_2=input.bool(True, 'Wait for Retracement - Took Previous High/Low', tooltip='Wait for price to take a previous candle low after long bias has been determined, or for price to take a previous candle high after short bias has been determined', group=g_STRAT),
    stop_orders=input.bool(False, 'Use Stop Orders', tooltip='When enabled, will only enter long setups once price has taken the previous candle\'s high (and vice versa), as opposed to entering immediately once all criteria are met', group=g_STRAT),
    fixed_rr=input.bool(True, 'Use Fixed R:R', tooltip='When enabled, will use the risk and reward inputs as stop loss and take profit orders. Otherwise, will hold until the trade window closes (EOD)', group=g_STRAT),
    risk=input.float(25, 'Risk (Points)', tooltip='Stop loss, specified in points', group=g_STRAT),
    reward=input.float(75, 'Reward (Points)', tooltip='Profit target, specified in points', group=g_STRAT),
    range_color=input.color(color.new(color.blue, 70), 'Price Range Color', group=g_VIS),
    show_bias=input.bool(True, 'Show Bias', inline='BIAS', tooltip='Display bias for the day', group=g_VIS),
    long_color=input.color(color.teal, '', inline='BIAS', group=g_VIS),
    short_color=input.color(color.red, '', inline='BIAS', group=g_VIS),
    draw_rr=input.bool(True, 'Draw Fixed R:R', tooltip='Draw risk to reward boxes relative to entry', group=g_VIS),
    draw_cutoff=input.bool(True, 'Draw Time Cutoff', tooltip='Draw the cutoff time for when price needs to take the range high or low', group=g_VIS)
):
    t_pre: Series = not na(time('', prev_range, 'America/New_York'))
    t_take: Series = not na(time('', take_by, 'America/New_York'))
    t_trade: Series = not na(time('', trade_window, 'America/New_York'))
    pre_h: Persistent[float] = na(float)
    pre_l: Persistent[float] = na(float)
    pre_box: Persistent[Box] = na(Box)
    pre_h_line: Persistent[Line] = na(Line)
    pre_l_line: Persistent[Line] = na(Line)
    bias: PersistentSeries[bool] = na(bool)
    long: PersistentSeries[bool] = False
    short: PersistentSeries[bool] = False
    opp_close: Persistent[bool] = False
    took_hl: Persistent[bool] = False
    buy_stop: Persistent[float] = na(float)
    sell_stop: Persistent[float] = na(float)
    entry: PersistentSeries[float] = na(float)
    entry_line: Persistent[Line] = na(Line)
    risk_box: Persistent[list[Box]] = array.new_box()
    reward_box: Persistent[list[Box]] = array.new_box()
    risk_price: Persistent[list[float]] = array.new_float()
    reward_price: Persistent[list[float]] = array.new_float()
    def rr_boxes(entry, long):
        __block_result__ = na
        if long:
            array.unshift(reward_box, box.new(time[1], entry + reward, time, entry, xloc=xloc.bar_time, bgcolor=color.new(long_color, 50), border_color=color.new(long_color, 50)))
            __block_result__ = array.unshift(risk_box, box.new(time[1], entry, time, entry - risk, xloc=xloc.bar_time, bgcolor=color.new(short_color, 50), border_color=color.new(short_color, 50)))
        else:
            array.unshift(reward_box, box.new(time[1], entry, time, entry - reward, xloc=xloc.bar_time, bgcolor=color.new(long_color, 50), border_color=color.new(long_color, 50)))
            __block_result__ = array.unshift(risk_box, box.new(time[1], entry + risk, time, entry, xloc=xloc.bar_time, bgcolor=color.new(short_color, 50), border_color=color.new(short_color, 50)))
        return __block_result__

    if t_pre:
        pre_h = high if na(pre_h) else math.max(pre_h, high)
        pre_l = low if na(pre_l) else math.min(pre_l, low)
        if not t_pre[1]:
            pre_box = box.new(time, high, time, low, xloc=xloc.bar_time, bgcolor=range_color, border_color=na, text=string.tostring(prev_range), text_color=range_color)
            pre_h_line = line.new(time, high, time, high, xloc=xloc.bar_time, color=color.new(range_color, 0))
            pre_l_line = line.new(time, low, time, low, xloc=xloc.bar_time, color=color.new(range_color, 0))
        else:
            box.set_top(pre_box, pre_h)
            box.set_rightbottom(pre_box, time, pre_l)
            line.set_y1(pre_h_line, pre_h)
            line.set_xy2(pre_h_line, time, pre_h)
            line.set_y1(pre_l_line, pre_l)
            line.set_xy2(pre_l_line, time, pre_l)
    if not t_trade and t_trade[1]:
        pre_h = na
        pre_l = na
        bias = na
        entry = na
        buy_stop = na
        sell_stop = na
        entry_line = na
        long = False
        short = False
        opp_close = False
        took_hl = False
        array.clear(reward_box)
        array.clear(risk_box)
    if t_take:
        if high > pre_h and na(bias):
            bias = True
            line.set_x2(pre_h_line, time)
            if show_bias:
                label.new(bar_index, high, 'Bias Long', textcolor=color.white, color=long_color)
        elif low < pre_l and na(bias):
            bias = False
            line.set_x2(pre_l_line, time)
            if show_bias:
                label.new(bar_index, low, 'Bias Short', textcolor=color.white, color=short_color, style=label.style_label_up)
    if not t_take and t_take[1]:
        if draw_cutoff:
            line.new(bar_index, high, bar_index, low, extend=extend.both, color=chart.fg_color, style=line.style_dotted)
        if na(bias):
            label.new(bar_index, high, 'Range Not Breached\nby 11:15', textcolor=chart.bg_color, color=chart.fg_color)
    plotshape(show_bias, color=long_color if bias == True else short_color if bias == False else na, location=location.bottom, size=size.small, style=shape.square)
    plotshape(long[1] and (not long[2]), color=long_color, location=location.belowbar, size=size.small, style=shape.triangleup)
    plotshape(short[1] and (not short[2]), color=short_color, location=location.abovebar, size=size.small, style=shape.triangledown)
    if t_trade:
        if not na(entry_line) and na(entry):
            line.set_x2(entry_line, time)
        if not retrace_1:
            opp_close = True
        else:
            if bias == True and close < open:
                opp_close = True
            if bias == False and close > open:
                opp_close = True
        if not retrace_2:
            took_hl = True
        else:
            if bias == True and low < low[1]:
                took_hl = True
            if bias == False and high > high[1]:
                took_hl = True
        if bias[1] == True and close > high[1] and opp_close and took_hl and (not long):
            long = True
            buy_stop = high
            if stop_orders:
                entry_line = line.new(time, buy_stop, time + timeframe.in_seconds() * 1000, buy_stop, xloc=xloc.bar_time, color=long_color)
        if bias[1] == False and close < low[1] and opp_close and took_hl and (not short):
            short = True
            sell_stop = low
            if stop_orders:
                entry_line = line.new(time, sell_stop, time + timeframe.in_seconds() * 1000, sell_stop, xloc=xloc.bar_time, color=short_color)
        if long == True and na(entry):
            strategy.entry('Long', strategy.long, stop=buy_stop if stop_orders else na)
        elif short == True and na(entry):
            strategy.entry('Short', strategy.short, stop=sell_stop if stop_orders else na)
        if fixed_rr:
            if strategy.position_size[1] == 0 and strategy.position_size != 0:
                if strategy.position_size > 0:
                    entry = buy_stop if stop_orders else open
                    array.unshift(risk_price, entry - risk)
                    array.unshift(reward_price, entry + reward)
                if strategy.position_size < 0:
                    entry = sell_stop if stop_orders else open
                    array.unshift(risk_price, entry + risk)
                    array.unshift(reward_price, entry - reward)
            if strategy.position_size > 0:
                strategy.exit('Long', comment='Exit Long', limit=array.get(reward_price, 0), stop=array.get(risk_price, 0))
                if draw_rr:
                    if fixed_rr and na(entry[2]) and (array.size(risk_box) == 0):
                        rr_boxes(entry, True)
                    if array.size(risk_box) > 0:
                        method_call('set_right', array.get(risk_box, 0), time)
                        method_call('set_right', array.get(reward_box, 0), time)
            if strategy.position_size < 0:
                strategy.exit('Short', comment='Exit Short', limit=array.get(reward_price, 0), stop=array.get(risk_price, 0))
                if draw_rr:
                    if fixed_rr and na(entry[2]) and (array.size(risk_box) == 0):
                        rr_boxes(entry, False)
                    if array.size(risk_box) > 0:
                        method_call('set_right', array.get(risk_box, 0), time)
                        method_call('set_right', array.get(reward_box, 0), time)
    if not t_trade and t_trade[1]:
        strategy.close_all('EOD')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
