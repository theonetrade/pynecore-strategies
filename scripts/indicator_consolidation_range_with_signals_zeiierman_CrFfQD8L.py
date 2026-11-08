"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, fill, high, input, label, line, low, math, na,
    nz, plot, script, size, ta
)
from pynecore.types import Color, Persistent, PersistentSeries, Series

t1: str = "Select the method used for detecting ranging market conditions.\n\n ADX: Uses the Average Directional Index to identify non-trending periods when ADX is below a set threshold.\n\n Volatility: Detects ranges by identifying periods of compression in volatility using standard deviation, variance, and ATR filters.\n\n Price Action: Confirms range by measuring the high-low percentage contraction and requiring a minimum number of DMI crosses, suggesting indecision or balance in price action."
t2: str = "Length or period used for detecting the range."
t3: str = "Multiplier applied to the calculated band distance."
t4: str = "Toggle to display Take Profit and Stop Loss levels on the chart."
t5: str = "Minimum number of bars between two consecutive SL/TP entries."
t6: str = "Stop Loss multiplier from the filtered base value."
t7: str = "Take Profit 1 multiplier from the filtered base value."
t8: str = "Take Profit 2 multiplier from the filtered base value."
t9: str = "Take Profit 3 multiplier from the filtered base value."
t10: str = "ADX threshold under which the market is considered ranging."
t11: str = "Smoothing period used for the ADX calculation."
t12: str = "Standard deviation compression threshold used to detect low volatility."
t13: str = "Variance compression threshold used to detect low volatility."
t14: str = "ATR compression threshold used to detect low volatility."


@script.indicator('Consolidation Range with Signals (Zeiierman)', overlay=True, max_labels_count=500, max_lines_count=500)
def main(
    method__ren__=input.string("ADX", options=("ADX", "Volatility"), title="Range Detection Method", group="Range Detection", tooltip=t1),
    len=input.int(10, minval=2, title="Range Period", group="Range Detection", tooltip=t2),
    band_mult=input.float(1.8, step=0.1, minval=0.01, title="Range Multiplier", group="Range Detection", tooltip=t3),
    upper_col=input.color(color.new('#0060E6'), title="Range", group="Range Detection", inline="bandcol"),
    lower_col=input.color(color.new('#29FAFA'), title="", group="Range Detection", inline="bandcol"),
    pos_col=input.color(color.new('#0060E6'), title="Trend", group="Range Detection", inline="trendcol"),
    neg_col=input.color(color.new('#29FAFA'), title="", group="Range Detection", inline="trendcol"),
    showTP=input.bool(True, title="Show SL/TP Levels", group="Targets", tooltip=t4),
    cooldown=input.int(20, title="SL/TP Cooldown (Bars)", group="Targets", tooltip=t5),
    sl_mult=input.float(0.4, step=0.1, minval=0.01, title="SL", group="Targets", inline="sl", tooltip=t6),
    showsl=input.bool(True, title="", group="Targets", inline="sl", tooltip=t6),
    tp1_mult=input.float(0.5, step=0.1, minval=0.01, title="TP1", group="Targets", inline="tp1", tooltip=t7),
    showtp1=input.bool(True, title="", group="Targets", inline="tp1", tooltip=t7),
    tp2_mult=input.float(1.0, step=0.1, minval=0.01, title="TP2", group="Targets", inline="tp2", tooltip=t8),
    showtp2=input.bool(False, title="", group="Targets", inline="tp2", tooltip=t8),
    tp3_mult=input.float(2.0, step=0.1, minval=0.01, title="TP3", group="Targets", inline="tp3", tooltip=t9),
    showtp3=input.bool(False, title="", group="Targets", inline="tp3", tooltip=t9),
    entry_col=input.color(color.blue, title="Entry", group="Targets", inline="tpcol"),
    sl_col=input.color(color.new('#FF0000'), title="SL", group="Targets", inline="tpcol"),
    bullColor=input.color(color.new('#09C10F'), title="TP", group="Targets", inline="tpcol"),
    bearColor=input.color(color.new('#FF69CB'), title="", group="Targets", inline="tpcol"),
    adx_thresh=input.int(17, step=1, minval=0, title="ADX Threshold", group="ADX", tooltip=t10),
    adx_smooth=input.int(10, step=1, minval=0, title="ADX Smoothing", group="ADX", tooltip=t11),
    vol_mult_std=input.float(0.8, step=0.1, minval=0.001, title="StdDev Multiplier", group="Volatility", tooltip=t12),
    vol_mult_var=input.float(0.8, step=0.1, minval=0.001, title="Variance Multiplier", group="Volatility", tooltip=t13),
    vol_mult_atr=input.float(0.9, step=0.1, minval=0.001, title="ATR Multiplier", group="Volatility", tooltip=t14)
):
    _, _, adx = ta.dmi(len, adx_smooth)
    isADX = adx < adx_thresh
    logret = math.log(close / close[1])
    std_now = ta.stdev(logret, len)
    std_avg = ta.sma(std_now, len)
    atr_now = ta.atr(len)
    atr_avg = ta.sma(atr_now, len)
    var_now = ta.variance(logret, len)
    var_avg = ta.sma(var_now, len)
    isVolatility = std_now < std_avg * vol_mult_std and var_now < var_avg * vol_mult_var and (atr_now < atr_avg * vol_mult_atr)
    methodDetected = method__ren__ == 'ADX' and isADX or (method__ren__ == 'Volatility' and isVolatility)
    rngfilt: PersistentSeries[float] = close
    trendColor: PersistentSeries[Color] = na(Color)
    rangeVisible: Persistent[bool] = False
    prev_hi: Persistent[float] = na(float)
    prev_lo: Persistent[float] = na(float)
    rangeStartBar: Persistent[int] = na(int)
    rangeBarsActive: Persistent[int] = 0
    lastBreakoutBar: Persistent[int] = na(int)
    if methodDetected and na(rangeStartBar):
        rangeStartBar = bar_index
    elif not methodDetected:
        rangeStartBar = na
    if methodDetected:
        rangeVisible = True
    diff = math.abs(high - low[1])
    r = ta.sma(2.618 * diff, 2000) * band_mult
    def pricejump(prev):
        highJump = prev + math.abs(close - prev) / r * r
        lowJump = prev - math.abs(close - prev) / r * r
        return (highJump, lowJump)

    def rangefilter(hhjump, lljump, prev):
        hhBreak = close > prev
        hhTooClose = close - r < prev
        hhShift = close - r
        llTooClose = close + r > prev
        llShift = close + r
        step1 = (prev if hhTooClose else hhShift) if hhBreak else prev if llTooClose else llShift
        hhAbove = close >= prev + r
        llBelow = close <= prev - r
        return hhjump if hhAbove else lljump if llBelow else step1

    def bands(filt):
        return (filt + r, filt - r)

    def trenddir(filt: Series):
        return (filt > nz(filt[1]), filt < nz(filt[1]))

    def trendcomp(filt):
        return (filt, ta.sma(filt, 2), ta.sma(filt, 4))

    prev = nz(rngfilt[1])
    hhJ, llJ = pricejump(prev)
    rngfilt = rangefilter(hhJ, llJ, prev)
    prev_rngfilt = nz(rngfilt[1])
    rngfilt_step_up = rngfilt > prev_rngfilt
    rngfilt_step_down = rngfilt < prev_rngfilt
    hiband, loband = bands(rngfilt)
    up, down = trenddir(rngfilt)
    TrendFast, TrendMed, TrendLong = trendcomp(rngfilt)
    if methodDetected:
        prev_hi = hiband
        prev_lo = loband
    if not methodDetected and (close[1] > prev_hi or close[1] < prev_lo):
        rangeVisible = False

    MIDX1 = (hiband - rngfilt) / 3
    MID1 = rngfilt + MIDX1
    MID2 = MID1 + MIDX1
    MIDX2 = (rngfilt - loband) / 3
    MID3 = rngfilt - MIDX2
    MID4 = MID3 - MIDX2
    trendColor = pos_col if up else neg_col if down else trendColor[1]
    plotTrend = plot(TrendFast if rangeVisible else close, 'Trend', trendColor if rangeVisible else color.new(trendColor, 100), 1)

    plotMid1 = plot(MID1 if rangeVisible else close, 'MID1', color.new(upper_col, 50) if rangeVisible else color.new(upper_col, 100), style=plot.style_stepline)
    plotMid2 = plot(MID2 if rangeVisible else close, 'MID2', color.new(upper_col, 50) if rangeVisible else color.new(upper_col, 100), style=plot.style_stepline)
    plotMid3 = plot(MID3 if rangeVisible else close, 'MID3', color.new(lower_col, 50) if rangeVisible else color.new(lower_col, 100), style=plot.style_stepline)
    plotMid4 = plot(MID4 if rangeVisible else close, 'MID4', color.new(lower_col, 50) if rangeVisible else color.new(lower_col, 100), style=plot.style_stepline)
    fill(plotMid2, plotTrend, MID2, TrendFast, color.new(upper_col, 60), na)
    fill(plotMid4, plotTrend, MID4, TrendFast, color.new(lower_col, 60), na)
    rangeBarsActive = 0 if na(rangeStartBar) else bar_index - rangeStartBar
    canTriggerBreakout = na(lastBreakoutBar) or bar_index - lastBreakoutBar >= cooldown
    enterLong = rangeVisible and rngfilt_step_up and canTriggerBreakout
    enterShort = rangeVisible and rngfilt_step_down and canTriggerBreakout
    def calcSLTP(isLong):
        base = rngfilt
        offset = r * sl_mult
        tp1off = r * tp1_mult
        tp2off = r * tp2_mult
        tp3off = r * tp3_mult
        stop_ = base - offset if isLong else base + offset
        tp1_ = base + tp1off if isLong else base - tp1off
        tp2_ = base + tp2off if isLong else base - tp2off
        tp3_ = base + tp3off if isLong else base - tp3off
        return (stop_, tp1_, tp2_, tp3_)

    def drawLevels(entry, sl, tp1, tp2, tp3, col):
        if showTP:
            line.new(bar_index, entry, bar_index + 20, entry, color=entry_col, width=2)
            if showsl:
                line.new(bar_index, sl, bar_index + 20, sl, color=color.new(sl_col, 0), width=2)
            if showtp1:
                line.new(bar_index, tp1, bar_index + 20, tp1, color=color.new(col, 0), width=2)
            if showtp2:
                line.new(bar_index, tp2, bar_index + 20, tp2, color=color.new(col, 0), width=2)
            if showtp3:
                line.new(bar_index, tp3, bar_index + 20, tp3, color=color.new(col, 0), width=2)
        __block_result__ = na
        if showTP:
            label.new(bar_index + 20, entry, 'Entry', style=label.style_label_left, color=entry_col, textcolor=color.white, size=size.tiny)
            if showsl:
                label.new(bar_index + 20, sl, 'SL', style=label.style_label_left, color=color.new(sl_col, 0), textcolor=color.white, size=size.tiny)
            if showtp1:
                label.new(bar_index + 20, tp1, 'TP 1', style=label.style_label_left, color=color.new(col, 0), textcolor=color.white, size=size.tiny)
            if showtp2:
                label.new(bar_index + 20, tp2, 'TP 2', style=label.style_label_left, color=color.new(col, 0), textcolor=color.white, size=size.tiny)
            __block_result_1__ = na
            if showtp3:
                __block_result_1__ = label.new(bar_index + 20, tp3, 'TP 3', style=label.style_label_left, color=color.new(col, 0), textcolor=color.white, size=size.tiny)
            __block_result__ = __block_result_1__
        return __block_result__

    SL: Persistent[float] = na(float)
    TP1: Persistent[float] = na(float)
    TP2: Persistent[float] = na(float)
    TP3: Persistent[float] = na(float)
    if enterLong and showTP and (na(lastBreakoutBar) or bar_index - lastBreakoutBar >= cooldown):
        s, t1_, t2_, t3_ = calcSLTP(True)
        SL = s
        TP1 = t1_
        TP2 = t2_
        TP3 = t3_
        drawLevels(close, SL, TP1, TP2, TP3, bullColor)
        lastBreakoutBar = bar_index
    if enterShort and showTP and (na(lastBreakoutBar) or bar_index - lastBreakoutBar >= cooldown):
        s, t1_, t2_, t3_ = calcSLTP(False)
        SL = s
        TP1 = t1_
        TP2 = t2_
        TP3 = t3_
        drawLevels(close, SL, TP1, TP2, TP3, bearColor)
        lastBreakoutBar = bar_index


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
