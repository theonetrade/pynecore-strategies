"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alert, array, bar_index, barstate, bgcolor, box, close, color, dayofweek,
    hour, input, label, line, location, math, na, plot, plotchar, plotshape, position, script,
    shape, size, strategy, string, syminfo, ta, table, text, time
)
from pynecore.types import Color, Label, Line, Persistent, Series, Table

group_devma: str = '🌀 VoVix DEVMA Configuration'
group_adaptive: str = '🧠 Adaptive Intelligence'
group_execution: str = '⚡ Intelligent Execution'
group_session: str = '⏰ Session'
group_visuals: str = '🎨 Visual Effects'
group_dashboard: str = '🎨 Dashboard'


@script.strategy('VoVix DEVMA', shorttitle='🌌 VoVix', overlay=False, initial_capital=100000, default_qty_type=strategy.fixed, default_qty_value=1, commission_type=strategy.commission.cash_per_contract, commission_value=0.62, slippage=2, calc_on_every_tick=False, process_orders_on_close=False, max_bars_back=1000, margin_long=0, margin_short=0, close_by_id=True)
def main(
    devLen=input.int(59, '🧬 Deviation Lookback', minval=15, maxval=60, group=group_devma, tooltip='🎯 WHAT IT IS: The lookback period for calculating the standard deviation of the Average True Range (ATR).\n\n⚡ HOW IT WORKS: This is the foundational calculation of the entire system. It determines the \'character\' or \'normal range\' of volatility itself. The DEVMA lines then analyze this character to detect changes.\n\n📈 HIGHER (50-60): Looks at a wider history, creating a very stable, smooth volatility character reading. This is slower to react to new volatility paradigms.\n📉 LOWER (15-30): Focuses on recent history, making the character reading more dynamic and sensitive to recent changes.\n\n💡 PRO TIP: 59 is an unconventional but highly effective setting that avoids common cycle lengths (like 50 or 60), reducing the chance of harmonic distortion. It provides a stable yet relevant character analysis.'),
    fastVoVixLen=input.int(20, '⚡ Fast VoVix Length', minval=10, maxval=50, group=group_devma, tooltip='🎯 WHAT IT IS: The lookback period for the fast-reacting moving average of volatility\'s deviation.\n\n⚡ HOW IT WORKS: This is the \'signal line\' of the engine. It measures the short-term rhythm of market energy. A crossover of this line with the Slow DEVMA line generates a trade signal.\n\n📈 HIGHER (30-50): Creates a smoother, less responsive signal line. This results in fewer, but potentially more significant, signals.\n📉 LOWER (10-15): More sensitive to immediate shifts in volatility. This results in more signals, but they can be more prone to noise.\n\n💡 PRO TIP: A setting of 20 provides a robust default that captures most meaningful shifts without being overly sensitive on medium-term timeframes.'),
    slowVoVixLen=input.int(60, '🐌 Slow VoVix Length', minval=30, maxval=100, group=group_devma, tooltip='🎯 WHAT IT IS: The lookback period for the slow-reacting moving average of volatility\'s deviation.\n\n⚡ HOW IT WORKS: This is the \'regime line\' of the engine. It establishes the baseline of the market\'s current volatility character. The crossover between the Fast and Slow lines generates the trade signal.\n\n📈 HIGHER (80-100): Defines a very long-term, stable regime baseline. It\'s excellent for filtering out minor fluctuations and focusing on major shifts.\n📉 LOWER (30-50): Defines a more reactive, shorter-term regime. It will adapt more quickly to broad changes in market character.\n\n💡 PRO TIP: A 3:1 ratio between Slow and Fast (e.g., 60/20) is a classic and effective combination for crossover systems, providing a great balance between responsiveness and stability.'),
    ENABLE_ADAPTIVE=input.bool(True, '🧠 Enable Adaptive Features', group=group_adaptive, tooltip='🎯 WHAT IT IS: The master switch for the strategy\'s learning capabilities.\n\n⚡ HOW IT WORKS: When enabled, the strategy begins tracking its own performance (win rate, trade duration). This data is then used to intelligently adjust other parameters, like the time-based exit. Note: In this version, it does NOT control position sizing.\n\n💡 PRO TIP: Keep this enabled to allow the strategy to fine-tune its time-based exits based on recent performance. Disabling it makes the strategy fully static.'),
    ADAPTIVE_TIME_EXIT=input.bool(True, '⏰ Adaptive Time-Based Exit', group=group_adaptive, tooltip='🎯 WHAT IT IS: Allows the \'Maximum Bars in Trade\' setting to adjust itself based on performance.\n\n⚡ HOW IT WORKS: If the strategy is winning frequently, it might slightly extend the time limit to let winners run. If it\'s losing, it might tighten the time limit. Requires \'Enable Adaptive Features\' to be on.\n\n💡 PRO TIP: This is a useful feature for dynamically adjusting to changing market speeds without manual intervention.'),
    tradeQty=input.int(1, '📊 Trade Quantity', minval=1, maxval=100, group=group_execution, tooltip='🎯 WHAT IT IS: The fixed number of contracts or shares to use for every trade.\n\n⚡ HOW IT WORKS: This strategy version uses a fixed position size. Every trade, regardless of the signal or market conditions, will be for this amount.\n\n💡 PRO TIP: For risk management, always start with the smallest possible trade size (e.g., 1) when testing a strategy on a new asset or timeframe.'),
    USE_SMART_STOPS=input.bool(True, '🛡️ Smart Stop Loss', group=group_execution, tooltip='🎯 WHAT IT IS: Toggles the use of an ATR-based initial stop loss.\n\n⚡ HOW IT WORKS: When enabled, the strategy places a dynamic stop loss that adjusts its distance from the entry price based on the market\'s recent volatility (ATR). If disabled, no initial stop loss will be placed.\n\n💡 PRO TIP: It is highly recommended to always keep this enabled as a primary risk management tool. Disabling it significantly increases the risk profile of the strategy.'),
    ATR_SL_MULTIPLIER=input.float(2.0, '🎯 Stop Loss ATR Multiplier', minval=0.5, maxval=5.0, step=0.1, group=group_execution, tooltip='🎯 WHAT IT IS: The multiplier for the ATR value that determines the stop loss distance.\n\n⚡ HOW IT WORKS: The stop loss is placed at: `Entry Price - (ATR * Multiplier)` for longs, and `Entry Price + (ATR * Multiplier)` for shorts.\n\n📈 HIGHER (3.0-5.0): Places the stop loss further away, giving the trade more room to breathe. Decreases the chance of being stopped out by noise, but increases the loss amount if the stop is hit.\n📉 LOWER (0.5-1.5): Places a tighter stop loss. Reduces the potential loss on any single trade, but increases the risk of being stopped out prematurely.\n\n💡 PRO TIP: 2.0 is a widely used industry standard that often provides a good balance between managing risk and allowing a trade to develop.'),
    ATR_TP_MULTIPLIER=input.float(3.0, '💰 Take Profit ATR Multiplier', minval=1.0, maxval=10.0, step=0.1, group=group_execution, tooltip='🎯 WHAT IT IS: The multiplier for the ATR value that determines the take profit distance.\n\n⚡ HOW IT WORKS: This sets a fixed profit target based on current volatility. The value represents a risk/reward ratio relative to a 1.0 ATR move.\n\n📈 HIGHER (5.0-10.0): Aims for larger, \'home-run\' wins. This will naturally lead to a lower win rate, but each winning trade will be more impactful.\n📉 LOWER (1.5-2.5): Aims for smaller, more achievable wins. This will lead to a higher win rate, but lower average profit per trade.\n\n💡 PRO TIP: A value of 3.0 sets a 1.5:1 risk/reward ratio when using a 2.0 SL multiplier, which is a solid and professional baseline.'),
    USE_TRAILING_STOP=input.bool(True, '🏃 Use Trailing Stop', group=group_execution, tooltip='🎯 WHAT IT IS: Toggles the use of an ATR-based trailing stop to lock in profits on winning trades.\n\n⚡ HOW IT WORKS: Once price moves in your favor by the \'Trail Points\' amount, a moving stop is activated \'Trail Offset\' behind the price. This is a powerful tool for capturing the majority of a strong trend.\n\n💡 PRO TIP: Trailing stops are essential for this strategy\'s performance, as they allow it to capitalize on the full extent of volatility expansion moves. It is highly recommended to keep this enabled.'),
    TRAIL_POINTS_MULT=input.float(0.5, '🎯 Trail Points ATR Multiplier', minval=0.5, maxval=5.0, step=0.1, group=group_execution, tooltip='🎯 WHAT IT IS: The distance, in ATR multiples, that price must move in your favor before the trailing stop is activated.\n\n⚡ HOW IT WORKS: If this is set to 1.0, the trailing stop will only become active after the trade is in unrealized profit of at least 1 ATR.\n\n📈 HIGHER: Delays the activation of the trailing stop, giving the trade more room to move initially.\n📉 LOWER: Activates the trailing stop very quickly, moving to protect the position and reduce risk sooner.\n\n💡 PRO TIP: A small value like 0.5 ensures the trailing mechanism engages quickly to begin managing the trade and protecting capital as soon as possible.'),
    TRAIL_OFFSET_MULT=input.float(0.5, '📏 Trail Offset ATR Multiplier', minval=0.1, maxval=2.0, step=0.1, group=group_execution, tooltip='🎯 WHAT IT IS: The distance, in ATR multiples, that the active trailing stop will follow behind the price.\n\n⚡ HOW IT WORKS: This determines how \'tight\' or \'loose\' the trail is. A smaller value keeps the stop closer to the price, locking in profits more aggressively.\n\n📈 HIGHER (1.5-2.0): A looser trail. Less likely to be stopped out on minor pullbacks, but gives back more profit when the trend finally reverses.\n📉 LOWER (0.1-0.5): A tighter trail. Protects profits more aggressively, but is more likely to be stopped out on small, normal pullbacks within a trend.\n\n💡 PRO TIP: A value between 0.5 and 1.0 is often effective for capturing the core of a momentum move without giving too much back.'),
    max_bars_in_trade=input.int(18, '⏰ Maximum Bars in Trade', group=group_execution, minval=1, maxval=100, tooltip='🎯 WHAT IT IS: A safety net that automatically closes any open trade after this many bars have passed since entry.\n\n⚡ HOW IT WORKS: This is a time-based stop. Its purpose is to ensure the strategy does not get stuck in a stagnant, unprofitable trade that is going nowhere.\n\n📈 HIGHER: Allows trades more time to develop. Suitable for longer-term strategies or higher chart timeframes.\n📉 LOWER: Forces a faster turnover of trades. Suitable for short-term, scalping, or day trading strategies.\n\n💡 PRO TIP: The ideal value depends heavily on your chart\'s timeframe. For a 45-minute chart, 18 bars represents over half a trading day, which is a reasonable limit for a momentum-based system.'),
    session_start=input.int(8, 'Session Start Hour', minval=0, maxval=23, group=group_session, tooltip='The hour (in the exchange\'s 24-hour format) when the strategy is allowed to start looking for trades.'),
    session_end=input.int(16, 'Session End Hour', minval=0, maxval=23, group=group_session, tooltip='The hour (in the exchange\'s 24-hour format) when the strategy stops looking for new trades. It will not close existing trades outside this time, only refrain from opening new ones.'),
    allow_weekend=input.bool(False, 'Allow Weekend Trading', group=group_session, tooltip='If checked, allows the strategy to open new trades on Saturdays and Sundays. This is primarily for 24/7 markets like cryptocurrencies.'),
    force_trading_session_active=input.bool(True, 'Force Trading Session Active', group=group_session, tooltip='If checked, the strategy will ignore the session start/end times and will trade 24/7. This is useful for backtesting on assets without clear sessions or to see the strategy\'s full, unfiltered performance.'),
    show_regime_background=input.bool(True, 'Show Regime Background', group=group_visuals, tooltip='Toggles the colored background that indicates the current market regime (Green for Expansion, Aqua for Contraction).'),
    show_morphism_flow=input.bool(True, '🌊 Circle Flow Lines', group=group_visuals, tooltip='Toggles the main flowing lines and particles that visualize the energy and direction of the DEVMA lines.'),
    show_homotopy_paths=input.bool(True, '📐 Homotopy Paths', group=group_visuals, tooltip='Toggles the layered transparent boxes that represent the structural space between the Fast and Slow DEVMA lines.'),
    show_consciousness_field=input.bool(True, '🧠 Consciousness Field', group=group_visuals, tooltip='Toggles the gridded, purple field that visualizes the signal\'s strength and historical presence.'),
    show_functorial_levels=input.bool(True, '📏 Functorial Levels', group=group_visuals, tooltip='Toggles the horizontal lines extending to the right, marking the current values of the Fast and Slow DEVMA lines.'),
    showOrderFlowClouds=input.bool(True, '🌊 Flow Boxes', group=group_visuals, tooltip='Toggles the smaller, compact boxes that visualize recent order flow intensity.'),
    cloudIntensity=input.float(0.7, '📦 Box Intensity', minval=0.1, maxval=2.0, step=0.1, group=group_visuals, tooltip='Controls the vertical size of the \'Flow Boxes\'. Higher values create larger, more prominent boxes.'),
    show_dashboard=input.bool(True, 'Show Dashboard', group=group_dashboard, tooltip='Toggles the main information panel on or off.'),
    dashboard_position=input.string('Top Right', 'Dashboard Position', options=('Top Right', 'Middle Right', 'Bottom Right'), group=group_dashboard, tooltip='Sets the on-chart position for the information dashboard.'),
    dashboard_size=input.string('Normal', 'Dashboard Size', options=('Tiny', 'Small', 'Normal'), group=group_dashboard, tooltip='Adjusts the size and amount of information displayed on the dashboard.')
):
    color_bullish: Color = color.new('#00FF88')
    color_bearish: Color = color.new('#FF6B6B')
    color_neutral: Color = color.new('#8BE9FD')
    color_warning: Color = color.new('#FFB86C')
    color_info: Color = color.new('#BD93F9')
    color_success: Color = color.new('#50FA7B')
    text_bright: Color = color.new('#F8F8F2')
    trade_performance: Persistent[list[float]] = array.new_float(30)
    trade_outcomes: Persistent[list[float]] = array.new_float(50)
    trade_durations: Persistent[list[int]] = array.new_int(20)
    total_trades: Persistent[int] = 0
    win_rate: Persistent[float] = 0.5
    avg_winning_duration: Persistent[int] = 20
    adaptive_time_exit_mult: Persistent[float] = 1.0
    adaptive_stop_mult: Persistent[float] = 1.0
    adaptive_profit_mult: Persistent[float] = 1.0
    atr_value = ta.atr(14)
    bar_hour = hour(time)
    bar_dow = dayofweek(time)
    in_session_hours = bar_hour >= session_start and bar_hour < session_end if session_start < session_end else bar_hour >= session_start or bar_hour < session_end
    not_weekend_day = allow_weekend or (bar_dow != dayofweek.saturday and bar_dow != dayofweek.sunday)
    is_trade_session_active = in_session_hours and not_weekend_day
    actual_trade_allowed = force_trading_session_active or is_trade_session_active
    def f_vovix_source():
        return (ta.atr(fastVoVixLen) - ta.atr(slowVoVixLen)) / (ta.stdev(ta.atr(fastVoVixLen), devLen) + 1e-06)

    src = f_vovix_source()
    dev = ta.stdev(src, devLen)
    fastDEVMA: Series = ta.sma(dev, fastVoVixLen)
    slowDEVMA: Series = ta.sma(dev, slowVoVixLen)
    devma_diff = fastDEVMA - slowDEVMA
    bullCross = ta.crossover(fastDEVMA, slowDEVMA) and devma_diff > 0
    bearCross = ta.crossunder(fastDEVMA, slowDEVMA) and math.abs(devma_diff) > 0
    expansion_regime = fastDEVMA > slowDEVMA
    signal_strength = math.abs(devma_diff) / dev * 100
    signal_quality = 'ELITE' if signal_strength > 5.0 else 'STRONG' if signal_strength > 3.0 else 'GOOD' if signal_strength > 1.0 else 'WEAK'
    can_enter_new_trade = strategy.position_size == 0 and actual_trade_allowed
    adaptive_max_bars = max_bars_in_trade
    if ENABLE_ADAPTIVE and ADAPTIVE_TIME_EXIT:
        if win_rate > 0.85:
            adaptive_max_bars = math.round(max_bars_in_trade * adaptive_time_exit_mult * 1.5)
        elif win_rate > 0.75:
            adaptive_max_bars = math.round(max_bars_in_trade * adaptive_time_exit_mult * 1.25)
        else:
            adaptive_max_bars = math.round(max_bars_in_trade * adaptive_time_exit_mult)
    if strategy.closedtrades > strategy.closedtrades[1] and barstate.isconfirmed:
        last_trade_pnl = strategy.closedtrades.profit(strategy.closedtrades - 1)
        last_trade_return = last_trade_pnl / strategy.initial_capital
        last_trade_bars = strategy.closedtrades.exit_bar_index(strategy.closedtrades - 1) - strategy.closedtrades.entry_bar_index(strategy.closedtrades - 1)
        array.unshift(trade_performance, last_trade_return)
        if array.size(trade_performance) > 30:
            array.pop(trade_performance)
        array.unshift(trade_outcomes, last_trade_return)
        if array.size(trade_outcomes) > 50:
            array.pop(trade_outcomes)
        if last_trade_pnl > 0:
            array.unshift(trade_durations, last_trade_bars)
            if array.size(trade_durations) > 20:
                array.pop(trade_durations)
        total_trades = total_trades + 1
        if array.size(trade_performance) >= 10:
            wins: int = 0
            for i in pine_range(0, array.size(trade_performance) - 1, 1):
                if array.get(trade_performance, i) > 0:
                    wins = wins + 1
            win_rate = wins / array.size(trade_performance)
    if ENABLE_ADAPTIVE and array.size(trade_performance) >= 5 and (total_trades % 3 == 0):
        if array.size(trade_durations) > 5:
            duration_sum: int = 0
            __loop_2__ = pine_loop(0, 1)
            while __loop_2__.step(math.min(array.size(trade_durations) - 1, 9)):
                i = __loop_2__.value
                duration_sum = duration_sum + array.get(trade_durations, i)
            avg_winning_duration = math.round(duration_sum / math.min(array.size(trade_durations), 10))
        if ADAPTIVE_TIME_EXIT and avg_winning_duration > 0:
            adaptive_time_exit_mult = math.max(0.5, math.min(2.0, avg_winning_duration / max_bars_in_trade))
    trade_attempt_status_msg: Persistent[str] = 'Idle'
    if bullCross and can_enter_new_trade and barstate.isconfirmed:
        trade_attempt_status_msg = 'EXPANSION → LONG'
        stop_distance = atr_value * ATR_SL_MULTIPLIER
        profit_distance = atr_value * ATR_TP_MULTIPLIER
        stop_loss = close - stop_distance if USE_SMART_STOPS else na
        take_profit = close + profit_distance
        strategy.entry('ExpansionLong', strategy.long, qty=tradeQty, comment='Expansion→LONG')
        if USE_TRAILING_STOP:
            trail_points = atr_value * TRAIL_POINTS_MULT
            trail_offset = atr_value * TRAIL_OFFSET_MULT
            strategy.exit('ExitExpLong', 'ExpansionLong', stop=stop_loss, limit=take_profit, trail_points=trail_points, trail_offset=trail_offset)
        else:
            strategy.exit('ExitExpLong', 'ExpansionLong', stop=stop_loss, limit=take_profit)
    if bearCross and can_enter_new_trade and barstate.isconfirmed:
        trade_attempt_status_msg = 'CONTRACTION → SHORT'
        stop_distance = atr_value * ATR_SL_MULTIPLIER
        profit_distance = atr_value * ATR_TP_MULTIPLIER
        stop_loss = close + stop_distance if USE_SMART_STOPS else na
        take_profit = close - profit_distance
        strategy.entry('ContractionShort', strategy.short, qty=tradeQty, comment='Contraction→SHORT')
        if USE_TRAILING_STOP:
            trail_points = atr_value * TRAIL_POINTS_MULT
            trail_offset = atr_value * TRAIL_OFFSET_MULT
            strategy.exit('ExitConShort', 'ContractionShort', stop=stop_loss, limit=take_profit, trail_points=trail_points, trail_offset=trail_offset)
        else:
            strategy.exit('ExitConShort', 'ContractionShort', stop=stop_loss, limit=take_profit)
    if strategy.position_size != 0:
        bars_in_trade = bar_index - strategy.opentrades.entry_bar_index(strategy.opentrades - 1)
        if bars_in_trade >= adaptive_max_bars and barstate.isconfirmed:
            strategy.close_all(comment='Time Exit ' + string.tostring(bars_in_trade) + 'b')
            trade_attempt_status_msg = 'Time Exit: ' + string.tostring(bars_in_trade) + 'bars'
    if show_dashboard and barstate.isconfirmed:
        dash_pos = position.top_right if dashboard_position == 'Top Right' else position.middle_right if dashboard_position == 'Middle Right' else position.bottom_right
        cols: int = 4
        rows = 20 if dashboard_size == 'Normal' else 16 if dashboard_size == 'Small' else 12
        dashboard: Persistent[Table] = na(Table)
        last_bar_drawn: Persistent[int] = 0
        should_redraw = na(dashboard) or bar_index - last_bar_drawn > 10 or barstate.isconfirmed
        if should_redraw:
            if not na(dashboard):
                table.delete(dashboard)
            dashboard = table.new(dash_pos, cols, rows, border_width=1, border_color=color.new(color.gray, 50), bgcolor=color.new(color.new('#1E222D'), 20))
            last_bar_drawn = bar_index
        table.clear(dashboard, 0, 0, cols - 1, rows - 1)
        dc_white = color.white
        dc_gray: Color = color.new('#B2B5BE')
        dc_green: Color = color.new('#26A69A')
        dc_red: Color = color.new('#EF5350')
        dc_gold: Color = color.new('#FFD700')
        dc_purple: Color = color.new('#9C27B0')
        dc_aqua: Color = color.new('#00BCD4')
        dc_orange: Color = color.new('#FF8C00')
        bg_header = color.new(color.black, 30)
        bg_section = color.new(color.gray, 85)
        text_size = size.tiny if dashboard_size == 'Tiny' else size.small if dashboard_size == 'Small' else size.tiny
        current_row: int = 0
        table.merge_cells(dashboard, 0, current_row, cols - 1, current_row)
        table.cell(dashboard, 0, current_row, '🌌 VOVIX DEVMA | ' + syminfo.ticker, text_halign=text.align_center, text_color=dc_white, bgcolor=bg_header, text_size=text_size)
        current_row = current_row + 1
        table.merge_cells(dashboard, 0, current_row, cols - 1, current_row)
        table.cell(dashboard, 0, current_row, '═══ 🎯 VOVIX ANALYSIS ═══', text_halign=text.align_center, text_color=dc_gold, bgcolor=bg_section, text_size=text_size)
        current_row = current_row + 1
        table.cell(dashboard, 0, current_row, 'Fast', text_color=dc_gray, text_size=text_size)
        fast_color = dc_green if fastDEVMA > fastDEVMA[1] else dc_red
        table.cell(dashboard, 1, current_row, string.tostring(fastDEVMA, '#.##'), text_halign=text.align_right, text_color=fast_color, text_size=text_size)
        table.cell(dashboard, 2, current_row, 'Slow', text_color=dc_gray, text_size=text_size)
        slow_color = dc_green if slowDEVMA > slowDEVMA[1] else dc_red
        table.cell(dashboard, 3, current_row, string.tostring(slowDEVMA, '#.##'), text_halign=text.align_right, text_color=slow_color, text_size=text_size)
        current_row = current_row + 1
        table.cell(dashboard, 0, current_row, 'Regime', text_color=dc_gray, text_size=text_size)
        regime_status = '🚀 EXPANSION' if expansion_regime else '⚛️ CONTRACTION'
        regime_color = dc_green if expansion_regime else dc_purple
        table.merge_cells(dashboard, 1, current_row, cols - 1, current_row)
        table.cell(dashboard, 1, current_row, regime_status, text_halign=text.align_right, text_color=regime_color, text_size=text_size)
        current_row = current_row + 1
        table.cell(dashboard, 0, current_row, 'Quality', text_color=dc_gray, text_size=text_size)
        qual_color = dc_gold if signal_quality == 'ELITE' else dc_green if signal_quality == 'STRONG' else dc_aqua if signal_quality == 'GOOD' else dc_gray
        table.merge_cells(dashboard, 1, current_row, cols - 1, current_row)
        table.cell(dashboard, 1, current_row, signal_quality, text_halign=text.align_right, text_color=qual_color, text_size=text_size)
        current_row = current_row + 1
        actual_win_rate = strategy.wintrades / strategy.closedtrades if strategy.closedtrades > 0 else 0.0
        table.cell(dashboard, 0, current_row, 'Win Rate', text_color=dc_gray, text_size=text_size)
        wr_color = dc_green if actual_win_rate >= 0.6 else dc_gold if actual_win_rate >= 0.4 else dc_red
        table.cell(dashboard, 1, current_row, string.tostring(actual_win_rate * 100, '#.#') + '%', text_halign=text.align_right, text_color=wr_color, text_size=text_size)
        table.cell(dashboard, 2, current_row, 'Trades', text_color=dc_gray, text_size=text_size)
        table.cell(dashboard, 3, current_row, string.tostring(strategy.closedtrades), text_halign=text.align_right, text_color=dc_white, text_size=text_size)
        current_row = current_row + 1
        table.cell(dashboard, 0, current_row, 'Trade Qty', text_color=dc_gray, text_size=text_size)
        table.merge_cells(dashboard, 1, current_row, 3, current_row)
        table.cell(dashboard, 1, current_row, string.tostring(tradeQty), text_color=dc_orange, text_size=text_size, text_halign=text.align_right)
        current_row = current_row + 1
        table.cell(dashboard, 0, current_row, 'Session', text_color=dc_gray, text_size=text_size)
        session_text_val = 'OPEN' if actual_trade_allowed else 'CLOSED'
        session_color_val = dc_green if actual_trade_allowed else dc_red
        table.merge_cells(dashboard, 1, current_row, 3, current_row)
        table.cell(dashboard, 1, current_row, session_text_val, text_color=session_color_val, text_size=text_size, text_halign=text.align_right)
        current_row = current_row + 1
        table.cell(dashboard, 0, current_row, 'Position', text_color=dc_gray, text_size=text_size)
        pos_text = '🟢 LONG' if strategy.position_size > 0 else '🔴 SHORT' if strategy.position_size < 0 else '⚪ FLAT'
        pos_color = dc_green if strategy.position_size > 0 else dc_red if strategy.position_size < 0 else dc_gray
        table.cell(dashboard, 1, current_row, pos_text, text_halign=text.align_right, text_color=pos_color, text_size=text_size)
        table.cell(dashboard, 2, current_row, 'PnL', text_color=dc_gray, text_size=text_size)
        pnl_color = dc_green if strategy.openprofit > 0 else dc_red if strategy.openprofit < 0 else dc_gray
        table.cell(dashboard, 3, current_row, string.tostring(strategy.openprofit, '#'), text_halign=text.align_right, text_color=pnl_color, text_size=text_size)
        current_row = current_row + 1
        if ENABLE_ADAPTIVE and dashboard_size != 'Tiny':
            table.merge_cells(dashboard, 0, current_row, cols - 1, current_row)
            table.cell(dashboard, 0, current_row, '═══ 🧠 ADAPTIVE STATUS ═══', text_halign=text.align_center, text_color=dc_purple, bgcolor=bg_section, text_size=text_size)
            current_row = current_row + 1
            table.cell(dashboard, 0, current_row, 'Stop Mult', text_color=dc_gray, text_size=text_size)
            stop_color = dc_red if adaptive_stop_mult > 1.0 else dc_green if adaptive_stop_mult < 1.0 else dc_white
            table.cell(dashboard, 1, current_row, string.tostring(adaptive_stop_mult, '#.##'), text_halign=text.align_right, text_color=stop_color, text_size=text_size)
            table.cell(dashboard, 2, current_row, 'Profit Mult', text_color=dc_gray, text_size=text_size)
            profit_color = dc_green if adaptive_profit_mult > 1.0 else dc_red if adaptive_profit_mult < 1.0 else dc_white
            table.cell(dashboard, 3, current_row, string.tostring(adaptive_profit_mult, '#.##'), text_halign=text.align_right, text_color=profit_color, text_size=text_size)
            current_row = current_row + 1
    signal_initial = ta.crossover(fastDEVMA, slowDEVMA)
    signal_terminal = ta.crossunder(fastDEVMA, slowDEVMA)
    signal_product = expansion_regime and signal_strength > 3.0
    signal_coproduct = not expansion_regime and signal_strength > 2.0
    initial_strength = math.min(1.0, signal_strength / 10.0) if signal_initial else 0.0
    terminal_strength = math.min(1.0, signal_strength / 10.0) if signal_terminal else 0.0
    v2_orderFlowScore = (fastDEVMA - slowDEVMA) / (dev + 1e-06)
    composite_morphism_strength = math.min(1.0, math.abs(v2_orderFlowScore))
    consciousness_level = math.min(1.0, signal_strength / 15.0)
    max_homotopy_score = math.min(1.0, math.abs(devma_diff) / dev)
    sma_5 = ta.sma(close, 5)
    sma_13 = ta.sma(close, 13)
    sma_21 = ta.sma(close, 21)
    sma_34 = ta.sma(close, 34)
    sma_55 = ta.sma(close, 55)
    functorial_integrity = win_rate
    signal_transparency_input: int = 30
    visual_transparency: int = 2
    type_recursion_depth: int = 8
    deformation_complexity: int = 13
    cloud_lookback: int = 20
    universe_depth: int = 5
    signal_alpha = 100 - signal_transparency_input
    product_plot = (fastDEVMA + slowDEVMA) / 2 if signal_product else na
    coproduct_plot = (fastDEVMA + slowDEVMA) / 2 if signal_coproduct else na
    plotshape(product_plot, 'Product Signal', shape.circle, location.absolute, color=color.new(color_neutral, signal_alpha), size=size.tiny)
    plotshape(product_plot, 'Product BG', shape.circle, location.absolute, color=color.new(color_neutral, signal_alpha + 10), size=size.small, offset=0)
    plotshape(coproduct_plot, 'Coproduct Signal', shape.circle, location.absolute, color=color.new(color_warning, signal_alpha), size=size.tiny)
    plotshape(coproduct_plot, 'Coproduct BG', shape.circle, location.absolute, color=color.new(color_warning, signal_alpha + 10), size=size.small, offset=0)
    if show_morphism_flow:
        flow_strength = math.max(0.3, composite_morphism_strength)
        flow_color = color_bullish if fastDEVMA > slowDEVMA else color_bearish
        base_transparency = 100 - visual_transparency
        beam_width = math.round(flow_strength * 8) + 2
        __loop_1__ = pine_loop(1, 1)
        while __loop_1__.step(math.min(type_recursion_depth + 2, 8)):
            i = __loop_1__.value
            if bar_index > i:
                alpha = base_transparency + 30 + i * 8
                beam_thickness = math.max(1, beam_width - i)
                y1 = fastDEVMA[i]
                y2 = fastDEVMA
                line.new(bar_index - i, y1, bar_index, y2, color=color.new(flow_color, math.min(70, alpha)), width=beam_thickness, style=line.style_solid)
        if flow_strength > 0.1:
            energy_range = dev * flow_strength * 1.5
            energy_transparency = math.max(10, base_transparency - 15)
            box.new(bar_index - type_recursion_depth, fastDEVMA + energy_range, bar_index, fastDEVMA - energy_range, bgcolor=color.new(flow_color, energy_transparency), border_color=color.new(flow_color, math.max(5, energy_transparency - 5)), border_width=1)
        for i in pine_range(1, type_recursion_depth, 1):
            if bar_index > i and i % 2 == 0:
                particle_size = size.small if flow_strength > 0.7 else size.tiny
                y_pos = (fastDEVMA + fastDEVMA[i]) / 2
                label.new(bar_index - i, y_pos, '●', color=color.new(flow_color, math.min(50, base_transparency)), textcolor=color.new(flow_color, math.min(40, base_transparency - 5)), style=label.style_none, size=particle_size)
    if show_homotopy_paths:
        path_range = dev * math.max(0.3, max_homotopy_score) * 1.2
        base_transparency = 100 - visual_transparency
        for i in pine_range(0, 2, 1):
            box_transparency = base_transparency + i * 2.5
            box_height = path_range * (1 - i * 0.2)
            center_line = (fastDEVMA + slowDEVMA) / 2
            box.new(bar_index - deformation_complexity, center_line + box_height, bar_index, center_line - box_height, bgcolor=color.new(color_info, box_transparency), border_color=color.new(color_info, box_transparency - 5), border_width=1)
    if show_consciousness_field:
        consciousness_range = dev * math.max(0.3, consciousness_level) * 1.2
        consciousness_color = color.purple
        bars_back = cloud_lookback
        base_transparency = 100 - visual_transparency
        if bars_back > 0:
            grid_size = math.max(5, math.floor(cast_int(bars_back / 8)))
            center_line = (fastDEVMA + slowDEVMA) / 2
            for i in pine_range(0, 7, 1):
                start_bar = bar_index - bars_back + i * grid_size
                end_bar = bar_index - bars_back + (i + 1) * grid_size
                if start_bar >= 0 and end_bar <= bar_index:
                    grid_transparency = base_transparency + i * 2
                    box.new(start_bar, center_line + consciousness_range, end_bar, center_line - consciousness_range, bgcolor=color.new(consciousness_color, math.min(95, grid_transparency)), border_color=color.new(consciousness_color, math.min(90, grid_transparency - 5)), border_width=1)
    functorial_lines: Persistent[list[Line]] = array.new_line()
    functorial_labels: Persistent[list[Label]] = array.new_label()
    if show_functorial_levels and barstate.isconfirmed:
        if array.size(functorial_lines) > 0:
            for i in pine_range(array.size(functorial_lines) - 1, 0, 1):
                line.delete(array.get(functorial_lines, i))
            array.clear(functorial_lines)
        if array.size(functorial_labels) > 0:
            for i in pine_range(array.size(functorial_labels) - 1, 0, 1):
                label.delete(array.get(functorial_labels, i))
            array.clear(functorial_labels)
        fast_val = fastDEVMA
        slow_val = slowDEVMA
        dev_val = dev
        levels_to_show = math.min(universe_depth, 3)
        transparency = 100 - signal_transparency_input
        displayed_lines: int = 0
        last_value: Persistent[float] = na(float)
        if displayed_lines < 3:
            level_color = color_success if functorial_integrity > 0.8 else color_warning if functorial_integrity > 0.5 else color_bearish
            glow_line = line.new(bar_index - 2, fast_val, bar_index + 35, fast_val, color=color.new(level_color, transparency + 15), width=2, style=line.style_solid)
            array.push(functorial_lines, glow_line)
            main_line = line.new(bar_index - 2, fast_val, bar_index + 35, fast_val, color=color.new(level_color, transparency), width=1, style=line.style_solid)
            array.push(functorial_lines, main_line)
            level_label_obj = label.new(bar_index + 35, fast_val, 'DEVMA: Fast', color=color.new(level_color, 20), textcolor=text_bright, style=label.style_label_left, size=size.small)
            array.push(functorial_labels, level_label_obj)
            last_value = fast_val
            displayed_lines = displayed_lines + 1
        if displayed_lines < 3 and (na(last_value) or math.abs(slow_val - last_value) > dev * 0.01):
            level_color = color_success if functorial_integrity > 0.8 else color_warning if functorial_integrity > 0.5 else color_bearish
            glow_line = line.new(bar_index - 2, slow_val, bar_index + 35, slow_val, color=color.new(level_color, transparency + 15), width=2, style=line.style_solid)
            array.push(functorial_lines, glow_line)
            main_line = line.new(bar_index - 2, slow_val, bar_index + 35, slow_val, color=color.new(level_color, transparency), width=1, style=line.style_solid)
            array.push(functorial_lines, main_line)
            level_label_obj = label.new(bar_index + 35, slow_val, 'DEVMA: Slow', color=color.new(level_color, 20), textcolor=text_bright, style=label.style_label_left, size=size.small)
            array.push(functorial_labels, level_label_obj)
            displayed_lines = displayed_lines + 1
    if showOrderFlowClouds and math.abs(v2_orderFlowScore) > 0.2 and barstate.isconfirmed:
        box_color = color.green if expansion_regime else color.red
        for i in pine_range(0, 1, 1):
            box_alpha = 85 + i * 5
            box_range = dev * cloudIntensity * (0.3 - i * 0.1)
            x1 = bar_index - 20 + i * 10
            x2 = bar_index - 10 + i * 10
            y_center = (fastDEVMA + slowDEVMA) / 2
            y1 = y_center + box_range
            y2 = y_center - box_range
            if x1 >= 0 and x2 >= 0:
                box.new(x1, y1, x2, y2, bgcolor=color.new(box_color, box_alpha), border_color=color.new(box_color, box_alpha - 5))
    plot(fastDEVMA, 'FastDEVMA', color=color.green if fastDEVMA > fastDEVMA[1] else color.maroon, linewidth=2)
    plot(slowDEVMA, 'SlowDEVMA', color=color.aqua if slowDEVMA > slowDEVMA[1] else color.orange, linewidth=2)
    plot(dev, 'StdDev', color=color.new(color.purple, 60), linewidth=1)
    plotchar(bullCross, 'Long Signal', '▲', location.bottom, color=color.green, size=size.tiny)
    plotchar(bearCross, 'Short Signal', '▼', location.top, color=color.red, size=size.tiny)
    bgcolor((color.new(color.green, 97) if expansion_regime else color.new(color.aqua, 97)) if show_regime_background else na)
    if bullCross:
        alert('🚀 VoVix EXPANSION: ' + signal_quality, alert.freq_once_per_bar)
    if bearCross:
        alert('❄️ VoVix CONTRACTION: ' + signal_quality, alert.freq_once_per_bar)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)