"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barmerge, barstate, box, close,
    color, dayofmonth, dayofweek, display, extend, fill, high, hl2, hour, input, label, line, low,
    math, minute, na, nz, open, plot, position, request, runtime, script, size, string, syminfo,
    ta, table, text, time, time_close, timeframe, timenow, volume, xloc, yloc
)
from pynecore.types import Box, Color, Label, Line, Persistent, PersistentSeries, Series, Table


@udt
class ORBData:
    name: str = na(str)
    minutes: int = na(int)
    high: float = na(float)
    low: float = na(float)
    mid: float = na(float)
    orbRange: float = na(float)
    isEnabled: bool = na(bool)
    isBuilding: bool = na(bool)
    isComplete: bool = na(bool)
    completionBar: int = na(int)
    breakoutUp: bool = na(bool)
    breakoutDown: bool = na(bool)
    breakoutBar: int = na(int)
    breakoutLevel: float = na(float)
    cyclesUp: int = na(int)
    cyclesDown: int = na(int)
    orbBox: Box = na(Box)
    highLine: Line = na(Line)
    lowLine: Line = na(Line)
    midLine: Line = na(Line)
    edgeLabel: Label = na(Label)
    orbColor: Color = na(Color)
    lineWidth: int = na(int)
    lineStyle: str = na(str)


grp_colors: str = "🎨 ORB COLORS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
grp_session: str = "⏰ SESSION SETTINGS ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
grp_breakout: str = "⚡ BREAKOUT DETECTION ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
grp_targets: str = "🎯 TARGETS & RISK ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
grp_FVG: str = "↩️ FVG FILTER ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
grp_lines: str = "📍 TP/SL LINES ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
grp_pullback: str = "↩️ PULLBACK FILTER ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
grp_volume: str = "📊 VOLUME FILTER ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
grp_trend: str = "📈 TREND FILTER ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
grp_dash: str = "📊 DASHBOARD ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
grp_htf: str = "📈 HIGHER TIMEFRAME ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
grp_god: str = "⚡ GOD MODE ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"


@script.indicator("Luxy BIG beautiful Dynamic ORB - v5", shorttitle="Luxy Big Beautiful ORB", overlay=True, max_labels_count=500, max_lines_count=500, max_boxes_count=300)
def main(
    showEdgeLabels=input.bool(True, "Show Edge Labels", inline="core", group=grp_colors),
    labelFormat=input.string("Detailed", "Label Format", options=("Simple", "Detailed"), group=grp_colors, inline="core1"),
    labelSize=input.string("Small", "All Label Size", inline="core1", options=("Tiny", "Small", "Normal", "Large", "Huge"), group=grp_colors, tooltip="Display ORB stage labels at the edge of price levels\n\nShows which ORB period is active (5min/15min/30min/60min)\nLabels follow price as chart scrolls\n\nON = Labels visible\nOFF = Clean chart\n\nVisual size for ALL labels (breakout, retest, failed)\n\nTINY: Minimal space, cluttered on small screens\nSMALL: Clean and readable (recommended)\nNORMAL: Good for presentations\nLARGE: High visibility\nHUGE: Maximum visibility\n\nLabel text format for ALL labels (TP/SL and Breakouts)\n\nSIMPLE:\n• Minimal text\n• TP/SL: 'ENTRY', 'TP1', 'SL'\n• Breakout: '🔼 BREAKOUT UP #1'\n• Clean and compact\n• Good for: Small screens, many lines\n\nDETAILED:\n• Full info with context\n• TP/SL: 'ENTRY: $150.50', 'TP1: $152.20 +1.1%'\n• Breakout: 'ORB15 | #1 | Vol: 2.3x'\n• Shows prices, percentages, ORB stage, volume\n• Good for: Analysis, larger screens (recommended) ⭐\n\nAFTER HIT:\n• TP: '✅ TP1: $152.20'\n• SL: '❌ SL: $148.50'"),
    showBG=input.bool(True, "Show Background", inline="BG", group=grp_colors),
    fillTransparency=input.int(95, "  | Transparency", inline="BG", minval=0, maxval=100, step=5, group=grp_colors, tooltip="Background fill transparency for ORB range\n\n0 = Fully opaque (solid color)\n50 = Semi-transparent\n95 = Nearly invisible (recommended)\n100 = Completely invisible"),
    enableORB5Signals=input.bool(True, "Enable ORB 5", group=grp_colors, inline="5-15", tooltip="Enable/Disable ORB stages\n\nORB 5: First 5 minutes - fastest signals, most noise\nORB 15: First 15 minutes - balanced signals\nORB 30: First 30 minutes - slower, more reliable\nORB 60: First 60 minutes - slowest, most confirmed\n\nDisable stages you don't want to trade"),
    orb5LineColor=input.color(color.yellow, "", inline="5-15", group=grp_colors),
    enableORB15Signals=input.bool(True, "Enable ORB15", group=grp_colors, inline="5-15"),
    orb15LineColor=input.color(color.green, "", inline="5-15", group=grp_colors),
    enableORB30Signals=input.bool(True, "Enable ORB30", group=grp_colors, inline="30-60"),
    orb30LineColor=input.color(color.blue, "", inline="30-60", group=grp_colors),
    enableORB60Signals=input.bool(True, "Enable ORB60", group=grp_colors, inline="30-60"),
    orb60LineColor=input.color(color.purple, "", inline="30-60", group=grp_colors),
    showMidLine=input.bool(True, "Mid-Range Line", group=grp_colors, tooltip="Display a thin line at the midpoint between ORB High and Low\n\nUSEFUL FOR:\n• Visual center reference\n• Mean reversion trading\n• Support/resistance level\n• Range symmetry analysis\n\nThe line uses the same color as the ORB boundaries but thinner\n\nON = Midpoint line visible\nOFF = Only High/Low lines"),
    sessionMode=input.string("Auto-Detect", "Session Mode", options=("Auto-Detect", "Custom"), group=grp_session, tooltip="Define trading session for ORB calculation\n\n🎯 AUTO-DETECT (Recommended):\n• TradingView automatically detects symbol's native hours\n• Stocks: Exchange hours (NYSE 9:30-16:00, LSE 8:00-16:30, etc.)\n• E-mini Futures: See 'Futures Trading Hours' setting below\n• Crypto: 24/7\n• Forex: Native forex session\n• Works perfectly for 99% of cases!\n\n⚙️ CUSTOM:\n• Define your own session hours manually\n• Use format: HHMM-HHMM (e.g., '0930-1600')\n• Set in 'Custom Session Hours' below\n• Timezone: Chart timezone\n\n💡 TIP: Auto-Detect handles timezone/DST automatically!\nIf ORB appears 1 hour off, check chart timezone:\nRight-click chart → Settings → Symbol → Timezone"),
    customSession=input.session("0930-1600", "Custom Session Hours", group=grp_session, tooltip="Custom trading session definition\n\nONLY ACTIVE when Session Mode = Custom\n\nFORMAT: HHMM-HHMM (24-hour)\n\nEXAMPLES:\n• 0930-1600 = NYSE regular hours\n• 0400-2000 = Extended trading\n• 0000-2359 = Full 24 hours\n\nTIMEZONE: Chart timezone"),
    enableExtendedHours=input.bool(False, "Include Extended Hours", group=grp_session, inline="ext1", tooltip="Include pre-market and after-hours trading\n\n🌅 PRE-MARKET: 04:00-09:30 EST\n🌆 REGULAR: 09:30-16:00 EST\n🌃 AFTER-HOURS: 16:00-20:00 EST\n\nWhen ENABLED:\n• ORB tracking works 04:00-20:00\n• Dashboard shows 'OPEN' during extended hours\n• Breakouts detected in extended hours\n\nWhen DISABLED:\n• ORB tracking only 09:30-16:00 (regular)\n• Dashboard shows 'CLOSED' outside regular hours\n\nRECOMMENDED: Enable if you trade extended hours"),
    extendedPreMarket=input.session("0400-0930", "Pre-Market", group=grp_session, inline="ext2", tooltip="Pre-market trading hours\n\nDEFAULT: 04:00-09:30 (NYSE)\n\nDefine the pre-market session window.\nOnly the START time (04:00) is used for extended hours calculation."),
    extendedAfterHours=input.session("1600-2000", "After-Hours", group=grp_session, inline="ext3", tooltip="After-hours trading session\n\nDEFAULT: 16:00-20:00 (NYSE)\n\nDefine the after-hours session window.\nOnly the END time (20:00) is used for extended hours calculation."),
    futuresTradingHours=input.string("Auto-Detect", "Futures Trading Hours", options=("Auto-Detect", "RTH Only (9:30-16:00)", "Electronic Full Day (24hr)"), group=grp_session, tooltip="Control how ORB tracks E-mini futures (ES, NQ, RTY, YM)\n\n🔹 RTH ONLY (9:30-16:00):\n• ORB resets at 9:30 AM ET\n• Tracking ends at 4:00 PM ET\n• Total: 6.5 hours\n• Best for: Day traders focusing on regular session\n\n🔹 ELECTRONIC FULL DAY (24hr):\n• ORB resets at 9:30 AM ET daily\n• Tracking continues 24 hours until next 9:30 AM\n• Covers full Globex session (18:00-17:00)\n• Best for: Swing traders, overnight positions\n\n🔹 AUTO-DETECT (recommended):\n• Checks for volume outside RTH hours\n• If volume detected → Electronic mode\n• If no volume → RTH mode\n• Adapts automatically to your trading style\n\nNOTE: This setting only affects E-mini futures.\nStocks use 'Extended Hours' setting above."),
    enableBreakout=input.bool(True, "Enable Breakout Detection", inline="Show", group=grp_breakout),
    showBreakLabels=input.bool(True, "Show Breakout Labels", group=grp_breakout, inline="Show", tooltip="Detect and label breakouts above ORB High or below ORB Low\n\nON: Shows breakout labels when price exits ORB range\nOFF: Only displays ORB levels without signals\n\nBreakouts detected on CLOSE (no repaint)"),
    enableRetest=input.bool(True, "Show Retest Labels", group=grp_breakout, inline="retest", tooltip="Show labels when price returns to ORB after breakout\n\nRETEST = Price broke out, then came back to test ORB level\n\nUSEFUL FOR:\n• Re-entry opportunities\n• Confirming support/resistance\n• Failed breakout detection\n\nON: Shows retest labels\nOFF: Only shows initial breakout"),
    signalMode=input.string("Track Cycles", "Signal Mode", options=("First Only", "Track Cycles"), group=grp_breakout, inline="mode", tooltip="How many breakout signals to show per day\n\nFIRST ONLY:\n• Shows only the FIRST breakout in each direction\n• One UP signal, one DOWN signal max per day\n• Clean chart, less noise\n• Good for: Swing traders, position traders\n\nTRACK CYCLES:\n• Tracks Breakout → Retest → Re-breakout cycles\n• Multiple signals as price oscillates\n• Detects momentum returns\n• Good for: Active traders, scalpers\n\nRECOMMENDED: Track Cycles"),
    maxCycles=input.int(6, "Max Cycles", minval=1, maxval=10, group=grp_breakout, inline="mode", tooltip="Maximum cycles to track when Signal Mode = Track Cycles\n\nCYCLE = Breakout → Retest → Re-breakout sequence\n\n1-2 cycles: Clean chart, fewer signals\n4-6 cycles: Balanced (recommended)\n8-10 cycles: Very active, may clutter chart\n\nIGNORED when Signal Mode = First Only"),
    breakoutBuffer=input.float(0.2, "Breakout Buffer (%)", minval=0, maxval=5, step=0.1, group=grp_breakout, inline="buffer", tooltip="Extra distance required beyond ORB level for breakout\n\nPREVENTS: False breakouts from tiny penetrations\n\nHOW IT WORKS:\n• UP: Price must close ABOVE (ORB High + buffer%)\n• DOWN: Price must close BELOW (ORB Low - buffer%)\n\nRECOMMENDATIONS:\n• 0.0% = Exact level (sensitive, more signals)\n• 0.1% = Tiny buffer (recommended)\n• 0.3% = Moderate filter\n• 0.5%+ = Conservative (fewer signals)\n\nHigher = fewer but stronger breakouts"),
    retestBuffer=input.float(0.0, "Retest Buffer (%)", minval=0, maxval=5, step=0.1, group=grp_breakout, inline="buffer", tooltip="Tolerance for retest detection\n\nALLOWS: Price to slightly penetrate ORB during retest\n\nHOW IT WORKS:\n• After UP breakout: Retest if price returns to ORB High ± buffer\n• After DOWN breakout: Retest if price returns to ORB Low ± buffer\n\nRECOMMENDATIONS:\n• 0.0% = Must touch exact level (strict)\n• 0.1-0.2% = Slight tolerance (recommended)\n• 0.3-0.5% = Generous tolerance\n\nHigher = more retests detected"),
    minRetestDistancePct=input.float(0.5, "Min Distance for Retest (%)", minval=0.5, maxval=10, step=0.5, group=grp_breakout, tooltip="How far price must travel away from ORB before retest is valid\n\nPREVENTS: Labeling tiny bounces as 'retests'\n\nEXAMPLE: ORB High = $10.00, Distance = 2%\n• Price breaks to $10.20 (2% away) ✓ Valid\n• Price returns to $10.00 → RETEST LABEL\n• If only went to $10.05 (0.5% away) ✗ Not valid\n\nRECOMMENDATIONS:\n• 0.5% = Very sensitive (many retests)\n• 2.0% = Balanced (filters noise) ⭐\n• 3.0%+ = Only strong moves\n\nHigher = fewer but more meaningful retests"),
    minBarsOutside=input.int(2, "Min Bars Outside ORB", minval=1, maxval=10, group=grp_breakout, tooltip="How many bars price must stay outside ORB for 'committed' breakout\n\nPREVENTS: Labeling quick failures as breakouts\n\nEXAMPLE: Min Bars = 2\n• Bar 1: Price breaks above ORB High\n• Bar 2: Still above ORB High ✓\n• Bar 3: Returns inside → Now can show retest\n\nIf returned on Bar 2 → Shows 'FAILED BREAK' instead\n\nRECOMMENDATIONS:\n• 1 bar = Aggressive (more signals, more failures)\n• 2 bars = Balanced (recommended) ⭐\n• 3-4 bars = Conservative (only strong moves)\n\nHigher = fewer but stronger breakouts"),
    minPullbackPct=input.float(0.3, "Min Pullback for Re-break (%)", minval=0.1, maxval=2, step=0.1, group=grp_breakout, tooltip="How far price must pull back before detecting new breakout\n\nPREVENTS: Too many signals from small wiggles\n\nEXAMPLE: Last breakout at $10.00\n• Price reaches $10.50\n• Must pull back to $10.35 (0.3% = $0.15) before new breakout counted\n\nRECOMMENDED:\n• 0.3% = Balanced (recommended) ⭐\n• 0.5% = Less sensitive\n• 1.0% = Very selective"),
    enableFVGFilter=input.bool(False, "Enable FVG Filter  | ", group=grp_FVG, inline="fvg1"),
    showFVG=input.bool(True, "Show FVG Boxes", group=grp_FVG, inline="fvg1", tooltip="Fair Value Gap Filter\n\nRequires breakout through FVG for confirmation\n\nFVG = Price gap from strong momentum\nON: Only signals with FVG\nOFF: All signals"),
    maxFVGtoKeep=input.int(5, "Max FVG", minval=1, maxval=20, inline="fvg2", group=grp_FVG),
    fvgProximity=input.float(2.0, "FVG Proximity", minval=0.5, maxval=5.0, inline="fvg2", step=0.5, group=grp_FVG, tooltip="How close to FVG?\n\n1.0 = Must be IN the FVG\n2.0 = Within 2x FVG size (recommended)\n3.0 = Within 3x FVG size (very permissive)"),
    fvgTransparency=input.int(90, "Transparency", minval=0, maxval=100, step=5, inline="fvgcolor", group=grp_FVG),
    fvgBullColor=input.color(color.green, "Bullish FVG", inline="fvgcolor", group=grp_FVG),
    fvgBearColor=input.color(color.orange, "Bearish FVG", inline="fvgcolor", group=grp_FVG),
    enablePullbackFilter=input.bool(False, "Enable Pullback Filter", group=grp_pullback, tooltip="Require pullback confirmation before showing breakout signal\n\nWHY: Filters weak breakouts that reverse immediately\nHOW: Waits for price to pull back slightly, then continue breakout direction\n\nWORKFLOW:\n1. Price breaks above/below ORB\n2. Wait for pullback (small dip/rise)\n3. Price continues in breakout direction\n4. NOW show signal ✅\n\nBENEFITS:\n• Better entry prices\n• Fewer false breakouts\n• Improved risk/reward\n• Confirmation of strength\n\nDRAWBACKS:\n• Misses fast runners\n• Slower signals\n• More conservative\n\nON: Wait for pullback confirmation\nOFF: Immediate signals (current behavior)\n\nRECOMMENDED: Try OFF first, enable if too many false signals"),
    pullbackPercent=input.float(0.3, "Pullback Required (%)", minval=0.1, maxval=2.0, step=0.1, group=grp_pullback, inline="pb", tooltip="How much pullback required for confirmation\n\nEXAMPLE: ORB High = $100, Pullback = 0.5%\n• Breaks to $100.60 (above ORB)\n• Pulls back to $100.10 (0.5% dip) ✓\n• Continues to $100.70 → SIGNAL!\n\nSMALLER % = More signals, faster\nLARGER % = Fewer signals, stronger\n\nRECOMMENDED:\n• 0.3% = Sensitive (active trading) ⭐\n• 0.5% = Balanced\n• 1.0% = Conservative (swing trading)"),
    pullbackTimeout=input.int(10, "Timeout (bars)", minval=3, maxval=30, group=grp_pullback, inline="pb", tooltip="Max bars to wait for pullback\n\nIf pullback doesn't happen within this time:\n→ Shows signal anyway (prevents missing strong moves)\n\nEXAMPLE: Timeout = 10 bars\n• Breakout occurs\n• Wait 10 bars for pullback\n• No pullback? → Show signal at bar 10\n• Pullback at bar 5? → Show signal when continues\n\nSHORTER = Less waiting, more immediate signals\nLONGER = More patient, better confirmation\n\nRECOMMENDED:\n• 5 bars = Quick (5min chart = 25 min)\n• 10 bars = Balanced (5min chart = 50 min) ⭐\n• 15 bars = Patient (5min chart = 75 min)"),
    enableVolumeFilter=input.bool(False, "Enable Volume Filter", group=grp_volume, inline="enable", tooltip="Require volume confirmation for breakout signals\n\nWHY: High volume breakouts are more reliable\nWHAT: Compares current volume to moving average\n\nON: Only shows breakouts with sufficient volume\nOFF: Shows all breakouts regardless of volume\n\nRECOMMENDED: ON for stocks, OFF for crypto"),
    volumeMaLength=input.int(20, "| MA Length", minval=1, group=grp_volume, inline="enable", tooltip="Volume moving average period for comparison\n\nSHORTER = More sensitive to recent volume spikes\nLONGER = Smoother average, less reactive\n\nRECOMMENDATIONS:\n• 10 periods: Very responsive\n• 20 periods: Balanced (recommended) ⭐\n• 50 periods: Long-term average\n\nCHART TIMEFRAME affects calculation:\n• 5min chart, MA=20 → Last 100 minutes\n• 1hour chart, MA=20 → Last 20 hours"),
    volumeMultiplier=input.float(1.5, "Min Volume ×", minval=0.5, step=0.1, group=grp_volume, inline="mult", tooltip="Minimum volume multiplier required for breakout\n\nCURRENT VOLUME must be ≥ (Volume MA × Multiplier)\n\nEXAMPLE: Volume MA = 1M shares, Multiplier = 1.5\n• Breakout with 1.6M volume ✓ Valid\n• Breakout with 1.2M volume ✗ Rejected\n\nRECOMMENDATIONS:\n• 1.0× = Any above-average volume\n• 1.5× = Moderate requirement (recommended) ⭐\n• 2.0× = Strong requirement (fewer signals)\n• 2.5×+ = Very selective\n\nHigher = fewer but higher-quality signals"),
    strongVolumeMultiplier=input.float(2.0, "Strong ×", minval=1.0, step=0.1, group=grp_volume, inline="mult", tooltip="Strong volume override threshold\n\nSPECIAL RULE: If volume exceeds this multiplier:\n→ BYPASSES all other filters (trend, etc.)\n→ Shows breakout immediately\n\nRATIONALE: Massive volume = institutional activity\n\nEXAMPLE: Volume MA = 1M, Strong = 2.0×\n• Breakout with 2.5M volume → Shows even if trend filter says NO\n\nRECOMMENDATIONS:\n• 2.0× = Balanced (recommended) ⭐\n• 2.5× = More selective\n• 3.0× = Only exceptional volume\n\nMUST BE ≥ Min Volume Multiplier"),
    enableTrendFilter=input.bool(False, "Enable Trend Filter", group=grp_trend, inline="FILTER", tooltip="Only show breakouts that align with broader trend\n\nWHY: Trend-aligned breakouts have higher success rate\nWHAT: Checks if price is above/below trend indicator\n\nRULES:\n• UP breakout: Only if price ABOVE trend\n• DOWN breakout: Only if price BELOW trend\n\nON: Filters against-trend breakouts\nOFF: Shows all breakouts\n\nRECOMMENDED: ON for conservative trading"),
    trendMode=input.string("VWAP", "| Trend Mode", inline="FILTER", options=("VWAP", "EMA", "Custom EMA", "SuperTrend", "VWAP+EMA", "VWAP+SuperTrend"), group=grp_trend, tooltip="Method to determine trend direction\n\nVWAP (Volume-Weighted Average Price):\n• Accounts for volume in price calculation\n• Good for: Intraday trading\n• Above VWAP = Bullish, Below = Bearish\n\nEMA (12-period):\n• Fast exponential moving average\n• Responsive to recent price action\n• Good for: Quick trends\n\nCUSTOM EMA:\n• Your own EMA period\n• Longer = Smoother trend\n• Good for: Swing trading (50-200 period)\n\nSUPERTREND:\n• ATR-based trailing stop\n• Clear trend direction\n• Good for: Strong trends\n\nVWAP+EMA:\n• BOTH must agree\n• More conservative\n• Fewer but higher quality signals\n\nVWAP+SUPERTREND:\n• BOTH must agree\n• Most conservative\n• Best signal quality"),
    customEmaLength=input.int(50, "Custom EMA Length", minval=1, group=grp_trend, inline="ema", tooltip="EMA period when Trend Mode = Custom EMA\n\nSHORTER = More reactive, more signals\nLONGER = Smoother, fewer signals\n\nRECOMMENDATIONS:\n• 20-30: Intraday trading\n• 50: Swing trading (recommended) ⭐\n• 100-200: Position trading\n\nIGNORED for other trend modes"),
    supertrendPeriod=input.int(10, "SuperTrend Period", minval=1, group=grp_trend, inline="st", tooltip="ATR period for SuperTrend calculation\n\nSHORTER = More sensitive, tighter stops\nLONGER = Smoother, wider stops\n\nRECOMMENDATIONS:\n• 7: Aggressive\n• 10: Balanced (recommended) ⭐\n• 14: Conservative\n\nONLY USED when Trend Mode includes SuperTrend"),
    supertrendMult=input.float(3.0, "Mult", minval=0.1, step=0.1, group=grp_trend, inline="st", tooltip="ATR multiplier for SuperTrend bands\n\nLOWER = Tighter bands, more trend changes\nHIGHER = Wider bands, fewer changes\n\nRECOMMENDATIONS:\n• 2.0: Sensitive (more signals)\n• 3.0: Balanced (recommended) ⭐\n• 4.0+: Conservative (fewer signals)\n\nONLY USED when Trend Mode includes SuperTrend"),
    enableTargets=input.bool(True, "Enable Targets & Stop-Loss", group=grp_targets, tooltip="Calculate and display profit targets (TP) and stop-loss (SL)\n\nWHEN ENABLED:\n• Shows TP/SL lines on chart during breakout\n• Displays values in dashboard\n• Calculates Risk/Reward ratio\n\nWHEN DISABLED:\n• Only shows ORB levels\n• No trade management\n\nRECOMMENDED: ON for active trading"),
    showTP1=input.bool(True, "TP1 (1R)", group=grp_targets, inline="show"),
    showTP1_5=input.bool(False, "TP1.5 (1.5R)", group=grp_targets, inline="show"),
    showTP2=input.bool(True, "TP2 (2R)", group=grp_targets, inline="show"),
    showTP3=input.bool(False, "TP3 (3R)", group=grp_targets, inline="show", tooltip="Select which Take Profit levels to display\n\nR = RISK UNITS (1R = distance from entry to stop-loss)\n\nTP1 (1R): Conservative target, 1:1 risk/reward\nTP1.5 (1.5R): Intermediate target\nTP2 (2R): Balanced target, 2:1 risk/reward\nTP3 (3R): Aggressive target, 3:1 risk/reward\n\nRECOMMENDED COMBINATIONS:\n• Scalping: TP1 + TP1.5\n• Day Trading: TP1 + TP2 ⭐\n• Swing Trading: TP1 + TP2 + TP3\n\nLines and labels stop updating when last enabled TP is hit"),
    stopMode=input.string("ATR", "Stop Method", options=("ATR", "ORB %", "Swing", "Safer", "Scaled ATR", "% Based", "Smart Adaptive"), group=grp_targets, inline="tgt", tooltip="How to calculate Stop Loss placement\n\n🆕 ATR-BASED VOLATILITY SYSTEM:\n\nSMART ADAPTIVE (Recommended) ⭐:\n• Adjusts to ACTUAL volatility (not price)\n• ATR < 1.5% = Tight stop (0.7× ATR)\n• ATR 1.5-3% = Normal stop (1.0× ATR)\n• ATR > 3% = Wide stop (1.5× ATR)\n• Perfect for: ALL assets automatically\n\nSCALED ATR:\n• Dynamic multiplier based on volatility %\n• Very volatile (>5% ATR): 2.5× ATR\n• High volatility (3-5%): 2.0× ATR\n• Normal (1.5-3%): 1.5× ATR\n• Low (<1.5%): 1.2× ATR\n• Good for: Mixed portfolios\n\nATR:\n• Standard ATR with volatility adjustment\n• Multiplier adjusts to market conditions\n• Formula: SL = Entry ± (ATR × Multiplier × VolAdjust)\n• Good for: Traditional traders\n\n% BASED:\n• Fixed percentage from entry\n• You set the % (e.g., 1.0%)\n• Simple and consistent\n• Good for: Beginners\n\n────────────────────────\n\n🔥 NEW VOLATILITY PROTECTION:\n\nALL METHODS NOW USE ATR-BASED MINIMUMS:\n• Crypto: Min 1.0× ATR (wider for volatility)\n• Forex: Min 0.3× ATR (tighter for stability)\n• Stocks: Min 0.5-1.5× ATR (based on volatility)\n\nABSOLUTE MINIMUMS:\n• Crypto: 1.0% of price\n• Forex: 0.2% of price\n• Stocks: 0.3% of price\n\n────────────────────────\n\nORB %:\n• Fixed percentage beyond ORB level\n• Simple and predictable\n• Formula: SL = ORB_Level ± (ORB_Range × %)\n• Good for: ORB-focused trading\n\nSWING:\n• Placed at recent swing high/low\n• Technical support/resistance\n• Respects chart structure\n• May be far from entry\n• Good for: Technical traders\n\nSAFER:\n• Widest stop of all methods\n• Lowest chance of stop-out\n• Largest potential loss\n• Good for: Risk-averse traders"),
    atrLength=input.int(14, "ATR", minval=5, maxval=50, group=grp_targets, inline="atr2", tooltip="ATR calculation period\n\nATR = Average True Range = How much price moves\n\nSHORTER = More reactive to recent volatility\nLONGER = Smoother, stable average\n\nRECOMMENDATIONS:\n• 7-10: Day trading, responsive\n• 14: Standard, balanced (recommended) ⭐\n• 20-30: Swing trading, smooth\n\nUSED FOR: ATR-based targets and stops"),
    atrMultiplier=input.float(1.5, "×", minval=0.5, maxval=3, step=0.1, group=grp_targets, inline="atr2", tooltip="ATR multiplier for stop-loss distance\n\nSL = Entry ± (ATR × Multiplier)\n\nLOWER = Tighter stop, less risk, more stop-outs\nHIGHER = Wider stop, more risk, fewer stop-outs\n\nRECOMMENDATIONS:\n• 1.0×: Tight stop (aggressive)\n• 1.5×: Balanced (recommended) ⭐\n• 2.0×: Loose stop (conservative)\n• 2.5×+: Very loose (volatile stocks)\n\nONLY AFFECTS: ATR stop method"),
    percentBasedStop=input.float(1.0, "% Based Stop", minval=0.1, maxval=5.0, step=0.1, group=grp_targets, inline="pct", tooltip="Stop Loss percentage from entry\n\nONLY USED when Stop Method = % Based\n\nFORMULA:\n• LONG: SL = Entry × (1 - Stop%)\n• SHORT: SL = Entry × (1 + Stop%)\n\nEXAMPLE: Entry = $100, Stop = 1.0%\n• LONG SL: $99.00 (1% below)\n• SHORT SL: $101.00 (1% above)\n\nRECOMMENDATIONS:\n• 0.5%: Tight (day trading, scalping)\n• 1.0%: Balanced (recommended) ⭐\n• 1.5%: Medium (swing trading)\n• 2.0%+: Wide (position trading)\n\nPERFECT FOR:\n• High-price assets (BTC, TSLA)\n• Consistent risk management\n• Easy to understand"),
    stopOrbFraction=input.float(20, "ORB Stop %", minval=10, maxval=50, step=5, group=grp_targets, inline="stop", tooltip="Stop distance as percentage of ORB range\n\nONLY USED when Stop Method = ORB %\n\nFORMULA:\n• LONG: SL = ORB_Low - (ORB_Range × 20%)\n• SHORT: SL = ORB_High + (ORB_Range × 20%)\n\nEXAMPLE: ORB Range = $1.00, Fraction = 20%\n• SL placed $0.20 beyond ORB boundary\n\nRECOMMENDATIONS:\n• 10-15%: Tight (more stop-outs)\n• 20%: Balanced (recommended) ⭐\n• 30-40%: Loose (fewer stop-outs)\n• 50%: Very loose"),
    swingBars=input.int(3, "Swing Bars", minval=1, maxval=10, group=grp_targets, inline="stop", tooltip="Lookback period to find swing high/low\n\nONLY USED when Stop Method = Swing\n\nSWING = Local high/low point (reversal point)\n\nSHORTER = Recent swing (closer SL)\nLONGER = Deeper swing (farther SL)\n\nEXAMPLE: Swing Bars = 3\n• Looks back 3 bars\n• Finds lowest low (for LONG) or highest high (for SHORT)\n• Places SL there\n\nRECOMMENDATIONS:\n• 2: Very recent swing (aggressive)\n• 3: Recent swing (recommended) ⭐\n• 5: Moderate swing\n• 7-10: Deep swing (conservative)"),
    showTPSLLines=input.bool(True, "Show TP/SL Lines on Chart", group=grp_lines, tooltip="Display Entry, TP, and SL as horizontal lines on chart\n\nWHEN BREAKOUT OCCURS:\n• Lines appear instantly\n• Extend forward as chart progresses\n• Update with each new bar\n\nLINES FREEZE (stop updating) when:\n• Last TP is hit ✓\n• Stop Loss is hit ✗\n• End of Day (if enabled)\n\nCOLORS:\n• Entry: Cyan (LONG) / Orange (SHORT)\n• TP: Green when hit, cyan/orange before\n• SL: Red always\n\nON: Shows lines (recommended)\nOFF: Only dashboard display"),
    freezeOnEOD=input.bool(True, "Freeze Lines at End of Day", group=grp_lines, inline="freeze", tooltip="Stop updating lines when trading session ends\n\nON (Recommended):\n• Lines freeze at session close\n• Keeps intraday setup visible\n• Clean daily reset\n• Good for: ORB strategy (intraday)\n\nOFF:\n• Lines continue extending until hit\n• May cross multiple sessions\n• Good for: Swing trading, 24/7 markets\n\nNOTE: Lines also freeze when SL hit or last TP hit"),
    showDashboard=input.bool(True, "Show Info Panel", group=grp_dash, inline="theme"),
    dashTheme=input.string("Dark", "| Theme", options=("Dark", "Light"), group=grp_dash, inline="theme", tooltip="Dashboard color scheme\n\nDARK (Recommended):\n• Light text on dark background\n• Matches dark chart themes\n• Less eye strain\n• Professional look\n\nLIGHT:\n• Dark text on light background\n• Matches light chart themes\n• Good for presentations\n• High contrast"),
    dashPos=input.string("Bottom Left", "Position", options=("Top Left", "Top Right", "Bottom Left", "Bottom Right", "Middle Right"), group=grp_dash, inline="pos", tooltip="Dashboard placement on chart\n\nTOP LEFT: Good for price action top-right\nTOP RIGHT: Good for price action top-left\nBOTTOM LEFT: Classic placement (recommended) ⭐\nBOTTOM RIGHT: Avoid volume bars\nMIDDLE RIGHT: Floating position\n\nChoose based on where price usually is"),
    dashSize=input.string("Auto", "Text Size", options=("Auto", "Small", "Normal", "Large"), group=grp_dash, inline="pos", tooltip="Text size inside dashboard\n\nAUTO: Adapts to chart zoom (recommended) ⭐\nSMALL: Compact, more screen space\nNORMAL: Readable\nLARGE: Presentations, poor eyesight"),
    showStage=input.bool(True, "Show Stage", group=grp_dash, inline="rows1", tooltip="Display current ORB stage\n\nSHOWS: Which timeframe is active\nâ€¢ ORB 5 (5 minutes)\nâ€¢ ORB 15 (15 minutes)\nâ€¢ ORB 30 (30 minutes)\nâ€¢ ORB 60 (60 minutes)\n\nUseful for knowing which ORB you're trading"),
    showRange=input.bool(True, "Show Range", group=grp_dash, inline="rows1", tooltip="Display ORB range size\n\nSHOWS:\nâ€¢ High-Low difference (dollars)\nâ€¢ Range as percentage\n\nEXAMPLE: '$0.50 (2.5%)'\n\nUseful for assessing if range is significant"),
    showStatus=input.bool(True, "Show Status", group=grp_dash, inline="rows1", tooltip="Display breakout status\n\nSTATES:\nINSIDE RANGE: Price within ORB\nâ€¢ ðŸŸ¢ BREAK UP: Above ORB High\n´ BREAK DOWN: Below ORB Low\nâ€¢ ðŸŸ  RETEST: Returned to ORB after breakout\n\nQuick visual confirmation of position"),
    showVol=input.bool(True, "Show Volume", group=grp_dash, inline="rows2", tooltip="Display volume status\n\nONLY SHOWN when Volume Filter enabled\n\nSHOWS:\nâ€¢ Current volume vs average\nâ€¢ Multiplier (e.g., '1.8x')\nâ€¢ âœ… if above threshold\nâ€¢ âŒ if below threshold\n\nUseful for confirming breakout strength"),
    showTrend=input.bool(True, "Show Trend", group=grp_dash, inline="rows2", tooltip="Display trend direction\n\nONLY SHOWN when Trend Filter enabled\n\nSHOWS:\nâ€¢ Trend direction (UP/DOWN/NEUTRAL)\nâ€¢ Method used (VWAP/EMA/etc.)\nâ€¢ âœ… Aligned / âŒ Against trend\n\nUseful for context"),
    showRisk=input.bool(True, "Show Risk/Reward", group=grp_dash, inline="rows2", tooltip="Display Risk/Reward ratio\n\nSHOWS: Ratio of potential profit to risk\n\nFORMAT: '1:2.5' means:\n• Risk: $100\n• Reward: $250\n\nINDICATORS:\n• ✅ Ratio ≥ 2.0 (good)\n• ⚠️ Ratio 1.5-2.0 (acceptable)\n• ❌ Ratio < 1.5 (poor)\n\nBased on highest enabled TP"),
    showVolatilityMeter=input.bool(True, "Show Volatility Meter", group=grp_dash, inline="rows3", tooltip="Display current market volatility level\n\nMEASURES: ATR as percentage of price\n\nLEVELS:\n🔥🔥🔥 EXTREME (>3%): Very volatile, wider stops needed\n🔥🔥 HIGH (2-3%): Active movement, standard stops\n🔥 MEDIUM (1-2%): Normal trading range\n⚪ LOW (<1%): Quiet market, tight stops possible\n\nUSE FOR:\n• Adjusting position size\n• Setting appropriate stops\n• Understanding market conditions\n\nHigh volatility = Bigger potential moves but more risk"),
    enablePosSizing=input.bool(True, "Calculate Position Size", group=grp_dash, tooltip="Calculate shares to buy based on risk management\n\nCALCULATES:\n• Max shares to buy\n• Position dollar value\n• Risk amount\n• TP profit projections\n• TP allocation splits\n\nWHY:\n• Consistent risk per trade\n• Proper position sizing\n• Prevents over-leveraging\n\nSHOWS: Extra section in dashboard\n\nON: Shows position sizing\nOFF: Only price levels"),
    riskMode=input.string("$ Amount", "Risk", options=("$ Amount", "% of Account"), group=grp_dash, inline="risk", tooltip="How to define your risk per trade\n\n$ AMOUNT:\n• Risk fixed dollar amount\n• Simple and direct\n• Example: '$150 per trade'\n• Good for: Consistent trading\n\n% OF ACCOUNT:\n• Risk percentage of total account\n• Scales with account size\n• Example: '1% of $25,000 = $250'\n• Good for: Account growth\n\nRECOMMENDED: % of Account"),
    fixedRisk=input.float(150, "$", minval=10, maxval=10000, group=grp_dash, inline="risk", tooltip="Fixed dollar amount to risk per trade\n\nONLY USED when Risk Mode = $ Amount\n\nEXAMPLE: Fixed Risk = $150\n• Entry: $10.00\n• Stop: $9.50 (50¢ risk per share)\n• Position: 300 shares ($150 ÷ $0.50)\n• Total position value: $3,000\n\nRECOMMENDATIONS:\n• $50-100: Small accounts\n• $150-300: Medium accounts ⭐\n• $500+: Large accounts"),
    accountSize=input.float(25000, "Account $", minval=1000, group=grp_dash, inline="acct", tooltip="Total trading account size\n\nUSED FOR: Calculating risk percentage\n\nEXAMPLE: Account = $25,000, Risk = 1%\n• Risk per trade = $250\n\nUPDATE THIS:\n• When account grows/shrinks significantly\n• For accurate position sizing\n• Monthly review recommended"),
    riskPct=input.float(0.5, "Risk %", minval=0.1, maxval=5, step=0.1, group=grp_dash, inline="acct", tooltip="Percentage of account to risk per trade\n\nONLY USED when Risk Mode = % of Account\n\nRISK LEVELS:\n• 0.25-0.5%: Very conservative, slow growth\n• 0.5-1%: Balanced (recommended) ⭐\n• 1-2%: Aggressive, faster growth\n• 2-3%: Very aggressive, high risk\n• 3%+: Extreme risk, not recommended\n\nEXAMPLE: Account = $25,000, Risk = 1%\n• Risk per trade = $250\n• Entry: $10, Stop: $9.50 (50¢ risk)\n• Position: 500 shares\n\nRECOMMENDED: 0.5-1% for most traders"),
    maxPositionPct=input.float(25.0, "Max Position %", minval=5, maxval=100, step=5, group=grp_dash, inline="poslimit", tooltip="Maximum position size as % of account\n\nPREVENTS OVER-LEVERAGE when stop is very tight\n\nEXAMPLE: Account = $10,000, Max = 25%\n• Maximum position value = $2,500\n• If stock = $100, max 25 shares\n• Even if risk calculation allows more\n\nRECOMMENDED LEVELS:\n• 10-15%: Very conservative\n• 20-25%: Balanced ⭐\n• 30-50%: Aggressive\n• 50%+: Very aggressive\n\nThis protects against:\n• Tight stops causing huge positions\n• Slippage on large positions\n• Liquidity issues"),
    accountCurrency=input.string("USD", "Account Currency", options=("USD", "EUR", "GBP", "JPY", "INR", "CAD", "AUD", "CHF"), group=grp_dash, inline="currency", tooltip="Currency of your trading account\n\nUSD: U.S. Dollar\nEUR: Euro\nGBP: British Pound\nJPY: Japanese Yen\nINR: Indian Rupee\nCAD: Canadian Dollar\nAUD: Australian Dollar\nCHF: Swiss Franc\n\nIMPORTANT: Affects position sizing calculations\nAll risk and position values are shown in this currency"),
    useDynamicRates=input.bool(True, "Live Exchange Rates", group=grp_dash, inline="exchange", tooltip="Fetch live exchange rates from market data\n\nON: Uses real-time rates from TradingView (recommended)\nOFF: Use manual rate input\n\nNOTE: Live rates may not be available for all pairs"),
    manualRate=input.float(1.0, "/ Or set manual Rate: $1=", minval=0.001, maxval=10000, step=0.1, group=grp_dash, inline="exchange", tooltip="Fallback exchange rate when live rates unavailable\n\nFrom USD to your account currency\n\nEXAMPLES:\n• USD to INR = 83.0\n• USD to EUR = 0.92\n• USD to JPY = 150.0"),
    enableHTF=input.bool(True, "Check Daily Trend", group=grp_htf, tooltip="Check higher timeframe trend before taking breakouts\n\nWHY: Breakouts WITH higher timeframe trend have higher success rate\n\nWHAT IT DOES:\n• Checks daily/4H/weekly trend\n• Shows warning if breakout against trend\n• Displays HTF bias in dashboard\n\nDOES NOT BLOCK signals - only warns you\n\nON: Shows HTF context (recommended for swing traders)\nOFF: Focuses only on intraday ORB"),
    htfTF=input.string("D", "Timeframe", options=("15", "30", "60", "120", "240", "D", "W", "M"), group=grp_htf, inline="htf", tooltip="Higher timeframe to analyze for trend\n\nRECOMMENDED OPTIONS:\n• 15/30/60 min: For 1-5 min charts\n• 240 (4H): For 15-60 min charts\n• D (Daily): For intraday trading ⭐\n• W (Weekly): For swing trading\n• M (Monthly): For position trading\n\nRULE: HTF should be 4-10× your chart timeframe\n\nEXAMPLES:\n• 5min chart → Use 30/60/D\n• 15min chart → Use 60/240/D\n• 1H chart → Use 240/D/W"),
    htfMethod=input.string("Price vs MA", "Method", options=("Price vs MA", "Candle Direction"), group=grp_htf, inline="htf", tooltip="How to determine HTF trend\n\nPRICE VS MA (Recommended):\n• Compares HTF close to moving average\n• Above MA = Bullish\n• Below MA = Bearish\n• Smooth and reliable\n• Less prone to whipsaws\n\nCANDLE DIRECTION:\n• Based on HTF candle color\n• Green candle = Bullish\n• Red candle = Bearish\n• More reactive\n• Can change quickly\n\nRECOMMENDED: Price vs MA for stability"),
    htfEMA=input.int(20, "MA", minval=5, maxval=200, group=grp_htf, inline="htf2", tooltip=""),
    htfMinStrength=input.float(2.0, "Min Distance %", minval=0.0, maxval=10.0, step=0.5, group=grp_htf, inline="htf2", tooltip="Moving average period for HTF trend\n\nONLY USED when Method = Price vs MA\n\nSHORTER = More reactive, frequent changes\nLONGER = Smoother, stable trend\n\nRECOMMENDATIONS:\n• 10-20: Responsive (short-term trend)\n• 20-50: Balanced (recommended) ⭐\n• 50-100: Smooth (intermediate trend)\n• 100-200: Very smooth (long-term trend)\n\nCOMMON CHOICES:\n• Daily TF + 20 EMA: Classic\n• Daily TF + 50 EMA: Swing trading\n• Weekly TF + 20 EMA: Position trading\n\nMinimum distance from MA to consider trend valid\n\nPrice must be at least X% away from MA\n\nLOWER = Accept weak trends\nHIGHER = Only strong trends\n\nRECOMMENDATIONS:\n• 0-1%: Very permissive\n• 1-2%: Balanced ⭐\n• 2-3%: Conservative\n• 3%+: Very selective\n\nHELPS AVOID:\n• Choppy/sideways markets\n• Weak trend signals\n• False breakouts"),
    godModeEnabled=input.bool(True, "Enable GOD MODE", group=grp_god, tooltip="Master switch for the GOD MODE intelligence layer\n\nADDS:\n• Breakout Quality Score (0-100, graded A+ to D) on labels, alerts and dashboard\n• Day Context row: gap vs yesterday + ORB width vs daily ATR\n• Level Confluence: flags ORB levels sitting on PDH/PDL or premarket high/low (🏆)\n• Chop-Day Guard: warns after repeated failed breaks\n• Adaptive breakout buffer scaled by ATR\n\nOFF = classic behavior, exactly as before"),
    godAdaptiveBuffer=input.bool(True, "Adaptive Buffer", group=grp_god, inline="god1", tooltip="Scales the breakout buffer with volatility\n\nEffective buffer = max(Breakout Buffer %, 10% of ATR)\n\nVolatile tickers automatically get a wider buffer (fewer false breakouts); quiet tickers keep the fixed %.\n\nReplaces one-size-fits-all % with per-ticker calibration."),
    godChopGuard=input.bool(True, "Chop-Day Guard", group=grp_god, inline="god1", tooltip="Detects choppy range days\n\n2+ FAILED BREAKS in one session = CHOP DAY:\n• ⚠️ Warning in dashboard\n• Quality Score capped at 40 (C/D)\n\nProtects against the most common ORB failure mode: range-day whipsaws."),
    godShowScore=input.bool(True, "Score on Labels", group=grp_god, inline="god1", tooltip="Appends the Quality Score to breakout labels\n\nExample: ⚡ 87 (A+) 🏆\n\n🏆 = ORB level confluent with PDH/PDL or premarket high/low")
):
    LABEL_OFFSET_ATR_MULTIPLIER: float = 0.8
    LABEL_OFFSET_BARS: int = 2

    MAX_BARS_FAILED_BREAK: int = 5

    tradingSession: str = "0930-1600:23456"
    sessionTimezone: str = syminfo.timezone
    sessionStartHour: Persistent[int] = na(int)
    sessionStartMinute: Persistent[int] = na(int)
    sessionEndHour: Persistent[int] = na(int)
    sessionEndMinute: Persistent[int] = na(int)
    useElectronicFullDay: bool = False

    if sessionMode == 'Auto-Detect':
        if syminfo.type == 'futures':
            tradingSession = ""
        elif syminfo.type == 'stock' or syminfo.type == 'fund' or syminfo.type == 'index' or (syminfo.type == 'dr') or (syminfo.type == 'etf'):
            if enableExtendedHours:
                preMarketStart: str = method_call('get', string.split(extendedPreMarket, '-'), 0)
                afterHoursEnd: str = method_call('get', string.split(extendedAfterHours, '-'), 1)
                tradingSession = preMarketStart + '-' + afterHoursEnd + ':23456'
            else:
                tradingSession = ""
        elif syminfo.type == 'crypto':
            tradingSession = ""
        elif syminfo.type == 'forex':
            tradingSession = ""
        else:
            tradingSession = ""
    elif sessionMode == 'Custom':
        if string.contains(customSession, ':'):
            tradingSession = customSession
        else:
            tradingSession = customSession + ':23456'

    if tradingSession != '':
        sessionTimeOnly: str = method_call('get', string.split(tradingSession, ':'), 0) if string.contains(tradingSession, ':') else tradingSession
        sessionParts: list[str] = string.split(sessionTimeOnly, '-')

        if array.size(sessionParts) == 2:
            startTime: str = array.get(sessionParts, 0)
            endTime: str = array.get(sessionParts, 1)

            if string.length(startTime) == 4:
                sessionStartHour = cast_int(string.tonumber(string.substring(startTime, 0, 2)))
                sessionStartMinute = cast_int(string.tonumber(string.substring(startTime, 2, 4)))

            if string.length(endTime) == 4:
                sessionEndHour = cast_int(string.tonumber(string.substring(endTime, 0, 2)))
                sessionEndMinute = cast_int(string.tonumber(string.substring(endTime, 2, 4)))

    if syminfo.type == 'futures':
        if string.contains(syminfo.ticker, 'ES') or string.contains(syminfo.ticker, 'NQ') or string.contains(syminfo.ticker, 'RTY') or string.contains(syminfo.ticker, 'YM'):
            sessionTimezone = "America/New_York"

            if futuresTradingHours == 'Electronic Full Day (24hr)':
                tradingSession = ""
                useElectronicFullDay = True
            elif futuresTradingHours == 'RTH Only (9:30-16:00)':
                tradingSession = "0930-1600:23456"
                useElectronicFullDay = False
            else:
                currentHour: int = hour(time, sessionTimezone)
                currentMinute: int = minute(time, sessionTimezone)
                outsideRTH: bool = currentHour < 9 or (currentHour == 9 and currentMinute < 30) or currentHour >= 16
                hasVolumeOutsideRTH: bool = outsideRTH and volume > 0

                if hasVolumeOutsideRTH:
                    tradingSession = ""
                    useElectronicFullDay = True
                else:
                    tradingSession = "0930-1600:23456"
                    useElectronicFullDay = False

    symbolCurrency = syminfo.currency

    liveRate: float = na(float)
    currencyPair: str = ""

    if useDynamicRates and accountCurrency != 'USD':
        currencyPair = 'EURUSD' if accountCurrency == 'EUR' else 'GBPUSD' if accountCurrency == 'GBP' else 'USDJPY' if accountCurrency == 'JPY' else 'USDINR' if accountCurrency == 'INR' else 'USDCAD' if accountCurrency == 'CAD' else 'AUDUSD' if accountCurrency == 'AUD' else 'USDCHF' if accountCurrency == 'CHF' else ''

        if currencyPair != '':
            liveRate = request.security(currencyPair, 'D', close, lookahead=barmerge.lookahead_off)

    defaultRate: float = 0.92 if accountCurrency == 'EUR' else 0.79 if accountCurrency == 'GBP' else 150.0 if accountCurrency == 'JPY' else 83.0 if accountCurrency == 'INR' else 1.38 if accountCurrency == 'CAD' else 1.55 if accountCurrency == 'AUD' else 0.9 if accountCurrency == 'CHF' else 1.0
    exchangeRate = 1.0 if accountCurrency == 'USD' else manualRate if not useDynamicRates else defaultRate if na(liveRate) else 1 / liveRate if accountCurrency == 'EUR' or accountCurrency == 'GBP' or accountCurrency == 'AUD' else liveRate

    enableAlerts: bool = True
    alertBreakouts: bool = True
    alertRetests: bool = True
    alertFailedBreaks: bool = True
    alertStageComplete: bool = True
    alertTradeManagement: bool = True

    if breakoutBuffer < 0 or breakoutBuffer > 5:
        runtime.error('❌ Breakout Buffer must be between 0-5%. Current value: ' + string.tostring(breakoutBuffer))
    if minRetestDistancePct < 0.5:
        runtime.error('❌ Min Retest Distance too low. Must be >= 0.5% to prevent false signals. Current: ' + string.tostring(minRetestDistancePct))
    if minBarsOutside < 1:
        runtime.error('❌ Min Bars Outside must be >= 1. Current: ' + string.tostring(minBarsOutside))
    if maxCycles < 1 or maxCycles > 10:
        runtime.error('❌ Max Cycles must be between 1-10. Current: ' + string.tostring(maxCycles))
    if enableVolumeFilter:
        if volumeMultiplier < 0.5:
            runtime.error('❌ Volume Multiplier too low. Must be >= 0.5x. Current: ' + string.tostring(volumeMultiplier))
        if strongVolumeMultiplier < volumeMultiplier:
            runtime.error('❌ Strong Volume Multiplier must be >= Min Volume Multiplier. Strong: ' + string.tostring(strongVolumeMultiplier) + ', Min: ' + string.tostring(volumeMultiplier))
        if volumeMaLength < 1:
            runtime.error('❌ Volume MA Length must be >= 1. Current: ' + string.tostring(volumeMaLength))
    if enableTargets:
        if atrLength < 5 or atrLength > 50:
            runtime.error('❌ ATR Length must be between 5-50. Current: ' + string.tostring(atrLength))
        if atrMultiplier < 0.5 or atrMultiplier > 5:
            runtime.error('❌ ATR Multiplier must be between 0.5-5. Current: ' + string.tostring(atrMultiplier))
        if stopOrbFraction < 10 or stopOrbFraction > 100:
            runtime.error('❌ ORB Stop % must be between 10-100%. Current: ' + string.tostring(stopOrbFraction))
        if swingBars < 1 or swingBars > 20:
            runtime.error('❌ Swing Bars must be between 1-20. Current: ' + string.tostring(swingBars))
    if enablePosSizing:
        if riskMode == '$ Amount' and fixedRisk < 10:
            runtime.error('❌ Fixed Risk too low. Must be >= $10. Current: $' + string.tostring(fixedRisk))
        if riskMode == '% of Account':
            if riskPct < 0.1 or riskPct > 10:
                runtime.error('❌ Risk % must be between 0.1-10%. Current: ' + string.tostring(riskPct) + '%')
            if accountSize < 100:
                runtime.error('❌ Account Size too low. Must be >= $100. Current: $' + string.tostring(accountSize))
    if fillTransparency < 0 or fillTransparency > 100:
        runtime.error('❌ Fill Transparency must be between 0-100%. Current: ' + string.tostring(fillTransparency))
    if enableHTF:
        if htfEMA < 5 or htfEMA > 200:
            runtime.error('❌ HTF EMA period must be between 5-200. Current: ' + string.tostring(htfEMA))
    if enableTrendFilter:
        if customEmaLength < 1 or customEmaLength > 500:
            runtime.error('❌ Custom EMA Length must be between 1-500. Current: ' + string.tostring(customEmaLength))

        if supertrendPeriod < 1 or supertrendPeriod > 50:
            runtime.error('❌ SuperTrend Period must be between 1-50. Current: ' + string.tostring(supertrendPeriod))

        if supertrendMult < 0.1 or supertrendMult > 10:
            runtime.error('❌ SuperTrend Multiplier must be between 0.1-10. Current: ' + string.tostring(supertrendMult))

    useNativeSession: bool = tradingSession == ''

    is24_7Market: bool = syminfo.type == 'crypto' and (useNativeSession or tradingSession == '0000-2359:1234567')

    inSession: Series[bool] = False
    if useNativeSession:
        inSession = not na(time(timeframe.period))
    else:
        if syminfo.type == 'stock' or syminfo.type == 'fund' or syminfo.type == 'index' or (syminfo.type == 'dr') or (syminfo.type == 'etf') or (syminfo.type == 'futures'):
            inSession = not na(time(timeframe.period, tradingSession, sessionTimezone))
        elif syminfo.type == 'crypto':
            if is24_7Market:
                inSession = True
            else:
                inSession = not na(time(timeframe.period, tradingSession, sessionTimezone))
        elif syminfo.type == 'forex':
            inSession = not na(time(timeframe.period, tradingSession, sessionTimezone))
        else:
            inSession = not na(time(timeframe.period, tradingSession, sessionTimezone))

    labH: Persistent[Label] = na(Label)
    labL: Persistent[Label] = na(Label)
    cachedLineColor: Persistent[Color] = na(Color)
    lastLabelH: Persistent[float] = na(float)
    lastLabelL: Persistent[float] = na(float)
    cachedStageName: Persistent[str] = na(str)
    hadSessionToday: Persistent[bool] = False
    hadBreakUp: Persistent[bool] = False
    hadBreakDown: Persistent[bool] = False
    breakUpBar: Persistent[int] = na(int)
    breakDownBar: Persistent[int] = na(int)
    shownBreakUpLabel: Persistent[bool] = False
    shownBreakDownLabel: Persistent[bool] = False
    everHadBreakUp: Persistent[bool] = False
    everHadBreakDown: Persistent[bool] = False
    breakoutEntryPrice: Persistent[float] = na(float)

    cyclesUp: Persistent[int] = 0
    cyclesDown: Persistent[int] = 0

    retestCyclesUp: Persistent[int] = 0
    retestCyclesDown: Persistent[int] = 0

    sessionBreakoutsUp: Persistent[int] = 0
    sessionBreakoutsDown: Persistent[int] = 0
    sessionRetestsUp: Persistent[int] = 0
    sessionRetestsDown: Persistent[int] = 0

    alertMsgRetestUp: Persistent[str] = ""
    alertMsgRetestDown: Persistent[str] = ""
    alertMsgFailedUp: Persistent[str] = ""
    alertMsgFailedDown: Persistent[str] = ""
    alertMsgStageComplete: Persistent[str] = ""

    alertBreakUpTriggered: bool = False
    alertBreakDownTriggered: bool = False
    alertRetestUpTriggered: bool = False
    alertRetestDownTriggered: bool = False
    alertFailedUpTriggered: bool = False
    alertFailedDownTriggered: bool = False
    alertStageCompleteTriggered: bool = False

    alertEntryTriggered: bool = False
    alertSLTriggered: bool = False
    alertTP1Triggered: bool = False
    alertTP1_5Triggered: bool = False
    alertTP2Triggered: bool = False
    alertTP3Triggered: bool = False

    barsOutsideAfterBreakUp: Persistent[int] = 0
    barsOutsideAfterBreakDown: Persistent[int] = 0

    lastBreakUpLabel: Persistent[Label] = na(Label)
    lastBreakDownLabel: Persistent[Label] = na(Label)
    lastLabelStage: Persistent[int] = na(int)

    breakUpBarIndex: Persistent[int] = 0
    breakDownBarIndex: Persistent[int] = 0

    pendingLongEntry: Persistent[bool] = False
    pendingShortEntry: Persistent[bool] = False
    pendingLongBar: Persistent[int] = na(int)
    pendingShortBar: Persistent[int] = na(int)

    breakoutLabels: Persistent[list[Label]] = array.new_label()
    MAX_LABELS_TO_KEEP: int = 10
    tpslLines: Persistent[list[Line]] = array.new_line()
    orbBoxes: Persistent[list[Box]] = array.new_box()
    MAX_LINES_TO_KEEP: int = 20
    MAX_BOXES_TO_KEEP: int = 10

    lastDashUpdateBar: Persistent[int] = -1

    cachedATR: Persistent[float] = na(float)
    cachedATRBar: Persistent[int] = -1
    cachedVolumeMA: Persistent[float] = na(float)
    cachedVolumeMABar: Persistent[int] = -1

    cachedEntry: Persistent[float] = na(float)
    cachedSL: Persistent[float] = na(float)
    cachedTP1: Persistent[float] = na(float)
    cachedTP1_5: Persistent[float] = na(float)
    cachedTP2: Persistent[float] = na(float)
    cachedTP3: Persistent[float] = na(float)
    cachedShares: Persistent[float] = na(float)
    cachedPosValue: Persistent[float] = na(float)
    cachedMaxLoss: Persistent[float] = na(float)
    cachedRiskAmount: Persistent[float] = na(float)

    fvgBoxes: Persistent[list[Box]] = array.new_box()
    fvgTops: Persistent[list[float]] = array.new_float()
    fvgBottoms: Persistent[list[float]] = array.new_float()
    fvgIsBullish: Persistent[list[bool]] = array.new_bool()
    fvgIsActive: Persistent[list[bool]] = array.new_bool()
    fvgStartBar: Persistent[list[int]] = array.new_int()

    hadRetestUp: Persistent[bool] = False
    hadRetestDown: Persistent[bool] = False
    retestUpBar: Persistent[int] = na(int)
    retestDownBar: Persistent[int] = na(int)
    wentFarEnoughUp: Persistent[bool] = False
    wentFarEnoughDown: Persistent[bool] = False
    sessionStartBar: Persistent[int] = na(int)
    sessionStartTime: Persistent[float] = na(float)

    trendVWAP: Persistent[float] = na(float)
    trendEMA12: Persistent[float] = na(float)
    trendEMACustom: Persistent[float] = na(float)
    trendSTUp: Persistent[float] = na(float)
    trendSTDown: Persistent[float] = na(float)
    trendSTDirection: Persistent[int] = 0
    volumeMA: Persistent[float] = na(float)

    htfBullish: Persistent[bool] = False
    htfBearish: Persistent[bool] = False
    htfBiasText: Persistent[str] = ""

    actH: Persistent[float] = na(float)
    actL: Persistent[float] = na(float)
    actM: Persistent[float] = na(float)

    tradeOrbHigh: Persistent[float] = na(float)
    tradeOrbLow: Persistent[float] = na(float)

    haveRange: Persistent[bool] = False
    haveDisplayRange: Persistent[bool] = False

    stage: Persistent[int] = 0
    displayH: Persistent[float] = na(float)
    displayL: Persistent[float] = na(float)

    orbEntryLine: Persistent[Line] = na(Line)
    orbEntryLabel: Persistent[Label] = na(Label)
    orbEntryPrice: Persistent[float] = na(float)
    orbEntryBar: Persistent[int] = na(int)
    orbLineColor: Persistent[Color] = na(Color)
    orbSLLine: Persistent[Line] = na(Line)
    orbSLLabel: Persistent[Label] = na(Label)
    orbSLPrice: Persistent[float] = na(float)
    orbTP1Line: Persistent[Line] = na(Line)
    orbTP1Label: Persistent[Label] = na(Label)
    orbTP1Price: Persistent[float] = na(float)
    orbTP1_5Line: Persistent[Line] = na(Line)
    orbTP1_5Label: Persistent[Label] = na(Label)
    orbTP1_5Price: Persistent[float] = na(float)
    orbTP2Line: Persistent[Line] = na(Line)
    orbTP2Label: Persistent[Label] = na(Label)
    orbTP2Price: Persistent[float] = na(float)
    orbTP3Line: Persistent[Line] = na(Line)
    orbTP3Label: Persistent[Label] = na(Label)
    orbTP3Price: Persistent[float] = na(float)
    orbLinesFrozen: Persistent[bool] = False
    orbTradeDirection: Persistent[int] = 0

    orbTP1Hit: Persistent[bool] = False
    orbTP1_5Hit: Persistent[bool] = False
    orbTP2Hit: Persistent[bool] = False
    orbTP3Hit: Persistent[bool] = False
    orbSLHit: Persistent[bool] = False

    session_wins: Persistent[int] = 0
    session_losses: Persistent[int] = 0
    session_total_rr: Persistent[float] = 0.0
    session_trades: Persistent[int] = 0
    session_best_r: Persistent[float] = 0.0
    session_worst_r: Persistent[float] = 0.0
    trade_closed: Persistent[bool] = False
    last_trade_result: Persistent[str] = ""

    current_trade_r: Persistent[float] = 0.0
    tp1_counted: Persistent[bool] = False
    tp1_5_counted: Persistent[bool] = False
    tp2_counted: Persistent[bool] = False
    tp3_counted: Persistent[bool] = False

    maxShares: Persistent[float] = na(float)
    positionValue: Persistent[float] = na(float)
    maxLoss: Persistent[float] = na(float)

    prevOrbEntryBar: Persistent[int] = na(int)

    dashTable: Persistent[Table] = na(Table)

    prevCyclesUp: Persistent[int] = 0
    prevCyclesDown: Persistent[int] = 0

    orb5Obj: Persistent[ORBData] = ORBData(name='ORB5', minutes=5, high=na, low=na, mid=na, orbRange=na, isEnabled=False, isBuilding=False, isComplete=False, completionBar=0, breakoutUp=False, breakoutDown=False, breakoutBar=0, breakoutLevel=na, cyclesUp=0, cyclesDown=0, orbBox=na, highLine=na, lowLine=na, midLine=na, edgeLabel=na, orbColor=color.blue, lineWidth=1, lineStyle=line.style_solid)
    orb15Obj: Persistent[ORBData] = ORBData(name='ORB15', minutes=15, high=na, low=na, mid=na, orbRange=na, isEnabled=False, isBuilding=False, isComplete=False, completionBar=0, breakoutUp=False, breakoutDown=False, breakoutBar=0, breakoutLevel=na, cyclesUp=0, cyclesDown=0, orbBox=na, highLine=na, lowLine=na, midLine=na, edgeLabel=na, orbColor=color.green, lineWidth=1, lineStyle=line.style_solid)
    orb30Obj: Persistent[ORBData] = ORBData(name='ORB30', minutes=30, high=na, low=na, mid=na, orbRange=na, isEnabled=False, isBuilding=False, isComplete=False, completionBar=0, breakoutUp=False, breakoutDown=False, breakoutBar=0, breakoutLevel=na, cyclesUp=0, cyclesDown=0, orbBox=na, highLine=na, lowLine=na, midLine=na, edgeLabel=na, orbColor=color.orange, lineWidth=1, lineStyle=line.style_solid)
    orb60Obj: Persistent[ORBData] = ORBData(name='ORB60', minutes=60, high=na, low=na, mid=na, orbRange=na, isEnabled=False, isBuilding=False, isComplete=False, completionBar=0, breakoutUp=False, breakoutDown=False, breakoutBar=0, breakoutLevel=na, cyclesUp=0, cyclesDown=0, orbBox=na, highLine=na, lowLine=na, midLine=na, edgeLabel=na, orbColor=color.red, lineWidth=1, lineStyle=line.style_solid)

    activeORB: Persistent[ORBData] = na(ORBData)
    allORBs: Persistent[list[ORBData]] = array.from_items(orb5Obj, orb15Obj, orb30Obj, orb60Obj)
    cachedPrevORBs: Persistent[list[ORBData]] = array.new(4, na(list[ORBData]))
    cachedNextORBs: Persistent[list[ORBData]] = array.new(4, na(list[ORBData]))
    orbNavigationCached: Persistent[bool] = False

    if barstate.isfirst:
        orb5Obj.isEnabled = enableORB5Signals
        orb15Obj.isEnabled = enableORB15Signals
        orb30Obj.isEnabled = enableORB30Signals
        orb60Obj.isEnabled = enableORB60Signals

        orb5Obj.orbColor = orb5LineColor
        orb15Obj.orbColor = orb15LineColor
        orb30Obj.orbColor = orb30LineColor
        orb60Obj.orbColor = orb60LineColor

    def sendAlert(message: str):
        __block_result__ = na
        if enableAlerts:
            __block_result__ = alert(message, alert.freq_once_per_bar_close)
        return __block_result__

    def hasVolumeConfirmation(volMA, mult, strongMult):
        __block_result_1__ = na
        if na(volMA) or volMA == 0:
            __block_result_1__ = True
        else:
            currentVol = volume
            isStrongVolume = strongMult > 0 and currentVol >= volMA * strongMult
            isNormalVolume = currentVol >= volMA * mult
            __block_result_1__ = isStrongVolume or isNormalVolume
        return __block_result_1__

    def calculateTargets(entry, sl, isBullish):
        risk: float = math.abs(entry - sl)
        orbWidth: float = actH - actL

        riskAdjustment: float = 1.0 if entry < 1000 else 0.8 if entry < 5000 else 0.6

        tp1_orb: float = entry + orbWidth * 1.0 if isBullish else entry - orbWidth * 1.0
        tp1_5_orb: float = entry + orbWidth * 1.5 if isBullish else entry - orbWidth * 1.5
        tp2_orb: float = entry + orbWidth * 2.0 if isBullish else entry - orbWidth * 2.0
        tp3_orb: float = entry + orbWidth * 3.0 if isBullish else entry - orbWidth * 3.0

        tp1_risk: float = entry + risk * 1.0 * riskAdjustment if isBullish else entry - risk * 1.0 * riskAdjustment
        tp1_5_risk: float = entry + risk * 1.5 * riskAdjustment if isBullish else entry - risk * 1.5 * riskAdjustment
        tp2_risk: float = entry + risk * 2.0 * riskAdjustment if isBullish else entry - risk * 2.0 * riskAdjustment
        tp3_risk: float = entry + risk * 3.0 * riskAdjustment if isBullish else entry - risk * 3.0 * riskAdjustment

        tp1: float = math.min(tp1_orb, tp1_risk) if isBullish else math.max(tp1_orb, tp1_risk)
        tp1_5: float = math.min(tp1_5_orb, tp1_5_risk) if isBullish else math.max(tp1_5_orb, tp1_5_risk)
        tp2: float = math.min(tp2_orb, tp2_risk) if isBullish else math.max(tp2_orb, tp2_risk)
        tp3: float = math.min(tp3_orb, tp3_risk) if isBullish else math.max(tp3_orb, tp3_risk)

        return (tp1, tp1_5, tp2, tp3)

    def calculateStopLoss(entry, orbHigh, orbLow, orbRange, atr, mode, isBullish):
        sl: float = na(float)
        orbFraction: float = stopOrbFraction / 100

        validATR: float = orbRange * 0.5 if na(atr) or atr == 0 else atr

        atrPercent: float = validATR / entry * 100

        minStopMultiplier: float = 1.0 if syminfo.type == 'crypto' else 0.3 if syminfo.type == 'forex' else 1.5 if atrPercent > 5 else 1.0 if atrPercent > 3 else 0.7 if atrPercent > 1.5 else 0.5

        minStopDistance: float = validATR * minStopMultiplier

        absoluteMin: float = entry * 0.01 if syminfo.type == 'crypto' else entry * 0.002 if syminfo.type == 'forex' else entry * 0.003

        minStopDistance = math.max(minStopDistance, absoluteMin)

        if isBullish:
            if mode == 'ATR':
                priceAdjust: float = 1.0 if entry < 1000 else 0.7 if entry < 5000 else 0.5
                sl = entry - validATR * atrMultiplier * priceAdjust
            elif mode == 'ORB %':
                sl = orbLow - orbRange * orbFraction
            elif mode == 'Swing':
                sl = ta.lowest(low, swingBars)
            elif mode == 'Safer':
                atrSL: float = entry - validATR * atrMultiplier * 2
                swingSL: float = ta.lowest(low, swingBars)
                orbSL: float = orbLow - orbRange * orbFraction * 1.5
                sl = math.min(swingSL, math.min(atrSL, orbSL))
            elif mode == '% Based':
                sl = entry * (1 - percentBasedStop / 100)
            elif mode == 'Smart Adaptive':
                smartMultiplier: float = 1.5 if atrPercent > 3 else 1.0 if atrPercent > 1.5 else 0.7
                atrStop: float = entry - validATR * smartMultiplier
                orbStop: float = orbLow - orbRange * 0.3

                sl = math.min(atrStop, orbStop)
            elif mode == 'Scaled ATR':
                scaledMult: float = 2.5 if atrPercent > 5 else 2.0 if atrPercent > 3 else 1.5 if atrPercent > 1.5 else 1.2
                sl = entry - validATR * scaledMult
        else:
            if mode == 'ATR':
                volAdjust: float = 1.2 if atrPercent > 3 else 1.0 if atrPercent > 1.5 else 0.8
                sl = entry + validATR * atrMultiplier * volAdjust
            elif mode == 'ORB %':
                sl = orbHigh + orbRange * orbFraction
            elif mode == 'Swing':
                sl = ta.highest(high, swingBars)
            elif mode == 'Safer':
                atrSL: float = entry + validATR * atrMultiplier * 2
                swingSL: float = ta.highest(high, swingBars)
                orbSL: float = orbHigh + orbRange * orbFraction * 1.5
                sl = math.max(swingSL, math.max(atrSL, orbSL))
            elif mode == '% Based':
                sl = entry * (1 + percentBasedStop / 100)
            elif mode == 'Smart Adaptive':
                smartMultiplier: float = 1.5 if atrPercent > 3 else 1.0 if atrPercent > 1.5 else 0.7
                atrStop: float = entry + validATR * smartMultiplier
                orbStop: float = orbHigh + orbRange * 0.3
                sl = math.max(atrStop, orbStop)
            elif mode == 'Scaled ATR':
                scaledMult: float = 2.5 if atrPercent > 5 else 2.0 if atrPercent > 3 else 1.5 if atrPercent > 1.5 else 1.2
                sl = entry + validATR * scaledMult

        sl = math.min(sl, entry - minStopDistance) if isBullish else math.max(sl, entry + minStopDistance)

        return sl

    def calculatePositionSize(entry, sl):
        riskAmount: float = 0.0

        if riskMode == '% of Account':
            riskAmount = accountSize * (riskPct / 100)
        else:
            riskAmount = fixedRisk

        if symbolCurrency != accountCurrency:
            riskAmount = riskAmount * exchangeRate

        riskPerShare: float = math.abs(entry - sl)
        sharesFromRisk: float = math.floor(riskAmount / riskPerShare) if riskPerShare > 0 else 0
        maxPositionValue: float = accountSize * (maxPositionPct / 100)

        if symbolCurrency != accountCurrency:
            maxPositionValue = maxPositionValue * exchangeRate

        maxSharesFromLimit: float = math.floor(maxPositionValue / entry) if entry > 0 else 0
        shares: float = math.min(sharesFromRisk, maxSharesFromLimit)
        posValue: float = shares * entry
        shares = math.floor(shares)
        maxLossCalc: float = shares * riskPerShare

        return (shares, posValue, maxLossCalc, riskAmount)

    def calculateTPSplits(show1, show1_5, show2, show3):
        activeCount: int = 0
        if show1:
            activeCount += 1
        if show1_5:
            activeCount += 1
        if show2:
            activeCount += 1
        if show3:
            activeCount += 1

        split1: float = 0.0
        split1_5: float = 0.0
        split2: float = 0.0
        split3: float = 0.0

        if activeCount == 1:
            if show1:
                split1 = 1.0
            elif show1_5:
                split1_5 = 1.0
            elif show2:
                split2 = 1.0
            elif show3:
                split3 = 1.0
        elif activeCount == 2:
            half: float = 0.5
            if show1:
                split1 = half
                if show1_5:
                    split1_5 = half
                elif show2:
                    split2 = half
                elif show3:
                    split3 = half
            elif show1_5:
                split1_5 = half
                if show2:
                    split2 = half
                elif show3:
                    split3 = half
            elif show2:
                split2 = half
                if show3:
                    split3 = half
            elif show3:
                split3 = half
        elif activeCount >= 3:
            remaining: float = 0.5
            remainder: float = remaining / (activeCount - 1)

            firstAssigned: bool = False
            if show1:
                split1 = remainder if firstAssigned else 0.5
                firstAssigned = True
            if show1_5:
                split1_5 = remainder if firstAssigned else 0.5
                firstAssigned = True
            if show2:
                split2 = remainder if firstAssigned else 0.5
                firstAssigned = True
            if show3:
                split3 = remainder if firstAssigned else 0.5
                firstAssigned = True

        return (split1, split1_5, split2, split3)

    def checkHTFBias():
        bullish: bool = False
        bearish: bool = False
        biasText: str = ""
        strength: float = 0.0

        if enableHTF:
            htfClose, htfOpen, htfMA = request.security(syminfo.tickerid, htfTF, (close, open, ta.ema(close, htfEMA)), barmerge.gaps_off, barmerge.lookahead_off)

            if htfMethod == 'Price vs MA':
                distancePct: float = (htfClose - htfMA) / htfMA * 100 if htfMA > 0 else 0
                strength = math.abs(distancePct)

                strongEnough: bool = strength >= htfMinStrength if enableHTF else False

                bullish = htfClose > htfMA and strongEnough
                bearish = htfClose < htfMA and strongEnough
            elif htfMethod == 'Candle Direction':
                bodySize: float = math.abs(htfClose - htfOpen)
                candleRange: float = bodySize / htfClose * 100 if htfClose > 0 else 0
                strength = candleRange

                bullish = htfClose > htfOpen
                bearish = htfClose < htfOpen

            if bullish:
                biasText = '✅✅ Strong Aligned' if strength > htfMinStrength * 2 else '✅ Aligned'
            elif bearish:
                biasText = '⚠️ Strong Counter ⚠️' if strength > htfMinStrength * 2 else '⚠️ Counter-Trend'
            else:
                biasText = "➖ Neutral/Weak"

        return (bullish, bearish, biasText, strength)

    def getBodyHigh():
        return math.max(open, close)

    def getBodyLow():
        return math.min(open, close)

    def bodyClosedAbove(level):
        return getBodyLow() > level

    def bodyClosedBelow(level):
        return getBodyHigh() < level

    currentTF_minutes: float = timeframe.in_seconds() / 60
    needsConfirmation = currentTF_minutes <= 5

    def getBuffer(level, pct):
        return level * (pct / 100)

    def priceRetestFromAbove(level, buffer):
        return getBodyLow() < level + buffer

    def priceRetestFromBelow(level, buffer):
        return getBodyHigh() > level - buffer

    def getLabelSize(sizeStr):
        return size.tiny if sizeStr == 'Tiny' else size.small if sizeStr == 'Small' else size.normal if sizeStr == 'Normal' else size.large if sizeStr == 'Large' else size.huge

    def calcSuperTrend(atrPeriod, multiplier):
        atr = ta.atr(atrPeriod)
        hl2Val = hl2

        basicUpperBand = hl2Val + multiplier * atr
        basicLowerBand = hl2Val - multiplier * atr

        finalUpperBand: PersistentSeries[float] = na(float)
        finalLowerBand: PersistentSeries[float] = na(float)
        trendDir: PersistentSeries[int] = 1

        finalUpperBand = basicUpperBand if na(finalUpperBand[1]) or basicUpperBand < finalUpperBand[1] or close[1] > finalUpperBand[1] else finalUpperBand[1]
        finalLowerBand = basicLowerBand if na(finalLowerBand[1]) or basicLowerBand > finalLowerBand[1] or close[1] < finalLowerBand[1] else finalLowerBand[1]

        trendDir = 1 if na(trendDir[1]) else 1 if close > finalUpperBand[1] else -1 if close < finalLowerBand[1] else trendDir[1]

        return (finalLowerBand, finalUpperBand, trendDir)

    def isTrendUp(mode, closePrice, vwapVal, ema12Val, emaCustomVal, stDir):
        __block_result_2__ = na
        __switch__ = mode
        if __switch__ == "VWAP":
            __block_result_2__ = closePrice > vwapVal
        elif __switch__ == "EMA":
            __block_result_2__ = closePrice > ema12Val
        elif __switch__ == "Custom EMA":
            __block_result_2__ = closePrice > emaCustomVal
        elif __switch__ == "SuperTrend":
            __block_result_2__ = stDir == 1
        elif __switch__ == "VWAP+EMA":
            __block_result_2__ = closePrice > vwapVal and closePrice > ema12Val
        elif __switch__ == "VWAP+SuperTrend":
            __block_result_2__ = closePrice > vwapVal and stDir == 1
        else:
            __block_result_2__ = True
        return __block_result_2__

    def isTrendDown(mode, closePrice, vwapVal, ema12Val, emaCustomVal, stDir):
        __block_result_3__ = na
        __switch__ = mode
        if __switch__ == "VWAP":
            __block_result_3__ = closePrice < vwapVal
        elif __switch__ == "EMA":
            __block_result_3__ = closePrice < ema12Val
        elif __switch__ == "Custom EMA":
            __block_result_3__ = closePrice < emaCustomVal
        elif __switch__ == "SuperTrend":
            __block_result_3__ = stDir == -1
        elif __switch__ == "VWAP+EMA":
            __block_result_3__ = closePrice < vwapVal and closePrice < ema12Val
        elif __switch__ == "VWAP+SuperTrend":
            __block_result_3__ = closePrice < vwapVal and stDir == -1
        else:
            __block_result_3__ = True
        return __block_result_3__

    def isTradingDay():
        isTrading: bool = True

        if syminfo.type == 'stock' or syminfo.type == 'fund' or syminfo.type == 'index' or (syminfo.type == 'dr') or (syminfo.type == 'etf') or (syminfo.type == 'futures'):
            currentDayOfWeek: int = dayofweek(timenow)

            isTrading = currentDayOfWeek >= 2 and currentDayOfWeek <= 6
        elif syminfo.type == 'crypto':
            isTrading = True
        elif syminfo.type == 'forex':
            currentDayOfWeek: int = dayofweek(timenow)

            isTrading = currentDayOfWeek >= 1 and currentDayOfWeek <= 6
        else:
            isTrading = True

        return isTrading

    def isReplayMode():
        isReplay: bool = False

        if barstate.islast:
            timeDiffMinutes: int = cast_int((timenow - time_close) / 60000)

            currentDayOfWeek: int = dayofweek(timenow)
            barDayOfWeek: int = dayofweek(time_close)

            isWeekendNow: bool = currentDayOfWeek == 7 or currentDayOfWeek == 1
            barWasFriday: bool = barDayOfWeek == 6

            if isWeekendNow and barWasFriday:
                isReplay = False
            elif currentDayOfWeek == 2 and barDayOfWeek == 6:
                isReplay = False
            else:
                isReplay = timeDiffMinutes > 1440

        return isReplay

    def isWithinSessionHours():
        withinHours: bool = False

        if useNativeSession:
            withinHours = inSession
        else:
            useReplayTime: bool = isReplayMode()
            timeToCheck: int = time if useReplayTime else timenow

            currentDayOfWeek: int = dayofweek(timeToCheck)
            isTradingDay__0000019f__: bool = currentDayOfWeek >= 2 and currentDayOfWeek <= 6 if syminfo.type == 'stock' else True

            if not isTradingDay__0000019f__ and syminfo.type == 'stock':
                withinHours = False
            elif not na(sessionStartHour) and (not na(sessionEndHour)):
                currentHour: int = hour(timeToCheck)
                currentMinute: int = minute(timeToCheck)

                currentMinutesFromMidnight: int = currentHour * 60 + currentMinute
                sessionStartMinutes: int = sessionStartHour * 60 + sessionStartMinute
                sessionEndMinutes: int = sessionEndHour * 60 + sessionEndMinute

                withinHours = currentMinutesFromMidnight >= sessionStartMinutes and currentMinutesFromMidnight <= sessionEndMinutes

        return withinHours

    def getPreviousEnabledORB(currentOrb: ORBData):
        prevOrb: ORBData = na(ORBData)
        for orb in allORBs:
            if orb.isEnabled and orb.minutes < currentOrb.minutes:
                if na(prevOrb) or orb.minutes > prevOrb.minutes:
                    prevOrb = orb
        return prevOrb

    def getNextEnabledORB(currentOrb: ORBData):
        nextOrb: ORBData = na(ORBData)
        for orb in allORBs:
            if orb.isEnabled and orb.minutes > currentOrb.minutes:
                if na(nextOrb) or orb.minutes < nextOrb.minutes:
                    nextOrb = orb
        return nextOrb

    def cleanupLine(lineObject):
        __block_result_4__ = na
        if not na(lineObject):
            array.push(tpslLines, lineObject)
            __block_result_5__ = na
            if array.size(tpslLines) > MAX_LINES_TO_KEEP:
                oldLine = array.shift(tpslLines)
                __block_result_6__ = na
                if not na(oldLine):
                    __block_result_6__ = line.delete(oldLine)
                __block_result_5__ = __block_result_6__
            __block_result_4__ = __block_result_5__
        return __block_result_4__

    def cleanupLabel(labelObject):
        __block_result_7__ = na
        if not na(labelObject):
            array.push(breakoutLabels, labelObject)
            __block_result_8__ = na
            if array.size(breakoutLabels) > MAX_LABELS_TO_KEEP:
                oldLabel = array.shift(breakoutLabels)
                __block_result_9__ = na
                if not na(oldLabel):
                    __block_result_9__ = label.delete(oldLabel)
                __block_result_8__ = __block_result_9__
            __block_result_7__ = __block_result_8__
        return __block_result_7__

    def cleanupBox(boxObject):
        __block_result_10__ = na
        if not na(boxObject):
            array.push(orbBoxes, boxObject)
            __block_result_11__ = na
            if array.size(orbBoxes) > MAX_BOXES_TO_KEEP:
                oldBox = array.shift(orbBoxes)
                __block_result_12__ = na
                if not na(oldBox):
                    __block_result_12__ = box.delete(oldBox)
                __block_result_11__ = __block_result_12__
            __block_result_10__ = __block_result_11__
        return __block_result_10__

    def detectBullishFVG():
        hasFVG: bool = False
        fvgTop: float = na(float)
        fvgBottom: float = na(float)

        if bar_index >= 2:
            if high[2] < low:
                hasFVG = True
                fvgTop = low
                fvgBottom = high[2]

        return (hasFVG, fvgTop, fvgBottom)

    def detectBearishFVG():
        hasFVG: bool = False
        fvgTop: float = na(float)
        fvgBottom: float = na(float)

        if bar_index >= 2:
            if low[2] > high:
                hasFVG = True
                fvgTop = low[2]
                fvgBottom = high

        return (hasFVG, fvgTop, fvgBottom)

    def hasValidFVGNearLevel(level, isBullish):
        foundFVG: bool = False

        if array.size(fvgTops) > 0:
            for i in pine_range(0, array.size(fvgTops) - 1):
                if array.get(fvgIsBullish, i) == isBullish:
                    fvgTop = array.get(fvgTops, i)
                    fvgBottom = array.get(fvgBottoms, i)
                    fvgSize = fvgTop - fvgBottom

                    expandedTop = fvgTop + fvgSize * fvgProximity
                    expandedBottom = fvgBottom - fvgSize * fvgProximity

                    if level >= expandedBottom and level <= expandedTop:
                        foundFVG = True
                        break

        return foundFVG

    def cleanupOldFVG():
        __block_result_13__ = na
        while array.size(fvgBoxes) > maxFVGtoKeep:
            oldBox = array.shift(fvgBoxes)
            array.shift(fvgTops)
            array.shift(fvgBottoms)
            array.shift(fvgIsBullish)
            array.shift(fvgIsActive)
            array.shift(fvgStartBar)
            __block_result_14__ = na
            if not na(oldBox):
                __block_result_14__ = box.delete(oldBox)
            __block_result_13__ = __block_result_14__
        return __block_result_13__

    def isWithinDisplayHours():
        withinDisplay: bool = False

        useReplayTime: bool = isReplayMode()
        timeToCheck: int = time if useReplayTime else timenow

        if syminfo.type == 'stock' or syminfo.type == 'fund' or syminfo.type == 'index' or (syminfo.type == 'dr') or (syminfo.type == 'etf') or (syminfo.type == 'futures'):
            currentDayOfWeek: int = dayofweek(timeToCheck)
            isTradingDay__000001ef__: bool = currentDayOfWeek >= 2 and currentDayOfWeek <= 6

            if not isTradingDay__000001ef__:
                withinDisplay = False
            else:
                currentHour: int = hour(timeToCheck)
                currentMinute: int = minute(timeToCheck)
                currentMinutesFromMidnight: int = currentHour * 60 + currentMinute

                displayStartMinutes: int = 4 * 60
                displayEndMinutes: int = 20 * 60

                withinDisplay = currentMinutesFromMidnight >= displayStartMinutes and currentMinutesFromMidnight < displayEndMinutes
        elif syminfo.type == 'crypto':
            withinDisplay = True
        elif syminfo.type == 'forex':
            withinDisplay = True
        else:
            withinDisplay = True

        return withinDisplay

    def isInRegularHours():
        inRegular: bool = False

        useReplayTime: bool = isReplayMode()
        timeToCheck: int = time if useReplayTime else timenow

        if syminfo.type == 'stock' or syminfo.type == 'fund' or syminfo.type == 'index' or (syminfo.type == 'dr') or (syminfo.type == 'etf') or (syminfo.type == 'futures'):
            currentDayOfWeek: int = dayofweek(timeToCheck)
            isTradingDay__000001ff__: bool = currentDayOfWeek >= 2 and currentDayOfWeek <= 6

            if not isTradingDay__000001ff__:
                inRegular = False
            else:
                currentHour: int = hour(timeToCheck)
                currentMinute: int = minute(timeToCheck)
                currentMinutesFromMidnight: int = currentHour * 60 + currentMinute

                regularStartMinutes: int = 9 * 60 + 30
                regularEndMinutes: int = 16 * 60

                if not useNativeSession and (not na(sessionStartHour)) and (not na(sessionEndHour)):
                    if enableExtendedHours:
                        regularStartMinutes = 9 * 60 + 30
                        regularEndMinutes = 16 * 60
                    else:
                        regularStartMinutes = sessionStartHour * 60 + sessionStartMinute
                        regularEndMinutes = sessionEndHour * 60 + sessionEndMinute

                inRegular = currentMinutesFromMidnight >= regularStartMinutes and currentMinutesFromMidnight <= regularEndMinutes
        elif syminfo.type == 'crypto':
            inRegular = True
        else:
            inRegular = True

        return inRegular

    isNewSession: bool = False
    isNewDay: bool = False

    if useElectronicFullDay:
        currentHour: int = hour(time, sessionTimezone)
        currentMinute: int = minute(time, sessionTimezone)
        prevHour: int = hour(time[1], sessionTimezone)
        prevMinute: int = minute(time[1], sessionTimezone)

        currentMinutesFromMidnight: int = currentHour * 60 + currentMinute
        prevMinutesFromMidnight: int = prevHour * 60 + prevMinute
        resetTimeMinutes: int = 9 * 60 + 30

        nowAfter930: bool = currentMinutesFromMidnight >= resetTimeMinutes
        prevBefore930: bool = prevMinutesFromMidnight < resetTimeMinutes

        isNewSession = nowAfter930 and prevBefore930
        isNewDay = False
    elif is24_7Market:
        currentDay = dayofmonth(time)
        prevDay = dayofmonth(time[1])
        isNewDay = currentDay != prevDay
        isNewSession = False
    else:
        isNewSession = inSession and (not inSession[1])
        isNewDay = ta.change(dayofweek) != 0

    shouldReset = isNewSession or isNewDay

    if shouldReset:
        hadSessionToday = False

        orbNavigationCached = False
        if shouldReset:
            hadSessionToday = False
            orbNavigationCached = False
            wentFarEnoughUp = False
            wentFarEnoughDown = False

        for i in pine_range(0, array.size(allORBs) - 1):
            orbObj = array.get(allORBs, i)
            if orbObj.minutes == 5:
                orbObj.high = high
                orbObj.low = low
                orbObj.mid = hl2
                orbObj.orbRange = 0
            else:
                orbObj.high = na
                orbObj.low = na
                orbObj.mid = na
                orbObj.orbRange = 0
            orbObj.isBuilding = True
            orbObj.isComplete = False
            orbObj.completionBar = 0
            orbObj.breakoutUp = False
            orbObj.breakoutDown = False
            orbObj.breakoutBar = 0
            orbObj.breakoutLevel = na
            orbObj.cyclesUp = 0
            orbObj.cyclesDown = 0

            if not na(orbObj.orbBox):
                box.delete(orbObj.orbBox)
            if not na(orbObj.highLine):
                line.delete(orbObj.highLine)
            if not na(orbObj.lowLine):
                line.delete(orbObj.lowLine)
            if not na(orbObj.midLine):
                line.delete(orbObj.midLine)
            if not na(orbObj.edgeLabel):
                label.delete(orbObj.edgeLabel)

            orbObj.orbBox = na
            orbObj.highLine = na
            orbObj.lowLine = na
            orbObj.midLine = na
            orbObj.edgeLabel = na

        activeORB = na
        actH = na
        actL = na
        actM = na

        tradeOrbHigh = na
        tradeOrbLow = na

        tradeOrbHigh = na
        tradeOrbLow = na
        haveRange = False
        haveDisplayRange = False
        stage = 0
        displayH = na
        displayL = na
        breakUpBarIndex = 0
        breakDownBarIndex = 0

        cyclesUp = 0
        cyclesDown = 0
        retestCyclesUp = 0
        retestCyclesDown = 0
        barsOutsideAfterBreakUp = 0
        barsOutsideAfterBreakDown = 0
        wentFarEnoughUp = False
        wentFarEnoughDown = False

        sessionBreakoutsUp = 0
        sessionBreakoutsDown = 0
        sessionRetestsUp = 0
        sessionRetestsDown = 0

        session_wins = 0
        session_losses = 0
        session_total_rr = 0.0
        session_trades = 0
        session_best_r = 0.0
        session_worst_r = 0.0
        trade_closed = False
        last_trade_result = ""

        current_trade_r = 0.0
        tp1_counted = False
        tp1_5_counted = False
        tp2_counted = False
        tp3_counted = False

        prevOrbEntryBar = na

        sessionStartBar = na
        sessionStartTime = na

        cachedLineColor = na
        cachedStageName = na

        lastLabelH = na
        lastLabelL = na
        lastLabelStage = na

        if not na(labH):
            label.delete(labH)
            labH = na
        if not na(labL):
            label.delete(labL)
            labL = na

        hadBreakUp = False
        hadBreakDown = False
        breakUpBar = na
        breakDownBar = na
        shownBreakUpLabel = False
        shownBreakDownLabel = False
        everHadBreakUp = False
        everHadBreakDown = False
        breakoutEntryPrice = na
        hadRetestUp = False
        hadRetestDown = False
        retestUpBar = na
        retestDownBar = na
        lastLabelStage = na

        pendingLongEntry = False
        pendingShortEntry = False
        pendingLongBar = na
        pendingShortBar = na

        if not na(orbEntryLine):
            line.delete(orbEntryLine)
            orbEntryLine = na
        if not na(orbEntryLabel):
            label.delete(orbEntryLabel)
            orbEntryLabel = na
        if not na(orbSLLine):
            line.delete(orbSLLine)
            orbSLLine = na
        if not na(orbSLLabel):
            label.delete(orbSLLabel)
            orbSLLabel = na
        if not na(orbTP1Line):
            line.delete(orbTP1Line)
            orbTP1Line = na
        if not na(orbTP1Label):
            label.delete(orbTP1Label)
            orbTP1Label = na
        if not na(orbTP1_5Line):
            line.delete(orbTP1_5Line)
            orbTP1_5Line = na
        if not na(orbTP1_5Label):
            label.delete(orbTP1_5Label)
            orbTP1_5Label = na
        if not na(orbTP2Line):
            line.delete(orbTP2Line)
            orbTP2Line = na
        if not na(orbTP2Label):
            label.delete(orbTP2Label)
            orbTP2Label = na
        if not na(orbTP3Line):
            line.delete(orbTP3Line)
            orbTP3Line = na
        if not na(orbTP3Label):
            label.delete(orbTP3Label)
            orbTP3Label = na

        orbEntryPrice = na
        orbEntryBar = na
        orbLineColor = na
        orbSLPrice = na
        orbTP1Price = na
        orbTP1_5Price = na
        orbTP2Price = na
        orbTP3Price = na
        orbLinesFrozen = False
        orbTP1Hit = False
        orbTP1_5Hit = False
        orbTP2Hit = False
        orbTP3Hit = False
        orbSLHit = False
        orbTradeDirection = 0

        current_trade_r = 0.0
        tp1_counted = False
        tp1_5_counted = False
        tp2_counted = False
        tp3_counted = False

        maxShares = na
        positionValue = na
        maxLoss = na

        lastDashUpdateBar = bar_index - 100

    sessionFirstBarTime: Persistent[float] = na(float)

    if inSession and na(sessionStartTime):
        sessionStartBar = bar_index
        sessionStartTime = time
        sessionFirstBarTime = time
        hadSessionToday = True
    if isNewSession:
        sessionStartBar = bar_index
        sessionStartTime = time
        sessionFirstBarTime = time
        hadSessionToday = True

    minsFromOpen: float = -1.0

    if not na(sessionFirstBarTime) and inSession:
        minsFromOpen = (time - sessionFirstBarTime) / 60000
        if minsFromOpen > 480:
            minsFromOpen = 480
        if minsFromOpen < 0:
            minsFromOpen = 0

    if barstate.isconfirmed or barstate.islast:
        needATR: bool = everHadBreakUp or everHadBreakDown or showDashboard or (not na(activeORB))
        if needATR and bar_index != cachedATRBar:
            cachedATR = ta.atr(atrLength)
            cachedATRBar = bar_index

        if bar_index != cachedVolumeMABar:
            cachedVolumeMA = ta.sma(volume, volumeMaLength)
            cachedVolumeMABar = bar_index

    currentTF_seconds = timeframe.in_seconds()
    isHTF = currentTF_seconds >= 86400

    godPrevDayHigh, godPrevDayLow, godPrevDayClose, godDailyATR = request.security(syminfo.tickerid, 'D', (high[1], low[1], close[1], inline_series(ta.atr(14), 1)), barmerge.gaps_off, barmerge.lookahead_off)

    godPmHigh: Persistent[float] = na(float)
    godPmLow: Persistent[float] = na(float)
    godSessionOpen: Persistent[float] = na(float)
    godFailedBreaks: Persistent[int] = 0
    godLastScore: Persistent[float] = na(float)
    godLastScoreDir: Persistent[str] = ""

    if shouldReset:
        godSessionOpen = open
        godFailedBreaks = 0
        godLastScore = na
        godLastScoreDir = ""

    if godModeEnabled and (not isHTF):
        if ta.change(time('D')) != 0:
            godPmHigh = na
            godPmLow = na
        if not inSession:
            godPmHigh = math.max(nz(godPmHigh, high), high)
            godPmLow = math.min(nz(godPmLow, low), low)

    godGapPct: float = (godSessionOpen - godPrevDayClose) / godPrevDayClose * 100 if godModeEnabled and (not na(godSessionOpen)) and (not na(godPrevDayClose)) and (godPrevDayClose > 0) else na
    godChopDay: bool = godModeEnabled and godChopGuard and (godFailedBreaks >= 2)

    if not isHTF and minsFromOpen >= 0 and (barstate.isconfirmed or barstate.islast) and inSession:
        for i in pine_range(0, array.size(allORBs) - 1):
            orbObj = array.get(allORBs, i)

            if orbObj.isEnabled and orbObj.isBuilding:
                if minsFromOpen > orbObj.minutes:
                    orbObj.isBuilding = False
                    orbObj.isComplete = True
                    orbObj.completionBar = bar_index

                    if na(activeORB) or orbObj.minutes > activeORB.minutes:
                        activeORB = orbObj
                        actH = orbObj.high
                        actL = orbObj.low
                        actM = orbObj.mid
                        haveRange = True
                        haveDisplayRange = True
                        stage = orbObj.minutes
                        displayH = orbObj.high
                        displayL = orbObj.low
                        cachedStageName = orbObj.name
                        cachedLineColor = orbObj.orbColor
                else:
                    if na(orbObj.high):
                        prevOrb = getPreviousEnabledORB(orbObj)
                        if not na(prevOrb) and prevOrb.isComplete:
                            orbObj.high = prevOrb.high
                            orbObj.low = prevOrb.low
                            orbObj.mid = prevOrb.mid
                            orbObj.orbRange = prevOrb.orbRange

                    if minsFromOpen < orbObj.minutes:
                        orbObj.high = math.max(nz(orbObj.high, high), high)
                        orbObj.low = math.min(nz(orbObj.low, low), low)
                        orbObj.mid = (orbObj.high + orbObj.low) / 2
                        orbObj.orbRange = orbObj.high - orbObj.low

                        if minsFromOpen >= orbObj.minutes - 1 and (not orbObj.isComplete):
                            orbObj.isBuilding = False
                            orbObj.isComplete = True
                            orbObj.completionBar = bar_index

                            activeORB = orbObj

                            actH = orbObj.high
                            actL = orbObj.low
                            actM = orbObj.mid
                            haveRange = True
                            haveDisplayRange = True

                            stage = orbObj.minutes
                            displayH = orbObj.high
                            displayL = orbObj.low
                            cachedStageName = orbObj.name
                            cachedLineColor = orbObj.orbColor

    if not orbNavigationCached and (not isHTF):
        for i in pine_range(0, array.size(allORBs) - 1):
            orbObj = array.get(allORBs, i)

            prevOrb: ORBData = na(ORBData)
            for j in pine_range(0, array.size(allORBs) - 1):
                checkOrb = array.get(allORBs, j)
                if checkOrb.isEnabled and checkOrb.minutes < orbObj.minutes:
                    if na(prevOrb) or checkOrb.minutes > prevOrb.minutes:
                        prevOrb = checkOrb
            array.set(cachedPrevORBs, i, prevOrb)

            nextOrb: ORBData = na(ORBData)
            for j in pine_range(0, array.size(allORBs) - 1):
                checkOrb = array.get(allORBs, j)
                if checkOrb.isEnabled and checkOrb.minutes > orbObj.minutes:
                    if na(nextOrb) or checkOrb.minutes < nextOrb.minutes:
                        nextOrb = checkOrb
            array.set(cachedNextORBs, i, nextOrb)

        orbNavigationCached = True

    for i in pine_range(0, array.size(allORBs) - 1):
        orbObj = array.get(allORBs, i)
        if orbObj.isEnabled and orbObj.isComplete and (orbObj.completionBar == bar_index):
            rangeSize = orbObj.high - orbObj.low
            rangePct = rangeSize / orbObj.low * 100
            alertMsgStageComplete = '✅ ' + orbObj.name + ' COMPLETE - ' + syminfo.ticker + ' | Range: $' + string.tostring(orbObj.high, '#.##') + ' - $' + string.tostring(orbObj.low, '#.##') + ' (' + string.tostring(rangePct, '#.#') + '%)'
            sendAlert(alertMsgStageComplete)
            alertStageCompleteTriggered = True

    if enableTrendFilter:
        if string.contains(trendMode, 'VWAP'):
            trendVWAP = ta.vwap(close)

        if trendMode == 'EMA' or trendMode == 'VWAP+EMA':
            trendEMA12 = ta.ema(close, 12)

        if trendMode == 'Custom EMA':
            trendEMACustom = ta.ema(close, customEmaLength)

        if string.contains(trendMode, 'SuperTrend'):
            if barstate.isnew or na(trendSTUp):
                stLower, stUpper, stDir = calcSuperTrend(supertrendPeriod, supertrendMult)
                trendSTUp = stLower
                trendSTDown = stUpper
                trendSTDirection = stDir

    def f_nearLvl(lvl, ref, tol):
        return not na(lvl) and (not na(ref)) and (math.abs(lvl - ref) <= tol)

    def f_godGrade(s):
        return 'A+' if s >= 85 else 'A' if s >= 70 else 'B' if s >= 55 else 'C' if s >= 40 else 'D'

    godLvlTol: float = nz(cachedATR) * 0.25
    godHighConfluence: bool = godModeEnabled and haveRange and (f_nearLvl(actH, godPrevDayHigh, godLvlTol) or f_nearLvl(actH, godPmHigh, godLvlTol))
    godLowConfluence: bool = godModeEnabled and haveRange and (f_nearLvl(actL, godPrevDayLow, godLvlTol) or f_nearLvl(actL, godPmLow, godLvlTol))

    def f_godScore(isUp: bool):
        score: float = 50.0
        volRatio: float = volume / cachedVolumeMA if nz(cachedVolumeMA) > 0 else 1.0
        score += 20 if volRatio >= strongVolumeMultiplier else 12 if volRatio >= volumeMultiplier else 4 if volRatio >= 1.0 else -10
        score += (15 if htfBullish else -15 if htfBearish else 0) if isUp else 15 if htfBearish else -15 if htfBullish else 0
        orVsAtr: float = activeORB.orbRange / godDailyATR if not na(godDailyATR) and godDailyATR > 0 and (not na(activeORB)) else na
        score += 0 if na(orVsAtr) else 10 if orVsAtr <= 0.25 else 5 if orVsAtr <= 0.5 else 0 if orVsAtr <= 0.75 else -10
        gapAligned: float = na if na(godGapPct) else godGapPct if isUp else -godGapPct
        score += 0 if na(gapAligned) else 8 if gapAligned >= 0.5 else -8 if gapAligned <= -0.5 else 0
        score += 12 if (godHighConfluence if isUp else godLowConfluence) else 0
        priorBreaks: int = (sessionBreakoutsUp if isUp else sessionBreakoutsDown) - 1
        score -= math.min(math.max(priorBreaks, 0) * 5, 15)
        if godChopDay:
            score = math.min(score, 40)
        return math.max(0.0, math.min(100.0, score))

    canDetectBreakout = not isHTF and enableBreakout and (not na(activeORB)) and barstate.isconfirmed
    volumeMA = cachedVolumeMA

    pendingLongDue: bool = pendingLongEntry and bar_index > pendingLongBar
    pendingShortDue: bool = pendingShortEntry and bar_index > pendingShortBar
    entryIsLong: bool = pendingLongDue and (not pendingShortDue)

    if pendingLongDue or pendingShortDue:
        if enableTargets:
            activeHigh: float = activeORB.high if not na(activeORB) else na
            activeLow: float = activeORB.low if not na(activeORB) else na

            if not na(activeHigh) and (not na(activeLow)):
                if not na(orbEntryLine):
                    line.delete(orbEntryLine)
                    orbEntryLine = na
                if not na(orbEntryLabel):
                    label.delete(orbEntryLabel)
                    orbEntryLabel = na
                if not na(orbSLLine):
                    line.delete(orbSLLine)
                    orbSLLine = na
                if not na(orbSLLabel):
                    label.delete(orbSLLabel)
                    orbSLLabel = na
                if not na(orbTP1Line):
                    line.delete(orbTP1Line)
                    orbTP1Line = na
                if not na(orbTP1Label):
                    label.delete(orbTP1Label)
                    orbTP1Label = na
                if not na(orbTP1_5Line):
                    line.delete(orbTP1_5Line)
                    orbTP1_5Line = na
                if not na(orbTP1_5Label):
                    label.delete(orbTP1_5Label)
                    orbTP1_5Label = na
                if not na(orbTP2Line):
                    line.delete(orbTP2Line)
                    orbTP2Line = na
                if not na(orbTP2Label):
                    label.delete(orbTP2Label)
                    orbTP2Label = na
                if not na(orbTP3Line):
                    line.delete(orbTP3Line)
                    orbTP3Line = na
                if not na(orbTP3Label):
                    label.delete(orbTP3Label)
                    orbTP3Label = na

                entry__00000328__: float = open
                atr__00000328__: float = cachedATR
                sl__00000328__: float = calculateStopLoss(entry__00000328__, activeHigh, activeLow, activeHigh - activeLow, atr__00000328__, stopMode, entryIsLong)
                tp1__00000328__, tp1_5__00000328__, tp2__00000328__, tp3__00000328__ = calculateTargets(entry__00000328__, sl__00000328__, entryIsLong)

                shares, posValue, maxLossCalc, riskAmount = calculatePositionSize(entry__00000328__, sl__00000328__)

                orbEntryPrice = entry__00000328__
                breakoutEntryPrice = entry__00000328__
                orbEntryBar = bar_index
                orbLineColor = color.new(color.aqua, 0) if entryIsLong else color.new(color.orange, 0)
                orbSLPrice = sl__00000328__
                orbTP1Price = tp1__00000328__
                orbTP1_5Price = tp1_5__00000328__
                orbTP2Price = tp2__00000328__
                orbTP3Price = tp3__00000328__
                orbLinesFrozen = False
                orbTP1Hit = False
                orbTP1_5Hit = False
                orbTP2Hit = False
                orbTP3Hit = False
                orbSLHit = False
                orbTradeDirection = 1 if entryIsLong else -1

                maxShares = shares
                positionValue = posValue
                maxLoss = maxLossCalc

                orbEntryLine = line.new(orbEntryBar, orbEntryPrice, bar_index, orbEntryPrice, xloc=xloc.bar_index, extend=extend.none, color=orbLineColor, width=1, style=line.style_solid)
                cleanupLine(orbEntryLine)
                entryText: str = 'ENTRY' if labelFormat == 'Simple' else string.format('ENTRY: ${0}', string.tostring(orbEntryPrice, '#.##'))
                orbEntryLabel = label.new(orbEntryBar, orbEntryPrice, entryText, xloc=xloc.bar_index, style=label.style_label_left, textcolor=color.white, color=orbLineColor, size=getLabelSize(labelSize))

                if showTPSLLines:
                    orbSLLine = line.new(orbEntryBar, orbSLPrice, bar_index, orbSLPrice, xloc=xloc.bar_index, extend=extend.none, color=color.new(color.red, 0), width=1, style=line.style_solid)
                    cleanupLine(orbSLLine)
                    slText: str = 'SL' if labelFormat == 'Simple' else string.format('SL: ${0}', string.tostring(orbSLPrice, '#.##'))
                    orbSLLabel = label.new(orbEntryBar, orbSLPrice, slText, xloc=xloc.bar_index, style=label.style_label_left, textcolor=color.white, color=color.new(color.red, 0), size=getLabelSize(labelSize))

                    if showTP1:
                        orbTP1Line = line.new(orbEntryBar, orbTP1Price, bar_index, orbTP1Price, xloc=xloc.bar_index, extend=extend.none, color=color.new(color.green, 0), width=1, style=line.style_solid)
                        cleanupLine(orbTP1Line)
                        tp1Pct: float = (orbTP1Price - entry__00000328__ if entryIsLong else entry__00000328__ - orbTP1Price) / entry__00000328__ * 100
                        tp1Text: str = 'TP1' if labelFormat == 'Simple' else string.format('TP1: ${0} +{1}%', string.tostring(orbTP1Price, '#.##'), string.tostring(tp1Pct, '#.#'))
                        orbTP1Label = label.new(orbEntryBar, orbTP1Price, tp1Text, xloc=xloc.bar_index, style=label.style_label_left, textcolor=color.white, color=color.new(color.green, 0), size=getLabelSize(labelSize))

                    if showTP1_5:
                        orbTP1_5Line = line.new(orbEntryBar, orbTP1_5Price, bar_index, orbTP1_5Price, xloc=xloc.bar_index, extend=extend.none, color=color.new(color.green, 0), width=1, style=line.style_solid)
                        cleanupLine(orbTP1_5Line)
                        tp1_5Pct: float = (orbTP1_5Price - entry__00000328__ if entryIsLong else entry__00000328__ - orbTP1_5Price) / entry__00000328__ * 100
                        tp1_5Text: str = 'TP1.5' if labelFormat == 'Simple' else string.format('TP1.5: ${0} +{1}%', string.tostring(orbTP1_5Price, '#.##'), string.tostring(tp1_5Pct, '#.#'))
                        orbTP1_5Label = label.new(orbEntryBar, orbTP1_5Price, tp1_5Text, xloc=xloc.bar_index, style=label.style_label_left, textcolor=color.white, color=color.new(color.green, 0), size=getLabelSize(labelSize))

                    if showTP2:
                        orbTP2Line = line.new(orbEntryBar, orbTP2Price, bar_index, orbTP2Price, xloc=xloc.bar_index, extend=extend.none, color=color.new(color.green, 0), width=1, style=line.style_solid)
                        cleanupLine(orbTP2Line)
                        tp2Pct: float = (orbTP2Price - entry__00000328__ if entryIsLong else entry__00000328__ - orbTP2Price) / entry__00000328__ * 100
                        tp2Text: str = 'TP2' if labelFormat == 'Simple' else string.format('TP2: ${0} +{1}%', string.tostring(orbTP2Price, '#.##'), string.tostring(tp2Pct, '#.#'))
                        orbTP2Label = label.new(orbEntryBar, orbTP2Price, tp2Text, xloc=xloc.bar_index, style=label.style_label_left, textcolor=color.white, color=color.new(color.green, 0), size=getLabelSize(labelSize))

                    if showTP3:
                        orbTP3Line = line.new(orbEntryBar, orbTP3Price, bar_index, orbTP3Price, xloc=xloc.bar_index, extend=extend.none, color=color.new(color.green, 0), width=1, style=line.style_solid)
                        cleanupLine(orbTP3Line)
                        tp3Pct: float = (orbTP3Price - entry__00000328__ if entryIsLong else entry__00000328__ - orbTP3Price) / entry__00000328__ * 100
                        tp3Text: str = 'TP3' if labelFormat == 'Simple' else string.format('TP3: ${0} +{1}%', string.tostring(orbTP3Price, '#.##'), string.tostring(tp3Pct, '#.#'))
                        orbTP3Label = label.new(orbEntryBar, orbTP3Price, tp3Text, xloc=xloc.bar_index, style=label.style_label_left, textcolor=color.white, color=color.new(color.green, 0), size=getLabelSize(labelSize))

        alertEntryTriggered = True

        if pendingLongDue:
            pendingLongEntry = False
            pendingLongBar = na
        if pendingShortDue:
            pendingShortEntry = False
            pendingShortBar = na

    bullFVG, bullTop, bullBottom = detectBullishFVG()
    bearFVG, bearTop, bearBottom = detectBearishFVG()

    if bullFVG and showFVG and (not na(activeORB)):
        fvgBox = box.new(left=bar_index - 2, top=bullTop, right=bar_index, bottom=bullBottom, border_color=color.new(fvgBullColor, 0), bgcolor=color.new(fvgBullColor, fvgTransparency), border_width=1, extend=extend.none)
        array.push(fvgBoxes, fvgBox)
        array.push(fvgTops, bullTop)
        array.push(fvgBottoms, bullBottom)
        array.push(fvgIsBullish, True)
        array.push(fvgIsActive, True)
        array.push(fvgStartBar, bar_index - 2)
        cleanupOldFVG()

    if bearFVG and showFVG and (not na(activeORB)):
        fvgBox = box.new(left=bar_index - 2, top=bearTop, right=bar_index, bottom=bearBottom, border_color=color.new(fvgBearColor, 0), bgcolor=color.new(fvgBearColor, fvgTransparency), border_width=1, extend=extend.none)
        array.push(fvgBoxes, fvgBox)
        array.push(fvgTops, bearTop)
        array.push(fvgBottoms, bearBottom)
        array.push(fvgIsBullish, False)
        array.push(fvgIsActive, True)
        array.push(fvgStartBar, bar_index - 2)
        cleanupOldFVG()

    if showFVG and array.size(fvgBoxes) > 0 and (barstate.isnew or barstate.islast):
        for i in pine_range(0, array.size(fvgBoxes) - 1):
            if array.get(fvgIsActive, i):
                fvgTop = array.get(fvgTops, i)
                fvgBottom = array.get(fvgBottoms, i)
                isBull = array.get(fvgIsBullish, i)
                startBar = array.get(fvgStartBar, i)
                currentBox = array.get(fvgBoxes, i)
                boxColor = fvgBullColor if isBull else fvgBearColor

                fvgFilled: bool = False
                if isBull:
                    fvgFilled = close < fvgBottom
                else:
                    fvgFilled = close > fvgTop

                if not na(currentBox):
                    if fvgFilled:
                        box.set_right(currentBox, bar_index)
                        box.set_border_style(currentBox, line.style_dashed)
                        array.set(fvgIsActive, i, False)

                        if bar_index - array.get(fvgStartBar, i) > 10:
                            box.delete(currentBox)
                            array.set(fvgBoxes, i, na)
                    else:
                        box.set_right(currentBox, bar_index)

    if not na(activeORB) and activeORB.isComplete and inSession and enableBreakout and barstate.isconfirmed:
        activeHigh = activeORB.high
        activeLow = activeORB.low
        activeMid: float = activeORB.mid

        effBreakoutBuffer: float = math.max(breakoutBuffer, cachedATR * 0.1 / close * 100) if godModeEnabled and godAdaptiveBuffer and (nz(cachedATR) > 0) and (close > 0) else breakoutBuffer
        activeBufferUp = getBuffer(activeHigh, effBreakoutBuffer)
        activeBufferDown = getBuffer(activeLow, effBreakoutBuffer)

        volumeOK = not enableVolumeFilter or hasVolumeConfirmation(volumeMA, volumeMultiplier, strongVolumeMultiplier)

        trendOK_Up = not enableTrendFilter or isTrendUp(trendMode, close, trendVWAP, trendEMA12, trendEMACustom, trendSTDirection)
        trendOK_Down = not enableTrendFilter or isTrendDown(trendMode, close, trendVWAP, trendEMA12, trendEMACustom, trendSTDirection)

        crossedAbove = close > activeHigh + activeBufferUp and close[1] <= activeHigh + activeBufferUp
        if crossedAbove and volumeOK and trendOK_Up and (not activeORB.breakoutUp):
            activeORB.breakoutUp = True
            activeORB.breakoutBar = bar_index
            activeORB.breakoutLevel = activeHigh
            activeORB.cyclesUp = activeORB.cyclesUp + 1
            cyclesUp = cyclesUp + 1
            hadRetestUp = False
            wentFarEnoughUp = False

            sessionBreakoutsUp = sessionBreakoutsUp + 1
            if godModeEnabled:
                godLastScore = f_godScore(True)
                godLastScoreDir = "UP"

            everHadBreakUp = True
            hadBreakUp = True
            breakUpBar = bar_index
            breakUpBarIndex = bar_index

            tradeOrbHigh = activeORB.high
            tradeOrbLow = activeORB.low

            if showBreakLabels:
                breakText: str = ""
                if labelFormat == 'Simple':
                    breakText = '🔼 BREAKOUT UP #' + string.tostring(sessionBreakoutsUp)
                else:
                    volRatio: float = volume / volumeMA if volumeMA > 0 else 0
                    volText: str = string.tostring(volRatio, '#.#') + 'x ⚡' if volRatio >= strongVolumeMultiplier else string.tostring(volRatio, '#.#') + 'x' if volRatio >= volumeMultiplier else string.tostring(volRatio, '#.#') + 'x ⚠️'
                    breakText = '🔼 BREAKOUT UP\n' + activeORB.name + ' #' + string.tostring(sessionBreakoutsUp) + '\nVol: ' + volText
                if godModeEnabled and godShowScore and (not na(godLastScore)):
                    breakText += '\n⚡ ' + string.tostring(godLastScore, '#') + ' (' + f_godGrade(godLastScore) + ')' + (' 🏆' if godHighConfluence else '')

                labelOffset: float = cachedATR * LABEL_OFFSET_ATR_MULTIPLIER
                labelY: float = high + labelOffset

                breakLabel = label.new(bar_index, labelY, breakText, color=color.new(color.green, 0), textalign=text.align_center, style=label.style_label_down, textcolor=color.white, size=getLabelSize(labelSize))
                cleanupLabel(breakLabel)

            if enableAlerts and alertBreakouts:
                alertMsg = '🔼 BREAKOUT UP' + string.tostring(sessionBreakoutsUp) + ' - ' + syminfo.ticker + ' @ ' + string.tostring(close, '#.##') + ' | ' + activeORB.name + (' | ⚡' + string.tostring(godLastScore, '#') + ' ' + f_godGrade(godLastScore) if godModeEnabled and (not na(godLastScore)) else '')
                sendAlert(alertMsg)
                alertBreakUpTriggered = True

            pendingLongEntry = True
            pendingLongBar = bar_index

        crossedBelow = close < activeLow - activeBufferDown and close[1] >= activeLow - activeBufferDown

        if crossedBelow and volumeOK and trendOK_Down and (not activeORB.breakoutDown):
            activeORB.breakoutDown = True
            activeORB.breakoutBar = bar_index
            activeORB.breakoutLevel = activeLow
            activeORB.cyclesDown = activeORB.cyclesDown + 1
            cyclesDown = cyclesDown + 1
            hadRetestDown = False
            wentFarEnoughDown = False

            sessionBreakoutsDown = sessionBreakoutsDown + 1
            if godModeEnabled:
                godLastScore = f_godScore(False)
                godLastScoreDir = "DOWN"

            everHadBreakDown = True
            hadBreakDown = True
            breakDownBar = bar_index
            breakDownBarIndex = bar_index

            tradeOrbHigh = activeORB.high
            tradeOrbLow = activeORB.low

            if showBreakLabels:
                breakText: str = ""
                if labelFormat == 'Simple':
                    breakText = '🔽 BREAKOUT DOWN #' + string.tostring(sessionBreakoutsDown)
                else:
                    volRatio: float = volume / volumeMA if volumeMA > 0 else 0
                    volText: str = string.tostring(volRatio, '#.#') + 'x ⚡' if volRatio >= strongVolumeMultiplier else string.tostring(volRatio, '#.#') + 'x' if volRatio >= volumeMultiplier else string.tostring(volRatio, '#.#') + 'x ⚠️'
                    breakText = '🔽 BREAKOUT DOWN\n' + activeORB.name + ' | #' + string.tostring(sessionBreakoutsDown) + '\nVol: ' + volText
                if godModeEnabled and godShowScore and (not na(godLastScore)):
                    breakText += '\n⚡ ' + string.tostring(godLastScore, '#') + ' (' + f_godGrade(godLastScore) + ')' + (' 🏆' if godLowConfluence else '')

                labelOffset: float = cachedATR * LABEL_OFFSET_ATR_MULTIPLIER
                labelY: float = low - labelOffset

                breakLabel = label.new(bar_index, labelY, breakText, color=color.new(color.red, 0), style=label.style_label_up, textalign=text.align_center, textcolor=color.white, size=getLabelSize(labelSize))
                cleanupLabel(breakLabel)

            if enableAlerts and alertBreakouts:
                alertMsg = '🔽 BREAKOUT DOWN #' + string.tostring(sessionBreakoutsDown) + ' - ' + syminfo.ticker + ' @ ' + string.tostring(close, '#.##') + ' | ' + activeORB.name + (' | ⚡' + string.tostring(godLastScore, '#') + ' ' + f_godGrade(godLastScore) if godModeEnabled and (not na(godLastScore)) else '')
                sendAlert(alertMsg)
                alertBreakDownTriggered = True

            pendingShortEntry = True
            pendingShortBar = bar_index

    if not isHTF and barstate.isconfirmed:
        if hadBreakUp and bar_index > breakUpBarIndex:
            if close > tradeOrbHigh:
                barsOutsideAfterBreakUp += 1

                minRetestDistance = tradeOrbHigh * (minRetestDistancePct / 100)
                if close > tradeOrbHigh + minRetestDistance:
                    wentFarEnoughUp = True
            else:
                barsOutsideAfterBreakUp = 0

        if hadBreakDown and bar_index > breakDownBarIndex:
            if close < tradeOrbLow:
                barsOutsideAfterBreakDown += 1

                minRetestDistance = tradeOrbLow * (minRetestDistancePct / 100)
                if close < tradeOrbLow - minRetestDistance:
                    wentFarEnoughDown = True
            else:
                barsOutsideAfterBreakDown = 0

    if not isHTF and enableRetest and haveRange and barstate.isconfirmed:
        retestBufferCalc = getBuffer(actH, retestBuffer)

        if hadBreakUp and (not hadRetestUp):
            wentFarEnough = wentFarEnoughUp

            isCommittedBreakout = barsOutsideAfterBreakUp >= minBarsOutside

            priceBackInside = close < tradeOrbHigh + retestBufferCalc and close > tradeOrbLow - retestBufferCalc

            barsSinceBreak = bar_index - breakUpBarIndex
            isFailedBreak = everHadBreakUp and barsSinceBreak > 0 and (barsSinceBreak <= MAX_BARS_FAILED_BREAK) and priceBackInside and (not isCommittedBreakout)
            if isFailedBreak:
                if not na(lastBreakUpLabel):
                    label.set_text(lastBreakUpLabel, '⚠️ FAILED BREAK')
                    label.set_color(lastBreakUpLabel, color.new(color.orange, 0))

                if alertFailedBreaks:
                    orbStageName = activeORB.name if not na(activeORB) else 'None'
                    alertMsgFailedUp = '⚠️ FAILED BREAK UP - ' + syminfo.ticker + ' @ $' + string.tostring(close, '#.##') + ' | ' + orbStageName + ' - Price back inside range after ' + string.tostring(barsSinceBreak) + ' bars'
                    sendAlert(alertMsgFailedUp)
                    alertFailedUpTriggered = True

                if cyclesUp > 0:
                    cyclesUp -= 1

                godFailedBreaks += 1
                hadBreakUp = False
                barsOutsideAfterBreakUp = 0
                if not na(activeORB):
                    activeORB.breakoutUp = False
            elif wentFarEnough and priceBackInside and isCommittedBreakout:
                hadRetestUp = True
                retestUpBar = bar_index
                barsOutsideAfterBreakUp = 0

                if signalMode == 'Track Cycles':
                    hadBreakUp = False
                    if not na(activeORB):
                        activeORB.breakoutUp = False

                showRetestLabel: bool = True
                if signalMode == 'Track Cycles':
                    showRetestLabel = retestCyclesUp < maxCycles

                if showRetestLabel:
                    retestCyclesUp += 1
                    sessionRetestsUp += 1

                    retestText = string.format('🔁 RETEST UP #{0}', string.tostring(sessionRetestsUp))
                    labelOffset: float = cachedATR * LABEL_OFFSET_ATR_MULTIPLIER
                    labelY: float = high + labelOffset
                    retestLabel = label.new(bar_index, labelY, retestText, style=label.style_label_down, color=color.new(color.orange, 20), textcolor=color.white, size=getLabelSize(labelSize))
                    cleanupLabel(retestLabel)

                    if alertRetests:
                        orbStageName = activeORB.name if not na(activeORB) else 'None'
                        alertMsgRetestUp = '🔁 RETEST UP #' + string.tostring(retestCyclesUp) + ' - ' + syminfo.ticker + ' @ $' + string.tostring(close, '#.##') + ' | Back to ' + orbStageName + ' range'
                        sendAlert(alertMsgRetestUp)
                        alertRetestUpTriggered = True

        if hadBreakDown and (not hadRetestDown):
            wentLowEnough = wentFarEnoughDown
            isCommittedBreakout = barsOutsideAfterBreakDown >= minBarsOutside
            priceBackInside = close > tradeOrbLow - retestBufferCalc and close < tradeOrbHigh + retestBufferCalc

            barsSinceBreak = bar_index - breakDownBarIndex
            isFailedBreak = everHadBreakDown and barsSinceBreak > 0 and (barsSinceBreak <= MAX_BARS_FAILED_BREAK) and priceBackInside and (not isCommittedBreakout)
            if isFailedBreak:
                if not na(lastBreakDownLabel):
                    label.set_text(lastBreakDownLabel, '⚠️ FAILED BREAK')
                    label.set_color(lastBreakDownLabel, color.new(color.orange, 0))

                if alertFailedBreaks:
                    orbStageName = activeORB.name if not na(activeORB) else 'None'
                    alertMsgFailedDown = '⚠️ FAILED BREAK DOWN - ' + syminfo.ticker + ' @ $' + string.tostring(close, '#.##') + ' | ' + orbStageName + ' - Price back inside range after ' + string.tostring(barsSinceBreak) + ' bars'
                    sendAlert(alertMsgFailedDown)
                    alertFailedDownTriggered = True

                if cyclesDown > 0:
                    cyclesDown -= 1

                godFailedBreaks += 1
                hadBreakDown = False
                barsOutsideAfterBreakDown = 0
                if not na(activeORB):
                    activeORB.breakoutDown = False
            elif wentLowEnough and priceBackInside and isCommittedBreakout:
                hadRetestDown = True
                retestDownBar = bar_index
                barsOutsideAfterBreakDown = 0

                if signalMode == 'Track Cycles':
                    hadBreakDown = False
                    if not na(activeORB):
                        activeORB.breakoutDown = False

                showRetestLabel: bool = True
                if signalMode == 'Track Cycles':
                    showRetestLabel = retestCyclesDown < maxCycles

                if showRetestLabel:
                    retestCyclesDown += 1
                    sessionRetestsDown += 1

                    retestText = string.format('🔁 RETEST DOWN #{0}', string.tostring(sessionRetestsDown))

                    labelOffset: float = cachedATR * LABEL_OFFSET_ATR_MULTIPLIER
                    labelY: float = low - labelOffset
                    retestLabel = label.new(bar_index, labelY, retestText, style=label.style_label_up, color=color.new(color.orange, 20), textcolor=color.white, size=getLabelSize(labelSize))
                    cleanupLabel(retestLabel)

                    if alertRetests:
                        orbStageName = activeORB.name if not na(activeORB) else 'None'
                        alertMsgRetestDown = '🔁 RETEST DOWN #' + string.tostring(retestCyclesDown) + ' - ' + syminfo.ticker + ' @ $' + string.tostring(close, '#.##') + ' | Back to ' + orbStageName + ' range'
                        sendAlert(alertMsgRetestDown)
                        alertRetestDownTriggered = True

    isBullish = everHadBreakUp
    entry = orbEntryPrice
    sl = orbSLPrice
    tp1 = orbTP1Price
    tp1_5 = orbTP1_5Price
    tp2 = orbTP2Price
    tp3 = orbTP3Price
    atr = cachedATR

    if not isHTF and showEdgeLabels and haveDisplayRange:
        stageChanged = stage != lastLabelStage
        priceChangedH = displayH != lastLabelH
        priceChangedL = displayL != lastLabelL
        labelsExist = not na(labH) and (not na(labL))
        needsUpdate = stageChanged or priceChangedH or priceChangedL or (not labelsExist)

        if needsUpdate:
            labelColor = color.new(cachedLineColor, 0)

            if na(labH):
                labH = label.new(bar_index + LABEL_OFFSET_BARS, displayH, cachedStageName, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_left, color=labelColor, textcolor=color.white, size=getLabelSize(labelSize))
            else:
                label.set_y(labH, displayH)
                if stageChanged:
                    label.set_text(labH, cachedStageName)
                    label.set_color(labH, labelColor)

            if na(labL):
                labL = label.new(bar_index + LABEL_OFFSET_BARS, displayL, cachedStageName, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_left, color=labelColor, textcolor=color.white, size=getLabelSize(labelSize))
            else:
                label.set_y(labL, displayL)
                if stageChanged:
                    label.set_text(labL, cachedStageName)
                    label.set_color(labL, labelColor)

            lastLabelH = displayH
            lastLabelL = displayL
            lastLabelStage = stage

        if barstate.islast and (not isHTF) and haveDisplayRange:
            if not na(labH):
                label.set_x(labH, bar_index + LABEL_OFFSET_BARS)
            if not na(labL):
                label.set_x(labL, bar_index + LABEL_OFFSET_BARS)

    if not orbLinesFrozen and (not na(orbEntryBar)) and (bar_index >= orbEntryBar):
        if not na(orbEntryLine):
            line.set_x2(orbEntryLine, bar_index)
        if not na(orbEntryLabel):
            label.set_x(orbEntryLabel, bar_index)

        if not na(orbSLLine):
            line.set_x2(orbSLLine, bar_index)
        if not na(orbSLLabel):
            label.set_x(orbSLLabel, bar_index)

        if not na(orbTP1Line):
            line.set_x2(orbTP1Line, bar_index)
        if not na(orbTP1Label):
            label.set_x(orbTP1Label, bar_index)

        if not na(orbTP1_5Line):
            line.set_x2(orbTP1_5Line, bar_index)
        if not na(orbTP1_5Label):
            label.set_x(orbTP1_5Label, bar_index)

        if not na(orbTP2Line):
            line.set_x2(orbTP2Line, bar_index)
        if not na(orbTP2Label):
            label.set_x(orbTP2Label, bar_index)

        if not na(orbTP3Line):
            line.set_x2(orbTP3Line, bar_index)
        if not na(orbTP3Label):
            label.set_x(orbTP3Label, bar_index)

    if not orbLinesFrozen and (not na(orbEntryPrice)) and (barstate.isconfirmed or barstate.islast):
        isLongTrade: bool = orbTradeDirection == 1

        if not orbTP1Hit and (not na(orbTP1Price)) and showTP1 and (bar_index >= orbEntryBar) and (high >= orbTP1Price if isLongTrade else low <= orbTP1Price):
            orbTP1Hit = True
            alertTP1Triggered = True
            if not na(orbTP1Label):
                tp1Text: str = '✅ TP1' if labelFormat == 'Simple' else string.format('✅ TP1: ${0}', string.tostring(orbTP1Price, '#.##'))
                label.set_text(orbTP1Label, tp1Text)
                label.set_color(orbTP1Label, color.new(color.green, 0))
            if not na(orbTP1Line):
                line.set_color(orbTP1Line, color.new(color.green, 0))

        if not orbTP1_5Hit and (not na(orbTP1_5Price)) and showTP1_5 and (bar_index >= orbEntryBar) and (high >= orbTP1_5Price if isLongTrade else low <= orbTP1_5Price):
            orbTP1_5Hit = True
            alertTP1_5Triggered = True
            if not na(orbTP1_5Label):
                tp1_5Text: str = '✅ TP1.5' if labelFormat == 'Simple' else string.format('✅ TP1.5: ${0}', string.tostring(orbTP1_5Price, '#.##'))
                label.set_text(orbTP1_5Label, tp1_5Text)
                label.set_color(orbTP1_5Label, color.new(color.green, 0))
            if not na(orbTP1_5Line):
                line.set_color(orbTP1_5Line, color.new(color.green, 0))

        if not orbTP2Hit and (not na(orbTP2Price)) and showTP2 and (bar_index >= orbEntryBar) and (high >= orbTP2Price if isLongTrade else low <= orbTP2Price):
            orbTP2Hit = True
            alertTP2Triggered = True
            if not na(orbTP2Label):
                tp2Text: str = '✅ TP2' if labelFormat == 'Simple' else string.format('✅ TP2: ${0}', string.tostring(orbTP2Price, '#.##'))
                label.set_text(orbTP2Label, tp2Text)
                label.set_color(orbTP2Label, color.new(color.green, 0))
            if not na(orbTP2Line):
                line.set_color(orbTP2Line, color.new(color.green, 0))

        if not orbTP3Hit and (not na(orbTP3Price)) and showTP3 and (bar_index >= orbEntryBar) and (high >= orbTP3Price if isLongTrade else low <= orbTP3Price):
            orbTP3Hit = True
            alertTP3Triggered = True
            if not na(orbTP3Label):
                tp3Text: str = '✅ TP3' if labelFormat == 'Simple' else string.format('✅ TP3: ${0}', string.tostring(orbTP3Price, '#.##'))
                label.set_text(orbTP3Label, tp3Text)
                label.set_color(orbTP3Label, color.new(color.green, 0))
            if not na(orbTP3Line):
                line.set_color(orbTP3Line, color.new(color.green, 0))

        lastTPHit: bool = False
        if showTP3 and orbTP3Hit:
            lastTPHit = True
        elif not showTP3 and showTP2 and orbTP2Hit:
            lastTPHit = True
        elif not showTP3 and (not showTP2) and showTP1_5 and orbTP1_5Hit:
            lastTPHit = True
        elif not showTP3 and (not showTP2) and (not showTP1_5) and showTP1 and orbTP1Hit:
            lastTPHit = True

        if lastTPHit:
            orbLinesFrozen = True

        if not orbSLHit and (not na(orbSLPrice)) and (bar_index >= orbEntryBar) and (low <= orbSLPrice if isLongTrade else high >= orbSLPrice):
            orbSLHit = True
            alertSLTriggered = True
            orbLinesFrozen = True

            if not na(activeORB):
                if isLongTrade:
                    activeORB.breakoutUp = False
                else:
                    activeORB.breakoutDown = False
            if not na(orbSLLabel):
                slText: str = '❌ SL' if labelFormat == 'Simple' else string.format('❌ SL: ${0}', string.tostring(orbSLPrice, '#.##'))
                label.set_text(orbSLLabel, slText)

        if freezeOnEOD and (not inSession) and inSession[1]:
            orbLinesFrozen = True

    cyclesChanged: bool = cyclesUp != prevCyclesUp or cyclesDown != prevCyclesDown
    newBreakoutDetected: bool = not na(orbEntryBar) and (na(prevOrbEntryBar) or orbEntryBar != prevOrbEntryBar or cyclesChanged)

    if newBreakoutDetected:
        trade_closed = False
        prevOrbEntryBar = orbEntryBar
        prevCyclesUp = cyclesUp
        prevCyclesDown = cyclesDown
        current_trade_r = 0.0
        tp1_counted = False
        tp1_5_counted = False
        tp2_counted = False
        tp3_counted = False

    hasActiveBreakout: bool = (everHadBreakUp or everHadBreakDown) and (not na(orbEntryBar))

    if hasActiveBreakout and (not trade_closed):
        current_trade_r = 0.0

        if orbTP3Hit and showTP3:
            current_trade_r = 3.0
        elif orbTP2Hit and showTP2:
            current_trade_r = 2.0
        elif orbTP1_5Hit and showTP1_5:
            current_trade_r = 1.5
        elif orbTP1Hit and showTP1:
            current_trade_r = 1.0

        lastTPisTP3: bool = showTP3
        lastTPisTP2: bool = showTP2 and (not showTP3)
        lastTPisTP1_5: bool = showTP1_5 and (not showTP2) and (not showTP3)
        lastTPisTP1: bool = showTP1 and (not showTP1_5) and (not showTP2) and (not showTP3)

        shouldClose: bool = False
        resultText: str = ""
        isWin: bool = False

        if orbSLHit:
            shouldClose = True
            isWin = False
            current_trade_r = -1.0
            resultText = "❌ SL Hit (-1R)"
        elif orbTP3Hit and lastTPisTP3 or (orbTP2Hit and lastTPisTP2) or (orbTP1_5Hit and lastTPisTP1_5) or (orbTP1Hit and lastTPisTP1):
            shouldClose = True
            isWin = True

            if orbTP3Hit and lastTPisTP3:
                resultText = "✅ TP3 Hit (+3R)"
            elif orbTP2Hit and lastTPisTP2:
                resultText = "✅ TP2 Hit (+2R)"
            elif orbTP1_5Hit and lastTPisTP1_5:
                resultText = "✅ TP1.5 Hit (+1.5R)"
            elif orbTP1Hit and lastTPisTP1:
                resultText = "✅ TP1 Hit (+1R)"
        elif freezeOnEOD and (not inSession) and inSession[1]:
            shouldClose = True

            if orbTradeDirection == 1:
                riskDist: float = entry - sl
                profitDist: float = close - entry
                current_trade_r = profitDist / riskDist if riskDist > 0 else 0.0
            elif orbTradeDirection == -1:
                riskDist: float = sl - entry
                profitDist: float = entry - close
                current_trade_r = profitDist / riskDist if riskDist > 0 else 0.0

            isWin = current_trade_r > 0

            eodIcon: str = '✅' if current_trade_r > 0 else '❌' if current_trade_r < 0 else '⚖️'
            resultText = string.format('{0} EOD Close: {1}R', eodIcon, string.tostring(current_trade_r, '#.#'))

        if shouldClose and (not trade_closed):
            trade_closed = True
            session_trades += 1

            session_total_rr += current_trade_r

            if isWin:
                session_wins += 1
                session_best_r = math.max(session_best_r, current_trade_r)
            else:
                session_losses += 1
                session_worst_r = math.min(session_worst_r, current_trade_r)

            last_trade_result = resultText

    plotORB5High: float = na(float)
    plotORB5Low: float = na(float)
    plotORB5Mid: float = na(float)
    plotORB15High: float = na(float)
    plotORB15Low: float = na(float)
    plotORB15Mid: float = na(float)
    plotORB30High: float = na(float)
    plotORB30Low: float = na(float)
    plotORB30Mid: float = na(float)
    plotORB60High: float = na(float)
    plotORB60Low: float = na(float)
    plotORB60Mid: float = na(float)

    lastEnabledORB: ORBData = na(ORBData)
    for orbObj in allORBs:
        if orbObj.isEnabled:
            if na(lastEnabledORB) or orbObj.minutes > lastEnabledORB.minutes:
                lastEnabledORB = orbObj

    if not isHTF and inSession:
        barEndTime: float = time + currentTF_seconds * 1000
        minsFromOpenToEndOfBar: float = (barEndTime - sessionFirstBarTime) / 60000 if not na(sessionFirstBarTime) else -1

        if orb5Obj.isEnabled and orb5Obj.minutes >= currentTF_minutes:
            prevOrb = array.get(cachedPrevORBs, 0)
            nextOrb = array.get(cachedNextORBs, 0)

            prevOrbVisible: bool = False if na(prevOrb) else prevOrb.minutes >= currentTF_minutes
            startMin: float = -1.0
            endMin: float = 9999.0 if na(nextOrb) else orb5Obj.minutes - 1
            inWindow: bool = minsFromOpen > startMin and minsFromOpen <= endMin
            hasData: bool = not na(orb5Obj.high) and (not na(orb5Obj.low))

            if inWindow and hasData:
                plotORB5High = orb5Obj.high
                plotORB5Low = orb5Obj.low
                plotORB5Mid = orb5Obj.mid
            else:
                plotORB5High = na
                plotORB5Low = na
                plotORB5Mid = na
        else:
            plotORB5High = na
            plotORB5Low = na
            plotORB5Mid = na

        if orb15Obj.isEnabled and orb15Obj.minutes >= currentTF_minutes:
            prevOrb = getPreviousEnabledORB(orb15Obj)
            nextOrb = getNextEnabledORB(orb15Obj)

            prevOrbVisible: bool = False if na(prevOrb) else prevOrb.minutes >= currentTF_minutes
            startMin: float = 0.0 if na(prevOrb) or not prevOrbVisible else prevOrb.minutes - 1
            endMin: float = 9999.0 if na(nextOrb) else orb15Obj.minutes
            startsBeforeEnd: bool = minsFromOpen < endMin
            endsAfterStart: bool = minsFromOpenToEndOfBar > startMin
            inWindow: bool = startsBeforeEnd and endsAfterStart
            hasData: bool = not na(orb15Obj.high) and (not na(orb15Obj.low))

            if inWindow and hasData:
                plotORB15High = orb15Obj.high
                plotORB15Low = orb15Obj.low
                plotORB15Mid = orb15Obj.mid
            else:
                plotORB15High = na
                plotORB15Low = na
                plotORB15Mid = na
        else:
            plotORB15High = na
            plotORB15Low = na
            plotORB15Mid = na

        if orb30Obj.isEnabled and orb30Obj.minutes >= currentTF_minutes:
            prevOrb = getPreviousEnabledORB(orb30Obj)
            nextOrb = getNextEnabledORB(orb30Obj)

            prevOrbVisible: bool = False if na(prevOrb) else prevOrb.minutes >= currentTF_minutes
            startMin: float = 0.0 if na(prevOrb) or not prevOrbVisible else prevOrb.minutes - 1
            endMin: float = 9999.0 if na(nextOrb) else orb30Obj.minutes
            startsBeforeEnd: bool = minsFromOpen < endMin
            endsAfterStart: bool = minsFromOpenToEndOfBar > startMin
            inWindow: bool = startsBeforeEnd and endsAfterStart
            hasData: bool = not na(orb30Obj.high) and (not na(orb30Obj.low))

            if inWindow and hasData:
                plotORB30High = orb30Obj.high
                plotORB30Low = orb30Obj.low
                plotORB30Mid = orb30Obj.mid
            else:
                plotORB30High = na
                plotORB30Low = na
                plotORB30Mid = na
        else:
            plotORB30High = na
            plotORB30Low = na
            plotORB30Mid = na

        if orb60Obj.isEnabled and orb60Obj.minutes >= currentTF_minutes:
            prevOrb = getPreviousEnabledORB(orb60Obj)
            nextOrb = getNextEnabledORB(orb60Obj)

            prevOrbVisible: bool = False if na(prevOrb) else prevOrb.minutes >= currentTF_minutes
            startMin: float = 0.0 if na(prevOrb) or not prevOrbVisible else prevOrb.minutes - 1
            endMin: float = 9999.0
            startsBeforeEnd: bool = minsFromOpen < endMin
            endsAfterStart: bool = minsFromOpenToEndOfBar > startMin
            inWindow: bool = startsBeforeEnd and endsAfterStart
            hasData: bool = not na(orb60Obj.high) and (not na(orb60Obj.low))

            if inWindow and hasData:
                plotORB60High = orb60Obj.high
                plotORB60Low = orb60Obj.low
                plotORB60Mid = orb60Obj.mid
            else:
                plotORB60High = na
                plotORB60Low = na
                plotORB60Mid = na
        else:
            plotORB60High = na
            plotORB60Low = na
            plotORB60Mid = na

    p_orb5_high = plot(plotORB5High, title='ORB5 High', color=color.new(orb5LineColor, 0), linewidth=1, style=plot.style_linebr, display=display.all)
    p_orb5_low = plot(plotORB5Low, title='ORB5 Low', color=color.new(orb5LineColor, 0), linewidth=1, style=plot.style_linebr, display=display.all)
    fill(p_orb5_high, p_orb5_low, color=color.new(orb5LineColor, fillTransparency if showBG else 100), title='ORB5 Fill')
    plot(plotORB5Mid if showMidLine else na, title='ORB5 Mid', color=color.new(orb5LineColor, 30), linewidth=1, style=plot.style_linebr, display=display.all)

    p_orb15_high = plot(plotORB15High, title='ORB15 High', color=color.new(orb15LineColor, 0), linewidth=1, style=plot.style_linebr, display=display.all)
    p_orb15_low = plot(plotORB15Low, title='ORB15 Low', color=color.new(orb15LineColor, 0), linewidth=1, style=plot.style_linebr, display=display.all)
    fill(p_orb15_high, p_orb15_low, color=color.new(orb15LineColor, fillTransparency if showBG else 100), title='ORB15 Fill')
    plot(plotORB15Mid if showMidLine else na, title='ORB15 Mid', color=color.new(orb15LineColor, 30), linewidth=1, style=plot.style_linebr, display=display.all)

    p_orb30_high = plot(plotORB30High, title='ORB30 High', color=color.new(orb30LineColor, 0), linewidth=1, style=plot.style_linebr, display=display.all)
    p_orb30_low = plot(plotORB30Low, title='ORB30 Low', color=color.new(orb30LineColor, 0), linewidth=1, style=plot.style_linebr, display=display.all)
    fill(p_orb30_high, p_orb30_low, color=color.new(orb30LineColor, fillTransparency if showBG else 100), title='ORB30 Fill')
    plot(plotORB30Mid if showMidLine else na, title='ORB30 Mid', color=color.new(orb30LineColor, 30), linewidth=1, style=plot.style_linebr, display=display.all)

    p_orb60_high = plot(plotORB60High, title='ORB60 High', color=color.new(orb60LineColor, 0), linewidth=1, style=plot.style_linebr, display=display.all)
    p_orb60_low = plot(plotORB60Low, title='ORB60 Low', color=color.new(orb60LineColor, 0), linewidth=1, style=plot.style_linebr, display=display.all)
    fill(p_orb60_high, p_orb60_low, color=color.new(orb60LineColor, fillTransparency if showBG else 100), title='ORB60 Fill')
    plot(plotORB60Mid if showMidLine else na, title='ORB60 Mid', color=color.new(orb60LineColor, 30), linewidth=1, style=plot.style_linebr, display=display.all)

    cachedHTFBiasText: Persistent[str] = ""
    lastHTFCheckBar: Persistent[int] = -1
    cachedHTFBullish: Persistent[bool] = False
    cachedHTFBearish: Persistent[bool] = False
    cachedHTFStrength: Persistent[float] = 0.0
    shouldCheckHTF: Persistent[bool] = False

    lastDashStage: Persistent[int] = -1
    lastDashBreakUp: Persistent[bool] = False
    lastDashBreakDown: Persistent[bool] = False
    lastDashOrbHigh: Persistent[float] = na(float)
    lastDashOrbLow: Persistent[float] = na(float)
    lastDashTP1Hit: Persistent[bool] = False
    lastDashTP1_5Hit: Persistent[bool] = False
    lastDashTP2Hit: Persistent[bool] = False
    lastDashTP3Hit: Persistent[bool] = False
    lastDashSLHit: Persistent[bool] = False

    if showDashboard and enableHTF:
        htfTimeChanged, = request.security(syminfo.tickerid, htfTF, (ta.change(time) != 0,), barmerge.gaps_off, barmerge.lookahead_off)

        if barstate.islast and (htfTimeChanged or na(cachedHTFBiasText)):
            htfBullishCalc, htfBearishCalc, htfBiasTextTemp, htfStrengthTemp = checkHTFBias()
            cachedHTFBiasText = htfBiasTextTemp
            cachedHTFBullish = htfBullishCalc
            cachedHTFBearish = htfBearishCalc
            cachedHTFStrength = htfStrengthTemp
            lastHTFCheckBar = bar_index

        htfBullish = cachedHTFBullish
        htfBearish = cachedHTFBearish
        htfBiasText = cachedHTFBiasText

        stageChanged: bool = stage != lastDashStage
        breakStateChanged: bool = hadBreakUp != lastDashBreakUp or hadBreakDown != lastDashBreakDown
        orbLevelsChanged: bool = not na(activeORB) and (activeORB.high != lastDashOrbHigh or activeORB.low != lastDashOrbLow)
        targetHitStateChanged: bool = orbTP1Hit != lastDashTP1Hit or orbTP1_5Hit != lastDashTP1_5Hit or orbTP2Hit != lastDashTP2Hit or (orbTP3Hit != lastDashTP3Hit) or (orbSLHit != lastDashSLHit)
        forceUpdate: bool = bar_index - lastDashUpdateBar >= 20
        dashDataChanged: bool = barstate.islast and (stageChanged or breakStateChanged or orbLevelsChanged or targetHitStateChanged or forceUpdate)

        isDarkTheme: bool = dashTheme == 'Dark'
        bgColor: Color = color.new(color.black, 0) if isDarkTheme else color.new(color.white, 10)
        txtColor: Color = color.white if isDarkTheme else color.black
        headerColor: Color = color.new(color.aqua, 30) if isDarkTheme else color.new(color.silver, 30)
        tablePos = position.top_left if dashPos == 'Top Left' else position.top_right if dashPos == 'Top Right' else position.bottom_left if dashPos == 'Bottom Left' else position.bottom_right if dashPos == 'Bottom Right' else position.middle_right
        txtSize = size.small if dashSize == 'Small' else size.normal if dashSize == 'Normal' else size.large if dashSize == 'Large' else size.auto

        if showDashboard and na(dashTable):
            dashTable = table.new(tablePos, 2, 28, bgcolor=bgColor, border_width=0, frame_width=1)
            table.clear(dashTable, 0, 0, 1, 27)
            table.set_position(dashTable, tablePos)
            lastDashUpdateBar = bar_index

        if showDashboard and (not na(dashTable)):
            lastDashUpdateBar = bar_index
            lastDashStage = stage
            lastDashBreakUp = hadBreakUp
            lastDashBreakDown = hadBreakDown
            if not na(activeORB):
                lastDashOrbHigh = activeORB.high
                lastDashOrbLow = activeORB.low
            lastDashTP1Hit = orbTP1Hit
            lastDashTP1_5Hit = orbTP1_5Hit
            lastDashTP2Hit = orbTP2Hit
            lastDashTP3Hit = orbTP3Hit
            lastDashSLHit = orbSLHit

            table.clear(dashTable, 0, 0, 1, 27)
            table.set_position(dashTable, tablePos)

        row: int = 0

        showFullDashboard: bool = False
        sessionIcon: str = ""
        sessionStatusText: str = ""

        isMarketOpen: bool = isTradingDay() and isWithinSessionHours()
        isDisplayWindow: bool = isWithinDisplayHours()

        hasValidOrbData: bool = not na(activeORB) or everHadBreakUp or everHadBreakDown or (not na(orbEntryPrice))

        if isHTF:
            sessionIcon = "⚠️"
            sessionStatusText = "HTF MODE - Use 5-60min timeframe"
            showFullDashboard = False
        elif isMarketOpen:
            isRegularHours: bool = isInRegularHours()
            sessionIcon = '☀️' if isRegularHours else '💤'
            sessionStatusText = 'MARKET OPEN' if isRegularHours else 'EXTENDED HOURS'
            showFullDashboard = True
        elif hadSessionToday and hasValidOrbData and isDisplayWindow and (not isMarketOpen):
            sessionIcon = "🌙"

            useReplayTime: bool = isReplayMode()
            timeToCheck: int = time if useReplayTime else timenow

            sessionDate: str = string.format_time(cast_int(sessionStartTime), 'MM/dd', syminfo.timezone) if not na(sessionStartTime) else 'N/A'
            currentDate: str = string.format_time(timeToCheck, 'MM/dd', syminfo.timezone)

            if sessionDate == currentDate:
                sessionStatusText = "AFTER HOURS - Today's Data (" + sessionDate + ')'
            else:
                sessionStatusText = "AFTER HOURS - Yesterday's Data (" + sessionDate + ')'

            showFullDashboard = True
        elif not hadSessionToday and isDisplayWindow and isTradingDay() and enableExtendedHours:
            sessionIcon = "⏰"
            sessionStatusText = "PRE-MARKET - Waiting for ORB"
            showFullDashboard = False
        else:
            sessionIcon = "🌙"
            sessionStatusText = "MARKET CLOSED"
            showFullDashboard = False

        if not showFullDashboard and (not na(dashTable)) and (dashDataChanged or forceUpdate):
            table.clear(dashTable, 0, 0, 1, 27)
            table.set_position(dashTable, tablePos)

            statusTitle: str = sessionIcon + ' ' + sessionStatusText
            statusBgColor: Color = color.new(color.gray, 20) if isDarkTheme else color.new(color.gray, 80)

            statusTooltip: str = ""
            if isHTF:
                statusTooltip = "ORB works only on timeframes 1-60 minutes.\n\nPlease switch to a lower timeframe to use ORB."
            elif not hadSessionToday and isDisplayWindow and isTradingDay() and enableExtendedHours:
                statusTooltip = "Waiting for market open to build ORB.\n\nExtended hours trading is enabled.\nORB will start building at session start."
            else:
                statusTooltip = "Market is closed.\n\nORB will activate during market hours."

            table.cell(dashTable, 0, 0, statusTitle, text_color=txtColor, text_size=txtSize, text_halign=text.align_center, bgcolor=statusBgColor, tooltip=statusTooltip)
            table.cell(dashTable, 1, 0, '', bgcolor=statusBgColor)
            table.merge_cells(dashTable, 0, 0, 1, 0)

            lastDashUpdateBar = bar_index
        elif showFullDashboard and (not na(dashTable)):
            entry__00000609__: float = na(float)
            sl__00000609__: float = na(float)
            tp1__00000609__: float = na(float)
            tp1_5__00000609__: float = na(float)
            tp2__00000609__: float = na(float)
            tp3__00000609__: float = na(float)
            atr__00000609__: float = na(float)
            isBullish__00000609__: bool = False
            shares: int = na(int)
            posValue: float = na(float)
            maxLossCalc: float = na(float)
            riskAmount: float = na(float)
            riskPctOfAcct: float = na(float)

            headerTitle: str = sessionIcon + ' ORB DASHBOARD'
            headerBgColor: Color = headerColor
            headerTooltip: str = 'ORB Dashboard - ' + sessionStatusText + '\n\n'

            if isWithinDisplayHours() and isInRegularHours():
                headerTooltip += "☀️ REGULAR HOURS (09:30-16:00)\n"
                headerTooltip += "Market is open for trading.\n\n"
            elif isWithinDisplayHours() and (not isInRegularHours()):
                headerTooltip += "🌙 EXTENDED HOURS\n"
                headerTooltip += "Pre-market (04:00-09:30) or After-hours (16:00-20:00)\n"
                headerTooltip += "Showing data from extended session.\n\n"

            if everHadBreakUp:
                headerTitle += " ⬆️"
                headerBgColor = color.new(color.green, 10)
                headerTooltip += "⬆️ BREAKOUT UP active\n"
            elif everHadBreakDown:
                headerTitle += " ⬇️"
                headerBgColor = color.new(color.red, 10)
                headerTooltip += "⬇️ BREAKOUT DOWN active\n"

            headerTooltip += "\n━━━━━━━━━━━━━━━━━━━━━\n"
            headerTooltip += "Shows Opening Range Breakout status and trade setup.\n"
            headerTooltip += "The dashboard displays active breakout trade parameters including entry, targets, and stop loss."

            if not na(dashTable):
                table.cell(dashTable, 0, row, headerTitle, text_color=txtColor, text_size=txtSize, text_halign=text.align_center, bgcolor=headerBgColor, tooltip=headerTooltip)
                table.cell(dashTable, 1, row, '', text_halign=text.align_center, bgcolor=headerBgColor)
                table.merge_cells(dashTable, 0, row, 1, row)
            row += 1

            if showStage and (not na(activeORB)):
                isMarketNow: bool = isTradingDay() and isWithinSessionHours()
                showingPastData: bool = hadSessionToday and (not isMarketNow)

                activeOrbText = '📊 Last: ' + activeORB.name if showingPastData else '🎯 Active: ' + activeORB.name

                useReplayTime: bool = isReplayMode()
                timeToCheck: int = time if useReplayTime else timenow
                modeIndicator: str = ' [REPLAY]' if useReplayTime else ' [LIVE]'

                currentTime: str = string.format_time(timeToCheck, 'HH:mm:ss', syminfo.timezone) + modeIndicator
                currentDate: str = string.format_time(timeToCheck, 'yyyy-MM-dd', syminfo.timezone)
                barTime: str = string.format_time(time, 'HH:mm:ss', syminfo.timezone)

                chartTimezoneDisplay: str = "Unknown - Check: Right-click → Settings → Timezone"

                timezoneHint: str = '\n\nℹ️ If time seems wrong:\n' + 'Your chart may be set to UTC, EST, or another timezone.\n' + 'To change: Right-click chart → Settings → Timezone\n\n' + 'Common settings:\n' + '• Asia/Jerusalem (Israel time)\n' + '• America/New_York (NYSE time)\n' + '• UTC (Universal time - neutral)\n'

                sessionDescription: str = ""
                if sessionMode == 'New-York':
                    sessionDescription = "NYSE Hours (09:30-16:00 EST/EDT)"
                elif sessionMode == 'London':
                    sessionDescription = "LSE Hours (08:00-16:30 GMT/BST)"
                elif sessionMode == 'Tokyo':
                    sessionDescription = "TSE Hours (09:00-15:00 JST)"
                elif sessionMode == 'Sydney':
                    sessionDescription = "ASX Hours (10:00-16:00 AEST)"
                elif sessionMode == 'Frankfurt':
                    sessionDescription = "XETRA Hours (09:00-17:30 CET/CEST)"
                elif sessionMode == 'Auto-Detect':
                    if syminfo.type == 'stock' or syminfo.type == 'fund' or syminfo.type == 'index' or (syminfo.type == 'dr') or (syminfo.type == 'etf') or (syminfo.type == 'futures'):
                        sessionDescription = 'Exchange Hours (Auto-detected for ' + syminfo.ticker + ')'
                    elif syminfo.type == 'crypto':
                        sessionDescription = "24/7 Trading"
                    else:
                        sessionDescription = "Auto-detected Session"
                elif sessionMode == 'Custom':
                    sessionDescription = 'Custom Session (' + string.replace(tradingSession, ':23456', '') + ')'

                withinSessionHours: bool = isWithinSessionHours()
                sessionStatus: str = '✅ OPEN' if withinSessionHours else '❌ CLOSED'

                timeFromOpen: str = "N/A"

                if withinSessionHours and (not na(sessionStartTime)):
                    minutesElapsed: int = cast_int((time - sessionStartTime) / 60000)
                    hours: int = cast_int(minutesElapsed / 60)
                    mins: int = minutesElapsed % 60
                    timeFromOpen = string.format('{0}h {1}m (OPEN)', hours, mins)
                elif not na(sessionStartTime):
                    timeFromOpen = "Session Closed"

                orbHighStr: str = string.tostring(activeORB.high, '#.####')
                orbLowStr: str = string.tostring(activeORB.low, '#.####')
                orbRangeStr: str = string.tostring(activeORB.orbRange, '#.####')
                orbRangePct: str = string.tostring(activeORB.orbRange / activeORB.low * 100, '#.##')

                breakoutStats: str = string.format('{0}↑ / {1}↓', activeORB.cyclesUp, activeORB.cyclesDown)
                totalBreakouts: int = activeORB.cyclesUp + activeORB.cyclesDown

                marketType = 'Stock' if syminfo.type == 'stock' else 'Crypto' if syminfo.type == 'crypto' else 'Forex' if syminfo.type == 'forex' else syminfo.type
                resetTiming = 'Midnight UTC (24/7 mode)' if is24_7Market else 'Session start: ' + string.replace(tradingSession, ':23456', '') + ' (' + sessionMode + ')'

                if sessionMode == 'New-York':
                    sessionDescription = "NYSE Hours (09:30-16:00 EST/EDT)"
                elif sessionMode == 'London':
                    sessionDescription = "LSE Hours (08:00-16:30 GMT/BST)"
                elif sessionMode == 'Tokyo':
                    sessionDescription = "TSE Hours (09:00-15:00 JST)"
                elif sessionMode == 'Sydney':
                    sessionDescription = "ASX Hours (10:00-16:00 AEST)"
                elif sessionMode == 'Frankfurt':
                    sessionDescription = "XETRA Hours (09:00-17:30 CET/CEST)"
                elif sessionMode == 'Auto-Detect':
                    if syminfo.type == 'stock' or syminfo.type == 'fund' or syminfo.type == 'index' or (syminfo.type == 'dr') or (syminfo.type == 'etf') or (syminfo.type == 'futures'):
                        sessionDescription = 'Exchange Hours (Auto-detected for ' + syminfo.ticker + ')'
                    elif syminfo.type == 'crypto':
                        sessionDescription = "24/7 Trading"
                    else:
                        sessionDescription = "Auto-detected Session"
                elif sessionMode == 'Custom':
                    sessionDescription = 'Custom Session (' + string.replace(tradingSession, ':23456', '') + ')'

                is24_7: bool = syminfo.type == 'crypto' or string.contains(tradingSession, '0000-2359')

                sessionInfoSection: str = ""
                if not is24_7:
                    sessionInfoSection = 'Time from session open: ' + timeFromOpen + '\n\n' + 'Session Definition: ' + sessionDescription + '\n' + 'Raw Session String: ' + tradingSession + '\n\n'

                activeOrbTooltip = 'Currently Active ORB\n\n' + 'This is the ORB period being used for breakout detection.\n\n' + '• Breakouts are checked against THIS ORB only\n' + '• When a new ORB completes, it becomes active\n' + '• Priority: ORB60 > ORB30 > ORB15 > ORB5\n\n' + '─────────────────\n' + '⏰ CHART TIME DISPLAY\n' + '─────────────────\n' + 'Date: ' + currentDate + '\n' + 'Current Bar: ' + currentTime + '\n' + 'Bar Open: ' + barTime + '\n\n' + 'ℹ️ If time seems wrong:\n' + 'Your chart may be set to UTC, EST, or another timezone.\n' + 'To change: Right-click chart → Settings → Timezone\n\n' + '─────────────────\n' + '📊 SESSION STATUS\n' + '─────────────────\n' + 'Status: ' + sessionStatus + '\n' + ('' if is24_7 else 'Time from session open: ' + timeFromOpen + '\n\n' + 'Session Definition: ' + sessionDescription + '\n' + 'Raw Session String: ' + tradingSession + '\n\n')

                table.cell(dashTable, 0, row, activeOrbText, text_color=color.new(color.yellow, 0), text_size=txtSize, text_halign=text.align_center, bgcolor=color.new(color.blue, 20), tooltip=activeOrbTooltip)
                table.cell(dashTable, 1, row, '', bgcolor=color.new(color.blue, 20))
                table.merge_cells(dashTable, 0, row, 1, row)
                row += 1

            if showRange and (not isHTF) and (not na(activeORB)):
                orbRange = activeORB.high - activeORB.low
                rangePct = orbRange / activeORB.low * 100 if activeORB.low > 0 else 0
                rangeTooltip: str = "ORB Range Size\n\nShows the width of the Opening Range in both dollars and percentage.\n\n• Large range (>1.5%) = High volatility\n• Medium range (0.5-1.5%) = Normal volatility\n• Small range (<0.5%) = Low volatility\n\nLarger ranges may require wider stops and smaller position sizes."

                table.cell(dashTable, 0, row, 'Range:', text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip=rangeTooltip)
                table.cell(dashTable, 1, row, string.format('${0} ({1}% width)', string.tostring(orbRange, '#.##'), string.tostring(rangePct, '#.#')), text_color=txtColor, text_size=txtSize, text_halign=text.align_right)
                row += 1

            if showVolatilityMeter and (not isHTF):
                atrPct: float = cachedATR / close * 100 if cachedATR > 0 and close > 0 else 0
                volIcon: str = '🔥🔥🔥' if atrPct > 3.0 else '🔥🔥' if atrPct > 2.0 else '🔥' if atrPct > 1.0 else '⚪'
                volText: str = 'Extreme' if atrPct > 3.0 else 'High' if atrPct > 2.0 else 'Medium' if atrPct > 1.0 else 'Low'
                volFull: str = volIcon + ' ' + volText

                volTooltip = 'Market Volatility Level\n\nMeasures current volatility using ATR percentage of price.\n\nCurrent ATR: ' + string.tostring(atrPct, '#.##') + '%\n\nLEVELS:\n🔥🔥🔥 EXTREME (>3%)\n• Very volatile conditions\n• Wider stops recommended\n• Smaller position sizes\n• Larger potential moves\n\n🔥🔥 HIGH (2-3%)\n• Active price movement\n• Standard stops work well\n• Normal position sizing\n• Good trading conditions\n\n🔥 MEDIUM (1-2%)\n• Normal trading range\n• Standard risk management\n• Typical daily movement\n\n⚪ LOW (<1%)\n• Quiet market\n• Tighter stops possible\n• Limited movement expected\n• May have smaller ORB ranges\n\nIMPLICATIONS:\nHigher volatility = Bigger potential profit BUT more risk of stop-out'

                table.cell(dashTable, 0, row, '📊 Volatility:', text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip=volTooltip)
                table.cell(dashTable, 1, row, volFull, text_color=txtColor, text_size=txtSize, text_halign=text.align_right)
                row += 1

            if godModeEnabled and (not isHTF):
                godScoreText: str = '—' if na(godLastScore) else '⚡ ' + string.tostring(godLastScore, '#') + ' (' + f_godGrade(godLastScore) + ') ' + godLastScoreDir + (' 🏆' if godLastScoreDir == 'UP' and godHighConfluence or (godLastScoreDir == 'DOWN' and godLowConfluence) else '')
                godScoreColor: Color = txtColor if na(godLastScore) else color.new(color.lime, 0) if godLastScore >= 70 else color.new(color.yellow, 0) if godLastScore >= 55 else color.new(color.orange, 0)
                godScoreTooltip: str = "GOD MODE Breakout Quality Score\n\nGrades the most recent breakout 0-100:\n• Volume strength vs average\n• HTF bias alignment\n• ORB width vs daily ATR (narrow = better)\n• Gap direction alignment\n• PDH/PDL/premarket level confluence (🏆)\n• Breakout cycle number (first = best)\n\nGRADES:\nA+ (85+) = Exceptional setup\nA (70-84) = Strong setup\nB (55-69) = Decent setup\nC (40-54) = Weak setup\nD (<40) = Avoid\n\nCHOP DAY caps the score at 40."
                table.cell(dashTable, 0, row, '⚡ GOD Score:', text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip=godScoreTooltip)
                table.cell(dashTable, 1, row, godScoreText, text_color=godScoreColor, text_size=txtSize, text_halign=text.align_right)
                row += 1
                godGapText: str = '' if na(godGapPct) else 'Gap ' + ('+' if godGapPct >= 0 else '') + string.tostring(godGapPct, '#.#') + '%'
                godOrText: str = 'OR ' + string.tostring(activeORB.orbRange / godDailyATR, '#.##') + '×dATR' if not na(godDailyATR) and godDailyATR > 0 and (not na(activeORB)) else ''
                godCtxText: str = '⚠️ CHOP DAY (' + string.tostring(godFailedBreaks) + ' fails)' if godChopDay else godGapText + (' | ' if godGapText != '' and godOrText != '' else '') + godOrText
                godCtxTooltip: str = "GOD MODE Day Context\n\nGAP: Today's open vs yesterday's close\n• Breakouts aligned with the gap direction score higher\n\nOR vs dATR: ORB width as a fraction of daily ATR\n• ≤0.25× = Compressed range, high expansion odds (best)\n• 0.25-0.5× = Normal\n• >0.75× = Range already used up, poor R/R\n\n⚠️ CHOP DAY: 2+ failed breaks this session\n• Quality Score capped at 40\n• Whipsaw conditions - trade with caution"
                table.cell(dashTable, 0, row, '🌅 Day Context:', text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip=godCtxTooltip)
                table.cell(dashTable, 1, row, godCtxText, text_color=color.new(color.orange, 0) if godChopDay else txtColor, text_size=txtSize, text_halign=text.align_right)
                row += 1

            if showVol and enableVolumeFilter and (not isHTF):
                volRatio = volume / volumeMA if volumeMA > 0 else 0
                volStatus = '✅ Strong' if volRatio >= strongVolumeMultiplier else '✅ Good' if volRatio >= volumeMultiplier else '⚠️ Weak'
                table.cell(dashTable, 0, row, 'Volume:', text_color=txtColor, text_size=txtSize, text_halign=text.align_left)
                table.cell(dashTable, 1, row, string.format('{0}× {1}', string.tostring(volRatio, '#.#'), volStatus), text_color=txtColor, text_size=txtSize, text_halign=text.align_right)
                row += 1

            if showTrend and (not isHTF):
                trendStatus: str = "➖ Neutral"
                if isTrendUp(trendMode, close, trendVWAP, trendEMA12, trendEMACustom, trendSTDirection):
                    trendStatus = "✅ Bullish"
                elif isTrendDown(trendMode, close, trendVWAP, trendEMA12, trendEMACustom, trendSTDirection):
                    trendStatus = "⚠️ Bearish"

                table.cell(dashTable, 0, row, 'Trend:', text_color=txtColor, text_size=txtSize, text_halign=text.align_left)
                table.cell(dashTable, 1, row, trendStatus + (' (Filtered)' if enableTrendFilter else ''), text_color=txtColor, text_size=txtSize, text_halign=text.align_right)
                row += 1

            if enableHTF:
                htfTooltip: str = "Higher Timeframe Bias\n\nShows if the broader market trend supports your breakout direction.\n\n✅ Aligned: HTF trend matches breakout direction (good)\n⚠️ Counter-Trend: HTF trend opposes breakout (risky)\n➖ Neutral: No clear HTF trend\n\nBreakouts WITH HTF trend have higher success rates."
                table.cell(dashTable, 0, row, 'HTF Bias:', text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip=htfTooltip)
                table.cell(dashTable, 1, row, cachedHTFBiasText, text_color=txtColor, text_size=txtSize, text_halign=text.align_right)
                row += 1

            table.cell(dashTable, 0, row, '', text_color=txtColor, text_size=size.tiny)
            table.cell(dashTable, 1, row, '', text_color=txtColor, text_size=size.tiny)
            table.cell_set_height(dashTable, 0, row, 0.1)
            table.cell_set_height(dashTable, 1, row, 0.1)
            row += 1

            if showStatus and (not isHTF):
                table.cell(dashTable, 0, row, '📈 ORB STATUS', text_color=txtColor, text_size=txtSize, text_halign=text.align_center, bgcolor=headerColor)
                table.cell(dashTable, 1, row, '', bgcolor=headerColor)
                table.merge_cells(dashTable, 0, row, 1, row)
                row += 1

                barEndTime: float = time + currentTF_seconds * 1000
                minsFromOpenToEndOfBar: float = (barEndTime - sessionFirstBarTime) / 60000 if not na(sessionFirstBarTime) else -1

                for i in pine_range(0, array.size(allORBs) - 1):
                    orbObj = array.get(allORBs, i)
                    if not na(orbObj) and orbObj.isEnabled:
                        orbStatus: str = ""
                        orbIcon: str = ""
                        orbTooltip: str = ""

                        barCoversCompletion: bool = minsFromOpen >= 0 and minsFromOpen < orbObj.minutes and (minsFromOpenToEndOfBar >= orbObj.minutes)

                        if orbObj.isBuilding:
                            if barCoversCompletion:
                                orbStatus = "✅ Complete (This Bar)"
                                orbIcon = ""
                                orbTooltip = orbObj.name + ' Status\n\nShowing COMPLETE because current bar covers the ' + string.tostring(orbObj.minutes) + '-minute period.\n\nBar timeframe: ' + timeframe.period + '\nBar covers: ' + string.tostring(minsFromOpen, '#') + '-' + string.tostring(minsFromOpenToEndOfBar, '#') + ' minutes from open\n\nInternal state: Still building (will finalize next bar)\nDisplay: Complete (user-friendly)'
                            else:
                                orbStatus = "🔨 Building..."
                                orbIcon = ""
                                orbTooltip = orbObj.name + ' Status\n\nCurrently building the ' + string.tostring(orbObj.minutes) + '-minute range.\n\nTime elapsed: ' + string.tostring(minsFromOpen, '#') + ' minutes\nCompletion at: ' + string.tostring(orbObj.minutes) + ' minutes\n\nThe range is updating with each bar until completion.'
                        elif orbObj.isComplete:
                            cycleText: str = ""
                            if orbObj.cyclesUp > 0 or orbObj.cyclesDown > 0:
                                cycleText = string.format(' | {0}↑/{1}↓', orbObj.cyclesUp, orbObj.cyclesDown)

                            if not na(activeORB) and orbObj.name == activeORB.name:
                                orbStatus = '✅ Complete' + cycleText
                                orbIcon = " ⭐"
                                orbTooltip = orbObj.name + ' Status\n\n✅ COMPLETE and ACTIVE\n\nThis is the current ORB being used for breakout detection.\n\nRange: $' + string.tostring(orbObj.low, '#.##') + ' - $' + string.tostring(orbObj.high, '#.##') + '\nBreakouts: ' + string.tostring(orbObj.cyclesUp) + ' UP | ' + string.tostring(orbObj.cyclesDown) + ' DOWN'
                            else:
                                orbStatus = '📌 Complete' + cycleText
                                orbIcon = ""
                                orbTooltip = orbObj.name + ' Status\n\n📌 COMPLETE (not active)\n\nThis ORB completed but a larger ORB is now active.\n\nRange: $' + string.tostring(orbObj.low, '#.##') + ' - $' + string.tostring(orbObj.high, '#.##') + '\nBreakouts: ' + string.tostring(orbObj.cyclesUp) + ' UP | ' + string.tostring(orbObj.cyclesDown) + ' DOWN'

                        table.cell(dashTable, 0, row, orbObj.name + orbIcon + ':', text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip=orbTooltip)
                        table.cell(dashTable, 1, row, orbStatus, text_color=txtColor, text_size=txtSize, text_halign=text.align_right)
                        row += 1

            if enableTargets and (not na(orbEntryBar)) and (not trade_closed):
                table.cell(dashTable, 0, row, '', text_color=txtColor, text_size=size.tiny)
                table.cell(dashTable, 1, row, '', text_color=txtColor, text_size=size.tiny)
                table.cell_set_height(dashTable, 0, row, 0.1)
                table.cell_set_height(dashTable, 1, row, 0.1)
                row += 1

                isBullish__00000609__ = everHadBreakUp
                entry__00000609__ = orbEntryPrice
                sl__00000609__ = orbSLPrice
                tp1__00000609__ = orbTP1Price
                tp1_5__00000609__ = orbTP1_5Price
                tp2__00000609__ = orbTP2Price
                tp3__00000609__ = orbTP3Price
                atr__00000609__ = cachedATR

                if enablePosSizing:
                    displayShares: float = maxShares
                    displayPosValue: float = positionValue
                    displayRiskAmount: float = maxLoss

                    if na(maxShares) or na(positionValue) or na(maxLoss):
                        table.cell(dashTable, 0, row, '⚠️ Position Error:', text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip='Position size calculation failed. Check Entry/SL values.')
                        table.cell(dashTable, 1, row, 'Invalid Data', text_color=color.new(color.red, 0), text_size=txtSize, text_halign=text.align_right)
                        row += 1
                    else:
                        table.cell(dashTable, 0, row, 'Position Size:', text_color=txtColor, text_size=txtSize, text_halign=text.align_center, bgcolor=headerColor)
                        table.cell(dashTable, 1, row, '', bgcolor=headerColor)
                        table.merge_cells(dashTable, 0, row, 1, row)
                        row += 1

                        currencySymbol: str = '€' if accountCurrency == 'EUR' else '£' if accountCurrency == 'GBP' else '¥' if accountCurrency == 'JPY' else '₹' if accountCurrency == 'INR' else 'C$' if accountCurrency == 'CAD' else 'A$' if accountCurrency == 'AUD' else 'Fr.' if accountCurrency == 'CHF' else '$'

                        sharesTooltip = 'Maximum Position Size in ' + accountCurrency + '\n\nNumber of shares you can buy while staying within your risk limits.\n\nCALCULATED BY:\nRisk Amount ÷ Distance to Stop Loss\n\nEXAMPLE:\n• Risk: ' + currencySymbol + '150\n• Entry: ' + currencySymbol + '10.00\n• Stop: ' + currencySymbol + '9.50 (50¢ distance)\n• Max Shares: 300 shares (' + currencySymbol + '150 ÷ ' + currencySymbol + '0.50)\n• Position Value: ' + currencySymbol + '3,000\n\nThis ensures consistent risk management across all trades.\n\n⚠️ FIXED at breakout - does not change with price!'
                        table.cell(dashTable, 0, row, 'Max Shares:', text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip=sharesTooltip)
                        sharesText: str = 'N/A' if na(displayShares) else string.tostring(displayShares, '#')
                        displayPosValueInAcctCurr: float = na if na(displayPosValue) else displayPosValue / (exchangeRate if accountCurrency == 'INR' else 1)
                        posValueText: str = 'N/A' if na(displayPosValueInAcctCurr) else string.tostring(displayPosValueInAcctCurr, '#,###')
                        table.cell(dashTable, 1, row, sharesText + ' (' + currencySymbol + posValueText + ')', text_color=txtColor, text_size=txtSize, text_halign=text.align_right)
                        row += 1

                        riskPctOfAcct = displayRiskAmount / accountSize * 100
                        riskTooltip = 'Risk Amount in ' + accountCurrency + "\n\nTotal amount you'll lose if stop loss is hit.\n\nSHOWS:\n• " + accountCurrency + ' amount at risk\n• Percentage of total account\n\nRECOMMENDED RISK LEVELS:\n• 0.5-1% of account (conservative)\n• 1-2% of account (balanced)\n• 2-3% of account (aggressive)\n\nNEVER risk more than 3% on a single trade.\n\nThis is your MAXIMUM LOSS - stick to it!\n\n⚠️ FIXED at breakout - does not change!'
                        table.cell(dashTable, 0, row, 'Risk:', text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip=riskTooltip)
                        table.cell(dashTable, 1, row, string.format('{0}{1} ({2}%)', currencySymbol, string.tostring(displayRiskAmount / (exchangeRate if accountCurrency == 'INR' else 1), '#'), string.tostring(riskPctOfAcct, '#.#')), text_color=color.new(color.orange, 0), text_size=txtSize, text_halign=text.align_right)
                        row += 1

                        table.cell(dashTable, 0, row, '', text_color=txtColor, text_size=size.tiny, height=0.5)
                        table.cell(dashTable, 1, row, '', text_color=txtColor, text_size=size.tiny, height=0.5)
                        row += 1

                validTrade: bool = not na(entry__00000609__) and (not na(sl__00000609__)) and (entry__00000609__ > 0) and (sl__00000609__ > 0)

                if validTrade:
                    entryTooltip: str = "Entry Price\n\nYour suggested entry point for the trade.\n\nFOR LONG: ORB High level (where breakout occurred)\nFOR SHORT: ORB Low level (where breakdown occurred)\n\nThis is where you would buy/sell to enter the position.\n\nNOTE: Market entry may differ slightly due to slippage."
                    table.cell(dashTable, 0, row, 'Entry:', text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip=entryTooltip)
                    table.cell(dashTable, 1, row, string.format('${0}', string.tostring(entry__00000609__, '#.##')), text_color=txtColor, text_size=txtSize, text_halign=text.align_right)
                    row += 1
                else:
                    table.cell(dashTable, 0, row, '⚠️ Trade Data:', text_color=txtColor, text_size=txtSize, text_halign=text.align_left)
                    table.cell(dashTable, 1, row, 'Calculating...', text_color=color.new(color.orange, 0), text_size=txtSize, text_halign=text.align_right)
                    row += 1

                slDist = math.abs(entry__00000609__ - sl__00000609__)
                slPct = slDist / entry__00000609__ * 100
                stopTooltip = 'Stop Loss\n\nYour exit price if trade goes against you. Limits maximum loss per trade.\n\nCALCULATED BY: ' + stopMode + ' method\n\nDISTANCE: Shows $ distance and % from entry\n\nIMPORTANT: Always use a stop loss to protect your capital. Never hold a losing position hoping it will recover.'
                table.cell(dashTable, 0, row, 'Stop:', text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip=stopTooltip)
                table.cell(dashTable, 1, row, string.format('${0} ({1}%)', string.tostring(sl__00000609__, '#.##'), string.tostring(slPct, '#.#')), text_color=txtColor, text_size=txtSize, text_halign=text.align_right)
                row += 1

                if showTP1:
                    tp1Dist = math.abs(tp1__00000609__ - entry__00000609__)
                    tp1Pct = tp1Dist / entry__00000609__ * 100
                    tp1Label = '✅ TP1:' if orbTP1Hit else 'TP1:'
                    tp1Tooltip: str = "Take Profit 1 (1R)\n\nFirst profit target at 1× Risk distance.\n\n1R = Risk/Reward ratio of 1:1\n\nIf you risk $100, TP1 gives you $100 profit.\n\nSTRATEGY:\n• Conservative: Exit full position at TP1\n• Balanced: Take 50% profit, hold rest for TP2\n• Aggressive: Hold through for higher targets\n\n✅ = Target hit"
                    table.cell(dashTable, 0, row, tp1Label, text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip=tp1Tooltip)
                    table.cell(dashTable, 1, row, string.format('${0} (+{1}%)', string.tostring(tp1__00000609__, '#.##'), string.tostring(tp1Pct, '#.#')), text_color=txtColor, text_size=txtSize, text_halign=text.align_right)
                    row += 1

                if showTP1_5:
                    tp1_5Dist = math.abs(tp1_5__00000609__ - entry__00000609__)
                    tp1_5Pct = tp1_5Dist / entry__00000609__ * 100
                    tp1_5Label = '✅ TP1.5:' if orbTP1_5Hit else 'TP1.5:'
                    tp1_5Tooltip: str = "Take Profit 1.5 (1.5R)\n\nIntermediate target at 1.5× Risk distance.\n\n1.5R = Risk/Reward ratio of 1:1.5\n\nIf you risk $100, TP1.5 gives you $150 profit.\n\nUSEFUL FOR:\n• Scaling out of positions gradually\n• Capturing middle-ground profits\n• Adjusting to market volatility\n\n✅ = Target hit"
                    table.cell(dashTable, 0, row, tp1_5Label, text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip=tp1_5Tooltip)
                    table.cell(dashTable, 1, row, string.format('${0} (+{1}%)', string.tostring(tp1_5__00000609__, '#.##'), string.tostring(tp1_5Pct, '#.#')), text_color=txtColor, text_size=txtSize, text_halign=text.align_right)
                    row += 1

                if showTP2:
                    tp2Dist = math.abs(tp2__00000609__ - entry__00000609__)
                    tp2Pct = tp2Dist / entry__00000609__ * 100
                    tp2Label = '✅ TP2:' if orbTP2Hit else 'TP2:'
                    tp2Tooltip: str = "Take Profit 2 (2R)\n\nMain profit target at 2× Risk distance.\n\n2R = Risk/Reward ratio of 1:2\n\nIf you risk $100, TP2 gives you $200 profit.\n\nThis is the STANDARD target for most ORB traders.\n\nSTRATEGY:\n• Exit remaining position at TP2\n• Move stop to breakeven after TP1 hit\n• Let runners go to TP3 if strong momentum\n\n✅ = Target hit"
                    table.cell(dashTable, 0, row, tp2Label, text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip=tp2Tooltip)
                    table.cell(dashTable, 1, row, string.format('${0} (+{1}%)', string.tostring(tp2__00000609__, '#.##'), string.tostring(tp2Pct, '#.#')), text_color=txtColor, text_size=txtSize, text_halign=text.align_right)
                    row += 1

                if showTP3:
                    tp3Dist = math.abs(tp3__00000609__ - entry__00000609__)
                    tp3Pct = tp3Dist / entry__00000609__ * 100
                    tp3Label = '✅ TP3:' if orbTP3Hit else 'TP3:'
                    tp3Tooltip: str = "Take Profit 3 (3R)\n\nExtended profit target at 3× Risk distance.\n\n3R = Risk/Reward ratio of 1:3\n\nIf you risk $100, TP3 gives you $300 profit.\n\nONLY FOR:\n• Strong trending days\n• High momentum breakouts\n• Extended runners\n\nMOST TRADES won't reach TP3.\n\nSTRATEGY: Trail stop or use for 'lottery tickets'\n\n✅ = Target hit"
                    table.cell(dashTable, 0, row, tp3Label, text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip=tp3Tooltip)
                    table.cell(dashTable, 1, row, string.format('${0} (+{1}%)', string.tostring(tp3__00000609__, '#.##'), string.tostring(tp3Pct, '#.#')), text_color=txtColor, text_size=txtSize, text_halign=text.align_right)
                    row += 1

                if showRisk:
                    riskDist = math.abs(entry__00000609__ - sl__00000609__)

                    rrTarget: float = tp3__00000609__ if orbTP3Hit and showTP3 else tp2__00000609__ if orbTP2Hit and showTP2 else tp1_5__00000609__ if orbTP1_5Hit and showTP1_5 else tp1__00000609__ if orbTP1Hit and showTP1 else tp3__00000609__ if showTP3 else tp2__00000609__ if showTP2 else tp1_5__00000609__ if showTP1_5 else tp1__00000609__ if showTP1 else tp2__00000609__
                    anyHit: bool = orbTP3Hit or orbTP2Hit or orbTP1_5Hit or orbTP1Hit

                    rewardDist = math.abs(rrTarget - entry__00000609__)
                    rrRatio = rewardDist / riskDist if riskDist > 0 else 0
                    rrStatus = '✅' if anyHit else '⭐' if rrRatio >= 2.0 else '⚠️' if rrRatio >= 1.5 else '❌'

                    table.cell(dashTable, 0, row, 'R/R Ratio:', text_color=txtColor, text_size=txtSize, text_halign=text.align_left)
                    table.cell(dashTable, 1, row, string.format('1:{0} {1}', string.tostring(rrRatio, '#.#'), rrStatus), text_color=txtColor, text_size=txtSize, text_halign=text.align_right)
                    row += 1

            if enableTargets and (everHadBreakUp or everHadBreakDown) and trade_closed and (last_trade_result != ''):
                table.cell(dashTable, 0, row, '', text_color=txtColor, text_size=size.tiny)
                table.cell(dashTable, 1, row, '', text_color=txtColor, text_size=size.tiny)
                table.cell_set_height(dashTable, 0, row, 0.1)
                table.cell_set_height(dashTable, 1, row, 0.1)
                row += 1

                lastTradeTooltip: str = "Last Trade Result\n\nShows the outcome of the most recent trade.\n\n✅ = Target hit (profit)\n❌ = Stop loss hit (loss)\n\nR = Risk/Reward ratio\n+2R means you made 2x your risk\n-1R means you lost your risk amount"
                if not na(dashTable):
                    table.clear(dashTable, 0, row, 1, row)

                table.cell(dashTable, 0, row, 'Last Trade:', text_color=txtColor, text_size=txtSize, text_halign=text.align_left, tooltip=lastTradeTooltip)
                table.cell(dashTable, 1, row, last_trade_result, text_color=txtColor, text_size=txtSize, text_halign=text.align_right)
                row += 1
        elif not na(dashTable):
            isDarkTheme__00000617__: bool = dashTheme == 'Dark'
            bgColor__00000617__: Color = color.new(color.black, 0) if isDarkTheme__00000617__ else color.new(color.white, 10)
            txtColor__00000617__: Color = color.white if isDarkTheme__00000617__ else color.black
            headerColor__00000617__: Color = color.new(color.aqua, 30) if isDarkTheme__00000617__ else color.new(color.silver, 30)

            headerTitle: str = sessionIcon + ' ORB DASHBOARD'
            headerTooltip: str = 'ORB Dashboard\n\n' + sessionStatusText + '\n\nMarket is currently closed.\n\nDisplay hours: 04:00-20:00\nCurrent time is outside this window.\n\nThe indicator will resume when the next session begins.'

            table.cell(dashTable, 0, row, headerTitle, text_color=txtColor__00000617__, text_size=txtSize, text_halign=text.align_center, bgcolor=headerColor__00000617__, tooltip=headerTooltip)
            table.cell(dashTable, 1, row, '', bgcolor=headerColor__00000617__)
            table.merge_cells(dashTable, 0, row, 1, row)
            row += 1

            notInSessionMsg: str = sessionStatusText
            notInSessionTooltip: str = 'Pre-Market Session\n\n📍 Trading day has started\n⏰ ORB will begin building at 09:30\n\nCurrent status:\n• Pre-market trading active (04:00-09:30)\n• Regular session starts at 09:30\n• ORB periods will track first 5, 15, 30, 60 minutes\n\nThe dashboard will show full data once ORB begins.' if sessionStatusText == 'PRE-MARKET - Waiting for ORB' else 'Market Closed\n\nCurrent time is outside display hours (04:00-20:00).\n\nORB tracking will resume at next session open.\n\nTo see data from the last session, scroll back to regular or extended trading hours on the chart.'
            table.cell(dashTable, 0, row, notInSessionMsg, text_color=txtColor__00000617__, text_size=txtSize, text_halign=text.align_center, bgcolor=color.new(color.gray, 90), tooltip=notInSessionTooltip)
            table.cell(dashTable, 1, row, '', bgcolor=color.new(color.gray, 90))
            table.merge_cells(dashTable, 0, row, 1, row)
            row += 1

        if session_trades > 0 and showFullDashboard and (not na(dashTable)):
            winRate: float = session_wins / session_trades * 100

            statsText: str = string.format('Stats: {0}✅ | {1}❌ | {2}R | WR: {3}%', string.tostring(session_wins), string.tostring(session_losses), string.tostring(session_total_rr, '#.#'), string.tostring(winRate, '#'))

            statsTooltip: str = "══════════════════════════════\n"
            statsTooltip += "📊 SESSION STATISTICS - Detailed View\n"
            statsTooltip += "══════════════════════════════\n\n"
            statsTooltip += 'TRADES TODAY: ' + string.tostring(session_trades) + '\n'
            statsTooltip += '├─ ✅ Wins: ' + string.tostring(session_wins) + ' (' + string.tostring(winRate, '#.#') + '%)\n'
            statsTooltip += '├─ ❌ Losses: ' + string.tostring(session_losses) + ' (' + string.tostring(100 - winRate, '#.#') + '%)\n'
            statsTooltip += '└─ ⚖️ Win Rate: ' + string.tostring(winRate, '#.#') + '%\n\n'
            statsTooltip += "══════════════════════════════\n"
            statsTooltip += "R PERFORMANCE:\n"
            statsTooltip += '├─ 💰 Total R: ' + string.tostring(session_total_rr, '#.##') + 'R\n'

            if session_wins > 0:
                avgWin: float = (session_total_rr + session_losses) / session_wins if session_total_rr > 0 else 0.0
                if avgWin > 0:
                    statsTooltip += '├─ 📈 Avg Win: ' + string.tostring(avgWin, '#.##') + 'R\n'

            if session_losses > 0:
                avgLoss: float = -1.0
                statsTooltip += '├─ 📉 Avg Loss: ' + string.tostring(avgLoss, '#.##') + 'R\n'

            statsTooltip += '├─ 🏆 Best Trade: ' + string.tostring(session_best_r, '#.##') + 'R\n'

            if session_worst_r < 0:
                statsTooltip += '└─ 💀 Worst Trade: ' + string.tostring(session_worst_r, '#.##') + 'R\n'

            statsTooltip += "══════════════════════════════\n"
            statsTooltip += "💡 TIP: Target 2:1 R/R minimum\n"

            if session_total_rr > 0:
                statsTooltip += "    Current session: PROFITABLE ⭐\n"
            elif session_total_rr == 0:
                statsTooltip += "    Current session: BREAKEVEN ⚖️\n"
            else:
                statsTooltip += "    Current session: NEGATIVE ⚠️\n"

            statsRowColor: Color = color.new(color.green, 92) if session_total_rr > 0 else color.new(color.red, 92) if session_total_rr < 0 else color.new(color.gray, 92)

            table.cell(dashTable, 0, row, statsText, text_color=color.new(color.white, 0), text_size=txtSize, text_halign=text.align_center, bgcolor=statsRowColor, tooltip=statsTooltip)
            table.cell(dashTable, 1, row, '', bgcolor=statsRowColor)
            table.merge_cells(dashTable, 0, row, 1, row)
            row += 1

    alertcondition(alertBreakUpTriggered and enableAlerts and alertBreakouts, title='🔼 ORB Breakout UP', message='{{ticker}} - Breakout ABOVE ORB High @ ${{close}}')

    alertcondition(alertBreakDownTriggered and enableAlerts and alertBreakouts, title='🔽 ORB Breakout DOWN', message='{{ticker}} - Breakout BELOW ORB Low @ ${{close}}')

    alertcondition(alertRetestUpTriggered and enableAlerts and alertRetests, title='🔁 ORB Retest UP', message='{{ticker}} - Retesting ORB after breakout UP @ ${{close}}')

    alertcondition(alertRetestDownTriggered and enableAlerts and alertRetests, title='🔁 ORB Retest DOWN', message='{{ticker}} - Retesting ORB after breakout DOWN @ ${{close}}')

    alertcondition(alertFailedUpTriggered and enableAlerts and alertFailedBreaks, title='⚠️ ORB Failed Break UP', message='{{ticker}} - Failed breakout UP, back inside ORB @ ${{close}}')

    alertcondition(alertFailedDownTriggered and enableAlerts and alertFailedBreaks, title='⚠️ ORB Failed Break DOWN', message='{{ticker}} - Failed breakout DOWN, back inside ORB @ ${{close}}')

    alertcondition(alertStageCompleteTriggered and enableAlerts and alertStageComplete, title='✅ ORB Stage Complete', message='{{ticker}} - ORB Stage completed')

    alertcondition(alertEntryTriggered and enableAlerts and alertTradeManagement and enableTargets, title='🎯 ENTRY Triggered', message='{{ticker}} - ENTRY @ ${{close}} | Trade setup activated')

    alertcondition(alertSLTriggered and enableAlerts and alertTradeManagement and enableTargets, title='❌ STOP LOSS Hit', message='{{ticker}} - STOP LOSS HIT @ ${{close}} | Trade closed with loss')

    alertcondition(alertTP1Triggered and enableAlerts and alertTradeManagement and enableTargets and showTP1, title='✅ TP1 Hit (1R)', message='{{ticker}} - TP1 HIT @ ${{close}} | 1R profit target reached')

    alertcondition(alertTP1_5Triggered and enableAlerts and alertTradeManagement and enableTargets and showTP1_5, title='✅ TP1.5 Hit (1.5R)', message='{{ticker}} - TP1.5 HIT @ ${{close}} | 1.5R profit target reached')

    alertcondition(alertTP2Triggered and enableAlerts and alertTradeManagement and enableTargets and showTP2, title='✅ TP2 Hit (2R)', message='{{ticker}} - TP2 HIT @ ${{close}} | 2R profit target reached')

    alertcondition(alertTP3Triggered and enableAlerts and alertTradeManagement and enableTargets and showTP3, title='✅ TP3 Hit (3R)', message='{{ticker}} - TP3 HIT @ ${{close}} | 3R profit target reached')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
