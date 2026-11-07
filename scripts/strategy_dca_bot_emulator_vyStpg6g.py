"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    close, high, hl2, hlc3, input, low, math, na, ohlc4, open, script,
    strategy, string, time, timestamp
)
from pynecore.types import Persistent


@script.strategy('DCA Bot Emulator', overlay=True, pyramiding=999, default_qty_type=strategy.cash, initial_capital=10000, commission_value=0.02, margin_long=0, margin_short=0, default_qty_value=1, close_by_id=True, na_bool=True)
def main(
    from_month=input.int(defval=1, title='From Month', minval=1, maxval=12),
    from_day=input.int(defval=1, title='From Day', minval=1, maxval=31),
    from_year=input(defval=2021, title='From Year'),
    to_month=input.int(defval=1, title='To Month', minval=1, maxval=12),
    to_day=input.int(defval=1, title='To Day', minval=1, maxval=31),
    to_year=input(defval=9999, title='To Year'),
    source_type=input.string('OHLC4', 'Source', options=('Close', 'Open', 'High', 'Low', 'HL2', 'HLC3', 'OHLC4', 'Median Body', 'Weighted Close', 'Trend Biased', 'Trend Biased Extreme')),
    __input_7__=input.float(2.0, title='Price deviation to open safety orders (%)', minval=0.0),
    __input_8__=input.float(1.0, title='Target Take Profit (%)', step=0.01, minval=0.0),
    __input_9__=input.float(0.0, title='Trailing deviation. Default= 0.0 (%)', step=0.01, minval=0.0),
    base_order=input(10.0, title='base order'),
    safe_order=input(10.0, title='safe order'),
    safe_order_volume_scale=input.float(1.1, step=0.01, title='Safety order volume scale'),
    safe_order_step_scale=input.float(1.1, step=0.01, title='Safety order step scale'),
    max_safe_order=input(30, title='max safe order')
):
    start = timestamp(from_year, from_month, from_day, 0, 0)
    finish = timestamp(to_year, to_month, to_day, 23, 59)
    window = True if time >= start and time <= finish else False
    def source_function(type):
        __block_result__ = na
        if type == 'Close':
            __block_result__ = close
        elif type == 'Open':
            __block_result__ = open
        elif type == 'High':
            __block_result__ = high
        elif type == 'Low':
            __block_result__ = low
        elif type == 'HL2':
            __block_result__ = hl2
        elif type == 'HL3':
            __block_result__ = hlc3
        elif type == 'OHLC4':
            __block_result__ = ohlc4
        elif type == 'Median Body':
            __block_result__ = (open + close) / 2
        elif type == 'Weighted Close':
            __block_result__ = (high + low + 2 * close) / 4
        elif type == 'Trend Biased':
            __block_result__ = (high + close) / 2 if close > open else (low + close) / 2
        elif type == 'Trend Biased Extreme':
            __block_result__ = high if close > open else low
        return __block_result__

    def truncate(number, decimals):
        factor = math.pow(10, decimals)
        return cast_int(number * factor) / factor

    price_deviation = __input_7__ / 100
    take_profit = __input_8__ / 100
    trailing = __input_9__ / 100
    current_so: Persistent[int] = 0
    initial_order: Persistent[float] = 0.0
    previous_high_value: Persistent[float] = 0.0
    original_ttp_value: Persistent[float] = 0.0
    take_profit_level = strategy.position_avg_price * (1 + take_profit)
    source_function_1 = source_function(source_type)
    if strategy.position_size == 0 and window and (source_function_1 > 0) and (previous_high_value == 0.0):
        strategy.entry('Long @' + string.tostring(source_function(source_type)), strategy.long, qty=base_order / source_function(source_type))
        initial_order = source_function(source_type)
        current_so = 1
        previous_high_value = 0.0
        original_ttp_value = 0
    threshold: float = 0.0
    if safe_order_step_scale == 1.0:
        threshold = initial_order - initial_order * price_deviation * safe_order_step_scale * current_so
    else:
        threshold = initial_order - initial_order * ((price_deviation * math.pow(safe_order_step_scale, current_so) - price_deviation) / (safe_order_step_scale - 1))
    source_function_2 = source_function(source_type)
    if current_so > 0 and source_function_2 <= threshold and (current_so <= max_safe_order) and (previous_high_value == 0.0):
        strategy.entry('SO ' + string.tostring(current_so) + '@' + string.tostring(source_function(source_type)), direction=strategy.long, qty=safe_order * math.pow(safe_order_volume_scale, current_so - 1) / source_function(source_type))
        current_so = current_so + 1
    if take_profit_level <= source_function(source_type) and strategy.position_size > 0 or previous_high_value > 0.0:
        if trailing > 0.0:
            if previous_high_value > 0.0:
                if source_function(source_type) >= previous_high_value:
                    previous_high_value = source_function(source_type)
                else:
                    previous_high_percent = (previous_high_value - original_ttp_value) * 1.0 / original_ttp_value
                    current_high_percent = (source_function(source_type) - original_ttp_value) * 1.0 / original_ttp_value
                    if previous_high_percent - current_high_percent >= trailing:
                        strategy.close_all(comment='Close (trailing) @' + string.tostring(truncate(current_high_percent * 100, 3)) + '%')
                        current_so = 0
                        previous_high_value = 0
                        original_ttp_value = 0
            else:
                previous_high_value = source_function(source_type)
                original_ttp_value = source_function(source_type)
        else:
            strategy.close_all(comment='Close @' + string.tostring(source_function(source_type)))
            current_so = 0
            previous_high_value = 0
            original_ttp_value = 0


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
