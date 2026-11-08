"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_import import shadowed_namespace
from pynecore.core.pine_udt import udt, udt_copy
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barstate, box, close, color,
    display, extend, format, high, input, label, last_bar_index, line, location, log, low, math,
    na, nz, open, plot, plotshape, position, runtime, script, shape, size, string, ta, table, text,
    time, time_close, timeframe, volume, xloc, yloc
)
from pynecore.types import Box, Label, Line, NA, Persistent, PersistentSeries, Table
import lib.TradingView.ta.v8 as ta__ren____lib


ta__ren__ = shadowed_namespace(ta__ren____lib, ta)


@udt
class orderBlockInfo:
    top: float = na(float)
    bottom: float = na(float)
    obVolume: float = na(float)
    obType: str = na(str)
    startTime: int = na(int)
    bbVolume: float = na(float)
    obLowVolume: float = na(float)
    obHighVolume: float = na(float)
    breaker: bool = False
    breakTime: int = na(int)
    breakerEndTime: int = na(int)
    timeframeStr: str = na(str)
    disabled: bool = False
    combinedTimeframesStr: str = na(str)
    combined: bool = False


@udt
class orderBlock:
    info: 'orderBlockInfo' = _dataclass_field(default_factory=lambda: na(orderBlockInfo))
    isRendered: bool = False
    orderBox: Box = na(Box)
    breakerBox: Box = na(Box)
    orderBoxLineTop: Line = na(Line)
    orderBoxLineBottom: Line = na(Line)
    breakerBoxLineTop: Line = na(Line)
    breakerBoxLineBottom: Line = na(Line)
    orderBoxText: Box = na(Box)
    orderBoxPositive: Box = na(Box)
    orderBoxNegative: Box = na(Box)
    orderSeperator: Line = na(Line)
    orderTextSeperator: Line = na(Line)


@udt
class FVGInfo:
    max: float = na(float)
    min: float = na(float)
    isBull: bool = na(bool)
    t: int = na(int)
    totalVolume: float = na(float)
    startBarIndex: int = na(int)
    endBarIndex: int = na(int)
    startTime: int = na(int)
    endTime: int = na(int)
    extendInfinite: bool = False
    combined: bool = False
    combinedTimeframesStr: str = na(str)
    disabled: bool = False
    timeframeStr: str = na(str)
    lowVolume: float = na(float)
    highVolume: float = na(float)
    isInverse: bool = False
    lastTouched: int = na(int)
    lastTouchedIFVG: int = na(int)
    inverseEndIndex: int = na(int)
    inverseEndTime: int = na(int)
    inverseVolume: float = na(float)


@udt
class FVG:
    info: 'FVGInfo' = _dataclass_field(default_factory=lambda: na(FVGInfo))
    isRendered: bool = False
    fvgBox: Box = na(Box)
    ifvgBox: Box = na(Box)
    fvgBoxText: Box = na(Box)
    fvgBoxPositive: Box = na(Box)
    fvgBoxNegative: Box = na(Box)
    fvgSeperator: Line = na(Line)
    fvgTextSeperator: Line = na(Line)


@udt
class obSwing:
    x: int = na(int)
    y: float = na(float)
    crossed: bool = False


@udt
class CVDS:
    state: str = na(str)
    startTime: int = na(int)
    overlapDirection: str = na(str)
    cvdsTime: int = na(int)
    cvdsClose: float = na(float)
    breakTime: int = na(int)
    fvg: 'FVG' = _dataclass_field(default_factory=lambda: na(FVG))
    fvgEndTime: int = na(int)
    ob: 'orderBlock' = _dataclass_field(default_factory=lambda: na(orderBlock))
    slTarget: float = na(float)
    tpTarget: float = na(float)
    entryType: str = na(str)
    entryTime: int = na(int)
    exitTime: int = na(int)
    entryPrice: float = na(float)
    exitPrice: float = na(float)
    dayEndedBeforeExit: int = na(int)


DEBUG: bool = False
DEBUGOBFVG: bool = False
maxBoxesCount: int = 500
maxDistanceToLastBar: int = 100000
showLastXFVGs: int = 2
maxOrderBlocks: int = 5
maxBarsBack: int = 50
extendLastXFVGsCount: int = 20
minimumFVGSize: int = 2
minimumIFVGSize: int = 2
overlapThresholdPercentage: float = 0
atrLen: int = 10
maxCVDS: int = 100
atrLenCVDS: int = 50


@script.indicator('Cumulative Volume Delta Strategy | Flux Charts', 'CVDS | Flux Charts', overlay=True, max_boxes_count=maxBoxesCount, max_labels_count=maxBoxesCount, max_lines_count=maxBoxesCount)
def main(
    anchorInput=input.timeframe('1D', 'Anchor Period', group='General Configuration', display=display.none),
    entryMode=input.string('FVGs', 'Entry Mode', options=('FVGs', 'Order Blocks'), group='General Configuration'),
    requireRetracement=input.bool(True, 'Require Retracement', tooltip='A retracement to the FVG or Order Block will be required for entry confirmation if enabled.', group='General Configuration'),
    showCVDSLines=input.bool(True, 'Show CVDS Lines', group='General Configuration'),
    fvgSensitivityText=input.string('High', 'FVG Detection Sensitivity', options=('All', 'Extreme', 'High', 'Normal', 'Low'), group='Fair Value Gaps'),
    showFVG=input.bool(True, 'Show FVGs', inline='bb', group='Fair Value Gaps'),
    swingLength=input.int(10, 'Swing Length', minval=3, maxval=45, tooltip='Swing length is used when finding order block formations. Smaller values will result in finding smaller order blocks.', group='Order Blocks', display=display.none),
    showOB=input.bool(True, 'Show Order Blocks', group='Order Blocks'),
    __input_8__=input.string('Normal', '[DBG] Label Size', options=('Normal', 'Small', 'Tiny'), group='General Configuration'),
    __input_9__=input.bool(False, '[DBG] Show All BB and FVGs', group='General Configuration'),
    showTPSL=input.bool(True, 'Enabled', group='TP / SL'),
    tpslMethod=input.string('Dynamic', 'TP / SL Method', options=('Dynamic', 'Fixed'), group='TP / SL'),
    riskAmount=input.string('High', 'Dynamic Risk', options=('Highest', 'High', 'Normal', 'Low', 'Lowest'), group='TP / SL', tooltip='The risk amount when Dynamic TP / SL method is selected.\n\nDifferent assets may have different volatility so changing this setting may result in change of performance of the indicator.'),
    __input_13__=input.float(6.5, '[DBG] Dynamic Custom Risk Mult', group='TP / SL'),
    tpPercent=input.float(0.3, 'Fixed Take Profit %', step=0.1, group='TP / SL'),
    slPercent=input.float(0.4, 'Fixed Stop Loss %', step=0.1, group='TP / SL'),
    backtestDisplayEnabled=input.bool(True, 'Enabled', group='Backtesting Dashboard', display=display.none),
    backtestingLocation=input.string('Top Center', 'Position', options=('Top Right', 'Right Center', 'Top Center'), group='Backtesting Dashboard', display=display.none),
    fillBackgrounds=input.bool(True, 'Fill Backgrounds', group='Backtesting Dashboard', display=display.none),
    screenerColor=input.color(color.new('#1B1F2B'), 'Background', inline='1', group='Backtesting Dashboard', display=display.none),
    __input_20__=input.float(0.57, '[DBG] Dynamic Risk:Reward Ratio', group='Debug'),
    __input_21__=input.string('Raw', '[DBG] Signal Type', options=('Advanced', 'Raw'), group='Debug'),
    buyAlertEnabled=input.bool(True, 'Buy Signal', inline='BS', group='Alerts'),
    sellAlertEnabled=input.bool(True, 'Sell Signal', inline='BS', group='Alerts'),
    tpAlertEnabled=input.bool(True, 'Take-Profit Signal', inline='TS', group='Alerts'),
    slAlertEnabled=input.bool(True, 'Stop-Loss Signal ', inline='TS', group='Alerts'),
    dbgTPSLVersion=input.string('Default', 'TP / SL Layout', options=('Default', 'Alternative'), group='Visuals'),
    fvgBullColor=input(color.new('#08998180'), 'Bullish Structure', inline='fvgColor', group='Visuals', display=display.none),
    fvgBearColor=input(color.new('#F2364680'), 'Bearish Structure', inline='fvgColor', group='Visuals', display=display.none),
    highColor=input.color(color.new('#089981'), 'Buy', inline='colors', group='Visuals'),
    lowColor=input.color(color.new('#F23646'), 'Sell', inline='colors', group='Visuals'),
    textColor=input.color(color.new('#FFFFFF'), 'Text', inline='colors', group='Visuals'),
    __input_32__=input.bool(True, 'Show Historic Zones', group='General Configuration', display=display.none),
    __input_33__=input.bool(True, 'Enabled', group='Fair Value Gaps', inline='EV', display=display.none),
    __input_34__=input.bool(False, 'Volumetric Info', group='Fair Value Gaps', inline='EV', display=display.none),
    __input_35__=input.string('Close', 'Zone Invalidation', options=('Wick', 'Close'), group='Fair Value Gaps'),
    __input_36__=input.string('Average Range', 'Zone Filtering', options=('Average Range', 'Volume Threshold'), group='Fair Value Gaps'),
    __input_37__=input.int(50, 'Volume Threshold %', group='Fair Value Gaps', tooltip='Only taken into calculation when filter method is Volume Threshold.', minval=1, maxval=200),
    __input_38__=input.string('Same Type', 'FVG Detection', options=('Same Type', 'All'), tooltip='Same Type -> All 3 bars that formed the FVG should be the same type. (Bullish / Bearish) \n\nAll -> Bar types may vary between bullish / bearish.', group='Fair Value Gaps'),
    __input_39__=input.bool(True, '', tooltip='', inline='sens', group='Fair Value Gaps'),
    __input_40__=input.bool(False, 'Combine Zones', group='Fair Value Gaps'),
    __input_41__=input.bool(False, 'Allow Gaps Between Bars', group='Fair Value Gaps', tooltip='On tickers that can have a different opening price than the previous bar\'s closing price, the indicator will not analyze those bars for FVGs if disabled.\n\nFor Example, if the today\'s opening price is different from the yesterday\'s closing price in a stock ticker.'),
    __input_42__=input.bool(True, '', group='Fair Value Gaps', inline='deleteUntouched'),
    __input_43__=input.int(200, 'Delete Untouched Zones After', group='Fair Value Gaps', minval=5, maxval=200, inline='deleteUntouched'),
    __input_44__=input.bool(False, 'Enabled', inline='EV', group='Inversion Fair Value Gaps'),
    __input_45__=input.bool(False, 'Volumetric Info', group='Inversion Fair Value Gaps', inline='EV', display=display.none),
    __input_46__=input.string('Wick', 'IFVG Zone Invalidation', options=('Wick', 'Close'), group='Inversion Fair Value Gaps'),
    __input_47__=input.bool(True, 'IFVG Full', group='Inversion Fair Value Gaps', display=display.none),
    __input_48__=input(color.new('#08998180'), 'Bullish', inline='breakerColor', group='Inversion Fair Value Gaps', display=display.none),
    __input_49__=input(color.new('#F2364580'), 'Bearish', inline='breakerColor', group='Inversion Fair Value Gaps', display=display.none),
    __input_50__=input.float(3.5, 'Max ATR Multiplier', group='General Configuration', display=display.none),
    __input_51__=input.int(15, 'Extend Zones', group='Style', minval=1, maxval=30, inline='ExtendZones'),
    __input_52__=input.bool(True, 'Dynamic', group='Style', inline='ExtendZones'),
    __input_53__=input.bool(True, 'Extend Last Zones', group='Style'),
    __input_54__=input.bool(False, 'Change Combined Zones Color', group='Style', inline='CombinedColor'),
    __input_55__=input.bool(False, 'Combined Text', group='Style', inline='CombinedColor'),
    __input_56__=input.color(color.new('#FFF70080'), '' if DEBUG else 'Combined Zone Color', group='Style', inline='CombinedColor'),
    __input_57__=input.string('Last Bar', 'Start FVG Zones From', options=('First Bar', 'Last Bar'), group='Style'),
    __input_58__=input.string('Left', 'Show Volume Bars At', options=('Left', 'Right'), group='Style', inline='volumebars'),
    __input_59__=input.bool(True, 'Mirror Volume Bars', group='Style', inline='volumebars')
):
    curTFMMS: Persistent[int] = timeframe.in_seconds()
    OBsEnabled: bool = True
    orderBlockVolumetricInfo: bool = False
    obEndMethod: str = 'Close'
    BBsEnabled: bool = False
    breakBlockVolumetricInfo: bool = False
    bbEndMethod: str = 'Wick'
    breakersFull: bool = True
    dbgLabelSize = __input_8__ if DEBUG else 'Normal'
    lblSize = size.small if dbgLabelSize == 'Small' else size.normal if dbgLabelSize == 'Normal' else size.tiny
    dbgShowBBFVG = __input_9__ if DEBUG else False
    customSLATRMult = __input_13__ if DEBUG else 6.5
    slATRMult = 10 if riskAmount == 'Highest' else 8.5 if riskAmount == 'High' else 6.5 if riskAmount == 'Normal' else 5 if riskAmount == 'Low' else 3 if riskAmount == 'Lowest' else customSLATRMult
    DynamicRR = __input_20__ if DEBUG else 0.57
    signalType = __input_21__ if DEBUG else 'Raw'
    bullOrderBlockColor = fvgBullColor
    bearOrderBlockColor = fvgBearColor
    showInvalidated = __input_32__ if DEBUGOBFVG else True
    fvgEnabled = __input_33__ if DEBUGOBFVG else True
    fvgVolumetricInfo = __input_34__ if DEBUGOBFVG else False
    fvgEndMethod = __input_35__ if DEBUGOBFVG else 'Close'
    fvgFilterMethod = __input_36__ if DEBUGOBFVG else 'Average Range'
    volumeThresholdPercent = __input_37__ if DEBUGOBFVG else 50
    fvgBars = __input_38__ if DEBUGOBFVG else 'Same Type'
    fvgSensEnabled = __input_39__ if DEBUGOBFVG else True
    combineFVGs = __input_40__ if DEBUGOBFVG else False
    allowGaps = __input_41__ if DEBUGOBFVG else False
    deleteUntouched = __input_42__ if DEBUGOBFVG else True
    deleteUntouchedAfterXBars = __input_43__ if DEBUGOBFVG else 200
    ifvgEnabled = __input_44__ if DEBUGOBFVG else False
    ifvgVolumetricInfo = __input_45__ if DEBUGOBFVG else False
    ifvgEndMethod = __input_46__ if DEBUGOBFVG else 'Wick'
    ifvgFull = __input_47__ if DEBUGOBFVG else True
    bullishInverseColor = __input_48__ if DEBUGOBFVG else color.new('#08998180')
    bearishInverseColor = __input_49__ if DEBUGOBFVG else color.new('#F2364580')
    maxATRMult = __input_50__ if DEBUG and DEBUGOBFVG else 3.5
    extendZonesBy = __input_51__ if DEBUG and DEBUGOBFVG else 15
    extendZonesDynamic = __input_52__ if DEBUG and DEBUGOBFVG else True
    extendLastFVGs = __input_53__ if DEBUG and DEBUGOBFVG else True
    changeCombinedFVGsColor = __input_54__ if DEBUG and DEBUGOBFVG else False
    combinedText = __input_55__ if DEBUG and DEBUGOBFVG else False
    combinedColor = __input_56__ if DEBUG and DEBUGOBFVG else color.new('#FFF70080')
    startZoneFrom = __input_57__ if DEBUG and DEBUGOBFVG else 'Last Bar'
    volumeBarsPlace = __input_58__ if DEBUG and DEBUGOBFVG else 'Left'
    mirrorVolumeBars = __input_59__ if DEBUG and DEBUGOBFVG else True
    def createFVGInfo(h, l, bull, t, tv):
        newFVGInfo: FVGInfo = FVGInfo(h, l, bull, t, tv)
        return newFVGInfo

    def createFVG(FVGInfoF: FVGInfo):
        newFVG: FVG = FVG(FVGInfoF)
        return newFVG

    def safeDeleteFVG(fvg__0000004e__: FVG):
        fvg__0000004e__.isRendered = False
        box.delete(fvg__0000004e__.fvgBox)
        box.delete(fvg__0000004e__.ifvgBox)
        box.delete(fvg__0000004e__.fvgBoxText)
        box.delete(fvg__0000004e__.fvgBoxPositive)
        box.delete(fvg__0000004e__.fvgBoxNegative)
        line.delete(fvg__0000004e__.fvgSeperator)
        return line.delete(fvg__0000004e__.fvgTextSeperator)

    volumeBarsLeftSide = volumeBarsPlace == 'Left'
    fvgSensitivity = 100 if fvgSensitivityText == 'All' else 6 if fvgSensitivityText == 'Extreme' else 2 if fvgSensitivityText == 'High' else 1.5 if fvgSensitivityText == 'Normal' else 1
    extendZonesByTime = extendZonesBy * timeframe.in_seconds(timeframe.period) * 1000
    atr = ta__ren__.atr(atrLen)
    volCheck = ta__ren__.cum(volume) > 0
    def moveLine(_line, _x, _y, _x2):
        line.set_xy1(_line, _x, _y)
        return line.set_xy2(_line, _x2, _y)

    def moveBox(_box, _topLeftX, _topLeftY, _bottomRightX, _bottomRightY):
        box.set_lefttop(_box, _topLeftX, _topLeftY)
        return box.set_rightbottom(_box, _bottomRightX, _bottomRightY)

    def colorWithTransparency(colorF, transparencyX):
        return color.new(colorF, color.t(colorF) * transparencyX)

    def createFVGBox(boxColor, transparencyX = 1.0, xlocType = xloc.bar_time):
        return box.new(na, na, na, na, text_size=size.normal, xloc=xlocType, extend=extend.none, bgcolor=colorWithTransparency(boxColor, transparencyX), text_color=textColor, text_halign=text.align_center, border_color=color.new('#00000000'))

    FVGInfoList: Persistent[list[FVGInfo]] = array.new(0, NA(FVGInfo))
    allFVGList: Persistent[list[FVG]] = array.new(0, NA(FVG))
    def arrHasFVG(arr: list[FVG], fvgF: FVG):
        hasFVG: bool = False
        if array.size(arr) > 0:
            for i in pine_range(0, array.size(arr) - 1, 1):
                fvg1: FVG = array.get(arr, i)
                if fvg1.info.startTime == fvgF.info.startTime:
                    hasFVG = True
                    break
        return hasFVG

    def arrHasIFVG(arr: list[FVG], fvgF: FVG):
        hasIFVG: bool = False
        if array.size(arr) > 0:
            for i in pine_range(0, array.size(arr) - 1, 1):
                fvg1: FVG = array.get(arr, i)
                if fvg1.info.isInverse:
                    if fvg1.info.startTime == fvgF.info.startTime:
                        hasIFVG = True
                        break
        return hasIFVG

    def renderFVG(fvg__0000009a__: FVG, customEndTime: int):
        fvg__0000009a__.isRendered = True
        if fvgEnabled and (not ifvgEnabled or not fvg__0000009a__.info.isInverse) and (showInvalidated or na(fvg__0000009a__.info.endTime)):
            fvg__0000009a__.fvgBox = createFVGBox(combinedColor if fvg__0000009a__.info.combined and changeCombinedFVGsColor else fvgBullColor if fvg__0000009a__.info.isBull else fvgBearColor, 1.5)
            fvg__0000009a__.fvgBoxText = createFVGBox(color.new(color.white, 100))
            if fvgVolumetricInfo:
                fvg__0000009a__.fvgBoxPositive = createFVGBox(fvgBullColor)
                fvg__0000009a__.fvgBoxNegative = createFVGBox(fvgBearColor)
                fvg__0000009a__.fvgSeperator = line.new(na, na, na, na, xloc.bar_time, extend.none, textColor, line.style_dashed, 1)
                fvg__0000009a__.fvgTextSeperator = line.new(na, na, na, na, xloc.bar_time, extend.none, textColor, line.style_solid, 1)
            zoneSize = (extendZonesByTime if na(fvg__0000009a__.info.endTime) else fvg__0000009a__.info.endTime - fvg__0000009a__.info.startTime) if extendZonesDynamic else extendZonesByTime
            if na(fvg__0000009a__.info.endTime) and fvg__0000009a__.info.extendInfinite:
                zoneSize = time + 1 - fvg__0000009a__.info.startTime
            if not na(customEndTime):
                zoneSize = customEndTime - fvg__0000009a__.info.startTime
            startX = fvg__0000009a__.info.startTime if volumeBarsLeftSide else fvg__0000009a__.info.startTime + zoneSize - zoneSize / 3
            maxEndX = fvg__0000009a__.info.startTime + zoneSize / 3 if volumeBarsLeftSide else fvg__0000009a__.info.startTime + zoneSize
            moveBox(fvg__0000009a__.fvgBox, fvg__0000009a__.info.startTime, fvg__0000009a__.info.max, fvg__0000009a__.info.startTime + zoneSize, fvg__0000009a__.info.min)
            moveBox(fvg__0000009a__.fvgBoxText, maxEndX if volumeBarsLeftSide else fvg__0000009a__.info.startTime, fvg__0000009a__.info.max, fvg__0000009a__.info.startTime + zoneSize if volumeBarsLeftSide else startX, fvg__0000009a__.info.min)
            percentage = cast_int(math.min(fvg__0000009a__.info.highVolume, fvg__0000009a__.info.lowVolume) / math.max(fvg__0000009a__.info.highVolume, fvg__0000009a__.info.lowVolume) * 100.0)
            FVGText: str = ''
            box.set_text(fvg__0000009a__.fvgBoxText, (string.tostring(fvg__0000009a__.info.totalVolume, format.volume) + ' (' + string.tostring(percentage) + '%)\n' if fvgVolumetricInfo else '') + ('[Combined]\n' if combinedText and fvg__0000009a__.info.combined else '') + FVGText)
            if fvg__0000009a__.info.combined and (not changeCombinedFVGsColor):
                box.set_bgcolor(fvg__0000009a__.fvgBox, colorWithTransparency(fvgBullColor if fvg__0000009a__.info.isBull else fvgBearColor, 1.1))
            if fvgVolumetricInfo:
                showHighLowBoxText: bool = False
                curEndXHigh = cast_int(math.ceil(fvg__0000009a__.info.highVolume / fvg__0000009a__.info.totalVolume * (maxEndX - startX) + startX))
                curEndXLow = cast_int(math.ceil(fvg__0000009a__.info.lowVolume / fvg__0000009a__.info.totalVolume * (maxEndX - startX) + startX))
                moveBox(fvg__0000009a__.fvgBoxPositive, startX if mirrorVolumeBars else curEndXLow, fvg__0000009a__.info.max, curEndXHigh if mirrorVolumeBars else maxEndX, (fvg__0000009a__.info.min + fvg__0000009a__.info.max) / 2)
                box.set_text(fvg__0000009a__.fvgBoxPositive, string.tostring(fvg__0000009a__.info.highVolume, format.volume) if showHighLowBoxText else '')
                moveBox(fvg__0000009a__.fvgBoxNegative, startX if mirrorVolumeBars else curEndXHigh, fvg__0000009a__.info.min, curEndXLow if mirrorVolumeBars else maxEndX, (fvg__0000009a__.info.min + fvg__0000009a__.info.max) / 2)
                box.set_text(fvg__0000009a__.fvgBoxNegative, string.tostring(fvg__0000009a__.info.lowVolume, format.volume) if showHighLowBoxText else '')
                moveLine(fvg__0000009a__.fvgSeperator, startX if volumeBarsLeftSide else maxEndX, (fvg__0000009a__.info.min + fvg__0000009a__.info.max) / 2, maxEndX if volumeBarsLeftSide else startX)
                line.set_xy1(fvg__0000009a__.fvgTextSeperator, maxEndX if volumeBarsLeftSide else startX, fvg__0000009a__.info.max)
                line.set_xy2(fvg__0000009a__.fvgTextSeperator, maxEndX if volumeBarsLeftSide else startX, fvg__0000009a__.info.min)
        __block_result__ = na
        if fvg__0000009a__.info.isInverse and ifvgEnabled:
            inverseColor = bearishInverseColor if fvg__0000009a__.info.isBull else bullishInverseColor
            fvg__0000009a__.ifvgBox = createFVGBox(inverseColor)
            startTimeIFVG = fvg__0000009a__.info.startTime if ifvgFull else fvg__0000009a__.info.endTime
            inverseZoneSize = time + 1 - startTimeIFVG if na(fvg__0000009a__.info.inverseEndTime) else fvg__0000009a__.info.inverseEndTime - startTimeIFVG
            moveBox(fvg__0000009a__.ifvgBox, startTimeIFVG, fvg__0000009a__.info.max, startTimeIFVG + inverseZoneSize, fvg__0000009a__.info.min)
            IFVGText: str = ''
            __block_result__ = box.set_text(fvg__0000009a__.ifvgBox, (string.tostring(fvg__0000009a__.info.inverseVolume, format.volume) + '\n' if ifvgVolumetricInfo else '') + ('[Combined]\n' if combinedText and fvg__0000009a__.info.combined else '') + IFVGText)
        return __block_result__

    def areaOfFVG(FVGInfoF: FVGInfo):
        XA1: float = FVGInfoF.startTime
        XA2: float = time + 1 if na(FVGInfoF.endTime) else FVGInfoF.endTime
        YA1: float = FVGInfoF.max
        YA2: float = FVGInfoF.min
        edge1: float = math.sqrt((XA2 - XA1) * (XA2 - XA1) + (YA2 - YA2) * (YA2 - YA2))
        edge2: float = math.sqrt((XA2 - XA2) * (XA2 - XA2) + (YA2 - YA1) * (YA2 - YA1))
        totalArea: float = edge1 * edge2
        return totalArea

    def doFVGsTouch(FVGInfo1: FVGInfo, FVGInfo2: FVGInfo):
        XA1: float = FVGInfo1.startTime
        XA2: float = time + 1 if na(FVGInfo1.endTime) else FVGInfo1.endTime
        YA1: float = FVGInfo1.max
        YA2: float = FVGInfo1.min
        XB1: float = FVGInfo2.startTime
        XB2: float = time + 1 if na(FVGInfo2.endTime) else FVGInfo2.endTime
        YB1: float = FVGInfo2.max
        YB2: float = FVGInfo2.min
        intersectionArea: float = math.max(0, math.min(XA2, XB2) - math.max(XA1, XB1)) * math.max(0, math.min(YA1, YB1) - math.max(YA2, YB2))
        unionArea: float = areaOfFVG(FVGInfo1) + areaOfFVG(FVGInfo2) - intersectionArea
        overlapPercentage: float = intersectionArea / unionArea * 100.0
        __block_result_1__ = na
        if overlapPercentage > overlapThresholdPercentage:
            __block_result_1__ = True
        else:
            __block_result_1__ = False
        return __block_result_1__

    def isFVGValid(FVGInfoF: FVGInfo):
        valid: bool = True
        if not showInvalidated and (not na(FVGInfoF.endTime)):
            valid = False
        elif FVGInfoF.disabled:
            valid = False
        return valid

    def isIFVGValid(FVGInfoF: FVGInfo):
        valid: bool = True
        if not ifvgEnabled:
            valid = False
        elif not showInvalidated and (not na(FVGInfoF.inverseEndTime)):
            valid = False
        elif FVGInfoF.disabled:
            valid = False
        return valid

    def isFVGValidInTimeframe(FVGInfoF: FVGInfo):
        valid: bool = True
        if not showInvalidated and (not na(FVGInfoF.endTime)):
            valid = False
        elif FVGInfoF.disabled:
            valid = False
        elif not na(FVGInfoF.endBarIndex) and FVGInfoF.endBarIndex - FVGInfoF.startBarIndex < minimumFVGSize:
            valid = False
        elif na(FVGInfoF.endBarIndex) and deleteUntouched and (bar_index - FVGInfoF.lastTouched > deleteUntouchedAfterXBars):
            valid = False
        return valid

    def isIFVGValidInTimeframe(FVGInfoF: FVGInfo):
        valid: bool = True
        if not ifvgEnabled:
            valid = False
        elif not showInvalidated and (not na(FVGInfoF.inverseEndIndex)):
            valid = False
        elif not na(FVGInfoF.inverseEndIndex) and FVGInfoF.inverseEndIndex - FVGInfoF.endBarIndex < minimumIFVGSize:
            valid = False
        elif na(FVGInfoF.inverseEndIndex) and deleteUntouched and (bar_index - FVGInfoF.lastTouchedIFVG > deleteUntouchedAfterXBars):
            valid = False
        return valid

    def combineFVGsFunc():
        __block_result_2__ = na
        if array.size(allFVGList) > 0:
            lastCombinations: int = 999
            __block_result_3__ = na
            while lastCombinations > 0:
                lastCombinations = 0
                __block_result_4__ = na
                __loop_2__ = pine_loop(0, 1)
                while __loop_2__.step(array.size(allFVGList) - 1):
                    i = __loop_2__.value
                    curFVG1 = array.get(allFVGList, i)
                    __block_result_5__ = na
                    __loop_3__ = pine_loop(0, 1)
                    while __loop_3__.step(array.size(allFVGList) - 1):
                        j = __loop_3__.value
                        curFVG2 = array.get(allFVGList, j)
                        if i == j:
                            continue
                        isFVGValid_1 = isFVGValid(curFVG2.info)
                        if not isFVGValid(curFVG1.info) or not isFVGValid_1:
                            continue
                        if curFVG1.info.isBull != curFVG2.info.isBull:
                            continue
                        __block_result_6__ = na
                        if doFVGsTouch(curFVG1.info, curFVG2.info):
                            curFVG1.info.disabled = True
                            curFVG2.info.disabled = True
                            newFVG: FVG = createFVG(createFVGInfo(math.max(curFVG1.info.max, curFVG2.info.max), math.min(curFVG1.info.min, curFVG2.info.min), curFVG1.info.isBull, math.min(curFVG1.info.t, curFVG2.info.t), 0))
                            newFVG.info.startTime = math.min(curFVG1.info.startTime, curFVG2.info.startTime)
                            newFVG.info.startBarIndex = math.min(curFVG1.info.startBarIndex, curFVG2.info.startBarIndex)
                            newFVG.info.endTime = math.max(nz(curFVG1.info.endTime), nz(curFVG2.info.endTime))
                            newFVG.info.endTime = na if newFVG.info.endTime == 0 else newFVG.info.endTime
                            newFVG.info.endBarIndex = math.max(nz(curFVG1.info.endBarIndex), nz(curFVG2.info.endBarIndex))
                            newFVG.info.endBarIndex = na if newFVG.info.endBarIndex == 0 else newFVG.info.endBarIndex
                            newFVG.info.timeframeStr = curFVG1.info.timeframeStr
                            newFVG.info.extendInfinite = curFVG1.info.extendInfinite or curFVG2.info.extendInfinite
                            newFVG.info.totalVolume = curFVG1.info.totalVolume + curFVG2.info.totalVolume
                            newFVG.info.lowVolume = curFVG1.info.lowVolume + curFVG2.info.lowVolume
                            newFVG.info.highVolume = curFVG1.info.highVolume + curFVG2.info.highVolume
                            newFVG.info.lastTouched = math.max(curFVG1.info.lastTouched, curFVG2.info.lastTouched)
                            newFVG.info.lastTouchedIFVG = math.max(curFVG1.info.lastTouchedIFVG, curFVG2.info.lastTouchedIFVG)
                            newFVG.info.inverseEndIndex = math.max(nz(curFVG1.info.inverseEndIndex), nz(curFVG2.info.inverseEndIndex))
                            newFVG.info.inverseEndIndex = na if newFVG.info.inverseEndIndex == 0 else newFVG.info.inverseEndIndex
                            newFVG.info.inverseEndTime = math.max(nz(curFVG1.info.inverseEndTime), nz(curFVG2.info.inverseEndTime))
                            newFVG.info.inverseEndTime = na if newFVG.info.inverseEndTime == 0 else newFVG.info.inverseEndTime
                            if curFVG1.info.isInverse or curFVG2.info.isInverse:
                                newFVG.info.inverseVolume = nz(curFVG1.info.inverseVolume) + nz(curFVG2.info.inverseVolume)
                                newFVG.info.isInverse = True
                            newFVG.info.combined = True
                            if timeframe.in_seconds(curFVG1.info.timeframeStr) != timeframe.in_seconds(curFVG2.info.timeframeStr):
                                newFVG.info.combinedTimeframesStr = ''
                            array.unshift(allFVGList, newFVG)
                            lastCombinations = lastCombinations + 1
                            __block_result_6__ = lastCombinations
                        __block_result_5__ = __block_result_6__
                    __block_result_4__ = __block_result_5__
                __block_result_3__ = __block_result_4__
            __block_result_2__ = __block_result_3__
        return __block_result_2__

    def handleFVGsFinal():
        newFVGsToAdd: list[FVG] = array.new(0, NA(FVG))
        alertTimeFVG: str = ''
        newBullishFVGAlert: bool = False
        newBearishFVGAlert: bool = False
        alertTimeIFVG: str = ''
        newBullishIFVGAlert: bool = False
        newBearishIFVGAlert: bool = False
        if not na(FVGInfoList):
            if array.size(FVGInfoList) > 0:
                for j in pine_range(0, array.size(FVGInfoList) - 1, 1):
                    newFVG = createFVG(udt_copy(array.get(FVGInfoList, j)))
                    newFVG.info.timeframeStr = ''
                    array.unshift(newFVGsToAdd, newFVG)
        if array.size(newFVGsToAdd) > 0:
            for i in pine_range(0, array.size(newFVGsToAdd) - 1, 1):
                curFVG = array.get(newFVGsToAdd, i)
                if not arrHasFVG(allFVGList, curFVG):
                    alertTimeFVG = curFVG.info.timeframeStr
                    if curFVG.info.isBull:
                        newBullishFVGAlert = True
                    else:
                        newBearishFVGAlert = True
                if curFVG.info.isInverse:
                    if not arrHasIFVG(allFVGList, curFVG):
                        alertTimeIFVG = curFVG.info.timeframeStr
                        if curFVG.info.isBull:
                            newBullishIFVGAlert = True
                        else:
                            newBearishIFVGAlert = True
        if array.size(allFVGList) > 0:
            for i in pine_range(0, array.size(allFVGList) - 1, 1):
                safeDeleteFVG(array.get(allFVGList, i))
        array.clear(allFVGList)
        if array.size(newFVGsToAdd) > 0:
            for i in pine_range(0, array.size(newFVGsToAdd) - 1, 1):
                array.unshift(allFVGList, array.get(newFVGsToAdd, i))
        totalFoundFVGs = array.size(allFVGList)
        if combineFVGs:
            combineFVGsFunc()
        renderedFVGCount: int = 0
        extendedLastXFVGsCount: int = 0
        if array.size(allFVGList) > 0:
            for i in pine_range(0, array.size(allFVGList) - 1, 1):
                curFVG = array.get(allFVGList, i)
                isIFVGValid_1 = isIFVGValid(curFVG.info)
                if not isFVGValid(curFVG.info) and (not isIFVGValid_1):
                    continue
                if extendLastFVGs and na(curFVG.info.endTime) and (extendedLastXFVGsCount < extendLastXFVGsCount):
                    extendedLastXFVGsCount = extendedLastXFVGsCount + 1
                    curFVG.info.extendInfinite = True
                if dbgShowBBFVG:
                    if curFVG.isRendered:
                        safeDeleteFVG(curFVG)
                    renderedFVGCount = renderedFVGCount + 1
                    renderFVG(curFVG, na)
        if DEBUG and False:
            log.info('Rendered ' + string.tostring(renderedFVGCount) + ' / ' + string.tostring(totalFoundFVGs) + ' FVGs.')
        return (alertTimeFVG, newBullishFVGAlert, newBearishFVGAlert, alertTimeIFVG, newBullishIFVGAlert, newBearishIFVGAlert)

    shortVol = ta__ren__.sma(volume, 5)
    longVol = ta__ren__.sma(volume, 15)
    if bar_index > last_bar_index - maxDistanceToLastBar and barstate.isconfirmed:
        bearCondition: bool = False
        bullCondition: bool = False
        shortTerm = shortVol if volCheck else 1
        longTerm = longVol if volCheck else 0
        firstBarSize = math.max(open, close) - math.min(open, close)
        secondBarSize = math.max(open[1], close[1]) - math.min(open[1], close[1])
        thirdBarSize = math.max(open[2], close[2]) - math.min(open[2], close[2])
        barSizeSum = firstBarSize + secondBarSize + thirdBarSize
        barSizeCheck: bool = True
        fvgBarsCheck: bool = False
        if fvgBars == 'Same Type':
            if open > close and open[1] > close[1] and (open[2] > close[2]) or (open <= close and open[1] <= close[1] and (open[2] <= close[2])):
                fvgBarsCheck = True
        else:
            fvgBarsCheck = True
        if fvgBarsCheck and barSizeCheck:
            maxCODiff = math.max(math.abs(close[2] - open[1]), math.abs(close[1] - open))
            if fvgFilterMethod == 'Average Range':
                bearCondition = (not fvgSensEnabled or barSizeSum * fvgSensitivity > atr / 1.5) and (allowGaps or maxCODiff <= atr)
                bullCondition = (not fvgSensEnabled or barSizeSum * fvgSensitivity > atr / 1.5) and (allowGaps or maxCODiff <= atr)
            elif fvgFilterMethod == 'Volume Threshold':
                thresholdMultiplier = volumeThresholdPercent / 100.0
                bearCondition = shortTerm > longTerm * thresholdMultiplier and (allowGaps or maxCODiff <= atr)
                bullCondition = shortTerm > longTerm * thresholdMultiplier and (allowGaps or maxCODiff <= atr)
        bearFVG = high < low[2] and close[1] < low[2] and bearCondition
        bullFVG = low > high[2] and close[1] > high[2] and bullCondition
        volSum3 = math.sum(volume, 3)
        totalVolume: float = volSum3 if volCheck else 0
        newFVGInfo: FVGInfo = createFVGInfo(low[2], high, False, time, totalVolume) if bearFVG else createFVGInfo(low, high[2], True, time, totalVolume) if bullFVG else na
        FVGSize = math.abs(low[2] - high) if bearFVG else math.abs(low - high[2]) if bullFVG else 0
        FVGSizeEnough = FVGSize * fvgSensitivity > atr
        if FVGSizeEnough:
            if not na(newFVGInfo):
                newFVGInfo.startTime = time[2] if startZoneFrom == 'First Bar' else time
                newFVGInfo.startBarIndex = bar_index - (2 if startZoneFrom == 'First Bar' else 0)
                newFVGInfo.lastTouched = bar_index
                if bearFVG:
                    newFVGInfo.lowVolume = volume + volume[1] if volCheck else 0
                    newFVGInfo.highVolume = volume[2] if volCheck else 0
                else:
                    newFVGInfo.lowVolume = volume[2] if volCheck else 0
                    newFVGInfo.highVolume = volume + volume[1] if volCheck else 0
            if not na(newFVGInfo):
                array.unshift(FVGInfoList, newFVGInfo)
                while array.size(FVGInfoList) > showLastXFVGs:
                    array.pop(FVGInfoList)
        if array.size(FVGInfoList) > 0:
            for i in pine_range(0, array.size(FVGInfoList) - 1, 1):
                curFVG = array.get(FVGInfoList, i)
                if curFVG.isBull and low <= curFVG.max or (not curFVG.isBull and high >= curFVG.min):
                    curFVG.lastTouched = bar_index
                if not curFVG.isBull and low <= curFVG.max or (curFVG.isBull and high >= curFVG.min):
                    curFVG.lastTouchedIFVG = bar_index
                if curFVG.isInverse and na(curFVG.inverseEndIndex):
                    if not curFVG.isBull and (low < curFVG.min if ifvgEndMethod == 'Wick' else close < curFVG.min):
                        curFVG.inverseEndIndex = bar_index
                        curFVG.inverseEndTime = time
                    if curFVG.isBull and (high > curFVG.max if ifvgEndMethod == 'Wick' else close > curFVG.max):
                        curFVG.inverseEndIndex = bar_index
                        curFVG.inverseEndTime = time
                if na(curFVG.endBarIndex):
                    if curFVG.isBull and (low < curFVG.min if fvgEndMethod == 'Wick' else close < curFVG.min):
                        curFVG.endBarIndex = bar_index
                        curFVG.endTime = time
                        curFVG.isInverse = True
                        curFVG.inverseVolume = nz(volume)
                        curFVG.lastTouchedIFVG = bar_index
                    if not curFVG.isBull and (high > curFVG.max if fvgEndMethod == 'Wick' else close > curFVG.max):
                        curFVG.endBarIndex = bar_index
                        curFVG.endTime = time
                        curFVG.isInverse = True
                        curFVG.inverseVolume = nz(volume)
                        curFVG.lastTouchedIFVG = bar_index
        FVGInfostoRemove: list[int] = array.new_int(0)
        if array.size(FVGInfoList) > 0:
            for i in pine_range(0, array.size(FVGInfoList) - 1, 1):
                curIndex = array.size(FVGInfoList) - 1 - i
                curFVGInfo = array.get(FVGInfoList, curIndex)
                isFVGValidInTimeframe_1 = isFVGValidInTimeframe(curFVGInfo)
                if not curFVGInfo.isInverse and (not isFVGValidInTimeframe_1):
                    array.push(FVGInfostoRemove, curIndex)
                isIFVGValidInTimeframe_1 = isIFVGValidInTimeframe(curFVGInfo)
                if curFVGInfo.isInverse and (not isIFVGValidInTimeframe_1):
                    array.push(FVGInfostoRemove, curIndex)
        if array.size(FVGInfostoRemove) > 0:
            for i in pine_range(0, array.size(FVGInfostoRemove) - 1, 1):
                deleteIndex = array.get(FVGInfostoRemove, i)
                array.remove(FVGInfoList, deleteIndex)
    orderBlockInfoList: Persistent[list[orderBlockInfo]] = array.new(0, NA(orderBlockInfo))
    allOrderBlocksList: Persistent[list[orderBlock]] = array.new(0, NA(orderBlock))
    def createOrderBlock(orderBlockInfoF: orderBlockInfo):
        newOrderBlock: orderBlock = orderBlock(orderBlockInfoF)
        return newOrderBlock

    def safeDeleteOrderBlock(orderBlockF: orderBlock):
        orderBlockF.isRendered = False
        box.delete(orderBlockF.orderBox)
        box.delete(orderBlockF.breakerBox)
        box.delete(orderBlockF.orderBoxText)
        box.delete(orderBlockF.orderBoxPositive)
        box.delete(orderBlockF.orderBoxNegative)
        line.delete(orderBlockF.orderBoxLineTop)
        line.delete(orderBlockF.orderBoxLineBottom)
        line.delete(orderBlockF.breakerBoxLineTop)
        line.delete(orderBlockF.breakerBoxLineBottom)
        line.delete(orderBlockF.orderSeperator)
        return line.delete(orderBlockF.orderTextSeperator)

    def arrHasOB(arr: list[orderBlock], obF: orderBlock):
        hasOB: bool = False
        if array.size(arr) > 0:
            for i in pine_range(0, array.size(arr) - 1, 1):
                ob1: orderBlock = array.get(arr, i)
                if ob1.info.startTime == obF.info.startTime and ob1.info.breaker == obF.info.breaker:
                    hasOB = True
                    break
        return hasOB

    def renderOrderBlock(ob: orderBlock):
        info__000001d3__: orderBlockInfo = ob.info
        ob.isRendered = True
        orderColor = bullOrderBlockColor if ob.info.obType == 'Bull' else bearOrderBlockColor
        __block_result_7__ = na
        if OBsEnabled and (not breakersFull or not (BBsEnabled and info__000001d3__.breaker)) and (not (not showInvalidated and info__000001d3__.breaker)):
            ob.orderBox = createFVGBox(orderColor, 1.5)
            if ob.info.combined and (not changeCombinedFVGsColor):
                box.set_bgcolor(ob.orderBox, colorWithTransparency(orderColor, 1.1))
            ob.orderBoxText = createFVGBox(color.new(color.white, 100))
            if orderBlockVolumetricInfo:
                ob.orderBoxPositive = createFVGBox(bullOrderBlockColor)
                ob.orderBoxNegative = createFVGBox(bearOrderBlockColor)
                ob.orderSeperator = line.new(na, na, na, na, xloc.bar_time, extend.none, textColor, line.style_dashed, 1)
                ob.orderTextSeperator = line.new(na, na, na, na, xloc.bar_time, extend.none, textColor, line.style_solid, 1)
            zoneSize = (extendZonesByTime if na(info__000001d3__.breakTime) else info__000001d3__.breakTime - curTFMMS * 1000 - info__000001d3__.startTime) if extendZonesDynamic else extendZonesByTime
            if na(info__000001d3__.breakTime):
                zoneSize = time + 1 - info__000001d3__.startTime
            startX = info__000001d3__.startTime if volumeBarsLeftSide else info__000001d3__.startTime + zoneSize - zoneSize / 3
            maxEndX = info__000001d3__.startTime + zoneSize / 3 if volumeBarsLeftSide else info__000001d3__.startTime + zoneSize
            moveBox(ob.orderBox, info__000001d3__.startTime, info__000001d3__.top, info__000001d3__.startTime + zoneSize, info__000001d3__.bottom)
            moveBox(ob.orderBoxText, maxEndX if volumeBarsLeftSide else info__000001d3__.startTime, info__000001d3__.top, info__000001d3__.startTime + zoneSize if volumeBarsLeftSide else startX, info__000001d3__.bottom)
            percentage = cast_int(math.min(info__000001d3__.obHighVolume, info__000001d3__.obLowVolume) / math.max(info__000001d3__.obHighVolume, info__000001d3__.obLowVolume) * 100.0)
            OBText = ('' if na(ob.info.combinedTimeframesStr) else ob.info.combinedTimeframesStr) + ''
            box.set_text(ob.orderBoxText, (string.tostring(ob.info.obVolume, format.volume) + ' (' + string.tostring(percentage) + '%)\n' if orderBlockVolumetricInfo else '') + ('[Combined]\n' if combinedText and ob.info.combined else '') + OBText)
            __block_result_8__ = na
            if orderBlockVolumetricInfo:
                showHighLowBoxText: bool = False
                curEndXHigh = cast_int(math.ceil(info__000001d3__.obHighVolume / info__000001d3__.obVolume * (maxEndX - startX) + startX))
                curEndXLow = cast_int(math.ceil(info__000001d3__.obLowVolume / info__000001d3__.obVolume * (maxEndX - startX) + startX))
                curEndXHigh = nz(curEndXHigh, maxEndX)
                curEndXLow = nz(curEndXLow, maxEndX)
                moveBox(ob.orderBoxPositive, startX if mirrorVolumeBars else curEndXLow, info__000001d3__.top, curEndXHigh if mirrorVolumeBars else maxEndX, (info__000001d3__.bottom + info__000001d3__.top) / 2)
                box.set_text(ob.orderBoxPositive, string.tostring(info__000001d3__.obHighVolume, format.volume) if showHighLowBoxText else '')
                moveBox(ob.orderBoxNegative, startX if mirrorVolumeBars else curEndXHigh, info__000001d3__.bottom, curEndXLow if mirrorVolumeBars else maxEndX, (info__000001d3__.bottom + info__000001d3__.top) / 2)
                box.set_text(ob.orderBoxNegative, string.tostring(info__000001d3__.obLowVolume, format.volume) if showHighLowBoxText else '')
                moveLine(ob.orderSeperator, startX if volumeBarsLeftSide else maxEndX, (info__000001d3__.bottom + info__000001d3__.top) / 2, maxEndX if volumeBarsLeftSide else startX)
                line.set_xy1(ob.orderTextSeperator, maxEndX if volumeBarsLeftSide else startX, info__000001d3__.top)
                __block_result_8__ = line.set_xy2(ob.orderTextSeperator, maxEndX if volumeBarsLeftSide else startX, info__000001d3__.bottom)
            __block_result_7__ = __block_result_8__
        return __block_result_7__

    def handleOrderBlocksFinal():
        if DEBUG and False:
            log.info('Order Block Count ' + string.tostring(array.size(orderBlockInfoList)))
        newBullishOBAlert: bool = False
        newBearishOBAlert: bool = False
        newBullishBBAlert: bool = False
        newBearishBBAlert: bool = False
        alertTimeOB: str = ''
        alertTimeBB: str = ''
        orderBlocksToAdd: list[orderBlock] = array.new(0, NA(orderBlock))
        if not na(orderBlockInfoList):
            if array.size(orderBlockInfoList) > 0:
                for j in pine_range(0, array.size(orderBlockInfoList) - 1, 1):
                    orderBlockInfoF = array.get(orderBlockInfoList, j)
                    orderBlockInfoF.timeframeStr = ''
                    array.unshift(orderBlocksToAdd, createOrderBlock(udt_copy(orderBlockInfoF)))
        if array.size(orderBlocksToAdd) > 0:
            for i in pine_range(0, array.size(orderBlocksToAdd) - 1, 1):
                obToTest = array.get(orderBlocksToAdd, i)
                if obToTest.info.breaker == False:
                    if not arrHasOB(allOrderBlocksList, obToTest):
                        alertTimeOB = obToTest.info.timeframeStr
                        if obToTest.info.obType == 'Bull':
                            newBullishOBAlert = True
                        else:
                            newBearishOBAlert = True
                else:
                    if not arrHasOB(allOrderBlocksList, obToTest):
                        alertTimeBB = obToTest.info.timeframeStr
                        if obToTest.info.obType == 'Bull':
                            newBearishBBAlert = True
                        else:
                            newBullishBBAlert = True
        if array.size(allOrderBlocksList) > 0:
            for i in pine_range(0, array.size(allOrderBlocksList) - 1, 1):
                safeDeleteOrderBlock(array.get(allOrderBlocksList, i))
        array.clear(allOrderBlocksList)
        if array.size(orderBlocksToAdd) > 0:
            for i in pine_range(0, array.size(orderBlocksToAdd) - 1, 1):
                array.unshift(allOrderBlocksList, array.get(orderBlocksToAdd, i))
        if array.size(allOrderBlocksList) > 0:
            for i in pine_range(0, array.size(allOrderBlocksList) - 1, 1):
                curOB = array.get(allOrderBlocksList, i)
                if dbgShowBBFVG:
                    renderOrderBlock(curOB)
        return (alertTimeOB, alertTimeBB, newBullishOBAlert, newBearishOBAlert, newBullishBBAlert, newBearishBBAlert)

    def findOrderBlocks():
        if bar_index > last_bar_index - maxDistanceToLastBar and barstate.isconfirmed and (OBsEnabled or BBsEnabled):
            upper = ta__ren__.highest(swingLength)
            lower = ta__ren__.lowest(swingLength)
            swingType: PersistentSeries[int] = 0
            top: Persistent[obSwing] = obSwing(na, na)
            btm: Persistent[obSwing] = obSwing(na, na)
            li = low[swingLength]
            hi = high[swingLength]
            bi = bar_index[swingLength]
            swingType = 0 if hi > upper else 1 if li < lower else swingType
            if swingType == 0 and swingType[1] != 0:
                top = obSwing(bi, hi)
            if swingType == 1 and swingType[1] != 1:
                btm = obSwing(bi, li)
            boxBtmBull = high[1]
            boxTopBull = low[1]
            boxLocBull = time[1]
            __loop_1__ = pine_loop(1, 1)
            while __loop_1__.step(bar_index - top.x - 1):
                i = __loop_1__.value
                if i > maxBarsBack - 2:
                    break
                boxBtmBull = math.min(low[i], boxBtmBull)
                boxTopBull = high[i] if boxBtmBull == low[i] else boxTopBull
                boxLocBull = time[i] if boxBtmBull == low[i] else boxLocBull
            boxBtmBear = low[1]
            boxTopBear = high[1]
            boxLocBear = time[1]
            __loop_1__ = pine_loop(1, 1)
            while __loop_1__.step(bar_index - btm.x - 1):
                i = __loop_1__.value
                if i > maxBarsBack - 2:
                    break
                boxTopBear = math.max(high[i], boxTopBear)
                boxBtmBear = low[i] if boxTopBear == high[i] else boxBtmBear
                boxLocBear = time[i] if boxTopBear == high[i] else boxLocBear
            obListSize = array.size(orderBlockInfoList)
            if obListSize > 0:
                for i in pine_range(0, obListSize - 1, 1):
                    currentOB = array.get(orderBlockInfoList, i)
                    if currentOB.obType == 'Bull':
                        if not currentOB.breaker:
                            if (low if obEndMethod == 'Wick' else math.min(open, close)) < currentOB.bottom:
                                currentOB.breaker = True
                                currentOB.breakTime = time_close
                                currentOB.bbVolume = volume
                        else:
                            if (high if bbEndMethod == 'Wick' else close) > currentOB.top and na(currentOB.breakerEndTime):
                                currentOB.breakerEndTime = time_close
                    else:
                        if not currentOB.breaker:
                            if (high if obEndMethod == 'Wick' else math.max(open, close)) > currentOB.top:
                                currentOB.breaker = True
                                currentOB.breakTime = time_close
                                currentOB.bbVolume = volume
                        else:
                            if (low if bbEndMethod == 'Wick' else close) < currentOB.bottom and na(currentOB.breakerEndTime):
                                currentOB.breakerEndTime = time_close
            if close > top.y and (not top.crossed):
                top.crossed = True
                obSize = math.abs(boxTopBull - boxBtmBull)
                if obSize <= atr * maxATRMult:
                    newOrderBlockInfo: orderBlockInfo = orderBlockInfo(boxTopBull, boxBtmBull, volume + volume[1] + volume[2], 'Bull', boxLocBull)
                    newOrderBlockInfo.obLowVolume = volume[2]
                    newOrderBlockInfo.obHighVolume = volume + volume[1]
                    array.unshift(orderBlockInfoList, newOrderBlockInfo)
                    if array.size(orderBlockInfoList) > maxOrderBlocks:
                        array.pop(orderBlockInfoList)
            if close < btm.y and (not btm.crossed):
                btm.crossed = True
                obSize = math.abs(boxTopBear - boxBtmBear)
                if obSize <= atr * maxATRMult:
                    newOrderBlockInfo: orderBlockInfo = orderBlockInfo(boxTopBear, boxBtmBear, volume + volume[1] + volume[2], 'Bear', boxLocBear)
                    newOrderBlockInfo.obLowVolume = volume + volume[1]
                    newOrderBlockInfo.obHighVolume = volume[2]
                    array.unshift(orderBlockInfoList, newOrderBlockInfo)
                    if array.size(orderBlockInfoList) > maxOrderBlocks:
                        array.pop(orderBlockInfoList)
        return orderBlockInfoList

    findOrderBlocks()
    if barstate.isconfirmed and bar_index > last_bar_index - maxDistanceToLastBar:
        alertTimeFVG, newBullishFVGAlert, newBearishFVGAlert, alertTimeIFVG, newBullishIFVGAlert, newBearishIFVGAlert = handleFVGsFinal()
        handleOrderBlocksFinal()
    __block_result_9__ = na
    if timeframe.isseconds:
        __block_result_9__ = '1S'
    elif timeframe.isintraday:
        __block_result_9__ = '1'
    elif timeframe.isdaily:
        __block_result_9__ = '5'
    else:
        __block_result_9__ = '60'
    lowerTimeframe: Persistent = __block_result_9__
    if timeframe.in_seconds() <= timeframe.in_seconds(lowerTimeframe):
        runtime.error('CVDS Indicator cannot run on 1-min & 1-second charts.')
    openVolume, maxVolume, minVolume, lastVolume = ta__ren__.requestVolumeDelta(lowerTimeframe, anchorInput)
    curRange = maxVolume - minVolume
    VDATR = ta__ren__.rma(curRange, atrLen)
    col = color.teal if lastVolume >= openVolume else color.red
    cumVol: Persistent[float] = 0.0
    cumVol = cumVol + nz(volume)
    if barstate.islast and cumVol == 0:
        runtime.error("The data vendor doesn't provide volume data for this symbol.")
    if timeframe.in_seconds() > timeframe.in_seconds(anchorInput):
        runtime.error('Anchor period must be higher than current timeframe.')
    lastSignal: Persistent[str] = 'Null'
    bearishSignal: bool = False
    bullishSignal: bool = False
    if signalType == 'Advanced':
        crossunder_1 = ta__ren__.crossunder(lastVolume, 0)
        if close > open and crossunder_1:
            bearishSignal = True
            lastSignal = 'Bear'
        crossover_1 = ta__ren__.crossover(lastVolume, 0)
        if close < open and crossover_1:
            bullishSignal = True
            lastSignal = 'Bull'
    else:
        if ta__ren__.crossunder(lastVolume, 0):
            bearishSignal = True
            lastSignal = 'Bear'
        if ta__ren__.crossover(lastVolume, 0):
            bullishSignal = True
            lastSignal = 'Bull'
    bullLine = high + atr * (curRange / VDATR)
    bearLine = low - atr * (curRange / VDATR)
    cvdsLine = bullLine if lastSignal == 'Bull' else bearLine
    lineCol = highColor if lastSignal == 'Bull' else lowColor
    cvdsLineRMA = ta__ren__.rma(cvdsLine, 3)
    plot(cvdsLineRMA if showCVDSLines else na, 'CVDS Line', lineCol, 1)
    initRun: Persistent[bool] = True
    buyAlertTick: bool = False
    sellAlertTick: bool = False
    tpAlertTick: bool = False
    slAlertTick: bool = False
    def getPosition(positionText):
        __block_result_10__ = na
        if positionText == 'Top Right':
            __block_result_10__ = position.top_right
        elif positionText == 'Top Center':
            __block_result_10__ = position.top_center
        elif positionText == 'Right Center':
            __block_result_10__ = position.middle_right
        elif positionText == 'Left Center':
            __block_result_10__ = position.middle_left
        elif positionText == 'Bottom Center':
            __block_result_10__ = position.bottom_center
        elif positionText == 'Middle Center':
            __block_result_10__ = position.middle_center
        return __block_result_10__

    lineX: Persistent[list[Line]] = array.new_line()
    boxX: Persistent[list[Box]] = array.new_box()
    labelX: Persistent[list[Label]] = array.new_label()
    cvdsList: Persistent[list[CVDS]] = array.new(0, NA(CVDS))
    lastCVDS: Persistent[CVDS] = na(CVDS)
    atrCVDS = nz(ta__ren__.atr(atrLenCVDS), ta__ren__.tr(True))
    def diffPercent(val1: float, val2: float):
        return math.abs(val1 - val2) / val2 * 100.0

    latestFVG: Persistent[FVG] = na(FVG)
    if array.size(allFVGList) > 0:
        latestFVG = array.get(allFVGList, 0)
    latestOB: Persistent[orderBlock] = na(orderBlock)
    if array.size(allOrderBlocksList) > 0:
        latestOB = array.get(allOrderBlocksList, 0)
    if bar_index > last_bar_index - maxDistanceToLastBar and barstate.isconfirmed:
        createNewCVDS: bool = True
        if not na(lastCVDS):
            if na(lastCVDS.exitPrice) and lastCVDS.state != 'Aborted':
                createNewCVDS = False
        if createNewCVDS:
            newCVDS: CVDS = CVDS('Waiting For CVDS', time)
            array.unshift(cvdsList, newCVDS)
            lastCVDS = newCVDS
            log.info('Waiting For CVDS')
        if not na(lastCVDS):
            if na(lastCVDS.entryTime):
                if lastCVDS.overlapDirection == 'Bull' and bearishSignal:
                    lastCVDS.state = 'Aborted'
                    log.info('Aborting')
                if lastCVDS.overlapDirection == 'Bear' and bullishSignal:
                    lastCVDS.state = 'Aborted'
                    log.info('Aborting')
            if lastCVDS.state == 'Waiting For CVDS' and (bullishSignal or bearishSignal):
                lastCVDS.cvdsTime = time
                lastCVDS.cvdsClose = close
                if bearishSignal:
                    lastCVDS.overlapDirection = 'Bear'
                    lastCVDS.breakTime = time
                    if entryMode == 'FVGs':
                        lastCVDS.state = 'Waiting For FVG'
                        log.info('Waiting For Bearish FVG @' + string.tostring(bar_index))
                    else:
                        lastCVDS.state = 'Waiting For OB'
                        log.info('Waiting For Bearish OB @' + string.tostring(bar_index))
                if bullishSignal:
                    lastCVDS.overlapDirection = 'Bull'
                    lastCVDS.breakTime = time
                    if entryMode == 'FVGs':
                        lastCVDS.state = 'Waiting For FVG'
                        log.info('Waiting For Bullish FVG @' + string.tostring(bar_index))
                    else:
                        lastCVDS.state = 'Waiting For OB'
                        log.info('Waiting For Bullish OB @' + string.tostring(bar_index))
            if lastCVDS.state == 'Waiting For OB':
                if lastCVDS.overlapDirection == 'Bear':
                    if not na(latestOB):
                        if latestOB.info.startTime > lastCVDS.breakTime and latestOB.info.obType == 'Bear':
                            lastCVDS.ob = latestOB
                            if not requireRetracement:
                                lastCVDS.state = 'Enter Position'
                            else:
                                lastCVDS.state = 'Waiting For OB Retracement'
                                log.info('Waiting For OB Retracement')
                else:
                    if not na(latestOB):
                        if latestOB.info.startTime > lastCVDS.breakTime and latestOB.info.obType == 'Bull':
                            lastCVDS.ob = latestOB
                            if not requireRetracement:
                                lastCVDS.state = 'Enter Position'
                            else:
                                lastCVDS.state = 'Waiting For OB Retracement'
                                log.info('Waiting For OB Retracement')
            if lastCVDS.state == 'Waiting For FVG':
                if lastCVDS.overlapDirection == 'Bear':
                    if not na(latestFVG):
                        if latestFVG.info.startTime == time and (not latestFVG.info.isBull):
                            lastCVDS.fvg = latestFVG
                            if not requireRetracement:
                                lastCVDS.state = 'Enter Position'
                            else:
                                lastCVDS.state = 'Waiting For FVG Retracement'
                                log.info('Waiting For FVG Retracement')
                else:
                    if not na(latestFVG):
                        if latestFVG.info.startTime == time and latestFVG.info.isBull:
                            lastCVDS.fvg = latestFVG
                            if not requireRetracement:
                                lastCVDS.state = 'Enter Position'
                            else:
                                lastCVDS.state = 'Waiting For FVG Retracement'
                                log.info('Waiting For FVG Retracement')
            if not na(lastCVDS.fvg):
                if na(lastCVDS.fvgEndTime):
                    if lastCVDS.state == 'Waiting For FVG Retracement' and time > lastCVDS.fvg.info.startTime:
                        if lastCVDS.fvg.info.isBull and low <= lastCVDS.fvg.info.max:
                            lastCVDS.state = 'Enter Position'
                        if not lastCVDS.fvg.info.isBull and high >= lastCVDS.fvg.info.min:
                            lastCVDS.state = 'Enter Position'
                    if lastCVDS.fvg.info.isBull and low < lastCVDS.fvg.info.min:
                        lastCVDS.fvgEndTime = time
                    if not lastCVDS.fvg.info.isBull and high > lastCVDS.fvg.info.max:
                        lastCVDS.fvgEndTime = time
            if not na(lastCVDS.ob):
                if na(lastCVDS.ob.info.breakTime):
                    if lastCVDS.state == 'Waiting For OB Retracement' and time > lastCVDS.ob.info.startTime:
                        if lastCVDS.ob.info.obType == 'Bull' and low <= lastCVDS.ob.info.top:
                            lastCVDS.state = 'Enter Position'
                        if lastCVDS.ob.info.obType == 'Bear' and high >= lastCVDS.ob.info.bottom:
                            lastCVDS.state = 'Enter Position'
                    if lastCVDS.ob.info.obType == 'Bull' and low < lastCVDS.ob.info.bottom:
                        lastCVDS.ob.info.breakTime = time
                    if lastCVDS.ob.info.obType == 'Bear' and high > lastCVDS.ob.info.top:
                        lastCVDS.ob.info.breakTime = time
        if not na(lastCVDS):
            if lastCVDS.state == 'Enter Position':
                log.info('Entry Taken')
                lastCVDS.state = 'Entry Taken'
                lastCVDS.entryTime = time
                lastCVDS.entryPrice = close
                if lastCVDS.overlapDirection == 'Bull':
                    lastCVDS.entryType = 'Long'
                    buyAlertTick = True
                    if tpslMethod == 'Fixed':
                        lastCVDS.slTarget = lastCVDS.entryPrice * (1 - slPercent / 100.0)
                        lastCVDS.tpTarget = lastCVDS.entryPrice * (1 + tpPercent / 100.0)
                    elif tpslMethod == 'Dynamic':
                        lastCVDS.slTarget = lastCVDS.entryPrice - atrCVDS * slATRMult
                        log.info(string.tostring(atrCVDS))
                        lastCVDS.tpTarget = lastCVDS.entryPrice + math.abs(lastCVDS.entryPrice - lastCVDS.slTarget) * DynamicRR
                else:
                    lastCVDS.entryType = 'Short'
                    sellAlertTick = True
                    if tpslMethod == 'Fixed':
                        lastCVDS.slTarget = lastCVDS.entryPrice * (1 + slPercent / 100.0)
                        lastCVDS.tpTarget = lastCVDS.entryPrice * (1 - tpPercent / 100.0)
                    elif tpslMethod == 'Dynamic':
                        lastCVDS.slTarget = lastCVDS.entryPrice + atrCVDS * slATRMult
                        lastCVDS.tpTarget = lastCVDS.entryPrice - math.abs(lastCVDS.entryPrice - lastCVDS.slTarget) * DynamicRR
        if not na(lastCVDS):
            if lastCVDS.state == 'Entry Taken' and time > lastCVDS.entryTime:
                if tpslMethod == 'Fixed':
                    if lastCVDS.entryType == 'Long' and (high / lastCVDS.entryPrice - 1) * 100 >= tpPercent:
                        tpAlertTick = True
                        lastCVDS.exitPrice = lastCVDS.entryPrice * (1 + tpPercent / 100.0)
                        lastCVDS.exitTime = time
                        lastCVDS.state = 'Take Profit'
                        if na(lastCVDS.fvgEndTime):
                            lastCVDS.fvgEndTime = time
                        if not na(lastCVDS.ob):
                            if na(lastCVDS.ob.info.breakTime):
                                lastCVDS.ob.info.breakTime = time
                    if lastCVDS.entryType == 'Short' and (low / lastCVDS.entryPrice - 1) * 100 <= -tpPercent:
                        tpAlertTick = True
                        lastCVDS.exitPrice = lastCVDS.entryPrice * (1 - tpPercent / 100.0)
                        lastCVDS.exitTime = time
                        lastCVDS.state = 'Take Profit'
                        if na(lastCVDS.fvgEndTime):
                            lastCVDS.fvgEndTime = time
                        if not na(lastCVDS.ob):
                            if na(lastCVDS.ob.info.breakTime):
                                lastCVDS.ob.info.breakTime = time
                    if lastCVDS.entryType == 'Long' and (low / lastCVDS.entryPrice - 1) * 100 <= -slPercent:
                        slAlertTick = True
                        lastCVDS.exitPrice = lastCVDS.entryPrice * (1 - slPercent / 100.0)
                        lastCVDS.exitTime = time
                        lastCVDS.state = 'Stop Loss'
                        if na(lastCVDS.fvgEndTime):
                            lastCVDS.fvgEndTime = time
                        if not na(lastCVDS.ob):
                            if na(lastCVDS.ob.info.breakTime):
                                lastCVDS.ob.info.breakTime = time
                    if lastCVDS.entryType == 'Short' and (high / lastCVDS.entryPrice - 1) * 100 >= slPercent:
                        slAlertTick = True
                        lastCVDS.exitPrice = lastCVDS.entryPrice * (1 + slPercent / 100.0)
                        lastCVDS.exitTime = time
                        lastCVDS.state = 'Stop Loss'
                        if na(lastCVDS.fvgEndTime):
                            lastCVDS.fvgEndTime = time
                        if not na(lastCVDS.ob):
                            if na(lastCVDS.ob.info.breakTime):
                                lastCVDS.ob.info.breakTime = time
                else:
                    if lastCVDS.entryType == 'Long' and high >= lastCVDS.tpTarget:
                        tpAlertTick = True
                        lastCVDS.exitPrice = lastCVDS.tpTarget
                        lastCVDS.exitTime = time
                        lastCVDS.state = 'Take Profit'
                        if na(lastCVDS.fvgEndTime):
                            lastCVDS.fvgEndTime = time
                        if not na(lastCVDS.ob):
                            if na(lastCVDS.ob.info.breakTime):
                                lastCVDS.ob.info.breakTime = time
                    if lastCVDS.entryType == 'Short' and low <= lastCVDS.tpTarget:
                        tpAlertTick = True
                        lastCVDS.exitPrice = lastCVDS.tpTarget
                        lastCVDS.exitTime = time
                        lastCVDS.state = 'Take Profit'
                        if na(lastCVDS.fvgEndTime):
                            lastCVDS.fvgEndTime = time
                        if not na(lastCVDS.ob):
                            if na(lastCVDS.ob.info.breakTime):
                                lastCVDS.ob.info.breakTime = time
                    if lastCVDS.entryType == 'Long' and low <= lastCVDS.slTarget:
                        slAlertTick = True
                        lastCVDS.exitPrice = lastCVDS.slTarget
                        lastCVDS.exitTime = time
                        lastCVDS.state = 'Stop Loss'
                        if na(lastCVDS.fvgEndTime):
                            lastCVDS.fvgEndTime = time
                        if not na(lastCVDS.ob):
                            if na(lastCVDS.ob.info.breakTime):
                                lastCVDS.ob.info.breakTime = time
                    if lastCVDS.entryType == 'Short' and high >= lastCVDS.slTarget:
                        slAlertTick = True
                        lastCVDS.exitPrice = lastCVDS.slTarget
                        lastCVDS.exitTime = time
                        lastCVDS.state = 'Stop Loss'
                        if na(lastCVDS.fvgEndTime):
                            lastCVDS.fvgEndTime = time
                        if not na(lastCVDS.ob):
                            if na(lastCVDS.ob.info.breakTime):
                                lastCVDS.ob.info.breakTime = time
    renderTopSL: bool = False
    renderBottomSL: bool = False
    renderTopTP: bool = False
    renderBottomTP: bool = False
    if not na(lastCVDS):
        if lastCVDS.state == 'Stop Loss' and time >= lastCVDS.exitTime:
            if lastCVDS.entryType == 'Long':
                renderBottomSL = True
            else:
                renderTopSL = True
            lastCVDS.state = 'Done'
        if lastCVDS.state == 'Take Profit':
            if lastCVDS.entryType == 'Long':
                renderTopTP = True
            else:
                renderBottomTP = True
            lastCVDS.state = 'Done'
    plotshape(renderTopSL, '', shape.circle, location.abovebar, color.red, textcolor=textColor, text='SL', size=size.tiny)
    plotshape(renderBottomSL, '', shape.circle, location.belowbar, color.red, textcolor=textColor, text='SL', size=size.tiny)
    plotshape(renderTopTP, '', shape.xcross, location.abovebar, color.blue, textcolor=textColor, text='TP', size=size.tiny)
    plotshape(renderBottomTP, '', shape.xcross, location.belowbar, color.blue, textcolor=textColor, text='TP', size=size.tiny)
    if barstate.islastconfirmedhistory:
        initRun = False
    alertcondition(buyAlertTick and (not initRun), 'Buy Signal', '')
    alertcondition(sellAlertTick and (not initRun), 'Sell Signal', '')
    alertcondition(tpAlertTick and (not initRun), 'Take-Profit Signal', '')
    alertcondition(slAlertTick and (not initRun), 'Stop-Loss Signal', '')
    if not initRun:
        if buyAlertTick and buyAlertEnabled:
            alert('Buy Signal')
        if sellAlertTick and sellAlertEnabled:
            alert('Sell Signal')
        if tpAlertTick and tpAlertEnabled:
            alert('Take-Profit Signal')
        if slAlertTick and slAlertEnabled:
            alert('Stop-Loss Signal')
    if barstate.islast and backtestDisplayEnabled:
        backtestDisplay: Persistent[Table] = table.new(getPosition(backtestingLocation), 2, 10, bgcolor=screenerColor, frame_width=2, frame_color=color.black, border_width=1, border_color=color.black)
        totalTSProfitPercent: float = 0
        successfulTrades: int = 0
        unsuccessfulTrades: int = 0
        if array.size(cvdsList) > 0:
            for i in pine_range(0, array.size(cvdsList) - 1, 1):
                curCVDS = array.get(cvdsList, i)
                if not na(curCVDS.exitPrice):
                    isSuccess: bool = False
                    if not na(curCVDS.exitPrice):
                        if curCVDS.entryType == 'Long' and curCVDS.exitPrice > curCVDS.entryPrice or (curCVDS.entryType == 'Short' and curCVDS.exitPrice < curCVDS.entryPrice):
                            totalTSProfitPercent = totalTSProfitPercent + math.abs(diffPercent(curCVDS.entryPrice, curCVDS.exitPrice))
                            isSuccess = True
                        else:
                            totalTSProfitPercent = totalTSProfitPercent - math.abs(diffPercent(curCVDS.entryPrice, curCVDS.exitPrice))
                            isSuccess = False
                    if isSuccess:
                        successfulTrades = successfulTrades + 1
                    else:
                        unsuccessfulTrades = unsuccessfulTrades + 1
        table.merge_cells(backtestDisplay, 0, 0, 1, 0)
        table.cell(backtestDisplay, 0, 0, 'CVDS Backtesting', text_color=color.white, bgcolor=screenerColor)
        table.cell(backtestDisplay, 0, 1, 'Total Entries', text_color=color.white, bgcolor=screenerColor)
        table.cell(backtestDisplay, 1, 1, string.tostring(successfulTrades + unsuccessfulTrades), text_color=color.white, bgcolor=screenerColor)
        table.cell(backtestDisplay, 0, 2, 'Wins', text_color=color.white, bgcolor=screenerColor)
        table.cell(backtestDisplay, 1, 2, string.tostring(successfulTrades), text_color=color.white, bgcolor=screenerColor)
        table.cell(backtestDisplay, 0, 3, 'Losses', text_color=color.white, bgcolor=screenerColor)
        table.cell(backtestDisplay, 1, 3, string.tostring(unsuccessfulTrades), text_color=color.white, bgcolor=screenerColor)
        table.cell(backtestDisplay, 0, 4, 'Winrate', text_color=color.white, bgcolor=screenerColor)
        table.cell(backtestDisplay, 1, 4, string.tostring(100.0 * (successfulTrades / (successfulTrades + unsuccessfulTrades)), '#.##') + '%', text_color=color.white, bgcolor=screenerColor)
        table.cell(backtestDisplay, 0, 5, 'Average Profit', text_color=color.white, bgcolor=screenerColor)
        table.cell(backtestDisplay, 1, 5, string.tostring(totalTSProfitPercent / (successfulTrades + unsuccessfulTrades), '#.##') + '%', text_color=color.white, bgcolor=screenerColor)
        table.cell(backtestDisplay, 0, 6, 'Total Profit', text_color=color.white, bgcolor=screenerColor)
        table.cell(backtestDisplay, 1, 6, string.tostring(totalTSProfitPercent, '#.##') + '%', text_color=color.white, bgcolor=screenerColor)
    if barstate.isconfirmed:
        if array.size(lineX) > 0:
            for i in pine_range(0, array.size(lineX) - 1, 1):
                line.delete(array.get(lineX, i))
        if array.size(boxX) > 0:
            for i in pine_range(0, array.size(boxX) - 1, 1):
                box.delete(array.get(boxX, i))
        if array.size(labelX) > 0:
            for i in pine_range(0, array.size(labelX) - 1, 1):
                label.delete(array.get(labelX, i))
        array.clear(lineX)
        array.clear(boxX)
        array.clear(labelX)
        if array.size(cvdsList) > 0:
            __loop_2__ = pine_loop(0, 1)
            while __loop_2__.step(math.min(maxCVDS, array.size(cvdsList) - 1)):
                i = __loop_2__.value
                curTS = array.get(cvdsList, i)
                if not na(curTS.entryTime):
                    if showCVDSLines and False:
                        if curTS.entryType == 'Long':
                            array.push(lineX, line.new(curTS.cvdsTime, curTS.entryPrice, curTS.entryTime, curTS.entryPrice, color=highColor, xloc=xloc.bar_time, width=2, style=line.style_dotted))
                            array.push(lineX, line.new(curTS.cvdsTime, curTS.entryPrice, curTS.cvdsTime, curTS.cvdsClose, color=highColor, xloc=xloc.bar_time, width=2, style=line.style_dotted))
                        else:
                            array.push(lineX, line.new(curTS.cvdsTime, curTS.entryPrice, curTS.entryTime, curTS.entryPrice, color=lowColor, xloc=xloc.bar_time, width=2, style=line.style_dotted))
                            array.push(lineX, line.new(curTS.cvdsTime, curTS.entryPrice, curTS.cvdsTime, curTS.cvdsClose, color=lowColor, xloc=xloc.bar_time, width=2, style=line.style_dotted))
                    if showFVG and (not na(curTS.fvg)):
                        safeDeleteFVG(curTS.fvg)
                        renderFVG(curTS.fvg, math.max(curTS.fvg.info.startTime + timeframe.in_seconds() * 1000 * 5, curTS.fvgEndTime))
                    if showOB and (not na(curTS.ob)):
                        safeDeleteOrderBlock(curTS.ob)
                        renderOrderBlock(curTS.ob)
                    if curTS.entryType == 'Long':
                        array.push(labelX, label.new(curTS.entryTime, close, 'Buy', xloc=xloc.bar_time, yloc=yloc.belowbar, textcolor=color.new(textColor, 0), color=highColor, style=label.style_label_up, size=lblSize))
                    else:
                        array.push(labelX, label.new(curTS.entryTime, close, 'Sell', xloc=xloc.bar_time, yloc=yloc.abovebar, textcolor=color.new(textColor, 0), color=lowColor, style=label.style_label_down, size=lblSize))
                    if showTPSL:
                        if dbgTPSLVersion == 'Alternative':
                            offset = atrCVDS / 3.0
                            endTime = nz(curTS.exitTime, time('', -15))
                            array.push(boxX, box.new(curTS.entryTime, curTS.tpTarget + offset, endTime, curTS.tpTarget - offset, text='TAKE PROFIT (' + string.tostring(curTS.tpTarget, format.mintick) + ')', text_color=textColor, xloc=xloc.bar_time, border_width=0, bgcolor=color.new(highColor, 50), text_size=size.small))
                            array.push(boxX, box.new(curTS.entryTime, curTS.slTarget + offset, endTime, curTS.slTarget - offset, text='STOP LOSS (' + string.tostring(curTS.slTarget, format.mintick) + ')', text_color=textColor, xloc=xloc.bar_time, border_width=0, bgcolor=color.new(lowColor, 50), text_size=size.small))
                        elif dbgTPSLVersion == 'Default':
                            endTime = nz(curTS.exitTime, time('', -15))
                            array.push(lineX, line.new(curTS.entryTime, curTS.entryPrice, curTS.entryTime, curTS.tpTarget, xloc=xloc.bar_time, color=highColor, style=line.style_dashed))
                            array.push(lineX, line.new(curTS.entryTime, curTS.tpTarget, endTime, curTS.tpTarget, xloc=xloc.bar_time, color=highColor, style=line.style_dashed))
                            array.push(labelX, label.new(endTime, curTS.tpTarget, 'TP', xloc=xloc.bar_time, yloc=yloc.price, textcolor=color.new(textColor, 0), color=color.new(highColor, 50), style=label.style_label_left, size=lblSize))
                            array.push(lineX, line.new(curTS.entryTime, curTS.entryPrice, curTS.entryTime, curTS.slTarget, xloc=xloc.bar_time, color=lowColor, style=line.style_dashed))
                            array.push(lineX, line.new(curTS.entryTime, curTS.slTarget, endTime, curTS.slTarget, xloc=xloc.bar_time, color=lowColor, style=line.style_dashed))
                            array.push(labelX, label.new(endTime, curTS.slTarget, 'SL', xloc=xloc.bar_time, yloc=yloc.price, textcolor=color.new(textColor, 0), color=color.new(lowColor, 50), style=label.style_label_left, size=lblSize))
                if not na(curTS.dayEndedBeforeExit):
                    array.push(labelX, label.new(curTS.dayEndedBeforeExit, close, 'Exit', xloc=xloc.bar_time, yloc=yloc.belowbar, textcolor=textColor, color=color.yellow, style=label.style_circle, size=size.tiny))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
