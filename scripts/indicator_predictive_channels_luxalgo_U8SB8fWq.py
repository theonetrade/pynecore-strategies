"""
@pyne edge

This code was compiled by PyneComp v6.0.79 — the Pine Script to Python compiler.
Run with open-source PyneCore: https://pynecore.org
Compile Pine Scripts online at PyneSys: https://pynesys.io
"""
from pynecore.lib import chart, close, color, display, fill, input, math, na, nz, plot, script, ta
from pynecore.types import Persistent, PersistentSeries


@script.indicator('Predictive Channels [LuxAlgo]', 'LuxAlgo - Predictive Channels', overlay=True)
def main(
    mult=input.float(5, 'Factor', minval=0),
    __input_1__=input.float(50, minval=0),
    r2Css=input(color.new('#F23645'), 'Upper Resistance', inline='resistance', group='Colors'),
    r1Css=input(color.new(color.new('#F23645'), 50), 'Lower', inline='resistance', group='Colors'),
    s1Css=input(color.new(color.new('#089981'), 50), 'Upper Support    ', inline='support', group='Colors'),
    s2Css=input(color.new('#089981'), 'Lower', inline='support', group='Colors'),
    avgCss=input(color.new('#787B86'), 'Average', group='Colors'),
    areaBull=input(color.new(color.new('#089981'), 80), 'Fill', inline='area', group='Colors'),
    areaBear=input(color.new(color.new('#F23645'), 80), '', inline='area', group='Colors')
):
    slope = __input_1__ * mult
    pc_avg: PersistentSeries = close
    os: Persistent[int] = 1
    hold_atr: Persistent[float] = 0.0
    atr = nz(ta.atr(200)) * mult
    pc_avg = close if math.abs(close - pc_avg) > atr else pc_avg + os * hold_atr / slope
    hold_atr = atr / 2 if pc_avg == close else hold_atr
    os = 1 if pc_avg > pc_avg[1] else -1 if pc_avg < pc_avg[1] else os
    pc_R2 = pc_avg + hold_atr
    pc_R1 = pc_avg + hold_atr / 2
    pc_S1 = pc_avg - hold_atr / 2
    pc_S2 = pc_avg - hold_atr
    plot_0 = plot(close, color=na, display=display.none, editable=False)
    plot(pc_R2, 'Upper Resistance', na if close == pc_avg else r2Css)
    plot(pc_R1, 'Lower Resistance', na if close == pc_avg else r1Css)
    plot_avg = plot(pc_avg, 'Average', na if close == pc_avg else avgCss)
    plot(pc_S1, 'Upper Support', na if close == pc_avg else s1Css)
    plot(pc_S2, 'Lower Support', na if close == pc_avg else s2Css)
    topcss = areaBull if close > pc_avg else color.new(chart.bg_color, 100)
    btmcss = areaBear if close < pc_avg else color.new(chart.bg_color, 100)
    fill(plot_0, plot_avg, pc_R2, pc_S2, topcss, btmcss)


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
