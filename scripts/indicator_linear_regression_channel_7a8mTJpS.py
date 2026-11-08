"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.lib import (
    array, bar_index, barcolor, barstate, chart, close, color, extend, fill,
    high, hl2, input, label, last_bar_index, line, linefill, location, low, math, na, open, plot,
    plotcandle, plotchar, script, size, ta
)
from pynecore.types import Color, Line, NA, Persistent, Series


@script.indicator('Linear Regression Channel', overlay=True, max_lines_count=3)
def main(
    bands=input.bool(True, 'Plot Linear Regression Bands', group='Settings Bands'),
    window=input.int(150, 'Length', group='Settings Bands'),
    devlen_b=input.float(3.0, 'Deviation Linear Regression Bands', step=0.1, group='Settings Bands'),
    channel=input.bool(False, 'Plot Linear Regression Channel', group='Settings Channel'),
    window1=input.int(150, 'Channel Length', group='Settings Channel'),
    devlen1=input.float(1.0, 'Deviation Linear Regression Channel', step=0.1, group='Settings Channel'),
    channel1=input.bool(False, 'Plot Future Projection of linear regression', group='Future Projection Channel'),
    arr_dirc=input.bool(False, 'Plot Arrow Direction', group='Future Projection Channel'),
    window2=input.int(50, 'Length', group='Future Projection Channel'),
    devlen2=input.float(1.0, 'Deviation Future Projection Regression Channel', step=0.1, group='Future Projection Channel')
):
    col_dn: Color = color.new('#F01313')
    col_up: Color = color.aqua
    col_mid: Color = color.yellow
    gray: Color = color.gray
    fg_col: Color = chart.fg_color
    reglines: Persistent[list[Line]] = array.new_line(3)
    reglines_: Persistent[list[Line]] = array.new_line(3)
    def linear_regression(src: Series, window):
        sum_x: float = 0.0
        sum_y: float = 0.0
        sum_xy: float = 0.0
        sum_x_sq: float = 0.0
        for i in pine_range(0, window - 1, 1):
            sum_x = sum_x + i + 1
            sum_y = sum_y + src[i]
            sum_xy = sum_xy + (i + 1) * src[i]
            sum_x_sq = sum_x_sq + math.pow(i + 1, 2)
        slope = (window * sum_xy - sum_x * sum_y) / (window * sum_x_sq - math.pow(sum_x, 2))
        intercept = (sum_y - slope * sum_x) / window
        y1 = intercept + slope * (window - 1)
        dev: float = 0.0
        for i in pine_range(0, window - 1, 1):
            dev = dev + math.pow(src[i] - (slope * (window - i) + intercept), 2)
        dev = math.sqrt(dev / window)
        return (intercept, y1, dev, slope)

    y2, y1, dev, slope = linear_regression(close, window)
    y2_, y1_, dev_, slope_ = linear_regression(close, window1)
    y2__, y1__, dev__, slope__ = linear_regression(close, window2)
    mid: float = y2 + slope
    upper: float = mid + ta.rma(high - low, window) * devlen_b
    lower: float = mid - ta.rma(high - low, window) * devlen_b
    isAllowed = last_bar_index - bar_index < window1
    p_u = plot(upper, color=na if bands and channel else gray if bands else na, linewidth=2)
    p_l = plot(lower, color=na if bands and channel else gray if bands else na, linewidth=2)
    p_m = plot(mid, color=na if bands and channel else gray if bands else na)
    fill(p_u, p_m, mid, upper, na, na if bands and channel else color.new(col_up, 80) if bands else na)
    fill(p_m, p_l, lower, mid, na if bands and channel else color.new(col_dn, 80) if bands else na, na)
    if barstate.islast and channel:
        for i in pine_range(0, 2, 1):
            array.set(reglines, i, line.new(x1=bar_index - (window1 - 1), y1=y1_ + dev_ * devlen1 * (i - 1), x2=bar_index, y2=y2_ + dev_ * devlen1 * (i - 1), color=color.gray, style=line.style_dashed if i % 2 == 1 else line.style_solid, width=2, extend=extend.none))
        linefill.new(array.get(reglines, 1), array.get(reglines, 2), color=color.new(col_up, 90))
        linefill.new(array.get(reglines, 1), array.get(reglines, 0), color=color.new(col_dn, 90))
    if barstate.islast and channel1:
        for i in pine_range(0, 2, 1):
            array.set(reglines_, i, line.new(x1=bar_index - (window2 - 1), y1=y1__ + dev__ * devlen2 * (i - 1), x2=bar_index, y2=y2__ + dev__ * devlen2 * (i - 1), color=color.gray, style=line.style_dotted if i % 2 == 1 else line.style_dashed, width=1, extend=extend.right))
        linefill.new(array.get(reglines_, 1), array.get(reglines_, 2), color=color.new(col_up, 95))
        linefill.new(array.get(reglines_, 1), array.get(reglines_, 0), color=color.new(col_dn, 95))
    if arr_dirc:
        l1: Series = label.new(chart.point.from_index(bar_index, high if hl2 > y2__ else low), text='⇗' if hl2 > y2__ else '⇘' if hl2 < y2__ else '⇒', textcolor=col_up if hl2 > y2__ else col_dn if hl2 < y2__ else gray, color=NA(Color), size=size.huge, style=label.style_label_left)
        label.delete(l1[1])
    b_c = (close - lower) / (upper - lower)
    b_c = 1 if b_c > 1 else 0 if b_c < 0 else b_c
    bar_color = ((color.from_gradient(b_c, 0, 0.5, col_up, col_mid) if b_c <= 0.5 else color.from_gradient(b_c, 0.5, 1, col_mid, col_dn)) if isAllowed else na) if channel else color.from_gradient(b_c, 0.5, 1, col_mid, col_up) if b_c >= 0.5 else color.from_gradient(b_c, 0, 0.5, col_dn, col_mid)
    plotcandle(open, high, low, close, title='Bar HeatMap', color=bar_color, wickcolor=bar_color, bordercolor=bar_color)
    barcolor(bar_color)
    condition1 = na if bands and channel else ta.pivotlow(3, 3) and close < lower if bands else na
    condition2 = na if bands and channel else ta.pivothigh(3, 3) and close > upper if bands else na
    plotchar(condition1, '', '◆', size=size.tiny, location=location.belowbar, color=col_up)
    plotchar(condition2, '', '◆', size=size.tiny, location=location.abovebar, color=col_dn)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
