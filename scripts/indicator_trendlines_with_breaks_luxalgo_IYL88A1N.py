"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.core.pine_cast import cast_bool
from pynecore.core.pine_method import method_call
from pynecore.lib import (
    alertcondition, bar_index, close, color, extend, high, input, line,
    location, low, math, na, plot, plotshape, script, shape, size, ta
)
from pynecore.types import Persistent, PersistentSeries


@script.indicator('Trendlines with Breaks [LuxAlgo]', 'LuxAlgo - Trendlines with Breaks', overlay=True)
def main(
    length=input.int(14, 'Swing Detection Lookback'),
    mult=input.float(1.0, 'Slope', minval=0, step=0.1),
    calcMethod=input.string('Atr', 'Slope Calculation Method', options=('Atr', 'Stdev', 'Linreg')),
    backpaint=input(True, tooltip='Backpainting offset displayed elements in the past. Disable backpainting to see real time information returned by the indicator.'),
    upCss=input.color(color.teal, 'Up Trendline Color', group='Style'),
    dnCss=input.color(color.red, 'Down Trendline Color', group='Style'),
    showExt=input(True, 'Show Extended Lines')
):
    upper: Persistent[float] = 0.0
    lower: Persistent[float] = 0.0
    slope_ph: Persistent[float] = 0.0
    slope_pl: Persistent[float] = 0.0
    offset: Persistent = length if backpaint else 0
    n = bar_index
    src = close
    ph = ta.pivothigh(length, length)
    pl = ta.pivotlow(length, length)
    __block_result__ = na
    __switch__ = calcMethod
    if __switch__ == 'Atr':
        __block_result__ = ta.atr(length) / length * mult
    elif __switch__ == 'Stdev':
        __block_result__ = ta.stdev(src, length) / length * mult
    elif __switch__ == 'Linreg':
        __block_result__ = math.abs(ta.sma(src * n, length) - ta.sma(src, length) * ta.sma(n, length)) / ta.variance(n, length) / 2 * mult
    slope = __block_result__
    slope_ph = slope if cast_bool(ph) else slope_ph
    slope_pl = slope if cast_bool(pl) else slope_pl
    upper = ph if cast_bool(ph) else upper - slope_ph
    lower = pl if cast_bool(pl) else lower + slope_pl
    upos: PersistentSeries[int] = 0
    dnos: PersistentSeries[int] = 0
    upos = 0 if cast_bool(ph) else 1 if close > upper - slope_ph * length else upos
    dnos = 0 if cast_bool(pl) else 1 if close < lower + slope_pl * length else dnos
    uptl: Persistent = line.new(na, na, na, na, color=upCss, style=line.style_dashed, extend=extend.right)
    dntl: Persistent = line.new(na, na, na, na, color=dnCss, style=line.style_dashed, extend=extend.right)
    if cast_bool(ph) and showExt:
        method_call('set_xy1', uptl, n - offset, ph if backpaint else upper - slope_ph * length)
        method_call('set_xy2', uptl, n - offset + 1, ph - slope if backpaint else upper - slope_ph * (length + 1))
    if cast_bool(pl) and showExt:
        method_call('set_xy1', dntl, n - offset, pl if backpaint else lower + slope_pl * length)
        method_call('set_xy2', dntl, n - offset + 1, pl + slope if backpaint else lower + slope_pl * (length + 1))
    plot(upper if backpaint else upper - slope_ph * length, 'Upper', color=na if cast_bool(ph) else upCss, offset=-offset)
    plot(lower if backpaint else lower + slope_pl * length, 'Lower', color=na if cast_bool(pl) else dnCss, offset=-offset)
    plotshape(low if upos > upos[1] else na, 'Upper Break', shape.labelup, location.absolute, upCss, text='B', textcolor=color.white, size=size.tiny)
    plotshape(high if dnos > dnos[1] else na, 'Lower Break', shape.labeldown, location.absolute, dnCss, text='B', textcolor=color.white, size=size.tiny)
    alertcondition(upos > upos[1], 'Upward Breakout', 'Price broke the down-trendline upward')
    alertcondition(dnos > dnos[1], 'Downward Breakout', 'Price broke the up-trendline downward')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
