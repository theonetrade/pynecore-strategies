"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    array, bar_index, barcolor, box, close, color, high, input, line,
    location, low, math, na, open, plot, plotshape, script, shape, size, ta, text, volume
)
from pynecore.types import Box, Persistent, Series


@script.indicator('Super OrderBlock / FVG / BoS Tools by makuchaku & eFe', overlay=True, max_boxes_count=500, max_lines_count=500)
def main(
    plotOB=input.bool(defval=True, title='Plot OB', group='Order Blocks'),
    obBullColor=input.color(defval=color.new(color.green, 90), title='Bullish OB Color', inline='Set Custom Color', group='Order Blocks'),
    obBearColor=input.color(defval=color.new(color.red, 90), title='Bearish OB Color', inline='Set Custom Color', group='Order Blocks'),
    obBoxBorder=input.string(defval=line.style_solid, title='OB Box Border Style', options=(line.style_dashed, line.style_dotted, line.style_solid), group='Order Blocks', tooltip='To disable border, set Border Width below to 0'),
    obBorderTransparency=input.int(defval=80, title='OB Border Box Transparency', minval=0, maxval=100, group='Order Blocks'),
    obMaxBoxSet=input.int(defval=10, title='Maximum OB Box Displayed', minval=1, maxval=100, group='Order Blocks', tooltip='Minimum = 1, Maximum = 100'),
    filterMitOB=input.bool(defval=False, title='Custom Color Mitigated OB', group='Order Blocks'),
    mitOBColor=input.color(defval=color.new(color.gray, 90), title='Mitigated OB Color', group='Order Blocks', inline='Set Custom Color Mit OB', tooltip='Set Transparency to 0 to make mitigated OB disappear'),
    plotFVG=input.bool(defval=True, title='Plot FVG', group='Fair Value Gaps', inline='FVG sets'),
    plotStructureBreakingFVG=input.bool(defval=True, title='Plot Structure Breaking FVG', group='Fair Value Gaps', inline='FVG sets'),
    fvgBullColor=input.color(defval=color.new(color.black, 90), title='Bullish FVG Color', inline='Set Custom Color', group='Fair Value Gaps'),
    fvgBearColor=input.color(defval=color.new(color.black, 90), title='Bearish FVG Color', inline='Set Custom Color', group='Fair Value Gaps'),
    fvgStructBreakingColor=input.color(defval=color.new(color.blue, 90), title='Structure Breaking FVG Color', inline='Set Custom Color', group='Fair Value Gaps'),
    fvgBoxBorder=input.string(defval=line.style_solid, title='FVG Box Border Style', options=(line.style_dashed, line.style_dotted, line.style_solid), group='Fair Value Gaps', tooltip='To disable border, set Border Width below to 0'),
    fvgBorderTransparency=input.int(defval=80, title='FVG Border Box Transparency', minval=0, maxval=100, group='Fair Value Gaps'),
    fvgMaxBoxSet=input.int(defval=10, title='Maximum FVG Box Displayed', minval=1, maxval=100, group='Fair Value Gaps', tooltip='Minimum = 1, Maximum = 100'),
    filterMitFVG=input.bool(defval=False, title='Custom Color Mitigated FVG', group='Fair Value Gaps'),
    mitFVGColor=input.color(defval=color.new(color.gray, 90), title='Mitigated FVG Color', group='Fair Value Gaps', inline='Set Custom Color Mit FVG', tooltip='Set Transparency to 0 to make mitigated FVG disappear'),
    plotRJB=input.bool(defval=False, title='Plot RJB', group='Rejection Blocks', inline='RJB sets'),
    rjbBullColor=input.color(defval=color.new(color.green, 90), title='Bullish RJB Color', inline='Set Custom Color', group='Rejection Blocks'),
    rjbBearColor=input.color(defval=color.new(color.red, 90), title='Bearish RJB Color', inline='Set Custom Color', group='Rejection Blocks'),
    rjbBoxBorder=input.string(defval=line.style_solid, title='RJB Box Border Style', options=(line.style_dashed, line.style_dotted, line.style_solid), group='Rejection Blocks', tooltip='To disable border, set Border Width below to 0'),
    rjbBorderTransparency=input.int(defval=80, title='RJB Border Box Transparency', minval=0, maxval=100, group='Rejection Blocks'),
    rjbMaxBoxSet=input.int(defval=10, title='Maximum RJB Box Displayed', minval=1, maxval=100, group='Rejection Blocks', tooltip='Minimum = 1, Maximum = 100'),
    filterMitRJB=input.bool(defval=False, title='Custom Color Mitigated RJB', group='Rejection Blocks'),
    mitRJBColor=input.color(defval=color.new(color.gray, 90), title='Mitigated RJB Color', group='Rejection Blocks', inline='Set Custom Color Mit RJB', tooltip='Set to 100 to make mitigated RJB disappear'),
    plotPVT=input.bool(defval=True, title='Plot Pivots', group='Pivots'),
    pivotLookup=input.int(defval=1, minval=1, maxval=5, title='Pivot Lookup', group='Pivots', tooltip='Minimum = 1, Maximum = 5'),
    pvtTopColor=input.color(defval=color.new(color.silver, 0), title='Pivot Top Color', group='Pivots', inline='PVT Color'),
    pvtBottomColor=input.color(defval=color.new(color.silver, 0), title='Pivot Bottom Color', group='Pivots', inline='PVT Color'),
    plotBOS=input.bool(defval=False, title='Plot BoS', group='Crossovers', inline='BOS sets'),
    useHighLowForBullishBoS=input.bool(defval=False, title='Use High/Low for Bullish BoS (for Bearish setup)', group='Crossovers'),
    useHighLowForBearishBoS=input.bool(defval=False, title='Use High/Low for Bearish BoS (for Bullish setup)', group='Crossovers'),
    bosBoxFlag=input.bool(title='BoS Box Length Manually', defval=False, group='Crossovers', tooltip='If activated the BoS Boxes will not extend unitl crossed by price. Instead will extend by the amount of bars choosen in the "Set BoS Box Length Manually" option'),
    bosBoxLength=input.int(title='BoS Box Length Manually', defval=3, minval=1, maxval=5, group='Crossovers', inline='BoS Boxes', tooltip='If "Set BoS Box Length Manually" is marked, choose by how many bars. Minimum = 1, Maximum = 5'),
    bosBullColor=input.color(defval=color.new(color.green, 90), title='Bullish BoS Color', inline='Set Custom Color', group='Crossovers'),
    bosBearColor=input.color(defval=color.new(color.red, 90), title='Bearish BoS Color', inline='Set Custom Color', group='Crossovers'),
    bosBoxBorder=input.string(defval=line.style_solid, title='BoS Box Border Style', options=(line.style_dashed, line.style_dotted, line.style_solid), group='Crossovers', tooltip='To disable border, set Border Width below to 0'),
    bosBorderTransparency=input.int(defval=80, title='BoS Border Box Transparency', minval=0, maxval=100, group='Crossovers'),
    bosMaxBoxSet=input.int(defval=10, title='Maximum BoS Box Displayed', minval=1, maxval=100, group='Crossovers', tooltip='Minimum = 1, Maximum = 100'),
    plotHVB=input.bool(defval=True, title='Plot HVB', group='High Volume Bar', tooltip='A candle where the average volume is higher than last few bars.'),
    hvbBullColor=input.color(defval=color.green, title='Bullish HVB Color', inline='Set Custom Color', group='High Volume Bar'),
    hvbBearColor=input.color(defval=color.red, title='Bearish HVB Color', inline='Set Custom Color', group='High Volume Bar'),
    hvbEMAPeriod=input.int(defval=12, minval=1, title='Volume EMA Period', group='High Volume Bar'),
    hvbMultiplier=input.float(defval=1.5, title='Volume Multiplier', minval=1, maxval=100, group='High Volume Bar'),
    plotPPDD=input.bool(defval=True, title='Plot PPDD OB\'s', group='Qualitative indicators', tooltip='Premium Premium Discount Discount (PPDD) is an OB formed after liquidity sweep. It will show up by default as a triangle (Bull ▲ / Bear ▼). Also PPDD1 (by deafult maked with a x-cross ⨯) which is a weak OB formed after liquidity sweep, that fails to completely engulf the high/low, but closes beyond the trapped candles open price.'),
    ppddBullColor=input.color(defval=color.new(color.green, 0), title='Bullish PPDD OB\'s Color', group='Qualitative indicators', inline='PPDD Color'),
    ppddBearColor=input.color(defval=color.new(color.red, 0), title='Bearish PPDD OB\'s Color', group='Qualitative indicators', inline='PPDD Color'),
    plotOBFVG=input.bool(defval=True, title='Plot Stacked OB+FVG', group='Qualitative indicators', tooltip='Marks the candle (default with a diamond ◆) when an OB & FVG are stacked, showing momentum'),
    obfvgBullColor=input.color(defval=color.new(color.green, 0), title='Bullish Stacked OB+FVG Color', group='Qualitative indicators', inline='OBFVG Color'),
    obfvgBearColor=input.color(defval=color.new(color.red, 0), title='Bearish Stacked OB+FVG Color', group='Qualitative indicators', inline='OBFVG Color'),
    plotLabelOB=input.bool(defval=True, title='Plot OB Label', inline='OB label', group='Label Options'),
    obLabelColor=input.color(defval=color.gray, title='Color', inline='OB label', group='Label Options'),
    obLabelSize=input.string(defval=size.tiny, title='Size', options=(size.huge, size.large, size.small, size.tiny, size.auto, size.normal), inline='OB label', group='Label Options'),
    plotLabelFVG=input.bool(defval=True, title='Plot FVG Label', inline='FVG label', group='Label Options'),
    fvgLabelColor=input.color(defval=color.gray, title='Color', inline='FVG label', group='Label Options'),
    fvgLabelSize=input.string(defval=size.tiny, title='Size', options=(size.huge, size.large, size.small, size.tiny, size.auto, size.normal), inline='FVG label', group='Label Options'),
    plotLabelRJB=input.bool(defval=True, title='Plot RJB Label', inline='RJB label', group='Label Options'),
    rjbLabelColor=input.color(defval=color.gray, title='Color', inline='RJB label', group='Label Options'),
    rjbLabelSize=input.string(defval=size.tiny, title='Size', options=(size.huge, size.large, size.small, size.tiny, size.auto, size.normal), inline='RJB label', group='Label Options'),
    plotLabelBOS=input.bool(defval=True, title='Plot BoS Label', inline='BOS label', group='Label Options'),
    bosLabelColor=input.color(defval=color.gray, title='Color', inline='BOS label', group='Label Options'),
    bosLabelSize=input.string(defval=size.tiny, title='Size', options=(size.huge, size.large, size.small, size.tiny, size.auto, size.normal), inline='BOS label', group='Label Options')
):
    _ob: Persistent[int] = 1
    _fvg: Persistent[int] = 2
    _rjb: Persistent[int] = 3
    _bos: Persistent[int] = 4
    _obLabel: Persistent[str] = 'OB'
    _fvgLabel: Persistent[str] = 'FVG'
    _rjbLabel: Persistent[str] = 'RJB'
    _bosLabel: Persistent[str] = 'BoS'
    _plus: Persistent[str] = '+'
    _minus: Persistent[str] = '-'
    _empty: Persistent[str] = ''
    _bearBoxesOB: Persistent[list[Box]] = array.new_box()
    _bullBoxesOB: Persistent[list[Box]] = array.new_box()
    _bearBoxesFVG: Persistent[list[Box]] = array.new_box()
    _bullBoxesFVG: Persistent[list[Box]] = array.new_box()
    _bearBoxesRJB: Persistent[list[Box]] = array.new_box()
    _bullBoxesRJB: Persistent[list[Box]] = array.new_box()
    _bearBoxesBOS: Persistent[list[Box]] = array.new_box()
    _bullBoxesBOS: Persistent[list[Box]] = array.new_box()
    def isUp(index):
        return close[index] > open[index]

    def isDown(index):
        return close[index] < open[index]

    def isObUp(index):
        isUp_1 = isUp(index)
        return isDown(index + 1) and isUp_1 and (close[index] > high[index + 1])

    def isObDown(index):
        isDown_1 = isDown(index)
        return isUp(index + 1) and isDown_1 and (close[index] < low[index + 1])

    def isFvgUp(index):
        return low[index] > high[index + 2]

    def isFvgDown(index):
        return high[index] < low[index + 2]

    def _controlBox(_boxes, _high, _low, _type):
        __block_result__ = na
        if array.size(_boxes) > 0:
            __block_result_1__ = na
            for i in pine_range(array.size(_boxes) - 1, 0, 1):
                _box = array.get(_boxes, i)
                _boxLow = box.get_bottom(_box)
                _boxHigh = box.get_top(_box)
                _boxRight = box.get_right(_box)
                __block_result_2__ = na
                if bosBoxFlag and _type == _bos:
                    __block_result_3__ = na
                    if na or (bar_index + bosBoxLength - 1 == _boxRight and (not (_high > _boxLow and _low < _boxLow or (_high > _boxHigh and _low < _boxHigh)))):
                        __block_result_3__ = box.set_right(_box, bar_index + bosBoxLength - 1)
                    __block_result_2__ = __block_result_3__
                elif filterMitOB and _type == _ob or (filterMitFVG and _type == _fvg) or (filterMitRJB and _type == _rjb):
                    __block_result_4__ = na
                    if na or (bar_index == _boxRight and (not (_high > _boxLow and _low < _boxLow or (_high > _boxHigh and _low < _boxHigh)))):
                        __block_result_4__ = box.set_right(_box, bar_index + 1)
                    else:
                        __block_result_5__ = na
                        if _type == _ob:
                            box.set_bgcolor(_box, mitOBColor)
                            __block_result_5__ = box.set_border_color(_box, mitOBColor)
                        elif _type == _fvg:
                            box.set_bgcolor(_box, mitFVGColor)
                            __block_result_5__ = box.set_border_color(_box, mitFVGColor)
                        elif _type == _rjb:
                            box.set_bgcolor(_box, mitRJBColor)
                            __block_result_5__ = box.set_border_color(_box, mitRJBColor)
                        __block_result_4__ = __block_result_5__
                    __block_result_2__ = __block_result_4__
                else:
                    __block_result_6__ = na
                    if na or (bar_index == _boxRight and (not (_high > _boxLow and _low < _boxLow or (_high > _boxHigh and _low < _boxHigh)))):
                        __block_result_6__ = box.set_right(_box, bar_index + 1)
                    __block_result_2__ = __block_result_6__
                __block_result_1__ = __block_result_2__
            __block_result__ = __block_result_1__
        return __block_result__

    hih = ta.pivothigh(high, pivotLookup, pivotLookup)
    lol = ta.pivotlow(low, pivotLookup, pivotLookup)
    top: Series = ta.valuewhen(cast_bool(hih), high[pivotLookup], 0)
    bottom: Series = ta.valuewhen(cast_bool(lol), low[pivotLookup], 0)
    plot(top, offset=-pivotLookup, linewidth=1, color=na if top != top[1] else pvtTopColor if plotPVT else na, title='Pivot Top')
    plot(bottom, offset=-pivotLookup, linewidth=1, color=na if bottom != bottom[1] else pvtBottomColor if plotPVT else na, title='Pivot Bottom')
    if isObUp(1) and plotOB:
        _bullboxOB = box.new(left=bar_index - 2, top=high[2], right=bar_index, bottom=math.min(low[2], low[1]), border_color=color.new(obBullColor, obBorderTransparency), border_style=obBoxBorder, border_width=1, bgcolor=obBullColor, text=_obLabel + _plus if plotLabelOB else _empty, text_halign=text.align_right, text_valign=text.align_bottom, text_size=obLabelSize, text_color=obLabelColor)
        if array.size(_bullBoxesOB) > obMaxBoxSet:
            box.delete(array.shift(_bullBoxesOB))
        array.push(_bullBoxesOB, _bullboxOB)
    if isObDown(1) and plotOB:
        _bearboxOB = box.new(left=bar_index - 2, top=math.max(high[2], high[1]), right=bar_index, bottom=low[2], border_color=color.new(obBearColor, obBorderTransparency), border_style=obBoxBorder, border_width=1, bgcolor=obBearColor, text=_obLabel + _minus if plotLabelOB else _empty, text_halign=text.align_right, text_valign=text.align_bottom, text_size=obLabelSize, text_color=obLabelColor)
        if array.size(_bearBoxesOB) > obMaxBoxSet:
            box.delete(array.shift(_bearBoxesOB))
        array.push(_bearBoxesOB, _bearboxOB)
    if plotOB:
        _controlBox(_bearBoxesOB, high, low, _ob)
        _controlBox(_bullBoxesOB, high, low, _ob)
    if isFvgUp(0):
        _bullboxFVG: Box = na(Box)
        if plotStructureBreakingFVG and close[1] > top and (low[1] < top) and (high[2] < top) and (low > top):
            _bullboxFVG = box.new(left=bar_index - 2, top=low, right=bar_index, bottom=high[2], bgcolor=fvgStructBreakingColor, border_color=color.new(fvgStructBreakingColor, fvgBorderTransparency), border_style=fvgBoxBorder, border_width=1, text=_fvgLabel + _plus if plotLabelFVG else _empty, text_halign=text.align_right, text_valign=text.align_bottom, text_size=fvgLabelSize, text_color=fvgLabelColor)
        elif plotFVG:
            _bullboxFVG = box.new(left=bar_index - 2, top=low, right=bar_index, bottom=high[2], bgcolor=fvgBullColor, border_color=color.new(fvgBullColor, fvgBorderTransparency), border_style=fvgBoxBorder, border_width=1, text=_fvgLabel + _plus if plotLabelFVG else _empty, text_halign=text.align_right, text_valign=text.align_bottom, text_size=fvgLabelSize, text_color=fvgLabelColor)
        if array.size(_bullBoxesFVG) > fvgMaxBoxSet:
            box.delete(array.shift(_bullBoxesFVG))
        array.push(_bullBoxesFVG, _bullboxFVG)
    if isFvgDown(0):
        _bearboxFVG: Box = na(Box)
        if plotStructureBreakingFVG and close[1] < bottom and (high[1] > bottom) and (low[2] > bottom) and (high < bottom):
            _bearboxFVG = box.new(left=bar_index - 2, top=low[2], right=bar_index, bottom=high, bgcolor=fvgStructBreakingColor, border_color=color.new(fvgStructBreakingColor, fvgBorderTransparency), border_style=fvgBoxBorder, border_width=1, text=_fvgLabel + _minus if plotLabelFVG else _empty, text_halign=text.align_right, text_valign=text.align_bottom, text_size=fvgLabelSize, text_color=fvgLabelColor)
        elif plotFVG:
            _bearboxFVG = box.new(left=bar_index - 2, top=low[2], right=bar_index, bottom=high, bgcolor=fvgBearColor, border_color=color.new(fvgBearColor, fvgBorderTransparency), border_style=fvgBoxBorder, border_width=1, text=_fvgLabel + _minus if plotLabelFVG else _empty, text_halign=text.align_right, text_valign=text.align_bottom, text_size=fvgLabelSize, text_color=fvgLabelColor)
        if array.size(_bearBoxesFVG) > fvgMaxBoxSet:
            box.delete(array.shift(_bearBoxesFVG))
        array.push(_bearBoxesFVG, _bearboxFVG)
    if plotFVG or plotStructureBreakingFVG:
        _controlBox(_bearBoxesFVG, high, low, _fvg)
        _controlBox(_bullBoxesFVG, high, low, _fvg)
    if plotRJB:
        isDownRjbObCondition = isObDown(1)
        isDownRjb1 = isDownRjbObCondition and high[1] < close[2] + 0.2 * (high[2] - close[2])
        isDownRjb2 = isDownRjbObCondition and high[1] > high[2]
        if isDownRjb1 and plotRJB:
            _bearboxRJB = box.new(left=bar_index - 2, top=high[2], right=bar_index, bottom=close[2], bgcolor=rjbBearColor, border_color=color.new(rjbBearColor, rjbBorderTransparency), border_style=rjbBoxBorder, border_width=1, text=_rjbLabel + _minus if plotLabelRJB else _empty, text_halign=text.align_right, text_valign=text.align_bottom, text_size=rjbLabelSize, text_color=rjbLabelColor)
            if array.size(_bearBoxesRJB) > rjbMaxBoxSet:
                box.delete(array.shift(_bearBoxesRJB))
            array.push(_bearBoxesRJB, _bearboxRJB)
        if isDownRjb2 and plotRJB:
            _bearboxRJB = box.new(left=bar_index - 1, top=high[1], right=bar_index, bottom=open[1], bgcolor=rjbBearColor, border_color=color.new(rjbBearColor, rjbBorderTransparency), border_style=rjbBoxBorder, border_width=1, text=_rjbLabel + _minus if plotLabelRJB else _empty, text_halign=text.align_right, text_valign=text.align_bottom, text_size=rjbLabelSize, text_color=rjbLabelColor)
            if array.size(_bearBoxesRJB) > rjbMaxBoxSet:
                box.delete(array.shift(_bearBoxesRJB))
            array.push(_bearBoxesRJB, _bearboxRJB)
    if plotRJB:
        isUpRjbObCondition = isObUp(1)
        isUpRjb1 = isUpRjbObCondition and low[1] > close[2] - 0.2 * (close[2] - low[2])
        isUpRjb2 = isUpRjbObCondition and low[1] < low[2]
        if isUpRjb1 and plotRJB:
            _bullboxRJB = box.new(left=bar_index - 2, top=close[2], right=bar_index, bottom=low[2], bgcolor=rjbBullColor, border_color=color.new(rjbBullColor, rjbBorderTransparency), border_style=rjbBoxBorder, border_width=1, text=_rjbLabel + _plus if plotLabelRJB else _empty, text_halign=text.align_right, text_valign=text.align_bottom, text_size=rjbLabelSize, text_color=rjbLabelColor)
            if array.size(_bullBoxesRJB) > rjbMaxBoxSet:
                box.delete(array.shift(_bullBoxesRJB))
            array.push(_bullBoxesRJB, _bullboxRJB)
        if isUpRjb2 and plotRJB:
            _bullboxRJB = box.new(left=bar_index - 1, top=open[1], right=bar_index, bottom=low[1], bgcolor=rjbBullColor, border_color=color.new(rjbBullColor, rjbBorderTransparency), border_style=rjbBoxBorder, border_width=1, text=_rjbLabel + _plus if plotLabelRJB else _empty, text_halign=text.align_right, text_valign=text.align_bottom, text_size=rjbLabelSize, text_color=rjbLabelColor)
            if array.size(_bullBoxesRJB) > rjbMaxBoxSet:
                box.delete(array.shift(_bullBoxesRJB))
            array.push(_bullBoxesRJB, _bullboxRJB)
    if plotRJB:
        _controlBox(_bearBoxesRJB, high, low, _rjb)
        _controlBox(_bullBoxesRJB, high, low, _rjb)
    if plotBOS:
        if ta.crossover(high if useHighLowForBullishBoS else close, top):
            _bullboxBOS = box.new(left=bar_index, top=top, right=bar_index + bosBoxLength if bosBoxFlag else bar_index + 1, bottom=bottom, bgcolor=bosBullColor, border_color=color.new(bosBullColor, bosBorderTransparency), border_style=bosBoxBorder, border_width=1, text=_bosLabel + _plus if plotLabelBOS else _empty, text_halign=text.align_right, text_valign=text.align_bottom, text_size=bosLabelSize, text_color=bosLabelColor)
            if array.size(_bullBoxesBOS) > bosMaxBoxSet:
                box.delete(array.shift(_bullBoxesBOS))
            array.push(_bullBoxesBOS, _bullboxBOS)
    if plotBOS:
        if ta.crossunder(low if useHighLowForBearishBoS else close, bottom):
            _bearboxBOS = box.new(left=bar_index, top=top, right=bar_index + bosBoxLength if bosBoxFlag else bar_index + 1, bottom=bottom, bgcolor=bosBearColor, border_color=color.new(bosBearColor, bosBorderTransparency), border_style=bosBoxBorder, border_width=1, text=_bosLabel + _minus if plotLabelBOS else _empty, text_halign=text.align_right, text_valign=text.align_bottom, text_size=bosLabelSize, text_color=bosLabelColor)
            if array.size(_bearBoxesBOS) > bosMaxBoxSet:
                box.delete(array.shift(_bearBoxesBOS))
            array.push(_bearBoxesBOS, _bearboxBOS)
    if plotBOS:
        _controlBox(_bearBoxesBOS, high, low, _bos)
        _controlBox(_bullBoxesBOS, high, low, _bos)
    isObDown_1 = isObDown(0)
    premiumPremium = plotPPDD and isObDown_1 and (math.max(high, high[1]) > top and close < top or (math.max(high, high[1]) > top[1] and close < top[1]))
    isObUp_1 = isObUp(0)
    discountDiscount = plotPPDD and isObUp_1 and (math.min(low, low[1]) < bottom and close > bottom or (math.min(low, low[1]) < bottom[1] and close > bottom[1]))
    plotshape(premiumPremium, 'Bearish PPDD OB', style=shape.triangledown, location=location.abovebar, color=ppddBearColor, size=size.tiny)
    plotshape(discountDiscount, 'Bullish PPDD OB', style=shape.triangleup, location=location.belowbar, color=ppddBullColor, size=size.tiny)
    isUp_1 = isUp(1)
    isDown_1 = isDown(0)
    premiumPremium1 = plotPPDD and isUp_1 and isDown_1 and (close < open[1]) and (math.max(high, high[1]) > top and close < top or (math.max(high, high[1]) > top[1] and close < top[1])) and (not premiumPremium)
    isDown_2 = isDown(1)
    isUp_2 = isUp(0)
    discountDiscount1 = plotPPDD and isDown_2 and isUp_2 and (close > open[1]) and (math.min(low, low[1]) < bottom and close > bottom or (math.min(low, low[1]) < bottom[1] and close > bottom[1])) and (not discountDiscount)
    plotshape(premiumPremium1, 'Bearish PPDD Weak OB', style=shape.xcross, location=location.abovebar, color=ppddBearColor, size=size.tiny)
    plotshape(discountDiscount1, 'Bullish PPDD Weak OB', style=shape.xcross, location=location.belowbar, color=ppddBullColor, size=size.tiny)
    volEma = ta.ema(volume, hvbEMAPeriod)
    isHighVolume = volume > hvbMultiplier * volEma
    isUp_3 = isUp(0)
    barcolor(hvbBullColor if plotHVB and isUp_3 and isHighVolume else na, title='Bullish HVB')
    isDown_3 = isDown(0)
    barcolor(hvbBearColor if plotHVB and isDown_3 and isHighVolume else na, title='Bearish HVB')
    isFvgDown_1 = isFvgDown(0)
    isObDown_2 = isObDown(1)
    plotshape(plotOBFVG and isFvgDown_1 and isObDown_2, 'Bearish OB+FVG Stack', style=shape.diamond, location=location.abovebar, color=obfvgBearColor, size=size.tiny)
    isFvgUp_1 = isFvgUp(0)
    isObUp_2 = isObUp(1)
    plotshape(plotOBFVG and isFvgUp_1 and isObUp_2, 'Bullish OB+FVG Stack', style=shape.diamond, location=location.belowbar, color=obfvgBullColor, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
