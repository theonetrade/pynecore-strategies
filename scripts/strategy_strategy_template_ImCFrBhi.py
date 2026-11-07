"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    close, color, input, na, plot, script, strategy, syminfo, ta, time,
    timestamp
)


@script.strategy(title='My New Strategy', initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, pyramiding=0, currency='USD', overlay=True, margin_long=0, margin_short=0, close_by_id=True)
def main(
    enable_long_strategy=input.bool(True, title='Enable Long Strategy', group='SL/TP For Long Strategy', inline='1'),
    long_stoploss_value=input.float(defval=50, title='Stoploss %', minval=0.1, group='SL/TP For Long Strategy', inline='2'),
    long_takeprofit_value=input.float(defval=50, title='Take Profit %', minval=0.1, group='SL/TP For Long Strategy', inline='2'),
    enable_short_strategy=input.bool(True, title='Enable Short Strategy', group='SL/TP For Short Strategy', inline='3'),
    short_stoploss_value=input.float(defval=50, title='Stoploss %', minval=0.1, group='SL/TP For Short Strategy', inline='4'),
    short_takeprofit_value=input.float(defval=50, title='Take Profit %', minval=0.1, group='SL/TP For Short Strategy', inline='4'),
    start_date=input.int(title='Start Date', defval=1, minval=1, maxval=31, group='Date Range', inline='1'),
    end_date=input.int(title='End Date', defval=1, minval=1, maxval=31, group='Date Range', inline='1'),
    start_month=input.int(title='Start Month', defval=1, minval=1, maxval=12, group='Date Range', inline='2'),
    end_month=input.int(title='End Month', defval=1, minval=1, maxval=12, group='Date Range', inline='2'),
    start_year=input.int(title='Start Year', defval=1804, minval=1800, maxval=3000, group='Date Range', inline='3'),
    end_year=input.int(title='End Year', defval=2077, minval=1800, maxval=3000, group='Date Range', inline='3')
):
    long_stoploss_percentage = close * (long_stoploss_value / 100) / syminfo.mintick
    long_takeprofit_percentage = close * (long_takeprofit_value / 100) / syminfo.mintick
    short_stoploss_percentage = close * (short_stoploss_value / 100) / syminfo.mintick
    short_takeprofit_percentage = close * (short_takeprofit_value / 100) / syminfo.mintick
    long_stoploss_price = strategy.position_avg_price * (1 - long_stoploss_value / 100)
    long_takeprofit_price = strategy.position_avg_price * (1 + long_takeprofit_value / 100)
    short_stoploss_price = strategy.position_avg_price * (1 + short_stoploss_value / 100)
    short_takeprofit_price = strategy.position_avg_price * (1 - short_takeprofit_value / 100)
    plot(long_stoploss_price if enable_long_strategy and (not enable_short_strategy) else na, color=color.new(color.new('#FF0000'), 0), style=plot.style_linebr, linewidth=2, title='Long SL Level')
    plot(long_takeprofit_price if enable_long_strategy and (not enable_short_strategy) else na, color=color.new(color.new('#008000'), 0), style=plot.style_linebr, linewidth=2, title='Long TP Level')
    plot(short_stoploss_price if enable_short_strategy and (not enable_long_strategy) else na, color=color.new(color.new('#FF0000'), 0), style=plot.style_linebr, linewidth=2, title='Short SL Level')
    plot(short_takeprofit_price if enable_short_strategy and (not enable_long_strategy) else na, color=color.new(color.new('#008000'), 0), style=plot.style_linebr, linewidth=2, title='Short TP Level')
    in_date_range = time >= timestamp(syminfo.timezone, start_year, start_month, start_date, 0, 0) and time < timestamp(syminfo.timezone, end_year, end_month, end_date, 0, 0)
    rsi = ta.rsi(close, 14)
    rsi_over_sold = rsi < 30
    rsi_over_bought = rsi > 70
    buy_signal = rsi_over_sold
    sell_signal = rsi_over_bought
    if buy_signal and in_date_range and (enable_long_strategy == True):
        if buy_signal:
            strategy.entry('Long', strategy.long, alert_message='Open Long Position')
        strategy.exit('Long  SL/TP', from_entry='Long', loss=long_stoploss_percentage, profit=long_takeprofit_percentage, alert_message='Your Long SL/TP Limit As Been Triggered.')
        if sell_signal:
            strategy.close('Long', alert_message='Close Long Position')
    if sell_signal and in_date_range and (enable_short_strategy == True):
        if sell_signal:
            strategy.entry('Short', strategy.short, alert_message='Open Short Position')
        strategy.exit('Short SL/TP', from_entry='Short', loss=short_stoploss_percentage, profit=short_takeprofit_percentage, alert_message='Your Short SL/TP Limit As Been Triggered.')
        if buy_signal:
            strategy.close('Short', alert_message='Close Short Position')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
