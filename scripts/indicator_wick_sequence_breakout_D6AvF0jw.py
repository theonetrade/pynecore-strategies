"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, box, close, color, display,
    extend, format, high, input, label, line, linefill, location, low, math, na, open, plot,
    plotshape, script, shape, size, string, syminfo, ta, volume
)
from pynecore.types import Box, Color, Label, Line, LineFill, NA, Persistent, Series


@udt
class Formation:
    mainBox: Box = na(Box)
    top: float = na(float)
    bot: float = na(float)
    leftBar: int = na(int)
    formBar: int = na(int)
    bullVol: float = na(float)
    bearVol: float = na(float)
    bullVolBox: Box = na(Box)
    bearVolBox: Box = na(Box)
    volLabel: Label = na(Label)
    mixed: bool = False


grpGen: str = "Candle & Signal Settings"
grpFilters: str = "Signal Filters"
grpAbs: str = "Absorption (small candle, high volume)"
grpExtra: str = "Formations"
grpVis: str = "Colors & Visualization"
grpTPSL: str = "TP/SL"
grpTPSLDisp: str = "TP/SL — Display"


@script.indicator("Wick Sequence Breakout", shorttitle="WSB", overlay=True, max_labels_count=500, max_boxes_count=500, max_lines_count=500)
def main(
    nBars=input.int(3, "Min. number of wick candles", minval=1, maxval=20, tooltip="How many candles with the required wick must occur within the window below for the formation to be considered valid.", group=grpGen),
    windowSize=input.int(5, "Window size (candles)", minval=1, maxval=50, tooltip="Number of most recent candles scanned for the required wick count.", group=grpGen),
    minUpperBear=input.float(45.0, "Min. upper wick share — bearish formation (%)", minval=0.0, maxval=100.0, step=1.0, tooltip="Minimum percentage share of the upper wick in the candle's total range.", group=grpGen),
    maxLowerBear=input.float(25.0, "Max. lower wick share — bearish formation (%)", minval=0.0, maxval=100.0, step=1.0, tooltip="Maximum allowed share of the lower wick in the candle's range.", group=grpGen),
    minLowerBull=input.float(45.0, "Min. lower wick share — bullish formation (%)", minval=0.0, maxval=100.0, step=1.0, tooltip="Minimum percentage share of the lower wick in the candle's total range.", group=grpGen),
    maxUpperBull=input.float(25.0, "Max. upper wick share — bullish formation (%)", minval=0.0, maxval=100.0, step=1.0, tooltip="Maximum allowed share of the upper wick in the candle's range.", group=grpGen),
    maxWaitBars=input.int(100, "Breakout wait limit (bars)", minval=0, tooltip="After how many candles without a breakout the box is cancelled. 0 = no limit.", group=grpGen),
    useCloseBO=input.bool(True, "Breakout by close price", tooltip="ON: breakout is evaluated using the closing price. OFF: evaluated using the candle's high/low.", group=grpGen),
    useMinRange=input.bool(False, "Filter small candles (ATR)", tooltip="Ignores candles whose range is smaller than ATR × the multiplier below, so tiny candles with random wicks do not build formations.\n\nSmall candles traded on high volume can still count through the Absorption setting.", group=grpFilters),
    minAtrMult=input.float(0.3, "ATR multiplier", minval=0.0, step=0.05, tooltip="Minimum candle range as a multiple of ATR for the candle to be taken into account.", group=grpFilters),
    atrLen=input.int(14, "ATR period", minval=1, tooltip="Number of candles used to calculate ATR.", group=grpFilters),
    useSignalSizeFilter=input.bool(False, "Filter by breakout candle size", tooltip="Requires the breakout candle to be sufficiently large relative to the average range.", group=grpFilters),
    signalSizeMult=input.float(1.5, "Size multiplier", minval=0.1, step=0.1, tooltip="Minimum breakout candle range as a multiple of the average range.", group=grpFilters),
    signalSizeLen=input.int(20, "Average candle size period", minval=1, tooltip="Number of candles used to calculate the average range.", group=grpFilters),
    showBearSig=input.bool(True, "Show bearish signals", tooltip="Filter: when disabled, the bearish signal (triangle + alert) is not generated at all, not just hidden.", group=grpFilters),
    showBullSig=input.bool(True, "Show bullish signals", tooltip="Filter: when disabled, the bullish signal (triangle + alert) is not generated at all, not just hidden.", group=grpFilters),
    removeInvalidBox=input.bool(True, "Remove box on mismatched signal", tooltip="ON: the formation box is removed from the chart (along with volume bars and % label) when the breakout direction does not match the dominant volume side — it does not remain on the chart in the neutral color. OFF: the box remains on the chart, painted in the neutral color.", group=grpFilters),
    useAbsorption=input.bool(True, "Count absorption candles", tooltip="Absorption = a small candle traded on high volume: a lot of buying or selling took place, yet price barely moved, which suggests the other side is soaking up the orders.\n\nON: such candles count toward a formation just like wick candles, including small wick candles that are filtered out by the ATR size filter. Direction comes from the wick if the candle has a qualifying one, otherwise from where it closed.\nOFF: only wick candles count.\n\nHas no effect on symbols without volume data.", group=grpAbs),
    volAvgLen=input.int(20, "Average volume period", minval=1, tooltip="Number of candles used for the average volume that absorption candles are compared against.", group=grpAbs),
    absVolMult=input.float(1.1, "Volume multiplier", minval=1.0, step=0.1, tooltip="How much above average the volume must be. 1.1 = at least 10% above average volume. Higher values = fewer, more significant absorption candles.", group=grpAbs),
    absMaxAtr=input.float(0.6, "Max. candle size (× ATR)", minval=0.05, step=0.05, tooltip="Maximum candle range, as a multiple of ATR, for the candle to be considered small. Lower values = only very tight candles qualify.", group=grpAbs),
    absClosePct=input.float(60.0, "Close location threshold (%)", minval=50.0, maxval=100.0, step=1.0, tooltip="Used for absorption candles without a qualifying wick. 0% = close at the low, 100% = close at the high.\nBullish: close at or above this level (buyers held price up).\nBearish: close at or below 100 minus this level (sellers held price down).\nCloses in between are treated as indecisive and ignored.", group=grpAbs),
    maxConcurrent=input.int(2, "Max. active formations", minval=1, maxval=30, tooltip="How many boxes can wait for a breakout at the same time.\n1: a new formation is detected only after the current one is resolved.\nHigher values: overlapping setups are tracked separately, at the cost of a busier chart. Values of 2–4 are usually enough.", group=grpExtra),
    useMixed=input.bool(True, "Mixed formations", tooltip="ON: a box is also drawn when the window contains enough wick/absorption candles in total, but neither buyers nor sellers reach the minimum on their own. This marks indecision or compression before a move. The direction is decided by the breakout and the dominant volume, like in other formations. Drawn with a dashed border.", group=grpExtra),
    keepExpiredBox=input.bool(False, "Keep expired boxes", tooltip="ON: a box that reaches the breakout wait limit stays on the chart, greyed out and labelled EXPIRED, so you can review setups that never triggered.\nOFF: expired boxes are removed.", group=grpExtra),
    paintWicks=input.bool(True, "Highlight wick candles", tooltip="Colors individual candles that qualify for a formation, regardless of whether a formation appears. Wick candles are lightly tinted, absorption candles more strongly.", group=grpVis),
    colBull=input.color(color.rgb(6, 162, 47), "Bullish color", tooltip="Used for signals, boxes, and bars on the buyer side.", group=grpVis),
    colBear=input.color(color.rgb(207, 23, 23), "Bearish color", tooltip="Used for signals, boxes, and bars on the seller side.", group=grpVis),
    colNeutral=input.color(color.gray, "Neutral color", tooltip="Used for the box while waiting and for the label in case of a tie.", group=grpVis),
    boxFillTransp=input.int(85, "Box background transparency", minval=0, maxval=100, tooltip="Transparency of the formation box fill (0 = full color, 100 = invisible).", group=grpVis),
    boxBorderTransp=input.int(60, "Box border transparency", minval=0, maxval=100, tooltip="Transparency of the formation box border.", group=grpVis),
    showVolBars=input.bool(True, "Show volume bars", tooltip="Visualizes the ratio of buy to sell volume beneath the box.", group=grpVis),
    showVolPctLabel=input.bool(True, "Show % label", tooltip="Shows the percentage share of the volume-dominant side.", group=grpVis),
    showTargets=input.bool(True, "Show TP/SL levels", tooltip="Draws Entry, Stop Loss, and Take Profit levels for each new breakout signal.", group=grpTPSL),
    useAtrSL=input.bool(True, "SL = ATR", tooltip="Enabled: the Stop Loss distance from the entry price is calculated based on ATR (ATR multiplier for SL).\nDisabled: a fixed percentage value is used (SL % from Entry).", group=grpTPSL),
    tpAtrPeriod=input.int(14, "ATR period (TP/SL)", minval=1, tooltip="ATR period used to determine the Stop Loss distance and Take Profit levels. Independent from the candle filter's ATR period.", group=grpTPSL),
    slAtrMult=input.float(1.5, "ATR multiplier for SL", step=0.1, group=grpTPSL, tooltip="ATR multiplier determining the Stop Loss distance from the entry price, active when SL = ATR is enabled."),
    slPercent=input.float(1.0, "SL % from Entry", step=0.1, group=grpTPSL, tooltip="Percentage distance of the Stop Loss from the entry price, used when SL = ATR is disabled."),
    rrTP1=input.float(1.0, "RR for TP1", step=0.1, group=grpTPSL, tooltip="Risk:Reward ratio for Take Profit level 1. A value of 1.0 means TP1 is located at a distance equal to the risk (SL) from the entry price."),
    rrTP2=input.float(2.0, "RR for TP2", step=0.1, group=grpTPSL, tooltip="Risk:Reward ratio for Take Profit level 2."),
    rrTP3=input.float(3.0, "RR for TP3", step=0.1, group=grpTPSL, tooltip="Risk:Reward ratio for Take Profit level 3."),
    showSlLevel=input.bool(True, "Show SL level", tooltip="Draws the Stop Loss line and label for the active signal.", group=grpTPSLDisp),
    showTp1Level=input.bool(True, "Show TP1 level", tooltip="Draws the Take Profit 1 line and label for the active signal.", group=grpTPSLDisp),
    showTp2Level=input.bool(True, "Show TP2 level", tooltip="Draws the Take Profit 2 line and label for the active signal.", group=grpTPSLDisp),
    showTp3Level=input.bool(True, "Show TP3 level", tooltip="Draws the Take Profit 3 line and label for the active signal.", group=grpTPSLDisp)
):
    colBearBar: Color = color.new(colBear, 70)
    colBullBar: Color = color.new(colBull, 70)
    colBearAbsBar: Color = color.new(colBear, 35)
    colBullAbsBar: Color = color.new(colBull, 35)
    colBearSig: Color = colBear
    colBullSig: Color = colBull

    colBoxActive: Color = color.new(colNeutral, boxFillTransp)
    colBoxBull: Color = color.new(colBull, boxFillTransp)
    colBoxBear: Color = color.new(colBear, boxFillTransp)
    colBoxInvalid: Color = color.new(colNeutral, boxFillTransp)

    borderActive: Color = color.new(colNeutral, boxBorderTransp)
    borderBull: Color = color.new(colBull, boxBorderTransp)
    borderBear: Color = color.new(colBear, boxBorderTransp)
    borderInvalid: Color = color.new(colNeutral, boxBorderTransp)

    colBullVolBar: Color = color.new(colBull, 15)
    colBearVolBar: Color = color.new(colBear, 15)

    rng: float = high - low
    upperWickPct: float = (high - math.max(open, close)) / rng * 100.0 if rng > 0 else 0.0
    lowerWickPct: float = (math.min(open, close) - low) / rng * 100.0 if rng > 0 else 0.0

    atrVal: float = ta.atr(atrLen)
    atrTP: float = ta.atr(tpAtrPeriod)

    avgCandleRange: Series[float] = ta.sma(rng, signalSizeLen)

    avgVol: float = ta.sma(volume, volAvgLen)
    highVolAbs: bool = useAbsorption and (not na(avgVol)) and (avgVol > 0) and (not na(volume)) and (volume >= avgVol * absVolMult)

    rangeOk: bool = not useMinRange or rng >= atrVal * minAtrMult

    bearWickShape: bool = upperWickPct >= minUpperBear and lowerWickPct <= maxLowerBear
    bullWickShape: bool = lowerWickPct >= minLowerBull and upperWickPct <= maxUpperBull

    isBearWick: bool = rangeOk and bearWickShape
    isBullWick: bool = rangeOk and bullWickShape

    closePos: float = (close - low) / rng * 100.0 if rng > 0 else 50.0
    isAbsorption: bool = highVolAbs and rng > 0 and (rng <= atrVal * absMaxAtr) and (not isBearWick) and (not isBullWick)
    isBullAbs: bool = isAbsorption and (bullWickShape or (not bearWickShape and closePos >= absClosePct))
    isBearAbs: bool = isAbsorption and (bearWickShape or (not bullWickShape and closePos <= 100.0 - absClosePct))

    isBearCand: Series[bool] = isBearWick or isBearAbs
    isBullCand: Series[bool] = isBullWick or isBullAbs

    barcolor((colBearBar if isBearWick else colBullBar if isBullWick else colBearAbsBar if isBearAbs else colBullAbsBar if isBullAbs else na) if paintWicks else na)

    def countBearInWindow(len: int):
        __hist_isBearCand__: Series[bool] = isBearCand[0]
        c: int = 0
        for i in pine_range(0, len - 1):
            c = c + (1 if __hist_isBearCand__[i] else 0)
        return c

    def countBullInWindow(len: int):
        __hist_isBullCand__: Series[bool] = isBullCand[0]
        c: int = 0
        for i in pine_range(0, len - 1):
            c = c + (1 if __hist_isBullCand__[i] else 0)
        return c

    def countAnyInWindow(len: int):
        __hist_isBullCand__: Series[bool] = isBullCand[0]
        __hist_isBearCand__: Series[bool] = isBearCand[0]
        c: int = 0
        for i in pine_range(0, len - 1):
            c = c + (1 if __hist_isBearCand__[i] or __hist_isBullCand__[i] else 0)
        return c

    bearCnt: int = countBearInWindow(windowSize)
    bullCnt: int = countBullInWindow(windowSize)
    anyCnt: int = countAnyInWindow(windowSize)

    bearPatternRaw: bool = bearCnt >= nBars
    bullPatternRaw: bool = bullCnt >= nBars

    bearPattern: Series[bool] = bearPatternRaw and (not bullPatternRaw)
    bullPattern: Series[bool] = bullPatternRaw and (not bearPatternRaw)

    mixedPattern: Series[bool] = useMixed and anyCnt >= nBars and (not bearPattern) and (not bullPattern)

    bearFormed: bool = bearPattern and (not bearPattern[1])
    bullFormed: bool = bullPattern and (not bullPattern[1])
    mixedFormed: bool = mixedPattern and (not mixedPattern[1])

    hhFormation: float = ta.highest(high, windowSize)
    llFormation: float = ta.lowest(low, windowSize)

    signalSizeOk: bool = not useSignalSizeFilter or rng >= avgCandleRange[1] * signalSizeMult

    def f_backfillBoxVol(lenBars: int, top: float, bot: float):
        bBull: float = 0.0
        bBear: float = 0.0
        for off in pine_range(0, lenBars - 1):
            h: float = high[off]
            l: float = low[off]
            c: float = close[off]
            v: float = volume[off]
            r: float = math.max(h - l, syminfo.mintick)
            if h > bot and l < top:
                bBull += v * (c - l) / r
                bBear += v * (h - c) / r
        return (bBull, bBear)


    forms: Persistent[list[Formation]] = array.new(0, NA(Formation))

    def f_deleteAll(f: Formation):
        box.delete(f.mainBox)
        if not na(f.bullVolBox):
            box.delete(f.bullVolBox)
            box.delete(f.bearVolBox)
        if not na(f.volLabel):
            label.delete(f.volLabel)
        return True

    def f_finalize(f: Formation, dir: int):
        box.set_right(f.mainBox, bar_index)
        box.set_bgcolor(f.mainBox, colBoxBull if dir == 1 else colBoxBear)
        box.set_border_color(f.mainBox, borderBull if dir == 1 else borderBear)
        box.set_extend(f.mainBox, extend.none)
        return True

    def f_invalidate(f: Formation):
        if removeInvalidBox:
            f_deleteAll(f)
        else:
            box.set_right(f.mainBox, bar_index)
            box.set_bgcolor(f.mainBox, colBoxInvalid)
            box.set_border_color(f.mainBox, borderInvalid)
            box.set_extend(f.mainBox, extend.none)
        return True

    def f_expire(f: Formation):
        if keepExpiredBox:
            box.set_right(f.mainBox, bar_index)
            box.set_bgcolor(f.mainBox, color.new(colNeutral, 92))
            box.set_border_color(f.mainBox, color.new(colNeutral, 75))
            box.set_extend(f.mainBox, extend.none)
            if not na(f.volLabel):
                label.set_text(f.volLabel, 'EXPIRED')
                label.set_color(f.volLabel, color.gray)
        else:
            f_deleteAll(f)
        return True

    recentActive: bool = False
    if array.size(forms) > 0:
        for j in pine_range(0, array.size(forms) - 1):
            g: Formation = array.get(forms, j)
            if g.formBar > bar_index - windowSize:
                recentActive = True

    createNew: bool = (bearFormed or bullFormed or (mixedFormed and (not recentActive))) and array.size(forms) < maxConcurrent

    if createNew:
        isMixed: bool = not bearFormed and (not bullFormed)
        f: Formation = Formation()
        f.top = hhFormation
        f.bot = llFormation
        f.leftBar = bar_index - windowSize + 1
        f.formBar = bar_index
        f.mixed = isMixed

        f.mainBox = box.new(f.leftBar, f.top, bar_index + 1, f.bot, bgcolor=colBoxActive, border_color=borderActive, border_style=line.style_dashed if isMixed else line.style_solid, force_overlay=True)

        bfBull, bfBear = f_backfillBoxVol(windowSize, f.top, f.bot)
        f.bullVol = bfBull
        f.bearVol = bfBear

        if showVolBars:
            f.bullVolBox = box.new(f.leftBar, f.bot, f.leftBar, f.bot, bgcolor=colBullVolBar, border_color=colBullVolBar, force_overlay=True)
            f.bearVolBox = box.new(f.leftBar, f.bot, f.leftBar, f.bot, bgcolor=colBearVolBar, border_color=colBearVolBar, force_overlay=True)
        if showVolPctLabel:
            f.volLabel = label.new(f.leftBar, f.bot, '', style=label.style_label_upper_left, color=colNeutral, textcolor=color.white, size=size.small, force_overlay=True)

        array.push(forms, f)

    bullSignal: bool = False
    bearSignal: bool = False

    if array.size(forms) > 0:
        for i in pine_range(array.size(forms) - 1, 0):
            f: Formation = array.get(forms, i)
            removeIt: bool = False

            breakoutUp: bool = (close if useCloseBO else high) > f.top
            breakoutDown: bool = (close if useCloseBO else low) < f.bot

            box.set_right(f.mainBox, bar_index + 1)
            box.set_top(f.mainBox, f.top)
            box.set_bottom(f.mainBox, f.bot)

            if bar_index > f.formBar and (not (breakoutUp or breakoutDown)):
                rNow: float = math.max(high - low, syminfo.mintick)
                if high > f.bot and low < f.top:
                    f.bullVol += volume * (close - low) / rNow
                    f.bearVol += volume * (high - close) / rNow

            if showVolBars and (not na(f.bullVolBox)) or (showVolPctLabel and (not na(f.volLabel))):
                barH: float = atrVal * 0.18
                gapH: float = atrVal * 0.08
                bullTop: float = f.bot - gapH
                bullBot: float = bullTop - barH
                bearTop: float = bullBot - gapH
                bearBot: float = bearTop - barH

                if showVolBars and (not na(f.bullVolBox)):
                    totalVolBars: float = f.bullVol + f.bearVol
                    fullWidth: int = math.max(bar_index + 1 - f.leftBar, 1)
                    bullRight: int = f.leftBar + math.round(fullWidth * (f.bullVol / totalVolBars)) if totalVolBars > 0 else f.leftBar + math.round(fullWidth * 0.5)
                    bearRight: int = f.leftBar + math.round(fullWidth * (f.bearVol / totalVolBars)) if totalVolBars > 0 else f.leftBar + math.round(fullWidth * 0.5)
                    box.set_lefttop(f.bullVolBox, f.leftBar, bullTop)
                    box.set_rightbottom(f.bullVolBox, bullRight, bullBot)
                    box.set_lefttop(f.bearVolBox, f.leftBar, bearTop)
                    box.set_rightbottom(f.bearVolBox, bearRight, bearBot)

                if showVolPctLabel and (not na(f.volLabel)):
                    totalVol: float = f.bullVol + f.bearVol
                    bullPct: float = f.bullVol / totalVol * 100.0 if totalVol > 0 else 50.0
                    sellPct: float = 100.0 - bullPct
                    bgCol: Color = colBull if bullPct >= 50.0 else colBear
                    txt: str = 'Buy ' + string.tostring(bullPct, '#.#') + '%\nSell ' + string.tostring(sellPct, '#.#') + '%'
                    label.set_xy(f.volLabel, f.leftBar, bearBot - gapH * 0.5)
                    label.set_text(f.volLabel, txt)
                    label.set_color(f.volLabel, bgCol)

            bullDom: bool = f.bullVol >= f.bearVol
            bearDom: bool = f.bearVol > f.bullVol
            validDirUp: bool = breakoutUp and bullDom
            validDirDown: bool = breakoutDown and bearDom

            if breakoutUp or breakoutDown:
                if validDirUp or validDirDown:
                    f_finalize(f, 1 if validDirUp else -1)
                    if signalSizeOk:
                        if validDirUp and showBullSig:
                            bullSignal = True
                        if validDirDown and showBearSig:
                            bearSignal = True
                else:
                    f_invalidate(f)
                removeIt = True
            elif maxWaitBars > 0 and bar_index - f.formBar > maxWaitBars:
                f_expire(f)
                removeIt = True

            if removeIt:
                array.remove(forms, i)

    tpslDir: Persistent[int] = 0
    tpslSL: Persistent[float] = na(float)
    tpslExtreme: Persistent[float] = na(float)
    tpslEntryLn: Persistent[Line] = na(Line)
    tpslEntryLb: Persistent[Label] = na(Label)
    tpslSlLn: Persistent[Line] = na(Line)
    tpslSlLb: Persistent[Label] = na(Label)
    tpslTp1Ln: Persistent[Line] = na(Line)
    tpslTp1Lb: Persistent[Label] = na(Label)
    tpslTp2Ln: Persistent[Line] = na(Line)
    tpslTp2Lb: Persistent[Label] = na(Label)
    tpslTp3Ln: Persistent[Line] = na(Line)
    tpslTp3Lb: Persistent[Label] = na(Label)
    tpslExtLn: Persistent[Line] = na(Line)
    tpslRiskFill: Persistent[LineFill] = na(LineFill)
    tpslRewardFill: Persistent[LineFill] = na(LineFill)
    tpslEntryBar: Persistent[int] = na(int)

    if showTargets and bullSignal != bearSignal:
        isBuyTrade: bool = bullSignal

        line.delete(tpslEntryLn)
        label.delete(tpslEntryLb)
        line.delete(tpslSlLn)
        label.delete(tpslSlLb)
        line.delete(tpslTp1Ln)
        label.delete(tpslTp1Lb)
        line.delete(tpslTp2Ln)
        label.delete(tpslTp2Lb)
        line.delete(tpslTp3Ln)
        label.delete(tpslTp3Lb)
        line.delete(tpslExtLn)
        linefill.delete(tpslRiskFill)
        linefill.delete(tpslRewardFill)

        tpslDir = 1 if isBuyTrade else -1
        tpslEntryBar = bar_index

        entryP: float = close
        riskDist: float = atrTP * slAtrMult if useAtrSL else entryP * (slPercent / 100.0)

        entryCol: Color = color.new(colBull if isBuyTrade else colBear, 40)
        slCol: Color = color.new(colBear if isBuyTrade else colBull, 40)
        tpCol: Color = color.new(colBull if isBuyTrade else colBear, 40)
        riskFillC: Color = color.new(colBear if isBuyTrade else colBull, 80)
        rewardFillC: Color = color.new(colBull if isBuyTrade else colBear, 80)

        slP: float = entryP - riskDist if isBuyTrade else entryP + riskDist
        tp1P: float = entryP + riskDist * rrTP1 if isBuyTrade else entryP - riskDist * rrTP1
        tp2P: float = entryP + riskDist * rrTP2 if isBuyTrade else entryP - riskDist * rrTP2
        tp3P: float = entryP + riskDist * rrTP3 if isBuyTrade else entryP - riskDist * rrTP3

        tpslSL = slP
        tpslExtreme = tp3P if showTp3Level else tp2P if showTp2Level else tp1P if showTp1Level else na

        tpslEntryLn = line.new(bar_index, entryP, bar_index + 1, entryP, color=entryCol, width=2, extend=extend.none)
        tpslEntryLb = label.new(bar_index, entryP, ('BUY ' if isBuyTrade else 'SELL ') + string.tostring(entryP, format.mintick), style=label.style_label_left, color=entryCol, textcolor=color.white, size=size.small)

        if showSlLevel:
            tpslSlLn = line.new(bar_index, slP, bar_index + 1, slP, color=slCol, width=1, style=line.style_dashed, extend=extend.none)
            tpslSlLb = label.new(bar_index, slP, 'SL ' + string.tostring(slP, format.mintick), style=label.style_label_left, color=slCol, textcolor=color.white, size=size.small)

        if showTp1Level:
            tpslTp1Ln = line.new(bar_index, tp1P, bar_index + 1, tp1P, color=tpCol, width=1, extend=extend.none)
            tpslTp1Lb = label.new(bar_index, tp1P, 'TP1 ' + string.tostring(tp1P, format.mintick), style=label.style_label_left, color=tpCol, textcolor=color.white, size=size.small)

        if showTp2Level:
            tpslTp2Ln = line.new(bar_index, tp2P, bar_index + 1, tp2P, color=tpCol, width=1, extend=extend.none)
            tpslTp2Lb = label.new(bar_index, tp2P, 'TP2 ' + string.tostring(tp2P, format.mintick), style=label.style_label_left, color=tpCol, textcolor=color.white, size=size.small)

        if showTp3Level:
            tpslTp3Ln = line.new(bar_index, tp3P, bar_index + 1, tp3P, color=tpCol, width=1, style=line.style_dotted, extend=extend.none)
            tpslTp3Lb = label.new(bar_index, tp3P, 'TP3 ' + string.tostring(tp3P, format.mintick), style=label.style_label_left, color=tpCol, textcolor=color.white, size=size.small)

        if showSlLevel:
            tpslRiskFill = linefill.new(tpslEntryLn, tpslSlLn, riskFillC)

        fillExtreme: float = entryP
        if isBuyTrade:
            if showTp1Level:
                fillExtreme = math.max(fillExtreme, tp1P)
            if showTp2Level:
                fillExtreme = math.max(fillExtreme, tp2P)
            if showTp3Level:
                fillExtreme = math.max(fillExtreme, tp3P)
            if fillExtreme > entryP:
                tpslExtLn = line.new(bar_index, fillExtreme, bar_index + 1, fillExtreme, color=na, extend=extend.none)
                tpslRewardFill = linefill.new(tpslEntryLn, tpslExtLn, rewardFillC)
        else:
            if showTp1Level:
                fillExtreme = math.min(fillExtreme, tp1P)
            if showTp2Level:
                fillExtreme = math.min(fillExtreme, tp2P)
            if showTp3Level:
                fillExtreme = math.min(fillExtreme, tp3P)
            if fillExtreme < entryP:
                tpslExtLn = line.new(bar_index, fillExtreme, bar_index + 1, fillExtreme, color=na, extend=extend.none)
                tpslRewardFill = linefill.new(tpslEntryLn, tpslExtLn, rewardFillC)

    if tpslDir != 0:
        if not na(tpslEntryLb):
            label.set_x(tpslEntryLb, bar_index)
        if not na(tpslSlLb):
            label.set_x(tpslSlLb, bar_index)
        if not na(tpslTp1Lb):
            label.set_x(tpslTp1Lb, bar_index)
        if not na(tpslTp2Lb):
            label.set_x(tpslTp2Lb, bar_index)
        if not na(tpslTp3Lb):
            label.set_x(tpslTp3Lb, bar_index)

        if not na(tpslEntryLn):
            line.set_x2(tpslEntryLn, bar_index + 1)
        if not na(tpslSlLn):
            line.set_x2(tpslSlLn, bar_index + 1)
        if not na(tpslTp1Ln):
            line.set_x2(tpslTp1Ln, bar_index + 1)
        if not na(tpslTp2Ln):
            line.set_x2(tpslTp2Ln, bar_index + 1)
        if not na(tpslTp3Ln):
            line.set_x2(tpslTp3Ln, bar_index + 1)
        if not na(tpslExtLn):
            line.set_x2(tpslExtLn, bar_index + 1)

        slHit: bool = low <= tpslSL if tpslDir == 1 else high >= tpslSL
        tpHit: bool = not na(tpslExtreme) and (high >= tpslExtreme if tpslDir == 1 else low <= tpslExtreme)

        if bar_index > tpslEntryBar and (slHit or tpHit):
            if not na(tpslEntryLn):
                line.set_x2(tpslEntryLn, bar_index)
            if not na(tpslSlLn):
                line.set_x2(tpslSlLn, bar_index)
            if not na(tpslTp1Ln):
                line.set_x2(tpslTp1Ln, bar_index)
            if not na(tpslTp2Ln):
                line.set_x2(tpslTp2Ln, bar_index)
            if not na(tpslTp3Ln):
                line.set_x2(tpslTp3Ln, bar_index)
            if not na(tpslExtLn):
                line.set_x2(tpslExtLn, bar_index)
            tpslDir = 0

    plotshape(bearSignal, title='Bearish signal (breakout downward)', style=shape.triangledown, location=location.abovebar, color=colBearSig, size=size.tiny)

    plotshape(bullSignal, title='Bullish signal (breakout upward)', style=shape.triangleup, location=location.belowbar, color=colBullSig, size=size.tiny)

    plot(1 if bullSignal else na, 'bt_buy_score', display=display.none)
    plot(1 if bearSignal else na, 'bt_sell_score', display=display.none)

    alertcondition(bearSignal, title='Downward breakout after upper wick formation', message='Formation {{ticker}} {{interval}}: DOWNWARD breakout, aligned with dominant sell volume — bearish signal')

    alertcondition(bullSignal, title='Upward breakout after lower wick formation', message='Formation {{ticker}} {{interval}}: UPWARD breakout, aligned with dominant buy volume — bullish signal')

    alertcondition(bullSignal or bearSignal, title='Any WSB signal', message='Formation {{ticker}} {{interval}}: WSB signal')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
