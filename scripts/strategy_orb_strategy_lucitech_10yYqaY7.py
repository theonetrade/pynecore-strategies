"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, array, bar_index, bgcolor, close, color, dayofmonth, dayofweek,
    display, fill, high, hour, input, label, line, location, low, math, minute, month, na, plot,
    plotshape, request, script, shape, size, strategy, string, syminfo, ta, time, timestamp,
    volume, year
)
from pynecore.types import Box, Color, Line, Persistent, Series

sltip: str = 'Defines the stop-loss length based on candles. 0 means 1 candle, 1 means 2 candles, and so on.'
betip: str = 'Enter the R multiple at which the stop loss moves to breakeven. 0 means breakeven is disabled.'
rrtip: str = 'The risk-reward ratio determines the relationship between potential reward and risk. For example, 3 means risking 1 unit to gain 3 units.'
risk_percent_tip: str = 'The percentage of your equity that you are willing to risk per trade.'
sl_type_tip: str = 'Choose the stop-loss calculation type: ATR-based, Candle-based, or Midline (ORB midpoint).'
ATRlength_tip: str = 'The number of periods used to calculate the Average True Range (ATR).'
smoothing_tip: str = 'Choose the smoothing method for ATR: RMA, SMA, EMA, or WMA.'
ATRlines_tip: str = 'Enable or disable plotting of ATR-based stop-loss lines.'
time_filter_tip: str = 'Enable or disable the time filter. When disabled, trades can occur at any time.'
day_filter_tip: str = 'Enable or disable the day filter. When enabled, trades only occur on selected days of the week.'
group_alert: str = 'Alert Settings'


@script.strategy('ORB Strategy [LuciTech]', overlay=True, max_bars_back=500, max_lines_count=500, max_boxes_count=500, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, margin_long=0, margin_short=0, close_by_id=True, na_bool=True)
def main(
    use_time_filter=input.bool(False, title='Use Time Filter', group='Time Filter', tooltip=time_filter_tip),
    start_hour=input.int(defval=0, title='Start Hour (24h)', minval=0, maxval=23, group='Time Filter'),
    start_minute=input.int(defval=59, title='Start Minute', minval=0, maxval=59, group='Time Filter'),
    end_hour=input.int(defval=23, title='End Hour (24h)', minval=0, maxval=23, group='Time Filter'),
    end_minute=input.int(defval=59, title='End Minute', minval=0, maxval=59, group='Time Filter'),
    showFill=input.bool(defval=False, title='Fill Background', inline='colour1', group='Time Filter'),
    fillColor=input.color(color.rgb(192, 192, 192, 90), title='', inline='colour1', group='Time Filter'),
    use_day_filter=input.bool(False, title='Use Day Filter', group='Day Filter', tooltip=day_filter_tip),
    monday=input.bool(True, title='Monday', inline='days1', group='Day Filter'),
    tuesday=input.bool(True, title='Tuesday', inline='days1', group='Day Filter'),
    wednesday=input.bool(True, title='Wednesday', inline='days1', group='Day Filter'),
    thursday=input.bool(True, title='Thursday', inline='days2', group='Day Filter'),
    friday=input.bool(True, title='Friday', inline='days2', group='Day Filter'),
    saturday=input.bool(False, title='Saturday', inline='days3', group='Day Filter'),
    sunday=input.bool(False, title='Sunday', inline='days3', group='Day Filter'),
    use_month_filter=input.bool(False, title='Use Month Filter', group='Month Filter', tooltip='Enable to restrict trading to specific months'),
    january=input.bool(True, title='January', inline='months1', group='Month Filter'),
    february=input.bool(True, title='February', inline='months1', group='Month Filter'),
    march=input.bool(True, title='March', inline='months1', group='Month Filter'),
    april=input.bool(True, title='April', inline='months2', group='Month Filter'),
    may=input.bool(True, title='May', inline='months2', group='Month Filter'),
    june=input.bool(True, title='June', inline='months2', group='Month Filter'),
    july=input.bool(True, title='July', inline='months3', group='Month Filter'),
    august=input.bool(True, title='August', inline='months3', group='Month Filter'),
    september=input.bool(True, title='September', inline='months3', group='Month Filter'),
    october=input.bool(True, title='October', inline='months4', group='Month Filter'),
    november=input.bool(True, title='November', inline='months4', group='Month Filter'),
    december=input.bool(True, title='December', inline='months4', group='Month Filter'),
    use_position_filter=input.bool(False, title='Use Position Type Filter', group='Position Type', tooltip='Enable to restrict trading to specific position types'),
    allow_long=input.bool(True, title='Allow Long', inline='positions', group='Position Type'),
    allow_short=input.bool(True, title='Allow Short', inline='positions', group='Position Type'),
    __input_31__=input.float(2, title='Risk %', minval=0.1, maxval=100, group='Risk Management', tooltip=risk_percent_tip),
    Risk_reward=input.float(defval=2, title='Risk:Reward', minval=1, maxval=10, step=0.1, group='Risk Management', tooltip=rrtip),
    breakeven=input.float(0, title='Breakeven at R', minval=0.0, step=0.1, group='Risk Management', tooltip=betip),
    sl_type=input.string('ATR', title='Stop Loss Type', options=('ATR', 'Candle', 'Midline'), group='Risk Management', tooltip=sl_type_tip),
    SL_length=input(0, title='Candle Length', group='Risk Management', tooltip=sltip),
    ATRlength=input.int(title='ATR length', defval=14, minval=1, group='Risk Management', tooltip=ATRlength_tip),
    smoothing=input.string(title='ATR Smoothing/ATR Lines', defval='SMA', options=('RMA', 'SMA', 'EMA', 'WMA'), group='Risk Management', tooltip=smoothing_tip),
    ATRlines=input(False, 'Show ATR Lines', group='Risk Management', tooltip=ATRlines_tip),
    ATRmulti=input.float(0, title='ATRMulti', group='Risk Management', tooltip=sltip, step=0.1),
    use_rvol_filter=input.bool(False, title='Use RVOL Filter', group='Relative Volume', tooltip='Only allow entries when current bar volume exceeds the average by the set multiplier'),
    rvol_length=input.int(20, title='RVOL Lookback (bars)', minval=2, group='Relative Volume', tooltip='Number of bars used to calculate the average volume baseline'),
    rvol_threshold=input.float(1.5, title='Minimum RVOL', minval=0.1, step=0.1, group='Relative Volume', tooltip='Entry is only allowed when volume / avg_volume >= this value. e.g. 1.5 = 50% above average'),
    rvol_show_label=input.bool(False, title='Show RVOL Value on Signal Bar', group='Relative Volume', tooltip='Displays the RVOL ratio on the chart at each breakout bar for debugging/review'),
    entrypricecolour=input.color(color.rgb(244, 244, 244, 75), title='Entry/SL/TP', group='Style', inline='peb'),
    stoplosscolour=input.color(color.rgb(255, 0, 0, 75), title='', group='Style', inline='peb'),
    takeprofitcolour=input.color(color.rgb(0, 255, 0, 75), title='', group='Style', inline='peb'),
    use_webhook_alerts=input.bool(True, 'Use Webhook Alerts', group=group_alert, tooltip='Enable to send webhook alerts with trade information in JSON format'),
    webhook_format=input.string('Concise Telegram', title='Webhook Format', options=('Standard', 'Telegram', 'Concise Telegram'), group=group_alert),
    telegram_chat_id=input.string('tele chatid', title='Telegram Chat ID', group=group_alert),
    highColor=input.color(color.green, 'High Line Color'),
    lowColor=input.color(color.red, 'Low Line Color'),
    midlineColor=input.color(color.white, 'Midline Color'),
    linewidth=input.int(2, 'Line Width', minval=1, maxval=4),
    showHistory=input.bool(True, 'Show Previous ORBs'),
    maxSavedOrbs=input.int(5, 'Show previous number of ORBs')
):
    fillcolour_tip: str = 'Select the background color to visually indicate the active time filter range on the chart.'
    risk_percent = __input_31__ / 100
    def ma_function(source, ATRlength):
        __block_result__ = na
        if smoothing == 'RMA':
            __block_result__ = ta.rma(source, ATRlength)
        elif smoothing == 'SMA':
            __block_result__ = ta.sma(source, ATRlength)
        elif smoothing == 'EMA':
            __block_result__ = ta.ema(source, ATRlength)
        else:
            __block_result__ = ta.wma(source, ATRlength)
        return __block_result__

    a = ma_function(ta.tr(True), ATRlength) * ATRmulti
    x = ma_function(ta.tr(True), ATRlength) * ATRmulti + high
    x2 = low - ma_function(ta.tr(True), ATRlength) * ATRmulti
    p1 = plot(x if ATRlines else na, title='ATR Short Stop Loss', color=stoplosscolour, trackprice=ATRlines)
    p2 = plot(x2 if ATRlines else na, title='ATR Long Stop Loss', color=takeprofitcolour, trackprice=ATRlines)
    avg_volume = ta.sma(volume, rvol_length)
    rvol = volume / avg_volume if avg_volume > 0 else 1.0
    rvol_pass = not use_rvol_filter or rvol >= rvol_threshold
    def is_within_time_window():
        current_time = time('1', 'America/New_York')
        start_time = timestamp(year(current_time), month(current_time), dayofmonth(current_time), start_hour, start_minute, 0)
        end_time = timestamp(year(current_time), month(current_time), dayofmonth(current_time), end_hour, end_minute, 0)
        return current_time >= start_time and current_time <= end_time

    def is_valid_trading_day():
        current_day = dayofweek(time)
        day_allowed: bool = False
        if current_day == 2 and monday:
            day_allowed = True
        elif current_day == 3 and tuesday:
            day_allowed = True
        elif current_day == 4 and wednesday:
            day_allowed = True
        elif current_day == 5 and thursday:
            day_allowed = True
        elif current_day == 6 and friday:
            day_allowed = True
        elif current_day == 7 and saturday:
            day_allowed = True
        elif current_day == 1 and sunday:
            day_allowed = True
        return day_allowed

    def is_valid_trading_month():
        current_month = month(time)
        month_allowed: bool = False
        if current_month == 1 and january:
            month_allowed = True
        elif current_month == 2 and february:
            month_allowed = True
        elif current_month == 3 and march:
            month_allowed = True
        elif current_month == 4 and april:
            month_allowed = True
        elif current_month == 5 and may:
            month_allowed = True
        elif current_month == 6 and june:
            month_allowed = True
        elif current_month == 7 and july:
            month_allowed = True
        elif current_month == 8 and august:
            month_allowed = True
        elif current_month == 9 and september:
            month_allowed = True
        elif current_month == 10 and october:
            month_allowed = True
        elif current_month == 11 and november:
            month_allowed = True
        elif current_month == 12 and december:
            month_allowed = True
        return month_allowed

    def is_valid_position_type(direction):
        position_allowed: bool = False
        if direction == 'LONG' and allow_long:
            position_allowed = True
        elif direction == 'SHORT' and allow_short:
            position_allowed = True
        return position_allowed

    is_within_time_window_1 = is_within_time_window()
    in_standard_time_range = not use_time_filter or is_within_time_window_1
    is_valid_trading_day_1 = is_valid_trading_day()
    in_valid_day = not use_day_filter or is_valid_trading_day_1
    is_valid_trading_month_1 = is_valid_trading_month()
    in_valid_month = not use_month_filter or is_valid_trading_month_1
    is_valid_position_type_1 = is_valid_position_type('LONG')
    in_valid_position_long = not use_position_filter or is_valid_position_type_1
    is_valid_position_type_2 = is_valid_position_type('SHORT')
    in_valid_position_short = not use_position_filter or is_valid_position_type_2
    inTimeRange = in_standard_time_range and in_valid_day and in_valid_month
    bgColor: Persistent[Color] = na(Color)
    is_within_time_window_2 = is_within_time_window()
    bgColor = fillColor if showFill and use_time_filter and is_within_time_window_2 else na
    bgcolor(bgColor)
    startTime = timestamp('America/New_York', year, month, dayofmonth, 9, 30)
    endTime = timestamp('America/New_York', year, month, dayofmonth, 9, 45)
    cutoffTime = timestamp('America/New_York', year, month, dayofmonth, 11, 0)
    inSession: Series = time >= startTime and time < endTime
    pastCutoff = time >= cutoffTime
    orbHighLines: Persistent[list[Line]] = array.new_line()
    orbLowLines: Persistent[list[Line]] = array.new_line()
    orbMidLines: Persistent[list[Line]] = array.new_line()
    fibLines: Persistent[list[Line]] = array.new_line()
    sessionHigh: Persistent[float] = na(float)
    sessionLow: Persistent[float] = na(float)
    mid: Persistent[float] = na(float)
    orb_index: Persistent[int] = na(int)
    liveHighLine: Persistent[Line] = na(Line)
    liveLowLine: Persistent[Line] = na(Line)
    liveMidLine: Persistent[Line] = na(Line)
    start_index: Persistent[int] = na(int)
    sessionFinalized: Persistent[bool] = False
    bullFired: Persistent[bool] = False
    bearFired: Persistent[bool] = False
    prevHighLine: Persistent[Line] = na(Line)
    prevLowLine: Persistent[Line] = na(Line)
    prevHigh = request.security(syminfo.tickerid, 'D', high[1])
    prevLow = request.security(syminfo.tickerid, 'D', low[1])
    if dayofmonth != dayofmonth[1]:
        start_index = bar_index
    if not inSession[1] and inSession:
        bullFired = False
        bearFired = False
    if not inSession[1] and inSession and showHistory:
        finalHigh = line.new(x1=orb_index, y1=sessionHigh, x2=bar_index - 1, y2=sessionHigh, color=highColor, width=linewidth, style=line.style_solid)
        finalLow = line.new(x1=orb_index, y1=sessionLow, x2=bar_index - 1, y2=sessionLow, color=lowColor, width=linewidth, style=line.style_solid)
        finalMid = line.new(x1=orb_index, y1=mid, x2=bar_index - 1, y2=mid, color=midlineColor, width=linewidth, style=line.style_solid)
        array.push(orbHighLines, finalHigh)
        array.push(orbLowLines, finalLow)
        array.push(orbMidLines, finalMid)
        if array.size(orbHighLines) > maxSavedOrbs:
            line.delete(array.shift(orbHighLines))
            line.delete(array.shift(orbLowLines))
            line.delete(array.shift(orbMidLines))
    if not inSession[1] and inSession:
        orb_index = bar_index
        sessionHigh = na
        sessionLow = na
        mid = na
        sessionFinalized = False
        line.delete(liveHighLine)
        line.delete(liveLowLine)
        line.delete(liveMidLine)
        liveHighLine = na
        liveLowLine = na
        liveMidLine = na
    if inSession:
        sessionHigh = high if na(sessionHigh) else math.max(sessionHigh, high)
        sessionLow = low if na(sessionLow) else math.min(sessionLow, low)
        mid = (sessionHigh + sessionLow) / 2
        line.delete(liveHighLine)
        line.delete(liveLowLine)
        line.delete(liveMidLine)
        liveHighLine = line.new(x1=orb_index, y1=sessionHigh, x2=bar_index + 2, y2=sessionHigh, color=highColor, width=linewidth)
        liveLowLine = line.new(x1=orb_index, y1=sessionLow, x2=bar_index + 2, y2=sessionLow, color=lowColor, width=linewidth)
        liveMidLine = line.new(x1=orb_index, y1=mid, x2=bar_index + 2, y2=mid, color=midlineColor, width=linewidth)
    if not inSession:
        line.set_x2(liveHighLine, bar_index + 2)
        line.set_x2(liveLowLine, bar_index + 2)
        line.set_x2(liveMidLine, bar_index + 2)
    orbLevelsReady = not na(sessionHigh) and (not na(sessionLow)) and (not na(mid)) and (not inSession) and (not pastCutoff)
    bullBreakout = orbLevelsReady and (not bullFired) and (close > sessionHigh) and (close[1] <= sessionHigh)
    if bullBreakout:
        bullFired = True
    bearBreakout = orbLevelsReady and (not bearFired) and (close < sessionLow) and (close[1] >= sessionLow)
    if bearBreakout:
        bearFired = True
    plotshape(bullBreakout, title='Bull ORB Break', style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small)
    plotshape(bearBreakout, title='Bear ORB Break', style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small)
    if rvol_show_label and (bullBreakout or bearBreakout):
        label.new(bar_index, low if bullBreakout else high, text='RVOL: ' + string.tostring(rvol, '#.##'), style=label.style_label_up if bullBreakout else label.style_label_down, color=color.new(color.green, 60) if rvol_pass else color.new(color.red, 60), textcolor=color.white, size=size.small)
    longCondition = inTimeRange and bullBreakout and in_valid_position_long and rvol_pass
    shortCondition = inTimeRange and bearBreakout and in_valid_position_short and rvol_pass
    stop_level: Persistent[float] = na(float)
    target_level: Persistent[float] = na(float)
    entry_price: Persistent[float] = na(float)
    initial_stop: Persistent[float] = na(float)
    moved_to_breakeven: Persistent[bool] = False
    current_bull_box: Persistent[Box] = na(Box)
    current_bear_box: Persistent[Box] = na(Box)
    current_second_bull_box: Persistent[Box] = na(Box)
    current_second_bear_box: Persistent[Box] = na(Box)
    def calculate_position_size(stop_distance):
        __block_result_1__ = na
        if stop_distance > 0:
            risk_amount = strategy.equity * risk_percent
            position_size = risk_amount / stop_distance
            __block_result_1__ = math.floor(position_size / syminfo.mintick) * syminfo.mintick
        else:
            __block_result_1__ = na
        return __block_result_1__

    def create_alert_message(direction, sl_price, tp_price):
        return '{"type":"' + direction + '","instrument":"' + syminfo.ticker + '","sl":' + string.tostring(sl_price, '#.#####') + ',"tp":' + string.tostring(tp_price, '#.#####') + '}'

    def create_telegram_alert_message(direction, sl_price, tp_price):
        header = '🟢BUY SIGNAL' if direction == 'BUY' else '🔴SELL SIGNAL'
        y = string.tostring(year)
        m = string.tostring(month)
        d = string.tostring(dayofmonth)
        h = string.tostring(hour)
        min = string.tostring(minute)
        m = '0' + m if string.length(m) == 1 else m
        d = '0' + d if string.length(d) == 1 else d
        h = '0' + h if string.length(h) == 1 else h
        min = '0' + min if string.length(min) == 1 else min
        datetime_str = y + '-' + m + '-' + d + ' ' + h + ':' + min
        return '{"chat_id": "' + telegram_chat_id + '", "text": "' + header + '\\n\\n{[' + syminfo.prefix + ']:[' + syminfo.ticker + '], price = [' + string.tostring(close, '#.#####') + ']}\\nDateTime = [' + datetime_str + ']\\nSL: ' + string.tostring(sl_price, '#.#####') + '\\nTP: ' + string.tostring(tp_price, '#.#####') + '"}'

    def create_concise_telegram_alert_message(direction, sl_price, tp_price):
        header = '🟢BUY ' if direction == 'BUY' else '🔴SELL '
        return '{"chat_id": "' + telegram_chat_id + '", "text": "' + header + syminfo.ticker + '\\nPRICE = ' + string.tostring(close, '#.#####') + '\\nSL: ' + string.tostring(sl_price, '#.#####') + '\\nTP: ' + string.tostring(tp_price, '#.#####') + '"}'

    if strategy.position_size == 0:
        moved_to_breakeven = False
        if longCondition:
            __block_result_2__ = na
            __switch_2__ = sl_type
            if __switch_2__ == 'ATR':
                __block_result_2__ = x2
            elif __switch_2__ == 'Candle':
                __block_result_2__ = low[SL_length]
            elif __switch_2__ == 'Midline':
                __block_result_2__ = mid
            else:
                __block_result_2__ = low[SL_length]
            stop_level = __block_result_2__
            initial_stop = stop_level
            stop_distance = close - stop_level
            target_level = close + Risk_reward * stop_distance
            position_size = calculate_position_size(stop_distance)
            if use_webhook_alerts:
                __block_result_3__ = na
                __switch_3__ = webhook_format
                if __switch_3__ == 'Telegram':
                    __block_result_3__ = create_telegram_alert_message('BUY', stop_level, target_level)
                elif __switch_3__ == 'Concise Telegram':
                    __block_result_3__ = create_concise_telegram_alert_message('BUY', stop_level, target_level)
                else:
                    __block_result_3__ = create_alert_message('BUY', stop_level, target_level)
                alert_message = __block_result_3__
                alert(alert_message, alert.freq_once_per_bar)
            if not na(position_size) and position_size > 0:
                strategy.entry('Long', strategy.long, qty=position_size)
                strategy.exit('Exit Long', 'Long', stop=stop_level, limit=target_level)
                entry_price = close
        if shortCondition:
            __block_result_4__ = na
            __switch_2__ = sl_type
            if __switch_2__ == 'ATR':
                __block_result_4__ = x
            elif __switch_2__ == 'Candle':
                __block_result_4__ = high[SL_length]
            elif __switch_2__ == 'Midline':
                __block_result_4__ = mid
            else:
                __block_result_4__ = high[SL_length]
            stop_level = __block_result_4__
            initial_stop = stop_level
            stop_distance = stop_level - close
            target_level = close - Risk_reward * stop_distance
            position_size = calculate_position_size(stop_distance)
            if use_webhook_alerts:
                __block_result_5__ = na
                __switch_3__ = webhook_format
                if __switch_3__ == 'Telegram':
                    __block_result_5__ = create_telegram_alert_message('SELL', stop_level, target_level)
                elif __switch_3__ == 'Concise Telegram':
                    __block_result_5__ = create_concise_telegram_alert_message('SELL', stop_level, target_level)
                else:
                    __block_result_5__ = create_alert_message('SELL', stop_level, target_level)
                alert_message = __block_result_5__
                alert(alert_message, alert.freq_once_per_bar)
            if not na(position_size) and position_size > 0:
                strategy.entry('Short', strategy.short, qty=position_size)
                strategy.exit('Exit Short', 'Short', stop=stop_level, limit=target_level)
                entry_price = close
    if breakeven > 0 and strategy.position_size != 0:
        initial_risk = math.abs(entry_price - initial_stop)
        if strategy.position_size > 0:
            current_profit = high - entry_price
            if current_profit >= breakeven * initial_risk and (not moved_to_breakeven):
                moved_to_breakeven = True
                strategy.cancel('Exit Long')
                stop_level = entry_price
                strategy.exit('Exit Long', 'Long', stop=entry_price, limit=target_level)
        if strategy.position_size < 0:
            current_profit = entry_price - low
            if current_profit >= breakeven * initial_risk and (not moved_to_breakeven):
                moved_to_breakeven = True
                strategy.cancel('Exit Short')
                stop_level = entry_price
                strategy.exit('Exit Short', 'Short', stop=entry_price, limit=target_level)
    plot(entry_price if strategy.position_size != 0 else na, title='Entry Price', color=entrypricecolour, style=plot.style_linebr)
    plot(stop_level if strategy.position_size != 0 else na, title='Stop Loss', color=stoplosscolour, style=plot.style_linebr)
    plot(target_level if strategy.position_size != 0 else na, title='Take Profit', color=takeprofitcolour, style=plot.style_linebr)
    fill_extension: Persistent[int] = 0
    plot_entry = plot(entry_price if strategy.position_size != 0 else na, 'Entry for SL Fill', display=display.none, offset=fill_extension)
    plot_sl = plot(stop_level if strategy.position_size != 0 else na, 'SL for Fill', display=display.none)
    fill(plot_entry, plot_sl, color=stoplosscolour if strategy.position_size != 0 else na)
    plot_entry_tp = plot(entry_price if strategy.position_size != 0 else na, 'Entry for TP Fill', display=display.none, offset=fill_extension)
    plot_tp = plot(target_level if strategy.position_size != 0 else na, 'TP for Fill', display=display.none)
    fill(plot_entry_tp, plot_tp, color=takeprofitcolour if strategy.position_size != 0 else na)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
