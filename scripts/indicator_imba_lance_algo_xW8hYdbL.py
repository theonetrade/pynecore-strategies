"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, alertcondition, array, bar_index, close, color, dayofmonth, high,
    hour, input, label, line, linefill, location, low, math, minute, month, na, open, plot,
    plotshape, position, script, shape, size, string, syminfo, ta, table, text, time, timeframe,
    timestamp, year
)
from pynecore.types import Color, Label, Line, Persistent, PersistentSeries, Series, Table


@udt
class Strategy_settings:
    sensitivity: float = 0
    risk_percent: float = 1
    break_even_target: str = '1'
    tp1_percent: float = 0
    tp1_percent_fix: float = 0
    tp2_percent: float = 0
    tp2_percent_fix: float = 0
    tp3_percent: float = 0
    tp3_percent_fix: float = 0
    tp4_percent: float = 0
    tp4_percent_fix: float = 0
    fixed_stop: bool = False
    sl_percent: float = 0


@udt
class Trade:
    start_bar_index: int = 0
    side: str = na(str)
    market_order_comission: float = na(float)
    limit_order_comission: float = na(float)
    entry_price: float = na(float)
    entry_hit: bool = False
    sl_price: float = na(float)
    tp1_price: float = na(float)
    tp1_percent_fix: float = na(float)
    tp2_price: float = na(float)
    tp2_percent_fix: float = na(float)
    tp3_price: float = na(float)
    tp3_percent_fix: float = na(float)
    tp4_price: float = na(float)
    tp4_percent_fix: float = na(float)
    break_even_price: float = na(float)
    sl_hit: bool = False
    tp1_hit: bool = False
    tp2_hit: bool = False
    tp3_hit: bool = False
    tp4_hit: bool = False
    position_size_left: float = 100
    risk_percent: float = na(float)
    is_closed: bool = False
    close_price: float = 0
    can_break_even: bool = False
    force_closed: bool = False
    profit: float = 0
    risk_reward: float = na(float)
    entry_line: Line = na(Line)
    stoploss_line: Line = na(Line)
    target1_line: Line = na(Line)
    target2_line: Line = na(Line)
    target3_line: Line = na(Line)
    target4_line: Line = na(Line)


POSITION: str = 'POSITION'
TAKE_PROFITS: str = 'TAKE PROFITS'
STOP_LOSS: str = 'STOPLOSS'
rsi_group: str = 'RSI'
info_panel_group: str = 'INFOPANELS'
dev_settings: str = 'DEVELOPER MODE'


@script.indicator(title='[IMBA] ALGO', shorttitle='[IMBA] ALGO', overlay=True, max_lines_count=500, max_labels_count=500, max_bars_back=1, na_bool=True)
def main(
    strategy_input=input.string(title='STRATEGY', options=('MANUAL', 'UNIVERSAL 15m', '===============', '-------A-------', '-------B-------', '-------C-------', '-------D-------', '-------E-------', '-------F-------', '-------G-------', '-------H-------', '-------I-------', '-------J-------', '-------K-------', '-------L-------', '-------M-------', '-------N-------', '-------O-------', '-------P-------', '-------Q-------', '-------R-------', '-------S-------', 'SOL 5m', '-------T-------', '-------U-------', '-------V-------', '-------W-------', '-------X-------', '-------Y-------', '-------Z-------'), defval='MANUAL', tooltip='EN:\nTo manually configure the strategy, select MANUAL otherwise, changing the settings won\'t have any effect\nRU:\nЧтобы настроить стратегию вручную, выберите MANUAL в противном случае изменение настроек не будет иметь никакого эффекта'),
    sensitivity_input=input.float(title='Sensitive', step=0.1, defval=18),
    start_date_input=input.time(defval=timestamp('1 June 2023'), title='Start calculating date'),
    show_tp_enty_sl=input.bool(defval=True, title='Show', group=POSITION, inline='2.1'),
    fill_positions=input.bool(defval=True, title='Fill', group=POSITION, inline='2.1'),
    risk_percent_input=input.float(title='Risk %', step=1, defval=1, group=POSITION, tooltip='EN:\nMaximum allowable loss % of the deposit per 1 trade\nRU:\nМаксимально допустимая потеря % от депозита на 1 сделку'),
    break_even_target_input=input.string(title='BE target', options=('WITHOUT', '1', '2', '3'), defval='1', group=POSITION),
    initial_deposit_input=input.float(title='Initial deposit', defval=1000, step=100, group=POSITION),
    fixed_stop_input=input.bool(defval=False, title='Fixed stoploss %', group=STOP_LOSS, tooltip='EN:\nIf choosed: stoploss will be calculated manually \nIf NOT choosed: stoploss will be calculated automatic\nRU:\nЕсли выбрано: стоп будет рассчитываться вручную \nЕсли НЕ выбрано: стоп будет рассчитываться автоматически'),
    sl_percent_input=input.float(title='SL %', step=0.1, defval=0.0, group=STOP_LOSS),
    tp1_percent_input=input.float(title='TP 1', step=0.05, defval=1.0, minval=0, group=TAKE_PROFITS, inline='2.2'),
    tp1_percent_fix_input=input.float(title='Fix %', step=5, defval=40, group=TAKE_PROFITS, inline='2.2'),
    tp2_percent_input=input.float(title='TP 2', step=0.05, defval=2.0, minval=0, group=TAKE_PROFITS, inline='2.3'),
    tp2_percent_fix_input=input.float(title='Fix %', step=5, defval=30, group=TAKE_PROFITS, inline='2.3'),
    tp3_percent_input=input.float(title='TP 3', step=0.05, defval=3.0, minval=0, group=TAKE_PROFITS, inline='2.4'),
    tp3_percent_fix_input=input.float(title='Fix %', step=5, defval=20, group=TAKE_PROFITS, inline='2.4'),
    tp4_percent_input=input.float(title='TP 4', step=0.05, defval=4.0, minval=0, group=TAKE_PROFITS, inline='2.5'),
    tp4_percent_fix_input=input.float(title='Fix %', step=5, defval=10, group=TAKE_PROFITS, inline='2.5'),
    show_rsi=input.bool(defval=False, title='Show', group=rsi_group, inline='3.1'),
    len=input(title='Length', defval=14, group=rsi_group, inline='3.2'),
    overbought=input(title='Overbought', defval=78, group=rsi_group, inline='3.3'),
    oversold=input(title='Oversold', defval=22, group=rsi_group, inline='3.3'),
    show_profit_panel=input.bool(defval=True, title='Show profit panel', group=info_panel_group),
    show_strategy_panel=input.bool(defval=False, title='Show strategy panel', group=info_panel_group),
    show_old_panel=input.bool(defval=False, title='Show old panel', group=info_panel_group),
    show_dev_labels=input.bool(defval=False, title='Show', group=dev_settings, tooltip='Shows all possible events')
):
    def RoundUp(number, decimals):
        factor = math.pow(10, decimals)
        return math.ceil(number * factor) / factor

    def calc_rr(entry_price: float, sl_price: float, take_price: float):
        return (take_price - entry_price) / (entry_price - sl_price) if entry_price > sl_price else (entry_price - take_price) / (sl_price - entry_price)

    def create_trend_line(sensitivity: float, fib: float):
        high_line = ta.highest(high, cast_int(sensitivity))
        low_line = ta.lowest(low, cast_int(sensitivity))
        channel_range = high_line - low_line
        return high_line - channel_range * fib

    @method
    def calc_profit(trade: Trade, show_labels: bool):
        trade_info_label: Label = na(Label)
        entry_hit_label: Label = na(Label)
        tp1_hit_label: Label = na(Label)
        tp2_hit_label: Label = na(Label)
        tp3_hit_label: Label = na(Label)
        tp4_hit_label: Label = na(Label)
        sl_hit_label: Label = na(Label)
        be_hit_label: Label = na(Label)
        profit: float = 0.0
        if trade.side == 'LONG':
            if low <= trade.entry_price and (not trade.entry_hit):
                trade.start_bar_index = bar_index
                trade.entry_hit = True
                entry_hit_label = label.new(trade.start_bar_index, trade.entry_price, string.tostring('ENTRY HIT'), style=label.style_label_right)
                trade_info_label = label.new(bar_index, high, 'Trade info:' + '\nEntry: ' + string.tostring(trade.entry_price) + '\nTp1: ' + string.tostring(trade.tp1_price) + '\nTp2: ' + string.tostring(trade.tp2_price) + '\nTp3:' + string.tostring(trade.tp3_price) + '\nTp4: ' + string.tostring(trade.tp4_price) + '\nSl: ' + string.tostring(trade.sl_price))
            if high >= trade.tp1_price and (not trade.tp1_hit) and trade.entry_hit:
                trade.tp1_hit = True
                trade.position_size_left = trade.position_size_left - trade.tp1_percent_fix
                profit = profit + calc_rr(trade.entry_price, trade.sl_price, trade.tp1_price) * trade.tp1_percent_fix / 100 * trade.risk_percent
                tp1_hit_label = label.new(trade.start_bar_index, trade.tp1_price, string.tostring('TP1 HIT +') + string.tostring(profit, '#.##') + '%' + '\nPosition size %: ' + string.tostring(trade.position_size_left), style=label.style_label_right)
            if high >= trade.tp2_price and (not trade.tp2_hit) and trade.entry_hit:
                trade.tp2_hit = True
                trade.can_break_even = True
                trade.position_size_left = trade.position_size_left - trade.tp2_percent_fix
                profit = profit + calc_rr(trade.entry_price, trade.sl_price, trade.tp2_price) * trade.tp2_percent_fix / 100 * trade.risk_percent
                tp2_hit_label = label.new(trade.start_bar_index, trade.tp2_price, string.tostring('TP2 HIT +') + string.tostring(profit, '#.##') + '%' + '\nPosition size %: ' + string.tostring(trade.position_size_left), style=label.style_label_right)
            if high >= trade.tp3_price and (not trade.tp3_hit) and trade.entry_hit:
                trade.tp3_hit = True
                trade.position_size_left = trade.position_size_left - trade.tp3_percent_fix
                profit = profit + calc_rr(trade.entry_price, trade.sl_price, trade.tp3_price) * trade.tp3_percent_fix / 100 * trade.risk_percent
                tp3_hit_label = label.new(trade.start_bar_index, trade.tp3_price, string.tostring('TP3 HIT +') + string.tostring(profit, '#.##') + '%' + '\nPosition size %: ' + string.tostring(trade.position_size_left), style=label.style_label_right)
            if high >= trade.tp4_price and (not trade.tp4_hit) and trade.entry_hit:
                trade.tp4_hit = True
                trade.is_closed = True
                trade.position_size_left = trade.position_size_left - trade.tp4_percent_fix
                profit = profit + calc_rr(trade.entry_price, trade.sl_price, trade.tp4_price) * trade.tp4_percent_fix / 100 * trade.risk_percent
                tp4_hit_label = label.new(trade.start_bar_index, trade.tp4_price, string.tostring('TP4 HIT +') + string.tostring(profit, '#.##') + '%' + '\nPosition size %: ' + string.tostring(trade.position_size_left), style=label.style_label_right)
            if high >= trade.break_even_price and (not trade.can_break_even) and trade.entry_hit:
                trade.can_break_even = True
            if trade.can_break_even and trade.entry_hit:
                if low <= trade.entry_price and (not close >= open) and (bar_index != trade.start_bar_index):
                    trade.is_closed = True
                    be_hit_label = label.new(bar_index, trade.entry_price, string.tostring('BE HIT'), style=label.style_label_left)
            if low <= trade.sl_price and (not trade.can_break_even) and trade.entry_hit and (bar_index != trade.start_bar_index):
                trade.sl_hit = True
                trade.is_closed = True
                profit = profit + -trade.risk_percent * trade.position_size_left / 100
                sl_hit_label = label.new(bar_index, trade.sl_price, string.tostring('SL HIT ') + string.tostring(profit, '#.##') + '%', color=color.red, style=label.style_label_left)
        else:
            if high >= trade.entry_price and (not trade.entry_hit):
                trade.start_bar_index = bar_index
                trade.entry_hit = True
                entry_hit_label = label.new(trade.start_bar_index, trade.entry_price, string.tostring('ENTRY HIT'), style=label.style_label_right)
                trade_info_label = label.new(bar_index, high, 'Trade info:' + '\nEntry: ' + string.tostring(trade.entry_price) + '\nTp1: ' + string.tostring(trade.tp1_price) + '\nTp2: ' + string.tostring(trade.tp2_price) + '\nTp3:' + string.tostring(trade.tp3_price) + '\nTp4: ' + string.tostring(trade.tp4_price) + '\nSl: ' + string.tostring(trade.sl_price))
            if low <= trade.tp1_price and (not trade.tp1_hit) and trade.entry_hit:
                trade.tp1_hit = True
                trade.position_size_left = trade.position_size_left - trade.tp1_percent_fix
                profit = profit + calc_rr(trade.entry_price, trade.sl_price, trade.tp1_price) * trade.tp1_percent_fix / 100 * trade.risk_percent
                tp1_hit_label = label.new(trade.start_bar_index, trade.tp1_price, string.tostring('TP1 HIT +') + string.tostring(profit, '#.##') + '%' + '\nPosition size %: ' + string.tostring(trade.position_size_left), style=label.style_label_right)
            if low <= trade.tp2_price and (not trade.tp2_hit) and trade.entry_hit:
                trade.tp2_hit = True
                trade.position_size_left = trade.position_size_left - trade.tp2_percent_fix
                profit = profit + calc_rr(trade.entry_price, trade.sl_price, trade.tp2_price) * trade.tp2_percent_fix / 100 * trade.risk_percent
                tp2_hit_label = label.new(trade.start_bar_index, trade.tp2_price, string.tostring('TP2 HIT +') + string.tostring(profit, '#.##') + '%' + '\nPosition size %: ' + string.tostring(trade.position_size_left), style=label.style_label_right)
            if low <= trade.tp3_price and (not trade.tp3_hit) and trade.entry_hit:
                trade.tp3_hit = True
                trade.position_size_left = trade.position_size_left - trade.tp3_percent_fix
                profit = profit + calc_rr(trade.entry_price, trade.sl_price, trade.tp3_price) * trade.tp3_percent_fix / 100 * trade.risk_percent
                tp3_hit_label = label.new(trade.start_bar_index, trade.tp3_price, string.tostring('TP3 HIT +') + string.tostring(profit, '#.##') + '%' + '\nPosition size %: ' + string.tostring(trade.position_size_left), style=label.style_label_right)
            if low <= trade.tp4_price and (not trade.tp4_hit) and trade.entry_hit:
                trade.tp4_hit = True
                trade.is_closed = True
                trade.position_size_left = trade.position_size_left - trade.tp4_percent_fix
                profit = profit + calc_rr(trade.entry_price, trade.sl_price, trade.tp4_price) * trade.tp4_percent_fix / 100 * trade.risk_percent
                tp4_hit_label = label.new(trade.start_bar_index, trade.tp4_price, string.tostring('TP4 HIT +') + string.tostring(profit, '#.##') + '%' + '\nPosition size %: ' + string.tostring(trade.position_size_left), style=label.style_label_right)
            if low <= trade.break_even_price and (not trade.can_break_even) and trade.entry_hit:
                trade.can_break_even = True
            if trade.can_break_even and trade.entry_hit:
                if high >= trade.entry_price and (not close <= open) and (bar_index != trade.start_bar_index):
                    trade.is_closed = True
                    be_hit_label = label.new(bar_index, trade.entry_price, string.tostring('BE HIT'), style=label.style_label_left)
            if high >= trade.sl_price and (not trade.can_break_even) and trade.entry_hit and (bar_index != trade.start_bar_index):
                trade.sl_hit = True
                trade.is_closed = True
                profit = profit + -trade.risk_percent * trade.position_size_left / 100
                sl_hit_label = label.new(bar_index, trade.sl_price, string.tostring('SL HIT ') + string.tostring(profit, '#.##') + '%', color=color.red, style=label.style_label_left)
        trade.profit = trade.profit + profit
        __block_result__ = na
        if not show_labels:
            label.delete(entry_hit_label)
            label.delete(tp1_hit_label)
            label.delete(tp2_hit_label)
            label.delete(tp3_hit_label)
            label.delete(tp4_hit_label)
            label.delete(sl_hit_label)
            label.delete(be_hit_label)
            __block_result__ = label.delete(trade_info_label)
        return __block_result__

    @method
    def close_trade(trade: Trade, show_labels: bool):
        profit: float = 0.0
        trade_closed_label: Label = na(Label)
        trade.force_closed = True
        if not trade.sl_hit:
            if trade.side == 'SHORT':
                trade.is_closed = True
                trade.close_price = close
                if close <= trade.entry_price:
                    percent_from_entry_to_close_price_at_trend_change = math.abs(close / trade.entry_price * 100)
                    percent_from_entry_to_sl_price = math.abs(trade.entry_price / trade.sl_price * 100)
                    profit = calc_rr(trade.entry_price, trade.sl_price, close) * trade.position_size_left / 100 * trade.risk_percent
                else:
                    profit = calc_rr(trade.entry_price, trade.sl_price, close) * trade.position_size_left / 100 * trade.risk_percent
                sign: str = '+' if profit >= 0 else na
                trade_closed_label = label.new(bar_index, high, string.tostring('TRADE CLOSED ') + sign + string.tostring(profit, '#.##') + '%')
            else:
                trade.is_closed = True
                trade.close_price = close
                if close <= trade.entry_price:
                    percent_from_entry_to_close_price_at_trend_change = math.abs((close / trade.entry_price - 1) * 100)
                    percent_from_entry_to_sl_price = math.abs((trade.entry_price / trade.sl_price - 1) * 100)
                    profit = -trade.risk_percent * (percent_from_entry_to_close_price_at_trend_change / percent_from_entry_to_sl_price) * trade.position_size_left / 100 + trade.profit
                else:
                    profit = calc_rr(trade.entry_price, trade.sl_price, close) * trade.position_size_left / 100 * trade.risk_percent
                sign: str = '+' if profit >= 0 else na
                trade_closed_label = label.new(bar_index, low, string.tostring('TRADE CLOSED ') + sign + string.tostring(profit, '#.##') + '%', style=label.style_label_up)
        if not show_labels:
            label.delete(trade_closed_label)
        trade.profit = trade.profit + profit
        return trade.profit

    def selector(strategy_name: str):
        strategy_settings: Strategy_settings = Strategy_settings()
        __switch__ = strategy_name
        if __switch__ == 'MANUAL':
            strategy_settings.sensitivity = 18
            strategy_settings.risk_percent = 1
            strategy_settings.break_even_target = '1'
            strategy_settings.tp1_percent = 1
            strategy_settings.tp1_percent_fix = 40
            strategy_settings.tp2_percent = 2
            strategy_settings.tp2_percent_fix = 30
            strategy_settings.tp3_percent = 3
            strategy_settings.tp3_percent_fix = 20
            strategy_settings.tp4_percent = 4
            strategy_settings.tp4_percent_fix = 10
            strategy_settings.fixed_stop = False
            strategy_settings.sl_percent = 0.0
        elif __switch__ == 'UNIVERSAL 15m':
            strategy_settings.sensitivity = 20
            strategy_settings.risk_percent = 1
            strategy_settings.break_even_target = '1'
            strategy_settings.tp1_percent = 1
            strategy_settings.tp1_percent_fix = 40
            strategy_settings.tp2_percent = 2
            strategy_settings.tp2_percent_fix = 30
            strategy_settings.tp3_percent = 3
            strategy_settings.tp3_percent_fix = 20
            strategy_settings.tp4_percent = 4
            strategy_settings.tp4_percent_fix = 10
            strategy_settings.fixed_stop = False
            strategy_settings.sl_percent = 0.0
        elif __switch__ == 'SOL 5m':
            strategy_settings.sensitivity = 20
            strategy_settings.risk_percent = 1
            strategy_settings.break_even_target = '1'
            strategy_settings.tp1_percent = 1
            strategy_settings.tp1_percent_fix = 40
            strategy_settings.tp2_percent = 2
            strategy_settings.tp2_percent_fix = 30
            strategy_settings.tp3_percent = 3
            strategy_settings.tp3_percent_fix = 20
            strategy_settings.tp4_percent = 4
            strategy_settings.tp4_percent_fix = 10
            strategy_settings.fixed_stop = False
            strategy_settings.sl_percent = 0.0
        return strategy_settings

    STRATEGIES: str = 'STRATEGIES'
    ENTRY: str = 'ENTRY'
    main_group: str = 'MAIN'
    fibo_lines_transparend: int = 60
    fill_best_transparend: int = 95
    fill_worst_transparend: int = 98
    high_line_color: Color = color.rgb(36, 255, 44, fibo_lines_transparend)
    fib_236_color: Color = color.rgb(130, 228, 74, fibo_lines_transparend)
    fib_382_color: Color = color.rgb(171, 224, 174, fibo_lines_transparend)
    fib_618_color: Color = color.rgb(235, 255, 51, fibo_lines_transparend)
    fib_786_color: Color = color.rgb(255, 131, 73, fibo_lines_transparend)
    low_line_color: Color = color.rgb(255, 82, 82, fibo_lines_transparend)
    high_best_fill_color: Color = color.rgb(48, 255, 55, fill_best_transparend)
    high_worst_fill_color: Color = color.rgb(37, 255, 44, fill_worst_transparend)
    low_best_fill_color: Color = color.rgb(255, 54, 54, fill_best_transparend)
    low_worst_fill_color: Color = color.rgb(255, 43, 43, fill_worst_transparend)
    tp_sl_entry_transparent: int = 30
    tp_color: Color = color.new(color.green, tp_sl_entry_transparent)
    entry_color: Color = color.rgb(120, 123, 134, tp_sl_entry_transparent)
    sl_color: Color = color.new(color.red, tp_sl_entry_transparent)
    line_style = line.style_dotted

    sensitivity: Persistent[float] = 18
    risk_percent: float = 1
    break_even_target: str = '2'
    tp1_percent: float = 0
    tp1_percent_fix: float = 0
    tp2_percent: float = 0
    tp2_percent_fix: float = 0
    tp3_percent: float = 0
    tp3_percent_fix: float = 0
    tp4_percent: float = 0
    tp4_percent_fix: float = 0
    fixed_stop: bool = False
    sl_percent: float = 0
    total_profit: Persistent[float] = 0.0
    trade_count: Persistent[int] = 0
    profit_trades: Persistent[int] = 0
    loss_trades: Persistent[int] = 0
    loss_streak: Persistent[int] = 0
    loss_in_a_row: Persistent[int] = 0
    win_streak: Persistent[int] = 0
    wins_in_a_row: Persistent[int] = 0
    first_trade_date: Persistent[int] = na(int)
    trade: Persistent[Trade] = na(Trade)
    is_long_trend_started: Persistent[bool] = False
    is_short_trend_started: Persistent[bool] = False
    is_trend_change: Persistent[bool] = na(bool)
    is_long_trend: PersistentSeries[bool] = False
    is_short_trend: Persistent[bool] = False
    can_long: Persistent[bool] = False
    can_short: Persistent[bool] = False
    trend_started_bar_index: Persistent[int] = na(int)
    tp1_line: Persistent[Line] = na(Line)
    tp1_label: Persistent[Label] = na(Label)
    tp2_line: Persistent[Line] = na(Line)
    tp2_label: Persistent[Label] = na(Label)
    tp3_line: Persistent[Line] = na(Line)
    tp3_label: Persistent[Label] = na(Label)
    tp4_line: Persistent[Line] = na(Line)
    tp4_label: Persistent[Label] = na(Label)
    entry_line: Persistent[Line] = na(Line)
    entry_label: Persistent[Label] = na(Label)
    close_line: Persistent[Line] = na(Line)
    sl_line: Persistent[Line] = na(Line)
    sl_label: Persistent[Label] = na(Label)
    lable_at_signal: Persistent[Label] = na(Label)
    signal_closed_bar: Persistent[int] = na(int)
    strategy_s: Persistent[Strategy_settings] = na(Strategy_settings)
    dep: Persistent[float] = initial_deposit_input
    strategy_s = Strategy_settings(sensitivity_input, risk_percent_input, break_even_target_input, tp1_percent_input, tp1_percent_fix_input, tp2_percent_input, tp2_percent_fix_input, tp3_percent_input, tp3_percent_fix_input, tp4_percent_input, tp4_percent_fix_input, fixed_stop_input, sl_percent_input) if strategy_input == 'MANUAL' else selector(strategy_input)
    sensitivity = strategy_s.sensitivity
    risk_percent = strategy_s.risk_percent
    break_even_target = strategy_s.break_even_target
    tp1_percent = strategy_s.tp1_percent
    tp1_percent_fix = strategy_s.tp1_percent_fix
    tp2_percent = strategy_s.tp2_percent
    tp2_percent_fix = strategy_s.tp2_percent_fix
    tp3_percent = strategy_s.tp3_percent
    tp3_percent_fix = strategy_s.tp3_percent_fix
    tp4_percent = strategy_s.tp4_percent
    tp4_percent_fix = strategy_s.tp4_percent_fix
    fixed_stop = strategy_s.fixed_stop
    sl_percent = strategy_s.sl_percent
    sensitivity = sensitivity * 10
    tp1_percent = tp1_percent / 100
    tp2_percent = tp2_percent / 100
    tp3_percent = tp3_percent / 100
    tp4_percent = tp4_percent / 100
    tp1_percent_fix = tp1_percent_fix / 100
    tp2_percent_fix = tp2_percent_fix / 100
    tp3_percent_fix = tp3_percent_fix / 100
    tp4_percent_fix = tp4_percent_fix / 100
    sl_percent = sl_percent / 100
    high_line = ta.highest(high, cast_int(sensitivity))
    low_line = ta.lowest(low, cast_int(sensitivity))
    channel_range = high_line - low_line
    fib_236 = high_line - channel_range * 0.236
    fib_382 = high_line - channel_range * 0.382
    fib_5 = high_line - channel_range * 0.5
    fib_618 = high_line - channel_range * 0.618
    fib_786 = high_line - channel_range * 0.786
    imba_trend_line = fib_5
    if time >= start_date_input:
        can_long = close >= imba_trend_line and close >= fib_236 and (not is_long_trend)
        can_short = close <= imba_trend_line and close <= fib_786 and (not is_short_trend)
    if can_long:
        is_long_trend = True
        is_short_trend = False
        is_long_trend_started = False if is_long_trend_started else True
    elif can_short:
        is_short_trend = True
        is_long_trend = False
        is_short_trend_started = False if is_short_trend_started else True
    else:
        is_trend_change = False
        can_long = False
        can_short = False
        is_short_trend_started = False
        is_long_trend_started = False
    is_trend_change = is_short_trend_started or is_long_trend_started
    plotshape(imba_trend_line if is_long_trend and is_long_trend_started else na, title='Long', style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small)
    plotshape(imba_trend_line if is_short_trend and is_short_trend_started else na, title='Short', style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small)
    plot(imba_trend_line, color=color.green if is_long_trend[1] else color.red, linewidth=3)
    if not na(trade):
        calc_profit(trade, show_dev_labels)
        if is_trend_change and (not trade.is_closed):
            close_trade(trade, show_dev_labels)
        if not trade.is_closed:
            label.set_x(entry_label, bar_index - 3)
            label.set_text(entry_label, string.tostring('🔰' if trade.side == 'LONG' else '🔰') + string.tostring(trade.entry_price))
            label.set_x(sl_label, bar_index - 3)
            label.set_text(sl_label, '⛔' + string.tostring(trade.sl_price))
            label.set_x(tp1_label, bar_index - 3)
            label.set_text(tp1_label, string.tostring('✅' if trade.tp1_hit else '1️⃣') + string.tostring(trade.tp1_price))
            label.set_x(tp2_label, bar_index - 3)
            label.set_text(tp2_label, string.tostring('✅' if trade.tp2_hit else '2️⃣') + string.tostring(trade.tp2_price))
            label.set_x(tp3_label, bar_index - 3)
            label.set_text(tp3_label, string.tostring('✅' if trade.tp3_hit else '3️⃣') + string.tostring(trade.tp3_price))
            label.set_x(tp4_label, bar_index - 3)
            label.set_text(tp4_label, string.tostring('✅' if trade.tp4_hit else '4️⃣') + string.tostring(trade.tp4_price))
            line.set_xy1(tp1_line, trade.start_bar_index, trade.tp1_price)
            line.set_xy2(tp1_line, bar_index + 1, trade.tp1_price)
            line.set_xy1(tp2_line, trade.start_bar_index, trade.tp2_price)
            line.set_xy2(tp2_line, bar_index + 1, trade.tp2_price)
            line.set_xy1(tp3_line, trade.start_bar_index, trade.tp3_price)
            line.set_xy2(tp3_line, bar_index + 1, trade.tp3_price)
            line.set_xy1(tp4_line, trade.start_bar_index, trade.tp4_price)
            line.set_xy2(tp4_line, bar_index + 1, trade.tp4_price)
            line.set_xy1(entry_line, trade.start_bar_index, trade.entry_price)
            line.set_xy2(entry_line, bar_index + 1, trade.entry_price)
            line.set_xy1(sl_line, trade.start_bar_index, trade.sl_price)
            line.set_xy2(sl_line, bar_index + 1, trade.sl_price)
        label.set_x(lable_at_signal, cast_int(math.avg(bar_index, trade.start_bar_index)))
        sign = '+' if trade.profit >= 0 else na
        label.set_text(lable_at_signal, sign + string.tostring(trade.profit, '#.##') + '%')
        label.set_color(lable_at_signal, color.green if trade.profit >= 0 else color.red)
        if fill_positions:
            if trade.tp1_hit:
                linefill.new(entry_line, tp1_line, color=color.new(color.green, 85))
            if trade.tp2_hit:
                linefill.new(tp1_line, tp2_line, color=color.new(color.green, 85))
            if trade.tp3_hit:
                linefill.new(tp2_line, tp3_line, color=color.new(color.green, 85))
            if trade.tp4_hit:
                linefill.new(tp3_line, tp4_line, color=color.new(color.green, 85))
            if trade.sl_hit:
                linefill.new(sl_line, entry_line, color=color.new(color.red, 85))
            if trade.force_closed:
                close_line = line.new(x1=trade.start_bar_index, y1=trade.close_price, x2=bar_index, y2=trade.close_price, color=color.white, style=line_style, width=2)
                if trade.profit <= 0:
                    linefill.new(close_line, entry_line, color=color.new(color.red, 85))
        if trade.is_closed:
            dep = trade.profit / 100 * dep + dep
            label.delete(entry_label)
            label.delete(sl_label)
            label.delete(tp1_label)
            label.delete(tp2_label)
            label.delete(tp3_label)
            label.delete(tp4_label)
            total_profit = total_profit + trade.profit
            trade_count = trade_count + 1
            if trade.profit >= 0:
                profit_trades = profit_trades + 1
                wins_in_a_row = wins_in_a_row + 1
                loss_in_a_row = 0
                win_streak = wins_in_a_row if wins_in_a_row > win_streak else win_streak
            else:
                loss_trades = loss_trades + 1
                loss_in_a_row = loss_in_a_row + 1
                wins_in_a_row = 0
                loss_streak = loss_in_a_row if loss_in_a_row > loss_streak else loss_streak
            trade = na
    alertcondition(can_long and na(trade), 'Long signal', 'Long')
    alertcondition(can_short and na(trade), 'Short signal', 'Short')
    alertcondition(can_short or (can_long and na(trade)), 'New signal', 'Check chart to see signal direction')
    if can_long or (can_short and na(trade)):
        first_trade_date = timestamp(year, month, dayofmonth, hour, minute) if trade_count == 0 else first_trade_date
        trade = Trade()
        trade.side = 'LONG' if can_long else 'SHORT'
        trade.entry_price = close
        trade.entry_hit = True
        trade.sl_price = math.round_to_mintick((trade.entry_price * (1 - sl_percent) if fixed_stop else fib_786 * (1 - sl_percent)) if can_long else trade.entry_price * (1 + sl_percent) if fixed_stop else fib_236 * (1 + sl_percent))
        trade.tp1_price = math.round_to_mintick(trade.entry_price * (1 + tp1_percent) if can_long else trade.entry_price * (1 - tp1_percent))
        trade.tp1_percent_fix = tp1_percent_fix * 100
        trade.tp2_price = math.round_to_mintick(trade.entry_price * (1 + tp2_percent) if can_long else trade.entry_price * (1 - tp2_percent))
        trade.tp2_percent_fix = tp2_percent_fix * 100
        trade.tp3_price = math.round_to_mintick(trade.entry_price * (1 + tp3_percent) if can_long else trade.entry_price * (1 - tp3_percent))
        trade.tp3_percent_fix = tp3_percent_fix * 100
        trade.tp4_price = math.round_to_mintick(trade.entry_price * (1 + tp4_percent) if can_long else trade.entry_price * (1 - tp4_percent))
        trade.tp4_percent_fix = tp4_percent_fix * 100
        __block_result_1__ = na
        __switch_1__ = break_even_target
        if __switch_1__ == '1':
            __block_result_1__ = trade.tp1_price
        elif __switch_1__ == '2':
            __block_result_1__ = trade.tp2_price
        elif __switch_1__ == '3':
            __block_result_1__ = trade.tp3_price
        elif __switch_1__ == 'WITHOUT':
            __block_result_1__ = trade.tp4_price
        trade.break_even_price = __block_result_1__
        trade.risk_percent = risk_percent
        trade.risk_reward = calc_rr(trade.entry_price, trade.sl_price, trade.tp4_price)
        trade.start_bar_index = bar_index
        alert_message = '\n{\n' + '    "side": "' + string.tostring(trade.side) + '",\n    "entry": "' + string.tostring(trade.entry_price) + '",\n    "tp1": "' + string.tostring(trade.tp1_price) + '",\n    "tp2": "' + string.tostring(trade.tp2_price) + '",\n    "tp3": "' + string.tostring(trade.tp3_price) + '",\n    "tp4": "' + string.tostring(trade.tp4_price) + '",\n    "winrate": "' + string.tostring(RoundUp(profit_trades / trade_count * 100, 2)) + '%' + '",\n    "strategy": "' + strategy_input + '",\n    "beTargetTrigger": "' + break_even_target + '",\n    "stop": "' + string.tostring(trade.sl_price) + '"\n}\n'
        alert(alert_message, alert.freq_once_per_bar_close)
        if show_tp_enty_sl:
            entry_line = line.new(x1=trade.start_bar_index, y1=trade.entry_price, x2=bar_index, y2=trade.entry_price, color=entry_color, style=line.style_solid, width=2)
            entry_label = label.new(bar_index, trade.entry_price, string.tostring(trade.entry_price), style=label.style_label_left, color=color.rgb(255, 255, 255, 100), textcolor=color.gray)
            sl_line = line.new(x1=trade.start_bar_index, y1=trade.sl_price, x2=bar_index, y2=trade.sl_price, color=sl_color, style=line_style, width=2)
            sl_label = label.new(bar_index, trade.sl_price, string.tostring(trade.sl_price), style=label.style_label_left, color=color.rgb(255, 255, 255, 100), textcolor=color.red)
            tp1_line = line.new(x1=trade.start_bar_index, y1=trade.tp1_price, x2=bar_index, y2=trade.tp1_price, color=tp_color, style=line_style, width=2)
            tp1_label = label.new(bar_index, trade.tp1_price, string.tostring(trade.tp1_price), style=label.style_label_left, color=color.rgb(255, 255, 255, 100), textcolor=color.green)
            tp2_line = line.new(x1=trade.start_bar_index, y1=trade.tp2_price, x2=bar_index, y2=trade.tp2_price, color=tp_color, style=line_style, width=2)
            tp2_label = label.new(bar_index, trade.tp2_price, string.tostring(trade.tp2_price), style=label.style_label_left, color=color.rgb(255, 255, 255, 100), textcolor=color.green)
            tp3_line = line.new(x1=trade.start_bar_index, y1=trade.tp3_price, x2=bar_index, y2=trade.tp3_price, color=tp_color, style=line_style, width=2)
            tp3_label = label.new(bar_index, trade.tp3_price, string.tostring(trade.tp3_price), style=label.style_label_left, color=color.rgb(255, 255, 255, 100), textcolor=color.green)
            tp4_line = line.new(x1=trade.start_bar_index, y1=trade.tp4_price, x2=bar_index, y2=trade.tp4_price, color=tp_color, style=line_style, width=2)
            tp4_label = label.new(bar_index, trade.tp4_price, string.tostring(trade.tp4_price), style=label.style_label_left, color=color.rgb(255, 255, 255, 100), textcolor=color.green)
            lable_at_signal = label.new(bar_index, trade.tp4_price * 1.004 if is_long_trend else trade.tp4_price * 0.996, '', style=label.style_label_center, textcolor=color.white)
    rsi_value = ta.rsi(close, len)
    is_overbought = rsi_value >= overbought
    is_oversold = rsi_value <= oversold
    plotshape(high if is_overbought and show_rsi else na, color=color.red, style=shape.cross, size=size.tiny, location=location.abovebar)
    plotshape(low if is_oversold and show_rsi else na, color=color.green, style=shape.cross, size=size.tiny, location=location.belowbar)
    lim: str = '-------------------------------------------------------'
    high_idk: str = '╔════════════════════════════╗'
    low_idk: str = '╚════════════════════════════╝'
    panel_str1 = high_idk + '\n' + '[IMBA] ALGO' + '\n' + low_idk
    panel_str13 = 'First signal: ' + string.format('{0,date,hh:mm} {0,date,long}', first_trade_date) + '\n' + lim
    panel_str14 = 'Signal closed: ' + string.tostring(trade_count) + '                 ' + 'Winrate: ' + string.tostring(RoundUp(profit_trades / trade_count * 100, 2)) + '%'
    panel_str15 = 'Profit signals: ' + string.tostring(profit_trades) + '              ' + 'Loss signals: ' + string.tostring(trade_count - profit_trades)
    panel_str16 = 'Win streak: ' + string.tostring(win_streak) + '                  ' + 'Loss streak: ' + string.tostring(loss_streak) + '\n' + lim
    panel_str17 = '💰 Profit: ' + string.tostring(total_profit, '#.##') + '% 💰'
    panel_last: str = '╚════════════════════════════╝'
    panel_str_arr: list[str] = array.from_items(panel_str1, panel_str13, panel_str14, panel_str15, panel_str16, panel_str17, panel_last)
    if show_old_panel:
        l: Series[Label] = label.new(bar_index + 20, close, text=array.join(panel_str_arr, '\n'), color=color.rgb(0, 0, 0, 87), style=label.style_label_left, textcolor=color.rgb(76, 187, 72), textalign=text.align_center)
        label.delete(l[1])
    profit_table: Persistent[Table] = na(Table)
    if show_profit_panel:
        profit_table = table.new(position.top_right, 3, 10, border_color=color.green, border_width=0)
        table.cell(profit_table, 0, 0, '═════════════════════════════' + '\n' + '[IMBA] ALGO' + '\n' + '═════════════════════════════', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=6, height=5, text_size=size.normal)
        table.cell(profit_table, 1, 0, '', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=6, height=3, text_size=size.normal)
        table.merge_cells(profit_table, 0, 0, 1, 0)
        table.cell(profit_table, 0, 1, 'First trade:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=8, height=3, text_size=size.normal, text_halign=text.align_left)
        table.cell(profit_table, 1, 1, string.format('{0,date,long}', first_trade_date), bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=8, height=3, text_size=size.normal)
        table.cell(profit_table, 0, 2, 'Total trades:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal, text_halign=text.align_left)
        table.cell(profit_table, 1, 2, string.tostring(trade_count), bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.cell(profit_table, 0, 3, 'Profit trades:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal, text_halign=text.align_left)
        table.cell(profit_table, 1, 3, string.tostring(profit_trades), bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.cell(profit_table, 0, 4, 'Loss trades:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal, text_halign=text.align_left)
        table.cell(profit_table, 1, 4, string.tostring(loss_trades), bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.cell(profit_table, 0, 5, 'Winrate:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal, text_halign=text.align_left)
        table.cell(profit_table, 1, 5, string.tostring(RoundUp(profit_trades / trade_count * 100, 2)) + '%', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.cell(profit_table, 0, 6, 'Win streak:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal, text_halign=text.align_left)
        table.cell(profit_table, 1, 6, string.tostring(win_streak), bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.cell(profit_table, 0, 7, 'Loss streak:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal, text_halign=text.align_left)
        table.cell(profit_table, 1, 7, string.tostring(loss_streak), bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.cell(profit_table, 0, 8, 'Deposit: ', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal, text_halign=text.align_left)
        table.cell(profit_table, 1, 8, string.tostring(dep, '##.##'), bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.cell(profit_table, 0, 9, '═════════════════════════════' + '\n' + '💰 Profit: ' + string.tostring(total_profit, '#.##') + '% 💰' + '\n' + '═════════════════════════════', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=10, text_size=size.normal, text_halign=text.align_center, text_valign=text.align_top)
        table.cell(profit_table, 1, 9, '', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.merge_cells(profit_table, 0, 9, 1, 9)
    strategy_table: Persistent[Table] = na(Table)
    if show_strategy_panel:
        strategy_table = table.new(position.bottom_right, 5, 6, border_color=color.green)
        table.cell(strategy_table, 1, 0, '══════════════════════════════════════════' + '\n' + syminfo.ticker + ' ' + timeframe.period + ' | WR: ' + string.tostring(profit_trades / (profit_trades + trade_count - profit_trades) * 100, '##,##') + '%' + ' | TT: ' + string.tostring(trade_count) + ' | P: ' + string.tostring(total_profit, '#.##') + '%' + '\n' + '══════════════════════════════════════════', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=6, height=7, text_size=size.normal, text_valign=text.align_bottom)
        table.cell(strategy_table, 2, 0, '', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=6, height=3, text_size=size.normal)
        table.cell(strategy_table, 3, 0, '', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=6, height=3, text_size=size.normal)
        table.cell(strategy_table, 4, 0, '', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=6, height=3, text_size=size.normal)
        table.merge_cells(strategy_table, 1, 0, 4, 0)
        table.cell(strategy_table, 1, 1, 'Strategy:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=6, height=3, text_size=size.normal, text_halign=text.align_left)
        table.cell(strategy_table, 2, 1, strategy_input, bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=6, height=3, text_size=size.normal)
        table.cell(strategy_table, 1, 2, 'Sensitivity:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal, text_halign=text.align_left)
        table.cell(strategy_table, 2, 2, string.tostring(sensitivity / 10), bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.cell(strategy_table, 1, 3, 'Risk:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal, text_halign=text.align_left)
        table.cell(strategy_table, 2, 3, string.tostring(risk_percent) + '%', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.cell(strategy_table, 1, 4, 'BE target:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal, text_halign=text.align_left)
        table.cell(strategy_table, 2, 4, string.tostring(break_even_target), bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.cell(strategy_table, 1, 5, 'Fixed stop:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal, text_halign=text.align_left)
        table.cell(strategy_table, 2, 5, string.tostring(fixed_stop), bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.cell(strategy_table, 3, 1, 'TP1:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=4, height=3, text_size=size.normal)
        table.cell(strategy_table, 4, 1, string.tostring(tp1_percent * 100) + '%' + ' (' + string.tostring(tp1_percent_fix * 100) + '%)', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.cell(strategy_table, 3, 2, 'TP2:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=4, height=3, text_size=size.normal)
        table.cell(strategy_table, 4, 2, string.tostring(tp2_percent * 100) + '%' + ' (' + string.tostring(tp2_percent_fix * 100) + '%)', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.cell(strategy_table, 3, 3, 'TP3:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=4, height=3, text_size=size.normal)
        table.cell(strategy_table, 4, 3, string.tostring(tp3_percent * 100) + '%' + ' (' + string.tostring(tp3_percent_fix * 100) + '%)', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.cell(strategy_table, 3, 4, 'TP4:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=4, height=3, text_size=size.normal)
        table.cell(strategy_table, 4, 4, string.tostring(tp4_percent * 100) + '%' + ' (' + string.tostring(tp4_percent_fix * 100) + '%)', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=5, height=3, text_size=size.normal)
        table.cell(strategy_table, 3, 5, 'Stop:', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=4, height=3, text_size=size.normal)
        table.cell(strategy_table, 4, 5, string.tostring(sl_percent * 100) + '%', bgcolor=color.rgb(0, 0, 0, 87), text_color=color.green, width=8, height=3, text_size=size.normal)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
