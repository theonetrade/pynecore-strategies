"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barstate, chart, color, fill, high, hl2, input, label, low,
    math, na, plot, script, size, ta
)
from pynecore.types import Color, NA, Persistent, PersistentSeries, Series


@script.indicator('Range Breakout [BigBeluga]', overlay=True, max_lines_count=4, max_labels_count=500)
def main(
    multi=input.float(4, 'Channel Width', step=0.1),
    show_x=input.bool(False, "Show X signals"),
    filter_sig=input.bool(False, "Filter Signals by Trends", tooltip="If True indicator filters ▲▼ based on channels breakout condition. If channel is bullish with green circle only ▲ displayed if bearish with red only ▼ signals displayed"),
    color1=input.color(color.new('#1DAC70'), "", inline="col", group="OB/OS"),
    color3=input.color(color.new('#DF3A79'), "", inline="col", group="OB/OS"),
    gradient=input.bool(True, "Gradient", inline="ll", group="OB/OS"),
    transp=input.int(80, "", inline="ll", group="OB/OS")
):
    length: int = 100
    color2: Color = chart.fg_color

    value: PersistentSeries[float] = na(float)
    value_upper: PersistentSeries[float] = na(float)
    value_lower: PersistentSeries[float] = na(float)
    value_upper_mid: Persistent[float] = na(float)
    value_lower_mid: Persistent[float] = na(float)
    trend: Persistent[bool] = False

    count: Persistent[int] = 0

    atr: float = ta.sma(ta.atr(200), 100) * multi

    if bar_index == 301:
        value = hl2
        value_upper = hl2 + atr
        value_lower = hl2 - atr
        value_upper_mid = math.avg(value, value_upper)
        value_lower_mid = math.avg(value, value_lower)

    cross_upper: bool = ta.crossover(low, value_upper) and barstate.isconfirmed
    cross_lower: bool = ta.crossunder(high, value_lower) and barstate.isconfirmed

    if low > value_upper or high < value_lower:
        count = count + 1

    if cross_upper or cross_lower or count == 100:
        count = 0
        value = hl2
        value_upper = hl2 + atr
        value_lower = hl2 - atr
        value_upper_mid = math.avg(value, value_upper)
        value_lower_mid = math.avg(value, value_lower)

    chage: bool = not value != value[1]
    buy_: bool = ta.crossover(low, value_lower_mid) and low[10] > value_lower_mid and barstate.isconfirmed and chage
    sell_: bool = ta.crossunder(high, value_upper_mid) and high[10] < value_upper_mid and barstate.isconfirmed and chage
    fakeout_up: bool = ta.crossunder(high, value_upper) and barstate.isconfirmed and chage
    fakeout_dn: bool = ta.crossover(low, value_lower) and barstate.isconfirmed and chage

    p1 = plot(na if value_upper != value_upper[1] else value_upper, color=color1, linewidth=1, style=plot.style_linebr)
    p0 = plot(value if bar_index % 2 == 0 else na, color=color2, style=plot.style_linebr)
    p2 = plot(na if value_lower != value_lower[1] else value_lower, color=color3, linewidth=1, style=plot.style_linebr)

    upper_mid: Series = math.avg(value_upper, value)
    lower_mid: Series = math.avg(value_lower, value)

    p01 = plot(na if upper_mid != upper_mid[1] else upper_mid, color=color.new(color2, 50), style=plot.style_linebr)
    p02 = plot(na if lower_mid != lower_mid[1] else lower_mid, color=color.new(color2, 50), style=plot.style_linebr)

    fill(p1, p01, value_upper, value, color.new(na if value_upper != value_upper[1] else color1, transp), color.new(na if value_upper != value_upper[1] else color1, 100 if gradient else transp))
    fill(p2, p02, value, value_lower, color.new(na if value_upper != value_upper[1] else color3, 100 if gradient else transp), color.new(na if value_upper != value_upper[1] else color3, transp))

    if cross_upper:
        trend = True
        label.new(bar_index - 1, value_upper[1], text='⦿', textcolor=color1, style=label.style_label_center, color=NA(Color), size=size.large, tooltip='Bullish Break')
    if cross_lower:
        trend = False
        label.new(bar_index - 1, value_lower[1], text='⦿', textcolor=color3, style=label.style_label_center, color=NA(Color), size=size.large, tooltip='Bearish Break')

    if buy_ and (trend if filter_sig else True):
        label.new(bar_index - 1, low[1], text='▲', textcolor=color1, style=label.style_label_up, color=NA(Color), size=size.normal)
    if sell_ and (not trend if filter_sig else True):
        label.new(bar_index - 1, high[1], text='▼', textcolor=color3, style=label.style_label_down, color=NA(Color), size=size.normal)

    if fakeout_up and show_x:
        label.new(bar_index - 1, high[1], text='X', textcolor=color3, style=label.style_label_down, color=NA(Color), size=size.normal)
    if fakeout_dn and show_x:
        label.new(bar_index - 1, low[1], text='X', textcolor=color1, style=label.style_label_up, color=NA(Color), size=size.normal)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
