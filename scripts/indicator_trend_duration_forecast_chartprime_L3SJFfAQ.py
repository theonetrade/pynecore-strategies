"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_cast import cast_int
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    array, bar_index, barstate, chart, close, color, input, label, line,
    math, plot, position, script, string, ta, table
)
from pynecore.types import Label, Line, NA, Persistent, PersistentSeries, Series


@script.indicator("Trend Duration Forecast [ChartPrime]", overlay=True)
def main(
    length=input.int(50, title="Smoothing Length", tooltip="Defines how many bars are used for the Hull Moving Average (HMA). A longer length smooths out short-term noise but increases lag."),
    trendLength=input.int(3, title="Trend Detection Sensitivity", tooltip="Controls how many consecutive bars are checked for rising/falling HMA slope. Lower values make trends switch faster, higher values make them more stable."),
    samples=input.int(10, title="Trend Sample Size", minval=2, tooltip="Defines how many past trend durations are stored to calculate the average probable trend length. Larger samples produce smoother probability estimates."),
    coloUP=input.color(color.rgb(18, 228, 158), "↑ Trend", inline="col"),
    coloDN=input.color(color.rgb(236, 86, 16), "↓ Trend", inline="col")
):
    trend: PersistentSeries = NA(bool)
    TrendCount: Persistent[int] = 0

    bullishCount: Persistent[list[int]] = array.new_int()
    bearishCount: Persistent[list[int]] = array.new_int()

    TrendUP: Persistent = NA(Label)
    TrendDN: Persistent = NA(Label)
    LengthLine: Persistent = NA(Line)
    LabelProbLen: Persistent = NA(Label)

    hma: Series[float] = ta.hma(close, length)

    if barstate.isconfirmed:
        if ta.rising(hma, trendLength):
            trend = True
        if ta.falling(hma, trendLength):
            trend = False

    if trend or not trend:
        TrendCount += 1

    if trend != trend[1]:
        method_call('delete', LengthLine)
        method_call('delete', LabelProbLen)
        method_call('set_tooltip', TrendUP, '')
        method_call('set_tooltip', TrendDN, '')

        if trend:
            array.push(bearishCount, TrendCount)
            TrendUP = label.new(bar_index, hma, 'Trend ↑\nProbable Length: ' + string.tostring(array.avg(bullishCount), '##'), color=color.new(coloUP, 100), textcolor=coloUP, style=label.style_label_up, tooltip='New bullish trend detected.\nShows Real length of the current bullish trend.')
            method_call('set_text', TrendDN, 'Trend ↓\n' + string.tostring(TrendCount) + '\n')
            LengthLine = line.new(bar_index - 1, hma[1], bar_index, hma[1], color=chart.fg_color, style=line.style_arrow_right)
            LabelProbLen = label.new(bar_index, hma[1], '', style=label.style_label_up, textcolor=chart.fg_color, color=color.new(color.white, 100), tooltip='Estimated extension of the current bullish trend based on average past durations.')
        else:
            array.push(bullishCount, TrendCount)
            TrendDN = label.new(bar_index, hma, 'Trend ↓\nProbable Length: ' + string.tostring(array.avg(bearishCount), '##'), color=color.new(coloDN, 100), textcolor=coloDN, style=label.style_label_down, tooltip='New bearish trend detected.\nShows Real length of the current bearish trend.')
            method_call('set_text', TrendUP, '\n' + string.tostring(TrendCount) + '\nTrend ↑')
            LengthLine = line.new(bar_index - 1, hma[1], bar_index, hma[1], color=chart.fg_color, style=line.style_arrow_right)
            LabelProbLen = label.new(bar_index, hma[1], '', style=label.style_label_down, textcolor=chart.fg_color, color=color.new(color.white, 100), tooltip='Estimated extension of the current bearish trend based on average past durations.')

        TrendCount = 0

    if not trend:
        method_call('set_text', TrendDN, 'Trend ↓\nReal Length: ' + string.tostring(TrendCount) + '\n')
        method_call('set_x2', LengthLine, method_call('get_x1', LengthLine) + array.avg(bearishCount) + 1)
        method_call('set_x', LabelProbLen, cast_int(math.avg(method_call('get_x1', LengthLine), method_call('get_x2', LengthLine))))
        method_call('set_text', LabelProbLen, 'Probable Length\n' + string.tostring(array.avg(bearishCount), '##'))
    else:
        method_call('set_text', TrendUP, 'Trend ↑\nReal Length: ' + string.tostring(TrendCount))
        method_call('set_x2', LengthLine, method_call('get_x1', LengthLine) + array.avg(bullishCount) + 1)
        method_call('set_x', LabelProbLen, cast_int(math.avg(method_call('get_x1', LengthLine), method_call('get_x2', LengthLine))))
        method_call('set_text', LabelProbLen, 'Probable Length\n' + string.tostring(array.avg(bullishCount), '##'))

    if array.size(bullishCount) > samples:
        array.shift(bullishCount)
    if array.size(bearishCount) > samples:
        array.shift(bearishCount)

    TColor = coloUP if trend else coloDN

    plot(hma, 'HMA', TColor, linewidth=3)

    tbl: Persistent = table.new(position.bottom_right, 100, 100)
    if barstate.islast:
        for i in pine_range(0, array.size(bullishCount) - 1):
            method_call('cell', tbl, 0, i + 1, string.tostring(i + 1), text_color=color.gray, tooltip='Sample index (1 = most recent trend)')

            lenBull = array.get(bullishCount, i)
            if i == 0:
                method_call('cell', tbl, 1, i, 'Trend ↑', text_color=coloUP, tooltip='Bullish trend length samples — based on detected rising HMA periods')
            method_call('cell', tbl, 1, i + 1, string.tostring(lenBull), text_color=chart.fg_color, tooltip='Duration of bullish trend #' + string.tostring(i + 1) + ' (' + string.tostring(lenBull) + ' bars)')

            lenBear = array.get(bearishCount, i)
            if i == 0:
                method_call('cell', tbl, 2, i, 'Trend ↓', text_color=coloDN, tooltip='Bearish trend length samples — based on detected falling HMA periods')
            method_call('cell', tbl, 2, i + 1, string.tostring(lenBear), text_color=chart.fg_color, tooltip='Duration of bearish trend #' + string.tostring(i + 1) + ' (' + string.tostring(lenBear) + ' bars)')

        method_call('cell', tbl, 1, array.size(bullishCount) + 1, string.tostring(array.avg(bullishCount), '##'), text_color=coloUP, tooltip='Average duration of recent bullish trends (' + string.tostring(array.avg(bullishCount), '##') + ' bars)')
        method_call('cell', tbl, 2, array.size(bearishCount) + 1, string.tostring(array.avg(bearishCount), '##'), text_color=coloDN, tooltip='Average duration of recent bearish trends (' + string.tostring(array.avg(bearishCount), '##') + ' bars)')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
