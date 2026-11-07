"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, currency, fill, high, input, low, na, plot,
    script, strategy, ta
)
from pynecore.types import NA


@script.strategy(title='Auto Fib Golden Pocket Band - Autofib Moving Average', shorttitle='Auto Fib Golden Pocket Band', overlay=True, pyramiding=15, process_orders_on_close=True, calc_on_every_tick=True, initial_capital=10000, currency=currency.USD, default_qty_value=100, default_qty_type=strategy.percent_of_equity, commission_type=strategy.commission.percent, commission_value=0.05, slippage=2, margin_long=0, margin_short=0, close_by_id=True)
def main(
    enable_StrongBand_Bull=input.bool(title='enable Upper Bullish Band . . . Fib Level', defval=True, group='══════ Strong Trend Levels ══════', inline='0'),
    select_StrongBand_Fib_Bull=input.float(0.236, title='     ', options=(-0.272, 0, 0.236, 0.382, 0.5, 0.618, 0.702, 0.71, 0.786, 0.83, 0.886, 1, 1.272), group='══════ Strong Trend Levels ══════', inline='0'),
    enable_StrongBand_Bear=input.bool(title='enable Lower Bearish Band . . . Fib Level', defval=False, group='══════ Strong Trend Levels ══════', inline='1'),
    select_StrongBand_Fib_Bear=input.float(0.382, '', options=(-0.272, 0, 0.236, 0.382, 0.5, 0.618, 0.702, 0.71, 0.786, 0.83, 0.886, 1, 1.272), group='══════ Strong Trend Levels ══════', inline='1'),
    StrongBand_Lookback=input.int(title='Pivot Look Back', minval=1, defval=400, group='══════ Strong Trend Levels ══════', inline='2'),
    StrongBand_EmaLen=input.int(title='Fib EMA Length', minval=1, defval=120, group='══════ Strong Trend Levels ══════', inline='2'),
    enable_MiddleBand_Bull=input.bool(title='enable Middle Bullish Band . . . Fib Level', defval=True, group='══════ Regular Trend Levels ══════', inline='0'),
    select_MiddleBand_Fib_Bull=input.float(0.618, '', options=(-0.272, 0, 0.236, 0.382, 0.5, 0.6, 0.618, 0.702, 0.71, 0.786, 0.83, 0.886, 1, 1.272), group='══════ Regular Trend Levels ══════', inline='0'),
    enable_MiddleBand_Bear=input.bool(title='enable Middle Bearish Band . . . Fib Level', defval=True, group='══════ Regular Trend Levels ══════', inline='1'),
    select_MiddleBand_Fib_Bear=input.float(0.382, '', options=(-0.272, 0, 0.236, 0.382, 0.5, 0.618, 0.702, 0.71, 0.786, 0.83, 0.886, 1, 1.272), group='══════ Regular Trend Levels ══════', inline='1'),
    MiddleBand_Lookback=input.int(title='Pivot Look Back', minval=1, defval=900, group='══════ Regular Trend Levels ══════', inline='2'),
    MiddleBand_EmaLen=input.int(title='Fib EMA Length', minval=1, defval=400, group='══════ Regular Trend Levels ══════', inline='2'),
    enable_SidewaysBand_Bull=input.bool(title='enable Lower Bullish Band . . . Fib Level', defval=True, group='══════ Sideways Trend Levels ══════', inline='0'),
    select_SidewaysBand_Fib_Bull=input.float(0.6, '', options=(-0.272, 0, 0.236, 0.382, 0.5, 0.6, 0.618, 0.702, 0.71, 0.786, 0.83, 0.886, 1, 1.272), group='══════ Sideways Trend Levels ══════', inline='0'),
    enable_SidewaysBand_Bear=input.bool(title='enable Upper Bearish Band . . . Fib Level', defval=True, group='══════ Sideways Trend Levels ══════', inline='1'),
    select_SidewaysBand_Fib_Bear=input.float(0.5, '', options=(-0.272, 0, 0.236, 0.382, 0.5, 0.618, 0.702, 0.71, 0.786, 0.83, 0.886, 1, 1.272), group='══════ Sideways Trend Levels ══════', inline='1'),
    SidewaysBand_Lookback=input.int(title='Pivot Look Back', minval=1, defval=4000, group='══════ Sideways Trend Levels ══════', inline='2'),
    SidewaysBand_EmaLen=input.int(title='Fib EMA Length', minval=1, defval=150, group='══════ Sideways Trend Levels ══════', inline='2'),
    enableSL=input.bool(True, title='enable Stop Loss', group='══════════ Stop Loss Settings ══════════'),
    whichSL=input.string(defval='low/high as SL', title='SL based on static % or based on the low/high', options=('low/high as SL', 'static % as SL'), group='══════════ Stop Loss Settings ══════════'),
    whichOffset=input.string(defval='% as offset', title='choose offset from the low/high', options=('$ as offset', '% as offset'), group='Stop Loss at the low/high'),
    __input_21__=input.float(1.4, title='SL Offset from the Low/high in %', group='Stop Loss at the low/high'),
    lowDBuffer=input.float(100, title='SL Offset from the Low/high in $', group='Stop Loss at the low/high'),
    SlLowLookback=input.int(title='SL lookback for Low/high', defval=5, minval=1, maxval=50, group='Stop Loss at the low/high'),
    __input_24__=input.float(0.5, title='Long Stop Loss in %', group='static % Stop Loss', inline='Input 1'),
    __input_25__=input.float(0.5, title='Short Stop Loss in %', group='static % Stop Loss', inline='Input 1'),
    __input_26__=input.float(4, title='Long Take Profit in %', group='Take Profit', inline='Input 1'),
    __input_27__=input.float(1.6, title='Short Take Profit in %', group='Take Profit', inline='Input 1'),
    selectalertFreq=input.string(defval='once per bar close', title='Alert Options', options=('once per bar', 'once per bar close', 'all'), group='═══════════ alert settings ═══════════'),
    BuyAlertMessage=input.string(defval='Bullish Divergence detected, put your SL @', title='Buy Alert Message', group='═══════════ alert settings ═══════════'),
    enableSlMessage=input.bool(True, title='enable Stop Loss Value at the end of "buy Alert message"', group='═══════════ alert settings ═══════════'),
    AfterSLMessage=input.string(defval='', title='Buy Alert message after SL Value', group='═══════════ alert settings ═══════════')
):
    isBelow_StrongBand_Bull: bool = True
    isBelow_StrongBand_Bear: bool = True
    StrongBand_Price_of_Low = NA(float)
    StrongBand_Price_of_High = NA(float)
    StrongBand_Bear_Fib_Price = NA(float)
    StrongBand_Bull_Fib_Price = NA(float)
    isBelow_MiddleBand_Bull: bool = True
    isBelow_MiddleBand_Bear: bool = True
    MiddleBand_Price_of_Low = NA(float)
    MiddleBand_Price_of_High = NA(float)
    MiddleBand_Bear_Fib_Price = NA(float)
    MiddleBand_Bull_Fib_Price = NA(float)
    isBelow_SidewaysBand_Bull: bool = True
    isBelow_SidewaysBand_Bear: bool = True
    SidewaysBand_Price_of_Low = NA(float)
    SidewaysBand_Price_of_High = NA(float)
    SidewaysBand_Bear_Fib_Price = NA(float)
    SidewaysBand_Bull_Fib_Price = NA(float)
    if enable_StrongBand_Bull:
        StrongBand_Price_of_High = ta.highest(high, StrongBand_Lookback)
        StrongBand_Price_of_Low = ta.lowest(low, StrongBand_Lookback)
        StrongBand_Bull_Fib_Price = (StrongBand_Price_of_High - StrongBand_Price_of_Low) * (1 - select_StrongBand_Fib_Bull) + StrongBand_Price_of_Low
        isBelow_StrongBand_Bull = StrongBand_Bull_Fib_Price > ta.lowest(low, 2) or not enable_StrongBand_Bull
    if enable_StrongBand_Bear:
        StrongBand_Price_of_High = ta.highest(high, StrongBand_Lookback)
        StrongBand_Price_of_Low = ta.lowest(low, StrongBand_Lookback)
        StrongBand_Bear_Fib_Price = (StrongBand_Price_of_High - StrongBand_Price_of_Low) * (1 - select_StrongBand_Fib_Bear) + StrongBand_Price_of_Low
        isBelow_StrongBand_Bear = StrongBand_Bear_Fib_Price < ta.highest(low, 2) or not enable_StrongBand_Bear
    if enable_MiddleBand_Bull:
        MiddleBand_Price_of_High = ta.highest(high, MiddleBand_Lookback)
        MiddleBand_Price_of_Low = ta.lowest(low, MiddleBand_Lookback)
        MiddleBand_Bull_Fib_Price = (MiddleBand_Price_of_High - MiddleBand_Price_of_Low) * (1 - select_MiddleBand_Fib_Bull) + MiddleBand_Price_of_Low
        isBelow_MiddleBand_Bull = MiddleBand_Bull_Fib_Price > ta.lowest(low, 2) or not enable_MiddleBand_Bull
    if enable_MiddleBand_Bear:
        MiddleBand_Price_of_High = ta.highest(high, MiddleBand_Lookback)
        MiddleBand_Price_of_Low = ta.lowest(low, MiddleBand_Lookback)
        MiddleBand_Bear_Fib_Price = (MiddleBand_Price_of_High - MiddleBand_Price_of_Low) * (1 - select_MiddleBand_Fib_Bear) + MiddleBand_Price_of_Low
        isBelow_MiddleBand_Bear = MiddleBand_Bear_Fib_Price < ta.highest(low, 2) or not enable_MiddleBand_Bear
    if enable_SidewaysBand_Bull:
        SidewaysBand_Price_of_High = ta.highest(high, SidewaysBand_Lookback)
        SidewaysBand_Price_of_Low = ta.lowest(low, SidewaysBand_Lookback)
        SidewaysBand_Bull_Fib_Price = (SidewaysBand_Price_of_High - SidewaysBand_Price_of_Low) * (1 - select_SidewaysBand_Fib_Bull) + SidewaysBand_Price_of_Low
        isBelow_SidewaysBand_Bull = SidewaysBand_Bull_Fib_Price > ta.lowest(low, 2) or not enable_SidewaysBand_Bull
    if enable_SidewaysBand_Bear:
        SidewaysBand_Price_of_High = ta.highest(high, SidewaysBand_Lookback)
        SidewaysBand_Price_of_Low = ta.lowest(low, SidewaysBand_Lookback)
        SidewaysBand_Bear_Fib_Price = (SidewaysBand_Price_of_High - SidewaysBand_Price_of_Low) * (1 - select_SidewaysBand_Fib_Bear) + SidewaysBand_Price_of_Low
        isBelow_SidewaysBand_Bear = SidewaysBand_Bear_Fib_Price < ta.highest(low, 2) or not enable_SidewaysBand_Bear
    StrongBand_current_Trend_EMA = NA(float)
    StrongBand_Bull_EMA = ta.ema(StrongBand_Bull_Fib_Price, StrongBand_EmaLen)
    StrongBand_Bear_EMA = ta.ema(StrongBand_Bear_Fib_Price, StrongBand_EmaLen)
    change_1 = ta.change(StrongBand_Bear_EMA)
    StrongBand_Ema_in_Uptrend = ta.change(StrongBand_Bull_EMA) > 0 or change_1 > 0
    change_2 = ta.change(StrongBand_Bear_EMA)
    StrongBand_Ema_Sideways = ta.change(StrongBand_Bull_EMA) == 0 or change_2 == 0
    change_3 = ta.change(StrongBand_Bear_EMA)
    StrongBand_Ema_in_Downtrend = ta.change(StrongBand_Bull_EMA) < 0 or change_3 < 0
    if StrongBand_Ema_in_Uptrend or StrongBand_Ema_Sideways:
        StrongBand_current_Trend_EMA = StrongBand_Bull_EMA
    if StrongBand_Ema_in_Downtrend:
        StrongBand_current_Trend_EMA = StrongBand_Bear_EMA
    MiddleBand_current_Trend_EMA = NA(float)
    MiddleBand_Bull_EMA = ta.ema(MiddleBand_Bull_Fib_Price, MiddleBand_EmaLen)
    MiddleBand_Bear_EMA = ta.ema(MiddleBand_Bear_Fib_Price, MiddleBand_EmaLen)
    change_4 = ta.change(MiddleBand_Bear_EMA)
    MiddleBand_Ema_in_Uptrend = ta.change(MiddleBand_Bull_EMA) > 0 or change_4 > 0
    change_5 = ta.change(MiddleBand_Bear_EMA)
    MiddleBand_Ema_Sideways = ta.change(MiddleBand_Bull_EMA) == 0 or change_5 == 0
    change_6 = ta.change(MiddleBand_Bear_EMA)
    MiddleBand_Ema_in_Downtrend = ta.change(MiddleBand_Bull_EMA) < 0 or change_6 < 0
    if MiddleBand_Ema_in_Uptrend or MiddleBand_Ema_Sideways:
        MiddleBand_current_Trend_EMA = MiddleBand_Bull_EMA
    if MiddleBand_Ema_in_Downtrend:
        MiddleBand_current_Trend_EMA = MiddleBand_Bear_EMA
    SidewaysBand_current_Trend_EMA = NA(float)
    SidewaysBand_Bull_EMA = ta.ema(SidewaysBand_Bull_Fib_Price, SidewaysBand_EmaLen)
    SidewaysBand_Bear_EMA = ta.ema(SidewaysBand_Bear_Fib_Price, SidewaysBand_EmaLen)
    change_7 = ta.change(SidewaysBand_Bear_EMA)
    SidewaysBand_Ema_in_Uptrend = ta.change(SidewaysBand_Bull_EMA) > 0 or change_7 > 0
    change_8 = ta.change(SidewaysBand_Bear_EMA)
    SidewaysBand_Ema_Sideways = ta.change(SidewaysBand_Bull_EMA) == 0 or change_8 == 0
    change_9 = ta.change(SidewaysBand_Bear_EMA)
    SidewaysBand_Ema_in_Downtrend = ta.change(SidewaysBand_Bull_EMA) < 0 or change_9 < 0
    if SidewaysBand_Ema_in_Uptrend or SidewaysBand_Ema_Sideways:
        SidewaysBand_current_Trend_EMA = SidewaysBand_Bull_EMA
    if SidewaysBand_Ema_in_Downtrend:
        SidewaysBand_current_Trend_EMA = SidewaysBand_Bear_EMA
    all_Fib_Emas_Trending = StrongBand_Ema_in_Uptrend and MiddleBand_Ema_in_Uptrend and SidewaysBand_Ema_in_Uptrend
    all_Fib_Emas_Downtrend = MiddleBand_Ema_in_Downtrend and StrongBand_Ema_in_Downtrend and SidewaysBand_Ema_in_Downtrend
    all_Fib_Emas_Sideways = MiddleBand_Ema_Sideways and StrongBand_Ema_Sideways and SidewaysBand_Ema_Sideways
    all_Fib_Emas_Trend_or_Sideways = MiddleBand_Ema_Sideways or StrongBand_Ema_Sideways or SidewaysBand_Ema_Sideways or ((StrongBand_Ema_in_Uptrend or MiddleBand_Ema_in_Uptrend or SidewaysBand_Ema_in_Uptrend) and (not (MiddleBand_Ema_in_Downtrend or StrongBand_Ema_in_Downtrend or SidewaysBand_Ema_in_Downtrend)))
    allFibsUpAndDownTrend = (MiddleBand_Ema_in_Downtrend or StrongBand_Ema_in_Downtrend or SidewaysBand_Ema_in_Downtrend) and (MiddleBand_Ema_Sideways or SidewaysBand_Ema_Sideways or StrongBand_Ema_Sideways or StrongBand_Ema_in_Uptrend or MiddleBand_Ema_in_Uptrend or SidewaysBand_Ema_in_Uptrend)
    Middle_and_Sideways_Emas_Trending = MiddleBand_Ema_in_Uptrend and SidewaysBand_Ema_in_Uptrend
    Middle_and_Sideways_Fib_Emas_Downtrend = MiddleBand_Ema_in_Downtrend and SidewaysBand_Ema_in_Downtrend
    Middle_and_Sideways_Fib_Emas_Sideways = MiddleBand_Ema_Sideways and SidewaysBand_Ema_Sideways
    Middle_and_Sideways_Fib_Emas_Trend_or_Sideways = MiddleBand_Ema_Sideways or SidewaysBand_Ema_Sideways or ((MiddleBand_Ema_in_Uptrend or SidewaysBand_Ema_in_Uptrend) and (not (MiddleBand_Ema_in_Downtrend or SidewaysBand_Ema_in_Downtrend)))
    Middle_and_Sideways_UpAndDownTrend = (MiddleBand_Ema_in_Downtrend or SidewaysBand_Ema_in_Downtrend) and (MiddleBand_Ema_Sideways or SidewaysBand_Ema_Sideways or MiddleBand_Ema_in_Uptrend or SidewaysBand_Ema_in_Uptrend)
    UpperBand_Ema_Color = color.lime if all_Fib_Emas_Trend_or_Sideways else color.red if all_Fib_Emas_Downtrend else color.white if allFibsUpAndDownTrend else na
    MiddleBand_Ema_Color = color.lime if Middle_and_Sideways_Fib_Emas_Trend_or_Sideways else color.red if Middle_and_Sideways_Fib_Emas_Downtrend else color.white if Middle_and_Sideways_UpAndDownTrend else na
    SidewaysBand_Ema_Color = color.lime if SidewaysBand_Ema_in_Uptrend else color.red if SidewaysBand_Ema_in_Downtrend else color.white if SidewaysBand_Ema_in_Downtrend and (SidewaysBand_Ema_Sideways or SidewaysBand_Ema_in_Uptrend) else na
    plotStrong_Ema = plot(StrongBand_current_Trend_EMA, color=UpperBand_Ema_Color, title='Strong Trend')
    plotMiddle_Ema = plot(MiddleBand_current_Trend_EMA, color=MiddleBand_Ema_Color, title='Normal Trend')
    plotSideways_Ema = plot(SidewaysBand_current_Trend_EMA, color=SidewaysBand_Ema_Color, title='Sidewaysd')
    Strong_Middle_fillcolor = color.new(color.green, 90)
    if all_Fib_Emas_Trend_or_Sideways:
        Strong_Middle_fillcolor = color.new(color.green, 90)
    if all_Fib_Emas_Downtrend:
        Strong_Middle_fillcolor = color.new(color.red, 90)
    if allFibsUpAndDownTrend:
        Strong_Middle_fillcolor = color.new(color.white, 90)
    Middle_Sideways_fillcolor = color.new(color.green, 90)
    if Middle_and_Sideways_Fib_Emas_Trend_or_Sideways:
        Middle_Sideways_fillcolor = color.new(color.green, 90)
    if Middle_and_Sideways_Fib_Emas_Downtrend:
        Middle_Sideways_fillcolor = color.new(color.red, 90)
    if Middle_and_Sideways_UpAndDownTrend:
        Middle_Sideways_fillcolor = color.new(color.white, 90)
    fill(plotStrong_Ema, plotMiddle_Ema, color=Strong_Middle_fillcolor, title='fib band background')
    fill(plotMiddle_Ema, plotSideways_Ema, color=Middle_Sideways_fillcolor, title='fib band background')
    StrongBand_Price_was_below_Bull_level = ta.lowest(low, 1) < StrongBand_current_Trend_EMA
    StrongBand_Price_is_above_Bull_level = close > StrongBand_current_Trend_EMA
    StronBand_Price_Average_above_Bull_Level = ta.ema(low, 10) > StrongBand_current_Trend_EMA
    StrongBand_Low_isnt_toLow = ta.lowest(StrongBand_current_Trend_EMA, 15) - ta.lowest(low, 15) < close * 0.005
    barssince_1 = ta.barssince(StrongBand_Ema_in_Downtrend)
    StronBand_Trend_isnt_fresh = ta.barssince(StrongBand_Ema_in_Downtrend) > 50 or na(barssince_1)
    MiddleBand_Price_was_below_Bull_level = ta.lowest(low, 1) < MiddleBand_current_Trend_EMA
    MiddleBand_Price_is_above_Bull_level = close > MiddleBand_current_Trend_EMA
    MiddleBand_Price_Average_above_Bull_Level = ta.ema(close, 20) > MiddleBand_current_Trend_EMA
    MiddleBand_Low_isnt_toLow = ta.lowest(MiddleBand_current_Trend_EMA, 10) - ta.lowest(low, 10) < close * 0.0065
    barssince_2 = ta.barssince(MiddleBand_Ema_in_Downtrend)
    MiddleBand_Trend_isnt_fresh = ta.barssince(MiddleBand_Ema_in_Downtrend) > 50 or na(barssince_2)
    SidewaysBand_Price_was_below_Bull_level = ta.lowest(low, 1) < SidewaysBand_current_Trend_EMA
    SidewaysBand_Price_is_above_Bull_level = close > SidewaysBand_current_Trend_EMA
    SidewaysBand_Price_Average_above_Bull_Level = ta.ema(low, 80) > SidewaysBand_current_Trend_EMA
    SidewaysBand_Low_isnt_toLow = ta.lowest(SidewaysBand_current_Trend_EMA, 150) - ta.lowest(low, 150) < close * 0.0065
    barssince_3 = ta.barssince(SidewaysBand_Ema_in_Downtrend)
    SidewaysBand_Trend_isnt_fresh = ta.barssince(SidewaysBand_Ema_in_Downtrend) > 50 or na(barssince_3)
    StrongBand_Buy_Alert = StronBand_Trend_isnt_fresh and StrongBand_Low_isnt_toLow and StronBand_Price_Average_above_Bull_Level and StrongBand_Price_was_below_Bull_level and StrongBand_Price_is_above_Bull_level and all_Fib_Emas_Trend_or_Sideways
    MiddleBand_Buy_Alert = MiddleBand_Trend_isnt_fresh and MiddleBand_Low_isnt_toLow and MiddleBand_Price_Average_above_Bull_Level and MiddleBand_Price_was_below_Bull_level and MiddleBand_Price_is_above_Bull_level and Middle_and_Sideways_Fib_Emas_Trend_or_Sideways
    SidewaysBand_Buy_Alert = SidewaysBand_Trend_isnt_fresh and SidewaysBand_Low_isnt_toLow and SidewaysBand_Price_Average_above_Bull_Level and SidewaysBand_Price_was_below_Bull_level and SidewaysBand_Price_is_above_Bull_level and (SidewaysBand_Ema_Sideways or (SidewaysBand_Ema_in_Uptrend and (not SidewaysBand_Ema_in_Downtrend)))
    StrongBand_Price_was_above_Bear_level = ta.highest(high, 1) > StrongBand_current_Trend_EMA
    StrongBand_Price_is_below_Bear_level = close < StrongBand_current_Trend_EMA
    StronBand_Price_Average_below_Bear_Level = ta.sma(high, 10) < StrongBand_current_Trend_EMA
    StrongBand_High_isnt_to_High = ta.highest(high, 15) - ta.highest(StrongBand_current_Trend_EMA, 15) < close * 0.005
    StrongBand_Bear_Trend_isnt_fresh = ta.barssince(StrongBand_Ema_in_Uptrend) > 50
    MiddleBand_Price_was_above_Bear_level = ta.highest(high, 1) > MiddleBand_current_Trend_EMA
    MiddleBand_Price_is_below_Bear_level = close < MiddleBand_current_Trend_EMA
    MiddleBand_Price_Average_below_Bear_Level = ta.sma(high, 9) < MiddleBand_current_Trend_EMA
    MiddleBand_High_isnt_to_High = ta.highest(high, 10) - ta.highest(MiddleBand_current_Trend_EMA, 10) < close * 0.0065
    MiddleBand_Bear_Trend_isnt_fresh = ta.barssince(MiddleBand_Ema_in_Uptrend) > 50
    SidewaysBand_Price_was_above_Bear_level = ta.highest(high, 1) > SidewaysBand_current_Trend_EMA
    SidewaysBand_Price_is_below_Bear_level = close < SidewaysBand_current_Trend_EMA
    SidewaysBand_Price_Average_below_Bear_Level = ta.sma(high, 20) < SidewaysBand_current_Trend_EMA
    SidewaysBand_High_isnt_to_High = ta.highest(high, 20) - ta.highest(SidewaysBand_current_Trend_EMA, 15) < close * 0.0065
    SidewaysBand_Bear_Trend_isnt_fresh = ta.barssince(SidewaysBand_Ema_in_Uptrend) > 50
    StrongBand_Sell_Alert = StronBand_Price_Average_below_Bear_Level and StrongBand_High_isnt_to_High and StrongBand_Bear_Trend_isnt_fresh and StrongBand_Price_was_above_Bear_level and StrongBand_Price_is_below_Bear_level and all_Fib_Emas_Downtrend and (not all_Fib_Emas_Trend_or_Sideways)
    MiddleBand_Sell_Alert = MiddleBand_Price_Average_below_Bear_Level and MiddleBand_High_isnt_to_High and MiddleBand_Bear_Trend_isnt_fresh and MiddleBand_Price_was_above_Bear_level and MiddleBand_Price_is_below_Bear_level and Middle_and_Sideways_Fib_Emas_Downtrend and (not Middle_and_Sideways_Fib_Emas_Trend_or_Sideways)
    SidewaysBand_Sell_Alert = SidewaysBand_Price_Average_below_Bear_Level and SidewaysBand_High_isnt_to_High and SidewaysBand_Bear_Trend_isnt_fresh and SidewaysBand_Price_was_above_Bear_level and SidewaysBand_Price_is_below_Bear_level and SidewaysBand_Ema_in_Downtrend and (not (SidewaysBand_Ema_Sideways or (SidewaysBand_Ema_in_Uptrend and (not SidewaysBand_Ema_in_Downtrend))))
    lowPBuffer = __input_21__ / 100
    longSlLow = NA(float)
    shortSlLow = NA(float)
    if whichOffset == '% as offset' and whichSL == 'low/high as SL' and enableSL:
        longSlLow = ta.lowest(low, SlLowLookback) * (1 - lowPBuffer)
        shortSlLow = ta.highest(high, SlLowLookback) * (1 + lowPBuffer)
    if whichOffset == '$ as offset' and whichSL == 'low/high as SL' and enableSL:
        longSlLow = ta.lowest(low, SlLowLookback) - lowDBuffer
        shortSlLow = ta.highest(high, SlLowLookback) + lowDBuffer
    longStopLoss = __input_24__ / 100
    shortStopLoss = __input_25__ / 100
    longTakeProfit1 = __input_26__ / 100
    shortTakeProfit1 = __input_27__ / 100
    shortTrading = enable_MiddleBand_Bear or enable_StrongBand_Bear or enable_SidewaysBand_Bear
    longTrading = enable_StrongBand_Bull or enable_MiddleBand_Bull or enable_SidewaysBand_Bull
    longTP1 = strategy.position_avg_price * (1 + longTakeProfit1) if strategy.position_size > 0 else strategy.position_avg_price * (1 - longTakeProfit1) if strategy.position_size < 0 else na
    longSL = strategy.position_avg_price * (1 - longStopLoss) if strategy.position_size > 0 else strategy.position_avg_price * (1 + longStopLoss) if strategy.position_size < 0 else na
    shortTP = strategy.position_avg_price * (1 + shortTakeProfit1) if strategy.position_size > 0 else strategy.position_avg_price * (1 - shortTakeProfit1) if strategy.position_size < 0 else na
    shortSL = strategy.position_avg_price * (1 - shortStopLoss) if strategy.position_size > 0 else strategy.position_avg_price * (1 + shortStopLoss) if strategy.position_size < 0 else na
    strategy.risk.allow_entry_in(strategy.direction.all if longTrading == True and shortTrading == True else strategy.direction.long if longTrading == True else strategy.direction.short if shortTrading == True else na)
    if StrongBand_Buy_Alert:
        strategy.entry('Bull', strategy.long, comment='Upper Band Long')
    if MiddleBand_Buy_Alert:
        strategy.entry('Bull', strategy.long, comment='Lower Band Long')
    if SidewaysBand_Buy_Alert:
        strategy.entry('Bull', strategy.long, comment='Lower Band Long')
    if StrongBand_Sell_Alert:
        strategy.entry('Bear', strategy.short, comment='Upper Band Short')
    if MiddleBand_Sell_Alert:
        strategy.entry('Bear', strategy.short, comment='Lower Band Short')
    if SidewaysBand_Sell_Alert:
        strategy.entry('Bear', strategy.short, comment='Lower Band Short')
    if enableSL and whichSL == 'static % as SL':
        strategy.exit(id='longTP-SL', from_entry='Bull', limit=longTP1, stop=longSL)
        strategy.exit(id='shortTP-SL', from_entry='Bear', limit=shortTP, stop=shortSL)
    def barsSinceLastEntry():
        return bar_index - strategy.opentrades.entry_bar_index(strategy.opentrades - 1) if strategy.opentrades > 0 else na

    barssince_4 = ta.barssince(StrongBand_Buy_Alert or MiddleBand_Buy_Alert or SidewaysBand_Buy_Alert)
    barsSinceLastEntry_1 = barsSinceLastEntry()
    if enableSL and whichSL == 'low/high as SL' and (barssince_4 < 2) and (barsSinceLastEntry_1 < 2):
        strategy.exit(id='longTP-SL', from_entry='Bull', limit=longTP1, stop=longSlLow)
    barssince_5 = ta.barssince(StrongBand_Sell_Alert or MiddleBand_Sell_Alert or SidewaysBand_Sell_Alert)
    barsSinceLastEntry_2 = barsSinceLastEntry()
    if enableSL and whichSL == 'low/high as SL' and (barssince_5 < 2) and (barsSinceLastEntry_2 < 2):
        strategy.exit(id='shortTP-SL', from_entry='Bear', limit=shortTP, stop=shortSlLow)
    if not enableSL:
        strategy.exit(id='longTP-SL', from_entry='Bull', limit=longTP1)
        strategy.exit(id='shortTP-SL', from_entry='Bear', limit=shortTP)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
