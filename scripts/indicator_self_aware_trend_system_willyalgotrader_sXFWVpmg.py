"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_float, cast_int
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barstate, bgcolor, chart, close,
    color, format, high, input, label, line, low, math, na, nz, open, plot, position, runtime,
    script, size, string, syminfo, ta, table, text, time, timeframe, volume
)
from pynecore.types import Color, Label, Line, Persistent, PersistentSeries, Series, Table


@udt
class LearnState:
    allTimeCount: int = 0
    allTimePeak: float = 0.0
    allTimeTrough: float = 0.0
    allTimeCumR: float = 0.0
    curWinStreak: int = 0
    curLossStreak: int = 0
    maxWinStreak: int = 0
    maxLossStreak: int = 0
    signalsSinceCalib: int = 0
    breakEvenCount: int = 0
    epoch: int = 0
    epochSum: float = 0.0
    calibStatus: str = "Collecting epoch"
    effQ: float = na(float)
    lastShiftDir: int = 0
    avgRAtLastShift: float = na(float)


@udt
class TradeState:
    dir: int = 0
    side: int = 0
    entryBar: int = 0
    entryTime: int = 0
    cell: int = -1
    epoch: int = 0
    entry: float = na(float)
    sl: float = na(float)
    risk: float = na(float)
    tp1: float = na(float)
    tp2: float = na(float)
    tp3: float = na(float)
    r1: float = na(float)
    r2: float = na(float)
    r3: float = na(float)
    hit1: bool = False
    hit2: bool = False
    hit3: bool = False
    takenR: float = 0.0
    costR: float = 0.0
    remaining: float = 0.0
    entryTqi: float = na(float)
    entryScore: float = na(float)
    entryScoreMax: float = na(float)
    signalPrice: float = na(float)
    id: str = ""
    reason: str = ""
    limitations: str = ""


GRP_MAIN: str = "⚙️ Main Settings"
GRP_ADAPT: str = "🧠 Adaptive Engine"
GRP_TQI: str = "📐 Trend Quality Engine"
GRP_FILTER: str = "🔍 Score Components (not entry filters)"
GRP_RISK: str = "🎯 Risk Management"
GRP_DYN_TP: str = "🎯 Dynamic TP Settings"
GRP_LEARN: str = "🤖 Self-Learning"
GRP_VISUAL: str = "🎨 Visual"
GRP_DASH: str = "📊 Dashboard"
GRP_ALERT: str = "🔔 Alerts"
GRP_COLORS: str = "🎨 Colors"
GRP_MODEL: str = "🧾 Model & Trader Card"


@script.indicator(title="Self-Aware Trend System [WillyAlgoTrader]", shorttitle="SATS", overlay=True, max_lines_count=500, max_labels_count=500, max_bars_back=5000)
def main(
    presetInput=input.string("Auto", "Preset", options=("Auto", "Custom", "Scalping", "Default", "Swing", "Crypto 24/7"), group=GRP_MAIN, tooltip="Quick presets that override key parameters."),
    atrLenInput=input.int(13, "ATR Length", minval=5, maxval=100, group=GRP_MAIN),
    baseMultInput=input.float(2.0, "Base Band Width (xATR)", minval=0.5, maxval=5.0, step=0.1, group=GRP_MAIN),
    sourceInput: Series[float] = input.source(close, "Source", group=GRP_MAIN),
    useAdaptiveInput=input.bool(True, "Enable Vol-Adaptive Bands (legacy ER)", group=GRP_ADAPT, tooltip="Legacy linear ER modulation. Kept for backwards compat — TQI Engine below is recommended."),
    erLengthInput=input.int(20, "Efficiency Window", minval=5, maxval=100, group=GRP_ADAPT),
    adaptStrengthInput=input.float(0.5, "Adaptation Strength", minval=0.0, maxval=1.0, step=0.05, group=GRP_ADAPT),
    atrBaselineLenInput=input.int(100, "ATR Baseline Length", minval=20, maxval=500, group=GRP_ADAPT),
    useTqiInput=input.bool(True, "Enable Trend Quality Engine", group=GRP_TQI, tooltip="Master switch. Computes continuous Trend Quality Index (TQI 0..1) each bar from 4 factors. Modulates band width non-linearly."),
    qualityStrengthInput=input.float(0.4, "Quality Influence", minval=0.0, maxval=1.0, step=0.05, group=GRP_TQI, tooltip="How aggressively TQI compresses/expands bands. 0 = no effect, 1 = maximum."),
    qualityCurveInput=input.float(1.5, "Quality Curve Power", minval=1.0, maxval=3.0, step=0.1, group=GRP_TQI, tooltip="Non-linearity. 1.0 = linear, >1 = bands expand slowly for mild quality drops, rapidly for severe ones."),
    multSmoothInput=input.bool(True, "Smooth Adaptive Multipliers", group=GRP_TQI, tooltip="EMA-smooths band multipliers before applying ratchet logic. Reduces abrupt multiplier changes; the band ratchet still applies."),
    useAsymBandsInput=input.bool(True, "Asymmetric Bands", group=GRP_TQI, tooltip="Active side (in direction of trend) tightens, passive side widens. Creates ratchet-with-leverage effect in strong trends."),
    asymStrengthInput=input.float(0.5, "Asymmetry Strength", minval=0.0, maxval=1.0, step=0.05, group=GRP_TQI),
    useEffAtrInput=input.bool(True, "Efficiency-Weighted ATR", group=GRP_TQI, tooltip="Scale ATR by (0.5 + 0.5*ER). Clean trending volatility counts full; noisy volatility is halved."),
    useCharFlipInput=input.bool(True, "Character-Flip Detection", group=GRP_TQI, tooltip="Allow SuperTrend to flip on quality collapse, not just price break. TQI must collapse from above High threshold (anywhere within the lookback window) to below Low threshold, with price already moving against the trend."),
    charFlipMinAgeInput=input.int(5, "Char-Flip: Min Trend Age / Window", minval=1, maxval=50, group=GRP_TQI, tooltip="Minimum bars current trend must hold before char-flip can fire. Also defines the TQI collapse lookback window (min 3 bars)."),
    charFlipHighInput=input.float(0.55, "Char-Flip: High TQI", minval=0.3, maxval=0.9, step=0.05, group=GRP_TQI),
    charFlipLowInput=input.float(0.25, "Char-Flip: Low TQI", minval=0.0, maxval=0.5, step=0.05, group=GRP_TQI),
    tqiWeightErInput=input.float(0.35, "Weight: Efficiency", minval=0.0, maxval=1.0, step=0.05, group=GRP_TQI),
    tqiWeightVolInput=input.float(0.2, "Weight: Selected Vol Factor", minval=0.0, maxval=1.0, step=0.05, group=GRP_TQI),
    tqiWeightStructInput=input.float(0.25, "Weight: Structure", minval=0.0, maxval=1.0, step=0.05, group=GRP_TQI),
    tqiWeightMomInput=input.float(0.2, "Weight: Momentum Persist", minval=0.0, maxval=1.0, step=0.05, group=GRP_TQI),
    tqiStructLenInput=input.int(20, "Structure Window", minval=5, maxval=100, group=GRP_TQI, tooltip="Lookback for structural price-position calculation."),
    tqiMomLenInput=input.int(10, "Momentum Persist Window", minval=3, maxval=50, group=GRP_TQI),
    useStructureInput=input.bool(True, "Use Structure in Score (display)", group=GRP_FILTER),
    pivotLenInput=input.int(3, "Pivot Strength", minval=2, maxval=10, group=GRP_FILTER),
    useRsiInput=input.bool(True, "Use RSI in Score (display)", group=GRP_FILTER),
    rsiLenInput=input.int(14, "RSI Length", minval=5, maxval=50, group=GRP_FILTER),
    rsiOBInput=input.int(70, "RSI Overbought", minval=55, maxval=90, group=GRP_FILTER),
    rsiOSInput=input.int(30, "RSI Oversold", minval=10, maxval=45, group=GRP_FILTER),
    rsiLookbackInput=input.int(20, "RSI Memory (bars)", minval=3, maxval=100, group=GRP_FILTER),
    useVolInput=input.bool(True, "Use Volume in Score (display)", group=GRP_FILTER),
    volLenInput=input.int(20, "Volume Z Window", minval=5, maxval=100, group=GRP_FILTER),
    showRiskInput=input.bool(True, "Show TP/SL Levels", group=GRP_RISK),
    slAtrMultInput=input.float(1.5, "SL Buffer (xATR)", minval=0.3, maxval=5.0, step=0.1, group=GRP_RISK),
    slMaxDistInput=input.float(4.0, "Max SL Distance (xATR)", minval=1.0, maxval=15.0, step=0.5, group=GRP_RISK, tooltip="Hard cap on stop distance from entry. Protects against stale/far pivots producing oversized risk per trade. The effective cap is never tighter than SL Buffer."),
    tpModeInput=input.string("Fixed", "TP Mode", options=("Fixed", "Dynamic"), group=GRP_RISK, tooltip="Fixed: classic fixed R-multiples.\nDynamic: TP levels adapt to TQI and volatility regime. High TQI + trending = wider targets; low TQI + choppy = tighter targets."),
    tp1RInput=input.float(1.0, "TP1 (R-multiple)", minval=0.5, maxval=10.0, step=0.1, group=GRP_RISK),
    tp2RInput=input.float(2.0, "TP2 (R-multiple)", minval=0.5, maxval=10.0, step=0.1, group=GRP_RISK),
    tp3RInput=input.float(3.0, "TP3 (R-multiple)", minval=0.5, maxval=10.0, step=0.1, group=GRP_RISK),
    dynTpTqiWeightInput=input.float(0.6, "TQI Influence on TP", minval=0.0, maxval=1.0, step=0.05, group=GRP_DYN_TP, tooltip="⚠ These settings only apply when TP Mode = Dynamic.\nHow much TQI affects target expansion. 0 = TQI ignored, 1 = full influence."),
    dynTpVolWeightInput=input.float(0.4, "Volatility Influence on TP", minval=0.0, maxval=1.0, step=0.05, group=GRP_DYN_TP, tooltip="How much vol regime affects targets. High vol = wider targets."),
    dynTpMinScaleInput=input.float(0.5, "Min TP Scale", minval=0.2, maxval=1.0, step=0.05, group=GRP_DYN_TP, tooltip="Floor multiplier — TPs never shrink below base × this value. Prevents absurdly tight targets in chop."),
    dynTpMaxScaleInput=input.float(2.0, "Max TP Scale", minval=1.0, maxval=4.0, step=0.1, group=GRP_DYN_TP, tooltip="Ceiling multiplier — TPs never expand beyond base × this value. Prevents unreachable targets."),
    dynTpFloorR1Input=input.float(0.5, "TP1 Absolute Floor (R)", minval=0.2, maxval=2.0, step=0.1, group=GRP_DYN_TP, tooltip="TP1 will never go below this R value regardless of scaling. TP2/TP3 floors scale proportionally and are capped by the absolute ceiling."),
    dynTpCeilR3Input=input.float(8.0, "TP Absolute Ceiling (R)", minval=2.0, maxval=20.0, step=0.5, group=GRP_DYN_TP, tooltip="No TP level will ever exceed this R value regardless of scaling."),
    labelOffsetInput=input.int(10, "Label Offset (bars)", minval=10, maxval=100, group=GRP_RISK),
    showHitsInput=input.bool(True, "Mark TP Hits (visual)", group=GRP_RISK),
    tradeMaxAgeInput=input.int(100, "Trade Timeout (bars)", minval=10, maxval=500, group=GRP_RISK),
    useAutoCalibInput=input.bool(False, "Enable Auto-Calibration (experimental)", group=GRP_LEARN, tooltip="EXPERIMENTAL hill-climbing: on poor edge, Quality Influence is shifted by one step; if the previous shift made avgR worse, the direction is reversed. On good edge the search is frozen. Note: changing ANY input fully recalculates the script and resets learning memory."),
    calibWindowInput=input.int(20, "Calibration Window", minval=5, maxval=100, group=GRP_LEARN),
    calibBadRInput=input.float(0.0, "Bad-Edge Threshold (R)", minval=-2.0, maxval=1.0, step=0.1, group=GRP_LEARN),
    calibGoodRInput=input.float(0.7, "Good-Edge Threshold (R)", minval=0.0, maxval=5.0, step=0.1, group=GRP_LEARN),
    calibStepQInput=input.float(0.05, "Quality Step", minval=0.01, maxval=0.3, step=0.01, group=GRP_LEARN),
    calibCooldownInput=input.int(5, "Calibration Cooldown (signals)", minval=1, maxval=50, group=GRP_LEARN),
    calibMinQInput=input.float(0.1, "Quality Floor", minval=0.0, maxval=1.0, step=0.05, group=GRP_LEARN),
    calibMaxQInput=input.float(0.9, "Quality Ceiling", minval=0.0, maxval=1.0, step=0.05, group=GRP_LEARN),
    alertInstanceInput=input.string("default", "Alert instance ID", group=GRP_ALERT, tooltip="Use a different ID for each running settings profile. Webhook schema v2 sends an ordered events array; update your receiver before enabling it."),
    feePctInput=input.float(0.0, "Commission per fill (%)", minval=0.0, maxval=5.0, step=0.01, group=GRP_MODEL, tooltip="Applied to entry and each exited fraction. 0 = no commission. Linear price-return model; excludes funding and inverse contracts."),
    slippageTicksInput=input.int(0, "Market slippage (ticks)", minval=0, maxval=1000, group=GRP_MODEL, tooltip="Adverse slippage on entry, SL, flip and timeout. TP fills remain at their limit. Stop gaps fill at the worse of open and stop, plus slippage."),
    minRiskTicksInput=input.int(2, "Minimum initial risk (ticks)", minval=1, maxval=10000, group=GRP_MODEL),
    pivotMaxAgeInput=input.int(100, "Maximum pivot age (bars)", minval=5, maxval=5000, group=GRP_MODEL),
    tqiVolModeInput=input.string("ATR regime", "TQI volatility factor", options=("ATR regime", "Volume activity"), group=GRP_TQI, tooltip="Explicit source; no silent switch between volume and volatility. Missing volume is excluded from TQI weights."),
    showTraderCardInput=input.bool(True, "Show trader card", group=GRP_MODEL),
    traderPosInput=input.string("Bottom Left", "Trader card position", options=("Top Left", "Top Right", "Bottom Left", "Bottom Right", "Middle Right"), group=GRP_MODEL),
    lateEntryRInput=input.float(0.5, "Late entry warning (initial R)", minval=0.0, maxval=10.0, step=0.1, group=GRP_MODEL),
    chopWindowInput=input.int(20, "Flip count window", minval=5, maxval=200, group=GRP_MODEL),
    chopCountInput=input.int(4, "Frequent flips warning", minval=2, maxval=50, group=GRP_MODEL),
    themeInput=input.string("Auto", "Theme", options=("Auto", "Dark", "Light"), group=GRP_VISUAL),
    showBandsInput=input.bool(True, "Show SuperTrend Bands", group=GRP_VISUAL),
    showTqiColorInput=input.bool(True, "Color Line by TQI", group=GRP_VISUAL, tooltip="Line transparency reflects current TQI. Bright = high quality, faded = low quality."),
    showSignalsInput=input.bool(True, "Show Signal Labels", group=GRP_VISUAL),
    showBgInput=input.bool(False, "Show Trend Background", group=GRP_VISUAL),
    showWatermarkInput=input.bool(True, "Show Watermark", group=GRP_VISUAL),
    showDashInput=input.bool(True, "Show Dashboard", group=GRP_DASH),
    showTqiBreakdownInput=input.bool(True, "Show TQI Breakdown", group=GRP_DASH),
    showBreakdownInput=input.bool(False, "Show Score Breakdown (raw contributions)", group=GRP_DASH),
    showPerfInput=input.bool(True, "Show Performance Stats", group=GRP_DASH),
    dashPosStr=input.string("Top Right", "Dashboard Position", options=("Top Left", "Top Right", "Bottom Left", "Bottom Right", "Middle Right"), group=GRP_DASH),
    bullColorInput=input.color(color.new('#00E676'), "Bull", inline="c1", group=GRP_COLORS),
    bearColorInput=input.color(color.new('#FF5252'), "Bear", inline="c1", group=GRP_COLORS),
    slColorInput=input.color(color.new('#FF1744'), "SL", inline="c2", group=GRP_COLORS),
    tpColorInput=input.color(color.new('#00E676'), "TP", inline="c2", group=GRP_COLORS),
    enableAlertsInput=input.bool(True, "Enable Alert Signals", group=GRP_ALERT),
    webhookInput=input.bool(False, "Webhook JSON v2 (events array)", group=GRP_ALERT, tooltip="Applies to combined alert() calls only.\nThe individual alertcondition() alerts (Buy/Sell variants, TP/SL events, timeout, flip-exit, char-flip)\nuse the message you type into the TradingView alert dialog.")
):
    INDICATOR_VERSION: str = "v1.13.1"
    WARMUP_FLOOR: int = 50
    MAX_HISTORY_SIGS: int = 100
    HIT_COLOR_HEX: Color = color.new('#40E0D0')
    MAX_SCORE_REF: int = 100

    ER_LOW_THRESH: float = 0.25
    ER_HIGH_THRESH: float = 0.5
    VOL_LOW_THRESH: float = 0.7
    VOL_HIGH_THRESH: float = 1.3

    EWMA_ALPHA: float = 0.2
    MULT_SMOOTH_ALPHA: float = 0.15

    TQI_MULT_FLOOR: float = 0.6
    TQI_MULT_RANGE: float = 0.8
    ASYM_TIGHTEN_MAX: float = 0.3
    ASYM_WIDEN_MAX: float = 0.4

    GRADE_SCORE_APLUS: int = 80
    GRADE_SCORE_A: int = 60
    GRADE_SCORE_B: int = 40

    GRADE_TQI_APLUS: float = 0.7
    GRADE_TQI_A: float = 0.5
    GRADE_TQI_B: float = 0.35

    tfMinutes: float = timeframe.in_seconds(timeframe.period) / 60.0

    if barstate.isfirst:
        if string.length(alertInstanceInput) == 0 or string.length(alertInstanceInput) > 64 or string.match(alertInstanceInput, '^[A-Za-z0-9_.-]+$') != alertInstanceInput:
            runtime.error('Alert instance ID: use 1-64 ASCII letters, digits, underscore, dot or hyphen.')
        if useTqiInput and tqiWeightErInput + tqiWeightVolInput + tqiWeightStructInput + tqiWeightMomInput <= 0:
            runtime.error('TQI requires at least one positive weight.')
        if useCharFlipInput and useTqiInput and (charFlipLowInput >= charFlipHighInput):
            runtime.error('Char-Flip Low must be below High.')
        if useAutoCalibInput and (calibMinQInput >= calibMaxQInput or calibBadRInput >= calibGoodRInput):
            runtime.error('Calibration requires Min Q < Max Q and Bad R < Good R.')
    resolvedPreset: str = presetInput
    if presetInput == 'Auto':
        resolvedPreset = 'Scalping' if tfMinutes <= 5 else 'Default' if tfMinutes <= 240 else 'Swing'

    __block_result__ = na
    __switch__ = resolvedPreset
    if __switch__ == "Scalping":
        __block_result__ = 10
    elif __switch__ == "Default":
        __block_result__ = 14
    elif __switch__ == "Swing":
        __block_result__ = 21
    elif __switch__ == "Crypto 24/7":
        __block_result__ = 14
    elif __switch__ == "Custom":
        __block_result__ = atrLenInput
    else:
        __block_result__ = atrLenInput
    effectiveAtrLen: int = __block_result__

    __block_result_1__ = na
    __switch__ = resolvedPreset
    if __switch__ == "Scalping":
        __block_result_1__ = 1.5
    elif __switch__ == "Default":
        __block_result_1__ = 2.0
    elif __switch__ == "Swing":
        __block_result_1__ = 2.5
    elif __switch__ == "Crypto 24/7":
        __block_result_1__ = 2.8
    elif __switch__ == "Custom":
        __block_result_1__ = baseMultInput
    else:
        __block_result_1__ = baseMultInput
    effectiveBaseMult: float = __block_result_1__

    __block_result_2__ = na
    __switch__ = resolvedPreset
    if __switch__ == "Scalping":
        __block_result_2__ = 14
    elif __switch__ == "Default":
        __block_result_2__ = 20
    elif __switch__ == "Swing":
        __block_result_2__ = 30
    elif __switch__ == "Crypto 24/7":
        __block_result_2__ = 20
    elif __switch__ == "Custom":
        __block_result_2__ = erLengthInput
    else:
        __block_result_2__ = erLengthInput
    effectiveErLen: int = __block_result_2__

    __block_result_3__ = na
    __switch__ = resolvedPreset
    if __switch__ == "Scalping":
        __block_result_3__ = 9
    elif __switch__ == "Default":
        __block_result_3__ = 14
    elif __switch__ == "Swing":
        __block_result_3__ = 21
    elif __switch__ == "Crypto 24/7":
        __block_result_3__ = 14
    elif __switch__ == "Custom":
        __block_result_3__ = rsiLenInput
    else:
        __block_result_3__ = rsiLenInput
    effectiveRsiLen: int = __block_result_3__

    __block_result_4__ = na
    __switch__ = resolvedPreset
    if __switch__ == "Scalping":
        __block_result_4__ = 1.0
    elif __switch__ == "Default":
        __block_result_4__ = 1.5
    elif __switch__ == "Swing":
        __block_result_4__ = 2.0
    elif __switch__ == "Crypto 24/7":
        __block_result_4__ = 2.5
    elif __switch__ == "Custom":
        __block_result_4__ = slAtrMultInput
    else:
        __block_result_4__ = slAtrMultInput
    effectiveSlMult: float = __block_result_4__

    fixedTp1R: float = math.min(tp1RInput, math.min(tp2RInput, tp3RInput))
    fixedTp3R: float = math.max(tp1RInput, math.max(tp2RInput, tp3RInput))
    fixedTp2R: float = tp1RInput + tp2RInput + tp3RInput - fixedTp1R - fixedTp3R

    __block_result_5__ = na
    __switch__ = themeInput
    if __switch__ == "Dark":
        __block_result_5__ = True
    elif __switch__ == "Light":
        __block_result_5__ = False
    else:
        __block_result_5__ = color.r(chart.bg_color) < 128
    isDark = __block_result_5__

    TEXT_COLOR = color.new('#E0E0E0') if isDark else color.new('#1A1A1A')
    TEXT_MUTED = color.new(color.new('#9E9E9E'), 0) if isDark else color.new(color.new('#757575'), 0)
    TEXT_BRIGHT = color.new('#FFFFFF') if isDark else color.new('#000000')
    TABLE_BG = color.new(color.new('#131722'), 5) if isDark else color.new(color.new('#FFFFFF'), 5)
    TABLE_BORDER = color.new(color.new('#2A2E39'), 0) if isDark else color.new(color.new('#D0D0D0'), 0)
    TABLE_ROW_ALT = color.new(color.new('#1C2030'), 0) if isDark else color.new(color.new('#F0F4F8'), 0)
    HEADER_BG = color.new(color.new('#2962FF'), 0)
    HEADER_TEXT: Color = color.new('#FFFFFF')
    LABEL_TEXT: Color = color.new('#FFFFFF')
    WM_COLOR = color.new(color.new('#FFFFFF'), 80) if isDark else color.new(color.new('#000000'), 80)

    BULL_BG = color.new(bullColorInput, 92)
    BEAR_BG = color.new(bearColorInput, 92)

    NEUTRAL_YELLOW = color.new(color.new('#FFEB3B'), 0)

    HIT_COLOR = color.new(HIT_COLOR_HEX, 0)

    def safeDiv(num: float, den: float, fallback: float = 0.0):
        return num / den if den != 0 and (not na(num)) and (not na(den)) else fallback

    def clamp(v: float, lo: float, hi: float):
        return math.max(lo, math.min(hi, v))

    def clampInt(v: int, lo: int, hi: int):
        return math.max(lo, math.min(hi, v))

    def calcEfficiencyRatio(src: Series[float], len: int):
        change: float = math.abs(src - src[len])
        volatility: float = math.sum(math.abs(src - src[1]), len)
        return safeDiv(change, volatility, 0.0)

    def calcVolumeZ(len: int):
        vMean: float = ta.sma(volume, len)
        vStd: float = ta.stdev(volume, len)
        return safeDiv(volume - vMean, vStd, 0.0)

    def mapClamp(v: float, inLo: float, inHi: float, outLo: float, outHi: float):
        t: float = clamp(safeDiv(v - inLo, inHi - inLo, 0.0), 0.0, 1.0)
        return outLo + t * (outHi - outLo)

    def mapClampInv(v: float, inLo: float, inHi: float, outHigh: float, outLow: float):
        t: float = clamp(safeDiv(v - inLo, inHi - inLo, 0.0), 0.0, 1.0)
        return outHigh - t * (outHigh - outLow)

    def getDashPos(s: str):
        __block_result_6__ = na
        __switch__ = s
        if __switch__ == "Top Left":
            __block_result_6__ = position.top_left
        elif __switch__ == "Top Right":
            __block_result_6__ = position.top_right
        elif __switch__ == "Bottom Left":
            __block_result_6__ = position.bottom_left
        elif __switch__ == "Bottom Right":
            __block_result_6__ = position.bottom_right
        else:
            __block_result_6__ = position.middle_right
        return __block_result_6__

    def erBin(er: float):
        return 0 if er < ER_LOW_THRESH else 1 if er < ER_HIGH_THRESH else 2

    def volBin(vRatio: float):
        return 0 if vRatio < VOL_LOW_THRESH else 1 if vRatio < VOL_HIGH_THRESH else 2

    def cellIdx(eb: int, vb: int):
        return eb * 3 + vb

    def roundDownTick(value: float):
        return math.floor(value / syminfo.mintick + 1e-09) * syminfo.mintick

    def roundUpTick(value: float):
        return math.ceil(value / syminfo.mintick - 1e-09) * syminfo.mintick

    def signedR(value: float):
        return '—' if na(value) else ('+' if value > 0 else '') + string.tostring(value, '0.00')

    def jsonNumber(value: float):
        return 'null' if na(value) else string.tostring(value, '0.################')

    def jsonString(value: str):
        escaped: str = string.replace_all(value, '\\', '\\\\')
        escaped = string.replace_all(escaped, '"', '\\"')
        escaped = string.replace_all(escaped, '\n', '\\n')
        escaped = string.replace_all(escaped, 'r', '\\r')
        escaped = string.replace_all(escaped, '\t', '\\t')
        return '"' + escaped + '"'

    def calcDynTpScale(tqiVal: float, volRatioVal: float, tqiWeight: float, volWeight: float, minScale: float, maxScale: float):
        tqiComp: float = clamp(tqiVal, 0.0, 1.0)
        volComp: float = clamp(mapClamp(volRatioVal, 0.5, 2.0, 0.0, 1.0), 0.0, 1.0)
        wSum: float = tqiWeight + volWeight
        wDenom: float = wSum if wSum > 0 else 1.0
        rawScale: float = (tqiComp * tqiWeight + volComp * volWeight) / wDenom
        finalScale: float = minScale + rawScale * (maxScale - minScale)
        return finalScale if wSum > 0 else 1.0

    signalRBuffer: Persistent[list[float]] = array.new_float()
    gridCount: Persistent[list[int]] = array.new_int(9, 0)
    gridEwmR: Persistent[list[float]] = array.new_float(9, 0.0)

    def updateGridCell(idx: int, r: float):
        __block_result_7__ = na
        if idx >= 0 and idx < 9:
            c: int = array.get(gridCount, idx) + 1
            prevEwm: float = array.get(gridEwmR, idx)
            newEwm: float = r if c == 1 else prevEwm * (1.0 - EWMA_ALPHA) + r * EWMA_ALPHA
            array.set(gridCount, idx, c)
            __block_result_7__ = array.set(gridEwmR, idx, newEwm)
        return __block_result_7__

    def calcRollingStats(window: int):
        n: int = array.size(signalRBuffer)
        __block_result_8__ = (na, na, na)
        if n == 0:
            __block_result_8__ = (0.0, 0.0, 0.0)
        else:
            startIdx: int = math.max(0, n - window)
            sumR: float = 0.0
            wins: int = 0
            runningR: float = 0.0
            minRun: float = 0.0
            peakRun: float = 0.0
            for i in pine_range(startIdx, n - 1):
                r: float = array.get(signalRBuffer, i)
                sumR += r
                if r > 1e-08:
                    wins += 1
                runningR += r
                peakRun = math.max(peakRun, runningR)
                minRun = math.min(minRun, runningR - peakRun)
            cnt: int = n - startIdx
            winRt: float = cast_float(wins) / cast_float(cnt) if cnt > 0 else 0.0
            avgR: float = sumR / cast_float(cnt) if cnt > 0 else 0.0
            __block_result_8__ = (winRt, avgR, minRun)
        return __block_result_8__

    def getRegimeEdge(idx: int):
        c: int = array.get(gridCount, idx)
        ewm: float = array.get(gridEwmR, idx)
        return (c, ewm)


    @method
    def record(this: LearnState, r: float, cIdx: int, entryEpoch: int):
        array.push(signalRBuffer, r)
        while array.size(signalRBuffer) > MAX_HISTORY_SIGS:
            array.shift(signalRBuffer)

        this.allTimeCount += 1
        this.allTimeCumR += r
        if this.allTimeCumR > this.allTimePeak:
            this.allTimePeak = this.allTimeCumR
        curDD: float = this.allTimeCumR - this.allTimePeak
        if curDD < this.allTimeTrough:
            this.allTimeTrough = curDD

        if r > 1e-08:
            this.curWinStreak += 1
            this.curLossStreak = 0
            if this.curWinStreak > this.maxWinStreak:
                this.maxWinStreak = this.curWinStreak
        elif r < -1e-08:
            this.curLossStreak += 1
            this.curWinStreak = 0
            if this.curLossStreak > this.maxLossStreak:
                this.maxLossStreak = this.curLossStreak
        else:
            this.breakEvenCount += 1
            this.curWinStreak = 0
            this.curLossStreak = 0

        updateGridCell(cIdx, r)

        __block_result_9__ = na
        if useAutoCalibInput and useTqiInput and (entryEpoch == this.epoch):
            this.signalsSinceCalib += 1
            this.epochSum += r
            required: int = math.max(calibWindowInput, calibCooldownInput)
            __block_result_10__ = na
            if this.signalsSinceCalib >= required:
                postAvgR: float = this.epochSum / this.signalsSinceCalib
                if postAvgR < calibBadRInput:
                    dir: int = 1 if this.lastShiftDir == 0 else this.lastShiftDir if na(this.avgRAtLastShift) or postAvgR >= this.avgRAtLastShift else -this.lastShiftDir
                    if dir > 0 and this.effQ >= calibMaxQInput or (dir < 0 and this.effQ <= calibMinQInput):
                        dir = -dir
                    nextQ: float = clamp(this.effQ + dir * calibStepQInput, calibMinQInput, calibMaxQInput)
                    this.calibStatus = string.tostring(this.effQ, '0.00') + ' -> ' + string.tostring(nextQ, '0.00') + ' (poor epoch)'
                    this.effQ = nextQ
                    this.lastShiftDir = dir
                else:
                    this.calibStatus = 'Good epoch: hold Q' if postAvgR > calibGoodRInput else 'Neutral epoch: hold Q'
                    if postAvgR > calibGoodRInput:
                        this.lastShiftDir = 0
                this.avgRAtLastShift = postAvgR
                this.signalsSinceCalib = 0
                this.epochSum = 0.0
                this.epoch += 1
                __block_result_10__ = this.epoch
            __block_result_9__ = __block_result_10__
        return __block_result_9__

    learn: Persistent[LearnState] = LearnState()

    warmupBars: int = math.max(WARMUP_FLOOR, math.max(effectiveAtrLen + atrBaselineLenInput - 2, math.max(effectiveRsiLen + rsiLookbackInput - 1, math.max(effectiveErLen, math.max(tqiMomLenInput, tqiStructLenInput)))))
    rawAtr: float = ta.atr(effectiveAtrLen)
    atrBaseline: float = ta.sma(rawAtr, atrBaselineLenInput)
    rsiVal: Series[float] = ta.rsi(close, effectiveRsiLen)
    volRatio: float = safeDiv(rawAtr, atrBaseline, 1.0)
    isWarmedUp: bool = bar_index >= warmupBars and (not na(atrBaseline)) and (rawAtr > 0) and (atrBaseline > 0) and (not na(sourceInput)) and (not na(sourceInput[effectiveErLen])) and (not useRsiInput or not na(rsiVal[rsiLookbackInput - 1]))
    validSourcePairs: float = math.sum(1.0 if not na(sourceInput) and (not na(sourceInput[1])) else 0.0, effectiveErLen)
    isWarmedUp = isWarmedUp and validSourcePairs == effectiveErLen

    erValue: float = calcEfficiencyRatio(sourceInput, effectiveErLen)

    atrValue: float = rawAtr * (0.5 + 0.5 * erValue) if useEffAtrInput else rawAtr

    tqiEr: float = clamp(erValue, 0.0, 1.0)

    volumeValidCount: float = math.sum(1.0 if not na(volume) else 0.0, volLenInput)
    volumeStd: float = ta.stdev(volume, volLenInput)
    volZRaw: float = calcVolumeZ(volLenInput)
    hasVolume: bool = volumeValidCount == volLenInput and volumeStd > 0
    tqiVolAvailable: bool = tqiVolModeInput == 'ATR regime' or hasVolume
    tqiVol: float = mapClamp(volRatio, 0.6, 1.8, 0.0, 1.0) if tqiVolModeInput == 'ATR regime' else mapClamp(volZRaw, -1.0, 2.0, 0.0, 1.0) if hasVolume else 0.0

    structHi: float = ta.highest(high, tqiStructLenInput)
    structLo: float = ta.lowest(low, tqiStructLenInput)
    structRange: float = structHi - structLo
    pricePos: float = safeDiv(close - structLo, structRange, 0.5)
    tqiStruct: float = clamp(math.abs(pricePos - 0.5) * 2.0, 0.0, 1.0)

    windowChange: float = close - close[tqiMomLenInput]
    upMoves: float = nz(math.sum(1.0 if close > close[1] else 0.0, tqiMomLenInput), 0.0)
    downMoves: float = nz(math.sum(1.0 if close < close[1] else 0.0, tqiMomLenInput), 0.0)
    tqiMom: float = upMoves / tqiMomLenInput if windowChange > 0 else downMoves / tqiMomLenInput if windowChange < 0 else 0.0

    availableVolWeight: float = tqiWeightVolInput if tqiVolAvailable else 0.0
    tqiWeightSum: float = tqiWeightErInput + availableVolWeight + tqiWeightStructInput + tqiWeightMomInput
    tqiReady: bool = not useTqiInput or tqiWeightSum > 0
    isWarmedUp = isWarmedUp and tqiReady
    tqiWeightDenom: float = tqiWeightSum if tqiWeightSum > 0 else 1.0
    tqiRaw: float = (tqiEr * tqiWeightErInput + tqiVol * availableVolWeight + tqiStruct * tqiWeightStructInput + tqiMom * tqiWeightMomInput) / tqiWeightDenom if useTqiInput else 0.5
    tqi: float = clamp(tqiRaw, 0.0, 1.0)

    legacyAdaptFactor: float = 1.0 + adaptStrengthInput * (0.5 - erValue) if useAdaptiveInput else 1.0

    if barstate.isfirst:
        learn.effQ = clamp(qualityStrengthInput, calibMinQInput, calibMaxQInput) if useAutoCalibInput else qualityStrengthInput
    if not useAutoCalibInput:
        learn.effQ = qualityStrengthInput
    effectiveQualityStrength: float = learn.effQ

    qualityDeviation: float = math.pow(1.0 - tqi, qualityCurveInput) if useTqiInput else 0.5
    tqiMult: float = 1.0 - effectiveQualityStrength + effectiveQualityStrength * (TQI_MULT_FLOOR + TQI_MULT_RANGE * qualityDeviation)

    symMult: float = effectiveBaseMult * legacyAdaptFactor * tqiMult

    activeMultRaw: float = symMult
    passiveMultRaw: float = symMult
    if useTqiInput and useAsymBandsInput:
        asymTighten: float = 1.0 - asymStrengthInput * tqi * ASYM_TIGHTEN_MAX
        asymWiden: float = 1.0 + asymStrengthInput * tqi * ASYM_WIDEN_MAX
        activeMultRaw = symMult * asymTighten
        passiveMultRaw = symMult * asymWiden

    activeMultSm: PersistentSeries[float] = na(float)
    passiveMultSm: PersistentSeries[float] = na(float)
    activeMultSm = activeMultRaw if na(activeMultSm[1]) else activeMultSm[1] * (1.0 - MULT_SMOOTH_ALPHA) + activeMultRaw * MULT_SMOOTH_ALPHA if multSmoothInput else activeMultRaw
    passiveMultSm = passiveMultRaw if na(passiveMultSm[1]) else passiveMultSm[1] * (1.0 - MULT_SMOOTH_ALPHA) + passiveMultRaw * MULT_SMOOTH_ALPHA if multSmoothInput else passiveMultRaw

    activeMult: float = activeMultSm
    passiveMult: float = passiveMultSm

    lowerBand: PersistentSeries[float] = na(float)
    upperBand: PersistentSeries[float] = na(float)
    stTrend: PersistentSeries[int] = 1

    prevTrend: int = 1 if na(stTrend[1]) else stTrend[1]

    lowerMult: float = activeMult if prevTrend == 1 else passiveMult
    upperMult: float = passiveMult if prevTrend == 1 else activeMult

    lowerBandRaw: float = sourceInput - lowerMult * atrValue
    upperBandRaw: float = sourceInput + upperMult * atrValue

    lowerBand = lowerBandRaw if na(lowerBand[1]) else math.max(lowerBandRaw, lowerBand[1]) if close[1] > lowerBand[1] else lowerBandRaw
    upperBand = upperBandRaw if na(upperBand[1]) else math.min(upperBandRaw, upperBand[1]) if close[1] < upperBand[1] else upperBandRaw

    priceFlipUp: bool = prevTrend == -1 and close > upperBand[1]
    priceFlipDown: bool = prevTrend == 1 and close < lowerBand[1]

    trendStartBar: Persistent[int] = 0
    trendAge: int = bar_index - trendStartBar

    charFlipWindow: int = math.max(charFlipMinAgeInput, 3)
    tqiWindowHigh: float = ta.highest(tqi, charFlipWindow)

    charFlipCondBase: bool = useCharFlipInput and useTqiInput and (trendAge >= charFlipMinAgeInput) and (tqiWindowHigh > charFlipHighInput) and (tqi < charFlipLowInput)
    charFlipDown: bool = charFlipCondBase and prevTrend == 1 and (close < close[charFlipWindow])
    charFlipUp: bool = charFlipCondBase and prevTrend == -1 and (close > close[charFlipWindow])

    finalFlipUp: bool = priceFlipUp or charFlipUp
    finalFlipDown: bool = priceFlipDown or charFlipDown

    stTrend = 1 if na(stTrend[1]) else 1 if finalFlipUp else -1 if finalFlipDown else prevTrend

    if stTrend != prevTrend:
        trendStartBar = bar_index

    stLine: float = lowerBand if stTrend == 1 else upperBand

    flipUp: bool = stTrend == 1 and stTrend[1] == -1
    flipDown: bool = stTrend == -1 and stTrend[1] == 1

    charFlipFiredUp: bool = charFlipUp and (not priceFlipUp) and flipUp
    charFlipFiredDown: bool = charFlipDown and (not priceFlipDown) and flipDown
    charFlipFired: bool = charFlipFiredUp or charFlipFiredDown

    useDynTp: bool = tpModeInput == 'Dynamic'

    dynScale: float = calcDynTpScale(tqi, volRatio, dynTpTqiWeightInput, dynTpVolWeightInput, dynTpMinScaleInput, dynTpMaxScaleInput) if useDynTp else 1.0

    tp1Floor: float = math.min(dynTpFloorR1Input, dynTpCeilR3Input)
    tp2Floor: float = math.min(dynTpFloorR1Input * (fixedTp2R / math.max(fixedTp1R, 0.01)), dynTpCeilR3Input)
    tp3Floor: float = math.min(dynTpFloorR1Input * (fixedTp3R / math.max(fixedTp1R, 0.01)), dynTpCeilR3Input)
    effTp1R: float = clamp(fixedTp1R * dynScale, tp1Floor, dynTpCeilR3Input) if useDynTp else fixedTp1R
    effTp2R: float = clamp(fixedTp2R * dynScale, tp2Floor, dynTpCeilR3Input) if useDynTp else fixedTp2R
    effTp3R: float = clamp(fixedTp3R * dynScale, tp3Floor, dynTpCeilR3Input) if useDynTp else fixedTp3R

    liveTp1R: float = math.min(effTp1R, math.min(effTp2R, effTp3R))
    liveTp3R: float = math.max(effTp1R, math.max(effTp2R, effTp3R))
    liveTp2R: float = effTp1R + effTp2R + effTp3R - liveTp1R - liveTp3R

    volZ: float = volZRaw if hasVolume else 0.0

    rsiLowestG: float = ta.lowest(rsiVal, rsiLookbackInput)
    rsiHighestG: float = ta.highest(rsiVal, rsiLookbackInput)

    pivotHigh: float = ta.pivothigh(high, pivotLenInput, pivotLenInput)
    pivotLow: float = ta.pivotlow(low, pivotLenInput, pivotLenInput)

    lastPivotHigh: Persistent[float] = na(float)
    lastPivotLow: Persistent[float] = na(float)
    lastPivotHighBar: Persistent[int] = na(int)
    lastPivotLowBar: Persistent[int] = na(int)

    if not na(pivotHigh):
        lastPivotHigh = pivotHigh
        lastPivotHighBar = bar_index - pivotLenInput
    if not na(pivotLow):
        lastPivotLow = pivotLow
        lastPivotLowBar = bar_index - pivotLenInput

    validLowPivot: bool = not na(lastPivotLow) and bar_index - lastPivotLowBar <= pivotMaxAgeInput and (lastPivotLow < close)
    validHighPivot: bool = not na(lastPivotHigh) and bar_index - lastPivotHighBar <= pivotMaxAgeInput and (lastPivotHigh > close)

    def calcScoreBreakdown(isBuy: bool, rsiLo: float, rsiHi: float):
        __hist_lowerBand__: Series[float] = lowerBand[0]
        __hist_upperBand__: Series[float] = upperBand[0]
        dirMove: float = close - close[3] if isBuy else close[3] - close
        momScore: float = mapClamp(safeDiv(dirMove, atrValue, 0.0), 0.3, 2.0, 0.0, 17.0)
        erScore: float = mapClamp(erValue, 0.15, 0.7, 0.0, 17.0)
        vScore: float = mapClamp(volZ, 0.0, 3.0, 0.0, 17.0) if useVolInput and hasVolume else 0.0
        rsiDepth: float = math.max(0.0, rsiOSInput - rsiLo) if isBuy else math.max(0.0, rsiHi - rsiOBInput)
        rsiScore: float = mapClamp(rsiDepth, 0.0, 15.0, 0.0, 17.0) if useRsiInput else 0.0
        pivDist: float = math.abs(close - lastPivotLow) if isBuy and (not na(lastPivotLow)) else math.abs(lastPivotHigh - close) if not isBuy and (not na(lastPivotHigh)) else 0.0
        pivotAvailable: bool = validLowPivot if isBuy else validHighPivot
        structScore: float = mapClampInv(safeDiv(pivDist, atrValue, 0.0), 0.0, 1.5, 16.0, 6.0) if useStructureInput and pivotAvailable else 0.0
        breakDepth: float = math.max(0.0, close - __hist_upperBand__[1]) if isBuy else math.max(0.0, __hist_lowerBand__[1] - close)
        breakScore: float = mapClamp(safeDiv(breakDepth, atrValue, 0.0), 0.0, 1.0, 0.0, 16.0)
        return (momScore, erScore, vScore, rsiScore, structScore, breakScore)

    bdMom, bdEr, bdVol, bdRsi, bdStruct, bdBreak = calcScoreBreakdown(stTrend == 1, rsiLowestG, rsiHighestG)
    scoreAvailableMax: float = 50.0 + (17.0 if useVolInput and hasVolume else 0.0) + (17.0 if useRsiInput else 0.0) + (16.0 if useStructureInput and (validLowPivot if stTrend == 1 else validHighPivot) else 0.0)
    bdTotal: float = 100.0 * (bdMom + bdEr + bdVol + bdRsi + bdStruct + bdBreak) / scoreAvailableMax

    curErBin: int = erBin(erValue)
    curVolBin: int = volBin(volRatio)
    curCellIdx: int = cellIdx(curErBin, curVolBin)

    buyScore: float = bdTotal if flipUp else 0.0
    sellScore: float = bdTotal if flipDown else 0.0

    trade: Persistent[TradeState] = TradeState()
    barEvents: list[str] = array.new_string()
    barNotes: list[str] = array.new_string()

    @method
    def emitEvent(this: TradeState, kind: str, level: float, fill__ren__: float, fraction: float, reason: str):
        eventId: str = INDICATOR_VERSION + ':' + this.id + ':' + string.tostring(time) + ':' + kind
        payload: str = '{"event":' + jsonString(kind) + ',"event_id":' + jsonString(eventId) + ',"trade_id":' + jsonString(this.id) + ',"side":' + jsonString('long' if this.side == 1 else 'short') + ',"bar_time":' + string.tostring(time) + ',"level_price":' + jsonNumber(level) + ',"fill_price":' + jsonNumber(fill__ren__) + ',"close_price":' + jsonNumber(close) + ',"fraction":' + jsonNumber(fraction) + ',"remaining":' + jsonNumber(this.remaining) + ',"realized_net_r":' + jsonNumber(this.takenR - this.costR) + ',"entry":' + jsonNumber(this.entry) + ',"sl":' + jsonNumber(this.sl) + ',"tp1":' + jsonNumber(this.tp1) + ',"tp2":' + jsonNumber(this.tp2) + ',"tp3":' + jsonNumber(this.tp3) + ',"score":' + jsonNumber(this.entryScore) + ',"tqi":' + jsonNumber(this.entryTqi if useTqiInput else na) + ',"reason":' + jsonString(reason) + '}'
        array.push(barEvents, payload)
        return array.push(barNotes, kind + ' ' + ('LONG' if this.side == 1 else 'SHORT') + ' @ ' + string.tostring(fill__ren__, format.mintick) + ' (' + reason + ')')

    @method
    def takeFill(this: TradeState, fill__ren__: float, fraction: float):
        this.takenR += fraction * this.side * (fill__ren__ - this.entry) / this.risk
        this.costR += fraction * math.abs(fill__ren__) * feePctInput / 100.0 / this.risk
        this.remaining = math.max(0.0, this.remaining - fraction)
        return this.remaining

    lastM: Persistent[float] = na(float)
    lastE: Persistent[float] = na(float)
    lastV: Persistent[float] = na(float)
    lastR: Persistent[float] = na(float)
    lastS: Persistent[float] = na(float)
    lastB: Persistent[float] = na(float)
    lastScoreMax: Persistent[float] = na(float)
    lastDisplaySide: Persistent[int] = 0
    lastSignalBar: Persistent[int] = 0
    lastExitReason: Persistent[str] = "No completed trade"
    lastExitR: Persistent[float] = na(float)
    lastExitTime: Persistent[int] = na(int)
    lastRejected: Persistent[str] = ""

    confirmedBuy: bool = False
    confirmedSell: bool = False
    tp1Event: bool = False
    tp2Event: bool = False
    tp3Event: bool = False
    slEvent: bool = False
    timeoutFlag: bool = False
    flipExitFlag: bool = False
    closedThisBar: bool = False
    rawBuy: bool = flipUp and barstate.isconfirmed and isWarmedUp
    rawSell: bool = flipDown and barstate.isconfirmed and isWarmedUp
    confirmedCharFlip: bool = charFlipFired and barstate.isconfirmed and isWarmedUp
    calculationEpoch: int = learn.epoch
    slipPrice: float = slippageTicksInput * syminfo.mintick

    if trade.dir != 0 and barstate.isconfirmed and (bar_index > trade.entryBar):
        stopHit: bool = low <= trade.sl if trade.side == 1 else high >= trade.sl

        opposite: bool = trade.side != stTrend
        timedOut: bool = bar_index - trade.entryBar >= tradeMaxAgeInput
        exitReason: str = ""
        exitFill: float = na(float)
        if stopHit:
            exitFill = (math.min(open, trade.sl) if trade.side == 1 else math.max(open, trade.sl)) - trade.side * slipPrice
            exiting: float = trade.remaining
            takeFill(trade, exitFill, exiting)
            slEvent = True
            exitReason = "SL"
            emitEvent(trade, 'sl_hit', trade.sl, exitFill, exiting, 'Stop/gap; SL first on ambiguous OHLC')
        else:
            if not trade.hit1 and (high >= trade.tp1 if trade.side == 1 else low <= trade.tp1):
                trade.hit1 = True
                takeFill(trade, trade.tp1, 1.0 / 3.0)
                tp1Event = True
                emitEvent(trade, 'tp1_hit', trade.tp1, trade.tp1, 1.0 / 3.0, 'Partial limit fill')
            if not trade.hit2 and (high >= trade.tp2 if trade.side == 1 else low <= trade.tp2):
                trade.hit2 = True
                takeFill(trade, trade.tp2, 1.0 / 3.0)
                tp2Event = True
                emitEvent(trade, 'tp2_hit', trade.tp2, trade.tp2, 1.0 / 3.0, 'Partial limit fill')
            if not trade.hit3 and (high >= trade.tp3 if trade.side == 1 else low <= trade.tp3):
                trade.hit3 = True
                takeFill(trade, trade.tp3, trade.remaining)
                tp3Event = True
                exitReason = "TP3"
                exitFill = trade.tp3
                emitEvent(trade, 'tp3_hit', trade.tp3, trade.tp3, 1.0 / 3.0, 'Final limit fill')
            elif opposite or timedOut:
                exitFill = close - trade.side * slipPrice
                exiting: float = trade.remaining
                takeFill(trade, exitFill, exiting)
                flipExitFlag = opposite
                timeoutFlag = not opposite
                exitReason = 'FLIP' if opposite else 'TIMEOUT'
                emitEvent(trade, 'flip_exit' if opposite else 'timeout_exit', close, exitFill, exiting, exitReason)
        if exitReason != '':
            lastExitReason = exitReason
            lastExitR = trade.takenR - trade.costR
            lastExitTime = time

            record(learn, lastExitR, trade.cell, trade.epoch)
            emitEvent(trade, 'trade_closed', na, exitFill, 0.0, exitReason)
            trade.dir = 0
            closedThisBar = True

    if (rawBuy or rawSell) and trade.dir == 0:
        direction: int = 1 if rawBuy else -1
        newEntry: float = math.round_to_mintick(close + direction * slipPrice)
        pivotUsable: bool = validLowPivot if direction == 1 else validHighPivot
        pivotBase: float = (lastPivotLow if pivotUsable else low) if direction == 1 else lastPivotHigh if pivotUsable else high
        buffer: float = effectiveSlMult * atrValue
        cap: float = math.max(slMaxDistInput, effectiveSlMult) * atrValue
        rawStop: float = math.max(math.min(pivotBase - buffer, newEntry - buffer), newEntry - cap) if direction == 1 else math.min(math.max(pivotBase + buffer, newEntry + buffer), newEntry + cap)
        newStop: float = roundDownTick(rawStop) if direction == 1 else roundUpTick(rawStop)
        newRisk: float = direction * (newEntry - newStop)

        distance1: float = math.max(syminfo.mintick, math.max(roundDownTick(newRisk * liveTp1R), roundUpTick(newRisk * tp1Floor) if useDynTp else 0.0))
        distance2: float = math.max(distance1, math.max(roundDownTick(newRisk * liveTp2R), roundUpTick(newRisk * tp2Floor) if useDynTp else 0.0))
        distance3: float = math.max(distance2, math.max(roundDownTick(newRisk * liveTp3R), roundUpTick(newRisk * tp3Floor) if useDynTp else 0.0))
        newTp1: float = math.round_to_mintick(newEntry + direction * distance1)
        newTp2: float = math.round_to_mintick(newEntry + direction * distance2)
        newTp3: float = math.round_to_mintick(newEntry + direction * distance3)
        tickTolerance: float = syminfo.mintick * 1e-06
        ceilingValid: bool = not useDynTp or distance3 <= newRisk * dynTpCeilR3Input + tickTolerance
        stopLive: bool = not na(newStop) and direction * (close - newStop) > tickTolerance
        levelsValid: bool = stopLive and (not na(newRisk)) and (newRisk >= minRiskTicksInput * syminfo.mintick - tickTolerance) and (direction * (newTp1 - newEntry) >= syminfo.mintick - tickTolerance) and (direction * (newTp2 - newTp1) >= -tickTolerance) and (direction * (newTp3 - newTp2) >= -tickTolerance) and ceilingValid
        if levelsValid:
            trade.dir = direction
            trade.side = direction
            trade.entryBar = bar_index
            trade.entryTime = time
            trade.entry = newEntry
            trade.signalPrice = close
            trade.sl = newStop
            trade.risk = newRisk
            trade.tp1 = newTp1
            trade.tp2 = newTp2
            trade.tp3 = newTp3
            trade.r1 = direction * (newTp1 - newEntry) / newRisk
            trade.r2 = direction * (newTp2 - newEntry) / newRisk
            trade.r3 = direction * (newTp3 - newEntry) / newRisk
            trade.hit1 = False
            trade.hit2 = False
            trade.hit3 = False
            trade.takenR = 0.0
            trade.costR = math.abs(newEntry) * feePctInput / 100.0 / newRisk
            trade.remaining = 1.0
            trade.cell = curCellIdx

            trade.epoch = calculationEpoch
            trade.id = alertInstanceInput + ':' + syminfo.tickerid + ':' + timeframe.period + ':' + string.tostring(time) + ':' + string.tostring(direction)
            trade.entryTqi = tqi
            trade.entryScore = bdTotal
            trade.entryScoreMax = scoreAvailableMax
            viaPrice: bool = priceFlipUp if direction == 1 else priceFlipDown
            viaQuality: bool = charFlipUp if direction == 1 else charFlipDown
            trade.reason = 'Price break + quality collapse' if viaPrice and viaQuality else 'Quality collapse' if viaQuality else 'Price band break'
            trade.limitations = ('' if hasVolume else 'Volume unavailable/flat; ') + ('' if pivotUsable else 'No recent valid pivot; ') + ('SL capped/rounded; ' if newRisk >= cap else '')
            confirmedBuy = direction == 1
            confirmedSell = direction == -1
            lastM = bdMom
            lastE = bdEr
            lastV = bdVol
            lastR = bdRsi
            lastS = bdStruct
            lastB = bdBreak
            lastScoreMax = scoreAvailableMax
            lastDisplaySide = direction
            lastSignalBar = bar_index
            lastRejected = ""
            emitEvent(trade, 'buy' if direction == 1 else 'sell', close, newEntry, 1.0, trade.reason)
        else:
            lastRejected = 'Rejected ' + ('BUY' if direction == 1 else 'SELL') + (': SL already breached at signal close after slippage' if not stopLive else ': invalid/sub-tick risk or targets')
    elif rawBuy or rawSell:
        lastRejected = "Entry skipped: model position is still active"

    if confirmedCharFlip:
        array.push(barEvents, '{"event":"char_flip","event_id":' + jsonString(INDICATOR_VERSION + ':' + alertInstanceInput + ':' + syminfo.tickerid + ':' + timeframe.period + ':' + string.tostring(time) + ':char') + ',"bar_time":' + string.tostring(time) + ',"side":' + jsonString('long' if stTrend == 1 else 'short') + ',"tqi":' + jsonNumber(tqi) + '}')
        array.push(barNotes, 'Confirmed character flip')

    recentFlipCount: float = math.sum(1.0 if flipUp or flipDown else 0.0, chopWindowInput)

    lineTransp: int = clampInt(cast_int(math.round(mapClampInv(tqi, 0.1, 0.9, 70.0, 0.0))), 0, 100) if showTqiColorInput and useTqiInput else 0
    stLineColor: Color = color.new(bullColorInput, lineTransp) if stTrend == 1 else color.new(bearColorInput, lineTransp)

    plot(stLine if showBandsInput and isWarmedUp else na, 'SuperTrend', color=stLineColor, linewidth=2)

    bgcolor((BULL_BG if stTrend == 1 else BEAR_BG) if showBgInput and isWarmedUp else na, title='Trend Background')

    scoreRefStr: str = '/' + string.tostring(MAX_SCORE_REF)
    tpModeTag: str = 'Dynamic ×' + string.tostring(dynScale, '0.00') if useDynTp else 'Fixed'

    if showSignalsInput and confirmedBuy:
        label.new(bar_index, low, '▲ BUY  ' + string.tostring(buyScore, '#'), color=bullColorInput, textcolor=LABEL_TEXT, style=label.style_label_up, size=size.small, tooltip='SATS — BUY\nScore: ' + string.tostring(buyScore, '#.0') + scoreRefStr + '\nTQI: ' + string.tostring(tqi, '0.00') + '\nER: ' + string.tostring(erValue, '0.00') + '\nRSI: ' + string.tostring(rsiVal, '#.0') + '\nVol Z: ' + string.tostring(volZ, '0.00') + '\nTP Mode: ' + tpModeTag + '\nR: ' + string.tostring(trade.r1, '0.00') + '/' + string.tostring(trade.r2, '0.00') + '/' + string.tostring(trade.r3, '0.00'))

    if showSignalsInput and confirmedSell:
        label.new(bar_index, high, '▼ SELL  ' + string.tostring(sellScore, '#'), color=bearColorInput, textcolor=LABEL_TEXT, style=label.style_label_down, size=size.small, tooltip='SATS — SELL\nScore: ' + string.tostring(sellScore, '#.0') + scoreRefStr + '\nTQI: ' + string.tostring(tqi, '0.00') + '\nER: ' + string.tostring(erValue, '0.00') + '\nRSI: ' + string.tostring(rsiVal, '#.0') + '\nVol Z: ' + string.tostring(volZ, '0.00') + '\nTP Mode: ' + tpModeTag + '\nR: ' + string.tostring(trade.r1, '0.00') + '/' + string.tostring(trade.r2, '0.00') + '/' + string.tostring(trade.r3, '0.00'))

    lineEntry: Persistent[Line] = na(Line)
    lineSL: Persistent[Line] = na(Line)
    lineTp1: Persistent[Line] = na(Line)
    lineTp2: Persistent[Line] = na(Line)
    lineTp3: Persistent[Line] = na(Line)
    lbEntry: Persistent[Label] = na(Label)
    lbSL: Persistent[Label] = na(Label)
    lbTp1: Persistent[Label] = na(Label)
    lbTp2: Persistent[Label] = na(Label)
    lbTp3: Persistent[Label] = na(Label)

    if showRiskInput:
        if (confirmedBuy or confirmedSell) and (not na(trade.sl)):
            line.delete(lineEntry)
            line.delete(lineSL)
            line.delete(lineTp1)
            line.delete(lineTp2)
            line.delete(lineTp3)
            label.delete(lbEntry)
            label.delete(lbSL)
            label.delete(lbTp1)
            label.delete(lbTp2)
            label.delete(lbTp3)

            lineEnd: int = bar_index + labelOffsetInput
            labelPos: int = bar_index + labelOffsetInput + 2

            tp1Lbl: str = 'TP1 ' + string.tostring(trade.tp1, format.mintick) + (' (' + string.tostring(trade.r1, '#.0') + 'R)' if useDynTp else '')
            tp2Lbl: str = 'TP2 ' + string.tostring(trade.tp2, format.mintick) + (' (' + string.tostring(trade.r2, '#.0') + 'R)' if useDynTp else '')
            tp3Lbl: str = 'TP3 ' + string.tostring(trade.tp3, format.mintick) + (' (' + string.tostring(trade.r3, '#.0') + 'R)' if useDynTp else '')

            lineEntry = line.new(bar_index, trade.entry, lineEnd, trade.entry, color=color.new(color.gray, 0), width=2, style=line.style_solid)
            lineSL = line.new(bar_index, trade.sl, lineEnd, trade.sl, color=slColorInput, width=2, style=line.style_solid)
            lineTp1 = line.new(bar_index, trade.tp1, lineEnd, trade.tp1, color=tpColorInput, width=1, style=line.style_dashed)
            lineTp2 = line.new(bar_index, trade.tp2, lineEnd, trade.tp2, color=tpColorInput, width=1, style=line.style_dashed)
            lineTp3 = line.new(bar_index, trade.tp3, lineEnd, trade.tp3, color=tpColorInput, width=2, style=line.style_dashed)

            lbEntry = label.new(labelPos, trade.entry, 'ENTRY ' + string.tostring(trade.entry, format.mintick), color=color.new(color.gray, 60), textcolor=TEXT_BRIGHT, style=label.style_label_left, size=size.small)
            lbSL = label.new(labelPos, trade.sl, 'SL ' + string.tostring(trade.sl, format.mintick), color=color.new(slColorInput, 60), textcolor=TEXT_BRIGHT, style=label.style_label_left, size=size.small)
            lbTp1 = label.new(labelPos, trade.tp1, tp1Lbl, color=color.new(tpColorInput, 60), textcolor=TEXT_BRIGHT, style=label.style_label_left, size=size.small)
            lbTp2 = label.new(labelPos, trade.tp2, tp2Lbl, color=color.new(tpColorInput, 60), textcolor=TEXT_BRIGHT, style=label.style_label_left, size=size.small)
            lbTp3 = label.new(labelPos, trade.tp3, tp3Lbl, color=color.new(tpColorInput, 60), textcolor=TEXT_BRIGHT, style=label.style_label_left, size=size.small)
        elif trade.dir != 0 and (not na(lineEntry)):
            newLineEnd: int = bar_index + labelOffsetInput
            newLabelPos: int = bar_index + labelOffsetInput + 2

            line.set_x2(lineEntry, newLineEnd)
            line.set_x2(lineSL, newLineEnd)
            line.set_x2(lineTp1, newLineEnd)
            line.set_x2(lineTp2, newLineEnd)
            line.set_x2(lineTp3, newLineEnd)

            label.set_x(lbEntry, newLabelPos)
            label.set_x(lbSL, newLabelPos)
            label.set_x(lbTp1, newLabelPos)
            label.set_x(lbTp2, newLabelPos)
            label.set_x(lbTp3, newLabelPos)

    if showRiskInput:
        if (tp1Event or tp2Event or tp3Event) and (not (confirmedBuy or confirmedSell)):
            if tp1Event and showHitsInput and (not na(lineTp1)):
                line.set_color(lineTp1, HIT_COLOR)
                label.set_text(lbTp1, 'TP1 HIT')
            if tp2Event and showHitsInput and (not na(lineTp2)):
                line.set_color(lineTp2, HIT_COLOR)
                label.set_text(lbTp2, 'TP2 HIT')
            if tp3Event and showHitsInput and (not na(lineTp3)):
                line.set_color(lineTp3, HIT_COLOR)
                label.set_text(lbTp3, 'TP3 HIT')
        if closedThisBar and (not (confirmedBuy or confirmedSell)) and (not na(lbEntry)):
            label.set_text(lbEntry, lastExitReason + ' | ' + signedR(lastExitR) + 'R')
            label.set_color(lbEntry, color.new(color.gray, 60))
            line.set_color(lineEntry, color.gray)
            line.set_color(lineSL, color.gray)
            line.set_color(lineTp1, color.gray)
            line.set_color(lineTp2, color.gray)
            line.set_color(lineTp3, color.gray)

    if showDashInput and barstate.islast:
        dashTable: Persistent[Table] = table.new(getDashPos(('Top Left' if dashPosStr == 'Top Right' else 'Top Right') if showTraderCardInput and dashPosStr == traderPosInput else dashPosStr), 2, 50, bgcolor=TABLE_BG, border_color=TABLE_BORDER, border_width=1, frame_color=TABLE_BORDER, frame_width=1)

        dashWinRate, dashAvgR, dashWindowDD = calcRollingStats(calibWindowInput)
        curRegimeCount, curRegimeEdge = getRegimeEdge(curCellIdx)

        trendStr: str = 'Bullish ▲' if stTrend == 1 else 'Bearish ▼'
        trendCol: Color = bullColorInput if stTrend == 1 else bearColorInput

        signalStr: str = 'BUY' if confirmedBuy else 'SELL' if confirmedSell else '—'
        signalCol: Color = bullColorInput if confirmedBuy else bearColorInput if confirmedSell else TEXT_MUTED

        regimeStr: str = 'Trending' if erValue >= ER_HIGH_THRESH else 'Mixed' if erValue >= ER_LOW_THRESH else 'Choppy'
        regimeCol: Color = bullColorInput if erValue >= ER_HIGH_THRESH else NEUTRAL_YELLOW if erValue >= ER_LOW_THRESH else bearColorInput

        volRegStr: str = 'Low Vol' if volRatio < VOL_LOW_THRESH else 'Norm Vol' if volRatio < VOL_HIGH_THRESH else 'High Vol'

        tqiStr: str = string.tostring(tqi, '0.00') if useTqiInput else 'off'
        tqiCol: Color = (bullColorInput if tqi > 0.6 else NEUTRAL_YELLOW if tqi > 0.35 else bearColorInput) if useTqiInput else TEXT_MUTED
        qStrStr: str = string.tostring(effectiveQualityStrength, '0.00') if useTqiInput else 'off'
        qStrCol: Color = (NEUTRAL_YELLOW if effectiveQualityStrength > qualityStrengthInput else bullColorInput if effectiveQualityStrength < qualityStrengthInput else TEXT_COLOR) if useTqiInput else TEXT_MUTED

        erStr: str = string.tostring(erValue, '0.00')
        rsiStr: str = string.tostring(rsiVal, '#.0')
        volStr: str = string.tostring(volZ, '0.00') + 'σ' if hasVolume else 'n/a'
        warmStr: str = 'Ready' if isWarmedUp else string.tostring(math.max(0, warmupBars - bar_index)) + ' bars / awaiting valid data'

        barsAgo: int = bar_index - lastSignalBar
        sideHdr: str = 'Last: BUY (' + string.tostring(barsAgo) + 'b ago)' if lastDisplaySide == 1 else 'Last: SELL (' + string.tostring(barsAgo) + 'b ago)' if lastDisplaySide == -1 else 'Last: —'
        sideCol: Color = bullColorInput if lastDisplaySide == 1 else bearColorInput if lastDisplaySide == -1 else TEXT_MUTED
        hasBreakdown: bool = lastDisplaySide != 0 and showBreakdownInput
        bdMomStr: str = string.tostring(lastM, '#.0') if lastDisplaySide != 0 and (not na(lastM)) else '—'
        bdErStr: str = string.tostring(lastE, '#.0') if lastDisplaySide != 0 and (not na(lastE)) else '—'
        bdVolStr: str = string.tostring(lastV, '#.0') if lastDisplaySide != 0 and (not na(lastV)) else '—'
        bdRsiStr: str = string.tostring(lastR, '#.0') if lastDisplaySide != 0 and (not na(lastR)) else '—'
        bdStructStr: str = string.tostring(lastS, '#.0') if lastDisplaySide != 0 and (not na(lastS)) else '—'
        bdBreakStr: str = string.tostring(lastB, '#.0') if lastDisplaySide != 0 and (not na(lastB)) else '—'

        tqiErStr: str = string.tostring(tqiEr, '0.00') if useTqiInput else '—'
        tqiVolStr: str = string.tostring(tqiVol, '0.00') if useTqiInput and tqiVolAvailable else 'n/a'
        tqiStructStr: str = string.tostring(tqiStruct, '0.00') if useTqiInput else '—'
        tqiMomStr: str = string.tostring(tqiMom, '0.00') if useTqiInput else '—'

        sigCount: int = array.size(signalRBuffer)
        winRateStr: str = '—' if sigCount == 0 else string.tostring(dashWinRate * 100, '#.0') + '%'
        avgRStr: str = '—' if sigCount == 0 else signedR(dashAvgR) + 'R'
        winDDStr: str = '—' if sigCount == 0 else string.tostring(dashWindowDD, '0.00') + 'R'
        allDDStr: str = '—' if learn.allTimeCount == 0 else string.tostring(learn.allTimeTrough, '0.00') + 'R'
        streakStr: str = '—' if learn.allTimeCount == 0 else 'W:' + string.tostring(learn.curWinStreak) + '/' + string.tostring(learn.maxWinStreak) + ' L:' + string.tostring(learn.curLossStreak) + '/' + string.tostring(learn.maxLossStreak)
        sampleStr: str = 'N=' + string.tostring(math.min(sigCount, calibWindowInput)) + ' | all signals'
        regimeEdgeStr: str = '—' if curRegimeCount == 0 else signedR(curRegimeEdge) + 'R (' + string.tostring(curRegimeCount) + ')'

        winRateCol: Color = TEXT_MUTED if sigCount < 5 else bullColorInput if dashWinRate >= 0.5 else bearColorInput
        avgRCol: Color = TEXT_MUTED if sigCount < 5 else bullColorInput if dashAvgR > 0 else bearColorInput
        regEdgeCol: Color = TEXT_MUTED if curRegimeCount < 5 else bullColorInput if curRegimeEdge > 0 else bearColorInput

        tpModeStr: str = 'Dynamic' if useDynTp else 'Fixed'
        dynScaleStr: str = '×' + string.tostring(dynScale, '0.00') if useDynTp else '—'
        liveRStr: str = string.tostring(trade.r1, '0.00') + ' / ' + string.tostring(trade.r2, '0.00') + ' / ' + string.tostring(trade.r3, '0.00') if trade.dir != 0 else string.tostring(liveTp1R, '0.0') + ' / ' + string.tostring(liveTp2R, '0.0') + ' / ' + string.tostring(liveTp3R, '0.0')
        tpModeCol: Color = (bullColorInput if dynScale > 1.2 else bearColorInput if dynScale < 0.8 else TEXT_COLOR) if useDynTp else TEXT_COLOR

        table.cell(dashTable, 0, 0, 'WillyAlgoTrader', text_color=HEADER_TEXT, bgcolor=HEADER_BG, text_size=size.small, text_halign=text.align_center)
        table.cell(dashTable, 1, 0, 'SATS', text_color=HEADER_TEXT, bgcolor=HEADER_BG, text_size=size.small, text_halign=text.align_center)

        table.cell(dashTable, 0, 1, 'Preset', text_color=TEXT_MUTED, text_size=size.small, bgcolor=TABLE_ROW_ALT)
        table.cell(dashTable, 1, 1, resolvedPreset, text_color=TEXT_COLOR, text_size=size.small, bgcolor=TABLE_ROW_ALT)

        table.cell(dashTable, 0, 2, 'Trend', text_color=TEXT_MUTED, text_size=size.small)
        table.cell(dashTable, 1, 2, trendStr, text_color=trendCol, text_size=size.small)

        table.cell(dashTable, 0, 3, 'TQI', text_color=TEXT_MUTED, text_size=size.small, bgcolor=TABLE_ROW_ALT)
        table.cell(dashTable, 1, 3, tqiStr, text_color=tqiCol, text_size=size.small, bgcolor=TABLE_ROW_ALT)

        table.cell(dashTable, 0, 4, 'Q.Strength', text_color=TEXT_MUTED, text_size=size.small)
        table.cell(dashTable, 1, 4, qStrStr, text_color=qStrCol, text_size=size.small)

        table.cell(dashTable, 0, 5, 'Signal', text_color=TEXT_MUTED, text_size=size.small, bgcolor=TABLE_ROW_ALT)
        table.cell(dashTable, 1, 5, signalStr, text_color=signalCol, text_size=size.small, bgcolor=TABLE_ROW_ALT)

        table.cell(dashTable, 0, 6, 'Regime', text_color=TEXT_MUTED, text_size=size.small)
        table.cell(dashTable, 1, 6, regimeStr + ' / ' + volRegStr, text_color=regimeCol, text_size=size.small)

        table.cell(dashTable, 0, 7, 'ER', text_color=TEXT_MUTED, text_size=size.small, bgcolor=TABLE_ROW_ALT)
        table.cell(dashTable, 1, 7, erStr, text_color=TEXT_COLOR, text_size=size.small, bgcolor=TABLE_ROW_ALT)

        table.cell(dashTable, 0, 8, 'RSI', text_color=TEXT_MUTED, text_size=size.small)
        table.cell(dashTable, 1, 8, rsiStr, text_color=TEXT_COLOR, text_size=size.small)

        table.cell(dashTable, 0, 9, 'Vol Z', text_color=TEXT_MUTED, text_size=size.small, bgcolor=TABLE_ROW_ALT)
        table.cell(dashTable, 1, 9, volStr, text_color=TEXT_COLOR, text_size=size.small, bgcolor=TABLE_ROW_ALT)

        table.cell(dashTable, 0, 10, 'TP Mode', text_color=TEXT_MUTED, text_size=size.small)
        table.cell(dashTable, 1, 10, tpModeStr, text_color=tpModeCol, text_size=size.small)

        table.cell(dashTable, 0, 11, 'Next TP Scale', text_color=TEXT_MUTED, text_size=size.small, bgcolor=TABLE_ROW_ALT)
        table.cell(dashTable, 1, 11, dynScaleStr, text_color=tpModeCol, text_size=size.small, bgcolor=TABLE_ROW_ALT)

        table.cell(dashTable, 0, 12, 'Active R' if trade.dir != 0 else 'Next R', text_color=TEXT_MUTED, text_size=size.small)
        table.cell(dashTable, 1, 12, liveRStr, text_color=TEXT_COLOR, text_size=size.small)

        table.cell(dashTable, 0, 13, 'Status', text_color=TEXT_MUTED, text_size=size.small, bgcolor=TABLE_ROW_ALT)
        table.cell(dashTable, 1, 13, warmStr, text_color=bullColorInput if isWarmedUp else NEUTRAL_YELLOW, text_size=size.small, bgcolor=TABLE_ROW_ALT)

        table.cell(dashTable, 0, 14, 'Version', text_color=TEXT_MUTED, text_size=size.small)
        table.cell(dashTable, 1, 14, INDICATOR_VERSION, text_color=TEXT_MUTED, text_size=size.small)

        rowCursor: int = 15
        if showTqiBreakdownInput and useTqiInput:
            table.cell(dashTable, 0, rowCursor, 'TQI Components', text_color=HEADER_TEXT, bgcolor=HEADER_BG, text_size=size.small, text_halign=text.align_center)
            table.cell(dashTable, 1, rowCursor, '0..1', text_color=HEADER_TEXT, bgcolor=HEADER_BG, text_size=size.small, text_halign=text.align_center)
            rowCursor += 1
            table.cell(dashTable, 0, rowCursor, 'Efficiency', text_color=TEXT_MUTED, text_size=size.small)
            table.cell(dashTable, 1, rowCursor, tqiErStr, text_color=TEXT_COLOR, text_size=size.small)
            rowCursor += 1
            table.cell(dashTable, 0, rowCursor, tqiVolModeInput, text_color=TEXT_MUTED, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            table.cell(dashTable, 1, rowCursor, tqiVolStr, text_color=TEXT_COLOR, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            rowCursor += 1
            table.cell(dashTable, 0, rowCursor, 'Structure', text_color=TEXT_MUTED, text_size=size.small)
            table.cell(dashTable, 1, rowCursor, tqiStructStr, text_color=TEXT_COLOR, text_size=size.small)
            rowCursor += 1
            table.cell(dashTable, 0, rowCursor, 'Mom Persist', text_color=TEXT_MUTED, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            table.cell(dashTable, 1, rowCursor, tqiMomStr, text_color=TEXT_COLOR, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            rowCursor += 1

        if showPerfInput:
            table.cell(dashTable, 0, rowCursor, 'Model net R' if feePctInput > 0 or slippageTicksInput > 0 else 'Model gross R', text_color=HEADER_TEXT, bgcolor=HEADER_BG, text_size=size.small, text_halign=text.align_center)
            table.cell(dashTable, 1, rowCursor, sampleStr, text_color=HEADER_TEXT, bgcolor=HEADER_BG, text_size=size.small, text_halign=text.align_center)
            rowCursor += 1

            table.cell(dashTable, 0, rowCursor, 'Win Rate', text_color=TEXT_MUTED, text_size=size.small)
            table.cell(dashTable, 1, rowCursor, winRateStr, text_color=winRateCol, text_size=size.small)
            rowCursor += 1

            table.cell(dashTable, 0, rowCursor, 'Avg R', text_color=TEXT_MUTED, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            table.cell(dashTable, 1, rowCursor, avgRStr, text_color=avgRCol, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            rowCursor += 1

            table.cell(dashTable, 0, rowCursor, 'Closed DD (window R)', text_color=TEXT_MUTED, text_size=size.small)
            table.cell(dashTable, 1, rowCursor, winDDStr, text_color=TEXT_MUTED if sigCount < 5 else bearColorInput, text_size=size.small)
            rowCursor += 1

            table.cell(dashTable, 0, rowCursor, 'Closed DD (loaded R)', text_color=TEXT_MUTED, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            table.cell(dashTable, 1, rowCursor, allDDStr, text_color=TEXT_MUTED if learn.allTimeCount == 0 else bearColorInput, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            rowCursor += 1

            table.cell(dashTable, 0, rowCursor, 'Streak W/L', text_color=TEXT_MUTED, text_size=size.small)
            table.cell(dashTable, 1, rowCursor, streakStr, text_color=TEXT_COLOR, text_size=size.small)
            rowCursor += 1

            table.cell(dashTable, 0, rowCursor, 'Regime Edge', text_color=TEXT_MUTED, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            table.cell(dashTable, 1, rowCursor, regimeEdgeStr, text_color=regEdgeCol, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            rowCursor += 1

        if hasBreakdown:
            table.cell(dashTable, 0, rowCursor, sideHdr, text_color=sideCol, bgcolor=HEADER_BG, text_size=size.small, text_halign=text.align_center)
            table.cell(dashTable, 1, rowCursor, '/' + string.tostring(lastScoreMax, '0') + ' raw', text_color=HEADER_TEXT, bgcolor=HEADER_BG, text_size=size.small, text_halign=text.align_center)
            rowCursor += 1
            table.cell(dashTable, 0, rowCursor, 'Momentum', text_color=TEXT_MUTED, text_size=size.small)
            table.cell(dashTable, 1, rowCursor, bdMomStr, text_color=TEXT_COLOR, text_size=size.small)
            rowCursor += 1
            table.cell(dashTable, 0, rowCursor, 'Efficiency', text_color=TEXT_MUTED, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            table.cell(dashTable, 1, rowCursor, bdErStr, text_color=TEXT_COLOR, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            rowCursor += 1
            table.cell(dashTable, 0, rowCursor, 'Volume', text_color=TEXT_MUTED, text_size=size.small)
            table.cell(dashTable, 1, rowCursor, bdVolStr, text_color=TEXT_COLOR, text_size=size.small)
            rowCursor += 1
            table.cell(dashTable, 0, rowCursor, 'RSI Depth', text_color=TEXT_MUTED, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            table.cell(dashTable, 1, rowCursor, bdRsiStr, text_color=TEXT_COLOR, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            rowCursor += 1
            table.cell(dashTable, 0, rowCursor, 'Structure', text_color=TEXT_MUTED, text_size=size.small)
            table.cell(dashTable, 1, rowCursor, bdStructStr, text_color=TEXT_COLOR, text_size=size.small)
            rowCursor += 1
            table.cell(dashTable, 0, rowCursor, 'ST Break', text_color=TEXT_MUTED, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            table.cell(dashTable, 1, rowCursor, bdBreakStr, text_color=TEXT_COLOR, text_size=size.small, bgcolor=TABLE_ROW_ALT)
            rowCursor += 1

    if barstate.islast and showWatermarkInput:
        wmTable: Persistent[Table] = table.new(position.bottom_center, 1, 1, bgcolor=color.new(color.black, 100), border_color=color.new(color.black, 100), border_width=0, frame_color=color.new(color.black, 100), frame_width=0)
        table.cell(wmTable, 0, 0, 'WillyAlgoTrader', text_color=WM_COLOR, text_size=size.normal, text_halign=text.align_center, bgcolor=color.new(color.black, 100))

    if enableAlertsInput and barstate.isconfirmed and (array.size(barEvents) > 0):
        packet: str = '{"schema":"sats.events.v2","version":' + jsonString(INDICATOR_VERSION) + ',"ticker":' + jsonString(syminfo.tickerid) + ',"tf":' + jsonString(timeframe.period) + ',"bar_time":' + string.tostring(time) + ',"events":[' + array.join(barEvents, ',') + ']}'
        readable: str = 'SATS ' + syminfo.tickerid + ' ' + timeframe.period + ' | ' + array.join(barNotes, ' | ')
        alert(packet if webhookInput else readable, alert.freq_once_per_bar_close)

    alertcondition(enableAlertsInput and confirmedBuy, title='🟢 Buy Signal', message='🟢 BUY on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and confirmedSell, title='🔴 Sell Signal', message='🔴 SELL on {{ticker}} | TF: {{interval}} | Price: {{close}}')

    buyScoreAPlus: bool = confirmedBuy and buyScore >= GRADE_SCORE_APLUS
    sellScoreAPlus: bool = confirmedSell and sellScore >= GRADE_SCORE_APLUS
    buyScoreAOrBetter: bool = confirmedBuy and buyScore >= GRADE_SCORE_A
    sellScoreAOrBetter: bool = confirmedSell and sellScore >= GRADE_SCORE_A
    buyScoreBOrBetter: bool = confirmedBuy and buyScore >= GRADE_SCORE_B
    sellScoreBOrBetter: bool = confirmedSell and sellScore >= GRADE_SCORE_B

    alertcondition(enableAlertsInput and buyScoreAPlus, title='🟢 Buy Signal (Score A+ only, ≥80)', message='🟢 BUY A+ (score) on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and sellScoreAPlus, title='🔴 Sell Signal (Score A+ only, ≥80)', message='🔴 SELL A+ (score) on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and buyScoreAOrBetter, title='🟢 Buy Signal (Score A+ and A, ≥60)', message='🟢 BUY A+/A (score) on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and sellScoreAOrBetter, title='🔴 Sell Signal (Score A+ and A, ≥60)', message='🔴 SELL A+/A (score) on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and buyScoreBOrBetter, title='🟢 Buy Signal (Score A+/A/B, ≥40)', message='🟢 BUY A+/A/B (score) on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and sellScoreBOrBetter, title='🔴 Sell Signal (Score A+/A/B, ≥40)', message='🔴 SELL A+/A/B (score) on {{ticker}} | TF: {{interval}} | Price: {{close}}')

    buyTqiAPlus: bool = useTqiInput and confirmedBuy and (tqi >= GRADE_TQI_APLUS)
    sellTqiAPlus: bool = useTqiInput and confirmedSell and (tqi >= GRADE_TQI_APLUS)
    buyTqiAOrBetter: bool = useTqiInput and confirmedBuy and (tqi >= GRADE_TQI_A)
    sellTqiAOrBetter: bool = useTqiInput and confirmedSell and (tqi >= GRADE_TQI_A)
    buyTqiBOrBetter: bool = useTqiInput and confirmedBuy and (tqi >= GRADE_TQI_B)
    sellTqiBOrBetter: bool = useTqiInput and confirmedSell and (tqi >= GRADE_TQI_B)

    alertcondition(enableAlertsInput and buyTqiAPlus, title='🟢 Buy Signal (TQI A+ only, ≥0.70)', message='🟢 BUY A+ (TQI) on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and sellTqiAPlus, title='🔴 Sell Signal (TQI A+ only, ≥0.70)', message='🔴 SELL A+ (TQI) on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and buyTqiAOrBetter, title='🟢 Buy Signal (TQI A+ and A, ≥0.50)', message='🟢 BUY A+/A (TQI) on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and sellTqiAOrBetter, title='🔴 Sell Signal (TQI A+ and A, ≥0.50)', message='🔴 SELL A+/A (TQI) on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and buyTqiBOrBetter, title='🟢 Buy Signal (TQI A+/A/B, ≥0.35)', message='🟢 BUY A+/A/B (TQI) on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and sellTqiBOrBetter, title='🔴 Sell Signal (TQI A+/A/B, ≥0.35)', message='🔴 SELL A+/A/B (TQI) on {{ticker}} | TF: {{interval}} | Price: {{close}}')

    alertcondition(enableAlertsInput and tp1Event, title='🎯 TP1 Hit', message='🎯 TP1 HIT on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and tp2Event, title='🎯 TP2 Hit', message='🎯 TP2 HIT on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and tp3Event, title='🏆 TP3 Hit', message='🏆 TP3 HIT on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and slEvent, title='🛑 SL Hit', message='🛑 SL HIT on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and timeoutFlag, title='⏱ Timeout Exit', message='⏱ TIMEOUT EXIT on {{ticker}} | TF: {{interval}} | Price: {{close}}')
    alertcondition(enableAlertsInput and flipExitFlag, title='🔁 Flip Exit', message='🔁 FLIP EXIT on {{ticker}} | TF: {{interval}} | Price: {{close}}')

    alertcondition(enableAlertsInput and confirmedCharFlip, title='🔄 Character-Flip', message='🔄 CHAR-FLIP on {{ticker}} | TF: {{interval}} | Price: {{close}} (TQI collapsed)')

    alertcondition(enableAlertsInput and (confirmedBuy or confirmedSell), title='⚡ Any Signal (Buy or Sell)', message='⚡ Signal on {{ticker}} | TF: {{interval}} | Price: {{close}}')

    if showTraderCardInput and barstate.islast:
        cardPosition: str = traderPosInput
        traderTable: Persistent[Table] = table.new(getDashPos(cardPosition), 2, 16, bgcolor=TABLE_BG, border_width=1, border_color=TABLE_BORDER)
        havePlan: bool = not na(trade.entry)
        active: bool = trade.dir != 0
        openR: float = trade.remaining * trade.side * (close - trade.entry) / trade.risk if active else 0.0
        realized: float = trade.takenR - trade.costR if havePlan else na
        totalR: float = realized + openR if havePlan else na
        driftR: float = trade.side * (close - trade.signalPrice) / trade.risk if havePlan else na
        insidePlan: bool = active and (not trade.hit2) and (trade.side * (close - trade.sl) > 0) and (trade.side * (trade.tp2 - close) > 0)
        newRR: float = math.abs(trade.tp2 - close) / math.abs(close - trade.sl) if insidePlan else na
        nextTarget: float = (trade.tp3 if trade.hit2 else trade.tp2) if trade.hit1 else trade.tp1
        stateText: str = ('LONG' if trade.side == 1 else 'SHORT') + ' | confirmed ' + string.format_time(trade.entryTime, 'MM-dd HH:mm', syminfo.timezone) if active else 'CLOSED: ' + lastExitReason + ' ' + string.format_time(lastExitTime, 'MM-dd HH:mm', syminfo.timezone) if havePlan else 'No model trade'
        healthText: str = 'Warming up / missing data' if not isWarmedUp else 'Data ready'
        healthText += ' | volume n/a' if not hasVolume else ''
        healthText += ' | no recent pivot' if not (validLowPivot if stTrend == 1 else validHighPivot) else ''
        healthText += ' | frequent flips' if recentFlipCount >= chopCountInput else ''
        healthText += ' | current bar provisional' if not barstate.isconfirmed else ''
        planText: str = string.tostring(trade.entry, format.mintick) + ' / ' + string.tostring(trade.sl, format.mintick) if havePlan else '—'
        riskText: str = string.tostring(trade.risk, format.mintick) + ' | ' + string.tostring(trade.risk / syminfo.mintick, '0') + ' ticks | ' + string.tostring(safeDiv(trade.risk * 100, math.abs(trade.entry)), '0.00') + '%' if havePlan else '—'
        targetsText: str = string.tostring(trade.tp1, format.mintick) + ' / ' + string.tostring(trade.tp2, format.mintick) + ' / ' + string.tostring(trade.tp3, format.mintick) if havePlan else '—'
        amountText: str = string.tostring(trade.remaining * 100, '0.0') + '% | TP ' + ('1✓ ' if trade.hit1 else '1— ') + ('2✓ ' if trade.hit2 else '2— ') + ('3✓' if trade.hit3 else '3—') if havePlan else '—'
        pnlText: str = signedR(realized) + ' / ' + signedR(openR) + ' / ' + signedR(totalR) + ' R0' if havePlan else '—'
        distanceText: str = string.tostring(trade.side * (close - trade.sl) / trade.risk, '0.00') + ' / ' + string.tostring(trade.side * (nextTarget - close) / trade.risk, '0.00') + ' R0' if active else '—'
        ageText: str = string.tostring(bar_index - trade.entryBar) + ' bars | timeout in ' + string.tostring(math.max(0, tradeMaxAgeInput - (bar_index - trade.entryBar))) if active else '—'
        lateText: str = 'No active plan' if not active else 'TP2 already filled; re-entry not modeled' if trade.hit2 else 'SL breached / TP2 reached' if not insidePlan else 'TP2 RR ' + string.tostring(newRR, '0.00') + ' | drift ' + signedR(driftR) + 'R0' + (' | LATE' if driftR > lateEntryRInput else '')
        snapshotText: str = trade.reason + ' | score ' + string.tostring(trade.entryScore, '0') + ' | TQI ' + (string.tostring(trade.entryTqi, '0.00') if useTqiInput else 'off') if havePlan else '—'
        calibText: str = 'Off' if not useAutoCalibInput or not useTqiInput else 'Q ' + string.tostring(learn.effQ, '0.00') + ' | ' + learn.calibStatus + ' | n=' + string.tostring(learn.signalsSinceCalib)
        names: list[str] = array.from_items('SATS MODEL TRADE', 'State', 'Signal snapshot', 'Entry / SL', 'Initial risk', 'TP1 / TP2 / TP3', 'Remaining / hits', 'Taken / open / total*', 'To SL / next TP', 'Age / timeout', 'Entry now (gross)', 'Data status', 'Signal limitations', 'Last rejected', 'Calibration', 'Execution model')
        values: list[str] = array.from_items(INDICATOR_VERSION, stateText, snapshotText, planText, riskText, targetsText, amountText, pnlText, distanceText, ageText, lateText, healthText, ('No data limitations at entry' if trade.limitations == '' else trade.limitations) if havePlan else '—', '—' if lastRejected == '' else lastRejected, calibText, 'Fee ' + string.tostring(feePctInput, '0.00') + '% / slip ' + string.tostring(slippageTicksInput) + 't; *open excludes exit costs')
        for row in pine_range(0, 15):
            table.cell(traderTable, 0, row, array.get(names, row), text_color=HEADER_TEXT if row == 0 else TEXT_MUTED, text_size=size.small, bgcolor=HEADER_BG if row == 0 else TABLE_ROW_ALT if row % 2 == 0 else TABLE_BG)
            table.cell(traderTable, 1, row, array.get(values, row), text_color=NEUTRAL_YELLOW if row == 11 and (not isWarmedUp or not hasVolume) else TEXT_COLOR, text_size=size.small, bgcolor=HEADER_BG if row == 0 else TABLE_ROW_ALT if row % 2 == 0 else TABLE_BG)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
