"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    close, color, fill, high, input, location, low, na, open, plot,
    plotshape, script, shape, size, strategy, ta
)
from pynecore.types import Persistent, PersistentSeries

main_group: str = "Fib Sensitivity"
atr_sl_finder_group: str = "ATR SL Finder"
trade_execution_group: str = "Strategy Execution"


@script.strategy("Fibonacci Trend Reversals", overlay=True, process_orders_on_close=True, commission_value=0.055, initial_capital=1000)
def main(
    sensitivity_input=input.float(title='Sensitive', step=1, defval=18, group=main_group),
    atrlength=input.int(title='Length', defval=14, minval=1, group=atr_sl_finder_group),
    smoothing=input.string(title='Smoothing', defval='RMA', options=('RMA', 'SMA', 'EMA', 'WMA'), group=atr_sl_finder_group),
    m=input(3.5, 'Multiplier', group=atr_sl_finder_group),
    tradeDirection=input.string("Both", "Trade Direction", options=("Long Only", "Short Only", "Both"), group=trade_execution_group, tooltip="Select if you want this strategy to run only Long or Only Short positions, or Both"),
    exitStrategy=input.string("ATR", "Stoploss Strategy", options=("ATR", "Fixed Percent", "Trend Switch"), group=trade_execution_group, tooltip="Choose what type of SL setting you want, ATR for dynamic or Fixed Percent for uniform SLs or Trend Switch for following and existing on Fibonacci Trend Reversal"),
    SLPercent=input.float(1, "Stoploss Percent (%)", group=trade_execution_group, tooltip="This will only be used if you selected 'Fixed Percent' as your Stoploss Strategy, if not, disregard"),
    risk_reward_ratio=input.float(2, "Risk Reward Ratio", group=trade_execution_group),
    partialTp=input.bool(True, "Use Partial Take Profit", tooltip="Enable this if you want to exit 50% of your position when half point of your Risk Reward is reached.", group=trade_execution_group)
):
    rsi_group: str = "RSI"
    is_long_trend_started: Persistent[bool] = False
    is_short_trend_started: Persistent[bool] = False
    is_trend_change: Persistent[bool] = False
    is_long_trend: PersistentSeries[bool] = False
    is_short_trend: Persistent[bool] = False
    can_long: Persistent[bool] = False
    can_short: Persistent[bool] = False

    sensitivity = sensitivity_input
    sensitivity *= 10

    high_line = ta.highest(high, cast_int(sensitivity))
    low_line = ta.lowest(low, cast_int(sensitivity))
    channel_range = high_line - low_line
    fib_236 = high_line - channel_range * 0.236
    fib_5 = high_line - channel_range * 0.5
    fib_786 = high_line - channel_range * 0.786
    imba_trend_line = fib_5

    percentile_13H = ta.percentile_nearest_rank(high, 13, 75)
    percentile_21H = ta.percentile_nearest_rank(high, 21, 75)
    percentile_34H = ta.percentile_nearest_rank(high, 34, 75)
    percentile_55H = ta.percentile_nearest_rank(high, 55, 75)
    percentile_89H = ta.percentile_nearest_rank(high, 89, 75)

    percentile_13L = ta.percentile_nearest_rank(low, 13, 25)
    percentile_21L = ta.percentile_nearest_rank(low, 21, 25)
    percentile_34L = ta.percentile_nearest_rank(low, 34, 25)
    percentile_55L = ta.percentile_nearest_rank(low, 55, 25)
    percentile_89L = ta.percentile_nearest_rank(low, 89, 25)

    highest_high = ta.percentile_nearest_rank(high, 144, 75)
    lowest_low = ta.percentile_nearest_rank(low, 144, 25)

    trendBull1 = percentile_13H > highest_high
    trendBull2 = percentile_21H > highest_high
    trendBull3 = percentile_34H > highest_high
    trendBull4 = percentile_55H > highest_high
    trendBull5 = percentile_89H > highest_high
    trendBull6 = percentile_13L > highest_high
    trendBull7 = percentile_21L > highest_high
    trendBull8 = percentile_34L > highest_high
    trendBull9 = percentile_55L > highest_high
    trendBull10 = percentile_89L > highest_high

    trendBear1 = percentile_13H < lowest_low
    trendBear2 = percentile_21H < lowest_low
    trendBear3 = percentile_34H < lowest_low
    trendBear4 = percentile_55H < lowest_low
    trendBear5 = percentile_89H < lowest_low
    trendBear6 = percentile_13L < lowest_low
    trendBear7 = percentile_21L < lowest_low
    trendBear8 = percentile_34L < lowest_low
    trendBear9 = percentile_55L < lowest_low
    trendBear10 = percentile_89L < lowest_low

    countBull = (1 if trendBull1 else 0) + (1 if trendBull2 else 0) + (1 if trendBull3 else 0) + (1 if trendBull4 else 0) + (1 if trendBull5 else 0) + (1 if trendBull6 else 0) + (1 if trendBull7 else 0) + (1 if trendBull8 else 0) + (1 if trendBull9 else 0) + (1 if trendBull10 else 0)

    countBear = (1 if trendBear1 else 0) + (1 if trendBear2 else 0) + (1 if trendBear3 else 0) + (1 if trendBear4 else 0) + (1 if trendBear5 else 0) + (1 if trendBear6 else 0) + (1 if trendBear7 else 0) + (1 if trendBear8 else 0) + (1 if trendBear9 else 0) + (1 if trendBear10 else 0)

    weakBullCount = (1 if percentile_13L < highest_high and percentile_13L > lowest_low else 0) + (1 if percentile_21L < highest_high and percentile_21L > lowest_low else 0) + (1 if percentile_34L < highest_high and percentile_34L > lowest_low else 0) + (1 if percentile_55L < highest_high and percentile_55L > lowest_low else 0) + (1 if percentile_89L < highest_high and percentile_89L > lowest_low else 0)

    weakBearCount = (1 if percentile_13H > lowest_low and percentile_13H < highest_high else 0) + (1 if percentile_21H > lowest_low and percentile_21H < highest_high else 0) + (1 if percentile_34H > lowest_low and percentile_34H < highest_high else 0) + (1 if percentile_55H > lowest_low and percentile_55H < highest_high else 0) + (1 if percentile_89H > lowest_low and percentile_89H < highest_high else 0)

    bullStrength = 10 * (countBull + 0.5 * weakBullCount - 0.5 * weakBearCount - countBear)
    bearStrength = 10 * (countBear + 0.5 * weakBearCount - 0.5 * weakBullCount - countBull)

    currentTrendValue = bullStrength - bearStrength

    tsot_bullish = currentTrendValue > 0
    tsot_bearish = currentTrendValue < 0

    can_long = close >= imba_trend_line and open < imba_trend_line and (not is_long_trend) and tsot_bullish
    can_short = close <= imba_trend_line and open > imba_trend_line and (not is_short_trend) and tsot_bearish

    if can_long:
        is_long_trend = True
        is_short_trend = False
        is_long_trend_started = False if is_long_trend_started else True
    elif can_short:
        is_short_trend = True
        is_long_trend = False
        is_short_trend_started = False if is_short_trend_started else True
    else:
        is_trend_change = False
        can_long = False
        can_short = False
        is_short_trend_started = False
        is_long_trend_started = False

    is_trend_change = is_short_trend_started or is_long_trend_started
    plotshape(imba_trend_line if is_long_trend and is_long_trend_started else na, title='Long', style=shape.triangleup, location=location.belowbar, color=color.blue, size=size.small)
    plotshape(imba_trend_line if is_short_trend and is_short_trend_started else na, title='Short', style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small)
    plot(imba_trend_line, color=color.blue if is_long_trend[1] else color.red, linewidth=1)
    src1 = high
    src2 = low
    def ma_function(source, length):
        __block_result__ = na
        if smoothing == 'RMA':
            __block_result__ = ta.rma(source, length)
        else:
            __block_result_1__ = na
            if smoothing == 'SMA':
                __block_result_1__ = ta.sma(source, length)
            else:
                __block_result_2__ = na
                if smoothing == 'EMA':
                    __block_result_2__ = ta.ema(source, length)
                else:
                    __block_result_2__ = ta.wma(source, length)
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    x = ma_function(ta.tr(True), atrlength) * m + src1
    x2 = src2 - ma_function(ta.tr(True), atrlength) * m

    p1 = plot(x, title='ATR Short Stop Loss', color=color.new('#FFFFFF18'))
    p2 = plot(x2, title='ATR Long Stop Loss', color=color.new('#FFFFFF18'))

    allowReversePosition: bool = True

    enterLong = can_long and (tradeDirection == 'Long Only' or tradeDirection == 'Both')
    enterShort = can_short and (tradeDirection == 'Short Only' or tradeDirection == 'Both')

    plotMarkers_long: Persistent[bool] = False
    firstTPHit_long: Persistent[bool] = False
    sl_long: Persistent[float] = na(float)
    breakEven_long: Persistent[float] = na(float)
    tp1_long: Persistent[float] = na(float)
    tp2_long: Persistent[float] = na(float)
    entryPrice_long: Persistent[float] = na(float)
    inLongPosition: Persistent[bool] = False

    plotMarkers_short: Persistent[bool] = False
    firstTPHit_short: Persistent[bool] = False
    sl_short: Persistent[float] = na(float)
    breakEven_short: Persistent[float] = na(float)
    tp1_short: Persistent[float] = na(float)
    tp2_short: Persistent[float] = na(float)
    entryPrice_short: Persistent[float] = na(float)
    inShortPosition: Persistent[bool] = False

    if exitStrategy != 'Trend Switch':
        if inLongPosition and can_short and allowReversePosition:
            strategy.close('Long', 'Reversing Long to Short')
            inLongPosition = False
        elif inShortPosition and can_long and allowReversePosition:
            strategy.close('Short', 'Reversing Short to Long')
            inShortPosition = False

    if exitStrategy == 'ATR':
        if enterLong:
            entryPrice_long = close
            sl_long = x2
            risk = entryPrice_long - sl_long
            tp1_long = entryPrice_long + risk_reward_ratio * risk / 2
            tp2_long = entryPrice_long + risk_reward_ratio * risk
            breakEven_long = entryPrice_long + entryPrice_long * 0.0005
            strategy.entry('Long', strategy.long)
            if not partialTp:
                strategy.exit('Exit Long', 'Long', limit=tp2_long, stop=sl_long)
            else:
                strategy.exit('TP 1 Long', 'Long', limit=tp1_long, qty_percent=50)
                strategy.exit('TP 2 Long', 'Long', limit=tp2_long, qty_percent=50)
            firstTPHit_long = False
            inLongPosition = True

        if enterShort:
            entryPrice_short = close
            sl_short = x
            risk = sl_short - entryPrice_short
            tp1_short = entryPrice_short - risk_reward_ratio * risk / 2
            tp2_short = entryPrice_short - risk_reward_ratio * risk
            breakEven_short = entryPrice_short - entryPrice_short * 0.0005
            strategy.entry('Short', strategy.short)
            if not partialTp:
                strategy.exit('Exit Short', 'Short', limit=tp2_short, stop=sl_short)
            else:
                strategy.exit('TP 1 Short', 'Short', limit=tp1_short, qty_percent=50)
                strategy.exit('TP 2 Short', 'Short', limit=tp2_short, qty_percent=50)
            firstTPHit_short = False
            inShortPosition = True

    if exitStrategy == 'Trend Switch':
        if enterLong and (not inLongPosition):
            strategy.close('Short', 'Switching Trend, Closing any Short Position')
            strategy.entry('Long', strategy.long)

        if enterShort and (not inShortPosition):
            strategy.close('Long', 'Switching Trend, Closing any Long Position')
            strategy.entry('Short', strategy.short)

    if exitStrategy == 'Fixed Percent':
        if enterLong and (not inLongPosition):
            entryPrice_long = close
            sl_long = close * (1 - SLPercent / 100)
            risk = entryPrice_long - sl_long
            tp1_long = entryPrice_long + risk_reward_ratio * risk / 2
            tp2_long = entryPrice_long + risk_reward_ratio * risk
            breakEven_long = entryPrice_long + entryPrice_long * 0.0005
            strategy.entry('Long', strategy.long)
            if not partialTp:
                strategy.exit('Exit Long', 'Long', limit=tp2_long, stop=sl_long)
            else:
                strategy.exit('TP 1 Long', 'Long', limit=tp1_long, qty_percent=50)
                strategy.exit('TP 2 Long', 'Long', limit=tp2_long, qty_percent=50)
            firstTPHit_long = False
            inLongPosition = True

        if enterShort and (not inShortPosition):
            entryPrice_short = close
            sl_short = close * (1 + SLPercent / 100)
            risk = sl_short - entryPrice_short
            tp1_short = entryPrice_short - risk_reward_ratio * risk / 2
            tp2_short = entryPrice_short - risk_reward_ratio * risk
            breakEven_short = entryPrice_short - entryPrice_short * 0.0005
            strategy.entry('Short', strategy.short)
            if not partialTp:
                strategy.exit('Exit Short', 'Short', limit=tp2_short, stop=sl_short)
            else:
                strategy.exit('TP 1 Short', 'Short', limit=tp1_short, qty_percent=50)
                strategy.exit('TP 2 Short', 'Short', limit=tp2_short, qty_percent=50)
            firstTPHit_short = False
            inShortPosition = True

    if inLongPosition and partialTp:
        if high >= tp1_long and (not firstTPHit_long):
            sl_long = breakEven_long
        elif low <= sl_long and (not firstTPHit_long):
            strategy.close('Long', 'SL long')
            inLongPosition = False
        elif low <= breakEven_long and firstTPHit_long:
            strategy.close('Long', 'BE Long')
            inLongPosition = False

    if inShortPosition and partialTp:
        if low <= tp1_short and (not firstTPHit_short):
            firstTPHit_short = True
            sl_short = breakEven_short
        elif high >= sl_short and (not firstTPHit_short):
            strategy.close('Short', 'SL Short')
            inShortPosition = False
        elif high >= breakEven_short and firstTPHit_short:
            strategy.close('Short', 'BE Short')
            inShortPosition = False

    if strategy.position_size == 0:
        plotMarkers_long = False
        plotMarkers_short = False
    if strategy.position_size > 0:
        plotMarkers_long = True
        plotMarkers_short = False
    elif strategy.position_size < 0:
        plotMarkers_long = False
        plotMarkers_short = True

    longEntryMarker = plot(entryPrice_long if plotMarkers_long else na, 'Entry Marker L', color=na)
    longSLMarker = plot(sl_long if plotMarkers_long else na, 'SL Marker L', color=color.new('#FF000050'), linewidth=1, style=plot.style_linebr)
    longTP1Marker = plot(tp1_long if plotMarkers_long else na, 'TP1 Marker L', color=color.new('#00FF0850'), linewidth=1, style=plot.style_linebr)
    longTP2Marker = plot(tp2_long if plotMarkers_long else na, 'TP2 Marker L', color=color.new('#1100FF50'), linewidth=1, style=plot.style_linebr)

    shortEntryMarker = plot(entryPrice_short if plotMarkers_short else na, 'Entry Marker S', color=na)
    shortSLMarker = plot(sl_short if plotMarkers_short else na, 'SL Marker S', color=color.new('#FF000050'), linewidth=1, style=plot.style_linebr)
    shortTP1Marker = plot(tp1_short if plotMarkers_short else na, 'TP1 Marker S', color=color.new('#00FF0850'), linewidth=1, style=plot.style_linebr)
    shortTP2Marker = plot(tp2_short if plotMarkers_short else na, 'TP2 Marker S', color=color.new('#1100FF50'), linewidth=1, style=plot.style_linebr)

    fill(plot1=longEntryMarker, plot2=longSLMarker, title='Long SL BG Fill', color=color.new('#B2283320'))
    fill(plot1=longEntryMarker, plot2=longTP2Marker, title='Long TP BG Fill', color=color.new('#08998120'))
    fill(plot1=shortEntryMarker, plot2=shortSLMarker, title='Short SL BG Fill', color=color.new('#B2283320'))
    fill(plot1=shortEntryMarker, plot2=shortTP2Marker, title='Short TP BG Fill', color=color.new('#08998120'))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
