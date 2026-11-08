"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, barcolor, chart, close, color, format, high, input, label,
    low, na, open, plot, plotcandle, script, string, ta, volume
)
from pynecore.types import Color, NA, PersistentSeries, Series


@script.indicator("Market Shift Levels [ChartPrime]", max_labels_count=500, overlay=True)
def main(
    length=input.int(55, "Length"),
    __input_1__=input.string("Volume", "Label Data: ", options=("Volume", "Price")),
    color_shiftUp=input.color(color.rgb(36, 213, 128), "", inline="col"),
    color_shiftDn=input.color(color.rgb(225, 43, 43), "", inline="col")
):
    lbl_data: bool = __input_1__ == 'Volume'

    level: PersistentSeries = NA(float)
    hma1: Series[float] = ta.hma(close, length)
    hma2: float = hma1[5]
    vol_sum: float = volume[2] + volume[1] + volume

    if ta.crossover(hma1, hma2):
        level = low
    if ta.crossunder(hma1, hma2):
        level = high

    shift_col: Color = color_shiftDn if close < level else color_shiftUp

    plot(na if level != level[1] else level, 'Market Shift Levels', color=NA(Color) if bar_index % 2 == 0 else chart.fg_color, style=plot.style_linebr)

    if high[2] < level and high < level and (high[1] > level):
        label.new(bar_index - 1, high[1], string.tostring(vol_sum if lbl_data else high[1], format.volume if lbl_data else '#,####.###') + '\n⬙', color=NA(Color), textcolor=color.red, style=label.style_label_down)

    if low[2] > level and low[1] < level and (low > level):
        label.new(bar_index - 1, low[1], '⬘\n' + string.tostring(vol_sum if lbl_data else high[1], format.volume if lbl_data else '#,####.###'), color=NA(Color), textcolor=color.lime, style=label.style_label_up)

    barcolor(shift_col, title='Bar Color')
    plotcandle(open, high, low, close, title='Candles Color', color=shift_col, wickcolor=shift_col, bordercolor=shift_col, force_overlay=True)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
