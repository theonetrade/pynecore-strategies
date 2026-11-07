"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, display, fill, input, label, na, plot, request,
    script, strategy, syminfo, ta
)
from pynecore.types import Persistent, Series


@script.strategy('Multi Timeframe RSI Buy Sell Strategy [TradeDots]', overlay=False, initial_capital=10000, commission_type=strategy.commission.percent, commission_value=0.01, default_qty_type=strategy.percent_of_equity, default_qty_value=60, margin_long=0, margin_short=0, close_by_id=True)
def main(
    input_rsi1_enable=input.bool(True, '', group='RSI 1 Settings', inline='RSI1'),
    input_rsi2_enable=input.bool(True, '', group='RSI 2 Settings', inline='RSI2'),
    input_rsi3_enable=input.bool(True, '', group='RSI 3 Settings', inline='RSI3'),
    input_rsi1_color=input.color(defval=color.new('#CAF0F8'), title='', group='RSI 1 Settings', inline='RSI1'),
    input_rsi2_color=input.color(defval=color.new('#00B4D8'), title='', group='RSI 2 Settings', inline='RSI2'),
    input_rsi3_color=input.color(defval=color.new('#0077B6'), title='', group='RSI 3 Settings', inline='RSI3'),
    input_rsi1_length=input.int(defval=14, title='RSI 1 Length', group='RSI 1 Settings'),
    input_rsi2_length=input.int(defval=14, title='RSI 2 Length', group='RSI 2 Settings'),
    input_rsi3_length=input.int(defval=14, title='RSI 3 Length', group='RSI 3 Settings'),
    input_rsi1_source: Series[float] = input(close, 'Source 1', group='RSI 1 Settings'),
    input_rsi2_source: Series[float] = input(close, 'Source 2', group='RSI 2 Settings'),
    input_rsi3_source: Series[float] = input(close, 'Source 3', group='RSI 3 Settings'),
    input_rsi1_tf=input.timeframe('5', group='RSI 1 Settings'),
    input_rsi2_tf=input.timeframe('15', group='RSI 2 Settings'),
    input_rsi3_tf=input.timeframe('30', group='RSI 3 Settings'),
    maTypeInput=input.string('SMA', title='MA Type', options=('SMA', 'EMA', 'SMMA (RMA)', 'WMA', 'VWMA'), group='MA Settings', display=display.data_window),
    maLengthInput=input.int(14, title='MA Length', group='MA Settings', display=display.data_window),
    input_enable_backtest=input.bool(True, 'Enable backtest', group='Strategy Settings'),
    input_sell_threshold=input.float(70, 'Sell Threshold', group='Strategy Settings'),
    input_buy_threshold=input.float(30, 'Buy Threshold', group='Strategy Settings'),
    input_cool_down=input.int(defval=5, title='Signal Cool Down Period', minval=1, step=1, group='Strategy Settings')
):
    RSI1 = request.security(syminfo.tickerid, input_rsi1_tf, ta.rsi(input_rsi1_source, input_rsi1_length))
    RSI2 = request.security(syminfo.tickerid, input_rsi2_tf, ta.rsi(input_rsi2_source, input_rsi2_length))
    RSI3 = request.security(syminfo.tickerid, input_rsi3_tf, ta.rsi(input_rsi3_source, input_rsi3_length))
    def ma(source, length, type):
        __block_result__ = na
        __switch__ = type
        if __switch__ == 'SMA':
            __block_result__ = ta.sma(source, length)
        elif __switch__ == 'EMA':
            __block_result__ = ta.ema(source, length)
        elif __switch__ == 'SMMA (RMA)':
            __block_result__ = ta.rma(source, length)
        elif __switch__ == 'WMA':
            __block_result__ = ta.wma(source, length)
        elif __switch__ == 'VWMA':
            __block_result__ = ta.vwma(source, length)
        return __block_result__

    RSI1_plot = plot(RSI1 if input_rsi1_enable else na, color=color.new('#CAF0F8'), title='RSI 1')
    RSI2_plot = plot(RSI2 if input_rsi2_enable else na, color=color.new('#00B4D8'), title='RSI 2')
    RSI3_plot = plot(RSI3 if input_rsi3_enable else na, color=color.new('#0077B6'), title='RSI 3')
    buy_cool_down_counter: Persistent[int] = input_cool_down
    sell_cool_down_counter: Persistent[int] = input_cool_down
    sum: float = 0
    n: int = 0
    if input_rsi1_enable == True:
        sum = sum + RSI1
        n = n + 1
    if input_rsi2_enable == True:
        sum = sum + RSI2
        n = n + 1
    if input_rsi3_enable == True:
        sum = sum + RSI3
        n = n + 1
    rsiMA: Series = ma(sum / n, maLengthInput, maTypeInput)
    line_opacity = 20 if rsiMA > 0 and rsiMA > rsiMA[1] or (rsiMA < 0 and rsiMA < rsiMA[1]) else 60
    plot(rsiMA, 'RSI-based MA', color.new(color.new('#9CFF87'), line_opacity) if rsiMA > 50 else color.new(color.new('#F9396A'), line_opacity), linewidth=2)
    plot(input_sell_threshold, 'Sell Threshold', color=color.from_gradient(rsiMA, 50, input_sell_threshold, color.new(color.gray, 60), color.new(color.new('#F9396A'), 40)), linewidth=2)
    plot(input_buy_threshold, 'Buy Threshold', color=color.from_gradient(rsiMA, input_buy_threshold, 50, color.new(color.new('#9CFF87'), 40), color.new(color.gray, 60)), linewidth=2)
    middleline = plot(50, title='Middle Line', style=plot.style_cross, color=color.gray)
    fill(RSI1_plot, middleline, 100, input_sell_threshold, top_color=color.new(color.new('#9CFF87'), 0), bottom_color=color.new(color.new('#9CFF87'), 100), title='Overbought Gradient Fill 1')
    fill(RSI1_plot, middleline, input_buy_threshold, 0, top_color=color.new(color.new('#F9396A'), 100), bottom_color=color.new(color.new('#F9396A'), 0), title='Oversold Gradient Fill 1')
    fill(RSI2_plot, middleline, 100, input_sell_threshold, top_color=color.new(color.new('#9CFF87'), 0), bottom_color=color.new(color.new('#9CFF87'), 100), title='Overbought Gradient Fill 2')
    fill(RSI2_plot, middleline, input_buy_threshold, 0, top_color=color.new(color.new('#F9396A'), 100), bottom_color=color.new(color.new('#F9396A'), 0), title='Oversold Gradient Fill 2')
    fill(RSI3_plot, middleline, 100, input_sell_threshold, top_color=color.new(color.new('#9CFF87'), 0), bottom_color=color.new(color.new('#9CFF87'), 100), title='Overbought Gradient Fill 3')
    fill(RSI3_plot, middleline, input_buy_threshold, 0, top_color=color.new(color.new('#F9396A'), 100), bottom_color=color.new(color.new('#F9396A'), 0), title='Oversold Gradient Fill 3')
    if (RSI1 < input_buy_threshold if input_rsi1_enable else True) and (RSI2 < input_buy_threshold if input_rsi2_enable else True) and (RSI3 < input_buy_threshold if input_rsi3_enable else True) and input_enable_backtest:
        if buy_cool_down_counter >= input_cool_down:
            strategy.close('Short')
            strategy.entry('Long', strategy.long)
            label.new(bar_index, RSI1, text='Buy', style=label.style_label_up, color=color.new('#9CFF87'))
            sell_cool_down_counter = input_cool_down
            buy_cool_down_counter = 0
        else:
            buy_cool_down_counter = buy_cool_down_counter + 1
    if (RSI1 > input_sell_threshold if input_rsi1_enable else True) and (RSI2 > input_sell_threshold if input_rsi2_enable else True) and (RSI3 > input_sell_threshold if input_rsi3_enable else True) and input_enable_backtest:
        if sell_cool_down_counter >= input_cool_down:
            strategy.close('Long')
            strategy.entry('Short', strategy.short)
            label.new(bar_index, RSI1, text='Sell', style=label.style_label_down, color=color.new('#F9396A'), textcolor=color.new('#FFFFFF'))
            sell_cool_down_counter = 0
            buy_cool_down_counter = input_cool_down
        else:
            sell_cool_down_counter = sell_cool_down_counter + 1


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
