"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_bool, cast_float, cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.lib import (
    array, bar_index, barstate, box, close, color, dayofmonth, dayofweek,
    extend, high, hour, label, line, low, math, minute, month, na, open, script, size, string,
    syminfo, ta, text, time, time_close, timeframe, timenow, timestamp, xloc, year
)
from pynecore.types import Box, Color, Label, Line, NA, Persistent, PersistentSeries, Series
from typing import Protocol, Any


__all__ = ['adr', 'adrHiLo', 'adrHigh', 'adrLow', 'calcDst', 'calcPsyLevels', 'calcPvsra', 'calcSessionStartEnd', 'cleanarr', 'countdownString', 'countdownStringSyd', 'drawLine', 'drawLineDO', 'drawOpenRange', 'drawPivot', 'drawSessionHiLo', 'drawSessionHiloLite', 'getPvsraFlagByColor', 'getdayOpen', 'msToHmsString', 'newBar', 'rLabel', 'rLabelLastBar', 'rLabelOffset', 'splitSessionString', 'timestampPreviousDayOfWeek', 'toPips', 'updateZones']


class _ProtocolCalcpvsra(Protocol):
    def __call__(self, pvsraVolume: Series[float], pvsraHigh: Series[float], pvsraLow: Series[float], pvsraClose: Series[float], pvsraOpen: Series[float], redVectorColor: Color, greenVectorColor: Color, violetVectorColor: Color, blueVectorColor: Color, darkGreyCandleColor: Color, lightGrayCandleColor: Color) -> Any: ...


class _ProtocolAdr(Protocol):
    def __call__(self, length: int, barsBack: int) -> Any: ...


class _ProtocolAdrhigh(Protocol):
    def __call__(self, adr__00000017__: Series[float], fromDo: bool) -> Any: ...


class _ProtocolAdrlow(Protocol):
    def __call__(self, adr__0000001a__: Series[float], fromDo: bool) -> Any: ...


class _ProtocolSplitsessionstring(Protocol):
    def __call__(self, sessXTime: str) -> Any: ...


class _ProtocolCalcsessionstartend(Protocol):
    def __call__(self, sessXTime: str, gmt: str) -> Any: ...


class _ProtocolDrawopenrange(Protocol):
    def __call__(self, sessXTime: str, sessXcol: Color, showOrX: bool, gmt: str) -> Any: ...


class _ProtocolDrawsessionhilo(Protocol):
    def __call__(self, sessXTime: str, showRectangleX: bool, showLabelX: bool, sessXcolLabel: Color, sessXLabel: str, gmt: str, sessionLineStyle: str) -> Any: ...


class _ProtocolCalcdst(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolTimestamppreviousdayofweek(Protocol):
    def __call__(self, previousDayOfWeek: str, hourOfDay: int, gmtOffset: str, oneWeekMillis: int) -> Any: ...


class _ProtocolGetdayopen(Protocol):
    def __call__(self, ) -> Any: ...


class _ProtocolNewbar(Protocol):
    def __call__(self, res: str) -> Any: ...


class _ProtocolTopips(Protocol):
    def __call__(self, val: Series[float]) -> Any: ...


class _ProtocolRlabel(Protocol):
    def __call__(self, ry: Series[float], rtext: str, rstyle: str, rcolor: Color, valid: bool, labelXOffset: Series[int]) -> Any: ...


class _ProtocolRlabeloffset(Protocol):
    def __call__(self, ry: Series[float], rtext: Series[str], rstyle: str, rcolor: Color, valid: bool, labelOffset: Series[int]) -> Any: ...


class _ProtocolRlabellastbar(Protocol):
    def __call__(self, ry: Series[float], rtext: Series[str], rstyle: str, rcolor: Color, valid: bool, labelXOffset: Series[int]) -> Any: ...


class _ProtocolDrawline(Protocol):
    def __call__(self, xSeries: Series[float], res: str, tag: str, xColor: Color, xStyle: str, xWidth: int, xExtend: str, isLabelValid: bool, xLabelOffset: Series[int], validTimeFrame: bool) -> Any: ...


class _ProtocolDrawlinedo(Protocol):
    def __call__(self, xSeries: Series[float], res: str, tag: str, xColor: Color, xStyle: str, xWidth: int, xExtend: str, isLabelValid: bool, xLabelOffset: Series[int], validTimeFrame: bool) -> Any: ...


class _ProtocolDrawpivot(Protocol):
    def __call__(self, pivotLevel: Series[float], res: str, tag: str, pivotColor: Color, pivotLabelColor: Color, pivotStyle: str, pivotWidth: int, pivotExtend: str, isLabelValid: bool, validTimeFrame: bool, levelStart: Series[int], pivotLabelXOffset: Series[int]) -> Any: ...


class _ProtocolGetpvsraflagbycolor(Protocol):
    def __call__(self, pvsraColor: Series[Color], redVectorColor: Color, greenVectorColor: Color, violetVectorColor: Color, blueVectorColor: Color, lightGrayCandleColor: Color) -> Any: ...


class _ProtocolUpdatezones(Protocol):
    def __call__(self, pvsra: Series[int], direction: int, boxArr: list[Box], maxlevels: int, pvsraHigh: Series[float], pvsraLow: Series[float], pvsraOpen: Series[float], pvsraClose: Series[float], transperancy: int, zoneupdatetype: str, zonecolor: Color, zonetype: str, borderwidth: int, coloroverride: bool, redVectorColor: Color, greenVectorColor: Color, violetVectorColor: Color, blueVectorColor: Color) -> Any: ...


class _ProtocolCleanarr(Protocol):
    def __call__(self, arr: list[Box]) -> Any: ...


class _ProtocolCalcpsylevels(Protocol):
    def __call__(self, oneWeekMillis: int, showPsylevels: bool, psyType: str, sydDST: Series[bool]) -> Any: ...


class _ProtocolAdrhilo(Protocol):
    def __call__(self, length: int, barsBack: int, fromDO: bool) -> Any: ...


class _ProtocolDrawsessionhilolite(Protocol):
    def __call__(self, sessXTime: str, showRectangleX: bool, showLabelX: bool, sessXcolLabel: Color, sessXLabel: str, gmt: str, sessionLineStyle: str, sessXcol: Color) -> Any: ...


class _ProtocolMstohmsstring(Protocol):
    def __call__(self, ms: Series[int]) -> Any: ...


class _ProtocolCountdownstring(Protocol):
    def __call__(self, openToday: Series[int], closeToday: Series[int], showMarketsWeekends: bool, oneDay: int) -> Any: ...


class _ProtocolCountdownstringsyd(Protocol):
    def __call__(self, sydOpenToday: Series[int], sydCloseToday: Series[int], showMarketsWeekends: bool, oneDay: int) -> Any: ...


calcPvsra: _ProtocolCalcpvsra = Exported()
adr: _ProtocolAdr = Exported()
adrHigh: _ProtocolAdrhigh = Exported()
adrLow: _ProtocolAdrlow = Exported()
splitSessionString: _ProtocolSplitsessionstring = Exported()
calcSessionStartEnd: _ProtocolCalcsessionstartend = Exported()
drawOpenRange: _ProtocolDrawopenrange = Exported()
drawSessionHiLo: _ProtocolDrawsessionhilo = Exported()
calcDst: _ProtocolCalcdst = Exported()
timestampPreviousDayOfWeek: _ProtocolTimestamppreviousdayofweek = Exported()
getdayOpen: _ProtocolGetdayopen = Exported()
newBar: _ProtocolNewbar = Exported()
toPips: _ProtocolTopips = Exported()
rLabel: _ProtocolRlabel = Exported()
rLabelOffset: _ProtocolRlabeloffset = Exported()
rLabelLastBar: _ProtocolRlabellastbar = Exported()
drawLine: _ProtocolDrawline = Exported()
drawLineDO: _ProtocolDrawlinedo = Exported()
drawPivot: _ProtocolDrawpivot = Exported()
getPvsraFlagByColor: _ProtocolGetpvsraflagbycolor = Exported()
updateZones: _ProtocolUpdatezones = Exported()
cleanarr: _ProtocolCleanarr = Exported()
calcPsyLevels: _ProtocolCalcpsylevels = Exported()
adrHiLo: _ProtocolAdrhilo = Exported()
drawSessionHiloLite: _ProtocolDrawsessionhilolite = Exported()
msToHmsString: _ProtocolMstohmsstring = Exported()
countdownString: _ProtocolCountdownstring = Exported()
countdownStringSyd: _ProtocolCountdownstringsyd = Exported()


@script.library('Traders_Reality_Lib', na_bool=True)
def main():
    @export
    def calcPvsra(pvsraVolume: Series[float], pvsraHigh: Series[float], pvsraLow: Series[float], pvsraClose: Series[float], pvsraOpen: Series[float], redVectorColor: Color, greenVectorColor: Color, violetVectorColor: Color, blueVectorColor: Color, darkGreyCandleColor: Color, lightGrayCandleColor: Color):
        averageVolume: float = math.sum(pvsraVolume[1], 10) / 10.0
        volumeSpread: Series[float] = pvsraVolume * (pvsraHigh - pvsraLow)
        highestVolumeSpread: float = ta.highest(volumeSpread[1], 10)
        pvsraColor: Color = na(Color)
        alertFlag: bool = False
        if pvsraVolume >= 2 * averageVolume or volumeSpread >= highestVolumeSpread:
            pvsraColor = greenVectorColor if pvsraClose > pvsraOpen else redVectorColor
            alertFlag = True
        elif pvsraVolume >= 1.5 * averageVolume:
            pvsraColor = blueVectorColor if pvsraClose > pvsraOpen else violetVectorColor
            alertFlag = True
        else:
            pvsraColor = lightGrayCandleColor if pvsraClose > pvsraOpen else darkGreyCandleColor
            alertFlag = False
        return (pvsraColor, alertFlag, averageVolume, volumeSpread, highestVolumeSpread)

    @export
    def adr(length: int, barsBack: int):
        trueRange: Series = high - low if na(high[1]) else math.max(math.max(high - low, math.abs(high - close[1])), math.abs(low - close[1]))
        return ta.sma(trueRange[barsBack], length)

    @export
    def adrHigh(adr__00000017__: Series[float], fromDo: bool):
        retVal: float = 0.0
        if not fromDo:
            retVal = low + adr__00000017__ if high - low < adr__00000017__ else low + adr__00000017__ if close >= open else high
        else:
            retVal = open + adr__00000017__
        return retVal

    @export
    def adrLow(adr__0000001a__: Series[float], fromDo: bool):
        retVal: float = 0.0
        if not fromDo:
            retVal = high - adr__0000001a__ if high - low < adr__0000001a__ else low if close >= open else high - adr__0000001a__
        else:
            retVal = open - adr__0000001a__
        return retVal

    @export
    def splitSessionString(sessXTime: str):
        times: str = array.get(string.split(sessXTime, ':'), 0)
        startTime: str = array.get(string.split(times, '-'), 0)
        endTime: str = array.get(string.split(times, '-'), 1)
        startTimeChars: list[str] = string.split(startTime, '')
        endTimeChars: list[str] = string.split(endTime, '')
        startHour: str = array.get(startTimeChars, 0) + array.get(startTimeChars, 1)
        startMin: str = array.get(startTimeChars, 2) + array.get(startTimeChars, 3)
        endHour: str = array.get(endTimeChars, 0) + array.get(endTimeChars, 1)
        endMin: str = array.get(endTimeChars, 2) + array.get(endTimeChars, 3)
        return (startHour, startMin, endHour, endMin)

    @export
    def calcSessionStartEnd(sessXTime: str, gmt: str):
        startHour, startMin, endHour, endMin = splitSessionString(sessXTime)
        targetstartTimeX = timestamp(gmt, year, month, dayofmonth, math.round(string.tonumber(startHour)), math.round(string.tonumber(startMin)), 0)
        targetendTimeX = timestamp(gmt, year, month, dayofmonth, math.round(string.tonumber(endHour)), math.round(string.tonumber(endMin)), 0)
        time_now = timestamp(year, month, dayofmonth, hour, minute, 0)
        midnight_exchange = timestamp(year, month, dayofmonth, 0, 0, 0)
        oneDay: int = 24 * 60 * 60 * 1000
        adjusted: bool = False
        if gmt == 'GMT+0':
            if math.round(string.tonumber(startHour)) > math.round(string.tonumber(endHour)):
                if time_now - targetstartTimeX >= 0:
                    targetendTimeX = targetendTimeX + oneDay
                    adjusted = True
        if gmt == 'GMT+1':
            if math.round(string.tonumber(startHour)) == 0:
                startHour = '24'
            if math.round(string.tonumber(endHour)) == 0:
                endHour = '24'
            if math.round(string.tonumber(startHour)) - 1 > math.round(string.tonumber(endHour)) - 1:
                if time_now - targetstartTimeX >= 0:
                    targetendTimeX = targetendTimeX + oneDay
                    adjusted = True
        if targetstartTimeX < midnight_exchange and midnight_exchange < targetendTimeX and (not adjusted):
            targetendTimeX = targetendTimeX + oneDay
        return (targetstartTimeX, targetendTimeX)

    @export
    def drawOpenRange(sessXTime: str, sessXcol: Color, showOrX: bool, gmt: str):
        __block_result__ = na
        if showOrX:
            hi: Persistent = NA(float)
            lo: Persistent = NA(float)
            hiLoBox: Persistent[Box] = na(Box)
            session__ren__: Series = time(timeframe.period, sessXTime, gmt)
            newTF: bool = cast_bool(session__ren__) and (not session__ren__[1])
            __block_result_1__ = na
            if newTF:
                targetstartTimeX, targetendTimeX = calcSessionStartEnd(sessXTime, gmt)
                sessionDuration = math.round(math.abs(time - targetendTimeX) / (timeframe.multiplier * 60 * 1000))
                hi = high
                lo = low
                hiLoBox = box.new(bar_index, hi, bar_index if timeframe.multiplier == 1 else bar_index + sessionDuration, lo, border_color=na, bgcolor=sessXcol)
                __block_result_1__ = NA(int)
            else:
                if timeframe.multiplier == 1 and (na(session__ren__[1]) and (not na(session__ren__)) or session__ren__[1] < session__ren__):
                    box.set_right(hiLoBox, bar_index + 1)
                __block_result_1__ = NA(int)
            __block_result__ = __block_result_1__
        return __block_result__

    @export
    def drawSessionHiLo(sessXTime: str, showRectangleX: bool, showLabelX: bool, sessXcolLabel: Color, sessXLabel: str, gmt: str, sessionLineStyle: str):
        __block_result_2__ = na
        if showRectangleX:
            hi: PersistentSeries = cast_float(0)
            lo: PersistentSeries = cast_float(10000000000.0)
            lineT: PersistentSeries[Line] = na(Line)
            lineB: PersistentSeries[Line] = na(Line)
            lineLabel: PersistentSeries[Label] = na(Label)
            session__ren__: Series = time(timeframe.period, sessXTime, gmt)
            sessLineStyleX = line.style_solid if sessionLineStyle == 'Solid' else line.style_dashed
            newTF: bool = cast_bool(session__ren__) and (not session__ren__[1])
            hi = high if newTF else math.max(high, hi[1]) if cast_bool(session__ren__) else hi[1]
            lo = low if newTF else math.min(low, lo[1]) if cast_bool(session__ren__) else lo[1]
            __block_result_3__ = na
            if newTF:
                beginIndex = bar_index
                targetstartTimeX, targetendTimeX = calcSessionStartEnd(sessXTime, gmt)
                sessionDuration = math.round(math.abs(time - targetendTimeX) / (timeframe.multiplier * 60 * 1000))
                lineT = line.new(beginIndex, hi, bar_index if timeframe.multiplier == 1 else bar_index + sessionDuration, hi, xloc=xloc.bar_index, style=sessLineStyleX, color=sessXcolLabel)
                lineB = line.new(beginIndex, lo, bar_index if timeframe.multiplier == 1 else bar_index + sessionDuration, lo, xloc=xloc.bar_index, style=sessLineStyleX, color=sessXcolLabel)
                line.delete(lineT[1])
                line.delete(lineB[1])
                if showLabelX:
                    lineLabel = label.new(beginIndex, hi, sessXLabel, xloc=xloc.bar_index, textcolor=sessXcolLabel, style=label.style_none, size=size.normal, textalign=text.align_right)
                    label.delete(lineLabel[1])
                __block_result_3__ = NA(int)
            else:
                if na(session__ren__[1]) and (not na(session__ren__)) or session__ren__[1] < session__ren__:
                    if timeframe.multiplier == 1:
                        line.set_x2(lineT, bar_index + 1)
                        line.set_x2(lineB, bar_index + 1)
                    line.set_y1(lineT, hi)
                    line.set_y2(lineT, hi)
                    line.set_y1(lineB, lo)
                    line.set_y2(lineB, lo)
                    if showLabelX and (not na(lineLabel)):
                        label.set_y(lineLabel, hi)
                __block_result_3__ = NA(int)
            __block_result_2__ = __block_result_3__
        return __block_result_2__

    @export
    def calcDst():
        previousSunday: int = dayofmonth - dayofweek + 1
        nyDST: bool = na(bool)
        ukDST: bool = na(bool)
        sydDST: bool = na(bool)
        if month < 3 or month > 11:
            nyDST = False
            ukDST = False
            sydDST = True
        elif month > 4 and month < 10:
            nyDST = True
            ukDST = True
            sydDST = False
        elif month == 3:
            nyDST = previousSunday >= 8
            ukDST = previousSunday >= 24
            sydDST = True
        elif month == 4:
            nyDST = True
            ukDST = True
            sydDST = previousSunday <= 0
        elif month == 10:
            nyDST = True
            ukDST = previousSunday <= 24
            sydDST = previousSunday >= 0
        else:
            nyDST = previousSunday <= 0
            ukDST = False
            sydDST = True
        return (nyDST, ukDST, sydDST)

    @export
    def timestampPreviousDayOfWeek(previousDayOfWeek: str, hourOfDay: int, gmtOffset: str, oneWeekMillis: int):
        dayofweekOffset: int = na(int)
        previousDayOfMonth: int = na(int)
        psySessionStartTime: int = na(int)
        returnValue: int = na(int)
        if previousDayOfWeek == 'Monday':
            dayofweekOffset = (dayofweek(time, gmtOffset) - 1 + 6) % 7
        if previousDayOfWeek == 'Saturday':
            dayofweekOffset = (dayofweek(time, gmtOffset) - 1 + 1) % 7
        previousDayOfMonth = dayofmonth(time, gmtOffset) - dayofweekOffset
        hour_1 = hour(time, gmtOffset)
        hour_2 = hour(time, gmtOffset)
        if dayofweekOffset == 0 and gmtOffset == 'GMT' and (hourOfDay >= hour_1) and (hourOfDay != 0):
            returnValue = timestamp(gmtOffset, year, month, previousDayOfMonth, hourOfDay, 0, 0) - oneWeekMillis
        elif dayofweekOffset == 0 and gmtOffset == 'GMT+1' and (hourOfDay - 1 >= hour_2):
            returnValue = timestamp(gmtOffset, year, month, previousDayOfMonth, hourOfDay, 0, 0) - oneWeekMillis
        else:
            returnValue = timestamp(gmtOffset, year, month, previousDayOfMonth, hourOfDay, 0, 0)
        return returnValue

    @export
    def getdayOpen():
        in_sessionDly = time('D', '24x7')
        isDly: bool = cast_bool(ta.change(time('D')))
        dlyOpen: Persistent = NA(float)
        if isDly:
            dlyOpen = open
        return dlyOpen

    @export
    def newBar(res: str):
        return ta.change(time(res)) != 0

    @export
    def toPips(val: Series[float]):
        pipSizeCalc = syminfo.mintick * (10 if syminfo.type == 'forex' else 1)
        returnVal = val / pipSizeCalc
        return returnVal

    @export
    def rLabel(ry: Series[float], rtext: str, rstyle: str, rcolor: Color, valid: bool, labelXOffset: Series[int]):
        rLabel__000000a9__: PersistentSeries[Label] = na(Label)
        if valid and barstate.isrealtime:
            rLabel__000000a9__ = label.new(x=labelXOffset, y=ry, text=rtext, xloc=xloc.bar_time, style=rstyle, textcolor=rcolor, textalign=text.align_right)
            label.delete(rLabel__000000a9__[1])
        return rLabel__000000a9__

    @export
    def rLabelOffset(ry: Series[float], rtext: Series[str], rstyle: str, rcolor: Color, valid: bool, labelOffset: Series[int]):
        __block_result_4__ = na
        if valid and barstate.isrealtime:
            rLabel__000000ad__: Series = label.new(x=labelOffset, y=ry, text=rtext, xloc=xloc.bar_time, style=rstyle, textcolor=rcolor, textalign=text.align_right)
            __block_result_4__ = label.delete(rLabel__000000ad__[1])
        return __block_result_4__

    @export
    def rLabelLastBar(ry: Series[float], rtext: Series[str], rstyle: str, rcolor: Color, valid: bool, labelXOffset: Series[int]):
        rLabel__000000b3__: PersistentSeries[Label] = na(Label)
        if valid and barstate.islast:
            rLabel__000000b3__ = label.new(x=labelXOffset, y=ry, text=rtext, xloc=xloc.bar_time, style=rstyle, textcolor=rcolor, textalign=text.align_right)
            label.delete(rLabel__000000b3__[1])
        return rLabel__000000b3__

    @export
    def drawLine(xSeries: Series[float], res: str, tag: str, xColor: Color, xStyle: str, xWidth: int, xExtend: str, isLabelValid: bool, xLabelOffset: Series[int], validTimeFrame: bool):
        xLine: PersistentSeries[Line] = na(Line)
        newBar_1 = newBar(res)
        if validTimeFrame and newBar_1:
            xLine = line.new(bar_index, xSeries, bar_index + 1, xSeries, extend=xExtend, color=xColor, style=xStyle, width=xWidth)
            line.delete(xLine[1])
        newBar_2 = newBar(res)
        if not na(xLine) and (not newBar_2):
            line.set_x2(xLine, bar_index)
            line.set_y1(xLine, xSeries)
            line.set_y2(xLine, xSeries)
        __block_result_5__ = na
        if isLabelValid:
            xLabel: Series = label.new(xLabelOffset, xSeries, tag, xloc=xloc.bar_time, style=label.style_none, textcolor=xColor)
            __block_result_5__ = label.delete(xLabel[1])
        return __block_result_5__

    @export
    def drawLineDO(xSeries: Series[float], res: str, tag: str, xColor: Color, xStyle: str, xWidth: int, xExtend: str, isLabelValid: bool, xLabelOffset: Series[int], validTimeFrame: bool):
        xLine: PersistentSeries[Line] = na(Line)
        if newBar(res) and validTimeFrame:
            line.set_x2(xLine, bar_index)
            line.set_extend(xLine, extend.none)
            xLine = line.new(bar_index, xSeries, bar_index, xSeries, extend=xExtend, color=xColor, style=xStyle, width=xWidth)
            line.delete(xLine[1])
        if not na(xLine) and line.get_x2(xLine) != bar_index:
            line.set_x2(xLine, bar_index)
        __block_result_6__ = na
        if isLabelValid:
            xLabel: Series = label.new(xLabelOffset, xSeries, tag, xloc=xloc.bar_time, style=label.style_none, textcolor=xColor)
            __block_result_6__ = label.delete(xLabel[1])
        return __block_result_6__

    @export
    def drawPivot(pivotLevel: Series[float], res: str, tag: str, pivotColor: Color, pivotLabelColor: Color, pivotStyle: str, pivotWidth: int, pivotExtend: str, isLabelValid: bool, validTimeFrame: bool, levelStart: Series[int], pivotLabelXOffset: Series[int]):
        pivotLine: PersistentSeries[Line] = na(Line)
        newBar_1 = newBar(res)
        if validTimeFrame and newBar_1:
            pivotLine = line.new(bar_index, pivotLevel, bar_index, pivotLevel, extend=pivotExtend, color=pivotColor, style=pivotStyle, width=pivotWidth)
            line.delete(pivotLine[1])
        newBar_2 = newBar(res)
        if not na(pivotLine) and (not newBar_2):
            line.set_x2(pivotLine, bar_index)
            line.set_y1(pivotLine, pivotLevel)
            line.set_y2(pivotLine, pivotLevel)
        if isLabelValid:
            pivotLabel: Series = label.new(pivotLabelXOffset, pivotLevel, tag, xloc=xloc.bar_time, style=label.style_none, textcolor=pivotLabelColor, textalign=text.align_right)
            label.delete(pivotLabel[1])
        if not barstate.islast:
            line.set_x2(pivotLine, x=bar_index)
        else:
            line.set_xloc(pivotLine, levelStart, time_close + 1 * 86400000, xloc=xloc.bar_time)
        return pivotLine

    @export
    def getPvsraFlagByColor(pvsraColor: Series[Color], redVectorColor: Color, greenVectorColor: Color, violetVectorColor: Color, blueVectorColor: Color, lightGrayCandleColor: Color):
        __block_result_7__ = na
        if pvsraColor == greenVectorColor:
            __block_result_7__ = 3
        elif pvsraColor == redVectorColor:
            __block_result_7__ = -3
        elif pvsraColor == blueVectorColor:
            __block_result_7__ = 2
        elif pvsraColor == violetVectorColor:
            __block_result_7__ = -2
        elif pvsraColor == lightGrayCandleColor:
            __block_result_7__ = 1
        else:
            __block_result_7__ = -1
        pvsra = __block_result_7__
        return pvsra

    @export
    def updateZones(pvsra: Series[int], direction: int, boxArr: list[Box], maxlevels: int, pvsraHigh: Series[float], pvsraLow: Series[float], pvsraOpen: Series[float], pvsraClose: Series[float], transperancy: int, zoneupdatetype: str, zonecolor: Color, zonetype: str, borderwidth: int, coloroverride: bool, redVectorColor: Color, greenVectorColor: Color, violetVectorColor: Color, blueVectorColor: Color):
        levelclose: Series = pvsraClose[1]
        levelopen = pvsraOpen[1]
        levelhigh = pvsraHigh[1]
        levellow = pvsraLow[1]
        levelChanged = levelclose != levelclose[1]
        length = array.size(boxArr)
        CUColorBG = color.new(greenVectorColor, transperancy)
        CDColorBG = color.new(redVectorColor, transperancy)
        AUColorBG = color.new(blueVectorColor, transperancy)
        ADColorBG = color.new(violetVectorColor, transperancy)
        __block_result_8__ = na
        if coloroverride:
            __block_result_8__ = zonecolor
        elif pvsra == 2:
            __block_result_8__ = AUColorBG
        elif pvsra == -2:
            __block_result_8__ = ADColorBG
        elif pvsra == 3:
            __block_result_8__ = CUColorBG
        elif pvsra == -3:
            __block_result_8__ = CDColorBG
        else:
            __block_result_8__ = na
        bgColor: Series = __block_result_8__
        if pvsra[1] < -1 or pvsra[1] > 1:
            __block_result_9__ = na
            if levelclose > levelopen:
                __block_result_9__ = levelhigh if zonetype == 'Body with wicks' else levelclose
            else:
                __block_result_9__ = levelhigh if zonetype == 'Body with wicks' else levelopen
            top = __block_result_9__
            __block_result_10__ = na
            if levelclose > levelopen:
                __block_result_10__ = levellow if zonetype == 'Body with wicks' else levelopen
            else:
                __block_result_10__ = levellow if zonetype == 'Body with wicks' else levelclose
            bottom = __block_result_10__
            array.unshift(boxArr, box.new(left=bar_index[1], top=top, right=bar_index, bottom=bottom, extend=extend.right, bgcolor=bgColor[1], border_width=borderwidth, border_color=color.rgb(255, 255, 255, 80)))
            length = length + 1
        if length > 0:
            for i in pine_range(0, length - 1, 1):
                valbox = array.get(boxArr, i)
                if not na(valbox):
                    valbottom = box.get_bottom(valbox)
                    valtop = box.get_top(valbox)
                    if direction == 1:
                        if pvsraClose >= valtop or pvsraHigh >= valtop:
                            box.delete(array.get(boxArr, i))
                            array.set(boxArr, i, na)
                        elif pvsraHigh > valbottom and pvsraHigh < valtop and (zoneupdatetype == 'Body with wicks'):
                            box.set_bottom(array.get(boxArr, i), pvsraHigh)
                        elif pvsraClose > valbottom and pvsraClose < valtop and (zoneupdatetype == 'Body with wicks'):
                            box.set_bottom(array.get(boxArr, i), pvsraClose)
                    elif direction == 0:
                        if pvsraClose <= valbottom or pvsraLow <= valbottom:
                            box.delete(array.get(boxArr, i))
                            array.set(boxArr, i, na)
                        elif pvsraLow > valbottom and pvsraLow < valtop and (zoneupdatetype == 'Body with wicks'):
                            box.set_top(array.get(boxArr, i), pvsraLow)
                        elif pvsraClose > valbottom and pvsraClose < valtop and (zoneupdatetype == 'Body with wicks'):
                            box.set_top(array.get(boxArr, i), pvsraClose)
        __block_result_11__ = na
        if length > maxlevels:
            val: Box = array.get(boxArr, length - 1)
            if not na(val):
                box.delete(val)
            __block_result_11__ = array.pop(boxArr)
        return __block_result_11__

    @export
    def cleanarr(arr: list[Box]):
        ret: bool = True
        if array.size(arr) > 0:
            __loop_1__ = pine_loop(0, 1)
            while __loop_1__.step(array.size(arr) - 1):
                i = __loop_1__.value
                if na(array.get(arr, i)):
                    array.remove(arr, i)
                else:
                    ret = False
                break
        return ret

    @export
    def calcPsyLevels(oneWeekMillis: int, showPsylevels: bool, psyType: str, sydDST: Series[bool]):
        psySession: int = na(int)
        psySessionStartDay: int = na(int)
        psySessionStartTime: int = na(int)
        inPsySession: Series[bool] = na(bool)
        psyHi: Series[float] = na(float)
        psyLo: Series[float] = na(float)
        psyHiLabel: str = na(str)
        psyLoLabel: str = na(str)
        __block_result_12__ = (na, na, na, na, na)
        if showPsylevels:
            if psyType == 'crypto':
                if sydDST:
                    psySession = time('240', '2200-0600:1', 'GMT+1')
                    psySessionStartTime = timestampPreviousDayOfWeek('Saturday', 22, 'GMT+1', oneWeekMillis)
                else:
                    psySession = time('240', '2200-0600:1', 'GMT')
                    psySessionStartTime = timestampPreviousDayOfWeek('Saturday', 22, 'GMT', oneWeekMillis)
            else:
                psySession = time('240', '0000-0800:2', 'GMT')
                psySessionStartTime = timestampPreviousDayOfWeek('Monday', 0, 'GMT', oneWeekMillis)
            inPsySession = False if na(psySession) else True
            if inPsySession:
                if not inPsySession[1]:
                    psyHi = high
                    psyLo = low
                    psyHiLabel = 'Psy-Hi calculating...'
                    psyLoLabel = 'Psy-Lo calculating...'
                else:
                    psyHi = math.max(high, psyHi[1])
                    psyLo = math.min(low, psyLo[1])
                    psyHiLabel = 'Psy-Hi calculating...'
                    psyLoLabel = 'Psy-Lo calculating...'
            else:
                psyHi = psyHi[1]
                psyLo = psyLo[1]
                psyHiLabel = 'Psy-Hi'
                psyLoLabel = 'Psy-Lo'
            __block_result_12__ = (psyHi, psyLo, psyHiLabel, psyLoLabel, psySessionStartTime)
        return __block_result_12__

    @export
    def adrHiLo(length: int, barsBack: int, fromDO: bool):
        adr__0000015f__: float = 0.0
        adrHigh__0000015f__: float = 0.0
        adrLow__0000015f__: float = 0.0
        trueRange: Series = high - low if na(high[1]) else math.max(math.max(high - low, math.abs(high - close[1])), math.abs(low - close[1]))
        adr__0000015f__ = ta.sma(trueRange[barsBack], length)
        if not fromDO:
            adrHigh__0000015f__ = low + adr__0000015f__ if high - low < adr__0000015f__ else low + adr__0000015f__ if close >= open else high
        else:
            adrHigh__0000015f__ = open + adr__0000015f__
        if not fromDO:
            adrLow__0000015f__ = high - adr__0000015f__ if high - low < adr__0000015f__ else low if close >= open else high - adr__0000015f__
        else:
            adrLow__0000015f__ = open - adr__0000015f__
        return (adr__0000015f__, adrHigh__0000015f__, adrLow__0000015f__)

    @export
    def drawSessionHiloLite(sessXTime: str, showRectangleX: bool, showLabelX: bool, sessXcolLabel: Color, sessXLabel: str, gmt: str, sessionLineStyle: str, sessXcol: Color):
        __block_result_13__ = na
        if showRectangleX:
            hi: PersistentSeries = cast_float(0)
            lo: PersistentSeries = cast_float(10000000000.0)
            line_t: Persistent[Line] = na(Line)
            line_b: Persistent[Line] = na(Line)
            line_m: Persistent[Line] = na(Line)
            line_label: Persistent[Label] = na(Label)
            hiLoBox: Persistent[Box] = na(Box)
            currentTime = timestamp(gmt, year, month, dayofmonth, hour, minute, 0)
            session__ren__: Series = time(timeframe.period, sessXTime, gmt)
            sessLineStyleX = line.style_solid if sessionLineStyle == 'Solid' else line.style_dashed
            newTF: bool = cast_bool(session__ren__) and (not session__ren__[1])
            hi = high if newTF else math.max(high, hi[1]) if cast_bool(session__ren__) else hi[1]
            lo = low if newTF else math.min(low, lo[1]) if cast_bool(session__ren__) else lo[1]
            targetstartTimeX, targetendTimeX = calcSessionStartEnd(sessXTime, gmt)
            __block_result_14__ = na
            if newTF:
                beginIndex = bar_index
                sessionDuration = math.round(math.abs(time - targetendTimeX) / (timeframe.multiplier * 60 * 1000))
                line_t = line.new(beginIndex, hi, bar_index if timeframe.multiplier == 1 else bar_index + sessionDuration, hi, xloc=xloc.bar_index, style=sessLineStyleX, color=sessXcolLabel)
                line_b = line.new(beginIndex, lo, bar_index if timeframe.multiplier == 1 else bar_index + sessionDuration, lo, xloc=xloc.bar_index, style=sessLineStyleX, color=sessXcolLabel)
                line_m = line.new(beginIndex, (hi + lo) / 2, bar_index if timeframe.multiplier == 1 else bar_index + sessionDuration, (hi + lo) / 2, xloc=xloc.bar_index, style=sessLineStyleX, color=sessXcolLabel)
                hiLoBox = box.new(bar_index, hi, bar_index if timeframe.multiplier == 1 else bar_index + sessionDuration, lo, border_color=na, bgcolor=sessXcol)
                if showLabelX:
                    line_label = label.new(beginIndex, hi, sessXLabel, xloc=xloc.bar_index, textcolor=sessXcolLabel, style=label.style_none, size=size.normal, textalign=text.align_right)
                __block_result_14__ = NA(int)
            else:
                if na(session__ren__[1]) and (not na(session__ren__)) or session__ren__[1] < session__ren__:
                    if timeframe.multiplier == 1:
                        line.set_x2(line_t, bar_index + 1)
                        line.set_x2(line_b, bar_index + 1)
                        line.set_x2(line_m, bar_index + 1)
                        box.set_right(hiLoBox, bar_index + 1)
                    line.set_y1(line_t, hi)
                    line.set_y2(line_t, hi)
                    line.set_y1(line_b, lo)
                    line.set_y2(line_b, lo)
                    line.set_y1(line_m, (hi + lo) / 2)
                    line.set_y2(line_m, (hi + lo) / 2)
                    box.set_top(hiLoBox, hi)
                    box.set_bottom(hiLoBox, lo)
                    if showLabelX and (not na(line_label)):
                        label.set_y(line_label, hi)
                __block_result_14__ = NA(int)
            __block_result_13__ = __block_result_14__
        return __block_result_13__

    @export
    def msToHmsString(ms: Series[int]):
        hours = cast_int(ms / (60 * 60 * 1000))
        minutes = cast_int(ms - hours * 60 * 60 * 1000 / (60 * 1000))
        minutesString = '0' + string.tostring(minutes) if minutes <= 9 else string.tostring(minutes)
        return string.tostring(hours) + ':' + minutesString

    @export
    def countdownString(openToday: Series[int], closeToday: Series[int], showMarketsWeekends: bool, oneDay: int):
        countdownString__000001a3__: str = na(str)
        dayofweek_1 = dayofweek(timenow, 'GMT')
        if dayofweek(timenow, 'GMT') == 1 and (not showMarketsWeekends):
            countdown = openToday + oneDay - timenow
            countdownString__000001a3__ = msToHmsString(countdown)
        elif dayofweek(timenow, 'GMT') >= 2 and dayofweek_1 <= 5 and (not showMarketsWeekends) or showMarketsWeekends:
            if timenow < openToday:
                countdown = openToday - timenow
                countdownString__000001a3__ = msToHmsString(countdown)
            elif timenow >= openToday and timenow < closeToday:
                countdownString__000001a3__ = 'Open'
            else:
                countdown = openToday + oneDay - timenow
                countdownString__000001a3__ = msToHmsString(countdown)
        elif dayofweek(timenow, 'GMT') == 6 and (not showMarketsWeekends):
            if timenow < openToday:
                countdown = openToday - timenow
                countdownString__000001a3__ = msToHmsString(countdown)
            elif timenow >= openToday and timenow < closeToday:
                countdownString__000001a3__ = 'Open'
            else:
                countdown = openToday + 3 * oneDay - timenow
                countdownString__000001a3__ = msToHmsString(countdown)
        else:
            countdown = openToday + 2 * oneDay - timenow
            countdownString__000001a3__ = msToHmsString(countdown)
        return countdownString__000001a3__

    @export
    def countdownStringSyd(sydOpenToday: Series[int], sydCloseToday: Series[int], showMarketsWeekends: bool, oneDay: int):
        sydCountdownString: str = na(str)
        dayofweek_1 = dayofweek(timenow, 'GMT')
        if dayofweek(timenow, 'GMT') == 1 and (not showMarketsWeekends):
            if timenow < sydOpenToday:
                sydCountdown = sydOpenToday - timenow
                sydCountdownString = msToHmsString(sydCountdown)
            else:
                sydCountdownString = 'Open'
        elif dayofweek(timenow, 'GMT') >= 2 and dayofweek_1 <= 5 and (not showMarketsWeekends) or showMarketsWeekends:
            if timenow < sydCloseToday:
                sydCountdownString = 'Open'
            elif timenow >= sydCloseToday and timenow < sydOpenToday:
                sydCountdown = sydOpenToday - timenow
                sydCountdownString = msToHmsString(sydCountdown)
            else:
                sydCountdownString = 'Open'
        elif dayofweek(timenow, 'GMT') == 6 and (not showMarketsWeekends):
            if timenow < sydCloseToday:
                sydCountdownString = 'Open'
            else:
                sydCountdown = sydOpenToday + 2 * oneDay - timenow
                sydCountdownString = msToHmsString(sydCountdown)
        else:
            sydCountdown = sydOpenToday + oneDay - timenow
            sydCountdownString = msToHmsString(sydCountdown)
        return sydCountdownString


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
