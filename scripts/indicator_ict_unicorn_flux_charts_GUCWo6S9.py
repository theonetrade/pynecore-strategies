"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore import pine_loop, pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_udt import udt, udt_copy
from pynecore.lib import (
    alert, alertcondition, array, bar_index, barstate, box, close, color,
    display, extend, format, high, input, label, last_bar_index, line, location, log, low, math,
    na, nz, open, plotshape, position, script, shape, size, string, ta, table, text, time,
    timeframe, volume, xloc, yloc
)
from pynecore.types import Box, Label, Line, NA, Persistent, PersistentSeries, Series, Table


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
class timeframeInfo:
    index: int = na(int)
    timeframeStr: str = na(str)
    isEnabled: bool = False
    FVGInfoList: 'list[FVGInfo]' = na(list)
    bullishOrderBlocksList: 'list[orderBlockInfo]' = na(list)
    bearishOrderBlocksList: 'list[orderBlockInfo]' = na(list)


@udt
class obSwing:
    x: int = na(int)
    y: float = na(float)
    swingVolume: float = na(float)
    crossed: bool = False


@udt
class Unicorn:
    state: str = na(str)
    startTime: int = na(int)
    overlapDirection: str = na(str)
    retraceTo: float = na(float)
    enterPositionBar: int = na(int)
    fvg: 'FVG' = _dataclass_field(default_factory=lambda: na(FVG))
    OB: 'orderBlock' = _dataclass_field(default_factory=lambda: na(orderBlock))
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
maxDistanceToLastBar: int = 3000
maxOrderBlocks: int = 40
showLastXFVGs: int = 20
extendLastXFVGsCount: int = 20
minimumFVGSize: int = 2
minimumIFVGSize: int = 2
overlapThresholdPercentage: float = 0
atrLen: int = 10
maxUnicorn: int = 75
atrLenUnicorn: int = 50


@script.indicator('ICT Unicorn | Flux Charts', overlay=True, max_boxes_count=maxBoxesCount, max_labels_count=maxBoxesCount, max_lines_count=maxBoxesCount, na_bool=True)
def main(
    fvgSensitivityText=input.string('Normal', 'FVG Detection Sensitivity', options=('Extreme', 'High', 'Normal', 'Low'), group='General Configuration'),
    swingLength=input.int(10, 'Swing Length', minval=3, tooltip='Swing length is used when finding order block formations. Smaller values will result in finding smaller order blocks.', group='General Configuration', display=display.none),
    dbgRequireRetracement=input.bool(False, 'Require Retracement', tooltip='A retracement to the FVG will be required for entry confirmation if enabled.', group='General Configuration'),
    showBB=input.bool(True, 'Show Breaker Blocks', inline='bb', group='General Configuration'),
    showFVG=input.bool(True, 'FVGs', inline='bb', group='General Configuration'),
    __input_5__=input.int(1, '[DBG] Entry Wait Bars', group='General Configuration'),
    __input_6__=input.string('Normal', '[DBG] Label Size', options=('Normal', 'Small', 'Tiny'), group='General Configuration'),
    __input_7__=input.int(100, '[DBG] Unicorn TP / SL Length', group='General Configuration'),
    __input_8__=input.bool(False, '[DBG] Show All BB and FVGs', group='General Configuration'),
    showTPSL=input.bool(True, 'Enabled', group='TP / SL'),
    tpslMethod=input.string('Unicorn', 'TP / SL Method', options=('Unicorn', 'Dynamic', 'Fixed'), group='TP / SL'),
    riskAmount=input.string('Normal', 'Dynamic Risk', options=('Highest', 'High', 'Normal', 'Low', 'Lowest'), group='TP / SL', tooltip='The risk amount when Dynamic TP / SL method is selected.\n\nDifferent assets may have different volatility so changing this setting may result in change of performance of the indicator.'),
    __input_12__=input.float(6.5, '[DBG] Dynamic Custom Risk Mult', group='TP / SL'),
    __input_13__=input.float(4.75, '[DBG] Unicorn SL Offset', group='TP / SL'),
    tpPercent=input.float(0.3, 'Fixed Take Profit %', group='TP / SL'),
    slPercent=input.float(0.4, 'Fixed Stop Loss %', group='TP / SL'),
    backtestDisplayEnabled=input.bool(True, 'Enabled', group='Backtesting Dashboard', display=display.none),
    backtestingLocation=input.string('Top Center', 'Position', options=('Top Right', 'Right Center', 'Top Center'), group='Backtesting Dashboard', display=display.none),
    fillBackgrounds=input.bool(True, 'Fill Backgrounds', group='Backtesting Dashboard', display=display.none),
    screenerColor=input.color(color.new('#1B1F2B'), 'Background', inline='1', group='Backtesting Dashboard', display=display.none),
    __input_20__=input.float(0.57, 'Unicorn Risk:Reward Ratio', group='Debug'),
    __input_21__=input.float(0.86, 'Dynamic Risk:Reward Ratio', group='Debug'),
    buyAlertEnabled=input.bool(True, 'Buy Signal', inline='BS', group='Alerts'),
    sellAlertEnabled=input.bool(True, 'Sell Signal', inline='BS', group='Alerts'),
    tpAlertEnabled=input.bool(True, 'Take-Profit Signal', inline='TS', group='Alerts'),
    slAlertEnabled=input.bool(True, 'Stop-Loss Signal ', inline='TS', group='Alerts'),
    dbgTPSLVersion=input.string('Default', 'TP / SL Layout', options=('Default', 'Alternative'), group='Visuals'),
    bullishBreakerBlockColor=input(color.new(color.new('#2962FF'), 75), 'Bullish Breaker', inline='breakerColor', group='Visuals', display=display.none),
    bearishBreakerBlockColor=input(color.new(color.new('#FFEB3B'), 75), 'Bearish Breaker', inline='breakerColor', group='Visuals', display=display.none),
    highColor=input.color(color.new('#08998180'), 'Buy', inline='colors', group='Visuals'),
    lowColor=input.color(color.new('#F2364680'), 'Sell', inline='colors', group='Visuals'),
    textColor=input.color(color.new('#FFFFFF'), 'Text', inline='colors', group='Visuals'),
    __input_32__=input.bool(True, 'Show Historic Zones', group='General Configuration', display=display.none),
    __input_33__=input.bool(True, 'Enabled', group='Fair Value Gaps', inline='EV', display=display.none),
    __input_34__=input.bool(False, 'Volumetric Info', group='Fair Value Gaps', inline='EV', display=display.none),
    __input_35__=input.string('Close', 'Zone Invalidation', options=('Wick', 'Close'), group='Fair Value Gaps'),
    __input_36__=input.string('Average Range', 'Zone Filtering', options=('Average Range', 'Volume Threshold'), group='Fair Value Gaps'),
    __input_37__=input.int(50, 'Volume Threshold %', group='Fair Value Gaps', tooltip='Only taken into calculation when filter method is Volume Threshold.', minval=1, maxval=200),
    __input_38__=input.string('Same Type', 'FVG Detection', options=('Same Type', 'All'), tooltip='Same Type -> All 3 bars that formed the FVG should be the same type. (Bullish / Bearish) \n\nAll -> Bar types may vary between bullish / bearish.', group='Fair Value Gaps'),
    __input_39__=input.bool(True, '', tooltip='', inline='sens', group='Fair Value Gaps'),
    __input_40__=input(color.new('#08998180'), 'Bullish', inline='fvgColor', group='Fair Value Gaps', display=display.none),
    __input_41__=input(color.new('#F2364680'), 'Bearish', inline='fvgColor', group='Fair Value Gaps', display=display.none),
    __input_42__=input.bool(False, 'Combine Zones', group='Fair Value Gaps'),
    __input_43__=input.bool(False, 'Allow Gaps Between Bars', group='Fair Value Gaps', tooltip='On tickers that can have a different opening price than the previous bar\'s closing price, the indicator will not analyze those bars for FVGs if disabled.\n\nFor Example, if the today\'s opening price is different from the yesterday\'s closing price in a stock ticker.'),
    __input_44__=input.bool(True, '', group='Fair Value Gaps', inline='deleteUntouched'),
    __input_45__=input.int(200, 'Delete Untouched Zones After', group='Fair Value Gaps', minval=5, maxval=200, inline='deleteUntouched'),
    __input_46__=input.bool(False, 'Enabled', inline='EV', group='Inversion Fair Value Gaps'),
    __input_47__=input.bool(False, 'Volumetric Info', group='Inversion Fair Value Gaps', inline='EV', display=display.none),
    __input_48__=input.string('Wick', 'IFVG Zone Invalidation', options=('Wick', 'Close'), group='Inversion Fair Value Gaps'),
    __input_49__=input.bool(True, 'IFVG Full', group='Inversion Fair Value Gaps', display=display.none),
    __input_50__=input(color.new('#08998180'), 'Bullish', inline='breakerColor', group='Inversion Fair Value Gaps', display=display.none),
    __input_51__=input(color.new('#F2364580'), 'Bearish', inline='breakerColor', group='Inversion Fair Value Gaps', display=display.none),
    __input_52__=input.bool(False, 'Enabled', group='Order Blocks', inline='EV', display=display.none),
    __input_53__=input.bool(True, 'Volumetric Info', group='Order Blocks', inline='EV', display=display.none),
    __input_54__=input.string('Close', 'Zone Invalidation', options=('Wick', 'Close'), group='Order Blocks', display=display.none),
    __input_55__=input.bool(False, 'Combine Zones', group='Order Blocks', display=display.none),
    __input_56__=input.string('High', 'Zone Count', options=('High', 'Medium', 'Low'), tooltip='Number of Order & Breaker Block Zones to be rendered. Higher options will result in older Order & Breaker Blocks shown.', group='Order Blocks', display=display.none),
    __input_57__=input(color.new('#08998180'), 'Bullish', inline='obColor', group='Order Blocks', display=display.none),
    __input_58__=input(color.new('#F2364680'), 'Bearish', inline='obColor', group='Order Blocks', display=display.none),
    __input_59__=input.bool(True, 'Enabled', group='Breaker Blocks', inline='EV', display=display.none),
    __input_60__=input.bool(False, 'Volumetric Info', group='Breaker Blocks', inline='EV', display=display.none),
    __input_61__=input.string('Close', 'Zone Invalidation', options=('Wick', 'Close'), group='Breaker Blocks', display=display.none),
    __input_62__=input.bool(True, 'Breakers Full', group='Breaker Blocks', display=display.none),
    __input_63__=input.float(3.5, 'Max ATR Multiplier', group='General Configuration', display=display.none),
    __input_64__=input.int(15, 'Extend Zones', group='Style', minval=1, maxval=30, inline='ExtendZones'),
    __input_65__=input.bool(True, 'Dynamic', group='Style', inline='ExtendZones'),
    __input_66__=input.bool(True, 'Extend Last Zones', group='Style'),
    __input_67__=input.bool(False, 'Change Combined Zones Color', group='Style', inline='CombinedColor'),
    __input_68__=input.bool(False, 'Combined Text', group='Style', inline='CombinedColor'),
    __input_69__=input.color(color.new('#FFF70080'), '' if DEBUG else 'Combined Zone Color', group='Style', inline='CombinedColor'),
    __input_70__=input.string('Last Bar', 'Start FVG Zones From', options=('First Bar', 'Last Bar'), group='Style'),
    __input_71__=input.string('Left', 'Show Volume Bars At', options=('Left', 'Right'), group='Style', inline='volumebars'),
    __input_72__=input.bool(True, 'Mirror Volume Bars', group='Style', inline='volumebars')
):
    entryWaitBars = __input_5__ if DEBUG else 1
    dbgLabelSize = __input_6__ if DEBUG else 'Normal'
    lblSize = size.small if dbgLabelSize == 'Small' else size.normal if dbgLabelSize == 'Normal' else size.tiny
    unicornTPSLLength = __input_7__ if DEBUG else 100
    dbgShowBBFVG = __input_8__ if DEBUG else False
    customSLATRMult = __input_12__ if DEBUG else 6.5
    dbgUnicornSLOffset = __input_13__ if DEBUG else 4.75
    slATRMult = 9.5 if riskAmount == 'Highest' else 6 if riskAmount == 'High' else 5 if riskAmount == 'Normal' else 4 if riskAmount == 'Low' else 1.5 if riskAmount == 'Lowest' else customSLATRMult
    UnicornRR = __input_20__ if DEBUG else 0.57
    DynamicRR = __input_21__ if DEBUG else 0.86
    showInvalidated = __input_32__ if DEBUGOBFVG else True
    fvgEnabled = __input_33__ if DEBUGOBFVG else True
    fvgVolumetricInfo = __input_34__ if DEBUGOBFVG else False
    fvgEndMethod = __input_35__ if DEBUGOBFVG else 'Close'
    fvgFilterMethod = __input_36__ if DEBUGOBFVG else 'Average Range'
    volumeThresholdPercent = __input_37__ if DEBUGOBFVG else 50
    fvgBars = __input_38__ if DEBUGOBFVG else 'Same Type'
    fvgSensEnabled = __input_39__ if DEBUGOBFVG else True
    fvgBullColor = __input_40__ if DEBUGOBFVG else color.new('#08998180')
    fvgBearColor = __input_41__ if DEBUGOBFVG else color.new('#F2364680')
    combineFVGs = __input_42__ if DEBUGOBFVG else False
    allowGaps = __input_43__ if DEBUGOBFVG else False
    deleteUntouched = __input_44__ if DEBUGOBFVG else True
    deleteUntouchedAfterXBars = __input_45__ if DEBUGOBFVG else 200
    ifvgEnabled = __input_46__ if DEBUGOBFVG else False
    ifvgVolumetricInfo = __input_47__ if DEBUGOBFVG else False
    ifvgEndMethod = __input_48__ if DEBUGOBFVG else 'Wick'
    ifvgFull = __input_49__ if DEBUGOBFVG else True
    bullishInverseColor = __input_50__ if DEBUGOBFVG else color.new('#08998180')
    bearishInverseColor = __input_51__ if DEBUGOBFVG else color.new('#F2364580')
    OBsEnabled = __input_52__ if DEBUGOBFVG else False
    orderBlockVolumetricInfo = __input_53__ if DEBUGOBFVG else True
    obEndMethod = __input_54__ if DEBUGOBFVG else 'Close'
    combineOBs = __input_55__ if DEBUGOBFVG else False
    zoneCountOB = __input_56__ if DEBUGOBFVG else 'High'
    bullOrderBlockColor = __input_57__ if DEBUGOBFVG else color.new('#08998180')
    bearOrderBlockColor = __input_58__ if DEBUGOBFVG else color.new('#F2364680')
    BBsEnabled = __input_59__ if DEBUGOBFVG else True
    breakBlockVolumetricInfo = __input_60__ if DEBUGOBFVG else False
    bbEndMethod = __input_61__ if DEBUGOBFVG else 'Close'
    breakersFull = __input_62__ if DEBUGOBFVG else True
    maxATRMult = __input_63__ if DEBUG and DEBUGOBFVG else 3.5
    extendZonesBy = __input_64__ if DEBUG and DEBUGOBFVG else 15
    extendZonesDynamic = __input_65__ if DEBUG and DEBUGOBFVG else True
    extendLastFVGs = __input_66__ if DEBUG and DEBUGOBFVG else True
    changeCombinedFVGsColor = __input_67__ if DEBUG and DEBUGOBFVG else False
    combinedText = __input_68__ if DEBUG and DEBUGOBFVG else False
    combinedColor = __input_69__ if DEBUG and DEBUGOBFVG else color.new('#FFF70080')
    startZoneFrom = __input_70__ if DEBUG and DEBUGOBFVG else 'Last Bar'
    volumeBarsPlace = __input_71__ if DEBUG and DEBUGOBFVG else 'Left'
    mirrorVolumeBars = __input_72__ if DEBUG and DEBUGOBFVG else True
    def createFVGInfo(h, l, bull, t, tv):
        newFVGInfo: FVGInfo = FVGInfo(h, l, bull, t, tv)
        return newFVGInfo

    def createFVG(FVGInfoF: FVGInfo):
        newFVG: FVG = FVG(FVGInfoF)
        return newFVG

    def safeDeleteFVG(fvg: FVG):
        fvg.isRendered = False
        box.delete(fvg.fvgBox)
        box.delete(fvg.ifvgBox)
        box.delete(fvg.fvgBoxText)
        box.delete(fvg.fvgBoxPositive)
        box.delete(fvg.fvgBoxNegative)
        line.delete(fvg.fvgSeperator)
        return line.delete(fvg.fvgTextSeperator)

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

    def newTimeframeInfo(index, timeframeStr, isEnabled):
        newTFInfo: timeframeInfo = timeframeInfo()
        newTFInfo.index = index
        newTFInfo.isEnabled = isEnabled
        newTFInfo.timeframeStr = timeframeStr
        newTFInfo.FVGInfoList = array.new(0, NA(FVGInfo))
        newTFInfo.bullishOrderBlocksList = array.new(0, NA(orderBlockInfo))
        newTFInfo.bearishOrderBlocksList = array.new(0, NA(orderBlockInfo))
        return newTFInfo

    volumeBarsLeftSide = volumeBarsPlace == 'Left'
    fvgSensitivity = 6 if fvgSensitivityText == 'Extreme' else 2 if fvgSensitivityText == 'High' else 1.5 if fvgSensitivityText == 'Normal' else 1
    extendZonesByTime = extendZonesBy * timeframe.in_seconds(timeframe.period) * 1000
    bullishOrderBlocks = 3 if zoneCountOB == 'Low' else 5 if zoneCountOB == 'Medium' else 20
    bearishOrderBlocks = 3 if zoneCountOB == 'Low' else 5 if zoneCountOB == 'Medium' else 20
    atr = ta.atr(atrLen)
    volCheck = ta.cum(volume) > 0
    def moveLine(_line, _x, _y, _x2):
        line.set_xy1(_line, _x, _y)
        return line.set_xy2(_line, _x2, _y)

    def moveBox(_box, _topLeftX, _topLeftY, _bottomRightX, _bottomRightY):
        box.set_lefttop(_box, _topLeftX, _topLeftY)
        return box.set_rightbottom(_box, _bottomRightX, _bottomRightY)

    def isTimeframeLower(timeframe1F, timeframe2F):
        return timeframe.in_seconds(timeframe1F) < timeframe.in_seconds(timeframe2F)

    def getMinTimeframe(timeframe1F, timeframe2F):
        __block_result__ = na
        if isTimeframeLower(timeframe1F, timeframe2F):
            __block_result__ = timeframe1F
        else:
            __block_result__ = timeframe2F
        return __block_result__

    def getMaxTimeframe(timeframe1F, timeframe2F):
        __block_result_1__ = na
        if isTimeframeLower(timeframe1F, timeframe2F):
            __block_result_1__ = timeframe2F
        else:
            __block_result_1__ = timeframe1F
        return __block_result_1__

    def formatTimeframeString(formatTimeframe):
        timeframeF = timeframe.period if formatTimeframe == '' else formatTimeframe
        __block_result_2__ = na
        if string.contains(timeframeF, 'D') or string.contains(timeframeF, 'W') or string.contains(timeframeF, 'S') or string.contains(timeframeF, 'M'):
            __block_result_2__ = timeframeF
        else:
            seconds = timeframe.in_seconds(timeframeF)
            __block_result_3__ = na
            if seconds >= 3600:
                hourCount = cast_int(seconds / 3600)
                __block_result_3__ = string.tostring(hourCount) + ' Hour' + ('s' if hourCount > 1 else '')
            else:
                __block_result_3__ = timeframeF + ' Min'
            __block_result_2__ = __block_result_3__
        return __block_result_2__

    def betterCross(s1: Series, s2):
        ret: str = na(str)
        if s1 >= s2 and s1[1] < s2:
            ret = 'Bull'
        if s1 < s2 and s1[1] >= s2:
            ret = 'Bear'
        return ret

    def colorWithTransparency(colorF, transparencyX):
        return color.new(colorF, color.t(colorF) * transparencyX)

    def createFVGBox(boxColor, transparencyX = 1.0, xlocType = xloc.bar_time):
        return box.new(na, na, na, na, text_size=size.normal, xloc=xlocType, extend=extend.none, bgcolor=colorWithTransparency(boxColor, transparencyX), text_color=textColor, text_halign=text.align_center, border_color=color.new('#00000000'))

    FVGInfoList: Persistent[list[FVGInfo]] = array.new(0, NA(FVGInfo))
    bullishOrderBlocksList: Persistent[list[orderBlockInfo]] = array.new(0, NA(orderBlockInfo))
    bearishOrderBlocksList: Persistent[list[orderBlockInfo]] = array.new(0, NA(orderBlockInfo))
    allOrderBlocksList: Persistent[list[orderBlock]] = array.new(0, NA(orderBlock))
    allFVGList: Persistent[list[FVG]] = array.new(0, NA(FVG))
    def renderOrderBlock(ob: orderBlock, customEndTime: int):
        info__000000cd__: orderBlockInfo = ob.info
        ob.isRendered = True
        orderColor = bullOrderBlockColor if ob.info.obType == 'Bull' else bearOrderBlockColor
        breakerBlockColor = bearishBreakerBlockColor if ob.info.obType == 'Bull' else bullishBreakerBlockColor
        if OBsEnabled and (not breakersFull or not (BBsEnabled and info__000000cd__.breaker)) and (not (not showInvalidated and info__000000cd__.breaker)):
            ob.orderBox = createFVGBox(orderColor, 1.5)
            if ob.info.combined and (not changeCombinedFVGsColor):
                box.set_bgcolor(ob.orderBox, colorWithTransparency(orderColor, 1.1))
            ob.orderBoxText = createFVGBox(color.new(color.white, 100))
            if orderBlockVolumetricInfo:
                ob.orderBoxPositive = createFVGBox(bullOrderBlockColor)
                ob.orderBoxNegative = createFVGBox(bearOrderBlockColor)
                ob.orderSeperator = line.new(na, na, na, na, xloc.bar_time, extend.none, textColor, line.style_dashed, 1)
                ob.orderTextSeperator = line.new(na, na, na, na, xloc.bar_time, extend.none, textColor, line.style_solid, 1)
            zoneSize = (extendZonesByTime if na(info__000000cd__.breakTime) else info__000000cd__.breakTime - info__000000cd__.startTime) if extendZonesDynamic else extendZonesByTime
            if na(info__000000cd__.breakTime):
                zoneSize = time + 1 - info__000000cd__.startTime
            startX = info__000000cd__.startTime if volumeBarsLeftSide else info__000000cd__.startTime + zoneSize - zoneSize / 3
            maxEndX = info__000000cd__.startTime + zoneSize / 3 if volumeBarsLeftSide else info__000000cd__.startTime + zoneSize
            moveBox(ob.orderBox, info__000000cd__.startTime, info__000000cd__.top, info__000000cd__.startTime + zoneSize, info__000000cd__.bottom)
            moveBox(ob.orderBoxText, maxEndX if volumeBarsLeftSide else info__000000cd__.startTime, info__000000cd__.top, info__000000cd__.startTime + zoneSize if volumeBarsLeftSide else startX, info__000000cd__.bottom)
            percentage = cast_int(math.min(info__000000cd__.obHighVolume, info__000000cd__.obLowVolume) / math.max(info__000000cd__.obHighVolume, info__000000cd__.obLowVolume) * 100.0)
            OBText: str = ''
            box.set_text(ob.orderBoxText, (string.tostring(ob.info.obVolume, format.volume) + ' (' + string.tostring(percentage) + '%)\n' if orderBlockVolumetricInfo else '') + ('[Combined]\n' if combinedText and ob.info.combined else '') + OBText)
            if orderBlockVolumetricInfo:
                showHighLowBoxText: bool = False
                curEndXHigh = cast_int(math.ceil(info__000000cd__.obHighVolume / info__000000cd__.obVolume * (maxEndX - startX) + startX))
                curEndXLow = cast_int(math.ceil(info__000000cd__.obLowVolume / info__000000cd__.obVolume * (maxEndX - startX) + startX))
                moveBox(ob.orderBoxPositive, startX if mirrorVolumeBars else curEndXLow, info__000000cd__.top, curEndXHigh if mirrorVolumeBars else maxEndX, (info__000000cd__.bottom + info__000000cd__.top) / 2)
                box.set_text(ob.orderBoxPositive, string.tostring(info__000000cd__.obHighVolume, format.volume) if showHighLowBoxText else '')
                moveBox(ob.orderBoxNegative, startX if mirrorVolumeBars else curEndXHigh, info__000000cd__.bottom, curEndXLow if mirrorVolumeBars else maxEndX, (info__000000cd__.bottom + info__000000cd__.top) / 2)
                box.set_text(ob.orderBoxNegative, string.tostring(info__000000cd__.obLowVolume, format.volume) if showHighLowBoxText else '')
                moveLine(ob.orderSeperator, startX if volumeBarsLeftSide else maxEndX, (info__000000cd__.bottom + info__000000cd__.top) / 2, maxEndX if volumeBarsLeftSide else startX)
                line.set_xy1(ob.orderTextSeperator, maxEndX if volumeBarsLeftSide else startX, info__000000cd__.top)
                line.set_xy2(ob.orderTextSeperator, maxEndX if volumeBarsLeftSide else startX, info__000000cd__.bottom)
        __block_result_4__ = na
        if info__000000cd__.breaker and BBsEnabled:
            startTime = info__000000cd__.breakTime if OBsEnabled and (not breakersFull) else info__000000cd__.startTime
            endTime = time + 1
            if not na(customEndTime):
                endTime = customEndTime
            ob.breakerBox = box.new(startTime, info__000000cd__.top, endTime, info__000000cd__.bottom, na, bgcolor=breakerBlockColor, extend=extend.none, xloc=xloc.bar_time, text_color=textColor, text_size=size.normal)
            BBText: str = ''
            box.set_text(ob.breakerBox, (string.tostring(ob.info.bbVolume, format.volume) + '\n' if breakBlockVolumetricInfo else '') + ('[Combined]\n' if combinedText and ob.info.combined else '') + BBText)
            ob.breakerBoxLineTop = line.new(startTime, info__000000cd__.top, endTime, info__000000cd__.top, xloc.bar_time, extend.none, colorWithTransparency(breakerBlockColor, 0), line.style_dashed)
            ob.breakerBoxLineBottom = line.new(startTime, info__000000cd__.bottom, endTime, info__000000cd__.bottom, xloc.bar_time, extend.none, colorWithTransparency(breakerBlockColor, 0), line.style_dashed)
            __block_result_4__ = ob.breakerBoxLineBottom
        return __block_result_4__

    def findOBSwings(len):
        swingType: PersistentSeries[int] = 0
        top: Persistent[obSwing] = obSwing(na, na)
        bottom: Persistent[obSwing] = obSwing(na, na)
        upper = ta.highest(len)
        lower = ta.lowest(len)
        swingType = 0 if high[len] > upper else 1 if low[len] < lower else swingType
        if swingType == 0 and swingType[1] != 0:
            top = obSwing(bar_index[len], high[len], volume[len])
        if swingType == 1 and swingType[1] != 1:
            bottom = obSwing(bar_index[len], low[len], volume[len])
        return (top, bottom)

    def areaOfOB(OBInfoF: orderBlockInfo):
        XA1: float = OBInfoF.startTime
        XA2: float = time + 1 if na(OBInfoF.breakTime) else OBInfoF.breakTime
        YA1: float = OBInfoF.top
        YA2: float = OBInfoF.bottom
        edge1: float = math.sqrt((XA2 - XA1) * (XA2 - XA1) + (YA2 - YA2) * (YA2 - YA2))
        edge2: float = math.sqrt((XA2 - XA2) * (XA2 - XA2) + (YA2 - YA1) * (YA2 - YA1))
        totalArea: float = edge1 * edge2
        return totalArea

    def areaOfBB(OBInfoF: orderBlockInfo):
        XA1: float = OBInfoF.breakTime
        XA2: float = time + 1
        YA1: float = OBInfoF.top
        YA2: float = OBInfoF.bottom
        edge1: float = math.sqrt((XA2 - XA1) * (XA2 - XA1) + (YA2 - YA2) * (YA2 - YA2))
        edge2: float = math.sqrt((XA2 - XA2) * (XA2 - XA2) + (YA2 - YA1) * (YA2 - YA1))
        totalArea: float = edge1 * edge2
        return totalArea

    def doOBsTouch(OBInfo1: orderBlockInfo, OBInfo2: orderBlockInfo):
        XA1: float = OBInfo1.startTime
        XA2: float = time + 1 if na(OBInfo1.breakTime) else OBInfo1.breakTime
        YA1: float = OBInfo1.top
        YA2: float = OBInfo1.bottom
        XB1: float = OBInfo2.startTime
        XB2: float = time + 1 if na(OBInfo2.breakTime) else OBInfo2.breakTime
        YB1: float = OBInfo2.top
        YB2: float = OBInfo2.bottom
        intersectionArea: float = math.max(0, math.min(XA2, XB2) - math.max(XA1, XB1)) * math.max(0, math.min(YA1, YB1) - math.max(YA2, YB2))
        unionArea: float = areaOfOB(OBInfo1) + areaOfOB(OBInfo2) - intersectionArea
        overlapPercentage: float = intersectionArea / unionArea * 100.0
        __block_result_5__ = na
        if overlapPercentage > overlapThresholdPercentage:
            __block_result_5__ = True
        else:
            __block_result_5__ = False
        return __block_result_5__

    def isOBValid(OBInfo: orderBlockInfo):
        valid: bool = True
        if OBInfo.disabled:
            valid = False
        return valid

    def arrHasOB(arr: list[orderBlock], obF: orderBlock):
        hasOB: bool = False
        if array.size(arr) > 0:
            for i in pine_range(0, array.size(arr) - 1, 1):
                ob1: orderBlock = array.get(arr, i)
                if doOBsTouch(ob1.info, obF.info):
                    hasOB = True
                    break
        return hasOB

    def combineOBsFunc():
        if array.size(allOrderBlocksList) > 0:
            lastCombinations: int = 999
            while lastCombinations > 0:
                lastCombinations = 0
                __loop_2__ = pine_loop(0, 1)
                while __loop_2__.step(array.size(allOrderBlocksList) - 1):
                    i = __loop_2__.value
                    curOB1 = array.get(allOrderBlocksList, i)
                    __loop_3__ = pine_loop(0, 1)
                    while __loop_3__.step(array.size(allOrderBlocksList) - 1):
                        j = __loop_3__.value
                        curOB2 = array.get(allOrderBlocksList, j)
                        if i == j:
                            continue
                        isOBValid_1 = isOBValid(curOB2.info)
                        if not isOBValid(curOB1.info) or not isOBValid_1:
                            continue
                        if curOB1.info.obType != curOB2.info.obType:
                            continue
                        if doOBsTouch(curOB1.info, curOB2.info):
                            curOB1.info.disabled = True
                            curOB2.info.disabled = True
                            newOB: orderBlock = createOrderBlock(orderBlockInfo(math.max(curOB1.info.top, curOB2.info.top), math.min(curOB1.info.bottom, curOB2.info.bottom), curOB1.info.obVolume + curOB2.info.obVolume, curOB1.info.obType))
                            newOB.info.startTime = math.min(curOB1.info.startTime, curOB2.info.startTime)
                            newOB.info.breakTime = math.max(nz(curOB1.info.breakTime), nz(curOB2.info.breakTime))
                            newOB.info.breakTime = na if newOB.info.breakTime == 0 else newOB.info.breakTime
                            newOB.info.timeframeStr = curOB1.info.timeframeStr
                            newOB.info.obVolume = curOB1.info.obVolume + curOB2.info.obVolume
                            newOB.info.obLowVolume = curOB1.info.obLowVolume + curOB2.info.obLowVolume
                            newOB.info.obHighVolume = curOB1.info.obHighVolume + curOB2.info.obHighVolume
                            newOB.info.bbVolume = nz(curOB1.info.bbVolume, 0) + nz(curOB2.info.bbVolume, 0)
                            newOB.info.breaker = curOB1.info.breaker or curOB2.info.breaker
                            newOB.info.combined = True
                            if timeframe.in_seconds(curOB1.info.timeframeStr) != timeframe.in_seconds(curOB2.info.timeframeStr):
                                newOB.info.combinedTimeframesStr = (formatTimeframeString(curOB1.info.timeframeStr) if na(curOB1.info.combinedTimeframesStr) else curOB1.info.combinedTimeframesStr) + ' & ' + (formatTimeframeString(curOB2.info.timeframeStr) if na(curOB2.info.combinedTimeframesStr) else curOB2.info.combinedTimeframesStr)
                            array.unshift(allOrderBlocksList, newOB)
                            lastCombinations = lastCombinations + 1
        return True

    def handleOrderBlocksFinal():
        if DEBUG:
            log.info('Bullish OB Count ' + string.tostring(array.size(bullishOrderBlocksList)))
            log.info('Bearish OB Count ' + string.tostring(array.size(bearishOrderBlocksList)))
        newBullishOBAlert: bool = False
        newBearishOBAlert: bool = False
        newBullishBBAlert: bool = False
        newBearishBBAlert: bool = False
        alertTimeOB: str = ''
        alertTimeBB: str = ''
        orderBlocksToAdd: list[orderBlock] = array.new(0, NA(orderBlock))
        if not na(bullishOrderBlocksList):
            if array.size(bullishOrderBlocksList) > 0:
                __loop_2__ = pine_loop(0, 1)
                while __loop_2__.step(math.min(array.size(bullishOrderBlocksList) - 1, bullishOrderBlocks - 1)):
                    j = __loop_2__.value
                    orderBlockInfoF = array.get(bullishOrderBlocksList, j)
                    orderBlockInfoF.timeframeStr = timeframe.period
                    array.unshift(orderBlocksToAdd, createOrderBlock(udt_copy(orderBlockInfoF)))
        if not na(bearishOrderBlocksList):
            if array.size(bearishOrderBlocksList) > 0:
                __loop_2__ = pine_loop(0, 1)
                while __loop_2__.step(math.min(array.size(bearishOrderBlocksList) - 1, bearishOrderBlocks - 1)):
                    j = __loop_2__.value
                    orderBlockInfoF = array.get(bearishOrderBlocksList, j)
                    orderBlockInfoF.timeframeStr = timeframe.period
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
        if combineOBs:
            combineOBsFunc()
        if array.size(allOrderBlocksList) > 0:
            for i in pine_range(0, array.size(allOrderBlocksList) - 1, 1):
                curOB = array.get(allOrderBlocksList, i)
                if isOBValid(curOB.info) and dbgShowBBFVG:
                    renderOrderBlock(curOB, na)
        return (alertTimeOB, alertTimeBB, newBullishOBAlert, newBearishOBAlert, newBullishBBAlert, newBearishBBAlert)

    top, btm = findOBSwings(swingLength)
    useBody: bool = False
    max: Series = math.max(close, open) if useBody else high
    min: Series = math.min(close, open) if useBody else low
    boxBtmBull = max[1]
    boxTopBull = min[1]
    boxLocBull = time[1]
    __loop_0__ = pine_loop(1, 1)
    while __loop_0__.step(bar_index - top.x - 1):
        i = __loop_0__.value
        boxBtmBull = math.min(min[i], boxBtmBull)
        boxTopBull = max[i] if boxBtmBull == min[i] else boxTopBull
        boxLocBull = time[i] if boxBtmBull == min[i] else boxLocBull
    boxBtmBear = min[1]
    boxTopBear = max[1]
    boxLocBear = time[1]
    __loop_0__ = pine_loop(1, 1)
    while __loop_0__.step(bar_index - btm.x - 1):
        i = __loop_0__.value
        boxTopBear = math.max(max[i], boxTopBear)
        boxBtmBear = min[i] if boxTopBear == max[i] else boxBtmBear
        boxLocBear = time[i] if boxTopBear == max[i] else boxLocBear
    if bar_index > last_bar_index - maxDistanceToLastBar:
        bullishBreaked: int = 0
        if array.size(bullishOrderBlocksList) > 0:
            for i in pine_range(array.size(bullishOrderBlocksList) - 1, 0, 1):
                currentOB = array.get(bullishOrderBlocksList, i)
                if not currentOB.breaker:
                    if (low if obEndMethod == 'Wick' else math.min(open, close)) < currentOB.bottom:
                        currentOB.breaker = True
                        currentOB.breakTime = time
                        currentOB.bbVolume = volume
                else:
                    if (high if bbEndMethod == 'Wick' else close) > currentOB.top:
                        array.remove(bullishOrderBlocksList, i)
                    elif i < bullishOrderBlocks and top.y < currentOB.top and (top.y > currentOB.bottom):
                        bullishBreaked = 1
        if close > top.y and (not top.crossed):
            top.crossed = True
            newOrderBlockInfo: orderBlockInfo = orderBlockInfo(boxTopBull, boxBtmBull, volume + volume[1] + volume[2], 'Bull', boxLocBull)
            newOrderBlockInfo.obLowVolume = volume[2]
            newOrderBlockInfo.obHighVolume = volume + volume[1]
            obSize = math.abs(newOrderBlockInfo.top - newOrderBlockInfo.bottom)
            if obSize <= atr * maxATRMult:
                array.unshift(bullishOrderBlocksList, newOrderBlockInfo)
                if array.size(bullishOrderBlocksList) > maxOrderBlocks:
                    array.pop(bullishOrderBlocksList)
        bearishBreaked: int = 0
        if array.size(bearishOrderBlocksList) > 0:
            for i in pine_range(array.size(bearishOrderBlocksList) - 1, 0, 1):
                currentOB = array.get(bearishOrderBlocksList, i)
                if not currentOB.breaker:
                    if (high if obEndMethod == 'Wick' else math.max(open, close)) > currentOB.top:
                        currentOB.breaker = True
                        currentOB.breakTime = time
                        currentOB.bbVolume = volume
                else:
                    if (low if bbEndMethod == 'Wick' else close) < currentOB.bottom:
                        array.remove(bearishOrderBlocksList, i)
                    elif i < bearishOrderBlocks and btm.y > currentOB.bottom and (btm.y < currentOB.top):
                        bearishBreaked = 1
        if close < btm.y and (not btm.crossed):
            btm.crossed = True
            newOrderBlockInfo: orderBlockInfo = orderBlockInfo(boxTopBear, boxBtmBear, volume + volume[1] + volume[2], 'Bear', boxLocBear)
            newOrderBlockInfo.obLowVolume = volume + volume[1]
            newOrderBlockInfo.obHighVolume = volume[2]
            obSize = math.abs(newOrderBlockInfo.top - newOrderBlockInfo.bottom)
            if obSize <= atr * maxATRMult:
                array.unshift(bearishOrderBlocksList, newOrderBlockInfo)
                if array.size(bearishOrderBlocksList) > maxOrderBlocks:
                    array.pop(bearishOrderBlocksList)
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

    def renderFVG(fvg: FVG, customEndTime: int):
        fvg.isRendered = True
        if fvgEnabled and (not ifvgEnabled or not fvg.info.isInverse) and (showInvalidated or na(fvg.info.endTime)):
            fvg.fvgBox = createFVGBox(combinedColor if fvg.info.combined and changeCombinedFVGsColor else highColor if fvg.info.isBull else lowColor, 1.5)
            fvg.fvgBoxText = createFVGBox(color.new(color.white, 100))
            if fvgVolumetricInfo:
                fvg.fvgBoxPositive = createFVGBox(highColor)
                fvg.fvgBoxNegative = createFVGBox(lowColor)
                fvg.fvgSeperator = line.new(na, na, na, na, xloc.bar_time, extend.none, textColor, line.style_dashed, 1)
                fvg.fvgTextSeperator = line.new(na, na, na, na, xloc.bar_time, extend.none, textColor, line.style_solid, 1)
            zoneSize = (extendZonesByTime if na(fvg.info.endTime) else fvg.info.endTime - fvg.info.startTime) if extendZonesDynamic else extendZonesByTime
            if na(fvg.info.endTime) and fvg.info.extendInfinite:
                zoneSize = time + 1 - fvg.info.startTime
            if not na(customEndTime):
                zoneSize = customEndTime - fvg.info.startTime
            startX = fvg.info.startTime if volumeBarsLeftSide else fvg.info.startTime + zoneSize - zoneSize / 3
            maxEndX = fvg.info.startTime + zoneSize / 3 if volumeBarsLeftSide else fvg.info.startTime + zoneSize
            moveBox(fvg.fvgBox, fvg.info.startTime, fvg.info.max, fvg.info.startTime + zoneSize, fvg.info.min)
            moveBox(fvg.fvgBoxText, maxEndX if volumeBarsLeftSide else fvg.info.startTime, fvg.info.max, fvg.info.startTime + zoneSize if volumeBarsLeftSide else startX, fvg.info.min)
            percentage = cast_int(math.min(fvg.info.highVolume, fvg.info.lowVolume) / math.max(fvg.info.highVolume, fvg.info.lowVolume) * 100.0)
            FVGText: str = ''
            box.set_text(fvg.fvgBoxText, (string.tostring(fvg.info.totalVolume, format.volume) + ' (' + string.tostring(percentage) + '%)\n' if fvgVolumetricInfo else '') + ('[Combined]\n' if combinedText and fvg.info.combined else '') + FVGText)
            if fvg.info.combined and (not changeCombinedFVGsColor):
                box.set_bgcolor(fvg.fvgBox, colorWithTransparency(highColor if fvg.info.isBull else lowColor, 1.1))
            if fvgVolumetricInfo:
                showHighLowBoxText: bool = False
                curEndXHigh = cast_int(math.ceil(fvg.info.highVolume / fvg.info.totalVolume * (maxEndX - startX) + startX))
                curEndXLow = cast_int(math.ceil(fvg.info.lowVolume / fvg.info.totalVolume * (maxEndX - startX) + startX))
                moveBox(fvg.fvgBoxPositive, startX if mirrorVolumeBars else curEndXLow, fvg.info.max, curEndXHigh if mirrorVolumeBars else maxEndX, (fvg.info.min + fvg.info.max) / 2)
                box.set_text(fvg.fvgBoxPositive, string.tostring(fvg.info.highVolume, format.volume) if showHighLowBoxText else '')
                moveBox(fvg.fvgBoxNegative, startX if mirrorVolumeBars else curEndXHigh, fvg.info.min, curEndXLow if mirrorVolumeBars else maxEndX, (fvg.info.min + fvg.info.max) / 2)
                box.set_text(fvg.fvgBoxNegative, string.tostring(fvg.info.lowVolume, format.volume) if showHighLowBoxText else '')
                moveLine(fvg.fvgSeperator, startX if volumeBarsLeftSide else maxEndX, (fvg.info.min + fvg.info.max) / 2, maxEndX if volumeBarsLeftSide else startX)
                line.set_xy1(fvg.fvgTextSeperator, maxEndX if volumeBarsLeftSide else startX, fvg.info.max)
                line.set_xy2(fvg.fvgTextSeperator, maxEndX if volumeBarsLeftSide else startX, fvg.info.min)
        __block_result_6__ = na
        if fvg.info.isInverse and ifvgEnabled:
            inverseColor = bearishInverseColor if fvg.info.isBull else bullishInverseColor
            fvg.ifvgBox = createFVGBox(inverseColor)
            startTimeIFVG = fvg.info.startTime if ifvgFull else fvg.info.endTime
            inverseZoneSize = time + 1 - startTimeIFVG if na(fvg.info.inverseEndTime) else fvg.info.inverseEndTime - startTimeIFVG
            moveBox(fvg.ifvgBox, startTimeIFVG, fvg.info.max, startTimeIFVG + inverseZoneSize, fvg.info.min)
            IFVGText = (formatTimeframeString(fvg.info.timeframeStr) if na(fvg.info.combinedTimeframesStr) else fvg.info.combinedTimeframesStr) + ' IFVG'
            __block_result_6__ = box.set_text(fvg.ifvgBox, (string.tostring(fvg.info.inverseVolume, format.volume) + '\n' if ifvgVolumetricInfo else '') + ('[Combined]\n' if combinedText and fvg.info.combined else '') + IFVGText)
        return __block_result_6__

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
        __block_result_7__ = na
        if overlapPercentage > overlapThresholdPercentage:
            __block_result_7__ = True
        else:
            __block_result_7__ = False
        return __block_result_7__

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
        __block_result_8__ = na
        if array.size(allFVGList) > 0:
            lastCombinations: int = 999
            __block_result_9__ = na
            while lastCombinations > 0:
                lastCombinations = 0
                __block_result_10__ = na
                __loop_2__ = pine_loop(0, 1)
                while __loop_2__.step(array.size(allFVGList) - 1):
                    i = __loop_2__.value
                    curFVG1 = array.get(allFVGList, i)
                    __block_result_11__ = na
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
                        __block_result_12__ = na
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
                                newFVG.info.combinedTimeframesStr = (formatTimeframeString(curFVG1.info.timeframeStr) if na(curFVG1.info.combinedTimeframesStr) else curFVG1.info.combinedTimeframesStr) + ' & ' + (formatTimeframeString(curFVG2.info.timeframeStr) if na(curFVG2.info.combinedTimeframesStr) else curFVG2.info.combinedTimeframesStr)
                            array.unshift(allFVGList, newFVG)
                            lastCombinations = lastCombinations + 1
                            __block_result_12__ = lastCombinations
                        __block_result_11__ = __block_result_12__
                    __block_result_10__ = __block_result_11__
                __block_result_9__ = __block_result_10__
            __block_result_8__ = __block_result_9__
        return __block_result_8__

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
                    newFVG.info.timeframeStr = timeframe.period
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
        if DEBUG:
            log.info('Rendered ' + string.tostring(renderedFVGCount) + ' / ' + string.tostring(totalFoundFVGs) + ' FVGs.')
        return (alertTimeFVG, newBullishFVGAlert, newBearishFVGAlert, alertTimeIFVG, newBullishIFVGAlert, newBearishIFVGAlert)

    shortVol = ta.sma(volume, 5)
    longVol = ta.sma(volume, 15)
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
    if barstate.isconfirmed and bar_index > last_bar_index - maxDistanceToLastBar:
        alertTimeFVG, newBullishFVGAlert, newBearishFVGAlert, alertTimeIFVG, newBullishIFVGAlert, newBearishIFVGAlert = handleFVGsFinal()
        if OBsEnabled or BBsEnabled:
            handleOrderBlocksFinal()
    def doBBFVGTouch(OBInfoX: orderBlockInfo, FVGInfoX: FVGInfo):
        __block_result_13__ = na
        if OBInfoX.breaker:
            XA1: float = OBInfoX.breakTime
            XA2: float = time + 1
            YA1: float = OBInfoX.top
            YA2: float = OBInfoX.bottom
            XB1: float = FVGInfoX.startTime
            XB2: float = time + 1 if na(FVGInfoX.endTime) else FVGInfoX.endTime
            YB1: float = FVGInfoX.max
            YB2: float = FVGInfoX.min
            intersectionArea: float = math.max(0, math.min(XA2, XB2) - math.max(XA1, XB1)) * math.max(0, math.min(YA1, YB1) - math.max(YA2, YB2))
            unionArea: float = areaOfBB(OBInfoX) + areaOfFVG(FVGInfoX) - intersectionArea
            overlapPercentage: float = intersectionArea / unionArea * 100.0
            __block_result_14__ = na
            if overlapPercentage > overlapThresholdPercentage:
                __block_result_14__ = True
            else:
                __block_result_14__ = False
            __block_result_13__ = __block_result_14__
        else:
            __block_result_13__ = False
        return __block_result_13__

    initRun: Persistent[bool] = True
    buyAlertTick: bool = False
    sellAlertTick: bool = False
    tpAlertTick: bool = False
    slAlertTick: bool = False
    def getPosition(positionText):
        __block_result_15__ = na
        if positionText == 'Top Right':
            __block_result_15__ = position.top_right
        elif positionText == 'Top Center':
            __block_result_15__ = position.top_center
        elif positionText == 'Right Center':
            __block_result_15__ = position.middle_right
        elif positionText == 'Left Center':
            __block_result_15__ = position.middle_left
        elif positionText == 'Bottom Center':
            __block_result_15__ = position.bottom_center
        elif positionText == 'Middle Center':
            __block_result_15__ = position.middle_center
        return __block_result_15__

    lineX: Persistent[list[Line]] = array.new_line()
    boxX: Persistent[list[Box]] = array.new_box()
    labelX: Persistent[list[Label]] = array.new_label()
    unicornList: Persistent[list[Unicorn]] = array.new(0, NA(Unicorn))
    lastUnicorn: Persistent[Unicorn] = na(Unicorn)
    atrUnicorn = ta.atr(atrLenUnicorn)
    def diffPercent(val1: float, val2: float):
        return math.abs(val1 - val2) / val2 * 100.0

    highUnicornTPSL = ta.highest(unicornTPSLLength)
    lowUnicornTPSL = ta.lowest(unicornTPSLLength)
    if bar_index > last_bar_index - maxDistanceToLastBar and barstate.isconfirmed:
        if True:
            createNewUnicorn: bool = True
            if not na(lastUnicorn):
                if na(lastUnicorn.exitPrice):
                    createNewUnicorn = False
            if createNewUnicorn:
                newUnicorn: Unicorn = Unicorn('Waiting For FVG-BB Overlap', time)
                array.unshift(unicornList, newUnicorn)
                lastUnicorn = newUnicorn
                log.info('New Unicorn')
            if not na(lastUnicorn):
                if lastUnicorn.state == 'Waiting For FVG-BB Overlap':
                    if array.size(allFVGList) > 0:
                        for i in pine_range(0, array.size(allFVGList) - 1, 1):
                            curFVG = array.get(allFVGList, i)
                            if array.size(allOrderBlocksList) > 0:
                                for j in pine_range(0, array.size(allOrderBlocksList) - 1, 1):
                                    curOB = array.get(allOrderBlocksList, j)
                                    if curOB.info.breaker:
                                        if curOB.info.obType == 'Bear' and curFVG.info.isBull or (curOB.info.obType == 'Bull' and (not curFVG.info.isBull)):
                                            if doBBFVGTouch(curOB.info, curFVG.info) and (time == curFVG.info.startTime or time == curOB.info.breakTime):
                                                lastUnicorn.state = 'FVG-BB Overlap'
                                                lastUnicorn.overlapDirection = 'Bull' if curFVG.info.isBull else 'Bear'
                                                lastUnicorn.retraceTo = curFVG.info.max if curFVG.info.isBull else curFVG.info.min
                                                lastUnicorn.fvg = curFVG
                                                lastUnicorn.OB = curOB
                if lastUnicorn.state == 'FVG-BB Overlap':
                    if not dbgRequireRetracement:
                        lastUnicorn.state = 'Enter Position'
                        lastUnicorn.enterPositionBar = bar_index
                    else:
                        lastUnicorn.state = 'Require Retracement'
        if not na(lastUnicorn):
            if lastUnicorn.state == 'Require Retracement':
                if lastUnicorn.overlapDirection == 'Bull' and low < lastUnicorn.retraceTo:
                    lastUnicorn.state = 'Enter Position'
                    lastUnicorn.enterPositionBar = bar_index
                if lastUnicorn.overlapDirection == 'Bear' and high > lastUnicorn.retraceTo:
                    lastUnicorn.state = 'Enter Position'
                    lastUnicorn.enterPositionBar = bar_index
        if not na(lastUnicorn):
            if lastUnicorn.state == 'Enter Position' and bar_index >= lastUnicorn.enterPositionBar + entryWaitBars:
                lastUnicorn.state = 'Entry Taken'
                lastUnicorn.entryTime = time
                lastUnicorn.entryPrice = close
                if lastUnicorn.overlapDirection == 'Bull':
                    lastUnicorn.entryType = 'Long'
                    buyAlertTick = True
                    if tpslMethod == 'Fixed':
                        lastUnicorn.slTarget = lastUnicorn.entryPrice * (1 - slPercent / 100.0)
                        lastUnicorn.tpTarget = lastUnicorn.entryPrice * (1 + tpPercent / 100.0)
                    elif tpslMethod == 'Dynamic':
                        lastUnicorn.slTarget = lastUnicorn.entryPrice - atrUnicorn * slATRMult
                        lastUnicorn.tpTarget = lastUnicorn.entryPrice + math.abs(lastUnicorn.entryPrice - lastUnicorn.slTarget) * DynamicRR
                    else:
                        lastUnicorn.slTarget = lowUnicornTPSL - atrUnicorn * dbgUnicornSLOffset
                        lastUnicorn.tpTarget = lastUnicorn.entryPrice + math.abs(lastUnicorn.entryPrice - lastUnicorn.slTarget) * UnicornRR
                else:
                    lastUnicorn.entryType = 'Short'
                    sellAlertTick = True
                    if tpslMethod == 'Fixed':
                        lastUnicorn.slTarget = lastUnicorn.entryPrice * (1 + slPercent / 100.0)
                        lastUnicorn.tpTarget = lastUnicorn.entryPrice * (1 - tpPercent / 100.0)
                    elif tpslMethod == 'Dynamic':
                        lastUnicorn.slTarget = lastUnicorn.entryPrice + atrUnicorn * slATRMult
                        lastUnicorn.tpTarget = lastUnicorn.entryPrice - math.abs(lastUnicorn.entryPrice - lastUnicorn.slTarget) * DynamicRR
                    else:
                        lastUnicorn.slTarget = highUnicornTPSL + atrUnicorn * dbgUnicornSLOffset
                        lastUnicorn.tpTarget = lastUnicorn.entryPrice - math.abs(lastUnicorn.entryPrice - lastUnicorn.slTarget) * UnicornRR
        if not na(lastUnicorn):
            if lastUnicorn.state == 'Entry Taken' and time > lastUnicorn.entryTime:
                log.info('Entry Taken')
                if tpslMethod == 'Fixed':
                    if lastUnicorn.entryType == 'Long' and (high / lastUnicorn.entryPrice - 1) * 100 >= tpPercent:
                        tpAlertTick = True
                        lastUnicorn.exitPrice = lastUnicorn.entryPrice * (1 + tpPercent / 100.0)
                        lastUnicorn.exitTime = time
                        lastUnicorn.state = 'Take Profit'
                    if lastUnicorn.entryType == 'Short' and (low / lastUnicorn.entryPrice - 1) * 100 <= -tpPercent:
                        tpAlertTick = True
                        lastUnicorn.exitPrice = lastUnicorn.entryPrice * (1 - tpPercent / 100.0)
                        lastUnicorn.exitTime = time
                        lastUnicorn.state = 'Take Profit'
                    if lastUnicorn.entryType == 'Long' and (low / lastUnicorn.entryPrice - 1) * 100 <= -slPercent:
                        slAlertTick = True
                        lastUnicorn.exitPrice = lastUnicorn.entryPrice * (1 - slPercent / 100.0)
                        lastUnicorn.exitTime = time
                        lastUnicorn.state = 'Stop Loss'
                    if lastUnicorn.entryType == 'Short' and (high / lastUnicorn.entryPrice - 1) * 100 >= slPercent:
                        slAlertTick = True
                        lastUnicorn.exitPrice = lastUnicorn.entryPrice * (1 + slPercent / 100.0)
                        lastUnicorn.exitTime = time
                        lastUnicorn.state = 'Stop Loss'
                else:
                    if lastUnicorn.entryType == 'Long' and high >= lastUnicorn.tpTarget:
                        tpAlertTick = True
                        lastUnicorn.exitPrice = lastUnicorn.tpTarget
                        lastUnicorn.exitTime = time
                        lastUnicorn.state = 'Take Profit'
                    if lastUnicorn.entryType == 'Short' and low <= lastUnicorn.tpTarget:
                        tpAlertTick = True
                        lastUnicorn.exitPrice = lastUnicorn.tpTarget
                        lastUnicorn.exitTime = time
                        lastUnicorn.state = 'Take Profit'
                    if lastUnicorn.entryType == 'Long' and low <= lastUnicorn.slTarget:
                        slAlertTick = True
                        lastUnicorn.exitPrice = lastUnicorn.slTarget
                        lastUnicorn.exitTime = time
                        lastUnicorn.state = 'Stop Loss'
                    if lastUnicorn.entryType == 'Short' and high >= lastUnicorn.slTarget:
                        slAlertTick = True
                        lastUnicorn.exitPrice = lastUnicorn.slTarget
                        lastUnicorn.exitTime = time
                        lastUnicorn.state = 'Stop Loss'
    renderTopSL: bool = False
    renderBottomSL: bool = False
    renderTopTP: bool = False
    renderBottomTP: bool = False
    if not na(lastUnicorn):
        if lastUnicorn.state == 'Stop Loss' and time >= lastUnicorn.exitTime:
            if lastUnicorn.entryType == 'Long':
                renderBottomSL = True
            else:
                renderTopSL = True
            lastUnicorn.state = 'Done'
        if lastUnicorn.state == 'Take Profit':
            if lastUnicorn.entryType == 'Long':
                renderTopTP = True
            else:
                renderBottomTP = True
            lastUnicorn.state = 'Done'
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
        if array.size(unicornList) > 0:
            for i in pine_range(0, array.size(unicornList) - 1, 1):
                curUnicorn = array.get(unicornList, i)
                if not na(curUnicorn.entryPrice):
                    isSuccess: bool = False
                    if not na(curUnicorn.exitPrice):
                        if curUnicorn.entryType == 'Long' and curUnicorn.exitPrice > curUnicorn.entryPrice or (curUnicorn.entryType == 'Short' and curUnicorn.exitPrice < curUnicorn.entryPrice):
                            totalTSProfitPercent = totalTSProfitPercent + math.abs(diffPercent(curUnicorn.entryPrice, curUnicorn.exitPrice))
                            isSuccess = True
                        else:
                            totalTSProfitPercent = totalTSProfitPercent - math.abs(diffPercent(curUnicorn.entryPrice, curUnicorn.exitPrice))
                            isSuccess = False
                    if isSuccess:
                        successfulTrades = successfulTrades + 1
                    else:
                        unsuccessfulTrades = unsuccessfulTrades + 1
        table.merge_cells(backtestDisplay, 0, 0, 1, 0)
        table.cell(backtestDisplay, 0, 0, 'Unicorn Backtesting', text_color=color.white, bgcolor=screenerColor)
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
        if array.size(unicornList) > 0:
            __loop_2__ = pine_loop(0, 1)
            while __loop_2__.step(math.min(maxUnicorn, array.size(unicornList) - 1)):
                i = __loop_2__.value
                curTS = array.get(unicornList, i)
                if not na(curTS.entryTime):
                    if showBB:
                        safeDeleteOrderBlock(curTS.OB)
                        renderOrderBlock(curTS.OB, curTS.entryTime)
                    if showFVG:
                        safeDeleteFVG(curTS.fvg)
                        renderFVG(curTS.fvg, curTS.entryTime)
                    if curTS.entryType == 'Long':
                        array.push(labelX, label.new(curTS.entryTime, close, 'Buy', xloc=xloc.bar_time, yloc=yloc.belowbar, textcolor=color.new(textColor, 0), color=highColor, style=label.style_label_up, size=lblSize))
                    else:
                        array.push(labelX, label.new(curTS.entryTime, close, 'Sell', xloc=xloc.bar_time, yloc=yloc.abovebar, textcolor=color.new(textColor, 0), color=lowColor, style=label.style_label_down, size=lblSize))
                    if showTPSL:
                        if dbgTPSLVersion == 'Alternative':
                            offset = atrUnicorn / 3.0
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
