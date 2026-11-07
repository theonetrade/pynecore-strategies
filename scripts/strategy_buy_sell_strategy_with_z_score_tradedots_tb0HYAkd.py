"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, currency, hline, input, label, plot, script,
    strategy, ta
)
from pynecore.types import Persistent, Series


@script.strategy('Buy Sell Strategy With Z-Score [TradeDots]', shorttitle='TradeDots Z-Score Buy Sell', overlay=False, max_lines_count=500, max_boxes_count=100, initial_capital=10000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0.03, default_qty_type=strategy.percent_of_equity, default_qty_value=30, pyramiding=9999, margin_long=0, margin_short=0, close_by_id=True)
def main(
    input_enable_backtest=input.bool(defval=True, title='Enable Backtest'),
    input_rolling_window=input.int(defval=80, title='Rolling Window', minval=1, step=1),
    input_z_thresh=input.float(defval=2.8, title='Z-Score Thershhold'),
    input_cool_down=input.int(defval=5, title='Signal Cool Down Period', minval=1, step=1)
):
    buy_cool_down_counter: Persistent[int] = input_cool_down
    sell_cool_down_counter: Persistent[int] = input_cool_down
    rolling_stdev = ta.stdev(close, input_rolling_window, False)
    rolling_mean = ta.sma(close, input_rolling_window)
    z_score: Series = (close - rolling_mean) / rolling_stdev
    line_opacity = 20 if z_score > 0 and z_score > z_score[1] or (z_score < 0 and z_score < z_score[1]) else 60
    plot(z_score, 'Z-Score', color.new(color.new('#9CFF87'), line_opacity) if z_score > 0 else color.new(color.new('#F9396A'), line_opacity), linewidth=2)
    plot(input_z_thresh, 'Sell Threshold', color=color.from_gradient(z_score, 0, input_z_thresh, color.new(color.gray, 70), color.new(color.new('#F9396A'), 0)), linewidth=2)
    plot(-input_z_thresh, 'Buy Threshold', color=color.from_gradient(z_score, -input_z_thresh, 0, color.new(color.new('#9CFF87'), 0), color.new(color.gray, 70)), linewidth=2)
    hline(0, title='Z-Score 0 Level')
    if z_score > input_z_thresh:
        if sell_cool_down_counter >= input_cool_down:
            label.new(bar_index, z_score, text='Sell', style=label.style_label_down, color=color.new('#F9396A'), textcolor=color.new('#FFFFFF'))
            if input_enable_backtest == True:
                strategy.close('Buy', qty_percent=100, comment='Close all buy orders')
                strategy.entry('Sell', strategy.short, comment='Open Short Position')
            sell_cool_down_counter = 0
            buy_cool_down_counter = input_cool_down
        else:
            sell_cool_down_counter = sell_cool_down_counter + 1
    elif z_score < -input_z_thresh:
        if buy_cool_down_counter >= input_cool_down:
            label.new(bar_index, z_score, text='Buy', style=label.style_label_up, color=color.new('#9CFF87'))
            if input_enable_backtest == True:
                strategy.close('Sell', qty_percent=100, comment='Close all sell orders')
                strategy.entry('Buy', strategy.long, comment='Open Long Position')
            sell_cool_down_counter = input_cool_down
            buy_cool_down_counter = 0
        else:
            buy_cool_down_counter = buy_cool_down_counter + 1


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
