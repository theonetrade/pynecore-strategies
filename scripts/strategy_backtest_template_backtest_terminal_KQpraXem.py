"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from enum import StrEnum as Enum
from pynecore.lib import (
    barstate, close, color, fill, format, high, hour, input, location, low,
    math, minute, na, nz, open, plot, plotshape, script, shape, size, strategy, string, syminfo,
    ta, time, timeframe, timestamp
)
from pynecore.types import Persistent, PersistentSeries, Series


class StopTargetMode(Enum):
    percentage = '% (Percentage)'
    forexCfd = 'Point - Forex / CFD'
    cryptoStock = 'Dollar - Crypto / Stock'


class StopMode(Enum):
    fixed = 'Fixed'
    trailing = 'Trailing'
    breakeven = 'Breakeven'


class TradeDir(Enum):
    long = 'LONG'
    short = 'SHORT'
    both = 'BOTH'


class SessionMode(Enum):
    off = 'Off'
    blackout = 'Blackout'
    tradeOnly = 'Trade Only'


class Timezone(Enum):
    utcMinus12 = 'UTC-12'
    utcMinus11 = 'UTC-11'
    utcMinus10 = 'UTC-10 (Hawaii)'
    utcMinus9 = 'UTC-9  (Alaska)'
    utcMinus8 = 'UTC-8  (Los Angeles)'
    utcMinus7 = 'UTC-7  (Denver / Phoenix)'
    utcMinus6 = 'UTC-6  (Chicago / Mexico City)'
    utcMinus5 = 'UTC-5  (New York / Toronto)'
    utcMinus4 = 'UTC-4  (New York DST / Santiago)'
    utcMinus3 = 'UTC-3  (São Paulo / Buenos Aires)'
    utcMinus2 = 'UTC-2'
    utcMinus1 = 'UTC-1  (Azores)'
    utc0 = 'UTC+0  (London / Lisbon)'
    utcPlus1 = 'UTC+1  (London DST / Paris / Frankfurt)'
    utcPlus2 = 'UTC+2  (Cairo / Johannesburg)'
    utcPlus3 = 'UTC+3  (Moscow / Riyadh / Istanbul)'
    utcPlus4 = 'UTC+4  (Dubai / Baku)'
    utcPlus5 = 'UTC+5  (Karachi / Tashkent)'
    utcPlus530 = 'UTC+5:30 (Mumbai / New Delhi)'
    utcPlus6 = 'UTC+6  (Dhaka / Almaty)'
    utcPlus7 = 'UTC+7  (Bangkok / Jakarta / Hanoi)'
    utcPlus8 = 'UTC+8  (Singapore / Hong Kong)'
    utcPlus9 = 'UTC+9  (Tokyo / Seoul)'
    utcPlus930 = 'UTC+9:30 (Adelaide)'
    utcPlus10 = 'UTC+10 (Sydney / Melbourne)'
    utcPlus11 = 'UTC+11 (Solomon Islands)'
    utcPlus12 = 'UTC+12 (Auckland / Fiji)'


g_Trig: str = "🔵 Trigger — Your Signal Inputs"
g_Filt: str = "🟡 Filter — Your Filter Inputs"
g_Backtest: str = "SELECT DATE RANGE"
g_days: str = "SELECT TRADING DAY"
g_Windows: str = "🕐 TRADE WINDOWS  (enter times in your local timezone)"
g_TD: str = "SELECT TRADE DIRECTION"
g_SM: str = "STOP MODE"
g_ST: str = "TAKE PROFIT & STOP LOSS"
g_Disp: str = "HIDE / SHOW SIGNALS"
g_Alert: str = "⏰ SELECT ALERT MODE"
g_longEn: str = "🤖🟢 LONG ENTRY (CUSTOM MESSAGE)"
g_longEx: str = "🤖🟢 LONG EXIT (CUSTOM MESSAGE)"
g_shortEn: str = "🤖🔴 SHORT ENTRY (CUSTOM MESSAGE)"
g_shortEx: str = "🤖🔴 SHORT EXIT (CUSTOM MESSAGE)"
g_AltMsg: str = "COPY THIS AND PASTE IN ALERT MESSAGE BOX"


@script.strategy(title="Backtest Template [Backtest Terminal]", shorttitle="BTT", overlay=True, default_qty_type=strategy.fixed, default_qty_value=1, initial_capital=10000, commission_type=strategy.commission.cash_per_contract, commission_value=0.07, slippage=2, margin_long=0, margin_short=0)
def main(
    fast_len=input.int(9, "Fast MA Length", minval=1, group=g_Trig, tooltip="Length of the fast EMA.\nWhen the fast MA crosses ABOVE the slow MA → Long signal.\nWhen the fast MA crosses BELOW the slow MA → Short signal."),
    slow_len=input.int(21, "Slow MA Length", minval=1, group=g_Trig, tooltip="Length of the slow EMA.\nAct as the reference line for the fast MA to cross."),
    trend_len=input.int(200, "Trend MA Length", minval=1, group=g_Filt, tooltip="Length of the trend EMA used as the filter reference line.\nLong  entries are only allowed when price is above this MA.\nShort entries are only allowed when price is below this MA.\nSet both filter variables to [true] to disable filtering entirely."),
    start_date=input.time(timestamp('01 1 2000 00:00 +0000'), "Backtest Start", group=g_Backtest, tooltip="The strategy will only place trades on or after this date.\nDefault Jan 1 2000 = from the beginning of available data."),
    end_date=input.time(timestamp('01 1 2050 00:00 +0000'), "Backtest End", group=g_Backtest, tooltip="The strategy will stop placing trades after this date.\nDefault Jan 1 2050 = no end limit."),
    tradeSession=input.session("0000-0000", "Trade Session", group=g_days, tooltip="Allowed trading hours in exchange server time (HHMM-HHMM).\nDefault 0000-0000 = 24 hours, no restriction.\nExample: 0900-1700 = trade only between 9 AM and 5 PM exchange time.\nNote: uses exchange server time, not your local time."),
    d_sunday=input.bool(True, "Sun.", group=g_days, inline="days", tooltip="Check the days the strategy is allowed to trade.\nUnchecking a day prevents new entries — open positions are still managed on unchecked days."),
    d_monday=input.bool(True, "Mon.", group=g_days, inline="days"),
    d_tuesday=input.bool(True, "Tue.", group=g_days, inline="days"),
    d_wednesday=input.bool(True, "Wed.", group=g_days, inline="days"),
    d_thursday=input.bool(True, "Thu.", group=g_days, inline="days"),
    d_friday=input.bool(True, "Fri.", group=g_days, inline="days"),
    d_saturday=input.bool(True, "Sat.", group=g_days, inline="days"),
    tzInput=input.enum(Timezone.utcPlus7, "My Timezone", group=g_Windows, tooltip="Select your local timezone.\nAll window times below must be entered in this timezone."),
    sessionMode_1=input.enum(SessionMode.off, "Tokyo   ", group=g_Windows, inline="s1", tooltip="Tokyo open reference times:\nUTC+9=07:00 | UTC+7=05:00 | UTC+0=22:00 | UTC-5=17:00\n\nOff        : this window has no effect\nBlackout   : block entries while inside this window\nTrade Only : only allow entries while inside this window"),
    s1_start=input.string("0200", "", group=g_Windows, inline="s1"),
    s1_end=input.string("0400", "", group=g_Windows, inline="s1"),
    sessionMode_2=input.enum(SessionMode.off, "London  ", group=g_Windows, inline="s2", tooltip="London open reference times:\nUTC+0=08:00 | UTC+1=09:00 | UTC+7=15:00 | UTC-5=03:00\n\nOff        : this window has no effect\nBlackout   : block entries while inside this window\nTrade Only : only allow entries while inside this window"),
    s2_start=input.string("1500", "", group=g_Windows, inline="s2"),
    s2_end=input.string("1700", "", group=g_Windows, inline="s2"),
    sessionMode_3=input.enum(SessionMode.off, "New York", group=g_Windows, inline="s3", tooltip="New York open reference times:\nUTC-5=09:30 | UTC+0=14:30 | UTC+7=21:30 | UTC+9=23:30\n\nOff        : this window has no effect\nBlackout   : block entries while inside this window\nTrade Only : only allow entries while inside this window"),
    s3_start=input.string("1930", "", group=g_Windows, inline="s3"),
    s3_end=input.string("2130", "", group=g_Windows, inline="s3"),
    sessionMode_4=input.enum(SessionMode.off, "Custom  ", group=g_Windows, inline="s4", tooltip="Define your own custom time window in your local timezone.\n\nOff        : this window has no effect\nBlackout   : block entries while inside this window\nTrade Only : only allow entries while inside this window"),
    s4_start=input.string("0000", "", group=g_Windows, inline="s4"),
    s4_end=input.string("0000", "", group=g_Windows, inline="s4"),
    tradeDirection=input.enum(TradeDir.both, "Trade Direction", group=g_TD),
    stopMode=input.enum(StopMode.fixed, "Stop Mode", group=g_SM, tooltip="Fixed     : Stop loss stays at the original level until hit or TP reached.\nTrailing  : Stop loss follows price — locks in profit as price moves.\nBreakeven : Stop loss moves to entry price once price moves in your favour."),
    useNoTp=input.bool(False, "Disable Take Profit (trailing stop manages exit)", group=g_SM, tooltip="When ON : no fixed Take Profit level is placed — the Trailing Stop is the only exit.\nWhen OFF: Take Profit fires at the level set in the Stop / Target Mode section.\nHas no effect when Stop Mode = Fixed or Breakeven."),
    __input_29__=input.float(3.0, "[%] Trailing Stop ( % )", minval=0.0, step=0.1, group=g_SM, tooltip="Active when Stop Mode = Trailing  AND  Stop/Target Mode = % (Percentage).\nThe stop trails this % below price (Long) or above price (Short)."),
    trailingStopPt=input.int(50, "[P] Trailing Stop (point)", minval=1, step=10, group=g_SM, tooltip="Active when Stop Mode = Trailing  AND  Stop/Target Mode = Point - Forex / CFD.\nThe stop trails this many points behind price.\nExample: 50 points on EURUSD (tick=0.00001) = 5 pip trailing distance."),
    trailingStopDol=input.float(100.0, "[$] Trailing Stop ($)", minval=0.1, step=10.0, group=g_SM, tooltip="Active when Stop Mode = Trailing  AND  Stop/Target Mode = Dollar - Crypto / Stock.\nThe stop trails this dollar amount behind price.\nExample: 100 on BTCUSD = $100 trailing distance."),
    trailingStopOff=input.float(0.0, "[%] Trailing Offset ( % )", minval=0.0, step=0.05, group=g_SM, tooltip="Active when Stop Mode = Trailing  AND  Stop/Target Mode = % (Percentage).\nPrice must move this % from entry before trailing activates.\nSet to 0 to trail immediately.\nShown as a yellow line on the chart."),
    trailingOffPt=input.int(0, "[P] Trailing Offset (point)", minval=0, step=10, group=g_SM, tooltip="Active when Stop Mode = Trailing  AND  Stop/Target Mode = Point - Forex / CFD.\nPrice must move this many points before trailing activates.\nSet to 0 to trail immediately.\nShown as a yellow line on the chart."),
    trailingOffDol=input.float(0.0, "[$] Trailing Offset ($)", minval=0.0, step=10.0, group=g_SM, tooltip="Active when Stop Mode = Trailing  AND  Stop/Target Mode = Dollar - Crypto / Stock.\nPrice must move this dollar amount before trailing activates.\nSet to 0 to trail immediately.\nShown as a yellow line on the chart."),
    breakevenStopOff=input.float(1.0, "[%] Breakeven Offset ( % )", minval=0.0, step=0.05, group=g_SM, tooltip="Active when Stop Mode = Breakeven  AND  Stop/Target Mode = % (Percentage).\nPrice must move this % from entry before the stop moves to entry price.\nShown as a white line on the chart."),
    breakevenOffPt=input.int(10, "[P] Breakeven Offset (point)", minval=0, step=10, group=g_SM, tooltip="Active when Stop Mode = Breakeven  AND  Stop/Target Mode = Point - Forex / CFD.\nPrice must move this many points before the stop moves to entry price.\nShown as a white line on the chart."),
    breakevenOffDol=input.float(50.0, "[$] Breakeven Offset ($)", minval=0.0, step=10.0, group=g_SM, tooltip="Active when Stop Mode = Breakeven  AND  Stop/Target Mode = Dollar - Crypto / Stock.\nPrice must move this dollar amount before the stop moves to entry price.\nShown as a white line on the chart."),
    positionType=input.enum(StopTargetMode.forexCfd, "Stop / Target Mode", group=g_ST, tooltip="How Stop Loss and Take Profit distances are calculated.\n% (Percentage)          : % of price — uses [%] inputs below.\nPoint - Forex / CFD     : instrument tick size — uses [P] inputs below.\nDollar - Crypto / Stock : direct price distance — uses [$] inputs below."),
    positionSrc=input.string("Close", "[%] Fixed Stop Source", options=("Close", "High/Low"), group=g_ST, tooltip="Active when Stop/Target Mode = % (Percentage).\nClose    : stop distance is calculated from the close price.\nHigh/Low : stop distance is calculated from the candle High (short) or Low (long)."),
    stopLoss=input.float(3.0, "[%] Stop Loss ( % )", minval=0.05, step=0.05, group=g_ST),
    riskReward=input.float(2.0, "[%] Risk : Reward ( 1 : ? )", minval=0.1, step=0.05, group=g_ST, tooltip="Take profit is derived from stop loss distance × this ratio."),
    stoploss_point=input.int(100, "[P] Stop Loss (point)", minval=1, step=10, group=g_ST, tooltip="Active when Stop/Target Mode = Point - Forex / CFD.\nExample: 100 points on EURUSD (tick=0.00001) = 0.00100 price distance."),
    takeProfit_point=input.int(200, "[P] Take Profit (point)", minval=1, step=10, group=g_ST, tooltip="Active when Stop/Target Mode = Point - Forex / CFD.\nExample: 200 points on EURUSD (tick=0.00001) = 0.00200 price distance."),
    stoploss_dollar=input.float(100.0, "[$] Stop Loss ($)", minval=0.1, step=10.0, group=g_ST, tooltip="Active when Stop/Target Mode = Dollar - Crypto / Stock.\nExample: 100 on BTCUSD = $100 stop distance from entry."),
    takeProfit_dollar=input.float(200.0, "[$] Take Profit ($)", minval=0.1, step=10.0, group=g_ST, tooltip="Active when Stop/Target Mode = Dollar - Crypto / Stock.\nExample: 200 on BTCUSD = $200 take profit distance from entry."),
    hideAllSignals=input.bool(False, "🚫 Hide Entry Signals On Chart", group=g_Disp, tooltip="Hides the green / red triangle markers on the chart.\nDoes not affect strategy logic or backtest results."),
    alertMode=input.string("App Alert", "App Alert / Custom message", options=("App Alert", "Custom"), group=g_Alert, tooltip="App Alert : sends a pre-formatted text message with ticker, direction, stop and target.\nCustom    : sends the JSON string you paste into the four inputs below.\n\nFor both modes: create a TradingView alert and paste {{strategy.order.alert_message}} into the alert message box."),
    LongEntryCode=input.string("", "", group=g_longEn, tooltip="Paste your single-line JSON here for the Long Entry event.\nThis fires when a Long position opens.\nExample action value: enter_long"),
    LongExitCode=input.string("", "", group=g_longEx, tooltip="Paste your single-line JSON here for the Long Exit event.\nThis fires when a Long position closes via TP, SL, or trailing stop.\nExample action value: exit_long"),
    ShortEntryCode=input.string("", "", group=g_shortEn, tooltip="Paste your single-line JSON here for the Short Entry event.\nThis fires when a Short position opens.\nExample action value: enter_short"),
    ShortExitCode=input.string("", "", group=g_shortEx, tooltip="Paste your single-line JSON here for the Short Exit event.\nThis fires when a Short position closes via TP, SL, or trailing stop.\nExample action value: exit_short"),
    altMsg_copy=input.string("{{strategy.order.alert_message}}", "Select all and copy this ➤", group=g_AltMsg, tooltip="Copy this string exactly and paste it into the TradingView alert message box.\nThis is required for both App Alert mode and Custom JSON mode.\nWithout this, alerts will not deliver the correct message.")
):
    confirmed = barstate.isconfirmed

    fast_ma = ta.ema(close, fast_len)
    slow_ma = ta.ema(close, slow_len)

    userLong = ta.crossover(fast_ma, slow_ma) and confirmed
    userShort = ta.crossunder(fast_ma, slow_ma) and confirmed

    plot(fast_ma, 'Fast MA', color.new(color.aqua, 0), 2)
    plot(slow_ma, 'Slow MA', color.new(color.fuchsia, 0), 2)

    trend_ma = ta.ema(close, trend_len)

    userFilterLong = close > trend_ma
    userFilterShort = close < trend_ma

    plot(trend_ma, 'Trend Filter MA', color.new(color.orange, 0), 2)

    timeOk = time >= start_date and time <= end_date



    trailingStopPerc = __input_29__ * 0.01






    __block_result__ = na
    __switch__ = tzInput
    if __switch__ == Timezone.utcMinus12:
        __block_result__ = -12.0
    elif __switch__ == Timezone.utcMinus11:
        __block_result__ = -11.0
    elif __switch__ == Timezone.utcMinus10:
        __block_result__ = -10.0
    elif __switch__ == Timezone.utcMinus9:
        __block_result__ = -9.0
    elif __switch__ == Timezone.utcMinus8:
        __block_result__ = -8.0
    elif __switch__ == Timezone.utcMinus7:
        __block_result__ = -7.0
    elif __switch__ == Timezone.utcMinus6:
        __block_result__ = -6.0
    elif __switch__ == Timezone.utcMinus5:
        __block_result__ = -5.0
    elif __switch__ == Timezone.utcMinus4:
        __block_result__ = -4.0
    elif __switch__ == Timezone.utcMinus3:
        __block_result__ = -3.0
    elif __switch__ == Timezone.utcMinus2:
        __block_result__ = -2.0
    elif __switch__ == Timezone.utcMinus1:
        __block_result__ = -1.0
    elif __switch__ == Timezone.utc0:
        __block_result__ = 0.0
    elif __switch__ == Timezone.utcPlus1:
        __block_result__ = 1.0
    elif __switch__ == Timezone.utcPlus2:
        __block_result__ = 2.0
    elif __switch__ == Timezone.utcPlus3:
        __block_result__ = 3.0
    elif __switch__ == Timezone.utcPlus4:
        __block_result__ = 4.0
    elif __switch__ == Timezone.utcPlus5:
        __block_result__ = 5.0
    elif __switch__ == Timezone.utcPlus530:
        __block_result__ = 5.5
    elif __switch__ == Timezone.utcPlus6:
        __block_result__ = 6.0
    elif __switch__ == Timezone.utcPlus7:
        __block_result__ = 7.0
    elif __switch__ == Timezone.utcPlus8:
        __block_result__ = 8.0
    elif __switch__ == Timezone.utcPlus9:
        __block_result__ = 9.0
    elif __switch__ == Timezone.utcPlus930:
        __block_result__ = 9.5
    elif __switch__ == Timezone.utcPlus10:
        __block_result__ = 10.0
    elif __switch__ == Timezone.utcPlus11:
        __block_result__ = 11.0
    elif __switch__ == Timezone.utcPlus12:
        __block_result__ = 12.0
    else:
        __block_result__ = 0.0
    utcOffsetHours = __block_result__

    def parseTime(t):
        h = math.floor(string.tonumber(t) / 100)
        m = string.tonumber(t) - h * 100
        return h * 60 + m

    def inWindow(startStr, endStr, offsetHours):
        startLocal = parseTime(startStr)
        endLocal = parseTime(endStr)
        offsetMins = math.round(offsetHours * 60)
        startUtc = (startLocal - offsetMins) % (24 * 60)
        endUtc = (endLocal - offsetMins) % (24 * 60)
        startUtc = startUtc + 24 * 60 if startUtc < 0 else startUtc
        endUtc = endUtc + 24 * 60 if endUtc < 0 else endUtc
        nowUtc = hour(time, 'UTC') * 60 + minute(time, 'UTC')
        return nowUtc >= startUtc or nowUtc < endUtc if startUtc >= endUtc else nowUtc >= startUtc and nowUtc < endUtc

    isBlackedOut = sessionMode_1 == SessionMode.blackout and inWindow(s1_start, s1_end, utcOffsetHours) or (sessionMode_2 == SessionMode.blackout and inWindow(s2_start, s2_end, utcOffsetHours)) or (sessionMode_3 == SessionMode.blackout and inWindow(s3_start, s3_end, utcOffsetHours)) or (sessionMode_4 == SessionMode.blackout and inWindow(s4_start, s4_end, utcOffsetHours))

    anyTradeOnly = sessionMode_1 == SessionMode.tradeOnly or sessionMode_2 == SessionMode.tradeOnly or sessionMode_3 == SessionMode.tradeOnly or (sessionMode_4 == SessionMode.tradeOnly)

    isInTradeWindow = not anyTradeOnly or (sessionMode_1 == SessionMode.tradeOnly and inWindow(s1_start, s1_end, utcOffsetHours)) or (sessionMode_2 == SessionMode.tradeOnly and inWindow(s2_start, s2_end, utcOffsetHours)) or (sessionMode_3 == SessionMode.tradeOnly and inWindow(s3_start, s3_end, utcOffsetHours)) or (sessionMode_4 == SessionMode.tradeOnly and inWindow(s4_start, s4_end, utcOffsetHours))

    days = '1' if d_sunday else ''
    days = days + ('2' if d_monday else '')
    days = days + ('3' if d_tuesday else '')
    days = days + ('4' if d_wednesday else '')
    days = days + ('5' if d_thursday else '')
    days = days + ('6' if d_friday else '')
    days = days + ('7' if d_saturday else '')
    def inSession(sess):
        return na(time(timeframe.period, sess + ':' + days)) == False

    entryLong = userLong and userFilterLong and (tradeDirection != TradeDir.short) and (not isBlackedOut) and isInTradeWindow and inSession(tradeSession) and timeOk

    entryShort = userShort and userFilterShort and (tradeDirection != TradeDir.long) and (not isBlackedOut) and isInTradeWindow and inSession(tradeSession) and timeOk

    t_stop: Persistent[float] = 0.0
    t_target: Persistent[float] = 0.0
    entry: Persistent[float] = 0.0
    longStopPrice: PersistentSeries[float] = 0.0
    shortStopPrice: PersistentSeries[float] = 0.0

    validLong: Series = entryLong and strategy.position_size[1] == 0 and confirmed
    validShort: Series = entryShort and strategy.position_size[1] == 0 and confirmed

    longStopSrc = close if positionSrc == 'Close' else low
    L_Stop_Perc = low - stopLoss * longStopSrc / 100
    divider = 1 / syminfo.mintick if positionType == StopTargetMode.forexCfd else 1
    sl_points = stoploss_point / divider if positionType == StopTargetMode.forexCfd else stoploss_dollar
    tp_points = takeProfit_point / divider if positionType == StopTargetMode.forexCfd else takeProfit_dollar
    L_Stop_Point = close - sl_points
    longStop = L_Stop_Perc if positionType == StopTargetMode.percentage else L_Stop_Point
    longStopDist = close - longStop
    L_Target_Perc = close + longStopDist * riskReward
    L_Target_Point = close + tp_points
    longTarget = L_Target_Perc if positionType == StopTargetMode.percentage else L_Target_Point

    brStopOff_Long = close + close * breakevenStopOff / 100 if positionType == StopTargetMode.percentage else close + breakevenOffPt * syminfo.mintick if positionType == StopTargetMode.forexCfd else close + breakevenOffDol
    trStopOff_Long = close + close * trailingStopOff / 100 if positionType == StopTargetMode.percentage else close + trailingOffPt * syminfo.mintick if positionType == StopTargetMode.forexCfd else close + trailingOffDol

    shortStopSrc = close if positionSrc == 'Close' else high
    S_Stop_Perc = high + stopLoss * shortStopSrc / 100
    S_Stop_Point = close + sl_points
    shortStop = S_Stop_Perc if positionType == StopTargetMode.percentage else S_Stop_Point
    shortStopDist = shortStop - close
    S_Target_Perc = close - shortStopDist * riskReward
    S_Target_Point = close - tp_points
    shortTarget = S_Target_Perc if positionType == StopTargetMode.percentage else S_Target_Point

    brStopOff_Short = close - close * breakevenStopOff / 100 if positionType == StopTargetMode.percentage else close - breakevenOffPt * syminfo.mintick if positionType == StopTargetMode.forexCfd else close - breakevenOffDol
    trStopOff_Short = close - close * trailingStopOff / 100 if positionType == StopTargetMode.percentage else close - trailingOffPt * syminfo.mintick if positionType == StopTargetMode.forexCfd else close - trailingOffDol

    trailDist = close * trailingStopPerc if positionType == StopTargetMode.percentage else trailingStopPt * syminfo.mintick if positionType == StopTargetMode.forexCfd else trailingStopDol

    __block_result_1__ = na
    if strategy.position_size > 0:
        __block_result_1__ = math.max(close - trailDist, longStopPrice[1])
    else:
        __block_result_1__ = 0
    longStopPrice = __block_result_1__

    __block_result_2__ = na
    if strategy.position_size < 0:
        __block_result_2__ = math.min(close + trailDist, shortStopPrice[1])
    else:
        __block_result_2__ = 999999
    shortStopPrice = __block_result_2__

    tr_act_lev: Series[float] = 0.0
    tr_act_lev = trStopOff_Long if validLong else trStopOff_Short if validShort else nz(tr_act_lev[1])

    tr_act_status: Series[bool] = False
    tr_act_status = False if validLong or validShort else True if strategy.position_size[1] > 0 and high > tr_act_lev or (strategy.position_size[1] < 0 and low < tr_act_lev) else tr_act_status[1]

    tr_stop_lev: Series[float] = 0.0
    tr_stop_lev = longStop if validLong else shortStop if validShort else longStopPrice if tr_act_status and strategy.position_size[1] > 0 else shortStopPrice if tr_act_status and strategy.position_size[1] < 0 else nz(tr_stop_lev[1])

    br_lev: Series[float] = 0.0
    br_lev = close if validLong or validShort else open if validLong[1] or validShort[1] else nz(br_lev[1])

    act_lev: Series[float] = 0.0
    act_lev = brStopOff_Long if validLong else brStopOff_Short if validShort else nz(act_lev[1])

    act_status: Series[bool] = False
    act_status = False if validLong or validShort else True if strategy.position_size[1] > 0 and high > act_lev or (strategy.position_size[1] < 0 and low < act_lev) else act_status[1]

    sl_lev: Series[float] = 0.0
    sl_lev = longStop if validLong else shortStop if validShort else br_lev if act_status and strategy.position_size[1] != 0 else nz(sl_lev[1])

    if (validLong or validShort) and strategy.position_size[1] == 0:
        t_stop = longStop if validLong else shortStop
        t_target = longTarget if validLong else shortTarget
        entry = close

    alertLongEntry = '[ {{ticker}} : {{exchange}} ]\n' + '🟢 ENTRY LONG   : {{close}}\n' + '🟡 STOP LOSS    : ' + string.tostring(longStop, format.mintick) + '\n' + '🔵 TARGET PRICE : ' + string.tostring(longTarget, format.mintick) + '\n'

    alertShortEntry = '[ {{ticker}} : {{exchange}} ]\n' + '🔴 ENTRY SHORT  : {{close}}\n' + '🟡 STOP LOSS    : ' + string.tostring(shortStop, format.mintick) + '\n' + '🔵 TARGET PRICE : ' + string.tostring(shortTarget, format.mintick) + '\n'

    if validLong and strategy.position_size == 0:
        strategy.entry(id='LONG', direction=strategy.long, alert_message=LongEntryCode if alertMode == 'Custom' else alertLongEntry)
        t_stop = longStop
        t_target = longTarget

    if validShort and strategy.position_size == 0:
        strategy.entry(id='SHORT', direction=strategy.short, alert_message=ShortEntryCode if alertMode == 'Custom' else alertShortEntry)
        t_stop = shortStop
        t_target = shortTarget

    long_PNL = (close - entry) / entry * 100
    short_PNL = (entry - close) / entry * 100

    alertLongExit = '[ {{ticker}} : {{exchange}} ]\n' + '🟢 EXIT LONG  : {{close}}\n' + ' 💰[ＰＮＬ ：' + string.tostring(long_PNL, format.mintick) + '％ ]\n'

    alertShortExit = '[ {{ticker}} : {{exchange}} ]\n' + '🔴 EXIT SHORT : {{close}}\n' + ' 💰[ＰＮＬ ：' + string.tostring(short_PNL, format.mintick) + '％ ]\n'

    if strategy.position_size > 0:
        strategy.exit(id='LONG EXIT', from_entry='LONG', limit=na if useNoTp else t_target, stop=tr_stop_lev if stopMode == StopMode.trailing else sl_lev if stopMode == StopMode.breakeven else t_stop, alert_message=LongExitCode if alertMode == 'Custom' else alertLongExit)

    if strategy.position_size < 0:
        strategy.exit(id='SHORT EXIT', from_entry='SHORT', limit=na if useNoTp else t_target, stop=tr_stop_lev if stopMode == StopMode.trailing else sl_lev if stopMode == StopMode.breakeven else t_stop, alert_message=ShortExitCode if alertMode == 'Custom' else alertShortExit)

    plotshape(False if hideAllSignals else entryLong, title='Long Entry Signal', style=shape.triangleup, location=location.belowbar, color=color.rgb(0, 255, 0, 0), size=size.tiny, editable=False)
    plotshape(False if hideAllSignals else entryShort, title='Short Entry Signal', style=shape.triangledown, location=location.abovebar, color=color.rgb(255, 0, 0, 0), size=size.tiny, editable=False)

    slL = plot(t_stop if strategy.position_size > 0 and stopMode != StopMode.trailing else na, 'Long Stop Loss', style=plot.style_linebr, color=color.rgb(255, 0, 0, 90), linewidth=1, editable=False)
    enL = plot(entry if strategy.position_size > 0 else na, 'Long Entry', style=plot.style_linebr, color=color.rgb(255, 255, 0, 90), linewidth=1, editable=False)
    tpL = plot(t_target if strategy.position_size > 0 else na, 'Long Take Profit', style=plot.style_linebr, color=color.rgb(0, 255, 0, 90), linewidth=1, editable=False)
    trL = plot(tr_stop_lev if strategy.position_size > 0 and stopMode == StopMode.trailing else na, 'Long Trail Stop', style=plot.style_linebr, color=color.new(color.red, 60), linewidth=1, editable=False)

    trailColL = color.rgb(204, 45, 45, 80) if tr_stop_lev < entry else color.rgb(204, 45, 45, 100)

    fill(tpL, enL, color=color.rgb(32, 140, 118, 80), title='Long TP Background', editable=False)
    fill(enL, slL, color=color.rgb(204, 45, 45, 80), title='Long SL Background', editable=False)
    fill(enL, trL, color=trailColL, title='Long Trailing Background', editable=False)

    plot(tr_act_lev if strategy.position_size > 0 and stopMode == StopMode.trailing else na, 'Long Trail Offset', color=color.new(color.yellow, 70), style=plot.style_linebr, linewidth=1, editable=False)
    plot(act_lev if strategy.position_size > 0 and stopMode == StopMode.breakeven else na, 'Long Breakeven Offset', color=color.new(color.white, 70), style=plot.style_linebr, linewidth=1, editable=False)

    slS = plot(t_stop if strategy.position_size < 0 and stopMode != StopMode.trailing else na, 'Short Stop Loss', style=plot.style_linebr, color=color.rgb(255, 0, 0, 90), linewidth=1, editable=False)
    enS = plot(entry if strategy.position_size < 0 else na, 'Short Entry', style=plot.style_linebr, color=color.rgb(255, 255, 0, 90), linewidth=1, editable=False)
    tpS = plot(t_target if strategy.position_size < 0 else na, 'Short Take Profit', style=plot.style_linebr, color=color.rgb(0, 255, 0, 90), linewidth=1, editable=False)
    trS = plot(tr_stop_lev if strategy.position_size < 0 and stopMode == StopMode.trailing else na, 'Short Trail Stop', style=plot.style_linebr, color=color.new(color.red, 60), linewidth=1, editable=False)

    trailColS = color.rgb(204, 45, 45, 80) if tr_stop_lev > entry else color.rgb(204, 45, 45, 100)

    fill(tpS, enS, color=color.rgb(32, 140, 118, 80), title='Short TP Background', editable=False)
    fill(enS, slS, color=color.rgb(204, 45, 45, 80), title='Short SL Background', editable=False)
    fill(enS, trS, color=trailColS, title='Short Trailing Background', editable=False)

    plot(tr_act_lev if strategy.position_size < 0 and stopMode == StopMode.trailing else na, 'Short Trail Offset', color=color.new(color.yellow, 70), style=plot.style_linebr, linewidth=1, editable=False)
    plot(act_lev if strategy.position_size < 0 and stopMode == StopMode.breakeven else na, 'Short Breakeven Offset', color=color.new(color.white, 70), style=plot.style_linebr, linewidth=1, editable=False)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
