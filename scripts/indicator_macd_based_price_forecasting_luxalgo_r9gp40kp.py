"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.core.series import inline_series
from pynecore.lib import (
    array, bar_index, barstate, chart, close, color, display, fill, input,
    map, math, na, plot, polyline, script, ta
)
from pynecore.types import NA, Persistent, Series
from pynecore.types.chart import ChartPoint


@udt
class vector:
    id: list[float] = na(list)


@udt
class holder:
    id: 'list[vector]' = na(list)


@script.indicator('MACD Based Price Forecasting [LuxAlgo]', 'LuxAlgo - MACD Based Price Forecasting', overlay=True, max_lines_count=500)
def main(
    fast=input.int(12, 'Fast Length', minval=2, group='MACD'),
    slow=input.int(26, 'Slow Length', minval=2, group='MACD'),
    sigLen=input.int(9, 'Signal Length', minval=2, group='MACD'),
    trend=input.string('MACD - Signal', 'Trend Determination', options=('MACD', 'MACD - Signal'), group='MACD'),
    maxMemory=input.int(50, 'Maximum Memory', minval=2, group='Forecast'),
    fcast=input.int(100, 'Forecasting Length', minval=1, group='Forecast'),
    upPer=input(80, 'Top Percentile', group='Forecast'),
    midPer=input(50, 'Average Percentage', group='Forecast'),
    dnPer=input(20, 'Bottom Percentile', group='Forecast'),
    upLine=input(color.new('#3179F5'), 'Line Color', inline='css', group='Style'),
    dnLine=input(color.new('#FF5D00'), '', inline='css', group='Style'),
    upArea=input(color.new(color.new('#3179F5'), 80), 'Areas', inline='areas', group='Style'),
    dnArea=input(color.new(color.new('#FF5D00'), 80), '', inline='areas', group='Style'),
    signalArea=input(True, 'Signal Area', inline='signal', group='Style'),
    signalBull=input(color.new(color.new('#089981'), 50), '', inline='signal', group='Style'),
    signalBear=input(color.new(color.new('#F23645'), 50), '', inline='signal', group='Style')
):
    n = bar_index
    @method
    def populate(get_holder: holder, idx, init_price):
        if array.size(get_holder.id) < idx + 1:
            array.push(get_holder.id, vector(array.new_float(0)))
        method_call('unshift', array.get(get_holder.id, idx).id, close - init_price)
        __block_result__ = na
        if method_call('size', array.get(get_holder.id, idx).id) > maxMemory:
            __block_result__ = method_call('pop', array.get(get_holder.id, idx).id)
        return __block_result__

    @method
    def forecast(get_holder: holder, idx, init_price, upper_coords, mid_coords, lower_coords):
        max_horizon = array.size(get_holder.id)
        x: int = 0
        __block_result_1__ = na
        __loop_0__ = pine_loop(idx - 1, 1)
        while __loop_0__.step(math.min(idx + fcast, max_horizon - 1)):
            i = __loop_0__.value
            get_vector = array.get(get_holder.id, i)
            upper = init_price + method_call('percentile_linear_interpolation', get_vector.id, upPer)
            mid = init_price + method_call('percentile_linear_interpolation', get_vector.id, midPer)
            lower = init_price + method_call('percentile_linear_interpolation', get_vector.id, dnPer)
            method_call('push', upper_coords, chart.point.from_index(n + x, upper))
            method_call('push', mid_coords, chart.point.from_index(n + x, mid))
            method_call('unshift', lower_coords, chart.point.from_index(n + x, lower))
            x = x + 1
            __block_result_1__ = x
        return __block_result_1__

    memory: Persistent[dict[int, holder]] = map.new()
    up_idx: Persistent[int] = 0
    dn_idx: Persistent[int] = 0
    uptrend_init_price: Persistent = close
    downtrend_init_price: Persistent = close
    macd, signal, _ = ta.macd(close, fast, slow, sigLen)
    if barstate.isfirst:
        map.put(memory, 1, holder(array.new(0, NA(vector))))
        map.put(memory, 0, holder(array.new(0, NA(vector))))
    __block_result_2__ = na
    __switch__ = trend
    if __switch__ == 'MACD':
        __block_result_2__ = ta.cross(macd, 0)
    else:
        __block_result_2__ = ta.cross(macd, signal)
    trigger = __block_result_2__
    uptrend: Series = macd > 0 if trend == 'MACD' else macd > signal
    downtrend: Series = macd < 0 if trend == 'MACD' else macd < signal
    uptrend_init_price = close if uptrend and (not uptrend[1]) else uptrend_init_price
    downtrend_init_price = close if downtrend and (not downtrend[1]) else downtrend_init_price
    init_value: Series = uptrend_init_price if uptrend else downtrend_init_price
    if uptrend:
        get_holder = map.get(memory, 1)
        method_call(populate, get_holder, up_idx, uptrend_init_price)
    if downtrend:
        get_holder = map.get(memory, 0)
        method_call(populate, get_holder, dn_idx, downtrend_init_price)
    up_idx = 0 if not uptrend else up_idx + 1
    dn_idx = 0 if not downtrend else dn_idx + 1
    if trigger:
        upper_coords: list[ChartPoint] = array.new(0, NA(ChartPoint))
        mid_coords: list[ChartPoint] = array.new(0, NA(ChartPoint))
        lower_coords: list[ChartPoint] = array.new(0, NA(ChartPoint))
        if uptrend:
            get_holder = map.get(memory, 1)
            method_call(forecast, get_holder, up_idx, uptrend_init_price, upper_coords, mid_coords, lower_coords)
        else:
            get_holder = map.get(memory, 0)
            method_call(forecast, get_holder, dn_idx, downtrend_init_price, upper_coords, mid_coords, lower_coords)
        polyline.delete(inline_series(polyline.new(mid_coords, line_color=upLine if uptrend else dnLine), 1))
        polyline.delete(inline_series(polyline.new(array.concat(upper_coords, lower_coords), line_color=na, fill_color=upArea if uptrend else dnArea), 1))
    init_plot = plot(init_value, 'Reference Price', na if init_value != init_value[1] else color.gray)
    price_plot = plot(close, editable=False, display=display.none)
    top_css = na if not signalArea else signalBull if uptrend else color.new(chart.bg_color, 100)
    btm_css = na if not signalArea else color.new(chart.bg_color, 100) if uptrend else signalBear
    fill(init_plot, price_plot, top_value=math.max(close, uptrend_init_price if uptrend else downtrend_init_price), bottom_value=math.min(close, uptrend_init_price if uptrend else downtrend_init_price), top_color=top_css, bottom_color=btm_css)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
