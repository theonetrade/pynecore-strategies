"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from dataclasses import field as _dataclass_field
from pynecore import pine_range
from pynecore.core.pine_cast import cast_bool, cast_int
from pynecore.core.pine_method import method_call
from pynecore.core.pine_udt import udt
from pynecore.lib import (
    array, bar_index, barcolor, barstate, close, color, hl2, input, label,
    last_bar_index, math, na, nz, plot, position, runtime, script, size, string, ta, table, text
)
from pynecore.types import NA, Persistent, PersistentSeries, Series


@udt
class supertrend:
    upper: float = _dataclass_field(default_factory=lambda: hl2)
    lower: float = _dataclass_field(default_factory=lambda: hl2)
    output: float = na(float)
    perf: float = 0
    factor: float = na(float)
    trend: int = 0


@udt
class vector:
    out: list[float] = na(list)


@script.indicator('SuperTrend AI (Clustering) [LuxAlgo]', 'LuxAlgo - SuperTrend AI', overlay=True, max_labels_count=500)
def main(
    length=input(10, 'ATR Length'),
    minMult=input.int(1, 'Factor Range', minval=0, inline='factor'),
    maxMult=input.int(5, '', minval=0, inline='factor'),
    step=input.float(0.5, 'Step', minval=0, step=0.1),
    perfAlpha=input.float(10, 'Performance Memory', minval=2),
    fromCluster=input.string('Best', 'From Cluster', options=('Best', 'Average', 'Worst')),
    maxIter=input.int(1000, 'Maximum Iteration Steps', minval=0, group='Optimization'),
    maxData=input.int(10000, 'Historical Bars Calculation', minval=0, group='Optimization'),
    bearCss=input(color.red, 'Trailing Stop', inline='ts', group='Style'),
    bullCss=input(color.teal, '', inline='ts', group='Style'),
    amaBearCss=input(color.new(color.red, 50), 'AMA', inline='ama', group='Style'),
    amaBullCss=input(color.new(color.teal, 50), '', inline='ama', group='Style'),
    showGradient=input(True, 'Candle Coloring', group='Style'),
    showSignals=input(True, 'Show Signals', group='Style'),
    showDash=input(True, 'Show Dashboard', group='Dashboard'),
    dashLoc=input.string('Top Right', 'Location', options=('Top Right', 'Bottom Right', 'Bottom Left'), group='Dashboard'),
    textSize=input.string('Small', 'Size', options=('Tiny', 'Small', 'Normal'), group='Dashboard')
):
    if minMult > maxMult:
        runtime.error('Minimum factor is greater than maximum factor in the range')
    holder: Persistent[list[supertrend]] = array.new(0, NA(supertrend))
    factors: Persistent[list[float]] = array.new_float(0)
    if barstate.isfirst:
        for i in pine_range(0, cast_int((maxMult - minMult) / step), 1):
            array.push(factors, minMult + i * step)
            array.push(holder, supertrend())
    atr = ta.atr(length)
    k: int = 0
    for factor in factors:
        get_spt = array.get(holder, k)
        up__0000002b__ = hl2 + atr * factor
        dn__0000002b__ = hl2 - atr * factor
        get_spt.trend = 1 if close > get_spt.upper else 0 if close < get_spt.lower else get_spt.trend
        get_spt.upper = math.min(up__0000002b__, get_spt.upper) if close[1] < get_spt.upper else up__0000002b__
        get_spt.lower = math.max(dn__0000002b__, get_spt.lower) if close[1] > get_spt.lower else dn__0000002b__
        diff = nz(math.sign(close[1] - get_spt.output))
        get_spt.perf = get_spt.perf + 2 / (perfAlpha + 1) * (nz(close - close[1]) * diff - get_spt.perf)
        get_spt.output = get_spt.lower if get_spt.trend == 1 else get_spt.upper
        get_spt.factor = factor
        k = k + 1
    factor_array: list[float] = array.new_float(0)
    data: list[float] = array.new_float(0)
    if last_bar_index - bar_index <= maxData:
        for element in holder:
            array.push(data, element.perf)
            array.push(factor_array, element.factor)
    centroids: list[float] = array.new_float(0)
    array.push(centroids, array.percentile_linear_interpolation(data, 25))
    array.push(centroids, array.percentile_linear_interpolation(data, 50))
    array.push(centroids, array.percentile_linear_interpolation(data, 75))
    factors_clusters: Persistent[list[vector]] = na(list[vector])
    perfclusters: Persistent[list[vector]] = na(list[vector])
    if last_bar_index - bar_index <= maxData:
        for _ in pine_range(0, maxIter, 1):
            factors_clusters = array.from_items(vector(array.new_float(0)), vector(array.new_float(0)), vector(array.new_float(0)))
            perfclusters = array.from_items(vector(array.new_float(0)), vector(array.new_float(0)), vector(array.new_float(0)))
            i: int = 0
            for value in data:
                dist: list[float] = array.new_float(0)
                for centroid in centroids:
                    array.push(dist, math.abs(value - centroid))
                idx = array.indexof(dist, array.min(dist))
                method_call('push', array.get(perfclusters, idx).out, value)
                method_call('push', array.get(factors_clusters, idx).out, array.get(factor_array, i))
                i = i + 1
            new_centroids: list[float] = array.new_float(0)
            for cluster_ in perfclusters:
                array.push(new_centroids, array.avg(cluster_.out))
            if array.get(new_centroids, 0) == array.get(centroids, 0) and array.get(new_centroids, 1) == array.get(centroids, 1) and (array.get(new_centroids, 2) == array.get(centroids, 2)):
                break
            centroids = new_centroids
    target_factor: Persistent[float] = na(float)
    perf_idx: Persistent[float] = na(float)
    perf_ama: Persistent[float] = na(float)
    __block_result__ = na
    __switch__ = fromCluster
    if __switch__ == 'Best':
        __block_result__ = 2
    elif __switch__ == 'Average':
        __block_result__ = 1
    elif __switch__ == 'Worst':
        __block_result__ = 0
    from__ren__: Persistent = __block_result__
    den = ta.ema(math.abs(close - close[1]), cast_int(perfAlpha))
    if not na(perfclusters):
        target_factor = nz(method_call('avg', array.get(factors_clusters, from__ren__).out), target_factor)
        perf_idx = math.max(nz(method_call('avg', array.get(perfclusters, from__ren__).out)), 0) / den
    upper: Persistent = hl2
    lower: Persistent = hl2
    os: PersistentSeries[int] = 0
    up = hl2 + atr * target_factor
    dn = hl2 - atr * target_factor
    upper = math.min(up, upper) if close[1] < upper else up
    lower = math.max(dn, lower) if close[1] > lower else dn
    os = 1 if close > upper else 0 if close < lower else os
    ts: Series = lower if cast_bool(os) else upper
    if na(ts[1]) and (not na(ts)):
        perf_ama = ts
    else:
        perf_ama = perf_ama + perf_idx * (ts - perf_ama)
    table_position: Persistent = position.bottom_left if dashLoc == 'Bottom Left' else position.top_right if dashLoc == 'Top Right' else position.bottom_right
    table_size: Persistent = size.tiny if textSize == 'Tiny' else size.small if textSize == 'Small' else size.normal
    tb: Persistent = table.new(table_position, 4, 4, bgcolor=color.new('#1E222D'), border_color=color.new('#373A46'), border_width=1, frame_color=color.new('#373A46'), frame_width=1)
    if showDash:
        if barstate.isfirst:
            method_call('cell', tb, 0, 0, 'Cluster', text_color=color.white, text_size=table_size)
            method_call('cell', tb, 0, 1, 'Best', text_color=color.white, text_size=table_size)
            method_call('cell', tb, 0, 2, 'Average', text_color=color.white, text_size=table_size)
            method_call('cell', tb, 0, 3, 'Worst', text_color=color.white, text_size=table_size)
            method_call('cell', tb, 1, 0, 'Size', text_color=color.white, text_size=table_size)
            method_call('cell', tb, 2, 0, 'Centroid Dispersion', text_color=color.white, text_size=table_size)
            method_call('cell', tb, 3, 0, 'Factors', text_color=color.white, text_size=table_size)
        if barstate.islast:
            topN = method_call('size', array.get(perfclusters, 2).out)
            midN = method_call('size', array.get(perfclusters, 1).out)
            btmN = method_call('size', array.get(perfclusters, 0).out)
            method_call('cell', tb, 1, 1, string.tostring(topN), text_color=color.white, text_size=table_size)
            method_call('cell', tb, 1, 2, string.tostring(midN), text_color=color.white, text_size=table_size)
            method_call('cell', tb, 1, 3, string.tostring(btmN), text_color=color.white, text_size=table_size)
            method_call('cell', tb, 3, 1, string.tostring(array.get(factors_clusters, 2).out), text_color=color.white, text_size=table_size, text_halign=text.align_left)
            method_call('cell', tb, 3, 2, string.tostring(array.get(factors_clusters, 1).out), text_color=color.white, text_size=table_size, text_halign=text.align_left)
            method_call('cell', tb, 3, 3, string.tostring(array.get(factors_clusters, 0).out), text_color=color.white, text_size=table_size, text_halign=text.align_left)
            i: int = 0
            for cluster_ in perfclusters:
                disp: float = 0.0
                if array.size(cluster_.out) > 1:
                    for value in cluster_.out:
                        disp = disp + math.abs(value - array.get(centroids, i))
                __block_result_1__ = na
                __switch_3__ = i
                if __switch_3__ == 0:
                    __block_result_1__ = btmN
                elif __switch_3__ == 1:
                    __block_result_1__ = midN
                elif __switch_3__ == 2:
                    __block_result_1__ = topN
                disp /= __block_result_1__
                i = i + 1
                method_call('cell', tb, 2, 4 - i, string.tostring(disp, '#.####'), text_color=color.white, text_size=table_size)
    css = bullCss if cast_bool(os) else bearCss
    plot(ts, 'Trailing Stop', na if os != os[1] else css)
    plot(perf_ama, 'Trailing Stop AMA', na if ta.cross(close, perf_ama) else amaBullCss if close > perf_ama else amaBearCss)
    barcolor(color.from_gradient(perf_idx, 0, 1, color.new(css, 80), css) if showGradient else na)
    n = bar_index
    if showSignals:
        if os > os[1]:
            label.new(n, ts, string.tostring(cast_int(perf_idx * 10)), color=bullCss, style=label.style_label_up, textcolor=color.white, size=size.tiny)
        if os < os[1]:
            label.new(n, ts, string.tostring(cast_int(perf_idx * 10)), color=bearCss, style=label.style_label_down, textcolor=color.white, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)