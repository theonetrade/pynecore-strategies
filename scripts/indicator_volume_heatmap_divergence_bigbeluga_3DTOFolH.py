"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barcolor, chart, color, display, format, high, input, label,
    location, low, na, plot, plotcandle, plotshape, scale, script, shape, size, string, ta, volume
)
from pynecore.types import Color, NA, Series


@script.indicator("Volume HeatMap Divergence [BigBeluga]", overlay=True, scale=scale.none, max_labels_count=500)
def main(
    showDiv=input.bool(True, "Divergence", group="Divergence", inline="div"),
    labelVolume=input.bool(True, "Volume", group="Divergence", inline="div"),
    labelPercent=input.bool(True, "Percent", group="Divergence", inline="div"),
    minRange=input.int(5, "Range Min", inline="Range", group="Divergence"),
    maxRange=input.int(60, "Max", inline="Range", group="Divergence"),
    divLookLeft=input.int(10, "Pivot Left", inline="pivot", group="Divergence"),
    divLookRight=input.int(5, "Right", inline="pivot", group="Divergence"),
    BullColor=input.color(color.new('#19B493'), "Bullish Color"),
    BearColor=input.color(color.new('#B95919'), "Bearish Color"),
    sizeOffset=input.int(400, "Chart Scale")
):
    vol: Series[float] = volume / ta.percentile_nearest_rank(volume, 1000, 100) * 100
    volColor: Color = color.from_gradient(vol, 0, 20, color.aqua, color.yellow) if vol < 20 else color.from_gradient(vol, 20, 100, color.yellow, color.red)
    candleColor: Color = color.from_gradient(vol, 20, 100, color.yellow, color.red)

    volVal = vol[divLookRight]

    def _inRange(pivot):
        barCount = ta.barssince(pivot)
        return minRange <= barCount and barCount <= maxRange

    def VolumeDivergence(doCheck):
        bull: bool = False
        bear: bool = False
        PH: Series[bool] = False

        if doCheck:
            PH = not na(ta.pivothigh(vol, divLookLeft, divLookRight))

            range_ = _inRange(PH[1])

            volHL = volVal > ta.valuewhen(PH, volVal, 1) and range_
            priceLL = low[divLookRight] < ta.valuewhen(PH, low[divLookRight], 1)
            bull = PH and volHL and priceLL

            volLH = volVal < ta.valuewhen(PH, volVal, 1) and range_
            priceHH = high[divLookRight] > ta.valuewhen(PH, high[divLookRight], 1)
            bear = PH and volLH and priceHH

        return (PH, bull, bear, high[divLookRight], low[divLookRight])

    PH, isBullDiv, isBearDiv, highLevel, lowLevel = VolumeDivergence(showDiv)

    plot(sizeOffset, editable=False, color=NA(Color))

    plotcandle(0, vol, 0, vol, title='Volume', color=volColor, wickcolor=volColor, bordercolor=volColor)

    barcolor(volColor, display=display.none)

    plot(volVal if PH else na, offset=-divLookRight, title='Bullish Volume HL', color=BullColor if isBullDiv else NA(Color), linewidth=2)
    plot(volVal if PH else na, offset=-divLookRight, title='Bearish Volume LH', color=BearColor if isBearDiv else NA(Color), linewidth=2)

    volTXT: str = '\n' + string.tostring(volume[divLookRight], format.volume) if labelVolume else ''
    percentTXT: str = '\n' + string.tostring(vol[divLookRight], format.percent) if labelPercent else ''

    if isBullDiv:
        label.new(bar_index[divLookRight], volVal, 'Bull' + volTXT + percentTXT, size=size.small, color=BullColor)
    if isBearDiv:
        label.new(bar_index[divLookRight], volVal, 'Bear' + volTXT + percentTXT, size=size.small, color=BearColor)

    plotshape(low[divLookRight] if isBullDiv else na, offset=-divLookRight, title='Bullish Price LL Label', style=shape.labelup, text='Bull', color=BullColor, textcolor=chart.fg_color, force_overlay=True, location=location.absolute)
    plotshape(highLevel if isBearDiv else na, offset=-divLookRight, title='Bearish Price HH Label', style=shape.labeldown, text='Bear', color=BearColor, textcolor=chart.fg_color, force_overlay=True, location=location.absolute)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
