"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    array, bar_index, barstate, bgcolor, chart, close, color, dayofmonth,
    display, format, hline, input, location, math, month, na, nz, open, plot, plotcandle, plotchar,
    request, runtime, script, session, string, syminfo, ta, table, time, time_close, timeframe,
    timestamp, volume, year
)
from pynecore.types import Color, Persistent, Series, Table
import lib.PineCoders.Time.v5 as PCtime
import lib.PineCoders.lower_tf.v5 as PCltf
import lib.TradingView.ta.v12 as TVta

GRAY: Color = color.new('#808080')
LIME: Color = color.new('#00FF00')
MAROON: Color = color.new('#800000')
ORANGE: Color = color.new('#FF8000')
PINK: Color = color.new('#FF0080')
TEAL: Color = color.new('#008080')
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
TT_TOTVOL: str = "If enabled and the calculation mode is 'Volume delta', the indicator projects each bar's total volume from the " + "open of each CVD candle for visual comparison.\n\nThe 'Bodies' field specifies the transparency of the total " + 'volume candle bodies. A value of 0 means fully opaque, and 100 means completely transparent.'
TT_LINE: str = "Select to view a line plot displaying the close values of the CVD candles."
TT_LTF: str = 'Controls the number of intrabars that the indicator analyzes per chart bar. ' + 'Increasing the intrabars per chart bar enables more precise calculations. However, it also reduces the number ' + 'of chart bars that the indicator can analyze. ' + 'The first five options determine the requested lower timeframe based on a desired relative amount of chart bar ' + 'coverage. The last five determine the timeframe based on an approximate number of intrabars per chart bar.'
TT_MA: str = "Select to plot an average of the CVD. If the 'CVD resets' input is 'None', the indicator calculates a moving " + "average with the length specified by the 'Length' field. Otherwise, it calculates the cumulative average of the " + 'CVD since the last reset.'
GRP1: str = "Visuals"


@script.indicator("CVD - Cumulative Volume Delta Candles", "CVD Candle", format=format.volume)
def main(
    resetInput=input.string(RST2, "CVD resets", inline="00", options=(RST1, RST2, RST5, RST6, RST3, RST4, RST7), tooltip=TT_RST),
    fixedTfInput=input.timeframe("D", "  Fixed higher timeframe:", tooltip=TT_RST_HTF),
    hourInput=input.int(9, "  Fixed time: Hour", inline="01", minval=0, maxval=23),
    minuteInput=input.int(30, "Minute", inline="01", minval=0, maxval=59, tooltip=TT_RST_TIME),
    trendInput=input.string(TR01, "  Trend: ", inline="02", options=(TR02, TR03, TR01)),
    trendPeriodInput=input.int(14, " Length", inline="02", minval=2),
    trendValue2Input=input.float(3.0, "", inline="02", minval=0.25, step=0.25, tooltip=TT_RST_TREND),
    ltfModeInput=input.string(LTF3, "Intrabar precision", inline="03", options=(LTF1, LTF2, LTF3, LTF4, LTF5, LTF6, LTF7, LTF8, LTF9, LTF10), tooltip=TT_LTF),
    vdCalcModeInput=input.string(VD01, "Volume delta calculation", inline="04", options=(VD01, VD02)),
    showCandlesInput=input.bool(True, "CVD candles", inline="11", group=GRP1),
    upColorInput=input.color(LIME, " 🡑", inline="11", group=GRP1),
    dnColorInput=input.color(PINK, "🡓", inline="11", group=GRP1),
    colorDivBodiesInput=input.bool(True, "Color CVD bodies on divergences ", inline="12", group=GRP1),
    upDivColorInput=input.color(TEAL, "🡑", inline="12", group=GRP1),
    dnDivColorInput=input.color(MAROON, "🡓", inline="12", group=GRP1),
    showTotVolInput=input.bool(False, "Total volume candle borders", inline="13", group=GRP1),
    upTotVolColorInput=input.color(TEAL, "🡑", inline="13", group=GRP1),
    dnTotVolColorInput=input.color(MAROON, "🡓", inline="13", group=GRP1),
    totVolBodyTranspInput=input.int(80, "bodies", inline="13", group=GRP1, minval=0, maxval=100, tooltip=TT_TOTVOL),
    showLineInput=input.bool(False, "CVD line", inline="14", group=GRP1),
    lineUpColorInput=input.color(LIME, " 🡑", inline="14", group=GRP1),
    lineDnColorInput=input.color(PINK, "🡓", inline="14", group=GRP1, tooltip=TT_LINE),
    showMaInput=input.bool(False, "CVD MA", inline="15", group=GRP1),
    maUpColorInput=input.color(TEAL, "  🡑", inline="15", group=GRP1),
    maDnColorInput=input.color(MAROON, "🡓", inline="15", group=GRP1),
    maPeriodInput=input.int(20, " Length", inline="15", group=GRP1, minval=2, tooltip=TT_MA),
    bgDivInput=input.bool(False, "Color background on divergences ", inline="16", group=GRP1),
    bgDivColorInput=input.color(BG_DIV, "", inline="16", group=GRP1),
    bgResetInput=input.bool(True, "Color background on resets ", inline="17", group=GRP1),
    bgResetColorInput=input.color(BG_RESETS, "", inline="17", group=GRP1),
    showZeroLineInput=input.bool(True, "Zero line", inline="18", group=GRP1),
    showInfoBoxInput=input.bool(True, "Show information box ", group=GRP1),
    infoBoxSizeInput=input.string("small", "Size ", inline="19", group=GRP1, options=("tiny", "small", "normal", "large", "huge", "auto")),
    infoBoxYPosInput=input.string("bottom", "↕", inline="19", group=GRP1, options=("top", "middle", "bottom")),
    infoBoxXPosInput=input.string("right", "↔", inline="19", group=GRP1, options=("left", "center", "right")),
    infoBoxColorInput=input.color(color.gray, "", inline="19", group=GRP1),
    infoBoxTxtColorInput=input.color(color.white, "T", inline="19", group=GRP1)
):
    MS_IN_MIN: int = 60 * 1000
    MS_IN_HOUR: int = MS_IN_MIN * 60
    MS_IN_DAY: int = MS_IN_HOUR * 24





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

    ltfString: Persistent[str] = PCltf.ltf(ltfModeInput, LTF1, LTF2, LTF3, LTF4, LTF5, LTF6, LTF7, LTF8, LTF9, LTF10)

    upVolumes, dnVolumes = request.security_lower_tf(syminfo.tickerid, ltfString, upDnIntrabarVolumes(), calc_bars_count=200000)

    totalUpVolume: float = nz(method_call('sum', upVolumes))
    totalDnVolume: float = nz(method_call('sum', dnVolumes))
    maxUpVolume: float = nz(method_call('max', upVolumes))
    maxDnVolume: float = nz(method_call('min', dnVolumes))
    totalVolume: float = totalUpVolume - totalDnVolume
    delta: float = totalUpVolume + totalDnVolume
    deltaPct: float = delta / totalVolume
    isDelta: bool = vdCalcModeInput == VD01
    barDelta: float = delta if isDelta else deltaPct

    cvd: Persistent[float] = 0.0
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
        __block_result_1__ = (time == chart.left_visible_bar_time, False, False, "Resets at the beginning of visible bars")
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

    if reset:
        cvd = 0

    cvdO: float = cvd
    cvdC: float = cvdO + barDelta
    cvdH: float = math.max(cvdO, cvdC) if not isDelta else cvdO + maxUpVolume
    cvdL: float = math.min(cvdO, cvdC) if not isDelta else cvdO + maxDnVolume
    cvd += barDelta

    ma: Persistent[float] = cvd
    cvdValues: Persistent[list[float]] = array.new_float()
    if resetInput == RST1:
        ma = ta.sma(cvdC, maPeriodInput)
    else:
        if reset:
            array.clear(cvdValues)
            array.push(cvdValues, cvd)
        else:
            array.push(cvdValues, cvd)
        ma = array.avg(cvdValues)

    totalVolumeLevel: float = cvdO + totalVolume * math.sign(barDelta)
    __block_result_3__ = (na, na, na, na)
    if showTotVolInput and isDelta:
        __block_result_3__ = (cvdO, math.max(cvdO, totalVolumeLevel), math.min(cvdO, totalVolumeLevel), totalVolumeLevel)
    else:
        __block_result_3__ = (na, na, na, na)
    totalVolO, totalVolH, totalVolL, totalVolC = __block_result_3__

    intrabars, chartBarsCovered, avgIntrabars = PCltf.ltfStats(upVolumes)
    chartBars: int = bar_index + 1

    divergence: bool = delta != 0 and math.sign(delta) != math.sign(close - open)

    candleColor: Color = (upDivColorInput if colorDivBodiesInput and divergence else upColorInput) if delta > 0 else dnDivColorInput if colorDivBodiesInput and divergence else dnColorInput
    totVolCandleColor: Color = upTotVolColorInput if delta > 0 else dnTotVolColorInput

    displayLocation = display.data_window
    plot(delta, 'Volume delta for the bar', candleColor, display=displayLocation)
    plot(totalUpVolume, 'Up volume for the bar', upColorInput, display=displayLocation)
    plot(totalDnVolume, 'Dn volume for the bar', dnColorInput, display=displayLocation)
    plot(totalVolume, 'Total volume', display=displayLocation)
    plot(na, '═════════════════', display=displayLocation)
    plot(cvdO, 'CVD before this bar', display=displayLocation)
    plot(cvdC, 'CVD after this bar', display=displayLocation)
    plot(maxUpVolume, 'Max intrabar up volume', upColorInput, display=displayLocation)
    plot(maxDnVolume, 'Max intrabar dn volume', dnColorInput, display=displayLocation)
    plot(intrabars, 'Intrabars in this bar', display=displayLocation)
    plot(avgIntrabars, 'Average intrabars', display=displayLocation)
    plot(chartBarsCovered, 'Chart bars covered', display=displayLocation)
    plot(bar_index + 1, 'Chart bars', display=displayLocation)
    plot(na, '═════════════════', display=displayLocation)

    plotcandle(totalVolO, totalVolH, totalVolL, totalVolC, 'CVD', color=color.new(totVolCandleColor, totVolBodyTranspInput), wickcolor=totVolCandleColor, bordercolor=totVolCandleColor)

    plotcandle(cvdO if showCandlesInput else na, cvdH, cvdL, cvdC, 'CVD', color=candleColor, wickcolor=candleColor, bordercolor=candleColor)

    plot(cvdC if showLineInput else na, 'CVD line', lineUpColorInput if cvdC > 0 else lineDnColorInput)
    plot(ma if showMaInput else na, 'CVD MA', na if reset else maUpColorInput if ma > 0 else maDnColorInput)

    hline(0 if showZeroLineInput else na, 'Zero', GRAY, hline.style_dotted)

    plotchar(hasTrendDirection and reset and trendIsUp, 'Up trend', '▲', location.top, upColorInput)
    plotchar(hasTrendDirection and reset and (not trendIsUp), 'Dn trend', '▼', location.top, dnColorInput)

    bgcolor(bgResetColorInput if bgResetInput and reset else bgDivColorInput if bgDivInput and divergence else na)

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
        runtime.error('Resets at a fixed time of day work on intraday charts only.')
    elif ta.cum(totalVolume) == 0 and barstate.islast:
        runtime.error('No volume is provided by the data vendor.')
    elif ta.cum(intrabars) == 0 and barstate.islast:
        runtime.error("No intrabar information is available for the '" + ltfString + "' timeframe.")


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)