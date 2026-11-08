"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, barstate, close, color,
    display, fill, high, hl2, hlc3, hlcc4, input, label, low, math, na, ohlc4, open, plot,
    position, script, size, string, ta, table, text, timeframe, volume, xloc
)
from pynecore.types import Persistent, PersistentSeries, Series

groupFair1: str = 'Fair value basis & bands'
groupCross: str = 'Crosses'
groupVisual: str = 'Visuals'
groupTable: str = 'Table'


@script.indicator('Fair value bands / Flowly Indicators', overlay=True, max_labels_count=500, max_lines_count=500)
def main(
    i_btCheck=input.bool(False, 'Highlight metric calculations', group=groupFair1, tooltip='Enables lot based coloring and time/volume distribution counters, found in Data Window tab.'),
    i_boost=input.float(1, 'Threshold band width', group=groupFair1, step=0.1, minval=0),
    i_bandBoost=input.float(1, 'Deviation band width', group=groupFair1, step=0.1, minval=0),
    i_anchorTf=input.timeframe('1D', 'VWAP anchor', group=groupFair1, tooltip='Timeframe to which VWAP is anchored to. Choose VWAP from fair value basis menu to activate.'),
    i_sourceString=input.string('OHLC4', '', options=('OHLC4', 'Open', 'High', 'Low', 'Close', 'HL2', 'HLC3', 'HLCC4'), inline='source', group=groupFair1),
    i_smoothingType=input.string('SMA', '', options=('SMA', 'EMA', 'HMA', 'RMA', 'WMA', 'VWMA', 'Median', 'VWAP'), inline='source', group=groupFair1),
    i_length=input.int(20, '', inline='source', group=groupFair1, minval=1),
    i_trendMode=input.string('Cross', '', options=('Cross', 'Direction'), inline='sourcecross', group=groupFair1),
    i_thresholdUpString=input.string('Low', '▲', options=('OHLC4', 'Open', 'High', 'Low', 'Close', 'HL2', 'HLC3', 'HLCC4'), inline='sourcecross', group=groupFair1),
    i_thresholdDownString=input.string('High', '▼', options=('OHLC4', 'Open', 'High', 'Low', 'Close', 'HL2', 'HLC3', 'HLCC4'), inline='sourcecross', group=groupFair1),
    i_crossSrc1: Series[float] = input.source(high, 'Cross', group=groupCross, inline='ucross1'),
    i_crossMethod1=input.string('Above', '', options=('Above', 'Below'), inline='ucross1', group=groupCross),
    i_crossRef1=input.string('+2', '', options=('Off', '+1', '+2', '+3', '-1', '-2', '-3'), inline='ucross1', group=groupCross),
    i_crossSrc2: Series[float] = input.source(low, 'Cross', group=groupCross, inline='ucross2'),
    i_crossMethod2=input.string('Below', '', options=('Above', 'Below'), inline='ucross2', group=groupCross),
    i_crossRef2=input.string('-2', '', options=('Off', '+1', '+2', '+3', '-1', '-2', '-3'), inline='ucross2', group=groupCross),
    i_crossSrc3: Series[float] = input.source(close, 'Cross', group=groupCross, inline='ucross3'),
    i_crossMethod3=input.string('Above', '', options=('Above', 'Below'), inline='ucross3', group=groupCross),
    i_crossRef3=input.string('Off', '', options=('Off', '+1', '+2', '+3', '-1', '-2', '-3'), inline='ucross3', group=groupCross),
    i_crossSrc4: Series[float] = input.source(close, 'Cross', group=groupCross, inline='ucross4'),
    i_crossMethod4=input.string('Above', '', options=('Above', 'Below'), inline='ucross4', group=groupCross),
    i_crossRef4=input.string('Off', '', options=('Off', '+1', '+2', '+3', '-1', '-2', '-3'), inline='ucross4', group=groupCross),
    i_crossAboveCol=input.color(color.blue, 'Above', group=groupCross, inline='crosses'),
    i_crossBelowCol=input.color(color.fuchsia, 'Below', group=groupCross, inline='crosses'),
    i_upColorLine=input.color(color.new(color.white, 50), 'Fair value basis ▲ / ▼', group=groupVisual, inline='line'),
    i_downColorLine=input.color(color.new(color.red, 50), '', group=groupVisual, inline='line'),
    i_upColorFill=input.color(color.new(color.white, 97), 'Threshold band ▲ / ▼', group=groupVisual, inline='fill'),
    i_downColorFill=input.color(color.new(color.red, 97), '', group=groupVisual, inline='fill'),
    extremeDeviationUp=input.color(color.new(color.red, 10), 'Deviation hue ▲ / ▼', group=groupVisual, inline='deviation'),
    extremeDeviationDown=input.color(color.new(color.new('#3C699E'), 10), '', group=groupVisual, inline='deviation'),
    extremeUpColor=input.color(color.new(color.red, 90), 'Deviation bands extreme ▲ / ▼', group=groupVisual, inline='band'),
    extremeDownColor=input.color(color.new(color.new('#205497'), 90), '', group=groupVisual, inline='band'),
    deviationBandColor=input.color(color.new(color.white, 95), 'Deviation bands', group=groupVisual, inline='dev'),
    tablePos=input.string('Top right', 'Table position', options=('Top right', 'Bottom right', 'Bottom left', 'Top left'), group=groupTable),
    tableSize=input.int(3, 'Table size', maxval=5, minval=1, group=groupTable)
):
    def stringSrc(source):
        src = open if source == 'Open' else high if source == 'High' else low if source == 'Low' else close if source == 'Close' else hl2 if source == 'HL2' else hlc3 if source == 'HLC3' else hlcc4 if source == 'HLC44' else ohlc4
        return src

    i_source = stringSrc(i_sourceString)
    i_thresholdUpSrc = stringSrc(i_thresholdUpString)
    i_thresholdDownSrc = stringSrc(i_thresholdDownString)
    anchor = timeframe.change(i_anchorTf)
    def smoothedValue(source, length):
        return ta.sma(source, length) if i_smoothingType == 'SMA' else ta.ema(source, length) if i_smoothingType == 'EMA' else ta.hma(source, length) if i_smoothingType == 'HMA' else ta.rma(source, length) if i_smoothingType == 'RMA' else ta.vwma(source, length) if i_smoothingType == 'VWMA' else ta.median(source, length) if i_smoothingType == 'Median' else ta.vwap(source, anchor) if i_smoothingType == 'VWAP' else ta.wma(source, length)

    fairPriceSmooth: Series = smoothedValue(i_source, i_length)
    lowSpread = low / fairPriceSmooth
    highSpread = high / fairPriceSmooth
    deviationDown = lowSpread if low < fairPriceSmooth and high > fairPriceSmooth else na
    deviationUp = highSpread if low < fairPriceSmooth and high > fairPriceSmooth else na
    deviationUpList: Persistent[list[float]] = array.new_float(0, 0)
    deviationDownList: Persistent[list[float]] = array.new_float(0, 0)
    deviationUpSize = array.size(deviationUpList)
    deviationDownSize = array.size(deviationDownList)
    sizeLimitDev: int = 1000
    if deviationUpSize > sizeLimitDev:
        array.remove(deviationUpList, 0)
    if deviationDownSize > sizeLimitDev:
        array.remove(deviationDownList, 0)
    array.push(deviationUpList, deviationUp)
    array.push(deviationDownList, deviationDown)
    medianUpDeviation = array.median(deviationUpList)
    medianDownDeviation = array.median(deviationDownList)
    upperBand = fairPriceSmooth * medianUpDeviation
    lowerBand = fairPriceSmooth * medianDownDeviation
    bandUpSpread = upperBand - fairPriceSmooth
    bandDownSpread = fairPriceSmooth - lowerBand
    upperBandBoosted = fairPriceSmooth + bandUpSpread * i_boost
    lowerBandBoosted = fairPriceSmooth - bandDownSpread * i_boost
    dirSwitch: PersistentSeries[int] = 0
    trendRuleUp = i_thresholdUpSrc > upperBandBoosted if i_trendMode == 'Cross' else fairPriceSmooth > fairPriceSmooth[1]
    trendRuleDown = i_thresholdDownSrc < lowerBandBoosted if i_trendMode == 'Cross' else fairPriceSmooth < fairPriceSmooth[1]
    if trendRuleDown:
        dirSwitch = -1
    else:
        if trendRuleUp:
            dirSwitch = 1
    ohlcSpread = ohlc4 / fairPriceSmooth
    pivotUps: Persistent[list[float]] = array.new_float(0, 0)
    pivotDowns: Persistent[list[float]] = array.new_float(0, 0)
    pivotUpsSize = array.size(pivotUps)
    pivotDownsSize = array.size(pivotDowns)
    sizeLimitBand: int = 2000
    if array.size(pivotUps) > sizeLimitBand:
        array.remove(pivotUps, 0)
    if array.size(pivotDowns) > sizeLimitBand:
        array.remove(pivotDowns, 0)
    pivotUp = ta.pivothigh(ohlcSpread, 5, 5)
    pivotDown = ta.pivotlow(ohlcSpread, 5, 5)
    if low > upperBand:
        array.push(pivotUps, pivotUp)
    else:
        if high < lowerBand:
            array.push(pivotDowns, pivotDown)
    medianPivotUp = array.median(pivotUps)
    medianPivotDown = array.median(pivotDowns)
    pivotBandUpBase = fairPriceSmooth * medianPivotUp
    pivotBandDownBase = fairPriceSmooth * medianPivotDown
    pBandUpSpread = (pivotBandUpBase - fairPriceSmooth) * i_bandBoost
    pBandDownSpread = (fairPriceSmooth - pivotBandDownBase) * i_bandBoost
    pivotBandUp = fairPriceSmooth + pBandUpSpread
    pivotBandDown = fairPriceSmooth - pBandDownSpread
    pivotBandUp2 = pivotBandUp + pBandUpSpread
    pivotBandDown2 = pivotBandDown - pBandDownSpread
    pivotBandUp3 = pivotBandUp2 + pBandUpSpread
    pivotBandDown3 = pivotBandDown2 - pBandDownSpread
    volSma = ta.sma(volume, 20)
    volMultiplier = 0 if na(volSma) else volume / volSma
    abovePos2 = i_source > pivotBandUp2
    betweenPos1AndPos2 = i_source > pivotBandUp and i_source <= pivotBandUp2
    betweenMidAndPos1 = i_source > fairPriceSmooth and i_source <= pivotBandUp
    betweenMidAndNeg1 = i_source < fairPriceSmooth and i_source >= pivotBandDown
    betweenNeg1AndNeg2 = i_source < pivotBandDown and i_source >= pivotBandDown2
    belowNeg2 = i_source < pivotBandDown2
    abovePos2Count: Persistent[int] = 0
    abovePos2Vol: Persistent[float] = 0
    betweenPos1AndPos2Count: Persistent[int] = 0
    betweenPos1AndPos2Vol: Persistent[float] = 0
    betweenMidAndPos1Count: Persistent[int] = 0
    betweenMidAndPos1Vol: Persistent[float] = 0
    betweenMidAndNeg1Count: Persistent[int] = 0
    betweenMidAndNeg1Vol: Persistent[float] = 0
    betweenNeg1AndNeg2Count: Persistent[int] = 0
    betweenNeg1AndNeg2Vol: Persistent[float] = 0
    belowNeg2Count: Persistent[int] = 0
    belowNeg2Vol: Persistent[float] = 0
    if abovePos2:
        abovePos2Count = abovePos2Count + 1
        abovePos2Vol = abovePos2Vol + volMultiplier
    if betweenPos1AndPos2:
        betweenPos1AndPos2Count = betweenPos1AndPos2Count + 1
        betweenPos1AndPos2Vol = betweenPos1AndPos2Vol + volMultiplier
    if betweenMidAndPos1:
        betweenMidAndPos1Count = betweenMidAndPos1Count + 1
        betweenMidAndPos1Vol = betweenMidAndPos1Vol + volMultiplier
    if betweenMidAndNeg1:
        betweenMidAndNeg1Count = betweenMidAndNeg1Count + 1
        betweenMidAndNeg1Vol = betweenMidAndNeg1Vol + volMultiplier
    if betweenNeg1AndNeg2:
        betweenNeg1AndNeg2Count = betweenNeg1AndNeg2Count + 1
        betweenNeg1AndNeg2Vol = betweenNeg1AndNeg2Vol + volMultiplier
    if belowNeg2:
        belowNeg2Count = belowNeg2Count + 1
        belowNeg2Vol = belowNeg2Vol + volMultiplier
    allCounts = belowNeg2Count + betweenPos1AndPos2Count + betweenMidAndPos1Count + betweenMidAndNeg1Count + betweenNeg1AndNeg2Count + abovePos2Count
    above2PosPerc = math.round(abovePos2Count / allCounts, 3) * 100
    above2PosPercVol = math.round(abovePos2Vol / abovePos2Count, 2)
    above1PosPerc = math.round(betweenPos1AndPos2Count / allCounts, 2) * 100
    above1PosPercVol = math.round(betweenPos1AndPos2Vol / betweenPos1AndPos2Count, 2)
    aboveMidPosPerc = math.round(betweenMidAndPos1Count / allCounts, 2) * 100
    aboveMidPosPercVol = math.round(betweenMidAndPos1Vol / betweenMidAndPos1Count, 2)
    belowMidNegPerc = math.round(betweenMidAndNeg1Count / allCounts, 2) * 100
    belowMidNegPercVol = math.round(betweenMidAndNeg1Vol / betweenMidAndNeg1Count, 2)
    below1NegPerc = math.round(betweenNeg1AndNeg2Count / allCounts, 2) * 100
    below1NegPercVol = math.round(betweenNeg1AndNeg2Vol / betweenNeg1AndNeg2Count, 2)
    below2NegPerc = math.round(belowNeg2Count / allCounts, 3) * 100
    below2NegPercVol = math.round(belowNeg2Vol / belowNeg2Count, 2)
    n: str = '\n'
    l: str = '⎯⎯'
    vl: str = '｜'
    lengthText = string.tostring(timeframe.in_seconds(i_anchorTf) / 3600) + 'H' if i_smoothingType == 'VWAP' else string.tostring(i_length)
    settingsText = 'Settings' + n + '⎯⎯⎯⎯⎯⎯⎯⎯⎯' + n + i_sourceString + vl + i_smoothingType + vl + lengthText + n + ('Cross' + vl + '▲ ' + i_thresholdUpString + vl + '▼ ' + i_thresholdDownString if i_trendMode == 'Cross' else 'Direction') + n + 'Mid: ' + string.tostring(i_boost) + vl + 'Out: ' + string.tostring(i_bandBoost)
    tablePosition = position.top_right if tablePos == 'Top right' else position.bottom_right if tablePos == 'Bottom right' else position.bottom_left if tablePos == 'Bottom left' else position.top_left
    tableTextSize = size.tiny if tableSize == 1 else size.small if tableSize == 2 else size.normal if tableSize == 3 else size.huge if tableSize == 4 else size.large
    metricTable: Persistent = table.new(position=tablePosition, columns=50, rows=50, bgcolor=color.new(color.black, 80), border_width=3, border_color=color.rgb(23, 23, 23))
    table.cell(table_id=metricTable, column=1, row=0, text='Position' + n + '⎯⎯⎯⎯' + n + 'Time' + n + '⎯⎯⎯⎯' + n + 'Volume', text_color=color.white, text_halign=text.align_left, text_size=tableTextSize)
    table.cell(table_id=metricTable, column=2, row=0, text='+3' + n + l + n + string.tostring(above2PosPerc) + '%' + n + l + n + string.tostring(above2PosPercVol) + 'x', text_color=color.white, text_halign=text.align_center, bgcolor=color.new(color.red, 70), text_size=tableTextSize)
    table.cell(table_id=metricTable, column=3, row=0, text='+2' + n + l + n + string.tostring(above1PosPerc) + '%' + n + l + n + string.tostring(above1PosPercVol) + 'x', text_color=color.white, text_halign=text.align_center, bgcolor=color.new(color.red, 90), text_size=tableTextSize)
    table.cell(table_id=metricTable, column=4, row=0, text='+1' + n + l + n + string.tostring(aboveMidPosPerc) + '%' + n + l + n + string.tostring(aboveMidPosPercVol) + 'x', text_color=color.white, text_halign=text.align_center, bgcolor=color.new(color.gray, 80), text_size=tableTextSize)
    table.cell(table_id=metricTable, column=6, row=0, text='-1 ' + n + l + n + string.tostring(belowMidNegPerc) + '%' + n + l + n + string.tostring(belowMidNegPercVol) + 'x', text_color=color.white, text_halign=text.align_center, bgcolor=color.new(color.gray, 80), text_size=tableTextSize)
    table.cell(table_id=metricTable, column=7, row=0, text='-2' + n + l + n + string.tostring(below1NegPerc) + '%' + n + l + n + string.tostring(below1NegPercVol) + 'x', text_color=color.white, text_halign=text.align_center, bgcolor=color.new(color.blue, 90), text_size=tableTextSize)
    table.cell(table_id=metricTable, column=8, row=0, text='-3' + n + l + n + string.tostring(below2NegPerc) + '%' + n + l + n + string.tostring(below2NegPercVol) + 'x', text_color=color.white, text_halign=text.align_center, bgcolor=color.new(color.blue, 70), text_size=tableTextSize)
    table.cell(table_id=metricTable, column=10, row=0, text=settingsText, text_color=color.white, text_halign=text.align_left, text_valign=text.align_top, bgcolor=color.new(color.new('#100E48'), 80), text_size=tableTextSize)
    midColorLine = i_upColorLine if dirSwitch == 1 else i_downColorLine
    midColorBand = i_upColorFill if dirSwitch == 1 else i_downColorFill
    deviationColor = extremeDeviationUp if dirSwitch == 1 else extremeDeviationDown
    extremeUpFill = extremeUpColor
    extremeDownFill = extremeDownColor
    pOhlc = plot(ohlc4, 'OHLC4', color=color.new(color.white, 100), display=display.all - display.status_line)
    pUpper = plot(upperBandBoosted, 'Threshold band up', color=color.new(color.white, 100), style=plot.style_linebr, display=display.all - display.status_line)
    pLower = plot(lowerBandBoosted, 'Threshold band down', color=color.new(color.white, 100), style=plot.style_linebr, display=display.all - display.status_line)
    pMid = plot(fairPriceSmooth, 'Fair value basis', color=midColorLine, linewidth=1, display=display.all - display.status_line)
    p1U = plot(pivotBandUp, 'Fair value deviation band up 1x', color=deviationBandColor, display=display.all - display.status_line)
    p1D = plot(pivotBandDown, 'Fair value deviation band down 1x', color=deviationBandColor, display=display.all - display.status_line)
    p2U = plot(pivotBandUp2, 'Fair value deviation band up 2x', color=deviationBandColor, display=display.all - display.status_line)
    p2D = plot(pivotBandDown2, 'Fair value deviation band down 2x', color=deviationBandColor, display=display.all - display.status_line)
    p3U = plot(pivotBandUp3, 'Fair value deviation band up 3x', color=deviationBandColor, display=display.all - display.status_line)
    p3D = plot(pivotBandDown3, 'Fair value deviation band down 3x', color=deviationBandColor, display=display.all - display.status_line)
    fill(p3U, p2U, color=extremeUpFill, title='Extreme fair value deviation band up fill')
    fill(p3D, p2D, color=extremeDownFill, title='Extreme fair value deviation band down fill')
    fill(pOhlc, pLower, pivotBandDown3, lowerBandBoosted, extremeDeviationDown, color.new(color.gray, 100), title='Extreme fair value deviation up hue fill')
    fill(pOhlc, pUpper, pivotBandUp3, upperBandBoosted, extremeDeviationUp, color.new(color.gray, 100), title='Extreme fair value deviation down hue fill')
    fill(pUpper, pLower, color=midColorBand, title='Threshold band fill')
    barcolor(color.blue if i_btCheck and belowNeg2 else color.rgb(124, 147, 239) if i_btCheck and betweenNeg1AndNeg2 else color.aqua if i_btCheck and betweenMidAndNeg1 else color.yellow if i_btCheck and betweenMidAndPos1 else color.orange if i_btCheck and betweenPos1AndPos2 else color.red if i_btCheck and abovePos2 else na)
    plot(volMultiplier if i_btCheck else na, title='Relative volume', color=color.new(color.fuchsia, 100), display=display.data_window)
    plot(allCounts if i_btCheck else na, title='All time counts', color=color.new(color.fuchsia, 100), display=display.data_window)
    plot(abovePos2Count if i_btCheck else na, title='+3 time count', color=color.new(color.red, 100), display=display.data_window)
    plot(abovePos2Vol if i_btCheck else na, title='+3 volume count cumulative', color=color.new(color.red, 100), display=display.data_window)
    plot(abovePos2Vol / abovePos2Count if i_btCheck else na, title='+3 volume count average', color=color.new(color.red, 100), display=display.data_window)
    plot(betweenPos1AndPos2Count if i_btCheck else na, title='+2 time count', color=color.new(color.orange, 100), display=display.data_window)
    plot(betweenPos1AndPos2Vol if i_btCheck else na, title='+2 volume count cumulative', color=color.new(color.orange, 100), display=display.data_window)
    plot(betweenPos1AndPos2Vol / betweenPos1AndPos2Count if i_btCheck else na, title='+2 volume count average', color=color.new(color.orange, 100), display=display.data_window)
    plot(betweenMidAndPos1Count if i_btCheck else na, title='+1 time count', color=color.new(color.yellow, 100), display=display.data_window)
    plot(betweenMidAndPos1Vol if i_btCheck else na, title='+1 volume count cumulative', color=color.new(color.yellow, 100), display=display.data_window)
    plot(betweenMidAndPos1Vol / betweenMidAndPos1Count if i_btCheck else na, title='+1 volume count average', color=color.new(color.yellow, 100), display=display.data_window)
    plot(betweenMidAndNeg1Count if i_btCheck else na, title='-1 time count', color=color.new(color.aqua, 100), display=display.data_window)
    plot(betweenMidAndNeg1Vol if i_btCheck else na, title='-1 volume count cumulative', color=color.new(color.aqua, 100), display=display.data_window)
    plot(betweenMidAndNeg1Vol / betweenMidAndNeg1Count if i_btCheck else na, title='-1 volume count average', color=color.new(color.aqua, 100), display=display.data_window)
    plot(betweenNeg1AndNeg2Count if i_btCheck else na, title='-2 time count', color=color.new(color.rgb(124, 147, 239), 100), display=display.data_window)
    plot(betweenNeg1AndNeg2Vol if i_btCheck else na, title='-2 volume count cumulative', color=color.new(color.rgb(124, 147, 239), 100), display=display.data_window)
    plot(betweenNeg1AndNeg2Vol / betweenNeg1AndNeg2Count if i_btCheck else na, title='-2 volume count average', color=color.new(color.rgb(124, 147, 239), 100), display=display.data_window)
    plot(belowNeg2Count if i_btCheck else na, title='-3 time count', color=color.new(color.blue, 100), display=display.data_window)
    plot(belowNeg2Vol if i_btCheck else na, title='-3 volume count cumulative', color=color.new(color.blue, 100), display=display.data_window)
    plot(belowNeg2Vol / belowNeg2Count if i_btCheck else na, title='-3 volume count average', color=color.new(color.blue, 100), display=display.data_window)
    deviation1CrossUp = ta.crossover(high, pivotBandUp)
    deviation2CrossUp = ta.crossover(high, pivotBandUp2)
    deviation3CrossUp = ta.crossover(high, pivotBandUp3)
    deviation1CrossDown = ta.crossunder(low, pivotBandDown)
    deviation2CrossDown = ta.crossunder(low, pivotBandDown2)
    deviation3CrossDown = ta.crossunder(low, pivotBandDown3)
    fairPriceInUp = dirSwitch == 1 and low <= upperBandBoosted
    fairPriceInDown = dirSwitch == -1 and high >= lowerBandBoosted
    newTrendUp = dirSwitch[1] == -1 and dirSwitch == 1 and barstate.isconfirmed
    newTrendDown = dirSwitch[1] == 1 and dirSwitch == -1 and barstate.isconfirmed
    alertcondition(deviation1CrossUp, 'Deviation band +1 cross', 'High cross above +1 band detected.')
    alertcondition(deviation2CrossUp, 'Deviation band +2 cross', 'High cross above +2 band detected.')
    alertcondition(deviation3CrossUp, 'Deviation band +3 cross', 'High cross above +3 band detected.')
    alertcondition(deviation1CrossDown, 'Deviation band -1 cross', 'Low cross below -1 band detected.')
    alertcondition(deviation2CrossDown, 'Deviation band -2 cross', 'Low cross below -2 band detected.')
    alertcondition(deviation3CrossDown, 'Deviation band -3 cross', 'Low cross below -3 band detected.')
    alertcondition(fairPriceInUp, 'Low at fair value basis in an uptrend', 'Low at fair value basis in an uptrend detected.')
    alertcondition(fairPriceInDown, 'High at fair value basis in a downtrend', 'High at fair value basis  in a downtrend detected.')
    alertcondition(newTrendUp, 'New trend up', 'New trend up detected')
    alertcondition(newTrendDown, 'New trend down', 'New trend down detected')
    alertcondition(deviation1CrossDown or deviation1CrossUp, 'Deviation band -1 cross or +1 cross', 'Low cross below -1/high cross above +1 band detected.')
    alertcondition(deviation2CrossDown or deviation2CrossUp, 'Deviation band -2 cross or +2 cross', 'Low cross below -2/high cross above +2 band detected.')
    alertcondition(deviation3CrossDown or deviation3CrossUp, 'Deviation band -3 cross or +3 cross', 'Low cross below -3/high cross above +3 band detected.')
    alertcondition(newTrendUp or newTrendDown, 'New trend up or new trend down', 'New trend up/down detected.')
    def crossFunc(src, crossType, crossRef):
        crossRefConv = pivotBandUp if crossRef == '+1' else pivotBandUp2 if crossRef == '+2' else pivotBandUp3 if crossRef == '+3' else pivotBandDown if crossRef == '-1' else pivotBandDown2 if crossRef == '-2' else pivotBandDown3
        cross = ta.crossover(src, crossRefConv) if crossType == 'Above' else ta.crossunder(src, crossRefConv)
        crossText = crossRef + '\n' + '▼' if crossType == 'Above' else '▲' + '\n' + crossRef
        crossPos = label.style_label_down if crossType == 'Above' else label.style_label_up
        crossLoc = high if crossType == 'Above' else low
        crossCol = i_crossAboveCol if crossType == 'Above' else i_crossBelowCol
        __block_result__ = na
        if cross:
            __block_result__ = label.new(x=bar_index, y=crossLoc, xloc=xloc.bar_index, text=crossText, style=crossPos, textcolor=crossCol, color=color.new(color.aqua, 100), size=size.normal)
        return __block_result__

    if i_crossRef1 != 'Off':
        crossFunc(i_crossSrc1, i_crossMethod1, i_crossRef1)
    if i_crossRef2 != 'Off':
        crossFunc(i_crossSrc2, i_crossMethod2, i_crossRef2)
    if i_crossRef3 != 'Off':
        crossFunc(i_crossSrc3, i_crossMethod3, i_crossRef3)
    if i_crossRef4 != 'Off':
        crossFunc(i_crossSrc4, i_crossMethod4, i_crossRef4)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)