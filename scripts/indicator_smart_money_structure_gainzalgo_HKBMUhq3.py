"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    bar_index, barstate, box, close, color, extend, high, hlc3, input, label,
    line, low, math, na, open, plot, position, request, script, size, string, syminfo, ta, table,
    volume
)
from pynecore.types import Box, Line, Persistent, PersistentSeries, Series, Table


@script.indicator('Smart Money Structure | GainzAlgo', overlay=True)
def main(
    length=input.int(5, 'Pivot Length', minval=1, maxval=20, step=1, tooltip='Number of bars to identify pivot highs and lows.'),
    momentum_threshold_base=input.float(0.01, 'Base Momentum Threshold (%)', minval=0.001, maxval=1.0, step=0.001, tooltip='Base percentage change for signals.'),
    tp_points=input.int(10, 'Take Profit (points)', minval=5, maxval=500, step=5),
    sl_points=input.int(10, 'Stop Loss (points)', minval=5, maxval=500, step=5),
    min_signal_distance=input.int(5, 'Min Signal Distance (bars)', minval=1, maxval=50, step=1),
    tp_box_height=input.float(0.5, 'TP Box Height % (Optional)', minval=0.1, maxval=2.0, step=0.1),
    pre_momentum_factor_base=input.float(0.5, 'Base Pre-Momentum Factor', minval=0.1, maxval=1.0, step=0.1, tooltip='Base factor for Get Ready signals.'),
    shortTrendPeriod=input.int(30, title='Short Trend Period', minval=10, maxval=100),
    longTrendPeriod=input.int(100, title='Long Trend Period', minval=50, maxval=200),
    use_momentum_filter=input.bool(True, 'Use Momentum Filter', group='Signal Filters', tooltip='Require price change to exceed momentum threshold.'),
    use_trend_filter=input.bool(True, 'Use Higher Timeframe Trend Filter', group='Signal Filters', tooltip='Require alignment with the selected higher timeframe trend.'),
    higher_tf_choice=input.string('5M', 'Higher Timeframe', options=('1M', '5M', '15M', '30M', '1H', '4H', 'D'), group='Signal Filters', tooltip='Choose the timeframe for the higher timeframe filter.'),
    use_lower_tf_filter=input.bool(True, 'Use Lower Timeframe Filter', group='Signal Filters', tooltip='Prevent signals against the selected lower timeframe trend.'),
    lower_tf_choice=input.string('5M', 'Lower Timeframe', options=('1M', '5M', '15M', '30M', '1H', '4H', 'D'), group='Signal Filters', tooltip='Choose the timeframe for the lower timeframe filter.'),
    use_volume_filter=input.bool(True, 'Use Volume Filter', group='Signal Filters', tooltip='Require volume above average (optional).'),
    use_breakout_filter=input.bool(True, 'Use Breakout Filter', group='Signal Filters', tooltip='Require price to break previous high/low (optional).'),
    show_get_ready=input.bool(False, 'Show Get Ready Signals', group='Signal Filters', tooltip='Enable or disable Get Ready signals.'),
    restrict_repeated_signals=input.bool(True, 'Restrict Repeated Signals', group='Signal Filters', tooltip='Prevent multiple signals in the same trend direction until trend changes.'),
    restrict_trend_tf_choice=input.string('5M', 'Restrict Trend Timeframe', options=('1M', '5M', '15M', '30M', '1H', '4H', 'D'), group='Signal Filters', tooltip='Choose the timeframe to check trend for restricting repeated signals.'),
    enable_liquidity_zones=input.bool(False, 'Enable Liquidity Zone Detection', group='Advanced Analysis Tools', tooltip='Identifies potential liquidity pools and sweep zones'),
    enable_market_profile=input.bool(True, 'Enable Market Profile Analysis', group='Advanced Analysis Tools', tooltip='Shows order flow imbalance and institutional activity'),
    enable_divergence_scanner=input.bool(True, 'Enable Divergence Scanner', group='Advanced Analysis Tools', tooltip='Detects price and momentum divergences for reversal signals'),
    enable_trend_analysis=input.bool(True, 'Enable Trend Strength Matrix', group='Advanced Analysis Tools', tooltip='Show detailed predictions for future trends across timeframes.'),
    volumeLongPeriod=input.int(50, 'Long Volume Period', minval=10, maxval=100, group='Volume Filter Settings'),
    volumeShortPeriod=input.int(5, 'Short Volume Period', minval=1, maxval=20, group='Volume Filter Settings'),
    breakoutPeriod=input.int(5, 'Breakout Period', minval=1, maxval=50, group='Breakout Filter Settings')
):
    atr_raw = ta.atr(14)
    atr = high - low if na(atr_raw) and bar_index > 0 else atr_raw
    volatility_factor = atr / close
    momentum_threshold = momentum_threshold_base * (1 + volatility_factor * 2)
    pre_momentum_factor = pre_momentum_factor_base * (1 - volatility_factor * 0.5)
    pre_momentum_threshold = momentum_threshold * pre_momentum_factor
    raw_cvd: Persistent[float] = 0.0
    delta_volume = volume if close > close[1] else -volume if close < close[1] else 0
    raw_cvd = raw_cvd + delta_volume
    cvd_level = 'Low' if math.abs(raw_cvd) < 10000 else 'Medium' if math.abs(raw_cvd) < 50000 else 'High'
    cvd_color = color.lime if raw_cvd > 0 else color.red if raw_cvd < 0 else color.yellow
    price_change = (close - close[1]) / close[1] * 100
    pivot_high = ta.pivothigh(high, length, length)
    pivot_low = ta.pivotlow(low, length, length)
    last_high: PersistentSeries[float] = na(float)
    last_low: PersistentSeries[float] = na(float)
    if not na(pivot_high):
        last_high = pivot_high
    if not na(pivot_low):
        last_low = pivot_low
    choch_sell_level: Persistent[float] = na(float)
    choch_buy_level: Persistent[float] = na(float)
    bos_sell_level: Persistent[float] = na(float)
    bos_buy_level: Persistent[float] = na(float)
    tp_sell_level: Persistent[float] = na(float)
    tp_buy_level: Persistent[float] = na(float)
    sl_sell_level: Persistent[float] = na(float)
    sl_buy_level: Persistent[float] = na(float)
    last_signal_bar: Persistent[int] = -min_signal_distance - 1
    last_signal: Persistent[str] = 'Neutral'
    last_trend: Persistent[int] = 0
    ema1M, vwap1M = request.security(syminfo.tickerid, '1', (ta.ema(close, 20), ta.vwap(hlc3)))
    ema5M, vwap5M = request.security(syminfo.tickerid, '5', (ta.ema(close, 20), ta.vwap(hlc3)))
    ema15M, vwap15M = request.security(syminfo.tickerid, '15', (ta.ema(close, 20), ta.vwap(hlc3)))
    ema30M, vwap30M = request.security(syminfo.tickerid, '30', (ta.ema(close, 20), ta.vwap(hlc3)))
    ema1H, vwap1H = request.security(syminfo.tickerid, '60', (ta.ema(close, 20), ta.vwap(hlc3)))
    ema4H, vwap4H = request.security(syminfo.tickerid, '240', (ta.ema(close, 20), ta.vwap(hlc3)))
    emaD, vwapD = request.security(syminfo.tickerid, 'D', (ta.ema(close, 20), ta.vwap(hlc3)))
    trend1M = 1 if close > ema1M and close > vwap1M else -1 if close < ema1M and close < vwap1M else 0
    trend5M = 1 if close > ema5M and close > vwap5M else -1 if close < ema5M and close < vwap5M else 0
    trend15M = 1 if close > ema15M and close > vwap15M else -1 if close < ema15M and close < vwap15M else 0
    trend30M = 1 if close > ema30M and close > vwap30M else -1 if close < ema30M and close < vwap30M else 0
    trend1H = 1 if close > ema1H and close > vwap1H else -1 if close < ema1H and close < vwap1H else 0
    trend4H = 1 if close > ema4H and close > vwap4H else -1 if close < ema4H and close < vwap4H else 0
    trendD = 1 if close > emaD and close > vwapD else -1 if close < emaD and close < vwapD else 0
    trend_strength_raw = trend1M + trend5M + trend15M + trend30M + trend1H + trend4H + trendD
    trend_strength = trend_strength_raw / 7 * 100
    system_confidence: Persistent[float] = 50.0
    if trend_strength_raw == 7 or trend_strength_raw == -7:
        system_confidence = 90.0
    elif trend_strength_raw >= 4 or trend_strength_raw <= -4:
        system_confidence = 75.0
    elif trend_strength_raw >= 2 or trend_strength_raw <= -2:
        system_confidence = 60.0
    else:
        system_confidence = 50.0
    higher_tf_trend: Persistent[int] = 0
    if higher_tf_choice == '1M':
        higher_tf_trend = trend1M
    elif higher_tf_choice == '5M':
        higher_tf_trend = trend5M
    elif higher_tf_choice == '15M':
        higher_tf_trend = trend15M
    elif higher_tf_choice == '30M':
        higher_tf_trend = trend30M
    elif higher_tf_choice == '1H':
        higher_tf_trend = trend1H
    elif higher_tf_choice == '4H':
        higher_tf_trend = trend4H
    elif higher_tf_choice == 'D':
        higher_tf_trend = trendD
    bullish_trend_ok = higher_tf_trend == 1
    bearish_trend_ok = higher_tf_trend == -1
    lower_tf_trend: Persistent[int] = 0
    if lower_tf_choice == '1M':
        lower_tf_trend = trend1M
    elif lower_tf_choice == '5M':
        lower_tf_trend = trend5M
    elif lower_tf_choice == '15M':
        lower_tf_trend = trend15M
    elif lower_tf_choice == '30M':
        lower_tf_trend = trend30M
    elif lower_tf_choice == '1H':
        lower_tf_trend = trend1H
    elif lower_tf_choice == '4H':
        lower_tf_trend = trend4H
    elif lower_tf_choice == 'D':
        lower_tf_trend = trendD
    lower_tf_bullish = lower_tf_trend == 1
    lower_tf_bearish = lower_tf_trend == -1
    lower_tf_not_neutral = lower_tf_trend != 0
    restrict_tf_trend: Persistent[int] = 0
    if restrict_trend_tf_choice == '1M':
        restrict_tf_trend = trend1M
    elif restrict_trend_tf_choice == '5M':
        restrict_tf_trend = trend5M
    elif restrict_trend_tf_choice == '15M':
        restrict_tf_trend = trend15M
    elif restrict_trend_tf_choice == '30M':
        restrict_tf_trend = trend30M
    elif restrict_trend_tf_choice == '1H':
        restrict_tf_trend = trend1H
    elif restrict_trend_tf_choice == '4H':
        restrict_tf_trend = trend4H
    elif restrict_trend_tf_choice == 'D':
        restrict_tf_trend = trendD
    volAvg50 = ta.sma(volume, volumeLongPeriod)
    volShort = ta.sma(volume, volumeShortPeriod)
    change_1 = ta.change(volShort)
    volCondition = volume > volAvg50 and change_1 > 0
    highestBreakout: Series = ta.highest(high, breakoutPeriod)
    lowestBreakout: Series = ta.lowest(low, breakoutPeriod)
    choch_sell = ta.crossunder(low, last_high) and close < open
    choch_buy = ta.crossover(high, last_low) and close > open
    bos_sell = ta.crossunder(low, last_low[1]) and low < last_low[1] and (close < open)
    bos_buy = ta.crossover(high, last_high[1]) and high > last_high[1] and (close > open)
    early_sell_signal = price_change < -momentum_threshold if use_momentum_filter else True
    early_buy_signal = price_change > momentum_threshold if use_momentum_filter else True
    sell_trend_ok = bearish_trend_ok if use_trend_filter else True
    buy_trend_ok = bullish_trend_ok if use_trend_filter else True
    sell_lower_tf_ok = not lower_tf_bullish and lower_tf_not_neutral if use_lower_tf_filter else True
    buy_lower_tf_ok = not lower_tf_bearish and lower_tf_not_neutral if use_lower_tf_filter else True
    sell_volume_ok = volCondition if use_volume_filter else True
    buy_volume_ok = volCondition if use_volume_filter else True
    sell_breakout_ok = close < lowestBreakout[1] if use_breakout_filter else True
    buy_breakout_ok = close > highestBreakout[1] if use_breakout_filter else True
    sell_allowed = not restrict_repeated_signals or last_signal != 'Sell' or (last_signal == 'Sell' and restrict_tf_trend != last_trend and (restrict_tf_trend != -1))
    buy_allowed = not restrict_repeated_signals or last_signal != 'Buy' or (last_signal == 'Buy' and restrict_tf_trend != last_trend and (restrict_tf_trend != 1))
    sell_condition = early_sell_signal and bar_index - last_signal_bar >= min_signal_distance and sell_trend_ok and sell_lower_tf_ok and sell_volume_ok and sell_breakout_ok and sell_allowed
    buy_condition = early_buy_signal and bar_index - last_signal_bar >= min_signal_distance and buy_trend_ok and buy_lower_tf_ok and buy_volume_ok and buy_breakout_ok and buy_allowed
    get_ready_sell = price_change < -pre_momentum_threshold and price_change > -momentum_threshold if use_momentum_filter else True and bar_index - last_signal_bar >= min_signal_distance and sell_trend_ok and sell_lower_tf_ok and sell_volume_ok and sell_breakout_ok
    get_ready_buy = price_change > pre_momentum_threshold and price_change < momentum_threshold if use_momentum_filter else True and bar_index - last_signal_bar >= min_signal_distance and buy_trend_ok and buy_lower_tf_ok and buy_volume_ok and buy_breakout_ok
    if enable_liquidity_zones:
        lookback: int = 20
        recent_high = ta.highest(high, lookback)
        if high >= recent_high * 0.9995 and high <= recent_high * 1.0005 and (bar_index > lookback):
            label.new(bar_index, high, '💧 LIQ', color=color.new(color.new('#FF6B35'), 80), style=label.style_label_down, textcolor=color.new('#FF6B35'), size=size.tiny)
        recent_low = ta.lowest(low, lookback)
        if low <= recent_low * 1.0005 and low >= recent_low * 0.9995 and (bar_index > lookback):
            label.new(bar_index, low, '💧 LIQ', color=color.new(color.new('#FF6B35'), 80), style=label.style_label_up, textcolor=color.new('#FF6B35'), size=size.tiny)
    if enable_market_profile:
        recent_buy_vol: Persistent[float] = 0.0
        recent_sell_vol: Persistent[float] = 0.0
        if close > open:
            recent_buy_vol = ta.sma(volume, 20)
        elif close < open:
            recent_sell_vol = ta.sma(volume, 20)
        vol_ratio = recent_buy_vol / (recent_buy_vol + recent_sell_vol) if recent_buy_vol > 0 and recent_sell_vol > 0 else 0.5
        strong_buy_flow = vol_ratio > 0.65 and volume > volAvg50 * 1.5
        strong_sell_flow = vol_ratio < 0.35 and volume > volAvg50 * 1.5
        if strong_buy_flow:
            label.new(bar_index, low, '🔥 BUY', color=color.new(color.new('#00D9FF'), 70), style=label.style_label_up, textcolor=color.white, size=size.small)
        if strong_sell_flow:
            label.new(bar_index, high, '🔥 SELL', color=color.new(color.new('#FF006E'), 70), style=label.style_label_down, textcolor=color.white, size=size.small)
    if enable_divergence_scanner:
        rsi: Series = ta.rsi(close, 14)
        price_lower_low = low < low[5] and low[5] < low[10]
        rsi_higher_low = rsi > rsi[5] and rsi[5] > rsi[10]
        bullish_divergence = price_lower_low and rsi_higher_low and (rsi < 40)
        price_higher_high = high > high[5] and high[5] > high[10]
        rsi_lower_high = rsi < rsi[5] and rsi[5] < rsi[10]
        bearish_divergence = price_higher_high and rsi_lower_high and (rsi > 60)
        if bullish_divergence:
            label.new(bar_index, low, '⚡ BULL', color=color.new(color.new('#00F5FF'), 60), style=label.style_label_up, textcolor=color.white, size=size.small)
        if bearish_divergence:
            label.new(bar_index, high, '⚡ BEAR', color=color.new(color.new('#C77DFF'), 60), style=label.style_label_down, textcolor=color.white, size=size.small)
    if show_get_ready and get_ready_sell:
        label.new(bar_index, high, '⚠ READY', color=color.new(color.new('#FFB627'), 70), style=label.style_label_down, textcolor=color.white, size=size.small)
    if show_get_ready and get_ready_buy:
        label.new(bar_index, low, '⚠ READY', color=color.new(color.new('#FFB627'), 70), style=label.style_label_up, textcolor=color.white, size=size.small)
    if sell_condition:
        label.new(bar_index, high, '🔴 SELL', color=color.new(color.new('#FF1744'), 0), style=label.style_label_down, textcolor=color.white, size=size.normal)
        tp_sell_level = low - tp_points
        sl_sell_level = high + sl_points
        last_signal = 'Sell'
        last_signal_bar = bar_index
        last_trend = restrict_tf_trend
    if buy_condition:
        label.new(bar_index, low, '🟢 BUY', color=color.new(color.new('#00E676'), 0), style=label.style_label_up, textcolor=color.white, size=size.normal)
        tp_buy_level = high + tp_points
        sl_buy_level = low - sl_points
        last_signal = 'Buy'
        last_signal_bar = bar_index
        last_trend = restrict_tf_trend
    choch_sell_line: Persistent[Line] = na(Line)
    choch_buy_line: Persistent[Line] = na(Line)
    bos_sell_line: Persistent[Line] = na(Line)
    bos_buy_line: Persistent[Line] = na(Line)
    choch_sell_box: Persistent[Box] = na(Box)
    choch_buy_box: Persistent[Box] = na(Box)
    bos_sell_box: Persistent[Box] = na(Box)
    bos_buy_box: Persistent[Box] = na(Box)
    if choch_sell:
        line.delete(choch_sell_line)
        box.delete(choch_sell_box)
        choch_sell_level = last_high
        choch_sell_line = line.new(bar_index, choch_sell_level, bar_index + 1, choch_sell_level, color=color.new(color.new('#00E5FF'), 0), style=line.style_solid, width=2)
        choch_sell_box = box.new(bar_index - 2, choch_sell_level * 1.001, bar_index + 5, choch_sell_level * 0.999, bgcolor=color.new(color.new('#00E5FF'), 95), border_color=color.new(color.new('#00E5FF'), 80), border_width=1)
        label.new(bar_index, choch_sell_level, 'CHoCH', color=color.new(color.new('#00E5FF'), 85), textcolor=color.new('#00E5FF'), style=label.style_label_left, size=size.tiny)
    if choch_buy:
        line.delete(choch_buy_line)
        box.delete(choch_buy_box)
        choch_buy_level = last_low
        choch_buy_line = line.new(bar_index, choch_buy_level, bar_index + 1, choch_buy_level, color=color.new(color.new('#76FF03'), 0), style=line.style_solid, width=2)
        choch_buy_box = box.new(bar_index - 2, choch_buy_level * 1.001, bar_index + 5, choch_buy_level * 0.999, bgcolor=color.new(color.new('#76FF03'), 95), border_color=color.new(color.new('#76FF03'), 80), border_width=1)
        label.new(bar_index, choch_buy_level, 'CHoCH', color=color.new(color.new('#76FF03'), 85), textcolor=color.new('#76FF03'), style=label.style_label_left, size=size.tiny)
    if bos_sell:
        line.delete(bos_sell_line)
        box.delete(bos_sell_box)
        bos_sell_level = last_low[1]
        bos_sell_line = line.new(bar_index, bos_sell_level, bar_index + 1, bos_sell_level, color=color.new(color.new('#E040FB'), 0), style=line.style_solid, width=2)
        bos_sell_box = box.new(bar_index - 2, bos_sell_level * 1.001, bar_index + 5, bos_sell_level * 0.999, bgcolor=color.new(color.new('#E040FB'), 95), border_color=color.new(color.new('#E040FB'), 80), border_width=1)
        label.new(bar_index, bos_sell_level, 'BOS', color=color.new(color.new('#E040FB'), 85), textcolor=color.new('#E040FB'), style=label.style_label_left, size=size.tiny)
    if bos_buy:
        line.delete(bos_buy_line)
        box.delete(bos_buy_box)
        bos_buy_level = last_high[1]
        bos_buy_line = line.new(bar_index, bos_buy_level, bar_index + 1, bos_buy_level, color=color.new(color.new('#00BFA5'), 0), style=line.style_solid, width=2)
        bos_buy_box = box.new(bar_index - 2, bos_buy_level * 1.001, bar_index + 5, bos_buy_level * 0.999, bgcolor=color.new(color.new('#00BFA5'), 95), border_color=color.new(color.new('#00BFA5'), 80), border_width=1)
        label.new(bar_index, bos_buy_level, 'BOS', color=color.new(color.new('#00BFA5'), 85), textcolor=color.new('#00BFA5'), style=label.style_label_left, size=size.tiny)
    sup: Persistent[Line] = na(Line)
    res: Persistent[Line] = na(Line)
    if barstate.islast:
        lowest_y2: float = 60000
        lowest_x2: int = 0
        highest_y2: float = 0
        highest_x2: int = 0
        maxShortBars: int = math.min(shortTrendPeriod, bar_index)
        for i in pine_range(1, maxShortBars, 1):
            if low[i] < lowest_y2:
                lowest_y2 = low[i]
                lowest_x2 = i
            if high[i] > highest_y2:
                highest_y2 = high[i]
                highest_x2 = i
        lowest_y1: float = 60000
        lowest_x1: int = 0
        highest_y1: float = 0
        highest_x1: int = 0
        maxLongBars: int = math.min(longTrendPeriod, bar_index)
        for j in pine_range(shortTrendPeriod + 1, maxLongBars, 1):
            if low[j] < lowest_y1:
                lowest_y1 = low[j]
                lowest_x1 = j
            if high[j] > highest_y1:
                highest_y1 = high[j]
                highest_x1 = j
        trendStrength: int = trend_strength_raw
        if lowest_x1 > 0 and lowest_x2 > 0:
            line.delete(sup)
            sup = line.new(cast_int(bar_index - lowest_x1), lowest_y1, cast_int(bar_index - lowest_x2), lowest_y2, extend=extend.right, style=line.style_solid, width=3, color=(color.new(color.new('#00E676'), 30) if trendStrength >= 4 else color.new(color.new('#76FF03'), 40) if trendStrength >= 2 else color.new(color.new('#FFEB3B'), 50)) if trendStrength >= 1 else color.new(color.gray, 60))
        if highest_x1 > 0 and highest_x2 > 0:
            line.delete(res)
            res = line.new(cast_int(bar_index - highest_x1), highest_y1, cast_int(bar_index - highest_x2), highest_y2, extend=extend.right, style=line.style_solid, width=3, color=(color.new(color.new('#FF1744'), 30) if trendStrength <= -4 else color.new(color.new('#E040FB'), 40) if trendStrength <= -2 else color.new(color.new('#FFEB3B'), 50)) if trendStrength <= -1 else color.new(color.gray, 60))
    plot(choch_sell_level, 'CHoCH Sell', color=color.new(color.new('#00E5FF'), 70), style=plot.style_circles, linewidth=1)
    plot(choch_buy_level, 'CHoCH Buy', color=color.new(color.new('#76FF03'), 70), style=plot.style_circles, linewidth=1)
    plot(bos_sell_level, 'BOS Sell', color=color.new(color.new('#E040FB'), 70), style=plot.style_circles, linewidth=1)
    plot(bos_buy_level, 'BOS Buy', color=color.new(color.new('#00BFA5'), 70), style=plot.style_circles, linewidth=1)
    momentum_5m = request.security(syminfo.tickerid, '5', close - close[3])
    momentum_15m = request.security(syminfo.tickerid, '15', close - close[3])
    momentum_30m = request.security(syminfo.tickerid, '30', close - close[3])
    momentum_1h = request.security(syminfo.tickerid, '60', close - close[3])
    momentum_4h = request.security(syminfo.tickerid, '240', close - close[3])
    momentum_d = request.security(syminfo.tickerid, 'D', close - close[3])
    volatility_5m = request.security(syminfo.tickerid, '5', ta.atr(14))
    volatility_15m = request.security(syminfo.tickerid, '15', ta.atr(14))
    volatility_30m = request.security(syminfo.tickerid, '30', ta.atr(14))
    volatility_1h = request.security(syminfo.tickerid, '60', ta.atr(14))
    volatility_4h = request.security(syminfo.tickerid, '240', ta.atr(14))
    volatility_d = request.security(syminfo.tickerid, 'D', ta.atr(14))
    volatility_avg_5m = request.security(syminfo.tickerid, '5', ta.sma(ta.atr(14), 20))
    volatility_avg_15m = request.security(syminfo.tickerid, '15', ta.sma(ta.atr(14), 20))
    volatility_avg_30m = request.security(syminfo.tickerid, '30', ta.sma(ta.atr(14), 20))
    volatility_avg_1h = request.security(syminfo.tickerid, '60', ta.sma(ta.atr(14), 20))
    volatility_avg_4h = request.security(syminfo.tickerid, '240', ta.sma(ta.atr(14), 20))
    volatility_avg_d = request.security(syminfo.tickerid, 'D', ta.sma(ta.atr(14), 20))
    score_5m = trend5M + (0.5 if momentum_5m > 0 else -0.5 if momentum_5m < 0 else 0) + (0.5 if volatility_5m > volatility_avg_5m else 0)
    score_15m = trend15M + (0.5 if momentum_15m > 0 else -0.5 if momentum_15m < 0 else 0) + (0.5 if volatility_15m > volatility_avg_15m else 0)
    score_30m = trend30M + (0.5 if momentum_30m > 0 else -0.5 if momentum_30m < 0 else 0) + (0.5 if volatility_30m > volatility_avg_30m else 0)
    score_1h = trend1H + (0.5 if momentum_1h > 0 else -0.5 if momentum_1h < 0 else 0) + (0.5 if volatility_1h > volatility_avg_1h else 0)
    score_4h = trend4H + (0.5 if momentum_4h > 0 else -0.5 if momentum_4h < 0 else 0) + (0.5 if volatility_4h > volatility_avg_4h else 0)
    score_d = trendD + (0.5 if momentum_d > 0 else -0.5 if momentum_d < 0 else 0) + (0.5 if volatility_d > volatility_avg_d else 0)
    pred_5m = '▲' if score_5m > 0.5 else '▼' if score_5m < -0.5 else '━'
    pred_15m = '▲' if score_15m > 0.5 else '▼' if score_15m < -0.5 else '━'
    pred_30m = '▲' if score_30m > 0.5 else '▼' if score_30m < -0.5 else '━'
    pred_1h = '▲' if score_1h > 0.5 else '▼' if score_1h < -0.5 else '━'
    pred_4h = '▲' if score_4h > 0.5 else '▼' if score_4h < -0.5 else '━'
    pred_d = '▲' if score_d > 0.5 else '▼' if score_d < -0.5 else '━'
    trendTable: Persistent[Table] = table.new(position.top_right, columns=2, rows=11, bgcolor=color.new(color.new('#0A0E27'), 15), border_width=1, border_color=color.new(color.new('#00D9FF'), 50))
    if barstate.islast:
        table.cell(trendTable, 0, 0, '⚡ SMART MONEY', text_color=color.new(color.new('#00F5FF'), 0), text_size=size.normal, bgcolor=color.new(color.new('#1A1F3A'), 30))
        table.cell(trendTable, 1, 0, 'v3.0', text_color=color.new(color.new('#00D9FF'), 40), text_size=size.small, bgcolor=color.new(color.new('#1A1F3A'), 30))
        table.cell(trendTable, 0, 1, '📊 Strength', text_color=color.new(color.new('#FFFFFF'), 20), text_size=size.small, bgcolor=color.new(color.new('#0F1629'), 40))
        strength_color = color.new(color.new('#00E676'), 0) if trend_strength > 50 else color.new(color.new('#76FF03'), 0) if trend_strength > 0 else color.new(color.new('#FF6B35'), 0) if trend_strength > -50 else color.new(color.new('#FF1744'), 0)
        table.cell(trendTable, 1, 1, string.tostring(math.round(trend_strength)), text_color=strength_color, text_size=size.normal, bgcolor=color.new(color.new('#0F1629'), 40))
        table.cell(trendTable, 0, 2, '🎯 Confidence', text_color=color.new(color.new('#FFFFFF'), 20), text_size=size.small, bgcolor=color.new(color.new('#0F1629'), 40))
        conf_color = color.new(color.new('#00E5FF'), 0) if system_confidence >= 75 else color.new(color.new('#00D9FF'), 20) if system_confidence >= 60 else color.new(color.new('#FFB627'), 0)
        table.cell(trendTable, 1, 2, string.tostring(system_confidence) + '%', text_color=conf_color, text_size=size.normal, bgcolor=color.new(color.new('#0F1629'), 40))
        table.cell(trendTable, 0, 3, '💎 Volume', text_color=color.new(color.new('#FFFFFF'), 20), text_size=size.small, bgcolor=color.new(color.new('#0F1629'), 40))
        cvd_display = string.tostring(math.round(raw_cvd / 1000)) + 'K'
        table.cell(trendTable, 1, 3, cvd_display, text_color=cvd_color, text_size=size.small, bgcolor=color.new(color.new('#0F1629'), 40))
        table.cell(trendTable, 0, 4, '1M', text_color=color.new(color.new('#8B93FF'), 30), text_size=size.tiny, bgcolor=color.new(color.new('#0A0E27'), 50))
        table.cell(trendTable, 1, 4, '▲' if trend1M == 1 else '▼' if trend1M == -1 else '━', text_color=color.new(color.new('#76FF03'), 0) if trend1M == 1 else color.new(color.new('#FF1744'), 0) if trend1M == -1 else color.new(color.new('#FFB627'), 40), text_size=size.small, bgcolor=color.new(color.new('#0A0E27'), 50))
        table.cell(trendTable, 0, 5, '5M', text_color=color.new(color.new('#8B93FF'), 30), text_size=size.tiny, bgcolor=color.new(color.new('#0A0E27'), 50))
        table.cell(trendTable, 1, 5, '▲' if trend5M == 1 else '▼' if trend5M == -1 else '━', text_color=color.new(color.new('#76FF03'), 0) if trend5M == 1 else color.new(color.new('#FF1744'), 0) if trend5M == -1 else color.new(color.new('#FFB627'), 40), text_size=size.small, bgcolor=color.new(color.new('#0A0E27'), 50))
        table.cell(trendTable, 0, 6, '15M', text_color=color.new(color.new('#8B93FF'), 30), text_size=size.tiny, bgcolor=color.new(color.new('#0A0E27'), 50))
        table.cell(trendTable, 1, 6, '▲' if trend15M == 1 else '▼' if trend15M == -1 else '━', text_color=color.new(color.new('#76FF03'), 0) if trend15M == 1 else color.new(color.new('#FF1744'), 0) if trend15M == -1 else color.new(color.new('#FFB627'), 40), text_size=size.small, bgcolor=color.new(color.new('#0A0E27'), 50))
        table.cell(trendTable, 0, 7, '30M', text_color=color.new(color.new('#8B93FF'), 30), text_size=size.tiny, bgcolor=color.new(color.new('#0A0E27'), 50))
        table.cell(trendTable, 1, 7, '▲' if trend30M == 1 else '▼' if trend30M == -1 else '━', text_color=color.new(color.new('#76FF03'), 0) if trend30M == 1 else color.new(color.new('#FF1744'), 0) if trend30M == -1 else color.new(color.new('#FFB627'), 40), text_size=size.small, bgcolor=color.new(color.new('#0A0E27'), 50))
        table.cell(trendTable, 0, 8, '1H', text_color=color.new(color.new('#8B93FF'), 30), text_size=size.tiny, bgcolor=color.new(color.new('#0A0E27'), 50))
        table.cell(trendTable, 1, 8, '▲' if trend1H == 1 else '▼' if trend1H == -1 else '━', text_color=color.new(color.new('#76FF03'), 0) if trend1H == 1 else color.new(color.new('#FF1744'), 0) if trend1H == -1 else color.new(color.new('#FFB627'), 40), text_size=size.small, bgcolor=color.new(color.new('#0A0E27'), 50))
        table.cell(trendTable, 0, 9, '4H', text_color=color.new(color.new('#8B93FF'), 30), text_size=size.tiny, bgcolor=color.new(color.new('#0A0E27'), 50))
        table.cell(trendTable, 1, 9, '▲' if trend4H == 1 else '▼' if trend4H == -1 else '━', text_color=color.new(color.new('#76FF03'), 0) if trend4H == 1 else color.new(color.new('#FF1744'), 0) if trend4H == -1 else color.new(color.new('#FFB627'), 40), text_size=size.small, bgcolor=color.new(color.new('#0A0E27'), 50))
        table.cell(trendTable, 0, 10, '1D', text_color=color.new(color.new('#8B93FF'), 30), text_size=size.tiny, bgcolor=color.new(color.new('#0A0E27'), 50))
        table.cell(trendTable, 1, 10, '▲' if trendD == 1 else '▼' if trendD == -1 else '━', text_color=color.new(color.new('#76FF03'), 0) if trendD == 1 else color.new(color.new('#FF1744'), 0) if trendD == -1 else color.new(color.new('#FFB627'), 40), text_size=size.small, bgcolor=color.new(color.new('#0A0E27'), 50))
    if enable_trend_analysis:
        ai_table: Persistent[Table] = table.new(position.bottom_right, columns=7, rows=2, bgcolor=color.new(color.new('#0A0E27'), 15), border_width=1, border_color=color.new(color.new('#E040FB'), 50))
        if barstate.islast:
            table.cell(ai_table, 0, 0, '🔮 TREND', text_color=color.new(color.new('#E040FB'), 0), text_size=size.small, bgcolor=color.new(color.new('#1A1F3A'), 30))
            table.cell(ai_table, 1, 0, '5M', text_color=color.new(color.new('#FFFFFF'), 30), text_size=size.tiny, bgcolor=color.new(color.new('#1A1F3A'), 30))
            table.cell(ai_table, 2, 0, '15M', text_color=color.new(color.new('#FFFFFF'), 30), text_size=size.tiny, bgcolor=color.new(color.new('#1A1F3A'), 30))
            table.cell(ai_table, 3, 0, '30M', text_color=color.new(color.new('#FFFFFF'), 30), text_size=size.tiny, bgcolor=color.new(color.new('#1A1F3A'), 30))
            table.cell(ai_table, 4, 0, '1H', text_color=color.new(color.new('#FFFFFF'), 30), text_size=size.tiny, bgcolor=color.new(color.new('#1A1F3A'), 30))
            table.cell(ai_table, 5, 0, '4H', text_color=color.new(color.new('#FFFFFF'), 30), text_size=size.tiny, bgcolor=color.new(color.new('#1A1F3A'), 30))
            table.cell(ai_table, 6, 0, '1D', text_color=color.new(color.new('#FFFFFF'), 30), text_size=size.tiny, bgcolor=color.new(color.new('#1A1F3A'), 30))
            table.cell(ai_table, 0, 1, 'Predict', text_color=color.new(color.new('#C77DFF'), 20), text_size=size.tiny, bgcolor=color.new(color.new('#0F1629'), 40))
            table.cell(ai_table, 1, 1, pred_5m, text_color=color.new(color.new('#00E676'), 0) if pred_5m == '▲' else color.new(color.new('#FF1744'), 0) if pred_5m == '▼' else color.new(color.new('#FFB627'), 40), text_size=size.normal, bgcolor=color.new(color.new('#0F1629'), 40))
            table.cell(ai_table, 2, 1, pred_15m, text_color=color.new(color.new('#00E676'), 0) if pred_15m == '▲' else color.new(color.new('#FF1744'), 0) if pred_15m == '▼' else color.new(color.new('#FFB627'), 40), text_size=size.normal, bgcolor=color.new(color.new('#0F1629'), 40))
            table.cell(ai_table, 3, 1, pred_30m, text_color=color.new(color.new('#00E676'), 0) if pred_30m == '▲' else color.new(color.new('#FF1744'), 0) if pred_30m == '▼' else color.new(color.new('#FFB627'), 40), text_size=size.normal, bgcolor=color.new(color.new('#0F1629'), 40))
            table.cell(ai_table, 4, 1, pred_1h, text_color=color.new(color.new('#00E676'), 0) if pred_1h == '▲' else color.new(color.new('#FF1744'), 0) if pred_1h == '▼' else color.new(color.new('#FFB627'), 40), text_size=size.normal, bgcolor=color.new(color.new('#0F1629'), 40))
            table.cell(ai_table, 5, 1, pred_4h, text_color=color.new(color.new('#00E676'), 0) if pred_4h == '▲' else color.new(color.new('#FF1744'), 0) if pred_4h == '▼' else color.new(color.new('#FFB627'), 40), text_size=size.normal, bgcolor=color.new(color.new('#0F1629'), 40))
            table.cell(ai_table, 6, 1, pred_d, text_color=color.new(color.new('#00E676'), 0) if pred_d == '▲' else color.new(color.new('#FF1744'), 0) if pred_d == '▼' else color.new(color.new('#FFB627'), 40), text_size=size.normal, bgcolor=color.new(color.new('#0F1629'), 40))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
