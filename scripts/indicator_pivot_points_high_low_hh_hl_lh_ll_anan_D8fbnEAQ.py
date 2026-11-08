"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, close, color, fixnan, format, high, input,
    label, last_bar_index, location, low, na, nz, open, plot, plotshape, script, shape, size,
    string, ta, yloc
)
from pynecore.types import Series

srcParams: str = 'Pivot Source | Left Length | Right Length'
lvlDisplay: str = 'Pivots Levels'
markDisplay: str = 'Pivots Markers'
valDisplay: str = 'Pivots Values'
settings: str = 'Others'


@script.indicator(title='Pivot Points High Low (HH/HL/LH/LL) [Anan] ', shorttitle='Pivots HL [Anan]', overlay=True, max_labels_count=500)
def main(
    srcH: Series[float] = input.source(high, title='High', inline='Pivot High', group=srcParams),
    leftLenH=input.int(title='', defval=4, minval=0, inline='Pivot High', group=srcParams),
    rightLenH=input.int(title='', defval=2, minval=0, inline='Pivot High', group=srcParams),
    colorH=input.color(title='', defval=color.new(color.teal, 50), inline='Pivot High', group=srcParams),
    srcL: Series[float] = input.source(low, title='Low', inline='Pivot Low', group=srcParams),
    leftLenL=input.int(title='', defval=4, minval=0, inline='Pivot Low', group=srcParams),
    rightLenL=input.int(title='', defval=2, minval=0, inline='Pivot Low', group=srcParams),
    colorL=input.color(title='', defval=color.new(color.red, 50), inline='Pivot Low', group=srcParams),
    showlevelhh=input.bool(True, 'Higher High', inline='1', group=lvlDisplay),
    showlevellh=input.bool(True, 'Lower High', inline='1', group=lvlDisplay),
    showlevelhl=input.bool(True, 'Higher Low', inline='1', group=lvlDisplay),
    showlevelll=input.bool(True, 'Lower Low', inline='1', group=lvlDisplay),
    showhh=input.bool(True, 'Higher High', inline='1', group=markDisplay),
    showlh=input.bool(True, 'Lower High', inline='1', group=markDisplay),
    showhl=input.bool(True, 'Higher Low', inline='1', group=markDisplay),
    showll=input.bool(True, 'Lower Low', inline='1', group=markDisplay),
    showpricehh=input.bool(True, 'Higher High', inline='1', group=valDisplay),
    showpricelh=input.bool(True, 'Lower High', inline='1', group=valDisplay),
    showpricehl=input.bool(True, 'Higher Low', inline='1', group=valDisplay),
    showpricell=input.bool(True, 'Lower Low', inline='1', group=valDisplay),
    maxBarsBack=input.int(0, 'Maximum Bars to Display (0 = All)', minval=0, group=settings),
    maxLvlLen=input.int(0, minval=0, title='Maximum S/R Level Extension Length (0 = Max)', group=settings),
    ShowChannel=input.bool(False, title='Show Levels as a Fractal Chaos Channel', group=settings),
    showCL=input.bool(defval=False, title='Show Avg Pivot High Low ', group=settings),
    ShowFB=input.bool(True, title='Show fractal Break out/down symbols', group=settings)
):
    ph = ta.pivothigh(srcH, leftLenH, rightLenH)
    pl = ta.pivotlow(srcL, leftLenL, rightLenL)

    ph_value = srcH[rightLenH]
    pl_value = srcL[rightLenL]

    valuewhen_1 = ta.valuewhen(not na(ph), ph_value, 1)
    valuewhen_2 = ta.valuewhen(not na(ph), ph_value, 0)
    higherhigh = na if na(ph) else ph if valuewhen_1 < valuewhen_2 else na
    lowerhigh = na if na(ph) else ph if valuewhen_1 > valuewhen_2 else na

    valuewhen_3 = ta.valuewhen(not na(pl), pl_value, 1)
    valuewhen_4 = ta.valuewhen(not na(pl), pl_value, 0)
    higherlow = na if na(pl) else pl if valuewhen_3 < valuewhen_4 else na
    lowerlow = na if na(pl) else pl if valuewhen_3 > valuewhen_4 else na

    def isInDisplayRange():
        return maxBarsBack == 0 or bar_index > last_bar_index - maxBarsBack

    def drawLabel(_offset, _pivot, _style, _yloc, _color):
        __block_result__ = na
        if not na(_pivot) and isInDisplayRange():
            __block_result__ = label.new(bar_index[_offset], _pivot, text='[' + string.tostring(_pivot, format.mintick) + ']', style=_style, yloc=_yloc, color=_color, textcolor=_color)
        return __block_result__

    drawLabel(rightLenH, higherhigh if showpricehh else na, label.style_none, yloc.abovebar, colorH)
    drawLabel(rightLenH, higherlow if showpricehl else na, label.style_none, yloc.belowbar, colorL)
    drawLabel(rightLenH, lowerhigh if showpricelh else na, label.style_none, yloc.abovebar, colorH)
    drawLabel(rightLenH, lowerlow if showpricell else na, label.style_none, yloc.belowbar, colorL)

    plotshape(higherhigh if showhh and isInDisplayRange() else na, title='HH', style=shape.triangledown, location=location.abovebar, color=colorH, text='HH', textcolor=colorH, offset=-rightLenH)
    plotshape(higherlow if showhl and isInDisplayRange() else na, title='HL', style=shape.triangleup, location=location.belowbar, color=colorL, text='HL', textcolor=colorL, offset=-rightLenH)
    plotshape(lowerhigh if showlh and isInDisplayRange() else na, title='LH', style=shape.triangledown, location=location.abovebar, color=colorH, text='LH', textcolor=colorH, offset=-rightLenL)
    plotshape(lowerlow if showll and isInDisplayRange() else na, title='LL', style=shape.triangleup, location=location.belowbar, color=colorL, text='LL', textcolor=colorL, offset=-rightLenL)

    pivot_avg = (fixnan(ph) + fixnan(pl)) / 2
    plot(pivot_avg if showCL and isInDisplayRange() else na, title='H+L /2', style=plot.style_stepline, color=colorH if close > pivot_avg else colorL)

    countH: Series[int] = 0
    countL: Series[int] = 0
    countH = nz(countH[1]) + 1 if na(ph) else 0
    countL = nz(countL[1]) + 1 if na(pl) else 0

    pvtH: Series[float] = 0.0
    pvtL: Series[float] = 0.0
    pvtH = pvtH[1] if na(ph) else ph_value
    pvtL = pvtL[1] if na(pl) else pl_value

    HpC = na if pvtH != pvtH[1] else colorH
    LpC = na if pvtL != pvtL[1] else colorL

    pvtHighToShow: Series[float] = 0.0
    pvtLowToShow: Series[float] = 0.0

    if showlevelhh and showlevellh:
        pvtHighToShow = pvtH
    elif showlevelhh and (not showlevellh):
        pvtHighToShow = pvtHighToShow[1] if na(higherhigh) else ph_value
    elif not showlevelhh and showlevellh:
        pvtHighToShow = pvtHighToShow[1] if na(lowerhigh) else ph_value
    else:
        pvtHighToShow = na

    if showlevelhl and showlevelll:
        pvtLowToShow = pvtL
    elif showlevelhl and (not showlevelll):
        pvtLowToShow = pvtLowToShow[1] if na(higherlow) else pl_value
    elif not showlevelhl and showlevelll:
        pvtLowToShow = pvtLowToShow[1] if na(lowerlow) else pl_value
    else:
        pvtLowToShow = na

    HpC_filtered = na if pvtHighToShow != pvtHighToShow[1] else colorH
    LpC_filtered = na if pvtLowToShow != pvtLowToShow[1] else colorL

    plot(pvtHighToShow if not ShowChannel and (maxLvlLen == 0 or countH < maxLvlLen) and (showlevelhh or showlevellh) and isInDisplayRange() else na, color=HpC_filtered, offset=-rightLenH, title='Top Levels HH,LH', style=plot.style_circles)
    plot(pvtLowToShow if not ShowChannel and (maxLvlLen == 0 or countL < maxLvlLen) and (showlevelhl or showlevelll) and isInDisplayRange() else na, color=LpC_filtered, offset=-rightLenL, title='Bottom Levels LL,HL', style=plot.style_circles)

    plot(pvtHighToShow if ShowChannel and (showlevelhh or showlevellh) and isInDisplayRange() else na, color=colorH, style=plot.style_stepline, title='Top Chaos Channel', offset=-rightLenH)
    plot(pvtLowToShow if ShowChannel and (showlevelhl or showlevelll) and isInDisplayRange() else na, color=colorL, style=plot.style_stepline, title='Bottom Chaos Channel', offset=-rightLenL)

    buy: bool = False
    sell: bool = False
    buy = close > pvtH and open <= pvtH
    sell = close < pvtL and open >= pvtL

    plotshape(1 if ShowFB and buy and isInDisplayRange() else na, title='Breakout Bar', text='↑↑', style=shape.triangleup, location=location.belowbar, color=colorH, textcolor=colorH, size=size.auto, editable=True)
    plotshape(-1 if ShowFB and sell and isInDisplayRange() else na, title='Breakdown Bar', text='↓↓', style=shape.triangledown, location=location.abovebar, color=colorL, textcolor=colorL, size=size.auto, editable=True)

    alertcondition(buy or sell, title='Fractal Break Arrow', message='Alert')
    alertcondition(buy, title='Fractal Break Long', message='Long')
    alertcondition(sell, title='Fractal Break Short', message='Short')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
