"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, barcolor, barstate, bgcolor, close, color,
    input, label, math, na, nz, plot, script, size, ta, xloc
)
from pynecore.types import Color, Label, Persistent, PersistentSeries, Series

ewmac_settings: str = "════════ EWMAC Settings ════════"
volatility_settings: str = "════════ Volatility Settings ════════"
score_settings: str = "════════ Score Settings ════════"
signal_settings: str = "════════ Signal Settings ════════"
visual_settings: str = "════════ Visualization Settings ════════"
tooltip_preset: str = "Select a predefined configuration for different trading styles and timeframes. Fast Response and Smooth Trend set the active rules, Volatility Length, Long-Run Weight, Long-Run Length, Adaptive Scaling Length, Entry Threshold, and Exit Fraction, overriding those inputs below. Rule spans, rule weights, and all other inputs keep their manual values."
tooltip_preset_det: str = "Default: Uses the manual settings below, with every rule, volatility, score, and signal parameter adjustable directly. Suited to swing trading on 4H and daily charts.\n\nFast Response (Rules 1-4, Entry 2.5): Activates the four fastest EWMAC pairs with a shorter volatility window and a lower entry threshold, so signals react to shorter-duration moves. Suited to intraday trading on 5min to 1H charts.\n\nSmooth Trend (Rules 4-6, Entry 6.0): Activates the three slowest EWMAC pairs with a longer volatility window and a higher entry threshold, so signals change less often and stay with longer trends. Suited to position trading on daily and weekly charts."
tooltip_src: str = "Price data used for the EWMAC rules, the volatility estimate, and the trend line. Close uses the final price of each bar, while hl2, hlc3, and ohlc4 average more of each bar's range. Averaged sources lower the volatility estimate relative to close, which produces larger scores when Scaling Method is set to Fixed. In Adaptive mode, the scaling recalibrates to the selected source automatically. Built for price series that stay above zero, such as stocks, crypto, forex, commodities, and indices. Spreads and other series that can reach zero or turn negative are outside its scope."
tooltip_rule1: str = "Fastest EWMAC pair. Enable the rule, set the fast EMA span, and set its weight relative to the other active rules. The slow EMA span is always four times the fast span. This speed responds to the shortest price swings and is the first to turn when direction changes. Active in the Fast Response preset. A weight of 0 removes the rule from both the trend score and the trend line."
tooltip_rule2: str = "Short-term EWMAC pair. Enable the rule, set the fast EMA span, and set its weight relative to the other active rules. The slow EMA span is always four times the fast span. This speed tracks short-term swings and reacts early to new trends. Active in the Fast Response preset. A weight of 0 removes the rule from both the trend score and the trend line."
tooltip_rule3: str = "Short to medium-term EWMAC pair. Enable the rule, set the fast EMA span, and set its weight relative to the other active rules. The slow EMA span is always four times the fast span. This speed follows developing trends while still reacting to shorter swings. Active in the Fast Response preset. A weight of 0 removes the rule from both the trend score and the trend line."
tooltip_rule4: str = "Medium-term EWMAC pair. Enable the rule, set the fast EMA span, and set its weight relative to the other active rules. The slow EMA span is always four times the fast span. This speed follows established trends. Active in both the Fast Response and Smooth Trend presets. A weight of 0 removes the rule from both the trend score and the trend line."
tooltip_rule5: str = "Medium to long-term EWMAC pair. Enable the rule, set the fast EMA span, and set its weight relative to the other active rules. The slow EMA span is always four times the fast span. This speed follows sustained trends and filters out shorter swings. Active in the Smooth Trend preset. A weight of 0 removes the rule from both the trend score and the trend line."
tooltip_rule6: str = "Slowest EWMAC pair. Enable the rule, set the fast EMA span, and set its weight relative to the other active rules. The slow EMA span is always four times the fast span. This speed follows long-term trends, turns last when direction changes, and holds its direction the longest. Active in the Smooth Trend preset. A weight of 0 removes the rule from both the trend score and the trend line."
tooltip_vol_len: str = "Lookback for the realized volatility estimate that converts every EWMAC pair into risk units, making scores comparable across instruments and volatility regimes. Shorter windows (16-24) track volatility changes quickly, so scores adjust faster when conditions shift but vary more from bar to bar. Longer windows (48-64) produce a steadier risk unit and smoother scores that adapt more gradually to new volatility conditions."
tooltip_blend_weight: str = "Share of the volatility estimate drawn from its long-run average rather than the short window. A volatility spike raises the short-window estimate and compresses scores, while a quiet stretch lowers it and enlarges them, and blending in the long-run average moderates both effects. At 0, the risk unit uses the short-window estimate alone and responds fully to current conditions. Lower values (0.10-0.20) keep the risk unit close to current volatility, so scores adapt quickly to regime changes. Higher values (0.40-0.60) anchor the risk unit to the long-run average, keeping scores more comparable across long histories while adjusting more gradually when volatility shifts."
tooltip_blend_len: str = "Window used to calculate the long-run volatility average. Longer windows (750-1000) span more volatility regimes and produce a steadier anchor. Shorter windows (250-400) let the anchor follow more recent conditions. Until enough bars are available to fill this window, the short-window estimate is used on its own. Has no effect when Long-Run Weight is set to 0."
tooltip_scaling_mode: str = "Method used to rescale each rule so its average absolute score is 10, placing every speed on the same scale before blending. Adaptive estimates each rule's scaling from its own recent history on the charted instrument, so the scaling adjusts to each instrument automatically. Fixed derives each rule's scaling from its fast EMA span alone, so the scaling stays identical across the full chart history and across instruments."
tooltip_scaling_len: str = "Window used to estimate each rule's scaling in Adaptive mode. Shorter windows (100-150) recalibrate quickly, so scores measure trend strength against more recent conditions. Longer windows (400-750) keep the scaling steadier, so scores stay comparable across a longer stretch of history. Until enough bars are available to fill this window, each rule uses Fixed scaling. Only active when Scaling Method is set to Adaptive."
tooltip_multiplier: str = "Restores the scale lost when several partially correlated rules are averaged into the trend score. At 0, the multiplier is selected automatically from the number of active rules, ranging from 1.00 for one rule to 1.36 for six, so the Entry Threshold keeps a similar meaning as rules are enabled or disabled. Values above 0 set the multiplier manually, and 1.00 leaves the trend score as the plain weighted average of the active rules. Lower values (1.00-1.10) suit closely spaced rules whose scores move together. Higher values (1.30-1.50) suit widely spaced rules that diversify more, and enlarge the trend score so it crosses the Entry Threshold sooner and falls back through the exit level later."
tooltip_score_cap: str = "Maximum absolute value allowed for each rule score and for the trend score. Lower caps (10-15) limit how far any single rule can pull the blend during sharp moves, keeping the trend score balanced across speeds. Higher caps (30-50) let strong rules contribute more of their full score. Keep the cap above the Entry Threshold so signals can confirm."
tooltip_entry: str = "Trend score level required to confirm a bullish or bearish signal. Scores are scaled so that 10 is the average absolute value, which makes the threshold directly interpretable: a threshold of 5 requires 50% of typical trend strength before a signal is confirmed. Lower values (2.0-3.0) confirm trends earlier with more frequent signals. Higher values (6.0-8.0) wait for stronger trends, producing fewer and later signals."
tooltip_neutral_state: str = "Enable/disable the neutral state. When enabled, a bullish or bearish signal releases to neutral once the trend score falls back through the exit level set by Exit Fraction, and the trend line switches to the neutral color. This separates fading trends from confirmed reversals. When disabled, each signal holds until the opposite Entry Threshold is crossed, so every bar is classified as bullish or bearish once the first signal is confirmed."
tooltip_exit_frac: str = "Exit level as a fraction of the Entry Threshold, forming a hysteresis band around confirmed signals. With an Entry Threshold of 6.0 and an Exit Fraction of 0.50, a bullish signal releases to neutral when the trend score falls below 3.0, and a bearish signal releases when it rises above -3.0. Lower values (0.25-0.35) keep signals active through deeper fades in trend strength. Higher values (0.70-0.90) release signals sooner as trend strength fades. Only active when Use Neutral State is enabled."
tooltip_color_preset: str = "Pre-configured color schemes for different chart themes and visual preferences. Classic uses traditional green and red. Aqua provides ocean-inspired blue and orange. Cosmic offers futuristic cyan and purple. Cyber features cool cyan and warm orange contrast. Neon delivers high-contrast yellow and magenta for maximum visibility. Custom uses the Bullish, Bearish, and Neutral colors set below, while all other presets use gray for the neutral state."
tooltip_bullish: str = "Color applied to the trend line, glow effect, signal readout, price bars, and background while the signal is bullish, which is confirmed when the trend score rises above the Entry Threshold. Use a vibrant color to highlight uptrend phases and potential long opportunities. Only used when Color Preset is set to Custom."
tooltip_bearish: str = "Color applied to the trend line, glow effect, signal readout, price bars, and background while the signal is bearish, which is confirmed when the trend score falls below the negative Entry Threshold. Use a warning color to highlight downtrend phases and potential short opportunities or exits. Only used when Color Preset is set to Custom."
tooltip_neutral_color: str = "Color applied to the trend line, glow effect, signal readout, price bars, and background while the signal is neutral, including the warm-up period before the first signal is confirmed. Gray is recommended as a neutral cue that clearly separates undecided phases from directional trends. Only used when Color Preset is set to Custom."
tooltip_line_width: str = "Thickness of the main trend line. The trend line is built from the same EWMAC pairs and rule weights as the trend score, and its color reflects the current signal. Lower values (1-2) keep the line clean alongside price action. Higher values (4-6) make the line and its signal color changes easier to follow on busy charts. The glow effect uses its own fixed widths."
tooltip_glow: str = "Enable/disable the neon glow effect around the trend line. When enabled, creates a layered visual effect with overlapping plots at increasing transparency, making the trend line and its signal color changes more prominent and easier to track. Disable for a cleaner, minimalist appearance or when running many indicators where visual clarity is paramount."
tooltip_readout: str = "Enable/disable the signal readout attached to the end of the trend line. The readout names the current signal as Bullish, Bearish, or Neutral on a label filled with the matching signal color, and its text switches automatically between black and white based on how light that color is, so it stays readable with any color choice on light or dark charts. All signals and alerts continue to work with the readout hidden."
tooltip_readout_size: str = "Text size for the signal readout. Tiny and Small suit crowded charts or lower timeframes where signals change often. Normal and Large suit presentation, screen recording, and higher timeframes."
tooltip_barcolor: str = "Enable/disable bar coloring based on the current signal. When enabled, price bars are tinted with the bullish, bearish, or neutral color, providing instant visual confirmation of the signal without reading the trend line directly. Disable if you prefer default bar colors or use another bar coloring indicator."
tooltip_bartrans: str = "Transparency of the bar coloring overlay. Lower values (0-30) produce vivid, fully saturated bars that make the signal immediately obvious. Higher values (70-90) apply a subtle tint that shows the signal without overwhelming price action. Only applies when Enable Bar Coloring is turned on."
tooltip_bgcolor: str = "Enable/disable background coloring based on the current signal. When enabled, the chart background is shaded with the bullish, bearish, or neutral color, highlighting each trend phase across the full height of the chart. Disable if you prefer a clean chart background or use another background coloring indicator."
tooltip_bgtrans: str = "Transparency of the background coloring. Lower values (50-70) produce strong shading that makes each trend phase stand out immediately. Higher values (85-95) apply a subtle tint that keeps price action and other chart elements easy to read. Only applies when Enable Background Coloring is turned on."


@script.indicator("EWMAC Trend Signals [QuantAlgo]", overlay=True)
def main(
    presetMode=input.string("Default", "Preset Configuration", group=ewmac_settings, options=("Default", "Fast Response", "Smooth Trend"), tooltip=tooltip_preset + '\n\n' + tooltip_preset_det),
    srcInput: Series[float] = input.source(close, "Price Source", group=ewmac_settings, tooltip=tooltip_src),
    r1On=input.bool(False, "Rule 1", group=ewmac_settings, inline="R1"),
    r1Len=input.int(2, "", group=ewmac_settings, inline="R1", minval=1, maxval=500),
    r1W=input.float(1.0, "", group=ewmac_settings, inline="R1", minval=0.0, maxval=10.0, step=0.1, tooltip=tooltip_rule1),
    r2On=input.bool(True, "Rule 2", group=ewmac_settings, inline="R2"),
    r2Len=input.int(4, "", group=ewmac_settings, inline="R2", minval=1, maxval=500),
    r2W=input.float(1.0, "", group=ewmac_settings, inline="R2", minval=0.0, maxval=10.0, step=0.1, tooltip=tooltip_rule2),
    r3On=input.bool(True, "Rule 3", group=ewmac_settings, inline="R3"),
    r3Len=input.int(8, "", group=ewmac_settings, inline="R3", minval=1, maxval=500),
    r3W=input.float(1.0, "", group=ewmac_settings, inline="R3", minval=0.0, maxval=10.0, step=0.1, tooltip=tooltip_rule3),
    r4On=input.bool(True, "Rule 4", group=ewmac_settings, inline="R4"),
    r4Len=input.int(16, "", group=ewmac_settings, inline="R4", minval=1, maxval=500),
    r4W=input.float(1.0, "", group=ewmac_settings, inline="R4", minval=0.0, maxval=10.0, step=0.1, tooltip=tooltip_rule4),
    r5On=input.bool(True, "Rule 5", group=ewmac_settings, inline="R5"),
    r5Len=input.int(32, "", group=ewmac_settings, inline="R5", minval=1, maxval=500),
    r5W=input.float(1.0, "", group=ewmac_settings, inline="R5", minval=0.0, maxval=10.0, step=0.1, tooltip=tooltip_rule5),
    r6On=input.bool(False, "Rule 6", group=ewmac_settings, inline="R6"),
    r6Len=input.int(64, "", group=ewmac_settings, inline="R6", minval=1, maxval=500),
    r6W=input.float(1.0, "", group=ewmac_settings, inline="R6", minval=0.0, maxval=10.0, step=0.1, tooltip=tooltip_rule6),
    volLenIn=input.int(32, "Volatility Length", group=volatility_settings, minval=5, maxval=500, tooltip=tooltip_vol_len),
    blendWeightIn=input.float(0.3, "Long-Run Weight", group=volatility_settings, minval=0.0, maxval=1.0, step=0.05, tooltip=tooltip_blend_weight),
    blendLenIn=input.int(500, "Long-Run Length", group=volatility_settings, minval=50, maxval=5000, tooltip=tooltip_blend_len),
    scalingMode=input.string("Adaptive", "Scaling Method", group=score_settings, options=("Adaptive", "Fixed"), tooltip=tooltip_scaling_mode),
    scalingLenIn=input.int(250, "Adaptive Scaling Length", group=score_settings, minval=20, maxval=2000, tooltip=tooltip_scaling_len),
    multiplierIn=input.float(0.0, "Diversification Multiplier (0 = Auto)", group=score_settings, minval=0.0, maxval=3.0, step=0.01, tooltip=tooltip_multiplier),
    scoreCap=input.float(20.0, "Score Cap", group=score_settings, minval=5.0, maxval=100.0, step=1.0, tooltip=tooltip_score_cap),
    entryThIn=input.float(4.0, "Entry Threshold", group=signal_settings, minval=0.5, maxval=20.0, step=0.5, tooltip=tooltip_entry),
    useNeutral=input.bool(True, "Use Neutral State", group=signal_settings, tooltip=tooltip_neutral_state),
    exitFracIn=input.float(0.5, "Exit Fraction", group=signal_settings, minval=0.0, maxval=1.0, step=0.05, tooltip=tooltip_exit_frac),
    colorPreset=input.string("Custom", "Color Preset", group=visual_settings, options=("Custom", "Classic", "Aqua", "Cosmic", "Cyber", "Neon"), tooltip=tooltip_color_preset),
    bullCustom=input.color(color.new('#00FFAA'), "Bullish Color", group=visual_settings, tooltip=tooltip_bullish),
    bearCustom=input.color(color.new('#FF0000'), "Bearish Color", group=visual_settings, tooltip=tooltip_bearish),
    neutCustom=input.color(color.new('#808080'), "Neutral Color", group=visual_settings, tooltip=tooltip_neutral_color),
    lineWidth=input.int(3, "Line Width", group=visual_settings, minval=1, maxval=8, tooltip=tooltip_line_width),
    showGlow=input.bool(True, "Enable Neon Glow Effect", group=visual_settings, tooltip=tooltip_glow),
    showReadout=input.bool(True, "Enable Signal Readout", group=visual_settings, tooltip=tooltip_readout),
    readoutSize=input.string("Normal", "Readout Text Size", group=visual_settings, options=("Tiny", "Small", "Normal", "Large"), tooltip=tooltip_readout_size),
    colorBars=input.bool(True, "Enable Bar Coloring", group=visual_settings, tooltip=tooltip_barcolor),
    barTrans=input.int(0, "Bar Color Transparency", group=visual_settings, minval=0, maxval=100, tooltip=tooltip_bartrans),
    colorBg=input.bool(False, "Enable Background Coloring", group=visual_settings, tooltip=tooltip_bgcolor),
    bgTrans=input.int(90, "Background Color Transparency", group=visual_settings, minval=0, maxval=100, tooltip=tooltip_bgtrans)
):
    __block_result__ = na
    __switch__ = presetMode
    if __switch__ == "Fast Response":
        __block_result__ = True
    elif __switch__ == "Smooth Trend":
        __block_result__ = False
    else:
        __block_result__ = r1On
    p1: bool = __block_result__

    __block_result_1__ = na
    __switch__ = presetMode
    if __switch__ == "Fast Response":
        __block_result_1__ = True
    elif __switch__ == "Smooth Trend":
        __block_result_1__ = False
    else:
        __block_result_1__ = r2On
    p2: bool = __block_result_1__

    __block_result_2__ = na
    __switch__ = presetMode
    if __switch__ == "Fast Response":
        __block_result_2__ = True
    elif __switch__ == "Smooth Trend":
        __block_result_2__ = False
    else:
        __block_result_2__ = r3On
    p3: bool = __block_result_2__

    __block_result_3__ = na
    __switch__ = presetMode
    if __switch__ == "Fast Response":
        __block_result_3__ = True
    elif __switch__ == "Smooth Trend":
        __block_result_3__ = True
    else:
        __block_result_3__ = r4On
    p4: bool = __block_result_3__

    __block_result_4__ = na
    __switch__ = presetMode
    if __switch__ == "Fast Response":
        __block_result_4__ = False
    elif __switch__ == "Smooth Trend":
        __block_result_4__ = True
    else:
        __block_result_4__ = r5On
    p5: bool = __block_result_4__

    __block_result_5__ = na
    __switch__ = presetMode
    if __switch__ == "Fast Response":
        __block_result_5__ = False
    elif __switch__ == "Smooth Trend":
        __block_result_5__ = True
    else:
        __block_result_5__ = r6On
    p6: bool = __block_result_5__

    __block_result_6__ = na
    __switch__ = presetMode
    if __switch__ == "Fast Response":
        __block_result_6__ = 16
    elif __switch__ == "Smooth Trend":
        __block_result_6__ = 64
    else:
        __block_result_6__ = volLenIn
    volLen: int = __block_result_6__

    __block_result_7__ = na
    __switch__ = presetMode
    if __switch__ == "Fast Response":
        __block_result_7__ = 0.15
    elif __switch__ == "Smooth Trend":
        __block_result_7__ = 0.4
    else:
        __block_result_7__ = blendWeightIn
    blendWeight: float = __block_result_7__

    __block_result_8__ = na
    __switch__ = presetMode
    if __switch__ == "Fast Response":
        __block_result_8__ = 250
    elif __switch__ == "Smooth Trend":
        __block_result_8__ = 750
    else:
        __block_result_8__ = blendLenIn
    blendLen: int = __block_result_8__

    __block_result_9__ = na
    __switch__ = presetMode
    if __switch__ == "Fast Response":
        __block_result_9__ = 150
    elif __switch__ == "Smooth Trend":
        __block_result_9__ = 400
    else:
        __block_result_9__ = scalingLenIn
    scalingLen: int = __block_result_9__

    __block_result_10__ = na
    __switch__ = presetMode
    if __switch__ == "Fast Response":
        __block_result_10__ = 2.5
    elif __switch__ == "Smooth Trend":
        __block_result_10__ = 6.0
    else:
        __block_result_10__ = entryThIn
    entryTh: float = __block_result_10__

    __block_result_11__ = na
    __switch__ = presetMode
    if __switch__ == "Fast Response":
        __block_result_11__ = 0.7
    elif __switch__ == "Smooth Trend":
        __block_result_11__ = 0.35
    else:
        __block_result_11__ = exitFracIn
    exitFrac: float = __block_result_11__

    srcSafe: Series[float] = math.max(srcInput, 1e-10)
    ret: float = math.log(srcSafe / math.max(nz(srcSafe[1], srcSafe), 1e-10))

    volShort: float = ta.stdev(ret, volLen)
    volLong: float = ta.sma(volShort, blendLen)
    volPct: float = volShort * (1.0 - blendWeight) + volLong * blendWeight if not na(volLong) else volShort
    volPct = math.max(volPct, 1e-10)

    volPrice: float = volPct * srcSafe

    def ewmacRule(src: float, fastLen: int, riskUnit: float, scaleLen: int, adaptive: bool, cap: float):
        fastMa: float = ta.ema(src, fastLen)
        slowMa: float = ta.ema(src, fastLen * 4)
        raw: float = (fastMa - slowMa) / math.max(riskUnit, 1e-10)
        avgAbs: float = ta.sma(math.abs(raw), scaleLen)
        fixedScale: float = 15.0 / math.sqrt(fastLen)
        scaleFactor: float = 10.0 / math.max(avgAbs, 1e-10) if adaptive and (not na(avgAbs)) else fixedScale
        score: float = math.max(math.min(raw * scaleFactor, cap), -cap)
        midpoint: float = (fastMa + slowMa) / 2.0
        return (score, midpoint)

    adaptiveScaling: bool = scalingMode == 'Adaptive'

    score1, mid1 = ewmacRule(srcSafe, r1Len, volPrice, scalingLen, adaptiveScaling, scoreCap)
    score2, mid2 = ewmacRule(srcSafe, r2Len, volPrice, scalingLen, adaptiveScaling, scoreCap)
    score3, mid3 = ewmacRule(srcSafe, r3Len, volPrice, scalingLen, adaptiveScaling, scoreCap)
    score4, mid4 = ewmacRule(srcSafe, r4Len, volPrice, scalingLen, adaptiveScaling, scoreCap)
    score5, mid5 = ewmacRule(srcSafe, r5Len, volPrice, scalingLen, adaptiveScaling, scoreCap)
    score6, mid6 = ewmacRule(srcSafe, r6Len, volPrice, scalingLen, adaptiveScaling, scoreCap)

    weightSum: float = 0.0
    scoreSum: float = 0.0
    lineSum: float = 0.0
    activeCount: int = 0

    if p1 and r1W > 0.0:
        weightSum += r1W
        scoreSum += score1 * r1W
        lineSum += mid1 * r1W
        activeCount += 1
    if p2 and r2W > 0.0:
        weightSum += r2W
        scoreSum += score2 * r2W
        lineSum += mid2 * r2W
        activeCount += 1
    if p3 and r3W > 0.0:
        weightSum += r3W
        scoreSum += score3 * r3W
        lineSum += mid3 * r3W
        activeCount += 1
    if p4 and r4W > 0.0:
        weightSum += r4W
        scoreSum += score4 * r4W
        lineSum += mid4 * r4W
        activeCount += 1
    if p5 and r5W > 0.0:
        weightSum += r5W
        scoreSum += score5 * r5W
        lineSum += mid5 * r5W
        activeCount += 1
    if p6 and r6W > 0.0:
        weightSum += r6W
        scoreSum += score6 * r6W
        lineSum += mid6 * r6W
        activeCount += 1

    __block_result_12__ = na
    __switch__ = activeCount
    if __switch__ == 0:
        __block_result_12__ = 1.0
    elif __switch__ == 1:
        __block_result_12__ = 1.0
    elif __switch__ == 2:
        __block_result_12__ = 1.1
    elif __switch__ == 3:
        __block_result_12__ = 1.2
    elif __switch__ == 4:
        __block_result_12__ = 1.27
    elif __switch__ == 5:
        __block_result_12__ = 1.32
    else:
        __block_result_12__ = 1.36
    multiplierTable: float = __block_result_12__

    divMultiplier: float = multiplierIn if multiplierIn > 0.0 else multiplierTable
    trendScoreRaw: float = scoreSum / weightSum * divMultiplier if weightSum > 0.0 else 0.0
    trendScore: float = math.max(math.min(trendScoreRaw, scoreCap), -scoreCap)
    trendLine: Series[float] = lineSum / weightSum if weightSum > 0.0 else srcSafe

    exitTh: float = entryTh * exitFrac

    signalState: PersistentSeries[int] = 0

    if barstate.isconfirmed:
        if trendScore > entryTh and signalState != 1:
            signalState = 1
        elif trendScore < -entryTh and signalState != -1:
            signalState = -1
        elif useNeutral and signalState == 1 and (trendScore < exitTh):
            signalState = 0
        elif useNeutral and signalState == -1 and (trendScore > -exitTh):
            signalState = 0

    turnedBull: bool = signalState == 1 and signalState[1] != 1
    turnedBear: bool = signalState == -1 and signalState[1] != -1
    turnedNeut: bool = signalState == 0 and signalState[1] != 0
    signalChanged: bool = turnedBull or turnedBear or turnedNeut

    __block_result_13__ = (na, na, na)
    __switch__ = colorPreset
    if __switch__ == "Classic":
        __block_result_13__ = (color.new('#00FF00'), color.new('#FF0000'), color.new('#808080'))
    elif __switch__ == "Aqua":
        __block_result_13__ = (color.new('#00D4FF'), color.new('#FF8C00'), color.new('#808080'))
    elif __switch__ == "Cosmic":
        __block_result_13__ = (color.new('#49FFCE'), color.new('#9932CC'), color.new('#808080'))
    elif __switch__ == "Cyber":
        __block_result_13__ = (color.new('#00CCCC'), color.new('#FF6600'), color.new('#808080'))
    elif __switch__ == "Neon":
        __block_result_13__ = (color.new('#FFFF00'), color.new('#FF00FF'), color.new('#808080'))
    else:
        __block_result_13__ = (bullCustom, bearCustom, neutCustom)
    bullCol, bearCol, neutCol = __block_result_13__

    signalColor: Color = bullCol if signalState == 1 else bearCol if signalState == -1 else neutCol

    displayLine: float = trendLine if barstate.isconfirmed else trendLine[1]

    plot(displayLine if showGlow else na, 'Trend Line Glow Outer', color.new(signalColor, 88), 20)
    plot(displayLine if showGlow else na, 'Trend Line Glow Inner', color.new(signalColor, 75), 10)
    plot(displayLine, 'Trend Line', color.new(signalColor, 0), lineWidth)

    barcolor(color.new(signalColor, barTrans) if colorBars else na, title='Trend Bar Color')
    bgcolor(color.new(signalColor, bgTrans) if colorBg else na, title='Trend Background Color')

    __block_result_14__ = na
    __switch__ = readoutSize
    if __switch__ == "Tiny":
        __block_result_14__ = size.tiny
    elif __switch__ == "Small":
        __block_result_14__ = size.small
    elif __switch__ == "Large":
        __block_result_14__ = size.large
    else:
        __block_result_14__ = size.normal
    readoutTextSize: str = __block_result_14__

    def readoutTextColor(fillColor: Color):
        brightness: float = (color.r(fillColor) * 299.0 + color.g(fillColor) * 587.0 + color.b(fillColor) * 114.0) / 1000.0
        return color.black if brightness >= 128.0 else color.white

    signalReadout: Persistent[Label] = na(Label)

    if showReadout and barstate.islast:
        label.delete(signalReadout)
        readoutText: str = '  Bullish  ' if signalState == 1 else '  Bearish  ' if signalState == -1 else '  Neutral  '
        readoutFill: Color = color.new(signalColor, 0)
        signalReadout = label.new(bar_index, displayLine, readoutText, xloc=xloc.bar_index, style=label.style_label_left, color=readoutFill, textcolor=readoutTextColor(readoutFill), size=readoutTextSize)

    alertcondition(turnedBull, title='Bullish Trend Signal', message='EWMAC Trend Signals: BULLISH trend confirmed on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(turnedBear, title='Bearish Trend Signal', message='EWMAC Trend Signals: BEARISH trend confirmed on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(turnedNeut, title='Neutral Trend Signal', message='EWMAC Trend Signals: Trend released to NEUTRAL on {{exchange}}:{{ticker}} - {{interval}}')
    alertcondition(signalChanged, title='Trend Signal Changed', message='EWMAC Trend Signals: Trend signal changed on {{exchange}}:{{ticker}} - {{interval}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)