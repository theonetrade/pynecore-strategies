"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barcolor, barstate, bgcolor,
    box, close, color, fill, format, high, hlc3, input, label, line, location, low, math, na, open,
    plot, plotshape, position, script, shape, size, string, ta, table, volume
)
from pynecore.types import Box, Label, Line, Persistent, Table


@script.indicator('VWAP Supply & Demand Zones PRO', overlay=True, max_lines_count=100, max_boxes_count=50)
def main(
    vwapLength=input.int(20, 'VWAP Length', minval=1, maxval=100, group='VWAP Settings'),
    zoneWidth=input.float(0.5, 'Zone Width %', minval=0.1, maxval=3.0, step=0.1, group='Zone Settings'),
    maxZones=input.int(5, 'Max Zones Per Type', minval=1, maxval=10, group='Zone Settings'),
    minTouches=input.int(2, 'Min Touches to Validate', minval=1, maxval=5, group='Zone Settings'),
    zoneExtension=input.int(30, 'Zone Extension (bars)', minval=10, maxval=100, group='Zone Settings'),
    showVWAP=input.bool(True, 'Show VWAP', group='Visual Settings'),
    showZones=input.bool(True, 'Show Supply/Demand Zones', group='Visual Settings'),
    showLabels=input.bool(True, 'Show Zone Labels', group='Visual Settings'),
    showHUD=input.bool(True, 'Show HUD', group='Visual Settings'),
    vwapColor=input.color(color.blue, 'VWAP Color', group='Colors'),
    supplyColor=input.color(color.red, 'Supply Zone Color', group='Colors'),
    demandColor=input.color(color.green, 'Demand Zone Color', group='Colors'),
    neutralColor=input.color(color.gray, 'Neutral Color', group='Colors'),
    alertOnNewZone=input.bool(True, 'Alert on New Zone', group='Alerts'),
    alertOnZoneTest=input.bool(True, 'Alert on Zone Test', group='Alerts'),
    alertOnZoneBreak=input.bool(True, 'Alert on Zone Break', group='Alerts')
):
    supplyBoxes: Persistent[list[Box]] = array.new_box()
    supplyLines: Persistent[list[Line]] = array.new_line()
    supplyLabels: Persistent[list[Label]] = array.new_label()
    supplyPrices: Persistent[list[float]] = array.new_float()
    supplyBottoms: Persistent[list[float]] = array.new_float()
    supplyTouches: Persistent[list[int]] = array.new_int()
    supplyBroken: Persistent[list[bool]] = array.new_bool()
    demandBoxes: Persistent[list[Box]] = array.new_box()
    demandLines: Persistent[list[Line]] = array.new_line()
    demandLabels: Persistent[list[Label]] = array.new_label()
    demandPrices: Persistent[list[float]] = array.new_float()
    demandTops: Persistent[list[float]] = array.new_float()
    demandTouches: Persistent[list[int]] = array.new_int()
    demandBroken: Persistent[list[bool]] = array.new_bool()
    hudTable: Persistent[Table] = na(Table)
    activeSupply: Persistent[int] = 0
    activeDemand: Persistent[int] = 0
    def f_safeColor(baseColor, transparency):
        return color.new(baseColor, transparency)

    def f_cleanupZones(boxes, lines, labels, prices1, prices2, touches, broken, maxCount):
        __block_result__ = na
        while array.size(boxes) > maxCount:
            if array.size(boxes) > 0:
                oldBox: Box = array.shift(boxes)
                box.delete(oldBox)
            if array.size(lines) > 0:
                oldLine: Line = array.shift(lines)
                line.delete(oldLine)
            if array.size(labels) > 0:
                oldLabel: Label = array.shift(labels)
                label.delete(oldLabel)
            if array.size(prices1) > 0:
                array.shift(prices1)
            if array.size(prices2) > 0:
                array.shift(prices2)
            if array.size(touches) > 0:
                array.shift(touches)
            __block_result_1__ = na
            if array.size(broken) > 0:
                __block_result_1__ = array.shift(broken)
            __block_result__ = __block_result_1__
        return __block_result__

    vwapSource = hlc3
    vwapNum = ta.sma(vwapSource * volume, vwapLength)
    vwapDen = ta.sma(volume, vwapLength)
    vwapValue = vwapNum / vwapDen if vwapDen != 0 else na
    hasEnoughHistory = bar_index > vwapLength * 2
    isConfirmedBar = barstate.isconfirmed or barstate.islastconfirmedhistory
    volMA = ta.sma(volume, 20)
    atrValue = ta.atr(14)
    crossover_1 = ta.crossover(close, vwapValue)
    vwapCrossUp = isConfirmedBar and crossover_1
    crossunder_1 = ta.crossunder(close, vwapValue)
    vwapCrossDown = isConfirmedBar and crossunder_1
    volumeConfirm = isConfirmedBar and volume > volMA * 1.2
    momentumConfirm = isConfirmedBar and math.abs(close - open) > atrValue * 0.5
    createSupplyZone = hasEnoughHistory and vwapCrossDown and volumeConfirm and momentumConfirm
    supplyZoneTop = high * (1 + zoneWidth / 100) if createSupplyZone else na
    supplyZoneBottom = vwapValue if createSupplyZone else na
    createDemandZone = hasEnoughHistory and vwapCrossUp and volumeConfirm and momentumConfirm
    demandZoneTop = vwapValue if createDemandZone else na
    demandZoneBottom = low * (1 - zoneWidth / 100) if createDemandZone else na
    if createSupplyZone and showZones and (not na(supplyZoneTop)) and (not na(supplyZoneBottom)):
        f_cleanupZones(supplyBoxes, supplyLines, supplyLabels, supplyPrices, supplyBottoms, supplyTouches, supplyBroken, maxZones - 1)
        startBar = bar_index
        endBar = bar_index + zoneExtension
        zoneBox: Box = box.new(startBar, supplyZoneTop, endBar, supplyZoneBottom, border_color=supplyColor, bgcolor=f_safeColor(supplyColor, 90))
        zoneLine: Line = line.new(startBar, supplyZoneTop, endBar, supplyZoneTop, color=supplyColor, width=2, style=line.style_dotted)
        __block_result_2__ = na
        if showLabels:
            __block_result_2__ = label.new(startBar + 2, supplyZoneTop, 'Supply\n' + string.tostring(supplyZoneTop, format.mintick), color=supplyColor, style=label.style_label_down, textcolor=color.white, size=size.small)
        else:
            __block_result_2__ = na
        zoneLabel: Label = __block_result_2__
        array.push(supplyBoxes, zoneBox)
        array.push(supplyLines, zoneLine)
        array.push(supplyLabels, zoneLabel)
        array.push(supplyPrices, supplyZoneTop)
        array.push(supplyBottoms, supplyZoneBottom)
        array.push(supplyTouches, 0)
        array.push(supplyBroken, False)
        if alertOnNewZone:
            alert('New Supply Zone Created at ' + string.tostring(supplyZoneTop, format.mintick), alert.freq_once_per_bar)
    if createDemandZone and showZones and (not na(demandZoneTop)) and (not na(demandZoneBottom)):
        f_cleanupZones(demandBoxes, demandLines, demandLabels, demandPrices, demandTops, demandTouches, demandBroken, maxZones - 1)
        startBar = bar_index
        endBar = bar_index + zoneExtension
        zoneBox: Box = box.new(startBar, demandZoneTop, endBar, demandZoneBottom, border_color=demandColor, bgcolor=f_safeColor(demandColor, 90))
        zoneLine: Line = line.new(startBar, demandZoneBottom, endBar, demandZoneBottom, color=demandColor, width=2, style=line.style_dotted)
        __block_result_3__ = na
        if showLabels:
            __block_result_3__ = label.new(startBar + 2, demandZoneBottom, 'Demand\n' + string.tostring(demandZoneBottom, format.mintick), color=demandColor, style=label.style_label_up, textcolor=color.white, size=size.small)
        else:
            __block_result_3__ = na
        zoneLabel: Label = __block_result_3__
        array.push(demandBoxes, zoneBox)
        array.push(demandLines, zoneLine)
        array.push(demandLabels, zoneLabel)
        array.push(demandPrices, demandZoneBottom)
        array.push(demandTops, demandZoneTop)
        array.push(demandTouches, 0)
        array.push(demandBroken, False)
        if alertOnNewZone:
            alert('New Demand Zone Created at ' + string.tostring(demandZoneBottom, format.mintick), alert.freq_once_per_bar)
    activeSupply = 0
    supplyCount = array.size(supplyBoxes)
    if supplyCount > 0:
        for i in pine_range(0, supplyCount - 1, 1):
            isBroken = array.get(supplyBroken, i)
            if not isBroken:
                zonePrice = array.get(supplyPrices, i)
                zoneBottom = array.get(supplyBottoms, i)
                box.set_right(array.get(supplyBoxes, i), bar_index + zoneExtension)
                line.set_x2(array.get(supplyLines, i), bar_index + zoneExtension)
                if high >= zoneBottom and high <= zonePrice:
                    touches = array.get(supplyTouches, i) + 1
                    array.set(supplyTouches, i, touches)
                    if alertOnZoneTest and touches == minTouches:
                        alert('Supply Zone Tested at ' + string.tostring(zonePrice, format.mintick), alert.freq_once_per_bar_close)
                if close > zonePrice:
                    array.set(supplyBroken, i, True)
                    zoneBox: Box = array.get(supplyBoxes, i)
                    box.set_bgcolor(zoneBox, f_safeColor(neutralColor, 95))
                    if alertOnZoneBreak:
                        alert('Supply Zone Broken at ' + string.tostring(zonePrice, format.mintick), alert.freq_once_per_bar_close)
                else:
                    activeSupply = activeSupply + 1
    activeDemand = 0
    demandCount = array.size(demandBoxes)
    if demandCount > 0:
        for i in pine_range(0, demandCount - 1, 1):
            isBroken = array.get(demandBroken, i)
            if not isBroken:
                zonePrice = array.get(demandPrices, i)
                zoneTop = array.get(demandTops, i)
                box.set_right(array.get(demandBoxes, i), bar_index + zoneExtension)
                line.set_x2(array.get(demandLines, i), bar_index + zoneExtension)
                if low <= zoneTop and low >= zonePrice:
                    touches = array.get(demandTouches, i) + 1
                    array.set(demandTouches, i, touches)
                    if alertOnZoneTest and touches == minTouches:
                        alert('Demand Zone Tested at ' + string.tostring(zonePrice, format.mintick), alert.freq_once_per_bar_close)
                if close < zonePrice:
                    array.set(demandBroken, i, True)
                    zoneBox: Box = array.get(demandBoxes, i)
                    box.set_bgcolor(zoneBox, f_safeColor(neutralColor, 95))
                    if alertOnZoneBreak:
                        alert('Demand Zone Broken at ' + string.tostring(zonePrice, format.mintick), alert.freq_once_per_bar_close)
                else:
                    activeDemand = activeDemand + 1
    vwapPlot = plot(vwapValue if showVWAP else na, 'VWAP', color=vwapColor, linewidth=2)
    upperBand = vwapValue * (1 + zoneWidth / 1000)
    lowerBand = vwapValue * (1 - zoneWidth / 1000)
    upperPlot = plot(upperBand if showVWAP else na, 'Upper Band', color=f_safeColor(vwapColor, 70), linewidth=1)
    lowerPlot = plot(lowerBand if showVWAP else na, 'Lower Band', color=f_safeColor(vwapColor, 70), linewidth=1)
    fill(upperPlot, vwapPlot, color=f_safeColor(supplyColor, 95), title='Upper Fill')
    fill(vwapPlot, lowerPlot, color=f_safeColor(demandColor, 95), title='Lower Fill')
    inSupplyZone: bool = False
    if supplyCount > 0:
        for i in pine_range(0, supplyCount - 1, 1):
            if not array.get(supplyBroken, i):
                zoneTop = array.get(supplyPrices, i)
                zoneBottom = array.get(supplyBottoms, i)
                if high >= zoneBottom and low <= zoneTop:
                    inSupplyZone = True
                    break
    inDemandZone: bool = False
    if demandCount > 0:
        for i in pine_range(0, demandCount - 1, 1):
            if not array.get(demandBroken, i):
                zoneBottom = array.get(demandPrices, i)
                zoneTop = array.get(demandTops, i)
                if high >= zoneBottom and low <= zoneTop:
                    inDemandZone = True
                    break
    bgcolor(f_safeColor(supplyColor, 95) if inSupplyZone else f_safeColor(demandColor, 95) if inDemandZone else na)
    plotshape(supplyZoneTop if createSupplyZone else na, title='Supply Zone Created', style=shape.triangledown, location=location.absolute, color=supplyColor, size=size.small)
    plotshape(demandZoneBottom if createDemandZone else na, title='Demand Zone Created', style=shape.triangleup, location=location.absolute, color=demandColor, size=size.small)
    barcolor((f_safeColor(demandColor, 70) if close > vwapValue else f_safeColor(supplyColor, 70)) if showVWAP and (not na(vwapValue)) else na)
    if barstate.isfirst and showHUD:
        hudTable = table.new(position.bottom_right, 3, 6, bgcolor=color.new(color.black, 90), border_width=1)
    if showHUD and barstate.islast and (not na(hudTable)):
        table.clear(hudTable, 0, 0, 2, 5)
        table.cell(hudTable, 0, 0, 'VWAP S&D', text_color=color.white, bgcolor=color.new(color.blue, 50))
        table.merge_cells(hudTable, 0, 0, 2, 0)
        table.cell(hudTable, 0, 1, 'Supply', text_color=color.white, text_size=size.tiny)
        table.cell(hudTable, 1, 1, string.tostring(activeSupply), text_color=supplyColor, text_size=size.tiny)
        table.cell(hudTable, 2, 1, '▼' if activeSupply > 0 else '-', text_color=supplyColor, text_size=size.tiny)
        table.cell(hudTable, 0, 2, 'Demand', text_color=color.white, text_size=size.tiny)
        table.cell(hudTable, 1, 2, string.tostring(activeDemand), text_color=demandColor, text_size=size.tiny)
        table.cell(hudTable, 2, 2, '▲' if activeDemand > 0 else '-', text_color=demandColor, text_size=size.tiny)
        table.cell(hudTable, 0, 3, 'VWAP', text_color=color.white, text_size=size.tiny)
        table.cell(hudTable, 1, 3, string.tostring(vwapValue, format.mintick), text_color=vwapColor, text_size=size.tiny)
        table.cell(hudTable, 2, 3, ('↑' if close > vwapValue else '↓') if not na(vwapValue) else '-', text_color=(demandColor if close > vwapValue else supplyColor) if not na(vwapValue) else neutralColor, text_size=size.tiny)
        marketBias = 'BEAR' if activeSupply > activeDemand else 'BULL' if activeDemand > activeSupply else 'NEUTRAL'
        biasColor = supplyColor if marketBias == 'BEAR' else demandColor if marketBias == 'BULL' else neutralColor
        table.cell(hudTable, 0, 4, 'Bias', text_color=color.white, text_size=size.tiny)
        table.cell(hudTable, 1, 4, marketBias, text_color=biasColor, text_size=size.tiny)
        table.cell(hudTable, 2, 4, '🐻' if marketBias == 'BEAR' else '🐂' if marketBias == 'BULL' else '➖', text_color=biasColor, text_size=size.tiny)
    alertcondition(inSupplyZone, title='In Supply Zone', message='Price entered supply zone - potential reversal')
    alertcondition(inDemandZone, title='In Demand Zone', message='Price entered demand zone - potential reversal')
    alertcondition(vwapCrossUp, title='VWAP Cross Up', message='Price crossed above VWAP')
    alertcondition(vwapCrossDown, title='VWAP Cross Down', message='Price crossed below VWAP')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
