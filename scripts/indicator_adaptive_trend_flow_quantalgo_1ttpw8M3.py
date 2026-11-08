"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, bar_index, barcolor, bgcolor, chart, close, color, fill,
    hlc3, input, label, math, na, plot, script, ta
)
from pynecore.types import Color, Persistent, Series

trend_settings: str = "════════ Trend Settings ════════"
visual_settings: str = "════════ Visualization Settings ════════"
tooltip_length: str = "Length of the trend calculation period. Higher values create smoother signals."
tooltip_smooth: str = "Smoothing period for volatility. Higher values reduce noise."
tooltip_sens: str = "Multiplier for volatility bands. Higher values create wider bands."
tooltip_bars: str = "Enable/disable bar coloring based on trend direction"
tooltip_bg: str = "Enable/disable background gradient coloring"
tooltip_signals: str = "Enable/disable signal markers on trend changes"


@script.indicator(title="Adaptive Trend Flow [QuantAlgo]", overlay=True, max_labels_count=500)
def main(
    length=input.int(10, "Main Length", minval=2, group=trend_settings, tooltip=tooltip_length),
    smooth_len=input.int(14, "Smoothing Length", minval=2, group=trend_settings, tooltip=tooltip_smooth),
    sensitivity=input.float(2.0, "Sensitivity", step=0.1, group=trend_settings, tooltip=tooltip_sens),
    bullcolor=input.color(color.new('#00FFAA'), "Bullish Color", group=visual_settings),
    bearcolor=input.color(color.new('#FF0000'), "Bearish Color", group=visual_settings),
    showbars=input.bool(True, "Color Bars?", group=visual_settings, tooltip=tooltip_bars),
    showbg=input.bool(True, "Background Color?", group=visual_settings, tooltip=tooltip_bg),
    showsignals=input.bool(True, "Show Signals?", group=visual_settings, tooltip=tooltip_signals)
):
    def calculate_trend_levels():
        typical = hlc3
        fast_ema = ta.ema(typical, length)
        slow_ema = ta.ema(typical, length * 2)
        basis = (fast_ema + slow_ema) / 2

        vol = ta.stdev(typical, length)
        smooth_vol = ta.ema(vol, smooth_len)

        upper = basis + smooth_vol * sensitivity
        lower = basis - smooth_vol * sensitivity

        return (basis, upper, lower)

    def get_trend_state(upper, lower, basis):
        prev_level: Persistent[float] = na(float)
        trend: Persistent[int] = 0

        if na(prev_level):
            trend = 1 if close > basis else -1
            prev_level = lower if trend == 1 else upper

        if trend == 1:
            if close < lower:
                trend = -1
                prev_level = upper
            else:
                prev_level = lower
        else:
            if close > upper:
                trend = 1
                prev_level = lower
            else:
                prev_level = upper

        return (trend, prev_level)

    basis, upper, lower = calculate_trend_levels()
    trend: Series
    trend, level = get_trend_state(upper, lower, basis)

    long_signal = trend == 1 and trend[1] == -1
    short_signal = trend == -1 and trend[1] == 1

    p2 = plot(basis, color=bullcolor if trend == 1 else bearcolor, linewidth=2)

    p1 = plot(level, color=bullcolor if close > level else bearcolor, linewidth=2, style=plot.style_linebr)

    plot(level, color=bullcolor if close > level else bearcolor, linewidth=2, style=plot.style_linebr)

    if showsignals and ta.crossunder(close, level):
        label.new(bar_index, level, '𝑺', color=bearcolor, textcolor=chart.fg_color, style=label.style_label_lower_right)

    if showsignals and ta.crossover(close, level):
        label.new(bar_index, level, '𝑳', color=bullcolor, textcolor=chart.bg_color, style=label.style_label_upper_right)

    intensity: Persistent[float] = 0.0
    prev_trend: Persistent[int] = 0

    if trend != prev_trend:
        intensity = 0.0
        prev_trend = trend

    intensity = math.min(intensity + 1, 20) if trend == 1 else math.min(intensity + 1, 20) if trend == -1 else intensity

    grad_color: Color = color.from_gradient(intensity, 0, 20, color.new(bullcolor, 95), color.new(bullcolor, 80)) if trend == 1 else color.from_gradient(intensity, 0, 20, color.new(bearcolor, 95), color.new(bearcolor, 80))

    bgcolor(grad_color if showbg else na)

    fill(p1, p2, level, basis, bullcolor if trend == 1 else bearcolor, na)
    fill(p1, p2, level, basis, bullcolor if trend == 1 else bearcolor, na)

    barcolor((color.new(bullcolor, 15) if trend == 1 else color.new(bearcolor, 15)) if showbars else na)

    alertcondition(long_signal, title='Adaptive Trend Flow Long', message='Adaptive Trend Flow Long {{exchange}}:{{ticker}}')
    alertcondition(short_signal, title='Adaptive Trend Flow Short', message='Adaptive Trend Flow Short {{exchange}}:{{ticker}}')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
