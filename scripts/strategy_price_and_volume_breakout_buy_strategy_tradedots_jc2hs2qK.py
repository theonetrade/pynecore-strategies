"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, high, input, label, line, low, open, plot,
    plotcandle, script, strategy, ta, volume
)
from pynecore.types import Series


@script.strategy('Price and Volume Breakout Buy Strategy [TradeDots]', overlay=True, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=70, commission_type=strategy.commission.percent, commission_value=0.01, margin_long=0, margin_short=0, close_by_id=True)
def main(
    input_price_breakout_period=input.int(60, 'Price Breakout Period'),
    input_volume_breakout_period=input.int(60, 'Volume Breakout Period'),
    input_trendline_legnth=input.int(200, 'Trendline Length'),
    input_order_direction=input.string('Long', options=('Long', 'Short', 'Long and Short'), title='Order Direction')
):
    price_highest: Series = ta.highest(input_price_breakout_period)
    price_lowest: Series = ta.lowest(input_price_breakout_period)
    volume_highest: Series = ta.highest(volume, input_volume_breakout_period)
    sma_1 = ta.sma(close, input_trendline_legnth)
    if close > price_highest[1] and volume > volume_highest[1] and (close > sma_1) and (strategy.opentrades == 0) and (input_order_direction != 'Short'):
        strategy.entry('Long', strategy.long)
        line.new(bar_index[input_price_breakout_period], price_highest[1], bar_index, price_highest[1], color=color.new('#9CFF87'), width=2)
        label.new(bar_index, low, '🟢 Breakout Buy', style=label.style_label_up, color=color.new('#9CFF87'))
    sma_2 = ta.sma(close, input_trendline_legnth)
    sma_3 = ta.sma(close, input_trendline_legnth)
    sma_4 = ta.sma(close, input_trendline_legnth)
    sma_5 = ta.sma(close, input_trendline_legnth)
    if close < ta.sma(close, input_trendline_legnth) and close[1] < sma_2 and (close[2] < sma_3) and (close[3] < sma_4) and (close[4] < sma_5) and (strategy.opentrades.size(strategy.opentrades - 1) > 0):
        strategy.close('Long')
        label.new(bar_index, high, '🔴 Close Position', style=label.style_label_down, color=color.new('#F9396A'), textcolor=color.white)
    sma_6 = ta.sma(close, input_trendline_legnth)
    if close < price_lowest[1] and volume > volume_highest[1] and (close < sma_6) and (strategy.opentrades == 0) and (input_order_direction != 'Long'):
        strategy.entry('Short', strategy.short)
        line.new(bar_index[input_price_breakout_period], price_lowest[1], bar_index, price_lowest[1], color=color.new('#F9396A'), width=2)
        label.new(bar_index, high, '🔴 Breakout Sell', style=label.style_label_down, color=color.new('#F9396A'), textcolor=color.white)
    sma_7 = ta.sma(close, input_trendline_legnth)
    sma_8 = ta.sma(close, input_trendline_legnth)
    sma_9 = ta.sma(close, input_trendline_legnth)
    sma_10 = ta.sma(close, input_trendline_legnth)
    if close > ta.sma(close, input_trendline_legnth) and close[1] > sma_7 and (close[2] > sma_8) and (close[3] > sma_9) and (close[4] > sma_10) and (strategy.opentrades.size(strategy.opentrades - 1) < 0):
        strategy.close('Short')
        label.new(bar_index, low, '🟢 Close Position', style=label.style_label_up, color=color.new('#9CFF87'))
    plot(ta.sma(close, input_trendline_legnth), color=color.white, linewidth=2)
    plotcandle(open, high, low, close, title='Candles', color=color.new('#9CFF87') if close > ta.sma(close, input_trendline_legnth) else color.new('#F9396A'), wickcolor=color.new('#9CFF87') if close > ta.sma(close, input_trendline_legnth) else color.new('#F9396A'), force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
