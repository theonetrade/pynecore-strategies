"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    array, bar_index, barmerge, barstate, close, color, extend, fill, high,
    hlc3, input, label, line, low, math, na, open, plot, plotcandle, request, script, size, string,
    syminfo, ta, text, timeframe, xloc, yloc
)
from pynecore.types import Color, Label, Line, Persistent

SHOW: str = "Show"
HIDE: str = "Hide"
STYLE_LINE: str = "Line"
STYLE_COLUMNS: str = "Columns"
STYLE_HISTOGRAM: str = "Histogram"
GUIDE_LABELS: str = "Labels Only"
GUIDE_BOTH: str = "Lines + Labels"
GUIDE_HIDE: str = "Hide"
LABEL_PADDING_GROUPED: str = "Grouped"
LABEL_PADDING_INDIVIDUAL: str = "Individual"
PRICE_SOURCE_MACD_HIST: str = "MACD Hist"
PRICE_SOURCE_IMPULSE_HIST: str = "Impulse Hist"
G_MACD: str = "01 — MACD / Signal"
G_HIST: str = "02 — MACD Histogram"
G_IMPULSE: str = "03 — Impulse / Signal"
G_GUIDES: str = "04 — Focused Guides"
G_RIGHT_LABELS: str = "05 — Right-Side Labels"
G_PRICE_OVERLAY: str = "06 — Price Pane Overlay"
MACD_FAST_LEN_DEFAULT: int = 12
MACD_SLOW_LEN_DEFAULT: int = 26
MACD_SIGNAL_LEN_DEFAULT: int = 9
IMPULSE_MA_LEN_DEFAULT: int = 34
IMPULSE_SIGNAL_LEN_DEFAULT: int = 9
ATR_LEN: int = 14
PAIR_LAST_N_DEFAULT: int = 144
COL_BULL: Color = color.teal
COL_BEAR: Color = color.new('#F51673')
COL_NEUTRAL: Color = color.rgb(165, 165, 165)
COL_IMPULSE_HIST_BULL: Color = color.new('#FF8400')
COL_IMPULSE_HIST_BEAR: Color = color.rgb(157, 78, 221)
COL_GUIDE_POS_PENDING: Color = color.teal
COL_GUIDE_POS_PASSED: Color = color.new('#FFE102')
COL_GUIDE_NEG_BELOW: Color = color.new('#F51673')
COL_GUIDE_NEG_PASSED: Color = color.rgb(165, 165, 165)
COL_GUIDE_ZERO: Color = color.rgb(165, 165, 165)
COL_POS_EXTREME: Color = color.new('#F76300')
COL_NEG_EXTREME: Color = color.new('#7A00A0')
GUIDE_PROXIMITY_FLOOR: float = 6.0
GUIDE_PROXIMITY_FRACTION: float = 0.35
GUIDE_LINE_LAST_N_DEFAULT: int = 2
GUIDE_LINE_WIDTH_DEFAULT: int = 1
PRICE_FOLLOW_LAST_N: int = 2
PRICE_FOLLOW_WIDTH: int = 1
PRICE_FOLLOW_TRANSP: int = 0
DIRECTION_EPS: float = 1e-08
TT_MACD: str = 'PRICE MACD / SIGNAL — NORMALIZED MOMENTUM SCALE\n\n' + 'Default raw MACD = EMA12(Close) − EMA26(Close). Signal = EMA9(raw MACD). Fast / Slow / Signal lengths are user-adjustable.\n\n' + 'Each raw line is divided by ATR14 and independently passed through the fixed Normalized Momentum Scale transfer. ' + 'This preserves true crossover/order while placing both lines on a bounded -100…+100 volatility-relative coordinate.\n\n' + 'MACD > Signal uses the shared Bull color. Signal > MACD uses the shared Bear color. The same Bull / Bear / Neutral palette drives both the MACD / Signal plots and their fill; fill transparency remains independent.\n\n' + 'Display Style controls both pair members. Last N uses native show_last.'
TT_HIST: str = 'ACTUAL MACD HISTOGRAM — NORMALIZED MOMENTUM SCALE\n\n' + 'Raw Histogram = raw MACD − raw Signal.\n\n' + 'The raw histogram is divided by ATR14 and passed through Normalized Momentum Scale independently. ' + 'It is NOT calculated by subtracting the already-remapped semantic MACD and Signal lines, because that would distort magnitude after the nonlinear transfer.\n\n' + 'The MACD Histogram inherits the shared MACD Bull / Bear / Neutral palette.'
TT_HTF_HIST: str = 'DEVELOPING AUTO-NEXT-HTF MACD HISTOGRAM — NMS\n\n' + 'The complete Price MACD Histogram is calculated natively on the automatically selected next higher timeframe:\n' + 'EMA12(Close) − EMA26(Close) → EMA9 Signal → raw Histogram → ÷ native HTF ATR14 → Normalized Momentum Scale.\n\n' + 'Transport uses gaps_off + lookahead_off with no [1] confirmed-bar offset. This is a developing HTF reading, so its value can continue changing until the active higher-timeframe candle closes.\n\n' + 'Default presentation = Line / SHOW, Last N = 144. The Developing HTF Histogram inherits the shared MACD Bull / Bear / Neutral palette. The right label shows the actual selected HTF.'
TT_IMPULSE: str = 'IMPULSE MACD / SIGNAL — NORMALIZED MOMENTUM SCALE\n\n' + 'LazyBear ownership:\n' + '• ImpulseMACD = md.\n' + '• Signal = sb = SMA(md, Signal Length).\n' + '• Impulse Hist = sh = md − sb.\n\n' + 'Default source architecture = HLC3 + SMMA/RMA34 High/Low envelope + ZLEMA34 midline. MA Length and Signal Length are user-adjustable. ' + 'ImpulseMACD measures how far the ZLEMA extends outside the smoothed High/Low envelope; zero means the midline remains inside the envelope.\n\n' + 'Raw ImpulseMACD and Signal are each divided by ATR14 and independently passed through the SAME fixed Normalized Momentum Scale transfer as Price MACD / Signal.\n\n' + 'DEFAULT PRESENTATION:\n' + '• ImpulseMACD = Histogram.\n' + '• Impulse Signal = Line.\n' + '• Impulse Hist = Histogram / SHOW.\n\n' + 'ImpulseMACD > Signal uses the shared Impulse Bull color. Signal > ImpulseMACD uses the shared Impulse Bear color. The same Bull / Bear / Neutral palette drives the Impulse plots, fill, histogram, and right labels.'
TT_IMPULSE_HIST: str = 'IMPULSEHISTO — LAZYBEAR sh = md − sb — NORMALIZED MOMENTUM SCALE\n\n' + 'This is the original LazyBear Impulse Hist relationship: sh = md − sb, where md is ImpulseMACD and sb is its SMA9 Signal.\n\n' + 'The raw Impulse histogram is divided by ATR14 and passed through Normalized Momentum Scale independently. ' + 'It is NOT calculated by subtracting the already-remapped semantic Impulse and Signal values.\n\n' + 'The Impulse Histogram inherits the shared Impulse Bull / Bear / Neutral palette. Defaults remain orange bullish, light purple bearish, and neutral gray.\n\n' + 'The Impulse histogram renders behind the standard MACD histogram and shares the Impulse Last-N window.'
TT_GUIDES: str = 'FOCUSED SEMANTIC GUIDES\n\n' + 'Zero always remains available as the center reference. Non-zero guide visibility is based on proximity to the CURRENTLY VISIBLE plotted geometry — MACD / Signal, MACD Hist, Developing HTF MACD Hist, ImpulseMACD / Signal, and Impulse Hist.\n\n' + "A guide appears only when at least one visible plotted value is genuinely close to that semantic rung. Capture radius = max(6 semantic points, 35% of the rung's nearest ladder spacing). This prevents distant ±55 / ±75 guides from appearing simply because they are the next rungs beyond MACD.\n\n" + 'Guide levels = 0 / ±13 / ±34 / ±55 / ±75 / ±89 / ±100. ±100 additionally requires visible plotted geometry beyond ±95.\n\n' + 'Guide COLORS remain MACD-state colors; only guide VISIBILITY uses all visible geometry. Labels Only is the default. Lines + Labels adds short right-edge dotted/dashed guide segments.'
TT_PRICE_OVERLAY: str = 'PRICE PANE OVERLAY\n\n' + 'Plots actual chart OHLC on the main price pane with force_overlay=true while this indicator remains in its oscillator pane.\n\n' + 'Color Source:\n' + '• MACD Hist = candle / follow-line color follows the sign of the standard MACD Histogram.\n' + '• Impulse Hist = candle / follow-line color follows the sign of the Impulse Histogram.\n\n' + 'The default source is MACD Hist. Candle body / wick / border transparency are independently adjustable.\n\n' + 'A hardcoded Close bar-to-bar follow line also uses the selected histogram color source. It always shows only the most recent 2 bars.'
TT_PRICE_CANDLE_TRANSP: str = 'Independent transparency controls for the force-overlay price candles.\n\n' + 'Defaults:\n' + '• Body = 75\n' + '• Wick = 0\n' + '• Border = 0'
TT_PADDING: str = 'One dynamic right-label padding engine.\n\n' + 'Individual — DEFAULT. Every visible telemetry label owns its own horizontal lane.\n' + 'Grouped — all visible telemetry labels share the first-padding lane.\n\n' + 'Order: Guide Levels → MACD Histogram → MACD → MACD Signal → HTF MACD Histogram → Impulse Hist → ImpulseMACD → Impulse Signal.\n\n' + 'All active guide rungs remain one Guide family. First Label Padding controls the first visible lane. ' + 'Padding Between Labels controls the standard distance to each next visible label in Individual mode. ' + 'A +2 EM visual compensation is applied after ImpulseMACD so the wider Impulse pair does not crowd its neighbor. ' + 'Only visible labels consume spacing.\n\n' + 'No forward bar_index offset is used.'


@script.indicator("MACD + Impulse MACD - Normalized Momentum Scale", "MACD", overlay=False, max_bars_back=5000, calc_bars_count=1500, max_labels_count=100, max_lines_count=50)
def main(
    in_macdFastLen=input.int(MACD_FAST_LEN_DEFAULT, "MACD Fast Length", minval=1, maxval=500, group=G_MACD, tooltip=TT_MACD),
    in_macdSlowLen=input.int(MACD_SLOW_LEN_DEFAULT, "MACD Slow Length", minval=1, maxval=500, group=G_MACD, tooltip=TT_MACD),
    in_macdSignalLen=input.int(MACD_SIGNAL_LEN_DEFAULT, "MACD Signal Length", minval=1, maxval=500, group=G_MACD, tooltip=TT_MACD),
    in_macdDisplayMode=input.string(SHOW, "MACD / Signal Display", options=(SHOW, HIDE), group=G_MACD, tooltip=TT_MACD),
    in_macdStyle=input.string(STYLE_LINE, "  ↳ Display Style", options=(STYLE_LINE, STYLE_COLUMNS, STYLE_HISTOGRAM), group=G_MACD, tooltip=TT_MACD),
    in_macdLastN=input.int(PAIR_LAST_N_DEFAULT, "  ↳ Last N Bars", minval=1, maxval=5000, group=G_MACD),
    in_macdWidth=input.int(1, "  ↳ Width", minval=1, maxval=5, group=G_MACD),
    in_macdTransp=input.int(65, "  ↳ Plot Transparency", minval=0, maxval=100, group=G_MACD),
    in_macdBullColor=input.color(COL_BULL, "Bull", group=G_MACD, inline="macdSharedColors"),
    in_macdBearColor=input.color(COL_BEAR, "Bear", group=G_MACD, inline="macdSharedColors"),
    in_macdNeutralColor=input.color(COL_NEUTRAL, "Neutral", group=G_MACD, inline="macdSharedColors"),
    in_macdFillMode=input.string(SHOW, "MACD / Signal Fill", options=(SHOW, HIDE), group=G_MACD, tooltip=TT_MACD),
    in_macdFillTransp=input.int(75, "  ↳ Fill Transparency", minval=0, maxval=100, group=G_MACD),
    in_macdRightLabelsMode=input.string(SHOW, "MACD / Signal Right-Side Labels", options=(SHOW, HIDE), group=G_MACD),
    in_histDisplayMode=input.string(SHOW, "MACD Histogram Display", options=(SHOW, HIDE), group=G_HIST, tooltip=TT_HIST),
    in_histStyle=input.string(STYLE_HISTOGRAM, "  ↳ Display Style", options=(STYLE_LINE, STYLE_COLUMNS, STYLE_HISTOGRAM), group=G_HIST, tooltip=TT_HIST),
    in_histLastN=input.int(PAIR_LAST_N_DEFAULT, "  ↳ Last N Bars", minval=1, maxval=5000, group=G_HIST),
    in_histWidth=input.int(2, "  ↳ Width", minval=1, maxval=5, group=G_HIST),
    in_histTransp=input.int(35, "  ↳ Transparency", minval=0, maxval=100, group=G_HIST),
    in_histRightLabelMode=input.string(SHOW, "MACD Histogram Right-Side Label", options=(SHOW, HIDE), group=G_HIST),
    in_htfHistDisplayMode=input.string(SHOW, "Developing HTF MACD Hist", options=(SHOW, HIDE), group=G_HIST, tooltip=TT_HTF_HIST),
    in_htfHistStyle=input.string(STYLE_LINE, "  ↳ HTF Display Style", options=(STYLE_LINE, STYLE_COLUMNS, STYLE_HISTOGRAM), group=G_HIST, tooltip=TT_HTF_HIST),
    in_htfHistLastN=input.int(PAIR_LAST_N_DEFAULT, "  ↳ HTF Last N Bars", minval=1, maxval=5000, group=G_HIST),
    in_htfHistWidth=input.int(2, "  ↳ HTF Width", minval=1, maxval=5, group=G_HIST),
    in_htfHistTransp=input.int(0, "  ↳ HTF Transparency", minval=0, maxval=100, group=G_HIST),
    in_htfHistRightLabelMode=input.string(SHOW, "HTF MACD Hist Right-Side Label", options=(SHOW, HIDE), group=G_HIST, tooltip=TT_HTF_HIST),
    in_impulseMaLen=input.int(IMPULSE_MA_LEN_DEFAULT, "Impulse MACD MA Length", minval=1, maxval=500, group=G_IMPULSE, tooltip=TT_IMPULSE),
    in_impulseSignalLen=input.int(IMPULSE_SIGNAL_LEN_DEFAULT, "Impulse Signal / Hist Length", minval=1, maxval=500, group=G_IMPULSE, tooltip=TT_IMPULSE),
    in_impulseDisplayMode=input.string(SHOW, "ImpulseMACD / Signal Display", options=(SHOW, HIDE), group=G_IMPULSE, tooltip=TT_IMPULSE),
    in_impulseMacdStyle=input.string(STYLE_LINE, "  ↳ ImpulseMACD Style", options=(STYLE_LINE, STYLE_COLUMNS, STYLE_HISTOGRAM), group=G_IMPULSE, tooltip=TT_IMPULSE),
    in_impulseSignalStyle=input.string(STYLE_LINE, "  ↳ Impulse Signal Style", options=(STYLE_LINE, STYLE_COLUMNS, STYLE_HISTOGRAM), group=G_IMPULSE, tooltip=TT_IMPULSE),
    in_impulseLastN=input.int(PAIR_LAST_N_DEFAULT, "  ↳ Last N Bars", minval=1, maxval=5000, group=G_IMPULSE),
    in_impulseWidth=input.int(1, "  ↳ Width", minval=1, maxval=5, group=G_IMPULSE),
    in_impulseTransp=input.int(65, "  ↳ Plot Transparency", minval=0, maxval=100, group=G_IMPULSE),
    in_impulseBullColor=input.color(COL_IMPULSE_HIST_BULL, "Bull", group=G_IMPULSE, inline="impulseSharedColors"),
    in_impulseBearColor=input.color(COL_IMPULSE_HIST_BEAR, "Bear", group=G_IMPULSE, inline="impulseSharedColors"),
    in_impulseNeutralColor=input.color(COL_NEUTRAL, "Neutral", group=G_IMPULSE, inline="impulseSharedColors"),
    in_impulseFillMode=input.string(SHOW, "Impulse / Signal Fill", options=(SHOW, HIDE), group=G_IMPULSE, tooltip=TT_IMPULSE),
    in_impulseFillTransp=input.int(90, "  ↳ Fill Transparency", minval=0, maxval=100, group=G_IMPULSE),
    in_impulseRightLabelsMode=input.string(SHOW, "Impulse / Signal Right-Side Labels", options=(SHOW, HIDE), group=G_IMPULSE),
    in_impulseHistDisplayMode=input.string(SHOW, "Impulse Hist Display", options=(SHOW, HIDE), group=G_IMPULSE, tooltip=TT_IMPULSE_HIST),
    in_impulseHistStyle=input.string(STYLE_HISTOGRAM, "  ↳ Histogram Style", options=(STYLE_LINE, STYLE_COLUMNS, STYLE_HISTOGRAM), group=G_IMPULSE, tooltip=TT_IMPULSE_HIST),
    in_impulseHistWidth=input.int(3, "  ↳ Histogram Width", minval=1, maxval=5, group=G_IMPULSE),
    in_impulseHistTransp=input.int(45, "  ↳ Histogram Transparency", minval=0, maxval=100, group=G_IMPULSE),
    in_impulseHistRightLabelMode=input.string(SHOW, "Impulse Hist Right-Side Label", options=(SHOW, HIDE), group=G_IMPULSE, tooltip=TT_IMPULSE_HIST),
    in_guideMode=input.string(GUIDE_LABELS, "Focused Guide Display", options=(GUIDE_LABELS, GUIDE_BOTH, GUIDE_HIDE), group=G_GUIDES, tooltip=TT_GUIDES),
    in_guideLineLastN=input.int(GUIDE_LINE_LAST_N_DEFAULT, "  ↳ Guide Line Last N Bars", minval=1, maxval=5000, group=G_GUIDES),
    in_guideLineWidth=input.int(GUIDE_LINE_WIDTH_DEFAULT, "  ↳ Guide Line Width", minval=1, maxval=5, group=G_GUIDES),
    in_guideLineTransp=input.int(78, "  ↳ Guide Line Transparency", minval=0, maxval=100, group=G_GUIDES),
    in_rightLabelPaddingMode=input.string(LABEL_PADDING_INDIVIDUAL, "Label Padding Mode", options=(LABEL_PADDING_GROUPED, LABEL_PADDING_INDIVIDUAL), group=G_RIGHT_LABELS, tooltip=TT_PADDING),
    in_rightLabelBasePad=input.int(2, "First Label Padding", minval=0, maxval=100, group=G_RIGHT_LABELS, tooltip=TT_PADDING),
    in_rightLabelPadStep=input.int(5, "Padding Between Labels", minval=1, maxval=40, group=G_RIGHT_LABELS, tooltip=TT_PADDING),
    in_priceOverlaySource=input.string(PRICE_SOURCE_MACD_HIST, "Price Pane Color Source", options=(PRICE_SOURCE_MACD_HIST, PRICE_SOURCE_IMPULSE_HIST), group=G_PRICE_OVERLAY, tooltip=TT_PRICE_OVERLAY),
    in_priceCandlesMode=input.string(SHOW, "Price Pane Candles", options=(SHOW, HIDE), group=G_PRICE_OVERLAY, tooltip=TT_PRICE_OVERLAY),
    in_priceCandleBodyTransp=input.int(75, "  ↳ Body Transparency", minval=0, maxval=100, group=G_PRICE_OVERLAY, tooltip=TT_PRICE_CANDLE_TRANSP),
    in_priceCandleWickTransp=input.int(0, "  ↳ Wick Transparency", minval=0, maxval=100, group=G_PRICE_OVERLAY, tooltip=TT_PRICE_CANDLE_TRANSP),
    in_priceCandleBorderTransp=input.int(0, "  ↳ Border Transparency", minval=0, maxval=100, group=G_PRICE_OVERLAY, tooltip=TT_PRICE_CANDLE_TRANSP)
):
    showMacdPair: bool = in_macdDisplayMode == SHOW
    showMacdFill: bool = in_macdFillMode == SHOW
    showMacdRightLabels: bool = in_macdRightLabelsMode == SHOW
    showMacdHist: bool = in_histDisplayMode == SHOW
    showMacdHistRightLabel: bool = in_histRightLabelMode == SHOW
    showHtfMacdHist: bool = in_htfHistDisplayMode == SHOW
    showHtfMacdHistRightLabel: bool = in_htfHistRightLabelMode == SHOW
    showImpulsePair: bool = in_impulseDisplayMode == SHOW
    showImpulseFill: bool = in_impulseFillMode == SHOW
    showImpulseRightLabels: bool = in_impulseRightLabelsMode == SHOW
    showImpulseHist: bool = in_impulseHistDisplayMode == SHOW
    showImpulseHistRightLabel: bool = in_impulseHistRightLabelMode == SHOW
    showGuideLabels: bool = in_guideMode != GUIDE_HIDE
    showGuideLines: bool = in_guideMode == GUIDE_BOTH
    guideEngineActive: bool = showGuideLabels or showGuideLines
    useGroupedRightLabelPadding: bool = in_rightLabelPaddingMode == LABEL_PADDING_GROUPED
    showPricePaneCandles: bool = in_priceCandlesMode == SHOW

    def f_dir(_x: float):
        return 1.0 if _x > 0.0 else -1.0 if _x < 0.0 else 0.0

    def f_lerp(_x: float, _x0: float, _x1: float, _y0: float, _y1: float):
        return _y1 if _x1 == _x0 else _y0 + (_x - _x0) / (_x1 - _x0) * (_y1 - _y0)

    def f_cap100(_x: float):
        return math.min(math.max(_x, 0.0), 100.0)

    def f_wideSemanticMag(_x: float):
        _m: float = math.abs(_x)
        _y: float = f_lerp(_m, 0.0, 0.7, 0.0, 34.0) if _m <= 0.7 else f_lerp(_m, 0.7, 1.25, 34.0, 55.0) if _m <= 1.25 else f_lerp(_m, 1.25, 2.5, 55.0, 65.0) if _m <= 2.5 else f_lerp(_m, 2.5, 4.0, 65.0, 75.0) if _m <= 4.0 else f_lerp(_m, 4.0, 7.0, 75.0, 89.0) if _m <= 7.0 else f_lerp(_m, 7.0, 12.0, 89.0, 95.0) if _m <= 12.0 else f_lerp(_m, 12.0, 20.0, 95.0, 100.0) if _m <= 20.0 else 100.0
        return f_cap100(_y)

    def f_wideSemantic(_x: float):
        return f_dir(_x) * f_wideSemanticMag(_x)

    def f_getNextTf():
        _mult: float = timeframe.multiplier
        _nextTf: str = "1D"

        if timeframe.isseconds:
            if timeframe.period == '1S':
                _nextTf = "5S"
            elif timeframe.period == '5S':
                _nextTf = "10S"
            elif timeframe.period == '10S':
                _nextTf = "15S"
            elif timeframe.period == '15S':
                _nextTf = "30S"
            elif timeframe.period == '30S':
                _nextTf = "45S"
            else:
                _nextTf = "1"
        elif timeframe.isminutes:
            if _mult <= 1:
                _nextTf = "3"
            elif _mult <= 2:
                _nextTf = "4"
            elif _mult <= 3:
                _nextTf = "5"
            elif _mult <= 5:
                _nextTf = "10"
            elif _mult <= 10:
                _nextTf = "15"
            elif _mult <= 15:
                _nextTf = "30"
            elif _mult <= 30:
                _nextTf = "60"
            elif _mult <= 60:
                _nextTf = "120"
            elif _mult <= 120:
                _nextTf = "240"
            elif _mult <= 240:
                _nextTf = "480"
            else:
                _nextTf = "D"
        elif timeframe.isdaily:
            _nextTf = "1W"
        elif timeframe.isweekly:
            _nextTf = "2W"
        elif timeframe.ismonthly:
            _nextTf = "2M"

        return _nextTf

    def f_prettyTfValue(_tf: str):
        _numericTf: float = string.tonumber(_tf)
        __block_result__ = na
        if not na(_numericTf):
            _minutes: int = cast_int(_numericTf)
            __block_result__ = string.tostring(cast_int(_minutes / 60)) + 'h' if _minutes >= 60 and _minutes % 60 == 0 else string.tostring(_minutes) + 'm'
        else:
            __block_result__ = '1D' if _tf == 'D' or _tf == '1D' else '1W' if _tf == 'W' or _tf == '1W' else '2W' if _tf == '2W' else '1M' if _tf == 'M' or _tf == '1M' else '2M' if _tf == '2M' else string.lower(_tf)
        return __block_result__

    def f_macdHistWideSemanticNative(_fastLen: int, _slowLen: int, _signalLen: int):
        _fast: float = ta.ema(close, _fastLen)
        _slow: float = ta.ema(close, _slowLen)
        _macd: float = _fast - _slow
        _signal: float = ta.ema(_macd, _signalLen)
        _hist: float = _macd - _signal
        _atr: float = ta.atr(ATR_LEN)
        _histAtr: float = _hist / _atr if not na(_atr) and _atr > 0.0 else na
        return f_wideSemantic(_histAtr) if not na(_histAtr) else na

    def f_padding(_n: int):
        return string.repeat('\u2003', math.max(_n, 0))

    def f_plain1Trim(_v: float):
        __block_result_1__ = na
        if na(_v):
            __block_result_1__ = "n/a"
        else:
            _oneDecimal: float = math.round(_v * 10.0) / 10.0
            _whole: float = math.round(_oneDecimal)
            __block_result_1__ = string.tostring(cast_int(_whole)) if math.abs(_oneDecimal - _whole) < 0.0001 else string.tostring(_oneDecimal, '#.0')
        return __block_result_1__

    def f_barsAgoText(_bars: int):
        return 'n/a' if na(_bars) else string.tostring(_bars) + 'ba'

    def f_buildRightLabelPads(_visible: list[bool], _extraAfter: list[int], _grouped: bool, _basePad: int, _step: int):
        _count: int = array.size(_visible)
        _pads: list[int] = array.new_int(_count, _basePad)
        _cursor: int = _basePad

        if _count > 0 and (not _grouped):
            for _index in pine_range(0, _count - 1):
                array.set(_pads, _index, _cursor)

                if array.get(_visible, _index):
                    _extra: int = array.get(_extraAfter, _index) if _index < array.size(_extraAfter) else 0

                    _cursor += _step + _extra

        return _pads

    def f_syncRightValueLabel(_label: Label, _show: bool, _x: int, _y: float, _text: str, _textColor: Color):
        _out: Label = _label
        _invisible: Color = color.new(color.black, 100)
        _valid: bool = _show and (not na(_x)) and (not na(_y))

        if _valid:
            if na(_out):
                _out = label.new(_x, _y, _text, xloc=xloc.bar_index, yloc=yloc.price, style=label.style_label_left, color=_invisible, textcolor=_textColor, textalign=text.align_center, size=size.normal)
            else:
                label.set_xy(_out, _x, _y)
                label.set_text(_out, _text)
                label.set_color(_out, _invisible)
                label.set_textcolor(_out, _textColor)
                label.set_style(_out, label.style_label_left)
                label.set_textalign(_out, text.align_center)
                label.set_size(_out, size.normal)
        elif not na(_out):
            label.delete(_out)
            _out = na

        return _out

    def f_guideStateColor(_level: float, _osc: float):
        return (COL_GUIDE_POS_PENDING if _level > 0.0 else COL_GUIDE_NEG_BELOW if _level < 0.0 else COL_GUIDE_ZERO) if na(_osc) else COL_POS_EXTREME if _level >= 100.0 - DIRECTION_EPS and _osc >= 100.0 - DIRECTION_EPS else COL_NEG_EXTREME if _level <= -100.0 + DIRECTION_EPS and _osc <= -100.0 + DIRECTION_EPS else (COL_GUIDE_NEG_BELOW if _osc <= _level else COL_GUIDE_NEG_PASSED) if _level < 0.0 else (COL_GUIDE_POS_PASSED if _osc > _level else COL_GUIDE_POS_PENDING) if _level > 0.0 else COL_GUIDE_ZERO

    def f_guideCaptureRadius(_levels: list[float], _index: int):
        _count: int = array.size(_levels)
        _level: float = array.get(_levels, _index)
        _leftGap: float = math.abs(_level - array.get(_levels, _index - 1)) if _index > 0 else na
        _rightGap: float = math.abs(array.get(_levels, _index + 1) - _level) if _index < _count - 1 else na

        _nearestGap: float = _rightGap if na(_leftGap) else _leftGap if na(_rightGap) else math.min(_leftGap, _rightGap)

        return math.max(GUIDE_PROXIMITY_FLOOR, _nearestGap * GUIDE_PROXIMITY_FRACTION)

    def f_guideLabelText(_level: float):
        return string.tostring(cast_int(math.round(_level)))

    def f_syncGuideLine(_line: Line, _show: bool, _left: int, _right: int, _level: float, _color: Color):
        _out: Line = _line
        _valid: bool = _show and (not na(_level)) and (_right >= _left)

        if _valid:
            _finalColor: Color = color.new(_color, in_guideLineTransp)
            _style: str = line.style_dashed if math.abs(_level) < 1e-06 else line.style_dotted

            if na(_out):
                _out = line.new(_left, _level, _right, _level, xloc=xloc.bar_index, extend=extend.none, color=_finalColor, style=_style, width=in_guideLineWidth)
            else:
                line.set_xy1(_out, _left, _level)
                line.set_xy2(_out, _right, _level)
                line.set_color(_out, _finalColor)
                line.set_style(_out, _style)
                line.set_width(_out, in_guideLineWidth)
        elif not na(_out):
            line.delete(_out)
            _out = na

        return _out

    def f_syncGuideLabel(_label: Label, _show: bool, _x: int, _level: float, _color: Color, _pad: int):
        _text: str = f_padding(_pad) + f_guideLabelText(_level)
        return f_syncRightValueLabel(_label, _show, _x, _level, _text, _color)

    atr14: float = ta.atr(ATR_LEN)

    macdFast: float = ta.ema(close, in_macdFastLen)
    macdSlow: float = ta.ema(close, in_macdSlowLen)
    macdRaw: float = macdFast - macdSlow
    macdSignalRaw: float = ta.ema(macdRaw, in_macdSignalLen)
    macdHistRaw: float = macdRaw - macdSignalRaw

    macdAtr: float = macdRaw / atr14 if not na(atr14) and atr14 > 0.0 else na
    macdSignalAtr: float = macdSignalRaw / atr14 if not na(atr14) and atr14 > 0.0 else na
    macdHistAtr: float = macdHistRaw / atr14 if not na(atr14) and atr14 > 0.0 else na

    macdLine: float = f_wideSemantic(macdAtr) if not na(macdAtr) else na
    macdSignalLine: float = f_wideSemantic(macdSignalAtr) if not na(macdSignalAtr) else na
    macdHist: float = f_wideSemantic(macdHistAtr) if not na(macdHistAtr) else na

    macdAboveSignal: bool = not na(macdRaw) and (not na(macdSignalRaw)) and (macdRaw > macdSignalRaw)
    macdSignalAbove: bool = not na(macdRaw) and (not na(macdSignalRaw)) and (macdSignalRaw > macdRaw)
    macdCross: bool = ta.cross(macdRaw, macdSignalRaw)

    macdBarsSinceCrossRaw: int = ta.barssince(macdCross)
    macdBarsSinceCross: int = na if na(macdBarsSinceCrossRaw) else macdBarsSinceCrossRaw + 1

    macdPairColor: Color = in_macdBullColor if macdAboveSignal else in_macdBearColor if macdSignalAbove else in_macdNeutralColor

    macdHistColor: Color = in_macdBullColor if macdHistRaw > 0.0 else in_macdBearColor if macdHistRaw < 0.0 else in_macdNeutralColor

    impulseSmmaHigh: float = ta.rma(high, in_impulseMaLen)
    impulseSmmaLow: float = ta.rma(low, in_impulseMaLen)

    impulseZlemaEma1: float = ta.ema(hlc3, in_impulseMaLen)
    impulseZlemaEma2: float = ta.ema(impulseZlemaEma1, in_impulseMaLen)
    impulseMidline: float = impulseZlemaEma1 + (impulseZlemaEma1 - impulseZlemaEma2)

    impulseRaw: float = impulseMidline - impulseSmmaHigh if impulseMidline > impulseSmmaHigh else impulseMidline - impulseSmmaLow if impulseMidline < impulseSmmaLow else 0.0

    impulseSignalRaw: float = ta.sma(impulseRaw, in_impulseSignalLen)
    impulseHistRaw: float = impulseRaw - impulseSignalRaw

    impulseAtr: float = impulseRaw / atr14 if not na(atr14) and atr14 > 0.0 else na
    impulseSignalAtr: float = impulseSignalRaw / atr14 if not na(atr14) and atr14 > 0.0 else na
    impulseHistAtr: float = impulseHistRaw / atr14 if not na(atr14) and atr14 > 0.0 else na

    impulseLine: float = f_wideSemantic(impulseAtr) if not na(impulseAtr) else na
    impulseSignalLine: float = f_wideSemantic(impulseSignalAtr) if not na(impulseSignalAtr) else na
    impulseHist: float = f_wideSemantic(impulseHistAtr) if not na(impulseHistAtr) else na

    impulseAboveSignal: bool = not na(impulseRaw) and (not na(impulseSignalRaw)) and (impulseRaw > impulseSignalRaw)
    impulseSignalAbove: bool = not na(impulseRaw) and (not na(impulseSignalRaw)) and (impulseSignalRaw > impulseRaw)
    impulseCross: bool = ta.cross(impulseRaw, impulseSignalRaw)

    impulseBarsSinceCrossRaw: int = ta.barssince(impulseCross)
    impulseBarsSinceCross: int = na if na(impulseBarsSinceCrossRaw) else impulseBarsSinceCrossRaw + 1

    impulsePairColor: Color = in_impulseBullColor if impulseAboveSignal else in_impulseBearColor if impulseSignalAbove else in_impulseNeutralColor

    impulseHistColor: Color = in_impulseBullColor if impulseHistRaw > 0.0 else in_impulseBearColor if impulseHistRaw < 0.0 else in_impulseNeutralColor

    macdHistHtfTf: str = f_getNextTf()

    macdHistHtfDeveloping: float = request.security(syminfo.tickerid, macdHistHtfTf, f_macdHistWideSemanticNative(in_macdFastLen, in_macdSlowLen, in_macdSignalLen), gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off)

    macdHistHtfColor: Color = in_macdBullColor if macdHistHtfDeveloping > 0.0 else in_macdBearColor if macdHistHtfDeveloping < 0.0 else in_macdNeutralColor

    useImpulsePriceOverlay: bool = in_priceOverlaySource == PRICE_SOURCE_IMPULSE_HIST

    pricePaneBaseColor: Color = impulseHistColor if useImpulsePriceOverlay else macdHistColor

    pricePaneCandleBodyColor: Color = color.new(pricePaneBaseColor, in_priceCandleBodyTransp)
    pricePaneCandleWickColor: Color = color.new(pricePaneBaseColor, in_priceCandleWickTransp)
    pricePaneCandleBorderColor: Color = color.new(pricePaneBaseColor, in_priceCandleBorderTransp)

    plot(impulseHist if showImpulseHist else na, title='Impulse Hist — NMS', color=color.new(impulseHistColor, in_impulseHistTransp), linewidth=in_impulseHistWidth, style=plot.style_columns if in_impulseHistStyle == STYLE_COLUMNS else plot.style_histogram if in_impulseHistStyle == STYLE_HISTOGRAM else plot.style_line, histbase=0.0, show_last=in_impulseLastN)

    plotImpulseFillAnchor = plot(impulseLine if showImpulseFill else na, title='Impulse Fill Anchor', color=color.new(impulsePairColor, 100), linewidth=1, style=plot.style_line, show_last=in_impulseLastN)

    plotImpulseSignalFillAnchor = plot(impulseSignalLine if showImpulseFill else na, title='Impulse Signal Fill Anchor', color=color.new(impulsePairColor, 100), linewidth=1, style=plot.style_line, show_last=in_impulseLastN)

    fill(plotImpulseFillAnchor, plotImpulseSignalFillAnchor, color=color.new(impulsePairColor, in_impulseFillTransp) if showImpulseFill else na, title='Impulse / Signal Fill', show_last=in_impulseLastN, fillgaps=False)

    plot(impulseLine if showImpulsePair else na, title='ImpulseMACD — NMS', color=color.new(impulsePairColor, in_impulseTransp), linewidth=in_impulseWidth, style=plot.style_columns if in_impulseMacdStyle == STYLE_COLUMNS else plot.style_histogram if in_impulseMacdStyle == STYLE_HISTOGRAM else plot.style_line, histbase=0.0, show_last=in_impulseLastN)

    plot(impulseSignalLine if showImpulsePair else na, title='Impulse Signal — NMS', color=color.new(impulsePairColor, in_impulseTransp), linewidth=in_impulseWidth, style=plot.style_columns if in_impulseSignalStyle == STYLE_COLUMNS else plot.style_histogram if in_impulseSignalStyle == STYLE_HISTOGRAM else plot.style_line, histbase=0.0, show_last=in_impulseLastN)

    plot(macdHist if showMacdHist else na, title='MACD Histogram — NMS', color=color.new(macdHistColor, in_histTransp), linewidth=in_histWidth, style=plot.style_columns if in_histStyle == STYLE_COLUMNS else plot.style_histogram if in_histStyle == STYLE_HISTOGRAM else plot.style_line, histbase=0.0, show_last=in_histLastN)

    plot(macdHistHtfDeveloping if showHtfMacdHist else na, title='Developing HTF MACD Histogram — NMS', color=color.new(macdHistHtfColor, in_htfHistTransp), linewidth=in_htfHistWidth, style=plot.style_columns if in_htfHistStyle == STYLE_COLUMNS else plot.style_histogram if in_htfHistStyle == STYLE_HISTOGRAM else plot.style_line, histbase=0.0, show_last=in_htfHistLastN)

    plotMacdFillAnchor = plot(macdLine if showMacdFill else na, title='MACD Fill Anchor', color=color.new(macdPairColor, 100), linewidth=1, style=plot.style_line, show_last=in_macdLastN)

    plotMacdSignalFillAnchor = plot(macdSignalLine if showMacdFill else na, title='MACD Signal Fill Anchor', color=color.new(macdPairColor, 100), linewidth=1, style=plot.style_line, show_last=in_macdLastN)

    fill(plotMacdFillAnchor, plotMacdSignalFillAnchor, color=color.new(macdPairColor, in_macdFillTransp) if showMacdFill else na, title='MACD / Signal Fill', show_last=in_macdLastN, fillgaps=False)

    plot(macdLine if showMacdPair else na, title='MACD — NMS', color=color.new(macdPairColor, in_macdTransp), linewidth=in_macdWidth, style=plot.style_columns if in_macdStyle == STYLE_COLUMNS else plot.style_histogram if in_macdStyle == STYLE_HISTOGRAM else plot.style_line, histbase=0.0, show_last=in_macdLastN)

    plot(macdSignalLine if showMacdPair else na, title='MACD Signal — NMS', color=color.new(macdPairColor, in_macdTransp), linewidth=in_macdWidth, style=plot.style_columns if in_macdStyle == STYLE_COLUMNS else plot.style_histogram if in_macdStyle == STYLE_HISTOGRAM else plot.style_line, histbase=0.0, show_last=in_macdLastN)

    plotcandle(open=open if showPricePaneCandles else na, high=high if showPricePaneCandles else na, low=low if showPricePaneCandles else na, close=close if showPricePaneCandles else na, title='NMS Price Pane Candles', color=pricePaneCandleBodyColor if showPricePaneCandles else na, wickcolor=pricePaneCandleWickColor if showPricePaneCandles else na, bordercolor=pricePaneCandleBorderColor if showPricePaneCandles else na, force_overlay=True, editable=False)

    plot(close, title='NMS Price Bar-to-Bar Follow Line', color=color.new(pricePaneBaseColor, PRICE_FOLLOW_TRANSP), linewidth=PRICE_FOLLOW_WIDTH, style=plot.style_linebr, show_last=PRICE_FOLLOW_LAST_N, force_overlay=True, editable=False)

    guideRightPad: int = in_rightLabelBasePad
    macdHistRightPad: int = in_rightLabelBasePad
    macdRightPad: int = in_rightLabelBasePad
    macdSignalRightPad: int = in_rightLabelBasePad
    htfMacdHistRightPad: int = in_rightLabelBasePad
    impulseHistRightPad: int = in_rightLabelBasePad
    impulseRightPad: int = in_rightLabelBasePad
    impulseSignalRightPad: int = in_rightLabelBasePad

    if barstate.islast:
        _rightLabelVisible: list[bool] = array.from_items(showGuideLabels, showMacdHistRightLabel and (not na(macdHist)), showMacdRightLabels and (not na(macdLine)), showMacdRightLabels and (not na(macdSignalLine)), showHtfMacdHistRightLabel and (not na(macdHistHtfDeveloping)), showImpulseHistRightLabel and (not na(impulseHist)), showImpulseRightLabels and (not na(impulseLine)), showImpulseRightLabels and (not na(impulseSignalLine)))

        _rightLabelExtraAfter: list[int] = array.from_items(0, 0, 0, 0, 0, 0, 2, 0)

        _rightLabelPads: list[int] = f_buildRightLabelPads(_rightLabelVisible, _rightLabelExtraAfter, useGroupedRightLabelPadding, in_rightLabelBasePad, in_rightLabelPadStep)

        guideRightPad = array.get(_rightLabelPads, 0)
        macdHistRightPad = array.get(_rightLabelPads, 1)
        macdRightPad = array.get(_rightLabelPads, 2)
        macdSignalRightPad = array.get(_rightLabelPads, 3)
        htfMacdHistRightPad = array.get(_rightLabelPads, 4)
        impulseHistRightPad = array.get(_rightLabelPads, 5)
        impulseRightPad = array.get(_rightLabelPads, 6)
        impulseSignalRightPad = array.get(_rightLabelPads, 7) if useGroupedRightLabelPadding else math.max(array.get(_rightLabelPads, 7) - 1, 0)

    guideLevels: Persistent[list[float]] = array.from_items(-100.0, -89.0, -75.0, -55.0, -34.0, -13.0, 0.0, 13.0, 34.0, 55.0, 75.0, 89.0, 100.0)

    guideLines: Persistent[list[Line]] = array.new_line()
    guideLabels: Persistent[list[Label]] = array.new_label()

    if barstate.islast and guideEngineActive:
        _count: int = array.size(guideLevels)

        _visibleGuideValues: list[float] = array.new_float()

        _macdPairGeometryVisible: bool = showMacdPair or showMacdFill
        _impulsePairGeometryVisible: bool = showImpulsePair or showImpulseFill

        if _macdPairGeometryVisible:
            if not na(macdLine):
                array.push(_visibleGuideValues, macdLine)

            if not na(macdSignalLine):
                array.push(_visibleGuideValues, macdSignalLine)

        if showMacdHist and (not na(macdHist)):
            array.push(_visibleGuideValues, macdHist)

        if showHtfMacdHist and (not na(macdHistHtfDeveloping)):
            array.push(_visibleGuideValues, macdHistHtfDeveloping)

        if _impulsePairGeometryVisible:
            if not na(impulseLine):
                array.push(_visibleGuideValues, impulseLine)

            if not na(impulseSignalLine):
                array.push(_visibleGuideValues, impulseSignalLine)

        if showImpulseHist and (not na(impulseHist)):
            array.push(_visibleGuideValues, impulseHist)

        _visibleMax: float = na(float)
        _visibleMin: float = na(float)
        _visibleCount: int = array.size(_visibleGuideValues)

        if _visibleCount > 0:
            for _valueIndex in pine_range(0, _visibleCount - 1):
                _value: float = array.get(_visibleGuideValues, _valueIndex)
                _visibleMax = _value if na(_visibleMax) else math.max(_visibleMax, _value)
                _visibleMin = _value if na(_visibleMin) else math.min(_visibleMin, _value)

        _rightIndex: int = bar_index
        _leftIndex: int = math.max(bar_index - in_guideLineLastN + 1, 0)

        if showGuideLines:
            while array.size(guideLines) < _count:
                array.push(guideLines, na)

        if showGuideLabels:
            while array.size(guideLabels) < _count:
                array.push(guideLabels, na)

        for _index in pine_range(0, _count - 1):
            _level: float = array.get(guideLevels, _index)
            _isZero: bool = math.abs(_level) < 1e-06
            _captureRadius: float = f_guideCaptureRadius(guideLevels, _index)

            _nearVisibleGeometry: bool = False

            if not _isZero and _visibleCount > 0:
                for _valueIndex in pine_range(0, _visibleCount - 1):
                    _value: float = array.get(_visibleGuideValues, _valueIndex)

                    if math.abs(_value - _level) <= _captureRadius:
                        _nearVisibleGeometry = True
                        break

            _ceilingEligible: bool = not na(_visibleMax) and _visibleMax > 95.0 if _level >= 100.0 - DIRECTION_EPS else not na(_visibleMin) and _visibleMin < -95.0 if _level <= -100.0 + DIRECTION_EPS else True

            _showLevel: bool = _isZero or (_nearVisibleGeometry and _ceilingEligible)

            _guideColor: Color = f_guideStateColor(_level, macdLine)

            if showGuideLines:
                _line: Line = array.get(guideLines, _index)
                _line = f_syncGuideLine(_line, _showLevel, _leftIndex, _rightIndex, _level, _guideColor)
                array.set(guideLines, _index, _line)

            if showGuideLabels:
                _label: Label = array.get(guideLabels, _index)
                _label = f_syncGuideLabel(_label, _showLevel, _rightIndex, _level, _guideColor, guideRightPad)
                array.set(guideLabels, _index, _label)
    elif barstate.islast and (not guideEngineActive):
        _lineCount: int = array.size(guideLines)
        if _lineCount > 0:
            for _i in pine_range(0, _lineCount - 1):
                _line: Line = array.get(guideLines, _i)
                if not na(_line):
                    line.delete(_line)
                    array.set(guideLines, _i, na)

        _labelCount: int = array.size(guideLabels)
        if _labelCount > 0:
            for _i in pine_range(0, _labelCount - 1):
                _label: Label = array.get(guideLabels, _i)
                if not na(_label):
                    label.delete(_label)
                    array.set(guideLabels, _i, na)

    macdRightLabel: Persistent[Label] = na(Label)
    macdSignalRightLabel: Persistent[Label] = na(Label)
    macdHistRightLabel: Persistent[Label] = na(Label)
    htfMacdHistRightLabel: Persistent[Label] = na(Label)
    impulseRightLabel: Persistent[Label] = na(Label)
    impulseSignalRightLabel: Persistent[Label] = na(Label)
    impulseHistRightLabel: Persistent[Label] = na(Label)

    if barstate.islast:
        _macdSpacer: str = f_padding(macdRightPad)
        _macdSignalSpacer: str = f_padding(macdSignalRightPad)
        _histSpacer: str = f_padding(macdHistRightPad)
        _htfHistSpacer: str = f_padding(htfMacdHistRightPad)
        _impulseSpacer: str = f_padding(impulseRightPad)
        _impulseSignalSpacer: str = f_padding(impulseSignalRightPad)
        _impulseHistSpacer: str = f_padding(impulseHistRightPad)

        _macdText: str = _macdSpacer + 'MACD' + '\n' + _macdSpacer + f_plain1Trim(macdLine) + ('\n' + _macdSpacer + f_barsAgoText(macdBarsSinceCross) if macdAboveSignal else '')

        _macdSignalText: str = _macdSignalSpacer + 'MACD' + '\n' + _macdSignalSpacer + 'Signal' + '\n' + _macdSignalSpacer + f_plain1Trim(macdSignalLine) + ('\n' + _macdSignalSpacer + f_barsAgoText(macdBarsSinceCross) if macdSignalAbove else '')

        _histText: str = _histSpacer + 'MACD' + '\n' + _histSpacer + 'Hist' + '\n' + _histSpacer + f_plain1Trim(macdHist)

        _htfHistText: str = _htfHistSpacer + f_prettyTfValue(macdHistHtfTf) + '\n' + _htfHistSpacer + 'MACD' + '\n' + _htfHistSpacer + 'Hist' + '\n' + _htfHistSpacer + f_plain1Trim(macdHistHtfDeveloping)

        _impulseText: str = _impulseSpacer + 'Impulse' + '\n' + _impulseSpacer + 'MACD' + '\n' + _impulseSpacer + f_plain1Trim(impulseLine) + ('\n' + _impulseSpacer + f_barsAgoText(impulseBarsSinceCross) if impulseAboveSignal else '')

        _impulseSignalText: str = _impulseSignalSpacer + 'Impulse' + '\n' + _impulseSignalSpacer + 'Signal' + '\n' + _impulseSignalSpacer + f_plain1Trim(impulseSignalLine) + ('\n' + _impulseSignalSpacer + f_barsAgoText(impulseBarsSinceCross) if impulseSignalAbove else '')

        _impulseHistText: str = _impulseHistSpacer + 'Impulse' + '\n' + _impulseHistSpacer + 'Hist' + '\n' + _impulseHistSpacer + f_plain1Trim(impulseHist)

        macdRightLabel = f_syncRightValueLabel(macdRightLabel, showMacdRightLabels, bar_index, macdLine, _macdText, macdPairColor)

        macdSignalRightLabel = f_syncRightValueLabel(macdSignalRightLabel, showMacdRightLabels, bar_index, macdSignalLine, _macdSignalText, macdPairColor)

        macdHistRightLabel = f_syncRightValueLabel(macdHistRightLabel, showMacdHistRightLabel, bar_index, macdHist, _histText, macdHistColor)

        htfMacdHistRightLabel = f_syncRightValueLabel(htfMacdHistRightLabel, showHtfMacdHistRightLabel, bar_index, macdHistHtfDeveloping, _htfHistText, macdHistHtfColor)

        impulseRightLabel = f_syncRightValueLabel(impulseRightLabel, showImpulseRightLabels, bar_index, impulseLine, _impulseText, impulsePairColor)

        impulseSignalRightLabel = f_syncRightValueLabel(impulseSignalRightLabel, showImpulseRightLabels, bar_index, impulseSignalLine, _impulseSignalText, impulsePairColor)

        impulseHistRightLabel = f_syncRightValueLabel(impulseHistRightLabel, showImpulseHistRightLabel, bar_index, impulseHist, _impulseHistText, impulseHistColor)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)