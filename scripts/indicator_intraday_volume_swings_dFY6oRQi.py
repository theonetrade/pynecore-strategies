"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alert, bgcolor, close, color, fill, high, input, label, location, low,
    math, na, open, plot, plotshape, script, shape, size, ta, time, timeframe, volume, xloc
)
from pynecore.types import PersistentSeries, Series


@script.indicator('Intraday Volume Swings', overlay=True, na_bool=True)
def main(
    mark_swings=input(True, title='Mark all volume swings?'),
    mark_new_day=input(True, title='Mark first bar of a new day?'),
    mark_greater_swings=input(True, title='Mark daily lower/higher swings?'),
    plot_current=input(False, title='Display levels as they form?'),
    region_must_close=input(True, title='Must close in region to trigger alert?')
):
    new_day = ta.change(time('D')) != 0
    increasing_volume = volume > volume[1]
    lower_low = low < low[1]
    higher_high = high > high[1]
    high_bar: Series = increasing_volume and higher_high
    low_bar: Series = increasing_volume and lower_low
    swing_low: Series = low_bar and low_bar[1] and low_bar[2]
    swing_high: Series = high_bar and high_bar[1] and high_bar[2]
    confirmed_swing_low = not swing_low and swing_low[1]
    confirmed_swing_high = not swing_high and swing_high[1]
    hh3 = ta.highest(high, 3)
    ll3 = ta.lowest(low, 3)
    swing_low_top: Series[float] = na(float)
    swing_low_bottom: Series[float] = na(float)
    swing_high_top: Series[float] = na(float)
    swing_high_bottom: Series[float] = na(float)
    if swing_low and (not swing_low[1]):
        swing_low_top = hh3
        swing_low_bottom = ll3
    elif swing_low and swing_low[1]:
        swing_low_top = math.max(swing_low_top[1], high)
        swing_low_bottom = math.min(swing_low_bottom[1], low)
    if swing_high and (not swing_high[1]):
        swing_high_top = hh3
        swing_high_bottom = ll3
    elif swing_high and swing_high[1]:
        swing_high_top = math.max(swing_high_top[1], high)
        swing_high_bottom = math.min(swing_high_bottom[1], low)
    daily_swing_low_top: PersistentSeries[float] = na(float)
    daily_swing_low_bottom: PersistentSeries[float] = na(float)
    daily_swing_high_top: PersistentSeries[float] = na(float)
    daily_swing_high_bottom: PersistentSeries[float] = na(float)
    if new_day and (not swing_low) and (not confirmed_swing_low):
        daily_swing_low_top = na
        daily_swing_low_bottom = na
    if new_day and swing_low:
        daily_swing_low_top = swing_low_top
        daily_swing_low_bottom = swing_low_bottom
    if new_day and confirmed_swing_low:
        daily_swing_low_top = swing_low_top[1]
        daily_swing_low_bottom = swing_low_bottom[1]
    if not new_day and confirmed_swing_low and na(daily_swing_low_bottom):
        daily_swing_low_top = swing_low_top[1]
        daily_swing_low_bottom = swing_low_bottom[1]
    if not new_day and confirmed_swing_low and (not na(daily_swing_low_bottom)) and (swing_low_bottom[1] < daily_swing_low_bottom):
        daily_swing_low_top = swing_low_top[1]
        daily_swing_low_bottom = swing_low_bottom[1]
    if new_day and (not swing_high) and (not confirmed_swing_high):
        daily_swing_high_top = na
        daily_swing_high_bottom = na
    if new_day and swing_high:
        daily_swing_high_top = swing_high_top
        daily_swing_high_bottom = swing_high_bottom
    if new_day and confirmed_swing_high:
        daily_swing_high_top = swing_high_top[1]
        daily_swing_high_bottom = swing_high_bottom[1]
    if not new_day and confirmed_swing_high and na(daily_swing_high_bottom):
        daily_swing_high_top = swing_high_top[1]
        daily_swing_high_bottom = swing_high_bottom[1]
    if not new_day and confirmed_swing_high and (not na(daily_swing_high_top)) and (swing_high_top[1] > daily_swing_high_top):
        daily_swing_high_top = swing_high_top[1]
        daily_swing_high_bottom = swing_high_bottom[1]
    valid_chart = timeframe.isintraday and (not na(volume))
    prev_swing_low_top: float = na(float)
    prev_swing_low_bottom: float = na(float)
    prev_swing_high_top: float = na(float)
    prev_swing_high_bottom: float = na(float)
    prev_swing_low_top2: float = na(float)
    prev_swing_low_bottom2: float = na(float)
    prev_swing_high_top2: float = na(float)
    prev_swing_high_bottom2: float = na(float)
    prev_swing_low_top = ta.valuewhen(new_day, daily_swing_low_top[1], 0)
    prev_swing_low_bottom = ta.valuewhen(new_day, daily_swing_low_bottom[1], 0)
    prev_swing_high_top = ta.valuewhen(new_day, daily_swing_high_top[1], 0)
    prev_swing_high_bottom = ta.valuewhen(new_day, daily_swing_high_bottom[1], 0)
    prev_swing_low_bottom2 = ta.valuewhen(new_day, daily_swing_low_bottom[1], 1)
    prev_swing_high_top2 = ta.valuewhen(new_day, daily_swing_high_top[1], 1)
    lower_swing_low = prev_swing_low_bottom < prev_swing_low_bottom2
    higher_swing_high = prev_swing_high_top > prev_swing_high_top2
    current_swing_low_top_plot = plot(daily_swing_low_top if valid_chart and plot_current else na, style=plot.style_circles, color=color.new(color.maroon, 50), linewidth=1)
    current_swing_low_bottom_plot = plot(daily_swing_low_bottom if valid_chart and plot_current else na, style=plot.style_circles, color=color.new(color.maroon, 50), linewidth=1)
    current_swing_high_top_plot = plot(daily_swing_high_top if valid_chart and plot_current else na, style=plot.style_circles, color=color.new(color.green, 50), linewidth=1)
    current_swing_high_bottom_plot = plot(daily_swing_high_bottom if valid_chart and plot_current else na, style=plot.style_circles, color=color.new(color.green, 50), linewidth=1)
    swing_low_top_plot = plot(prev_swing_low_top if valid_chart else na, color=color.new('#00000000'), title='Swing Low Upper Plot')
    swing_low_bottom_plot = plot(prev_swing_low_bottom if valid_chart else na, color=color.new('#00000000'), title='Swing Low Lower Plot')
    swing_high_top_plot = plot(prev_swing_high_top if valid_chart else na, color=color.new('#00000000'), title='Swing High Upper Plot')
    swing_high_bottom_plot = plot(prev_swing_high_bottom if valid_chart else na, color=color.new('#00000000'), title='Swing High Lower Plot')
    fill(swing_low_top_plot, swing_low_bottom_plot, color=color.new(color.red, 70))
    fill(swing_high_top_plot, swing_high_bottom_plot, color=color.new(color.lime, 70))
    plotshape((na if na(confirmed_swing_low) else 1 if confirmed_swing_low else 0) if mark_swings else na, style=shape.triangleup, location=location.belowbar, size=size.tiny, color=color.new(color.red, 0), title='Swing Low')
    plotshape((na if na(confirmed_swing_high) else 1 if confirmed_swing_high else 0) if mark_swings else na, style=shape.triangledown, location=location.abovebar, size=size.tiny, color=color.new(color.lime, 0), title='Swing High')
    higher_swing_label: Series = label.new(x=time, y=math.avg(prev_swing_high_bottom, prev_swing_high_top), xloc=xloc.bar_time, color=color.green, textcolor=color.white, style=label.style_label_left, size=size.small, text='Higher Swing High') if mark_greater_swings and higher_swing_high else na
    lower_swing_label: Series = label.new(x=time, y=math.avg(prev_swing_low_bottom, prev_swing_low_top), xloc=xloc.bar_time, color=color.red, textcolor=color.white, style=label.style_label_left, size=size.small, text='Lower Swing Low') if mark_greater_swings and lower_swing_low else na
    label.delete(higher_swing_label[1])
    label.delete(lower_swing_label[1])
    bgcolor(color.yellow if new_day and mark_new_day else color.new('#00000000'))
    warning_label: Series = label.new(x=time, y=close, xloc=xloc.bar_time, color=color.red, textcolor=color.white, style=label.style_label_left, size=size.normal, text='Warning!!!\nIntraday Timeframes with Volume Only') if not valid_chart else na
    label.delete(warning_label[1])
    if open[1] < prev_swing_high_bottom and close[1] >= prev_swing_high_bottom if region_must_close else open < prev_swing_high_bottom and high >= prev_swing_high_bottom:
        alert("Pushing up into yesterday's swing high region", alert.freq_once_per_bar)
    if open[1] > prev_swing_low_top and close[1] <= prev_swing_low_top if region_must_close else open > prev_swing_low_top and low <= prev_swing_low_top:
        alert("Pushing down into yesterday's swing low region", alert.freq_once_per_bar)
    if open[1] < daily_swing_high_bottom and close[1] >= daily_swing_high_bottom if region_must_close else open < daily_swing_high_bottom and high >= daily_swing_high_bottom:
        alert('Pushing up into current swing high region', alert.freq_once_per_bar)
    if open[1] > daily_swing_low_top and close[1] <= daily_swing_low_top if region_must_close else open > daily_swing_low_top and low <= daily_swing_low_top:
        alert('Pushing down into current swing low region', alert.freq_once_per_bar)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)