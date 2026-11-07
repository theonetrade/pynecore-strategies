"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from enum import StrEnum as Enum
from pynecore.core.pine_method import method_call
from pynecore.core.series import inline_series
from pynecore.lib import (
    bar_index, bgcolor, close, color, display, high, input, label, low, math,
    na, nz, plot, script, strategy, syminfo, ta, timestamp, yloc
)
from pynecore.types import Color, Persistent, PersistentSeries
import lib.jason5480.chrono_utils.v7 as chr


class PlacementMethod(Enum):
    perc = 'PERC'
    atr = 'ATR'
    rr = 'RR'


class Trailing(Enum):
    tp = 'TP'
    on = 'ON'
    off = 'OFF'


@script.strategy(title='Trailing Take Profit Trailing Stop Loss', shorttitle='TTPTSL', overlay=True, pyramiding=0, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=100000, max_lines_count=150, max_labels_count=300)
def main(
    __input_0__=input.bool(defval=False, title='From     ', inline='From Date', group='Filters', display=display.data_window),
    __input_1__=input.time(defval=timestamp('01 Jan 2023 00:00'), title='​', inline='From Date', group='Filters', display=display.data_window),
    __input_2__=input.bool(defval=False, title='To       ', inline='To Date', group='Filters', display=display.data_window),
    __input_3__=input.time(defval=timestamp('01 Jan 2024 00:00'), title='​​', inline='To Date', group='Filters', display=display.data_window),
    __input_4__=input.enum(defval=chr.Timezone.Exchange, title='Timezones Ref->Chart', inline='Timezone', group='Filters', display=display.data_window),
    __input_5__=input.enum(defval=chr.Timezone.Exchange, title='->', tooltip='The Timezone Ref is the reference timezone that is used for the "From" and "To" datetime window settings. The Timezone Chart is the timezone to convert into. WARNING! The chart timezone setting should always match with the actual chart timezone on the bottom right corner of your chart.', inline='Timezone', group='Filters', display=display.data_window),
    longDealsEnabled=input.bool(defval=True, title='Long Deals', inline='Long/Short Deals', group='Strategy'),
    shortDealsEnabled=input.bool(defval=True, title='Short Deals', tooltip='Enable long/short deals. An open signal will be emited when the long/short start deal conditions are met. If this option is un-checked you will not enter into long/short positions.', inline='Long/Short Deals', group='Strategy'),
    fastMALen=input.int(defval=21, title='Fast/Slow SMA Length', minval=1, inline='MA Length', group='Strategy'),
    slowMALen=input.int(defval=49, title='', minval=1, tooltip='How many candles back to calculte the fast/slow SMA.', inline='MA Length', group='Strategy'),
    atrLength=input.int(defval=14, title='ATR Length', minval=1, tooltip='How many previous candles to use for the ATR calculation.', group='General'),
    stopLossMethod=input.enum(defval=PlacementMethod.perc, title='Stop Loss Method', options=(PlacementMethod.perc, PlacementMethod.atr), tooltip='The method to calculate the Stop Loss (percentagewise, based on initial ATR or based on ATR changing over time).', group='Stop Loss - Target'),
    __input_12__=input.float(defval=7.5, title='Long/Short Stop Loss %', minval=0.05, maxval=100, step=0.05, inline='Trailing Stop Loss Perc', group='Stop Loss - Target'),
    __input_13__=input.float(defval=7.5, title='', minval=0.05, maxval=100, step=0.05, tooltip='The percentage of the price decrease/increase to set the Stop Loss price target for long/short positions.', inline='Trailing Stop Loss Perc', group='Stop Loss - Target'),
    longStopLossAtrMul=input.float(defval=3.0, title='ATR Long/Short Mul ', minval=0.1, step=0.1, inline='Trailing Stop Loss ATR Multiplier', group='Stop Loss - Target'),
    shortStopLossAtrMul=input.float(defval=3.0, title='', minval=0.1, step=0.1, tooltip='ATR multiplier to be used for the long/short Stop Loss.', inline='Trailing Stop Loss ATR Multiplier', group='Stop Loss - Target'),
    stopLossTrailingEnabled=input.enum(defval=Trailing.tp, title='Enable Trailing', tooltip='Enable the trailing for Stop Loss when Take Profit order is executed (TP) or from the start of the entry order (ON) or not at all (OFF).', group='Stop Loss - Trailing'),
    breakEvenEnabled=input.bool(defval=False, title='Break Even', tooltip='When Take Profit price target is hit, move the Stop Loss to the entry price (or to a more strict price defined by the Stop Loss %/ATR Multiplier).', group='Stop Loss - Trailing'),
    takeProfitQuantityPerc=input.float(defval=50, title='Take Profit Quantity %', minval=0.0, maxval=100, step=1.0, tooltip='The percentage of the position that will be withdrawn when the take profit price target is reached.', group='Take Profit - Quantity'),
    takeProfitMethod=input.enum(defval=PlacementMethod.perc, title='Take Profit Method', tooltip='The method to calculate the Take Profit price.', group='Take Profit - Target'),
    __input_20__=input.float(defval=10.0, title='Long/Short Take Profit %', minval=0.05, step=0.05, inline='Take Profit Perc', group='Take Profit - Target'),
    __input_21__=input.float(defval=10.0, title='', minval=0.05, step=0.05, tooltip='The percentage of the price increase/decrease to set the take profit price target for long/short positions.', inline='Take Profit Perc', group='Take Profit - Target'),
    longTakeProfitAtrMul=input.float(defval=9.0, title='ATR Long/Short Mul ', minval=0.1, step=0.1, inline='Take Profit ATR Multiplier', group='Take Profit - Target'),
    shortTakeProfitAtrMul=input.float(defval=9.0, title='', minval=0.1, step=0.1, tooltip='ATR multiplier to be used for the long/short Take Profit.', inline='Take Profit ATR Multiplier', group='Take Profit - Target'),
    longRiskRewardRatio=input.float(defval=1.5, title='Long/Short RR Ratio ', minval=0.1, step=0.1, inline='Risk Reward Ratio', group='Take Profit - Target'),
    shortRiskRewardRatio=input.float(defval=1.5, title='', minval=0.1, step=0.1, tooltip='The Risk/Reward Ratio to be used for the long/short Take Profit based on the Stop Loss Price.', inline='Risk Reward Ratio', group='Take Profit - Target'),
    takeProfitTrailingEnabled=input.bool(defval=True, title='Enable Trailing', tooltip='Enable or disable the trailing for take profit.', group='Take Profit - Trailing'),
    distanceMethod=input.enum(defval=PlacementMethod.perc, title='Distance Method', options=(PlacementMethod.perc, PlacementMethod.atr), tooltip='The method to calculate the Distance for the Trailing Take Profit.', group='Take Profit - Trailing'),
    __input_28__=input.float(defval=1.0, title='Distance %', minval=0.01, maxval=100, step=0.05, tooltip='The percentage wise step to be used for following the price, when the take profit target is reached.', group='Take Profit - Trailing'),
    distanceAtrMul=input.float(defval=1.0, title='Distance ATR Mul', minval=0.01, step=0.05, tooltip='Multiplier to be used on the initial entrys` ATR to calculate the step for following the price, when the take profit target is reached.', group='Take Profit - Trailing')
):
    dateTimeWindow: Persistent[chr.DateTimeWindow] = method_call('init', chr.DateTimeWindow.new(), fromDateTime=__input_1__ if __input_0__ else na, toDateTime=__input_3__ if __input_2__ else na, refTimezone=chr.exTimezone(__input_4__), chTimezone=chr.exTimezone(__input_5__))

    dateFilterApproval: bool = method_call('is_bar_included', dateTimeWindow)

    bgcolor(color=na if dateFilterApproval else color.new(color.new('#FF0000'), 95), offset=1, title='Filter')

    fastMA: float = ta.sma(close, fastMALen)
    slowMA: float = ta.sma(close, slowMALen)

    crossover: bool = ta.crossover(fastMA, slowMA)
    crossunder: bool = ta.crossunder(fastMA, slowMA)

    openLongPosition: bool = longDealsEnabled and dateFilterApproval and crossover
    openShortPosition: bool = shortDealsEnabled and dateFilterApproval and crossunder

    closeLongPosition: bool = longDealsEnabled and crossunder
    closeShortPosition: bool = shortDealsEnabled and crossover

    plot(series=fastMA, title='Fast SMA', color=color.yellow, linewidth=1, style=plot.style_line)
    plot(series=slowMA, title='Slow SMA', color=color.orange, linewidth=1, style=plot.style_line)

    validOpenLongPosition: bool = openLongPosition and (not strategy.opentrades.size(strategy.opentrades - 1) > 0)
    validOpenShortPosition: bool = openShortPosition and (not strategy.opentrades.size(strategy.opentrades - 1) < 0)

    longIsActive: bool = validOpenLongPosition or (strategy.opentrades.size(strategy.opentrades - 1) > 0 and (not closeLongPosition))
    shortIsActive: bool = validOpenShortPosition or (strategy.opentrades.size(strategy.opentrades - 1) < 0 and (not closeShortPosition))

    TEXT_COLOR: Color = color.new(color.white, 0)
    if validOpenLongPosition:
        label.new(x=bar_index, y=na, text='Open', yloc=yloc.belowbar, color=color.new('#2962FF'), style=label.style_label_up, textcolor=TEXT_COLOR)
    if validOpenShortPosition:
        label.new(x=bar_index, y=na, text='Close', yloc=yloc.abovebar, color=color.new('#FF1744'), style=label.style_label_down, textcolor=TEXT_COLOR)

    longTrailingTakeProfitExecuted: PersistentSeries[bool] = False
    shortTrailingTakeProfitExecuted: PersistentSeries[bool] = False

    openAtr: float = ta.valuewhen(validOpenLongPosition or validOpenShortPosition, ta.atr(atrLength), 0)

    longTrailingStopLossPerc = __input_12__ / 100
    shortTrailingStopLossPerc = __input_13__ / 100

    def getLongStopLossPrice(baseSrc):
        __block_result__ = na
        __switch__ = stopLossMethod
        if __switch__ == PlacementMethod.perc:
            __block_result__ = baseSrc * (1 - longTrailingStopLossPerc)
        elif __switch__ == PlacementMethod.atr:
            __block_result__ = baseSrc - longStopLossAtrMul * openAtr
        else:
            __block_result__ = na
        return __block_result__

    longTakeProfitTrailingEnabled: bool = stopLossTrailingEnabled == Trailing.on or (stopLossTrailingEnabled == Trailing.tp and longTrailingTakeProfitExecuted)

    longStopLossPrice: PersistentSeries[float] = na(float)
    __block_result_1__ = na
    if longIsActive:
        __block_result_2__ = na
        if validOpenLongPosition:
            __block_result_2__ = getLongStopLossPrice(close)
        else:
            stopPrice = getLongStopLossPrice(high if longTakeProfitTrailingEnabled else strategy.opentrades.entry_price(strategy.opentrades - 1))
            stopPrice = math.max(stopPrice, strategy.opentrades.entry_price(strategy.opentrades - 1)) if breakEvenEnabled and longTrailingTakeProfitExecuted else stopPrice
            __block_result_2__ = math.max(stopPrice, nz(longStopLossPrice[1]))
        __block_result_1__ = __block_result_2__
    else:
        __block_result_1__ = na
    longStopLossPrice = __block_result_1__

    def getShortStopLossPrice(baseSrc):
        __block_result_3__ = na
        __switch__ = stopLossMethod
        if __switch__ == PlacementMethod.perc:
            __block_result_3__ = baseSrc * (1 + shortTrailingStopLossPerc)
        elif __switch__ == PlacementMethod.atr:
            __block_result_3__ = baseSrc + shortStopLossAtrMul * openAtr
        else:
            __block_result_3__ = na
        return __block_result_3__

    shortTakeProfitTrailingEnabled: bool = stopLossTrailingEnabled == Trailing.on or (stopLossTrailingEnabled == Trailing.tp and shortTrailingTakeProfitExecuted)

    shortStopLossPrice: PersistentSeries[float] = na(float)
    __block_result_4__ = na
    if shortIsActive:
        __block_result_5__ = na
        if validOpenShortPosition:
            __block_result_5__ = getShortStopLossPrice(close)
        else:
            stopPrice = getShortStopLossPrice(low if shortTakeProfitTrailingEnabled else strategy.opentrades.entry_price(strategy.opentrades - 1))
            stopPrice = math.min(stopPrice, strategy.opentrades.entry_price(strategy.opentrades - 1)) if breakEvenEnabled and shortTrailingTakeProfitExecuted else stopPrice
            __block_result_5__ = math.min(stopPrice, nz(shortStopLossPrice[1], 999999.9))
        __block_result_4__ = __block_result_5__
    else:
        __block_result_4__ = na
    shortStopLossPrice = __block_result_4__

    STOP_LOSS_COLOR: Color = color.new(color.maroon, 0)
    plot(series=longStopLossPrice, title='Long Stop Loss', color=STOP_LOSS_COLOR, linewidth=1, style=plot.style_linebr, offset=1)
    plot(series=shortStopLossPrice, title='Short Stop Loss', color=STOP_LOSS_COLOR, linewidth=1, style=plot.style_linebr, offset=1)
    longTakeProfitPerc = __input_20__ / 100
    shortTakeProfitPerc = __input_21__ / 100
    distancePerc = __input_28__ / 100

    def getLongTakeProfitPrice():
        __block_result_6__ = na
        __switch__ = takeProfitMethod
        if __switch__ == PlacementMethod.perc:
            __block_result_6__ = close * (1 + longTakeProfitPerc)
        elif __switch__ == PlacementMethod.atr:
            __block_result_6__ = close + longTakeProfitAtrMul * openAtr
        elif __switch__ == PlacementMethod.rr:
            __block_result_6__ = close + longRiskRewardRatio * (close - getLongStopLossPrice(close))
        else:
            __block_result_6__ = na
        return __block_result_6__

    def getLongTakeProfitPerc():
        return (close - getLongTakeProfitPrice()) / close

    longTakeProfitPrice: PersistentSeries[float] = na(float)
    __block_result_7__ = na
    if longIsActive and (not longTrailingTakeProfitExecuted):
        __block_result_8__ = na
        if validOpenLongPosition:
            __block_result_8__ = getLongTakeProfitPrice()
        else:
            __block_result_8__ = nz(longTakeProfitPrice[1], getLongTakeProfitPrice())
        __block_result_7__ = __block_result_8__
    else:
        __block_result_7__ = na
    longTakeProfitPrice = __block_result_7__

    longTrailingTakeProfitExecuted = strategy.opentrades.size(strategy.opentrades - 1) > 0 and (longTrailingTakeProfitExecuted[1] or strategy.opentrades.size(strategy.opentrades - 1) < inline_series(strategy.opentrades.size(strategy.opentrades - 1), 1) or (inline_series(strategy.opentrades.size(strategy.opentrades - 1), 1) == 0 and high >= longTakeProfitPrice))

    __block_result_9__ = na
    __switch__ = distanceMethod
    if __switch__ == PlacementMethod.perc:
        __block_result_9__ = longTakeProfitPrice * distancePerc / syminfo.mintick
    elif __switch__ == PlacementMethod.atr:
        __block_result_9__ = distanceAtrMul * openAtr / syminfo.mintick
    else:
        __block_result_9__ = na
    longTrailingTakeProfitStepTicks = __block_result_9__

    def getShortTakeProfitPrice():
        __block_result_10__ = na
        __switch__ = takeProfitMethod
        if __switch__ == PlacementMethod.perc:
            __block_result_10__ = close * (1 - shortTakeProfitPerc)
        elif __switch__ == PlacementMethod.atr:
            __block_result_10__ = close - shortTakeProfitAtrMul * openAtr
        elif __switch__ == PlacementMethod.rr:
            __block_result_10__ = close - shortRiskRewardRatio * (getShortStopLossPrice(close) - close)
        else:
            __block_result_10__ = na
        return __block_result_10__

    def getShortTakeProfitPerc():
        return (getShortTakeProfitPrice() - close) / close

    shortTakeProfitPrice: PersistentSeries[float] = na(float)
    __block_result_11__ = na
    if shortIsActive and (not shortTrailingTakeProfitExecuted):
        __block_result_12__ = na
        if validOpenShortPosition:
            __block_result_12__ = getShortTakeProfitPrice()
        else:
            __block_result_12__ = nz(shortTakeProfitPrice[1], getShortTakeProfitPrice())
        __block_result_11__ = __block_result_12__
    else:
        __block_result_11__ = na
    shortTakeProfitPrice = __block_result_11__

    shortTrailingTakeProfitExecuted = strategy.opentrades.size(strategy.opentrades - 1) < 0 and (shortTrailingTakeProfitExecuted[1] or strategy.opentrades.size(strategy.opentrades - 1) > inline_series(strategy.opentrades.size(strategy.opentrades - 1), 1) or (inline_series(strategy.opentrades.size(strategy.opentrades - 1), 1) == 0 and low <= shortTakeProfitPrice))

    __block_result_13__ = na
    __switch__ = distanceMethod
    if __switch__ == PlacementMethod.perc:
        __block_result_13__ = shortTakeProfitPrice * distancePerc / syminfo.mintick
    elif __switch__ == PlacementMethod.atr:
        __block_result_13__ = distanceAtrMul * openAtr / syminfo.mintick
    else:
        __block_result_13__ = na
    shortTrailingTakeProfitStepTicks = __block_result_13__

    TAKE_PROFIT_COLOR: Color = color.new(color.teal, 0)
    plot(series=longTakeProfitPrice, title='Long Take Profit', color=TAKE_PROFIT_COLOR, linewidth=1, style=plot.style_linebr, offset=1)
    plot(series=shortTakeProfitPrice, title='Short Take Profit', color=TAKE_PROFIT_COLOR, linewidth=1, style=plot.style_linebr, offset=1)

    if closeLongPosition:
        strategy.close(id='Long Entry', comment='Close Long', alert_message='Long: Closed at market price')

    if closeShortPosition:
        strategy.close(id='Short Entry', comment='Close Short', alert_message='Short: Closed at market price')

    if validOpenLongPosition:
        strategy.entry(id='Long Entry', direction=strategy.long, alert_message='Long(' + syminfo.ticker + '): Started')

    if longIsActive:
        strategy.exit(id='Long Take Profit / Stop Loss', from_entry='Long Entry', qty_percent=takeProfitQuantityPerc, limit=na if takeProfitTrailingEnabled else longTakeProfitPrice, stop=longStopLossPrice, trail_price=longTakeProfitPrice if takeProfitTrailingEnabled else na, trail_offset=longTrailingTakeProfitStepTicks if takeProfitTrailingEnabled else na, alert_profit='Long(' + syminfo.ticker + '): Take Profit executed', alert_loss='Long(' + syminfo.ticker + '): Stop Loss executed', alert_trailing='Long(' + syminfo.ticker + '): Trailing Take Profit executed')
        strategy.exit(id='Long Stop Loss', from_entry='Long Entry', stop=longStopLossPrice, alert_loss='Long(' + syminfo.ticker + '): Stop Loss executed')

    if validOpenShortPosition:
        strategy.entry(id='Short Entry', direction=strategy.short, alert_message='Short(' + syminfo.ticker + '): Started')

    if shortIsActive:
        strategy.exit(id='Short Take Profit / Stop Loss', from_entry='Short Entry', qty_percent=takeProfitQuantityPerc, limit=na if takeProfitTrailingEnabled else shortTakeProfitPrice, stop=shortStopLossPrice, trail_price=shortTakeProfitPrice if takeProfitTrailingEnabled else na, trail_offset=shortTrailingTakeProfitStepTicks if takeProfitTrailingEnabled else na, alert_profit='Short(' + syminfo.ticker + '): Take Profit executed', alert_loss='Short(' + syminfo.ticker + '): Stop Loss executed', alert_trailing='Short(' + syminfo.ticker + '): Trailing Take Profit executed')
        strategy.exit(id='Short Stop Loss', from_entry='Short Entry', stop=shortStopLossPrice, alert_loss='Short(' + syminfo.ticker + '): Stop Loss executed')

    plot(series=strategy.opentrades.entry_price(strategy.opentrades - 1), title='Position', color=color.gray, linewidth=1, style=plot.style_linebr)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
