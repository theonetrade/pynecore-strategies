"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, box, close, color, display,
    extend, high, input, last_bar_index, line, location, log, low, math, na, nz, open, plot,
    plotshape, script, shape, size, string, ta, time, xloc
)
from pynecore.types import Color, Line, NA, Persistent


@udt
class liqInfo:
    startTime: int = na(int)
    endTime: int = na(int)
    price: float = na(float)
    liqType: str = na(str)
    grabsFound: int = 0


@udt
class liq:
    info: 'liqInfo' = _dataclass_field(default_factory=lambda: na(liqInfo))
    isRendered: bool = False
    liqZone: Line = na(Line)


@udt
class liqGrabZone:
    startTime: int = na(int)
    endTime: int = na(int)
    priceHigh: float = na(float)
    priceLow: float = na(float)
    liqType: str = na(str)
    disabled: bool = False
    ephemeral: bool = False


DEBUG: bool = False
SHOW_LAST_X: int = 500
MAX_ZONES: int = 100
EXTEND_ZONES_BY: int = 15
RETEST_COOLDOWN: int = 5
MIN_ZONE_SIZE: int = 3
LINE_COLOR: Color = color.white
LINE_STYLE: str = '----'


@script.indicator(title='Liquidity Grab Zones | Flux Charts', overlay=True, max_boxes_count=500, max_labels_count=500, max_lines_count=500, max_bars_back=1005)
def main(
    maxDistanceString=input.string('Normal', 'Max Distance To Last Bar', options=('Normal', 'Low'), group='General Configuration', display=display.none),
    pivotLenLiq=input.int(25, 'Pivot Length', group='General Configuration', display=display.none),
    WBR=input.float(0.5, 'Wick-Body Ratio', step=0.1, group='General Configuration', display=display.none),
    zoneInvalidation=input.string('Close', 'Zone Invalidation', group='General Configuration', options=('Wick', 'Close'), display=display.none),
    retestsEnabled=input.bool(True, 'Retests', inline='rb', group='General Configuration', display=display.none),
    breaksEnabled=input.bool(False, 'Breaks', inline='rb', group='General Configuration', display=display.none),
    inverseZones=input.bool(True, 'Inverse Zones After Broken', group='General Configuration', display=display.none),
    showInvalidated=input.bool(True, 'Show Historic Zones', group='General Configuration', display=display.none),
    sellsideColor=input(color.new('#08998180'), 'Bullish', inline='bsColor', group='General Configuration', display=display.none),
    buysideColor=input(color.new('#F2364680'), 'Bearish', inline='bsColor', group='General Configuration', display=display.none),
    __input_10__=input.bool(True, '[DBG] Combine Zones', group='Debug', display=display.none),
    __input_11__=input.int(5, '[DBG] Base Bubble Size', group='Style', display=display.none),
    __input_12__=input.int(0, '[DBG] Min Distance', group='Style', display=display.none),
    __input_13__=input.int(1, '[DBG] Max Grabs Per Zone', group='Style', display=display.none),
    __input_14__=input.float(1, '[DBG] Min ATR Between Pivots', group='Style', display=display.none),
    __input_15__=input.float(20, '[DBG] Bubble Offset', group='Style', display=display.none),
    __input_16__=input.color(color.new('#FFFFFF80'), '[DBG] Text Color', group='Style', inline='BBcolors'),
    __input_17__=input.bool(False, '[DBG] Render Liquidity Zones', group='Style'),
    __input_18__=input.bool(True, '[DBG] Render Bubbles', group='Style'),
    __input_19__=input.bool(True, '[DBG] Render Liquidity Grab Zones', group='Style'),
    __input_20__=input.bool(True, '[DBG] Place Labels At Same Level', group='Style')
):
    MAX_DISTANCE: int = 500
    combineZones = __input_10__ if DEBUG else True
    bubbleSize = __input_11__ if DEBUG else 5
    minDist = __input_12__ if DEBUG else 0
    grabsPerZone = __input_13__ if DEBUG else 1
    minATRBetweenPivots = __input_14__ if DEBUG else 1
    bubbleOffset = __input_15__ if DEBUG else 20
    textColor = __input_16__ if DEBUG else color.new('#FFFFFF80')
    renderLiqZones = __input_17__ if DEBUG else False
    renderBubbles = __input_18__ if DEBUG else False
    renderLiqGrabZones = __input_19__ if DEBUG else True
    labelsAtSameLevel = __input_20__ if DEBUG else True
    MAX_DISTANCE = 150 if maxDistanceString == 'Low' else 500 if maxDistanceString == 'Normal' else 750
    def safeDeleteLiq(liqF: liq):
        liqF.isRendered = False
        return line.delete(liqF.liqZone)

    allLiqList: Persistent[list[liq]] = array.new(0, NA(liq))
    allLiqGrabZones: Persistent[list[liqGrabZone]] = array.new(0, NA(liqGrabZone))
    highestTALiq = ta.pivothigh(pivotLenLiq, pivotLenLiq)
    lowestTALiq = ta.pivotlow(pivotLenLiq, pivotLenLiq)
    curATR = ta.atr(5)
    def renderLiq(liqF: liq):
        __block_result__ = na
        if renderLiqZones:
            liqF.liqZone = line.new(liqF.info.startTime, liqF.info.price, nz(liqF.info.endTime, time + 1), liqF.info.price, xloc=xloc.bar_time, color=buysideColor if liqF.info.liqType == 'Buyside' else sellsideColor)
            __block_result__ = liqF.liqZone
        return __block_result__

    def handleLiqsFinal():
        if DEBUG:
            log.info('Liqudities Count ' + string.tostring(array.size(allLiqList)))
        __block_result_1__ = na
        if array.size(allLiqList) > 0:
            __block_result_2__ = na
            for i in pine_range(0, array.size(allLiqList) - 1, 1):
                curLiq = array.get(allLiqList, i)
                safeDeleteLiq(curLiq)
                __block_result_3__ = na
                if not curLiq.isRendered and (not (not showInvalidated and (not na(curLiq.info.endTime)))):
                    __block_result_3__ = renderLiq(curLiq)
                __block_result_2__ = __block_result_3__
            __block_result_1__ = __block_result_2__
        return __block_result_1__

    def areaOfZone(zone: liqGrabZone):
        XA1: int = zone.startTime
        XA2 = zone.startTime + EXTEND_ZONES_BY if na(zone.endTime) else zone.endTime
        YA1: float = zone.priceHigh
        YA2: float = zone.priceLow
        edge1 = math.sqrt((XA2 - XA1) * (XA2 - XA1) + (YA2 - YA2) * (YA2 - YA2))
        edge2 = math.sqrt((XA2 - XA2) * (XA2 - XA2) + (YA2 - YA1) * (YA2 - YA1))
        totalArea = edge1 * edge2
        return totalArea

    def doZonesTouch(zone1: liqGrabZone, zone2: liqGrabZone):
        XA1: int = zone1.startTime
        XA2 = bar_index if na(zone1.endTime) else zone1.endTime
        YA1: float = zone1.priceHigh
        YA2: float = zone1.priceLow
        XB1: int = zone2.startTime
        XB2 = bar_index if na(zone2.endTime) else zone2.endTime
        YB1: float = zone2.priceHigh
        YB2: float = zone2.priceLow
        intersectionArea = math.max(0, math.min(XA2, XB2) - math.max(XA1, XB1)) * math.max(0, math.min(YA1, YB1) - math.max(YA2, YB2))
        unionArea = areaOfZone(zone1) + areaOfZone(zone2) - intersectionArea
        overlapPercentage: float = intersectionArea / unionArea * 100.0
        if intersectionArea > 0.0:
            log.info(string.tostring(overlapPercentage))
        __block_result_4__ = na
        if overlapPercentage > 0:
            __block_result_4__ = True
        else:
            __block_result_4__ = False
        return __block_result_4__

    def combineFunc():
        __block_result_5__ = na
        if array.size(allLiqGrabZones) > 0:
            lastCombinations: int = 999
            __block_result_6__ = na
            while lastCombinations > 0:
                lastCombinations = 0
                __block_result_7__ = na
                __loop_2__ = pine_loop(0, 1)
                while __loop_2__.step(array.size(allLiqGrabZones) - 1):
                    i = __loop_2__.value
                    curZone1 = array.get(allLiqGrabZones, i)
                    __block_result_8__ = na
                    __loop_3__ = pine_loop(0, 1)
                    while __loop_3__.step(array.size(allLiqGrabZones) - 1):
                        j = __loop_3__.value
                        curZone2 = array.get(allLiqGrabZones, j)
                        if i == j:
                            continue
                        if curZone1.liqType != curZone2.liqType:
                            continue
                        if curZone1.disabled or curZone2.disabled:
                            continue
                        __block_result_9__ = na
                        if doZonesTouch(curZone1, curZone2):
                            curZone1.disabled = True
                            curZone2.disabled = True
                            newZone: liqGrabZone = liqGrabZone(na, na, math.max(curZone1.priceHigh, curZone2.priceHigh), math.min(curZone1.priceLow, curZone2.priceLow), curZone1.liqType)
                            newZone.startTime = math.min(curZone1.startTime, curZone2.startTime)
                            newZone.endTime = math.max(nz(curZone1.endTime), nz(curZone2.endTime))
                            newZone.endTime = na if newZone.endTime == 0 else newZone.endTime
                            array.unshift(allLiqGrabZones, newZone)
                            lastCombinations = lastCombinations + 1
                            __block_result_9__ = lastCombinations
                        __block_result_8__ = __block_result_9__
                    __block_result_7__ = __block_result_8__
                __block_result_6__ = __block_result_7__
            __block_result_5__ = __block_result_6__
        return __block_result_5__

    if bar_index > last_bar_index - MAX_DISTANCE:
        if array.size(allLiqList) > 0:
            for i in pine_range(0, array.size(allLiqList) - 1, 1):
                curLiq = array.get(allLiqList, i)
                if na(curLiq.info.endTime) and (close > curLiq.info.price if curLiq.info.liqType == 'Buyside' else close < curLiq.info.price):
                    curLiq.info.endTime = time
        if not na(highestTALiq):
            newLiqInfo: liqInfo = liqInfo(time[pivotLenLiq], na, highestTALiq, 'Buyside')
            addLiq: bool = True
            if array.size(allLiqList) > 0:
                for i in pine_range(0, array.size(allLiqList) - 1, 1):
                    curInfo: liqInfo = array.get(allLiqList, i).info
                    if na(curInfo.endTime) and curInfo.liqType == 'Buyside':
                        if math.abs(highestTALiq - curInfo.price) < curATR * minATRBetweenPivots:
                            addLiq = False
                            break
            if addLiq:
                array.unshift(allLiqList, liq(newLiqInfo))
                if array.size(allLiqList) > SHOW_LAST_X:
                    safeDeleteLiq(array.pop(allLiqList))
        if not na(lowestTALiq):
            newLiqInfo: liqInfo = liqInfo(time[pivotLenLiq], na, lowestTALiq, 'Sellside')
            addLiq: bool = True
            if array.size(allLiqList) > 0:
                for i in pine_range(0, array.size(allLiqList) - 1, 1):
                    curInfo: liqInfo = array.get(allLiqList, i).info
                    if na(curInfo.endTime) and curInfo.liqType == 'Sellside':
                        if math.abs(lowestTALiq - curInfo.price) < curATR * minATRBetweenPivots:
                            addLiq = False
                            break
            if addLiq:
                array.unshift(allLiqList, liq(newLiqInfo))
                if array.size(allLiqList) > SHOW_LAST_X:
                    safeDeleteLiq(array.pop(allLiqList))
    lastHigh: Persistent[int] = 0
    lastLow: Persistent[int] = 0
    renderHighCircle5: bool = False
    renderHighCircle10: bool = False
    renderHighCircle15: bool = False
    highCirclePrice: float = na(float)
    renderLowCircle5: bool = False
    renderLowCircle10: bool = False
    renderLowCircle15: bool = False
    lowCirclePrice: float = na(float)
    if array.size(allLiqList) > 0:
        for i in pine_range(0, array.size(allLiqList) - 1, 1):
            curLiq = array.get(allLiqList, i)
            if not na(curLiq.info.endTime):
                continue
            if curLiq.info.grabsFound == grabsPerZone:
                continue
            bodySize = math.abs(close - open)
            wickSize = high - math.max(close, open) if curLiq.info.liqType == 'Buyside' else math.min(close, open) - low
            curWBR = wickSize / bodySize
            if curLiq.info.liqType == 'Buyside':
                if high >= curLiq.info.price and bar_index - lastHigh > minDist:
                    lastHigh = bar_index
                    if curWBR >= WBR * 3:
                        renderHighCircle15 = True
                    elif curWBR >= WBR * 2:
                        renderHighCircle10 = True
                    elif curWBR >= WBR:
                        renderHighCircle5 = True
                    highCirclePrice = high + curATR * bubbleOffset / 100.0
                    curLiq.info.grabsFound = curLiq.info.grabsFound + 1
            else:
                if low <= curLiq.info.price and bar_index - lastLow > minDist:
                    lastLow = bar_index
                    if curWBR >= WBR * 3:
                        renderLowCircle15 = True
                    elif curWBR >= WBR * 2:
                        renderLowCircle10 = True
                    elif curWBR >= WBR:
                        renderLowCircle5 = True
                    lowCirclePrice = low - curATR * bubbleOffset / 100.0
                    curLiq.info.grabsFound = curLiq.info.grabsFound + 1
    plot(highCirclePrice if renderHighCircle5 and renderBubbles and barstate.isconfirmed else na, '', buysideColor, math.max(1, bubbleSize), plot.style_circles, False, 0)
    plot(highCirclePrice if renderHighCircle10 and renderBubbles and barstate.isconfirmed else na, '', buysideColor, math.max(1, cast_int(bubbleSize * 1.5)), plot.style_circles, False, 0)
    plot(highCirclePrice if renderHighCircle15 and renderBubbles and barstate.isconfirmed else na, '', buysideColor, math.max(1, bubbleSize * 2), plot.style_circles, False, 0)
    plot(lowCirclePrice if renderLowCircle5 and renderBubbles and barstate.isconfirmed else na, '', sellsideColor, math.max(1, bubbleSize), plot.style_circles, False, 0)
    plot(lowCirclePrice if renderLowCircle10 and renderBubbles and barstate.isconfirmed else na, '', sellsideColor, math.max(1, cast_int(bubbleSize * 1.5)), plot.style_circles, False, 0)
    plot(lowCirclePrice if renderLowCircle15 and renderBubbles and barstate.isconfirmed else na, '', sellsideColor, math.max(1, bubbleSize * 2), plot.style_circles, False, 0)
    if (renderHighCircle5 or renderHighCircle10 or renderHighCircle15) and barstate.isconfirmed:
        array.unshift(allLiqGrabZones, liqGrabZone(bar_index, na, high, math.max(close, open), 'Buyside'))
        if array.size(allLiqGrabZones) > MAX_ZONES:
            array.pop(allLiqGrabZones)
    elif (renderLowCircle5 or renderLowCircle10 or renderLowCircle15) and barstate.isconfirmed:
        array.unshift(allLiqGrabZones, liqGrabZone(bar_index, na, math.min(close, open), low, 'Sellside'))
        if array.size(allLiqGrabZones) > MAX_ZONES:
            array.pop(allLiqGrabZones)
    renderBreakLabelBuyside: float = na(float)
    renderBreakLabelSellside: float = na(float)
    if array.size(allLiqGrabZones) > 0 and renderLiqGrabZones and barstate.isconfirmed:
        __loop_1__ = pine_loop(0, 1)
        while __loop_1__.step(array.size(allLiqGrabZones) - 1):
            i = __loop_1__.value
            curZone = array.get(allLiqGrabZones, i)
            if curZone.disabled:
                continue
            if na(curZone.endTime) and bar_index > curZone.startTime:
                if curZone.liqType == 'Buyside':
                    if (close if zoneInvalidation == 'Close' else high) > curZone.priceHigh:
                        curZone.endTime = bar_index
                        if curZone.endTime - curZone.startTime > MIN_ZONE_SIZE:
                            renderBreakLabelBuyside = curZone.priceLow
                            if inverseZones and (not curZone.ephemeral):
                                array.unshift(allLiqGrabZones, liqGrabZone(bar_index, na, curZone.priceHigh, curZone.priceLow, 'Sellside', False, True))
                else:
                    if (close if zoneInvalidation == 'Close' else low) < curZone.priceLow:
                        curZone.endTime = bar_index
                        if curZone.endTime - curZone.startTime > MIN_ZONE_SIZE:
                            renderBreakLabelSellside = curZone.priceHigh
                            if inverseZones and (not curZone.ephemeral):
                                array.unshift(allLiqGrabZones, liqGrabZone(bar_index, na, curZone.priceHigh, curZone.priceLow, 'Buyside', False, True))
    lastRetestIndex: Persistent[int] = 0
    renderRetestLabelBuyside: float = na(float)
    renderRetestLabelSellside: float = na(float)
    if array.size(allLiqGrabZones) > 0 and renderLiqGrabZones and (bar_index - lastRetestIndex > RETEST_COOLDOWN) and barstate.isconfirmed:
        for i in pine_range(0, array.size(allLiqGrabZones) - 1, 1):
            curZone = array.get(allLiqGrabZones, i)
            if bar_index - curZone.startTime < MIN_ZONE_SIZE:
                continue
            if curZone.disabled:
                continue
            if not na(curZone.endTime):
                continue
            middleLine = (curZone.priceLow + curZone.priceHigh) / 2.0
            if curZone.liqType == 'Buyside':
                if high > middleLine:
                    renderRetestLabelBuyside = curZone.priceHigh
                    lastRetestIndex = bar_index
            else:
                if low < middleLine:
                    renderRetestLabelSellside = curZone.priceLow
                    lastRetestIndex = bar_index
    plotshape(renderRetestLabelBuyside if not na(renderRetestLabelBuyside) and retestsEnabled else na, '', shape.labeldown, color=buysideColor, text='R', location=location.absolute if labelsAtSameLevel else location.abovebar, textcolor=color.white, size=size.small)
    plotshape(renderRetestLabelSellside if not na(renderRetestLabelSellside) and retestsEnabled else na, '', shape.labelup, color=sellsideColor, text='R', location=location.absolute if labelsAtSameLevel else location.belowbar, textcolor=color.white, size=size.small)
    plotshape(renderBreakLabelBuyside if not na(renderBreakLabelBuyside) and breaksEnabled else na, '', shape.labelup, color=color.blue, text='B', location=location.absolute if labelsAtSameLevel else location.belowbar, textcolor=color.white, size=size.small)
    plotshape(renderBreakLabelSellside if not na(renderBreakLabelSellside) and breaksEnabled else na, '', shape.labeldown, color=color.blue, text='B', location=location.absolute if labelsAtSameLevel else location.abovebar, textcolor=color.white, size=size.small)
    alertcondition((renderHighCircle5 or renderHighCircle10 or renderHighCircle15) and barstate.isconfirmed, 'Buyside Liquidity Grab @ {{ticker}}', 'Buyside Liquidity Grab @ {{ticker}}')
    alertcondition((renderLowCircle5 or renderLowCircle10 or renderLowCircle15) and barstate.isconfirmed, 'Sellside Liquidity Grab @ {{ticker}}', 'Sellside Liquidity Grab @ {{ticker}}')
    alertcondition(not na(renderRetestLabelBuyside) and barstate.isconfirmed, 'Buyside Liq Grab Zone Retest @ {{ticker}}', 'Buyside Liq Grab Zone Retest @ {{ticker}}')
    alertcondition(not na(renderRetestLabelSellside) and barstate.isconfirmed, 'Sellside Liq Grab Zone Retest @ {{ticker}}', 'Sellside Liq Grab Zone Retest @ {{ticker}}')
    alertcondition(not na(renderBreakLabelBuyside) and barstate.isconfirmed, 'Buyside Liq Grab Zone Break @ {{ticker}}', 'Buyside Liq Grab Zone Break @ {{ticker}}')
    alertcondition(not na(renderBreakLabelSellside) and barstate.isconfirmed, 'Sellside Liq Grab Zone Break @ {{ticker}}', 'Sellside Liq Grab Zone Break @ {{ticker}}')
    if combineZones:
        combineFunc()
    if barstate.islast:
        handleLiqsFinal()
        for i in box.all:
            box.delete(i)
        for i in line.all:
            line.delete(i)
        if array.size(allLiqGrabZones) > 0 and renderLiqGrabZones:
            for i in pine_range(0, array.size(allLiqGrabZones) - 1, 1):
                curZone = array.get(allLiqGrabZones, i)
                if not showInvalidated and (not na(curZone.endTime)):
                    continue
                if curZone.disabled:
                    continue
                if not na(curZone.endTime):
                    if curZone.endTime - curZone.startTime <= MIN_ZONE_SIZE:
                        continue
                if na(curZone.endTime) or (not na(curZone.endTime) and showInvalidated):
                    box.new(curZone.startTime, curZone.priceHigh, nz(curZone.endTime, bar_index + 1), curZone.priceLow, xloc=xloc.bar_index, extend=extend.right if na(curZone.endTime) else extend.none, border_width=0, bgcolor=buysideColor if curZone.liqType == 'Buyside' else sellsideColor)
                    middlePrice = (curZone.priceHigh + curZone.priceLow) / 2
                    line.new(curZone.startTime, middlePrice, nz(curZone.endTime, bar_index + 1), middlePrice, color=LINE_COLOR, style=line.style_dotted if LINE_STYLE == '....' else line.style_solid if LINE_STYLE == '____' else line.style_dashed, extend=extend.right if na(curZone.endTime) else extend.none)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
