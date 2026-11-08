"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method, method_call
from pynecore.lib import (
    bar_index, box, chart, close, color, fill, high, input, label, location,
    low, math, na, plot, plotshape, script, shape, size, string, ta, text
)
from pynecore.types import Box, Color, NA, Persistent, Series


@script.indicator('Zero-Lag MA Trend Levels [ChartPrime]', overlay=True, na_bool=True)
def main(
    length=input.int(15, title='Length'),
    show_levl=input.bool(True, 'Trend Levels'),
    up=input.color(color.new('#30D453'), '+', group='Colors', inline='i'),
    dn=input.color(color.new('#4043F1'), '-', group='Colors', inline='i')
):
    box1: Persistent = NA(Box)
    atr: float = ta.atr(200)
    emaValue: float = ta.ema(close, length)
    correction: float = close + close - emaValue
    zlma: Series[float] = ta.ema(correction, length)
    signalUp: bool = ta.crossover(zlma, emaValue)
    signalDn: bool = ta.crossunder(zlma, emaValue)
    zlma_color: Color = up if zlma > zlma[3] else dn if zlma < zlma[3] else na
    ema_col: Color = up if emaValue < zlma else dn
    p1 = plot(zlma, color=zlma_color, linewidth=1)
    p2 = plot(emaValue, color=ema_col, linewidth=1)
    fill(p1, p2, zlma, emaValue, color.new(zlma_color, 80), color.new(ema_col, 80))
    @method
    def draw_box(col: Color, top, bot, price):
        return box.new(bar_index, top, bar_index, bot, col, 1, bgcolor=color.new(col, 90), text=string.tostring(math.round(price, 2)), text_size=size.tiny, text_color=chart.fg_color, text_halign=text.align_right)

    if show_levl:
        check_signals: Series[bool] = signalUp or signalDn
        if signalUp:
            box1 = draw_box(up, zlma, zlma - atr, close)
        elif signalDn:
            box1 = draw_box(dn, zlma + atr, zlma, close)
        if not signalUp or not signalDn:
            method_call('set_right', box1, bar_index + 4)
        else:
            box1 = NA(Box)
        if ta.crossunder(high, method_call('get_bottom', box1)) and (not check_signals[1]) and (not check_signals) and (emaValue > zlma):
            label.new(bar_index - 1, high[1], '▼', color=NA(Color), textcolor=dn, style=label.style_label_down)
        elif ta.crossover(low, method_call('get_top', box1)) and (not check_signals) and (not check_signals[1]) and (emaValue < zlma):
            label.new(bar_index - 1, low[1], '▲', color=NA(Color), textcolor=up, style=label.style_label_up)
    plotshape(zlma if signalUp else na, '', shape.diamond, location.absolute, color=up, size=size.tiny)
    plotshape(zlma if signalDn else na, '', shape.diamond, location.absolute, color=dn, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
