"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.lib import (
    alertcondition, barcolor, close, color, fill, format, high, input,
    location, low, math, na, nz, open, plot, plotbar, plotshape, script, shape, ta
)
from pynecore.types import NA, Series


@script.indicator('Bjorgum Reversal', shorttitle='Bj Reversal', format=format.price, precision=4, overlay=True, timeframe='', na_bool=True)
def main(
    long=input.int(title='TSI Long Length', defval=25, group='TSI Inputs'),
    short=input.int(title='TSI Short Length', defval=5, group='TSI Inputs'),
    signal=input.int(title='TSI Signal Length', defval=14, group='TSI Inputs'),
    start=input.float(0.043, minval=0.0, maxval=0.099, title='Start - Default = 2 - Multiplied by .001', group='PSAR Inputs'),
    increment=input.float(0.043, minval=0.0, maxval=0.099, title='Step Setting (Sensitivity) - Default = 2 - Multiplied by .001', group='PSAR Inputs'),
    maximum=input.float(0.34, minval=0.0, maxval=0.99, title='Maximum Step (Sensitivity) - Default = 2 - Multiplied by .01', group='PSAR Inputs'),
    aLength=input.int(5, minval=1, group='T3 MA Lengths'),
    Length=input.int(8, minval=1, group='T3 MA Lengths'),
    bullcol=input.color(color.new('#64B5F6'), title='Bull Trend Color', group='Bar Color'),
    bearcol=input.color(color.new('#EF5350'), title='Bear Trend Color', group='Bar Color'),
    bullrev=input.color(color.new('#FFF176'), title='Bullish Reversal Color', group='Bar Color'),
    bearrev=input.color(color.new('#FFF176'), title='Bearish Reversal Color', group='Bar Color'),
    haover=input.bool(title='Overlays HA bars in place of regular candles. (Must \'mute\' main candles while in use. Toggle \'👁\' symbol next to ticker name to hide candles)', defval=False, group='Heikin-Ashi Bar Overlay'),
    rPrice=input.bool(title='Real Price Line - Displays \'real close\' level', defval=False, group='Heikin-Ashi Bar Overlay')
):
    price = close
    def double_smooth(src, long, short):
        fist_smooth = ta.ema(src, long)
        return ta.ema(fist_smooth, short)

    pc = ta.change(price)
    double_smoothed_pc = double_smooth(pc, long, short)
    double_smoothed_abs_pc = double_smooth(math.abs(pc), long, short)
    tsi_value: Series = 100 * (double_smoothed_pc / double_smoothed_abs_pc)
    ema_1 = ta.ema(tsi_value, signal)
    data = tsi_value > tsi_value[1] and tsi_value < ema_1
    ema_2 = ta.ema(tsi_value, signal)
    dtat = tsi_value < tsi_value[1] and tsi_value > ema_2
    plotshape(data, style=shape.triangleup, location=location.belowbar, color=color.new(color.new('#17FF00'), 0), title='Curl Up')
    plotshape(dtat, style=shape.triangledown, location=location.abovebar, color=color.new(color.new('#FFEB3B'), 0), title='Curl Down')
    startCalc = start
    incrementCalc = increment
    maximumCalc = maximum
    sarUp = ta.sar(startCalc, incrementCalc, maximumCalc)
    sarDown = ta.sar(startCalc, incrementCalc, maximumCalc)
    colUp = color.new('#64B5F6') if close >= sarDown else na
    colDown = color.new('#EF5350') if close <= sarUp else na
    plot(sarUp if cast_bool(sarUp) else na, title='Up Trending SAR', style=plot.style_circles, linewidth=1, color=colUp)
    plot(sarDown if cast_bool(sarDown) else na, title='Down Trending SAR', style=plot.style_circles, linewidth=1, color=colDown)
    AxPrice = close
    axe1 = ta.ema(AxPrice, aLength)
    axe2 = ta.ema(axe1, aLength)
    axe3 = ta.ema(axe2, aLength)
    axe4 = ta.ema(axe3, aLength)
    axe5 = ta.ema(axe4, aLength)
    axe6 = ta.ema(axe5, aLength)
    ab: float = 0.7
    ac1 = -ab * ab * ab
    ac2 = 3 * ab * ab + 3 * ab * ab * ab
    ac3 = -6 * ab * ab - 3 * ab - 3 * ab * ab * ab
    ac4 = 1 + 3 * ab + ab * ab * ab + 3 * ab * ab
    anT3Average: Series = ac1 * axe6 + ac2 * axe5 + ac3 * axe4 + ac4 * axe3
    colOne = anT3Average > anT3Average[1]
    colTwo = anT3Average < anT3Average[1]
    color2 = color.new('#64B5F6') if colOne else color.new('#EF5350') if colTwo else na
    p2 = plot(anT3Average, color=color2, title='T3 Fast')
    xPrice = close
    xe1 = ta.ema(xPrice, Length)
    xe2 = ta.ema(xe1, Length)
    xe3 = ta.ema(xe2, Length)
    xe4 = ta.ema(xe3, Length)
    xe5 = ta.ema(xe4, Length)
    xe6 = ta.ema(xe5, Length)
    b: float = 0.7
    c1 = -b * b * b
    c2 = 3 * b * b + 3 * b * b * b
    c3 = -6 * b * b - 3 * b - 3 * b * b * b
    c4 = 1 + 3 * b + b * b * b + 3 * b * b
    nT3Average: Series = c1 * xe6 + c2 * xe5 + c3 * xe4 + c4 * xe3
    upCol = nT3Average > nT3Average[1]
    downCol = nT3Average < nT3Average[1]
    myColor = color.new('#64B5F6') if upCol else color.new('#EF5350') if downCol else na
    p1 = plot(nT3Average, color=myColor, title='T3 Slow')
    fillData = nT3Average < anT3Average
    fillDtat = nT3Average > anT3Average
    fillCol = color.new('#64B5F6') if fillData else color.new('#EF5350') if fillDtat else na
    fill(p1, p2, color=color.new(fillCol, 80), title='T3 Fill')
    haClose: Series = (open + high + low + close) / 4
    haOpen: Series = NA(float)
    haOpen = (open + close) / 2 if na(haOpen[1]) else (nz(haOpen[1]) + nz(haClose[1])) / 2
    haHigh = math.max(high, math.max(haOpen, haClose))
    haLow = math.min(low, math.min(haOpen, haClose))
    uc = close > nT3Average and anT3Average >= nT3Average
    dc = close < nT3Average and anT3Average <= nT3Average
    dr = close < nT3Average and anT3Average >= nT3Average
    ur = close > nT3Average and anT3Average <= nT3Average
    hauc = haClose > nT3Average and anT3Average >= nT3Average
    hadc = haClose < nT3Average and anT3Average <= nT3Average
    hadr = haClose < nT3Average and anT3Average >= nT3Average
    haur = haClose > nT3Average and anT3Average <= nT3Average
    hadu = haClose >= haOpen
    hadd = haClose < haOpen
    hadefval = bullcol if hadu else bearcol if hadd else na
    iff_1 = bullrev if ur else na
    iff_2 = bearrev if dr else iff_1
    iff_3 = bearcol if dc else iff_2
    barColor = bullcol if uc else iff_3
    iff_4 = bullrev if haur else hadefval
    iff_5 = bearrev if hadr else iff_4
    iff_6 = bearcol if hadc else iff_5
    habarColor = bullcol if hauc else iff_6
    barcolor(color=barColor)
    plotbar(haOpen, haHigh, haLow, haClose, title='Heikin-Ashi', editable=False, color=habarColor if haover else na if True else hadefval)
    plot(close, trackprice=True if rPrice else na, offset=-9999, editable=False, color=habarColor)
    c = ta.cross(close, nT3Average)
    alertcondition(c, title='Close crosses T3', message='Reversal candle is forming!')
    d = ta.cross(nT3Average, anT3Average)
    alertcondition(d, title='T3 crossing T3', message='A new trend may be forming!')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
