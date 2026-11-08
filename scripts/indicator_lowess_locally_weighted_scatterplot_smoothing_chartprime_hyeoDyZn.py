"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, bar_index, close, color, high, input, label, line, location, low,
    math, na, plot, plotshape, script, shape, size, string, ta
)
from pynecore.types import Color, Label, Line, Persistent, Series


@script.indicator('LOWESS (Locally Weighted Scatterplot Smoothing) [ChartPrime]', 'Lowess & GaussianMA [ChartPrime]', overlay=True, max_lines_count=500, max_labels_count=500)
def main(
    length=input.int(30, minval=1, title='Length', group='LOWESS (Locally Weighted Scatterplot Smoothing)'),
    leftBars=input.int(5, 'Length', group='Pivots'),
    show_count=input.bool(False, 'Count Breaks', group='==='),
    Gaussian_plot=input.bool(False, 'Gaussian Scatterplot')
):
    rightBars: int = leftBars - 2
    line_h: Persistent[Line] = na(Line)
    line_l: Persistent[Line] = na(Line)
    lbl_h: Persistent[Label] = na(Label)
    lbl_l: Persistent[Label] = na(Label)
    count_up: Persistent[int] = 0
    count_dn: Persistent[int] = 0
    col_up: Color = color.new('#60BEFD')
    col_dn: Color = color.new('#AB61FF')
    ph = ta.pivothigh(leftBars, rightBars)
    pl = ta.pivotlow(leftBars, rightBars)
    def lowess(src: Series, length):
        sum_w: float = 0.0
        sum_wx: float = 0.0
        sum_wy: float = 0.0
        for i in pine_range(0, length - 1, 1):
            w = math.pow(1 - math.pow(i / length, 3), 3)
            sum_w = sum_w + w
            sum_wx = sum_wx + w * i
            sum_wy = sum_wy + w * src[i]
        a = sum_wy / sum_w
        b = sum_wx / sum_w
        return a + b / (length - 1) / 2000

    def GaussianMA(src, length):
        h_l: list[float] = array.new_float(length)
        gma: float = 0.0
        sumOfWeights: float = 0.0
        sigma: float = (ta.atr(length) + ta.stdev(close, length)) / 2
        highest: Series[float] = 0.0
        lowest: Series[float] = 0.0
        smoothed: float = 0.0
        for i in pine_range(0, length - 1, 1):
            array.push(h_l, close[i])
            highest = array.max(h_l)
            lowest = array.min(h_l)
            weight = math.exp(-math.pow((i - (length - 1)) / (2 * sigma), 2) / 2)
            value = math.max(highest[i], highest) + math.min(lowest[i], lowest)
            gma = gma + value * weight
            sumOfWeights = sumOfWeights + weight
        gma = gma / sumOfWeights / 2
        smoothed = lowess(gma, 10)
        return (gma, smoothed)

    smoothed: Series
    gma, smoothed = GaussianMA(close, length)
    random1 = math.random(0, 255)
    gmaColor = color.rgb(random1, random1, random1)
    smoothedColor = col_up if smoothed > smoothed[2] else col_dn if smoothed <= smoothed[2] else na
    plot(gma, 'Gaussian Moving Average', (gmaColor if Gaussian_plot else na) if bar_index % 4 == 0 else na, 1, plot.style_cross)
    plot(smoothed, 'Gaussian Moving Average', smoothedColor)
    plot(smoothed, 'Gaussian Moving Average', color.new(smoothedColor, 80), 5)
    if smoothedColor == col_up and ph:
        line_h = line.new(bar_index[rightBars], high[rightBars], bar_index[rightBars], high[rightBars])
        lbl_h = label.new(na, high[rightBars], '⬥', color=color.new('#00000000'), textcolor=col_up, size=size.large)
    if ta.crossover(close, line.get_y1(line_h)):
        count_dn = 0
        count_up = count_up + 1
        line.set_x2(line_h, bar_index)
        line.set_color(line_h, color.new(col_up, 30))
        label.set_x(lbl_h, bar_index)
        if not show_count:
            label.set_style(lbl_h, label.style_label_center)
        if show_count:
            label.set_y(lbl_h, high)
            label.set_size(lbl_h, size.normal)
            label.set_style(lbl_h, label.style_label_down)
            label.set_text(lbl_h, string.tostring(count_up))
        line_h = na
    if smoothedColor == col_dn and pl:
        line_l = line.new(bar_index[rightBars], low[rightBars], bar_index[rightBars], low[rightBars])
        lbl_l = label.new(na, low[rightBars], '⬥', color=color.new('#00000000'), textcolor=col_dn, size=size.large)
    if ta.crossunder(close, line.get_y1(line_l)):
        count_up = 0
        count_dn = count_dn + 1
        line.set_x2(line_l, bar_index)
        line.set_color(line_l, color.new(col_dn, 30))
        label.set_x(lbl_l, bar_index)
        if not show_count:
            label.set_style(lbl_l, label.style_label_center)
        if show_count:
            label.set_y(lbl_l, low)
            label.set_size(lbl_l, size.normal)
            label.set_style(lbl_l, label.style_label_up)
            label.set_text(lbl_l, string.tostring(count_dn))
        line_l = na
    plotshape(smoothed, '', shape.diamond, location.absolute, color=col_up if ta.crossover(smoothed, smoothed[2]) else col_dn if ta.crossunder(smoothed, smoothed[2]) else na, offset=0, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)