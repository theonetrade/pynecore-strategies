"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    bar_index, bgcolor, close, color, display, input, label, na, nz, plot,
    script, strategy, syminfo, ta, timestamp, yloc
)
from pynecore.types import Persistent, PersistentSeries
import lib.jason5480.chrono_utils.v7 as chr


@script.strategy(title='Trailing Take Profit', shorttitle='TTP', overlay=True, pyramiding=0, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=100000, max_lines_count=150, max_labels_count=150)
def main(
    __input_0__=input.bool(defval=False, title='From     ', inline='From Date', group='Filters', display=display.data_window),
    __input_1__=input.time(defval=timestamp('01 Jan 2023 00:00'), title='​', inline='From Date', group='Filters', display=display.data_window),
    __input_2__=input.bool(defval=False, title='To       ', inline='To Date', group='Filters', display=display.data_window),
    __input_3__=input.time(defval=timestamp('01 Jan 2024 00:00'), title='​​', inline='To Date', group='Filters', display=display.data_window),
    __input_4__=input.enum(defval=chr.Timezone.Exchange, title='Timezones Ref->Chart', inline='Timezone', group='Filters', display=display.data_window),
    __input_5__=input.enum(defval=chr.Timezone.Exchange, title='->', tooltip='The Timezone Ref is the reference timezone that is used for the "From" and "To" datetime window settings. The Timezone Chart is the timezone to convert into. WARNING! The chart timezone setting should always match with the actual chart timezone on the bottom right corner of your chart.', inline='Timezone', group='Filters', display=display.data_window),
    fastMALen=input.int(defval=21, title='Fast/Slow SMA Length', minval=1, inline='MA Length', group='Strategy'),
    slowMALen=input.int(defval=49, title='', minval=1, tooltip='How many candles back to calculte the fast/slow SMA.', inline='MA Length', group='Strategy'),
    __input_8__=input.float(defval=7.0, title='Take Profit %', minval=0.05, step=0.05, tooltip='The percentage of the price increase to set the take profit price target.', group='Take Profit'),
    takeProfitTrailingEnabled=input.bool(defval=True, title='Enable Trailing', tooltip='Enable or disable the trailing for take profit. WARNING! This feature will repaint. Make sure you use it with "Bar Magnifier" and "Deep Backtesting" for realistic backtest results', group='Take Profit'),
    __input_10__=input.float(defval=1.0, title='  Trailing Distance %', minval=0.01, maxval=100, step=0.01, tooltip='The distance as a percentage of the take profit price to keep from the high price after the target is reached when trailing.', group='Take Profit')
):
    dateTimeWindow: Persistent[chr.DateTimeWindow] = method_call('init', chr.DateTimeWindow.new(), fromDateTime=__input_1__ if __input_0__ else na, toDateTime=__input_3__ if __input_2__ else na, refTimezone=chr.exTimezone(__input_4__), chTimezone=chr.exTimezone(__input_5__))

    dateFilterApproval: bool = method_call('is_bar_included', dateTimeWindow)

    bgcolor(color=na if dateFilterApproval else color.new(color.new('#FF0000'), 95), offset=1, title='Filter')

    fastMA: float = ta.sma(close, fastMALen)
    slowMA: float = ta.sma(close, slowMALen)

    openLongPosition: bool = ta.crossover(fastMA, slowMA) and dateFilterApproval

    plot(series=fastMA, title='Fast SMA', color=color.yellow, linewidth=1, style=plot.style_line)
    plot(series=slowMA, title='Slow SMA', color=color.orange, linewidth=1, style=plot.style_line)

    validOpenLongPosition: bool = openLongPosition and strategy.opentrades.size(strategy.opentrades - 1) <= 0

    longIsActive: bool = validOpenLongPosition or strategy.opentrades.size(strategy.opentrades - 1) > 0

    if validOpenLongPosition:
        label.new(x=bar_index, y=na, text='Open', yloc=yloc.belowbar, color=color.new('#2962FF'), style=label.style_label_up, textcolor=color.white)

    longTakeProfitPerc = __input_8__ / 100
    trailingTakeProfitDistancePerc = __input_10__ / 100

    longTakeProfitPrice: PersistentSeries[float] = na(float)
    __block_result__ = na
    if validOpenLongPosition:
        __block_result__ = close * (1 + longTakeProfitPerc)
    elif longIsActive:
        __block_result__ = nz(longTakeProfitPrice[1], close * (1 + longTakeProfitPerc))
    else:
        __block_result__ = na
    longTakeProfitPrice = __block_result__

    longTrailingTakeProfitStepTicks = longTakeProfitPrice * trailingTakeProfitDistancePerc / syminfo.mintick

    plot(series=longTakeProfitPrice, title='Long Take Profit', color=color.teal, linewidth=1, style=plot.style_linebr, offset=1)

    if validOpenLongPosition:
        strategy.entry(id='Long Entry', direction=strategy.long, alert_message='Long(' + syminfo.ticker + '): Started')

    if longIsActive:
        strategy.exit(id='Long Take Profit', from_entry='Long Entry', limit=na if takeProfitTrailingEnabled else longTakeProfitPrice, trail_price=longTakeProfitPrice if takeProfitTrailingEnabled else na, trail_offset=longTrailingTakeProfitStepTicks if takeProfitTrailingEnabled else na, alert_profit='Long(' + syminfo.ticker + '): Take Profit executed', alert_trailing='Long(' + syminfo.ticker + '): Trailing Take Profit executed')

    plot(series=strategy.opentrades.entry_price(strategy.opentrades - 1), title='Position', color=color.gray, linewidth=1, style=plot.style_linebr)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
