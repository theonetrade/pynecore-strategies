"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barcolor, close, color, extend, high, input, label, line,
    location, low, na, open, plotchar, plotshape, request, script, shape, size, string, syminfo,
    text, time, timeframe, xloc, yloc
)
from pynecore.types import Series


@script.indicator('Strat Assistant', overlay=True, precision=0, na_bool=True)
def main(
    _actionWickPercentage=input(title='Action Wick Percentage', defval=0.75),
    _isPrevDayHighLineActive=input(title='Prev Day High Line Active?', defval=True),
    _prevDayHighColor=input(title='Prev Day High Line Color', defval=color.lime),
    _isPrevDayLowLineActive=input(title='Prev Day Low Line Active?', defval=True),
    _prevDayLowColor=input(title='Prev Day High Line Color', defval=color.maroon),
    _isPrevWeekHighLineActive=input(title='Prev Week High Lines Active?', defval=False),
    _prevWeekHighColor=input(title='Prev Week High Line Color', defval=color.orange),
    _isPrevWeekLowLineActive=input(title='Prev Week Low Lines Active?', defval=False),
    _prevWeekLowColor=input(title='Prev Week Low Line Color', defval=color.purple),
    _isFtcActive=input(title='Full Time Frame Continuity Active?', defval=True),
    _isDebugLabelActive=input(title='Debug Label (Beta)', defval=False)
):
    _bullColor = color.green
    _bearColor = color.red
    _outsideColor = color.fuchsia
    _insideColor = color.new(color.new('#F6BE00'), 0)
    _bullShape = shape.arrowup
    _bearShape = shape.arrowdown
    _oneBarColor = _insideColor
    _oneBarChar: str = '1'
    _twoUpBarColor = _bullColor
    _twoUpBarChar: str = '2'
    _twoUpBarStyle = _bullShape
    _twoDownBarColor = _bearColor
    _twoDownBarChar: str = '2'
    _twoDownBarStyle = _bearShape
    _threeBarColor = _outsideColor
    _threeBarChar: str = '3'
    _barCharLocation = location.belowbar
    _barShapeLocation = location.abovebar
    _stratComboLocation = location.top
    _stratComboStyle = shape.flag
    _stratComboOffset: int = 3
    _actionableOffset: int = 2
    _actionalSignalShape = shape.flag
    _actionalSignalLocation = location.bottom
    _firstBarIndex: int = 0
    _secondBarIndex: int = 1
    _thirdBarIndex: int = 2
    _fourthBarIndex: int = 3
    _barIndexOffset: int = 1
    _is222BearishContinuation: str = '222 Bearish \nContinuation'
    _is222BullishContinuation: str = '222 Bullish \nContinuation'
    _is212BearishContinuationMeasuredMove: str = '212 Bearish Continuation \nMeasured Move'
    _is212BullishContinuationMeasuredMove: str = '212 Bullish Continuation \nMeasured Move'
    _is22BearishReversal: str = '22 Bearish \nReversal'
    _is22BullishReversal: str = '22 Bullish \nReversal'
    _is212BearishReversal: str = '212 Bearish \nReversal'
    _is212BullishReversal: str = '212 Bullish \nReversal'
    _is322BearishReversal: str = '322 Bearish \nReversal'
    _is322BullishReversal: str = '322 Bullish \nReversal'
    _is32BearishReversal: str = '32 Bearish \nReversal'
    _is32BullishReversal: str = '32 Bullish \nReversal'
    _is312BearishReversal: str = '312 Bearish \nReversal'
    _is312BullishReversal: str = '312 Bullish \nReversal'
    _is122BearishRevStratReversal: str = '122 Bearish RevStrat \nReversal'
    _is122BullishRevStratReversal: str = '122 Bullish RevStrat \nReversal'
    _is2222BearishRandyJackson: str = '2222 Bearish \nRandyJackson'
    _is2222BullishRandyJackson: str = '2222 Bullish \nRandyJackson'
    _is3BearishRevStratReversal: str = '3 Bearish \nRevStrat Reversal'
    _is3BullishRevStratReversal: str = '3 Bullish \nRevStrat Reversal'
    _ftcLocation = location.absolute
    _oneMinuteTimeFrame: str = '1'
    _threeMinuteTimeFrame: str = '3'
    _fiveMinuteTimeFrame: str = '5'
    _tenMinuteTimeFrame: str = '10'
    _fifteenMinuteTimeFrame: str = '15'
    _thirtyMinuteTimeFrame: str = '30'
    _fourtyFiveMinuteTimeFrame: str = '45'
    _hourTimeFrame: str = '60'
    _twoHourTimeFrame: str = '120'
    _threeHourTimeFrame: str = '180'
    _fourHourTimeFrame: str = '240'
    _dayTimeFrame: str = 'D'
    _weekTimeFrame: str = 'W'
    _monthTimeFrame: str = 'M'
    _quarterTimeFrame: str = '3M'
    _ftcBaseOffset: int = 1
    _ftc15Offset = _ftcBaseOffset + 1
    _ftc30Offset = _ftcBaseOffset + 2
    _ftcHourOffset = _ftcBaseOffset + 3
    _ftcFourHourOffset = _ftcBaseOffset + 4
    _ftcDayOffset = _ftcBaseOffset + 5
    _ftcWeekOffset = _ftcBaseOffset + 6
    _ftcMonthOffset = _ftcBaseOffset + 7
    _ftcQuarterOffset = _ftcBaseOffset + 8
    _ftc15Text: str = '15'
    _ftc30Text: str = '30'
    _ftcHourText: str = 'H'
    _ftcFourHourText: str = '4H'
    _ftcDayText: str = 'D'
    _ftcWeekText: str = 'W'
    _ftcMonthText: str = 'M'
    _ftcQuarterText: str = 'Q'
    _ftcInsideText: str = 'IN\n'
    _ftcOutsideText: str = 'O\n'
    def getOneBar(rightBar, leftBar):
        return high[rightBar] <= high[leftBar] and low[rightBar] >= low[leftBar]

    def getTwoUpBar(rightBar, leftBar):
        return high[rightBar] > high[leftBar] and (not low[rightBar] < low[leftBar])

    def getTwoDownBar(rightBar, leftBar):
        return low[rightBar] < low[leftBar] and (not high[rightBar] > high[leftBar])

    def getThreeBar(rightBar, leftBar):
        return high[rightBar] > high[leftBar] and low[rightBar] < low[leftBar]

    def getBarColor():
        getOneBar_1 = getOneBar(0, 1)
        getThreeBar_1 = getThreeBar(0, 1)
        getTwoUpBar_1 = getTwoUpBar(0, 1)
        getTwoDownBar_1 = getTwoDownBar(0, 1)
        iff_1 = _twoDownBarColor if getTwoDownBar_1 else na
        iff_2 = _twoUpBarColor if getTwoUpBar_1 else iff_1
        iff_3 = _threeBarColor if getThreeBar_1 else iff_2
        return _oneBarColor if getOneBar_1 else iff_3

    def getIndexOneBar(barIndex):
        return getOneBar(barIndex, barIndex + _barIndexOffset)

    def getIndexTwoUpBar(barIndex):
        return getTwoUpBar(barIndex, barIndex + _barIndexOffset)

    def getIndexTwoDownBar(barIndex):
        return getTwoDownBar(barIndex, barIndex + _barIndexOffset)

    def getIndexThreeBar(barIndex):
        return getThreeBar(barIndex, barIndex + _barIndexOffset)

    getIndexTwoDownBar_1 = getIndexTwoDownBar(_secondBarIndex)
    getIndexTwoDownBar_2 = getIndexTwoDownBar(_firstBarIndex)
    is222BearishContinuation = getIndexTwoDownBar(_thirdBarIndex) and getIndexTwoDownBar_1 and getIndexTwoDownBar_2
    getIndexTwoUpBar_1 = getIndexTwoUpBar(_secondBarIndex)
    getIndexTwoUpBar_2 = getIndexTwoUpBar(_firstBarIndex)
    is222BullishContinuation = getIndexTwoUpBar(_thirdBarIndex) and getIndexTwoUpBar_1 and getIndexTwoUpBar_2
    getIndexOneBar_1 = getIndexOneBar(_secondBarIndex)
    getIndexTwoDownBar_3 = getIndexTwoDownBar(_firstBarIndex)
    is212BearishContinuationMeasuredMove = getIndexTwoDownBar(_thirdBarIndex) and getIndexOneBar_1 and getIndexTwoDownBar_3
    getIndexOneBar_2 = getIndexOneBar(_secondBarIndex)
    getIndexTwoUpBar_3 = getIndexTwoUpBar(_firstBarIndex)
    is212BullishContinuationMeasuredMove = getIndexTwoUpBar(_thirdBarIndex) and getIndexOneBar_2 and getIndexTwoUpBar_3
    getIndexTwoDownBar_4 = getIndexTwoDownBar(_firstBarIndex)
    getIndexOneBar_3 = getIndexOneBar(_thirdBarIndex)
    getIndexTwoDownBar_5 = getIndexTwoDownBar(_thirdBarIndex)
    getIndexTwoDownBar_6 = getIndexTwoDownBar(3)
    getIndexThreeBar_1 = getIndexThreeBar(_thirdBarIndex)
    is22BearishReversal = getIndexTwoUpBar(_secondBarIndex) and getIndexTwoDownBar_4 and (not getIndexOneBar_3) and (not getIndexTwoDownBar_5) and (not getIndexTwoDownBar_6) and (not getIndexThreeBar_1)
    getIndexTwoUpBar_4 = getIndexTwoUpBar(_firstBarIndex)
    getIndexOneBar_4 = getIndexOneBar(_thirdBarIndex)
    getIndexTwoUpBar_5 = getIndexTwoUpBar(_thirdBarIndex)
    getIndexTwoUpBar_6 = getIndexTwoUpBar(3)
    getIndexThreeBar_2 = getIndexThreeBar(_thirdBarIndex)
    is22BullishReversal = getIndexTwoDownBar(_secondBarIndex) and getIndexTwoUpBar_4 and (not getIndexOneBar_4) and (not getIndexTwoUpBar_5) and (not getIndexTwoUpBar_6) and (not getIndexThreeBar_2)
    getIndexOneBar_5 = getIndexOneBar(_secondBarIndex)
    getIndexTwoDownBar_7 = getIndexTwoDownBar(_firstBarIndex)
    is212BearishReversal = getIndexTwoUpBar(_thirdBarIndex) and getIndexOneBar_5 and getIndexTwoDownBar_7
    getIndexOneBar_6 = getIndexOneBar(_secondBarIndex)
    getIndexTwoUpBar_7 = getIndexTwoUpBar(_firstBarIndex)
    is212BullishReversal = getIndexTwoDownBar(_thirdBarIndex) and getIndexOneBar_6 and getIndexTwoUpBar_7
    getIndexTwoUpBar_8 = getIndexTwoUpBar(_secondBarIndex)
    getIndexTwoDownBar_8 = getIndexTwoDownBar(_firstBarIndex)
    is322BearishReversal = getIndexThreeBar(_thirdBarIndex) and getIndexTwoUpBar_8 and getIndexTwoDownBar_8
    getIndexTwoDownBar_9 = getIndexTwoDownBar(_secondBarIndex)
    getIndexTwoUpBar_9 = getIndexTwoUpBar(_firstBarIndex)
    is322BullishReversal = getIndexThreeBar(_thirdBarIndex) and getIndexTwoDownBar_9 and getIndexTwoUpBar_9
    getIndexTwoDownBar_10 = getIndexTwoDownBar(_firstBarIndex)
    is32BearishReversal = getIndexThreeBar(_secondBarIndex) and getIndexTwoDownBar_10
    getIndexTwoUpBar_10 = getIndexTwoUpBar(_firstBarIndex)
    is32BullishReversal = getIndexThreeBar(_secondBarIndex) and getIndexTwoUpBar_10
    getIndexOneBar_7 = getIndexOneBar(_secondBarIndex)
    getIndexTwoDownBar_11 = getIndexTwoDownBar(_firstBarIndex)
    is312BearishReversal = getIndexThreeBar(_thirdBarIndex) and getIndexOneBar_7 and getIndexTwoDownBar_11
    getIndexOneBar_8 = getIndexOneBar(_secondBarIndex)
    getIndexTwoUpBar_11 = getIndexTwoUpBar(_firstBarIndex)
    is312BullishReversal = getIndexThreeBar(_thirdBarIndex) and getIndexOneBar_8 and getIndexTwoUpBar_11
    getIndexTwoUpBar_12 = getIndexTwoUpBar(_secondBarIndex)
    getIndexTwoDownBar_12 = getIndexTwoDownBar(_firstBarIndex)
    is122BearishRevStratReversal = getIndexOneBar(_thirdBarIndex) and getIndexTwoUpBar_12 and getIndexTwoDownBar_12
    getIndexTwoDownBar_13 = getIndexTwoDownBar(_secondBarIndex)
    getIndexTwoUpBar_13 = getIndexTwoUpBar(_firstBarIndex)
    is122BullishRevStratReversal = getIndexOneBar(_thirdBarIndex) and getIndexTwoDownBar_13 and getIndexTwoUpBar_13
    getIndexTwoDownBar_14 = getIndexTwoDownBar(_thirdBarIndex)
    getIndexTwoUpBar_14 = getIndexTwoUpBar(_secondBarIndex)
    getIndexTwoDownBar_15 = getIndexTwoDownBar(_firstBarIndex)
    is2222BearishRandyJackson = getIndexTwoDownBar(_fourthBarIndex) and getIndexTwoDownBar_14 and getIndexTwoUpBar_14 and getIndexTwoDownBar_15
    getIndexTwoUpBar_15 = getIndexTwoUpBar(_thirdBarIndex)
    getIndexTwoDownBar_16 = getIndexTwoDownBar(_secondBarIndex)
    getIndexTwoUpBar_16 = getIndexTwoUpBar(_firstBarIndex)
    is2222BullishRandyJackson = getIndexTwoUpBar(_fourthBarIndex) and getIndexTwoUpBar_15 and getIndexTwoDownBar_16 and getIndexTwoUpBar_16
    is3BearishRevStratReversal = getIndexThreeBar(_firstBarIndex) and close < low[1]
    is3BullishRevStratReversal = getIndexThreeBar(_firstBarIndex) and close > low[1]
    def getActionalbeWickHeight(wickPercentage):
        return (high - low) * wickPercentage

    getShooterTop = high - getActionalbeWickHeight(_actionWickPercentage)
    getHammerBottom = low + getActionalbeWickHeight(_actionWickPercentage)
    isInsideBar = getIndexOneBar(_firstBarIndex)
    getIndexOneBar_9 = getIndexOneBar(_firstBarIndex)
    isShooter = open < getShooterTop and close < getShooterTop and (not getIndexOneBar_9)
    getIndexOneBar_10 = getIndexOneBar(_firstBarIndex)
    isHammer = open > getHammerBottom and close > getHammerBottom and (not getIndexOneBar_10)
    def getSecurityByTimeFrame(timeFrame):
        openValue, closeValue, highValue, lowValue, timeValue = request.security(syminfo.tickerid, timeFrame, (open, close, high, low, time))
        return (openValue, closeValue, highValue, lowValue, timeValue)

    def getOneBarBySeries(highSeries: Series, lowSeries: Series):
        return highSeries <= highSeries[1] and lowSeries >= lowSeries[1]

    def getThreeBarBySeries(highSeries: Series, lowSeries: Series):
        return highSeries > highSeries[1] and lowSeries < lowSeries[1]

    open15Value, close15Value, high15Value, low15Value, time15Value = getSecurityByTimeFrame(_fifteenMinuteTimeFrame)
    open30Value, close30Value, high30Value, low30Value, time30Value = getSecurityByTimeFrame(_thirtyMinuteTimeFrame)
    open60Value, close60Value, highHourValue, lowHourValue, timeHourValue = getSecurityByTimeFrame(_hourTimeFrame)
    openFourHourValue, closeFourHourValue, highFourHourValue, lowFourHourValue, timeFourHourValue = getSecurityByTimeFrame(_fourHourTimeFrame)
    highDayValue: Series
    lowDayValue: Series
    timeDayValue: Series
    openDayValue, closeDayValue, highDayValue, lowDayValue, timeDayValue = getSecurityByTimeFrame(_dayTimeFrame)
    highWeekValue: Series
    lowWeekValue: Series
    openWeekValue, closeWeekValue, highWeekValue, lowWeekValue, timeWeekValue = getSecurityByTimeFrame(_weekTimeFrame)
    openMonthValue, closeMonthValue, highMonthValue, lowMonthValue, timeMonthValue = getSecurityByTimeFrame(_monthTimeFrame)
    openQuarterValue, closeQuarterValue, highQuarterValue, lowQuarterValue, timeQuarterValue = getSecurityByTimeFrame(_quarterTimeFrame)
    is15FtcGreen = open15Value <= close15Value
    is30FtcGreen = open30Value <= close30Value
    isHourFtcGreen = open60Value <= close60Value
    isFourHourFtcGreen = openFourHourValue <= closeFourHourValue
    isDayFtcGreen = openDayValue <= closeDayValue
    isWeekFtcGreen = openWeekValue <= closeWeekValue
    isMonthFtcGreen = openMonthValue <= closeMonthValue
    isQuarterFtcGreen = openQuarterValue <= closeQuarterValue
    is15FtcInside = getOneBarBySeries(high15Value, low15Value)
    is30FtcInside = getOneBarBySeries(high30Value, low30Value)
    isHourFtcInside = getOneBarBySeries(highHourValue, lowHourValue)
    isFourHourFtcInside = getOneBarBySeries(highFourHourValue, lowFourHourValue)
    isDayFtcInside = getOneBarBySeries(highDayValue, lowDayValue)
    isWeekFtcInside = getOneBarBySeries(highWeekValue, lowWeekValue)
    isMonthFtcInside = getOneBarBySeries(highMonthValue, lowMonthValue)
    isQuarterFtcInside = getOneBarBySeries(highQuarterValue, lowQuarterValue)
    is15FtcOutside = getThreeBarBySeries(high15Value, low15Value)
    is30FtcOutside = getThreeBarBySeries(high30Value, low30Value)
    isHourFtcOutside = getThreeBarBySeries(highHourValue, lowHourValue)
    isFourHourFtcOutside = getThreeBarBySeries(highFourHourValue, lowFourHourValue)
    isDayFtcOutside = getThreeBarBySeries(highDayValue, lowDayValue)
    isWeekFtcOutside = getThreeBarBySeries(highWeekValue, lowWeekValue)
    isMonthFtcOutside = getThreeBarBySeries(highMonthValue, lowMonthValue)
    isQuarterFtcOutside = getThreeBarBySeries(highQuarterValue, lowQuarterValue)
    is15ValidTimeFrame = timeframe.period == _oneMinuteTimeFrame or timeframe.period == _threeMinuteTimeFrame or timeframe.period == _fiveMinuteTimeFrame or (timeframe.period == _tenMinuteTimeFrame) or (timeframe.period == _fifteenMinuteTimeFrame)
    is30ValidTimeFrame = is15ValidTimeFrame or timeframe.period == _thirtyMinuteTimeFrame
    isHourValidTimeFrame = is30ValidTimeFrame or timeframe.period == _hourTimeFrame or timeframe.period == _fourtyFiveMinuteTimeFrame
    isFourHourValidTimeFrame = isHourValidTimeFrame or timeframe.isintraday
    isDayValidTimeFrame = isFourHourValidTimeFrame or timeframe.isdaily
    isWeekValidTimeFrame = isDayValidTimeFrame or timeframe.period == _weekTimeFrame or timeframe.isintraday
    isMonthValidTimeFrame = isWeekValidTimeFrame or timeframe.ismonthly
    isQuarterValidTimeFrame = isWeekValidTimeFrame or timeframe.isdwm
    ftcTimeFrameOffset: int = 0
    if not isQuarterValidTimeFrame:
        ftcTimeFrameOffset = 8
    elif not isMonthValidTimeFrame:
        ftcTimeFrameOffset = 7
    elif not isWeekValidTimeFrame:
        ftcTimeFrameOffset = 6
    elif not isDayValidTimeFrame:
        ftcTimeFrameOffset = 5
    elif not isFourHourValidTimeFrame:
        ftcTimeFrameOffset = 4
    elif not isHourValidTimeFrame:
        ftcTimeFrameOffset = 3
    elif not is30ValidTimeFrame:
        ftcTimeFrameOffset = 2
    elif not is15ValidTimeFrame:
        ftcTimeFrameOffset = 1
    is15Valid = is15ValidTimeFrame
    is30Valid = is30ValidTimeFrame
    isHourValid = isHourValidTimeFrame
    isFourHourValid = isFourHourValidTimeFrame
    isDayValid = isDayValidTimeFrame
    isWeekValid = isWeekValidTimeFrame
    isMonthValid = isMonthValidTimeFrame
    isQuarterValid = isQuarterValidTimeFrame
    is15FtcGreenPlot = _isFtcActive and is15Valid and is15FtcGreen
    is15FtcRedPlot = _isFtcActive and is15Valid and (not is15FtcGreen)
    is15FtcInsidePlot = _isFtcActive and is15Valid and is15FtcInside
    is15FtcOutsidePlot = _isFtcActive and is15Valid and is15FtcOutside
    is30FtcGreenPlot = is30Valid and is30FtcGreen
    is30FtcRedPlot = is30Valid and (not is30FtcGreen)
    is30FtcInsidePlot = _isFtcActive and is30Valid and is30FtcInside
    is30FtcOutsidePlot = _isFtcActive and is30Valid and is30FtcOutside
    isHourFtcGreenPlot = isHourValid and isHourFtcGreen
    isHourFtcRedPlot = isHourValid and (not isHourFtcGreen)
    isHourFtcInsidePlot = _isFtcActive and isHourValid and isHourFtcInside
    isHourFtcOutsidePlot = _isFtcActive and isHourValid and isHourFtcOutside
    isFourHourFtcGreenPlot = isFourHourValid and isFourHourFtcGreen
    isFourHourFtcRedPlot = isFourHourValid and (not isFourHourFtcGreen)
    isFourHourFtcInsidePlot = _isFtcActive and isFourHourValid and isFourHourFtcInside
    isFourHourFtcOutsidePlot = _isFtcActive and isFourHourValid and isFourHourFtcOutside
    isDayFtcGreenPlot = isDayValid and isDayFtcGreen
    isDayFtcRedPlot = isDayValid and (not isDayFtcGreen)
    isDayFtcInsidePlot = _isFtcActive and isDayValid and isDayFtcInside
    isDayFtcOutsidePlot = _isFtcActive and isDayValid and isDayFtcOutside
    isWeekFtcGreenPlot = isWeekValid and isWeekFtcGreen
    isWeekFtcRedPlot = isWeekValid and (not isWeekFtcGreen)
    isWeekFtcInsidePlot = _isFtcActive and isWeekValid and isWeekFtcInside
    isWeekFtcOutsidePlot = _isFtcActive and isWeekValid and isWeekFtcOutside
    isMonthFtcGreenPlot = isMonthValid and isMonthFtcGreen
    isMonthFtcRedPlot = isMonthValid and (not isMonthFtcGreen)
    isMonthFtcInsidePlot = _isFtcActive and isMonthValid and isMonthFtcInside
    isMonthFtcOutsidePlot = _isFtcActive and isMonthValid and isMonthFtcOutside
    isQuarterFtcGreenPlot = isQuarterValid and isQuarterFtcGreen
    isQuarterFtcRedPlot = isQuarterValid and (not isQuarterFtcGreen)
    isQuarterFtcInsidePlot = _isFtcActive and isQuarterValid and isQuarterFtcInside
    isQuarterFtcOutsidePlot = _isFtcActive and isQuarterValid and isQuarterFtcOutside
    plotchar(getOneBar(0, 1), title='One Bar', char=_oneBarChar, location=_barCharLocation, color=_oneBarColor)
    plotshape(getTwoUpBar(0, 1), style=_twoUpBarStyle, title='Two Up Bar Shape', location=_barShapeLocation, color=_twoUpBarColor)
    plotchar(getTwoUpBar(0, 1), title='Two Up Bar', char=_twoUpBarChar, location=_barCharLocation, color=_twoUpBarColor)
    plotshape(getTwoDownBar(0, 1), style=_twoDownBarStyle, title='Two Bar Shape', location=_barShapeLocation, color=_twoDownBarColor)
    plotchar(getTwoDownBar(0, 1), title='Two Down Bar', char=_twoDownBarChar, location=_barCharLocation, color=_twoDownBarColor)
    plotchar(getThreeBar(0, 1), title='Three Bar', char=_threeBarChar, location=_barCharLocation, color=_threeBarColor)
    barcolor(getBarColor())
    plotshape(isShooter, title='isShooter Label', style=_actionalSignalShape, color=color.new(_bearColor, 0), location=_actionalSignalLocation, text='Shooter', textcolor=color.new(_bearColor, 0), offset=_actionableOffset, show_last=1)
    plotshape(isHammer, title='isHammer Label', style=_actionalSignalShape, color=color.new(_bullColor, 0), location=_actionalSignalLocation, text='Hammer', textcolor=color.new(_bullColor, 0), offset=_actionableOffset, show_last=1)
    plotshape(isInsideBar, title='isInsideBar Label', style=_actionalSignalShape, color=_insideColor, location=_actionalSignalLocation, text='Inside Bar', textcolor=_insideColor, offset=_actionableOffset, show_last=1)
    plotchar(close if is15FtcInsidePlot else na, title='isFtc15Inside', char='', text=_ftcInsideText, location=_ftcLocation, offset=_ftc15Offset - ftcTimeFrameOffset, color=_insideColor, show_last=1)
    plotchar(close if is15FtcOutsidePlot else na, title='isFtc15Outside', char='', text=_ftcOutsideText, location=_ftcLocation, offset=_ftc15Offset - ftcTimeFrameOffset, color=color.new(_outsideColor, 0), show_last=1)
    plotshape(close if is15FtcGreenPlot else na, title='isFtc15Green', style=_bullShape, text=_ftc15Text, location=_ftcLocation, offset=_ftc15Offset - ftcTimeFrameOffset, color=color.new(_bullColor, 0), show_last=1)
    plotshape(close if is15FtcRedPlot else na, title='isFtc15Red', style=_bearShape, text=_ftc15Text, location=_ftcLocation, offset=_ftc15Offset - ftcTimeFrameOffset, color=color.new(_bearColor, 0), show_last=1)
    plotchar(close if is30FtcInsidePlot else na, title='isFtc30Inside', char='', text=_ftcInsideText, location=_ftcLocation, offset=_ftc30Offset - ftcTimeFrameOffset, color=_insideColor, show_last=1)
    plotchar(close if is30FtcOutsidePlot else na, title='isFtc30Outside', char='', text=_ftcOutsideText, location=_ftcLocation, offset=_ftc30Offset - ftcTimeFrameOffset, color=color.new(_outsideColor, 0), show_last=1)
    plotshape(close if is30FtcGreenPlot else na, title='isFtc30Green', style=_bullShape, text=_ftc30Text, location=_ftcLocation, offset=_ftc30Offset - ftcTimeFrameOffset, color=color.new(_bullColor, 0), show_last=1)
    plotshape(close if is30FtcRedPlot else na, title='isFtc30Red', style=_bearShape, text=_ftc30Text, location=_ftcLocation, offset=_ftc30Offset - ftcTimeFrameOffset, color=color.new(_bearColor, 0), show_last=1)
    plotchar(close if isHourFtcInsidePlot else na, title='isFtcHourInside', char='', text=_ftcInsideText, location=_ftcLocation, offset=_ftcHourOffset - ftcTimeFrameOffset, color=_insideColor, show_last=1)
    plotchar(close if isHourFtcOutsidePlot else na, title='isFtcHourOutside', char='', text=_ftcOutsideText, location=_ftcLocation, offset=_ftcHourOffset - ftcTimeFrameOffset, color=color.new(_outsideColor, 0), show_last=1)
    plotshape(close if isHourFtcGreenPlot else na, title='isFtcHourGreen', style=_bullShape, text=_ftcHourText, location=_ftcLocation, offset=_ftcHourOffset - ftcTimeFrameOffset, color=color.new(_bullColor, 0), show_last=1)
    plotshape(close if isHourFtcRedPlot else na, title='isFtcHourRed', style=_bearShape, text=_ftcHourText, location=_ftcLocation, offset=_ftcHourOffset - ftcTimeFrameOffset, color=color.new(_bearColor, 0), show_last=1)
    plotchar(close if isFourHourFtcInsidePlot else na, title='isFtcFourHourInside', char='', text=_ftcInsideText, location=_ftcLocation, offset=_ftcFourHourOffset - ftcTimeFrameOffset, color=_insideColor, show_last=1)
    plotchar(close if isFourHourFtcOutsidePlot else na, title='isFtcFourHourOutside', char='', text=_ftcOutsideText, location=_ftcLocation, offset=_ftcFourHourOffset - ftcTimeFrameOffset, color=color.new(_outsideColor, 0), show_last=1)
    plotshape(close if isFourHourFtcGreenPlot else na, title='isFtcFourHourGreen', style=_bullShape, text=_ftcFourHourText, location=_ftcLocation, offset=_ftcFourHourOffset - ftcTimeFrameOffset, color=color.new(_bullColor, 0), show_last=1)
    plotshape(close if isFourHourFtcRedPlot else na, title='isFtcFourHourRed', style=_bearShape, text=_ftcFourHourText, location=_ftcLocation, offset=_ftcFourHourOffset - ftcTimeFrameOffset, color=color.new(_bearColor, 0), show_last=1)
    plotchar(close if isDayFtcInsidePlot else na, title='isFtcDayInside', char='', text=_ftcInsideText, location=_ftcLocation, offset=_ftcDayOffset - ftcTimeFrameOffset, color=_insideColor, show_last=1)
    plotchar(close if isDayFtcOutsidePlot else na, title='isFtcDayOutside', char='', text=_ftcOutsideText, location=_ftcLocation, offset=_ftcDayOffset - ftcTimeFrameOffset, color=color.new(_outsideColor, 0), show_last=1)
    plotshape(close if isDayFtcGreenPlot else na, title='isFtcDayGreen', style=_bullShape, text=_ftcDayText, location=_ftcLocation, offset=_ftcDayOffset - ftcTimeFrameOffset, color=color.new(_bullColor, 0), show_last=1)
    plotshape(close if isDayFtcRedPlot else na, title='isFtcDayRed', style=_bearShape, text=_ftcDayText, location=_ftcLocation, offset=_ftcDayOffset - ftcTimeFrameOffset, color=color.new(_bearColor, 0), show_last=1)
    plotchar(close if isWeekFtcInsidePlot else na, title='isFtcWeekInside', char='', text=_ftcInsideText, location=_ftcLocation, offset=_ftcWeekOffset - ftcTimeFrameOffset, color=_insideColor, show_last=1)
    plotchar(close if isWeekFtcOutsidePlot else na, title='isFtcWeekOutside', char='', text=_ftcOutsideText, location=_ftcLocation, offset=_ftcWeekOffset - ftcTimeFrameOffset, color=color.new(_outsideColor, 0), show_last=1)
    plotshape(close if isWeekFtcGreenPlot else na, title='isFtcWeekGreen', style=_bullShape, text=_ftcWeekText, location=_ftcLocation, offset=_ftcWeekOffset - ftcTimeFrameOffset, color=color.new(_bullColor, 0), show_last=1)
    plotshape(close if isWeekFtcRedPlot else na, title='isFtcWeekRed', style=_bearShape, text=_ftcWeekText, location=_ftcLocation, offset=_ftcWeekOffset - ftcTimeFrameOffset, color=color.new(_bearColor, 0), show_last=1)
    plotchar(close if isMonthFtcInsidePlot else na, title='isFtcMonthInside', char='', text=_ftcInsideText, location=_ftcLocation, offset=_ftcMonthOffset - ftcTimeFrameOffset, color=_insideColor, show_last=1)
    plotchar(close if isMonthFtcOutsidePlot else na, title='isFtcMonthOutside', char='', text=_ftcOutsideText, location=_ftcLocation, offset=_ftcMonthOffset - ftcTimeFrameOffset, color=color.new(_outsideColor, 0), show_last=1)
    plotshape(close if isMonthFtcGreenPlot else na, title='isFtcMonthGreen', style=_bullShape, text=_ftcMonthText, location=_ftcLocation, offset=_ftcMonthOffset - ftcTimeFrameOffset, color=color.new(_bullColor, 0), show_last=1)
    plotshape(close if isMonthFtcRedPlot else na, title='isFtcMonthRed', style=_bearShape, text=_ftcMonthText, location=_ftcLocation, offset=_ftcMonthOffset - ftcTimeFrameOffset, color=color.new(_bearColor, 0), show_last=1)
    plotchar(close if isQuarterFtcInsidePlot else na, title='isFtcQuarterInside', char='', text=_ftcInsideText, location=_ftcLocation, offset=_ftcQuarterOffset - ftcTimeFrameOffset, color=_insideColor, show_last=1)
    plotchar(close if isQuarterFtcOutsidePlot else na, title='isFtcQuarterOutside', char='', text=_ftcOutsideText, location=_ftcLocation, offset=_ftcQuarterOffset - ftcTimeFrameOffset, color=color.new(_outsideColor, 0), show_last=1)
    plotshape(close if isQuarterFtcGreenPlot else na, title='isFtcQuarterGreen', style=_bullShape, text=_ftcQuarterText, location=_ftcLocation, offset=_ftcQuarterOffset - ftcTimeFrameOffset, color=color.new(_bullColor, 0), show_last=1)
    plotshape(close if isQuarterFtcRedPlot else na, title='isFtcQuarterRed', style=_bearShape, text=_ftcQuarterText, location=_ftcLocation, offset=_ftcQuarterOffset - ftcTimeFrameOffset, color=color.new(_bearColor, 0), show_last=1)
    plotshape(is222BearishContinuation, title=_is222BearishContinuation, style=_stratComboStyle, color=color.new(_bearColor, 0), location=_stratComboLocation, text=_is222BearishContinuation, textcolor=color.new(_bearColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is222BullishContinuation, title=_is222BullishContinuation, style=_stratComboStyle, color=color.new(_bullColor, 0), location=_stratComboLocation, text=_is222BullishContinuation, textcolor=color.new(_bullColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is212BearishContinuationMeasuredMove, title=_is212BearishContinuationMeasuredMove, style=_stratComboStyle, color=color.new(_bearColor, 0), location=_stratComboLocation, text=_is212BearishContinuationMeasuredMove, textcolor=color.new(_bearColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is212BullishContinuationMeasuredMove, title=_is212BullishContinuationMeasuredMove, style=_stratComboStyle, color=color.new(_bullColor, 0), location=_stratComboLocation, text=_is212BullishContinuationMeasuredMove, textcolor=color.new(_bullColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is22BearishReversal, title=_is22BearishReversal, style=_stratComboStyle, color=color.new(_bearColor, 0), location=_stratComboLocation, text=_is22BearishReversal, textcolor=color.new(_bearColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is22BullishReversal, title=_is22BullishReversal, style=_stratComboStyle, color=color.new(_bullColor, 0), location=_stratComboLocation, text=_is22BullishReversal, textcolor=color.new(_bullColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is212BearishReversal, title=_is212BearishReversal, style=_stratComboStyle, color=color.new(_bearColor, 0), location=_stratComboLocation, text=_is212BearishReversal, textcolor=color.new(_bearColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is212BullishReversal, title=_is212BullishReversal, style=_stratComboStyle, color=color.new(_bullColor, 0), location=_stratComboLocation, text=_is212BullishReversal, textcolor=color.new(_bullColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is322BearishReversal, title=_is322BearishReversal, style=_stratComboStyle, color=color.new(_bearColor, 0), location=_stratComboLocation, text=_is322BearishReversal, textcolor=color.new(_bearColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is322BullishReversal, title=_is322BullishReversal, style=_stratComboStyle, color=color.new(_bullColor, 0), location=_stratComboLocation, text=_is322BullishReversal, textcolor=color.new(_bullColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is32BearishReversal, title=_is32BearishReversal, style=_stratComboStyle, color=color.new(_bearColor, 0), location=_stratComboLocation, text=_is32BearishReversal, textcolor=color.new(_bearColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is32BullishReversal, title=_is32BullishReversal, style=_stratComboStyle, color=color.new(_bullColor, 0), location=_stratComboLocation, text=_is32BullishReversal, textcolor=color.new(_bullColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is312BearishReversal, title=_is312BearishReversal, style=_stratComboStyle, color=color.new(_bearColor, 0), location=_stratComboLocation, text=_is312BearishReversal, textcolor=color.new(_bearColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is312BullishReversal, title=_is312BullishReversal, style=_stratComboStyle, color=color.new(_bullColor, 0), location=_stratComboLocation, text=_is312BullishReversal, textcolor=color.new(_bullColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is122BearishRevStratReversal, title=_is122BearishRevStratReversal, style=_stratComboStyle, color=color.new(_bearColor, 0), location=_stratComboLocation, text=_is122BearishRevStratReversal, textcolor=color.new(_bearColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is122BullishRevStratReversal, title=_is122BullishRevStratReversal, style=_stratComboStyle, color=color.new(_bullColor, 0), location=_stratComboLocation, text=_is122BullishRevStratReversal, textcolor=color.new(_bullColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is2222BearishRandyJackson, title=_is2222BearishRandyJackson, style=_stratComboStyle, color=color.new(_bearColor, 0), location=_stratComboLocation, text=_is2222BearishRandyJackson, textcolor=color.new(_bearColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is2222BullishRandyJackson, title=_is2222BullishRandyJackson, style=_stratComboStyle, color=color.new(_bullColor, 0), location=_stratComboLocation, text=_is2222BullishRandyJackson, textcolor=color.new(_bullColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is3BearishRevStratReversal, title=_is3BearishRevStratReversal, style=_stratComboStyle, color=color.new(_bearColor, 0), location=_stratComboLocation, text=_is3BearishRevStratReversal, textcolor=color.new(_bearColor, 0), offset=_stratComboOffset, show_last=1)
    plotshape(is3BullishRevStratReversal, title=_is3BullishRevStratReversal, style=_stratComboStyle, color=color.new(_bullColor, 0), location=_stratComboLocation, text=_is3BullishRevStratReversal, textcolor=color.new(_bullColor, 0), offset=_stratComboOffset, show_last=1)
    if _isPrevDayHighLineActive and (timeframe.isintraday or timeframe.isdaily):
        highDayLine: Series = line.new(x1=timeDayValue[1], y1=highDayValue[1], x2=time, xloc=xloc.bar_time, y2=highDayValue[1], extend=extend.right, color=_prevDayHighColor, style=line.style_dashed, width=1)
        line.delete(highDayLine[1])
    if _isPrevDayLowLineActive and (timeframe.isintraday or timeframe.isdaily):
        lowDayLine: Series = line.new(x1=timeDayValue[1], y1=lowDayValue[1], x2=time, xloc=xloc.bar_time, y2=lowDayValue[1], extend=extend.right, color=_prevDayLowColor, style=line.style_dashed, width=1)
        line.delete(lowDayLine[1])
    if _isPrevWeekHighLineActive and (timeframe.isintraday or timeframe.isdaily or timeframe.isweekly):
        highWeekLine: Series = line.new(x1=timeDayValue[1], y1=highWeekValue[1], x2=time, xloc=xloc.bar_time, y2=highWeekValue[1], extend=extend.right, color=_prevWeekHighColor, style=line.style_dashed, width=1)
        line.delete(highWeekLine[1])
    if _isPrevWeekLowLineActive and (timeframe.isintraday or timeframe.isdaily or timeframe.isweekly):
        lowWeekLine: Series = line.new(x1=timeDayValue[1], y1=lowWeekValue[1], x2=time, xloc=xloc.bar_time, y2=lowWeekValue[1], extend=extend.right, color=_prevWeekLowColor, style=line.style_dashed, width=1)
        line.delete(lowWeekLine[1])
    debugText = 'PrevDay H|L: ' + string.tostring(highDayValue[1], '#.##') + '|' + string.tostring(lowDayValue[1], '#.##') + '\n PrevWeek H|L: ' + string.tostring(highWeekValue[1], '#.##') + '|' + string.tostring(lowWeekValue[1], '#.##')
    if _isDebugLabelActive:
        debugLabel: Series = label.new(x=bar_index, y=close - close * 0.003, textalign=text.align_left, text=debugText, yloc=yloc.price, color=color.black, textcolor=color.white, size=size.normal, style=label.style_label_upper_left)
        label.delete(debugLabel[1])


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
