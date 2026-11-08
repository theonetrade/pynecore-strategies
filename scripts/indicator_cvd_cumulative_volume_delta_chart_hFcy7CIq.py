"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_import import shadowed_namespace
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    array, bar_index, barcolor, barstate, bgcolor, box, chart, close, color,
    dayofmonth, display, format, high, hl2, input, label, line, location, low, math, month, na, nz,
    open, plot, plotchar, request, runtime, script, session, size, string, syminfo, ta, table,
    time, time_close, timeframe, timestamp, volume, year
)
from pynecore.types import Color, NA, Persistent, Series, Table
import lib.PineCoders.Time.v5 as PCtime
import lib.PineCoders.VisibleChart.v5 as chart__ren____lib
import lib.PineCoders.lower_tf.v5 as PCltf
import lib.TradingView.ta.v12 as TVta


chart__ren__ = shadowed_namespace(chart__ren____lib, chart)

LIME: Color = color.lime
PINK: Color = color.fuchsia
WHITE: Color = color.white
ORANGE: Color = color.orange
GRAY: Color = color.new('#808080')
LIME_LINE: Color = color.new(LIME, 30)
LIME_BG: Color = color.new(LIME, 95)
LIME_HI: Color = color.new(LIME, 80)
PINK_LINE: Color = color.new(PINK, 30)
PINK_BG: Color = color.new(PINK, 95)
PINK_LO: Color = color.new(PINK, 80)
BG_DIV: Color = color.new(ORANGE, 90)
BG_RESETS: Color = color.new(GRAY, 90)
RST1: str = "None"
RST2: str = "On a stepped higher timeframe"
RST3: str = "On a fixed higher timeframe..."
RST4: str = "At a fixed time..."
RST5: str = "At the beginning of the regular session"
RST6: str = "At the first visible chart bar"
RST7: str = "On trend changes..."
TR01: str = "Supertrend"
TR02: str = "Aroon"
TR03: str = "Parabolic SAR"
VD01: str = "Volume delta"
VD02: str = "Volume delta percent"
LN01: str = "Line"
LN02: str = "Histogram"
LS01: str = "tiny"
LS02: str = "small"
LS03: str = "normal"
LS04: str = "large"
LS05: str = "huge"
LTF1: str = "Covering most chart bars (least precise)"
LTF2: str = "Covering some chart bars (less precise)"
LTF3: str = "Covering less chart bars (more precise)"
LTF4: str = "Covering few chart bars (very precise)"
LTF5: str = "Covering the least chart bars (most precise)"
LTF6: str = "~12 intrabars per chart bar"
LTF7: str = "~24 intrabars per chart bar"
LTF8: str = "~50 intrabars per chart bar"
LTF9: str = "~100 intrabars per chart bar"
LTF10: str = "~250 intrabars per chart bar"
TT_RST: str = 'Specifies the reset behavior of the CVD calculation. When selecting one of the last three options, use the ' + 'inputs below to specify additional settings for the reset conditions.'
TT_RST_HTF: str = "Specifies the higher timeframe to use for the 'On a fixed higher timeframe' CVD reset option. " + 'The CVD calculation resets at the open of a bar on the specified timeframe.'
TT_RST_TIME: str = "Hour: 0-23\nMinute: 0-59\nThese values specify the fixed time of day to use for the 'At a fixed time' CVD reset " + "option. The CVD calculation resets when the time of day is after or equal to the bar's opening time and " + "before the bar's closing time."
TT_RST_TREND: str = "These values control the settings of the trend indicator to use for the 'On trend changes' CVD reset option. " + 'The CVD calculation resets when the indicator signals a change in trend direction.\n\n' + 'The first field specifies the length for the Aroon indicator or the ATR length for the Supertrend indicator.\n\n' + 'The second field specifies the ATR multiplier for the Supertrend indicator.\n\n' + 'The Parabolic SAR uses predefined settings. Neither field affects it.'
TT_LINE: str = "Select the style and color of the CVD lines."
TT_LTF: str = 'Controls the number of intrabars that the indicator analyzes per chart bar. ' + 'Increasing the intrabars per chart bar enables more precise calculations. However, it also reduces the number ' + 'of chart bars that the indicator can analyze. ' + 'The first five options determine the requested lower timeframe based on a desired relative amount of chart bar ' + 'coverage. The last five determine the timeframe based on an approximate number of intrabars per chart bar.'
TT_CVD: str = 'If enabled, the indicator displays cumulative delta values summed from the reset point. ' + 'Otherwise, it displays the raw volume delta for each bar.'
TT_YSPCE: str = "Scales the height of all oscillator zones using a percentage of the largest zone's height."
GRP1: str = "Visuals"


@script.indicator("CVD - Cumulative Volume Delta (Chart)", "CVD Chart", True, format=format.volume, max_lines_count=500, max_labels_count=500, max_boxes_count=500)
def main(
    resetInput=input.string(RST2, "CVD resets", inline="00", options=(RST1, RST2, RST5, RST6, RST3, RST4, RST7), tooltip=TT_RST),
    fixedTfInput=input.timeframe("D", "  Fixed higher timeframe:", inline="01", tooltip=TT_RST_HTF),
    hourInput=input.int(9, "  Fixed time: Hour", inline="02", minval=0, maxval=23),
    minuteInput=input.int(30, "Minute", inline="02", minval=0, maxval=59, tooltip=TT_RST_TIME),
    trendInput=input.string(TR01, "  Trend: ", inline="03", options=(TR02, TR03, TR01)),
    trendPeriodInput=input.int(14, " Length", inline="03", minval=2),
    trendValue2Input=input.float(3.0, "", inline="03", minval=0.25, step=0.25, tooltip=TT_RST_TREND),
    ltfModeInput=input.string(LTF3, "Intrabar precision", inline="04", options=(LTF1, LTF2, LTF3, LTF4, LTF5, LTF6, LTF7, LTF8, LTF9, LTF10), tooltip=TT_LTF),
    vdCalcModeInput=input.string(VD01, "Volume delta calculation", inline="05", options=(VD01, VD02)),
    cumulativeInput=input.bool(True, "Cumulative values", inline="06", tooltip=TT_CVD),
    lineTypeInput=input.string(LN01, "CVD", inline="00", group=GRP1, options=(LN01, LN02)),
    upColorInput=input.color(LIME_LINE, "🡓", inline="01", group=GRP1),
    dnColorInput=input.color(PINK_LINE, "🡓", inline="01", group=GRP1, tooltip=TT_LINE),
    __input_13__=input.float(100, "Zone height (%)", inline="02", group=GRP1, tooltip=TT_YSPCE),
    showBgAreaInput=input.bool(True, "  Color background area ", inline="05", group=GRP1),
    upBgColorInput=input.color(LIME_BG, "🡑", inline="05", group=GRP1),
    dnBgColorInput=input.color(PINK_BG, "🡓", inline="05", group=GRP1),
    showHiLoInput=input.bool(True, "  Hi/Lo lines ", inline="06", group=GRP1),
    hiColorInput=input.color(LIME_HI, "🡑", inline="06", group=GRP1),
    loColorInput=input.color(PINK_LO, "🡓", inline="06", group=GRP1),
    showZeroLineInput=input.bool(True, "  Zero line", inline="07", group=GRP1),
    zeroLineColorInput=input.color(GRAY, "🡓", inline="07", group=GRP1),
    labelInput=input.bool(True, "Hi/Lo labels", inline="03", group=GRP1),
    labelSizeInput=input.string(LS03, "", inline="03", group=GRP1, options=(LS01, LS02, LS03, LS04, LS05)),
    tooltipInput=input.bool(True, "Value tooltips", inline="04", group=GRP1),
    colorDivBodiesInput=input.bool(True, "Color bars on divergences ", inline="08", group=GRP1),
    upDivColorInput=input.color(LIME, "🡑", inline="08", group=GRP1),
    dnDivColorInput=input.color(PINK, "🡓", inline="08", group=GRP1),
    bgDivInput=input.bool(False, "Color background on divergences ", inline="09", group=GRP1),
    bgDivColorInput=input.color(BG_DIV, "", inline="09", group=GRP1),
    bgResetInput=input.bool(True, "Color background on resets ", inline="10", group=GRP1),
    bgResetColorInput=input.color(BG_RESETS, "", inline="10", group=GRP1),
    showInfoBoxInput=input.bool(True, "Show information box ", inline="11", group=GRP1),
    infoBoxSizeInput=input.string("small", "Size ", inline="12", group=GRP1, options=("tiny", "small", "normal", "large", "huge", "auto")),
    infoBoxYPosInput=input.string("bottom", "↕", inline="12", group=GRP1, options=("top", "middle", "bottom")),
    infoBoxXPosInput=input.string("right", "↔", inline="12", group=GRP1, options=("left", "center", "right")),
    infoBoxColorInput=input.color(GRAY, "", inline="12", group=GRP1),
    infoBoxTxtColorInput=input.color(WHITE, "T", inline="12", group=GRP1)
):
    MS_IN_MIN: int = 60 * 1000
    MS_IN_HOUR: int = MS_IN_MIN * 60
    MS_IN_DAY: int = MS_IN_HOUR * 24
    LBL_TXT: str = " \n \n \n \n \n \n \n \n \n "






    percentYRangeInput: float = __input_13__ / 100.0

    def upDnIntrabarVolumes():
        upVol: Series[float] = 0.0
        dnVol: Series[float] = 0.0
        if close > open:
            upVol += volume
        elif close < open:
            dnVol -= volume
        elif close > close[1]:
            upVol += volume
        elif close < close[1]:
            dnVol -= volume
        elif upVol[1] > 0:
            upVol += volume
        elif dnVol[1] < 0:
            dnVol -= volume
        elif close == open:
            upVol += volume
        return (upVol, dnVol)

    def htfStep():
        tfInMs: int = timeframe.in_seconds() * 1000
        __block_result__ = na
        if tfInMs <= MS_IN_MIN:
            __block_result__ = "60"
        elif tfInMs < MS_IN_HOUR * 3:
            __block_result__ = "1D"
        elif tfInMs <= MS_IN_HOUR * 12:
            __block_result__ = "1W"
        elif tfInMs < MS_IN_DAY * 7:
            __block_result__ = "1M"
        else:
            __block_result__ = "12M"
        return __block_result__

    def timeReset(hours: int, minutes: int):
        openTime: int = timestamp(year, month, dayofmonth, hours, minutes, 0)
        timeInBar: Series[bool] = time <= openTime and time_close > openTime
        return timeframe.isintraday and (not timeInBar[1]) and timeInBar

    def scale__global__(oldValue: Series[float], oldMin: Series[float], oldMax: Series[float], newMin: Series[float], newMax: Series[float]):
        oldRange: float = oldMax - oldMin
        newRange: float = newMax - newMin
        return (oldValue - oldMin) * newRange / oldRange + newMin

    def scaleHistoWidth(bars: Series[int], maxWidth: int, decayLength: int, offset: int):
        return math.ceil(2 * maxWidth / (1 + math.exp(6 * (bars - offset) / decayLength)))

    ltfString: Persistent[str] = PCltf.ltf(ltfModeInput, LTF1, LTF2, LTF3, LTF4, LTF5, LTF6, LTF7, LTF8, LTF9, LTF10)

    upVolumes, dnVolumes = request.security_lower_tf(syminfo.tickerid, ltfString, upDnIntrabarVolumes(), calc_bars_count=200000)

    useVdPct: bool = vdCalcModeInput == VD02
    useHisto: bool = lineTypeInput == LN02

    leftBar: int = chart__ren__.leftBarIndex()
    rightBar: int = chart__ren__.rightBarIndex()
    isVisible: bool = chart__ren__.barIsVisible()
    isLastBar: bool = chart__ren__.isLastVisibleBar()
    totalBars: int = chart__ren__.bars()

    lineWidth: int = scaleHistoWidth(totalBars, 29, 391, -63)

    totalUpVolume: float = nz(method_call('sum', upVolumes))
    totalDnVolume: float = nz(method_call('sum', dnVolumes))
    maxUpVolume: float = nz(method_call('max', upVolumes))
    maxDnVolume: float = nz(method_call('min', dnVolumes))
    totalVolume: float = totalUpVolume - totalDnVolume
    delta: float = totalUpVolume + totalDnVolume
    deltaPct: float = delta / totalVolume
    barDelta: float = deltaPct if useVdPct else delta

    __block_result_1__ = (na, na, na, na)
    __switch__ = resetInput
    if __switch__ == RST1:
        __block_result_1__ = (False, False, False, "No resets")
    elif __switch__ == RST2:
        __block_result_1__ = (timeframe.change(htfStep()), False, False, 'Resets every ' + htfStep())
    elif __switch__ == RST3:
        __block_result_1__ = (timeframe.change(fixedTfInput), False, False, 'Resets every ' + fixedTfInput)
    elif __switch__ == RST4:
        __block_result_1__ = (timeReset(hourInput, minuteInput), False, False, string.format('Resets at {0,number,00}:{1,number,00}', hourInput, minuteInput))
    elif __switch__ == RST5:
        __block_result_1__ = (session.isfirstbar_regular, False, False, "Resets at the beginning of the session")
    elif __switch__ == RST6:
        __block_result_1__ = (time == chart__ren__.left_visible_bar_time, False, False, "Resets at the beginning of visible bars")
    elif __switch__ == RST7:
        __block_result_2__ = (na, na, na, na)
        __switch_1__ = trendInput
        if __switch_1__ == TR01:
            _, direction = ta.supertrend(trendValue2Input, trendPeriodInput)
            __block_result_2__ = (ta.change(direction, 1) != 0, True, direction == -1, "Resets on Supertrend changes")
        elif __switch_1__ == TR02:
            up, dn = TVta.aroon(trendPeriodInput)
            __block_result_2__ = (ta.cross(up, dn), True, ta.crossover(up, dn), "Resets on Aroon changes")
        elif __switch_1__ == TR03:
            psar: float = ta.sar(0.02, 0.02, 0.2)
            __block_result_2__ = (ta.cross(psar, close), True, ta.crossunder(psar, close), "Resets on PSAR changes")
        __block_result_1__ = __block_result_2__
    else:
        __block_result_1__ = (False, False, False, na)
    reset, hasTrendDirection, trendIsUp, resetDescription = __block_result_1__

    intrabars: int = method_call('size', upVolumes)
    chartBarsCovered: int = cast_int(ta.cum(math.sign(intrabars)))
    avgIntrabars: float = ta.cum(intrabars) / chartBarsCovered

    divergence: bool = delta != 0 and math.sign(delta) != math.sign(close - open)

    segCvdValues: Persistent[list[float]] = array.new_float()
    rawCvdValues: Persistent[list[float]] = array.new_float()
    barCenters: Persistent[list[float]] = array.new_float()
    zeroLevels: Persistent[list[float]] = array.new_float()
    priceRanges: Persistent[list[float]] = array.new_float()
    highCvd: Persistent[list[float]] = array.new_float()
    lowCvd: Persistent[list[float]] = array.new_float()
    resetBars: Persistent[list[int]] = array.new_int()
    priceHi: Persistent[float] = high
    priceLo: Persistent[float] = low
    cvd: Persistent[float] = 0.0
    priceHi = math.max(priceHi, high) if isVisible else high
    priceLo = math.min(priceLo, low) if isVisible else low

    if reset or isLastBar:
        if isVisible:
            array.push(segCvdValues, cvd + barDelta if cumulativeInput else barDelta)
            array.push(resetBars, bar_index)
            array.push(zeroLevels, math.avg(priceHi, priceLo) - (priceHi - priceLo))
            array.push(priceRanges, (priceHi - priceLo) / 2)
            array.push(highCvd, array.max(segCvdValues))
            array.push(lowCvd, array.min(segCvdValues))
            array.push(barCenters, hl2)
            array.concat(rawCvdValues, segCvdValues)
            array.clear(segCvdValues)
        priceHi = high
        priceLo = low
        cvd = 0 if reset else cvd

    cvdO: float = cvd
    cvd += barDelta

    if isLastBar:
        startBar: int = leftBar
        step: int = 0
        yRangeMax: float = array.max(priceRanges) * percentYRangeInput
        highScale: float = 1 if useVdPct and (not cumulativeInput) else array.max(array.abs(rawCvdValues))

        for i, resetBar in enumerate(resetBars):
            zero: float = array.get(zeroLevels, i)
            yRange: float = array.get(priceRanges, i)
            highValue: float = array.get(highCvd, i)
            lowValue: float = array.get(lowCvd, i)
            highLevel: float = scale__global__(highValue, 0, highScale, zero, zero + yRangeMax)
            offset: float = zero + yRange - (math.max(highLevel, zero) if useHisto else highLevel)
            zeroLevel: float = zero + offset
            hiLevel: float = zeroLevel + yRangeMax
            loLevel: float = zeroLevel - yRangeMax

            if showZeroLineInput:
                line.new(startBar, zeroLevel, resetBar, zeroLevel, color=zeroLineColorInput, style=line.style_dashed)
            if showHiLoInput:
                line.new(startBar, hiLevel, resetBar, hiLevel, color=hiColorInput)
                line.new(startBar, loLevel, resetBar, loLevel, color=loColorInput)
            if showBgAreaInput:
                box.new(startBar, hiLevel, resetBar, zeroLevel, border_color=NA(Color), bgcolor=upBgColorInput)
                box.new(startBar, loLevel, resetBar, zeroLevel, border_color=NA(Color), bgcolor=dnBgColorInput)

            bar: int = startBar
            lastPriceValue: float = na(float)
            placeHigh: bool = True
            placeLow: bool = True

            for x in pine_range(step, resetBar - startBar + step):
                cvdValue: float = array.get(rawCvdValues, x)
                eachCvd: float = cvdValue if cvdValue != 0 else na
                priceLvl: float = scale__global__(eachCvd, 0, highScale, zero, zero + yRangeMax) + offset
                lineColor: Color = upColorInput if priceLvl > zeroLevel else dnColorInput
                labelStr: str = (string.format('{0, number, percent}', eachCvd) if useVdPct else string.tostring(eachCvd, format.volume)) if labelInput else NA(str)
                isHiCvd: bool = eachCvd == highValue
                isLoCvd: bool = eachCvd == lowValue

                if labelInput and (isHiCvd or isLoCvd):
                    drawHiLbl: bool = isHiCvd and placeHigh and (bar != leftBar)
                    drawLoLbl: bool = isLoCvd and placeLow and (bar != leftBar)
                    labelStyle: str = label.style_label_down if isHiCvd else label.style_label_up
                    labelPrice: float = (zeroLevel if highValue < 0 and isHiCvd or (lowValue > 0 and isLoCvd) else priceLvl) if useHisto else priceLvl
                    if drawHiLbl or drawLoLbl:
                        label.new(bar, labelPrice, labelStr, color=NA(Color), style=labelStyle, textcolor=lineColor, size=labelSizeInput)
                        placeHigh = False if drawHiLbl else placeHigh
                        placeLow = False if drawLoLbl else placeLow

                if tooltipInput:
                    label.new(bar, array.get(barCenters, x), LBL_TXT, color=NA(Color), size=size.tiny, style=label.style_label_center, tooltip=labelStr)

                if useHisto:
                    line.new(bar, zeroLevel, bar, priceLvl, color=lineColor, width=lineWidth)
                elif bar > startBar:
                    line.new(bar - 1, lastPriceValue, bar, priceLvl, color=lineColor, width=2)

                bar += 1
                lastPriceValue = priceLvl

            step += resetBar - startBar + 1
            startBar = resetBar

    if isVisible:
        array.push(segCvdValues, cvd if cumulativeInput else barDelta)
        array.push(barCenters, hl2)

    candleColor: Color = (upDivColorInput if delta > 0 else dnDivColorInput) if colorDivBodiesInput and divergence else na

    displayDataWindow = display.data_window
    plot(delta, 'Volume delta for the bar', candleColor, display=displayDataWindow)
    plot(totalUpVolume, 'Up volume for the bar', upColorInput, display=displayDataWindow)
    plot(totalDnVolume, 'Dn volume for the bar', dnColorInput, display=displayDataWindow)
    plot(totalVolume, 'Total volume', display=displayDataWindow)
    plot(na, '═════════════════', display=displayDataWindow)
    plot(cvdO, 'CVD before this bar', display=displayDataWindow)
    plot(cvd, 'CVD after this bar', display=displayDataWindow)
    plot(maxUpVolume, 'Max intrabar up volume', upColorInput, display=displayDataWindow)
    plot(maxDnVolume, 'Max intrabar dn volume', dnColorInput, display=displayDataWindow)
    plot(intrabars, 'Intrabars in this bar', display=displayDataWindow)
    plot(avgIntrabars, 'Average intrabars', display=displayDataWindow)
    plot(chartBarsCovered, 'Chart bars covered', display=displayDataWindow)
    plot(bar_index + 1, 'Chart bars', display=displayDataWindow)
    plot(na, '═════════════════', display=displayDataWindow)
    plot(totalBars, 'Total visible bars', display=displayDataWindow)
    plot(leftBar, 'First visible bar index', display=displayDataWindow)
    plot(rightBar, 'Last visible bar index', display=displayDataWindow)
    plot(na, '═════════════════', display=displayDataWindow)

    plotchar(hasTrendDirection and reset and trendIsUp, 'Up trend', '▲', location.top, upColorInput)
    plotchar(hasTrendDirection and reset and (not trendIsUp), 'Dn trend', '▼', location.top, dnColorInput)

    bgcolor(bgResetColorInput if bgResetInput and reset else bgDivColorInput if bgDivInput and divergence else na)
    barcolor(candleColor)

    if showInfoBoxInput and barstate.islastconfirmedhistory:
        infoBox: Persistent[Table] = table.new(infoBoxYPosInput + '_' + infoBoxXPosInput, 1, 1)
        infoBoxBgColor: Color = infoBoxColorInput
        txt: str = string.format('{0}\nUses intrabars at {1}\nAvg intrabars per chart bar: {2,number,#.##}\n' + 'Chart bars covered: {3}\u200a/\u200a{4} ({5,number,percent})', resetDescription, PCtime.formattedNoOfPeriods(timeframe.in_seconds(ltfString) * 1000), avgIntrabars, chartBarsCovered, bar_index + 1, chartBarsCovered / (bar_index + 1))
        if avgIntrabars < 5:
            txt += "\nThis quantity of intrabars is dangerously small.\nResults will not be as reliable with so few."
            infoBoxBgColor = color.red
        table.cell(infoBox, 0, 0, txt, text_color=infoBoxTxtColorInput, text_size=infoBoxSizeInput, bgcolor=infoBoxBgColor)

    if resetInput == RST3 and timeframe.in_seconds(fixedTfInput) <= timeframe.in_seconds():
        runtime.error("The higher timeframe for resets must be greater than the chart's timeframe.")
    elif resetInput == RST4 and (not timeframe.isintraday):
        runtime.error('Resets at a fixed time work on intraday charts only.')
    elif resetInput == RST5 and (not timeframe.isintraday):
        runtime.error('Resets at the begining of session work on intraday charts only.')
    elif ta.cum(totalVolume) == 0 and barstate.islast:
        runtime.error('No volume is provided by the data vendor.')
    elif ta.cum(intrabars) == 0 and barstate.islast:
        runtime.error("No intrabar information exists at the '" + ltfString + "' timeframe.")


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)