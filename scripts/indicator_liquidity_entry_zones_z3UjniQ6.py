"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, barstate, box, close, color,
    display, extend, high, hour, input, label, line, location, low, math, na, nz, open, plotshape,
    position, script, shape, size, string, syminfo, ta, table, time, xloc
)
from pynecore.types import Box, Color, Label, Line, Persistent, Table

groupTrend: str = "📈 Trend Filter"
groupSweep: str = "💧 Liquidity Sweep Detection"
groupQuality: str = "🧪 Candle Quality Filters"
groupConfirm: str = "✅ Entry Confirmation"
groupSim: str = "⚖️ ATR Risk Projection"
groupVisual: str = "🎨 Visual Settings"


@script.indicator("Liquidity Entry Zones [trade_w_samet]", shorttitle="Liquidity Entry Zones [trade_w_samet]", overlay=True, max_labels_count=500, max_lines_count=500, max_boxes_count=500)
def main(
    localEmaLength=input.int(50, "📏 EMA Length", minval=1, group=groupTrend, tooltip="Defines the local EMA used for the optional trend filter. Higher values create a smoother directional filter.", display=display.none),
    useLocalEmaFilter=input.bool(True, "🧭 Use EMA Trend Filter", group=groupTrend, tooltip="When enabled, long signals require price above the EMA and short signals require price below the EMA.", display=display.none),
    pivotLength=input.int(5, "🧱 Swing Pivot Length", minval=1, group=groupSweep, tooltip="Controls how swing highs and swing lows are detected for liquidity reference levels.", display=display.none),
    storedLevels=input.int(20, "📚 Stored Liquidity Levels", minval=5, maxval=100, group=groupSweep, tooltip="Maximum number of recent liquidity levels stored from swing highs and swing lows.", display=display.none),
    minSweepDistanceAtr=input.float(0.1, "📏 Minimum Sweep Distance / ATR", minval=0.01, step=0.01, group=groupSweep, tooltip="Minimum sweep distance measured as an ATR multiplier. Example: 0.10 means the sweep must exceed the level by at least 10% of ATR.", display=display.none),
    reclaimRule=input.string("Close Back Inside", "🔁 Reclaim Rule", options=("Close Back Inside", "Strong Reclaim"), group=groupSweep, tooltip="Close Back Inside requires price to close back beyond the swept liquidity level. Strong Reclaim also requires a stronger close beyond the candle midpoint.", display=display.none),
    minWickPercent=input.float(0.35, "🕯️ Minimum Sweep Wick %", minval=0.0, maxval=1.0, step=0.01, group=groupQuality, tooltip="Minimum wick percentage required on the sweep candle. Higher values require stronger rejection wicks.", display=display.none),
    maxBodyPercent=input.float(0.65, "📦 Maximum Body %", minval=0.05, maxval=1.0, step=0.01, group=groupQuality, tooltip="Maximum allowed candle body percentage. Lower values favor wick-heavy rejection candles.", display=display.none),
    minCandleRangeAtr=input.float(0.2, "📐 Minimum Candle Range / ATR", minval=0.01, step=0.01, group=groupQuality, tooltip="Minimum candle range measured as an ATR multiplier. Helps filter out very small sweep candles.", display=display.none),
    requireBullishBody=input.bool(True, "🟢 Long Confirmation Must Be Bullish", group=groupQuality, tooltip="When enabled, long confirmations require the confirmation candle to close above its open.", display=display.none),
    requireBearishBody=input.bool(True, "🔴 Short Confirmation Must Be Bearish", group=groupQuality, tooltip="When enabled, short confirmations require the confirmation candle to close below its open.", display=display.none),
    confirmationWindow=input.int(2, "⏱️ Max Bars After Sweep For Confirmation", minval=0, maxval=10, group=groupConfirm, tooltip="Maximum number of bars allowed after a valid sweep for confirmation to appear.", display=display.none),
    requireMidlineBreak=input.bool(True, "➗ Require Sweep Candle Midline Break", group=groupConfirm, tooltip="When enabled, confirmation must break the midpoint of the sweep candle in the signal direction.", display=display.none),
    signalCooldownBars=input.int(10, "🧊 Cooldown Bars Between Signals", minval=0, group=groupConfirm, tooltip="Minimum number of bars required between two confirmed signals.", display=display.none),
    enableSimulation=input.bool(True, "🧪 Enable Internal Trade Simulation", group=groupSim, tooltip="When enabled, the script projects ATR-based stop loss and RR-based take profit levels after each signal.", display=display.none),
    atrLength=input.int(14, "📐 ATR Length", minval=1, group=groupSim, tooltip="ATR period used to calculate the stop loss distance.", display=display.none),
    stopLossAtrMultiplier=input.float(1.5, "🛑 Stop Loss ATR Multiplier", minval=0.1, step=0.1, group=groupSim, tooltip="Stop Loss distance is calculated as ATR multiplied by this value.", display=display.none),
    takeProfitRRInput=input.string("3 RR", "🎯 Take Profit RR", options=("1.5 RR", "2 RR", "3 RR", "4 RR", "5 RR", "6 RR"), group=groupSim, tooltip="Take Profit is calculated from the ATR-based stop distance using the selected RR multiple.", display=display.none),
    blockSignalsInTrade=input.bool(True, "🚧 Block New Signals While Trade Is Active", group=groupSim, tooltip="When enabled, new signals are blocked while an internal projected trade is still active.", display=display.none),
    showStoppedTrades=input.bool(False, "👁️ Show Stopped Trades", group=groupSim, tooltip="When disabled, stopped-out trade projection objects are removed from the chart for a cleaner view.", display=display.none),
    showSignalLabels=input.bool(True, "🏷️ Show Signal Labels", group=groupVisual, tooltip="Shows BUY and SELL labels on confirmed signals.", display=display.none),
    showEntryLine=input.bool(True, "⚪ Show Entry Line", group=groupVisual, tooltip="Shows the projected entry line after a confirmed signal.", display=display.none),
    showStatusPanel=input.bool(True, "📊 Show Status Panel", group=groupVisual, tooltip="Shows the live status dashboard. Performance rows such as trades, win rate, net result, and drawdown are not displayed.", display=display.none),
    showSignalBarColors=input.bool(True, "🎨 Color Signal Bars", group=groupVisual, tooltip="Colors confirmed signal bars green for long and red for short.", display=display.none),
    showSweepGuides=input.bool(True, "🧲 Show Sweep Guides", group=groupVisual, tooltip="Shows dotted sweep trace guides when valid liquidity sweeps are detected.", display=display.none),
    guideExtendBars=input.int(20, "➡️ Guide Extension Bars", minval=5, maxval=100, group=groupVisual, tooltip="Controls how far sweep guide lines extend into the future.", display=display.none),
    signalLabelSize=input.string("Normal", "🔠 Signal Label Size", options=("Tiny", "Small", "Normal", "Large"), group=groupVisual, tooltip="Controls the size of BUY, SELL, TP HIT, and SL HIT labels.", display=display.none),
    panelPosition=input.string("Bottom Right", "📍 Panel Position", options=("Top Right", "Top Left", "Bottom Right", "Bottom Left"), group=groupVisual, tooltip="Controls where the status panel appears on the chart.", display=display.none)
):
    CLR_BG: Color = color.rgb(7, 10, 16)
    CLR_PANEL: Color = color.rgb(13, 18, 27)
    CLR_PANEL_ALT: Color = color.rgb(18, 25, 36)
    CLR_BORDER: Color = color.rgb(44, 57, 76)
    CLR_TEXT: Color = color.rgb(245, 247, 250)
    CLR_MUTED: Color = color.rgb(148, 163, 184)

    CLR_CYAN: Color = color.rgb(34, 211, 238)
    CLR_CYAN_SOFT: Color = color.rgb(8, 145, 178)
    CLR_GREEN: Color = color.rgb(16, 185, 129)
    CLR_GREEN_SOFT: Color = color.rgb(5, 150, 105)
    CLR_RED: Color = color.rgb(239, 68, 68)
    CLR_RED_SOFT: Color = color.rgb(220, 38, 38)
    CLR_SILVER: Color = color.rgb(203, 213, 225)
    CLR_GOLD: Color = color.rgb(250, 204, 21)
    CLR_TRACE_BULL: Color = color.rgb(74, 222, 128)
    CLR_TRACE_BEAR: Color = color.rgb(248, 113, 113)

    BOX_TRANSPARENCY: int = 86

    def f_table_position(_pos):
        return position.top_left if _pos == 'Top Left' else position.bottom_right if _pos == 'Bottom Right' else position.bottom_left if _pos == 'Bottom Left' else position.top_right

    def f_fmt(_value):
        return string.tostring(_value, '#.##')

    def f_label_size(_size):
        return size.tiny if _size == 'Tiny' else size.small if _size == 'Small' else size.large if _size == 'Large' else size.normal

    def f_tp_rr(_value):
        return 1.5 if _value == '1.5 RR' else 2.0 if _value == '2 RR' else 3.0 if _value == '3 RR' else 4.0 if _value == '4 RR' else 5.0 if _value == '5 RR' else 6.0

    def f_clamp(_value, _min, _max):
        return math.max(_min, math.min(_max, _value))

    def f_score_color(_score):
        return CLR_GREEN if _score >= 75 else CLR_CYAN if _score >= 55 else CLR_RED

    def f_push_line_prune(_arr, _line, _max):
        array.push(_arr, _line)
        __block_result__ = na
        if array.size(_arr) > _max:
            _old: Line = array.shift(_arr)
            __block_result__ = line.delete(_old)
        return __block_result__

    def f_push_label_prune(_arr, _label, _max):
        array.push(_arr, _label)
        __block_result_1__ = na
        if array.size(_arr) > _max:
            _old: Label = array.shift(_arr)
            __block_result_1__ = label.delete(_old)
        return __block_result_1__

    def f_push_box_prune(_arr, _box, _max):
        array.push(_arr, _box)
        __block_result_2__ = na
        if array.size(_arr) > _max:
            _old: Box = array.shift(_arr)
            __block_result_2__ = box.delete(_old)
        return __block_result_2__

    def f_panel_clear(_t):
        __block_result_3__ = na
        for col in pine_range(0, 1):
            __block_result_4__ = na
            for row in pine_range(0, 9):
                __block_result_4__ = table.cell(_t, col, row, '', bgcolor=CLR_BG, text_color=CLR_BG)
            __block_result_3__ = __block_result_4__
        return __block_result_3__

    def f_quality_score(_wickPct, _bodyPct, _rangeAtr, _minWick, _maxBody, _minRangeAtr, _emaOk, _reclaimOk, _midBreakOk):
        wickScore: float = f_clamp(_wickPct / _minWick * 32.0, 0.0, 32.0) if _minWick > 0 else 32.0
        bodyScore: float = f_clamp((_maxBody - _bodyPct) / _maxBody * 24.0, 0.0, 24.0) if _maxBody > 0 else 24.0
        rangeScore: float = f_clamp(_rangeAtr / _minRangeAtr * 18.0, 0.0, 18.0) if _minRangeAtr > 0 else 18.0
        emaScore: float = 10.0 if _emaOk else 0.0
        reclaimScore: float = 10.0 if _reclaimOk else 0.0
        midScore: float = 6.0 if _midBreakOk else 0.0
        return f_clamp(wickScore + bodyScore + rangeScore + emaScore + reclaimScore + midScore, 0.0, 100.0)

    def f_draw_signal_brackets(_bar, _high, _low, _buffer, _color, _arr):
        leftX: int = _bar - 1
        midX: int = _bar
        rightX: int = _bar + 1
        topY: float = _high + _buffer
        botY: float = _low - _buffer
        topIn: float = _high + _buffer * 0.35
        botIn: float = _low - _buffer * 0.35

        l1: Line = line.new(x1=leftX, y1=topY, x2=midX, y2=topY, xloc=xloc.bar_index, color=_color, width=1)
        l2: Line = line.new(x1=leftX, y1=topY, x2=leftX, y2=topIn, xloc=xloc.bar_index, color=_color, width=1)
        l3: Line = line.new(x1=leftX, y1=botY, x2=midX, y2=botY, xloc=xloc.bar_index, color=_color, width=1)
        l4: Line = line.new(x1=leftX, y1=botY, x2=leftX, y2=botIn, xloc=xloc.bar_index, color=_color, width=1)

        l5: Line = line.new(x1=midX, y1=topY, x2=rightX, y2=topY, xloc=xloc.bar_index, color=_color, width=1)
        l6: Line = line.new(x1=rightX, y1=topY, x2=rightX, y2=topIn, xloc=xloc.bar_index, color=_color, width=1)
        l7: Line = line.new(x1=midX, y1=botY, x2=rightX, y2=botY, xloc=xloc.bar_index, color=_color, width=1)
        l8: Line = line.new(x1=rightX, y1=botY, x2=rightX, y2=botIn, xloc=xloc.bar_index, color=_color, width=1)

        f_push_line_prune(_arr, l1, 160)
        f_push_line_prune(_arr, l2, 160)
        f_push_line_prune(_arr, l3, 160)
        f_push_line_prune(_arr, l4, 160)
        f_push_line_prune(_arr, l5, 160)
        f_push_line_prune(_arr, l6, 160)
        f_push_line_prune(_arr, l7, 160)
        return f_push_line_prune(_arr, l8, 160)

    def f_add_sweep_trace(_price, _bull, _extendBars, _lineArr, _ghostArr, _labelArr):
        traceColor: Color = color.new(CLR_TRACE_BULL, 0) if _bull else color.new(CLR_TRACE_BEAR, 0)
        ghostColor: Color = color.new(CLR_TRACE_BULL, 82) if _bull else color.new(CLR_TRACE_BEAR, 82)

        traceLine: Line = line.new(x1=bar_index, y1=_price, x2=bar_index + _extendBars, y2=_price, xloc=xloc.bar_index, extend=extend.none, color=traceColor, width=1, style=line.style_dotted)
        ghostLine: Line = line.new(x1=bar_index, y1=_price, x2=bar_index + _extendBars * 2, y2=_price, xloc=xloc.bar_index, extend=extend.none, color=ghostColor, width=1, style=line.style_solid)
        traceLab: Label = label.new(bar_index + _extendBars, _price, 'SWEEP TRACE', xloc=xloc.bar_index, style=label.style_label_up if _bull else label.style_label_down, color=CLR_GREEN_SOFT if _bull else CLR_RED_SOFT, textcolor=CLR_TEXT, size=size.tiny)

        f_push_line_prune(_lineArr, traceLine, 80)
        f_push_line_prune(_ghostArr, ghostLine, 20)
        return f_push_label_prune(_labelArr, traceLab, 40)

    def f_session_name(_hour):
        return 'ASIA' if _hour >= 0 and _hour < 8 else 'LONDON' if _hour >= 8 and _hour < 16 else 'NEW YORK' if _hour >= 16 and _hour < 24 else 'UNKNOWN'

    localEma = ta.ema(close, localEmaLength)
    atrValue = ta.atr(atrLength)
    takeProfitRR = f_tp_rr(takeProfitRRInput)

    candleRange = high - low
    candleBody = math.abs(close - open)
    upperWick = high - math.max(open, close)
    lowerWick = math.min(open, close) - low

    bodyPercent = candleBody / candleRange if candleRange > 0 else 0.0
    upperWickPercent = upperWick / candleRange if candleRange > 0 else 0.0
    lowerWickPercent = lowerWick / candleRange if candleRange > 0 else 0.0

    candleRangeAtr = candleRange / atrValue if not na(atrValue) and atrValue > 0 else 0.0
    minSweepDistancePx = minSweepDistanceAtr * atrValue if not na(atrValue) else na
    minRangeDistancePx = minCandleRangeAtr * atrValue if not na(atrValue) else na

    stopLossDistance = atrValue * stopLossAtrMultiplier if not na(atrValue) else na
    takeProfitDistance = stopLossDistance * takeProfitRR if not na(stopLossDistance) else na
    riskModelReady = not na(stopLossDistance) and stopLossDistance > 0 and (not na(takeProfitDistance)) and (takeProfitDistance > 0)

    visualBuffer: float = math.max(syminfo.mintick * 8.0, candleRange * 0.08)
    entryZoneHalf: float = math.max(syminfo.mintick * 6.0, nz(atrValue, candleRange) * 0.04)
    entryLineOffset: float = math.max(syminfo.mintick * 2.0, nz(atrValue, candleRange) * 0.02)

    atrPct: float = atrValue / close * 100.0 if not na(atrValue) and close != 0 else 0.0
    volatilityState: str = 'HIGH' if atrPct >= 0.8 else 'NORMAL' if atrPct >= 0.35 else 'LOW'
    volatilityColor: Color = CLR_RED if atrPct >= 0.8 else CLR_CYAN if atrPct >= 0.35 else CLR_GREEN

    gmt3Hour: int = hour(time, 'GMT+3')
    sessionState: str = f_session_name(gmt3Hour)
    sessionColor: Color = CLR_CYAN if sessionState == 'LONDON' else CLR_GOLD if sessionState == 'NEW YORK' else CLR_SILVER

    pivotHigh = ta.pivothigh(high, pivotLength, pivotLength)
    pivotLow = ta.pivotlow(low, pivotLength, pivotLength)

    storedHighLevels: Persistent[list[float]] = array.new_float()
    storedHighBars: Persistent[list[int]] = array.new_int()
    storedLowLevels: Persistent[list[float]] = array.new_float()
    storedLowBars: Persistent[list[int]] = array.new_int()

    if not na(pivotHigh):
        array.push(storedHighLevels, pivotHigh)
        array.push(storedHighBars, bar_index - pivotLength)
        if array.size(storedHighLevels) > storedLevels:
            array.shift(storedHighLevels)
            array.shift(storedHighBars)

    if not na(pivotLow):
        array.push(storedLowLevels, pivotLow)
        array.push(storedLowBars, bar_index - pivotLength)
        if array.size(storedLowLevels) > storedLevels:
            array.shift(storedLowLevels)
            array.shift(storedLowBars)

    sweptHighLevel: float = na(float)
    sweptHighBar: int = na(int)
    sweptLowLevel: float = na(float)
    sweptLowBar: int = na(int)

    highLevelCount: int = array.size(storedHighLevels)
    if highLevelCount > 0:
        for i in pine_range(highLevelCount - 1, 0):
            highLevel: float = array.get(storedHighLevels, i)
            highBar: int = array.get(storedHighBars, i)
            if highBar < bar_index and high > highLevel and (not na(minSweepDistancePx)) and (high - highLevel >= minSweepDistancePx):
                sweptHighLevel = highLevel
                sweptHighBar = highBar
                break

    lowLevelCount: int = array.size(storedLowLevels)
    if lowLevelCount > 0:
        for i in pine_range(lowLevelCount - 1, 0):
            lowLevel: float = array.get(storedLowLevels, i)
            lowBar: int = array.get(storedLowBars, i)
            if lowBar < bar_index and low < lowLevel and (not na(minSweepDistancePx)) and (lowLevel - low >= minSweepDistancePx):
                sweptLowLevel = lowLevel
                sweptLowBar = lowBar
                break

    bearishReclaim = not na(sweptHighLevel) and (close < sweptHighLevel if reclaimRule == 'Close Back Inside' else close < sweptHighLevel and close < (high + low) / 2.0)

    bullishReclaim = not na(sweptLowLevel) and (close > sweptLowLevel if reclaimRule == 'Close Back Inside' else close > sweptLowLevel and close > (high + low) / 2.0)

    validSellSweep = not na(sweptHighLevel) and bearishReclaim and (upperWickPercent >= minWickPercent) and (bodyPercent <= maxBodyPercent) and (not na(minRangeDistancePx)) and (candleRange >= minRangeDistancePx)

    validBuySweep = not na(sweptLowLevel) and bullishReclaim and (lowerWickPercent >= minWickPercent) and (bodyPercent <= maxBodyPercent) and (not na(minRangeDistancePx)) and (candleRange >= minRangeDistancePx)

    sweepTraceLines: Persistent[list[Line]] = array.new_line()
    referenceLines: Persistent[list[Line]] = array.new_line()
    sweepTraceLabels: Persistent[list[Label]] = array.new_label()

    if showSweepGuides and validBuySweep and (not na(sweptLowLevel)):
        f_add_sweep_trace(sweptLowLevel, True, guideExtendBars, sweepTraceLines, referenceLines, sweepTraceLabels)

    if showSweepGuides and validSellSweep and (not na(sweptHighLevel)):
        f_add_sweep_trace(sweptHighLevel, False, guideExtendBars, sweepTraceLines, referenceLines, sweepTraceLabels)

    pendingBullSweepBar: Persistent[int] = na(int)
    pendingBullHigh: Persistent[float] = na(float)
    pendingBullLow: Persistent[float] = na(float)
    pendingBullMid: Persistent[float] = na(float)
    pendingBullLevel: Persistent[float] = na(float)
    pendingBullScore: Persistent[float] = na(float)

    pendingBearSweepBar: Persistent[int] = na(int)
    pendingBearHigh: Persistent[float] = na(float)
    pendingBearLow: Persistent[float] = na(float)
    pendingBearMid: Persistent[float] = na(float)
    pendingBearLevel: Persistent[float] = na(float)
    pendingBearScore: Persistent[float] = na(float)

    bullEmaOkForSweep = not useLocalEmaFilter or close > localEma
    bearEmaOkForSweep = not useLocalEmaFilter or close < localEma
    bullMidOkNow = not requireMidlineBreak or close > (high + low) / 2.0
    bearMidOkNow = not requireMidlineBreak or close < (high + low) / 2.0

    bullSweepScoreNow = f_quality_score(lowerWickPercent, bodyPercent, candleRangeAtr, minWickPercent, maxBodyPercent, minCandleRangeAtr, bullEmaOkForSweep, bullishReclaim, bullMidOkNow)
    bearSweepScoreNow = f_quality_score(upperWickPercent, bodyPercent, candleRangeAtr, minWickPercent, maxBodyPercent, minCandleRangeAtr, bearEmaOkForSweep, bearishReclaim, bearMidOkNow)

    if validBuySweep:
        pendingBullSweepBar = bar_index
        pendingBullHigh = high
        pendingBullLow = low
        pendingBullMid = (high + low) / 2.0
        pendingBullLevel = sweptLowLevel
        pendingBullScore = bullSweepScoreNow

    if validSellSweep:
        pendingBearSweepBar = bar_index
        pendingBearHigh = high
        pendingBearLow = low
        pendingBearMid = (high + low) / 2.0
        pendingBearLevel = sweptHighLevel
        pendingBearScore = bearSweepScoreNow

    bullWindowOpen = not na(pendingBullSweepBar) and bar_index - pendingBullSweepBar <= confirmationWindow
    bearWindowOpen = not na(pendingBearSweepBar) and bar_index - pendingBearSweepBar <= confirmationWindow

    localLongOk = not useLocalEmaFilter or close > localEma
    localShortOk = not useLocalEmaFilter or close < localEma
    bullBodyOk = not requireBullishBody or close > open
    bearBodyOk = not requireBearishBody or close < open
    bullMidOk = not requireMidlineBreak or close > pendingBullMid
    bearMidOk = not requireMidlineBreak or close < pendingBearMid

    buyConfirmed = bullWindowOpen and bullBodyOk and localLongOk and bullMidOk

    sellConfirmed = bearWindowOpen and bearBodyOk and localShortOk and bearMidOk

    lastSignalBar: Persistent[int] = na(int)
    cooldownPassed = na(lastSignalBar) or bar_index - lastSignalBar > signalCooldownBars

    rawBuySignal = buyConfirmed
    rawSellSignal = sellConfirmed

    buySignal = rawBuySignal and cooldownPassed
    sellSignal = rawSellSignal and cooldownPassed and (not buySignal)

    lastSignalScore: Persistent[float] = na(float)
    lastSignalDir: Persistent[int] = 0

    if buySignal:
        lastSignalScore = nz(pendingBullScore, bullSweepScoreNow)
        lastSignalDir = 1

    if sellSignal:
        lastSignalScore = nz(pendingBearScore, bearSweepScoreNow)
        lastSignalDir = -1

    if buySignal or sellSignal:
        lastSignalBar = bar_index

    if buySignal or (not na(pendingBullSweepBar) and bar_index - pendingBullSweepBar > confirmationWindow):
        pendingBullSweepBar = na
        pendingBullHigh = na
        pendingBullLow = na
        pendingBullMid = na
        pendingBullLevel = na
        pendingBullScore = na

    if sellSignal or (not na(pendingBearSweepBar) and bar_index - pendingBearSweepBar > confirmationWindow):
        pendingBearSweepBar = na
        pendingBearHigh = na
        pendingBearLow = na
        pendingBearMid = na
        pendingBearLevel = na
        pendingBearScore = na

    positionDirection: Persistent[int] = 0
    simulatedEntry: Persistent[float] = na(float)
    simulatedTP: Persistent[float] = na(float)
    simulatedSL: Persistent[float] = na(float)
    simulatedEntryOffset: Persistent[float] = na(float)
    simulatedEntryBar: Persistent[int] = na(int)

    tradeIsActive = positionDirection != 0

    allowLongSignal = riskModelReady and (not tradeIsActive if blockSignalsInTrade else True) if enableSimulation else True
    allowShortSignal = riskModelReady and (not tradeIsActive if blockSignalsInTrade else True) if enableSimulation else True

    plotLongSignal = buySignal and allowLongSignal
    plotShortSignal = sellSignal and allowShortSignal

    bracketLines: Persistent[list[Line]] = array.new_line()
    scoreLabels: Persistent[list[Label]] = array.new_label()
    signalBoxes: Persistent[list[Box]] = array.new_box()
    pathLines: Persistent[list[Line]] = array.new_line()

    activeTpBox: Persistent[Box] = na(Box)
    activeSlBox: Persistent[Box] = na(Box)
    activeEntryZone: Persistent[Box] = na(Box)
    activeEntryLine1: Persistent[Line] = na(Line)
    activeEntryLine2: Persistent[Line] = na(Line)
    activeInvalidationLine: Persistent[Line] = na(Line)
    activeProjectionLine: Persistent[Line] = na(Line)
    activeEntryTag: Persistent[Label] = na(Label)
    activeTpTag: Persistent[Label] = na(Label)
    activeSlTag: Persistent[Label] = na(Label)
    activeInvalidationTag: Persistent[Label] = na(Label)

    if plotLongSignal:
        f_draw_signal_brackets(bar_index, high, low, visualBuffer, CLR_CYAN, bracketLines)

        sigTop: float = math.max(open, close)
        sigBot: float = math.min(open, close)
        signalBodyBox: Box = box.new(left=bar_index, top=sigTop, right=bar_index + 1, bottom=sigBot, xloc=xloc.bar_index, border_color=color.new(CLR_CYAN, 0), bgcolor=color.new(CLR_GREEN, 82), border_width=1)
        f_push_box_prune(signalBoxes, signalBodyBox, 50)

        scoreTag: Label = label.new(bar_index, low - visualBuffer * 1.2, 'Q:' + string.tostring(math.round(nz(lastSignalScore, 0))), xloc=xloc.bar_index, style=label.style_label_up, color=CLR_CYAN_SOFT, textcolor=CLR_TEXT, size=size.tiny)
        f_push_label_prune(scoreLabels, scoreTag, 50)

    if plotShortSignal:
        f_draw_signal_brackets(bar_index, high, low, visualBuffer, CLR_CYAN, bracketLines)

        sigTop: float = math.max(open, close)
        sigBot: float = math.min(open, close)
        signalBodyBox: Box = box.new(left=bar_index, top=sigTop, right=bar_index + 1, bottom=sigBot, xloc=xloc.bar_index, border_color=color.new(CLR_CYAN, 0), bgcolor=color.new(CLR_RED, 82), border_width=1)
        f_push_box_prune(signalBoxes, signalBodyBox, 50)

        scoreTag: Label = label.new(bar_index, high + visualBuffer * 1.2, 'Q:' + string.tostring(math.round(nz(lastSignalScore, 0))), xloc=xloc.bar_index, style=label.style_label_down, color=CLR_CYAN_SOFT, textcolor=CLR_TEXT, size=size.tiny)
        f_push_label_prune(scoreLabels, scoreTag, 50)

    if enableSimulation and plotLongSignal:
        positionDirection = 1
        simulatedEntry = close
        simulatedSL = simulatedEntry - stopLossDistance
        simulatedTP = simulatedEntry + takeProfitDistance
        simulatedEntryOffset = entryLineOffset
        simulatedEntryBar = bar_index

        activeTpBox = box.new(left=bar_index, top=simulatedTP, right=bar_index, bottom=simulatedEntry, xloc=xloc.bar_index, border_color=color.new(CLR_CYAN, 0), bgcolor=color.new(CLR_CYAN, BOX_TRANSPARENCY), border_width=1)
        activeSlBox = box.new(left=bar_index, top=simulatedEntry, right=bar_index, bottom=simulatedSL, xloc=xloc.bar_index, border_color=color.new(CLR_RED, 0), bgcolor=color.new(CLR_RED, BOX_TRANSPARENCY), border_width=1)
        activeEntryZone = box.new(left=bar_index, top=simulatedEntry + entryZoneHalf, right=bar_index, bottom=simulatedEntry - entryZoneHalf, xloc=xloc.bar_index, border_color=color.new(CLR_CYAN, 40), bgcolor=color.new(CLR_CYAN, 92), border_width=1)

        if showEntryLine:
            activeEntryLine1 = line.new(x1=bar_index, y1=simulatedEntry, x2=bar_index, y2=simulatedEntry, xloc=xloc.bar_index, extend=extend.none, color=color.new(CLR_CYAN, 0), width=1, style=line.style_solid)
            activeEntryLine2 = line.new(x1=bar_index, y1=simulatedEntry + simulatedEntryOffset, x2=bar_index, y2=simulatedEntry + simulatedEntryOffset, xloc=xloc.bar_index, extend=extend.none, color=color.new(CLR_CYAN, 70), width=1, style=line.style_dotted)

        activeInvalidationLine = line.new(x1=bar_index, y1=simulatedSL, x2=bar_index, y2=simulatedSL, xloc=xloc.bar_index, extend=extend.none, color=color.new(CLR_RED, 0), width=1, style=line.style_dashed)
        activeProjectionLine = line.new(x1=bar_index, y1=simulatedEntry, x2=bar_index + 6, y2=simulatedEntry + (simulatedTP - simulatedEntry) * 0.22, xloc=xloc.bar_index, extend=extend.none, color=color.new(CLR_GREEN, 15), width=1, style=line.style_dotted)
        f_push_line_prune(pathLines, activeProjectionLine, 60)

        activeEntryTag = label.new(bar_index, simulatedEntry, 'ENTRY', xloc=xloc.bar_index, style=label.style_label_left, color=CLR_CYAN_SOFT, textcolor=CLR_TEXT, size=size.tiny)
        activeTpTag = label.new(bar_index, simulatedTP, 'TARGET ' + f_fmt(takeProfitRR) + 'R', xloc=xloc.bar_index, style=label.style_label_left, color=CLR_GREEN_SOFT, textcolor=CLR_TEXT, size=size.tiny)
        activeSlTag = label.new(bar_index, simulatedSL, 'ATR STOP', xloc=xloc.bar_index, style=label.style_label_left, color=CLR_RED_SOFT, textcolor=CLR_TEXT, size=size.tiny)
        activeInvalidationTag = label.new(bar_index, simulatedSL, 'INVALIDATION', xloc=xloc.bar_index, style=label.style_label_left, color=CLR_RED_SOFT, textcolor=CLR_TEXT, size=size.tiny)

    if enableSimulation and plotShortSignal:
        positionDirection = -1
        simulatedEntry = close
        simulatedSL = simulatedEntry + stopLossDistance
        simulatedTP = simulatedEntry - takeProfitDistance
        simulatedEntryOffset = entryLineOffset
        simulatedEntryBar = bar_index

        activeTpBox = box.new(left=bar_index, top=simulatedEntry, right=bar_index, bottom=simulatedTP, xloc=xloc.bar_index, border_color=color.new(CLR_CYAN, 0), bgcolor=color.new(CLR_CYAN, BOX_TRANSPARENCY), border_width=1)
        activeSlBox = box.new(left=bar_index, top=simulatedSL, right=bar_index, bottom=simulatedEntry, xloc=xloc.bar_index, border_color=color.new(CLR_RED, 0), bgcolor=color.new(CLR_RED, BOX_TRANSPARENCY), border_width=1)
        activeEntryZone = box.new(left=bar_index, top=simulatedEntry + entryZoneHalf, right=bar_index, bottom=simulatedEntry - entryZoneHalf, xloc=xloc.bar_index, border_color=color.new(CLR_CYAN, 40), bgcolor=color.new(CLR_CYAN, 92), border_width=1)

        if showEntryLine:
            activeEntryLine1 = line.new(x1=bar_index, y1=simulatedEntry, x2=bar_index, y2=simulatedEntry, xloc=xloc.bar_index, extend=extend.none, color=color.new(CLR_CYAN, 0), width=1, style=line.style_solid)
            activeEntryLine2 = line.new(x1=bar_index, y1=simulatedEntry - simulatedEntryOffset, x2=bar_index, y2=simulatedEntry - simulatedEntryOffset, xloc=xloc.bar_index, extend=extend.none, color=color.new(CLR_CYAN, 70), width=1, style=line.style_dotted)

        activeInvalidationLine = line.new(x1=bar_index, y1=simulatedSL, x2=bar_index, y2=simulatedSL, xloc=xloc.bar_index, extend=extend.none, color=color.new(CLR_RED, 0), width=1, style=line.style_dashed)
        activeProjectionLine = line.new(x1=bar_index, y1=simulatedEntry, x2=bar_index + 6, y2=simulatedEntry - (simulatedEntry - simulatedTP) * 0.22, xloc=xloc.bar_index, extend=extend.none, color=color.new(CLR_RED, 15), width=1, style=line.style_dotted)
        f_push_line_prune(pathLines, activeProjectionLine, 60)

        activeEntryTag = label.new(bar_index, simulatedEntry, 'ENTRY', xloc=xloc.bar_index, style=label.style_label_left, color=CLR_CYAN_SOFT, textcolor=CLR_TEXT, size=size.tiny)
        activeTpTag = label.new(bar_index, simulatedTP, 'TARGET ' + f_fmt(takeProfitRR) + 'R', xloc=xloc.bar_index, style=label.style_label_left, color=CLR_GREEN_SOFT, textcolor=CLR_TEXT, size=size.tiny)
        activeSlTag = label.new(bar_index, simulatedSL, 'ATR STOP', xloc=xloc.bar_index, style=label.style_label_left, color=CLR_RED_SOFT, textcolor=CLR_TEXT, size=size.tiny)
        activeInvalidationTag = label.new(bar_index, simulatedSL, 'INVALIDATION', xloc=xloc.bar_index, style=label.style_label_left, color=CLR_RED_SOFT, textcolor=CLR_TEXT, size=size.tiny)

    if enableSimulation and tradeIsActive:
        if not na(activeTpBox):
            box.set_right(activeTpBox, bar_index)
        if not na(activeSlBox):
            box.set_right(activeSlBox, bar_index)
        if not na(activeEntryZone):
            box.set_right(activeEntryZone, bar_index)

        if not na(activeEntryLine1):
            line.set_x2(activeEntryLine1, bar_index)
            line.set_y2(activeEntryLine1, simulatedEntry)

        if not na(activeEntryLine2):
            activeOffset: float = nz(simulatedEntryOffset, entryLineOffset)
            line.set_x2(activeEntryLine2, bar_index)
            line.set_y2(activeEntryLine2, simulatedEntry + activeOffset if positionDirection == 1 else simulatedEntry - activeOffset)

        if not na(activeInvalidationLine):
            line.set_x2(activeInvalidationLine, bar_index)
            line.set_y2(activeInvalidationLine, simulatedSL)

        if not na(activeEntryTag):
            label.set_x(activeEntryTag, bar_index)
            label.set_y(activeEntryTag, simulatedEntry)

        if not na(activeTpTag):
            label.set_x(activeTpTag, bar_index)
            label.set_y(activeTpTag, simulatedTP)

        if not na(activeSlTag):
            label.set_x(activeSlTag, bar_index)
            label.set_y(activeSlTag, simulatedSL)

        if not na(activeInvalidationTag):
            label.set_x(activeInvalidationTag, bar_index)
            label.set_y(activeInvalidationTag, simulatedSL)

    exitWin: bool = False
    exitLoss: bool = False
    exitDirection: int = positionDirection

    if enableSimulation and tradeIsActive and (bar_index > simulatedEntryBar):
        if positionDirection == 1:
            longSlHit: bool = low <= simulatedSL
            longTpHit: bool = high >= simulatedTP

            if longSlHit and longTpHit:
                exitLoss = True
            elif longSlHit:
                exitLoss = True
            elif longTpHit:
                exitWin = True

        if positionDirection == -1:
            shortSlHit: bool = high >= simulatedSL
            shortTpHit: bool = low <= simulatedTP

            if shortSlHit and shortTpHit:
                exitLoss = True
            elif shortSlHit:
                exitLoss = True
            elif shortTpHit:
                exitWin = True

    if exitWin:
        label.new(bar_index, high if exitDirection == 1 else low, 'TP ' + f_fmt(takeProfitRR) + 'R HIT', xloc=xloc.bar_index, style=label.style_label_down if exitDirection == 1 else label.style_label_up, color=CLR_GREEN, textcolor=CLR_TEXT, size=f_label_size(signalLabelSize))

        positionDirection = 0
        simulatedEntry = na
        simulatedTP = na
        simulatedSL = na
        simulatedEntryOffset = na
        simulatedEntryBar = na
        activeTpBox = na
        activeSlBox = na
        activeEntryZone = na
        activeEntryLine1 = na
        activeEntryLine2 = na
        activeInvalidationLine = na
        activeProjectionLine = na
        activeEntryTag = na
        activeTpTag = na
        activeSlTag = na
        activeInvalidationTag = na

    if exitLoss:
        if showStoppedTrades:
            label.new(bar_index, low if exitDirection == 1 else high, 'ATR SL HIT', xloc=xloc.bar_index, style=label.style_label_up if exitDirection == 1 else label.style_label_down, color=CLR_RED, textcolor=CLR_TEXT, size=f_label_size(signalLabelSize))
        else:
            if not na(activeTpBox):
                box.delete(activeTpBox)
            if not na(activeSlBox):
                box.delete(activeSlBox)
            if not na(activeEntryZone):
                box.delete(activeEntryZone)
            if not na(activeEntryLine1):
                line.delete(activeEntryLine1)
            if not na(activeEntryLine2):
                line.delete(activeEntryLine2)
            if not na(activeInvalidationLine):
                line.delete(activeInvalidationLine)
            if not na(activeProjectionLine):
                line.delete(activeProjectionLine)
            if not na(activeEntryTag):
                label.delete(activeEntryTag)
            if not na(activeTpTag):
                label.delete(activeTpTag)
            if not na(activeSlTag):
                label.delete(activeSlTag)
            if not na(activeInvalidationTag):
                label.delete(activeInvalidationTag)

        positionDirection = 0
        simulatedEntry = na
        simulatedTP = na
        simulatedSL = na
        simulatedEntryOffset = na
        simulatedEntryBar = na
        activeTpBox = na
        activeSlBox = na
        activeEntryZone = na
        activeEntryLine1 = na
        activeEntryLine2 = na
        activeInvalidationLine = na
        activeProjectionLine = na
        activeEntryTag = na
        activeTpTag = na
        activeSlTag = na
        activeInvalidationTag = na

    simulationState: str = 'ON' if enableSimulation else 'OFF'
    riskModelText: str = 'SL ' + f_fmt(stopLossAtrMultiplier) + ' ATR / TP ' + f_fmt(takeProfitRR) + 'R'

    biasText: str = ('BULLISH' if close > localEma else 'BEARISH' if close < localEma else 'NEUTRAL') if useLocalEmaFilter else 'FILTER OFF'

    biasColor: Color = (CLR_GREEN if close > localEma else CLR_RED if close < localEma else CLR_SILVER) if useLocalEmaFilter else CLR_MUTED

    sweepStateText: str = 'BULL SWEEP DETECTED' if validBuySweep else 'BEAR SWEEP DETECTED' if validSellSweep else 'BULL SWEEP PENDING' if bullWindowOpen else 'BEAR SWEEP PENDING' if bearWindowOpen else 'IDLE'

    sweepStateColor: Color = CLR_GREEN if validBuySweep else CLR_RED if validSellSweep else CLR_CYAN if bullWindowOpen or bearWindowOpen else CLR_MUTED

    signalStateText: str = 'BUY CONFIRMED' if plotLongSignal else 'SELL CONFIRMED' if plotShortSignal else 'TRADE ACTIVE' if tradeIsActive else 'WAITING'

    signalStateColor: Color = CLR_GREEN if plotLongSignal else CLR_RED if plotShortSignal else CLR_CYAN if tradeIsActive else CLR_MUTED

    panelScore: float = nz(pendingBullScore, 0.0) if bullWindowOpen else nz(pendingBearScore, 0.0) if bearWindowOpen else nz(lastSignalScore, 0.0)

    panelScoreColor: Color = f_score_color(panelScore)

    riskStateText: str = 'WARMING UP' if not riskModelReady else 'DEFENSIVE' if atrPct >= 0.8 else 'CONTROLLED' if atrPct >= 0.35 else 'LOW VOL'

    riskStateColor: Color = CLR_MUTED if not riskModelReady else CLR_RED if atrPct >= 0.8 else CLR_CYAN if atrPct >= 0.35 else CLR_GREEN

    plotshape(validBuySweep, title='Bull Sweep', style=shape.circle, location=location.belowbar, color=color.new(CLR_CYAN, 0), size=size.tiny)
    plotshape(validSellSweep, title='Bear Sweep', style=shape.circle, location=location.abovebar, color=color.new(CLR_CYAN, 0), size=size.tiny)

    plotshape(plotLongSignal, title='Buy Signal Ring', style=shape.circle, location=location.belowbar, color=color.new(CLR_CYAN, 0), size=size.small)
    plotshape(plotShortSignal, title='Sell Signal Ring', style=shape.circle, location=location.abovebar, color=color.new(CLR_CYAN, 0), size=size.small)

    plotshape(plotLongSignal, title='Buy Signal Marker', style=shape.triangleup, location=location.belowbar, color=color.new(CLR_GREEN, 0), size=size.tiny)
    plotshape(plotShortSignal, title='Sell Signal Marker', style=shape.triangledown, location=location.abovebar, color=color.new(CLR_RED, 0), size=size.tiny)

    if showSignalLabels and plotLongSignal:
        label.new(bar_index, low, 'BUY', xloc=xloc.bar_index, style=label.style_label_up, color=CLR_GREEN_SOFT, textcolor=CLR_TEXT, size=f_label_size(signalLabelSize))

    if showSignalLabels and plotShortSignal:
        label.new(bar_index, high, 'SELL', xloc=xloc.bar_index, style=label.style_label_down, color=CLR_RED_SOFT, textcolor=CLR_TEXT, size=f_label_size(signalLabelSize))

    barcolor((color.new(CLR_GREEN, 0) if plotLongSignal else color.new(CLR_RED, 0) if plotShortSignal else na) if showSignalBarColors else na)

    panel: Persistent[Table] = table.new(f_table_position(panelPosition), 2, 10, border_width=1, border_color=CLR_BORDER)

    if barstate.islast:
        if showStatusPanel:
            table.cell(panel, 0, 0, 'LIQUIDITY ENTRY', bgcolor=CLR_PANEL_ALT, text_color=CLR_TEXT)
            table.cell(panel, 1, 0, 'STATUS PANEL', bgcolor=CLR_PANEL_ALT, text_color=CLR_GOLD)

            table.cell(panel, 0, 1, 'Simulation', bgcolor=CLR_PANEL, text_color=CLR_MUTED)
            table.cell(panel, 1, 1, simulationState, bgcolor=CLR_PANEL, text_color=CLR_CYAN)

            table.cell(panel, 0, 2, 'Risk Model', bgcolor=CLR_BG, text_color=CLR_TEXT)
            table.cell(panel, 1, 2, riskModelText, bgcolor=CLR_BG, text_color=CLR_GOLD)

            table.cell(panel, 0, 3, 'Bias', bgcolor=CLR_BG, text_color=CLR_TEXT)
            table.cell(panel, 1, 3, biasText, bgcolor=CLR_BG, text_color=biasColor)

            table.cell(panel, 0, 4, 'Sweep State', bgcolor=CLR_BG, text_color=CLR_TEXT)
            table.cell(panel, 1, 4, sweepStateText, bgcolor=CLR_BG, text_color=sweepStateColor)

            table.cell(panel, 0, 5, 'Signal State', bgcolor=CLR_BG, text_color=CLR_TEXT)
            table.cell(panel, 1, 5, signalStateText, bgcolor=CLR_BG, text_color=signalStateColor)

            table.cell(panel, 0, 6, 'Quality Score', bgcolor=CLR_BG, text_color=CLR_TEXT)
            table.cell(panel, 1, 6, f_fmt(panelScore), bgcolor=CLR_BG, text_color=panelScoreColor)

            table.cell(panel, 0, 7, 'Volatility', bgcolor=CLR_BG, text_color=CLR_TEXT)
            table.cell(panel, 1, 7, volatilityState, bgcolor=CLR_BG, text_color=volatilityColor)

            table.cell(panel, 0, 8, 'Session', bgcolor=CLR_BG, text_color=CLR_TEXT)
            table.cell(panel, 1, 8, sessionState, bgcolor=CLR_BG, text_color=sessionColor)

            table.cell(panel, 0, 9, 'Risk State', bgcolor=CLR_BG, text_color=CLR_TEXT)
            table.cell(panel, 1, 9, riskStateText, bgcolor=CLR_BG, text_color=riskStateColor)
        else:
            f_panel_clear(panel)

    alertcondition(plotLongSignal, title='Bullish Liquidity Reclaim', message='Bullish liquidity reclaim confirmed')
    alertcondition(plotShortSignal, title='Bearish Liquidity Reclaim', message='Bearish liquidity reclaim confirmed')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
