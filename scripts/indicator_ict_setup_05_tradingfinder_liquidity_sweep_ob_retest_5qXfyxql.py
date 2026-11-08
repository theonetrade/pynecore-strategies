"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_float, cast_int
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barstate, box, close, color,
    high, input, label, line, location, low, math, na, nz, open, plotshape, script, shape, size,
    syminfo, ta, time, timeframe, xloc
)
from pynecore.types import Box, Color, Label, Line, NA, Persistent, Series
import lib.TFlab.OrderBlockRefiner_TradingFinder.v2 as Refiner


@udt
class OrderBlock:
    direction: int = na(int)

    originBar: int = na(int)

    createdBar: int = na(int)

    top: float = na(float)

    bottom: float = na(float)

    active: bool = na(bool)

    touched: bool = na(bool)

    touchBar: int = na(int)

    fills: list[Box] = na(list)

    topLine: Line = na(Line)

    bottomLine: Line = na(Line)


@udt
class Imbalance:
    direction: int = na(int)

    originBar: int = na(int)

    createdBar: int = na(int)

    top: float = na(float)

    bottom: float = na(float)

    active: bool = na(bool)

    fills: list[Box] = na(list)

    topLine: Line = na(Line)

    bottomLine: Line = na(Line)

    textLabel: Label = na(Label)


@script.indicator("ICT Setup 05 [TradingFinder] Liquidity Sweep & OB Retest", "LS & Order Block", overlay=True, max_bars_back=5000, max_boxes_count=500, max_lines_count=500, max_labels_count=500)
def main(
    signalMode=input.string("Balanced", "Signal Mode", options=("More Signals", "Balanced", "High Quality"), tooltip="Signal Mode changes the confirmation strictness. BUY/SELL requires a valid Venom OB retest and a directional close back outside the block. Imbalance remains visual context only."),
    ShowPattern=input.bool(True, "Show Pattern"),
    ShowSignals=input.bool(True, "Show Signals"),
    DemandColor=input.color(color.new('#00B4EB'), "Demand OB", inline="OB"),
    SupplyColor=input.color(color.new('#E7EB00'), "Supply OB", inline="OB"),
    BullImbalanceColor=input.color(color.new('#00C66A'), "Bull Imbalance", inline="FVG"),
    BearImbalanceColor=input.color(color.new('#D72A50'), "Bear Imbalance", inline="FVG"),
    ShowOpeningRange=input.bool(False, "Show Opening Range"),
    Alert=input.bool(True, "Alert")
):
    cisdBarBackCheck = 160 if signalMode == 'More Signals' else 120 if signalMode == 'Balanced' else 80

    cisdLifeBars = 180 if signalMode == 'More Signals' else 120 if signalMode == 'Balanced' else 75

    fvgWaitBars = 36 if signalMode == 'More Signals' else 24 if signalMode == 'Balanced' else 14

    displacementATR = 0.3 if signalMode == 'More Signals' else 0.45 if signalMode == 'Balanced' else 0.65

    reactionBars = 6 if signalMode == 'More Signals' else 4 if signalMode == 'Balanced' else 3

    reactionClosePosition = 0.52 if signalMode == 'More Signals' else 0.57 if signalMode == 'Balanced' else 0.62

    cancelOnOppositeSweep = signalMode == 'High Quality'

    atr = ta.atr(55)

    barRange = math.max(high - low, syminfo.mintick)

    closeLocation = (close - low) / barRange

    body: Series = close - open

    absBody = math.abs(body)

    OpeningRangeSession: str = "0800-0930"

    TradingSession: str = "0930-1700"

    nyOR: Series = math.sign(nz(time(timeframe.period, OpeningRangeSession, 'America/New_York')))

    nyTrade: Series = math.sign(nz(time(timeframe.period, TradingSession, 'America/New_York')))

    newOpeningRange = nyOR == 1 and nz(nyOR[1]) == 0

    newTradingSession = nyTrade == 1 and nz(nyTrade[1]) == 0

    endTradingSession = nyTrade == 0 and nz(nyTrade[1]) == 1

    contextLines: Persistent[list[Line]] = array.new_line()

    contextLabels: Persistent[list[Label]] = array.new_label()

    def keepLine(id: Line, limit: int):
        array.push(contextLines, id)

        __block_result__ = na
        while array.size(contextLines) > limit:
            __block_result__ = line.delete(array.shift(contextLines))
        return __block_result__

    def keepLabel(id: Label, limit: int):
        array.push(contextLabels, id)

        __block_result_1__ = na
        while array.size(contextLabels) > limit:
            __block_result_1__ = label.delete(array.shift(contextLabels))
        return __block_result_1__

    def drawLevelTag(x1: int, x2: int, price: float, tagText: str, bullish: bool):
        lineColor: Color = color.new(color.new('#5BE660'), 20) if bullish else color.new(color.new('#E65B5B'), 20)

        tagColor: Color = color.new('#A5F2A7') if bullish else color.new('#DD8E8E')

        txtColor: Color = color.new('#151515') if bullish else color.new('#FFFFFF')

        ln: Line = line.new(x1, price, x2, price, xloc=xloc.bar_index, color=lineColor, style=line.style_dotted, width=1)

        midX: int = cast_int(math.round((x1 + x2) / 2.0))

        lb: Label = label.new(midX, price, tagText, xloc=xloc.bar_index, color=tagColor, textcolor=txtColor, style=label.style_label_center, size=size.small)

        keepLine(ln, 80)

        return keepLabel(lb, 80)


    orderBlocks: Persistent[list[OrderBlock]] = array.new(0, NA(OrderBlock))

    def deleteOrderBlock(ob: OrderBlock):
        if array.size(ob.fills) > 0:
            __loop_1__ = pine_loop(0)
            while __loop_1__.step(array.size(ob.fills) - 1):
                i = __loop_1__.value
                box.delete(array.get(ob.fills, i))

        if not na(ob.topLine):
            line.delete(ob.topLine)

        __block_result_2__ = na
        if not na(ob.bottomLine):
            __block_result_2__ = line.delete(ob.bottomLine)
        return __block_result_2__

    def trimOrderBlocks():
        __block_result_3__ = na
        while array.size(orderBlocks) > 12:
            oldest: OrderBlock = array.shift(orderBlocks)

            __block_result_3__ = deleteOrderBlock(oldest)
        return __block_result_3__

    def createOrderBlock(direction: int, originBar: int, zoneTop: float, zoneBottom: float):
        zoneColor: Color = DemandColor if direction == 1 else SupplyColor

        topLine: Line = line.new(originBar, zoneTop, bar_index, zoneTop, xloc=xloc.bar_index, color=zoneColor, style=line.style_dashed, width=1)

        bottomLine: Line = line.new(originBar, zoneBottom, bar_index, zoneBottom, xloc=xloc.bar_index, color=zoneColor, style=line.style_dashed, width=1)

        fills: list[Box] = array.new_box()

        zoneHeight: float = zoneTop - zoneBottom

        for i in pine_range(0, 20 - 1):
            layerBottom: float = zoneBottom + zoneHeight * (i / cast_float(20))

            layerTop: float = zoneBottom + zoneHeight * ((i + 1) / cast_float(20))

            rank: float = i + 1 if direction == 1 else 20 - i

            transp: int = cast_int(math.min(95.0, math.round(50.0 + rank * 2.25)))

            bx: Box = box.new(left=originBar, top=layerTop, right=bar_index, bottom=layerBottom, xloc=xloc.bar_index, bgcolor=color.new(zoneColor, transp), border_color=na)

            array.push(fills, bx)

        return OrderBlock(direction, originBar, bar_index, zoneTop, zoneBottom, True, False, na, fills, topLine, bottomLine)

    def setOrderBlockRight(ob: OrderBlock, rightBar: int):
        maxRightBar: int = ob.originBar + 1000

        __block_result_4__ = na
        if rightBar <= maxRightBar:
            if array.size(ob.fills) > 0:
                __loop_2__ = pine_loop(0)
                while __loop_2__.step(array.size(ob.fills) - 1):
                    i = __loop_2__.value
                    box.set_right(array.get(ob.fills, i), rightBar)

            line.set_x2(ob.topLine, rightBar)

            __block_result_4__ = line.set_x2(ob.bottomLine, rightBar)
        return __block_result_4__

    def finishOrderBlock(ob: OrderBlock):
        ob.active = False

        finalRight: int = ob.touchBar if ob.touched and (not na(ob.touchBar)) else bar_index

        return setOrderBlockRight(ob, finalRight)


    imbalances: Persistent[list[Imbalance]] = array.new(0, NA(Imbalance))

    def deleteImbalance(im: Imbalance):
        if array.size(im.fills) > 0:
            __loop_1__ = pine_loop(0)
            while __loop_1__.step(array.size(im.fills) - 1):
                i = __loop_1__.value
                box.delete(array.get(im.fills, i))

        if not na(im.topLine):
            line.delete(im.topLine)

        if not na(im.bottomLine):
            line.delete(im.bottomLine)

        __block_result_5__ = na
        if not na(im.textLabel):
            __block_result_5__ = label.delete(im.textLabel)
        return __block_result_5__

    def trimImbalances():
        __block_result_6__ = na
        while array.size(imbalances) > 12:
            oldest: Imbalance = array.shift(imbalances)

            __block_result_6__ = deleteImbalance(oldest)
        return __block_result_6__

    def createImbalance(direction: int, originBar: int, zoneTop: float, zoneBottom: float):
        zoneColor: Color = BullImbalanceColor if direction == 1 else BearImbalanceColor

        topLine: Line = line.new(originBar, zoneTop, bar_index, zoneTop, xloc=xloc.bar_index, color=color.new(zoneColor, 5), style=line.style_dashed, width=2)

        bottomLine: Line = line.new(originBar, zoneBottom, bar_index, zoneBottom, xloc=xloc.bar_index, color=color.new(zoneColor, 5), style=line.style_dashed, width=2)

        fills: list[Box] = array.new_box()

        zoneHeight: float = zoneTop - zoneBottom

        for i in pine_range(0, 20 - 1):
            layerBottom: float = zoneBottom + zoneHeight * (i / cast_float(20))

            layerTop: float = zoneBottom + zoneHeight * ((i + 1) / cast_float(20))

            rank: float = i + 1 if direction == 1 else 20 - i

            transp: int = cast_int(math.min(92.0, math.round(48.0 + rank * 1.6)))

            bx: Box = box.new(left=originBar, top=layerTop, right=bar_index, bottom=layerBottom, xloc=xloc.bar_index, bgcolor=color.new(zoneColor, transp), border_color=na)

            array.push(fills, bx)

        txt: Label = label.new(bar_index, math.avg(zoneTop, zoneBottom), 'Imbalance', xloc=xloc.bar_index, color=color.new(color.black, 55), textcolor=color.white, style=label.style_label_center, size=size.small)

        return Imbalance(direction, originBar, bar_index, zoneTop, zoneBottom, True, fills, topLine, bottomLine, txt)

    def setImbalanceRight(im: Imbalance, rightBar: int):
        if array.size(im.fills) > 0:
            __loop_1__ = pine_loop(0)
            while __loop_1__.step(array.size(im.fills) - 1):
                i = __loop_1__.value
                box.set_right(array.get(im.fills, i), rightBar)

        line.set_x2(im.topLine, rightBar)

        line.set_x2(im.bottomLine, rightBar)

        return label.set_x(im.textLabel, cast_int(math.round((im.originBar + rightBar) / 2.0)))

    def finishImbalance(im: Imbalance, rightBar: int):
        im.active = False

        return setImbalanceRight(im, rightBar)

    openingHigh: Persistent[float] = na(float)

    openingLow: Persistent[float] = na(float)

    openingStartBar: Persistent[int] = na(int)

    openingHighBar: Persistent[int] = na(int)

    openingLowBar: Persistent[int] = na(int)

    if newOpeningRange:
        openingHigh = high

        openingLow = low

        openingStartBar = bar_index

        openingHighBar = bar_index

        openingLowBar = bar_index
    elif nyOR == 1:
        if na(openingHigh) or high >= openingHigh:
            openingHigh = high

            openingHighBar = bar_index

        if na(openingLow) or low <= openingLow:
            openingLow = low

            openingLowBar = bar_index

    if ShowOpeningRange and newTradingSession and (not na(openingHigh)) and (not na(openingLow)):
        hi: Line = line.new(bar_index, openingHigh, bar_index + 45, openingHigh, xloc=xloc.bar_index, color=color.new(color.new('#7D8A9D'), 45), style=line.style_dotted)

        lo: Line = line.new(bar_index, openingLow, bar_index + 45, openingLow, xloc=xloc.bar_index, color=color.new(color.new('#7D8A9D'), 45), style=line.style_dotted)

        keepLine(hi, 30)

        keepLine(lo, 30)

    highSwept: Persistent[bool] = False

    lowSwept: Persistent[bool] = False

    tradingStartBar: Persistent[int] = na(int)

    highOB: Persistent[float] = na(float)

    lowOB: Persistent[float] = na(float)

    bearOBIndex: Persistent[int] = na(int)

    bullOBIndex: Persistent[int] = na(int)

    bearCisdArmed: Persistent[bool] = False

    bullCisdArmed: Persistent[bool] = False

    bearCisdLevel: Persistent[float] = na(float)

    bullCisdLevel: Persistent[float] = na(float)

    bearCisdIndex: Persistent[int] = na(int)

    bullCisdIndex: Persistent[int] = na(int)

    bearSweepBar: Persistent[int] = na(int)

    bullSweepBar: Persistent[int] = na(int)

    waitingBearFVG: Persistent[bool] = False

    waitingBullFVG: Persistent[bool] = False

    bearChochBar: Persistent[int] = na(int)

    bullChochBar: Persistent[int] = na(int)

    bearFVGReady: Persistent[bool] = False

    bullFVGReady: Persistent[bool] = False

    activeBearFVGArrayIndex: Persistent[int] = na(int)

    activeBullFVGArrayIndex: Persistent[int] = na(int)

    bearFVGBar: Persistent[int] = na(int)

    bullFVGBar: Persistent[int] = na(int)

    if newTradingSession:
        tradingStartBar = bar_index

        highSwept = False

        lowSwept = False

        highOB = high

        lowOB = low

        bearOBIndex = bar_index

        bullOBIndex = bar_index

        bearCisdArmed = False

        bullCisdArmed = False

        waitingBearFVG = False

        waitingBullFVG = False

        bearFVGReady = False

        bullFVGReady = False

        activeBearFVGArrayIndex = na

        activeBullFVGArrayIndex = na

        bearFVGBar = na

        bullFVGBar = na

    prevHighSwept: bool = highSwept

    prevLowSwept: bool = lowSwept

    if nyTrade == 1:
        if na(highOB) or high > highOB:
            highOB = high

            bearOBIndex = bar_index

        if na(lowOB) or low < lowOB:
            lowOB = low

            bullOBIndex = bar_index

        if not na(openingHigh) and high > openingHigh:
            highSwept = True

        if not na(openingLow) and low < openingLow:
            lowSwept = True

    newHighSweep: bool = barstate.isconfirmed and nyTrade == 1 and highSwept and (not prevHighSwept) and (not lowSwept)

    newLowSweep: bool = barstate.isconfirmed and nyTrade == 1 and lowSwept and (not prevLowSwept) and (not highSwept)

    if ShowPattern and newHighSweep and (not na(openingHigh)):
        x1: int = openingHighBar if not na(openingHighBar) else math.max(bar_index - 15, 0)

        drawLevelTag(x1, bar_index, openingHigh, 'BSL', False)

    if ShowPattern and newLowSweep and (not na(openingLow)):
        x1: int = openingLowBar if not na(openingLowBar) else math.max(bar_index - 15, 0)

        drawLevelTag(x1, bar_index, openingLow, 'SSL', True)

    if newHighSweep:
        bearSweepBar = bar_index

        bearCisdArmed = False

        bearCisdLevel = na

        bearCisdIndex = na

        foundBearBody: bool = False

        for i in pine_range(1, cisdBarBackCheck):
            if not foundBearBody and (not na(body[i])) and (body[i] < 0):
                bearCisdLevel = math.min(open[i - 1], open[i - 2]) if i > 1 else open[i - 1]

                bearCisdIndex = (bar_index[i - 2] if math.min(open[i - 1], open[i - 2]) == open[i - 2] else bar_index[i - 1]) if i > 1 else bar_index[i - 1]

                bearCisdArmed = True

                foundBearBody = True

    if newLowSweep:
        bullSweepBar = bar_index

        bullCisdArmed = False

        bullCisdLevel = na

        bullCisdIndex = na

        foundBullBody: bool = False

        for i in pine_range(1, cisdBarBackCheck):
            if not foundBullBody and (not na(body[i])) and (body[i] > 0):
                bullCisdLevel = math.max(open[i - 1], open[i - 2]) if i > 1 else open[i - 1]

                bullCisdIndex = (bar_index[i - 2] if math.max(open[i - 1], open[i - 2]) == open[i - 2] else bar_index[i - 1]) if i > 1 else bar_index[i - 1]

                bullCisdArmed = True

                foundBullBody = True

    if cancelOnOppositeSweep and nyTrade == 1:
        if bearCisdArmed and lowSwept:
            bearCisdArmed = False

        if bullCisdArmed and highSwept:
            bullCisdArmed = False

    bullChochTrigger: bool = False

    bearChochTrigger: bool = False

    if barstate.isconfirmed and nyTrade == 1:
        if bearCisdArmed and (not na(bearCisdLevel)) and (not na(bearSweepBar)):
            if bar_index - bearSweepBar <= cisdLifeBars:
                if close <= bearCisdLevel:
                    bearCisdArmed = False

                    bearChochTrigger = True

                    bearChochBar = bar_index

                    waitingBearFVG = True

                    if ShowPattern and (not na(bearCisdIndex)):
                        drawLevelTag(bearCisdIndex, bar_index, bearCisdLevel, 'ChoCh', False)
            else:
                bearCisdArmed = False

        if bullCisdArmed and (not na(bullCisdLevel)) and (not na(bullSweepBar)):
            if bar_index - bullSweepBar <= cisdLifeBars:
                if close >= bullCisdLevel:
                    bullCisdArmed = False

                    bullChochTrigger = True

                    bullChochBar = bar_index

                    waitingBullFVG = True

                    if ShowPattern and (not na(bullCisdIndex)):
                        drawLevelTag(bullCisdIndex, bar_index, bullCisdLevel, 'ChoCh', True)
            else:
                bullCisdArmed = False

    Bu_Xd1, Bu_Xd2, Bu_Yd12, Bu_Xp1, Bu_Xp2, Bu_Yp12 = Refiner.OBRefiner('Demand', 'On', 'Aggressive', bullChochTrigger, bullOBIndex)

    Be_Xd1, Be_Xd2, Be_Yd12, Be_Xp1, Be_Xp2, Be_Yp12 = Refiner.OBRefiner('Supply', 'On', 'Aggressive', bearChochTrigger, bearOBIndex)

    bullishOBCreated: bool = False

    bearishOBCreated: bool = False

    if bullChochTrigger:
        zoneTop: float = math.max(Bu_Yd12, Bu_Yp12)

        zoneBottom: float = math.min(Bu_Yd12, Bu_Yp12)

        zoneBar: int = Bu_Xd1

        if not na(zoneBar) and (not na(zoneTop)) and (not na(zoneBottom)) and (zoneTop > zoneBottom):
            ob: OrderBlock = createOrderBlock(1, zoneBar, zoneTop, zoneBottom)

            array.push(orderBlocks, ob)

            trimOrderBlocks()

            bullishOBCreated = True

    if bearChochTrigger:
        zoneTop: float = math.max(Be_Yd12, Be_Yp12)

        zoneBottom: float = math.min(Be_Yd12, Be_Yp12)

        zoneBar: int = Be_Xd1

        if not na(zoneBar) and (not na(zoneTop)) and (not na(zoneBottom)) and (zoneTop > zoneBottom):
            ob: OrderBlock = createOrderBlock(-1, zoneBar, zoneTop, zoneBottom)

            array.push(orderBlocks, ob)

            trimOrderBlocks()

            bearishOBCreated = True

    bullFVG: bool = barstate.isconfirmed and low > high[2] and (close > open) and (absBody >= atr * displacementATR)

    bearFVG: bool = barstate.isconfirmed and high < low[2] and (close < open) and (absBody >= atr * displacementATR)

    if waitingBullFVG and (not na(bullChochBar)):
        if bar_index - bullChochBar > fvgWaitBars:
            waitingBullFVG = False
        elif bullFVG and bar_index >= bullChochBar:
            fvgTop: float = low

            fvgBottom: float = high[2]

            im: Imbalance = createImbalance(1, bar_index - 2, fvgTop, fvgBottom)

            array.push(imbalances, im)

            trimImbalances()

            activeBullFVGArrayIndex = array.size(imbalances) - 1

            bullFVGBar = bar_index

            bullFVGReady = True

            waitingBullFVG = False

    if waitingBearFVG and (not na(bearChochBar)):
        if bar_index - bearChochBar > fvgWaitBars:
            waitingBearFVG = False
        elif bearFVG and bar_index >= bearChochBar:
            fvgTop: float = low[2]

            fvgBottom: float = high

            im: Imbalance = createImbalance(-1, bar_index - 2, fvgTop, fvgBottom)

            array.push(imbalances, im)

            trimImbalances()

            activeBearFVGArrayIndex = array.size(imbalances) - 1

            bearFVGBar = bar_index

            bearFVGReady = True

            waitingBearFVG = False

    if barstate.isconfirmed and array.size(orderBlocks) > 0:
        for i in pine_range(0, array.size(orderBlocks) - 1):
            ob: OrderBlock = array.get(orderBlocks, i)

            if ob.active:
                expired: bool = bar_index > ob.originBar + 1000

                if expired:
                    finishOrderBlock(ob)
                else:
                    if not ob.touched:
                        setOrderBlockRight(ob, bar_index)

                    invalidated: bool = close < ob.bottom if ob.direction == 1 else close > ob.top

                    if invalidated:
                        finishOrderBlock(ob)
                    else:
                        touched: bool = bar_index > ob.createdBar and low <= ob.top and (high >= ob.bottom)

                        if touched and (not ob.touched):
                            ob.touched = True

                            ob.touchBar = bar_index

                            setOrderBlockRight(ob, bar_index)

    bullishSignal: bool = False

    bearishSignal: bool = False

    if barstate.isconfirmed and array.size(orderBlocks) > 0:
        for i in pine_range(0, array.size(orderBlocks) - 1):
            ob: OrderBlock = array.get(orderBlocks, i)

            if ob.active and bar_index <= ob.originBar + 1000 and ob.touched and (not na(ob.touchBar)):
                bullConfirmation: bool = ob.direction == 1 and close > open and (close > ob.top) and (closeLocation >= reactionClosePosition)

                bearConfirmation: bool = ob.direction == -1 and close < open and (close < ob.bottom) and (closeLocation <= 1.0 - reactionClosePosition)

                if bullConfirmation:
                    bullishSignal = True

                    finishOrderBlock(ob)
                elif bearConfirmation:
                    bearishSignal = True

                    finishOrderBlock(ob)
                elif bar_index - ob.touchBar > reactionBars:
                    finishOrderBlock(ob)

    plotshape(ShowSignals and bullishSignal, 'Bullish Signal', shape.triangleup, location.belowbar, color=color.new('#56D36F'), size=size.small, text='BUY', textcolor=color.white)

    plotshape(ShowSignals and bearishSignal, 'Bearish Signal', shape.triangledown, location.abovebar, color=color.new('#FF5A70'), size=size.small, text='SELL', textcolor=color.white)

    if endTradingSession:
        tradingStartBar = na

        highSwept = False

        lowSwept = False

        highOB = na

        lowOB = na

        bearOBIndex = na

        bullOBIndex = na

        bearCisdArmed = False

        bullCisdArmed = False

        waitingBearFVG = False

        waitingBullFVG = False

        bearFVGReady = False

        bullFVGReady = False

        activeBearFVGArrayIndex = na

        activeBullFVGArrayIndex = na

    alertcondition(bullishOBCreated, 'ICT05 Demand OB', 'Demand Order Block')

    alertcondition(bearishOBCreated, 'ICT05 Supply OB', 'Supply Order Block')

    alertcondition(bullishSignal, 'ICT05 Buy Signal', 'Buy Signal')

    alertcondition(bearishSignal, 'ICT05 Sell Signal', 'Sell Signal')

    if Alert and bullishSignal:
        alert('ICT05 Buy Signal', alert.freq_once_per_bar_close)

    if Alert and bearishSignal:
        alert('ICT05 Sell Signal', alert.freq_once_per_bar_close)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)