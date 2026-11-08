"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    array, bar_index, barmerge, barstate, box, close, color, high, input,
    label, line, location, low, math, na, nz, open, plotcandle, plotshape, request, script, shape,
    size, string, syminfo, ta, table, text, time, timeframe, timestamp, xloc, yloc
)
from pynecore.types import Box, Label, Line, Persistent, PersistentSeries, Series, Table

GRP_TF1: str = '•••••••• Timeframe 1 Market Structure ••••••••'
GRP_OTHER_STRUCTURE: str = '•••••••• Other Structure Settings ••••••••'


@script.indicator('Algo Market Structure (Nephew_Sam_)', overlay=True, max_bars_back=800, max_labels_count=300, max_lines_count=300, na_bool=True)
def main(
    tf1_useStructure=input.bool(True, '', inline='1', group=GRP_TF1),
    tf1_timeframe=input.timeframe('', 'Timeframe 1', inline='1', group=GRP_TF1),
    tf1_min=input.timeframe('', 'Min', inline='1', group=GRP_TF1),
    tf1_div1=input.bool(False, '----------------------------------', group=GRP_TF1),
    tf1_structureTopColor=input.color(color.new(color.green, 70), 'Top', group=GRP_TF1, inline='2'),
    tf1_structureBottomColor=input.color(color.new(color.green, 70), 'Bottom', group=GRP_TF1, inline='2'),
    tf1_structurelabelSize=input.string(title='Size', defval='auto', options=('auto', 'Tiny', 'Small'), group=GRP_TF1, inline='2'),
    tf1_showHhll=input.bool(True, 'HH/LL Labels', inline='2b', group=GRP_TF1),
    tf1_hhllBullColor=input.color(color.lime, 'Bull', group=GRP_TF1, inline='2b'),
    tf1_hhllBearColor=input.color(color.red, 'Bear', group=GRP_TF1, inline='2b'),
    tf1_hhllLabelSize=input.string(title='Size', defval='Small', options=('auto', 'Tiny', 'Small', 'Normal'), group=GRP_TF1, inline='2b'),
    tf1_div2=input.bool(False, '----------------------------------', group=GRP_TF1),
    tf1_showIlq=input.bool(True, 'Show ILQ ?', inline='3', group=GRP_TF1),
    tf1_ilqText=input.string(defval='ILQ', title='Text', inline='3', group=GRP_TF1),
    tf1_ilqStyle=input.string(title='Style', defval='Solid', options=('Solid', 'Dashed', 'Dotted'), inline='4', group=GRP_TF1),
    tf1_ilqWidth=input.int(2, 'Width', minval=1, maxval=4, inline='4', group=GRP_TF1),
    tf1_ilqCol=input.color(color.orange, title='Col', inline='4', group=GRP_TF1),
    tf1_div3=input.bool(False, '----------------------------------', group=GRP_TF1),
    tf1_showTlq=input.bool(True, 'Show TLQ ?', inline='5', group=GRP_TF1),
    tf1_tlqText=input.string(defval='TLQ', title='Text', inline='5', group=GRP_TF1),
    tf1_showBos=input.bool(True, 'Bos lines ?', inline='5', group=GRP_TF1),
    tf1_tlqStyle=input.string(title='Style', defval='Solid', options=('Solid', 'Dashed', 'Dotted'), inline='6', group=GRP_TF1),
    tf1_tlqWidth=input.int(1, 'Width', minval=1, maxval=4, inline='6', group=GRP_TF1),
    tf1_tlqCol=input.color(color.lime, title='Col', inline='6', group=GRP_TF1),
    tf1_div4=input.bool(False, '----------------------------------', group=GRP_TF1),
    tf1_showEpa=input.bool(True, 'Show EPA ?', inline='7', group=GRP_TF1),
    tf1_epaText=input.string(defval='EPA', title='Text', inline='7', group=GRP_TF1),
    tf1_epaDelete=input.bool(True, 'Delete Unfilled', inline='7', group=GRP_TF1),
    tf1_epaStyle=input.string(title='Style', defval='Dashed', options=('Solid', 'Dashed', 'Dotted'), inline='8', group=GRP_TF1),
    tf1_epaWidth=input.int(1, 'Width', minval=1, maxval=4, inline='8', group=GRP_TF1),
    tf1_epaCol=input.color(color.blue, title='Col', inline='8', group=GRP_TF1),
    tf1_div5=input.bool(False, '----------------------------------', group=GRP_TF1),
    tf1_showMsu=input.bool(True, 'Show MSU Arrows ?', inline='9', group=GRP_TF1),
    tf1_div6=input.bool(False, '----------------------------------', group=GRP_TF1),
    tf1_showExtreme=input.bool(True, 'Show Extreme ?', inline='10', group=GRP_TF1),
    tf1_extremeText=input.string(defval='Extreme', title='Text', inline='10', group=GRP_TF1),
    tf1_extremeCol=input.color(color.new(color.gray, 80), title='Col', inline='10', group=GRP_TF1),
    tf1_div7=input.bool(False, '----------------------------------', group=GRP_TF1),
    tf1_showVta=input.bool(True, 'Show VTA ?', inline='11', group=GRP_TF1),
    tf1_strictVta=input.bool(False, 'Strict ?', inline='11', group=GRP_TF1),
    tf1_vtaText=input.string(defval='Valid Trading Range', title='Text', inline='11', group=GRP_TF1),
    tf1_vtaTopCol=input.color(color.red, title='Top Col', inline='12', group=GRP_TF1),
    tf1_vtaBottomCol=input.color(color.green, title='Bottom Col', inline='12', group=GRP_TF1),
    tf1_deleteVta=input.bool(True, 'Delete filled ?', inline='12', group=GRP_TF1),
    tf1_div8=input.bool(False, '----------------------------------', group=GRP_TF1),
    tf1_changeBarCol=input.bool(True, 'Change bar colors (read tooltip)?', inline='13', group=GRP_TF1, tooltip='Right click on your indicator, then under visual order select bring to front.\n\nSelect only 1 timeframe at a time.'),
    tf1_bullishBullBarCol=input.color(color.rgb(107, 194, 179), title='Bullish Bull', inline='14', group=GRP_TF1),
    tf1_bullishBearBarCol=input.color(color.rgb(53, 141, 131), title='Bullish Bear', inline='14', group=GRP_TF1),
    tf1_bearishBullBarCol=input.color(color.rgb(247, 134, 143), title='Bearish Bull', inline='15', group=GRP_TF1),
    tf1_bearishBearBarCol=input.color(color.rgb(193, 81, 95), title='Bearish Bear', inline='15', group=GRP_TF1),
    structure_show_table=input.bool(True, 'Table', inline='1', group=GRP_OTHER_STRUCTURE),
    structure_table_vertical=input.string('bottom', '↕', inline='2', group=GRP_OTHER_STRUCTURE, options=('top', 'middle', 'bottom')),
    structure_table_horizontal=input.string('right', '↔', inline='2', group=GRP_OTHER_STRUCTURE, options=('left', 'center', 'right')),
    indicator_start_time=input.time(timestamp('02 Jan 2015 00:00 +0300'), title='Indicator Start Date', group=GRP_OTHER_STRUCTURE, tooltip='You can set a recent time if structure has been in a long range')
):
    TRANSPARENT = color.new(color.white, 100)
    LABEL_SPACE: str = '          '
    MIN = -1e+19
    MAX: float = 1e+19
    timesArray: Persistent[list[int]] = array.new_int()
    array.push(timesArray, time)
    def isNeutral(i = 0):
        return open[i] == close[i]

    def isBearish(i = 0):
        _n = isNeutral(i)
        _temp = close[i + 1] < open[i + 1] if _n else close[i] < open[i]
        return _temp

    def isBullish(i = 0):
        _n = isNeutral(i)
        _temp = close[i + 1] > open[i + 1] if _n else close[i] > open[i]
        return _temp

    def getLineStyle(_style):
        _linestyle = line.style_solid if _style == 'Solid' else line.style_dashed if _style == 'Dashed' else line.style_dotted
        return _linestyle

    def getlabelSize(_labelSize):
        _size = size.auto if _labelSize == 'auto' else size.tiny if _labelSize == 'Tiny' else size.small if _labelSize == 'Small' else size.normal if _labelSize == 'Normal' else size.huge
        return _size

    def addToArray(_array, _val):
        return array.unshift(_array, _val)

    def removeFromArray(_array, _index):
        return array.remove(_array, _index)

    def updateArrayElement(_array, _index, _val):
        return array.set(_array, _index, _val)

    def getLastElementInArray(_arr):
        _size = array.size(_arr)
        _el = array.get(_arr, _size - 1) if _size > 0 else na
        return _el

    def _get(_array, _i = 0):
        _temp = array.get(_array, _i)
        return _temp

    def get5ArrayValues(_array):
        _0 = array.get(_array, 0)
        _1 = array.get(_array, 1)
        _2 = array.get(_array, 2)
        _3 = array.get(_array, 3)
        _4 = array.get(_array, 4)
        return (_0, _1, _2, _3, _4)

    def _bottom(_id):
        return box.get_bottom(_id)

    def _top(_id):
        return box.get_top(_id)

    def _left(_id):
        return box.get_left(_id)

    def _right(_id):
        return box.get_right(_id)

    def isRegularFractal(mode, n):
        ret = high[n - 1] < high[n] and high[n + 1] < high[n] if mode == 'Buy' else low[n - 1] > low[n] and low[n + 1] > low[n] if mode == 'Sell' else False
        return ret

    def isBWFractal(mode, n):
        ret = high[n - 2] < high[n] and high[n - 1] < high[n] and (high[n + 1] < high[n]) and (high[n + 2] < high[n]) if mode == 'Buy' else low[n - 2] > low[n] and low[n - 1] > low[n] and (low[n + 1] > low[n]) and (low[n + 2] > low[n]) if mode == 'Sell' else False
        return ret

    def isFractalHigh(i, _filter):
        return isRegularFractal('Buy', i) if _filter == '3' else isBWFractal('Buy', i + 1)

    def isFractalLow(i, _filter):
        return isRegularFractal('Sell', i) if _filter == '3' else isBWFractal('Sell', i + 1)

    def delete_label(_l):
        __block_result__ = na
        if not na(_l):
            __block_result__ = label.delete(_l)
        return __block_result__

    def delete_line(_l):
        __block_result_1__ = na
        if not na(_l):
            __block_result_1__ = line.delete(_l)
        return __block_result_1__

    def delete_box(_l):
        __block_result_2__ = na
        if not na(_l):
            __block_result_2__ = box.delete(_l)
        return __block_result_2__

    def reso(exp, res):
        return request.security(syminfo.tickerid, res, exp, lookahead=barmerge.lookahead_on)

    def resolutionInMinutes(tf = ''):
        chartTf = timeframe.multiplier * (1.0 / 60 if timeframe.isseconds else 1.0 if timeframe.isminutes else 60.0 * 24 if timeframe.isdaily else 60.0 * 24 * 7 if timeframe.isweekly else 60.0 * 24 * 30.4375 if timeframe.ismonthly else na)
        result: float = chartTf if tf == '' else request.security(syminfo.tickerid, tf, chartTf)
        return result

    def f_timeFrom(length, _tf = timeframe.period):
        _timeFrom: int = na(int)
        _timeFrom = cast_int(time + resolutionInMinutes(_tf) * 60 * 1000 * length)
        return _timeFrom

    def isHigherTimeframe(tf, eq = False):
        _cond = resolutionInMinutes() >= resolutionInMinutes(tf) if eq else resolutionInMinutes() > resolutionInMinutes(tf)
        return _cond

    def isLowerTimeframe(tf, eq = False):
        _cond = resolutionInMinutes() <= resolutionInMinutes(tf) if eq else resolutionInMinutes() < resolutionInMinutes(tf)
        return _cond

    def timeToBarIndex(_from):
        __cond = math.round((time - _from) / (1000 * timeframe.in_seconds(timeframe.period)))
        _cond = math.abs(math.round(__cond)) if __cond <= 5000 else 5000
        return _cond

    def barIndexAtTime(_arr, timeToFind: Series[int]):
        barOfTime: int = array.indexof(_arr, timeToFind)
        _result: int = na(int)
        if barOfTime == -1:
            _timetobars = timeToBarIndex(timeToFind)
            _result = _timetobars
        else:
            _result = bar_index - barOfTime
        result = math.abs(math.round(_result)) if _result <= 5000 else 5000
        return result

    def findHtfTimeInLtf(_src, _pivotPrice, _maxBack):
        _time: int = na(int)
        _bar_index: int = na(int)
        _delta: float = 100000000000.0
        if not na(_pivotPrice):
            for _i in pine_range(_maxBack, 0, 1):
                _thisDelta = math.abs(high[_i] - _pivotPrice) if _src == 'high' else math.abs(low[_i] - _pivotPrice)
                if _thisDelta < _delta:
                    _delta = _thisDelta
                    _time = time[_i]
                    _bar_index = bar_index[_i]
        return (_time, _bar_index)

    def getExactTime(_time, _price, _timeframe, _direction):
        _pivotTime = _time
        if isLowerTimeframe(_timeframe):
            _barsback = barIndexAtTime(timesArray, _time)
            __hTime, __hBi = findHtfTimeInLtf(_direction, _price, _barsback)
            _pivotTime = __hTime
        return _pivotTime

    def findHighestBetweenTimes(_time1, _time2, _defaultH):
        _highest = _defaultH
        _highestTime = _time1
        sBi0 = barIndexAtTime(timesArray, _time1)
        sBi1 = barIndexAtTime(timesArray, _time2)
        if _time1 > _time2:
            _startFrom = sBi1 if isBullish(sBi1) else sBi1 - 1
            _endTo = sBi0 if isBearish(sBi0) else sBi0 + 1
            for i in pine_range(_startFrom, _endTo, 1):
                if high[i] > _highest:
                    _highest = high[i]
                    _highestTime = time[i]
        return (_highest, _highestTime)

    def findLowestBetweenTimes(_time1, _time2, _defaultL):
        _lowest = _defaultL
        _lowestTime = _time1
        sBi0 = barIndexAtTime(timesArray, _time1)
        sBi1 = barIndexAtTime(timesArray, _time2)
        if _time1 > _time2:
            _startFrom = sBi1 if isBearish(sBi1) else sBi1 - 1
            _endTo = sBi0 if isBullish(sBi0) else sBi0 + 1
            for i in pine_range(_startFrom, _endTo, 1):
                if low[i] < _lowest:
                    _lowest = low[i]
                    _lowestTime = time[i]
        return (_lowest, _lowestTime)

    def get_pivot_ohlc(i = 0):
        return (open, high, low, close, time, open[1], high[1], low[1], close[1], time[1], open[2], high[2], low[2], close[2], time[2])

    def get_phpl(countSinceBullCandle, countSinceBearCandle):
        _highest = ta.highest(countSinceBullCandle + 1) if countSinceBullCandle >= 0 else -1
        _highestBi = ta.valuewhen(high == _highest, bar_index, 0)
        _highestTime = ta.valuewhen(high == _highest, time, 0)
        _lowest = ta.lowest(countSinceBearCandle + 1) if countSinceBearCandle >= 0 else -1
        _lowestBi = ta.valuewhen(low == _lowest, bar_index, 0)
        _lowestTime = ta.valuewhen(low == _lowest, time, 0)
        return (_highest, _highestTime, _lowest, _lowestTime)

    def getPhlData(_t, _offset):
        h = reso(high[_offset], _t)
        l = reso(low[_offset], _t)
        _time: Series = time(_t)
        newbar = na(_time[1]) or _time > _time[1]
        return (h, l, newbar, _time)

    _TimeTo = f_timeFrom(7)
    def GetPipSize():
        return syminfo.mintick * (10 if syminfo.type == 'forex' else 1)

    tf1_open, tf1_high, tf1_low, tf1_close, tf1_time, tf1_open1, tf1_high1, tf1_low1, tf1_close1, tf1_time1, tf1_open2, tf1_high2, tf1_low2, tf1_close2, tf1_time2 = request.security(syminfo.tickerid, tf1_timeframe, get_pivot_ohlc(), lookahead=barmerge.lookahead_on)
    isHigherTimeframe_1 = isHigherTimeframe(tf1_min, True)
    isUseTimeframe1 = not isHigherTimeframe(tf1_timeframe) and isHigherTimeframe_1 and tf1_useStructure and (time > indicator_start_time)
    tf1_lastBullCandle: Persistent[bool] = False
    tf1_lastBearCandle: Persistent[bool] = False
    if tf1_close1 > tf1_open1:
        tf1_lastBullCandle = True
        tf1_lastBearCandle = False
    if tf1_close1 < tf1_open1:
        tf1_lastBullCandle = False
        tf1_lastBearCandle = True
    _tf1_countBull = ta.barssince(tf1_lastBullCandle)
    tf1_countSinceBullCandle = request.security(syminfo.tickerid, tf1_timeframe, _tf1_countBull, lookahead=barmerge.lookahead_on)
    _tf1_countBear = ta.barssince(tf1_lastBearCandle)
    tf1_countSinceBearCandle = request.security(syminfo.tickerid, tf1_timeframe, _tf1_countBear, lookahead=barmerge.lookahead_on)
    tf1_newbar = ta.change(time(tf1_timeframe)) > 0
    tf1_pivotHighs: Persistent[list[float]] = array.new_float(5, MIN)
    tf1_pivotHighsTime: Persistent[list[int]] = array.new_int(5)
    tf1_pivotLows: Persistent[list[float]] = array.new_float(5, MAX)
    tf1_pivotLowsTime: Persistent[list[int]] = array.new_int(5)
    tf1_pivotHighLabel: Persistent[Label] = na(Label)
    tf1_pivotLowLabel: Persistent[Label] = na(Label)
    tf1_pivotHighHhllLabel: Persistent[Label] = na(Label)
    tf1_pivotLowHhllLabel: Persistent[Label] = na(Label)
    tf1_isStructureHigh: bool = False
    tf1_isStructureLow: bool = False
    tf1_canPlot = tf1_newbar and isUseTimeframe1
    tf1_mostRecentBullCount1: Persistent = time
    tf1_mostRecentBearCount1: Persistent = time
    tf1_initialised: Persistent[bool] = False
    if tf1_canPlot and (not tf1_initialised):
        addToArray(tf1_pivotHighsTime, tf1_time)
        addToArray(tf1_pivotHighs, tf1_high)
        addToArray(tf1_pivotLowsTime, tf1_time)
        addToArray(tf1_pivotLows, tf1_low)
        tf1_initialised = True
    if tf1_canPlot:
        if tf1_countSinceBullCandle >= 1:
            __time = tf1_time1 if tf1_close1 > tf1_open1 else tf1_time
            tf1_highest, tf1_highestTime = findHighestBetweenTimes(__time, _get(tf1_pivotHighsTime), MIN)
            if tf1_countSinceBullCandle == 1:
                tf1_mostRecentBullCount1 = __time
            if tf1_highest > _get(tf1_pivotHighs):
                _get_1 = _get(tf1_pivotHighsTime)
                if tf1_countSinceBullCandle == 1 and tf1_close1 != tf1_open1 or (tf1_countSinceBullCandle > 1 and tf1_highestTime >= tf1_mostRecentBullCount1 and (tf1_close < tf1_open)):
                    tf1_isStructureHigh = True
                    addToArray(tf1_pivotHighsTime, tf1_highestTime)
                    addToArray(tf1_pivotHighs, tf1_highest)
                    tf1_pivotHighLabel = label.new(tf1_highestTime, tf1_highest, xloc=xloc.bar_time, style=label.style_circle, size=getlabelSize(tf1_structurelabelSize), color=tf1_structureTopColor)
                    if tf1_showHhll:
                        tf1_pivotHighHhllLabel = label.new(tf1_highestTime, tf1_highest, xloc=xloc.bar_time, yloc=yloc.abovebar, text='HH', style=label.style_none, size=getlabelSize(tf1_hhllLabelSize), textcolor=tf1_hhllBullColor)
                    tf1_lowest, tf1_lowestTime = findLowestBetweenTimes(_get(tf1_pivotHighsTime), _get(tf1_pivotHighsTime, 1), MAX)
                    if tf1_lowestTime != _get(tf1_pivotLowsTime):
                        addToArray(tf1_pivotLowsTime, tf1_lowestTime)
                        addToArray(tf1_pivotLows, tf1_lowest)
                        tf1_pivotLowLabel = label.new(tf1_lowestTime, tf1_lowest, xloc=xloc.bar_time, style=label.style_circle, size=getlabelSize(tf1_structurelabelSize), color=tf1_structureBottomColor)
                        if tf1_showHhll:
                            tf1_pivotLowHhllLabel = label.new(tf1_lowestTime, tf1_lowest, xloc=xloc.bar_time, yloc=yloc.belowbar, text='HL', style=label.style_none, size=getlabelSize(tf1_hhllLabelSize), textcolor=tf1_hhllBullColor)
                elif tf1_countSinceBullCandle > 1 and _get_1 >= tf1_mostRecentBullCount1 and (tf1_close < tf1_open):
                    updateArrayElement(tf1_pivotHighsTime, 0, tf1_highestTime)
                    updateArrayElement(tf1_pivotHighs, 0, tf1_highest)
                    label.delete(tf1_pivotHighLabel)
                    tf1_pivotHighLabel = label.new(tf1_highestTime, tf1_highest, xloc=xloc.bar_time, style=label.style_circle, size=getlabelSize(tf1_structurelabelSize), color=tf1_structureTopColor)
                    if tf1_showHhll:
                        label.delete(tf1_pivotHighHhllLabel)
                        tf1_pivotHighHhllLabel = label.new(tf1_highestTime, tf1_highest, xloc=xloc.bar_time, yloc=yloc.abovebar, text='HH', style=label.style_none, size=getlabelSize(tf1_hhllLabelSize), textcolor=tf1_hhllBullColor)
        if tf1_countSinceBearCandle >= 1:
            __time = tf1_time1 if tf1_close1 < tf1_open1 else tf1_time
            tf1_lowest, tf1_lowestTime = findLowestBetweenTimes(__time, _get(tf1_pivotLowsTime), MAX)
            if tf1_countSinceBearCandle == 1:
                tf1_mostRecentBearCount1 = __time
            if tf1_lowest < _get(tf1_pivotLows):
                _get_1 = _get(tf1_pivotLowsTime)
                if tf1_countSinceBearCandle == 1 and tf1_close1 != tf1_open1 or (tf1_countSinceBearCandle > 1 and tf1_lowestTime >= tf1_mostRecentBearCount1 and (tf1_close > tf1_open)):
                    tf1_isStructureLow = True
                    addToArray(tf1_pivotLowsTime, tf1_lowestTime)
                    addToArray(tf1_pivotLows, tf1_lowest)
                    tf1_pivotLowLabel = label.new(tf1_lowestTime, tf1_lowest, xloc=xloc.bar_time, style=label.style_circle, size=getlabelSize(tf1_structurelabelSize), color=tf1_structureBottomColor)
                    if tf1_showHhll:
                        tf1_pivotLowHhllLabel = label.new(tf1_lowestTime, tf1_lowest, xloc=xloc.bar_time, yloc=yloc.belowbar, text='LL', style=label.style_none, size=getlabelSize(tf1_hhllLabelSize), textcolor=tf1_hhllBearColor)
                    tf1_highest, tf1_highestTime = findHighestBetweenTimes(_get(tf1_pivotLowsTime), _get(tf1_pivotLowsTime, 1), MIN)
                    if tf1_highestTime != _get(tf1_pivotHighsTime):
                        addToArray(tf1_pivotHighsTime, tf1_highestTime)
                        addToArray(tf1_pivotHighs, tf1_highest)
                        tf1_pivotHighLabel = label.new(tf1_highestTime, tf1_highest, xloc=xloc.bar_time, style=label.style_circle, size=getlabelSize(tf1_structurelabelSize), color=tf1_structureTopColor)
                        if tf1_showHhll:
                            tf1_pivotHighHhllLabel = label.new(tf1_highestTime, tf1_highest, xloc=xloc.bar_time, yloc=yloc.abovebar, text='LH', style=label.style_none, size=getlabelSize(tf1_hhllLabelSize), textcolor=tf1_hhllBearColor)
                elif tf1_countSinceBearCandle > 1 and _get_1 >= tf1_mostRecentBearCount1 and (tf1_close > tf1_open):
                    updateArrayElement(tf1_pivotLowsTime, 0, tf1_lowestTime)
                    updateArrayElement(tf1_pivotLows, 0, tf1_lowest)
                    label.delete(tf1_pivotLowLabel)
                    tf1_pivotLowLabel = label.new(tf1_lowestTime, tf1_lowest, xloc=xloc.bar_time, style=label.style_circle, size=getlabelSize(tf1_structurelabelSize), color=tf1_structureBottomColor)
                    if tf1_showHhll:
                        label.delete(tf1_pivotLowHhllLabel)
                        tf1_pivotLowHhllLabel = label.new(tf1_lowestTime, tf1_lowest, xloc=xloc.bar_time, yloc=yloc.belowbar, text='LL', style=label.style_none, size=getlabelSize(tf1_hhllLabelSize), textcolor=tf1_hhllBearColor)
    tf1_ph0, tf1_ph1, tf1_ph2, tf1_ph3, tf1_ph4 = get5ArrayValues(tf1_pivotHighs)
    tf1_pl0, tf1_pl1, tf1_pl2, tf1_pl3, tf1_pl4 = get5ArrayValues(tf1_pivotLows)
    tf1_ph0Time, tf1_ph1Time, tf1_ph2Time, tf1_ph3Time, tf1_ph4Time = get5ArrayValues(tf1_pivotHighsTime)
    tf1_pl0Time, tf1_pl1Time, tf1_pl2Time, tf1_pl3Time, tf1_pl4Time = get5ArrayValues(tf1_pivotLowsTime)
    tf1_isPriceEfficient: Persistent[bool] = False
    tf1_structureDirection: Persistent[str] = 'bullish'
    tf1_isMSU: Persistent[bool] = False
    tf1_isBullishMsu: bool = False
    tf1_isBearishMsu: bool = False
    tf1_isBullishVta: bool = False
    tf1_isBearishVta: bool = False
    tf1_bottomTlqPrice: Persistent[float] = na(float)
    tf1_topTlqPrice: Persistent[float] = na(float)
    tf1_isValidHH: Series = tf1_isStructureHigh and tf1_ph0 > tf1_ph1 and (tf1_ph0 > tf1_ph2) if tf1_structureDirection == 'bullish' else tf1_isStructureHigh and tf1_ph0 > nz(tf1_topTlqPrice)
    tf1_isValidLL: Series = tf1_isStructureLow and tf1_pl0 < tf1_pl1 and (tf1_pl0 < tf1_pl2) if tf1_structureDirection == 'bearish' else tf1_isStructureLow and tf1_pl0 < nz(tf1_bottomTlqPrice)
    tf1_bottomIlqPrice: Persistent[float] = na(float)
    tf1_topIlqPrice: Persistent[float] = na(float)
    tf1_bottomIlqLine: Persistent[Line] = na(Line)
    tf1_topIlqLine: Persistent[Line] = na(Line)
    tf1_bottomIlqLabel: Persistent[Label] = na(Label)
    tf1_topIlqLabel: Persistent[Label] = na(Label)
    if tf1_showIlq:
        if tf1_canPlot:
            if tf1_isValidHH or tf1_isValidLL:
                delete_line(tf1_bottomIlqLine)
                delete_line(tf1_topIlqLine)
                delete_label(tf1_bottomIlqLabel)
                delete_label(tf1_topIlqLabel)
            if tf1_isValidHH:
                tf1_bottomIlqPrice = tf1_pl0
                tf1_topIlqPrice = na
                tf1_bottomIlqLine = line.new(tf1_pl0Time, tf1_pl0, _TimeTo, tf1_pl0, xloc=xloc.bar_time, color=tf1_ilqCol, style=getLineStyle(tf1_ilqStyle), width=tf1_ilqWidth)
                tf1_bottomIlqLabel = label.new(_TimeTo, tf1_pl0, tf1_ilqText + LABEL_SPACE, xloc=xloc.bar_time, style=label.style_none, size=getlabelSize('Normal'), textcolor=tf1_ilqCol)
            if tf1_isValidLL:
                tf1_topIlqPrice = tf1_ph0
                tf1_bottomIlqPrice = na
                tf1_topIlqLine = line.new(tf1_ph0Time, tf1_ph0, _TimeTo, tf1_ph0, xloc=xloc.bar_time, color=tf1_ilqCol, style=getLineStyle(tf1_ilqStyle), width=tf1_ilqWidth)
                tf1_topIlqLabel = label.new(_TimeTo, tf1_ph0, tf1_ilqText + LABEL_SPACE, xloc=xloc.bar_time, style=label.style_none, size=getlabelSize('Normal'), textcolor=tf1_ilqCol)
        if not na(tf1_bottomIlqLine):
            line.set_x2(tf1_bottomIlqLine, _TimeTo)
        if not na(tf1_bottomIlqLabel):
            label.set_x(tf1_bottomIlqLabel, _TimeTo)
        if not na(tf1_bottomIlqLine) and tf1_low < tf1_bottomIlqPrice:
            line.delete(tf1_bottomIlqLine)
            if not na(tf1_bottomIlqLabel):
                label.delete(tf1_bottomIlqLabel)
        if not na(tf1_topIlqLine):
            line.set_x2(tf1_topIlqLine, _TimeTo)
        if not na(tf1_topIlqLabel):
            label.set_x(tf1_topIlqLabel, _TimeTo)
        if not na(tf1_topIlqLine) and tf1_high > tf1_topIlqPrice:
            line.delete(tf1_topIlqLine)
            if not na(tf1_topIlqLabel):
                label.delete(tf1_topIlqLabel)
    tf1_bottomTlqLine: Persistent[Line] = na(Line)
    tf1_topTlqLine: Persistent[Line] = na(Line)
    tf1_bottomTlqLabel: Persistent[Label] = na(Label)
    tf1_topTlqLabel: Persistent[Label] = na(Label)
    ex_usedBosTimes: Persistent[list[int]] = array.new_int(0)
    if tf1_showTlq:
        if not na(tf1_bottomTlqLine) and (low < tf1_bottomTlqPrice or (tf1_isValidHH[1] and low[1] < tf1_bottomTlqPrice) or (low[2] < tf1_pl1 and low[2] < tf1_pl2 and (low[2] < tf1_bottomTlqPrice))) and (not array.includes(ex_usedBosTimes, line.get_x1(tf1_bottomTlqLine))):
            tf1_structureDirection = 'bearish'
            tf1_bottomTlqPrice = na
            addToArray(ex_usedBosTimes, line.get_x1(tf1_bottomTlqLine))
            if tf1_showBos:
                line.new(line.get_x1(tf1_bottomTlqLine), line.get_y1(tf1_bottomTlqLine), time, line.get_y1(tf1_bottomTlqLine), xloc=xloc.bar_time, color=color.red)
                label.new(time, line.get_y1(tf1_bottomTlqLine), 'BOS' + LABEL_SPACE, xloc=xloc.bar_time, style=label.style_none, size=getlabelSize('Normal'), textcolor=color.red)
            line.delete(tf1_bottomTlqLine)
            if not na(tf1_bottomTlqLabel):
                label.delete(tf1_bottomTlqLabel)
        if not na(tf1_topTlqLine) and (high > tf1_topTlqPrice or (tf1_isValidLL[1] and high > tf1_topTlqPrice) or (high[2] > tf1_ph1 and high[2] > tf1_ph2 and (high[2] > tf1_topTlqPrice))) and (not array.includes(ex_usedBosTimes, line.get_x1(tf1_bottomTlqLine))):
            tf1_structureDirection = 'bullish'
            tf1_topTlqPrice = na
            addToArray(ex_usedBosTimes, line.get_x1(tf1_topTlqLine))
            if tf1_showBos:
                line.new(line.get_x1(tf1_topTlqLine), line.get_y1(tf1_topTlqLine), time, line.get_y1(tf1_topTlqLine), xloc=xloc.bar_time, color=color.green)
                label.new(time, line.get_y1(tf1_topTlqLine), 'BOS' + LABEL_SPACE, xloc=xloc.bar_time, style=label.style_none, size=getlabelSize('Normal'), textcolor=color.green)
            line.delete(tf1_topTlqLine)
            if not na(tf1_topTlqLabel):
                label.delete(tf1_topTlqLabel)
        if close < line.get_y1(tf1_topTlqLine):
            tf1_structureDirection = 'bearish'
        if close > line.get_y1(tf1_bottomTlqLine):
            tf1_structureDirection = 'bullish'
        if tf1_canPlot:
            if tf1_isValidHH or tf1_isValidLL:
                delete_line(tf1_bottomTlqLine)
                delete_line(tf1_topTlqLine)
                delete_label(tf1_bottomTlqLabel)
                delete_label(tf1_topTlqLabel)
            if tf1_isValidHH:
                tf1_bottomTlqPrice = tf1_pl1 if tf1_pl1 < tf1_pl0 else tf1_pl0
                tf1_bottomTlqTime = tf1_pl1Time if tf1_pl1 < tf1_pl0 else tf1_pl0Time
                tf1_topTlqPrice = na
                if not array.includes(ex_usedBosTimes, tf1_bottomTlqTime):
                    tf1_bottomTlqLine = line.new(tf1_bottomTlqTime, tf1_bottomTlqPrice, _TimeTo, tf1_bottomTlqPrice, xloc=xloc.bar_time, color=tf1_tlqCol, style=getLineStyle(tf1_tlqStyle), width=tf1_tlqWidth)
                    tf1_bottomTlqLabel = label.new(_TimeTo, tf1_bottomTlqPrice, tf1_tlqText + LABEL_SPACE, xloc=xloc.bar_time, style=label.style_none, size=getlabelSize('Normal'), textcolor=tf1_tlqCol)
            if tf1_isValidLL:
                tf1_topTlqPrice = tf1_ph1 if tf1_ph1 > tf1_ph0 else tf1_ph0
                tf1_topTlqTime = tf1_ph1Time if tf1_ph1 > tf1_ph0 else tf1_ph0Time
                tf1_bottomTlqPrice = na
                if not array.includes(ex_usedBosTimes, tf1_topTlqTime):
                    tf1_topTlqLine = line.new(tf1_topTlqTime, tf1_topTlqPrice, _TimeTo, tf1_topTlqPrice, xloc=xloc.bar_time, color=tf1_tlqCol, style=getLineStyle(tf1_tlqStyle), width=tf1_tlqWidth)
                    tf1_topTlqLabel = label.new(_TimeTo, tf1_topTlqPrice, tf1_tlqText + LABEL_SPACE, xloc=xloc.bar_time, style=label.style_none, size=getlabelSize('Normal'), textcolor=tf1_tlqCol)
        if not na(tf1_bottomTlqLine):
            line.set_x2(tf1_bottomTlqLine, _TimeTo)
        if not na(tf1_bottomTlqLabel):
            label.set_x(tf1_bottomTlqLabel, _TimeTo)
        if not na(tf1_topTlqLine):
            line.set_x2(tf1_topTlqLine, _TimeTo)
        if not na(tf1_topTlqLabel):
            label.set_x(tf1_topTlqLabel, _TimeTo)
    tf1_bottomExtremeBox: PersistentSeries[Box] = na(Box)
    tf1_topExtremeBox: PersistentSeries[Box] = na(Box)
    if tf1_showExtreme:
        if tf1_canPlot:
            if tf1_isValidHH or tf1_isValidLL:
                delete_box(tf1_bottomExtremeBox)
                delete_box(tf1_topExtremeBox)
            if tf1_isValidHH:
                tf1_bottomExtremePrice = tf1_pl1 if tf1_pl1 < tf1_pl0 else tf1_pl0
                tf1_bottomExtremeTime = tf1_pl1Time if tf1_pl1 < tf1_pl0 else tf1_pl0Time
                _biL = barIndexAtTime(timesArray, tf1_bottomExtremeTime)
                lowestBody = close[_biL] if open[_biL] > close[_biL] else open[_biL]
                if _biL > 1:
                    tf1_bottomExtremeBox = box.new(tf1_bottomExtremeTime, lowestBody, _TimeTo, tf1_bottomExtremePrice, xloc=xloc.bar_time, border_color=TRANSPARENT, bgcolor=tf1_extremeCol, text=tf1_extremeText, text_color=color.new(tf1_extremeCol, 0), text_halign=text.align_right, text_valign=text.align_top, text_size=getlabelSize('Small'))
                    delete_box(tf1_bottomExtremeBox[1])
            if tf1_isValidLL:
                tf1_topExtremePrice = tf1_ph1 if tf1_ph1 > tf1_ph0 else tf1_ph0
                tf1_topExtremeTime = tf1_ph1Time if tf1_ph1 > tf1_ph0 else tf1_ph0Time
                _biH = barIndexAtTime(timesArray, tf1_topExtremeTime)
                highestBody = close[_biH] if open[_biH] < close[_biH] else open[_biH]
                if _biH > 1:
                    tf1_topExtremeBox = box.new(tf1_topExtremeTime, tf1_topExtremePrice, _TimeTo, highestBody, xloc=xloc.bar_time, border_color=TRANSPARENT, bgcolor=tf1_extremeCol, text=tf1_extremeText, text_color=color.new(tf1_extremeCol, 0), text_halign=text.align_right, text_valign=text.align_bottom, text_size=getlabelSize('Small'))
                    delete_box(tf1_topExtremeBox[1])
        if not na(tf1_bottomExtremeBox):
            box.set_right(tf1_bottomExtremeBox, _TimeTo)
        _bottom_1 = _bottom(tf1_bottomExtremeBox)
        if not na(tf1_bottomExtremeBox) and low < _bottom_1:
            delete_box(tf1_bottomExtremeBox)
        if not na(tf1_topExtremeBox):
            box.set_right(tf1_topExtremeBox, _TimeTo)
        _top_1 = _top(tf1_topExtremeBox)
        if not na(tf1_topExtremeBox) and high > _top_1:
            delete_box(tf1_topExtremeBox)
    tf1_bearEpaPrice: Persistent[float] = na(float)
    tf1_bullEpaPrice: Persistent[float] = na(float)
    tf1_bearEpaLine: Persistent[Line] = na(Line)
    tf1_bullEpaLine: Persistent[Line] = na(Line)
    tf1_bearEpaLabel: Persistent[Label] = na(Label)
    tf1_bullEpaLabel: Persistent[Label] = na(Label)
    if tf1_showEpa:
        if tf1_canPlot:
            if tf1_isValidHH or tf1_isValidLL:
                tf1_isPriceEfficient = False
                if tf1_epaDelete:
                    delete_line(tf1_bearEpaLine)
                    delete_line(tf1_bullEpaLine)
                    delete_label(tf1_bearEpaLabel)
                    delete_label(tf1_bullEpaLabel)
            if tf1_isValidLL:
                tf1_bearEpaPrice = tf1_pl1
                tf1_bullEpaPrice = na
                tf1_bearEpaLine = line.new(tf1_pl1Time, tf1_pl1, _TimeTo, tf1_pl1, xloc=xloc.bar_time, color=tf1_epaCol, style=getLineStyle(tf1_epaStyle), width=tf1_epaWidth)
                tf1_bearEpaLabel = label.new(_TimeTo, tf1_pl1, tf1_epaText + LABEL_SPACE, xloc=xloc.bar_time, style=label.style_none, size=getlabelSize('Normal'), textcolor=tf1_epaCol)
            if tf1_isValidHH:
                tf1_bullEpaPrice = tf1_ph1
                tf1_bearEpaPrice = na
                tf1_bullEpaLine = line.new(tf1_ph1Time, tf1_ph1, _TimeTo, tf1_ph1, xloc=xloc.bar_time, color=tf1_epaCol, style=getLineStyle(tf1_epaStyle), width=tf1_epaWidth)
                tf1_bullEpaLabel = label.new(_TimeTo, tf1_ph1, tf1_epaText + LABEL_SPACE, xloc=xloc.bar_time, style=label.style_none, size=getlabelSize('Normal'), textcolor=tf1_epaCol)
        if not na(tf1_bearEpaLine):
            line.set_x2(tf1_bearEpaLine, _TimeTo)
        if not na(tf1_bearEpaLabel):
            label.set_x(tf1_bearEpaLabel, _TimeTo)
        if not na(tf1_bearEpaLine) and high > tf1_bearEpaPrice:
            tf1_isPriceEfficient = True
            line.delete(tf1_bearEpaLine)
            if not na(tf1_bearEpaLabel):
                label.delete(tf1_bearEpaLabel)
        if not na(tf1_bullEpaLine):
            line.set_x2(tf1_bullEpaLine, _TimeTo)
        if not na(tf1_bullEpaLabel):
            label.set_x(tf1_bullEpaLabel, _TimeTo)
        if not na(tf1_bullEpaLine) and low < tf1_bullEpaPrice:
            tf1_isPriceEfficient = True
            line.delete(tf1_bullEpaLine)
            if not na(tf1_bullEpaLabel):
                label.delete(tf1_bullEpaLabel)
    tf1_isBearishMsu = tf1_ph0 < tf1_ph1 and tf1_pl0 < tf1_pl1 and (high > tf1_ph0) and (high < tf1_ph1)
    tf1_isBullishMsu = tf1_pl0 > tf1_pl1 and tf1_ph0 > tf1_ph1 and (low < tf1_pl0) and (low > tf1_pl1)
    plotshape(tf1_showMsu and tf1_isBearishMsu, color=color.red, style=shape.arrowdown, location=location.bottom, size=size.tiny, editable=False)
    plotshape(tf1_showMsu and tf1_isBullishMsu, color=color.lime, style=shape.arrowup, location=location.bottom, size=size.tiny, editable=False)
    tf1_bottomVtaBox: Persistent[Box] = na(Box)
    tf1_topVtaBox: Persistent[Box] = na(Box)
    tf1_bottomVtaBoxes: Persistent[list[Box]] = array.new_box(0)
    tf1_topVtaBoxes: Persistent[list[Box]] = array.new_box(0)
    tf1_isStrictBottomVta = tf1_pl1 < tf1_pl2 and tf1_pl0 < tf1_pl1 and (tf1_ph0 > tf1_ph1) and (close > tf1_ph0)
    tf1_isStrictTopVta = tf1_ph1 > tf1_ph2 and tf1_ph0 > tf1_ph1 and (tf1_pl0 < tf1_pl1) and (close < tf1_pl0)
    tf1_isBottomVta = tf1_isStrictBottomVta if tf1_strictVta else tf1_ph0 > tf1_ph1 and tf1_pl0 < tf1_pl1 and (close > tf1_ph0)
    tf1_isTopVta = tf1_isStrictTopVta if tf1_strictVta else tf1_pl0 < tf1_pl1 and tf1_ph0 > tf1_ph1 and (close < tf1_pl0)
    ex_usedVtaTimes: Persistent[list[int]] = array.new_int(0)
    if tf1_showVta:
        if tf1_isTopVta and (not array.includes(ex_usedVtaTimes, tf1_pl0Time)) and (tf1_ph0Time >= tf1_pl0Time):
            addToArray(ex_usedVtaTimes, tf1_pl0Time)
            addToArray(tf1_topVtaBoxes, box.new(tf1_pl0Time, tf1_ph0, _TimeTo, tf1_pl0, xloc=xloc.bar_time, border_color=tf1_vtaTopCol, bgcolor=TRANSPARENT, text=tf1_vtaText, text_color=tf1_vtaTopCol, text_halign=text.align_right, text_valign=text.align_top, text_size=getlabelSize('Small')))
        if tf1_isBottomVta and (not array.includes(ex_usedVtaTimes, tf1_ph0Time)) and (tf1_pl0Time >= tf1_ph0Time):
            addToArray(ex_usedVtaTimes, tf1_ph0Time)
            addToArray(tf1_bottomVtaBoxes, box.new(tf1_ph0Time, tf1_ph0, _TimeTo, tf1_pl0, xloc=xloc.bar_time, border_color=tf1_vtaBottomCol, bgcolor=TRANSPARENT, text=tf1_vtaText, text_color=tf1_vtaBottomCol, text_halign=text.align_right, text_valign=text.align_bottom, text_size=getlabelSize('Small')))
        if tf1_deleteVta == True:
            if array.size(tf1_topVtaBoxes) > 0:
                for i in pine_range(array.size(tf1_topVtaBoxes) - 1, 0, 1):
                    _box = array.get(tf1_topVtaBoxes, i)
                    _bottom_1 = _bottom(_box)
                    _top_1 = _top(_box)
                    if not na(_box) and high > _bottom_1 and (close < _top_1):
                        tf1_isBearishVta = True
                    _top_2 = _top(_box)
                    if not na(_box) and tf1_close > _top_2:
                        removeFromArray(tf1_topVtaBoxes, i)
                        box.delete(_box)
            if array.size(tf1_bottomVtaBoxes) > 0:
                for i in pine_range(array.size(tf1_bottomVtaBoxes) - 1, 0, 1):
                    _box = array.get(tf1_bottomVtaBoxes, i)
                    _top_1 = _top(_box)
                    _bottom_1 = _bottom(_box)
                    if not na(_box) and low < _top_1 and (close > _bottom_1):
                        tf1_isBullishVta = True
                    _bottom_2 = _bottom(_box)
                    if not na(_box) and tf1_close < _bottom_2:
                        removeFromArray(tf1_bottomVtaBoxes, i)
                        box.delete(_box)
    tf1_barcolor = na if not isUseTimeframe1 else tf1_bullishBullBarCol if tf1_structureDirection == 'bullish' and close > open else tf1_bullishBearBarCol if tf1_structureDirection == 'bullish' and close < open else tf1_bearishBullBarCol if tf1_structureDirection == 'bearish' and close > open else tf1_bearishBearBarCol if tf1_structureDirection == 'bearish' and close < open else na
    plotcandle(open if tf1_changeBarCol else na, high, low, close, title='Title', color=tf1_barcolor, wickcolor=tf1_barcolor, bordercolor=tf1_barcolor)
    tf1_isBullishPattern: bool = False
    tf1_isBearishPattern: bool = False
    tf1_isBearishPattern = tf1_ph2 > tf1_ph3 and tf1_ph1 > tf1_ph2 and (tf1_ph0 < tf1_ph1) and (tf1_pl1 < tf1_pl2) and (tf1_pl0 < tf1_pl1) and (close > tf1_pl0)
    tf1_isBullishPattern = tf1_pl2 < tf1_pl3 and tf1_pl1 < tf1_pl2 and (tf1_pl0 > tf1_pl1) and (tf1_ph1 > tf1_ph2) and (tf1_ph0 > tf1_ph1) and (close < tf1_ph0)
    plotshape(tf1_div8 and tf1_isBearishPattern and (tf1_structureDirection == 'bearish'), color=color.red, style=shape.xcross, location=location.bottom, size=size.tiny, editable=False)
    plotshape(tf1_div8 and tf1_isBullishPattern and (tf1_structureDirection == 'bullish'), color=color.lime, style=shape.xcross, location=location.bottom, size=size.tiny, editable=False)
    if barstate.islast and structure_show_table:
        _table: Table = table.new(structure_table_vertical + '_' + structure_table_horizontal, columns=6, rows=5, border_width=3)
        table.cell(_table, column=0, row=0, text='')
        table.cell(_table, column=0, row=1, text='Structure', text_color=color.white, bgcolor=color.new(color.black, 80))
        table.cell(_table, column=0, row=2, text='Effeciency', text_color=color.white, bgcolor=color.new(color.black, 80))
        table.cell(_table, column=0, row=3, text='MSU', text_color=color.white, bgcolor=color.new(color.black, 80))
        table.cell(_table, column=0, row=4, text='VTA', text_color=color.white, bgcolor=color.new(color.black, 80))
        if isUseTimeframe1:
            _timeframeString = timeframe.period if tf1_timeframe == '' else tf1_timeframe
            table.cell(_table, column=1, row=0, text=string.tostring(_timeframeString), text_color=color.green, bgcolor=color.new(color.green, 90))
            table.cell(_table, column=1, row=1, text=('Bullish ▲' if tf1_structureDirection == 'bullish' else 'Bearish ▼') if isUseTimeframe1 else 'NA', text_color=color.lime if tf1_structureDirection == 'bullish' else color.red)
            table.cell(_table, column=1, row=2, text=('Efficient ✓' if tf1_isPriceEfficient else 'Inefficient 𐄂') if isUseTimeframe1 else 'NA', text_color=color.lime if tf1_isPriceEfficient else color.red)
            table.cell(_table, column=1, row=3, text=('MSU ▲' if tf1_isBullishMsu else 'MSU ▼' if tf1_isBearishMsu else '') if isUseTimeframe1 else 'NA', text_color=color.lime if tf1_isBullishMsu else color.red)
            table.cell(_table, column=1, row=4, text=('VTA ▲' if tf1_isBullishVta else 'VTA ▼' if tf1_isBearishVta else '') if isUseTimeframe1 else 'NA', text_color=color.lime if tf1_isBullishVta else color.red)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
