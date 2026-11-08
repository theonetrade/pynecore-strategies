"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, array, bar_index, close, color, high, input, label, line,
    location, low, na, open, plotshape, script, size, ta, yloc
)
from pynecore.types import Label, Line, Persistent, Series


@script.indicator('Sweep institutional', overlay=True, max_lines_count=500, max_labels_count=500, na_bool=True)
def main(
    cooldownPeriod=input.int(10, title='Cooldown Period', minval=0, group='Settings'),
    showSwing=input.bool(True, title='Show Swings?', inline='s_1', group='Swing Detaction'),
    swingClr=input.color(color.new(color.black, 0), title='', inline='s_1', group='Swing Detaction'),
    bullWidth=input.int(1, title='Line Width:', group='Bullish Sweep'),
    bullStyle=input.string('Dashed', title='Line Style:', options=('Solid', 'Dotted', 'Dashed'), group='Bullish Sweep'),
    bullColor=input.color(color.new(color.teal, 0), title='Bullish Color:', group='Bullish Sweep'),
    bearWidth=input.int(1, title='Line Width:', group='Bearish Sweep'),
    bearStyle=input.string('Dashed', title='Line Style:', options=('Solid', 'Dotted', 'Dashed'), group='Bearish Sweep'),
    bearColor=input.color(color.new(color.maroon, 0), title='Bearish Color:', group='Bearish Sweep')
):
    lbLeft: int = 20
    lbRight: int = 20
    def lineStyle(s):
        __block_result__ = na
        if s == 'Solid':
            __block_result__ = line.style_solid
        elif s == 'Dotted':
            __block_result__ = line.style_dotted
        else:
            __block_result__ = line.style_dashed
        return __block_result__

    bullSignalIndex: Persistent[int] = 0
    bearSignalIndex: Persistent[int] = 0
    bullLine: Persistent[Line] = na(Line)
    bearLine: Persistent[Line] = na(Line)
    highLine: Persistent[Line] = na(Line)
    lowLine: Persistent[Line] = na(Line)
    swingHighLbl: Persistent[Label] = na(Label)
    swingLowLbl: Persistent[Label] = na(Label)
    swingHighLblTxt: Persistent[Label] = na(Label)
    swingLowLblTxt: Persistent[Label] = na(Label)
    swingLowVal: Persistent[float] = na(float)
    swingHighVal: Persistent[float] = na(float)
    pLow = ta.pivotlow(low, lbLeft, lbRight)
    pHigh = ta.pivothigh(high, lbLeft, lbRight)
    pLowVal: Series = ta.valuewhen(not na(pLow), low[lbRight], 0)
    pHighVal: Series = ta.valuewhen(not na(pHigh), high[lbRight], 0)
    prevLowIndex = ta.valuewhen(not na(pLow), bar_index[lbRight], 0)
    prevHighIndex = ta.valuewhen(not na(pHigh), bar_index[lbRight], 0)
    lp = ta.lowest(low, lbLeft)
    hp = ta.highest(high, lbLeft)
    highestClose = ta.highest(close, lbLeft)
    lowestClose = ta.lowest(close, lbLeft)
    bullishSFP: Series = low < pLowVal and close > pLowVal and (open > pLowVal) and (low == lp) and (lowestClose >= pLowVal)
    bearishSFP: Series = high > pHighVal and close < pHighVal and (open < pHighVal) and (high == hp) and (highestClose <= pHighVal)
    bullCond = bullishSFP[3] and close > pLowVal and (close[1] > pLowVal[1]) and (close[2] > pLowVal[2]) and (bar_index >= bullSignalIndex + cooldownPeriod)
    bearCond = bearishSFP[3] and close < pHighVal and (close[1] < pHighVal[1]) and (close[2] < pHighVal[2]) and (bar_index >= bearSignalIndex + cooldownPeriod)
    swingLowCounter: Persistent[int] = 0
    swingHighCounter: Persistent[int] = 0
    isSwingLowCheck: Persistent[bool] = False
    isSwingHighCheck: Persistent[bool] = False
    stopPrintingLow: Persistent[bool] = False
    stopPrintingHigh: Persistent[bool] = False
    if high < swingLowVal and isSwingLowCheck:
        swingLowCounter = swingLowCounter + 1
    if low > swingHighVal and isSwingHighCheck:
        swingHighCounter = swingHighCounter + 1
    if ta.crossunder(close, swingLowVal) and isSwingLowCheck == False:
        isSwingLowCheck = True
        swingLowCounter = 1
    if ta.crossover(close, swingHighVal) and isSwingHighCheck == False:
        isSwingHighCheck = True
        swingHighCounter = 1
    if swingLowCounter == 5 and isSwingLowCheck:
        stopPrintingLow = True
        isSwingLowCheck = False
        line.set_x2(lowLine, bar_index[4])
    if swingHighCounter == 5 and isSwingHighCheck:
        stopPrintingHigh = True
        isSwingHighCheck = False
        line.set_x2(highLine, bar_index[4])
    if bullCond:
        bullSignalIndex = bar_index
        bullLine = line.new(prevLowIndex, pLowVal, bar_index - 3, pLowVal, color=bullColor, width=bullWidth, style=lineStyle(bullStyle))
    if bearCond:
        bearSignalIndex = bar_index
        bearLine = line.new(prevHighIndex, pHighVal, bar_index - 3, pHighVal, color=bearColor, width=bearWidth, style=lineStyle(bearStyle))
    swingHighArr: Persistent[list[Label]] = array.new_label(0)
    swingHighTextArr: Persistent[list[Label]] = array.new_label(0)
    swingLowArr: Persistent[list[Label]] = array.new_label(0)
    swingLowTextArr: Persistent[list[Label]] = array.new_label(0)
    if array.size(swingHighArr) >= 3:
        label.delete(array.shift(swingHighArr))
        label.delete(array.shift(swingHighTextArr))
    if array.size(swingLowArr) >= 3:
        label.delete(array.shift(swingLowArr))
        label.delete(array.shift(swingLowTextArr))
    if showSwing:
        if stopPrintingHigh == False:
            line.set_x2(highLine, bar_index + 5)
        if stopPrintingLow == False:
            line.set_x2(lowLine, bar_index + 5)
    if showSwing and (not na(pHigh)) and (bearishSFP[lbRight] == False):
        stopPrintingHigh = False
        swingHighVal = high[lbRight]
        line.delete(highLine)
        highLine = line.new(bar_index[lbRight], high[lbRight], bar_index + 10, high[lbRight], color=swingClr, width=2)
        swingHighLbl = label.new(bar_index[lbRight], high[lbRight], text='', yloc=yloc.abovebar, color=swingClr, textcolor=swingClr, style=label.style_triangledown, size=size.auto)
        swingHighLblTxt = label.new(bar_index[lbRight], high[lbRight], text='Swing\nH', yloc=yloc.abovebar, color=swingClr, textcolor=swingClr, style=label.style_none, size=size.small)
        array.push(swingHighArr, swingHighLbl)
        array.push(swingHighTextArr, swingHighLblTxt)
    if showSwing and (not na(pLow)) and (bullishSFP[lbRight] == False):
        stopPrintingLow = False
        swingLowVal = low[lbRight]
        line.delete(lowLine)
        lowLine = line.new(bar_index[lbRight], low[lbRight], bar_index + 10, low[lbRight], color=swingClr, width=2)
        swingLowLbl = label.new(bar_index[lbRight], low[lbRight], text='', yloc=yloc.belowbar, color=swingClr, textcolor=swingClr, style=label.style_triangleup, size=size.auto)
        swingLowLblTxt = label.new(bar_index[lbRight], low[lbRight], text='Swing\nL', yloc=yloc.belowbar, color=swingClr, textcolor=swingClr, style=label.style_none, size=size.small)
        array.push(swingLowArr, swingLowLbl)
        array.push(swingLowTextArr, swingLowLblTxt)
    plotshape(bullCond, text='Sweep', color=bullColor, textcolor=bullColor, location=location.belowbar, offset=-3)
    plotshape(bearCond, text='Sweep', color=bearColor, textcolor=bearColor, location=location.abovebar, offset=-3)
    alertcondition(bullishSFP, title='Bullish Sweep', message='{{ticker}} Bullish Sweep, Price:{{close}}')
    alertcondition(bearishSFP, title='Bearish Sweep', message='{{ticker}} Bearish Sweep, Price:{{close}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
