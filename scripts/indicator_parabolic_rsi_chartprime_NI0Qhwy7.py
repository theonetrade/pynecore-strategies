"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barstate, chart, close, color, display, fill, hline, input,
    location, math, na, plot, plotchar, plotshape, script, shape, size, ta
)
from pynecore.types import NA, Persistent, Series


@script.indicator("Parabolic RSI [ChartPrime]", overlay=False)
def main(
    len=input.int(14, "RSI Length", group="RSI"),
    upper_=input.int(70, "Threshold: ⭱", inline="Threshold"),
    lower_=input.int(30, " ⤓", inline="Threshold"),
    display_sar=input.bool(True, "SAR", group="SAR"),
    start=input.float(0.02, "Start", step=0.01, inline="sar", group="SAR"),
    inc=input.float(0.02, "Increment", step=0.01, inline="sar", group="SAR"),
    max=input.float(0.2, "Maximum", step=0.01, inline="sar", group="SAR"),
    color_up=input.color(color.new('#EEA47F'), "", inline="c"),
    color_dn=input.color(color.new('#00539C'), "", inline="c")
):
    rsi = ta.rsi(close, len)

    def pine_sar(src: Series, start, inc, max):
        src_high: Series = src + 1
        src_low: Series = src - 1

        result: Persistent[float] = na(float)
        maxMin: Persistent[float] = na(float)
        acceleration: Persistent[float] = na(float)
        isBelow: Persistent[bool] = False
        isFirstTrendBar: bool = False

        if bar_index <= len + 2:
            if src > src[1]:
                isBelow = True
                maxMin = src_high
                result = src_low[1]
            else:
                isBelow = False
                maxMin = src_low
                result = src_high[1]

            isFirstTrendBar = True
            acceleration = start

        result = result + acceleration * (maxMin - result)

        if isBelow:
            if result > src_low:
                isFirstTrendBar = True
                isBelow = False
                result = math.max(src_high, maxMin)
                maxMin = src_low
                acceleration = start
        else:
            if result < src_high:
                isFirstTrendBar = True
                isBelow = True
                result = math.min(src_low, maxMin)
                maxMin = src_high
                acceleration = start

        if not isFirstTrendBar:
            if isBelow:
                if src_high > maxMin:
                    maxMin = src_high
                    acceleration = math.min(acceleration + inc, max)
            else:
                if src_low < maxMin:
                    maxMin = src_low
                    acceleration = math.min(acceleration + inc, max)

        if isBelow:
            result = math.min(result, src_low[1])
            if bar_index > 1:
                result = math.min(result, src_low[2])
        else:
            result = math.max(result, src_high[1])
            if bar_index > 1:
                result = math.max(result, src_high[2])

        return (result, isBelow)

    isBelow: Series
    sar_rsi, isBelow = pine_sar(rsi, start, inc, max)

    sig_up = isBelow != isBelow[1] and isBelow and barstate.isconfirmed
    sig_dn = isBelow != isBelow[1] and (not isBelow) and barstate.isconfirmed

    s_sig_up = isBelow != isBelow[1] and isBelow and barstate.isconfirmed and (sar_rsi <= lower_)
    s_sig_dn = isBelow != isBelow[1] and (not isBelow) and barstate.isconfirmed and (sar_rsi >= upper_)

    sar: Persistent = NA(float)

    if display_sar:
        sar = na if isBelow != isBelow[1] else sar_rsi

    sar_col = color_up if isBelow else color_dn

    rsiPlot = plot(rsi, 'RSI', color=chart.fg_color)
    rsiUpperBand = hline(upper_, 'RSI Upper Band', color=color.new('#787B86'))
    midline = hline(50, 'RSI Middle Band', color=color.new(color.new('#787B86'), 50))
    rsiLowerBand = hline(lower_, 'RSI Lower Band', color=color.new('#787B86'))
    fill(rsiUpperBand, rsiLowerBand, color=color.new('#C292571A'), title='RSI Background Fill')
    midLinePlot = plot(50, color=na, editable=False, display=display.none)
    fill(rsiPlot, midLinePlot, 100, 70, top_color=color.new(color.red, 0), bottom_color=color.new(color.orange, 100), title='Overbought Gradient Fill')
    fill(rsiPlot, midLinePlot, 30, 0, top_color=color.new(color.red, 100), bottom_color=color.new(color.orange, 0), title='Oversold Gradient Fill')

    sar_p = plot(sar, 'SAR', color=sar_col, style=plot.style_circles)

    plotshape(sar_rsi if sig_up and sar_rsi >= lower_ else na, 'Rsi Up', shape.diamond, location.absolute, size=size.tiny, color=sar_col)
    plotshape(sar_rsi if sig_dn and sar_rsi <= upper_ else na, 'Rsi Dn', shape.diamond, location.absolute, size=size.tiny, color=sar_col)

    plotchar(sar_rsi if s_sig_up else na, 'Rsi Up', '◈', location.absolute, size=size.tiny, color=sar_col)
    plotchar(sar_rsi if s_sig_dn else na, 'Rsi Dn', '◈', location.absolute, size=size.tiny, color=sar_col)

    plotshape(s_sig_up, 'Chart Strong Rsi Up', shape.diamond, location.belowbar, size=size.small, color=sar_col, force_overlay=True)
    plotshape(s_sig_dn, 'Chart Strong Rsi Dn', shape.diamond, location.abovebar, size=size.small, color=sar_col, force_overlay=True)

    plotshape(sig_up and sar_rsi >= lower_, 'Chart Rsi Up', shape.diamond, location.belowbar, size=size.tiny, color=sar_col, force_overlay=True)
    plotshape(sig_dn and sar_rsi <= upper_, 'Chart Rsi Dn', shape.diamond, location.abovebar, size=size.tiny, color=sar_col, force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
