"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from enum import StrEnum as Enum
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, barstate, box, chart, close,
    color, fill, format, high, input, label, line, location, low, math, na, ohlc4, open, plot,
    plotshape, position, script, shape, size, string, syminfo, ta, table, text, time, volume, xloc,
    yloc
)
from pynecore.types import Box, Color, Label, Line, NA, Persistent, PersistentSeries, Series, Table


class AltSource(Enum):
    default_src = 'Default Source'
    formula_1 = '(open + close +3 * (high + low)) / 8'
    formula_2 = 'close + high + low -2 * open'
    formula_3 = '(close +5 * (high + low) -7 * (open)) / 4'
    formula_4 = '(open + close +5 * (high + low)) / 12'
    formula_5 = '(close > open ? high : low)'
    heiken_ashi = 'Heiken-Ashi'


class VolOscType(Enum):
    tfs = 'TFS Volume Oscillator'
    obv = 'On Balance Volume'
    klinger = 'Klinger Volume Oscillator'
    cumulative = 'Cumulative Volume Oscillator'
    vzo = 'Volume Zone Oscillator'


class VolRatioType(Enum):
    obv = 'On Balance Volume'
    cum_delta = 'Cumulative Volume Delta'
    pvt = 'Price Volume Trend'


class KumoFillStyle(Enum):
    solid = 'Solid'
    gradient = 'Gradient'


class ChikouMode(Enum):
    fixed = 'Fixed'
    adaptive = 'Adaptive'


class SrLayout(Enum):
    line_mode = 'Line'
    zone_mode = 'Zone'


class SrPlacement(Enum):
    wick = 'Wick'
    body = 'Body'
    median = 'Median'


class SrLabelSize(Enum):
    tiny = 'Tiny'
    small = 'Small'
    normal = 'Normal'


class BarColorMode(Enum):
    disabled = 'Disabled'
    vs_tkkj = 'Price vs TK/KJ'
    vs_kumo = 'Price vs Kumo'
    confluence = 'Confluence Strength'
    regime = 'Current Regime'
    kumo_bias = 'Kumo Future Bias'


class PanelPosition(Enum):
    top_right = 'Top Right'
    bottom_right = 'Bottom Right'
    top_left = 'Top Left'
    bottom_left = 'Bottom Left'


class PanelTextSize(Enum):
    tiny = 'Tiny'
    small = 'Small'
    normal = 'Normal'
    large = 'Large'


class CycleRange(Enum):
    basic = 'Basic (9/17/26)'
    extended = 'Extended (+33/42/51)'
    full = 'Full (+65→257)'


class KihonAnchor(Enum):
    signals = 'Signals (▲▼)'
    tk_cross = 'Tenkan Cross'
    kj_cross = 'Kijun Cross'
    tk_kj_cross = 'TK x KJ Cross'
    kumo_change = 'Kumo Change'
    swing_high = 'Swing Highs'
    swing_low = 'Swing Lows'
    swings = 'Swings (H+L)'
    wave = 'Wave Completion'


class Preset(Enum):
    classic = 'Classic 9/26/52/26'
    five_d = '5D 8/22/44/22'
    crypto = 'Crypto 10/30/60/30'
    slow = 'Slow 20/60/120/60'
    custom = 'Custom (Adaptive Lengths)'


@udt
class SwingPoint:
    bar_idx: int = na(int)
    bar_tm: int = na(int)
    price: float = na(float)
    dir: int = na(int)


GRP_SOURCE: str = "SOURCE"
GRP_CORE: str = "ICHIMOKU CORE (一目均衡表)"
GRP_ADAPTIVE: str = "ADAPTIVE LENGTHS"
GRP_VOLUME: str = "VOLUME ANALYSIS"
GRP_VOLATILITY: str = "VOLATILITY (ATR)"
GRP_FILTERS: str = "SIGNAL FILTERS"
GRP_SR_ZONES: str = "SUPPORT & RESISTANCE"
GRP_TK_RANGE: str = "TK-RANGE (転換・基準)"
GRP_SWING: str = "HOSODA THEORIES — SWING DETECTION (スイング)"
GRP_WAVE: str = "HOSODA THEORIES — WAVE THEORY (波動論)"
GRP_PRICE_THEORY: str = "HOSODA THEORIES — PRICE THEORY (値幅観測論)"
GRP_TIME_THEORY: str = "HOSODA THEORIES — TIME THEORY (時間論)"
GRP_TXP: str = "HOSODA THEORIES — TIME x PRICE CONFLUENCE (時間・値幅合流)"
GRP_BAR_COLOR: str = "BAR COLORS"
GRP_PANEL: str = "PANEL"
GRP_PANEL_COLORS: str = "PANEL COLORS"


@script.indicator("Ichimoku Kinko Hyo (一目均衡表)", overlay=True, max_bars_back=5000, max_lines_count=500, max_labels_count=500, max_boxes_count=500)
def main(
    src_price: Series[float] = input.source(close, "Source", group=GRP_SOURCE, tooltip="Primary price source used for all Ichimoku calculations.\nDefault: Close. Other options (HL2, HLC3, etc.) can smooth signals but may reduce responsiveness."),
    alt_source_formula=input.enum(AltSource.default_src, "Alternative Source", group=GRP_SOURCE, tooltip="Alternative price formulas for Ichimoku calculations.\n• Default Source: Uses the Source selected above\n• Other options: Custom weighted formulas combining OHLC values for smoother or more reactive signals\n• Heiken-Ashi: Smoothed candle-based calculation\nAdvanced users may experiment with different formulas to reduce noise."),
    wma_smoothing=input.bool(True, "SWMA Smoothing", group=GRP_SOURCE, tooltip="Applies a Symmetrically Weighted Moving Average to the price source before Ichimoku calculations.\nSWMA uses balanced weights across 4 bars, giving more importance to the two middle bars. This produces cleaner signals with less noise, at the cost of slightly more lag."),
    preset=input.enum(Preset.custom, "Preset", group=GRP_CORE, tooltip="Classic/5D/Crypto/Slow use standard Ichimoku presets.\nCustom (Adaptive Lengths) uses your dynamic bounds & offset.\nIn Custom mode, each Ichimoku line (Tenkan, Kijun, Senkou, Chikou) has its own independent adaptive length engine based on its filters."),
    preset_panel_only=input.bool(False, "Preset → Panel Only", group=GRP_CORE, tooltip="When enabled, preset (Classic/5D/Crypto/Slow) applies ONLY to the Panel calculations.\n• Disabled (default): Preset applies to both Chart and Panel\n• Enabled: Chart uses Custom adaptive lengths, Panel uses preset lengths\nUseful for comparing custom adaptive setup against standard Ichimoku consensus."),
    line_divider=input.int(1, "Reactivity Divider", minval=1, maxval=4, group=GRP_CORE, tooltip="Global fine-tuning tool that affects both Tenkan-Sen and Kijun-Sen calculations.\nDivides each line's length to create a shorter reactive sub-component, then blends both averages.\n• 1 = Standard (default, no sub-component effect)\n• 2 = 2x more reactive\n• 3-4 = Very reactive (experimental)\nApplies to both chart lines and panel consensus calculations."),
    show_tenkan=input.bool(True, "Tenkan-Sen", group=GRP_CORE, inline="tenkan", tooltip="Tenkan-Sen = Toggle visibility of the Tenkan-Sen (Conversion Line).\nColor = Line color on chart."),
    tenkan_color=input.color(color.new(color.new('#007FFF'), 0), "", group=GRP_CORE, inline="tenkan", tooltip=""),
    show_kijun=input.bool(True, "Kijun-Sen    ", group=GRP_CORE, inline="kijun", tooltip="Kijun-Sen = Toggle visibility of the Kijun-Sen (Base Line).\nColor = Line color on chart."),
    kijun_color=input.color(color.new(color.new('#E53935'), 0), "", group=GRP_CORE, inline="kijun", tooltip=""),
    show_price_labels=input.bool(True, "Show TK/KJ Labels", group=GRP_CORE, tooltip="Display smart price labels at the end of Tenkan and Kijun lines.\nLABEL CONTENT:\n• TK: Price + Spread vs KJ in () — momentum indicator\n• KJ: Price + Distance from Price in [] — mean reversion ref\nLABEL FEATURES:\n• Direction arrows (↗↘→) show line trend\n• Dynamic colors: Teal=Support, Red=Resistance, Orange=Equilibrium\n• Auto-merge into single label when TK ≈ KJ\n• Rich tooltip with detailed analysis on hover"),
    tkkj_label_bull_color=input.color(color.new(color.new('#26A69A'), 70), "Bullish", group=GRP_CORE, inline="tkkjlbl", tooltip="Bullish = Label background when price is ABOVE the line (support level).\nBearish = Label background when price is BELOW the line (resistance level).\nEquilibrium = Label background when TK ≈ KJ (equilibrium state)."),
    tkkj_label_bear_color=input.color(color.new(color.new('#EF5350'), 70), "Bearish", group=GRP_CORE, inline="tkkjlbl"),
    tkkj_label_neutral_color=input.color(color.new(color.new('#FF9800'), 70), "Equilibrium", group=GRP_CORE, inline="tkkjlbl", tooltip=""),
    show_chikou=input.bool(True, "Chikou Span (遅行)", group=GRP_CORE, tooltip="Toggle visibility of the Chikou Span (Lagging Span).\nThe Chikou plots current price shifted back in time, allowing visual comparison with past price action. Color changes based on position relative to past price (Bull/Bear/Equilibrium colors below)."),
    chikou_mode=input.enum(ChikouMode.adaptive, "Chikou Offset (遅行)", group=GRP_CORE, tooltip="How the Chikou Span offset is determined:\nFIXED (Orthodox Hosoda): Uses preset offset (26, 22, 30, etc.), represents fixed market cycles, recommended for traditional Ichimoku.\nADAPTIVE (Dynamic): Uses adaptive Chikou length, offset adjusts with market conditions, more responsive but less orthodox."),
    chikou_bull_color=input.color(color.new(color.new('#26A69A'), 0), "Bullish", group=GRP_CORE, inline="chikoucolor"),
    chikou_bear_color=input.color(color.new(color.new('#EF5350'), 0), "Bearish", group=GRP_CORE, inline="chikoucolor"),
    chikou_neutral_color=input.color(color.new(color.new('#FF9800'), 0), "Equilibrium", group=GRP_CORE, inline="chikoucolor"),
    chikou_linewidth=input.int(1, "Chikou Line Width", minval=1, maxval=5, group=GRP_CORE, tooltip="Thickness of the Chikou Span line on chart.\nApplies to both Fixed and Adaptive offset modes.\n• 1 = Default (thin, matches TK/KJ)\n• 2-3 = Medium emphasis\n• 4-5 = Strong visual prominence"),
    show_senkou_a=input.bool(True, "Senkou Span A", group=GRP_CORE, inline="senkou", tooltip="Senkou Span A = Toggle visibility of the Leading Span A line.\nSenkou Span B = Toggle visibility of the Leading Span B line."),
    show_senkou_b=input.bool(True, "Senkou Span B", group=GRP_CORE, inline="senkou", tooltip=""),
    kumo_bull_color=input.color(color.new(color.new('#26A69A'), 0), "Bullish", group=GRP_CORE, inline="senkoucolor"),
    kumo_bear_color=input.color(color.new(color.new('#EF5350'), 0), "Bearish", group=GRP_CORE, inline="senkoucolor"),
    kumo_neutral_color=input.color(color.new(color.new('#B0BEC5'), 0), "Equilibrium", group=GRP_CORE, inline="senkoucolor"),
    kumo_fill_enabled=input.bool(True, "Kumo Fill Transparency       ", group=GRP_CORE, inline="kumo", tooltip="Kumo Fill = Toggle Kumo (cloud) shading between Senkou Span A and B.\nTransparency = How see-through the fill is (1 = nearly solid, 100 = fully invisible)."),
    kumo_fill_transparency=input.int(75, "", minval=1, maxval=100, group=GRP_CORE, inline="kumo", tooltip=""),
    kumo_fill_style=input.enum(KumoFillStyle.gradient, "Kumo Fill Style", group=GRP_CORE, tooltip="Visual style for Kumo (cloud) fill:\n• Solid: Single color based on Kumo direction\n• Gradient: Smooth strength-based 2-color gradient"),
    show_signals=input.bool(True, "Show Signals", group=GRP_CORE, tooltip="Toggle signal markers (▲▼) on chart.\nSignals mark structural trend reversals where all enabled Ichimoku filters align.\n• ▲ Triangle Up = Bullish reversal\n• ▼ Triangle Down = Bearish reversal\nThese signals also anchor S/R zones and can optionally anchor Kihon Sūchi time cycles (see Anchor Mode in Time Theory)."),
    bull_event_color=input.color(color.new(color.new('#26A69A'), 0), "Bullish Event", group=GRP_CORE, inline="evt_clr", tooltip="Global colors for bullish/bearish events.\nApplied to:\n• Signal markers (▲▼)\n• S/R Zones (Support/Resistance)\n• Time Theory (Kihon & Taito Sūchi projections)\n• Swing markers (●)"),
    bear_event_color=input.color(color.new(color.new('#EF5350'), 0), "Bearish Event", group=GRP_CORE, inline="evt_clr", tooltip=""),
    tk_min_length=input.int(9, "Tenkan Min Length", minval=1, group=GRP_ADAPTIVE, tooltip="Lower bound for adaptive length — contracts toward this value when adaptive filters (Volume/ATR/Chikou Trend) confirm.\n⚠ If ALL filters are disabled, length stays at Max Length (no contraction)."),
    tk_max_length=input.int(30, "Tenkan Max Length", minval=1, group=GRP_ADAPTIVE, tooltip="Upper bound for adaptive length — expands toward this value when adaptive filters don't confirm.\nThe length oscillates between Min and Max based on market conditions."),
    __input_33__=input.float(96.85, "Tenkan Smoothing %", minval=0, maxval=100, group=GRP_ADAPTIVE, tooltip="Controls how smoothly the Tenkan-Sen adaptive length transitions between Min and Max.\nHigher values (closer to 100%) = slower, smoother transitions.\nLower values = faster, more reactive length changes.\nDefault 96.85% provides gradual adaptation."),
    tk_vol_filter=input.bool(True, "Volume", group=GRP_ADAPTIVE, inline="tkf", tooltip="Tenkan-Sen adaptive length filters.\nVolume = Use volume oscillator to contract/expand length.\nATR = Use ATR volatility to contract/expand length.\nChikou Trend = Use Chikou trend to contract/expand length.\n⚠ If ALL are disabled, length stays at Max Length (no contraction)."),
    tk_atr_filter=input.bool(True, "ATR", group=GRP_ADAPTIVE, inline="tkf"),
    tk_chikou_filter=input.bool(True, "Chikou Trend", group=GRP_ADAPTIVE, inline="tkf", tooltip=""),
    kj_min_length=input.int(20, "Kijun Min Length", minval=1, group=GRP_ADAPTIVE, tooltip="Lower bound for adaptive length — contracts toward this value when adaptive filters (Volume/ATR/Chikou Trend) confirm.\n⚠ If ALL filters are disabled, length stays at Max Length (no contraction)."),
    kj_max_length=input.int(60, "Kijun Max Length", minval=1, group=GRP_ADAPTIVE, tooltip="Upper bound for adaptive length — expands toward this value when adaptive filters don't confirm.\nThe length oscillates between Min and Max based on market conditions."),
    __input_39__=input.float(96.85, "Kijun Smoothing %", minval=0, maxval=100, group=GRP_ADAPTIVE, tooltip="Controls how smoothly the Kijun-Sen adaptive length transitions between Min and Max.\nHigher values (closer to 100%) = slower, smoother transitions.\nLower values = faster, more reactive length changes.\nDefault 96.85% provides gradual adaptation."),
    kj_vol_filter=input.bool(True, "Volume", group=GRP_ADAPTIVE, inline="kjf", tooltip="Kijun-Sen adaptive length filters.\nVolume = Use volume oscillator to contract/expand length.\nATR = Use ATR volatility to contract/expand length.\nChikou Trend = Use Chikou trend to contract/expand length.\n⚠ If ALL are disabled, length stays at Max Length (no contraction)."),
    kj_atr_filter=input.bool(True, "ATR", group=GRP_ADAPTIVE, inline="kjf"),
    kj_chikou_filter=input.bool(True, "Chikou Trend", group=GRP_ADAPTIVE, inline="kjf", tooltip=""),
    ch_min_length=input.int(26, "Chikou Min Length", minval=1, group=GRP_ADAPTIVE, tooltip="Lower bound for adaptive length — contracts toward this value when adaptive filters (Volume/ATR/Chikou Trend) confirm.\n⚠ If ALL filters are disabled, length stays at Max Length (no contraction)."),
    ch_max_length=input.int(50, "Chikou Max Length", minval=1, group=GRP_ADAPTIVE, tooltip="Upper bound for adaptive length — expands toward this value when adaptive filters don't confirm.\nThe length oscillates between Min and Max based on market conditions."),
    __input_45__=input.float(96.85, "Chikou Smoothing %", minval=0, maxval=100, group=GRP_ADAPTIVE, tooltip="Controls how smoothly the Chikou Span adaptive length transitions between Min and Max.\nHigher values (closer to 100%) = slower, smoother transitions.\nLower values = faster, more reactive length changes.\nDefault 96.85% provides gradual adaptation."),
    ch_filter_period=input.int(25, "Chikou Filter Period", minval=1, group=GRP_ADAPTIVE, tooltip="Lookback period for the Chikou breakout filter.\nDetermines how many past bars the Chikou Span is compared against. Used by adaptive length engine, signal Chikou Trend filter, and bar color confluence.\nHigher values detect longer-term breakouts, lower values are more responsive."),
    ch_vol_filter=input.bool(True, "Volume", group=GRP_ADAPTIVE, inline="chf", tooltip="Chikou Span adaptive length filters.\nVolume = Use volume oscillator to contract/expand length.\nATR = Use ATR volatility to contract/expand length.\nChikou Trend = Use Chikou trend to contract/expand length.\n⚠ If ALL are disabled, length stays at Max Length (no contraction)."),
    ch_atr_filter=input.bool(True, "ATR", group=GRP_ADAPTIVE, inline="chf"),
    ch_trend_filter=input.bool(True, "Chikou Trend", group=GRP_ADAPTIVE, inline="chf", tooltip=""),
    sk_min_length=input.int(50, "Senkou Min Length", minval=1, group=GRP_ADAPTIVE, tooltip="Lower bound for adaptive length — contracts toward this value when adaptive filters (Volume/ATR/Chikou Trend) confirm.\n⚠ If ALL filters are disabled, length stays at Max Length (no contraction)."),
    sk_max_length=input.int(120, "Senkou Max Length", minval=1, group=GRP_ADAPTIVE, tooltip="Upper bound for adaptive length — expands toward this value when adaptive filters don't confirm.\nThe length oscillates between Min and Max based on market conditions."),
    __input_52__=input.float(96.85, "Senkou Smoothing %", minval=0, maxval=100, group=GRP_ADAPTIVE, tooltip="Controls how smoothly the Senkou Span adaptive length transitions between Min and Max.\nHigher values (closer to 100%) = slower, smoother transitions.\nLower values = faster, more reactive length changes.\nDefault 96.85% provides gradual adaptation."),
    sk_offset_length=input.int(26, "Senkou Span Offset", minval=1, group=GRP_ADAPTIVE, tooltip="Offset (in bars) for Senkou Span projection into the future.\nAlso used for Chikou Span when Chikou Offset (遅行) is set to Fixed.\nPreset values: Classic=26, 5D=22, Crypto=30, Slow=60"),
    sk_vol_filter=input.bool(True, "Volume", group=GRP_ADAPTIVE, inline="sn_chks", tooltip="Senkou Span adaptive length filters.\nVolume = Use volume oscillator to contract/expand length.\nATR = Use ATR volatility to contract/expand length.\nChikou Trend = Use Chikou trend to contract/expand length.\n⚠ If ALL are disabled, length stays at Max Length (no contraction)."),
    sk_atr_filter=input.bool(True, "ATR", group=GRP_ADAPTIVE, inline="sn_chks"),
    sk_chikou_filter=input.bool(True, "Chikou Trend", group=GRP_ADAPTIVE, inline="sn_chks", tooltip=""),
    vol_osc_type=input.enum(VolOscType.obv, "Volume Oscillator Type", group=GRP_VOLUME, tooltip="Main volume oscillator for signal generation.\n• On Balance Volume (OBV): Tracks cumulative volume flow\n• TFS: Normalized accumulation indicator\n• Klinger: Trend-based with smoothing (uses Fast/Slow Length below)\n• Cumulative: Multi-method volume delta (uses RVSI parameters below)\n• Volume Zone Oscillator (VZO): Ranges from -100 to +100 (uses VZO Length below)"),
    vol_osc_type_tk=input.enum(VolOscType.obv, "├─ Tenkan Oscillator", group=GRP_VOLUME, tooltip="Volume oscillator for Tenkan-Sen adaptive length calculation.\nSame parameter dependencies as main oscillator."),
    vol_osc_type_kj=input.enum(VolOscType.obv, "├─ Kijun Oscillator", group=GRP_VOLUME, tooltip="Volume oscillator for Kijun-Sen adaptive length calculation.\nSame parameter dependencies as main oscillator."),
    vol_osc_type_sk=input.enum(VolOscType.obv, "├─ Senkou Oscillator", group=GRP_VOLUME, tooltip="Volume oscillator for Senkou Span adaptive length calculation.\nSame parameter dependencies as main oscillator."),
    vol_osc_type_ch=input.enum(VolOscType.obv, "└─ Chikou Oscillator", group=GRP_VOLUME, tooltip="Volume oscillator for Chikou Span adaptive length calculation.\nSame parameter dependencies as main oscillator."),
    vol_peak_threshold=input.float(50, "Volume Breakout Threshold", minval=1, group=GRP_VOLUME, tooltip="Threshold level for volume breakout signals.\n⚠ Works best with Volume Zone Oscillator (VZO) which has a fixed -100 to +100 scale. Other oscillators have unbounded scales, making a fixed threshold less effective.\nRecommended for VZO: 40-60 (default 50)"),
    vol_fast_length=input.int(34, "┌─ Klinger Fast Length", minval=1, group=GRP_VOLUME, tooltip="⚠ CONDITIONAL PARAMETER\nOnly used when oscillator type = 'Klinger Volume Oscillator'\nFast smoothing period for Klinger calculation.\nSmaller values react faster to volume changes.\nDefault: 34"),
    vol_slow_length=input.int(55, "└─ Klinger Slow Length", minval=1, group=GRP_VOLUME, tooltip="⚠ CONDITIONAL PARAMETER\nOnly used when oscillator type = 'Klinger Volume Oscillator'\nSlow smoothing period for Klinger calculation.\nLarger values provide a steadier baseline.\nDefault: 55"),
    vol_zone_length=input.int(21, "─── VZO Length", minval=1, group=GRP_VOLUME, tooltip="⚠ CONDITIONAL PARAMETER\nOnly used when oscillator type = 'Volume Zone Oscillator'\nSmoothing period for VZO calculation.\nSmaller = more reactive, Larger = smoother.\nDefault: 21"),
    vol_ratio_type=input.enum(VolRatioType.pvt, "┌─ RVSI Base Type", group=GRP_VOLUME, tooltip="⚠ CONDITIONAL PARAMETER\nOnly used when oscillator type = 'Cumulative Volume Oscillator'\nBase calculation method for cumulative volume:\n• On Balance Volume: Classic directional volume flow\n• Cumulative Volume Delta: Net buying vs selling pressure\n• Price Volume Trend: Volume weighted by price changes (default)"),
    vol_ratio_length=input.int(14, "─── TFS Length", minval=1, group=GRP_VOLUME, tooltip="⚠ CONDITIONAL PARAMETER\nOnly used when oscillator type = 'TFS Volume Oscillator'\nLookback period for TFS accumulation calculation.\nDefault: 14"),
    vol_ema_length_1=input.int(8, "├─ RVSI EMA Fast", minval=1, group=GRP_VOLUME, tooltip="⚠ CONDITIONAL PARAMETER\nOnly used when oscillator type = 'Cumulative Volume Oscillator'\nFast smoothing period for cumulative volume.\nSmaller = more reactive to recent volume changes.\nDefault: 8"),
    vol_ema_length_2=input.int(21, "└─ RVSI EMA Slow", minval=1, group=GRP_VOLUME, tooltip="⚠ CONDITIONAL PARAMETER\nOnly used when oscillator type = 'Cumulative Volume Oscillator'\nSlow smoothing period for cumulative volume.\nLarger = smoother baseline for comparison.\nDefault: 21"),
    atr_fast_length=input.int(14, "ATR Fast Length", group=GRP_VOLATILITY, tooltip="Fast ATR period for volatility comparison. Used to detect expanding volatility when fast ATR > slow ATR."),
    atr_slow_length=input.int(46, "ATR Slow Length", group=GRP_VOLATILITY, tooltip="Slow ATR period for volatility baseline. When fast ATR exceeds slow ATR, volatility is considered expanding."),
    filter_volume=input.bool(True, "Volume Filter", group=GRP_FILTERS, tooltip="Confirms the selected Volume Oscillator output is above (bull) or below (bear) the Breakout Threshold (set in Volume section).\n⚠ If ALL filters are disabled, signals cannot be generated."),
    filter_tk_kj_cross=input.bool(True, "Tenkan/Kijun Cross", group=GRP_FILTERS, tooltip="Confirms a Tenkan/Kijun crossover in the signal direction."),
    filter_atr_volatility=input.bool(True, "ATR Volatility", group=GRP_FILTERS, tooltip="Confirms market volatility is expanding (fast ATR > slow ATR)."),
    filter_chikou_vs_price=input.bool(True, "Chikou > Price", group=GRP_FILTERS, tooltip="Confirms Chikou Span is above (bull) or below (bear) past price."),
    filter_momentum=input.bool(True, "Chikou Momentum", group=GRP_FILTERS, tooltip="Confirms Chikou momentum aligns with the signal direction."),
    filter_price_vs_kumo=input.bool(True, "Price > Kumo", group=GRP_FILTERS, tooltip="Confirms price is clearly above the Kumo top (bull) or below it (bear).\nNote: Price inside the Kumo is treated as bearish bias — only a full breakout above the cloud confirms bullish."),
    filter_price_vs_tenkan=input.bool(True, "Price > Tenkan", group=GRP_FILTERS, tooltip="Confirms price is above (bull) or below (bear) the Tenkan-Sen."),
    filter_chikou_trend=input.bool(True, "Chikou Trend", group=GRP_FILTERS, tooltip="Confirms the Chikou Span has broken above recent highs (bull) or below recent lows (bear).\nThis measures whether price has achieved a clear directional breakout relative to past price action over the Chikou lookback period."),
    filter_consolidation=input.bool(True, "Flat Market Filter", group=GRP_FILTERS, tooltip="Blocks all signals when the market is in deep consolidation — detected when trend strength is very low and the Kumo is extremely thin.\nRecommended to avoid low-quality signals in ranging markets."),
    sr_enabled=input.bool(True, "Show S/R Zones", group=GRP_SR_ZONES, tooltip="Master toggle for Support/Resistance zone engine.\nZones are created at each signal event (▲▼) — structural trend reversals detected by the Ichimoku system.\nEach zone tracks price interaction: contact, break, retest, and optional flip (S↔R)."),
    sr_zone_layout=input.enum(SrLayout.line_mode, "Zone Style", group=GRP_SR_ZONES, tooltip="Visual style for S/R zones:\n• Line: Horizontal line at the level\n• Zone: Border-only box with a dotted median line at the equilibrium point. Box size depends on Zone Placement setting."),
    sr_zone_placement=input.enum(SrPlacement.wick, "Zone Placement", group=GRP_SR_ZONES, tooltip="Where to anchor the S/R level:\n• Wick: High/Low range — full rejection zone (default)\n• Body: Open/Close range — tighter zones\n• Median: (High+Low)/2 — Hosoda's equilibrium principle\nWick is the classic S/R approach: levels are defined by the full candle range where price was rejected. Body gives tighter zones focused on where the market actually closed. Median uses Hosoda's balance point — breakouts are detected earlier but may trigger prematurely in volatile markets."),
    sr_max_zones=input.int(12, "Max Zones", minval=2, maxval=50, group=GRP_SR_ZONES, tooltip="Maximum number of S/R zones visible on the chart.\nDYNAMIC ATR PRUNING: Zones beyond (Max Zones x 1.5) x ATR are auto-removed every bar. Handles distance — removes zones too far from price.\n• 20 zones → 30x ATR radius\n• 12 zones → 18x ATR radius (default)\n• 8 zones → 12x ATR radius\nAGE-BASED QUOTA: When more zones exist than Max Zones, the oldest ones are removed first. Recent zones always survive. ATR handles distance, quota handles freshness."),
    sr_zone_width=input.int(1, "Line/Border Width", minval=1, maxval=3, group=GRP_SR_ZONES, tooltip="Thickness of S/R zone lines or box borders.\n• 1 = Thin (default, less visual clutter)\n• 2 = Medium\n• 3 = Thick (more prominent zones)"),
    sr_extend=input.bool(True, "Extend Zones (Live)", group=GRP_SR_ZONES, tooltip="When enabled (default), all zones extend to the current bar continuously.\nWhen disabled, zones extend until their first touch by price. Once touched, the zone freezes.\nUntouched zones continue to extend until price reaches them."),
    sr_flip_enabled=input.bool(False, "Flip Zone on Break (S↔R)", group=GRP_SR_ZONES, tooltip="When enabled, broken zones flip their type:\n• Broken Support → becomes Resistance\n• Broken Resistance → becomes Support\nThis reflects the classic trading principle that old support becomes new resistance (and vice-versa).\nFlipped zones behave like new zones: freeze state and touch tracking reset."),
    sr_show_labels=input.bool(True, "Show Zone Labels", group=GRP_SR_ZONES, tooltip="Display informative labels on S/R zones.\nLABEL CONTENT:\n• Zone type (S / R)\n• Price level (anchor point from Zone Placement)\nEXAMPLE: 'S • 45230.50'\nLabels update position when zones freeze on first touch (Extend OFF)."),
    sr_label_size=input.enum(SrLabelSize.small, "└─ Label Size", group=GRP_SR_ZONES, tooltip="Size of price labels on S/R zones. Only applies when 'Show Zone Labels' is enabled."),
    tkr_enabled=input.bool(False, "Show TK-Range Highlight", group=GRP_TK_RANGE, tooltip="Highlight phases where price is trapped BETWEEN Tenkan and Kijun lines.\nDetection is based on CLOSE price — a breakout is confirmed only when close exits the TK/KJ band.\nIf TK/KJ converge while price is still inside (spread collapses), the zone exits as CONVERGED (⇔) — no directional breakout is assigned.\nFEATURES:\n• Median line shows center of consolidation\n• Optional zone extension (like S/R)\n• Smart merge prevents overlapping zones\n• Contextual labels (duration + direction while active, direction + move % after breakout)\n• Hover tooltips with ATR-based range quality"),
    tkr_color=input.color(color.new(color.new('#FFB300'), 85), "Box Color", group=GRP_TK_RANGE, tooltip="Color for TK-Range consolidation boxes.\nDefault amber/orange is chosen to be:\n• Distinct from bullish teal and bearish red\n• Visible against both Kumo colors\n• Neutral, reflecting the directionless nature of consolidation"),
    tkr_min_bars=input.int(3, "Min Bars to Qualify", minval=1, maxval=20, group=GRP_TK_RANGE, tooltip="Minimum consecutive bars with CLOSE inside TK/KJ range before displaying the box.\nHigher values = fewer but more significant consolidation zones.\nRecommended: 3-5 bars"),
    tkr_show_median=input.bool(True, "Show Median Line", group=GRP_TK_RANGE, tooltip="Display a dotted line at the center of each TK-Range box.\nThe median represents the equilibrium point within the consolidation zone and can act as a micro support/resistance level."),
    tkr_extend=input.bool(True, "Extend Zones", group=GRP_TK_RANGE, tooltip="When enabled, TK-Range boxes extend to the current bar (like S/R zones).\nWhen disabled, boxes end exactly when price exits the consolidation.\nNote: Extended zones that overlap will automatically merge."),
    tkr_show_label=input.bool(True, "Show Labels", group=GRP_TK_RANGE, tooltip="Display a centered label inside each TK-Range box.\nFORMAT:\n• Active zone: Duration + Direction (e.g. '7b • →')\n• Completed zone (Extend OFF): Duration + Direction (e.g. '7b • ↑')\n• Completed zone (Extend ON): Duration + Direction + Move % (e.g. '7b • ↑ +3.2%')\n• Converged zone: Duration + ⇔ (e.g. '7b • ⇔') — TK/KJ spread collapsed"),
    tkr_max_history=input.int(5, "Max Historical Zones", minval=1, maxval=100, group=GRP_TK_RANGE, tooltip="Maximum number of past consolidation zones to keep on the chart.\nOldest zones are removed when this limit is reached.\nEXTEND MODE: Zones too far from price are automatically pruned (distance threshold = Max Zones x 3 x ATR)."),
    swing_enabled=input.bool(False, "Swing Detection", group=GRP_SWING, tooltip="Detect swing highs/lows — the foundation for Hosoda's three theories:\n• 波動論 Wave Theory — pattern recognition\n• 値幅観測論 Price Theory — price targets\n• 時間論 Time Theory — cycle analysis\nA bar is confirmed as a swing if it remains the highest (or lowest) within Swing Length bars on both sides.\n⚠ Markers appear with a delay equal to Swing Length."),
    swing_length=input.int(10, "Swing Length", minval=2, maxval=50, group=GRP_SWING, tooltip="Bars on EACH SIDE to confirm a swing point.\n• 3-5: More swings, minor moves\n• 8-15: Balanced (recommended)\n• 20+: Major pivots only\nAlso determines detection delay."),
    swing_show_hl=input.bool(True, "Show Swing Markers", group=GRP_SWING, tooltip="Display ● markers on confirmed swing highs (above bar) and lows (below bar).\nMarkers appear at the actual swing bar, offset back by Swing Length.\nColors follow Bullish/Bearish Event colors."),
    swing_max_stored=input.int(50, "Max Stored Points", minval=20, maxval=100, group=GRP_SWING, tooltip="Maximum swing points kept in memory.\nData source for Wave, Price, and Time theories.\n• 50: Recommended\n• Higher: More depth for higher timeframes"),
    wave_enabled=input.bool(False, "Wave Detection", group=GRP_WAVE, tooltip="波動論 (Hadōron) — Detect Hosoda's wave patterns from swing points.\nBASIC (2-4 points):\n• I — Impulse: single leg A→B\n• V — Return: price returns to origin\n• N — Continuation: impulse-correction-continuation\nCOMPLEX (4-5 points):\n• P — Converging triangle\n• Y — Expanding triangle\n• W — Double formation\nThe N-wave is the most important — it drives Price Theory targets.\n⚠ Requires Swing Detection."),
    wave_show_I=input.bool(True, "Basic:       ", group=GRP_WAVE, inline="wave_basic", tooltip="N-wave = core pattern — a 4-point A→B→C→D structure.\nWhen detected, it triggers Price Theory targets:\n• V = B + (B - C)\n• E = B + (B - A)\n• N = C + (B - A)\n• NT = C + (C - A)"),
    wave_color_I=input.color(color.new(color.new('#E91E63'), 0), "I", group=GRP_WAVE, inline="wave_basic", tooltip=""),
    wave_show_V=input.bool(True, "", group=GRP_WAVE, inline="wave_basic", tooltip=""),
    wave_color_V=input.color(color.new(color.new('#F9A825'), 0), "V", group=GRP_WAVE, inline="wave_basic", tooltip=""),
    wave_show_N=input.bool(True, "", group=GRP_WAVE, inline="wave_basic", tooltip=""),
    wave_color_N=input.color(color.new(color.new('#4A8AD4'), 0), "N ", group=GRP_WAVE, inline="wave_basic", tooltip=""),
    wave_show_P=input.bool(True, "Complex:", group=GRP_WAVE, inline="wave_complex", tooltip="Complex waves require 4-5 swing points.\n• P — Range narrows (C-D tighter than A-B). Compression before breakout.\n• Y — Range widens (C-D wider than A-B). Increasing volatility.\n• W — Repeating structure (A≈C≈E, B≈D). Double bottom/top.\nLess frequent than I/V/N but signal important structural shifts."),
    wave_color_P=input.color(color.new(color.new('#0097A7'), 0), "P", group=GRP_WAVE, inline="wave_complex", tooltip=""),
    wave_show_Y=input.bool(True, "", group=GRP_WAVE, inline="wave_complex", tooltip=""),
    wave_color_Y=input.color(color.new(color.new('#FF5D00'), 0), "Y", group=GRP_WAVE, inline="wave_complex", tooltip=""),
    wave_show_W=input.bool(True, "", group=GRP_WAVE, inline="wave_complex", tooltip=""),
    wave_color_W=input.color(color.new(color.new('#00C853'), 0), "W", group=GRP_WAVE, inline="wave_complex", tooltip=""),
    wave_max_display=input.int(8, "Max Waves Displayed", minval=1, maxval=20, group=GRP_WAVE, tooltip="Maximum number of waves to show on the chart.\nOldest waves are removed when this limit is reached.\nKeep low (5-8) for readability, increase (15-20) for comprehensive analysis."),
    wave_overlap=input.bool(False, "Allow Overlapping", group=GRP_WAVE, tooltip="ON: All detected waves shown, even if they share endpoints. Labels may stack.\nOFF (default): Only highest-priority wave per endpoint.\nPriority: N > W > P > Y > V > I"),
    price_t_enabled=input.bool(False, "Price Targets", group=GRP_PRICE_THEORY, tooltip="値幅観測論 (Nehaba Kansokuron) — Project WHERE price is likely to reach from N-wave geometry.\nTWO MODES:\n• Completed N-wave (A→B→C→D): targets beyond D\n• Developing N-wave (A→B→C): targets where D should complete\nTARGETS:\n• V = B + (B - C)\n• N = C + (B - A)\n• E = B + (B - A)\n• NT = C + (C - A)\n• 2E / 3E = extended multiples\nTarget lines extend into the Senkou projection zone for Price x Kumo confluence reading.\n⚠ Requires Swing + Wave Detection."),
    price_t_show_V=input.bool(True, "Basic:", group=GRP_PRICE_THEORY, inline="pt_basic", tooltip="V = quickest target (from correction).\nN = classic continuation.\nE = strongest projection.\nNT = most conservative.\nAll derived from the same N-wave geometry."),
    price_t_color_V=input.color(color.new(color.new('#FFAB00'), 20), "V", group=GRP_PRICE_THEORY, inline="pt_basic", tooltip=""),
    price_t_show_N=input.bool(True, "", group=GRP_PRICE_THEORY, inline="pt_basic", tooltip=""),
    price_t_color_N=input.color(color.new(color.new('#42A5F5'), 20), "N", group=GRP_PRICE_THEORY, inline="pt_basic", tooltip=""),
    price_t_show_E=input.bool(True, "", group=GRP_PRICE_THEORY, inline="pt_basic", tooltip=""),
    price_t_color_E=input.color(color.new(color.new('#EC407A'), 20), "E", group=GRP_PRICE_THEORY, inline="pt_basic", tooltip=""),
    price_t_show_NT=input.bool(True, "", group=GRP_PRICE_THEORY, inline="pt_basic", tooltip=""),
    price_t_color_NT=input.color(color.new(color.new('#66BB6A'), 20), "NT", group=GRP_PRICE_THEORY, inline="pt_basic", tooltip=""),
    price_t_show_2E=input.bool(False, "Extended:", group=GRP_PRICE_THEORY, inline="pt_ext", tooltip="Extended multiples of the E distance.\n• 2E = B + 2x(B - A)\n• 3E = B + 3x(B - A)\nRare extreme targets — useful in strong trending markets."),
    price_t_color_2E=input.color(color.new(color.new('#FF7043'), 20), "2E", group=GRP_PRICE_THEORY, inline="pt_ext", tooltip=""),
    price_t_show_3E=input.bool(False, "", group=GRP_PRICE_THEORY, inline="pt_ext", tooltip=""),
    price_t_color_3E=input.color(color.new(color.new('#AB47BC'), 20), "3E", group=GRP_PRICE_THEORY, inline="pt_ext", tooltip=""),
    price_t_validate=input.bool(True, "Show Validation", group=GRP_PRICE_THEORY, tooltip="Track whether price has reached each target.\n• Reached ✓ — price hit the level\n• Pending ⋯ — still an active projection\nWhen disabled, all targets show as Completed."),
    price_t_developing=input.bool(True, "Show Developing Targets", group=GRP_PRICE_THEORY, tooltip="Project targets from a DEVELOPING N-wave (3 points: A→B→C) before D completes.\nThe most actionable feature — shows WHERE price is expected to go.\n• Targets show where D should reach\n• Visual: lighter dotted lines\n• Updates dynamically as the wave develops\n⚠ Disappear once the wave completes or the pattern breaks."),
    kihon_enabled=input.bool(False, "Kihon Sūchi (基本数値)", group=GRP_TIME_THEORY, tooltip="時間論 (Jikanron) — Project fixed time cycles from anchor events.\nIdentifies universal rhythm points where trend changes are more likely.\nNUMBERS: 9, 17, 26, 33, 42, 51, 65, 76, 129, 172, 200, 257\n• 9 anchor modes (Signals, Crosses, Swings, Waves...)\n• Multi-anchor: track 1-3 recent events\n• Confluence: gold highlight when cycles converge (±1 bar)\n• Past validation: ✓ where price made a swing\n⚠ Cycles indicate WHEN, not direction."),
    kihon_anchor=input.enum(KihonAnchor.signals, "├─ Anchor Mode", group=GRP_TIME_THEORY, tooltip="Event that anchors Kihon Sūchi projections:\n• Signals (▲▼): Structural trend reversals\n• Tenkan Cross: Price x Tenkan-Sen\n• Kijun Cross: Price x Kijun-Sen\n• TK x KJ Cross: Tenkan x Kijun (Golden/Dead Cross)\n• Kumo Change: Kumo color flip\n• Swing High / Low / Both: Confirmed pivots\n• Wave: End of detected wave pattern\n⚠ Swing/Wave modes require their respective modules."),
    kihon_range=input.enum(CycleRange.basic, "├─ Cycle Range", group=GRP_TIME_THEORY, tooltip="Kihon Sūchi cycles to project:\nBASIC: 9, 17, 26 — most reliable\nEXTENDED: + 33, 42, 51\nFULL: + 65, 76, 129, 172, 200, 257"),
    kihon_history=input.int(1, "├─ Anchor History", minval=1, maxval=3, group=GRP_TIME_THEORY, tooltip="Recent anchor events to track simultaneously.\n• 1: Current event only (cleanest)\n• 2-3: Enables CONFLUENCE detection — gold marker when cycles from different anchors converge (±1 bar)"),
    kihon_color=input.color(color.new(color.new('#787B86'), 0), "└─ Kihon Color", group=GRP_TIME_THEORY, tooltip="Base color for Kihon Sūchi lines and badges.\nOverrides:\n• Active windows (±1 bar) use Bullish/Bearish Event colors\n• Confluence zones use gold highlight"),
    taito_enabled=input.bool(False, "Taito Sūchi (対等数値)", group=GRP_TIME_THEORY, tooltip="対等数値 (Taitō Sūchi) — Project time symmetry from swing durations.\nMeasures the TIME between consecutive swings, then projects that duration forward — markets tend to reproduce symmetric time periods.\nCounterpart of Price Theory:\n• Price Theory → WHERE (price geometry)\n• Taito Sūchi → WHEN (time symmetry)\nExample: Swing A→B took 34 bars → next move from B expected around B + 34.\n⚠ Requires Swing Detection."),
    taito_count=input.int(3, "├─ Swing Pairs", minval=1, maxval=5, group=GRP_TIME_THEORY, tooltip="Recent consecutive swing intervals to project.\n• 1: Most recent pair only\n• 3: Last 3 intervals (default) — emerging rhythm\n• 5: Full context — dominant periodicities"),
    taito_harmonics=input.int(1, "├─ Harmonics", minval=1, maxval=9, group=GRP_TIME_THEORY, tooltip="Harmonic multiples to project per swing pair.\n• 1: Base duration T only (default)\n• 3: T, 2T, 3T — harmonic rhythm\n• 9: Full series — comprehensive analysis\nIf a move took 34 bars, reversal windows exist at 34, 68, 102...\nHigher harmonics fade progressively."),
    taito_color=input.color(color.new(color.new('#AB47BC'), 0), "└─ Taito Color", group=GRP_TIME_THEORY, tooltip="Color for Taito Sūchi projection lines and badges."),
    txp_enabled=input.bool(False, "Time x Price Confluence", group=GRP_TXP, tooltip="時間・値幅合流 (Jikan-Nehaba Gōryū) — WHERE and WHEN converge.\nClusters independent time cycles x price targets into scored zones where multiple Hosoda methods point to the same price at the same time.\nSCORING:\n  score = weighted_time + price_sources + kumo_bonus\n  Cycles weighted by significance (重み Omomi):\n  K26/K42/K76/K129 = 3, K17/K33/K51/K65/K172/K200/K257 = 2, K9 = 1\n  Only score ≥ 4 displayed.\n◆ Diamond = target reached during time window.\n  Fires independently of forecast score.\n⚠ Requires Kihon/Taito + Price Targets enabled.\n  Developing targets (3-point waves) excluded."),
    txp_show_forecast=input.bool(True, "├─ Forecast Zones", group=GRP_TXP, tooltip="Display cluster zones projected into the future.\nBox height = tolerance zone (±ATR). Box width = ±2 bars around cluster center. Opacity and border scale with score. Score displayed centered in box — hover for full details.\nBorder uses chart foreground for theme-agnostic visibility.\nNote: box = clustering tolerance zone. Price may enter the box without reaching the exact target. ◆ only confirms at exact target level."),
    txp_kumo_enhance=input.bool(True, "├─ Kumo Enhancement", group=GRP_TXP, tooltip="Award +1 score when a cluster zone intersects the projected Kumo (current Senkou values).\nTriple confluence (Time x Price x Kumo) is the strongest setup in Hosoda's framework. Kumo-enhanced clusters use a distinct color.\nNote: uses current projected Kumo as approximation for near-future bars."),
    txp_tolerance=input.float(0.5, "├─ Price Tolerance (xATR)", minval=0.1, maxval=2.0, step=0.1, group=GRP_TXP, tooltip="Proximity threshold for clustering (xATR14).\nTwo intersections merge into one cluster when their price levels are within this tolerance AND their time bars are within ±2 bars.\n• 0.5: Tight — only close targets merge\n• 1.0: Medium — accommodates volatility\n• 2.0: Loose — captures broader zones\nAlso defines vertical height of forecast boxes."),
    txp_color=input.color(color.new('#78909C'), "   Base", group=GRP_TXP, inline="txp_colors", tooltip="Fill color for standard confluence zones and confirmed ◆ markers. Border always uses chart foreground for theme-agnostic visibility.\nDefault slate blue-grey is chosen to be:\n• Distinct from bullish/bearish signal colors\n• Visible against both dark and light chart themes\n• Neutral-analytical, reflecting structural overlay"),
    txp_kumo_color=input.color(color.new('#546E7A'), "Kumo", group=GRP_TXP, inline="txp_colors", tooltip="Fill color for Kumo-enhanced triple confluence (Time x Price x Kumo). Used when score ≥ 5 or zone intersects projected Kumo.\nDeeper slate variant creates visual hierarchy with base zones while maintaining neutral-analytical tone."),
    barcolor_mode=input.enum(BarColorMode.vs_tkkj, "Bar Color Mode", group=GRP_BAR_COLOR, tooltip="Choose how bar colors are determined:\nBASIC MODES\n• Price vs TK/KJ: Bull when price > both Tenkan & Kijun\n• Price vs Kumo: Bull when price > Kumo\n• Current Regime: Follows signal direction (▲▼)\nADVANCED MODES\n• Confluence Strength: Gradient intensity based on aligned Ichimoku conditions\n• Kumo Future Bias: Based on projected Kumo direction (predictive)\n• Disabled: Turns off bar coloring"),
    bar_bull_color=input.color(color.new(color.new('#2E7D32'), 0), "Bull", group=GRP_BAR_COLOR, inline="barcolor"),
    bar_bear_color=input.color(color.new(color.new('#C62828'), 0), "Bear", group=GRP_BAR_COLOR, inline="barcolor"),
    bar_neutral_color=input.color(color.new(color.new('#78909C'), 0), "Equilibrium", group=GRP_BAR_COLOR, inline="barcolor"),
    panel_enabled=input.bool(True, "Show Panel", group=GRP_PANEL, tooltip="Master toggle for the Ichimoku analysis panel.\nThe panel displays a real-time summary of all Ichimoku conditions (TK position, Kumo breakout, Chikou signal, etc.) with color-coded strength indicators."),
    panel_lite_mode=input.bool(False, "Lite Mode (Mobile)", group=GRP_PANEL, tooltip="2-column panel optimized for mobile screens.\nDifferences from full panel:\n• 2 columns instead of 3\n• Compact header\n• Shortened terminology in DETAILS"),
    panel_position=input.enum(PanelPosition.bottom_right, "Position", group=GRP_PANEL, tooltip="Screen position of the analysis panel.\nChoose a corner that doesn't overlap with your chart's price action."),
    panel_text_size=input.enum(PanelTextSize.small, "Text Size", group=GRP_PANEL, tooltip="Font size for panel text.\n• Tiny: Compact, ideal for small screens or when panel must be minimal\n• Small: Default, good balance of readability and space\n• Normal/Large: Better readability on larger monitors"),
    panel_header_color=input.color(color.new(color.new('#000000'), 20), "Header Color", group=GRP_PANEL, tooltip="Background color for the panel header row (STATUS / CONSENSUS).\nAdjust transparency to blend with your chart theme."),
    panel_bg_color=input.color(color.new(color.new('#696969'), 80), "Background Color", group=GRP_PANEL, tooltip="Background color for all panel data rows.\nDefault is semi-transparent gray (80% transparency) to remain readable on both dark and light chart themes."),
    panel_show_tk_cross=input.bool(True, "Show TK Cross vs Kumo", group=GRP_PANEL, tooltip="Shows the Tenkan/Kijun cross strength relative to Kumo.\n\nStrong: TK range fully above (bull) or below (bear) Kumo, with TK trend aligned.\nWeak: Position confirmed but trend diverges.\n\nNote: Hiding panel rows is display-only — CONSENSUS always uses all 5 signals."),
    panel_show_kijun=input.bool(True, "Show Kijun Position", group=GRP_PANEL, tooltip="Shows the Kijun-Sen position relative to Kumo combined with price vs Kijun trend.\n\nStrong: Kijun above (bull) or below (bear) Kumo, with price confirming.\nWeak: Position confirmed but price diverges from Kijun."),
    panel_show_chikou_confirm=input.bool(True, "Show Chikou Confirm", group=GRP_PANEL, tooltip="Shows Chikou Span confirmation strength: compares current price with past highs/lows (Chikou above/below past candles) and evaluates price position relative to Kumo.\n\nStrong: Chikou clears past price AND price is on the same side of Kumo.\nWeak: Chikou confirms direction but price is inside or on the wrong side of Kumo."),
    panel_show_price_kumo=input.bool(True, "Show Price vs Kumo", group=GRP_PANEL, tooltip="Shows price position relative to the Kumo (cloud).\n\nStrong Bull: Price above Kumo.\nStrong Bear: Price below Kumo.\nNeutral: Price inside Kumo (no clear trend)."),
    panel_show_kumo_twist=input.bool(True, "Show Kumo Twist", group=GRP_PANEL, tooltip="Shows Kumo direction (Senkou A vs B) combined with price position.\n\nStrong: Kumo direction (A > B = bull, A < B = bear) aligns with price breakout.\nWeak: Kumo direction confirmed but price is on the opposite side or inside."),
    panel_show_details=input.bool(True, "Show Details Section", group=GRP_PANEL, tooltip="Display DETAILS section at bottom of panel.\n• Filters — Are all enabled conditions met?\n• Missing — Which filter conditions are not yet confirmed\n• Regime — Current trend direction and duration\n• Preset — Active Ichimoku period settings"),
    panel_color_strong_bull=input.color(color.new(color.new('#00897B'), 0), "Strong Bull ", group=GRP_PANEL_COLORS, inline="panel_bull"),
    panel_color_weak_bull=input.color(color.new(color.new('#26A69A'), 0), "Weak Bull  ", group=GRP_PANEL_COLORS, inline="panel_bull"),
    panel_color_strong_bear=input.color(color.new(color.new('#E53935'), 0), "Strong Bear", group=GRP_PANEL_COLORS, inline="panel_bear"),
    panel_color_weak_bear=input.color(color.new(color.new('#EF5350'), 0), "Weak Bear", group=GRP_PANEL_COLORS, inline="panel_bear"),
    panel_color_equilibrium=input.color(color.new(color.new('#F57C00'), 0), "Equilibrium ", group=GRP_PANEL_COLORS, inline="panel_consolidation"),
    panel_color_neutral=input.color(color.new(color.new('#9E9E9E'), 0), "Neutral      ", group=GRP_PANEL_COLORS, inline="panel_consolidation")
):
    tk_dyn_pct = __input_33__ / 100.0
    kj_dyn_pct = __input_39__ / 100.0
    ch_dyn_pct = __input_45__ / 100.0
    sk_dyn_pct = __input_52__ / 100.0

    ha_open_calc: Series = NA(float)
    ha_open_calc = (open + close) / 2 if na(ha_open_calc[1]) else (ha_open_calc[1] + ohlc4[1]) / 2

    __block_result__ = na
    __switch__ = alt_source_formula
    if __switch__ == AltSource.formula_1:
        __block_result__ = (open + close + 3 * (high + low)) / 8
    elif __switch__ == AltSource.formula_2:
        __block_result__ = close + high + low - 2 * open
    elif __switch__ == AltSource.formula_3:
        __block_result__ = (close + 5 * (high + low) - 7 * open) / 4
    elif __switch__ == AltSource.formula_4:
        __block_result__ = (open + close + 5 * (high + low)) / 12
    elif __switch__ == AltSource.formula_5:
        __block_result__ = high if close > open else low
    elif __switch__ == AltSource.heiken_ashi:
        __block_result__ = high if ohlc4 > ha_open_calc else low
    else:
        __block_result__ = src_price
    alternativesrc = __block_result__

    price = ta.swma(alternativesrc) if wma_smoothing else alternativesrc

    atr_5 = ta.atr(5)
    atr_14 = ta.atr(14)
    atr_fast = ta.atr(atr_fast_length)
    atr_slow = ta.atr(atr_slow_length)

    def calc_pattern_rate(cond, tw, bw, body):
        denom = tw + bw + body
        return 0.5 if denom == 0 else 0.5 * (tw + bw + (2 * body if cond else 0)) / denom

    def calc_volume_signal(vol_src, _o, _h, _l, _c):
        tw = _h - math.max(_o, _c)
        bw = math.min(_o, _c) - _l
        body = math.abs(_c - _o)
        deltaup = vol_src * calc_pattern_rate(_o <= _c, tw, bw, body)
        deltadown = vol_src * calc_pattern_rate(_o > _c, tw, bw, body)
        delta = deltaup if _c >= _o else -deltadown
        cumdelta = ta.cum(delta)
        __block_result_1__ = na
        __switch__ = vol_ratio_type
        if __switch__ == VolRatioType.obv:
            __block_result_1__ = ta.obv
        elif __switch__ == VolRatioType.cum_delta:
            __block_result_1__ = cumdelta
        else:
            __block_result_1__ = ta.pvt
        cv = __block_result_1__
        ema1 = ta.ema(cv, vol_ema_length_1)
        ema2 = ta.ema(cv, vol_ema_length_2)
        return ema1 - ema2

    def calc_zone_bounds(_src: Series, _type, _len):
        vp = _type if _src > _src[1] else -_type if _src < _src[1] else 0
        denom = ta.ema(_type, _len)
        numer = ta.ema(vp, _len)
        return 0.0 if denom == 0 else 100 * (numer / denom)

    def calc_zone_oscillator(vol_src, _c):
        zLen = vol_zone_length
        return calc_zone_bounds(_c, vol_src, zLen)

    def calc_vol_oscillator(osc_type: VolOscType, vol_src: float, vol_len: int, _o: float, _h: float, _l: float, _c: Series[float]):
        iff_1 = -vol_src if _c < _o else 0
        tfs_val = math.sum(vol_src if _c > _o else iff_1, vol_len) / vol_len
        obv_val = ta.cum(math.sign(ta.change(_c)) * vol_src)
        xtrend = vol_src * 100 if _c > _c[1] else -vol_src * 100
        kvo_val = ta.ema(xtrend, vol_fast_length) - ta.ema(xtrend, vol_slow_length)
        cum_val = calc_volume_signal(vol_src, _o, _h, _l, _c)
        vzo_val = calc_zone_oscillator(vol_src, _c)
        __block_result_2__ = na
        __switch__ = osc_type
        if __switch__ == VolOscType.tfs:
            __block_result_2__ = tfs_val
        elif __switch__ == VolOscType.obv:
            __block_result_2__ = obv_val
        elif __switch__ == VolOscType.klinger:
            __block_result_2__ = kvo_val
        elif __switch__ == VolOscType.cumulative:
            __block_result_2__ = cum_val
        elif __switch__ == VolOscType.vzo:
            __block_result_2__ = vzo_val
        else:
            __block_result_2__ = 0.0
        return __block_result_2__

    tk_vol_signal = calc_vol_oscillator(vol_osc_type_tk, volume, vol_ratio_length, open, high, low, close)
    kj_vol_signal = calc_vol_oscillator(vol_osc_type_kj, volume, vol_ratio_length, open, high, low, close)
    sk_vol_signal = calc_vol_oscillator(vol_osc_type_sk, volume, vol_ratio_length, open, high, low, close)
    ch_vol_signal = calc_vol_oscillator(vol_osc_type_ch, volume, vol_ratio_length, open, high, low, close)
    vol_signal_sum = calc_vol_oscillator(vol_osc_type, volume, vol_ratio_length, open, high, low, close)

    tk_vol_breakout_up = tk_vol_signal > vol_peak_threshold
    kj_vol_breakout_up = kj_vol_signal > vol_peak_threshold
    sk_vol_breakout_up = sk_vol_signal > vol_peak_threshold
    ch_vol_breakout_up = ch_vol_signal > vol_peak_threshold
    vol_breakout_down = vol_signal_sum < vol_peak_threshold
    vol_breakout_up = vol_signal_sum > vol_peak_threshold

    atr_vol_active = atr_fast > atr_slow

    def calc_chikou_color(src: float, len: int, _h: float, _l: float, bull_col: Color, bear_col: Color, r_col: Color):
        isup = src > inline_series(ta.highest(_h, len), len)
        isdown = src < inline_series(ta.lowest(_l, len), len)
        _clr = bear_col if isdown else bull_col if isup else r_col
        regime = 1 if isup else -1 if isdown else 0
        return (_clr, regime)

    chikou_color, chikou_filter_signal = calc_chikou_color(price, ch_filter_period, high, low, chikou_bull_color, chikou_bear_color, chikou_neutral_color)

    def check_filters(chka: list[bool], reference_a: list[bool]):
        result_bool: bool = False

        for i in pine_range(0, array.size(chka) - 1):
            if array.get(chka, i):
                result_bool = array.get(reference_a, i)
                break

        for i in pine_range(0, array.size(chka) - 1):
            if array.get(chka, i):
                result_bool = result_bool and array.get(reference_a, i)
        return result_bool

    is_adaptive_mode = preset == Preset.custom

    effective_tk_min = tk_min_length if is_adaptive_mode or preset_panel_only else 9 if preset == Preset.classic else 8 if preset == Preset.five_d else 10 if preset == Preset.crypto else 20 if preset == Preset.slow else tk_min_length
    effective_tk_max = tk_max_length if is_adaptive_mode or preset_panel_only else 30 if preset == Preset.classic else 22 if preset == Preset.five_d else 30 if preset == Preset.crypto else 60 if preset == Preset.slow else tk_max_length
    effective_kj_min = kj_min_length if is_adaptive_mode or preset_panel_only else 20 if preset == Preset.classic else 22 if preset == Preset.five_d else 30 if preset == Preset.crypto else 60 if preset == Preset.slow else kj_min_length
    effective_kj_max = kj_max_length if is_adaptive_mode or preset_panel_only else 60 if preset == Preset.classic else 44 if preset == Preset.five_d else 60 if preset == Preset.crypto else 120 if preset == Preset.slow else kj_max_length
    effective_sk_min = sk_min_length if is_adaptive_mode or preset_panel_only else 50 if preset == Preset.classic else 44 if preset == Preset.five_d else 60 if preset == Preset.crypto else 120 if preset == Preset.slow else sk_min_length
    effective_sk_max = sk_max_length if is_adaptive_mode or preset_panel_only else 120 if preset == Preset.classic else 88 if preset == Preset.five_d else 120 if preset == Preset.crypto else 240 if preset == Preset.slow else sk_max_length
    effective_ch_min = ch_min_length if is_adaptive_mode or preset_panel_only else 26 if preset == Preset.classic else 22 if preset == Preset.five_d else 30 if preset == Preset.crypto else 60 if preset == Preset.slow else ch_min_length
    effective_ch_max = ch_max_length if is_adaptive_mode or preset_panel_only else 50 if preset == Preset.classic else 44 if preset == Preset.five_d else 60 if preset == Preset.crypto else 120 if preset == Preset.slow else ch_max_length
    effective_offset = sk_offset_length if is_adaptive_mode or preset_panel_only else 26 if preset == Preset.classic else 22 if preset == Preset.five_d else 30 if preset == Preset.crypto else 60 if preset == Preset.slow else sk_offset_length

    warmup_period = math.max(math.max(math.max(effective_tk_max, effective_kj_max), math.max(effective_sk_max, effective_ch_max)), effective_offset)
    is_warmed_up = bar_index >= warmup_period

    def preset_val(classic: int, fiveD: int, crypto: int, slow: int, custom: int):
        return classic if preset == Preset.classic else fiveD if preset == Preset.five_d else crypto if preset == Preset.crypto else slow if preset == Preset.slow else custom

    tkarray: list[bool] = array.from_items(tk_vol_filter, tk_atr_filter, tk_chikou_filter)
    kjarray: list[bool] = array.from_items(kj_vol_filter, kj_atr_filter, kj_chikou_filter)
    skarray: list[bool] = array.from_items(sk_vol_filter, sk_atr_filter, sk_chikou_filter)
    charray: list[bool] = array.from_items(ch_vol_filter, ch_atr_filter, ch_trend_filter)
    tkvolarray: list[bool] = array.from_items(tk_vol_breakout_up, atr_vol_active, chikou_filter_signal == 1)
    kjvolarray: list[bool] = array.from_items(kj_vol_breakout_up, atr_vol_active, chikou_filter_signal == 1)
    skvolarray: list[bool] = array.from_items(sk_vol_breakout_up, atr_vol_active, chikou_filter_signal == 1)
    chvolarray: list[bool] = array.from_items(ch_vol_breakout_up, atr_vol_active, chikou_filter_signal == 1)

    tk_vol_rising = check_filters(tkarray, tkvolarray)
    kj_vol_rising = check_filters(kjarray, kjvolarray)
    sk_vol_rising = check_filters(skarray, skvolarray)
    ch_vol_rising = check_filters(charray, chvolarray)

    dyn_buf: Persistent[list[float]] = array.new_float(4, na)

    def calc_adaptive_length(id: int, para: bool, adapt_Pct: float, minLength: int, maxLength: int):
        ichi_max_length: float = array.get(dyn_buf, id)
        if na(ichi_max_length):
            ichi_max_length = math.avg(minLength, maxLength)

        ichi_max_length = math.max(minLength, ichi_max_length * adapt_Pct) if para else math.min(maxLength, ichi_max_length * (2 - adapt_Pct))
        array.set(dyn_buf, id, ichi_max_length)
        return cast_int(ichi_max_length)

    adaptive_tk_raw = calc_adaptive_length(0, tk_vol_rising, tk_dyn_pct, effective_tk_min, effective_tk_max)
    adaptive_kj_raw = calc_adaptive_length(1, kj_vol_rising, kj_dyn_pct, effective_kj_min, effective_kj_max)
    adaptive_sk_raw = calc_adaptive_length(2, sk_vol_rising, sk_dyn_pct, effective_sk_min, effective_sk_max)
    adaptive_ch_raw = calc_adaptive_length(3, ch_vol_rising, ch_dyn_pct, effective_ch_min, effective_ch_max)

    chart_is_adaptive = is_adaptive_mode or preset_panel_only

    tk_base = preset_val(9, 8, 10, 20, tk_min_length)
    kj_base = preset_val(26, 22, 30, 60, kj_min_length)
    sk_base = preset_val(52, 44, 60, 120, sk_min_length)
    ch_base = preset_val(26, 22, 30, 60, ch_min_length)

    adaptive_tk = adaptive_tk_raw if chart_is_adaptive else tk_base
    adaptive_kj = adaptive_kj_raw if chart_is_adaptive else kj_base
    adaptive_sk = adaptive_sk_raw if chart_is_adaptive else sk_base
    adaptive_ch = adaptive_ch_raw if chart_is_adaptive else ch_base

    effective_chikou_offset = adaptive_ch if chikou_mode == ChikouMode.adaptive else effective_offset

    def parse_text_size(s: PanelTextSize):
        __block_result_3__ = na
        __switch__ = s
        if __switch__ == PanelTextSize.tiny:
            __block_result_3__ = size.tiny
        elif __switch__ == PanelTextSize.small:
            __block_result_3__ = size.small
        elif __switch__ == PanelTextSize.normal:
            __block_result_3__ = size.normal
        elif __switch__ == PanelTextSize.large:
            __block_result_3__ = size.large
        else:
            __block_result_3__ = size.normal
        return __block_result_3__

    def parse_position(p: PanelPosition):
        __block_result_4__ = na
        __switch__ = p
        if __switch__ == PanelPosition.top_right:
            __block_result_4__ = position.top_right
        elif __switch__ == PanelPosition.bottom_right:
            __block_result_4__ = position.bottom_right
        elif __switch__ == PanelPosition.top_left:
            __block_result_4__ = position.top_left
        elif __switch__ == PanelPosition.bottom_left:
            __block_result_4__ = position.bottom_left
        else:
            __block_result_4__ = position.bottom_right
        return __block_result_4__

    def calc_signal_strength(pos, uptrend):
        __block_result_5__ = na
        if uptrend:
            __block_result_6__ = na
            __switch_1__ = pos
            if __switch_1__ == 1:
                __block_result_6__ = 1
            elif __switch_1__ == 0:
                __block_result_6__ = 2
            else:
                __block_result_6__ = 3
            __block_result_5__ = __block_result_6__
        else:
            __block_result_7__ = na
            __switch_1__ = pos
            if __switch_1__ == -1:
                __block_result_7__ = -1
            elif __switch_1__ == 0:
                __block_result_7__ = -2
            else:
                __block_result_7__ = -3
            __block_result_5__ = __block_result_7__
        return __block_result_5__

    def format_lengths_display():
        __block_result_8__ = na
        if is_adaptive_mode:
            display_off = adaptive_ch if chikou_mode == ChikouMode.adaptive else effective_offset
            __block_result_8__ = string.format('Dyn: {0}/{1}/{2}/{3}', adaptive_tk, adaptive_kj, adaptive_sk, display_off)
        else:
            __block_result_9__ = na
            __switch_1__ = preset
            if __switch_1__ == Preset.classic:
                __block_result_9__ = "9/26/52/26"
            elif __switch_1__ == Preset.five_d:
                __block_result_9__ = "8/22/44/22"
            elif __switch_1__ == Preset.crypto:
                __block_result_9__ = "10/30/60/30"
            elif __switch_1__ == Preset.slow:
                __block_result_9__ = "20/60/120/60"
            else:
                __block_result_9__ = "Custom"
            __block_result_8__ = __block_result_9__
        return __block_result_8__

    def get_preset_short():
        __block_result_10__ = na
        __switch__ = preset
        if __switch__ == Preset.classic:
            __block_result_10__ = "CLASSIC"
        elif __switch__ == Preset.five_d:
            __block_result_10__ = "5D"
        elif __switch__ == Preset.crypto:
            __block_result_10__ = "CRYPTO"
        elif __switch__ == Preset.slow:
            __block_result_10__ = "SLOW"
        else:
            __block_result_10__ = "CUSTOM"
        return __block_result_10__

    def get_score_symbol(val):
        __block_result_11__ = na
        __switch__ = val
        if __switch__ == 1:
            __block_result_11__ = "↑ Strong"
        elif __switch__ == 2:
            __block_result_11__ = "◈ Equilibrium"
        elif __switch__ == 3:
            __block_result_11__ = "↗ Weak"
        elif __switch__ == -1:
            __block_result_11__ = "↓ Strong"
        elif __switch__ == -2:
            __block_result_11__ = "◈ Equilibrium"
        elif __switch__ == -3:
            __block_result_11__ = "↘ Weak"
        else:
            __block_result_11__ = "○ Neutral"
        return __block_result_11__

    def get_score_color(val):
        __block_result_12__ = na
        __switch__ = val
        if __switch__ == 1:
            __block_result_12__ = panel_color_strong_bull
        elif __switch__ == 2:
            __block_result_12__ = panel_color_equilibrium
        elif __switch__ == 3:
            __block_result_12__ = panel_color_weak_bull
        elif __switch__ == -1:
            __block_result_12__ = panel_color_strong_bear
        elif __switch__ == -2:
            __block_result_12__ = panel_color_equilibrium
        elif __switch__ == -3:
            __block_result_12__ = panel_color_weak_bear
        else:
            __block_result_12__ = panel_color_neutral
        return __block_result_12__

    price_history_buffer: Persistent[list[float]] = array.new_float()
    array.unshift(price_history_buffer, price)

    price_buffer_max = math.max(effective_ch_max, effective_offset) + 200
    if array.size(price_history_buffer) > price_buffer_max:
        array.pop(price_history_buffer)
    chikou_past_price = array.get(price_history_buffer, effective_chikou_offset) if effective_chikou_offset >= 0 and effective_chikou_offset < array.size(price_history_buffer) else na
    chikou_past_price_prev = array.get(price_history_buffer, effective_chikou_offset - 1) if effective_chikou_offset - 1 >= 0 and effective_chikou_offset - 1 < array.size(price_history_buffer) else na
    chikou_below_past = not na(chikou_past_price) and price < chikou_past_price
    chikou_above_past = not na(chikou_past_price) and price > chikou_past_price

    def calc_donchian(len):
        conversion_length = math.max(1, cast_int(len / line_divider))
        midline = math.avg(ta.lowest(len), ta.highest(len))
        reactive_line = math.avg(ta.lowest(conversion_length), ta.highest(conversion_length))
        return (midline + reactive_line) / 2.0

    tenkansen: Series = calc_donchian(adaptive_tk)
    kijunsen: Series = calc_donchian(adaptive_kj)
    senkoua: Series = math.avg(tenkansen, kijunsen)
    senkoub: Series = math.avg(ta.highest(high, adaptive_sk), ta.lowest(low, adaptive_sk))
    chikou_span = price

    senkou_a_present = senkoua[effective_offset - 1]
    senkou_b_present = senkoub[effective_offset - 1]
    kumo_top = math.max(senkou_a_present, senkou_b_present)
    kumo_bottom = math.min(senkou_a_present, senkou_b_present)

    momentum_value = price - chikou_past_price_prev if not na(chikou_past_price_prev) else na
    bear_momentum = not na(momentum_value) and momentum_value < 0
    bull_momentum = not na(momentum_value) and momentum_value > 0

    price_below_kumo = price < kumo_top
    price_above_kumo = price > kumo_top

    indexarray: list[bool] = array.from_items(filter_volume, filter_atr_volatility, filter_tk_kj_cross, filter_momentum, filter_chikou_vs_price, filter_price_vs_kumo, filter_price_vs_tenkan, filter_chikou_trend)

    downvolumearray: list[bool] = array.from_items(vol_breakout_down, atr_vol_active, tenkansen < kijunsen, bear_momentum, chikou_below_past, price_below_kumo, price < tenkansen, chikou_filter_signal == -1)

    uppervolumearray: list[bool] = array.from_items(vol_breakout_up, atr_vol_active, tenkansen > kijunsen, bull_momentum, chikou_above_past, price_above_kumo, price > tenkansen, chikou_filter_signal == 1)

    condition_names_bull: Persistent[list[str]] = array.from_items('Vol', 'ATR', 'TKxKJ', 'Mom', 'CS>P', 'P>K', 'P>TK', 'CS tr')
    condition_names_bear: Persistent[list[str]] = array.from_items('Vol', 'ATR', 'TKxKJ', 'Mom', 'CS<P', 'P<K', 'P<TK', 'CS tr')

    def calc_trend_strength(len):
        tr = ta.tr
        plus_dm = math.max(high - high[1], 0) if high - high[1] > low[1] - low else 0
        minus_dm = math.max(low[1] - low, 0) if low[1] - low > high - high[1] else 0

        tr_smooth = ta.ema(tr, len)
        plus_smooth = ta.ema(plus_dm, len)
        minus_smooth = ta.ema(minus_dm, len)

        plus_di = 100 * plus_smooth / tr_smooth if tr_smooth > 0 else 0
        minus_di = 100 * minus_smooth / tr_smooth if tr_smooth > 0 else 0

        sum_di = plus_di + minus_di
        dx = 100 * math.abs(plus_di - minus_di) / sum_di if sum_di > 0 else 0
        return ta.ema(dx, len)

    trend_strength = calc_trend_strength(14)

    market_consolidating = trend_strength < 20

    base_for_thickness = math.max(math.abs(kumo_top), math.abs(kumo_bottom), syminfo.mintick)
    kumo_thickness = math.abs(kumo_top - kumo_bottom) / base_for_thickness * 100

    kumo_is_flat = kumo_thickness < 0.3

    def get_panel_lengths():
        __block_result_13__ = (na, na, na, na)
        __switch__ = preset
        if __switch__ == Preset.custom:
            __block_result_13__ = (adaptive_tk, adaptive_kj, adaptive_sk, effective_chikou_offset)
        elif __switch__ == Preset.classic:
            __block_result_13__ = (9, 26, 52, 26)
        elif __switch__ == Preset.five_d:
            __block_result_13__ = (8, 22, 44, 22)
        elif __switch__ == Preset.crypto:
            __block_result_13__ = (10, 30, 60, 30)
        elif __switch__ == Preset.slow:
            __block_result_13__ = (20, 60, 120, 60)
        else:
            __block_result_13__ = (adaptive_tk, adaptive_kj, adaptive_sk, effective_offset)
        return __block_result_13__

    def calc_panel_scores():
        score_1: int = 0
        score_2: int = 0
        score_3: int = 0
        score_4: int = 0
        score_5: int = 0
        consensus: int = 0

        use_tk, use_kj, use_sk, use_off = get_panel_lengths()

        use_tk = math.max(1, math.min(use_tk, 4999))
        use_kj = math.max(1, math.min(use_kj, 4999))
        use_sk = math.max(1, math.min(use_sk, 4999))
        use_off = math.max(1, math.min(use_off, 4999)) - 1

        panel_tenkan = calc_donchian(use_tk)
        panel_kijun = calc_donchian(use_kj)
        panel_spana: Series = math.avg(panel_tenkan, panel_kijun)
        panel_spanb: Series = math.avg(ta.highest(high, use_sk), ta.lowest(low, use_sk))

        kumo_top_current = math.max(panel_spana[use_off], panel_spanb[use_off])
        kumo_bot_current = math.min(panel_spana[use_off], panel_spanb[use_off])

        tk_cloud_top = math.max(panel_tenkan, panel_kijun)
        tk_cloud_bot = math.min(panel_tenkan, panel_kijun)
        tk_position = 1 if tk_cloud_bot > kumo_top_current else -1 if tk_cloud_top < kumo_bot_current else 0
        tk_trend = panel_tenkan > panel_kijun
        score_1 = calc_signal_strength(tk_position, tk_trend)

        kj_position = 1 if panel_kijun > kumo_top_current else -1 if panel_kijun < kumo_bot_current else 0
        kj_trend = close > panel_kijun
        score_2 = calc_signal_strength(kj_position, kj_trend)

        chikou_vs_high = close > high[use_off]
        chikou_vs_low = close < low[use_off]
        ch_trend = 1 if chikou_vs_high else -1 if chikou_vs_low else 0
        ch_position = 1 if close > kumo_top_current else -1 if close < kumo_bot_current else 0
        score_3 = calc_signal_strength(ch_position, True) if ch_trend == 1 else calc_signal_strength(ch_position, False) if ch_trend == -1 else 0

        score_4 = 1 if close > kumo_top_current else -1 if close < kumo_bot_current else 0

        kumo_trend = panel_spana > panel_spanb
        kumo_position = score_4
        score_5 = calc_signal_strength(kumo_position, kumo_trend)

        temp_arr: Persistent[list[int]] = array.new_int(0)
        array.clear(temp_arr)
        array.push(temp_arr, score_1)
        array.push(temp_arr, score_2)
        array.push(temp_arr, score_3)
        array.push(temp_arr, score_4)
        array.push(temp_arr, score_5)

        if array.size(temp_arr) > 0:
            arr_max = array.max(temp_arr)
            arr_min = array.min(temp_arr)
            consensus = arr_max if arr_min > 0 else arr_min if arr_max < 0 else 0

        return (score_1, score_2, score_3, score_4, score_5, consensus)

    panel_tk_cross_score, panel_kijun_score, panel_chikou_score, panel_price_kumo_score, panel_kumo_twist_score, panel_consensus_score = calc_panel_scores()

    panel_consensus_direction: Series = 1 if panel_consensus_score > 0 else -1 if panel_consensus_score < 0 else 0
    panel_consensus_changed = panel_consensus_direction != panel_consensus_direction[1] and (panel_consensus_direction != 0 or panel_consensus_direction[1] != 0)

    def get_composite_status(is_bull_direction):
        missing_conditions: Persistent[list[str]] = array.new_string()
        array.clear(missing_conditions)

        condition_array = uppervolumearray if is_bull_direction else downvolumearray
        names_array = condition_names_bull if is_bull_direction else condition_names_bear

        for i in pine_range(0, array.size(indexarray) - 1):
            is_enabled = array.get(indexarray, i)
            is_met = method_call('get', condition_array, i)

            if is_enabled and (not is_met):
                array.push(missing_conditions, method_call('get', names_array, i))

        sz = array.size(missing_conditions)
        status_text = 'All conditions MET ✓' if sz == 0 else string.format('Waiting for {0} condition{1}', sz, 's' if sz > 1 else '')

        missing_text: str = ""
        if sz > 0:
            max_show = math.min(sz, 5)
            for i in pine_range(0, max_show - 1):
                missing_text += (', ' if i > 0 else '') + array.get(missing_conditions, i)
            if sz > 5:
                missing_text += "…"

        return (status_text, missing_text)

    def get_composite_direction():
        bull_met: int = 0
        bear_met: int = 0

        if filter_volume:
            if vol_breakout_up:
                bull_met += 1
            if vol_breakout_down:
                bear_met += 1

        if filter_tk_kj_cross:
            if tenkansen > kijunsen:
                bull_met += 1
            if tenkansen < kijunsen:
                bear_met += 1

        if filter_momentum:
            if bull_momentum:
                bull_met += 1
            if bear_momentum:
                bear_met += 1

        if filter_chikou_vs_price:
            if chikou_above_past:
                bull_met += 1
            if chikou_below_past:
                bear_met += 1

        if filter_price_vs_kumo:
            if price_above_kumo:
                bull_met += 1
            if price_below_kumo:
                bear_met += 1

        if filter_price_vs_tenkan:
            if price > tenkansen:
                bull_met += 1
            if price < tenkansen:
                bear_met += 1

        if filter_chikou_trend:
            if chikou_filter_signal == 1:
                bull_met += 1
            if chikou_filter_signal == -1:
                bear_met += 1

        return bull_met >= bear_met

    not_in_consolidation = not (kumo_is_flat and market_consolidating) if filter_consolidation else True

    composite_bear_filter = check_filters(indexarray, downvolumearray)
    composite_bull_filter = check_filters(indexarray, uppervolumearray)

    bear_condition: Series = (tenkansen == kijunsen and tenkansen[1] > kijunsen[1] or composite_bear_filter) and not_in_consolidation

    bull_condition: Series = (tenkansen == kijunsen and tenkansen[1] < kijunsen[1] or composite_bull_filter) and not_in_consolidation

    signal_short = is_warmed_up and bear_condition and (not bear_condition[1])
    signal_long = is_warmed_up and bull_condition and (not bull_condition[1])

    regime: PersistentSeries[int] = 0

    if signal_short and regime >= 0:
        regime = -1
    if signal_long and regime <= 0:
        regime = 1

    regime_flip_bear = regime == -1 and regime[1] != -1
    regime_flip_bull = regime == 1 and regime[1] != 1

    bars_in_regime: Persistent[int] = 0
    if regime_flip_bull or regime_flip_bear:
        bars_in_regime = 0
    else:
        bars_in_regime += 1

    atr_offset = 0.85 * atr_5

    plotshape(high + atr_offset if show_signals and regime_flip_bear else na, title='Signal: Bearish Reversal ▼', style=shape.triangledown, color=bear_event_color, location=location.absolute, size=size.small)

    plotshape(low - atr_offset if show_signals and regime_flip_bull else na, title='Signal: Bullish Reversal ▲', style=shape.triangleup, color=bull_event_color, location=location.absolute, size=size.small)

    tkr_boxes: Persistent[list[Box]] = array.new_box()
    tkr_medians: Persistent[list[Line]] = array.new_line()
    tkr_labels: Persistent[list[Label]] = array.new_label()
    tkr_tops: Persistent[list[float]] = array.new_float()
    tkr_bots: Persistent[list[float]] = array.new_float()
    tkr_start_bars: Persistent[list[int]] = array.new_int()
    tkr_end_bars: Persistent[list[int]] = array.new_int()
    tkr_durations: Persistent[list[int]] = array.new_int()
    tkr_range_pcts: Persistent[list[float]] = array.new_float()
    tkr_is_active: Persistent[list[bool]] = array.new_bool()
    tkr_breakout_dir: Persistent[list[int]] = array.new_int()
    tkr_exit_price: Persistent[list[float]] = array.new_float()

    tkr_consec_count: PersistentSeries[int] = 0
    tkr_range_start: Persistent[int] = na(int)
    tkr_range_high: Persistent[float] = na(float)
    tkr_range_low: Persistent[float] = na(float)
    tkr_box_created: Persistent[bool] = False
    tkr_active_box: Persistent[Box] = na(Box)
    tkr_active_median: Persistent[Line] = na(Line)
    tkr_active_label: Persistent[Label] = na(Label)

    tkr_have_lines = not na(tenkansen) and (not na(kijunsen))
    tkr_top: Series = math.max(tenkansen, kijunsen) if tkr_have_lines else na
    tkr_bot: Series = math.min(tenkansen, kijunsen) if tkr_have_lines else na
    tkr_spread = math.abs(tenkansen - kijunsen) if tkr_have_lines else na

    tkr_range_pct = tkr_spread / atr_14 * 100 if atr_14 > 0 and (not na(tkr_spread)) else 50

    tkr_min_spread = atr_14 * 0.1

    tkr_tolerance = syminfo.mintick * 0.5
    tkr_inside = tkr_have_lines and tkr_spread >= tkr_min_spread and (close >= tkr_bot - tkr_tolerance) and (close <= tkr_top + tkr_tolerance)

    tkr_max_boxes_dynamic = tkr_max_history

    def tkr_format_label(bars: int, is_active: bool, breakout_dir: int, brk_pct: float):
        bars_txt = string.format('{0}b', bars)
        __block_result_14__ = na
        if is_active:
            __block_result_14__ = bars_txt + ' • →'
        else:
            dir_txt = '↑' if breakout_dir == 1 else '↓' if breakout_dir == -1 else '⇔'
            core_txt = string.format('{0} • {1}', bars_txt, dir_txt)
            __block_result_15__ = na
            if tkr_extend and (not na(brk_pct)) and (breakout_dir != 0):
                move_txt = string.format('{0}{1}%', '+' if brk_pct >= 0 else '', math.round(brk_pct, 2))
                __block_result_15__ = core_txt + ' ' + move_txt
            else:
                __block_result_15__ = core_txt
            __block_result_14__ = __block_result_15__
        return __block_result_14__

    def tkr_range_quality_text(pct: float):
        __block_result_16__ = na
        if pct < 75:
            __block_result_16__ = "Tight squeeze — explosive potential\n"
        elif pct > 100:
            __block_result_16__ = "Wide range — measured move likely\n"
        else:
            __block_result_16__ = ""
        return __block_result_16__

    def tkr_zones_overlap(top1: float, bot1: float, top2: float, bot2: float):
        return top1 >= bot2 and bot1 <= top2

    def tkr_delete_zone(idx: int):
        __block_result_17__ = na
        if idx >= 0 and idx < array.size(tkr_boxes):
            bx = array.get(tkr_boxes, idx)
            if not na(bx):
                method_call('delete', bx)
            if idx < array.size(tkr_medians):
                md = array.get(tkr_medians, idx)
                if not na(md):
                    method_call('delete', md)
            if idx < array.size(tkr_labels):
                lb = array.get(tkr_labels, idx)
                if not na(lb):
                    method_call('delete', lb)
            array.remove(tkr_boxes, idx)
            array.remove(tkr_medians, idx)
            array.remove(tkr_labels, idx)
            array.remove(tkr_tops, idx)
            array.remove(tkr_bots, idx)
            array.remove(tkr_start_bars, idx)
            array.remove(tkr_end_bars, idx)
            array.remove(tkr_durations, idx)
            array.remove(tkr_range_pcts, idx)
            array.remove(tkr_is_active, idx)
            array.remove(tkr_breakout_dir, idx)
            __block_result_17__ = array.remove(tkr_exit_price, idx)
        return __block_result_17__

    def tkr_cleanup():
        __block_result_18__ = na
        while array.size(tkr_boxes) > tkr_max_boxes_dynamic:
            __block_result_18__ = tkr_delete_zone(0)
        return __block_result_18__

    def tkr_update_label(lbl: Label, x_pos: int, y_top: float, y_bot: float, dur: int, range_pct: float, is_active: bool, brk_dir: int, brk_pct: float, exit_px: float):
        __block_result_19__ = na
        if not na(lbl):
            mid_y = (y_top + y_bot) / 2
            txt = tkr_format_label(dur, is_active, brk_dir, brk_pct)
            label.set_xy(lbl, x_pos, mid_y)
            label.set_text(lbl, txt)

            quality_txt = tkr_range_quality_text(range_pct)

            tooltip_txt: str = ""
            median_str = string.tostring(mid_y, format.mintick)
            if is_active:
                tooltip_txt = string.format('TK-Range Consolidation (ACTIVE)\n\nDuration: {0} bars\n{1}\nMedian: {2}\n⟷ Watch for breakout direction', dur, quality_txt, median_str)
            elif brk_dir == 0:
                tooltip_txt = string.format('TK-Range Consolidation (CONVERGED)\n\nDuration: {0} bars\n{1}\nMedian: {2}\nEXIT: TK/KJ spread collapsed — no directional breakout', dur, quality_txt, median_str)
            else:
                brk_dir_txt = '↑ Bullish' if brk_dir == 1 else '↓ Bearish'
                move_str = string.format('{0}{1}%', '+' if brk_pct >= 0 else '', math.round(brk_pct, 2))
                tooltip_txt = string.format('TK-Range Consolidation (COMPLETED)\n\nDuration: {0} bars\n{1}\nMedian: {2}\nBREAKOUT\nDirection: {3}\nPrice: {4}\nMove: {5}', dur, quality_txt, median_str, brk_dir_txt, string.tostring(exit_px, format.mintick), move_str)
            __block_result_19__ = label.set_tooltip(lbl, tooltip_txt)
        return __block_result_19__

    def tkr_try_merge_zones():
        __block_result_20__ = na
        if tkr_extend and array.size(tkr_boxes) > 1:
            merged: bool = True
            iterations: int = 0

            __block_result_21__ = na
            while merged and iterations < 5:
                merged = False
                iterations += 1
                sz = array.size(tkr_boxes)
                __block_result_22__ = na
                if sz > 1:
                    __block_result_23__ = na
                    for i in pine_range(sz - 1, sz - 1):
                        __block_result_24__ = na
                        if i < array.size(tkr_boxes):
                            top_i = array.get(tkr_tops, i)
                            bot_i = array.get(tkr_bots, i)
                            for j in pine_range(i - 1, 0):
                                if j < array.size(tkr_boxes):
                                    top_j = array.get(tkr_tops, j)
                                    bot_j = array.get(tkr_bots, j)
                                    if tkr_zones_overlap(top_i, bot_i, top_j, bot_j):
                                        new_top = math.max(top_i, top_j)
                                        new_bot = math.min(bot_i, bot_j)

                                        dur_i = array.get(tkr_durations, i)
                                        dur_j = array.get(tkr_durations, j)
                                        new_dur = math.max(dur_i, dur_j)

                                        new_pct = (new_top - new_bot) / atr_14 * 100 if atr_14 > 0 else 50

                                        array.set(tkr_tops, i, new_top)
                                        array.set(tkr_bots, i, new_bot)
                                        array.set(tkr_durations, i, new_dur)
                                        array.set(tkr_range_pcts, i, new_pct)

                                        st_bar_i = array.get(tkr_start_bars, i)
                                        st_bar_j = array.get(tkr_start_bars, j)
                                        earliest_start = math.min(st_bar_i, st_bar_j)
                                        array.set(tkr_start_bars, i, earliest_start)

                                        bx_i = array.get(tkr_boxes, i)
                                        if not na(bx_i):
                                            method_call('set_top', bx_i, new_top)
                                            method_call('set_bottom', bx_i, new_bot)
                                            method_call('set_left', bx_i, earliest_start)

                                        if tkr_show_median and i < array.size(tkr_medians):
                                            md_i = array.get(tkr_medians, i)
                                            if not na(md_i):
                                                new_mid = (new_top + new_bot) / 2
                                                method_call('set_y1', md_i, new_mid)
                                                method_call('set_y2', md_i, new_mid)
                                                method_call('set_x1', md_i, earliest_start)

                                        if tkr_show_label and i < array.size(tkr_labels):
                                            lbl_i = array.get(tkr_labels, i)
                                            mid_bar = cast_int((earliest_start + bar_index) / 2)
                                            is_act_i = array.get(tkr_is_active, i)
                                            brk_dir_i = array.get(tkr_breakout_dir, i)
                                            exit_px_i = array.get(tkr_exit_price, i)

                                            brk_pct_i: float = 0.0
                                            if not is_act_i and (not na(exit_px_i)) and (exit_px_i > 0):
                                                if brk_dir_i == 1 and new_top > 0:
                                                    brk_pct_i = (close - new_top) / new_top * 100
                                                elif brk_dir_i == -1 and new_bot > 0:
                                                    brk_pct_i = (new_bot - close) / new_bot * 100

                                            tkr_update_label(lbl_i, mid_bar, new_top, new_bot, new_dur, new_pct, is_act_i, brk_dir_i, brk_pct_i, exit_px_i)

                                        tkr_delete_zone(j)
                                        merged = True
                                        break
                            __block_result_25__ = na
                            if merged:
                                break
                            __block_result_24__ = __block_result_25__
                        __block_result_23__ = __block_result_24__
                    __block_result_22__ = __block_result_23__
                __block_result_21__ = __block_result_22__
            __block_result_20__ = __block_result_21__
        return __block_result_20__

    if tkr_enabled:
        if tkr_inside:
            tkr_consec_count += 1

            if tkr_consec_count == 1:
                tkr_range_start = bar_index
                tkr_range_high = tkr_top
                tkr_range_low = tkr_bot
                tkr_box_created = False
            else:
                tkr_range_high = math.max(tkr_range_high, tkr_top)
                tkr_range_low = math.min(tkr_range_low, tkr_bot)

            if tkr_consec_count >= tkr_min_bars:
                if not tkr_box_created:
                    border_col = color.new(tkr_color, 45)

                    tkr_active_box = box.new(left=tkr_range_start, top=tkr_range_high, right=bar_index, bottom=tkr_range_low, xloc=xloc.bar_index, bgcolor=tkr_color, border_color=border_col, border_width=1, border_style=line.style_dotted)

                    if tkr_show_median:
                        median_y = (tkr_range_high + tkr_range_low) / 2
                        median_col = color.new(tkr_color, 35)
                        tkr_active_median = line.new(x1=tkr_range_start, y1=median_y, x2=bar_index, y2=median_y, xloc=xloc.bar_index, color=median_col, width=1, style=line.style_dotted)

                    if tkr_show_label:
                        label_y = (tkr_range_high + tkr_range_low) / 2
                        label_txt = tkr_format_label(tkr_consec_count, True, 0, 0.0)
                        label_x = cast_int((tkr_range_start + bar_index) / 2)
                        quality_txt = tkr_range_quality_text(tkr_range_pct)
                        tkr_active_label = label.new(x=label_x, y=label_y, text=label_txt, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_center, size=size.small, color=color.new(tkr_color, 90), textcolor=chart.fg_color, tooltip=string.format('TK-Range Consolidation (ACTIVE)\n\nDuration: {0} bars\n{1}\nMedian: {2}\n⟷ Watch for breakout direction', tkr_consec_count, quality_txt, string.tostring(label_y, format.mintick)))

                    tkr_box_created = True

                    array.push(tkr_boxes, tkr_active_box)
                    array.push(tkr_medians, tkr_active_median)
                    array.push(tkr_labels, tkr_active_label)
                    array.push(tkr_tops, tkr_range_high)
                    array.push(tkr_bots, tkr_range_low)
                    array.push(tkr_start_bars, tkr_range_start)
                    array.push(tkr_end_bars, bar_index)
                    array.push(tkr_durations, tkr_consec_count)
                    array.push(tkr_range_pcts, tkr_range_pct)
                    array.push(tkr_is_active, True)
                    array.push(tkr_breakout_dir, 0)
                    array.push(tkr_exit_price, na)

                    tkr_cleanup()
                else:
                    if not na(tkr_active_box):
                        box.set_right(tkr_active_box, bar_index)
                        box.set_top(tkr_active_box, tkr_range_high)
                        box.set_bottom(tkr_active_box, tkr_range_low)

                    if tkr_show_median and (not na(tkr_active_median)):
                        median_y = (tkr_range_high + tkr_range_low) / 2
                        line.set_x2(tkr_active_median, bar_index)
                        line.set_y1(tkr_active_median, median_y)
                        line.set_y2(tkr_active_median, median_y)

                    if tkr_show_label and (not na(tkr_active_label)):
                        label_x = cast_int((tkr_range_start + bar_index) / 2)
                        label_y = (tkr_range_high + tkr_range_low) / 2
                        label_txt = tkr_format_label(tkr_consec_count, True, 0, 0.0)
                        quality_txt = tkr_range_quality_text(tkr_range_pct)
                        label.set_xy(tkr_active_label, label_x, label_y)
                        label.set_text(tkr_active_label, label_txt)
                        label.set_tooltip(tkr_active_label, string.format('TK-Range Consolidation (ACTIVE)\n\nDuration: {0} bars\n{1}\nMedian: {2}\n⟷ Watch for breakout direction', tkr_consec_count, quality_txt, string.tostring(label_y, format.mintick)))

                    sz = array.size(tkr_durations)
                    if sz > 0:
                        array.set(tkr_durations, sz - 1, tkr_consec_count)
                        array.set(tkr_tops, sz - 1, tkr_range_high)
                        array.set(tkr_bots, sz - 1, tkr_range_low)
                        array.set(tkr_end_bars, sz - 1, bar_index)
                        array.set(tkr_range_pcts, sz - 1, tkr_range_pct)
        else:
            if tkr_box_created:
                sz = array.size(tkr_is_active)
                if sz > 0:
                    array.set(tkr_is_active, sz - 1, False)
                    array.set(tkr_end_bars, sz - 1, bar_index)

                    zone_top = array.get(tkr_tops, sz - 1)
                    zone_bot = array.get(tkr_bots, sz - 1)
                    breakout_dir = 1 if close >= zone_top else -1 if close <= zone_bot else 0
                    array.set(tkr_breakout_dir, sz - 1, breakout_dir)
                    array.set(tkr_exit_price, sz - 1, close if breakout_dir != 0 else na)

                    if tkr_show_label:
                        lbl = array.get(tkr_labels, sz - 1)
                        if not na(lbl):
                            dur = array.get(tkr_durations, sz - 1)
                            range_pct_stored = array.get(tkr_range_pcts, sz - 1)

                            brk_pct: float = 0.0
                            if breakout_dir == 1 and zone_top > 0:
                                brk_pct = (close - zone_top) / zone_top * 100
                            elif breakout_dir == -1 and zone_bot > 0:
                                brk_pct = (zone_bot - close) / zone_bot * 100

                            start_bar = array.get(tkr_start_bars, sz - 1)
                            label_x = cast_int((start_bar + bar_index) / 2)

                            tkr_update_label(lbl, label_x, zone_top, zone_bot, dur, range_pct_stored, False, breakout_dir, brk_pct, close)

            tkr_consec_count = 0
            tkr_range_start = na
            tkr_range_high = na
            tkr_range_low = na
            tkr_box_created = False
            tkr_active_box = na
            tkr_active_median = na
            tkr_active_label = na

        if tkr_extend:
            if atr_14 > 0 and array.size(tkr_boxes) > 0:
                tkr_prune_radius = tkr_max_boxes_dynamic * 3.0 * atr_14
                for i in pine_range(array.size(tkr_boxes) - 1, 0):
                    if i < array.size(tkr_is_active) and (not array.get(tkr_is_active, i)):
                        zone_mid = (array.get(tkr_tops, i) + array.get(tkr_bots, i)) / 2
                        if math.abs(close - zone_mid) > tkr_prune_radius:
                            tkr_delete_zone(i)
            sz = array.size(tkr_boxes)
            if sz > 0:
                for i in pine_range(0, sz - 1):
                    is_active = array.get(tkr_is_active, i)
                    if not is_active:
                        bx = array.get(tkr_boxes, i)
                        if not na(bx):
                            method_call('set_right', bx, bar_index)

                        if tkr_show_median and i < array.size(tkr_medians):
                            md = array.get(tkr_medians, i)
                            if not na(md):
                                method_call('set_x2', md, bar_index)

                        if tkr_show_label and i < array.size(tkr_labels):
                            lbl = array.get(tkr_labels, i)
                            if not na(lbl):
                                start_bar = array.get(tkr_start_bars, i)
                                top_lvl = array.get(tkr_tops, i)
                                bot_lvl = array.get(tkr_bots, i)
                                dur = array.get(tkr_durations, i)
                                range_pct_stored = array.get(tkr_range_pcts, i)
                                brk_dir = array.get(tkr_breakout_dir, i)
                                exit_px = array.get(tkr_exit_price, i)

                                brk_pct: float = 0.0
                                if not na(exit_px) and exit_px > 0:
                                    if brk_dir == 1 and top_lvl > 0:
                                        brk_pct = (close - top_lvl) / top_lvl * 100
                                    elif brk_dir == -1 and bot_lvl > 0:
                                        brk_pct = (bot_lvl - close) / bot_lvl * 100

                                label_x = cast_int((start_bar + bar_index) / 2)
                                tkr_update_label(lbl, label_x, top_lvl, bot_lvl, dur, range_pct_stored, False, brk_dir, brk_pct, exit_px)

            tkr_try_merge_zones()

    tkr_was_inside = tkr_consec_count[1] >= tkr_min_bars
    tkr_exited_up = tkr_was_inside and (not tkr_inside) and (close > tkr_top[1])
    tkr_exited_down = tkr_was_inside and (not tkr_inside) and (close < tkr_bot[1])

    tkr_last_median_cross_level: Persistent[float] = na(float)
    tkr_median_crossed_up: bool = False
    tkr_median_crossed_down: bool = False

    if tkr_enabled and tkr_extend and tkr_show_median:
        sz = array.size(tkr_boxes)
        if sz > 0:
            for i in pine_range(0, sz - 1):
                is_active = array.get(tkr_is_active, i)
                if not is_active:
                    top_lvl = array.get(tkr_tops, i)
                    bot_lvl = array.get(tkr_bots, i)
                    mid_lvl = (top_lvl + bot_lvl) / 2

                    if close >= bot_lvl and close <= top_lvl:
                        if close > mid_lvl and close[1] <= mid_lvl:
                            tkr_median_crossed_up = True
                            tkr_last_median_cross_level = mid_lvl
                        if close < mid_lvl and close[1] >= mid_lvl:
                            tkr_median_crossed_down = True
                            tkr_last_median_cross_level = mid_lvl

    sr_lines: Persistent[list[Line]] = array.new_line()
    sr_boxes: Persistent[list[Box]] = array.new_box()
    sr_medians: Persistent[list[Line]] = array.new_line()
    sr_labels: Persistent[list[Label]] = array.new_label()
    sr_is_res: Persistent[list[bool]] = array.new_bool()
    sr_frozen: Persistent[list[bool]] = array.new_bool()
    sr_levels: Persistent[list[float]] = array.new_float()
    sr_zone_tops: Persistent[list[float]] = array.new_float()
    sr_zone_bots: Persistent[list[float]] = array.new_float()
    sr_left_x: Persistent[list[int]] = array.new_int()
    sr_in_contact: Persistent[list[bool]] = array.new_bool()
    sr_first_touched: Persistent[list[bool]] = array.new_bool()
    sr_broken: Persistent[list[bool]] = array.new_bool()
    sr_median_broken: Persistent[list[bool]] = array.new_bool()

    def calc_sr_bounds(is_resistance):
        __block_result_26__ = (na, na, na)
        __switch__ = sr_zone_placement
        if __switch__ == SrPlacement.wick:
            level = high if is_resistance else low
            __block_result_26__ = (level, high, low)
        elif __switch__ == SrPlacement.body:
            level = math.max(open, close) if is_resistance else math.min(open, close)
            __block_result_26__ = (level, math.max(open, close), math.min(open, close))
        else:
            level = (high + low) / 2
            __block_result_26__ = (level, high, low)
        return __block_result_26__

    def delete_sr_zone(idx):
        method_call('delete', array.get(sr_lines, idx))
        method_call('delete', array.get(sr_boxes, idx))
        method_call('delete', array.get(sr_medians, idx))
        method_call('delete', array.get(sr_labels, idx))
        array.remove(sr_lines, idx)
        array.remove(sr_boxes, idx)
        array.remove(sr_medians, idx)
        array.remove(sr_labels, idx)
        array.remove(sr_is_res, idx)
        array.remove(sr_frozen, idx)
        array.remove(sr_levels, idx)
        array.remove(sr_zone_tops, idx)
        array.remove(sr_zone_bots, idx)
        array.remove(sr_left_x, idx)
        array.remove(sr_in_contact, idx)
        array.remove(sr_first_touched, idx)
        array.remove(sr_broken, idx)
        return array.remove(sr_median_broken, idx)

    def get_sr_label_text(is_res, level):
        zone_type: str = 'R' if is_res else 'S'
        return string.format('{0} • {1}', zone_type, math.round_to_mintick(level))

    def update_sr_label(idx, level, zone_color):
        lb = array.get(sr_labels, idx)
        __block_result_27__ = na
        if not na(lb):
            is_resistance = array.get(sr_is_res, idx)
            label_text = get_sr_label_text(is_resistance, level)
            method_call('set_text', lb, label_text)
            method_call('set_textcolor', lb, zone_color)
            __block_result_27__ = method_call('set_y', lb, level)
        return __block_result_27__

    def create_sr_zone(is_resistance):
        level, zone_top, zone_bot = calc_sr_bounds(is_resistance)
        zone_color = bear_event_color if is_resistance else bull_event_color

        new_line: Line = na(Line)
        if sr_zone_layout == SrLayout.line_mode:
            new_line = line.new(bar_index, level, bar_index, level, xloc=xloc.bar_index, color=zone_color, width=sr_zone_width, style=line.style_solid)

        new_box: Box = na(Box)
        if sr_zone_layout == SrLayout.zone_mode:
            new_box = box.new(bar_index, zone_top, bar_index, zone_bot, xloc=xloc.bar_index, border_color=zone_color, border_width=sr_zone_width, bgcolor=color.new(zone_color, 100))

        new_median: Line = na(Line)
        if sr_zone_layout == SrLayout.zone_mode:
            median_y = (zone_top + zone_bot) / 2
            new_median = line.new(bar_index, median_y, bar_index, median_y, xloc=xloc.bar_index, color=zone_color, width=sr_zone_width, style=line.style_dotted)

        new_label: Label = na(Label)
        if sr_show_labels:
            label_text = get_sr_label_text(is_resistance, level)
            __block_result_28__ = na
            __switch_1__ = sr_label_size
            if __switch_1__ == SrLabelSize.tiny:
                __block_result_28__ = size.tiny
            elif __switch_1__ == SrLabelSize.small:
                __block_result_28__ = size.small
            else:
                __block_result_28__ = size.normal
            label_sz = __block_result_28__
            label_y = level
            new_label = label.new(bar_index, label_y, label_text, xloc=xloc.bar_index, style=label.style_label_left, color=color.new(zone_color, 100), textcolor=zone_color, size=label_sz)

        array.push(sr_lines, new_line)
        array.push(sr_boxes, new_box)
        array.push(sr_medians, new_median)
        array.push(sr_labels, new_label)
        array.push(sr_is_res, is_resistance)
        array.push(sr_frozen, False)
        array.push(sr_levels, level)
        array.push(sr_zone_tops, zone_top)
        array.push(sr_zone_bots, zone_bot)
        array.push(sr_left_x, bar_index)
        array.push(sr_in_contact, False)
        array.push(sr_first_touched, False)
        array.push(sr_broken, False)
        return array.push(sr_median_broken, False)

    sr_frozen_label_offset = atr_slow * 0.5

    def update_sr_zones():
        res_broken_up: bool = False
        sup_broken_down: bool = False
        med_crossed_up: bool = False
        med_crossed_down: bool = False
        zone_flipped: bool = False
        zone_retested: bool = False

        sz = array.size(sr_lines) if sr_enabled else 0
        if sz > 0:
            for i in pine_range(sz - 1, 0):
                is_res = array.get(sr_is_res, i)
                was_frozen = array.get(sr_frozen, i)
                level = array.get(sr_levels, i)
                zone_top = array.get(sr_zone_tops, i)
                zone_bot = array.get(sr_zone_bots, i)
                left_x = array.get(sr_left_x, i)
                was_contact = array.get(sr_in_contact, i)
                was_touched = array.get(sr_first_touched, i)
                was_broken = array.get(sr_broken, i)
                was_med_broken = array.get(sr_median_broken, i)

                zone_color = bear_event_color if is_res else bull_event_color
                is_fresh = bar_index == left_x

                just_broke: bool = False
                just_flipped: bool = False
                is_catchup: bool = False

                if not is_fresh and (not was_broken):
                    broke_up: bool = False

                    if sr_zone_layout == SrLayout.line_mode:
                        if is_res and close > level and (close[1] <= level):
                            just_broke = True
                            broke_up = True
                        elif not is_res and close < level and (close[1] >= level):
                            just_broke = True
                            broke_up = False
                    elif sr_zone_placement == SrPlacement.median:
                        if is_res and close > level and (close[1] <= level):
                            just_broke = True
                            broke_up = True
                        elif not is_res and close < level and (close[1] >= level):
                            just_broke = True
                            broke_up = False
                    else:
                        if is_res and close > zone_top and (close[1] <= zone_top):
                            just_broke = True
                            broke_up = True
                        elif not is_res and close < zone_bot and (close[1] >= zone_bot):
                            just_broke = True
                            broke_up = False

                    if not just_broke:
                        price_already_beyond: bool = False
                        if sr_zone_layout == SrLayout.line_mode:
                            price_already_beyond = close > level if is_res else close < level
                        elif sr_zone_placement == SrPlacement.median:
                            price_already_beyond = close > level if is_res else close < level
                        else:
                            price_already_beyond = close > zone_top if is_res else close < zone_bot

                        if price_already_beyond:
                            just_broke = True
                            broke_up = is_res
                            is_catchup = True

                    if just_broke:
                        if not is_catchup:
                            if broke_up:
                                res_broken_up = True
                            else:
                                sup_broken_down = True

                            if sr_zone_layout == SrLayout.zone_mode and sr_zone_placement == SrPlacement.median:
                                if broke_up:
                                    med_crossed_up = True
                                else:
                                    med_crossed_down = True
                                array.set(sr_median_broken, i, True)

                        if sr_flip_enabled:
                            array.set(sr_is_res, i, not is_res)
                            is_res = not is_res

                            if sr_zone_placement != SrPlacement.median:
                                new_level = zone_top if is_res else zone_bot
                                array.set(sr_levels, i, new_level)
                                level = new_level

                                if sr_zone_layout == SrLayout.line_mode:
                                    ln__000003c6__ = array.get(sr_lines, i)
                                    if not na(ln__000003c6__):
                                        method_call('set_y1', ln__000003c6__, level)
                                        method_call('set_y2', ln__000003c6__, level)

                            zone_color = bear_event_color if is_res else bull_event_color
                            just_flipped = True
                            zone_flipped = True

                            array.set(sr_frozen, i, False)
                            array.set(sr_first_touched, i, False)
                            array.set(sr_median_broken, i, False)
                            array.set(sr_in_contact, i, True)

                            update_sr_label(i, level, zone_color)
                        else:
                            array.set(sr_broken, i, True)

                retest_confirmed: bool = False

                if not just_broke and (not is_fresh) and (not was_broken):
                    if sr_zone_layout == SrLayout.line_mode:
                        if is_res:
                            retest_confirmed = high >= level and close < level
                        else:
                            retest_confirmed = low <= level and close > level
                    else:
                        if sr_zone_placement == SrPlacement.median:
                            if is_res:
                                retest_confirmed = high >= level and close < level
                            else:
                                retest_confirmed = low <= level and close > level
                        else:
                            if is_res:
                                retest_confirmed = high >= zone_bot and close < zone_bot
                            else:
                                retest_confirmed = low <= zone_top and close > zone_top

                just_touched: bool = False
                if not is_fresh and (not was_broken) and (not was_touched):
                    if sr_zone_layout == SrLayout.line_mode or sr_zone_placement == SrPlacement.median:
                        just_touched = high >= level if is_res else low <= level
                    else:
                        just_touched = high >= zone_bot if is_res else low <= zone_top

                if just_touched:
                    array.set(sr_first_touched, i, True)
                    was_touched = True

                if not sr_extend and just_touched:
                    array.set(sr_frozen, i, True)

                if was_touched and retest_confirmed and (not was_contact) and (not array.get(sr_frozen, i)) and (not just_touched):
                    zone_retested = True

                array.set(sr_in_contact, i, retest_confirmed)

                if sr_zone_layout == SrLayout.zone_mode and (not is_fresh) and (not was_broken) and (not was_med_broken) and (not just_broke):
                    median_y = (zone_top + zone_bot) / 2
                    if close > median_y and close[1] <= median_y:
                        med_crossed_up = True
                        array.set(sr_median_broken, i, True)
                    elif close < median_y and close[1] >= median_y:
                        med_crossed_down = True
                        array.set(sr_median_broken, i, True)

                is_now_frozen: bool = array.get(sr_frozen, i)
                should_extend: bool = not is_now_frozen or just_flipped or just_touched

                ln = array.get(sr_lines, i)
                if not na(ln):
                    if should_extend:
                        method_call('set_x2', ln, bar_index)
                    method_call('set_color', ln, zone_color)

                bx = array.get(sr_boxes, i)
                if not na(bx):
                    if should_extend:
                        method_call('set_right', bx, bar_index)
                    method_call('set_border_color', bx, zone_color)
                    method_call('set_bgcolor', bx, color.new(zone_color, 100))

                md = array.get(sr_medians, i)
                if not na(md):
                    if should_extend:
                        method_call('set_x2', md, bar_index)
                    method_call('set_color', md, zone_color)

                lb = array.get(sr_labels, i)
                if not na(lb):
                    label_y = level
                    if just_flipped and was_frozen:
                        method_call('set_x', lb, bar_index)
                        method_call('set_y', lb, label_y)
                        method_call('set_style', lb, label.style_label_left)
                        method_call('set_textcolor', lb, zone_color)
                        method_call('set_text', lb, get_sr_label_text(is_res, level))
                    elif is_now_frozen and (not was_frozen):
                        center_x = left_x + cast_int(math.round((bar_index - left_x) * 0.5))
                        frozen_offset = sr_frozen_label_offset
                        frozen_label_y = label_y + frozen_offset if is_res else label_y - frozen_offset
                        method_call('set_x', lb, center_x)
                        method_call('set_y', lb, frozen_label_y)
                        method_call('set_style', lb, label.style_label_down if is_res else label.style_label_up)
                        method_call('set_textcolor', lb, zone_color)
                        method_call('set_text', lb, get_sr_label_text(is_res, level))
                    elif not is_now_frozen:
                        method_call('set_x', lb, bar_index)
                        method_call('set_y', lb, label_y)
                        method_call('set_textcolor', lb, zone_color)
                        method_call('set_text', lb, get_sr_label_text(is_res, level))
                    else:
                        frozen_offset = sr_frozen_label_offset
                        frozen_label_y = label_y + frozen_offset if is_res else label_y - frozen_offset
                        method_call('set_textcolor', lb, zone_color)
                        method_call('set_y', lb, frozen_label_y)
                        method_call('set_text', lb, get_sr_label_text(is_res, level))

        return (res_broken_up, sup_broken_down, med_crossed_up, med_crossed_down, zone_flipped, zone_retested)

    if sr_enabled:
        if regime_flip_bull:
            create_sr_zone(False)
        if regime_flip_bear:
            create_sr_zone(True)

    sr_resistance_broken_up, sr_support_broken_down, sr_median_crossed_up, sr_median_crossed_down, sr_zone_flipped, sr_zone_retested = update_sr_zones()

    sr_median_crossed: bool = sr_zone_layout == SrLayout.zone_mode and (sr_median_crossed_up or sr_median_crossed_down)

    sr_atr_max_dist = atr_slow * (sr_max_zones * 1.5)

    if sr_enabled and array.size(sr_lines) > 0:
        if not na(sr_atr_max_dist) and sr_atr_max_dist > 0:
            for i in pine_range(array.size(sr_lines) - 1, 0):
                level = array.get(sr_levels, i)
                if math.abs(close - level) > sr_atr_max_dist:
                    delete_sr_zone(i)

    if sr_enabled:
        while array.size(sr_lines) > sr_max_zones:
            res_count: int = 0
            sup_count: int = 0
            for i in pine_range(0, array.size(sr_is_res) - 1):
                if array.get(sr_is_res, i):
                    res_count += 1
                else:
                    sup_count += 1

            evict_res: bool = res_count > sup_count
            evict_sup: bool = sup_count > res_count

            old_idx: int = -1
            old_bar: int = bar_index
            for i in pine_range(0, array.size(sr_lines) - 1):
                is_res = array.get(sr_is_res, i)

                if evict_res and (not is_res) or (evict_sup and is_res):
                    continue
                lx = array.get(sr_left_x, i)
                if lx < old_bar:
                    old_bar = lx
                    old_idx = i

            if old_idx == -1:
                old_idx = 0

            delete_sr_zone(old_idx)

    sr_was_enabled: Persistent[bool] = True

    if sr_was_enabled and (not sr_enabled):
        if array.size(sr_lines) > 0:
            for i in pine_range(0, array.size(sr_lines) - 1):
                method_call('delete', array.get(sr_lines, i))
        if array.size(sr_boxes) > 0:
            for i in pine_range(0, array.size(sr_boxes) - 1):
                method_call('delete', array.get(sr_boxes, i))
        if array.size(sr_medians) > 0:
            for i in pine_range(0, array.size(sr_medians) - 1):
                method_call('delete', array.get(sr_medians, i))
        if array.size(sr_labels) > 0:
            for i in pine_range(0, array.size(sr_labels) - 1):
                method_call('delete', array.get(sr_labels, i))
        array.clear(sr_lines)
        array.clear(sr_boxes)
        array.clear(sr_medians)
        array.clear(sr_labels)
        array.clear(sr_is_res)
        array.clear(sr_frozen)
        array.clear(sr_levels)
        array.clear(sr_zone_tops)
        array.clear(sr_zone_bots)
        array.clear(sr_left_x)
        array.clear(sr_in_contact)
        array.clear(sr_first_touched)
        array.clear(sr_broken)
        array.clear(sr_median_broken)

    sr_was_enabled = sr_enabled

    plotsa = plot(senkoua, title='Senkou Span A', color=na if not show_senkou_a else kumo_bull_color, linewidth=1, offset=effective_offset - 1)
    plotsb = plot(senkoub, title='Senkou Span B', color=na if not show_senkou_b else kumo_bear_color, linewidth=1, offset=effective_offset - 1)

    kumo_midpoint = math.avg(senkoua, senkoub)
    kumo_mid_rsi = ta.rsi(kumo_midpoint, 14)

    def calc_kumo_fill_color():
        __block_result_29__ = na
        __switch__ = kumo_fill_style
        if __switch__ == KumoFillStyle.solid:
            __block_result_29__ = kumo_bull_color if senkoua > senkoub else kumo_bear_color if senkoua < senkoub else kumo_neutral_color
        elif __switch__ == KumoFillStyle.gradient:
            __block_result_29__ = color.from_gradient(kumo_mid_rsi, 0, 100, kumo_neutral_color, kumo_bull_color) if senkoua > senkoub else color.from_gradient(kumo_mid_rsi, 0, 100, kumo_neutral_color, kumo_bear_color) if senkoua < senkoub else kumo_neutral_color
        else:
            __block_result_29__ = NA(Color)
        return __block_result_29__

    kumo_fill_color_val = calc_kumo_fill_color()

    fill(plotsa, plotsb, color=na if not kumo_fill_enabled else color.new(kumo_fill_color_val, kumo_fill_transparency))

    plot(tenkansen, title='Tenkan-Sen', color=na if not show_tenkan else tenkan_color, linewidth=1)
    plot(kijunsen, title='Kijun-Sen', color=na if not show_kijun else kijun_color, linewidth=1)

    chikou_fixed_off = -(effective_offset - 1)
    plot(chikou_span if chikou_mode == ChikouMode.fixed and show_chikou else na, title='Chikou Span (Fixed)', color=chikou_color, linewidth=chikou_linewidth, offset=chikou_fixed_off)

    chikou_buf_x: Persistent[list[int]] = array.new_int()
    chikou_buf_y: Persistent[list[float]] = array.new_float()
    chikou_buf_color: Persistent[list[Color]] = array.new_color()
    chikou_drawn_lines: Persistent[list[Line]] = array.new_line()
    chikou_last_drawn_x: Persistent[int] = na(int)

    if chikou_mode == ChikouMode.adaptive and show_chikou:
        current_x = bar_index - adaptive_ch
        current_y = chikou_span
        current_c = chikou_color

        array.push(chikou_buf_x, current_x)
        array.push(chikou_buf_y, current_y)
        array.push(chikou_buf_color, current_c)

        max_buffer: int = 1000
        while array.size(chikou_buf_x) > max_buffer:
            array.shift(chikou_buf_x)
            array.shift(chikou_buf_y)
            array.shift(chikou_buf_color)

        should_draw = na(chikou_last_drawn_x) or current_x > chikou_last_drawn_x

        if should_draw:
            best_prev_idx = -1
            best_prev_x = NA(int)

            for i in pine_range(0, array.size(chikou_buf_x) - 2):
                x = array.get(chikou_buf_x, i)
                if x < current_x and (na(best_prev_x) or x > best_prev_x):
                    best_prev_x = x
                    best_prev_idx = i

            if best_prev_idx >= 0 and (not na(best_prev_x)):
                prev_y = array.get(chikou_buf_y, best_prev_idx)
                gap = current_x - best_prev_x

                if gap <= 10:
                    chikou_new_line = line.new(x1=best_prev_x, y1=prev_y, x2=current_x, y2=current_y, color=current_c, width=chikou_linewidth)
                    array.push(chikou_drawn_lines, chikou_new_line)

            chikou_last_drawn_x = current_x

            MAX_TV_LINES: int = 500

            reserved_sr_lines = sr_max_zones * (2 if sr_zone_layout == SrLayout.zone_mode else 1) if sr_enabled else 0
            reserved_tkr = tkr_max_history if tkr_enabled and tkr_show_median else 0
            reserved_waves = 30 if wave_enabled else 0
            reserved_pt = 12 if price_t_enabled else 0
            reserved_kihon = kihon_history * (3 if kihon_range == CycleRange.basic else 6 if kihon_range == CycleRange.extended else 12) if kihon_enabled else 0
            reserved_taito = taito_count * (1 + taito_harmonics * 2) if taito_enabled else 0
            reserved_buffer: int = 20

            max_chikou_lines = math.max(50, MAX_TV_LINES - reserved_sr_lines - reserved_tkr - reserved_waves - reserved_pt - reserved_kihon - reserved_taito - reserved_buffer)

            while array.size(chikou_drawn_lines) > max_chikou_lines:
                method_call('delete', array.shift(chikou_drawn_lines))

    if chikou_mode != ChikouMode.adaptive or not show_chikou:
        if array.size(chikou_drawn_lines) > 0:
            for i in pine_range(0, array.size(chikou_drawn_lines) - 1):
                method_call('delete', array.get(chikou_drawn_lines, i))
            array.clear(chikou_drawn_lines)
        array.clear(chikou_buf_x)
        array.clear(chikou_buf_y)
        array.clear(chikou_buf_color)
        chikou_last_drawn_x = na

    label_tenkan_price: Persistent[Label] = na(Label)
    label_kijun_price: Persistent[Label] = na(Label)
    label_tkkj_merged: Persistent[Label] = na(Label)

    if show_price_labels and barstate.islast:
        if not na(label_tenkan_price):
            label.delete(label_tenkan_price)
        if not na(label_kijun_price):
            label.delete(label_kijun_price)
        if not na(label_tkkj_merged):
            label.delete(label_tkkj_merged)

        tk_kj_spread = (tenkansen - kijunsen) / kijunsen * 100 if kijunsen != 0 else 0
        spread_str = string.format('{0}{1}%', '+' if tk_kj_spread >= 0 else '', string.tostring(tk_kj_spread, '#.##'))

        tk_dir = '↗' if tenkansen > tenkansen[1] else '↘' if tenkansen < tenkansen[1] else '→'
        kj_dir = '↗' if kijunsen > kijunsen[1] else '↘' if kijunsen < kijunsen[1] else '→'

        price_above_tk = close > tenkansen
        price_above_kj = close > kijunsen

        tk_dist_pct = (close - tenkansen) / tenkansen * 100 if tenkansen != 0 else 0
        kj_dist_pct = (close - kijunsen) / kijunsen * 100 if kijunsen != 0 else 0

        tk_kj_diff = math.abs(tenkansen - kijunsen)
        is_equilibrium = tk_kj_diff <= syminfo.mintick

        tk_above_kj = tenkansen > kijunsen

        tk_bg_color = tkkj_label_neutral_color if is_equilibrium else tkkj_label_bull_color if price_above_tk else tkkj_label_bear_color
        kj_bg_color = tkkj_label_neutral_color if is_equilibrium else tkkj_label_bull_color if price_above_kj else tkkj_label_bear_color

        tk_txt_color: Color = chart.fg_color
        kj_txt_color: Color = chart.fg_color

        tk_trend_text = 'Rising ↗' if tk_dir == '↗' else 'Falling ↘' if tk_dir == '↘' else 'Flat →'
        kj_trend_text = 'Rising ↗' if kj_dir == '↗' else 'Falling ↘' if kj_dir == '↘' else 'Flat →'
        tk_position_text = '▲ Above (Support)' if price_above_tk else '▼ Below (Resistance)'
        kj_position_text = '▲ Above (Support)' if price_above_kj else '▼ Below (Resistance)'

        tk_kj_state = 'TK > KJ — ▲ Bullish' if tk_above_kj else 'TK < KJ — ▼ Bearish' if tenkansen < kijunsen else 'TK = KJ — → Flat'

        tk_tooltip = string.format('TENKAN-SEN\n' + '{0}\n' + '\n' + 'POSITION\n' + 'Distance: {1}%\n' + 'Price is {2}\n' + '\n' + 'CONTEXT\n' + 'Trend: {3}\n' + 'Spread: {4}\n' + 'TK vs KJ: {5}', string.tostring(math.round_to_mintick(tenkansen)), string.tostring(tk_dist_pct, '#.##'), tk_position_text, tk_trend_text, spread_str, tk_kj_state)

        kj_tooltip = string.format('KIJUN-SEN\n' + '{0}\n' + '\n' + 'POSITION\n' + 'Distance: {1}%\n' + 'Price is {2}\n' + '\n' + 'CONTEXT\n' + 'Trend: {3}\n' + 'Spread: {4}\n' + 'TK vs KJ: {5}', string.tostring(math.round_to_mintick(kijunsen)), string.tostring(kj_dist_pct, '#.##'), kj_position_text, kj_trend_text, spread_str, tk_kj_state)

        merged_tooltip = string.format('EQUILIBRIUM\n' + 'TK ≈ KJ\n' + '\n' + 'LEVELS\n' + 'Tenkan: {0}\n' + 'Kijun: {1}\n' + 'Spread: {2}\n' + '\n' + 'INSIGHT\n' + '⇄ Lines converged — Loss of momentum\n' + 'Watch for breakout or reversal', string.tostring(math.round_to_mintick(tenkansen)), string.tostring(math.round_to_mintick(kijunsen)), spread_str)

        if is_equilibrium and show_tenkan and show_kijun:
            merged_price = math.avg(tenkansen, kijunsen)
            merged_dir = tk_dir if tk_dir == kj_dir else '⇄'
            merged_text = string.format('TK≈KJ {0} {1}', merged_dir, math.round_to_mintick(merged_price))

            label_tkkj_merged = label.new(bar_index, merged_price, merged_text, style=label.style_label_left, textcolor=tk_txt_color, size=size.small, color=tkkj_label_neutral_color, tooltip=merged_tooltip)
        else:
            if show_tenkan:
                tk_text = string.format('TK {0} {1} ({2})', tk_dir, math.round_to_mintick(tenkansen), spread_str)
                label_tenkan_price = label.new(bar_index, tenkansen, tk_text, style=label.style_label_left, textcolor=tk_txt_color, size=size.small, color=tk_bg_color, tooltip=tk_tooltip)

            if show_kijun:
                kj_dist_str = string.format('{0}{1}%', '+' if kj_dist_pct >= 0 else '', string.tostring(kj_dist_pct, '#.##'))
                kj_text = string.format('KJ {0} {1} [{2}]', kj_dir, math.round_to_mintick(kijunsen), kj_dist_str)
                label_kijun_price = label.new(bar_index, kijunsen, kj_text, style=label.style_label_left, textcolor=kj_txt_color, size=size.small, color=kj_bg_color, tooltip=kj_tooltip)

    swing_ph = ta.pivothigh(high, swing_length, swing_length)
    swing_pl = ta.pivotlow(low, swing_length, swing_length)

    swing_points: Persistent[list[SwingPoint]] = array.new(0, NA(SwingPoint))

    if swing_enabled:
        swing_bar = bar_index[swing_length]
        swing_tm = time[swing_length]

        if not na(swing_ph):
            last_dir = array.last(swing_points).dir if array.size(swing_points) > 0 else 0
            if last_dir == 1:
                last_pt: SwingPoint = array.last(swing_points)
                if swing_ph > last_pt.price:
                    last_pt.bar_idx = swing_bar
                    last_pt.bar_tm = swing_tm
                    last_pt.price = swing_ph
            else:
                array.push(swing_points, SwingPoint(swing_bar, swing_tm, swing_ph, 1))

        if not na(swing_pl):
            last_dir = array.last(swing_points).dir if array.size(swing_points) > 0 else 0
            if last_dir == -1:
                last_pt: SwingPoint = array.last(swing_points)
                if swing_pl < last_pt.price:
                    last_pt.bar_idx = swing_bar
                    last_pt.bar_tm = swing_tm
                    last_pt.price = swing_pl
            else:
                array.push(swing_points, SwingPoint(swing_bar, swing_tm, swing_pl, -1))

        while array.size(swing_points) > swing_max_stored:
            array.shift(swing_points)

    swing_labels: Persistent[list[Label]] = array.new_label()

    if swing_enabled and swing_show_hl:
        if not na(swing_ph):
            lbl = label.new(bar_index[swing_length], swing_ph, '', style=label.style_circle, color=bear_event_color, size=size.auto, yloc=yloc.abovebar)
            array.push(swing_labels, lbl)
        if not na(swing_pl):
            lbl = label.new(bar_index[swing_length], swing_pl, '', style=label.style_circle, color=bull_event_color, size=size.auto, yloc=yloc.belowbar)
            array.push(swing_labels, lbl)

        while array.size(swing_labels) > swing_max_stored * 2:
            method_call('delete', array.shift(swing_labels))

    def wave_color(tag: str):
        __block_result_30__ = na
        __switch__ = tag
        if __switch__ == "I":
            __block_result_30__ = wave_color_I
        elif __switch__ == "V":
            __block_result_30__ = wave_color_V
        elif __switch__ == "N":
            __block_result_30__ = wave_color_N
        elif __switch__ == "P":
            __block_result_30__ = wave_color_P
        elif __switch__ == "Y":
            __block_result_30__ = wave_color_Y
        elif __switch__ == "W":
            __block_result_30__ = wave_color_W
        else:
            __block_result_30__ = color.gray
        return __block_result_30__

    def wave_tooltip(tag: str, bias: int, amp_pct: float, duration: int):
        dir_str = '▲ Bullish' if bias == 1 else '▼ Bearish'

        __block_result_31__ = na
        __switch__ = tag
        if __switch__ == "I":
            __block_result_31__ = "Impulse — single directional leg (A→B)"
        elif __switch__ == "V":
            __block_result_31__ = "Return — price returns near origin (A→B→C ≈ A)"
        elif __switch__ == "N":
            __block_result_31__ = "Continuation — impulse, correction, continuation (A→B→C→D exceeds B)"
        elif __switch__ == "P":
            __block_result_31__ = "Converging triangle — narrowing range (compression)"
        elif __switch__ == "Y":
            __block_result_31__ = "Expanding triangle — widening range (expansion)"
        elif __switch__ == "W":
            __block_result_31__ = "Double formation — repeating structure (A≈C≈E, B≈D)"
        else:
            __block_result_31__ = ""
        desc: str = __block_result_31__

        __block_result_32__ = na
        __switch__ = tag
        if __switch__ == "I":
            __block_result_32__ = "A→B: impulse"
        elif __switch__ == "V":
            __block_result_32__ = "A→B: impulse | B→C: return to A"
        elif __switch__ == "N":
            __block_result_32__ = "A→B: impulse | B→C: correction | C→D: continuation"
        elif __switch__ == "P":
            __block_result_32__ = "A-C: contracting | B-D: contracting"
        elif __switch__ == "Y":
            __block_result_32__ = "A-C: expanding | B-D: expanding"
        elif __switch__ == "W":
            __block_result_32__ = "A→B→C→D→E: double pattern"
        else:
            __block_result_32__ = ""
        structure: str = __block_result_32__

        return string.format('Wave {0} ({1})\n{2}\n\nStructure: {3}\nDuration: {4} bars | Amplitude: {5}%', tag, dir_str, desc, structure, duration, string.tostring(amp_pct, '#.#'))

    wave_lines: Persistent[list[Line]] = array.new_line()
    wave_labels: Persistent[list[Label]] = array.new_label()

    if swing_enabled and wave_enabled and barstate.islast:
        if array.size(wave_lines) > 0:
            for i in pine_range(0, array.size(wave_lines) - 1):
                method_call('delete', array.get(wave_lines, i))
            array.clear(wave_lines)
        if array.size(wave_labels) > 0:
            for i in pine_range(0, array.size(wave_labels) - 1):
                method_call('delete', array.get(wave_labels, i))
            array.clear(wave_labels)

        sz = array.size(swing_points)

        if sz >= 2:
            idx: int = sz - 1
            found: int = 0

            while idx >= 1 and found < wave_max_display:
                matched_tag: str = ""
                matched_bias: int = 0
                matched_pts: int = 0
                amp_pct: float = 0.0

                if matched_tag == '' and idx >= 3 and wave_show_N:
                    A: SwingPoint = array.get(swing_points, idx - 3)
                    B: SwingPoint = array.get(swing_points, idx - 2)
                    C: SwingPoint = array.get(swing_points, idx - 1)
                    D: SwingPoint = array.get(swing_points, idx)
                    duration = D.bar_idx - A.bar_idx
                    leg = math.abs(A.price - B.price)

                    threshold = leg * 0.2
                    is_bull = A.price < B.price and C.price > A.price + threshold and (C.price < B.price - threshold) and (D.price > B.price + threshold)
                    is_bear = A.price > B.price and C.price < A.price - threshold and (C.price > B.price + threshold) and (D.price < B.price - threshold)

                    if (is_bull or is_bear) and duration >= 9:
                        matched_tag = "N"
                        matched_bias = 1 if is_bull else -1
                        matched_pts = 4
                        amp_pct = leg / A.price * 100 if A.price != 0 else 0.0

                if matched_tag == '' and idx >= 4 and wave_show_W:
                    A: SwingPoint = array.get(swing_points, idx - 4)
                    B: SwingPoint = array.get(swing_points, idx - 3)
                    C: SwingPoint = array.get(swing_points, idx - 2)
                    D: SwingPoint = array.get(swing_points, idx - 1)
                    E: SwingPoint = array.get(swing_points, idx)
                    duration = E.bar_idx - A.bar_idx
                    leg = math.abs(A.price - B.price)
                    threshold = leg * 0.2

                    is_pattern = math.abs(A.price - C.price) <= threshold and math.abs(C.price - E.price) <= threshold and (math.abs(B.price - D.price) <= threshold) and (A.dir == C.dir) and (B.dir == D.dir)
                    if is_pattern and duration >= 9:
                        matched_tag = "W"
                        matched_bias = -1 if B.price > A.price else 1
                        matched_pts = 5
                        amp_pct = leg / A.price * 100 if A.price != 0 else 0.0

                if matched_tag == '' and idx >= 3 and wave_show_P:
                    A: SwingPoint = array.get(swing_points, idx - 3)
                    B: SwingPoint = array.get(swing_points, idx - 2)
                    C: SwingPoint = array.get(swing_points, idx - 1)
                    D: SwingPoint = array.get(swing_points, idx)
                    duration = D.bar_idx - A.bar_idx
                    range_AB = math.abs(A.price - B.price)
                    range_CD = math.abs(C.price - D.price)

                    if range_CD < range_AB * 0.85 and range_CD > range_AB * 0.1 and (duration >= 9):
                        hi_AB = math.max(A.price, B.price)
                        lo_AB = math.min(A.price, B.price)
                        if C.price <= hi_AB and C.price >= lo_AB and (D.price <= hi_AB) and (D.price >= lo_AB):
                            matched_tag = "P"
                            matched_bias = 1 if D.dir == 1 else -1
                            matched_pts = 4
                            amp_pct = range_AB / A.price * 100 if A.price != 0 else 0.0

                if matched_tag == '' and idx >= 3 and wave_show_Y:
                    A: SwingPoint = array.get(swing_points, idx - 3)
                    B: SwingPoint = array.get(swing_points, idx - 2)
                    C: SwingPoint = array.get(swing_points, idx - 1)
                    D: SwingPoint = array.get(swing_points, idx)
                    duration = D.bar_idx - A.bar_idx
                    range_AB = math.abs(A.price - B.price)
                    range_CD = math.abs(C.price - D.price)

                    if range_CD > range_AB * 1.15 and duration >= 9:
                        hi_AB = math.max(A.price, B.price)
                        lo_AB = math.min(A.price, B.price)
                        if (C.price > hi_AB or C.price < lo_AB) and (D.price > hi_AB or D.price < lo_AB):
                            matched_tag = "Y"
                            matched_bias = 1 if D.dir == 1 else -1
                            matched_pts = 4
                            amp_pct = range_CD / A.price * 100 if A.price != 0 else 0.0

                if matched_tag == '' and idx >= 2 and wave_show_V:
                    A: SwingPoint = array.get(swing_points, idx - 2)
                    B: SwingPoint = array.get(swing_points, idx - 1)
                    C: SwingPoint = array.get(swing_points, idx)
                    duration = C.bar_idx - A.bar_idx
                    leg = math.abs(A.price - B.price)
                    threshold = leg * 0.2

                    if math.abs(C.price - A.price) <= threshold and duration >= 9:
                        matched_tag = "V"
                        matched_bias = 1 if C.dir == -1 else -1
                        matched_pts = 3
                        amp_pct = leg / A.price * 100 if A.price != 0 else 0.0

                if matched_tag == '' and idx >= 1 and wave_show_I:
                    A: SwingPoint = array.get(swing_points, idx - 1)
                    B: SwingPoint = array.get(swing_points, idx)
                    duration = B.bar_idx - A.bar_idx
                    leg = math.abs(A.price - B.price)
                    if duration >= 9:
                        matched_tag = "I"
                        matched_bias = 1 if B.price > A.price else -1
                        matched_pts = 2
                        amp_pct = leg / A.price * 100 if A.price != 0 else 0.0

                if matched_tag != '':
                    clr = wave_color(matched_tag)
                    start_i = idx - matched_pts + 1

                    if bar_index - array.get(swing_points, start_i).bar_idx > 4999:
                        idx -= matched_pts - 1
                        continue
                    duration = array.get(swing_points, idx).bar_idx - array.get(swing_points, start_i).bar_idx
                    tip = wave_tooltip(matched_tag, matched_bias, amp_pct, duration)

                    if matched_tag == 'P' or matched_tag == 'Y':
                        pA: SwingPoint = array.get(swing_points, start_i)
                        pB: SwingPoint = array.get(swing_points, start_i + 1)
                        pC: SwingPoint = array.get(swing_points, start_i + 2)
                        pD: SwingPoint = array.get(swing_points, start_i + 3)
                        array.push(wave_lines, line.new(pA.bar_idx, pA.price, pC.bar_idx, pC.price, color=clr, style=line.style_solid, width=2))
                        array.push(wave_lines, line.new(pB.bar_idx, pB.price, pD.bar_idx, pD.price, color=clr, style=line.style_solid, width=2))
                    else:
                        for j in pine_range(start_i, idx - 1):
                            p1: SwingPoint = array.get(swing_points, j)
                            p2: SwingPoint = array.get(swing_points, j + 1)
                            array.push(wave_lines, line.new(p1.bar_idx, p1.price, p2.bar_idx, p2.price, color=clr, style=line.style_solid, width=2))

                    end_pt: SwingPoint = array.get(swing_points, idx)
                    lbl_yloc = yloc.abovebar if end_pt.dir == 1 else yloc.belowbar
                    array.push(wave_labels, label.new(end_pt.bar_idx, end_pt.price, matched_tag, style=label.style_none, textcolor=clr, size=size.normal, yloc=lbl_yloc, tooltip=tip))

                    found += 1
                    idx -= 1 if wave_overlap else matched_pts - 1
                else:
                    idx -= 1

    pt_lines: Persistent[list[Line]] = array.new_line()
    pt_labels: Persistent[list[Label]] = array.new_label()

    if swing_enabled and wave_enabled and price_t_enabled and barstate.islast:
        if array.size(pt_lines) > 0:
            for i in pine_range(0, array.size(pt_lines) - 1):
                method_call('delete', array.get(pt_lines, i))
            array.clear(pt_lines)
        if array.size(pt_labels) > 0:
            for i in pine_range(0, array.size(pt_labels) - 1):
                method_call('delete', array.get(pt_labels, i))
            array.clear(pt_labels)

        sz = array.size(swing_points)

        n_found: bool = False
        nA: float = na(float)
        nB: float = na(float)
        nC: float = na(float)
        nD_bar: int = na(int)
        n_bias: int = 0

        if sz >= 4:
            scan: int = sz - 1

            scan_limit: int = math.max(3, sz - 20)
            while scan >= scan_limit and (not n_found):
                A: SwingPoint = array.get(swing_points, scan - 3)
                B: SwingPoint = array.get(swing_points, scan - 2)
                C: SwingPoint = array.get(swing_points, scan - 1)
                D: SwingPoint = array.get(swing_points, scan)
                duration = D.bar_idx - A.bar_idx
                leg = math.abs(A.price - B.price)
                threshold = leg * 0.2
                is_bull = A.price < B.price and C.price > A.price + threshold and (C.price < B.price - threshold) and (D.price > B.price + threshold)
                is_bear = A.price > B.price and C.price < A.price - threshold and (C.price > B.price + threshold) and (D.price < B.price - threshold)
                if (is_bull or is_bear) and duration >= 9:
                    nA = A.price
                    nB = B.price
                    nC = C.price
                    nD_bar = D.bar_idx
                    n_bias = 1 if is_bull else -1
                    n_found = True
                scan -= 1

        tv: float = na(float)
        te: float = na(float)
        tn: float = na(float)
        tnt: float = na(float)
        t2e: float = na(float)
        t3e: float = na(float)

        if n_found:
            tv = nB + (nB - nC)
            te = nB + (nB - nA)
            tn = nC + (nB - nA)
            tnt = nC + (nC - nA)
            t2e = nB + 2 * (nB - nA)
            t3e = nB + 3 * (nB - nA)

            bars_since_D = bar_index - nD_bar
            if bars_since_D <= 4999:
                hi_since_D: float = high
                lo_since_D: float = low
                if bars_since_D > 0:
                    for k in pine_range(0, bars_since_D - 1):
                        hi_since_D = math.max(hi_since_D, high[k])
                        lo_since_D = math.min(lo_since_D, low[k])

                pt_names: list[str] = array.from_items('V', 'N', 'E', 'NT', '2E', '3E')
                pt_levels: list[float] = array.from_items(tv, tn, te, tnt, t2e, t3e)
                pt_show: list[bool] = array.from_items(price_t_show_V, price_t_show_N, price_t_show_E, price_t_show_NT, price_t_show_2E, price_t_show_3E)
                pt_colors: list[Color] = array.from_items(price_t_color_V, price_t_color_N, price_t_color_E, price_t_color_NT, price_t_color_2E, price_t_color_3E)

                for i in pine_range(0, 5):
                    if array.get(pt_show, i):
                        lvl = array.get(pt_levels, i)
                        clr = array.get(pt_colors, i)
                        nm: str = array.get(pt_names, i)

                        reached: bool = False
                        if price_t_validate:
                            if n_bias == 1:
                                reached = hi_since_D >= lvl
                            else:
                                reached = lo_since_D <= lvl

                        valid_mark = (' ✓' if reached else ' ⋯') if price_t_validate else ''
                        valid_state: str = ('(Reached ✓)' if reached else '(Pending ⋯)') if price_t_validate else '(Completed)'

                        __block_result_33__ = na
                        __switch_5__ = nm
                        if __switch_5__ == "V":
                            __block_result_33__ = string.format('V = B + (B - C) = {0} + ({0} - {1})', string.tostring(nB, format.mintick), string.tostring(nC, format.mintick))
                        elif __switch_5__ == "E":
                            __block_result_33__ = string.format('E = B + (B - A) = {0} + ({0} - {1})', string.tostring(nB, format.mintick), string.tostring(nA, format.mintick))
                        elif __switch_5__ == "N":
                            __block_result_33__ = string.format('N = C + (B - A) = {0} + ({1} - {2})', string.tostring(nC, format.mintick), string.tostring(nB, format.mintick), string.tostring(nA, format.mintick))
                        elif __switch_5__ == "NT":
                            __block_result_33__ = string.format('NT = C + (C - A) = {0} + ({0} - {1})', string.tostring(nC, format.mintick), string.tostring(nA, format.mintick))
                        elif __switch_5__ == "2E":
                            __block_result_33__ = string.format('2E = B + 2x(B - A) = {0} + 2x({0} - {1})', string.tostring(nB, format.mintick), string.tostring(nA, format.mintick))
                        elif __switch_5__ == "3E":
                            __block_result_33__ = string.format('3E = B + 3x(B - A) = {0} + 3x({0} - {1})', string.tostring(nB, format.mintick), string.tostring(nA, format.mintick))
                        else:
                            __block_result_33__ = ""
                        formula: str = __block_result_33__

                        dir_str = '▲ Bullish' if n_bias == 1 else '▼ Bearish'
                        tip = string.format('Price Target {0} {1}\n{2} N-wave\n\n{3}\n= {4}', nm, valid_state, dir_str, formula, string.tostring(lvl, format.mintick))

                        array.push(pt_lines, line.new(nD_bar, lvl, bar_index + effective_offset, lvl, color=clr, style=line.style_dashed, width=1))

                        lbl_text = string.format('{0} • {1}{2}', nm, string.tostring(lvl, format.mintick), valid_mark)
                        array.push(pt_labels, label.new(bar_index + effective_offset, lvl, lbl_text, xloc=xloc.bar_index, style=label.style_label_left, color=color.new(clr, 100), textcolor=clr, size=size.small, tooltip=tip))

        if price_t_developing and sz >= 3:
            devA: SwingPoint = array.get(swing_points, sz - 3)
            devB: SwingPoint = array.get(swing_points, sz - 2)
            devC: SwingPoint = array.get(swing_points, sz - 1)

            dev_duration = devC.bar_idx - devA.bar_idx
            dev_leg = math.abs(devA.price - devB.price)
            dev_thr = dev_leg * 0.2

            dev_bull = devA.price < devB.price and devC.price > devA.price + dev_thr and (devC.price < devB.price - dev_thr)
            dev_bear = devA.price > devB.price and devC.price < devA.price - dev_thr and (devC.price > devB.price + dev_thr)

            if (dev_bull or dev_bear) and dev_duration >= 9:
                dev_bias = 1 if dev_bull else -1

                dv: float = devB.price + (devB.price - devC.price)
                de: float = devB.price + (devB.price - devA.price)
                dn: float = devC.price + (devB.price - devA.price)
                dnt: float = devC.price + (devC.price - devA.price)
                d2e: float = devB.price + 2 * (devB.price - devA.price)
                d3e: float = devB.price + 3 * (devB.price - devA.price)

                dev_names: list[str] = array.from_items('V', 'N', 'E', 'NT', '2E', '3E')
                dev_levels: list[float] = array.from_items(dv, dn, de, dnt, d2e, d3e)
                dev_show: list[bool] = array.from_items(price_t_show_V, price_t_show_N, price_t_show_E, price_t_show_NT, price_t_show_2E, price_t_show_3E)
                dev_colors: list[Color] = array.from_items(price_t_color_V, price_t_color_N, price_t_color_E, price_t_color_NT, price_t_color_2E, price_t_color_3E)

                for i in pine_range(0, 5):
                    if array.get(dev_show, i):
                        dlvl = array.get(dev_levels, i)
                        dclr = array.get(dev_colors, i)
                        dnm: str = array.get(dev_names, i)

                        dup: bool = False
                        if n_found:
                            __switch_6__ = dnm
                            if __switch_6__ == "V":
                                dup = math.abs(dlvl - tv) / math.max(dlvl, 1) < 0.001
                            elif __switch_6__ == "N":
                                dup = math.abs(dlvl - tn) / math.max(dlvl, 1) < 0.001
                            elif __switch_6__ == "E":
                                dup = math.abs(dlvl - te) / math.max(dlvl, 1) < 0.001
                            elif __switch_6__ == "NT":
                                dup = math.abs(dlvl - tnt) / math.max(dlvl, 1) < 0.001
                            elif __switch_6__ == "2E":
                                dup = math.abs(dlvl - t2e) / math.max(dlvl, 1) < 0.001
                            elif __switch_6__ == "3E":
                                dup = math.abs(dlvl - t3e) / math.max(dlvl, 1) < 0.001
                        if dup:
                            continue

                        dev_alpha: int = 35
                        dev_line_clr = color.new(dclr, dev_alpha)

                        dev_dir_str = '▲ Bullish' if dev_bias == 1 else '▼ Bearish'
                        __block_result_34__ = na
                        __switch_5__ = dnm
                        if __switch_5__ == "V":
                            __block_result_34__ = string.format('V = B + (B - C) = {0} + ({0} - {1})', string.tostring(devB.price, format.mintick), string.tostring(devC.price, format.mintick))
                        elif __switch_5__ == "E":
                            __block_result_34__ = string.format('E = B + (B - A) = {0} + ({0} - {1})', string.tostring(devB.price, format.mintick), string.tostring(devA.price, format.mintick))
                        elif __switch_5__ == "N":
                            __block_result_34__ = string.format('N = C + (B - A) = {0} + ({1} - {2})', string.tostring(devC.price, format.mintick), string.tostring(devB.price, format.mintick), string.tostring(devA.price, format.mintick))
                        elif __switch_5__ == "NT":
                            __block_result_34__ = string.format('NT = C + (C - A) = {0} + ({0} - {1})', string.tostring(devC.price, format.mintick), string.tostring(devA.price, format.mintick))
                        elif __switch_5__ == "2E":
                            __block_result_34__ = string.format('2E = B + 2x(B - A) = {0} + 2x({0} - {1})', string.tostring(devB.price, format.mintick), string.tostring(devA.price, format.mintick))
                        elif __switch_5__ == "3E":
                            __block_result_34__ = string.format('3E = B + 3x(B - A) = {0} + 3x({0} - {1})', string.tostring(devB.price, format.mintick), string.tostring(devA.price, format.mintick))
                        else:
                            __block_result_34__ = ""
                        dev_formula: str = __block_result_34__

                        dev_tip = string.format('Price Target ⟨{0}⟩ (Developing)\n{1} N-wave (A→B→C forming)\n\n{2}\n= {3}', dnm, dev_dir_str, dev_formula, string.tostring(dlvl, format.mintick))

                        array.push(pt_lines, line.new(devC.bar_idx, dlvl, bar_index + effective_offset, dlvl, color=dev_line_clr, style=line.style_dotted, width=1))

                        dev_lbl_text = string.format('⟨{0}⟩ • {1}', dnm, string.tostring(dlvl, format.mintick))
                        array.push(pt_labels, label.new(bar_index + effective_offset, dlvl, dev_lbl_text, xloc=xloc.bar_index, style=label.style_label_left, color=color.new(dclr, 100), textcolor=color.new(dclr, dev_alpha - 20), size=size.small, tooltip=dev_tip))

    kihon_flip_bars: Persistent[list[int]] = array.new_int()
    kihon_flip_dirs: Persistent[list[int]] = array.new_int()

    tk_cross_event: bool = ta.cross(close, tenkansen)
    kj_cross_event: bool = ta.cross(close, kijunsen)
    tk_kj_cross_event: bool = ta.cross(tenkansen, kijunsen)
    kumo_change_event: bool = (senkoua >= senkoub) != (senkoua[1] >= senkoub[1])

    tk_cross_dir: int = 1 if close > tenkansen else -1
    kj_cross_dir: int = 1 if close > kijunsen else -1
    tk_kj_cross_dir: int = 1 if tenkansen > kijunsen else -1
    kumo_change_dir: int = 1 if senkoua >= senkoub else -1

    last_wave_bar: Persistent[int] = -1
    wave_completed: bool = False
    wave_dir: int = 0
    wave_type: str = ""

    if swing_enabled and wave_enabled and (array.size(swing_points) >= 2):
        wsz = array.size(swing_points)

        latest_sp: SwingPoint = array.last(swing_points)
        if latest_sp.bar_idx == bar_index - swing_length:
            if wsz >= 4 and last_wave_bar != latest_sp.bar_idx:
                wA: SwingPoint = array.get(swing_points, wsz - 4)
                wB: SwingPoint = array.get(swing_points, wsz - 3)
                wC: SwingPoint = array.get(swing_points, wsz - 2)
                wD: SwingPoint = array.get(swing_points, wsz - 1)
                w_leg = math.abs(wA.price - wB.price)
                w_thr = w_leg * 0.2
                w_bull = wA.price < wB.price and wC.price > wA.price + w_thr and (wC.price < wB.price - w_thr) and (wD.price > wB.price + w_thr)
                w_bear = wA.price > wB.price and wC.price < wA.price - w_thr and (wC.price > wB.price + w_thr) and (wD.price < wB.price - w_thr)
                if (w_bull or w_bear) and wD.bar_idx - wA.bar_idx >= 9:
                    wave_completed = True
                    wave_dir = 1 if w_bull else -1
                    wave_type = "N"
                    last_wave_bar = latest_sp.bar_idx

            if not wave_completed and wsz >= 5 and (last_wave_bar != latest_sp.bar_idx):
                wA: SwingPoint = array.get(swing_points, wsz - 5)
                wB: SwingPoint = array.get(swing_points, wsz - 4)
                wC: SwingPoint = array.get(swing_points, wsz - 3)
                wD: SwingPoint = array.get(swing_points, wsz - 2)
                wE: SwingPoint = array.get(swing_points, wsz - 1)
                w_leg = math.abs(wA.price - wB.price)
                w_thr = w_leg * 0.2
                w_duration = wE.bar_idx - wA.bar_idx
                is_w_pattern = math.abs(wA.price - wC.price) <= w_thr and math.abs(wC.price - wE.price) <= w_thr and (math.abs(wB.price - wD.price) <= w_thr) and (wA.dir == wC.dir) and (wB.dir == wD.dir)
                if is_w_pattern and w_duration >= 9:
                    wave_completed = True
                    wave_dir = -1 if wB.price > wA.price else 1
                    wave_type = "W"
                    last_wave_bar = latest_sp.bar_idx

            if not wave_completed and wsz >= 4 and (last_wave_bar != latest_sp.bar_idx):
                wA: SwingPoint = array.get(swing_points, wsz - 4)
                wB: SwingPoint = array.get(swing_points, wsz - 3)
                wC: SwingPoint = array.get(swing_points, wsz - 2)
                wD: SwingPoint = array.get(swing_points, wsz - 1)
                w_duration = wD.bar_idx - wA.bar_idx
                range_AB = math.abs(wA.price - wB.price)
                range_CD = math.abs(wC.price - wD.price)
                if range_CD < range_AB * 0.85 and range_CD > range_AB * 0.1 and (w_duration >= 9):
                    hi_AB = math.max(wA.price, wB.price)
                    lo_AB = math.min(wA.price, wB.price)
                    if wC.price <= hi_AB and wC.price >= lo_AB and (wD.price <= hi_AB) and (wD.price >= lo_AB):
                        wave_completed = True
                        wave_dir = 1 if wD.dir == 1 else -1
                        wave_type = "P"
                        last_wave_bar = latest_sp.bar_idx

            if not wave_completed and wsz >= 4 and (last_wave_bar != latest_sp.bar_idx):
                wA: SwingPoint = array.get(swing_points, wsz - 4)
                wB: SwingPoint = array.get(swing_points, wsz - 3)
                wC: SwingPoint = array.get(swing_points, wsz - 2)
                wD: SwingPoint = array.get(swing_points, wsz - 1)
                w_duration = wD.bar_idx - wA.bar_idx
                range_AB = math.abs(wA.price - wB.price)
                range_CD = math.abs(wC.price - wD.price)
                if range_CD > range_AB * 1.15 and w_duration >= 9:
                    hi_AB = math.max(wA.price, wB.price)
                    lo_AB = math.min(wA.price, wB.price)
                    if (wC.price > hi_AB or wC.price < lo_AB) and (wD.price > hi_AB or wD.price < lo_AB):
                        wave_completed = True
                        wave_dir = 1 if wD.dir == 1 else -1
                        wave_type = "Y"
                        last_wave_bar = latest_sp.bar_idx

            if not wave_completed and wsz >= 3 and (last_wave_bar != latest_sp.bar_idx):
                wA: SwingPoint = array.get(swing_points, wsz - 3)
                wB: SwingPoint = array.get(swing_points, wsz - 2)
                wC: SwingPoint = array.get(swing_points, wsz - 1)
                w_leg = math.abs(wA.price - wB.price)
                w_thr = w_leg * 0.2
                if math.abs(wC.price - wA.price) <= w_thr and wC.bar_idx - wA.bar_idx >= 9:
                    wave_completed = True
                    wave_dir = 1 if wC.dir == -1 else -1
                    wave_type = "V"
                    last_wave_bar = latest_sp.bar_idx

            if not wave_completed and last_wave_bar != latest_sp.bar_idx:
                wA: SwingPoint = array.get(swing_points, wsz - 2)
                wB: SwingPoint = array.get(swing_points, wsz - 1)
                if wB.bar_idx - wA.bar_idx >= 9:
                    wave_completed = True
                    wave_dir = 1 if wB.price > wA.price else -1
                    wave_type = "I"
                    last_wave_bar = latest_sp.bar_idx

    pt_alert_V: Persistent[float] = na(float)
    pt_alert_N: Persistent[float] = na(float)
    pt_alert_E: Persistent[float] = na(float)
    pt_alert_NT: Persistent[float] = na(float)
    pt_alert_2E: Persistent[float] = na(float)
    pt_alert_3E: Persistent[float] = na(float)
    pt_alert_bias: Persistent[int] = 0
    pt_reached_V: PersistentSeries[bool] = False
    pt_reached_N: PersistentSeries[bool] = False
    pt_reached_E: PersistentSeries[bool] = False
    pt_reached_NT: PersistentSeries[bool] = False
    pt_reached_2E: PersistentSeries[bool] = False
    pt_reached_3E: PersistentSeries[bool] = False

    if wave_completed and wave_type == 'N' and (array.size(swing_points) >= 4):
        wsz_pt = array.size(swing_points)
        ptA: float = array.get(swing_points, wsz_pt - 4).price
        ptB: float = array.get(swing_points, wsz_pt - 3).price
        ptC: float = array.get(swing_points, wsz_pt - 2).price
        pt_alert_V = ptB + (ptB - ptC)
        pt_alert_E = ptB + (ptB - ptA)
        pt_alert_N = ptC + (ptB - ptA)
        pt_alert_NT = ptC + (ptC - ptA)
        pt_alert_2E = ptB + 2 * (ptB - ptA)
        pt_alert_3E = ptB + 3 * (ptB - ptA)
        pt_alert_bias = wave_dir
        pt_reached_V = False
        pt_reached_N = False
        pt_reached_E = False
        pt_reached_NT = False
        pt_reached_2E = False
        pt_reached_3E = False

    pt_just_reached_bull: bool = False
    pt_just_reached_bear: bool = False

    if pt_alert_bias == 1 and (not na(pt_alert_V)):
        if not pt_reached_V and high >= pt_alert_V:
            pt_reached_V = True
            pt_just_reached_bull = True
        if not pt_reached_N and high >= pt_alert_N:
            pt_reached_N = True
            pt_just_reached_bull = True
        if not pt_reached_E and high >= pt_alert_E:
            pt_reached_E = True
            pt_just_reached_bull = True
        if not pt_reached_NT and high >= pt_alert_NT:
            pt_reached_NT = True
            pt_just_reached_bull = True
        if not pt_reached_2E and high >= pt_alert_2E:
            pt_reached_2E = True
            pt_just_reached_bull = True
        if not pt_reached_3E and high >= pt_alert_3E:
            pt_reached_3E = True
            pt_just_reached_bull = True
    elif pt_alert_bias == -1 and (not na(pt_alert_V)):
        if not pt_reached_V and low <= pt_alert_V:
            pt_reached_V = True
            pt_just_reached_bear = True
        if not pt_reached_N and low <= pt_alert_N:
            pt_reached_N = True
            pt_just_reached_bear = True
        if not pt_reached_E and low <= pt_alert_E:
            pt_reached_E = True
            pt_just_reached_bear = True
        if not pt_reached_NT and low <= pt_alert_NT:
            pt_reached_NT = True
            pt_just_reached_bear = True
        if not pt_reached_2E and low <= pt_alert_2E:
            pt_reached_2E = True
            pt_just_reached_bear = True
        if not pt_reached_3E and low <= pt_alert_3E:
            pt_reached_3E = True
            pt_just_reached_bear = True

    kihon_event_bull: bool = False
    kihon_event_bear: bool = False
    kihon_anchor_bar: int = bar_index

    __switch__ = kihon_anchor
    if __switch__ == KihonAnchor.signals:
        kihon_event_bull = regime_flip_bull
        kihon_event_bear = regime_flip_bear
    elif __switch__ == KihonAnchor.tk_cross:
        kihon_event_bull = tk_cross_event and tk_cross_dir == 1
        kihon_event_bear = tk_cross_event and tk_cross_dir == -1
    elif __switch__ == KihonAnchor.kj_cross:
        kihon_event_bull = kj_cross_event and kj_cross_dir == 1
        kihon_event_bear = kj_cross_event and kj_cross_dir == -1
    elif __switch__ == KihonAnchor.tk_kj_cross:
        kihon_event_bull = tk_kj_cross_event and tk_kj_cross_dir == 1
        kihon_event_bear = tk_kj_cross_event and tk_kj_cross_dir == -1
    elif __switch__ == KihonAnchor.kumo_change:
        kihon_event_bull = kumo_change_event and kumo_change_dir == 1
        kihon_event_bear = kumo_change_event and kumo_change_dir == -1
    elif __switch__ == KihonAnchor.swing_high:
        kihon_event_bear = swing_enabled and (not na(swing_ph))
        kihon_anchor_bar = bar_index - swing_length
    elif __switch__ == KihonAnchor.swing_low:
        kihon_event_bull = swing_enabled and (not na(swing_pl))
        kihon_anchor_bar = bar_index - swing_length
    elif __switch__ == KihonAnchor.swings:
        kihon_event_bull = swing_enabled and (not na(swing_pl))
        kihon_event_bear = swing_enabled and (not na(swing_ph))
        kihon_anchor_bar = bar_index - swing_length
    elif __switch__ == KihonAnchor.wave:
        kihon_event_bull = wave_completed and wave_dir == 1
        kihon_event_bear = wave_completed and wave_dir == -1
        if swing_enabled and array.size(swing_points) > 0:
            kihon_anchor_bar = array.last(swing_points).bar_idx

    if kihon_event_bull:
        array.unshift(kihon_flip_bars, kihon_anchor_bar)
        array.unshift(kihon_flip_dirs, 1)
    if kihon_event_bear:
        array.unshift(kihon_flip_bars, kihon_anchor_bar)
        array.unshift(kihon_flip_dirs, -1)
    while array.size(kihon_flip_bars) > kihon_history:
        array.pop(kihon_flip_bars)
        array.pop(kihon_flip_dirs)

    kihon_lines: Persistent[list[Line]] = array.new_line()
    kihon_labels: Persistent[list[Label]] = array.new_label()

    def kihon_clear():
        if array.size(kihon_lines) > 0:
            for i in pine_range(array.size(kihon_lines) - 1, 0):
                method_call('delete', array.get(kihon_lines, i))
            array.clear(kihon_lines)
        __block_result_35__ = na
        if array.size(kihon_labels) > 0:
            for i in pine_range(array.size(kihon_labels) - 1, 0):
                method_call('delete', array.get(kihon_labels, i))
            __block_result_35__ = array.clear(kihon_labels)
        return __block_result_35__

    taito_lines: Persistent[list[Line]] = array.new_line()
    taito_labels: Persistent[list[Label]] = array.new_label()

    def taito_clear():
        if array.size(taito_lines) > 0:
            for i in pine_range(array.size(taito_lines) - 1, 0):
                method_call('delete', array.get(taito_lines, i))
            array.clear(taito_lines)
        __block_result_36__ = na
        if array.size(taito_labels) > 0:
            for i in pine_range(array.size(taito_labels) - 1, 0):
                method_call('delete', array.get(taito_labels, i))
            __block_result_36__ = array.clear(taito_labels)
        return __block_result_36__

    time_range_hi = ta.highest(high, 300)
    time_range_lo = ta.lowest(low, 300)

    time_line_top = time_range_hi + atr_14 * 1.5
    time_line_bot = time_range_lo - atr_14 * 1.5

    kihon_window_active: bool = False
    taito_window_active: bool = False

    if kihon_enabled and array.size(kihon_flip_bars) > 0:
        kihon_all_cycles: list[int] = array.from_items(9, 17, 26)
        if kihon_range == CycleRange.extended or kihon_range == CycleRange.full:
            array.push(kihon_all_cycles, 33)
            array.push(kihon_all_cycles, 42)
            array.push(kihon_all_cycles, 51)
        if kihon_range == CycleRange.full:
            array.push(kihon_all_cycles, 65)
            array.push(kihon_all_cycles, 76)
            array.push(kihon_all_cycles, 129)
            array.push(kihon_all_cycles, 172)
            array.push(kihon_all_cycles, 200)
            array.push(kihon_all_cycles, 257)
        for a in pine_range(0, array.size(kihon_flip_bars) - 1):
            if kihon_window_active:
                break
            fb = array.get(kihon_flip_bars, a)
            for c in pine_range(0, array.size(kihon_all_cycles) - 1):
                if math.abs(bar_index - (fb + array.get(kihon_all_cycles, c))) <= 1:
                    kihon_window_active = True
                    break

    if swing_enabled and taito_enabled and (array.size(swing_points) >= 2):
        taito_sz = array.size(swing_points)
        taito_pairs = math.min(taito_count, taito_sz - 1)
        for p in pine_range(0, taito_pairs - 1):
            if taito_window_active:
                break
            t_idxB = taito_sz - 1 - p
            t_idxA = t_idxB - 1
            if t_idxA >= 0:
                t_dur = array.get(swing_points, t_idxB).bar_idx - array.get(swing_points, t_idxA).bar_idx
                if t_dur > 0:
                    for m in pine_range(1, taito_harmonics):
                        t_target = array.get(swing_points, t_idxB).bar_idx + t_dur * m
                        if math.abs(bar_index - t_target) <= 1:
                            taito_window_active = True
                            break

    txp_boxes: Persistent[list[Box]] = array.new_box()
    txp_labels: Persistent[list[Label]] = array.new_label()

    def txp_clear():
        for b in txp_boxes:
            box.delete(b)
        array.clear(txp_boxes)
        for l in txp_labels:
            label.delete(l)
        return array.clear(txp_labels)

    txp_time_window: bool = kihon_window_active or taito_window_active

    txp_has_targets: bool = not na(pt_alert_V) and (price_t_show_V and (not pt_reached_V) or (price_t_show_N and (not pt_reached_N)) or (price_t_show_E and (not pt_reached_E)) or (price_t_show_NT and (not pt_reached_NT)) or (price_t_show_2E and (not pt_reached_2E)) or (price_t_show_3E and (not pt_reached_3E)))

    txp_hit_V: bool = price_t_show_V and pt_reached_V and (not pt_reached_V[1])
    txp_hit_N: bool = price_t_show_N and pt_reached_N and (not pt_reached_N[1])
    txp_hit_E: bool = price_t_show_E and pt_reached_E and (not pt_reached_E[1])
    txp_hit_NT: bool = price_t_show_NT and pt_reached_NT and (not pt_reached_NT[1])
    txp_hit_2E: bool = price_t_show_2E and pt_reached_2E and (not pt_reached_2E[1])
    txp_hit_3E: bool = price_t_show_3E and pt_reached_3E and (not pt_reached_3E[1])

    txp_any_hit: bool = txp_hit_V or txp_hit_N or txp_hit_E or txp_hit_NT or txp_hit_2E or txp_hit_3E

    txp_confirmed: bool = txp_enabled and txp_time_window and txp_any_hit
    txp_confirmed_bull: bool = txp_confirmed and pt_alert_bias == 1
    txp_confirmed_bear: bool = txp_confirmed and pt_alert_bias == -1

    txp_window_alert: bool = txp_enabled and txp_time_window and txp_has_targets and (not txp_confirmed)

    if txp_confirmed:
        txp_hit_names: list[str] = array.new_string()
        txp_hit_levels: list[float] = array.new_float()
        if txp_hit_V:
            array.push(txp_hit_names, 'V @ ' + string.tostring(pt_alert_V, format.mintick))
            array.push(txp_hit_levels, pt_alert_V)
        if txp_hit_N:
            array.push(txp_hit_names, 'N @ ' + string.tostring(pt_alert_N, format.mintick))
            array.push(txp_hit_levels, pt_alert_N)
        if txp_hit_E:
            array.push(txp_hit_names, 'E @ ' + string.tostring(pt_alert_E, format.mintick))
            array.push(txp_hit_levels, pt_alert_E)
        if txp_hit_NT:
            array.push(txp_hit_names, 'NT @ ' + string.tostring(pt_alert_NT, format.mintick))
            array.push(txp_hit_levels, pt_alert_NT)
        if txp_hit_2E:
            array.push(txp_hit_names, '2E @ ' + string.tostring(pt_alert_2E, format.mintick))
            array.push(txp_hit_levels, pt_alert_2E)
        if txp_hit_3E:
            array.push(txp_hit_names, '3E @ ' + string.tostring(pt_alert_3E, format.mintick))
            array.push(txp_hit_levels, pt_alert_3E)

        txp_hit_text: str = ""
        for i in pine_range(0, array.size(txp_hit_names) - 1):
            txp_hit_text += '  • ' + array.get(txp_hit_names, i)
            if i < array.size(txp_hit_names) - 1:
                txp_hit_text += "\n"

        txp_dia_level: float = na(float)
        txp_dia_dist: float = 10000000000.0
        for i in pine_range(0, array.size(txp_hit_levels) - 1):
            d = math.abs(close - array.get(txp_hit_levels, i))
            if d < txp_dia_dist:
                txp_dia_dist = d
                txp_dia_level = array.get(txp_hit_levels, i)

        txp_at_kumo: bool = False
        if txp_kumo_enhance and (not na(txp_dia_level)):
            txp_k_hi = math.max(senkou_a_present, senkou_b_present)
            txp_k_lo = math.min(senkou_a_present, senkou_b_present)
            txp_at_kumo = txp_dia_level >= txp_k_lo - 0.5 * atr_14 and txp_dia_level <= txp_k_hi + 0.5 * atr_14

        txp_dia_clr = txp_kumo_color if txp_at_kumo else txp_color
        txp_dia_sz = size.small if txp_at_kumo else size.tiny
        txp_timing = 'Kihon Sūchi' if kihon_window_active else 'Taito Sūchi'
        txp_kumo_ln: str = '\n\n☁ KUMO: Target near cloud edge\n   └─ Triple confluence (TxPxK)' if txp_at_kumo else ''

        txp_anchor_ln: str = ""
        if kihon_window_active and kihon_enabled:
            txp_anc_aligned: bool = False
            txp_anc_mode: str = ""
            __switch_2__ = kihon_anchor
            if __switch_2__ == KihonAnchor.signals:
                txp_anc_mode = "Signals"
                txp_anc_aligned = pt_alert_bias == 1 and regime == 1 or (pt_alert_bias == -1 and regime == -1)
            elif __switch_2__ == KihonAnchor.tk_cross:
                txp_anc_mode = "TK Cross"
                txp_anc_aligned = pt_alert_bias == 1 and close > tenkansen or (pt_alert_bias == -1 and close < tenkansen)
            elif __switch_2__ == KihonAnchor.kj_cross:
                txp_anc_mode = "KJ Cross"
                txp_anc_aligned = pt_alert_bias == 1 and close > kijunsen or (pt_alert_bias == -1 and close < kijunsen)
            elif __switch_2__ == KihonAnchor.tk_kj_cross:
                txp_anc_mode = "TKxKJ Cross"
                txp_anc_aligned = pt_alert_bias == 1 and tenkansen > kijunsen or (pt_alert_bias == -1 and tenkansen < kijunsen)
            elif __switch_2__ == KihonAnchor.kumo_change:
                txp_anc_mode = "Kumo Change"
                txp_anc_aligned = pt_alert_bias == 1 and senkoua > senkoub or (pt_alert_bias == -1 and senkoua < senkoub)
            elif __switch_2__ == KihonAnchor.swing_high:
                txp_anc_mode = "Swing High"
                if swing_enabled and array.size(swing_points) > 0:
                    txp_anc_aligned = close < array.last(swing_points).price
            elif __switch_2__ == KihonAnchor.swing_low:
                txp_anc_mode = "Swing Low"
                if swing_enabled and array.size(swing_points) > 0:
                    txp_anc_aligned = close > array.last(swing_points).price
            elif __switch_2__ == KihonAnchor.swings:
                txp_anc_mode = "Swings"
                if swing_enabled and array.size(swing_points) > 0:
                    last_sw = array.last(swing_points)
                    txp_anc_aligned = pt_alert_bias == 1 and last_sw.dir == -1 and (close > last_sw.price) or (pt_alert_bias == -1 and last_sw.dir == 1 and (close < last_sw.price))
            elif __switch_2__ == KihonAnchor.wave:
                txp_anc_mode = "Wave"

                txp_anc_aligned = True
            txp_anc_status = 'Aligned ✓' if txp_anc_aligned else 'Diverging ✗'
            txp_anchor_ln = string.format('\n\nANCHOR: {0} — {1}', txp_anc_mode, txp_anc_status)
        elif taito_window_active and (not kihon_window_active):
            txp_anchor_ln = "\n\nANCHOR: Taito Sūchi — Time symmetry"

        txp_dia_tip = string.format('TIME x PRICE CONFLUENCE — CONFIRMED ◆\n' + '時間・値幅合流\n\n' + 'TARGET(S) REACHED:\n{0}\n\n' + 'TIMING: {1} window (±1 bar){2}{3}', txp_hit_text, txp_timing, txp_kumo_ln, txp_anchor_ln)

        txp_dia_y = low - atr_offset * 1.8 if txp_confirmed_bull else high + atr_offset * 1.8
        txp_dia_style = label.style_label_up if txp_confirmed_bull else label.style_label_down

        label.new(bar_index, txp_dia_y, '◆', style=txp_dia_style, color=txp_dia_clr, textcolor=chart.fg_color, size=txp_dia_sz, tooltip=txp_dia_tip)

    if barstate.islast and kihon_enabled and (array.size(kihon_flip_bars) > 0):
        kihon_clear()

        cycles: list[int] = array.from_items(9, 17, 26)
        if kihon_range == CycleRange.extended or kihon_range == CycleRange.full:
            array.push(cycles, 33)
            array.push(cycles, 42)
            array.push(cycles, 51)
        if kihon_range == CycleRange.full:
            array.push(cycles, 65)
            array.push(cycles, 76)
            array.push(cycles, 129)
            array.push(cycles, 172)
            array.push(cycles, 200)
            array.push(cycles, 257)

        max_future_bar = bar_index + 50

        tgt_bars: list[int] = array.new_int()
        tgt_cycles: list[int] = array.new_int()
        tgt_anchors: list[int] = array.new_int()

        num_anchors = array.size(kihon_flip_bars)
        for a in pine_range(0, num_anchors - 1):
            fb = array.get(kihon_flip_bars, a)
            for c in pine_range(0, array.size(cycles) - 1):
                n = array.get(cycles, c)
                tb = fb + n
                if tb > max_future_bar:
                    continue
                array.push(tgt_bars, tb)
                array.push(tgt_cycles, n)
                array.push(tgt_anchors, a)

        total = array.size(tgt_bars)

        tgt_is_conf: list[bool] = array.new_bool(total, False)
        tgt_skip: list[bool] = array.new_bool(total, False)

        if total > 1:
            for i in pine_range(0, total - 2):
                if not array.get(tgt_skip, i):
                    for j in pine_range(i + 1, total - 1):
                        if not array.get(tgt_skip, j) and array.get(tgt_anchors, i) != array.get(tgt_anchors, j):
                            if math.abs(array.get(tgt_bars, i) - array.get(tgt_bars, j)) <= 1:
                                array.set(tgt_is_conf, i, True)
                                array.set(tgt_skip, j, True)

        next_found: bool = False
        confluence_clr: Color = color.new('#FFD700')

        if total > 0:
            for i in pine_range(0, total - 1):
                if array.get(tgt_skip, i):
                    continue

                tb = array.get(tgt_bars, i)
                bars_away = tb - bar_index
                if math.abs(bars_away) > 4999:
                    continue
                anchor_idx = array.get(tgt_anchors, i)
                is_conf = array.get(tgt_is_conf, i)
                flip_dir = array.get(kihon_flip_dirs, anchor_idx)

                is_past = bars_away < -1
                is_window = math.abs(bars_away) <= 1
                is_future = bars_away > 1
                is_next: bool = False
                if is_future and (not next_found):
                    is_next = True
                    next_found = True

                validated: bool = False
                if is_past and swing_enabled and (array.size(swing_points) > 0):
                    for sp_i in pine_range(array.size(swing_points) - 1, 0):
                        if math.abs(array.get(swing_points, sp_i).bar_idx - tb) <= 1:
                            validated = True
                            break
                        if array.get(swing_points, sp_i).bar_idx < tb - 1:
                            break

                age_alpha: int = anchor_idx * 15
                base_alpha: int = 0
                if is_conf:
                    base_alpha = 5
                elif is_window:
                    base_alpha = 10 + age_alpha
                elif is_next:
                    base_alpha = 25 + age_alpha
                elif is_future:
                    base_alpha = 50 + age_alpha
                else:
                    base_alpha = 35 + age_alpha if validated else 65 + age_alpha
                base_alpha = math.min(base_alpha, 85)

                line_w: int = 2 if is_conf else 2 if is_window else 1

                line_clr: Color = na(Color)
                if is_conf:
                    line_clr = color.new(confluence_clr, base_alpha)
                elif is_window:
                    line_clr = color.new(bull_event_color if flip_dir == 1 else bear_event_color, base_alpha)
                else:
                    line_clr = color.new(kihon_color, base_alpha)

                l = line.new(tb, time_line_bot, tb, time_line_top, xloc=xloc.bar_index, color=line_clr, width=line_w, style=line.style_dashed if is_conf or is_window or is_next else line.style_dotted)
                array.push(kihon_lines, l)

                badge_text: str = na(str)
                if is_conf:
                    conf_nums = string.tostring(array.get(tgt_cycles, i))
                    if i < total - 1:
                        for j in pine_range(i + 1, total - 1):
                            if array.get(tgt_skip, j) and math.abs(array.get(tgt_bars, j) - tb) <= 1:
                                conf_nums += string.format('+{0}', array.get(tgt_cycles, j))
                    badge_text = conf_nums
                else:
                    arrow = '▲' if flip_dir == 1 else '▼'
                    badge_text = string.format('{0} {1}', arrow, array.get(tgt_cycles, i))

                if is_past:
                    badge_text += ' ✓' if validated else ' ·'

                badge_bg: Color = na(Color)
                badge_fg: Color = na(Color)
                if is_conf:
                    badge_bg = color.new(confluence_clr, math.max(base_alpha - 10, 0))
                    badge_fg = color.new(color.new('#000000'), 0)
                elif is_window:
                    badge_bg = bull_event_color if flip_dir == 1 else bear_event_color
                    badge_fg = color.white
                else:
                    badge_bg = color.new(kihon_color, math.max(base_alpha - 10, 0))
                    badge_fg = color.new(chart.fg_color, base_alpha)

                dir_text = '▲ Bull' if flip_dir == 1 else '▼ Bear'
                status = 'Time confluence — multiple cycles converge' if is_conf else 'Reversal window active' if is_window else 'Current bar' if bars_away == 0 else string.format('Due in {0} bars from current bar', bars_away) if is_future else string.format('Occurred {0} bars back from current bar', math.abs(bars_away))

                valid_line = ('\nPrice swing detected ✓' if validated else '\nNo significant swing ·') if is_past else ''

                __block_result_37__ = na
                __switch_3__ = kihon_anchor
                if __switch_3__ == KihonAnchor.signals:
                    __block_result_37__ = "Signal"
                elif __switch_3__ == KihonAnchor.tk_cross:
                    __block_result_37__ = "TK Cross"
                elif __switch_3__ == KihonAnchor.kj_cross:
                    __block_result_37__ = "KJ Cross"
                elif __switch_3__ == KihonAnchor.tk_kj_cross:
                    __block_result_37__ = "TKxKJ Cross"
                elif __switch_3__ == KihonAnchor.kumo_change:
                    __block_result_37__ = "Kumo Change"
                elif __switch_3__ == KihonAnchor.swing_high:
                    __block_result_37__ = "Swing High"
                elif __switch_3__ == KihonAnchor.swing_low:
                    __block_result_37__ = "Swing Low"
                elif __switch_3__ == KihonAnchor.swings:
                    __block_result_37__ = "Swing"
                elif __switch_3__ == KihonAnchor.wave:
                    __block_result_37__ = "Wave"
                anchor_mode_text = __block_result_37__

                anchor_label = string.format('Anchor: {0} {1} #{2}\n', dir_text, anchor_mode_text, anchor_idx + 1) if num_anchors > 1 else ''

                tip = string.format('Kihon Sūchi {0}{1}\nKihon Sūchi — Time Cycle\n\n{2}{3}{4}', array.get(tgt_cycles, i), ' (confluence)' if is_conf else '', anchor_label, status, valid_line)

                lbl = label.new(tb, time_line_top, badge_text, xloc=xloc.bar_index, style=label.style_label_down, color=badge_bg, textcolor=badge_fg, size=size.small if is_conf or is_window else size.tiny, tooltip=tip)
                array.push(kihon_labels, lbl)

        for a in pine_range(0, array.size(kihon_flip_bars) - 1):
            fb = array.get(kihon_flip_bars, a)
            if bar_index - fb > 4999:
                continue
            fd = array.get(kihon_flip_dirs, a)
            a_arrow = '▲' if fd == 1 else '▼'
            a_clr = bull_event_color if fd == 1 else bear_event_color
            a_alpha = a * 20
            __block_result_38__ = na
            __switch_2__ = kihon_anchor
            if __switch_2__ == KihonAnchor.signals:
                __block_result_38__ = "Signal"
            elif __switch_2__ == KihonAnchor.tk_cross:
                __block_result_38__ = "TK Cross"
            elif __switch_2__ == KihonAnchor.kj_cross:
                __block_result_38__ = "KJ Cross"
            elif __switch_2__ == KihonAnchor.tk_kj_cross:
                __block_result_38__ = "TKxKJ Cross"
            elif __switch_2__ == KihonAnchor.kumo_change:
                __block_result_38__ = "Kumo Change"
            elif __switch_2__ == KihonAnchor.swing_high:
                __block_result_38__ = "Swing High"
            elif __switch_2__ == KihonAnchor.swing_low:
                __block_result_38__ = "Swing Low"
            elif __switch_2__ == KihonAnchor.swings:
                __block_result_38__ = "Swing"
            elif __switch_2__ == KihonAnchor.wave:
                __block_result_38__ = "Wave"
            a_mode = __block_result_38__
            a_tip = string.format('{0} {1} (#{2})\nKihon Sūchi anchor point', a_mode, a_arrow, a + 1)
            a_lbl = label.new(fb, time_line_bot, a_arrow, xloc=xloc.bar_index, style=label.style_label_up, color=color.new(a_clr, a_alpha), textcolor=color.white, size=size.tiny, tooltip=a_tip)
            array.push(kihon_labels, a_lbl)
    elif barstate.islast and kihon_enabled:
        kihon_clear()

    if barstate.islast and swing_enabled and taito_enabled and (array.size(swing_points) >= 2):
        taito_clear()

        sz = array.size(swing_points)
        pairs_to_show = math.min(taito_count, sz - 1)

        max_future_bar = bar_index + 50

        for p in pine_range(0, pairs_to_show - 1):
            idx_B = sz - 1 - p
            idx_A = idx_B - 1
            if idx_A < 0:
                continue

            ptA: SwingPoint = array.get(swing_points, idx_A)
            ptB: SwingPoint = array.get(swing_points, idx_B)

            duration = ptB.bar_idx - ptA.bar_idx
            if duration <= 0:
                continue

            bracket_y = time_line_bot
            pair_fade = p * 15
            bracket_alpha = math.min(45 + pair_fade, 90)
            bracket_clr = color.new(taito_color, bracket_alpha)

            if bar_index - ptA.bar_idx <= 4999:
                array.push(taito_lines, line.new(ptA.bar_idx, bracket_y, ptB.bar_idx, bracket_y, xloc=xloc.bar_index, color=bracket_clr, width=1, style=line.style_solid))

            for m in pine_range(1, taito_harmonics):
                target_bar = ptB.bar_idx + duration * m

                if target_bar > max_future_bar:
                    continue

                if math.abs(target_bar - bar_index) > 4999:
                    continue

                bars_away = target_bar - bar_index

                is_past = bars_away < -1
                is_window = math.abs(bars_away) <= 1
                is_future = bars_away > 1

                validated: bool = False
                if is_past and array.size(swing_points) > 0:
                    for sp_i in pine_range(array.size(swing_points) - 1, 0):
                        if math.abs(array.get(swing_points, sp_i).bar_idx - target_bar) <= 1:
                            validated = True
                            break
                        if array.get(swing_points, sp_i).bar_idx < target_bar - 1:
                            break

                harmonic_fade: int = (m - 1) * 10
                base_alpha: int = 0
                if is_window:
                    base_alpha = 10 + pair_fade + harmonic_fade
                elif is_future:
                    base_alpha = 30 + pair_fade + harmonic_fade
                else:
                    base_alpha = 30 + pair_fade + harmonic_fade if validated else 60 + pair_fade + harmonic_fade
                base_alpha = math.min(base_alpha, 85)

                line_w = 2 if is_window else 1
                line_style = line.style_dashed if is_window else line.style_dashed if is_future else line.style_dotted
                line_clr = color.new(taito_color, base_alpha)

                array.push(taito_lines, line.new(target_bar, time_line_bot, target_bar, time_line_top, xloc=xloc.bar_index, color=line_clr, width=line_w, style=line_style))

                if bar_index - ptB.bar_idx <= 4999:
                    array.push(taito_lines, line.new(ptB.bar_idx, bracket_y, target_bar, bracket_y, xloc=xloc.bar_index, color=color.new(taito_color, bracket_alpha + harmonic_fade), width=1, style=line.style_dotted))

                harmonic_suffix = string.format(' x{0}', m) if m > 1 else ''
                badge_text = string.format('T={0}{1}', duration, harmonic_suffix)
                if is_past:
                    badge_text += ' ✓' if validated else ' ·'

                badge_bg = color.new(taito_color, math.max(base_alpha - 10, 0))
                badge_fg = color.white if is_window else color.new(chart.fg_color, base_alpha)

                dir_A = 'High' if ptA.dir == 1 else 'Low'
                dir_B = 'High' if ptB.dir == 1 else 'Low'
                harmonic_info = string.format(' (x{0} harmonic)', m) if m > 1 else ''
                projected_bars = string.tostring(duration * m)
                status = 'Time symmetry window active' if is_window else 'Current bar' if bars_away == 0 else string.format('Due in {0} bars', bars_away) if is_future else string.format('Occurred {0} bars ago', math.abs(bars_away))
                valid_line = ('\nPrice swing detected ✓' if validated else '\nNo significant swing ·') if is_past else ''

                tip = string.format('Taito Sūchi T={0}{1}\nTaito Sūchi — Time Symmetry\n\nMeasured: Swing {2} → {3} = {0} bars\nProjected: {4} bars forward from {3}\n\n{5}{6}', duration, harmonic_info, dir_A, dir_B, projected_bars, status, valid_line)

                array.push(taito_labels, label.new(target_bar, time_line_top, badge_text, xloc=xloc.bar_index, style=label.style_label_down, color=badge_bg, textcolor=badge_fg, size=size.small if is_window else size.tiny, tooltip=tip))
    elif barstate.islast and taito_enabled:
        taito_clear()

    if barstate.islast and txp_enabled and txp_show_forecast:
        txp_clear()

        txp_tbars: list[int] = array.new_int()
        txp_tsrcs: list[str] = array.new_string()
        txp_tweights: list[int] = array.new_int()
        txp_max_bar = bar_index + 50

        if kihon_enabled and array.size(kihon_flip_bars) > 0:
            txp_cycles: list[int] = array.from_items(9, 17, 26)
            txp_cweights: list[int] = array.from_items(1, 2, 3)
            if kihon_range == CycleRange.extended or kihon_range == CycleRange.full:
                array.push(txp_cycles, 33)
                array.push(txp_cweights, 2)
                array.push(txp_cycles, 42)
                array.push(txp_cweights, 3)
                array.push(txp_cycles, 51)
                array.push(txp_cweights, 2)
            if kihon_range == CycleRange.full:
                array.push(txp_cycles, 65)
                array.push(txp_cweights, 2)
                array.push(txp_cycles, 76)
                array.push(txp_cweights, 3)
                array.push(txp_cycles, 129)
                array.push(txp_cweights, 3)
                array.push(txp_cycles, 172)
                array.push(txp_cweights, 2)
                array.push(txp_cycles, 200)
                array.push(txp_cweights, 2)
                array.push(txp_cycles, 257)
                array.push(txp_cweights, 2)

            for a in pine_range(0, array.size(kihon_flip_bars) - 1):
                fb = array.get(kihon_flip_bars, a)
                for c in pine_range(0, array.size(txp_cycles) - 1):
                    n = array.get(txp_cycles, c)
                    tb = fb + n
                    if tb >= bar_index - 1 and tb <= txp_max_bar:
                        a_sfx = string.format('.{0}', a + 1) if a > 0 else ''
                        array.push(txp_tbars, tb)
                        array.push(txp_tsrcs, string.format('K{0}{1}', n, a_sfx))
                        array.push(txp_tweights, array.get(txp_cweights, c))

        if swing_enabled and taito_enabled and (array.size(swing_points) >= 2):
            t_sz = array.size(swing_points)
            t_pairs = math.min(taito_count, t_sz - 1)
            for p in pine_range(0, t_pairs - 1):
                t_B = t_sz - 1 - p
                t_A = t_B - 1
                if t_A >= 0:
                    t_dur = array.get(swing_points, t_B).bar_idx - array.get(swing_points, t_A).bar_idx
                    if t_dur > 0:
                        for m in pine_range(1, taito_harmonics):
                            tb = array.get(swing_points, t_B).bar_idx + t_dur * m
                            if tb >= bar_index - 1 and tb <= txp_max_bar:
                                array.push(txp_tbars, tb)

                                array.push(txp_tsrcs, string.format('T{0}p{1}', t_dur * m, p))
                                array.push(txp_tweights, 2 if m == 1 else 1)

        txp_plevels: list[float] = array.new_float()
        txp_pnames: list[str] = array.new_string()

        if not na(pt_alert_V):
            if price_t_show_V and (not pt_reached_V):
                array.push(txp_plevels, pt_alert_V)
                array.push(txp_pnames, 'V')
            if price_t_show_N and (not pt_reached_N):
                array.push(txp_plevels, pt_alert_N)
                array.push(txp_pnames, 'N')
            if price_t_show_E and (not pt_reached_E):
                array.push(txp_plevels, pt_alert_E)
                array.push(txp_pnames, 'E')
            if price_t_show_NT and (not pt_reached_NT):
                array.push(txp_plevels, pt_alert_NT)
                array.push(txp_pnames, 'NT')
            if price_t_show_2E and (not pt_reached_2E):
                array.push(txp_plevels, pt_alert_2E)
                array.push(txp_pnames, '2E')
            if price_t_show_3E and (not pt_reached_3E):
                array.push(txp_plevels, pt_alert_3E)
                array.push(txp_pnames, '3E')

        txp_r_bars: list[int] = array.new_int()
        txp_r_levels: list[float] = array.new_float()
        txp_r_tsrc: list[str] = array.new_string()
        txp_r_psrc: list[str] = array.new_string()
        txp_r_tweight: list[int] = array.new_int()

        if array.size(txp_tbars) > 0 and array.size(txp_plevels) > 0:
            for t in pine_range(0, array.size(txp_tbars) - 1):
                for p in pine_range(0, array.size(txp_plevels) - 1):
                    array.push(txp_r_bars, array.get(txp_tbars, t))
                    array.push(txp_r_levels, array.get(txp_plevels, p))
                    array.push(txp_r_tsrc, array.get(txp_tsrcs, t))
                    array.push(txp_r_psrc, array.get(txp_pnames, p))
                    array.push(txp_r_tweight, array.get(txp_tweights, t))

        txp_cl_bar: list[int] = array.new_int()
        txp_cl_level: list[float] = array.new_float()
        txp_cl_count: list[int] = array.new_int()
        txp_cl_nt: list[int] = array.new_int()
        txp_cl_np: list[int] = array.new_int()
        txp_cl_tt: list[str] = array.new_string()
        txp_cl_pt: list[str] = array.new_string()
        txp_cl_kumo: list[bool] = array.new_bool()

        __loop_1__ = pine_loop(0)
        while __loop_1__.step(math.max(array.size(txp_r_bars) - 1, 0)):
            i = __loop_1__.value
            if i >= array.size(txp_r_bars):
                break
            r_bar = array.get(txp_r_bars, i)
            r_lvl = array.get(txp_r_levels, i)
            r_ts: str = array.get(txp_r_tsrc, i)
            r_ps: str = array.get(txp_r_psrc, i)
            r_tw = array.get(txp_r_tweight, i)

            merged: bool = False
            __loop_2__ = pine_loop(0)
            while __loop_2__.step(math.max(array.size(txp_cl_bar) - 1, 0)):
                c = __loop_2__.value
                if c >= array.size(txp_cl_bar):
                    break
                if math.abs(r_bar - array.get(txp_cl_bar, c)) <= 2 and math.abs(r_lvl - array.get(txp_cl_level, c)) <= txp_tolerance * atr_14:
                    cnt = array.get(txp_cl_count, c)
                    new_bar = cast_int(math.round((array.get(txp_cl_bar, c) * cnt + r_bar) / (cnt + 1.0)))
                    new_lvl = (array.get(txp_cl_level, c) * cnt + r_lvl) / (cnt + 1)
                    array.set(txp_cl_bar, c, new_bar)
                    array.set(txp_cl_level, c, new_lvl)
                    array.set(txp_cl_count, c, cnt + 1)

                    if not string.contains(array.get(txp_cl_tt, c), '|' + r_ts + '|'):
                        array.set(txp_cl_tt, c, array.get(txp_cl_tt, c) + r_ts + '|')
                        array.set(txp_cl_nt, c, array.get(txp_cl_nt, c) + r_tw)

                    if not string.contains(array.get(txp_cl_pt, c), '|' + r_ps + '|'):
                        array.set(txp_cl_pt, c, array.get(txp_cl_pt, c) + r_ps + '|')
                        array.set(txp_cl_np, c, array.get(txp_cl_np, c) + 1)
                    merged = True
                    break

            if not merged:
                array.push(txp_cl_bar, r_bar)
                array.push(txp_cl_level, r_lvl)
                array.push(txp_cl_count, 1)
                array.push(txp_cl_nt, r_tw)
                array.push(txp_cl_np, 1)
                array.push(txp_cl_tt, '|' + r_ts + '|')
                array.push(txp_cl_pt, '|' + r_ps + '|')
                array.push(txp_cl_kumo, False)

        txp_kumo_hi = math.max(senkoua, senkoub)
        txp_kumo_lo = math.min(senkoua, senkoub)

        txp_cl_score: list[int] = array.new_int()
        __loop_1__ = pine_loop(0)
        while __loop_1__.step(math.max(array.size(txp_cl_bar) - 1, 0)):
            c = __loop_1__.value
            if c >= array.size(txp_cl_bar):
                break
            cl_lvl = array.get(txp_cl_level, c)
            near_k = txp_kumo_enhance and cl_lvl >= txp_kumo_lo - 0.5 * atr_14 and (cl_lvl <= txp_kumo_hi + 0.5 * atr_14)
            array.set(txp_cl_kumo, c, near_k)

            array.push(txp_cl_score, math.min(array.get(txp_cl_nt, c), 8) + array.get(txp_cl_np, c) + (1 if near_k else 0))

        __loop_1__ = pine_loop(0)
        while __loop_1__.step(math.max(array.size(txp_cl_bar) - 1, 0)):
            c = __loop_1__.value
            if c >= array.size(txp_cl_bar):
                break
            score = array.get(txp_cl_score, c)
            if score < 4:
                continue

            cl_bar = array.get(txp_cl_bar, c)
            if math.abs(cl_bar - bar_index) > 4999:
                continue
            cl_lvl = array.get(txp_cl_level, c)
            cl_kumo = array.get(txp_cl_kumo, c)

            cl_tt_raw: str = array.get(txp_cl_tt, c)
            cl_pt_raw: str = array.get(txp_cl_pt, c)
            cl_tt = string.replace_all(string.substring(cl_tt_raw, 1, string.length(cl_tt_raw) - 1), '|', '+')
            cl_pt = string.replace_all(string.substring(cl_pt_raw, 1, string.length(cl_pt_raw) - 1), '|', '+')

            cl_tt = string.replace_all(string.replace_all(string.replace_all(string.replace_all(string.replace_all(cl_tt, 'p0', ''), 'p1', ''), 'p2', ''), 'p3', ''), 'p4', '')

            fill_a = math.max(92 - score * 6, 50)

            border_a = math.max(70 - score * 10, 20)
            border_w = 2 if score >= 5 else 1
            base_clr = txp_kumo_color if cl_kumo or score >= 5 else txp_color

            half_h = txp_tolerance * atr_14
            bars_away = cl_bar - bar_index

            array.push(txp_boxes, box.new(cl_bar - 2, cl_lvl + half_h, cl_bar + 2, cl_lvl - half_h, xloc=xloc.bar_index, bgcolor=color.new(base_clr, fill_a), border_color=color.new(chart.fg_color, border_a), border_width=border_w, text=string.tostring(score), text_color=chart.fg_color, text_size=size.small if score >= 5 else size.tiny, text_halign=text.align_center, text_valign=text.align_center))

            bias_txt = 'Bullish' if pt_alert_bias == 1 else 'Bearish'
            kumo_txt: str = '\n\n☁ KUMO: Zone intersects projected cloud\n   └─ Triple confluence (TxPxK)' if cl_kumo else ''

            price_detail: str = ""
            if string.contains(cl_pt_raw, '|V|'):
                price_detail += '\n  • V @ ' + string.tostring(pt_alert_V, format.mintick)
            if string.contains(cl_pt_raw, '|N|'):
                price_detail += '\n  • N @ ' + string.tostring(pt_alert_N, format.mintick)
            if string.contains(cl_pt_raw, '|E|'):
                price_detail += '\n  • E @ ' + string.tostring(pt_alert_E, format.mintick)
            if string.contains(cl_pt_raw, '|NT|'):
                price_detail += '\n  • NT @ ' + string.tostring(pt_alert_NT, format.mintick)
            if string.contains(cl_pt_raw, '|2E|'):
                price_detail += '\n  • 2E @ ' + string.tostring(pt_alert_2E, format.mintick)
            if string.contains(cl_pt_raw, '|3E|'):
                price_detail += '\n  • 3E @ ' + string.tostring(pt_alert_3E, format.mintick)

            src_text = string.format('{0} x {1}{2}', cl_pt, cl_tt, ' ☁' if cl_kumo else '')

            cl_tip = string.format('Time x Price Confluence — Score [{0}]\n' + '{1}\n' + '時間・値幅合流 (Kasanari)\n\n' + 'PRICE CONVERGENCE: {2}{3}\n\n' + 'TIME CONVERGENCE: {4}\n\n' + 'Zone: ±2 bars around bar +{5} from current{6}', score, src_text, bias_txt, price_detail, cl_tt, bars_away, kumo_txt)

            array.push(txp_labels, label.new(cl_bar, cl_lvl, string.tostring(score), xloc=xloc.bar_index, style=label.style_label_center, color=color.new(chart.fg_color, 100), textcolor=color.new(chart.fg_color, 100), size=size.small if score >= 5 else size.tiny, tooltip=cl_tip))
    elif barstate.islast and txp_enabled:
        txp_clear()

    confluence_bull = (1 if close > kumo_top else 0) + (1 if tenkansen > kijunsen else 0) + (1 if close > tenkansen else 0) + (1 if chikou_above_past else 0) + (1 if chikou_filter_signal == 1 else 0)

    confluence_bear = (1 if close < kumo_bottom else 0) + (1 if tenkansen < kijunsen else 0) + (1 if close < tenkansen else 0) + (1 if chikou_below_past else 0) + (1 if chikou_filter_signal == -1 else 0)

    def calc_bar_color():
        __block_result_39__ = na
        __switch__ = barcolor_mode
        if __switch__ == BarColorMode.disabled:
            __block_result_39__ = NA(Color)
        elif __switch__ == BarColorMode.vs_tkkj:
            __block_result_39__ = bar_bull_color if close > tenkansen and close > kijunsen else bar_bear_color if close < tenkansen and close < kijunsen else bar_neutral_color
        elif __switch__ == BarColorMode.vs_kumo:
            __block_result_39__ = bar_bull_color if close > kumo_top else bar_bear_color if close < kumo_bottom else bar_neutral_color
        elif __switch__ == BarColorMode.confluence:
            __block_result_40__ = na
            if confluence_bull > confluence_bear:
                transparency = 80 - confluence_bull * 16
                __block_result_40__ = color.new(bar_bull_color, math.max(0, transparency))
            elif confluence_bear > confluence_bull:
                transparency = 80 - confluence_bear * 16
                __block_result_40__ = color.new(bar_bear_color, math.max(0, transparency))
            else:
                __block_result_40__ = bar_neutral_color
            __block_result_39__ = __block_result_40__
        elif __switch__ == BarColorMode.regime:
            __block_result_39__ = bar_bull_color if regime == 1 else bar_bear_color if regime == -1 else bar_neutral_color
        elif __switch__ == BarColorMode.kumo_bias:
            __block_result_39__ = bar_bull_color if senkoua > senkoub else bar_bear_color if senkoua < senkoub else bar_neutral_color
        else:
            __block_result_39__ = NA(Color)
        return __block_result_39__

    barcolor(calc_bar_color())

    if panel_enabled:
        t1: Persistent[Table] = table.new(parse_position(panel_position), 3, 15, bgcolor=panel_bg_color, border_width=1)

        if barstate.islast:
            table.clear(t1, 0, 0, 2, 14)

            panel_text_color: Color = chart.fg_color
            txt_size = parse_text_size(panel_text_size)
            header_bg = panel_header_color
            background = panel_bg_color

            if panel_lite_mode:
                row: int = 0

                table.cell(t1, 0, row, 'CROSS SIGNALS', text_color=color.white, text_size=txt_size, bgcolor=header_bg)
                table.cell(t1, 1, row, 'STATUS', text_color=color.white, text_size=txt_size, bgcolor=header_bg, text_halign=text.align_right)
                row += 1

                tk_signal = panel_tk_cross_score
                kj_signal = panel_kijun_score
                ch_signal = panel_chikou_score
                price_kumo = panel_price_kumo_score
                kumo_twist = panel_kumo_twist_score
                overall_signal = panel_consensus_score

                if panel_show_tk_cross:
                    table.cell(t1, 0, row, 'TK Cross vs Kumo', text_color=panel_text_color, text_size=txt_size, bgcolor=background)
                    table.cell(t1, 1, row, get_score_symbol(tk_signal), text_color=get_score_color(tk_signal), text_size=txt_size, bgcolor=background, text_halign=text.align_right)
                    row += 1
                if panel_show_kijun:
                    table.cell(t1, 0, row, 'Kijun Position', text_color=panel_text_color, text_size=txt_size, bgcolor=background)
                    table.cell(t1, 1, row, get_score_symbol(kj_signal), text_color=get_score_color(kj_signal), text_size=txt_size, bgcolor=background, text_halign=text.align_right)
                    row += 1
                if panel_show_chikou_confirm:
                    table.cell(t1, 0, row, 'Chikou Confirm', text_color=panel_text_color, text_size=txt_size, bgcolor=background)
                    table.cell(t1, 1, row, get_score_symbol(ch_signal), text_color=get_score_color(ch_signal), text_size=txt_size, bgcolor=background, text_halign=text.align_right)
                    row += 1
                if panel_show_price_kumo:
                    table.cell(t1, 0, row, 'Price vs Kumo', text_color=panel_text_color, text_size=txt_size, bgcolor=background)
                    table.cell(t1, 1, row, get_score_symbol(price_kumo), text_color=get_score_color(price_kumo), text_size=txt_size, bgcolor=background, text_halign=text.align_right)
                    row += 1
                if panel_show_kumo_twist:
                    table.cell(t1, 0, row, 'Kumo Twist', text_color=panel_text_color, text_size=txt_size, bgcolor=background)
                    table.cell(t1, 1, row, get_score_symbol(kumo_twist), text_color=get_score_color(kumo_twist), text_size=txt_size, bgcolor=background, text_halign=text.align_right)
                    row += 1
                table.cell(t1, 0, row, 'CONSENSUS', text_color=color.white, text_size=txt_size, bgcolor=header_bg)
                table.cell(t1, 1, row, get_score_symbol(overall_signal), text_color=get_score_color(overall_signal), text_size=txt_size, bgcolor=header_bg, text_halign=text.align_right)
                row += 1

                if panel_show_details:
                    table.cell(t1, 0, row, '─────', text_color=color.new(panel_text_color, 50), text_size=txt_size)
                    table.cell(t1, 1, row, 'DETAILS', text_color=color.new(panel_text_color, 50), text_size=txt_size, text_halign=text.align_right)
                    row += 1

                    is_bull_dir = get_composite_direction()
                    status_text, missing_text = get_composite_status(is_bull_dir)

                    lite_status: str = 'All MET ✓' if missing_text == '' else ''
                    if missing_text != '':
                        num_str = string.replace_all(status_text, 'Waiting for ', '')
                        num_str = string.replace_all(num_str, ' conditions', '')
                        num_str = string.replace_all(num_str, ' condition', '')
                        lite_status = 'Pending (' + num_str + ')'
                    status_color = panel_text_color if missing_text == '' else panel_color_strong_bear

                    table.cell(t1, 0, row, 'Filters', text_color=panel_text_color, text_size=txt_size, bgcolor=background)
                    table.cell(t1, 1, row, lite_status, text_color=status_color, text_size=txt_size, bgcolor=background, text_halign=text.align_right)
                    row += 1

                    if missing_text != '':
                        lite_missing = missing_text

                        lite_commas = string.length(lite_missing) - string.length(string.replace_all(lite_missing, ',', ''))
                        if lite_commas >= 3:
                            pos: int = 0
                            found: int = 0
                            __loop_6__ = pine_loop(0)
                            while __loop_6__.step(string.length(lite_missing) - 1):
                                j = __loop_6__.value
                                if string.substring(lite_missing, j, j + 1) == ',':
                                    found += 1
                                    if found == 3:
                                        pos = j
                                        break
                            if pos > 0:
                                lite_missing = string.substring(lite_missing, 0, pos) + '…'

                        table.cell(t1, 0, row, 'Missing', text_color=panel_text_color, text_size=txt_size, bgcolor=background)
                        table.cell(t1, 1, row, lite_missing, text_color=panel_color_strong_bear, text_size=txt_size, bgcolor=background, text_halign=text.align_right)
                        row += 1

                    regime_arrow = '▲' if regime == 1 else '▼' if regime == -1 else '–'
                    regime_dir = 'Bull' if regime == 1 else 'Bear' if regime == -1 else 'Flat'
                    regime_text = string.format('{0} {1} ({2}b)', regime_arrow, regime_dir, bars_in_regime)
                    regime_color = panel_color_strong_bull if regime == 1 else panel_color_strong_bear if regime == -1 else panel_color_neutral
                    table.cell(t1, 0, row, 'Regime', text_color=panel_text_color, text_size=txt_size, bgcolor=background)
                    table.cell(t1, 1, row, regime_text, text_color=regime_color, text_size=txt_size, bgcolor=background, text_halign=text.align_right)
                    row += 1

                    table.cell(t1, 0, row, 'PRESET', text_color=panel_text_color, text_size=txt_size, bgcolor=background)
                    table.cell(t1, 1, row, get_preset_short(), text_color=panel_text_color, text_size=txt_size, bgcolor=background, text_halign=text.align_right)
                    row += 1
            else:
                table.cell(t1, 0, 0, 'CROSS SIGNALS', text_color=color.white, text_size=txt_size, bgcolor=header_bg)
                table.cell(t1, 1, 0, 'STATUS', text_color=color.white, text_size=txt_size, bgcolor=header_bg, text_halign=text.align_center)
                table.merge_cells(t1, 1, 0, 2, 0)

                row: int = 1

                tk_signal = panel_tk_cross_score
                kj_signal = panel_kijun_score
                ch_signal = panel_chikou_score
                price_kumo = panel_price_kumo_score
                kumo_twist = panel_kumo_twist_score
                overall_signal = panel_consensus_score

                if panel_show_tk_cross:
                    table.cell(t1, 0, row, 'TK Cross vs Kumo', text_color=panel_text_color, text_size=txt_size, bgcolor=background)
                    table.cell(t1, 1, row, get_score_symbol(tk_signal), text_color=get_score_color(tk_signal), text_size=txt_size, bgcolor=background, text_halign=text.align_center)
                    table.merge_cells(t1, 1, row, 2, row)
                    row += 1

                if panel_show_kijun:
                    table.cell(t1, 0, row, 'Kijun Position', text_color=panel_text_color, text_size=txt_size, bgcolor=background)
                    table.cell(t1, 1, row, get_score_symbol(kj_signal), text_color=get_score_color(kj_signal), text_size=txt_size, bgcolor=background, text_halign=text.align_center)
                    table.merge_cells(t1, 1, row, 2, row)
                    row += 1

                if panel_show_chikou_confirm:
                    table.cell(t1, 0, row, 'Chikou Confirm', text_color=panel_text_color, text_size=txt_size, bgcolor=background)
                    table.cell(t1, 1, row, get_score_symbol(ch_signal), text_color=get_score_color(ch_signal), text_size=txt_size, bgcolor=background, text_halign=text.align_center)
                    table.merge_cells(t1, 1, row, 2, row)
                    row += 1

                if panel_show_price_kumo:
                    table.cell(t1, 0, row, 'Price vs Kumo', text_color=panel_text_color, text_size=txt_size, bgcolor=background)
                    table.cell(t1, 1, row, get_score_symbol(price_kumo), text_color=get_score_color(price_kumo), text_size=txt_size, bgcolor=background, text_halign=text.align_center)
                    table.merge_cells(t1, 1, row, 2, row)
                    row += 1

                if panel_show_kumo_twist:
                    table.cell(t1, 0, row, 'Kumo Twist', text_color=panel_text_color, text_size=txt_size, bgcolor=background)
                    table.cell(t1, 1, row, get_score_symbol(kumo_twist), text_color=get_score_color(kumo_twist), text_size=txt_size, bgcolor=background, text_halign=text.align_center)
                    table.merge_cells(t1, 1, row, 2, row)
                    row += 1

                table.cell(t1, 0, row, 'CONSENSUS', text_color=color.white, text_size=txt_size, bgcolor=header_bg)
                table.cell(t1, 1, row, get_score_symbol(overall_signal), text_color=get_score_color(overall_signal), text_size=txt_size, bgcolor=header_bg, text_halign=text.align_center)
                table.merge_cells(t1, 1, row, 2, row)
                row += 1

                if panel_show_details:
                    table.cell(t1, 0, row, '─────────', text_color=color.new(panel_text_color, 50), text_size=txt_size)
                    table.cell(t1, 1, row, 'DETAILS', text_color=color.new(panel_text_color, 50), text_size=txt_size, text_halign=text.align_center)
                    table.cell(t1, 2, row, '─────────', text_color=color.new(panel_text_color, 50), text_size=txt_size)
                    row += 1

                    is_bull_dir = get_composite_direction()
                    status_text, missing_text = get_composite_status(is_bull_dir)
                    status_color = panel_text_color if missing_text == '' else panel_color_strong_bear

                    table.cell(t1, 0, row, 'Filters', text_color=panel_text_color, text_size=txt_size)
                    table.cell(t1, 1, row, status_text, text_color=status_color, text_size=txt_size, text_halign=text.align_center)
                    table.merge_cells(t1, 1, row, 2, row)
                    row += 1

                    if missing_text != '':
                        display_missing = missing_text
                        table.cell(t1, 0, row, 'Missing', text_color=panel_text_color, text_size=txt_size)
                        table.cell(t1, 1, row, display_missing, text_color=panel_color_strong_bear, text_size=txt_size, text_halign=text.align_center)
                        table.merge_cells(t1, 1, row, 2, row)
                        row += 1

                    regime_arrow = '▲' if regime == 1 else '▼' if regime == -1 else '–'
                    regime_dir = 'Bull' if regime == 1 else 'Bear' if regime == -1 else 'Flat'
                    regime_text = string.format('{0} {1} ({2} bars)', regime_arrow, regime_dir, bars_in_regime)
                    regime_color = panel_color_strong_bull if regime == 1 else panel_color_strong_bear if regime == -1 else panel_color_neutral
                    table.cell(t1, 0, row, 'Regime', text_color=panel_text_color, text_size=txt_size)
                    table.cell(t1, 1, row, regime_text, text_color=regime_color, text_size=txt_size, text_halign=text.align_center)
                    table.merge_cells(t1, 1, row, 2, row)
                    row += 1

                    table.cell(t1, 0, row, 'PRESET', text_color=panel_text_color, text_size=txt_size)
                    table.cell(t1, 1, row, format_lengths_display(), text_color=panel_text_color, text_size=txt_size, text_halign=text.align_center)
                    table.merge_cells(t1, 1, row, 2, row)
                    row += 1

    alertcondition(regime_flip_bull, title='Signal: Bullish Reversal ▲', message='SIGNAL: Bullish Reversal — All Ichimoku filters aligned ▲ — {{ticker}} {{interval}} @ {{close}}')

    alertcondition(regime_flip_bear, title='Signal: Bearish Reversal ▼', message='SIGNAL: Bearish Reversal — All Ichimoku filters aligned ▼ — {{ticker}} {{interval}} @ {{close}}')

    alertcondition(sr_zone_flipped, title='S/R: Zone Flipped (S↔R)', message='Ichimoku: S/R zone flipped type (Support ↔ Resistance) - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(sr_zone_retested, title='S/R: Zone Retested', message='Ichimoku: S/R zone retested (price rejected at level) - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(sr_resistance_broken_up, title='S/R: Resistance Broken ↑', message='Ichimoku: Resistance broken upward (bullish breakout) - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(sr_support_broken_down, title='S/R: Support Broken ↓', message='Ichimoku: Support broken downward (bearish breakdown) - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(sr_median_crossed, title='S/R: Median (Equilibrium) Crossed', message='Ichimoku: S/R equilibrium (median) crossed — Hosoda balance point breached - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(tkr_exited_up, title='TK-Range: Bullish Breakout ↑', message='TK-RANGE BREAKOUT: Price broke ABOVE TK/KJ consolidation zone - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(tkr_exited_down, title='TK-Range: Bearish Breakdown ↓', message='TK-RANGE BREAKDOWN: Price broke BELOW TK/KJ consolidation zone - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(tkr_extend and (tkr_median_crossed_up or tkr_median_crossed_down), title='TK-Range: Median (Equilibrium) Crossed', message='TK-RANGE MEDIAN: Equilibrium crossed within extended consolidation zone - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(swing_enabled and (not na(swing_ph)), title='Swing: High Detected', message='SWING HIGH detected - Structural pivot confirmed - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(swing_enabled and (not na(swing_pl)), title='Swing: Low Detected', message='SWING LOW detected - Structural pivot confirmed - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(wave_completed and wave_dir == 1, title='Wave: Bullish Pattern Detected', message='WAVE THEORY: Bullish wave pattern completed (I/V/N/P/Y/W) - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(wave_completed and wave_dir == -1, title='Wave: Bearish Pattern Detected', message='WAVE THEORY: Bearish wave pattern completed (I/V/N/P/Y/W) - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(pt_just_reached_bull, title='Price Target: Bullish Target Reached ↑', message='PRICE THEORY: Bullish N-wave target reached (V/N/E/NT/2E/3E) - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(pt_just_reached_bear, title='Price Target: Bearish Target Reached ↓', message='PRICE THEORY: Bearish N-wave target reached (V/N/E/NT/2E/3E) - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(kihon_window_active, title='Kihon: Time Cycle Window', message='KIHON SŪCHI: Time cycle window active (±1 bar) - Potential reversal timing - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(taito_window_active, title='Taito: Time Symmetry Window', message='TAITO SŪCHI: Time symmetry projection reached (±1 bar) - Duration echo detected - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(txp_window_alert, title='TxP: Time Window with Active Targets', message='TIME x PRICE: Kihon/Taito window active with unreached price targets — watch for confluence - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(txp_confirmed_bull, title='TxP: Bullish Confluence CONFIRMED ◆', message='TIME x PRICE CONFLUENCE CONFIRMED ◆ — Bullish target reached during time cycle window - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(txp_confirmed_bear, title='TxP: Bearish Confluence CONFIRMED ◆', message='TIME x PRICE CONFLUENCE CONFIRMED ◆ — Bearish target reached during time cycle window - {{ticker}} {{interval}} @ {{close}}')

    alertcondition(panel_consensus_changed, title='Panel: Consensus Direction Changed', message='PANEL: CONSENSUS DIRECTION CHANGED - Check panel for new bias - {{ticker}} {{interval}} @ {{close}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)