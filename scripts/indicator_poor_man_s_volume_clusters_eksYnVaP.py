"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    bar_index, barmerge, barstate, close, color, high, input, label, line,
    location, low, math, na, plot, plotshape, request, script, shape, size, ta, time, time_close,
    timeframe, volume, xloc, yloc
)
from pynecore.types import Label, Line, Persistent, Series


@script.indicator('Poor man\'s volume clusters', 'PMVolClust', overlay=True, max_bars_back=500, na_bool=True)
def main(
    block_size=input.int(15, 'Bars in profile block', minval=10, maxval=166),
    visual_row_width=input.float(10.0, 'Visual row width', minval=10),
    show_vpoc=input(True, 'Show volume point of control'),
    filter_size=input(200, 'Profile maximum high pass filter size in bars'),
    use_custom_volume_source=input(False, 'Use custom volume source'),
    volume_source_symbol=input.symbol('', 'Custom volume source symbol')
):
    BOUNARY_COLOR = color.blue
    PROFILE1_COLOR = color.purple
    PROFILE2_COLOR = color.teal
    VPOC_COLOR = color.orange
    custom_volume: Series = request.security(volume_source_symbol, timeframe.period, volume, lookahead=barmerge.lookahead_on) if use_custom_volume_source else volume
    block_index: Series = math.floor(bar_index / block_size)
    block_bar = bar_index % block_size
    rolling_high: Series = ta.highest(block_bar + 1)
    rolling_low: Series = ta.lowest(block_bar + 1)
    block_high: Series = rolling_high[block_bar + 1]
    block_low: Series = rolling_low[block_bar + 1]
    block_height = block_high - block_low
    row_height = block_height / 15
    n_rows_affected: int = 0
    row0_low = block_low + row_height * 0
    row0_high = block_low + row_height * 1
    row0_price: Series = (row0_low + row0_high) / 2
    row0_value: Series[float] = 0.0
    if high[block_size] > row0_low and low[block_size] < row0_high:
        row0_value = custom_volume[block_size]
        n_rows_affected = n_rows_affected + 1
    row1_low = block_low + row_height * 1
    row1_high = block_low + row_height * 2
    row1_price: Series = (row1_low + row1_high) / 2
    row1_value: Series[float] = 0.0
    if high[block_size] > row1_low and low[block_size] < row1_high:
        row1_value = custom_volume[block_size]
        n_rows_affected = n_rows_affected + 1
    row2_low = block_low + row_height * 2
    row2_high = block_low + row_height * 3
    row2_price: Series = (row2_low + row2_high) / 2
    row2_value: Series[float] = 0.0
    if high[block_size] > row2_low and low[block_size] < row2_high:
        row2_value = custom_volume[block_size]
        n_rows_affected = n_rows_affected + 1
    row3_low = block_low + row_height * 3
    row3_high = block_low + row_height * 4
    row3_price: Series = (row3_low + row3_high) / 2
    row3_value: Series[float] = 0.0
    if high[block_size] > row3_low and low[block_size] < row3_high:
        row3_value = custom_volume[block_size]
        n_rows_affected = n_rows_affected + 1
    row4_low = block_low + row_height * 4
    row4_high = block_low + row_height * 5
    row4_price: Series = (row4_low + row4_high) / 2
    row4_value: Series[float] = 0.0
    if high[block_size] > row4_low and low[block_size] < row4_high:
        row4_value = custom_volume[block_size]
        n_rows_affected = n_rows_affected + 1
    row5_low = block_low + row_height * 5
    row5_high = block_low + row_height * 6
    row5_price: Series = (row5_low + row5_high) / 2
    row5_value: Series[float] = 0.0
    if high[block_size] > row5_low and low[block_size] < row5_high:
        row5_value = custom_volume[block_size]
        n_rows_affected = n_rows_affected + 1
    row6_low = block_low + row_height * 6
    row6_high = block_low + row_height * 7
    row6_price: Series = (row6_low + row6_high) / 2
    row6_value: Series[float] = 0.0
    if high[block_size] > row6_low and low[block_size] < row6_high:
        row6_value = custom_volume[block_size]
        n_rows_affected = n_rows_affected + 1
    row7_low = block_low + row_height * 7
    row7_high = block_low + row_height * 8
    row7_price: Series = (row7_low + row7_high) / 2
    row7_value: Series[float] = 0.0
    if high[block_size] > row7_low and low[block_size] < row7_high:
        row7_value = custom_volume[block_size]
        n_rows_affected = n_rows_affected + 1
    row8_low = block_low + row_height * 8
    row8_high = block_low + row_height * 9
    row8_price: Series = (row8_low + row8_high) / 2
    row8_value: Series[float] = 0.0
    if high[block_size] > row8_low and low[block_size] < row8_high:
        row8_value = custom_volume[block_size]
        n_rows_affected = n_rows_affected + 1
    row9_low = block_low + row_height * 9
    row9_high = block_low + row_height * 10
    row9_price: Series = (row9_low + row9_high) / 2
    row9_value: Series[float] = 0.0
    if high[block_size] > row9_low and low[block_size] < row9_high:
        row9_value = custom_volume[block_size]
        n_rows_affected = n_rows_affected + 1
    row10_low = block_low + row_height * 10
    row10_high = block_low + row_height * 11
    row10_price: Series = (row10_low + row10_high) / 2
    row10_value: Series[float] = 0.0
    if high[block_size] > row10_low and low[block_size] < row10_high:
        row10_value = custom_volume[block_size]
        n_rows_affected = n_rows_affected + 1
    row11_low = block_low + row_height * 11
    row11_high = block_low + row_height * 12
    row11_price: Series = (row11_low + row11_high) / 2
    row11_value: Series[float] = 0.0
    if high[block_size] > row11_low and low[block_size] < row11_high:
        row11_value = custom_volume[block_size]
        n_rows_affected = n_rows_affected + 1
    row12_low = block_low + row_height * 12
    row12_high = block_low + row_height * 13
    row12_price: Series = (row12_low + row12_high) / 2
    row12_value: Series[float] = 0.0
    if high[block_size] > row12_low and low[block_size] < row12_high:
        row12_value = custom_volume[block_size]
        n_rows_affected = n_rows_affected + 1
    row13_low = block_low + row_height * 13
    row13_high = block_low + row_height * 14
    row13_price: Series = (row13_low + row13_high) / 2
    row13_value: Series[float] = 0.0
    if high[block_size] > row13_low and low[block_size] < row13_high:
        row13_value = custom_volume[block_size]
        n_rows_affected = n_rows_affected + 1
    row14_low = block_low + row_height * 14
    row14_high = block_low + row_height * 15
    row14_price: Series = (row14_low + row14_high) / 2
    row14_value: Series[float] = 0.0
    if high[block_size] > row14_low and low[block_size] < row14_high:
        row14_value = custom_volume[block_size]
        n_rows_affected = n_rows_affected + 1
    row0_value = row0_value / n_rows_affected / row_height
    row1_value = row1_value / n_rows_affected / row_height
    row2_value = row2_value / n_rows_affected / row_height
    row3_value = row3_value / n_rows_affected / row_height
    row4_value = row4_value / n_rows_affected / row_height
    row5_value = row5_value / n_rows_affected / row_height
    row6_value = row6_value / n_rows_affected / row_height
    row7_value = row7_value / n_rows_affected / row_height
    row8_value = row8_value / n_rows_affected / row_height
    row9_value = row9_value / n_rows_affected / row_height
    row10_value = row10_value / n_rows_affected / row_height
    row11_value = row11_value / n_rows_affected / row_height
    row12_value = row12_value / n_rows_affected / row_height
    row13_value = row13_value / n_rows_affected / row_height
    row14_value = row14_value / n_rows_affected / row_height
    if block_bar != 0:
        row0_value = row0_value + row0_value[1]
        row1_value = row1_value + row1_value[1]
        row2_value = row2_value + row2_value[1]
        row3_value = row3_value + row3_value[1]
        row4_value = row4_value + row4_value[1]
        row5_value = row5_value + row5_value[1]
        row6_value = row6_value + row6_value[1]
        row7_value = row7_value + row7_value[1]
        row8_value = row8_value + row8_value[1]
        row9_value = row9_value + row9_value[1]
        row10_value = row10_value + row10_value[1]
        row11_value = row11_value + row11_value[1]
        row12_value = row12_value + row12_value[1]
        row13_value = row13_value + row13_value[1]
        row14_value = row14_value + row14_value[1]
    vpoc_price: float = na(float)
    highest_row_value: Series[float] = 0.0
    if block_bar == block_size - 1:
        if highest_row_value < row0_value:
            highest_row_value = row0_value
            vpoc_price = row0_price
        if highest_row_value < row1_value:
            highest_row_value = row1_value
            vpoc_price = row1_price
        if highest_row_value < row2_value:
            highest_row_value = row2_value
            vpoc_price = row2_price
        if highest_row_value < row3_value:
            highest_row_value = row3_value
            vpoc_price = row3_price
        if highest_row_value < row4_value:
            highest_row_value = row4_value
            vpoc_price = row4_price
        if highest_row_value < row5_value:
            highest_row_value = row5_value
            vpoc_price = row5_price
        if highest_row_value < row6_value:
            highest_row_value = row6_value
            vpoc_price = row6_price
        if highest_row_value < row7_value:
            highest_row_value = row7_value
            vpoc_price = row7_price
        if highest_row_value < row8_value:
            highest_row_value = row8_value
            vpoc_price = row8_price
        if highest_row_value < row9_value:
            highest_row_value = row9_value
            vpoc_price = row9_price
        if highest_row_value < row10_value:
            highest_row_value = row10_value
            vpoc_price = row10_price
        if highest_row_value < row11_value:
            highest_row_value = row11_value
            vpoc_price = row11_price
        if highest_row_value < row12_value:
            highest_row_value = row12_value
            vpoc_price = row12_price
        if highest_row_value < row13_value:
            highest_row_value = row13_value
            vpoc_price = row13_price
        if highest_row_value < row14_value:
            highest_row_value = row14_value
            vpoc_price = row14_price
    else:
        highest_row_value = highest_row_value[1]
    highest_row_value_avg: Series = ta.ema(highest_row_value, filter_size)
    row0_width: Series = math.floor(visual_row_width * row0_value / highest_row_value_avg[block_bar + 1])
    row1_width: Series = math.floor(visual_row_width * row1_value / highest_row_value_avg[block_bar + 1])
    row2_width: Series = math.floor(visual_row_width * row2_value / highest_row_value_avg[block_bar + 1])
    row3_width: Series = math.floor(visual_row_width * row3_value / highest_row_value_avg[block_bar + 1])
    row4_width: Series = math.floor(visual_row_width * row4_value / highest_row_value_avg[block_bar + 1])
    row5_width: Series = math.floor(visual_row_width * row5_value / highest_row_value_avg[block_bar + 1])
    row6_width: Series = math.floor(visual_row_width * row6_value / highest_row_value_avg[block_bar + 1])
    row7_width: Series = math.floor(visual_row_width * row7_value / highest_row_value_avg[block_bar + 1])
    row8_width: Series = math.floor(visual_row_width * row8_value / highest_row_value_avg[block_bar + 1])
    row9_width: Series = math.floor(visual_row_width * row9_value / highest_row_value_avg[block_bar + 1])
    row10_width: Series = math.floor(visual_row_width * row10_value / highest_row_value_avg[block_bar + 1])
    row11_width: Series = math.floor(visual_row_width * row11_value / highest_row_value_avg[block_bar + 1])
    row12_width: Series = math.floor(visual_row_width * row12_value / highest_row_value_avg[block_bar + 1])
    row13_width: Series = math.floor(visual_row_width * row13_value / highest_row_value_avg[block_bar + 1])
    row14_width: Series = math.floor(visual_row_width * row14_value / highest_row_value_avg[block_bar + 1])
    bounds_high_y = block_high[block_bar + 1] if block_bar != block_size - 1 else na
    bounds_low_y = block_low[block_bar + 1] if block_bar != block_size - 1 else na
    plot(bounds_high_y, color=color.new(BOUNARY_COLOR, 0), style=plot.style_linebr, offset=-block_size * 2, title='History block high')
    plot(bounds_low_y, color=color.new(BOUNARY_COLOR, 0), style=plot.style_linebr, offset=-block_size * 2, title='History block low')
    history1_block_bar = (block_index + 1) % 2 * block_size + block_bar
    history1_row0_price = row0_price[history1_block_bar + 1]
    history1_row0_width = math.min(28, row0_width[history1_block_bar + 1])
    history1_row0_y = history1_row0_price if history1_block_bar <= history1_row0_width else na
    history1_row1_price = row1_price[history1_block_bar + 1]
    history1_row1_width = math.min(28, row1_width[history1_block_bar + 1])
    history1_row1_y = history1_row1_price if history1_block_bar <= history1_row1_width else na
    history1_row2_price = row2_price[history1_block_bar + 1]
    history1_row2_width = math.min(28, row2_width[history1_block_bar + 1])
    history1_row2_y = history1_row2_price if history1_block_bar <= history1_row2_width else na
    history1_row3_price = row3_price[history1_block_bar + 1]
    history1_row3_width = math.min(28, row3_width[history1_block_bar + 1])
    history1_row3_y = history1_row3_price if history1_block_bar <= history1_row3_width else na
    history1_row4_price = row4_price[history1_block_bar + 1]
    history1_row4_width = math.min(28, row4_width[history1_block_bar + 1])
    history1_row4_y = history1_row4_price if history1_block_bar <= history1_row4_width else na
    history1_row5_price = row5_price[history1_block_bar + 1]
    history1_row5_width = math.min(28, row5_width[history1_block_bar + 1])
    history1_row5_y = history1_row5_price if history1_block_bar <= history1_row5_width else na
    history1_row6_price = row6_price[history1_block_bar + 1]
    history1_row6_width = math.min(28, row6_width[history1_block_bar + 1])
    history1_row6_y = history1_row6_price if history1_block_bar <= history1_row6_width else na
    history1_row7_price = row7_price[history1_block_bar + 1]
    history1_row7_width = math.min(28, row7_width[history1_block_bar + 1])
    history1_row7_y = history1_row7_price if history1_block_bar <= history1_row7_width else na
    history1_row8_price = row8_price[history1_block_bar + 1]
    history1_row8_width = math.min(28, row8_width[history1_block_bar + 1])
    history1_row8_y = history1_row8_price if history1_block_bar <= history1_row8_width else na
    history1_row9_price = row9_price[history1_block_bar + 1]
    history1_row9_width = math.min(28, row9_width[history1_block_bar + 1])
    history1_row9_y = history1_row9_price if history1_block_bar <= history1_row9_width else na
    history1_row10_price = row10_price[history1_block_bar + 1]
    history1_row10_width = math.min(28, row10_width[history1_block_bar + 1])
    history1_row10_y = history1_row10_price if history1_block_bar <= history1_row10_width else na
    history1_row11_price = row11_price[history1_block_bar + 1]
    history1_row11_width = math.min(28, row11_width[history1_block_bar + 1])
    history1_row11_y = history1_row11_price if history1_block_bar <= history1_row11_width else na
    history1_row12_price = row12_price[history1_block_bar + 1]
    history1_row12_width = math.min(28, row12_width[history1_block_bar + 1])
    history1_row12_y = history1_row12_price if history1_block_bar <= history1_row12_width else na
    history1_row13_price = row13_price[history1_block_bar + 1]
    history1_row13_width = math.min(28, row13_width[history1_block_bar + 1])
    history1_row13_y = history1_row13_price if history1_block_bar <= history1_row13_width else na
    history1_row14_price = row14_price[history1_block_bar + 1]
    history1_row14_width = math.min(28, row14_width[history1_block_bar + 1])
    history1_row14_y = history1_row14_price if history1_block_bar <= history1_row14_width else na
    plot(history1_row0_y, color=color.new(PROFILE1_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 1 row 0')
    plot(history1_row1_y, color=color.new(PROFILE1_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 1 row 1')
    plot(history1_row2_y, color=color.new(PROFILE1_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 1 row 2')
    plot(history1_row3_y, color=color.new(PROFILE1_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 1 row 3')
    plot(history1_row4_y, color=color.new(PROFILE1_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 1 row 4')
    plot(history1_row5_y, color=color.new(PROFILE1_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 1 row 5')
    plot(history1_row6_y, color=color.new(PROFILE1_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 1 row 6')
    plot(history1_row7_y, color=color.new(PROFILE1_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 1 row 7')
    plot(history1_row8_y, color=color.new(PROFILE1_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 1 row 8')
    plot(history1_row9_y, color=color.new(PROFILE1_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 1 row 9')
    plot(history1_row10_y, color=color.new(PROFILE1_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 1 row 10')
    plot(history1_row11_y, color=color.new(PROFILE1_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 1 row 11')
    plot(history1_row12_y, color=color.new(PROFILE1_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 1 row 12')
    plot(history1_row13_y, color=color.new(PROFILE1_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 1 row 13')
    plot(history1_row14_y, color=color.new(PROFILE1_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 1 row 14')
    history2_block_bar = (block_index + 2) % 2 * block_size + block_bar
    history2_row0_price = row0_price[history2_block_bar + 1]
    history2_row0_width = math.min(28, row0_width[history2_block_bar + 1])
    history2_row0_y = history2_row0_price if history2_block_bar <= history2_row0_width else na
    history2_row1_price = row1_price[history2_block_bar + 1]
    history2_row1_width = math.min(28, row1_width[history2_block_bar + 1])
    history2_row1_y = history2_row1_price if history2_block_bar <= history2_row1_width else na
    history2_row2_price = row2_price[history2_block_bar + 1]
    history2_row2_width = math.min(28, row2_width[history2_block_bar + 1])
    history2_row2_y = history2_row2_price if history2_block_bar <= history2_row2_width else na
    history2_row3_price = row3_price[history2_block_bar + 1]
    history2_row3_width = math.min(28, row3_width[history2_block_bar + 1])
    history2_row3_y = history2_row3_price if history2_block_bar <= history2_row3_width else na
    history2_row4_price = row4_price[history2_block_bar + 1]
    history2_row4_width = math.min(28, row4_width[history2_block_bar + 1])
    history2_row4_y = history2_row4_price if history2_block_bar <= history2_row4_width else na
    history2_row5_price = row5_price[history2_block_bar + 1]
    history2_row5_width = math.min(28, row5_width[history2_block_bar + 1])
    history2_row5_y = history2_row5_price if history2_block_bar <= history2_row5_width else na
    history2_row6_price = row6_price[history2_block_bar + 1]
    history2_row6_width = math.min(28, row6_width[history2_block_bar + 1])
    history2_row6_y = history2_row6_price if history2_block_bar <= history2_row6_width else na
    history2_row7_price = row7_price[history2_block_bar + 1]
    history2_row7_width = math.min(28, row7_width[history2_block_bar + 1])
    history2_row7_y = history2_row7_price if history2_block_bar <= history2_row7_width else na
    history2_row8_price = row8_price[history2_block_bar + 1]
    history2_row8_width = math.min(28, row8_width[history2_block_bar + 1])
    history2_row8_y = history2_row8_price if history2_block_bar <= history2_row8_width else na
    history2_row9_price = row9_price[history2_block_bar + 1]
    history2_row9_width = math.min(28, row9_width[history2_block_bar + 1])
    history2_row9_y = history2_row9_price if history2_block_bar <= history2_row9_width else na
    history2_row10_price = row10_price[history2_block_bar + 1]
    history2_row10_width = math.min(28, row10_width[history2_block_bar + 1])
    history2_row10_y = history2_row10_price if history2_block_bar <= history2_row10_width else na
    history2_row11_price = row11_price[history2_block_bar + 1]
    history2_row11_width = math.min(28, row11_width[history2_block_bar + 1])
    history2_row11_y = history2_row11_price if history2_block_bar <= history2_row11_width else na
    history2_row12_price = row12_price[history2_block_bar + 1]
    history2_row12_width = math.min(28, row12_width[history2_block_bar + 1])
    history2_row12_y = history2_row12_price if history2_block_bar <= history2_row12_width else na
    history2_row13_price = row13_price[history2_block_bar + 1]
    history2_row13_width = math.min(28, row13_width[history2_block_bar + 1])
    history2_row13_y = history2_row13_price if history2_block_bar <= history2_row13_width else na
    history2_row14_price = row14_price[history2_block_bar + 1]
    history2_row14_width = math.min(28, row14_width[history2_block_bar + 1])
    history2_row14_y = history2_row14_price if history2_block_bar <= history2_row14_width else na
    plot(history2_row0_y, color=color.new(PROFILE2_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 2 row 0')
    plot(history2_row1_y, color=color.new(PROFILE2_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 2 row 1')
    plot(history2_row2_y, color=color.new(PROFILE2_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 2 row 2')
    plot(history2_row3_y, color=color.new(PROFILE2_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 2 row 3')
    plot(history2_row4_y, color=color.new(PROFILE2_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 2 row 4')
    plot(history2_row5_y, color=color.new(PROFILE2_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 2 row 5')
    plot(history2_row6_y, color=color.new(PROFILE2_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 2 row 6')
    plot(history2_row7_y, color=color.new(PROFILE2_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 2 row 7')
    plot(history2_row8_y, color=color.new(PROFILE2_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 2 row 8')
    plot(history2_row9_y, color=color.new(PROFILE2_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 2 row 9')
    plot(history2_row10_y, color=color.new(PROFILE2_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 2 row 10')
    plot(history2_row11_y, color=color.new(PROFILE2_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 2 row 11')
    plot(history2_row12_y, color=color.new(PROFILE2_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 2 row 12')
    plot(history2_row13_y, color=color.new(PROFILE2_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 2 row 13')
    plot(history2_row14_y, color=color.new(PROFILE2_COLOR, 0), style=plot.style_linebr, linewidth=2, offset=-block_size * 2, title='History 2 row 14')
    vpoc_y = vpoc_price if show_vpoc else na
    plotshape(vpoc_y, title='VPoC', location=location.absolute, color=color.new(VPOC_COLOR, 0), style=shape.diamond, size=size.tiny, offset=-block_size * 2)
    recent0_high_line: Persistent[Line] = na(Line)
    recent0_low_line: Persistent[Line] = na(Line)
    recent0_vpoc_label: Persistent[Label] = na(Label)
    recent0_row0_line: Persistent[Line] = na(Line)
    recent0_row1_line: Persistent[Line] = na(Line)
    recent0_row2_line: Persistent[Line] = na(Line)
    recent0_row3_line: Persistent[Line] = na(Line)
    recent0_row4_line: Persistent[Line] = na(Line)
    recent0_row5_line: Persistent[Line] = na(Line)
    recent0_row6_line: Persistent[Line] = na(Line)
    recent0_row7_line: Persistent[Line] = na(Line)
    recent0_row8_line: Persistent[Line] = na(Line)
    recent0_row9_line: Persistent[Line] = na(Line)
    recent0_row10_line: Persistent[Line] = na(Line)
    recent0_row11_line: Persistent[Line] = na(Line)
    recent0_row12_line: Persistent[Line] = na(Line)
    recent0_row13_line: Persistent[Line] = na(Line)
    recent0_row14_line: Persistent[Line] = na(Line)
    recent1_high_line: Persistent[Line] = na(Line)
    recent1_low_line: Persistent[Line] = na(Line)
    recent1_vpoc_label: Persistent[Label] = na(Label)
    recent1_row0_line: Persistent[Line] = na(Line)
    recent1_row1_line: Persistent[Line] = na(Line)
    recent1_row2_line: Persistent[Line] = na(Line)
    recent1_row3_line: Persistent[Line] = na(Line)
    recent1_row4_line: Persistent[Line] = na(Line)
    recent1_row5_line: Persistent[Line] = na(Line)
    recent1_row6_line: Persistent[Line] = na(Line)
    recent1_row7_line: Persistent[Line] = na(Line)
    recent1_row8_line: Persistent[Line] = na(Line)
    recent1_row9_line: Persistent[Line] = na(Line)
    recent1_row10_line: Persistent[Line] = na(Line)
    recent1_row11_line: Persistent[Line] = na(Line)
    recent1_row12_line: Persistent[Line] = na(Line)
    recent1_row13_line: Persistent[Line] = na(Line)
    recent1_row14_line: Persistent[Line] = na(Line)
    recent2_high_line: Persistent[Line] = na(Line)
    recent2_low_line: Persistent[Line] = na(Line)
    recent2_row0_line: Persistent[Line] = na(Line)
    recent2_row1_line: Persistent[Line] = na(Line)
    recent2_row2_line: Persistent[Line] = na(Line)
    recent2_row3_line: Persistent[Line] = na(Line)
    recent2_row4_line: Persistent[Line] = na(Line)
    recent2_row5_line: Persistent[Line] = na(Line)
    recent2_row6_line: Persistent[Line] = na(Line)
    recent2_row7_line: Persistent[Line] = na(Line)
    recent2_row8_line: Persistent[Line] = na(Line)
    recent2_row9_line: Persistent[Line] = na(Line)
    recent2_row10_line: Persistent[Line] = na(Line)
    recent2_row11_line: Persistent[Line] = na(Line)
    recent2_row12_line: Persistent[Line] = na(Line)
    recent2_row13_line: Persistent[Line] = na(Line)
    recent2_row14_line: Persistent[Line] = na(Line)
    if barstate.islast:
        recent0_start_i = block_size * 0 + block_bar
        recent0_end_i = math.max(block_size * 0 - (block_size - block_bar) + 1, 0)
        recent0_color_n = (block_index[recent0_end_i] + 3) % 2
        __block_result__ = na
        if recent0_color_n == 0:
            __block_result__ = color.purple
        elif recent0_color_n == 1:
            __block_result__ = color.teal
        recent0_color = __block_result__
        if not na(time[recent0_start_i]) and recent0_start_i - recent0_end_i > 5:
            if na(recent0_low_line):
                recent0_low_line = line.new(bar_index, high, bar_index, high, color=BOUNARY_COLOR)
            if na(recent0_high_line):
                recent0_high_line = line.new(bar_index, low, bar_index, low, color=BOUNARY_COLOR)
            recent0_block_high = rolling_high[recent0_end_i]
            recent0_block_low = rolling_low[recent0_end_i]
            line.set_xloc(recent0_low_line, time[recent0_start_i], time[recent0_end_i], xloc.bar_time)
            line.set_y1(recent0_low_line, recent0_block_low)
            line.set_y2(recent0_low_line, recent0_block_low)
            line.set_xloc(recent0_high_line, time[recent0_start_i], time[recent0_end_i], xloc.bar_time)
            line.set_y1(recent0_high_line, recent0_block_high)
            line.set_y2(recent0_high_line, recent0_block_high)
            recent0_block_height = recent0_block_high - recent0_block_low
            recent0_row_height = recent0_block_height / 15
            recent0_row0_low = recent0_block_low + recent0_row_height * 0
            recent0_row0_high = recent0_block_low + recent0_row_height * 1
            recent0_row0_value: float = 0.0
            recent0_row1_low = recent0_block_low + recent0_row_height * 1
            recent0_row1_high = recent0_block_low + recent0_row_height * 2
            recent0_row1_value: float = 0.0
            recent0_row2_low = recent0_block_low + recent0_row_height * 2
            recent0_row2_high = recent0_block_low + recent0_row_height * 3
            recent0_row2_value: float = 0.0
            recent0_row3_low = recent0_block_low + recent0_row_height * 3
            recent0_row3_high = recent0_block_low + recent0_row_height * 4
            recent0_row3_value: float = 0.0
            recent0_row4_low = recent0_block_low + recent0_row_height * 4
            recent0_row4_high = recent0_block_low + recent0_row_height * 5
            recent0_row4_value: float = 0.0
            recent0_row5_low = recent0_block_low + recent0_row_height * 5
            recent0_row5_high = recent0_block_low + recent0_row_height * 6
            recent0_row5_value: float = 0.0
            recent0_row6_low = recent0_block_low + recent0_row_height * 6
            recent0_row6_high = recent0_block_low + recent0_row_height * 7
            recent0_row6_value: float = 0.0
            recent0_row7_low = recent0_block_low + recent0_row_height * 7
            recent0_row7_high = recent0_block_low + recent0_row_height * 8
            recent0_row7_value: float = 0.0
            recent0_row8_low = recent0_block_low + recent0_row_height * 8
            recent0_row8_high = recent0_block_low + recent0_row_height * 9
            recent0_row8_value: float = 0.0
            recent0_row9_low = recent0_block_low + recent0_row_height * 9
            recent0_row9_high = recent0_block_low + recent0_row_height * 10
            recent0_row9_value: float = 0.0
            recent0_row10_low = recent0_block_low + recent0_row_height * 10
            recent0_row10_high = recent0_block_low + recent0_row_height * 11
            recent0_row10_value: float = 0.0
            recent0_row11_low = recent0_block_low + recent0_row_height * 11
            recent0_row11_high = recent0_block_low + recent0_row_height * 12
            recent0_row11_value: float = 0.0
            recent0_row12_low = recent0_block_low + recent0_row_height * 12
            recent0_row12_high = recent0_block_low + recent0_row_height * 13
            recent0_row12_value: float = 0.0
            recent0_row13_low = recent0_block_low + recent0_row_height * 13
            recent0_row13_high = recent0_block_low + recent0_row_height * 14
            recent0_row13_value: float = 0.0
            recent0_row14_low = recent0_block_low + recent0_row_height * 14
            recent0_row14_high = recent0_block_low + recent0_row_height * 15
            recent0_row14_value: float = 0.0
            for i in pine_range(recent0_start_i, recent0_end_i + 1, 1):
                bar_n_rows_affected: int = 0
                bar_row0_value: float = 0.0
                if low[i] < recent0_row0_high and high[i] > recent0_row0_low:
                    bar_row0_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row1_value: float = 0.0
                if low[i] < recent0_row1_high and high[i] > recent0_row1_low:
                    bar_row1_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row2_value: float = 0.0
                if low[i] < recent0_row2_high and high[i] > recent0_row2_low:
                    bar_row2_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row3_value: float = 0.0
                if low[i] < recent0_row3_high and high[i] > recent0_row3_low:
                    bar_row3_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row4_value: float = 0.0
                if low[i] < recent0_row4_high and high[i] > recent0_row4_low:
                    bar_row4_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row5_value: float = 0.0
                if low[i] < recent0_row5_high and high[i] > recent0_row5_low:
                    bar_row5_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row6_value: float = 0.0
                if low[i] < recent0_row6_high and high[i] > recent0_row6_low:
                    bar_row6_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row7_value: float = 0.0
                if low[i] < recent0_row7_high and high[i] > recent0_row7_low:
                    bar_row7_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row8_value: float = 0.0
                if low[i] < recent0_row8_high and high[i] > recent0_row8_low:
                    bar_row8_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row9_value: float = 0.0
                if low[i] < recent0_row9_high and high[i] > recent0_row9_low:
                    bar_row9_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row10_value: float = 0.0
                if low[i] < recent0_row10_high and high[i] > recent0_row10_low:
                    bar_row10_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row11_value: float = 0.0
                if low[i] < recent0_row11_high and high[i] > recent0_row11_low:
                    bar_row11_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row12_value: float = 0.0
                if low[i] < recent0_row12_high and high[i] > recent0_row12_low:
                    bar_row12_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row13_value: float = 0.0
                if low[i] < recent0_row13_high and high[i] > recent0_row13_low:
                    bar_row13_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row14_value: float = 0.0
                if low[i] < recent0_row14_high and high[i] > recent0_row14_low:
                    bar_row14_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                recent0_row0_value = recent0_row0_value + bar_row0_value / bar_n_rows_affected / recent0_row_height
                recent0_row1_value = recent0_row1_value + bar_row1_value / bar_n_rows_affected / recent0_row_height
                recent0_row2_value = recent0_row2_value + bar_row2_value / bar_n_rows_affected / recent0_row_height
                recent0_row3_value = recent0_row3_value + bar_row3_value / bar_n_rows_affected / recent0_row_height
                recent0_row4_value = recent0_row4_value + bar_row4_value / bar_n_rows_affected / recent0_row_height
                recent0_row5_value = recent0_row5_value + bar_row5_value / bar_n_rows_affected / recent0_row_height
                recent0_row6_value = recent0_row6_value + bar_row6_value / bar_n_rows_affected / recent0_row_height
                recent0_row7_value = recent0_row7_value + bar_row7_value / bar_n_rows_affected / recent0_row_height
                recent0_row8_value = recent0_row8_value + bar_row8_value / bar_n_rows_affected / recent0_row_height
                recent0_row9_value = recent0_row9_value + bar_row9_value / bar_n_rows_affected / recent0_row_height
                recent0_row10_value = recent0_row10_value + bar_row10_value / bar_n_rows_affected / recent0_row_height
                recent0_row11_value = recent0_row11_value + bar_row11_value / bar_n_rows_affected / recent0_row_height
                recent0_row12_value = recent0_row12_value + bar_row12_value / bar_n_rows_affected / recent0_row_height
                recent0_row13_value = recent0_row13_value + bar_row13_value / bar_n_rows_affected / recent0_row_height
                recent0_row14_value = recent0_row14_value + bar_row14_value / bar_n_rows_affected / recent0_row_height
            recent0_avg_i = math.min(recent0_start_i + 1 + block_size * 2, bar_index)
            recent0_row0_price = (recent0_row0_low + recent0_row0_high) / 2
            recent0_row0_width = math.floor(visual_row_width * recent0_row0_value / highest_row_value_avg[recent0_avg_i])
            recent0_row1_price = (recent0_row1_low + recent0_row1_high) / 2
            recent0_row1_width = math.floor(visual_row_width * recent0_row1_value / highest_row_value_avg[recent0_avg_i])
            recent0_row2_price = (recent0_row2_low + recent0_row2_high) / 2
            recent0_row2_width = math.floor(visual_row_width * recent0_row2_value / highest_row_value_avg[recent0_avg_i])
            recent0_row3_price = (recent0_row3_low + recent0_row3_high) / 2
            recent0_row3_width = math.floor(visual_row_width * recent0_row3_value / highest_row_value_avg[recent0_avg_i])
            recent0_row4_price = (recent0_row4_low + recent0_row4_high) / 2
            recent0_row4_width = math.floor(visual_row_width * recent0_row4_value / highest_row_value_avg[recent0_avg_i])
            recent0_row5_price = (recent0_row5_low + recent0_row5_high) / 2
            recent0_row5_width = math.floor(visual_row_width * recent0_row5_value / highest_row_value_avg[recent0_avg_i])
            recent0_row6_price = (recent0_row6_low + recent0_row6_high) / 2
            recent0_row6_width = math.floor(visual_row_width * recent0_row6_value / highest_row_value_avg[recent0_avg_i])
            recent0_row7_price = (recent0_row7_low + recent0_row7_high) / 2
            recent0_row7_width = math.floor(visual_row_width * recent0_row7_value / highest_row_value_avg[recent0_avg_i])
            recent0_row8_price = (recent0_row8_low + recent0_row8_high) / 2
            recent0_row8_width = math.floor(visual_row_width * recent0_row8_value / highest_row_value_avg[recent0_avg_i])
            recent0_row9_price = (recent0_row9_low + recent0_row9_high) / 2
            recent0_row9_width = math.floor(visual_row_width * recent0_row9_value / highest_row_value_avg[recent0_avg_i])
            recent0_row10_price = (recent0_row10_low + recent0_row10_high) / 2
            recent0_row10_width = math.floor(visual_row_width * recent0_row10_value / highest_row_value_avg[recent0_avg_i])
            recent0_row11_price = (recent0_row11_low + recent0_row11_high) / 2
            recent0_row11_width = math.floor(visual_row_width * recent0_row11_value / highest_row_value_avg[recent0_avg_i])
            recent0_row12_price = (recent0_row12_low + recent0_row12_high) / 2
            recent0_row12_width = math.floor(visual_row_width * recent0_row12_value / highest_row_value_avg[recent0_avg_i])
            recent0_row13_price = (recent0_row13_low + recent0_row13_high) / 2
            recent0_row13_width = math.floor(visual_row_width * recent0_row13_value / highest_row_value_avg[recent0_avg_i])
            recent0_row14_price = (recent0_row14_low + recent0_row14_high) / 2
            recent0_row14_width = math.floor(visual_row_width * recent0_row14_value / highest_row_value_avg[recent0_avg_i])
            recent0_vpoc_price: float = na(float)
            recent0_highes_row_value: float = 0
            if recent0_highes_row_value < recent0_row0_value:
                recent0_highes_row_value = recent0_row0_value
                recent0_vpoc_price = recent0_row0_price
            if recent0_highes_row_value < recent0_row1_value:
                recent0_highes_row_value = recent0_row1_value
                recent0_vpoc_price = recent0_row1_price
            if recent0_highes_row_value < recent0_row2_value:
                recent0_highes_row_value = recent0_row2_value
                recent0_vpoc_price = recent0_row2_price
            if recent0_highes_row_value < recent0_row3_value:
                recent0_highes_row_value = recent0_row3_value
                recent0_vpoc_price = recent0_row3_price
            if recent0_highes_row_value < recent0_row4_value:
                recent0_highes_row_value = recent0_row4_value
                recent0_vpoc_price = recent0_row4_price
            if recent0_highes_row_value < recent0_row5_value:
                recent0_highes_row_value = recent0_row5_value
                recent0_vpoc_price = recent0_row5_price
            if recent0_highes_row_value < recent0_row6_value:
                recent0_highes_row_value = recent0_row6_value
                recent0_vpoc_price = recent0_row6_price
            if recent0_highes_row_value < recent0_row7_value:
                recent0_highes_row_value = recent0_row7_value
                recent0_vpoc_price = recent0_row7_price
            if recent0_highes_row_value < recent0_row8_value:
                recent0_highes_row_value = recent0_row8_value
                recent0_vpoc_price = recent0_row8_price
            if recent0_highes_row_value < recent0_row9_value:
                recent0_highes_row_value = recent0_row9_value
                recent0_vpoc_price = recent0_row9_price
            if recent0_highes_row_value < recent0_row10_value:
                recent0_highes_row_value = recent0_row10_value
                recent0_vpoc_price = recent0_row10_price
            if recent0_highes_row_value < recent0_row11_value:
                recent0_highes_row_value = recent0_row11_value
                recent0_vpoc_price = recent0_row11_price
            if recent0_highes_row_value < recent0_row12_value:
                recent0_highes_row_value = recent0_row12_value
                recent0_vpoc_price = recent0_row12_price
            if recent0_highes_row_value < recent0_row13_value:
                recent0_highes_row_value = recent0_row13_value
                recent0_vpoc_price = recent0_row13_price
            if recent0_highes_row_value < recent0_row14_value:
                recent0_highes_row_value = recent0_row14_value
                recent0_vpoc_price = recent0_row14_price
            if na(recent0_row0_line):
                recent0_row0_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent0_row1_line):
                recent0_row1_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent0_row2_line):
                recent0_row2_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent0_row3_line):
                recent0_row3_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent0_row4_line):
                recent0_row4_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent0_row5_line):
                recent0_row5_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent0_row6_line):
                recent0_row6_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent0_row7_line):
                recent0_row7_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent0_row8_line):
                recent0_row8_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent0_row9_line):
                recent0_row9_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent0_row10_line):
                recent0_row10_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent0_row11_line):
                recent0_row11_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent0_row12_line):
                recent0_row12_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent0_row13_line):
                recent0_row13_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent0_row14_line):
                recent0_row14_line = line.new(bar_index, close, bar_index, close, width=2)
            line.set_xloc(recent0_row0_line, time[recent0_start_i], time_close[math.max(recent0_start_i - recent0_row0_width, 0)], xloc.bar_time)
            line.set_y1(recent0_row0_line, recent0_row0_price)
            line.set_y2(recent0_row0_line, recent0_row0_price)
            line.set_color(recent0_row0_line, recent0_color)
            line.set_xloc(recent0_row1_line, time[recent0_start_i], time_close[math.max(recent0_start_i - recent0_row1_width, 0)], xloc.bar_time)
            line.set_y1(recent0_row1_line, recent0_row1_price)
            line.set_y2(recent0_row1_line, recent0_row1_price)
            line.set_color(recent0_row1_line, recent0_color)
            line.set_xloc(recent0_row2_line, time[recent0_start_i], time_close[math.max(recent0_start_i - recent0_row2_width, 0)], xloc.bar_time)
            line.set_y1(recent0_row2_line, recent0_row2_price)
            line.set_y2(recent0_row2_line, recent0_row2_price)
            line.set_color(recent0_row2_line, recent0_color)
            line.set_xloc(recent0_row3_line, time[recent0_start_i], time_close[math.max(recent0_start_i - recent0_row3_width, 0)], xloc.bar_time)
            line.set_y1(recent0_row3_line, recent0_row3_price)
            line.set_y2(recent0_row3_line, recent0_row3_price)
            line.set_color(recent0_row3_line, recent0_color)
            line.set_xloc(recent0_row4_line, time[recent0_start_i], time_close[math.max(recent0_start_i - recent0_row4_width, 0)], xloc.bar_time)
            line.set_y1(recent0_row4_line, recent0_row4_price)
            line.set_y2(recent0_row4_line, recent0_row4_price)
            line.set_color(recent0_row4_line, recent0_color)
            line.set_xloc(recent0_row5_line, time[recent0_start_i], time_close[math.max(recent0_start_i - recent0_row5_width, 0)], xloc.bar_time)
            line.set_y1(recent0_row5_line, recent0_row5_price)
            line.set_y2(recent0_row5_line, recent0_row5_price)
            line.set_color(recent0_row5_line, recent0_color)
            line.set_xloc(recent0_row6_line, time[recent0_start_i], time_close[math.max(recent0_start_i - recent0_row6_width, 0)], xloc.bar_time)
            line.set_y1(recent0_row6_line, recent0_row6_price)
            line.set_y2(recent0_row6_line, recent0_row6_price)
            line.set_color(recent0_row6_line, recent0_color)
            line.set_xloc(recent0_row7_line, time[recent0_start_i], time_close[math.max(recent0_start_i - recent0_row7_width, 0)], xloc.bar_time)
            line.set_y1(recent0_row7_line, recent0_row7_price)
            line.set_y2(recent0_row7_line, recent0_row7_price)
            line.set_color(recent0_row7_line, recent0_color)
            line.set_xloc(recent0_row8_line, time[recent0_start_i], time_close[math.max(recent0_start_i - recent0_row8_width, 0)], xloc.bar_time)
            line.set_y1(recent0_row8_line, recent0_row8_price)
            line.set_y2(recent0_row8_line, recent0_row8_price)
            line.set_color(recent0_row8_line, recent0_color)
            line.set_xloc(recent0_row9_line, time[recent0_start_i], time_close[math.max(recent0_start_i - recent0_row9_width, 0)], xloc.bar_time)
            line.set_y1(recent0_row9_line, recent0_row9_price)
            line.set_y2(recent0_row9_line, recent0_row9_price)
            line.set_color(recent0_row9_line, recent0_color)
            line.set_xloc(recent0_row10_line, time[recent0_start_i], time_close[math.max(recent0_start_i - recent0_row10_width, 0)], xloc.bar_time)
            line.set_y1(recent0_row10_line, recent0_row10_price)
            line.set_y2(recent0_row10_line, recent0_row10_price)
            line.set_color(recent0_row10_line, recent0_color)
            line.set_xloc(recent0_row11_line, time[recent0_start_i], time_close[math.max(recent0_start_i - recent0_row11_width, 0)], xloc.bar_time)
            line.set_y1(recent0_row11_line, recent0_row11_price)
            line.set_y2(recent0_row11_line, recent0_row11_price)
            line.set_color(recent0_row11_line, recent0_color)
            line.set_xloc(recent0_row12_line, time[recent0_start_i], time_close[math.max(recent0_start_i - recent0_row12_width, 0)], xloc.bar_time)
            line.set_y1(recent0_row12_line, recent0_row12_price)
            line.set_y2(recent0_row12_line, recent0_row12_price)
            line.set_color(recent0_row12_line, recent0_color)
            line.set_xloc(recent0_row13_line, time[recent0_start_i], time_close[math.max(recent0_start_i - recent0_row13_width, 0)], xloc.bar_time)
            line.set_y1(recent0_row13_line, recent0_row13_price)
            line.set_y2(recent0_row13_line, recent0_row13_price)
            line.set_color(recent0_row13_line, recent0_color)
            line.set_xloc(recent0_row14_line, time[recent0_start_i], time_close[math.max(recent0_start_i - recent0_row14_width, 0)], xloc.bar_time)
            line.set_y1(recent0_row14_line, recent0_row14_price)
            line.set_y2(recent0_row14_line, recent0_row14_price)
            line.set_color(recent0_row14_line, recent0_color)
            if show_vpoc:
                if na(recent0_vpoc_label):
                    recent0_vpoc_label = label.new(bar_index, close, yloc=yloc.price, style=label.style_diamond, size=size.tiny, color=VPOC_COLOR)
                label.set_xloc(recent0_vpoc_label, time[recent0_start_i + 1], xloc.bar_time)
                label.set_y(recent0_vpoc_label, recent0_vpoc_price)
            if not show_vpoc and (not na(recent0_vpoc_label)):
                label.delete(recent0_vpoc_label)
                recent0_vpoc_label = na
        else:
            if not na(recent0_low_line):
                line.delete(recent0_low_line)
                recent0_low_line = na
            if not na(recent0_high_line):
                line.delete(recent0_high_line)
                recent0_high_line = na
            if not na(recent0_vpoc_label):
                label.delete(recent0_vpoc_label)
                recent0_vpoc_label = na
            if not na(recent0_row0_line):
                line.delete(recent0_row0_line)
                recent0_row0_line = na
            if not na(recent0_row1_line):
                line.delete(recent0_row1_line)
                recent0_row1_line = na
            if not na(recent0_row2_line):
                line.delete(recent0_row2_line)
                recent0_row2_line = na
            if not na(recent0_row3_line):
                line.delete(recent0_row3_line)
                recent0_row3_line = na
            if not na(recent0_row4_line):
                line.delete(recent0_row4_line)
                recent0_row4_line = na
            if not na(recent0_row5_line):
                line.delete(recent0_row5_line)
                recent0_row5_line = na
            if not na(recent0_row6_line):
                line.delete(recent0_row6_line)
                recent0_row6_line = na
            if not na(recent0_row7_line):
                line.delete(recent0_row7_line)
                recent0_row7_line = na
            if not na(recent0_row8_line):
                line.delete(recent0_row8_line)
                recent0_row8_line = na
            if not na(recent0_row9_line):
                line.delete(recent0_row9_line)
                recent0_row9_line = na
            if not na(recent0_row10_line):
                line.delete(recent0_row10_line)
                recent0_row10_line = na
            if not na(recent0_row11_line):
                line.delete(recent0_row11_line)
                recent0_row11_line = na
            if not na(recent0_row12_line):
                line.delete(recent0_row12_line)
                recent0_row12_line = na
            if not na(recent0_row13_line):
                line.delete(recent0_row13_line)
                recent0_row13_line = na
            if not na(recent0_row14_line):
                line.delete(recent0_row14_line)
                recent0_row14_line = na
        recent1_start_i = block_size * 1 + block_bar
        recent1_end_i = math.max(block_size * 1 - (block_size - block_bar) + 1, 0)
        recent1_color_n = (block_index[recent1_end_i] + 3) % 2
        __block_result_1__ = na
        if recent1_color_n == 0:
            __block_result_1__ = color.purple
        elif recent1_color_n == 1:
            __block_result_1__ = color.teal
        recent1_color = __block_result_1__
        if not na(time[recent1_start_i]) and recent1_start_i - recent1_end_i > 5:
            if na(recent1_low_line):
                recent1_low_line = line.new(bar_index, high, bar_index, high, color=BOUNARY_COLOR)
            if na(recent1_high_line):
                recent1_high_line = line.new(bar_index, low, bar_index, low, color=BOUNARY_COLOR)
            recent1_block_high = rolling_high[recent1_end_i]
            recent1_block_low = rolling_low[recent1_end_i]
            line.set_xloc(recent1_low_line, time[recent1_start_i], time[recent1_end_i], xloc.bar_time)
            line.set_y1(recent1_low_line, recent1_block_low)
            line.set_y2(recent1_low_line, recent1_block_low)
            line.set_xloc(recent1_high_line, time[recent1_start_i], time[recent1_end_i], xloc.bar_time)
            line.set_y1(recent1_high_line, recent1_block_high)
            line.set_y2(recent1_high_line, recent1_block_high)
            recent1_block_height = recent1_block_high - recent1_block_low
            recent1_row_height = recent1_block_height / 15
            recent1_row0_low = recent1_block_low + recent1_row_height * 0
            recent1_row0_high = recent1_block_low + recent1_row_height * 1
            recent1_row0_value: float = 0.0
            recent1_row1_low = recent1_block_low + recent1_row_height * 1
            recent1_row1_high = recent1_block_low + recent1_row_height * 2
            recent1_row1_value: float = 0.0
            recent1_row2_low = recent1_block_low + recent1_row_height * 2
            recent1_row2_high = recent1_block_low + recent1_row_height * 3
            recent1_row2_value: float = 0.0
            recent1_row3_low = recent1_block_low + recent1_row_height * 3
            recent1_row3_high = recent1_block_low + recent1_row_height * 4
            recent1_row3_value: float = 0.0
            recent1_row4_low = recent1_block_low + recent1_row_height * 4
            recent1_row4_high = recent1_block_low + recent1_row_height * 5
            recent1_row4_value: float = 0.0
            recent1_row5_low = recent1_block_low + recent1_row_height * 5
            recent1_row5_high = recent1_block_low + recent1_row_height * 6
            recent1_row5_value: float = 0.0
            recent1_row6_low = recent1_block_low + recent1_row_height * 6
            recent1_row6_high = recent1_block_low + recent1_row_height * 7
            recent1_row6_value: float = 0.0
            recent1_row7_low = recent1_block_low + recent1_row_height * 7
            recent1_row7_high = recent1_block_low + recent1_row_height * 8
            recent1_row7_value: float = 0.0
            recent1_row8_low = recent1_block_low + recent1_row_height * 8
            recent1_row8_high = recent1_block_low + recent1_row_height * 9
            recent1_row8_value: float = 0.0
            recent1_row9_low = recent1_block_low + recent1_row_height * 9
            recent1_row9_high = recent1_block_low + recent1_row_height * 10
            recent1_row9_value: float = 0.0
            recent1_row10_low = recent1_block_low + recent1_row_height * 10
            recent1_row10_high = recent1_block_low + recent1_row_height * 11
            recent1_row10_value: float = 0.0
            recent1_row11_low = recent1_block_low + recent1_row_height * 11
            recent1_row11_high = recent1_block_low + recent1_row_height * 12
            recent1_row11_value: float = 0.0
            recent1_row12_low = recent1_block_low + recent1_row_height * 12
            recent1_row12_high = recent1_block_low + recent1_row_height * 13
            recent1_row12_value: float = 0.0
            recent1_row13_low = recent1_block_low + recent1_row_height * 13
            recent1_row13_high = recent1_block_low + recent1_row_height * 14
            recent1_row13_value: float = 0.0
            recent1_row14_low = recent1_block_low + recent1_row_height * 14
            recent1_row14_high = recent1_block_low + recent1_row_height * 15
            recent1_row14_value: float = 0.0
            for i in pine_range(recent1_start_i, recent1_end_i + 1, 1):
                bar_n_rows_affected: int = 0
                bar_row0_value: float = 0.0
                if low[i] < recent1_row0_high and high[i] > recent1_row0_low:
                    bar_row0_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row1_value: float = 0.0
                if low[i] < recent1_row1_high and high[i] > recent1_row1_low:
                    bar_row1_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row2_value: float = 0.0
                if low[i] < recent1_row2_high and high[i] > recent1_row2_low:
                    bar_row2_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row3_value: float = 0.0
                if low[i] < recent1_row3_high and high[i] > recent1_row3_low:
                    bar_row3_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row4_value: float = 0.0
                if low[i] < recent1_row4_high and high[i] > recent1_row4_low:
                    bar_row4_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row5_value: float = 0.0
                if low[i] < recent1_row5_high and high[i] > recent1_row5_low:
                    bar_row5_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row6_value: float = 0.0
                if low[i] < recent1_row6_high and high[i] > recent1_row6_low:
                    bar_row6_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row7_value: float = 0.0
                if low[i] < recent1_row7_high and high[i] > recent1_row7_low:
                    bar_row7_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row8_value: float = 0.0
                if low[i] < recent1_row8_high and high[i] > recent1_row8_low:
                    bar_row8_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row9_value: float = 0.0
                if low[i] < recent1_row9_high and high[i] > recent1_row9_low:
                    bar_row9_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row10_value: float = 0.0
                if low[i] < recent1_row10_high and high[i] > recent1_row10_low:
                    bar_row10_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row11_value: float = 0.0
                if low[i] < recent1_row11_high and high[i] > recent1_row11_low:
                    bar_row11_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row12_value: float = 0.0
                if low[i] < recent1_row12_high and high[i] > recent1_row12_low:
                    bar_row12_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row13_value: float = 0.0
                if low[i] < recent1_row13_high and high[i] > recent1_row13_low:
                    bar_row13_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row14_value: float = 0.0
                if low[i] < recent1_row14_high and high[i] > recent1_row14_low:
                    bar_row14_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                recent1_row0_value = recent1_row0_value + bar_row0_value / bar_n_rows_affected / recent1_row_height
                recent1_row1_value = recent1_row1_value + bar_row1_value / bar_n_rows_affected / recent1_row_height
                recent1_row2_value = recent1_row2_value + bar_row2_value / bar_n_rows_affected / recent1_row_height
                recent1_row3_value = recent1_row3_value + bar_row3_value / bar_n_rows_affected / recent1_row_height
                recent1_row4_value = recent1_row4_value + bar_row4_value / bar_n_rows_affected / recent1_row_height
                recent1_row5_value = recent1_row5_value + bar_row5_value / bar_n_rows_affected / recent1_row_height
                recent1_row6_value = recent1_row6_value + bar_row6_value / bar_n_rows_affected / recent1_row_height
                recent1_row7_value = recent1_row7_value + bar_row7_value / bar_n_rows_affected / recent1_row_height
                recent1_row8_value = recent1_row8_value + bar_row8_value / bar_n_rows_affected / recent1_row_height
                recent1_row9_value = recent1_row9_value + bar_row9_value / bar_n_rows_affected / recent1_row_height
                recent1_row10_value = recent1_row10_value + bar_row10_value / bar_n_rows_affected / recent1_row_height
                recent1_row11_value = recent1_row11_value + bar_row11_value / bar_n_rows_affected / recent1_row_height
                recent1_row12_value = recent1_row12_value + bar_row12_value / bar_n_rows_affected / recent1_row_height
                recent1_row13_value = recent1_row13_value + bar_row13_value / bar_n_rows_affected / recent1_row_height
                recent1_row14_value = recent1_row14_value + bar_row14_value / bar_n_rows_affected / recent1_row_height
            recent1_avg_i = math.min(recent1_start_i + 1 + block_size * 3, bar_index)
            recent1_row0_price = (recent1_row0_low + recent1_row0_high) / 2
            recent1_row0_width = math.floor(visual_row_width * recent1_row0_value / highest_row_value_avg[recent1_avg_i])
            recent1_row1_price = (recent1_row1_low + recent1_row1_high) / 2
            recent1_row1_width = math.floor(visual_row_width * recent1_row1_value / highest_row_value_avg[recent1_avg_i])
            recent1_row2_price = (recent1_row2_low + recent1_row2_high) / 2
            recent1_row2_width = math.floor(visual_row_width * recent1_row2_value / highest_row_value_avg[recent1_avg_i])
            recent1_row3_price = (recent1_row3_low + recent1_row3_high) / 2
            recent1_row3_width = math.floor(visual_row_width * recent1_row3_value / highest_row_value_avg[recent1_avg_i])
            recent1_row4_price = (recent1_row4_low + recent1_row4_high) / 2
            recent1_row4_width = math.floor(visual_row_width * recent1_row4_value / highest_row_value_avg[recent1_avg_i])
            recent1_row5_price = (recent1_row5_low + recent1_row5_high) / 2
            recent1_row5_width = math.floor(visual_row_width * recent1_row5_value / highest_row_value_avg[recent1_avg_i])
            recent1_row6_price = (recent1_row6_low + recent1_row6_high) / 2
            recent1_row6_width = math.floor(visual_row_width * recent1_row6_value / highest_row_value_avg[recent1_avg_i])
            recent1_row7_price = (recent1_row7_low + recent1_row7_high) / 2
            recent1_row7_width = math.floor(visual_row_width * recent1_row7_value / highest_row_value_avg[recent1_avg_i])
            recent1_row8_price = (recent1_row8_low + recent1_row8_high) / 2
            recent1_row8_width = math.floor(visual_row_width * recent1_row8_value / highest_row_value_avg[recent1_avg_i])
            recent1_row9_price = (recent1_row9_low + recent1_row9_high) / 2
            recent1_row9_width = math.floor(visual_row_width * recent1_row9_value / highest_row_value_avg[recent1_avg_i])
            recent1_row10_price = (recent1_row10_low + recent1_row10_high) / 2
            recent1_row10_width = math.floor(visual_row_width * recent1_row10_value / highest_row_value_avg[recent1_avg_i])
            recent1_row11_price = (recent1_row11_low + recent1_row11_high) / 2
            recent1_row11_width = math.floor(visual_row_width * recent1_row11_value / highest_row_value_avg[recent1_avg_i])
            recent1_row12_price = (recent1_row12_low + recent1_row12_high) / 2
            recent1_row12_width = math.floor(visual_row_width * recent1_row12_value / highest_row_value_avg[recent1_avg_i])
            recent1_row13_price = (recent1_row13_low + recent1_row13_high) / 2
            recent1_row13_width = math.floor(visual_row_width * recent1_row13_value / highest_row_value_avg[recent1_avg_i])
            recent1_row14_price = (recent1_row14_low + recent1_row14_high) / 2
            recent1_row14_width = math.floor(visual_row_width * recent1_row14_value / highest_row_value_avg[recent1_avg_i])
            recent1_vpoc_price: float = na(float)
            recent1_highes_row_value: float = 0
            if recent1_highes_row_value < recent1_row0_value:
                recent1_highes_row_value = recent1_row0_value
                recent1_vpoc_price = recent1_row0_price
            if recent1_highes_row_value < recent1_row1_value:
                recent1_highes_row_value = recent1_row1_value
                recent1_vpoc_price = recent1_row1_price
            if recent1_highes_row_value < recent1_row2_value:
                recent1_highes_row_value = recent1_row2_value
                recent1_vpoc_price = recent1_row2_price
            if recent1_highes_row_value < recent1_row3_value:
                recent1_highes_row_value = recent1_row3_value
                recent1_vpoc_price = recent1_row3_price
            if recent1_highes_row_value < recent1_row4_value:
                recent1_highes_row_value = recent1_row4_value
                recent1_vpoc_price = recent1_row4_price
            if recent1_highes_row_value < recent1_row5_value:
                recent1_highes_row_value = recent1_row5_value
                recent1_vpoc_price = recent1_row5_price
            if recent1_highes_row_value < recent1_row6_value:
                recent1_highes_row_value = recent1_row6_value
                recent1_vpoc_price = recent1_row6_price
            if recent1_highes_row_value < recent1_row7_value:
                recent1_highes_row_value = recent1_row7_value
                recent1_vpoc_price = recent1_row7_price
            if recent1_highes_row_value < recent1_row8_value:
                recent1_highes_row_value = recent1_row8_value
                recent1_vpoc_price = recent1_row8_price
            if recent1_highes_row_value < recent1_row9_value:
                recent1_highes_row_value = recent1_row9_value
                recent1_vpoc_price = recent1_row9_price
            if recent1_highes_row_value < recent1_row10_value:
                recent1_highes_row_value = recent1_row10_value
                recent1_vpoc_price = recent1_row10_price
            if recent1_highes_row_value < recent1_row11_value:
                recent1_highes_row_value = recent1_row11_value
                recent1_vpoc_price = recent1_row11_price
            if recent1_highes_row_value < recent1_row12_value:
                recent1_highes_row_value = recent1_row12_value
                recent1_vpoc_price = recent1_row12_price
            if recent1_highes_row_value < recent1_row13_value:
                recent1_highes_row_value = recent1_row13_value
                recent1_vpoc_price = recent1_row13_price
            if recent1_highes_row_value < recent1_row14_value:
                recent1_highes_row_value = recent1_row14_value
                recent1_vpoc_price = recent1_row14_price
            if na(recent1_row0_line):
                recent1_row0_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent1_row1_line):
                recent1_row1_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent1_row2_line):
                recent1_row2_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent1_row3_line):
                recent1_row3_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent1_row4_line):
                recent1_row4_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent1_row5_line):
                recent1_row5_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent1_row6_line):
                recent1_row6_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent1_row7_line):
                recent1_row7_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent1_row8_line):
                recent1_row8_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent1_row9_line):
                recent1_row9_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent1_row10_line):
                recent1_row10_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent1_row11_line):
                recent1_row11_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent1_row12_line):
                recent1_row12_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent1_row13_line):
                recent1_row13_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent1_row14_line):
                recent1_row14_line = line.new(bar_index, close, bar_index, close, width=2)
            line.set_xloc(recent1_row0_line, time[recent1_start_i], time_close[math.max(recent1_start_i - recent1_row0_width, 0)], xloc.bar_time)
            line.set_y1(recent1_row0_line, recent1_row0_price)
            line.set_y2(recent1_row0_line, recent1_row0_price)
            line.set_color(recent1_row0_line, recent1_color)
            line.set_xloc(recent1_row1_line, time[recent1_start_i], time_close[math.max(recent1_start_i - recent1_row1_width, 0)], xloc.bar_time)
            line.set_y1(recent1_row1_line, recent1_row1_price)
            line.set_y2(recent1_row1_line, recent1_row1_price)
            line.set_color(recent1_row1_line, recent1_color)
            line.set_xloc(recent1_row2_line, time[recent1_start_i], time_close[math.max(recent1_start_i - recent1_row2_width, 0)], xloc.bar_time)
            line.set_y1(recent1_row2_line, recent1_row2_price)
            line.set_y2(recent1_row2_line, recent1_row2_price)
            line.set_color(recent1_row2_line, recent1_color)
            line.set_xloc(recent1_row3_line, time[recent1_start_i], time_close[math.max(recent1_start_i - recent1_row3_width, 0)], xloc.bar_time)
            line.set_y1(recent1_row3_line, recent1_row3_price)
            line.set_y2(recent1_row3_line, recent1_row3_price)
            line.set_color(recent1_row3_line, recent1_color)
            line.set_xloc(recent1_row4_line, time[recent1_start_i], time_close[math.max(recent1_start_i - recent1_row4_width, 0)], xloc.bar_time)
            line.set_y1(recent1_row4_line, recent1_row4_price)
            line.set_y2(recent1_row4_line, recent1_row4_price)
            line.set_color(recent1_row4_line, recent1_color)
            line.set_xloc(recent1_row5_line, time[recent1_start_i], time_close[math.max(recent1_start_i - recent1_row5_width, 0)], xloc.bar_time)
            line.set_y1(recent1_row5_line, recent1_row5_price)
            line.set_y2(recent1_row5_line, recent1_row5_price)
            line.set_color(recent1_row5_line, recent1_color)
            line.set_xloc(recent1_row6_line, time[recent1_start_i], time_close[math.max(recent1_start_i - recent1_row6_width, 0)], xloc.bar_time)
            line.set_y1(recent1_row6_line, recent1_row6_price)
            line.set_y2(recent1_row6_line, recent1_row6_price)
            line.set_color(recent1_row6_line, recent1_color)
            line.set_xloc(recent1_row7_line, time[recent1_start_i], time_close[math.max(recent1_start_i - recent1_row7_width, 0)], xloc.bar_time)
            line.set_y1(recent1_row7_line, recent1_row7_price)
            line.set_y2(recent1_row7_line, recent1_row7_price)
            line.set_color(recent1_row7_line, recent1_color)
            line.set_xloc(recent1_row8_line, time[recent1_start_i], time_close[math.max(recent1_start_i - recent1_row8_width, 0)], xloc.bar_time)
            line.set_y1(recent1_row8_line, recent1_row8_price)
            line.set_y2(recent1_row8_line, recent1_row8_price)
            line.set_color(recent1_row8_line, recent1_color)
            line.set_xloc(recent1_row9_line, time[recent1_start_i], time_close[math.max(recent1_start_i - recent1_row9_width, 0)], xloc.bar_time)
            line.set_y1(recent1_row9_line, recent1_row9_price)
            line.set_y2(recent1_row9_line, recent1_row9_price)
            line.set_color(recent1_row9_line, recent1_color)
            line.set_xloc(recent1_row10_line, time[recent1_start_i], time_close[math.max(recent1_start_i - recent1_row10_width, 0)], xloc.bar_time)
            line.set_y1(recent1_row10_line, recent1_row10_price)
            line.set_y2(recent1_row10_line, recent1_row10_price)
            line.set_color(recent1_row10_line, recent1_color)
            line.set_xloc(recent1_row11_line, time[recent1_start_i], time_close[math.max(recent1_start_i - recent1_row11_width, 0)], xloc.bar_time)
            line.set_y1(recent1_row11_line, recent1_row11_price)
            line.set_y2(recent1_row11_line, recent1_row11_price)
            line.set_color(recent1_row11_line, recent1_color)
            line.set_xloc(recent1_row12_line, time[recent1_start_i], time_close[math.max(recent1_start_i - recent1_row12_width, 0)], xloc.bar_time)
            line.set_y1(recent1_row12_line, recent1_row12_price)
            line.set_y2(recent1_row12_line, recent1_row12_price)
            line.set_color(recent1_row12_line, recent1_color)
            line.set_xloc(recent1_row13_line, time[recent1_start_i], time_close[math.max(recent1_start_i - recent1_row13_width, 0)], xloc.bar_time)
            line.set_y1(recent1_row13_line, recent1_row13_price)
            line.set_y2(recent1_row13_line, recent1_row13_price)
            line.set_color(recent1_row13_line, recent1_color)
            line.set_xloc(recent1_row14_line, time[recent1_start_i], time_close[math.max(recent1_start_i - recent1_row14_width, 0)], xloc.bar_time)
            line.set_y1(recent1_row14_line, recent1_row14_price)
            line.set_y2(recent1_row14_line, recent1_row14_price)
            line.set_color(recent1_row14_line, recent1_color)
            if show_vpoc:
                if na(recent1_vpoc_label):
                    recent1_vpoc_label = label.new(bar_index, close, yloc=yloc.price, style=label.style_diamond, size=size.tiny, color=VPOC_COLOR)
                label.set_xloc(recent1_vpoc_label, time[recent1_start_i + 1], xloc.bar_time)
                label.set_y(recent1_vpoc_label, recent1_vpoc_price)
            if not show_vpoc and (not na(recent1_vpoc_label)):
                label.delete(recent1_vpoc_label)
                recent1_vpoc_label = na
        else:
            if not na(recent1_low_line):
                line.delete(recent1_low_line)
                recent1_low_line = na
            if not na(recent1_high_line):
                line.delete(recent1_high_line)
                recent1_high_line = na
            if not na(recent1_vpoc_label):
                label.delete(recent1_vpoc_label)
                recent1_vpoc_label = na
            if not na(recent1_row0_line):
                line.delete(recent1_row0_line)
                recent1_row0_line = na
            if not na(recent1_row1_line):
                line.delete(recent1_row1_line)
                recent1_row1_line = na
            if not na(recent1_row2_line):
                line.delete(recent1_row2_line)
                recent1_row2_line = na
            if not na(recent1_row3_line):
                line.delete(recent1_row3_line)
                recent1_row3_line = na
            if not na(recent1_row4_line):
                line.delete(recent1_row4_line)
                recent1_row4_line = na
            if not na(recent1_row5_line):
                line.delete(recent1_row5_line)
                recent1_row5_line = na
            if not na(recent1_row6_line):
                line.delete(recent1_row6_line)
                recent1_row6_line = na
            if not na(recent1_row7_line):
                line.delete(recent1_row7_line)
                recent1_row7_line = na
            if not na(recent1_row8_line):
                line.delete(recent1_row8_line)
                recent1_row8_line = na
            if not na(recent1_row9_line):
                line.delete(recent1_row9_line)
                recent1_row9_line = na
            if not na(recent1_row10_line):
                line.delete(recent1_row10_line)
                recent1_row10_line = na
            if not na(recent1_row11_line):
                line.delete(recent1_row11_line)
                recent1_row11_line = na
            if not na(recent1_row12_line):
                line.delete(recent1_row12_line)
                recent1_row12_line = na
            if not na(recent1_row13_line):
                line.delete(recent1_row13_line)
                recent1_row13_line = na
            if not na(recent1_row14_line):
                line.delete(recent1_row14_line)
                recent1_row14_line = na
        recent2_start_i = block_size * 2 + block_bar
        recent2_end_i = math.max(block_size * 2 - (block_size - block_bar) + 1, 0)
        recent2_color_n = (block_index[recent2_end_i] + 3) % 2
        __block_result_2__ = na
        if recent2_color_n == 0:
            __block_result_2__ = color.purple
        elif recent2_color_n == 1:
            __block_result_2__ = color.teal
        recent2_color = __block_result_2__
        if not na(time[recent2_start_i]) and recent2_start_i - recent2_end_i > 5:
            if na(recent2_low_line):
                recent2_low_line = line.new(bar_index, high, bar_index, high, color=BOUNARY_COLOR)
            if na(recent2_high_line):
                recent2_high_line = line.new(bar_index, low, bar_index, low, color=BOUNARY_COLOR)
            recent2_block_high = rolling_high[recent2_end_i]
            recent2_block_low = rolling_low[recent2_end_i]
            line.set_xloc(recent2_low_line, time[recent2_start_i], time[recent2_end_i], xloc.bar_time)
            line.set_y1(recent2_low_line, recent2_block_low)
            line.set_y2(recent2_low_line, recent2_block_low)
            line.set_xloc(recent2_high_line, time[recent2_start_i], time[recent2_end_i], xloc.bar_time)
            line.set_y1(recent2_high_line, recent2_block_high)
            line.set_y2(recent2_high_line, recent2_block_high)
            recent2_block_height = recent2_block_high - recent2_block_low
            recent2_row_height = recent2_block_height / 15
            recent2_row0_low = recent2_block_low + recent2_row_height * 0
            recent2_row0_high = recent2_block_low + recent2_row_height * 1
            recent2_row0_value: float = 0.0
            recent2_row1_low = recent2_block_low + recent2_row_height * 1
            recent2_row1_high = recent2_block_low + recent2_row_height * 2
            recent2_row1_value: float = 0.0
            recent2_row2_low = recent2_block_low + recent2_row_height * 2
            recent2_row2_high = recent2_block_low + recent2_row_height * 3
            recent2_row2_value: float = 0.0
            recent2_row3_low = recent2_block_low + recent2_row_height * 3
            recent2_row3_high = recent2_block_low + recent2_row_height * 4
            recent2_row3_value: float = 0.0
            recent2_row4_low = recent2_block_low + recent2_row_height * 4
            recent2_row4_high = recent2_block_low + recent2_row_height * 5
            recent2_row4_value: float = 0.0
            recent2_row5_low = recent2_block_low + recent2_row_height * 5
            recent2_row5_high = recent2_block_low + recent2_row_height * 6
            recent2_row5_value: float = 0.0
            recent2_row6_low = recent2_block_low + recent2_row_height * 6
            recent2_row6_high = recent2_block_low + recent2_row_height * 7
            recent2_row6_value: float = 0.0
            recent2_row7_low = recent2_block_low + recent2_row_height * 7
            recent2_row7_high = recent2_block_low + recent2_row_height * 8
            recent2_row7_value: float = 0.0
            recent2_row8_low = recent2_block_low + recent2_row_height * 8
            recent2_row8_high = recent2_block_low + recent2_row_height * 9
            recent2_row8_value: float = 0.0
            recent2_row9_low = recent2_block_low + recent2_row_height * 9
            recent2_row9_high = recent2_block_low + recent2_row_height * 10
            recent2_row9_value: float = 0.0
            recent2_row10_low = recent2_block_low + recent2_row_height * 10
            recent2_row10_high = recent2_block_low + recent2_row_height * 11
            recent2_row10_value: float = 0.0
            recent2_row11_low = recent2_block_low + recent2_row_height * 11
            recent2_row11_high = recent2_block_low + recent2_row_height * 12
            recent2_row11_value: float = 0.0
            recent2_row12_low = recent2_block_low + recent2_row_height * 12
            recent2_row12_high = recent2_block_low + recent2_row_height * 13
            recent2_row12_value: float = 0.0
            recent2_row13_low = recent2_block_low + recent2_row_height * 13
            recent2_row13_high = recent2_block_low + recent2_row_height * 14
            recent2_row13_value: float = 0.0
            recent2_row14_low = recent2_block_low + recent2_row_height * 14
            recent2_row14_high = recent2_block_low + recent2_row_height * 15
            recent2_row14_value: float = 0.0
            for i in pine_range(recent2_start_i, recent2_end_i + 1, 1):
                bar_n_rows_affected: int = 0
                bar_row0_value: float = 0.0
                if low[i] < recent2_row0_high and high[i] > recent2_row0_low:
                    bar_row0_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row1_value: float = 0.0
                if low[i] < recent2_row1_high and high[i] > recent2_row1_low:
                    bar_row1_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row2_value: float = 0.0
                if low[i] < recent2_row2_high and high[i] > recent2_row2_low:
                    bar_row2_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row3_value: float = 0.0
                if low[i] < recent2_row3_high and high[i] > recent2_row3_low:
                    bar_row3_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row4_value: float = 0.0
                if low[i] < recent2_row4_high and high[i] > recent2_row4_low:
                    bar_row4_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row5_value: float = 0.0
                if low[i] < recent2_row5_high and high[i] > recent2_row5_low:
                    bar_row5_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row6_value: float = 0.0
                if low[i] < recent2_row6_high and high[i] > recent2_row6_low:
                    bar_row6_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row7_value: float = 0.0
                if low[i] < recent2_row7_high and high[i] > recent2_row7_low:
                    bar_row7_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row8_value: float = 0.0
                if low[i] < recent2_row8_high and high[i] > recent2_row8_low:
                    bar_row8_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row9_value: float = 0.0
                if low[i] < recent2_row9_high and high[i] > recent2_row9_low:
                    bar_row9_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row10_value: float = 0.0
                if low[i] < recent2_row10_high and high[i] > recent2_row10_low:
                    bar_row10_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row11_value: float = 0.0
                if low[i] < recent2_row11_high and high[i] > recent2_row11_low:
                    bar_row11_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row12_value: float = 0.0
                if low[i] < recent2_row12_high and high[i] > recent2_row12_low:
                    bar_row12_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row13_value: float = 0.0
                if low[i] < recent2_row13_high and high[i] > recent2_row13_low:
                    bar_row13_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                bar_row14_value: float = 0.0
                if low[i] < recent2_row14_high and high[i] > recent2_row14_low:
                    bar_row14_value = custom_volume[i]
                    bar_n_rows_affected = bar_n_rows_affected + 1
                recent2_row0_value = recent2_row0_value + bar_row0_value / bar_n_rows_affected / recent2_row_height
                recent2_row1_value = recent2_row1_value + bar_row1_value / bar_n_rows_affected / recent2_row_height
                recent2_row2_value = recent2_row2_value + bar_row2_value / bar_n_rows_affected / recent2_row_height
                recent2_row3_value = recent2_row3_value + bar_row3_value / bar_n_rows_affected / recent2_row_height
                recent2_row4_value = recent2_row4_value + bar_row4_value / bar_n_rows_affected / recent2_row_height
                recent2_row5_value = recent2_row5_value + bar_row5_value / bar_n_rows_affected / recent2_row_height
                recent2_row6_value = recent2_row6_value + bar_row6_value / bar_n_rows_affected / recent2_row_height
                recent2_row7_value = recent2_row7_value + bar_row7_value / bar_n_rows_affected / recent2_row_height
                recent2_row8_value = recent2_row8_value + bar_row8_value / bar_n_rows_affected / recent2_row_height
                recent2_row9_value = recent2_row9_value + bar_row9_value / bar_n_rows_affected / recent2_row_height
                recent2_row10_value = recent2_row10_value + bar_row10_value / bar_n_rows_affected / recent2_row_height
                recent2_row11_value = recent2_row11_value + bar_row11_value / bar_n_rows_affected / recent2_row_height
                recent2_row12_value = recent2_row12_value + bar_row12_value / bar_n_rows_affected / recent2_row_height
                recent2_row13_value = recent2_row13_value + bar_row13_value / bar_n_rows_affected / recent2_row_height
                recent2_row14_value = recent2_row14_value + bar_row14_value / bar_n_rows_affected / recent2_row_height
            recent2_avg_i = math.min(recent2_start_i + 1 + block_size * 4, bar_index)
            recent2_row0_price = (recent2_row0_low + recent2_row0_high) / 2
            recent2_row0_width = math.floor(visual_row_width * recent2_row0_value / highest_row_value_avg[recent2_avg_i])
            recent2_row1_price = (recent2_row1_low + recent2_row1_high) / 2
            recent2_row1_width = math.floor(visual_row_width * recent2_row1_value / highest_row_value_avg[recent2_avg_i])
            recent2_row2_price = (recent2_row2_low + recent2_row2_high) / 2
            recent2_row2_width = math.floor(visual_row_width * recent2_row2_value / highest_row_value_avg[recent2_avg_i])
            recent2_row3_price = (recent2_row3_low + recent2_row3_high) / 2
            recent2_row3_width = math.floor(visual_row_width * recent2_row3_value / highest_row_value_avg[recent2_avg_i])
            recent2_row4_price = (recent2_row4_low + recent2_row4_high) / 2
            recent2_row4_width = math.floor(visual_row_width * recent2_row4_value / highest_row_value_avg[recent2_avg_i])
            recent2_row5_price = (recent2_row5_low + recent2_row5_high) / 2
            recent2_row5_width = math.floor(visual_row_width * recent2_row5_value / highest_row_value_avg[recent2_avg_i])
            recent2_row6_price = (recent2_row6_low + recent2_row6_high) / 2
            recent2_row6_width = math.floor(visual_row_width * recent2_row6_value / highest_row_value_avg[recent2_avg_i])
            recent2_row7_price = (recent2_row7_low + recent2_row7_high) / 2
            recent2_row7_width = math.floor(visual_row_width * recent2_row7_value / highest_row_value_avg[recent2_avg_i])
            recent2_row8_price = (recent2_row8_low + recent2_row8_high) / 2
            recent2_row8_width = math.floor(visual_row_width * recent2_row8_value / highest_row_value_avg[recent2_avg_i])
            recent2_row9_price = (recent2_row9_low + recent2_row9_high) / 2
            recent2_row9_width = math.floor(visual_row_width * recent2_row9_value / highest_row_value_avg[recent2_avg_i])
            recent2_row10_price = (recent2_row10_low + recent2_row10_high) / 2
            recent2_row10_width = math.floor(visual_row_width * recent2_row10_value / highest_row_value_avg[recent2_avg_i])
            recent2_row11_price = (recent2_row11_low + recent2_row11_high) / 2
            recent2_row11_width = math.floor(visual_row_width * recent2_row11_value / highest_row_value_avg[recent2_avg_i])
            recent2_row12_price = (recent2_row12_low + recent2_row12_high) / 2
            recent2_row12_width = math.floor(visual_row_width * recent2_row12_value / highest_row_value_avg[recent2_avg_i])
            recent2_row13_price = (recent2_row13_low + recent2_row13_high) / 2
            recent2_row13_width = math.floor(visual_row_width * recent2_row13_value / highest_row_value_avg[recent2_avg_i])
            recent2_row14_price = (recent2_row14_low + recent2_row14_high) / 2
            recent2_row14_width = math.floor(visual_row_width * recent2_row14_value / highest_row_value_avg[recent2_avg_i])
            recent2_vpoc_price: float = na(float)
            recent2_highes_row_value: float = 0
            if recent2_highes_row_value < recent2_row0_value:
                recent2_highes_row_value = recent2_row0_value
                recent2_vpoc_price = recent2_row0_price
            if recent2_highes_row_value < recent2_row1_value:
                recent2_highes_row_value = recent2_row1_value
                recent2_vpoc_price = recent2_row1_price
            if recent2_highes_row_value < recent2_row2_value:
                recent2_highes_row_value = recent2_row2_value
                recent2_vpoc_price = recent2_row2_price
            if recent2_highes_row_value < recent2_row3_value:
                recent2_highes_row_value = recent2_row3_value
                recent2_vpoc_price = recent2_row3_price
            if recent2_highes_row_value < recent2_row4_value:
                recent2_highes_row_value = recent2_row4_value
                recent2_vpoc_price = recent2_row4_price
            if recent2_highes_row_value < recent2_row5_value:
                recent2_highes_row_value = recent2_row5_value
                recent2_vpoc_price = recent2_row5_price
            if recent2_highes_row_value < recent2_row6_value:
                recent2_highes_row_value = recent2_row6_value
                recent2_vpoc_price = recent2_row6_price
            if recent2_highes_row_value < recent2_row7_value:
                recent2_highes_row_value = recent2_row7_value
                recent2_vpoc_price = recent2_row7_price
            if recent2_highes_row_value < recent2_row8_value:
                recent2_highes_row_value = recent2_row8_value
                recent2_vpoc_price = recent2_row8_price
            if recent2_highes_row_value < recent2_row9_value:
                recent2_highes_row_value = recent2_row9_value
                recent2_vpoc_price = recent2_row9_price
            if recent2_highes_row_value < recent2_row10_value:
                recent2_highes_row_value = recent2_row10_value
                recent2_vpoc_price = recent2_row10_price
            if recent2_highes_row_value < recent2_row11_value:
                recent2_highes_row_value = recent2_row11_value
                recent2_vpoc_price = recent2_row11_price
            if recent2_highes_row_value < recent2_row12_value:
                recent2_highes_row_value = recent2_row12_value
                recent2_vpoc_price = recent2_row12_price
            if recent2_highes_row_value < recent2_row13_value:
                recent2_highes_row_value = recent2_row13_value
                recent2_vpoc_price = recent2_row13_price
            if recent2_highes_row_value < recent2_row14_value:
                recent2_highes_row_value = recent2_row14_value
                recent2_vpoc_price = recent2_row14_price
            if na(recent2_row0_line):
                recent2_row0_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent2_row1_line):
                recent2_row1_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent2_row2_line):
                recent2_row2_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent2_row3_line):
                recent2_row3_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent2_row4_line):
                recent2_row4_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent2_row5_line):
                recent2_row5_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent2_row6_line):
                recent2_row6_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent2_row7_line):
                recent2_row7_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent2_row8_line):
                recent2_row8_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent2_row9_line):
                recent2_row9_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent2_row10_line):
                recent2_row10_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent2_row11_line):
                recent2_row11_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent2_row12_line):
                recent2_row12_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent2_row13_line):
                recent2_row13_line = line.new(bar_index, close, bar_index, close, width=2)
            if na(recent2_row14_line):
                recent2_row14_line = line.new(bar_index, close, bar_index, close, width=2)
            line.set_xloc(recent2_row0_line, time[recent2_start_i], time_close[math.max(recent2_start_i - recent2_row0_width, 0)], xloc.bar_time)
            line.set_y1(recent2_row0_line, recent2_row0_price)
            line.set_y2(recent2_row0_line, recent2_row0_price)
            line.set_color(recent2_row0_line, recent2_color)
            line.set_xloc(recent2_row1_line, time[recent2_start_i], time_close[math.max(recent2_start_i - recent2_row1_width, 0)], xloc.bar_time)
            line.set_y1(recent2_row1_line, recent2_row1_price)
            line.set_y2(recent2_row1_line, recent2_row1_price)
            line.set_color(recent2_row1_line, recent2_color)
            line.set_xloc(recent2_row2_line, time[recent2_start_i], time_close[math.max(recent2_start_i - recent2_row2_width, 0)], xloc.bar_time)
            line.set_y1(recent2_row2_line, recent2_row2_price)
            line.set_y2(recent2_row2_line, recent2_row2_price)
            line.set_color(recent2_row2_line, recent2_color)
            line.set_xloc(recent2_row3_line, time[recent2_start_i], time_close[math.max(recent2_start_i - recent2_row3_width, 0)], xloc.bar_time)
            line.set_y1(recent2_row3_line, recent2_row3_price)
            line.set_y2(recent2_row3_line, recent2_row3_price)
            line.set_color(recent2_row3_line, recent2_color)
            line.set_xloc(recent2_row4_line, time[recent2_start_i], time_close[math.max(recent2_start_i - recent2_row4_width, 0)], xloc.bar_time)
            line.set_y1(recent2_row4_line, recent2_row4_price)
            line.set_y2(recent2_row4_line, recent2_row4_price)
            line.set_color(recent2_row4_line, recent2_color)
            line.set_xloc(recent2_row5_line, time[recent2_start_i], time_close[math.max(recent2_start_i - recent2_row5_width, 0)], xloc.bar_time)
            line.set_y1(recent2_row5_line, recent2_row5_price)
            line.set_y2(recent2_row5_line, recent2_row5_price)
            line.set_color(recent2_row5_line, recent2_color)
            line.set_xloc(recent2_row6_line, time[recent2_start_i], time_close[math.max(recent2_start_i - recent2_row6_width, 0)], xloc.bar_time)
            line.set_y1(recent2_row6_line, recent2_row6_price)
            line.set_y2(recent2_row6_line, recent2_row6_price)
            line.set_color(recent2_row6_line, recent2_color)
            line.set_xloc(recent2_row7_line, time[recent2_start_i], time_close[math.max(recent2_start_i - recent2_row7_width, 0)], xloc.bar_time)
            line.set_y1(recent2_row7_line, recent2_row7_price)
            line.set_y2(recent2_row7_line, recent2_row7_price)
            line.set_color(recent2_row7_line, recent2_color)
            line.set_xloc(recent2_row8_line, time[recent2_start_i], time_close[math.max(recent2_start_i - recent2_row8_width, 0)], xloc.bar_time)
            line.set_y1(recent2_row8_line, recent2_row8_price)
            line.set_y2(recent2_row8_line, recent2_row8_price)
            line.set_color(recent2_row8_line, recent2_color)
            line.set_xloc(recent2_row9_line, time[recent2_start_i], time_close[math.max(recent2_start_i - recent2_row9_width, 0)], xloc.bar_time)
            line.set_y1(recent2_row9_line, recent2_row9_price)
            line.set_y2(recent2_row9_line, recent2_row9_price)
            line.set_color(recent2_row9_line, recent2_color)
            line.set_xloc(recent2_row10_line, time[recent2_start_i], time_close[math.max(recent2_start_i - recent2_row10_width, 0)], xloc.bar_time)
            line.set_y1(recent2_row10_line, recent2_row10_price)
            line.set_y2(recent2_row10_line, recent2_row10_price)
            line.set_color(recent2_row10_line, recent2_color)
            line.set_xloc(recent2_row11_line, time[recent2_start_i], time_close[math.max(recent2_start_i - recent2_row11_width, 0)], xloc.bar_time)
            line.set_y1(recent2_row11_line, recent2_row11_price)
            line.set_y2(recent2_row11_line, recent2_row11_price)
            line.set_color(recent2_row11_line, recent2_color)
            line.set_xloc(recent2_row12_line, time[recent2_start_i], time_close[math.max(recent2_start_i - recent2_row12_width, 0)], xloc.bar_time)
            line.set_y1(recent2_row12_line, recent2_row12_price)
            line.set_y2(recent2_row12_line, recent2_row12_price)
            line.set_color(recent2_row12_line, recent2_color)
            line.set_xloc(recent2_row13_line, time[recent2_start_i], time_close[math.max(recent2_start_i - recent2_row13_width, 0)], xloc.bar_time)
            line.set_y1(recent2_row13_line, recent2_row13_price)
            line.set_y2(recent2_row13_line, recent2_row13_price)
            line.set_color(recent2_row13_line, recent2_color)
            line.set_xloc(recent2_row14_line, time[recent2_start_i], time_close[math.max(recent2_start_i - recent2_row14_width, 0)], xloc.bar_time)
            line.set_y1(recent2_row14_line, recent2_row14_price)
            line.set_y2(recent2_row14_line, recent2_row14_price)
            line.set_color(recent2_row14_line, recent2_color)
        else:
            if not na(recent2_low_line):
                line.delete(recent2_low_line)
                recent2_low_line = na
            if not na(recent2_high_line):
                line.delete(recent2_high_line)
                recent2_high_line = na
            if not na(recent2_row0_line):
                line.delete(recent2_row0_line)
                recent2_row0_line = na
            if not na(recent2_row1_line):
                line.delete(recent2_row1_line)
                recent2_row1_line = na
            if not na(recent2_row2_line):
                line.delete(recent2_row2_line)
                recent2_row2_line = na
            if not na(recent2_row3_line):
                line.delete(recent2_row3_line)
                recent2_row3_line = na
            if not na(recent2_row4_line):
                line.delete(recent2_row4_line)
                recent2_row4_line = na
            if not na(recent2_row5_line):
                line.delete(recent2_row5_line)
                recent2_row5_line = na
            if not na(recent2_row6_line):
                line.delete(recent2_row6_line)
                recent2_row6_line = na
            if not na(recent2_row7_line):
                line.delete(recent2_row7_line)
                recent2_row7_line = na
            if not na(recent2_row8_line):
                line.delete(recent2_row8_line)
                recent2_row8_line = na
            if not na(recent2_row9_line):
                line.delete(recent2_row9_line)
                recent2_row9_line = na
            if not na(recent2_row10_line):
                line.delete(recent2_row10_line)
                recent2_row10_line = na
            if not na(recent2_row11_line):
                line.delete(recent2_row11_line)
                recent2_row11_line = na
            if not na(recent2_row12_line):
                line.delete(recent2_row12_line)
                recent2_row12_line = na
            if not na(recent2_row13_line):
                line.delete(recent2_row13_line)
                recent2_row13_line = na
            if not na(recent2_row14_line):
                line.delete(recent2_row14_line)
                recent2_row14_line = na


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
