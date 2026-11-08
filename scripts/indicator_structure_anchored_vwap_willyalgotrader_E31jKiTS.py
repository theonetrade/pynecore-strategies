"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_float
from pynecore.core.pine_method import method
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, array, bar_index, barstate, bgcolor, chart, close, color, display,
    extend, format, high, hl2, input, label, line, location, low, math, na, nz, open, plot,
    plotshape, polyline, position, script, shape, size, string, syminfo, ta, table, text, time,
    timeframe, timestamp, volume, xloc, yloc
)
from pynecore.types import Color, Label, Line, NA, Persistent, Polyline, Series, Table
from pynecore.types.chart import ChartPoint


@udt
class Leg:
    dir: int = na(int)
    anchor: int = na(int)
    trail: list[ChartPoint] = na(list)
    hi1: list[ChartPoint] = na(list)
    lo1: list[ChartPoint] = na(list)
    hi2: list[ChartPoint] = na(list)
    lo2: list[ChartPoint] = na(list)
    anchorPx: float = na(float)
    curve: Polyline = na(Polyline)
    band1: Polyline = na(Polyline)
    band2: Polyline = na(Polyline)
    vwap: float = na(float)
    sigma: float = na(float)
    hitNow: bool = False

    volUp: float = 0.0
    volDn: float = 0.0
    away: int = 0
    retests: int = 0
    volUpC: float = 0.0
    volDnC: float = 0.0
    awayC: int = 0
    retestsC: int = 0


@udt
class Memo:
    ln: Line = na(Line)
    y: float = na(float)
    col: Color = na(Color)
    alive: bool = True


GRP_MAIN: str = "⚙️ Main Settings"
GRP_VWAP: str = "📐 Anchored VWAP"
GRP_BANDS: str = "📏 Deviation Bands"
GRP_SIGNAL: str = "🎯 Signals & Levels"
GRP_RISK: str = "🛡️ Risk Management"
GRP_VISUAL: str = "🎨 Visual"
GRP_DASH: str = "📊 Dashboard"
GRP_ALERT: str = "🔔 Alerts"
GRP_COLORS: str = "🎨 Colors"


@script.indicator(title="Structure-Anchored VWAP [WillyAlgoTrader]", shorttitle="SA-VWAP [WAT]", overlay=True, max_bars_back=5000, max_lines_count=500, max_labels_count=500, max_polylines_count=100, na_bool=True)
def main(
    pivLInput=input.int(55, "Pivot strength   left", minval=1, maxval=200, inline="piv", group=GRP_MAIN),
    pivRInput=input.int(55, "right", minval=1, maxval=200, inline="piv", group=GRP_MAIN, tooltip='A swing high needs this many lower highs on each side (same idea for lows).\n' + '• Right = confirmation delay in bars — a pivot is only known that many bars later\n' + '• 5/5 scalping | 20/20 intraday | 55/55 default, large swings\n' + '• Higher = fewer, more significant legs'),
    minAmpInput=input.float(1.5, "Minimum swing size (x ATR)", minval=0.0, maxval=10.0, step=0.25, group=GRP_MAIN, tooltip='A new pivot must sit at least this far from the previous opposite pivot.\n' + '• Filters noise inside ranges\n' + '• 0 = off | 1.5 = recommended | 3.0+ = only large swings'),
    atrLenInput=input.int(13, "ATR Length", minval=2, maxval=100, group=GRP_MAIN, tooltip='ATR period used by the swing-size filter and the equal-high/low tolerance.\n' + '• Lower = filter reacts faster to volatility changes\n• Recommended: 10-20'),
    anchorModeInput=input.string("Swing", "Re-anchor on", options=("Swing", "Structure break", "Fast", "Manual"), group=GRP_MAIN, tooltip='Swing: a new leg starts at every confirmed pivot (delay = right bars).\n' + 'Structure break: a new leg starts only when price closes beyond the previous swing (BOS); ' + 'the anchor is the extreme that preceded the break. Fewer, cleaner legs.\n' + 'Fast: no confirmation. The bar printing the highest high (lowest low) of the lookback is a new ' + 'extreme; the leg flips as soon as an extreme opposite to the previous one appears and is anchored ' + 'at that previous extreme. Immediate reaction, more sensitive to noise.\n' + 'Manual: one leg from the date and time below — behaves like the built-in Anchored VWAP tool.'),
    fastLenInput=input.int(30, "Fast mode: extreme lookback (bars)", minval=2, maxval=500, group=GRP_MAIN, tooltip="Used by the Fast mode only.\n• Larger = fewer, bigger legs\n• Smaller = flips more often"),
    eqTolInput=input.float(0.1, "Equal high/low tolerance (x ATR)", minval=0.0, maxval=2.0, step=0.05, group=GRP_MAIN, tooltip='Two pivots closer than this are labelled EQH / EQL instead of HH / LL.\n' + '• 0 = never label equal highs/lows\n• Recommended: 0.05-0.25'),
    manualTimeInput=input.time(timestamp('2026-09-01 00:00 +0000'), "Manual anchor (date & time)", group=GRP_MAIN, tooltip='Manual mode only. The leg starts at the first bar at or after this time.\n' + "Shown in the chart's timezone, so 00:00 UTC appears as 05:00 on a UTC+5 chart."),
    srcInput: Series[float] = input.source(hl2, "Price source", group=GRP_VWAP, tooltip='Price used inside the VWAP.\n' + '• hl2 = (H+L)/2 — matches the built-in Anchored VWAP tool\n' + '• hlc3 = typical price, gives closes more weight\n• close = most reactive'),
    weightModeInput=input.string("Cumulative", "Weighting", options=("Cumulative", "Half-life"), group=GRP_VWAP, tooltip='Cumulative: a true anchored VWAP — every bar of the leg keeps its full weight.\n' + 'Half-life: older bars fade, their weight halves every N bars. Hugs price on long legs; ' + 'not a textbook VWAP, but useful on instruments without volume.'),
    halfLifeInput=input.int(21, "Half-life (bars)", minval=1, maxval=500, group=GRP_VWAP, tooltip="Half-life weighting only. After this many bars a bar's weight is halved.\n" + '• Lower = line clings to price\n• Higher = closer to a plain VWAP'),
    clampVolInput=input.bool(True, "Clamp volume spikes at", inline="clamp", group=GRP_VWAP),
    clampMultInput=input.float(4.0, "x median", minval=1.0, maxval=50.0, step=0.5, inline="clamp", group=GRP_VWAP, tooltip='Bars with volume above N x the 50-bar median are counted at the cap, so a single print ' + 'cannot drag the whole VWAP.\n• 4 = recommended for crypto\n• Turn off for clean futures data'),
    maxLegBarsInput=input.int(4000, "Max leg length (bars)", minval=100, maxval=4900, group=GRP_VWAP, tooltip='A leg longer than this rolls its anchor forward one bar at a time, so the calculation ' + 'stays bounded on very old anchors. Lower it if the script feels slow.'),
    showB1Input=input.bool(True, "Band 1", inline="b1", group=GRP_BANDS),
    mult1Input=input.float(0.5, "Sigma", minval=0.1, maxval=10.0, step=0.1, inline="b1", group=GRP_BANDS, tooltip='Inner band, in volume-weighted standard deviations of price around the anchored VWAP, ' + 'measured over the leg itself.\n• 0.5 = value area edge\n• 1.0 = classic 1 sigma'),
    showB2Input=input.bool(False, "Band 2", inline="b2", group=GRP_BANDS),
    mult2Input=input.float(2.0, "Sigma", minval=0.1, maxval=10.0, step=0.1, inline="b2", group=GRP_BANDS, tooltip='Outer band. Also defines the Premium / Discount extremes used by the dashboard and alerts.\n' + '• 2.0 = statistically stretched\n• 2.5-3.0 = only true extremes'),
    fillTInput=input.int(90, "Fill transparency", minval=50, maxval=99, step=1, group=GRP_BANDS, tooltip="Transparency of the band fill.\n• 90 = subtle (recommended)\n• 99 = outline only"),
    retestMinAwayInput=input.int(5, "Bars away before a retest counts", minval=1, maxval=100, group=GRP_SIGNAL, tooltip="Price must stay on the leg's side of the VWAP, outside the touch tolerance, for this many " + 'bars before a touch counts as a retest entry.\n• Higher = fewer, cleaner signals'),
    retestTolInput=input.float(0.25, "Touch tolerance (x sigma)", minval=0.0, maxval=3.0, step=0.05, group=GRP_SIGNAL, tooltip='How close price must come to the VWAP to count as a touch, in sigma.\n' + '• 0 = the bar must cross the line exactly\n• 0.25 = recommended'),
    showMemoInput=input.bool(True, "VWAP memory levels", group=GRP_SIGNAL, tooltip='When a leg ends, its last VWAP value stays on the chart as a dashed level until price ' + 'trades through it. Old anchored VWAPs often keep acting as support and resistance.'),
    memoMaxInput=input.int(4, "Max memory levels", minval=1, maxval=20, group=GRP_SIGNAL, tooltip="How many untouched memory levels to keep. Older ones are dropped first."),
    memoKeepInput=input.bool(False, "Keep crossed levels (dotted)", group=GRP_SIGNAL, tooltip="On: a level price has traded through stays as a faded dotted line.\nOff: it is removed."),
    riskPresetInput=input.string("Balanced", "Risk Preset", options=("Conservative", "Balanced", "Aggressive", "Scalping", "Custom"), group=GRP_RISK, tooltip='Quick risk presets (SL ×ATR / TP1 / TP2 / TP3 in R):\n' + '• Conservative: 2.5 / 1R / 2R / 4R\n' + '• Balanced: 1.5 / 1R / 2R / 3R\n' + '• Aggressive: 1.0 / 1.5R / 2.5R / 4R\n' + '• Scalping: 0.8 / 0.8R / 1.5R / 2R\n' + '• Custom: use manual inputs below'),
    atrLenRiskInput=input.int(13, "ATR Length (SL)", minval=5, maxval=50, group=GRP_RISK, tooltip="ATR period for stop-loss distance.\n14 = standard on most timeframes"),
    slMultInput=input.float(1.5, "SL ×ATR (Custom)", minval=0.5, maxval=5.0, step=0.1, group=GRP_RISK, tooltip="Custom stop distance = ATR × this. Used only when preset = Custom"),
    tp1MultInput=input.float(1.0, "TP1 ×Risk (Custom)", minval=0.5, maxval=5.0, step=0.1, group=GRP_RISK, tooltip="TP1 as multiple of risk. 1.0 = 1:1 R:R"),
    tp2MultInput=input.float(2.0, "TP2 ×Risk (Custom)", minval=1.0, maxval=10.0, step=0.1, group=GRP_RISK, tooltip="TP2 as multiple of risk. 2.0 = 1:2 R:R"),
    tp3MultInput=input.float(3.0, "TP3 ×Risk (Custom)", minval=1.5, maxval=15.0, step=0.1, group=GRP_RISK, tooltip="TP3 as multiple of risk. 3.0 = 1:3 R:R"),
    showSlTpInput=input.bool(True, "Show SL/TP Lines", group=GRP_RISK, tooltip='Draw stop and take-profit lines after each entry.\n' + "Lines persist showing the last trade's outcome until the next entry."),
    showSlTpLabelsInput=input.bool(True, "Show SL/TP Labels", group=GRP_RISK, tooltip="Show price labels on the SL/TP lines"),
    showPctOnLabelsInput=input.bool(True, "Show % Distance on Labels", group=GRP_RISK, tooltip="Append % distance from entry to SL/TP labels.\nExample: 'SL 78120.5 (-0.36%)'."),
    useBreakEvenInput=input.bool(True, "Break-Even After TP1", group=GRP_RISK, tooltip='When TP1 is hit, move stop-loss to entry price.\n' + 'From the next bar onward, any wick touching entry closes the\n' + 'trade at break-even. (TP1 still counts as a WIN.)'),
    entryLineStyleInput=input.string("Dotted", "Entry Line Style", options=("Solid", "Dashed", "Dotted"), group=GRP_RISK, tooltip="Entry is a REFERENCE, not an action level — keep it subtle."),
    slLineStyleInput=input.string("Solid", "SL Line Style", options=("Solid", "Dashed", "Dotted"), group=GRP_RISK, tooltip="SL is the most critical risk level — keep it visually prominent."),
    tpLineStyleInput=input.string("Dashed", "TP Line Style", options=("Solid", "Dashed", "Dotted"), group=GRP_RISK, tooltip="Style for TP1/TP2/TP3.\nOn hit, a TP line turns solid teal regardless."),
    themeInput=input.string("Auto", "Theme", options=("Auto", "Dark", "Light"), group=GRP_VISUAL, tooltip="Chart color theme.\n• Auto: detect from chart background\n• Dark / Light: force manually"),
    showSignalsInput=input.bool(True, "Show Buy/Sell Signals", group=GRP_VISUAL, tooltip="Print Long ▲ / Short ▼ markers when a trade opens on a VWAP retest"),
    showLabelsInput=input.bool(True, "Show HH/HL/LH/LL", inline="lbl", group=GRP_VISUAL),
    lblSizeInput=input.string("small", "", options=("tiny", "small", "normal"), inline="lbl", group=GRP_VISUAL, tooltip="Label every confirmed pivot with its structure type, and its size."),
    labelFontSizeInput=input.string("Small", "SL/TP Label Font Size", options=("Tiny", "Small", "Normal", "Large", "Huge"), group=GRP_VISUAL, tooltip="Font size for SL/TP/Entry labels. Use Tiny for a compact look."),
    showBgInput=input.bool(False, "Show Leg Background", group=GRP_VISUAL, tooltip="Tint the chart background with the current leg direction. Off by default to keep candles clean."),
    maxLegsInput=input.int(30, "Finished legs kept on chart", minval=1, maxval=45, group=GRP_VISUAL, tooltip="How many completed legs stay drawn. Lower it if the chart feels crowded or slow."),
    showWatermarkInput=input.bool(True, "Show Watermark", group=GRP_VISUAL, tooltip="Display 'WillyAlgoTrader' watermark on chart"),
    showDashInput=input.bool(True, "Show Dashboard", group=GRP_DASH, tooltip="Master toggle for the dashboard table"),
    dashPosStr=input.string("Top Right", "Dashboard Position", options=("Top Left", "Top Right", "Bottom Left", "Bottom Right", "Middle Right"), group=GRP_DASH),
    showMarketSecInput=input.bool(True, "  ├ Market section", group=GRP_DASH, tooltip="Trend, Signal, Strength, Last swing, Timeframe"),
    showVwapSecInput=input.bool(True, "  ├ VWAP section", group=GRP_DASH, tooltip="Anchor, VWAP value, distance in sigma and %, zone, volume balance"),
    showTradeSecInput=input.bool(True, "  ├ Trade section", group=GRP_DASH, tooltip="SL, TP1-3, R:R, SL distance. Collapses to one row when flat."),
    showStatsSecInput=input.bool(True, "  └ Stats section", group=GRP_DASH, tooltip="Trades, W/L, Win Rate (+gauge), recent Form"),
    webhookInput=input.bool(False, "Webhook JSON Format", group=GRP_ALERT, tooltip="Send alerts as JSON for webhook / autotrading integrations"),
    showSlHitAlertInput=input.bool(True, "Alert on SL Hit", group=GRP_ALERT, tooltip="Fire an alert when price hits the active stop-loss"),
    alertTpHitInput=input.bool(False, "Alert on TP / Break-Even", group=GRP_ALERT, tooltip="Fire alerts when TP1/TP2/TP3 are touched and on break-even."),
    alertStructInput=input.bool(False, "Alert on New Leg / VWAP Cross", group=GRP_ALERT, tooltip="Fire alerts when a new leg is anchored and when price closes across the VWAP."),
    bullColorInput=input.color(color.new('#00E676'), "Bull", inline="c1", group=GRP_COLORS),
    bearColorInput=input.color(color.new('#FF5252'), "Bear", inline="c1", group=GRP_COLORS),
    lineWInput=input.int(2, "VWAP line width", minval=1, maxval=5, group=GRP_COLORS, tooltip="Thickness of the anchored VWAP curve. 2 = recommended.")
):
    INDICATOR_VERSION: str = "v1.1.0"
    INDICATOR_NAME: str = "Structure-Anchored VWAP"
    BRAND_NAME: str = "WillyAlgoTrader"

    LINE_FORWARD_BARS: int = 20
    LINE_UPDATE_BARS: int = 5
    LABEL_OFFSET_BARS: int = 1
    BE_DIM_TRANSP: int = 70
    FORM_LEN: int = 10

    __block_result__ = na
    __switch__ = themeInput
    if __switch__ == "Dark":
        __block_result__ = True
    elif __switch__ == "Light":
        __block_result__ = False
    else:
        __block_result__ = color.r(chart.bg_color) < 128
    isDark = __block_result__

    BULL_COLOR = bullColorInput
    BEAR_COLOR = bearColorInput

    BULL_TEXT = color.new('#00E676') if isDark else color.new('#00A152')
    BEAR_TEXT = color.new('#FF5252') if isDark else color.new('#D32F2F')
    NEUTRAL_TEXT = color.new('#FFEB3B') if isDark else color.new('#F57F17')
    DISCOUNT_TEXT = color.new('#4FC3F7') if isDark else color.new('#0277BD')

    BULL_LABEL_TEXT: Color = color.new('#004D25')
    BEAR_LABEL_TEXT: Color = color.new('#FFFFFF')

    TEXT_COLOR = color.new('#E0E0E0') if isDark else color.new('#1A1A1A')
    TEXT_MUTED = color.new(color.new('#9E9E9E'), 0) if isDark else color.new(color.new('#757575'), 0)
    TABLE_BG = color.new(color.new('#131722'), 5) if isDark else color.new(color.new('#FFFFFF'), 5)
    TABLE_ROW_ALT = color.new(color.new('#1C2030'), 0) if isDark else color.new(color.new('#F0F4F8'), 0)
    TABLE_BORDER = color.new(color.new('#2A2E39'), 0) if isDark else color.new(color.new('#D0D0D0'), 0)
    HEADER_TEXT: Color = color.new('#FFFFFF')
    WM_COLOR = color.new(color.new('#FFFFFF'), 80) if isDark else color.new(color.new('#000000'), 80)

    HEADER_BG_BULL = color.new(color.new('#0F6E56'), 0)
    HEADER_BG_BEAR = color.new(color.new('#A32D2D'), 0)
    HEADER_BG_FLAT = color.new(color.new('#2962FF'), 0)

    SL_COLOR = color.new(color.new('#E57373'), 0) if isDark else color.new(color.new('#B71C1C'), 0)
    TP1_COLOR = color.new(color.new('#66BB6A'), 30) if isDark else color.new(color.new('#388E3C'), 30)
    TP2_COLOR = color.new(color.new('#66BB6A'), 40) if isDark else color.new(color.new('#388E3C'), 40)
    TP3_COLOR = color.new(color.new('#66BB6A'), 0) if isDark else color.new(color.new('#388E3C'), 0)
    ENTRY_COLOR = color.new(color.new('#5C8AAE'), 0) if isDark else color.new(color.new('#34495E'), 0)
    TP_LABEL_COLOR = color.new(color.new('#66BB6A'), 0) if isDark else color.new(color.new('#388E3C'), 0)
    TP_HIT_COLOR = color.new(color.new('#4DB6AC'), 0) if isDark else color.new(color.new('#00695C'), 0)
    BE_COLOR = color.new(color.new('#FFA726'), 0) if isDark else color.new(color.new('#E65100'), 0)
    LABEL_TEXT = color.new('#1A1A1A') if isDark else color.new('#FFFFFF')
    FORM_COLOR = color.new('#5C8AAE') if isDark else color.new('#34495E')

    def safeDiv(num: float, den: float, fallback: float):
        return num / den if den != 0 and (not na(num)) and (not na(den)) else fallback

    def fmtPrice(v: float):
        return '—' if na(v) else string.tostring(v, format.mintick)

    def fmtSigned(v: float, suffix: str):
        return '—' if na(v) else ('+' if v >= 0 else '') + string.tostring(v, '#.##') + suffix

    def formatPctFromEntry(level: float, entry: float):
        res: str = ""
        if showPctOnLabelsInput and (not na(level)) and (not na(entry)) and (entry != 0):
            pct: float = (level - entry) / entry * 100.0
            sign: str = '+' if pct >= 0 else ''
            res = ' (' + sign + string.tostring(pct, '#.##') + '%)'
        return res

    def buildGauge(value: float, maxVal: float, width: int):
        result: str = ""
        filled: int = 0 if maxVal <= 0 else math.round(math.min(width, math.max(0.0, value / maxVal * width)))
        for i in pine_range(0, width - 1):
            result += '▰' if i < filled else '▱'
        return result

    def lineStyleFromString(s: str):
        return line.style_dashed if s == 'Dashed' else line.style_dotted if s == 'Dotted' else line.style_solid

    def sizeFromString(s: str):
        return size.tiny if s == 'Tiny' else size.small if s == 'Small' else size.normal if s == 'Normal' else size.large if s == 'Large' else size.huge if s == 'Huge' else size.small

    def sizeOf(s: str):
        return size.tiny if s == 'tiny' else size.small if s == 'small' else size.normal

    def classify(cur: float, ref: float, isHigh: bool, tolAbs: float):
        tag: str = ""
        if na(ref):
            tag = 'H' if isHigh else 'L'
        elif math.abs(cur - ref) <= tolAbs:
            tag = 'EQH' if isHigh else 'EQL'
        elif cur > ref:
            tag = 'HH' if isHigh else 'HL'
        else:
            tag = 'LH' if isHigh else 'LL'
        return tag

    __block_result_1__ = na
    __switch__ = dashPosStr
    if __switch__ == "Top Left":
        __block_result_1__ = position.top_left
    elif __switch__ == "Top Right":
        __block_result_1__ = position.top_right
    elif __switch__ == "Bottom Left":
        __block_result_1__ = position.bottom_left
    elif __switch__ == "Bottom Right":
        __block_result_1__ = position.bottom_right
    elif __switch__ == "Middle Right":
        __block_result_1__ = position.middle_right
    else:
        __block_result_1__ = position.top_right
    dashPos = __block_result_1__

    entryLineStyle = lineStyleFromString(entryLineStyleInput)
    slLineStyle = lineStyleFromString(slLineStyleInput)
    tpLineStyle = lineStyleFromString(tpLineStyleInput)
    labelSize = sizeFromString(labelFontSizeInput)


    def newLeg(d: int, a: int):
        return Leg(d, a, array.new(0, NA(ChartPoint)), array.new(0, NA(ChartPoint)), array.new(0, NA(ChartPoint)), array.new(0, NA(ChartPoint)), array.new(0, NA(ChartPoint)))

    def contour(top: list[ChartPoint], bottom: list[ChartPoint]):
        out: list[ChartPoint] = array.new(0, NA(ChartPoint))
        for i in pine_range(0, array.size(top) - 1):
            array.push(out, array.get(top, i))
        for i in pine_range(array.size(bottom) - 1, 0):
            array.push(out, array.get(bottom, i))
        return out

    settled: bool = barstate.isconfirmed
    atr: float = nz(ta.atr(atrLenInput), 0.0)

    WARMUP_BARS: int = math.max(pivLInput + pivRInput, 50)
    isWarmedUp: bool = bar_index >= WARMUP_BARS

    pivHi: float = ta.pivothigh(high, pivLInput, pivRInput)
    pivLo: float = ta.pivotlow(low, pivLInput, pivRInput)
    pivBar: int = bar_index - pivRInput
    minSwing: float = minAmpInput * atr
    eqTolAbs: float = eqTolInput * atr

    swType: Persistent[int] = 0
    swHi: Persistent[float] = na(float)
    swHiBar: Persistent[int] = na(int)
    swLo: Persistent[float] = na(float)
    swLoBar: Persistent[int] = na(int)
    refHi: Persistent[float] = na(float)
    refLo: Persistent[float] = na(float)
    swHiLbl: Persistent[Label] = na(Label)
    swLoLbl: Persistent[Label] = na(Label)
    lastStruct: Persistent[str] = "—"

    hiEvent: bool = False
    loEvent: bool = False
    hiExt: bool = False
    loExt: bool = False

    if settled and (not na(pivHi)):
        if swType == 1:
            if pivHi > swHi:
                swHi = pivHi
                swHiBar = pivBar
                hiEvent = True
                hiExt = True
        elif swType == 0 or pivHi - swLo >= minSwing:
            refHi = swHi
            swHi = pivHi
            swHiBar = pivBar
            swType = 1
            hiEvent = True

    if settled and (not na(pivLo)):
        if swType == -1:
            if pivLo < swLo:
                swLo = pivLo
                swLoBar = pivBar
                loEvent = True
                loExt = True
        elif swType == 0 or swHi - pivLo >= minSwing:
            refLo = swLo
            swLo = pivLo
            swLoBar = pivBar
            swType = -1
            loEvent = True

    if hiEvent:
        tag: str = classify(swHi, refHi, True, eqTolAbs)
        lastStruct = tag
        if hiExt:
            label.delete(swHiLbl)
        if showLabelsInput:
            swHiLbl = label.new(swHiBar, swHi, tag, xloc.bar_index, yloc.price, color.new(color.black, 100), label.style_label_down, BULL_TEXT if tag == 'HH' else NEUTRAL_TEXT, sizeOf(lblSizeInput), tooltip='Swing high ' + string.tostring(swHi, format.mintick) + '\nconfirmed after ' + string.tostring(pivRInput) + ' bars')

    if loEvent:
        tag: str = classify(swLo, refLo, False, eqTolAbs)
        lastStruct = tag
        if loExt:
            label.delete(swLoLbl)
        if showLabelsInput:
            swLoLbl = label.new(swLoBar, swLo, tag, xloc.bar_index, yloc.price, color.new(color.black, 100), label.style_label_up, BEAR_TEXT if tag == 'LL' else BULL_TEXT, sizeOf(lblSizeInput), tooltip='Swing low ' + string.tostring(swLo, format.mintick) + '\nconfirmed after ' + string.tostring(pivRInput) + ' bars')

    newHiN: bool = high >= ta.highest(high, fastLenInput)
    newLoN: bool = low <= ta.lowest(low, fastLenInput)

    extType: Persistent[int] = 0
    extHiBar: Persistent[int] = na(int)
    extLoBar: Persistent[int] = na(int)
    fastUp: bool = False
    fastDn: bool = False

    if settled and (newHiN or newLoN):
        bothWays: bool = newHiN and newLoN
        takeHi: bool = newHiN and (not bothWays or close >= open)
        takeLo: bool = newLoN and (not bothWays or close < open)
        if takeHi:
            extHiBar = bar_index
            fastUp = extType == -1
            extType = 1
        if takeLo:
            extLoBar = bar_index
            fastDn = extType == 1
            extType = -1

    hasVolume: Persistent[bool] = False
    hasVolume = hasVolume or nz(volume, 0.0) > 0

    px: float = nz(srcInput, close)
    volMed: float = nz(ta.median(volume, 50), 0.0)
    wRaw: float = nz(volume, 0.0) if hasVolume else 1.0
    wt: float = math.min(wRaw, volMed * clampMultInput) if clampVolInput and hasVolume and (volMed > 0) else wRaw

    lam: float = math.exp(-math.log(2.0) / halfLifeInput) if weightModeInput == 'Half-life' else 1.0

    cumW: Persistent[float] = 0.0
    cumPW: Persistent[float] = 0.0
    cumP2: Persistent[float] = 0.0
    cumW = lam * cumW + wt
    cumPW = lam * cumPW + px * wt
    cumP2 = lam * cumP2 + px * px * wt

    CAP: int = maxLegBarsInput + 2
    bufW: Persistent[list[float]] = array.new_float()
    bufPW: Persistent[list[float]] = array.new_float()
    bufP2: Persistent[list[float]] = array.new_float()
    bufC: Persistent[list[float]] = array.new_float()
    bufH: Persistent[list[float]] = array.new_float()
    bufL: Persistent[list[float]] = array.new_float()
    bufA: Persistent[list[float]] = array.new_float()
    bufBar: Persistent[int] = -1

    def record(buf: list[float], v: float):
        if bufBar == bar_index and array.size(buf) > 0:
            array.set(buf, array.size(buf) - 1, v)
        else:
            array.push(buf, v)
        if array.size(buf) > CAP:
            array.shift(buf)
        return array.size(buf)

    record(bufW, cumW)
    record(bufPW, cumPW)
    record(bufP2, cumP2)
    record(bufC, close)
    record(bufH, high)
    record(bufL, low)
    record(bufA, atr)
    bufBar = bar_index

    def hist(buf: list[float], back: int):
        out: float = na(float)
        idx: int = array.size(buf) - 1 - back
        if idx >= 0 and idx < array.size(buf):
            out = array.get(buf, idx)
        return out

    def legStats(back: int, aBack: int):
        f: float = 1.0 if lam == 1.0 else math.pow(lam, aBack - back + 1)
        v: float = hist(bufW, back) - f * nz(hist(bufW, aBack + 1))
        pw: float = hist(bufPW, back) - f * nz(hist(bufPW, aBack + 1))
        p2: float = hist(bufP2, back) - f * nz(hist(bufP2, aBack + 1))
        m: float = pw / v if v > 0 else na
        sd: float = math.sqrt(math.max(p2 / v - m * m, 0.0)) if v > 0 else 0.0
        return (m, sd)

    def extremeSince(fromBar: int, wantLow: bool):
        span: int = math.min(bar_index - nz(fromBar, bar_index - maxLegBarsInput), maxLegBarsInput)
        bestOff: int = 0
        bestVal: float = low if wantLow else high
        if span > 1:
            for i in pine_range(1, span - 1):
                v: float = hist(bufL, i) if wantLow else hist(bufH, i)
                if wantLow and v < bestVal or (not wantLow and v > bestVal):
                    bestVal = v
                    bestOff = i
        return bar_index - bestOff

    @method
    def erase(this: Leg):
        polyline.delete(this.curve)
        polyline.delete(this.band1)
        return polyline.delete(this.band2)

    @method
    def reset(this: Leg):
        array.clear(this.trail)
        array.clear(this.hi1)
        array.clear(this.lo1)
        array.clear(this.hi2)
        array.clear(this.lo2)
        this.volUp = 0.0
        this.volDn = 0.0
        this.away = 0
        this.retests = 0
        this.volUpC = 0.0
        this.volDnC = 0.0
        this.awayC = 0
        this.retestsC = 0
        return this.retestsC

    @method
    def putPoint(this: Leg, back: int, m: float, sd: float, commit: bool):
        x: int = bar_index - back

        if array.size(this.trail) > 0 and array.last(this.trail).index == x:
            array.pop(this.trail)
            if array.size(this.hi1) > 0 and array.last(this.hi1).index == x:
                array.pop(this.hi1)
                array.pop(this.lo1)
            if array.size(this.hi2) > 0 and array.last(this.hi2).index == x:
                array.pop(this.hi2)
                array.pop(this.lo2)
        array.push(this.trail, chart.point.from_index(x, m))
        if showB1Input:
            array.push(this.hi1, chart.point.from_index(x, m + sd * mult1Input))
            array.push(this.lo1, chart.point.from_index(x, m - sd * mult1Input))
        if showB2Input:
            array.push(this.hi2, chart.point.from_index(x, m + sd * mult2Input))
            array.push(this.lo2, chart.point.from_index(x, m - sd * mult2Input))

        wBar: float = hist(bufW, back) - lam * nz(hist(bufW, back + 1))
        cB: float = hist(bufC, back)
        hB: float = hist(bufH, back)
        lB: float = hist(bufL, back)
        above: bool = cB >= m
        this.volUp = this.volUpC + (wBar if above else 0.0)
        this.volDn = this.volDnC + (0.0 if above else wBar)
        tol: float = sd * retestTolInput if sd > 0 else nz(hist(bufA, back), 0.0) * 0.1
        touch: bool = lB <= m + tol and hB >= m - tol
        outside: bool = lB > m + tol if this.dir > 0 else hB < m - tol
        hit: bool = touch and this.awayC >= retestMinAwayInput
        this.away = 0 if touch else this.awayC + 1 if outside else 0
        this.retests = this.retestsC + (1 if hit else 0)
        this.hitNow = hit
        this.vwap = m
        this.sigma = sd
        __block_result_2__ = na
        if commit:
            this.volUpC = this.volUp
            this.volDnC = this.volDn
            this.awayC = this.away
            this.retestsC = this.retests
            __block_result_2__ = this.retestsC
        return __block_result_2__

    @method
    def rebuild(this: Leg):
        reset(this)
        aBack: int = math.min(bar_index - this.anchor, maxLegBarsInput)
        this.anchor = bar_index - aBack
        this.anchorPx = hist(bufL, aBack) if this.dir > 0 else hist(bufH, aBack)
        __block_result_3__ = na
        for i in pine_range(aBack, 0):
            m, s = legStats(i, aBack)
            __block_result_4__ = na
            if not na(m):
                __block_result_4__ = putPoint(this, i, m, s, i > 0 or settled)
            __block_result_3__ = __block_result_4__
        return __block_result_3__

    @method
    def advance(this: Leg):
        if bar_index - this.anchor > maxLegBarsInput:
            this.anchor = bar_index - maxLegBarsInput
            while array.size(this.trail) > 0 and array.first(this.trail).index < this.anchor:
                array.shift(this.trail)
            while array.size(this.hi1) > 0 and array.first(this.hi1).index < this.anchor:
                array.shift(this.hi1)
                array.shift(this.lo1)
            while array.size(this.hi2) > 0 and array.first(this.hi2).index < this.anchor:
                array.shift(this.hi2)
                array.shift(this.lo2)
        m, s = legStats(0, bar_index - this.anchor)
        __block_result_5__ = na
        if not na(m):
            __block_result_5__ = putPoint(this, 0, m, s, settled)
        return __block_result_5__

    @method
    def trimTo(this: Leg, lastBar: int):
        while array.size(this.trail) > 0 and array.last(this.trail).index > lastBar:
            array.pop(this.trail)
        while array.size(this.hi1) > 0 and array.last(this.hi1).index > lastBar:
            array.pop(this.hi1)
            array.pop(this.lo1)
        while array.size(this.hi2) > 0 and array.last(this.hi2).index > lastBar:
            array.pop(this.hi2)
            array.pop(this.lo2)
        this.vwap = array.last(this.trail).price if array.size(this.trail) > 0 else na
        return this.vwap

    @method
    def draw(this: Leg):
        erase(this)
        base: Color = BULL_COLOR if this.dir > 0 else BEAR_COLOR
        if showB2Input and array.size(this.hi2) >= 2:
            this.band2 = polyline.new(contour(this.hi2, this.lo2), False, True, xloc.bar_index, line_color=color.new(base, 85), fill_color=color.new(base, fillTInput), line_style=line.style_dotted, line_width=1)
        if showB1Input and array.size(this.hi1) >= 2:
            this.band1 = polyline.new(contour(this.hi1, this.lo1), False, True, xloc.bar_index, line_color=color.new(base, 70), fill_color=color.new(base, fillTInput), line_style=line.style_dotted, line_width=1)
        __block_result_6__ = na
        if array.size(this.trail) >= 2:
            this.curve = polyline.new(this.trail, False, False, xloc.bar_index, line_color=base, line_width=lineWInput)
            __block_result_6__ = this.curve
        return __block_result_6__

    memos: Persistent[list[Memo]] = array.new(0, NA(Memo))

    def memoCrossed(mm: Memo, atBar: int):
        mm.alive = False
        line.set_x2(mm.ln, atBar)
        __block_result_7__ = na
        if memoKeepInput:
            line.set_style(mm.ln, line.style_dotted)
            __block_result_7__ = line.set_color(mm.ln, color.new(mm.col, 75))
        else:
            __block_result_7__ = line.delete(mm.ln)
        return __block_result_7__

    def addMemo(y: float, fromBar: int, col: Color):
        __block_result_8__ = na
        if not na(y):
            mm: Memo = Memo(line.new(fromBar, y, bar_index, y, xloc.bar_index, extend.none, color.new(col, 35), line.style_dashed, 1), y, col)

            span: int = bar_index - fromBar
            if span > 1:
                for i in pine_range(span - 1, 1):
                    if hist(bufL, i) <= y and hist(bufH, i) >= y:
                        memoCrossed(mm, bar_index - i)
                        break
            __block_result_9__ = na
            if mm.alive or memoKeepInput:
                array.push(memos, mm)
                __block_result_10__ = na
                while array.size(memos) > memoMaxInput:
                    old: Memo = array.shift(memos)
                    __block_result_10__ = line.delete(old.ln)
                __block_result_9__ = __block_result_10__
            __block_result_8__ = __block_result_9__
        return __block_result_8__

    def updateMemos():
        __block_result_11__ = na
        if array.size(memos) > 0:
            __block_result_12__ = na
            for i in pine_range(array.size(memos) - 1, 0):
                mm: Memo = array.get(memos, i)
                __block_result_13__ = na
                if mm.alive:
                    line.set_x2(mm.ln, bar_index)
                    __block_result_14__ = na
                    if low <= mm.y and high >= mm.y:
                        memoCrossed(mm, bar_index)
                        __block_result_15__ = na
                        if not memoKeepInput:
                            __block_result_15__ = array.remove(memos, i)
                        __block_result_14__ = __block_result_15__
                    __block_result_13__ = __block_result_14__
                __block_result_12__ = __block_result_13__
            __block_result_11__ = __block_result_12__
        return __block_result_11__

    legDir: Persistent[int] = 0
    anchorBar: Persistent[int] = na(int)
    nextDir: int = 0
    nextAnchor: int = na(int)

    if anchorModeInput == 'Swing':
        if hiEvent or loEvent:
            nextDir = -1 if swType == 1 else 1
            nextAnchor = swHiBar if swType == 1 else swLoBar
    elif anchorModeInput == 'Fast':
        if fastUp:
            nextDir = 1
            nextAnchor = extLoBar
        elif fastDn:
            nextDir = -1
            nextAnchor = extHiBar
    elif anchorModeInput == 'Manual':
        if settled and time >= manualTimeInput and (nz(time[1], 0) < manualTimeInput):
            nextDir = 1
            nextAnchor = bar_index
    elif settled:
        brkUp: bool = legDir != 1 and (not na(swHi)) and (close > swHi)
        brkDn: bool = legDir != -1 and (not na(swLo)) and (close < swLo)
        if brkUp:
            nextDir = 1
            nextAnchor = extremeSince(swHiBar, True)
        elif brkDn:
            nextDir = -1
            nextAnchor = extremeSince(swLoBar, False)

    archive: Persistent[list[Leg]] = array.new(0, NA(Leg))
    live: Persistent[Leg] = na(Leg)
    reanchored: bool = False

    if not na(nextAnchor):
        reanchored = True
        if not na(live):
            trimTo(live, nextAnchor)
            draw(live)
            if showMemoInput and nextDir != live.dir:
                addMemo(live.vwap, nextAnchor, BULL_COLOR if live.dir > 0 else BEAR_COLOR)
            array.push(archive, live)
            while array.size(archive) > maxLegsInput:
                old: Leg = array.shift(archive)
                erase(old)
        live = newLeg(nextDir, nextAnchor)
        rebuild(live)
        legDir = nextDir
        anchorBar = live.anchor
    elif not na(live):
        advance(live)

    updateMemos()

    if not na(live) and barstate.islast:
        draw(live)

    vwapNow: Series[float] = na(float)
    sigNow: float = na(float)
    legBalance: float = na(float)
    legAnchorPx: float = na(float)
    legMove: float = na(float)
    legBars: int = 0
    legRetests: int = 0
    retestBull: bool = False
    retestBear: bool = False

    if not na(live):
        vwapNow = live.vwap
        sigNow = live.sigma
        legBars = bar_index - live.anchor
        legRetests = live.retests
        legAnchorPx = live.anchorPx
        legMove = safeDiv(close - nz(live.anchorPx, close), nz(live.anchorPx, close), 0.0) * 100.0
        legBalance = safeDiv(live.volUp, live.volUp + live.volDn, na) * 100.0
        retestBull = live.dir > 0 and live.hitNow
        retestBear = live.dir < 0 and live.hitNow

    up1: float = vwapNow + sigNow * mult1Input
    dn1: float = vwapNow - sigNow * mult1Input
    up2: float = vwapNow + sigNow * mult2Input
    dn2: float = vwapNow - sigNow * mult2Input

    distSig: float = safeDiv(close - nz(vwapNow, close), nz(sigNow, 0.0), na)
    distPct: float = safeDiv(close - nz(vwapNow, close), nz(vwapNow, close), 0.0) * 100.0

    zoneStr: str = '—' if na(distSig) else 'Premium' if distSig > mult2Input else 'Discount' if distSig < -mult2Input else 'Fair value'
    zoneCol: Color = NEUTRAL_TEXT if zoneStr == 'Premium' else DISCOUNT_TEXT if zoneStr == 'Discount' else TEXT_COLOR

    confirmedBuy: bool = retestBull and settled and isWarmedUp
    confirmedSell: bool = retestBear and settled and isWarmedUp

    evAnchorBull: bool = reanchored and legDir > 0 and settled and isWarmedUp
    evAnchorBear: bool = reanchored and legDir < 0 and settled and isWarmedUp

    hasPrevVwap: bool = not na(vwapNow) and (not na(vwapNow[1]))
    evCrossUp: bool = hasPrevVwap and (not reanchored) and (close > vwapNow) and (close[1] <= vwapNow[1]) and settled and isWarmedUp
    evCrossDn: bool = hasPrevVwap and (not reanchored) and (close < vwapNow) and (close[1] >= vwapNow[1]) and settled and isWarmedUp

    lastEventStr: Persistent[str] = "—"
    if evAnchorBull:
        lastEventStr = "New leg ▲"
    if evAnchorBear:
        lastEventStr = "New leg ▼"
    if confirmedBuy:
        lastEventStr = "Retest ▲"
    if confirmedSell:
        lastEventStr = "Retest ▼"

    balAlign: float = 50.0 if na(legBalance) else legBalance if legDir > 0 else 100.0 - legBalance
    scoreRaw: float = 0.0
    scoreRaw += balAlign * 0.4
    scoreRaw += 25.0 if legDir != 0 and (not na(distSig)) and (distSig * legDir > 0) else 0.0
    scoreRaw += 20.0 if not na(distSig) and math.abs(distSig) <= mult2Input else 0.0
    scoreRaw += 15.0 if legRetests > 0 else 0.0
    strengthVal: float = na if legDir == 0 else math.min(scoreRaw, 100.0)

    __block_result_16__ = (na, na, na, na)
    __switch__ = riskPresetInput
    if __switch__ == "Conservative":
        __block_result_16__ = (2.5, 1.0, 2.0, 4.0)
    elif __switch__ == "Aggressive":
        __block_result_16__ = (1.0, 1.5, 2.5, 4.0)
    elif __switch__ == "Scalping":
        __block_result_16__ = (0.8, 0.8, 1.5, 2.0)
    elif __switch__ == "Custom":
        __block_result_16__ = (slMultInput, tp1MultInput, tp2MultInput, tp3MultInput)
    else:
        __block_result_16__ = (1.5, 1.0, 2.0, 3.0)
    effSLMult, effTP1, effTP2, effTP3 = __block_result_16__

    riskAtr: float = nz(ta.atr(atrLenRiskInput), 0.0)
    slDistance: float = riskAtr * effSLMult

    activeEntry: Persistent[float] = na(float)
    activeSL: Persistent[float] = na(float)
    activeTP1: Persistent[float] = na(float)
    activeTP2: Persistent[float] = na(float)
    activeTP3: Persistent[float] = na(float)
    activeDir: Persistent[int] = 0
    entryBar: Persistent[int] = na(int)

    tp1Reached: Persistent[bool] = False
    tp2Reached: Persistent[bool] = False
    tp3Reached: Persistent[bool] = False
    beActive: Persistent[bool] = False

    statWins: Persistent[int] = 0
    statLosses: Persistent[int] = 0
    formStr: Persistent[str] = ""

    canOpen: bool = activeDir == 0
    openLong: bool = confirmedBuy and slDistance > 0 and canOpen
    openShort: bool = confirmedSell and slDistance > 0 and canOpen

    if openLong:
        activeEntry = close
        activeSL = close - slDistance
        activeTP1 = close + slDistance * effTP1
        activeTP2 = close + slDistance * effTP2
        activeTP3 = close + slDistance * effTP3
        activeDir = 1
        entryBar = bar_index
        tp1Reached = False
        tp2Reached = False
        tp3Reached = False
        beActive = False

    if openShort:
        activeEntry = close
        activeSL = close + slDistance
        activeTP1 = close - slDistance * effTP1
        activeTP2 = close - slDistance * effTP2
        activeTP3 = close - slDistance * effTP3
        activeDir = -1
        entryBar = bar_index
        tp1Reached = False
        tp2Reached = False
        tp3Reached = False
        beActive = False

    beActiveAtBarStart: bool = beActive
    effectiveSL: float = activeSL

    canCheckHit: bool = activeDir != 0 and (not na(entryBar)) and (bar_index > entryBar) and barstate.isconfirmed

    slHit: bool = canCheckHit and (low <= effectiveSL if activeDir == 1 else high >= effectiveSL)
    tp1Hit: bool = canCheckHit and (high >= activeTP1 if activeDir == 1 else low <= activeTP1)
    tp2Hit: bool = canCheckHit and (high >= activeTP2 if activeDir == 1 else low <= activeTP2)
    tp3Hit: bool = canCheckHit and (high >= activeTP3 if activeDir == 1 else low <= activeTP3)

    tp1FirstTouch: bool = tp1Hit and (not tp1Reached) and (not slHit)
    tp2FirstTouch: bool = tp2Hit and (not tp2Reached) and (not slHit)
    tp3FirstTouch: bool = tp3Hit and (not tp3Reached) and (not slHit)

    if tp1FirstTouch:
        tp1Reached = True
    if tp2FirstTouch:
        tp2Reached = True
    if tp3FirstTouch:
        tp3Reached = True

    beJustActivated: bool = False
    if useBreakEvenInput and tp1FirstTouch and (not beActive):
        activeSL = activeEntry
        beActive = True
        beJustActivated = True

    hitSL: Persistent[float] = na(float)
    hitEntry: Persistent[float] = na(float)
    if slHit:
        hitSL = effectiveSL
        hitEntry = activeEntry

    exitEntry: float = activeEntry
    exitSL: float = effectiveSL
    exitTP1: float = activeTP1
    exitTP2: float = activeTP2
    exitTP3: float = activeTP3
    exitBeActive: bool = beActiveAtBarStart
    displayTp1Reached: bool = tp1Reached
    displayTp2Reached: bool = tp2Reached
    displayTp3Reached: bool = tp3Reached

    if (slHit or tp3Hit) and activeDir != 0:
        tradeWin: bool = tp1Reached
        if tradeWin:
            statWins += 1
        else:
            statLosses += 1

        formStr = formStr + ('▰' if tradeWin else '▱')
        if string.length(formStr) > FORM_LEN:
            formStr = string.substring(formStr, string.length(formStr) - FORM_LEN)
        activeDir = 0
        activeSL = na
        activeTP1 = na
        activeTP2 = na
        activeTP3 = na
        activeEntry = na
        entryBar = na
        tp1Reached = False
        tp2Reached = False
        tp3Reached = False
        beActive = False

    plotshape(low if showSignalsInput and openLong else na, 'Buy', style=shape.labelup, location=location.belowbar, color=BULL_COLOR, textcolor=BULL_LABEL_TEXT, text='Long ▲', size=size.small)

    plotshape(high if showSignalsInput and openShort else na, 'Sell', style=shape.labeldown, location=location.abovebar, color=BEAR_COLOR, textcolor=BEAR_LABEL_TEXT, text='Short ▼', size=size.small)

    plot(vwapNow, 'VWAP', display=display.data_window)
    plot(up1, '+1 band', display=display.data_window)
    plot(dn1, '-1 band', display=display.data_window)
    plot(up2, '+2 band', display=display.data_window)
    plot(dn2, '-2 band', display=display.data_window)
    plot(strengthVal, 'Strength', display=display.data_window)

    bgcolor(color.new(BULL_COLOR if legDir > 0 else BEAR_COLOR, 92) if showBgInput and legDir != 0 else na, title='Leg Background')

    slLine: Persistent[Line] = na(Line)
    tp1Line: Persistent[Line] = na(Line)
    tp2Line: Persistent[Line] = na(Line)
    tp3Line: Persistent[Line] = na(Line)
    entryLine: Persistent[Line] = na(Line)

    slLabel: Persistent[Label] = na(Label)
    tp1Label: Persistent[Label] = na(Label)
    tp2Label: Persistent[Label] = na(Label)
    tp3Label: Persistent[Label] = na(Label)
    entryLabel: Persistent[Label] = na(Label)

    if (openLong or openShort) and showSlTpInput:
        line.delete(slLine)
        line.delete(tp1Line)
        line.delete(tp2Line)
        line.delete(tp3Line)
        line.delete(entryLine)
        label.delete(slLabel)
        label.delete(tp1Label)
        label.delete(tp2Label)
        label.delete(tp3Label)
        label.delete(entryLabel)

        x1: int = bar_index
        x2: int = bar_index + LINE_FORWARD_BARS

        entryLine = line.new(x1, activeEntry, x2, activeEntry, color=ENTRY_COLOR, style=entryLineStyle, width=1)
        slLine = line.new(x1, activeSL, x2, activeSL, color=SL_COLOR, style=slLineStyle, width=2)
        tp1Line = line.new(x1, activeTP1, x2, activeTP1, color=TP1_COLOR, style=tpLineStyle, width=1)
        tp2Line = line.new(x1, activeTP2, x2, activeTP2, color=TP2_COLOR, style=tpLineStyle, width=1)
        tp3Line = line.new(x1, activeTP3, x2, activeTP3, color=TP3_COLOR, style=tpLineStyle, width=1)

        if showSlTpLabelsInput:
            lblX: int = x2 + LABEL_OFFSET_BARS
            entryS: str = string.tostring(activeEntry, format.mintick)
            slS: str = fmtPrice(activeSL) + formatPctFromEntry(activeSL, activeEntry)
            tp1S: str = fmtPrice(activeTP1) + formatPctFromEntry(activeTP1, activeEntry)
            tp2S: str = fmtPrice(activeTP2) + formatPctFromEntry(activeTP2, activeEntry)
            tp3S: str = fmtPrice(activeTP3) + formatPctFromEntry(activeTP3, activeEntry)

            entryLabel = label.new(lblX, activeEntry, 'ENTRY ' + entryS, color=ENTRY_COLOR, textcolor=LABEL_TEXT, style=label.style_label_left, size=labelSize)
            slLabel = label.new(lblX, activeSL, 'SL ' + slS, color=SL_COLOR, textcolor=LABEL_TEXT, style=label.style_label_left, size=labelSize)
            tp1Label = label.new(lblX, activeTP1, 'TP1 ' + tp1S, color=TP_LABEL_COLOR, textcolor=LABEL_TEXT, style=label.style_label_left, size=labelSize)
            tp2Label = label.new(lblX, activeTP2, 'TP2 ' + tp2S, color=TP_LABEL_COLOR, textcolor=LABEL_TEXT, style=label.style_label_left, size=labelSize)
            tp3Label = label.new(lblX, activeTP3, 'TP3 ' + tp3S, color=TP_LABEL_COLOR, textcolor=LABEL_TEXT, style=label.style_label_left, size=labelSize)

    if showSlTpInput and (not na(tp1Line)) and displayTp1Reached:
        line.set_color(tp1Line, TP_HIT_COLOR)
        line.set_style(tp1Line, line.style_solid)
        if showSlTpLabelsInput and (not na(tp1Label)):
            label.set_text(tp1Label, 'TP1 ✓ ' + fmtPrice(exitTP1) + formatPctFromEntry(exitTP1, exitEntry))
            label.set_color(tp1Label, TP_HIT_COLOR)
    if showSlTpInput and (not na(tp2Line)) and displayTp2Reached:
        line.set_color(tp2Line, TP_HIT_COLOR)
        line.set_style(tp2Line, line.style_solid)
        if showSlTpLabelsInput and (not na(tp2Label)):
            label.set_text(tp2Label, 'TP2 ✓ ' + fmtPrice(exitTP2) + formatPctFromEntry(exitTP2, exitEntry))
            label.set_color(tp2Label, TP_HIT_COLOR)
    if showSlTpInput and (not na(tp3Line)) and displayTp3Reached:
        line.set_color(tp3Line, TP_HIT_COLOR)
        line.set_style(tp3Line, line.style_solid)
        if showSlTpLabelsInput and (not na(tp3Label)):
            label.set_text(tp3Label, 'TP3 ✓ ' + fmtPrice(exitTP3) + formatPctFromEntry(exitTP3, exitEntry))
            label.set_color(tp3Label, TP_HIT_COLOR)

    if showSlTpInput and beActive and (activeDir != 0):
        if not na(slLine):
            line.set_color(slLine, color.new(SL_COLOR, BE_DIM_TRANSP))
        if showSlTpLabelsInput:
            if not na(slLabel):
                label.set_color(slLabel, color.new(SL_COLOR, BE_DIM_TRANSP))
            if not na(entryLabel):
                entryS: str = string.tostring(activeEntry, format.mintick)
                label.set_text(entryLabel, 'ENTRY ' + entryS + '  → SL (BE)')
                label.set_color(entryLabel, BE_COLOR)

    if activeDir != 0 and showSlTpInput and (not na(slLine)):
        newX2: int = bar_index + LINE_UPDATE_BARS
        newLblX: int = newX2 + LABEL_OFFSET_BARS
        line.set_x2(slLine, newX2)
        line.set_x2(tp1Line, newX2)
        line.set_x2(tp2Line, newX2)
        line.set_x2(tp3Line, newX2)
        line.set_x2(entryLine, newX2)
        if showSlTpLabelsInput and (not na(slLabel)):
            label.set_x(slLabel, newLblX)
            label.set_x(tp1Label, newLblX)
            label.set_x(tp2Label, newLblX)
            label.set_x(tp3Label, newLblX)
            label.set_x(entryLabel, newLblX)

    dashTable: Persistent[Table] = na(Table)

    if showDashInput and barstate.islast:
        trendWord: str = 'Bullish' if legDir == 1 else 'Bearish' if legDir == -1 else 'Neutral'
        trendCol: Color = BULL_TEXT if legDir == 1 else BEAR_TEXT if legDir == -1 else NEUTRAL_TEXT
        headerBg: Color = HEADER_BG_BULL if legDir == 1 else HEADER_BG_BEAR if legDir == -1 else HEADER_BG_FLAT

        signalStr: str = 'LONG' if activeDir == 1 else 'SHORT' if activeDir == -1 else 'Wait'
        signalCol: Color = BULL_TEXT if activeDir == 1 else BEAR_TEXT if activeDir == -1 else TEXT_MUTED

        strengthStr: str = '—' if na(strengthVal) else string.tostring(strengthVal, '#') + '  ' + buildGauge(strengthVal, 100, 8)
        strengthCol: Color = TEXT_MUTED if na(strengthVal) else BULL_TEXT if strengthVal >= 70 else NEUTRAL_TEXT if strengthVal >= 40 else BEAR_TEXT

        dashAnchor: str = '—' if legDir == 0 or na(legAnchorPx) else lastStruct + ' @ ' + string.tostring(legAnchorPx, format.mintick)
        dashLegBars: str = '—' if legDir == 0 else string.tostring(legBars) + ' bars · ' + fmtSigned(legMove, '%')
        dashMode: str = anchorModeInput + ' / ' + ('half-life ' + string.tostring(halfLifeInput) if weightModeInput == 'Half-life' else 'cumulative')
        dashVwap: str = fmtPrice(vwapNow)
        dashDist: str = '—' if na(distSig) else fmtSigned(distSig, 'σ') + '   ' + fmtSigned(distPct, '%')
        dashBalance: str = '—' if na(legBalance) else string.tostring(legBalance, '#') + '%  ' + buildGauge(nz(legBalance), 100, 6)
        dashBalLbl: str = 'Vol above VWAP' if hasVolume else 'Bars above VWAP'
        balanceCol: Color = TEXT_COLOR if na(legBalance) else BULL_TEXT if legBalance >= 50 else BEAR_TEXT

        currentRR: float = effTP1 if activeDir != 0 else 0.0
        slDistPct: float = math.abs(activeEntry - activeSL) / activeEntry * 100 if activeDir != 0 and (not na(activeEntry)) and (activeEntry != 0) else 0.0

        dashSL: str = ('BE @ ' if beActive else '') + string.tostring(activeSL, format.mintick) if activeDir != 0 and (not na(activeSL)) else '—'
        dashTP1: str = ('✓ ' if tp1Reached else '') + string.tostring(activeTP1, format.mintick) if activeDir != 0 and (not na(activeTP1)) else '—'
        dashTP2: str = ('✓ ' if tp2Reached else '') + string.tostring(activeTP2, format.mintick) if activeDir != 0 and (not na(activeTP2)) else '—'
        dashTP3: str = ('✓ ' if tp3Reached else '') + string.tostring(activeTP3, format.mintick) if activeDir != 0 and (not na(activeTP3)) else '—'
        dashSlCol: Color = BE_COLOR if beActive else SL_COLOR
        dashTp1Col: Color = TP_HIT_COLOR if tp1Reached else TP_LABEL_COLOR
        dashTp2Col: Color = TP_HIT_COLOR if tp2Reached else TP_LABEL_COLOR
        dashTp3Col: Color = TP_HIT_COLOR if tp3Reached else TP_LABEL_COLOR

        dashRR: str = string.tostring(currentRR, '#.#') + 'R'
        dashDistPct: str = string.tostring(slDistPct, '#.##') + '%'
        rrColor: Color = BULL_TEXT if currentRR >= 1.5 else NEUTRAL_TEXT if currentRR >= 1.0 else BEAR_TEXT
        distColor: Color = BEAR_TEXT if slDistPct > 3.0 else NEUTRAL_TEXT if slDistPct > 1.0 else BULL_TEXT

        closedTrades: int = statWins + statLosses
        winRate: float = statWins / cast_float(closedTrades) * 100.0 if closedTrades > 0 else 0.0
        dashWL: str = string.tostring(statWins) + ' / ' + string.tostring(statLosses)
        dashWR: str = string.tostring(winRate, '#.#') + '%  ' + buildGauge(winRate, 100, 8) if closedTrades > 0 else '—'
        wrCol: Color = TEXT_MUTED if closedTrades == 0 else BULL_TEXT if winRate >= 55.0 else NEUTRAL_TEXT if winRate >= 45.0 else BEAR_TEXT
        dashForm: str = '—' if formStr == '' else formStr

        marketRows: int = 6 if showMarketSecInput else 0
        vwapRows: int = 8 if showVwapSecInput else 0
        tradeRows: int = (7 if activeDir != 0 else 2) if showTradeSecInput else 0
        statsRows: int = 5 if showStatsSecInput else 0
        totalRows: int = 2 + marketRows + vwapRows + tradeRows + statsRows

        if not na(dashTable):
            table.delete(dashTable)
        dashTable = table.new(dashPos, 2, totalRows, bgcolor=TABLE_BG, border_color=TABLE_BORDER, border_width=1, frame_color=TABLE_BORDER, frame_width=1)

        r: int = 0
        zeb: bool = False
        rb: Color = TABLE_BG

        table.cell(dashTable, 0, r, '◆ SA-VWAP · ' + trendWord, text_color=HEADER_TEXT, bgcolor=headerBg, text_size=size.small, text_halign=text.align_center)
        table.merge_cells(dashTable, 0, r, 1, r)
        r += 1

        if showMarketSecInput:
            table.cell(dashTable, 0, r, '— Market —', text_color=TEXT_MUTED, bgcolor=TABLE_ROW_ALT, text_size=size.tiny, text_halign=text.align_center)
            table.merge_cells(dashTable, 0, r, 1, r)
            r += 1
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, 'Trend', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='Direction of the current anchored leg.')
            table.cell(dashTable, 1, r, trendWord, text_color=trendCol, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, 'Signal', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='Current position. A new trade opens only while flat.')
            table.cell(dashTable, 1, r, signalStr, text_color=signalCol, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, 'Strength', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip="Composite 0-100: volume balance (40) + price on the leg's side (25) + not stretched past band 2 (20) + leg already retested (15). A context score, not a backtested edge.")
            table.cell(dashTable, 1, r, strengthStr, text_color=strengthCol, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, 'Last event', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='Most recent leg anchor or VWAP retest.')
            table.cell(dashTable, 1, r, lastEventStr, text_color=TEXT_COLOR, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, 'Timeframe', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb)
            table.cell(dashTable, 1, r, timeframe.period, text_color=TEXT_COLOR, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb

        if showVwapSecInput:
            table.cell(dashTable, 0, r, '— VWAP —', text_color=TEXT_MUTED, bgcolor=TABLE_ROW_ALT, text_size=size.tiny, text_halign=text.align_center)
            table.merge_cells(dashTable, 0, r, 1, r)
            r += 1
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, 'Mode', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='Anchor mode / weighting. Without volume data the VWAP falls back to time weighting.')
            table.cell(dashTable, 1, r, dashMode, text_color=TEXT_COLOR, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, 'Anchor', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='Structure tag and price of the bar the current leg is anchored to.')
            table.cell(dashTable, 1, r, dashAnchor, text_color=TEXT_COLOR, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, 'Leg age', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='Bars since the anchor and price move from it.')
            table.cell(dashTable, 1, r, dashLegBars, text_color=TEXT_COLOR, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, 'VWAP', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='Anchored VWAP value on the current bar.')
            table.cell(dashTable, 1, r, dashVwap, text_color=trendCol, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, 'Price vs VWAP', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='Distance from the VWAP in leg sigma and in percent.')
            table.cell(dashTable, 1, r, dashDist, text_color=TEXT_COLOR, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, 'Zone', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='Premium above +band 2, Discount below -band 2, Fair value in between.')
            table.cell(dashTable, 1, r, zoneStr, text_color=zoneCol, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, dashBalLbl, text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip="Share of the leg's traded weight that changed hands above the VWAP. Above 50% = buyers control the leg.")
            table.cell(dashTable, 1, r, dashBalance, text_color=balanceCol, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb

        if showTradeSecInput:
            table.cell(dashTable, 0, r, '— Trade —', text_color=TEXT_MUTED, bgcolor=TABLE_ROW_ALT, text_size=size.tiny, text_halign=text.align_center)
            table.merge_cells(dashTable, 0, r, 1, r)
            r += 1
            if activeDir != 0:
                rb = TABLE_ROW_ALT if zeb else TABLE_BG
                table.cell(dashTable, 0, r, 'SL', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip="Active stop. 'BE @' = moved to entry after TP1.")
                table.cell(dashTable, 1, r, dashSL, text_color=dashSlCol, text_size=size.small, bgcolor=rb)
                r += 1
                zeb = not zeb
                rb = TABLE_ROW_ALT if zeb else TABLE_BG
                table.cell(dashTable, 0, r, 'TP1', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='✓ = touched (counts as a win).')
                table.cell(dashTable, 1, r, dashTP1, text_color=dashTp1Col, text_size=size.small, bgcolor=rb)
                r += 1
                zeb = not zeb
                rb = TABLE_ROW_ALT if zeb else TABLE_BG
                table.cell(dashTable, 0, r, 'TP2', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb)
                table.cell(dashTable, 1, r, dashTP2, text_color=dashTp2Col, text_size=size.small, bgcolor=rb)
                r += 1
                zeb = not zeb
                rb = TABLE_ROW_ALT if zeb else TABLE_BG
                table.cell(dashTable, 0, r, 'TP3', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='Final target. Touching it closes the trade.')
                table.cell(dashTable, 1, r, dashTP3, text_color=dashTp3Col, text_size=size.small, bgcolor=rb)
                r += 1
                zeb = not zeb
                rb = TABLE_ROW_ALT if zeb else TABLE_BG
                table.cell(dashTable, 0, r, 'R:R (TP1)', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='Reward-to-risk at TP1.')
                table.cell(dashTable, 1, r, dashRR, text_color=rrColor, text_size=size.small, bgcolor=rb)
                r += 1
                zeb = not zeb
                rb = TABLE_ROW_ALT if zeb else TABLE_BG
                table.cell(dashTable, 0, r, 'SL Dist %', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='Stop distance as % of entry (not position risk).')
                table.cell(dashTable, 1, r, dashDistPct, text_color=distColor, text_size=size.small, bgcolor=rb)
                r += 1
                zeb = not zeb
            else:
                rb = TABLE_ROW_ALT if zeb else TABLE_BG
                table.cell(dashTable, 0, r, 'Flat · waiting for a VWAP retest', text_color=TEXT_MUTED, text_size=size.small, text_halign=text.align_center, bgcolor=rb)
                table.merge_cells(dashTable, 0, r, 1, r)
                r += 1
                zeb = not zeb

        if showStatsSecInput:
            table.cell(dashTable, 0, r, '— Stats —', text_color=TEXT_MUTED, bgcolor=TABLE_ROW_ALT, text_size=size.tiny, text_halign=text.align_center)
            table.merge_cells(dashTable, 0, r, 1, r)
            r += 1
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, 'Trades', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='Closed trades this session (wins + losses).')
            table.cell(dashTable, 1, r, string.tostring(closedTrades), text_color=TEXT_COLOR, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, 'W / L', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb)
            table.cell(dashTable, 1, r, dashWL, text_color=TEXT_COLOR, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, 'Win rate', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='Wins / closed. A trade is a WIN once TP1 is touched.')
            table.cell(dashTable, 1, r, dashWR, text_color=wrCol, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb
            rb = TABLE_ROW_ALT if zeb else TABLE_BG
            table.cell(dashTable, 0, r, 'Form', text_color=TEXT_MUTED, text_size=size.small, bgcolor=rb, tooltip='Last ' + string.tostring(FORM_LEN) + ' closed trades.  ▰ = win · ▱ = loss (newest on the right).')
            table.cell(dashTable, 1, r, dashForm, text_color=FORM_COLOR, text_size=size.small, bgcolor=rb)
            r += 1
            zeb = not zeb

        table.cell(dashTable, 0, r, INDICATOR_NAME + ' · ' + INDICATOR_VERSION, text_color=TEXT_MUTED, text_size=size.tiny, text_halign=text.align_center)
        table.merge_cells(dashTable, 0, r, 1, r)

    if barstate.islast and showWatermarkInput:
        wmTable: Persistent[Table] = table.new(position.bottom_center, 1, 1, bgcolor=color.new(color.black, 100), border_color=color.new(color.black, 100), border_width=0, frame_color=color.new(color.black, 100), frame_width=0)
        table.cell(wmTable, 0, 0, BRAND_NAME, text_color=WM_COLOR, text_size=size.normal, text_halign=text.align_center, bgcolor=color.new(color.black, 100))

    if openLong or openShort:
        aPrice: str = string.tostring(close, format.mintick)
        aSL: str = string.tostring(nz(activeSL), format.mintick)
        aTP1: str = string.tostring(nz(activeTP1), format.mintick)
        aTP2: str = string.tostring(nz(activeTP2), format.mintick)
        aTP3: str = string.tostring(nz(activeTP3), format.mintick)
        aRR: str = string.tostring(effTP1, '#.#')
        aVwap: str = string.tostring(nz(vwapNow), format.mintick)

        if openLong:
            jsonBuy: str = '{"action":"buy","ticker":"' + syminfo.tickerid + '","tf":"' + timeframe.period + '","price":' + aPrice + ',"vwap":' + aVwap + ',"sl":' + aSL + ',"tp1":' + aTP1 + ',"tp2":' + aTP2 + ',"tp3":' + aTP3 + ',"rr":' + aRR + '}'
            textBuy: str = '🟢 LONG | VWAP retest | ' + syminfo.tickerid + ' | TF: ' + timeframe.period + ' | Price: ' + aPrice + ' | SL: ' + aSL + ' | TP1: ' + aTP1 + ' | TP2: ' + aTP2 + ' | TP3: ' + aTP3 + ' | R:R: ' + aRR
            alert(jsonBuy if webhookInput else textBuy, alert.freq_once_per_bar_close)

        if openShort:
            jsonSell: str = '{"action":"sell","ticker":"' + syminfo.tickerid + '","tf":"' + timeframe.period + '","price":' + aPrice + ',"vwap":' + aVwap + ',"sl":' + aSL + ',"tp1":' + aTP1 + ',"tp2":' + aTP2 + ',"tp3":' + aTP3 + ',"rr":' + aRR + '}'
            textSell: str = '🔴 SHORT | VWAP retest | ' + syminfo.tickerid + ' | TF: ' + timeframe.period + ' | Price: ' + aPrice + ' | SL: ' + aSL + ' | TP1: ' + aTP1 + ' | TP2: ' + aTP2 + ' | TP3: ' + aTP3 + ' | R:R: ' + aRR
            alert(jsonSell if webhookInput else textSell, alert.freq_once_per_bar_close)

    if slHit and showSlHitAlertInput:
        textSlHit: str = ('🛡️ BE STOP-OUT | ' if exitBeActive else '🛑 SL HIT | ') + syminfo.tickerid + ' | Entry: ' + string.tostring(nz(hitEntry), format.mintick) + ' | SL: ' + string.tostring(nz(hitSL), format.mintick)
        alert(textSlHit, alert.freq_once_per_bar_close)

    if beJustActivated and alertTpHitInput:
        alert('🛡️ BREAK-EVEN | ' + syminfo.tickerid + ' | SL moved to ' + string.tostring(nz(exitEntry), format.mintick), alert.freq_once_per_bar_close)
    if tp1FirstTouch and alertTpHitInput:
        alert('🎯 TP1 HIT | ' + syminfo.tickerid + ' | Price: ' + string.tostring(nz(exitTP1), format.mintick), alert.freq_once_per_bar_close)
    if tp2FirstTouch and alertTpHitInput:
        alert('🎯🎯 TP2 HIT | ' + syminfo.tickerid + ' | Price: ' + string.tostring(nz(exitTP2), format.mintick), alert.freq_once_per_bar_close)
    if tp3FirstTouch and alertTpHitInput:
        alert('🏆 TP3 HIT | ' + syminfo.tickerid + ' | Price: ' + string.tostring(nz(exitTP3), format.mintick), alert.freq_once_per_bar_close)

    if evAnchorBull and alertStructInput:
        alert('🟢 New bullish leg | ' + syminfo.tickerid + ' | TF: ' + timeframe.period + ' | Anchor: ' + fmtPrice(legAnchorPx), alert.freq_once_per_bar_close)
    if evAnchorBear and alertStructInput:
        alert('🔴 New bearish leg | ' + syminfo.tickerid + ' | TF: ' + timeframe.period + ' | Anchor: ' + fmtPrice(legAnchorPx), alert.freq_once_per_bar_close)
    if evCrossUp and alertStructInput:
        alert('🔵 Close above VWAP | ' + syminfo.tickerid + ' | TF: ' + timeframe.period + ' | VWAP: ' + fmtPrice(vwapNow), alert.freq_once_per_bar_close)
    if evCrossDn and alertStructInput:
        alert('🔵 Close below VWAP | ' + syminfo.tickerid + ' | TF: ' + timeframe.period + ' | VWAP: ' + fmtPrice(vwapNow), alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
