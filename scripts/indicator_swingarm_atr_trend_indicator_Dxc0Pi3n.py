"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import (
    alertcondition, close, color, fill, fixnan, high, input, location, low,
    math, na, nz, open, plot, plotshape, request, script, shape, size, syminfo, ta, ticker,
    timeframe
)
from pynecore.types import Series


@script.indicator('Blackflag FTS', overlay=True, timeframe='', na_bool=True)
def main(
    trailType=input.string('modified', 'Trailtype', options=('modified', 'unmodified')),
    ATRPeriod=input(28, 'ATR Period'),
    ATRFactor=input(5, 'ATR Factor'),
    show_fib_entries=input(True, 'Show Fib Entries?')
):
    norm_o = request.security(ticker.new(syminfo.prefix, syminfo.ticker), timeframe.period, open)
    norm_h: Series = request.security(ticker.new(syminfo.prefix, syminfo.ticker), timeframe.period, high)
    norm_l: Series = request.security(ticker.new(syminfo.prefix, syminfo.ticker), timeframe.period, low)
    norm_c: Series = request.security(ticker.new(syminfo.prefix, syminfo.ticker), timeframe.period, close)
    def Wild_ma(_src, _malength):
        _wild: Series[float] = 0.0
        _wild = nz(_wild[1]) + (_src - nz(_wild[1])) / _malength
        return _wild

    HiLo = math.min(norm_h - norm_l, 1.5 * nz(ta.sma(norm_h - norm_l, ATRPeriod)))
    HRef = norm_h - norm_c[1] if norm_l <= norm_h[1] else norm_h - norm_c[1] - 0.5 * (norm_l - norm_h[1])
    LRef = norm_c[1] - norm_l if norm_h >= norm_l[1] else norm_c[1] - norm_l - 0.5 * (norm_l[1] - norm_h)
    trueRange = math.max(HiLo, HRef, LRef) if trailType == 'modified' else math.max(norm_h - norm_l, math.abs(norm_h - norm_c[1]), math.abs(norm_l - norm_c[1]))
    loss = ATRFactor * Wild_ma(trueRange, ATRPeriod)
    Up = norm_c - loss
    Dn = norm_c + loss
    TrendUp: Series = Up
    TrendDown: Series = Dn
    Trend: Series[int] = 1
    TrendUp = math.max(Up, TrendUp[1]) if norm_c[1] > TrendUp[1] else Up
    TrendDown = math.min(Dn, TrendDown[1]) if norm_c[1] < TrendDown[1] else Dn
    Trend = 1 if norm_c > TrendDown[1] else -1 if norm_c < TrendUp[1] else nz(Trend[1], 1)
    trail = TrendUp if Trend == 1 else TrendDown
    ex: Series[float] = 0.0
    ex = norm_h if ta.crossover(Trend, 0) else norm_l if ta.crossunder(Trend, 0) else math.max(ex[1], norm_h) if Trend == 1 else math.min(ex[1], norm_l) if Trend == -1 else ex[1]
    plot(trail, 'Trailingstop', style=plot.style_line, color=color.green if Trend == 1 else color.red if Trend == -1 else na)
    plot(ex, 'Extremum', style=plot.style_circles, color=color.lime if Trend == 1 else color.fuchsia if Trend == -1 else na)
    state: Series = 'long' if Trend == 1 else 'short'
    fib1Level: float = 61.8
    fib2Level: float = 78.6
    fib3Level: float = 88.6
    f1: Series = ex + (trail - ex) * fib1Level / 100
    f2: Series = ex + (trail - ex) * fib2Level / 100
    f3: Series = ex + (trail - ex) * fib3Level / 100
    l100 = trail + 0
    Fib1 = plot(f1, 'Fib 1', style=plot.style_line, color=color.new(color.black, 0))
    Fib2 = plot(f2, 'Fib 2', style=plot.style_line, color=color.new(color.black, 0))
    Fib3 = plot(f3, 'Fib 3', style=plot.style_line, color=color.new(color.black, 0))
    L100 = plot(l100, 'l100', style=plot.style_line, color=color.new(color.black, 0))
    fill(Fib1, Fib2, color=color.green if state == 'long' else color.red if state == 'short' else na)
    fill(Fib2, Fib3, color=color.new(color.green, 70) if state == 'long' else color.new(color.red, 70) if state == 'short' else na)
    fill(Fib3, L100, color=color.new(color.green, 60) if state == 'long' else color.new(color.red, 60) if state == 'short' else na)
    crossunder_1 = ta.crossunder(norm_c, f1[1])
    l1 = state[1] == 'long' and crossunder_1
    crossunder_2 = ta.crossunder(norm_c, f2[1])
    l2 = state[1] == 'long' and crossunder_2
    crossunder_3 = ta.crossunder(norm_c, f3[1])
    l3 = state[1] == 'long' and crossunder_3
    crossover_1 = ta.crossover(norm_c, f1[1])
    s1 = state[1] == 'short' and crossover_1
    crossover_2 = ta.crossover(norm_c, f2[1])
    s2 = state[1] == 'short' and crossover_2
    crossover_3 = ta.crossover(norm_c, f3[1])
    s3 = state[1] == 'short' and crossover_3
    atr = ta.sma(trueRange, 14)
    plotshape(low - atr if show_fib_entries and l1 else na, 'LS1', style=shape.triangleup, location=location.belowbar, color=color.new(color.yellow, 0), size=size.tiny)
    plotshape(low - 1.5 * atr if show_fib_entries and l2 else na, 'LS2', style=shape.triangleup, location=location.belowbar, color=color.new(color.yellow, 0), size=size.tiny)
    plotshape(low - 2 * atr if show_fib_entries and l3 else na, 'LS3', style=shape.triangleup, location=location.belowbar, color=color.new(color.yellow, 0), size=size.tiny)
    plotshape(high + atr if show_fib_entries and s1 else na, 'SS1', style=shape.triangledown, location=location.abovebar, color=color.new(color.purple, 0), size=size.tiny)
    plotshape(high + 1.5 * atr if show_fib_entries and s2 else na, 'SS2', style=shape.triangledown, location=location.abovebar, color=color.new(color.purple, 0), size=size.tiny)
    plotshape(high + 2 * atr if show_fib_entries and s3 else na, 'SS3', style=shape.triangledown, location=location.abovebar, color=color.new(color.purple, 0), size=size.tiny)
    alertcondition(l1, title='cross over Fib1', message='Price crossed below Fib1 level in long trend')
    alertcondition(l2, title='cross over Fib2', message='Price crossed below Fib2 level in long trend')
    alertcondition(l3, title='cross over Fib3', message='Price crossed below Fib3 level in long trend')
    alertcondition(s1, title='cross under Fib1', message='Price crossed above Fib1 level in short trend')
    alertcondition(s2, title='cross under Fib2', message='Price crossed above Fib2 level in short trend')
    alertcondition(s3, title='cross under Fib3', message='Price crossed above Fib3 level in short trend')
    alertcondition(fixnan(f1) != fixnan(f1[1]), title='Stop Line Change', message='Stop Line Change')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)