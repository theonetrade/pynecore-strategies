"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barmerge, barstate, box, close,
    color, display, fill, format, high, hl2, input, label, low, math, na, plot, position, request,
    script, size, string, syminfo, ta, table, text, timeframe, volume, yloc
)
from pynecore.types import Box, Color, Label, Persistent, PersistentSeries, Table

GROUP_PRESET: str = "==== Quick Setup ======================="
GROUP_DISPLAY: str = "==== Dashboard & Display ============"
GROUP_ST: str = "==== Supertrend ======================="
GROUP_VOL: str = "==== Volume ==========================="
GROUP_FILTERS: str = "==== Quality Filters ================="
GROUP_PREDICTION: str = "==== Trend Duration Prediction====="
GROUP_GODMODE: str = "==== 🚀 GOD MODE ====================="
ribbonInfo: str = "Gradient Ribbon - Trend Strength Visualization\n\nColors based on Supertrend + Volume:\n\n🟢 GREEN = Bullish + Volume Spike (strongest)\n🔵 BLUE = Bullish + High Volume\n🟠 ORANGE = Bearish + High Volume\n🔴 RED = Bearish (weakest)\n\n26 exponential layers for smooth appearance."
labelEntryInfo: str = "Entry Signal Labels\n\nShows 🔪 BUY and 🔪 SELL signals on chart.\n\nIncludes:\n• Volume status\n• Volume Momentum\n• Quality score\n\nThese are your main trading signals."
labelInfoInfo: str = "Informative Labels\n\nShows additional market events:\n\n💥 Volume Spike\n• Significant volume increase\n• Cooldown: 8 bars\n\nThese provide context, not entry signals."
labelSizeInfo: str = "Label Size\n\nControls text size for ALL labels:\n• Entry signals (BUY/SELL)\n• Volume spikes\n\nRecommended:\n• Small charts: Small\n• Normal charts: Normal (default)\n• Large charts: Large"
stInfo: str = "Supertrend Settings - Optimized for All Trading Styles\n\nATR-based trend indicator:\n• Adapts to volatility automatically\n• Provides clear trend direction\n• Built-in stop levels\n\nOptimal by style:\n• Scalping: ATR 7-10, Mult 1.8-2.2\n• Day Trading: ATR 10-14, Mult 2.2-2.8\n• Swing Trading: ATR 14-21, Mult 2.8-3.5\n• Position Trading: ATR 21-30, Mult 3.5-4.5\n\nTighter = more signals, Wider = stronger signals"
volMomInfo: str = "Volume Momentum Confirmation - All Trading Styles\n\nCompares short-term vs long-term volume averages:\n• Confirms trend strength with actual money flow\n• Rising momentum = Recent volume > Historical average\n• No lag like price-based indicators\n• More intuitive than mathematical filters\n\nOptimal periods by style:\n• Scalping: 3 vs 10 (instant response)\n• Day Trading: 5 vs 20 (balanced)\n• Swing Trading: 10 vs 30 (trend stability)\n• Position Trading: 20 vs 50 (major moves)\n\n⚠️ AUTO-DISABLED for Scalping mode (too restrictive)\n\nON = Fewer but volume-confirmed signals\nOFF = All Supertrend signals (no filter)"
volInfo: str = "Volume Analysis - Critical for All Trading Styles\n\nThresholds are multipliers of average volume:\n\n🔥 HIGH = Strong participation\n💥 SPIKE = Major event/breakout\n📍 LOW = Weak participation\n\nOptimal by style:\n• Scalping: High 1.5-2.0x, Spike 2.5-3.5x\n• Day Trading: High 1.3-1.7x, Spike 2.2-3.0x\n• Swing Trading: High 1.2-1.5x, Spike 2.0-2.7x\n• Position Trading: High 1.1-1.3x, Spike 1.8-2.3x\n\nVolume confirmation improves signal quality."
filterInfo: str = "Signal Quality Filtering\n\nQuality Score (0-70) based on:\n• Volume (30 points)\n• Volatility Expansion (30 points)\n• Volume Momentum (10 points)\n\nRecommended minimums:\n• 30 = GOOD+ (balanced)\n• 45 = STRONG+ (conservative)\n• 60 = EXCELLENT (very strict)"
scalpelInfo: str = "🔪 Scalpel Mode - Pullback Entry System\n\nInstead of entering on SuperTrend flip bar:\n• Wait 2-5 bars for pullback\n• Enter when price bounces off ATR pullback level\n• Require strong volume momentum\n• Need volume spike/high\n• Must have good distance from ST\n\nAPPROACH:\n✓ More selective entries\n✓ Improved risk/reward potential\n✓ Focus on quality over quantity\n✓ Better alignment with money flow\n\nBased on:\n• Mark Minervini VCP pullbacks\n• William O'Neil volume confirmation\n• Dan Zanger volatility expansion"
predictionModeInfo: str = "Prediction Mode 🎯\n\nChoose your prediction complexity level:\n\n📊 SIMPLE:\n• Basic median-based predictions only\n• No advanced multipliers\n• Easiest to understand\n• Best for beginners\n\n⚙️ STANDARD (Recommended):\n• Full statistical analysis\n• All quality calculations\n• NO advanced multipliers\n• Balanced accuracy & simplicity\n\n🚀 ADVANCED:\n• Everything from Standard\n• PLUS 5 intelligent multipliers:\n  - Market Structure (±30%)\n  - Stock Type Behavior (±40%)\n  - Flip Strength (±20%)\n  - Error Learning (±15%)\n  - Regime Detection (±20%)\n• Highest accuracy (30-50% improvement)\n• Most complex\n\n💡 Recommendation:\n• Start with Standard\n• Move to Advanced after understanding basics"
stockTypeInfo: str = "Stock Type Classification\n\nDifferent assets have unique trend behaviors:\n\n📊 Small Cap (0.65x) - Shortest trends\n• High volatility, quick reversals\n• Best for: Penny stocks, micro-caps\n\n🧬 Biotech/Spec (0.55x) - Most volatile\n• News-driven, sharp moves\n• Best for: Biotech, pharma, speculative\n\n🏛️ Blue Chip (1.35x) - Longest trends\n• Stable, institutional\n• Best for: Large caps, indices\n\n🚀 Tech Growth (1.10x) - Extended trends\n• Growth stocks, momentum\n\n💰 Dividend (1.25x) - Stable trends\n• Value stocks, utilities\n\n🔄 Cyclical (0.90x) - Moderate trends\n• Sector rotation sensitive\n\n⚡ Crypto/High Vol (0.60x) - Extreme volatility\n• 24/7 markets, rapid changes"
ewaInfo: str = "Exponential Weighted Average (EWA)\n\nGives more weight to recent trends vs older trends.\n\nBENEFITS:\n✅ More responsive to changing market conditions\n✅ Recent trends more relevant to current behavior\n✅ Adapts faster to regime changes\n\nDECAY FACTOR:\n• 0.95 = Slight preference to recent (balanced)\n• 0.90 = Moderate preference (recommended)\n• 0.80 = Strong preference (very adaptive)\n• 0.50 = Extreme preference (only recent matters)\n\nExample with 0.9:\n• Last trend: 100% weight\n• 2nd last: 90% weight\n• 3rd last: 81% weight\n• etc.\n\nDisable for equal weighting of all 15 trends."
structureInfo: str = "Market Structure Detection\n\nAnalyzes pivot highs/lows to identify key S/R levels.\n\nLOOKBACK PERIOD:\n• Bars left and right to confirm a pivot\n• Higher = stronger but fewer levels\n• Lower = more levels but less significant\n\nRecommended:\n• Scalping: 3-5 (recent levels)\n• Day Trading: 5-7 (intraday levels)\n• Swing: 10-15 (major levels)\n• Position: 20-30 (key levels)\n\nSENSITIVITY:\n• % of ATR to consider price \"near\" a level\n• 50% = within half ATR of level\n• 100% = within 1 full ATR\n\nAdjustment: Trends near levels get -30% duration"
errorLearningInfo: str = "Error Learning System\n\nAdaptively learns from prediction mistakes:\n\n• Tracks last N predictions vs actual durations\n• Calculates error ratio (predicted / actual)\n• Adjusts future predictions accordingly\n\nMEMORY DEPTH:\n• How many past predictions to remember\n• Higher = more stable, slower adaptation\n• Lower = faster learning, more reactive\n\nRecommended:\n• 5 = Fast adaptation\n• 10 = Balanced (default)\n• 20 = Very stable\n\nExample:\n• If consistently over-predicting by 20%\n• System learns and reduces future predictions\n\nBenefits:\n✅ Self-correcting\n✅ Adapts to changing market regimes\n✅ Improves over time"
godModeInfo: str = "🚀 GOD MODE — Master Switch\n\nAdds a value layer on top of the classic engine:\n• MTF Confluence (higher-timeframe SuperTrend agreement)\n• SL / TP levels on every signal\n• Optional signal gating by higher-TF agreement\n\nOFF = the classic indicator, unchanged (zero behavior change).\nON  = full GOD MODE."
VOL_SPIKE_COOLDOWN: int = 8


@script.indicator("Luxy Super-Duper SuperTrend Predictor Engine", shorttitle="Luxy SuperDuperTrend", overlay=True, max_boxes_count=500, max_bars_back=5000)
def main(
    trading_style=input.string("Auto (Detect from TF)", "Trading Style Preset", options=("Auto (Detect from TF)", "Scalping (1-5m)", "Day Trading (15m-1h)", "Swing Trading (4h-D)", "Position Trading (D-W)", "Custom"), group=GROUP_PRESET, tooltip="🎯 Trading Style Configuration\n\n🤖 AUTO (DETECT FROM TF) - RECOMMENDED ✅\nAutomatically selects optimal settings based on your chart timeframe:\n• 1m-5m → Scalping (ATR: 7, Mult: 2.0)\n• 15m-1h → Day Trading (ATR: 10, Mult: 2.5)\n• 2h-4h-D → Swing Trading (ATR: 14, Mult: 3.0)\n• W-M → Position Trading (ATR: 21, Mult: 4.0)\n\nBenefits:\n✅ Zero configuration - works immediately\n✅ Always matched to your timeframe\n✅ Switch TF = automatic adjustment\n\n📊 MANUAL PRESETS:\n📈 Scalping (1-5m): Ultra-fast signals, high sensitivity\n⚡ Day Trading (15m-1h): Balanced speed and accuracy\n🔄 Swing Trading (4h-D): Medium-term trends, less noise\n📊 Position Trading (D-W): Long-term trends, minimal false signals\n\n🛠️ CUSTOM MODE:\nFull manual control - uses YOUR input values below\nFor advanced users who want precise customization\n\n⚠️ NOTE: Presets override manual inputs. For custom values, select 'Custom'."),
    show_dashboard=input.bool(True, "Show Dashboard", group=GROUP_DISPLAY, tooltip="Show/Hide Dashboard Table\n\nDisplays real-time metrics:\n• Signal Quality Score (0-70)\n• Supertrend direction & level\n• Volume state & ratio\n• Volatility regime\n• Prediction track record\n\nAll metrics update on each bar close.\n\n💡 Disable to reduce chart clutter"),
    table_position=input.string("Bottom Right", "Position", options=("Top Left", "Top Center", "Top Right", "Middle Left", "Middle Center", "Middle Right", "Bottom Left", "Bottom Center", "Bottom Right"), group=GROUP_DISPLAY, inline="table_settings", tooltip="Dashboard Position\n\nChoose where to display the dashboard table on your chart.\n\n9 positions available:\n• Top: Left, Center, Right\n• Middle: Left, Center, Right\n• Bottom: Left, Center, Right\n\n💡 Choose a position that doesn't overlap important price action"),
    table_text_size=input.string("Small", "Text Size", options=("Auto", "Tiny", "Small", "Normal", "Large", "Huge"), group=GROUP_DISPLAY, inline="table_settings", tooltip="Dashboard Text Size\n\nControls the size of text in the dashboard table.\n\nOptions:\n• Auto - Adapts to chart size\n• Tiny - Smallest (minimal space)\n• Small - Compact (recommended)\n• Normal - Standard readability\n• Large - Easy to read\n• Huge - Maximum visibility\n\n💡 Use smaller sizes on busy charts"),
    show_ribbon_fill=input.bool(True, "Show Ribbon Fill", group=GROUP_DISPLAY, tooltip="Toggles the visibility of the gradient background fill for the SuperTrend ribbon.", inline="ribbon_viz"),
    show_supertrend_line=input.bool(True, "Show SuperTrend Line", group=GROUP_DISPLAY, tooltip="Toggles the visibility of the main SuperTrend line.", inline="ribbon_viz"),
    bull_color_input=input.color(color.green, "Bullish Color", group=GROUP_DISPLAY, inline="ribbon_colors", tooltip="Bullish Trend Color\n\nSets the color for:\n• Supertrend line (when bullish)\n• Gradient ribbon fill (when bullish)\n• BUY signal labels\n\nDefault: Green\n\n💡 Choose colors that match your chart theme"),
    bear_color_input=input.color(color.red, "Bearish Color", group=GROUP_DISPLAY, inline="ribbon_colors", tooltip="Bearish Trend Color\n\nSets the color for:\n• Supertrend line (when bearish)\n• Gradient ribbon fill (when bearish)\n• SELL signal labels\n\nDefault: Red\n\n💡 Choose colors that match your chart theme"),
    show_entry_labels=input.bool(True, "Show Entry Signals (BUY/SELL)", group=GROUP_DISPLAY, tooltip=labelEntryInfo),
    show_info_labels=input.bool(False, "Show Info Labels (Volume)", group=GROUP_DISPLAY, tooltip=labelInfoInfo),
    label_text_size=input.string("Normal", "Label Size (All)", options=("Auto", "Tiny", "Small", "Normal", "Large", "Huge"), group=GROUP_DISPLAY, tooltip=labelSizeInfo),
    st_length_input=input.int(10, "ATR Length", minval=1, maxval=50, group=GROUP_ST, inline="st1", tooltip=stInfo),
    st_mult_input=input.float(3.0, "ATR Multiplier (Base)", minval=0.5, step=0.5, group=GROUP_ST, inline="st1"),
    st_use_adaptive=input.bool(True, "Use Adaptive Multiplier", group=GROUP_ST, inline="adapt", tooltip="Adaptive Multiplier System\n\nDynamically adjusts multiplier (0.8x to 1.2x base) based on:\n• Trend Strength (price correlation)\n• Volume Weight (relative to average)\n\nBenefits:\n✅ Tighter bands in calm markets\n✅ Wider bands in volatile conditions\n✅ Better for biotech/small-cap stocks\n\nDisable for classic constant multiplier."),
    st_smooth_factor=input.float(0.15, "Smoothing Factor", minval=0.0, maxval=0.5, step=0.05, group=GROUP_ST, inline="adapt", tooltip="EMA smoothing applied to Supertrend bands\n\n0.0 = no smoothing (instant response)\n0.15 = balanced (~13 bars)\n0.3+ = very smooth (slow response)\n\n💡 Volume Momentum filter compensates for lag"),
    st_neutral_bars=input.int(0, "Neutral Bars After Flip", minval=0, maxval=10, group=GROUP_ST, tooltip="Neutral Bars After Flip\n\nHide Supertrend for X bars after trend flip.\n\nBenefits:\n✅ Reduces false signals immediately after flip\n✅ Gives price time to confirm new direction\n✅ Cleaner visual on choppy markets\n\nRecommended:\n• 0 = disabled (classic behavior)\n• 2-3 = balanced (swing trading)\n• 5+ = very conservative"),
    volume_momentum_enabled=input.bool(True, "Enable Volume Momentum Filter", group=GROUP_ST, inline="volmom1", tooltip=volMomInfo),
    vol_mom_fast_input=input.int(5, "Fast Period", minval=2, maxval=20, group=GROUP_ST, inline="volmom1"),
    vol_mom_slow_input=input.int(20, "Slow Period", minval=10, maxval=50, group=GROUP_ST, inline="volmom1", tooltip="Volume Momentum Slow Period\n\nHistorical volume average for comparison.\n\nRepresents:\n• Long-term baseline volume\n• Historical average activity\n\nTypical values:\n• Scalping: 10 bars (recent baseline)\n• Day Trading: 20 bars (daily baseline) - DEFAULT\n• Swing: 30 bars (weekly baseline)\n• Position: 50 bars (monthly baseline)\n\nMust be larger than Fast Period.\n\n💡 Larger values = more stable baseline, less noise"),
    vol_length_input=input.int(20, "Volume MA Length", minval=5, maxval=100, group=GROUP_VOL, inline="vol1", tooltip=volInfo),
    vol_high_threshold_input=input.float(1.5, "High Volume (x)", minval=1.0, step=0.1, group=GROUP_VOL, inline="vol2"),
    vol_spike_threshold_input=input.float(2.5, "Spike Volume (x)", minval=1.5, step=0.5, group=GROUP_VOL, inline="vol2"),
    vol_low_threshold=input.float(0.5, "Low Volume (x)", minval=0.1, maxval=1.0, step=0.1, group=GROUP_VOL, inline="vol3", tooltip="Low Volume Threshold\n\nDefines when volume is considered LOW (weak participation).\n\nMeasured as multiplier of average volume:\n• 0.5x = Current volume is 50% of average\n• 0.7x = Current volume is 70% of average\n\nLow volume signals:\n⚠️ Weak trend confirmation\n⚠️ Lower quality setups\n⚠️ May indicate trend exhaustion\n\nDefault: 0.5x\n\n💡 Lower values = stricter definition of low volume"),
    min_quality_score=input.int(30, "Minimum Quality Score", minval=0, maxval=70, group=GROUP_FILTERS, tooltip=filterInfo),
    require_volume_confirm=input.bool(True, "Require Volume Confirmation", group=GROUP_FILTERS, tooltip="Only generate signals when volume > average"),
    use_scalpel=input.bool(False, "🔪 Scalpel Mode", group=GROUP_FILTERS, tooltip=scalpelInfo),
    scalpel_window=input.int(5, "Pullback Window", minval=2, maxval=10, group=GROUP_FILTERS, inline="scalpel1", tooltip="Bars to wait for pullback entry after flip"),
    scalpel_min_dist=input.float(0.4, "Min Distance (xATR)", minval=0.2, maxval=1.0, step=0.1, group=GROUP_FILTERS, inline="scalpel1", tooltip="Minimum Distance from SuperTrend\n\nEnsures entry has sufficient distance from SuperTrend level for better risk/reward.\n\nMeasured in ATR multiples:\n• 0.2 = Very tight (20% of ATR)\n• 0.4 = Balanced (40% of ATR) - DEFAULT\n• 0.6 = Conservative (60% of ATR)\n• 1.0 = Very conservative (full ATR)\n\nHigher values:\n✅ Better risk/reward ratio\n✅ More room for stop placement\n❌ Fewer signals\n\nLower values:\n✅ More signals\n❌ Tighter stops needed\n\n💡 Use higher values (0.6-1.0) for volatile markets"),
    scalpel_quality=input.int(55, "Scalpel Quality Min", minval=50, maxval=90, group=GROUP_FILTERS, tooltip="Quality threshold for Scalpel Mode (higher = stricter)\n\nMax possible score is 70. Default 55 keeps entries selective while still firing; 65+ almost never triggers (needs volume spike + expanding volatility + strong momentum together)."),
    i_enable_prediction=input.bool(True, "Show Trend Duration Prediction", group=GROUP_PREDICTION, tooltip="Display prediction box showing expected trend duration based on historical SuperTrend analysis. Analyzes last 15 trends to predict current trend lifespan."),
    i_prediction_mode=input.string("Advanced", "Prediction Mode", options=("Simple", "Standard", "Advanced"), group=GROUP_PREDICTION, tooltip=predictionModeInfo),
    i_stock_type=input.string("Blue Chip / Large Cap", "Asset Type", options=("Small Cap", "Biotech / Speculative", "Blue Chip / Large Cap", "Tech Growth", "Dividend / Value", "Cyclical", "Crypto / High Volatility"), group=GROUP_PREDICTION, tooltip=stockTypeInfo),
    i_use_ewa=input.bool(True, "Use Exponential Weighting", group=GROUP_PREDICTION, inline="ewa1", tooltip=ewaInfo),
    i_ewa_decay=input.float(0.9, "Decay Factor", minval=0.5, maxval=0.99, step=0.05, group=GROUP_PREDICTION, inline="ewa1"),
    i_outlier_filter=input.bool(True, "Filter Extreme Values", group=GROUP_PREDICTION, tooltip="Outlier Filtering (IQR Method)\n\nRemoves extreme trend durations that could skew predictions.\n\nUses Interquartile Range (IQR):\n• Calculates Q1 (25th percentile) and Q3 (75th percentile)\n• Filters values outside Q1-2×IQR to Q3+2×IQR\n• Keeps at least 60% of data for reliability\n\nBenefits:\n✅ More stable predictions\n✅ Reduces impact of anomalies\n✅ Better accuracy in normal conditions\n\nDisable if:\n❌ You have very few samples (<10)\n❌ You want to include all historical data\n\nRecommended: ON (default)"),
    i_use_median=input.bool(True, "Use Median (more stable)", group=GROUP_PREDICTION, tooltip="Use Median for Central Tendency\n\nChooses between median vs mean for predictions.\n\nMEDIAN (Recommended):\n✅ More robust to outliers\n✅ Represents typical trend duration\n✅ Better for skewed distributions\n✅ Stable with small sample sizes\n\nMEAN (Alternative):\n• Considers all data points equally\n• Sensitive to extreme values\n• Good for symmetric distributions\n\nThe indicator blends both (60% median + 40% trimmed mean) for optimal robustness.\n\nRecommended: ON (default)"),
    i_structure_lookback=input.int(10, "Structure Lookback", minval=3, maxval=30, group=GROUP_PREDICTION, inline="struct1", tooltip=structureInfo),
    i_structure_sensitivity=input.float(0.5, "Proximity (xATR)", minval=0.2, maxval=1.0, step=0.1, group=GROUP_PREDICTION, inline="struct1"),
    i_use_error_learning=input.bool(True, "Enable Error Learning", group=GROUP_PREDICTION, inline="learn1", tooltip=errorLearningInfo),
    i_error_memory_depth=input.int(10, "Memory Depth", minval=3, maxval=20, group=GROUP_PREDICTION, inline="learn1"),
    godmode_enabled=input.bool(True, "🚀 Enable GOD MODE", group=GROUP_GODMODE, tooltip=godModeInfo),
    htf1_tf=input.timeframe("60", "Higher TF 1", group=GROUP_GODMODE, inline="gm_mtf", tooltip="Higher timeframes for confluence.\n\n⚠️ Set BOTH above your chart timeframe (e.g. on a 15m chart use 60 + 240).\nThe higher-TF SuperTrend direction is compared to the current chart for conviction."),
    htf2_tf=input.timeframe("240", "Higher TF 2", group=GROUP_GODMODE, inline="gm_mtf"),
    mtf_gate_signals=input.bool(False, "MTF: Only Signal When Higher TFs Agree", group=GROUP_GODMODE, tooltip="ON = a BUY needs BOTH higher TFs bullish (SELL needs both bearish). Fewer but higher-conviction signals.\nOFF = higher-TF info shown for context only; signals unchanged."),
    show_risk_levels=input.bool(True, "Show SL / TP on Signals", group=GROUP_GODMODE, tooltip="Adds a Stop (at the SuperTrend line) and two R-multiple Take-Profit targets to every BUY/SELL tooltip."),
    tp1_r=input.float(2.0, "TP1 (x R)", minval=0.5, maxval=10.0, step=0.5, group=GROUP_GODMODE, inline="gm_tp"),
    tp2_r=input.float(3.5, "TP2 (x R)", minval=0.5, maxval=10.0, step=0.5, group=GROUP_GODMODE, inline="gm_tp")
):
    def detect_trading_style():
        result: str = "Day Trading (15m-1h)"

        if timeframe.isminutes:
            mins: int = timeframe.multiplier
            result = 'Scalping (1-5m)' if mins <= 5 else 'Day Trading (15m-1h)'
        elif timeframe.isintraday:
            hours: int = timeframe.multiplier
            result = 'Day Trading (15m-1h)' if hours <= 1 else 'Swing Trading (4h-D)'
        elif timeframe.isdaily:
            result = "Swing Trading (4h-D)"
        elif timeframe.isweekly or timeframe.ismonthly:
            result = "Position Trading (D-W)"

        return result

    actual_style = detect_trading_style() if trading_style == 'Auto (Detect from TF)' else trading_style


    label_size_const = size.auto if label_text_size == 'Auto' else size.tiny if label_text_size == 'Tiny' else size.small if label_text_size == 'Small' else size.normal if label_text_size == 'Normal' else size.large if label_text_size == 'Large' else size.huge

    st_length = st_length_input if actual_style == 'Custom' else 7 if actual_style == 'Scalping (1-5m)' else 10 if actual_style == 'Day Trading (15m-1h)' else 14 if actual_style == 'Swing Trading (4h-D)' else 21 if actual_style == 'Position Trading (D-W)' else st_length_input
    st_mult = st_mult_input if actual_style == 'Custom' else 2.0 if actual_style == 'Scalping (1-5m)' else 2.5 if actual_style == 'Day Trading (15m-1h)' else 3.0 if actual_style == 'Swing Trading (4h-D)' else 4.0 if actual_style == 'Position Trading (D-W)' else st_mult_input

    use_volume_momentum = False if actual_style == 'Scalping (1-5m)' else volume_momentum_enabled
    vol_mom_fast = vol_mom_fast_input if actual_style == 'Custom' else 3 if actual_style == 'Scalping (1-5m)' else 5 if actual_style == 'Day Trading (15m-1h)' else 10 if actual_style == 'Swing Trading (4h-D)' else 20 if actual_style == 'Position Trading (D-W)' else vol_mom_fast_input
    vol_mom_slow = vol_mom_slow_input if actual_style == 'Custom' else 10 if actual_style == 'Scalping (1-5m)' else 20 if actual_style == 'Day Trading (15m-1h)' else 30 if actual_style == 'Swing Trading (4h-D)' else 50 if actual_style == 'Position Trading (D-W)' else vol_mom_slow_input

    vol_length = vol_length_input if actual_style == 'Custom' else 10 if actual_style == 'Scalping (1-5m)' else 20 if actual_style == 'Day Trading (15m-1h)' else 30 if actual_style == 'Swing Trading (4h-D)' else 50 if actual_style == 'Position Trading (D-W)' else vol_length_input
    vol_high_threshold = vol_high_threshold_input if actual_style == 'Custom' else 1.8 if actual_style == 'Scalping (1-5m)' else 1.5 if actual_style == 'Day Trading (15m-1h)' else 1.3 if actual_style == 'Swing Trading (4h-D)' else 1.2 if actual_style == 'Position Trading (D-W)' else vol_high_threshold_input
    vol_spike_threshold = vol_spike_threshold_input if actual_style == 'Custom' else 3.0 if actual_style == 'Scalping (1-5m)' else 2.5 if actual_style == 'Day Trading (15m-1h)' else 2.2 if actual_style == 'Swing Trading (4h-D)' else 2.0 if actual_style == 'Position Trading (D-W)' else vol_spike_threshold_input



    tr = ta.tr
    atrS = ta.atr(st_length)

    volWeight: float = volume / ta.sma(volume, st_length)
    volWeight = 1.0 if na(volWeight) else volWeight

    trendStrength: float = math.abs(ta.correlation(close, bar_index, st_length))
    trendStrength = 0.5 if na(trendStrength) else trendStrength

    adaptiveMult: float = st_mult * (0.8 + trendStrength * 0.4) * math.sqrt(math.max(0.1, volWeight)) if st_use_adaptive else st_mult

    upLine: PersistentSeries[float] = na(float)
    dnLine: PersistentSeries[float] = na(float)

    upRaw: float = hl2 - atrS * adaptiveMult
    dnRaw: float = hl2 + atrS * adaptiveMult

    if na(upLine[1]):
        upLine = upRaw
        dnLine = dnRaw
    else:
        upLine = upLine[1] * (1 - st_smooth_factor) + upRaw * st_smooth_factor if close > upLine[1] else upRaw
        dnLine = dnLine[1] * (1 - st_smooth_factor) + dnRaw * st_smooth_factor if close < dnLine[1] else dnRaw

    stDir: PersistentSeries[int] = na(int)
    stDir = (1 if close >= hl2 else -1) if na(stDir[1]) else stDir[1]
    stDir = 1 if stDir == -1 and close > dnLine[1] else -1 if stDir == 1 and close < upLine[1] else stDir

    stFlip: bool = stDir != stDir[1]

    neutral: bool = False
    if st_neutral_bars > 0:
        barsSinceFlip: int = ta.barssince(stFlip)
        neutral = barsSinceFlip >= 0 and barsSinceFlip < st_neutral_bars

    supertrend: float = upLine if stDir == 1 else dnLine
    direction: int = stDir

    is_bullish = stDir == 1
    is_bearish = stDir == -1

    supertrend_flip_bullish = stFlip and stDir == 1
    supertrend_flip_bearish = stFlip and stDir == -1

    st_line_color = bull_color_input if is_bullish else bear_color_input
    show_line: bool = show_supertrend_line and (not neutral) and (not stFlip)
    plot(supertrend if show_line else na, 'SuperTrend Line', color=st_line_color, linewidth=2)

    def st_dir_htf():
        _line, _dir = ta.supertrend(st_mult, st_length)
        return _dir

    htf1_dir = request.security(syminfo.tickerid, htf1_tf, st_dir_htf(), lookahead=barmerge.lookahead_off)
    htf2_dir = request.security(syminfo.tickerid, htf2_tf, st_dir_htf(), lookahead=barmerge.lookahead_off)

    htf1_bull: bool = htf1_dir < 0
    htf2_bull: bool = htf2_dir < 0
    mtf_bull_count: int = (1 if htf1_bull else 0) + (1 if htf2_bull else 0)
    mtf_agree_count: int = (0 if na(htf1_dir) else 1 if is_bullish == htf1_bull else 0) + (0 if na(htf2_dir) else 1 if is_bullish == htf2_bull else 0)

    vol_ma_fast = ta.sma(volume, vol_mom_fast)
    vol_ma_slow = ta.sma(volume, vol_mom_slow)
    vol_momentum_ratio = vol_ma_fast / vol_ma_slow

    vol_momentum_rising = vol_momentum_ratio > 1.0
    vol_momentum_strong = vol_momentum_ratio > 1.2
    vol_momentum_weak = vol_momentum_ratio < 0.8
    vol_momentum_neutral = vol_momentum_ratio >= 0.8 and vol_momentum_ratio <= 1.0

    vol_momentum_confirms_bull = is_bullish and vol_momentum_rising
    vol_momentum_confirms_bear = is_bearish and vol_momentum_rising
    vol_momentum_strong_trend = is_bullish and vol_momentum_strong or (is_bearish and vol_momentum_strong)

    vol_ma = ta.sma(volume, vol_length)

    vol_ratio = volume / vol_ma

    vol_is_spike = vol_ratio >= vol_spike_threshold
    vol_is_high = vol_ratio >= vol_high_threshold
    vol_is_low = vol_ratio <= vol_low_threshold
    vol_is_normal = not vol_is_spike and (not vol_is_high) and (not vol_is_low)

    vol_state = '💥 SPIKE' if vol_is_spike else '🔥 HIGH' if vol_is_high else '📍 LOW' if vol_is_low else '➡️ NORMAL'

    strong_volume_confirm = vol_is_spike or vol_is_high
    basic_volume_confirm = vol_ratio >= 1.0

    atr_current = ta.atr(14)
    atr_ma = ta.sma(atr_current, 20)
    atr_ratio = atr_current / atr_ma

    vol_expanding = atr_ratio >= 1.3
    vol_rising = atr_ratio >= 1.0 and atr_ratio < 1.3
    vol_contracting = atr_ratio <= 0.9
    vol_stable = atr_ratio > 0.9 and atr_ratio < 1.0

    volatility_state = '🔥 EXPANDING' if atr_ratio >= 1.3 else '📈 RISING' if vol_rising else '📉 CONTRACTING' if vol_contracting else '➡️ STABLE'

    quality_score: Persistent[int] = 0

    quality_score = (30 if vol_is_spike else 20 if vol_is_high else 10 if basic_volume_confirm else 0) + (30 if vol_expanding else 15 if vol_rising else 0) + (10 if use_volume_momentum and vol_momentum_strong_trend else 5 if use_volume_momentum and vol_momentum_rising else 0)

    quality_level = '⭐⭐⭐ EXCELLENT' if quality_score >= 60 else '⭐⭐ STRONG' if quality_score >= 45 else '⭐ GOOD' if quality_score >= 30 else '⚠️ WEAK'

    supertrend_long = supertrend_flip_bullish
    supertrend_short = supertrend_flip_bearish

    signal_quality_ok = quality_score >= min_quality_score

    volume_ok = not require_volume_confirm or basic_volume_confirm

    vol_momentum_ok_long = not use_volume_momentum or vol_momentum_confirms_bull
    vol_momentum_ok_short = not use_volume_momentum or vol_momentum_confirms_bear

    classic_long: bool = supertrend_long and signal_quality_ok and volume_ok and vol_momentum_ok_long
    classic_short: bool = supertrend_short and signal_quality_ok and volume_ok and vol_momentum_ok_short

    bars_since_bull_flip: Persistent[int] = 999
    bars_since_bear_flip: Persistent[int] = 999

    signal_given_in_bull_window: Persistent[bool] = False
    signal_given_in_bear_window: Persistent[bool] = False

    if supertrend_flip_bullish:
        bars_since_bull_flip = 0
        signal_given_in_bull_window = False
    elif bars_since_bull_flip < 999:
        bars_since_bull_flip += 1

    if supertrend_flip_bearish:
        bars_since_bear_flip = 0
        signal_given_in_bear_window = False
    elif bars_since_bear_flip < 999:
        bars_since_bear_flip += 1

    in_bull_window: bool = bars_since_bull_flip > 0 and bars_since_bull_flip <= scalpel_window
    in_bear_window: bool = bars_since_bear_flip > 0 and bars_since_bear_flip <= scalpel_window

    pullback_level_long: float = supertrend + atrS * 0.5 if is_bullish else na
    pullback_level_short: float = supertrend - atrS * 0.5 if is_bearish else na

    bounce_long: bool = ta.crossover(close, pullback_level_long)
    scalpel_long_conditions: bool = in_bull_window and is_bullish and bounce_long and vol_momentum_rising and (close - supertrend >= atr_current * scalpel_min_dist) and basic_volume_confirm and (quality_score >= scalpel_quality)
    scalpel_long: bool = scalpel_long_conditions and (not signal_given_in_bull_window)

    bounce_short: bool = ta.crossunder(close, pullback_level_short)
    scalpel_short_conditions: bool = in_bear_window and is_bearish and bounce_short and vol_momentum_rising and (supertrend - close >= atr_current * scalpel_min_dist) and basic_volume_confirm and (quality_score >= scalpel_quality)
    scalpel_short: bool = scalpel_short_conditions and (not signal_given_in_bear_window)

    if scalpel_long:
        signal_given_in_bull_window = True

    if scalpel_short:
        signal_given_in_bear_window = True

    mtf_long_ok: bool = not (godmode_enabled and mtf_gate_signals) or mtf_bull_count == 2
    mtf_short_ok: bool = not (godmode_enabled and mtf_gate_signals) or mtf_bull_count == 0
    goldenCross = (scalpel_long if use_scalpel else classic_long) and mtf_long_ok
    deathCross = (scalpel_short if use_scalpel else classic_short) and mtf_short_ok

    lastSignalType: Persistent[str] = na(str)
    lastSignalPrice: Persistent[float] = na(float)
    lastSignalBarIndex: Persistent[int] = na(int)

    if goldenCross:
        lastSignalType = "LONG"
        lastSignalPrice = close
        lastSignalBarIndex = bar_index

    if deathCross:
        lastSignalType = "SHORT"
        lastSignalPrice = close
        lastSignalBarIndex = bar_index

    PREDICTION_SAMPLES: int = 50
    BOX_COUNT: int = 30

    bull_trend_durations: Persistent[list[int]] = array.new_int(0)
    bear_trend_durations: Persistent[list[int]] = array.new_int(0)
    current_trend_bars: Persistent[int] = 0
    flip_bar_index: Persistent[int] = 0
    flip_supertrend_level: Persistent[float] = supertrend

    all_trend_durations: Persistent[list[int]] = array.new_int(0)
    all_trend_is_bullish: Persistent[list[bool]] = array.new_bool(0)

    prediction_boxes: Persistent[list[Box]] = array.new_box(0)
    prediction_labels: Persistent[list[Label]] = array.new_label(0)

    prediction_box_counts: Persistent[list[int]] = array.new_int(0)
    prediction_label_counts: Persistent[list[int]] = array.new_int(0)
    prediction_set_is_bullish: Persistent[list[bool]] = array.new_bool(0)

    last_10_predicted_avg: Persistent[list[float]] = array.new_float(0)
    last_10_predicted_end: Persistent[list[float]] = array.new_float(0)
    last_10_actual_duration: Persistent[list[int]] = array.new_int(0)
    last_10_is_bullish: Persistent[list[bool]] = array.new_bool(0)

    prediction_flip_bar_indices: Persistent[list[int]] = array.new_int(0)
    prediction_flip_supertrend_levels: Persistent[list[float]] = array.new_float(0)
    all_flip_bar_indices: Persistent[list[int]] = array.new_int(0)
    all_flip_prices: Persistent[list[float]] = array.new_float(0)
    all_flip_supertrend_levels: Persistent[list[float]] = array.new_float(0)
    all_flip_is_bullish: Persistent[list[bool]] = array.new_bool(0)

    trend_quality_scores: Persistent[list[int]] = array.new_int(0)
    trend_volume_ratios: Persistent[list[float]] = array.new_float(0)
    all_flip_volatility_ratios: Persistent[list[float]] = array.new_float(0)
    all_flip_distances_from_st: Persistent[list[float]] = array.new_float(0)

    current_predicted_avg: Persistent[float] = na(float)
    current_predicted_end: Persistent[float] = na(float)
    current_base_percentile: Persistent[float] = na(float)
    current_prediction_is_bullish: Persistent[bool] = False

    success_count: Persistent[int] = 0
    success_rate: Persistent[float] = na(float)
    avg_accuracy: Persistent[float] = na(float)
    prediction_count: Persistent[int] = 0

    def calculate_decay_rate():
        base_decay: float = 1.0

        if vol_ratio > 2.5:
            base_decay *= 1.3
        elif vol_ratio > 1.5:
            base_decay *= 1.1
        elif vol_ratio < 0.7:
            base_decay *= 0.85

        if atr_ratio > 1.3:
            base_decay *= 1.2
        elif atr_ratio < 0.8:
            base_decay *= 0.9

        return base_decay

    def ewa_avg(arr, decay):
        __block_result__ = na
        if array.size(arr) == 0:
            __block_result__ = na
        else:
            sum_weighted: float = 0.0
            sum_weights: float = 0.0
            n: int = array.size(arr)

            for i in pine_range(0, n - 1):
                weight: float = math.pow(decay, n - 1 - i)
                value: float = array.get(arr, i)
                sum_weighted += value * weight
                sum_weights += weight

            __block_result__ = sum_weighted / sum_weights
        return __block_result__

    def ewa_stdev(arr, decay, mean):
        __block_result_1__ = na
        if array.size(arr) <= 1:
            __block_result_1__ = 0.0
        else:
            sum_weighted_sq: float = 0.0
            sum_weights: float = 0.0
            n: int = array.size(arr)

            for i in pine_range(0, n - 1):
                weight: float = math.pow(decay, n - 1 - i)
                value: float = array.get(arr, i)
                diff: float = value - mean
                sum_weighted_sq += weight * diff * diff
                sum_weights += weight

            __block_result_1__ = math.sqrt(sum_weighted_sq / sum_weights)
        return __block_result_1__

    def get_structure_multiplier(current_price, pivot_highs, pivot_lows, sensitivity_atr):
        structure_mult: float = 1.0

        __block_result_2__ = na
        if array.size(pivot_highs) == 0 and array.size(pivot_lows) == 0:
            __block_result_2__ = structure_mult
        else:
            proximity_threshold: float = atr_current * sensitivity_atr
            near_level: bool = False

            if array.size(pivot_highs) > 0:
                for i in pine_range(0, array.size(pivot_highs) - 1):
                    level: float = array.get(pivot_highs, i)
                    if math.abs(current_price - level) <= proximity_threshold:
                        near_level = True
                        break

            if not near_level and array.size(pivot_lows) > 0:
                for i in pine_range(0, array.size(pivot_lows) - 1):
                    level: float = array.get(pivot_lows, i)
                    if math.abs(current_price - level) <= proximity_threshold:
                        near_level = True
                        break

            structure_mult = 0.7 if near_level else 1.0
            __block_result_2__ = structure_mult
        return __block_result_2__

    def get_stock_type_multiplier(stock_type):
        type_mult: float = 1.0

        if stock_type == 'Small Cap':
            type_mult = 0.65
        elif stock_type == 'Biotech / Speculative':
            type_mult = 0.55
        elif stock_type == 'Blue Chip / Large Cap':
            type_mult = 1.35
        elif stock_type == 'Tech Growth':
            type_mult = 1.1
        elif stock_type == 'Dividend / Value':
            type_mult = 1.25
        elif stock_type == 'Cyclical':
            type_mult = 0.9
        elif stock_type == 'Crypto / High Volatility':
            type_mult = 0.6

        return type_mult

    def calculate_flip_strength(vol_ratio_at_flip, atr_ratio_at_flip, quality_at_flip):
        strength: float = 0.0

        if vol_ratio_at_flip >= 2.5:
            strength += 40.0
        elif vol_ratio_at_flip >= 1.5:
            strength += 28.0
        elif vol_ratio_at_flip >= 1.0:
            strength += 15.0

        if atr_ratio_at_flip >= 1.2:
            strength += 30.0
        elif atr_ratio_at_flip >= 1.0:
            strength += 20.0
        elif atr_ratio_at_flip >= 0.8:
            strength += 10.0

        strength += quality_at_flip / 100.0 * 30.0

        flip_mult: float = 0.5 + strength / 100.0 * 1.5
        return flip_mult

    def calculate_learning_adjustment(error_ratios):
        learning_mult: float = 1.0

        __block_result_3__ = na
        if array.size(error_ratios) < 3:
            __block_result_3__ = learning_mult
        else:
            avg_error_ratio: float = array.avg(error_ratios)

            if avg_error_ratio > 1.0:
                reduction: float = math.min((avg_error_ratio - 1.0) * 0.5, 0.15)
                learning_mult = 1.0 - reduction
            elif avg_error_ratio < 1.0:
                increase: float = math.min((1.0 - avg_error_ratio) * 0.5, 0.15)
                learning_mult = 1.0 + increase

            __block_result_3__ = learning_mult
        return __block_result_3__

    def find_probability_threshold(target, median_duration, decay_rate):
        __block_result_4__ = na
        if median_duration <= 0 or target >= 1.0:
            __block_result_4__ = na
        else:
            k: float = 1.5
            lambda__ren__ = median_duration / math.pow(0.693, 1 / k)

            adjusted_target = 0.5 + (target - 0.5) / decay_rate
            adjusted_target = math.max(0.01, math.min(0.99, adjusted_target))

            x = lambda__ren__ * math.pow(-math.log(1.0 - adjusted_target), 1.0 / k)

            __block_result_4__ = math.max(5, math.min(500, x))
        return __block_result_4__

    def empirical_survival_pct(arr: list[int], x: float):
        n: int = array.size(arr)
        __block_result_5__ = na
        if n == 0:
            __block_result_5__ = na
        else:
            cnt: int = 0
            for i in pine_range(0, n - 1):
                if array.get(arr, i) >= x:
                    cnt = cnt + 1
            __block_result_5__ = 100.0 * cnt / n
        return __block_result_5__

    def calculate_regime_multiplier(trend_durations, analysis_depth):
        regime_mult: float = 1.0

        total_trends: int = array.size(trend_durations)

        __block_result_6__ = na
        if total_trends < analysis_depth:
            __block_result_6__ = regime_mult
        else:
            recent_sum: float = 0.0
            for i in pine_range(0, analysis_depth - 1):
                recent_sum += array.get(trend_durations, total_trends - 1 - i)
            recent_avg: float = recent_sum / analysis_depth

            historical_avg: float = array.avg(trend_durations)

            ratio: float = recent_avg / historical_avg

            if ratio >= 1.3:
                regime_mult = 1.2
            elif ratio >= 1.1:
                regime_mult = 1.1
            elif ratio <= 0.7:
                regime_mult = 0.8
            elif ratio <= 0.9:
                regime_mult = 0.9

            __block_result_6__ = regime_mult
        return __block_result_6__

    def calculate_similarity_score(curr_vol: float, hist_vol: float, curr_atr: float, hist_atr: float, curr_quality: int, hist_quality: int, curr_dist: float, hist_dist: float, curr_near_level: bool, hist_near_level: bool):
        similarity: float = 0.0

        if math.abs(curr_vol - hist_vol) <= 0.5:
            similarity += 30.0
        elif math.abs(curr_vol - hist_vol) <= 1.0:
            similarity += 15.0

        if math.abs(curr_atr - hist_atr) <= 0.3:
            similarity += 30.0
        elif math.abs(curr_atr - hist_atr) <= 0.6:
            similarity += 15.0

        if math.abs(curr_quality - hist_quality) <= 15:
            similarity += 20.0
        elif math.abs(curr_quality - hist_quality) <= 30:
            similarity += 10.0

        curr_dist_norm: float = curr_dist / atr_current
        hist_dist_norm: float = hist_dist / atr_current
        if math.abs(curr_dist_norm - hist_dist_norm) <= 0.5:
            similarity += 10.0

        if curr_near_level == hist_near_level:
            similarity += 10.0

        return similarity

    error_ratios: Persistent[list[float]] = array.new_float(0)

    all_flip_structure_mults: Persistent[list[float]] = array.new_float(0)
    all_flip_stock_type_mults: Persistent[list[float]] = array.new_float(0)
    all_flip_strength_mults: Persistent[list[float]] = array.new_float(0)
    all_flip_learning_mults: Persistent[list[float]] = array.new_float(0)
    all_flip_regime_mults: Persistent[list[float]] = array.new_float(0)

    advanced_structure_mult: Persistent[float] = 1.0
    advanced_stock_type_mult: Persistent[float] = 1.0
    advanced_flip_strength_mult: Persistent[float] = 1.0
    advanced_learning_mult: Persistent[float] = 1.0
    advanced_regime_mult: Persistent[float] = 1.0

    def get_similar_trends(all_durations: list[int], all_is_bullish: list[bool], current_is_bullish: bool, current_vol_ratio: float, current_atr_ratio: float, current_quality: int, current_dist: float, current_near_level: bool, target_count: int, min_similar: int):
        similar_durations: Persistent[list[int]] = array.new_int(0)
        array.clear(similar_durations)

        total_trends: int = array.size(all_durations)

        __block_result_7__ = na
        if total_trends == 0:
            __block_result_7__ = similar_durations
        else:
            scores: Persistent[list[float]] = array.new_float(0)
            durations: Persistent[list[int]] = array.new_int(0)
            array.clear(scores)
            array.clear(durations)

            for i in pine_range(0, total_trends - 1):
                hist_is_bullish: bool = array.get(all_is_bullish, i)

                if hist_is_bullish == current_is_bullish:
                    hist_vol: float = array.get(trend_volume_ratios, i)
                    hist_atr: float = array.get(all_flip_volatility_ratios, i)
                    hist_quality: int = array.get(trend_quality_scores, i)
                    hist_dist: float = array.get(all_flip_distances_from_st, i)
                    hist_structure_mult: float = array.get(all_flip_structure_mults, i)
                    hist_near_level: bool = hist_structure_mult < 1.0

                    score: float = calculate_similarity_score(current_vol_ratio, hist_vol, current_atr_ratio, hist_atr, current_quality, hist_quality, current_dist, hist_dist, current_near_level, hist_near_level)

                    array.push(scores, score)
                    array.push(durations, array.get(all_durations, i))

            valid_count: int = array.size(scores)

            if valid_count <= min_similar:
                similar_durations = array.copy(durations)
            else:
                for i in pine_range(0, valid_count - 2):
                    for j in pine_range(0, valid_count - 2 - i):
                        if array.get(scores, j) < array.get(scores, j + 1):
                            temp_score: float = array.get(scores, j)
                            array.set(scores, j, array.get(scores, j + 1))
                            array.set(scores, j + 1, temp_score)

                            temp_dur: int = array.get(durations, j)
                            array.set(durations, j, array.get(durations, j + 1))
                            array.set(durations, j + 1, temp_dur)

                take_count: int = math.min(target_count, valid_count)
                for i in pine_range(0, take_count - 1):
                    array.push(similar_durations, array.get(durations, i))

            __block_result_7__ = similar_durations
        return __block_result_7__

    g_pivot_highs: Persistent[list[float]] = array.new_float(0)
    g_pivot_lows: Persistent[list[float]] = array.new_float(0)
    g_ph: float = ta.pivothigh(high, i_structure_lookback, i_structure_lookback)
    g_pl: float = ta.pivotlow(low, i_structure_lookback, i_structure_lookback)
    if not na(g_ph):
        array.push(g_pivot_highs, g_ph)
        if array.size(g_pivot_highs) > 10:
            array.shift(g_pivot_highs)
    if not na(g_pl):
        array.push(g_pivot_lows, g_pl)
        if array.size(g_pivot_lows) > 10:
            array.shift(g_pivot_lows)

    if stFlip and barstate.isconfirmed:
        array.push(trend_quality_scores, quality_score)
        array.push(trend_volume_ratios, vol_ratio)
        if array.size(trend_quality_scores) > PREDICTION_SAMPLES:
            array.shift(trend_quality_scores)
            array.shift(trend_volume_ratios)

        if i_prediction_mode == 'Advanced' and i_use_error_learning and (not na(current_predicted_end)) and (current_trend_bars > 0):
            error_ratio: float = current_predicted_end / current_trend_bars
            array.push(error_ratios, error_ratio)

            if array.size(error_ratios) > i_error_memory_depth:
                array.shift(error_ratios)

        if not na(current_predicted_avg) and (not na(current_predicted_end)):
            array.push(last_10_predicted_avg, current_predicted_avg)
            array.push(last_10_predicted_end, current_predicted_end)
            array.push(last_10_actual_duration, current_trend_bars)
            array.push(last_10_is_bullish, current_prediction_is_bullish)

            if array.size(last_10_actual_duration) > 10:
                array.shift(last_10_predicted_avg)
                array.shift(last_10_predicted_end)
                array.shift(last_10_actual_duration)
                array.shift(last_10_is_bullish)

        advanced_structure_mult = 1.0
        advanced_stock_type_mult = 1.0
        advanced_flip_strength_mult = 1.0
        advanced_learning_mult = 1.0
        advanced_regime_mult = 1.0

        if i_prediction_mode == 'Advanced':
            advanced_structure_mult = get_structure_multiplier(close, g_pivot_highs, g_pivot_lows, i_structure_sensitivity)

            advanced_stock_type_mult = get_stock_type_multiplier(i_stock_type)

            current_flip_strength: float = calculate_flip_strength(vol_ratio, atr_ratio, quality_score)
            advanced_flip_strength_mult = current_flip_strength

            if i_use_error_learning:
                advanced_learning_mult = calculate_learning_adjustment(error_ratios)

            new_trend_is_bullish: bool = stDir == 1
            trend_type_for_regime: list[int] = bull_trend_durations if new_trend_is_bullish else bear_trend_durations
            advanced_regime_mult = calculate_regime_multiplier(trend_type_for_regime, 3)

        if stDir == 1:
            array.push(bear_trend_durations, current_trend_bars)
            if array.size(bear_trend_durations) > PREDICTION_SAMPLES:
                array.shift(bear_trend_durations)

            array.push(all_trend_durations, current_trend_bars)
            array.push(all_trend_is_bullish, False)

            array.push(all_flip_bar_indices, bar_index)
            array.push(all_flip_prices, close)
            array.push(all_flip_supertrend_levels, supertrend)
            array.push(all_flip_is_bullish, True)

            array.push(all_flip_structure_mults, advanced_structure_mult)
            array.push(all_flip_stock_type_mults, advanced_stock_type_mult)
            array.push(all_flip_strength_mults, advanced_flip_strength_mult)
            array.push(all_flip_learning_mults, advanced_learning_mult)
            array.push(all_flip_regime_mults, advanced_regime_mult)

            array.push(all_flip_volatility_ratios, atr_ratio)
            array.push(all_flip_distances_from_st, math.abs(close - supertrend))

            if array.size(all_trend_durations) > PREDICTION_SAMPLES:
                array.shift(all_trend_durations)
                array.shift(all_trend_is_bullish)
                array.shift(all_flip_bar_indices)
                array.shift(all_flip_prices)
                array.shift(all_flip_supertrend_levels)
                array.shift(all_flip_is_bullish)
                array.shift(all_flip_structure_mults)
                array.shift(all_flip_stock_type_mults)
                array.shift(all_flip_strength_mults)
                array.shift(all_flip_learning_mults)
                array.shift(all_flip_regime_mults)
                array.shift(all_flip_volatility_ratios)
                array.shift(all_flip_distances_from_st)
        else:
            array.push(bull_trend_durations, current_trend_bars)
            if array.size(bull_trend_durations) > PREDICTION_SAMPLES:
                array.shift(bull_trend_durations)

            array.push(all_trend_durations, current_trend_bars)
            array.push(all_trend_is_bullish, True)

            array.push(all_flip_bar_indices, bar_index)
            array.push(all_flip_prices, close)
            array.push(all_flip_supertrend_levels, supertrend)
            array.push(all_flip_is_bullish, False)

            array.push(all_flip_structure_mults, advanced_structure_mult)
            array.push(all_flip_stock_type_mults, advanced_stock_type_mult)
            array.push(all_flip_strength_mults, advanced_flip_strength_mult)
            array.push(all_flip_learning_mults, advanced_learning_mult)
            array.push(all_flip_regime_mults, advanced_regime_mult)

            array.push(all_flip_volatility_ratios, atr_ratio)
            array.push(all_flip_distances_from_st, math.abs(close - supertrend))

            if array.size(all_trend_durations) > PREDICTION_SAMPLES:
                array.shift(all_trend_durations)
                array.shift(all_trend_is_bullish)
                array.shift(all_flip_bar_indices)
                array.shift(all_flip_prices)
                array.shift(all_flip_supertrend_levels)
                array.shift(all_flip_is_bullish)
                array.shift(all_flip_structure_mults)
                array.shift(all_flip_stock_type_mults)
                array.shift(all_flip_strength_mults)
                array.shift(all_flip_learning_mults)
                array.shift(all_flip_regime_mults)
                array.shift(all_flip_volatility_ratios)
                array.shift(all_flip_distances_from_st)

        flip_bar_index = bar_index
        flip_supertrend_level = supertrend
        current_trend_bars = 1

        if i_enable_prediction and barstate.isconfirmed:
            new_trend_is_bullish: bool = stDir == 1

            current_vol_ratio: float = vol_ratio
            current_atr_ratio: float = atr_ratio
            current_quality: int = quality_score
            current_dist: float = math.abs(close - supertrend)
            current_near_level: bool = advanced_structure_mult < 1.0

            trend_type_durations: list[int] = get_similar_trends(all_trend_durations, all_trend_is_bullish, new_trend_is_bullish, current_vol_ratio, current_atr_ratio, current_quality, current_dist, current_near_level, 15, 5)
            trend_samples: int = array.size(trend_type_durations)

            min_samples_needed: int = 5 if actual_style == 'Scalping (1-5m)' else 3 if actual_style == 'Day Trading (15m-1h)' else 2 if actual_style == 'Swing Trading (4h-D)' else 1 if actual_style == 'Position Trading (D-W)' else 1

            if trend_samples >= min_samples_needed:
                trend_predicted_end: float = na(float)
                trend_avg: float = na(float)
                trend_median: float = na(float)
                trend_spread: float = na(float)
                filtered_durations: list[int] = array.new_int(0)
                current_decay_rate: float = calculate_decay_rate()

                if i_prediction_mode == 'Simple':
                    trend_median = array.median(trend_type_durations)
                    trend_avg = trend_median
                    trend_spread = 0.0
                    filtered_durations = array.copy(trend_type_durations)

                    trend_predicted_end = trend_median * 2.5
                else:
                    filtered_durations = array.copy(trend_type_durations)
                    if array.size(filtered_durations) >= 5:
                        p10__000001a2__: float = array.percentile_nearest_rank(filtered_durations, 10)
                        p90: float = array.percentile_nearest_rank(filtered_durations, 90)

                        for i in pine_range(array.size(filtered_durations) - 1, 0):
                            val: float = array.get(filtered_durations, i)
                            if val < p10__000001a2__ or val > p90:
                                array.remove(filtered_durations, i)

                    trend_median = array.median(filtered_durations)

                    trim_count: int = cast_int(array.size(filtered_durations) * 0.2)
                    trimmed: list[int] = array.copy(filtered_durations)
                    array.sort(trimmed)
                    if trim_count > 0 and array.size(trimmed) > 2 * trim_count:
                        for i in pine_range(0, trim_count - 1):
                            array.shift(trimmed)
                            array.pop(trimmed)

                    trimmed_mean: float = (ewa_avg(trimmed, i_ewa_decay) if i_use_ewa else array.avg(trimmed)) if array.size(trimmed) > 0 else trend_median
                    trend_avg = trend_median * 0.6 + trimmed_mean * 0.4

                    deviations: list[float] = array.new_float(0)
                    for i in pine_range(0, array.size(filtered_durations) - 1):
                        dev: float = math.abs(array.get(filtered_durations, i) - trend_median)
                        array.push(deviations, dev)

                    mad: float = array.median(deviations)
                    iqr_spread: float = array.percentile_nearest_rank(filtered_durations, 75) - array.percentile_nearest_rank(filtered_durations, 25)

                    trend_spread = mad * 1.4826 * 0.5 + iqr_spread * 0.7 * 0.5

                    volatility_adj: float = 0.85 if atr_ratio > 1.2 else 1.15 if atr_ratio < 0.8 else 1.0
                    volume_adj: float = 0.8 if vol_ratio > 2.0 else 1.2 if vol_ratio < 0.7 else 1.0

                    style_multiplier: float = 1.0
                    if actual_style == 'Scalping (1-5m)':
                        style_multiplier = 0.7
                        trend_spread = trend_spread * 0.8
                    elif actual_style == 'Day Trading (15m-1h)':
                        style_multiplier = 0.85
                    elif actual_style == 'Swing Trading (4h-D)':
                        style_multiplier = 1.1
                        trend_spread = trend_spread * 1.1
                    elif actual_style == 'Position Trading (D-W)':
                        style_multiplier = 1.3
                        trend_spread = trend_spread * 1.2

                    context_multiplier: float = volatility_adj * volume_adj * style_multiplier

                    base_percentile: float = na(float)
                    if advanced_flip_strength_mult < 0.7:
                        base_percentile = array.percentile_nearest_rank(filtered_durations, 25)
                    elif advanced_flip_strength_mult > 1.3:
                        base_percentile = array.percentile_nearest_rank(filtered_durations, 90)
                    else:
                        base_percentile = trend_median

                    current_base_percentile = base_percentile

                    trend_predicted_end = find_probability_threshold(0.95, base_percentile, current_decay_rate)

                    if not na(trend_predicted_end):
                        trend_predicted_end = trend_predicted_end * context_multiplier

                        trend_predicted_end = math.min(trend_predicted_end, 500)

                if i_prediction_mode == 'Advanced':
                    total_mult: float = advanced_structure_mult * advanced_stock_type_mult * advanced_flip_strength_mult * advanced_learning_mult * advanced_regime_mult

                    total_mult = math.max(0.4, math.min(2.0, total_mult))

                    trend_predicted_end = trend_predicted_end * total_mult

                trend_predicted_end = math.min(trend_predicted_end, 500)

                trend_samples_display: int = trend_samples
                trend_confidence: float = math.min(100, trend_samples_display / PREDICTION_SAMPLES * 100)
                trend_confidence_label: str = 'High' if trend_confidence > 80 else 'Medium' if trend_confidence > 50 else 'Low'
                trend_data_quality: str = 'Excellent' if trend_samples_display >= PREDICTION_SAMPLES else 'Good' if trend_samples_display >= 10 else 'Limited'
                weighting_method: str = 'EWA (Decay: ' + string.tostring(i_ewa_decay, '#.##') + ')' if i_use_ewa else 'Equal weights'
                trend_min: int = array.min(trend_type_durations)
                trend_max: int = array.max(trend_type_durations)

                advanced_section: str = ""
                if i_prediction_mode == 'Advanced':
                    advanced_section = '\n\n─────────────────────────────\n' + '   ADVANCED ADJUSTMENTS 🚀\n' + '─────────────────────────────\n\n' + '🏛️ Market Structure: ' + string.tostring(advanced_structure_mult, '#.##') + 'x\n' + '📊 Stock Type (' + i_stock_type + '): ' + string.tostring(advanced_stock_type_mult, '#.##') + 'x\n' + '💪 Flip Strength: ' + string.tostring(advanced_flip_strength_mult, '#.##') + 'x\n' + ('🧠 Error Learning: ' + string.tostring(advanced_learning_mult, '#.##') + 'x\n' if i_use_error_learning else '') + '⚡ Regime: ' + string.tostring(advanced_regime_mult, '#.##') + 'x\n' + '⚡ Total Impact: ' + string.tostring(advanced_structure_mult * advanced_stock_type_mult * advanced_flip_strength_mult * advanced_learning_mult * advanced_regime_mult, '#.##') + 'x\n\n💡 Advanced mode active'

                mode_info: str = '📊 SIMPLE MODE - Basic median calculation' if i_prediction_mode == 'Simple' else '⚙️ STANDARD MODE - Full statistical analysis' if i_prediction_mode == 'Standard' else '🚀 ADVANCED MODE - Statistics + multipliers'

                trend_tooltip: str = '════════════════════════════\n' + '  HISTORICAL TREND ANALYSIS\n' + '════════════════════════════\n\n' + mode_info + '\n\n' + '📊 Estimated Range: ' + string.tostring(cast_int(trend_predicted_end)) + ' bars\n' + '   (Based on past trend patterns)\n' + '📈 Trend Type: ' + ('Bullish' if new_trend_is_bullish else 'Bearish') + '\n\n' + '─────────────────────────────\n' + '       CONFIDENCE METRICS\n' + '─────────────────────────────\n\n' + '💪 Data Confidence: ' + string.tostring(cast_int(trend_confidence)) + '% (' + trend_confidence_label + ')\n' + '🔬 Sample Size: ' + string.tostring(trend_samples_display) + ' past trends\n' + '📊 Data Quality: ' + trend_data_quality + '\n' + '⚖️ Weighting: ' + weighting_method + '\n\n' + '─────────────────────────────\n' + '      HISTORICAL STATISTICS\n' + '─────────────────────────────\n\n' + '📉 Average: ' + string.tostring(trend_avg, '#.#') + ' bars (50% point)\n' + '📐 Spread: ±' + string.tostring(trend_spread, '#.#') + ' bars\n' + '📌 Range: ' + string.tostring(trend_min) + ' - ' + string.tostring(trend_max) + ' bars\n' + '📊 Median: ' + string.tostring(trend_median, '#.#') + ' bars\n' + '🎯 Extended Range: ' + string.tostring(trend_predicted_end, '#.#') + ' bars' + advanced_section + '\n\n─────────────────────────────\n\n' + '⚠️ IMPORTANT:\n' + 'This analyzes ' + string.tostring(trend_samples_display) + ' past SuperTrend trends.\n' + 'Future trends may behave differently.\n' + 'Not investment advice.' + ('\n\n💡 Using EWA: Recent trends weighted higher' if i_use_ewa else '')

                if array.size(prediction_box_counts) >= 5:
                    box_count: int = array.shift(prediction_box_counts)
                    label_count: int = array.shift(prediction_label_counts)
                    array.shift(prediction_set_is_bullish)
                    array.shift(prediction_flip_bar_indices)
                    array.shift(prediction_flip_supertrend_levels)

                    for i in pine_range(0, box_count - 1):
                        box.delete(array.shift(prediction_boxes))
                    for i in pine_range(0, label_count - 1):
                        label.delete(array.shift(prediction_labels))

                box_width: float = trend_predicted_end / BOX_COUNT

                box_height: float = atrS * 0.12
                box_top: float = na(float)
                box_bottom: float = na(float)
                if new_trend_is_bullish:
                    box_top = flip_supertrend_level - atrS * 0.03
                    box_bottom = box_top - box_height
                else:
                    box_bottom = flip_supertrend_level + atrS * 0.03
                    box_top = box_bottom + box_height

                base_color: Color = color.green if new_trend_is_bullish else color.red

                new_box_count: int = 0
                new_label_count: int = 0

                for i in pine_range(0, BOX_COUNT - 1):
                    box_left: int = flip_bar_index + cast_int(i * box_width)
                    box_right: int = flip_bar_index + cast_int((i + 1) * box_width)

                    opacity: int = 5 + cast_int(i / 29.0 * 90)
                    box_color: Color = color.new(base_color, opacity)

                    new_box: Box = box.new(box_left, box_top, box_right, box_bottom, bgcolor=box_color, border_color=na)
                    array.push(prediction_boxes, new_box)
                    new_box_count += 1

                label_offset: float = 0
                center_label_y: float = box_top + label_offset
                center_bar: int = flip_bar_index + cast_int(trend_predicted_end / 2)
                lbl_center: Label = label.new(center_bar, center_label_y, 'ℹ️ Trend Analysis', style=label.style_label_down, color=color.new(color.blue, 0), textcolor=color.white, size=label_size_const, tooltip=trend_tooltip, yloc=yloc.price)
                array.push(prediction_labels, lbl_center)
                new_label_count += 1

                prob_positions: list[float] = array.from_items(0.25, 0.5, 0.75, 0.9, 1.0)

                for i in pine_range(0, 4):
                    position_ratio: float = array.get(prob_positions, i)
                    prob_bar: int = flip_bar_index + cast_int(position_ratio * trend_predicted_end)
                    bars_from_start: float = position_ratio * trend_predicted_end

                    continuation_pct: float = empirical_survival_pct(filtered_durations, bars_from_start)

                    rounded_percentage: int = 0 if na(continuation_pct) else cast_int(math.round(continuation_pct / 5.0) * 5)

                    prob_text: str = string.tostring(rounded_percentage) + '%'

                    position_name: str = '25% Point (Q1)' if i == 0 else '50% Point (Median)' if i == 1 else '75% Point (Q3)' if i == 2 else '90% Point' if i == 3 else '100% Point (End)'
                    prob_tooltip: str = 'HISTORICAL TREND FREQUENCY\n' + '━━━━━━━━━━━━━━━━\n' + 'At bar #' + string.tostring(cast_int(bars_from_start)) + ' from trend start\n\n' + '📈 ' + string.tostring(rounded_percentage) + '% = Historical frequency: past trends reached here\n' + '📊 ' + string.tostring(100 - rounded_percentage) + '% = Historical frequency: past trends ended before\n\n' + 'Example: ' + string.tostring(rounded_percentage) + '% means:\n' + '• ' + string.tostring(rounded_percentage) + ' out of 100 past trends continued to this point\n' + '• ' + string.tostring(100 - rounded_percentage) + ' out of 100 ended before reaching here\n\n' + 'Based on:\n' + '• ' + string.tostring(array.size(filtered_durations)) + ' past SuperTrend trends on this chart\n' + '• Current volume: ' + string.tostring(vol_ratio, '#.#') + 'x avg\n' + '• Current volatility: ' + string.tostring(atr_ratio, '#.#') + 'x avg\n\n' + '⚠️ DISCLAIMER:\n' + 'This is historical analysis, not prediction.\n' + 'Future trends may behave differently.\n' + 'Not investment advice.'

                    prob_label_offset: float = 3 * syminfo.mintick
                    lbl_prob: Label = label.new(prob_bar, box_bottom - prob_label_offset, prob_text, style=label.style_none, textcolor=color.black, text_formatting=text.format_bold, size=label_size_const, yloc=yloc.price, tooltip=prob_tooltip)
                    array.push(prediction_labels, lbl_prob)
                    new_label_count += 1

                array.push(prediction_box_counts, new_box_count)
                array.push(prediction_label_counts, new_label_count)
                array.push(prediction_set_is_bullish, new_trend_is_bullish)
                array.push(prediction_flip_bar_indices, flip_bar_index)
                array.push(prediction_flip_supertrend_levels, flip_supertrend_level)

                current_predicted_avg = trend_avg
                current_predicted_end = trend_predicted_end
                current_prediction_is_bullish = new_trend_is_bullish
    else:
        current_trend_bars += 1

    if i_enable_prediction and barstate.islast and (array.size(last_10_actual_duration) == 0):
        backtest_predicted_avg: Persistent[list[float]] = array.new_float(0)
        backtest_predicted_end: Persistent[list[float]] = array.new_float(0)
        backtest_actual_duration: Persistent[list[int]] = array.new_int(0)
        backtest_is_bullish: Persistent[list[bool]] = array.new_bool(0)

        total_trends: int = array.size(all_trend_durations)
        if total_trends > 1:
            for i in pine_range(1, total_trends - 1):
                current_duration: int = array.get(all_trend_durations, i)
                current_is_bullish: bool = array.get(all_trend_is_bullish, i)

                prior_trends_same_type: Persistent[list[int]] = array.new_int(0)
                array.clear(prior_trends_same_type)

                for j in pine_range(0, i - 1):
                    prior_is_bullish: bool = array.get(all_trend_is_bullish, j)
                    if prior_is_bullish == current_is_bullish:
                        array.push(prior_trends_same_type, array.get(all_trend_durations, j))

                prior_samples: int = array.size(prior_trends_same_type)
                if prior_samples >= 1:
                    pred_avg: float = ewa_avg(prior_trends_same_type, i_ewa_decay) if i_use_ewa else array.avg(prior_trends_same_type)
                    pred_median: float = array.median(prior_trends_same_type)
                    pred_end: float = find_probability_threshold(0.95, pred_median, 1.0)

                    array.push(backtest_predicted_avg, pred_avg)
                    array.push(backtest_predicted_end, pred_end)
                    array.push(backtest_actual_duration, current_duration)
                    array.push(backtest_is_bullish, current_is_bullish)

        backtest_count: int = array.size(backtest_actual_duration)
        if backtest_count > 0:
            start_idx: int = math.max(0, backtest_count - 10)
            for i in pine_range(start_idx, backtest_count - 1):
                array.push(last_10_predicted_avg, array.get(backtest_predicted_avg, i))
                array.push(last_10_predicted_end, array.get(backtest_predicted_end, i))
                array.push(last_10_actual_duration, array.get(backtest_actual_duration, i))
                array.push(last_10_is_bullish, array.get(backtest_is_bullish, i))

    if i_enable_prediction and barstate.islast:
        current_durations = bull_trend_durations if is_bullish else bear_trend_durations
        samples = array.size(current_durations)

        if samples >= 1:
            avg_duration: float = ewa_avg(current_durations, i_ewa_decay) if i_use_ewa else array.avg(current_durations)
            std_dev: float = (ewa_stdev(current_durations, i_ewa_decay, avg_duration) if i_use_ewa else array.stdev(current_durations)) if samples > 1 else 0.0
            min_duration: int = array.min(current_durations)
            max_duration: int = array.max(current_durations)
            median_duration: float = array.median(current_durations)

            predicted_end_raw: float = find_probability_threshold(0.95, median_duration, calculate_decay_rate())
            predicted_end: float = avg_duration + 2.0 * std_dev if na(predicted_end_raw) else math.min(predicted_end_raw, 500)

            confidence: float = math.min(100, samples / PREDICTION_SAMPLES * 100)
            confidence_label: str = 'High' if confidence > 80 else 'Medium' if confidence > 50 else 'Low'
            data_quality: str = 'Excellent' if samples >= PREDICTION_SAMPLES else 'Good' if samples >= 10 else 'Limited'

            remaining_bars: int = cast_int(predicted_end - current_trend_bars)
            percent_complete: float = current_trend_bars / predicted_end * 100

            prediction_count = array.size(last_10_actual_duration)

            if prediction_count > 0:
                success_count = 0
                total_accuracy: float = 0.0

                for i in pine_range(0, prediction_count - 1):
                    actual: int = array.get(last_10_actual_duration, i)
                    pred_avg: float = array.get(last_10_predicted_avg, i)
                    pred_end: float = array.get(last_10_predicted_end, i)

                    if actual <= pred_end:
                        success_count = success_count + 1

                    error_pct: float = math.abs(actual - pred_avg) / pred_avg * 100
                    accuracy: float = math.max(0, 100 - error_pct)
                    total_accuracy += accuracy

                success_rate = success_count / prediction_count * 100
                avg_accuracy = total_accuracy / prediction_count

            weighting_method: str = 'EWA (Decay: ' + string.tostring(i_ewa_decay, '#.##') + ')' if i_use_ewa else 'Equal weights'
            '════════════════════════════\n' + '  TREND DURATION PREDICTION\n' + '════════════════════════════\n\n' + '📊 Predicted End: ' + string.tostring(cast_int(predicted_end)) + ' bars (95% coverage)\n' + '📈 Current Trend: ' + ('Bullish' if is_bullish else 'Bearish') + ' (' + string.tostring(current_trend_bars) + ' bars)\n' + '⏱️ Remaining: ' + string.tostring(remaining_bars) + ' bars\n' + '🎯 Progress: ' + string.tostring(cast_int(percent_complete)) + '%\n\n' + '─────────────────────────────\n' + '       CONFIDENCE METRICS\n' + '─────────────────────────────\n\n' + '💪 Confidence: ' + string.tostring(cast_int(confidence)) + '% (' + confidence_label + ')\n' + '🔬 Sample Size: ' + string.tostring(samples) + ' trends\n' + '📊 Data Quality: ' + data_quality + '\n' + '⚖️ Weighting: ' + weighting_method + '\n\n' + '─────────────────────────────\n' + '      HISTORICAL STATISTICS\n' + '─────────────────────────────\n\n' + '📉 Average: ' + string.tostring(avg_duration, '#.#') + ' bars (50% point)\n' + '📐 Std Dev: ±' + string.tostring(std_dev, '#.#') + ' bars\n' + '📌 Range: ' + string.tostring(min_duration) + ' - ' + string.tostring(max_duration) + ' bars\n' + '📊 Median: ' + string.tostring(median_duration, '#.#') + ' bars\n' + '🎯 Predicted (95% Weibull): ' + string.tostring(predicted_end, '#.#') + ' bars\n\n' + '─────────────────────────────\n\n' + 'Based on last ' + string.tostring(samples) + ' SuperTrend flips\n' + 'Timeframe: Current chart' + ('\n\n💡 Using EWA: Recent trends weighted higher' if i_use_ewa else '')

    if goldenCross and show_entry_labels and barstate.isconfirmed:
        signal_mode = '🔪 ' if use_scalpel else ''

        sl_price: float = supertrend
        risk_ps: float = math.max(math.abs(close - sl_price), atrS)
        risk_section: str = '\n\n💰 RISK (Stop = SuperTrend)\nStop: ' + string.tostring(sl_price, format.mintick) + ' (risk ' + string.tostring(risk_ps, format.mintick) + ')\nTP1 (' + string.tostring(tp1_r, '#.#') + 'R): ' + string.tostring(close + tp1_r * risk_ps, format.mintick) + '\nTP2 (' + string.tostring(tp2_r, '#.#') + 'R): ' + string.tostring(close + tp2_r * risk_ps, format.mintick) if godmode_enabled and show_risk_levels else ''
        mtf_section: str = '\n\n🔭 HTF (' + htf1_tf + '/' + htf2_tf + '): ' + string.tostring(mtf_agree_count) + '/2 agree' if godmode_enabled else ''

        label_text = signal_mode + 'ℹ️ BUY'

        label_tooltip = '🟢 BUY SIGNAL\n━━━━━━━━━━━━━━━━\nPrice: ' + string.tostring(close, format.mintick) + '\nSupertrend: ' + string.tostring(supertrend, format.mintick) + '\n\n📊 VOLUME:\n' + vol_state + ' (' + string.tostring(vol_ratio, '#.##') + 'x)\n\n📈 VOLUME MOMENTUM:\n' + ('📊📊 STRONG (' + string.tostring(vol_momentum_ratio, '#.##') + 'x)' if vol_momentum_strong else '📈 Rising (' + string.tostring(vol_momentum_ratio, '#.##') + 'x)' if vol_momentum_rising else '➡️ Neutral') + '\n\n⭐ QUALITY:\n' + quality_level + ' (' + string.tostring(quality_score) + '/70)' + mtf_section + risk_section
        label_y = low - 2 * syminfo.mintick

        label.new(bar_index, label_y, label_text, style=label.style_label_up, color=color.new(bull_color_input, 0), textcolor=color.white, size=label_size_const, tooltip=label_tooltip)

    if deathCross and show_entry_labels and barstate.isconfirmed:
        signal_mode = '🔪 ' if use_scalpel else ''

        sl_price: float = supertrend
        risk_ps: float = math.max(math.abs(sl_price - close), atrS)
        risk_section: str = '\n\n💰 RISK (Stop = SuperTrend)\nStop: ' + string.tostring(sl_price, format.mintick) + ' (risk ' + string.tostring(risk_ps, format.mintick) + ')\nTP1 (' + string.tostring(tp1_r, '#.#') + 'R): ' + string.tostring(close - tp1_r * risk_ps, format.mintick) + '\nTP2 (' + string.tostring(tp2_r, '#.#') + 'R): ' + string.tostring(close - tp2_r * risk_ps, format.mintick) if godmode_enabled and show_risk_levels else ''
        mtf_section: str = '\n\n🔭 HTF (' + htf1_tf + '/' + htf2_tf + '): ' + string.tostring(mtf_agree_count) + '/2 agree' if godmode_enabled else ''

        label_text = signal_mode + 'ℹ️ SELL'

        label_tooltip = '🔴 SELL SIGNAL\n━━━━━━━━━━━━━━━━\nPrice: ' + string.tostring(close, format.mintick) + '\nSupertrend: ' + string.tostring(supertrend, format.mintick) + '\n\n📊 VOLUME:\n' + vol_state + ' (' + string.tostring(vol_ratio, '#.##') + 'x)\n\n📉 VOLUME MOMENTUM:\n' + ('📊📊 STRONG (' + string.tostring(vol_momentum_ratio, '#.##') + 'x)' if vol_momentum_strong else '📉 Rising (' + string.tostring(vol_momentum_ratio, '#.##') + 'x)' if vol_momentum_rising else '➡️ Neutral') + '\n\n⭐ QUALITY:\n' + quality_level + ' (' + string.tostring(quality_score) + '/70)' + mtf_section + risk_section
        label_y = high + 2 * syminfo.mintick

        label.new(bar_index, label_y, label_text, style=label.style_label_down, color=color.new(bear_color_input, 0), textcolor=color.white, size=label_size_const, tooltip=label_tooltip)

    bars_since_vol_spike_label: Persistent[int] = 999

    if bars_since_vol_spike_label < 999:
        bars_since_vol_spike_label += 1

    volume_spike_alert = vol_is_spike and (not goldenCross) and (not deathCross) and signal_quality_ok and volume_ok and (vol_momentum_ok_long or vol_momentum_ok_short) and (bars_since_vol_spike_label >= VOL_SPIKE_COOLDOWN)

    if volume_spike_alert and show_info_labels and barstate.isconfirmed:
        spike_text = '💥\nVOL\nSPIKE\n' + string.tostring(vol_ratio, '#.#') + 'x'
        spike_tooltip = '💥 VOLUME SPIKE DETECTED\n━━━━━━━━━━━━━━━━━\nCurrent Volume: ' + string.tostring(volume, '#') + '\nAverage (' + string.tostring(vol_length) + '): ' + string.tostring(vol_ma, '#') + '\nRatio: ' + string.tostring(vol_ratio, '#.##') + 'x\n\nThreshold: ' + string.tostring(vol_spike_threshold, '#.#') + 'x\n\n✅ ALL ENTRY FILTERS PASSED:\n• Quality: ' + string.tostring(quality_score) + '/' + string.tostring(min_quality_score) + ' ✓\n• Volume: Confirmed ✓\n• Vol Momentum: Confirmed ✓\n\n💡 Major event with full confirmation!\nHigh-quality setup - watch for entry.'
        spike_color = color.aqua if is_bullish else color.orange
        spike_style = label.style_label_up if is_bullish else label.style_label_down
        spike_y = low if is_bullish else high

        label.new(bar_index, spike_y, spike_text, style=spike_style, color=color.new(spike_color, 0), textcolor=color.white, size=label_size_const, tooltip=spike_tooltip)

        bars_since_vol_spike_label = 0

    ribbon_active: bool = show_ribbon_fill and (not neutral)

    price_to_st_distance = math.abs(close - supertrend)

    vol_intensity: float = -(vol_ratio - 1.0) * 30
    baseColor = bull_color_input if is_bullish else bear_color_input

    vol_momentum_boost: float = 15 if use_volume_momentum and (is_bullish and vol_momentum_confirms_bull or (is_bearish and vol_momentum_confirms_bear)) else 0

    bar_mid: float = (high + low) / 2

    is_flip_bar: bool = supertrend_flip_bullish or supertrend_flip_bearish

    was_bullish: bool = supertrend_flip_bearish
    was_bearish: bool = supertrend_flip_bullish

    ribbon_start: float = na(float)
    ribbon_end: float = na(float)

    if is_flip_bar:
        if supertrend_flip_bullish:
            ribbon_start = bar_mid if close > bar_mid else close
            ribbon_end = high if close > bar_mid else bar_mid
        else:
            ribbon_start = bar_mid if close < bar_mid else close
            ribbon_end = low if close < bar_mid else bar_mid
    else:
        ribbon_start = close
        ribbon_end = supertrend

    def get_layer(start, end_val, step):
        return (start * (15 - step) + end_val * step) / 15

    l1: float = ribbon_start if ribbon_active else na
    l2: float = get_layer(ribbon_start, ribbon_end, 1) if ribbon_active else na
    l3: float = get_layer(ribbon_start, ribbon_end, 2) if ribbon_active else na
    l4: float = get_layer(ribbon_start, ribbon_end, 3) if ribbon_active else na
    l5: float = get_layer(ribbon_start, ribbon_end, 4) if ribbon_active else na
    l6: float = get_layer(ribbon_start, ribbon_end, 5) if ribbon_active else na
    l7: float = get_layer(ribbon_start, ribbon_end, 6) if ribbon_active else na
    l8: float = get_layer(ribbon_start, ribbon_end, 7) if ribbon_active else na
    l9: float = get_layer(ribbon_start, ribbon_end, 8) if ribbon_active else na
    l10: float = get_layer(ribbon_start, ribbon_end, 9) if ribbon_active else na
    l11: float = get_layer(ribbon_start, ribbon_end, 10) if ribbon_active else na
    l12: float = get_layer(ribbon_start, ribbon_end, 11) if ribbon_active else na
    l13: float = get_layer(ribbon_start, ribbon_end, 12) if ribbon_active else na
    l14: float = get_layer(ribbon_start, ribbon_end, 13) if ribbon_active else na
    l15: float = get_layer(ribbon_start, ribbon_end, 14) if ribbon_active else na
    l16: float = ribbon_end if ribbon_active else na

    def get_opacity(base_opacity):
        return math.max(5, math.min(95, base_opacity - vol_momentum_boost + vol_intensity))

    c1: Color = color.new(baseColor, get_opacity(85)) if ribbon_active else na
    c2: Color = color.new(baseColor, get_opacity(81)) if ribbon_active else na
    c3: Color = color.new(baseColor, get_opacity(77)) if ribbon_active else na
    c4: Color = color.new(baseColor, get_opacity(73)) if ribbon_active else na
    c5: Color = color.new(baseColor, get_opacity(69)) if ribbon_active else na
    c6: Color = color.new(baseColor, get_opacity(65)) if ribbon_active else na
    c7: Color = color.new(baseColor, get_opacity(61)) if ribbon_active else na
    c8: Color = color.new(baseColor, get_opacity(57)) if ribbon_active else na
    c9: Color = color.new(baseColor, get_opacity(53)) if ribbon_active else na
    c10: Color = color.new(baseColor, get_opacity(49)) if ribbon_active else na
    c11: Color = color.new(baseColor, get_opacity(45)) if ribbon_active else na
    c12: Color = color.new(baseColor, get_opacity(41)) if ribbon_active else na
    c13: Color = color.new(baseColor, get_opacity(37)) if ribbon_active else na
    c14: Color = color.new(baseColor, get_opacity(33)) if ribbon_active else na
    c15: Color = color.new(baseColor, get_opacity(30)) if ribbon_active else na

    p1 = plot(l1, display=display.none, editable=False)
    p2 = plot(l2, display=display.none, editable=False)
    p3 = plot(l3, display=display.none, editable=False)
    p4 = plot(l4, display=display.none, editable=False)
    p5 = plot(l5, display=display.none, editable=False)
    p6 = plot(l6, display=display.none, editable=False)
    p7 = plot(l7, display=display.none, editable=False)
    p8 = plot(l8, display=display.none, editable=False)
    p9 = plot(l9, display=display.none, editable=False)
    p10 = plot(l10, display=display.none, editable=False)
    p11 = plot(l11, display=display.none, editable=False)
    p12 = plot(l12, display=display.none, editable=False)
    p13 = plot(l13, display=display.none, editable=False)
    p14 = plot(l14, display=display.none, editable=False)
    p15 = plot(l15, display=display.none, editable=False)
    p16 = plot(l16, display=display.none, editable=False)

    fill(p1, p2, c1 if ribbon_active else na, editable=False)
    fill(p2, p3, c2 if ribbon_active else na, editable=False)
    fill(p3, p4, c3 if ribbon_active else na, editable=False)
    fill(p4, p5, c4 if ribbon_active else na, editable=False)
    fill(p5, p6, c5 if ribbon_active else na, editable=False)
    fill(p6, p7, c6 if ribbon_active else na, editable=False)
    fill(p7, p8, c7 if ribbon_active else na, editable=False)
    fill(p8, p9, c8 if ribbon_active else na, editable=False)
    fill(p9, p10, c9 if ribbon_active else na, editable=False)
    fill(p10, p11, c10 if ribbon_active else na, editable=False)
    fill(p11, p12, c11 if ribbon_active else na, editable=False)
    fill(p12, p13, c12 if ribbon_active else na, editable=False)
    fill(p13, p14, c13 if ribbon_active else na, editable=False)
    fill(p14, p15, c14 if ribbon_active else na, editable=False)
    fill(p15, p16, c15 if ribbon_active else na, editable=False)

    if show_dashboard and barstate.islast:
        tablePos = position.top_left if table_position == 'Top Left' else position.top_center if table_position == 'Top Center' else position.top_right if table_position == 'Top Right' else position.middle_left if table_position == 'Middle Left' else position.middle_center if table_position == 'Middle Center' else position.middle_right if table_position == 'Middle Right' else position.bottom_left if table_position == 'Bottom Left' else position.bottom_center if table_position == 'Bottom Center' else position.bottom_right

        tableTxtSize = size.auto if table_text_size == 'Auto' else size.tiny if table_text_size == 'Tiny' else size.small if table_text_size == 'Small' else size.normal if table_text_size == 'Normal' else size.large if table_text_size == 'Large' else size.huge

        dash_bg = color.new(color.black, 0)
        header_bg = color.new(color.gray, 50)
        header_text: str = "SUPER-DUPER SUPERTREND"

        dashTable: Persistent[Table] = table.new(tablePos, columns=2, rows=20, bgcolor=dash_bg, border_width=0)

        header_tooltip: str = "Super-Duper SuperTrend Dashboard\n\nReal-time trend analysis combining:\n• BIAS-style adaptive Supertrend\n• Volume confirmation\n• Quality scoring system\n\nAll metrics update live on each bar close."
        table.cell(dashTable, 0, 0, header_text, text_color=color.white, text_size=tableTxtSize, bgcolor=header_bg, text_halign=text.align_center, tooltip=header_tooltip)
        table.merge_cells(dashTable, 0, 0, 1, 0)

        vol_points = 30 if vol_is_spike else 20 if vol_is_high else 10 if basic_volume_confirm else 0
        volatility_points = 30 if vol_expanding else 15 if vol_rising else 0
        vol_momentum_points = 10 if use_volume_momentum and vol_momentum_strong_trend else 5 if use_volume_momentum and vol_momentum_rising else 0

        quality_label_tooltip = 'Signal Quality Score (0-70 points)\n\nMeasures signal strength based on:\n\n📊 VOLUME (0-30 pts): ' + string.tostring(vol_points) + ' pts\n• Spike (2.5x+) = 30\n• High (1.5x+) = 20\n• Above average = 10\n\n🌪️ VOLATILITY (0-30 pts): ' + string.tostring(volatility_points) + ' pts\n• Expanding (1.3x+) = 30\n• Rising (1.0x+) = 15\n\n📈 VOL MOMENTUM BONUS (0-10 pts): ' + string.tostring(vol_momentum_points) + ' pts\n• Strong momentum = 10\n• Rising momentum = 5\n\nThresholds:\n• 60+ = EXCELLENT ⭐⭐⭐\n• 45-59 = STRONG ⭐⭐\n• 30-44 = GOOD ⭐\n• 0-29 = WEAK ⚠️'

        quality_value_tooltip = 'Current Score: ' + string.tostring(quality_score) + '/70\nLevel: ' + quality_level + '\n\n' + ('✅ ABOVE minimum threshold (' + string.tostring(min_quality_score) + ')' if quality_score >= min_quality_score else '❌ BELOW minimum threshold (' + string.tostring(min_quality_score) + ')') + '\n\nBREAKDOWN:\n━━━━━━━━━━━━\n📊 Volume: ' + string.tostring(vol_points) + ' pts (' + vol_state + ')\n🌪️ Volatility: ' + string.tostring(volatility_points) + ' pts (' + volatility_state + ')\n📈 Vol Momentum: ' + string.tostring(vol_momentum_points) + ' pts' + (' (' + string.tostring(vol_momentum_ratio, '#.##') + 'x)' if use_volume_momentum else ' (disabled)') + '\n━━━━━━━━━━━━\nTOTAL: ' + string.tostring(quality_score) + ' pts\n\n' + ('💡 EXCELLENT quality - very high probability signal' if quality_score >= 60 else '💡 STRONG quality - reliable signal' if quality_score >= 45 else '💡 GOOD quality - decent signal' if quality_score >= 30 else '⚠️ WEAK quality - consider waiting for better setup')

        table.cell(dashTable, 0, 1, 'Signal Quality', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_left, tooltip=quality_label_tooltip)
        table.cell(dashTable, 1, 1, quality_level + ' (' + string.tostring(quality_score) + '/70)', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_center, tooltip=quality_value_tooltip)

        table.cell(dashTable, 0, 2, '═══════════════════', text_color=color.new(color.gray, 50), text_size=size.tiny, text_halign=text.align_center)
        table.merge_cells(dashTable, 0, 2, 1, 2)

        st_text = '🟢 BULLISH' if is_bullish else '🔴 BEARISH'
        st_price = ' @ ' + string.tostring(supertrend, format.mintick)

        multiplier_adjustment = (adaptiveMult / st_mult - 1.0) * 100 if st_use_adaptive else 0
        base_band = atrS * st_mult
        adaptive_band = atrS * adaptiveMult
        st_label_tooltip = 'BIAS-Style Adaptive Supertrend\n\nAdvanced calculation features:\n\n🔧 ADAPTIVE MULTIPLIER:' + (' ON' if st_use_adaptive else ' OFF') + '\n• Base multiplier: ' + string.tostring(st_mult, '#.##') + 'x\n• Current multiplier: ' + string.tostring(adaptiveMult, '#.##') + 'x\n• Adjustment: ' + ('+' if multiplier_adjustment > 0 else '') + string.tostring(multiplier_adjustment, '#.#') + '%\n\nAdapts based on:\n• Volume weight: ' + string.tostring(volWeight, '#.##') + 'x\n• Trend strength: ' + string.tostring(trendStrength * 100, '#') + '%\n\n📈 EMA SMOOTHING: ' + string.tostring(st_smooth_factor * 100, '#') + '%\n• Reduces noise\n• ~' + string.tostring(cast_int(1 / st_smooth_factor), '#') + ' bar smoothing\n\n⏸️ NEUTRAL BARS: ' + string.tostring(st_neutral_bars) + ' bars\n• Hides ribbon after flip\n• Reduces false signals' + ('\n• Currently: ' + ('IN NEUTRAL WINDOW' if neutral else 'active') if st_neutral_bars > 0 else '')
        st_value_tooltip = 'Current Trend: ' + ('🟢 BULLISH' if is_bullish else '🔴 BEARISH') + '\n\nSupertrend Level: ' + string.tostring(supertrend, format.mintick) + '\nCurrent Price: ' + string.tostring(close, format.mintick) + '\nDistance: ' + string.tostring(math.abs(close - supertrend), format.mintick) + ' (' + string.tostring(math.abs(close - supertrend) / close * 100, '#.##') + '%)\n\nLAST FLIP:\n• Direction: ' + ('Flipped to BULLISH' if is_bullish else 'Flipped to BEARISH') + ('\n• Status: ⏸️ IN NEUTRAL WINDOW' if neutral else '\n• Status: ✅ Active') + '\n\nBAND DETAILS:\n━━━━━━━━━━━━\nATR (' + string.tostring(st_length) + '): ' + string.tostring(atrS, format.mintick) + '\nBase width: ' + string.tostring(base_band, format.mintick) + '\nAdaptive width: ' + string.tostring(adaptive_band, format.mintick) + '\nAdjustment: ' + ('+' if multiplier_adjustment > 0 else '') + string.tostring(multiplier_adjustment, '#.#') + '%\n\n' + ('💡 Support at ' + string.tostring(supertrend, format.mintick) + '\n   Hold above = trend intact' if is_bullish else '💡 Resistance at ' + string.tostring(supertrend, format.mintick) + '\n   Break above = trend reversal')

        table.cell(dashTable, 0, 3, 'Supertrend', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_left, tooltip=st_label_tooltip)
        table.cell(dashTable, 1, 3, st_text + st_price, text_color=color.white, text_size=tableTxtSize, text_halign=text.align_center, tooltip=st_value_tooltip)

        vol_text = vol_state + ' (' + string.tostring(vol_ratio, '#.#') + 'x)'
        vol_label_tooltip = 'Volume Analysis System\n\nCompares current volume to ' + string.tostring(vol_length) + '-bar average.\n\nTHRESHOLDS:\n━━━━━━━━━━━━\n💥 SPIKE: ' + string.tostring(vol_spike_threshold, '#.#') + 'x+ average\n   Major event/breakout\n   Highest quality signal\n\n🔥 HIGH: ' + string.tostring(vol_high_threshold, '#.#') + 'x+ average\n   Strong participation\n   Good confirmation\n\n➡️ NORMAL: 1.0x - ' + string.tostring(vol_high_threshold, '#.#') + 'x\n   Average activity\n   Neutral confirmation\n\n📍 LOW: Below ' + string.tostring(vol_low_threshold, '#.#') + 'x average\n   Weak participation\n   Lower quality signal\n\nVolume affects:\n• Quality score (0-30 points)\n• Ribbon darkness (gradual)\n• Adaptive multiplier strength'
        vol_value_tooltip = 'Current Volume State: ' + vol_state + '\n\nVOLUME METRICS:\n━━━━━━━━━━━━\nCurrent: ' + string.tostring(volume, '#') + '\nAverage (' + string.tostring(vol_length) + '): ' + string.tostring(vol_ma, '#') + '\nRatio: ' + string.tostring(vol_ratio, '#.##') + 'x\n\nCATEGORY:\n' + ('💥 SPIKE (' + string.tostring(vol_spike_threshold, '#.#') + 'x+)\n   ✅ Exceptional confirmation!\n   +30 quality points' if vol_is_spike else '🔥 HIGH (' + string.tostring(vol_high_threshold, '#.#') + 'x+)\n   ✅ Strong confirmation\n   +20 quality points' if vol_is_high else '📍 LOW (below ' + string.tostring(vol_low_threshold, '#.#') + 'x)\n   ⚠️ Weak confirmation\n   +0 quality points' if vol_is_low else '➡️ NORMAL\n   Basic confirmation\n   +10 quality points') + '\n\nRIBBON EFFECT:\n' + ('Darkening: -' + string.tostring((vol_ratio - 1.0) * 30, '#') + '% transparency\nHigher volume = darker ribbon' if vol_ratio > 1.0 else 'No darkening (below average)') + '\n\n💡 ' + ('Strong volume confirms trend strength!' if vol_is_spike or vol_is_high else 'Low volume - trend may be weak' if vol_is_low else 'Average volume - trend developing normally')

        table.cell(dashTable, 0, 4, 'Volume', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_left, tooltip=vol_label_tooltip)
        table.cell(dashTable, 1, 4, vol_text, text_color=color.white, text_size=tableTxtSize, text_halign=text.align_center, tooltip=vol_value_tooltip)
        volatility_label_tooltip: str = "Volatility Analysis (ATR Regime)\n\nMeasures current volatility vs 20-bar average.\n\nREGIMES:\n━━━━━━━━━━━━\n🔥 EXPANDING (1.3x+)\n   Major price swings\n   Breakout potential\n   +30 quality points\n\n📈 RISING (1.0x - 1.3x)\n   Increasing volatility\n   Building momentum\n   +15 quality points\n\n➡️ STABLE (0.9x - 1.0x)\n   Normal conditions\n   Steady trend\n   +0 quality points\n\n📉 CONTRACTING (below 0.9x)\n   Low volatility\n   Consolidation phase\n   +0 quality points\n\nVolatility affects:\n• Quality score (0-30 pts)\n• Breakout probability\n• Stop-loss positioning"

        volatility_value_tooltip = 'Current Volatility: ' + volatility_state + '\n\nATR METRICS:\n━━━━━━━━━━━━\nCurrent ATR(14): ' + string.tostring(atr_current, format.mintick) + '\nAverage ATR(20): ' + string.tostring(atr_ma, format.mintick) + '\nRatio: ' + string.tostring(atr_ratio, '#.##') + 'x\n\nREGIME ANALYSIS:\n' + ('🔥 EXPANDING\n   ATR is 1.3x+ average\n   ✅ High volatility = breakout likely\n   ✅ +30 quality points\n   💡 Excellent for trend trades!' if atr_ratio >= 1.3 else '📈 RISING\n   ATR is above average\n   ✅ Volatility increasing\n   ✅ +15 quality points\n   💡 Momentum building' if vol_rising else '📉 CONTRACTING\n   ATR below 0.9x average\n   ⚠️ Low volatility\n   ⚠️ +0 quality points\n   💡 Consolidation - wait for expansion' if vol_contracting else '➡️ STABLE\n   ATR near average\n   Normal market conditions\n   +0 quality points\n   💡 Steady trend environment') + '\n\nSUPERTREND IMPACT:\n' + ('Adaptive bands adjust automatically\nBand width: ' + string.tostring(adaptive_band, format.mintick) if st_use_adaptive else 'Fixed bands (adaptive disabled)')

        table.cell(dashTable, 0, 5, 'Volatility', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_left, tooltip=volatility_label_tooltip)
        table.cell(dashTable, 1, 5, volatility_state, text_color=color.white, text_size=tableTxtSize, text_halign=text.align_center, tooltip=volatility_value_tooltip)

        table.cell(dashTable, 0, 6, '═══════════════════', text_color=color.new(color.gray, 50), text_size=size.tiny, text_halign=text.align_center)
        table.merge_cells(dashTable, 0, 6, 1, 6)

        if godmode_enabled:
            htf1_txt: str = '⚪' if na(htf1_dir) else '🟢' if htf1_bull else '🔴'
            htf2_txt: str = '⚪' if na(htf2_dir) else '🟢' if htf2_bull else '🔴'
            mtf_value: str = htf1_tf + ' ' + htf1_txt + '  ' + htf2_tf + ' ' + htf2_txt + '  (' + string.tostring(mtf_agree_count) + '/2)'
            mtf_tooltip: str = 'Multi-Timeframe Confluence 🔭\n\nHigher-TF SuperTrend direction vs the current chart:\n\n🔭 ' + htf1_tf + ': ' + ('no data' if na(htf1_dir) else '🟢 Bullish' if htf1_bull else '🔴 Bearish') + '\n🔭 ' + htf2_tf + ': ' + ('no data' if na(htf2_dir) else '🟢 Bullish' if htf2_bull else '🔴 Bearish') + '\n\nAgreement with current chart: ' + string.tostring(mtf_agree_count) + '/2\n\n' + ('⚙️ Gate ON — signals require BOTH higher TFs to agree.' if mtf_gate_signals else '⚙️ Gate OFF — shown for context only (toggle in GOD MODE settings).') + '\n\n💡 Set both TFs ABOVE your chart timeframe.\n💡 More agreement = higher-conviction entries.'
            table.cell(dashTable, 0, 7, '🔭 HTF Confluence', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_left, tooltip=mtf_tooltip)
            table.cell(dashTable, 1, 7, mtf_value, text_color=color.white, text_size=tableTxtSize, text_halign=text.align_center, tooltip=mtf_tooltip)

        if i_enable_prediction:
            current_durations_check = bull_trend_durations if is_bullish else bear_trend_durations
            samples_check = array.size(current_durations_check)

            if prediction_count > 0:
                breakdown: str = ""
                for i in pine_range(0, prediction_count - 1):
                    actual: int = array.get(last_10_actual_duration, i)
                    pred_avg: float = array.get(last_10_predicted_avg, i)
                    pred_end: float = array.get(last_10_predicted_end, i)
                    was_bull: bool = array.get(last_10_is_bullish, i)

                    was_success: bool = actual <= pred_end
                    trend_emoji: str = '🟢' if was_bull else '🔴'
                    success_emoji: str = '✅' if was_success else '❌'

                    breakdown = breakdown + string.tostring(i + 1) + '. ' + trend_emoji + ' ' + success_emoji + ' Predicted: ' + string.tostring(cast_int(pred_avg)) + ' bars | Actual: ' + string.tostring(actual) + ' bars\n'

                pred_header_tooltip: str = 'Prediction Track Record\n\nShows performance of last 10 trend duration predictions:\n\n🎯 Success Rate:\nPercentage of trends that ended within the predicted 95% range\n\n📐 Average Accuracy:\nHow close predictions were to actual durations\nCalculated as: 100% - average(|error|)\n\n💡 Based on ' + string.tostring(prediction_count) + ' completed predictions'
                success_tooltip: str = 'SUCCESS RATE\n━━━━━━━━━━━━━━━━━━━━\n\n' + string.tostring(cast_int(success_count)) + ' out of ' + string.tostring(prediction_count) + ' trends ended within predicted range\n\n' + string.tostring(cast_int(success_rate)) + '% = Percentage of trends that stayed within predicted 95% range\n\n━━━━━━━━━━━━━━━━━━━━\nLAST ' + string.tostring(prediction_count) + ' PREDICTIONS:\n━━━━━━━━━━━━━━━━━━━━\n\n' + breakdown + '\n✅ = Within predicted range\n❌ = Outside predicted range\n🟢 = Bullish trend\n🔴 = Bearish trend'
                accuracy_tooltip: str = 'AVERAGE ACCURACY\n━━━━━━━━━━━━━━━━━━━━\n\n' + string.tostring(cast_int(avg_accuracy)) + '% = Average closeness to predicted duration\n\nCalculated as: 100% - average(|predicted - actual| / predicted × 100)\n\nExample:\n• Predicted: 50 bars\n• Actual: 45 bars\n• Error: |50-45|/50 = 10%\n• Accuracy: 100% - 10% = 90%\n\nHigher % = More accurate predictions'

                table.cell(dashTable, 0, 8, '📊 PREDICTION RECORD', text_color=color.white, text_size=tableTxtSize, bgcolor=header_bg, text_halign=text.align_center, tooltip=pred_header_tooltip)
                table.merge_cells(dashTable, 0, 8, 1, 8)

                table.cell(dashTable, 0, 9, 'Success Rate', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_left, tooltip=success_tooltip)
                table.cell(dashTable, 1, 9, string.tostring(cast_int(success_count)) + '/10 (' + string.tostring(cast_int(success_rate)) + '%)', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_center, tooltip=success_tooltip)

                table.cell(dashTable, 0, 10, 'Avg Accuracy', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_left, tooltip=accuracy_tooltip)
                table.cell(dashTable, 1, 10, string.tostring(cast_int(avg_accuracy)) + '%', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_center, tooltip=accuracy_tooltip)
            else:
                status_text: str = '✅ Active\n' + string.tostring(samples_check) + ' trends analyzed' if samples_check >= 1 else '⏳ Collecting data...\nNeed 1+ trend flip'
                status_tooltip: str = 'Trend Duration Prediction Status\n\n' + ('ACTIVE ✅\n━━━━━━━━━━━━━━━\nPrediction is active and showing on chart!\n\nCurrent trend: ' + ('🟢 Bullish' if is_bullish else '🔴 Bearish') + '\nHistorical trends: ' + string.tostring(samples_check) + '\n\n💡 Look for colored gradient box with prediction percentages on the chart.\n\nTrack record will appear here after 10 completed predictions.' if samples_check >= 1 else 'WAITING FOR DATA ⏳\n━━━━━━━━━━━━━━━\nPrediction needs at least 1 SuperTrend flip to start.\n\nCurrent status:\n• SuperTrend flips: ' + string.tostring(samples_check) + '\n• Minimum needed: 1\n\n💡 Wait for the first trend flip, then predictions will appear automatically!')

                table.cell(dashTable, 0, 8, '📊 Prediction Status', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_left, tooltip=status_tooltip)
                table.cell(dashTable, 1, 8, status_text, text_color=color.white, text_size=tableTxtSize, text_halign=text.align_center, tooltip=status_tooltip)

        if i_enable_prediction and prediction_count > 0:
            table.cell(dashTable, 0, 11, '═══════════════════', text_color=color.new(color.gray, 50), text_size=size.tiny, text_halign=text.align_center)
            table.merge_cells(dashTable, 0, 11, 1, 11)

        if i_enable_prediction and i_prediction_mode == 'Advanced':
            last_structure_mult: float = 1.0
            last_stock_type_mult: float = 1.0
            last_flip_strength_mult: float = 1.0
            last_learning_mult: float = 1.0
            last_regime_mult: float = 1.0

            flip_history_size: int = array.size(all_flip_structure_mults)
            if flip_history_size > 0:
                last_structure_mult = array.get(all_flip_structure_mults, flip_history_size - 1)
                last_stock_type_mult = array.get(all_flip_stock_type_mults, flip_history_size - 1)
                last_flip_strength_mult = array.get(all_flip_strength_mults, flip_history_size - 1)
                last_learning_mult = array.get(all_flip_learning_mults, flip_history_size - 1)
                last_regime_mult = array.get(all_flip_regime_mults, flip_history_size - 1)

            total_advanced_mult: float = last_structure_mult * last_stock_type_mult * last_flip_strength_mult * last_learning_mult * last_regime_mult

            adv_header_tooltip: str = 'Advanced Prediction Adjustments 🚀\n\nEnhances base predictions with 5 intelligent factors:\n\n1️⃣ Market Structure (±30%)\n• Detects S/R levels via pivot analysis\n• Near levels = shorter trends\n\n2️⃣ Stock Type (±40%)\n• Different assets have unique behaviors\n• ' + i_stock_type + ' multiplier applied\n\n3️⃣ Flip Strength (±20%)\n• Strong momentum = longer trends\n• Based on volume, volatility, quality at flip\n\n4️⃣ Error Learning (±15%)\n• Learns from past mistakes\n• Adapts predictions over time\n\n5️⃣ Regime Detection (±20%)\n• Analyzes recent trend patterns\n• Long recent trends → longer prediction\n• Short recent trends → shorter prediction\n\nThese multiply the base prediction for 30-50% better accuracy!'
            structure_tooltip: str = 'MARKET STRUCTURE: ' + string.tostring(last_structure_mult, '#.##') + 'x\n\n' + ('• Near S/R level (-30%)\n• Trend likely to reverse sooner' if last_structure_mult < 1.0 else '• No nearby S/R levels\n• Normal trend duration expected') + '\n\nDetects support/resistance via pivot analysis (' + string.tostring(i_structure_lookback) + ' bars)\n\nProximity threshold: ' + string.tostring(i_structure_sensitivity, '#.#') + ' × ATR'
            type_tooltip: str = 'STOCK TYPE: ' + string.tostring(last_stock_type_mult, '#.##') + 'x\n\nAsset: ' + i_stock_type + '\n\n' + ('• Stable asset → longer trends' if last_stock_type_mult > 1.0 else '• Volatile asset → shorter trends' if last_stock_type_mult < 1.0 else '• Moderate behavior') + '\n\nDifferent assets have unique trend patterns:\n• Blue Chip: 1.35x (longest)\n• Dividend: 1.25x\n• Tech Growth: 1.10x\n• Cyclical: 0.90x\n• Small Cap: 0.65x\n• Crypto: 0.60x\n• Biotech: 0.55x (shortest)'
            flip_tooltip: str = 'FLIP STRENGTH: ' + string.tostring(last_flip_strength_mult, '#.##') + 'x\n\nBased on:\n• Volume at flip\n• Volatility expansion\n• Quality score\n\n' + ('• Strong flip → extended trend\n• High momentum = sustained move' if last_flip_strength_mult > 1.0 else '• Weak flip → shorter trend\n• Low momentum = quick reversal' if last_flip_strength_mult < 1.0 else '• Moderate flip strength\n• Average trend expected')
            learning_tooltip: str = 'ERROR LEARNING: ' + string.tostring(last_learning_mult, '#.##') + 'x\n\nAdaptive correction from past errors\n\nMemory: ' + string.tostring(array.size(error_ratios)) + '/' + string.tostring(i_error_memory_depth) + ' predictions\n\n' + (('• Reducing predictions\n• System was over-predicting\n• Learning to be more conservative' if last_learning_mult < 1.0 else '• Increasing predictions\n• System was under-predicting\n• Learning to be more aggressive' if last_learning_mult > 1.0 else '• No adjustment needed\n• Predictions are accurate') if array.size(error_ratios) >= 3 else '• Not enough data yet\n• Need 3+ completed predictions\n• Currently learning...')
            regime_tooltip: str = 'REGIME DETECTION: ' + string.tostring(last_regime_mult, '#.##') + 'x\n\nAnalyzes last 3 trends (same type)\n\n' + ('• Recent trends LONGER than average\n• Market regime favors extended trends ✅\n• Expect continuation' if last_regime_mult > 1.0 else '• Recent trends SHORTER than average\n• Market regime favors brief trends ⚠️\n• Expect quick reversals' if last_regime_mult < 1.0 else '• Recent trends match historical average\n• Normal market regime ➡️\n• No bias detected')

            table.cell(dashTable, 0, 12, '🚀 ADVANCED FACTORS', text_color=color.white, text_size=tableTxtSize, bgcolor=header_bg, text_halign=text.align_center, tooltip=adv_header_tooltip)
            table.merge_cells(dashTable, 0, 12, 1, 12)

            table.cell(dashTable, 0, 13, 'Structure', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_left, tooltip=structure_tooltip)
            table.cell(dashTable, 1, 13, string.tostring(last_structure_mult, '#.##') + 'x', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_center, tooltip=structure_tooltip)

            table.cell(dashTable, 0, 14, 'Type', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_left, tooltip=type_tooltip)
            table.cell(dashTable, 1, 14, string.tostring(last_stock_type_mult, '#.##') + 'x', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_center, tooltip=type_tooltip)

            table.cell(dashTable, 0, 15, 'Flip', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_left, tooltip=flip_tooltip)
            table.cell(dashTable, 1, 15, string.tostring(last_flip_strength_mult, '#.##') + 'x', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_center, tooltip=flip_tooltip)

            current_row: int = 16
            if i_use_error_learning:
                table.cell(dashTable, 0, current_row, 'Learning', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_left, tooltip=learning_tooltip)
                table.cell(dashTable, 1, current_row, string.tostring(last_learning_mult, '#.##') + 'x', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_center, tooltip=learning_tooltip)
                current_row += 1

            table.cell(dashTable, 0, current_row, 'Regime', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_left, tooltip=regime_tooltip)
            table.cell(dashTable, 1, current_row, string.tostring(last_regime_mult, '#.##') + 'x', text_color=color.white, text_size=tableTxtSize, text_halign=text.align_center, tooltip=regime_tooltip)

        if i_enable_prediction:
            disclaimer_text: str = "⚠️ DISCLAIMER"
            disclaimer_tooltip: str = "IMPORTANT LEGAL DISCLAIMER\n━━━━━━━━━━━━━━━━━━━━\n\n⚠️ NOT FINANCIAL ADVICE\nThis indicator provides historical analysis only.\nIt is NOT investment, financial, or trading advice.\n\n📊 HISTORICAL ANALYSIS\nPredictions are based on past SuperTrend patterns.\nPast performance does NOT guarantee future results.\n\n⚡ NO GUARANTEES\nMarkets are unpredictable and risky.\nTrends can reverse unexpectedly at any time.\n\n💰 USE AT YOUR OWN RISK\nYou are solely responsible for your trading decisions.\nNever risk more than you can afford to lose.\n\n🔍 DO YOUR OWN RESEARCH\nThis is an educational tool only.\nConsult a licensed financial advisor before trading.\n\n━━━━━━━━━━━━━━━━━━━━\n✅ By using this indicator, you acknowledge\n   these limitations and accept full responsibility."

            table.cell(dashTable, 0, 18, disclaimer_text, text_color=color.orange, text_size=size.tiny, text_halign=text.align_center, tooltip=disclaimer_tooltip)
            table.merge_cells(dashTable, 0, 18, 1, 18)

    if goldenCross and barstate.isconfirmed:
        vol_momentum_status = (' | Vol Momentum: 📊📊 STRONG (' + string.tostring(vol_momentum_ratio, '#.##') + 'x)' if vol_momentum_strong else ' | Vol Momentum: 📈 Rising (' + string.tostring(vol_momentum_ratio, '#.##') + 'x)') if use_volume_momentum else ''
        alert('⬆️ LONG: Supertrend bullish + Quality: ' + string.tostring(quality_score) + '/70\n' + 'Volume: ' + vol_state + vol_momentum_status, alert.freq_once_per_bar_close)

    if deathCross and barstate.isconfirmed:
        vol_momentum_status = (' | Vol Momentum: 📊📊 STRONG (' + string.tostring(vol_momentum_ratio, '#.##') + 'x)' if vol_momentum_strong else ' | Vol Momentum: 📉 Rising (' + string.tostring(vol_momentum_ratio, '#.##') + 'x)') if use_volume_momentum else ''
        alert('⬇️ SHORT: Supertrend bearish + Quality: ' + string.tostring(quality_score) + '/70\n' + 'Volume: ' + vol_state + vol_momentum_status, alert.freq_once_per_bar_close)

    alertcondition(goldenCross, title='🟢 BUY Signal', message='⬆️ LONG: {{ticker}} on {{interval}}\nSupertrend flipped bullish\nQuality Score: High\nVolume: Confirmed\n\nPrice: {{close}}\nTime: {{time}}')
    alertcondition(deathCross, title='🔴 SELL Signal', message='⬇️ SHORT: {{ticker}} on {{interval}}\nSupertrend flipped bearish\nQuality Score: High\nVolume: Confirmed\n\nPrice: {{close}}\nTime: {{time}}')
    alertcondition(goldenCross or deathCross, title='🔔 ANY Signal (BUY or SELL)', message='🔔 SIGNAL: {{ticker}} on {{interval}}\nSupertrend signal detected\n\nPrice: {{close}}\nTime: {{time}}\n\nCheck chart for direction!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
