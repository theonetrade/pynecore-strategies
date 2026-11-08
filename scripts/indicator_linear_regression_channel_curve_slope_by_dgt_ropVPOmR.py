"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alert, alertcondition, bar_index, barcolor, barstate, close, color,
    display, extend, format, high, input, label, line, location, low, math, max_bars_back, na, nz,
    open, plot, plotarrow, plotchar, position, script, size, string, syminfo, ta, table, text,
    timeframe, volume, xloc
)
from pynecore.types import NA, Persistent, Series, Table

display__ren__ = display.all - display.status_line
group_linReg: str = 'Linear Regression — 1st Channel'
tooltip_linreg = 'Linear Regression Channel' + '\nBase Line: The line that best fits price over the selected period (Count),' + '\ncalculated using the least-squares method.'
group_linReg2: str = 'Linear Regression — 2nd Channel (HTF)'
tooltip_linreg2 = 'Second Linear Regression Channel — User-Defined Timeframe' + '\n\nWhen enabled, the Linear Regression Channel extends by:' + '\nCount × (Selected Higher Timeframe ÷ Current Timeframe).' + '\n\nLimitations:' + '\n• May exceed the maximum allowed history limit (5000 bars),' + '\n  resulting in: "The study references too many candles in history (5001)".' + '\n  Solution: Reduce Count or select 1H / 4H.' + '\n\n• Lines may not be visible while labels are present.' + '\n  Solution: Scroll left or enable "Shorten Display when TF Extend is enabled".' + '\n\n• Applicable to intraday timeframes only.'
group_linRegC: str = 'Linear Regression Curve'
group_linRegS: str = 'Linear Regression Slope'
group_vol_vol: str = 'Volume / Volatility AddOns'
tooltip_high_volatility = 'High Volatility\n' + 'Detected when the current bar range exceeds ATR × Threshold over the selected period.'
tooltip_volume_spike_sign_of_exhaustion = 'Sign of Exhaustion\n' + 'A volume spike occurs when the current volume exceeds the volume moving average multiplied by the threshold value.'
tooltip_volume_weighted_colored_bars = 'Volume-Weighted Colored Bars\n' + 'Colors bars based on the bar’s volume relative to the volume moving average.'


@script.indicator('Linear Regression Channel / Curve / Slope by DGT', 'LɪɴRᴇɢ ☼☾', True)
def main(
    i_linreg=input.bool(True, 'LinReg1 ⇨ Count', inline='LinReg1', group=group_linReg, tooltip=tooltip_linreg),
    i_linregLength=input.int(200, '', minval=2, maxval=5000, inline='LinReg1', group=group_linReg, display=display__ren__),
    i_linregSrc: Series[float] = input.source(close, '       Source', inline='LinReg1', group=group_linReg, display=display__ren__),
    i_extendLines=input.bool(False, 'Extend Lines       ', inline='Lines', group=group_linReg),
    i_trendColor=input.bool(False, 'Use Trend Colors', inline='Lines', group=group_linReg),
    i_channelLevels=input.string('Levels', 'Level Labels', options=('Levels', 'Levels (Prices)', 'None'), inline='Level', group=group_linReg, display=display__ren__),
    levelTextSize=input.string('Small', '', options=('Small', 'Normal'), inline='Level', group=group_linReg, display=display__ren__),
    levelOffset=input.int(0, 'Offset', minval=0, inline='Level', group=group_linReg, display=display__ren__),
    i_linreg2=input.bool(True, 'LinReg2 ⇨ Count', inline='LinReg2', group=group_linReg2),
    i_linregLength2=input.int(50, '', minval=2, maxval=5000, inline='LinReg2', group=group_linReg2, display=display__ren__),
    i_linregSrc2: Series[float] = input.source(close, '       Source', inline='LinReg2', group=group_linReg2, display=display__ren__),
    i_useTF=input.bool(True, 'LinReg2 ⇨ Extend to User-Defined TF (Intraday Only)', inline='HTF2', group=group_linReg2, tooltip=tooltip_linreg2),
    i_htf_user=input.string('4H', '', options=('1D', '4H', '1H'), inline='HTF2', group=group_linReg2, display=display__ren__),
    i_shorten=input.bool(True, 'LinReg2 ⇨ Shorten Display when TF Extend Enabled', inline='SHORT', group=group_linReg2),
    i_showLast=input.int(500, '', minval=200, inline='SHORT', group=group_linReg2, display=display__ren__),
    i_extendLines2=input.bool(False, 'Extend Lines       ', inline='Lines', group=group_linReg2),
    i_trendColor2=input.bool(False, 'Use Trend Colors', inline='Lines', group=group_linReg2),
    i_channelLevels2=input.string('Levels', 'Level Labels', options=('Levels', 'Levels (Prices)', 'None'), inline='Level', group=group_linReg2, display=display__ren__),
    levelTextSize2=input.string('Small', '', options=('Small', 'Normal'), inline='Level', group=group_linReg2, display=display__ren__),
    levelOffset2=input.int(0, 'Offset', minval=0, inline='Level', group=group_linReg2, display=display__ren__),
    i_lrcolor_m=input.color(color.new('#F44336'), 'Linear Regression Line       ', inline='lrLine', group=group_linReg),
    i_lrstyle_m=input.string('Solid', '', options=('Dashed', 'Dotted', 'Solid'), inline='lrLine', group=group_linReg, display=display__ren__),
    i_lrwidth_m=input.int(3, '', minval=1, inline='lrLine', group=group_linReg, display=display__ren__),
    i_lrshow_1=input.bool(True, 'StdDev', inline='lrLevel_1', group=group_linReg),
    i_lrvalue_1=input.float(1.0, '', minval=0, step=0.1, inline='lrLevel_1', group=group_linReg, display=display__ren__),
    i_lrcolor_1=input.color(color.new('#2196F3'), '', inline='lrLevel_1', group=group_linReg),
    i_lrstyle_1=input.string('Dashed', '', options=('Dashed', 'Dotted', 'Solid'), inline='lrLevel_1', group=group_linReg, display=display__ren__),
    i_lrwidth_1=input.int(1, '', minval=1, inline='lrLevel_1', group=group_linReg, display=display__ren__),
    i_lrshow_2=input.bool(True, 'StdDev', inline='lrLevel_2', group=group_linReg),
    i_lrvalue_2=input.float(2.0, '', minval=1, step=0.1, inline='lrLevel_2', group=group_linReg, display=display__ren__),
    i_lrcolor_2=input.color(color.new('#2196F3'), '', inline='lrLevel_2', group=group_linReg),
    i_lrstyle_2=input.string('Solid', '', options=('Dashed', 'Dotted', 'Solid'), inline='lrLevel_2', group=group_linReg, display=display__ren__),
    i_lrwidth_2=input.int(2, '', minval=1, inline='lrLevel_2', group=group_linReg, display=display__ren__),
    i_lrshow_3=input.bool(True, 'StdDev', inline='lrLevel_3', group=group_linReg),
    i_lrvalue_3=input.float(3.0, '', minval=2, step=0.1, inline='lrLevel_3', group=group_linReg, display=display__ren__),
    i_lrcolor_3=input.color(color.new('#2196F3'), '', inline='lrLevel_3', group=group_linReg),
    i_lrstyle_3=input.string('Dotted', '', options=('Dashed', 'Dotted', 'Solid'), inline='lrLevel_3', group=group_linReg, display=display__ren__),
    i_lrwidth_3=input.int(2, '', minval=1, inline='lrLevel_3', group=group_linReg, display=display__ren__),
    i_2lrcolor_m=input.color(color.new('#FF9800'), 'Linear Regression Line       ', inline='2lrLine', group=group_linReg2),
    i_2lrstyle_m=input.string('Solid', '', options=('Dashed', 'Dotted', 'Solid'), inline='2lrLine', group=group_linReg2, display=display__ren__),
    i_2lrwidth_m=input.int(3, '', minval=1, inline='2lrLine', group=group_linReg2, display=display__ren__),
    i_2lrshow_1=input.bool(True, 'StdDev', inline='2lrLevel_1', group=group_linReg2),
    i_2lrvalue_1=input.float(1.0, '', minval=0, step=0.1, inline='2lrLevel_1', group=group_linReg2, display=display__ren__),
    i_2lrcolor_1=input.color(color.new('#00BCD4'), '', inline='2lrLevel_1', group=group_linReg2),
    i_2lrstyle_1=input.string('Dashed', '', options=('Dashed', 'Dotted', 'Solid'), inline='2lrLevel_1', group=group_linReg2, display=display__ren__),
    i_2lrwidth_1=input.int(1, '', minval=1, inline='2lrLevel_1', group=group_linReg2, display=display__ren__),
    i_2lrshow_2=input.bool(True, 'StdDev', inline='2lrLevel_2', group=group_linReg2),
    i_2lrvalue_2=input.float(2.0, '', minval=1, step=0.1, inline='2lrLevel_2', group=group_linReg2, display=display__ren__),
    i_2lrcolor_2=input.color(color.new('#00BCD4'), '', inline='2lrLevel_2', group=group_linReg2),
    i_2lrstyle_2=input.string('Solid', '', options=('Dashed', 'Dotted', 'Solid'), inline='2lrLevel_2', group=group_linReg2, display=display__ren__),
    i_2lrwidth_2=input.int(2, '', minval=1, inline='2lrLevel_2', group=group_linReg2, display=display__ren__),
    i_2lrshow_3=input.bool(True, 'StdDev', inline='2lrLevel_3', group=group_linReg2),
    i_2lrvalue_3=input.float(3.0, '', minval=2, step=0.1, inline='2lrLevel_3', group=group_linReg2, display=display__ren__),
    i_2lrcolor_3=input.color(color.new('#00BCD4'), '', inline='2lrLevel_3', group=group_linReg2),
    i_2lrstyle_3=input.string('Dotted', '', options=('Dashed', 'Dotted', 'Solid'), inline='2lrLevel_3', group=group_linReg2, display=display__ren__),
    i_2lrwidth_3=input.int(2, '', minval=1, inline='2lrLevel_3', group=group_linReg2, display=display__ren__),
    i_showCurve=input.bool(True, 'Linear Regression Curve      |     Length', inline='Curve', group=group_linRegC),
    i_linregCurveL=input.int(50, '', inline='Curve', group=group_linRegC, display=display__ren__),
    i_lrcolorCurve=input.color(color.new('#872323'), '', inline='Curve', group=group_linRegC),
    i_showCurveBand=input.bool(False, 'Linear Regression Curve Bands           ', inline='Bands', group=group_linRegC),
    i_lrcolorBand1=input.color(color.new('#00897B'), '1', inline='Bands', group=group_linRegC),
    i_lrcolorBand2=input.color(color.new('#00897B'), '2', inline='Bands', group=group_linRegC),
    i_lrcolorBand3=input.color(color.new('#00897B'), '3', inline='Bands', group=group_linRegC),
    i_showCurveBTyp=input.string('StdDev', 'Bands', options=('StdDev', 'ATR'), inline='Bands2', group=group_linRegC, display=display__ren__),
    i_linregCurveBL=input.int(21, '  StdDev', inline='Bands2', group=group_linRegC, display=display__ren__),
    i_linregCurveAL=input.int(13, ' ATR', inline='Bands2', group=group_linRegC, display=display__ren__),
    i_showSlope=input.bool(False, 'Linear Regression Slope  |  Length', inline='Slope', group=group_linRegS),
    i_linregSlopeL=input.int(5, '', inline='Slope', group=group_linRegS, display=display__ren__),
    i_lrcolorSlopeU=input.color(color.new(color.new('#06BAD1'), 50), '', inline='Slope', group=group_linRegS),
    i_lrcolorSlopeD=input.color(color.new(color.new('#F57F17'), 50), '', inline='Slope', group=group_linRegS),
    i_hATRLb=input.bool(False, '⚡', inline='ATR', group=group_vol_vol, tooltip=tooltip_high_volatility),
    __input_71__=input.int(13, 'ATR : Length', inline='ATR', group=group_vol_vol, display=display__ren__),
    __input_72__=input.float(2.718, '    Multiplier', minval=0.1, step=0.1, inline='ATR', group=group_vol_vol, display=display__ren__),
    __input_73__=input.int(89, 'Volume Moving Average Length', group=group_vol_vol, display=display__ren__),
    i_vSpikeLb=input.bool(False, '🚦', inline='SRS1', group=group_vol_vol, tooltip=tooltip_volume_spike_sign_of_exhaustion),
    i_vSpikeThresh=input.float(4.669, 'Volume Spike Threshold                    ', minval=0.1, step=0.1, inline='SRS1', group=group_vol_vol, display=display__ren__),
    i_vwcb=input.bool(True, '', inline='VWC', group=group_vol_vol, tooltip=tooltip_volume_weighted_colored_bars),
    i_vwcbHighThresh=input.float(1.618, 'VWCB Thresholds :  High ', minval=1.0, step=0.1, inline='VWC', group=group_vol_vol, display=display__ren__),
    i_vwcbLowThresh=input.float(0.618, '  Low', minval=0.1, step=0.1, inline='VWC', group=group_vol_vol, display=display__ren__)
):
    def f_calcSlope(_source: Series, _length):
        max_bars_back(_source, 5000)

        __block_result__ = (na, na)
        if not barstate.islast:
            __block_result__ = (NA(float), NA(float))
        else:
            sumX: float = 0.0
            sumY: float = 0.0
            sumXSqr: float = 0.0
            sumXY: float = 0.0

            for i in pine_range(0, _length - 1, 1):
                val = _source[i]
                per = i + 1.0
                sumX = sumX + per
                sumY = sumY + val
                sumXSqr = sumXSqr + per * per
                sumXY = sumXY + val * per

            slope__0000001a__ = (_length * sumXY - sumX * sumY) / (_length * sumXSqr - sumX * sumX)
            intercept__0000001a__ = sumY / _length - slope__0000001a__ * sumX / _length + slope__0000001a__

            __block_result__ = (slope__0000001a__, intercept__0000001a__)
        return __block_result__

    def f_calcDev(_source: Series, _length, _slope, _intercept):
        stdDevAcc: float = 0.0
        periods = _length - 1
        val = _intercept

        for i in pine_range(0, periods, 1):
            price = _source[i]
            price = price - val
            stdDevAcc = stdDevAcc + price * price
            val = val + _slope

        stdDev = math.sqrt(stdDevAcc / periods)
        return stdDev

    slope, intercept = f_calcSlope(i_linregSrc, i_linregLength)
    stdDev = f_calcDev(i_linregSrc, i_linregLength, slope, intercept)
    startPrice = intercept + slope * (i_linregLength - 1)
    endPrice = intercept

    htf_multiplier = 60 if i_htf_user == '1H' else 240 if i_htf_user == '4H' else 1440 if i_htf_user == '1D' else na
    linregLength2 = i_linregLength2 * htf_multiplier / timeframe.multiplier if i_useTF and timeframe.isintraday and (htf_multiplier > timeframe.multiplier) else i_linregLength2

    slope2, intercept2 = f_calcSlope(i_linregSrc2, linregLength2)
    stdDev2 = f_calcDev(i_linregSrc2, linregLength2, slope2, intercept2)
    startPrice2 = intercept2 + slope2 * (i_showLast if i_shorten and i_useTF and (i_showLast < linregLength2) else linregLength2 - 1)
    endPrice2 = intercept2

    def f_crossingLevel(_current: Series, _level):
        return _level > _current and _level < _current[1] or (_level < _current and _level > _current[1])

    def f_drawLabel(_index, _price, _txt, _txtColor, _style, _align, _lrc, _tooltip, size__ren__, extend__ren__):
        id: Persistent = label.new(_index, _price, _txt, textcolor=_txtColor, style=_style, textalign=_align, color=color.new('#00000000'), tooltip=_tooltip, size=size__ren__)
        label.set_xy(id, _index, _price)
        label.set_textcolor(id, _txtColor)
        label.set_text(id, _txt + '\n\n' if extend__ren__ else _txt)
        return label.set_tooltip(id, _tooltip)

    def f_drawLine(_iStart, _pStart, _iEnd, _pEnd, _color, _width, _style, _extend):
        style = line.style_solid if _style == 'Solid' else line.style_dotted if _style == 'Dotted' else line.style_dashed if _style == 'Dashed' else line.style_arrow_right

        linReg: Persistent = line.new(_iStart, _pStart, _iEnd, _pEnd, xloc.bar_index, extend.right if _extend else extend.none, _color, style, _width)
        line.set_xy1(linReg, _iStart, _pStart)
        line.set_xy2(linReg, _iEnd, _pEnd)
        return line.set_color(linReg, _color)

    def processLinRegLevel(_show, _level, _colorL, _widthL, _styleL, _linReg, _which, extend__ren__):
        __block_result_1__ = na
        if _show and _linReg:
            pStart = startPrice if _which else startPrice2
            pEnd = endPrice if _which else endPrice2
            dev__0000004a__ = stdDev if _which else stdDev2
            trendColor = i_trendColor if _which else i_trendColor2
            channelLevels = i_channelLevels if _which else i_channelLevels2
            textSize = levelTextSize if _which else levelTextSize2
            offset = levelOffset if _which else levelOffset2

            length = i_linregLength if _which else i_showLast if i_shorten and i_useTF and (i_showLast < linregLength2) else linregLength2
            lrColor = (color.red if pStart > pEnd else color.green) if trendColor else _colorL

            f_drawLine(bar_index - length + 1, pStart + _level * dev__0000004a__, bar_index, pEnd + _level * dev__0000004a__, lrColor, _widthL, _styleL, extend__ren__)
            f_drawLine(bar_index - length + 1, pStart - _level * dev__0000004a__, bar_index, pEnd - _level * dev__0000004a__, lrColor, _widthL, _styleL, extend__ren__)

            lbl = '1' if _which else '2'

            if channelLevels != 'None':
                f_drawLabel(bar_index + offset, pEnd + _level * dev__0000004a__, 'SD ' + string.tostring(_level) + ' R' + lbl + (' (' + string.tostring(pEnd + _level * dev__0000004a__, format.mintick) + ')' if channelLevels == 'Levels (Prices)' else ''), lrColor, label.style_label_left, text.align_left, True, string.tostring(pEnd + _level * dev__0000004a__, format.mintick), size.small if textSize == 'Small' else size.normal, extend__ren__)
                f_drawLabel(bar_index + offset, pEnd - _level * dev__0000004a__, 'SD ' + string.tostring(_level) + ' S' + lbl + (' (' + string.tostring(pEnd - _level * dev__0000004a__, format.mintick) + ')' if channelLevels == 'Levels (Prices)' else ''), lrColor, label.style_label_left, text.align_left, True, string.tostring(pEnd - _level * dev__0000004a__, format.mintick), size.small if textSize == 'Small' else size.normal, extend__ren__)

                if offset > 9:
                    f_drawLine(bar_index + 3, pEnd + _level * dev__0000004a__, bar_index + offset, pEnd + _level * dev__0000004a__, lrColor, 1, 'Arrow', False)
                    f_drawLine(bar_index + 3, pEnd - _level * dev__0000004a__, bar_index + offset, pEnd - _level * dev__0000004a__, lrColor, 1, 'Arrow', False)

            if f_crossingLevel(close, pEnd + _level * dev__0000004a__):
                alert('LɪɴRᴇɢ | ' + syminfo.ticker + ' — Price crossed LR' + lbl + ' Upper Band (SD ' + string.tostring(_level) + ') @ ' + string.tostring(pEnd + _level * dev__0000004a__, format.mintick))

            __block_result_2__ = na
            if f_crossingLevel(close, pEnd - _level * dev__0000004a__):
                __block_result_2__ = alert('LɪɴRᴇɢ | ' + syminfo.ticker + ' — Price crossed LR' + lbl + ' Lower Band (SD ' + string.tostring(_level) + ') @ ' + string.tostring(pEnd - _level * dev__0000004a__, format.mintick))
            __block_result_1__ = __block_result_2__
        return __block_result_1__

    if i_linreg:
        f_drawLine(bar_index - i_linregLength + 1, startPrice, bar_index, endPrice, (color.red if startPrice > endPrice else color.green) if i_trendColor else i_lrcolor_m, i_lrwidth_m, i_lrstyle_m, i_extendLines)

        if i_channelLevels != 'None':
            f_drawLabel(bar_index + levelOffset, endPrice, 'LRL 1ST' + (' (' + string.tostring(endPrice, format.mintick) + ')' if i_channelLevels == 'Levels (Prices)' else ''), (color.red if startPrice > endPrice else color.green) if i_trendColor else i_lrcolor_m, label.style_label_left, text.align_left, True, string.tostring(endPrice, format.mintick), size.small if levelTextSize == 'Small' else size.normal, i_extendLines)

            if levelOffset > 9:
                f_drawLine(bar_index + 3, endPrice, bar_index + levelOffset, endPrice, i_lrcolor_m, 1, 'Arrow', False)

        if f_crossingLevel(close, endPrice):
            alert('LɪɴRᴇɢ | ' + syminfo.ticker + ' — Price crossed LR1 Base Line @ ' + string.tostring(endPrice, format.mintick))
    processLinRegLevel(i_lrshow_1, i_lrvalue_1, i_lrcolor_1, i_lrwidth_1, i_lrstyle_1, i_linreg, True, i_extendLines)
    processLinRegLevel(i_lrshow_2, i_lrvalue_2, i_lrcolor_2, i_lrwidth_2, i_lrstyle_2, i_linreg, True, i_extendLines)
    processLinRegLevel(i_lrshow_3, i_lrvalue_3, i_lrcolor_3, i_lrwidth_3, i_lrstyle_3, i_linreg, True, i_extendLines)

    if i_linreg2:
        f_drawLine(bar_index - (i_showLast if i_shorten and i_useTF and (i_showLast < linregLength2) else linregLength2) + 1, startPrice2, bar_index, endPrice2, (color.red if startPrice2 > endPrice2 else color.green) if i_trendColor2 else i_2lrcolor_m, i_2lrwidth_m, i_2lrstyle_m, i_extendLines2)

        if i_channelLevels2 != 'None':
            f_drawLabel(bar_index + levelOffset2, endPrice2, 'LRL 2ND' + (' (' + string.tostring(endPrice2, format.mintick) + ')' if i_channelLevels2 == 'Levels (Prices)' else ''), (color.red if startPrice2 > endPrice2 else color.green) if i_trendColor2 else i_2lrcolor_m, label.style_label_left, text.align_left, True, string.tostring(endPrice2, format.mintick), size.small if levelTextSize2 == 'Small' else size.normal, i_extendLines2)

            if levelOffset2 > 9:
                f_drawLine(bar_index + 3, endPrice2, bar_index + levelOffset2, endPrice2, i_2lrcolor_m, 1, 'Arrow', False)

        if f_crossingLevel(close, endPrice2):
            alert('LɪɴRᴇɢ | ' + syminfo.ticker + ' — Price crossed LR2 Base Line @ ' + string.tostring(endPrice2, format.mintick))
    processLinRegLevel(i_2lrshow_1, i_2lrvalue_1, i_2lrcolor_1, i_2lrwidth_1, i_2lrstyle_1, i_linreg2, False, i_extendLines2)
    processLinRegLevel(i_2lrshow_2, i_2lrvalue_2, i_2lrcolor_2, i_2lrwidth_2, i_2lrstyle_2, i_linreg2, False, i_extendLines2)
    processLinRegLevel(i_2lrshow_3, i_2lrvalue_3, i_2lrcolor_3, i_2lrwidth_3, i_2lrstyle_3, i_linreg2, False, i_extendLines2)

    def f_lrAlert(_txt, _price):
        return alert('LɪɴRᴇɢ | ' + syminfo.ticker + ' — ' + _txt + ' @ ' + string.tostring(_price, format.mintick))

    if i_linreg and i_linreg2:
        if f_crossingLevel(endPrice, endPrice2):
            f_lrAlert('LR1 Base crossed LR2 Base Line', endPrice2)

        if f_crossingLevel(endPrice, endPrice2 + i_2lrvalue_1 * stdDev2):
            f_lrAlert('LR1 Base crossed LR2 Upper Band (SD ' + string.tostring(i_2lrvalue_1) + ')', endPrice2 + i_2lrvalue_1 * stdDev2)

        if f_crossingLevel(endPrice, endPrice2 + i_2lrvalue_2 * stdDev2):
            f_lrAlert('LR1 Base crossed LR2 Upper Band (SD ' + string.tostring(i_2lrvalue_2) + ')', endPrice2 + i_2lrvalue_2 * stdDev2)

        if f_crossingLevel(endPrice, endPrice2 + i_2lrvalue_3 * stdDev2):
            f_lrAlert('LR1 Base crossed LR2 Upper Band (SD ' + string.tostring(i_2lrvalue_3) + ')', endPrice2 + i_2lrvalue_3 * stdDev2)

        if f_crossingLevel(endPrice, endPrice2 - i_2lrvalue_1 * stdDev2):
            f_lrAlert('LR1 Base crossed LR2 Lower Band (SD ' + string.tostring(i_2lrvalue_1) + ')', endPrice2 - i_2lrvalue_1 * stdDev2)

        if f_crossingLevel(endPrice, endPrice2 - i_2lrvalue_2 * stdDev2):
            f_lrAlert('LR1 Base crossed LR2 Lower Band (SD ' + string.tostring(i_2lrvalue_2) + ')', endPrice2 - i_2lrvalue_2 * stdDev2)

        if f_crossingLevel(endPrice, endPrice2 - i_2lrvalue_3 * stdDev2):
            f_lrAlert('LR1 Base crossed LR2 Lower Band (SD ' + string.tostring(i_2lrvalue_3) + ')', endPrice2 - i_2lrvalue_3 * stdDev2)


    dev = ta.stdev(i_linregSrc, i_linregCurveBL) if i_showCurveBTyp == 'StdDev' else ta.atr(i_linregCurveAL)
    lrc = ta.linreg(i_linregSrc, i_linregCurveL, 0)

    plot(lrc if i_showCurve else na, 'LRC', i_lrcolorCurve, 3, show_last=3 * i_linregLength, display=display__ren__)
    plot(lrc + 1 * dev if i_showCurve and i_showCurveBand else na, 'LRC Band StdDev 1', i_lrcolorBand1, 1, show_last=3 * i_linregLength, display=display__ren__)
    plot(lrc - 1 * dev if i_showCurve and i_showCurveBand else na, 'LRC Band StdDev 1', i_lrcolorBand1, 1, show_last=3 * i_linregLength, display=display__ren__)
    plot(lrc + 2 * dev if i_showCurve and i_showCurveBand else na, 'LRC Band StdDev 2', i_lrcolorBand2, 1, show_last=3 * i_linregLength, display=display__ren__)
    plot(lrc - 2 * dev if i_showCurve and i_showCurveBand else na, 'LRC Band StdDev 2', i_lrcolorBand2, 1, show_last=3 * i_linregLength, display=display__ren__)
    plot(lrc + 3 * dev if i_showCurve and i_showCurveBand else na, 'LRC Band StdDev 3', i_lrcolorBand3, 1, show_last=3 * i_linregLength, display=display__ren__)
    plot(lrc - 3 * dev if i_showCurve and i_showCurveBand else na, 'LRC Band StdDev 3', i_lrcolorBand3, 1, show_last=3 * i_linregLength, display=display__ren__)

    plotarrow(ta.correlation(close, bar_index, i_linregSlopeL) * ta.stdev(close, i_linregSlopeL) / ta.stdev(bar_index, i_linregSlopeL) if i_showSlope else na, 'Linear Regression Slope', i_lrcolorSlopeU, i_lrcolorSlopeD, show_last=3 * i_linregLength, display=display__ren__)

    i_weightedATR = ta.atr(__input_71__) * __input_72__

    i_vSMA = ta.sma(nz(volume), __input_73__)


    nzVolume = nz(volume)
    bullCandle = close > open
    bearCandle = close < open
    range_1 = math.abs(high - low)

    exhaustVol = nzVolume > i_vSpikeThresh * i_vSMA
    plotchar(exhaustVol if i_vSpikeLb and cast_bool(nzVolume) else False, 'Exhaustion Bar', '🚦', location.abovebar, size=size.tiny, show_last=3 * i_linregLength, display=display__ren__)
    alertcondition(ta.crossover(nzVolume, i_vSMA * i_vSpikeThresh), 'Volume Spike — Possible Exhaustion', 'LɪɴRᴇɢ | {{exchange}}:{{ticker}} — Unusual volume spike detected, possible exhaustion or climactic move.\nPrice : {{close}}')

    highVolatility = range_1 > i_weightedATR
    plotchar(highVolatility if i_hATRLb else False, 'High Volatile Bar', '⚡', location.belowbar, size=size.tiny, show_last=3 * i_linregLength, display=display__ren__)
    alertcondition(ta.crossover(range_1, i_weightedATR), 'High Volatility — Wide Bar Detected', 'LɪɴRᴇɢ | {{exchange}}:{{ticker}} — Unusually wide bar detected, possible breakout or volatility surge.\nPrice : {{close}}')

    vwcbCol = (color.new('#006400') if bullCandle else color.new('#910000')) if nzVolume > i_vSMA * i_vwcbHighThresh else (color.new('#FF9800') if bearCandle else color.new('#7FFFD4')) if nzVolume < i_vSMA * i_vwcbLowThresh else na

    barcolor(vwcbCol if i_vwcb and cast_bool(nzVolume) else na, title='Volume Weighted Colored Bars', show_last=3 * i_linregLength)

    logo: Persistent[Table] = table.new(position.bottom_right, 1, 1)
    if barstate.islast:
        table.cell(logo, 0, 0, '☼☾  ', text_size=size.normal, text_color=color.teal, tooltip='SoleMare Analytics')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
