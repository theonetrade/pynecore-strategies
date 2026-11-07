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


@script.strategy('Chande Momentum Oscillator (CMO) Buy Sell Strategy [TradeDots]', overlay=False, max_lines_count=500, max_boxes_count=100, initial_capital=10000, currency=currency.USD, commission_type=strategy.commission.percent, commission_value=0.01, default_qty_type=strategy.percent_of_equity, default_qty_value=80, margin_long=0, margin_short=0, close_by_id=True)
def main(
    enable_backtest=input.bool(defval=True, title='Enable Backtest'),
    source: Series[float] = input(close, 'Source', group='Chande Momentum Oscillator'),
    length=input(9, 'CMO Length', group='Chande Momentum Oscillator'),
    order_direction=input.string('Long & Short', 'Order Direction', options=('Long & Short', 'Long Only', 'Short Only'), group='Strategy'),
    cool_down_period=input.int(defval=5, title='Signal Cool Down Period', minval=1, step=1, group='Strategy'),
    overbought_tresh=input(40, 'Selling Threshold', group='Strategy'),
    oversold_tresh=input(-40, 'Buying Threshold', group='Strategy')
):
    buy_counter: Persistent[int] = cool_down_period
    sell_counter: Persistent[int] = cool_down_period
    cmo = ta.cmo(source, length)
    signal = ta.ema(cmo, 9)
    hist: Series = cmo - signal
    histA_IsUp = hist > hist[1] and hist > 0
    histA_IsDown = hist < hist[1] and hist > 0
    histB_IsDown = hist < hist[1] and hist <= 0
    histB_IsUp = hist > hist[1] and hist <= 0
    hist_color = color.new('#38A3A5') if histA_IsUp else color.new('#CBF3F0') if histA_IsDown else color.new('#0096C7') if histB_IsDown else color.new('#ADE8F4') if histB_IsUp else color.gray
    plot(cmo, 'CMO Line', color=color.new('#9CFF87'))
    plot(signal, 'CMO Signal Line', color=color.new('#F9396A'))
    plot(hist, 'CMO Hist', color=hist_color, style=plot.style_columns, linewidth=5)
    plot(overbought_tresh, 'Selling Threshold', color=color.from_gradient(cmo, 0, overbought_tresh, color.new(color.gray, 70), color.new(color.new('#F9396A'), 0)), linewidth=2)
    plot(oversold_tresh, 'Buying Threshold', color=color.from_gradient(cmo, oversold_tresh, 0, color.new(color.new('#9CFF87'), 0), color.new(color.gray, 70)), linewidth=2)
    hline(overbought_tresh, title='Overbought Threshold')
    hline(0, title='0 Line')
    hline(oversold_tresh, title='Oversold Threshold')
    if signal > overbought_tresh and histA_IsDown and (order_direction != 'Long Only'):
        if sell_counter >= cool_down_period:
            label.new(bar_index, signal, text='🔴', style=label.style_label_down, color=color.new('#F9396A'), textcolor=color.new('#FFFFFF'))
            if enable_backtest:
                strategy.entry('Sell', strategy.short, comment='Open Short Position')
            sell_counter = 0
            buy_counter = cool_down_period
        else:
            sell_counter = sell_counter + 1
    elif signal < oversold_tresh and histB_IsUp and (order_direction != 'Short Only'):
        if buy_counter >= cool_down_period:
            label.new(bar_index, signal, text='🟢', style=label.style_label_up, color=color.new('#9CFF87'))
            if enable_backtest:
                strategy.entry('Buy', strategy.long, comment='Open Long Position')
            buy_counter = 0
            sell_counter = cool_down_period
        else:
            buy_counter = buy_counter + 1
    if enable_backtest:
        if signal > overbought_tresh and strategy.opentrades.size(strategy.opentrades - 1) > 0:
            strategy.close('Buy', qty_percent=100, comment='Close Long Position')
            label.new(bar_index, signal, text='Close', style=label.style_label_down, color=color.new('#F9396A'), textcolor=color.new('#FFFFFF'))
            buy_counter = cool_down_period
        elif signal < oversold_tresh and strategy.opentrades.size(strategy.opentrades - 1) < 0:
            strategy.close('Sell', qty_percent=100, comment='Close Short Position')
            label.new(bar_index, signal, text='Close', style=label.style_label_up, color=color.new('#9CFF87'))
            sell_counter = cool_down_period
    if signal < overbought_tresh:
        sell_counter = cool_down_period
    if signal > oversold_tresh:
        buy_counter = cool_down_period


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
