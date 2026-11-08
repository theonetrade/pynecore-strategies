"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_int
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, close, color, display, high,
    input, last_bar_index, low, math, na, open, plot, script, ta
)
from pynecore.types import Persistent

DEBUG: bool = False
maxDistanceToLastBar: int = 5000
renderingEnabled: bool = True
liqGrabLiqZoneCount: int = 5
bubbleSize: int = 5
liqGrabCooldown: int = 3


@script.indicator(title='Liquidity Grabs | Flux Charts', overlay=True)
def main(
    buysideColorGrab=input(color.new('#F2364680'), "Buyside", inline="EV", group="Liquidity Grabs", display=display.none),
    sellsideColorGrab=input(color.new('#08998180'), "Sellside", inline="EV", group="Liquidity Grabs", display=display.none),
    pivotLenLiqGrab=input.int(25, "Pivot Length", group="Liquidity Grabs", display=display.none),
    WBR=input.float(0.5, "Wick-Body Ratio", step=0.1, group="Liquidity Grabs", display=display.none)
):
    invalidateBottomClose = math.min(close, open)
    invalidateTopClose = math.max(close, open)
    def getInvalidationPoint(isTop: bool, isClose: bool):
        __block_result__ = na
        if isTop and isClose:
            __block_result__ = invalidateTopClose
        elif isTop and (not isClose):
            __block_result__ = high
        elif not isTop and isClose:
            __block_result__ = invalidateBottomClose
        else:
            __block_result__ = low
        return __block_result__

    pivotHighLiqGrab: float = ta.pivothigh(pivotLenLiqGrab, pivotLenLiqGrab)
    pivotLowLiqGrab: float = ta.pivotlow(pivotLenLiqGrab, pivotLenLiqGrab)

    def detectLiquidityGrab():
        buysideLiqs: Persistent[list[float]] = array.new_float()
        sellsideLiqs: Persistent[list[float]] = array.new_float()
        liqsToRemove: Persistent[list[float]] = array.new_float()
        _grabFound: bool = False
        _grabBuyside: bool = True
        _grabSize: int = 1

        if not na(pivotHighLiqGrab):
            array.push(buysideLiqs, pivotHighLiqGrab)
            if array.size(buysideLiqs) > liqGrabLiqZoneCount:
                array.shift(buysideLiqs)
        if not na(pivotLowLiqGrab):
            array.push(sellsideLiqs, pivotLowLiqGrab)
            if array.size(sellsideLiqs) > liqGrabLiqZoneCount:
                array.shift(sellsideLiqs)

        for curLiq in buysideLiqs:
            if getInvalidationPoint(True, False) > curLiq and getInvalidationPoint(True, True) < curLiq:
                bodySize = math.abs(close - open)
                wickSize = high - math.max(close, open)
                curWBR = wickSize / bodySize
                _grabFound = True
                _grabBuyside = True
                _grabSize = math.floor(math.min(curWBR / WBR, 3))
                array.push(liqsToRemove, curLiq)
                break
            if getInvalidationPoint(True, True) > curLiq:
                array.push(liqsToRemove, curLiq)
                break
        if not _grabFound:
            for curLiq in sellsideLiqs:
                if getInvalidationPoint(False, False) < curLiq and getInvalidationPoint(False, True) > curLiq:
                    bodySize = math.abs(close - open)
                    wickSize = math.min(close, open) - low
                    curWBR = wickSize / bodySize
                    _grabFound = True
                    _grabBuyside = False
                    _grabSize = math.floor(math.min(curWBR / WBR, 3))
                    array.push(liqsToRemove, curLiq)
                    break
                if getInvalidationPoint(False, True) < curLiq:
                    array.push(liqsToRemove, curLiq)
                    break

        for liqToRemove in liqsToRemove:
            buysideIndex = array.indexof(buysideLiqs, liqToRemove)
            if buysideIndex != -1:
                array.remove(buysideLiqs, buysideIndex)
                continue
            sellsideIndex = array.indexof(sellsideLiqs, liqToRemove)
            if sellsideIndex != -1:
                array.remove(sellsideLiqs, sellsideIndex)
        array.clear(liqsToRemove)

        return (_grabFound, _grabBuyside, _grabSize)

    buysideLiqGrabSmall: bool = False
    buysideLiqGrabMedium: bool = False
    buysideLiqGrabLarge: bool = False
    sellsideLiqGrabSmall: bool = False
    sellsideLiqGrabMedium: bool = False
    sellsideLiqGrabLarge: bool = False
    lastBuysideGrab: Persistent[int] = 0
    lastSellsideGrab: Persistent[int] = 0
    liqGrabCooldownOK: bool = False
    if last_bar_index - bar_index < maxDistanceToLastBar and barstate.isconfirmed:
        _grabFound, _grabBuyside, _grabSize = detectLiquidityGrab()
        liqGrabCooldownOK = _grabBuyside and bar_index - lastBuysideGrab > liqGrabCooldown or (not _grabBuyside and bar_index - lastSellsideGrab > liqGrabCooldown)
        if _grabFound and _grabSize > 0:
            buysideLiqGrabSmall = _grabBuyside and _grabSize == 1
            buysideLiqGrabMedium = _grabBuyside and _grabSize == 2
            buysideLiqGrabLarge = _grabBuyside and _grabSize == 3
            sellsideLiqGrabSmall = not _grabBuyside and _grabSize == 1
            sellsideLiqGrabMedium = not _grabBuyside and _grabSize == 2
            sellsideLiqGrabLarge = not _grabBuyside and _grabSize == 3
            if liqGrabCooldownOK:
                lastBuysideGrab = bar_index if _grabBuyside else lastBuysideGrab
                lastSellsideGrab = lastSellsideGrab if _grabBuyside else bar_index

    plot(high if buysideLiqGrabSmall and renderingEnabled and liqGrabCooldownOK else na, 'Buyside Liq Grab Small', buysideColorGrab, bubbleSize, plot.style_circles, False, 0, display=display.pane)
    plot(high if buysideLiqGrabMedium and renderingEnabled and liqGrabCooldownOK else na, 'Buyside Liq Grab Medium', buysideColorGrab, cast_int(bubbleSize * 1.5), plot.style_circles, False, 0, display=display.pane)
    plot(high if buysideLiqGrabLarge and renderingEnabled and liqGrabCooldownOK else na, 'Buyside Liq Grab Large', buysideColorGrab, bubbleSize * 2, plot.style_circles, False, 0, display=display.pane)
    plot(low if sellsideLiqGrabSmall and renderingEnabled and liqGrabCooldownOK else na, 'Sellside Liq Grab Small', sellsideColorGrab, bubbleSize, plot.style_circles, False, 0, display=display.pane)
    plot(low if sellsideLiqGrabMedium and renderingEnabled and liqGrabCooldownOK else na, 'Sellside Liq Grab Medium', sellsideColorGrab, cast_int(bubbleSize * 1.5), plot.style_circles, False, 0, display=display.pane)
    plot(low if sellsideLiqGrabLarge and renderingEnabled and liqGrabCooldownOK else na, 'Sellside Liq Grab Large', sellsideColorGrab, bubbleSize * 2, plot.style_circles, False, 0, display=display.pane)

    alertcondition((buysideLiqGrabSmall or buysideLiqGrabMedium or buysideLiqGrabLarge) and barstate.isconfirmed, 'Buyside Liquidity Grab @ {{ticker}}', 'Buyside Liquidity Grab @ {{ticker}}')
    alertcondition((sellsideLiqGrabSmall or sellsideLiqGrabMedium or sellsideLiqGrabLarge) and barstate.isconfirmed, 'Sellside Liquidity Grab @ {{ticker}}', 'Sellside Liquidity Grab @ {{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
