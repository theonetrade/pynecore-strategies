"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_import import shadowed_namespace
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    alertcondition, array, bar_index, barstate, chart, close, color, display,
    fill, hl2, input, label, location, math, na, nz, open, plot, plotshape, position, script,
    shape, size, string, ta, table, text
)
from pynecore.types import Persistent, Series
import lib.TradingView.ta.v7 as ta__ren____lib


ta__ren__ = shadowed_namespace(ta__ren____lib, ta)


@script.indicator('Machine Learning Adaptive SuperTrend [AlgoAlpha]', 'AlgoAlpha - 🤖 Adaptive SuperTrend', overlay=True, max_labels_count=500)
def main(
    atr_len=input.int(10, 'ATR Length', group='SuperTrend Settings'),
    fact=input.float(3, 'SuperTrend Factor', group='SuperTrend Settings'),
    training_data_period=input.int(100, 'Training Data Length', group='K-Means Settings'),
    highvol=input.float(0.75, 'Initial High volatility Percentile Guess', maxval=1, group='K-Means Settings', tooltip='The initial guess of where the potential \'high volatility\' area is, a value of 0.75 will take the 75th percentile of the range of ATR values over the training data period'),
    midvol=input.float(0.5, 'Initial Medium volatility Percentile Guess', maxval=1, group='K-Means Settings', tooltip='The initial guess of where the potential \'medium volatility\' area is, a value of 0.5 will take the 50th percentile of the range of ATR values over the training data period'),
    lowvol=input.float(0.25, 'Initial Low volatility Percentile Guess', maxval=1, group='K-Means Settings', tooltip='The initial guess of where the potential \'low volatility\' area is, a value of 0.25 will take the 25th percentile of the range of ATR values over the training data period'),
    t1=input.int(70, 'Transparency 1', maxval=100, minval=0, group='Appearance'),
    t2=input.int(95, 'Transparency 2', maxval=100, minval=0, group='Appearance'),
    green=input.color(color.new('#00FFBB'), 'Bullish Color', group='Appearance'),
    red=input.color(color.new('#FF1100'), 'Bearish Color', group='Appearance')
):
    def pine_supertrend(factor, atr: Series):
        src = hl2
        upperBand: Series = src + factor * atr
        lowerBand: Series = src - factor * atr
        prevLowerBand = nz(lowerBand[1])
        prevUpperBand = nz(upperBand[1])
        lowerBand = lowerBand if lowerBand > prevLowerBand or close[1] < prevLowerBand else prevLowerBand
        upperBand = upperBand if upperBand < prevUpperBand or close[1] > prevUpperBand else prevUpperBand
        _direction: int = na(int)
        superTrend: Series[float] = na(float)
        prevSuperTrend = superTrend[1]
        if na(atr[1]):
            _direction = 1
        elif prevSuperTrend == prevUpperBand:
            _direction = -1 if close > upperBand else 1
        else:
            _direction = 1 if close < lowerBand else -1
        superTrend = lowerBand if _direction == -1 else upperBand
        return (superTrend, _direction)

    volatility: Series = ta__ren__.atr(atr_len)
    upper = ta__ren__.highest(volatility, training_data_period)
    lower = ta__ren__.lowest(volatility, training_data_period)
    high_volatility = lower + (upper - lower) * highvol
    medium_volatility = lower + (upper - lower) * midvol
    low_volatility = lower + (upper - lower) * lowvol
    iterations: int = 0
    size_a: int = 0
    size_b: int = 0
    size_c: int = 0
    hv: list[float] = array.new_float()
    mv: list[float] = array.new_float()
    lv: list[float] = array.new_float()
    amean: list[float] = array.new_float(1, high_volatility)
    bmean: list[float] = array.new_float(1, medium_volatility)
    cmean: list[float] = array.new_float(1, low_volatility)
    if nz(volatility) > 0 and bar_index >= training_data_period - 1:
        while (True if array.size(amean) == 1 else array.first(amean) != array.get(amean, 1)) or (True if array.size(bmean) == 1 else array.first(bmean) != array.get(bmean, 1)) or (True if array.size(cmean) == 1 else array.first(cmean) != array.get(cmean, 1)):
            array.clear(hv)
            array.clear(mv)
            array.clear(lv)
            for i in pine_range(training_data_period - 1, 0, 1):
                _1 = math.abs(volatility[i] - array.first(amean))
                _2 = math.abs(volatility[i] - array.first(bmean))
                _3 = math.abs(volatility[i] - array.first(cmean))
                if _1 < _2 and _1 < _3:
                    array.unshift(hv, volatility[i])
                if _2 < _1 and _2 < _3:
                    array.unshift(mv, volatility[i])
                if _3 < _1 and _3 < _2:
                    array.unshift(lv, volatility[i])
            array.unshift(amean, array.avg(hv))
            array.unshift(bmean, array.avg(mv))
            array.unshift(cmean, array.avg(lv))
            size_a = array.size(hv)
            size_b = array.size(mv)
            size_c = array.size(lv)
            iterations = iterations + 1
    hv_new = array.first(amean)
    mv_new = array.first(bmean)
    lv_new = array.first(cmean)
    vdist_a = math.abs(volatility - hv_new)
    vdist_b = math.abs(volatility - mv_new)
    vdist_c = math.abs(volatility - lv_new)
    distances: list[float] = array.new_float()
    centroids: list[float] = array.new_float()
    array.push(distances, vdist_a)
    array.push(distances, vdist_b)
    array.push(distances, vdist_c)
    array.push(centroids, hv_new)
    array.push(centroids, mv_new)
    array.push(centroids, lv_new)
    cluster: Series = array.indexof(distances, array.min(distances))
    assigned_centroid = na if cluster == -1 else array.get(centroids, cluster)
    ST, dir = pine_supertrend(fact, assigned_centroid)
    upTrend = plot(ST if close > ST else na, color=color.new(green, t1), style=plot.style_linebr)
    downTrend = plot(ST if close < ST else na, color=color.new(red, t1), style=plot.style_linebr, force_overlay=False)
    bodyMiddle = plot(na if barstate.isfirst else (open + close) / 2, 'Body Middle', display=display.none)
    fill(bodyMiddle, upTrend, (open + close) / 2, ST, color.new(green, t2), color.new(green, t1))
    fill(bodyMiddle, downTrend, ST, (open + close) / 2, color.new(red, t1), color.new(red, t2))
    plotshape(ST if ta__ren__.crossunder(dir, 0) else na, 'Bullish Trend', shape.labelup, location.absolute, green, text='▲', textcolor=chart.fg_color, size=size.small)
    plotshape(ST if ta__ren__.crossover(dir, 0) else na, 'Bearish Trend', shape.labeldown, location.absolute, red, text='▼', textcolor=chart.fg_color, size=size.small)
    label.new(bar_index, ST + ta__ren__.atr(7) if dir > 0 else ST - ta__ren__.atr(7), text=string.tostring(4 - (cluster + 1)), style=label.style_none, textcolor=color.from_gradient(cluster + 1, 1, 3, color.new(red if dir > 0 else green, 30), color.new(red if dir > 0 else green, 90)))
    if barstate.islast:
        data_table: Persistent = table.new(position=position.top_right, columns=4, rows=4, bgcolor=chart.bg_color, border_width=1, border_color=chart.fg_color, frame_color=chart.fg_color, frame_width=1)
        table.cell(data_table, text_halign=text.align_center, column=0, row=0, text='Cluster Number (Volatility Level)', text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=0, text='Cluster Centroid (ATR)', text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=2, row=0, text='Cluster Size (No. of Data Points in Each Cluster)', text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=3, row=0, text='Current Volatility', text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=0, row=1, text='3 (High)', text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=0, row=2, text='2 (Medium)', text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=0, row=3, text='1 (Low)', text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=1, text=string.format('{0,number,#.##}', hv_new), text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=2, text=string.format('{0,number,#.##}', mv_new), text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=1, row=3, text=string.format('{0,number,#.##}', lv_new), text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=2, row=1, text=string.format('{0,number,#.##}', size_c), text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=2, row=2, text=string.format('{0,number,#.##}', size_b), text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=2, row=3, text=string.format('{0,number,#.##}', size_a), text_color=chart.fg_color)
        table.cell(data_table, text_halign=text.align_center, column=3, row=1, text='HIGH ' + '(ATR: ' + string.format('{0,number,#.##}', volatility) + ')', text_color=chart.bg_color)
        table.cell(data_table, text_halign=text.align_center, column=3, row=2, text='MEDIUM ' + '(ATR: ' + string.format('{0,number,#.##}', volatility) + ')', text_color=chart.bg_color)
        table.cell(data_table, text_halign=text.align_center, column=3, row=3, text='LOW ' + '(ATR: ' + string.format('{0,number,#.##}', volatility) + ')', text_color=chart.bg_color)
        if cluster == 0:
            method_call('cell_set_bgcolor', data_table, 3, 1, chart.fg_color)
        else:
            method_call('cell_set_bgcolor', data_table, 3, 1, chart.bg_color)
        if cluster == 1:
            method_call('cell_set_bgcolor', data_table, 3, 2, chart.fg_color)
        else:
            method_call('cell_set_bgcolor', data_table, 3, 2, chart.bg_color)
        if cluster == 2:
            method_call('cell_set_bgcolor', data_table, 3, 3, chart.fg_color)
        else:
            method_call('cell_set_bgcolor', data_table, 3, 3, chart.bg_color)
    alertcondition(ta__ren__.crossunder(dir, 0) and barstate.isconfirmed, 'Bullish Trend Shift')
    alertcondition(ta__ren__.crossover(dir, 0) and barstate.isconfirmed, 'Bearish Trend Shift')
    alertcondition(cluster == 0 and cluster[1] != 0 and barstate.isconfirmed, 'High Volatility')
    alertcondition(cluster == 1 and cluster[1] != 1 and barstate.isconfirmed, 'Medium Volatility')
    alertcondition(cluster == 2 and cluster[1] != 2 and barstate.isconfirmed, 'Low Volatility')
    alertcondition(cluster == 2 and cluster[1] != 2 and barstate.isconfirmed, 'Low Volatility')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)