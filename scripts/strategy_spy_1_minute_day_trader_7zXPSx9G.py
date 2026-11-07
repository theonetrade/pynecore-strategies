"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    array, bar_index, barstate, close, color, display, high, hlc3, hour,
    input, low, math, minute, na, open, plot, request, script, strategy, syminfo, ta, time,
    time_close, timestamp
)
from pynecore.types import Persistent, Series


@script.strategy(title='SPY 1 Minute Day Trader', initial_capital=1800000, default_qty_type=strategy.percent_of_equity, default_qty_value=7, pyramiding=0, commission_type=strategy.commission.cash_per_order, commission_value=2.6, overlay=True, calc_on_every_tick=False, process_orders_on_close=True, max_labels_count=500, margin_long=0, margin_short=0, close_by_id=True)
def main(
    shortpinbars=input.bool(True, 'Trade 3x tail to body short pin bar reversals'),
    longpinbars=input.bool(True, 'Trade 3x tail to body long pin bar reversals'),
    D1=input.bool(False, 'Show missing parameters for all time / Unchecked (default) will allow descriptive tooltip for last 500 entries'),
    notrade=input.bool(True, 'Trade from 10:30 until Noon EST'),
    notradelunch=input.bool(True, 'Trade during lunchtime from noon until 1 EST'),
    notrade1to3=input.bool(True, 'Trade from 1 until 3 EST'),
    notradePH=input.bool(True, 'Trade during Power Hour 3 until 4 EST'),
    option_SL_P=input.float(0.00075, title='Stop Loss Percentage in Decimal Form'),
    option_TP_P=input.float(0.00075, title='Take Profit Percentage in Decimal Form'),
    TSTAMP=input.time(title='From this date. To see entire backtest range set to a year ago.', defval=timestamp('2022-05-12T09:30:00')),
    fastLength=input.int(12, minval=1, title='MACD Fast Length'),
    slowLength=input.int(26, minval=1, title='MACD Slow Length'),
    signalLength=input.int(9, minval=1, title='MACD Signal Smoothing'),
    length=input.int(14, 'Stochastic Length'),
    smoothK=input.int(3, 'Stoicastic Smooth K'),
    src: Series[float] = input(close, 'Stoicastic Source'),
    atr_length=input.int(14, title='ATR Length', minval=1),
    len=input.int(14, title='ADX Length', minval=1)
):
    long_entry_price: Persistent[float] = na(float)
    short_entry_price: Persistent[float] = na(float)
    stop_loss: Persistent[float] = na(float)
    take_profit: Persistent[float] = na(float)
    twoxtake_profit: Persistent[float] = na(float)
    threextake_profit: Persistent[float] = na(float)
    short_stop_loss: Persistent[float] = na(float)
    short_take_profit: Persistent[float] = na(float)
    twoxshort_take_profit: Persistent[float] = na(float)
    threexshort_take_profit: Persistent[float] = na(float)
    long_entry_time: Persistent[int] = 0
    long_entry_minute: Persistent[int] = 0
    short_entry_time: Persistent[int] = 0
    short_entry_minute: Persistent[int] = 0
    allow_long_entry: Persistent[bool] = True
    allow_short_entry: Persistent[bool] = True
    allow_trades: Persistent[bool] = True
    hourlyclose: Persistent[int] = 0
    notify: Persistent[int] = 0
    shortnotify: Persistent[int] = 0
    adxinput: Persistent[int] = 18
    entry: Persistent[int] = 0
    tooltipnote: Persistent[str] = 'Emtpy'
    signal: Persistent[str] = 'Empty'
    show: Persistent[int] = 0
    upperBandValue: float = na(float)
    lowerBandValue: float = na(float)
    vwapmid = request.security(syminfo.tickerid, '1', ta.vwap(hlc3))
    vwap_array: list[float] = array.new_float()
    array.push(vwap_array, vwapmid)
    array.push(vwap_array, vwapmid + 1)
    array.push(vwap_array, vwapmid - 1)
    std_dev = array.stdev(vwap_array)
    upperBandValue = vwapmid + std_dev * 2
    lowerBandValue = vwapmid - std_dev * 2
    plot(vwapmid, title='VWAP', color=color.aqua, linewidth=2)
    plot(upperBandValue, title='Upper VWAP', color=color.aqua, linewidth=1)
    plot(lowerBandValue, title='Lower VWAP', color=color.aqua, linewidth=1)
    ema5 = ta.ema(close, 5)
    ema13 = ta.ema(close, 13)
    sma20 = ta.sma(close, 20)
    highestHigh = ta.highest(src, length)
    lowestLow = ta.lowest(src, length)
    k = 100 * ((src - lowestLow) / (highestHigh - lowestLow))
    d = ta.sma(k, smoothK)
    rsiValue = ta.rsi(close, 5)
    rsiSignal = ta.sma(rsiValue, 9)
    macdLine: Series
    macdLine, signalLine, _ = ta.macd(close, fastLength, slowLength, signalLength)
    macdSlope = (macdLine - macdLine[3]) / (bar_index - bar_index[3])
    tr = ta.tr(True)
    atr = ta.atr(atr_length)
    atr_squared = math.pow(atr, 2)
    mean_atr_squared = ta.sma(atr_squared, 20)
    rms_atr = math.sqrt(mean_atr_squared)
    min_bars_between_trades: int = 12
    up = ta.change(high)
    down = -ta.change(low)
    plusDM = na if na(up) else up if up > down and up > 0 else 0
    minusDM = na if na(down) else down if down > up and down > 0 else 0
    plusDI = 100 * ta.ema(plusDM, len) / ta.ema(tr, len)
    minusDI = 100 * ta.ema(minusDM, len) / ta.ema(tr, len)
    DX = 100 * math.abs(plusDI - minusDI) / (plusDI + minusDI)
    adx = ta.ema(DX, len)
    src_5m = request.security(syminfo.tickerid, '5', close)
    ema_5m_20 = ta.ema(src_5m, 20)
    ema_5m = ta.ema(src_5m, 13)
    ema_5m_5 = ta.ema(src_5m, 5)
    plot(ema_5m, '5 Min 13 EMA', color=color.orange, linewidth=2)
    plot(ema_5m_5, '5 Min 5 EMA', color=color.blue, linewidth=2)
    highPrice = high
    lowPrice = low
    closePrice = close
    unixTimestamp = time_close
    minuteValue = minute(unixTimestamp)
    tradingMinute = minuteValue + (hour(unixTimestamp) - 9) * 60 - 30
    lowOfDay = ta.lowest(low, tradingMinute)
    highOfDay = ta.highest(high, tradingMinute)
    isAfter1030 = request.security(syminfo.tickerid, '60', tradingMinute >= 0)
    highOfLastHour = ta.highest(high, 90)
    lowOfLastHour = ta.lowest(low, 90)
    plot(lowOfDay, 'Low of Day', color.fuchsia)
    plot(highOfDay, 'High of Day', color.fuchsia)
    buy_signal = ema5 > ema13 and ema_5m > ema_5m_5 and (rsiSignal < 49) and (tradingMinute <= 60) and barstate.isconfirmed or (notrade == cast_bool(1) and ema5 > ema13 and (ema_5m > ema_5m_5) and (rsiSignal < 49) and (tradingMinute > 60) and (tradingMinute <= 150) and barstate.isconfirmed) or (notradelunch == cast_bool(1) and ema5 > ema13 and (ema_5m > ema_5m_5) and (rsiSignal < 49) and (tradingMinute > 150) and (tradingMinute <= 210) and barstate.isconfirmed) or (notrade1to3 and ema5 > ema13 and (ema_5m > ema_5m_5) and (rsiSignal < 49) and (tradingMinute > 210) and (tradingMinute <= 330) and barstate.isconfirmed) or (notradePH == cast_bool(1) and ema5 > ema13 and (ema_5m > ema_5m_5) and (rsiSignal < 49) and (tradingMinute > 330) and barstate.isconfirmed)
    short_buy_signal = ema5 < ema13 and ema_5m < ema_5m_5 and (rsiSignal > 0) and (tradingMinute <= 60) and barstate.isconfirmed or (notrade == cast_bool(1) and ema5 < ema13 and (ema_5m < ema_5m_5) and (rsiSignal > 60) and (tradingMinute > 60) and (tradingMinute <= 150) and barstate.isconfirmed) or (notradelunch == cast_bool(1) and ema5 < ema13 and (ema_5m < ema_5m_5) and (rsiSignal > 60) and (tradingMinute > 150) and (tradingMinute <= 210) and barstate.isconfirmed) or (notrade1to3 and ema5 < ema13 and (ema_5m < ema_5m_5) and (rsiSignal > 60) and (tradingMinute > 210) and (tradingMinute <= 330) and barstate.isconfirmed) or (notradePH == cast_bool(1) and ema5 < ema13 and (ema_5m < ema_5m_5) and (rsiSignal > 65) and (tradingMinute > 330) and barstate.isconfirmed)
    C1 = 1 if ema5 > ema13 else 0
    C2 = 1 if d >= 0 else 0
    C4 = 1 if adx > 0 else 0
    C5 = 1 if macdSlope > 0 else 0
    C18 = 1 if rms_atr < 0.75 else 0
    C19 = 1 if (ema_5m - ema_5m_5) / close > 0.0005 and tradingMinute <= 60 or ((ema_5m - ema_5m_5) / close > 0.0005 and tradingMinute > 60 and (tradingMinute <= 150)) or (math.abs(ema_5m - ema_5m_5) / close > 0.0002 and tradingMinute > 150 and (tradingMinute <= 210)) or ((ema_5m - ema_5m_5) / close > 0.0001 and tradingMinute > 210 and (tradingMinute <= 330)) or (math.abs(ema_5m - ema_5m_5) / close > 0.0002 and tradingMinute > 330) else 0
    C22 = 1 if close > open else 0
    C23 = 1 if math.abs(close - highOfDay) / close > 0.0006 and tradingMinute <= 150 or (math.abs(close - highOfDay) / close > 0.0006 and tradingMinute > 150 and (tradingMinute <= 210)) or (math.abs(close - highOfDay) / close > 0.0002 and tradingMinute > 210 and (tradingMinute <= 330)) or (math.abs(close - highOfDay) / close > 0.0006 and tradingMinute > 330) else 0
    C25 = 1 if close >= lowerBandValue else 0
    C8 = 1 if ema5 < ema13 else 0
    C9 = 1 if d >= 0 else 0
    C11 = 1 if adx > 20 else 0
    C12 = 1 if macdSlope < 0 else 0
    C16 = 1 if rms_atr < 0.75 else 0
    C20 = 1 if (ema_5m - ema_5m_5) / close > 0.0005 and tradingMinute <= 60 or (math.abs(ema_5m - ema_5m_5) / close > 0.0002 and tradingMinute > 60 and (tradingMinute <= 150)) or (math.abs(ema_5m - ema_5m_5) / close > 0.0003 and tradingMinute > 150 and (tradingMinute <= 210)) or ((ema_5m - ema_5m_5) / close > 0.0003 and tradingMinute > 210 and (tradingMinute <= 330)) or ((ema_5m - ema_5m_5) / close > 0.0003 and tradingMinute > 330) else 0
    C21 = 1 if open > close else 0
    C24 = 1 if math.abs(close - lowOfDay) / close > 0.0006 and tradingMinute <= 150 or (math.abs(close - lowOfDay) / close > 0.0006 and tradingMinute > 150 and (tradingMinute <= 210)) or (math.abs(close - lowOfDay) / close > 0.0002 and tradingMinute > 210 and (tradingMinute <= 330)) or (math.abs(close - lowOfDay) / close > 0.0006 and tradingMinute > 330) else 0
    C26 = 1 if close <= upperBandValue else 0
    if C1 + C2 + C4 + C5 + C18 + C19 + C22 + C23 + C25 == 8 and C1 == 0 and barstate.isconfirmed:
        tooltipnote = '1 min 13 EMA > 5 EMA (decreasing trend)'
        signal = '↓'
        show = 1
    elif C1 + C2 + C4 + C5 + C18 + C19 + C22 + C23 + C25 == 8 and C2 == 0 and barstate.isconfirmed:
        tooltipnote = 'Stoichastic > 90 (overbought may dump)'
        signal = 'd'
        show = 1
    elif C1 + C2 + C4 + C5 + C18 + C19 + C22 + C23 + C25 == 8 and C4 == 0 and barstate.isconfirmed:
        tooltipnote = 'ADX < 20 (not trending)'
        signal = 'A\nD\nX'
        show = 1
    elif C1 + C2 + C4 + C5 + C18 + C19 + C22 + C23 + C25 == 8 and C5 == 0 and barstate.isconfirmed:
        tooltipnote = 'MACD has downward slope (losing momentum)'
        signal = 'M\n/'
        show = 1
    elif C1 + C2 + C4 + C5 + C18 + C19 + C22 + C23 + C25 == 8 and C18 == 0 and barstate.isconfirmed:
        tooltipnote = 'ATR > 0.75 (increased volatility)'
        signal = 'A\nT\nR'
        show = 1
    elif C1 + C2 + C4 + C5 + C18 + C19 + C22 + C23 + C25 == 8 and C19 == 0 and barstate.isconfirmed:
        tooltipnote = '5 Min 5/13 EMA difference too close (noisy trade)'
        signal = '5'
        show = 1
    elif C1 + C2 + C4 + C5 + C18 + C19 + C22 + C23 + C25 == 8 and C22 == 0 and barstate.isconfirmed:
        tooltipnote = 'Candle closes below open (trend reversing?)'
        signal = 'C'
        show = 1
    elif C1 + C2 + C4 + C5 + C18 + C19 + C22 + C23 + C25 == 8 and C23 == 0 and barstate.isconfirmed:
        tooltipnote = 'Too close to high of day (out of runway?)'
        signal = 'H'
        show = 1
    elif C1 + C2 + C4 + C5 + C18 + C19 + C22 + C23 + C25 == 8 and C25 == 0 and barstate.isconfirmed:
        tooltipnote = 'Below VWAP 2 standard deviations (on a run!)'
        signal = 'V'
        show = 1
    if C8 + C9 + C11 + C12 + C16 + C20 + C21 + C24 + C26 == 8 and C8 == 0 and barstate.isconfirmed:
        tooltipnote = '1 min 5 EMA > 13 EMA (increasing trend)'
        signal = '↑'
        show = 2
    elif C8 + C9 + C11 + C12 + C16 + C20 + C21 + C24 + C26 == 8 and C9 == 0 and barstate.isconfirmed:
        tooltipnote = 'Stoichastic > 0 (oversold may cause bounce)'
        signal = 'd'
        show = 2
    elif C8 + C9 + C11 + C12 + C16 + C20 + C21 + C24 + C26 == 8 and C11 == 0 and barstate.isconfirmed:
        tooltipnote = 'ADX < 20 (not trending)'
        signal = 'A\nD\nX'
        show = 2
    elif C8 + C9 + C11 + C12 + C16 + C20 + C21 + C24 + C26 == 8 and C12 == 0 and barstate.isconfirmed:
        tooltipnote = 'MACD has upward slope (gaining momentum)'
        signal = 'M\n/'
        show = 2
    elif C8 + C9 + C11 + C12 + C16 + C20 + C21 + C24 + C26 == 8 and C16 == 0 and barstate.isconfirmed:
        tooltipnote = 'ATR > 0.75 (increased volatility)'
        signal = 'A\nT\nR'
        show = 2
    elif C8 + C9 + C11 + C12 + C16 + C20 + C21 + C24 + C26 == 8 and C20 == 0 and barstate.isconfirmed:
        tooltipnote = '5 Min 5/13 EMA difference too close (noisy trade)'
        signal = '5'
        show = 2
    elif C8 + C9 + C11 + C12 + C16 + C20 + C21 + C24 + C26 == 8 and C21 == 0 and barstate.isconfirmed:
        tooltipnote = 'Candle closes above open (trend reversing?)'
        signal = 'C'
        show = 2
    elif C8 + C9 + C11 + C12 + C16 + C20 + C21 + C24 + C26 == 8 and C24 == 0 and barstate.isconfirmed:
        tooltipnote = 'Too close to low of day (out of runway?)'
        signal = 'L'
        show = 2
    elif C8 + C9 + C11 + C12 + C16 + C20 + C21 + C24 + C26 == 8 and C26 == 0 and barstate.isconfirmed:
        tooltipnote = 'Above VWAP 2 standard deviations (on a run!)'
        signal = 'V'
        show = 2
    if show == 1 or show == 2:
        show = 0
    if buy_signal and strategy.position_size == 0 and allow_trades and allow_long_entry and barstate.isconfirmed and (time >= TSTAMP):
        long_entry_price = open
        strategy.entry('Pivot Up', strategy.long, alert_message='Pivoting Up')
        stop_loss = long_entry_price - option_SL_P * open
        take_profit = long_entry_price + option_TP_P * open
        twoxtake_profit = long_entry_price + 2 * option_TP_P * open
        threextake_profit = long_entry_price + 3 * option_TP_P * open
        long_entry_time = time
        long_entry_minute = tradingMinute
        allow_long_entry = False
        allow_trades = False
        notify = 1
        entry = 0
    if high == open and close - low >= 3 * (open - close) and (open >= close) and ((high - low) / high >= option_TP_P) and (strategy.position_size <= 0) and (longpinbars == cast_bool(1)) and barstate.isconfirmed and (time >= TSTAMP):
        long_entry_price = open
        strategy.entry('Pivot Pin Bar Up', strategy.long, alert_message='Pivoting Pin Bar Up')
        stop_loss = long_entry_price - option_SL_P * open
        take_profit = long_entry_price + option_TP_P * open
        twoxtake_profit = long_entry_price + 2 * option_TP_P * open
        threextake_profit = long_entry_price + 3 * option_TP_P * open
        long_entry_time = time
        long_entry_minute = tradingMinute
        allow_long_entry = False
        allow_trades = False
        notify = 1
        entry = 0
    plot(open - option_SL_P * open if notify == 1 else na, 'Stop Loss', color.yellow, style=plot.style_linebr, offset=1, linewidth=3, display=display.pane)
    plot(open + option_TP_P * open if notify == 1 else na, 'Take Profit', color.yellow, style=plot.style_linebr, offset=1, linewidth=3, display=display.pane)
    plot(open + 2 * option_TP_P * open if notify == 1 else na, '2x Take Profit', color.orange, style=plot.style_linebr, offset=1, linewidth=2, display=display.pane)
    if notify == 1:
        notify = notify - 1
    if short_buy_signal and strategy.position_size == 0 and allow_trades and allow_short_entry and (time >= TSTAMP):
        short_entry_price = open
        strategy.entry('Pivot Down', strategy.short, alert_message='Pivoting Down')
        short_stop_loss = short_entry_price + option_SL_P * open
        short_take_profit = short_entry_price - option_TP_P * open
        twoxshort_take_profit = short_entry_price - 2 * option_TP_P * open
        threexshort_take_profit = short_entry_price - 3 * option_TP_P * open
        short_entry_time = time
        short_entry_minute = tradingMinute
        allow_short_entry = False
        allow_trades = False
        shortnotify = 1
        entry = 0
    if close == low and high - close >= 3 * (close - open) and (open <= close) and ((high - low) / high >= option_TP_P) and (strategy.position_size >= 0) and (shortpinbars == cast_bool(1)) and barstate.isconfirmed and (time >= TSTAMP):
        short_entry_price = open
        strategy.entry('Pivot Pin Bar Down', strategy.short, alert_message='Pivoting Pin Bar Down')
        short_stop_loss = short_entry_price + option_SL_P * open
        short_take_profit = short_entry_price - option_TP_P * open
        twoxshort_take_profit = short_entry_price - 2 * option_TP_P * open
        threexshort_take_profit = short_entry_price - 3 * option_TP_P * open
        short_entry_time = time
        short_entry_minute = tradingMinute
        allow_short_entry = False
        allow_trades = False
        shortnotify = 1
        entry = 0
    plot(open + option_SL_P * open if shortnotify == 1 else na, 'Stop Loss', color.yellow, style=plot.style_linebr, offset=1, linewidth=3, display=display.pane)
    plot(open - option_TP_P * open if shortnotify == 1 else na, 'Take Profit', color.yellow, style=plot.style_linebr, offset=1, linewidth=3, display=display.pane)
    plot(open - 2 * option_TP_P * open if shortnotify == 1 else na, '2x Take Profit', color.orange, style=plot.style_linebr, offset=1, linewidth=2, display=display.pane)
    if shortnotify == 1 and barstate.isconfirmed:
        shortnotify = shortnotify - 1
    if strategy.position_size > 0 and barstate.isconfirmed:
        if close < stop_loss and barstate.isconfirmed:
            strategy.close('Pivot Up', 'Exit Longs Stopped', alert_message='Exit Longs Stopped')
            strategy.close('Pivot Pin Bar Up', 'Exit Longs Stopped', alert_message='Exit Longs Stopped')
        elif close >= twoxtake_profit and (adx <= 25 or close < close[3]) and barstate.isconfirmed:
            if entry == 1 and barstate.isconfirmed:
                take_profit = threextake_profit
            if entry == 0 and barstate.isconfirmed:
                entry = 1
                stop_loss = take_profit
                strategy.exit('Exit Longs', 'Pivot Up', stop=stop_loss, limit=take_profit, alert_message='Exit Longs')
                strategy.exit('Exit Longs', 'Pivot Pin Bar Up', stop=stop_loss, limit=take_profit, alert_message='Exit Longs')
        elif src_5m < ema_5m and tradingMinute - long_entry_minute > 3 and (adx <= 25 or close < close[3]) and barstate.isconfirmed:
            strategy.exit('Exit Longs 5 Min EMA Cross', 'Pivot Up', stop=stop_loss, limit=take_profit, alert_message='Exit Longs 5 Min EMA Cross')
            strategy.exit('Exit Longs 5 Min EMA Cross', 'Pivot Pin Bar Up', stop=stop_loss, limit=take_profit, alert_message='Exit Longs 5 Min EMA Cross')
    elif strategy.position_size < 0 and barstate.isconfirmed:
        if close > short_stop_loss and barstate.isconfirmed:
            strategy.close('Pivot Down', 'Exit Shorts Stopped', alert_message='Exit Shorts Stopped')
            strategy.close('Pivot Pin Bar Down', 'Exit Shorts Stopped', alert_message='Exit Shorts Stopped')
        elif close <= twoxshort_take_profit and (adx <= 25 or close > close[3]) and barstate.isconfirmed:
            if entry == 1 and barstate.isconfirmed:
                take_profit = threexshort_take_profit
            if entry == 0 and barstate.isconfirmed:
                entry = 1
                stop_loss = short_take_profit
                strategy.exit('Exit Shorts', 'Pivot Down', stop=short_stop_loss, limit=short_take_profit, alert_message='Exit Shorts')
                strategy.exit('Exit Shorts', 'Pivot Pin Bar Down', stop=short_stop_loss, limit=short_take_profit, alert_message='Exit Shorts')
        elif src_5m > ema_5m and tradingMinute - short_entry_minute > 3 and (adx <= 25 or close > close[3]) and barstate.isconfirmed:
            strategy.exit('Exit Shorts 5 Min EMA Cross', 'Pivot Down', stop=short_stop_loss, limit=short_take_profit, alert_message='Exit Shorts 5 Min EMA Cross')
            strategy.exit('Exit Shorts 5 Min EMA Cross', 'Pivot Pin Bar Down', stop=short_stop_loss, limit=short_take_profit, alert_message='Exit Shorts 5 Min EMA Cross')
    if time > long_entry_time + (time - time[1]) * min_bars_between_trades and barstate.isconfirmed:
        allow_long_entry = True
        allow_trades = True
    if time > short_entry_time + (time - time[1]) * min_bars_between_trades and barstate.isconfirmed:
        allow_short_entry = True
        allow_trades = True
    if hour == 15 and minute >= 55 and barstate.isconfirmed:
        allow_trades = False
    if hour == 9 and minute <= 35 and barstate.isconfirmed:
        allow_trades = False
    if hour == 15 and minute == 57 and (strategy.position_size != 0) and barstate.isconfirmed:
        strategy.close('Pivot Up', alert_message='Market Closing')
        strategy.close('Pivot Down', alert_message='Market Closing')
        strategy.close('Pivot Pin Bar Up', alert_message='Market Closing')
        strategy.close('Pivot Pin Bar Down', alert_message='Market Closing')
        hourlyclose = 1
    if hourlyclose == 1 and barstate.isconfirmed:
        hourlyclose = 0


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
