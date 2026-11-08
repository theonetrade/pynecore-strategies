"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.series import inline_series
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, box, close, color, fill,
    high, input, label, line, location, low, math, na, nz, plot, plotshape, script, shape, size,
    string, syminfo, ta, xloc
)
from pynecore.types import Box, Color, Label, Line, Persistent, Series

g1: str = "Trend"
g2: str = "Position"
g3: str = "Display"


@script.indicator("Trend Target Ribbon [BOSWaves]", overlay=True, max_lines_count=100, max_boxes_count=100, max_labels_count=100)
def main(
    src: Series[float] = input.source(close, "Source", group=g1, tooltip="Price source used for the ALMA trend calculation."),
    almaLen=input.int(34, "ALMA Length", minval=5, group=g1, tooltip="Number of bars used to calculate the ALMA moving average. Higher values produce a smoother, slower trend line."),
    almaOffset=input.float(0.85, "ALMA Offset", minval=0.0, maxval=1.0, step=0.05, group=g1, tooltip="Controls the balance between responsiveness and smoothness. Higher values shift weighting toward recent price action."),
    almaSigma=input.float(6.0, "ALMA Sigma", minval=1.0, maxval=15.0, step=0.5, group=g1, tooltip="Controls the smoothness of the ALMA curve. Higher values produce a smoother line with less noise."),
    devLen=input.int(34, "Deviation Length", minval=5, group=g1, tooltip="Number of bars used to calculate the standard deviation bands around the ALMA for trend confirmation."),
    devMult=input.float(0.65, "Trend Confirmation", minval=0.1, maxval=3.0, step=0.05, group=g1, tooltip="Multiplier applied to the deviation bands. Higher values require price to move further from the ALMA before confirming a trend."),
    slopeLen=input.int(3, "Slope Length", minval=1, maxval=10, group=g1, tooltip="Number of bars back used to measure the ALMA's slope for trend confirmation."),
    slopeMin=input.float(0.08, "Minimum Slope", minval=0.0, maxval=1.0, step=0.01, group=g1, tooltip="Minimum slope strength, relative to ATR, required to confirm a trend direction."),
    atrLen=input.int(14, "ATR Length", minval=5, group=g1, tooltip="Number of bars used to calculate the Average True Range, used for slope normalization and stop distance."),
    stopLookback=input.int(12, "Stop Structure Lookback", minval=3, maxval=50, group=g2, tooltip="Number of bars back used to locate swing structure for stop loss placement."),
    minStopAtr=input.float(0.75, "Minimum Stop ATR", minval=0.25, maxval=3.0, step=0.05, group=g2, tooltip="Minimum stop distance allowed, expressed as a multiple of ATR."),
    maxStopAtr=input.float(3.0, "Maximum Stop ATR", minval=1.0, maxval=8.0, step=0.25, group=g2, tooltip="Maximum stop distance allowed, expressed as a multiple of ATR."),
    targetCount=input.int(4, "Profit Targets", minval=2, maxval=4, group=g2, tooltip="Number of profit targets plotted for each position, from 2 to 4."),
    zonePct=input.float(0.06, "Target Zone Size", minval=0.01, maxval=0.2, step=0.01, group=g2, tooltip="Size of the shaded zone drawn around each profit target, as a percentage of the risk distance."),
    approachR=input.float(0.65, "Target Approach Range", minval=0.1, maxval=1.5, step=0.05, group=g2, tooltip="Distance, in risk multiples, within which a target begins visually highlighting as price approaches it."),
    extendBars=input.int(30, "Projection Length", minval=10, maxval=100, group=g2, tooltip="Number of bars the entry, stop, and target lines are projected forward from the current bar."),
    keepPositions=input.int(4, "Positions On Chart", minval=1, maxval=5, group=g2, tooltip="Number of past positions kept visible on the chart before the oldest is removed."),
    showRibbon=input.bool(True, "Show Trend Gradient", group=g3, tooltip="Toggles visibility of the trend gradient ribbon."),
    showLabels=input.bool(True, "Show Position Labels", group=g3, tooltip="Toggles visibility of position, stop, and target labels."),
    paintBars=input.bool(True, "Color Candles", group=g3, tooltip="Toggles gradient coloring of candles based on trend conviction."),
    labelInput=input.string("Normal", "Label Size", options=("Tiny", "Small", "Normal", "Large", "Huge"), group=g3, tooltip="Controls the size of position and target labels."),
    buyCol=input.color(color.new('#00FF00'), "Bull", inline="c1", group=g3, tooltip="Color used for bullish trend elements."),
    sellCol=input.color(color.new('#FF0066'), "Bear", inline="c1", group=g3, tooltip="Color used for bearish trend elements."),
    tpCol=input.color(color.new('#00FF00'), "Take Profit", inline="c2", group=g3, tooltip="Color used for take-profit target elements."),
    slCol=input.color(color.new('#FF0066'), "Stop Loss", inline="c2", group=g3, tooltip="Color used for stop-loss elements."),
    whiteCol=input.color(color.new('#FFFFFF'), "Core", group=g3, tooltip="Color used for the core ALMA line and entry markers."),
    neutralCol=input.color(color.new('#555555'), "Neutral", group=g3, tooltip="Color used when no trend is active.")
):
    def f_label_size(value: str):
        return size.tiny if value == 'Tiny' else size.small if value == 'Small' else size.large if value == 'Large' else size.huge if value == 'Huge' else size.normal

    labelSize: str = f_label_size(labelInput)

    alma: Series[float] = ta.alma(src, almaLen, almaOffset, almaSigma)
    dev: float = ta.stdev(src, devLen)
    atr: float = ta.atr(atrLen)

    slopeScore: float = (alma - alma[slopeLen]) / atr if atr > 0 else 0.0

    upperConfirm: float = alma + dev * devMult
    lowerConfirm: float = alma - dev * devMult

    bullSetup: bool = slopeScore > slopeMin and close > upperConfirm
    bearSetup: bool = slopeScore < -slopeMin and close < lowerConfirm

    trend: Persistent[int] = 0

    bullFlip: bool = False
    bearFlip: bool = False

    if trend != 1 and bullSetup:
        trend = 1
        bullFlip = True
    elif trend != -1 and bearSetup:
        trend = -1
        bearFlip = True

    bull: bool = trend == 1
    bear: bool = trend == -1
    flip: bool = bullFlip or bearFlip

    trendCol: Color = buyCol if bull else sellCol if bear else neutralCol

    distanceScore: float = math.abs(close - alma) / atr if atr > 0 else 0.0

    conviction: float = math.max(0.0, math.min(1.0, math.abs(slopeScore) * 2.0 + distanceScore * 0.35))

    ribbonEdge: float = alma - dev * 0.55 if bull else alma + dev * 0.55 if bear else alma

    ribbonMid: float = (alma + ribbonEdge) * 0.5

    almaDraw: float = na if flip else alma
    midDraw: float = na if flip else ribbonMid
    edgeDraw: float = na if flip else ribbonEdge

    edgeT: int = cast_int(math.round(82.0 - conviction * 16.0))
    coreT: int = cast_int(math.round(50.0 - conviction * 35.0))

    pEdgeGlow = plot(edgeDraw if showRibbon else na, 'Trend Glow', color=color.new(trendCol, 86), linewidth=9, style=plot.style_linebr)

    pEdge = plot(edgeDraw if showRibbon else na, 'Trend Edge', color=color.new(trendCol, edgeT), linewidth=3, style=plot.style_linebr)

    pMid = plot(midDraw if showRibbon else na, 'Trend Mid', color=color.new(trendCol, 100), linewidth=1, style=plot.style_linebr)

    pAlma = plot(almaDraw if showRibbon else na, 'ALMA', color=color.new(whiteCol, coreT), linewidth=1, style=plot.style_linebr)

    fill(pEdge, pMid, color=color.new(trendCol, 84) if showRibbon else na)

    fill(pMid, pAlma, color=color.new(trendCol, 93) if showRibbon else na)

    weakCol: Color = color.new(trendCol, 72)

    barCol: Color = color.from_gradient(conviction, 0.0, 1.0, weakCol, trendCol)

    barcolor(barCol if paintBars and trend != 0 else na)

    entryPrice: Persistent[float] = na(float)
    stopPrice: Persistent[float] = na(float)
    riskDist: Persistent[float] = na(float)

    entryBar: Persistent[int] = na(int)
    positionDir: Persistent[int] = 0

    positionEnded: Persistent[bool] = True

    entryGlow: Persistent[Line] = na(Line)
    entryCore: Persistent[Line] = na(Line)
    stopGlow: Persistent[Line] = na(Line)
    stopCore: Persistent[Line] = na(Line)

    riskBox: Persistent[Box] = na(Box)

    entryTag: Persistent[Label] = na(Label)
    stopTag: Persistent[Label] = na(Label)

    targetGlow: Persistent[list[Line]] = array.new_line()
    targetCore: Persistent[list[Line]] = array.new_line()
    targetZone: Persistent[list[Box]] = array.new_box()
    targetBand: Persistent[list[Box]] = array.new_box()
    targetTags: Persistent[list[Label]] = array.new_label()

    targetHit: Persistent[list[bool]] = array.new_bool(4, False)

    allPositionLines: Persistent[list[Line]] = array.new_line()
    allPositionBoxes: Persistent[list[Box]] = array.new_box()
    allPositionLabels: Persistent[list[Label]] = array.new_label()

    positionCount: Persistent[int] = 0

    if flip and (not na(entryPrice)) and (not positionEnded):
        endBar: int = bar_index
        oldCol: Color = buyCol if positionDir == 1 else sellCol

        line.set_xy2(entryGlow, endBar, entryPrice)
        line.set_xy2(entryCore, endBar, entryPrice)
        line.set_xy2(stopGlow, endBar, stopPrice)
        line.set_xy2(stopCore, endBar, stopPrice)

        line.set_color(entryGlow, color.new(oldCol, 88))
        line.set_color(entryCore, color.new(whiteCol, 50))

        line.set_color(stopGlow, color.new(slCol, 88))
        line.set_color(stopCore, color.new(slCol, 48))

        box.set_right(riskBox, endBar)
        box.set_bgcolor(riskBox, color.new(slCol, 97))

        if showLabels:
            label.set_xy(entryTag, endBar + 1, entryPrice)
            label.set_color(entryTag, color.new(oldCol, 58))

            label.set_xy(stopTag, endBar + 1, stopPrice)
            label.set_color(stopTag, color.new(slCol, 65))

        for i in pine_range(0, array.size(targetGlow) - 1):
            targetPrice: float = entryPrice + positionDir * riskDist * (i + 1)

            glow: Line = array.get(targetGlow, i)
            core: Line = array.get(targetCore, i)
            zone: Box = array.get(targetZone, i)
            band: Box = array.get(targetBand, i)
            tag: Label = array.get(targetTags, i)

            hit: bool = array.get(targetHit, i)

            line.set_xy2(glow, endBar, targetPrice)
            line.set_xy2(core, endBar, targetPrice)

            line.set_color(glow, color.new(tpCol, 80 if hit else 94))

            line.set_color(core, color.new(whiteCol, 38) if hit else color.new(tpCol, 72))

            box.set_right(zone, endBar)
            box.set_right(band, endBar)

            box.set_bgcolor(zone, color.new(tpCol, 93 if hit else 98))

            box.set_bgcolor(band, color.new(tpCol, 95 if hit else 99))

            if showLabels:
                label.set_xy(tag, endBar + 1, targetPrice)

                label.set_color(tag, color.new(tpCol, 52 if hit else 76))

        positionEnded = True

    if flip:
        linesPerPosition: int = 4 + targetCount * 2
        boxesPerPosition: int = 1 + targetCount * 2
        labelsPerPosition: int = 2 + targetCount

        if positionCount >= keepPositions:
            for i in pine_range(0, linesPerPosition - 1):
                oldLine: Line = array.shift(allPositionLines)
                line.delete(oldLine)

            for i in pine_range(0, boxesPerPosition - 1):
                oldBox: Box = array.shift(allPositionBoxes)
                box.delete(oldBox)

            for i in pine_range(0, labelsPerPosition - 1):
                oldLabel: Label = array.shift(allPositionLabels)
                label.delete(oldLabel)

            positionCount -= 1

        array.clear(targetGlow)
        array.clear(targetCore)
        array.clear(targetZone)
        array.clear(targetBand)
        array.clear(targetTags)

        for i in pine_range(0, 3):
            array.set(targetHit, i, False)

        entryPrice = close
        entryBar = bar_index
        positionDir = 1 if bull else -1
        positionEnded = False

        structureStop: float = inline_series(ta.lowest(low, stopLookback), 1) if positionDir == 1 else inline_series(ta.highest(high, stopLookback), 1)

        rawRisk: float = entryPrice - structureStop if positionDir == 1 else structureStop - entryPrice

        minimumRisk: float = atr * minStopAtr
        maximumRisk: float = atr * maxStopAtr

        riskDist = math.min(math.max(nz(rawRisk, minimumRisk), minimumRisk), maximumRisk)

        stopPrice = entryPrice - positionDir * riskDist

        activeCol: Color = buyCol if positionDir == 1 else sellCol

        entryGlow = line.new(entryBar, entryPrice, bar_index + extendBars, entryPrice, xloc=xloc.bar_index, color=color.new(activeCol, 76), width=8)

        array.push(allPositionLines, entryGlow)

        entryCore = line.new(entryBar, entryPrice, bar_index + extendBars, entryPrice, xloc=xloc.bar_index, color=color.new(whiteCol, 10), width=1)

        array.push(allPositionLines, entryCore)

        stopGlow = line.new(entryBar, stopPrice, bar_index + extendBars, stopPrice, xloc=xloc.bar_index, color=color.new(slCol, 74), width=8)

        array.push(allPositionLines, stopGlow)

        stopCore = line.new(entryBar, stopPrice, bar_index + extendBars, stopPrice, xloc=xloc.bar_index, color=color.new(slCol, 2), width=2)

        array.push(allPositionLines, stopCore)

        riskBox = box.new(left=entryBar, top=math.max(entryPrice, stopPrice), right=bar_index + extendBars, bottom=math.min(entryPrice, stopPrice), xloc=xloc.bar_index, bgcolor=color.new(slCol, 94), border_color=color.new(slCol, 100))

        array.push(allPositionBoxes, riskBox)

        entryTag = label.new(bar_index + extendBars, entryPrice, 'LONG' if positionDir == 1 else 'SHORT', style=label.style_label_left, color=color.new(activeCol, 16) if showLabels else color.new(activeCol, 100), textcolor=whiteCol if showLabels else color.new(whiteCol, 100), size=labelSize)

        array.push(allPositionLabels, entryTag)

        stopTag = label.new(bar_index + extendBars, stopPrice, 'SL  -1R', style=label.style_label_left, color=color.new(slCol, 22) if showLabels else color.new(slCol, 100), textcolor=whiteCol if showLabels else color.new(whiteCol, 100), size=labelSize)

        array.push(allPositionLabels, stopTag)

        previousLevel: float = entryPrice

        for i in pine_range(0, targetCount - 1):
            targetPrice: float = entryPrice + positionDir * riskDist * (i + 1)
            zoneHalf: float = riskDist * zonePct

            glow: Line = line.new(entryBar, targetPrice, bar_index + extendBars, targetPrice, xloc=xloc.bar_index, color=color.new(tpCol, 94), width=8)

            core: Line = line.new(entryBar, targetPrice, bar_index + extendBars, targetPrice, xloc=xloc.bar_index, color=color.new(tpCol, 82), width=1)

            zone: Box = box.new(left=entryBar, top=targetPrice + zoneHalf, right=bar_index + extendBars, bottom=targetPrice - zoneHalf, xloc=xloc.bar_index, bgcolor=color.new(tpCol, 97), border_color=color.new(tpCol, 92))

            band: Box = box.new(left=entryBar, top=math.max(previousLevel, targetPrice), right=bar_index + extendBars, bottom=math.min(previousLevel, targetPrice), xloc=xloc.bar_index, bgcolor=color.new(tpCol, 97 - i), border_color=color.new(tpCol, 100))

            tag: Label = label.new(bar_index + extendBars, targetPrice, 'T' + string.tostring(i + 1) + '  ' + string.tostring(i + 1) + 'R', style=label.style_label_left, color=color.new(tpCol, 80) if showLabels else color.new(tpCol, 100), textcolor=whiteCol if showLabels else color.new(whiteCol, 100), size=labelSize)

            array.push(targetGlow, glow)
            array.push(targetCore, core)
            array.push(targetZone, zone)
            array.push(targetBand, band)
            array.push(targetTags, tag)

            array.push(allPositionLines, glow)
            array.push(allPositionLines, core)

            array.push(allPositionBoxes, zone)
            array.push(allPositionBoxes, band)

            array.push(allPositionLabels, tag)

            previousLevel = targetPrice

        positionCount += 1

    if not na(entryPrice) and (not positionEnded) and (array.size(targetGlow) > 0):
        activeCol: Color = buyCol if positionDir == 1 else sellCol

        stoppedNow: bool = bar_index > entryBar and (low <= stopPrice if positionDir == 1 else high >= stopPrice)

        if stoppedNow:
            endBar: int = bar_index

            line.set_xy2(entryGlow, endBar, entryPrice)
            line.set_xy2(entryCore, endBar, entryPrice)

            line.set_xy2(stopGlow, endBar, stopPrice)
            line.set_xy2(stopCore, endBar, stopPrice)

            line.set_color(entryGlow, color.new(activeCol, 88))

            line.set_color(entryCore, color.new(whiteCol, 50))

            line.set_color(stopGlow, color.new(slCol, 48))

            line.set_color(stopCore, color.new(whiteCol, 5))

            box.set_right(riskBox, endBar)

            box.set_bgcolor(riskBox, color.new(slCol, 87))

            if showLabels:
                label.set_xy(entryTag, endBar + 1, entryPrice)

                label.set_color(entryTag, color.new(activeCol, 58))

                label.set_xy(stopTag, endBar + 1, stopPrice)

                label.set_text(stopTag, 'SL  -1R  ✓')

                label.set_color(stopTag, color.new(slCol, 12))

            for i in pine_range(0, array.size(targetGlow) - 1):
                targetPrice: float = entryPrice + positionDir * riskDist * (i + 1)

                glow: Line = array.get(targetGlow, i)
                core: Line = array.get(targetCore, i)
                zone: Box = array.get(targetZone, i)
                band: Box = array.get(targetBand, i)
                tag: Label = array.get(targetTags, i)

                hit: bool = array.get(targetHit, i)

                line.set_xy2(glow, endBar, targetPrice)
                line.set_xy2(core, endBar, targetPrice)

                line.set_color(glow, color.new(tpCol, 80 if hit else 95))

                line.set_color(core, color.new(whiteCol, 38) if hit else color.new(tpCol, 82))

                box.set_right(zone, endBar)
                box.set_right(band, endBar)

                box.set_bgcolor(zone, color.new(tpCol, 93 if hit else 99))

                box.set_bgcolor(band, color.new(tpCol, 95 if hit else 99))

                if showLabels:
                    label.set_xy(tag, endBar + 1, targetPrice)

                    label.set_color(tag, color.new(tpCol, 52 if hit else 82))

            positionEnded = True
        else:
            line.set_xy2(entryGlow, bar_index + extendBars, entryPrice)

            line.set_xy2(entryCore, bar_index + extendBars, entryPrice)

            line.set_xy2(stopGlow, bar_index + extendBars, stopPrice)

            line.set_xy2(stopCore, bar_index + extendBars, stopPrice)

            box.set_right(riskBox, bar_index + extendBars)

            if showLabels:
                label.set_xy(entryTag, bar_index + extendBars, entryPrice)

                label.set_xy(stopTag, bar_index + extendBars, stopPrice)

            previousLevel: float = entryPrice

            for i in pine_range(0, array.size(targetGlow) - 1):
                targetPrice: float = entryPrice + positionDir * riskDist * (i + 1)
                zoneHalf: float = riskDist * zonePct

                hit: bool = array.get(targetHit, i)

                hit = hit or (high >= targetPrice if positionDir == 1 else low <= targetPrice)

                array.set(targetHit, i, hit)

                distance: float = math.abs(close - targetPrice)

                radius: float = math.max(riskDist * approachR, syminfo.mintick)

                proximity: float = math.max(0.0, math.min(1.0, 1.0 - distance / radius))

                glowT: int = 60 if hit else cast_int(math.round(95.0 - proximity * 30.0))

                targetCoreT: int = 4 if hit else cast_int(math.round(88.0 - proximity * 72.0))

                zoneT: int = 84 if hit else cast_int(math.round(98.0 - proximity * 10.0))

                bandT: int = math.max(85, 90 - i * 2) if hit else cast_int(math.round(97.0 - proximity * 5.0))

                glow: Line = array.get(targetGlow, i)
                core: Line = array.get(targetCore, i)
                zone: Box = array.get(targetZone, i)
                band: Box = array.get(targetBand, i)
                tag: Label = array.get(targetTags, i)

                line.set_xy2(glow, bar_index + extendBars, targetPrice)

                line.set_xy2(core, bar_index + extendBars, targetPrice)

                line.set_color(glow, color.new(tpCol, glowT))

                line.set_color(core, color.new(whiteCol, targetCoreT) if hit else color.new(tpCol, targetCoreT))

                box.set_right(zone, bar_index + extendBars)

                box.set_top(zone, targetPrice + zoneHalf)

                box.set_bottom(zone, targetPrice - zoneHalf)

                box.set_bgcolor(zone, color.new(tpCol, zoneT))

                box.set_border_color(zone, color.new(tpCol, math.max(25, zoneT - 12)))

                box.set_right(band, bar_index + extendBars)

                box.set_top(band, math.max(previousLevel, targetPrice))

                box.set_bottom(band, math.min(previousLevel, targetPrice))

                box.set_bgcolor(band, color.new(tpCol, bandT))

                if showLabels:
                    label.set_xy(tag, bar_index + extendBars, targetPrice)

                    label.set_text(tag, 'T' + string.tostring(i + 1) + '  ' + string.tostring(i + 1) + 'R' + ('  ✓' if hit else ''))

                    label.set_color(tag, color.new(tpCol, 14 if hit else math.max(38, targetCoreT)))

                previousLevel = targetPrice

    plotshape(bullFlip, title='Bull Trend', location=location.belowbar, style=shape.diamond, size=size.small, color=buyCol)

    plotshape(bearFlip, title='Bear Trend', location=location.abovebar, style=shape.diamond, size=size.small, color=sellCol)

    alertcondition(bullFlip, 'Bull Trend', 'Bull trend position started')

    alertcondition(bearFlip, 'Bear Trend', 'Bear trend position started')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
