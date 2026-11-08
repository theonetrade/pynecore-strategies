"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt
from pynecore.core.series import inline_series
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barmerge, barstate, bgcolor,
    chart, close, color, fill, format, high, hl2, hlc3, input, label, line, low, math, na, ohlc4,
    open, plot, position, request, runtime, script, size, string, syminfo, ta, table, text, time,
    time_close, timeframe, timestamp, volume, xloc
)
from pynecore.types import Color, Label, Line, NA, Persistent, Series, Table


@udt
class Trade:
    active: bool = False
    dir: int = 0
    id: str = ""
    entryBar: int = na(int)
    entryTime: int = na(int)
    entry: float = na(float)
    initialStop: float = na(float)
    stop: float = na(float)
    risk: float = na(float)
    tp1: float = na(float)
    tp2: float = na(float)
    tp3: float = na(float)
    hit1: bool = False
    hit2: bool = False
    hit3: bool = False
    remaining: float = 1.0
    grossR: float = 0.0
    costR: float = 0.0
    score: float = na(float)
    maxScore: float = na(float)
    grade: str = ""
    regime: int = 0
    origin: str = ""
    exitBar: int = na(int)
    exitTime: int = na(int)
    exitPrice: float = na(float)
    reason: str = ""
    ambiguous: bool = False
    mfe: float = 0.0
    mae: float = 0.0


@udt
class Row:
    kind: int = 0
    key: str = ""
    value: str = ""
    col: Color = na(Color)
    tip: str = ""


VERSION: str = "2.1.0"
ADX_TREND: int = 20
ATR_MEAN_LEN: int = 42
VOLUME_MEAN_LEN: int = 20
VOLUME_SPIKE: float = 1.2
STRUCTURE_BUFFER: float = 0.2
STRUCTURE_CAP: float = 1.5
RSI_UPPER: float = 75
RSI_LOWER: float = 25
LOW_VOL_RATIO: float = 0.7
JOURNAL_MAX: int = 50
FORM_LEN: int = 10
MAIN: str = "Main / data"
ENGINE: str = "Entry engine"
RISK: str = "Risk / execution model"
CONTEXT: str = "Context / session"
SIZE: str = "Position estimate — linear instruments only"
VIEW: str = "Display"
ALERTS: str = "Alerts"


@script.indicator("Precision Sniper [WillyAlgoTrader]", "PrecSniper", overlay=True, max_labels_count=500, max_lines_count=30)
def main(
    sourceChoice=input.string("Close", "Price source", options=("Close", "HL2", "HLC3", "OHLC4"), group=MAIN, tooltip="EMA / RSI / MACD only. Momentum and execution use actual OHLC. External indicator sources are intentionally unsupported."),
    presetInput=input.string("Auto", "Preset", options=("Auto", "Conservative", "Default", "Aggressive", "Scalping", "Swing", "Crypto 24/7", "Custom"), group=MAIN, tooltip="Parameter profiles, not validated profitability rankings. Auto: <=5m Scalping; <=1h Default; <4h Conservative; otherwise Swing."),
    htfMode=input.string("Soft score", "HTF mode", options=("Off", "Soft score", "Hard filter"), group=MAIN),
    htfInput=input.timeframe("", "Higher timeframe (empty = OFF)", group=MAIN, tooltip="Must be strictly higher when enabled. Uses the last closed HTF bar. Empty means OFF, no unavailable score weight."),
    vwapMode=input.string("Auto", "Session VWAP", options=("Auto", "On", "Off"), group=MAIN, tooltip="Auto disables VWAP for Crypto 24/7. On intraday only, with volume data."),
    warmupMult=input.int(3, "Warmup periods", minval=2, maxval=10, group=MAIN),
    startInput=input.time(timestamp('01 Jan 2020 00:00 +0000'), "Entry/statistics start", group=MAIN),
    endInput=input.time(timestamp('01 Jan 2100 00:00 +0000'), "Entry/statistics end", group=MAIN, tooltip="No new entries at/after end; an open model position closes at the first available confirmed close at/after end. Includes that closing bar."),
    emaFastInput=input.int(9, "EMA fast (Custom)", minval=3, maxval=50, group=ENGINE),
    emaSlowInput=input.int(21, "EMA slow (Custom)", minval=10, maxval=100, group=ENGINE),
    emaTrendInput=input.int(55, "EMA trend (Custom)", minval=20, maxval=200, group=ENGINE),
    rsiLenInput=input.int(13, "RSI length (Custom)", minval=5, maxval=30, group=ENGINE),
    scoreInput=input.int(5, "Minimum score / 10 (Custom)", minval=1, maxval=10, group=ENGINE, tooltip="Normalized OPTIONAL evidence. Mandatory crossover and price momentum do not add free points. v1 scores are not comparable."),
    gradeFilter=input.string("All", "Grade filter", options=("All", "A+ and A", "A+ Only"), group=ENGINE),
    hideC=input.bool(True, "Hide C grade", group=ENGINE, tooltip="Raises the required evidence ratio to 0.5 regardless of preset. Scalping (0.4) and Aggressive (0.3) only apply their lower thresholds when this is off."),
    volMode=input.string("Skip Signals", "High volatility", options=("Off", "Skip Signals", "Widen SL"), group=ENGINE),
    volThreshold=input.float(1.3, "High ATR / mean ATR", minval=1.05, maxval=3, step=0.05, group=ENGINE),
    volWiden=input.float(1.5, "High-vol stop multiplier", minval=1, maxval=3, step=0.1, group=ENGINE),
    confirmWindow=input.int(0, "Extra confirmation bars after crossover", minval=0, maxval=10, group=ENGINE, tooltip="0 preserves crossover-only entries. Optional research feature: one candidate, at most one entry; expires on opposite cross, loss of price momentum, or timeout."),
    maxExtension=input.float(0, "Maximum distance to fast EMA / ATR (0 = off)", minval=0, maxval=10, step=0.1, group=ENGINE),
    atrLenInput=input.int(14, "ATR length (Custom)", minval=5, maxval=50, group=RISK),
    slMultInput=input.float(1.5, "ATR stop multiplier (Custom)", minval=0.5, maxval=5, step=0.1, group=RISK),
    tp1Mult=input.float(1, "TP1 R", minval=0.5, maxval=5, step=0.1, group=RISK),
    tp2Mult=input.float(2, "TP2 R", minval=1, maxval=8, step=0.1, group=RISK),
    tp3Mult=input.float(3, "TP3 R", minval=1.5, maxval=12, step=0.5, group=RISK),
    tp1Pct=input.float(0, "Close original position at TP1 (%)", minval=0, maxval=99, group=RISK),
    tp2Pct=input.float(0, "Close original position at TP2 (%)", minval=0, maxval=99, group=RISK, tooltip="TP1 + TP2 must be < 100%. Defaults 0: whole-position model."),
    trailInput=input.bool(True, "Step stop after targets", group=RISK, tooltip="TP1 -> entry; TP2 -> TP1; TP3 -> TP2. Effective NEXT bar. Entry-price stop is not net breakeven after costs. No continuous trailing beyond TP3."),
    fullTP3=input.bool(True, "Close remaining position at TP3", group=RISK),
    structureInput=input.bool(True, "Use window structure", group=RISK),
    swingLookback=input.int(10, "Previous bars for structure (+ current)", minval=3, maxval=30, group=RISK),
    structurePolicy=input.string("Cap and flag", "Structure beyond 1.5x ATR stop", options=("Cap and flag", "Skip entry"), group=RISK),
    minRiskTicks=input.int(2, "Minimum initial risk (ticks)", minval=1, maxval=1000, group=RISK),
    commissionPct=input.float(0, "Commission per side (%)", minval=0, maxval=5, step=0.01, group=RISK, tooltip="Manual proportional cost per fill. Zero means costs excluded. Fixed fees/funding are not modeled."),
    spreadTicks=input.float(0, "Estimated round-trip spread (ticks)", minval=0, maxval=1000, group=RISK),
    slipTicks=input.float(0, "Adverse slippage per side (ticks)", minval=0, maxval=1000, group=RISK, tooltip="A cost deduction for every fill, including target fills. Stop gaps are handled separately by open vs stop."),
    costWarningR=input.float(0.2, "Cost warning / initial R", minval=0.01, maxval=2, step=0.01, group=RISK),
    positiveOnly=input.bool(True, "Require positive trade prices", group=RISK),
    sessionMode=input.string("Info only", "Trading window", options=("Off", "Info only", "Filter entries"), group=CONTEXT),
    sessionHours=input.session("0000-0000", "Session hours", group=CONTEXT),
    sessionDays=input.string("1234567", "Session days (1=Sun ... 7=Sat)", group=CONTEXT),
    sessionTZ=input.string("Etc/UTC", "Session timezone (IANA)", group=CONTEXT, tooltip="For example America/New_York. Independent of chart display timezone."),
    showLevels=input.bool(True, "Show nearest known levels", group=CONTEXT),
    pivotLen=input.int(3, "Confirmed pivot bars left/right", minval=1, maxval=20, group=CONTEXT),
    lateR=input.float(0.5, "Signal extension warning (R)", minval=0.1, maxval=5, step=0.1, group=CONTEXT),
    sizeEnabled=input.bool(False, "Enable manual position estimate", group=SIZE),
    linearConfirmed=input.bool(False, "I verified linear contract, point value and account currency", group=SIZE, tooltip="Only linear P/L with account and quote currency matching. Inverse contracts / FX conversion / liquidation are not modeled."),
    accountCurrency=input.string("USD", "Account currency (must equal quote currency)", group=SIZE),
    equityInput=input.float(10000, "Account equity (manual)", minval=0.01, group=SIZE),
    riskMode=input.string("Percent", "Risk budget mode", options=("Percent", "Cash"), group=SIZE),
    riskPct=input.float(1, "Risk budget (%)", minval=0.01, maxval=100, group=SIZE),
    riskCash=input.float(100, "Risk budget (cash)", minval=0.01, group=SIZE),
    pointValueInput=input.float(1, "Cash per price point per unit (manual)", minval=1e-08, group=SIZE),
    lotStep=input.float(1, "Quantity step", minval=1e-08, group=SIZE),
    minQty=input.float(1, "Minimum quantity", minval=1e-08, group=SIZE),
    manualEntry=input.float(0, "Hypothetical entry override (0 = live close)", minval=0, group=SIZE, tooltip="Only changes the calculator. It never rewrites the model trade."),
    showDash=input.bool(True, "Dashboard", group=VIEW, tooltip="Master toggle for the dashboard table."),
    dashPos=input.string("Top Right", "Dashboard position", options=("Top Right", "Top Left", "Middle Right", "Middle Left", "Bottom Right", "Bottom Left"), group=VIEW),
    showMarketSec=input.bool(True, "  ├ Market section", group=VIEW, tooltip="Regime, HTF, volatility, session, data status, profile."),
    showSignalSec=input.bool(True, "  ├ Signal section", group=VIEW, tooltip="Candidate state, evidence gauge, plan, estimated cost, last decision."),
    showTradeSec=input.bool(True, "  ├ Trade section", group=VIEW, tooltip="Open model position: entry, stop, targets, P/L, distances. Collapses to one row when flat."),
    showStats=input.bool(True, "  ├ Stats section", group=VIEW, tooltip="Closed-trade statistics and the recent-form strip."),
    showDiagSec=input.bool(False, "  └ Diagnostics section", group=VIEW, tooltip="Evidence factors, candidate funnel, rejection reasons, group breakdowns."),
    textSize=input.string("Small", "Text size", options=("Tiny", "Small", "Normal"), group=VIEW),
    panelAlpha=input.int(8, "Panel transparency", minval=0, maxval=90, group=VIEW),
    theme=input.string("Auto", "Theme", options=("Auto", "Dark", "Light"), group=VIEW),
    showJournal=input.bool(False, "Recent trades table", group=VIEW),
    journalRows=input.int(5, "Recent trades shown", minval=1, maxval=15, group=VIEW),
    journalPos=input.string("Bottom Left", "Journal position", options=("Top Right", "Top Left", "Middle Right", "Middle Left", "Bottom Right", "Bottom Left"), group=VIEW),
    showSignals=input.bool(True, "Entry markers", group=VIEW),
    signalSizeInput=input.string("Small", "Signal size", options=("Tiny", "Small", "Normal", "Large", "Huge"), group=VIEW),
    showGradeInput=input.bool(True, "Show grade on entry markers", group=VIEW),
    neutralColorInput=input.color(color.new('#FFEB3B'), "Neutral", group=VIEW),
    showExits=input.bool(True, "Exit markers", group=VIEW),
    showRibbon=input.bool(True, "EMA ribbon", group=VIEW),
    showTPSL=input.bool(True, "Trade levels", group=VIEW),
    showTrail=input.bool(True, "Effective step stop", group=VIEW),
    showBg=input.bool(False, "Trend background", group=VIEW),
    showWatermark=input.bool(True, "Watermark", group=VIEW),
    labelOffset=input.int(20, "Level label offset", minval=5, maxval=50, group=VIEW),
    bullColor=input.color(color.new('#00B876'), "Bull", group=VIEW),
    bearColor=input.color(color.new('#E34850'), "Bear", group=VIEW),
    webhookInput=input.bool(False, "JSON event batch", group=ALERTS, tooltip="Schema v2; one batch at bar close, distinct events with trade_id/event_id. Existing v1 receivers must be updated. Recreate TradingView alerts after updating."),
    alertEntry=input.bool(True, "Entry events", group=ALERTS),
    alertTargets=input.bool(True, "Target events", group=ALERTS),
    alertStopMove=input.bool(True, "Stop changes", group=ALERTS),
    alertExit=input.bool(True, "Full exit events", group=ALERTS),
    alertCandidate=input.bool(False, "Candidate expiry / cancellation", group=ALERTS),
    instanceTag=input.string("main", "Alert instance tag", group=ALERTS, tooltip="Use a distinct tag per concurrently running configuration on the same symbol/timeframe.")
):
    tfSeconds: float = timeframe.in_seconds()
    preset: str = ('Scalping' if tfSeconds <= 300 else 'Default' if tfSeconds <= 3600 else 'Conservative' if tfSeconds < 14400 else 'Swing') if presetInput == 'Auto' else presetInput
    __block_result__ = (na, na, na, na, na, na, na)
    __switch__ = preset
    if __switch__ == "Scalping":
        __block_result__ = (5, 13, 34, 8, 10, 4, 0.8)
    elif __switch__ == "Aggressive":
        __block_result__ = (8, 18, 50, 11, 12, 3, 1.2)
    elif __switch__ == "Default":
        __block_result__ = (9, 21, 55, 13, 14, 5, 1.5)
    elif __switch__ == "Conservative":
        __block_result__ = (12, 26, 89, 14, 14, 7, 2.0)
    elif __switch__ == "Swing":
        __block_result__ = (13, 34, 89, 21, 20, 6, 2.5)
    elif __switch__ == "Crypto 24/7":
        __block_result__ = (9, 21, 55, 14, 20, 5, 2.0)
    else:
        __block_result__ = (emaFastInput, emaSlowInput, emaTrendInput, rsiLenInput, atrLenInput, scoreInput, slMultInput)
    fastLen, slowLen, trendLen, rsiLen, atrLen, minScore, slMult = __block_result__
    htfEnabled: bool = htfMode != 'Off' and htfInput != ''
    if barstate.isfirst:
        if syminfo.mintick * 1000000000.0 < 10:
            runtime.error('Minimum supported price tick is 0.00000001 (1e-8). Smaller ticks require a separate precision model.')
        if not chart.is_standard:
            runtime.error('Use standard time-based candles. Synthetic OHLC are not executable prices.')
        if na(tfSeconds) or tfSeconds <= 0:
            runtime.error('Only time-based charts are supported.')
        if not (fastLen < slowLen and slowLen < trendLen):
            runtime.error('EMA periods must satisfy Fast < Slow < Trend.')
        if not (tp1Mult < tp2Mult and tp2Mult < tp3Mult):
            runtime.error('TP multipliers must satisfy TP1 < TP2 < TP3.')
        if tp1Pct + tp2Pct >= 100:
            runtime.error('TP1 + TP2 partial fractions must be less than 100%.')
        if startInput >= endInput:
            runtime.error('Statistics start must precede end.')
        if htfEnabled and timeframe.in_seconds(htfInput) <= tfSeconds:
            runtime.error('Enabled HTF must be strictly higher; use empty/Off to disable.')
        if na(string.match(sessionDays, '^[1-7]+$')):
            runtime.error('Session days must contain digits 1 to 7.')
        if showDash and showJournal and (dashPos == journalPos):
            runtime.error('Select different corners for the dashboard and trade journal.')

    def fmt(x: float):
        return 'N/A' if na(x) else string.tostring(x, '#.##')

    def price(x: float):
        return 'N/A' if na(x) else string.tostring(x, format.mintick)

    def jsonNum(x: float):
        return 'null' if na(x) else string.tostring(x, '#.################')

    def qtyFmt(x: float):
        return 'N/A' if na(x) else string.tostring(x, '#.################')

    def escape(x: str):
        return string.replace_all(string.replace_all(string.replace_all(string.replace_all(string.replace_all(x, '\\', '\\\\'), '"', '\\"'), '\n', '\\n'), 'r', '\\r'), '\t', '\\t')

    def gradeOf(ratio: float):
        return 'A+' if ratio >= 0.8 else 'A' if ratio >= 0.65 else 'B' if ratio >= 0.5 else 'C'

    def gradeIndex(g: str):
        return 0 if g == 'A+' else 1 if g == 'A' else 2 if g == 'B' else 3

    def directionName(d: int):
        return 'Long' if d == 1 else 'Short' if d == -1 else 'None'

    def pos(p: str):
        return position.top_left if p == 'Top Left' else position.middle_left if p == 'Middle Left' else position.middle_right if p == 'Middle Right' else position.bottom_left if p == 'Bottom Left' else position.bottom_right if p == 'Bottom Right' else position.top_right

    def buildGauge(value: float, maxVal: float, width: int):
        result: str = ""
        filled: int = 0 if na(value) or maxVal <= 0 else math.round(math.min(width, math.max(0.0, value / maxVal * width)))
        for i in pine_range(0, width - 1):
            result += '▰' if i < filled else '▱'
        return result

    txtSize = size.tiny if textSize == 'Tiny' else size.normal if textSize == 'Normal' else size.small
    signalSize = size.tiny if signalSizeInput == 'Tiny' else size.normal if signalSizeInput == 'Normal' else size.large if signalSizeInput == 'Large' else size.huge if signalSizeInput == 'Huge' else size.small
    def roundDown(x: float):
        return math.round_to_mintick(math.floor(x / syminfo.mintick + 1e-08) * syminfo.mintick)

    def roundUp(x: float):
        return math.round_to_mintick(math.ceil(x / syminfo.mintick - 1e-08) * syminfo.mintick)

    def sideCost(fillPrice: float):
        return math.abs(fillPrice) * commissionPct / 100 + (spreadTicks * 0.5 + slipTicks) * syminfo.mintick

    def nearestAbove(ref: float, a: float, b: float, c: float):
        found: float = na(float)
        for level in array.from_items(a, b, c):
            if not na(level) and level > ref and (na(found) or level < found):
                found = level
        return found

    def nearestBelow(ref: float, a: float, b: float, c: float):
        found: float = na(float)
        for level in array.from_items(a, b, c):
            if not na(level) and level < ref and (na(found) or level > found):
                found = level
        return found

    source: float = hl2 if sourceChoice == 'HL2' else hlc3 if sourceChoice == 'HLC3' else ohlc4 if sourceChoice == 'OHLC4' else close
    emaFast: float = ta.ema(source, fastLen)
    emaSlow: float = ta.ema(source, slowLen)
    emaTrend: float = ta.ema(source, trendLen)
    atr: float = ta.atr(atrLen)
    atrMean: float = ta.sma(atr, ATR_MEAN_LEN)
    rsi: float = ta.rsi(source, rsiLen)
    hist: Series
    _, _, hist = ta.macd(source, 12, 26, 9)
    diPlus, diMinus, adx = ta.dmi(14, 14)
    volMean: float = ta.sma(volume, VOLUME_MEAN_LEN)
    vwap: float = ta.vwap(hlc3)
    hasVolume: Persistent[bool] = False
    if barstate.isconfirmed and (not na(volume)) and (volume > 0):
        hasVolume = True
    vwapEnabled: bool = timeframe.isintraday and (vwapMode == 'On' or (vwapMode == 'Auto' and preset != 'Crypto 24/7'))
    volumeReady: bool = not hasVolume or (not na(volume) and volume >= 0 and (not na(volMean)) and (volMean > 0))
    vwapReady: bool = not (vwapEnabled and hasVolume) or not na(vwap)
    volAbove: bool = hasVolume and volumeReady and (volume > volMean * VOLUME_SPIKE)
    htfFast, htfSlow, htfClosedAt, htfReady = request.security(syminfo.tickerid, htfInput if htfEnabled else timeframe.period, (inline_series(ta.ema(source, fastLen), 1), inline_series(ta.ema(source, slowLen), 1), time_close[1], bar_index[1] >= slowLen * warmupMult), lookahead=barmerge.lookahead_on)
    htfBias: int = (1 if htfFast > htfSlow else -1 if htfFast < htfSlow else 0) if htfEnabled and htfReady else 0
    warmupBars: int = math.max(trendLen * warmupMult, atrLen + ATR_MEAN_LEN)
    warmed: bool = bar_index >= warmupBars
    ready: bool = warmed and (not na(atr)) and (atr > 0) and (not na(atrMean)) and (atrMean > 0) and (not na(rsi)) and (not na(hist[1])) and (not na(adx)) and volumeReady and vwapReady and (not htfEnabled or (htfReady and (not na(htfFast)) and (not na(htfSlow))))
    volRatio: float = atr / atrMean if atrMean > 0 else na
    highVol: bool = not na(volRatio) and volRatio > volThreshold
    volatility: str = 'N/A' if na(volRatio) else 'High' if highVol else 'Low' if volRatio < LOW_VOL_RATIO else 'Normal'
    stopMultiplier: float = volWiden if volMode == 'Widen SL' and highVol else 1
    bullCross: bool = ta.crossover(emaFast, emaSlow)
    bearCross: bool = ta.crossunder(emaFast, emaSlow)

    bullMomentum: bool = close > emaFast and close > emaSlow
    bearMomentum: bool = close < emaFast and close < emaSlow
    trendDir: int = 1 if emaFast > emaSlow and close > emaTrend else -1 if emaFast < emaSlow and close < emaTrend else 0
    trending: bool = adx >= ADX_TREND
    regime: int = 0 if not trending else 1 if trendDir != 0 else 2
    regimeName: str = 'Range (ADX<' + string.tostring(ADX_TREND) + ')' if regime == 0 else 'Trend ' + directionName(trendDir) if regime == 1 else 'Mixed'
    scoreMax: float = 5 + (1 if hasVolume else 0) + (1 if vwapEnabled and hasVolume else 0) + (1.5 if htfEnabled and htfMode == 'Soft score' else 0)
    bullScore: float = (1 if close > emaTrend else 0) + (1 if rsi > 50 and rsi < RSI_UPPER else 0) + (1 if hist > 0 else 0) + (1 if hist > hist[1] else 0) + (1 if trending and diPlus > diMinus else 0) + (1 if volAbove else 0) + (1 if vwapEnabled and hasVolume and (close > vwap) else 0) + (1.5 if htfEnabled and htfMode == 'Soft score' and (htfBias == 1) else 0)
    bearScore: float = (1 if close < emaTrend else 0) + (1 if rsi < 50 and rsi > RSI_LOWER else 0) + (1 if hist < 0 else 0) + (1 if hist < hist[1] else 0) + (1 if trending and diMinus > diPlus else 0) + (1 if volAbove else 0) + (1 if vwapEnabled and hasVolume and (close < vwap) else 0) + (1.5 if htfEnabled and htfMode == 'Soft score' and (htfBias == -1) else 0)
    requiredRatio: float = math.max(minScore / 10.0, math.max(0.5 if hideC else 0, 0.8 if gradeFilter == 'A+ Only' else 0.65 if gradeFilter == 'A+ and A' else 0))
    swingLow: float = ta.lowest(low, swingLookback + 1)
    swingHigh: float = ta.highest(high, swingLookback + 1)

    def makePlan(d: int):
        e: float = math.round_to_mintick(close)
        atrDistance: float = atr * slMult * stopMultiplier
        atrStop: float = e - d * atrDistance
        structStop: float = swingLow - atr * STRUCTURE_BUFFER if d == 1 else swingHigh + atr * STRUCTURE_BUFFER

        rawStop: float = (math.min(atrStop, structStop) if d == 1 else math.max(atrStop, structStop)) if structureInput else atrStop
        capped: bool = structureInput and math.abs(e - rawStop) > atrDistance * STRUCTURE_CAP
        bounded: float = e - d * atrDistance * STRUCTURE_CAP if capped else rawStop
        stop: float = roundDown(bounded) if d == 1 else roundUp(bounded)
        risk: float = math.abs(e - stop)
        p1: float = math.round_to_mintick(e + d * risk * tp1Mult)
        p2: float = math.round_to_mintick(e + d * risk * tp2Mult)
        p3: float = math.round_to_mintick(e + d * risk * tp3Mult)
        valid: bool = not na(risk) and risk >= minRiskTicks * syminfo.mintick - syminfo.mintick * 1e-06 and (d * (e - stop) > 0) and (d * (p1 - e) > 0) and (d * (p2 - p1) > 0) and (d * (p3 - p2) > 0) and (not positiveOnly or math.min(math.min(e, stop), math.min(p1, math.min(p2, p3))) > 0)
        origin: str = 'ATR' if not structureInput else 'ATR capped (inside structure possible)' if capped else 'Structure' if rawStop != atrStop else 'ATR'
        return (e, stop, risk, p1, p2, p3, capped, valid, origin)

    sessionSpec: str = sessionHours + ':' + sessionDays

    inSession: Series[bool] = not na(time(timeframe.period, sessionSpec, sessionTZ))
    sessionAllowed: bool = sessionMode != 'Filter entries' or inSession
    dateAllowed: bool = time >= startInput and time_close < endInput

    sessionKey: Series[int] = time('1D', sessionSpec, sessionTZ)
    sessionStart: bool = inSession and (not inSession[1] or (sessionHours == '0000-0000' and sessionKey != sessionKey[1]))
    sessionHigh: Persistent[float] = na(float)
    sessionLow: Persistent[float] = na(float)
    if inSession:
        sessionHigh = high if sessionStart or na(sessionHigh) else math.max(sessionHigh, high)
        sessionLow = low if sessionStart or na(sessionLow) else math.min(sessionLow, low)
    priorDayHigh, priorDayLow = request.security(syminfo.tickerid, '1D' if timeframe.isintraday else timeframe.period, (high[1], low[1]), lookahead=barmerge.lookahead_on)
    pivotHigh: float = ta.pivothigh(high, pivotLen, pivotLen)
    pivotLow: float = ta.pivotlow(low, pivotLen, pivotLen)
    knownHigh: Persistent[float] = na(float)
    knownLow: Persistent[float] = na(float)
    if barstate.isconfirmed:
        if not na(pivotHigh):
            knownHigh = pivotHigh
        if not na(pivotLow):
            knownLow = pivotLow

    @method
    def netR(t: Trade):
        return t.grossR - t.costR

    @method
    def takePartial(t: Trade, px: float, requestedFraction: float):
        fraction: float = math.min(t.remaining, math.max(0, requestedFraction))
        t.grossR += fraction * t.dir * (px - t.entry) / t.risk
        t.costR += fraction * sideCost(px) / t.risk
        t.remaining = math.max(0, t.remaining - fraction)
        return t.remaining

    @method
    def finish(t: Trade, px: float, why: str):
        takePartial(t, px, t.remaining)
        t.active = False
        t.exitPrice = px
        t.exitBar = bar_index
        t.exitTime = time_close
        t.reason = why
        return t.reason

    @method
    def observe(t: Trade, favorable: float, adverse: float):
        t.mfe = math.max(t.mfe, math.max(0, t.dir * (favorable - t.entry) / t.risk))
        t.mae = math.max(t.mae, math.max(0, -t.dir * (adverse - t.entry) / t.risk))
        return t.mae

    @method
    def event(t: Trade, events: list[str], texts: list[str], kind: str, level: float, enabled: bool):
        __block_result_1__ = na
        if enabled:
            eid: str = t.id + ':' + string.tostring(time_close) + ':' + kind
            message: str = '{"event_id":"' + escape(eid) + '","trade_id":"' + escape(t.id) + '","event_type":"' + kind + '","direction":"' + directionName(t.dir) + '","bar_time":' + string.tostring(time)
            message += ',"time_close":' + string.tostring(time_close)
            message += ',"entry":' + jsonNum(t.entry)
            message += ',"level_price":' + jsonNum(level)
            message += ',"bar_close":' + jsonNum(close)
            message += ',"initial_stop":' + jsonNum(t.initialStop)
            message += ',"new_stop":' + jsonNum(t.stop)
            message += ',"stop_effective":"next_bar","tp1":' + jsonNum(t.tp1)
            message += ',"tp2":' + jsonNum(t.tp2)
            message += ',"tp3":' + jsonNum(t.tp3)
            message += ',"remaining":' + jsonNum(t.remaining)
            message += ',"position_closed":' + ('false' if t.active else 'true')
            message += ',"exit_reason":"' + escape(t.reason) + '","realized_net_r":' + jsonNum(netR(t))
            message += ',"score":' + jsonNum(t.score)
            message += ',"score_max":' + jsonNum(t.maxScore)
            message += ',"grade":"' + t.grade + '","ambiguous_bar":' + ('true' if t.ambiguous else 'false') + '}'
            array.push(events, message)
            __block_result_1__ = array.push(texts, syminfo.tickerid + ' | ' + timeframe.period + ' | ' + directionName(t.dir) + ' | ' + kind + ' | Level ' + price(level) + ' | Stop ' + price(t.stop) + ' | Remaining ' + fmt(t.remaining * 100) + '% | Model net ' + fmt(netR(t)) + 'R | ' + t.reason + ' | ' + string.format_time(time_close, 'yyyy-MM-dd HH:mm', sessionTZ))
        return __block_result_1__

    trade: Persistent[Trade] = Trade()
    journal: Persistent[list[Trade]] = array.new(0, NA(Trade))
    rejected: Persistent[list[int]] = array.new_int(12, 0)
    groupN: Persistent[list[int]] = array.new_int(9, 0)
    groupR: Persistent[list[float]] = array.new_float(9, 0)
    candidates: Persistent[int] = 0
    accepted: Persistent[int] = 0
    pendingDir: Persistent[int] = 0
    pendingBar: Persistent[int] = na(int)
    pendingId: Persistent[str] = ""
    lastDecision: Persistent[str] = "Waiting for crossover"
    total: Persistent[int] = 0
    wins: Persistent[int] = 0
    losses: Persistent[int] = 0
    breakevens: Persistent[int] = 0
    lossStreak: Persistent[int] = 0
    maxLossStreak: Persistent[int] = 0
    totalR: Persistent[float] = 0
    grossWin: Persistent[float] = 0
    grossLoss: Persistent[float] = 0
    peakR: Persistent[float] = 0
    maxDrawdownR: Persistent[float] = 0
    totalDuration: Persistent[int] = 0
    ambiguousTrades: Persistent[int] = 0
    reachedTP1: Persistent[int] = 0
    reachedTP2: Persistent[int] = 0
    totalMFE: Persistent[float] = 0
    totalMAE: Persistent[float] = 0
    firstEntryAt: Persistent[int] = na(int)
    lastExitAt: Persistent[int] = na(int)
    events: list[str] = array.new_string()
    texts: list[str] = array.new_string()
    confirmedBuy: bool = False
    confirmedSell: bool = False
    tp1Event: bool = False
    tp2Event: bool = False
    tp3Event: bool = False
    slEvent: bool = False
    exitEvent: bool = False
    stopEvent: bool = False
    cancelEvent: bool = False

    def rejectReason(code: int):
        __block_result_2__ = na
        __switch__ = code
        if __switch__ == 1:
            __block_result_2__ = "Data not ready / warmup"
        elif __switch__ == 2:
            __block_result_2__ = "Outside date window"
        elif __switch__ == 3:
            __block_result_2__ = "Outside trading session"
        elif __switch__ == 4:
            __block_result_2__ = "High volatility blocks entry"
        elif __switch__ == 5:
            __block_result_2__ = "Price momentum lost"
        elif __switch__ == 6:
            __block_result_2__ = "RSI extreme"
        elif __switch__ == 7:
            __block_result_2__ = "HTF opposes / neutral"
        elif __switch__ == 8:
            __block_result_2__ = "Insufficient score"
        elif __switch__ == 9:
            __block_result_2__ = "Invalid tick/risk/target geometry"
        elif __switch__ == 10:
            __block_result_2__ = "Structure exceeds cap"
        elif __switch__ == 11:
            __block_result_2__ = "Too far from fast EMA"
        else:
            __block_result_2__ = "Accepted"
        return __block_result_2__

    def gate(d: int, planValid: bool, capped: bool):
        evidence: float = bullScore if d == 1 else bearScore
        momentum: bool = bullMomentum if d == 1 else bearMomentum

        result: int = 0
        if not ready:
            result = 1
        elif not dateAllowed:
            result = 2
        elif not sessionAllowed:
            result = 3
        elif volMode == 'Skip Signals' and highVol:
            result = 4
        elif not momentum:
            result = 5
        elif rsi >= RSI_UPPER if d == 1 else rsi <= RSI_LOWER:
            result = 6
        elif htfEnabled and htfMode == 'Hard filter' and (htfBias != d):
            result = 7
        elif evidence + 1e-09 < requiredRatio * scoreMax:
            result = 8
        elif not planValid:
            result = 9
        elif structurePolicy == 'Skip entry' and capped:
            result = 10
        elif maxExtension > 0 and math.abs(close - emaFast) / atr > maxExtension:
            result = 11
        return result

    def candidateEvent(ev: list[str], tx: list[str], id: str, dir: int, why: str):
        __block_result_3__ = na
        if alertCandidate:
            array.push(ev, '{"event_id":"' + escape(id + ':' + string.tostring(time_close) + ':candidate_cancelled') + '","candidate_id":"' + escape(id) + '","event_type":"candidate_cancelled","direction":"' + directionName(dir) + '","time_close":' + string.tostring(time_close) + ',"reason":"' + escape(why) + '"}')
            __block_result_3__ = array.push(tx, syminfo.tickerid + ' | ' + timeframe.period + ' | ' + directionName(dir) + ' candidate cancelled | ' + why)
        return __block_result_3__

    if barstate.isconfirmed:
        if (bullCross or bearCross) and dateAllowed and warmed:
            if pendingDir != 0:
                candidateEvent(events, texts, pendingId, pendingDir, 'Opposite crossover')
                cancelEvent = True
                array.set(rejected, 0, array.get(rejected, 0) + 1)
            pendingDir = 1 if bullCross else -1
            pendingBar = bar_index
            pendingId = instanceTag + ':' + syminfo.tickerid + ':' + timeframe.period + ':' + string.tostring(time_close)
            candidates += 1
        signal: int = 0
        if pendingDir != 0:
            _, _, _, _, _, _, cap, valid, _ = makePlan(pendingDir)
            code: int = gate(pendingDir, valid, cap)

            if not (bullMomentum if pendingDir == 1 else bearMomentum):
                code = 5

            lastChance: bool = bar_index - pendingBar >= confirmWindow
            alreadyOpen: bool = trade.active and trade.dir == pendingDir
            if code == 0 and (not alreadyOpen):
                signal = pendingDir
                lastDecision = directionName(signal) + ' accepted'
                accepted += 1
                pendingDir = 0
            else:
                lastDecision = 'Same direction already open' if alreadyOpen else rejectReason(code)
                terminal: bool = lastChance or code == 5 or alreadyOpen or (not dateAllowed)
                if terminal:
                    slot: int = 0 if alreadyOpen else code
                    array.set(rejected, slot, array.get(rejected, slot) + 1)
                    candidateEvent(events, texts, pendingId, pendingDir, lastDecision)
                    cancelEvent = True
                    pendingDir = 0

        if trade.active and bar_index > trade.entryBar:
            oldStop: float = trade.stop
            stopped: bool = low <= oldStop if trade.dir == 1 else high >= oldStop
            touch1: bool = not trade.hit1 and (high >= trade.tp1 if trade.dir == 1 else low <= trade.tp1)
            touch2: bool = not trade.hit2 and (high >= trade.tp2 if trade.dir == 1 else low <= trade.tp2)
            touch3: bool = not trade.hit3 and (high >= trade.tp3 if trade.dir == 1 else low <= trade.tp3)
            if stopped:
                fillPrice: float = math.min(open, oldStop) if trade.dir == 1 else math.max(open, oldStop)
                trade.ambiguous = trade.ambiguous or touch1 or touch2 or touch3
                observe(trade, open, open)
                observe(trade, fillPrice, fillPrice)
                finish(trade, fillPrice, 'SL' if oldStop == trade.initialStop else 'Step stop')
                slEvent = True
            else:
                if touch1:
                    trade.hit1 = True
                    takePartial(trade, trade.tp1, tp1Pct / 100)
                    tp1Event = True
                    event(trade, events, texts, 'tp1_hit', trade.tp1, alertTargets)
                if touch2:
                    trade.hit2 = True
                    takePartial(trade, trade.tp2, tp2Pct / 100)
                    tp2Event = True
                    event(trade, events, texts, 'tp2_hit', trade.tp2, alertTargets)
                if touch3:
                    trade.hit3 = True
                    tp3Event = True
                    event(trade, events, texts, 'tp3_hit', trade.tp3, alertTargets)
                    if fullTP3:
                        observe(trade, open, open)
                        observe(trade, trade.tp3, trade.tp3)
                        finish(trade, trade.tp3, 'TP3')
                if trade.active:
                    observe(trade, high if trade.dir == 1 else low, low if trade.dir == 1 else high)
                    if signal == -trade.dir:
                        finish(trade, close, 'Reversal')
                    elif time_close >= endInput:
                        finish(trade, close, 'Date end')
                    elif trailInput:
                        nextStop: float = trade.tp2 if trade.hit3 else trade.tp1 if trade.hit2 else trade.entry if trade.hit1 else trade.stop
                        if trade.dir * (nextStop - trade.stop) > syminfo.mintick * 0.1:
                            trade.stop = nextStop
                            stopEvent = True
                            event(trade, events, texts, 'stop_changed', nextStop, alertStopMove)

            if not trade.active:
                exitEvent = True
                realized: float = netR(trade)
                total += 1
                totalR += realized
                peakR = math.max(peakR, totalR)
                maxDrawdownR = math.max(maxDrawdownR, peakR - totalR)
                totalDuration += bar_index - trade.entryBar
                lastExitAt = time_close
                totalMFE += trade.mfe
                totalMAE += trade.mae
                reachedTP1 += 1 if trade.hit1 else 0
                reachedTP2 += 1 if trade.hit2 else 0
                ambiguousTrades += 1 if trade.ambiguous else 0
                if realized > 1e-08:
                    wins += 1
                    grossWin += realized
                    lossStreak = 0
                elif realized < -1e-08:
                    losses += 1
                    grossLoss += -realized
                    lossStreak += 1
                    maxLossStreak = math.max(maxLossStreak, lossStreak)
                else:
                    breakevens += 1
                    lossStreak = 0
                for bucket in array.from_items(0 if trade.dir == 1 else 1, 2 + gradeIndex(trade.grade), 6 + trade.regime):
                    array.set(groupN, bucket, array.get(groupN, bucket) + 1)
                    array.set(groupR, bucket, array.get(groupR, bucket) + realized)
                event(trade, events, texts, 'exit', trade.exitPrice, alertExit)
                array.unshift(journal, trade)
                if array.size(journal) > JOURNAL_MAX:
                    array.pop(journal)
                if showExits:
                    label.new(bar_index, trade.exitPrice, trade.reason + ' ' + fmt(realized) + 'R', style=label.style_label_down if trade.dir == 1 else label.style_label_up, color=bullColor if realized > 0 else bearColor if realized < 0 else neutralColorInput, textcolor=color.white, size=size.tiny, tooltip='Model exit ' + price(trade.exitPrice) + '\nGross ' + fmt(trade.grossR) + 'R / costs ' + fmt(trade.costR) + 'R\nMFE/MAE lower bounds ' + fmt(trade.mfe) + '/' + fmt(trade.mae) + 'R\n' + ('Ambiguous OHLC: old stop first' if trade.ambiguous else 'Confirmed bar model'))

        if signal != 0 and (not trade.active):
            e, st, r, t1, t2, t3, cap, valid, origin = makePlan(signal)
            trade = Trade(active=True, dir=signal, id=instanceTag + ':' + syminfo.tickerid + ':' + timeframe.period + ':' + string.tostring(time_close), entryBar=bar_index, entryTime=time_close, entry=e, initialStop=st, stop=st, risk=r, tp1=t1, tp2=t2, tp3=t3, score=bullScore if signal == 1 else bearScore, maxScore=scoreMax, grade=gradeOf((bullScore if signal == 1 else bearScore) / scoreMax), regime=regime, origin=origin)
            trade.costR = sideCost(e) / r
            firstEntryAt = time_close if na(firstEntryAt) else firstEntryAt
            confirmedBuy = signal == 1
            confirmedSell = signal == -1
            event(trade, events, texts, 'entry', e, alertEntry)
            if showSignals:
                label.new(bar_index, low if signal == 1 else high, directionName(signal) + (' ' + trade.grade if showGradeInput else ''), style=label.style_label_up if signal == 1 else label.style_label_down, color=bullColor if signal == 1 else bearColor, textcolor=color.white, size=signalSize, tooltip='Entry ' + price(e) + ' | risk ' + price(r) + '\nEvidence ' + fmt(trade.score) + '/' + fmt(scoreMax) + '\n' + origin + '\n' + regimeName + '\nPartial TP1/2: ' + fmt(tp1Pct) + '% / ' + fmt(tp2Pct) + '%')

    if barstate.isconfirmed and array.size(events) > 0:
        payload: str = '{"schema_version":2,"script_version":"' + VERSION + '","instance":"' + escape(instanceTag) + '","ticker":"' + escape(syminfo.tickerid) + '","tf":"' + timeframe.period + '","execution_model":"close_entry_old_stop_first_next_bar_trail","events":[' + array.join(events, ',') + ']}'
        alert(payload if webhookInput else array.join(texts, '\n'), alert.freq_once_per_bar_close)

    alertcondition(confirmedBuy, 'Buy Signal', 'Confirmed BUY {{ticker}} {{interval}} at {{close}}')
    alertcondition(confirmedSell, 'Sell Signal', 'Confirmed SELL {{ticker}} {{interval}} at {{close}}')
    alertcondition(confirmedBuy and trade.grade == 'A+', 'Buy A+ only', 'BUY A+ {{ticker}} {{interval}}')
    alertcondition(confirmedSell and trade.grade == 'A+', 'Sell A+ only', 'SELL A+ {{ticker}} {{interval}}')
    alertcondition(confirmedBuy and (trade.grade == 'A+' or trade.grade == 'A'), 'Buy A+ and A', 'BUY A+/A {{ticker}} {{interval}}')
    alertcondition(confirmedSell and (trade.grade == 'A+' or trade.grade == 'A'), 'Sell A+ and A', 'SELL A+/A {{ticker}} {{interval}}')
    alertcondition(confirmedBuy and trade.grade != 'C', 'Buy B or better', 'BUY B+ {{ticker}} {{interval}}')
    alertcondition(confirmedSell and trade.grade != 'C', 'Sell B or better', 'SELL B+ {{ticker}} {{interval}}')
    alertcondition(tp1Event, 'TP1 Hit', 'Model TP1 {{ticker}} {{interval}} (bar close {{close}} is not fill price)')
    alertcondition(tp2Event, 'TP2 Hit', 'Model TP2 {{ticker}} {{interval}}')
    alertcondition(tp3Event, 'TP3 Hit', 'Model TP3 {{ticker}} {{interval}}')
    alertcondition(slEvent, 'Stop Hit', 'Model stop exit {{ticker}} {{interval}}')
    alertcondition(exitEvent, 'Position Closed', 'Model position closed {{ticker}} {{interval}}')
    alertcondition(stopEvent, 'Stop Changed', 'Model stop changed for NEXT bar {{ticker}} {{interval}}')
    alertcondition(cancelEvent, 'Candidate Cancelled', 'Candidate expired/cancelled {{ticker}} {{interval}}')
    alertcondition(confirmedBuy or confirmedSell, 'Any Signal', 'Confirmed entry {{ticker}} {{interval}}')

    dark: bool = theme == 'Dark' or (theme == 'Auto' and 0.2126 * color.r(chart.bg_color) + 0.7152 * color.g(chart.bg_color) + 0.0722 * color.b(chart.bg_color) < 128)
    textColor: Color = chart.fg_color if theme == 'Auto' else color.new('#E0E0E0') if dark else color.new('#1A1A1A')
    textMuted: Color = color.new('#9E9E9E') if dark else color.new('#757575')
    tableBg: Color = color.new(color.new('#131722') if dark else color.new('#FFFFFF'), panelAlpha)
    tableRowAlt: Color = color.new(color.new('#1C2030') if dark else color.new('#F0F4F8'), panelAlpha)
    tableBorder: Color = color.new('#2A2E39') if dark else color.new('#D0D0D0')
    headerText: Color = color.new('#FFFFFF')
    headerBull: Color = color.new('#0F6E56')
    headerBear: Color = color.new('#A32D2D')
    headerFlat: Color = color.new('#2962FF')
    bullText: Color = bullColor if dark else color.new('#006B45')
    bearText: Color = bearColor if dark else color.new('#A32330')
    neutralText: Color = neutralColorInput if dark else color.new('#F57F17')
    wmColor: Color = color.new(textColor, 80)
    pFast = plot(emaFast if showRibbon else na, 'EMA Fast', color=color.new(bullColor, 20), linewidth=2)
    pSlow = plot(emaSlow if showRibbon else na, 'EMA Slow', color=color.new(bearColor, 20), linewidth=2)
    fill(pFast, pSlow, color=color.new(bullColor if emaFast > emaSlow else bearColor, 88))
    plot(emaTrend if showRibbon else na, 'EMA Trend', color=textMuted)
    bgcolor(color.new(bullColor if trendDir == 1 else bearColor if trendDir == -1 else neutralColorInput, 94) if showBg else na)
    above: float = nearestAbove(close, priorDayHigh if timeframe.isintraday else na, sessionHigh if timeframe.isintraday and inSession else na, knownHigh)
    below: float = nearestBelow(close, priorDayLow if timeframe.isintraday else na, sessionLow if timeframe.isintraday and inSession else na, knownLow)
    plot(above if showLevels else na, 'Nearest resistance (known now)', color=color.new(bearColor, 35), style=plot.style_linebr)
    plot(below if showLevels else na, 'Nearest support (known now)', color=color.new(bullColor, 35), style=plot.style_linebr)

    levelLines: Persistent[list[Line]] = array.new_line()
    levelLabels: Persistent[list[Label]] = array.new_label()

    levelRightTime: int = time_close + cast_int(tfSeconds * 1000) * labelOffset if trade.active else trade.exitTime
    if confirmedBuy or confirmedSell:
        for ln in levelLines:
            line.delete(ln)
        for lb in levelLabels:
            label.delete(lb)
        array.clear(levelLines)
        array.clear(levelLabels)
        if showTPSL:
            for i in pine_range(0, 5):
                level: float = trade.entry if i == 0 else trade.initialStop if i == 1 else trade.tp1 if i == 2 else trade.tp2 if i == 3 else trade.tp3 if i == 4 else trade.stop
                col: Color = color.new('#2979FF') if i == 0 else bearColor if i == 1 else color.orange if i == 5 else bullColor
                array.push(levelLines, line.new(trade.entryTime, level, levelRightTime, level, xloc=xloc.bar_time, color=na if i == 5 and (not showTrail) else col, style=line.style_solid if i == 0 or i == 1 else line.style_dashed))
                array.push(levelLabels, label.new(levelRightTime, level, '', xloc=xloc.bar_time, style=label.style_label_left, color=color.new(col, 25), textcolor=color.white, size=size.tiny))
    if barstate.islast and array.size(levelLines) > 0:
        right: int = levelRightTime
        for i in pine_range(0, 5):
            ln: Line = array.get(levelLines, i)
            lb: Label = array.get(levelLabels, i)
            level: float = trade.entry if i == 0 else trade.initialStop if i == 1 else trade.tp1 if i == 2 else trade.tp2 if i == 3 else trade.tp3 if i == 4 else trade.stop
            name: str = 'ENTRY' if i == 0 else 'INITIAL SL' if i == 1 else 'STEP SL' + (' (next bar)' if stopEvent else '') if i == 5 else 'TP' + string.tostring(i - 1)
            hit: bool = trade.hit1 if i == 2 else trade.hit2 if i == 3 else trade.hit3 if i == 4 else False
            line.set_xy2(ln, right, level)
            if i == 5:
                line.set_y1(ln, level)
            if hit:
                line.set_style(ln, line.style_solid)
            label.set_xy(lb, right, level)
            label.set_text(lb, '' if i == 5 and (not showTrail) else name + (' ✓ ' if hit else ' ') + price(level) + ('' if trade.active else ' [closed]'))
            if i == 5 and (not showTrail):
                label.set_color(lb, na)

    def addData(rows: list[Row], key: str, value: str, col: Color, tip: str):
        return array.push(rows, Row(kind=0, key=key, value=value, col=col, tip=tip))

    def addSection(rows: list[Row], title: str):
        return array.push(rows, Row(kind=1, key=title))

    def addNote(rows: list[Row], note: str, col: Color):
        return array.push(rows, Row(kind=2, value=note, col=col))

    def renderRows(rows: list[Row], where: str, headerBg: Color):
        n: int = array.size(rows)
        tb: Table = table.new(pos(where), 2, math.max(n, 1), bgcolor=tableBg, border_color=tableBorder, border_width=1, frame_color=tableBorder, frame_width=1)
        dataIdx: int = 0
        if n > 0:
            for r in pine_range(0, n - 1):
                it: Row = array.get(rows, r)
                if it.kind == 3:
                    table.cell(tb, 0, r, it.value, text_color=headerText, bgcolor=headerBg, text_size=txtSize, text_halign=text.align_center)
                    table.merge_cells(tb, 0, r, 1, r)
                elif it.kind == 1:
                    table.cell(tb, 0, r, it.key, text_color=textMuted, bgcolor=tableRowAlt, text_size=size.tiny, text_halign=text.align_center)
                    table.merge_cells(tb, 0, r, 1, r)
                elif it.kind == 4:
                    table.cell(tb, 0, r, it.value, text_color=textMuted, bgcolor=tableBg, text_size=size.tiny, text_halign=text.align_center)
                    table.merge_cells(tb, 0, r, 1, r)
                else:
                    rb: Color = tableRowAlt if dataIdx % 2 == 1 else tableBg
                    dataIdx += 1
                    if it.kind == 2:
                        table.cell(tb, 0, r, it.value, text_color=it.col, bgcolor=rb, text_size=txtSize, text_halign=text.align_center)
                        table.merge_cells(tb, 0, r, 1, r)
                    else:
                        table.cell(tb, 0, r, it.key, text_color=textMuted, bgcolor=rb, text_size=txtSize, text_halign=text.align_left, tooltip=it.tip)
                        table.cell(tb, 1, r, it.value, text_color=it.col, bgcolor=rb, text_size=txtSize, text_halign=text.align_left, tooltip=it.tip)
        return tb

    def formStrip():
        s: str = ""
        n: int = math.min(FORM_LEN, array.size(journal))
        if n > 0:
            for j in pine_range(n - 1, 0):
                r: float = method_call(netR, array.get(journal, j))
                s += '▰' if r > 1e-08 else '▱' if r < -1e-08 else '▫'
        return s

    dash: Persistent[Table] = na(Table)
    logTable: Persistent[Table] = na(Table)
    watermark: Persistent[Table] = table.new(position.bottom_center, 1, 1)
    def groupText(index: int):
        n: int = array.get(groupN, index)
        value: str = fmt(array.get(groupR, index) / n) + 'R' if n > 0 else 'N/A'
        return string.tostring(n) + ' trades / ' + value + (' [small N]' if n < 30 else '')

    if barstate.islast:
        focusDir: int = pendingDir if pendingDir != 0 else trade.dir if trade.active else trendDir if trendDir != 0 else 1 if bullScore >= bearScore else -1
        _, sPlan, rPlan, _, _, _, capPlan, validPlan, originPlan = makePlan(focusDir)
        liveGate: int = gate(focusDir, validPlan, capPlan)
        liveScore: float = bullScore if focusDir == 1 else bearScore
        dataStatus: str = 'Warmup ' + string.tostring(bar_index) + '/' + string.tostring(warmupBars) if not warmed else 'Volume data missing — blocked' if not volumeReady else 'VWAP unavailable — blocked' if not vwapReady else 'HTF warmup/missing — blocked' if htfEnabled and (not htfReady or na(htfFast) or na(htfSlow)) else 'Missing/invalid price indicators — blocked' if not ready else 'Ready; no volume weights' if not hasVolume else 'Ready'

        signalStatus: str = "No new crossover"
        if confirmedBuy or confirmedSell:
            signalStatus = lastDecision
        elif pendingDir != 0:
            signalStatus = directionName(pendingDir) + ': ' + ('Conditions met; awaiting bar close' if liveGate == 0 else rejectReason(liveGate))
        elif bullCross or bearCross:
            if not barstate.isconfirmed:
                signalStatus = "Unconfirmed crossover"
            elif not dateAllowed:
                signalStatus = "Outside date window"
            elif not warmed:
                signalStatus = "Data not ready / warmup"
            else:
                signalStatus = lastDecision
        nextTP: float = trade.tp1 if not trade.hit1 else trade.tp2 if not trade.hit2 else trade.tp3 if not trade.hit3 else na
        unrealizedR: float = trade.remaining * trade.dir * (close - trade.entry) / trade.risk if trade.active else na

        roomDir: int = trade.dir if trade.active else focusDir
        roomLevel: float = above if roomDir == 1 else below
        refRisk: float = trade.risk if trade.active else rPlan
        roomR: float = math.abs(roomLevel - close) / refRisk if not na(roomLevel) and refRisk > 0 else na
        estimateEntry: float = manualEntry if manualEntry > 0 else close
        estimateStop: float = trade.stop if trade.active else sPlan
        estimateDir: int = trade.dir if trade.active else focusDir
        estimateRisk: float = estimateDir * (estimateEntry - estimateStop)
        estimatedCosts: float = sideCost(estimateEntry) + sideCost(estimateStop)
        riskBudget: float = riskCash if riskMode == 'Cash' else equityInput * riskPct / 100
        calcValid: bool = sizeEnabled and linearConfirmed and (accountCurrency == syminfo.currency) and (estimateRisk >= syminfo.mintick) and (not positiveOnly or math.min(estimateEntry, estimateStop) > 0) and (trade.active or (ready and validPlan))
        quantity: float = math.floor(riskBudget / ((estimateRisk + estimatedCosts) * pointValueInput) / lotStep) * lotStep if calcValid else na
        calcStatus: str = 'Off' if not sizeEnabled else 'Verify linear contract first' if not linearConfirmed else 'Currency mismatch: ' + syminfo.currency if accountCurrency != syminfo.currency else 'Invalid plan / stop side' if not calcValid else 'Below minimum quantity' if quantity < minQty else qtyFmt(quantity) + ' units; risk ' + fmt(quantity * (estimateRisk + estimatedCosts) * pointValueInput) + ' ' + accountCurrency
        estimatedCostR: float = estimatedCosts / estimateRisk if estimateRisk > 0 else na
        drift: float = trade.dir * (close - trade.entry) / trade.risk if trade.risk > 0 else na
        remainingRR: float = trade.dir * (nextTP - estimateEntry) / estimateRisk if trade.active and estimateRisk > 0 and (not na(nextTP)) and (trade.dir * (nextTP - estimateEntry) > 0) else na
        stopDistance: float = trade.dir * (close - trade.stop) if trade.active else na
        targetDistance: float = trade.dir * (nextTP - close) if trade.active and (not na(nextTP)) else na
        trendWord: str = 'Bullish' if trendDir == 1 else 'Bearish' if trendDir == -1 else 'Neutral'
        trendCol: Color = bullText if trendDir == 1 else bearText if trendDir == -1 else neutralText
        headerBg: Color = headerBull if trendDir == 1 else headerBear if trendDir == -1 else headerFlat

        if showDash:
            rows: list[Row] = array.new(0, NA(Row))
            array.push(rows, Row(kind=3, value='◆ PrecSniper · ' + trendWord))

            if showMarketSec:
                addSection(rows, '— Market —')
                addData(rows, 'Regime', regimeName, trendCol, 'ADX regime and EMA alignment on the current bar.')
                addData(rows, 'HTF', htfInput + ' ' + directionName(htfBias) + ' · ' + htfMode + ('' if na(htfClosedAt) else ' · closed ' + string.format_time(htfClosedAt, 'MM-dd HH:mm', sessionTZ)) if htfEnabled else 'Off', bullText if htfBias == 1 else bearText if htfBias == -1 else textColor, 'Bias of the last CLOSED higher-timeframe bar. Soft score adds 1.5 points; Hard filter blocks opposing entries.')
                addData(rows, 'Volatility', volatility + ' ' + fmt(volRatio) + 'x · ATR ' + fmt(atr / math.abs(close) * 100 if close != 0 else na) + '% · ' + volMode, bearText if highVol else textColor, 'ATR relative to its ' + string.tostring(ATR_MEAN_LEN) + '-bar mean, ATR as % of price, and the high-volatility action.')
                addData(rows, 'Session', 'Off' if sessionMode == 'Off' else ('Inside' if inSession else 'Outside') + ' · ' + sessionTZ + ' · ' + sessionMode, textColor, 'Trading window state in the session timezone.')
                addData(rows, 'Data', dataStatus + (' · last trade OHLC ambiguity' if trade.ambiguous else ''), textColor if ready else bearText, 'Warmup and data readiness. Entries are blocked until Ready.')
                addData(rows, 'Profile', preset + ' · EMA ' + string.tostring(fastLen) + '/' + string.tostring(slowLen) + '/' + string.tostring(trendLen) + ' · RSI ' + string.tostring(rsiLen) + ' · ATR ' + string.tostring(atrLen) + ' · SL ' + fmt(slMult) + 'x', textMuted, 'Effective parameter profile after preset resolution.')

            if showSignalSec:
                addSection(rows, '— Signal —')
                requiredPts: float = requiredRatio * scoreMax
                addData(rows, 'Candidate', signalStatus, bullText if liveGate == 0 else textMuted, 'Crossover candidate state and the first failing gate, evaluated live.')
                addData(rows, 'Evidence', fmt(liveScore) + '/' + fmt(scoreMax) + '  ' + buildGauge(liveScore, scoreMax, 8) + ' · need ' + fmt(requiredPts) + (' [closed]' if barstate.isconfirmed else ' [live]'), bullText if liveScore + 1e-09 >= requiredPts else neutralText, 'Optional evidence for the focused side vs the required minimum. Grade thresholds: A+ 80%, A 65%, B 50%.')
                addData(rows, 'Plan', directionName(focusDir) + ' · SL ' + price(sPlan) + ' · risk ' + price(rPlan) + ' · ' + originPlan, textColor if validPlan else bearText, 'Stop, initial risk and stop origin the model would use for an entry at the current close.')
                addData(rows, 'Est. cost', fmt(estimatedCostR) + 'R' + (' [high vs stop]' if estimatedCostR >= costWarningR else '') + ' · manual inputs', bearText if estimatedCostR >= costWarningR else textColor, 'Round-trip commission, spread and slippage as a fraction of initial risk.')
                addData(rows, 'Last decision', lastDecision, textMuted, 'Outcome of the most recent candidate.')

            if showTradeSec:
                addSection(rows, '— Trade —')
                if trade.active:
                    stepped: bool = trade.stop != trade.initialStop
                    addData(rows, 'Position', directionName(trade.dir) + ' · ' + string.tostring(bar_index - trade.entryBar) + ' bars · ' + fmt(trade.remaining * 100) + '% left', bullText if trade.dir == 1 else bearText, 'Open model position and the remaining fraction after partial exits.')
                    addData(rows, 'Entry', price(trade.entry) + ' · ' + trade.grade + ' · ' + fmt(trade.score) + '/' + fmt(trade.maxScore) + ' · ' + trade.origin, textColor, 'Entry price, grade, evidence and stop origin at entry. ' + ('' if na(trade.entryTime) else string.format_time(trade.entryTime, 'yyyy-MM-dd HH:mm', sessionTZ) + ' ' + sessionTZ))
                    addData(rows, 'Stop', ('Step @ ' if stepped else '') + price(trade.stop) + (' (next bar)' if stopEvent else '') + ' · initial ' + price(trade.initialStop) + (' · step ON' if trailInput else ' · step OFF'), neutralText if stepped else bearText, 'Effective stop. Step changes apply from the NEXT bar. Entry-price stop is not net breakeven after costs.')
                    addData(rows, 'TP1', ('✓ ' if trade.hit1 else '') + price(trade.tp1) + ' · ' + fmt(tp1Pct) + '%', bullText if trade.hit1 else textColor, '✓ = touched. Percent = partial close of the original position.')
                    addData(rows, 'TP2', ('✓ ' if trade.hit2 else '') + price(trade.tp2) + ' · ' + fmt(tp2Pct) + '%', bullText if trade.hit2 else textColor, '✓ = touched. Percent = partial close of the original position.')
                    addData(rows, 'TP3', ('✓ ' if trade.hit3 else '') + price(trade.tp3) + (' · closes rest' if fullTP3 else ' · holds rest'), bullText if trade.hit3 else textColor, "Final target. With 'Close remaining position at TP3' the trade ends here.")
                    addData(rows, 'Unrealized', fmt(unrealizedR) + 'R gross · realized ' + fmt(netR(trade)) + 'R net', bullText if unrealizedR > 0 else bearText if unrealizedR < 0 else textColor, 'Open P/L in R on the remaining fraction, and realized net R from partial fills.')
                    addData(rows, 'Distances', price(stopDistance) + ' / ' + price(targetDistance) + ' · ' + fmt(stopDistance / trade.risk) + 'R / ' + fmt(targetDistance / trade.risk) + 'R · ' + fmt(stopDistance / math.abs(close) * 100 if close != 0 else na) + '% / ' + fmt(targetDistance / math.abs(close) * 100 if close != 0 else na) + '%', textColor, 'Live distance to the stop / to the next target: price, R, percent.')
                    addData(rows, 'Room', directionName(roomDir) + ' · ' + price(roomLevel) + ' · ' + fmt(roomR) + 'R' + (' (none tracked)' if na(roomLevel) else ''), textColor, 'Nearest known level in the trade direction and its distance in R from live price.')
                    addData(rows, 'Drift', fmt(drift) + 'R' + (' [extended]' if drift >= lateR else '') + ' · hyp. R:R ' + fmt(remainingRR), neutralText if drift >= lateR else textColor, 'Price drift from entry in R. Hypothetical R:R = next target vs stop for an entry at the live price, not the original trade R.')
                else:
                    addNote(rows, 'Flat · waiting for a crossover', textMuted)
                    if trade.dir != 0:
                        lastR: float = netR(trade)
                        addData(rows, 'Last trade', directionName(trade.dir) + ' · ' + trade.reason + ' · ' + fmt(lastR) + 'R' + (' [amb]' if trade.ambiguous else ''), bullText if lastR > 0 else bearText if lastR < 0 else textColor, 'Most recent closed model trade.')
                    addData(rows, 'Room', directionName(roomDir) + ' [plan] · ' + price(roomLevel) + ' · ' + fmt(roomR) + 'R' + (' (none tracked)' if na(roomLevel) else ''), textColor, 'Nearest known level for the planned side and its distance in planned R.')

            if sizeEnabled:
                addSection(rows, '— Sizing —')
                addData(rows, 'Estimate', calcStatus, textColor if calcValid else textMuted, 'Manual position estimate for linear instruments. Never rewrites the model trade.')
                addData(rows, 'Size / notional', qtyFmt(quantity) + ' / ' + fmt(quantity * math.abs(estimateEntry) * pointValueInput) + ' ' + accountCurrency + ' (not margin)' if calcValid and quantity >= minQty else 'N/A', textMuted, 'Quantity from the risk budget, and notional value at the estimate entry.')

            if showStats:
                addSection(rows, '— Stats —')
                winRate: float = 100.0 * wins / total if total > 0 else na
                form: str = formStrip()
                addData(rows, 'Closed', string.tostring(total) + ' · ' + string.tostring(wins) + 'W / ' + string.tostring(losses) + 'L / ' + string.tostring(breakevens) + 'BE', textColor, 'Closed model trades in the requested window.')
                addData(rows, 'Win rate', fmt(winRate) + '%  ' + buildGauge(winRate, 100, 8) if total > 0 else 'N/A', textMuted if total == 0 else bullText if winRate >= 55 else neutralText if winRate >= 45 else bearText, 'Wins / closed trades. Net R above zero counts as a win.')
                addData(rows, 'Expectancy / PF', fmt(totalR / total) + 'R / ' + (fmt(grossWin / grossLoss) if grossLoss > 0 else 'no losses' if grossWin > 0 else 'N/A') if total > 0 else 'N/A', textMuted if total == 0 else bullText if totalR > 0 else bearText if totalR < 0 else textColor, 'Average net R per closed trade, and gross profit / gross loss.')
                addData(rows, 'Net / max DD', fmt(totalR) + 'R / ' + fmt(maxDrawdownR) + 'R', bullText if totalR > 0 else bearText if totalR < 0 else textColor, 'Net total R and the largest peak-to-trough drop of closed-trade equity.')
                addData(rows, 'Avg win / loss / streak', fmt(grossWin / wins if wins > 0 else na) + 'R / ' + fmt(grossLoss / losses if losses > 0 else na) + 'R / ' + string.tostring(maxLossStreak), textColor, 'Average winning R, average losing R, longest losing streak.')
                addData(rows, 'Duration / ambiguous', fmt(1.0 * totalDuration / total if total > 0 else na) + ' bars / ' + string.tostring(ambiguousTrades), textColor, 'Average bars per trade, and trades where stop and target touched on the same bar (old stop first).')
                addData(rows, 'TP1 / TP2 reach', fmt(100.0 * reachedTP1 / total if total > 0 else na) + '% / ' + fmt(100.0 * reachedTP2 / total if total > 0 else na) + '%', textColor, 'Share of closed trades that touched TP1 / TP2.')
                addData(rows, 'MFE / MAE', fmt(totalMFE / total if total > 0 else na) + 'R / ' + fmt(totalMAE / total if total > 0 else na) + 'R', textMuted, 'Average maximum favorable / adverse excursion, lower bounds from OHLC.')
                addData(rows, 'Form', 'N/A' if form == '' else form, textColor, 'Last ' + string.tostring(FORM_LEN) + ' closed trades, newest on the right. ▰ win · ▱ loss · ▫ break-even.')
                addData(rows, 'Window / costs', string.format_time(startInput, 'yyyy-MM-dd', sessionTZ) + '..' + string.format_time(endInput, 'yyyy-MM-dd', sessionTZ) + ' · ' + ('manual costs ON' if commissionPct + spreadTicks + slipTicks > 0 else 'costs OFF'), textMuted, 'Requested statistics window and whether manual costs are applied.')

            if showDiagSec:
                addSection(rows, '— Diagnostics —')
                addData(rows, 'Factors', 'Trend/RSI/MACD/Accel/ADX = 1 each · Vol/VWAP = 1 · soft HTF = 1.5', textMuted, 'Weights of the optional evidence factors for the focused side.')
                addData(rows, 'Trend / RSI / MACD / accel', ('1' if focusDir * (close - emaTrend) > 0 else '0') + ' / ' + ('1' if (rsi > 50 and rsi < RSI_UPPER if focusDir == 1 else rsi < 50 and rsi > RSI_LOWER) else '0') + ' / ' + ('1' if focusDir * hist > 0 else '0') + ' / ' + ('1' if focusDir * (hist - hist[1]) > 0 else '0'), textColor, 'Live factor states for the focused side.')
                addData(rows, 'ADX / volume / VWAP / HTF', ('1' if trending and focusDir * (diPlus - diMinus) > 0 else '0') + ' / ' + (('1' if volAbove else '0') if hasVolume else 'N/A') + ' / ' + (('1' if focusDir * (close - vwap) > 0 else '0') if vwapEnabled and hasVolume else 'OFF') + ' / ' + (directionName(htfBias) if htfEnabled else 'OFF'), textColor, 'Live factor states for the focused side.')
                addData(rows, 'Candidates / accepted / pending', string.tostring(candidates) + ' / ' + string.tostring(accepted) + ' / ' + ('1' if pendingDir != 0 else '0'), textColor, 'Crossover candidates seen, entries accepted, candidate pending now.')
                reasons: str = ""
                for k in pine_range(0, 11):
                    n: int = array.get(rejected, k)
                    if n > 0:
                        reasons += ('' if reasons == '' else '; ') + ('opposite cross/already open' if k == 0 else rejectReason(k)) + '=' + string.tostring(n)
                addData(rows, 'Rejections', 'None' if reasons == '' else reasons, textMuted, 'One final rejection reason per candidate.')
                addData(rows, 'Long / Short', groupText(0) + ' | ' + groupText(1), textColor, 'Count and average net R by direction.')
                addData(rows, 'A+ / A', groupText(2) + ' | ' + groupText(3), textColor, 'Count and average net R by grade.')
                addData(rows, 'B / C', groupText(4) + ' | ' + groupText(5), textColor, 'Count and average net R by grade.')
                addData(rows, 'Range / Trend / Mixed', groupText(6) + ' | ' + groupText(7) + ' | ' + groupText(8), textColor, 'Count and average net R by regime at entry.')
                addData(rows, 'First entry / last exit', ('N/A' if na(firstEntryAt) else string.format_time(firstEntryAt, 'yyyy-MM-dd', sessionTZ)) + ' / ' + ('N/A' if na(lastExitAt) else string.format_time(lastExitAt, 'yyyy-MM-dd', sessionTZ)), textMuted, 'Observed span of model trades on the loaded history.')

            array.push(rows, Row(kind=4, value='Precision Sniper · ' + VERSION + ' · model, not broker fills'))
            if not na(dash):
                table.delete(dash)
            dash = renderRows(rows, dashPos, headerBg)

        if showJournal:
            shown: int = math.min(journalRows, array.size(journal))
            if not na(logTable):
                table.delete(logTable)
            logTable = table.new(pos(journalPos), 7, shown + (3 if shown == 0 else 2), bgcolor=tableBg, border_color=tableBorder, border_width=1, frame_color=tableBorder, frame_width=1)
            table.cell(logTable, 0, 0, '◆ Recent model trades', text_color=headerText, bgcolor=headerBg, text_size=txtSize, text_halign=text.align_center)
            table.merge_cells(logTable, 0, 0, 6, 0)
            headers: list[str] = array.from_items('Entry ' + sessionTZ, 'Side / grade', 'Entry', 'Exit', 'Reason', 'Bars', 'Net R')
            for col in pine_range(0, 6):
                table.cell(logTable, col, 1, array.get(headers, col), bgcolor=tableRowAlt, text_color=textMuted, text_size=size.tiny, text_halign=text.align_center)
            if shown == 0:
                table.cell(logTable, 0, 2, 'No closed model trades yet', bgcolor=tableBg, text_color=textMuted, text_size=txtSize, text_halign=text.align_center)
                table.merge_cells(logTable, 0, 2, 6, 2)
            else:
                for j in pine_range(0, shown - 1):
                    item: Trade = array.get(journal, j)
                    itemR: float = netR(item)
                    rb: Color = tableRowAlt if j % 2 == 1 else tableBg
                    rc: Color = bullText if itemR > 0 else bearText if itemR < 0 else textColor
                    cells: list[str] = array.from_items(string.format_time(item.entryTime, 'MM-dd HH:mm', sessionTZ), directionName(item.dir) + ' ' + item.grade, price(item.entry), price(item.exitPrice), item.reason + (' [amb]' if item.ambiguous else ''), string.tostring(item.exitBar - item.entryBar), fmt(itemR) + 'R')
                    for col in pine_range(0, 6):
                        table.cell(logTable, col, j + 2, array.get(cells, col), bgcolor=rb, text_color=rc if col == 6 else textColor, text_size=txtSize, text_halign=text.align_left if col == 0 or col == 4 else text.align_right)
        if showWatermark:
            table.cell(watermark, 0, 0, 'WillyAlgoTrader · ' + VERSION + ' · model, not broker fills', text_color=wmColor, text_size=size.normal, text_halign=text.align_center)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
