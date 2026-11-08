"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    bar_index, barstate, chart, close, color, display, fill, input, label,
    line, linefill, location, math, na, plot, plotshape, position, script, shape, size, string, ta,
    table
)
from pynecore.types import Color, Label, Line, Persistent, Series


@script.indicator("Logarithmic Regression Channel-Trend [BigBeluga]", "LogReg Channel-Trend [BigBeluga]", overlay=True)
def main(
    length=input.int(100, "Lookback Period"),
    channel_width=input.float(1.5, "Channel Width", step=0.1),
    channel_len=input(100, "Channel Length"),
    mid_disp=input.bool(True, "Mid Line", inline="s"),
    fill_band=input.bool(True, "Fill Band", inline="s"),
    col1=input.color(color.new('#21DFAC'), "", inline="s1"),
    col2=input.color(color.new('#DF216D'), "", inline="s1")
):
    def f_log_regression(src: Series, length):
        sumX: float = 0.0
        sumY: float = 0.0
        sumXSqr: float = 0.0
        sumXY: float = 0.0

        for i in pine_range(0, length - 1):
            val = math.log(src[i])
            per = i + 1.0
            sumX += per
            sumY += val
            sumXSqr += per * per
            sumXY += val * per

        slope = (length * sumXY - sumX * sumY) / (length * sumXSqr - sumX * sumX)
        average = sumY / length
        intercept = average - slope * sumX / length + slope

        return (slope, intercept)

    slope, intercept = f_log_regression(close, length)

    start: float = math.exp(intercept + slope * length)
    end: Series[float] = math.exp(intercept)
    diff: float = end - end[3]
    deviation: float = ta.stdev(close, length)
    up_sig: bool = ta.crossover(diff, 0) and barstate.isconfirmed
    dn_sig: bool = ta.crossunder(diff, 0) and barstate.isconfirmed

    color_up: Color = color.from_gradient(diff, ta.lowest(diff, 200), ta.highest(diff, 200), na, col1)
    color_dn: Color = color.from_gradient(diff, ta.lowest(diff, 200), ta.highest(diff, 200), col2, na)
    channel_col: Color = col1 if end > start else col2
    trend_col: Color = color_up if end > end[3] else color_dn
    trend_col1: Color = col1 if end > end[3] else col2

    p1 = plot(end, 'Log Regression', color=trend_col1, linewidth=2)
    p2 = plot(end[3], color=trend_col, display=display.none, editable=False)
    plotshape(end if up_sig else na, 'Up', shape.xcross, location.absolute, chart.fg_color, size=size.tiny)
    plotshape(end if dn_sig else na, 'Dn', shape.xcross, location.absolute, chart.fg_color, size=size.tiny)

    fill(p1, p2, trend_col if fill_band else na)

    up1: Persistent[Line] = na(Line)
    up: Persistent[Line] = na(Line)
    base: Persistent[Line] = na(Line)
    lw: Persistent[Line] = na(Line)
    lw1: Persistent[Line] = na(Line)
    lbl_t: Persistent[Label] = na(Label)

    if na(base) and mid_disp:
        base = line.new(bar_index[channel_len], start, bar_index, end, style=line.style_dashed)
    else:
        line.set_xy1(base, bar_index[channel_len], start)
        line.set_xy2(base, bar_index, end)
        line.set_color(base, chart.fg_color)

    if na(up1):
        up1 = line.new(bar_index[channel_len], start + deviation * (channel_width + 0.3), bar_index, end + deviation * (channel_width + 0.3), width=3)
    else:
        line.set_xy1(up1, bar_index[channel_len], start + deviation * (channel_width + 0.3))
        line.set_xy2(up1, bar_index, end + deviation * (channel_width + 0.3))
        line.set_color(up1, channel_col)

    if na(up):
        up = line.new(bar_index[channel_len], start + deviation * channel_width, bar_index, end + deviation * channel_width, width=1)
    else:
        line.set_xy1(up, bar_index[channel_len], start + deviation * channel_width)
        line.set_xy2(up, bar_index, end + deviation * channel_width)
        line.set_color(up, na)

    if na(lw):
        lw = line.new(bar_index[channel_len], start - deviation * channel_width, bar_index, end - deviation * channel_width, width=1)
    else:
        line.set_xy1(lw, bar_index[channel_len], start - deviation * channel_width)
        line.set_xy2(lw, bar_index, end - deviation * channel_width)
        line.set_color(lw, na)

    if na(lw1):
        lw1 = line.new(bar_index[channel_len], start - deviation * (channel_width + 0.3), bar_index, end - deviation * (channel_width + 0.3), width=3)
        lbl_t = label.new(bar_index[channel_len], start - deviation * (channel_width + 0.3))
    else:
        line.set_xy1(lw1, bar_index[channel_len], start - deviation * (channel_width + 0.3))
        line.set_xy2(lw1, bar_index, end - deviation * (channel_width + 0.3))
        line.set_color(lw1, channel_col)

        label.set_xy(lbl_t, bar_index[channel_len], start - deviation * (channel_width + 0.3))
        label.set_text(lbl_t, 'UP' if end > start else 'DN')
        label.set_style(lbl_t, label.style_label_lower_right if end < start else label.style_label_upper_right)
        label.set_color(lbl_t, channel_col)
        label.set_textcolor(lbl_t, color.new('#070F23'))

    linefill.new(lw, lw1, color.new(channel_col, 70))
    linefill.new(up, up1, color.new(channel_col, 70))

    if barstate.islast:
        dash = table.new(position.top_right, 10, 10, bgcolor=color.new(chart.fg_color, 90), border_color=chart.bg_color, border_width=5)
        method_call('cell', dash, 0, 0, 'Slope: ' + string.tostring(slope * 100, '#,###.###'), text_color=chart.fg_color)
        method_call('cell', dash, 0, 1, 'Log Regression Channel: ' + ('UP' if end > start else 'DN'), text_color=channel_col)
        method_call('cell', dash, 0, 2, 'Logarithmic Regression: ' + ('UP' if end > end[3] else 'DN'), text_color=color.new(trend_col, 0))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
