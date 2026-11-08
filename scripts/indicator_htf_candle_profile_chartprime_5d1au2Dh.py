"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_udt import udt
from pynecore.core.series import inline_series
from pynecore.lib import (
    array, bar_index, barstate, bgcolor, box, chart, close, color, format,
    high, input, label, line, location, low, math, na, open, plotchar, script, size, string, ta,
    timeframe, volume
)
from pynecore.types import Box, Color, Label, Line, NA, Persistent


@udt
class Profile:
    lines: list[Line] = na(list)
    boxes: list[Box] = na(list)
    labels: list[Label] = na(list)


@script.indicator("HTF Candle Profile [ChartPrime]", overlay=True, max_boxes_count=500, max_polylines_count=100, max_lines_count=500, max_bars_back=5000)
def main(
    tf=input.timeframe("W", "TimeFrame", options=("D", "W", "M"), tooltip="Daily, Weekly, Monthly"),
    offset=input.int(5, "Profile Offset"),
    minPeriod=input.int(50, "Min Period Profile", minval=10, tooltip="Defines how many bars must pass before calculating the HTF candle profile to ensure enough data for accurate volume distribution."),
    dHigh=input.bool(True, "High", group="Levels", inline="Levels"),
    dLow=input.bool(True, "Low", group="Levels", inline="Levels"),
    dClose=input.bool(True, "Close", group="Levels", inline="Levels"),
    dOpen=input.bool(True, "Open", group="Levels", inline="Levels"),
    dPoc=input.bool(True, "PoC", group="Levels", inline="Levels", tooltip="HTF Levels"),
    bullishColor=input.color(color.green, "", inline="candle"),
    bearishColor=input.color(color.red, "", inline="candle")
):
    start: Persistent[list[int]] = array.new_int()
    period: Persistent[int] = 0
    changeBg: Color = NA(Color)

    O: Persistent[list[float]] = array.new_float()
    C: Persistent[list[float]] = array.new_float()
    Op: Persistent = NA(float)
    Cl: Persistent = NA(float)

    i_Size: Persistent = NA(int)

    if inline_series(timeframe.change(tf), 1):
        array.push(O, open)
        array.push(C, close)
        array.push(start, bar_index)
        changeBg = color.new(chart.fg_color, 90)
        i_Size = bar_index - array.get(start, -1)

    if array.size(start) > 1:
        if bar_index - array.last(start) < minPeriod:
            period = bar_index - array.get(start, -2)
            Op = array.get(O, -2)
            Cl = array.last(C)
        else:
            period = bar_index - array.last(start)
            Op = array.last(O)
            Cl = close

    bgcolor(changeBg, show_last=1000)
    plotchar(inline_series(timeframe.change(tf), 1), 'TimeFrame', tf, location.bottom, chart.fg_color, size=size.small, show_last=1000)

    HL: list[float] = array.new_float()
    atr = ta.atr(200) * 0.3

    if barstate.islast:
        ProfileDraws: Persistent[list[Profile]] = array.new(0, NA(Profile))

        for i in pine_range(0, period):
            array.push(HL, high[i])
            array.push(HL, low[i])

        max = array.max(HL)
        min = array.min(HL)

        if array.size(ProfileDraws) > 0:
            for p in ProfileDraws:
                for l in p.lines:
                    line.delete(l)
                for b in p.boxes:
                    box.delete(b)
                for l in p.labels:
                    label.delete(l)

        Height = max - min
        size__ren__ = math.ceil(Height / atr)
        step = Height / size__ren__
        binsVol: list[float] = array.new_float(size__ren__, 0.0)

        for k in pine_range(0, period):
            Close = close[k]

            for i in pine_range(0, size__ren__ - 1):
                loww = min + step * i
                mid = loww + step / 2

                if math.abs(Close - mid) <= step:
                    array.set(binsVol, i, array.get(binsVol, i) + volume[k])

        Lines: list[Line] = array.new_line()
        Boxes: list[Box] = array.new_box()
        Labels: list[Label] = array.new_label()

        BarColor: Color = bullishColor if Cl > Op else bearishColor

        for i in pine_range(0, size__ren__ - 1):
            bot = array.min(HL) + step * i
            top = bot + step

            VolumeVal = cast_int(array.get(binsVol, i) / array.max(binsVol) * 50)
            indx = bar_index + 50 + offset
            bgColor = color.from_gradient(VolumeVal, 0, 50, color.new(BarColor, 90), BarColor)

            b = box.new(indx, top, indx - VolumeVal, bot, chart.bg_color, 1, bgcolor=bgColor)
            array.push(Boxes, b)

            if VolumeVal == 50 and dPoc:
                array.push(Lines, line.new(indx - VolumeVal, math.avg(bot, top), bar_index - period, math.avg(bot, top), color=BarColor))
                array.push(Labels, label.new(bar_index - period, math.avg(top, bot), string.tostring(array.get(binsVol, i), format.volume), color=NA(Color), textcolor=chart.fg_color, style=label.style_label_right))

        indxBar = bar_index + 55 + offset

        array.push(Lines, line.new(indxBar, max, indxBar, min, color=BarColor))
        array.push(Lines, line.new(indxBar, Cl, indxBar, Op, color=BarColor, width=10))

        if dHigh:
            array.push(Labels, label.new(indxBar, max, 'High: ' + string.tostring(max), style=label.style_label_down, color=NA(Color), textcolor=chart.fg_color))
            array.push(Lines, line.new(bar_index - period, max, indxBar, max, color=BarColor, style=line.style_dashed))
        if dLow:
            array.push(Labels, label.new(indxBar, min, 'Low: ' + string.tostring(min), style=label.style_label_up, color=NA(Color), textcolor=chart.fg_color))
            array.push(Lines, line.new(bar_index - period, min, indxBar, min, color=BarColor, style=line.style_dashed))
        if dClose:
            array.push(Labels, label.new(indxBar, Cl, 'Close: ' + string.tostring(Cl), style=label.style_label_left, color=NA(Color), textcolor=chart.fg_color))
            array.push(Lines, line.new(bar_index - period, Cl, indxBar, Cl, color=BarColor, style=line.style_dotted))
        if dOpen:
            array.push(Labels, label.new(indxBar, Op, 'Open: ' + string.tostring(Op), style=label.style_label_left, color=NA(Color), textcolor=chart.fg_color))
            array.push(Lines, line.new(bar_index - period, Op, indxBar, Op, color=BarColor, style=line.style_dotted))

        array.push(ProfileDraws, Profile(Lines, Boxes, Labels))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
