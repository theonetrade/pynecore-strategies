"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, box, chart, close, color, high, input, label, line, location,
    low, math, na, open, plotchar, script, size, string, ta, volume
)
from pynecore.types import Box, Color, NA, Persistent, PersistentSeries, Series


@script.indicator('Support and Resistance (High Volume Boxes) [ChartPrime]', shorttitle='SR Breaks and Retests [ChartPrime]', overlay=True, max_boxes_count=50, na_bool=True)
def main(
    lookbackPeriod=input.int(20, 'Lookback Period', minval=1, group='Settings'),
    vol_len=input.int(2, 'Delta Volume Filter Length', tooltip='Higher input, will filter low volume boxes', group='Settings'),
    box_withd=input.float(1, 'Adjust Box Width', maxval=1000, minval=0, step=0.1)
):
    def upAndDownVolume():
        posVol: float = 0.0
        negVol: float = 0.0
        isBuyVolume: Persistent[bool] = True
        if close > open:
            isBuyVolume = True
        elif close < open:
            isBuyVolume = False
        if isBuyVolume:
            posVol = posVol + volume
        else:
            negVol = negVol - volume
        return posVol + negVol

    def calcSupportResistance(src, lookbackPeriod):
        Vol = upAndDownVolume()
        vol_hi = ta.highest(Vol / 2.5, vol_len)
        vol_lo = ta.lowest(Vol / 2.5, vol_len)
        supportLevel: Persistent[float] = na(float)
        supportLevel_1: Persistent[float] = na(float)
        resistanceLevel: Persistent[float] = na(float)
        resistanceLevel_1: Persistent[float] = na(float)
        sup: Persistent[Box] = na(Box)
        res: Persistent[Box] = na(Box)
        res_color: Persistent[Color] = na(Color)
        sup_color: Persistent[Color] = na(Color)
        multi: Persistent[float] = na(float)
        brekout_res: Persistent[bool] = na(bool)
        brekout_sup: Persistent[bool] = na(bool)
        res_holds: Persistent[bool] = na(bool)
        sup_holds: Persistent[bool] = na(bool)
        pivotHigh = ta.pivothigh(src, lookbackPeriod, lookbackPeriod)
        pivotLow = ta.pivotlow(src, lookbackPeriod, lookbackPeriod)
        atr = ta.atr(200)
        withd = atr * box_withd
        if not na(pivotLow) and Vol > vol_hi:
            supportLevel = pivotLow
            supportLevel_1 = supportLevel - withd
            topLeft = chart.point.from_index(bar_index - lookbackPeriod, supportLevel)
            bottomRight = chart.point.from_index(bar_index, supportLevel_1)
            sup_color = color.from_gradient(Vol, 0, ta.highest(Vol, 25), NA(Color), color.new(color.green, 30))
            sup = box.new(top_left=topLeft, bottom_right=bottomRight, border_color=color.green, border_width=1, bgcolor=sup_color, text='Vol: ' + string.tostring(math.round(Vol, 2)), text_color=chart.fg_color, text_size=size.small)
        if not na(pivotHigh) and Vol < vol_lo:
            resistanceLevel = pivotHigh
            resistanceLevel_1 = resistanceLevel + withd
            topLeft = chart.point.from_index(bar_index - lookbackPeriod, resistanceLevel)
            bottomRight = chart.point.from_index(bar_index, resistanceLevel_1)
            res_color = color.from_gradient(Vol, ta.lowest(Vol, 25), 0, color.new(color.red, 30), NA(Color))
            res = box.new(top_left=topLeft, bottom_right=bottomRight, border_color=color.red, border_width=1, bgcolor=res_color, text='Vol: ' + string.tostring(math.round(Vol, 2)), text_color=chart.fg_color, text_size=size.small)
        box.set_right(sup, bar_index + 1)
        box.set_right(res, bar_index + 1)
        brekout_res = ta.crossover(low, resistanceLevel_1)
        res_holds = ta.crossunder(high, resistanceLevel)
        sup_holds = ta.crossover(low, supportLevel)
        brekout_sup = ta.crossunder(high, supportLevel_1)
        if brekout_sup:
            box.set_bgcolor(sup, color.new(color.red, 80))
            box.set_border_color(sup, color.red)
            box.set_border_style(sup, line.style_dashed)
        if sup_holds:
            box.set_bgcolor(sup, sup_color)
            box.set_border_color(sup, color.green)
            box.set_border_style(sup, line.style_solid)
        if brekout_res:
            box.set_bgcolor(res, color.new(color.green, 80))
            box.set_border_color(res, color.new(color.green, 0))
            box.set_border_style(res, line.style_dashed)
        if res_holds:
            box.set_bgcolor(res, res_color)
            box.set_border_color(res, color.new(color.red, 0))
            box.set_border_style(res, line.style_solid)
        return (supportLevel, resistanceLevel, brekout_res, res_holds, sup_holds, brekout_sup)

    supportLevel: Series
    resistanceLevel: Series
    supportLevel, resistanceLevel, brekout_res, res_holds, sup_holds, brekout_sup = calcSupportResistance(close, lookbackPeriod)
    res_is_sup: PersistentSeries[bool] = na(bool)
    sup_is_res: PersistentSeries[bool] = na(bool)
    if brekout_res:
        res_is_sup = True
    elif res_holds:
        res_is_sup = False
    if brekout_sup:
        sup_is_res = True
    elif sup_holds:
        sup_is_res = False
    plotchar(res_holds, 'Resistance Holds', '◆', color=color.new('#E92929'), size=size.tiny, location=location.abovebar, offset=-1)
    plotchar(sup_holds, 'Support Holds', '◆', color=color.new('#20CA26'), size=size.tiny, location=location.belowbar, offset=-1)
    plotchar(brekout_res and res_is_sup[1], 'Resistance as Support Holds', '◆', color=color.new('#20CA26'), size=size.tiny, location=location.belowbar, offset=-1)
    plotchar(brekout_sup and sup_is_res[1], 'Support as Resistance Holds', '◆', color=color.new('#E92929'), size=size.tiny, location=location.abovebar, offset=-1)
    if brekout_sup and (not sup_is_res[1]):
        label.new(bar_index[1], supportLevel[1], text='Break Sup', style=label.style_label_down, color=color.new('#7E1E1E'), textcolor=chart.fg_color, size=size.small)
    if brekout_res and (not res_is_sup[1]):
        label.new(bar_index[1], resistanceLevel[1], text='Break Res', style=label.style_label_up, color=color.new('#2B6D2D'), textcolor=chart.fg_color, size=size.small)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
