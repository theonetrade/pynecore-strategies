"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_loop, pine_range
from pynecore.lib import (
    array, bar_index, barstate, box, close, color, high, input, label, low,
    math, na, open, plot, script, string, ta, time
)
from pynecore.types import Box, Color, Label, Persistent, PersistentSeries, Series


@script.indicator('Fibonacci levels MTF', overlay=True)
def main(
    timeframe__ren__=input.timeframe(defval='D', title='Higher Time Frame'),
    currentlast=input.string(defval='Last', title='Current or Last HTF Candle', options=('Current', 'Last')),
    showfibolabels=input.bool(defval=True, title='Price Labels'),
    showhtfcandle=input.bool(defval=False, title='Show HTF Candles', inline='candle'),
    upcol=input.color(defval=color.rgb(0, 255, 0, 75), title='', inline='candle'),
    downcol=input.color(defval=color.rgb(255, 0, 0, 75), title='', inline='candle'),
    wickcol=input.color(defval=color.new(color.gray, 75), title='', inline='candle'),
    enable0=input.bool(defval=True, title='Level 0', inline='0', group='Fibonacci Levels'),
    level0=input.float(defval=0.0, title='', inline='0', group='Fibonacci Levels'),
    color0=input.color(defval=color.blue, title='', inline='0', group='Fibonacci Levels'),
    enable1=input.bool(defval=True, title='Level 1', inline='1', group='Fibonacci Levels'),
    level1=input.float(defval=0.236, title='', inline='1', group='Fibonacci Levels'),
    color1=input.color(defval=color.lime, title='', inline='1', group='Fibonacci Levels'),
    enable2=input.bool(defval=True, title='Level 2', inline='2', group='Fibonacci Levels'),
    level2=input.float(defval=0.382, title='', inline='2', group='Fibonacci Levels'),
    color2=input.color(defval=color.red, title='', inline='2', group='Fibonacci Levels'),
    enable3=input.bool(defval=True, title='Level 3', inline='3', group='Fibonacci Levels'),
    level3=input.float(defval=0.5, title='', inline='3', group='Fibonacci Levels'),
    color3=input.color(defval=color.orange, title='', inline='3', group='Fibonacci Levels'),
    enable4=input.bool(defval=True, title='Level 4', inline='4', group='Fibonacci Levels'),
    level4=input.float(defval=0.618, title='', inline='4', group='Fibonacci Levels'),
    color4=input.color(defval=color.teal, title='', inline='4', group='Fibonacci Levels'),
    enable5=input.bool(defval=True, title='Level 5', inline='5', group='Fibonacci Levels'),
    level5=input.float(defval=0.786, title='', inline='5', group='Fibonacci Levels'),
    color5=input.color(defval=color.navy, title='', inline='5', group='Fibonacci Levels'),
    enable100=input.bool(defval=True, title='Level 6', inline='100', group='Fibonacci Levels'),
    level100=input.float(defval=1, title='', inline='100', group='Fibonacci Levels'),
    color100=input.color(defval=color.blue, title='', inline='100', group='Fibonacci Levels'),
    enable6=input.bool(defval=False, title='Level 7', inline='6', group='Fibonacci Levels'),
    level6=input.float(defval=-0.382, title='', inline='6', group='Fibonacci Levels'),
    color6=input.color(defval=color.gray, title='', inline='6', group='Fibonacci Levels'),
    enable7=input.bool(defval=False, title='Level 8', inline='7', group='Fibonacci Levels'),
    level7=input.float(defval=1.236, title='', inline='7', group='Fibonacci Levels'),
    color7=input.color(defval=color.gray, title='', inline='7', group='Fibonacci Levels')
):
    newbar = ta.change(time(timeframe__ren__)) != 0
    htfhigh: PersistentSeries[float] = high
    htflow: PersistentSeries[float] = low
    htfopen: PersistentSeries[float] = open
    htfclose: Series[float] = close
    counter: Persistent[int] = 0
    if newbar:
        htfhigh = high
        htflow = low
        htfopen = open
        counter = 0
    else:
        htfhigh = math.max(htfhigh, high)
        htflow = math.min(htflow, low)
        counter = counter + 1
    if showhtfcandle:
        candle: Persistent[list[Box]] = array.new_box(3, na)
        if not newbar:
            for x in pine_range(0, 2, 1):
                box.delete(array.get(candle, x))
        array.set(candle, 0, box.new(bar_index - counter, math.max(htfopen, htfclose), bar_index, math.min(htfopen, htfclose), border_width=0, bgcolor=upcol if htfclose >= htfopen else downcol))
        array.set(candle, 1, box.new(bar_index - counter, htfhigh, bar_index, math.max(htfopen, htfclose), border_width=0, bgcolor=wickcol))
        array.set(candle, 2, box.new(bar_index - counter, math.min(htfopen, htfclose), bar_index, htflow, border_width=0, bgcolor=wickcol))
    open_: Persistent[float] = na(float)
    high_: Persistent[float] = na(float)
    low_: Persistent[float] = na(float)
    close_: Persistent[float] = na(float)
    if currentlast == 'Last' and newbar:
        open_ = htfopen[1]
        high_ = htfhigh[1]
        low_ = htflow[1]
        close_ = htfclose[1]
    elif currentlast == 'Current':
        open_ = htfopen
        high_ = htfhigh
        low_ = htflow
        close_ = htfclose
    enabled: Persistent[list[bool]] = array.from_items(enable100, enable7, enable6, enable5, enable4, enable3, enable2, enable1, enable0)
    levels: Persistent[list[float]] = array.from_items(level100, level7, level6, level5, level4, level3, level2, level1, level0)
    colors: Persistent[list[Color]] = array.from_items(color100, color7, color7, color5, color4, color3, color2, color1, color0)
    mlevels: list[float] = array.new_float(9, na)
    if not newbar:
        for x in pine_range(0, array.size(levels) - 1, 1):
            array.set(mlevels, x, (high_ - (high_ - low_) * array.get(levels, x) if close_ >= open_ else low_ + (high_ - low_) * array.get(levels, x)) if array.get(enabled, x) else na)
    plot(array.get(mlevels, 0), color=array.get(colors, 0), style=plot.style_linebr)
    plot(array.get(mlevels, 1), color=array.get(colors, 1), style=plot.style_linebr)
    plot(array.get(mlevels, 2), color=array.get(colors, 2), style=plot.style_linebr)
    plot(array.get(mlevels, 3), color=array.get(colors, 3), style=plot.style_linebr)
    plot(array.get(mlevels, 4), color=array.get(colors, 4), style=plot.style_linebr)
    plot(array.get(mlevels, 5), color=array.get(colors, 5), style=plot.style_linebr)
    plot(array.get(mlevels, 6), color=array.get(colors, 6), style=plot.style_linebr)
    plot(array.get(mlevels, 7), color=array.get(colors, 7), style=plot.style_linebr)
    plot(array.get(mlevels, 8), color=array.get(colors, 8), style=plot.style_linebr)
    if barstate.islast and showfibolabels:
        flabels: Persistent[list[Label]] = array.new_label(0)
        __loop_1__ = pine_loop(0, 1)
        while __loop_1__.step(array.size(flabels) - 1 if array.size(flabels) > 0 else na):
            x = __loop_1__.value
            label.delete(array.pop(flabels))
        mid: float = (high_ + low_) / 2
        for x in pine_range(0, array.size(enabled) - 1 if array.size(enabled) > 0 else na, 1):
            if array.get(enabled, x):
                level = array.get(mlevels, x)
                stl = label.style_label_lower_left if level > mid else label.style_label_upper_left if level < mid else label.style_label_left
                array.push(flabels, label.new(bar_index + 1, level, text=string.tostring(math.round(array.get(levels, x), 3)) + ' (' + string.tostring(math.round_to_mintick(level)) + ')', color=array.get(colors, x), textcolor=color.white, style=stl))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
