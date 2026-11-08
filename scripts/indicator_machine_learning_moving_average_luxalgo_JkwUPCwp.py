"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore import pine_range
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    array, bar_index, barstate, chart, close, color, fill, input, math,
    matrix, na, plot, script, ta
)
from pynecore.types import Matrix, NA, Persistent, PersistentSeries, Series


@script.indicator('Machine Learning Moving Average [LuxAlgo]', 'LuxAlgo - Machine Learning Moving Average', overlay=True)
def main(
    window=input.int(100, minval=0),
    forecast=input.int(0),
    sigma=input.float(0.01, step=0.1, minval=0),
    mult=input.float(2, 'Multiplicative Factor', minval=0),
    src: Series[float] = input.source(close, 'Source'),
    upCss=input(color.new(color.new('#5B9CF6'), 50), 'Upper Extremity', group='Style'),
    dnCss=input(color.new(color.new('#E91E63'), 50), 'Lower Extremity', group='Style'),
    bullCss=input(color.new('#3179F5'), 'Moving Average', inline='ma', group='Style'),
    bearCss=input(color.new('#E91E63'), '', inline='ma', group='Style')
):
    def rbf(x1, x2, l):
        return math.exp(-math.pow(x1 - x2, 2) / (2.0 * math.pow(l, 2)))

    def kernel_matrix(X1, X2, l):
        km: Matrix[float] = matrix.new(method_call('size', X1), method_call('size', X2), initial_value=NA(float))
        i: int = 0
        for x1 in X1:
            j: int = 0
            for x2 in X2:
                rbf__00000016__ = rbf(x1, x2, l)
                matrix.set(km, i, j, rbf__00000016__)
                j = j + 1
            i = i + 1
        return km

    identity: Persistent[Matrix[int]] = matrix.new(window, window, 0)
    K_row: Persistent[list[float]] = na(list[float])
    if barstate.isfirst:
        xtrain: list[int] = array.new_int(0)
        xtest: list[int] = array.new_int(0)
        for i in pine_range(0, window - 1, 1):
            for j in pine_range(0, window - 1, 1):
                matrix.set(identity, i, j, 1 if i == j else 0)
            array.push(xtrain, i)
        for i in pine_range(0, window + forecast - 1, 1):
            array.push(xtest, i)
        s = matrix.mult(identity, sigma * sigma)
        Ktrain = method_call('sum', kernel_matrix(xtrain, xtrain, window), s)
        K_inv = method_call('pinv', Ktrain)
        K_star = kernel_matrix(xtrain, xtest, window)
        K_row = method_call('row', method_call('mult', method_call('transpose', K_star), K_inv), window + forecast - 1)
    os: PersistentSeries[int] = 0
    mean = ta.sma(src, window)
    out: Series[float] = na(float)
    if bar_index > window:
        dotprod: float = 0.0
        for i in pine_range(0, window - 1, 1):
            dotprod = dotprod + array.get(K_row, i) * (src[window - 1 - i] - mean)
        out = dotprod + mean
    mae = ta.sma(math.abs(src - out), window) * mult
    upper = out + mae
    lower = out - mae
    os = 1 if close > upper and out > out[1] else 0 if close < lower and out < out[1] else os
    plot_out = plot(out, 'End Point GPR', color=bullCss if os else bearCss)
    plot(out if os != os[1] else na, 'Circle', bullCss if os else bearCss, 3, plot.style_circles)
    plot_upper = plot(upper, 'Upper', color=na)
    plot_lower = plot(lower, 'Lower', color=na)
    fill(plot_upper, plot_out, out + mae, out, upCss, color.new(chart.bg_color, 100))
    fill(plot_out, plot_lower, out, out - mae, color.new(chart.bg_color, 100), dnCss)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
