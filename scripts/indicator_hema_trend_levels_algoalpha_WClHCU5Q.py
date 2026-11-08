"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    alertcondition, array, bar_index, barcolor, box, chart, close, color,
    display, fill, high, input, location, low, math, na, open, plot, plotchar, plotshape, script,
    shape, size, ta
)
from pynecore.types import Box, Persistent


@script.indicator("HEMA Trend Levels [AlgoAlpha]", "AlgoAlpha - HEMA Trend ", overlay=True, max_boxes_count=500, explicit_plot_zorder=True)
def main(
    hemaLength1=input.int(20, title="HEMA Length Fast", group="HEMA Settings", tooltip="First HEMA period length (20 by default)"),
    hemaLength2=input.int(40, title="HEMA Length Slow", group="HEMA Settings", tooltip="Second HEMA period length (40 by default)"),
    bullColor=input.color(color.new('#00FFBB'), title="Bullish Color", tooltip="Color used for bullishness", group="Appearance"),
    bearColor=input.color(color.new('#FF1100'), title="Bearish Color", tooltip="Color used for bearishness", group="Appearance")
):
    def f_hema(_src, _length):
        halfLength = math.max(1, math.round(_length / 2))
        sqrtLength = math.max(1, math.round(math.sqrt(_length)))
        ema_half = ta.ema(_src, halfLength)
        ema_full = ta.ema(_src, _length)
        diff = 2 * ema_half - ema_full
        return ta.ema(diff, sqrtLength)

    hema1 = f_hema(close, hemaLength1)
    hema2 = f_hema(close, hemaLength2)

    hemaTop = plot(hema1 if hema1 > hema2 else hema2, 'Top HEMA', display=display.none)
    hemaBottom = plot(hema2 if hema1 > hema2 else hema1, 'Bottom HEMA', display=display.none)

    fillColor = bullColor if hema1 > hema2 else bearColor

    fill(hemaTop, hemaBottom, hema1, hema2, color.new(chart.bg_color, 100), color.new(fillColor, 70), 'HEMA Gradient')

    plot(hema1, title='HEMA 20', color=color.new(fillColor, 70))
    plot(hema2, title='HEMA 40', color=color.new(fillColor, 70))

    bullishCondition = close > hema1 and hema1 > hema2
    bearishCondition = close < hema1 and hema1 < hema2
    grayCondition = close < hema1 and hema1 > hema2 or (close > hema1 and hema1 < hema2)

    barcolor(color.new(bullColor, 50) if bullishCondition else color.new(bearColor, 50) if bearishCondition else color.new(color.gray, 50) if grayCondition else na)

    vola = ta.atr(14) / 2

    bull_box: Persistent[list[Box]] = array.new_box()
    bear_box: Persistent[list[Box]] = array.new_box()

    if ta.crossover(hema1, hema2):
        array.unshift(bull_box, box.new(bar_index, low + vola, bar_index + 5, low, bgcolor=color.new(bullColor, 70), border_color=color.new(color.black, 100)))
    elif ta.crossunder(hema1, hema2):
        array.unshift(bear_box, box.new(bar_index, high - vola, bar_index + 5, high, bgcolor=color.new(bearColor, 70), border_color=color.new(color.black, 100)))

    low_test: float = 0.0
    high_test: float = 0.0

    if array.size(bull_box) > 0:
        Q = array.first(bull_box)
        if low < method_call('get_top', Q) and high > method_call('get_top', Q) and (open > method_call('get_top', Q)) and (close > method_call('get_top', Q)):
            low_test = method_call('get_bottom', Q)
        method_call('set_right', Q, bar_index)

    if array.size(bear_box) > 0:
        Q = array.first(bear_box)
        if high > method_call('get_top', Q) and low < method_call('get_top', Q) and (open < method_call('get_top', Q)) and (close < method_call('get_top', Q)):
            high_test = method_call('get_bottom', Q)
        method_call('set_right', Q, bar_index)

    plotchar(low_test - vola if low_test != 0.0 else na, 'low_test', '▲', location.absolute, bullColor, size=size.tiny)
    plotchar(high_test + vola if high_test != 0.0 else na, 'high_test', '▼', location.absolute, bearColor, size=size.tiny)
    plotshape(low - vola * 3 if ta.crossover(hema1, hema2) else na, 'Bullish Trend', shape.labelup, location.absolute, color.new(bullColor, 50), text='▲', textcolor=chart.fg_color, size=size.small)
    plotshape(high + vola * 3 if ta.crossunder(hema1, hema2) else na, 'Bearish Trend', shape.labeldown, location.absolute, color.new(bearColor, 50), text='▼', textcolor=chart.fg_color, size=size.small)

    alertcondition(ta.crossover(hema1, hema2), title='Bullish Crossover', message='HEMA 20 crossed above HEMA 40 - Bullish Trend')
    alertcondition(ta.crossunder(hema1, hema2), title='Bearish Crossunder', message='HEMA 20 crossed below HEMA 40 - Bearish Trend')

    alertcondition(low_test != 0.0, title='Bullish Test', message='Price tested bullish box support')
    alertcondition(high_test != 0.0, title='Bearish Test', message='Price tested bearish box resistance')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
