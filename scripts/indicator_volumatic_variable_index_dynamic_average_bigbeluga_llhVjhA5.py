"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop
from pynecore.core.pine_method import method
from pynecore.core.series import inline_series
from pynecore.lib import (
    array, bar_index, barstate, chart, close, color, display, fill, format,
    high, hl2, input, label, last_bar_index, line, location, low, math, na, nz, open, plot,
    plotshape, script, shape, size, string, ta, volume
)
from pynecore.types import Color, Line, Persistent, PersistentSeries, Series


@script.indicator('Volumatic Variable Index Dynamic Average [BigBeluga]', 'Volumatic VIDYA [BigBeluga]', overlay=True, max_lines_count=500, max_labels_count=500)
def main(
    vidya_length=input.int(10, 'VIDYA Length'),
    vidya_momentum=input.int(20, 'VIDYA Momentum'),
    band_distance=input.float(2, 'Distance factor for upper/lower bands', step=0.1),
    source: Series[float] = input.source(close, 'Source'),
    up_trend_color=input(color.new('#17DFAD'), '+', group='Color', inline='c'),
    down_trend_color=input(color.new('#DD326B'), '-', group='Color', inline='c'),
    shadow=input.bool(True, 'Shadow', group='Color', inline='c')
):
    pivot_left_bars: int = 3
    pivot_right_bars: int = pivot_left_bars

    pivot_line: Persistent[Line] = na(Line)
    volume_value: Persistent[float] = na(float)
    smoothed_value: float = na(float)
    is_trend_up: PersistentSeries[bool] = False

    liquidity_lines_low: Persistent[list[Line]] = array.new_line(500)
    liquidity_lines_high: Persistent[list[Line]] = array.new_line(500)

    up_trend_volume: Persistent[float] = na(float)
    down_trend_volume: Persistent[float] = na(float)

    def vidya_calc(src, vidya_length, vidya_momentum):
        momentum: float = ta.change(src)
        sum_pos_momentum: float = math.sum(momentum if momentum >= 0 else 0.0, vidya_momentum)
        sum_neg_momentum: float = math.sum(0.0 if momentum >= 0 else -momentum, vidya_momentum)
        abs_cmo: float = math.abs(100 * (sum_pos_momentum - sum_neg_momentum) / (sum_pos_momentum + sum_neg_momentum))
        alpha: float = 2 / (vidya_length + 1)
        vidya_value: PersistentSeries[float] = 0.0
        vidya_value = alpha * abs_cmo / 100 * src + (1 - alpha * abs_cmo / 100) * nz(vidya_value[1])

        return ta.sma(vidya_value, 15)

    @method
    def extend_liquidity_lines(line_array: list[Line], price_level: Series[float], is_cross: bool, volume_val):
        __block_result__ = na
        if array.size(line_array) > 0 and last_bar_index - bar_index < 5000:
            __block_result_1__ = na
            __loop_1__ = pine_loop(0, 1)
            while __loop_1__.step(array.size(line_array) - 1):
                i = __loop_1__.value
                __block_result_2__ = na
                if i < array.size(line_array):
                    liquidity_line: Line = array.get(line_array, i)
                    current_line_level: float = line.get_y2(liquidity_line)
                    price_cross: bool = price_level < current_line_level and price_level[1] >= current_line_level if is_cross else price_level > current_line_level and price_level[1] <= current_line_level

                    is_short_line: bool = bar_index - line.get_x1(liquidity_line) < 50

                    __block_result_3__ = na
                    if price_cross and is_short_line:
                        line.set_x2(liquidity_line, bar_index)
                        array.remove(line_array, i)

                        label.new(bar_index - 1, price_level[1], string.tostring(volume_val, format.volume), color=color.rgb(0, 0, 0, 99), style=label.style_label_lower_left if is_cross else label.style_label_upper_left, textcolor=chart.fg_color, size=size.small)

                        __block_result_3__ = label.new(bar_index - 1, price_level[1], text='◉', color=color.new('#00000003'), textcolor=down_trend_color if is_cross else up_trend_color, style=label.style_label_center, size=size.normal)
                    __block_result_2__ = __block_result_3__
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    atr_value: float = ta.atr(200)

    vidya_value = vidya_calc(source, vidya_length, vidya_momentum)

    upper_band: float = vidya_value + atr_value * band_distance
    lower_band: float = vidya_value - atr_value * band_distance

    if ta.crossover(source, upper_band):
        is_trend_up = True
    if ta.crossunder(source, lower_band):
        is_trend_up = False

    if is_trend_up:
        smoothed_value = lower_band
    if not is_trend_up:
        smoothed_value = upper_band
    if ta.change(is_trend_up):
        smoothed_value = na

    pivot_high: bool = not na(ta.pivothigh(pivot_left_bars, pivot_right_bars))
    pivot_low: bool = not na(ta.pivotlow(close, pivot_left_bars, pivot_right_bars))

    if low[pivot_right_bars] > smoothed_value and pivot_low:
        pivot_line = line.new(bar_index[pivot_right_bars], low[pivot_right_bars], bar_index[pivot_right_bars] + 5, low[pivot_right_bars], color=color.new(up_trend_color, 50))

        array.push(liquidity_lines_low, pivot_line)
        volume_value = math.sum(volume, pivot_right_bars + pivot_left_bars) / (pivot_right_bars + pivot_left_bars)

    if high[pivot_right_bars] < smoothed_value and pivot_high:
        pivot_line = line.new(bar_index[pivot_right_bars], high[pivot_right_bars], bar_index[pivot_right_bars] + 5, high[pivot_right_bars], color=color.new(down_trend_color, 50))

        array.push(liquidity_lines_high, pivot_line)
        volume_value = math.sum(-volume, pivot_right_bars + pivot_left_bars) / (pivot_right_bars + pivot_left_bars)

    extend_liquidity_lines(liquidity_lines_high, smoothed_value, True, volume_value)
    extend_liquidity_lines(liquidity_lines_low, smoothed_value, False, volume_value)

    trend_cross_up: Series[bool] = not is_trend_up[1] and is_trend_up
    trend_cross_down: Series[bool] = not is_trend_up and is_trend_up[1]

    if ta.change(trend_cross_up) or ta.change(trend_cross_down):
        up_trend_volume = 0
        down_trend_volume = 0

    if not (ta.change(trend_cross_up) or ta.change(trend_cross_down)):
        up_trend_volume = up_trend_volume + (volume if close > open else 0)
        down_trend_volume = down_trend_volume + (volume if close < open else 0)

    avg_volume_delta: float = (up_trend_volume + down_trend_volume) / 2

    trend_color: Color = up_trend_color if is_trend_up else down_trend_color if not is_trend_up else chart.fg_color

    delta_volume: str = '0%' if string.tostring((up_trend_volume - down_trend_volume) / avg_volume_delta * 100, format.percent) == 'NaN%' else string.tostring((up_trend_volume - down_trend_volume) / avg_volume_delta * 100, format.percent)

    if barstate.islast:
        label.delete(inline_series(label.new(bar_index, smoothed_value, 'Buy: ' + string.tostring(up_trend_volume, format.volume) + '\n Sell: ' + string.tostring(down_trend_volume, format.volume) + '\nDelta Volume: ' + delta_volume, color=color.new(trend_color, 90), style=label.style_label_upper_left if is_trend_up else label.style_label_lower_left, textcolor=chart.fg_color), 1))

        label.delete(inline_series(label.new(bar_index, smoothed_value, text='✪', color=color.new('#00000003'), textcolor=trend_color, style=label.style_label_center, size=size.large), 1))

    p1 = plot(smoothed_value, color=trend_color, linewidth=2, style=plot.style_linebr)
    p2 = plot(hl2, display=display.none)

    fill(p1, p2, smoothed_value, hl2, color.new(trend_color, 80 if shadow else 100), na)

    plotshape(series=smoothed_value if trend_cross_up[1] else na, title='Trend Up', style=shape.labelup, location=location.absolute, color=color.new(up_trend_color, 50), text='▲', textcolor=chart.fg_color)

    plotshape(series=smoothed_value if trend_cross_down[1] else na, title='Trend Down', style=shape.labeldown, location=location.absolute, color=color.new(down_trend_color, 50), text='▼', textcolor=chart.fg_color)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
