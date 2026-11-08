"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, barmerge, barstate, bgcolor,
    close, color, dayofmonth, extend, high, hour, input, label, line, location, low, math, minute,
    month, na, nz, plot, plotshape, position, request, script, session, shape, size, string,
    syminfo, ta, table, text, ticker, time, timeframe, volume, year
)
from pynecore.types import Color, Label, Line, Persistent, Series, Table

P_MILK: str = 'MILKMAN  ·  SPY/SPX only  ·  3m  ·  scoped historical stats'
P_UNIV: str = 'UNIVERSAL  ·  any market & timeframe  ·  no statistics'
P_CUST: str = 'CUSTOM  ·  my own rules'
day_trading: str = 'Day'
multiday_trading: str = 'Multiday'
swing_trading: str = 'Swing'
position_trading: str = 'Position'
longterm_trading: str = 'Long-term'


@script.indicator("Trinity ATR Levels", shorttitle="Trinity ATR Levels", overlay=True, max_labels_count=500, max_lines_count=200, dynamic_requests=False)
def main(
    preset=input.string(P_MILK, 'Mode', options=(P_MILK, P_UNIV, P_CUST), tooltip='WHAT THE THREE MODES CHANGE\n' + 'The levels are identical in all three. What differs is when a signal may fire, how often it may re-fire, and whether probabilities are shown at all.\n\n' + '──MILKMAN ──\n' + 'The researched configuration, followed as closely as the published studies allow: 3-minute confirmed closes, regular trading hours, one entry per direction per day, no entry buffer, daily levels from the regular session.\n' + 'Probabilities are displayed, because this is the only configuration they were measured in: SPY, regular hours, 3-minute closes, 2000-2025. Put the chart on anything other than SPY or SPX and they hide themselves.\n' + 'Use this if you want the published SPY regular-hours configuration.\n\n' + '──UNIVERSAL ──\n' + 'The same levels and the same trigger / Golden Gate structure, on any market and any timeframe: crypto, FX, futures, single stocks. Signals run around the clock because a 24-hour market has no cash session to gate against, re-entries are unlimited with a longer cooldown, and a 1% ATR entry buffer filters the extra noise of less liquid instruments.\n' + 'Probabilities are hidden entirely. Not because the structure fails elsewhere -- ATR levels are used across every market -- but because nobody has measured the hit rates outside SPY. Showing SPY numbers on BTC would be inventing evidence.\n' + 'Use this anywhere that is not SPY or SPX.\n\n' + '──CUSTOM ──\n' + 'Every setting under "Signal Rules" applies. Nothing is forced. Statistics follow the scope switch in that group.\n' + 'Use this once you know which specific rule you want to change and why.'),
    trading_type_in=input.string(day_trading, 'Level Period', options=(day_trading, multiday_trading, swing_trading, position_trading, longterm_trading), tooltip='Which higher timeframe the levels are built from. Day uses the daily ATR and the previous daily close; the others build the identical structure from weekly, monthly, quarterly or yearly bars.\n\n' + 'FORCED TO DAY in the Milkman mode -- daily levels are what the research measured, and the probabilities mean nothing against a weekly or monthly ATR.\n\n' + 'WORTH KNOWING (Universal and Custom modes): the higher periods turn this into a swing-trading tool rather than a day-trading one. Swing and Position build the triggers and the Golden Gate from monthly and quarterly ranges, which on liquid instruments -- large-cap equities, index ETFs, major FX pairs, the big futures contracts -- gives genuinely useful multi-week structure. Read them as levels to trade around rather than as intraday signals, and use a chart timeframe to match: a 4-hour or daily chart suits monthly levels far better than a 3-minute one.\n\n' + 'Where it works less well: thinly traded small-cap crypto. Those markets can move several ATRs in a session and then sit dead for weeks, so a monthly or quarterly ATR produces levels either far out of reach or already blown through. Stick to the daily period on those, or to the more liquid pairs.', group='② Levels'),
    atr_length=input.int(14, 'ATR Length', minval=1, group='② Levels'),
    trigger_percentage=input.float(0.236, 'Trigger (share of ATR)', step=0.001, minval=0.01, maxval=1.0, tooltip='Where the entry gate sits either side of the previous close, as a fraction of the ATR. 0.236 is the researched value. Every label reads this input, so changing it will not leave stale text behind.', group='② Levels'),
    session_mode_in=input.string('Regular (RTH)', 'PDC / ATR Session', options=('Regular (RTH)', 'Extended'), tooltip='Regular: the previous official cash-session close and the regular-hours ATR. Extended: the previous extended-session print.\nSet by the mode -- Regular for Milkman, Extended for Universal, since 24-hour markets have no cash session.', group='② Levels'),
    use_current_close=input.bool(False, 'Use the Forming Period Close  (Saty "Use Current Close")', tooltip='WHICH CLOSE THE LEVELS ARE BUILT FROM\n' + "Every level is the reference close plus or minus a fraction of ATR. This chooses which close that is. It comes from Saty Mahajan's original ATR Levels and is genuine to the system -- but it is a planning tool, not a trading one.\n\n" + '──OFF (default, and correct for trading) ──\n' + "The PREVIOUS completed period's close and ATR. On a Day period that is yesterday's official close. The levels are fixed before the session starts and do not move all day, which is the entire point: you decide where the trigger and the Golden Gate are before price gets there.\n\n" + '──ON ──\n' + "The FORMING period's close and ATR -- on a Day period, the live price. The levels rebuild on every tick and drift with price.\n\n" + 'WHEN TO TURN IT ON\n' + "In the last minutes of a session, or after hours, the forming close is effectively the final close -- so switching it on previews where tomorrow's levels will sit. Note them down, then switch it back off. That is the only use.\n\n" + 'WHY IT DOES NOT WORK DURING A SESSION\n' + 'If the reference close is the current price, price sits exactly on it by definition, permanently. The trigger boxes are defined as price being between the previous close and a trigger, so they can never be true. The Gate cannot open, the trigger cannot fire, and the whole entry engine goes inert.\n' + "Historically it is worse than inert: each past day's levels get drawn from that same day's close, which is look-ahead. Any pattern you think you see in the history is manufactured by the setting.\n\n" + 'AND THE STATISTICS\n' + 'Every Milkman study assumes levels locked to the prior daily close. With this ON, none of the percentages apply -- leave it OFF in the Milkman mode.', group='② Levels'),
    signal_tf_in=input.string('Strict 3m (Milkman)', 'Signals Fire On', options=('Strict 3m (Milkman)', 'Any chart timeframe'), tooltip='IGNORED unless the mode is Custom.\nStrict 3m: signals only on a 3-minute chart, which is what the research measured.', group='③Signal Rules  (Custom mode only)'),
    signal_session_in=input.string('Regular hours only', 'Signals Active During', options=('Regular hours only', 'Premarket + regular hours', 'Every bar (24h markets)'), tooltip='IGNORED unless the mode is Custom.\nDecided by the session clock, not by whether your chart displays extended hours. Crypto and FX need "Every bar".\nThis setting also decides where the trading day starts for entry counts and the first-hour window.', group='③Signal Rules  (Custom mode only)'),
    max_entries_in=input.int(1, 'Trigger Entries Per Direction Per Session', minval=0, maxval=10, tooltip='IGNORED unless the mode is Custom.\n0 = unlimited. 1 = one long and one short per day, which is how the setup is traded; re-entries after a shakeout come from the T-PB, GG and EMA8 signals instead.', group='③Signal Rules  (Custom mode only)'),
    cooldown_in=input.int(3, 'Re-arm Cooldown After an Exit (bars)', minval=0, maxval=50, tooltip='IGNORED unless the mode is Custom.\nConfirmed bars that must pass after an exit before the trigger can fire again. This is what stops ENTER/EXIT flickering when price straddles the level.', group='③Signal Rules  (Custom mode only)'),
    buffer_in=input.float(0.0, 'Entry Buffer Beyond Trigger (% of ATR)', minval=0.0, maxval=10.0, step=0.5, tooltip='IGNORED unless the mode is Custom.\n0 = the pure Milkman rule: a bare confirmed close through the level.\nAbove 0 the ENTRY must clear the trigger by that margin, but the EXIT still uses the trigger itself -- a buffer should filter which signals you take, not move your stop. That deliberately leaves a band where you are in the trade and not yet stopped; the dashboard shows both prices whenever a buffer is set.', group='③Signal Rules  (Custom mode only)'),
    debounce_in=input.bool(True, 'Debounce Pullback Entries to First Touch', tooltip='IGNORED unless the mode is Custom.\nOn: a pullback signal fires once when price first tags the level, not on every bar it lingers there.', group='③Signal Rules  (Custom mode only)'),
    gapsafe_in=input.bool(True, 'Gap-Safe Cross Detection', tooltip='IGNORED unless the mode is Custom.\nOn: the opening cross is measured against the previous session close, so an overnight gap through the trigger still produces an entry on an extended-hours chart.', group='③Signal Rules  (Custom mode only)'),
    enforce_scope_in=input.bool(True, 'Hide Statistics Outside SPY/SPX · 3m · Day · RTH', tooltip='IGNORED unless the mode is Custom.\nThe percentages were measured on SPY alone. Turning this off shows them everywhere, where they will be wrong.', group='③Signal Rules  (Custom mode only)'),
    simple_mode=input.bool(False, 'Simple Mode (essential levels only)', tooltip='Leaves PDC, both triggers, 38.2% and 61.8% -- the levels the system actually trades. Hides 50%, 78.6%, the extensions, previous period high/low and premarket high/low. Recommended for anyone new to ATR levels.', group='④ Display'),
    palette=input.string('Default (gold / green / red)', 'Colour Palette', options=('Default (gold / green / red)', 'Colour-blind safe (Okabe-Ito)'), tooltip='The default gold and green are hard to separate with deuteranopia or protanopia. The Okabe-Ito set stays distinguishable across the common forms of colour vision deficiency and in greyscale. It overrides the custom level colours while active.', group='④ Display'),
    dashboard_detail=input.string('Full', 'Dashboard', options=('Full', 'Compact', 'Off'), tooltip='Full: every row -- location, watch, entry, targets, stop, stall guidance, Bilbo, context, timing, distance and status.\nCompact: the six lines you actually act on -- where price is, what to do, targets, stop, Bilbo and status -- with the wording trimmed so the panel stays narrow.\nOff: no dashboard. The levels, markers and labels are unaffected.\n\nAbove a 1-hour chart both layouts drop automatically to a swing view -- location, targets, stop and distance. The intraday rows are removed rather than left saying they are inactive, because the 3-minute entry rules and the 1-hour Bilbo filter genuinely cannot be evaluated there.', group='④ Display'),
    milkman_table_position=input.string('Top Right', 'Dashboard Position', options=('Top Left', 'Top Right', 'Bottom Left', 'Bottom Right'), group='④ Display'),
    milkman_table_size=input.string('Small', 'Dashboard Text Size', options=('Small', 'Normal', 'Large'), group='④ Display'),
    show_mode_row=input.bool(True, 'Dashboard: Mode Row (Full only)', group='④ Display'),
    show_distance_row=input.bool(True, 'Dashboard: Distance-to-Level Row (Full only)', tooltip='How far price sits from the trigger, 38.2% and 61.8% in price and in % of ATR, plus how far an open trade has travelled through the Golden Gate.', group='④ Display'),
    show_status_row=input.bool(True, 'Dashboard: Status Row', tooltip='One line that always answers "why is nothing happening" -- signals switched off, entry blocked by cooldown or budget, timeframe degradation, or simply waiting and how far away the level is.', group='④ Display'),
    show_legend=input.bool(False, 'Show Legend / Cheat Sheet', tooltip='A second panel explaining every level, marker and term. Switch it on when handing the chart to someone new.', group='④ Display'),
    legend_position=input.string('Bottom Left', 'Legend Position', options=('Top Left', 'Top Right', 'Bottom Left', 'Bottom Right'), group='④ Display'),
    show_info=input.bool(True, 'Show Range/ATR Info Table', group='④ Display'),
    table_position=input.string('Bottom Right', 'Info Table Position', options=('Top Right', 'Bottom Left', 'Bottom Right'), group='④ Display'),
    table_size=input.string('Small', 'Info Table Size', options=('Small', 'Normal', 'Large'), group='④ Display'),
    use_options_labels=input.bool(True, 'Use Calls/Puts Instead of Long/Short', group='④ Display'),
    show_trigger_markers=input.bool(True, 'ENTER  -- confirmed close through the trigger', group='⑤ Chart Markers'),
    show_exit_markers=input.bool(True, 'EXIT   -- confirmed close back through it', group='⑤ Chart Markers'),
    show_gg_markers=input.bool(True, 'GG     -- Golden Gate opens at 38.2%', group='⑤ Chart Markers'),
    show_tpb_markers=input.bool(True, 'T-PB   -- pullback to the trigger (highest EV in SPY sample)', group='⑤ Chart Markers'),
    show_ema8_markers=input.bool(False, 'EMA8   -- pullback to the 10-minute EMA8', tooltip='The third-best entry by expected value, behind the trigger pullback and an immediate entry at 38.2%. Off by default because it is the busiest signal on the chart. Automatically suppressed above a 10-minute chart, where the 10m EMA cannot be read reliably.', group='⑤ Chart Markers'),
    show_pdc_reclaim=input.bool(True, 'PDC    -- first-hour reclaim of the previous close', tooltip='Measured on 10-minute closes inside the first hour of the session. Automatically suppressed above a 10-minute chart.', group='⑤ Chart Markers'),
    show_gg_barcolor=input.bool(True, 'Colour the Golden Gate candle', group='⑤ Chart Markers'),
    gg_barcolor_mode=input.string('Entry bar only', 'Which Bars to Colour', options=('Entry bar only', 'Every bar inside the Gate'), group='⑤ Chart Markers'),
    gg_bull_bar_in=input.color(color.rgb(255, 200, 40), 'Bull Gate Candle', group='⑤ Chart Markers'),
    gg_bear_bar_in=input.color(color.rgb(255, 160, 30), 'Bear Gate Candle', group='⑤ Chart Markers'),
    show_mid_ext_in=input.bool(True, 'Show 50% and 78.6%', tooltip='The Golden Gate boundaries (38.2% and 61.8%), both triggers and the previous close always draw -- the system cannot be read without them. This controls only the two secondary levels.', group='⑥ Levels: Colours & Visibility'),
    show_ext_in=input.bool(False, 'Show Extensions Beyond ±1 ATR', group='⑥ Levels: Colours & Visibility'),
    level_size=input.int(2, 'Level Line Thickness', minval=1, maxval=5, group='⑥ Levels: Colours & Visibility'),
    pdc_color_in=input.color(color.white, 'Previous Close', group='⑥ Levels: Colours & Visibility'),
    trig_dn_in=input.color(color.rgb(247, 15, 15), 'Put Trigger', group='⑥ Levels: Colours & Visibility'),
    trig_up_in=input.color(color.rgb(63, 231, 21), 'Call Trigger', group='⑥ Levels: Colours & Visibility'),
    c382_in=input.color(color.rgb(255, 200, 50), '38.2%  (Gate opens)', group='⑥ Levels: Colours & Visibility'),
    c500_in=input.color(color.rgb(220, 100, 30), '50.0%  (negative EV midpoint)', group='⑥ Levels: Colours & Visibility'),
    c618_in=input.color(color.rgb(255, 215, 0), '61.8%  (Gate target)', group='⑥ Levels: Colours & Visibility'),
    c786_in=input.color(color.rgb(255, 140, 0), '78.6%  (extension)', group='⑥ Levels: Colours & Visibility'),
    catr_in=input.color(color.white, '±1 ATR  (full range)', group='⑥ Levels: Colours & Visibility'),
    cext_in=input.color(color.new(color.orange, 0), 'Extensions', group='⑥ Levels: Colours & Visibility'),
    show_pdh_pdl_in=input.bool(True, 'Show Previous Period High / Low', group='⑦ Session Levels'),
    show_pmh_pml_in=input.bool(True, 'Show Premarket High / Low', group='⑦ Session Levels'),
    show_session_labels=input.bool(True, 'Show Their Labels', group='⑦ Session Levels'),
    pdh_color=input.color(color.rgb(0, 200, 220), 'Previous High', group='⑦ Session Levels'),
    pdl_color=input.color(color.rgb(220, 80, 200), 'Previous Low', group='⑦ Session Levels'),
    pmh_color=input.color(color.rgb(70, 130, 255), 'Premarket High', group='⑦ Session Levels'),
    pml_color=input.color(color.rgb(170, 90, 255), 'Premarket Low', group='⑦ Session Levels'),
    session_level_size=input.int(1, 'Line Thickness', minval=1, maxval=5, group='⑦ Session Levels'),
    premarket_session=input.session('0400-0930', 'Premarket Window', tooltip='US equity default 04:00-09:30 exchange time. Needs Extended Hours enabled on the chart or these stay blank.', group='⑦ Session Levels'),
    rth_session=input.session('0930-1600', 'Regular Session Window', tooltip='Defines regular hours for the signal gate, the premarket lock, and the trading-day boundary when signals are session-gated.', group='⑦ Session Levels'),
    show_ema8_10m=input.bool(True, 'Show 10-minute EMA8', tooltip='Pulled from the 10-minute timeframe, so it draws the same line on a 1m, 3m or hourly chart. This is the EMA the entry study measured -- your chart\'s own 8 EMA is a different line.\nAbove a 10-minute chart it can only be approximated, and the Status row will say so.', group='⑧ 10-minute EMA8'),
    ema8_10m_mode=input.string('Confirmed (matches signals)', 'Source', options=('Confirmed (matches signals)', 'Live (tracks price, repaints)'), tooltip='Confirmed: the last COMPLETED 10-minute EMA8, exactly what the pullback signals test against. It draws as a staircase, stepping every 10 minutes -- that is the true shape, not a rendering fault.\nLive: the forming value. Smoother, but it moves within the bar.', group='⑧ 10-minute EMA8'),
    ema8_10m_color=input.color(color.rgb(120, 200, 255), 'Colour', group='⑧ 10-minute EMA8'),
    ema8_10m_width=input.int(2, 'Thickness', minval=1, maxval=5, group='⑧ 10-minute EMA8'),
    show_ema8_10m_label=input.bool(True, 'Show Price Label', group='⑧ 10-minute EMA8'),
    label_mode=input.string('Summary', 'Level Label Detail', options=('Detailed', 'Summary', 'Off'), group='⑨ Labels & Shading'),
    label_bg_color=input.color(color.new(color.rgb(15, 15, 25), 80), 'Label Background', group='⑨ Labels & Shading'),
    label_text_color=input.color(color.white, 'Label Text', group='⑨ Labels & Shading'),
    label_size_choice=input.string('Small', 'Level Label Size', options=('Tiny', 'Small', 'Normal'), group='⑨ Labels & Shading'),
    session_label_size_choice=input.string('Small', 'Price Tag Size', options=('Tiny', 'Small', 'Normal'), group='⑨ Labels & Shading'),
    show_fib_labels=input.bool(True, 'Show Price Tags on Levels', group='⑨ Labels & Shading'),
    show_target_stop=input.bool(True, 'Show TARGET & STOP Tags', group='⑨ Labels & Shading'),
    tp_label_size=input.string('Tiny', 'TARGET & STOP Size', options=('Tiny', 'Small', 'Normal', 'Large', 'Huge'), group='⑨ Labels & Shading'),
    label_right_offset=input.int(6, 'Label Offset (bars right of price)', minval=0, maxval=80, group='⑨ Labels & Shading'),
    show_trigger_box=input.bool(False, 'Shade the Trigger Box', group='⑨ Labels & Shading'),
    show_golden_gate_box=input.bool(False, 'Shade the Golden Gate', group='⑨ Labels & Shading'),
    trigger_box_color=input.color(color.new(color.yellow, 88), 'Trigger Box Shade', group='⑨ Labels & Shading'),
    gg_bull_shade=input.color(color.new(color.green, 65), 'Gate Shade (bull)', group='⑨ Labels & Shading'),
    gg_bear_shade=input.color(color.new(color.red, 65), 'Gate Shade (bear)', group='⑨ Labels & Shading'),
    fast_ema=input.int(8, 'Fast EMA (info table trend colour only)', minval=1, group='⑩ Trend & Runner'),
    pivot_ema=input.int(21, 'Pivot EMA', minval=1, group='⑩ Trend & Runner'),
    slow_ema=input.int(34, 'Slow EMA', minval=1, group='⑩ Trend & Runner'),
    take_profit_choice=input.string('1.0 ATR (Classic)', 'Runner Target', options=('1.0 ATR (Classic)', '1.236 ATR', '1.618 ATR (Golden Ratio)', '2.0 ATR', '2.618 ATR', '3.0 ATR'), tooltip='A discretionary runner target, entirely separate from the researched Golden Gate target at 61.8%.', group='⑩ Trend & Runner'),
    alert_long=input.bool(True, 'Enable Long Trigger Alert', group='⑪ Alerts'),
    alert_short=input.bool(True, 'Enable Short Trigger Alert', tooltip='Alert wording is deliberately mechanics-only. TradingView fixes alert text when the script compiles, so it cannot know which mode or symbol you are on -- quoting SPY percentages there would be wrong everywhere except SPY. The probabilities are in the dashboard, which does know the scope.', group='⑪ Alerts')
):
    p_milk = preset == P_MILK
    p_univ = preset == P_UNIV
    p_cust = preset == P_CUST

    trading_type = day_trading if p_milk else trading_type_in
    session_mode = session_mode_in if p_cust else 'Regular (RTH)' if p_milk else 'Extended'

    signal_tf_mode = signal_tf_in if p_cust else 'Strict 3m (Milkman)' if p_milk else 'Any chart timeframe'
    signal_session = signal_session_in if p_cust else 'Regular hours only' if p_milk else 'Every bar (24h markets)'
    max_entries = max_entries_in if p_cust else 1 if p_milk else 0
    cooldown_bars = cooldown_in if p_cust else 3 if p_milk else 5
    buffer_pct = buffer_in if p_cust else 0.0 if p_milk else 1.0
    pb_debounce = debounce_in if p_cust else True
    gap_safe_cross = gapsafe_in if p_cust else True
    enforce_scope = enforce_scope_in if p_cust else True
    show_milkman_table = dashboard_detail != 'Off'
    compact_mode = dashboard_detail == 'Compact'
    tp_multiplier = 1.0 if take_profit_choice == '1.0 ATR (Classic)' else 1.236 if take_profit_choice == '1.236 ATR' else 1.618 if take_profit_choice == '1.618 ATR (Golden Ratio)' else 2.0 if take_profit_choice == '2.0 ATR' else 2.618 if take_profit_choice == '2.618 ATR' else 3.0

    eff_show_mid_ext = False if simple_mode else show_mid_ext_in
    eff_show_ext = False if simple_mode else show_ext_in
    eff_show_pdh_pdl = False if simple_mode else show_pdh_pdl_in
    eff_show_pmh_pml = False if simple_mode else show_pmh_pml_in

    cb = palette == 'Colour-blind safe (Okabe-Ito)'
    c_up = color.rgb(0, 114, 178) if cb else trig_up_in
    c_dn = color.rgb(213, 94, 0) if cb else trig_dn_in
    e_382 = color.rgb(86, 180, 233) if cb else c382_in
    e_500 = color.rgb(140, 140, 140) if cb else c500_in
    e_618 = color.rgb(0, 158, 115) if cb else c618_in
    e_786 = color.rgb(240, 228, 66) if cb else c786_in
    e_atr1 = color.rgb(230, 230, 230) if cb else catr_in
    e_ext = color.rgb(204, 121, 167) if cb else cext_in
    e_pdc = color.rgb(255, 255, 255) if cb else pdc_color_in
    e_gg_bull = color.rgb(86, 180, 233) if cb else gg_bull_bar_in
    e_gg_bear = color.rgb(230, 159, 0) if cb else gg_bear_bar_in

    def f_lbl_size(choice: str):
        return size.tiny if choice == 'Tiny' else size.normal if choice == 'Normal' else size.large if choice == 'Large' else size.huge if choice == 'Huge' else size.small

    lbl_sz = f_lbl_size(label_size_choice)
    sess_lbl_sz = f_lbl_size(session_label_size_choice)
    tp_label_size_val = f_lbl_size(tp_label_size)

    STAT_VERSION: str = 'Milkman stats v2026-08-29 (SPY RTH 2000-2025)'

    S_days_open_in_box: float = 49.4
    S_box_held_1h_bull: float = 75.3
    S_box_held_1h_bear: float = 71.6

    S_call_conf_382: float = 73.6
    S_call_invalidated: float = 59.5
    S_median_mins_382: int = 18

    S_trig_382_bull: float = 78.5
    S_trig_382_bear: float = 79.0
    S_l382_618_bull: float = 62.7
    S_l382_618_bear: float = 65.5
    S_l618_786_bull: float = 68.9
    S_l618_786_bear: float = 74.7
    S_l786_atr_bull: float = 60.9
    S_l786_atr_bear: float = 66.9
    S_day_atr_bull: float = 13.8
    S_day_atr_bear: float = 16.1

    S_gg_base_bull: float = 62.5
    S_gg_base_bear: float = 65.4

    S_bilbo_hr: float = 71.0
    S_bilbo_hf: float = 73.8
    S_bilbo_lf: float = 85.1
    S_bilbo_lr: float = 86.6

    S_bilbo_786_bull: float = 56.0
    S_bilbo_atr_bull: float = 34.7
    S_bilbo_786_bear: float = 75.9
    S_bilbo_atr_bear: float = 63.8
    S_base_786_bull: float = 43.2
    S_base_786_bear: float = 48.7

    S_entry_imm_bull: float = 61.3
    S_entry_imm_bear: float = 64.3
    S_ev_imm_bull: float = 8.9
    S_ev_imm_bear: float = 9.8
    S_entry_ema8_bull: float = 59.2
    S_entry_ema8_bear: float = 59.8
    S_ev_ema8_bull: float = 6.1
    S_ev_ema8_bear: float = 7.7
    S_ev_mid50_bull = -4.8
    S_ev_mid50_bear = -4.0
    S_ev_trigpb_bull: float = 12.4
    S_ev_trigpb_bear: float = 14.0

    S_trig_holds_bull: float = 84.0
    S_trig_holds_bear: float = 88.6

    S_pdc_reclaim_trig: float = 73.0
    S_pdc_reclaim_gg: float = 49.0

    S_open_gap_bull: float = 86.0
    S_open_gap_bear: float = 88.0

    def ladder_bull(h: int):
        return 63.0 if h <= 9 else 57.0 if h == 10 else 55.0 if h == 11 else 48.0 if h == 12 else 39.0 if h == 13 else 41.0 if h == 14 else 16.0

    def ladder_bear(h: int):
        return 64.0 if h <= 9 else 60.0 if h == 10 else 56.0 if h == 11 else 56.0 if h == 12 else 56.0 if h == 13 else 48.0 if h == 14 else 30.0

    def pct(v: float):
        return string.tostring(v, '#.#') + '%'

    def ev(v: float):
        return ('+' if v >= 0 else '') + string.tostring(v, '#.#') + ' ATR%'

    trig_pct_txt = string.tostring(trigger_percentage * 100, '#.#') + '% ATR'

    def timeframe_func():
        return 'D' if trading_type == day_trading else 'W' if trading_type == multiday_trading else 'M' if trading_type == swing_trading else '3M' if trading_type == position_trading else '12M' if trading_type == longterm_trading else 'D'

    price = close
    fast_ema_value = ta.ema(price, fast_ema)
    pivot_ema_value = ta.ema(price, pivot_ema)
    slow_ema_value = ta.ema(price, slow_ema)
    bullish = price >= fast_ema_value and fast_ema_value >= pivot_ema_value and (pivot_ema_value >= slow_ema_value)
    bearish = price <= fast_ema_value and fast_ema_value <= pivot_ema_value and (pivot_ema_value <= slow_ema_value)

    htf_ticker = ticker.new(syminfo.prefix, syminfo.ticker, session=session.regular if session_mode == 'Regular (RTH)' else session.extended)
    period_index = 0 if use_current_close else 1

    htf_ref_close, htf_ref_atr, htf_cur_high, htf_cur_low, htf_prev_high, htf_prev_low = request.security(htf_ticker, timeframe_func(), (close[period_index], inline_series(ta.atr(atr_length), period_index), high, low, high[1], low[1]), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)

    previous_close: Series = htf_ref_close
    atr: Series = htf_ref_atr
    period_high = htf_cur_high
    period_low = htf_cur_low
    pdh = htf_prev_high
    pdl = htf_prev_low

    atr_safe = atr if atr > 0 else na
    range_1 = period_high - period_low
    tr_percent_of_atr = range_1 / atr * 100 if atr > 0 else 0.0

    lower_trigger = previous_close - trigger_percentage * atr
    upper_trigger = previous_close + trigger_percentage * atr

    lower_0382 = previous_close - atr * 0.382
    upper_0382 = previous_close + atr * 0.382
    lower_0500 = previous_close - atr * 0.5
    upper_0500 = previous_close + atr * 0.5
    lower_0618 = previous_close - atr * 0.618
    upper_0618 = previous_close + atr * 0.618
    lower_0786 = previous_close - atr * 0.786
    upper_0786 = previous_close + atr * 0.786
    lower_1000 = previous_close - atr
    upper_1000 = previous_close + atr
    lower_1236 = lower_1000 - atr * 0.236
    upper_1236 = upper_1000 + atr * 0.236
    lower_1618 = lower_1000 - atr * 0.618
    upper_1618 = upper_1000 + atr * 0.618
    lower_2000 = lower_1000 - atr
    upper_2000 = upper_1000 + atr
    lower_2236 = lower_2000 - atr * 0.236
    upper_2236 = upper_2000 + atr * 0.236
    lower_2618 = lower_2000 - atr * 0.618
    upper_2618 = upper_2000 + atr * 0.618

    in_premarket: Series = not na(time(timeframe.period, premarket_session))
    in_rth: Series = not na(time(timeframe.period, rth_session))

    day_key: Series = year * 10000 + month * 100 + dayofmonth
    new_rth = in_rth and (not in_rth[1] or day_key != day_key[1])
    new_pm = in_premarket and (not in_premarket[1])

    hour_et = hour(time, 'America/New_York')
    minute_et = minute(time, 'America/New_York')
    time_decimal = hour_et + minute_et / 60.0

    sess_start_bar: Persistent[int] = 0
    if new_rth:
        sess_start_bar = bar_index

    pm_high_live: Persistent[float] = na(float)
    pm_low_live: Persistent[float] = na(float)
    pm_high_lock: Persistent[float] = na(float)
    pm_low_lock: Persistent[float] = na(float)

    if new_pm:
        pm_high_live = high
        pm_low_live = low
    elif in_premarket:
        pm_high_live = math.max(nz(pm_high_live, high), high)
        pm_low_live = math.min(nz(pm_low_live, low), low)

    if new_rth:
        pm_high_lock = pm_high_live
        pm_low_lock = pm_low_live

    pm_high = pm_high_live if in_premarket else pm_high_lock
    pm_low = pm_low_live if in_premarket else pm_low_lock

    is_3m = timeframe.isminutes and timeframe.multiplier == 3
    tf_ok_for_signals = is_3m if signal_tf_mode == 'Strict 3m (Milkman)' else True
    session_ok_for_signals = True if signal_session == 'Every bar (24h markets)' else in_rth or in_premarket if signal_session == 'Premarket + regular hours' else in_rth
    signal_close = tf_ok_for_signals and session_ok_for_signals and barstate.isconfirmed

    new_session = day_key != day_key[1] if signal_session == 'Every bar (24h markets)' else new_rth

    session_start_ms: Persistent[int] = na(int)
    if new_session:
        session_start_ms = time
    first_hour = not na(session_start_ms) and time - session_start_ms <= 3600000

    chart_mins = timeframe.multiplier / 60.0 if timeframe.isseconds else timeframe.multiplier if timeframe.isminutes else 1440.0 if timeframe.isdaily else 10080.0 if timeframe.isweekly else 43200.0 if timeframe.ismonthly else 0.0

    htf_10m_ok = chart_mins > 0 and chart_mins <= 10
    htf_1h_ok = chart_mins > 0 and chart_mins <= 60

    sym_ok = syminfo.ticker == 'SPY' or syminfo.ticker == 'SPX'
    mode_ok = trading_type == day_trading
    sess_ok = session_mode == 'Regular (RTH)'
    in_scope = sym_ok and is_3m and mode_ok and sess_ok

    stats_valid = False if p_univ else in_scope if p_milk else not enforce_scope or in_scope

    def st(s: str):
        return s if stats_valid else ''

    mode_short = 'MILKMAN' if p_milk else 'UNIVERSAL' if p_univ else 'CUSTOM'
    mode_line = 'MILKMAN  ·  SPY/SPX · 3m · RTH\n1 entry per direction per day · no buffer\nstats ' + ('ON' if stats_valid else 'HIDDEN -- chart is out of scope') if p_milk else 'UNIVERSAL  ·  any market & timeframe\n24h signals · 1% ATR buffer · unlimited re-entries\nstats OFF by design' if p_univ else 'CUSTOM  ·  ' + ('any timeframe' if tf_ok_for_signals else '3m only') + ' · ' + signal_session + '\n' + ('unlimited' if max_entries == 0 else string.tostring(max_entries)) + ' entries · ' + string.tostring(buffer_pct, '#.#') + '% buffer\nstats ' + ('ON' if stats_valid else 'HIDDEN')

    scope_reason = ('' if sym_ok else ' symbol') + ('' if is_3m else ' 3m') + ('' if mode_ok else ' Day-period') + ('' if sess_ok else ' RTH-session')
    scope_tag = '' if p_univ else '' if stats_valid else '  |  stats hidden -- off:' + scope_reason

    po_1h = request.security(syminfo.tickerid, '60', inline_series(ta.ema((close - ta.ema(close, 21)) / (3.0 * ta.atr(14)) * 100, 3), 1), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    po_1h_prev = request.security(syminfo.tickerid, '60', inline_series(ta.ema((close - ta.ema(close, 21)) / (3.0 * ta.atr(14)) * 100, 3), 2), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)

    c10_1 = request.security(syminfo.tickerid, '10', close[1], gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    c10_2 = request.security(syminfo.tickerid, '10', close[2], gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    new_10m = ta.change(time('10')) != 0

    ema8_10m = request.security(syminfo.tickerid, '10', inline_series(ta.ema(close, 8), 1), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_on)
    ema8_10m_live = request.security(syminfo.tickerid, '10', ta.ema(close, 8), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)
    ema8_10m_plot = ema8_10m_live if ema8_10m_mode == 'Live (tracks price, repaints)' else ema8_10m

    po_extended_up = po_1h > 100
    po_distribution = po_1h > 61.8 and po_1h <= 100
    po_neutral_up = po_1h > 23.6 and po_1h <= 61.8
    po_neutral_zone = po_1h >= -23.6 and po_1h <= 23.6
    po_neutral_down = po_1h >= -61.8 and po_1h < -23.6
    po_accumulation = po_1h >= -100 and po_1h < -61.8
    po_extended_down = po_1h < -100

    po_1h_rising = po_1h > po_1h_prev
    po_1h_falling = po_1h < po_1h_prev

    bull_bilbo_active = po_distribution
    bear_bilbo_active = po_accumulation

    po_zone_name = 'EXTENDED UP' if po_extended_up else 'DISTRIBUTION' if po_distribution else 'NEUTRAL UP' if po_neutral_up else 'NEUTRAL' if po_neutral_zone else 'NEUTRAL DOWN' if po_neutral_down else 'ACCUMULATION' if po_accumulation else 'EXTENDED DOWN' if po_extended_down else 'UNKNOWN'

    bilbo_color = color.new(color.rgb(255, 215, 0), 15) if bull_bilbo_active else color.new(color.orange, 15) if bear_bilbo_active else color.new(color.green, 55) if po_neutral_up else color.new(color.red, 55) if po_neutral_down else color.new(color.gray, 50)

    in_bull_trigger_box = close > previous_close and close < upper_trigger
    in_bear_trigger_box = close < previous_close and close > lower_trigger
    in_trigger_box = in_bull_trigger_box or in_bear_trigger_box

    long_active: Persistent[bool] = False
    short_active: Persistent[bool] = False
    trigger_hour: Persistent[int] = na(int)
    bars_since_trigger: Persistent[int] = 0
    bull_reached_382: Persistent[bool] = False
    bear_reached_382: Persistent[bool] = False
    long_entry_count: Persistent[int] = 0
    short_entry_count: Persistent[int] = 0
    bars_since_long_exit: Persistent[int] = 9999
    bars_since_short_exit: Persistent[int] = 9999

    trig_buf = buffer_pct / 100.0 * atr
    long_line = upper_trigger + trig_buf
    short_line = lower_trigger - trig_buf
    has_buffer = buffer_pct > 0

    sess_prev_close: Persistent[float] = na(float)
    cross_ref = sess_prev_close if gap_safe_cross and (not na(sess_prev_close)) else close[1]

    raw_long_trigger = signal_close and close > long_line and (cross_ref <= long_line)
    raw_short_trigger = signal_close and close < short_line and (cross_ref >= short_line)

    long_armed = not long_active and (max_entries == 0 or long_entry_count < max_entries) and (bars_since_long_exit >= cooldown_bars)
    short_armed = not short_active and (max_entries == 0 or short_entry_count < max_entries) and (bars_since_short_exit >= cooldown_bars)

    entry_long_trigger = raw_long_trigger and long_armed
    entry_short_trigger = raw_short_trigger and short_armed

    suppressed_long = raw_long_trigger and (not long_armed)
    suppressed_short = raw_short_trigger and (not short_armed)

    exit_long = signal_close and long_active and (close < upper_trigger)
    exit_short = signal_close and short_active and (close > lower_trigger)

    if new_session:
        long_active = False
        short_active = False
        trigger_hour = na
        bars_since_trigger = 0
        bull_reached_382 = False
        bear_reached_382 = False
        long_entry_count = 0
        short_entry_count = 0
        bars_since_long_exit = 9999
        bars_since_short_exit = 9999

    if signal_close:
        bars_since_long_exit = bars_since_long_exit + 1
        bars_since_short_exit = bars_since_short_exit + 1

    if entry_long_trigger:
        long_active = True
        short_active = False
        trigger_hour = hour_et
        bars_since_trigger = 0
        bull_reached_382 = False
        long_entry_count = long_entry_count + 1

    if entry_short_trigger:
        short_active = True
        long_active = False
        trigger_hour = hour_et
        bars_since_trigger = 0
        bear_reached_382 = False
        short_entry_count = short_entry_count + 1

    if exit_long:
        long_active = False
        bars_since_long_exit = 0
    if exit_short:
        short_active = False
        bars_since_short_exit = 0

    if signal_close and (long_active or short_active) and (not (entry_long_trigger or entry_short_trigger)):
        bars_since_trigger = bars_since_trigger + 1

    if session_ok_for_signals and barstate.isconfirmed:
        sess_prev_close = close

    if long_active and close >= upper_0382:
        bull_reached_382 = True
    if short_active and close <= lower_0382:
        bear_reached_382 = True

    entry_long_gg = signal_close and long_active and (close >= upper_0382) and (close[1] < upper_0382)
    entry_short_gg = signal_close and short_active and (close <= lower_0382) and (close[1] > lower_0382)

    raw_long_ema8: Series = signal_close and htf_10m_ok and long_active and bull_reached_382 and (close <= upper_0618) and (low <= ema8_10m) and (close > ema8_10m)
    raw_short_ema8: Series = signal_close and htf_10m_ok and short_active and bear_reached_382 and (close >= lower_0618) and (high >= ema8_10m) and (close < ema8_10m)
    entry_long_ema8 = raw_long_ema8 and (not pb_debounce or not raw_long_ema8[1])
    entry_short_ema8 = raw_short_ema8 and (not pb_debounce or not raw_short_ema8[1])

    raw_long_trigpb: Series = signal_close and long_active and bull_reached_382 and (low <= upper_trigger) and (close > upper_trigger)
    raw_short_trigpb: Series = signal_close and short_active and bear_reached_382 and (high >= lower_trigger) and (close < lower_trigger)
    entry_long_trigpb = raw_long_trigpb and (not pb_debounce or not raw_long_trigpb[1])
    entry_short_trigpb = raw_short_trigpb and (not pb_debounce or not raw_short_trigpb[1])

    pdc_reclaim_bull = htf_10m_ok and new_10m and first_hour and (c10_1 > previous_close) and (c10_2 <= previous_close) and (c10_2 >= lower_trigger)
    pdc_reclaim_bear = htf_10m_ok and new_10m and first_hour and (c10_1 < previous_close) and (c10_2 >= previous_close) and (c10_2 <= upper_trigger)

    bar_counter_color = color.new(color.green, 40) if bars_since_trigger <= 6 else color.new(color.orange, 40) if bars_since_trigger <= 12 else color.new(color.gray, 40)

    vol_avg = ta.sma(volume, 20)
    rel_vol = volume / vol_avg if vol_avg > 0 else 1.0
    rel_vol_pct = math.round(rel_vol * 100)
    vol_note = 'RelVol ' + string.tostring(rel_vol_pct) + '% (' + ('high' if rel_vol >= 1.5 else 'normal' if rel_vol >= 0.8 else 'low') + ') -- discretionary'

    tr_vs_atr_color = color.green if tr_percent_of_atr <= 70 else color.red if tr_percent_of_atr >= 90 else color.orange
    trading_mode = 'Day' if trading_type == day_trading else 'Multiday' if trading_type == multiday_trading else 'Swing' if trading_type == swing_trading else 'Position' if trading_type == position_trading else 'Long-term'
    long_label = 'Calls' if use_options_labels else 'Long'
    short_label = 'Puts' if use_options_labels else 'Short'
    trend_color = color.green if bullish else color.red if bearish else color.orange
    table_size_val = size.small if table_size == 'Small' else size.large if table_size == 'Large' else size.normal
    session_tag = 'RTH' if session_mode == 'Regular (RTH)' else 'EXT'
    table_pos = position.top_right if table_position == 'Top Right' else position.bottom_left if table_position == 'Bottom Left' else position.bottom_right

    tbl: Persistent = table.new(table_pos, 1, 6, border_width=1, frame_color=trend_color)
    if barstate.islast and show_info:
        table.cell(tbl, 0, 0, 'Trinity ATR Levels  [' + session_tag + ']', bgcolor=trend_color, text_size=table_size_val)
        table.cell(tbl, 0, 1, trading_mode + ' Range ($' + string.tostring(range_1, '#.##') + ') is ' + string.tostring(tr_percent_of_atr, '#.#') + '% of ATR', bgcolor=tr_vs_atr_color, text_size=table_size_val)
        table.cell(tbl, 0, 2, 'PDC $' + string.tostring(previous_close, '#.##') + '  ATR $' + string.tostring(atr, '#.##'), bgcolor=color.new(color.gray, 20), text_size=table_size_val)
        table.cell(tbl, 0, 3, long_label + ' > $' + string.tostring(upper_trigger, '#.##'), bgcolor=c_up, text_size=table_size_val)
        table.cell(tbl, 0, 4, short_label + ' < $' + string.tostring(lower_trigger, '#.##'), bgcolor=c_dn, text_size=table_size_val)
        table.cell(tbl, 0, 5, 'PDH $' + string.tostring(pdh, '#.##') + '  PDL $' + string.tostring(pdl, '#.##') + '  PMH $' + string.tostring(pm_high, '#.##') + '  PML $' + string.tostring(pm_low, '#.##'), bgcolor=color.new(color.rgb(180, 190, 210), 0), text_color=color.black, text_size=table_size_val)

    latched_bull = ladder_bull(nz(trigger_hour, 9))
    latched_bear = ladder_bear(nz(trigger_hour, 9))
    latched_pct = latched_bull if long_active else latched_bear if short_active else na

    time_quality = 'TRIGGERED ' + string.tostring(nz(trigger_hour, 9)) + ':00 ET' + st('  |  Gate completion for this trigger hour: ' + pct(latched_pct) + '  (' + ('bull' if long_active else 'bear') + ' ladder)') if long_active or short_active else 'PRE-MARKET  |  Levels set. Wait for the open.' if time_decimal < 9.5 else 'OPEN' + st('  |  Gap straight through 38.2%: bull ' + pct(S_open_gap_bull) + ' / bear ' + pct(S_open_gap_bear)) + '  |  Best window of the day.' if time_decimal < 10.0 else 'NO TRIGGER YET  |  ' + string.tostring(hour_et) + ':00 ET' + st('  |  If one latches now: bull ' + pct(ladder_bull(hour_et)) + ' / bear ' + pct(ladder_bear(hour_et)))

    timing_color = color.new(color.rgb(70, 70, 90), 20) if not stats_valid else color.new(color.gray, 40) if na(latched_pct) else color.new(color.green, 20) if latched_pct >= 60 else color.new(color.orange, 30) if latched_pct >= 45 else color.new(color.red, 25)

    mk_tbl_pos = position.top_left if milkman_table_position == 'Top Left' else position.top_right if milkman_table_position == 'Top Right' else position.bottom_left if milkman_table_position == 'Bottom Left' else position.bottom_right
    mk_tbl_size = size.small if milkman_table_size == 'Small' else size.large if milkman_table_size == 'Large' else size.normal

    price_zone = 'Above +1 ATR -- full range hit.' + st(' Rare (' + pct(S_day_atr_bull) + ' of days).') if close >= upper_1000 else 'Between 78.6% and +1 ATR -- post-Gate extension.' if close >= upper_0786 else 'At or above 61.8% -- Golden Gate complete.' if close >= upper_0618 else 'Between 50% and 61.8% -- inside the Gate, past midpoint.' if close >= upper_0500 else 'Between 38.2% and 50% -- the Gate just opened.' if close >= upper_0382 else 'Between trigger and 38.2% -- en route to the Gate.' if close >= upper_trigger else 'Between PDC and call trigger -- bull trigger box.' if close >= previous_close else 'Between PDC and put trigger -- bear trigger box.' if close >= lower_trigger else 'Between trigger and 38.2% -- en route to the bear Gate.' if close >= lower_0382 else 'Between 38.2% and 50% -- bear Gate just opened.' if close >= lower_0500 else 'Between 50% and 61.8% -- inside the bear Gate.' if close >= lower_0618 else 'At or below 61.8% -- bear Golden Gate complete.' if close >= lower_0786 else 'Between 78.6% and -1 ATR -- bear post-Gate extension.' if close >= lower_1000 else 'Below -1 ATR -- full bear range hit.' + st(' Rare (' + pct(S_day_atr_bear) + ' of days).')

    dash_bull = color.new(color.rgb(0, 80, 125), 0) if cb else color.new(color.rgb(20, 90, 30), 0)
    dash_bear = color.new(color.rgb(150, 66, 0), 0) if cb else color.new(color.rgb(110, 20, 20), 0)
    dash_wait = color.new(color.rgb(150, 120, 10), 5)
    price_zone_color = dash_bull if long_active else dash_bear if short_active else dash_wait

    tf_warning = '' if tf_ok_for_signals else '\n⚠Signals gated OFF -- not a 3m chart.'

    def entry_price_txt(up: bool):
        return '$' + string.tostring(long_line if up else short_line, '#.##') + ' (trigger $' + string.tostring(upper_trigger if up else lower_trigger, '#.##') + ' + ' + string.tostring(buffer_pct, '#.#') + '% ATR buffer)' if has_buffer else '$' + string.tostring(upper_trigger if up else lower_trigger, '#.##')

    watch_note = 'HOLD above $' + string.tostring(upper_trigger, '#.##') + ' on a confirmed close.\nClose back below = EXIT.' + st(' Same-day 38.2% falls to ' + pct(S_call_invalidated) + '.') + tf_warning if long_active and close < upper_0382 else 'HOLD below $' + string.tostring(lower_trigger, '#.##') + ' on a confirmed close.\nClose back above = EXIT.' + st(' (Invalidation % is calls-only research.)') + tf_warning if short_active and close > lower_0382 else 'Confirmed close back BELOW the trigger = EXIT.\nWatch the trigger and 10m EMA8 for re-entry.' if long_active and close < upper_0618 else 'Confirmed close back ABOVE the trigger = EXIT.\nWatch the trigger and 10m EMA8 for re-entry.' if short_active and close > lower_0618 else 'Trail to 38.2%. Gate complete.' + st('\nTo 78.6%: ' + pct(S_l618_786_bull) + ' (' + pct(S_bilbo_786_bull) + ' with Bilbo).') if close >= upper_0618 else 'Trail to 38.2%. Bear Gate done.' + st('\nTo 78.6%: ' + pct(S_l618_786_bear) + ' (' + pct(S_bilbo_786_bear) + ' with Bilbo).') if close <= lower_0618 else 'Confirmed close ABOVE ' + entry_price_txt(True) + ' = enter.\nPDC reclaim in the first hour = flip bear' + st(' (' + pct(S_pdc_reclaim_trig) + ' reach the opposite trigger)') + '.' + tf_warning if in_bull_trigger_box else 'Confirmed close BELOW ' + entry_price_txt(False) + ' = enter.\nPDC reclaim in the first hour = flip bull' + st(' (' + pct(S_pdc_reclaim_trig) + ' reach the opposite trigger)') + '.' + tf_warning if in_bear_trigger_box else 'No active setup. Wait for the trigger box.' + st('\n' + pct(S_days_open_in_box) + ' of days open there.')

    entry_note = 'ENTER LONG  ' + entry_price_txt(True) + st('\n' + pct(S_call_conf_382) + ' reach 38.2% same day. Close back below -> ' + pct(S_call_invalidated) + ' = exit.') if entry_long_trigger else 'ENTER SHORT  ' + entry_price_txt(False) + st('\nTrigger to 38.2%: ' + pct(S_trig_382_bear) + '. No put-side 3m study exists.') if entry_short_trigger else 'T-PB LONG (pullback to trigger)' + st('  -- BEST EV ' + ev(S_ev_trigpb_bull)) + '\nTarget 61.8% $' + string.tostring(upper_0618, '#.##') if entry_long_trigpb else 'T-PB SHORT (pullback to trigger)' + st('  -- BEST EV ' + ev(S_ev_trigpb_bear)) + '\nTarget 61.8% $' + string.tostring(lower_0618, '#.##') if entry_short_trigpb else 'GATE ENTRY LONG  $' + string.tostring(upper_0382, '#.##') + st('\nImmediate: ' + pct(S_entry_imm_bull) + ', ' + ev(S_ev_imm_bull) + '.') + ' Target 61.8%.' if entry_long_gg else 'GATE ENTRY SHORT  $' + string.tostring(lower_0382, '#.##') + st('\nImmediate: ' + pct(S_entry_imm_bear) + ', ' + ev(S_ev_imm_bear) + '.') + ' Target 61.8%.' if entry_short_gg else 'EMA8 PULLBACK LONG (10-minute EMA8)' + st('\n' + pct(S_entry_ema8_bull) + ', ' + ev(S_ev_ema8_bull) + ' -- ranks below the trigger pullback.') if entry_long_ema8 else 'EMA8 PULLBACK SHORT (10-minute EMA8)' + st('\n' + pct(S_entry_ema8_bear) + ', ' + ev(S_ev_ema8_bear) + ' -- ranks below the trigger pullback.') if entry_short_ema8 else 'In trade. Riding to 38.2%.\nNext entries: Gate open, T-PB' + (', EMA8.' if htf_10m_ok else '. (EMA8 needs a 10m or faster chart.)') if long_active and close < upper_0382 else 'In trade. Riding to 38.2%.\nNext entries: Gate open, T-PB' + (', EMA8.' if htf_10m_ok else '. (EMA8 needs a 10m or faster chart.)') if short_active and close > lower_0382 else 'No entry yet.\nWait for a confirmed close above ' + entry_price_txt(True) if in_bull_trigger_box else 'No entry yet.\nWait for a confirmed close below ' + entry_price_txt(False) if in_bear_trigger_box else 'No setup active.'

    entry_color = color.new(color.green, 5) if entry_long_trigger or entry_long_gg or entry_long_ema8 or entry_long_trigpb else color.new(color.red, 5) if entry_short_trigger or entry_short_gg or entry_short_ema8 or entry_short_trigpb else color.new(color.rgb(120, 90, 20), 10) if suppressed_long or suppressed_short else color.new(color.orange, 30) if in_trigger_box or long_active or short_active else color.new(color.gray, 60)

    target_note = 'T1: $' + string.tostring(upper_0382, '#.##') + ' (38.2%)' + st('  ' + pct(S_trig_382_bull)) + '\nT2: $' + string.tostring(upper_0618, '#.##') + ' (61.8%)' + st('  ' + (pct(S_bilbo_hr if po_1h_rising else S_bilbo_hf) + ' BILBO' if bull_bilbo_active else pct(S_gg_base_bull) + ' baseline')) if long_active and close < upper_0382 else 'T1: $' + string.tostring(upper_0618, '#.##') + ' (61.8%)' + st('  ' + pct(S_l382_618_bull)) + '\nT2: $' + string.tostring(upper_0786, '#.##') + ' (78.6%)' + st('  ' + (pct(S_bilbo_786_bull) + ' Bilbo' if bull_bilbo_active else pct(S_base_786_bull) + ' base')) if long_active and close >= upper_0382 and (close < upper_0618) else 'T1: $' + string.tostring(upper_0786, '#.##') + ' (78.6%)' + st('  ' + pct(S_l618_786_bull)) + '\nT2: $' + string.tostring(upper_1000, '#.##') + ' (+1 ATR)' + st('  ' + (pct(S_bilbo_atr_bull) + ' Bilbo' if bull_bilbo_active else pct(S_l786_atr_bull) + ' from 78.6')) if close >= upper_0618 and close < upper_0786 else 'T1: $' + string.tostring(lower_0382, '#.##') + ' (38.2%)' + st('  ' + pct(S_trig_382_bear)) + '\nT2: $' + string.tostring(lower_0618, '#.##') + ' (61.8%)' + st('  ' + (pct(S_bilbo_lf if po_1h_falling else S_bilbo_lr) + ' BILBO' if bear_bilbo_active else pct(S_gg_base_bear) + ' baseline')) if short_active and close > lower_0382 else 'T1: $' + string.tostring(lower_0618, '#.##') + ' (61.8%)' + st('  ' + pct(S_l382_618_bear)) + '\nT2: $' + string.tostring(lower_0786, '#.##') + ' (78.6%)' + st('  ' + (pct(S_bilbo_786_bear) + ' Bilbo' if bear_bilbo_active else pct(S_base_786_bear) + ' base')) if short_active and close <= lower_0382 and (close > lower_0618) else 'T1: $' + string.tostring(lower_0786, '#.##') + ' (78.6%)' + st('  ' + pct(S_l618_786_bear)) + '\nT2: $' + string.tostring(lower_1000, '#.##') + ' (-1 ATR)' + st('  ' + (pct(S_bilbo_atr_bear) + ' Bilbo' if bear_bilbo_active else pct(S_l786_atr_bear) + ' from 78.6')) if close <= lower_0618 and close > lower_0786 else 'If triggered: T1 $' + string.tostring(upper_0382, '#.##') + st(' (' + pct(S_trig_382_bull) + ')') + '\nGate T2 $' + string.tostring(upper_0618, '#.##') + st('  ' + ('(BILBO active)' if bull_bilbo_active else '(' + pct(S_gg_base_bull) + ' baseline)')) if in_bull_trigger_box else 'If triggered: T1 $' + string.tostring(lower_0382, '#.##') + st(' (' + pct(S_trig_382_bear) + ')') + '\nGate T2 $' + string.tostring(lower_0618, '#.##') + st('  ' + ('(BILBO active)' if bear_bilbo_active else '(' + pct(S_gg_base_bear) + ' baseline)')) if in_bear_trigger_box else 'No active target'

    buffer_stop_note = '\nEntry was ' + string.tostring(buffer_pct, '#.#') + '% ATR beyond this; the stop uses the trigger itself.' if has_buffer else ''

    stop_note = 'Confirmed close below $' + string.tostring(upper_trigger, '#.##') + st('\nTrigger holding -> ' + pct(S_trig_holds_bull) + ' Gate completion (10m closes)') + buffer_stop_note if long_active and close >= upper_0382 else 'Confirmed close below $' + string.tostring(upper_trigger, '#.##') + '\nEXIT.' + st(' Reaching 38.2% drops to ' + pct(S_call_invalidated) + '.') + buffer_stop_note if long_active else 'Confirmed close above $' + string.tostring(lower_trigger, '#.##') + st('\nTrigger holding -> ' + pct(S_trig_holds_bear) + ' Gate completion (10m closes)') + buffer_stop_note if short_active and close <= lower_0382 else 'Confirmed close above $' + string.tostring(lower_trigger, '#.##') + '\nEXIT immediately on any close back above.' + buffer_stop_note if short_active else 'Trail to $' + string.tostring(upper_0382, '#.##') + ' (38.2%)\nGate gain locked in' if close >= upper_0618 and close < upper_0786 else 'Trail to $' + string.tostring(lower_0382, '#.##') + ' (38.2%)\nGate gain locked in' if close <= lower_0618 and close > lower_0786 else 'Trail to $' + string.tostring(upper_0618, '#.##') + ' (61.8%)\nProtect the extension' if close >= upper_0786 else 'Trail to $' + string.tostring(lower_0618, '#.##') + ' (61.8%)\nProtect the extension' if close <= lower_0786 else 'No stop active yet'

    stall_note = st('Median winner reaches 38.2% in ' + string.tostring(S_median_mins_382) + ' min -- half take longer.\n') + 'There is no time stop in the research. [discretionary]' if long_active and close < upper_0382 else st('Median winner reaches 38.2% in ' + string.tostring(S_median_mins_382) + ' min -- half take longer.\n') + 'There is no time stop in the research. [discretionary]' if short_active and close > lower_0382 else 'Consolidation at 38.2% is normal.\nWatch the trigger, not the stall. [discretionary]' if close >= upper_0382 and close < upper_0500 else 'Consolidation at 38.2% is normal.\nWatch the trigger, not the stall. [discretionary]' if close <= lower_0382 and close > lower_0500 else 'At 50% -- do NOT enter fresh.' + st(' EV ' + ev(S_ev_mid50_bull) + '.') + '\nHold to 61.8%.' if close >= upper_0500 and close < upper_0618 else 'At 50% -- do NOT enter fresh.' + st(' EV ' + ev(S_ev_mid50_bear) + '.') + '\nHold to 61.8%.' if close <= lower_0500 and close > lower_0618 else 'Scale out. Check the 1h PO.' + st('\nBilbo? ' + pct(S_bilbo_786_bull) + ' reach 78.6%. No Bilbo: ' + pct(S_base_786_bull) + '.') if close >= upper_0618 else 'Scale out. Check the 1h PO.' + st('\nBilbo? ' + pct(S_bilbo_786_bear) + ' reach 78.6%. No Bilbo: ' + pct(S_base_786_bear) + '.') if close <= lower_0618 else 'Box held 1h (10m closes) -> Gate opens.' + st('\nBull ' + pct(S_box_held_1h_bull) + ' / bear ' + pct(S_box_held_1h_bear) + '. First-hour PDC reclaim reaches the opposite 38.2% ' + pct(S_pdc_reclaim_gg) + ' of the time.') if in_trigger_box else 'No stall scenario active.'

    bilbo_tf_note = '' if htf_1h_ok else '\n⚠above 1h -- the PO is approximated.'

    bilbo_active_text = ('BULL BILBO  High+Rising' + st('  ' + pct(S_bilbo_hr) + '  (n=193)  |  Full size. Runners past 61.8% viable.') + bilbo_tf_note if po_1h_rising else 'BULL BILBO  High+Falling' + st('  ' + pct(S_bilbo_hf) + '  (n=168)  |  Full size. Watch if PO leaves the zone.') + bilbo_tf_note) if bull_bilbo_active else ('BEAR BILBO  Low+Falling' + st('  ' + pct(S_bilbo_lf) + '  (n=141)  |  Strongest state. ' + pct(S_bilbo_atr_bear) + ' reach full ATR.') + bilbo_tf_note if po_1h_falling else 'BEAR BILBO  Low+Rising' + st('  ' + pct(S_bilbo_lr) + '  (n=149)  |  Full size. Watch if PO leaves the zone.') + bilbo_tf_note) if bear_bilbo_active else 'No Bilbo  ·  ' + po_zone_name + '\nMid-zone PO slope = NO signal.' + st('\nBaselines: bull ' + pct(S_gg_base_bull) + ' / bear ' + pct(S_gg_base_bear) + '.') + bilbo_tf_note

    def lvl_dist(lvl: float):
        diff = lvl - close
        return ('+' if diff >= 0 else '') + string.tostring(diff, '#.##') + ('' if na(atr_safe) else ' (' + string.tostring(math.abs(diff) / atr_safe * 100, '#.#') + '% ATR)')

    gg_progress = (close - upper_0382) / (upper_0618 - upper_0382) * 100 if long_active and close > upper_0382 and (upper_0618 > upper_0382) else (lower_0382 - close) / (lower_0382 - lower_0618) * 100 if short_active and close < lower_0382 and (lower_0382 > lower_0618) else na

    bias_up = long_active or in_bull_trigger_box or (not short_active and close >= previous_close)

    dist_note = ('Trigger  ' + lvl_dist(upper_trigger) + '\n38.2%    ' + lvl_dist(upper_0382) + '\n61.8%    ' + lvl_dist(upper_0618) if bias_up else 'Trigger  ' + lvl_dist(lower_trigger) + '\n38.2%    ' + lvl_dist(lower_0382) + '\n61.8%    ' + lvl_dist(lower_0618)) + ('' if na(gg_progress) else '\nThrough the Gate: ' + string.tostring(math.min(100, math.max(0, gg_progress)), '#') + '%')

    budget_used_long = max_entries > 0 and long_entry_count >= max_entries
    budget_used_short = max_entries > 0 and short_entry_count >= max_entries

    tf_degrade_note = '' if htf_10m_ok else '\n⚠' + timeframe.period + ' chart: the 10m EMA8 pullback and\nPDC reclaim are off (10m cannot be read from a slower chart).'

    diagnostic = 'SIGNALS OFF -- chart is ' + timeframe.period + '\nThis mode only fires on 3m. Change chart or mode.' if not tf_ok_for_signals else 'SIGNALS OFF -- outside the signal session\n(' + rth_session + ' exchange time). Levels stay live.' if not session_ok_for_signals else 'LONG live. Exit: a confirmed close below $' + string.tostring(upper_trigger, '#.##') + '.' + tf_degrade_note if long_active else 'SHORT live. Exit: a confirmed close above $' + string.tostring(lower_trigger, '#.##') + '.' + tf_degrade_note if short_active else 'Cross seen, entry BLOCKED -- ' + ('long budget used (' + string.tostring(long_entry_count) + '/' + string.tostring(max_entries) + ') for this session.' if budget_used_long else 'cooldown, ' + string.tostring(math.max(0, cooldown_bars - bars_since_long_exit)) + ' more bar(s).') if suppressed_long else 'Cross seen, entry BLOCKED -- ' + ('short budget used (' + string.tostring(short_entry_count) + '/' + string.tostring(max_entries) + ') for this session.' if budget_used_short else 'cooldown, ' + string.tostring(math.max(0, cooldown_bars - bars_since_short_exit)) + ' more bar(s).') if suppressed_short else 'WAITING -- need a confirmed close above\n$' + string.tostring(long_line, '#.##') + ', currently ' + lvl_dist(long_line) + ' away.' + tf_degrade_note if in_bull_trigger_box else 'WAITING -- need a confirmed close below\n$' + string.tostring(short_line, '#.##') + ', currently ' + lvl_dist(short_line) + ' away.' + tf_degrade_note if in_bear_trigger_box else 'Above the call trigger, but the long budget\nis used for this session. Pullback entries only.' if close > upper_trigger and budget_used_long else 'Below the put trigger, but the short budget\nis used for this session. Pullback entries only.' if close < lower_trigger and budget_used_short else 'Above the call trigger with no open trade --\nthe cross happened outside the signal session.' if close > upper_trigger else 'Below the put trigger with no open trade --\nthe cross happened outside the signal session.' if close < lower_trigger else 'WAITING -- price is at PDC, outside both\ntrigger boxes. No setup forming.' + tf_degrade_note

    diagnostic_color = color.new(color.rgb(120, 60, 0), 10) if not tf_ok_for_signals or not session_ok_for_signals else color.new(color.rgb(100, 70, 10), 10) if not htf_10m_ok else color.new(color.rgb(20, 70, 40), 10) if long_active or short_active else color.new(color.rgb(120, 90, 20), 10) if suppressed_long or suppressed_short else color.new(color.rgb(35, 40, 60), 10)

    context_note = 'Bar ' + string.tostring(bars_since_trigger) + ' since trigger\nEntries: long ' + string.tostring(long_entry_count) + ('/' + string.tostring(max_entries) if max_entries > 0 else '') + ', short ' + string.tostring(short_entry_count) + ('/' + string.tostring(max_entries) if max_entries > 0 else '') + '\n' + vol_note

    BILBO_TIP = 'BILBO -- the 1-hour Phase Oscillator filter.\n\n' + 'The Phase Oscillator measures how far price has stretched from its 21-period EMA, scaled by ATR, so it reads roughly -150 to +150 on any instrument.\n\n' + 'Above +61.8 is the DISTRIBUTION zone. Below -61.8 is ACCUMULATION. When a Golden Gate setup triggers while the last COMPLETED 1-hour bar sits in one of those outer zones, the Gate historically completed more often than baseline. That condition is what "Bilbo" names -- it is a filter on the setup you already have, not a signal of its own.\n\n' + 'The gauge runs bear on the left to bull on the right. The arrow marks the current reading and points up or down according to whether the oscillator rose or fell against the previous completed hour.\n\n' + 'It reads only completed hourly bars, so it never repaints during the hour. Mid-zone slope carries no signal at all -- the old "weak bucket" advice was an artifact of a look-ahead bug, corrected on 2026-04-26.'

    def gauge_str(pos: int, rising: bool):
        g: str = ''
        for i in pine_range(0, 10):
            g = g + (('▲' if rising else '▼') if i == pos else '·')
        return g

    po_gauge_pos = math.round(math.max(0, math.min(10, (math.max(-150, math.min(150, po_1h)) + 150) / 300 * 10)))
    po_gauge = gauge_str(po_gauge_pos, po_1h_rising)

    bilbo_state_short = 'BULL BILBO' + st(' ' + pct(S_bilbo_hr if po_1h_rising else S_bilbo_hf)) if bull_bilbo_active else 'BEAR BILBO' + st(' ' + pct(S_bilbo_lf if po_1h_falling else S_bilbo_lr)) if bear_bilbo_active else 'no Bilbo'

    bilbo_line = 'BEAR ' + po_gauge + ' BULL   ' + string.tostring(po_1h, '#.#') + '  ' + po_zone_name + '\n' + bilbo_state_short + bilbo_tf_note

    loc_compact = 'Above +1 ATR' if close >= upper_1000 else '78.6% to +1 ATR' if close >= upper_0786 else 'Gate COMPLETE (61.8%)' if close >= upper_0618 else 'Inside the Gate' if close >= upper_0382 else 'Trigger to 38.2%' if close >= upper_trigger else 'Bull trigger box' if close >= previous_close else 'Bear trigger box' if close >= lower_trigger else 'Bear trigger to 38.2%' if close >= lower_0382 else 'Inside the bear Gate' if close >= lower_0618 else 'Bear Gate COMPLETE' if close >= lower_0786 else '78.6% to -1 ATR' if close >= lower_1000 else 'Below -1 ATR'

    act_compact = 'Signals off -- chart is ' + timeframe.period if not tf_ok_for_signals else 'Signals off -- outside the session' if not session_ok_for_signals else 'LONG live  ·  exit on close < $' + string.tostring(upper_trigger, '#.##') if long_active else 'SHORT live  ·  exit on close > $' + string.tostring(lower_trigger, '#.##') if short_active else 'Cross blocked -- see Status' if suppressed_long or suppressed_short else 'Wait for a close above $' + string.tostring(long_line, '#.##') if in_bull_trigger_box else 'Wait for a close below $' + string.tostring(short_line, '#.##') if in_bear_trigger_box else 'No setup'

    tgt_compact = 'T1 $' + string.tostring(upper_0382, '#.##') + st(' (' + pct(S_trig_382_bull) + ')') + '   T2 $' + string.tostring(upper_0618, '#.##') + st(' (' + pct(S_gg_base_bull) + ')') if bias_up else 'T1 $' + string.tostring(lower_0382, '#.##') + st(' (' + pct(S_trig_382_bear) + ')') + '   T2 $' + string.tostring(lower_0618, '#.##') + st(' (' + pct(S_gg_base_bear) + ')')

    stop_compact = 'Confirmed close below $' + string.tostring(upper_trigger, '#.##') if long_active else 'Confirmed close above $' + string.tostring(lower_trigger, '#.##') if short_active else 'None active'

    status_compact = 'Signals gated off -- this mode fires on 3m only.' if not tf_ok_for_signals else 'Outside the signal session. Levels stay live.' if not session_ok_for_signals else 'Blocked -- ' + ('long budget used' if budget_used_long else 'cooldown ' + string.tostring(math.max(0, cooldown_bars - bars_since_long_exit)) + ' bar(s)') if suppressed_long else 'Blocked -- ' + ('short budget used' if budget_used_short else 'cooldown ' + string.tostring(math.max(0, cooldown_bars - bars_since_short_exit)) + ' bar(s)') if suppressed_short else 'Bar ' + string.tostring(bars_since_trigger) + ' since trigger' + ('' if na(gg_progress) else '  ·  ' + string.tostring(math.min(100, math.max(0, gg_progress)), '#') + '% through the Gate') if long_active or short_active else 'Waiting  ·  ' + mode_short + ('  ·  stats on' if stats_valid else '  ·  stats off')

    swing_layout = chart_mins > 60

    swing_status = 'SWING LAYOUT · ' + timeframe.period + ' chart\nIntraday rows hidden -- the 3m entry rules, the 1h Bilbo\nfilter and the ET timing ladder cannot be read above 1h.\nLevels, targets, stops and distances remain valid.' + ('\nLevel Period is still Day -- Swing or Position would suit this chart.' if trading_type == day_trading else '\nLevel Period: ' + trading_mode + '.')

    n_rows = (5 if swing_layout else 7) if compact_mode else 7 if swing_layout else 14

    mk_tbl: Persistent[Table] = na(Table)

    if not show_milkman_table:
        if not na(mk_tbl):
            table.delete(mk_tbl)
            mk_tbl = na
    elif na(mk_tbl):
        mk_tbl = table.new(mk_tbl_pos, 2, n_rows, border_width=1, border_color=color.new(color.rgb(60, 80, 120), 20), frame_color=color.new(color.rgb(40, 60, 100), 5), frame_width=2)

    if barstate.islast and show_milkman_table and (not na(mk_tbl)):
        c_key = color.new(color.rgb(30, 40, 70), 0)
        c_neutral = color.new(color.rgb(22, 28, 50), 0)
        c_mode = color.new(color.rgb(25, 60, 95), 0) if p_milk else color.new(color.rgb(60, 50, 90), 0) if p_univ else color.new(color.rgb(70, 60, 40), 0)
        bilbo_bg = color.new(color.rgb(120, 95, 0), 5) if bull_bilbo_active else color.new(color.rgb(150, 55, 0), 5) if bear_bilbo_active else c_neutral
        gauge_tc = color.new(bilbo_color, 0)
        hdr_color = dash_bull if long_active else dash_bear if short_active else dash_wait

        if compact_mode and swing_layout:
            table.cell(mk_tbl, 0, 0, syminfo.ticker, bgcolor=hdr_color, text_color=color.white, text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 0, timeframe.period + '  ·  ' + trading_mode + ' levels  ·  ATR $' + string.tostring(math.round(atr, 2)), bgcolor=hdr_color, text_color=color.new(color.silver, 10), text_size=mk_tbl_size, tooltip=mode_line)

            table.cell(mk_tbl, 0, 1, 'WHERE', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 1, loc_compact, bgcolor=price_zone_color, text_color=color.white, text_size=mk_tbl_size, tooltip=price_zone)

            table.cell(mk_tbl, 0, 2, 'TARGETS', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 2, tgt_compact, bgcolor=color.new(color.rgb(20, 70, 30), 0), text_color=color.white, text_size=mk_tbl_size, tooltip=target_note)

            table.cell(mk_tbl, 0, 3, 'DISTANCE', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 3, dist_note, bgcolor=c_neutral, text_color=color.new(color.silver, 5), text_size=mk_tbl_size)

            table.cell(mk_tbl, 0, 4, 'LAYOUT', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 4, 'Swing  ·  ' + timeframe.period + '  ·  intraday rows hidden', bgcolor=color.new(color.rgb(60, 55, 90), 10), text_color=color.white, text_size=mk_tbl_size, tooltip=swing_status)
        elif compact_mode:
            table.cell(mk_tbl, 0, 0, syminfo.ticker, bgcolor=hdr_color, text_color=color.white, text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 0, timeframe.period + '  ·  ' + mode_short + '  ·  ATR $' + string.tostring(math.round(atr, 2)) + scope_tag, bgcolor=hdr_color, text_color=color.new(color.silver, 10), text_size=mk_tbl_size, tooltip=mode_line)

            table.cell(mk_tbl, 0, 1, 'WHERE', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 1, loc_compact, bgcolor=price_zone_color, text_color=color.white, text_size=mk_tbl_size, tooltip=price_zone)

            table.cell(mk_tbl, 0, 2, 'DO', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 2, act_compact, bgcolor=entry_color, text_color=color.white, text_size=mk_tbl_size, tooltip=entry_note + '\n\n' + watch_note)

            table.cell(mk_tbl, 0, 3, 'TARGETS', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 3, tgt_compact, bgcolor=color.new(color.rgb(20, 70, 30), 0), text_color=color.white, text_size=mk_tbl_size, tooltip=target_note)

            table.cell(mk_tbl, 0, 4, 'STOP', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 4, stop_compact, bgcolor=color.new(color.rgb(80, 20, 20), 0), text_color=color.white, text_size=mk_tbl_size, tooltip=stop_note)

            table.cell(mk_tbl, 0, 5, 'BILBO', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size, tooltip=BILBO_TIP)
            table.cell(mk_tbl, 1, 5, bilbo_line, bgcolor=bilbo_bg, text_color=gauge_tc, text_size=mk_tbl_size, tooltip=BILBO_TIP)

            table.cell(mk_tbl, 0, 6, 'STATUS', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 6, status_compact, bgcolor=diagnostic_color, text_color=color.white, text_size=mk_tbl_size, tooltip=diagnostic)
        elif swing_layout:
            table.cell(mk_tbl, 0, 0, 'MILKMAN  ' + syminfo.ticker, bgcolor=hdr_color, text_color=color.white, text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 0, timeframe.period + '  |  ' + trading_mode + ' levels  |  ATR $' + string.tostring(math.round(atr, 2)) + '  |  ' + session_tag, bgcolor=hdr_color, text_color=color.new(color.silver, 10), text_size=mk_tbl_size)

            table.cell(mk_tbl, 0, 1, 'MODE', bgcolor=c_mode, text_color=color.white, text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 1, mode_line, bgcolor=c_mode, text_color=color.new(color.silver, 0), text_size=mk_tbl_size)

            table.cell(mk_tbl, 0, 2, 'LOCATION', bgcolor=price_zone_color, text_color=color.white, text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 2, price_zone, bgcolor=price_zone_color, text_color=color.white, text_size=mk_tbl_size)

            table.cell(mk_tbl, 0, 3, 'TARGETS', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 3, target_note, bgcolor=color.new(color.rgb(20, 70, 30), 0), text_color=color.white, text_size=mk_tbl_size)

            table.cell(mk_tbl, 0, 4, 'STOP', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 4, stop_note, bgcolor=color.new(color.rgb(80, 20, 20), 0), text_color=color.white, text_size=mk_tbl_size)

            table.cell(mk_tbl, 0, 5, 'DISTANCE', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 5, dist_note, bgcolor=c_neutral, text_color=color.new(color.silver, 5), text_size=mk_tbl_size)

            table.cell(mk_tbl, 0, 6, 'LAYOUT', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 6, swing_status, bgcolor=color.new(color.rgb(60, 55, 90), 10), text_color=color.white, text_size=mk_tbl_size)
        else:
            table.cell(mk_tbl, 0, 0, 'MILKMAN  ' + syminfo.ticker, bgcolor=hdr_color, text_color=color.white, text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 0, string.tostring(hour_et) + ':' + ('0' if minute_et < 10 else '') + string.tostring(minute_et) + ' ET · ' + timeframe.period + ' · ATR $' + string.tostring(math.round(atr, 2)) + ' · ' + session_tag + ('' if stats_valid or p_univ else '\nstats hidden -- off:' + scope_reason), bgcolor=hdr_color, text_color=color.new(color.silver, 10), text_size=mk_tbl_size, tooltip=st(STAT_VERSION))

            if show_mode_row:
                table.cell(mk_tbl, 0, 1, 'MODE', bgcolor=c_mode, text_color=color.white, text_size=mk_tbl_size)
                table.cell(mk_tbl, 1, 1, mode_line, bgcolor=c_mode, text_color=color.new(color.silver, 0), text_size=mk_tbl_size)
            else:
                table.cell(mk_tbl, 0, 1, '', bgcolor=c_neutral, text_size=size.tiny)
                table.cell(mk_tbl, 1, 1, '', bgcolor=c_neutral, text_size=size.tiny)

            table.cell(mk_tbl, 0, 2, 'LOCATION', bgcolor=price_zone_color, text_color=color.white, text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 2, price_zone, bgcolor=price_zone_color, text_color=color.white, text_size=mk_tbl_size)

            table.cell(mk_tbl, 0, 3, 'WATCH', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 3, watch_note, bgcolor=c_neutral, text_color=color.white, text_size=mk_tbl_size)

            table.cell(mk_tbl, 0, 4, 'ENTRY', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 4, entry_note, bgcolor=entry_color, text_color=color.white, text_size=mk_tbl_size)

            table.cell(mk_tbl, 0, 5, 'TARGETS', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 5, target_note, bgcolor=color.new(color.rgb(20, 70, 30), 0), text_color=color.white, text_size=mk_tbl_size)

            table.cell(mk_tbl, 0, 6, 'STOP', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 6, stop_note, bgcolor=color.new(color.rgb(80, 20, 20), 0), text_color=color.white, text_size=mk_tbl_size)

            table.cell(mk_tbl, 0, 7, 'IF STALLS', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 7, stall_note, bgcolor=c_neutral, text_color=color.new(color.silver, 10), text_size=mk_tbl_size)

            table.cell(mk_tbl, 0, 8, 'BILBO', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size, tooltip=BILBO_TIP)
            table.cell(mk_tbl, 1, 8, bilbo_line, bgcolor=bilbo_bg, text_color=gauge_tc, text_size=mk_tbl_size, tooltip=BILBO_TIP)

            table.cell(mk_tbl, 0, 9, 'BILBO STATE', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size, tooltip=BILBO_TIP)
            table.cell(mk_tbl, 1, 9, bilbo_active_text, bgcolor=bilbo_bg, text_color=color.white, text_size=mk_tbl_size, tooltip=BILBO_TIP)

            table.cell(mk_tbl, 0, 10, 'CONTEXT', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 10, context_note, bgcolor=bar_counter_color, text_color=color.white, text_size=mk_tbl_size)

            table.cell(mk_tbl, 0, 11, 'TIMING', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
            table.cell(mk_tbl, 1, 11, time_quality, bgcolor=timing_color, text_color=color.white, text_size=mk_tbl_size)

            if show_distance_row:
                table.cell(mk_tbl, 0, 12, 'DISTANCE', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
                table.cell(mk_tbl, 1, 12, dist_note, bgcolor=c_neutral, text_color=color.new(color.silver, 5), text_size=mk_tbl_size)
            else:
                table.cell(mk_tbl, 0, 12, '', bgcolor=c_neutral, text_size=size.tiny)
                table.cell(mk_tbl, 1, 12, '', bgcolor=c_neutral, text_size=size.tiny)

            if show_status_row:
                table.cell(mk_tbl, 0, 13, 'STATUS', bgcolor=c_key, text_color=color.new(color.silver, 20), text_size=mk_tbl_size)
                table.cell(mk_tbl, 1, 13, diagnostic, bgcolor=diagnostic_color, text_color=color.white, text_size=mk_tbl_size)
            else:
                table.cell(mk_tbl, 0, 13, '', bgcolor=c_neutral, text_size=size.tiny)
                table.cell(mk_tbl, 1, 13, '', bgcolor=c_neutral, text_size=size.tiny)

    plot(lower_1000, color=color.new(e_atr1, 40), linewidth=level_size, title='-1 ATR')
    plot(lower_0618, color=color.new(e_618, 40), linewidth=level_size, title='-61.8%')
    plot(lower_0382, color=color.new(e_382, 40), linewidth=level_size, title='-38.2%')
    plot(lower_trigger, color=color.new(c_dn, 40), linewidth=level_size, title='Put Trigger')
    plot(previous_close, color=color.new(e_pdc, 40), linewidth=level_size, title='PDC')
    plot(upper_trigger, color=color.new(c_up, 40), linewidth=level_size, title='Call Trigger')
    plot(upper_0382, color=color.new(e_382, 40), linewidth=level_size, title='+38.2%')
    plot(upper_0618, color=color.new(e_618, 40), linewidth=level_size, title='+61.8%')
    plot(upper_1000, color=color.new(e_atr1, 40), linewidth=level_size, title='+1 ATR')
    plot(ema8_10m_plot if show_ema8_10m else na, color=color.new(ema8_10m_color, 0), linewidth=ema8_10m_width, title='10m EMA8')

    lvl_start_bar: Persistent[int] = 0
    if na(previous_close[1]) or previous_close != previous_close[1] or atr != atr[1]:
        lvl_start_bar = bar_index

    aux_lines: Persistent[list[Line]] = array.new_line()

    def add_lvl(y: float, c: Color, w: int, sty: str):
        __block_result__ = na
        if not na(y):
            __block_result__ = array.push(aux_lines, line.new(lvl_start_bar, y, bar_index, y, extend=extend.right, color=c, width=w, style=sty))
        return __block_result__

    if barstate.islast:
        if array.size(aux_lines) > 0:
            for i in pine_range(0, array.size(aux_lines) - 1):
                line.delete(array.get(aux_lines, i))
            array.clear(aux_lines)

        if eff_show_mid_ext:
            add_lvl(upper_0500, color.new(e_500, 40), level_size, line.style_solid)
            add_lvl(lower_0500, color.new(e_500, 40), level_size, line.style_solid)
            add_lvl(upper_0786, color.new(e_786, 40), level_size, line.style_solid)
            add_lvl(lower_0786, color.new(e_786, 40), level_size, line.style_solid)

        if eff_show_ext:
            add_lvl(upper_1236, color.new(e_ext, 55), 1, line.style_dotted)
            add_lvl(upper_1618, color.new(e_618, 55), 1, line.style_dotted)
            add_lvl(upper_2000, color.new(e_atr1, 55), 1, line.style_dotted)
            add_lvl(upper_2236, color.new(e_ext, 65), 1, line.style_dotted)
            add_lvl(upper_2618, color.new(e_ext, 65), 1, line.style_dotted)
            add_lvl(lower_1236, color.new(e_ext, 55), 1, line.style_dotted)
            add_lvl(lower_1618, color.new(e_618, 55), 1, line.style_dotted)
            add_lvl(lower_2000, color.new(e_atr1, 55), 1, line.style_dotted)
            add_lvl(lower_2236, color.new(e_ext, 65), 1, line.style_dotted)
            add_lvl(lower_2618, color.new(e_ext, 65), 1, line.style_dotted)

        if has_buffer:
            add_lvl(long_line, color.new(c_up, 55), 1, line.style_dashed)
            add_lvl(short_line, color.new(c_dn, 55), 1, line.style_dashed)

    zone_bg = trigger_box_color if show_trigger_box and in_trigger_box else gg_bull_shade if show_golden_gate_box and long_active and (close >= upper_0382) and (close <= upper_0618) else gg_bear_shade if show_golden_gate_box and short_active and (close <= lower_0382) and (close >= lower_0618) else na
    bgcolor(zone_bg, title='Trigger / Golden Gate Shading')

    inside_bull_gate = long_active and close >= upper_0382 and (close <= upper_0618)
    inside_bear_gate = short_active and close <= lower_0382 and (close >= lower_0618)

    gg_bar_col = na if not show_gg_barcolor else (e_gg_bull if entry_long_gg else e_gg_bear if entry_short_gg else na) if gg_barcolor_mode == 'Entry bar only' else e_gg_bull if inside_bull_gate else e_gg_bear if inside_bear_gate else na

    barcolor(gg_bar_col, title='Golden Gate Candle')

    ln_pdh: Persistent[Line] = na(Line)
    ln_pdl: Persistent[Line] = na(Line)
    ln_pmh: Persistent[Line] = na(Line)
    ln_pml: Persistent[Line] = na(Line)
    if not na(ln_pdh):
        line.delete(ln_pdh)
    if not na(ln_pdl):
        line.delete(ln_pdl)
    if not na(ln_pmh):
        line.delete(ln_pmh)
    if not na(ln_pml):
        line.delete(ln_pml)
    if barstate.islast:
        if eff_show_pdh_pdl and (not na(pdh)):
            ln_pdh = line.new(lvl_start_bar, pdh, bar_index, pdh, extend=extend.right, color=pdh_color, width=session_level_size, style=line.style_dashed)
        if eff_show_pdh_pdl and (not na(pdl)):
            ln_pdl = line.new(lvl_start_bar, pdl, bar_index, pdl, extend=extend.right, color=pdl_color, width=session_level_size, style=line.style_dashed)
        if eff_show_pmh_pml and (not na(pm_high)):
            ln_pmh = line.new(sess_start_bar, pm_high, bar_index, pm_high, extend=extend.right, color=pmh_color, width=session_level_size, style=line.style_dotted)
        if eff_show_pmh_pml and (not na(pm_low)):
            ln_pml = line.new(sess_start_bar, pm_low, bar_index, pm_low, extend=extend.right, color=pml_color, width=session_level_size, style=line.style_dotted)

    ref_close_label: Persistent[Label] = na(Label)
    targetLabel: Persistent[Label] = na(Label)
    stopLabel: Persistent[Label] = na(Label)
    ema8_label: Persistent[Label] = na(Label)
    fib0382u: Persistent[Label] = na(Label)
    fib0500u: Persistent[Label] = na(Label)
    fib0618u: Persistent[Label] = na(Label)
    fib0786u: Persistent[Label] = na(Label)
    fib1000u: Persistent[Label] = na(Label)
    fib1236u: Persistent[Label] = na(Label)
    fib1618u: Persistent[Label] = na(Label)
    fib2000u: Persistent[Label] = na(Label)
    fib2236u: Persistent[Label] = na(Label)
    fib2618u: Persistent[Label] = na(Label)
    fib0382d: Persistent[Label] = na(Label)
    fib0500d: Persistent[Label] = na(Label)
    fib0618d: Persistent[Label] = na(Label)
    fib0786d: Persistent[Label] = na(Label)
    fib1000d: Persistent[Label] = na(Label)
    fib1236d: Persistent[Label] = na(Label)
    fib1618d: Persistent[Label] = na(Label)
    fib2000d: Persistent[Label] = na(Label)
    fib2236d: Persistent[Label] = na(Label)
    fib2618d: Persistent[Label] = na(Label)
    prob_trig_u: Persistent[Label] = na(Label)
    prob_382_u: Persistent[Label] = na(Label)
    prob_618_u: Persistent[Label] = na(Label)
    prob_786_u: Persistent[Label] = na(Label)
    prob_atr1_u: Persistent[Label] = na(Label)
    prob_trig_d: Persistent[Label] = na(Label)
    prob_382_d: Persistent[Label] = na(Label)
    prob_618_d: Persistent[Label] = na(Label)
    prob_786_d: Persistent[Label] = na(Label)
    prob_atr1_d: Persistent[Label] = na(Label)
    gg_zone_label_u: Persistent[Label] = na(Label)
    gg_zone_label_d: Persistent[Label] = na(Label)
    pdh_label: Persistent[Label] = na(Label)
    pdl_label: Persistent[Label] = na(Label)
    pmh_label: Persistent[Label] = na(Label)
    pml_label: Persistent[Label] = na(Label)

    lab_x = bar_index + label_right_offset

    if barstate.islast:
        label.delete(ref_close_label)
        label.delete(targetLabel)
        label.delete(stopLabel)
        label.delete(ema8_label)
        label.delete(fib0382u)
        label.delete(fib0500u)
        label.delete(fib0618u)
        label.delete(fib0786u)
        label.delete(fib1000u)
        label.delete(fib1236u)
        label.delete(fib1618u)
        label.delete(fib2000u)
        label.delete(fib2236u)
        label.delete(fib2618u)
        label.delete(fib0382d)
        label.delete(fib0500d)
        label.delete(fib0618d)
        label.delete(fib0786d)
        label.delete(fib1000d)
        label.delete(fib1236d)
        label.delete(fib1618d)
        label.delete(fib2000d)
        label.delete(fib2236d)
        label.delete(fib2618d)
        label.delete(prob_trig_u)
        label.delete(prob_382_u)
        label.delete(prob_618_u)
        label.delete(prob_786_u)
        label.delete(prob_atr1_u)
        label.delete(prob_trig_d)
        label.delete(prob_382_d)
        label.delete(prob_618_d)
        label.delete(prob_786_d)
        label.delete(prob_atr1_d)
        label.delete(gg_zone_label_u)
        label.delete(gg_zone_label_d)
        label.delete(pdh_label)
        label.delete(pdl_label)
        label.delete(pmh_label)
        label.delete(pml_label)

        ref_close_label = label.new(lab_x, previous_close, 'PDC: $' + string.tostring(previous_close, '#.##'), style=label.style_label_left, color=color.new(e_pdc, 0), textcolor=color.black, size=sess_lbl_sz)

        if show_ema8_10m and show_ema8_10m_label and (not na(ema8_10m_plot)):
            ema8_label = label.new(lab_x, ema8_10m_plot, '10m EMA8 $' + string.tostring(ema8_10m_plot, '#.##') + ('' if htf_10m_ok else ' (approx)'), style=label.style_label_left, color=color.new(ema8_10m_color, 0), textcolor=color.black, size=sess_lbl_sz)

        if show_session_labels:
            if eff_show_pdh_pdl and (not na(pdh)):
                pdh_label = label.new(lab_x, pdh, 'PDH $' + string.tostring(pdh, '#.##'), style=label.style_label_left, color=color.new(pdh_color, 0), textcolor=color.black, size=sess_lbl_sz)
            if eff_show_pdh_pdl and (not na(pdl)):
                pdl_label = label.new(lab_x, pdl, 'PDL $' + string.tostring(pdl, '#.##'), style=label.style_label_left, color=color.new(pdl_color, 0), textcolor=color.white, size=sess_lbl_sz)
            if eff_show_pmh_pml and (not na(pm_high)):
                pmh_label = label.new(lab_x, pm_high, 'PMH $' + string.tostring(pm_high, '#.##'), style=label.style_label_left, color=color.new(pmh_color, 0), textcolor=color.white, size=sess_lbl_sz)
            if eff_show_pmh_pml and (not na(pm_low)):
                pml_label = label.new(lab_x, pm_low, 'PML $' + string.tostring(pm_low, '#.##'), style=label.style_label_left, color=color.new(pml_color, 0), textcolor=color.white, size=sess_lbl_sz)

        if show_fib_labels:
            fib0382u = label.new(lab_x, upper_0382, '38.2%  $' + string.tostring(upper_0382, '#.##'), style=label.style_label_right, color=color.new(e_382, 30), textcolor=color.white, size=sess_lbl_sz)
            fib0382d = label.new(lab_x, lower_0382, '38.2%  $' + string.tostring(lower_0382, '#.##'), style=label.style_label_right, color=color.new(e_382, 30), textcolor=color.white, size=sess_lbl_sz)
            fib0618u = label.new(lab_x, upper_0618, 'GATE TARGET 61.8%  $' + string.tostring(upper_0618, '#.##'), style=label.style_label_right, color=color.new(e_618, 20), textcolor=color.white, size=sess_lbl_sz)
            fib0618d = label.new(lab_x, lower_0618, 'GATE TARGET 61.8%  $' + string.tostring(lower_0618, '#.##'), style=label.style_label_right, color=color.new(e_618, 20), textcolor=color.white, size=sess_lbl_sz)
            fib1000u = label.new(lab_x, upper_1000, '+1 ATR  $' + string.tostring(upper_1000, '#.##'), style=label.style_label_right, color=color.new(e_atr1, 20), textcolor=color.black, size=sess_lbl_sz)
            fib1000d = label.new(lab_x, lower_1000, '-1 ATR  $' + string.tostring(lower_1000, '#.##'), style=label.style_label_right, color=color.new(e_atr1, 20), textcolor=color.black, size=sess_lbl_sz)

            if eff_show_mid_ext:
                fib0786u = label.new(lab_x, upper_0786, '78.6%  $' + string.tostring(upper_0786, '#.##'), style=label.style_label_right, color=color.new(e_786, 30), textcolor=color.white, size=sess_lbl_sz)
                fib0786d = label.new(lab_x, lower_0786, '78.6%  $' + string.tostring(lower_0786, '#.##'), style=label.style_label_right, color=color.new(e_786, 30), textcolor=color.white, size=sess_lbl_sz)

            if eff_show_ext:
                fib1236u = label.new(lab_x, upper_1236, '123.6%', style=label.style_label_left, color=color.new(e_ext, 0), textcolor=color.white, size=sess_lbl_sz)
                fib1618u = label.new(lab_x, upper_1618, '161.8%', style=label.style_label_left, color=color.new(e_618, 0), textcolor=color.white, size=sess_lbl_sz)
                fib2000u = label.new(lab_x, upper_2000, '+2 ATR', style=label.style_label_left, color=color.new(e_atr1, 0), textcolor=color.white, size=sess_lbl_sz)
                fib2236u = label.new(lab_x, upper_2236, '223.6%', style=label.style_label_left, color=color.new(e_ext, 0), textcolor=color.white, size=sess_lbl_sz)
                fib2618u = label.new(lab_x, upper_2618, '261.8%', style=label.style_label_left, color=color.new(e_ext, 0), textcolor=color.white, size=sess_lbl_sz)
                fib1236d = label.new(lab_x, lower_1236, '123.6%', style=label.style_label_left, color=color.new(e_ext, 0), textcolor=color.white, size=sess_lbl_sz)
                fib1618d = label.new(lab_x, lower_1618, '161.8%', style=label.style_label_left, color=color.new(e_618, 0), textcolor=color.white, size=sess_lbl_sz)
                fib2000d = label.new(lab_x, lower_2000, '-2 ATR', style=label.style_label_left, color=color.new(e_atr1, 0), textcolor=color.white, size=sess_lbl_sz)
                fib2236d = label.new(lab_x, lower_2236, '223.6%', style=label.style_label_left, color=color.new(e_ext, 0), textcolor=color.white, size=sess_lbl_sz)
                fib2618d = label.new(lab_x, lower_2618, '261.8%', style=label.style_label_left, color=color.new(e_ext, 0), textcolor=color.white, size=sess_lbl_sz)

        if label_mode != 'Off':
            trig_u_text = 'CALL TRIGGER  $' + string.tostring(upper_trigger, '#.##') + '  |  confirmed close above = entry' + st('  |  ' + pct(S_call_conf_382) + ' reach 38.2% same day  |  back below -> ' + pct(S_call_invalidated)) + '  |  close back below = EXIT' if label_mode == 'Summary' else 'CALL TRIGGER  $' + string.tostring(upper_trigger, '#.##') + '  (' + trig_pct_txt + ')' + '\n' + 'The entry gate. Price must CLOSE a confirmed candle above this level -- a touch or a wick does not count.' + '\n' + st('After a confirmed close above: ' + pct(S_call_conf_382) + ' reach 38.2% the same day.' + '\n' + 'If price then closes back BELOW this line, that falls to ' + pct(S_call_invalidated) + '. The invalidation filter is the whole edge.' + '\n' + 'The median winner reaches 38.2% in ' + string.tostring(S_median_mins_382) + ' minutes -- the MEDIAN, so half take longer. There is no deadline.') + ('' if stats_valid else 'Statistics are off in this mode. The mechanic is unchanged: enter on a confirmed close through the level, exit on a confirmed close back through it.')
            prob_trig_u = label.new(lab_x, upper_trigger, trig_u_text, style=label.style_label_left, color=label_bg_color, textcolor=label_text_color, size=lbl_sz)

            gg_382_u_text = 'GATE OPENS  $' + string.tostring(upper_0382, '#.##') + st('  |  ' + pct(S_trig_382_bull) + ' reach here  |  to 61.8%: ' + pct(S_l382_618_bull) + '  |  best entry = pullback to trigger (' + ev(S_ev_trigpb_bull) + ')') if label_mode == 'Summary' else 'GOLDEN GATE OPENS  $' + string.tostring(upper_0382, '#.##') + '  (38.2% ATR)' + '\n' + 'The trade corridor runs from here to 61.8%.' + '\n' + st(pct(S_trig_382_bull) + ' of bull trigger days reach here. From here to 61.8%: ' + pct(S_l382_618_bull) + '.' + '\n' + 'Entry options, ranked by EV:' + '\n' + '  1. Pullback to the TRIGGER -- ' + ev(S_ev_trigpb_bull) + ', appears on 63% of setups. Best EV.' + '\n' + '  2. Immediate at 38.2% -- ' + pct(S_entry_imm_bull) + ', ' + ev(S_ev_imm_bull) + '.' + '\n' + '  3. Pullback to the 10-MINUTE EMA8 -- ' + pct(S_entry_ema8_bull) + ', ' + ev(S_ev_ema8_bull) + '.' + '\n' + 'Do NOT wait for the 50% midpoint -- fresh entries there are ' + ev(S_ev_mid50_bull) + '.') + ('' if stats_valid else 'Entry options: pullback to the trigger, immediate at 38.2%, or a pullback to the 10-minute EMA8. Avoid fresh entries at the 50% midpoint.')
            prob_382_u = label.new(lab_x, upper_0382, gg_382_u_text, style=label.style_label_left, color=label_bg_color, textcolor=label_text_color, size=lbl_sz)

            if eff_show_mid_ext:
                mid_500_u_text = '50% MIDPOINT  $' + string.tostring(upper_0500, '#.##') + '  |  do NOT enter fresh' + st(' (' + ev(S_ev_mid50_bull) + ')') + '  |  already in: hold, stop at the trigger' if label_mode == 'Summary' else '50% MIDPOINT  $' + string.tostring(upper_0500, '#.##') + '\n' + 'Halfway through the Gate. Do NOT enter fresh here' + st(' -- measured EV is ' + ev(S_ev_mid50_bull)) + '. Reward left to 61.8% is smaller than the risk back to the trigger.' + '\n' + 'Already in: hold. Stop stays a confirmed close back through the trigger.'
                fib0500u = label.new(lab_x, upper_0500, mid_500_u_text, style=label.style_label_left, color=label_bg_color, textcolor=label_text_color, size=lbl_sz)

                mid_500_d_text = '50% MIDPOINT  $' + string.tostring(lower_0500, '#.##') + '  |  do NOT enter fresh' + st(' (' + ev(S_ev_mid50_bear) + ')') + '  |  already in: hold, stop at the trigger' if label_mode == 'Summary' else '50% MIDPOINT  $' + string.tostring(lower_0500, '#.##') + '\n' + 'Halfway through the bear Gate. Do NOT enter fresh here' + st(' -- measured EV is ' + ev(S_ev_mid50_bear)) + '.' + '\n' + 'Already in: hold. Stop stays a confirmed close back through the trigger.'
                fib0500d = label.new(lab_x, lower_0500, mid_500_d_text, style=label.style_label_left, color=label_bg_color, textcolor=label_text_color, size=lbl_sz)

                ext_786_u_text = 'POST-GATE  $' + string.tostring(upper_0786, '#.##') + st('  |  ' + pct(S_l618_786_bull) + ' of 61.8% touches reach here  |  to +1 ATR: ' + pct(S_l786_atr_bull)) + '  |  trail to 61.8%' if label_mode == 'Summary' else 'POST-GATE EXTENSION  $' + string.tostring(upper_0786, '#.##') + '  (78.6% ATR)' + '\n' + 'Beyond the Gate. Trail your stop up to 61.8% on arrival. Do not add here.' + '\n' + st(pct(S_l618_786_bull) + ' of 61.8% touches reach here. From here to the full ATR: ' + pct(S_l786_atr_bull) + '.')
                prob_786_u = label.new(lab_x, upper_0786, ext_786_u_text, style=label.style_label_left, color=label_bg_color, textcolor=label_text_color, size=lbl_sz)

                ext_786_d_text = 'POST-GATE  $' + string.tostring(lower_0786, '#.##') + st('  |  ' + pct(S_l618_786_bear) + ' of 61.8% touches reach here  |  to -1 ATR: ' + pct(S_l786_atr_bear)) + '  |  trail to 61.8%' if label_mode == 'Summary' else 'POST-GATE EXTENSION  $' + string.tostring(lower_0786, '#.##') + '  (78.6% ATR)' + '\n' + 'Beyond the bear Gate. Trail your stop to 61.8% on arrival. Do not add here.' + '\n' + st(pct(S_l618_786_bear) + ' of 61.8% touches reach here. From here to the full ATR: ' + pct(S_l786_atr_bear) + '.')
                prob_786_d = label.new(lab_x, lower_0786, ext_786_d_text, style=label.style_label_left, color=label_bg_color, textcolor=label_text_color, size=lbl_sz)

            gg_618_u_text = 'GATE TARGET  $' + string.tostring(upper_0618, '#.##') + st('  |  ' + pct(S_gg_base_bull) + ' baseline (Bilbo ' + pct(S_bilbo_hr) + '/' + pct(S_bilbo_hf) + ')') + '  |  scale out 50%+' if label_mode == 'Summary' else 'GOLDEN GATE TARGET  $' + string.tostring(upper_0618, '#.##') + '  (61.8% ATR)' + '\n' + 'The primary target. The Gate completes here. Scale out at least half.' + '\n' + st('Bull baseline: ' + pct(S_gg_base_bull) + ' (n=3,421). With Bilbo at entry: High+Rising ' + pct(S_bilbo_hr) + ', High+Falling ' + pct(S_bilbo_hf) + '.' + '\n' + 'No Bilbo? From here to 78.6% is ' + pct(S_base_786_bull) + '. Bilbo? ' + pct(S_bilbo_786_bull) + ' to 78.6% and ' + pct(S_bilbo_atr_bull) + ' to +1 ATR.')
            prob_618_u = label.new(lab_x, upper_0618, gg_618_u_text, style=label.style_label_left, color=label_bg_color, textcolor=label_text_color, size=lbl_sz)

            atr1_u_text = 'FULL ATR  $' + string.tostring(upper_1000, '#.##') + st('  |  ' + pct(S_day_atr_bull) + ' of ALL days reach here') + '  |  take full profits' if label_mode == 'Summary' else 'FULL ATR  $' + string.tostring(upper_1000, '#.##') + '  (+1 ATR)' + '\n' + 'Rare territory.' + st(' ' + pct(S_day_atr_bull) + ' of all trading days reach the full upside ATR.') + '\n' + 'Take full profits. There is no researched edge beyond this level. Mean reversion is the base case.'
            prob_atr1_u = label.new(lab_x, upper_1000, atr1_u_text, style=label.style_label_left, color=label_bg_color, textcolor=label_text_color, size=lbl_sz)

            trig_d_text = 'PUT TRIGGER  $' + string.tostring(lower_trigger, '#.##') + '  |  confirmed close below = entry' + st('  |  trigger to 38.2%: ' + pct(S_trig_382_bear) + '  |  no put-side 3m study') if label_mode == 'Summary' else 'PUT TRIGGER  $' + string.tostring(lower_trigger, '#.##') + '  (' + trig_pct_txt + ')' + '\n' + 'The short-side entry gate. Price must CLOSE a confirmed candle below this level.' + '\n' + st('IMPORTANT: the 3-minute close study was run on CALLS ONLY. The ' + pct(S_call_conf_382) + ' / ' + pct(S_call_invalidated) + ' pair does NOT apply here.' + '\n' + 'Measured on the bear side: trigger to 38.2% is ' + pct(S_trig_382_bear) + ', trigger holding to Gate completion is ' + pct(S_trig_holds_bear) + ' (10m closes).' + '\n') + 'Exit rule: a confirmed close back above this line ends the setup.'
            prob_trig_d = label.new(lab_x, lower_trigger, trig_d_text, style=label.style_label_left, color=label_bg_color, textcolor=label_text_color, size=lbl_sz)

            gg_382_d_text = 'GATE OPENS  $' + string.tostring(lower_0382, '#.##') + st('  |  ' + pct(S_trig_382_bear) + ' reach here  |  to 61.8%: ' + pct(S_l382_618_bear) + '  |  best entry = pullback to trigger (' + ev(S_ev_trigpb_bear) + ')') if label_mode == 'Summary' else 'GOLDEN GATE OPENS  $' + string.tostring(lower_0382, '#.##') + '  (38.2% ATR)' + '\n' + 'The bear trade corridor runs from here to 61.8%.' + '\n' + st(pct(S_trig_382_bear) + ' of bear trigger days reach here. From here to 61.8%: ' + pct(S_l382_618_bear) + '.' + '\n' + 'Entry options, ranked by EV:' + '\n' + '  1. Pullback to the TRIGGER -- ' + ev(S_ev_trigpb_bear) + ', appears on 70% of setups. Best EV.' + '\n' + '  2. Immediate at 38.2% -- ' + pct(S_entry_imm_bear) + ', ' + ev(S_ev_imm_bear) + '.' + '\n' + '  3. Bounce to the 10-MINUTE EMA8 -- ' + pct(S_entry_ema8_bear) + ', ' + ev(S_ev_ema8_bear) + '.' + '\n' + 'Bilbo (1h PO Low+Falling) lifts Gate completion to ' + pct(S_bilbo_lf) + ' -- the strongest state in the system.')
            prob_382_d = label.new(lab_x, lower_0382, gg_382_d_text, style=label.style_label_left, color=label_bg_color, textcolor=label_text_color, size=lbl_sz)

            gg_618_d_text = 'GATE TARGET  $' + string.tostring(lower_0618, '#.##') + st('  |  ' + pct(S_gg_base_bear) + ' baseline (Bilbo ' + pct(S_bilbo_lf) + '/' + pct(S_bilbo_lr) + ')') + '  |  scale out 50%+' if label_mode == 'Summary' else 'GOLDEN GATE TARGET  $' + string.tostring(lower_0618, '#.##') + '  (61.8% ATR)' + '\n' + 'The primary short-side target. Scale out at least half. Selling cascades end abruptly.' + '\n' + st('Bear baseline: ' + pct(S_gg_base_bear) + ' (n=3,196). With Bilbo at entry: Low+Falling ' + pct(S_bilbo_lf) + ', Low+Rising ' + pct(S_bilbo_lr) + '.' + '\n' + 'Bilbo? ' + pct(S_bilbo_786_bear) + ' reach 78.6% and ' + pct(S_bilbo_atr_bear) + ' reach -1 ATR. No Bilbo: ' + pct(S_base_786_bear) + ' to 78.6%.')
            prob_618_d = label.new(lab_x, lower_0618, gg_618_d_text, style=label.style_label_left, color=label_bg_color, textcolor=label_text_color, size=lbl_sz)

            atr1_d_text = 'FULL ATR  $' + string.tostring(lower_1000, '#.##') + st('  |  ' + pct(S_day_atr_bear) + ' of ALL days reach here') + '  |  take full profits' if label_mode == 'Summary' else 'FULL ATR  $' + string.tostring(lower_1000, '#.##') + '  (-1 ATR)' + '\n' + 'Rare territory.' + st(' ' + pct(S_day_atr_bear) + ' of all trading days reach the full downside ATR.') + '\n' + 'Take full profits. Selling cascades end without warning. A mean reversion back toward PDC is the next setup, not a continued short.'
            prob_atr1_d = label.new(lab_x, lower_1000, atr1_d_text, style=label.style_label_left, color=label_bg_color, textcolor=label_text_color, size=lbl_sz)

        if show_golden_gate_box:
            if long_active:
                gg_mid_bull = (upper_0382 + upper_0618) / 2
                gg_zone_label_u = label.new(lab_x, gg_mid_bull, 'THE GOLDEN GATE  (' + string.tostring(upper_0382, '#.##') + ' to ' + string.tostring(upper_0618, '#.##') + ')' + '\n' + st('Bull completion: ' + pct(S_l382_618_bull) + ' from 38.2%, ' + pct(S_gg_base_bull) + ' from the trigger day.' + '\n') + 'WHILE INSIDE: hold. The only stop is a confirmed close BELOW the call trigger.' + '\n' + 'EXITS TOP: scale out, trail to 38.2%.' + st(' ' + pct(S_l618_786_bull) + ' continue to 78.6%.') + '\n' + 'EXITS BOTTOM: if the trigger also breaks, the setup has failed -- exit.', style=label.style_label_right, color=color.new(color.green, 15), textcolor=color.white, size=size.small)

            if short_active:
                gg_mid_bear = (lower_0382 + lower_0618) / 2
                gg_zone_label_d = label.new(lab_x, gg_mid_bear, 'THE GOLDEN GATE  (' + string.tostring(lower_0382, '#.##') + ' to ' + string.tostring(lower_0618, '#.##') + ')' + '\n' + st('Bear completion: ' + pct(S_l382_618_bear) + ' from 38.2%, ' + pct(S_gg_base_bear) + ' from the trigger day.' + '\n') + 'WHILE INSIDE: hold. The only stop is a confirmed close ABOVE the put trigger.' + '\n' + 'EXITS BOTTOM: scale out, trail to 38.2%.' + st(' Bilbo entries: ' + pct(S_bilbo_atr_bear) + ' reach full ATR.') + '\n' + 'EXITS TOP: if the trigger also breaks, the setup has failed -- exit.', style=label.style_label_right, color=color.new(color.red, 15), textcolor=color.white, size=size.small)

        if show_target_stop:
            long_target = previous_close + tp_multiplier * atr
            short_target = previous_close - tp_multiplier * atr
            tp_name = string.tostring(tp_multiplier) + ' ATR (runner -- not the Gate target)'

            if long_active:
                targetLabel = label.new(lab_x, long_target, 'RUNNER TARGET\n$' + string.tostring(long_target, '#.##') + '\n' + tp_name, style=label.style_label_left, color=color.new(color.green, 0), textcolor=color.white, size=tp_label_size_val)
                stopLabel = label.new(lab_x, upper_trigger, 'STOP\n$' + string.tostring(upper_trigger, '#.##') + '\nconfirmed close below', style=label.style_label_left, color=color.new(color.red, 0), textcolor=color.white, size=tp_label_size_val)

            if short_active:
                targetLabel = label.new(lab_x, short_target, 'RUNNER TARGET\n$' + string.tostring(short_target, '#.##') + '\n' + tp_name, style=label.style_label_left, color=color.new(color.red, 0), textcolor=color.white, size=tp_label_size_val)
                stopLabel = label.new(lab_x, lower_trigger, 'STOP\n$' + string.tostring(lower_trigger, '#.##') + '\nconfirmed close above', style=label.style_label_left, color=color.new(color.green, 0), textcolor=color.white, size=tp_label_size_val)

    plotshape(show_pdc_reclaim and pdc_reclaim_bull, title='PDC Reclaim Bull', style=shape.triangleup, location=location.belowbar, color=color.new(c_up, 0), size=size.tiny, text='PDC', textcolor=color.white)
    plotshape(show_pdc_reclaim and pdc_reclaim_bear, title='PDC Reclaim Bear', style=shape.triangledown, location=location.abovebar, color=color.new(c_dn, 0), size=size.tiny, text='PDC', textcolor=color.white)

    plotshape(show_trigger_markers and entry_long_trigger, title='ENTER Long', style=shape.labelup, location=location.belowbar, color=color.new(c_up, 0), textcolor=color.black, size=size.tiny, text='ENTER')
    plotshape(show_trigger_markers and entry_short_trigger, title='ENTER Short', style=shape.labeldown, location=location.abovebar, color=color.new(c_dn, 0), textcolor=color.black, size=size.tiny, text='ENTER')

    plotshape(show_gg_markers and entry_long_gg, title='Gate Open Long', style=shape.diamond, location=location.belowbar, color=color.new(color.green, 0), textcolor=color.white, size=size.tiny, text='GG')
    plotshape(show_gg_markers and entry_short_gg, title='Gate Open Short', style=shape.diamond, location=location.abovebar, color=color.new(color.red, 0), textcolor=color.white, size=size.tiny, text='GG')

    plotshape(show_tpb_markers and entry_long_trigpb, title='T-PB Long', style=shape.triangleup, location=location.belowbar, color=color.new(color.aqua, 0), textcolor=color.black, size=size.tiny, text='T-PB')
    plotshape(show_tpb_markers and entry_short_trigpb, title='T-PB Short', style=shape.triangledown, location=location.abovebar, color=color.new(color.fuchsia, 0), textcolor=color.black, size=size.tiny, text='T-PB')

    plotshape(show_ema8_markers and entry_long_ema8, title='EMA8 Pullback Long', style=shape.circle, location=location.belowbar, color=color.new(color.lime, 0), textcolor=color.black, size=size.tiny, text='EMA8')
    plotshape(show_ema8_markers and entry_short_ema8, title='EMA8 Pullback Short', style=shape.circle, location=location.abovebar, color=color.new(color.orange, 0), textcolor=color.black, size=size.tiny, text='EMA8')

    plotshape(show_exit_markers and exit_long, title='EXIT Long', style=shape.xcross, location=location.abovebar, color=color.new(color.red, 0), textcolor=color.white, size=size.tiny, text='EXIT')
    plotshape(show_exit_markers and exit_short, title='EXIT Short', style=shape.xcross, location=location.belowbar, color=color.new(color.red, 0), textcolor=color.white, size=size.tiny, text='EXIT')

    alertcondition(entry_long_trigger and alert_long, title='ENTER Long (trigger)', message='ticker interval -- LONG entry. Confirmed close above the call trigger. Stop: a confirmed close back below it.')
    alertcondition(entry_short_trigger and alert_short, title='ENTER Short (trigger)', message='ticker interval -- SHORT entry. Confirmed close below the put trigger. Stop: a confirmed close back above it.')
    alertcondition(exit_long, title='EXIT Long', message='ticker interval -- EXIT LONG. Confirmed close back below the call trigger. The setup is invalidated.')
    alertcondition(exit_short, title='EXIT Short', message='ticker interval -- EXIT SHORT. Confirmed close back above the put trigger. The setup is invalidated.')
    alertcondition(entry_long_gg, title='Gate Open Long (38.2%)', message='ticker interval -- Bull Golden Gate open at 38.2%. Target 61.8%. Stop: a confirmed close below the trigger.')
    alertcondition(entry_short_gg, title='Gate Open Short (38.2%)', message='ticker interval -- Bear Golden Gate open at 38.2%. Target 61.8%. Stop: a confirmed close above the trigger.')
    alertcondition(entry_long_trigpb, title='T-PB Long (trigger pullback)', message='ticker interval -- Bull pullback to the trigger, with the Gate already open. Target 61.8%.')
    alertcondition(entry_short_trigpb, title='T-PB Short (trigger pullback)', message='ticker interval -- Bear pullback to the trigger, with the Gate already open. Target 61.8%.')
    alertcondition(entry_long_ema8, title='EMA8 Pullback Long', message='ticker interval -- Bull pullback to the 10-minute EMA8 inside the Gate. Target 61.8%.')
    alertcondition(entry_short_ema8, title='EMA8 Pullback Short', message='ticker interval -- Bear bounce to the 10-minute EMA8 inside the Gate. Target 61.8%.')
    alertcondition(signal_close and close > upper_0618 and (close[1] <= upper_0618), title='Gate Complete Long (61.8%)', message='ticker interval -- Bull Golden Gate complete at 61.8%. Scale out and trail to 38.2%.')
    alertcondition(signal_close and close < lower_0618 and (close[1] >= lower_0618), title='Gate Complete Short (61.8%)', message='ticker interval -- Bear Golden Gate complete at 61.8%. Scale out and trail to 38.2%.')
    alertcondition(pdc_reclaim_bull, title='PDC Reclaim Bull', message='ticker interval -- Previous close reclaimed from the bear box on a first-hour 10m close. Consider flipping long.')
    alertcondition(pdc_reclaim_bear, title='PDC Reclaim Bear', message='ticker interval -- Previous close lost from the bull box on a first-hour 10m close. Consider flipping short.')

    legend_pos = position.top_left if legend_position == 'Top Left' else position.top_right if legend_position == 'Top Right' else position.bottom_left if legend_position == 'Bottom Left' else position.bottom_right

    lg: Persistent[Table] = na(Table)
    lg_k = color.new(color.rgb(30, 40, 70), 0)
    lg_v = color.new(color.rgb(20, 25, 45), 0)

    def lg_row(r: int, k: str, v: str):
        table.cell(lg, 0, r, k, bgcolor=lg_k, text_color=color.new(color.silver, 10), text_size=size.tiny, text_halign=text.align_left)
        return table.cell(lg, 1, r, v, bgcolor=lg_v, text_color=color.white, text_size=size.tiny, text_halign=text.align_left)

    if not show_legend:
        if not na(lg):
            table.delete(lg)
            lg = na
    elif na(lg):
        lg = table.new(legend_pos, 2, 15, border_width=1, border_color=color.new(color.rgb(60, 80, 120), 30), frame_color=color.new(color.rgb(40, 60, 100), 10), frame_width=1)

    if barstate.islast and show_legend and (not na(lg)):
        table.cell(lg, 0, 0, 'HOW TO READ THIS', bgcolor=color.new(color.rgb(20, 35, 70), 0), text_color=color.white, text_size=size.tiny)
        table.cell(lg, 1, 0, 'Levels are the previous close ± a share of the ATR', bgcolor=color.new(color.rgb(20, 35, 70), 0), text_color=color.new(color.silver, 5), text_size=size.tiny)

        lg_row(1, 'Mode: ' + mode_short, 'The researched SPY/SPX configuration. Percentages shown only in that exact scope.' if p_milk else 'Same structure, any market. Percentages hidden -- they were never measured outside SPY.' if p_univ else 'Your own rules, set under Signal Rules.')
        lg_row(2, 'PDC', 'Previous period close. Every level is measured from it.')
        lg_row(3, 'Trigger', 'The entry gate at ' + trig_pct_txt + ' either side of PDC. A CONFIRMED close beyond it starts the trade. A wick does not count.')
        lg_row(4, '38.2%', 'The Golden Gate opens. First target, and the second-best place to enter.')
        lg_row(5, '50%', 'Midpoint. Never enter fresh here -- the risk/reward is negative. Hold if already in.')
        lg_row(6, '61.8%', 'THE GATE TARGET. The main objective. Scale out at least half.')
        lg_row(7, '78.6% / 1 ATR', 'Extension. Trail the stop, do not add. A full ATR move is rare.')
        lg_row(8, 'ENTER / EXIT', 'ENTER = confirmed close through the trigger. EXIT = confirmed close back through it. The exit is the edge.')
        lg_row(9, 'GG / T-PB / EMA8', 'Entry types: Gate open at 38.2%, pullback to the trigger (best odds), pullback to the 10-minute EMA8.')
        lg_row(10, 'Gold candle', 'The bar that opened the Golden Gate.')
        lg_row(11, 'BILBO', 'A 1-hour Phase Oscillator filter. In the outer zones the setup historically performed better.')
        lg_row(12, 'Percentages', 'Measured on SPY, 3-minute closes, regular hours, 2000-2025. Hidden on any other chart or mode.')
        lg_row(13, 'STATUS row', 'Always explains why no signal is showing -- gated off, blocked, degraded timeframe, or simply waiting.')
        lg_row(14, 'Swing trading', 'Outside Milkman mode, set Level Period to Swing or Position: the same structure built from monthly or quarterly ranges, useful on liquid tickers with a 4h or daily chart. Less reliable on thin small-cap crypto.')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
