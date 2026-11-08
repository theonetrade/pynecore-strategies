"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    array, bar_index, chart, close, color, format, high, input, label, line,
    location, low, na, open, plot, plotcandle, plotshape, script, shape, size, string, ta, volume
)
from pynecore.types import Color, Line, NA, Persistent, PersistentSeries, Series


@script.indicator('Market Structure Trailing Stop [BigBeluga]', 'MS TrailingStop [BigBeluga]', overlay=True, max_lines_count=500, max_labels_count=500, na_bool=True)
def main(
    leftBars=input(8, 'Highs & Lows'),
    use_ts=input.bool(False, '', inline='1'),
    trail_len=input.int(25, 'Trailing Stop', inline='1'),
    volume_threshold=input.int(500, 'Volume 𝄛', inline='1', tooltip='Filter TrailingStop by Volume Size'),
    use_bos=input.bool(False, 'BoS', tooltip='Show Break of Structure', inline='2'),
    sweep_x=input.bool(False, 'Liquidity Sweep (X)', tooltip='if BoS Displayed Show Liquidity Sweeps (X)', inline='2'),
    trend_col=input.bool(False, 'Market Trend')
):
    rightBars: int = leftBars
    up: Color = color.new('#1FC0B0')
    dn: Color = color.new('#D11C43')
    ph = ta.pivothigh(leftBars, rightBars)
    pl = ta.pivotlow(leftBars, rightBars)
    upper_line: PersistentSeries = NA(Line)
    lower_line: PersistentSeries = NA(Line)
    count1: Persistent[int] = 0
    count2: Persistent[int] = 0
    n1: Persistent[int] = 0
    n2: Persistent[int] = 0
    count_trend1: Persistent[int] = 0
    count_trend2: Persistent[int] = 0
    volume_1: Persistent[list[float]] = array.new_float()
    volume_2: Persistent[list[float]] = array.new_float()
    if not na(ph):
        upper_line = line.new(bar_index[rightBars], high[rightBars], bar_index[rightBars], high[rightBars], force_overlay=True)
        n1 = bar_index[rightBars]
    if not na(pl):
        lower_line = line.new(bar_index[rightBars], low[rightBars], bar_index[rightBars], low[rightBars], force_overlay=True)
        n2 = bar_index[rightBars]
    if high > method_call('get_y1', upper_line) and low < method_call('get_y1', upper_line):
        count1 = count1 + 1
        count2 = 0
        line.set_color(upper_line[1], up)
        line.set_style(upper_line[1], line.style_dashed)
        line.set_x2(upper_line[1], bar_index)
        if count1 == 1:
            array.clear(volume_1)
            for i in pine_range(0, bar_index - n1, 1):
                array.push(volume_1, volume[i] if close[i] > open[i] else -volume[i])
            line.set_style(upper_line[1], line.style_solid)
            label.new(n1, line.get_y1(upper_line[1]), string.tostring(array.sum(volume_1), format.volume) + '\nCHoCh', color=NA(Color), style=label.style_label_down, textcolor=chart.fg_color)
        if count1 > 1 and use_bos:
            index = bar_index - (bar_index - n1) / 2
            array.clear(volume_1)
            for i in pine_range(0, bar_index - n1, 1):
                array.push(volume_1, volume[i] if close[i] > open[i] else -volume[i])
            line.set_style(upper_line[1], line.style_solid)
            lbl1 = label.new(index, line.get_y1(upper_line[1]), string.tostring(array.sum(volume_1), format.volume) + '\nBoS', color=NA(Color), style=label.style_label_down, textcolor=up, size=size.small, force_overlay=True)
            if close < open and high > method_call('get_y1', upper_line) and (open < method_call('get_y1', upper_line)) and sweep_x:
                method_call('delete', lbl1)
                label.new(index, line.get_y1(upper_line[1]), string.tostring(array.sum(volume_1), format.volume) + '\n✖', color=NA(Color), style=label.style_label_down, textcolor=up, force_overlay=True)
        upper_line = NA(Line)
    if high > method_call('get_y1', lower_line) and low < method_call('get_y1', lower_line):
        count2 = count2 + 1
        count1 = 0
        line.set_color(lower_line[1], dn)
        line.set_style(lower_line[1], line.style_dashed)
        line.set_x2(lower_line[1], bar_index)
        if count2 == 1:
            array.clear(volume_2)
            for i in pine_range(0, bar_index - n2, 1):
                array.push(volume_2, volume[i] if close[i] > open[i] else -volume[i])
            line.set_style(lower_line[1], line.style_solid)
            label.new(n2, line.get_y1(lower_line[1]), 'CHoCh\n' + string.tostring(array.sum(volume_2), format.volume), color=NA(Color), style=label.style_label_up, textcolor=chart.fg_color)
        if count2 > 1 and use_bos:
            index = bar_index - (bar_index - n2) / 2
            array.clear(volume_2)
            for i in pine_range(0, bar_index - n2, 1):
                array.push(volume_2, volume[i] if close[i] > open[i] else -volume[i])
            line.set_style(lower_line[1], line.style_solid)
            lbl2 = label.new(index, line.get_y1(lower_line[1]), 'BoS\n' + string.tostring(array.sum(volume_2), format.volume), color=NA(Color), style=label.style_label_up, textcolor=dn, size=size.small, force_overlay=True)
            if close < open and low < method_call('get_y1', lower_line) and (close > method_call('get_y1', lower_line)) and sweep_x:
                method_call('delete', lbl2)
                label.new(index, line.get_y1(lower_line[1]), '✖\n' + string.tostring(array.sum(volume_2), format.volume), color=NA(Color), style=label.style_label_up, textcolor=dn, force_overlay=True)
        lower_line = NA(Line)
    if count1 > 0:
        count_trend2 = 0
        count_trend1 = count_trend1 + 1
    if count2 > 0:
        count_trend1 = 0
        count_trend2 = count_trend2 + 1
    H: Series = ta.highest(trail_len)
    L: Series = ta.lowest(trail_len)
    band: Series = L if count_trend1 > 0 and L[1] <= L and (L[2] <= L[1]) and (L[3] <= L[2]) and (L[4] <= L[3]) and (L[5] <= L[4]) and (array.sum(volume_1) > volume_threshold) and use_ts else H if count_trend2 > 0 and H[1] >= H and (H[2] >= H[1]) and (H[3] >= H[2]) and (H[4] >= H[3]) and (H[5] >= H[4]) and (array.sum(volume_2) < -volume_threshold) and use_ts else na
    if use_ts:
        if ta.crossover(close, band) or (close > band and na(band[1]) and (not na(band))):
            label.new(bar_index, band, 'B', color=color.new(color.lime, 50), style=label.style_label_up, textcolor=chart.fg_color, size=size.tiny, force_overlay=True)
        if ta.crossunder(close, band) or (close < band and na(band[1]) and (not na(band))):
            label.new(bar_index, band, 'S', color=color.new(color.new('#DF1E1E'), 50), style=label.style_label_down, textcolor=chart.fg_color, size=size.tiny, force_overlay=True)
    plot(na if ta.cross(close, band) else band, style=plot.style_linebr, color=color.new(up, 20) if close > band else color.new(dn, 20), force_overlay=True)
    plot(na if ta.cross(close, band) else band, style=plot.style_linebr, color=color.new(up, 80) if close > band else color.new(dn, 80), linewidth=5, force_overlay=True)
    plotshape(high[rightBars] if not na(ph) else na, '', shape.circle, location.absolute, offset=-rightBars, color=up, force_overlay=True)
    plotshape(low[rightBars] if not na(pl) else na, '', shape.circle, location.absolute, offset=-rightBars, color=dn, force_overlay=True)
    plotshape(high[rightBars] if not na(ph) else na, '', shape.circle, location.absolute, offset=-rightBars, color=color.new(up, 50), size=size.tiny, force_overlay=True)
    plotshape(low[rightBars] if not na(pl) else na, '', shape.circle, location.absolute, offset=-rightBars, color=color.new(dn, 50), size=size.tiny, force_overlay=True)
    color_trend = (up if count_trend1 > 0 else dn if count_trend2 > 0 else na) if trend_col else na
    plotcandle(open, high, low, close, title='Candle Trend', color=color_trend, wickcolor=color_trend, bordercolor=color_trend)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
