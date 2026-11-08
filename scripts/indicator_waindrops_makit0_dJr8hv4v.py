"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    array, bar_index, barstate, close, color, high, hlc3, input, label, line,
    low, math, na, plot, script, size, string, syminfo, ta, text, time, timeframe, timenow, volume,
    xloc, yloc
)
from pynecore.types import Label, Line, Persistent, Series

BARS: str = 'BARS'
HISTOGRAM: str = 'HISTOGRAM'
ONE: str = 'ONE'
TWO: str = 'TWO'
FOUR: str = 'FOUR'
EACHBAR: str = 'EACH BAR'
AUTO: str = 'AUTO'
TINY: str = 'TINY'
SMALL: str = 'SMALL'
NORMAL: str = 'NORMAL'
LARGE: str = 'LARGE'


@script.indicator('Waindrops_v0.67beta', shorttitle='WD_v067b', overlay=True, max_lines_count=500, max_labels_count=500, na_bool=True)
def main(
    i_showHelp=input(False, 'Click here or set any impar period to see the HELP INFO'),
    i_period=input.int(60, 'PERIOD SIZE (max 2880 min)', minval=2, maxval=2880),
    i_showBars=input(True, 'BARS'),
    i_showCentralBars=input(True, 'Central bars'),
    i_showVWAPBars=input(True, 'VWAP bars'),
    i_barPixels=input.int(2, '  Bars pixels', minval=1),
    i_barsColorMode=input.string(BARS, '  Bars color mode', options=(BARS, HISTOGRAM)),
    i_barsColor=input(color.white, '  Bars color'),
    i_showHistogram=input(True, 'HISTOGRAM'),
    i_histogramPeriods=input.int(5, '  Execution window (x24H)', minval=1),
    i_histogramGranularity=input.int(2, '  Ticks per bar (max 50)', minval=1, maxval=50),
    i_histogramUpdateMode=input.string(EACHBAR, '  Updates per period', options=(ONE, TWO, FOUR, EACHBAR)),
    i_histogramPixels=input.int(4, '  Pixels per bar', minval=1),
    i_histogramNeutralTreshold=input.int(0, '  Neutral treshold (ticks)', minval=0),
    i_histogramBearColor=input(color.new(color.red, 50), '  Bearish Histogram color'),
    i_histogramBullColor=input(color.new(color.green, 50), '  Bullish histogram color'),
    i_histogramNeutralColor=input(color.new(color.blue, 50), '  Neutral histogram color'),
    i_showVolumeInfo=input(True, 'VOLUME LABELS'),
    i_volumeLabelsColor=input(color.new(color.white, 50), '  Volume labels color'),
    i_volumeLabelsSize=input.string(TINY, '  Volume labels size', options=(AUTO, TINY, SMALL, NORMAL, LARGE)),
    i_trackPrice=input(True, 'TRACK PRICE')
):
    _mintick: Persistent = syminfo.mintick
    def f_round_tick(price):
        return math.round(price / _mintick) * _mintick

    def f_delta_tick(price1, price2):
        return price1 / _mintick - price2 / _mintick

    def f_ticksInRange(rangeHigh, rangeLow):
        return rangeHigh / _mintick - rangeLow / _mintick + 1

    def f_line_new(timeX1, y1, timeX2, y2):
        return line.new(timeX1, y1, timeX2, y2, xloc=xloc.bar_time, width=i_barPixels)

    def f_line_set_y1y2(id, y1, y2):
        line.set_y1(id, y1)
        return line.set_y2(id, y2)

    def f_line_set_y(id, y):
        return f_line_set_y1y2(id, y, y)

    def f_line_set_color(l_1, l_2, l_3, lineColor):
        line.set_color(l_1, lineColor)
        line.set_color(l_2, lineColor)
        return line.set_color(l_3, lineColor)

    def f_void():
        return line.delete(na)

    def f_printHelp(_txt):
        _lbl: Persistent = label.new(bar_index, ta.highest(200), _txt, xloc.bar_index, yloc.price, color.new('#00000000'), label.style_label_right, i_barsColor, size.large, text.align_left)
        label.set_xy(_lbl, bar_index, 0.5 * (ta.highest(300) + ta.lowest(300)))
        return label.set_text(_lbl, _txt)

    def f_label_new(timex, y, text_1, style, size__ren__, align):
        return label.new(timex, y, text_1, xloc=xloc.bar_time, color=color.new(color.white, 100), style=style, textcolor=i_volumeLabelsColor, size=size__ren__, textalign=align)

    def f_label_set_y(label1, label2, label3, y):
        label.set_y(label1, y)
        label.set_y(label2, y)
        return label.set_y(label3, y)

    _timeframe_multiplier: Persistent = timeframe.multiplier
    msByPeriodUnit: Persistent = 1000 * 60 * _timeframe_multiplier
    def f_getTimePointInPeriod(_startTime, _unitsIncrement):
        return _startTime + _unitsIncrement / _timeframe_multiplier * msByPeriodUnit

    def f_clearArrays(a_1, a_2, a_3, a_4, a_5, a_6):
        array.clear(a_1)
        array.clear(a_2)
        array.clear(a_3)
        array.clear(a_4)
        array.clear(a_5)
        return array.clear(a_6)

    def f_array_indexof(a_base, value):
        _init: int = 0
        _end = array.size(a_base) - 1
        output = -1
        for i in pine_range(_init, _end, 1):
            if _end < 0 or output != -1:
                break
            if array.get(a_base, i) == value:
                output = i
        return output

    def f_populate_array(a_lvl, a_vol):
        _high = high
        _low = low
        rangeTicks = f_ticksInRange(_high, _low)
        volumeByTick = volume / rangeTicks
        __block_result__ = na
        for level in pine_range(_low, _high, _mintick):
            index = f_array_indexof(a_lvl, level)
            __block_result_1__ = na
            if index < 0:
                array.push(a_lvl, level)
                __block_result_1__ = array.push(a_vol, volumeByTick)
            else:
                updatedVol = array.get(a_vol, index) + volumeByTick
                __block_result_1__ = array.set(a_vol, index, updatedVol)
            __block_result__ = __block_result_1__
        return __block_result__

    def f_volumeByLevel(a_lvl, a_vol, level):
        index = f_array_indexof(a_lvl, level)
        return array.get(a_vol, index) if index != -1 else 0

    def f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level, count):
        output: float = 0.0
        output = output + f_volumeByLevel(a_lvl, a_vol, level) if count >= 1 else output
        output = output + f_volumeByLevel(a_lvl, a_vol, level + _mintick) if count >= 2 else output
        output = output + f_volumeByLevel(a_lvl, a_vol, level + 2 * _mintick) if count >= 3 else output
        output = output + f_volumeByLevel(a_lvl, a_vol, level + 3 * _mintick) if count >= 4 else output
        output = output + f_volumeByLevel(a_lvl, a_vol, level + 4 * _mintick) if count >= 5 else output
        return output

    def f_volumeByMultiLevel_NOLOOP(a_lvl, a_vol, level, count):
        output: float = 0.0
        __block_result_2__ = na
        if count <= 5:
            output = f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level, count)
            __block_result_2__ = output
        elif count <= 10:
            output = f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 5 * _mintick, count - 5)
            __block_result_2__ = output
        elif count <= 15:
            output = f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 5 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 10 * _mintick, count - 10)
            __block_result_2__ = output
        elif count <= 20:
            output = f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 5 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 10 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 15 * _mintick, count - 15)
            __block_result_2__ = output
        elif count <= 25:
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 5 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 10 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 15 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 20 * _mintick, count - 20)
            __block_result_2__ = output
        elif count <= 30:
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 5 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 10 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 15 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 20 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 25 * _mintick, count - 25)
            __block_result_2__ = output
        elif count <= 35:
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 5 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 10 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 15 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 20 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 25 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 30 * _mintick, count - 30)
            __block_result_2__ = output
        elif count <= 40:
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 5 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 10 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 15 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 20 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 25 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 30 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 35 * _mintick, count - 35)
            __block_result_2__ = output
        elif count <= 45:
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 5 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 10 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 15 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 20 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 25 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 30 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 35 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 40 * _mintick, count - 40)
            __block_result_2__ = output
        elif count <= 50:
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 5 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 10 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 15 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 20 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 25 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 30 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 35 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 40 * _mintick, count)
            output = output + f_volumeBy5Levels_NOLOOP(a_lvl, a_vol, level + 45 * _mintick, count - 45)
            __block_result_2__ = output
        return __block_result_2__

    def f_deleteHistogram(a_histogram):
        _end = array.size(a_histogram)
        __block_result_3__ = na
        if _end > 0:
            __block_result_4__ = na
            for i in pine_range(0, _end - 1, 1):
                __block_result_4__ = line.delete(array.shift(a_histogram))
            __block_result_3__ = __block_result_4__
        return __block_result_3__

    def f_deleteVolumeLabels(a_volumeLabels):
        _end = array.size(a_volumeLabels)
        __block_result_5__ = na
        if _end > 0:
            __block_result_6__ = na
            for i in pine_range(0, _end - 1, 1):
                __block_result_6__ = label.delete(array.shift(a_volumeLabels))
            __block_result_5__ = __block_result_6__
        return __block_result_5__

    def f_updateHistogram(a_histogram, x1, x2, y, histogramColor, histogramPixels):
        return array.push(a_histogram, line.new(x1, y, x2, y, xloc=xloc.bar_time, color=histogramColor, width=histogramPixels))

    def f_updateVolumeLabels(a_volumeLabels, x, y, leftVolume, rightVolume, size__ren__):
        return array.push(a_volumeLabels, f_label_new(x, y, string.tostring(leftVolume, '0') + ' - ' + string.tostring(rightVolume, '0'), label.style_label_center, size__ren__, text.align_center))

    isIndex = syminfo.type == 'index'
    isPeriodOK = timeframe.isminutes == True and _timeframe_multiplier <= 720 and (i_period % 2 == 0) and (i_period % _timeframe_multiplier == 0)
    customHelpHeader = 'Ticker not allowed! It is an index, select a ticker with volume data.' if isIndex else 'Parameters not allowed! Select a new period size and/or chart timeframe.' if not isPeriodOK else 'HELP INFO'
    isGoodToGo = not isIndex and (not i_showHelp) and isPeriodOK
    if not isGoodToGo:
        f_printHelp('' + '\n' + '\n' + '\nWaindrops [Makit0] v0.67beta' + '\n' + '\n' + customHelpHeader + '\n' + '\n\u2003• Max allowed period input 2880 min (48H)' + '\n\u2003• Max allowed chart resolution 720 min (12H)' + '\n\u2003• You must choose a value divisible by 2 and multiple of the current chart timeframe' + '\n\u2003• For example a period of 10 on 1 min chart, a period of 60 on a 5 min chart, etc...' + '\n\u2003• Rule of thumb (valid period size): multiply your current chart timeframe by a par number' + '\n' + '\nHow-to set full session periods:' + '\n\u2003• ES -> waindrop: 1380 | volume profile: 2760 | overnight/cash waindrop: 1860' + '\n\u2003• SPY -> waindrop:  390 | volume profile:  780' + '\n\u2003• EURUSD -> waindrop: 1440 | volume profile: 2880' + '\n' + '\nHow-to avoid errors:' + '\n\u2003• Hide and show the indicator (eye-shape button): this makes the script recalculate' + '\n\u2003• Increase the chart timeframe: less bars on the same period size equals less script iterations' + '\n\u2003• Lower the period size: equals smaller histograms and those are easier to calculate' + '\n\u2003• Lower the execution window: it is faster to execute in the last day than in the last 100 days' + '\n\u2003• Lower the ticks per bar: more ticks per bar equals more calculations to generate the histogram' + '\n\u2003• Lower the updates per period: huge impact, avoid the each bar update to boost speed execution' + '\n\u2003• Deactivate the volume labels: high impact, avoid to plot labels to boost speed execution' + '\n\u2003• Deactivate the histogram (yep, this is a bit overkill I know... but very effective too :D)' + '\n')
    if isGoodToGo:
        halfPeriod = cast_int(0.5 * i_period)
        isNewPeriod = ta.change(time(string.tostring(i_period))) != 0
        isHalfPeriod = ta.change(time(string.tostring(halfPeriod))) != 0
        newPeriodTime: Persistent[int] = 0
        _time: Persistent[int] = 0
        _time = time
        newPeriodTime = _time if isNewPeriod else newPeriodTime
        halfPeriodTime = f_getTimePointInPeriod(newPeriodTime, halfPeriod)
        fullPeriodTime = f_getTimePointInPeriod(halfPeriodTime, halfPeriod)
        is2ndHalf: Series = _time >= halfPeriodTime
        cumVol: Persistent[float] = 0.0
        cumPriceXVol: Persistent[float] = 0.0
        _volume: Persistent[float] = 0.0
        _volume = volume
        _hlc3: Persistent[float] = 0.0
        _hlc3 = hlc3
        cumVol = _volume if isHalfPeriod else cumVol + _volume
        cumPriceXVol = _hlc3 * _volume if isHalfPeriod else cumPriceXVol + _hlc3 * _volume
        periodHigh: Persistent[float] = 0.0
        periodLow: Persistent[float] = 0.0
        _high: Persistent[float] = 0.0
        _high = high
        _low: Persistent[float] = 0.0
        _low = low
        periodHigh = _high if isNewPeriod else _high if _high > periodHigh else periodHigh
        periodLow = _low if isNewPeriod else _low if _low < periodLow else periodLow
        vwapLeft: Persistent[float] = 0.0
        vwapRight: Persistent[float] = 0.0
        vwapLeft = f_round_tick(vwapLeft if is2ndHalf else cumPriceXVol / cumVol)
        vwapRight = f_round_tick(cumPriceXVol / cumVol if is2ndHalf else vwapRight)
        vwapDelta = f_delta_tick(vwapRight, vwapLeft) if is2ndHalf else f_delta_tick(vwapLeft, vwapRight)
        histogramColor = i_histogramNeutralColor if math.abs(vwapDelta) <= i_histogramNeutralTreshold else i_histogramBullColor if vwapDelta > 0 else i_histogramBearColor
        barsColor = i_barsColor if i_barsColorMode == BARS else histogramColor
        l_central: Persistent[Line] = na(Line)
        l_left: Persistent[Line] = na(Line)
        l_right: Persistent[Line] = na(Line)
        if i_showBars:
            if is2ndHalf:
                if isHalfPeriod:
                    l_right = f_line_new(halfPeriodTime, vwapRight, fullPeriodTime, vwapRight) if i_showVWAPBars else na
                    f_void()
                else:
                    f_line_set_y(l_right, vwapRight)
            else:
                if isNewPeriod:
                    l_central = f_line_new(halfPeriodTime, periodHigh, halfPeriodTime, periodLow) if i_showCentralBars else na
                    l_left = f_line_new(newPeriodTime, vwapLeft, halfPeriodTime, vwapLeft) if i_showVWAPBars else na
                    if is2ndHalf[1]:
                        line.set_x2(l_right, _time)
                        l_right = na
                    f_void()
                else:
                    f_line_set_y(l_left, vwapLeft)
            f_line_set_y1y2(l_central, periodHigh, periodLow)
            f_line_set_color(l_left, l_central, l_right, barsColor)
        executionWindow = timenow - _time < 1000 * 60 * 60 * 24 * i_histogramPeriods
        isExecutionAllowed = (i_showHistogram or i_showVolumeInfo) and executionWindow and barstate.isconfirmed
        if isExecutionAllowed:
            a_priceLeft: Persistent[list[float]] = array.new_float(0)
            a_volumeLeft: Persistent[list[float]] = array.new_float(0)
            a_priceRight: Persistent[list[float]] = array.new_float(0)
            a_volumeRight: Persistent[list[float]] = array.new_float(0)
            a_histogram: Persistent[list[Line]] = array.new_line(na)
            a_volumeLabels: Persistent[list[Label]] = array.new_label(na)
            leftVolumeInfoLabel: Persistent[Label] = na(Label)
            rightVolumeInfoLabel: Persistent[Label] = na(Label)
            totalVolumeInfoLabel: Persistent[Label] = na(Label)
            labelSize = size.auto if i_volumeLabelsSize == AUTO else size.tiny if i_volumeLabelsSize == TINY else size.small if i_volumeLabelsSize == SMALL else size.normal if i_volumeLabelsSize == NORMAL else size.large
            if isNewPeriod:
                f_clearArrays(a_priceLeft, a_volumeLeft, a_priceRight, a_volumeRight, a_histogram, a_volumeLabels)
                if i_showVolumeInfo:
                    leftVolumeInfoLabel = f_label_new(halfPeriodTime, periodLow, '', label.style_label_right, labelSize, text.align_right)
                    rightVolumeInfoLabel = f_label_new(halfPeriodTime, periodLow, '', label.style_label_left, labelSize, text.align_left)
                    totalVolumeInfoLabel = f_label_new(halfPeriodTime, periodLow, '', label.style_label_up, labelSize, text.align_center)
            if is2ndHalf:
                f_populate_array(a_priceRight, a_volumeRight)
            else:
                f_populate_array(a_priceLeft, a_volumeLeft)
            factorLeft: Persistent[int] = 0
            factorRight: Persistent[int] = 0
            factorLeft = cast_int((_time - newPeriodTime) / msByPeriodUnit) + 1 if not is2ndHalf else factorLeft
            factorRight = cast_int((_time - halfPeriodTime) / msByPeriodUnit) + 1 if is2ndHalf else factorRight
            quarterPeriod = cast_int(0.5 * halfPeriod)
            quarter1PeriodTime = f_getTimePointInPeriod(newPeriodTime, quarterPeriod)
            quarter3PeriodTime = f_getTimePointInPeriod(halfPeriodTime, quarterPeriod)
            isEndOfQuarter1 = _time == quarter1PeriodTime - msByPeriodUnit
            isEndOf1stHalf = _time == halfPeriodTime - msByPeriodUnit
            isEndOfQuarter3 = _time == quarter3PeriodTime - msByPeriodUnit
            isEndOfPeriod = _time == fullPeriodTime - msByPeriodUnit
            triggerUpdateONE = isEndOfPeriod
            triggerUpdateTWO = triggerUpdateONE or isEndOf1stHalf
            triggerUpdateFOUR = triggerUpdateTWO or isEndOfQuarter1 or isEndOfQuarter3
            isUpdateAllowed = i_histogramUpdateMode == EACHBAR or (i_histogramUpdateMode == ONE and triggerUpdateONE) or (i_histogramUpdateMode == TWO and triggerUpdateTWO) or (i_histogramUpdateMode == FOUR and triggerUpdateFOUR)
            if isUpdateAllowed:
                a_volumeLeftParsed: list[float] = array.new_float(0)
                a_volumeRightParsed: list[float] = array.new_float(0)
                step = i_histogramGranularity * _mintick
                for level in pine_range(periodLow, periodHigh, step):
                    array.push(a_volumeLeftParsed, f_volumeByMultiLevel_NOLOOP(a_priceLeft, a_volumeLeft, level, i_histogramGranularity))
                    array.push(a_volumeRightParsed, f_volumeByMultiLevel_NOLOOP(a_priceRight, a_volumeRight, level, i_histogramGranularity))
                if i_showVolumeInfo:
                    f_label_set_y(leftVolumeInfoLabel, rightVolumeInfoLabel, totalVolumeInfoLabel, periodLow - step)
                    label.set_text(leftVolumeInfoLabel, string.tostring(array.sum(a_volumeLeftParsed), '0'))
                    label.set_text(rightVolumeInfoLabel, string.tostring(array.sum(a_volumeRightParsed), '0'))
                    label.set_text(totalVolumeInfoLabel, string.tostring(array.sum(a_volumeLeftParsed) + array.sum(a_volumeRightParsed), '0'))
                endIndex = (math.max(array.size(a_volumeLeftParsed), array.size(a_volumeRightParsed)) if is2ndHalf else array.size(a_volumeLeftParsed)) - 1
                if endIndex >= 0:
                    f_deleteHistogram(a_histogram)
                    f_deleteVolumeLabels(a_volumeLabels)
                    for i in pine_range(0, endIndex, 1):
                        volumeLeft = array.get(a_volumeLeftParsed, i)
                        volumeRight = array.get(a_volumeRightParsed, i)
                        sizeLeft = math.round(factorLeft * (volumeLeft / array.max(a_volumeLeftParsed)))
                        sizeRight = math.round(factorRight * (volumeRight / array.max(a_volumeRightParsed)))
                        x1 = halfPeriodTime - sizeLeft * msByPeriodUnit
                        x2 = halfPeriodTime + sizeRight * msByPeriodUnit
                        y = periodLow + i * step
                        if i_showHistogram:
                            f_updateHistogram(a_histogram, x1, x2, y, histogramColor, i_histogramPixels)
                        if i_showVolumeInfo:
                            f_updateVolumeLabels(a_volumeLabels, halfPeriodTime, y, volumeLeft, volumeRight, labelSize)
    plot(close if i_trackPrice else na, title='', style=plot.style_circles, show_last=1, linewidth=4, color=color.new(color.yellow, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)