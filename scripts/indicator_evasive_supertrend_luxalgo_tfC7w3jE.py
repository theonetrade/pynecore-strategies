"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, display, fill, hl2, input, label, math, na, nz,
    plot, script, size, ta
)
from pynecore.types import Color, PersistentSeries

ST_GROUP: str = 'Supertrend Settings'
NOISE_GROUP: str = 'Noise Avoidance Logic'
VISUAL_GROUP: str = 'Visualization'


@script.indicator("Evasive SuperTrend [LuxAlgo]", "LuxAlgo - Evasive SuperTrend", overlay=True, max_labels_count=500)
def main(
    lengthInput=input.int(10, 'ATR Length', minval=1, group=ST_GROUP),
    multiplierInput=input.float(3.0, 'Base Multiplier', minval=0.1, step=0.1, group=ST_GROUP),
    thresholdInput=input.float(1.0, 'Noise Threshold (xATR)', minval=0.1, step=0.1, group=NOISE_GROUP, tooltip='If price gets closer to the band than this value, the band is pushed away.'),
    alphaInput=input.float(0.5, 'Expansion Alpha (xATR)', minval=0, step=0.1, group=NOISE_GROUP, tooltip='Distance (in ATRs) to push the band away when noise is detected.'),
    showLabelsInput=input.bool(True, 'Show Signal Labels', group=VISUAL_GROUP),
    showFillsInput=input.bool(True, 'Show Gradient Fills', group=VISUAL_GROUP)
):
    BULL_COLOR: Color = color.new('#089981')
    BEAR_COLOR: Color = color.new('#F23645')



    atr: float = ta.atr(lengthInput)

    stBand: PersistentSeries[float] = na(float)
    trend: PersistentSeries[int] = 1

    src: float = hl2
    upperBase: float = src + multiplierInput * atr
    lowerBase: float = src - multiplierInput * atr

    prevBand: float = nz(stBand[1], lowerBase if trend == 1 else upperBase)

    isNoisy: bool = math.abs(close - prevBand) < atr * thresholdInput

    if trend == 1:
        if isNoisy:
            stBand = prevBand - atr * alphaInput
        else:
            stBand = math.max(lowerBase, prevBand)

        if close < stBand:
            trend = -1
            stBand = upperBase
    else:
        if isNoisy:
            stBand = prevBand + atr * alphaInput
        else:
            stBand = math.min(upperBase, prevBand)

        if close > stBand:
            trend = 1
            stBand = lowerBase

    trendChanged: bool = trend != trend[1]

    stColor: Color = BULL_COLOR if trend == 1 else BEAR_COLOR

    plot(stBand if trendChanged else na, 'Trend Switch Dot', color=stColor, style=plot.style_circles, linewidth=4, join=False)

    plotId = plot(stBand, 'Band for Fill', color=na)

    plot(na if isNoisy else stBand, 'Solid Band', color=stColor, linewidth=2, style=plot.style_linebr)

    plot(stBand if isNoisy else na, 'Dotted Band', color=stColor, linewidth=2, style=plot.style_linebr, linestyle=plot.linestyle_dotted)

    srcId = plot(src, 'Source', color=na)

    topValue: float = math.max(src, stBand)
    bottomValue: float = math.min(src, stBand)
    topFillColor: Color = color.new(BULL_COLOR, 50) if trend == 1 else color.new(BEAR_COLOR, 100)
    bottomFillColor: Color = color.new(BULL_COLOR, 100) if trend == 1 else color.new(BEAR_COLOR, 50)

    fill(plotId, srcId, topValue, bottomValue, topFillColor, bottomFillColor, title='Trend Fill', display=display.all if showFillsInput else display.none)

    if showLabelsInput and trendChanged:
        label.new(bar_index, stBand, text='BULL' if trend == 1 else 'BEAR', color=stColor, textcolor=color.new('#FFFFFF'), style=label.style_label_up if trend == 1 else label.style_label_down, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
