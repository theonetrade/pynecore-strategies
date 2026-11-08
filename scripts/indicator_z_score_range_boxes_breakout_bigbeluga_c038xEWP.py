"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, box, chart, close, color, extend, fill, high, input, label,
    line, low, math, na, plot, script, size, string, ta, text
)
from pynecore.types import Box, Color, Line, NA, Persistent, Series


@script.indicator("Z-Score Range Boxes Breakout [BigBeluga]", overlay=False, max_boxes_count=500, max_lines_count=500, max_labels_count=500)
def main(
    length=input.int(20, "Z-Score Length", group="Z-Score Settings", tooltip="Number of bars used to calculate the standard deviation and mean for the Z-Score."),
    zSource: Series[float] = input.source(close, "Z-Score Source", group="Z-Score Settings", tooltip="Price source data used for the Z-Score calculation."),
    smoothLen=input.int(5, "Smoothing Line Length", group="Z-Score Settings", tooltip="Period length for smoothing the final Z-Score line."),
    osThreshold=input.float(-2.0, "Oversold Trigger Level (-3 or -4)", step=0.1, group="Thresholds", tooltip="Z-Score level that triggers an oversold (bullish) range box setup."),
    obThreshold=input.float(2.0, "Overbought Trigger Level (3 or 4)", step=0.1, group="Thresholds", tooltip="Z-Score level that triggers an overbought (bearish) range box setup."),
    boxBars=input.int(10, "Box Period Length (Bars)", group="Box Settings", tooltip="Number of bars the developing box tracks before finalizing the range boundaries."),
    osColorInput=input.color(color.aqua, "Oversold / Bullish Color", group="Color Settings", tooltip="Color theme applied to oversold boxes, extended lines, and breakout markers."),
    obColorInput=input.color(color.rgb(255, 131, 82), "Overbought / Bearish Color", group="Color Settings", tooltip="Color theme applied to overbought boxes, extended lines, and breakout markers.")
):
    stDev = ta.stdev(zSource, length)
    mean = ta.sma(zSource, length)
    zScore = (zSource - mean) / stDev if stDev != 0 else 0
    zSmooth = ta.sma(zScore, 1 if length == 0 else smoothLen)

    activeOsBox: Persistent[Box] = na(Box)
    osStartBar: Persistent[int] = na(int)

    activeObBox: Persistent[Box] = na(Box)
    obStartBar: Persistent[int] = na(int)

    isOversold = ta.crossunder(zSmooth, osThreshold) and na(activeOsBox) and na(activeObBox)
    isOverbought = ta.crossover(zSmooth, obThreshold) and na(activeOsBox) and na(activeObBox)

    topExtLine: Persistent[Line] = na(Line)
    midExtLine: Persistent[Line] = na(Line)
    botExtLine: Persistent[Line] = na(Line)

    currentRangeTop: Persistent[float] = na(float)
    currentRangeBot: Persistent[float] = na(float)

    if isOversold:
        currentRangeTop = na
        currentRangeBot = na

        osStartBar = bar_index
        zText: str = 'Z: ' + string.tostring(zSmooth, '#.##')
        activeOsBox = box.new(left=bar_index, top=high, right=bar_index + boxBars, bottom=low, border_color=osColorInput, bgcolor=color.new(osColorInput, 85), text=zText, text_color=chart.fg_color, text_size=size.small, text_valign=text.align_top, text_halign=text.align_left, extend=extend.none, force_overlay=True)

    if not na(activeOsBox):
        barsElapsed: int = bar_index - osStartBar
        if barsElapsed <= boxBars:
            currentTop: float = box.get_top(activeOsBox)
            currentBot: float = box.get_bottom(activeOsBox)
            box.set_top(activeOsBox, math.max(currentTop, high))
            box.set_bottom(activeOsBox, math.min(currentBot, low))
            box.set_right(activeOsBox, osStartBar + boxBars)

            if barsElapsed == boxBars:
                fTop: float = box.get_top(activeOsBox)
                fBot: float = box.get_bottom(activeOsBox)
                fMid: float = (fTop + fBot) / 2

                currentRangeTop = fTop
                currentRangeBot = fBot

                topExtLine = line.new(osStartBar, fTop, bar_index, fTop, color=color.new(osColorInput, 20), width=1, force_overlay=True)
                midExtLine = line.new(osStartBar, fMid, bar_index, fMid, color=color.new(osColorInput, 20), style=line.style_dashed, width=1, force_overlay=True)
                botExtLine = line.new(osStartBar, fBot, bar_index, fBot, color=color.new(osColorInput, 20), width=1, force_overlay=True)
        else:
            activeOsBox = na

    if isOverbought:
        currentRangeTop = na
        currentRangeBot = na

        obStartBar = bar_index
        zText: str = 'Z: ' + string.tostring(zSmooth, '#.##')
        activeObBox = box.new(left=bar_index, top=high, right=bar_index + boxBars, bottom=low, border_color=obColorInput, bgcolor=color.new(obColorInput, 85), text=zText, text_color=chart.fg_color, text_size=size.small, text_valign=text.align_bottom, text_halign=text.align_right, extend=extend.none, force_overlay=True)

    if not na(activeObBox):
        barsElapsed: int = bar_index - obStartBar
        if barsElapsed <= boxBars:
            currentTop: float = box.get_top(activeObBox)
            currentBot: float = box.get_bottom(activeObBox)
            box.set_top(activeObBox, math.max(currentTop, high))
            box.set_bottom(activeObBox, math.min(currentBot, low))
            box.set_right(activeObBox, obStartBar + boxBars)

            if barsElapsed == boxBars:
                fTop: float = box.get_top(activeObBox)
                fBot: float = box.get_bottom(activeObBox)
                fMid: float = (fTop + fBot) / 2

                currentRangeTop = fTop
                currentRangeBot = fBot

                topExtLine = line.new(obStartBar, fTop, bar_index, fTop, color=color.new(obColorInput, 20), width=1, force_overlay=True)
                midExtLine = line.new(obStartBar, fMid, bar_index, fMid, color=color.new(obColorInput, 20), style=line.style_dashed, width=1, force_overlay=True)
                botExtLine = line.new(obStartBar, fBot, bar_index, fBot, color=color.new(obColorInput, 20), width=1, force_overlay=True)
        else:
            activeObBox = na

    bullishBreakout: bool = ta.crossover(close, currentRangeTop) and (not na(currentRangeTop))
    bearishBreakout: bool = ta.crossunder(close, currentRangeBot) and (not na(currentRangeBot))

    if bullishBreakout:
        topExtLine = na
        midExtLine = na
        currentRangeTop = na

        label.new(x=bar_index, y=low, text='', color=osColorInput, textcolor=NA(Color), style=label.style_label_up, size=size.tiny, force_overlay=True)

    if bearishBreakout:
        botExtLine = na
        midExtLine = na
        currentRangeBot = na

        label.new(x=bar_index, y=high, text='', color=obColorInput, textcolor=NA(Color), style=label.style_label_down, size=size.tiny, force_overlay=True)

    if not na(topExtLine) and na(activeOsBox) and na(activeObBox) and (not isOversold) and (not isOverbought):
        line.set_x2(topExtLine, bar_index)
        if not na(midExtLine):
            line.set_x2(midExtLine, bar_index)

    if not na(botExtLine) and na(activeOsBox) and na(activeObBox) and (not isOversold) and (not isOverbought):
        if not na(botExtLine):
            line.set_x2(botExtLine, bar_index)

    oscColor: Color = color.from_gradient(zSmooth, -3.0, 3.0, osColorInput, obColorInput)

    pZ = plot(zSmooth, title='Smoothed Z-Score Gradient', color=oscColor, linewidth=2)
    pMid = plot(0.0, title='Zero Midline', color=color.new(chart.fg_color, 50), linewidth=1, style=plot.style_line)
    pObLine = plot(obThreshold, title='OB Line', color=obColorInput, linewidth=1, linestyle=plot.linestyle_dashed)
    pOsLine = plot(osThreshold, title='OS Line', color=osColorInput, linewidth=1, linestyle=plot.linestyle_dashed)

    fill(pZ, pObLine, 4, obThreshold, color.new(obColorInput, 30) if zSmooth > obThreshold else NA(Color), color.new(obColorInput, 90) if zSmooth > obThreshold else NA(Color))
    fill(pZ, pOsLine, -4, osThreshold, color.new(osColorInput, 30) if zSmooth < osThreshold else NA(Color), color.new(osColorInput, 90) if zSmooth < osThreshold else NA(Color))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)