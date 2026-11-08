"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    bar_index, close, color, high, input, line, location, low, math, na,
    plotshape, script, shape, size, ta
)
from pynecore.types import Line, Persistent, PersistentSeries


@script.indicator('Horns Pattern Identifier [LuxAlgo]', overlay=True, max_lines_count=500)
def main(
    threshold=input.float(0.05, step=0.01, minval=0),
    bull_css=input.color(color.new('#0CB51A'), 'Bullish Horn Levels', group='Style'),
    bear_css=input.color(color.new('#FF1100'), 'Bearish Horn Levels', group='Style')
):
    conf: Persistent[Line] = na(Line)
    tp: Persistent[Line] = na(Line)
    target: Persistent[float] = 0.0
    lvl: PersistentSeries[float] = 0.0
    os: Persistent[int] = 0
    cross: PersistentSeries[int] = 0
    max = math.max(high, high[1], high[2])
    min = math.min(low, low[1], low[2])
    top = math.abs(high - high[2]) / (max - min)
    btm = math.abs(low - low[2]) / (max - min)
    n = bar_index
    line.set_x2(conf, n)
    line.set_x2(tp, n)
    if ta.crossunder(top, threshold) and high[1] < math.min(high, high[2]):
        os = 0
        line.set_x2(conf, n - 2)
        line.set_x2(tp, n - 2)
        line.new(n, high, n - 2, high[2], color=bear_css)
        lvl = min
        target = min - (max - min)
        conf = line.new(n, lvl, n + 1, lvl, style=line.style_dotted, color=bear_css)
        tp = line.new(n, target, n + 1, target, style=line.style_dashed, color=bear_css)
    if ta.crossunder(btm, threshold) and low[1] > math.max(low, low[2]):
        os = 1
        line.set_x2(conf, n - 2)
        line.set_x2(tp, n - 2)
        line.new(n, low, n - 2, low[2], color=bull_css)
        lvl = max
        target = max + max - min
        conf = line.new(n, lvl, n + 1, lvl, style=line.style_dotted, color=bull_css)
        tp = line.new(n, target, n + 1, target, style=line.style_dashed, color=bull_css)
    buy = ta.crossover(close, lvl) and os == 1 and (cross == 1)
    sell = ta.crossunder(close, lvl) and os == 0 and (cross == 1)
    cross = 1 if lvl != lvl[1] else 0 if buy or sell else cross[1]
    plotshape(low if buy else na, 'Buy Label', style=shape.labelup, location=location.absolute, color=color.new('#0CB51A'), text='B', textcolor=color.white, size=size.tiny)
    plotshape(high if sell else na, 'Sell Label', style=shape.labeldown, location=location.absolute, color=color.new('#FF1100'), text='S', textcolor=color.white, size=size.tiny)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
