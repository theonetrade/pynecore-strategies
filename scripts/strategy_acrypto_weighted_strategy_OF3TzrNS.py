"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    array, bar_index, barstate, close, color, currency, display, fill, high,
    hl2, input, location, low, math, month, na, nz, ohlc4, plot, plotchar, plotshape, position,
    script, shape, size, strategy, string, ta, table, time, timestamp, volume, year
)
from pynecore.types import NA, Persistent, Series, Table


@script.strategy(title='Acrypto - Weighted Strategy v1.4.8', overlay=True, precision=2, commission_value=0.075, commission_type=strategy.commission.percent, initial_capital=1000, currency=currency.USD, default_qty_type=strategy.percent_of_equity, default_qty_value=100, slippage=1, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    allow_longs=input.bool(True, 'Allow Longs', group='Trading type'),
    allow_shorts=input.bool(True, 'Allow Shorts', group='Trading type'),
    from_day=input.int(1, 'From Day', minval=1, maxval=31, group='DataStamp'),
    from_month=input.int(1, 'From Month', minval=1, maxval=12, group='DataStamp'),
    from_year=input.int(2021, 'From Year', minval=1980, maxval=9999, group='DataStamp'),
    to_day=input.int(1, 'To Day', minval=1, maxval=31, group='DataStamp'),
    to_month=input.int(1, 'To Month', minval=1, maxval=12, group='DataStamp'),
    to_year=input.int(9999, 'To Year', minval=2017, maxval=9999, group='DataStamp'),
    stoploss=input.bool(True, 'Stop loss', group='Stop loss'),
    movestoploss=input.string('TP-2', 'Move stop loss', options=('None', 'Percentage', 'TP-1', 'TP-2', 'TP-3'), group='Stop loss'),
    movestoploss_entry=input.bool(False, 'Move stop loss to entry', group='Stop loss'),
    __input_11__=input.float(6.0, 'Stop Loss %', minval=0, maxval=100, group='Stop loss'),
    __input_12__=input.float(20.0, 'Move stop loss factor %', group='Stop loss'),
    stop_source: Series[float] = input.source(hl2, 'Stop Source', group='Stop loss'),
    take_profits=input.bool(True, 'Take profits', group='Take Profits'),
    MAX_TP=input.int(6, 'Max number of TP', minval=1, maxval=6, group='Take Profits'),
    __input_16__=input.float(6.8, 'Long - take profits each x (%)', minval=0.0, maxval=999, step=1, group='Take Profits'),
    long_profit_qty=input.float(15, 'Long - take x (%) from open position', minval=0.0, maxval=100, step=1, group='Take Profits'),
    __input_18__=input.float(13, 'Short - take profits each x (%)', minval=0.0, maxval=999, step=1, group='Take Profits'),
    short_profit_qty=input.float(10, 'Short - take x (%) from open position', minval=0.0, maxval=100, step=1, group='Take Profits'),
    delay_macd=input.int(1, 'Candles delay MACD', minval=1, group='Delays'),
    delay_srsi=input.int(2, 'Candles delay Stoch RSI', minval=1, group='Delays'),
    delay_rsi=input.int(2, 'Candles delay RSI', minval=1, group='Delays'),
    delay_super=input.int(1, 'Candles delay Supertrend', minval=1, group='Delays'),
    delay_cross=input.int(1, 'Candles delay MA cross', minval=1, group='Delays'),
    delay_exit=input.int(7, 'Candles delay exit', minval=1, group='Delays'),
    str_0=input.bool(True, 'Strategy 0: Weighted Strategy', group='Weights'),
    weight_trigger=input.int(2, 'Weight Signal entry [0, 5]', minval=0, maxval=5, step=1, group='Weights'),
    weight_str1=input.int(1, 'Weight Strategy 1 [0, 5]', minval=0, maxval=5, step=1, group='Weights'),
    weight_str2=input.int(1, 'Weight Strategy 2 [0, 5]', minval=0, maxval=5, step=1, group='Weights'),
    weight_str3=input.int(1, 'Weight Strategy 3 [0, 5]', minval=0, maxval=5, step=1, group='Weights'),
    weight_str4=input.int(1, 'Weight Strategy 4 [0, 5]', minval=0, maxval=5, step=1, group='Weights'),
    weight_str5=input.int(1, 'Weight Strategy 5 [0, 5]', minval=0, maxval=5, step=1, group='Weights'),
    str_1=input.bool(True, 'Strategy 1: MACD', group='Strategy 1: MACD'),
    MA1_period_1=input.int(16, 'MA 1', minval=1, maxval=9999, step=1, group='Strategy 1: MACD'),
    MA1_type_1=input.string('EMA', 'MA1 Type', options=('RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'DEMA', 'TEMA', 'VWMA'), group='Strategy 1: MACD'),
    MA1_source_1: Series[float] = input.source(hl2, 'MA1 Source', group='Strategy 1: MACD'),
    MA2_period_1=input.int(36, 'MA 2', minval=1, maxval=9999, step=1, group='Strategy 1: MACD'),
    MA2_type_1=input.string('EMA', 'MA2 Type', options=('RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'DEMA', 'TEMA', 'VWMA'), group='Strategy 1: MACD'),
    MA2_source_1: Series[float] = input.source(high, 'MA2 Source', group='Strategy 1: MACD'),
    str_2=input.bool(True, 'Strategy 2: Stoch RSI', group='Strategy 2: Stoch RSI'),
    long_RSI=input.float(70, 'Exit SRSI Long (%)', minval=0.0, step=1, group='Strategy 2: Stoch RSI'),
    short_RSI=input.float(27, 'Exit SRSI Short (%)', minval=0.0, step=1, group='Strategy 2: Stoch RSI'),
    length_RSI=input.int(14, 'RSI Length', group='Strategy 2: Stoch RSI'),
    length_stoch=input.int(14, 'RSI Stochastic', group='Strategy 2: Stoch RSI'),
    smoothK=input.int(3, 'Smooth k', group='Strategy 2: Stoch RSI'),
    str_3=input.bool(True, 'Strategy 3: RSI', group='Strategy 3: RSI'),
    long_RSI2=input.float(77, 'Exit RSI Long (%)', minval=0.0, step=1, group='Strategy 3: RSI'),
    short_RSI2=input.float(30, 'Exit RSI Short (%)', minval=0.0, step=1, group='Strategy 3: RSI'),
    str_4=input.bool(True, 'Strategy 4: Supertrend', group='Strategy 4: Supertrend'),
    periods_4=input.int(2, 'ATR Period', group='Strategy 4: Supertrend'),
    source_4: Series[float] = input.source(hl2, 'Source', group='Strategy 4: Supertrend'),
    multiplier=input.float(2.4, 'ATR Multiplier', step=0.1, group='Strategy 4: Supertrend'),
    change_ATR=input.bool(True, 'Change ATR Calculation Method ?', group='Strategy 4: Supertrend'),
    str_5=input.bool(True, 'Strategy 5: MA CROSS', group='Strategy 5: MA CROSS'),
    MA1_period_5=input.int(46, 'MA 1', minval=1, maxval=9999, step=1, group='Strategy 5: MA CROSS'),
    MA1_type_5=input.string('EMA', 'MA1 Type', options=('RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'DEMA', 'TEMA', 'VWMA'), group='Strategy 5: MA CROSS'),
    MA1_source_5: Series[float] = input.source(close, 'MA1 Source', group='Strategy 5: MA CROSS'),
    MA2_period_5=input.int(82, 'MA 2', minval=1, maxval=9999, step=1, group='Strategy 5: MA CROSS'),
    MA2_type_5=input.string('EMA', 'MA2 Type', options=('RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'DEMA', 'TEMA', 'VWMA'), group='Strategy 5: MA CROSS'),
    MA2_source_5: Series[float] = input.source(close, 'MA2 Source', group='Strategy 5: MA CROSS'),
    str_6=input.bool(False, 'Close order at potential Top/Bottom', group='Potential TOP/BOTTOM'),
    top_qty=input.float(30, 'Top - take x (%) from the remaining position', minval=0.0, maxval=100, step=1, group='Potential TOP/BOTTOM'),
    bottom_qty=input.float(30, 'Bottom - take x (%) from the remaining position', minval=0.0, maxval=100, step=1, group='Potential TOP/BOTTOM'),
    source_6_top: Series[float] = input.source(close, 'TP-TOP at previous?', group='Potential TOP/BOTTOM'),
    source_6_bottom: Series[float] = input.source(close, 'TP-BOTTOM at previous?', group='Potential TOP/BOTTOM'),
    __input_66__=input.float(150, 'Trail volume Long (%)', minval=0.0, step=1, group='Potential TOP/BOTTOM'),
    __input_67__=input.float(150, 'Trail volume Short (%)', minval=0.0, step=1, group='Potential TOP/BOTTOM'),
    FLAG_SIGNALS=input.bool(True, 'Show Buy/Sell Signals ?', group='Miscellaneous'),
    FLAG_SHADOWS=input.bool(True, 'Show shadows satisfied strategies ?', group='Miscellaneous'),
    alarm_label_long=input.string('Buy', 'Label open long', group='Basic alarm system'),
    alarm_label_short=input.string('Sell', 'Label open short', group='Basic alarm system'),
    alarm_label_close_long=input.string('Close long', 'Label close long', group='Basic alarm system'),
    alarm_label_close_short=input.string('Close short', 'Label close short', group='Basic alarm system'),
    alarm_label_TP_long=input.string('TP long', 'Label Take Profit long', group='Basic alarm system'),
    alarm_label_TP_short=input.string('TP short', 'Label Take Profit short', group='Basic alarm system'),
    alarm_label_SL=input.string('SL', 'Label Stop-Loss', group='Basic alarm system'),
    show_performance=input.bool(True, 'Show Monthly Performance ?', group='Performance - credits: @QuantNomad'),
    prec=input(2, 'Return Precision', group='Performance - credits: @QuantNomad')
):
    stoploss_perc = __input_11__ * 0.01
    move_stoploss_factor = __input_12__ * 0.01 + 1
    long_profit_perc = __input_16__ * 0.01
    short_profit_perc = __input_18__ * 0.01
    long_trail_perc = __input_66__ * 0.01
    short_trail_perc = __input_67__ * 0.01
    start = timestamp(from_year, from_month, from_day, 0, 0)
    end = timestamp(to_year, to_month, to_day, 23, 59)
    FLAG_FIRST: Persistent[bool] = False
    price_stop_long: Persistent[float] = 0.0
    price_stop_short: Persistent[float] = 0.0
    profit_qty: Persistent[float] = 0.0
    profit_perc: Persistent[float] = 0.0
    nextTP: Persistent[float] = 0.0
    since_entry: Persistent[int] = 0
    since_close: Persistent[int] = 0
    if strategy.position_size > 0:
        profit_qty = long_profit_qty
        profit_perc = long_profit_perc
    elif strategy.position_size < 0:
        profit_qty = short_profit_qty
        profit_perc = short_profit_perc
    else:
        nextTP = 0.0
    def ma(MAType, MASource, MAPeriod):
        __block_result__ = na
        if MAType == 'SMA':
            __block_result__ = ta.sma(MASource, MAPeriod)
        elif MAType == 'EMA':
            __block_result__ = ta.ema(MASource, MAPeriod)
        elif MAType == 'WMA':
            __block_result__ = ta.wma(MASource, MAPeriod)
        elif MAType == 'RMA':
            __block_result__ = ta.rma(MASource, MAPeriod)
        elif MAType == 'HMA':
            __block_result__ = ta.wma(2 * ta.wma(MASource, MAPeriod / 2) - ta.wma(MASource, MAPeriod), math.round(math.sqrt(MAPeriod)))
        elif MAType == 'DEMA':
            e = ta.ema(MASource, MAPeriod)
            __block_result__ = 2 * e - ta.ema(e, MAPeriod)
        elif MAType == 'TEMA':
            e = ta.ema(MASource, MAPeriod)
            __block_result__ = 3 * (e - ta.ema(e, MAPeriod)) + ta.ema(ta.ema(e, MAPeriod), MAPeriod)
        elif MAType == 'VWMA':
            __block_result__ = ta.vwma(MASource, MAPeriod)
        return __block_result__

    def n_strategies():
        result: Persistent[float] = 0.0
        if str_1:
            result = 1.0
        if str_2:
            result = result + 1.0
        if str_3:
            result = result + 1.0
        if str_4:
            result = result + 1.0
        __block_result_1__ = na
        if str_5:
            result = result + 1.0
            __block_result_1__ = result
        return __block_result_1__

    def price_takeProfit(percentage, N):
        __block_result_2__ = na
        if strategy.position_size > 0:
            __block_result_2__ = strategy.position_avg_price * (1 + N * percentage)
        else:
            __block_result_2__ = strategy.position_avg_price * (1 - N * percentage)
        return __block_result_2__

    def weight_values(signal):
        __block_result_3__ = na
        if signal:
            weight: float = 1.0
            __block_result_3__ = weight
        else:
            weight: float = 0.0
            __block_result_3__ = weight
        return __block_result_3__

    def weight_total(signal1, signal2, signal3, signal4, signal5):
        return weight_str1 * weight_values(signal1) + weight_str2 * weight_values(signal2) + weight_str3 * weight_values(signal3) + weight_str4 * weight_values(signal4) + weight_str5 * weight_values(signal5)

    def set_alarm_label_TP():
        __block_result_4__ = na
        if strategy.position_size > 0:
            __block_result_4__ = alarm_label_TP_long
        elif strategy.position_size < 0:
            __block_result_4__ = alarm_label_TP_short
        return __block_result_4__

    def colors(type, value = 0):
        switch_var_0 = string.lower(type)
        __block_result_5__ = na
        __switch__ = switch_var_0
        if __switch__ == 'buy':
            __block_result_5__ = color.new(color.aqua, value)
        elif __switch__ == 'sell':
            __block_result_5__ = color.new(color.gray, value)
        elif __switch__ == 'TP':
            __block_result_5__ = color.new(color.aqua, value)
        elif __switch__ == 'SL':
            __block_result_5__ = color.new(color.gray, value)
        elif __switch__ == 'signal':
            __block_result_5__ = color.new(color.orange, value)
        elif __switch__ == 'profit':
            __block_result_5__ = color.new(color.teal, value)
        elif __switch__ == 'loss':
            __block_result_5__ = color.new(color.red, value)
        elif __switch__ == 'info':
            __block_result_5__ = color.new(color.white, value)
        elif __switch__ == 'highlights':
            __block_result_5__ = color.new(color.orange, value)
        return __block_result_5__

    def bars_since_entry():
        return bar_index - strategy.opentrades.entry_bar_index(0)

    def bars_since_close():
        return ta.barssince(cast_bool(ta.change(strategy.closedtrades)))

    since_entry = bars_since_entry()
    since_close = bars_since_close()
    if strategy.opentrades == 0:
        since_entry = delay_exit
    if strategy.closedtrades == 0:
        since_close = delay_exit
    MA1 = ma(MA1_type_1, MA1_source_1, MA1_period_1)
    MA2 = ma(MA2_type_1, MA2_source_1, MA2_period_1)
    MACD = MA1 - MA2
    signal = ma('SMA', MACD, 9)
    trend: Series = MACD - signal
    long: Series = MACD > signal
    short: Series = MACD < signal
    proportion = math.abs(MACD / signal)
    long_signal1 = long and long[delay_macd - 1] and (not long[delay_macd])
    short_signal1 = short and short[delay_macd - 1] and (not short[delay_macd])
    close_long1 = short and (not long[delay_macd])
    close_short1 = long and (not short[delay_macd])
    rsi = ta.rsi(close, length_RSI)
    srsi = ta.stoch(rsi, rsi, rsi, length_stoch)
    k = ma('SMA', srsi, smoothK)
    isRsiOB: Series = k >= long_RSI
    isRsiOS: Series = k <= short_RSI
    long_signal2 = isRsiOS[delay_srsi] and (not isRsiOB) and (since_entry >= delay_exit) and (since_close >= delay_exit)
    short_signal2 = isRsiOB[delay_srsi] and (not isRsiOS) and (since_entry >= delay_exit) and (since_close >= delay_exit)
    close_long2 = short_signal2
    close_short2 = long_signal2
    isRsiOB2: Series = rsi >= long_RSI2
    isRsiOS2: Series = rsi <= short_RSI2
    long_signal3 = isRsiOS2[delay_rsi] and (not isRsiOB2) and (since_entry >= delay_exit) and (since_close >= delay_exit)
    short_signal3 = isRsiOB2[delay_rsi] and (not isRsiOS2) and (since_entry >= delay_exit) and (since_close >= delay_exit)
    close_long3 = short_signal3
    close_short3 = long_signal3
    atr2 = ma('SMA', ta.tr, periods_4)
    atr = ta.atr(periods_4) if change_ATR else atr2
    up: Series = source_4 - multiplier * atr
    up1 = nz(up[1], up)
    up = math.max(up, up1) if close[1] > up1 else up
    dn: Series = source_4 + multiplier * atr
    dn1 = nz(dn[1], dn)
    dn = math.min(dn, dn1) if close[1] < dn1 else dn
    trend = 1
    trend = nz(trend[1], trend)
    trend = 1 if trend == -1 and close > dn1 else -1 if trend == 1 and close < up1 else trend
    long4 = trend == 1
    short4 = trend == -1
    long_signal4 = trend == 1 and trend[delay_super - 1] == 1 and (trend[delay_super] == -1)
    short_signal4 = trend == -1 and trend[delay_super - 1] == -1 and (trend[delay_super] == 1)
    changeCond = trend != trend[1]
    close_long4 = short_signal4
    close_short4 = short_signal4
    MA12 = ma(MA1_type_5, MA1_source_5, MA1_period_5)
    MA22 = ma(MA2_type_5, MA2_source_5, MA2_period_5)
    long5: Series = MA12 > MA22
    short5: Series = MA12 < MA22
    long_signal5 = long5 and long5[delay_cross - 1] and (not long5[delay_cross])
    short_signal5 = short5 and short5[delay_cross - 1] and (not short5[delay_cross])
    close_long5 = short5 and (not long5[delay_cross])
    close_short5 = long5 and (not short5[delay_cross])
    volumeRSI_condition = volume[2] > volume[3] and volume[2] > volume[4] and (volume[2] > volume[5])
    ma_1 = ma('SMA', volume, 20)
    condition_OB1 = isRsiOB2 and (isRsiOB or volume < ma_1 / 2) and volumeRSI_condition
    ma_2 = ma('SMA', volume, 20)
    condition_OS1 = isRsiOS2 and (isRsiOS or volume < ma_2 / 2) and volumeRSI_condition
    condition_OB2 = volume[2] / volume[1] > 1.0 + long_trail_perc and isRsiOB and volumeRSI_condition
    condition_OS2 = volume[2] / volume[1] > 1.0 + short_trail_perc and isRsiOS and volumeRSI_condition
    condition_OB3 = weight_total(MACD < signal, isRsiOB, isRsiOB2, short4, short5) >= weight_trigger
    condition_OS3 = weight_total(MACD > signal, isRsiOS, isRsiOS2, long4, long5) >= weight_trigger
    condition_OB: Series = condition_OB1 or condition_OB2
    condition_OS: Series = condition_OS1 or condition_OS2
    condition_OB_several = condition_OB[1] and condition_OB[2] or (condition_OB[1] and condition_OB[3]) or (condition_OB[1] and condition_OB[4]) or (condition_OB[1] and condition_OB[5]) or (condition_OB[1] and condition_OB[6]) or (condition_OB[1] and condition_OB[7])
    condition_OS_several = condition_OS[1] and condition_OS[2] or (condition_OS[1] and condition_OS[3]) or (condition_OS[1] and condition_OS[4]) or (condition_OS[1] and condition_OS[5]) or (condition_OS[1] and condition_OS[6]) or (condition_OS[1] and condition_OS[7])
    if time >= start and time <= end:
        if str_0:
            if not str_1:
                weight_str1 = 0
            if not str_2:
                weight_str2 = 0
            if not str_3:
                weight_str3 = 0
            if not str_4:
                weight_str4 = 0
            if not str_5:
                weight_str5 = 0
            if allow_shorts == True:
                w_total = weight_total(short_signal1, short_signal2, short_signal3, short_signal4, short_signal5)
                if w_total >= weight_trigger:
                    strategy.entry('Short', strategy.short, alert_message=alarm_label_short)
            if allow_longs == True:
                w_total = weight_total(long_signal1, long_signal2, long_signal3, long_signal4, long_signal5)
                if w_total >= weight_trigger:
                    strategy.entry('Long', strategy.long, alert_message=alarm_label_long)
        else:
            if allow_shorts == True:
                if str_1:
                    if short_signal1:
                        strategy.entry('Short', strategy.short, alert_message=alarm_label_short)
                if str_2:
                    if short_signal2:
                        strategy.entry('Short', strategy.short, alert_message=alarm_label_short)
                if str_3:
                    if short_signal3:
                        strategy.entry('Short', strategy.short, alert_message=alarm_label_short)
                if str_4:
                    if short_signal4:
                        strategy.entry('Short', strategy.short, alert_message=alarm_label_short)
                if str_5:
                    if short_signal5:
                        strategy.entry('Short', strategy.short, alert_message=alarm_label_short)
            if allow_longs == True:
                if str_1:
                    if long_signal1:
                        strategy.entry('Long', strategy.long, alert_message=alarm_label_long)
                if str_2:
                    if long_signal2:
                        strategy.entry('Long', strategy.long, alert_message=alarm_label_long)
                if str_3:
                    if long_signal3:
                        strategy.entry('Long', strategy.long, alert_message=alarm_label_long)
                if str_4:
                    if long_signal4:
                        strategy.entry('Long', strategy.long, alert_message=alarm_label_long)
                if str_5:
                    if long_signal5:
                        strategy.entry('Long', strategy.long, alert_message=alarm_label_long)
        if strategy.position_size != 0 and take_profits and (since_entry == 0):
            for i in pine_range(1, MAX_TP, 1):
                id = 'TP ' + string.tostring(i)
                strategy.exit(id=id, limit=price_takeProfit(profit_perc, i), qty_percent=profit_qty, comment=id, alert_message=set_alarm_label_TP())
        if strategy.position_size > 0:
            if since_close == 0:
                if high > price_takeProfit(profit_perc, 6) and MAX_TP >= 6:
                    n: int = 6
                    nextTP = na
                    if movestoploss == 'Percentage':
                        price_stop_long = strategy.position_avg_price * (1 + n * profit_perc - stoploss_perc * move_stoploss_factor)
                    elif movestoploss == 'TP-1':
                        price_stop_long = price_takeProfit(profit_perc, n - 1)
                    elif movestoploss == 'TP-2':
                        price_stop_long = price_takeProfit(profit_perc, n - 2)
                    elif movestoploss == 'TP-3':
                        price_stop_long = price_takeProfit(profit_perc, n - 3)
                elif high > price_takeProfit(profit_perc, 5) and MAX_TP >= 5:
                    n: int = 5
                    nextTP = price_takeProfit(profit_perc, n + 1)
                    if movestoploss == 'Percentage':
                        price_stop_long = strategy.position_avg_price * (1 + n * profit_perc - stoploss_perc * move_stoploss_factor)
                    elif movestoploss == 'TP-1':
                        price_stop_long = price_takeProfit(profit_perc, n - 1)
                    elif movestoploss == 'TP-2':
                        price_stop_long = price_takeProfit(profit_perc, n - 2)
                    elif movestoploss == 'TP-3':
                        price_stop_long = price_takeProfit(profit_perc, n - 3)
                elif high > price_takeProfit(profit_perc, 4) and MAX_TP >= 4:
                    n: int = 4
                    nextTP = price_takeProfit(profit_perc, n + 1)
                    if movestoploss == 'Percentage':
                        price_stop_long = strategy.position_avg_price * (1 + n * profit_perc - stoploss_perc * move_stoploss_factor)
                    elif movestoploss == 'TP-1':
                        price_stop_long = price_takeProfit(profit_perc, n - 1)
                    elif movestoploss == 'TP-2':
                        price_stop_long = price_takeProfit(profit_perc, n - 2)
                    elif movestoploss == 'TP-3':
                        price_stop_long = price_takeProfit(profit_perc, n - 3)
                elif high > price_takeProfit(profit_perc, 3) and MAX_TP >= 3:
                    n: int = 3
                    nextTP = price_takeProfit(profit_perc, n + 1)
                    if movestoploss == 'Percentage':
                        price_stop_long = strategy.position_avg_price * (1 + n * profit_perc - stoploss_perc * move_stoploss_factor)
                    elif movestoploss == 'TP-1':
                        price_stop_long = price_takeProfit(profit_perc, n - 1)
                    elif movestoploss == 'TP-2':
                        price_stop_long = price_takeProfit(profit_perc, n - 2)
                    elif movestoploss == 'TP-3' and movestoploss_entry:
                        price_stop_long = strategy.position_avg_price
                elif high > price_takeProfit(profit_perc, 2) and MAX_TP >= 2:
                    n: int = 2
                    nextTP = price_takeProfit(profit_perc, n + 1)
                    if movestoploss == 'Percentage':
                        price_stop_long = strategy.position_avg_price * (1 + n * profit_perc - stoploss_perc * move_stoploss_factor)
                    elif movestoploss == 'TP-1':
                        price_stop_long = price_takeProfit(profit_perc, n - 1)
                    elif movestoploss == 'TP-2' and movestoploss_entry:
                        price_stop_long = strategy.position_avg_price
                    elif movestoploss == 'TP-3' and movestoploss_entry:
                        price_stop_long = strategy.position_avg_price
                elif high > price_takeProfit(profit_perc, 1) and MAX_TP >= 1:
                    n: int = 1
                    nextTP = price_takeProfit(profit_perc, n + 1)
                    if movestoploss == 'Percentage':
                        price_stop_long = strategy.position_avg_price * (1 + n * profit_perc - stoploss_perc * move_stoploss_factor)
                    elif movestoploss == 'TP-1' and movestoploss_entry:
                        price_stop_long = strategy.position_avg_price
                    elif movestoploss == 'TP-2' and movestoploss_entry:
                        price_stop_long = strategy.position_avg_price
                    elif movestoploss == 'TP-3' and movestoploss_entry:
                        price_stop_long = strategy.position_avg_price
            if since_entry == 0:
                n: int = 0
                nextTP = price_takeProfit(profit_perc, n + 1)
                price_stop_long = strategy.position_avg_price * (1 - stoploss_perc)
        if strategy.position_size < 0:
            if since_close == 0:
                if low < price_takeProfit(profit_perc, 6) and MAX_TP >= 6:
                    n: int = 6
                    nextTP = na
                    if movestoploss == 'Percentage':
                        price_stop_short = strategy.position_avg_price * (1 - n * profit_perc + stoploss_perc * move_stoploss_factor)
                    elif movestoploss == 'TP-1':
                        price_stop_short = price_takeProfit(profit_perc, n - 1)
                    elif movestoploss == 'TP-2':
                        price_stop_short = price_takeProfit(profit_perc, n - 2)
                    elif movestoploss == 'TP-3':
                        price_stop_short = price_takeProfit(profit_perc, n - 3)
                elif low < price_takeProfit(profit_perc, 5) and MAX_TP >= 5:
                    n: int = 5
                    nextTP = price_takeProfit(profit_perc, n + 1)
                    if movestoploss == 'Percentage':
                        price_stop_short = strategy.position_avg_price * (1 - n * profit_perc + stoploss_perc * move_stoploss_factor)
                    elif movestoploss == 'TP-1':
                        price_stop_short = price_takeProfit(profit_perc, n - 1)
                    elif movestoploss == 'TP-2':
                        price_stop_short = price_takeProfit(profit_perc, n - 2)
                    elif movestoploss == 'TP-3':
                        price_stop_short = price_takeProfit(profit_perc, n - 3)
                elif low < price_takeProfit(profit_perc, 4) and MAX_TP >= 4:
                    n: int = 4
                    nextTP = price_takeProfit(profit_perc, n + 1)
                    if movestoploss == 'Percentage':
                        price_stop_short = strategy.position_avg_price * (1 - n * profit_perc + stoploss_perc * move_stoploss_factor)
                    elif movestoploss == 'TP-1':
                        price_stop_short = price_takeProfit(profit_perc, n - 1)
                    elif movestoploss == 'TP-2':
                        price_stop_short = price_takeProfit(profit_perc, n - 2)
                    elif movestoploss == 'TP-3':
                        price_stop_short = price_takeProfit(profit_perc, n - 3)
                elif low < price_takeProfit(profit_perc, 3) and MAX_TP >= 3:
                    n: int = 3
                    nextTP = price_takeProfit(profit_perc, n + 1)
                    if movestoploss == 'Percentage':
                        price_stop_short = strategy.position_avg_price * (1 - n * profit_perc + stoploss_perc * move_stoploss_factor)
                    elif movestoploss == 'TP-1':
                        price_stop_short = price_takeProfit(profit_perc, n - 1)
                    elif movestoploss == 'TP-2':
                        price_stop_short = price_takeProfit(profit_perc, n - 2)
                    elif movestoploss == 'TP-3' and movestoploss_entry:
                        price_stop_short = strategy.position_avg_price
                elif low < price_takeProfit(profit_perc, 2) and MAX_TP >= 2:
                    n: int = 2
                    nextTP = price_takeProfit(profit_perc, n + 1)
                    if movestoploss == 'Percentage':
                        price_stop_short = strategy.position_avg_price * (1 - n * profit_perc + stoploss_perc * move_stoploss_factor)
                    elif movestoploss == 'TP-1':
                        price_stop_short = price_takeProfit(profit_perc, n - 1)
                    elif movestoploss == 'TP-2' and movestoploss_entry:
                        price_stop_short = strategy.position_avg_price
                    elif movestoploss == 'TP-3' and movestoploss_entry:
                        price_stop_short = strategy.position_avg_price
                elif low < price_takeProfit(profit_perc, 1) and MAX_TP >= 1:
                    n: int = 1
                    nextTP = price_takeProfit(profit_perc, n + 1)
                    if movestoploss == 'Percentage':
                        price_stop_short = strategy.position_avg_price * (1 - n * profit_perc + stoploss_perc * move_stoploss_factor)
                    elif movestoploss == 'TP-1' and movestoploss_entry:
                        price_stop_short = strategy.position_avg_price
                    elif movestoploss == 'TP-2' and movestoploss_entry:
                        price_stop_short = strategy.position_avg_price
                    elif movestoploss == 'TP-3' and movestoploss_entry:
                        price_stop_short = strategy.position_avg_price
            if since_entry == 0:
                n: int = 0
                nextTP = price_takeProfit(profit_perc, n + 1)
                price_stop_short = strategy.position_avg_price * (1 + stoploss_perc)
        if allow_longs == True and allow_shorts == False:
            if str_0:
                w_total = weight_total(short_signal1, short_signal2, short_signal3, short_signal4, short_signal5)
                if w_total >= weight_trigger:
                    strategy.close('Long', qty_percent=100, comment='SHORT', alert_message=alarm_label_close_long)
            else:
                if str_1:
                    if close_long1:
                        strategy.close('Long', qty_percent=100, comment='SHORT', alert_message=alarm_label_close_long)
                if str_2:
                    if close_long2:
                        strategy.close('Long', qty_percent=100, comment='SHORT', alert_message=alarm_label_close_long)
                if str_3:
                    if close_long3:
                        strategy.close('Long', qty_percent=100, comment='SHORT', alert_message=alarm_label_close_long)
                if str_4:
                    if close_long4:
                        strategy.close('Long', qty_percent=100, comment='SHORT', alert_message=alarm_label_close_long)
                if str_5:
                    if close_long5:
                        strategy.close('Long', qty_percent=100, comment='SHORT', alert_message=alarm_label_close_long)
        if allow_longs == False and allow_shorts == True:
            if str_0:
                w_total = weight_total(long_signal1, long_signal2, long_signal3, long_signal4, long_signal5)
                if w_total >= weight_trigger:
                    strategy.close('Short', qty_percent=100, comment='LONG', alert_message=alarm_label_close_short)
            else:
                if str_1:
                    if close_long1:
                        strategy.close('Short', qty_percent=100, comment='LONG', alert_message=alarm_label_close_short)
                if str_2:
                    if close_long2:
                        strategy.close('Short', qty_percent=100, comment='LONG', alert_message=alarm_label_close_short)
                if str_3:
                    if close_long3:
                        strategy.close('Short', qty_percent=100, comment='LONG', alert_message=alarm_label_close_short)
                if str_4:
                    if close_long4:
                        strategy.close('Short', qty_percent=100, comment='LONG', alert_message=alarm_label_close_short)
                if str_5:
                    if close_long5:
                        strategy.close('Short', qty_percent=100, comment='LONG', alert_message=alarm_label_close_short)
        if allow_shorts == True and strategy.position_size < 0 and stoploss and (since_entry > 0):
            if stop_source >= price_stop_short:
                strategy.close('Short', qty_percent=100, comment='STOP', alert_message=alarm_label_SL)
            if str_6:
                if top_qty == 100:
                    if condition_OS_several:
                        strategy.close('Short', qty_percent=bottom_qty, comment='STOP', alert_message=alarm_label_SL)
                else:
                    if condition_OS_several:
                        strategy.exit('Short', limit=source_6_bottom[1], qty_percent=bottom_qty, comment='TP-B', alert_message=set_alarm_label_TP())
        if allow_longs == True and strategy.position_size > 0 and stoploss and (since_entry > 0):
            if stop_source <= price_stop_long:
                strategy.close('Long', qty_percent=100, comment='STOP', alert_message=alarm_label_SL)
            if str_6:
                if top_qty == 100:
                    if condition_OB_several:
                        strategy.close('Long', qty_percent=top_qty, comment='STOP', alert_message=alarm_label_SL)
                else:
                    if condition_OB_several:
                        strategy.exit('Long', limit=source_6_top[1], qty_percent=top_qty, comment='TP-T', alert_message=set_alarm_label_TP())
    price_stop = price_stop_long if strategy.position_size > 0 else price_stop_short
    plotchar(volume[2] / volume[1], 'Volume 2 / Volume 1', '', location.top, size=size.tiny, color=color.new(color.orange, 0))
    plotchar(since_entry, 'Since entry [bars]', '', location.top, size=size.tiny, color=color.new(color.orange, 0))
    plotchar(since_close, 'Since close/TP [bars]', '', location.top, size=size.tiny, color=color.new(color.orange, 0))
    plotchar(strategy.position_avg_price, 'Average position price', '', location.top, size=size.tiny, color=color.new(color.orange, 0))
    plotchar(strategy.position_size, 'Position size', '', location.top, size=size.tiny, color=color.new(color.orange, 0))
    plotchar(nextTP, 'Next TP target', '', location.top, size=size.tiny, color=color.new(color.teal, 0))
    plotchar(price_stop, 'STOP Price', '', location.top, size=size.tiny, color=color.new(color.gray, 0))
    plotchar(strategy.opentrades, 'Open trades', '', location.top, size=size.tiny, color=color.blue if strategy.position_size > 0 else color.gray)
    plotchar(strategy.netprofit, 'Net profit [$]', '', location.top, size=size.tiny, color=color.blue if strategy.netprofit > 0 else color.gray)
    plotchar(strategy.grossprofit, 'Gross profit [$]', '', location.top, size=size.tiny, color=color.blue)
    plotchar(strategy.grossloss, 'Gross loss [$]', '', location.top, size=size.tiny, color=color.gray)
    plotchar(strategy.openprofit, 'Unrealized P&L [$]', '', location.top, size=size.tiny, color=color.blue if strategy.openprofit > 0 else color.gray)
    plotchar(strategy.closedtrades, 'Closed trades', '', location.top, size=size.tiny, color=color.orange)
    plotchar(strategy.wintrades / strategy.closedtrades * 100, 'Winrate [%]', '', location.top, size=size.tiny, color=color.blue if strategy.wintrades / strategy.closedtrades > 60 else color.gray)
    plot(trend, 'Trend', style=plot.style_columns, color=color.new(color.teal, 30) if MACD > signal else color.new(color.gray, 30), display=display.none)
    plot(MACD, 'MACD', color=color.new(color.blue, 0), display=display.none)
    plot(signal, 'Signal', color=color.new(color.orange, 0), display=display.none)
    plotshape(up if long_signal1 and FLAG_SIGNALS else na, 'Buy MACD', text='MACD', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0), display=display.none)
    plotshape(dn if short_signal1 and FLAG_SIGNALS else na, 'Sell MACD', text='MACD', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.gray, 0), textcolor=color.new(color.white, 0), display=display.none)
    plotshape(up if long_signal2 and FLAG_SIGNALS else na, title='Buy Stoch RSI', text='SRSI', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0), display=display.none)
    plotshape(dn if short_signal2 and FLAG_SIGNALS else na, title='Sell Stoch RSI', text='SRSI', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.gray, 0), textcolor=color.new(color.white, 0), display=display.none)
    plotshape(up if long_signal3 and FLAG_SIGNALS else na, title='Buy RSI', text='RSI', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0), display=display.none)
    plotshape(dn if short_signal3 and FLAG_SIGNALS else na, title='Sell RSI', text='RSI', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.gray, 0), textcolor=color.new(color.white, 0), display=display.none)
    plotshape(up if long_signal4 and FLAG_SIGNALS else na, title='Buy Supertrend', text='Supertrend', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0), display=display.none)
    plotshape(dn if short_signal4 and FLAG_SIGNALS else na, title='Sell Supertrend', text='Supertrend', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.gray, 0), textcolor=color.new(color.white, 0), display=display.none)
    plotshape(up if long_signal5 and FLAG_SIGNALS else na, title='Buy MA CROSS', text='MA CROSS', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0), display=display.none)
    plotshape(dn if short_signal5 and FLAG_SIGNALS else na, title='Sell MA CROSS', text='MA CROSS', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.gray, 0), textcolor=color.new(color.white, 0), display=display.none)
    plotshape(dn if condition_OB_several else na, title='Top', text='T', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0))
    plotshape(up if condition_OS_several else na, title='Bottom', text='B', location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0))
    w_total_long = weight_total(long_signal1, long_signal2, long_signal3, long_signal4, long_signal5)
    w_total_short = weight_total(short_signal1, short_signal2, short_signal3, short_signal4, short_signal5)
    plotshape(up if w_total_long >= weight_trigger and FLAG_SIGNALS else na, title='Buy Weigthed strategy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0))
    plotshape(dn if w_total_short >= weight_trigger and FLAG_SIGNALS else na, title='Sell Weigthed strategy', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.gray, 0), textcolor=color.new(color.white, 0))
    plot(series=price_stop_long if strategy.position_size > 0 else na, color=color.new(color.gray, 30), style=plot.style_cross, linewidth=2, title='Long Stop Loss')
    plot(series=price_stop_short if strategy.position_size < 0 else na, color=color.new(color.gray, 30), style=plot.style_cross, linewidth=2, title='Short Stop Loss')
    plot(nextTP if strategy.position_size > 0 or strategy.position_size < 0 else na, color=color.new(color.aqua, 30), style=plot.style_cross, linewidth=2, title='Next TP')
    mPlot = plot(ohlc4, title='Price ohlc4', style=plot.style_circles, linewidth=math.max(1, 0), display=display.none)
    upPlot = plot(up if (long_signal1 or long_signal2 or long_signal3 or long_signal4 or long_signal5) and w_total_long > w_total_short else na, title='Up Trend', style=plot.style_linebr, linewidth=2, color=color.new(color.aqua, 0), display=display.none)
    dnPlot = plot(dn if (short_signal1 or short_signal2 or short_signal3 or short_signal4 or short_signal5) and w_total_short > w_total_long else na, title='Down Trend', style=plot.style_linebr, linewidth=2, color=color.new(color.gray, 0), display=display.none)
    plotchar(weight_trigger, 'Trigger strategies', '', location.top, size=size.tiny, color=color.new(color.orange, 0))
    plotchar(w_total_long, 'Satisfied Long strategies', '', location.top, size=size.tiny, color=color.orange if w_total_long >= weight_trigger else color.gray)
    plotchar(w_total_short, 'Satisfied Short strategies', '', location.top, size=size.tiny, color=color.orange if w_total_long >= weight_trigger else color.gray)
    plotshape(up if (long_signal1 or long_signal2 or long_signal3 or long_signal4 or long_signal5) and w_total_long > w_total_short else na, title='UpTrend Begins', location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(color.aqua, 0), display=display.none)
    plotshape(dn if (short_signal1 or short_signal2 or short_signal3 or short_signal4 or short_signal5) and w_total_short > w_total_long else na, title='DownTrend Begins', location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(color.gray, 0), display=display.none)
    fill(mPlot, upPlot, title='UpTrend Highligter', color=colors('buy', 80 if FLAG_SHADOWS else 100))
    fill(mPlot, dnPlot, title='DownTrend Highligter', color=colors('sell', 80 if FLAG_SHADOWS else 100))
    if show_performance:
        new_month = month(time) != month(time[1])
        new_year = year(time) != year(time[1])
        eq: Series = strategy.equity
        bar_pnl = eq / eq[1] - 1
        cur_month_pnl: Series[float] = 0.0
        cur_year_pnl: Series[float] = 0.0
        cur_month_pnl = 0.0 if new_month else (1 + cur_month_pnl[1]) * (1 + bar_pnl) - 1
        cur_year_pnl = 0.0 if new_year else (1 + cur_year_pnl[1]) * (1 + bar_pnl) - 1
        month_pnl: Persistent[list[float]] = array.new_float(0)
        month_time: Persistent[list[int]] = array.new_int(0)
        year_pnl: Persistent[list[float]] = array.new_float(0)
        year_time: Persistent[list[int]] = array.new_int(0)
        last_computed: Series[bool] = False
        if not na(cur_month_pnl[1]) and (new_month or barstate.islastconfirmedhistory):
            if last_computed[1]:
                array.pop(month_pnl)
                array.pop(month_time)
            array.push(month_pnl, cur_month_pnl[1])
            array.push(month_time, time[1])
        if not na(cur_year_pnl[1]) and (new_year or barstate.islastconfirmedhistory):
            if last_computed[1]:
                array.pop(year_pnl)
                array.pop(year_time)
            array.push(year_pnl, cur_year_pnl[1])
            array.push(year_time, time[1])
        last_computed = True if barstate.islastconfirmedhistory else nz(last_computed[1])
        monthly_table: Persistent = NA(Table)
        if barstate.islastconfirmedhistory:
            monthly_table = table.new(position.bottom_right, columns=14, rows=array.size(year_pnl) + 1, border_width=1)
            table.cell(monthly_table, 0, 0, '', bgcolor=color.new('#CCCCCC'))
            table.cell(monthly_table, 1, 0, 'Jan', bgcolor=color.new('#CCCCCC'))
            table.cell(monthly_table, 2, 0, 'Feb', bgcolor=color.new('#CCCCCC'))
            table.cell(monthly_table, 3, 0, 'Mar', bgcolor=color.new('#CCCCCC'))
            table.cell(monthly_table, 4, 0, 'Apr', bgcolor=color.new('#CCCCCC'))
            table.cell(monthly_table, 5, 0, 'May', bgcolor=color.new('#CCCCCC'))
            table.cell(monthly_table, 6, 0, 'Jun', bgcolor=color.new('#CCCCCC'))
            table.cell(monthly_table, 7, 0, 'Jul', bgcolor=color.new('#CCCCCC'))
            table.cell(monthly_table, 8, 0, 'Aug', bgcolor=color.new('#CCCCCC'))
            table.cell(monthly_table, 9, 0, 'Sep', bgcolor=color.new('#CCCCCC'))
            table.cell(monthly_table, 10, 0, 'Oct', bgcolor=color.new('#CCCCCC'))
            table.cell(monthly_table, 11, 0, 'Nov', bgcolor=color.new('#CCCCCC'))
            table.cell(monthly_table, 12, 0, 'Dec', bgcolor=color.new('#CCCCCC'))
            table.cell(monthly_table, 13, 0, 'Year', bgcolor=color.new('#999999'))
            for yi in pine_range(0, array.size(year_pnl) - 1, 1):
                table.cell(monthly_table, 0, yi + 1, string.tostring(year(array.get(year_time, yi))), bgcolor=color.new('#CCCCCC'))
                y_color = color.new(color.teal, transp=40) if array.get(year_pnl, yi) > 0 else color.new(color.gray, transp=40)
                table.cell(monthly_table, 13, yi + 1, string.tostring(math.round(array.get(year_pnl, yi) * 100, prec)), bgcolor=y_color, text_color=color.new(color.white, 0))
            for mi in pine_range(0, array.size(month_time) - 1, 1):
                m_row = year(array.get(month_time, mi)) - year(array.get(year_time, 0)) + 1
                m_col = month(array.get(month_time, mi))
                m_color = color.new(color.teal, transp=40) if array.get(month_pnl, mi) > 0 else color.new(color.gray, transp=40)
                table.cell(monthly_table, m_col, m_row, string.tostring(math.round(array.get(month_pnl, mi) * 100, prec)), bgcolor=m_color, text_color=color.new(color.white, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
