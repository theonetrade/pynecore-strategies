"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from enum import StrEnum as Enum
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_export import Exported, export
from pynecore.core.pine_method import method, method_call
from pynecore.core.pine_udt import udt, udt_copy
from pynecore.lib import (
    array, bar_index, barmerge, barstate, box, chart, close, color, format,
    high, label, last_bar_time, line, low, map, math, matrix, na, nz, open, polyline, position,
    request, script, size, strategy, string, syminfo, ta, table, text, time, time_close, timeframe,
    xloc
)
from pynecore.types import Box, Color, Label, Line, Matrix, NA, Persistent, Polyline, Series
from pynecore.types.chart import ChartPoint
from typing import Protocol, Any
import lib.PineCoders.Time.v4 as pct


__all__ = ['FVG', 'IQZZ', 'OB', 'OBdraw', 'OTEstrat', 'OTEtimes', 'checkIfClosed', 'checkIfTraded', 'displacement', 'displacement__ren__', 'drawBos', 'drawFVG', 'drawMSS', 'equalLevels', 'equalLevelsDraw', 'getStrongHigh', 'getStrongLow', 'getTime', 'gradBoxes', 'invalidBlockCheck', 'invalidFVGcheck', 'isLastBar', 'labelLine', 'lastBarRejections', 'm2022', 'macros', 'macros__ren__', 'necessaryData', 'necessaryData__ren__', 'orderBlock', 'po3', 'po3data', 'quickTime', 'raidCoordinates', 'raidExitDrawings', 'rejectionBlocks', 'silverBullet', 'silverBulletDrawings', 'silverBulletLevels', 'silverBullet__ren__', 'strongPoints', 'sweeps', 'unicornExits', 'unicornModel']


@udt
class FVG:
    H: float = na(float)
    L: float = na(float)
    direction: str = na(str)
    T: int = na(int)
    fvgLabel: Label = na(Label)
    fvgLineTop: Line = na(Line)
    fvgLineBot: Line = na(Line)
    fvgBox: Box = na(Box)


@udt
class labelLine:
    lin: Line = na(Line)
    lab: Label = na(Label)


@udt
class orderBlock:
    orderBlockData: list[float] = na(list)
    orderBlockBox: Box = na(Box)
    vioCount: int = 0
    traded: bool = False
    status: str = 'OB'
    orderBlockLab: Label = na(Label)


@udt
class strongPoints:
    price: float = na(float)
    timeAtprice: int = na(int)
    strongPointLabel: Label = na(Label)
    strongPointLine: Line = na(Line)
    overlayLine: Line = na(Line)
    overlayLine2: Line = na(Line)


@udt
class displacement__ren__:
    highPrice: float = na(float)
    lowPrice: float = na(float)
    timeAtPrice: int = na(int)
    displacementBox: Box = na(Box)
    displacementLab: Label = na(Label)


@udt
class po3data:
    dHigh: float = na(float)
    dLow: float = na(float)
    dOpen: float = na(float)
    dClose: float = na(float)
    po3box: Box = na(Box)
    po3line: list[Line] = na(list)
    po3Labels: list[Label] = na(list)


@udt
class macros__ren__:
    sessions: list[bool] = na(list)
    prices: Matrix[float] = na(Matrix)
    sessionTimes: list[str] = na(list)
    sessionLines: Matrix[Line] = na(Matrix)


@udt
class OTEtimes:
    upTimes: list[int] = na(list)
    dnTimes: list[int] = na(list)
    tpLineLong: Line = na(Line)
    tpLabelLong: Label = na(Label)
    slLineLong: Line = na(Line)
    slLabelLong: Label = na(Label)
    tpLineShort: Line = na(Line)
    tpLabelShort: Label = na(Label)
    slLineShort: Line = na(Line)
    slLabelShort: Label = na(Label)


@udt
class sweeps:
    upSweeps: Matrix[float] = na(Matrix)
    dnSweeps: Matrix[float] = na(Matrix)
    upSweepDrawings: list[Box] = na(list)
    dnSweepDrawings: list[Box] = na(list)


@udt
class raidExitDrawings:
    tpLine: Line = na(Line)
    tpLabel: Label = na(Label)
    slLine: Line = na(Line)
    slLabel: Label = na(Label)


@udt
class m2022:
    mTime: int = na(int)
    mIndex: int = na(int)
    mEntryDistance: float = na(float)
    mEntry: float = na(float)
    fvgHigh: float = na(float)
    fvgLow: float = na(float)
    longFVGentryBox: Box = na(Box)
    shortFVGentryBox: Box = na(Box)
    line50P: Line = na(Line)
    line100P: Line = na(Line)
    line0P: Line = na(Line)
    label50P: Label = na(Label)
    label100P: Label = na(Label)
    label0P: Label = na(Label)
    sweepData: list[float] = na(list)


@udt
class silverBullet__ren__:
    session__ren__: bool = na(bool)
    sessionStr: str = na(str)
    sessionBias: str = na(str)
    sessionHigh: float = _dataclass_field(default_factory=lambda: high)
    sessionLow: float = _dataclass_field(default_factory=lambda: low)
    sessionFVG: float = na(float)
    sessionFVGdraw: Box = na(Box)
    traded: bool = False
    tp: float = na(float)
    sl: float = na(float)
    sessionDraw: Box = na(Box)
    sessionDrawLabel: Label = na(Label)


@udt
class silverBulletDrawings:
    tpLine: Line = na(Line)
    tpLabel: Label = na(Label)
    slLine: Line = na(Line)
    slLabel: Label = na(Label)


@udt
class unicornModel:
    hPoint: ChartPoint = na(ChartPoint)
    hPoint2: ChartPoint = na(ChartPoint)
    hPoint3: ChartPoint = na(ChartPoint)
    breakerBlock: Box = na(Box)
    FVG: Box = na(Box)
    topBlock: float = na(float)
    botBlock: float = na(float)
    startBlock: int = na(int)
    includes: list[int] = na(list)
    entry: float = na(float)
    tpLine: Line = na(Line)
    tpLabel: Label = na(Label)
    slLine: Line = na(Line)
    slLabel: Label = na(Label)


@udt
class rejectionBlocks:
    rejectionPoint: ChartPoint = na(ChartPoint)
    bodyPrice: float = na(float)
    rejectionBox: Box = na(Box)
    rejectionLabel: Label = na(Label)


@udt
class equalLevelsDraw:
    connector: Line = na(Line)
    connectorLab: Label = na(Label)
    levels: list[float] = na(list)
    times: list[int] = na(list)
    startTime: int = na(int)
    radiate: list[Label] = na(list)


@udt
class necessaryData__ren__:
    highArr: list[float] = na(list)
    lowArr: list[float] = na(list)
    timeArr: list[int] = na(list)
    logArr: list[float] = na(list)
    signArr: list[float] = na(list)
    closeArr: list[float] = na(list)
    binaryTimeArr: list[int] = na(list)
    binaryCloseArr: list[float] = na(list)
    binaryOpenArr: list[float] = na(list)
    atrTFarr: list[float] = na(list)
    openArr: list[float] = na(list)


class unicornExits(Enum):
    sL = 'Swing Low'
    sH = 'Swing High'
    bFVG = 'FVG/BB Bottom'
    tFVG = 'FVG/BB Top'
    zero5 = 'Fib -0.5'
    one5 = 'Fib -1'
    two5 = 'Fib -2'


class silverBulletLevels(Enum):
    pdH = 'Previous Day High'
    pdL = 'Previous Day Low'
    sH = 'Swing High'
    sL = 'Swing Low'


class raidCoordinates(Enum):
    CB = 'Closest Breaker'
    CBB = 'Closest Breaker Bottom'
    CBS = 'Closest Breaker Start'
    CBT = 'Closest Breaker Top'
    HR = 'High Raided'
    LR = 'Low Raided'
    ST = 'Start Time'
    SP = 'Start Price'
    H = 'High'
    L = 'Low'
    ET = 'End Time'
    EP = 'End Price'
    HRT = 'High Raided Time'
    HRP = 'High Raided Price'
    HRVT = 'High Raided Violation Time'
    LPRHR = 'Lowest Price Reached High Raided'
    LPRHRT = 'Lowest Price Reached High Raided Time'
    LRT = 'Low Raided Time'
    LRP = 'Low Raided Price'
    LRVT = 'Low Raided Violation Time'
    HPRLR = 'Highest Price Reached Low Raided'
    HPRLRT = 'Highest Price Reached Low Raided Time'
    LTP = 'Long TP'
    LTPT = 'Long TP Time'
    LSL = 'Long SL'
    LSLT = 'Long SL Time'
    STP = 'Short TP'
    STPT = 'Short TP Time'
    SSL = 'Short SL'
    SSLT = 'Short SL Time'


class _ProtocolIslastbar(Protocol):
    def __call__(self, userTF: int) -> Any: ...


class _ProtocolNecessarydata(Protocol):
    def __call__(self, atrTF: float) -> Any: ...


class _ProtocolGradboxes(Protocol):
    def __call__(self, gradientBoxes: list[Box], idColor: Color, timeStart: int, bottom: float, top: float, rightCoordinate: int) -> Any: ...


class _ProtocolCheckiftraded(Protocol):
    def __call__(self, tradeName: str) -> Any: ...


class _ProtocolCheckifclosed(Protocol):
    def __call__(self, tradeName: str) -> Any: ...


class _ProtocolIqzz(Protocol):
    def __call__(self, atrMult: float, finalTF: str) -> Any: ...


class _ProtocolDrawbos(Protocol):
    def __call__(self, id: list[labelLine], startPoint: ChartPoint, getKeyPointTime: int, getKeyPointPrice: float, col: Color, showBOS: bool, isUp: bool) -> Any: ...


class _ProtocolDrawmss(Protocol):
    def __call__(self, id: list[labelLine], startPoint: ChartPoint, getKeyPointTime: int, getKeyPointPrice: float, col: Color, showMSS: bool, isUp: bool, upRejections: list[rejectionBlocks], dnRejections: list[rejectionBlocks], highArr__000000a2__: list[float], lowArr__000000a2__: list[float], timeArr__000000a2__: list[int], closeArr__000000a2__: list[float], openArr__000000a2__: list[float], atrTFarr__000000a2__: list[float], upRejectionsPrices: list[float], dnRejectionsPrices: list[float]) -> Any: ...


class _ProtocolGettime(Protocol):
    def __call__(self, id: list[float], compare: float, timeArr__000000a9__: list[int]) -> Any: ...


class _ProtocolOb(Protocol):
    def __call__(self, id: list[orderBlock], highArr__000000b4__: list[float], signArr__000000b4__: list[float], lowArr__000000b4__: list[float], timeArr__000000b4__: list[int], sign: int) -> Any: ...


class _ProtocolOtestrat(Protocol):
    def __call__(self, OTEstart: ChartPoint, future: int, closeArr__0000018d__: list[float], highArr__0000018d__: list[float], lowArr__0000018d__: list[float], timeArr__0000018d__: list[int], longOTEPT: str, longOTESL: int, longOTElevel: float, shortOTEPT: str, shortOTESL: int, shortOTElevel: float, structureDirection: str, oteLongs: bool, atrTF: float, oteShorts: bool) -> Any: ...


class _ProtocolDisplacement(Protocol):
    def __call__(self, logZ: float, atrTFreg: float, highArr__000001f8__: list[float], timeArr__000001f8__: list[int], lowArr__000001f8__: list[float], upDispShow: int, dnDispShow: int, masterCoords: dict[str, float], labelLevels: str, dispUpcol: Color, rightCoordinate: int, dispDncol: Color, noBorders: bool) -> Any: ...


class _ProtocolGetstronglow(Protocol):
    def __call__(self, id: list[strongPoints], startIndex: int, timeArr__00000201__: list[int], lowArr__00000201__: list[float], strongLowPoints: list[float]) -> Any: ...


class _ProtocolGetstronghigh(Protocol):
    def __call__(self, id: list[strongPoints], startIndex: int, timeArr__0000020a__: list[int], highArr__0000020a__: list[float], strongHighPoints: list[float]) -> Any: ...


class _ProtocolEquallevels(Protocol):
    def __call__(self, highArr__00000283__: list[float], lowArr__00000283__: list[float], timeArr__00000283__: list[int], rightCoordinate: int, equalHighsCol: Color, equalLowsCol: Color, liteMode: bool) -> Any: ...


class _ProtocolQuicktime(Protocol):
    def __call__(self, timeString: str) -> Any: ...


class _ProtocolMacros(Protocol):
    def __call__(self, showMacros: bool, noBorders: bool) -> Any: ...


class _ProtocolPo3(Protocol):
    def __call__(self, tf: str, left: int, right: int, show: bool) -> Any: ...


class _ProtocolSilverbullet(Protocol):
    def __call__(self, silverBulletStratLong: bool, silverBulletStratShort: bool, future: int, userTF: int, H: float, L: float, H2: float, L2: float, noBorders: bool, silverBulletLongTP: silverBulletLevels, historicalPoints: list[ChartPoint], historicalData: necessaryData__ren__, silverBulletLongSL: silverBulletLevels, silverBulletShortTP: silverBulletLevels, silverBulletShortSL: silverBulletLevels) -> Any: ...


class _ProtocolInvalidfvgcheck(Protocol):
    def __call__(self, FVGarr: list[FVG], upFVGpricesSorted: list[float], dnFVGpricesSorted: list[float]) -> Any: ...


class _ProtocolDrawfvg(Protocol):
    def __call__(self, counter: dict[str, int], FVGshow: int, FVGname: str, FVGcol: Color, data: FVG, masterCoords: dict[str, float], labelLevels: str, borderTransp: int, liteMode: bool, rightCoordinate: int) -> Any: ...


class _ProtocolInvalidblockcheck(Protocol):
    def __call__(self, bullishOBbox: list[orderBlock], bearishOBbox: list[orderBlock], userTF: int) -> Any: ...


class _ProtocolLastbarrejections(Protocol):
    def __call__(self, id: list[rejectionBlocks], rejectionColor: Color, idShow: int, rejectionString: str, labelLevels: str, borderTransp: int, liteMode: bool, rightCoordinate: int, masterCoords: dict[str, float]) -> Any: ...


class _ProtocolObdraw(Protocol):
    def __call__(self, id: list[orderBlock], OBshow: int, BBshow: int, OBcol: Color, BBcol: Color, bullishString: str, bearishString: str, isBullish: bool, labelLevels: str, borderTransp: int, liteMode: bool, rightCoordinate: int, masterCoords: dict[str, float]) -> Any: ...


isLastBar: _ProtocolIslastbar = Exported()
necessaryData: _ProtocolNecessarydata = Exported()
gradBoxes: _ProtocolGradboxes = Exported()
checkIfTraded: _ProtocolCheckiftraded = Exported()
checkIfClosed: _ProtocolCheckifclosed = Exported()
IQZZ: _ProtocolIqzz = Exported()
drawBos: _ProtocolDrawbos = Exported()
drawMSS: _ProtocolDrawmss = Exported()
getTime: _ProtocolGettime = Exported()
OB: _ProtocolOb = Exported()
OTEstrat: _ProtocolOtestrat = Exported()
displacement: _ProtocolDisplacement = Exported()
getStrongLow: _ProtocolGetstronglow = Exported()
getStrongHigh: _ProtocolGetstronghigh = Exported()
equalLevels: _ProtocolEquallevels = Exported()
quickTime: _ProtocolQuicktime = Exported()
macros: _ProtocolMacros = Exported()
po3: _ProtocolPo3 = Exported()
silverBullet: _ProtocolSilverbullet = Exported()
invalidFVGcheck: _ProtocolInvalidfvgcheck = Exported()
drawFVG: _ProtocolDrawfvg = Exported()
invalidBlockCheck: _ProtocolInvalidblockcheck = Exported()
lastBarRejections: _ProtocolLastbarrejections = Exported()
OBdraw: _ProtocolObdraw = Exported()


displacement.new = displacement__ren__
macros.new = macros__ren__
silverBullet.new = silverBullet__ren__
necessaryData.new = necessaryData__ren__


@script.library('ICTlibrary', dynamic_requests=True)
def main():
    @export
    def isLastBar(userTF: int):
        return time('', -1) >= time_close(timeframe.from_seconds(userTF))

    @export
    def necessaryData(atrTF: float):
        historicalData: Persistent[necessaryData__ren__] = necessaryData__ren__(array.new_float(), array.new_float(), array.new_int(), array.new_float(), array.new_float(), array.new_float(), array.new_int(), array.new_float(), array.new_float(), array.new_float(), array.new_float())
        array.unshift(historicalData.highArr, high)
        array.unshift(historicalData.lowArr, low)
        array.unshift(historicalData.timeArr, time)
        array.push(historicalData.binaryTimeArr, time)
        array.unshift(historicalData.closeArr, close)
        array.push(historicalData.logArr, math.log(close / close[1]))
        array.unshift(historicalData.signArr, math.sign(close - open))
        array.push(historicalData.binaryCloseArr, close)
        array.push(historicalData.binaryOpenArr, open)
        array.unshift(historicalData.atrTFarr, atrTF)
        array.unshift(historicalData.openArr, open)
        logZ = (array.last(historicalData.logArr) - array.avg(historicalData.logArr)) / array.stdev(historicalData.logArr)
        if array.size(historicalData.logArr) > 200:
            array.shift(historicalData.logArr)
        return (historicalData, logZ)

    @export
    @method
    def gradBoxes(gradientBoxes: list[Box], idColor: Color, timeStart: int, bottom: float, top: float, rightCoordinate: int):
        if not na(array.first(gradientBoxes)):
            for boxx in gradientBoxes:
                box.delete(boxx)
        Range = math.abs(top - bottom) / 19
        avg = math.avg(bottom, top)
        trueBottom = math.min(bottom, top)
        nLine: Persistent = NA(Line)
        method_call('delete', nLine)
        nLine = line.new(timeStart, avg, rightCoordinate, avg, width=2, color=idColor, xloc=xloc.bar_time)
        __block_result__ = na
        for x in pine_range(0, 19, 1):
            __block_result_1__ = na
            if x <= 9:
                __block_result_1__ = color.from_gradient(x, -1, 9, chart.bg_color, idColor)
            else:
                __block_result_1__ = color.from_gradient(x, 10, 20, idColor, chart.bg_color)
            col = __block_result_1__
            __block_result__ = array.set(gradientBoxes, x, box.new(timeStart, trueBottom + Range * (x + 1), rightCoordinate, trueBottom + Range * x, bgcolor=color.new(col, 85), border_color=color.new(col, 100), xloc=xloc.bar_time))
        return __block_result__

    @export
    def checkIfTraded(tradeName: str):
        openTrades = strategy.opentrades - 1
        closedTrades = strategy.closedtrades - 1
        return strategy.opentrades.entry_id(openTrades) == tradeName and strategy.opentrades.entry_bar_index(openTrades) == bar_index or (strategy.closedtrades.entry_id(closedTrades) == tradeName and strategy.closedtrades.entry_bar_index(closedTrades) == bar_index)

    @export
    def checkIfClosed(tradeName: str):
        closedTrades = strategy.closedtrades - 1
        return strategy.closedtrades.entry_id(closedTrades) == tradeName and strategy.closedtrades.entry_bar_index(closedTrades) == bar_index or (strategy.closedtrades.entry_id(closedTrades) == tradeName and strategy.closedtrades.exit_bar_index(closedTrades) == bar_index)

    @export
    def IQZZ(atrMult: float, finalTF: str):
        point__00000068__: Persistent = close
        timeP: Persistent = time
        dir: Persistent[int] = 0
        atr = request.security('', finalTF, ta.atr(14))
        atr = atr * atrMult
        if dir == 1:
            point__00000068__ = math.max(point__00000068__, high)
            __block_result_2__ = na
            __switch_1__ = high == point__00000068__
            if __switch_1__ == True:
                __block_result_2__ = time
            else:
                __block_result_2__ = timeP
            timeP = __block_result_2__
            if low <= point__00000068__ - atr and high != point__00000068__:
                dir = -1
                point__00000068__ = low
                timeP = time
        elif dir == -1:
            point__00000068__ = math.min(low, point__00000068__)
            __block_result_3__ = na
            __switch_1__ = low == point__00000068__
            if __switch_1__ == True:
                __block_result_3__ = time
            else:
                __block_result_3__ = timeP
            timeP = __block_result_3__
            if high >= point__00000068__ + atr and low != point__00000068__:
                dir = 1
                point__00000068__ = high
                timeP = time
        if dir == 0:
            if high >= point__00000068__ + atr:
                dir = 1
                point__00000068__ = high
                timeP = time
            elif low <= point__00000068__ + atr:
                dir = -1
                point__00000068__ = low
                timeP = time
        return dir

    @export
    @method
    def drawBos(id: list[labelLine], startPoint: ChartPoint, getKeyPointTime: int, getKeyPointPrice: float, col: Color, showBOS: bool, isUp: bool):
        avg = math.round(math.avg(getKeyPointTime, time))
        __block_result_4__ = na
        if showBOS:
            __block_result_5__ = na
            __switch_1__ = isUp
            if __switch_1__ == True:
                __block_result_5__ = label.style_label_up
            else:
                __block_result_5__ = label.style_label_down
            position__ren__ = __block_result_5__
            __block_result_4__ = array.push(id, labelLine(line.new(startPoint, chart.point.from_time(time, getKeyPointPrice), color=col, xloc=xloc.bar_time, style=line.style_dotted), label.new(avg, getKeyPointPrice, xloc=xloc.bar_time, color=color.new('#00000000'), textcolor=col, text='BoS', size=size.tiny, style=position__ren__)))
        return __block_result_4__

    @export
    @method
    def drawMSS(id: list[labelLine], startPoint: ChartPoint, getKeyPointTime: int, getKeyPointPrice: float, col: Color, showMSS: bool, isUp: bool, upRejections: list[rejectionBlocks], dnRejections: list[rejectionBlocks], highArr__000000a2__: list[float], lowArr__000000a2__: list[float], timeArr__000000a2__: list[int], closeArr__000000a2__: list[float], openArr__000000a2__: list[float], atrTFarr__000000a2__: list[float], upRejectionsPrices: list[float], dnRejectionsPrices: list[float]):
        avg = math.round(math.avg(getKeyPointTime, time))
        if isUp:
            max: float = 0.0
            maxTime: int = 0
            isRejection: bool = False
            bodyPrice: Persistent[float] = 0.0
            for i, data in enumerate(highArr__000000a2__):
                if data >= getKeyPointPrice:
                    max = math.max(max, data)
                    if data == max:
                        maxTime = array.get(timeArr__000000a2__, i)
                        bodyPrice = math.max(array.get(closeArr__000000a2__, i), array.get(openArr__000000a2__, i))
                        isRejection = math.abs(data - bodyPrice) >= array.get(atrTFarr__000000a2__, i) / 3
                else:
                    break
            if max != 0 and isRejection:
                array.unshift(upRejections, rejectionBlocks(chart.point.from_time(maxTime, max), bodyPrice))
                array.insert(upRejectionsPrices, array.binary_search_rightmost(upRejectionsPrices, max), max)
        else:
            min: float = 2e+21
            minTime: int = 0
            isRejection: bool = False
            bodyPrice: Persistent[float] = 0.0
            for i, data in enumerate(lowArr__000000a2__):
                if data <= getKeyPointPrice:
                    min = math.min(min, data)
                    if data == min:
                        minTime = array.get(timeArr__000000a2__, i)
                        bodyPrice = math.min(array.get(closeArr__000000a2__, i), array.get(openArr__000000a2__, i))
                        isRejection = math.abs(data - bodyPrice) >= array.get(atrTFarr__000000a2__, i) / 3
                else:
                    break
            if min != 2e+21 and isRejection:
                array.unshift(dnRejections, rejectionBlocks(chart.point.from_time(minTime, min), bodyPrice))
                array.insert(dnRejectionsPrices, array.binary_search_rightmost(dnRejectionsPrices, min), min)
        __block_result_6__ = na
        if showMSS:
            __block_result_7__ = na
            __switch_1__ = isUp
            if __switch_1__ == True:
                __block_result_7__ = label.style_label_up
            else:
                __block_result_7__ = label.style_label_down
            position__ren__ = __block_result_7__
            __block_result_6__ = array.push(id, labelLine(line.new(startPoint, chart.point.from_time(time, getKeyPointPrice), color=col, xloc=xloc.bar_time), label.new(avg, getKeyPointPrice, xloc=xloc.bar_time, color=color.new('#00000000'), textcolor=col, text='MSS', size=size.tiny, style=position__ren__)))
        return __block_result_6__

    @export
    @method
    def getTime(id: list[float], compare: float, timeArr__000000a9__: list[int]):
        startTime: int = 0
        __block_result_8__ = na
        if array.size(id) > 0:
            for i, v in enumerate(id):
                if v == compare:
                    startTime = array.get(timeArr__000000a9__, i)
                    break
            __block_result_8__ = startTime
        else:
            __block_result_8__ = time
        return __block_result_8__

    @export
    @method
    def OB(id: list[orderBlock], highArr__000000b4__: list[float], signArr__000000b4__: list[float], lowArr__000000b4__: list[float], timeArr__000000b4__: list[int], sign: int):
        __block_result_9__ = na
        for i in pine_range(1, array.size(highArr__000000b4__) - 1, 1):
            __block_result_10__ = na
            if array.get(signArr__000000b4__, i) == sign:
                getHigh = array.get(highArr__000000b4__, i)
                getLow = array.get(lowArr__000000b4__, i)
                array.unshift(id, orderBlock(array.from_items(array.get(timeArr__000000b4__, i), getHigh, last_bar_time, getLow)))
                break
            __block_result_9__ = __block_result_10__
        return __block_result_9__

    @export
    def OTEstrat(OTEstart: ChartPoint, future: int, closeArr__0000018d__: list[float], highArr__0000018d__: list[float], lowArr__0000018d__: list[float], timeArr__0000018d__: list[int], longOTEPT: str, longOTESL: int, longOTElevel: float, shortOTEPT: str, shortOTESL: int, shortOTElevel: float, structureDirection: str, oteLongs: bool, atrTF: float, oteShorts: bool):
        highestPoint: Persistent[float] = 0.0
        lowestPoint: Persistent[float] = 2e+21
        highestPoinT: Persistent[int] = 0
        lowestPoinT: Persistent[int] = 0
        oteDrawings: Persistent[OTEtimes] = OTEtimes(array.new_int(), array.new_int())
        field_0: Series = OTEstart.time
        if OTEstart.time != field_0[1]:
            highestPoint = 0
            lowestPoint = 2e+21
        OTElevels: Persistent[dict[str, float]] = map.new()
        openTrades = strategy.opentrades - 1
        closedTrades = strategy.closedtrades - 1
        keys = map.keys(OTElevels)
        highestPoint = math.max(highestPoint, high)
        lowestPoint = math.min(lowestPoint, low)
        if highestPoint == high:
            highestPoinT = time
            strategy.cancel('Long OTE')
        if lowestPoint == low:
            lowestPoinT = time
            strategy.cancel('Short OTE')
        if strategy.position_size != 0:
            strategy.cancel('Long OTE')
            strategy.cancel('Short OTE')
        if not na(oteDrawings.tpLineLong):
            line.set_x2(oteDrawings.tpLineLong, future)
            label.set_x(oteDrawings.tpLabelLong, future)
            line.set_x2(oteDrawings.slLineLong, future)
            label.set_x(oteDrawings.slLabelLong, future)
            if checkIfClosed('Long OTE'):
                switch_var_5 = strategy.closedtrades.exit_price(closedTrades) > strategy.closedtrades.entry_price(closedTrades)
                __switch_2__ = switch_var_5
                if __switch_2__ == True:
                    line.delete(oteDrawings.slLineLong)
                    label.delete(oteDrawings.slLabelLong)
                    oteDrawings.tpLineLong = NA(Line)
                    oteDrawings.tpLabelLong = NA(Label)
                else:
                    line.delete(oteDrawings.tpLineLong)
                    label.delete(oteDrawings.tpLabelLong)
                    oteDrawings.slLineLong = NA(Line)
                    oteDrawings.slLabelLong = NA(Label)
        if checkIfTraded('Long OTE'):
            array.push(oteDrawings.upTimes, cast_int(map.get(OTElevels, 'Long OTE Highest PoinT')))
            entry = map.get(OTElevels, 'Long OTE Entry')
            for i in pine_range(1, array.size(closeArr__0000018d__) - 1, 1):
                if array.get(highArr__0000018d__, i) >= entry and array.get(lowArr__0000018d__, i) <= entry or array.get(highArr__0000018d__, i) <= entry:
                    getTime__00000106__ = array.get(timeArr__0000018d__, i)
                    line.new(getTime__00000106__, entry, time, entry, color=color.new('#74FFBC'), xloc=xloc.bar_time, style=line.style_dotted, width=2)
                    label.new(math.round(math.avg(getTime__00000106__, time)), entry, color=color.new('#00000000'), xloc=xloc.bar_time, text=string.tostring(longOTElevel), textcolor=color.new('#74FFBC'), style=label.style_label_up, size=size.small)
                    getTP = map.get(OTElevels, 'Long OTE TP')
                    getSL = map.get(OTElevels, 'Long OTE SL')
                    oteDrawings.tpLineLong = line.new(cast_int(map.get(OTElevels, 'Long OTE Highest PoinT')), getTP, future, getTP, color=color.new('#74FFBC'), xloc=xloc.bar_time, style=line.style_solid, width=2)
                    oteDrawings.tpLabelLong = label.new(future, getTP, text=longOTEPT, style=label.style_label_lower_right, textcolor=color.new('#74FFBC'), xloc=xloc.bar_time, color=color.new('#00000000'), size=size.small)
                    oteDrawings.slLineLong = line.new(cast_int(map.get(OTElevels, 'Long OTE Start Time')), getSL, future, getSL, color=color.red, xloc=xloc.bar_time, style=line.style_solid, width=2)
                    __block_result_11__ = na
                    __switch_3__ = longOTESL
                    if __switch_3__ == 0:
                        __block_result_11__ = 'Swing Low'
                    else:
                        __block_result_11__ = 'Swing Low - ' + string.tostring(longOTESL) + ' Ticks'
                    txt = __block_result_11__
                    oteDrawings.slLabelLong = label.new(future, getSL, text=txt, style=label.style_label_upper_right, textcolor=color.red, xloc=xloc.bar_time, color=color.new('#00000000'), size=size.small)
                    if checkIfClosed('Long OTE'):
                        switch_var_8 = strategy.closedtrades.exit_price(closedTrades) > strategy.closedtrades.entry_price(closedTrades)
                        __switch_4__ = switch_var_8
                        if __switch_4__ == True:
                            line.delete(oteDrawings.slLineLong)
                            label.delete(oteDrawings.slLabelLong)
                            oteDrawings.tpLineLong = NA(Line)
                            oteDrawings.tpLabelLong = NA(Label)
                        else:
                            line.delete(oteDrawings.tpLineLong)
                            label.delete(oteDrawings.tpLabelLong)
                            oteDrawings.slLineLong = NA(Line)
                            oteDrawings.slLabelLong = NA(Label)
                    points = array.from_items(chart.point.from_time(cast_int(map.get(OTElevels, 'Long OTE Start Time')), map.get(OTElevels, 'Long OTE Start Price')), chart.point.from_time(cast_int(map.get(OTElevels, 'Long OTE Highest PoinT')), map.get(OTElevels, 'Long OTE Highest Point')), chart.point.from_time(time, entry))
                    polyline.new(points, xloc=xloc.bar_time, line_color=color.rgb(128, 116, 255))
                    for values in keys:
                        if string.contains(values, 'Long'):
                            map.put(OTElevels, values, na)
                    break
        if not na(oteDrawings.tpLineShort):
            line.set_x2(oteDrawings.tpLineShort, future)
            label.set_x(oteDrawings.tpLabelShort, future)
            line.set_x2(oteDrawings.slLineShort, future)
            label.set_x(oteDrawings.slLabelShort, future)
            if checkIfClosed('Short OTE'):
                switch_var_10 = strategy.closedtrades.exit_price(closedTrades) < strategy.closedtrades.entry_price(closedTrades)
                __switch_2__ = switch_var_10
                if __switch_2__ == True:
                    line.delete(oteDrawings.slLineShort)
                    label.delete(oteDrawings.slLabelShort)
                    oteDrawings.tpLineShort = NA(Line)
                    oteDrawings.tpLabelShort = NA(Label)
                else:
                    line.delete(oteDrawings.tpLineShort)
                    label.delete(oteDrawings.tpLabelShort)
                    oteDrawings.slLineShort = NA(Line)
                    oteDrawings.slLabelShort = NA(Label)
        if checkIfTraded('Short OTE'):
            array.push(oteDrawings.dnTimes, cast_int(map.get(OTElevels, 'Short OTE Lowest PoinT')))
            entry = map.get(OTElevels, 'Short OTE Entry')
            for i in pine_range(1, array.size(closeArr__0000018d__) - 1, 1):
                if array.get(highArr__0000018d__, i) >= entry and array.get(lowArr__0000018d__, i) <= entry or array.get(lowArr__0000018d__, i) >= entry:
                    getTime__0000014c__ = array.get(timeArr__0000018d__, i)
                    line.new(getTime__0000014c__, entry, time, entry, color=color.rgb(255, 116, 116), xloc=xloc.bar_time, style=line.style_dotted, width=2)
                    label.new(math.round(math.avg(getTime__0000014c__, time)), entry, color=color.new('#00000000'), xloc=xloc.bar_time, text=string.tostring(shortOTElevel), textcolor=color.rgb(255, 116, 116), style=label.style_label_down, size=size.small)
                    getTP = map.get(OTElevels, 'Short OTE TP')
                    getSL = map.get(OTElevels, 'Short OTE SL')
                    oteDrawings.tpLineShort = line.new(cast_int(map.get(OTElevels, 'Short OTE Lowest PoinT')), getTP, future, getTP, color=color.new('#74FFBC'), xloc=xloc.bar_time, style=line.style_solid, width=2)
                    oteDrawings.tpLabelShort = label.new(future, getTP, text=shortOTEPT, style=label.style_label_upper_right, textcolor=color.new('#74FFBC'), xloc=xloc.bar_time, color=color.new('#00000000'), size=size.small)
                    oteDrawings.slLineShort = line.new(cast_int(map.get(OTElevels, 'Short OTE Start Time')), getSL, future, getSL, color=color.red, xloc=xloc.bar_time, style=line.style_solid, width=2)
                    __block_result_12__ = na
                    __switch_3__ = shortOTESL
                    if __switch_3__ == 0:
                        __block_result_12__ = 'Swing High'
                    else:
                        __block_result_12__ = 'Swing How + ' + string.tostring(shortOTESL) + ' Ticks'
                    txt = __block_result_12__
                    oteDrawings.slLabelShort = label.new(future, getSL, text=txt, style=label.style_label_lower_right, textcolor=color.red, xloc=xloc.bar_time, color=color.new('#00000000'), size=size.small)
                    if checkIfClosed('Short OTE'):
                        switch_var_13 = strategy.closedtrades.exit_price(closedTrades) < strategy.closedtrades.entry_price(closedTrades)
                        __switch_4__ = switch_var_13
                        if __switch_4__ == True:
                            line.delete(oteDrawings.slLineShort)
                            label.delete(oteDrawings.slLabelShort)
                            oteDrawings.tpLineShort = NA(Line)
                            oteDrawings.tpLabelShort = NA(Label)
                        else:
                            line.delete(oteDrawings.tpLineShort)
                            label.delete(oteDrawings.tpLabelShort)
                            oteDrawings.slLineShort = NA(Line)
                            oteDrawings.slLabelShort = NA(Label)
                    points = array.from_items(chart.point.from_time(cast_int(map.get(OTElevels, 'Short OTE Start Time')), map.get(OTElevels, 'Short OTE Start Price')), chart.point.from_time(cast_int(map.get(OTElevels, 'Short OTE Lowest PoinT')), map.get(OTElevels, 'Short OTE Lowest Point')), chart.point.from_time(time, entry))
                    polyline.new(points, xloc=xloc.bar_time, line_color=color.rgb(128, 116, 255))
                    for values in keys:
                        if string.contains(values, 'Short'):
                            map.put(OTElevels, values, na)
                    break
        if structureDirection == 'Up':
            strategy.cancel('Short OTE')
            if strategy.opentrades.entry_id(openTrades) != 'Short OTE':
                for values in keys:
                    if string.contains(values, 'Short'):
                        map.put(OTElevels, values, na)
            if oteLongs:
                if highestPoint - OTEstart.price >= atrTF:
                    if not array.includes(oteDrawings.upTimes, highestPoinT):
                        entry = math.round_to_mintick(highestPoint - (highestPoint - OTEstart.price) * longOTElevel)
                        __block_result_13__ = na
                        __switch_4__ = longOTEPT
                        if __switch_4__ == 'Swing High':
                            __block_result_13__ = math.round_to_mintick(highestPoint)
                        else:
                            __block_result_13__ = math.round_to_mintick(highestPoint - (highestPoint - OTEstart.price) * string.tonumber(longOTEPT))
                        tp = __block_result_13__
                        sl = math.round_to_mintick(OTEstart.price - longOTESL * syminfo.mintick)
                        if close >= entry and barstate.isconfirmed and (strategy.opentrades == 0):
                            map.put(OTElevels, 'Long OTE Entry', entry)
                            map.put(OTElevels, 'Long OTE TP', tp)
                            map.put(OTElevels, 'Long OTE SL', sl)
                            map.put(OTElevels, 'Long OTE Start Time', OTEstart.time)
                            map.put(OTElevels, 'Long OTE Start Price', OTEstart.price)
                            map.put(OTElevels, 'Long OTE Highest Point', highestPoint)
                            map.put(OTElevels, 'Long OTE Highest PoinT', highestPoinT)
                            strategy.entry('Long OTE', strategy.long, comment='OTE Long', limit=entry)
                            strategy.exit('Long OTE Exit', 'Long OTE', limit=tp, stop=sl, comment_profit='Long OTE Profit', comment_loss='Long OTE Loss')
                if close < OTEstart.price:
                    array.push(oteDrawings.upTimes, highestPoinT)
        else:
            strategy.cancel('Long OTE')
            if strategy.opentrades.entry_id(openTrades) != 'Long OTE':
                for values in keys:
                    if string.contains(values, 'Long'):
                        map.put(OTElevels, values, na)
            if oteShorts:
                if OTEstart.price - lowestPoint >= atrTF:
                    if not array.includes(oteDrawings.dnTimes, lowestPoinT):
                        entry = math.round_to_mintick((OTEstart.price - lowestPoint) * shortOTElevel + lowestPoint)
                        __block_result_14__ = na
                        __switch_4__ = shortOTEPT
                        if __switch_4__ == 'Swing Low':
                            __block_result_14__ = math.round_to_mintick(lowestPoint)
                        else:
                            __block_result_14__ = math.round_to_mintick(lowestPoint - (lowestPoint - OTEstart.price) * string.tonumber(shortOTEPT))
                        tp = __block_result_14__
                        sl = math.round_to_mintick(OTEstart.price + shortOTESL * syminfo.mintick)
                        if close <= entry and barstate.isconfirmed and (strategy.opentrades == 0):
                            map.put(OTElevels, 'Short OTE Entry', entry)
                            map.put(OTElevels, 'Short OTE TP', tp)
                            map.put(OTElevels, 'Short OTE SL', sl)
                            map.put(OTElevels, 'Short OTE Start Time', OTEstart.time)
                            map.put(OTElevels, 'Short OTE Start Price', OTEstart.price)
                            map.put(OTElevels, 'Short OTE Lowest Point', lowestPoint)
                            map.put(OTElevels, 'Short OTE Lowest PoinT', lowestPoinT)
                            strategy.entry('Short OTE', strategy.short, comment='OTE Short', limit=entry)
                            strategy.exit('Short OTE Exit', 'Short OTE', limit=tp, stop=sl, comment_profit='Short OTE Profit', comment_loss='Short OTE Loss')
                if close > OTEstart.price:
                    array.push(oteDrawings.dnTimes, lowestPoinT)
        return 0

    @export
    def displacement(logZ: float, atrTFreg: float, highArr__000001f8__: list[float], timeArr__000001f8__: list[int], lowArr__000001f8__: list[float], upDispShow: int, dnDispShow: int, masterCoords: dict[str, float], labelLevels: str, dispUpcol: Color, rightCoordinate: int, dispDncol: Color, noBorders: bool):
        upVolatility: Persistent[list[float]] = array.new_float()
        dnVolatility: Persistent[list[float]] = array.new_float()
        upDisplacement: Persistent[list[displacement__ren__]] = array.new(0, NA(displacement__ren__))
        dnDisplacement: Persistent[list[displacement__ren__]] = array.new(0, NA(displacement__ren__))
        if logZ >= 1 and high <= close + atrTFreg * 0.5:
            array.push(upVolatility, logZ)
        else:
            if array.size(upVolatility) >= 3:
                size__ren__ = array.size(upVolatility) + 1
                getHigh = array.get(highArr__000001f8__, size__ren__)
                array.unshift(upDisplacement, displacement__ren__(getHigh, low, array.get(timeArr__000001f8__, size__ren__)))
            array.clear(upVolatility)
        if logZ <= -1 and low >= close - atrTFreg * 0.5:
            array.push(dnVolatility, logZ)
        else:
            if array.size(dnVolatility) >= 3:
                size__ren__ = array.size(dnVolatility) + 1
                getLow = array.get(lowArr__000001f8__, size__ren__)
                array.unshift(dnDisplacement, displacement__ren__(high, getLow, array.get(timeArr__000001f8__, size__ren__)))
            array.clear(dnVolatility)
        if array.size(upDisplacement) > 0:
            for i in pine_range(array.size(upDisplacement) - 1, 0, 1):
                if close < array.get(upDisplacement, i).highPrice:
                    method_call('delete', array.remove(upDisplacement, i).displacementBox)
        if array.size(dnDisplacement) > 0:
            for i in pine_range(array.size(dnDisplacement) - 1, 0, 1):
                if close > array.get(dnDisplacement, i).lowPrice:
                    method_call('delete', array.remove(dnDisplacement, i).displacementBox)
        __block_result_15__ = na
        if barstate.islast:
            if array.size(upDisplacement) > 0:
                for i in pine_range(0, array.size(upDisplacement) - 1, 1):
                    getDisp = array.get(upDisplacement, i)
                    method_call('delete', getDisp.displacementBox)
                    if labelLevels == 'Outside':
                        method_call('delete', getDisp.displacementLab)
                    if i < upDispShow:
                        __block_result_16__ = na
                        __switch_4__ = labelLevels == 'Inside'
                        if __switch_4__ == True:
                            __block_result_16__ = 'DP'
                        else:
                            __block_result_16__ = ''
                        txt = __block_result_16__
                        __block_result_17__ = na
                        __switch_4__ = noBorders
                        if __switch_4__ == True:
                            __block_result_17__ = 100
                        else:
                            __block_result_17__ = 25
                        borderTransp: Persistent = __block_result_17__
                        __block_result_18__ = (na, na)
                        __switch_4__ = i == 0
                        if __switch_4__ == True:
                            __block_result_18__ = (color.new('#00000000'), color.new('#00000000'))
                        else:
                            __block_result_18__ = (color.new(dispUpcol, borderTransp), color.new(dispUpcol, 75))
                        bordCol, bgCol = __block_result_18__
                        getDisp.displacementBox = box.new(getDisp.timeAtPrice, getDisp.highPrice, rightCoordinate, getDisp.lowPrice, xloc=xloc.bar_time, bgcolor=bgCol, border_color=bordCol, text=txt, text_halign=text.align_right, text_size=size.auto, text_color=color.new(chart.fg_color, 25))
                        if labelLevels == 'Outside':
                            getDisp.displacementLab = label.new(rightCoordinate, math.avg(getDisp.highPrice, getDisp.lowPrice), color=color.new('#00000000'), textcolor=dispUpcol, text='DP', style=label.style_label_left, xloc=xloc.bar_time, size=size.tiny)
                        if i == 0:
                            gradientBoxes: Persistent[list[Box]] = array.new_box(20)
                            gradBoxes(gradientBoxes, dispUpcol, getDisp.timeAtPrice, getDisp.lowPrice, getDisp.highPrice, rightCoordinate)
                        if na(map.get(masterCoords, 'Up Displacement')) and upDispShow != 0:
                            map.put(masterCoords, 'Up Displacement', math.avg(getDisp.highPrice, getDisp.lowPrice))
            __block_result_19__ = na
            if array.size(dnDisplacement) > 0:
                __block_result_20__ = na
                for i in pine_range(0, array.size(dnDisplacement) - 1, 1):
                    getDisp = array.get(dnDisplacement, i)
                    method_call('delete', getDisp.displacementBox)
                    if labelLevels == 'Outside':
                        method_call('delete', getDisp.displacementLab)
                    __block_result_21__ = na
                    if i < dnDispShow:
                        col = color.from_gradient(getDisp.lowPrice, close, close + atrTFreg * 10, color.new(dispDncol, 25), color.new(dispDncol, 90))
                        __block_result_22__ = na
                        __switch_4__ = labelLevels == 'Inside'
                        if __switch_4__ == True:
                            __block_result_22__ = 'DP'
                        else:
                            __block_result_22__ = ''
                        txt = __block_result_22__
                        __block_result_23__ = na
                        __switch_4__ = noBorders
                        if __switch_4__ == True:
                            __block_result_23__ = 100
                        else:
                            __block_result_23__ = 25
                        borderTransp: Persistent = __block_result_23__
                        __block_result_24__ = (na, na)
                        __switch_4__ = i == 0
                        if __switch_4__ == True:
                            __block_result_24__ = (color.new('#00000000'), color.new('#00000000'))
                        else:
                            __block_result_24__ = (color.new(dispDncol, borderTransp), color.new(dispDncol, 75))
                        bordCol, bgCol = __block_result_24__
                        getDisp.displacementBox = box.new(getDisp.timeAtPrice, getDisp.highPrice, rightCoordinate, getDisp.lowPrice, xloc=xloc.bar_time, bgcolor=bgCol, border_color=bordCol, text=txt, text_halign=text.align_right, text_size=size.auto, text_color=color.new(chart.fg_color, 25))
                        if labelLevels == 'Outside':
                            getDisp.displacementLab = label.new(rightCoordinate, math.avg(getDisp.highPrice, getDisp.lowPrice), color=color.new('#00000000'), textcolor=dispDncol, text='DP', style=label.style_label_left, xloc=xloc.bar_time, size=size.tiny)
                        if i == 0:
                            gradientBoxes: Persistent[list[Box]] = array.new_box(20)
                            gradBoxes(gradientBoxes, dispDncol, getDisp.timeAtPrice, getDisp.lowPrice, getDisp.highPrice, rightCoordinate)
                        __block_result_25__ = na
                        if na(map.get(masterCoords, 'Down Displacement')) and upDispShow != 0:
                            __block_result_25__ = map.put(masterCoords, 'Down Displacement', math.avg(getDisp.highPrice, getDisp.lowPrice))
                        __block_result_21__ = __block_result_25__
                    __block_result_20__ = __block_result_21__
                __block_result_19__ = __block_result_20__
            __block_result_15__ = __block_result_19__
        return __block_result_15__

    @export
    @method
    def getStrongLow(id: list[strongPoints], startIndex: int, timeArr__00000201__: list[int], lowArr__00000201__: list[float], strongLowPoints: list[float]):
        getLow: float = 2e+21
        getLowTime: int = 0
        for i in pine_range(startIndex, 0, 1):
            getLowArr = array.get(lowArr__00000201__, i)
            getLow = math.min(getLow, getLowArr)
            if getLow == getLowArr:
                getLowTime = array.get(timeArr__00000201__, i)
        array.unshift(strongLowPoints, getLow)
        return array.unshift(id, strongPoints(price=getLow, timeAtprice=getLowTime))

    @export
    @method
    def getStrongHigh(id: list[strongPoints], startIndex: int, timeArr__0000020a__: list[int], highArr__0000020a__: list[float], strongHighPoints: list[float]):
        getHigh: float = 0.0
        getHighTime: int = 0
        for i in pine_range(startIndex, 0, 1):
            gethighArr = array.get(highArr__0000020a__, i)
            getHigh = math.max(getHigh, gethighArr)
            if getHigh == gethighArr:
                getHighTime = array.get(timeArr__0000020a__, i)
        array.unshift(strongHighPoints, getHigh)
        return array.unshift(id, strongPoints(price=getHigh, timeAtprice=getHighTime))

    @export
    def equalLevels(highArr__00000283__: list[float], lowArr__00000283__: list[float], timeArr__00000283__: list[int], rightCoordinate: int, equalHighsCol: Color, equalLowsCol: Color, liteMode: bool):
        equalHighsValues: Persistent[equalLevelsDraw] = equalLevelsDraw(levels=array.new_float(), radiate=array.new_label(), times=array.new_int())
        equalLowsValues: Persistent[equalLevelsDraw] = equalLevelsDraw(levels=array.new_float(), radiate=array.new_label(), times=array.new_int())
        if not na(equalHighsValues):
            if array.size(equalHighsValues.levels) > 0:
                line.delete(equalHighsValues.connector)
                label.delete(equalHighsValues.connectorLab)
                array.clear(equalHighsValues.levels)
                array.clear(equalHighsValues.times)
                if array.size(equalHighsValues.radiate) > 0:
                    __loop_3__ = pine_loop(0, 1)
                    while __loop_3__.step(array.size(equalHighsValues.radiate) - 1):
                        i = __loop_3__.value
                        method_call('delete', array.shift(equalHighsValues.radiate))
        if not na(equalLowsValues):
            if array.size(equalLowsValues.levels) > 0:
                line.delete(equalLowsValues.connector)
                label.delete(equalLowsValues.connectorLab)
                array.clear(equalLowsValues.levels)
                array.clear(equalLowsValues.times)
                if array.size(equalLowsValues.radiate) > 0:
                    __loop_3__ = pine_loop(0, 1)
                    while __loop_3__.step(array.size(equalLowsValues.radiate) - 1):
                        i = __loop_3__.value
                        method_call('delete', array.shift(equalLowsValues.radiate))
        atrArr: Persistent[list[float]] = array.new_float()
        array.unshift(atrArr, ta.atr(14) / 15)
        __block_result_26__ = na
        if barstate.islast:
            __block_result_27__ = na
            __switch_1__ = barstate.isconfirmed
            if __switch_1__ == True:
                __block_result_27__ = 0
            else:
                __block_result_27__ = 1
            start = __block_result_27__
            min = math.min(100, array.size(highArr__00000283__))
            sliceHighs = array.slice(highArr__00000283__, start, min)
            sliceLows = array.slice(lowArr__00000283__, start, min)
            sliceATR = array.slice(atrArr, start, min)
            sliceTime = array.slice(timeArr__00000283__, start, min)
            highFound: bool = False
            lowFound: bool = False
            if method_call('size', sliceHighs) > 1:
                for i in pine_range(method_call('size', sliceHighs) - 1, 1, 1):
                    getInitialHigh = method_call('get', sliceHighs, i)
                    getAtr = method_call('get', sliceATR, i)
                    getInitialTime = method_call('get', sliceTime, i)
                    for x in pine_range(i - 1, 0, 1):
                        compare = method_call('get', sliceHighs, x)
                        compareTime = method_call('get', sliceTime, x)
                        if compare > getInitialHigh - getAtr and compare < getInitialHigh + getAtr:
                            if array.size(equalHighsValues.levels) == 0:
                                array.push(equalHighsValues.levels, getInitialHigh)
                                array.push(equalHighsValues.times, getInitialTime)
                                equalHighsValues.startTime = getInitialTime
                            array.push(equalHighsValues.levels, compare)
                            array.push(equalHighsValues.times, compareTime)
                            highFound = True
                        if compare > getInitialHigh + getAtr:
                            array.clear(equalHighsValues.levels)
                            array.clear(equalHighsValues.times)
                            equalHighsValues.startTime = NA(int)
                            highFound = False
                            break
                    if highFound:
                        getAvg = array.avg(equalHighsValues.levels)
                        equalHighsValues.connector = line.new(equalHighsValues.startTime, getAvg, rightCoordinate, getAvg, xloc=xloc.bar_time, color=equalHighsCol, style=line.style_dotted)
                        equalHighsValues.connectorLab = label.new(math.round(math.avg(equalHighsValues.startTime, array.last(equalHighsValues.times))), getAvg, xloc=xloc.bar_time, color=color.new('#00000000'), textcolor=equalHighsCol, style=label.style_label_down, size=size.tiny, text='Equal Highs')
                        if not liteMode:
                            for x, price in enumerate(equalHighsValues.levels):
                                getTime__00000259__ = array.get(equalHighsValues.times, x)
                                array.push(equalHighsValues.radiate, label.new(getTime__00000259__, price, xloc=xloc.bar_time, text='•', style=label.style_text_outline, color=color.new(equalHighsCol, 80), textcolor=equalHighsCol, size=size.normal))
                                array.push(equalHighsValues.radiate, label.new(getTime__00000259__, price, xloc=xloc.bar_time, text='•', style=label.style_text_outline, color=color.new(equalHighsCol, 80), textcolor=equalHighsCol, size=size.normal))
                        break
            __block_result_28__ = na
            if method_call('size', sliceLows) > 1:
                __block_result_29__ = na
                for i in pine_range(method_call('size', sliceLows) - 1, 1, 1):
                    getInitialLow = method_call('get', sliceLows, i)
                    getAtr = method_call('get', sliceATR, i)
                    getInitialTime = method_call('get', sliceTime, i)
                    for x in pine_range(i - 1, 0, 1):
                        compare = method_call('get', sliceLows, x)
                        compareTime = method_call('get', sliceTime, x)
                        if compare > getInitialLow - getAtr and compare < getInitialLow + getAtr:
                            if array.size(equalLowsValues.levels) == 0:
                                array.push(equalLowsValues.levels, getInitialLow)
                                array.push(equalLowsValues.times, getInitialTime)
                                equalLowsValues.startTime = getInitialTime
                            array.push(equalLowsValues.levels, compare)
                            array.push(equalLowsValues.times, compareTime)
                            lowFound = True
                        if compare < getInitialLow - getAtr:
                            array.clear(equalLowsValues.levels)
                            array.clear(equalLowsValues.times)
                            equalLowsValues.startTime = NA(int)
                            lowFound = False
                            break
                    __block_result_30__ = na
                    if lowFound:
                        getAvg = array.avg(equalLowsValues.levels)
                        equalLowsValues.connector = line.new(equalLowsValues.startTime, getAvg, rightCoordinate, getAvg, xloc=xloc.bar_time, color=equalLowsCol, style=line.style_dotted)
                        equalLowsValues.connectorLab = label.new(math.round(math.avg(equalLowsValues.startTime, array.last(equalLowsValues.times))), getAvg, xloc=xloc.bar_time, color=color.new('#00000000'), textcolor=equalLowsCol, style=label.style_label_up, size=size.tiny, text='Equal Lows')
                        if not liteMode:
                            for x, price in enumerate(equalLowsValues.levels):
                                getTime__0000027d__ = array.get(equalLowsValues.times, x)
                                array.push(equalLowsValues.radiate, label.new(getTime__0000027d__, price, xloc=xloc.bar_time, text='•', style=label.style_text_outline, color=color.new(equalLowsCol, 80), textcolor=equalLowsCol, size=size.normal))
                                array.push(equalLowsValues.radiate, label.new(getTime__0000027d__, price, xloc=xloc.bar_time, text='•', style=label.style_text_outline, color=color.new(equalLowsCol, 80), textcolor=equalLowsCol, size=size.normal))
                        break
                    __block_result_29__ = __block_result_30__
                __block_result_28__ = __block_result_29__
            __block_result_26__ = __block_result_28__
        return __block_result_26__

    @export
    def quickTime(timeString: str):
        return not na(time('1', timeString, 'America/New_York'))

    @export
    def macros(showMacros: bool, noBorders: bool):
        __block_result_31__ = na
        if showMacros and timeframe.in_seconds('') <= timeframe.in_seconds('5'):
            macro: macros__ren__ = macros__ren__(array.from_items(quickTime('0233-0300'), quickTime('0403-0430'), quickTime('0850-0910'), quickTime('0950-1010'), quickTime('1050-1110'), quickTime('1150-1210'), quickTime('1310-1340'), quickTime('1515-1545')), sessionTimes=array.from_items('London\n02:33-03:00', 'London\n04:03-04:30', 'NY AM\n08:50-09:10', 'NY AM\n09:50-10:10', 'NY AM\n10:50-11:10', 'NY Lunch\n11:50-12:10', 'NY PM\n13:10-13:40', 'NY Last Hr.\n15:15-15:45'))
            macroPrices: Persistent[macros__ren__] = macros__ren__(na, matrix.new(8, 5, initial_value=NA(float)), sessionLines=matrix.new(8, 2, initial_value=NA(Line)))
            macroBoxes: Persistent[list[Box]] = array.new_box()
            macroLabels: Persistent[list[Label]] = array.new_label()
            __block_result_32__ = na
            for i, session__ren__ in enumerate(macro.sessions):
                __block_result_33__ = na
                if session__ren__:
                    if na(matrix.get(macroPrices.prices, i, 0)):
                        matrix.set(macroPrices.prices, i, 0, open)
                        matrix.set(macroPrices.prices, i, 4, time)
                    matrix.set(macroPrices.prices, i, 1, close)
                    matrix.set(macroPrices.prices, i, 2, math.max(high, nz(matrix.get(macroPrices.prices, i, 2))))
                    __block_result_33__ = matrix.set(macroPrices.prices, i, 3, math.min(low, nz(matrix.get(macroPrices.prices, i, 3), 2e+21)))
                else:
                    __block_result_34__ = na
                    if not na(matrix.get(macroPrices.prices, i, 0)):
                        getTop = matrix.get(macroPrices.prices, i, 2)
                        getBot = matrix.get(macroPrices.prices, i, 3)
                        __block_result_35__ = na
                        __switch_4__ = noBorders
                        if __switch_4__ == True:
                            __block_result_35__ = 100
                        else:
                            __block_result_35__ = 25
                        borderTransp = __block_result_35__
                        array.unshift(macroBoxes, box.new(left=cast_int(matrix.get(macroPrices.prices, i, 4)), top=getTop, right=time, bottom=getBot, xloc=xloc.bar_time, bgcolor=color.new(chart.fg_color, 80), border_color=color.new(chart.fg_color, borderTransp), border_style=line.style_dashed))
                        array.unshift(macroLabels, label.new(math.round(math.avg(matrix.get(macroPrices.prices, i, 4), time)), getTop, xloc=xloc.bar_time, color=color.new('#00000000'), textcolor=chart.fg_color, text=array.get(macro.sessionTimes, i), size=size.tiny))
                        if array.size(macroBoxes) > 100:
                            method_call('delete', array.pop(macroBoxes))
                            method_call('delete', array.pop(macroLabels))
                        if last_bar_time - time <= 86400 * 1000 * 2:
                            for lines in macroPrices.sessionLines:
                                method_call('delete', array.get(lines, 0))
                                method_call('delete', array.get(lines, 1))
                            matrix.set(macroPrices.sessionLines, i, 0, line.new(time, getTop, last_bar_time, getTop, color=chart.fg_color, style=line.style_dotted, xloc=xloc.bar_time))
                            matrix.set(macroPrices.sessionLines, i, 1, line.new(time, getBot, last_bar_time, getBot, color=chart.fg_color, style=line.style_dotted, xloc=xloc.bar_time))
                        __block_result_34__ = matrix.fill(macroPrices.prices, na, i, i + 1, 0, 5)
                    __block_result_33__ = __block_result_34__
                __block_result_32__ = __block_result_33__
            __block_result_31__ = __block_result_32__
        return __block_result_31__

    @export
    def po3(tf: str, left: int, right: int, show: bool):
        __block_result_36__ = na
        if show:
            middle = math.round(math.avg(right, left))
            po3__0000033a__: Persistent[po3data] = po3data(high, low, open, close, NA(Box), array.new_line(2), array.new_label(5))
            po3__0000033a__.dHigh = math.max(high, po3__0000033a__.dHigh)
            po3__0000033a__.dLow = math.min(low, po3__0000033a__.dLow)
            po3__0000033a__.dClose = close
            po3Poly: Persistent[list[Polyline]] = array.new(4, NA(Polyline))
            if timeframe.change(tf):
                po3__0000033a__.dHigh = high
                po3__0000033a__.dLow = low
                po3__0000033a__.dOpen = open
            __block_result_37__ = na
            if barstate.islast:
                bodyCol__25 = math.sign(po3__0000033a__.dClose - po3__0000033a__.dOpen)
                __block_result_38__ = na
                __switch_2__ = bodyCol__25
                if __switch_2__ == 1:
                    __block_result_38__ = color.new('#74FFBC')
                elif __switch_2__ == -1:
                    __block_result_38__ = color.rgb(255, 116, 116)
                else:
                    __block_result_38__ = color.gray
                bodyCol = __block_result_38__
                top = math.max(po3__0000033a__.dClose, po3__0000033a__.dOpen)
                bot = math.min(po3__0000033a__.dClose, po3__0000033a__.dOpen)
                if na(po3__0000033a__.po3box):
                    po3__0000033a__.po3box = box.new(bar_index + left, top, bar_index + right, bot, border_color=color.new(color.gray, 25), bgcolor=color.new(bodyCol, 25))
                box.set_lefttop(po3__0000033a__.po3box, bar_index + left, top)
                box.set_rightbottom(po3__0000033a__.po3box, bar_index + right, bot)
                box.set_bgcolor(po3__0000033a__.po3box, color.new(bodyCol, 25))
                coords = array.from_items(chart.point.from_index(bar_index + left, top), chart.point.from_index(bar_index + right, top), chart.point.from_index(bar_index + right, bot), chart.point.from_index(bar_index + left, bot))
                for poly in po3Poly:
                    polyline.delete(poly)
                array.set(po3Poly, 0, polyline.new(coords, line_width=3, line_color=color.new(bodyCol, 80), xloc=xloc.bar_index, closed=True))
                array.set(po3Poly, 1, polyline.new(coords, line_width=6, line_color=color.new(bodyCol, 95), xloc=xloc.bar_index, closed=True))
                coords = array.from_items(chart.point.from_index(bar_index + middle, top), chart.point.from_index(bar_index + middle, po3__0000033a__.dHigh))
                array.set(po3Poly, 2, polyline.new(coords, line_width=3, line_color=color.new(color.gray, 80), xloc=xloc.bar_index, closed=True))
                coords = array.from_items(chart.point.from_index(bar_index + middle, bot), chart.point.from_index(bar_index + middle, po3__0000033a__.dLow))
                array.set(po3Poly, 3, polyline.new(coords, line_width=3, line_color=color.new(color.gray, 80), xloc=xloc.bar_index, closed=True))
                if na(array.first(po3__0000033a__.po3line)):
                    array.set(po3__0000033a__.po3line, 0, line.new(bar_index + middle, top, bar_index + middle, po3__0000033a__.dHigh, color=color.gray))
                    array.set(po3__0000033a__.po3line, 1, line.new(bar_index + middle, bot, bar_index + middle, po3__0000033a__.dLow, color=color.gray))
                method_call('set_xy1', array.first(po3__0000033a__.po3line), bar_index + middle, top)
                method_call('set_xy2', array.first(po3__0000033a__.po3line), bar_index + middle, po3__0000033a__.dHigh)
                method_call('set_xy1', array.get(po3__0000033a__.po3line, 1), bar_index + middle, bot)
                method_call('set_xy2', array.get(po3__0000033a__.po3line, 1), bar_index + middle, po3__0000033a__.dLow)
                if timeframe.change(''):
                    for lab in po3__0000033a__.po3Labels:
                        label.delete(lab)
                __block_result_39__ = na
                for i in pine_range(0, 4, 1):
                    y__27 = i % 5
                    __block_result_40__ = na
                    __switch_3__ = y__27
                    if __switch_3__ == 0:
                        __block_result_40__ = po3__0000033a__.dOpen
                    elif __switch_3__ == 1:
                        __block_result_40__ = po3__0000033a__.dClose
                    elif __switch_3__ == 2:
                        __block_result_40__ = po3__0000033a__.dHigh
                    elif __switch_3__ == 3:
                        __block_result_40__ = po3__0000033a__.dLow
                    else:
                        __block_result_40__ = po3__0000033a__.dHigh
                    y = __block_result_40__
                    __block_result_41__ = na
                    if i != 4:
                        __block_result_42__ = na
                        if na(array.get(po3__0000033a__.po3Labels, i)):
                            __block_result_42__ = array.push(po3__0000033a__.po3Labels, label.new(bar_index + right, y, text=string.tostring(y, format.mintick), color=color.new('#00000000'), style=label.style_label_left, textcolor=color.new(chart.fg_color, 25), size=size.tiny))
                        else:
                            method_call('set_xy', array.get(po3__0000033a__.po3Labels, i), bar_index + right, y)
                            __block_result_42__ = method_call('set_text', array.get(po3__0000033a__.po3Labels, i), string.tostring(y, format.mintick))
                        __block_result_41__ = __block_result_42__
                    else:
                        __block_result_43__ = na
                        if na(array.get(po3__0000033a__.po3Labels, i)):
                            __block_result_43__ = array.push(po3__0000033a__.po3Labels, label.new(bar_index + middle, y, text=pct.secondsToTfString(timeframe.in_seconds(tf)), color=color.new('#00000000'), style=label.style_label_down, textcolor=color.new(chart.fg_color, 25), size=size.tiny))
                        else:
                            method_call('set_xy', array.get(po3__0000033a__.po3Labels, i), bar_index + right, y)
                            __block_result_43__ = method_call('set_text', array.get(po3__0000033a__.po3Labels, i), pct.secondsToTfString(timeframe.in_seconds(tf)))
                        __block_result_41__ = __block_result_43__
                    __block_result_39__ = __block_result_41__
                __block_result_37__ = __block_result_39__
            __block_result_36__ = __block_result_37__
        return __block_result_36__

    @export
    def silverBullet(silverBulletStratLong: bool, silverBulletStratShort: bool, future: int, userTF: int, H: float, L: float, H2: float, L2: float, noBorders: bool, silverBulletLongTP: silverBulletLevels, historicalPoints: list[ChartPoint], historicalData: necessaryData__ren__, silverBulletLongSL: silverBulletLevels, silverBulletShortTP: silverBulletLevels, silverBulletShortSL: silverBulletLevels):
        if silverBulletStratLong or silverBulletStratShort:
            if timeframe.in_seconds('') > timeframe.in_seconds('5'):
                tab: Persistent = table.new(position.middle_center, 99, 99, na)
                method_call('cell', tab, 0, 0, 'Please Use 5-Minute Timeframe Or Lower For Silver Bullet', text_color=chart.fg_color, text_size=size.huge)
            else:
                bias: Persistent[str] = ''
                HTFdirection = IQZZ(2, '15')
                sbDrawings: Persistent[silverBulletDrawings] = silverBulletDrawings()
                sessionsTrailing: Persistent[list[silverBullet__ren__]] = na(list[silverBullet__ren__])
                sessionsArr = array.from_items(silverBullet__ren__(quickTime('0300-0400'), 'London Open\n3:00 - 4:00'), silverBullet__ren__(quickTime('1000-1100'), 'NYAM\n10:00 - 11:00'), silverBullet__ren__(quickTime('1400-1500'), 'NYPM\n14:00 - 15:00'))
                sessionValues: Persistent[list[silverBullet__ren__]] = array.new(0, NA(silverBullet__ren__))
                drawingsCopy: Persistent[silverBulletDrawings] = na(silverBulletDrawings)
                isActive: bool = False
                openTrades = strategy.opentrades - 1
                closedTrades = strategy.closedtrades - 1
                if strategy.opentrades > 0 or (not method_call('first', sessionsArr).session__ren__ and (not method_call('get', sessionsArr, 1).session__ren__) and (not method_call('last', sessionsArr).session__ren__)):
                    strategy.cancel('Long Silver Bullet')
                    strategy.cancel('Short Silver Bullet')
                if array.size(sessionValues) > 0:
                    last = array.last(sessionValues)
                    if not na(last.sessionFVGdraw):
                        method_call('set_right', last.sessionFVGdraw, future)
                    if string.contains(strategy.opentrades.entry_id(openTrades), 'Silver Bullet') and strategy.opentrades.entry_bar_index(openTrades) == bar_index or (string.contains(strategy.closedtrades.entry_id(closedTrades), 'Silver Bullet') and strategy.closedtrades.entry_bar_index(closedTrades) == bar_index):
                        last.traded = True
                        last.sessionFVGdraw = NA(Box)
                        drawingsCopy = silverBulletDrawings(udt_copy(sbDrawings.tpLine), udt_copy(sbDrawings.tpLabel), udt_copy(sbDrawings.slLine), udt_copy(sbDrawings.slLabel))
                        line.delete(sbDrawings.tpLine)
                        label.delete(sbDrawings.tpLabel)
                        line.delete(sbDrawings.slLine)
                        label.delete(sbDrawings.slLabel)
                if not na(drawingsCopy):
                    if not na(drawingsCopy.tpLine):
                        line.set_x2(drawingsCopy.tpLine, future)
                        label.set_x(drawingsCopy.tpLabel, future)
                        line.set_x2(drawingsCopy.slLine, future)
                        label.set_x(drawingsCopy.slLabel, future)
                        if strategy.closedtrades.exit_bar_index(closedTrades) == bar_index:
                            if strategy.closedtrades.entry_id(closedTrades) == 'Long Silver Bullet':
                                switch_var_29 = strategy.closedtrades.exit_price(closedTrades) >= strategy.closedtrades.entry_price(closedTrades)
                                __switch_6__ = switch_var_29
                                if __switch_6__ == True:
                                    drawingsCopy.tpLine = NA(Line)
                                    drawingsCopy.tpLabel = NA(Label)
                                    line.delete(drawingsCopy.slLine)
                                    label.delete(drawingsCopy.slLabel)
                                else:
                                    drawingsCopy.slLine = NA(Line)
                                    drawingsCopy.slLabel = NA(Label)
                                    line.delete(drawingsCopy.tpLine)
                                    label.delete(drawingsCopy.tpLabel)
                            else:
                                switch_var_31 = strategy.closedtrades.exit_price(closedTrades) <= strategy.closedtrades.entry_price(closedTrades)
                                __switch_6__ = switch_var_31
                                if __switch_6__ == True:
                                    drawingsCopy.tpLine = NA(Line)
                                    drawingsCopy.tpLabel = NA(Label)
                                    line.delete(drawingsCopy.slLine)
                                    label.delete(drawingsCopy.slLabel)
                                else:
                                    drawingsCopy.slLine = NA(Line)
                                    drawingsCopy.slLabel = NA(Label)
                                    line.delete(drawingsCopy.tpLine)
                                    label.delete(drawingsCopy.tpLabel)
                if silverBulletStratLong or silverBulletStratShort:
                    isLastBar_1 = isLastBar(userTF)
                    if not na(sessionsTrailing) and barstate.isconfirmed and isLastBar_1:
                        for i, data in enumerate(sessionsArr):
                            if data.session__ren__:
                                isActive = True
                                if not array.get(sessionsTrailing, i).session__ren__:
                                    if array.size(sessionValues) > 0:
                                        method_call('delete', array.last(sessionValues).sessionFVGdraw)
                                    array.clear(sessionValues)
                                    __block_result_44__ = na
                                    __switch_7__ = HTFdirection
                                    if __switch_7__ == 1:
                                        __block_result_44__ = 'Bullish'
                                    elif __switch_7__ == -1:
                                        __block_result_44__ = 'Bearish'
                                    bias = __block_result_44__
                                    array.push(sessionValues, silverBullet__ren__(data.session__ren__, data.sessionStr, bias, sessionDraw=box.new(time, high, future, low, bgcolor=color.new(chart.fg_color, 95), border_color=chart.fg_color, xloc=xloc.bar_time, border_style=line.style_dashed), sessionDrawLabel=label.new(time, high, color=color.new('#00000000'), textcolor=chart.fg_color, xloc=xloc.bar_time, text=data.sessionStr, size=size.small)))
                                elif array.size(sessionValues) > 0:
                                    getSessionValues = array.last(sessionValues)
                                    getSessionValues.sessionHigh = math.max(H, getSessionValues.sessionHigh)
                                    getSessionValues.sessionLow = math.min(L, getSessionValues.sessionLow)
                                    method_call('set_top', getSessionValues.sessionDraw, getSessionValues.sessionHigh)
                                    method_call('set_rightbottom', getSessionValues.sessionDraw, future, getSessionValues.sessionLow)
                                    method_call('set_xy', getSessionValues.sessionDrawLabel, math.round(math.avg(method_call('get_left', getSessionValues.sessionDraw), method_call('get_right', getSessionValues.sessionDraw))), getSessionValues.sessionHigh)
                                    if bias == 'Bullish' and strategy.opentrades == 0 and (not getSessionValues.traded) and silverBulletStratLong:
                                        if H2 < L:
                                            getSessionValues.sessionFVG = L
                                            method_call('delete', getSessionValues.sessionFVGdraw)
                                            __block_result_45__ = na
                                            __switch_9__ = noBorders
                                            if __switch_9__ == True:
                                                __block_result_45__ = 100
                                            else:
                                                __block_result_45__ = 25
                                            borderTransp: Persistent = __block_result_45__
                                            getSessionValues.sessionFVGdraw = box.new(time, L, future, H2, border_color=color.new(color.new('#74FFBC'), borderTransp), bgcolor=color.new(color.new('#74FFBC'), 95), xloc=xloc.bar_time, text='FVG', text_size=size.small, text_halign=text.align_left, text_color=chart.fg_color)
                                            tp = NA(float)
                                            sl = NA(float)
                                            tpTime = NA(int)
                                            slTime = NA(int)
                                            if silverBulletLongTP == silverBulletLevels.sH:
                                                if array.size(historicalPoints) > 0:
                                                    for dataPoints in historicalPoints:
                                                        if dataPoints.price > H:
                                                            tp = dataPoints.price
                                                            tpTime = dataPoints.time
                                                            break
                                            else:
                                                dayHigh, dayHigh1 = request.security('', '1D', (high, high[1]), lookahead=barmerge.lookahead_on)
                                                __block_result_46__ = na
                                                if dayHigh1 > L:
                                                    __block_result_46__ = dayHigh1
                                                else:
                                                    __block_result_46__ = dayHigh
                                                tp = __block_result_46__
                                                for x, highs in enumerate(historicalData.highArr):
                                                    if highs == tp:
                                                        tpTime = array.get(historicalData.timeArr, x)
                                                        break
                                            if silverBulletLongSL == silverBulletLevels.sL:
                                                if array.size(historicalPoints) > 0:
                                                    for dataPoints in historicalPoints:
                                                        if dataPoints.price < L:
                                                            sl = dataPoints.price
                                                            slTime = dataPoints.time
                                                            break
                                            else:
                                                dayLow, dayLow1 = request.security('', '1D', (low, low[1]), lookahead=barmerge.lookahead_on)
                                                __block_result_47__ = na
                                                if dayLow1 < L:
                                                    __block_result_47__ = dayLow1
                                                else:
                                                    __block_result_47__ = dayLow
                                                sl = __block_result_47__
                                                for x, lows in enumerate(historicalData.lowArr):
                                                    if lows == sl:
                                                        slTime = array.get(historicalData.timeArr, x)
                                                        break
                                            if not na(tp) and (not na(sl)) and (close > L):
                                                line.delete(sbDrawings.tpLine)
                                                label.delete(sbDrawings.tpLabel)
                                                sbDrawings.tpLine = line.new(tpTime, tp, future, tp, xloc=xloc.bar_time, color=color.new('#74FFBC'), style=line.style_dotted)
                                                sbDrawings.tpLabel = label.new(future, tp, text='Silver Bullet TP\n' + string.tostring(silverBulletLongTP), size=size.small, style=label.style_label_lower_right, color=color.new('#00000000'), textcolor=color.new('#74FFBC'), xloc=xloc.bar_time)
                                                line.delete(sbDrawings.slLine)
                                                label.delete(sbDrawings.slLabel)
                                                sbDrawings.slLine = line.new(slTime, sl, future, sl, xloc=xloc.bar_time, color=color.rgb(255, 116, 116), style=line.style_dotted)
                                                sbDrawings.slLabel = label.new(future, sl, text='Silver Bullet SL\n' + string.tostring(silverBulletLongSL), size=size.small, style=label.style_label_upper_right, color=color.new('#00000000'), textcolor=color.rgb(255, 116, 116), xloc=xloc.bar_time)
                                                strategy.entry('Long Silver Bullet', strategy.long, limit=L)
                                                strategy.exit('Long Silver Bullet Exit', 'Long Silver Bullet', limit=tp, stop=sl)
                                        if not na(getSessionValues.sessionFVGdraw):
                                            method_call('set_right', getSessionValues.sessionFVGdraw, future)
                                        continue
                                    if bias == 'Bearish' and strategy.opentrades == 0 and (not getSessionValues.traded) and silverBulletStratShort:
                                        if L2 > H:
                                            getSessionValues.sessionFVG = H
                                            method_call('delete', getSessionValues.sessionFVGdraw)
                                            __block_result_48__ = na
                                            __switch_9__ = noBorders
                                            if __switch_9__ == True:
                                                __block_result_48__ = 100
                                            else:
                                                __block_result_48__ = 25
                                            borderTransp: Persistent = __block_result_48__
                                            getSessionValues.sessionFVGdraw = box.new(time, H, future, L2, border_color=color.new(color.red, borderTransp), bgcolor=color.new(color.red, 95), xloc=xloc.bar_time, text='FVG', text_size=size.small, text_halign=text.align_left, text_color=chart.fg_color)
                                            tp = NA(float)
                                            sl = NA(float)
                                            tpTime = NA(int)
                                            slTime = NA(int)
                                            if silverBulletShortTP == silverBulletLevels.sL:
                                                if array.size(historicalPoints) > 0:
                                                    for dataPoints in historicalPoints:
                                                        if dataPoints.price < L:
                                                            tp = dataPoints.price
                                                            tpTime = dataPoints.time
                                                            break
                                            else:
                                                dayLow, dayLow1 = request.security('', '1D', (low, low[1]), lookahead=barmerge.lookahead_on)
                                                __block_result_49__ = na
                                                if dayLow1 < H:
                                                    __block_result_49__ = dayLow1
                                                else:
                                                    __block_result_49__ = dayLow
                                                tp = __block_result_49__
                                                for x, lows in enumerate(historicalData.lowArr):
                                                    if lows == tp:
                                                        tpTime = array.get(historicalData.timeArr, x)
                                                        break
                                            if silverBulletLongSL == silverBulletLevels.sH:
                                                if array.size(historicalPoints) > 0:
                                                    for dataPoints in historicalPoints:
                                                        if dataPoints.price > H:
                                                            sl = dataPoints.price
                                                            slTime = dataPoints.time
                                                            label.new(slTime, sl, xloc=xloc.bar_time)
                                                            break
                                            else:
                                                dayHigh, dayHigh1 = request.security('', '1D', (high, high[1]), lookahead=barmerge.lookahead_on)
                                                __block_result_50__ = na
                                                if dayHigh1 > H:
                                                    __block_result_50__ = dayHigh1
                                                else:
                                                    __block_result_50__ = dayHigh
                                                sl = __block_result_50__
                                                for x, highs in enumerate(historicalData.highArr):
                                                    if highs == sl:
                                                        slTime = array.get(historicalData.timeArr, x)
                                                        break
                                            if not na(tp) and (not na(sl)) and (close < H):
                                                line.delete(sbDrawings.tpLine)
                                                label.delete(sbDrawings.tpLabel)
                                                sbDrawings.tpLine = line.new(tpTime, tp, future, tp, xloc=xloc.bar_time, color=color.new('#74FFBC'), style=line.style_dotted)
                                                sbDrawings.tpLabel = label.new(future, tp, text='Silver Bullet TP\n' + string.tostring(silverBulletShortTP), size=size.small, style=label.style_label_upper_right, color=color.new('#00000000'), textcolor=color.new('#74FFBC'), xloc=xloc.bar_time)
                                                line.delete(sbDrawings.slLine)
                                                label.delete(sbDrawings.slLabel)
                                                sbDrawings.slLine = line.new(slTime, sl, future, sl, xloc=xloc.bar_time, color=color.rgb(255, 116, 116), style=line.style_dotted)
                                                sbDrawings.slLabel = label.new(future, sl, text='Silver Bullet SL\n' + string.tostring(silverBulletShortSL), size=size.small, style=label.style_label_lower_right, color=color.new('#00000000'), textcolor=color.rgb(255, 116, 116), xloc=xloc.bar_time)
                                                strategy.entry('Short Silver Bullet', strategy.short, limit=H)
                                                strategy.exit('Short Silver Bullet Exit', 'Short Silver Bullet', limit=tp, stop=sl)
                                        if not na(getSessionValues.sessionFVGdraw):
                                            method_call('set_right', getSessionValues.sessionFVGdraw, future)
                    sessionsTrailing = udt_copy(sessionsArr)
        return 0

    @export
    @method
    def invalidFVGcheck(FVGarr: list[FVG], upFVGpricesSorted: list[float], dnFVGpricesSorted: list[float]):
        getMax = array.max(upFVGpricesSorted)
        getMin = array.min(dnFVGpricesSorted)
        isHigher = close < getMax
        isLower = close > getMin
        if array.size(FVGarr) > 0:
            if isHigher or isLower:
                for i in pine_range(array.size(FVGarr) - 1, 0, 1):
                    data = array.get(FVGarr, i)
                    if isHigher:
                        if data.direction == 'Up':
                            if close < data.H:
                                if not na(data.fvgBox):
                                    method_call('delete', data.fvgBox)
                                array.remove(FVGarr, i)
                            continue
                    if isLower:
                        if data.direction == 'Down':
                            if close > data.L:
                                if not na(data.fvgBox):
                                    method_call('delete', data.fvgBox)
                                array.remove(FVGarr, i)
            if isHigher:
                getIndex = array.binary_search_rightmost(upFVGpricesSorted, close)
                slice = array.slice(upFVGpricesSorted, math.min(getIndex, array.size(upFVGpricesSorted) - 1), array.size(upFVGpricesSorted))
                method_call('clear', slice)
            if isLower:
                getIndex = array.binary_search_rightmost(dnFVGpricesSorted, close)
                slice = array.slice(dnFVGpricesSorted, 0, getIndex)
                method_call('clear', slice)
        return 0

    @export
    @method
    def drawFVG(counter: dict[str, int], FVGshow: int, FVGname: str, FVGcol: Color, data: FVG, masterCoords: dict[str, float], labelLevels: str, borderTransp: int, liteMode: bool, rightCoordinate: int):
        count = map.get(counter, FVGname)
        __block_result_51__ = na
        if count < FVGshow:
            if na(map.get(masterCoords, FVGname)) and FVGshow != 0:
                map.put(masterCoords, FVGname, math.avg(data.H, data.L))
            __block_result_52__ = na
            __switch_1__ = labelLevels == 'Inside'
            if __switch_1__ == True:
                __block_result_52__ = 'FVG'
            else:
                __block_result_52__ = ''
            txt = __block_result_52__
            __block_result_53__ = (na, na)
            __switch_1__ = count == 0
            if __switch_1__ == True:
                __block_result_53__ = (color.new('#00000000'), color.new('#00000000'))
            else:
                __block_result_53__ = (color.new(FVGcol, borderTransp), color.new(FVGcol, 75))
            bordCol, bgCol = __block_result_53__
            if count == 0 and liteMode:
                bordCol = color.new(FVGcol, borderTransp)
                bgCol = color.new(FVGcol, 75)
            data.fvgBox = box.new(data.T, data.H, rightCoordinate, data.L, bgcolor=bgCol, border_color=bordCol, xloc=xloc.bar_time, text=txt, text_halign=text.align_right, text_color=color.new(chart.fg_color, 25))
            if labelLevels == 'Outside':
                data.fvgLabel = label.new(rightCoordinate, math.avg(data.H, data.L), color=color.new('#00000000'), textcolor=FVGcol, xloc=xloc.bar_time, text='FVG', style=label.style_label_left, size=size.tiny)
            if count == 0 and (not liteMode):
                gradientBoxes: Persistent[list[Box]] = array.new_box(20)
                gradBoxes(gradientBoxes, FVGcol, data.T, data.L, data.H, rightCoordinate)
            __block_result_51__ = map.put(counter, FVGname, map.get(counter, FVGname) + 1)
        return __block_result_51__

    @export
    def invalidBlockCheck(bullishOBbox: list[orderBlock], bearishOBbox: list[orderBlock], userTF: int):
        isLastBar_1 = isLastBar(userTF)
        if array.size(bullishOBbox) > 0 and barstate.isconfirmed and isLastBar_1:
            for i in pine_range(array.size(bullishOBbox) - 1, 0, 1):
                getOrderBlock = array.get(bullishOBbox, i)
                getTop = method_call('get', getOrderBlock.orderBlockData, 1)
                getBot = method_call('last', getOrderBlock.orderBlockData)
                if getOrderBlock.vioCount == 0:
                    if close < getBot:
                        getOrderBlock.vioCount = getOrderBlock.vioCount + 1
                        getOrderBlock.status = 'BB'
                else:
                    if close > getTop:
                        method_call('delete', array.remove(bullishOBbox, i).orderBlockBox)
        isLastBar_2 = isLastBar(userTF)
        if array.size(bearishOBbox) > 0 and barstate.isconfirmed and isLastBar_2:
            for i in pine_range(array.size(bearishOBbox) - 1, 0, 1):
                getOrderBlock = array.get(bearishOBbox, i)
                getBot = method_call('last', getOrderBlock.orderBlockData)
                getTop = method_call('get', getOrderBlock.orderBlockData, 1)
                if getOrderBlock.vioCount == 0:
                    if close > getTop:
                        getOrderBlock.vioCount = getOrderBlock.vioCount + 1
                        getOrderBlock.status = 'BB'
                else:
                    if close < getBot:
                        method_call('delete', array.remove(bearishOBbox, i).orderBlockBox)
        return 0

    @export
    @method
    def lastBarRejections(id: list[rejectionBlocks], rejectionColor: Color, idShow: int, rejectionString: str, labelLevels: str, borderTransp: int, liteMode: bool, rightCoordinate: int, masterCoords: dict[str, float]):
        __block_result_54__ = na
        if barstate.islast:
            __block_result_55__ = na
            if array.size(id) > 0:
                countRB: int = 0
                __block_result_56__ = na
                __switch_2__ = labelLevels == 'Inside'
                if __switch_2__ == True:
                    __block_result_56__ = 'RB'
                else:
                    __block_result_56__ = ''
                txt = __block_result_56__
                __block_result_57__ = (na, na)
                __switch_2__ = countRB == 0
                if __switch_2__ == True:
                    __block_result_57__ = (color.new('#00000000'), color.new('#00000000'))
                else:
                    __block_result_57__ = (color.new(rejectionColor, borderTransp), color.new(rejectionColor, 75))
                bordCol, bgCol = __block_result_57__
                if countRB == 0 and liteMode:
                    bordCol = color.new(rejectionColor, borderTransp)
                    bgCol = color.new(rejectionColor, 75)
                __block_result_58__ = na
                for i, data in enumerate(id):
                    box.delete(data.rejectionBox)
                    if labelLevels == 'Outside':
                        label.delete(data.rejectionLabel)
                    __block_result_59__ = na
                    if countRB < idShow:
                        data.rejectionBox = box.new(data.rejectionPoint.time, data.rejectionPoint.price, rightCoordinate, data.bodyPrice, xloc=xloc.bar_time, bgcolor=bgCol, border_color=bordCol, text=txt, text_color=color.new(chart.fg_color, 25), text_halign=text.align_right)
                        avg = math.avg(data.rejectionPoint.price, data.bodyPrice)
                        if labelLevels == 'Outside':
                            data.rejectionLabel = label.new(rightCoordinate, avg, xloc=xloc.bar_time, size=size.tiny, text='RB', color=color.new('#00000000'), style=label.style_label_left, textcolor=rejectionColor)
                        if countRB == 0 and (not liteMode):
                            map.put(masterCoords, rejectionString, data.rejectionPoint.price)
                            bottom: float = data.bodyPrice
                            top = data.rejectionPoint.price
                            gradientBoxes: Persistent[list[Box]] = array.new_box(20)
                            gradBoxes(gradientBoxes, rejectionColor, data.rejectionPoint.time, bottom, top, rightCoordinate)
                        countRB = countRB + 1
                        __block_result_59__ = countRB
                    __block_result_58__ = __block_result_59__
                __block_result_55__ = __block_result_58__
            __block_result_54__ = __block_result_55__
        return __block_result_54__

    @export
    @method
    def OBdraw(id: list[orderBlock], OBshow: int, BBshow: int, OBcol: Color, BBcol: Color, bullishString: str, bearishString: str, isBullish: bool, labelLevels: str, borderTransp: int, liteMode: bool, rightCoordinate: int, masterCoords: dict[str, float]):
        __block_result_60__ = na
        if barstate.islast:
            countOB: int = 0
            countBB: int = 0
            __block_result_61__ = na
            if array.size(id) > 0:
                __block_result_62__ = na
                for i in pine_range(0, array.size(id) - 1, 1):
                    getData = array.get(id, i)
                    method_call('delete', getData.orderBlockBox)
                    if labelLevels == 'Outside':
                        method_call('delete', getData.orderBlockLab)
                    if countOB < OBshow:
                        if getData.status == 'OB':
                            halign = text.align_right
                            __block_result_63__ = na
                            __switch_5__ = labelLevels == 'Inside'
                            if __switch_5__ == True:
                                __block_result_63__ = 'OB'
                            else:
                                __block_result_63__ = ''
                            txt = __block_result_63__
                            __block_result_64__ = (na, na)
                            __switch_5__ = countOB == 0
                            if __switch_5__ == True:
                                __block_result_64__ = (color.new('#00000000'), color.new('#00000000'))
                            else:
                                __block_result_64__ = (color.new(OBcol, borderTransp), color.new(OBcol, 75))
                            bordCol, bgCol = __block_result_64__
                            if countOB == 0 and liteMode:
                                bordCol = color.new(OBcol, borderTransp)
                                bgCol = color.new(OBcol, 75)
                            getData.orderBlockBox = box.new(cast_int(method_call('first', getData.orderBlockData)), method_call('get', getData.orderBlockData, 1), rightCoordinate, method_call('last', getData.orderBlockData), border_color=bordCol, bgcolor=bgCol, xloc=xloc.bar_time, border_style=line.style_solid, text=txt, text_halign=halign, text_color=color.new(chart.fg_color, 25))
                            if labelLevels == 'Outside':
                                getData.orderBlockLab = label.new(rightCoordinate, math.avg(method_call('get', getData.orderBlockData, 1), method_call('last', getData.orderBlockData)), color=color.new('#00000000'), textcolor=OBcol, text='OB', style=label.style_label_left, xloc=xloc.bar_time, size=size.tiny)
                            if countOB == 0 and (not liteMode):
                                bottom = method_call('last', getData.orderBlockData)
                                top = method_call('get', getData.orderBlockData, 1)
                                avg = math.avg(top, bottom)
                                gradientBoxes: Persistent[list[Box]] = array.new_box(20)
                                gradBoxes(gradientBoxes, OBcol, cast_int(method_call('first', getData.orderBlockData)), bottom, top, rightCoordinate)
                            countOB = countOB + 1
                            __block_result_65__ = na
                            __switch_5__ = isBullish
                            if __switch_5__ == True:
                                __block_result_65__ = bullishString
                            else:
                                __block_result_65__ = bearishString
                            str__ren__ = __block_result_65__
                            if na(map.get(masterCoords, str__ren__)) and OBshow != 0:
                                map.put(masterCoords, str__ren__, math.avg(method_call('get_top', getData.orderBlockBox), method_call('get_bottom', getData.orderBlockBox)))
                    __block_result_66__ = na
                    if countBB < BBshow:
                        __block_result_67__ = na
                        if getData.status == 'BB':
                            halign = text.align_right
                            __block_result_68__ = na
                            __switch_5__ = labelLevels == 'Inside'
                            if __switch_5__ == True:
                                __block_result_68__ = 'BB'
                            else:
                                __block_result_68__ = ''
                            txt = __block_result_68__
                            __block_result_69__ = (na, na)
                            __switch_5__ = countBB == 0
                            if __switch_5__ == True:
                                __block_result_69__ = (color.new('#00000000'), color.new('#00000000'))
                            else:
                                __block_result_69__ = (color.new(BBcol, borderTransp), color.new(BBcol, 75))
                            bordCol, bgCol = __block_result_69__
                            if countBB == 0 and liteMode:
                                bordCol = color.new(BBcol, borderTransp)
                                bgCol = color.new(BBcol, 75)
                            getData.orderBlockBox = box.new(cast_int(method_call('first', getData.orderBlockData)), method_call('get', getData.orderBlockData, 1), rightCoordinate, method_call('last', getData.orderBlockData), border_color=bordCol, bgcolor=bgCol, xloc=xloc.bar_time, border_style=line.style_solid, text=txt, text_halign=halign, text_color=color.new(chart.fg_color, 25))
                            if labelLevels == 'Outside':
                                getData.orderBlockLab = label.new(rightCoordinate, math.avg(method_call('get', getData.orderBlockData, 1), method_call('last', getData.orderBlockData)), color=color.new('#00000000'), textcolor=BBcol, text='BB', style=label.style_label_left, xloc=xloc.bar_time, size=size.tiny)
                            if countBB == 0 and (not liteMode):
                                bottom = method_call('last', getData.orderBlockData)
                                top = method_call('get', getData.orderBlockData, 1)
                                gradientBoxes: Persistent[list[Box]] = array.new_box(20)
                                gradBoxes(gradientBoxes, BBcol, cast_int(method_call('first', getData.orderBlockData)), bottom, top, rightCoordinate)
                            countBB = countBB + 1
                            __block_result_70__ = na
                            __switch_5__ = isBullish
                            if __switch_5__ == True:
                                __block_result_70__ = bearishString
                            else:
                                __block_result_70__ = bullishString
                            str__ren__ = __block_result_70__
                            __block_result_71__ = na
                            if na(map.get(masterCoords, str__ren__)) and BBshow != 0:
                                __block_result_71__ = map.put(masterCoords, str__ren__, math.avg(method_call('get_top', getData.orderBlockBox), method_call('get_bottom', getData.orderBlockBox)))
                            __block_result_67__ = __block_result_71__
                        __block_result_66__ = __block_result_67__
                    __block_result_62__ = __block_result_66__
                __block_result_61__ = __block_result_62__
            __block_result_60__ = __block_result_61__
        return __block_result_60__


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
