"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_float, cast_int
from pynecore.lib import (
    alert, array, bar_index, barstate, close, color, dayofmonth, fill, high,
    hour, input, label, low, math, minute, month, na, open, plot, position, script, second, size,
    strategy, string, syminfo, ta, table, text, time, time_close, timestamp, xloc, year, yloc
)
from pynecore.types import Persistent, Series, Table

_tooltip: str = 'RSI-7: Use the builtin RSI-7 indicator (set trigger values down below)\nExternal Indicator: plugin an external indicator. Make sure the indicator plots a value and configure down below the trigger point (greater than X, less than X, equal to X) '
_tooltip1: str = 'Take Profit: End deal when the price reached a % TP\nExternal Indicator: End deal using an external indicator (configure settings below)'
_tooltip2: str = 'Percentage: Open SO orders every N% of price movement. The price and size are calculated according to settings below (step scale, volume scale)\nExternal indicator: Open SO orders using an external indicator (configure settings below)'
_tooltip3: str = 'Select external indicator'
_tooltip4: str = 'Comparison for Deal start [greater or equal than, smaller or equal than, exactly equal]\nIf for example the external indicator is RSI deal could start when RSI7 <= 20'
_tooltip5: str = 'Value of external indicator for deal start'
_tooltip6: str = 'Comparison for Deal end [greater or equal than, smaller or equal than, exactly equal]\nIf for example the external indicator is RSI deal could end when RSI7 >= 80'
_tooltip7: str = 'Value of External indicator for deal end'
_tooltip8: str = 'Comparison for Safety order [greater or equal than, smaller or equal than, exactly equal]\nIf for example the external indicator is RSI trigger additional safety order every time RSI7 <= 10.\nATTENTION! This does not take into consideration the price value, so a low RSI does not mean a lower price as well'
_tooltip9: str = 'Value of external indicator to trigger safety orders'
_tooltip_bot_control: str = 'If this is enabled the strategy can control some bot operations via Webhook calls.\n\nTo enable Webhook calls, check this option, complete Bot id and Email Token. After the strategy is configured, create an alert on the strategy, select Order fills only, and in the message field simply input {{strategy.order.alert_message}}.'


@script.strategy(title='Zendog V3 backtest DCA bot 3commas', shorttitle='Zendog V3 DCA', overlay=True, max_labels_count=500, pyramiding=99, initial_capital=10000, calc_on_order_fills=False, commission_type=strategy.commission.percent, commission_value=0.075, margin_long=0, margin_short=0, default_qty_type=strategy.fixed, default_qty_value=1, close_by_id=True)
def main(
    cfg_theme=input.string(defval='dark', title='Chart theme', options=('light', 'dark')),
    deal_start_type=input.string(defval='RSI-7', title='Deal start type', options=('RSI-7', 'External Indicator'), group='Deal start & end conditions', tooltip=_tooltip),
    deal_end_type=input.string(defval='Take Profit', title='Deal end type', options=('Take Profit', 'External Indicator'), group='Deal start & end conditions', tooltip=_tooltip1),
    safety_order_type=input.string(defval='Percentage', title='Safety order type', options=('Percentage', 'External Indicator'), group='Deal start & end conditions', tooltip=_tooltip2),
    external_indicator: Series[float] = input.source(defval=close, title='External indicator', group='Deal start & end conditions', tooltip=_tooltip3),
    deal_start_operation=input.string(defval='=', title='Deal start operator', group='Deal start & end conditions', options=('<=', '=', '>='), tooltip=_tooltip4),
    deal_start_value=input.float(defval=-99999, title='Deal start value', group='Deal start & end conditions', tooltip=_tooltip5),
    deal_end_operation=input.string(defval='=', title='Deal end operator', group='Deal start & end conditions', options=('<=', '=', '>='), tooltip=_tooltip6),
    deal_end_value=input.float(defval=-99999, title='Deal end value', group='Deal start & end conditions', tooltip=_tooltip7),
    safety_order_operation=input.string(defval='=', title='Safety order operator', group='Deal start & end conditions', options=('<=', '=', '>='), tooltip=_tooltip8),
    safety_order_value=input.float(defval=-99999, title='Safety order value', group='Deal start & end conditions', tooltip=_tooltip9),
    rsi_start_operation=input.string(defval='<=', title='RSI-7 Operation', group='RSI7 (if used for Deal start trigger)', options=('<=', '>=')),
    rsi_start_value=input.int(defval=30, title='RSI-7 Value', group='RSI7 (if used for Deal start trigger)'),
    limit_date_range=input.bool(title='Limit Date Range', defval=False, group='Backtest date range'),
    start_time=input.time(defval=timestamp('01 Jan 2022 00:00 +0000'), title='Start Time', group='Backtest date range'),
    end_time=input.time(defval=timestamp('31 Dec 2022 00:00 +0000'), title='End Time', group='Backtest date range'),
    cfg_strategy_type=input.string(title='Strategy Type', defval='long', options=('long', 'short'), group='Strategy settings'),
    cfg_base_order_size_usd=input.float(title='Base order size', defval=1000, step=1000, group='Strategy settings'),
    cfg_safety_order_size_usd=input.float(title='Safety order size', defval=700, step=100, group='Strategy settings'),
    cfg_take_profit_type=input.string(title='Take Profit Type', defval='% From total volume', options=('% From base order', '% From total volume'), group='Strategy settings'),
    cfg_take_profit_perc=input.float(title='Take Profit (%)', minval=0.0, step=0.1, defval=2, group='Strategy settings'),
    cfg_enable_stop_loss=input.bool(title='Enable Stop Loss', defval=False, group='Strategy settings'),
    cfg_stop_loss_perc=input.float(title='Stop Loss (%)', minval=0.0, step=0.1, defval=20, group='Strategy settings'),
    cfg_max_safety_orders=input.float(title='Max Safety Trades Count', defval=5, group='Strategy settings'),
    cfg_safety_order_price_deviation_perc=input.float(title='Price Deviation To Open Safety Trades (%)', minval=0.0, step=0.1, defval=3, group='Strategy settings'),
    cfg_safety_order_volume_scale=input.float(title='Safety Order Volume Scale', defval=1, step=0.1, group='Strategy settings'),
    cfg_safety_order_price_step_scale=input.float(title='Safety Order Step Scale', defval=1, step=0.1, group='Strategy settings'),
    cfg_planb_timeout=input.int(title='PLAN-B Timeout', defval=1, step=1, group='PLAN-B', tooltip='Timeout to activate PLAN-B. Use \'none\' in the dropdown below to disable PLAN-B'),
    cfg_planb_timeout_type=input.string(title='', defval='none', options=('none', 'min', 'hour', 'day'), group='PLAN-B'),
    cfg_planb_action=input.string(title='PLAN-B Action', defval='none', options=('none', 'paint only', 'close deal'), group='PLAN-B'),
    cfg_planb_take_profit=input.float(title='PLAN-B Close Deal (%) ', defval=0.5, step=0.1, group='PLAN-B', tooltip='Alternative % from total volume (versus position_avg_size) to use when PLAN-B is activated.\nIt is either a positive % for alternative TP or a negative % for alternative SL'),
    cfg_enable_bot_control=input.bool(title='Enable Bot Control Via Webhook', defval=False, group='3commas Bot Settings', tooltip=_tooltip_bot_control),
    cfg_bot_id=input.string(title='Bot id', defval='', group='3commas Bot Settings'),
    cfg_email_token=input.string(title='Email token', defval='', group='3commas Bot Settings'),
    cfg_exec_deal_start=input.bool(title='Deal start', defval=True, group='3commas Bot Settings'),
    cfg_exec_safety_order=input.bool(title='Safety Orders', defval=True, group='3commas Bot Settings', tooltip='The strategy will send a message to add funds in the quote currency (for BTCUSDT quote is USDT). The amount of funds are calculated based on SO settings (size, volume steps). For exact values use the steps table.'),
    cfg_exec_take_profit=input.bool(title='Take profit deal stop', defval=True, group='3commas Bot Settings'),
    cfg_exec_external_indicator=input.bool(title='External indicator deal stop', defval=True, group='3commas Bot Settings'),
    cfg_exec_stop_loss=input.bool(title='Stop Loss', defval=True, group='3commas Bot Settings'),
    cfg_exec_planb_timeout=input.bool(title='PLAN-B', defval=True, group='3commas Bot Settings'),
    cfg_commision_percent=input.float(title='Commision (%)', minval=0.0, step=0.001, defval=0.075, group='Broker'),
    cfg_decimals=input.int(title='Decimals For Display', defval=2, group='Visuals'),
    cfg_show_pnl_labels=input.bool(title='Show PnL Labels', defval=True, group='Visuals'),
    cfg_show_stats_table=input.bool(title='Show Table With Statistics', defval=True, group='Visuals'),
    cfg_show_settings_table=input.bool(title='Show Table With Strategy Settings', defval=False, group='Visuals'),
    cfg_show_step_table=input.bool(title='Show Table With Steps Similar To 3commas', defval=False, group='Visuals', tooltip='Make sure the Table with Strategy Settings is disabled because they use the same position\n\nIf the Safety orders type is not percentage all significant values will be replaced by - (dashes)'),
    cfg_steps_bo_price=input.float(title='BO Entry Price For Steps Table', defval=0, group='Visuals', tooltip='Custom BO price used to calculate all table values. If this is not configured, the close value will be used')
):
    theme_text_color = color.white if cfg_theme == 'dark' else color.black
    def f_print(_text):
        _label: Persistent = label.new(x=bar_index, y=na, text=string.tostring(_text), xloc=xloc.bar_index, yloc=yloc.price, color=color.blue, style=label.style_label_up, textcolor=theme_text_color, size=size.normal, textalign=text.align_left)
        __block_result__ = na
        if barstate.islastconfirmedhistory:
            label.set_xy(_label, bar_index, low * 0.99)
            __block_result__ = label.set_text(_label, string.tostring(_text))
        return __block_result__

    deal_start_condition: bool = False
    deal_end_condition: bool = False
    safety_order_condition: bool = False
    if deal_start_type == 'RSI-7' and rsi_start_operation == '<=':
        deal_start_condition = ta.rsi(close, 7) <= rsi_start_value
    elif deal_start_type == 'RSI-7' and rsi_start_operation == '>=':
        deal_start_condition = ta.rsi(close, 7) >= rsi_start_value
    elif deal_start_type == 'External Indicator' and deal_start_value != -99999 and (deal_start_operation == '=') and (external_indicator == deal_start_value):
        deal_start_condition = True
    elif deal_start_type == 'External Indicator' and deal_start_value != -99999 and (deal_start_operation == '<=') and (external_indicator <= deal_start_value):
        deal_start_condition = True
    elif deal_start_type == 'External Indicator' and deal_start_value != -99999 and (deal_start_operation == '>=') and (external_indicator >= deal_start_value):
        deal_start_condition = True
    else:
        deal_start_condition = False
    if deal_end_type == 'External Indicator' and deal_end_value != -99999 and (deal_end_operation == '=') and (external_indicator == deal_end_value):
        deal_end_condition = True
    elif deal_end_type == 'External Indicator' and deal_end_value != -99999 and (deal_end_operation == '<=') and (external_indicator <= deal_end_value):
        deal_end_condition = True
    elif deal_end_type == 'External Indicator' and deal_end_value != -99999 and (deal_end_operation == '>=') and (external_indicator >= deal_end_value):
        deal_end_condition = True
    else:
        deal_end_condition = False
    if safety_order_type == 'External Indicator' and safety_order_value != -99999 and (safety_order_operation == '=') and (external_indicator == safety_order_value):
        safety_order_condition = True
    elif safety_order_type == 'External Indicator' and safety_order_value != -99999 and (safety_order_operation == '<=') and (external_indicator <= safety_order_value):
        safety_order_condition = True
    elif safety_order_type == 'External Indicator' and safety_order_value != -99999 and (safety_order_operation == '>=') and (external_indicator >= safety_order_value):
        safety_order_condition = True
    else:
        safety_order_condition = False
    in_date_range: bool = True
    if limit_date_range:
        in_date_range = time >= start_time and time <= end_time
    else:
        in_date_range = True
    IS_LONG: Persistent[bool] = cfg_strategy_type == 'long'
    def get_planb_timeout():
        _timeout: float = 0
        __block_result_1__ = na
        if cfg_planb_timeout_type == 'day':
            _timeout = cfg_planb_timeout * 86400000
            __block_result_1__ = _timeout
        elif cfg_planb_timeout_type == 'hour':
            _timeout = cfg_planb_timeout * 3600000
            __block_result_1__ = _timeout
        elif cfg_planb_timeout_type == 'min':
            _timeout = cfg_planb_timeout * 60000
            __block_result_1__ = _timeout
        return __block_result_1__

    glb_planb_timeout: Persistent[float] = get_planb_timeout()
    count_executed_safety_orders: Persistent[int] = 0
    glb_take_profit_price: Persistent[float] = na(float)
    glb_planb_timeout_price: Persistent[float] = na(float)
    glb_stop_loss_price: Persistent[float] = na(float)
    glb_base_order_price: Persistent[float] = na(float)
    glb_base_order_qty: Persistent[float] = na(float)
    glb_next_safety_order_price: Persistent[float] = na(float)
    glb_required_capital: Persistent[float] = na(float)
    glb_total_volume: Persistent[float] = 0
    glb_current_deal_position_size: Persistent[float] = na(float)
    glb_current_deal_avg_price: Persistent[float] = na(float)
    glb_strategy_prev_netprofit: Persistent[float] = 0
    glb_current_deal_close_value: Persistent[float] = 0
    glb_current_deal_pnl: Persistent[float] = 0
    glb_still_in_deal: Persistent[bool] = False
    glb_debug_text: Persistent[str] = ''
    debug_printed: Persistent[bool] = False
    glb_so_orders_placed: Persistent[bool] = False
    statsarray_safety_orders: Persistent[list[int]] = array.new_int(0)
    statsarray_safety_orders_timeout: Persistent[list[int]] = array.new_int(0)
    glb_dealstart_bar_index: Persistent[int] = 0
    statsarray_no_of_bars: Persistent[list[int]] = array.new_int(0)
    glb_dealstart_bar_time: Persistent[int] = 0
    statsarray_no_of_days: Persistent[list[float]] = array.new_float(0)
    stats_max_days_in_deal: Persistent[float] = 0
    stats_max_days_in_deal_start_time: Persistent[int] = 0
    stats_max_days_in_deal_close_time: Persistent[int] = 0
    firstdeal_started: Persistent[bool] = False
    firstdeal_bar_index: Persistent[int] = 0
    firstdeal_start_price: Persistent[float] = 0
    firstdeal_start_time: Persistent[int] = 0
    lastdeal_close_bar_index: Persistent[int] = 0
    lastdeal_close_time: Persistent[int] = 0
    bh_start_price: Persistent[float] = 0
    bh_start_time: Persistent[int] = 0
    bh_end_price: Persistent[float] = 0
    bh_end_time: Persistent[int] = 0
    bh_calculation_started: Persistent[bool] = False
    stats_max_drawdown: Persistent[float] = 0
    stats_max_drawdown_time: Persistent[int] = 0
    stats_max_drawdown_equity_percent: Persistent[float] = 0
    stats_biggest_dev: Persistent[float] = 0
    stats_biggest_dev_time: Persistent[int] = 0
    stats_deals_started: Persistent[float] = 0
    stats_deals_finished: Persistent[float] = 0
    stats_deals_stop_loss_finished: Persistent[float] = 0
    stats_deals_take_profit_finished: Persistent[float] = 0
    stats_deals_timeout_finished: Persistent[float] = 0
    statsarray_winning_deals_pnl: Persistent[list[float]] = array.new_float(0)
    statsarray_losing_deals_pnl: Persistent[list[float]] = array.new_float(0)
    statsarray_timeout_deals_pnl: Persistent[list[float]] = array.new_float(0)
    def stepped_deviation(so_index):
        _stepped_deviation: float = 0
        __block_result_2__ = na
        if so_index > 0:
            __block_result_3__ = na
            for _i in pine_range(1, so_index, 1):
                _stepped_deviation = _stepped_deviation + cfg_safety_order_price_deviation_perc * math.pow(cfg_safety_order_price_step_scale, _i - 1)
                __block_result_3__ = _stepped_deviation
            __block_result_2__ = __block_result_3__
        else:
            _stepped_deviation = 0
            __block_result_2__ = _stepped_deviation
        return __block_result_2__

    def steps_required_price(_bo_price, _avg_price, _pos_size, _take_profit_percent):
        _price: float = 0
        __block_result_4__ = na
        if cfg_take_profit_type == '% From total volume':
            __block_result_5__ = na
            if IS_LONG:
                _required_price = _avg_price * (1 + _take_profit_percent / 100)
                __block_result_5__ = _required_price
            else:
                _required_price = _avg_price * (1 - _take_profit_percent / 100)
                __block_result_5__ = _required_price
            __block_result_4__ = __block_result_5__
        elif cfg_take_profit_type == '% From base order':
            __block_result_6__ = na
            if IS_LONG:
                _req_usdt = cfg_base_order_size_usd * cfg_take_profit_perc / 100
                _required_price = (_avg_price * _pos_size + _req_usdt) / _pos_size
                __block_result_6__ = _required_price
            else:
                _req_usdt = cfg_base_order_size_usd * cfg_take_profit_perc / 100
                _required_price = (_avg_price * _pos_size - _req_usdt) / _pos_size
                __block_result_6__ = _required_price
            __block_result_4__ = __block_result_6__
        return __block_result_4__

    def steps_required_percent(_last_price, _required_price):
        __block_result_7__ = na
        if IS_LONG:
            _required_percent = math.round(_required_price * 100 / _last_price - 100, 2)
            __block_result_7__ = _required_percent
        else:
            _required_percent = math.round(100 - _required_price * 100 / _last_price, 2)
            __block_result_7__ = _required_percent
        return __block_result_7__

    def valid_stop_loss():
        _valid: bool = False
        __block_result_8__ = na
        if cfg_enable_stop_loss:
            stepped_deviation_1 = stepped_deviation(cfg_max_safety_orders)
            __block_result_9__ = na
            if safety_order_type == 'Percentage' and cfg_stop_loss_perc > stepped_deviation_1:
                _valid = True
                __block_result_9__ = _valid
            elif safety_order_type == 'External Indicator':
                _valid = True
                __block_result_9__ = _valid
            else:
                _valid = False
                __block_result_9__ = _valid
            __block_result_8__ = __block_result_9__
        else:
            _valid = False
            __block_result_8__ = _valid
        return __block_result_8__

    def next_so_price(so_index, _bo_price):
        _stepped_deviation: float = stepped_deviation(so_index)
        __block_result_10__ = na
        if IS_LONG:
            _next_so_price: float = _bo_price * (1 - _stepped_deviation / 100)
            __block_result_10__ = _next_so_price
        else:
            _next_so_price: float = _bo_price * (1 + _stepped_deviation / 100)
            __block_result_10__ = _next_so_price
        return __block_result_10__

    def next_so_size_usd(so_index):
        _next_so_size_usd: float = cfg_safety_order_size_usd * math.pow(cfg_safety_order_volume_scale, so_index - 1)
        return _next_so_size_usd

    def next_so_qty(so_index, _bo_price):
        _next_so_size_usd: float = next_so_size_usd(so_index)
        _next_so_qty: float = _next_so_size_usd / next_so_price(so_index, _bo_price)
        return _next_so_qty

    def is_planb_timeout():
        _res: bool = False
        __block_result_11__ = na
        if na(glb_dealstart_bar_time) == False:
            __block_result_12__ = na
            if time - glb_dealstart_bar_time >= glb_planb_timeout:
                _res = True
                __block_result_12__ = _res
            __block_result_11__ = __block_result_12__
        else:
            _res = False
            __block_result_11__ = _res
        return __block_result_11__

    def get_required_capital():
        _total_buy: float = 0
        __block_result_13__ = na
        if cfg_max_safety_orders > 0:
            _total_buy = _total_buy + cfg_base_order_size_usd
            __block_result_14__ = na
            for _i in pine_range(1, cfg_max_safety_orders, 1):
                _total_buy = _total_buy + next_so_size_usd(_i)
                __block_result_14__ = _total_buy
            __block_result_13__ = __block_result_14__
        else:
            _total_buy = _total_buy + cfg_base_order_size_usd
            __block_result_13__ = _total_buy
        return __block_result_13__

    def get_days(start_time, end_time):
        time_diff = end_time - start_time
        diff_days = math.round(time_diff / 86400000, 1)
        return diff_days

    def get_timestring_from_seconds(seconds):
        __block_result_15__ = na
        if seconds >= 86400:
            _string: str = string.tostring(math.round(seconds / 86400, 1)) + ' days'
            __block_result_15__ = _string
        elif seconds >= 3600:
            _string: str = string.tostring(math.round(seconds / 3600, 1)) + ' hours'
            __block_result_15__ = _string
        else:
            _string: str = string.tostring(math.round(seconds / 60, 1)) + ' mins'
            __block_result_15__ = _string
        return __block_result_15__

    def get_timestring_from_days(days):
        return get_timestring_from_seconds(days * 86400)

    def get_timespan_string(start_time, end_time):
        _seconds_diff = (end_time - start_time) / 1000
        return get_timestring_from_seconds(_seconds_diff)

    def get_commission_for_volume(vol):
        _commision = vol * cfg_commision_percent / 100
        return _commision

    def get_final_pnl_new():
        _pnl: float = 0
        if array.size(statsarray_losing_deals_pnl) > 0:
            _pnl = _pnl + array.sum(statsarray_losing_deals_pnl)
        if array.size(statsarray_winning_deals_pnl) > 0:
            _pnl = _pnl + array.sum(statsarray_winning_deals_pnl)
        _pnl = _pnl + strategy.openprofit
        return _pnl

    def get_final_pnl_prct_new():
        return get_final_pnl_new() * 100 / glb_required_capital

    def take_profit_price(_avg_price = strategy.position_avg_price, _pos_size = strategy.position_size):
        __block_result_16__ = na
        if cfg_take_profit_type == '% From total volume':
            __block_result_17__ = na
            if IS_LONG:
                _tp_price = _avg_price * (1 + cfg_take_profit_perc / 100)
                __block_result_17__ = _tp_price
            else:
                _tp_price = _avg_price * (1 - cfg_take_profit_perc / 100)
                __block_result_17__ = _tp_price
            __block_result_16__ = __block_result_17__
        elif cfg_take_profit_type == '% From base order':
            __block_result_18__ = na
            if IS_LONG:
                _tp_size_usd = cfg_base_order_size_usd * cfg_take_profit_perc / 100
                _tp_price = (_avg_price * _pos_size + _tp_size_usd) / _pos_size
                __block_result_18__ = _tp_price
            else:
                _tp_size_usd = cfg_base_order_size_usd * cfg_take_profit_perc / 100
                _tp_price = (_avg_price * _pos_size - _tp_size_usd) / _pos_size
                __block_result_18__ = _tp_price
            __block_result_16__ = __block_result_18__
        return __block_result_16__

    def planb_timeout_price():
        __block_result_19__ = na
        if IS_LONG:
            _price = strategy.position_avg_price * (1 + cast_float(cfg_planb_take_profit) / 100)
            __block_result_19__ = _price
        else:
            _price = strategy.position_avg_price * (1 - cast_float(cfg_planb_take_profit) / 100)
            __block_result_19__ = _price
        return __block_result_19__

    def stop_loss_price(_bo_price):
        __block_result_20__ = na
        if IS_LONG:
            __block_result_20__ = _bo_price * (1 - cfg_stop_loss_perc / 100)
        else:
            __block_result_20__ = _bo_price * (1 + cfg_stop_loss_perc / 100)
        return __block_result_20__

    def take_profit_price_hit():
        __block_result_21__ = na
        if IS_LONG:
            __block_result_21__ = high >= glb_take_profit_price and strategy.position_size == 0
        else:
            __block_result_21__ = low <= glb_take_profit_price and strategy.position_size == 0
        return __block_result_21__

    def planb_price_hit():
        __block_result_22__ = na
        if IS_LONG:
            __block_result_22__ = high >= glb_planb_timeout_price and strategy.position_size == 0
        else:
            __block_result_22__ = low <= glb_planb_timeout_price and strategy.position_size == 0
        return __block_result_22__

    def stop_loss_price_hit():
        _cond: bool = False
        __block_result_23__ = na
        if valid_stop_loss():
            __block_result_24__ = na
            if IS_LONG:
                _cond = low <= glb_stop_loss_price and strategy.position_size == 0
                __block_result_24__ = _cond
            else:
                _cond = high >= glb_stop_loss_price and strategy.position_size == 0
                __block_result_24__ = _cond
            __block_result_23__ = __block_result_24__
        else:
            _cond = False
            __block_result_23__ = _cond
        return __block_result_23__

    def get_current_dev_vs_bo_price():
        __block_result_25__ = na
        if IS_LONG:
            _dev = low * 100 / glb_base_order_price - 100
            __block_result_25__ = _dev
        else:
            _dev = 100 - high * 100 / glb_base_order_price
            __block_result_25__ = _dev
        return __block_result_25__

    def get_current_drawdown_equity():
        _deal_total_value = strategy.position_size * strategy.position_avg_price
        __block_result_26__ = na
        if IS_LONG:
            _drawdown_actual_value = strategy.position_size * low
            _drawdown_equity_percent = _drawdown_actual_value * 100 / _deal_total_value - 100
            __block_result_26__ = _drawdown_equity_percent
        else:
            _drawdown_actual_value = strategy.position_size * high
            _drawdown_equity_percent = 100 - _drawdown_actual_value * 100 / _deal_total_value
            __block_result_26__ = _drawdown_equity_percent
        return __block_result_26__

    def is_deal_started():
        _flag: bool = False
        __block_result_27__ = na
        if IS_LONG and strategy.position_size > 0:
            _flag = True
            __block_result_27__ = _flag
        elif not IS_LONG and strategy.position_size < 0:
            _flag = True
            __block_result_27__ = _flag
        else:
            _flag = False
            __block_result_27__ = _flag
        return __block_result_27__

    def was_deal_marked_as_finished():
        __block_result_28__ = na
        if glb_still_in_deal == True:
            _state: bool = False
            __block_result_28__ = _state
        else:
            _state: bool = True
            __block_result_28__ = _state
        return __block_result_28__

    def init_stats_array_safety_orders():
        __block_result_29__ = na
        for _i in pine_range(0, cfg_max_safety_orders, 1):
            array.push(statsarray_safety_orders, 0)
            __block_result_29__ = array.push(statsarray_safety_orders_timeout, 0)
        return __block_result_29__

    def get_3cbot_startdeal_json():
        _string = '{"message_type":"bot", "bot_id":"' + cfg_bot_id + '", "email_token":"' + cfg_email_token + '", "delay_seconds":0, "pair":"' + string.tostring(syminfo.currency) + '_' + string.tostring(syminfo.basecurrency) + '"}'
        return _string

    def get_3cbot_stopdeal_json():
        _string = '{"action": "close_at_market_price_all", "message_type":"bot", "bot_id":"' + cfg_bot_id + '", "email_token":"' + cfg_email_token + '", "delay_seconds":0, "pair":"' + string.tostring(syminfo.currency) + '_' + string.tostring(syminfo.basecurrency) + '"}'
        return _string

    def get_3cbot_addfundsinquote_json(add_volume = 0):
        _string = '{"action": "add_funds_in_quote", "message_type":"bot", "bot_id":"' + cfg_bot_id + '", "email_token":"' + cfg_email_token + '", "delay_seconds":0, "volume":"' + string.tostring(add_volume) + '"}'
        return _string

    def get_month_string(month_number):
        __block_result_30__ = na
        if month_number == 1:
            _string: str = 'Jan'
            __block_result_30__ = _string
        elif month_number == 2:
            _string: str = 'Feb'
            __block_result_30__ = _string
        elif month_number == 3:
            _string: str = 'Mar'
            __block_result_30__ = _string
        elif month_number == 4:
            _string: str = 'Apr'
            __block_result_30__ = _string
        elif month_number == 5:
            _string: str = 'May'
            __block_result_30__ = _string
        elif month_number == 6:
            _string: str = 'Jun'
            __block_result_30__ = _string
        elif month_number == 7:
            _string: str = 'Jul'
            __block_result_30__ = _string
        elif month_number == 8:
            _string: str = 'Aug'
            __block_result_30__ = _string
        elif month_number == 9:
            _string: str = 'Sep'
            __block_result_30__ = _string
        elif month_number == 10:
            _string: str = 'Oct'
            __block_result_30__ = _string
        elif month_number == 11:
            _string: str = 'Nov'
            __block_result_30__ = _string
        elif month_number == 12:
            _string: str = 'Dec'
            __block_result_30__ = _string
        return __block_result_30__

    def time_to_date_string(timeinms):
        __block_result_31__ = na
        if timeinms > 0:
            _string = string.tostring(dayofmonth(timeinms), '00/') + get_month_string(month(timeinms)) + '/' + string.tostring(year(timeinms), '0000') + ' ' + string.tostring(hour(timeinms), '00:') + string.tostring(minute(timeinms), '00:') + string.tostring(second(timeinms), '00')
            __block_result_31__ = _string
        else:
            _string: str = ''
            __block_result_31__ = _string
        return __block_result_31__

    def get_bg_color_grey(row):
        _bgcolor = color.new('#CACACA') if row % 2 == 0 else color.new('#E5E5E5')
        return _bgcolor

    def get_bg_color_blue(transp = 0):
        _bgcolor = color.new(color.new('#006BB3'), transp)
        return _bgcolor

    def get_bg_color_green(transp = 0):
        _bgcolor = color.new(color.new('#A6E59B'), transp)
        return _bgcolor

    def get_bg_color_red(transp = 0):
        _bgcolor = color.new(color.new('#E59B9B'), transp)
        return _bgcolor

    def get_bg_color_lightblue(transp = 0):
        _bgcolor = color.new(color.new('#00BFFF'), transp)
        return _bgcolor

    def get_bg_color_orange(transp = 0):
        _bgcolor = color.new(color.new('#FFA500'), transp)
        return _bgcolor

    if in_date_range and bh_calculation_started == False:
        bh_start_price = open
        bh_start_time = time
        bh_calculation_started = True
        bh_end_price = close
        bh_end_time = time_close
    if in_date_range:
        bh_end_price = close
        bh_end_time = time_close
    is_deal_started_1 = is_deal_started()
    was_deal_marked_as_finished_1 = was_deal_marked_as_finished()
    if in_date_range and deal_start_condition and (not is_deal_started_1) and was_deal_marked_as_finished_1:
        if firstdeal_started == False:
            firstdeal_started = True
            firstdeal_bar_index = bar_index
            firstdeal_start_price = close
            firstdeal_start_time = time
            init_stats_array_safety_orders()
        glb_still_in_deal = True
        stats_deals_started = stats_deals_started + 1
        glb_dealstart_bar_index = bar_index
        glb_dealstart_bar_time = time
        if glb_strategy_prev_netprofit != strategy.netprofit:
            glb_strategy_prev_netprofit = strategy.netprofit
        glb_base_order_qty = cfg_base_order_size_usd / close
        glb_base_order_price = close
        _alert_human = 'D' + string.tostring(stats_deals_started) + '-BO (' + string.tostring(syminfo.basecurrency) + '-' + string.tostring(syminfo.currency) + (' LONG' if cfg_strategy_type == 'long' else ' SHORT') + ') | ' + string.tostring(glb_base_order_qty * glb_base_order_price) + ' ' + string.tostring(syminfo.currency)
        if cfg_enable_bot_control and cfg_exec_deal_start:
            _alert_json = get_3cbot_startdeal_json()
            strategy.entry(id='D' + string.tostring(stats_deals_started) + '-BO', direction=strategy.long if IS_LONG else strategy.short, qty=glb_base_order_qty, alert_message=_alert_json)
            alert(_alert_human, alert.freq_once_per_bar_close)
        else:
            strategy.entry(id='D' + string.tostring(stats_deals_started) + '-BO', direction=strategy.long if IS_LONG else strategy.short, qty=glb_base_order_qty)
            alert(_alert_human, alert.freq_once_per_bar_close)
    was_deal_marked_as_finished_2 = was_deal_marked_as_finished()
    if is_deal_started() and (not was_deal_marked_as_finished_2):
        if strategy.opentrades == 1 and (not glb_so_orders_placed):
            glb_so_orders_placed = True
            glb_base_order_price = strategy.position_avg_price
            glb_base_order_qty = strategy.position_size
            count_executed_safety_orders = 0
            glb_debug_text = glb_debug_text + 'BO: ' + string.tostring(math.round(glb_base_order_qty, cfg_decimals)) + ' * ' + string.tostring(math.round(glb_base_order_price, cfg_decimals)) + '=' + string.tostring(glb_base_order_qty * glb_base_order_price) + '\n'
            if cfg_max_safety_orders > 0 and safety_order_type == 'Percentage':
                for _so_number in pine_range(1, cfg_max_safety_orders, 1):
                    _next_so_price = next_so_price(_so_number, glb_base_order_price)
                    _next_so_qty = next_so_qty(_so_number, glb_base_order_price)
                    _next_so_size_usd = next_so_size_usd(_so_number)
                    glb_debug_text = glb_debug_text + 'SO' + string.tostring(_so_number) + ': ' + string.tostring(math.round(_next_so_qty, cfg_decimals)) + '*' + string.tostring(math.round(_next_so_price, cfg_decimals)) + '=' + string.tostring(_next_so_qty * _next_so_price) + '\n'
                    if cfg_enable_bot_control and cfg_exec_safety_order:
                        _alert_json = get_3cbot_addfundsinquote_json(_next_so_size_usd)
                        strategy.entry(id='D' + string.tostring(stats_deals_started) + '-SO' + string.tostring(_so_number), direction=strategy.long if IS_LONG else strategy.short, qty=_next_so_qty, limit=_next_so_price, alert_message=_alert_json)
                    else:
                        strategy.entry(id='D' + string.tostring(stats_deals_started) + '-SO' + string.tostring(_so_number), direction=strategy.long if IS_LONG else strategy.short, qty=_next_so_qty, limit=_next_so_price)
                glb_next_safety_order_price = next_so_price(1, glb_base_order_price)
            if valid_stop_loss():
                glb_stop_loss_price = stop_loss_price(glb_base_order_price)
                glb_debug_text = glb_debug_text + 'SL: ' + string.tostring(glb_stop_loss_price) + '\n'
                if cfg_enable_bot_control and cfg_exec_stop_loss:
                    _alert_json = get_3cbot_stopdeal_json()
                    if is_deal_started():
                        strategy.exit(id='D' + string.tostring(stats_deals_started) + '-SL', stop=glb_stop_loss_price, alert_message=_alert_json)
                else:
                    if is_deal_started():
                        strategy.exit(id='D' + string.tostring(stats_deals_started) + '-SL', stop=glb_stop_loss_price)
        if strategy.opentrades > count_executed_safety_orders + 1 and safety_order_type == 'Percentage':
            __loop_2__ = pine_loop(count_executed_safety_orders + 1, 1)
            while __loop_2__.step(strategy.opentrades):
                _i = __loop_2__.value
                _next_so_price = next_so_price(_i, glb_base_order_price)
                _next_so_qty = next_so_qty(_i, glb_base_order_price)
                _alert_human = 'D' + string.tostring(stats_deals_started) + '-SO' + string.tostring(_i) + ' [delayed] (' + string.tostring(syminfo.basecurrency) + '_' + string.tostring(syminfo.currency) + (' LONG' if cfg_strategy_type == 'long' else ' SHORT') + ') | ' + string.tostring(_next_so_price * _next_so_qty) + ' ' + string.tostring(syminfo.currency)
                alert(_alert_human, alert.freq_once_per_bar_close)
            count_executed_safety_orders = strategy.opentrades - 1
            if count_executed_safety_orders < cfg_max_safety_orders:
                glb_next_safety_order_price = next_so_price(count_executed_safety_orders + 1, glb_base_order_price)
            elif count_executed_safety_orders == cfg_max_safety_orders:
                glb_next_safety_order_price = na
        if safety_order_type == 'External Indicator' and safety_order_condition == True and (count_executed_safety_orders < cfg_max_safety_orders):
            count_executed_safety_orders = count_executed_safety_orders + 1
            _next_so_size_usd = next_so_size_usd(count_executed_safety_orders)
            _next_so_qty = _next_so_size_usd / close
            if cfg_enable_bot_control and cfg_exec_safety_order:
                _alert_json = get_3cbot_addfundsinquote_json(_next_so_size_usd)
                strategy.entry(id='D' + string.tostring(stats_deals_started) + '-SO' + string.tostring(count_executed_safety_orders), direction=strategy.long if IS_LONG else strategy.short, qty=_next_so_qty, alert_message=_alert_json)
            else:
                strategy.entry(id='D' + string.tostring(stats_deals_started) + '-SO' + string.tostring(count_executed_safety_orders), direction=strategy.long if IS_LONG else strategy.short, qty=_next_so_qty)
            _alert_human = 'D' + string.tostring(stats_deals_started) + '-SO' + string.tostring(count_executed_safety_orders) + ' (' + string.tostring(syminfo.basecurrency) + '_' + string.tostring(syminfo.currency) + (' LONG' if cfg_strategy_type == 'long' else ' SHORT') + ') | ' + string.tostring(_next_so_size_usd) + ' ' + string.tostring(syminfo.currency)
            alert(_alert_human, alert.freq_once_per_bar_close)
        if deal_end_type == 'Take Profit':
            glb_take_profit_price = take_profit_price()
            if cfg_enable_bot_control and cfg_exec_take_profit:
                _alert_json = get_3cbot_stopdeal_json()
                if is_deal_started():
                    strategy.order(id='D' + string.tostring(stats_deals_started) + '-TP', limit=glb_take_profit_price, direction=strategy.short if IS_LONG else strategy.long, qty=math.abs(strategy.position_size), alert_message=_alert_json)
            else:
                if is_deal_started():
                    strategy.order(id='D' + string.tostring(stats_deals_started) + '-TP', limit=glb_take_profit_price, direction=strategy.short if IS_LONG else strategy.long, qty=math.abs(strategy.position_size))
            ''
        else:
            glb_take_profit_price = na
            ''
        if is_planb_timeout() and cfg_planb_action != 'none':
            glb_planb_timeout_price = planb_timeout_price()
        if is_planb_timeout() and cfg_planb_action == 'close deal':
            strategy.cancel(id='D' + string.tostring(stats_deals_started) + '-TP')
            if cfg_enable_bot_control and cfg_exec_planb_timeout:
                _alert_json = get_3cbot_stopdeal_json()
                if is_deal_started():
                    strategy.order(id='D' + string.tostring(stats_deals_started) + '-TIMEOUT', limit=glb_planb_timeout_price, direction=strategy.short if IS_LONG else strategy.long, qty=math.abs(strategy.position_size), alert_message=_alert_json)
            else:
                if is_deal_started():
                    strategy.order(id='D' + string.tostring(stats_deals_started) + '-TIMEOUT', limit=glb_planb_timeout_price, direction=strategy.short if IS_LONG else strategy.long, qty=math.abs(strategy.position_size))
        glb_current_deal_position_size = strategy.position_size
        glb_current_deal_avg_price = strategy.position_avg_price
        if strategy.openprofit < stats_max_drawdown:
            stats_max_drawdown = strategy.openprofit
            stats_max_drawdown_equity_percent = get_current_drawdown_equity()
            stats_max_drawdown_time = time
        _current_dev_vs_bo_price = get_current_dev_vs_bo_price()
        if _current_dev_vs_bo_price < stats_biggest_dev:
            stats_biggest_dev = _current_dev_vs_bo_price
            stats_biggest_dev_time = time
    condition_take_profit: bool = False
    condition_stop_external_indicator: bool = False
    condition_stop_loss: bool = False
    condition_planb_timeout: bool = False
    is_deal_started_2 = is_deal_started()
    was_deal_marked_as_finished_3 = was_deal_marked_as_finished()
    is_planb_timeout_1 = is_planb_timeout()
    take_profit_price_hit_1 = take_profit_price_hit()
    is_deal_started_3 = is_deal_started()
    was_deal_marked_as_finished_4 = was_deal_marked_as_finished()
    is_deal_started_4 = is_deal_started()
    was_deal_marked_as_finished_5 = was_deal_marked_as_finished()
    if stop_loss_price_hit() and (not is_deal_started_2) and (not was_deal_marked_as_finished_3):
        condition_stop_loss = True
    elif planb_price_hit() and is_planb_timeout_1 and (cfg_planb_action == 'close deal'):
        condition_planb_timeout = True
    elif deal_end_type == 'Take Profit' and take_profit_price_hit_1 and (not is_deal_started_3) and (not was_deal_marked_as_finished_4):
        condition_take_profit = True
    elif deal_end_type == 'External Indicator' and deal_end_condition == True and is_deal_started_4 and (not was_deal_marked_as_finished_5):
        condition_stop_external_indicator = True
    condition_to_cancel_open_orders = condition_take_profit or condition_stop_external_indicator or condition_stop_loss or condition_planb_timeout
    if condition_to_cancel_open_orders:
        if condition_to_cancel_open_orders:
            strategy.cancel_all()
        stats_deals_finished = stats_deals_finished + 1
        glb_total_volume = glb_total_volume + glb_current_deal_position_size * glb_current_deal_avg_price
        _current_days_in_deal = get_days(glb_dealstart_bar_time, time)
        array.push(statsarray_no_of_bars, bar_index - glb_dealstart_bar_index)
        array.push(statsarray_no_of_days, _current_days_in_deal)
        if stats_max_days_in_deal <= _current_days_in_deal:
            stats_max_days_in_deal = _current_days_in_deal
            stats_max_days_in_deal_start_time = glb_dealstart_bar_time
            stats_max_days_in_deal_close_time = time
        if condition_stop_loss:
            stats_deals_stop_loss_finished = stats_deals_stop_loss_finished + 1
            glb_current_deal_pnl = strategy.netprofit - glb_strategy_prev_netprofit
            glb_strategy_prev_netprofit = strategy.netprofit
            glb_current_deal_close_value = glb_current_deal_position_size * glb_stop_loss_price
            glb_total_volume = glb_total_volume + glb_current_deal_close_value
            array.push(statsarray_losing_deals_pnl, glb_current_deal_pnl)
            if cfg_show_pnl_labels:
                label.new(bar_index, glb_stop_loss_price, text=string.tostring(math.round(glb_current_deal_pnl, cfg_decimals)) + '  ' + string.tostring(syminfo.currency) + '\n' + get_timespan_string(glb_dealstart_bar_time, time), yloc=yloc.price, size=size.normal, style=label.style_label_down, textcolor=color.black, color=get_bg_color_red())
            _alert_human = 'D' + string.tostring(stats_deals_started) + '-SL [delayed] (' + string.tostring(syminfo.basecurrency) + '_' + string.tostring(syminfo.currency) + (' LONG' if cfg_strategy_type == 'long' else ' SHORT') + ') | ' + string.tostring(math.round(glb_current_deal_pnl, cfg_decimals)) + ' ' + string.tostring(syminfo.currency) + ' | ' + get_timespan_string(glb_dealstart_bar_time, time)
            alert(_alert_human, alert.freq_once_per_bar_close)
        elif condition_planb_timeout:
            stats_deals_timeout_finished = stats_deals_timeout_finished + 1
            glb_current_deal_pnl = strategy.netprofit - glb_strategy_prev_netprofit
            glb_strategy_prev_netprofit = strategy.netprofit
            glb_current_deal_close_value = glb_current_deal_position_size * open
            glb_total_volume = glb_total_volume + glb_current_deal_close_value
            array.push(statsarray_timeout_deals_pnl, glb_current_deal_pnl)
            if glb_current_deal_pnl >= 0:
                array.push(statsarray_winning_deals_pnl, glb_current_deal_pnl)
            else:
                array.push(statsarray_losing_deals_pnl, glb_current_deal_pnl)
            array.set(statsarray_safety_orders, count_executed_safety_orders, array.get(statsarray_safety_orders, count_executed_safety_orders) + 1)
            array.set(statsarray_safety_orders_timeout, count_executed_safety_orders, array.get(statsarray_safety_orders_timeout, count_executed_safety_orders) + 1)
            if cfg_show_pnl_labels:
                label.new(bar_index, glb_planb_timeout_price, text='' + string.tostring(math.round(glb_current_deal_pnl, cfg_decimals)) + '  ' + string.tostring(syminfo.currency) + '\n' + get_timespan_string(glb_dealstart_bar_time, time), yloc=yloc.price, size=size.normal, style=label.style_label_down, textcolor=color.black, color=get_bg_color_lightblue())
            _alert_human = 'D' + string.tostring(stats_deals_started) + '-TIMEOUT [delayed] (' + string.tostring(syminfo.basecurrency) + '_' + string.tostring(syminfo.currency) + (' LONG' if cfg_strategy_type == 'long' else ' SHORT') + ') | ' + string.tostring(math.round(glb_current_deal_pnl, cfg_decimals)) + ' ' + string.tostring(syminfo.currency) + ' | ' + get_timespan_string(glb_dealstart_bar_time, time)
            alert(_alert_human, alert.freq_once_per_bar_close)
        elif condition_take_profit:
            array.set(statsarray_safety_orders, count_executed_safety_orders, array.get(statsarray_safety_orders, count_executed_safety_orders) + 1)
            stats_deals_take_profit_finished = stats_deals_take_profit_finished + 1
            glb_current_deal_pnl = strategy.netprofit - glb_strategy_prev_netprofit
            glb_strategy_prev_netprofit = strategy.netprofit
            glb_current_deal_close_value = glb_current_deal_position_size * glb_take_profit_price
            glb_total_volume = glb_total_volume + glb_current_deal_close_value
            array.push(statsarray_winning_deals_pnl, glb_current_deal_pnl)
            if cfg_show_pnl_labels:
                label.new(bar_index, glb_take_profit_price, text='' + string.tostring(math.round(glb_current_deal_pnl, cfg_decimals)) + '  ' + string.tostring(syminfo.currency) + '\n' + get_timespan_string(glb_dealstart_bar_time, time), yloc=yloc.price, size=size.normal, style=label.style_label_up, textcolor=color.black, color=get_bg_color_green())
            _alert_human = 'D' + string.tostring(stats_deals_started) + '-TP [delayed] (' + string.tostring(syminfo.basecurrency) + '_' + string.tostring(syminfo.currency) + (' LONG' if cfg_strategy_type == 'long' else ' SHORT') + ') | ' + string.tostring(math.round(glb_current_deal_pnl, cfg_decimals)) + ' ' + string.tostring(syminfo.currency) + ' | ' + get_timespan_string(glb_dealstart_bar_time, time)
            alert(_alert_human, alert.freq_once_per_bar_close)
        elif condition_stop_external_indicator:
            if cfg_enable_bot_control and cfg_exec_external_indicator:
                _alert_json = get_3cbot_stopdeal_json()
                strategy.order(id='D' + string.tostring(stats_deals_started) + '-EXT-IND', direction=strategy.short if IS_LONG else strategy.long, qty=math.abs(strategy.position_size), alert_message=_alert_json)
            else:
                strategy.order(id='D' + string.tostring(stats_deals_started) + '-EXT-IND', direction=strategy.short if IS_LONG else strategy.long, qty=math.abs(strategy.position_size))
            array.set(statsarray_safety_orders, count_executed_safety_orders, array.get(statsarray_safety_orders, count_executed_safety_orders) + 1)
            stats_deals_take_profit_finished = stats_deals_take_profit_finished + 1
            glb_current_deal_close_value = glb_current_deal_position_size * close
            glb_total_volume = glb_total_volume + glb_current_deal_close_value
            glb_current_deal_pnl = strategy.openprofit - get_commission_for_volume(glb_current_deal_close_value)
            glb_strategy_prev_netprofit = strategy.netprofit + glb_current_deal_pnl
            if glb_current_deal_pnl >= 0:
                array.push(statsarray_winning_deals_pnl, glb_current_deal_pnl)
            else:
                array.push(statsarray_losing_deals_pnl, glb_current_deal_pnl)
            if cfg_show_pnl_labels:
                label.new(bar_index, close, text='' + string.tostring(math.round(glb_current_deal_pnl, cfg_decimals)) + '  ' + string.tostring(syminfo.currency) + '\n' + get_timespan_string(glb_dealstart_bar_time, time), yloc=yloc.price, size=size.normal, style=label.style_label_up, textcolor=color.black, color=get_bg_color_orange())
            _alert_human = 'D' + string.tostring(stats_deals_started) + '-EXT-IND [delayed] (' + string.tostring(syminfo.basecurrency) + '_' + string.tostring(syminfo.currency) + (' LONG' if cfg_strategy_type == 'long' else ' SHORT') + ') | ' + string.tostring(math.round(glb_current_deal_pnl, cfg_decimals)) + ' ' + string.tostring(syminfo.currency) + ' | ' + get_timespan_string(glb_dealstart_bar_time, time)
            alert(_alert_human, alert.freq_once_per_bar_close)
        glb_still_in_deal = False
        lastdeal_close_bar_index = bar_index
        lastdeal_close_time = time
        glb_take_profit_price = na
        glb_planb_timeout_price = na
        glb_stop_loss_price = na
        glb_base_order_price = na
        glb_base_order_qty = na
        glb_next_safety_order_price = na
        glb_so_orders_placed = False
        glb_current_deal_position_size = na
        glb_current_deal_avg_price = na
        glb_current_deal_close_value = na
        glb_current_deal_pnl = 0
        glb_debug_text = ''
        debug_printed = False
        glb_dealstart_bar_index = na
        glb_dealstart_bar_time = na
        count_executed_safety_orders = 0
    _color_avg_price = theme_text_color
    _color_take_profit = get_bg_color_green(90)
    if is_planb_timeout() and cfg_planb_action != 'none':
        _color_avg_price = get_bg_color_lightblue()
    if is_planb_timeout() and cfg_planb_action == 'close deal':
        _color_take_profit = get_bg_color_green(100)
    p1 = plot(glb_take_profit_price, color=get_bg_color_green(), style=plot.style_circles, title='Take Profit')
    p2 = plot(strategy.position_avg_price, color=theme_text_color, style=plot.style_circles, title='Deal avg price')
    p3 = plot(glb_next_safety_order_price, color=get_bg_color_orange(), style=plot.style_circles, title='Safety order')
    p4 = plot(glb_stop_loss_price, color=get_bg_color_red(), style=plot.style_circles, title='Stop loss')
    p5 = plot(glb_planb_timeout_price, color=get_bg_color_lightblue(), style=plot.style_circles, title='PLAN-B')
    fill(p1, p2, color=_color_take_profit, title='Fill take profit')
    fill(p2, p3, color=get_bg_color_orange(90), title='Fill safety order')
    fill(p2, p5, color=get_bg_color_lightblue(90), title='Fill PLAN-B')
    fill(p3, p4, color=get_bg_color_red(90), title='Fill stop loss')
    _col = get_bg_color_red(90) if cfg_max_safety_orders == 0 or na(glb_next_safety_order_price) else get_bg_color_red(100)
    fill(p2, p4, color=_col, title='Fill stop loss')
    if barstate.islastconfirmedhistory:
        glb_required_capital = get_required_capital()
        _deal_in_progress = stats_deals_finished < stats_deals_started
        if _deal_in_progress:
            lastdeal_close_bar_index = bar_index
            lastdeal_close_time = time
            array.push(statsarray_no_of_bars, bar_index - glb_dealstart_bar_index)
            array.push(statsarray_no_of_days, get_days(glb_dealstart_bar_time, time_close))
            if stats_max_days_in_deal <= get_days(glb_dealstart_bar_time, time_close):
                stats_max_days_in_deal = get_days(glb_dealstart_bar_time, time_close)
                stats_max_days_in_deal_start_time = glb_dealstart_bar_time
                stats_max_days_in_deal_close_time = time_close
        _text_warnings: str = ''
        if stats_deals_started == 0:
            _text_warnings = _text_warnings + ' - No deal started\n'
        if stats_deals_finished == 0:
            _text_warnings = _text_warnings + ' - No deal finished\n'
        valid_stop_loss_1 = valid_stop_loss()
        if cfg_enable_stop_loss and valid_stop_loss_1 == False:
            _text_warnings = _text_warnings + ' - Stop loss is less than last safety order (should be more than ' + string.tostring(math.round(stepped_deviation(cfg_max_safety_orders), 2)) + '%' + ')\n'
        if stepped_deviation(cfg_max_safety_orders) > 100:
            _text_warnings = _text_warnings + ' - Covered deviation via safety orders is over 100%\n'
        if _text_warnings != '':
            warnings: Table = table.new(position.bottom_center, columns=1, rows=2, frame_width=1, frame_color=color.red, border_width=1, border_color=color.red, bgcolor=color.red)
            table.cell(warnings, 0, 0, 'WARNINGS!\n(Fix them, otherwise the stats are innacurate)', text_color=color.white, text_halign=text.align_center)
            table.cell(warnings, 0, 1, _text_warnings, text_color=color.white, text_halign=text.align_left)
        if cfg_show_step_table:
            if cfg_steps_bo_price == 0 or na(cfg_steps_bo_price):
                cfg_steps_bo_price = close
            _steps_bo_size = cfg_base_order_size_usd / cfg_steps_bo_price
            steps_amount: Table = table.new(position.bottom_left, columns=12, rows=cast_int(cfg_max_safety_orders) + 4, frame_width=1, frame_color=color.black, border_width=1, border_color=color.black, bgcolor=color.green)
            table.cell(steps_amount, 0, 0, 'Order\nno', text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 1, 0, 'Deviation\n( % )', text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 2, 0, 'Size\n( ' + string.tostring(syminfo.basecurrency) + ' )', text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 3, 0, 'Volume\n( ' + string.tostring(syminfo.currency) + ' )', text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 4, 0, 'Price\n( ' + string.tostring(syminfo.currency) + ' )', text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 5, 0, 'Avg price\n( ' + string.tostring(syminfo.currency) + ' )', text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 6, 0, 'Price for TP\n( ' + string.tostring(syminfo.currency) + ' )', text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 7, 0, '% change\nfor TP', text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 8, 0, '% change\nfor BEP', text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 9, 0, 'Total size\n( ' + string.tostring(syminfo.basecurrency) + ' )', text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 10, 0, 'Total Vol\n( ' + string.tostring(syminfo.currency) + ' )', text_color=color.white, text_size=size.small)
            _steps_total_size: float = _steps_bo_size
            _steps_total_volume: float = cfg_steps_bo_price * _steps_bo_size
            table.cell(steps_amount, 0, 1, 'BO', text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 1, 1, '0', text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 2, 1, string.tostring(math.round(_steps_bo_size, cfg_decimals)), text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 3, 1, string.tostring(math.round(cfg_steps_bo_price * _steps_bo_size, cfg_decimals)), text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 4, 1, string.tostring(math.round(cfg_steps_bo_price, cfg_decimals)), text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 5, 1, string.tostring(math.round(_steps_total_volume / _steps_total_size, cfg_decimals)), text_color=color.white, text_size=size.small)
            _req_price_for_tp = steps_required_price(cfg_steps_bo_price, _steps_total_volume / _steps_total_size, _steps_total_size, cfg_take_profit_perc)
            table.cell(steps_amount, 6, 1, string.tostring(math.round(_req_price_for_tp, cfg_decimals)), text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 7, 1, string.tostring(steps_required_percent(cfg_steps_bo_price, _req_price_for_tp)), text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 8, 1, string.tostring(steps_required_percent(cfg_steps_bo_price, cfg_steps_bo_price)), text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 9, 1, string.tostring(math.round(_steps_total_size, cfg_decimals)), text_color=color.white, text_size=size.small)
            table.cell(steps_amount, 10, 1, string.tostring(_steps_total_volume), text_color=color.white, text_size=size.small)
            _steps_next_safety_order_price: float = 0
            _steps_next_safety_order_qty: float = 0
            if cfg_max_safety_orders > 0 and safety_order_type == 'Percentage':
                for _i in pine_range(1, cfg_max_safety_orders, 1):
                    _steps_next_safety_order_price = next_so_price(_i, cfg_steps_bo_price)
                    _steps_next_safety_order_qty = next_so_qty(_i, cfg_steps_bo_price)
                    _steps_total_size = _steps_total_size + _steps_next_safety_order_qty
                    _steps_total_volume = _steps_total_volume + _steps_next_safety_order_qty * _steps_next_safety_order_price
                    table.cell(steps_amount, 0, _i + 2, string.tostring(_i), text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 1, _i + 2, string.tostring(stepped_deviation(_i)), text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 2, _i + 2, string.tostring(math.round(_steps_next_safety_order_qty, cfg_decimals)), text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 3, _i + 2, string.tostring(math.round(_steps_next_safety_order_qty * _steps_next_safety_order_price, cfg_decimals)), text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 4, _i + 2, string.tostring(math.round(_steps_next_safety_order_price, cfg_decimals)), text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 5, _i + 2, string.tostring(math.round(_steps_total_volume / _steps_total_size, cfg_decimals)), text_color=color.white, text_size=size.small)
                    _req_price_for_tp = steps_required_price(cfg_steps_bo_price, _steps_total_volume / _steps_total_size, _steps_total_size, cfg_take_profit_perc)
                    table.cell(steps_amount, 6, _i + 2, string.tostring(math.round(_req_price_for_tp, cfg_decimals)), text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 7, _i + 2, string.tostring(steps_required_percent(_steps_next_safety_order_price, _req_price_for_tp)), text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 8, _i + 2, string.tostring(steps_required_percent(_steps_next_safety_order_price, _steps_total_volume / _steps_total_size)), text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 9, _i + 2, string.tostring(math.round(_steps_total_size, cfg_decimals)), text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 10, _i + 2, string.tostring(_steps_total_volume), text_color=color.white, text_size=size.small)
            elif cfg_max_safety_orders > 0:
                _steps_next_safety_order_qty_usd: float = 0
                for _i in pine_range(1, cfg_max_safety_orders, 1):
                    _steps_next_safety_order_qty_usd = next_so_size_usd(_i)
                    _steps_total_volume = _steps_total_volume + _steps_next_safety_order_qty_usd
                    table.cell(steps_amount, 0, _i + 2, string.tostring(_i), text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 1, _i + 2, '-', text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 2, _i + 2, '-', text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 3, _i + 2, string.tostring(math.round(_steps_next_safety_order_qty_usd, cfg_decimals)), text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 4, _i + 2, '-', text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 5, _i + 2, '-', text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 6, _i + 2, '-', text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 7, _i + 2, '-', text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 8, _i + 2, '-', text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 9, _i + 2, '-', text_color=color.white, text_size=size.small)
                    table.cell(steps_amount, 10, _i + 2, string.tostring(_steps_total_volume), text_color=color.white, text_size=size.small)
        if cfg_show_stats_table:
            rowsforstats: int = array.size(statsarray_safety_orders) + 25
            sostats: Table = table.new(position.top_right, columns=2, rows=rowsforstats, frame_width=1, frame_color=color.black)
            _row: int = 0
            table.cell(sostats, column=0, row=_row, text='Zendog DCA Backtester ' + string.tostring(syminfo.basecurrency) + ' / ' + string.tostring(syminfo.currency), text_halign=text.align_left, text_size=size.small, text_color=color.white, bgcolor=get_bg_color_blue())
            table.cell(sostats, column=1, row=_row, text='', text_size=size.small, text_color=color.white, bgcolor=get_bg_color_blue())
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Status:', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            if _deal_in_progress:
                table.cell(sostats, column=1, row=_row, text='Deal in progress', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_red())
            elif stats_deals_started == 0 and stats_deals_finished == 0:
                table.cell(sostats, column=1, row=_row, text='No deals', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_red())
            else:
                table.cell(sostats, column=1, row=_row, text='All deals closed', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_green())
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Open deals:', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            if stats_deals_started - stats_deals_finished == 0:
                table.cell(sostats, column=1, row=_row, text='0', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_green())
            else:
                _current_deal_total_value = strategy.position_size * strategy.position_avg_price
                _current_deal_actual_value = strategy.position_size * close
                _current_deal_equity_percent: float = 0
                if IS_LONG:
                    _current_deal_equity_percent = _current_deal_actual_value * 100 / _current_deal_total_value - 100
                else:
                    _current_deal_equity_percent = 100 - _current_deal_actual_value * 100 / _current_deal_total_value
                _text0 = string.tostring(stats_deals_started - stats_deals_finished) + ' deal\n'
                _text0 = _text0 + string.tostring(math.round(strategy.openprofit, cfg_decimals)) + ' ' + string.tostring(syminfo.currency)
                _text0 = _text0 + ' (' + string.tostring(math.round(_current_deal_equity_percent, 2)) + '%)\n'
                _text0 = _text0 + string.tostring(get_timespan_string(glb_dealstart_bar_time, time_close)) + ', currently at SO ' + string.tostring(count_executed_safety_orders + 1) + '\n'
                _text0 = _text0 + '(start: ' + string.tostring(time_to_date_string(glb_dealstart_bar_time)) + ')'
                table.cell(sostats, column=1, row=_row, text=_text0, text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_red())
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Finished deals:', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            table.cell(sostats, column=1, row=_row, text=string.tostring(stats_deals_finished), text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Winning deals:', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            if stats_deals_take_profit_finished == 0:
                table.cell(sostats, column=1, row=_row, text=string.tostring(array.size(statsarray_winning_deals_pnl)), text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            else:
                _text5: str = ''
                _text5 = _text5 + string.tostring(stats_deals_take_profit_finished)
                _text5 = _text5 + ' (' + string.tostring(math.round(array.avg(statsarray_winning_deals_pnl), cfg_decimals))
                _text5 = _text5 + ' ' + string.tostring(syminfo.currency) + ' on avg)'
                table.cell(sostats, column=1, row=_row, text=_text5, text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_green())
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Losing deals:', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            if array.size(statsarray_losing_deals_pnl) == 0:
                table.cell(sostats, column=1, row=_row, text=string.tostring(array.size(statsarray_losing_deals_pnl)), text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_green())
            else:
                _text6: str = ''
                _text6 = _text6 + string.tostring(array.size(statsarray_losing_deals_pnl))
                _text6 = _text6 + ' (' + string.tostring(math.round(array.avg(statsarray_losing_deals_pnl), cfg_decimals))
                _text6 = _text6 + ' ' + string.tostring(syminfo.currency) + ' on avg)'
                table.cell(sostats, column=1, row=_row, text=_text6, text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_red())
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Timeout deals:', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            if stats_deals_timeout_finished == 0:
                table.cell(sostats, column=1, row=_row, text=string.tostring(stats_deals_timeout_finished), text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_green())
            else:
                _text6: str = ''
                _text6 = _text6 + string.tostring(stats_deals_timeout_finished)
                _text6 = _text6 + ' (' + string.tostring(math.round(array.avg(statsarray_timeout_deals_pnl), cfg_decimals))
                _text6 = _text6 + ' ' + string.tostring(syminfo.currency) + ' on avg)'
                table.cell(sostats, column=1, row=_row, text=_text6, text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_lightblue())
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Total time  ( Max  |  Avg time in deal ):', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _text4 = '' + string.tostring(get_timespan_string(bh_start_time, bh_end_time)) + '    ( '
            _text4 = _text4 + '' + get_timestring_from_days(array.max(statsarray_no_of_days)) + '  |  '
            _text4 = _text4 + '' + get_timestring_from_days(array.avg(statsarray_no_of_days)) + ' )'
            table.cell(sostats, column=1, row=_row, text=_text4, text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Total backtest:\n' + string.tostring(time_to_date_string(bh_start_time)) + '\n' + string.tostring(time_to_date_string(bh_end_time)), text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            table.cell(sostats, column=1, row=_row, text='Max days in deal:\n' + string.tostring(time_to_date_string(stats_max_days_in_deal_start_time)) + '\n' + string.tostring(time_to_date_string(stats_max_days_in_deal_close_time)), text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Required capital:', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            table.cell(sostats, column=1, row=_row, text=string.tostring(glb_required_capital) + ' ' + string.tostring(syminfo.currency), text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Profit:\n(after commision)', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _text1 = string.tostring(math.round(get_final_pnl_new(), cfg_decimals)) + ' ' + string.tostring(syminfo.currency)
            _text1 = _text1 + ' (' + string.tostring(math.round(get_final_pnl_prct_new(), 2)) + ' %)\n'
            if get_days(bh_start_time, bh_end_time) >= 1:
                _text1 = _text1 + string.tostring(math.round(get_final_pnl_prct_new() / get_days(bh_start_time, bh_end_time), 2)) + '% / day'
            else:
                _text1 = _text1 + string.tostring(math.round(get_final_pnl_prct_new(), 2)) + '% / day'
            table.cell(sostats, column=1, row=_row, text=_text1, text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _row = _row + 1
            _bh_equity = glb_required_capital / bh_start_price * bh_end_price - glb_required_capital
            _bh_commision = get_commission_for_volume(glb_required_capital + glb_required_capital / bh_start_price * bh_end_price)
            _bh_equity = _bh_equity - _bh_commision
            _bh_prct_total = math.round(_bh_equity * 100 / glb_required_capital, 2)
            table.cell(sostats, column=0, row=_row, text='Buy & hold return:\n(after commision)', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _text2 = string.tostring(math.round(_bh_equity, cfg_decimals)) + ' ' + string.tostring(syminfo.currency)
            _text2 = _text2 + ' (' + string.tostring(_bh_prct_total) + '%)\n'
            if get_days(bh_start_time, bh_end_time) >= 1:
                _text2 = _text2 + string.tostring(math.round(_bh_prct_total / get_days(bh_start_time, bh_end_time), 2)) + '% / day'
            else:
                _text2 = _text2 + string.tostring(math.round(_bh_prct_total, 2)) + '% / day'
            table.cell(sostats, column=1, row=_row, text=_text2, text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Covered deviation:', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            table.cell(sostats, column=1, row=_row, text=string.tostring(math.round(stepped_deviation(cfg_max_safety_orders), 2)) + '%', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _row = _row + 1
            _bef: str = 'before SL' if valid_stop_loss() else ''
            table.cell(sostats, column=0, row=_row, text='Max deviation:\n(Deal start price vs worst candle ' + _bef + ')', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            table.cell(sostats, column=1, row=_row, text=string.tostring(math.round(stats_biggest_dev, 2)) + '%\n' + '(' + time_to_date_string(stats_biggest_dev_time) + ')', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Max drawdown from breakeven:\n(Avg price vs worst candle ' + _bef + ')', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            table.cell(sostats, column=1, row=_row, text=string.tostring(math.round(stats_max_drawdown, cfg_decimals)) + ' ' + string.tostring(syminfo.currency) + ' (' + string.tostring(math.round(stats_max_drawdown_equity_percent, 2)) + '%)\n' + '(' + time_to_date_string(stats_max_drawdown_time) + ')', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Max # bars in deal:', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            table.cell(sostats, column=1, row=_row, text=string.tostring(array.max(statsarray_no_of_bars)), text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Avg # bars in deal:', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            table.cell(sostats, column=1, row=_row, text=string.tostring(math.round(array.avg(statsarray_no_of_bars), 2)), text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Total volume:', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            table.cell(sostats, column=1, row=_row, text=string.tostring(math.round(glb_total_volume, cfg_decimals)) + ' ' + string.tostring(syminfo.currency), text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _row = _row + 1
            table.cell(sostats, column=0, row=_row, text='Commision:', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            table.cell(sostats, column=1, row=_row, text=string.tostring(math.round(get_commission_for_volume(glb_total_volume), cfg_decimals)) + ' ' + string.tostring(syminfo.currency), text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
            _row = _row + 1
            if array.size(statsarray_safety_orders) > 0:
                table.cell(sostats, column=0, row=_row, text='Close stats for ' + string.tostring(stats_deals_finished) + ' deals', text_color=color.white, text_size=size.small, bgcolor=get_bg_color_blue(), text_halign=text.align_left)
                table.cell(sostats, column=1, row=_row, text='Number (%) / Exit with timeout', text_color=color.white, text_size=size.small, bgcolor=get_bg_color_blue())
                _row = _row + 1
                _saved_row = _row
                _row = _row + 2
                _max_safety_orders: int = 0
                _avg_safety_orders: float = 0
                for _i in pine_range(0, array.size(statsarray_safety_orders) - 1, 1):
                    _closed_text: str = ''
                    if _i == 0:
                        _closed_text = 'BO    (' + string.tostring(math.round(stepped_deviation(_i), 2)) + '%)'
                    else:
                        _closed_text = 'SO ' + string.tostring(_i) + ' (' + string.tostring(math.round(stepped_deviation(_i), 2)) + '%)'
                    _cnt = array.get(statsarray_safety_orders, _i)
                    if _cnt > 0 and _i > _max_safety_orders:
                        _max_safety_orders = _i
                    _avg_safety_orders = _avg_safety_orders + _cnt * _i
                    table.cell(sostats, column=0, row=_row + _i, text='Closed with ' + _closed_text, text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row + _i))
                    table.cell(sostats, column=1, row=_row + _i, text=string.tostring(_cnt) + ' (' + string.tostring(math.round(_cnt * 100 / stats_deals_finished, 2)) + '%) / ' + string.tostring(array.get(statsarray_safety_orders_timeout, _i)), text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row + _i))
                _avg_safety_orders = math.round(_avg_safety_orders / array.sum(statsarray_safety_orders), 1)
                table.cell(sostats, column=0, row=_saved_row, text='Max SO used:', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_saved_row))
                table.cell(sostats, column=1, row=_saved_row, text=string.tostring(_max_safety_orders), text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_saved_row))
                table.cell(sostats, column=0, row=_saved_row + 1, text='Avg SO used:', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_saved_row + 1))
                table.cell(sostats, column=1, row=_saved_row + 1, text=string.tostring(_avg_safety_orders), text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_saved_row + 1))
            if valid_stop_loss():
                _row = _row + array.size(statsarray_safety_orders)
                table.cell(sostats, column=0, row=_row, text='Closed with Stop Loss (' + string.tostring(cfg_stop_loss_perc) + '%)', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))
                table.cell(sostats, column=1, row=_row, text=string.tostring(stats_deals_stop_loss_finished) + ' (' + string.tostring(math.round(stats_deals_stop_loss_finished * 100 / stats_deals_finished, 2)) + '%)', text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_red() if stats_deals_stop_loss_finished > 0 else get_bg_color_green())
        if cfg_show_settings_table:
            settings: Table = table.new(position.bottom_left, columns=1, rows=2, frame_width=1, frame_color=color.black)
            _row: int = 0
            table.cell(settings, column=0, row=0, text='DCA Settings', text_halign=text.align_left, text_size=size.small, text_color=color.white, bgcolor=get_bg_color_blue())
            _text = 'Type: ' + string.tostring(cfg_strategy_type) + '; '
            _text = _text + 'Commision: ' + string.tostring(cfg_commision_percent) + '%;\n'
            _text = _text + 'Condition: ' + string.tostring(deal_start_type) + ' '
            if deal_start_type == 'RSI-7':
                _text = _text + string.tostring(rsi_start_operation)
                _text = _text + ' ' + string.tostring(rsi_start_value) + ' \n\n'
            elif deal_start_type == 'External Indicator':
                _text = _text + '( '
                _text = _text + string.tostring(deal_start_operation) + ' '
                _text = _text + string.tostring(deal_start_value)
                _text = _text + ' )\n\n'
            _text = _text + 'TP: ' + string.tostring(cfg_take_profit_perc) + '% '
            _text = _text + ' (' + string.tostring(cfg_take_profit_type) + ')'
            if cfg_enable_stop_loss:
                _text = _text + '\nSL: ' + string.tostring(cfg_stop_loss_perc) + '%'
            _text = _text + '\n\n'
            _text = _text + 'BO: ' + string.tostring(cfg_base_order_size_usd) + ' ' + string.tostring(syminfo.currency) + '; '
            _text = _text + 'SO: ' + string.tostring(cfg_safety_order_size_usd) + ' ' + string.tostring(syminfo.currency) + ';\n'
            _text = _text + 'SO Dev: ' + string.tostring(cfg_safety_order_price_deviation_perc) + '% ; '
            _text = _text + 'Max SO: ' + string.tostring(cfg_max_safety_orders) + '; '
            _text = _text + 'Covered: ' + string.tostring(math.round(stepped_deviation(cfg_max_safety_orders), 2)) + ' %;\n'
            _text = _text + 'SO Volume Scale: ' + string.tostring(cfg_safety_order_volume_scale) + '; '
            _text = _text + 'SO Step Scale: ' + string.tostring(cfg_safety_order_price_step_scale) + ';\n'
            table.cell(settings, column=0, row=1, text=_text, text_halign=text.align_left, text_color=color.black, text_size=size.small, bgcolor=get_bg_color_grey(_row))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
