"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    bar_index, chart, close, color, high, input, label, line, location, low,
    math, max_bars_back, na, plot, plotshape, script, shape, size, string, ta
)
from pynecore.types import Color, Line, Persistent, PersistentSeries, Series

NN: str = 'Disabled'
AB: str = 'Point A - Point B'
AC: str = 'Point A - Current bar'


@script.indicator('Trend Lines [LuxAlgo]', shorttitle='LuxAlgo - Trend Lines', max_lines_count=500, max_labels_count=500, overlay=True)
def main(
    length=input.int(50, minval=2, group='Swings'),
    toggle=input.string(NN, 'Check breaks between:', options=(AB, AC, NN), group='Trendline validation'),
    source=input.string('close', 'source (breaks)', options=('close', 'H/L'), group='Trendline validation'),
    count=input.int(3, 'Minimal bars', minval=0, group='Trendline breaks', tooltip='Uninterrupted Trendline for at least x bars'),
    showA=input.bool(True, 'show Angles', group='Angles'),
    ratio=input.float(3, 'Ratio X-Y axis', step=0.1, group='Angles'),
    anglA=input.float(0.1, 'Only Trendlines between:', minval=0.1, inline='angle', group='Angles'),
    anglB=input.float(90, ' - ', minval=0.1, inline='angle', group='Angles'),
    upCss=input.color(color.new('#2962FF'), 'Up', group='Colours'),
    dnCss=input.color(color.new('#F23645'), 'Down', group='Colours')
):
    phx1: Persistent[int] = na(int)
    phslope: Persistent[float] = na(float)
    phy1: Persistent[float] = na(float)
    upper: PersistentSeries[float] = na(float)
    plotH: Persistent[float] = na(float)
    isOnH: Persistent[bool] = False
    plx1: Persistent[int] = na(int)
    plslope: Persistent[float] = na(float)
    ply1: Persistent[float] = na(float)
    lower: PersistentSeries[float] = na(float)
    plotL: Persistent[float] = na(float)
    isOnL: Persistent[bool] = False
    testLine: Persistent[Line] = line.new(na, na, na, na, color=color.new(color.blue, 100))
    n = bar_index
    bg: Color = chart.bg_color
    fg: Color = chart.fg_color
    ph = ta.pivothigh(length, length)
    pl = ta.pivotlow(length, length)
    bars: int = 500
    height = bars / ratio
    Xaxis = math.min(math.max(1, n), bars)
    Yaxis = ta.highest(Xaxis) - ta.lowest(Xaxis)
    srcBl: Series = close if source == 'close' else high
    srcBr: Series = close if source == 'close' else low
    def calculate_slope(x1, x2, y1, y2):
        diffX = x2 - x1
        diffY = y2 - y1
        diffY_to_Yaxis = Yaxis / diffY
        normalised_slope = height / diffY_to_Yaxis / diffX
        slope = diffY / diffX
        angle = math.round(math.atan(normalised_slope) * 180 / math.pi, 2)
        return (normalised_slope, slope, angle)

    if not na(ph):
        if ph < phy1:
            normalised_slope, slope, angle = calculate_slope(phx1, n - length, phy1, ph)
            line.set_xy1(testLine, phx1, phy1)
            line.set_xy2(testLine, n, ph + slope * length)
            src: Series = close if source == 'close' else high
            max_bars_back(src, 2000)
            isOnH = False
            broken: bool = False
            if math.abs(angle) > anglA and math.abs(angle) < anglB:
                if toggle != NN:
                    for i in pine_range(length if toggle == AB else 0, n - phx1, 1):
                        if src[i] > line.get_price(testLine, n - i):
                            broken = True
                            break
                if not broken:
                    phslope = slope
                    isOnH = True
                    upper = ph + slope * length
                    line.new(phx1, phy1, n, ph + slope * length, color=dnCss, style=line.style_dotted)
                    if showA:
                        label.new(phx1, phy1, text=string.tostring(angle), style=label.style_label_down, color=color.new(bg, 100), textcolor=dnCss)
        phy1 = ph
        phx1 = n - length
    upper = upper + phslope
    change_1 = ta.change(phslope)
    plotH = na if not na(ph) and change_1 else na if srcBl[1] > upper[1] else upper
    bs_H = ta.barssince(na(plotH))
    if not na(pl):
        if pl > ply1:
            normalised_slope, slope, angle = calculate_slope(plx1, n - length, ply1, pl)
            line.set_xy1(testLine, plx1, ply1)
            line.set_xy2(testLine, n, pl + slope * length)
            src: Series = close if source == 'close' else low
            max_bars_back(src, 2000)
            isOnL = False
            broken: bool = False
            if angle > anglA and angle < anglB:
                if toggle != NN:
                    for i in pine_range(length if toggle == AB else 0, n - plx1, 1):
                        if src[i] < line.get_price(testLine, n - i):
                            broken = True
                            break
                if not broken:
                    plslope = slope
                    isOnL = True
                    lower = pl + slope * length
                    line.new(plx1, ply1, n, pl + slope * length, color=upCss, style=line.style_dotted)
                    if showA:
                        label.new(plx1, ply1, text=string.tostring(angle), style=label.style_label_up, color=color.new(bg, 100), textcolor=upCss)
        ply1 = pl
        plx1 = n - length
    lower = lower + plslope
    change_2 = ta.change(plslope)
    plotL = na if not na(pl) and change_2 else na if srcBr[1] < lower[1] else lower
    bs_L = ta.barssince(na(plotL))
    plot(plotH, 'Down Trendline', dnCss, 1, plot.style_linebr)
    plot(plotL, 'Up Trendline', upCss, 1, plot.style_linebr)
    plotshape(bs_H > count and srcBl > upper and (srcBl[1] <= upper[1]), 'Bullish break', shape.labelup, location.belowbar, dnCss, size=size.tiny)
    plotshape(bs_L > count and srcBr < lower and (srcBr[1] >= lower[1]), 'Bearish break', shape.labeldown, location.abovebar, upCss, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
